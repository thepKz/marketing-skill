# Prompt Contracts

## Master image prompt

Write a production contract in priority order:

```text
JOB AND SINGLE IDEA
Create [asset] for [audience/channel]. Communicate [one idea].

REFERENCES AND LOCKS
Reference priority: [list]. Preserve exactly: [identity/product/logo/color/material/geometry].

SUBJECT AND ACTION
[Who or what, physical details, pose/action, expression, product interaction.]

SCENE AND SOCIAL CONTEXT
[Location or set, time, cultural context, prop logic, capture mode.]

COMPOSITION AND CROP
[Shot size, camera height, angle, placement, focus target, background distance, copy-safe area, ratio.]

CAMERA BEHAVIOR
[Full-frame-equivalent lens intent, camera distance, aperture/depth intent, shutter/motion intent, ISO/noise intent, white balance.]

LIGHTING GEOMETRY
[Key source, modifier, position, height, distance, fill level, separation, spill, background treatment.]

REALISM AND MATERIALS
[Skin, hair, anatomy, fabric, packaging, reflections, contact, texture, retouching level.]

TEXT
[Exact short text only when the provider and workflow support it; otherwise add typography during layout.]

REJECT
[Short, asset-specific failure list.]
```

Numbers are visual instructions, not unverifiable claims that a generated file has real EXIF data.

## Edit prompt

```text
EDIT OBJECTIVE
[One sentence describing the final result.]

CHANGE
- [Exact change]

LOCK
- [Identity, product, composition, text, or material details that must remain exact]

MATCH
- [Perspective, light direction, exposure, grain, depth, color spill, reflection, material behavior]

MASK OR REGION
- [Precise spatial description]

REJECT
- [Artifacts, reconstruction drift, and unintended changes]
```

Prefer localized passes over full regeneration when exact regions must remain stable.

## Variant control

Change one or two named axes per variant:

- `V1-composition`: safer hierarchy.
- `V2-composition`: deliberate asymmetry or crop.
- `V3-proof`: clearer mechanism or evidence.
- `V4-action`: more natural human or product interaction.
- `V5-light`: alternate motivated lighting geometry.
- `V6-capture`: studio-natural versus environmental or phone-candid.

Do not create variants by swapping random style adjectives.

## Prompt output record

Store or return:

- Prompt ID, campaign/content lineage, channel, and ratio.
- Input references and priority.
- Lock list and unknowns.
- Master prompt and provider adaptation.
- Negative constraints and controlled variable.
- Provider settings when available.
- Selected output, rejection reasons, edit pass, and export notes.

Use `assets/templates/image-prompt-record.json` for machine-readable handoff.
