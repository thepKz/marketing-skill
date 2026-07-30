# Identity and Layout Construction

## Contents

- What this unit is for
- The one-pixel rule
- The platform mask
- Optical centring is arithmetic
- Clearspace in mark-relative units
- The WCAG logotype exemption and why it is a trap
- Minimum size is measured, not declared
- Banner sets
- Type scale
- Delivery checklist

## What this unit is for

`brand-dna.md` records a visual grammar that already exists. `plan_design_options.py` chooses a
direction for a menu, poster, packshot or key visual. Neither one constructs a mark or a banner grid.
This unit does that, and it does it from arithmetic rather than taste, because almost every real
failure of a logo is a failure at a size nobody checked.

Look up `data/mark-scale-ladder.csv` for the slot sizes and their detail budgets. Use
`data/layout-dials.csv` for margin, type and accent ratios, and `data/composition-grids.csv` for
frame grids and the platform safe band. Do not restate the phi argument here; that table already
settles it.

## The one-pixel rule

A stroke narrower than one device pixel does not render as a thin line. It renders as a grey line, or
it disappears. So the smallest slot a mark must survive sets a hard floor on its thinnest stroke:

```text
minimum stroke, as a fraction of mark height  =  (floor in device pixels) / (slot in px)

floor = 1 px  at a slot rendered at its native size   (16, 32, 48)
floor = 2 px  at a slot the platform resamples         (180, 192, 400, 512)
```

At the 16 px favicon that is 1/16, or **6.25% of the mark's height**. A mark whose thinnest element is
a 2%-of-height hairline cannot exist at 16 px, and no amount of hinting fixes it — there is no pixel
to put it in. An enclosed counter needs roughly twice the stroke floor, because a one-pixel hole closes
under antialiasing, so **12.5% at 16 px** before a hole reads as a hole rather than a smudge.

The floor doubles at the large slots for a reason worth stating: nothing displays a 512 px icon at
512 px. Android, the store listing and the splash screen all resample it, and a stroke that was exactly
one pixel in the master lands on a fractional pixel after resampling and greys out. One device pixel is
the floor for a slot you control; two is the floor for a slot someone else scales.

The whole ladder is in the CSV. The consequence worth internalising: a 16 px slot contains 256 pixels
in total. Anything with more than about two distinct elements is being asked to encode itself in fewer
pixels than a single character of body text occupies. Serifs, gradients, inner shadows and two-tone
fills are all decisions to fail at that slot.

Design the mark at the largest slot, then **render it down and look**, at every slot, at 100%. Do not
judge a favicon by zooming into a 512 px master.

## The platform mask

Android and the PWA specification crop icons to a platform shape. The standardised safe zone is a
circular area centred in the icon **with a radius equal to 40% of the icon width**; the outer 10% edge
may be cropped on some platforms.

For a 512 px master that is a safe circle 409.6 px across. Two consequences:

- A mark composed to fill its square loses its corners. Compose to the inscribed circle.
- Do not pre-round corners for iOS. The OS applies its own mask, and a pre-rounded icon gets rounded
  twice, which reads as a smaller icon floating in a box.

Social avatars are the same problem without a specification: most platforms display a circle over a
square upload, so the usable area is the inscribed circle, about 78.5% of the square.

## Optical centring is arithmetic

Centring a mark inside a container by its bounding box is wrong whenever the mark's visual mass is
asymmetric, and the size of the error is computable rather than a matter of feel.

Take the standard case: a right-pointing triangle inside a circle, the play button. For a triangle
with a vertical base at the left edge and its apex at the right, in a box of width `w`:

```text
bounding-box centre   x = w / 2      = 50.0% of width
centroid of the mass  x = (0 + 0 + w) / 3 = 33.3% of width
```

Aligning the bounding box therefore places the visual mass **16.7% of the width to the right** of where
the eye expects it. That is why every play button in production is nudged left, and why the nudge is
not a preference. Align the centroid, then verify by eye; the arithmetic tells you which direction and
roughly how far, and the eye confirms.

The same correction applies to any wordmark whose first or last character is round or open — `O`, `C`,
`A`, `J` — because a curve's bounding box overstates its mass. Overshoot the round character slightly
past the alignment edge, exactly as a type designer does.

## Clearspace in mark-relative units

Clearspace stated in millimetres or pixels is wrong at every size except the one it was written for.
State it as a multiple of something measurable **inside the mark**: the cap height, the stroke width,
or the width of one counter.

```text
clearspace = 1 x cap height of the wordmark, on all four sides   (a workable default)
```

A rule expressed this way survives a business card and a building. Pick the element that is easiest
for a third party to measure without the source file, because that is who will be applying it.

## The WCAG logotype exemption and why it is a trap

WCAG 2.1 SC 1.4.3 requires a contrast ratio of at least 4.5:1 for text, and 3:1 for large-scale text,
where large scale is defined as at least 18 point, or 14 point bold. It then states, verbatim:

> Text that is part of a logo or brand name has no contrast requirement.

So a logo cannot fail SC 1.4.3. That is a statement about conformance, not about legibility, and three
things follow that people miss:

1. **Exempt is not legible.** WCAG's own note on large-scale text warns that fonts with extraordinarily
   thin strokes or unusual letterforms are harder to read, especially at lower contrast. The exemption
   removes the obligation, not the problem.
2. **The moment the mark becomes a control, the exemption stops covering it.** SC 1.4.11 Non-text
   Contrast requires 3:1 for visual information needed to identify user interface components and
   states. A logo that is also the home link, or that sits inside a button, brings its affordance under
   1.4.11 even though the logotype itself stays exempt.
3. **Tagline text beside a mark is usually not part of the logo.** If it is set as text and reads as a
   sentence, treat it as text and hold it to 4.5:1, or to 3:1 at 24 px regular / 18.66 px bold, which
   is what 18 pt and 14 pt bold come to at 96 dpi.

The safe posture: hold the mark to 3:1 against every background it is approved to sit on, by choice
rather than by requirement, and record the approved backgrounds in `BRAND.md`.

## Minimum size is measured, not declared

A minimum size copied from another brand's guideline is a guess. Derive it:

1. Render the mark at descending widths — 240, 160, 120, 80, 56, 40, 32, 24, 16 px.
2. View each at 100% at real distance. For print, print it; screen preview overstates print legibility.
3. Find the width at which the **weakest single element** fails: a counter closes, a stroke greys out,
   two shapes merge, a character becomes ambiguous.
4. The minimum is one step above that. Record which element failed and why, so a future revision knows
   what the constraint is protecting.

If the mark fails above the smallest slot it has to occupy, the mark is wrong for the system, not the
system wrong for the mark. That usually means a simplified variant is required — and a simplified
variant is a separate approved asset with its own minimum, not a licence to squash the primary.

## Banner sets

Build one master per aspect ratio, not one per pixel size. Sizes within a ratio are exports; ratios
are designs. A 300x250 and a 336x280 are both close to 6:5 and share a layout. A 728x90 is 8:1 and
shares nothing with either.

Per ratio, fix the reading order first, then let the dials carry the rest:

- Reserve the copy area before placing the image, using `copy_reserve` from `data/layout-dials.csv`.
  A reserve the image fills is not a reserve; verify on the render.
- Hold one accent, at the `accent_area` fraction for the positioning. Two accents in a 728x90 leaves
  nothing emphasised, because emphasis is a ratio.
- For 9:16 placements use the safe-band row in `data/composition-grids.csv`: compose the readable core
  to about 40% of frame height, not 50%.
- Never ask an image model to render final small type. Generate the plate, set the type in the layout.

Re-open the platform's own asset requirements before every flight. Accepted sizes and file limits
change without notice, which is why `data/market-data-sources.csv` carries the Google asset-requirement
page as a live lookup rather than a cached list of dimensions.

## Type scale

Pick one ratio and one body size, then derive every step; do not hand-pick sizes. `size_ratio` in
`data/layout-dials.csv` bounds the useful range at 1.6 to 4.5 from body to headline, and
`type_families` and `weight_steps` bound how many faces and weights may carry the hierarchy — one
family with a real weight range beats two families, and a third family reads as a filled-in template.

A derived scale is checkable by a third party and survives a new size being added later. A hand-picked
set of sizes has no rule to extend, so the next person adds a size that belongs to no system.

## Delivery checklist

- Mark renders correctly at every slot in `data/mark-scale-ladder.csv`, checked at 100%, not zoomed.
- Important content inside the 40%-radius safe circle for maskable and circular-crop contexts.
- No pre-rounded corners on the iOS asset.
- Clearspace stated as a multiple of an element inside the mark.
- Minimum size derived by the descending-render test, with the failing element recorded.
- Mark holds 3:1 against every approved background, and any tagline set as text holds 4.5:1.
- Logo-as-link affordance satisfies SC 1.4.11 at 3:1.
- One master per aspect ratio; exports derived, never upscaled.
- Final type set in the layout, never rendered by an image model.
