#!/usr/bin/env python3
"""Validate critical gates and score a creative evaluation record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit  # noqa: E402


MAX_SCORES = {
    "strategy": 20,
    "fidelity": 20,
    "distinction": 20,
    "craft": 20,
    "channel": 10,
    "rights_claims": 10,
}


def evaluate(record: dict) -> dict:
    gates = record.get("critical_gates", {})
    failed = sorted(name for name, passed in gates.items() if passed is False)
    scores = record.get("scores", {})
    normalized = {}
    for name, maximum in MAX_SCORES.items():
        raw = float(scores.get(name, 0))
        if raw < 0 or raw > maximum:
            raise ValueError(f"Score {name} must be between 0 and {maximum}")
        normalized[name] = raw
    total = sum(normalized.values())
    if failed:
        status = "rejected-critical"
    elif total >= 90:
        status = "production-candidate"
    elif total >= 80:
        status = "strong-revise"
    elif total >= 70:
        status = "promising-rebuild-gaps"
    elif total >= 50:
        status = "revise"
    else:
        status = "reject"
    return {
        "asset_id": record.get("asset_id", "UNKNOWN"),
        "total": total,
        "maximum": 100,
        "status": status,
        "failed_critical_gates": failed,
        "scores": normalized,
        "rejection_reasons": record.get("rejection_reasons", []),
        "notes": record.get("notes", []),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score a creative QA record.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    record = json.loads(Path(args.input).read_text(encoding="utf-8"))
    content = json.dumps(evaluate(record), indent=2, ensure_ascii=True) + "\n"
    emit(content, args.output)


if __name__ == "__main__":
    main()

