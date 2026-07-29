#!/usr/bin/env python3
"""Turn a vague research request into a traceable, bounded research plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json  # noqa: E402


SOURCE_TIERS = {
    "official": "Official regulator, platform, company filing, or first-party documentation.",
    "primary": "Direct customer, menu, listing, interview, survey, or observed competitor evidence.",
    "secondary": "Reputable research, trade publication, or analyst synthesis; verify its method.",
    "discovery": "Search snippets, social posts, forums, and directories used only to find stronger sources.",
}


def build_plan(request: dict) -> dict:
    objective = str(request.get("objective") or request.get("request") or "Understand the market and customer").strip()
    category = str(request.get("category") or request.get("product_family") or "the category").strip()
    market = str(request.get("market") or request.get("geography") or "the target market").strip()
    questions = [
        {
            "id": "demand",
            "question": f"Is there observable demand for {category} in {market}?",
            "source_tier": ["primary", "secondary"],
            "queries": [f"{category} {market} customer demand", f"{category} {market} search trend", f"{category} {market} reviews"],
            "stop_condition": "At least three independent demand signals with dates, methods, and bias noted.",
        },
        {
            "id": "competition",
            "question": f"Who do buyers compare with or substitute for {category} in {market}?",
            "source_tier": ["primary", "official", "discovery"],
            "queries": [f"best {category} {market}", f"{category} price {market}", f"{category} alternative {market}"],
            "stop_condition": "Five to ten direct/indirect alternatives, each with a source, price or offer observation, and positioning note.",
        },
        {
            "id": "buyer-language",
            "question": "What words, objections, and moments do real buyers use?",
            "source_tier": ["primary", "discovery"],
            "queries": [f"{category} review", f"{category} complaint", f"{category} recommendation {market}"],
            "stop_condition": "Ten verbatim phrases from attributable sources, grouped into jobs, anxieties, and objections.",
        },
        {
            "id": "constraints",
            "question": "Which platform, legal, operational, or seasonal constraints can change the plan?",
            "source_tier": ["official", "secondary"],
            "queries": [f"{category} regulation {market}", "official platform advertising requirements", f"{category} seasonality {market}"],
            "stop_condition": "Every time-sensitive constraint has an official URL, retrieval date, owner, and review date.",
        },
    ]
    return {
        "schema_version": 1,
        "objective": objective,
        "scope": {"category": category, "market": market},
        "source_tiers": SOURCE_TIERS,
        "questions": questions,
        "evidence_ledger_fields": ["source_id", "url", "retrieved_at", "source_tier", "observation", "claim_supported", "bias", "confidence"],
        "synthesis_rules": [
            "Separate observed facts from inference and recommendation.",
            "Show arithmetic for bottom-up sizing; use ranges, not false precision.",
            "Do not turn search volume, likes, or one review into market proof.",
            "Mark unanswered questions and the cheapest next research action.",
        ],
    }


def to_markdown(plan: dict) -> str:
    lines = ["# Research plan / Kế hoạch nghiên cứu", "", f"**Objective:** {plan['objective']}", "", "## Scope", "", f"- Category: `{plan['scope']['category']}`", f"- Market: `{plan['scope']['market']}`", "", "## Questions", ""]
    for item in plan["questions"]:
        lines += [f"### {item['id']}: {item['question']}", "", f"- Source tiers: {', '.join(item['source_tier'])}", f"- Queries: {'; '.join(item['queries'])}", f"- Stop condition: {item['stop_condition']}", ""]
    lines += ["## Evidence ledger", "", "| source_id | url | retrieved_at | tier | observation | claim_supported | bias | confidence |", "|---|---|---|---|---|---|---|---|", "| — | — | — | — | Add evidence during live research | — | — | — |", "", "## Synthesis rules", ""]
    lines += [f"- {rule}" for rule in plan["synthesis_rules"]]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--markdown-output")
    args = parser.parse_args()
    plan = build_plan(json.loads(Path(args.input).read_text(encoding="utf-8-sig")))
    if args.markdown_output:
        Path(args.markdown_output).write_text(to_markdown(plan), encoding="utf-8")
    emit_json(plan, args.output)


if __name__ == "__main__":
    main()
