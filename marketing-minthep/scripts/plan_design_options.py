#!/usr/bin/env python3
"""Create bounded design directions before rendering a menu or branded artefact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit_json  # noqa: E402


def plan_options(request: dict) -> dict:
    artefact = str(request.get("artefact") or request.get("format") or "menu").lower()
    product = str(request.get("product") or request.get("subject") or "product").strip()
    options = [
        {"id": "quiet-editorial", "name": "Quiet editorial", "best_for": "Premium positioning and calm browsing", "palette": ["warm paper", "ink black", "one accent"], "layout": "Generous margins, one dominant image, restrained type scale", "risk": "Can feel sparse if proof and hierarchy are weak"},
        {"id": "modern-street", "name": "Modern street", "best_for": "Fast scanning and social-friendly energy", "palette": ["off-white", "charcoal", "signal red"], "layout": "Modular cards, bold numerals, diagonal crop or sticker accent", "risk": "Can become noisy; cap accents and type weights"},
        {"id": "heritage-craft", "name": "Heritage craft", "best_for": "Local provenance and sensory storytelling", "palette": ["natural kraft", "deep green", "clay"], "layout": "Editorial columns, ingredient notes, tactile texture", "risk": "Can read old-fashioned without a contemporary grid"},
    ]
    if artefact not in {"menu", "wireframe", "poster", "landing", "packaging"}:
        artefact = "menu"
    return {
        "schema_version": 1,
        "artefact": artefact,
        "subject": product,
        "decision_rule": "Choose one direction before rendering; preserve the same content and change one visual axis per variant.",
        "options": options,
        "required_inputs": ["exact content and prices", "delivery size or print trim", "brand assets and rights", "primary customer action", "must-keep product details"],
        "qa_gates": ["All text is exact and readable at delivery size", "Price and product facts match source", "Contrast and safe areas pass", "No invented garnish, packaging, logo, or claim"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    emit_json(plan_options(json.loads(Path(args.input).read_text(encoding="utf-8-sig"))), args.output)


if __name__ == "__main__":
    main()
