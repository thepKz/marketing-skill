# Canva-Native AI Design

## Purpose

Use this reference when the user wants AI to create a social graphic, infographic, menu background, poster, carousel, one-pager, or campaign visual that feels deliberately composed in Canva while keeping final text editable and reliable.

The target is not a screenshot of Canva and not a generic template. The target is a flat visual system with the layer logic, component contrast, image masks, and reusable geometry a human designer would build before typesetting.

## Core production split

Default ownership:

- AI owns the flat visual composition: surface, image treatment, masks, panels, rails, callouts, motif, light, palette roles, and text-safe geometry.
- Human/Canva owns the final headline, Vietnamese copy, data, price, claim, logo, contact details, and QR.
- Deterministic HTML/SVG owns text only when the user explicitly requests code-based, automated, or editable-source production.
- Native AI text is an explicit exception and must pass locked-copy diff and visual QA.

Do not reduce this route to "generate a background." A Canva-native AI asset is a complete composition without final text, not an attractive photograph surrounded by empty space.

## What human Canva design is doing

Across a coherent Canva series, the content changes while a small system repeats:

1. **Surface:** one stable page field or two controlled fields.
2. **Brand anchor:** a compact, repeatable logo/identity position.
3. **Image mask family:** one geometric language for photographs, such as angled frame, rounded polygon, circle, or edge crop.
4. **Information module family:** repeated panels, tabs, arrows, rails, or callout shapes with shared corner, stroke, and shadow behavior.
5. **Signal component:** one bounded CTA, warning, selected item, or key fact treatment.
6. **Edge motif:** one low-information visual signature that supports the category, such as circuit traces, registration marks, ingredient linework, or a measured pattern.
7. **Text zones:** explicit hierarchy fields that stay quiet enough for human typography.

The system works because components contrast with one another by role. Surface, image, panel, signal, and text field must not share the same lightness, chroma, texture density, and edge behavior.

## Component grammar

Declare the component inventory before prompting:

| Component | Functional job | Default constraint |
|---|---|---|
| identity field | establish the brand before the generic topic | compact, stable position, never a giant empty logo area |
| primary image window | carry the main proof or subject | one dominant mask family and one crop logic |
| support image window | add range or evidence | subordinate scale; same light and mask grammar |
| information module | hold future copy or data | one repeated shape family, no fake text |
| navigation rail | sequence categories or steps | one path, rhythm, or numbering edge |
| signal/CTA field | carry one commercial action | bounded area; not reused for every component |
| edge motif | create recognition without stealing attention | low density inside text zones; stronger only at edges |
| footer reserve | hold contact, legal, URL, or QR | deterministic content added later |

House defaults, not standards:

- one dominant image-mask family per surface;
- one information-module family per surface;
- one signal color with one primary job;
- one edge-motif family;
- one clear primary visual mass;
- no component exists only because an empty corner felt uncomfortable.

Break a default only when the brief names the reason and the result remains reusable across a series.

## Clean, minimal, and contrast

Clean means low competition between components, not low information. Minimal means every visible element has a job, not that most of the canvas is blank.

Build contrast across at least two of these axes for adjacent components:

- lightness;
- chroma;
- scale;
- shape;
- edge hardness;
- material/texture density;
- photographic versus flat-color behavior.

Do not use maximum contrast everywhere. High-contrast pairs are reserved for the primary reading edge or signal component. Secondary panels step down in lightness or chroma. Decorative motifs must not create the same spatial frequency as body text.

Fail `CONTRAST-FLAT` when image, panel, surface, and CTA have similar visual weight. Fail `CONTRAST-OVERDRIVE` when every boundary, title zone, panel, and signal uses maximum contrast.

## Blueprint workflow

1. Lock format, aspect ratio, safe area, intended crop, and channel.
2. Inventory the real future content: brand, headline length, number of modules, image count, CTA, footer, and QR.
3. Build a text-free blueprint using blank blocks and registration marks. Do not put lorem ipsum or fake labels into the AI reference.
4. Name every reference role: identity, product/subject, composition, mask language, palette, texture, or motif.
5. Generate one flat composition with exact component geometry and explicit text-safe zones.
6. Reject letters, numbers, logo imitations, QR-like texture, watermarks, or decorative pseudo-writing.
7. Import the approved bitmap into Canva and lock it as the background/artwork layer.
8. Add final typography and data with named Canva text styles.
9. Test the longest headline, densest module, widest number/price, mobile crop, and series extension.

If the visual will become a carousel or content series, define the invariant component set and three variation axes before generating. For example: mask family and rail remain fixed; image, module count, and signal position may vary within limits.

## Prompt contract

State these blocks explicitly:

```text
Asset: flat Canva-ready composition, no mockup.
Format: exact ratio and target channel.
Component inventory: identity field, image masks, information modules, signal field, motif, footer reserve.
Hierarchy: primary visual mass, second reading edge, CTA position.
Geometry: size and position of every component family.
Palette roles: surface, structural support, signal, image/subject.
Material: flat color, print grain, paper, enamel, glass, or another named behavior.
Text ownership: human/Canva adds all final text, data, logo, and QR.
Hard reject: letters, words, numbers, fake glyphs, QR-like marks, watermark, component soup, template averaging, mockup.
```

Avoid vague phrases such as "make it Canva style" or "professional infographic." Translate them into observable component, contrast, mask, density, and layer instructions.

## Anti-AI and anti-template gates

- `COMPONENT-SOUP`: unrelated rounded cards, arrows, hexagons, stickers, badges, and glows appear on one surface.
- `MASK-DRIFT`: image frames change corner language, stroke, angle, or depth without a role.
- `LAYER-AMNESIA`: AI paints text-like detail or subject texture through a future typography zone.
- `AI-TEXT`: generated letters, numbers, logo, price, data, or QR-like marks appear in the default text-free route.
- `CONTRAST-FLAT`: components blend because they share the same visual weight.
- `CONTRAST-OVERDRIVE`: every component shouts with maximum contrast.
- `EMPTY-MINIMALISM`: large blank regions have no reading or production function.
- `TEMPLATE-AVERAGE`: the output averages popular template defaults instead of expressing product truth.
- `ONE-OFF`: a second slide or additional module requires a new visual language.
- `MOCKUP`: output is shown on a device, hand, desk, paper object, or browser instead of as flat artwork.

## Acceptance

Approve only when:

- the bitmap reads as a complete composition before text is added;
- the text-safe zones remain calm at full size and thumbnail size;
- component families are few, related, and reusable;
- the main image and signal component do not compete;
- removing the logo still leaves a recognizable system;
- final copy can be added in Canva without covering the subject or inventing new boxes;
- another page in the same series can be built by changing content rather than redesigning the grammar.
