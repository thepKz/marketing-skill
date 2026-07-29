#!/usr/bin/env python3
"""Route a broad marketing request into focused workbenches and asset outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
FORMAT_REGISTRY = ROOT / "assets" / "registries" / "asset-formats.json"

JOB_MODULES = {
    "strategy-offer": ["marketing-foundation.md", "brand-dna.md", "rights-and-claims.md"],
    "campaign-launch": ["campaign-systems.md", "paid-media-creative.md", "channel-deliverables.md"],
    "content-distribution": ["content-system.md", "copywriting.md", "channel-deliverables.md"],
    "commerce-merchandising": ["commerce-merchandising.md", "product-category-playbooks.md", "product-imagery.md"],
    "pr-communications": ["pr-communications.md", "rights-and-claims.md", "source-map.md"],
    "sales-enablement": ["sales-enablement.md", "copywriting.md", "rights-and-claims.md"],
    "creator-ugc": ["creator-ugc.md", "channel-deliverables.md", "rights-and-claims.md"],
    "lifecycle-retention": ["lifecycle-retention.md", "copywriting.md", "learning-loop.md"],
    "creative-production": ["reference-first-image-flow.md", "product-imagery.md", "realistic-studio-imagery.md"],
    "measurement-optimization": ["learning-loop.md", "creative-evaluation.md", "production-pipeline.md"],
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
    channels = [str(item).lower() for item in request.get("channels", [])]
    scope = str(request.get("asset_scope", "focused")).lower()
    limit = {"focused": 8, "system": 14, "production": 24}.get(scope, 8)
    active_jobs = inferred_jobs if scope in {"system", "production"} else inferred_jobs[:1]
    families = list(dict.fromkeys(family for active_job in active_jobs for family in JOB_FAMILIES[active_job]))
    candidates = [item for item in _load_formats() if item["family"] in families]
    if channels:
        matching = [item for item in candidates if set(item["channels"]) & set(channels)]
        candidates = matching or candidates

    selected = []
    seen_families = set()
    for item in candidates:
        if item["family"] not in seen_families:
            selected.append(item)
            seen_families.add(item["family"])
    for item in candidates:
        if item not in selected and len(selected) < limit:
            selected.append(item)

    product_family = str(request.get("product_family", "other")).lower()
    proof_requirements = PRODUCT_PROOF.get(product_family, PRODUCT_PROOF["other"])
    questions = []
    if not request.get("objective"):
        questions.append("What business outcome or customer action should this work create?")
    if not request.get("product_family"):
        questions.append("What kind of product, service, or offer is being promoted?")
    if not request.get("proof"):
        questions.append("Which product facts, demonstrations, reviews, data, or assets are confirmed and usable as proof?")

    overlays = []
    text = " ".join(str(value) for value in request.values()).lower()
    if any(word in text for word in ("virtual person", "ai model", "người ảo")):
        overlays.extend(["virtual-person-system.md", "makeup-art-direction.md"])
    if request.get("reference_assets") or request.get("art_direction"):
        overlays.extend(["reference-first-image-flow.md", "prompt-contracts.md"])

    return {
        "primary_job": job,
        "supporting_jobs": active_jobs[1:],
        "asset_scope": scope,
        "modules_to_load": list(dict.fromkeys([module for active_job in active_jobs for module in JOB_MODULES[active_job]] + overlays)),
        "product_family": product_family,
        "proof_requirements": proof_requirements,
        "selected_assets": selected,
        "asset_count": len(selected),
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
