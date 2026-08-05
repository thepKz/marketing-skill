# Poster Art Direction

## Purpose

Use this after `poster-and-banner.md` has settled format, distance, copy capacity, and type size. It directs the image and composition without forcing every poster into one grid, medium, era, or aesthetic family.

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

## Production split

Default to `AI plate -> real/reference imagery in controlled masks -> human/Canva type`.

AI may own surface, light, material, symbolic device, image treatment, mask geometry, and text-safe zones. Prefer a real packshot or source photograph when product identity matters; asking a model to redraw a product is a fidelity risk, not a premium workflow. Human/Canva owns final copy, Vietnamese diacritics, logo, price, date, address, contact details, legal text, and QR.

Native AI text is allowed only when explicitly requested and short enough for provider QA. A generated plate containing fake letters fails even when the letters look decorative.

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
