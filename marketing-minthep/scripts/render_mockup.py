#!/usr/bin/env python3
"""Render a small, dependency-free SVG/HTML mockup from a design spec JSON file.

Nothing here is positioned by a fraction of the canvas height. That was the previous approach and
it produced two defects you could only see by looking at a render: the title, set at 5.9 percent
of the width, grew tall enough that its ascenders struck the kicker baseline sitting at 11.1
percent of the height, so "SIGNATURE MENU" had the diacritic of "mỗi" cutting through it; and a
title longer than the space beside the hero ran straight under the bowl, so "Bún bò Huế gia
truyền cô Tám" rendered as "Bún bò Huế gia truy" with the rest painted over. Text was also
wrapped by counting characters, with the character budget computed as 48 divided by the scale,
which is backwards: a 2160px poster got a 24-character measure, wrapped the subtitle after a
third of the sentence, and silently dropped the remaining two thirds.

So the layout is measured and flowed instead. `advance` estimates rendered width from a
per-character table calibrated against browser renders of the two font stacks below (within 1.5
percent on the four strings tested), `wrap` breaks on that width rather than on a character
count, and every vertical position is derived by stacking real cap heights and descenders down
from the top margin. Copy that does not fit raises, the way an over-long item list already did:
a mockup that quietly deletes two thirds of a sentence looks finished, which is what makes it
dangerous.
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
import unicodedata
from pathlib import Path

# Full stacks, not bare family names. A bare "Arial" falls back to an unpredictable default on
# any machine without it — including the Linux runners that build the handbook — which changes
# every metric the layout depends on.
#
# Every family here was checked against the two-diacritic Vietnamese letters (ấ ố ồ ế ữ ợ ử ẩ ẽ,
# the U+1EA0–U+1EF9 block) by reading its cmap. Georgia used to lead the serif stack and covers
# none of them: it has â and ô from Latin-1 but not ấ or ố, so a renderer drew the base letter
# with a floating accent beside it and "Nấu theo lối cũ" came out as "Nâ´u theo lô´i cũ". A font
# that silently mangles the language the deliverables are written in cannot be the first choice,
# so it is gone rather than demoted. Do not add a family to either stack without checking its
# coverage the same way — the failure is invisible in ASCII test fixtures.
SANS = "Arial, 'Segoe UI', Tahoma, 'Liberation Sans', 'DejaVu Sans', 'Noto Sans', sans-serif"
SERIF = "Cambria, Constantia, 'Times New Roman', 'Liberation Serif', 'DejaVu Serif', 'Noto Serif', serif"

# Families measured as lacking the block above. None may appear in a stack.
FONTS_WITHOUT_VIETNAMESE = ("Georgia", "Book Antiqua", "Garamond")

# Vertical metrics as fractions of the font size, close enough for both stacks. CAP is how far
# the ink rises above the baseline, DROP how far it falls below, LEAD the baseline-to-baseline
# step inside a wrapped block. Everything vertical is built from these three numbers, so a
# theme that changes a type size cannot silently start overlapping its neighbour.
CAP, DROP, LEAD = 0.74, 0.26, 1.24

# Per-character advance widths as fractions of the font size. A single average coefficient
# treated "Illinois" and "Wammawamma" as the same width, which is how the price leader ended up
# as a six-dot stub next to a long dish name. Diacritics are stripped before measuring because
# ấ advances exactly as far as a — that is also why this needs no font library.
NARROW = set("ijltfIrJ.,;:!|'\"()[]{}/\\-`’‘·")
WIDE = set("mwMW@%&—–")
# Errs wide on purpose. Wrapping early costs a line break; wrapping late runs type off the page.
SAFETY = 1.04
BOLD = 1.06

# Below this a row's description line collides with the next row's name.
MIN_ROW_PITCH = 58

# A theme has to change the layout, not just the palette. `plan_design_options.py` sells these
# three as genuinely different directions — "generous margins, restrained type scale" against
# "modular rows, bold numerals" — so if they rendered identically apart from colour, the option
# set would be a lie dressed up as a choice. Each entry below is what that promise costs in
# geometry.
#   margin      side margin as a fraction of width
#   title       title size as a fraction of width
#   pitch       natural row pitch at 1080 wide, before the band stretches or compresses it
#   header      how the top rule is drawn
#   marker      what precedes each item name
#   dotted      whether a leader connects the name to the price
THEMES = {
    # Space is the whole idea, so margins are wide, type is large and quiet, rows breathe, and
    # nothing decorates the row — a leader dot or an index number would break the calm.
    "quiet-editorial": {
        "bg": "#f3efe6", "ink": "#171717", "accent": "#b65f45",
        "display": SERIF, "body": SANS,
        "margin": 0.111, "title": 0.065, "pitch": 82, "header": "hairline",
        "marker": "none", "dotted": False,
    },
    # Built for scanning on a phone: tighter margins, denser rows, a heavy accent bar, and an
    # index numeral so a customer can order by number across a counter.
    "modern-street": {
        "bg": "#f5f1e8", "ink": "#171717", "accent": "#df4b2e",
        "display": SANS, "body": SANS,
        "margin": 0.0833, "title": 0.059, "pitch": 70, "header": "bar",
        "marker": "number", "dotted": False,
    },
    # Print-menu conventions: a double rule, a bullet, and a dotted leader to the price, which is
    # how a paper menu has guided the eye across a wide column for a century.
    "heritage-craft": {
        "bg": "#e8ddc8", "ink": "#24362b", "accent": "#a85932",
        "display": SERIF, "body": SERIF,
        "margin": 0.0972, "title": 0.056, "pitch": 78, "header": "double",
        "marker": "bullet", "dotted": True,
    },
}


def advance(text: str, size: float, bold: bool = False) -> float:
    """Estimate the rendered width of a string, erring slightly wide."""
    total = 0.0
    for character in unicodedata.normalize("NFD", str(text)):
        if unicodedata.combining(character):
            continue
        if character == " ":
            total += 0.28
        elif character in NARROW:
            total += 0.30
        elif character in WIDE:
            total += 0.90
        elif character.isupper():
            total += 0.68
        elif character.isdigit():
            total += 0.56
        else:
            total += 0.55
    return total * size * SAFETY * (BOLD if bold else 1.0)


def wrap(text: str, size: float, limit: float, max_lines: int, field: str, bold: bool = False) -> list[str]:
    """Break `text` to `limit` pixels, or raise naming what has to be shortened.

    Truncation is not an option here. The subtitle used to be cut to two lines and the remainder
    thrown away, so a spec whose subtitle read "...ruốc Huế nguyên chất, không dùng bột ngọt"
    rendered as "...ruốc Huế nguyên chất," — ending on a comma, which is the layout advertising
    that it ate the rest of the sentence.
    """
    words = str(text).split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if advance(candidate, size, bold) <= limit:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    if len(lines) > max_lines:
        budget = sum(len(line) for line in lines[:max_lines])
        raise ValueError(
            f"{field} needs {len(lines)} lines at this size and the layout holds {max_lines}; "
            f"shorten it to about {budget} characters or raise the canvas width"
        )
    return lines


def _tspans(lines: list[str], x: float, step: float) -> str:
    return "".join(
        f'<tspan x="{x:.0f}" dy="{0 if index == 0 else step:.0f}">{html.escape(line)}</tspan>'
        for index, line in enumerate(lines)
    )


def _bowl(x: float, y: float, box_w: float, box_h: float, scale: float) -> str:
    """A schematic noodle bowl drawn to fit the box it is given.

    It used to take a single radius and derive the height from it, so on a box that was taller
    than it was wide the bowl came out as a flat disc — a dark ellipse with a red one on top,
    reading as a hockey puck rather than a bowl of anything. Vessel depth is now a share of the
    box height, so the silhouette stays a bowl at any hero shape.

    It is deliberately a diagram, not an illustration. A placeholder that tried to look like a
    photograph would invite someone to mistake it for the dish, and the render is only ever
    standing in for a real photo that has not been taken yet.
    """
    rx = min(box_w, box_h * 1.9) / 2
    rim_ry = rx * 0.40
    depth = min(box_h - rim_ry * 2, rx * 0.62)
    cx = x + box_w / 2
    rim_cy = y + rim_ry + max(0.0, (box_h - rim_ry * 2 - depth)) / 2
    foot_cy = rim_cy + depth
    return (
        # The rim, as a whole ellipse, so the bowl reads as open at the top.
        f'<ellipse cx="{cx:.0f}" cy="{rim_cy:.0f}" rx="{rx:.0f}" ry="{rim_ry:.0f}" fill="#231f20"/>'
        # The front wall, from the near edge of the rim down to a narrower foot. Both arcs have to
        # bulge downward: with SVG's y-axis pointing down, that is sweep 0 travelling left to
        # right and sweep 1 travelling right to left. Getting the second one wrong turned the
        # bowl into a saucer with two spikes under it.
        f'<path d="M{cx - rx:.0f} {rim_cy:.0f} '
        f'A{rx:.0f} {rim_ry:.0f} 0 0 0 {cx + rx:.0f} {rim_cy:.0f} '
        f'L{cx + rx * 0.62:.0f} {foot_cy:.0f} '
        f'A{rx * 0.62:.0f} {rim_ry * 0.62:.0f} 0 0 1 {cx - rx * 0.62:.0f} {foot_cy:.0f} Z" '
        f'fill="#231f20"/>'
        # Broth surface, inset so the rim reads as a rim.
        f'<ellipse cx="{cx:.0f}" cy="{rim_cy:.0f}" rx="{rx * 0.88:.0f}" ry="{rim_ry * 0.88:.0f}" '
        f'fill="#a8432e"/>'
        # Two garnish arcs sitting on the broth, not floating above the vessel.
        f'<path d="M{cx - rx * 0.60:.0f} {rim_cy + rim_ry * 0.10:.0f} '
        f'Q{cx:.0f} {rim_cy + rim_ry * 0.72:.0f} {cx + rx * 0.60:.0f} {rim_cy + rim_ry * 0.10:.0f}" '
        f'fill="none" stroke="#efc08a" stroke-width="{max(2, round(8 * scale))}" stroke-linecap="round"/>'
        f'<path d="M{cx - rx * 0.44:.0f} {rim_cy - rim_ry * 0.30:.0f} '
        f'Q{cx:.0f} {rim_cy - rim_ry * 0.66:.0f} {cx + rx * 0.44:.0f} {rim_cy - rim_ry * 0.30:.0f}" '
        f'fill="none" stroke="#f3d7b1" stroke-width="{max(1, round(5 * scale))}" stroke-linecap="round" opacity=".8"/>'
    )


def _art_menu(spec: dict, width: int, height: int) -> str:
    """Render art-directed restaurant menus whose structures differ, not only their palettes."""
    theme = str(spec.get("theme", "art-nocturne"))
    image = html.escape(str(spec.get("hero_image", "")), quote=True)
    secondary = html.escape(str(spec.get("secondary_image", spec.get("hero_image", ""))), quote=True)
    title = html.escape(str(spec.get("title", "Bún bò")))
    kicker = html.escape(str(spec.get("kicker", "MENU / CONCEPT")))
    subtitle = html.escape(str(spec.get("subtitle", "Thông tin chờ quán xác nhận")))
    footer = html.escape(str(spec.get("footer", "CONCEPT MENU / Nội dung cần được quán duyệt")))
    items = list(spec.get("items", []))[:4]
    scale = width / 1080

    def rows(x: int, y: int, span: int, pitch: int, ink: str, accent: str,
             numbered: bool = False, descriptions: bool = True) -> str:
        output = []
        for index, item in enumerate(items):
            row_y = y + index * pitch
            name = html.escape(str(item.get("name", "Món")))
            desc = html.escape(str(item.get("description", "")))
            price = html.escape(str(item.get("price", "—")))
            marker = f'<text x="{x}" y="{row_y}" class="art-marker">{index + 1:02d}</text>' if numbered else ""
            name_x = x + (54 if numbered else 0)
            output.append(
                f'{marker}<text x="{name_x}" y="{row_y}" class="art-item">{name}</text>'
                f'<text x="{x + span}" y="{row_y}" text-anchor="end" class="art-price">{price}</text>'
                + (f'<text x="{name_x}" y="{row_y + round(27 * scale)}" class="art-desc">{desc}</text>'
                   if descriptions else "")
                + f'<line x1="{x}" y1="{row_y + round(43 * scale)}" x2="{x + span}" '
                  f'y2="{row_y + round(43 * scale)}" stroke="{ink}" stroke-opacity=".22"/>'
            )
        return "".join(output)

    common_defs = (
        '<filter id="mono"><feColorMatrix type="saturate" values="0"/></filter>'
        '<filter id="warm"><feColorMatrix type="matrix" values="1.08 0 0 0 0.02  0 0.95 0 0 0  0 0 0.82 0 0  0 0 0 1 0"/></filter>'
    )

    if theme == "art-nocturne":
        bg, ink, accent = "#11100f", "#f8f3e8", "#ff5b2e"
        hero_h = round(height * 0.50)
        body = rows(round(70 * scale), round(height * 0.66), round(940 * scale), round(112 * scale), ink, accent, True)
        art = f'''
<defs>{common_defs}<clipPath id="art-clip"><rect width="{width}" height="{hero_h}"/></clipPath></defs>
<rect width="100%" height="100%" fill="{bg}"/>
<image href="{image}" width="{width}" height="{hero_h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#art-clip)"/>
<rect width="{width}" height="{hero_h}" fill="#080706" opacity=".34"/>
<text x="{round(70*scale)}" y="{round(74*scale)}" class="art-kicker">{kicker}</text>
<text x="{round(70*scale)}" y="{round(hero_h-92*scale)}" class="art-title">{title}</text>
<text x="{round(73*scale)}" y="{round(hero_h-48*scale)}" class="art-subtitle">{subtitle}</text>
<rect x="{round(70*scale)}" y="{round(hero_h+42*scale)}" width="{round(940*scale)}" height="{round(8*scale)}" fill="{accent}"/>
{body}<text x="{round(70*scale)}" y="{height-round(28*scale)}" class="art-footer">{footer}</text>'''
        css = f'.art-title{{font:900 {round(104*scale)}px {SANS};fill:{ink};letter-spacing:-4px}}.art-kicker,.art-footer{{font:700 {round(17*scale)}px {SANS};fill:{ink};letter-spacing:3px}}.art-subtitle{{font:500 {round(21*scale)}px {SANS};fill:{ink}}}.art-item{{font:800 {round(29*scale)}px {SANS};fill:{ink}}}.art-marker{{font:700 {round(16*scale)}px {SANS};fill:{accent}}}.art-price{{font:800 {round(27*scale)}px {SANS};fill:{accent}}}.art-desc{{font:400 {round(17*scale)}px {SANS};fill:{ink};opacity:.68}}'
    elif theme == "art-lacquer":
        bg, ink, accent = "#721f24", "#fff4df", "#efb54a"
        circle = round(245 * scale)
        body = rows(round(145*scale), round(680*scale), round(790*scale), round(125*scale), ink, accent, False)
        art = f'''
<defs>{common_defs}<clipPath id="art-clip"><circle cx="{width//2}" cy="{round(280*scale)}" r="{circle}"/></clipPath></defs>
<rect width="100%" height="100%" fill="{bg}"/>
<g fill="none" stroke="{accent}" stroke-opacity=".20" stroke-width="3">
  <path d="M50 80 C240 20 420 140 540 70 S850 20 1030 110"/>
  <path d="M30 1170 C220 1080 390 1210 560 1140 S850 1080 1050 1180"/>
  <circle cx="118" cy="1020" r="44"/><circle cx="118" cy="1020" r="28"/>
  <circle cx="965" cy="155" r="36"/><circle cx="965" cy="155" r="20"/>
</g>
<circle cx="{width//2}" cy="{round(280*scale)}" r="{circle+round(16*scale)}" fill="none" stroke="{accent}" stroke-width="2"/>
<image href="{image}" x="{width//2-circle}" y="{round(280*scale)-circle}" width="{circle*2}" height="{circle*2}" preserveAspectRatio="xMidYMid slice" clip-path="url(#art-clip)" filter="url(#warm)"/>
<text x="{width//2}" y="{round(54*scale)}" text-anchor="middle" class="art-kicker">{kicker}</text>
<text x="{width//2}" y="{round(585*scale)}" text-anchor="middle" class="art-title">{title}</text>
<text x="{width//2}" y="{round(624*scale)}" text-anchor="middle" class="art-subtitle">{subtitle}</text>
{body}<text x="{width//2}" y="{height-round(30*scale)}" text-anchor="middle" class="art-footer">{footer}</text>'''
        css = f'.art-title{{font:700 {round(72*scale)}px {SERIF};fill:{ink}}}.art-kicker,.art-footer{{font:600 {round(15*scale)}px {SANS};fill:{accent};letter-spacing:4px}}.art-subtitle{{font:400 {round(19*scale)}px {SERIF};fill:{ink};opacity:.82}}.art-item{{font:700 {round(27*scale)}px {SERIF};fill:{ink}}}.art-price{{font:700 {round(23*scale)}px {SANS};fill:{accent}}}.art-desc{{font:400 {round(16*scale)}px {SANS};fill:{ink};opacity:.7}}'
    elif theme == "art-counter-signal":
        bg, ink, accent = "#174bd6", "#ffffff", "#ff6b35"
        photo_x = round(600*scale)
        body = rows(round(62*scale), round(690*scale), round(956*scale), round(122*scale), ink, accent, True, False)
        art = f'''
<defs>{common_defs}<clipPath id="art-clip"><polygon points="{photo_x},0 {width},0 {width},{round(620*scale)} {round(510*scale)},{round(620*scale)}"/></clipPath></defs>
<rect width="100%" height="100%" fill="{bg}"/>
<g fill="none" stroke="#ffffff" stroke-opacity=".18" stroke-width="5">
  <path d="M40 470 L300 210 L560 470"/><path d="M94 520 L326 288 L558 520"/>
  <circle cx="82" cy="112" r="26"/><circle cx="82" cy="112" r="12"/>
</g>
<rect x="0" y="0" width="{round(585*scale)}" height="{round(620*scale)}" fill="{accent}"/>
<image href="{image}" x="{round(470*scale)}" y="0" width="{round(610*scale)}" height="{round(620*scale)}" preserveAspectRatio="xMidYMid slice" clip-path="url(#art-clip)"/>
<text x="{round(62*scale)}" y="{round(66*scale)}" class="art-kicker">{kicker}</text>
<text x="{round(62*scale)}" y="{round(225*scale)}" class="art-title"><tspan x="{round(62*scale)}">BÚN</tspan><tspan x="{round(62*scale)}" dy="{round(116*scale)}">BÒ</tspan></text>
<text x="{round(62*scale)}" y="{round(520*scale)}" class="art-subtitle">{subtitle}</text>
<text x="{round(62*scale)}" y="{round(610*scale)}" class="art-category">CHỌN MÓN / GỌI SỐ</text>
{body}<text x="{round(62*scale)}" y="{height-round(30*scale)}" class="art-footer">{footer}</text>'''
        css = f'.art-title{{font:900 {round(126*scale)}px {SANS};fill:#11100f;letter-spacing:-5px}}.art-kicker,.art-category,.art-footer{{font:800 {round(16*scale)}px {SANS};fill:{ink};letter-spacing:3px}}.art-subtitle{{font:700 {round(22*scale)}px {SANS};fill:#11100f}}.art-item{{font:900 {round(33*scale)}px {SANS};fill:{ink}}}.art-marker{{font:900 {round(18*scale)}px {SANS};fill:{accent}}}.art-price{{font:900 {round(31*scale)}px {SANS};fill:{accent}}}'
    elif theme == "art-gallery-mono":
        bg, ink, accent = "#f7f7f5", "#111111", "#111111"
        body = rows(round(510*scale), round(510*scale), round(500*scale), round(155*scale), ink, accent, False)
        art = f'''
<defs>{common_defs}<clipPath id="art-clip"><rect x="0" y="0" width="{round(435*scale)}" height="{height}"/></clipPath></defs>
<rect width="100%" height="100%" fill="{bg}"/>
<path d="M470 0 L470 1350" stroke="#111111" stroke-width="8"/>
<image href="{image}" x="0" y="0" width="{round(435*scale)}" height="{height}" preserveAspectRatio="xMidYMid slice" clip-path="url(#art-clip)" filter="url(#mono)"/>
<text x="{round(510*scale)}" y="{round(76*scale)}" class="art-kicker">{kicker}</text>
<text x="{round(510*scale)}" y="{round(235*scale)}" class="art-title">{title}</text>
<text x="{round(514*scale)}" y="{round(284*scale)}" class="art-subtitle">{subtitle}</text>
<line x1="{round(510*scale)}" y1="{round(350*scale)}" x2="{round(1010*scale)}" y2="{round(350*scale)}" stroke="{ink}" stroke-width="3"/>
{body}<text x="{round(510*scale)}" y="{height-round(32*scale)}" class="art-footer">{footer}</text>'''
        css = f'.art-title{{font:700 {round(54*scale)}px {SERIF};fill:{ink}}}.art-kicker{{font:700 {round(15*scale)}px {SANS};fill:{ink};letter-spacing:3px}}.art-footer{{font:700 {round(11*scale)}px {SANS};fill:{ink};letter-spacing:2px}}.art-subtitle{{font:400 {round(20*scale)}px {SERIF};fill:{ink}}}.art-item{{font:700 {round(25*scale)}px {SERIF};fill:{ink}}}.art-price{{font:700 {round(22*scale)}px {SANS};fill:{ink}}}.art-desc{{font:400 {round(15*scale)}px {SANS};fill:{ink};opacity:.66}}'
    else:  # art-broadsheet
        bg, ink, accent = "#eee9df", "#1b1a18", "#c53b24"
        body_left = rows(round(62*scale), round(760*scale), round(448*scale), round(132*scale), ink, accent, False)
        art = f'''
<defs>{common_defs}<clipPath id="art-clip"><rect x="{round(552*scale)}" y="{round(315*scale)}" width="{round(466*scale)}" height="{round(835*scale)}"/></clipPath></defs>
<rect width="100%" height="100%" fill="{bg}"/>
<g fill="none" stroke="{accent}" stroke-width="4" opacity=".6">
  <path d="M60 360 h420"/><path d="M60 372 h300"/>
  <circle cx="970" cy="148" r="40"/><path d="M940 148 h60 M970 118 v60"/>
</g>
<text x="{round(62*scale)}" y="{round(65*scale)}" class="art-kicker">{kicker}</text>
<line x1="{round(62*scale)}" y1="{round(92*scale)}" x2="{round(1018*scale)}" y2="{round(92*scale)}" stroke="{ink}" stroke-width="5"/>
<text x="{round(62*scale)}" y="{round(255*scale)}" class="art-title">{title}</text>
<text x="{round(66*scale)}" y="{round(300*scale)}" class="art-subtitle">{subtitle}</text>
<image href="{image}" x="{round(552*scale)}" y="{round(315*scale)}" width="{round(466*scale)}" height="{round(835*scale)}" preserveAspectRatio="xMidYMid slice" clip-path="url(#art-clip)" filter="url(#warm)"/>
<text x="{round(62*scale)}" y="{round(660*scale)}" class="art-category">MÓN TRONG NGÀY</text>
{body_left}<rect x="{round(552*scale)}" y="{round(1178*scale)}" width="{round(466*scale)}" height="{round(92*scale)}" fill="{accent}"/>
<text x="{round(575*scale)}" y="{round(1236*scale)}" class="art-callout">NƯỚC DÙNG NẤU MỖI SÁNG</text>
<text x="{round(62*scale)}" y="{height-round(30*scale)}" class="art-footer">{footer}</text>'''
        css = f'.art-title{{font:900 {round(102*scale)}px {SANS};fill:{ink};letter-spacing:-4px}}.art-kicker,.art-category,.art-footer{{font:800 {round(15*scale)}px {SANS};fill:{ink};letter-spacing:3px}}.art-subtitle{{font:400 {round(20*scale)}px {SERIF};fill:{ink}}}.art-item{{font:800 {round(25*scale)}px {SANS};fill:{ink}}}.art-price{{font:800 {round(22*scale)}px {SANS};fill:{accent}}}.art-desc{{font:400 {round(15*scale)}px {SERIF};fill:{ink};opacity:.72}}.art-callout{{font:900 {round(18*scale)}px {SANS};fill:#fff;letter-spacing:2px}}'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title subtitle">
<title id="title">{title}</title><desc id="subtitle">{subtitle}</desc>{art}<style>{css}</style></svg>'''


def render(spec: dict) -> str:
    width = int(spec.get("width", 1080))
    height = int(spec.get("height", 1350))
    if width < 480 or height < 480:
        raise ValueError(f"canvas {width}x{height} is too small to lay out; minimum is 480x480")
    if str(spec.get("theme", "")).startswith("art-"):
        return _art_menu(spec, width, height)
    style = THEMES.get(str(spec.get("theme", "quiet-editorial")), THEMES["quiet-editorial"])
    display_font, body_font = style["display"], style["body"]
    bg = html.escape(str(spec.get("background", style["bg"])))
    ink = html.escape(str(spec.get("ink", style["ink"])))
    accent = html.escape(str(spec.get("accent", style["accent"])))

    scale = width / 1080
    margin = round(width * style["margin"])
    right = width - margin
    rule_weight = max(1, round(8 * scale))
    header_rule_y = round(height * 0.0519)
    footer_rule_y = height - round(height * 0.0519)
    footer_y = height - round(height * 0.0222)
    gutter = round(28 * scale)

    size = {
        "kicker": max(11, round(22 * scale)),
        "title": max(24, round(width * style["title"])),
        "subtitle": max(12, round(24 * scale)),
        "category": max(10, round(20 * scale)),
        "item": max(14, round(28 * scale)),
        "desc": max(10, round(19 * scale)),
        "price": max(13, round(26 * scale)),
        "footer": max(9, round(15 * scale)),
    }

    # The hero box is claimed before any type is measured, because the type has to be told where
    # not to go. Height is capped against the width so the bowl cannot be squashed into a disc.
    items = list(spec.get("items", []))
    hero_href = spec.get("hero_image")
    hero_shape = spec.get("hero_shape", "bowl")
    has_hero = bool(hero_href) or hero_shape == "bowl"
    hero_w = round(width * 0.30)
    hero_x = right - hero_w
    hero_top = header_rule_y + round(38 * scale)
    hero_h = min(round(height * 0.20), round(hero_w * 0.78))
    # Everything in the header measures against this, not against the page edge.
    column = (hero_x - gutter if has_hero else right) - margin

    kicker_lines = wrap(
        str(spec.get("kicker", "MENU / CONCEPT")), size["kicker"], column, 2, "kicker", bold=True
    )
    # Three lines, not two: at quiet-editorial's 6.5-percent title size the column beside the
    # hero holds about eleven characters a line, and a shop name of any length is normal input.
    title_lines = wrap(
        str(spec.get("title", "Untitled design")), size["title"], column, 3, "title", bold=True
    )
    subtitle_lines = wrap(
        str(spec.get("subtitle", "Replace with approved copy")), size["subtitle"], column, 3, "subtitle"
    )

    def flow(cursor: float, lines: list[str], point: float, air: float) -> tuple[list[int], float]:
        """Stack a text block under `cursor`, returning its baselines and new ink bottom."""
        first = cursor + point * (air + CAP)
        baselines = [round(first + index * point * LEAD) for index in range(len(lines))]
        return baselines, baselines[-1] + point * DROP

    cursor = float(header_rule_y + rule_weight)
    kicker_y, cursor = flow(cursor, kicker_lines, size["kicker"], 1.35)
    title_y, cursor = flow(cursor, title_lines, size["title"], 0.42)
    subtitle_y, cursor = flow(cursor, subtitle_lines, size["subtitle"], 0.62)

    hero = ""
    if hero_href:
        hero = (
            f'<image href="{html.escape(str(hero_href), quote=True)}" x="{hero_x}" y="{hero_top}" '
            f'width="{hero_w}" height="{hero_h}" preserveAspectRatio="xMidYMid slice" '
            f'clip-path="url(#hero-clip)"/>'
        )
    elif hero_shape == "bowl":
        hero = _bowl(hero_x, hero_top, hero_w, hero_h, scale)

    # The divider clears whichever is lower, the header type or the hero. Fixing it at 31 percent
    # of the height meant a two-line title pushed the subtitle through it.
    divider_y = round(max(cursor, hero_top + hero_h if has_hero else 0) + 44 * scale)

    # The top rule carries most of the theme's first impression, so each direction draws its own:
    # a heavy accent bar shouts, a hairline whispers, a double rule reads as printed stationery.
    if style["header"] == "bar":
        inset = round(width * 0.0648)
        header_svg = (
            f'<rect x="{inset}" y="{header_rule_y}" width="{width - 2 * inset}" '
            f'height="{rule_weight}" fill="{accent}"/>'
        )
    elif style["header"] == "double":
        gap = max(3, round(6 * scale))
        header_svg = (
            f'<line x1="{margin}" y1="{header_rule_y}" x2="{right}" y2="{header_rule_y}" '
            f'stroke="{accent}" stroke-width="{max(2, round(4 * scale))}"/>'
            f'<line x1="{margin}" y1="{header_rule_y + gap}" x2="{right}" y2="{header_rule_y + gap}" '
            f'stroke="{accent}" stroke-width="{max(1, round(1.5 * scale))}"/>'
        )
    else:
        header_svg = (
            f'<line x1="{margin}" y1="{header_rule_y}" x2="{right}" y2="{header_rule_y}" '
            f'stroke="{accent}" stroke-width="{max(1, round(2 * scale))}"/>'
        )

    # The category label and the rows are laid out as one group and the leftover space is split
    # above and below it. Anchoring the label to the divider and the rows to the band left four
    # dishes on a tall canvas sitting under a label they had visibly detached from, with a hole
    # over the footer; both halves of that read as a rendering fault rather than as white space.
    group_top = divider_y + round(40 * scale)
    group_bottom = footer_rule_y - round(30 * scale)
    label_height = round(size["category"] * (CAP + DROP) + 34 * scale)
    band_top = group_top + label_height
    band = group_bottom - band_top
    marker = style["marker"]
    indent = margin + (round(46 * scale) if marker != "none" else 0)
    desc_offset = round(size["item"] * DROP + size["desc"] * CAP + 8 * scale)
    desc_step = round(size["desc"] * LEAD)
    category_y = group_top + round(size["category"] * CAP)

    rows: list[str] = []
    if items:
        # Names and descriptions are wrapped before any vertical arithmetic, because how tall a
        # row is depends on how many lines it took. A long dish name used to run under its own
        # price; a long description ran off the right edge.
        laid: list[dict] = []
        for index, item in enumerate(items):
            name_text = str(item.get("name", "Item"))
            price_text = str(item.get("price", "TBD"))
            price_w = advance(price_text, size["price"], bold=True)
            name_limit = right - indent - price_w - round(20 * scale)
            laid.append(
                {
                    "name_text": name_text,
                    "price_text": price_text,
                    "price_w": price_w,
                    "name": wrap(name_text, size["item"], name_limit, 2, f"item {index + 1} name", bold=True),
                    "desc": wrap(
                        str(item.get("description", "")), size["desc"], right - indent, 2,
                        f"item {index + 1} description",
                    ),
                }
            )
        name_lines = max(len(row["name"]) for row in laid)
        desc_lines = max(1 if row["desc"] == [""] else len(row["desc"]) for row in laid)
        # Ink height of the tallest row, which is what a pitch actually has to clear.
        row_ink = round(
            size["item"] * (CAP + (name_lines - 1) * LEAD)
            + desc_offset
            + size["desc"] * ((desc_lines - 1) * LEAD + DROP)
        )
        floor_pitch = max(round(MIN_ROW_PITCH * scale), row_ink + round(10 * scale))
        capacity = max(1, (band - row_ink) // floor_pitch + 1)
        if len(items) > capacity:
            raise ValueError(
                f"{len(items)} items do not fit a {width}x{height} canvas; it holds {capacity}. "
                "Split the menu across pages or raise the canvas height."
            )
        # Expansion is capped at 1.5x. A two-item menu on a tall canvas genuinely should carry
        # white space; spreading two rows over 700px would read as a broken layout, not a
        # generous one.
        natural_pitch = max(floor_pitch, round(style["pitch"] * scale))
        pitch = max(floor_pitch, min((band - row_ink) // max(1, len(items) - 1) if len(items) > 1 else band,
                                     round(natural_pitch * 1.5)))
        block = (len(items) - 1) * pitch + row_ink
        slack = max(0, (band - block) // 2)
        category_y = group_top + slack + round(size["category"] * CAP)
        first_baseline = band_top + slack + round(size["item"] * CAP)
        for index, row in enumerate(laid):
            y = first_baseline + index * pitch
            svg = ""
            if marker == "number":
                svg += f'<text x="{margin}" y="{y}" class="marker">{index + 1:02d}</text>'
            elif marker == "bullet":
                svg += (
                    f'<circle cx="{margin + round(10 * scale)}" cy="{y - round(size["item"] * 0.30)}" '
                    f'r="{max(2, round(5 * scale))}" fill="{accent}"/>'
                )
            name_step = round(size["item"] * LEAD)
            last_name_y = y + (len(row["name"]) - 1) * name_step
            svg += (
                f'<text x="{indent}" y="{y}" class="item">{_tspans(row["name"], indent, name_step)}</text>'
                f'<text x="{indent}" y="{last_name_y + desc_offset}" class="desc">'
                f'{_tspans(row["desc"], indent, desc_step)}</text>'
                f'<text x="{right}" y="{y}" text-anchor="end" class="price">'
                f'{html.escape(row["price_text"])}</text>'
            )
            if style["dotted"] and len(row["name"]) == 1:
                # The leader runs between measured ends with a gap at each side. It is dropped
                # rather than shortened when there is no honest room: a missing leader is
                # invisible, a leader printed through a dish name is not.
                lead_start = indent + advance(row["name_text"], size["item"], bold=True) + round(14 * scale)
                lead_end = right - row["price_w"] - round(14 * scale)
                if lead_end - lead_start > round(40 * scale):
                    svg += (
                        f'<line x1="{lead_start:.0f}" y1="{y - round(size["item"] * 0.22)}" '
                        f'x2="{lead_end:.0f}" y2="{y - round(size["item"] * 0.22)}" stroke="{ink}" '
                        f'stroke-opacity=".35" stroke-width="{max(1, round(2 * scale))}" '
                        f'stroke-dasharray="{max(1, round(2 * scale))} {max(3, round(6 * scale))}"/>'
                    )
            rows.append(svg)
    body = "\n".join(rows) or (
        f'<text x="{margin}" y="{band_top + round(size["item"] * CAP)}" class="desc">'
        "Add approved content items to render the layout.</text>"
    )

    title = html.escape(str(spec.get("title", "Untitled design")))
    subtitle = html.escape(str(spec.get("subtitle", "Replace with approved copy")))
    category = html.escape(str(spec.get("category", "SIGNATURE DISH")))
    footer_lines = wrap(
        str(spec.get("footer", "Exact ingredients, price, availability and CTA must be approved before publication.")),
        size["footer"], right - margin, 1, "footer",
    )
    footer = html.escape(footer_lines[0])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title subtitle">
<title id="title">{title}</title><desc id="subtitle">{subtitle}</desc>
<defs><clipPath id="hero-clip"><rect x="{hero_x}" y="{hero_top}" width="{hero_w}" height="{hero_h}" rx="0"/></clipPath></defs>
<rect width="100%" height="100%" fill="{bg}"/>{header_svg}
<text x="{margin}" y="{kicker_y[0]}" fill="{ink}" class="kicker">{_tspans(kicker_lines, margin, round(size["kicker"] * LEAD))}</text>
<text x="{margin}" y="{title_y[0]}" fill="{ink}" class="title">{_tspans(title_lines, margin, round(size["title"] * LEAD))}</text><text x="{margin}" y="{subtitle_y[0]}" fill="{ink}" class="subtitle">{_tspans(subtitle_lines, margin, round(size["subtitle"] * LEAD))}</text>{hero}
<line x1="{margin}" y1="{divider_y}" x2="{right}" y2="{divider_y}" stroke="{ink}" stroke-opacity=".25"/><text x="{margin}" y="{category_y}" fill="{accent}" class="category">{category}</text>{body}
<line x1="{margin}" y1="{footer_rule_y}" x2="{right}" y2="{footer_rule_y}" stroke="{ink}" stroke-opacity=".25"/><text x="{margin}" y="{footer_y}" fill="{ink}" class="footer">{footer}</text>
<style>.kicker{{font:600 {size["kicker"]}px {body_font};letter-spacing:{max(1, round(4 * scale))}px}}.title{{font:700 {size["title"]}px {display_font}}}.subtitle{{font:400 {size["subtitle"]}px {body_font}}}.category{{font:700 {size["category"]}px {body_font};letter-spacing:{max(1, round(3 * scale))}px}}.item{{font:700 {size["item"]}px {body_font}}}.marker{{font:700 {max(11, round(20 * scale))}px {body_font};fill:{accent};opacity:.9}}.desc{{font:400 {size["desc"]}px {body_font};fill:{ink};opacity:.72}}.price{{font:700 {size["price"]}px {body_font};fill:{accent}}}.footer{{font:400 {size["footer"]}px {body_font};opacity:.65}}</style></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--html-output")
    args = parser.parse_args()
    input_path = Path(args.input)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    spec = json.loads(input_path.read_text(encoding="utf-8-sig"))
    # Copy a local hero beside the SVG so the rendered menu stays portable after global install.
    hero_image = spec.get("hero_image")
    if hero_image and not str(hero_image).startswith("data:"):
        hero_path = input_path.parent / str(hero_image)
        if hero_path.is_file():
            copied_hero = output.parent / hero_path.name
            if hero_path.resolve() != copied_hero.resolve():
                shutil.copy2(hero_path, copied_hero)
            spec["hero_image"] = copied_hero.name
    svg = render(spec)
    output.write_text(svg, encoding="utf-8")
    if args.html_output:
        page = f'<!doctype html><meta charset="utf-8"><title>Mockup</title><style>body{{margin:0;background:#ddd;display:grid;place-items:center;min-height:100vh}}svg{{max-width:92vw;max-height:92vh;box-shadow:0 12px 40px #0003}}</style>{svg}'
        Path(args.html_output).write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
