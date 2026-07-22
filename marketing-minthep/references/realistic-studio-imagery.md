# Realistic Studio Imagery

## Contents

- Realism model
- Camera specification
- Lighting specification
- Composition and geometry
- Human and material behavior
- Capture recipes
- Prompt recipe
- QA and source notes

## Realism model

Photorealism comes from a coherent physical system, not from repeating `photorealistic`, `8K`, `RAW`, or camera brand names. Make these layers agree:

1. **Optics**: field of view, perspective, working distance, depth of field, focus falloff.
2. **Exposure**: aperture intent, motion behavior, noise level, highlight and shadow latitude.
3. **Light**: source size, direction, height, distance, hardness, fill, spill, and color.
4. **Geometry**: subject-to-camera and subject-to-background distance, camera height, pose, contact, and occlusion.
5. **Materials**: skin, hair, fabric, glass, metal, paper, liquid, and packaging respond differently.
6. **Capture signature**: studio, environmental, phone, flash, film-like, or polished commercial.
7. **Post-production**: contrast, sharpening, grain, color separation, and retouching remain plausible for the capture mode.

Do not request mutually contradictory traits such as deep focus at `f/1.2`, a sharp moving hand at a slow shutter, or hard noon shadows from a giant frontal softbox.

## Camera specification

Use full-frame-equivalent focal lengths as visual shorthand unless the provider exposes real camera controls.

| Intent | Starting range | Behavior |
|---|---:|---|
| Environmental phone-like scene | 24-35mm | Includes context; close distance can exaggerate near features |
| Natural half/full body | 35-50mm | Moderate context and believable spatial relationship |
| Portrait or beauty | 70-105mm | Narrower angle, comfortable distance, controlled background |
| Product hero | 70-120mm | Low distortion and clean proportions |
| Texture or detail | 90-120mm macro behavior | Close focus, shallow depth, precise material detail |

Nikon documents that shorter focal lengths create a wider angle of view, while longer focal lengths create a narrower angle with greater magnification; it also identifies 70-200mm as common for portrait and product work. Use this as optical guidance, not a guarantee that a model simulates a named lens exactly.

Specify aperture by focus intent:

- `f/1.8-f/2.8 intent`: shallow focus, one eye or one product plane dominant; higher failure risk for groups and labels.
- `f/4-f/5.6 intent`: natural portrait or product separation with more usable detail.
- `f/8-f/11 intent`: product sets, groups, or scenes where several depth planes must read.

Nikon notes that lower f-numbers produce shallower depth of field and higher f-numbers produce greater depth of field. Also specify what must be sharp; an f-number alone is insufficient.

Specify shutter and ISO as behavior:

- `1/125-1/250s intent`: stable portrait and hand detail.
- `1/500s+ intent`: frozen motion, hair, liquid, or fabric.
- `1/30-1/60s intent`: deliberate ambient blur or phone-night character; state what stays sharp.
- `ISO 100-400 intent`: clean controlled studio file.
- `ISO 800-3200 intent`: plausible low-light texture and restrained chroma/luma noise.

Specify white balance by source: neutral flash/daylight near 5200-5600K, warm practical interior near 3000-4000K, or deliberate mixed light. Treat Kelvin values as direction, not fake EXIF evidence.

## Lighting specification

Describe light in physical terms:

```text
key source + modifier + position + height + distance + fill + separation + background treatment
```

Examples:

- `Large diffused key 45 degrees camera-left, slightly above eye level, close to subject; white bounce camera-right one to two stops under key; unlit gray background two meters behind.`
- `Medium hard reflector high camera-right, negative fill camera-left, narrow rim from behind, black seamless held one stop below subject.`
- `Top-front strip softbox for bottle label, two tall side cards shaping the edges, cross-polarized reflection control, low frontal fill, grounded contact shadow.`

Use ratio language as a starting intent:

- `1:1`: near-flat beauty or catalog light.
- `2:1`: soft natural modeling.
- `4:1`: more dramatic portrait depth.
- `8:1+`: high contrast; preserve important shadow detail deliberately.

When a generator does not understand ratios reliably, translate them to `fill one stop under key`, `fill two stops under key`, or `almost no fill`.

Light size is relative to the subject. A large close source creates broad transitions and large catchlights; a smaller or farther source creates harder edges. Background brightness must be directed independently when a studio look is required.

## Composition and geometry

Set:

- Aspect ratio and final channel.
- Shot size: extreme close-up, close-up, medium, three-quarter, full, or environmental.
- Camera height: eye, chest, waist, floor, or overhead.
- Camera angle and subject angle.
- Dominant plane and focus target.
- Subject placement and gaze/action vector.
- Negative space location for copy.
- Background distance and visual entropy.
- Crop locks: do not cut joints, product closure, logo, hands, or required context.

Use one compositional system deliberately:

- Centered or optical symmetry for product authority and catalog clarity.
- Rule-of-thirds or off-axis balance for natural lifestyle direction.
- Diagonal movement for fashion, action, or scroll-stopping tension.
- Frame-within-frame for environmental depth.
- Layered foreground/midground/background for candid realism.
- Repetition with one break for range or campaign systems.

Do not combine every rule. One dominant subject and one dominant message should survive at thumbnail size.

## Human and material behavior

For people, specify:

- Fictional adult casting appropriate to the market and brief.
- Natural skeletal balance, weight-bearing leg, shoulder and hip relationship.
- Action that gives hands a believable job.
- Eye focus, micro-expression, breath, and social context.
- Pores, peach fuzz, fine lines appropriate to age, tonal variation, natural asymmetry, flyaway hair, fabric pressure, and contact shadows.
- Retouching level: none, editorial cleanup, or commercial cleanup; never erase skin structure by default.

For products, specify exact scale, support, contact shadow, edge reflections, label plane, cap/pump geometry, surface roughness, translucency, condensation, fingerprints, and whether imperfections are acceptable.

## Capture recipes

### Studio-natural beauty portrait

```text
85mm portrait behavior, camera at eye level, head-and-shoulders framing, focus on the near iris,
f/4 depth intent, 1/200s motion intent, clean ISO 200 texture, 5400K neutral color.
Large diffused key 45 degrees camera-left and slightly above eye level, white bounce one stop under key,
subtle hair separation, matte gray background two meters behind. Natural pores and asymmetry,
editorial cleanup only, no pore erasure or reshaping.
```

### Controlled product hero

```text
100mm product-lens behavior, three-quarter view at label height, f/8 depth intent, all required label and closure planes sharp.
Large top-front diffusion, two side cards defining edge highlights, low frontal fill, controlled reflections,
neutral seamless background, believable contact shadow and exact product scale.
```

### Environmental fashion portrait

```text
35-50mm behavior from conversational distance, camera near chest height, three-quarter body,
subject placed off-axis with movement into negative space. Window or open-shade key, practical ambient retained,
background one to two stops under face, natural posture and hand action, mild motion or focus imperfection only when motivated.
```

### Phone-candid night image

```text
24-28mm phone-main-camera behavior, arm's-length or friend-held distance, available mixed light,
restrained computational sharpening, limited highlight latitude, plausible ISO noise, imperfect but intentional framing,
one clear social action, background details that support the moment, no fake film damage.
```

## Prompt recipe

Write in priority order because providers may weight earlier content more heavily:

```text
JOB AND SINGLE IDEA
SUBJECT / PRODUCT LOCKS
ACTION AND SOCIAL CONTEXT
COMPOSITION AND CROP
CAMERA BEHAVIOR
LIGHTING GEOMETRY
MATERIAL AND HUMAN REALISM
COLOR AND FINISH
COPY-SAFE AREA
REJECT LIST
```

Black Forest Labs recommends a `Subject + Action + Style + Context` structure and notes that word order matters. For complex production scenes, use labeled sections or structured JSON so variables can be changed independently. Keep the most important subject, lock, and action early.

## QA

Reject when any answer is no:

- Do focal length, camera distance, perspective, and crop agree?
- Does depth of field match aperture intent and required sharp planes?
- Do motion and shutter intent agree?
- Can every highlight, catchlight, and shadow be explained by the light setup?
- Does the background brightness match the stated separation and spill control?
- Do skin, hair, fabric, glass, metal, liquid, and packaging react plausibly?
- Are hands occupied naturally and anatomy mechanically possible?
- Are product scale, gravity, contact, label plane, and reflections consistent?
- Does the image preserve one clear message at thumbnail and every required crop?
- Is any imperfection motivated rather than added as a generic `raw` effect?

## Source notes

Checked 2026-07-22:

- OpenAI Image generation guide: https://developers.openai.com/api/docs/guides/image-generation — generation vs editing workflows, multi-turn high-fidelity edits, and output controls for size, quality, format, and compression.
- Nikon, Understanding Maximum Aperture: https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/understanding-maximum-aperture — aperture, exposure, shutter relationship, and depth of field.
- Nikon, Understanding Focal Length: https://www.nikonusa.com/learn-and-explore/c/tips-and-techniques/understanding-focal-length — angle of view, magnification, and focal-length use cases.
- Black Forest Labs, FLUX.2 Prompting Guide: https://docs.bfl.ai/guides/prompting_guide_flux2 — prompt ordering, length guidance, photorealistic camera references, multi-reference workflows, and structured prompting.

The numeric recipes in this document are production starting points, not claims that an image model reproduces real EXIF or lighting ratios exactly. Inspect rendered outputs and iterate locally.
