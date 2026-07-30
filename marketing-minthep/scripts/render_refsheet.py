#!/usr/bin/env python3
"""Draw the reference sheets a non-marketer actually needs, as real SVG, with no API key.

A skill that only writes prose about lighting asks the reader to hold a diagram in their head. So
these five sheets are the diagram. Every number printed on them is computed from the same data
tables the rest of the skill reads, which means a sheet cannot drift away from the advice: change
`data/layout-dials.csv` and the dial sheet changes with it.

  lighting   A plan view of six setups, seen from above, with the shadow each one throws.
  frames     Every placement at its real proportion, with the reserved copy area and the bands the
             platform's own interface covers, shaded.
  palettes   Every palette as a card, with its measured contrast ratio printed on it.
  dials      One layout drawn three times — at the minimum, the default and the maximum of a single
             dial — so the reader sees what the number does instead of reading what it does.
  reference  The same borrowed picture drawn twice: once as the parts that belong to somebody, once
             as the geometry that belongs to nobody, then a verdict on each of eleven axes.

The dial sheet is the one that answers "cơ chế bố cục": the mechanism is a small set of numbers,
and the only honest way to explain a number is to show the same thing twice with it changed. The
reference sheet answers the question underneath every "make it like this": which half of the
picture you were handed is actually available to you.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, use_utf8_stdout  # noqa: E402
from find_recipe import PHI, ratio_lines  # noqa: E402
from render_mockup import CAP, LEAD, advance, wrap  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"


def _table(name: str) -> list[dict[str, str]]:
    """Read a data table without leaving the handle open — these run inside a test process too."""
    return list(csv.DictReader(io.StringIO((DATA / name).read_text(encoding="utf-8"))))


PAPER = "#F5F1E8"
INK = "#141414"
COBALT = "#2A4BD7"
ORANGE = "#D9541E"
MUTED = "#8A8478"

FAMILY = "Helvetica Neue, Helvetica, Arial, sans-serif"

# Each setup is (label, why, [(x, y, kind, note)], shadow_angle_degrees). Positions are in a
# unit square with the subject at (0.5, 0.5) and the camera at the bottom edge, which is how a
# lighting plan is drawn on set. The shadow angle is derived from the key position rather than
# chosen, so a sheet cannot show a shadow that disagrees with its own key light — the single most
# common failure in generated imagery, and it would be absurd to reproduce it in the diagram.
SETUPS = [
    (
        "45/45 soft key",
        "The default for a packshot, a founder portrait, and most food. One decision, hard to get wrong.",
        [(0.18, 0.26, "soft", "Large soft source, front-left, 45° around and 30° up"),
         (0.86, 0.42, "bounce", "White bounce, right, one to two stops down")],
    ),
    (
        "Window and bounce",
        "What a shop already has. Costs nothing and reads as a real place rather than a set.",
        [(0.06, 0.50, "window", "The actual window, side-on to the subject"),
         (0.90, 0.55, "bounce", "Anything white opposite it — a wall, a menu, a shirt")],
    ),
    (
        "Raking side light",
        "Texture is the product: bread crumb, fabric weave, a swatch, a worn leather.",
        [(0.04, 0.60, "hard", "Hard-ish source almost parallel to the surface"),
         (0.94, 0.60, "flag", "Black flag opposite, so the shadows stay deep")],
    ),
    (
        "Backlight for translucency",
        "Anything light passes through: broth, tea, a cold drink, honey, a thin fabric.",
        [(0.50, 0.06, "hard", "Source three-quarters behind, slightly off centre"),
         (0.50, 0.92, "bounce", "Low front bounce so the near face is not black")],
    ),
    (
        "Strip for glass",
        "One long highlight down a bottle. Two highlights is what makes glass look rendered.",
        [(0.22, 0.16, "strip", "Narrow tall soft strip, behind-left"),
         (0.82, 0.40, "flag", "Black card right — no second highlight, ever")],
    ),
    (
        "Overhead butterfly",
        "Beauty and makeup, where the makeup is the subject and the shape must stay even.",
        [(0.50, 0.14, "soft", "Large soft source directly above and slightly front"),
         (0.50, 0.86, "bounce", "Bounce under the chin"),
         (0.08, 0.50, "flag", "Black cards both sides for shape"),
         (0.92, 0.50, "flag", "")],
    ),
]

# name, width, height, top band, bottom band, band note, reserve rect as fractions of the usable
# area (x, y, w, h) or None, why it exists. The reserve is given as an explicit rectangle rather
# than a word like "upper third" that a lookup then has to interpret — the first version keyed a
# dict on that word, which is a second place for the two to disagree.
PLACEMENTS = [
    ("Feed square", 1080, 1080, 0, 0, "",
     None, "Marketplace tiles, and the one ratio every channel accepts. No reserve: the platform "
     "prints the title and price under the tile, not on it, so type on the image duplicates it"),
    ("Feed portrait", 1080, 1350, 0, 0, "",
     (0.0, 0.0, 1.0, 0.34), "The largest area a feed will give you, so the headline can be large"),
    ("Story / Reel", 1080, 1920, 250, 420, "App draws its own interface over 250px top, 420px bottom",
     (0.0, 0.0, 1.0, 1.0), "Everything must live between the bands. This is why a story is laid "
     "out again rather than cropped from the feed post"),
    ("Landscape", 1920, 1080, 0, 0, "",
     (0.0, 0.0, 0.36, 1.0), "Video, web hero, presentation. Type goes to one side because the "
     "subject cannot be centred and covered at once"),
    ("Print A4 menu", 1240, 1754, 60, 60, "Trim margin 60px — a print shop cuts into this",
     (0.0, 0.0, 1.0, 0.16), "Nothing that must survive can enter the grey. Screens forgive an "
     "edge; a guillotine does not"),
]


def _text(x: float, y: float, content: str, size: float, *, fill: str = INK, bold: bool = False,
          anchor: str = "start", family: str = FAMILY) -> str:
    weight = ' font-weight="700"' if bold else ""
    anchored = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (
        f'<text x="{x:.0f}" y="{y:.0f}" font-family="{family}" font-size="{size:.1f}"'
        f' fill="{fill}"{weight}{anchored}>{html.escape(content)}</text>'
    )


def _block(x: float, y: float, content: str, size: float, width: float, field: str,
           *, fill: str = INK, max_lines: int = 6) -> tuple[str, float]:
    """Wrap a paragraph inside a measured width and report where the block ended.

    Returns the markup and the y of the next free baseline, so a caller stacks blocks instead of
    guessing at gaps. Everything on these sheets is stacked this way; nothing is placed at a
    fraction of the canvas height.
    """
    lines = wrap(content, size, width, max_lines, field)
    step = size * LEAD
    spans = "".join(
        f'<tspan x="{x:.0f}" dy="{0 if index == 0 else step:.0f}">{html.escape(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    markup = (
        f'<text x="{x:.0f}" y="{y:.0f}" font-family="{FAMILY}" font-size="{size:.1f}"'
        f' fill="{fill}">{spans}</text>'
    )
    return markup, y + step * (len(lines) - 1) + size * LEAD


def _header(title: str, subtitle: str, width: float, margin: float,
            *, max_lines: int = 3) -> tuple[str, float]:
    parts = [_text(margin, margin + 34, title, 38, bold=True)]
    body, cursor = _block(margin, margin + 34 + 46, subtitle, 17, width - margin * 2, "subtitle",
                          fill=MUTED, max_lines=max_lines)
    parts.append(body)
    parts.append(f'<rect x="{margin}" y="{cursor + 6:.0f}" width="{width - margin * 2:.0f}" height="2" fill="{INK}"/>')
    return "".join(parts), cursor + 34


def _open(width: float, height: float) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}"'
        f' viewBox="0 0 {width:.0f} {height:.0f}">'
        f'<rect width="{width:.0f}" height="{height:.0f}" fill="{PAPER}"/>'
    )


def sheet_lighting() -> str:
    """Six plan views. The shadow is drawn opposite the key, computed, not decided."""
    width, margin, gap = 1400, 60, 30
    cell = (width - margin * 2 - gap * 2) / 3
    plan = cell * 0.62
    head, cursor = _header(
        "Lighting plans, seen from above",
        "The camera is the triangle below each square and the subject is the black disc in the "
        "middle. Blue is the key — the one light that decides the picture. Orange is fill or "
        "bounce. Black bars are flags, which take light away. The grey wedge is the shadow, drawn "
        "from the key position, so it always agrees with the light. Pick one setup and name it in "
        "the brief; a named source is what lets you reject a highlight later.",
        width, margin, max_lines=5,
    )
    parts = [head]
    rows = (len(SETUPS) + 2) // 3
    row_h = plan + 210
    for index, (label, why, lights) in enumerate(SETUPS):
        col, row = index % 3, index // 3
        ox = margin + col * (cell + gap)
        oy = cursor + row * row_h
        # The plan square.
        parts.append(f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{plan:.0f}" height="{plan:.0f}" fill="#EFE9DE"/>')
        cx, cy = ox + plan / 2, oy + plan / 2
        key = lights[0]
        kx, ky = ox + key[0] * plan, oy + key[1] * plan
        # Shadow falls directly away from the key, at a length that reads at this scale.
        dx, dy = cx - kx, cy - ky
        length = (dx * dx + dy * dy) ** 0.5 or 1.0
        sx, sy = cx + dx / length * plan * 0.30, cy + dy / length * plan * 0.30
        spread = plan * 0.085
        px, py = -dy / length * spread, dx / length * spread
        parts.append(
            f'<path d="M{cx + px:.1f},{cy + py:.1f} L{sx + px * 1.5:.1f},{sy + py * 1.5:.1f} '
            f'L{sx - px * 1.5:.1f},{sy - py * 1.5:.1f} L{cx - px:.1f},{cy - py:.1f} Z" '
            f'fill="{MUTED}" opacity="0.38"/>'
        )
        parts.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{plan * 0.075:.0f}" fill="{INK}"/>')
        # The camera marker sits outside the square. Inside it, a bounce placed low in the plan
        # landed on top of the word "camera" — twice, on the backlight and butterfly setups.
        tip = oy + plan
        parts.append(
            f'<path d="M{cx - 11:.0f},{tip + 16:.0f} L{cx + 11:.0f},{tip + 16:.0f} '
            f'L{cx:.0f},{tip + 3:.0f} Z" fill="{INK}"/>'
        )
        parts.append(_text(cx + 18, tip + 16, "camera", 12, fill=MUTED))
        for order, (lx, ly, kind, _note) in enumerate(lights):
            px_, py_ = ox + lx * plan, oy + ly * plan
            size = plan * (0.11 if kind in ("soft", "window") else 0.07)
            colour = COBALT if order == 0 else (INK if kind == "flag" else ORANGE)
            if kind == "strip":
                parts.append(f'<rect x="{px_ - size * 0.28:.0f}" y="{py_ - size:.0f}" '
                             f'width="{size * 0.56:.0f}" height="{size * 2:.0f}" fill="{colour}"/>')
            elif kind == "flag":
                parts.append(f'<rect x="{px_ - size * 0.9:.0f}" y="{py_ - size * 0.22:.0f}" '
                             f'width="{size * 1.8:.0f}" height="{size * 0.44:.0f}" fill="{colour}"/>')
            else:
                parts.append(f'<circle cx="{px_:.0f}" cy="{py_:.0f}" r="{size:.0f}" fill="{colour}"/>')
            if order == 0:
                parts.append(f'<line x1="{px_:.0f}" y1="{py_:.0f}" x2="{cx:.0f}" y2="{cy:.0f}" '
                             f'stroke="{COBALT}" stroke-width="2" stroke-dasharray="7 6"/>')
        text_y = oy + plan + 52
        parts.append(_text(ox, text_y, label, 21, bold=True))
        body, text_y = _block(ox, text_y + 26, why, 14, cell, "why", fill=MUTED, max_lines=3)
        parts.append(body)
        for _lx, _ly, _kind, note in lights:
            if not note:
                continue
            body, text_y = _block(ox, text_y + 4, f"— {note}", 13, cell, "note", max_lines=3)
            parts.append(body)
    height = cursor + rows * row_h + margin
    return _open(width, height) + "".join(parts) + "</svg>"


def sheet_frames() -> str:
    """Every placement at its real proportion, with reserved and covered areas shaded."""
    width, margin, gap = 1400, 60, 34
    head, cursor = _header(
        "Where the copy goes, and where the app covers it",
        "Each frame is drawn at its true proportion. Cobalt is the area kept deliberately empty so "
        "type can sit there. Solid grey is the band the platform draws its own interface over: copy "
        "there is not tight against the edge, it is behind a button. A story is laid out again, not "
        "cropped from the feed post. One frame here has no reserve on purpose, and says why.",
        width, margin, max_lines=4,
    )
    parts = [head]
    tallest = max(h / w for _n, w, h, *_r in PLACEMENTS)
    box = (width - margin * 2 - gap * (len(PLACEMENTS) - 1)) / len(PLACEMENTS)
    plate_h = box * tallest
    for index, (name, pw, ph, top, bottom, band_note, reserve, why) in enumerate(PLACEMENTS):
        scale = min(box / pw, plate_h / ph)
        fw, fh = pw * scale, ph * scale
        ox = margin + index * (box + gap) + (box - fw) / 2
        oy = cursor + (plate_h - fh)
        parts.append(f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{fw:.0f}" height="{fh:.0f}" fill="#E7E1D4"/>')
        if reserve:
            usable_y = oy + top * scale
            usable_h = fh - (top + bottom) * scale
            rx = ox + fw * reserve[0]
            ry = usable_y + usable_h * reserve[1]
            parts.append(f'<rect x="{rx:.0f}" y="{ry:.0f}" width="{fw * reserve[2]:.0f}" '
                         f'height="{usable_h * reserve[3]:.0f}" fill="{COBALT}" opacity="0.16"/>')
        for band_y, band_h in ((oy, top * scale), (oy + fh - bottom * scale, bottom * scale)):
            if band_h > 0:
                parts.append(f'<rect x="{ox:.0f}" y="{band_y:.0f}" width="{fw:.0f}" '
                             f'height="{band_h:.0f}" fill="{MUTED}" opacity="0.55"/>')
        parts.append(f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{fw:.0f}" height="{fh:.0f}" '
                     f'fill="none" stroke="{INK}" stroke-width="2"/>')
        text_y = cursor + plate_h + 34
        parts.append(_text(ox, text_y, name, 19, bold=True))
        parts.append(_text(ox, text_y + 22, f"{pw} x {ph}", 14, fill=COBALT))
        body, text_y = _block(ox, text_y + 46, why, 13, box, "why", fill=MUTED, max_lines=6)
        parts.append(body)
        if band_note:
            body, text_y = _block(ox, text_y + 2, band_note, 13, box, "band", max_lines=3)
            parts.append(body)
    height = cursor + plate_h + 230 + margin
    return _open(width, height) + "".join(parts) + "</svg>"


def _grid_overlay(ox: float, oy: float, fw: float, fh: float, near: float) -> str:
    """Draw the three competing grids on one frame, so the argument about them can be looked at.

    Only the lower-left line of each pair is drawn. Each grid is symmetric about the centre, so the
    second line carries no information the first does not, and six lines on a frame 80 px tall is
    mush. What survives is the only thing in dispute: how far apart the three verticals sit.
    """
    marks = [
        (1 / 3, MUTED, '4 4', 1.0),
        (1 - 1 / PHI, ORANGE, '2 3', 1.0),
        (near, COBALT, None, 1.6),
    ]
    parts = []
    for fraction, colour, dash, weight in marks:
        stroke = f' stroke-dasharray="{dash}"' if dash else ""
        x, y = ox + fw * fraction, oy + fh * fraction
        parts.append(f'<line x1="{x:.1f}" y1="{oy:.1f}" x2="{x:.1f}" y2="{oy + fh:.1f}" '
                     f'stroke="{colour}" stroke-width="{weight}"{stroke}/>')
        parts.append(f'<line x1="{ox:.1f}" y1="{y:.1f}" x2="{ox + fw:.1f}" y2="{y:.1f}" '
                     f'stroke="{colour}" stroke-width="{weight}"{stroke}/>')
    parts.append(f'<circle cx="{ox + fw * near:.1f}" cy="{oy + fh * near:.1f}" r="3.4" fill="{COBALT}"/>')
    return "".join(parts)


def _golden_panel(x: float, y: float, width: float) -> tuple[str, float]:
    """phi used the way it survives scrutiny: to pick sizes, never to place a subject.

    Drawn rather than asserted because the claim in the table is comparative — a 61.8/38.2 split of
    a layout is a real decision, and 38.2% against a thirds 33.3% is 5% of a frame. One of those is
    worth defending to a client and the other is not, and they are the same number.
    """
    parts = [_text(x, y, "phi, doing the one job it is good at", 22, bold=True)]
    body, cursor = _block(x, y + 30, (
        "The golden ratio is not a delivery ratio — no channel accepts 1.618:1 and no viewer reads "
        "it as anything. It is a generator for sizes. Split a layout 61.8 / 38.2 and every panel "
        "relates to every other by one constant, which is why the result looks decided. Use the "
        "same number to place a subject and you are defending 5% of a frame with mathematics that "
        "does not cover the claim."
    ), 15, width, "golden", fill=MUTED, max_lines=4)
    parts.append(body)

    split_w, split_h = width * 0.52, 150
    sx, sy = x, cursor + 12
    image_w = split_w / PHI
    parts.append(f'<rect x="{sx:.0f}" y="{sy:.0f}" width="{image_w:.0f}" height="{split_h}" '
                 f'fill="{COBALT}" opacity="0.16"/>')
    parts.append(f'<rect x="{sx + image_w:.0f}" y="{sy:.0f}" width="{split_w - image_w:.0f}" '
                 f'height="{split_h}" fill="#E7E1D4"/>')
    parts.append(f'<rect x="{sx:.0f}" y="{sy:.0f}" width="{split_w:.0f}" height="{split_h}" '
                 f'fill="none" stroke="{INK}" stroke-width="2"/>')
    parts.append(_text(sx + image_w / 2, sy + split_h / 2 + 5, "image  61.8%", 15,
                       fill=INK, bold=True, anchor="middle"))
    parts.append(_text(sx + image_w + (split_w - image_w) / 2, sy + split_h / 2 + 5, "copy  38.2%", 14,
                       fill=MUTED, anchor="middle"))
    parts.append(_text(sx, sy + split_h + 24, "A split you can defend: one constant, every panel.", 13,
                       fill=MUTED))

    tx = x + split_w + 46
    parts.append(_text(tx, sy + 16, "Type scale, each step x1.618", 14, bold=True))
    step_y = sy + 34
    size = 15.0
    for _rung in range(4):
        step_y += size * 1.15
        parts.append(_text(tx, step_y, f"{size:.0f} px", size, fill=INK))
        size *= PHI
    parts.append(_text(tx, step_y + 26, "15 / 24 / 39 / 64 — four sizes, one decision.", 13, fill=MUTED))
    return "".join(parts), sy + split_h + 46


def sheet_ratios() -> str:
    """Every delivery ratio at true proportion, with the three grids drawn on each one.

    The point of the sheet is the migration. Thirds sits at 33.3% whatever the frame; the
    dynamic-symmetry eye walks from 14.9% on scope to 50% on a square, so the two grids agree on
    3:2 and ISO paper and disagree by 377 px on scope. That is an argument nobody can settle from
    prose, which is why it is drawn. Every number comes from `ratio_lines`, the same function the
    terminal lookup prints, so the sheet cannot claim a position the table denies.
    """
    rows = [r for r in _table("frame-ratios.csv") if r["family"] != "phi"]
    rows.sort(key=lambda r: -int(r["w"]) / int(r["h"]))
    # Six across rather than the four the other sheets use, on a wider canvas that keeps each
    # column the same width. Twelve ratios in three bands makes a sheet twice as tall as it is
    # wide, and a page that has to show it beside anything else can only do that by leaving half a
    # row empty. Two bands of six is the same twelve frames in a shape a layout can actually use.
    width, margin, gap, cols = 2020, 60, 26, 6
    head, cursor = _header(
        "Which ratio, and which grid that ratio wants",
        "Each frame is its true proportion. Grey dashed is thirds at 33.3%, orange dotted is the phi "
        "line at 38.2%, cobalt is the dynamic-symmetry eye with its dot. Only the lower-left line of "
        "each pair is drawn; all three grids are symmetric, so the second line says nothing new. "
        "Watch the cobalt line move as the frames get narrower and the grey one stay put — that gap, "
        "in pixels, is the entire disagreement between the two grids.",
        width, margin, max_lines=4,
    )
    parts = [head]
    box = (width - margin * 2 - gap * (cols - 1)) / cols

    for band_start in range(0, len(rows), cols):
        band = rows[band_start:band_start + cols]
        plate_h = box * max(int(r["h"]) / int(r["w"]) for r in band)
        caption_bottom = cursor + plate_h
        for index, row in enumerate(band):
            pw, ph = int(row["w"]), int(row["h"])
            geo = ratio_lines(pw, ph)
            scale = min(box / pw, plate_h / ph)
            fw, fh = pw * scale, ph * scale
            ox = margin + index * (box + gap)
            oy = cursor + (plate_h - fh)
            parts.append(f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{fw:.0f}" height="{fh:.0f}" '
                         f'fill="#E7E1D4"/>')
            parts.append(_grid_overlay(ox, oy, fw, fh, geo["eye_near"]))
            parts.append(f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{fw:.0f}" height="{fh:.0f}" '
                         f'fill="none" stroke="{INK}" stroke-width="2"/>')
            text_y = cursor + plate_h + 30
            parts.append(_text(ox, text_y, row["label"], 20, bold=True))
            parts.append(_text(ox, text_y + 21, f"{pw} x {ph}  ·  {geo['decimal']:.3f}", 13, fill=COBALT))
            # The computed line reports the gap and stops. It does not say which grid to use, because
            # the row already answers that in its grid column and the two would contradict each
            # other: 5:4 has a 5.7% gap, which is "visible", and still wants centre because it is
            # nearly square. A measurement that also gives advice will eventually give bad advice.
            gap_px = geo["eye_gap_px"]
            verdict = (
                f"Eye {geo['eye_near'] * 100:.1f}%, thirds 33.3% — {gap_px:.0f} px apart on "
                f"{pw} px of width, {gap_px / pw * 100:.1f}% of the frame. "
            ) + ("Under 5%: the grids agree here and the choice is empty."
                 if gap_px < pw * 0.05 else "Over 5%: they disagree and the choice shows.")
            body, text_y = _block(ox, text_y + 44, verdict, 12.5, box, "verdict", max_lines=4)
            parts.append(body)
            body, text_y = _block(ox, text_y + 4, f"Grid: {row['grid']} — {row['anchor_rule']}",
                                  12.5, box, "anchor", fill=MUTED, max_lines=4)
            parts.append(body)
            caption_bottom = max(caption_bottom, text_y)
        cursor = caption_bottom + 54

    golden, cursor = _golden_panel(margin, cursor + 14, width - margin * 2)
    parts.append(golden)
    return _open(width, cursor + margin) + "".join(parts) + "</svg>"


def sheet_palettes() -> str:
    """Every palette as a card, with the contrast ratio measured rather than asserted."""
    rows = _table("palettes.csv")
    width, margin, gap = 1400, 60, 26
    columns = 4
    card_w = (width - margin * 2 - gap * (columns - 1)) / columns
    card_h = 300
    head, cursor = _header(
        "Palettes, with the contrast measured",
        "Every ratio on this sheet is computed from the two hex values beside it, not asserted. "
        "Body text needs 4.5 to 1 against its background; an accent under 3 to 1 can be a fill but "
        "not a hairline or a word. The label colour shown on each button is whichever of black or "
        "white actually passes on that accent.",
        width, margin,
    )
    parts = [head]
    for index, row in enumerate(rows):
        col, line = index % columns, index // columns
        ox = margin + col * (card_w + gap)
        oy = cursor + line * (card_h + gap)
        parts.append(f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{card_w:.0f}" height="{card_h:.0f}" '
                     f'fill="{row["bg"]}" stroke="{INK}" stroke-width="2"/>')
        pad = 18
        parts.append(_text(ox + pad, oy + pad + 20, row["name_en"], 20, fill=row["ink"], bold=True))
        parts.append(_text(ox + pad, oy + pad + 42, row["name_vi"], 15, fill=row["ink"]))
        # The support and accent as real areas, because a colour named is not a colour seen.
        swatch_y = oy + pad + 58
        swatch_h = 46
        parts.append(f'<rect x="{ox + pad:.0f}" y="{swatch_y:.0f}" width="{(card_w - pad * 2) * 0.5:.0f}" '
                     f'height="{swatch_h}" fill="{row["accent"]}"/>')
        parts.append(f'<rect x="{ox + pad + (card_w - pad * 2) * 0.5:.0f}" y="{swatch_y:.0f}" '
                     f'width="{(card_w - pad * 2) * 0.5:.0f}" height="{swatch_h}" fill="{row["support"]}"/>')
        # A button drawn with the label colour the data says passes.
        label = "Xem menu"
        btn_h = 40
        btn_w = advance(label, 15, bold=True) + 34
        btn_y = swatch_y + swatch_h + 16
        parts.append(f'<rect x="{ox + pad:.0f}" y="{btn_y:.0f}" width="{btn_w:.0f}" height="{btn_h}" '
                     f'rx="6" fill="{row["accent"]}"/>')
        parts.append(_text(ox + pad + btn_w / 2, btn_y + btn_h / 2 + 15 * CAP / 2, label, 15,
                           fill=row["accent_label"], bold=True, anchor="middle"))
        facts = (
            f'ink {row["ratio_ink_on_bg"]}:1 · accent {row["ratio_accent_on_bg"]}:1 · '
            f'label {row["ratio_label_on_accent"]}:1'
        )
        body, next_y = _block(ox + pad, btn_y + btn_h + 26, facts, 13, card_w - pad * 2, "facts",
                              fill=row["ink"], max_lines=2)
        parts.append(body)
        body, next_y = _block(ox + pad, next_y + 2, row["use_for"], 13, card_w - pad * 2, "use",
                              fill=row["ink"], max_lines=3)
        parts.append(body)
        body, next_y = _block(ox + pad, next_y + 2, f'Not for: {row["avoid_for"]}', 13,
                              card_w - pad * 2, "avoid", fill=row["ink"], max_lines=3)
        parts.append(body)
    lines = (len(rows) + columns - 1) // columns
    height = cursor + lines * (card_h + gap) + margin
    return _open(width, height) + "".join(parts) + "</svg>"


def sheet_dials(dial_id: str = "margin_ratio") -> str:
    """One dial, three positions, the same content each time.

    A dial explained in prose is a number somebody has to trust. A dial shown at its minimum, its
    default and its maximum is a number somebody can judge in a second, which is the whole point
    for a reader who has never laid anything out.
    """
    rows = {row["dial"]: row for row in _table("layout-dials.csv")}
    if dial_id not in rows:
        raise SystemExit(f"no dial called {dial_id!r}. Known: {', '.join(rows)}")
    dial = rows[dial_id]
    width, margin, gap = 1400, 60, 40
    head, cursor = _header(
        f"One dial, three positions — {dial_id}",
        f'{dial["what_it_changes"]}. Same four items, same words, same colours in all three. Only '
        f'this one number changed. Raise it when: {dial["raise_it_when"]}. Lower it when: '
        f'{dial["lower_it_when"]}. It breaks when: {dial["breaks_at"]}',
        width, margin, max_lines=6,
    )
    parts = [head]
    plate_w = (width - margin * 2 - gap * 2) / 3
    plate_h = plate_w * 1.25
    items = ["Bún bò", "Bún bò đặc biệt", "Bún bò giò heo", "Trà đá"]
    positions = [
        ("minimum", float(dial["min"])),
        ("default", float(dial["quiet_editorial"])),
        ("maximum", float(dial["max"])),
    ]
    for index, (name, value) in enumerate(positions):
        ox = margin + index * (plate_w + gap)
        oy = cursor
        parts.append(f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{plate_w:.0f}" height="{plate_h:.0f}" '
                     f'fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>')
        # Every dial resolves into these four numbers; only the one under test moves.
        pad = plate_w * (value if dial_id == "margin_ratio" else 0.10)
        title_size = plate_w * (value if dial_id == "title_ratio" else 0.062)
        pitch = plate_w * (value if dial_id == "row_pitch_ratio" else 0.072)
        lead = value if dial_id == "line_leading" else 1.28
        column = plate_w - pad * 2
        title_lines = wrap("Bún bò Huế", title_size, column, 2, "title", bold=True)
        y = oy + pad + title_size * CAP
        for line in title_lines:
            parts.append(_text(ox + pad, y, line, title_size, bold=True))
            y += title_size * lead
        y += pitch * 0.4
        parts.append(f'<line x1="{ox + pad:.0f}" y1="{y:.0f}" x2="{ox + plate_w - pad:.0f}" '
                     f'y2="{y:.0f}" stroke="{INK}" stroke-width="1"/>')
        body_size = plate_w * 0.040
        y += pitch * 0.75
        for item in items:
            parts.append(_text(ox + pad, y, item, body_size))
            parts.append(_text(ox + plate_w - pad, y, "—", body_size, anchor="end"))
            y += pitch
        parts.append(_text(ox, oy + plate_h + 30, f"{name} · {dial_id} = {value:g}", 17, bold=True))
        note = {
            "minimum": "Cheapest-looking of the three, and the one a print shop will cut into.",
            "default": "What the quiet-editorial theme ships with.",
            "maximum": "Most expensive-looking, and it fits the fewest items.",
        }[name]
        body, _ = _block(ox, oy + plate_h + 56, note, 14, plate_w, "note", fill=MUTED, max_lines=3)
        parts.append(body)
    height = cursor + plate_h + 140 + margin
    return _open(width, height) + "".join(parts) + "</svg>"


VERDICT_COLOUR = {"keep": COBALT, "transform": ORANGE, "reject": MUTED, "avoid": INK}

VERDICT_GLOSS = {
    "keep": "Take it as it is",
    "transform": "Take the idea, change the thing",
    "reject": "Note it, then do not use it",
    "avoid": "Do not put it in a prompt at all",
}


def _plate_copied(ox: float, oy: float, w: float, h: float) -> str:
    """The reference as a beginner reads it: a picture full of things that belong to somebody.

    The protected parts are marked with rectangles rather than rings. The first version used dashed
    circles and they read as decoration: a circle wide enough to enclose a headline block also
    encloses half the plate and escapes the frame edge, so four marks produced four overlaps and no
    information. A rectangle is the size of the thing it is about.
    """
    parts = [f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{w:.0f}" height="{h:.0f}" '
             f'fill="#EFE9DE" stroke="{INK}" stroke-width="2"/>']
    # A headline, a tagline and a logo lozenge — the three parts that are literally retypable.
    parts.append(f'<rect x="{ox + w * 0.08:.0f}" y="{oy + h * 0.14:.0f}" '
                 f'width="{w * 0.34:.0f}" height="{h * 0.045:.0f}" fill="{INK}"/>')
    parts.append(f'<rect x="{ox + w * 0.08:.0f}" y="{oy + h * 0.21:.0f}" '
                 f'width="{w * 0.24:.0f}" height="{h * 0.028:.0f}" fill="{MUTED}"/>')
    parts.append(f'<rect x="{ox + w * 0.08:.0f}" y="{oy + h * 0.85:.0f}" width="{w * 0.17:.0f}" '
                 f'height="{h * 0.06:.0f}" rx="{h * 0.03:.0f}" fill="{ORANGE}"/>')
    # A figure, deliberately schematic: a head and a shoulder trapezoid. Drawn solid, because the
    # point of this plate is that the beginner is looking at the parts that are filled in.
    hx, hy, hr = ox + w * 0.64, oy + h * 0.30, w * 0.055
    parts.append(f'<circle cx="{hx:.0f}" cy="{hy:.0f}" r="{hr:.0f}" fill="{INK}"/>')
    shoulder_y, hem_y = hy + hr * 1.5, oy + h * 0.78
    parts.append(
        f'<path d="M{hx - hr * 1.1:.0f},{shoulder_y:.0f} L{hx + hr * 1.1:.0f},{shoulder_y:.0f} '
        f'L{hx + hr * 2.4:.0f},{hem_y:.0f} L{hx - hr * 2.4:.0f},{hem_y:.0f} Z" fill="{INK}"/>'
    )
    # x, y, width, height, label, and which corner the label hangs off. Every box is sized to its
    # element and every label sits in a part of the plate no other label reaches.
    marks = [
        (0.055, 0.105, 0.385, 0.160, "the words", "above"),
        (0.640 - 0.083, 0.300 - 0.083 / 0.75, 0.166, 0.166 / 0.75, "the face", "above"),
        (0.470, 0.200, 0.340, 0.610, "the exact pose", "below"),
        (0.060, 0.825, 0.210, 0.110, "the logo", "above"),
    ]
    for fx, fy, fw_, fh_, label, side in marks:
        bx, by = ox + w * fx, oy + h * fy
        parts.append(f'<rect x="{bx:.0f}" y="{by:.0f}" width="{w * fw_:.0f}" height="{h * fh_:.0f}" '
                     f'fill="none" stroke="{ORANGE}" stroke-width="2.5" stroke-dasharray="6 5"/>')
        ly = by - 8 if side == "above" else by + h * fh_ + 18
        parts.append(_text(bx, ly, label, 13, fill=ORANGE, bold=True))
    return "".join(parts)


def _plate_extracted(ox: float, oy: float, w: float, h: float) -> str:
    """The same reference reduced to what transfers: geometry, light direction, reading order."""
    parts = [f'<rect x="{ox:.0f}" y="{oy:.0f}" width="{w:.0f}" height="{h:.0f}" '
             f'fill="#FFFFFF" stroke="{INK}" stroke-width="2"/>']
    for third in (1, 2):
        parts.append(f'<line x1="{ox + w * third / 3:.0f}" y1="{oy:.0f}" x2="{ox + w * third / 3:.0f}" '
                     f'y2="{oy + h:.0f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 6"/>')
        parts.append(f'<line x1="{ox:.0f}" y1="{oy + h * third / 3:.0f}" x2="{ox + w:.0f}" '
                     f'y2="{oy + h * third / 3:.0f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="4 6"/>')
    # The empty area, as a rectangle rather than the phrase "upper left". The two plates put their
    # marks in the same places on purpose: the cobalt rectangle here covers the orange "the words"
    # rectangle there, which is the whole argument of the sheet in one overlay.
    parts.append(f'<rect x="{ox + w * 0.055:.0f}" y="{oy + h * 0.105:.0f}" width="{w * 0.385:.0f}" '
                 f'height="{h * 0.160:.0f}" fill="{COBALT}" opacity="0.16"/>')
    parts.append(_text(ox + w * 0.055, oy + h * 0.105 - 8, "empty, 38% of width", 13, fill=COBALT, bold=True))
    # The subject as an outline only — position and share of frame, no identity.
    parts.append(f'<rect x="{ox + w * 0.470:.0f}" y="{oy + h * 0.200:.0f}" width="{w * 0.340:.0f}" '
                 f'height="{h * 0.610:.0f}" fill="none" stroke="{INK}" stroke-width="2"/>')
    parts.append(_text(ox + w * 0.470, oy + h * 0.810 + 18, "subject, 34% of width, centre-right", 13))
    # Key light, from the side the left plate's own shading implies.
    lx, ly, lr = ox + w * 0.14, oy + h * 0.50, w * 0.038
    parts.append(f'<circle cx="{lx:.0f}" cy="{ly:.0f}" r="{lr:.0f}" fill="{COBALT}"/>')
    parts.append(f'<line x1="{lx:.0f}" y1="{ly:.0f}" x2="{ox + w * 0.52:.0f}" y2="{oy + h * 0.40:.0f}" '
                 f'stroke="{COBALT}" stroke-width="2" stroke-dasharray="7 6"/>')
    parts.append(_text(lx - lr, ly + lr + 18, "key, front-left, 45°", 13, fill=COBALT, bold=True))
    # The reading path, as three numbered stops.
    for order, (px, py) in enumerate(
        [(ox + w * 0.12, oy + h * 0.155), (ox + w * 0.64, oy + h * 0.30), (ox + w * 0.145, oy + h * 0.88)],
        start=1,
    ):
        parts.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="14" fill="{INK}"/>')
        parts.append(_text(px, py + 14 * CAP / 2, str(order), 14, fill="#FFFFFF", bold=True, anchor="middle"))
    parts.append(_text(ox + w - 14, oy + h - 16, "crop 4:3", 13, fill=MUTED, anchor="end"))
    return "".join(parts)


def sheet_reference() -> str:
    """The two halves of a reference, drawn side by side, then the eleven axes that split them.

    A reference is the one input a non-marketer supplies confidently and uses wrongly: they hand
    over a picture they like and mean "make this". The useful half of that picture — where the light
    is, how much of the frame the subject takes, what is left empty, what order it reads in — is
    free to take and is the half nobody looks at. The other half is somebody's face, somebody's
    words and somebody's logo, and it is the half that gets copied.

    Prose cannot make that split legible, because the split is spatial. So the same frame is drawn
    twice: once as the beginner reads it, once as a brief reads it. Then every axis from
    `references/reference-analysis.md` gets a verdict from `data/reference-axes.csv`, which is why
    the sheet cannot drift away from the doctrine it illustrates.
    """
    rows = _table("reference-axes.csv")
    width, margin, gap = 1400, 60, 44
    head, cursor = _header(
        "One reference, two halves",
        "Both frames below are the same picture. On the left is what gets copied: a face, a "
        "headline, a logo, a pose, each of which belongs to somebody. On the right is the same "
        "picture written as a brief: where the light is, how much of the frame the subject takes, "
        "what is left empty, and what order it reads in. Everything on the right is free. Nothing "
        "on the left is. The table underneath gives each axis a verdict, so the answer to \"can I "
        "use this\" is a row rather than a feeling.",
        width, margin, max_lines=5,
    )
    parts = [head]
    plate_w = (width - margin * 2 - gap) / 2
    plate_h = plate_w * 0.75  # 4:3, and the right plate prints that ratio, so it has to be true
    for index, (label, note, draw) in enumerate((
        ("Copied", "What a beginner takes. Four boxes, four owners.", _plate_copied),
        ("Extracted", "What a brief takes. Same frame, none of the ownership.", _plate_extracted),
    )):
        ox = margin + index * (plate_w + gap)
        parts.append(_text(ox, cursor + 20, label, 24, bold=True))
        parts.append(_text(ox, cursor + 44, note, 14, fill=MUTED))
        parts.append(draw(ox, cursor + 64, plate_w, plate_h))
    cursor += 64 + plate_h + 56

    # The spans plus the four gutters have to come to exactly the usable width. The first version
    # totalled 1360 against 1280 available, which does not raise anything — SVG text simply keeps
    # going, so the Leave column ran 80px off the right edge of the canvas.
    columns = [("Axis", 190), ("Verdict", 170), ("Ask yourself", 280), ("Take", 300), ("Leave", 260)]
    gutter = 20
    usable = width - margin * 2
    assert sum(span for _t, span in columns) + gutter * (len(columns) - 1) == usable
    xs, offset = [], margin
    for _title, span in columns:
        xs.append(offset)
        offset += span + gutter
    parts.append(_text(margin, cursor, "Eleven axes, with a verdict on each", 24, bold=True))
    cursor += 34
    for (title, _span), x in zip(columns, xs):
        parts.append(_text(x, cursor, title.upper(), 12, fill=MUTED, bold=True))
    cursor += 10
    parts.append(f'<rect x="{margin}" y="{cursor:.0f}" width="{width - margin * 2}" height="2" fill="{INK}"/>')
    cursor += 26

    for row in rows:
        colour = VERDICT_COLOUR[row["verdict"]]
        cells = [
            (row["name_en"], 15, INK, True, columns[0][1]),
            (None, 0, colour, False, columns[1][1]),
            (row["question_en"], 14, MUTED, False, columns[2][1]),
            (row["take"], 14, INK, False, columns[3][1]),
            (row["leave"], 14, colour, False, columns[4][1]),
        ]
        # The row is as tall as its tallest cell, measured rather than assumed. The first version
        # used a fixed pitch and the `leave` column of the rights row ran into the row below it.
        heights = []
        for content, size, _fill, _bold, span in cells:
            if content is None:
                heights.append(52.0)
                continue
            heights.append(len(wrap(content, size, span, 6, "cell")) * size * LEAD)
        row_h = max(heights) + 20
        parts.append(_text(xs[0], cursor + 13, row["name_en"], 15, bold=True))
        parts.append(_text(xs[0], cursor + 32, row["name_vi"], 13, fill=MUTED))
        chip_w = advance(row["verdict"].upper(), 12, bold=True) + 24
        parts.append(f'<rect x="{xs[1]:.0f}" y="{cursor:.0f}" width="{chip_w:.0f}" height="24" rx="4" fill="{colour}"/>')
        parts.append(_text(xs[1] + chip_w / 2, cursor + 12 + 12 * CAP / 2, row["verdict"].upper(), 12,
                           fill="#FFFFFF", bold=True, anchor="middle"))
        gloss, _ = _block(xs[1], cursor + 42, VERDICT_GLOSS[row["verdict"]], 13, columns[1][1],
                          "gloss", fill=MUTED, max_lines=2)
        parts.append(gloss)
        body, _ = _block(xs[2], cursor + 13, row["question_en"], 14, columns[2][1], "question",
                         fill=MUTED, max_lines=6)
        parts.append(body)
        body, _ = _block(xs[3], cursor + 13, row["take"], 14, columns[3][1], "take", max_lines=6)
        parts.append(body)
        body, _ = _block(xs[4], cursor + 13, row["leave"], 14, columns[4][1], "leave", fill=colour,
                         max_lines=6)
        parts.append(body)
        cursor += row_h
        parts.append(f'<line x1="{margin}" y1="{cursor - 10:.0f}" x2="{width - margin}" '
                     f'y2="{cursor - 10:.0f}" stroke="{MUTED}" stroke-width="1" opacity="0.5"/>')

    closing, cursor = _block(
        margin,
        cursor + 24,
        "Three axes say transform, and reference-analysis.md asks you to move at least three before "
        "using a pattern at all. That is not a coincidence: hook, material and copy behaviour are "
        "the three that carry the most recognition, so moving them is what stops a reference being "
        "traceable at a glance. If the result can still be traced to one source, start again.",
        15, width - margin * 2, "closing", fill=MUTED, max_lines=4,
    )
    parts.append(closing)
    return _open(width, cursor + margin) + "".join(parts) + "</svg>"


SHEETS = {
    "lighting": sheet_lighting,
    "frames": sheet_frames,
    "ratios": sheet_ratios,
    "palettes": sheet_palettes,
    "dials": sheet_dials,
    "reference": sheet_reference,
}


def wrap_html(svg: str, title: str) -> str:
    return (
        "<!doctype html>\n<html lang=\"vi\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{html.escape(title)}</title>\n"
        "<style>body{margin:0;background:#e9e5dc;display:flex;justify-content:center;"
        "padding:28px}svg{max-width:96vw;height:auto;box-shadow:0 2px 24px rgba(0,0,0,.14)}</style>\n"
        f"</head>\n<body>\n{svg}\n</body>\n</html>\n"
    )


def main() -> None:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description="Render a reference sheet as SVG.")
    parser.add_argument("--sheet", choices=sorted(SHEETS), required=True)
    parser.add_argument("--dial", default="margin_ratio", help="which dial the dials sheet shows")
    parser.add_argument("--output")
    parser.add_argument("--html-output")
    args = parser.parse_args()
    svg = sheet_dials(args.dial) if args.sheet == "dials" else SHEETS[args.sheet]()
    emit(svg + "\n", args.output)
    if args.html_output:
        emit(wrap_html(svg, f"marketing-minthep — {args.sheet}"), args.html_output)


if __name__ == "__main__":
    main()
