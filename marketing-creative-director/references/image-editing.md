# Image Editing

## Build an edit contract

Before editing, separate the request into four lists:

1. **Change**: the exact regions, objects, colors, text, background, lighting, or composition to modify.
2. **Lock**: everything that must remain unchanged.
3. **Match**: perspective, grain, light direction, depth of field, reflection, material, and color behavior the new content must inherit.
4. **Reject**: artifacts or unintended transformations that invalidate the edit.

If the user supplies multiple references, rank them: identity, product, style, environment, composition.

## Common edit workflows

### Background replacement

- Preserve subject edges, flyaway hair, transparent materials, contact shadows, and reflected color.
- Match camera height, horizon, perspective, depth of field, and light direction.
- Rebuild realistic floor or surface contact; do not leave a cutout floating.

### Product compositing

- Lock product geometry, logo, label, cap, color, and material.
- Match scene reflections to glossy or metallic packaging.
- Preserve real scale relative to hands, furniture, or environment.
- Add only claims and label text supplied by the user.

### Human retouching

- Preserve identity and realistic skin texture by default.
- Make local corrections instead of globally smoothing skin.
- Keep natural facial asymmetry, hair detail, eye reflections, and hand anatomy.
- Do not change body shape, skin tone, age presentation, or facial structure unless explicitly requested.

### Object removal

- Reconstruct hidden texture and perspective rather than blurring the region.
- Check repeated patterns, edges, shadows, and reflections where the object existed.

### Color or material change

- Preserve luminance, folds, highlights, texture scale, and reflected environment.
- Update secondary color spill and reflections caused by the changed surface.

### Text and packaging change

- Prefer adding exact typography in design software after image generation.
- If image editing must render text, provide the exact string, position, hierarchy, and reference, then inspect every character.
- Reject pseudo-text, misspellings, duplicated logos, and inconsistent perspective.

## Multi-pass strategy

Use the smallest edit per pass when fidelity matters:

1. Establish composition or background.
2. Fix subject integration and light.
3. Correct product or identity details.
4. Add typography outside the image model when possible.
5. Export channel crops from the verified master.

Do not repeatedly regenerate the entire image for a local defect. Use masks or localized edits when the tool supports them.

## Edit QA

Inspect at full size and thumbnail size:

- Edges and masks.
- Hands, face, hair, logos, labels, and small repeated details.
- Contact shadows, reflections, and light direction.
- Perspective and scale.
- Color spill and white balance.
- Compression, grain, sharpness, and depth-of-field continuity.
- Differences from the lock list.

