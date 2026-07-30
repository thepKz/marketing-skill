# Makeup Art Direction

## Contents

- Reference confidence
- Makeup contract
- Look lanes
- Identifying a look from a photograph
- Beauty pose contract
- Reference mixing
- QA
- Research pool

## Reference confidence

Treat a social profile as a discovery source, not a stable visual preset. A profile can contain conflicting campaigns, makeup artists, lighting, retouching, and eras.

- `profile-level hypothesis`: Use when only a profile URL is available. Label the direction as inferred and ask for 3-8 post URLs or screenshots when exactness matters.
- `post-level observation`: Use when a specific post, frame, or screenshot is visible. Map only what is actually present.
- `authorized identity reference`: Use only when the supplied person is the permitted edit target. Otherwise extract non-identifying makeup, pose, hair, light, and grade.

Do not use a public figure's name in an execution prompt for an original marketing image. Convert the observed grammar into fields for a fictional adult subject.

## Makeup contract

Specify makeup through these nine axes. Do not rely on labels such as `K-pop makeup`, `clean girl`, or `glam` alone.

1. `skin_finish`: natural, satin, luminous, soft-matte, glossy/wet, or deliberately powdered.
2. `coverage_texture`: sheer, medium, or full; state whether pores, peach fuzz, freckles, and tonal variation remain visible.
3. `brows`: straight or arched, soft or defined, density, front diffusion, and tail shape.
4. `eyeshadow`: hue family, placement, edge softness, lid depth, lower-eye treatment, shimmer location, and aegyo-sal treatment when relevant.
5. `liner_lashes`: liner color and path, wing geometry, tightline, lower-lash definition, lash separation, density, and cluster behavior.
6. `cheeks`: blush hue, intensity, diffusion, and placement such as central, high cheek, under-eye, temple-draped, or sun-kissed.
7. `contour_highlight`: placement, strength, undertone, and whether highlights are diffuse, pearl, or specular.
8. `lips`: hue, opacity, center-to-edge behavior, edge sharpness, gradient, stain, balm, gloss, satin, matte, or lacquer finish.
9. `palette_retouch`: warm/cool/neutral palette, contrast, skin-tone protection, editorial or commercial cleanup, and prohibited reshaping.

Keep makeup compatible with the light. A luminous base needs controlled specular highlights; a dark smoky eye needs enough fill to retain color and lash separation; glossy lips need a plausible source-shaped reflection.

## Look lanes

Use a lane as a starting system, then write all nine axes explicitly.

| Lane | Useful grammar | Avoid |
|---|---|---|
| `bare-minimal` | Sheer skin, brushed brows, tightline, muted cheeks, balm lip | Calling an obviously polished face unretouched |
| `fresh-luminous` | Satin glow, champagne detail, separated lashes, high translucent blush, glossy tint | Oily forehead, pore erasure, random glitter |
| `quiet-luxury` | Soft-matte or satin skin, taupe eye, restrained contour, rosewood lip | Generic beige wash with no facial structure |
| `romantic-glossy` | Rose-beige eye, soft straight brow, central/high blush, blurred glossy gradient lip | Doll-face anatomy or identity copying |
| `cool-crystalline` | Icy pink, silver, or lilac accents, precise liner, separated/spiky lashes, cool pink blush | Blue skin, metallic spill, plastic texture |
| `sculpted-feline` | Elongated smoky wing, temple blush, controlled cheek structure, neutral lacquer lip | Changing jaw, eye size, or facial anatomy |
| `smoky-grunge` | Smudged liner, deeper lash line, imperfect edge, muted or deep lip, harder flash | Accidental raccoon eye or crushed shadow detail |
| `graphic-editorial` | Color block, graphic liner, metallic or gem accent with one dominant device | Combining every experimental device at once |
| `monochrome-tonal` | One hue family repeated across eye, cheek, and lip with varied texture | Flat color with no material separation |

## Identifying a look from a photograph

A lane above is a starting mood. It cannot answer the question that actually arrives, which is somebody pasting a photo and asking what this is and how to brief it. That needs rows, and `data/makeup-looks.csv` holds 47 of them: ten families, each row carrying all nine axes plus the tell that identifies it, the look it gets mistaken for, and the one observation that separates the two.

Run `scripts/read_makeup.py`:

- `--observe "wet skin, no crease, blush under the eye"` ranks candidates by which of your observations each row accounts for, and names which column matched. Free text, Vietnamese or English, diacritics optional. Exit 2 means more than one candidate survived, which is a state to continue from rather than a failure.
- `--ask` prints the whole diagnostic sequence from `data/makeup-diagnostics.csv`.
- `--brief LOOK_ID` prints one look as the nine-axis contract with its light requirement, its `use_when` and `avoid_when`, and the questions that have to be settled before shooting.

### Misidentification is the failure mode, not ignorance

Nobody briefs the wrong look because they have never heard of it. They brief the wrong look because two looks share a name in casual use and differ in exactly one place. That one place is the `discriminator` column, and it is the most load-bearing content in the table.

| Confused pair | Where to look |
|---|---|
| `kr-mul-gwang` vs `us-glass-skin` | Edges. Glass skin has a visible highlight boundary; mul-gwang has none, because the glow is the base rather than a product on top of it. The most common misidentification in the table. |
| `kr-gradient-lip` vs `us-overlined-lip` | Which side of the lip border the colour falls on. A gradient fades out before it; an overline crosses it. One hides the outline, the other invents one. |
| `us-siren-eye` vs `jp-ulzzang-doll` | Placement, and they are exact opposites. Siren empties the inner corner and loads the outer; doll-eye loads the centre and brightens the inner corner. |
| `kr-mul-gwang` vs `ed-wet-editorial` | Whether the water is real. Wet editorial has discrete droplets with their own highlights and pigment that has visibly run; mul-gwang is dry to the touch. |
| `cn-douyin` vs `us-instagram-glam` | Direction of the sculpting. Douyin narrows the whole face; Instagram glam widens the eye and the lip. One shrinks features, the other inflates them. |

### The order to ask in

Eleven questions read the photograph. `--observe` sorts them by how many candidates the worst-case answer would remove from the current shortlist, so the order changes with the shortlist rather than being fixed. The single highest-yield question in general is where the liner is thickest, because that one placement separates the Korean, Japanese, Western-commercial and editorial families at once.

Four questions have `information_value: blocking` and no photograph answers any of them: whether the reference is licensed and whether the person in it is the person being published, what the product claims and whether the base contradicts it, what size the image will be seen at, and which market it is for. A brief that omits these is executable and still wrong. `--brief` prints them whether or not they were asked.

### What the grades mean here

Every row is graded, and the grades are not flattering. 28 rows are `craft-heuristic`, 8 are `inferred`, 7 are `industry-primary`, one is `physics` (`tech-flashback-safe`, where titanium dioxide reflecting flash is measurable rather than stylistic), and one is `myth-adjacent`: `us-glass-skin`, because the Western usage detached from the Korean original and now names a different look than the word implies. Every `source` cell begins `Recall, unverified 2026-07-30` and names a specific place to check. None of it was verified against a primary source, because web access was unavailable when the table was written. Read the source cell before quoting a row to a client.

Four rows are not styles at all. `tech-flashback-safe`, `tech-ecommerce-swatch`, `tech-before-after` and `af-deep-skin-editorial` are the makeup decisions that determine whether a frame is usable or a claim is supportable, and they are in a marketing skill for that reason.

## Beauty pose contract

Lock pose separately from makeup:

- Crop and camera distance.
- Face angle, chin height, gaze target, and head tilt.
- Shoulder line, neck extension, and weight distribution.
- Hand task and product contact; fingers must have a believable job.
- Hair placement and which facial planes remain visible.
- Micro-expression and social context.

For four variants, keep the subject and identity treatment stable:

1. `clean-anchor`: closest safe translation of the selected makeup and pose grammar.
2. `makeup-forward`: change one makeup axis or lane while preserving light and pose.
3. `lighting-forward`: preserve makeup; change one motivated light setup.
4. `editorial-pose`: preserve makeup and styling; change crop, gaze, or hand task.

Use a fifth hybrid only when the user requests a more experimental departure.

## Reference mixing

Use no more than three strong sources per canonical direction:

1. Subject mood, pose, hair, or wardrobe.
2. Makeup detail.
3. Lighting, crop, or color grade.

Label granular roles such as `makeup-base`, `makeup-eyes`, `makeup-lips`, `pose`, `hair`, `lighting`, and `grade`. Do not merge identity into the makeup reference.

Examples of controlled combinations:

- Natural skin realism + cool crystalline eye geometry + romantic glossy blush/lip.
- Quiet-luxury makeup + hard-flash editorial lighting.
- Sculpted feline makeup + restrained studio-natural skin and a clean close-up crop.

## QA

Reject or repair when:

- Skin undertone changes between face, neck, ears, and hands.
- Pores and tonal variation disappear without an approved commercial-retouch reason.
- Makeup floats above the face rather than following eyelid, cheek, and lip geometry.
- Liner, lashes, pupils, catchlights, or lip reflections conflict with the camera angle or light.
- Blush, contour, or highlight alters facial anatomy instead of describing it.
- Lip edges merge with teeth, gums, applicator, hair, or fingers.
- Product shade or finish is presented as exact without a calibrated product reference.
- The generated subject becomes recognizable as a celebrity reference.
- An authorized edit target becomes a more generic or different-looking person.
- Makeup changes eyelid folds, eye spacing, nose geometry, lip boundary, jawline, chin, age presentation, or natural asymmetry.

For authorized real-person edits, list identity locks before the makeup axes. Makeup may change color, coverage, finish, liner, lash styling, blush, highlight, and lip surface only. It may not change facial proportions or replace the subject's skin.

## Research pool

Checked 2026-07-22. Instagram profile URLs are discovery sources only; public access does not grant republication rights.

### User-selected profile references

- https://www.instagram.com/for_everyoung10/ - romantic glossy, polished beauty hypothesis.
- https://www.instagram.com/goyounjung/ - cinematic natural, quiet-luxury hypothesis.
- https://www.instagram.com/imwinter/ - cool crystalline, graphic-pop hypothesis.
- https://www.instagram.com/katarinabluu/ - sculpted feline, futurist-glam hypothesis.

### Makeup and editorial references

- https://www.instagram.com/jsmbeauty_/ - translucent base and skin-first beauty.
- https://www.instagram.com/bit.boot_jungyo/ - clean idol and no-makeup makeup.
- https://www.instagram.com/nakyeum/ - sculptural face direction.
- https://www.instagram.com/minah9022/ - smoky and grunge direction.
- https://www.instagram.com/ponysmakeup/ - graphic liner and editorial color.
- https://www.instagram.com/allurekorea/ - beauty detail, skin finish, and controlled reflection.
- https://www.instagram.com/voguekorea/ - luxury editorial composition.
- https://www.instagram.com/wkorea/ - experimental light, crop, and makeup.

Useful expansion profiles include `jennierubyjane`, `xeesoxee`, `hoooooyeony`, `skuukzky`, `vousmevoyez`, and `noodle.zip`. Confirm a specific post before turning any profile-level label into a production contract.
