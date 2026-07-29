#!/usr/bin/env python3
"""Generate a marketing-system brief with separate business job and artifact mode."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit  # noqa: E402


CHANNELS = {
    "meta": ["4:5 feed", "9:16 story/reel", "1:1 proof carousel"],
    "tiktok": ["9:16 native hook", "9:16 proof cutdown"],
    "google": ["1:1 modular image", "1.91:1 landscape", "4:5 portrait"],
    "linkedin": ["1:1 single image", "document/carousel", "1.91:1 link visual"],
    "pinterest": ["2:3 discovery pin", "9:16 idea/video pin"],
    "web": ["wide desktop hero", "mobile hero", "inline proof image"],
}

JOBS = (
    "strategy-offer",
    "campaign-launch",
    "content-distribution",
    "commerce-merchandising",
    "pr-communications",
    "sales-enablement",
    "creator-ugc",
    "lifecycle-retention",
    "creative-production",
    "measurement-optimization",
)
ARTIFACT_MODES = ("campaign", "product", "human", "virtual-person", "edit", "creative-tool-ui", "mixed")
INDUSTRIES = (
    "beauty",
    "fashion",
    "food-cpg",
    "saas-b2b",
    "ecommerce",
    "hospitality",
    "wellness",
    "local-service",
    "creator-education",
    "other",
)
PROVIDERS = (
    "generic",
    "gpt-image-2",
    "nano-banana-2-lite",
    "nano-banana-2",
    "nano-banana-pro",
    "midjourney",
    "flux",
    "ideogram",
    "firefly",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Marketing-Minthep production brief.")
    parser.add_argument("--project", required=True)
    parser.add_argument("--job", choices=JOBS, default="campaign-launch")
    parser.add_argument("--artifact-mode", choices=ARTIFACT_MODES, default="mixed")
    parser.add_argument("--industry", choices=INDUSTRIES, default="other")
    parser.add_argument("--provider", choices=PROVIDERS, default="generic")
    parser.add_argument("--channels", nargs="+", default=["meta", "tiktok", "web"])
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output")
    return parser.parse_args()


def selected_channels(raw: list[str]) -> list[str]:
    values = [item.strip().lower() for group in raw for item in group.split(",") if item.strip()]
    unknown = [item for item in values if item not in CHANNELS]
    if unknown:
        raise SystemExit(f"Unknown channel(s): {', '.join(unknown)}")
    return list(dict.fromkeys(values))


def build_record(
    project: str,
    artifact_mode: str,
    industry: str,
    provider: str,
    channels: list[str],
    job: str = "campaign-launch",
) -> dict:
    assets = []
    counter = 1
    for channel in channels:
        for deliverable in CHANNELS[channel]:
            assets.append(
                {
                    "asset_id": f"ASSET-{counter:03d}",
                    "channel": channel,
                    "deliverable": deliverable,
                    "funnel_stage": "TBD",
                    "concept_lane": "TBD",
                    "hypothesis": "TBD",
                    "hook": "TBD",
                    "proof": "TBD",
                    "cta": "TBD",
                    "status": "planned",
                }
            )
            counter += 1

    return {
        "schema_version": 3,
        "project": project,
        "primary_job": job,
        "artifact_mode": artifact_mode,
        "industry": industry,
        "provider": provider,
        "truth_map": {"confirmed": [], "observed": [], "inferred": [], "unknown": []},
        "brief": {
            "objective": "TBD",
            "conversion_action": "TBD",
            "audience": "TBD",
            "market": "TBD",
            "product_truth": "TBD",
            "mechanism": "TBD",
            "offer": "TBD",
            "proof": "TBD",
            "brand_assets": "TBD",
            "anti_references": "TBD",
            "constraints": "TBD",
            "success_metric": "TBD",
        },
        "message_ladder": {
            "tension": "TBD",
            "promise": "TBD",
            "mechanism": "TBD",
            "proof": "TBD",
            "action": "TBD",
        },
        "concept_lanes": [
            {"name": "Clear", "idea": "TBD", "visual_grammar": "TBD", "risk": "TBD"},
            {"name": "Signature", "idea": "TBD", "visual_grammar": "TBD", "risk": "TBD"},
            {"name": "Departure", "idea": "TBD", "visual_grammar": "TBD", "risk": "TBD"},
        ],
        "references": [],
        "locks": {"product": [], "identity": [], "copy": [], "claims": []},
        "assets": assets,
        "qa": {"critical_gates": {}, "scores": {}, "rejection_reasons": []},
        "open_questions": [],
    }


def to_markdown(record: dict) -> str:
    brief = record["brief"]
    ladder = record["message_ladder"]
    lines = [
        f"# {record['project']} Creative System",
        "",
        f"Job: `{record['primary_job']}` | Artifact mode: `{record['artifact_mode']}` | Industry: `{record['industry']}` | Provider: `{record['provider']}`",
        "",
        "## Truth Map",
        "",
        "- Confirmed: TBD",
        "- Observed: TBD",
        "- Inferred: TBD",
        "- Unknown: TBD",
        "",
        "## Brief",
        "",
    ]
    lines.extend(f"- **{key.replace('_', ' ').title()}**: {value}" for key, value in brief.items())
    lines.extend(["", "## Message Ladder", ""])
    lines.extend(f"- **{key.title()}**: {value}" for key, value in ladder.items())
    lines.extend(["", "## Concept Lanes", ""])
    for lane in record["concept_lanes"]:
        lines.append(
            f"- **{lane['name']}**: {lane['idea']} | Grammar: {lane['visual_grammar']} | Risk: {lane['risk']}"
        )
    lines.extend(
        [
            "",
            "## Asset Manifest",
            "",
            "| ID | Channel | Deliverable | Stage | Lane | Hypothesis | Hook | Proof | CTA |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for asset in record["assets"]:
        lines.append(
            "| {asset_id} | {channel} | {deliverable} | {funnel_stage} | {concept_lane} | "
            "{hypothesis} | {hook} | {proof} | {cta} |".format(**asset)
        )
    lines.extend(
        [
            "",
            "## Locks and QA",
            "",
            "- Product, identity, copy, and claim locks: TBD",
            "- Critical gates: TBD",
            "- Rejection reasons: TBD",
            "- Verification performed: TBD",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    record = build_record(
        args.project,
        args.artifact_mode,
        args.industry,
        args.provider,
        selected_channels(args.channels),
        args.job,
    )
    content = json.dumps(record, indent=2, ensure_ascii=True) + "\n" if args.format == "json" else to_markdown(record)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    emit(content, args.output)


if __name__ == "__main__":
    main()
