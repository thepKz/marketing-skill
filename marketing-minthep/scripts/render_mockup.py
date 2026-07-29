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
    themes = {
        "quiet-editorial": ("#f3efe6", "#171717", "#b65f45", SERIF, SANS),
        "modern-street": ("#f5f1e8", "#171717", "#df4b2e", SANS, SANS),
        "heritage-craft": ("#e8ddc8", "#24362b", "#a85932", SERIF, SANS),
    }
    theme = str(spec.get("theme", "quiet-editorial"))
    default_bg, default_ink, default_accent, display_font, body_font = themes.get(theme, themes["quiet-editorial"])
    bg = html.escape(str(spec.get("background", default_bg)))
    ink = html.escape(str(spec.get("ink", default_ink)))
    accent = html.escape(str(spec.get("accent", default_accent)))
    title_text = str(spec.get("title", "Untitled design"))
    title = html.escape(title_text)
    subtitle_text = str(spec.get("subtitle", "Replace with approved copy"))
    subtitle = html.escape(subtitle_text)

    # Geometry, all derived. `scale` keeps type and rule weights in proportion when the canvas
    # changes; vertical anchors are measured from the real edges so nothing lands off-canvas.
    scale = width / 1080
    margin = round(width * 0.0926)
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
        natural_pitch = round(74 * scale)
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
        for index, item in enumerate(items):
            name = html.escape(str(item.get("name", "Item")))
            description = html.escape(str(item.get("description", "")))
            price = html.escape(str(item.get("price", "TBD")))
            y = band_top + round(35 * scale) + index * pitch
            rows.append(
                f'<text x="{margin}" y="{y}" class="item">{name}</text>'
                f'<text x="{margin}" y="{y + desc_offset}" class="desc">{description}</text>'
                f'<text x="{right}" y="{y}" text-anchor="end" class="price">{price}</text>'
            )
    body = "\n".join(rows) or (
        f'<text x="{margin}" y="{band_top + round(35 * scale)}" class="desc">'
        "Add approved content items to render the layout.</text>"
    )
    category = html.escape(str(spec.get("category", "SIGNATURE DISH")))
    footer = html.escape(str(spec.get("footer", "Exact ingredients, price, availability and CTA must be approved before publication.")))
    kicker = html.escape(str(spec.get("kicker", "MENU / CONCEPT")))
    type_scale = {
        "kicker": max(11, round(22 * scale)),
        "title": max(24, round(64 * scale)),
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
<rect width="100%" height="100%" fill="{bg}"/><rect x="{round(width * 0.0648)}" y="{header_rule_y}" width="{width - 2 * round(width * 0.0648)}" height="{rule_weight}" fill="{accent}"/>
<text x="{margin}" y="{kicker_y}" fill="{ink}" class="kicker">{kicker}</text>
<text x="{margin}" y="{title_y}" fill="{ink}" class="title">{title}</text><text x="{margin}" y="{subtitle_y}" fill="{ink}" class="subtitle">{subtitle_svg}</text>{hero}
<line x1="{margin}" y1="{divider_y}" x2="{right}" y2="{divider_y}" stroke="{ink}" stroke-opacity=".25"/><text x="{margin}" y="{category_y}" fill="{accent}" class="category">{category}</text>{body}
<line x1="{margin}" y1="{footer_rule_y}" x2="{right}" y2="{footer_rule_y}" stroke="{ink}" stroke-opacity=".25"/><text x="{margin}" y="{footer_y}" fill="{ink}" class="footer">{footer}</text>
<style>.kicker{{font:600 {type_scale["kicker"]}px {body_font};letter-spacing:{max(1, round(4 * scale))}px}}.title{{font:700 {type_scale["title"]}px {display_font}}}.subtitle{{font:400 {type_scale["subtitle"]}px {body_font}}}.category{{font:700 {type_scale["category"]}px {body_font};letter-spacing:{max(1, round(3 * scale))}px}}.item{{font:700 {type_scale["item"]}px {body_font}}}.desc{{font:400 {type_scale["desc"]}px {body_font};fill:{ink};opacity:.72}}.price{{font:700 {type_scale["price"]}px {body_font};fill:{accent}}}.footer{{font:400 {type_scale["footer"]}px {body_font};opacity:.65}}</style></svg>'''


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
