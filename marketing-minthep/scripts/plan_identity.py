#!/usr/bin/env python3
"""Check a mark against every slot it has to survive, and derive the banner and type systems.

Everything here is arithmetic taken from references/identity-design.md. The point is that a logo
failure is almost always a failure at a size nobody rendered, and that size is computable before
anyone opens a drawing tool.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit_json  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"


def _table(name: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO((DATA / name).read_text(encoding="utf-8"))))


def _luminance(hex_colour: str) -> float:
    value = hex_colour.strip().lstrip("#")
    channels = [int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(one: str, two: str) -> float:
    first, second = _luminance(one), _luminance(two)
    high, low = max(first, second), min(first, second)
    return round((high + 0.05) / (low + 0.05), 2)


def check_slots(thinnest_stroke_pct: float, smallest_counter_pct: float | None,
                distinct_elements: int, content_radius_pct: float | None) -> list[dict]:
    """Walk the ladder and say, per slot, what breaks. thinnest_stroke_pct is the mark's own
    thinnest element as a percentage of mark height, which is the one number a designer can read
    off their own artboard."""
    verdicts = []
    for row in _table("mark-scale-ladder.csv"):
        slot_px = int(row["px"])
        stroke_floor = float(row["min_stroke_pct_of_mark_height"])
        counter_floor = float(row["min_counter_pct_of_mark_height"])
        fails = []
        if thinnest_stroke_pct < stroke_floor:
            fails.append(
                f"thinnest stroke is {thinnest_stroke_pct}% of mark height, under the "
                f"{stroke_floor}% floor at {slot_px}px. It renders grey or disappears"
            )
        if smallest_counter_pct is not None and smallest_counter_pct < counter_floor:
            fails.append(
                f"smallest counter is {smallest_counter_pct}%, under the {counter_floor}% floor. "
                "The hole closes under antialiasing and reads as a smudge"
            )
        if distinct_elements > int(row["max_distinct_elements"]):
            fails.append(
                f"{distinct_elements} distinct elements is over the {row['max_distinct_elements']} "
                f"this slot can hold in {row['total_pixels']} total pixels"
            )
        if row["safe_circle_px"] != "-" and content_radius_pct is not None \
                and content_radius_pct > 40.0:
            fails.append(
                f"content reaches {content_radius_pct}% of icon width from centre, outside the "
                f"40% safe radius. The platform mask crops it at {row['safe_circle_px']}px"
            )
        verdicts.append({
            "slot": row["slot"],
            "px": slot_px,
            "passes": not fails,
            "fails": fails,
            "safe_circle_px": row["safe_circle_px"],
            "what_fails_first_here": row["what_fails_first"],
        })
    return verdicts


def banner_families(sizes: list[str]) -> list[dict]:
    """One master per aspect ratio; sizes within a ratio are exports. Sizes are grouped when their
    ratios sit within 5% of each other, which is what puts 300x250 and 336x280 in one family."""
    parsed = []
    for size in sizes:
        width, height = (int(part) for part in str(size).lower().replace("*", "x").split("x"))
        parsed.append({"size": f"{width}x{height}", "w": width, "h": height,
                       "ratio": width / height, "area": width * height})
    families: list[dict] = []
    for item in sorted(parsed, key=lambda entry: -entry["ratio"]):
        for family in families:
            if abs(item["ratio"] - family["ratio"]) / family["ratio"] <= 0.05:
                family["members"].append(item)
                break
        else:
            families.append({"ratio": item["ratio"], "members": [item]})
    output = []
    for family in families:
        master = max(family["members"], key=lambda entry: entry["area"])
        output.append({
            "ratio": f"{family['ratio']:.2f}:1",
            "design_master": master["size"],
            "derive_as_exports": [entry["size"] for entry in family["members"]
                                  if entry["size"] != master["size"]],
            # 6:5 is 1.20 and is not a landscape layout in any useful sense, so the square-ish band
            # has to be wide enough to hold the whole medium-rectangle family.
            "orientation": "landscape" if family["ratio"] > 1.3
                           else "portrait" if family["ratio"] < 0.77 else "square-ish",
            "note": "Compose the readable core to about 40% of frame height and check the platform "
                    "safe band in data/composition-grids.csv"
                    if family["ratio"] < 0.6 else
                    "A strip this wide holds one accent and one line. Two accents leave nothing "
                    "emphasised" if family["ratio"] > 4 else
                    "Reserve the copy area before placing the image, per copy_reserve in "
                    "data/layout-dials.csv",
        })
    return output


def type_scale(body_px: float, headline_ratio: float, steps: int) -> dict:
    dial = next(row for row in _table("layout-dials.csv") if row["dial"] == "size_ratio")
    low, high = float(dial["min"]), float(dial["max"])
    clamped = min(max(headline_ratio, low), high)
    steps = max(steps, 2)
    step_ratio = clamped ** (1 / (steps - 1))
    ladder = [round(body_px * step_ratio ** index, 1) for index in range(steps)]
    return {
        "body_px": body_px,
        "headline_ratio_requested": headline_ratio,
        "headline_ratio_used": round(clamped, 2),
        "clamped": clamped != headline_ratio,
        # The dial's breaks_at sentence describes the bottom of the range, so it is the wrong
        # explanation for a ratio clamped at the top. Say which bound was hit and why.
        "clamp_reason": "-" if clamped == headline_ratio else dial["breaks_at"] if clamped == low else
                        f"Clamped to the {high} ceiling in data/layout-dials.csv. Above it the "
                        "headline stops being the top of a scale and becomes a second, unrelated "
                        f"typeface size: {dial['lower_it_when']}",
        "step_ratio": round(step_ratio, 3),
        "ladder_px": ladder,
        "rule": "Every size is body times the step ratio to a power. A size that is not on this "
                "ladder belongs to no system, and the next person will add another one.",
    }


def plan_identity(request: dict) -> dict:
    stroke = float(request.get("thinnest_stroke_pct_of_height", 0) or 0)
    counter = request.get("smallest_counter_pct_of_height")
    counter = float(counter) if counter not in (None, "", "-") else None
    elements = int(request.get("distinct_elements", 1) or 1)
    radius = request.get("content_radius_pct_of_width")
    radius = float(radius) if radius not in (None, "", "-") else None
    mark_colour = str(request.get("mark_colour", "#000000"))
    backgrounds = list(request.get("approved_backgrounds") or ["#ffffff"])
    is_link = bool(request.get("mark_is_a_link_or_control"))
    has_tagline = bool(request.get("tagline_set_as_text"))

    slots = check_slots(stroke, counter, elements, radius)
    required = str(request.get("smallest_required_slot") or "favicon-16")
    passing = [slot for slot in slots if slot["passes"]]
    derived_minimum = min((slot["px"] for slot in passing), default=None)

    required_slot = next((slot for slot in slots if slot["slot"] == required), None)
    if required_slot and not required_slot["passes"]:
        verdict = (
            f"The mark does not survive {required}, which the system requires. That makes the mark "
            "wrong for the system, not the system wrong for the mark: draw a simplified variant and "
            "approve it as its own asset with its own minimum."
        )
    elif derived_minimum is None:
        verdict = "The mark survives no slot on the ladder. Reduce elements or thicken the strokes."
    else:
        verdict = (
            f"Smallest surviving slot is {derived_minimum}px. Confirm it by the descending-render "
            "test at 100%, not by zooming into the master, and record which element failed below it."
        )

    ratios = []
    for background in backgrounds:
        measured = contrast(mark_colour, background)
        ratios.append({
            "background": background,
            "ratio": measured,
            "logotype_exemption_applies": True,
            "meets_3_to_1_by_choice": measured >= 3.0,
            "required_because_it_is_a_control": is_link,
            "verdict": "Passes SC 1.4.11 at 3:1" if measured >= 3.0 and is_link
                       else "Fails SC 1.4.11: the mark is a control, so 3:1 is required, not optional"
                       if is_link else "Exempt from SC 1.4.3, and holds 3:1 anyway"
                       if measured >= 3.0 else
                       "Exempt from SC 1.4.3, but under 3:1. Exempt is not legible",
        })

    return {
        "schema_version": 1,
        "slot_report": slots,
        "derived_minimum_size_px": derived_minimum,
        "smallest_required_slot": required,
        "verdict": verdict,
        "contrast": ratios,
        "tagline_rule": "A tagline set as text is not part of the logo. Hold it to 4.5:1, or 3:1 at "
                        "24px regular / 18.66px bold, which is 18pt and 14pt bold at 96dpi."
                        if has_tagline else "No tagline declared as text.",
        "clearspace": "State it as a multiple of an element inside the mark. Default: 1 x cap height "
                      "on all four sides. Pixels and millimetres are wrong at every size except the "
                      "one they were written for.",
        "banner_families": banner_families(request.get("banner_sizes") or []),
        "type_scale": type_scale(float(request.get("body_px", 16) or 16),
                                 float(request.get("headline_ratio", 2.6) or 2.6),
                                 int(request.get("type_steps", 5) or 5)),
        "delivery_gates": [
            "Rendered at every slot at 100%, not zoomed",
            "Important content inside the 40%-radius safe circle for masked and circular contexts",
            "No pre-rounded corners on the iOS asset; the OS applies its own mask",
            "Centroid aligned rather than bounding box wherever the mass is asymmetric",
            "One master per aspect ratio; exports derived, never upscaled",
            "Final type set in the layout, never rendered by an image model",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    emit_json(plan_identity(json.loads(Path(args.input).read_text(encoding="utf-8-sig"))), args.output)


if __name__ == "__main__":
    main()
