# Makeup Art Direction

## Contents

- Reference confidence
- Makeup contract
- Look lanes
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
