# Calibrating the Craft Rules Against a Measured Set

## Contents

- What this unit is for
- The sample, and what it is not
- Why the instrument is not in this repository
- The method
- What the measurements did to the rules
- The four that changed something
- The one that could not be confirmed
- Five numbers the skill did not have
- What the whole exercise cannot establish
- Re-deriving it

## What this unit is for

`reference-reading.md` reads one post at a time and writes a row. That is the right way to learn a
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

## The sample, and what it is not

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

## Why the instrument is not in this repository

The script that produced these numbers lives outside the skill, and both reasons are worth stating
because both are reusable rules.

It needs Pillow. All 38 shipped tools run on the standard library alone, which is why a customer can
clone this repository and use it without installing anything. One tool with a dependency turns that
into a dependency policy, and the calibration is worth less than the property it would cost.

And the photographs are not ours to publish. The set's own manifest says copyright remains with the
original owners, which is the same sentence that got 17 files deleted from `docs/` — see
`reference-reading.md` for the line that actually matters. So the images stay out, the instrument that
reads them stays out, and only the numbers come in. This is the rule the image API already follows:
the API verifies prompts and no shipped script depends on it.

What that costs is honesty about reproducibility, and the cost is paid in the last section rather than
hidden.

## The method

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

## What the measurements did to the rules

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

## The four that changed something

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

## The one that could not be confirmed

`chroma-budget-by-count` allows at most one colour at or above C 0.19. No frame in the set breaks it:
238 carry zero loud hue families and 6 carry one. That looks like confirmation and is not, because
only 7 frames of 244 reach C 0.19 even at their 95th-percentile pixel. The sample almost never
approaches the limit, so it cannot test it.

The gate therefore keeps its `house-rule` grade. Promoting it here would be the most tempting error
available in this whole exercise: a rule nothing contradicted, recorded as a rule something confirmed.

## Five numbers the skill did not have

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

## What the whole exercise cannot establish

- **Any of it is not reproducible from this repository.** The images are absent by decision and the
  instrument is absent by policy. What is here is a claim about a measurement, not the measurement.
  That is a real weakness and it is the correct trade: see `reference-reading.md`.
- **No axis here explains engagement.** Nothing was correlated with likes, and with five accounts and
  no view counts nothing could be. Every number describes what professionals delivered, not what
  worked.
- **Choice cannot be separated from physics.** Skin, fabric and daylight are low-chroma in sRGB. Part
  of the chroma result is what a camera can record rather than what an art director decided, and this
  method cannot split them.
- **Choice cannot be separated from location.** Indoor tungsten and outdoor blue hour both produce a
  warm subject on a cool ground.
- **Grade cannot be separated from subject.** A muted grade over a saturated scene and a muted scene
  shot straight measure identically, which is the same blind spot `reference-reading.md` names as
  product versus grade.
- **One day of five feeds is not an industry.** Re-measuring in six months would produce different
  numbers, and the direction of the change would be the interesting part.

## Re-deriving it

To repeat this on a set you have rights to: decode to a 160px long edge, read ratio from the header,
convert every pixel through `scripts/plan_palette.py`'s `rgb_to_oklab`, and weight every statistic by
pixel count. Record the sample size, the accounts or sources, and the date, because a calibration is a
claim about a moment.

Then fill `data/reference-set-calibration.csv` the same way: name the claim, name the file and column
it lives in, and set the verdict honestly. `consistent-but-untested` exists as a verdict for a reason,
and a table where every row says `confirmed` is a table that was written to agree with itself.
