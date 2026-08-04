#!/usr/bin/env python3
"""Size the type on a poster or a banner from the distance it is read at, not from taste.

The word "poster" appears in sixteen references in this skill and nothing owned it. No table held a
trim size, no script computed anything, and the only guidance was a sentence about not reaching for
72px display type by reflex. So the actual question a poster asks - how much can this say - was
answered by eye, which is the same instrument that produces the Canva output the brief complains
about: a headline at a size that looked right on a laptop, on a sheet nobody will stand that close to.

There is one formula and it is not a matter of opinion. A letter's legibility is set by the angle it
subtends at the eye, so cap height and viewing distance are one quantity, and three bands on that
angle decide everything:

    5 arcmin    the acuity floor. A 20/20 eye resolves the letter and no more. This is where the
                Snellen chart's 6-metre line comes from, and 8.73 mm at 6 m is that line, so the
                arithmetic below is checkable against an optician's wall.
    20 arcmin   sustained reading. Where a person who has stopped walking can read a paragraph
                without effort.
    28.65 arcmin  the glance band. This is the sign trade's "one inch of letter height per ten feet"
                restated as an angle, which is what it always was.

A headline is read at a glance, from across a street, by somebody in motion. Support copy is read
after they have stopped, or not at all. Those are different bands, so this script sizes them
differently, and that single distinction is what most template output gets wrong: everything on the
sheet is scaled from the canvas instead of from the reader.

Screens need no metres. The CSS reference pixel is *defined* as the angle of one pixel on a 96 dpi
display at arm's length, which fixes 1 px at 1.279 arcmin whatever device renders it. So a display
banner's arithmetic is the same arithmetic in another unit, and it lands somewhere useful: the
browser's default 16 px body size is a cap height of about 15 arcmin, just under the sustained-reading
band, which is why 16 px reads as a floor rather than as a comfortable size.

What the script then does is the part a calculator does not: it measures the actual headline against
the actual measure. `advance` and `CAP` are imported from `render_mockup.py` rather than restated,
because two copies of a font metric drift and the renderer is the thing that will draw this. A
headline that needs three lines at glance size on a 320 x 50 banner is not a design problem to be
solved with a tighter font. There is no font. The arithmetic says so before anybody opens an editor.

What it will not do: judge whether the headline is any good (`check_specificity.py`), decide whether
the claim is legal (`check_claims.py`), pick the colours (`plan_palette.py`, and
`sample_reference.py` when the type sits on a photograph), or tell you whether you may hang the thing
in the street. That last one is a researched gap and `references/poster-and-banner.md` says so.

Everything is stdlib. No key, no network, no image provider.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402
from render_mockup import CAP, advance  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
FORMATS_TABLE = DATA / "poster-formats.csv"

# One arcminute in radians. Every threshold below is an angle, so this is the only conversion.
ARCMIN = math.pi / 10800

# The sign trade does not speak in arcminutes. It speaks in the Legibility Index: feet of legible
# distance per inch of cap height. It is the same axis inverted, and the conversion is exact.
# cap / distance = (1/12) / LI radians, so arcmin = (10800/pi) / (12 x LI) = 286.4789 / LI.
# Carrying both means one formula can answer an optician, a print shop and a billboard vendor
# without any of them being told they are using somebody else's unit. `--self-check` pins it.
LI_ARCMIN = (10800.0 / math.pi) / 12.0

# The three bands, in arcminutes of cap height, each one point on that axis.
#
# ACUITY 5' is the Snellen 20/20 optotype, 5 arcmin overall by definition - LI 57. It is a floor
# and not a target: resolving a letter is not reading a word, and no published sign rule sets type
# anywhere near this small.
#
# SUSTAINED 20' is continuous comfortable reading, and it is the one band with a standards citation.
# ISO 9241-3:1992 clause 5.4: "Character heights subtending from 20' to 22' are preferred for most
# tasks. The minimum character height shall be 16'." Read from the clause text of the BS EN
# adoption on 2026-08-04, not from ISO, whose own text is paywalled. Two honest caveats: it is a
# visual-display-terminal standard, and it was withdrawn in 2008. So this is a screen preference
# borrowed for print, which is more than the band had before and less than a print law.
#
# GLANCE 28.65' is the sign trade's "one inch of cap height per ten feet", which is exactly LI 10.
# Every published rule is one point on this same axis, and sorted by how much type they demand the
# ladder runs (a smaller LI is a bigger letter for the same distance):
#   ADA 2010 Table 703.5.5 slope, +1/8 inch per foot          LI 8        35.8'
#   ADA 2010 Table 703.5.5 base, 5/8 inch at 72 inches        LI 9.6      29.8'
#   ---- the glance band ----                                 LI 10       28.65'
#   United States Sign Council measured, Bertucci 2006 Tab. 1 LI 20-38  7.5-14.3'
#   OAAA OOH Creative Best Practices p.28, distance/font table LI 25      11.5'
#   USSC simplified default, its own text calls it "an average only" LI 30 9.5'
#   MUTCD/FHWA non-Interstate rule of thumb, 1 inch per 40 feet LI 40      7.2'
#   Snellen 20/20 optotype, the acuity floor above            LI 57        5.0'
# Note what the top of that ladder is: the ADA slope is a cap-to-distance ratio of 1:96, which is
# LI 8, not LI 96 - the inches-to-inches ratio and the feet-per-inch index differ by the factor 12,
# and conflating them puts an accessibility floor at 3' where nothing can be read. So the glance band
# is not the strictest rule here; it sits 4% below the ADA base point and roughly a factor of two
# above every commercial sign table. Two caveats on the ADA rows: it is US accessibility law with no
# force in Vietnam, and it is written for a low-vision reader at close range reading a room sign, not
# for a banner. That an accessibility statute and the sign trade's oldest rule of thumb land within
# 4% of each other from unrelated directions is the reason to trust the number at all.
# LI 10 is also research-backed for one case, and it is the case this skill is usually in. USSC
# measured that a sign read side-on, from a scooter or a car, needs about three times the cap height a
# viewer facing it needs; dividing the measured perpendicular band by three gives LI 6.7 to 12.7, and
# LI 10 sits inside that. A banner strung across a street is read side-on. A poster on a wall you
# walk up to is not, so an A2 sheet at glance size is generous by roughly a factor of two - which is
# why the run prints the LI next to the angle instead of hiding it.
ACUITY_ARCMIN = 5.0
SUSTAINED_ARCMIN = 20.0
GLANCE_ARCMIN = 28.65

# How many words a reader in motion gets through. The only sourced ceiling: the Outdoor Advertising
# Association of America's own creative guide states "7 words or less is a proven benchmark" (OOH
# Creative Best Practices, p.27), and the USSC legibility table above is only valid under its own
# stated condition of six words or thirty letters. An independent check from reading research lands
# in the same place - Brysbaert's meta-analysis of 190 studies and 18,573 participants puts adult
# silent reading of non-fiction at 238 wpm, most adults between 175 and 300.
# https://doi.org/10.1016/j.jml.2019.104047 - read 2026-08-04
# 238 wpm is 3.97 words a second, so a two-second glance buys about eight words and a slow reader
# about six. A trade association and a reading-research meta-analysis agreeing to within one word
# from opposite directions is the strongest thing in this file. Both measured a viewer in a vehicle
# or a fixated reader of prose, neither measured Vietnamese, and neither measured a pedestrian - so
# the gate fails a rider or a driver, reviews a walker or a scroller, and is skipped for a reader
# who has stopped, keyed off the viewer_motion column rather than off a guess.
GLANCE_WORD_CEILING = 7
MOTION_FAILS = ("riding", "driving")
MOTION_REVIEWS = ("walking", "scrolling")

# CSS 2.1 defines the reference pixel as the visual angle of one pixel on a 96 dpi device held at
# arm's length, taken as 28 inches. So one CSS pixel is a fixed angle by specification, and a
# banner needs no viewing distance supplied: the unit already carries one.
CSS_PX_ARCMIN = ((1.0 / 96.0) / 28.0) / ARCMIN

# Every physical format in the table is an ISO 216 sheet or a trade size. The ISO rows are
# checkable: the series is defined by a root sheet and repeated halving across the long side, so a
# typo in one dimension breaks the ratio. Tolerance is 1.5 mm because ISO 216 itself rounds each
# size down to whole millimetres, which walks the ratio slightly at every step.
ISO_ROOTS = {"a": (841.0, 1189.0), "b": (1000.0, 1414.0)}
ISO_TOLERANCE_MM = 1.5

# The only hard published numbers on how much text an image model will set correctly, from Google's
# own Imagen prompt guide: "Limit text to 25 characters or less for optimal generation" and
# "Avoid exceeding three phrases for cleaner compositions."
# https://cloud.google.com/vertex-ai/generative-ai/docs/image/img-gen-prompt-guide - fetched 2026-08-04
# They are a vendor's advice about a vendor's model, not a law of typography, which is why --generated
# returns review rather than failed: the answer is to composite the type, not to shorten the sentence.
GENERATED_CHAR_CEILING = 25
GENERATED_BLOCK_CEILING = 3


def cap_height(arcmin: float, unit: str, distance_m: float | None) -> float:
    """The cap height that subtends `arcmin` at the reader's eye, in the format's own unit."""
    if unit == "css-px":
        return arcmin / CSS_PX_ARCMIN
    if distance_m is None:
        raise ValueError("a physical format needs a viewing distance in metres")
    return distance_m * 1000.0 * arcmin * ARCMIN


def legibility_index(arcmin: float) -> float:
    """The same threshold as the sign trade states it: feet of legible distance per inch of cap."""
    return LI_ARCMIN / arcmin


def font_size(cap: float) -> float:
    """The type size that produces a given cap height, using the renderer's own metric."""
    return cap / CAP


def fit_lines(text: str, size: float, measure: float, bold: bool = True) -> list[str] | None:
    """Greedy wrap to `measure`, or None when one word alone is wider than the measure.

    `wrap` in render_mockup.py raises instead of returning, because a mockup that silently drops a
    clause looks finished. Here not fitting is the answer being asked for, so it returns.
    """
    words = str(text).split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    if advance(current, size, bold) > measure:
        return None
    for word in words[1:]:
        if advance(f"{current} {word}", size, bold) <= measure:
            current = f"{current} {word}"
        else:
            if advance(word, size, bold) > measure:
                return None
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def largest_size_that_fits(text: str, measure: float, max_lines: int, ceiling: float) -> float:
    """The biggest type size at which `text` fits `max_lines` of `measure`. Bisection, 40 steps."""
    low, high = 0.01, max(ceiling, 0.02)
    fitted = fit_lines(text, low, measure)
    if fitted is None or len(fitted) > max_lines:
        return 0.0
    for _ in range(40):
        mid = (low + high) / 2.0
        lines = fit_lines(text, mid, measure)
        if lines is not None and len(lines) <= max_lines:
            low = mid
        else:
            high = mid
    return low


class Formats:
    def __init__(self, path: Path = FORMATS_TABLE) -> None:
        with path.open(encoding="utf-8", newline="") as handle:
            self.rows = list(csv.DictReader(handle))
        self.by_id = {row["format_id"]: row for row in self.rows}

    def numeric(self, row: dict, field: str) -> float | None:
        value = (row.get(field) or "").strip()
        try:
            return float(value)
        except ValueError:
            return None


def band_of(arcmin: float) -> str:
    if arcmin >= GLANCE_ARCMIN:
        return "glance"
    if arcmin >= SUSTAINED_ARCMIN:
        return "sustained"
    if arcmin >= ACUITY_ARCMIN:
        return "acuity-floor"
    return "below-acuity"


def report(formats: Formats, format_id: str, distance_m: float | None, headline: str,
           support: list[str], max_lines: int, generated: bool = False) -> dict:
    row = formats.by_id[format_id]
    unit = row["unit"]
    width = formats.numeric(row, "size_w")
    height = formats.numeric(row, "size_h")
    margin = formats.numeric(row, "safe_margin_mm")

    payload: dict = {
        "format": {
            "format_id": format_id,
            "label": row["label"],
            "family": row["family"],
            "unit": unit,
            "size_w": row["size_w"],
            "size_h": row["size_h"],
            "size_grade": row["size_grade"],
            "what_it_does_not_tell_you": row["what_it_does_not_tell_you"],
        },
        "gates": [],
        "verdict": {"status": "passed", "why": []},
    }

    def fail(status: str, why: str) -> None:
        order = {"passed": 0, "review": 1, "failed": 2}
        current = payload["verdict"]["status"]
        if order[status] > order[current]:
            payload["verdict"]["status"] = status
        payload["verdict"]["why"].append(why)

    if width is None or height is None or margin is None:
        payload["gates"].append({
            "gate": "format-has-a-size",
            "status": "failed",
            "detail": f"{format_id} carries {row['size_grade']} instead of dimensions. "
                      f"{row['size_source']}",
        })
        fail("failed", "the format has no dimensions in this table, so nothing can be computed")
        return payload

    if unit == "css-px":
        if distance_m is not None:
            payload["gates"].append({
                "gate": "distance-belongs-to-the-unit",
                "status": "failed",
                "detail": "a CSS pixel is defined as an angle, so a screen format already carries "
                          "its viewing distance. Passing --distance would apply it twice",
            })
            fail("failed", "--distance is meaningless on a screen format")
            return payload
        distance_note = (f"none needed: 1 css-px = {CSS_PX_ARCMIN:.3f} arcmin by specification")
    else:
        if distance_m is None:
            distance_m = formats.numeric(row, "view_distance")
            if distance_m is None:
                payload["gates"].append({
                    "gate": "format-has-a-distance",
                    "status": "failed",
                    "detail": f"{format_id} declares '{row['view_distance']}' for viewing distance. "
                              f"Measure the place and pass --distance",
                })
                fail("failed", "no viewing distance, measured or declared")
                return payload
            distance_note = (f"{distance_m} m taken from the table, graded "
                             f"{row['distance_grade']} - it is an assumption about the place, "
                             f"not a fact about the format")
        else:
            distance_note = f"{distance_m} m supplied by --distance"

    measure = width - 2.0 * margin
    payload["reader"] = {
        "distance": distance_note,
        "measure": round(measure, 2),
        "safe_margin": margin,
        "bands_as_cap_height": {
            name: round(cap_height(arcmin, unit, distance_m), 2)
            for name, arcmin in (("acuity-floor", ACUITY_ARCMIN),
                                 ("sustained", SUSTAINED_ARCMIN),
                                 ("glance", GLANCE_ARCMIN))
        },
        "bands_as_type_size": {
            name: round(font_size(cap_height(arcmin, unit, distance_m)), 2)
            for name, arcmin in (("acuity-floor", ACUITY_ARCMIN),
                                 ("sustained", SUSTAINED_ARCMIN),
                                 ("glance", GLANCE_ARCMIN))
        },
        "bands_as_legibility_index": {
            name: round(legibility_index(arcmin), 1)
            for name, arcmin in (("acuity-floor", ACUITY_ARCMIN),
                                 ("sustained", SUSTAINED_ARCMIN),
                                 ("glance", GLANCE_ARCMIN))
        },
    }

    glance_size = font_size(cap_height(GLANCE_ARCMIN, unit, distance_m))
    payload["reader"]["indicative_chars_per_line_at_glance"] = int(
        measure // advance("n", glance_size, True)) if advance("n", glance_size, True) else 0

    # The headline. Sized at the glance band, because it is read by somebody who has not stopped.
    fitted = fit_lines(headline, glance_size, measure)
    biggest = largest_size_that_fits(headline, measure, max_lines, glance_size * 4.0)
    achieved_arcmin = (biggest * CAP) * (CSS_PX_ARCMIN if unit == "css-px"
                                         else 1.0 / (distance_m * 1000.0 * ARCMIN))
    if fitted is not None and len(fitted) <= max_lines:
        payload["gates"].append({
            "gate": "headline-reads-at-a-glance",
            "status": "passed",
            "detail": f"fits {len(fitted)} of {max_lines} allowed lines at glance size "
                      f"{glance_size:.1f} {unit}",
            "lines": fitted,
        })
    else:
        shown = len(fitted) if fitted is not None else "one word wider than the measure"
        band = band_of(achieved_arcmin)
        status = "review" if band in ("glance", "sustained") else "failed"
        payload["gates"].append({
            "gate": "headline-reads-at-a-glance",
            "status": status,
            "detail": f"needs {shown} lines at glance size {glance_size:.1f} {unit}. The largest "
                      f"size that fits {max_lines} line(s) is {biggest:.1f} {unit}, a cap height of "
                      f"{achieved_arcmin:.1f} arcmin, which is the {band} band",
            "lines": fit_lines(headline, biggest, measure) if biggest else None,
        })
        if status == "failed":
            fail("failed", f"the headline only fits by dropping to {achieved_arcmin:.1f} arcmin, "
                           f"below the {SUSTAINED_ARCMIN:.0f} arcmin a stopped reader needs. Cut "
                           f"words, do not cut type")
        else:
            fail("review", f"the headline fits at {achieved_arcmin:.1f} arcmin, readable to "
                           f"somebody standing still but not at a glance. Either it is not the "
                           f"headline or the reader is closer than declared")

    # How many words, not how big. Legible and read are different questions, and this is the second
    # one: a rider passing a banner has a couple of seconds whether or not the type is right.
    motion = (row.get("viewer_motion") or "").strip()
    words = len(str(headline).split())
    if motion in MOTION_FAILS or motion in MOTION_REVIEWS:
        over = words > GLANCE_WORD_CEILING
        status = "passed"
        if over:
            status = "failed" if motion in MOTION_FAILS else "review"
        payload["gates"].append({
            "gate": "the-headline-is-short-enough-to-finish",
            "status": status,
            "detail": (f"{words} words for a reader {motion}, inside the {GLANCE_WORD_CEILING} the "
                       f"OAAA publishes and the ~8 a 238 wpm reader gets through in two seconds"
                       if not over else
                       f"{words} words for a reader {motion}, past the {GLANCE_WORD_CEILING} the "
                       f"OAAA calls a proven benchmark and past the ~8 a 238 wpm reader finishes in "
                       f"two seconds. The measured sources cover motorists, so this is "
                       f"{'a failure' if motion in MOTION_FAILS else 'a review, not a verdict'}"),
        })
        if over and motion in MOTION_FAILS:
            fail("failed", f"{words} words cannot be finished at {motion} speed. This is not a type "
                           f"problem and no size fixes it")
        elif over:
            fail("review", f"{words} words is past the OOH benchmark, but the benchmark was measured "
                           f"on motorists and this reader is {motion}. Decide, do not assume")
    else:
        payload["gates"].append({
            "gate": "the-headline-is-short-enough-to-finish",
            "status": "skipped",
            "detail": f"the reader is {motion or 'not declared as moving'}, and neither the OAAA "
                      f"benchmark nor the USSC condition was measured on a reader who has stopped. "
                      f"{words} words is recorded, not judged",
        })

    # Support copy. Sized at the sustained band: it is read after the reader has stopped, or never.
    if support:
        sustained_size = font_size(cap_height(SUSTAINED_ARCMIN, unit, distance_m))
        overflow = []
        for line in support:
            lines = fit_lines(line, sustained_size, measure, bold=False)
            if lines is None or len(lines) > 2:
                overflow.append(line if lines is None else f"{line} ({len(lines)} lines)")
        payload["gates"].append({
            "gate": "support-copy-reads-when-they-stop",
            "status": "passed" if not overflow else "review",
            "detail": (f"{len(support)} line(s) at sustained size {sustained_size:.1f} {unit}"
                       if not overflow else
                       f"these need more than two lines at sustained size "
                       f"{sustained_size:.1f} {unit}: {'; '.join(overflow)}"),
        })
        if overflow:
            fail("review", "support copy overflows at the size a stopped reader needs")

        # The vertical check: everything stacked, against the canvas.
        stack = font_size(cap_height(GLANCE_ARCMIN, unit, distance_m)) * 1.24 * max(
            1, len(fitted) if fitted else max_lines)
        stack += sustained_size * 1.24 * len(support)
        room = height - 2.0 * margin
        payload["gates"].append({
            "gate": "the-stack-fits-the-sheet",
            "status": "passed" if stack <= room else "failed",
            "detail": f"headline plus support needs {stack:.0f} of {room:.0f} {unit} of height "
                      f"inside the safe area",
        })
        if stack > room:
            fail("failed", "the copy is taller than the sheet at the sizes the distance demands")

    # Only asked when the artwork is going to be generated with its type baked in. This is the gate
    # that saves a generation run rather than judging one after the fact.
    if generated:
        blocks = [headline] + list(support)
        too_long = [b for b in blocks if len(b) > GENERATED_CHAR_CEILING]
        breaches = []
        if too_long:
            breaches.append(f"{len(too_long)} block(s) exceed {GENERATED_CHAR_CEILING} characters: "
                            + "; ".join(f"'{b}' ({len(b)})" for b in too_long))
        if len(blocks) > GENERATED_BLOCK_CEILING:
            breaches.append(f"{len(blocks)} text blocks against a ceiling of "
                            f"{GENERATED_BLOCK_CEILING}")
        payload["gates"].append({
            "gate": "native-text-is-within-the-generators-own-limit",
            "status": "passed" if not breaches else "review",
            "detail": (f"{len(blocks)} block(s), longest {max(len(b) for b in blocks)} characters, "
                       f"inside the published ceiling"
                       if not breaches else
                       ". ".join(breaches) + ". Set this type in render_mockup.py and composite it "
                       "over the generated artwork, or generate the plate wordless and add the "
                       "words. Do not shorten the sentence to suit the model"),
        })
        if breaches:
            fail("review", "the copy is past the ceiling the image provider publishes for native "
                           "text, so the type belongs in a compositing step, not in the prompt")

    if not payload["verdict"]["why"]:
        payload["verdict"]["why"].append(
            "every element is at or above the band its reader needs")
    return payload


def as_text(payload: dict) -> str:
    fmt = payload["format"]
    out = [f"POSTER PLAN - {fmt['label']} ({fmt['format_id']})",
           f"  size {fmt['size_w']} x {fmt['size_h']} {fmt['unit']}, "
           f"family {fmt['family']}, size grade {fmt['size_grade']}"]
    reader = payload.get("reader")
    if reader:
        out.append(f"  distance: {reader['distance']}")
        out.append(f"  measure: {reader['measure']} {fmt['unit']} "
                   f"(margin {reader['safe_margin']})")
        out.append("  cap height needed / type size / the same threshold as an LI:")
        for band, cap in reader["bands_as_cap_height"].items():
            out.append(f"    {band:<13} {cap:>8.2f} cap  ->  "
                       f"{reader['bands_as_type_size'][band]:>8.2f} type   "
                       f"LI {reader['bands_as_legibility_index'][band]:>5.1f}")
        out.append(f"  a glance-size line holds about "
                   f"{reader['indicative_chars_per_line_at_glance']} characters")
    out.append("")
    for gate in payload["gates"]:
        out.append(f"  [{gate['status'].upper()}] {gate['gate']}")
        out.append(f"      {gate['detail']}")
        for line in gate.get("lines") or []:
            out.append(f"      | {line}")
    out.append("")
    out.append(f"VERDICT {payload['verdict']['status'].upper()}")
    for why in payload["verdict"]["why"]:
        out.append(f"  - {why}")
    out.append("")
    out.append(f"  What this format cannot tell you: {fmt['what_it_does_not_tell_you']}")
    return "\n".join(out) + "\n"


def explain_units() -> str:
    return (
        "WHY A POSTER AND A BANNER USE ONE FORMULA\n\n"
        "A letter is legible by the angle it subtends, so cap height and viewing distance are one\n"
        "quantity. cap = distance * angle, with the angle in radians.\n\n"
        f"  1 arcmin = {ARCMIN:.9f} rad\n\n"
        "Three bands on that angle:\n"
        f"  acuity floor   {ACUITY_ARCMIN:>6.2f} arcmin   the Snellen 20/20 optotype\n"
        f"  sustained      {SUSTAINED_ARCMIN:>6.2f} arcmin   ISO 9241-3:1992 cl. 5.4, 20' to 22'\n"
        f"  glance         {GLANCE_ARCMIN:>6.2f} arcmin   one inch of letter per ten feet\n\n"
        "The sign trade states the same thresholds upside down, as a Legibility Index: feet of\n"
        f"legible distance per inch of cap height. arcmin = {LI_ARCMIN:.4f} / LI, exactly.\n"
        "Every published rule is one point on that single axis, and this file's glance band is the\n"
        "most demanding of them:\n"
        f"  LI {legibility_index(ACUITY_ARCMIN):>5.1f}   {ACUITY_ARCMIN:>5.2f} arcmin   "
        "Snellen acuity ceiling - a floor, not a rule\n"
        "  LI  96.0    2.98 arcmin   ADA 2010 cl. 703.5.5 slope, +1/8 in per foot: a legal floor\n"
        "  LI  40.0    7.16 arcmin   MUTCD/FHWA non-Interstate, its own text calls it a thumb rule\n"
        "  LI  30.0    9.55 arcmin   USSC simplified default, stated as an average that may fall\n"
        "                            short\n"
        "  LI 20-38  7.5-14.3       USSC measured, by typeface, colour pair and illumination\n"
        "  LI  25.0   11.46 arcmin   OAAA's own published distance/font table\n"
        f"  LI {legibility_index(GLANCE_ARCMIN):>5.1f}  {GLANCE_ARCMIN:>6.2f} arcmin   "
        "this file's glance band: the trade's 1 in per 10 ft\n\n"
        "That last one is research-backed for one case: USSC measured that a sign read side-on\n"
        "needs about three times the cap height a viewer facing it needs, which divides the\n"
        "measured band to LI 6.7-12.7. A street banner is read side-on. A poster you walk up to is\n"
        "not, so on a wall the glance band is generous by roughly two.\n\n"
        "Two anchors make it checkable rather than asserted, and --self-check runs both:\n"
        f"  6 m at the acuity floor is "
        f"{cap_height(ACUITY_ARCMIN, 'mm', 6.0):.2f} mm, which is the 6-metre line on an\n"
        "  optician's chart, 8.73 mm.\n"
        f"  3.048 m (ten feet) at the glance band is "
        f"{cap_height(GLANCE_ARCMIN, 'mm', 3.048):.2f} mm, which is one inch.\n\n"
        "A screen needs no metres. CSS 2.1 defines the reference pixel as the angle of one pixel\n"
        "on a 96 dpi display at arm's length (28 in), so one CSS pixel is\n"
        f"  {CSS_PX_ARCMIN:.4f} arcmin, by specification, on every device.\n"
        f"The browser default 16 px sets a cap height of {16 * CAP:.2f} px = "
        f"{16 * CAP * CSS_PX_ARCMIN:.2f} arcmin,\n"
        "just under the sustained band. That is why 16 px behaves as a floor and not as a\n"
        "comfortable size, and why a caption at 12 px is a decision to be unread.\n\n"
        f"Cap height to type size uses CAP = {CAP}, imported from render_mockup.py so the number\n"
        "that sizes the type is the number that draws it.\n"
    )


def self_check() -> tuple[str, int]:
    lines, failures = [], 0

    def check(name: str, got: float, want: float, tolerance: float, unit: str) -> None:
        nonlocal failures
        ok = abs(got - want) <= tolerance
        failures += 0 if ok else 1
        lines.append(f"  [{'ok' if ok else 'FAIL'}] {name}: {got:.4f} {unit} "
                     f"(expected {want} +/- {tolerance})")

    # The optician's wall. A 20/20 optotype at 6 m is 8.73 mm tall.
    check("Snellen 20/20 at 6 m", cap_height(ACUITY_ARCMIN, "mm", 6.0), 8.73, 0.01, "mm")
    # The sign trade's rule of thumb, restated.
    check("one inch per ten feet", cap_height(GLANCE_ARCMIN, "mm", 3.048), 25.4, 0.05, "mm")
    # Linear in distance: double the distance, double the letter.
    check("linearity at 20 m", cap_height(GLANCE_ARCMIN, "mm", 20.0),
          cap_height(GLANCE_ARCMIN, "mm", 10.0) * 2, 0.001, "mm")
    # The two axes are one axis. The acuity ceiling is LI 57 and the trade rule is LI 10, and both
    # fall out of the same conversion rather than being asserted beside each other.
    check("acuity floor as an LI", legibility_index(ACUITY_ARCMIN), 57.30, 0.01, "ft/in")
    check("glance band as an LI", legibility_index(GLANCE_ARCMIN), 10.0, 0.01, "ft/in")
    check("OAAA table as an angle", LI_ARCMIN / 25.0, 11.46, 0.01, "arcmin")
    # The CSS reference pixel, from the specification's own definition.
    check("css reference pixel", CSS_PX_ARCMIN, 1.2789, 0.0005, "arcmin")
    # The browser default lands just under sustained reading, which is the point of the band.
    check("16 css-px cap height", 16 * CAP * CSS_PX_ARCMIN, 15.14, 0.02, "arcmin")

    # ISO 216 is a definition, so every A and B row in the table is recomputable. The definition is
    # the 1:sqrt(2) ratio - it is what makes halving the long side reproduce the shape - so the two
    # roots are checked against it before anything is derived from them.
    for series, (short, long_) in ISO_ROOTS.items():
        check(f"ISO 216 {series.upper()} root is 1:sqrt(2)", long_ / short, math.sqrt(2.0),
              0.001, "ratio")

    formats = Formats()
    for row in formats.rows:
        if row["size_grade"] != "iso-216-definitional":
            continue
        series = row["format_id"][0]
        step = int(row["format_id"][1])
        # Halving n times across the long side: the new short side is the old long side halved and
        # the new long side is the old short side. The rounding compounds, hence the tolerance.
        w, h = ISO_ROOTS[series]
        for _ in range(step):
            w, h = h / 2.0, w
        got_w, got_h = float(row["size_w"]), float(row["size_h"])
        ok = abs(got_w - w) <= ISO_TOLERANCE_MM and abs(got_h - h) <= ISO_TOLERANCE_MM
        failures += 0 if ok else 1
        lines.append(f"  [{'ok' if ok else 'FAIL'}] {row['format_id']} from the ISO 216 "
                     f"{series.upper()} root: {got_w:.0f} x {got_h:.0f} against "
                     f"{w:.1f} x {h:.1f} mm")

    head = ("SELF-CHECK - the arithmetic against an optician's chart, the sign trade's own index, "
            "the\nCSS specification and the ISO 216 definition\n")
    tail = (f"\n{len(lines)} checks, {failures} failed\n")
    return head + "\n".join(lines) + tail, (2 if failures else 0)


def list_formats(formats: Formats) -> str:
    out = ["FORMATS in data/poster-formats.csv", ""]
    family = None
    for row in formats.rows:
        if row["family"] != family:
            family = row["family"]
            out.append(f"  {family}")
        size = f"{row['size_w']} x {row['size_h']} {row['unit']}"
        out.append(f"    {row['format_id']:<22} {size:<24} {row['label']}")
        allowance = (row.get("edge_allowance_mm") or "0").strip()
        if allowance not in ("0", "not-applicable"):
            out.append(f"      material the shop consumes: {allowance} mm every side, outside the "
                       f"visible area. Not bleed, and nothing may be inside it")
        if row["size_grade"] != "iso-216-definitional":
            out.append(f"      size grade: {row['size_grade']}")
    out.append("")
    out.append("  A size grade other than iso-216-definitional means the number is a trade")
    out.append("  convention or a vendor's to declare. Confirm it on the quote before designing.")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="Size poster and banner type from the distance it is read at.")
    parser.add_argument("--format", help="a format_id from data/poster-formats.csv")
    parser.add_argument("--distance", type=float,
                        help="viewing distance in metres, measured at the place. Overrides the "
                             "table's declared assumption. Not accepted for screen formats")
    parser.add_argument("--headline", help="the line that has to work at a glance")
    parser.add_argument("--support", action="append", default=[],
                        help="a line read after the reader stops. Repeatable")
    parser.add_argument("--max-lines", type=int, default=2,
                        help="lines the headline may occupy (default 2)")
    parser.add_argument("--generated", action="store_true",
                        help="the artwork will be image-generated with this type baked in. Adds the "
                             "gate for the provider's published native-text ceiling")
    parser.add_argument("--list-formats", action="store_true")
    parser.add_argument("--explain-units", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--format-out", dest="fmt", choices=("text", "json"), default="text")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    if args.self_check:
        text, code = self_check()
        emit(text, args.output)
        return code
    if args.explain_units:
        emit(explain_units(), args.output)
        return 0

    formats = Formats()
    if args.list_formats:
        emit(list_formats(formats), args.output)
        return 0

    if not args.format:
        parser.error("--format is required. Run --list-formats")
    if args.format not in formats.by_id:
        parser.error(f"no such format: {args.format}. Run --list-formats")
    if not args.headline:
        parser.error("--headline is required: the gate is whether the headline reads at distance")
    if args.max_lines < 1:
        parser.error("--max-lines must be at least 1")
    if args.distance is not None and args.distance <= 0:
        parser.error("--distance must be positive")

    payload = report(formats, args.format, args.distance, args.headline, args.support,
                     args.max_lines, args.generated)
    if args.fmt == "json":
        emit_json(payload, args.output)
    else:
        emit(as_text(payload), args.output)
    return {"passed": 0, "failed": 2, "review": 3}[payload["verdict"]["status"]]


if __name__ == "__main__":
    sys.exit(main())
