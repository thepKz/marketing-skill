#!/usr/bin/env python3
"""Compile a provider-neutral creative brief into provider-ready prompt text."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit  # noqa: E402


PROVIDERS = (
    "generic",
    "openai",
    "gpt-image-2",
    "nano-banana-2-lite",
    "nano-banana-2",
    "nano-banana-pro",
    "midjourney",
    "flux",
    "ideogram",
    "firefly",
)

CAPTURE_MODES = {
    "studio-clean": "Controlled commercial studio capture with exact materials and restrained retouching.",
    "studio-natural": "Controlled soft studio capture with natural skin, hair, fabric, posture, and tonal variation.",
    "environmental-editorial": "Authored environmental capture with credible location light and spatial depth.",
    "phone-candid": "Believable phone-camera capture with motivated framing, exposure limits, and social behavior.",
}


def load_record(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def value(record: dict, key: str, default: str = "TBD") -> str:
    prompt = record.get("prompt", {})
    brief = record.get("brief", {})
    return str(prompt.get(key) or brief.get(key) or record.get(key) or default)


def master_prompt(record: dict) -> str:
    mode = str(record.get("mode", "campaign"))
    operation = str(record.get("operation", "")).lower()
    is_person = mode in ("human", "virtual-person", "human-edit", "makeup-edit", "outfit-edit")
    is_edit = operation == "edit" or mode.endswith("-edit") or bool(record.get("edit_target"))
    identity_sensitive_edit = mode in ("human-edit", "makeup-edit", "outfit-edit") or bool(record.get("identity_sensitive_edit"))
    capture_mode = value(record, "capture_mode", "studio-natural" if is_person else "studio-clean")
    capture_direction = CAPTURE_MODES.get(capture_mode, capture_mode)
    lines = [
        "CAPTURE MODE",
        f"{capture_mode}: {capture_direction}",
        "",
    ]
    if is_person:
        lines.extend(
            [
                "CASTING",
                value(
                    record,
                    "casting",
                    "Fictional adult subject with brief-appropriate casting, plausible anatomy, natural skin structure, and no automatic ethnicity, body, or beauty-style default.",
                ),
                "",
            ]
        )
    if identity_sensitive_edit:
        lines.extend(
            [
                "IDENTITY-PRESERVING EDIT CONTRACT",
                "Change only the explicitly requested makeup, grooming, or wardrobe regions.",
                (
                    "Lock the exact facial identity: head shape, facial width and height, eye shape and spacing, eyelids, brows, "
                    "nose bridge, tip and nostrils, philtrum, lip geometry, jawline, chin, cheek structure, ears, skin tone, age "
                    "presentation, hairline, expression, gaze, natural asymmetry, identity marks, body proportions, pose, hands, "
                    "camera, crop, lighting, and background unless one of these is explicitly named in Change."
                ),
                (
                    "Makeup may change pigment, finish, liner, lashes, blush, highlight, and lip surface only. It must not enlarge "
                    "eyes, narrow the nose, sharpen the jaw, create a V-line, change facial proportions, replace skin, change "
                    "ethnicity, change age, or make the subject look like a different person."
                ),
                (
                    "For wardrobe edits, match garment fit, seams, fabric behavior, folds, shadows, occlusion, and contact while "
                    "preserving the person's face, hair, makeup unless requested, body shape, pose, and every non-wardrobe region."
                ),
                "Reject face drift, beautification drift, body reshaping, pose drift, extra accessories, skin replacement, or full-image restyling.",
                "",
            ]
        )
    elif is_edit:
        lines.extend(
            [
                "LOCALIZED EDIT CONTRACT",
                f"CHANGE: {value(record, 'change', 'Only the explicitly requested region, object, background, lighting, or styling.')}",
                f"LOCK: {value(record, 'lock', 'All source pixels, product geometry, labels, identity, pose, crop, and proportions outside Change.')}",
                f"MATCH: {value(record, 'match', 'Perspective, scale, grain, focus, occlusion, reflections, color spill, and contact shadows.')}",
                f"MASK: {value(record, 'mask', 'Use the smallest practical mask; feather only where the physical edge requires it.')}",
                f"REJECT: {value(record, 'reject', 'Full-image restyling, source drift, invented text, floating objects, or inconsistent light and shadow.')}",
                "",
            ]
        )
    if mode == "virtual-person":
        lines.extend(
            [
                "VIRTUAL PERSON DESIGN",
                (
                    f"Purpose: {value(record, 'virtual_person_purpose', 'Recurring fictional adult brand person')}. "
                    f"Face impression: {value(record, 'face_impression', 'cinematic-natural with original distinguishing details')}. "
                    f"Identity anchors: {value(record, 'identity_anchors', 'Lock face shape, eye spacing, nose, lips, jaw, hairline, and one original distinguishing detail')}. "
                    f"Adult body presentation: {value(record, 'body_build', 'healthy slender-light-frame build')}. "
                    f"Posture and gesture: {value(record, 'posture_signature', 'natural skeletal balance and a repeatable gesture signature')}. "
                    f"Allowed variation: {value(record, 'allowed_variation', 'makeup, hair, wardrobe, pose, camera, and grade may vary; biological identity may not')}."
                ),
                "",
                "CONSISTENCY INPUTS",
                value(record, "identity_references", "Use a neutral front, both three-quarter views, profile, full-body, and expression sheet before campaign styling."),
                "",
            ]
        )
    if is_person:
        lines.extend(
            [
                "MAKEUP AND GROOMING",
                (
                    f"Skin: {value(record, 'makeup_skin', 'Natural skin structure with brief-appropriate finish and coverage')}. "
                    f"Brows: {value(record, 'makeup_brows', 'Brief-appropriate natural brow geometry')}. "
                    f"Eyes: {value(record, 'makeup_eyes', 'Specify shadow placement, liner path, and lash definition from authorized references')}. "
                    f"Cheeks and structure: {value(record, 'makeup_cheeks', 'Specify blush placement and restrained contour/highlight')}. "
                    f"Lips: {value(record, 'makeup_lips', 'Specify hue, edge behavior, opacity, and finish')}. "
                    f"Palette and retouch: {value(record, 'makeup_finish', 'Protect skin tone and texture; editorial cleanup only unless approved otherwise')}."
                ),
                "",
            ]
        )
    lines.extend(
        [
            "JOB",
            value(record, "job", value(record, "objective")),
            "",
            "AUDIENCE AND MESSAGE",
            f"Audience: {value(record, 'audience')}. Single idea: {value(record, 'single_idea', value(record, 'promise'))}.",
            "",
            "REFERENCES AND LOCKS",
            f"References: {value(record, 'references', 'None supplied')}. Preserve exactly: {value(record, 'locks', 'No exact locks supplied')}.",
            "",
            "SUBJECT AND ACTION",
            value(record, "subject_action"),
            "",
            "SCENE AND ART DIRECTION",
            value(record, "scene"),
            "",
            "COMPOSITION AND CROP",
            f"{value(record, 'composition')}. Camera height and angle: {value(record, 'camera_geometry')}. Aspect ratio: {value(record, 'aspect_ratio')}. Copy-safe area: {value(record, 'copy_safe_area')}.",
            "",
            "CAMERA BEHAVIOR",
            f"Lens and distance: {value(record, 'lens_distance')}. Focus and aperture intent: {value(record, 'focus_depth')}. Motion and shutter intent: {value(record, 'motion_shutter')}. ISO/noise and white balance: {value(record, 'sensor_color')}.",
            "",
            "LIGHTING GEOMETRY",
            f"{value(record, 'lighting')}. Fill and separation: {value(record, 'fill_separation')}. Background distance/treatment: {value(record, 'background_treatment')}.",
            "",
            "REALISM AND MATERIALS",
            value(record, "materials"),
            "",
            "TEXT",
            value(record, "exact_text", "No generated text; add typography during layout."),
            "",
            "DO NOT",
            value(record, "negative_constraints", "No fake text, product drift, plastic skin, anatomy errors, impossible light or physics, watermark, or generic AI styling."),
        ]
    )
    return "\n".join(lines)


def compile_provider(record: dict, provider: str) -> str:
    master = master_prompt(record)
    if provider in ("generic", "openai", "gpt-image-2"):
        prefix = "PROVIDER: GPT IMAGE 2\nMODEL: gpt-image-2\n" if provider != "generic" else "PROVIDER: GENERIC\n"
        return prefix + master

    if provider in ("nano-banana-2-lite", "nano-banana-2", "nano-banana-pro"):
        models = {
            "nano-banana-2-lite": "gemini-3.1-flash-lite-image",
            "nano-banana-2": "gemini-3.1-flash-image",
            "nano-banana-pro": "gemini-3-pro-image",
        }
        return (
            f"PROVIDER: {provider.upper()}\nMODEL: {models[provider]}\n"
            + master
            + "\n\nEXECUTION: Send role-labeled image inputs with the canonical prompt. "
            "For exploration variants, start independent interactions; use previous_interaction_id only for the selected refinement branch."
        )

    flat = " ".join(line.strip() for line in master.splitlines() if line.strip())
    if provider == "midjourney":
        return (
            "PROVIDER: MIDJOURNEY\n"
            + flat
            + "\n\nCAVEAT: Add current aspect-ratio and style parameters only after checking live Midjourney syntax. Do not rely on generated packaging text."
        )
    if provider == "flux":
        return (
            "PROVIDER: FLUX\nPOSITIVE PROMPT\n"
            + flat
            + "\n\nNEGATIVE PROMPT\n"
            + value(record, "negative_constraints", "product drift, fake text, plastic skin, anatomy errors, impossible shadows")
            + "\n\nCAVEAT: Record the exact Flux model and host because controls vary."
        )
    if provider == "ideogram":
        return (
            "PROVIDER: IDEOGRAM\n"
            + master
            + "\n\nTEXT CHECK: Preserve quoted spelling, hierarchy, casing, and placement. Inspect every character before use."
        )
    if provider == "firefly":
        return (
            "PROVIDER: ADOBE FIREFLY\n"
            + master
            + "\n\nFINISHING: Separate composition and style references. Use masks for local edits and finish exact typography in Adobe design tools."
        )
    raise ValueError(f"Unsupported provider: {provider}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile a creative brief for an image provider.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--provider", choices=PROVIDERS, default="generic")
    parser.add_argument("--output")
    args = parser.parse_args()
    content = compile_provider(load_record(args.input), args.provider) + "\n"
    emit(content, args.output)


if __name__ == "__main__":
    main()
