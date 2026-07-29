# Bún bò — one shop, worked end to end

A single request ("I sell bún bò, I want a menu") turned into three design directions and three
rendered files, so you can see what the skill produces before trusting it with your own product.
Two more files carry the same shop into photography and video.

## Run it

```bash
python ../../../scripts/plan_design_options.py --input request.json
python ../../../scripts/render_mockup.py --input menu-modern-street.json \
  --output out.svg --html-output out.html
python ../../../scripts/compile_prompt.py --input key-visual.json --provider generic
python ../../../scripts/plan_video_sequence.py --input video-sequence.json --format report
```

`plan_design_options.py` returns the three directions and names one recommendation. Pick one,
then render it. The `--html-output` flag wraps the SVG in a page you can open in a browser.

| File | What it is |
|---|---|
| `request.json` | The original request, in the words a shop owner would use |
| `menu-*.json` | The three design directions, ready to render |
| `key-visual.json` | One photography brief, compiled to a provider-ready prompt |
| `video-sequence.json` | Five shots for a 15s vertical, sequenced with carried continuity |

## The photography brief

`key-visual.json` is deliberately specific about material behaviour: translucent broth with fat
rings rather than opaque soup, noodles wet and separate rather than clumped, herbs cut and
slightly bruised rather than glossy. That is where food images stop looking generated. It reserves
the upper-left 45 percent of the frame as empty space and puts the stock pot on the other side,
because a reserved area that the scene description fills is a reserved area you cannot use.

It also asks for no text at all. The dish name and price go in during layout, after the price is
confirmed — a rendered price is an invented price.

## The video sequence

`video-sequence.json` describes the world once and lets each shot declare only what changes, so
the sequencer carries light direction, screen direction, hand, props and steam state forward by
itself. Run it with `--format prompts` for the per-shot prompts, `--format csv` for the shot list.
Break continuity and it refuses to emit anything, which is the point.

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
- A title, subtitle, dish name, description or footer that needs more lines than its block
  holds. The error names the field and the character budget. This used to be a silent trim: a
  158-character subtitle rendered as its first two lines, ending mid-clause on a comma.
- A canvas under 480x480, which cannot carry legible type at any scale.

Everything else is measured rather than guessed at. Type is placed by stacking real cap heights
and descenders down from the top margin, not at fractions of the canvas height, so a long title
cannot push the subtitle through the divider; and the title wraps inside the column beside the
hero rather than running under the bowl.

It will also quietly drop the dotted price leader when a dish name is long enough that the dots
would collide with it. A missing leader is invisible; a leader printed through a dish name is not.

## Not a photograph

`hero_shape: "bowl"` draws a schematic bowl — an ellipse, a broth disc, two garnish arcs. It is
deliberately a diagram. It stands in for a photo of *your* bowl that nobody has taken yet, and a
placeholder aiming at photorealism would invite someone to mistake it for the dish. When you have
a real photo, set `hero_image` to its path instead.
