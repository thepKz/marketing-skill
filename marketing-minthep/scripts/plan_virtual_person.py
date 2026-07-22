#!/usr/bin/env python3
"""Plan a fictional adult virtual person before image generation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FACE_OPTIONS = {
    "F1": {"name": "soft-romantic", "impression": "warm, polished, inviting", "risk": "generic or doll-like"},
    "F2": {"name": "cinematic-natural", "impression": "calm, intelligent, credible", "risk": "too quiet at thumbnail size"},
    "F3": {"name": "cool-editorial", "impression": "precise, modern, self-possessed", "risk": "distant or over-sculpted"},
    "F4": {"name": "distinctive-fashion", "impression": "memorable, directional, unconventional", "risk": "novelty overwhelms the product"},
}

BUILD_OPTIONS = {
    "B1": {"name": "slender-light-frame", "guardrail": "healthy adult proportions; no extreme thinness"},
    "B2": {"name": "balanced-natural", "guardrail": "moderate proportions and relaxed posture"},
    "B3": {"name": "athletic-lean", "guardrail": "functional tone without exaggerated definition"},
    "B4": {"name": "soft-curved", "guardrail": "natural soft lines without reshaping"},
}

MAKEUP_OPTIONS = {
    "M1": "fresh-luminous",
    "M2": "quiet-luxury",
    "M3": "douyin-luminous",
    "M4": "cool-crystalline",
    "M5": "sculpted-feline",
    "M6": "smoky-grunge",
    "M7": "graphic-editorial",
}

POSE_OPTIONS = {
    "P1": "gentle-approachable",
    "P2": "quiet-luxury",
    "P3": "direct-idol",
    "P4": "editorial-geometry",
}


def _recommend(request: dict) -> dict:
    text = " ".join(str(request.get(k, "")) for k in ("purpose", "vibe", "audience", "notes")).lower()
    if any(word in text for word in ("douyin", "idol", "romantic", "beauty")):
        return {"face": "F1", "build": "B1", "makeup": "M3", "pose": "P3"}
    if any(word in text for word in ("luxury", "cinematic", "skincare", "credible")):
        return {"face": "F2", "build": "B1", "makeup": "M2", "pose": "P2"}
    if any(word in text for word in ("fashion", "editorial", "cool", "technology")):
        return {"face": "F3", "build": "B1", "makeup": "M4", "pose": "P4"}
    return {"face": "F2", "build": "B2", "makeup": "M1", "pose": "P1"}


def plan_virtual_person(request: dict) -> dict:
    if request.get("minor") is True:
        raise ValueError("This workflow supports fictional adults only")

    recommended = _recommend(request)
    selected = dict(recommended)
    selected.update({k: v for k, v in request.get("selection", {}).items() if v})

    registries = {"face": FACE_OPTIONS, "build": BUILD_OPTIONS, "makeup": MAKEUP_OPTIONS, "pose": POSE_OPTIONS}
    for category, code in selected.items():
        if code not in registries[category]:
            raise ValueError(f"Unsupported {category} option: {code}")

    missing = [key for key in ("purpose", "vibe") if not request.get(key)]
    questions = []
    if "purpose" in missing:
        questions.append("What job should this virtual person perform for the brand?")
    if "vibe" in missing:
        questions.append("Should the dominant impression feel approachable, romantic, cinematic, cool, or distinctive?")
    if not request.get("selection"):
        questions.append("Do you want the recommended combination, or will you choose face/build/makeup/pose codes?")

    return {
        "adult_only": True,
        "purpose": request.get("purpose", "brand-face"),
        "recommended_selection": recommended,
        "active_selection": selected,
        "selected_profile": {
            "face": FACE_OPTIONS[selected["face"]],
            "build": BUILD_OPTIONS[selected["build"]],
            "makeup": MAKEUP_OPTIONS[selected["makeup"]],
            "pose": POSE_OPTIONS[selected["pose"]],
        },
        "options": registries,
        "questions": questions[:3],
        "next_step": "Create a neutral identity sheet before campaign styling.",
        "identity_locks": [
            "face shape and cheek structure",
            "eye spacing and natural lid geometry",
            "nose bridge, width, and tip",
            "lip proportions and resting closure",
            "jaw and chin without extreme narrowing",
            "original distinguishing detail",
            "healthy adult body frame and posture signature",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Return virtual-person options and a recommended identity direction.")
    parser.add_argument("--input", required=True, help="JSON request file")
    parser.add_argument("--output", help="Optional JSON output file")
    args = parser.parse_args()
    request = json.loads(Path(args.input).read_text(encoding="utf-8"))
    content = json.dumps(plan_virtual_person(request), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
