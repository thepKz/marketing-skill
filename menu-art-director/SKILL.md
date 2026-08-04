---
name: menu-art-director
description: Create restaurant, cafe, bar, QR, and menu-board designs from a real brief. Use for menu art direction, food photography, typography, layout, native-text AI proofs, or anti-AI visual QA.
---

# Menu Art Director

Turn a menu request into a usable design direction, not a decorative prompt. The output must help a diner orient, compare items, and order quickly while still giving the restaurant a memorable visual point of view.

For a redesign, restaurant identity, or “make this more branded” request, read `references/brand-menu-vision.md` before choosing a visual route. Use it to compare brand systems, define recognition, and avoid palette-only or ornament-only art direction.

## Production Contract

Capture before styling:

- surface: table print, counter board, delivery listing, QR/mobile, poster, or social;
- real item names, prices, ingredients, allergens, availability, service speed, audience, and language;
- brand truth, references, anti-references, print size or viewport, and intended reading distance.
- business identity: restaurant name, approved mark, address, phone, order URL, social handle, and QR destination.

Never invent a price, ingredient, claim, award, dietary label, opening hour, or provenance. Label unknowns and use `—` until the owner confirms them.

Never invent contact details or a functional QR destination. If identity information is missing, either use a clearly labelled fictional concept brand or reserve an identity zone and say what the owner must supply. Image models may create a QR-looking texture but not a trustworthy QR code; a working QR requires a provided URL and deterministic generation, even when the surrounding menu uses `full-ai-artwork`.

When the user asks for a complete menu, research public menus before designing. Build a source ledger with URL, source type, access date, observed item name, observed price, and limitations. Prefer first-party restaurant menus; use delivery platforms as behavioural traces and secondary articles only for directional context. Do not create “ten plausible side dishes” from memory.

Lock every researched name, description, category, and price in a deterministic data file before styling. Mark the result `benchmark-not-for-sale` until the owner confirms portions, ingredients, allergens, availability, packaging fees, and current prices. A complete menu must contain real item rows; placeholders are acceptable only for facts that remain genuinely unknown.

## Choose The Route

Select one route and say why:

1. `full-ai-artwork`: the image model renders a flat, finished menu artwork for direct export/print: food, layout, typography, Vietnamese copy, prices, pattern language, and footer in one image. Use when the user asks for an artistic AI image or says “tạo toàn bộ bằng AI”. Do not convert this route into HTML or a photographed paper mockup.
2. `full-ai-proof`: the image model renders food, layout, typography, Vietnamese copy, prices, and footer in one image for concept exploration. Use when the user wants to compare directions but has not yet selected the final art route.
3. `designed-production`: AI generates or edits the food photograph; deterministic typography and layout create the menu. Use only when the user accepts a hybrid production workflow.
4. `photo-led-minimal`: use one documentary food photograph with a restrained type system and almost no decoration. Use when the food and place are the brand.

Do not silently change routes. If the user explicitly asks for one generated image containing the food, words, layout and art direction, use `full-ai-artwork` first. Do not recommend a hybrid companion unless the user asks for production-safe text or the AI route has been rejected after documented iterations.

## Art Direction Brief

Write five short layers before prompting:

1. **Story:** premise, feeling, restaurant role, diner takeaway.
2. **Look:** camera angle, light behavior, surface, palette roles, material, density, and one memorable decision.
3. **Execution:** dimensions, safe areas, type hierarchy, image crops, print/digital specs, and required copy.
4. **Variants:** what changes for 9:16, 4:5, 1:1, counter distance, delivery thumbnail, and print.
5. **Standards:** approved example, rejected example, rights/claim constraints, and revision gate.

Avoid adjective-only briefs. Replace “premium modern” with observable instructions such as “ordinary stainless table, 35-degree diner angle, one red accent line, no border, 72px outer margin.”

For brand-led work, research at least four contrasting systems before styling: one mass or value chain, one premium or design-led chain, one story-led independent brand, and one relevant local-market brand. Compare category architecture, signature device, image behavior, material, typography, ordering speed, and touchpoint extension. Record `keep`, `transform`, `reject`, and rights risk; never average the references into a moodboard.

Define a brand premise, a signature device with a functional job, a menu architecture, an image family, and an extension test. The signature device must survive at least three touchpoints such as menu board, takeaway label, QR header, or social crop. Fail `PALETTE-ONLY` when color is the only memory cue, `MOTIF-ONLY` when removing ornament removes the identity, and `ONE-OFF` when adding a category breaks the composition.

Run a three-second cover test before approval: hide the name and logo. The menu should still belong to the same brand through category behavior, image grammar, material, type, and color roles. If not, strengthen the system instead of adding decoration.

For an artistic menu, define a visual thesis and an ornament grammar before prompting:

- thesis: one sentence explaining what makes this menu belong to this food/place;
- source shape: a visible form from the bowl, broth, ingredient, sign, textile, tile or local craft;
- motif grammar: one primary motif, one secondary micro-pattern, and explicit scale/repetition/edge rules;
- flat-art requirement: direct-print artwork, not a menu photographed on a table, held in a hand, placed in a mockup, or shown inside a device;
- palette derivation: no more than four colors, each tied to an observed material or ingredient.

Derive the palette by measuring the reference, not by naming its hues. Run
`marketing-minthep/scripts/sample_reference.py --image REF --check accent=HEX support=HEX` before
locking any brand color that will sit on the same surface as the food. It reports each hue arc's share
of the frame and its chroma, and fails an accent more saturated than the food's own chromatic peak.
"The bowls are blue, so make the rail blue" keeps the hue and discards the two quantities that made it
harmonious — how saturated it was and how little of the frame it held. The result reads as a rectangle
drawn on a photograph, which is the visual signature of a template edit and fails `PALETTE-ONLY`.

Reject decorative additions that cannot be traced to the visual thesis. A local reference is not permission to paste lotus, dragon, palace, bamboo, silk, or “Asian” symbols into the design.

Define motif safe zones. Keep full-strength ornament at edges, image zones, or section transitions; reduce it to background density inside text areas and maintain a clean exclusion zone around every word and price. Decorative marks touching copy fail `ORNAMENT`, even when the motif is sourceable.

## Layout And Typography

Declare reading order before styling:

1. orientation/category;
2. signature dish or offer;
3. food image;
4. item name and price;
5. add-ons/drinks;
6. footer, allergen, service, or ordering note.

Use one emphasis device per priority. Do not combine oversized type, boxes, badges, icons, photos, and color bursts on the same item. Prefer one or two title lines; keep titles visually subordinate to the food unless the brief is explicitly poster-led. Measure Vietnamese copy at the target viewport before forcing line breaks.

Build a type system, not merely a font choice:

- identity: wordmark or restaurant name with distinctive but legible character;
- menu title: medium prominence and never weaker than category labels;
- category: compact navigational voice, visibly subordinate to identity/title;
- item: highly readable Vietnamese text with calm rhythm;
- descriptor: smaller, lighter, increased line-height, still printable;
- price: one tabular treatment and one alignment rule across every category.

Reject the default AI combination of giant condensed category labels plus generic body type. Inspect `Ă Â Ê Ô Ơ Ư Đ` and common tone stacks at full size before accepting a font style.

Set a type-family budget before generation. Default to one Vietnamese-capable superfamily across identity, title, categories, items, descriptions, and prices; create hierarchy with weight, size, width, case, and tracking. Allow a second family only when the contrast has a named role and both families share compatible proportions. Reject `FONT-SOUP` when the skeleton, terminals, x-height, numeral style, or diacritic construction visibly changes without intent.

For a short menu, use a single-column list or a disciplined asymmetric split. Align prices on a common edge. Keep item rows scannable in under two seconds. Use a maximum of two type families and a restrained palette with one accent.

For a dense menu of more than eight items, treat copy as data rather than decoration. Render names and prices deterministically from the locked inventory, then add food imagery around that structure. Do not ask an image model to typeset a production menu with dozens of names and prices. A native-text full-AI version may accompany the production layout only as an explicitly labelled proof and must never replace the source ledger.

When the user selects `full-ai-artwork`, the dense-menu rule changes only in route, not in QA: put the complete copy in one quoted block, use a two-panel or poster composition with low-entropy text zones, and require direct-print flat output. Never hide the copy behind a mockup. The image is still rejected if any row, price or diacritic drifts.

Use descriptions to explain why higher-priced variants differ. If ingredient evidence exists, give main items one concise descriptor line instead of forcing diners to ask staff. Compress repeated add-ons only when they share the same price and the grouping does not hide portion differences or modifiers; record the grouped display copy separately from the source ledger.

Audit negative space as a functional resource, not a prestige effect. Every large empty region must protect reading, separate a category, reserve a known operational element, or create deliberate image tension. Fail `HIERARCHY` when text ends high on the page and an unstructured blank band appears before the food; close the gap by moving the shared scene, regrouping content, or changing the page ratio, never by adding arbitrary ornament.

Before rendering, choose exactly one price grammar for the whole page: right-aligned tabular prices, dotted leaders, or inline dash. Mixing price grammars fails `HIERARCHY`.

## Image Prompt Contract

For dense `full-ai-artwork`, prefer a control-blueprint workflow when image-to-image input is available:

1. render the locked inventory into an exact HTML/SVG blueprint;
2. rasterize it at the final aspect ratio with correct hierarchy, safe zones, grouped rows, descriptions, and price alignment;
3. provide the raster as the strict layout/copy reference;
4. provide separate style and food references when supported, with each role named explicitly;
5. ask the model to redraw the entire image, and paste the locked copy into the prompt as literal strings to typeset rather than asking it to preserve the words that are in the reference;
6. OCR/diff the result against the locked inventory and repair only failed regions.

The blueprint is a control image, not the final design. Keep it visually plain enough that the model can identify structure, but complete enough that no layout decision remains ambiguous.

Probe the provider's actual reference-image schema before promising this route. Do not assume image input requires `/images/edits`: some compatible providers keep `/images/generations` and add an `image` field containing an HTTP(S) URL or a supported data URL. In provider test consoles, a placeholder reference URL may be omitted from the generated request until the field contains a real value; fill it and inspect the resulting request shape before declaring the capability absent. A local filesystem path is never a URL. Use a supported data URL or a deliberately exposed asset URL, and record which transport was accepted.

A prompt-only generations endpoint cannot consume an HTML raster merely because its path is mentioned in text. If the provider's documented generation reference field, edits, multimodal Responses, and multimodal Chat all reject image input, record `CAPABILITY` and keep the blueprint ready for another provider; do not claim that prompt-from-zero used the reference.

Treat reference transport and reference success as separate gates. Probe scalar and array forms when the provider schema is ambiguous: some compatible endpoints reject `"image": "..."` but accept `"image": ["..."]`. An HTTP 200 or an SSE progress stream is not proof of image generation. Require a downloadable URL or decodable image payload, open the saved bitmap, and record the accepted request shape. If the stream ends with text or an error such as “did not return an image,” fail `CAPABILITY`; never relabel a prompt-only render as reference-conditioned.

Before recording `CAPABILITY`, bisect the prompt. A refusal that streams text deltas and never enters an image-generation stage is a routing decision, not a missing capability, and providers report it with whatever error string they have to hand — including one about billing. Hold the endpoint, key and transport fixed and change one thing at a time. In this repository a six-request bisection found that asking a model to preserve the words that are in the supplied reference reliably produced prose instead of a bitmap, while the same request with that one sentence removed returned a 3 MB PNG. Naming a paid tier in an error message is not evidence about the account; only a request that differs in exactly one field is.

That is also why step 5 pastes the copy in as strings. Transcribe-the-reference is both the phrasing most likely to be refused and the one that teaches the model nothing about which words matter, and a model that is merely told to stop preserving the copy will invent a brand name and its own prices. The generative pass never owns the price column: diff every row against the locked inventory afterwards and reject the bitmap that disagrees, because a wrong price on a menu is a commercial fact, not a rendering defect.

When another agent or image service must continue after `CAPABILITY`, create one self-contained handoff beside the control image. Include the exact reference path, locked data path, endpoint and model, accepted request schema, final prompt, rejection labels, and bitmap acceptance checks. Refer to credentials through an environment-variable name; never duplicate a secret into the handoff, repository, logs, screenshots, or chat. State the last provider response verbatim enough to prevent the next agent from repeating a transport probe that already failed.

## Multi-Food Image Program

Build a shot list before generating a menu with more than one food image. For every required shot record dish identity, serving count, vessel, camera angle, crop, scale role, light direction, surface, contact shadow, and forbidden substitutions. Default to a 35-degree diner angle with the entire serving visible unless the brief requires another view.

Assign one composition role to every subject:

- `dominant`: the signature dish and largest visual mass;
- `support`: one or two smaller dishes that explain range without competing with the hero;
- `accent`: the smallest drink, condiment, ingredient, or service cue.

Direct the set as a consistent menu series with shared visual grammar: one camera family, one physical light direction, compatible white balance, related ceramics, believable scale, one surface family, and natural contact shadows. Keep dish-specific truth intact. Reject `DISH-IDENTITY` when a serving changes form, count, wrapper, vessel, garnish, or key ingredient; reject duplicated dishes and invented toppings.

When the provider accepts only one image field, build one composite reference board containing the exact text blueprint plus all required food references. Label each image role in the board and prompt. The board must communicate dominance, support, accent, and safe zones without looking like the desired final layout.

Reject equal thumbnails, circular portrait sets, card grids, product catalogs, contact sheets, and Canva-style collages unless the user explicitly requests that language. Integrate multiple foods through varied scale, overlap, edge crop, shared shadow, and a sourceable motif; do not place every dish in the same frame shape.

Choose one primary image family: continuous table scene, disciplined product modules, ingredient/process atlas, story ephemera, or photo-led restraint. Allow at most one supporting behavior. For a continuous table scene, every dish must share one physical surface, horizon/perspective family, light direction, white balance, and shadow field; isolated cutouts placed on empty paper fail `SCENE-COHERENCE` even when each cutout is individually attractive.

For food photography specify subject truth, camera height/angle, lens behavior, light direction/hardness, surface, contact shadow, crop, and what is intentionally ordinary. Add rejects: no ingredient explosion, duplicated toppings, impossible steam, floating bowl, glossy CGI food, decorative border, fake logo, random text, or luxury cliché.

For a cutout composite, prefer extracting the served dish from a real source photograph. If no usable source exists, generate one proof on a removable chroma-key field before scaling. Validate alpha coverage, transparent corners, edge halos, subject completeness, and color contamination. Derive the palette or motif from a visible property of the dish, bowl, or restaurant rather than adding unrelated decoration. Rebuild contact shadow and color response for the destination surface; a clean cutout with no grounding is still a sticker.

For `full-ai-proof`, include exact copy in a quoted block and require:

- native Vietnamese diacritics;
- title under roughly 10% of canvas height and never more than two lines;
- exact prices and footer;
- generous low-entropy text zones;
- no extra words, fake glyphs, watermark, or text collision.

Inspect every result at full size. A prompt is not proof of text fidelity.

For `full-ai-artwork`, additionally specify medium and finish: screenprint, risograph, painted sign, woodblock, enamel, collage or another deliberate technique. Name the ink behavior, registration, edge, grain and paper only when they support the thesis. Do not stack five techniques in one image.

For a researched full menu, also compare the rendered rows against the locked data file: category count, item count, exact spelling, exact price, missing rows, duplicated rows, and source note. Fail the render if any count or value drifts.

## Art Direction Gate

Before the anti-AI gate, score the image from 0–2 on each axis: visual thesis, motif sourceability, palette discipline, composition tension, food truth, typography fidelity, and direct-print readiness. A concept with a beautiful texture but no thesis is not art direction.

Also inspect content geometry: compare text mass, image mass, and negative space by quadrant. Repair imbalance by grouping repeated rows, adding evidence-backed descriptors, moving the food crop, or changing the column structure; do not fill holes with arbitrary ornament.

## Anti-AI Gate

Reject `GENERIC` when the category alone predicts the visual: black-and-gold luxury, symmetric ornamental border, marble, smoke, random silk, fake vintage grain, giant serif title, centered hero bowl, excessive garnish, or “cinematic” lighting without physical behavior. Also reject second-order defaults such as beige editorial cards or maximalist collage when no brief-driven reason exists.

Record concrete rejection labels: `CAPABILITY`, `GENERIC`, `HIERARCHY`, `FONT-SOUP`, `DISH-IDENTITY`, `SCENE-COHERENCE`, `PALETTE-ONLY`, `MOTIF-ONLY`, `ONE-OFF`, `CROP`, `PHYSICS`, `CLAIM`, `FIDELITY`, `OFF-BRAND`, `ORNAMENT`, `PALETTE`, `MOCKUP`, or `RIGHTS`.

Run a visible self-improvement loop: generate, inspect at full size, attach concrete rejection labels, change one targeted variable, regenerate, and compare against the previous candidate. Promote a variant only after copy, price, dish identity, hierarchy, motif safe-zone, physics, and direct-print checks pass. Preserve the selected prompt, references, rejected variants, and rejection log so the next run learns from evidence instead of adding more adjectives.

## Deliverable

Return:

- three option cards and one recommended direction;
- the five-layer art direction brief;
- a low-fidelity wireframe with reading order;
- copy pack and image prompt(s);
- format/export specs;
- QA checklist and rejection log.

For a real production request, write these artifacts to the workbench and run its strict status check before claiming completion.

Before delivery, open the real output and record visual QA. Confirm that all menu rows remain above or beside the food image, no title dominates the page, Vietnamese line breaks are intentional, prices share an alignment edge, and the footer identifies benchmark versus for-sale status.

For `full-ai-artwork`, confirm the output is a flat artwork intended for direct export: no browser chrome, device frame, tabletop mockup, hand, envelope, or photographed menu object unless the user explicitly requests that presentation. Record the visual thesis, motif source, palette roles, rejected variants, and the exact final asset path.
