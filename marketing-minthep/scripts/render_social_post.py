#!/usr/bin/env python3
"""Render a real social post — image plus caption sheet — from a spec JSON file.

The menu renderer next door proves a layout can be measured rather than guessed at, so this
reuses its whole metric engine (`advance`, `wrap`, the CAP/DROP/LEAD stack, the three themes)
instead of starting a second, differently-wrong one. What is new here is the part of a post that
is not the picture:

  * Platform chrome. A story is 1080x1920 but the top 250px carries the avatar row and the bottom
    420px carries the reply field and the link sticker. Copy placed there is not "close to the
    edge", it is behind a button. Each placement declares its reserved bands and every baseline is
    flowed inside what is left, so the CTA cannot end up under the send box.
  * A caption is a deliverable, not an afterthought. `--caption-output` writes the caption, the
    hashtags, the alt text and the disclosure line as a sheet a human can paste, and any of those
    the spec did not state comes out as `UNKNOWN` with the reason — never as filler. An invented
    caption is the same failure as an invented price: it looks finished, so someone posts it.

Copy that does not fit raises and names the field, inherited from `wrap`. The block that would
collide with the CTA raises too, with the overflow in pixels, because a post whose headline runs
through its own button is worse than a post that was never rendered.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from _emit import emit, use_utf8_stdout
from render_mockup import CAP, DROP, LEAD, THEMES, _bowl, _tspans, advance, wrap

# Reserved bands are platform chrome measured at 1080 wide, scaled with the canvas. `feed-square`
# and `feed-portrait` reserve nothing at the top because the caption sits outside the image; a
# story reserves both ends because the app draws over them.
PLACEMENTS = {
    "feed-square": {"width": 1080, "height": 1080, "safe_top": 0, "safe_bottom": 0, "hero": 0.40},
    "feed-portrait": {"width": 1080, "height": 1350, "safe_top": 0, "safe_bottom": 0, "hero": 0.44},
    "story": {"width": 1080, "height": 1920, "safe_top": 250, "safe_bottom": 420, "hero": 0.46},
}

# What a caption sheet has to carry, and what each line means when nobody supplied it. The reason
# is printed beside the UNKNOWN so the gap is actionable rather than decorative.
CAPTION_FIELDS = (
    ("caption_vi", "Caption (VI)", "nobody wrote the Vietnamese caption; do not translate the EN one and call it approved copy"),
    ("caption_en", "Caption (EN)", "nobody wrote the English caption"),
    ("hashtags", "Hashtags", "no tag set was approved; invented tags reach the wrong audience"),
    ("alt_vi", "Alt text (VI)", "alt text describes what is actually in the frame, so it cannot be written before the photo exists"),
    ("alt_en", "Alt text (EN)", "same as above"),
    ("disclosure", "Disclosure", "state #ad / #tài_trợ / none-required and who decided"),
)


def _chip(x: float, y: float, w: float, h: float, label: str, size: float, accent: str, bg: str, font: str) -> str:
    """A CTA button sized to its own label, with the label centred on the measured cap height."""
    radius = h / 2
    return (
        f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{radius:.0f}" fill="{accent}"/>'
        f'<text x="{x + w / 2:.0f}" y="{y + h / 2 + size * CAP / 2:.0f}" text-anchor="middle" '
        f'fill="{bg}" style="font:700 {size:.0f}px {font};letter-spacing:{max(1, round(size * 0.06)):.0f}px">'
        f'{html.escape(label)}</text>'
    )


def render(spec: dict) -> str:
    name = str(spec.get("placement", "feed-portrait"))
    if name not in PLACEMENTS:
        raise ValueError(f"placement {name!r} is not one of {', '.join(PLACEMENTS)}")
    place = PLACEMENTS[name]
    width, height = int(place["width"]), int(place["height"])
    scale = width / 1080
    safe_top = round(place["safe_top"] * scale)
    safe_bottom = round(place["safe_bottom"] * scale)

    style = THEMES.get(str(spec.get("theme", "modern-street")), THEMES["modern-street"])
    display_font, body_font = style["display"], style["body"]
    bg = html.escape(str(spec.get("background", style["bg"])))
    ink = html.escape(str(spec.get("ink", style["ink"])))
    accent = html.escape(str(spec.get("accent", style["accent"])))
    margin = round(width * style["margin"])
    right = width - margin
    column = right - margin

    size = {
        "kicker": max(12, round(24 * scale)),
        "headline": max(30, round(width * style["title"] * 1.10)),
        "subhead": max(14, round(30 * scale)),
        "proof": max(13, round(27 * scale)),
        "cta": max(14, round(30 * scale)),
        "offer": max(11, round(21 * scale)),
        "footer": max(10, round(17 * scale)),
    }

    # The hero is full-bleed and claimed first, for the same reason the menu claims its bowl
    # first: the type has to be told where it may not go.
    share = float(spec.get("hero_share", place["hero"]))
    if not 0.20 <= share <= 0.58:
        raise ValueError(f"hero_share {share} leaves either no picture or no copy; keep it in 0.20-0.58")
    hero_h = round((height - safe_top - safe_bottom) * share)
    hero_href = spec.get("hero_image")
    if hero_href:
        hero = (
            f'<image href="{html.escape(str(hero_href), quote=True)}" x="0" y="{safe_top}" '
            f'width="{width}" height="{hero_h}" preserveAspectRatio="xMidYMid slice"/>'
        )
    else:
        # The placeholder gets a near-square box centred in the band, not the whole band. Handed
        # the full 900x430 of a feed hero the bowl draws an 810px rim over a 100px wall, which is
        # the flat-disc failure `_bowl` was rewritten to avoid — it just arrives from the caller
        # instead of from inside.
        box_w = min(column, round(hero_h * 0.95))
        box_h = round(hero_h * 0.72)
        hero = (
            f'<rect x="0" y="{safe_top}" width="{width}" height="{hero_h}" fill="#e7e1d4"/>'
            + _bowl((width - box_w) / 2, safe_top + (hero_h - box_h) / 2, box_w, box_h, scale)
        )

    # Bottom-up, so the footer and the button sit where the platform leaves room rather than where
    # the copy happens to end.
    footer_y = height - safe_bottom - round(30 * scale)
    footer_rule_y = footer_y - round(size["footer"] * CAP + 22 * scale)
    cta_label = str(spec.get("cta", "Xem menu"))
    cta_h = round(size["cta"] * (CAP + DROP) + 34 * scale)
    cta_w = round(advance(cta_label, size["cta"], bold=True) + size["cta"] * 0.06 * len(cta_label) + 56 * scale)
    cta_top = footer_rule_y - round(30 * scale) - cta_h
    if cta_w > column:
        raise ValueError(f"CTA {cta_label!r} is {cta_w}px wide and the column is {column}px; shorten it")

    text_top = float(safe_top + hero_h + round(48 * scale))

    def flow(cursor: float, lines: list[str], point: float, air: float) -> tuple[list[int], float]:
        first = cursor + point * (air + CAP)
        baselines = [round(first + index * point * LEAD) for index in range(len(lines))]
        return baselines, baselines[-1] + point * DROP

    kicker_lines = wrap(str(spec.get("kicker", "POST / CONCEPT")), size["kicker"], column, 1, "kicker", bold=True)
    headline_lines = wrap(str(spec.get("headline", "Untitled post")), size["headline"], column, 3, "headline", bold=True)
    subhead_lines = wrap(str(spec.get("subhead", "Replace with approved copy")), size["subhead"], column, 3, "subhead")

    cursor = text_top
    kicker_y, cursor = flow(cursor, kicker_lines, size["kicker"], 0.0)
    headline_y, cursor = flow(cursor, headline_lines, size["headline"], 0.46)
    subhead_y, cursor = flow(cursor, subhead_lines, size["subhead"], 0.66)

    # Proof lines are the part a generated post usually fabricates, so they are rendered exactly as
    # given and nothing is added to round the list up to three.
    proofs = [str(entry) for entry in spec.get("proof", [])][:3]
    proof_indent = margin + round(34 * scale)
    laid_proofs: list[tuple[list[str], list[int]]] = []
    for index, text in enumerate(proofs):
        lines = wrap(text, size["proof"], right - proof_indent, 2, f"proof {index + 1}")
        baselines, cursor = flow(cursor, lines, size["proof"], 0.80 if index == 0 else 0.62)
        laid_proofs.append((lines, baselines))

    offer = str(spec.get("offer", "")).strip()
    offer_svg = ""
    if offer:
        offer_x = margin + cta_w + round(26 * scale)
        offer_lines = wrap(offer, size["offer"], right - offer_x, 2, "offer")
        step = round(size["offer"] * LEAD)
        first = cta_top + cta_h / 2 - (len(offer_lines) - 1) * step / 2 + size["offer"] * CAP / 2
        offer_svg = (
            f'<text x="{offer_x}" y="{first:.0f}" fill="{ink}" class="offer">'
            f'{_tspans(offer_lines, offer_x, step)}</text>'
        )

    headroom = cta_top - round(30 * scale)
    if cursor > headroom:
        raise ValueError(
            f"the copy block ends {round(cursor - headroom)}px below where the CTA starts on "
            f"{name}; cut a proof line, shorten the headline, or lower hero_share"
        )

    # A story reserves 420px at the bottom for app chrome, so a two-proof post left the copy
    # hugging the hero with a hand's width of nothing above the button. The block is measured
    # first and then centred in the space it actually has, capped so a very short post does not
    # drift into the middle of the card and detach from the picture.
    slack = min(round((headroom - cursor) / 2), round(90 * scale))
    if slack > 0:
        kicker_y = [value + slack for value in kicker_y]
        headline_y = [value + slack for value in headline_y]
        subhead_y = [value + slack for value in subhead_y]
        laid_proofs = [(lines, [value + slack for value in bases]) for lines, bases in laid_proofs]

    mark = round(size["proof"] * 0.30)
    proof_svg = [
        f'<rect x="{margin}" y="{bases[0] - mark:.0f}" width="{mark}" height="{mark}" fill="{accent}"/>'
        f'<text x="{proof_indent}" y="{bases[0]}" fill="{ink}" class="proof">'
        f'{_tspans(lines, proof_indent, round(size["proof"] * LEAD))}</text>'
        for lines, bases in laid_proofs
    ]

    footer_lines = wrap(
        str(spec.get("footer", "CONCEPT POST / claims, price and offer must be approved before publication.")),
        size["footer"], column, 1, "footer",
    )
    letter = max(1, round(4 * scale))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="post-title post-desc">
<title id="post-title">{html.escape(str(spec.get("headline", "Untitled post")))}</title>
<desc id="post-desc">{html.escape(str(spec.get("alt_en") or spec.get("subhead", "Concept social post layout")))}</desc>
<rect width="100%" height="100%" fill="{bg}"/>{hero}
<text x="{margin}" y="{kicker_y[0]}" fill="{accent}" class="kicker">{_tspans(kicker_lines, margin, round(size["kicker"] * LEAD))}</text>
<text x="{margin}" y="{headline_y[0]}" fill="{ink}" class="headline">{_tspans(headline_lines, margin, round(size["headline"] * LEAD))}</text>
<text x="{margin}" y="{subhead_y[0]}" fill="{ink}" class="subhead">{_tspans(subhead_lines, margin, round(size["subhead"] * LEAD))}</text>
{"".join(proof_svg)}
{_chip(margin, cta_top, cta_w, cta_h, cta_label, size["cta"], accent, bg, body_font)}{offer_svg}
<line x1="{margin}" y1="{footer_rule_y}" x2="{right}" y2="{footer_rule_y}" stroke="{ink}" stroke-opacity=".25"/>
<text x="{margin}" y="{footer_y}" fill="{ink}" class="footer">{html.escape(footer_lines[0])}</text>
<style>.kicker{{font:700 {size["kicker"]}px {body_font};letter-spacing:{letter}px}}.headline{{font:700 {size["headline"]}px {display_font}}}.subhead{{font:400 {size["subhead"]}px {body_font};opacity:.82}}.proof{{font:400 {size["proof"]}px {body_font};opacity:.86}}.offer{{font:600 {size["offer"]}px {body_font};opacity:.78}}.footer{{font:400 {size["footer"]}px {body_font};opacity:.6}}</style></svg>'''


def caption_sheet(spec: dict) -> str:
    """The paste-ready half of the post. Absent fields are named, not filled."""
    lines = [
        f"# {spec.get('headline', 'Untitled post')}",
        "",
        f"- Placement: `{spec.get('placement', 'feed-portrait')}` · Theme: `{spec.get('theme', 'modern-street')}`",
        f"- CTA on image: {spec.get('cta', 'UNKNOWN')}",
        "",
    ]
    for key, label, reason in CAPTION_FIELDS:
        value = spec.get(key)
        if isinstance(value, list):
            value = " ".join(str(item) for item in value)
        value = str(value or "").strip()
        lines.append(f"## {label}")
        lines.append(value if value else f"UNKNOWN — {reason}")
        lines.append("")
    lines.append("## Before posting")
    lines.append("Every UNKNOWN above is a blocker, not a placeholder. Replace each one with copy a")
    lines.append("person approved, then check the claim in each proof line against a source you can name.")
    return "\n".join(lines) + "\n"


def main() -> None:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True, help="SVG path")
    parser.add_argument("--html-output", help="wrap the SVG in a page you can open in a browser")
    parser.add_argument("--caption-output", help="markdown caption, hashtag, alt-text and disclosure sheet")
    args = parser.parse_args()
    spec = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    svg = render(spec)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    if args.html_output:
        page = (
            '<!doctype html><meta charset="utf-8"><title>Post</title><style>body{margin:0;'
            "background:#ddd;display:grid;place-items:center;min-height:100vh}svg{max-width:92vw;"
            "max-height:92vh;box-shadow:0 12px 40px #0003}</style>" + svg
        )
        Path(args.html_output).write_text(page, encoding="utf-8")
    if args.caption_output:
        emit(caption_sheet(spec), args.caption_output)
    print(f"post: {output} ({spec.get('placement', 'feed-portrait')})")


if __name__ == "__main__":
    main()
