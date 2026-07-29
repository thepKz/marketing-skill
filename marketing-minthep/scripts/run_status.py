#!/usr/bin/env python3
"""Audit a run workspace for completeness before it is presented as finished.

Two independent axes. Fill state answers "is there content" (empty / draft / final).
Quality state answers "is the content defensible" (clean / flagged) and catches unsourced
figures, placeholder leaks, lopsided translations, and sections thin enough to be filler.
Under --strict either axis failing exits non-zero, so a run cannot be reported complete
while gaps remain. --allow-warnings narrows that to fill state only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit  # noqa: E402

WRITE_MARKER = re.compile(r"^>\s*WRITE:", re.MULTILINE)
STATUS_MARKER = re.compile(r"<!--\s*minthep:deliverable\s+id=(\S+)\s+lang=(\S+)\s+status=(\S+)\s*-->")
PLACEHOLDER = re.compile(r"\b(TBD|TODO|FIXME|lorem ipsum|xxx+|\.\.\.\.+|placeholder)\b", re.IGNORECASE)
UNVERIFIED = re.compile(r"\[UNVERIFIED", re.IGNORECASE)
URL = re.compile(r"https?://")
# A quantity that reads like a load-bearing figure: percentages, money, or large numbers.
FIGURE = re.compile(r"(?<![\w/])(?:\d[\d.,]*\s*%|\d[\d.,]{3,}|(?:VND|USD|\$|₫)\s*\d)")

HEADING = re.compile(r"^##\s+(.+)$", re.MULTILINE)

VALID_STATUS = ("empty", "draft", "final")

# A section body shorter than this reads as a gesture at an answer rather than an answer.
THIN_SECTION_BYTES = 120
# Only judge a document thin when it has enough sections for the ratio to mean something.
THIN_SECTION_FLOOR = 4


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _thin_sections(text: str) -> tuple[int, int]:
    """Return (thin_count, total_count) for `## ` sections, measuring body only."""
    matches = list(HEADING.finditer(text))
    if not matches:
        return 0, 0
    thin = 0
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if len(body.encode("utf-8")) < THIN_SECTION_BYTES:
            thin += 1
    return thin, len(matches)


def audit_file(path: Path) -> dict:
    result = {
        "path": path.name,
        "exists": path.exists(),
        "status": "missing",
        "unfilled_sections": 0,
        "placeholders": 0,
        "unverified_markers": 0,
        "figures": 0,
        "sources": 0,
        "thin_sections": 0,
        "sections": 0,
        "bytes": 0,
        "issues": [],
        "warnings": [],
    }
    if not path.exists():
        result["issues"].append("file is missing")
        return result

    text = _read(path)
    result["bytes"] = len(text.encode("utf-8"))

    if path.suffix == ".csv":
        rows = [line for line in text.splitlines() if line.strip()]
        data_rows = max(0, len(rows) - 1)
        result["status"] = "final" if data_rows else "empty"
        result["data_rows"] = data_rows
        if not data_rows:
            result["issues"].append("header only, no rows")
        return result

    if path.suffix == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            result["status"] = "invalid"
            result["issues"].append(f"invalid JSON: {error.msg} at line {error.lineno}")
            return result
        filled = bool(payload) and payload != {}
        result["status"] = "final" if filled else "empty"
        if not filled:
            result["issues"].append("empty JSON object")
        return result

    marker = STATUS_MARKER.search(text)
    declared = marker.group(3) if marker else None
    if declared and declared not in VALID_STATUS:
        result["issues"].append(f"status marker '{declared}' is not one of {', '.join(VALID_STATUS)}")
        declared = None

    result["unfilled_sections"] = len(WRITE_MARKER.findall(text))
    result["placeholders"] = len(PLACEHOLDER.findall(text))
    result["unverified_markers"] = len(UNVERIFIED.findall(text))
    result["figures"] = len(FIGURE.findall(text))
    result["sources"] = len(URL.findall(text))
    result["thin_sections"], result["sections"] = _thin_sections(text)

    if result["unfilled_sections"]:
        result["status"] = "empty" if declared in (None, "empty") else declared
        result["issues"].append(f"{result['unfilled_sections']} section(s) still hold a WRITE prompt")
    else:
        result["status"] = declared or "draft"

    if not marker:
        result["issues"].append("no minthep:deliverable status marker found")

    # Quality warnings only make sense once the WRITE prompts are gone; before that every
    # section is trivially thin and unsourced, and the fill state already says so.
    if result["unfilled_sections"]:
        return result

    if result["placeholders"]:
        result["warnings"].append(f"{result['placeholders']} placeholder token(s) left in the text")
    if result["figures"] >= 3 and result["sources"] == 0:
        result["warnings"].append(
            f"{result['figures']} figure(s) present but no source URL in the file"
        )
    if (
        result["sections"] >= THIN_SECTION_FLOOR
        and result["thin_sections"] * 2 > result["sections"]
    ):
        result["warnings"].append(
            f"{result['thin_sections']} of {result['sections']} section(s) are under "
            f"{THIN_SECTION_BYTES} bytes; the document is filled but thin"
        )
    return result


def _dedupe(values) -> list[str]:
    """Keep first occurrence. Both language versions of a file report the same defect."""
    return list(dict.fromkeys(values))


def audit_run(run_dir: Path) -> dict:
    manifest_path = run_dir / "run.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No run.json in {run_dir}. Is this a run workspace?")
    manifest = json.loads(_read(manifest_path))

    files = []
    per_deliverable = []
    for entry in manifest["deliverables"]:
        audits = [audit_file(run_dir / rel) for rel in entry["paths"]]
        files.extend(audits)
        statuses = {item["status"] for item in audits}
        if "missing" in statuses or "invalid" in statuses:
            status = "missing"
        elif statuses == {"final"}:
            status = "final"
        elif "empty" in statuses:
            status = "empty"
        else:
            status = "draft"
        per_deliverable.append(
            {
                "id": entry["id"],
                "title": entry["title"],
                "status": status,
                "gate": entry["gate"],
                "issues": _dedupe(issue for item in audits for issue in item["issues"]),
                "warnings": _dedupe(warning for item in audits for warning in item["warnings"]),
                "unfilled_sections": sum(item["unfilled_sections"] for item in audits),
            }
        )

    if manifest["languages"] and len(manifest["languages"]) > 1:
        for entry in manifest["deliverables"]:
            if not entry.get("bilingual"):
                continue
            record = next(item for item in per_deliverable if item["id"] == entry["id"])
            if record["status"] in ("empty", "missing"):
                continue
            sizes = [
                len(_read(run_dir / rel).encode("utf-8")) if (run_dir / rel).exists() else 0
                for rel in entry["paths"]
            ]
            filled = [value for value in sizes if value > 0]
            if len(filled) > 1 and min(filled) * 2 < max(filled):
                record["warnings"].append(
                    "language versions differ by more than 2x in size; one translation is likely incomplete"
                )

    counts = {status: 0 for status in ("empty", "draft", "final", "missing")}
    for record in per_deliverable:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
        record["quality"] = "flagged" if record["warnings"] else "clean"

    blocking = [record for record in per_deliverable if record["status"] in ("empty", "missing")]
    flagged = [record for record in per_deliverable if record["warnings"]]
    return {
        "run_id": manifest["run_id"],
        "pipeline": manifest["pipeline"],
        "mode": manifest["mode"],
        "languages": manifest["languages"],
        "counts": counts,
        "total_deliverables": len(per_deliverable),
        "total_unfilled_sections": sum(record["unfilled_sections"] for record in per_deliverable),
        "unverified_markers": sum(item["unverified_markers"] for item in files),
        "filled": not blocking,
        "complete": not blocking and not flagged,
        "deliverables": per_deliverable,
        "blocking": [record["id"] for record in blocking],
        "flagged": [record["id"] for record in flagged],
        "next_actions": _next_actions(blocking, flagged),
    }


def _next_actions(blocking: list[dict], flagged: list[dict]) -> list[str]:
    if blocking:
        return [f"Fill {record['id']}: {record['gate']}" for record in blocking[:5]]
    if flagged:
        return [
            f"Fix {record['id']}: {record['warnings'][0]}" for record in flagged[:5]
        ]
    return ["Run is structurally complete. Review gates, then score against the creative rubric."]


def render_text(report: dict) -> str:
    lines = [
        f"Run {report['run_id']} · {report['pipeline']} · mode={report['mode']} · "
        f"langs={','.join(report['languages'])}",
        f"Deliverables: {report['total_deliverables']} "
        f"(final {report['counts'].get('final', 0)}, draft {report['counts'].get('draft', 0)}, "
        f"empty {report['counts'].get('empty', 0)}, missing {report['counts'].get('missing', 0)})",
        f"Unfilled sections: {report['total_unfilled_sections']} · "
        f"Unverified markers: {report['unverified_markers']}",
        "",
    ]
    for record in report["deliverables"]:
        flag = {"final": "OK  ", "draft": "WIP ", "empty": "TODO", "missing": "MISS"}[record["status"]]
        if record["warnings"]:
            flag = "FLAG"
        lines.append(f"[{flag}] {record['id']:<24} {record['title']}")
        for issue in record["issues"]:
            lines.append(f"         ! {issue}")
        for warning in record["warnings"]:
            lines.append(f"         ~ {warning}")
    lines.append("")
    if report["blocking"]:
        lines.append("INCOMPLETE: " + ", ".join(report["blocking"]))
    elif report["flagged"]:
        lines.append("FILLED BUT FLAGGED: " + ", ".join(report["flagged"]))
    else:
        lines.append("COMPLETE")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit a run workspace for completeness.")
    parser.add_argument("--run", required=True, help="Path to the run directory containing run.json")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument(
        "--strict", action="store_true", help="Exit 1 unless every deliverable is filled and clean"
    )
    parser.add_argument(
        "--allow-warnings",
        action="store_true",
        help="With --strict, fail only on empty or missing deliverables, not on quality warnings",
    )
    parser.add_argument("--output", help="Optional output file")
    args = parser.parse_args()

    report = audit_run(Path(args.run).resolve())
    content = (
        json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.json else render_text(report)
    )
    emit(content, args.output)

    if args.strict:
        passed = report["filled"] if args.allow_warnings else report["complete"]
        if not passed:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
