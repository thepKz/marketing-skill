#!/usr/bin/env python3
"""Create a bilingual deliverable workspace on disk for one marketing run.

This is the execution contract of the skill: it turns a request into real files with
required sections and acceptance gates, so a run cannot end as conversation.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_REGISTRY = ROOT / "assets" / "registries" / "pipelines.json"
TEMPLATE_DIR = ROOT / "assets" / "templates"

MODES = ("focused", "system", "production")
MAX_SLUG = 48

# Vietnamese and English trigger words. Weighted: a phrase match counts more than a word.
PIPELINE_KEYWORDS = {
    "plan-from-zero": (
        ("marketing plan", "kế hoạch marketing", "lên kế hoạch", "ke hoach marketing", "go to market",
         "launch plan", "business plan", "từ đầu", "from scratch", "chiến lược marketing"),
        ("plan", "strategy", "positioning", "offer", "funnel", "kế", "hoạch", "chiến", "lược", "mở",
         "quán", "bán", "startup", "brand"),
    ),
    "deep-research": (
        ("market research", "nghiên cứu thị trường", "đánh giá thị trường", "market assessment",
         "competitor analysis", "phân tích đối thủ", "market size", "quy mô thị trường", "feasibility"),
        ("research", "nghiên", "cứu", "competitor", "đối", "thủ", "market", "thị", "trường", "survey",
         "khảo", "sát", "demand", "sizing", "tam", "sam", "som"),
    ),
    "image-from-reference": (
        ("from this photo", "from this image", "từ hình này", "từ ảnh này", "product shot", "packshot",
         "key visual", "branding image", "hình ảnh branding", "ảnh nghệ thuật", "artistic image",
         "identity preserving", "outfit swap", "photoshoot", "chụp hình", "retouch"),
        ("image", "photo", "picture", "ảnh", "hình", "chụp", "visual", "shoot", "studio", "lighting",
         "portrait", "packshot", "edit", "composite", "makeup", "model"),
    ),
    "design-render": (
        ("menu design", "thiết kế menu", "làm menu", "thực đơn", "landing page", "wireframe", "one pager",
         "one-pager", "packaging design", "thiết kế bao bì", "brochure", "tờ rơi", "poster design",
         "print menu", "menu hiện đại"),
        ("menu", "thực", "đơn", "wireframe", "layout", "poster", "packaging", "brochure", "flyer",
         "leaflet", "typography", "grid", "print", "in", "banner", "design", "thiết", "kế", "mockup"),
    ),
    "video-campaign": (
        ("shot list", "storyboard", "video ad", "quảng cáo video", "kịch bản video", "video script",
         "short video", "video ngắn", "reel", "tiktok video", "cutdown", "video campaign"),
        ("video", "clip", "reel", "shorts", "footage", "kịch", "bản", "storyboard", "shot", "veo",
         "sora", "kling", "runway", "motion"),
    ),
    "optimize-iterate": (
        ("not working", "không hiệu quả", "kém hiệu quả", "improve performance", "tối ưu",
         "cải thiện", "diagnose", "chẩn đoán", "why is my", "drop in", "giảm doanh số", "rising cac",
         "ad fatigue"),
        ("optimize", "optimise", "performance", "roas", "cpa", "cpc", "ctr", "conversion", "diagnose",
         "audit", "tối", "ưu", "giảm", "báo", "cáo", "report", "experiment", "test", "a/b"),
    ),
}


def _slugify(value: str, fallback: str = "run") -> str:
    text = unicodedata.normalize("NFD", str(value))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d").replace("Đ", "D")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    text = re.sub(r"-{2,}", "-", text)
    if len(text) <= MAX_SLUG:
        return text or fallback
    # Cut back to the last word boundary so the folder name stays readable and never
    # ends on a dangling separator. Only when that boundary is late enough to keep
    # most of the slug; otherwise take the hard clip.
    clipped = text[:MAX_SLUG]
    tail = clipped.rfind("-")
    if tail >= MAX_SLUG // 2:
        clipped = clipped[:tail]
    return clipped.strip("-") or fallback


def load_registry() -> dict:
    return json.loads(PIPELINE_REGISTRY.read_text(encoding="utf-8"))


def route_pipeline(request: dict, registry: dict) -> dict:
    """Score the request text against pipeline triggers. Explicit pipeline always wins."""
    pipelines = registry["pipelines"]
    explicit = str(request.get("pipeline", "auto")).lower()
    if explicit not in ("auto", ""):
        if explicit not in pipelines:
            raise ValueError(f"Unsupported pipeline: {explicit}. Choose from {', '.join(pipelines)}.")
        return {"pipeline": explicit, "scores": {}, "reason": "explicitly requested"}

    text = " ".join(
        str(request.get(key, ""))
        for key in ("request", "objective", "project", "notes", "deliverable")
    ).lower()
    scores: dict[str, int] = {}
    for name, (phrases, words) in PIPELINE_KEYWORDS.items():
        score = 3 * sum(1 for phrase in phrases if phrase in text)
        score += sum(1 for word in words if re.search(rf"\b{re.escape(word)}", text))
        scores[name] = score

    best = max(scores, key=lambda name: (scores[name], -list(pipelines).index(name)))
    if scores[best] == 0:
        return {
            "pipeline": "plan-from-zero",
            "scores": scores,
            "reason": "no signal in the request text; defaulted to the widest pipeline",
        }
    runner_up = sorted(scores.items(), key=lambda item: -item[1])[1]
    reason = f"highest trigger score ({scores[best]}); next was {runner_up[0]} at {runner_up[1]}"
    return {"pipeline": best, "scores": scores, "reason": reason}


def _active(deliverables: list[dict], mode: str) -> list[dict]:
    return [item for item in deliverables if mode in item.get("modes", MODES)]


def _header(spec: dict, lang: str | None, context: dict) -> str:
    title = spec["title_vi"] if lang == "vi" else spec["title"]
    if lang is None:
        title = f"{spec['title_vi']} / {spec['title']}"
    lang_field = lang or "vi+en"
    lines = [
        f"<!-- minthep:deliverable id={spec['id']} lang={lang_field} status=empty -->",
        f"# {title}",
        "",
        f"**Run:** `{context['run_id']}` · **Pipeline:** `{context['pipeline']}` · "
        f"**Mode:** `{context['mode']}` · **Status:** `empty`",
        "",
        f"**Acceptance gate / Tiêu chí nghiệm thu:** {spec['gate']}",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def _markdown_stub(spec: dict, lang: str | None, context: dict) -> str:
    parts = [_header(spec, lang, context)]
    for section in spec.get("sections", []):
        if lang == "vi":
            heading = section["vi"]
        elif lang == "en":
            heading = section["en"]
        else:
            heading = f"{section['vi']} / {section['en']}"
        parts.append(f"## {heading}\n\n> WRITE: {section['write']}\n")
    return "\n".join(parts) + "\n"


def _dir_readme(spec: dict, context: dict) -> str:
    return (
        f"<!-- minthep:deliverable id={spec['id']} lang=vi+en status=empty -->\n"
        f"# {spec['title_vi']} / {spec['title']}\n\n"
        f"**Run:** `{context['run_id']}` · **Status:** `empty`\n\n"
        f"**Acceptance gate / Tiêu chí nghiệm thu:** {spec['gate']}\n\n"
        f"> WRITE: {spec.get('readme', 'Populate this folder, then replace this line.')}\n"
    )


def build_run(request: dict, registry: dict | None = None) -> dict:
    registry = registry or load_registry()
    routing = route_pipeline(request, registry)
    pipeline_name = routing["pipeline"]
    pipeline = registry["pipelines"][pipeline_name]

    mode = str(request.get("mode", "focused")).lower()
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}. Choose from {', '.join(MODES)}.")

    languages = [str(item).lower() for item in request.get("languages", ["vi", "en"])]
    for lang in languages:
        if lang not in ("vi", "en"):
            raise ValueError(f"Unsupported language: {lang}. Supported: vi, en.")
    if not languages:
        raise ValueError("At least one language is required.")

    created = str(request.get("date") or _dt.date.today().isoformat())
    slug = _slugify(request.get("slug") or request.get("project") or request.get("request", ""), "run")
    run_id = f"{created}-{slug}"

    context = {"run_id": run_id, "pipeline": pipeline_name, "mode": mode}
    deliverables = []
    for spec in _active(pipeline["deliverables"], mode):
        kind = spec.get("kind", "md")
        if kind == "md" and spec.get("bilingual"):
            paths = [f"{spec['file']}.{lang}.md" for lang in languages]
        elif kind == "dir":
            paths = [f"{spec['file']}/README.md"]
        else:
            paths = [spec["file"]]
        deliverables.append(
            {
                "id": spec["id"],
                "kind": kind,
                "bilingual": bool(spec.get("bilingual")),
                "title": spec["title"],
                "title_vi": spec["title_vi"],
                "gate": spec["gate"],
                "paths": paths,
                "status": "empty",
            }
        )

    return {
        "schema_version": 1,
        "run_id": run_id,
        "created": created,
        "project": request.get("project") or request.get("request", ""),
        "pipeline": pipeline_name,
        "pipeline_title": pipeline["title"],
        "mode": mode,
        "languages": languages,
        "routing": routing,
        "references_to_load": pipeline["references"],
        "scripts": pipeline["scripts"],
        "deliverables": deliverables,
        "truth_gate": [
            "Label every fact confirmed, observed, inferred, or unknown. An unknown may never become public copy.",
            "Cite a URL and a retrieval date for anything time-sensitive, priced, versioned, or platform-specific.",
            "Never claim research, rendering, publication, outreach, or performance that did not happen.",
        ],
        "next_actions": [
            f"Read the references listed for {pipeline_name}, then fill 01-intake before anything else.",
            "Replace every `> WRITE:` line with real content and update the status marker in the file header.",
            f"Run scripts/run_status.py --run <path> to confirm no deliverable is still empty.",
        ],
    }


def write_run(run: dict, root: Path, force: bool = False) -> dict:
    registry = load_registry()
    pipeline = registry["pipelines"][run["pipeline"]]
    specs = {item["id"]: item for item in pipeline["deliverables"]}
    run_dir = root / "runs" / run["run_id"]
    if run_dir.exists() and not force:
        raise FileExistsError(f"{run_dir} already exists. Pass --force to overwrite.")
    run_dir.mkdir(parents=True, exist_ok=True)

    context = {"run_id": run["run_id"], "pipeline": run["pipeline"], "mode": run["mode"]}
    written = []
    for entry in run["deliverables"]:
        spec = specs[entry["id"]]
        kind = entry["kind"]
        for rel in entry["paths"]:
            target = run_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if kind == "md" and entry["bilingual"]:
                lang = rel.rsplit(".", 2)[-2]
                target.write_text(_markdown_stub(spec, lang, context), encoding="utf-8")
            elif kind == "md":
                target.write_text(_markdown_stub(spec, None, context), encoding="utf-8")
            elif kind == "csv":
                target.write_text(spec["header"] + "\n", encoding="utf-8")
            elif kind == "json":
                template = spec.get("template")
                source = TEMPLATE_DIR / template if template else None
                if source and source.exists():
                    shutil.copyfile(source, target)
                else:
                    target.write_text("{}\n", encoding="utf-8")
            elif kind == "dir":
                target.write_text(_dir_readme(spec, context), encoding="utf-8")
            written.append(str(target.relative_to(run_dir)).replace("\\", "/"))

    (run_dir / "run.json").write_text(
        json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (run_dir / "README.md").write_text(_index(run, written), encoding="utf-8")
    result = dict(run)
    result["run_dir"] = str(run_dir)
    result["files_written"] = written + ["run.json", "README.md"]
    return result


def _index(run: dict, written: list[str]) -> str:
    lines = [
        f"# {run['project'] or run['run_id']}",
        "",
        f"**Pipeline:** {run['pipeline_title']} (`{run['pipeline']}`) · **Mode:** `{run['mode']}` · "
        f"**Languages:** {', '.join(run['languages'])} · **Created:** {run['created']}",
        "",
        f"Routing: {run['routing']['reason']}.",
        "",
        "## Deliverables / Sản phẩm giao",
        "",
        "| # | Deliverable | Sản phẩm | Files | Gate |",
        "|---|---|---|---|---|",
    ]
    for index, entry in enumerate(run["deliverables"], start=1):
        files = " · ".join(f"[`{path}`]({path})" for path in entry["paths"])
        gate = entry["gate"].replace("|", "\\|")
        lines.append(f"| {index} | {entry['title']} | {entry['title_vi']} | {files} | {gate} |")
    lines += [
        "",
        "## How to use / Cách dùng",
        "",
        "1. Fill `01-intake` first. Everything downstream inherits its truth labels.",
        "2. Replace every `> WRITE:` line with real content. That marker is how completeness is measured.",
        "3. Update the `status=` marker in each file header: `empty` -> `draft` -> `final`.",
        "4. Run `python scripts/run_status.py --run .` to see what is still outstanding.",
        "",
        "## Truth gate / Cổng sự thật",
        "",
    ]
    lines += [f"- {rule}" for rule in run["truth_gate"]]
    lines += ["", "## References to load / Tài liệu cần đọc", ""]
    lines += [f"- `references/{item}`" for item in run["references_to_load"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a bilingual deliverable workspace for one marketing run.")
    parser.add_argument("--input", help="JSON request file")
    parser.add_argument("--request", help="Plain-text request, used instead of --input")
    parser.add_argument("--pipeline", default=None, help="Force a pipeline instead of routing")
    parser.add_argument("--mode", default=None, choices=list(MODES))
    parser.add_argument("--slug", default=None)
    parser.add_argument("--languages", default=None, help="Comma separated, e.g. vi,en")
    parser.add_argument("--root", default=".", help="Where the runs/ directory lives")
    parser.add_argument("--date", default=None, help="ISO date, defaults to today")
    parser.add_argument("--plan-only", action="store_true", help="Print the manifest without writing files")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing run directory")
    parser.add_argument("--output", help="Optional JSON output file")
    args = parser.parse_args()

    if args.input:
        request = json.loads(Path(args.input).read_text(encoding="utf-8"))
    elif args.request:
        request = {"request": args.request}
    else:
        parser.error("Provide --input or --request.")

    for key, value in (
        ("pipeline", args.pipeline),
        ("mode", args.mode),
        ("slug", args.slug),
        ("date", args.date),
    ):
        if value:
            request[key] = value
    if args.languages:
        request["languages"] = [item.strip() for item in args.languages.split(",") if item.strip()]

    run = build_run(request)
    if not args.plan_only:
        run = write_run(run, Path(args.root).resolve(), force=args.force)

    emit_json(run, args.output)


if __name__ == "__main__":
    main()
