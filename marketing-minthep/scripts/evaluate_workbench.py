#!/usr/bin/env python3
"""Validate pipeline routing and the on-disk execution contract."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from new_run import build_run, load_registry, route_pipeline
from start_workbench import start

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "assets" / "evals" / "routing-cases.json"


def evaluate(cases_path: Path = DEFAULT_CASES) -> dict:
    registry = load_registry()
    cases = json.loads(cases_path.read_text(encoding="utf-8-sig"))["cases"]
    results = []
    for case in cases:
        run = build_run({"request": case["request"]}, registry)
        expected_supporting = case.get("expected_supporting", [])
        expected_mode = case.get("expected_mode", run["mode"])
        passed = (
            run["pipeline"] == case["expected_pipeline"]
            and all(item in run["supporting_pipelines"] for item in expected_supporting)
            and run["mode"] == expected_mode
        )
        results.append({"id": case["id"], "expected": case["expected_pipeline"], "actual": run["pipeline"], "mode": run["mode"], "supporting": run["supporting_pipelines"], "passed": passed})

    missing = []
    for name, pipeline in registry["pipelines"].items():
        for reference in pipeline.get("references", []):
            if not (ROOT / "references" / reference).exists():
                missing.append(f"{name}:references/{reference}")
        for script in pipeline.get("scripts", []):
            if not (ROOT / "scripts" / script).exists():
                missing.append(f"{name}:scripts/{script}")

    seeded = {}
    with tempfile.TemporaryDirectory() as tmp:
        for pipeline in registry["pipelines"]:
            result = start({"request": f"evaluation {pipeline}", "pipeline": pipeline, "mode": "focused", "date": "2026-01-01"}, Path(tmp))
            seeded[pipeline] = result["seeded_files"]

    passed = all(item["passed"] for item in results) and not missing and all(seeded.values())
    return {"passed": passed, "routing": results, "missing_paths": missing, "seeded_files": seeded}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default=str(DEFAULT_CASES))
    parser.add_argument("--output")
    args = parser.parse_args()
    report = evaluate(Path(args.cases))
    content = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
