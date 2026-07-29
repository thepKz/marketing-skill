#!/usr/bin/env python3
"""Generate a marketing-system brief with separate business job and artifact mode.

This is the campaign command the README puts in front of people, and it used to answer a request
with a form. Every field came back `TBD` — thirteen in the brief, five in the message ladder, nine
across each of seventeen assets, 153 in total — and it could not read a request even if you had
one, because there was no flag to pass it. Running it produced a document that knew nothing about
the campaign it was named after, and the seventeen assets were the plain cartesian product of the
three default channels and their format lists, which is not a plan; it is a multiplication.

Now `--request` is the main way in. What the sentence states is filled in and labelled; the asset
count follows the budget tier rather than the channel count; and what remains blank is split into
two kinds, because they are not the same kind of gap. `UNKNOWN` means nobody has said and the plan
is blocked until they do — the price, the margin, what proof exists. `TBD` means it is ours to
decide and has not been decided yet, like which concept lane an asset belongs to. A brief that
prints both as `TBD` hides the three questions that actually stop the work.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit  # noqa: E402
from _signals import BUDGET_ASSET_CAP, phase_plan, read_signals  # noqa: E402


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


# The signal reader speaks the proof taxonomy; this file speaks a coarser commercial one. One
# mapping between them, so a request that says "bún bò" reaches food-cpg without the caller
# having to know either list exists.
FAMILY_TO_INDUSTRY = {
    "food-beverage": "food-cpg",
    "beauty": "beauty",
    "fashion": "fashion",
    "saas": "saas-b2b",
    "electronics": "ecommerce",
    "home": "ecommerce",
    "jewelry-luxury": "ecommerce",
    "hospitality": "hospitality",
    "education": "creator-education",
    "service": "local-service",
    "other": "other",
}

# Which channels a business of each shape can actually work. A single storefront with a small
# budget running LinkedIn document carousels is a plan written for somebody else.
LOCAL_CHANNELS = ["meta", "tiktok", "web"]
BROAD_CHANNELS = ["meta", "tiktok", "google", "web"]

# Funnel stages in order, so assets get a stage instead of the string "TBD". An asset without a
# stage cannot be judged, and every asset having the same non-answer is how a manifest of
# seventeen rows carries no information at all.
STAGE_CYCLE = ("discover", "consider", "convert")

UNKNOWN = "UNKNOWN — nobody has stated this; the plan is blocked until they do"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Marketing-Minthep production brief.")
    parser.add_argument("--project", help="Short project name; derived from --request when omitted")
    parser.add_argument("--request", help="The request in the words the client used, VI or EN")
    parser.add_argument("--job", choices=JOBS, default=None)
    parser.add_argument("--artifact-mode", choices=ARTIFACT_MODES, default="mixed")
    parser.add_argument("--industry", choices=INDUSTRIES, default=None)
    parser.add_argument("--provider", choices=PROVIDERS, default="generic")
    parser.add_argument("--channels", nargs="+", default=None)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output")
    args = parser.parse_args()
    if not args.project and not args.request:
        parser.error("Provide --request, or --project, or both.")
    return args


def selected_channels(raw: list[str]) -> list[str]:
    values = [item.strip().lower() for group in raw for item in group.split(",") if item.strip()]
    unknown = [item for item in values if item not in CHANNELS]
    if unknown:
        raise SystemExit(f"Unknown channel(s): {', '.join(unknown)}")
    return list(dict.fromkeys(values))


def _build_assets(channels: list[str], cap: int) -> list[dict]:
    """Pick assets round-robin across channels, up to the cap, and give each one a real stage.

    Round-robin rather than channel-by-channel: taking the first `cap` rows off a nested loop
    spends the whole allowance on the first channel and silently leaves the others with nothing,
    which reads as a decision about channels that nobody made.
    """
    queues = [[(channel, item) for item in CHANNELS[channel]] for channel in channels]
    ordered: list[tuple[str, str]] = []
    for index in range(max((len(queue) for queue in queues), default=0)):
        for queue in queues:
            if index < len(queue):
                ordered.append(queue[index])

    assets = []
    for counter, (channel, deliverable) in enumerate(ordered[:cap], start=1):
        assets.append(
            {
                "asset_id": f"ASSET-{counter:03d}",
                "channel": channel,
                "deliverable": deliverable,
                "funnel_stage": STAGE_CYCLE[(counter - 1) % len(STAGE_CYCLE)],
                "concept_lane": "TBD",
                "hypothesis": "TBD",
                "hook": "TBD",
                "proof": UNKNOWN,
                "cta": "TBD",
                "status": "planned",
            }
        )
    return assets


def build_record(
    project: str,
    artifact_mode: str,
    industry: str,
    provider: str,
    channels: list[str],
    job: str = "campaign-launch",
    request: str = "",
) -> dict:
    signals = read_signals(request or project)
    horizon, budget, market = signals["horizon"], signals["budget"], signals["market"]
    cap = BUDGET_ASSET_CAP.get(budget["tier"], BUDGET_ASSET_CAP["unstated"])
    assets = _build_assets(channels, cap)

    inferred = []
    if horizon["stated"]:
        inferred.append(f"Horizon {horizon['weeks']} weeks, read from \"{horizon['evidence']}\"")
    if budget["stated"]:
        inferred.append(f"Budget pressure {budget['tier']}, read from \"{budget['evidence']}\"")
    if signals["product_family"]["family"] != "other":
        inferred.append(
            f"Product family {signals['product_family']['family']}, read from "
            f"\"{signals['product_family']['evidence'][0]}\" -> industry {industry}"
        )
    if market["places"]:
        inferred.append(f"Market Vietnam, read from \"{market['places'][0]}\"" +
                        (", single location" if market["single_location"] else ""))

    return {
        "schema_version": 4,
        "project": project,
        "request": request,
        "primary_job": job,
        "artifact_mode": artifact_mode,
        "industry": industry,
        "provider": provider,
        "signals": signals,
        "horizon_weeks": horizon["weeks"],
        "horizon_stated": horizon["stated"],
        "phases": phase_plan(horizon["weeks"]),
        "budget_tier": budget["tier"],
        "asset_cap": cap,
        "truth_map": {
            "confirmed": [f"Request as stated: {request}"] if request else [],
            "observed": [],
            "inferred": inferred,
            "unknown": [
                "Unit price and variable cost",
                "What proof exists and is usable",
                "Which brand assets and rights are in hand",
            ],
        },
        "brief": {
            "objective": "TBD",
            "conversion_action": "TBD",
            "audience": "TBD",
            "market": f"Vietnam ({market['places'][0]})" if market["places"] else UNKNOWN,
            "product_truth": UNKNOWN,
            "mechanism": UNKNOWN,
            "offer": "TBD",
            "proof": UNKNOWN,
            "brand_assets": UNKNOWN,
            "anti_references": "TBD",
            "constraints": (
                f"{horizon['weeks']}-week horizon"
                + (f" (stated: \"{horizon['evidence']}\")" if horizon["stated"] else " (assumed, not stated)")
                + f"; {budget['tier']} budget; at most {cap} assets"
            ),
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
        # Three, and only the ones whose answers change the plan. The horizon question appears
        # only when the request did not state one, so a client who already said "6 tuần" is not
        # asked for it a second time.
        "open_questions": (
            [] if horizon["stated"] else ["How long is the campaign? This brief assumes 13 weeks."]
        ) + [
            "What does one unit sell for, and what does it cost to make? The CAC ceiling derives from those two.",
            "Which product facts, demos, or results are confirmed and usable as proof?",
            "Which brand assets, photos, and permissions are already in hand?",
        ][: 3 if horizon["stated"] else 2],
    }


def to_markdown(record: dict) -> str:
    brief = record["brief"]
    ladder = record["message_ladder"]
    horizon_note = (
        f"{record['horizon_weeks']} weeks"
        if record["horizon_stated"]
        else f"{record['horizon_weeks']} weeks (assumed — not stated)"
    )
    lines = [
        f"# {record['project']} Creative System",
        "",
        f"Job: `{record['primary_job']}` | Artifact mode: `{record['artifact_mode']}` | "
        f"Industry: `{record['industry']}` | Provider: `{record['provider']}`",
        "",
        f"Horizon: **{horizon_note}** | Budget tier: **{record['budget_tier']}** | "
        f"Assets: **{len(record['assets'])}** of at most {record['asset_cap']}",
        "",
    ]
    if record.get("request"):
        lines += [f"> {record['request']}", "", "*The request as received. Everything below it is "
                  "either read from that sentence and labelled, or still open.*", ""]
    lines += ["## Truth Map", ""]
    for key in ("confirmed", "observed", "inferred", "unknown"):
        entries = record["truth_map"][key]
        if entries:
            lines.append(f"- **{key.title()}**:")
            lines.extend(f"  - {entry}" for entry in entries)
        else:
            lines.append(f"- **{key.title()}**: none recorded yet")
    lines += ["", "## Phases", "", "| Phase | Weeks | Days | Learning goal |", "|---|---|---|---|"]
    for phase in record["phases"]:
        lines.append(
            f"| {phase['name_en']} | {phase['week_from']}-{phase['week_to']} | "
            f"{phase['day_from']}-{phase['day_to']} | {phase['goal_en']} |"
        )
    lines += [
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
        # The full UNKNOWN sentence is unreadable inside a nine-column table, so the cell carries
        # the token and the legend under the table carries the meaning.
        row = dict(asset, proof="UNKNOWN" if asset["proof"] == UNKNOWN else asset["proof"])
        lines.append(
            "| {asset_id} | {channel} | {deliverable} | {funnel_stage} | {concept_lane} | "
            "{hypothesis} | {hook} | {proof} | {cta} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Locks and QA",
            "",
            "- Product, identity, copy, and claim locks: TBD",
            "- Critical gates: TBD",
            "- Rejection reasons: TBD",
            "- Verification performed: none. Nothing in this file has been produced or checked.",
            "",
            "## Open questions",
            "",
        ]
    )
    lines.extend(f"{index}. {question}" for index, question in enumerate(record["open_questions"], start=1))
    lines.extend(
        [
            "",
            "`UNKNOWN` above means nobody has stated it and the plan is blocked until they do. "
            "`TBD` means it is ours to decide and has not been decided. Do not fill an `UNKNOWN` "
            "with a plausible guess — that is the one move that turns a brief into a lie.",
            "",
        ]
    )
    return "\n".join(lines)


def _clause(text: str, limit: int = 60) -> str:
    """The first clause of a request, for use as a heading."""
    head = str(text).strip().split("\n")[0]
    for separator in (",", ".", ";", " - ", " — "):
        if separator in head:
            head = head.split(separator)[0].strip()
            break
    if len(head) <= limit:
        return head
    clipped = head[:limit]
    boundary = clipped.rfind(" ")
    return (clipped[:boundary] if boundary >= limit // 2 else clipped).strip()


def derive_inputs(args: argparse.Namespace) -> dict:
    """Fill the flags the caller did not pass from the request text.

    Explicit flags always win: a caller who names an industry has told us something the wording
    could only be guessed at. Everything else comes from the sentence, which is the point — the
    previous defaults meant `--request` could have existed and still changed nothing.
    """
    request = (args.request or "").strip()
    signals = read_signals(request or args.project or "")
    family = signals["product_family"]["family"]
    industry = args.industry or FAMILY_TO_INDUSTRY.get(family, "other")
    if args.channels:
        channels = selected_channels(args.channels)
    else:
        channels = LOCAL_CHANNELS if signals["market"]["single_location"] else BROAD_CHANNELS
    # First clause, not first sixty characters. A hard slice produced the heading "Tôi bán bún bò
    # ở Sài Gòn, muốn lên chiến dịch ra mắt trong 6 Creative System", which cuts a sentence in
    # half and then attaches a English noun phrase to the wound.
    project = args.project or _clause(request) or "Untitled campaign"
    return {
        "project": project,
        "request": request,
        "industry": industry,
        "channels": channels,
        "job": args.job or "campaign-launch",
    }


def main() -> None:
    args = parse_args()
    derived = derive_inputs(args)
    record = build_record(
        derived["project"],
        args.artifact_mode,
        derived["industry"],
        args.provider,
        derived["channels"],
        derived["job"],
        request=derived["request"],
    )
    content = json.dumps(record, indent=2, ensure_ascii=True) + "\n" if args.format == "json" else to_markdown(record)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    emit(content, args.output)


if __name__ == "__main__":
    main()
