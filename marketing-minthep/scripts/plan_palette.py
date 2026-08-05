#!/usr/bin/env python3
"""Check and build a colour palette with arithmetic instead of taste.

Colour combination is taught as a wheel: pick a hue, step 180 degrees, call it
complementary. The wheel is a way of generating candidates, not a way of judging them. What
actually decides whether two colours work together on a package, a thumbnail or a landing
page is three separate quantities - how far apart their hues are, how far apart their
lightnesses are, and how much chroma the palette spends in total - and all three are
measurable before anyone opens a design tool.

This script measures them. Give it a palette and it reports, per pair, the WCAG contrast
ratio and what that ratio permits; the perceptual lightness separation in OKLCH; whether the
pair will vibrate at its shared edge; whether the pair survives the three dichromacies; and
whether the palette as a whole spends more chroma than it can carry. Give it one seed colour
instead and it generates the classical schemes with lightness and chroma held to the same
gates, so a scheme arrives already checked.

Everything is stdlib. No key, no network, no image provider.

Spaces used, and why each one is here:

- sRGB, because that is what a hex value means and what a screen shows.
- Linear sRGB, because both the WCAG luminance formula and the colour-vision-deficiency
  matrices are defined on light, not on gamma-encoded numbers.
- OKLab and OKLCH (Ottosson 2020), because hue rotation and lightness comparison in HSV are
  wrong in a way that matters commercially: HSV gives #FFFF00 and #0000FF the same value of
  100%, and in OKLCH they sit at lightness 0.968 and 0.452, which is half the scale apart.
  Against white the yellow contrasts at 1.07:1 and the blue at 8.59:1. So a "harmony" built
  on equal HSV value produces a palette whose members are nowhere near equally light, and one
  of them cannot be seen. The derivation below records the four numbers for review.

What this script cannot tell you: whether the palette suits the brand, whether the category
already owns it, whether a colour carries a meaning in the market you are selling into, and
whether the accent is the one a competitor has registered as a trademark. Those are
`references/colour-combination.md`, `data/palettes.csv` and a search, not arithmetic.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit_json, use_utf8_stdout  # noqa: E402

SKILL_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = SKILL_ROOT / "data"

# WCAG 2.x SC 1.4.3 and SC 1.4.11. Large scale is 18pt / 24px, or 14pt / 18.66px bold.
WCAG_BODY = 4.5
WCAG_LARGE = 3.0
WCAG_NON_TEXT = 3.0

# House gates. These are NOT standards, and the important honesty is about which part of each
# gate has evidence behind it. In every case the *shape* of the rule is defensible - the effect
# it screens for is documented - and the *number* is ours. No published threshold exists for any
# of the four below. `data/colour-gates.csv` records that per gate, and the report prints the
# grade beside the verdict, so nobody quotes a house number as a requirement.
#
# LIGHTNESS_SEPARATION: two colours whose hues are close read as one colour printed unevenly
# unless their OKLCH lightness differs. An independent derivation of this rule landed on the
# same form in the same space with 0.10; we hold 0.12 because when both numbers are invented,
# the stricter one costs a designer one adjustment and the looser one costs a reader the
# distinction. Do not describe 0.12 as a perceptual boundary. It is not one.
#
# Which is why there are two numbers. A single hard edge on an invented threshold produces
# verdicts it cannot support: three of the twenty shipped palettes missed 0.12 by less than 0.01,
# and one by 0.0004. Calling that a failure is the same false precision as quoting a house rule as
# a standard. So the span between the two independent derivations is treated as what it is - the
# range over which nobody knows - and a pair landing inside it is returned for review rather than
# judged. Below 0.10 both derivations agree the pair is broken, and it fails. The band's edges come
# from documented disagreement, not from what would make our own data pass.
LIGHTNESS_SEPARATION = 0.12
LIGHTNESS_SEPARATION_FAIL = 0.10
SAME_HUE_DEGREES = 30.0
# HUE_NEEDS_CHROMA is the one threshold in this file that was measured rather than chosen, and it
# exists because the same-hue rule was firing on colours that have no hue. #F2F2F0 sits at chroma
# 0.003; its hue angle of 110 degrees is not a property of the colour, it is what is left of a
# rounding error, and asking whether it is "the same hue" as lime is not a question.
#
# The floor comes from sweeping the sRGB cube at every fifth value, keeping everything under
# chroma 0.055, and measuring how far each of those colours' OKLCH hue angle moves when one 8-bit
# channel changes by one - the smallest change 8-bit colour can express. Bucketed by chroma rounded
# to 0.01, median and 90th percentile swing:
#
#     C     0.00   0.01   0.02   0.03   0.04   0.05
#     med    72.7    5.3    2.8    1.9    1.4    1.1   degrees
#     p90   163.6   11.3    5.0    3.3    2.5    1.9   degrees
#
# At chroma 0 the median swing is more than twice the entire 30-degree same-hue window, so the
# angle is not a property of the colour. Two colours can each wobble by the p90 amount in opposite
# directions, so for quantisation not to decide the test, 2 x p90 has to stay well inside that
# window - under a quarter of it. 0.03 gives 6.6 degrees of 30, which is 22 percent; 0.02 gives
# 10.0, which is 33 percent and too much of the answer. Sampling every third value instead of every
# fifth moves no p90 in this table by more than 0.1 degrees except in the C 0.00 bucket, where the
# sample is small. Re-run the sweep before changing this threshold rather than trusting the table above.
HUE_NEEDS_CHROMA = 0.03
# VIBRATION: near-equal lightness plus high chroma plus far-apart hue produces an edge the eye
# cannot settle on. All three conditions must hold; any one alone is harmless. The effect
# (chromostereopsis) is real and its onset has never been mapped into OKLCH across displays and
# observers, so this screens for manual review rather than proving anything.
VIBRATION_MAX_DELTA_L = 0.10
VIBRATION_MIN_CHROMA = 0.14
VIBRATION_MIN_HUE_GAP = 100.0
# CHROMA BUDGET: a palette can carry one loud colour. Two compete and neither wins. A count
# alone cannot tell a 20px accent from a full-bleed panel at the same chroma, so when the caller
# supplies surface shares the budget is also checked by area. Without shares that second check
# reports skipped, never passed: a share nobody measured would be an invented input.
LOUD_CHROMA = 0.19
CHROMA_BUDGET_LOUD_MAX = 1
CHROMA_SHARE_MAX = 0.20
# RAMP: equal increments of the OKLCH lightness coordinate are not equal perceptual steps once
# chroma varies along the path, so a ramp is cut at equal fractions of measured OKLab arc length
# and then checked for evenness against its own mean step.
RAMP_EVENNESS_TOLERANCE = 0.15
RAMP_ARC_SAMPLES = 256
RAMP_RELAX_SWEEPS = 400
# CVD: OKLab euclidean distance below which two colours are not reliably told apart.
CVD_COLLAPSE_DISTANCE = 0.09

SCHEMES = {
    "monochrome": (0.0,),
    "analogous": (-30.0, 30.0),
    "complementary": (180.0,),
    "split-complementary": (150.0, 210.0),
    "triadic": (120.0, 240.0),
    "tetradic": (90.0, 180.0, 270.0),
}

# Machado, Oliveira and Fernandes, "A Physiologically-based Model for Simulation of Color
# Vision Deficiency", IEEE Transactions on Visualization and Computer Graphics 15(6), 2009.
# Severity 1.0 matrices, applied to linear sRGB.
CVD_MATRICES = {
    "protanopia": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deuteranopia": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritanopia": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


# --------------------------------------------------------------------------- conversions


def parse_hex(value: str) -> tuple[float, float, float]:
    text = value.strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        raise ValueError(f"{value!r} is not a 3 or 6 digit hex colour")
    try:
        return tuple(int(text[i : i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]
    except ValueError as exc:
        raise ValueError(f"{value!r} is not a hex colour") from exc


def to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{round(max(0.0, min(1.0, c)) * 255):02X}" for c in rgb)


def linearise(channel: float) -> float:
    # WCAG 2.1 and IEC 61966-2-1. The threshold is 0.04045 on the encoded value; the
    # 0.03928 that appears in older WCAG text is a rounding of the same boundary and
    # changes no result at 8-bit precision.
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def delinearise(channel: float) -> float:
    if channel <= 0.0031308:
        return 12.92 * channel
    return 1.055 * (channel ** (1 / 2.4)) - 0.055


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = (linearise(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(one: str, two: str) -> float:
    a = relative_luminance(parse_hex(one))
    b = relative_luminance(parse_hex(two))
    lighter, darker = max(a, b), min(a, b)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def rgb_to_oklab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (linearise(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def oklab_to_rgb(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    L, a, b = lab
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = (v**3 for v in (l_, m_, s_))
    return (
        delinearise(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
        delinearise(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
        delinearise(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s),
    )


def to_oklch(hex_value: str) -> dict:
    L, a, b = rgb_to_oklab(parse_hex(hex_value))
    chroma = math.hypot(a, b)
    hue = math.degrees(math.atan2(b, a)) % 360.0
    return {"L": round(L, 4), "C": round(chroma, 4), "h": round(hue, 1)}


def from_oklch(L: float, C: float, h: float) -> tuple[str, bool]:
    """Return the hex for an OKLCH triple and whether chroma had to be reduced to fit sRGB.

    Out-of-gamut is the normal case for a saturated hue at an extreme lightness, and silently
    clipping the channels shifts the hue. Reducing chroma until the colour fits keeps hue and
    lightness, which are the two things a scheme is actually made of.
    """
    radians = math.radians(h)
    for step in range(0, 101):
        trial = C * (1 - step / 100.0)
        rgb = oklab_to_rgb((L, trial * math.cos(radians), trial * math.sin(radians)))
        if all(-0.0005 <= c <= 1.0005 for c in rgb):
            return to_hex(rgb), step > 0
    return to_hex(oklab_to_rgb((L, 0.0, 0.0))), True


def oklab_distance(one: str, two: str) -> float:
    a = rgb_to_oklab(parse_hex(one))
    b = rgb_to_oklab(parse_hex(two))
    return round(math.dist(a, b), 4)


def simulate_cvd(hex_value: str, deficiency: str) -> str:
    matrix = CVD_MATRICES[deficiency]
    linear = [linearise(c) for c in parse_hex(hex_value)]
    out = [sum(row[i] * linear[i] for i in range(3)) for row in matrix]
    return to_hex(tuple(delinearise(max(0.0, min(1.0, v))) for v in out))  # type: ignore[arg-type]


def hue_gap(one: float, two: float) -> float:
    raw = abs(one - two) % 360.0
    return min(raw, 360.0 - raw)


# ------------------------------------------------------------------------------- checks


def check_pair(name_one: str, hex_one: str, name_two: str, hex_two: str) -> dict:
    ratio = contrast_ratio(hex_one, hex_two)
    one, two = to_oklch(hex_one), to_oklch(hex_two)
    delta_l = round(abs(one["L"] - two["L"]), 4)
    gap = round(hue_gap(one["h"], two["h"]), 1)

    # One colour filling two roles is a decision, not a defect, and every separation gate below
    # would otherwise fire on it: zero lightness difference and zero hue gap is what a colour
    # scores against itself. Reporting that as a failed palette taught the reader to distrust the
    # gates, which is worse than missing a finding. It is still worth naming, because a palette
    # whose accent equals its ink has no accent, and that is a hierarchy question for the
    # designer rather than an arithmetic one for this script.
    if parse_hex(hex_one) == parse_hex(hex_two):
        return {
            "pair": f"{name_one} / {name_two}",
            "hex": [hex_one.upper(), hex_two.upper()],
            "contrast_ratio": ratio,
            "permits": ["nothing; a colour cannot be distinguished from itself"],
            "oklch": {name_one: one, name_two: two},
            "delta_lightness": delta_l,
            "hue_gap_degrees": gap,
            "oklab_distance": 0.0,
            "colour_vision": {d: {"seen_as": [simulate_cvd(hex_one, d)] * 2, "distance": 0.0,
                                  "collapses": False} for d in CVD_MATRICES},
            "same_colour_in_two_roles": True,
            "findings": [],
            "notes": [
                f"{name_one} and {name_two} are the same colour, so the separation gates do not "
                f"apply to this pair. If {name_two} was meant to be an accent, the palette has "
                "none; if the repetition is deliberate, nothing here is wrong."
            ],
            "passes": True,
        }

    permits = []
    if ratio >= 7.0:
        permits.append("body text at AAA")
    if ratio >= WCAG_BODY:
        permits.append("body text at AA")
    if ratio >= WCAG_LARGE:
        permits.append("large text at AA (18pt, or 14pt bold)")
    if ratio >= WCAG_NON_TEXT:
        permits.append("a control boundary or icon under SC 1.4.11")
    if not permits:
        permits.append("decoration only; this pair may not carry text or an interface edge")

    findings = []
    # Same hue and similar lightness is the commonest palette failure and the one a designer
    # cannot see on a large swatch, because size hides it. It shows up at thumbnail scale.
    #
    # Both colours have to actually have a hue for the comparison to mean anything. Without the
    # chroma floor this fired on off-white against lime and called them the same hue family, which
    # is how a gate loses its reader: one absurd finding and the other eight stop being read.
    hue_is_meaningful = min(one["C"], two["C"]) >= HUE_NEEDS_CHROMA
    if hue_is_meaningful and gap <= SAME_HUE_DEGREES and delta_l < LIGHTNESS_SEPARATION:
        findings.append(
            f"hues are {gap} degrees apart and lightness differs by only {delta_l}; "
            f"below the {LIGHTNESS_SEPARATION} house floor these read as one colour at "
            "thumbnail size. Separate the lightness rather than the hue."
        )
    if (
        delta_l <= VIBRATION_MAX_DELTA_L
        and min(one["C"], two["C"]) >= VIBRATION_MIN_CHROMA
        and gap >= VIBRATION_MIN_HUE_GAP
    ):
        findings.append(
            f"equal lightness ({delta_l} apart), both chromatic (C {one['C']} and {two['C']}), "
            f"hues {gap} degrees apart: the shared edge will vibrate. Drop one lightness by "
            f"{LIGHTNESS_SEPARATION} or take {VIBRATION_MIN_CHROMA - 0.04:.2f} off one chroma."
        )

    cvd = {}
    baseline = oklab_distance(hex_one, hex_two)
    for deficiency in CVD_MATRICES:
        seen_one = simulate_cvd(hex_one, deficiency)
        seen_two = simulate_cvd(hex_two, deficiency)
        distance = oklab_distance(seen_one, seen_two)
        collapsed = distance < CVD_COLLAPSE_DISTANCE <= baseline
        cvd[deficiency] = {
            "seen_as": [seen_one, seen_two],
            "distance": distance,
            "collapses": collapsed,
        }
        if collapsed:
            findings.append(
                f"under {deficiency} the pair closes from {baseline} to {distance}; anything "
                "these two colours distinguish must also be distinguished by shape, label or "
                "position, never by hue alone"
            )

    return {
        "pair": f"{name_one} / {name_two}",
        "hex": [hex_one.upper(), hex_two.upper()],
        "contrast_ratio": ratio,
        "permits": permits,
        "oklch": {name_one: one, name_two: two},
        "delta_lightness": delta_l,
        "hue_gap_degrees": gap,
        "oklab_distance": baseline,
        "colour_vision": cvd,
        "same_colour_in_two_roles": False,
        "findings": findings,
        "notes": [],
        "passes": not findings,
    }


def check_chroma_budget(colours: dict[str, str], shares: dict[str, float] | None = None) -> dict:
    """Check the loud-colour count, and the loud-colour area when the caller measured it.

    The count on its own has a hole this used to state and not fix: it cannot tell a 20px accent
    from a full-bleed panel at the same chroma. Surface share closes it, but only when somebody
    has actually measured the layout. Absent shares the area check reports `skipped`, never
    `passed`, because a share nobody measured is an invented input and the whole value of this
    script is that it does not invent inputs.
    """
    measured = {name: to_oklch(value) for name, value in colours.items()}
    loud = sorted(
        (name for name, m in measured.items() if m["C"] >= LOUD_CHROMA),
        key=lambda n: measured[n]["C"],
        reverse=True,
    )
    total = round(sum(m["C"] for m in measured.values()), 4)
    verdict = (
        f"{len(loud)} colours at or above C {LOUD_CHROMA}: {', '.join(loud)}. A palette carries "
        f"one loud colour; past that they compete and the eye has no primary. Keep "
        f"{loud[0]} and pull the rest below {LOUD_CHROMA}, or move them to small-area use only."
        if len(loud) > CHROMA_BUDGET_LOUD_MAX
        else f"{len(loud)} loud colour(s), within the budget of {CHROMA_BUDGET_LOUD_MAX}."
    )
    area: dict = {"status": "skipped", "why": "no surface shares were supplied, so the area "
                  "budget was not evaluated. Pass --share ROLE=FRACTION to evaluate it."}
    if shares:
        unknown = sorted(set(shares) - set(colours))
        if unknown:
            raise ValueError(f"shares name colours that are not in the palette: {', '.join(unknown)}")
        loud_share = round(sum(shares.get(name, 0.0) for name in loud), 4)
        supplied = round(sum(shares.values()), 4)
        area = {
            "status": "passed" if loud_share <= CHROMA_SHARE_MAX else "failed",
            "loud_share": loud_share,
            "limit": CHROMA_SHARE_MAX,
            "shares_supplied_total": supplied,
            "verdict": (
                f"loud colours cover {loud_share:.0%} of the measured area, within the "
                f"{CHROMA_SHARE_MAX:.0%} budget."
                if loud_share <= CHROMA_SHARE_MAX
                else f"loud colours cover {loud_share:.0%} of the measured area against a "
                f"{CHROMA_SHARE_MAX:.0%} budget. At that share the accent has become the "
                f"background; either shrink its area or take chroma off it."
            ),
        }
        if abs(supplied - 1.0) > 0.02:
            area["note"] = (
                f"the supplied shares total {supplied:.2f}, not 1.00. The check ran against what "
                "was given, so the result describes only the area you measured."
            )
    return {
        "loud_colours": loud,
        "loud_threshold": LOUD_CHROMA,
        "total_chroma": total,
        # `passes` treats a skipped area check as not-failing, which is the only defensible reading:
        # an unmeasured layout is neither compliant nor in breach. `count` and `surface_share` are
        # kept separate so a caller can tell which of the two budgets actually decided the answer.
        "passes": len(loud) <= CHROMA_BUDGET_LOUD_MAX and area["status"] != "failed",
        "count": {
            "status": "passed" if len(loud) <= CHROMA_BUDGET_LOUD_MAX else "failed",
            "loud_count": len(loud),
            "limit": CHROMA_BUDGET_LOUD_MAX,
            "verdict": verdict,
        },
        "verdict": verdict,
        "surface_share": area,
        "what_it_cannot_tell_you": (
            "Whether the loud colour is the right one. The budget is arithmetic about how many "
            "and how much; which colour leads is a positioning decision this cannot reach."
        ),
    }


def _ramp_path(seed_chroma: float, hue: float, position: float) -> tuple[float, float]:
    """The continuous path a ramp follows, as (lightness, chroma) at 0..1 along it.

    Chroma is tapered because a very light or very dark step cannot hold the seed's chroma
    inside sRGB, and forcing it there is what produces the muddy top and bottom of most
    hand-built ramps. Peak chroma sits near the middle, where the gamut is widest.
    """
    lightness = 0.97 - position * 0.92
    taper = math.sin(math.pi * position) ** 0.6
    return lightness, seed_chroma * max(0.12, taper)


def _equalise_chords(samples: list[tuple[float, str, bool]], cuts: list[int]) -> list[int]:
    """Nudge interior cuts until adjacent swatches are as close to equidistant as the path allows.

    Equal arc length is the right starting point and the wrong finishing point. Arc length is
    additive along the curve; what a viewer compares is the straight-line OKLab distance between
    two swatches sitting next to each other. Where the path curves sharply the arc between two
    cuts overshoots the chord between them, so equal-arc cuts come out unequal to the eye - and
    the path curves hardest at the dark end, where chroma collapses toward black. That is exactly
    where equal-arc ramps were measuring short.

    So this hill-climbs on the quantity that is actually judged: it moves each interior cut one
    sample at a time while the squared spread of adjacent chord distances falls. Squared spread
    rather than the worst deviation, because the worst deviation is flat under a single-sample
    move and gives the search nothing to descend. Endpoints stay fixed, order is preserved, and
    the objective strictly decreases, so it terminates.
    """

    def spread(positions: list[int]) -> float:
        chords = [oklab_distance(samples[a][1], samples[b][1])
                  for a, b in zip(positions, positions[1:])]
        mean = sum(chords) / len(chords)
        return sum((c - mean) ** 2 for c in chords)

    best = list(cuts)
    score = spread(best)
    for _ in range(RAMP_RELAX_SWEEPS):
        improved = False
        for index in range(1, len(best) - 1):
            for delta in (-1, 1):
                moved = best[index] + delta
                if not best[index - 1] < moved < best[index + 1]:
                    continue
                candidate = list(best)
                candidate[index] = moved
                trial = spread(candidate)
                if trial < score - 1e-12:
                    best, score, improved = candidate, trial, True
        if not improved:
            break
    return best


def build_ramp(seed: str, steps: int) -> list[dict]:
    """A ramp whose adjacent steps are equidistant in OKLab, not merely equal in coordinates.

    Interpolating in sRGB gives steps that crowd in the middle and flatten at the ends, which is
    the failure this whole function exists to avoid. But spacing the OKLCH lightness coordinate
    evenly does not fix it either, and that is the subtler error: because chroma varies along the
    path, equal lightness increments cover unequal perceptual distances, so the tapered ends move
    less than the middle even though the L numbers are evenly spaced.

    So the path is sampled densely, cut at equal fractions of its measured arc length, and then
    relaxed until adjacent swatches sit as close to equidistant as the path permits. Measured over
    ten recorded calibration seeds, at nine steps, the worst step falls from up to 35.1 percent
    off the mean under linear lightness to 5.5 percent, and every one of the ten improves. `evenness`
    still reports the residual, because on some hues the path genuinely cannot hold the number of
    steps asked for: at twelve steps the worst case is 17.9 percent and the gate fails, which is more
    use than a ramp that looks even in its coordinates and has two indistinguishable swatches at the
    dark end.
    """
    base = to_oklch(seed)
    samples = []
    for index in range(RAMP_ARC_SAMPLES + 1):
        position = index / RAMP_ARC_SAMPLES
        lightness, chroma = _ramp_path(base["C"], base["h"], position)
        hex_value, clipped = from_oklch(lightness, chroma, base["h"])
        samples.append((position, hex_value, clipped))

    cumulative = [0.0]
    for previous, current in zip(samples, samples[1:]):
        cumulative.append(cumulative[-1] + oklab_distance(previous[1], current[1]))
    total = cumulative[-1]

    cuts = []
    for index in range(steps):
        target = total * index / (steps - 1)
        # The path is monotone in distance, so the first sample at or past the target is the cut.
        cuts.append(next((i for i, d in enumerate(cumulative) if d >= target), len(samples) - 1))
    cuts = _equalise_chords(samples, cuts)

    out = []
    for order, cut in enumerate(cuts):
        _, hex_value, clipped = samples[cut]
        out.append(
            {
                "step": (order + 1) * 100 // 1 if steps == 9 else order + 1,
                "hex": hex_value,
                "oklch": to_oklch(hex_value),
                "chroma_reduced_to_fit_srgb": clipped,
            }
        )
    return out


def check_ramp_evenness(ramp: list[dict]) -> dict:
    """Measure the ramp against its own mean step, because the cut is not the last word.

    Cutting at equal arc length gets the steps right on the path; fitting each step into sRGB can
    then move it off the path. This reports what actually came out rather than what was intended.
    """
    distances = [round(oklab_distance(one["hex"], two["hex"]), 4)
                 for one, two in zip(ramp, ramp[1:])]
    if not distances:
        return {"status": "skipped", "why": "a ramp of one step has no adjacent distances"}
    mean = sum(distances) / len(distances)
    worst = max(abs(d - mean) for d in distances) / mean if mean else 0.0
    return {
        "status": "passed" if worst <= RAMP_EVENNESS_TOLERANCE else "failed",
        "step_distances": distances,
        "mean_step": round(mean, 4),
        "worst_deviation": round(worst, 4),
        "tolerance": RAMP_EVENNESS_TOLERANCE,
        "verdict": (
            f"the widest step is {worst:.1%} off the mean, within the "
            f"{RAMP_EVENNESS_TOLERANCE:.0%} tolerance."
            if worst <= RAMP_EVENNESS_TOLERANCE
            else f"the widest step is {worst:.1%} off the mean against a "
            f"{RAMP_EVENNESS_TOLERANCE:.0%} tolerance, which reads as a missing tone. This "
            f"usually means the seed chroma cannot be held at one end of the ramp."
        ),
        "what_it_cannot_tell_you": (
            "Whether the ramp has the right number of steps for the interface, or whether its "
            "lightest and darkest ends are the ones the design needs."
        ),
    }


def build_scheme(seed: str, scheme: str, background: str | None) -> dict:
    if scheme not in SCHEMES:
        raise ValueError(f"unknown scheme {scheme!r}; choose from {', '.join(sorted(SCHEMES))}")
    base = to_oklch(seed)
    members = [{"role": "seed", "hex": seed.upper(), "oklch": base, "chroma_reduced_to_fit_srgb": False}]
    for index, offset in enumerate(SCHEMES[scheme]):
        hue = (base["h"] + offset) % 360.0
        # Hold lightness and chroma constant across the scheme. Rotating hue alone is what
        # makes the members siblings; letting lightness drift with the hue is what makes a
        # generated scheme look accidental.
        hex_value, clipped = from_oklch(base["L"], base["C"], hue)
        members.append(
            {
                "role": f"{scheme}-{index + 1}",
                "hex": hex_value,
                "oklch": to_oklch(hex_value),
                "hue_offset": offset,
                "chroma_reduced_to_fit_srgb": clipped,
            }
        )
    note = (
        "Every member shares the seed's lightness, so none of them can carry text against "
        "another. A scheme is a set of accents; the text colour and the background are a "
        "separate decision made against contrast, not against the wheel."
    )
    result = {"scheme": scheme, "members": members, "note": note}
    if background:
        result["against_background"] = [
            {
                "role": member["role"],
                "hex": member["hex"],
                "contrast_ratio": contrast_ratio(member["hex"], background),
                "may_carry_body_text": contrast_ratio(member["hex"], background) >= WCAG_BODY,
            }
            for member in members
        ]
    return result


def load_palette_row(palette_id: str) -> dict[str, str]:
    path = DATA_DIR / "palettes.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["id"] == palette_id:
                return {
                    "bg": row["bg"],
                    "ink": row["ink"],
                    "accent": row["accent"],
                    "support": row["support"],
                }
    raise ValueError(f"no palette {palette_id!r} in data/palettes.csv")


def check_palette(
    colours: dict[str, str],
    shares: dict[str, float] | None = None,
    carries_meaning: list[tuple[str, str]] | None = None,
) -> dict:
    """Measure every pair, then report the gates by name, by evidence grade and by what is decided.

    Each gate carries the grade `data/colour-gates.csv` records for it, because the difference
    between "WCAG says so" and "we decided this" is the first thing a designer pushing back
    deserves to know.

    Four statuses, and the distinction between the last two is the point of the function:

    - `passed` and `failed` mean what they say.
    - `skipped` means the input was never supplied. The surface-share budget cannot be met by a
      layout nobody measured, so it reports skipped rather than passed.
    - `review` means the arithmetic ran and does not settle it. Two gates land here honestly. A
      colour-vision collapse is not a palette defect, because SC 1.4.1 is broken by a use where
      colour alone carries meaning, and the layout is invisible from here - pass `carries_meaning`
      and the same finding becomes a failure. A same-hue pair inside the band where two independent
      derivations disagree is likewise not something arithmetic should rule on.

    `review` exists so that the gates that do fail mean something. A checker that returns a verdict
    on everything gets ignored on everything.
    """
    names = list(colours)
    pairs = [
        check_pair(names[i], colours[names[i]], names[j], colours[names[j]])
        for i in range(len(names))
        for j in range(i + 1, len(names))
    ]
    budget = check_chroma_budget(colours, shares)
    failing = [p["pair"] for p in pairs if not p["passes"]]
    # The separation gates ask whether two colours can be told apart, which is not a question a
    # colour used twice can answer. Excluding those pairs here rather than inside each gate keeps
    # the exclusion in one place and visible in the payload.
    distinct = [p for p in pairs if not p["same_colour_in_two_roles"]]
    doubled = [p["pair"] for p in pairs if p["same_colour_in_two_roles"]]
    collapsing = [p for p in distinct if any(v["collapses"] for v in p["colour_vision"].values())]
    same_hue_tight = [
        p for p in distinct
        if p["hue_gap_degrees"] <= SAME_HUE_DEGREES
        and p["delta_lightness"] < LIGHTNESS_SEPARATION
        and min(v["C"] for v in p["oklch"].values()) >= HUE_NEEDS_CHROMA
    ]
    # A declared pair is one the caller says carries meaning on its own. Order is not significant,
    # so both spellings are accepted and the lookup is done on a frozenset of the two role names.
    declared = set()
    for one, two in carries_meaning or []:
        declared.add(f"{one} / {two}")
        declared.add(f"{two} / {one}")

    def verdict(passed: bool) -> str:
        return "passed" if passed else "failed"

    gates = [
        {
            "gate": "body-text-contrast",
            "evidence_grade": "standard-requirement",
            "source": "WCAG 2.2 SC 1.4.3",
            "status": verdict(any(p["contrast_ratio"] >= WCAG_BODY for p in pairs)),
            "measured": f"best pair reaches {max(p['contrast_ratio'] for p in pairs):.2f}:1",
        },
        {
            "gate": "large-text-contrast",
            "evidence_grade": "standard-requirement",
            "source": "WCAG 2.2 SC 1.4.3",
            "status": verdict(any(p["contrast_ratio"] >= WCAG_LARGE for p in pairs)),
            "measured": f"{sum(1 for p in pairs if p['contrast_ratio'] >= WCAG_LARGE)} of "
            f"{len(pairs)} pairs reach {WCAG_LARGE}:1",
        },
        {
            "gate": "non-text-contrast",
            "evidence_grade": "standard-requirement",
            "source": "WCAG 2.2 SC 1.4.11",
            "status": verdict(any(p["contrast_ratio"] >= WCAG_NON_TEXT for p in pairs)),
            "measured": f"{sum(1 for p in pairs if p['contrast_ratio'] >= WCAG_NON_TEXT)} of "
            f"{len(pairs)} pairs reach {WCAG_NON_TEXT}:1",
        },
        {
            "gate": "colour-is-not-the-only-cue",
            "evidence_grade": "standard-requirement-with-house-threshold",
            "source": "WCAG 2.2 SC 1.4.1; simulation from Machado et al. 2009; the "
            f"{CVD_COLLAPSE_DISTANCE} collapse distance is ours",
            "status": (
                "passed" if not collapsing
                else "failed" if [p for p in collapsing if p["pair"] in declared]
                else "review"
            ),
            "measured": f"{len(collapsing)} of {len(distinct)} pairs collapse under simulated "
            "dichromacy" + (f": {', '.join(p['pair'] for p in collapsing)}" if collapsing else ""),
            "why_this_status": (
                "no pair closes under any of the three dichromacies." if not collapsing
                else "a pair you declared as carrying meaning closes under simulation, so colour "
                "alone cannot carry it." if [p for p in collapsing if p["pair"] in declared]
                else "SC 1.4.1 is broken by a use, not by a palette. These pairs close under "
                "simulation, but whether that matters depends on whether either one is ever the "
                "only thing telling two states apart, and this script cannot see the layout. "
                "Declare the pairs that carry meaning with --carries-meaning ROLE+ROLE to have "
                "them judged instead of reported."
            ),
        },
        {
            "gate": "same-hue-lightness-separation",
            "evidence_grade": "house-rule",
            "source": f"no published threshold; the {LIGHTNESS_SEPARATION_FAIL} to "
            f"{LIGHTNESS_SEPARATION} band is the span between two independent derivations, and a "
            "pair inside it is reported rather than judged",
            "status": (
                "failed" if [p for p in same_hue_tight if p["delta_lightness"] < LIGHTNESS_SEPARATION_FAIL]
                else "review" if same_hue_tight
                else "passed"
            ),
            "measured": f"{sum(1 for p in distinct if p['hue_gap_degrees'] <= SAME_HUE_DEGREES)}"
            f" pairs sit within {SAME_HUE_DEGREES} degrees of hue"
            + (
                "; "
                + ", ".join(f"{p['pair']} separated by {p['delta_lightness']}" for p in same_hue_tight)
                if same_hue_tight
                else ""
            ),
            "why_this_status": (
                "every close-hue pair clears the separation floor." if not same_hue_tight
                else f"a close-hue pair sits below {LIGHTNESS_SEPARATION_FAIL}, which is under both "
                "derivations of this rule, so it reads as one colour rather than two."
                if [p for p in same_hue_tight if p["delta_lightness"] < LIGHTNESS_SEPARATION_FAIL]
                else f"the pair lands between {LIGHTNESS_SEPARATION_FAIL} and "
                f"{LIGHTNESS_SEPARATION}, where our number and an independent one disagree. Look at "
                "it at the smallest size it has to work, and decide. A verdict here would be "
                "arithmetic pretending to be perception."
            ),
        },
        {
            "gate": "no-vibrating-edge",
            "evidence_grade": "house-rule",
            "source": "the effect is documented, the onset is not; this is a screening rule",
            "status": verdict(
                all(
                    not (
                        p["delta_lightness"] <= VIBRATION_MAX_DELTA_L
                        and p["hue_gap_degrees"] >= VIBRATION_MIN_HUE_GAP
                        and min(v["C"] for v in p["oklch"].values()) >= VIBRATION_MIN_CHROMA
                    )
                    for p in distinct
                )
            ),
            "measured": "screens lightness, chroma and hue gap together",
        },
        {
            "gate": "chroma-budget-by-count",
            "evidence_grade": "house-rule",
            "source": "a composition convention, not a measurement",
            "status": verdict(budget["count"]["status"] == "passed"),
            "measured": budget["count"]["verdict"],
        },
        {
            "gate": "chroma-budget-by-surface-share",
            "evidence_grade": "house-rule",
            "source": f"no published threshold; {CHROMA_SHARE_MAX} is ours, and only checked "
            "against shares somebody measured",
            "status": budget["surface_share"]["status"],
            "measured": budget["surface_share"].get("verdict")
            or budget["surface_share"].get("why", ""),
        },
    ]
    failed = [g["gate"] for g in gates if g["status"] == "failed"]
    skipped = [g["gate"] for g in gates if g["status"] == "skipped"]
    review = [g["gate"] for g in gates if g["status"] == "review"]
    passed = [g["gate"] for g in gates if g["status"] == "passed"]

    if failed:
        summary = (
            f"Palette fails {len(failed)} of {len(gates)} gates: {', '.join(failed)}. Fix the "
            "named quantity; do not swap the colour for one that feels better. Check the evidence "
            "grade before conceding a house rule to a client."
        )
    else:
        summary = f"Palette clears {len(passed)} of {len(gates)} gates with none failing"
        if review:
            summary += (
                f", and returns {len(review)} for a decision this script should not make "
                f"({', '.join(review)}); read `why_this_status` on each"
            )
        if skipped:
            summary += f", and skips {len(skipped)} for want of input"
        summary += (
            ". The arithmetic is clear; whether it suits the brand and whether the category "
            "already owns it are not arithmetic questions."
        )

    return {
        "colours": {k: v.upper() for k, v in colours.items()},
        "measured": {k: to_oklch(v) for k, v in colours.items()},
        "surface_shares": shares or {},
        "pairs_carrying_meaning": sorted(declared) or [],
        "same_colour_in_two_roles": doubled,
        "pairs": pairs,
        "chroma_budget": budget,
        "acceptance_gates": gates,
        "failing_gates": failed,
        "gates_for_review": review,
        "skipped_gates": skipped,
        "failing_pairs": failing,
        "verdict": summary,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", nargs="+", metavar="ROLE=HEX", help="Palette to check, e.g. bg=#F5F1E8 ink=#141414 accent=#2A4BD7")
    parser.add_argument("--palette-id", help="Check a palette already in data/palettes.csv by id.")
    parser.add_argument("--scheme", choices=sorted(SCHEMES), help="Generate a scheme from --seed.")
    parser.add_argument("--seed", help="Seed hex for --scheme or --ramp.")
    parser.add_argument("--against", help="Background hex to measure a generated scheme against.")
    parser.add_argument("--ramp", type=int, metavar="STEPS", help="Build a perceptually even ramp of N steps from --seed.")
    parser.add_argument(
        "--share",
        nargs="+",
        metavar="ROLE=FRACTION",
        help="Measured share of visible area per role, e.g. bg=0.7 ink=0.1 accent=0.2. Supply this "
        "only from a layout you actually measured; without it the surface-area budget is skipped "
        "rather than assumed to pass.",
    )
    parser.add_argument(
        "--carries-meaning",
        nargs="+",
        metavar="ROLE+ROLE",
        help="Pairs where colour alone tells two states apart, e.g. accent+support. A "
        "colour-vision collapse on a declared pair is a failure; on any other pair it is reported "
        "for review, because SC 1.4.1 is broken by a use and this script cannot see the layout.",
    )
    parser.add_argument("--output")
    args = parser.parse_args()

    use_utf8_stdout()

    def parse_meaning() -> list[tuple[str, str]] | None:
        if not args.carries_meaning:
            return None
        out = []
        for item in args.carries_meaning:
            roles = [r.strip() for r in item.split("+") if r.strip()]
            if len(roles) != 2:
                raise ValueError(f"{item!r} is not ROLE+ROLE")
            out.append((roles[0], roles[1]))
        return out

    def parse_shares() -> dict[str, float] | None:
        if not args.share:
            return None
        out = {}
        for item in args.share:
            if "=" not in item:
                raise ValueError(f"{item!r} is not ROLE=FRACTION")
            role, _, value = item.partition("=")
            try:
                fraction = float(value)
            except ValueError:
                raise ValueError(f"{value!r} is not a number") from None
            if not 0.0 <= fraction <= 1.0:
                raise ValueError(f"share for {role.strip()!r} is {fraction}, not a fraction of 1")
            out[role.strip()] = fraction
        return out

    try:
        shares = parse_shares()
        meaning = parse_meaning()
        if (shares or meaning) and not (args.check or args.palette_id):
            raise ValueError("--share and --carries-meaning only apply to --check or --palette-id")
        if args.palette_id:
            payload = check_palette(load_palette_row(args.palette_id), shares, meaning)
            payload["palette_id"] = args.palette_id
        elif args.check:
            colours = {}
            for item in args.check:
                if "=" not in item:
                    raise ValueError(f"{item!r} is not ROLE=HEX")
                role, _, value = item.partition("=")
                parse_hex(value)
                colours[role.strip()] = value.strip()
            payload = check_palette(colours, shares, meaning)
        elif args.scheme:
            if not args.seed:
                raise ValueError("--scheme needs --seed")
            payload = build_scheme(args.seed, args.scheme, args.against)
        elif args.ramp:
            if not args.seed:
                raise ValueError("--ramp needs --seed")
            if args.ramp < 3:
                raise ValueError("a ramp needs at least 3 steps")
            ramp = build_ramp(args.seed, args.ramp)
            payload = {
                "seed": args.seed.upper(),
                "steps": ramp,
                "evenness": check_ramp_evenness(ramp),
            }
        else:
            parser.print_help()
            return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    emit_json(payload, args.output)
    # Exit 2 on a failed gate. Exit 3 when nothing failed but something needs a human decision,
    # which is the same convention plan_command_chain.py uses for a plan that is sound but not
    # runnable as printed. A skipped gate does not change the exit code at all: it is neither a
    # pass nor a breach, and making it exit non-zero would push callers toward inventing shares to
    # get a clean run, which is the one outcome this script exists to prevent.
    gates = payload.get("acceptance_gates", [])
    if any(g["status"] == "failed" for g in gates):
        return 2
    if payload.get("evenness", {}).get("status") == "failed":
        return 2
    if any(g["status"] == "review" for g in gates):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
