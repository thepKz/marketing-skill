# Reading a Reference

## Contents

- What this unit is for
- The line that actually matters
- The seven-question pass
- A pose has a job
- Height beats size
- Scale inversion
- Curated candour
- Environmental typography
- The light sets the makeup contrast, not the taste
- What a finished photograph cannot tell you
- Recording protocol

## What this unit is for

`source-map.md` says where to look. It lists four profiles as discovery indexes and then stops, with a
line reserving the right to make claims only against a specific post. This unit is the other half: what
to write down once you are looking, and what must never end up in the repository.

The observations live in `data/reference-observations.csv`, one row per post actually opened, with the
post URL as the citation. Cross-reference `data/makeup-looks.csv` for look identification,
`data/composition-grids.csv` for frame geometry and the platform safe band, and
`data/layout-dials.csv` for the margin and accent ratios a derived layout has to respect.

## The line that actually matters

Labelling a photograph does not license it. A credit line is an acknowledgement, not permission, and the
skill already learned this the expensive way: seventeen files were deleted from `docs/` because the
stated terms turned out to be a disclaimer.

But the thing worth taking from a reference is not the file. It is the measurement:

| Not protected — record it freely | Protected — never store or republish |
|---|---|
| Pose geometry: angles, weight distribution, rotation | The photograph, the crop, the frame as shot |
| Light direction, quality, ratio | The retouched file, at any resolution |
| Colour and palette structure, temperature | The subject's face and identity |
| Makeup placement and product category | The specific garment or campaign artwork |
| Framing ratio, subject scale, placement | A recognisable recreation of one image |

So the working rule is: **view, measure, write the measurement, store no image.** A URL in a data table
is a citation. A downloaded JPEG in `docs/assets/` is a publication, which is why
`test_every_reference_image_has_a_licence_line` exists and why nothing in this unit trips it.

The failure this prevents is not legal pedantry. An observation table survives a reference going private,
being deleted, or being relicensed; a folder of scraped files does not, and the day it breaks you have
lost the reasoning too.

## The seven-question pass

Ask the same seven questions of every reference, in this order. The order matters: the answers get harder
to fake as you go down, so a reference that stops producing answers halfway is a reference you were
admiring rather than reading.

1. **Frame.** Ratio, and whether the delivered ratio is the shot ratio. A letterboxed strip inside a
   square canvas is a decision.
2. **Subject scale.** What share of frame height the figure occupies. Write the number.
3. **Placement.** Where the figure sits, and what the vacated area is doing.
4. **Camera height.** Eye, chest, overhead. This is the single fact most people never record and the one
   that most reliably reproduces the reference.
5. **Pose geometry, and what the pose is for.** Two answers, not one. See below.
6. **Light.** Direction, quality, and whether the subject sits over or under the background.
7. **Where the type comes from.** In the image, overlaid, or absent because it lives in the caption.

Then the honesty question: what does this frame *not* tell you? Fill that column before the transferable
one, because a rule written without its blind spot gets applied where it does not hold.

## A pose has a job

A pose recorded as "half back-turn, chin over the shoulder" is a shape. The same pose recorded as
"showing the print on the back of the garment while keeping the face to camera" is reusable, because it
names the condition under which it is the right pose.

The ballpark row in the table is the clean case: hips rotated away, near shoulder brought toward the
lens, chin back over that shoulder, and the near arm lifted to the hair so it stops crossing the
lettering. Every element of that is forced by the garment's graphic being on the back. Change the
garment and the pose is wrong.

So never record a pose without its job. When the job is genuinely "nothing" — as in an inert frontal
selfie where hair and wardrobe carry the frame — record that too, because stillness is a decision and
adding a gesture to a busy frame is how a good reference gets ruined in the copy.

## Height beats size

To make a held product the subject, raise it above the eyeline. A small bag held above the crown outranks
a large one at the hip, because the eye resolves the topmost high-contrast object first and the face has
been demoted below it.

This is the cheapest fix available when a brand demands product prominence and the frame is already
crowded: do not scale the product up, move it up.

## Scale inversion

A strong one-point perspective lets you make the subject small without losing them. Converging
architectural lines point at the figure, so a full body at under a third of frame height still reads as
the subject, and the frame reads as photography rather than advertising.

The table records a two-post contrast on one account within four weeks: the wide corridor frame at
1.3M likes against the tight product collage at 443.2K. Do not carry that forward as a rule. Two posts,
different products, different weeks, no view counts — it is graded `two-post-anecdote` deliberately. What
it is good for is a test you can propose with a number attached, and a reply to a brand that wants the
product filling the frame.

## Curated candour

The highest-engagement frame in the set is a dressing-room shot with a desk fan and clutter left in, cut
to a video-still ratio, warm tungsten, subject looking just off the lens. The face is fully lit and
finished.

That is the whole device: **signal candour with the environment, keep the craft on the face.** Tidying the
background would cost the register; softening the light would cost the face. People reproduce this
backwards — they light casually and clean the room, which produces a bad photo of a tidy room.

The same warning applies as above: one account cannot separate reward-for-register from
reward-for-person. Treat it as a form to test, not a guarantee.

## Environmental typography

Shoot beside real words instead of overlaying them. A physical sign in frame carries the headline,
survives being reposted, and cannot be mistaken for a template — which is the failure mode of every
type layer dropped onto a stock image.

Practically: this is a location requirement, so it belongs in the brief, not in post. It also removes the
question of whether an image model should render the type, which it should never do — set final type in
the layout, as `identity-design.md` requires.

## The light sets the makeup contrast, not the taste

Open daylight at midday, no fill: hold the makeup low-contrast. A drawn lash line and a hard blush edge
that look correct indoors photograph as dirt in open shade, because the shadowless top light flattens the
skin and leaves only the drawn edges.

Large soft frontal source, close: contrast can drop even further, and a flush carried high across the
nose bridge reads as skin rather than product.

Single warm side source: the lip is the one element worth lifting. A bare face under warm falloff reads as
tired unless something has gloss on it.

`data/makeup-looks.csv` identifies the look; this is the constraint that decides whether the look can be
worn in the light you actually have.

## What a finished photograph cannot tell you

Four things, systematically, and every row in the table has to name at least one:

- **Product versus grade.** Whether a flush is blush or a warm grade is not recoverable from a delivered
  frame at social resolution. Claiming the product is inventing the useful half.
- **The retouch.** Skin, waistline and background geometry have all been adjusted. An observation about
  skin texture is an observation about a retouching decision.
- **The crop.** You are seeing the surviving rectangle of a wider frame. The composition may have been
  found afterwards, which matters if you are writing a shot list from it.
- **The discards.** One posted frame implies dozens rejected. The pose you are copying may be the only
  one of its family that worked, and the table cannot tell you why.

## Recording protocol

One row per post opened. Fill every column, including `what_this_cannot_tell_you` and `do_not_copy`, and
set `evidence_grade` honestly: `single-post-observation` for one frame,
`two-post-anecdote` for a comparison on one account, `craft-heuristic` where the rule predates the
reference and the frame merely illustrates it. Keep the post URL and the date you looked, because a
reference is a claim about a moment and the account will change.

Never add a row from a thumbnail, a search snippet, or a description. Open the post.
