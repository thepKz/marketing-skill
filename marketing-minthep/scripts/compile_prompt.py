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

# The same capture mode means different things pointed at a bottle and pointed at a face. This
# used to be one sentence per mode, written in person vocabulary, and emitted for product shots
# too: a serum-bottle prompt carried "natural skin, hair, fabric, posture" into the renderer. A
# test render came back with silk drapery filling the copy area the brief had asked to keep
# empty, because the prompt asked for fabric on a page where no fabric existed.
CAPTURE_MODES = {
    "studio-clean": {
        "product": "Controlled commercial studio capture with exact materials, true colour, and restrained retouching.",
        "person": "Controlled commercial studio capture with exact wardrobe materials and restrained retouching.",
    },
    "studio-natural": {
        "product": "Controlled soft studio capture with honest material texture and tonal variation.",
        "person": "Controlled soft studio capture with natural skin, hair, fabric, posture, and tonal variation.",
    },
    "environmental-editorial": {
        "product": "Authored environmental capture with credible location light and spatial depth.",
        "person": "Authored environmental capture with credible location light, spatial depth, and unposed body language.",
    },
    "phone-candid": {
        "product": "Believable phone-camera capture with motivated framing and exposure limits.",
        "person": "Believable phone-camera capture with motivated framing, exposure limits, and social behavior.",
    },
}

# Provider size hints for the ratios a marketing deliverable actually uses. The ratio written in
# the prompt text is not what shapes the pixels — the API's size parameter is — so the compiled
# prompt has to tell the operator what to set. A prompt that says 4:5 and a call that renders
# 1:1 produces a crop where the copy area was.
RENDER_SIZES = {
    "1:1": "1024x1024",
    "4:5": "1024x1280",
    "5:4": "1280x1024",
    "2:3": "1024x1536",
    "3:2": "1536x1024",
    "3:4": "1024x1365",
    "4:3": "1365x1024",
    "9:16": "1080x1920",
    "16:9": "1920x1080",
}

# Appended to whatever the brief forbids, because a brief author cannot be expected to name every
# trope in advance. Each entry is a failure mode observed in test renders or a physical
# impossibility, not a style opinion: this list is about credibility, not taste.
HOUSE_NEGATIVES = (
    "no generic silk or satin drapery used as filler; "
    "no unmotivated petals, splashes, smoke, or floating props; "
    "no marble slab, pastel pedestal, or bokeh light spots added for mood; "
    "no lens flare or glow that no light source in the scene could cast; "
    "no shadow that disagrees with the stated light direction; "
    "no object resting on nothing; "
    "no plastic skin, waxy food, duplicated fingers, or extra limbs; "
    "no invented logo, label copy, price, or signage text; "
    "no watermark or signature."
)


def load_record(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def value(record: dict, key: str, default: str = "TBD") -> str:
    prompt = record.get("prompt", {})
    brief = record.get("brief", {})
    return str(prompt.get(key) or brief.get(key) or record.get(key) or default)


def frame_block(record: dict) -> list[str]:
    """Frame, composition, and the reserved copy area stated as something to do.

    The copy-safe area used to be emitted as a fact — "Copy-safe area: Upper-left 40 percent" —
    which tells a renderer nothing it can act on. A test render put the bottle dead centre and
    filled the upper-left with drapery, so the deliverable had nowhere to set a headline: the
    brief's most commercially important requirement was the one silently dropped. It is now an
    instruction with a stated consequence, and the composition is named before the scene so it
    is not competing with a nearer sentence about mood.
    """
    ratio = value(record, "aspect_ratio")
    size = RENDER_SIZES.get(ratio)
    lines = ["FRAME AND NEGATIVE SPACE", f"Aspect ratio: {ratio}."]
    if size:
        lines.append(
            f"Set the provider's output size to {size} or the nearest supported size at this ratio. "
            "Do not rely on the ratio being read from this text."
        )
    lines.append(
        f"Composition: {value(record, 'composition')}. Camera height and angle: {value(record, 'camera_geometry')}."
    )
    copy_area = value(record, "copy_safe_area", "")
    if copy_area:
        lines.append(
            f"Keep this area of the frame deliberately empty: {copy_area}. No subject, no prop, no drapery, "
            "no pattern, and no high-contrast detail there. Type will be set into it during layout, so it "
            "must read as quiet, even-toned space, not as background that happens to be less busy. "
            # Briefs contradict themselves: the scene names a prop on one side and the copy area
            # reserves that same side. Left unresolved, the renderer picks, and the deliverable
            # loses the one thing a layout cannot work around. Precedence is stated rather than
            # assumed, so a self-contradicting brief still produces a usable frame.
            "If any other line in this prompt would place an object there, this empty area wins and "
            "that object moves or leaves the frame."
        )
    else:
        lines.append(
            "No copy area is reserved, so the layout will place type outside the image or crop it. "
            "Compose as a full-bleed picture rather than leaving arbitrary empty space."
        )
    lines.append("")
    return lines


def master_prompt(record: dict) -> str:
    mode = str(record.get("mode", "campaign"))
    operation = str(record.get("operation", "")).lower()
    is_person = mode in ("human", "virtual-person", "human-edit", "makeup-edit", "outfit-edit")
    is_edit = operation == "edit" or mode.endswith("-edit") or bool(record.get("edit_target"))
    identity_sensitive_edit = mode in ("human-edit", "makeup-edit", "outfit-edit") or bool(record.get("identity_sensitive_edit"))
    capture_mode = value(record, "capture_mode", "studio-natural" if is_person else "studio-clean")
    described = CAPTURE_MODES.get(capture_mode)
    capture_direction = described[("person" if is_person else "product")] if described else capture_mode

    # The subject leads. This block used to open with the provider name and the capture mode, so
    # the highest-attention position in the prompt was spent on metadata and the thing being
    # photographed arrived seventh.
    lines = [
        "SUBJECT AND ACTION",
        value(record, "subject_action"),
        "",
    ]
    lines.extend(frame_block(record))
    lines.extend(
        [
            "SCENE AND ART DIRECTION",
            value(record, "scene"),
            "",
            "CAPTURE MODE",
            f"{capture_mode}: {capture_direction}",
            "",
        ]
    )
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
            "CAMERA BEHAVIOR",
            f"Lens and distance: {value(record, 'lens_distance')}. Focus and aperture intent: {value(record, 'focus_depth')}. Motion and shutter intent: {value(record, 'motion_shutter')}. ISO/noise and white balance: {value(record, 'sensor_color')}.",
            "",
            "LIGHTING GEOMETRY",
            f"{value(record, 'lighting')}. Fill and separation: {value(record, 'fill_separation')}. Background distance/treatment: {value(record, 'background_treatment')}.",
            "",
            "REALISM AND MATERIALS",
            value(record, "materials"),
            "",
            "REFERENCES AND LOCKS",
            f"References: {value(record, 'references', 'None supplied')}. Preserve exactly: {value(record, 'locks', 'No exact locks supplied')}.",
            "",
            "TEXT",
            value(record, "exact_text", "No generated text; add typography during layout."),
            "",
            # Job and audience are context for the person reading the prompt, not instructions a
            # renderer can execute. They sit after the visual contract so they do not compete
            # with it for attention.
            "JOB",
            value(record, "job", value(record, "objective")),
            "",
            "AUDIENCE AND MESSAGE",
            f"Audience: {value(record, 'audience')}. Single idea: {value(record, 'single_idea', value(record, 'promise'))}.",
            "",
            "DO NOT",
            value(record, "negative_constraints", "No product drift or anatomy errors."),
            HOUSE_NEGATIVES,
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
