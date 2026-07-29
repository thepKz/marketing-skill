#!/usr/bin/env python3
"""Sequence a video shot list so that adjacent shots actually connect.

`references/video-production.md` already tells the author to "carry screen direction, gaze,
hand position, light direction, time of day, prop placement, and fluid/steam state through
adjacent shots". That is advice, and advice is not carried by anything. The way a shot list
was previously built was to write one brief per shot and run `compile_prompt.py` on each, so
every shot described its world from scratch. Two independently written descriptions of the
same bowl are never the same bowl, and the cut shows it: the steam resets, the light jumps
sides, the subject turns around mid-move. The prompts read fine one at a time and do not
join up.

This script removes the chance to forget. It takes one spec: a `world` that holds for the
whole film, and shots that declare only what *changes*. Everything else is inherited from the
previous shot, so continuity is the default and a break has to be written down to happen.

Three things follow from that, and they are the whole point:

1. The lock block is computed once and emitted byte-identical into every shot. A paraphrased
   lock is how product identity drifts, so no shot gets its own wording.
2. Each shot states what it CARRIED and what it CHANGES. A generative model given "the light
   stays 45 degrees camera-left, as in the previous shot" holds it; given a fresh sentence
   about lighting, it re-rolls.
3. Continuity errors are refused, not mentioned. A screen-direction flip with no cutaway is
   the 180-degree rule broken; it exits non-zero instead of printing a suggestion.

    python plan_video_sequence.py --input spec.json                    # per-shot prompts
    python plan_video_sequence.py --input spec.json --format report    # bilingual shot plan
    python plan_video_sequence.py --input spec.json --format csv       # shot table
    python plan_video_sequence.py --input spec.json --format json      # machine-readable
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit  # noqa: E402


# State a viewer notices the moment it breaks at a cut. Each key carries a short label for
# tables and prompt lines, a description for the reader who has not met the term, and the reject
# line that belongs to it. The reject text is derived from the lock rather than written per shot,
# so the two can never disagree — a shot cannot lock the light and then permit it to move.
CARRIED: tuple[tuple[str, str, str, str], ...] = (
    ("screen_direction", "screen direction", "direction of travel across frame", "the subject reversing travel direction across the cut"),
    ("gaze", "gaze", "where the subject looks", "the eyeline jumping to a new target"),
    ("hand", "hand", "which hand performs the action", "the action swapping to the other hand"),
    ("light_direction", "light direction", "key light position relative to camera", "the key light jumping to the opposite side"),
    ("time_of_day", "time of day", "sun position and colour temperature", "shadow length or colour temperature shifting"),
    ("prop_placement", "props", "where each prop sits in the set", "props appearing, vanishing, or relocating"),
    ("material_state", "material state", "steam, condensation, fill level, melt, wear", "steam resetting or looping, fill level rising, condensation appearing"),
    ("wardrobe", "wardrobe", "garments, layers, accessories", "a garment, layer, or accessory changing"),
)
CARRIED_KEYS = tuple(key for key, _, _, _ in CARRIED)
CARRIED_LABEL = {key: label for key, label, _, _ in CARRIED}
CARRIED_ABOUT = {key: about for key, _, about, _ in CARRIED}
CARRIED_REJECT = {key: reject for key, _, _, reject in CARRIED}

# Facts that hold for the whole film, in the order they are emitted. Order is fixed so the lock
# block is stable across runs and a diff between two versions of a spec is readable.
WORLD_FIELDS: tuple[tuple[str, str], ...] = (
    ("product", "Product"),
    ("person", "Person"),
    ("location", "Location"),
    ("palette", "Palette and grade"),
    ("lens_family", "Lens family"),
)

# Reversing one of these across a cut disorients the viewer: it reads as the subject having
# turned around rather than the camera having moved. Film grammar calls it the 180-degree rule.
# Crossing the line is legitimate, but it needs a cutaway to hide the reversal, so the spec has
# to say `"cutaway": true` and take responsibility for it.
OPPOSED_DIRECTIONS = (
    frozenset({"left-to-right", "right-to-left"}),
    frozenset({"toward camera", "away from camera"}),
)

# Generative video drifts as a function of shot length: the longer a single generation runs, the
# further the subject travels from its first frame. The reference already says to prefer short
# controlled shots and cut around drift. This is that instruction as a number.
GENERATIVE_MAX_SHOT_S = 5.0

# A duration list that does not add up to the placement length is a shot list that cannot be
# cut. Half a second of tolerance absorbs rounding in hand-written specs.
DURATION_TOLERANCE_S = 0.5


def _text(value: object, default: str = "TBD") -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def resolve(spec: dict) -> dict:
    """Thread carried state through the shots and collect every continuity break found.

    Returns the resolved sequence rather than raising, so a caller can report all problems at
    once. A spec with four breaks should not take four runs to fix.
    """
    world = dict(spec.get("world") or {})
    shots_in = list(spec.get("shots") or [])
    problems: list[str] = []
    notes: list[str] = []

    if not shots_in:
        problems.append("spec has no shots")

    generative = "generative" in str(spec.get("production_mode", "generative")).lower()
    max_shot = float(spec.get("max_shot_s") or (GENERATIVE_MAX_SHOT_S if generative else 0) or 0)

    # Opening state comes from the world where the world supplies it. A key nobody ever sets
    # stays unset and is reported once, at the end, rather than silently becoming "TBD" in
    # thirty prompt lines.
    state = {key: _text(world.get(key), "") for key in CARRIED_KEYS}

    resolved: list[dict] = []
    seen_ids: set[str] = set()
    clock = 0.0

    for index, raw in enumerate(shots_in, start=1):
        shot_id = _text(raw.get("id"), f"S{index}")
        if shot_id in seen_ids:
            problems.append(f"duplicate shot id {shot_id!r}")
        seen_ids.add(shot_id)

        changes = dict(raw.get("set") or {})
        # A misspelled continuity key is the worst failure mode available here, because the
        # value looks written down in the spec and silently reaches no prompt at all.
        for key in changes:
            if key not in CARRIED_KEYS:
                problems.append(
                    f"{shot_id}: unknown continuity key {key!r}; expected one of {', '.join(CARRIED_KEYS)}"
                )

        established: list[tuple[str, str]] = []
        changed: list[tuple[str, str, str]] = []
        carried: list[tuple[str, str]] = []

        for key in CARRIED_KEYS:
            incoming = state[key]
            declared = _text(changes.get(key), "") if key in changes else ""
            if declared and declared != incoming:
                if incoming:
                    changed.append((key, incoming, declared))
                else:
                    established.append((key, declared))
                state[key] = declared
            elif incoming:
                carried.append((key, incoming))

        cutaway = bool(raw.get("cutaway"))
        for key, before, after in changed:
            if key == "screen_direction" and not cutaway:
                pair = frozenset({before.lower(), after.lower()})
                if pair in OPPOSED_DIRECTIONS:
                    problems.append(
                        f"{shot_id}: screen direction reverses {before!r} -> {after!r} on a straight cut. "
                        "Either keep the direction or insert a cutaway and set \"cutaway\": true."
                    )
            if key == "time_of_day" and not cutaway and not _text(raw.get("reason"), ""):
                problems.append(
                    f"{shot_id}: time of day jumps {before!r} -> {after!r} with no cutaway and no stated "
                    "reason. A daylight jump inside a continuous scene reads as an error."
                )

        duration = float(raw.get("duration_s") or 0)
        if duration <= 0:
            problems.append(f"{shot_id}: duration_s must be a positive number")
        elif max_shot and duration > max_shot:
            problems.append(
                f"{shot_id}: {duration:g}s exceeds the {max_shot:g}s generative ceiling. Split it and cut, "
                "or set production_mode to live-action where a long take is actually shootable."
            )
        for field in ("job", "action"):
            if not _text(raw.get(field), ""):
                problems.append(f"{shot_id}: missing {field}")

        # On-screen numbers are the one thing in a shot list that can be legally wrong. Flagged,
        # not blocked: the script cannot know whether a price is real, only that someone must check.
        on_screen = _text(raw.get("text"), "")
        if any(character.isdigit() for character in on_screen):
            notes.append(f"{shot_id}: on-screen text {on_screen!r} contains a number — verify before publishing")

        start, clock = clock, clock + max(duration, 0.0)
        resolved.append(
            {
                "id": shot_id,
                "job": _text(raw.get("job")),
                "duration_s": duration,
                "start_s": round(start, 2),
                "end_s": round(clock, 2),
                "action": _text(raw.get("action")),
                "framing": _text(raw.get("framing"), "framing not specified"),
                "camera": _text(raw.get("camera"), "locked camera"),
                "transition": _text(raw.get("transition"), "hard cut"),
                "reason": _text(raw.get("reason"), ""),
                "cutaway": cutaway,
                "text": on_screen,
                "audio": _text(raw.get("audio"), ""),
                "established": established,
                "changed": changed,
                "carried": carried,
            }
        )

    target = float(spec.get("duration_s") or 0)
    if target and abs(clock - target) > DURATION_TOLERANCE_S:
        problems.append(
            f"shot durations total {clock:g}s against a {target:g}s target; the cut will not fit the placement"
        )

    never_set = [key for key in CARRIED_KEYS if not state[key]]
    if never_set:
        notes.append(
            "never specified anywhere, so no shot can lock it: "
            + ", ".join(f"{key} ({CARRIED_ABOUT[key]})" for key in never_set)
        )

    return {
        "title": _text(spec.get("title"), "Untitled sequence"),
        "aspect_ratio": _text(spec.get("aspect_ratio"), "9:16"),
        "production_mode": _text(spec.get("production_mode"), "generative"),
        "total_s": round(clock, 2),
        "target_s": target,
        "world": world,
        "shots": resolved,
        "problems": problems,
        "notes": notes,
    }


def lock_block(sequence: dict) -> str:
    """The one paragraph every shot shares, character for character."""
    world = sequence["world"]
    lines = ["CONTINUITY LOCK — identical in every shot, do not paraphrase or re-describe"]
    for key, label in WORLD_FIELDS:
        value = _text(world.get(key), "")
        if value:
            lines.append(f"  {label}: {value}")
    lines.append(f"  Aspect ratio: {sequence['aspect_ratio']}")
    lines.append(
        "  Constant across every shot: product silhouette, label plane, cap and closure, material, "
        "colour, person identity, handedness, and environment anchors."
    )
    return "\n".join(lines)


def shot_prompt(sequence: dict, index: int) -> str:
    """One provider-ready shot prompt: the shared lock, then inherited state, then the delta."""
    shot = sequence["shots"][index]
    previous = sequence["shots"][index - 1] if index else None
    lines = [
        f"SHOT {shot['id']} — {shot['start_s']:g}-{shot['end_s']:g}s ({shot['duration_s']:g}s) — {shot['job']}",
        "",
        lock_block(sequence),
        "",
        "ACTION",
        f"  {shot['action']}",
        "",
        "CAMERA",
        f"  Framing: {shot['framing']}. Movement: {shot['camera']}.",
    ]

    if shot["established"]:
        lines += ["", "ESTABLISHED HERE — every later shot inherits these exact values"]
        lines += [f"  {CARRIED_LABEL[key]}: {value}" for key, value in shot["established"]]

    if shot["carried"]:
        header = (
            f"CARRIED FROM {previous['id']} — must match frame-for-frame at the cut"
            if previous
            else "CARRIED — hold for the whole shot"
        )
        lines += ["", header]
        lines += [f"  {CARRIED_LABEL[key]}: {value}" for key, value in shot["carried"]]

    if shot["changed"]:
        lines += ["", "CHANGES THIS SHOT — intentional; nothing outside this list may move"]
        lines += [f"  {CARRIED_LABEL[key]}: {before} -> {after}" for key, before, after in shot["changed"]]

    if previous:
        # The handoff, stated as a frame identity rather than a hope. Providers that accept a
        # first/last frame can use it directly; providers that do not still get the constraint
        # in words, which is the difference between a match cut and two unrelated clips.
        #
        # It points at the carried block instead of restating it. An earlier version repeated
        # every value here, which doubled the length of the prompt and gave the model two
        # separately-worded copies of the same constraint to disagree with.
        anchor = f"every value under CARRIED FROM {previous['id']}" if shot["carried"] else "the continuity lock above"
        lines += [
            "",
            f"CUT FROM {previous['id']} — {shot['transition']}",
            f"  The first frame of this shot continues the last frame of {previous['id']}: {anchor} "
            "holds unchanged across the cut.",
        ]
        if shot["reason"]:
            lines.append(f"  Reason for the cut: {shot['reason']}")
        if shot["cutaway"]:
            lines.append("  This is a cutaway, so a deliberate reorientation is permitted at this cut only.")

    if shot["text"]:
        lines += ["", "ON-SCREEN TEXT", f"  {shot['text']}"]
        lines.append("  Set this in the edit unless the provider is verified for exact text.")
    if shot["audio"]:
        lines += ["", "AUDIO", f"  {shot['audio']}"]

    # Rejects are generated from the locks above, so the list is exactly as long as the set of
    # things this shot promised to hold.
    rejects = [CARRIED_REJECT[key] for key, _ in shot["carried"]]
    rejects += [
        "product drift or label distortion",
        "morphing, duplicated, or looping detail",
        "invented on-screen text",
        "impossible light, shadow, contact, or fluid behaviour",
    ]
    lines += ["", "REJECT"]
    lines += [f"  - {reject}" for reject in rejects]
    return "\n".join(lines)


def format_prompts(sequence: dict) -> str:
    blocks = [shot_prompt(sequence, index) for index in range(len(sequence["shots"]))]
    return ("\n\n" + "=" * 78 + "\n\n").join(blocks) + "\n"


def format_report(sequence: dict) -> str:
    """Bilingual plan for a human reader. Headings ship en/vi like every other deliverable."""
    lines = [
        f"# {sequence['title']}",
        "",
        f"{sequence['total_s']:g}s · {sequence['aspect_ratio']} · {sequence['production_mode']} · "
        f"{len(sequence['shots'])} shots",
        "",
        "## Continuity lock / Khoá liên tục",
        "",
        "```text",
        lock_block(sequence),
        "```",
        "",
        "## Shot list / Danh sách cảnh",
        "",
        "| # | Time | Job | Action | Camera | Carried / Kế thừa | Set here / Đặt ở đây |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for shot in sequence["shots"]:
        carried = ", ".join(CARRIED_LABEL[key] for key, _ in shot["carried"]) or "—"
        # The opening shot changes nothing and carries nothing: it *establishes*. Reporting that
        # as two empty cells made the shot that sets the whole film's state look like the one
        # shot with no continuity in it.
        set_here = [CARRIED_LABEL[key] for key, _ in shot["established"]]
        set_here += [CARRIED_LABEL[key] for key, _, _ in shot["changed"]]
        lines.append(
            f"| {shot['id']} | {shot['start_s']:g}-{shot['end_s']:g}s | {shot['job']} | {shot['action']} "
            f"| {shot['camera']} | {carried} | {', '.join(set_here) or '—'} |"
        )

    lines += ["", "## Cut handoffs / Điểm nối", ""]
    for index in range(1, len(sequence["shots"])):
        shot, previous = sequence["shots"][index], sequence["shots"][index - 1]
        lines.append(f"**{previous['id']} → {shot['id']}** · {shot['transition']}")
        lines.append("")
        # One line per held value, not one paragraph of them. This list is meant to be read at
        # the edit while looking at two frames, which a comma-joined sentence defeats.
        lines += [f"- {CARRIED_LABEL[key]}: {value}" for key, value in shot["carried"]] or ["- the locked world above"]
        if shot["reason"]:
            lines.append(f"- *why this cut:* {shot['reason']}")
        lines.append("")

    if sequence["notes"]:
        lines += ["", "## Check before publishing / Kiểm tra trước khi phát hành", ""]
        lines += [f"- {note}" for note in sequence["notes"]]
    return "\n".join(lines) + "\n"


def format_csv(sequence: dict) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["shot", "start_s", "end_s", "duration_s", "job", "action", "framing", "camera", "transition", "text", "audio", "carried", "changes"])
    for shot in sequence["shots"]:
        writer.writerow(
            [
                shot["id"], shot["start_s"], shot["end_s"], shot["duration_s"], shot["job"],
                shot["action"], shot["framing"], shot["camera"], shot["transition"], shot["text"], shot["audio"],
                "; ".join(f"{key}={value}" for key, value in shot["carried"]),
                "; ".join(f"{key}: {before} -> {after}" for key, before, after in shot["changed"]),
            ]
        )
    return buffer.getvalue()


FORMATS = {"prompts": format_prompts, "report": format_report, "csv": format_csv}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sequence video shots with carried continuity.")
    parser.add_argument("--input", required=True, help="JSON sequence spec")
    parser.add_argument("--format", choices=(*FORMATS, "json"), default="prompts")
    parser.add_argument("--output")
    arguments = parser.parse_args()

    sequence = resolve(json.loads(Path(arguments.input).read_text(encoding="utf-8")))

    if sequence["problems"]:
        # Refuse rather than warn. A shot list that breaks continuity is the bug this script
        # exists to prevent, and emitting it with a warning above it is how it ships anyway.
        for stream_line in ["Continuity errors — nothing was emitted:", *(f"  - {p}" for p in sequence["problems"])]:
            print(stream_line, file=sys.stderr)
        return 1

    if arguments.format == "json":
        content = json.dumps(sequence, ensure_ascii=False, indent=2) + "\n"
    else:
        content = FORMATS[arguments.format](sequence)
    emit(content, arguments.output)

    for note in sequence["notes"]:
        print(f"note: {note}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
