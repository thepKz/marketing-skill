#!/usr/bin/env python3
"""Create a bilingual deliverable workspace on disk for one marketing run.

This is the execution contract of the skill: it turns a request into real files with
required sections and acceptance gates, so a run cannot end as conversation.

The workspace is shaped by what the request actually says. That was not true before: a request
reading "lên chiến dịch ra mắt trong 6 tuần ... ngân sách nhỏ" produced a deliverable named
`10-calendar-90d` whose sections were "Days 1-30 / 31-60 / 61-90", and an intake file whose first
instruction was "> WRITE: Quote the user verbatim" — asking to be handed back the sentence sitting
in `_meta/request.json`. A scaffold that ignores a stated six-week horizon and then asks for
information it already holds is why campaign building read as broken. The horizon now names and
divides the calendar, and everything read from the request is written into the intake table with
its label attached, so the plan starts from the request instead of from a blank form.
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
from _signals import phase_plan, read_signals  # noqa: E402

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
         "short video", "video ngắn", "reel", "tiktok video", "video tiktok", "cutdown", "video campaign"),
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
    "rewrite-human": (
        ("viết lại", "viet lai", "rewrite", "sửa văn", "sound human", "sounds like ai", "reads like ai",
         "nghe như ai viết", "giọng tự nhiên", "dịch máy", "dich may", "word by word", "word-by-word",
         "dịch từng chữ", "humanize", "humanise", "làm cho tự nhiên", "biên tập lại", "transcreate",
         "dịch sang tiếng anh", "dịch sang tiếng việt", "translate this copy", "bản dịch"),
        ("rewrite", "reword", "rephrase", "humanize", "humanise", "transcreate", "viết", "lại", "dịch",
         "biên", "tập", "polish", "cadence", "nhịp", "giọng", "translation", "calque"),
    ),
    # "kpi" and "bsc" are the words that actually arrive, and they arrive far more often as an
    # acronym than as "balanced scorecard". Note what is deliberately absent from the word list:
    # "target", "mục tiêu" and "đo" all belong to half the other pipelines, and adding them here
    # would pull ordinary planning requests into a scoring engine that cannot serve them.
    "score-kpi": (
        ("kpi", "bsc", "balanced scorecard", "scorecard", "thẻ điểm cân bằng", "xây dựng kpi",
         "xay dung kpi", "lên kpi", "giao kpi", "chấm điểm kpi", "chấm điểm bsc", "đánh giá kpi",
         "kpi cho phòng", "kpi cá nhân", "trọng số kpi", "achievement rate", "% achievement",
         "tỉ lệ hoàn thành kpi", "cascade kpi", "phân bổ kpi", "okr"),
        ("kpi", "bsc", "scorecard", "okr", "cascade", "lagging", "leading", "weighting",
         "trọng", "số"),
    ),
    # "model" and "outfit swap" already live in image-from-reference for editing a
    # supplied photo. These triggers are deliberately more specific, so a one-off edit
    # request does not get pulled into building a whole recurring identity.
    "virtual-model": (
        ("virtual model", "ai model", "digital model", "brand ambassador", "virtual influencer",
         "ai influencer", "digital human", "consistent character", "virtual try-on", "try-on model",
         "người mẫu ảo", "người mẫu ai", "nhân vật ảo", "đại diện thương hiệu ảo", "mascot ảo",
         "nguoi mau ao", "nguoi mau ai", "nhan vat ao"),
        ("virtual", "ảo", "ambassador", "influencer", "persona", "presenter", "avatar", "mascot",
         "nhân", "vật"),
    ),
}


def _supporting_pipelines(routing: dict) -> list[str]:
    primary = routing["pipeline"]
    scores = routing.get("scores", {})
    primary_score = scores.get(primary, 0)
    if not scores or primary_score <= 0:
        return []
    threshold = max(3, int(primary_score * 0.6))
    ranked = sorted(scores.items(), key=lambda item: -item[1])
    return [name for name, score in ranked if name != primary and score >= threshold][:2]


def _select_mode(request: dict, pipeline_name: str, pipeline: dict) -> str:
    explicit = request.get("mode")
    if explicit:
        return str(explicit).lower()
    text = " ".join(str(request.get(key, "")) for key in ("request", "objective", "deliverable", "notes")).lower()
    production_signals = ("render", "xuất", "export", "production-ready", "file mp4", "file png", "file pdf", "in ấn")
    if pipeline_name in {"image-from-reference", "design-render", "video-campaign"} and any(signal in text for signal in production_signals):
        return "production"
    return str(pipeline.get("default_mode", "focused")).lower()


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

    # Preserve the user's first concrete deliverable when a design request also asks
    # for a supporting video; the latter becomes a linked workbench instead of
    # silently replacing the menu/layout job.
    if "menu" in text and any(token in text for token in ("video", "tiktok", "reel", "storyboard")):
        menu_position = text.find("menu")
        video_positions = [pos for token in ("video", "tiktok", "reel", "storyboard") if (pos := text.find(token)) >= 0]
        if video_positions and menu_position <= min(video_positions):
            scores["design-render"] = max(scores["design-render"], scores["video-campaign"] + 1)

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


def request_text(request: dict) -> str:
    return " ".join(
        str(request.get(key, ""))
        for key in ("request", "objective", "project", "notes", "deliverable")
    ).strip()


def _calendar_spec(spec: dict, horizon: dict) -> dict:
    """Rebuild the calendar deliverable around the horizon the request stated.

    The filename carries the horizon because the filename is the part people quote back. Calling
    a six-week plan `10-calendar-90d` is a factual error in the one artefact whose whole subject
    is time. When no horizon was stated the file keeps the 90-day default and the section body
    says so, so the assumption is visible rather than dressed up as a decision.
    """
    weeks = horizon["weeks"]
    phases = phase_plan(weeks)
    spec = dict(spec)
    spec["file"] = f"10-calendar-{weeks}w"
    spec["title"] = f"{weeks}-week calendar ({horizon['days']} days)"
    spec["title_vi"] = f"Lịch {weeks} tuần ({horizon['days']} ngày)"

    if horizon["stated"]:
        opening = (
            f"What must exist before day one: assets, tracking, inventory, permissions. The "
            f"horizon is {weeks} weeks, from the request's \"{horizon['evidence']}\", so pre-launch "
            f"work has to fit before week 1 rather than inside it."
        )
    else:
        opening = (
            "What must exist before day one: assets, tracking, inventory, permissions. No horizon "
            "was stated, so this calendar assumes 13 weeks. Confirm or replace that before "
            "committing anyone to a date."
        )

    sections = [{"en": "Phase 0 pre-launch", "vi": "Giai đoạn 0 trước khi chạy", "write": opening}]
    for phase in phases:
        span = (
            f"Week {phase['week_from']}"
            if phase["week_from"] == phase["week_to"]
            else f"Weeks {phase['week_from']}-{phase['week_to']}"
        )
        span_vi = (
            f"Tuần {phase['week_from']}"
            if phase["week_from"] == phase["week_to"]
            else f"Tuần {phase['week_from']}-{phase['week_to']}"
        )
        sections.append(
            {
                "en": f"{span} — {phase['name_en']} (days {phase['day_from']}-{phase['day_to']})",
                "vi": f"{span_vi} — {phase['name_vi']} (ngày {phase['day_from']}-{phase['day_to']})",
                "write": f"{phase['goal_en']} One learning goal per week, named before the activity.",
            }
        )
    sections += [spec["sections"][-2], spec["sections"][-1]]
    spec["sections"] = sections
    return spec


def _intake_seeds(request: dict, signals: dict, context: dict) -> dict:
    """Pre-fill the intake sections whose answers are already in hand.

    Only two sections can be honestly seeded: the verbatim request, which we have, and the label
    table, where each row states what was read and the phrase it was read from. Product truth,
    rights, and price stay empty because nobody has told us any of them, and a seeded guess there
    is the exact failure the truth gate exists to prevent.
    """
    verbatim = str(request.get("request") or request.get("project") or "").strip()
    horizon, budget = signals["horizon"], signals["budget"]
    family, market = signals["product_family"], signals["market"]

    rows = [
        "| Field | Value | Label | Read from |",
        "|---|---|---|---|",
    ]

    def row(field: str, value: str, label: str, evidence: str) -> None:
        rows.append(f"| {field} | {value} | `{label}` | {evidence or '—'} |")

    row("Campaign horizon", f"{horizon['weeks']} weeks ({horizon['days']} days)",
        horizon["label"] if horizon["stated"] else "assumption",
        f"\"{horizon['evidence']}\"" if horizon["stated"] else "not stated; 13 weeks assumed")
    row("Budget pressure", budget["tier"], budget["label"],
        f"\"{budget['evidence']}\"" if budget["stated"] else "not stated")
    row("Product family", family["family"], family["label"],
        ", ".join(f"\"{word}\"" for word in family["evidence"]))
    row("Market", market["market"] + (", single location" if market["single_location"] else ""),
        market["label"], ", ".join(f"\"{place}\"" for place in market["places"]))
    row("Pipeline / mode", f"{context['pipeline']} / {context['mode']}", "decision", "routing score")
    row("Unit price", "unknown", "unknown", "never stated; the budget deliverable needs it")
    row("Contribution margin", "unknown", "unknown", "never stated; the CAC ceiling derives from it")

    seeds = {
        "Confirmed / observed / inferred / unknown": "\n".join(rows) + (
            "\n\n> WRITE: Add the product, price, capacity, and proof rows. Every `unknown` above "
            "either gets an answer or gets an assumption written next to it. Nothing labelled "
            "`inferred` may be repeated downstream as a confirmed fact."
        ),
    }
    if verbatim:
        seeds["Request as stated"] = (
            f"> {verbatim}\n\n"
            "*Quoted as received, uncleaned. Anything below that is not in this sentence is an "
            "inference and is labelled as one.*"
        )
    return seeds


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


def _markdown_stub(spec: dict, lang: str | None, context: dict, seeds: dict | None = None) -> str:
    seeds = seeds or {}
    parts = [_header(spec, lang, context)]
    for section in spec.get("sections", []):
        if lang == "vi":
            heading = section["vi"]
        elif lang == "en":
            heading = section["en"]
        else:
            heading = f"{section['vi']} / {section['en']}"
        body = seeds.get(section["en"])
        parts.append(f"## {heading}\n\n{body}\n" if body else f"## {heading}\n\n> WRITE: {section['write']}\n")
    return "\n".join(parts) + "\n"


def _dir_readme(spec: dict, context: dict) -> str:
    return (
        f"<!-- minthep:deliverable id={spec['id']} lang=vi+en status=empty -->\n"
        f"# {spec['title_vi']} / {spec['title']}\n\n"
        f"**Run:** `{context['run_id']}` · **Status:** `empty`\n\n"
        f"**Acceptance gate / Tiêu chí nghiệm thu:** {spec['gate']}\n\n"
        f"> WRITE: {spec.get('readme', 'Populate this folder, then replace this line.')}\n"
    )


def resolved_specs(pipeline: dict, mode: str, signals: dict) -> list[dict]:
    """The deliverable specs for this mode, after the request has been allowed to reshape them.

    `build_run` and `write_run` both go through here so the manifest and the files on disk cannot
    disagree about what a deliverable is called. They used to be derived independently, which is
    the kind of split that stays invisible until one side is changed.
    """
    specs = []
    for spec in _active(pipeline["deliverables"], mode):
        if spec["id"] == "10-calendar":
            spec = _calendar_spec(spec, signals["horizon"])
        specs.append(spec)
    return specs


def build_run(request: dict, registry: dict | None = None) -> dict:
    registry = registry or load_registry()
    routing = route_pipeline(request, registry)
    pipeline_name = routing["pipeline"]
    pipeline = registry["pipelines"][pipeline_name]

    mode = _select_mode(request, pipeline_name, pipeline)
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

    signals = read_signals(request_text(request))
    context = {"run_id": run_id, "pipeline": pipeline_name, "mode": mode}
    deliverables = []
    for spec in resolved_specs(pipeline, mode, signals):
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
        "signals": signals,
        "supporting_pipelines": _supporting_pipelines(routing),
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


def write_run(run: dict, root: Path, force: bool = False, request: dict | None = None) -> dict:
    registry = load_registry()
    pipeline = registry["pipelines"][run["pipeline"]]
    signals = run.get("signals") or read_signals(str(run.get("project", "")))
    specs = {item["id"]: item for item in resolved_specs(pipeline, run["mode"], signals)}
    run_dir = root / "runs" / run["run_id"]
    if run_dir.exists() and not force:
        raise FileExistsError(f"{run_dir} already exists. Pass --force to overwrite.")
    run_dir.mkdir(parents=True, exist_ok=True)

    context = {"run_id": run["run_id"], "pipeline": run["pipeline"], "mode": run["mode"]}
    seeds = {"01-intake": _intake_seeds(request or {"request": run.get("project", "")}, signals, context)}
    written = []
    for entry in run["deliverables"]:
        spec = specs[entry["id"]]
        kind = entry["kind"]
        seed = seeds.get(entry["id"])
        for rel in entry["paths"]:
            target = run_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if kind == "md" and entry["bilingual"]:
                lang = rel.rsplit(".", 2)[-2]
                target.write_text(_markdown_stub(spec, lang, context, seed), encoding="utf-8")
            elif kind == "md":
                target.write_text(_markdown_stub(spec, None, context, seed), encoding="utf-8")
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


def _signal_note(signals: dict) -> str:
    """One line saying what was read from the request and what was assumed instead.

    It goes at the top of the run index because a reader has to be able to see, before opening
    anything, whether the six-week horizon in their head is the one the plan is built on.
    """
    if not signals:
        return ""
    horizon, budget, family = signals["horizon"], signals["budget"], signals["product_family"]
    read = [
        f"horizon **{horizon['weeks']} weeks** ({'stated: ' + horizon['evidence'] if horizon['stated'] else 'assumed, not stated'})",
        f"budget **{budget['tier']}**" + (f" (from \"{budget['evidence']}\")" if budget["stated"] else " (not stated)"),
        f"product family **{family['family']}**" + (f" (from \"{family['evidence'][0]}\")" if family["evidence"] else " (not recognised)"),
    ]
    return "Read from the request: " + "; ".join(read) + ". Correct any of these in `01-intake` first — everything downstream is built on them."


def _index(run: dict, written: list[str]) -> str:
    lines = [
        f"# {run['project'] or run['run_id']}",
        "",
        f"**Pipeline:** {run['pipeline_title']} (`{run['pipeline']}`) · **Mode:** `{run['mode']}` · "
        f"**Languages:** {', '.join(run['languages'])} · **Created:** {run['created']}",
        "",
        f"Routing: {run['routing']['reason']}.",
        "",
        _signal_note(run.get("signals") or {}),
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
        run = write_run(run, Path(args.root).resolve(), force=args.force, request=request)

    emit_json(run, args.output)


if __name__ == "__main__":
    main()
