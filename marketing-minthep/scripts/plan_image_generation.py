#!/usr/bin/env python3
"""Plan reference-first image generation across GPT Image 2 and Nano Banana."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PROVIDER_ALIASES = {
    "openai": "gpt-image-2",
    "gpt-image-2": "gpt-image-2",
    "nano-banana-2-lite": "nano-banana-2-lite",
    "gemini-3.1-flash-lite-image": "nano-banana-2-lite",
    "nano-banana-2": "nano-banana-2",
    "gemini-3.1-flash-image": "nano-banana-2",
    "nano-banana-pro": "nano-banana-pro",
    "gemini-3-pro-image": "nano-banana-pro",
}

MODEL_BY_PROVIDER = {
    "gpt-image-2": "gpt-image-2",
    "nano-banana-2-lite": "gemini-3.1-flash-lite-image",
    "nano-banana-2": "gemini-3.1-flash-image",
    "nano-banana-pro": "gemini-3-pro-image",
}


def _reference_count(request: dict) -> int:
    refs = request.get("reference_images", [])
    if isinstance(refs, int):
        return max(refs, 0)
    return len(refs or [])


def _choose_provider(request: dict, ref_count: int, variants: int) -> str:
    preferred = str(request.get("provider_preference", "auto")).lower()
    if preferred != "auto":
        if preferred not in PROVIDER_ALIASES:
            raise ValueError(f"Unsupported provider preference: {preferred}")
        return PROVIDER_ALIASES[preferred]

    complex_work = bool(request.get("complex_layout_or_text") or request.get("brand_precision"))
    consistency = bool(request.get("needs_character_consistency") or request.get("needs_object_consistency"))
    multi_turn = bool(request.get("multi_turn"))
    same_prompt = bool(request.get("same_prompt_variants", variants > 1))
    latency = str(request.get("latency_priority", "balanced")).lower()

    if complex_work:
        return "nano-banana-pro"
    if consistency or ref_count >= 4:
        return "nano-banana-2"
    if latency == "fast" and ref_count <= 1 and not multi_turn:
        return "nano-banana-2-lite"
    if ref_count >= 2:
        return "nano-banana-2"
    if variants > 1 and same_prompt and ref_count == 0:
        return "gpt-image-2"
    return "gpt-image-2"


def route_image_request(request: dict) -> dict:
    variants = int(request.get("variant_count", 1))
    if variants < 1 or variants > 5:
        raise ValueError("variant_count must be between 1 and 5 for the interactive skill flow")

    ref_count = _reference_count(request)
    provider = _choose_provider(request, ref_count, variants)
    model = MODEL_BY_PROVIDER[provider]
    operation = str(request.get("operation", "generate")).lower()
    multi_turn = bool(request.get("multi_turn"))
    same_prompt = bool(request.get("same_prompt_variants", variants > 1))
    assumptions = []
    questions = []

    reference_intent = request.get("reference_intent")
    if ref_count and not reference_intent:
        reference_intent = "style-only"
        assumptions.append("Unlabeled references are treated as style-only, not identity locks.")

    if not request.get("description") and not request.get("prompt"):
        questions.append("What should the final image communicate or depict?")

    if operation == "edit" and ref_count == 0:
        questions.append("Which supplied image is the edit target that must remain locked?")

    if provider == "gpt-image-2":
        if multi_turn:
            api_surface = "OpenAI Responses API image_generation tool"
            api_operation = "action=auto" if operation not in ("generate", "edit") else f"action={operation}"
            calls = variants
            variant_strategy = (
                "Branch every exploration variant from the same original response/image context; "
                "use previous_response_id only to refine the selected branch."
            )
        elif ref_count or operation == "edit":
            api_surface = "OpenAI Image API"
            api_operation = "images.edit"
            calls = variants
            variant_strategy = (
                "Run independent edit/reference calls from the same original inputs. "
                "Use one named prompt delta per call; only use multi-output edit behavior after live-spec verification."
            )
        else:
            api_surface = "OpenAI Image API"
            api_operation = "images.generate"
            if variants > 1 and same_prompt:
                calls = 1
                variant_strategy = f"Use n={variants} for same-prompt variants, then inspect and label the outputs."
            else:
                calls = variants
                variant_strategy = "Run independent generation calls with one named delta per variant."
    else:
        api_surface = "Gemini Interactions API"
        api_operation = "interactions.create"
        calls = variants
        variant_strategy = (
            "Start independent interactions from the same canonical references and locks. "
            "Use previous_interaction_id only after selecting a winning direction."
        )

    reasons = {
        "gpt-image-2": "Direct generation/editing and conversational refinement with automatic high-fidelity image inputs.",
        "nano-banana-2-lite": "Lowest-latency route for simple work with few references and no sequential consistency dependency.",
        "nano-banana-2": "Multiple-reference processing and character/object consistency are the dominant requirements.",
        "nano-banana-pro": "Complex layout, text, localization, brand precision, or premium production control is required.",
    }

    return {
        "provider": provider,
        "model": model,
        "api_surface": api_surface,
        "api_operation": api_operation,
        "request_count": calls,
        "variant_count": variants,
        "reference_count": ref_count,
        "reference_intent": reference_intent or "none",
        "variant_strategy": variant_strategy,
        "reason": reasons[provider],
        "assumptions": assumptions,
        "questions": questions,
        "verified_against_official_docs": "2026-07-22",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan GPT Image 2 or Nano Banana execution.")
    parser.add_argument("--input", required=True, help="JSON request file")
    parser.add_argument("--output", help="Optional JSON output file")
    args = parser.parse_args()
    request = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = route_image_request(request)
    content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
