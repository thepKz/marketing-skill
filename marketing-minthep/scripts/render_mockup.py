#!/usr/bin/env python3
"""Render a small, dependency-free SVG/HTML mockup from a design spec JSON file."""

from __future__ import annotations

import argparse
import html
import json
import textwrap
from pathlib import Path


def render(spec: dict) -> str:
    width = int(spec.get("width", 1080))
    height = int(spec.get("height", 1350))
    themes = {
        "quiet-editorial": ("#f3efe6", "#171717", "#b65f45", "Georgia", "Arial"),
        "modern-street": ("#f5f1e8", "#171717", "#df4b2e", "Arial", "Arial"),
        "heritage-craft": ("#e8ddc8", "#24362b", "#a85932", "Georgia", "Arial"),
    }
    theme = str(spec.get("theme", "quiet-editorial"))
    default_bg, default_ink, default_accent, display_font, body_font = themes.get(theme, themes["quiet-editorial"])
    bg = html.escape(str(spec.get("background", default_bg)))
    ink = html.escape(str(spec.get("ink", default_ink)))
    accent = html.escape(str(spec.get("accent", default_accent)))
    title = html.escape(str(spec.get("title", "Untitled design")))
    subtitle = html.escape(str(spec.get("subtitle", "Replace with approved copy")))
    subtitle_lines = textwrap.wrap(html.unescape(subtitle), width=48, break_long_words=False, break_on_hyphens=False)[:2] or [""]
    subtitle_svg = "".join(
        f'<tspan x="100" dy="{0 if index == 0 else 30}">{html.escape(line)}</tspan>'
        for index, line in enumerate(subtitle_lines)
    )
    items = spec.get("items", [])
    hero_href = spec.get("hero_image")
    hero = ""
    if hero_href:
        hero = f'<image href="{html.escape(str(hero_href), quote=True)}" x="690" y="110" width="290" height="270" preserveAspectRatio="xMidYMid slice" clip-path="url(#hero-clip)"/>'
    elif spec.get("hero_shape", "bowl") == "bowl":
        hero = '<ellipse cx="835" cy="230" rx="130" ry="62" fill="#231f20"/><ellipse cx="835" cy="214" rx="118" ry="47" fill="#a8432e"/><path d="M747 206 Q835 250 923 206" fill="none" stroke="#efc08a" stroke-width="8" stroke-linecap="round"/><path d="M770 185 Q835 155 900 185" fill="none" stroke="#f3d7b1" stroke-width="5" stroke-linecap="round" opacity=".8"/>'
    rows = []
    for index, item in enumerate(items[:12]):
        name = html.escape(str(item.get("name", "Item")))
        description = html.escape(str(item.get("description", "")))
        price = html.escape(str(item.get("price", "TBD")))
        y = 500 + index * 74
        rows.append(f'<text x="100" y="{y}" class="item">{name}</text><text x="100" y="{y+28}" class="desc">{description}</text><text x="980" y="{y}" text-anchor="end" class="price">{price}</text>')
    body = "\n".join(rows) or '<text x="100" y="530" class="desc">Add approved content items to render the layout.</text>'
    category = html.escape(str(spec.get("category", "SIGNATURE DISH")))
    footer = html.escape(str(spec.get("footer", "Exact ingredients, price, availability and CTA must be approved before publication.")))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title subtitle">
<title id="title">{title}</title><desc id="subtitle">{subtitle}</desc>
<defs><clipPath id="hero-clip"><rect x="690" y="110" width="290" height="270" rx="0"/></clipPath></defs>
<rect width="100%" height="100%" fill="{bg}"/><rect x="70" y="70" width="940" height="8" fill="{accent}"/>
<text x="100" y="150" fill="{ink}" class="kicker">{html.escape(str(spec.get("kicker", "MENU / CONCEPT")))}</text>
<text x="100" y="220" fill="{ink}" class="title">{title}</text><text x="100" y="260" fill="{ink}" class="subtitle">{subtitle_svg}</text>{hero}
<line x1="100" y1="420" x2="980" y2="420" stroke="{ink}" stroke-opacity=".25"/><text x="100" y="465" fill="{accent}" class="category">{category}</text>{body}
<line x1="100" y1="1280" x2="980" y2="1280" stroke="{ink}" stroke-opacity=".25"/><text x="100" y="1320" fill="{ink}" class="footer">{footer}</text>
<style>.kicker{{font:600 22px {body_font};letter-spacing:4px}}.title{{font:700 64px {display_font}}}.subtitle{{font:400 24px {body_font}}}.category{{font:700 20px {body_font};letter-spacing:3px}}.item{{font:700 28px {body_font}}}.desc{{font:400 19px {body_font};fill:{ink};opacity:.72}}.price{{font:700 26px {body_font};fill:{accent}}}.footer{{font:400 15px {body_font};opacity:.65}}</style></svg>'''


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
