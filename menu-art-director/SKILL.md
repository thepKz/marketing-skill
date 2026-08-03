---
name: menu-art-director
description: Create restaurant, cafe, bar, QR, and menu-board designs from a real brief. Use for menu art direction, food photography, typography, layout, native-text AI proofs, or anti-AI visual QA.
---

# Menu Art Director

Turn a menu request into a usable design direction, not a decorative prompt. The output must help a diner orient, compare items, and order quickly while still giving the restaurant a memorable visual point of view.

## Production Contract

Capture before styling:

- surface: table print, counter board, delivery listing, QR/mobile, poster, or social;
- real item names, prices, ingredients, allergens, availability, service speed, audience, and language;
- brand truth, references, anti-references, print size or viewport, and intended reading distance.

Never invent a price, ingredient, claim, award, dietary label, opening hour, or provenance. Label unknowns and use `—` until the owner confirms them.

## Choose The Route

Select one route and say why:

1. `full-ai-proof`: the image model renders food, layout, typography, Vietnamese copy, prices, and footer in one image. Use for concept exploration or when the user explicitly wants an all-in-one AI artifact. Generate one proof first; do not scale until native text, title size, and visual specificity pass.
2. `designed-production`: AI generates or edits the food photograph; deterministic typography and layout create the menu. Use when the menu must read like a real restaurant artifact, support multiple sizes, or keep exact Vietnamese text reliable.
3. `photo-led-minimal`: use one documentary food photograph with a restrained type system and almost no decoration. Use when the food and place are the brand.

Do not silently change routes. If `full-ai-proof` looks like a category template, report `GENERIC` and recommend `designed-production` or `photo-led-minimal`.

## Art Direction Brief

Write five short layers before prompting:

1. **Story:** premise, feeling, restaurant role, diner takeaway.
2. **Look:** camera angle, light behavior, surface, palette roles, material, density, and one memorable decision.
3. **Execution:** dimensions, safe areas, type hierarchy, image crops, print/digital specs, and required copy.
4. **Variants:** what changes for 9:16, 4:5, 1:1, counter distance, delivery thumbnail, and print.
5. **Standards:** approved example, rejected example, rights/claim constraints, and revision gate.

Avoid adjective-only briefs. Replace “premium modern” with observable instructions such as “ordinary stainless table, 35-degree diner angle, one red accent line, no border, 72px outer margin.”

## Layout And Typography

Declare reading order before styling:

1. orientation/category;
2. signature dish or offer;
3. food image;
4. item name and price;
5. add-ons/drinks;
6. footer, allergen, service, or ordering note.

Use one emphasis device per priority. Do not combine oversized type, boxes, badges, icons, photos, and color bursts on the same item. Prefer one or two title lines; keep titles visually subordinate to the food unless the brief is explicitly poster-led. Measure Vietnamese copy at the target viewport before forcing line breaks.

For a short menu, use a single-column list or a disciplined asymmetric split. Align prices on a common edge. Keep item rows scannable in under two seconds. Use a maximum of two type families and a restrained palette with one accent.

## Image Prompt Contract

For food photography specify subject truth, camera height/angle, lens behavior, light direction/hardness, surface, contact shadow, crop, and what is intentionally ordinary. Add rejects: no ingredient explosion, duplicated toppings, impossible steam, floating bowl, glossy CGI food, decorative border, fake logo, random text, or luxury cliché.

For a cutout composite, prefer extracting the served dish from a real source photograph. If no usable source exists, generate one proof on a removable chroma-key field before scaling. Validate alpha coverage, transparent corners, edge halos, subject completeness, and color contamination. Derive the palette or motif from a visible property of the dish, bowl, or restaurant rather than adding unrelated decoration. Rebuild contact shadow and color response for the destination surface; a clean cutout with no grounding is still a sticker.

For `full-ai-proof`, include exact copy in a quoted block and require:

- native Vietnamese diacritics;
- title under roughly 10% of canvas height and never more than two lines;
- exact prices and footer;
- generous low-entropy text zones;
- no extra words, fake glyphs, watermark, or text collision.

Inspect every result at full size. A prompt is not proof of text fidelity.

## Anti-AI Gate

Reject `GENERIC` when the category alone predicts the visual: black-and-gold luxury, symmetric ornamental border, marble, smoke, random silk, fake vintage grain, giant serif title, centered hero bowl, excessive garnish, or “cinematic” lighting without physical behavior. Also reject second-order defaults such as beige editorial cards or maximalist collage when no brief-driven reason exists.

Record concrete rejection labels: `GENERIC`, `HIERARCHY`, `CROP`, `PHYSICS`, `CLAIM`, `FIDELITY`, `OFF-BRAND`, or `RIGHTS`.

## Deliverable

Return:

- three option cards and one recommended direction;
- the five-layer art direction brief;
- a low-fidelity wireframe with reading order;
- copy pack and image prompt(s);
- format/export specs;
- QA checklist and rejection log.

For a real production request, write these artifacts to the workbench and run its strict status check before claiming completion.
