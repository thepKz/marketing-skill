#!/usr/bin/env python3
"""Create a run workspace and seed its deterministic planning artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from new_run import build_run, write_run
from plan_design_options import plan_options
from plan_image_generation import route_image_request
from plan_marketing_system import plan_marketing_system
from research_plan import build_plan, to_markdown


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def seed_workbench(request: dict, run_dir: Path) -> list[str]:
    """Write route-specific machine artifacts without pretending to author the reports."""
    run_manifest = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    pipeline = run_manifest["pipeline"]
    meta = run_dir / "_meta"
    meta.mkdir(exist_ok=True)
    written = []

    request_path = meta / "request.json"
    _write_json(request_path, request)
    written.append(str(request_path.relative_to(run_dir)).replace("\\", "/"))

    if pipeline in {"plan-from-zero", "deep-research"}:
        research = build_plan(request)
        json_path = meta / "research-plan.json"
        md_path = meta / "research-plan.md"
        _write_json(json_path, research)
        md_path.write_text(to_markdown(research), encoding="utf-8")
        written += [str(json_path.relative_to(run_dir)).replace("\\", "/"), str(md_path.relative_to(run_dir)).replace("\\", "/")]

    if pipeline == "plan-from-zero":
        planning_request = dict(request)
        planning_request.setdefault("asset_scope", request.get("mode", "focused"))
        system_plan = plan_marketing_system(planning_request)
        plan_path = meta / "marketing-system-plan.json"
        _write_json(plan_path, system_plan)
        written.append(str(plan_path.relative_to(run_dir)).replace("\\", "/"))

    if pipeline in {"design-render", "image-from-reference"}:
        options_path = meta / "design-options.json"
        _write_json(options_path, plan_options(request))
        written.append(str(options_path.relative_to(run_dir)).replace("\\", "/"))

    if pipeline == "image-from-reference":
        image_request = dict(request)
        if "reference_images" not in image_request and request.get("reference_assets"):
            image_request["reference_images"] = request["reference_assets"]
        image_request.setdefault("description", request.get("objective") or request.get("request"))
        image_request.setdefault("operation", "edit" if request.get("edit_target") else "generate")
        image_request.setdefault("variant_count", 4)
        route_path = meta / "image-provider-plan.json"
        _write_json(route_path, route_image_request(image_request))
        written.append(str(route_path.relative_to(run_dir)).replace("\\", "/"))

    if pipeline in {"image-from-reference", "design-render", "video-campaign"}:
        capability_path = meta / "render-capability.json"
        capability = {
            "requested_pipeline": pipeline,
            "status": "not-rendered",
            "rendered_files": [],
            "rule": "Update this record only after opening and QA-reviewing real output files. Prompts, specs, wireframes, and storyboards are not rendered media.",
        }
        _write_json(capability_path, capability)
        written.append(str(capability_path.relative_to(run_dir)).replace("\\", "/"))

    if run_manifest["mode"] == "production" and pipeline in {"image-from-reference", "video-campaign"}:
        production_root = run_dir / "production-files"
        folders = ["source", "generations", "edits", "exports", "review"] if pipeline == "image-from-reference" else ["source", "shots", "audio", "edits", "exports", "review"]
        for folder in folders:
            target = production_root / folder
            target.mkdir(parents=True, exist_ok=True)
            note = target / "README.md"
            note.write_text(f"# {folder}\n\nStore actual {folder} files here. Do not mark the run rendered until they exist and pass QA.\n", encoding="utf-8")
            written.append(str(note.relative_to(run_dir)).replace("\\", "/"))

    manifest_path = meta / "seed-manifest.json"
    _write_json(manifest_path, {"pipeline": pipeline, "seeded": written})
    written.append(str(manifest_path.relative_to(run_dir)).replace("\\", "/"))
    return written


def start(request: dict, root: Path, force: bool = False) -> dict:
    run = build_run(request)
    result = write_run(run, root, force=force)
    run_dir = Path(result["run_dir"])
    result["seeded_files"] = seed_workbench(request, run_dir)
    result["supporting_runs"] = []
    for pipeline in run.get("supporting_pipelines", []):
        supporting_request = dict(request)
        supporting_request["pipeline"] = pipeline
        supporting_request["slug"] = f"{pipeline}-{run['created']}"
        supporting_run = build_run(supporting_request)
        supporting_result = write_run(supporting_run, root, force=force)
        supporting_result["seeded_files"] = seed_workbench(supporting_request, Path(supporting_result["run_dir"]))
        result["supporting_runs"].append({
            "pipeline": pipeline,
            "run_id": supporting_result["run_id"],
            "run_dir": supporting_result["run_dir"],
            "seeded_files": supporting_result["seeded_files"],
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="JSON request file")
    parser.add_argument("--request", help="Plain-language request")
    parser.add_argument("--pipeline")
    parser.add_argument("--mode", choices=["focused", "system", "production"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    if args.input:
        request = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    elif args.request:
        request = {"request": args.request}
    else:
        parser.error("Provide --input or --request.")
    if args.pipeline:
        request["pipeline"] = args.pipeline
    if args.mode:
        request["mode"] = args.mode

    result = start(request, Path(args.root).resolve(), force=args.force)
    content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
