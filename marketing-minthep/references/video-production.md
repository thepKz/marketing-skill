# Marketing Video Production

Use this reference for short-form ads, product demos, food videos, creator briefs, campaign films, motion key visuals, and image-to-video plans. Start with the audience decision and proof, not a list of transitions.

## Video brief

Define:

- business job, audience state, one belief change, proof, offer, CTA, and success metric;
- placement, aspect ratio, duration, sound-on/off behavior, safe zones, and deliverable count;
- available footage, product/person references, rights, claims, and edit locks;
- production mode: live action, animation, image-to-video, generative video, screen recording, or hybrid.

## Story spine

Use the smallest useful sequence:

```text
0.0-2.0s: pattern interrupt or immediate outcome
2.0-6.0s: product, problem, or mechanism made legible
6.0-12.0s: proof or demonstration
12.0s+: objection, offer, or CTA as the placement allows
```

This is a planning baseline, not a universal performance claim. Do not hide a weak idea under rapid cuts. A useful demo may be a single uninterrupted take when continuity itself is the proof.

## Shot contract

Every shot needs:

```text
shot ID + duration + narrative job + subject/action + framing/camera height/lens behavior
+ movement vector/speed + lighting continuity + audio/dialogue + on-screen text
+ transition reason + reference/identity/product locks + reject conditions
```

Do not write these one at a time. Write one sequence spec where the `world` holds for the whole
film and each shot declares only what *changes*, then generate the shot list and the per-shot
prompts from it:

```text
python scripts/plan_video_sequence.py --input sequence.json --format prompts
python scripts/plan_video_sequence.py --input sequence.json --format report   # bilingual plan
python scripts/plan_video_sequence.py --input sequence.json --format csv      # 04-shot-list.csv
```

The script carries the state in the next section forward automatically, emits one continuity lock
byte-identical into every shot, and derives each shot's reject list from what that shot locked.
Hand-written shot prompts describe the world afresh each time, and two descriptions of the same
subject become two different subjects: that is why unenforced shot lists come back not joining up.

Keep movement motivated:

- push in to increase attention or reveal detail;
- pull out to reveal context or scale;
- lateral move for parallax, comparison, or process;
- orbit only when product geometry remains truthful;
- locked camera for credibility, instruction, and before/after proof;
- handheld character only when the social context supports it.

For subtle depth, prefer a slow dolly with readable foreground/background parallax over an artificial zoom. Avoid simultaneous camera motion, subject motion, animated typography, and a complex transition unless each has a job.

## Continuity and generative constraints

- Lock product silhouette, label plane, cap/closure, material, color, person identity, wardrobe, handedness, and environment anchors across shots. These go in the spec's `world`.
- Carry screen direction, gaze, hand position, light direction, time of day, prop placement, and material state (steam, condensation, fill level, melt) through adjacent shots. These are the eight keys the sequencer inherits shot to shot; a shot that says nothing about one of them stays locked to it.
- Never reverse screen direction on a straight cut. Crossing the line reads as the subject having turned around, so it needs a cutaway, declared as `"cutaway": true`.
- Prefer short controlled shots for generative video; cut around drift instead of accepting morphing. Drift grows with shot length, so the sequencer refuses a generative shot over five seconds.
- Use first/last frames, reference images, masks, or image-edit passes when the provider supports them.
- Add exact typography, prices, subtitles, disclosures, and logos in the edit unless the provider is verified for exact text.

## Food video

Build appetite through real process and material behavior:

- steam rises and disperses with continuity;
- broth, oil, sauce, noodles, meat, ice, condensation, and garnish obey gravity and temperature;
- utensils displace food correctly and hands have a clear task;
- use macro detail, serving action, and a complete-bowl recognition shot;
- preserve truthful portion and ingredients.

Useful bun bo sequence: broth pour or steam hook -> complete bowl recognition -> noodle/meat lift -> ingredient or cooking proof -> price/location/CTA. Reject duplicated noodles, looping steam, morphing bowls, impossible liquid, or a garnish appearing between cuts.

## Sound and accessibility

- Design for sound-off comprehension with captions and visual proof.
- Use production sound or Foley to reinforce material truth; do not let generic music replace the product mechanism.
- Keep captions inside verified platform safe zones, readable against motion, and synchronized.
- Provide transcript/captions and avoid flashing or motion patterns that create accessibility risk.

## Required outputs

Provide the concept, hook, script, beat sheet, shot list, edit map, per-shot visual prompts, start/end frames, audio plan, on-screen copy, prompt/reference package, thumbnail, cutdowns, ratio-specific recomposition notes, export specs, rights/disclosure notes, and QA checklist. Branch variants by one named axis such as hook, proof order, spokesperson, pacing, offer, or CTA.

Mark generated footage as concept or previsualization unless it was actually rendered and reviewed. Include a fallback still-image treatment when motion generation is unavailable.

## QA

- The product, proof, and CTA remain understandable with sound off.
- Product/person continuity survives every shot.
- Motion, shadows, reflections, liquids, steam, and contact remain physically plausible.
- Exact claims and text are supplied and legally supportable.
- The first frame and poster frame work as still compositions.
- Captions, logos, faces, products, and CTA avoid live UI zones.
- Export frame rate, resolution, codec, audio loudness, captions, and file limits are verified against the live channel specification.
- Each cutdown changes one named hypothesis rather than mixing multiple variables.
