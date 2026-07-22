# Reference-First Image Flow

## Contents

- Default user experience
- Reference role map
- Clarification gate
- Direction and variant design
- Generation loop
- Celebrity and identity handling
- Delivery contract

## Default user experience

Use this flow when the user supplies one or more images with a description:

```text
references + description + intended use
-> analyze reference roles
-> preserve locks and extract visual grammar
-> ask only material questions, otherwise proceed
-> choose provider and execution mode
-> generate one final or four controlled variants
-> inspect, reject failures, and refine the selected direction
```

Do not force the user to fill a long form. Infer reversible details and show the assumptions briefly.

## Reference role map

Assign each image one primary role and optional secondary roles:

| Role | Extract | Preserve only when authorized |
|---|---|---|
| `identity` | Face, body, age presentation, distinguishing features | Exact identity and proportions |
| `product` | Shape, logo, packaging, material, label plane | Exact product geometry and approved text |
| `pose` | Weight distribution, hand task, gaze, gesture | Pose family, not accidental anatomy defects |
| `composition` | Shot size, camera height, angle, subject placement, negative space | Spatial grammar |
| `lighting` | Key direction, source size, fill, separation, color, background exposure | Light behavior |
| `styling` | Hair, makeup, wardrobe, accessories, set language | Non-protected styling qualities |
| `color-grade` | White balance, contrast, saturation, highlight rolloff, grain | Tonal treatment |
| `texture` | Skin, fabric, film, surface, material behavior | Material response |

Return a compact reference map:

```text
Image 1: composition + lighting
Image 2: styling + pose
Image 3: product lock
Identity intent: style-only / preserve-authorized-subject / unknown
```

## Clarification gate

Proceed without asking when:

- The user describes the subject and desired outcome.
- Reference roles can be inferred safely.
- The output channel or ratio can be inferred or left `auto`.
- The work uses an original fictional adult rather than reproducing a public figure.

Ask at most three short questions when an answer materially changes:

1. **Identity**: Is a supplied person the edit target to preserve, or only a style reference?
2. **Use and ratio**: Is this for `9:16`, `4:5`, `1:1`, web hero, or another fixed placement?
3. **Direction**: Should the result feel studio-clean, studio-natural, environmental-editorial, or phone-candid when the references conflict?

If the user says “make something like this” and the images feature celebrities, default to a fictional adult with the same non-identifying photographic grammar. State the assumption and proceed.

## Direction and variant design

Create one canonical direction containing:

- Single communication idea.
- Reference map and priority.
- Subject/product locks.
- Capture mode.
- Composition and crop.
- Camera and lighting geometry.
- Styling, materials, and color finish.
- Negative constraints.

When producing four variants, use this default spread:

1. `V1-anchor`: closest safe translation of the reference grammar.
2. `V2-composition`: change camera distance, placement, or crop.
3. `V3-light`: change one motivated light setup while keeping styling stable.
4. `V4-action`: change pose, gesture, or product interaction.

Optional fifth:

5. `V5-departure`: one controlled art-direction break with explicit risk.

Keep identity/product locks, message, ratio, and major styling stable unless that variable is the named test.

## Generation loop

1. Build the provider-neutral master prompt.
2. Run `scripts/plan_image_generation.py`.
3. Compile the provider prompt with `scripts/compile_prompt.py`.
4. Generate all exploration variants from the same canonical reference map.
5. Inspect each output for identity/product fidelity, anatomy, physics, reference use, and crop.
6. Reject critical failures before showing a recommendation.
7. Recommend one result and explain the decisive strength in one sentence.
8. Refine only the selected result with a single-change instruction.

Do not chain V2 from V1, V3 from V2, and V4 from V3. Serial mutation compounds drift. Branch variants from the same source state, then use multi-turn editing only on the selected branch.

## Celebrity and identity handling

For public-figure references such as Jang Wonyoung or aespa:

- Analyze pose family, framing, light, styling, makeup language, wardrobe silhouette, palette, set, and grade.
- Do not use the celebrity name in the execution prompt when the goal is an original marketing image.
- Replace recognizable identity with `fictional adult subject` and brief-appropriate casting.
- Do not imply endorsement, collaboration, or product use by the public figure.
- Preserve exact identity only for a permitted edit where the user supplied or authorized the target image and the requested change is allowed.

## Delivery contract

Return:

1. Assumptions and any identity safety translation.
2. Reference map.
3. Recommended provider and why.
4. Master direction.
5. One final image or four/five labeled variants.
6. QA notes and rejected failures.
7. One recommended next edit.

If rendering is unavailable, return the same structure with executable prompts and explicitly say no images were rendered.
