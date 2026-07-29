#!/usr/bin/env python3
"""Render a small, dependency-free SVG/HTML mockup from a design spec JSON file."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def render(spec: dict) -> str:
    width = int(spec.get("width", 1080))
    height = int(spec.get("height", 1350))
    bg = html.escape(str(spec.get("background", "#f3efe6")))
    ink = html.escape(str(spec.get("ink", "#171717")))
    accent = html.escape(str(spec.get("accent", "#d9553d")))
    title = html.escape(str(spec.get("title", "Untitled design")))
    subtitle = html.escape(str(spec.get("subtitle", "Replace with approved copy")))
    items = spec.get("items", [])
    rows = []
    for index, item in enumerate(items[:12]):
        name = html.escape(str(item.get("name", "Item")))
        description = html.escape(str(item.get("description", "")))
        price = html.escape(str(item.get("price", "TBD")))
        y = 310 + index * 74
        rows.append(f'<text x="100" y="{y}" class="item">{name}</text><text x="100" y="{y+28}" class="desc">{description}</text><text x="980" y="{y}" text-anchor="end" class="price">{price}</text>')
    body = "\n".join(rows) or '<text x="100" y="340" class="desc">Add approved content items to render the layout.</text>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title subtitle">
<title id="title">{title}</title><desc id="subtitle">{subtitle}</desc>
<rect width="100%" height="100%" fill="{bg}"/><rect x="70" y="70" width="940" height="8" fill="{accent}"/>
<text x="100" y="150" fill="{ink}" class="kicker">{html.escape(str(spec.get("kicker", "MENU / CONCEPT")))}</text>
<text x="100" y="220" fill="{ink}" class="title">{title}</text><text x="100" y="260" fill="{ink}" class="subtitle">{subtitle}</text>
<line x1="100" y1="290" x2="980" y2="290" stroke="{ink}" stroke-opacity=".25"/>{body}
<style>.kicker{{font:600 22px Arial;letter-spacing:4px}}.title{{font:700 64px Georgia}}.subtitle{{font:400 24px Arial}}.item{{font:700 28px Arial}}.desc{{font:400 19px Arial;fill:{ink};opacity:.72}}.price{{font:700 26px Arial;fill:{accent}}}</style></svg>'''


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
