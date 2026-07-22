#!/usr/bin/env python3
"""Summarize campaign creative performance without overstating causality."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def number(row: dict, key: str) -> float:
    raw = row.get(key, "")
    return float(raw) if raw not in (None, "") else 0.0


def ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def analyze(rows: list[dict]) -> list[dict]:
    results = []
    for row in rows:
        impressions = number(row, "impressions")
        clicks = number(row, "clicks")
        views3s = number(row, "views3s")
        conversions = number(row, "conversions")
        spend = number(row, "spend")
        revenue = number(row, "revenue")
        results.append(
            {
                "asset_id": row.get("asset_id", "UNKNOWN"),
                "lane": row.get("lane", ""),
                "channel": row.get("channel", ""),
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "ctr": ratio(clicks, impressions),
                "view3s_rate": ratio(views3s, impressions),
                "cvr": ratio(conversions, clicks),
                "cpa": ratio(spend, conversions),
                "roas": ratio(revenue, spend),
                "sample_warning": impressions < 1000 or clicks < 30,
            }
        )
    return sorted(results, key=lambda item: (item["conversions"], item["clicks"]), reverse=True)


def percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.2f}%"


def money(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def to_markdown(results: list[dict]) -> str:
    lines = [
        "# Creative Performance Report",
        "",
        "| Asset | Lane | Channel | Impressions | CTR | 3s rate | CVR | CPA | ROAS | Warning |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for item in results:
        lines.append(
            f"| {item['asset_id']} | {item['lane']} | {item['channel']} | {int(item['impressions'])} | "
            f"{percent(item['ctr'])} | {percent(item['view3s_rate'])} | {percent(item['cvr'])} | "
            f"{money(item['cpa'])} | {money(item['roas'])} | {'small sample' if item['sample_warning'] else ''} |"
        )
    lines.extend(
        [
            "",
            "Interpretation guardrail: ranking is descriptive, not causal. Check offer, audience, placement, spend, and landing-page continuity before declaring a creative winner.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze creative performance CSV.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output")
    args = parser.parse_args()
    with Path(args.input).open(encoding="utf-8", newline="") as handle:
        results = analyze(list(csv.DictReader(handle)))
    content = json.dumps(results, indent=2, ensure_ascii=True) + "\n" if args.format == "json" else to_markdown(results)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
