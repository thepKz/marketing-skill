#!/usr/bin/env python3
"""Compile a provider-neutral creative brief into provider-ready prompt text."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


RAW_HUMAN_OPENING = (
    "Create a completely RAW quality, unprocessed, unedited image with full iPhone camera quality."
)
PROVIDERS = ("generic", "openai", "midjourney", "flux", "ideogram", "firefly")


def load_record(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def value(record: dict, key: str, default: str = "TBD") -> str:
    prompt = record.get("prompt", {})
    brief = record.get("brief", {})
    return str(prompt.get(key) or brief.get(key) or record.get(key) or default)


def master_prompt(record: dict) -> str:
    mode = str(record.get("mode", "campaign"))
    lines = []
    if mode == "human":
        lines.extend(
            [
                RAW_HUMAN_OPENING,
                "Adult subject, Korean K-pop-inspired makeup, slender healthy idol-like silhouette, plausible anatomy, natural skin texture, and no beauty-filter smoothing unless another direction is supplied.",
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
            "COMPOSITION",
            f"{value(record, 'composition')}. Aspect ratio: {value(record, 'aspect_ratio')}. Copy-safe area: {value(record, 'copy_safe_area')}.",
            "",
            "CAMERA AND LIGHT",
            value(record, "camera_light"),
            "",
            "REALISM AND MATERIALS",
            value(record, "materials"),
            "",
            "TEXT",
            value(record, "exact_text", "No generated text; add typography during layout."),
            "",
            "DO NOT",
            value(record, "negative_constraints", "No fake text, product drift, anatomy errors, impossible physics, watermark, or generic AI styling."),
        ]
    )
    return "\n".join(lines)


def compile_provider(record: dict, provider: str) -> str:
    master = master_prompt(record)
    if provider in ("generic", "openai"):
        prefix = "PROVIDER: OPENAI IMAGES\n" if provider == "openai" else "PROVIDER: GENERIC\n"
        return prefix + master

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
            + value(record, "negative_constraints", "product drift, fake text, anatomy errors, impossible shadows")
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
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
