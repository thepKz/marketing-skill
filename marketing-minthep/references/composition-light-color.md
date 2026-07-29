# Composition, Light, and Color Direction

Use this reference to turn a vague request such as `modern`, `premium`, `appetizing`, or `artistic` into a physical shot plan. For the evidence and calculations behind these rules, consult `dossiers/composition-and-layout-vision.md`, `dossiers/light-and-shadow.md`, and `dossiers/materials-and-surfaces.md`.

## Decision order

1. Name the communication job: recognition, appetite, proof, instruction, aspiration, comparison, or atmosphere.
2. Choose one dominant subject and one secondary attention target.
3. Choose the aspect ratio and reserve channel-safe copy space before styling.
4. Specify camera height, angle, distance, shot size, subject occupancy, and crop locks.
5. Specify light by source size, direction, distance, subtraction/fill, and background exposure.
6. Choose a color role for each surface; do not choose a palette independently of product truth and light.

## Composition choices

| Job | Starting composition | Typical failure |
|---|---|---|
| Clear product recognition | Optical center, clean silhouette, 60-85% occupancy | Moving the hero off-center only to obey thirds |
| Appetite or tactile desire | Macro or close three-quarter view, visible surface texture, edible entry point | Too many garnishes, impossible steam, no bowl contact |
| Demonstration | Hands and product action near frame center, mechanism readable | Face or props outcompete the action |
| Premium brand world | Controlled negative space, few objects, precise material contrast | Empty space with no hierarchy or proof |
| Editorial tension | Deliberate asymmetry, diagonal or crop intrusion | A small accidental offset that reads as bad alignment |
| Multi-SKU comparison | Hero centered, consistent scale and baseline, one controlled variable | Inconsistent product size, label plane, or spacing |

For product-led imagery, the hero should be at least roughly `1.3x` stronger than the next visual element at thumbnail size. Faces and readable text are strong attention magnets; redirect gaze, reduce face size, darken it, or crop it when the product loses.

## Light contract

Never request only `cinematic lighting`. State:

```text
key source apparent size + azimuth/elevation + distance + fill/subtraction in stops
+ separation/rim when needed + background exposure + contact-shadow behavior
```

Operational rules:

- Large close sources create broad transitions and large catchlights; small or distant sources create harder edges.
- Groups and deep products usually need the source farther away for more even exposure.
- A soft source still produces a dark, crisp seam at the exact contact point. Reject shadows that become lighter at contact and darker farther away.
- Catchlight size and shadow hardness must agree. A huge catchlight with a razor-hard nose shadow is physically inconsistent.
- For glass, metal, glossy packaging, and liquids, shape reflections with cards or strips rather than trying to remove all highlights.

## Color system

Assign colors by role:

- `truth color`: product, food, skin, packaging, or ingredient color that must remain accurate.
- `brand anchor`: one recognizable brand hue or neutral family.
- `attention accent`: CTA, garnish, prop, or highlight used sparingly to direct attention.
- `environment field`: the supporting background and surface family.
- `grade`: white balance, contrast curve, saturation, highlight rolloff, black level, and grain.

Prefer a dominant family plus one accent over a palette of equally saturated colors. Use luminance contrast before saturation to create hierarchy. For food, protect believable browns, reds, greens, fat sheen, and steam neutrality; do not force every ingredient into the brand palette. For skin, preserve local hue variation and prevent colored backgrounds from contaminating skin beyond plausible reflected spill.

## Prompt block

```text
COMMUNICATION JOB AND HERO
COMPOSITION: ratio, shot size, camera height/angle, placement, occupancy, negative space, crop locks
LIGHT: source size, direction, distance, fill/subtraction, background exposure, contact shadow
COLOR: truth colors, brand anchor, accent, environment field, grade and white balance
MATERIAL RESPONSE: roughness, translucency, condensation, oil, metal/glass reflections, fabric or skin texture
REJECT: competing hero, floating object, impossible shadow, clipped required detail, color contamination, fake text
```

## QA

- The communication job is clear at thumbnail size.
- The hero survives every required ratio without blind cropping.
- Every shadow, catchlight, reflection, and color spill has an explainable source.
- Product, food, skin, packaging, and brand colors remain credible.
- Negative space is usable rather than merely empty.
- A deliberate rule break is strong enough to read as intentional.
