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
- Reference analysis
- Reference-first image flow
- Calibrating the craft rules against a measured set

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

## Reference analysis

### Analyze without copying

Treat references as evidence of structure, material, pacing, and market saturation. Never reproduce a distinctive layout, tagline, character, pose, sequence, or artist signature.

A reference you cannot redistribute is still usable. What you keep is the measurement, not the file: `data/reference-observations.csv` holds one row per post actually opened, and the `Calibrating the craft rules against a measured set` section later in this file holds a population pass over 244 frames this repository deliberately does not ship. That distinction matters to a reader deciding whether a rule here is asserted or measured — "no evidence" and "evidence whose source cannot be republished" look identical from the outside, and only one of them is true here.

### Reference fingerprint

For every useful reference, capture:

| Axis | Questions |
|---|---|
| Strategic job | Awareness, proof, conversion, retention, culture, launch? |
| Hook | What earns attention in the first frame or viewport? |
| Hierarchy | What is understood first, second, and third? |
| Composition | Grid, crop, asymmetry, scale, depth, text-safe field? |
| Subject | Product, person, mechanism, place, typography, demonstration? |
| Camera and light | Distance, lens behavior, source, hardness, color, realism? |
| Material | Glass, paper, skin, metal, fabric, food, interface, environment? |
| Copy behavior | Claim, tension, proof, CTA, rhythm, density? |
| Motion | State change, sequence, reveal, pacing, transition? |
| Saturation | Rare, emerging, common, or category reflex? |
| Rights risk | Trademark, celebrity, artist style, proprietary asset, copied device? |

### Rejection map

Create four lists:

1. **Keep**: structural principles tied to the objective.
2. **Transform**: useful pattern that needs an original mechanism or material.
3. **Reject**: saturated category reflex or incompatible brand behavior.
4. **Avoid legally**: protected identity, artwork, logo, character, or close imitation risk.

### Search strategy

Search separately for:

- Audience behavior and tension.
- Product mechanism and physical materials.
- Channel-native execution.
- Adjacent categories with similar decisions but different visual defaults.
- Anti-reference examples that reveal what the category overuses.

Search for the physical scene rather than a broad category. "Frosted serum bottle on a scratched stainless tray under bathroom window light" is more useful than "skincare ad."

### Originality transformation

Transform at least three axes before using a reference pattern:

- Change the mechanism or metaphor.
- Change material and physical setting.
- Change composition and crop behavior.
- Change proof type.
- Change narrative order.
- Change channel-native behavior.
- Change typography role and copy rhythm.

Document the transformation in one sentence. If the result can still be traced to one source at a glance, restart.

### Research record

```text
Source:
Observed on:
What it proves:
Useful structure:
Saturated or risky element:
Original transformation:
Rights note:
```

## Reference-first image flow

### Default user experience

Use this flow when the user supplies one or more images with a description:

```text
references + description + intended use
-> analyze reference roles
-> preserve locks and extract visual grammar
-> ask only material questions, otherwise proceed
-> choose provider and execution mode
-> generate one final or four controlled variants
-> inspect, reject failures, and refine the selected direction
```

Do not force the user to fill a long form. Infer reversible details and show the assumptions briefly.

### Reference role map

Assign each image one primary role and optional secondary roles:

| Role | Extract | Preserve only when authorized |
|---|---|---|
| `identity` | Face, body, age presentation, distinguishing features | Exact identity and proportions |
| `product` | Shape, logo, packaging, material, label plane | Exact product geometry and approved text |
| `pose` | Weight distribution, hand task, gaze, gesture | Pose family, not accidental anatomy defects |
| `composition` | Shot size, camera height, angle, subject placement, negative space | Spatial grammar |
| `lighting` | Key direction, source size, fill, separation, color, background exposure | Light behavior |
| `styling` | Hair, makeup, wardrobe, accessories, set language | Non-protected styling qualities |
| `color-grade` | White balance, contrast, saturation, highlight rolloff, grain | Tonal treatment |
| `texture` | Skin, fabric, film, surface, material behavior | Material response |

Return a compact reference map:

```text
Image 1: composition + lighting
Image 2: styling + pose
Image 3: product lock
Identity intent: style-only / preserve-authorized-subject / unknown
```

### Clarification gate

Proceed without asking when:

- The user describes the subject and desired outcome.
- Reference roles can be inferred safely.
- The output channel or ratio can be inferred or left `auto`.
- The work uses an original fictional adult rather than reproducing a public figure.

Ask at most three short questions when an answer materially changes:

1. **Identity**: Is a supplied person the edit target to preserve, or only a style reference?
2. **Use and ratio**: Is this for `9:16`, `4:5`, `1:1`, web hero, or another fixed placement?
3. **Direction**: Should the result feel studio-clean, studio-natural, environmental-editorial, or phone-candid when the references conflict?

If the user says “make something like this” and the images feature celebrities, default to a fictional adult with the same non-identifying photographic grammar. State the assumption and proceed.

### Direction and variant design

Create one canonical direction containing:

- Single communication idea.
- Reference map and priority.
- Subject/product locks.
- Capture mode.
- Composition and crop.
- Camera and lighting geometry.
- Styling, materials, and color finish.
- Negative constraints.

When producing four variants, use this default spread:

1. `V1-anchor`: closest safe translation of the reference grammar.
2. `V2-composition`: change camera distance, placement, or crop.
3. `V3-light`: change one motivated light setup while keeping styling stable.
4. `V4-action`: change pose, gesture, or product interaction.

Optional fifth:

5. `V5-departure`: one controlled art-direction break with explicit risk.

Keep identity/product locks, message, ratio, and major styling stable unless that variable is the named test.

### Generation loop

1. Build the provider-neutral master prompt.
2. Run `scripts/plan_image_generation.py`.
3. Compile the provider prompt with `scripts/compile_prompt.py`.
4. Generate all exploration variants from the same canonical reference map.
5. Inspect each output for identity/product fidelity, anatomy, physics, reference use, and crop.
6. Reject critical failures before showing a recommendation.
7. Recommend one result and explain the decisive strength in one sentence.
8. Refine only the selected result with a single-change instruction.

Do not chain V2 from V1, V3 from V2, and V4 from V3. Serial mutation compounds drift. Branch variants from the same source state, then use multi-turn editing only on the selected branch.

### Celebrity and identity handling

For public-figure references such as Jang Wonyoung or aespa:

- Analyze pose family, framing, light, styling, makeup language, wardrobe silhouette, palette, set, and grade.
- Do not use the celebrity name in the execution prompt when the goal is an original marketing image.
- Replace recognizable identity with `fictional adult subject` and brief-appropriate casting.
- Do not imply endorsement, collaboration, or product use by the public figure.
- Preserve exact identity only for a permitted edit where the user supplied or authorized the target image and the requested change is allowed.

### Delivery contract

Return:

1. Assumptions and any identity safety translation.
2. Reference map.
3. Recommended provider and why.
4. Master direction.
5. One final image or four/five labeled variants.
6. QA notes and rejected failures.
7. One recommended next edit.

If rendering is unavailable, return the same structure with executable prompts and explicitly say no images were rendered.

## Calibrating the craft rules against a measured set

### What this unit is for

The single-post protocol at the top of this file reads one post at a time and writes a row. That is the right way to learn a
device, and it is the wrong way to learn a distribution. Ten hand-read posts in
`data/reference-observations.csv` produced the line "two hues plus skin" twice, and two occurrences of
a phrase is not a frequency. This unit is the population pass: 244 frames measured by machine on the
same axes, with the results in `data/reference-set-calibration.csv`, one row per axis.

The point is not to add more craft rules. It is to grade the ones already asserted. Every row carries
the claim it grades, the file and column that claim lives in, and a verdict of `confirmed`, `refined`,
`consistent-but-untested` or `baseline`. Four claims were refined, one confirmed, one could not be
tested by this sample at all, and five axes came back with no prior claim to grade, which is its own
finding: on five of eleven measurable properties of a photograph, the skill had opinions and no
numbers.

### The sample, and what it is not

244 photographs from five public accounts: one group and brand account and four personal accounts,
44 to 50 frames each, all professional or professionally managed Korean entertainment output, all
delivered to Instagram, all collected on one day.

Everything in that sentence is a limit. This is one industry, one country, one platform, one register,
one week of a feed. It is a portrait set, so the subject fills a large share of every frame and skin
is present in all 244. It contains no product photography, no marketplace tile, no ad unit, no flat
graphic layout, and no landscape work without a person in it. A number measured here transfers to a
Vietnamese cosmetics brand's feed portraits with an argument, and does not transfer to its catalogue
tiles at all.

The set is also self-selecting on success: these are posted frames. The discards are invisible, so
every distribution below is a distribution of what survived an editor, not of what was shot.

### Why the instrument is not in this repository

The script that produced these numbers lives outside the skill, and both reasons are worth stating
because both are reusable rules.

It needs Pillow. Every shipped tool runs on the standard library alone, which is why a customer can
clone this repository and use it without installing anything. One tool with a dependency turns that
into a dependency policy, and the calibration is worth less than the property it would cost.

And the photographs are not ours to publish. The set's own manifest says copyright remains with the
original owners, which is the same sentence that got 17 files deleted from `docs/` — see
the `Reference analysis` section above for the line that actually matters. So the images stay out, the instrument that
reads them stays out, and only the numbers come in. This is the rule the image API already follows:
the API verifies prompts and no shipped script depends on it.

What that costs is honesty about reproducibility, and the cost is paid in the last section rather than
hidden.

### The method

Each frame is decoded once to a 160px long edge. Colour statistics are scale-invariant well below
that, and 244 full-resolution decodes cost minutes for numbers that do not move. Aspect ratio is read
from the file header without decoding, so the crop measured is the crop delivered.

Then, per frame:

- **Chroma** in OKLCH, through `scripts/plan_palette.py`'s own `rgb_to_oklab`, imported rather than
  rewritten. A second implementation of OKLab would grade the gate against a slightly different
  definition of chroma and the disagreement would be invisible: it would look like a finding about
  photographs.
- **Hue families** at 30 degrees each, counting only pixels above HSV saturation 0.15. Below that a
  pixel is making a value decision, not a hue one, and a near-neutral's hue angle is unstable anyway —
  `data/colour-gates.csv` records that a neutral's hue swings a median 72.7 degrees under a single
  8-bit step. A family holding under 5 percent of the frame is an accent, not a palette member.
- **Value** as HSV value, with the spread taken as p95 minus p5 rather than max minus min, so one
  blown specular highlight does not decide what the contrast of a photograph is.

Every statistic is weighted by pixel count, not by distinct colour, because a colour occupying one
pixel and a colour occupying a third of the frame are not two equal samples.

### What the measurements did to the rules

| Axis | Verdict | The rule it graded |
|---|---|---|
| `frame-ratio-share` | confirmed | 1:1 is a legacy feed ratio |
| `loud-surface-share` | refined | Loud colour under 20 percent of the area |
| `hue-family-count` | refined | Two hues plus skin |
| `ratio-by-account-register` | refined | 4:5 is the Meta feed ratio |
| `neutral-share` | refined | Background dressing should not compete |
| `loud-colour-count` | consistent-but-untested | At most one colour at or above C 0.19 |
| `peak-chroma` | baseline | Nothing. No number existed |
| `value-spread` | baseline | Nothing. No number existed |
| `shadow-and-highlight-share` | baseline | Nothing. No number existed |
| `warm-bias` | baseline | Nothing. No number existed |
| `dominant-hue-family` | baseline | Nothing. No number existed |

### The four that changed something

**The 20 percent chroma budget does no work on a photograph.** `chroma-budget-by-surface-share` fails
a palette whose loud colours cover more than a fifth of the visible area. In this set the median frame
covers **zero** percent, the p90 covers 0.26 percent, and 190 of 244 frames contain no pixel at C 0.19
at all. Exactly one frame of 244 exceeds the gate. A threshold that 243 of 244 professional frames
clear by two orders of magnitude is not a gate, it is a formality.

The refinement is deliberately narrow. 20 percent stays for flat layouts, where a full-bleed brand
panel is a legitimate surface and no photograph is being described. For a photograph or a photo-derived
render the working line is 3 percent, which 96 percent of this set sits under. Lowering the layout
threshold on photographic evidence would be the object mismatch this file is supposed to name, not
commit.

**Two hues plus skin is a target, not a rule.** The median frame carries exactly two hue families, so
the hand observations picked the centre correctly. But 42 percent of frames carry three or more, and
209 of 244 sit at three or fewer. So the honest statement is a ceiling of three with a target of two.
Stated as a flat rule of two it makes a run delete a third hue the reference set treats as ordinary,
which is a worse failure than the one it prevents.

**Ratio follows register, not taste.** 4:5 is the default at 71 percent overall, and that number hides
the actual structure: the group and brand account runs 9:16 in 38 of its 44 frames while all four
personal accounts default to 4:5. A brand account is vertical-video-first and a person account is
feed-portrait-first. So "what ratio" cannot be answered before "who is posting", and the skill was
treating those as one question. What this does not establish is why: a brand account posts more stage
and performance footage, which is natively 9:16, so the ratio may be following the source material.

**"Should not compete" was a preference until it had a share.** The observation table says a
background should locate the photo without competing, which is correct and gives nobody anything to
do. Measured, `neutral-share` has a median of 0.404: about 40 percent of a professional frame is
making no colour decision at all, and all five accounts sit between a third and a half. A generated
frame where every surface carries a hue is not a stylistic variant of this set, it is a different
structure. What the number cannot say is where the neutral area sits, and that matters: a neutral wall
behind the subject and a neutral outfit against a coloured wall give the same share and read nothing
alike.

The confirmation is smaller but worth having. `data/frame-ratios.csv` already calls 1:1 a legacy feed
ratio, and now legacy has a number: three frames in 244. 2:3 appeared zero times.

### The one that could not be confirmed

`chroma-budget-by-count` allows at most one colour at or above C 0.19. No frame in the set breaks it:
238 carry zero loud hue families and 6 carry one. That looks like confirmation and is not, because
only 7 frames of 244 reach C 0.19 even at their 95th-percentile pixel. The sample almost never
approaches the limit, so it cannot test it.

The gate therefore keeps its `house-rule` grade. Promoting it here would be the most tempting error
available in this whole exercise: a rule nothing contradicted, recorded as a rule something confirmed.

### Five numbers the skill did not have

These graded nothing, because nothing existed to grade. Each is a measured property of professional
output that the skill previously described only in adjectives.

- **`value-spread`: professional frames use nearly the whole tonal range.** Median 0.788, and
  per-account medians agree within five points, which is the tightest agreement of any axis measured.
  The flat mid-tone render an unprompted model produces is measurably not this look.
- **`shadow-and-highlight-share`: a fifth of the frame at each end.** Medians 0.212 and 0.229, and
  near-symmetric. Shadow is not something professional work minimises, which contradicts what a
  soft-light brief tends to produce.
- **`warm-bias`: warm is the default.** Median +0.546, and all five accounts are warm at the median.
  Cool is the deliberate exception, so a brief asking for cool and editorial is asking for the p10 of
  professional practice and should be told so.
- **`dominant-hue-family`: orange leads nearly half the frames.** 113 of 244, with the blue side
  leading 65. The set is a warm subject on a cool ground. Green leads once in 244.
- **`peak-chroma`: C 0.19 is far from where photography lives.** The median frame's 95th-percentile
  pixel sits at C 0.0713, roughly 38 percent of the loud threshold. The skill had a definition of loud
  and no scale to read it against.

Use these as reference points, not as targets. A frame at the median of all five is not therefore
good; it is unremarkable, which is a different and sometimes useful thing.

### What the whole exercise cannot establish

- **Any of it is not reproducible from this repository.** The images are absent by decision and the
  instrument is absent by policy. What is here is a claim about a measurement, not the measurement.
  That is a real weakness and it is the correct trade: see the `Reference analysis` section above.
- **No axis here explains engagement.** Nothing was correlated with likes, and with five accounts and
  no view counts nothing could be. Every number describes what professionals delivered, not what
  worked.
- **Choice cannot be separated from physics.** Skin, fabric and daylight are low-chroma in sRGB. Part
  of the chroma result is what a camera can record rather than what an art director decided, and this
  method cannot split them.
- **Choice cannot be separated from location.** Indoor tungsten and outdoor blue hour both produce a
  warm subject on a cool ground.
- **Grade cannot be separated from subject.** A muted grade over a saturated scene and a muted scene
  shot straight measure identically, which is the same blind spot the single-post protocol above names as
  product versus grade.
- **One day of five feeds is not an industry.** Re-measuring in six months would produce different
  numbers, and the direction of the change would be the interesting part.

### Re-deriving it

To repeat this on a set you have rights to: decode to a 160px long edge, read ratio from the header,
convert every pixel through `scripts/plan_palette.py`'s `rgb_to_oklab`, and weight every statistic by
pixel count. Record the sample size, the accounts or sources, and the date, because a calibration is a
claim about a moment.

Then fill `data/reference-set-calibration.csv` the same way: name the claim, name the file and column
it lives in, and set the verdict honestly. `consistent-but-untested` exists as a verdict for a reason,
and a table where every row says `confirmed` is a table that was written to agree with itself.
