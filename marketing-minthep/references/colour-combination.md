# Colour Combination

## Contents

- What this unit is for
- Running it
- The four quantities
- Why the space matters
- The nine gates and the four verdicts
- Why `review` exists
- Which numbers are ours
- A near-neutral has no hue to share
- Ramps: arc length is not chord distance
- What a scheme is, and what it is not
- Reading the twenty shipped palettes
- The evidence that exists
- The two statistics that do not
- Colour in Vietnam
- Taking a colour brief in Vietnamese
- Order of work
- Refusals
- What this unit cannot decide

## What this unit is for

Colour combination is taught as a wheel. Pick a hue, step 180 degrees, call it complementary; step
120 twice, call it triadic. The wheel is a way of generating candidates. It is not a way of judging
them, and it says nothing about the three questions that actually decide whether a palette survives
contact with a product page, a printed menu or a 320-pixel-wide thumbnail: can the text be read, can
the two states be told apart, and does anything lead.

All three are measurable before anyone opens a design tool. This unit measures them. Everything here
is arithmetic in stdlib Python — no key, no network, no image provider — so a palette decision can be
checked, disagreed with, and re-checked after the disagreement.

`colour` takes a `composition-system` and produces a `palette-decision`. It sits after `compose`
because a palette is assigned to roles that a layout has already defined, and before `identify`,
because a mark has to survive at sixteen pixels in black before its colour is worth arguing about.
See `command-surface.md`.

## Running it

```
plan_palette.py --palette-id paper-cobalt
plan_palette.py --check bg=#F5F1E8 ink=#141414 accent=#2A4BD7 support=#D9541E
plan_palette.py --check bg=#161616 ink=#F2F2F0 accent=#C8FF3D --carries-meaning accent+ink
plan_palette.py --check bg=#EDEEF0 ink=#101215 accent=#0057FF --share bg=0.7 ink=0.1 accent=0.2
plan_palette.py --scheme triadic --seed '#0057FF' --against '#EDEEF0'
plan_palette.py --ramp 9 --seed '#2A4BD7'
```

Exit 0 is a clean palette. Exit 1 is a usage error. Exit 2 is a failed gate: something in the
palette breaches a requirement and the palette is not shippable as given. Exit 3 is the interesting
one — nothing failed, and something needs a person. A skipped gate does not change the exit code at
all, because making it non-zero would push a caller toward inventing the missing input to get a
clean run, which is the single outcome this script exists to prevent.

Do not describe a palette you have not run. The output carries per-pair contrast ratios, what each
ratio permits by WCAG band, lightness separation, hue gap, edge-vibration risk, dichromacy survival,
and the palette-wide chroma budget. Quote those numbers instead of adjectives.

## The four quantities

**Contrast** decides whether text can be read. WCAG relative luminance from linear sRGB, ratio
`(L1 + 0.05) / (L2 + 0.05)`. 4.5:1 for body text at AA, 3:1 for large text and for non-text
boundaries such as icons, input borders and focus rings.

**Lightness separation** decides whether two colours read as two colours. Measured as the absolute
difference in OKLCH lightness. Two swatches can pass a contrast check against a shared background
and still be indistinguishable from each other, which is how a chart with a five-colour legend ends
up with three colours in it.

**Hue gap** decides whether the separation question even applies. Two colours 12 degrees apart in
hue are the same colour family and must separate by lightness. Two colours 150 degrees apart do not
need to, but may now vibrate at their shared edge if both are saturated and similarly light.

**Chroma budget** decides whether anything leads. The palette is checked twice: by count, at most
one colour at or above OKLCH chroma 0.19, and by measured surface share, with the loud colours
holding no more than a fifth of the visible area. Two shouting colours is not a colour failure. It
is a hierarchy failure that presents as one.

## Why the space matters

HSV gives `#FFFF00` and `#0000FF` the same value of 100%. In OKLCH they sit at lightness 0.968 and
0.452 — half the scale apart. Against white, the yellow contrasts at 1.07:1 and the blue at 8.59:1;
one of them is invisible. Any harmony built on equal HSV value produces a palette whose members are
nowhere near equally light, and the error is largest exactly where it costs most, on saturated
yellows and cyans that a designer will place text on.

So: sRGB because that is what a hex value means and what a screen shows; linear sRGB because both
the WCAG luminance formula and the colour-vision matrices are defined on light rather than on
gamma-encoded numbers; OKLab and OKLCH (Ottosson, 2020) for every comparison of lightness, chroma
and hue. When a rotation leaves the sRGB gamut, chroma is reduced until the colour fits rather than
channels being clipped, and the output says `chroma_reduced_to_fit_srgb` so nobody has to guess why
the printed hex is duller than the one requested.

## The nine gates and the four verdicts

`data/colour-gates.csv` is the table, with nine columns per gate: what it applies to, its threshold,
its formula, the space it is computed in, the verdict if it fails, its evidence grade, its source,
and what it does not establish. Read it there rather than restating the thresholds from memory. These
are the nine names the output uses, so a line in a JSON payload can be traced back to a rule:

| Gate | Asks |
|---|---|
| body-text-contrast | Can this pair carry body copy at AA |
| large-text-contrast | Can it carry large text |
| non-text-contrast | Can it carry an icon, a border or a focus ring |
| same-hue-lightness-separation | Do two colours of one family read as two colours |
| no-vibrating-edge | Will the shared edge shimmer |
| colour-is-not-the-only-cue | Do the two survive dichromacy if colour is the only signal |
| chroma-budget-by-count | Does more than one colour shout |
| chroma-budget-by-surface-share | Has the shouting colour become the background |
| ramp-step-evenness | Are the steps of a generated ramp perceptually equal |

Eight of the nine run on a palette; `ramp-step-evenness` runs on a generated ramp. Every gate returns
one of four verdicts, and the difference between them is the whole point.

| Verdict | Means |
|---|---|
| passed | The arithmetic ran and cleared the threshold |
| failed | The arithmetic ran and breached it |
| skipped | The input was never supplied, so nothing was measured |
| review | The arithmetic ran and does not settle the question |

`skipped` and `review` are not softer versions of `failed`. `skipped` is the honest answer when the
caller supplied no surface shares: the surface-share budget cannot pass on shares nobody measured.
`review` is the honest answer when the number is inside the band where the threshold is an invention,
or when the breach depends on a use the script cannot see.

## Why `review` exists

From the checker's own docstring: `review` exists so that the gates that do fail mean something. A
checker that returns a verdict on everything gets ignored on everything.

The first version of this checker had no `review`. It compared a colour to itself and called zero
separation a defect. It called an off-white the same hue family as lime on the strength of a rounding
error. It ruled on a use it could not see. It failed a pair by 0.0004 against a threshold it had
invented. Ten of the twenty shipped palettes came back broken, and not one of the ten was.

Four tests in `test_tools.py` exist because of those four bugs, which is the more general lesson: a
gate that fires on a correct palette is worse than no gate, because it teaches the user to skip the
output.

## Which numbers are ours

Three grades, and the table states one per gate:

- `standard-requirement` — the three contrast gates. W3C WCAG 2.2 SC 1.4.3 and SC 1.4.11.
- `standard-requirement-with-house-threshold` — the colour-vision gate. SC 1.4.1 is the requirement
  and Machado, Oliveira and Fernandes (2009, IEEE TVCG) is the simulation; the 0.09 OKLab collapse
  distance is ours.
- `house-rule` — the other five. Lightness separation, edge vibration, both chroma budgets, ramp
  evenness. No published threshold exists for any of them.

Five of nine being house rules is survivable only while two things stay true: the table says which
five, and the gates that do fail mean something. If a client asks whether a number is a standard or
a preference, read them the column. The shape of each rule is defensible; the number is ours, and
the honest defence of a number is that it is written down, tested and open to argument, not that it
sounds authoritative in a table.

## A near-neutral has no hue to share

The lightness-separation gate only applies when both colours carry at least 0.03 chroma. Below that
the hue angle is not a property of the colour. Sweeping the sRGB cube shows a near-neutral's OKLCH
hue angle swinging by a median 72.7 degrees when a single 8-bit channel changes by one — more than
twice the entire 30-degree same-hue window. `#F2F2F0` reports a hue of 106 degrees, and that number
is what remains of a rounding error.

The floor is where quantisation stops deciding the answer. At chroma 0.03 the 90th-percentile swing
is 3.3 degrees, so two colours wobbling in opposite directions move 6.6 degrees inside a 30-degree
window: 22 percent. At 0.02 the same figure is 33 percent, which is too much of the answer. The
derivation is a comment in `plan_palette.py`, and `test_tools.py` re-runs the sweep and checks the
comment against it rather than trusting it.

## Ramps: arc length is not chord distance

A tonal ramp built by stepping the OKLCH lightness coordinate evenly is not perceptually even, because
chroma varies along the path and the eye judges the chord between neighbours, not the coordinate.
Cutting the path by equal arc length is closer and still wrong, because the path curves hardest at
the dark end where chroma collapses.

So the ramp is cut by arc length and then relaxed until adjacent chords are as close to equal as the
path allows. Over the ten seeds the tests hold, at nine steps, the worst step falls from up to 35.1
percent off the mean to 5.5 percent, and every one of the ten seeds improves. The gate still reports
the residual, because on some hues the path genuinely cannot hold the number of steps asked for: at
twelve steps the worst case is 17.9 percent and the gate fails. That is more use than a ramp which
looks even in its coordinates and has two indistinguishable swatches at the bottom.

## What a scheme is, and what it is not

`--scheme` generates candidates with lightness and chroma held to the same gates, so a scheme arrives
already measured. It also arrives with a warning attached, and the warning is the useful part.

Every member of a generated scheme shares the seed's lightness. Triadic from `#0057FF` gives
`#CE002C` and `#068605`, all three within 0.002 of lightness 0.537. Against `#EDEEF0` two of them
clear 4.5:1 and the third reaches 4.09:1 and cannot carry body text. None of the three can carry text
against another. A scheme is a set of accents. The text colour and the background are a separate
decision, made against contrast, not against the wheel.

Never present a wheel scheme as a result. It is a shortlist that has passed a first check.

## Reading the twenty shipped palettes

`data/palettes.csv` holds twenty palettes with four roles each — `bg`, `ink`, `accent`, `support` —
plus what each is for, what it is wrong for, and the measured ratios. All twenty clear every gate.
Six carry a review, and the reviews are the instructive part:

| Palette | Reviewed for |
|---|---|
| bone-terracotta, charcoal-lime, blush-oxblood, slate-coral | colour-is-not-the-only-cue |
| offwhite-navy, plum-butter | same-hue-lightness-separation |

Two palettes use one colour in two roles: `black-white` and `kraft-black`. The checker names that in
`same_colour_in_two_roles` and does not fail it, because a palette which deliberately declines to
have an accent is a decision, not a defect.

The `avoid_for` column is load-bearing and is where most of the commercial judgement lives.
`white-crimson` drives appetite and caps price. `charcoal-lime` makes almost every dish look unwell.
`mint-graphite` pushes cooked food toward grey. `grey-electric` is the palette every SaaS already
has. Read `avoid_for` before `use_for`; the exclusion is the more expensive mistake.

## The evidence that exists

Four rows in `data/marketing-benchmarks.csv` carry what was actually reachable, each with its fetch
status and its limit.

- `colour-62-90-assessment` — Singh (2006), *Management Decision* 44(6). The abstract reports that
  62 to 90 percent of an initial assessment is attributed to colour alone, in a review that says of
  itself that it highlights inconsistencies and controversies in colour psychology. Abstract only.
- `colour-brand-personality` — Labrecque and Milne (2012), *JAMS* 40(5). Four studies mapping hue
  onto brand-personality dimensions, with saturation and value as amplifiers. This is the evidence
  that chroma and lightness are levers rather than decoration, which is what the chroma budget and
  the separation gate operate on. Abstract only.
- `colour-product-congruity` — Bottomley and Doyle (2006), *Marketing Theory* 6(1). Logo colour reads
  as appropriate or not depending on the product it sits on. Abstract only.
- `colour-recognition-80-percent` — no publication exists. See below.

The usable synthesis is short. Colour affects a first impression strongly and measurably. Which
colour is right is a function of the product, not of the colour, so the question "what does blue
mean" has no answer worth acting on and the question "what is this product for" does.

## The two statistics that do not

**"85 percent of purchase decisions are made on colour."** Traceable to Singh (2006), which says
62 to 90 percent, of an *initial assessment* rather than a purchase decision, in a literature review
which flags its own inconsistencies. A range that wide is a statement about how unsettled the
evidence is. Collapsing it to one number reverses its meaning. Quote the band and the review, or
quote nothing.

**"Colour increases brand recognition by 80 percent," attributed to a University of Loyola study.**
Three Crossref bibliographic searches — on the figure, on the attributed university, and on the
underlying construct — return no publication resembling the claim. No version in circulation names a
journal, a year or a sample. The table records this as `fetch_status: no-source-found`, which is
deliberately not `paywalled`: paywalled means a document exists and costs money, and letting an
untraceable claim sit in the same category as a paid report lends it credibility it has not earned.

When a brief quotes either statistic, say the citation does not carry the claim, and offer the
measurable question instead: does the mark survive at sixteen pixels, and does the palette hold its
separation gates.

## Colour in Vietnam

Category convention is observable and worth stating; it is convention, not research, and it is
graded that way.

Red with gold or yellow is the settled register for Tết and for gifting, which is why `ivory-gold`
and `white-crimson` name those occasions. Occasion palettes suppress habit, so the same red that
carries a Tết hamper works against an everyday repeat purchase — this is the congruity finding in
Bottomley and Doyle, arriving as a commercial constraint rather than a theory.

White and, in the north especially, black carry funeral association. This does not make white
unusable, and reasoning from it directly is where colour folklore does real damage: white is also
the required product background on every marketplace a Vietnamese seller lists on. The association
lives in a bouquet, a card and a wreath. It does not live in a packshot. Context decides, which is
exactly what the congruity evidence predicts and what a meaning-lookup table cannot express.

Two constraints the arithmetic cannot see. Print: an accent checked on a screen loses chroma on
uncoated and kraft stock, which is most local packaging, so a palette approved in sRGB has to be
proofed on the substrate before it is signed off. Screen: much Vietnamese traffic is a mid-range
Android phone held outdoors, so treat the WCAG minima as a floor and not a target, and check the
palette at the size it will actually be seen.

## Taking a colour brief in Vietnamese

Vietnamese does not partition blue and green the way the gates assume. *Xanh* covers both; *xanh lá*
is leaf, *xanh dương* and *xanh biển* are sky and sea, and a client who says *xanh* has specified
nothing a script can consume. Two palettes in the table, `white-jade` and `grey-electric`, are both
*xanh* to a client. Their accents sit 93 degrees apart in hue and within 0.017 of each other in
lightness, so the only thing separating them is the axis the word does not specify.

So do not take a colour brief in colour names, in either language. Ask for one of three things: a
hex value, a photograph of the physical object, or an existing asset to sample. Then state what you
measured back to the client in their words plus the hex, so the disagreement happens before the
work. `name_vi` exists in `data/palettes.csv` for exactly that handover, and is a label for a
measured palette rather than a specification of one.

## Order of work

1. Take the `composition-system`. Roles come from the layout; do not invent a fifth role to fit a
   colour you like.
2. Fix the background and the ink first, against contrast. This is the pair that most constrains
   everything else, and it is the one that fails cheapest to fix.
3. Generate accent candidates however you like, wheel included. Then run them.
4. Declare the pairs that carry meaning by colour alone, with `--carries-meaning`. Undeclared, a
   colour-vision collapse is only reported; declared, it fails. The declaration is the caller's job
   because SC 1.4.1 is broken by a use, not by a palette.
5. Measure the surface shares off the actual layout and pass them with `--share`. Without them the
   surface budget is skipped, and a palette can pass on count while the loud colour has quietly
   become the background.
6. Build the ramp last, from the accent, and read the evenness residual rather than the swatches.
7. Write the `palette-decision` down: role, hex, OKLCH, every gate verdict, every review with the
   reason it is a review, and every skip with the input that would close it.
8. Check whether the category already owns the accent, and whether anyone has registered it. That is
   a search and a lawyer.

## Refusals

- A wheel scheme presented as a result. It is a shortlist that passed one check.
- The 85-percent and 80-percent colour statistics. One says something weaker than it is quoted as
  saying; the other has no source.
- A colour-meaning lookup table. Meaning is congruity with the product, and a table that says blue
  means trust is folklore with a citation stapled to it.
- Shares nobody measured, to turn a `skipped` into a `passed`.
- Downgrading a house rule's grade in a client deck to make a preference sound like a standard.
- A palette signed off for print without a substrate proof.
- A hue named rather than measured, in Vietnamese or in English.

## What this unit cannot decide

Whether the palette suits the brand. Whether the category already owns it. Whether the accent is a
competitor's registered mark. Whether the colour carries a meaning in the specific market being sold
into that the four sourced rows do not cover. What the palette looks like in CMYK on the actual
stock. And whether the reviewed pairs matter, which depends on a layout the script has never seen
and a person has.
