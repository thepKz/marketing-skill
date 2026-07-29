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
    text = " ".join(str(request.get(key, "")) for key in ("request", "objective", "description", "notes")).lower()
    inferred = "key-visual" if any(word in text for word in ("image", "photo", "ảnh", "key visual", "branding")) else "menu"
    artefact = str(request.get("artefact") or request.get("format") or inferred).lower()
    product = str(request.get("product") or request.get("subject") or "product").strip()
    if artefact in {"key-visual", "image", "photo", "photoshoot"}:
        artefact = "key-visual"
        options = [
            {"id": "precision-studio", "name": "Precision studio", "best_for": "Exact product/identity fidelity and premium clarity", "palette": ["product truth colors", "controlled neutral", "one brand accent"], "layout": "Locked subject, shaped reflection, deliberate copy-safe field", "change_axis": "background material and light geometry", "risk": "Can feel sterile without a distinctive mechanism or material cue"},
            {"id": "material-world", "name": "Material world", "best_for": "Turning a product mechanism into an ownable visual device", "palette": ["product truth colors", "mechanism-derived material", "restrained contrast"], "layout": "Hero product/person grounded in one physical material system", "change_axis": "material behavior and environmental field", "risk": "Generated material may distort labels, skin, hands, or product geometry"},
            {"id": "environmental-editorial", "name": "Environmental editorial", "best_for": "Aspirational context with social and campaign versatility", "palette": ["credible location color", "skin/product truth", "controlled grade"], "layout": "Authored crop with context, action, and channel-safe negative space", "change_axis": "setting and human/product action", "risk": "Context can outcompete the product or cause identity drift"},
        ]
        recommended = "precision-studio" if any(word in text for word in ("giữ nguyên", "preserve", "exact", "edit", "sửa")) else "material-world"
    else:
        if artefact not in {"menu", "wireframe", "poster", "landing", "packaging"}:
            artefact = "menu"
        options = [
            {"id": "quiet-editorial", "name": "Quiet editorial", "best_for": "Premium positioning and calm browsing", "palette": ["warm paper", "ink black", "one accent"], "layout": "Generous margins, one dominant image, restrained type scale", "change_axis": "space and typographic hierarchy", "risk": "Can feel sparse if proof and hierarchy are weak"},
            {"id": "modern-street", "name": "Modern street", "best_for": "Fast scanning and social-friendly energy", "palette": ["off-white", "charcoal", "signal red"], "layout": "Modular rows, bold numerals, diagonal crop or sticker accent", "change_axis": "density and signal color", "risk": "Can become noisy; cap accents and type weights"},
            {"id": "heritage-craft", "name": "Heritage craft", "best_for": "Local provenance and sensory storytelling", "palette": ["natural kraft", "deep green", "clay"], "layout": "Editorial columns, ingredient notes, tactile texture", "change_axis": "provenance and material cues", "risk": "Can read old-fashioned without a contemporary grid"},
        ]
        fast_context = any(word in text for word in ("văn phòng", "fast", "counter", "tiktok", "delivery", "hiện đại"))
        premium_context = any(word in text for word in ("premium", "cao cấp", "fine dining", "tĩnh"))
        recommended = "quiet-editorial" if premium_context else "modern-street" if fast_context else "heritage-craft"
    return {
        "schema_version": 1,
        "artefact": artefact,
        "subject": product,
        "recommended_option": recommended,
        "recommendation_basis": "Derived from the supplied audience, service context, fidelity needs, and requested channel; confirm inferred inputs before final rendering.",
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
