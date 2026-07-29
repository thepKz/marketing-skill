# Bún bò — menu options, worked end to end

A single request ("I sell bún bò, I want a menu") turned into three design directions and three
rendered files, so you can see what the skill produces before trusting it with your own product.

## Run it

```bash
python ../../../scripts/plan_design_options.py --input request.json
python ../../../scripts/render_mockup.py --input menu-modern-street.json \
  --output out.svg --html-output out.html
```

`plan_design_options.py` returns the three directions and names one recommendation. Pick one,
then render it. The `--html-output` flag wraps the SVG in a page you can open in a browser.

## The three directions

They are the same four menu lines. Only the design direction changes — and it changes real
geometry, not just the palette. That distinction matters: three options that differed only in
colour would be one option wearing three hats.

| | Quiet editorial | Modern street | Heritage craft |
|---|---|---|---|
| Best for | Premium positioning, calm browsing | Fast scanning, phone and counter | Local provenance, printed menu |
| Side margin | 11.1% of width | 8.3% | 9.7% |
| Title size | 6.5% of width | 5.9% | 5.6% |
| Row pitch at 1080px | 82 | 70 | 78 |
| Top rule | Hairline | Heavy accent bar | Double rule |
| Row treatment | Nothing — decoration breaks the calm | `01` index, so a customer can order by number | Bullet plus a dotted leader to the price |
| Fails when | Proof and hierarchy are weak, and it reads sparse | Accents multiply and it turns noisy | The grid is loose and it reads old-fashioned |

Rendered output lives in `docs/assets/generated/bun-bo-menu-<direction>.svg`.

## Why every price is an em dash

Nobody told the skill what a bowl of bún bò costs at your shop. So it renders `—`, and the
footer says `CONCEPT LAYOUT / Không phải menu giá đã được duyệt` — this is a layout, not an
approved price list. The item descriptions say what is still missing rather than inventing a
plausible-sounding ingredient line.

This is the point of the example, not a limitation of it. A menu mockup with invented prices
looks finished, which is exactly what makes it dangerous: someone prints it. Fill in
`price` and `description` from your own menu, re-render, and the concept footer is the next
thing to replace.

## What the renderer will refuse

- More items than the canvas can hold. It raises and tells you the capacity instead of
  silently truncating the list, because a partial menu presented as a whole menu is a lie.
- A canvas under 480x480, which cannot carry legible type at any scale.

It will also quietly drop the dotted price leader when a dish name is long enough that the dots
would collide with it. A missing leader is invisible; a leader printed through a dish name is not.

## Not a photograph

`hero_shape: "bowl"` draws a schematic bowl — an ellipse, a broth disc, two garnish arcs. It is
deliberately a diagram. It stands in for a photo of *your* bowl that nobody has taken yet, and a
placeholder aiming at photorealism would invite someone to mistake it for the dish. When you have
a real photo, set `hero_image` to its path instead.
