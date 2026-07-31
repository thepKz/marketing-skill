# One photograph, many compositions: what is actually derivable

## What this unit is for

A shop owner has one usable photograph of their product. The listing needs ten frames, the feed needs
four more, and every tool on the market says the one photograph is enough now.

It is enough for some of them. This unit says which, by counting rather than by encouraging. Of the
eighteen slots in `data/product-compositions.csv`, seven come out of a single front-on exposure with
no conditions attached, three come out of it only if the source allows something specific, and eight
cannot come out of it at all. Not "come out worse". Cannot. The information is not in the file.

That is the whole argument. A front-on photograph does not contain the back of the pack, one unit does
not contain a bundle, and one colourway does not contain a range. Asking a model for them does not
fail loudly — it returns something plausible, and a plausible ingredient panel is a fabricated claim
with the shop's name on it.

## Running it

    python scripts/plan_composition_set.py --list-slots
    python scripts/plan_composition_set.py --set marketplace --source 3024x4032 --product-px 2600
    python scripts/plan_composition_set.py --set full --source 4000x6000 --product-px 3400 \
        --have back-exposure three-quarter-exposure
    python scripts/plan_composition_set.py --slots story-vertical grid-thumb --source 3024x4032 \
        --accept-upscale 1.3 --format json

`--source` is the pixel size of the file that exists. `--product-px` is how tall the product itself
stands inside it, which the user measures once. `--have` names additional exposures already taken,
using the values in the table's `needs_present` column. `--set` selects a bundle: `marketplace`,
`social`, `one-photo`, or `full`. Exit codes are 0 clean, 1 usage error, 2 a slot cannot be produced,
3 computable but unsettled.

## The seven derivations, and the line through them

Every slot names one derivation, and the seven are a fixed list. That fixed list is doing real work:
without it, "AI enhancement" enters as a derivation and stops distinguishing anything, which is the
exact failure this unit documents.

Five of them preserve the product's own pixels:

- `reframe` — crop or straighten inside the source. No new pixels anywhere.
- `relight` — exposure, white balance, local contrast. No new pixels, no new geometry.
- `outpaint` — extend the frame outward. New pixels only outside the silhouette.
- `background-swap` — replace behind the cutout. New pixels only outside the silhouette.
- `scene-rebuild` — place the cutout into a built environment, contact and spill rebuilt.

Two do not:

- `new-geometry` — needs a view of the product the source does not contain.
- `new-subject` — needs a person, a second unit or a second state the source does not contain.

The line between the two groups is the line between editing and inventing, and the generator enforces
it in both directions: a preserving derivation cannot be marked unobtainable, and a non-preserving one
cannot be marked obtainable. Neither cell can drift without the other one contradicting it.

## Reading the count honestly

Seven slots clear from one exposure with no conditions: `main-hero-white`, `main-hero-cleaned`,
`spec-callout`, `story-vertical`, `grid-thumb`, `banner-copy-field`, `hero-wide-web`. Notice what they
have in common. Every one of them is either a crop of what is already there or an extension of the
space around it. Nothing on that list asks the product to turn.

Three are conditional: `detail-macro` on whether real texture is resolved at the crop,
`in-use-context` and `flatlay-props` on whether the edge is cuttable and the light matchable.

Eight need a second exposure: `three-quarter`, `back-panel`, `top-down`, `scale-in-hand`,
`bundle-contents`, `variant-line-up`, `on-model`, `before-after`.

And separately from all of that, five of the eighteen are valid as a marketplace main image. Eight are
explicitly disallowed there. A composition being good is not the same as a composition being
submittable, and the two get conflated constantly — a spec callout with overlaid text is a strong
second image and an instant rejection as the first one, because on a main image any overlay counts as
a promotional element.

## Two constraints, reported separately

`scripts/plan_composition_set.py` computes the resample factor a slot demands and reports both causes
rather than the larger one, because they have different fixes.

The **frame** constraint is the largest crop at the slot's ratio that fits inside the source, against
the delivery size from `data/frame-ratios.csv`. Fix: shoot at higher resolution.

The **product-fill** constraint is how tall the product needs to stand in the delivered frame, against
how tall it stands in the source. Fix: move the camera closer.

A 3024x4032 phone photo with the product 2600 px tall passes both for a square hero at 0.357x and
0.34x. There is no upscale, and the frame constraint alone would have said the same. It is on other
slots that the two diverge, and reporting only the worst number would send the user to reshoot when
they needed to step forward.

## The macro that runs backwards, and why it was wrong first

`detail-macro` originally passed at 0.415x, and that verdict was wrong in a way worth recording,
because it is the error a reader would make with the same table in front of them.

A macro crops *into* the product. It shows fifteen percent of it. So the pixels available are fifteen
percent of the product's height, not all of it — 390 px of a 2600 px product — and those 390 px have
to deliver a 1080 px frame. The factor is 2.769x, and the slot fails. Treating `product_px` as fully
available made a material crop look cheaper than a full-product hero, which is precisely backwards: a
crop into the subject is the most source-hungry frame in the set, not the least.

The table carries `shows_pct_of_product` so this cannot be reasoned away, and the generator refuses any
row that crops into the product without declaring its condition as `pixels`. `detail-macro` is graded
`standard-requirement-with-house-threshold`: the fifteen percent is a house figure, and the rule that
the result must not be upscaled is not.

## Where the arithmetic stops

Three rows carry `condition_is` set to `judgement`, and for those the script returns `review` even when
the pixel check passes cleanly. `in-use-context` on a phone photo has more than enough pixels at
0.357x, and the pixels were never what decided it. What decides it is whether the silhouette can be
cut and whether the source's light direction can be matched by the room being built behind it, and no
resample factor answers either.

Returning `passed` there would be the script answering a question it did not ask. So the vocabulary is
the same four statuses this skill uses everywhere — `passed`, `failed`, `skipped` when the input was
never supplied, and `review` when the arithmetic ran and does not settle it — and for the same reason:

> `review` exists so that the gates that do fail mean something. A checker that returns a verdict on
> everything gets ignored on everything.

The report separates the two ways a slot lands in `review`, because they send the user to different
files. An accepted upscale is settled by looking at the delivered frame. An unsettled condition is
settled by looking at the source.

## The reshoot argument, as a count

`reshoot_value()` exists because of how this conversation actually goes. Told that additional images
improve conversion, a shop owner does nothing. Told that photographing the back of the box turns one
failing slot into a producible one, and naming which, they can decide.

The output lists each missing exposure against the slots it unlocks. On the marketplace set from one
front-on phone photo, six exposures each unlock exactly one slot — which is itself the finding. There
is no single cheap reshoot that rescues the set. Each frame costs its own exposure, and that is the
number to put next to the cost of the shoot.

## The metadata that is not optional

Google Merchant Center requires generated or substantially edited images to declare their provenance
in IPTC `DigitalSourceType`. Getting it wrong is a feed disapproval, not a style note, so the script
emits the QCode and the full vocabulary URI for every producible slot.

There is a trap in the primary source. Google names three codes. The IPTC vocabulary, fetched
2026-07-31 from `https://cv.iptc.org/newscodes/digitalsourcetype/`, has seventeen live concepts with
lowerCamelCase QCodes — and the one that actually describes editing a real photograph,
`compositeWithTrainedAlgorithmicMedia`, is not among Google's three. Every code in the table is
validated against the fetched vocabulary, so a plausible-looking invented code cannot enter it.

The generator also enforces the pairing in both directions: a slot whose derivation writes new pixels
must carry a composite code, and one that does not must not. A `reframe` declared as a composite is as
wrong as a `scene-rebuild` declared as a plain capture.

## The fill band, and what it is not

The percentages on the marketplace slots are not house taste. Google Merchant Center documents the
main product image occupying no less than 75 and no more than 90 percent of the frame, and the five
`allowed` rows that frame a whole product sit inside that band. Rows outside it are outside it because
the band does not apply to them, and each says so in `fails_when`.

`on-model` is the exception that looks like an error: 50 percent fill and still `allowed`, because for
worn goods a person in the main image is permitted. Its `fails_when` is the one that matters most in
this unit — a generated body gives the garment a fit it does not have, and that arrives back as a
return, not as a complaint about the photograph.

`before-after` is graded `house-rule` and its source column points somewhere else entirely, to
`claims-proof-ledger.md`. That frame is a claim wearing a composition's clothes. If the difference
between the two halves is the lighting, the composition is fine and the listing is false.

## What has no source

Shopee's own image specification could not be retrieved. What is available is third-party SEO writing
that contradicts itself — 600x600 against 500x500 against 1024x1024, 70 percent fill against 75 —
and not one of those numbers is in this table. The contradiction is recorded as `no-source-found`
rather than resolved by picking the most common figure, which would have produced a plausible number
with no provenance. For a Shopee listing, read the seller centre page at the time of upload; this unit
gives the general arithmetic and declines to guess the platform's current constant.

## Limits

The presence gate is only as good as `--have`. A user who claims an exposure they did not take gets a
clean pass on a frame they cannot produce, and nothing here detects that.

The pixel arithmetic assumes the source is genuinely sharp at full size. It measures resolution, not
focus. A 6000 px file with a soft subject passes every check in this script and fails on the shelf,
and the `lock` column on each row is what to inspect before shipping.

Nothing here judges whether the composition is any good. It judges whether it is derivable and whether
it is submittable. Load `composition-light-color.md` for the first question and this unit for the
second.
