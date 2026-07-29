#!/usr/bin/env python3
"""Draw the reference sheets a non-marketer actually needs, as real SVG, with no API key.

A skill that only writes prose about lighting asks the reader to hold a diagram in their head. So
these four sheets are the diagram. Every number printed on them is computed from the same data
tables the rest of the skill reads, which means a sheet cannot drift away from the advice: change
`data/layout-dials.csv` and the dial sheet changes with it.

  lighting  A plan view of six setups, seen from above, with the shadow each one throws.
  frames    Every placement at its real proportion, with the reserved copy area and the bands the
            platform's own interface covers, shaded.
  palettes  Every palette as a card, with its measured contrast ratio printed on it.
  dials     One layout drawn three times — at the minimum, the default and the maximum of a single
            dial — so the reader sees what the number does instead of reading what it does.

The dial sheet is the one that answers "cơ chế bố cục": the mechanism is a small set of numbers,
and the only honest way to explain a number is to show the same thing twice with it changed.
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


SHEETS = {
    "lighting": sheet_lighting,
    "frames": sheet_frames,
    "palettes": sheet_palettes,
    "dials": sheet_dials,
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
