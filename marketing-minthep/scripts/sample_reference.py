#!/usr/bin/env python3
"""Measure the palette a reference photograph already has, then judge a brand palette against it.

`plan_palette.py` answers "do these colours work together". It cannot answer the question that
actually decides whether a menu, a post or a pack looks art-directed or looks like a template with
content poured into it: **does the brand colour belong to the photograph it sits next to.**

The failure this script exists to catch is specific and it is the commonest one in the trade. A
designer opens a palette list, picks an accent, and drops the product photo in afterwards. The
accent is then a colour *named* after something in the scene rather than *measured* from it, and
the two read as two unrelated systems on one page. The tell is not the hue. It is chroma and area:
the brand version of the colour is two or three times more saturated than the same colour is in the
photograph, and it covers several times more of the frame. The eye then lands on the navigation
furniture instead of on the food.

The measured case that motivated this script is in the repository. `menu-brand-led-v1.png` uses a
cobalt rail justified as the blue of Hue ceramics. The ceramics are real and the blue is genuinely
in the source photographs, so the hue is honest. The numbers are not:

    blue arc 240-270 deg      share of frame    mean chroma    p98 chroma    max chroma
    banh-rang-bua.png              4.44%            0.088         0.148        0.164
    tra-dao.png                    1.35%            0.083         0.116        0.132
    menu-brand-led-v1.png          9.48%            0.130         0.133        0.216

Reproduce that table with `--image PATH` at the default stride of 4. The rail runs the same hue at
roughly 1.5x the average saturation it has in the glaze, over two to seven times the area, and its
peak of 0.216 out-saturates every single pixel of food in the three source photographs, whose whole
frame maxima are 0.164, 0.167 and 0.195. That is the arithmetic of "khong hai hoa". It is not a
matter of taste and it did not need an opinion to find.

So this script reports two things:

1. What the reference actually contains - chroma percentiles, the neutral mass, and the hue arcs
   present with the share of frame, chroma and lightness of each. This is the number a prompt or a
   palette should be built from, and it is also what you hand a generator when you tell it which
   colours the scene already has.
2. Whether each proposed brand colour survives three gates against that measurement. All three are
   house rules. `data/colour-gates.csv` records that, and the report prints the grade beside the
   verdict, so nobody quotes a house number as a requirement.

What this script cannot tell you: whether the photograph is any good, whether its colour is the
colour the product has in daylight, whether the reference is licensed for use, or whether a hue
absent from this one frame is absent from the brand - a prop, a room, a package or a tradition can
carry a colour that no single photograph shows. Gate 3 therefore returns `review`, never `failed`.

Everything is stdlib. PNG is decoded here rather than through a third-party imaging library, which
is why the input must be PNG: see `decode_png` for the exact formats accepted and refused. No key,
no network, no image provider - the same rule as the rest of the skill.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit_json, use_utf8_stdout  # noqa: E402
from plan_palette import parse_hex, rgb_to_oklab, to_hex  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[1]

# Below this chroma a pixel is treated as neutral and excluded from every hue arc. Cream paper,
# white plate, brown-black ink and grey shadow all sit under it, and they carry no hue argument.
# The number is ours. It is the same 0.04 that separates "a tint of" from "a colour" in the ramp
# work in plan_palette.py, and moving it moves the arc shares, so the report prints it.
NEUTRAL_CHROMA = 0.04

# Hue arcs are 30 degrees wide: twelve buckets, the granularity at which a person names a colour
# ("that blue", "that ochre") rather than distinguishes two of them. Narrower buckets split one
# glaze across two arcs and make the share numbers meaningless.
ARC_WIDTH = 30

# Gate 1 band. The rule - the subject keeps the chromatic peak - is defensible on its own terms: in
# an image whose job is to sell food, brand furniture more saturated than any pixel of the food
# moves the eye off the food. The edge is the problem, because the reference peak is a maximum, and
# a maximum is the least stable statistic there is: it moves with the sampling stride. So the edge
# was not invented, it was measured. Across the three food references in this repository at strides
# 1, 2, 4, 6, 8 and 12, the maximum chroma moved by 1.098x, 1.018x and 1.068x, while the 98th
# percentile moved by 1.009x, 1.001x and 1.009x. Re-run this calibration before changing the gate.
#
# An accent therefore fails only when it clears the peak by more than the stride alone can move it,
# and a smaller margin is returned for review rather than judged. Three photographs is a small
# sample and 1.10 is a house number read off it; it is not a perceptual boundary and nothing about
# it is standard.
PEAK_MARGIN_FAIL = 1.10

# Gate 2 band. An accent may intensify a colour the scene has - print ink is not glaze under
# kitchen light, and a rail at the glaze's exact chroma reads muddy. It may not replace it. Two
# numbers rather than one, for the reason given at length in plan_palette.py: a single hard edge on
# an invented threshold produces verdicts it cannot support. Between the two the answer is "a human
# decides", and the report says so.
CHROMA_INFLATION_REVIEW = 1.5
CHROMA_INFLATION_FAIL = 2.0

# Gate 3. An arc holding less than this share of the frame is noise - compression ringing, one
# specular fringe, a chromatic-aberration edge - and is not evidence that the scene contains the
# colour.
MIN_ANCHOR_SHARE = 0.005


# ------------------------------------------------------------------------------- PNG decoding


def _unfilter(raw: bytes, width: int, height: int, bpp: int) -> list[bytearray]:
    """Reverse the five PNG scanline filters. RFC 2083 section 6."""
    stride = width * bpp
    rows: list[bytearray] = []
    previous = bytearray(stride)
    position = 0
    for index in range(height):
        if position >= len(raw):
            raise ValueError(f"PNG data ends at scanline {index} of {height}; the file is truncated")
        filter_type = raw[position]
        position += 1
        line = bytearray(raw[position : position + stride])
        if len(line) != stride:
            raise ValueError(f"PNG scanline {index} is {len(line)} bytes, expected {stride}")
        position += stride
        if filter_type == 0:
            pass
        elif filter_type == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif filter_type == 2:
            for i in range(stride):
                line[i] = (line[i] + previous[i]) & 0xFF
        elif filter_type == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + previous[i]) >> 1)) & 0xFF
        elif filter_type == 4:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                up = previous[i]
                corner = previous[i - bpp] if i >= bpp else 0
                estimate = left + up - corner
                da, db, dc = abs(estimate - left), abs(estimate - up), abs(estimate - corner)
                if da <= db and da <= dc:
                    predictor = left
                elif db <= dc:
                    predictor = up
                else:
                    predictor = corner
                line[i] = (line[i] + predictor) & 0xFF
        else:
            raise ValueError(f"PNG scanline {index} uses filter {filter_type}, which is not 0-4")
        rows.append(line)
        previous = line
    return rows


def decode_png(path: str | Path) -> tuple[int, int, list[bytearray], int]:
    """Return (width, height, unfiltered scanlines, bytes per pixel) for a PNG this tool accepts.

    Accepted: bit depth 8, non-interlaced, colour type 0 (grey), 2 (truecolour), 3 (palette),
    4 (grey+alpha) or 6 (truecolour+alpha). Palette entries are expanded to RGB.

    Refused, with the reason named rather than a traceback: JPEG and every other container, because
    decoding one in the standard library means writing a DCT and this skill does not take an imaging
    dependency; 16-bit depth and Adam7 interlacing, because no reference in this repository uses
    them and an untested decoder path is worse than a refusal. Convert first - the measurement is
    unaffected by a lossless re-encode.
    """
    blob = Path(path).read_bytes()
    if blob[:8] != b"\x89PNG\r\n\x1a\n":
        if blob[:2] == b"\xff\xd8":
            raise ValueError(
                f"{path} is a JPEG. This tool decodes PNG only, so that the skill needs no imaging "
                "library. Re-save as PNG and measure that."
            )
        raise ValueError(f"{path} is not a PNG (signature {blob[:8]!r})")

    width = height = depth = colour_type = interlace = -1
    idat = bytearray()
    palette: bytes = b""
    position = 8
    while position < len(blob):
        (length,) = struct.unpack(">I", blob[position : position + 4])
        kind = blob[position + 4 : position + 8]
        body = blob[position + 8 : position + 8 + length]
        position += 12 + length
        if kind == b"IHDR":
            width, height, depth, colour_type, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif kind == b"PLTE":
            palette = bytes(body)
        elif kind == b"IDAT":
            idat += body
        elif kind == b"IEND":
            break

    if width <= 0:
        raise ValueError(f"{path} has no IHDR chunk")
    if depth != 8:
        raise ValueError(f"{path} is {depth}-bit. This tool reads 8-bit PNG; convert and measure that.")
    if interlace != 0:
        raise ValueError(f"{path} is Adam7 interlaced. Save it non-interlaced and measure that.")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(colour_type)
    if channels is None:
        raise ValueError(f"{path} uses PNG colour type {colour_type}, which is not 0, 2, 3, 4 or 6")
    if colour_type == 3 and not palette:
        raise ValueError(f"{path} is a palette PNG with no PLTE chunk")

    rows = _unfilter(zlib.decompress(bytes(idat)), width, height, channels)
    if colour_type == 3:
        expanded = []
        for row in rows:
            out = bytearray(width * 3)
            for x in range(width):
                base = row[x] * 3
                out[x * 3 : x * 3 + 3] = palette[base : base + 3]
            expanded.append(out)
        return width, height, expanded, 3
    return width, height, rows, channels


def sample_pixels(path: str | Path, step: int = 4) -> tuple[tuple[int, int], list[tuple[int, int, int]]]:
    """Read every `step`-th pixel on both axes. Every scanline is still unfiltered, because PNG
    filters are sequential and a row cannot be skipped, but only the sampled pixels are kept."""
    if step < 1:
        raise ValueError(f"--step is {step}; it must be 1 or more")
    width, height, rows, bpp = decode_png(path)
    grey = bpp in (1, 2)
    pixels = []
    for y in range(0, height, step):
        row = rows[y]
        for x in range(0, width, step):
            base = x * bpp
            if grey:
                value = row[base]
                pixels.append((value, value, value))
            else:
                pixels.append((row[base], row[base + 1], row[base + 2]))
    return (width, height), pixels


# ------------------------------------------------------------------------------- measurement


def _oklch(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    L, a, b = rgb_to_oklab((rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360.0


def _percentile(sorted_values: list[float], quantile: float) -> float:
    if not sorted_values:
        return 0.0
    index = min(len(sorted_values) - 1, int(quantile * len(sorted_values)))
    return sorted_values[index]


def measure(path: str | Path, step: int = 4) -> dict:
    """Report the palette a photograph already has, in the space the rest of the skill judges in."""
    (width, height), pixels = sample_pixels(path, step)
    if not pixels:
        raise ValueError(f"{path} sampled to zero pixels at step {step}")

    chromas: list[float] = []
    arcs: dict[int, dict] = {}
    peak = {"C": -1.0}
    neutral = 0
    for rgb in pixels:
        L, C, h = _oklch(rgb)
        chromas.append(C)
        if C > peak["C"]:
            peak = {"C": C, "L": L, "h": h, "hex": to_hex((rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0))}
        if C < NEUTRAL_CHROMA:
            neutral += 1
            continue
        bucket = int(h) // ARC_WIDTH * ARC_WIDTH
        arc = arcs.setdefault(bucket, {"chroma": [], "lightness": []})
        arc["chroma"].append(C)
        arc["lightness"].append(L)

    total = len(pixels)
    chromas.sort()
    reported = []
    for bucket in sorted(arcs):
        arc = arcs[bucket]
        arc_chroma = sorted(arc["chroma"])
        arc_light = sorted(arc["lightness"])
        reported.append(
            {
                "arc": f"{bucket}-{bucket + ARC_WIDTH}",
                "hue_from": bucket,
                "hue_to": bucket + ARC_WIDTH,
                "share_of_frame": round(len(arc_chroma) / total, 4),
                "chroma_mean": round(sum(arc_chroma) / len(arc_chroma), 4),
                "chroma_p98": round(_percentile(arc_chroma, 0.98), 4),
                "chroma_max": round(arc_chroma[-1], 4),
                "lightness_mean": round(sum(arc_light) / len(arc_light), 4),
                "lightness_min": round(arc_light[0], 4),
                "lightness_max": round(arc_light[-1], 4),
            }
        )
    reported.sort(key=lambda a: a["share_of_frame"], reverse=True)

    return {
        "image": str(path),
        "pixels": {"width": width, "height": height, "sampled": total, "step": step},
        "neutral_chroma_threshold": NEUTRAL_CHROMA,
        "neutral_share": round(neutral / total, 4),
        "chroma": {
            "mean": round(sum(chromas) / total, 4),
            "p90": round(_percentile(chromas, 0.90), 4),
            "p98": round(_percentile(chromas, 0.98), 4),
            "max": round(chromas[-1], 4),
        },
        "most_saturated_pixel": {
            "hex": peak["hex"],
            "L": round(peak["L"], 4),
            "C": round(peak["C"], 4),
            "h": round(peak["h"], 1),
        },
        "hue_arcs": reported,
        "what_this_does_not_establish": (
            "That the photograph is good, that its colour is the colour the product has in "
            "daylight, that the reference is licensed, or that a hue missing from this frame is "
            "missing from the brand."
        ),
    }


# ------------------------------------------------------------------------------- gates


def _arc_for_hue(measurement: dict, hue: float) -> dict | None:
    for arc in measurement["hue_arcs"]:
        if arc["hue_from"] <= hue < arc["hue_to"]:
            return arc
    return None


def check_against_reference(measurement: dict, colours: dict[str, str]) -> list[dict]:
    """Run the three house gates for each proposed brand colour against a measured reference."""
    gates = []
    reference_peak = measurement["chroma"]["max"]

    for role, hex_value in colours.items():
        lab = rgb_to_oklab(parse_hex(hex_value))
        C = round(math.hypot(lab[1], lab[2]), 4)
        h = round(math.degrees(math.atan2(lab[2], lab[1])) % 360.0, 1)

        if C < NEUTRAL_CHROMA:
            gates.append(
                {
                    "gate": "subject-holds-chroma-peak",
                    "role": role,
                    "colour": hex_value.upper(),
                    "status": "skipped",
                    "measured": f"chroma {C} is below the {NEUTRAL_CHROMA} neutral threshold",
                    "reading": "A neutral carries no hue argument against the reference. Paper, ink "
                    "and shadow are judged by plan_palette.py, not here.",
                    "evidence_grade": "house-rule",
                }
            )
            continue

        # Gate 1. The subject must stay the most saturated thing in the frame.
        ratio_to_peak = round(C / reference_peak, 3) if reference_peak else None
        if ratio_to_peak is None or ratio_to_peak > PEAK_MARGIN_FAIL:
            peak_status = "failed"
            peak_reading = (
                "Brand furniture is more saturated than any pixel of the subject by more than the "
                "sampling stride can account for, so the eye lands on the navigation instead of on "
                "the thing being sold."
            )
        elif ratio_to_peak > 1.0:
            peak_status = "review"
            peak_reading = (
                "Above the reference peak, but by less than the margin a change of sampling stride "
                "alone can move that peak. Re-measure at --step 1 before calling it either way."
            )
        else:
            peak_status = "passed"
            peak_reading = "The subject keeps the chromatic peak."
        gates.append(
            {
                "gate": "subject-holds-chroma-peak",
                "role": role,
                "colour": hex_value.upper(),
                "status": peak_status,
                "measured": f"accent chroma {C} against reference peak chroma {reference_peak} "
                f"(ratio {ratio_to_peak}, review above 1.0, fail above {PEAK_MARGIN_FAIL})",
                "verdict_if_failed": "ACCENT-OUTSHOUTS-SUBJECT",
                "reading": peak_reading,
                "evidence_grade": "house-rule",
            }
        )

        arc = _arc_for_hue(measurement, h)

        # Gate 2. Intensifying a colour the scene has is allowed; replacing it is not.
        if arc is None or arc["share_of_frame"] < MIN_ANCHOR_SHARE:
            gates.append(
                {
                    "gate": "accent-chroma-matches-reference",
                    "role": role,
                    "colour": hex_value.upper(),
                    "status": "skipped",
                    "measured": f"hue {h} deg has no arc above {MIN_ANCHOR_SHARE} share in the reference",
                    "reading": "Nothing to compare the chroma against. Gate 3 covers the absence.",
                    "evidence_grade": "house-rule",
                }
            )
        else:
            ceiling = arc["chroma_p98"]
            factor = round(C / ceiling, 3) if ceiling else None
            if factor is None or factor > CHROMA_INFLATION_FAIL:
                status = "failed"
            elif factor > CHROMA_INFLATION_REVIEW:
                status = "review"
            else:
                status = "passed"
            gates.append(
                {
                    "gate": "accent-chroma-matches-reference",
                    "role": role,
                    "colour": hex_value.upper(),
                    "status": status,
                    "measured": f"accent chroma {C} against arc {arc['arc']} p98 chroma {ceiling} "
                    f"(factor {factor}, review above {CHROMA_INFLATION_REVIEW}, fail above "
                    f"{CHROMA_INFLATION_FAIL})",
                    "verdict_if_failed": "CHROMA-INFLATED",
                    "reading": (
                        "The brand version is a saturated swatch that merely shares a hue name with "
                        "the scene. Pull chroma toward the measured value."
                        if status == "failed"
                        else "Above the glaze but within the band where print ink legitimately runs "
                        "hotter than the photographed surface. A human decides."
                        if status == "review"
                        else "The accent intensifies a colour the scene actually has."
                    ),
                    "evidence_grade": "house-rule",
                }
            )

        # Gate 3. Is the hue in the scene at all. Review, never fail: one frame is not a brand.
        share = arc["share_of_frame"] if arc else 0.0
        anchored = share >= MIN_ANCHOR_SHARE
        gates.append(
            {
                "gate": "accent-hue-is-anchored-in-reference",
                "role": role,
                "colour": hex_value.upper(),
                "status": "passed" if anchored else "review",
                "measured": f"hue {h} deg sits in arc {arc['arc'] if arc else 'none'} holding "
                f"{round(share * 100, 2)}% of the frame (anchor needs {MIN_ANCHOR_SHARE * 100}%)",
                "verdict_if_failed": "HUE-NOT-IN-REFERENCE",
                "reading": (
                    "The hue is in the photograph, so it can read as something the scene contains "
                    "rather than as a rectangle drawn on top."
                    if anchored
                    else "This hue is not in this frame. That is legitimate for a deliberate "
                    "contrast accent, and this gate cannot see the prop, room or package that may "
                    "carry it - so put it in the scene, or declare it as imported contrast."
                ),
                "evidence_grade": "house-rule",
            }
        )

    return gates


def compare_share(measurement: dict, rendered: dict, hue: float) -> dict:
    """Report how the area of one hue arc changed between the reference and the finished artwork.

    Reported, not gated. A brand rail may legitimately hold more of the page than the glaze holds
    of the photograph; there is no defensible threshold, so this returns the two numbers and the
    ratio and stops there.
    """
    source = _arc_for_hue(measurement, hue)
    output = _arc_for_hue(rendered, hue)
    source_share = source["share_of_frame"] if source else 0.0
    output_share = output["share_of_frame"] if output else 0.0
    return {
        "hue": round(hue, 1),
        "arc": (source or output or {}).get("arc", "none"),
        "share_in_reference": source_share,
        "share_in_artwork": output_share,
        "ratio": round(output_share / source_share, 2) if source_share else None,
        "chroma_mean_in_reference": (source or {}).get("chroma_mean"),
        "chroma_mean_in_artwork": (output or {}).get("chroma_mean"),
        "note": "Reported, not gated. No defensible threshold exists for how much of a page a "
        "brand colour may hold relative to its share of the source photograph.",
    }


# ------------------------------------------------------------------------------- CLI


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--image", help="Reference photograph to measure. PNG, 8-bit, non-interlaced.")
    parser.add_argument(
        "--check",
        nargs="+",
        metavar="ROLE=HEX",
        help="Brand colours to judge against the measurement, e.g. accent=#2A4BD7 support=#D9541E",
    )
    parser.add_argument(
        "--artwork",
        help="Finished artwork to compare arc-by-arc against the reference. Reports how the share "
        "and chroma of each hue moved between source and output; gates nothing.",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=4,
        help="Sampling stride in pixels on both axes (default 4). 1 reads every pixel and is slow.",
    )
    parser.add_argument("--output")
    args = parser.parse_args()

    use_utf8_stdout()

    if not args.image:
        parser.error("--image is required")

    try:
        payload = measure(args.image, args.step)
        colours: dict[str, str] = {}
        if args.check:
            for item in args.check:
                if "=" not in item:
                    raise ValueError(f"{item!r} is not ROLE=HEX")
                role, _, value = item.partition("=")
                parse_hex(value)
                colours[role.strip()] = value.strip()
            payload["proposed"] = {r: v.upper() for r, v in colours.items()}
            payload["acceptance_gates"] = check_against_reference(payload, colours)
        if args.artwork:
            rendered = measure(args.artwork, args.step)
            buckets = sorted(
                {a["hue_from"] for a in payload["hue_arcs"]} | {a["hue_from"] for a in rendered["hue_arcs"]}
            )
            payload["artwork"] = {
                "image": rendered["image"],
                "chroma": rendered["chroma"],
                "most_saturated_pixel": rendered["most_saturated_pixel"],
                "arc_shift": [
                    compare_share(payload, rendered, bucket + ARC_WIDTH / 2) for bucket in buckets
                ],
            }
    except (ValueError, OSError, zlib.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    emit_json(payload, args.output)

    # Same convention as plan_palette.py: 2 on a failed gate, 3 when nothing failed but something
    # needs a human decision, 0 otherwise. A skipped gate changes nothing.
    gates = payload.get("acceptance_gates", [])
    if any(g["status"] == "failed" for g in gates):
        return 2
    if any(g["status"] == "review" for g in gates):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
