# Poster and banner: distance craft plus art direction

Distance sizes the type and limits the words; the art direction turns the message into a focal
mechanism instead of a fixed template. Both halves of poster work live in this file.

# Poster and Banner

## What this unit is for

A poster is not a small ad enlarged. It is a piece of copy that has to be read from a fixed distance by somebody who is not stopping, and that single sentence decides the size of the type, which decides how many words are allowed, which decides what the poster is about. Everything else is downstream of the distance.

Most posters and banners are made in Canva, and the ones that work are working for reasons that can be written down. This unit writes them down, and then does the part Canva does not: it computes whether the copy fits before anybody opens an editor.

Run `plan_poster.py --explain-units` for the arithmetic — it ends by reproducing an optician's chart — and `--list-formats` for the trim sizes.

## The one formula

A letter is legible by the angle it subtends at the eye, so cap height and viewing distance are one quantity, not two:

```text
cap height = viewing distance × angle
```

Three bands on that angle carry everything:

| Band | Angle | LI | What it means | Used for |
|---|---|---|---|---|
| Acuity floor | 5′ | 57 | A 20/20 eye resolves the letter and no more | Nothing. It is the floor, and resolving a letter is not reading a word |
| Sustained | 20′ | 14.3 | A person who has stopped can read a paragraph without effort. ISO 9241-3:1992 cl. 5.4 prefers 20′ to 22′ and sets 16′ as its minimum | Support copy, prices, addresses, hours |
| Glance | 28.65′ | 10 | The sign trade's "one inch of letter height per ten feet", restated as the angle it always was | Headlines, anything read in motion |

Two anchors make this checkable instead of asserted, and `--explain-units` prints both:

- 5′ at 6 m is **8.73 mm**, which is the 6-metre line on a Snellen chart. The formula agrees with an optician's wall.
- 28.65′ at 3.048 m (ten feet) is **25.4 mm**, one inch. The trade rule of thumb falls out of the arithmetic rather than sitting beside it.

### The same axis, as the sign trade states it

No print shop or OOH vendor talks in arcminutes. They talk in the **Legibility Index**: feet of legible distance per inch of cap height. It is the identical axis inverted — `arcmin = 286.479 / LI`, exactly — which means every published rule is one point on one line, and they can finally be compared. Sorted by how much type each demands, since a *smaller* LI is a *bigger* letter for the same distance:

| Rule | LI | Angle | What it is |
|---|---|---|---|
| ADA 2010 Table 703.5.5 slope, +1/8 in per foot | 8 | 35.8′ | A US legal floor. The slope is a cap-to-distance ratio of **1:96**, which is LI 8 — not LI 96 |
| ADA 2010 Table 703.5.5 base, 5/8 in at 72 in | 9.6 | 29.8′ | The same clause's starting point, 4% stricter than the row below it |
| **This unit's glance band** | **10** | **28.65′** | Stricter than every commercial table by two to four times, and just inside the ADA floor |
| USSC **measured**, by typeface, colour pair and illumination | 20–38 | 7.5–14.3′ | The only research-measured band here. Colour and illumination alone move it 1.9× |
| OAAA published distance/font table | 25 | 11.5′ | The trade association's own guide. Every band in it divides out at 25 |
| USSC simplified default | 30 | 9.5′ | The USSC calls it "an average only, and it may fall short" |
| MUTCD/FHWA non-Interstate | 40 | 7.2′ | The FHWA's own text calls it an accepted rule of thumb |
| Snellen acuity ceiling | 57 | 5.0′ | A definition, not a rule. Nothing is designed here |

The unit-conversion trap in row one is worth spelling out, because it is a factor of twelve and it is silent. ADA's +1/8 inch per foot is inches of cap per inch of distance = 1:96; the Legibility Index is *feet* of distance per *inch* of cap = 8. Read 1:96 as an LI and an accessibility floor lands at 3′, below the acuity limit, where nothing can be read by anybody.

The glance band's own justification has to be stated rather than assumed. LI 10 is research-backed for exactly one case: the USSC measured that a sign read **side-on** needs about three times the cap height a viewer facing it needs, which divides the measured band down to LI 6.7–12.7, and LI 10 sits inside it. A banner strung across a street is read side-on by somebody on a scooter. A poster on a wall you walk up to is not — so on a wall the glance band is generous by roughly a factor of two, and `plan_poster.py` prints the LI next to the angle so the operator can see that rather than discover it in a print bill.

The corroboration is the useful part: a US accessibility statute written for a low-vision reader at close range, and the sign trade's oldest rule of thumb, land within 4% of one another from unrelated directions. Neither was aimed at a Vietnamese street banner and the ADA has no force here, so it is agreement rather than authority — but agreement is what the number rests on.

Two facts about that table worth keeping: **all caps costs about 15 per cent** more letter height than upper-and-lower with initial caps, on the USSC's own statement, and the USSC found drivers **missed 30 per cent of parallel signs even when actively looking for them**. Neither is in the arithmetic. The second one is the argument against the medium, not against the design.

### Legible is not the same as read

Size answers whether a letter can be resolved. It says nothing about whether the sentence gets finished, and for a reader in motion that is the binding constraint:

- The OAAA's own creative guide: **"7 words or less is a proven benchmark."** The USSC legibility table is only valid under its own stated condition of **six words or thirty letters**.
- From the opposite direction, reading research: Brysbaert's meta-analysis of 190 studies and 18,573 participants puts adult silent reading of non-fiction at **238 wpm**, most adults between 175 and 300. That is 3.97 words a second, so a two-second glance buys about **eight words** and a slow reader about six.

A trade association and a reading-research meta-analysis agreeing to within one word from unrelated directions is the strongest cross-validation in this unit, so `plan_poster.py` gates on it — and gates honestly. Both sources measured motorists or fixated readers of prose, neither measured Vietnamese, and neither measured a pedestrian. So the gate **fails** a rider or a driver, **reviews** a walker or a scroller, and is **skipped** for a reader who has stopped, keyed off the `viewer_motion` column rather than off a guess. The OAAA also reports that ads with two message elements are 21 per cent more likely to be noticed than ads with five, attributed to the *Journal of Advertising Research* without a full citation — treat it as the direction of travel, not as a number.

Screens need no metres. CSS defines the reference pixel as the visual angle of one pixel on a 96 dpi display at arm's length, so **one CSS pixel is 1.279′ by specification**, on every device, whatever its own density. That lands somewhere useful: the browser default 16 px sets a cap height of 15.1′, just under the sustained band — which is why 16 px behaves as a floor rather than as a comfortable size, and why a caption at 12 px is a decision to go unread.

**The distinction that most template output gets wrong:** a headline is read at the glance band and support copy at the sustained band, because they have different readers. The person who reads the address has already stopped walking. Scaling everything from the canvas instead of from the reader is what produces a poster that looks balanced on a laptop and is unreadable on a wall.

## What Canva actually encodes

Canva makes untrained users look competent by pre-committing five things before any layout happens. All five are portable, and all five are cheaper to copy than to rediscover.

| Mechanism | What Canva fixes | The rule underneath |
|---|---|---|
| Brand fonts | One default font each for headings, subheadings and body — three roles, no more | Hierarchy is a slot system filled before layout starts, not a per-element decision |
| Brand Kit palette | An enumerated set. The free tier allows one palette of three colours | A brand is a finite list. A colour not on the list cannot appear |
| Palette generator | Returns four named colours sampled from an uploaded photo | Derive the palette from the hero image. This is the direct antidote to `palette-divorce` |
| Page guides | Exactly three presets: 12 columns, 6 columns, or a 3×3 grid | 12 → 6 → 3 nest, so every block width is a whole number of columns |
| Bleed | Fixed at 0.125 in (3.175 mm) on all sides, not user-editable | A safe area you design inside and a trim area you deliberately overrun are two different numbers |
| Brand Template locks | `Lock position only` on a text box freezes font, size, colour, alignment, case, line spacing — and leaves **the content of the text box editable**. Locks must be set before publishing and cannot be added afterwards | **Copy is free, form is frozen.** This is the single rule that makes Canva output competent in untrained hands |

That last row is the important one, and it is exactly how this unit is built: the type sizes come from `plan_poster.py` and the format, the strings come from the brief, and nothing in the pipeline lets a string change a size.

Canva also publishes two numbers worth carrying: **300 DPI minimum for print**, and its own poster page naming 18×24, 24×36 and 27×40 inches as the common sizes — chosen by viewing distance, indoor to transit stop, which is the same argument as the table above. Its banner presets (Facebook cover 851×315, X 1500×500) are 2.7:1 to 3:1 letterboxes, which is why banner hierarchy has to run left to right: vertical composition is not available.

## What Canva does not do, and this unit does

- Tell you whether the headline fits. `plan_poster.py` measures the actual string against the actual measure at the size the distance demands, using the same font metric that draws the mockup.
- Tell you the viewing distance. It is a property of the place, not the format. Every distance in `data/poster-formats.csv` is graded `declared-assumption` and every row says so in its own words.
- Refuse a format. A 320×50 mobile banner carries one line at glance size, so a layout with a headline, a price and a button in it has already failed. The arithmetic says so before the design does.
- Say whether the claim is legal (`check_claims.py`), whether the copy is specific (`check_specificity.py`), whether the placement renders (`check_channel_spec.py`), or whether the type survives on the photograph (`sample_reference.py`, `plan_palette.py`).

## Generated artwork with type in it

The published ceiling on native text comes from Google's own Imagen prompt guide: **limit text to 25 characters, and no more than three phrases**. `plan_poster.py --generated` gates on both. Breaching them returns `review`, not `failed`, because the answer is to composite the type — not to shorten the sentence to suit the model.

For Vietnamese the ceiling is effectively lower, and the reason is in `data/slop-tells.csv` under `diacritic-drift`: script-level degradation is measurable in every model tested, the marks specific to Vietnamese are what break first, and an English-reading review passes it because an English-reading eye never looks at the marks. Ten poster and banner tells sit in that table with a ten-second eye check each — `diacritic-drift`, `font-melt`, `wordmark-invention`, `hierarchy-collapse`, `rag-chaos`, `edge-bleed`, `decor-noise`, `faux-depth-furniture`, `palette-divorce`, `qr-fiction`. `invented-text` and `centered-everything` were already there and already cover fabricated signage and the dead-centre layout.

The working division: **generate the plate, composite the words** — with the venue name as the one default passenger in the plate, since a short name fits under both ceilings and gains from sharing the scene's light (conditions in Production split below). A brand mark is never generated, a QR code is never generated, and a price is never generated.

## The researched gap

**Whether you may hang it is not in this unit.** Placement, permit and duration for outdoor advertising in Vietnam are governed separately, `data/vn-advertising-law.csv` has no outdoor rows, and this repository has not researched them. `bang-ron-ngang`, `phuon-doc` and `billboard-roadside` all say so in their own `what_it_does_not_tell_you` cell.

What to bring back before a street banner or a billboard is designed:

1. The commune or ward requirement for a *thông báo sản phẩm quảng cáo* on a banner, and the lead time.
2. Whether the site is on a licensed OOH inventory list, and the site code.
3. The vendor's own artwork template for that site code — its canvas, its bleed, its eyelet allowance. A generic file gets rejected.
4. For an LED wall, the pixel pitch in millimetres. A minimum legible type size is set by pitch as well as by distance, and pitch is not in the format table.

### Every grade the table uses, and how far you may lean on it

A grade is not a footnote. It is the cell that decides whether the script computes, warns, or refuses, so a reader who meets one of these words in `poster-formats.csv` can find it here. Ordered by how much weight it carries.

| Grade | Column | What it means | What the script does |
| --- | --- | --- | --- |
| `iso-216-definitional` | size | Not a measurement. A0 is 841 × 1189 mm and every later size is the previous long side halved, so the seven A and B rows are derivable from the 1:√2 root | Computes. The seven rows derive from the root, so a drifted row is recomputable by hand |
| `css-definitional` | distance | The CSS reference pixel is specified as an angle, 1/96 inch at arm's length, so a screen format carries its own viewing distance | Computes with no distance, and **fails** if `--distance` is passed, because that applies the distance twice |
| `trade-multi-vendor` | size | No standards body publishes the number, but several independent Vietnamese shops publish the same one — 600 × 1600 mm for a standee in three size lists, 800 × 3000 mm for a băng rôn ngang in two. A convention, and what the word means on a quote | Computes |
| `industry-common-unsourced` | size | The five web ad sizes every ad server accepts and every publisher lists. This repository fetched no primary specification for them | Computes |
| `trade-common-unsourced` | size | One shop, unverified | Computes |
| `declared-assumption` | distance | This repository's guess at the place, not a fact about the format. Measure the room and pass `--distance` | Computes, and says in the output that the number is an assumption |
| `place-declared` | distance | The venue decides and no default is possible | Computes off the assumed distance only until you measure |
| `vendor-declared` | size, allowance | There is no default at all; the vendor's spec sheet is the only source | **Fails.** Nothing is computed on a fiction |
| `not-applicable` | allowance | Screens and LED walls: nothing is cut, folded, hemmed or punched | Skips the allowance entirely |

One vendor claims băng rôn sizes follow a Ministry of Culture regulation and cites no decree, so **no regulatory maximum is encoded here.**

### Bleed and material allowance are two different numbers

Conflating them either wastes the design or tears the banner, and the two trades use opposite conventions:

| | What it is | Typical | Who consumes it |
|---|---|---|---|
| Bleed | Artwork extended past the trim so a blade landing 0.8 mm off still lands in ink | 3 mm sheet, 6.35 mm large-format poster | The guillotine |
| Safe margin | A keep-out band **inside** the finished edge that nothing load-bearing enters | 6–80 mm by format in `data/poster-formats.csv` | Nobody — it is empty on purpose |
| Edge allowance | Material **outside** the visible area that is physically folded, sewn or punched through | **50 mm every side on hiflex**, and 100 mm on the top edge for a pole sleeve | The print shop |

The 50 mm is published identically by two independent Vietnamese hiflex shops. Neither states an engineering basis for it, so it is craft convention rather than a tear-strength measurement — but a file that treats it as bleed loses 50 mm of artwork into a hem. `plan_poster.py --list-formats` prints it as "material the shop consumes" for exactly this reason.

One more thing the vendors converge on: **DPI is a function of viewing distance, not of medium.** Vietnamese hiflex shops quote 150 dpi for a file read at 0.8–1.8 m, falling to 40–50 dpi for a sign two storeys up, and the Ghent Workgroup's Sign & Display spec is built on the same two variables. That is the same argument as the cap-height table, on a different quantity — so one measured viewing distance should drive both dials. This unit does not encode a DPI table because the GWG's own numbers are download-gated and the Vietnamese figures come from single vendors who contradict each other on backdrops; ask the shop that is printing it.

### Looked for, does not exist

These were searched for deliberately, and the finding is that no published source carries them. They are listed so the next person does not spend the afternoon, and so that nothing in this unit quietly invents one:

| Wanted | Status |
|---|---|
| An x-height correction to cap height | No standard or paper supplies a factor. Every rule here specifies cap height, measured on an uppercase I, and two faces at equal cap height with x-height ratios of 0.50 and 0.75 are not equally legible. Unsolved, not merely uncited |
| A SEGD cap-height formula | SEGD publishes none. What it does publish is line spacing: 135 % minimum to 170 % maximum of uppercase-I height, baseline to baseline |
| Minimum cap height as a percentage of banner height | No number from the OAAA, the USSC, the IAB or any DOOH spec. The IAB deliberately specifies aspect ratio and size range and states no minimum font size at all. It is derivable from a physical size and a stated distance, and that derivation is ours, not a citation |
| How many hierarchy levels a poster can carry, and the minimum size ratio for two levels to read as distinct | No research located for either. Müller-Brockmann mentions "3, 4 or more different type sizes" only to say their leading must be reconciled — that is not a limit claim. Taste, and labelled as taste |
| An optical-margin or round-letter overshoot percentage | No primary type-design source found. The commonly repeated 1–3 % has no traceable origin |
| A billboard exposure duration in seconds | The OAAA guide states none. Use the USSC's viewer-reaction-time machinery instead: 8 s under 35 mph, 10 s over, 11–12 s high-speed multi-lane, closing rate `fps = mph × 1.47` |
| A Vietnamese băng rôn legal size maximum | Claimed by one vendor, no decree cited |

`data/slop-tells.csv` and the ISO 216 rows are what this unit is sure of. This table is what it is not, and both belong in the same file.

## Order of work

1. `plan_poster.py --list-formats`, pick the format, and measure the real viewing distance at the place.
2. Write the headline. Run `plan_poster.py --format … --distance … --headline … --support …`. If it returns `failed`, cut words. Do not cut type.
3. Sample the palette from the hero photograph — four swatches — and check the contrast the accent has to survive.
4. Set three type roles at the sizes the run reported, and freeze them.
5. Lay out on 12, 6 or 3 columns, with one strong left edge and one deliberate break in it.
6. Render with `render_mockup.py`, which raises on an overflow instead of cropping it.
7. Proof against the ten tells before the file leaves.


---

# Poster Art Direction

## Purpose

Use this after the distance craft above has settled format, distance, copy capacity, and type size. It directs the image and composition without forcing every poster into one grid, medium, era, or aesthetic family.

The hard problem is not decoration. A poster needs one idea that survives a three-second glance, one image behavior that carries that idea, and enough information capacity for the real copy.

## Hard gates and soft defaults

Hard gates:

- product, identity, offer, date, venue, price, claim, and rights truth;
- viewing-distance and word-capacity check;
- one dominant reading edge and one primary visual mass;
- final text, logo, data, price, and QR remain deterministic by default;
- flat artwork unless a presentation mockup is explicitly requested;
- full-size and thumbnail QA.

Soft defaults:

- one focal mechanism;
- one image family;
- one structural device;
- three palette roles plus one bounded signal;
- one deliberate grid break;
- headline no more than two lines.

Break a soft default when the brief benefits. Do not break a hard gate for style.

## Start from a focal mechanism

Write one sentence in this form:

```text
The poster makes [message] visible by turning [sourceable product/story element]
into [scale contrast, negative-space reveal, repeated rhythm, material transformation,
crop tension, documentary evidence, or another observable mechanism].
```

Examples of mechanisms, not templates:

- an ingredient becomes the navigation path;
- a product aperture bends the scene's light;
- one oversized object makes the user or product feel small;
- a silhouette contains the second meaning in negative space;
- a repeated module creates urgency or abundance;
- a documentary crop makes process evidence dominate polished branding;
- typography becomes the image only when the words themselves are the subject.

Reject a concept that can be described only with adjectives such as premium, cinematic, bold, modern, Mondo, editorial, or minimalist.

## Choose a poster mode

| Mode | What leads | Suitable when | Common failure |
|---|---|---|---|
| product proof | real product or process evidence | commerce, launch, demonstration | centered packshot on empty luxury space |
| symbolic | one distilled object or visual metaphor | culture, event, campaign idea | clever image unrelated to the action |
| editorial | crop, sequence, caption rhythm | story, report, exhibition, fashion | magazine styling with no hierarchy at distance |
| action/offer | price, date, CTA, availability | retail, event conversion, local promotion | every element becomes a high-contrast badge |
| atmosphere | one continuous scene and material world | hospitality, place, entertainment | generic cinematic lighting without physical behavior |
| system poster | repeated mask/module grammar | campaign series, multi-SKU, multi-event | one-off composition that cannot accept the next item |

Combine at most two modes. Name which one leads.

## Flexible composition

Use the content to choose geometry:

- one short promise may use extreme scale contrast or one symbolic field;
- a product plus evidence may use one hero mask and one or two subordinate windows;
- a date-heavy event may use a typographic spine with an image interruption;
- several products may use repeated modules, but one SKU or group must lead;
- an artistic poster may spend more area on atmosphere, but must retain a deterministic identity and information reserve.

Do not automatically center the subject, use a giant title, apply a Swiss grid, add a decorative border, or reserve a fixed percentage of empty space. Negative space must create figure-ground meaning, protect reading, or build scale tension; otherwise it is `EMPTY-PRESTIGE`.

## Committed geometry

The focal mechanism decides what the poster is; this skeleton decides where things land before
taste starts. Every number is a declared craft value, not a citation — the same grade the format
table uses — and the skeleton exists for the same reason menu geometry does: a run that reinvents
the frame each time ships a different poster each time. Deviate for the focal mechanism, on
purpose and named in the brief; never by drift.

| Surface | Outer margin | Identity zone | Headline | Image field | Information strip |
|---|---|---|---|---|---|
| A-series print, A3–A0 | 4% of the short side, all edges | ≤10% of page height, one edge only | Enters in the top third, on one committed left edge, ≤2 lines | ≥55% of page area | ≤12% of page height at the base, sustained-band type |
| Social 4:5 (1080×1350) | 72 px | One corner, ≤120 px tall | Within the top 40%, ≤2 lines | ≥50% of canvas | One badge or price lockup, never both stacked |
| Story 9:16 (1080×1920) | 64 px sides | Below the top reserve | Reserve the top 250 px and bottom 340 px for platform UI; the message lives in the middle 60% | Full-bleed behind the reserves | CTA sits just above the bottom reserve |
| Banner letterbox ≥2.5:1 | 4% of height | Left block, ≤20% of width | Centre field, ≥55% of width, one line | Behind or right of the message | Right block, ≤25% of width |

Three rules ride every surface: at most three type sizes, because three roles is all a poster
carries; headline-to-support cap-height ratio at least 3:1, or the hierarchy reads as two
paragraphs; and exactly one deliberate grid break, because one break is emphasis and two is noise.
The skeleton is where layout starts, and `EQUAL-SIGNALS` is what shipping it unbroken and unloved
looks like — commit the frame, then spend the taste on the one place it bends.

## Production split

Default to `AI plate -> real/reference imagery in controlled masks -> human/Canva type`.

AI may own surface, light, material, symbolic device, image treatment, mask geometry, text-safe zones — and, by default, the brand or venue **name** as display lettering, because a name drawn in the plate's own light and material reads as belonging where a pasted name reads as a sticker. The name exception has three conditions: it is the name only, never the logo mark; it fits the 25-character native-text ceiling; and every Vietnamese diacritic is proofed against `diacritic-drift` — two broken renders and the name moves to the composite layer. Prefer a real packshot or source photograph when product identity matters; asking a model to redraw a product is a fidelity risk, not a premium workflow. Human/Canva owns final copy, Vietnamese diacritics in running text, logo, price, date, address, contact details, legal text, and QR.

Native AI text beyond the name is allowed only when explicitly requested and short enough for provider QA. A generated plate containing fake letters fails even when the letters look decorative.

## External-skill findings

A 2026-08-05 review of the public `qiaomu-mondo-poster-design` skill found three transferable strengths: symbolic distillation instead of literal collage, dramatic scale contrast, and deliberately limited palette roles. Its rigid style anchors — Mondo naming, forced screen-print finish, vintage-decade cues, centered symmetry, fixed ratios, and artist imitation — are optional references, not house rules. Apply the mechanism when it fits; do not turn one successful aesthetic into the poster router.

The public `brand-guidelines` catalogue entry reinforces a different lesson: identity needs declared colors and type roles before execution. It provides no complete poster workflow by itself, so use it as a brand-consistency reminder rather than as an art-direction engine.

The public `magazine-poster` template contributes dateline rhythm, editorial headline contrast, image-caption behavior, and long-form hierarchy. Its cream newsprint, giant serif, mandatory strike/italic pair, six numbered cells, and fixed footer are a single template, not the definition of editorial design. Borrow the reading rhythm when the message needs explanation; change the component count, paper color, image density, and headline device when the content asks for it.

## Prompt contract

State: asset and ratio; focal mechanism; primary and support image behavior; content capacity; geometry; palette roles; material/light behavior; text ownership; flat-art requirement; fidelity locks; and explicit rejects.

Avoid artist-name-only prompting. Translate a reference into observable decisions such as two-color figure-ground inversion, oversized crop, halftone ink, documentary flash, hard side light, narrow type spine, or modular image windows.

## Reject labels

- `NO-THESIS`: attractive components without one poster idea.
- `STYLE-COSTUME`: named aesthetic applied without message or product reason.
- `EMPTY-PRESTIGE`: blank space performs no reading or figure-ground job.
- `CENTERED-PACKSHOT`: product floats in the middle with no mechanism.
- `EQUAL-SIGNALS`: image, headline, badge, price, and CTA all shout equally.
- `REFERENCE-MIMICRY`: copies a recognizable artist, layout, or trade dress rather than extracting a mechanism.
- `PRODUCT-DRIFT`: generated redraw changes product shape, label, material, or color.
- `MASK-DRIFT`: image windows lose their shared geometry.
- `AI-TEXT`: fake or incorrect visible text in the default plate route.
- `ONE-OFF`: the next size, SKU, or poster needs a new visual language.

Approve only when the poster reads at thumbnail size, rewards full-size viewing, keeps the real information editable, and can explain its focal mechanism without naming a style.
