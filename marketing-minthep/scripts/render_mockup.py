#!/usr/bin/env python3
"""Render a small, dependency-free SVG/HTML mockup from a design spec JSON file.

Layout is computed from width and height rather than hardcoded, so a spec that asks for a
1200x1600 poster or a 1080x1080 square gets a correct layout instead of a silently broken one.
The item band absorbs the slack: four dishes spread out, eleven tighten up, and a spec that
genuinely cannot fit raises instead of overprinting the footer.
"""

from __future__ import annotations

import argparse
import html
import json
import textwrap
from pathlib import Path

# Full stacks, not bare family names. A bare "Arial" falls back to an unpredictable default on
# any machine without it — including the Linux runners that build the handbook — which changes
# every metric the layout depends on. The fallbacks are chosen for Vietnamese diacritic coverage.
SANS = "Arial, 'Liberation Sans', 'DejaVu Sans', 'Noto Sans', sans-serif"
SERIF = "Georgia, 'Liberation Serif', 'DejaVu Serif', 'Noto Serif', serif"

# Below this the description line collides with the next item's name.
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


def _advance(text: str, size: float) -> float:
    """Estimate rendered width of a bold string, on purpose too high.

    Real metrics would need a font library, and the only consumer of this is the dotted price
    leader, where erring wide means the dots stop a little early and erring narrow means they
    print through a dish name. So the coefficient is set above any realistic average advance.
    """
    return len(text) * size * 0.62


def _bowl(cx: float, cy: float, radius: float, scale: float) -> str:
    """A schematic noodle bowl: vessel, broth, and two garnish arcs.

    It is deliberately a diagram, not an illustration. A placeholder that tried to look like a
    photograph would invite someone to mistake it for the dish, and the render is only ever
    standing in for a real photo that has not been taken yet.
    """
    rx = radius
    return (
        f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{rx * 0.477:.0f}" fill="#231f20"/>'
        f'<ellipse cx="{cx:.0f}" cy="{cy - rx * 0.123:.0f}" rx="{rx * 0.908:.0f}" '
        f'ry="{rx * 0.362:.0f}" fill="#a8432e"/>'
        f'<path d="M{cx - rx * 0.677:.0f} {cy - rx * 0.185:.0f} Q{cx:.0f} {cy + rx * 0.154:.0f} '
        f'{cx + rx * 0.677:.0f} {cy - rx * 0.185:.0f}" fill="none" stroke="#efc08a" '
        f'stroke-width="{max(2, round(8 * scale))}" stroke-linecap="round"/>'
        f'<path d="M{cx - rx * 0.5:.0f} {cy - rx * 0.346:.0f} Q{cx:.0f} {cy - rx * 0.577:.0f} '
        f'{cx + rx * 0.5:.0f} {cy - rx * 0.346:.0f}" fill="none" stroke="#f3d7b1" '
        f'stroke-width="{max(1, round(5 * scale))}" stroke-linecap="round" opacity=".8"/>'
    )


def render(spec: dict) -> str:
    width = int(spec.get("width", 1080))
    height = int(spec.get("height", 1350))
    if width < 480 or height < 480:
        raise ValueError(f"canvas {width}x{height} is too small to lay out; minimum is 480x480")
    style = THEMES.get(str(spec.get("theme", "quiet-editorial")), THEMES["quiet-editorial"])
    display_font, body_font = style["display"], style["body"]
    bg = html.escape(str(spec.get("background", style["bg"])))
    ink = html.escape(str(spec.get("ink", style["ink"])))
    accent = html.escape(str(spec.get("accent", style["accent"])))
    title_text = str(spec.get("title", "Untitled design"))
    title = html.escape(title_text)
    subtitle_text = str(spec.get("subtitle", "Replace with approved copy"))
    subtitle = html.escape(subtitle_text)

    # Geometry, all derived. `scale` keeps type and rule weights in proportion when the canvas
    # changes; vertical anchors are measured from the real edges so nothing lands off-canvas.
    scale = width / 1080
    margin = round(width * style["margin"])
    right = width - margin
    rule_weight = max(1, round(8 * scale))
    header_rule_y = round(height * 0.0519)
    kicker_y = round(height * 0.111)
    title_y = round(height * 0.163)
    subtitle_y = round(height * 0.193)
    subtitle_leading = round(30 * scale)
    divider_y = round(height * 0.311)
    category_y = round(height * 0.344)
    footer_rule_y = height - round(height * 0.0519)
    footer_y = height - round(height * 0.0222)

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

    measure = max(24, round(48 / max(scale, 0.4)))
    subtitle_lines = textwrap.wrap(
        subtitle_text, width=measure, break_long_words=False, break_on_hyphens=False
    )[:2] or [""]
    subtitle_svg = "".join(
        f'<tspan x="{margin}" dy="{0 if index == 0 else subtitle_leading}">{html.escape(line)}</tspan>'
        for index, line in enumerate(subtitle_lines)
    )

    items = list(spec.get("items", []))
    hero_x = round(width * 0.639)
    hero_y = round(height * 0.0815)
    hero_w = width - margin - hero_x
    hero_h = round(height * 0.2)
    hero_href = spec.get("hero_image")
    hero = ""
    if hero_href:
        hero = (
            f'<image href="{html.escape(str(hero_href), quote=True)}" x="{hero_x}" y="{hero_y}" '
            f'width="{hero_w}" height="{hero_h}" preserveAspectRatio="xMidYMid slice" '
            f'clip-path="url(#hero-clip)"/>'
        )
    elif spec.get("hero_shape", "bowl") == "bowl":
        hero = _bowl(hero_x + hero_w / 2, hero_y + hero_h * 0.44, hero_w / 2, scale)

    # The item band is the only elastic part of the layout. Rows get their natural pitch when
    # there is room and compress toward MIN_ROW_PITCH when there is not, which is what removes
    # the dead space a short menu used to leave above the footer.
    band_top = category_y + round(35 * scale)
    band_bottom = footer_rule_y - round(30 * scale)
    band = band_bottom - band_top
    rows = []
    if items:
        natural_pitch = round(style["pitch"] * scale)
        floor_pitch = round(MIN_ROW_PITCH * scale)
        capacity = max(1, band // floor_pitch)
        if len(items) > capacity:
            raise ValueError(
                f"{len(items)} items do not fit a {width}x{height} canvas; it holds {capacity}. "
                "Split the menu across pages or raise the canvas height."
            )
        # Expansion is capped at 1.5x. A two-item menu on a tall canvas genuinely should carry
        # white space; spreading two rows over 700px would read as a broken layout, not a
        # generous one. So absorb slack up to a point and leave the rest deliberate.
        pitch = max(floor_pitch, min(band // len(items), round(natural_pitch * 1.5)))
        desc_offset = round(28 * scale)
        marker = style["marker"]
        # A marker shifts the text block right, so the description has to move with it or the two
        # lines stop reading as one row.
        indent = margin + (round(46 * scale) if marker != "none" else 0)
        item_size = max(14, round(28 * scale))
        price_size = max(13, round(26 * scale))
        for index, item in enumerate(items):
            name_text = str(item.get("name", "Item"))
            name = html.escape(name_text)
            description = html.escape(str(item.get("description", "")))
            price_text = str(item.get("price", "TBD"))
            price = html.escape(price_text)
            y = band_top + round(35 * scale) + index * pitch
            row = ""
            if marker == "number":
                row += (
                    f'<text x="{margin}" y="{y}" class="marker">{index + 1:02d}</text>'
                )
            elif marker == "bullet":
                row += (
                    f'<circle cx="{margin + round(10 * scale)}" cy="{y - round(9 * scale)}" '
                    f'r="{max(2, round(5 * scale))}" fill="{accent}"/>'
                )
            row += (
                f'<text x="{indent}" y="{y}" class="item">{name}</text>'
                f'<text x="{indent}" y="{y + desc_offset}" class="desc">{description}</text>'
                f'<text x="{right}" y="{y}" text-anchor="end" class="price">{price}</text>'
            )
            if style["dotted"]:
                # There are no font metrics available here, so the ends of the leader are
                # estimated from an average advance width, deliberately over-estimated so the
                # dots stop short rather than running under the text. If the estimate leaves no
                # room at all, the leader is dropped — a missing leader is invisible, a leader
                # printed through a dish name is not.
                lead_start = indent + _advance(name_text, item_size) + round(14 * scale)
                lead_end = right - _advance(price_text, price_size) - round(14 * scale)
                if lead_end - lead_start > round(40 * scale):
                    row += (
                        f'<line x1="{lead_start:.0f}" y1="{y - round(6 * scale)}" '
                        f'x2="{lead_end:.0f}" y2="{y - round(6 * scale)}" stroke="{ink}" '
                        f'stroke-opacity=".35" stroke-width="{max(1, round(2 * scale))}" '
                        f'stroke-dasharray="{max(1, round(2 * scale))} {max(3, round(6 * scale))}"/>'
                    )
            rows.append(row)
    body = "\n".join(rows) or (
        f'<text x="{margin}" y="{band_top + round(35 * scale)}" class="desc">'
        "Add approved content items to render the layout.</text>"
    )
    category = html.escape(str(spec.get("category", "SIGNATURE DISH")))
    footer = html.escape(str(spec.get("footer", "Exact ingredients, price, availability and CTA must be approved before publication.")))
    kicker = html.escape(str(spec.get("kicker", "MENU / CONCEPT")))
    type_scale = {
        "kicker": max(11, round(22 * scale)),
        "title": max(24, round(width * style["title"])),
        "subtitle": max(12, round(24 * scale)),
        "category": max(10, round(20 * scale)),
        "item": max(14, round(28 * scale)),
        "desc": max(10, round(19 * scale)),
        "price": max(13, round(26 * scale)),
        "footer": max(9, round(15 * scale)),
    }
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title subtitle">
<title id="title">{title}</title><desc id="subtitle">{subtitle}</desc>
<defs><clipPath id="hero-clip"><rect x="{hero_x}" y="{hero_y}" width="{hero_w}" height="{hero_h}" rx="0"/></clipPath></defs>
<rect width="100%" height="100%" fill="{bg}"/>{header_svg}
<text x="{margin}" y="{kicker_y}" fill="{ink}" class="kicker">{kicker}</text>
<text x="{margin}" y="{title_y}" fill="{ink}" class="title">{title}</text><text x="{margin}" y="{subtitle_y}" fill="{ink}" class="subtitle">{subtitle_svg}</text>{hero}
<line x1="{margin}" y1="{divider_y}" x2="{right}" y2="{divider_y}" stroke="{ink}" stroke-opacity=".25"/><text x="{margin}" y="{category_y}" fill="{accent}" class="category">{category}</text>{body}
<line x1="{margin}" y1="{footer_rule_y}" x2="{right}" y2="{footer_rule_y}" stroke="{ink}" stroke-opacity=".25"/><text x="{margin}" y="{footer_y}" fill="{ink}" class="footer">{footer}</text>
<style>.kicker{{font:600 {type_scale["kicker"]}px {body_font};letter-spacing:{max(1, round(4 * scale))}px}}.title{{font:700 {type_scale["title"]}px {display_font}}}.subtitle{{font:400 {type_scale["subtitle"]}px {body_font}}}.category{{font:700 {type_scale["category"]}px {body_font};letter-spacing:{max(1, round(3 * scale))}px}}.item{{font:700 {type_scale["item"]}px {body_font}}}.marker{{font:700 {max(11, round(20 * scale))}px {body_font};fill:{accent};opacity:.9}}.desc{{font:400 {type_scale["desc"]}px {body_font};fill:{ink};opacity:.72}}.price{{font:700 {type_scale["price"]}px {body_font};fill:{accent}}}.footer{{font:400 {type_scale["footer"]}px {body_font};opacity:.65}}</style></svg>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--html-output")
    args = parser.parse_args()
    svg = render(json.loads(Path(args.input).read_text(encoding="utf-8-sig")))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    if args.html_output:
        page = f'<!doctype html><meta charset="utf-8"><title>Mockup</title><style>body{{margin:0;background:#ddd;display:grid;place-items:center;min-height:100vh}}svg{{max-width:92vw;max-height:92vh;box-shadow:0 12px 40px #0003}}</style>{svg}'
        Path(args.html_output).write_text(page, encoding="utf-8")


if __name__ == "__main__":
    main()
