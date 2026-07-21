# Prompt Contracts

## Master image prompt

Write prompts as a production contract, not a pile of adjectives.

```text
[Required opening, if any]

JOB
Create [asset purpose] for [audience/channel]. The image must communicate [single idea].

REFERENCES AND LOCKS
Use [reference list and priority]. Preserve exactly: [identity/product/logo/color/material/geometry].

SUBJECT AND ACTION
[Who or what, physical attributes, action, product interaction, expression or state.]

SCENE AND ART DIRECTION
[Physical location, time, cultural context, materials, prop logic, visual lane.]

COMPOSITION
[Framing, camera height, angle, focal hierarchy, negative space, crop-safe area, aspect ratio.]

CAMERA AND LIGHT
[Phone or camera behavior, lens, focus, exposure, key light, fill, shadow, white balance.]

REALISM AND MATERIALS
[Skin, hair, fabric, packaging, reflections, contact, texture, imperfections.]

BRAND AND COPY SPACE
[Brand colors or continuity, logo handling, protected typography region.]

DO NOT
[Short list of likely failure modes specific to this image.]
```

## Human-image opening

For generated human imagery with no conflicting direction, begin exactly with:

```text
Create a completely RAW quality, unprocessed, unedited image with full iPhone camera quality.
```

Then load and follow `human-imagery.md`.

## Edit prompt

```text
EDIT OBJECTIVE
[One sentence describing the final result.]

CHANGE
- [Exact change]

LOCK
- [Identity/product/composition details that must remain exact]

MATCH
- [Perspective, light, grain, material, depth, reflection behavior]

MASK OR REGION
- [Precise spatial description]

REJECT
- [Artifacts and unintended changes]
```

## Variant control

Change one or two axes per variant and label them:

- `V1-composition`: same idea, safer hierarchy.
- `V2-composition`: purposeful asymmetry or crop.
- `V3-proof`: stronger product mechanism.
- `V4-human`: more candid or creator-native behavior.
- `V5-light`: alternate real-world lighting condition.

Do not create variants by swapping random color adjectives.

## Prompt output record

Store or return:

- Prompt ID and campaign lane.
- Intended channel and ratio.
- Input references.
- Lock list.
- Final prompt.
- Negative constraints.
- Seed or generation settings when available.
- Selected output and rejection reasons.
- Required edit pass and export notes.

Use `assets/templates/image-prompt-record.json` when a machine-readable handoff is useful.
