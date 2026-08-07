# Colour Combination

## Contents

- What this unit is for
- Running it
- The four quantities
- Why the space matters
- The twelve gates and the four verdicts
- Why `review` exists
- Measuring the photograph before choosing the palette
- Which numbers are ours
- A near-neutral has no hue to share
- Ramps: arc length is not chord distance
- What a scheme is, and what it is not
- Reading the shipped palettes
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

When the palette will sit on the same surface as a photograph, measure the photograph too:

```
sample_reference.py --image ref/bowl.png
sample_reference.py --image ref/bowl.png --check accent=#2A4BD7 support=#D9541E
sample_reference.py --image ref/bowl.png --artwork out/menu.png --check accent=#2A4BD7
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

## The twelve gates and the four verdicts

`data/colour-gates.csv` is the table, with nine columns per gate: what it applies to, its threshold,
its formula, the space it is computed in, the verdict if it fails, its evidence grade, its source,
and what it does not establish. Read it there rather than restating the thresholds from memory. These
are the twelve names the output uses, so a line in a JSON payload can be traced back to a rule:

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
| subject-holds-chroma-peak | Is the brand louder than the thing being sold |
| accent-chroma-matches-reference | Was the accent measured from the photograph or only named after it |
| accent-hue-is-anchored-in-reference | Is this colour in the scene at all |

Eight run on a palette; `ramp-step-evenness` runs on a generated ramp; the last three run on a
palette *and* a photograph, and are the subject of the next section. Every gate returns one of four
verdicts, and the difference between them is the whole point.

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

Those four bugs are recorded because a gate that fires on a correct palette is worse than no gate:
it teaches the user to skip the output. Re-run the calibration cases before changing a threshold.

## Measuring the photograph before choosing the palette

The nine palette gates all ask whether the colours work against each other. None of them can see the
photograph the palette will be printed next to, and that is where the commonest failure in the trade
lives. It has a mechanism, and the mechanism is worth naming precisely, because most people who commit
it think they did the right thing.

The right thing looks like this: open the reference photograph, see that the ceramics are blue, and
make the brand colour blue. The hue is honest — it really is in the scene. What gets discarded are the
other two quantities that made the blue harmonious in the photograph: **how saturated it was** and
**how much of the frame it held**. A hue name carries neither. So the accent comes off a swatch list
at full chroma, gets applied to a navigation rail at ten times the area, and the result is a palette
that passes every contrast and budget gate while looking, to anyone who glances at it, like a
rectangle drawn on top of a photograph. This is mechanically what happens when a menu is opened in a
template editor and the blue is picked by eye.

`sample_reference.py` inverts the order of work: decode the photograph, measure its chroma
distribution per 30-degree hue arc, and judge the proposed accent against that measurement. It is
stdlib-only — zlib and struct decode the PNG — so this needs no imaging library, no key and no
network, like everything else here.

The three gates it adds are `subject-holds-chroma-peak`, `accent-chroma-matches-reference` and
`accent-hue-is-anchored-in-reference`. Read `data/colour-gates.csv` for the thresholds. What they
caught on this repository's own bún bò menu is the clearest teaching case available:

| Measured | Value |
|---|---|
| Blue arc 240–270 in the three food references | 0.43, 1.35 and 4.44 percent of frame, mean chroma 0.056 to 0.088 |
| Highest chroma of any pixel in any of the three | 0.195 |
| Brand cobalt `#2A4BD7` | C 0.2165 — above the peak of every one of them |
| Blue arc, reference board → finished menu | 0.97 → 9.48 percent of frame, a factor of 9.8, mean chroma 0.091 → 0.130 |
| Most saturated pixel, reference board | `#DA4D06`, h 40.0, C 0.1882 — on the food |
| Most saturated pixel, finished menu | `#1651D9`, h 263.1, C 0.2162 — on the navigation rail |

The blue arc grew by a factor of nearly ten and the chromatic peak moved off the thing being sold onto
the furniture. That is `không hài hòa` stated as arithmetic rather than as taste, and it is the answer
to the question of why a palette that cleared nine gates still looked wrong. Run against the reference
board, the cobalt fails `subject-holds-chroma-peak` at ratio 1.15 and comes back for review on
`accent-chroma-matches-reference` at factor 1.55, and the script exits 2.

The annatto is the counter-example worth keeping. `#D9541E` at C 0.1784, h 39.8 passes all three gates
against the reference board and clears the chroma comparison against both bánh bột lọc and trà đào,
whose warm 30–60 arc genuinely holds 7.3 percent of the frame at p98 chroma 0.158 to 0.175. Against
bánh răng bừa, where that arc holds 0.35 percent, the same colour comes back for review instead — the
gate reports that this photograph cannot judge it rather than inventing a verdict. The procedure that
condemns one accent clears the other, which is the only reason to trust either result.

Two limits. A reference shot flat or under-saturated lowers the bar it sets, so a pass against a weak
photograph means nothing — look at the photograph before quoting the gate. And one frame is not a
brand: a colour this photograph never shows may still be carried by a room, a package or a tradition,
which is why the anchoring gate reviews and never fails.

## Which numbers are ours

Three grades, and the table states one per gate:

- `standard-requirement` — the three contrast gates. W3C WCAG 2.2 SC 1.4.3 and SC 1.4.11.
- `standard-requirement-with-house-threshold` — the colour-vision gate. SC 1.4.1 is the requirement
  and Machado, Oliveira and Fernandes (2009, IEEE TVCG) is the simulation; the 0.09 OKLab collapse
  distance is ours.
- `house-rule` — the other eight. Lightness separation, edge vibration, both chroma budgets, ramp
  evenness, and the three reference gates: chroma peak, accent chroma against the reference arc, and
  hue anchoring. No published threshold exists for any of them.

Eight of twelve being house rules is survivable only while two things stay true: the table says which
eight, and the gates that do fail mean something. If a client asks whether a number is a standard or
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
derivation is a comment in `plan_palette.py`; re-run the sweep and compare it with the comment rather
than trusting a remembered value.

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

## Reading the shipped palettes

`data/palettes.csv` holds thirty-six palettes with four roles each — `bg`, `ink`, `accent`,
`support` — plus what each is for, what it is wrong for, and the measured ratios. The original
twenty editorial palettes were joined by four food/VN rows and twelve mood rows (black-gold luxe,
Korean pastel, seventies retro, tropical, tech dark, neon nightlife, terracotta, navy monochrome,
two-ink riso, milk tea, herbal spa, Tết red-gold), every ratio computed, every accent carrying its
honest restriction in `accent_use`. Of the original twenty, six carry a review, and the reviews are
the instructive part:

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


---

<!-- Deep dossier merged from references/dossiers/colour-science-and-harmony.md (2026-08-06). Long-form research behind the working sections above. External facts retrieved 2026-07-29; re-check anything priced, versioned, or platform-specific.  -->

# Colour Science and Harmony for Brand and Food Imagery

## What this is for

You are not a colourist and you will not become one. You are the person who has to sign off a
palette, reject a photo, or tell a retoucher what is wrong — and be right. This dossier gives you
the physics and the decision rules behind those calls: which colour space a file must be in before
it leaves the building, why the "same" orange looks different on a phone and a menu card, why a
bowl of **bún bò Huế** photographs muddy under mixed light, and what contrast number makes text
over a food photo legal rather than merely pretty. Every operational claim carries an evidence
marker. Where a claim is craft rather than measurement, it says so.

Evidence markers used throughout:

- `[verified]` — page fetched and read, with URL and retrieval date.
- `[search-level]` — seen only in a search summary. Treat as a lead, re-check before betting money on it.
- `[illustrative]` — invented number used to make arithmetic followable. Not real data.
- `[UNVERIFIED - <what would close it>]` — a named gap.

Retrieval date for all sources in this document: **2026-07-29**.

---

# PART 1 — COLOUR SPACES THAT ACTUALLY MATTER

## 1.1 The four-space working model

Forget the long list of colour spaces. In a brand-and-food workflow there are exactly four that
change your decisions, plus one perceptual space you compute in but never ship.

| Space | Role in your workflow | Where it lives | What kills you |
|---|---|---|---|
| **sRGB** | The delivery default for anything on the open web | Web exports, social uploads, email, PowerPoint | Nothing — it is the safe floor. Its sin is being small. |
| **Display P3** | Wide-gamut delivery for Apple-ecosystem screens and modern browsers | App assets, hero images on your own site, video | Degrades unpredictably when the profile is stripped |
| **Adobe RGB (1998)** | Intermediate space for print-bound photography | RAW conversion, retouch masters, print PDFs | Looks *desaturated* if it reaches a browser as untagged data |
| **CMYK (a named profile, e.g. an ISO coated profile)** | Print output only | Menu cards, packaging, banners | Cannot reach saturated orange/green; ink limits |
| **Oklab / OKLCH** | Computation and palette construction, never delivery | Your design tokens, ramp generation | Nothing, if you convert out to sRGB before shipping |

### The numbers behind the sizes

- Adobe RGB (1998) "encompasses 52.1%" of the CIE 1931 chromaticity diagram; sRGB "encompasses
  approximately 35% of visible colors". Adobe RGB's gamma is approximately 2.2, precise value
  563/256 = 2.19921875, **without sRGB's linear segment near black**. White point is D65
  (x=0.3127, y=0.3290), with a reference monitor luminance of 160.00 cd/m². It was "designed to
  encompass most of the colors achievable on CMYK color printers", and its real advantage over
  sRGB is "richer cyans and greens". `[verified]` (source:
  https://en.wikipedia.org/wiki/Adobe_RGB_color_space, retrieved 2026-07-29)
- DCI-P3 "covers 53.6% of the CIE 1931 chromaticity diagram" and "86.9% of Pointer's gamut, while
  ... sRGB only covers 69.4%". **Display P3's gamut is approximately 50% larger than sRGB in
  volume and 25% in surface.** `[verified]` (source: https://en.wikipedia.org/wiki/DCI-P3,
  retrieved 2026-07-29)

Note the trap in those two bullets: **Adobe RGB (52.1%) and DCI-P3 (53.6%) are almost the same
*size* but different *shapes*.** Adobe RGB is stretched toward cyan-green (because it was built for
CMYK); P3 is stretched toward red-orange (because it was built for cinema and displays). For food
imagery this matters enormously: chilli oil red and cooked-tomato red are where P3 buys you
something and Adobe RGB does not. For a printed menu, Adobe RGB's cyan-green reach is the useful
part and P3's red reach is largely wasted.

### Decision rule 1 — which space to work in

```
Is the final destination print (offset, digital press, large format)?
  YES -> master in Adobe RGB (1998) 16-bit, convert to the printer's named CMYK profile at output
  NO  -> is the destination your own controlled surface (app, own site hero, video)?
           YES -> master in Display P3, deliver BOTH a P3 and an sRGB rendition
           NO  -> master and deliver sRGB 8-bit, profile embedded
```

**What breaks if ignored:** mastering in sRGB and later needing print means the cyan-green
information was thrown away at the start and cannot be recovered — greens in herbs go flat and
the printer's proof will look duller than your screen with no fix available except a reshoot.

## 1.2 Why a wide-gamut file degrades on export — the exact mechanism

Two independent failure modes. They look similar (colours are wrong) but have opposite symptoms.

**Failure mode A — the profile is stripped, data is left alone.** "Most modern web browsers assume
untagged images are in sRGB" and "web browsers assign sRGB to all untagged material, and then
convert into the monitor profile". If the file's numbers were actually Adobe RGB or ProPhoto,
"the colours may look washed out or dull" because "browsers are interpreting the Adobe RGB data as
sRGB, causing desaturation". Photoshop's "Save For Web/Export both strip the profile at default
settings". `[search-level]` — this is consistent across multiple vendor-community and tutorial
sources but I read only search summaries; flag for re-check against Adobe's current Export As
documentation. (search: "untagged image assumed sRGB Adobe RGB washed out desaturated export",
2026-07-29)

Why it desaturates rather than oversaturates: Adobe RGB's primaries sit *outside* sRGB's. A value
of `R=255` in Adobe RGB means "a redder red than sRGB's reddest". Reinterpreted as sRGB, `R=255`
now means only "sRGB's reddest" — a less saturated colour. Every channel gets pulled inward. The
image goes limp, and it goes limp *most* in the cyan-greens where Adobe RGB extends furthest.
That is exactly the herb-and-lime region of a Vietnamese food photo.

**Failure mode B — the data is converted, but with the wrong intent or no intent.** Here the
profile survives but the gamut mapping is crude. Out-of-gamut colours get clipped to the boundary,
which flattens gradients into posterised blocks. On a bowl of broth this shows up as the oily
highlight on the surface losing its ramp and becoming a single hard patch of orange.

**Failure mode C — the inverse: P3 data reinterpreted as sRGB.** Same arithmetic, same
desaturation direction. But the more common P3 complaint in practice is the opposite: an sRGB
asset placed next to a P3 asset on a P3 display, where the P3 asset looks *aggressively* more
saturated and the sRGB one looks dead. Nothing is broken; you have simply put two gamuts side by
side. `[illustrative]` example of the size of the effect: a brand red that reads as a confident
crimson in sRGB may look almost fluorescent when the same *numbers* are declared as P3 — the
numbers are identical, the meaning is not. That specific perceptual description is craft, not
measurement.

### Decision rule 2 — export contract

Every image that leaves your organisation must satisfall four:

1. **Profile embedded, not assumed.** If your tool has a checkbox called "Embed Color Profile",
   it is on. `[search-level]` Photoshop's Export As requires this to be checked manually.
2. **Converted, not assigned.** "Convert to Profile" changes the numbers to preserve the
   appearance. "Assign Profile" keeps the numbers and changes the appearance. For delivery you
   almost always want *convert*. `[search-level]`
3. **8-bit sRGB for the open web; 16-bit for anything that will be edited again.** 8-bit
   wide-gamut files are the worst of both worlds — the wider gamut spreads the same 256 steps over
   more colour, so smooth gradients (broth surface, out-of-focus background) band.
4. **A visible sanity check.** Open the exported file in a plain browser window, not your design
   tool. If it shifts, the pipeline is wrong.

**What breaks if ignored:** the single most common real-world outcome is a brand red that is
correct in the brand book, correct in the design file, and wrong in every Instagram post — because
one export step stripped a profile and nobody looked at the result outside Figma or Photoshop.

## 1.3 The CSS layer

Modern CSS can address these spaces directly. The `color()` function supports predefined spaces
including `srgb`, `srgb-linear`, `display-p3`, `display-p3-linear`, `a98-rgb`, `prophoto-rgb`,
`rec2020`, `rec2100-pq`, `rec2100-hlg`, `rec2100-linear`, plus CIE XYZ variants `xyz`/`xyz-d65`
and `xyz-d50`. Values outside 0–1 "are permitted but will be out of gamut for the given color
space", and support can be detected with the `color-gamut` media feature. Baseline: widely
available since May 2023. `[verified]` (source:
https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/color, retrieved 2026-07-29)

Practical pattern for a wide-gamut brand colour with a safe fallback:

```css
:root {
  --brand-chilli: #C2410C;                        /* sRGB fallback, always first */
}
@media (color-gamut: p3) {
  :root {
    --brand-chilli: color(display-p3 0.76 0.26 0.05);  /* [illustrative] values */
  }
}
```

The P3 numbers above are `[illustrative]` — invented to show the syntax. Real values must come
from converting your measured brand colour, not from guessing.

---

# PART 2 — WHY HSL LIES, AND WHAT OKLCH FIXES

## 2.1 The specific defect

HSL and HSV are trivial algebraic rearrangements of sRGB. They are not perceptual models and were
never claimed to be. The consequence, stated by the author of Oklab about HSV: an "HSV gradient
with constant saturation and value shows dramatic lightness variations across different hues".
CIELAB is better but still has a hue-prediction problem, "particularly for blue hues" — with
constant lightness and saturation, "yellow, magenta and cyan appear much lighter than red and
blue". `[verified]` (source: https://bottosson.github.io/posts/oklab/, retrieved 2026-07-29)

Concretely: `hsl(60 100% 50%)` (yellow) and `hsl(240 100% 50%)` (blue) have the same `L` value of
50%. They are nowhere near the same perceived lightness. Yellow is nearly the brightest thing
sRGB can produce; that blue is dark enough to carry white text.

You can check this against the WCAG relative-luminance weights, which are real photometry:
`L = 0.2126*R + 0.7152*G + 0.0722*B`. `[verified]` (source:
https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, retrieved 2026-07-29) Green
carries 71.52% of luminance, blue only 7.22%. Any model that treats "L=50%" as hue-independent is
ignoring a roughly ten-to-one weighting difference between the green and blue channels.

### What this does to your work

| Task | HSL failure | Visible symptom |
|---|---|---|
| Generate a tint/shade ramp by stepping `L` | Steps are perceptually uneven and hue drifts | The 300 and 400 steps of your blue look identical; the 600 and 700 steps of your yellow look identical |
| Build a categorical palette at "equal saturation" | Yellow and cyan swatches dominate; blues and reds recede | Chart legends where one series screams and another disappears |
| Desaturate a colour toward grey | Lightness changes at the same time | "Muted" brand variant is also darker, breaking contrast compliance |
| Rotate hue for a complementary pair | The pair has mismatched lightness | Complementary scheme reads as one strong colour plus one weak one |

## 2.2 What OKLCH gives you

Oklab was designed to be an opponent colour space that "predict[s] lightness and chroma
orthogonally", enable smooth blending, and stay numerically stable. Measured against the Munsell
dataset it beats CIELAB on both metrics the author reports: **hue uniformity RMS error 0.49 vs
CIELAB's 0.69; chroma prediction RMS error 0.81 vs CIELAB's 1.84.** Unlike CIELAB and HSV, which
"introduce hue shifts toward purple when blending with white", Oklab produces uniform
transitions. `[verified]` (source: https://bottosson.github.io/posts/oklab/, retrieved 2026-07-29)

CSS `oklch()` syntax and ranges: `oklch(L C H [/ A])` where **L is 0 to 1 (or 0%–100%),
C is 0 to about 0.4 as a practical maximum (100% maps to 0.4, theoretically unbounded), H is
0–360deg, A optional.** The `L` in `oklch()` is perceived lightness and differs from the `L` in
`hsl()`. Hue angles differ too: **in oklch, 0deg is approximately magenta and red is
approximately 41deg**, whereas in sRGB/HSL red is 0deg. `oklch()` can express colours outside
sRGB. Baseline: widely available since May 2023. `[verified]` (source:
https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/oklch, retrieved 2026-07-29)

That hue-angle offset is the single most common OKLCH mistake. If you port an HSL hue number
straight into `oklch()` you get the wrong colour and you will blame the space.

### Decision rule 3 — palette generation

- Generate ramps by **holding H, stepping L on a fixed schedule, and letting C fall off near both
  ends.** C must fall off because maximum available chroma shrinks as you approach black and white
  — asking for `oklch(0.95 0.25 41)` requests a colour that does not exist in any real gamut and
  you get a clipped, wrong result.
- A workable L schedule for a 9-step UI ramp: `0.97, 0.93, 0.86, 0.76, 0.65, 0.55, 0.45, 0.35,
  0.25`. `[illustrative]` — these are a sane starting shape, not a standard. Adjust once you see
  the ramp.
- **Cross-check every generated step against a real contrast calculation** in sRGB before shipping.
  OKLCH's `L` is perceptually uniform but WCAG's contrast ratio is computed from sRGB relative
  luminance with the 0.2126/0.7152/0.0722 weights `[verified]`, so equal OKLCH lightness steps do
  **not** produce equal WCAG ratios. `[UNVERIFIED - a published mapping table between OKLCH L and
  WCAG contrast ratio; I found none and would not trust one that ignores the surround]`

### Decision rule 4 — when HSL is still fine

HSL is acceptable for exactly two things: (a) a quick eyedropper conversation with a human ("make
it more red"), and (b) hue rotation where you will re-check lightness afterwards anyway. It is not
acceptable as the storage format for design tokens.

---

# PART 3 — HARMONY SCHEMES AND THEIR REAL FAILURE MODES

The schemes below are art-direction convention, taught in every colour course. Their *definitions*
are craft consensus rather than measurable fact; treat the definitions as `[illustrative]`
convention. The **failure modes** are the useful content, and are craft observations, not
measurements — I am labelling them as such rather than dressing them as science.

| Scheme | Definition (convention) | Real failure mode | Fix |
|---|---|---|---|
| **Monochromatic** | One hue, varying L and C | Everything reads as one flat field; no focal point; photography inside it looks like a mistake | Introduce a single neutral at very different L, or one small accent at high C (<5% of area) |
| **Analogous** | 2–4 adjacent hues | Adjacent hues at similar L merge into mush at small sizes and on phone screens | Force at least 0.15 OKLCH L separation between any two adjacent-hue elements that must be told apart |
| **Complementary** | Two opposing hues | Vibration/simultaneous-contrast buzz at hard edges; equal-area split makes the composition fight itself | Never 50/50. Use roughly 70/20/10 area (dominant / secondary / accent). Separate opposing hues with a neutral gutter |
| **Split-complementary** | Base + two hues flanking its complement | The two flanking hues are analogous to each other and collapse into one perceived colour | Differentiate the flankers by L, not by hue |
| **Triadic** | Three hues at ~120° | All three at full chroma = children's-toy palette; nothing recedes | Keep one at full C, drop the other two below C≈0.08 |
| **Tetradic / double-complementary** | Two complementary pairs | Four fighting hues; almost always ends up as visual noise | Demote two of the four to near-neutral tints; treat as a two-colour scheme with two accents |
| **Achromatic + single accent** | Neutrals plus one hue | Accent has to do all the work; if the accent fails contrast the whole system fails | Verify accent-on-neutral and neutral-on-accent contrast both pass before committing |

The wheel schemes above are the classical seven. The working catalogue is wider:
`data/colour-harmonies.csv` holds eighteen combination methods as numeric recipes — the seven
wheel schemes plus the methods designers actually reach for (60-30-10 proportion, warm field with
one cool cut and its mirror, two-ink riso duotone, pastel field with dark ink, jewel-on-dark,
earth-plus-pop, black-white-and-one, high-key, low-key, and sampling the palette from the hero
photograph). Each row states its OKLCH structure, area ratio, contrast rule, mood signal, failure
mode, fix, and a shipped palette that demonstrates it. Pick the method by what the surface must
signal, then pull or build the palette to match; the method row is the argument, the palette row is
the numbers.

## 3.1 The three failure modes that actually cost money

**1. Harmony computed in the wrong space.** A "complementary pair" derived by adding 180° in HSL
gives you two colours of mismatched perceived lightness (Part 2). The scheme is geometrically
correct and visually broken. Compute the rotation in OKLCH and then *equalise L deliberately* if
you want the pair to have equal weight, or *deliberately unequalise it* if you want hierarchy.
Either is a choice; HSL makes it an accident.

**2. Harmony that ignores area.** Every scheme above is a statement about hue relationships and
says nothing about proportion. Two colours in "perfect" complementary relation at 50/50 area is
an unstable, fatiguing composition. Area proportion is the variable that most reliably rescues a
scheme, and it is the one designers reach for last. `[illustrative]` starting proportions:
60/30/10 for calm, 70/20/10 for confident, 85/10/5 for editorial restraint.

**3. Harmony applied to the frame while ignoring the photograph.** This is the food-brand-specific
killer. Your palette is a background; the food is the foreground and it has its own palette that
you do not control. If your brand secondary is a mid-green and your dish is garnished with **rau
răm**, **húng quế** and **ngò gai**, the herbs and the brand colour are competing analogues at
similar L and the garnish stops reading as garnish. See Part 6.

## 3.2 Checklist — auditing a scheme in five minutes

- [ ] Convert every colour to OKLCH. Write down L for each. Are any two L values within 0.05 of
      each other while carrying different meaning? That is a merge risk.
- [ ] Compute area share of each colour in the actual layout, not the swatch sheet. Is anything
      at 40–60%? Rebalance.
- [ ] Desaturate the whole layout to greyscale. Does the hierarchy survive? If not, the scheme is
      carrying information in hue alone — see Part 8.
- [ ] Put the layout next to the three most likely competitor layouts. Does yours have a hue that
      none of them own? If not, the harmony is fine and the differentiation is zero.
- [ ] Render the layout at phone width and look at it at arm's length. Adjacent hues at similar L
      collapse first at small size.


---

# PART 4 — SIMULTANEOUS CONTRAST: HOW A BACKGROUND MOVES YOUR PRODUCT'S COLOUR

## 4.1 The effect, precisely

Simultaneous contrast is not an opinion. "A neutral gray target will appear lighter or darker than
it does in isolation when immediately preceded by, or simultaneously compared to, respectively, a
dark gray or light gray target." The chromatic version: a grey strip on a coloured background
"appears tinged with the contrasting color — appearing reddish on green, greenish on red". This was
documented in the 11th century by Ibn al-Haytham, who noted paint spots appear "almost black" on
white backgrounds but "paler than their true colour on black", and that leaf-green paint "may
appear clearer and younger on dark blue and darker and older on yellow". The probable mechanism
involves "neurons in the V4 area that have inhibitory connections to neighboring cells", though
whether the effect is physiological or psychological is debated. `[verified]` (source:
https://en.wikipedia.org/wiki/Contrast_effect, retrieved 2026-07-29)

The variables that control the *strength* of chromatic induction are named: **size of the
surrounding field, separation between colour and surround, similarity of chromaticity, luminance
difference, and structure of the surround.** `[verified]` (same source) The same source explicitly
does **not** give numerical magnitudes. `[UNVERIFIED - a quantitative induction model with
published coefficients, e.g. a CIECAM-family appearance model prediction of induction magnitude as
a function of surround area; I did not locate one and will not invent numbers]`

## 4.2 Translating the five variables into art direction

| Variable | Direction of effect | Operational lever |
|---|---|---|
| **Size of surround** | Bigger surround = stronger shift | A product shot on a full-bleed coloured background is maximally shifted. A product in a small inset with white margin is barely shifted. |
| **Separation** | Contact = strong; gap = weak | A 4–8 px white or neutral keyline around a product cutout kills most of the induction. This is why product catalogues use white space. |
| **Chromaticity similarity** | Similar hue = weaker apparent hue shift but higher merge risk | A same-hue surround does not push the product's hue much; it eats its edges instead. |
| **Luminance difference** | Larger difference = stronger lightness shift | A pale broth on a dark background looks *lighter and thinner*; on a light background it looks *deeper*. |
| **Structure of surround** | Textured/patterned surround = unpredictable local shifts | Never place a product cutout on a busy patterned background if the product's colour is a brand asset. |

## 4.3 Worked example — a fixed brand orange across four backgrounds

All perceptual descriptions below are **craft predictions from the induction rules above, not
measurements**. The colour values are `[illustrative]`.

Brand accent: an orange at approximately `oklch(0.68 0.17 55)` `[illustrative]`.

| Background | Predicted apparent shift in the orange | Consequence |
|---|---|---|
| Pure white `#FFFFFF` | Appears darker, slightly more saturated | Safest reference; use for the master swatch |
| Deep neutral `oklch(0.20 0 0)` | Appears lighter, brighter, more "neon" | Ads on dark UI look off-brand vs the print book |
| Complementary blue `oklch(0.45 0.14 250)` | Appears more saturated, slightly warmer | Maximum vibrance, maximum edge buzz |
| Analogous warm red `oklch(0.50 0.16 30)` | Appears yellower, less saturated | The brand orange stops reading as itself |

**Decision rule 5 — the reference-surround rule.** Define brand colours *with a stated surround*.
A brand book that says "Accent: #C2410C" is incomplete. It should say "Accent: #C2410C, specified
on white; on backgrounds darker than OKLCH L 0.35 use the compensated variant #B23A09."
`[illustrative]` compensated value.

**What breaks if ignored:** the brand guardian approves a swatch on a white page, the social team
uses it on a dark gradient, and the two teams argue for a year about whether the orange "drifted".
Nothing drifted. The surround changed.

## 4.4 The food-specific case: the bowl is the surround

In a food photograph the product's surround is not the background wall — it is the **bowl, the
table surface, and the immediately adjacent garnish**, in that order of influence, because those
subtend the largest angle next to the food.

- A white bowl makes broth read **darker and more concentrated**. Usually what you want for
  **bún bò Huế** or **phở** — it sells richness.
- A dark bowl (common in modern Vietnamese restaurant ceramics) makes the same broth read
  **lighter, thinner, greyer**, and it steals the darkest tone in the frame so the surface
  highlight loses its ramp.
- A blue-glazed bowl pushes the broth's brown toward orange, which can look artificial. Blue also
  carries an appetite penalty (Part 6).
- A warm terracotta or unglazed clay surround pushes broth *toward neutral*, which reads as
  "muddy". This is the most common failure in Vietnamese food photography styled for a "rustic"
  mood.

**Decision rule 6:** for broth-forward dishes the vessel should be either near-neutral light
(OKLCH L above 0.85, C below 0.02) or near-neutral dark (L below 0.25, C below 0.02). Any chromatic
vessel is a deliberate bet and must be tested against the specific dish, not adopted as a house
style.

---

# PART 5 — COLOUR TEMPERATURE AND WHITE BALANCE

## 5.1 The Kelvin scale, with real numbers

| Source | CCT (K) |
|---|---|
| Match flame | 1,700 |
| Candle flame | 1,850 |
| Sunrise / sunset | 1,850 |
| Incandescent lamps (standard) | 2,400 |
| Incandescent lamps (soft white) | 2,550 |
| "Soft white" LED / CFL | 2,700 |
| Warm white LED / CFL | 3,000 |
| Horizon daylight | 5,000 |
| Daylight, overcast | 6,500 |
| Clear blue sky (shade) | 15,000–27,000 |

`[verified]` (source: https://en.wikipedia.org/wiki/Color_temperature, retrieved 2026-07-29)

The terminology is inverted relative to physics: **lower colour temperatures (2,700–3,000 K) are
called "warm" (yellowish) and temperatures above 5,000 K are "cool" (bluish) — "exactly the
opposite of black-body radiation."** The terms reflect psychological association, not heat.
`[verified]` (same source)

**CCT is not CRI.** Colour temperature "describes the color of light by comparing it to an
idealized opaque, non-reflective body". CRI is a separate measure of "how well a light source's
illumination of eight sample patches compares to the illumination provided by a reference source".
`[verified]` (same source)

That distinction is the one that costs you food shoots. **A 3,000 K light can be perfectly "warm"
and still render food badly**, because CCT says nothing about whether the spectrum has a hole in
it. A cheap LED with a deficient red region renders **ớt** (chilli), **cà chua** (tomato) and
cooked pork dull and slightly brown no matter how you white balance, because the light contains
insufficient energy at those wavelengths to be reflected. You cannot fix a missing wavelength in
post — there is no signal to amplify.

**Decision rule 7 — lamp spec for food.** Specify both numbers when hiring or buying: CCT within
±200 K of target, and CRI as high as budget allows. `[UNVERIFIED - the specific CRI or TM-30
Rf/Rg threshold below which food photography visibly degrades; I found no authoritative threshold
and will not invent one. What would close it: a published photographic or lighting standard, or a
controlled comparison test.]` Practical substitute for the missing threshold: photograph a known
red object (a chilli) under the candidate light and under window daylight and compare. If the
chilli loses saturation under the lamp, reject the lamp.

## 5.2 How white balance actually works, and what mixed light does

White balance is "the adjustment of color intensities to render neutral colors (white, gray)
correctly". The dominant mechanism is **channel scaling**: if a surface believed to be white reads
R=240, you "multiply all red values by 255/240", and analogously for green and blue. The von Kries
refinement converts RGB into LMS space (representing the retina's three cone types), scales those
components independently, then converts back. Practical methods are lighting presets, automatic
algorithms, and custom white balance from a grey card. Wrong white balance produces a cast where
"everything in the image appears to have been shifted towards one colour", and flesh tones are the
critical case — off-balance, "the human subject can look sick or dead". `[verified]` (source:
https://en.wikipedia.org/wiki/Color_balance, retrieved 2026-07-29)

That page does not discuss mixed lighting and does not name the D50/D55/D65/A standard illuminants.
`[verified]` (same source — explicit absence, noted so you do not cite it for those)

### Why mixed lighting is structurally unfixable

Read the mechanism again: white balance is **one global set of three multipliers applied to the
whole frame.** That is the entire problem.

If your scene has a 3,000 K tungsten lamp on the left and 6,500 K overcast window light on the
right, there exists **no single triple of multipliers** that neutralises both. Correct for the
tungsten and the window side goes blue. Correct for the window and the tungsten side goes orange.
Split the difference and both sides are wrong, plus the middle of the frame — where the food is —
sits in a colour that matches nothing.

Severity scales with the *ratio* of the temperatures, not their difference. 3,000 K vs 6,500 K is a
factor of about 2.2 — violent. 5,000 K vs 6,500 K is a factor of 1.3 — usually survivable and often
invisible once balanced to the dominant source.

### Decision rule 8 — the single-source rule

```
Count light sources on the food that differ by more than ~500 K.
  0 or 1  -> shoot; white balance off a grey card placed where the food is
  2       -> kill one. Switch it off, gel it to match, or flag it out.
  3+      -> stop. The shot will be unusable. Reset the set.
```

**What breaks if ignored:** the broth's brown and the herb's green land on opposite sides of the
frame under different illuminants; after white balance one is right and the other is either
green-grey or orange-brown. Retouchers "fix" this with local colour adjustments — expensive,
inconsistent across a shoot, and it produces a set of images that do not match each other. That is
fatal for a menu or a delivery-app listing where images sit in a grid and are compared directly.

### Practical gelling arithmetic

The standard studio move is to gel the mismatched source. `[search-level]` — gel families and their
mired-shift ratings are well established in cinematography practice but I did not fetch a
manufacturer table, so **do not quote specific gel product designations from this document.**
`[UNVERIFIED - a fetched manufacturer filter table giving mired shift values. What would close it:
reading current filter technical data from a lighting-filter manufacturer.]`

The conceptually correct unit for gel arithmetic is the **mired** (micro reciprocal degree,
10^6/K), because equal mired shifts are roughly equal *perceptual* shifts while equal Kelvin shifts
are not. 2,000 K -> 2,500 K is a large visible change; 6,000 K -> 6,500 K is a small one, despite
both being 500 K. `[search-level]` — standard photographic-science content; re-check against a
colour-science textbook before republishing the definition.

## 5.3 Temperature as a brand variable

Colour temperature is not only a technical setting; it is a mood control you can specify in a brief.

| Target look | Reads as | Fits |
|---|---|---|
| 2,700–3,200 K look | Evening, intimate, indulgent, sit-down | **Bún bò Huế** at dinner, **lẩu** (hotpot), bar food, dessert |
| 4,000–4,500 K look | Neutral-warm, appetising, honest | Menu photography, delivery-app hero images |
| 5,000–5,600 K look | Daylight, fresh, clean | **Gỏi cuốn**, salads, fresh herbs, beverages, packshots on white |
| 6,500 K+ look | Cold, retail, unappetising for hot food | Almost never for cooked food; acceptable for iced drinks |

**Decision rule 9:** write the intended look temperature into the shoot brief as a number and grade
the whole set to it. A set graded to a consistent target survives a grid; a set graded shot-by-shot
to "whatever looked nice" does not.


---

# PART 6 — HOW FOOD COLOUR READS ON CAMERA

## 6.1 The three pigment systems you are actually photographing

Almost all the colour in a Vietnamese dish comes from three chemistries. Knowing which one you are
looking at tells you whether a colour problem is fixable on set, in the kitchen, or not at all.

### (a) Melanoidins — the browns

The Maillard reaction "typically proceeds rapidly from around 140 to 165 °C (280 to 330 °F)" and
produces **melanoidins**, the complex compounds "responsible for the brown color and distinctive
flavor in browned foods". It is chemically distinct from caramelisation: Maillard is amino acids
reacting with reducing sugars, caramelisation is "the pyrolysis of certain sugars". Above the
Maillard range, caramelisation dominates, then pyrolysis — burning. `[verified]` (source:
https://en.wikipedia.org/wiki/Maillard_reaction, retrieved 2026-07-29)

**Operational consequence:** the appetising brown on grilled pork for **bún thịt nướng**, on
**chả**, on roast **vịt**, and the depth of a long-simmered **nước dùng** are melanoidin colour.
Melanoidins are **broad-spectrum absorbers** — they are low-chroma, mid-to-low-lightness browns.
This is why brown food is the hardest thing to photograph well: it is intrinsically close to
neutral, so it sits right where any white-balance error or any warm/cool cast shows up worst. A
2 % green cast in a saturated red is invisible; the same cast in a brown makes it look grey and
stale.

**Rule:** browns need *contrast partners*, not more saturation. Add a light neutral (rice noodle,
white bowl rim, **bún**), a high-chroma small accent (chilli, spring onion), and a specular
highlight. Do not try to make brown look brown by pushing saturation — you get orange.

### (b) Chlorophylls — the greens, and why they die

Chlorophyll has a magnesium atom at its centre. Heat and acid displace it, converting chlorophyll
to **pheophytin**, which is "a drab olive green". Specifically, "chlorophyll a turns into grey-green
pheophytin a and chlorophyll b turns into yellowish pheophytin b". Above about 60 °C, chloroplast
membranes begin to break down, exposing chlorophyll to the plant's own acids; "a rapid accumulation
of pheophytins in cooked or canned foods is a result of the combined action of heat and acid release
after cell rupture". Low pH greatly accelerates the change. `[search-level]` — this is consistent
food-science content across multiple sources including a ScienceDirect topic page and an
extension-service PDF, but I read search summaries rather than the primary papers. (search:
"chlorophyll pheophytin conversion green vegetables acid heat", 2026-07-29) `[UNVERIFIED - the
primary literature time-temperature curves. What would close it: fetching the ScienceDirect paper
on pH and chlorophyll degradation in blanched green peas.]`

**Operational consequence — this is the single most actionable fact in this dossier for Vietnamese
food.** Every fresh green in a Vietnamese dish is a clock running against you:

| Green element | Threat | Shooting-order consequence |
|---|---|---|
| **Rau răm**, **húng quế**, **tía tô**, **ngò gai** placed on hot broth | Heat from below converts chlorophyll to pheophytin | Add herbs **last**, seconds before the frame. Have a second plated set ready. |
| **Chanh** (lime) juice squeezed onto greens | Acid accelerates conversion | Never pre-squeeze for camera. Squeeze after the shot or fake it. |
| **Giá** (bean sprouts) and **rau muống** in hot liquid | Wilting plus pigment loss | Keep raw and cold; place dry on top. |
| Blanched greens | Bright immediately after blanching, olive within minutes | Shoot within the first minute or use an ice-bath hold. |

**What breaks if ignored:** the herbs read olive-grey. In OKLCH terms they lose chroma and shift
hue toward yellow, so they stop contrasting with the broth's brown and the dish loses its freshness
signal entirely. No amount of retouching restores it convincingly, because selective green
saturation on a dull green produces a plastic, uniform green that looks fake.

### (c) Carotenoids and capsanthin — the reds and oranges

The red-orange of **ớt** (chilli), **dầu ớt** / **sa tế** (chilli oil), **cà rốt**, **gấc** and the
orange sheen on **bún bò Huế** broth comes from carotenoid-family pigments, which are fat-soluble.
`[search-level]` — general food-chemistry knowledge; I did not fetch a primary source for the
specific pigment identities in these ingredients. `[UNVERIFIED - primary source naming capsanthin
as the dominant pigment in Vietnamese chilli oil preparations. What would close it: fetching a food
chemistry reference on Capsicum pigments.]`

**Operational consequences:**

- Because they are **fat-soluble**, they concentrate in the oil layer. On broth this creates a
  **thin, high-chroma film floating on a low-chroma brown** — the most valuable colour event in the
  frame. Light it to make that film specular. Kill it and the bowl goes dead.
- They are **narrow-band reflectors in the long-wavelength region**, which means they are the first
  thing destroyed by a low-CRI light with a red deficiency (Part 5.1) and the first thing to clip
  in a small gamut (Part 1.1).
- Saturated reds are also the **first thing to clip in sRGB and in CMYK**. A chilli oil highlight
  that is beautiful in Adobe RGB may be a flat, detail-free patch of red after sRGB conversion —
  the shape of the oil droplet disappears because every pixel hits the same clipped value.

**Rule:** expose so the reddest pixel in the chilli oil retains at least a little separation from
maximum, and check the red channel histogram, not the luminance histogram. Luminance histograms
hide red clipping because red carries only 0.2126 of luminance weight `[verified]` (WCAG luminance
formula, source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, retrieved
2026-07-29) — a fully clipped red channel barely moves the luminance histogram.

## 6.2 The Vietnamese-dish colour audit

Use this before approving any dish photograph. Each row is a colour job the frame must do.

| Job | What to look for | Fail symptom |
|---|---|---|
| **Broth depth** | Broth reads clearly darker than the noodles and the bowl | Broth and bowl at similar L -> dish looks watery |
| **Oil film** | A distinct high-chroma orange/red band with specular highlights | No specular -> broth looks cold and congealed |
| **Herb freshness** | Greens at high chroma, hue clearly on the green side of yellow | Olive/grey-green -> pheophytin, reshoot |
| **Chilli accent** | Small area, highest chroma in the frame, unclipped | Clipped flat red -> no texture, reads as a sticker |
| **Noodle/rice highlight** | Near-neutral light element to anchor white balance | Warm-tinted "white" -> whole frame reads jaundiced |
| **Protein browning** | Melanoidin brown with visible grill/sear structure | Flat uniform brown -> underexposed or low-CRI light |
| **Aromatic garnish** | Spring onion, fried shallot: mid-chroma yellow-greens and golds | Merged into the broth -> no separation, add a lighter counter-tone |

## 6.3 Which backgrounds kill appetite appeal

Here the evidence is genuinely mixed and you should know it, because this is an area where
marketing writing routinely overclaims.

**What is actually established in the source I read:** A study of **448 women aged 18–35** across
two experiments, viewing food images and rating desire to eat on a 7-point scale, found that in
Experiment 1 **all colour-manipulated versions of the food items (red, blue, black-and-white)
significantly reduced appetite compared to the original colour (p < 0.001)**, and colour
*suggestions* enhanced the appetite reduction for blue and black-and-white (p < 0.047). Red with
suggestion showed no significant difference from red without. Critically, in **Experiment 2 there
were no significant effects of background colour on food wanting.** The authors themselves note
that "research on the effects of red/blue food coloring on the wanting and liking of food has
produced heterogeneous results". `[verified]` (source:
https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.589826/full, retrieved
2026-07-29)

Read that carefully, because it cuts against the folk wisdom: **colouring the food itself reduced
appetite; colouring the background did not.** Any claim that "blue backgrounds suppress appetite"
does not follow from this study — this study found the opposite for backgrounds.

**What is search-level and softer:** Blue is rare in natural foods; blue-dyed food is reported less
appealing; and one study is reported to have found blue lighting "significantly" decreased how much
men ate, with no effect in women. `[search-level]` — I saw this only as a search-result summary,
including a publisher media-coverage page. (search: "blue food color appetite suppressant research",
2026-07-29) `[UNVERIFIED - the primary paper, its sample size and effect size. What would close it:
fetching the study in the journal *Appetite* referenced by that media-coverage page.]` Popular
attributions of these effects to named researchers appear in secondary sources; **I am not repeating
attributions I did not verify against the primary papers.**

### The defensible operating rules

Given the evidence above, here is what I will actually assert, separating grounded from craft:

**Grounded (from the verified study):**
1. Do not recolour the food. Any hue manipulation applied to the food itself — including heavy
   creative grading, "blue-hour" grades over hot dishes, or duotone treatments — is the
   manipulation shown to significantly reduce appetite ratings. `[verified]` basis.
2. Do not desaturate the food. Black-and-white significantly reduced appetite in the same
   experiment. `[verified]` basis. Monochrome food photography is an art choice that costs you
   appetite appeal; make it knowingly.
3. Be sceptical of background-colour claims, including ones in your own brand deck. The verified
   experiment found no significant background effect. `[verified]` basis.

**Craft, not measured — labelled as such:**
4. Backgrounds fail food photographs for *contrast and induction* reasons (Part 4), which is a
   different and better-supported mechanism than "appetite psychology". The practical failures are:
   - Background at similar L to the food -> the dish has no silhouette.
   - Background at similar hue to the dish's dominant colour -> the dish disappears into it. A
     warm terracotta background behind a brown broth is the classic Vietnamese-food failure.
   - Background at high chroma in the *complement* of the food -> edge vibration and the food's own
     colour shifts (Part 4.3).
   - Cool, high-CCT, low-chroma grey-blue backgrounds behind hot food -> the food's warmth reads as
     a cast rather than as heat, because the eye takes the large neutral field as its white
     reference. This is an induction/adaptation argument, not an appetite-psychology one.
5. The reliably safe background family for Vietnamese hot dishes: near-neutral, slightly warm,
   either clearly lighter (OKLCH L 0.80+) or clearly darker (L 0.20-) than the broth, with chroma
   under about 0.03. `[illustrative]` thresholds — a defensible starting point, not a measured
   optimum.

**Decision rule 10 — background test.** Before the shoot, photograph the *background material
alone* and the *dish alone*, convert both to OKLCH, and compare. If |ΔL| < 0.15 or ΔH < 30° at
similar chroma, change the background. This takes ten minutes and prevents the most expensive
category of food-photography failure.


---

# PART 7 — WCAG CONTRAST FOR TEXT OVER IMAGERY

## 7.1 The numbers, exactly

From WCAG 2.2 Success Criterion 1.4.3 Contrast (Minimum), Level AA:

- Standard text and images of text: **contrast ratio of at least 4.5:1**.
- Large-scale text and images of large-scale text: **at least 3:1**.
- "Large scale" means **at least 18 point, or 14 point bold**, or "font size that would yield
  equivalent size for Chinese, Japanese and Korean (CJK) fonts".
- Point-to-pixel: **1 pt = 1.333 px, therefore 14 pt and 18 pt are equivalent to approximately
  18.5 px and 24 px**.
- Contrast ratio formula: **(L1 + 0.05) / (L2 + 0.05)**, where L1 is the relative luminance of the
  lighter colour and L2 of the darker.
- Relative luminance: **L = 0.2126 × R + 0.7152 × G + 0.0722 × B**, with per-channel conditional
  conversion based on the **0.04045** threshold.
- Exceptions: **incidental text** — "text or images of text that are part of an inactive user
  interface component, that are pure decoration, that are not visible to anyone, or that are part
  of a picture that contains significant other visual content, have no contrast requirement". And
  **logotypes** — "text that is part of a logo or brand name has no contrast requirement".

`[verified]` (source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, retrieved
2026-07-29)

Note what is *not* on that list: there is no AAA number in the material I fetched, and there is no
separate non-text/UI-component number. Those exist in WCAG as separate success criteria (1.4.6 and
1.4.11) which I did **not** fetch. `[UNVERIFIED - the exact thresholds of WCAG 1.4.6 Contrast
(Enhanced) and 1.4.11 Non-text Contrast. What would close it: fetching those two Understanding
pages. Do not quote 7:1 or 3:1 for those from this document.]`

## 7.2 The trap: "text over imagery" has no single contrast ratio

A contrast ratio is defined between **two colours**. A photograph is thousands of colours. So the
question "does this headline pass over this food photo?" is malformed until you decide *which*
background pixel you are measuring against.

The only safe interpretation: **the text must pass against the worst pixel it overlaps.** Not the
average. Not the pixel you happened to sample. If one letter's stroke crosses a bright specular
highlight on the chilli oil and the ratio there is 2.1:1, that glyph is illegible and the
composition fails, regardless of what the average says.

### Decision rule 11 — the four legitimate techniques, in order of preference

| Technique | How it works | Cost | When to use |
|---|---|---|---|
| **1. Reserve a plate** | Compose the shot with a deliberately empty, tonally uniform region for text | Requires planning at shoot time; free afterwards | Always the first choice. Brief it. |
| **2. Solid scrim / colour block** | Put the text on an opaque or high-opacity panel over the image | Covers image; can look like a compromise | Dense text, long copy, guaranteed compliance |
| **3. Gradient scrim** | Linear gradient from opaque at the text edge to transparent | Needs enough depth; a shallow gradient fails at the text's far edge | Bottom-anchored titles over full-bleed photography |
| **4. Text shadow / outline** | Adds a local dark or light halo | Degrades type quality; hard to keep consistent; easy to over-apply | Last resort, small amounts of text |

**What breaks if ignored:** the technique that fails most often in practice is a gradient scrim that
is too shallow. The designer checks contrast at the *baseline* of the headline, where the scrim is
darkest, and passes. The ascenders of the top line sit where the gradient is already 30% opacity and
the ratio there is 2.5:1. Always measure at the **top of the tallest glyph on the topmost line**,
which is where any bottom-anchored gradient is weakest.

### Worked scrim arithmetic

Setup: white text `#FFFFFF` over a broth photograph. The brightest pixel under the text is a
specular highlight measured at sRGB `#F2E3C8`.

Step 1 — relative luminance of the highlight. Using the WCAG channel conversion and the
0.2126/0.7152/0.0722 weights `[verified]`, the linearised channels for `#F2E3C8` are approximately
R 0.871, G 0.768, B 0.591 `[illustrative]` — I am stating these as illustrative because I computed
them by hand rather than with a tool, and the arithmetic below is for showing the *shape* of the
calculation, not for citation.

L_highlight ≈ 0.2126(0.871) + 0.7152(0.768) + 0.0722(0.591) ≈ 0.185 + 0.549 + 0.043 ≈ **0.777**
`[illustrative]`

Step 2 — white is L = 1.0 by definition.

Step 3 — ratio = (1.0 + 0.05) / (0.777 + 0.05) = 1.05 / 0.827 ≈ **1.27:1** `[illustrative]`

That is catastrophic. White text on that highlight is invisible. It needs 4.5:1, so it needs a
background luminance L2 satisfying (1.05)/(L2 + 0.05) ≥ 4.5, i.e. L2 ≤ 1.05/4.5 − 0.05 =
0.2333 − 0.05 = **0.183**. The background under the text must be brought from L ≈ 0.777 down to
L ≤ 0.183 — a very heavy scrim, roughly a 75%-opacity black overlay in the worst region.
`[illustrative]` arithmetic throughout; verify with a real contrast tool before shipping.

**The lesson from the arithmetic:** any specular highlight in the text zone forces a scrim so heavy
that it destroys the photograph underneath. Therefore the real fix is technique 1 — **keep
highlights out of the text zone at shoot time.** That is a lighting and composition instruction, not
a design instruction, and it must be in the shoot brief.

## 7.3 The logo and "incidental text" exceptions — how far they actually go

Both exceptions are real and quoted above `[verified]`. Two cautions:

1. The logotype exception covers "text that is part of a logo or brand name". It does **not** cover
   your tagline, your price, your call-to-action, or your address set in the brand typeface.
2. The incidental exception covers text "that is part of a picture that contains significant other
   visual content". A photograph of a shopfront with the shop's name on the sign is incidental. A
   headline you composited on top of a photograph is not — you authored it, it carries meaning, and
   it is in scope.

**Decision rule 12:** if the text conveys information a user needs, assume it is in scope and meet
4.5:1 (or 3:1 at ≥24 px / ≥18.5 px bold). Do not architect a campaign around an exception.

## 7.4 APCA and WCAG 3 — do not switch yet

As of the W3C's April 2026 Editor's Draft, the specification carries an editor's note stating
**"The contrast algorithm used in WCAG 3 is yet to be determined."** APCA is **not** part of WCAG 3;
it was marked for removal in early 2023 after failing to gain working-group support and was pulled
from the July 2023 working draft, per the principle that "exploratory content that does not gain WG
support ... is automatically removed". The recommendation is to choose colours conforming to
**WCAG 2** even if you use experimental algorithms, and to document any deviations. WCAG 3 is
"years away from completion — potentially 2030 or later". `[verified]` (source:
https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html, retrieved 2026-07-29)

For context on what APCA is: it outputs a lightness contrast value written as **Lc** on a scale from
0 to roughly ±106, where positive Lc means dark text on light background and negative means light on
dark; commonly cited guidance is **Lc 90+ for columns of body text and Lc 75 as a practical
minimum**. `[search-level]` — from search summaries of APCA's own documentation and third-party
guides; I did not fetch the APCA documentation directly. `[UNVERIFIED - the current official APCA
Lc threshold table. What would close it: fetching git.apcacontrast.com documentation.]`

**Decision rule 13:** WCAG 2.2 ratios are the compliance floor today. APCA may be used as a
*secondary* sanity check — it is better at flagging the specific case of light text on dark
backgrounds, which WCAG 2 handles poorly — but never as a justification for shipping a pair that
fails 4.5:1.

---

# PART 8 — COLOUR-BLIND-SAFE PALETTE CONSTRUCTION

## 8.1 Prevalence — the numbers that justify the budget

| Condition | Males | Females |
|---|---|---|
| Dichromacy (total) | 2.4% | 0.03% |
| — Protanopia | 1.3% | 0.02% |
| — Deuteranopia | 1.2% | 0.01% |
| — Tritanopia | 0.008% | 0.008% |
| Anomalous trichromacy (total) | 6.3% | 0.37% |
| — Protanomaly | 1.3% | 0.02% |
| — Deuteranomaly | 5.0% | 0.35% |
| — Tritanomaly | 0.0001% | 0.0001% |

"As many as 8 percent of men and 0.4 percent of women experience congenital color deficiency" among
those of Northern European ancestry. `[verified]` (source:
https://en.wikipedia.org/wiki/Color_blindness, retrieved 2026-07-29). The same page does not break
prevalence down by other ethnicities. `[verified]` explicit absence.

The US National Eye Institute states "about 1 in 12 men have color vision deficiency" and that men
have much higher risk than women; it names three types — red-green (the most common), blue-yellow,
and complete colour vision deficiency. `[verified]` (source:
https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness,
retrieved 2026-07-29)

**Important caveat for a Vietnamese-market brand:** the 8%/0.4% figure is explicitly scoped to
Northern European ancestry. `[UNVERIFIED - prevalence of congenital colour vision deficiency in
Vietnamese or broader East/Southeast Asian populations. What would close it: an epidemiological
study of CVD prevalence in Vietnam. Do not assume the European figure transfers.]` Design for it
anyway — the cost of a CVD-safe palette is near zero and the failure mode is a customer who cannot
tell your "sold out" state from your "available" state.

## 8.2 The confusion pairs — what actually gets mixed up

**Red-green deficiency (protan and deutan):** cyan and grey; rose-pink and grey; blue and purple;
yellow and neon green; red, green, orange and brown. **Blue-yellow (tritan):** yellow and grey;
blue and green; dark blue/violet and black; violet and yellow-green; red and rose-pink.
`[verified]` (source: https://en.wikipedia.org/wiki/Color_blindness, retrieved 2026-07-29)

Two of these deserve a food-brand flag:

- **"Red, green, orange, and brown" all confusable in one cluster.** That cluster is the entire
  colour palette of a Vietnamese hot dish. A protan or deutan viewer cannot use hue to separate
  chilli from herb from broth. Freshness must therefore be signalled by **lightness and texture**,
  not hue: the herb must be visibly *lighter* than the broth and visibly *leafy*, not merely
  *greener*.
- **"Blue and purple"** — if your brand uses a blue primary with a purple secondary, roughly one
  man in sixteen sees one colour.

## 8.3 The Okabe–Ito palette

The most widely cited colour-blind-safe categorical palette. Eight colours plus an optional
neutral grey: Orange `#E69F00`, Sky Blue `#56B4E9`, Bluish Green `#009E73`, Yellow `#F0E442`,
Blue `#0072B2`, Vermillion `#D55E00`, Reddish Purple `#CC79A7`, Black `#000000`, plus neutral grey
`#999999`. Proposed by Masataka Okabe and Kei Ito in the Color Universal Design guide, intended to
remain distinguishable under deuteranopia, protanopia and tritanopia. `[search-level]` — the hex
values above are consistent across several independent visualisation-library and blog sources, but
when I fetched the authors' own Color Universal Design page it **did not expose RGB or CMYK values
in its accessible text**; it names the colours only as vermilion, yellow, orange shades, bluish
green, reddish purple, sky blue and blue. `[verified]` for that absence (source:
https://jfly.uni-koeln.de/color/, retrieved 2026-07-29). `[UNVERIFIED - the hex values as published
by Okabe and Ito themselves. What would close it: locating the figure/table in the original CUD
document, or the values as embedded in a package that cites the original directly.]` Treat the hex
list as a well-attested community standard rather than as a primary citation.

## 8.4 The Color Universal Design rules — the actually authoritative part

From the authors' own page `[verified]` (source: https://jfly.uni-koeln.de/color/, retrieved
2026-07-29):

1. **Redundant coding.** "Use not only different colors but also a combination of different shapes,
   positions, line types and coloring patterns."
2. **Contrast and brightness.** Avoid situations where "texts and objects are obscured with the
   background"; maintain sufficient contrast in brightness and saturation; avoid combinations such
   as red characters on green backgrounds, which "appear identical to colorblind viewers".
3. **Colour selection strategy.** Use "warm" and "cool" colours alternately. When combining two
   warm or two cool colours, apply "distinct differences in brightness or saturation". Avoid
   low-saturation or low-brightness combinations.

The overarching principle: colour should **enhance** rather than solely carry information, working
alongside shape, pattern and position.

## 8.5 Construction procedure

**Decision rule 14 — build a CVD-safe palette in six steps.**

1. **Decide how many categories you actually need.** More than about six categorical colours is a
   design failure regardless of CVD; the eye cannot hold the legend.
2. **Alternate warm and cool** around the sequence, per CUD rule 3. `[verified]`
3. **Enforce a lightness ladder.** Assign each category a distinct OKLCH L, separated by at least
   0.10, so that the palette survives greyscale conversion. This directly implements CUD rule 2
   using a perceptual lightness metric.
4. **Simulate.** Run the palette through protanopia, deuteranopia and tritanopia simulation. Check
   every *pair*, not the set as a whole — n colours means n(n−1)/2 pairs; 6 colours = 15 pairs.
5. **Add redundancy for anything load-bearing.** Icon shape, label, pattern, position. Per CUD
   rule 1. `[verified]`
6. **Greyscale test as the final gate.** Print the layout in black and white. Anything that becomes
   ambiguous was carrying information in hue alone.

**What breaks if ignored:** in a food-delivery or menu context the specific failures are: sold-out
vs available states distinguished only by red/green; spice-level indicators distinguished only by a
red ramp (a protan viewer sees a near-flat ramp); and category tags on a menu distinguished only by
pastel hue at identical lightness — which collapses for CVD viewers *and* for everyone else on a
sunlit phone screen.

## 8.6 A note on simulation tools

Simulation is essential but approximate: it models dichromacy well and *anomalous* trichromacy —
which is the larger population at 6.3% of males vs 2.4% dichromacy `[verified]` — only crudely,
since anomalous trichromats retain partial discrimination that varies by individual. Passing a
dichromacy simulation is a conservative test: if it passes there, anomalous trichromats will
generally do at least as well. `[UNVERIFIED - a validated model of anomalous trichromacy
discrimination sufficient for design QA. What would close it: colour-science literature on
anomaloscope-calibrated simulation.]` I am not naming specific simulator products, because I did
not verify their current availability or algorithms.


---

# PART 9 — BUILDING A BRAND PALETTE THAT SURVIVES PRINT, SCREEN AND A PHONE CAMERA

This is the practical core. The goal is a palette where the same colour name means the same thing on
a menu card, on a phone screen, and in a photograph a customer takes of your restaurant and posts.

## 9.1 The three constraints, stated as inequalities

**Constraint A — print gamut.** CMYK cannot reach the saturated orange, saturated green, or
saturated violet that sRGB can. Adobe RGB was explicitly "designed to encompass most of the colors
achievable on CMYK color printers" `[verified]` — meaning the CMYK gamut is *inside* Adobe RGB, and
notably narrower in the reds and oranges than in the cyan-greens.

**Constraint B — ink limit (TAC).** Total Area Coverage is the sum of the four CMYK percentages at
any single point. For offset, "the ink limit is typically set to 300%", with typical limits of
280–320%; one manufacturer states "the maximum TAC for any part of an art file is 320%". Exceeding
TAC increases dry time, causes smudging, paper warping and excess ink use. A commonly cited rich
black is **C60 M40 Y40 K100 = 240% TAC**; converting the darkest possible Lab black (0,0,0) into an
ISO coated 300% profile yields approximately **C78 M68 Y58 K95, total 299%**. `[search-level]` —
these figures were consistent across several printing-industry sources in search summaries, but I
did not successfully fetch a primary source (one returned HTTP 403). `[UNVERIFIED - the exact TAC
figure in ISO 12647-2 and your own printer's stated limit. What would close it: the ISO standard
text, or a written spec from the actual print vendor. **Always ask the printer; do not use a number
from this document.**]`

**Constraint C — the phone camera.** Your customer's phone applies automatic white balance, automatic
exposure, and vendor-specific tone and saturation processing that you do not control. A brand colour
that depends on precise hue to be recognisable will not survive this. `[UNVERIFIED - the specific
colour-processing pipelines of current phone models; these are undocumented, vendor-specific, and
change with firmware. What would close it: nothing publicly available. Design around the
uncertainty instead of trying to characterise it.]`

## 9.2 The design consequence: choose colours by *robustness*, not by taste

**Decision rule 15 — the robustness hierarchy.** Rank candidate brand colours by how many
constraints they satisfy, then choose from the top of the list.

| Robustness tier | Character | Survives | Example family |
|---|---|---|---|
| **Tier 1 — highly robust** | Mid-lightness, mid-chroma, unambiguous hue family | Print, screen, camera, CVD, greyscale | A deep warm red; a dark teal; a mid ochre |
| **Tier 2 — robust with care** | High-chroma but inside CMYK reach | Print with a spot colour or careful profile; screen; camera | A saturated brick/vermillion |
| **Tier 3 — screen-only** | Beyond CMYK: electric orange, neon green, vivid violet | Screen only; degrades badly in print | Fluorescent accents |
| **Tier 4 — avoid as primary** | Very light or very dark, low chroma | Nothing reliably; disappears on camera | Pale pastels, near-blacks |

**The single most important structural decision:** your brand primary should be **Tier 1**. Put your
Tier 3 excitement in a *screen-only accent* that is explicitly documented as screen-only, and
specify its print substitute in the brand book.

**What breaks if ignored:** the classic disaster is choosing a brilliant sRGB orange as the primary,
approving it on a laptop, then discovering that (a) it converts to a duller, browner orange in CMYK,
(b) the printer's proof does not match the screen and the client rejects it, (c) a spot colour is
proposed to fix it, adding a print unit cost, and (d) photographs of the printed material taken on
phones show a fourth version of the colour. Four different oranges, one brand, no recovery path
except a rebrand.

## 9.3 Rendering intents — which one, and why

The four ICC rendering intents and what they do:

- **Perceptual** — "smoothly transitions out-of-gamut colors into the displayable range while
  preserving gradations, though it may distort in-gamut colors". Recommended for colour separation
  work; results "depend heavily on the profile maker's decisions".
- **Relative colorimetric** — prioritises fidelity with adjustment for media differences; "usually
  this is done in a way where hue and lightness are maintained at the cost of reduced saturation".
  Default on many systems; good for proofing.
- **Absolute colorimetric** — renders exact CIELAB values where possible; "colors outside of the
  proof print system's possible color are mapped to the boundary of the color gamut". Useful for
  matching specific brand colours but "may produce perceptually incorrect results".
- **Saturation** — "designed to present eye-catching business graphics by preserving the saturation
  (colorfulness)"; prioritises vividness over accurate hue.

Out-of-gamut colours must be "shifted to the inside of the gamut, as they otherwise cannot be
represented on the output device and would simply be clipped". `[verified]` (source:
https://en.wikipedia.org/wiki/Color_management, retrieved 2026-07-29)

**Decision rule 16 — intent selection.**

| Content | Intent | Reason |
|---|---|---|
| Photographs (food imagery) | **Perceptual** | Preserves gradation; the smooth ramp on broth and skin matters more than any single colour's exactness |
| Flat brand colours, logos, type | **Relative colorimetric** | Keeps hue and lightness; you want the brand red to stay red, and there are no gradients to protect |
| Same file containing both | **Split the file** | Export photography and flat art separately, or accept that one of them is compromised |
| Proofing a specific brand colour match | **Absolute colorimetric** | It is the only intent that will tell you the truth about whether the colour is reachable |
| Business charts | **Saturation** | Only place it belongs |

**What breaks if ignored:** using relative colorimetric on food photography clips the chilli-oil
highlight and the deepest broth shadow to flat patches; using perceptual on flat brand colours
shifts them slightly *even when they were in gamut*, so your printed brand red does not match your
printed brand red from the previous job.

## 9.4 The palette specification template

A brand palette that survives all three media is not a list of hex codes. It is a table with one row
per colour and one column per medium, plus a stated surround. Fill this in for every brand colour.

| Field | Example entry | Notes |
|---|---|---|
| Token name | `brand/chilli-600` | Semantic + numeric step |
| OKLCH (source of truth) | `oklch(0.55 0.17 38)` `[illustrative]` | The canonical definition; all others derive from it |
| sRGB hex | `#B23A0F` `[illustrative]` | For web, email, office documents |
| Display P3 | `color(display-p3 0.66 0.24 0.08)` `[illustrative]` | Optional; must have the sRGB fallback |
| CMYK, named profile | `C10 M80 Y95 K5` in `<printer's profile name>` `[illustrative]` | **Profile name is mandatory.** CMYK numbers are meaningless without it |
| Spot colour, if used | `<to be specified by printer>` | Do not guess a Pantone number |
| Specified surround | White | Per Decision rule 5 |
| Dark-surround variant | `#A03408` `[illustrative]` | For dark UI |
| Contrast: white text on it | `4.9:1` `[illustrative]` — verify | Must be measured, not assumed |
| Contrast: it on white | `4.9:1` `[illustrative]` | Same pair, but note it fails as *text* on white if below 4.5:1 |
| CVD status | Passes protan/deutan/tritan pairwise vs all other tokens | Per Decision rule 14 |
| Max TAC contribution | 190% `[illustrative]` | Must be under the printer's limit |
| Tier | Tier 1 | Per Decision rule 15 |

Any brand book that does not carry the profile name next to the CMYK values is not a brand book. It
is a suggestion.

## 9.5 Surviving the phone camera

You cannot control the phone's processing, so control the *scene* so that the processing has no
excuse to misbehave.

**Decision rule 17 — camera-robust brand surfaces.**

1. **Put a neutral in every branded surface.** A white or near-neutral element (a white logo field,
   a white plate rim, a white bowl) gives every auto-white-balance algorithm a correct reference. If
   the entire frame is warm terracotta, the phone will neutralise the terracotta and your brand
   colour comes out grey.
2. **Never let the brand colour be the largest field in a photographable environment.** Big
   monochrome fields drive auto white balance off a cliff, because the algorithm assumes the scene
   averages to neutral.
3. **Choose brand colours with margin from adjacent hue families.** A red that is 15° from orange
   will be photographed as orange by some phones. A red that is 40° from orange survives. `[illustrative]`
   angular thresholds — the principle is real, the numbers are invented.
4. **Do not rely on lightness alone for recognisability.** Auto exposure will move it.
5. **Test it.** Print the material, photograph it on three different phones under the venue's actual
   lighting, and put the results side by side. This is the cheapest and most neglected test in
   branding, and it is the only one that tests the real distribution channel — customers' cameras.

**What breaks if ignored:** the brand looks correct in every asset you produce and wrong in every
piece of user-generated content, which is where most of your impressions actually happen.

## 9.6 Worked example — a Vietnamese noodle-restaurant palette

All values `[illustrative]`. This is a demonstration of the *structure*, not a recommended palette.

| Token | Role | OKLCH | Tier | Notes |
|---|---|---|---|---|
| `ink/900` | Text, logo | `oklch(0.22 0.02 40)` | 1 | Warm near-black; prints as rich black, not 100K alone |
| `broth/700` | Brand primary | `oklch(0.42 0.09 48)` | 1 | Deep melanoidin brown-red; sits inside CMYK comfortably |
| `chilli/550` | Accent, CTA | `oklch(0.58 0.16 32)` | 2 | High-chroma red-orange; verify against printer profile |
| `herb/600` | Secondary accent | `oklch(0.55 0.11 145)` | 1 | Deliberately darker and less chromatic than real herbs, so photographed garnish never competes with it |
| `rice/50` | Background, neutral | `oklch(0.97 0.008 80)` | 1 | Barely warm off-white; the AWB reference (rule 17.1) |
| `stone/300` | Dividers, disabled | `oklch(0.80 0.01 60)` | 1 | |
| `neon-chilli` | **Screen only** | `oklch(0.70 0.24 32)` | 3 | Documented as unprintable; print substitute is `chilli/550` |

Note the deliberate design move in `herb/600`: the brand green is specified *darker and duller than
real herbs* precisely because the photography will contain real herbs. If the brand green matched
fresh **húng quế**, every photo would fight the layout (Part 3.1, failure mode 3).

Text-contrast obligations for this palette, to be measured not assumed:

- `rice/50` text on `broth/700` — must reach 4.5:1. `[illustrative]` expectation: passes.
- `ink/900` text on `rice/50` — must reach 4.5:1. `[illustrative]` expectation: passes comfortably.
- `rice/50` text on `chilli/550` — borderline. **This is the one to measure.** A mid-lightness
  accent is the classic failure: too dark for black text, too light for white text.
- `herb/600` as *text* on `rice/50` — likely fails 4.5:1 at body size. Use it as a fill, not as text,
  or darken a text-only variant.

**Decision rule 18:** every accent colour in the mid-lightness band (OKLCH L roughly 0.50–0.65) needs
a **text-only darker sibling**, because it will fail contrast as text against a light background even
though it works as a fill. Not having this sibling is why designers quietly break contrast rules on
links and buttons.

---

# PART 10 — CHECKLISTS

## 10.1 Pre-shoot brief (food)

- [ ] One light source, or all sources within ~500 K of each other (Rule 8)
- [ ] Lamp CRI as high as budget allows; chilli test performed (Rule 7)
- [ ] Grey card shot at the food's position, first frame of every setup
- [ ] Vessel is near-neutral, light or dark, chroma under 0.02 (Rule 6)
- [ ] Background tested against the dish in OKLCH: |ΔL| ≥ 0.15 (Rule 10)
- [ ] Text zone identified and kept free of specular highlights (Part 7.2)
- [ ] Herbs and lime held back; second plated set standing by (Part 6.1b)
- [ ] Shooting in RAW, mastering in Adobe RGB if print is in scope (Rule 1)
- [ ] Look temperature written into the brief as a number (Rule 9)

## 10.2 Image approval

- [ ] Red channel histogram checked for clipping in chilli/chilli oil (Part 6.1c)
- [ ] Greens on the green side of yellow, chroma intact — no pheophytin olive
- [ ] A near-neutral light element present and actually neutral after grading
- [ ] Oil film has specular highlights
- [ ] Broth clearly darker than noodles and bowl
- [ ] Set is internally consistent when viewed as a grid
- [ ] No hue manipulation applied to the food itself (Part 6.3, rule 1)
- [ ] Not converted to black-and-white unless deliberately accepting the appetite cost

## 10.3 Export

- [ ] Profile embedded, not stripped (Rule 2.1)
- [ ] "Convert to Profile", not "Assign Profile" (Rule 2.2)
- [ ] sRGB 8-bit for open web; 16-bit retained for anything re-editable (Rule 2.3)
- [ ] Perceptual intent for photographs; relative colorimetric for flat art (Rule 16)
- [ ] Opened in a plain browser window and compared to the source (Rule 2.4)
- [ ] For P3 assets: sRGB fallback declared first in CSS (Part 1.3)

## 10.4 Palette sign-off

- [ ] Every token has an OKLCH source of truth (Part 9.4)
- [ ] Every CMYK value carries its profile name (Part 9.4)
- [ ] Primary is Tier 1; Tier 3 colours labelled screen-only with print substitutes (Rule 15)
- [ ] TAC under the **printer's own stated limit**, obtained in writing (Part 9.1)
- [ ] Contrast measured for every text/background pair actually used; 4.5:1 or 3:1 at ≥24 px /
      ≥18.5 px bold (Part 7.1)
- [ ] Mid-lightness accents have text-only darker siblings (Rule 18)
- [ ] Pairwise CVD simulation passed for protan, deutan, tritan (Rule 14)
- [ ] Greyscale print test passed
- [ ] Dark-surround variants specified (Rule 5)
- [ ] Printed material photographed on three phones under venue lighting (Rule 17.5)

## 10.5 Fast diagnosis table

| Symptom | Most likely cause | Where to look |
|---|---|---|
| Brand colour "drifted" between two media | Surround changed, or profile stripped | Parts 1.2, 4.3 |
| Web images look flat and dull vs the design file | Wide-gamut data reinterpreted as sRGB | Part 1.2 failure mode A |
| Tint ramp has two steps that look identical | Ramp generated in HSL | Part 2.1 |
| Complementary pair looks unbalanced | Hue rotated in HSL, lightness mismatched | Part 3.1 failure mode 1 |
| One half of the frame is orange, the other blue | Mixed lighting | Part 5.2 |
| Herbs look olive-grey | Chlorophyll to pheophytin | Part 6.1b |
| Chilli oil is a flat red patch with no texture | Red channel clipped, or gamut clipped | Part 6.1c |
| Dish has no silhouette against the background | Background too close in L or hue | Part 6.3, Rule 10 |
| Headline unreadable over one part of a photo | Measured against average, not worst pixel | Part 7.2 |
| Printed piece looks muddy and takes long to dry | TAC exceeded | Part 9.1 |
| Brand red photographs as orange on customers' phones | Insufficient hue margin, or no neutral reference in scene | Rule 17 |
| Chart series invisible to some viewers | Information carried in hue alone | Part 8.5 |

---

# SOURCES

Fetched and read on 2026-07-29:

1. W3C, *Understanding SC 1.4.3: Contrast (Minimum)* — https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
2. Björn Ottosson, *A perceptual color space for image processing* (Oklab) — https://bottosson.github.io/posts/oklab/
3. MDN, *color()* — https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/color
4. MDN, *oklch()* — https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/oklch
5. Wikipedia, *DCI-P3* — https://en.wikipedia.org/wiki/DCI-P3
6. Wikipedia, *Adobe RGB color space* — https://en.wikipedia.org/wiki/Adobe_RGB_color_space
7. Wikipedia, *Color temperature* — https://en.wikipedia.org/wiki/Color_temperature
8. Wikipedia, *Color balance* — https://en.wikipedia.org/wiki/Color_balance
9. Wikipedia, *Color management* — https://en.wikipedia.org/wiki/Color_management
10. Wikipedia, *Contrast effect* — https://en.wikipedia.org/wiki/Contrast_effect
11. Wikipedia, *Color blindness* — https://en.wikipedia.org/wiki/Color_blindness
12. Wikipedia, *Maillard reaction* — https://en.wikipedia.org/wiki/Maillard_reaction
13. US National Eye Institute, *Color Blindness* — https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness
14. Okabe & Ito, *Color Universal Design* — https://jfly.uni-koeln.de/color/
15. Frontiers in Psychology, *Effects of Coloring Food Images on the Propensity to Eat: A Placebo Approach With Color Suggestions* — https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.589826/full
16. Adrian Roselli, *WCAG3 Contrast as of April 2026* — https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html

Search-level only (re-check before citing): Okabe–Ito hex values; Photoshop Export As profile
behaviour; TAC/ink-limit and rich-black figures; APCA Lc thresholds; chlorophyll-to-pheophytin
primary literature; blue-lighting appetite study; carotenoid pigment identities.

Attempted and failed: https://www.color.org/rendering_intents.xalter (HTTP 404);
https://pandagm.com/docs/total-area-coverage-tac-should-be-320-or-lower/ (HTTP 403).

## Open gaps, consolidated

| Gap | What would close it |
|---|---|
| WCAG 1.4.6 and 1.4.11 exact thresholds | Fetch those two Understanding pages |
| Quantitative chromatic induction magnitudes | A CIECAM-family appearance model reference |
| CRI / TM-30 threshold for food photography | A lighting or photographic standard, or a controlled test |
| Manufacturer gel mired-shift table | Current filter technical data from a lighting-filter maker |
| Okabe–Ito hex values from the primary source | The figure/table in the original CUD document |
| CVD prevalence in Vietnamese / SE Asian populations | An epidemiological study in Vietnam |
| ISO 12647-2 TAC figure and your printer's real limit | The standard text; a written vendor spec |
| Validated anomalous-trichromacy simulation for QA | Colour-science literature on anomaloscope-calibrated simulation |
| Phone-camera colour pipelines | Not publicly available; design around the uncertainty |
| Primary blue-lighting appetite study details | Fetch the paper in *Appetite* |
| Mapping between OKLCH L steps and WCAG contrast ratios | Would need to be computed and validated; no published table found |
