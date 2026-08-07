#!/usr/bin/env python3
"""Route a broad marketing request into focused workbenches and asset outputs.

Two things here used to make the output wrong for the request that produced it. `product_family`
defaulted to `other` unless the caller passed the taxonomy key by hand, so "Tôi bán bún bò" got
the generic proof list — "product recognition, mechanism, use context" — when a food-beverage
entry with "appetite and texture, preparation, occasion and serving" was sitting in the table
unused. And the asset list was capped only by `asset_scope`, so a shop that said "ngân sách nhỏ"
was handed eight assets including an out-of-home key visual, a conceptual art still life, and a
LinkedIn carousel: a plan for a company it is not, and eight shoots it cannot pay for.

The budget tier now caps the count and removes channels the tier cannot sustain, and the open
questions are only the ones the request has not already answered. Asking "What kind of product is
being promoted?" of someone who opened with what they sell is the single clearest way for a tool
to announce that it did not read the input.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit  # noqa: E402
from _signals import (  # noqa: E402
    BUDGET_ASSET_CAP,
    BUDGET_EXCLUDED_CHANNELS,
    BUDGET_EXCLUDED_FAMILIES,
    read_signals,
)

ROOT = Path(__file__).resolve().parents[1]
FORMAT_REGISTRY = ROOT / "assets" / "registries" / "asset-formats.json"

JOB_MODULES = {
    "strategy-offer": ["marketing-canon.md", "identity-design.md", "claims-proof-ledger.md"],
    "campaign-launch": ["campaign-systems.md", "campaign-systems.md", "channel-spec-registry.md"],
    "content-distribution": ["copywriting.md", "copywriting.md", "channel-spec-registry.md"],
    "commerce-merchandising": ["product-category-playbooks.md", "product-category-playbooks.md", "product-imagery.md"],
    "pr-communications": ["pr-communications.md", "claims-proof-ledger.md", "source-map.md"],
    "sales-enablement": ["lead-handling.md", "copywriting.md", "claims-proof-ledger.md"],
    "creator-ugc": ["affiliate-commerce.md", "channel-spec-registry.md", "claims-proof-ledger.md"],
    "lifecycle-retention": ["lifecycle-retention.md", "copywriting.md", "performance-direction.md"],
    "creative-production": ["reference-reading.md", "product-imagery.md", "realistic-studio-imagery.md"],
    "measurement-optimization": ["performance-direction.md", "output-contract.md"],
}

JOB_FAMILIES = {
    "strategy-offer": ["owned"],
    "campaign-launch": ["campaign", "content", "owned", "art"],
    "content-distribution": ["content", "owned"],
    "commerce-merchandising": ["commerce", "owned"],
    "pr-communications": ["pr", "art"],
    "sales-enablement": ["sales", "owned"],
    "creator-ugc": ["content", "campaign"],
    "lifecycle-retention": ["lifecycle", "content"],
    "creative-production": ["commerce", "campaign", "art"],
    "measurement-optimization": [],
}

PRODUCT_PROOF = {
    "beauty": ["texture/application", "exact shade and pack", "ingredient or mechanism evidence", "real skin behavior"],
    "fashion": ["fit and silhouette", "fabric/construction", "styling range", "size and detail"],
    "food-beverage": ["appetite and texture", "preparation", "pack recognition", "occasion and serving"],
    "electronics": ["interface or function", "scale and ports", "setup", "comparison and compatibility"],
    "home": ["room scale", "material and finish", "assembly or care", "before/after use context"],
    "jewelry-luxury": ["material and craft", "scale on body", "closure and detail", "provenance when confirmed"],
    "saas": ["real workflow", "interface artifact", "time/risk change", "integration or customer evidence"],
    "service": ["process", "staff expertise", "site or tool evidence", "case outcome and next step"],
    "education": ["curriculum artifact", "teaching method", "learner work", "credible outcome evidence"],
    "hospitality": ["place and spatial flow", "service moment", "room or amenity truth", "arrival and stay sequence"],
    "other": ["product recognition", "mechanism", "use context", "credible proof"],
}

JOB_KEYWORDS = {
    "strategy-offer": (
        "positioning", "offer", "pricing", "strategy", "funnel", "marketing plan", "from scratch",
        "định vị", "chào bán", "giá", "chiến lược", "kế hoạch marketing", "từ đầu", "không biết marketing",
    ),
    "campaign-launch": ("launch", "campaign", "promotion", "paid ads", "paid campaign", "quảng cáo"),
    "content-distribution": ("content", "seo", "social", "editorial", "calendar", "blog", "nội dung", "lịch nội dung"),
    "commerce-merchandising": ("pdp", "marketplace", "listing", "catalog", "sell", "rao bán", "ecommerce", "retail"),
    "pr-communications": ("press", "public relations", "journalist", "earned media", "newsroom", "pr launch"),
    "sales-enablement": ("sales deck", "proposal", "battlecard", "demo script", "sales kit", "one-pager"),
    "creator-ugc": ("creator", "ugc", "influencer", "kol", "seeding", "whitelisting"),
    "lifecycle-retention": ("retention", "welcome flow", "abandoned cart", "win-back", "post-purchase", "lifecycle"),
    "creative-production": ("image", "photo", "visual", "art direction", "hình ảnh", "ảnh", "studio", "chụp hình"),
    "measurement-optimization": ("analyze", "performance", "optimize", "report", "roas", "cpa", "measurement"),
}

CHANNEL_JOB_SIGNALS = {
    "pdp": "commerce-merchandising",
    "marketplace": "commerce-merchandising",
    "catalog": "commerce-merchandising",
    "retail": "commerce-merchandising",
    "paid": "campaign-launch",
    "meta": "campaign-launch",
    "google": "campaign-launch",
    "pr": "pr-communications",
    "newsroom": "pr-communications",
    "sales": "sales-enablement",
    "creator": "creator-ugc",
    "email": "lifecycle-retention",
    "sms": "lifecycle-retention",
    "instagram": "content-distribution",
    "tiktok": "content-distribution",
    "linkedin": "content-distribution",
}


def _infer_jobs(request: dict) -> list[str]:
    explicit = str(request.get("primary_job", "auto")).lower()
    text = " ".join(
        str(request.get(key, ""))
        for key in ("request", "objective", "notes", "project", "deliverable")
    ).lower()
    scores = {job: sum(1 for word in words if word in text) for job, words in JOB_KEYWORDS.items()}
    for channel in (str(item).lower() for item in request.get("channels", [])):
        signaled_job = CHANNEL_JOB_SIGNALS.get(channel)
        if signaled_job:
            scores[signaled_job] += 1

    requested = [str(job).lower() for job in request.get("workbenches", [])]
    invalid = [job for job in requested if job not in JOB_MODULES]
    if invalid:
        raise ValueError(f"Unsupported workbench(es): {', '.join(invalid)}")

    if explicit != "auto":
        if explicit not in JOB_MODULES:
            raise ValueError(f"Unsupported primary_job: {explicit}")
        primary = explicit
    else:
        primary = max(scores, key=scores.get) if any(scores.values()) else "campaign-launch"

    ranked = sorted(JOB_MODULES, key=lambda job: (-scores[job], list(JOB_MODULES).index(job)))
    return list(dict.fromkeys([primary] + requested + [job for job in ranked if scores[job] > 0]))


def _load_formats() -> list[dict]:
    return json.loads(FORMAT_REGISTRY.read_text(encoding="utf-8"))["formats"]


def plan_marketing_system(request: dict) -> dict:
    inferred_jobs = _infer_jobs(request)
    job = inferred_jobs[0]
    signals = read_signals(" ".join(str(value) for value in request.values()))
    budget_tier = str(request.get("budget_tier") or signals["budget"]["tier"]).lower()

    channels = [str(item).lower() for item in request.get("channels", [])]
    scope = str(request.get("asset_scope", "focused")).lower()
    scope_limit = {"focused": 8, "system": 14, "production": 24}.get(scope, 8)
    # The tighter of the two wins. A "production" scope does not buy a shoestring budget
    # twenty-four assets; it only says how thoroughly the ones it can afford are specified.
    limit = min(scope_limit, BUDGET_ASSET_CAP.get(budget_tier, BUDGET_ASSET_CAP["unstated"]))
    active_jobs = inferred_jobs if scope in {"system", "production"} else inferred_jobs[:1]
    families = list(dict.fromkeys(family for active_job in active_jobs for family in JOB_FAMILIES[active_job]))
    candidates = [item for item in _load_formats() if item["family"] in families]
    if channels:
        matching = [item for item in candidates if set(item["channels"]) & set(channels)]
        candidates = matching or candidates

    excluded_channels = set(BUDGET_EXCLUDED_CHANNELS.get(budget_tier, ()))
    excluded_families = set(BUDGET_EXCLUDED_FAMILIES.get(budget_tier, ()))
    dropped = []
    if excluded_channels or excluded_families:
        affordable = []
        for item in candidates:
            item_channels = set(item["channels"])
            if item["family"] in excluded_families:
                dropped.append({"id": item["id"], "name": item["name"],
                                "reason": f"the {item['family']} family is not affordable at a {budget_tier} budget"})
            # Dropped only when the format has nowhere else to run. A 9:16 demo that also lives
            # on TikTok survives a paid-media exclusion; an out-of-home-only visual does not.
            elif item_channels and item_channels <= excluded_channels:
                dropped.append({"id": item["id"], "name": item["name"],
                                "reason": f"{'/'.join(sorted(item_channels))} is out of reach at a {budget_tier} budget"})
            else:
                # Kept, but only for the channels the tier can actually run. Leaving `ooh` on a
                # surviving key visual meant the manifest still listed a billboard for a shop
                # with four assets and a small budget; the asset is fine, the placement is not.
                remaining = [channel for channel in item["channels"] if channel not in excluded_channels]
                affordable.append(dict(item, channels=remaining or item["channels"]))
        candidates = affordable or candidates

    selected = []
    seen_families = set()
    for item in candidates:
        if item["family"] not in seen_families and len(selected) < limit:
            selected.append(item)
            seen_families.add(item["family"])
    for item in candidates:
        if item not in selected and len(selected) < limit:
            selected.append(item)

    explicit_family = str(request.get("product_family", "")).lower()
    product_family = explicit_family or signals["product_family"]["family"]
    proof_requirements = PRODUCT_PROOF.get(product_family, PRODUCT_PROOF["other"])
    questions = []
    if not request.get("objective"):
        questions.append("What business outcome or customer action should this work create?")
    if not explicit_family and signals["product_family"]["family"] == "other":
        questions.append("What kind of product, service, or offer is being promoted?")
    if not request.get("proof"):
        questions.append("Which product facts, demonstrations, reviews, data, or assets are confirmed and usable as proof?")
    # The question the budget deliverable actually blocks on. Unit price and variable cost are the
    # two numbers a CAC ceiling is derived from, and neither can be inferred from wording.
    if budget_tier != "unstated" and not request.get("unit_economics"):
        questions.append("What does one unit sell for, and what does it cost you to make? The CAC ceiling comes from those two numbers and nothing else.")

    overlays = []
    text = " ".join(str(value) for value in request.values()).lower()
    if any(word in text for word in ("virtual person", "ai model", "người ảo")):
        overlays.extend(["virtual-person-system.md", "makeup-art-direction.md"])
    if request.get("reference_assets") or request.get("art_direction"):
        overlays.extend(["reference-reading.md", "prompt-contracts.md"])

    return {
        "primary_job": job,
        "supporting_jobs": active_jobs[1:],
        "asset_scope": scope,
        "modules_to_load": list(dict.fromkeys([module for active_job in active_jobs for module in JOB_MODULES[active_job]] + overlays)),
        "product_family": product_family,
        "product_family_label": "confirmed" if explicit_family else signals["product_family"]["label"],
        "proof_requirements": proof_requirements,
        "budget_tier": budget_tier,
        "asset_cap": limit,
        "signals": signals,
        "selected_assets": selected,
        "asset_count": len(selected),
        "assets_dropped_for_budget": dropped,
        "questions": questions[:3],
        "truth_gate": [
            "Do not invent claims, specifications, reviews, prices, availability, scarcity, labels, or endorsements.",
            "Treat generated packaging without an exact reference as concept art.",
            "Verify current platform specifications before export or upload.",
        ],
        "next_actions": [
            "Confirm or label assumptions.",
            "Create the route-specific artifact pack.",
            "Produce only assets with a defined job, proof, channel, CTA, and acceptance gate.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan an all-in-one marketing workbench and minimum asset system.")
    parser.add_argument("--input", required=True, help="JSON request file")
    parser.add_argument("--output", help="Optional JSON output file")
    args = parser.parse_args()
    request = json.loads(Path(args.input).read_text(encoding="utf-8"))
    content = json.dumps(plan_marketing_system(request), ensure_ascii=False, indent=2) + "\n"
    emit(content, args.output)


if __name__ == "__main__":
    main()
