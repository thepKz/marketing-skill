# Virtual Person System

## Contents

- Decision flow
- Option menu
- Face design
- Body presentation
- Douyin makeup
- Identity bible
- Generation sequence
- QA

## Decision flow

Use this system for a recurring fictional model, AI creator, brand face, campaign character, or product demonstrator.

1. Identify the person's job: brand authority, aspirational fashion, relatable creator, product demonstration, storytelling, or entertainment IP.
2. Return three or four option cards before generating when the user has not chosen a direction. Explain the impression, best use, and risk of each.
3. Let the user choose codes for face, body, makeup, and presence, or recommend one combination when asked.
4. Build an identity bible and neutral reference sheet before campaign variations.
5. Generate exploration branches from the same identity anchors. Do not redesign the person in every scene.

Ask at most three material questions:

1. What job should this person perform for the brand?
2. Which overall impression should dominate: approachable, aspirational, cool, romantic, or distinctive?
3. Is the body and makeup preference a lock or only a starting recommendation?

## Option menu

### Face impression

| Code | Direction | Audience impression | Best for | Risk to control |
|---|---|---|---|---|
| `F1` | Soft romantic | Warm, polished, inviting | Beauty, lifestyle, feminine fashion | Becoming generic or doll-like |
| `F2` | Cinematic natural | Calm, intelligent, credible | Skincare, premium lifestyle, storytelling | Becoming visually quiet at thumbnail size |
| `F3` | Cool editorial | Precise, modern, self-possessed | Fashion, technology, high-concept beauty | Feeling distant or over-sculpted |
| `F4` | Distinctive fashion | Memorable, directional, unconventional | Editorial, creator IP, launch concepts | Novelty overwhelming product meaning |

Design attractiveness through coherence, expression, grooming, and image craft rather than one universal facial template. Preserve plausible adult anatomy, natural asymmetry, and distinguishing details.

### Body presentation

| Code | Direction | Visual behavior |
|---|---|---|
| `B1` | Slender light-frame | Long visual lines, narrow healthy frame, light posture, fashion-friendly silhouette |
| `B2` | Balanced natural | Moderate proportions, relaxed posture, broad channel versatility |
| `B3` | Athletic lean | Visible functional tone, grounded stance, energetic action |
| `B4` | Soft curved | Softer line rhythm, grounded presence, fabric and pose-led shape |

For this project's stated preference, recommend `B1` for idol, fashion, or Douyin-led directions unless the product or audience suggests otherwise. Describe it as a healthy adult build. Do not request emaciation, protruding bones, extreme thinness, implausible waist reduction, or a weight number. Never claim one build is inherently more attractive.

### Presence and pose

| Code | Direction | Pose grammar |
|---|---|---|
| `P1` | Gentle approachable | Relaxed shoulders, slight chin drop, soft gaze, natural hand task |
| `P2` | Quiet luxury | Three-quarter face, gaze off camera, restrained movement, long posture |
| `P3` | Direct idol | Camera-aware gaze, precise face framing, polished hand and hair placement |
| `P4` | Editorial geometry | Strong shoulder line, extended neck, deliberate negative space, angular crop |

### Makeup

Use the complete contract in `makeup-art-direction.md`.

| Code | Lane |
|---|---|
| `M1` | Fresh luminous |
| `M2` | Quiet luxury |
| `M3` | Douyin luminous |
| `M4` | Cool crystalline |
| `M5` | Sculpted feline |
| `M6` | Smoky grunge |
| `M7` | Graphic editorial |

## Face design

Lock facial identity with concrete, non-celebrity anchors:

- Overall face shape and cheek structure.
- Forehead and hairline behavior.
- Eye spacing, lid type, canthal direction, iris color, and natural asymmetry.
- Brow baseline and density without makeup.
- Nose bridge, width, tip, and nostril geometry.
- Lip proportions, cupid's bow, resting closure, and natural asymmetry.
- Jaw and chin shape without extreme narrowing.
- Ear visibility, moles, freckles, or other original distinguishing marks.
- Neutral expression and smile behavior.

Do not create a face by averaging named celebrities. Translate references into separate non-identifying traits and add at least one original distinguishing anchor.

## Body presentation

Lock body identity separately from styling:

- Adult height impression, shoulder width, torso-to-leg rhythm, and frame category.
- Postural habits, center of gravity, hand scale, and gesture style.
- Healthy anatomy and believable joint range.
- Garment fit, fabric pressure, and footwear behavior.

Camera angle and wardrobe can change apparent proportions. Do not encode lens distortion as permanent anatomy.

## Douyin makeup

Treat `Douyin` as a makeup and capture grammar, not an ethnicity or identity instruction.

### M3 / Douyin luminous contract

- `skin_finish`: translucent satin-luminous base with controlled cheek and nose highlights; retain pores and tonal variation.
- `brows`: softly straight or shallow arch, diffused front, clean tail.
- `eyeshadow`: peach, rose-beige, taupe, or champagne wash with concentrated upper-lid and inner-corner light.
- `aegyo_sal`: create a narrow lower-lid highlight over a soft shadow that follows the actual orbicularis/under-eye curve; keep both sides plausible and expression-aware.
- `liner_lashes`: fine brown or black tightline, short horizontal/puppy or delicate lifted wing, separated upper clusters, optional restrained lower-lash accents.
- `cheeks`: translucent blush high and slightly central or softly under-eye; do not cover the entire mid-face.
- `structure`: restrained nose and cheek contour; small pearl highlight rather than a painted white stripe.
- `lips`: blurred gradient tint, syrup gloss, or lacquer center with believable source-shaped reflection.
- `capture`: frontal or three-quarter beauty crop, soft large key, controlled fill, crisp iris and lash detail, clean pastel or dark polished grade.

Reject oversized generated eyes, painted under-eye bags, white crescent stickers, duplicated lower lashes, poreless skin, pinched nose, extreme V-line jaw, or childlike age presentation.

## Identity bible

Create:

1. One canonical written profile with selected codes.
2. Neutral head reference: front, left three-quarter, right three-quarter, and profile.
3. Neutral full-body reference with simple fitted clothing and undistorted camera distance.
4. Expression sheet: neutral, small smile, focused, surprised, and campaign-specific expression.
5. Makeup-off or minimal baseline when makeup will vary across campaigns.
6. Lock list, freedom list, and reject list.

Record which traits are biological identity, grooming, makeup, wardrobe, camera, or temporary styling. Only biological identity remains fixed across all campaigns.

## Generation sequence

1. Run `scripts/plan_virtual_person.py` to return options and a recommendation.
2. Confirm or safely infer the selected codes.
3. Generate the neutral identity sheet before high-styling campaign images.
4. Use Nano Banana 2 when multiple identity views and consistency dominate. Use GPT Image 2 Responses when conversational iteration is the main workflow.
5. Branch four campaign variants from the same identity sheet and canonical profile.
6. Refine only the selected branch.

## QA

Reject when:

- The person resembles a named public figure strongly enough to imply copying or endorsement.
- Facial anchors drift between angles, makeup lanes, or scenes.
- Slender presentation becomes unhealthy, anatomically impossible, or childlike.
- Makeup changes eye, nose, jaw, or lip anatomy instead of sitting on it.
- Aegyo-sal becomes a painted pouch, duplicate eyelid, or mismatched shadow.
- Full-body perspective contradicts the identity sheet.
- The person is attractive only through pore erasure, extreme symmetry, or generic beauty-filter traits.
