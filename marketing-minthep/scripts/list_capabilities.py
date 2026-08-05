#!/usr/bin/env python3
"""List what this skill can actually do right now, read live from disk.

The question that keeps arriving is not "what can this skill do" in the abstract, it is
"what is in here that I have forgotten about" - after enough pipelines, references, data
tables, and scripts accumulate, nobody can hold the whole registry in their head, and a
hand-written capability list drifts the moment a file is added or renamed. This reads
`assets/registries/pipelines.json`, every `references/*.md`, every `data/*.csv`, and the
module docstring of every `scripts/*.py`, so the answer is always the current state of the
repository rather than a snapshot someone forgot to update.
"""

from __future__ import annotations

import argparse
import ast
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _load_pipelines() -> list[dict]:
    import json

    registry = json.loads((ROOT / "assets" / "registries" / "pipelines.json").read_text(encoding="utf-8"))
    result = []
    for name, pipeline in registry["pipelines"].items():
        result.append(
            {
                "name": name,
                "title": pipeline.get("title", ""),
                "title_vi": pipeline.get("title_vi", ""),
                "use_when": pipeline.get("use_when", ""),
                "references": pipeline.get("references", []),
                "scripts": pipeline.get("scripts", []),
                "deliverable_count": len(pipeline.get("deliverables", [])),
            }
        )
    return result


def _first_heading(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return path.stem


def _load_references() -> list[dict]:
    result = []
    for path in sorted((ROOT / "references").glob("*.md")):
        result.append({"file": path.name, "title": _first_heading(path)})
    return result


def _load_data_tables() -> list[dict]:
    result = []
    for path in sorted((ROOT / "data").glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration:
                header = []
            rows = sum(1 for _ in reader)
        result.append({"file": path.name, "rows": rows, "columns": header})
    return result


def _first_docstring_line(path: Path) -> str:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return ""
    doc = ast.get_docstring(tree) or ""
    return doc.strip().splitlines()[0] if doc.strip() else ""


def _load_scripts() -> list[dict]:
    result = []
    for path in sorted((ROOT / "scripts").glob("*.py")):
        if path.name.startswith("_"):
            continue
        result.append({"file": path.name, "summary": _first_docstring_line(path)})
    return result


def _matches(query: str, *fields: str) -> bool:
    needle = query.lower()
    return any(needle in field.lower() for field in fields if field)


def build_capabilities(query: str | None = None) -> dict:
    pipelines = _load_pipelines()
    references = _load_references()
    data_tables = _load_data_tables()
    scripts = _load_scripts()

    if query:
        pipelines = [p for p in pipelines if _matches(query, p["name"], p["title"], p["title_vi"], p["use_when"])]
        references = [r for r in references if _matches(query, r["file"], r["title"])]
        scripts = [s for s in scripts if _matches(query, s["file"], s["summary"])]
        data_tables = [d for d in data_tables if _matches(query, d["file"])]

    return {
        "pipelines": pipelines,
        "references": references,
        "data_tables": data_tables,
        "scripts": scripts,
    }


def render_text(capabilities: dict) -> str:
    lines = []
    lines.append(f"Pipelines ({len(capabilities['pipelines'])})")
    for pipeline in capabilities["pipelines"]:
        lines.append(f"  {pipeline['name']} - {pipeline['title']} / {pipeline['title_vi']}")
        lines.append(f"    use when: {pipeline['use_when']}")
    lines.append(f"References ({len(capabilities['references'])})")
    for reference in capabilities["references"]:
        lines.append(f"  {reference['file']} - {reference['title']}")
    lines.append(f"Data tables ({len(capabilities['data_tables'])})")
    for table in capabilities["data_tables"]:
        lines.append(f"  {table['file']} - {table['rows']} rows, columns: {', '.join(table['columns'])}")
    lines.append(f"Scripts ({len(capabilities['scripts'])})")
    for script in capabilities["scripts"]:
        lines.append(f"  {script['file']} - {script['summary']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", help="Filter by a keyword against names, titles, and summaries.")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--output")
    args = parser.parse_args()

    capabilities = build_capabilities(args.query)
    if args.format == "json":
        emit_json(capabilities, args.output)
    else:
        emit(render_text(capabilities), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
