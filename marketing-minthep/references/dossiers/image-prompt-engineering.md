# Prompt Engineering for Image Models — Deep Reference Dossier

## What this is for

You are not a marketer and not an ML engineer, but you have to make an image model produce a
specific picture — a menu hero shot, a Facebook ad frame, a product photo where the packaging must
stay legally identical, a poster with the words **Bún bò Huế** spelled correctly. This dossier is
the operational manual: how prompts are actually parsed and ordered, when to describe a *subject*
versus a *photograph*, what each reference image slot really does, how to lock a product across
edits, where negative prompting exists and where it is a myth, how to get rendered text right, how
to control aspect ratio and seed, how to iterate without losing your mind, and what each classic
failure mode looks like plus the fix. Every factual claim carries an evidence marker. Where I could
not verify against live documentation, I say so rather than inventing a parameter.

---

## Evidence key (read this first)

| Marker | Meaning |
|---|---|
| `[verified]` | I fetched and read the page. URL + retrieval date given inline. |
| `[search-level]` | I only saw a search-result summary, not the page body. Re-check before betting money on it. |
| `[craft]` | Model-agnostic practitioner craft. Not a documented API behaviour; it is a technique that survives model changes. Falsifiable by your own A/B, and you should run that A/B. |
| `[illustrative]` | A number invented so arithmetic is followable. **Not real.** Never quote it outward. |
| `[UNVERIFIED - x]` | A named gap. `x` says exactly what would close it. |

Retrieval date for everything below: **2026-07-29**. Image-model docs churn faster than almost any
other API surface. Treat every parameter name as perishable: verify before you ship code.

### Standing warning about model names and parameters

This dossier names a model or parameter **only** where I read it on a live doc page in this session.
Anywhere a version string or parameter would be useful but I did not read it, you get
`[UNVERIFIED - needs live doc check]`. If you copy a parameter from here into production code
without checking the current provider reference, you will eventually send a request that 400s or,
worse, silently ignores the field. Silent ignore is the dangerous one — the image still comes back,
just not the image you asked for.

---

## Part 0 — The one-paragraph mental model

An image model is a conditional sampler. It draws from a distribution of plausible images and the
prompt is a *bias*, not a *command*. Everything in this dossier is a way of making the bias sharper:
adding constraints the model can actually represent, removing ambiguity that lets the sampler
wander, and pinning the random parts (seed, references) so that when you change one word you can
see what that word did. Two consequences you must internalise:

1. **A prompt is a budget, not a wish list.** Attention is finite. Every clause you add dilutes the
   others. Ideogram's own troubleshooting guidance for "the AI ignores important parts of my prompt"
   is to place key details early, repeat them with emphasis, and keep prompts under roughly 150
   words `[verified]` (source: https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/8-troubleshooting.md,
   retrieved 2026-07-29). If you ignore this, you get the "I asked for nine things and got four"
   failure, and you will not know which four because you changed nine variables at once.
2. **You cannot debug what you cannot hold still.** Without seed control or a fixed reference image,
   two renders of the same prompt differ for reasons that have nothing to do with your edit. Every
   "this prompt word does nothing" conclusion drawn without a held seed is unsound `[craft]`.

---

## Part 1 — Prompt structure and what ordering does

### 1.1 The documented consensus structure

Three independent vendor docs converge on a subject-first, context-and-style-after skeleton. This is
the strongest cross-provider signal in the whole dossier.

| Source | Documented structure | Evidence |
|---|---|---|
| Google Imagen prompt guide | Three core elements: **Subject** (the primary object), **Context and background**, **Style**. Max prompt length **480 tokens**. | `[verified]` (source: https://ai.google.dev/gemini-api/docs/imagen, retrieved 2026-07-29) |
| Black Forest Labs FLUX.2 prompting guide | **"Subject + Action + Style + Context"**, with priority sequence: main subject → key action → critical style → essential context → secondary details. | `[verified]` (source: https://docs.bfl.ml/guides/prompting_guide_flux2, retrieved 2026-07-29) |
| Hugging Face Diffusers prompting doc | "Every effective prompt needs three core elements: Subject … Style … Context". And: **"Use these elements as a structured narrative, not a keyword list. Modern models understand language better than keyword matching."** | `[verified]` (source: https://huggingface.co/docs/diffusers/en/using-diffusers/weighted_prompts, retrieved 2026-07-29) |
| OpenAI cookbook image-gen prompting guide | A different and more production-shaped order: **"background/scene → subject → key details → constraints"**, plus "include the intended use (ad, UI mock, infographic) to set the 'mode'" and "use short labeled segments or line breaks instead of one long paragraph". | `[verified]` (source: https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/multimodal/image-gen-1.5-prompting_guide.ipynb, retrieved 2026-07-29) |

Note the genuine disagreement: BFL says subject first because **"Word order matters - FLUX.2 pays
more attention to what comes first"** `[verified]`, while the OpenAI cookbook puts scene before
subject. Do not average them. **Decision rule:** use the structure documented by the provider you
are actually calling; if the provider documents none, use subject-first `[craft]`. The reason
subject-first is the safer default when unknown is that early tokens are the ones least likely to be
dropped under attention dilution, and a scene without the right subject is a total loss whereas a
subject in a slightly wrong scene is salvageable by one edit.

### 1.2 The seven-slot prompt skeleton (model-agnostic)

Use this as a fill-in form. Slots you leave blank get filled by the model's priors — which is
sometimes what you want (blank *style* on a photo request usually yields generic stock-photo
lighting) and sometimes catastrophic (blank *framing* on a portrait request is the #1 cause of
"my subject got cropped").

```
1. MODE / INTENT      what artefact is this  →  "product photograph for an e-commerce hero"
2. SUBJECT            the one thing that must exist  →  "a bowl of bún bò Huế"
3. SUBJECT DETAIL     material, colour, state, count  →  "beef shank slices, chả lụa, one thick
                      round rice noodle bundle, chilli oil surface sheen"
4. SCENE / CONTEXT    where and when  →  "dark walnut table, morning side light, Huế street stall
                      in soft background blur"
5. RENDERING SPEC     photographic OR illustrative spec (Part 2)  →  "50mm, f/2.0, single large
                      softbox from camera left, no fill"
6. COMPOSITION        framing, crop, subject placement, negative space  →  "three-quarter overhead,
                      bowl centred, 25% clear space at top for a headline"
7. CONSTRAINTS        exclusions and invariants  →  "no visible logos, no on-image text, no hands"
```

Slot 1 is the highest-leverage and most-skipped. The cookbook is explicit that stating intended use
"sets the mode" `[verified]`. Mechanically, "product photograph for e-commerce" pulls the whole
sample toward a cluster of images with clean backgrounds, even lighting and centred subjects;
without it your bowl of bún bò may arrive as a moody restaurant-review photo. What breaks if you
skip it: you will spend three iterations fixing background clutter that one word would have
prevented.

Slot 7 is second-highest leverage and also skipped. The cookbook says to **"State exclusions and
invariants explicitly"** such as **"'no watermark,' 'no extra text,' 'no logos/trademarks'"**
`[verified]`. See Part 4 for why this works on instruction-following models even when there is no
negative-prompt field.

### 1.3 Labeled segments beat one long sentence

For any prompt over roughly 40 words, break it into labeled lines. The cookbook says exactly this:
**"use short labeled segments or line breaks instead of one long paragraph"** `[verified]`.

```
Scene: hotel breakfast buffet, 7am, warm window light from the left.
Subject: a single white ceramic bowl of bún bò Huế on a bamboo tray.
Details: 4 slices of beef shank, 2 rounds of chả lụa, one lime wedge, a small pile of
  shredded banana blossom. Broth is deep red-orange with a thin chilli-oil sheen.
Camera: 50mm equivalent, f/2.8, three-quarter high angle, shallow depth of field.
Light: one large softbox camera left, white bounce card right, no hard specular hits.
Composition: bowl slightly right of centre, 30% empty space upper left.
Constraints: no text, no logos, no hands, no chopsticks crossing the bowl rim.
```

Why this wins `[craft]`: it makes *your own* one-variable iteration mechanical. You can change the
`Light:` line and diff the outputs. With a single run-on sentence you cannot even reliably find the
clause you edited, and you will accidentally change two things.

Cost: on some diffusion-family models, labeled/structured text is itself a style signal and can
nudge output toward graphic-design-looking images `[UNVERIFIED - needs a controlled A/B on your
target model: same content, labeled vs. prose, 8 seeds each]`.

### 1.4 What ordering actually does, mechanically

Three separate effects hide under "order matters". Distinguishing them tells you which fix to reach
for.

| Effect | Symptom | Underlying cause | Fix |
|---|---|---|---|
| **Positional salience** | Later clauses silently dropped. | Early tokens get more effective attention; documented for FLUX.2 as "pays more attention to what comes first" `[verified]` (bfl.ml, 2026-07-29), and Ideogram's fix for ignored prompt content is "placing key details early" `[verified]` (ideogram troubleshooting, 2026-07-29). | Move the must-have to the front. Shorten the tail. |
| **Adjacency binding** | "red bowl, white noodles" comes back as white bowl, red noodles. | Attribute-to-noun binding is learned from proximity and syntax, and it is a documented failure mode of diffusion text conditioning (see Part 8.2). | Keep each attribute physically adjacent to its noun; give each object its own clause/sentence. |
| **Style dominance** | One aesthetic word ("anime", "cinematic") repaints the entire image including things you specified concretely. | Global style tokens condition the whole latent, not a region. | Put style *last*, keep it to one or two words, and if it still bleeds, move it into a reference image instead (Part 3). |

**Threshold rule `[craft]`:** if a prompt has more than ~5 distinct objects that each need their own
attribute, stop prompting and start compositing. Generate elements separately, or use a composition
reference / layout control. Past five bound attributes, per-object accuracy degrades fast enough
that you will spend more iterations than a composite would have cost. (I do not have a published
accuracy-vs-object-count curve to cite: `[UNVERIFIED - needs a citable compositional benchmark such
as a T2I-CompBench-style result read from source]`.)

### 1.5 Length: how much prompt is too much

| Length band | Use when | Evidence |
|---|---|---|
| 10–30 words | Concept exploration, "show me the space of possibilities" | `[verified]` BFL FLUX.2 guide labels this "quick concept exploration" (docs.bfl.ml, 2026-07-29) |
| 30–80 words | Most production work | `[verified]` BFL: "Usually ideal for most projects" |
| 80+ words | Complex scenes with hard specs | `[verified]` BFL: "Complex scenes requiring detailed specs" |
| Hard ceiling ~150 words | Ideogram's stated remedy for prompt neglect includes "keeping prompts under approximately 150 words" `[verified]` (ideogram troubleshooting, 2026-07-29) |
| Hard ceiling 480 tokens | Imagen documented max prompt length `[verified]` (ai.google.dev/gemini-api/docs/imagen, 2026-07-29) |

The classic legacy constraint — the 77-token CLIP text-encoder window on older Stable Diffusion
lineages, and the chunking tricks used to exceed it — is real in practitioner lore but I did not
read a page stating it in this session: `[UNVERIFIED - needs the CLIP/diffusers tokenizer limit
confirmed from a live diffusers or CLIP doc page]`. Treat "my prompt is 300 words and the last third
does nothing" as plausible on older open-weight pipelines and test it with a canary word (put
"a single yellow rubber duck" at the very end; if the duck never appears, your tail is being
truncated or starved) `[craft]`.

The OpenAI cookbook takes the opposite tack on length and it is worth quoting the operational
consequence: long prompts can work, but **"Start with a clean base prompt, then refine with small,
single-change follow-ups"** `[verified]`. In other words, long prompts are a *destination*, not a
*starting point*.

### 1.6 Prompt weighting: exists, but narrower than people think

Explicit numeric weighting is an open-weights / community-tooling feature, not a universal one.

| Syntax | Multiplier | Where |
|---|---|---|
| `(cat)` | increase by 1.1x | `[verified]` Diffusers prompting doc table (huggingface.co/docs/diffusers/en/using-diffusers/weighted_prompts, retrieved 2026-07-29) |
| `((cat))` | increase by 1.21x | `[verified]` same |
| `(cat:1.5)` | increase by 1.5x | `[verified]` same |
| `(cat:0.5)` | decrease by 4x | `[verified]` same — note the asymmetry, this is what the table says |

Implementation detail that matters: in Diffusers this is not a prompt-string feature, it is done by
passing scaled embeddings — "Diffusers handles this through `prompt_embeds` and
`pooled_prompt_embeds` arguments which take scaled text embedding vectors", generated with the
`sd_embed` library, which "only supports Stable Diffusion, Stable Diffusion XL, Stable Diffusion 3,
Stable Cascade, and Flux" `[verified]` (same page). And the load-bearing caveat: **"Prompt weighting
doesn't necessarily help for newer models like Flux which already has very good prompt adherence"**
`[verified]`.

**Decision rule:** if you are typing `(word:1.3)` into a hosted, instruction-following image
endpoint, you are probably typing literal parentheses into a caption and the model may render them
or ignore them. Weighting is for open-weight pipelines you control. On hosted models, get emphasis
by (a) moving the concept earlier, (b) restating it in a second, more concrete clause, (c) removing
competing detail. Ideogram's documented remedy for ignored content is exactly "repeating them with
emphasis" in natural language `[verified]`.

Midjourney has a separate documented weighting syntax using `::` with numeric weights, including
negative weights, and a rule that total weight must remain positive `[search-level]` (search summary
citing https://docs.midjourney.com/hc/en-us/articles/32658968492557-Multi-Prompts-Weights; the page
itself returned HTTP 403 to my fetch, so treat syntax details as unconfirmed — `[UNVERIFIED - needs
the Midjourney Multi-Prompts & Weights page read directly, e.g. from a logged-in browser]`).

---

## Part 2 — Describing a subject vs. describing a photograph

This is the single distinction that most separates people whose images look intentional from people
whose images look like AI images.

### 2.1 The two modes

**Subject description** answers *what exists*: "a bowl of bún bò Huế with beef shank and chả lụa".
**Photograph description** answers *what instrument recorded it and under what light*: "shot on a
50mm lens at f/2.0, single softbox camera left, slight underexposure, fine film grain".

The model treats both as conditioning, but they act on different axes. Subject terms determine
content and are where binding errors happen. Photographic terms determine the *rendering* — depth of
field, falloff, contrast curve, grain, colour response — and they are far more reliable per token
because they correlate with enormous, consistently-captioned regions of the training distribution
(stock and Flickr EXIF-style captions).

The cookbook states the practical consequence bluntly: **"camera/composition terms (lens, aperture
feel, lighting) often steer realism more reliably than generic '8K/ultra-detailed.'"** `[verified]`
(openai-cookbook image-gen prompting guide, retrieved 2026-07-29).

Google's Imagen prompt guide documents an entire photographic modifier vocabulary as first-class:
Camera Proximity (close-up, zoomed out), Camera Position (aerial, from below), Lighting (natural,
dramatic, warm, cold), Camera Settings (motion blur, soft focus, bokeh), Lens types (35mm, 50mm,
fisheye, wide angle, macro), and Film types (black and white, polaroid) `[verified]` (source:
https://ai.google.dev/gemini-api/docs/imagen, retrieved 2026-07-29). Gemini's image-generation guide
gives a photorealism template of the same shape: **"A photorealistic [type of shot] of a [subject
description] in a [setting description]…"** and lists "Control the camera" (angle, lens type,
perspective) among its core best practices `[verified]` (source:
https://ai.google.dev/gemini-api/docs/image-generation, retrieved 2026-07-29).

### 2.2 When to use which — decision table

| Situation | Lead with | Why | What breaks if you get it wrong |
|---|---|---|---|
| Photoreal product / food hero | Photograph mode, heavy | Realism comes from optics and light, not adjectives | Prompting "hyper realistic, 8K, award winning" gives glossy plastic-looking CGI food |
| Illustration, icon, flat graphic | Subject + medium mode | Camera terms are meaningless in a vector illustration and inject fake depth of field | You get a *photo of an illustration*, with lens blur on flat art |
| Editorial / lifestyle scene | Both, photograph mode last | Need content control *and* a consistent look across a set | Set looks like it came from five different photographers |
| Text-heavy poster / packaging | Subject + layout + typography mode; camera terms minimal | Depth of field is the enemy of legible text | Blurred, unreadable headline |
| Anything that must match an existing brand look | Reference image for look, prompt for content (Part 3) | Words cannot specify a brand's exact colour grade | Style drifts every render; set is unusable |
| Diagram, infographic, UI mock | Mode/intent + layout, zero camera | Camera language pulls toward photography | Perspective distortion on what should be flat |

### 2.3 The photographic spec, slot by slot

Give one value per axis. Two values on one axis (e.g. "macro wide-angle") fight and you get mush.

| Axis | Vocabulary that works | Effect on the image | Watch out |
|---|---|---|---|
| Focal length | 24mm / 35mm / 50mm / 85mm / 135mm; macro; fisheye `[verified]` as documented Imagen lens types | Perspective compression and apparent subject-to-background relationship. Wide = context and distortion; long = isolation and flattening | Wide-angle on faces distorts noses; models reproduce this faithfully |
| Aperture / DOF | f/1.4, f/2, f/8, f/16; "shallow depth of field"; "deep focus"; "bokeh" `[verified]` Imagen lists bokeh/soft focus as camera settings | How much of the frame is sharp | Wide apertures destroy rendered text and fine product detail |
| Camera position | eye level / low angle / from below / aerial / overhead / three-quarter overhead `[verified]` Imagen documents aerial and from-below | Power, scale, and how much of the surface you see | Food usually wants 30–45° or straight overhead; eye level on a bowl shows you the rim and nothing else `[craft]` |
| Shot size | extreme close-up / close-up / medium / full body / wide `[verified]` Ideogram's documented fix for cropping is explicit framing language such as "full body" | Crop safety | Omitting this is the main cause of cropped subjects |
| Light: quality | soft / hard; large softbox / bare bulb / overcast / direct midday sun | Shadow edge transition | "Soft light" plus "dramatic shadows" is contradictory; pick one |
| Light: direction | from camera left / backlit / rim light / top-down / window light from the right | Shape and mood | Backlight plus "clean product shot" fights; backlit steam for pho/bún bò is the exception where it is right |
| Light: colour | warm 3200K tungsten / neutral / cool blue shade / mixed | Grade | Mixed colour temp reads as "amateur phone photo" — useful if that is the brief |
| Film / medium | black and white; polaroid `[verified]` Imagen documented film types; colour negative; slide film; instant film | Grain, contrast curve, colour cast | Naming a specific commercial film stock is a real technique but stock-specific claims here would be fabrication: `[UNVERIFIED - needs a doc or controlled test showing your target model responds to named stocks]` |
| Post / artefacts | slight vignette, fine grain, no HDR look, natural skin texture | Prevents the over-processed look | "No HDR" is a negative statement — see Part 4 for whether that lands |

### 2.4 Worked contrast — same subject, three specs

Base subject, held constant: *a bowl of bún bò Huế on a dark wood table*.

**A. Subject only.**
```
A bowl of bún bò Huế on a dark wood table.
```
Expected: competent, generic, centre-lit, ambiguous mood, unpredictable framing. Fine for a
thumbnail, unusable as a set `[craft]`.

**B. Subject + photograph mode (documentary / editorial).**
```
Editorial food photograph. A bowl of bún bò Huế on a dark wood table, Huế street stall.
50mm, f/2.0, eye-level three-quarter angle, natural window light from camera left, deep
shadows on the right, warm tungsten spill in the background, fine film grain, slight
vignette, natural steam.
```
Expected: coherent single-photographer look, repeatable across dishes by swapping only the subject
line.

**C. Subject + photograph mode (commercial / catalogue).**
```
Studio product photograph for a menu. A bowl of bún bò Huế, centred, on a seamless dark
walnut surface. 85mm, f/8, 30-degree high angle, one large softbox directly above and
slightly behind, white bounce card in front, no hard speculars, even exposure, no grain.
Composition: bowl centred, 30% clear space at top.
```
Expected: clean, flat-lit, crop-safe, headline-ready. Boring on purpose. This is what a menu needs.

The lesson `[craft]`: B and C differ in *zero* subject words. If you find yourself changing the
subject line to fix the mood, you have diagnosed the wrong slot.

### 2.5 The anti-pattern list

| Anti-pattern | Why it fails | Replace with |
|---|---|---|
| "8K, ultra detailed, hyperrealistic, masterpiece, award winning" | Quality-token stacking correlates with over-processed CGI-ish training images, not with real photographs. The cookbook explicitly prefers camera/composition terms over generic "8K/ultra-detailed" `[verified]` | One medium word + a real optical spec |
| "professional photography" | Means nothing; every axis left blank | Name the lighting setup |
| Naming a living photographer to borrow their look | Style-by-artist-name is unreliable, frequently blocked, and an IP/ethics problem for commercial work. Provider policies vary and I have not read them here: `[UNVERIFIED - needs the specific provider's content/IP policy read live]` | Describe the optical properties, or use a style reference image you own |
| Camera terms on flat illustration | Injects fake depth of field | "flat vector", "no gradients", "even line weight" |
| Two lens specs in one prompt | Contradiction | One focal length |

---

## Part 3 — Reference images: four distinct roles

"Attach an image" is not one feature. There are at least four semantically different jobs, and
providers expose them very differently. Mixing them up is the most expensive mistake in this
dossier, because it wastes whole batches.

### 3.1 The four roles

| Role | What is copied | What is free to change | Typical use |
|---|---|---|---|
| **Composition / structure** | Layout, outline, depth, pose, where things sit in frame | Colour, material, style, identity, content | Re-shoot an approved layout with a new dish; storyboard-to-final |
| **Style** | Colour palette, tone, texture, lighting mood, medium | Subject, layout, identity | Make 20 posts look like one campaign |
| **Identity / character** | A specific person's or character's face and features | Pose, outfit, scene, lighting | Same mascot across a series |
| **Product lock (asset fidelity)** | An exact object, including label typography, logo geometry, proportions | Background, lighting, camera, surrounding scene | Recontextualising real SKU packaging |

Adobe Firefly exposes the first two as separate API objects. Structure is a `structure` parameter
containing `strength` plus an `imageReference`, where structure means "Apply structural
characteristics (like image outline and depth) to newly generated images", and `strength` is "A value
between 1 and 100 that determines how closely the generated image resembles the reference image",
default 50 `[verified]` (source: https://developer.adobe.com/firefly-services/docs/firefly-api/guides/concepts/structure-image-reference/,
retrieved 2026-07-29). Style reference is a parallel `style` object with nested `imageReference` /
`source` / `uploadId`, `strength` between 1 and 100, default 50, guiding "the look and feel of
generated image variations" through "specific styles, colors, artistic methods, or mood"
`[verified]` (source: https://developer.adobe.com/firefly-services/docs/firefly-api/guides/concepts/style-image-reference/,
retrieved 2026-07-29). The two can be combined; the docs describe them together as giving "more
control of image generation beyond the text prompt" `[verified]`.

That page did **not** document what style reference deliberately excludes `[verified]` — the fetch
returned no such statement — so if you need to know whether style reference will drag composition
along with it, test it, do not assume: `[UNVERIFIED - needs a controlled test: same prompt, same
seed, one style ref, strengths 20/50/80]`.

### 3.2 Providers that fold all roles into "just images + words"

Some providers give you no role slots; you declare the role in prose. More flexible, much easier to
get wrong.

- OpenAI's image edits endpoint accepts one or more reference images plus a prompt and supports
  masked inpainting and outpainting; if a mask is provided it applies to the first image only
  `[verified]` (source: https://developers.openai.com/api/docs/guides/image-generation, retrieved
  2026-07-29). The prompting guidance is to "Reference each input by index and description
  ('Image 1: product photo... Image 2: style reference...')" and to "describe how they interact
  ('apply Image 2's style to Image 1')" `[verified]` (source:
  https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/multimodal/image-gen-1.5-prompting_guide.ipynb,
  retrieved 2026-07-29).
- BFL's FLUX.2 guide: up to 8 reference images at 1MP output on the pro tier, capacity decreasing as
  output resolution rises, and users should "clearly describe the role of each" input `[verified]`
  (source: https://docs.bfl.ml/guides/prompting_guide_flux2, retrieved 2026-07-29).
- Gemini's image-generation doc describes conversational editing and "semantic masking" to change one
  element while preserving the rest, with per-model reference budgets — as retrieved: up to 10 object
  images and up to 4 character images on one tier, and up to 6 object / 5 character / 3 style
  reference images on another `[verified]` (source: https://ai.google.dev/gemini-api/docs/image-generation,
  retrieved 2026-07-29). That style reference is counted *separately* from objects and characters is
  the tell: the model is being told roles, and role budgets are finite.

**Rule:** if the API has role slots, use them — prose role declarations are weaker than a typed
parameter. If it does not, index and label every image in the first two lines of the prompt, before
the scene description `[craft]`. Unlabeled multi-image input is the number-one cause of "why did it
paste my product's colour onto the background".

### 3.3 The labeling pattern that works

```
Image 1 = PRODUCT. Reproduce exactly: shape, proportions, label artwork, all label text,
  logo geometry, cap colour. Do not redraw, restyle, or re-letter anything on Image 1.
Image 2 = COMPOSITION. Use only the layout: subject position, camera angle, horizon line,
  and the empty area on the right. Ignore its colours, its lighting and its subject.
Image 3 = STYLE. Use only colour palette, contrast and light quality. Ignore its subject
  and its layout.

Task: place the Image 1 product into the composition of Image 2, graded like Image 3.
Change only the background and lighting. Keep the product identical to Image 1.
```

Every line does work. Naming what to *ignore* in each reference is what prevents the classic
style-reference-ate-my-layout failure `[craft]`.

### 3.4 Product lock: keeping a product unchanged across edits

The hardest reliability problem in commercial image work, because "close enough" is not acceptable —
a re-lettered label is a factually false product image, and depending on jurisdiction and claim type
that is a regulatory problem, not an aesthetic one `[UNVERIFIED - needs the specific
advertising-standards or labelling regulation for your market read live; nobody should quote a rule
from this document]`.

**The protocol, in order:**

1. **Never let the model redraw the product if you can composite it instead.** The most reliable
   product lock is not a prompt technique: generate the *environment* with the model, then place the
   real, unmodified product cut-out on top in an image editor. Zero drift by construction. Use
   generative tools only for shadow and reflection matching `[craft]`. If a stakeholder wants "AI did
   the whole thing", they need it right more than they need it pure.
2. **If the model must hold the product, use masked editing so product pixels sit outside the
   editable region.** OpenAI's edits endpoint supports partial edits with masks; input image and mask
   must match in format and size (under 50MB) and the mask requires an alpha channel `[verified]`
   (developers.openai.com image-generation guide, retrieved 2026-07-29). Then read the caveat:
   "Masking with GPT Image is entirely prompt-based. The model uses the mask as guidance, but may not
   follow its exact shape with complete precision." `[verified]` (same page). That sentence is the
   whole reason step 1 exists. A mask is a strong hint, not a hard clip. If your requirement is
   "these pixels must be byte-identical", a soft mask does not meet it.
3. **Use a dedicated product-recontextualisation feature if the provider has one.** Google documents
   an Imagen product-recontext API surface `[search-level]` (search summary referencing
   https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/imagen-product-recontext-api;
   my fetch of that URL returned only navigation chrome, so parameter names, how many product
   reference images it accepts, and any preservation guarantee are `[UNVERIFIED - needs that page
   fetched successfully or read in a browser]`). Do not code against it from this dossier.
4. **Maximise input fidelity.** OpenAI exposes an `input_fidelity` parameter that "controls how
   strongly a model preserves details from input images during edits and reference-image workflows",
   and for the model named on the page as `gpt-image-2` the parameter should be omitted because the
   model "processes every image input at high fidelity automatically" `[verified]`
   (developers.openai.com image-generation guide, retrieved 2026-07-29). Practical consequence:
   whether you set this depends on which model you call — read the current page before shipping. The
   cookbook notes higher fidelity helps preserve identity during substantial scene changes
   `[verified]`.
5. **Write the invariant list explicitly, every single turn.** The cookbook's rule: for edits, use
   "'change only X' + 'keep everything else the same'", and "repeat the preserve list on each
   iteration to reduce drift" `[verified]`. Gemini's doc phrases the same move as "Keep everything
   else in the image exactly the same, preserving the original style, lighting, and composition."
   `[verified]` (ai.google.dev image-generation, retrieved 2026-07-29). Drop the preserve list on
   turn 4 because "it already knows" and the label drifts on turn 4.
6. **Cap the chain length.** Each generative edit re-encodes the whole image; drift compounds
   silently. **Rule of thumb `[craft]`: no more than 3–4 generative edits from an original before you
   go back to the original and redo the edit as one combined instruction.** Ignore this and the
   failure is invisible turn-to-turn, obvious when you put turn 1 and turn 8 side by side.
7. **Verify at pixel level, not by vibe.** Zoom to 100% on every piece of label text and every logo
   edge; diff against the source. A check at fit-to-screen zoom will not catch a re-lettered
   diacritic — and in Vietnamese that is exactly where it bites: **Bún bò Huế** losing the dấu sắc on
   *Huế*, or **chả lụa** coming back as *cha lua*, is a wrong product name, not a typo `[craft]`.

**Product-lock QA checklist (run before anything leaves the building):**

- [ ] Every glyph on the packaging matches the source, including diacritics, at 100% zoom.
- [ ] Logo proportions and negative space unchanged (overlay the source at 50% opacity).
- [ ] Brand colours within tolerance (sample the hex; a few points of drift is visible in print).
- [ ] Product geometry unchanged — no invented curves, no extra seams, no changed cap height.
- [ ] Nutrition/legal panels either fully legible and correct, or deliberately out of frame / out of
      focus. Half-legible garbled legal text is the worst outcome.
- [ ] Shadows and reflections physically consistent with the stated light direction.
- [ ] No second, hallucinated copy of the product in the background.
- [ ] Provenance/watermarking implications understood (see 6.5).

### 3.5 Identity vs. product lock — they fail differently

Identity (a face) tolerates variation: a person can be lit differently and still read as that person,
and viewers forgive a lot. Product lock tolerates almost none, because the label is *typography*, and
typography is the exact thing image models are worst at (Part 5).

**Rule:** never use the same mechanism for both. Faces → identity/character reference slots and
consistency features. Labels → masks and compositing, plus glyph-level QA `[craft]`.

Where the provider documents a character-consistency budget, respect it: Gemini's page as retrieved
allows "up to 4 images of characters to maintain character consistency" on one tier `[verified]`
(ai.google.dev image-generation, retrieved 2026-07-29). More references of the same character
generally help up to the budget; beyond it, extras are ignored or crowd out other roles.

### 3.6 The open-weights control stack (self-hosting teams)

Structure / style / identity roles map onto named community mechanisms — depth and edge conditioning,
image-prompt adapters, subject fine-tuning. These are real and widely used, but I did not fetch their
documentation in this session and will not name versions or parameter values from memory:
`[UNVERIFIED - needs the conditioning / adapter / fine-tuning docs for your specific stack read
live]`. The role taxonomy in 3.1 still applies; only the parameter names change.

---

## Part 4 — Negative prompting: where it exists, where it does not, and what to do instead

### 4.1 Two completely different things share one name

1. **A negative-prompt *parameter*.** A separate conditioning input. On classifier-free-guidance
   diffusion pipelines this is the unconditional branch: the sampler is pushed *away* from it at every
   step. It is a real, mechanical steering force.
2. **A negation *sentence* in the main prompt** ("no people", "without text"). On an
   instruction-following image model this is an instruction the model may honour. On a
   bag-of-concepts diffusion text encoder it is often read as *inclusion* — the tokens "people" and
   "text" are in the conditioning either way.

Confusing these is why people say "negative prompts don't work" and other people say "they're
essential". Both are right about different systems.

### 4.2 Verified support matrix

| Provider surface | Negative-prompt parameter? | Evidence |
|---|---|---|
| Stability, Stable Image Core via Amazon Bedrock | **Yes.** `negative_prompt` — "Keywords of what you do not wish to see in the output image. Max: 10.000 characters." | `[verified]` (source: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-diffusion-stable-image-core-text-image-request-response.html, retrieved 2026-07-29) |
| Google Imagen on Vertex AI | **Yes, but legacy.** `negativePrompt` is supported on `imagen-3.0-generate-001`, `imagen-3.0-fast-generate-001`, `imagen-3.0-capability-001`, and the doc states: "Negative prompts are a legacy feature, and are not included with the Imagen models starting with `imagen-3.0-generate-002` and newer." | `[verified]` (source: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/omit-content-using-a-negative-prompt, retrieved 2026-07-29) |
| Google Imagen via the Gemini API docs page | **Not mentioned** anywhere on the parameter list I read (aspectRatio, numberOfImages, imageSize, personGeneration were all documented; negativePrompt and seed were not). | `[verified]` (source: https://ai.google.dev/gemini-api/docs/imagen, retrieved 2026-07-29) |
| Gemini image generation | **No parameter.** Not mentioned as supported. The docs instead list "semantic negative prompts" as a *prompting* best practice — i.e. express exclusions in natural language. | `[verified]` (source: https://ai.google.dev/gemini-api/docs/image-generation, retrieved 2026-07-29) |
| OpenAI image generation / edits | **No.** "No negative prompt parameter exists in this documentation." | `[verified]` (source: https://developers.openai.com/api/docs/guides/image-generation, retrieved 2026-07-29) |
| BFL FLUX.2 | **No.** "FLUX.2 does not support negative prompts." Guide says to describe desired outcomes rather than exclusions. | `[verified]` (source: https://docs.bfl.ml/guides/prompting_guide_flux2, retrieved 2026-07-29) |
| Ideogram | **Yes**, a Negative Prompt setting. "The Negative Prompt feature guides the AI away from generating specific types of images or content." | `[verified]` (source: https://docs.ideogram.ai/using-ideogram/generation-settings/negative-prompt, retrieved 2026-07-29) |
| Midjourney | **Yes**, the `--no` parameter, described as equivalent to a negative weight. | `[search-level]` — docs.midjourney.com returned HTTP 403 to my fetch. `[UNVERIFIED - needs the Midjourney "No" doc page read directly]` |
| Diffusers / open-weight pipelines | **Yes**, `negative_prompt`, and `negative_prompt_embeds` / `negative_pooled_prompt_embeds` for weighted variants. | `[verified]` (source: https://huggingface.co/docs/diffusers/en/using-diffusers/weighted_prompts, retrieved 2026-07-29 — the page tips: "You could also pass negative prompts to `negative_prompt_embeds` and `negative_pooled_prompt_embeds`") |

**The trend is unambiguous and it is the single most important structural fact in this dossier:** as
models move from CFG-diffusion toward large instruction-following generators, the negative-prompt
parameter is being *removed*, and exclusions move into the prompt as natural language. Google says it
in so many words — "legacy feature" `[verified]`. BFL says it flatly — not supported `[verified]`.
If your team's house style guide is a wall of `negative_prompt: "blurry, deformed, extra fingers,
watermark, low quality, bad anatomy"`, that guide is aging out. On a model with no such parameter,
that string either goes nowhere or, if you paste it into the main prompt, actively summons watermarks
and extra fingers.

### 4.3 How to write a negative prompt when the parameter exists

| Rule | Why | Evidence |
|---|---|---|
| Write nouns and attributes, not negated sentences. `people` — not `no people`, not `without people`. | The field is already negative; negating inside it is a double negative the model will not parse. Google's own example pairs prompt "a rainy city street at night" with negative prompt "people" rather than "with no people". | `[verified]` (cloud docs negative-prompt page, retrieved 2026-07-29) |
| Comma-separate a short list. | Ideogram: "Separate multiple items with commas (for example: green, green candies, cheese, cheddar.)" and "Be as precise as possible without providing excessive detail". | `[verified]` (docs.ideogram.ai negative-prompt, retrieved 2026-07-29) |
| Never contradict your own positive prompt. | Ideogram: "The content of the regular prompt will always be favored over the negative prompt", and contradictions reduce effectiveness. Asking for "a guitar" while negatively prompting "strings" is the documented shape of this mistake. | `[verified]` (same page) |
| Keep it short. | Long negative lists dilute each other exactly like long positive prompts, and each term drags the whole sample. Character *ceilings* are enormous (Stability allows 10,000 chars `[verified]`) which is not permission to use them. | `[craft]` |
| Prefer positive description first. | Ideogram: "It is often simpler and more effective to write prompts that naturally exclude unwanted elements instead of relying heavily on negative prompts." | `[verified]` (same page) |

**Failure to follow rule 1 breaks silently**: `negative_prompt: "no people"` on a CFG pipeline pushes
away from the concept-cluster of the word "no" plus the concept "people" — usually still helpful by
accident, which is why the bug survives for years in people's templates.

### 4.4 What to do when there is no negative parameter

Four substitutes, in order of reliability `[craft]`, with the documented hooks noted:

1. **Positive substitution — describe what occupies the space instead.** "An empty street at dawn,
   clean pavement, no litter" → better as "an empty street at dawn, freshly swept wet pavement". You
   have replaced an absence with a presence, which is the only thing a generative model can actually
   draw. Ideogram's documented fix for "Unwanted object, person or text appears" is exactly this —
   simplify the prompt and use "visual substitution instead of negatives" `[verified]`
   (docs.ideogram.ai troubleshooting, retrieved 2026-07-29).
2. **Explicit constraint clauses, placed last.** Instruction-following models do honour these. The
   OpenAI cookbook recommends stating exclusions and invariants explicitly — "'no watermark,' 'no
   extra text,' 'no logos/trademarks'" `[verified]`. Gemini lists "semantic negative prompts" as a
   core best practice `[verified]`. So: on these models, writing "no on-image text" is the *documented*
   method, not a hack.
3. **Structural prevention.** You cannot get a mangled hand if the hand is out of frame. Reframe
   ("crop at the wrists", "hands behind back", "holding the bowl with both hands wrapped around it, no
   fingers spread"). This converts a generation problem into a composition decision.
4. **Post-hoc masked repair.** Generate, then inpaint the offending region with a narrow prompt.
   Cheapest per unit of certainty when the defect is local (one bad hand, one stray object) and the
   rest of the frame is approved.

### 4.5 Decision rule

```
Does the API expose a negative-prompt field?
├─ Yes → use it for CONCRETE NOUNS you keep seeing and do not want (people, text,
│        watermark, hands, plates, cutlery). Max ~6 terms. Never negate inside it.
│        Never contradict the positive prompt.
└─ No  → 1. rewrite the exclusion as a positive description of what IS there
         2. add a short "Constraints:" line at the end of the prompt
         3. if it still appears twice in a row, change the framing so it cannot appear
         4. if it still appears, generate and inpaint it out
```

Never do both #1 and a long constraint list at once on your first attempt — you will not know which
worked, and one of them is probably costing you image quality.

---

## Part 5 — Getting rendered text exactly right

Text is the highest-stakes, lowest-reliability part of image generation, and for Vietnamese it is
harder than for English because of diacritics.

### 5.1 The documented rules

| Rule | Source statement | Evidence |
|---|---|---|
| Put the literal string in quotes | "Put literal text in quotes or ALL CAPS and specify typography details (font style, size, color, placement)" | `[verified]` (openai-cookbook image-gen prompting guide, retrieved 2026-07-29) |
| Quote it, again | "Enclose Text in Quotation Marks: Use quotation marks to specify the exact text you want to appear in the image." | `[verified]` (source: https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/2-prompting-fundamentals/text-and-typography, retrieved 2026-07-29) |
| Quote it, a third time | Recommends quotation marks: "The text 'OPEN' appears in red neon letters" | `[verified]` (docs.bfl.ml FLUX.2 prompting guide, retrieved 2026-07-29) |
| Spell hard words letter by letter | "For tricky words (brand names, uncommon spellings), spell them out letter-by-letter to improve character accuracy" | `[verified]` (openai-cookbook, retrieved 2026-07-29) |
| Keep it short — hard number | "Limit text to 25 characters or less for optimal generation." | `[verified]` (source: https://ai.google.dev/gemini-api/docs/imagen, retrieved 2026-07-29) |
| Keep it short — qualitative | "The longer the text you want to include, the higher the chance of spelling errors, distortions, or incomplete words." Ideogram "is not designed to generate complete, text-heavy documents." | `[verified]` (ideogram text-and-typography, retrieved 2026-07-29) |
| English is the safe case | "Text rendering is most accurate in English. Non-Latin scripts often produce unpredictable results." Also: "text that you would like to be written using a non-Latin alphabet **or accented Latin characters** may have some difficulty being generated correctly." | `[verified]` (ideogram text-and-typography, retrieved 2026-07-29) |
| Split multi-line text | "Break longer text into chunks. If you're trying to generate more than one line of text, split the content into sections with specific placement instructions." | `[verified]` (same page) |
| You cannot name a typeface | "At this time, it's not currently possible to specify a typeface by name." Describe stylistic properties instead — "bold sans-serif", "thin rounded bauhaus style". | `[verified]` (same page) — note this is Ideogram-specific; other providers may differ `[UNVERIFIED - needs per-provider check of whether named typefaces are honoured]` |
| Describe the font, expect interpretation | "Specify font style and size preferences; expect creative interpretation rather than precise replication." | `[verified]` (ai.google.dev/gemini-api/docs/imagen, retrieved 2026-07-29) |
| Busy scenes make text worse | "The more intricate the rest of the scene, the harder it is for the AI to cleanly render text." | `[verified]` (ideogram text-and-typography, retrieved 2026-07-29) |
| Put text early in the prompt | Ideogram's fix for "Text appears broken, misspelled, or missing" includes placing text in quotes, positioning it early in prompts, and using inpainting-style correction for fixes. | `[verified]` (docs.ideogram.ai troubleshooting, retrieved 2026-07-29) |
| Even good models still miss | "Although significantly improved, the model can still struggle with precise text placement and clarity." | `[verified]` (developers.openai.com image-generation guide, retrieved 2026-07-29) |
| Some models are marketed on text | "Gemini excels at rendering text. Be clear about the text, the font style (descriptively), and the overall design." | `[verified]` (ai.google.dev image-generation, retrieved 2026-07-29) |
| Structured text payloads exist | Ideogram 4.0 is described as supporting structured prompt control via natural language or JSON, with bounding-box layout control, and text elements carrying both the literal string and a separate visual style description. | `[search-level]` — from search summaries; `[UNVERIFIED - needs the Ideogram structured-prompt reference read directly to confirm field names]` |

### 5.2 The 25-character threshold, and what it implies

Google's Imagen guide gives the only hard number I could verify: **25 characters or less**
`[verified]`. Treat it as a *general* planning constraint even on other providers until you have your
own data, because the underlying cause — glyph-level rendering is per-character error-prone, so error
probability compounds with length — is architectural, not vendor-specific `[craft]`.

Arithmetic to make the risk concrete. **These numbers are `[illustrative]` — invented so the shape of
the compounding is visible. They are not measured and must not be quoted as fact.**

Assume an `[illustrative]` per-character correctness of 99% on a clean, high-contrast layout:

| Rendered string | Chars | `[illustrative]` P(all correct) = 0.99^n |
|---|---|---|
| `PHỞ` | 3 | 97% |
| `BÚN BÒ HUẾ` | 10 | 90% |
| `Bún bò Huế đặc biệt` | 19 | 83% |
| `Quán Bún Bò Huế Cô Ba — Mở cửa 6:00` | 35 | 70% |
| A three-line address block | 90 | 40% |

Again: `[illustrative]`. The operational lesson survives even if the true per-character rate is very
different — **each extra character is a multiplicative risk, so the fix is always fewer characters, not
better prompting.** At 35 characters you are gambling per render; at 90 you are wasting money.

### 5.3 The decision rule that saves the most time

```
Is the text short (≤ ~25 chars), a single line, in Latin script without diacritics,
and does an approximate typeface satisfy the brief?
├─ YES → generate the text in-image. Quote it. Specify placement and font description.
└─ NO  → DO NOT generate the text. Generate the image with reserved empty space, then
         set the type in a design tool.
```

This is the highest-value rule in the dossier for anyone doing Vietnamese-language marketing
material. Ideogram documents that *accented Latin characters* are among the difficult cases
`[verified]`. Vietnamese is accent-dense: **Bún bò Huế**, **bánh mì**, **cà phê sữa đá**, **chả cá Lã
Vọng**, **nước mắm**, **phở gà**. Each mark is an independent chance for the model to produce a word
that is not a word. `Huê`, `Huề`, `Hue` and `Huế` are four different strings and only one is the city.
A native reader clocks it instantly; a non-native reviewer will approve the wrong one.

**So: for Vietnamese copy, plan to composite type by default.** Prompt the image for empty space and
set the words yourself. What breaks if you ignore this: you ship a menu, poster or ad with a
misspelled dish name — the single most credibility-destroying error possible in food marketing, and
it is invisible to the person who approved it.

### 5.4 Prompting for reserved space (the composite-friendly render)

```
Mode: social ad background plate, no text.
Subject: a bowl of bún bò Huế, three-quarter overhead, right third of frame.
Scene: dark slate surface, scattered chilli and herb sprigs, soft steam.
Camera: 50mm, f/5.6, even studio light, one softbox top-left, subtle rim light.
Composition: 4:5 vertical. Subject occupies the lower right. The upper LEFT 40% of the
  frame is smooth, uncluttered dark surface with a gentle falloff, suitable for
  overlaying a headline. No objects, no highlights and no texture detail in that area.
Constraints: no text, no letters, no numbers, no logos, no watermark, no hands.
```

Two mechanics here matter. First, "no text, no letters, no numbers" as an explicit constraint clause
is the documented approach on models without a negative field (Part 4.2, 4.4). Second, describing the
reserved region *positively* — "smooth, uncluttered dark surface with a gentle falloff" — rather than
as an absence is what actually produces usable negative space. Gemini documents a minimalist /
negative-space template of the same shape: "A minimalist composition featuring a single [subject]
positioned in the [location]…" `[verified]` (ai.google.dev image-generation, retrieved 2026-07-29).

### 5.5 When you must generate text in-image

Sequence, and do not skip steps:

1. Reduce the string to the shortest form that carries meaning. `KHAI TRƯƠNG` beats
   `CHƯƠNG TRÌNH KHAI TRƯƠNG ƯU ĐÃI ĐẶC BIỆT`.
2. Put the quoted string early in the prompt `[verified]` Ideogram troubleshooting.
3. Simplify the surrounding scene — busy scenes degrade text `[verified]` Ideogram.
4. Flatten the surface the text sits on. Text on a plane renders far better than text wrapped around
   a curved cup or a folded napkin `[craft]`. Curved-surface text is where letterforms melt.
5. Increase deliverable resolution. More pixels per glyph is more room for correct strokes. Available
   sizes are provider-specific: see Part 6.
6. Deepen depth of field. f/8 not f/1.8. Bokeh is the enemy of legibility `[craft]`.
7. Generate a batch, not one. Text correctness is a lottery; buy more tickets. **Rule: for any
   in-image text, generate at least 4 candidates and read every glyph on each** `[craft]`.
8. Fix locally with masked inpainting rather than re-rolling the whole image — that is Ideogram's
   documented remedy shape (correct the text region rather than the scene) `[verified]`.
9. Final check: read the text **out loud** from the rendered image, and have a native speaker do it
   for non-English copy. Silent reading auto-corrects; reading aloud does not.

---

## Part 6 — Aspect ratio, resolution, and seed

### 6.1 Aspect ratio is a parameter, not a prompt word

Asking for "16:9" in the prompt text is unreliable to the point of being a known user complaint
`[search-level]` (a Gemini Apps community thread titled "Gemini's image generation is stuck at 1:1
aspect ratio, despite request and prompt for 16:9" appeared in search results;
`[UNVERIFIED - needs the thread read directly, and it concerns a consumer app rather than the API]`).
The mechanism is simple: output dimensions are set by the sampling/decoding configuration, so a
request expressed only in prose has to be *interpreted into* that configuration. If the surface does
not do that interpretation, your words change nothing.

**Rule:** set aspect ratio through the parameter. Use the prompt only to describe *composition within*
the frame ("subject in the lower right", "30% clear space at top"). If the only surface you have is a
chat box with no ratio control, expect the platform default and plan to crop `[craft]`.

### 6.2 Verified aspect-ratio and size surfaces

| Surface | Ratios / sizes | Evidence |
|---|---|---|
| Google Imagen (Gemini API docs page) | `aspectRatio`: `"1:1"`, `"3:4"`, `"4:3"`, `"9:16"`, `"16:9"`, default `"1:1"`. `imageSize`: `1K`, `2K` (Standard and Ultra models only), default `1K`. `numberOfImages`: 1–4, default 4. `personGeneration`: `"dont_allow"` / `"allow_adult"` (default) / `"allow_all"`, with `allow_all` restricted in EU, UK, CH, MENA. | `[verified]` (source: https://ai.google.dev/gemini-api/docs/imagen, retrieved 2026-07-29) |
| Gemini image generation | Ratios as retrieved: `1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`. Sizes: 512px (0.5K), 1K, 2K, 4K, with uppercase K, e.g. `"4K"`; one lightweight tier supports 1K only. | `[verified]` (source: https://ai.google.dev/gemini-api/docs/image-generation, retrieved 2026-07-29) |
| Gemini image generation — *parameter naming* | The page as retrieved showed aspect ratio and size passed inside a response-format object, e.g. `"aspect_ratio": "16:9"` and `"image_size": "2K"`. | `[verified]` that this is what the retrieved page rendered, **but** naming conventions differ between the raw REST surface, Vertex AI, and SDK wrappers. `[UNVERIFIED - needs the exact request field path confirmed in the SDK/REST reference you are calling before you write code]` |
| Stability Stable Image Core (via Bedrock) | `aspect_ratio` enum: `16:9`, `1:1`, `21:9`, `2:3`, `3:2`, `4:5`, `5:4`, `9:16`, `9:21`; default `1:1`; "only valid for text-to-image requests". `output_format`: JPEG, PNG. "Supported dimensions: height 640 to 1,536 px, width 640 to 1,536 px." `prompt` max 10,000 characters. | `[verified]` (source: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-diffusion-stable-image-core-text-image-request-response.html, retrieved 2026-07-29) |
| OpenAI image generation | Popular resolutions listed: `1024x1024`, `1536x1024`, `1024x1536`, `2048x2048`, `2048x1152`, `3840x2160`, `2160x3840`, and `auto`. Constraints: max edge ≤ 3840px; both edges multiples of 16; aspect ratio ≤ 3:1 long-to-short; total pixels 655,360–8,294,400. `quality`: `low`, `medium`, `high`, `auto` (default), with `quality: "low"` recommended for quick iteration. | `[verified]` (source: https://developers.openai.com/api/docs/guides/image-generation, retrieved 2026-07-29) |
| BFL FLUX.2 | Ratios include 1:1, 16:9, 9:16, 4:3, 21:9; "Output dimensions must be multiples of 16." | `[verified]` (source: https://docs.bfl.ml/guides/prompting_guide_flux2, retrieved 2026-07-29) |

Two operational consequences that bite people:

- **The multiple-of-16 rule** (OpenAI `[verified]`, BFL `[verified]`) means arbitrary pixel dimensions
  are not available. If you need 1080×1350 for a vertical social post you will generate the nearest
  legal size and crop. Plan the crop *before* you compose, or the model will put your subject exactly
  where you are about to cut.
- **The ≤3:1 ratio ceiling** on OpenAI `[verified]` means extreme banners (a 4:1 web hero) cannot be
  generated natively — generate wider-than-tall inside the limit and outpaint or extend, or generate at
  3:1 and crop. Attempting 4:1 will error or be silently coerced `[UNVERIFIED - needs a test call to
  see which]`.

### 6.3 Aspect ratio changes the *content*, not just the crop

This is the part beginners miss. Ratio is part of the conditioning: portrait frames pull toward
portrait-composed training images (single subject, vertical emphasis), wide frames pull toward
landscape and environmental compositions. Changing 1:1 → 16:9 with an identical prompt does not widen
your existing image; it generates a *different* image that happens to be wide, often by inventing
scene to the sides or by pulling the camera back `[craft]`.

**Rule:** decide the ratio before you tune the prompt. If you tune at 1:1 and then switch to 9:16,
expect to re-tune. Ideogram's documented fix for cropping problems pairs prompt framing language with
"adjusting aspect ratios" — the two are coupled `[verified]` (docs.ideogram.ai troubleshooting,
retrieved 2026-07-29).

For multi-format campaigns, the cheapest reliable route `[craft]`:

1. Generate the master at the *widest* format you need, with the subject positioned so that a centre
   crop and a vertical crop both work.
2. Derive tighter ratios by cropping.
3. Re-generate (not crop) only when the derived crop loses something essential.
4. Never derive a wide format from a square by outpainting if the extension must contain product or
   text — extension invents content, and invented content is unverified content.

### 6.4 Seed: where it exists and what it buys you

| Surface | Seed | Evidence |
|---|---|---|
| Stability Stable Image Core (Bedrock) | `seed` — "A specific value that is used to guide the 'randomness' of the generation. (Omit this parameter or pass 0 to use a random seed.) Range: 0 to 4294967295." The response returns `seeds` used. | `[verified]` (docs.aws.amazon.com Stable Image Core page, retrieved 2026-07-29) |
| Google Imagen on Vertex AI | Seed exists; range integers **1 to 2,147,483,647**; "Providing the same seed number always results in the same output images"; and critically "you must set `\"addWatermark\": false` to use this field". Caveat from the same page: "While the images you receive when using a seed are the same, there isn't a guarantee that Imagen returns the images in the same order each time." | `[verified]` (source: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/generate-deterministic-images, retrieved 2026-07-29) |
| Google Imagen via the Gemini API docs page | Seed **not mentioned** in the parameter list I read. | `[verified]` (ai.google.dev/gemini-api/docs/imagen, retrieved 2026-07-29) |
| Gemini image generation | Seed **not mentioned** as supported. | `[verified]` (ai.google.dev image-generation, retrieved 2026-07-29) |
| OpenAI image generation | Seed **not mentioned**. | `[verified]` (developers.openai.com image-generation guide, retrieved 2026-07-29) |
| BFL FLUX.2 | Seed present for reproducible results (guide's quick reference shows e.g. `seed: 42`). | `[verified]` (docs.bfl.ml prompting guide, retrieved 2026-07-29) |
| Midjourney | A seed parameter is widely documented. | `[search-level]`; `[UNVERIFIED - docs.midjourney.com returned 403 to my fetch]` |
| Ideogram | "Seed Number is available as an additional model-dependent control." | `[search-level]` from search summary; `[UNVERIFIED - needs the Ideogram generation-settings seed page read directly]` |

**What seed buys you:** the ability to change exactly one word and see only that word's effect. This
is the entire foundation of Part 7. Without it, you are comparing two samples from a distribution and
attributing the difference to your edit — which is a measurement error, not an experiment.

**What seed does not buy you:**

- Cross-model or cross-version reproducibility. Same seed, different model version, different image.
  Google's page does not promise cross-version stability, only same-seed-same-output `[verified]`;
  assume version bumps invalidate your seed library `[craft]`.
- Ordering guarantees in a batch — Google states there is no guarantee images come back in the same
  order `[verified]`. If your pipeline picks "the third image", it can pick a different one next run.
  Match by returned seed, not by index.
- Immunity to prompt-side nondeterminism. If a provider auto-rewrites your prompt (prompt upsampling
  / magic prompt / prompt rewriter), a fixed image seed does not fix the rewriter. Turn the rewriter
  **off** while iterating: BFL documents `prompt_upsampling` as "If true, performs upsampling on the
  prompt… adds detail and context to your prompt automatically" `[search-level]` (search summary of
  BFL/AI-SDK docs; `[UNVERIFIED - needs the BFL API reference read directly for the exact field]`),
  and Ideogram's Magic Prompt "uses Ideogram's built-in language model to interpret, refine, or expand
  your text" `[search-level]` (search summary of https://docs.ideogram.ai/using-ideogram/generation-settings/magic-prompt;
  `[UNVERIFIED - needs that page read directly]`). Google also documents a prompt-rewriter surface
  `[search-level]` (a "use prompt rewriter" cloud docs page appeared in results;
  `[UNVERIFIED - needs fetching]`). Any of these makes A/B comparison meaningless because your prompt
  is not the prompt that was used.

**Rule:** during iteration, hold seed fixed AND rewriter off. When you have a winner, re-roll across
4–8 seeds to check the prompt is robust rather than seed-lucky. A prompt that only works on one seed
is not a prompt, it is a coincidence `[craft]`.

### 6.5 The watermark / seed trade-off is a real operational fork

Google requires `"addWatermark": false` to use seed `[verified]`, and separately, Gemini's image docs
state "All generated images include a SynthID watermark" `[verified]` (ai.google.dev
image-generation, retrieved 2026-07-29). So on some surfaces you can choose determinism *or*
invisible provenance marking, and on others provenance is not optional at all.

Decide deliberately, and write the decision down:

- **Client/regulated work:** keep provenance marking on. Lose seed control; compensate with larger
  batches and reference images for consistency. Some markets and platforms have AI-disclosure
  expectations — `[UNVERIFIED - needs the disclosure rules for your market and each ad platform read
  live; do not infer them from this document]`.
- **Internal exploration:** turn watermarking off if permitted, keep seeds, iterate fast, then
  reproduce the final render with watermarking back on and re-verify (the image may change).

That last clause is the trap: if turning the watermark back on changes the pixels, your approved
render and your delivered render are not the same file. Approve the delivered configuration.

---

## Part 7 — Iterating with one variable at a time

### 7.1 Why this is non-negotiable

Image generation feels like conversation, so people edit like conversation: three changes at once,
then a judgement about the whole. That produces no knowledge. After twenty renders you have twenty
images and no idea which words matter, so you cannot write the *next* prompt any better — and prompt
reuse is the only thing that makes this economical at scale.

The vendor guidance is unusually consistent on this:

- "Start with a clean base prompt, then refine with small, single-change follow-ups" and "Long prompts
  can work, but debugging is easier if you start with a clean base prompt and refine with small,
  single-change follow-ups. Re-specify critical constraints when drift appears." `[verified]`
  (openai-cookbook image-gen prompting guide, retrieved 2026-07-29)
- "Multi-turn conversation is the recommended way to iterate on images." `[verified]`
  (ai.google.dev image-generation, retrieved 2026-07-29)
- "Iterate and refine" listed among core best practices `[verified]` (same page)
- "Start simple, then add details." `[verified]` (huggingface.co diffusers prompting doc, retrieved
  2026-07-29)

### 7.2 The loop

```
0. FIX THE FRAME       Choose aspect ratio + output size. Never change these mid-loop.
1. BASE PROMPT         Slots 1,2,4 only (intent, subject, scene). 15-25 words. Cheapest
                       quality setting — OpenAI's guide suggests starting at quality:"low"
                       for latency-sensitive work [verified].
2. BATCH               4 images. Fix the seed if you have one; otherwise record the seeds.
3. TRIAGE              Is the SUBJECT right? If no, fix the subject and repeat step 2.
                       Nothing downstream matters until the subject is right.
4. ONE VARIABLE        Add or change exactly ONE slot. Re-render on the SAME seed.
5. DIFF                Compare side by side at 100% zoom. Write down what the change did.
6. KEEP OR REVERT      Keep only if it improved the thing you were targeting. Revert
                       otherwise — even if the image got prettier in some other way.
7. REPEAT 4-6          Until all seven slots are filled or you stop improving.
8. ROBUSTNESS          Re-run the final prompt on 4-8 fresh seeds. If quality collapses on
                       most, the prompt is seed-dependent: strengthen the weak slot.
9. UPRES               Only now raise quality/size. Re-verify text and product at 100%.
10. LOG                Save prompt + seed + parameters + output together. A prompt without
                       its parameters is not reproducible.
```

Step 3 is the one people skip and it costs the most. Tuning lighting on an image whose subject is
wrong is pure waste.

Step 9 exists because quality/size changes can alter content, not merely resolution. Never assume the
high-quality render is the low-quality render with more pixels `[craft]`.

### 7.3 Change-one-thing table: symptom → the single slot to touch

| Symptom | Change ONLY this | Do not touch |
|---|---|---|
| Subject is wrong or absent | Slot 2/3: make the subject more concrete; move it to the front | Lighting, style, camera |
| Right subject, wrong mood | Slot 5 light lines | Subject wording |
| Right mood, wrong depth/realism | Slot 5 focal length + aperture | Light |
| Subject cropped | Slot 6 shot size ("full body", "full bowl visible") and/or the ratio | Everything else |
| Background too busy | Slot 4, simplify; or slot 1, say "studio" | Subject |
| Style bleeding into product | Move style out of slot 5 into a style reference image (Part 3) | Subject, composition |
| Text garbled | Shorten the string (Part 5); simplify the scene | Camera, style |
| Count wrong | Slot 3: restate the number and describe the arrangement | Style |
| Attribute swapped between objects | Slot 3: split into separate sentences, one object each | Everything else |
| Colours off-brand | Slot 3/5: name the colour on the object; consider hex (BFL documents "color #FF5733" or "hex #FF5733" and warns "Hex codes work best when clearly associated with specific objects" `[verified]`, docs.bfl.ml, retrieved 2026-07-29) | Composition |
| Product drifted during edit | Restate the full preserve list; reduce the number of chained edits; go back to the original | The scene description |

### 7.4 The iteration log (copy this table)

| # | Seed | Changed slot | Exact change | Effect observed | Keep? |
|---|---|---|---|---|---|
| 1 | 1042 | — | base prompt | subject correct, flat light | ✅ base |
| 2 | 1042 | 5 light | added "one softbox camera left" | shape appeared, right side too dark | ✅ |
| 3 | 1042 | 5 light | added "white bounce card right" | shadow opened, still directional | ✅ |
| 4 | 1042 | 5 lens | 50mm → 85mm | background compressed, less context | ❌ revert (brief needs the stall visible) |
| 5 | 1042 | 6 comp | "30% clear space upper left" | headline space appeared, bowl smaller | ✅ |

Seeds shown are `[illustrative]`. The point is the *shape*: one row per change, and an explicit
keep/revert with a reason. Teams that keep this log build a house prompt library in weeks. Teams that
do not re-solve the same problem every campaign.

### 7.5 Editing vs. re-generating — which to reach for

| Situation | Do this | Why |
|---|---|---|
| One local defect, rest approved | Masked inpaint on that region | Preserves the approved 95%; smallest blast radius |
| Global look is wrong | Re-generate from prompt | Editing cannot fix a fundamentally wrong lighting design |
| Need the same scene in a new ratio | Re-generate at the target ratio; do not outpaint if the extension must contain anything verifiable | Outpainting invents content |
| Need the same product in a new scene | Product-lock workflow (Part 3.4) | The product is the invariant, the scene is the variable |
| Need 20 on-brand variations | Fix a style reference + vary the subject line only | Words alone will not hold a look across 20 renders |
| Fifth consecutive edit on one image | Stop. Return to the original and issue one combined instruction | Drift compounds per edit (Part 3.4 step 6) |

---

## Part 8 — The failure modes, diagnosed

Each entry: what it looks like, why it happens, the first fix, the fallback, and what it costs if you
ship it.

### 8.1 Concept bleed (a.k.a. attribute/style leakage)

**Looks like:** you ask for "a woman in a red dress beside a blue vintage car" and get a reddish car,
or "watercolour style" turns the product label into a painting too.

**Why:** conditioning is global. Cross-attention distributes a token's influence over the whole latent
rather than confining it to one region. Style tokens are the worst offenders because they legitimately
describe the whole image.

**First fix:** one object per sentence, attribute adjacent to its noun, style token moved to the end
and reduced to one or two words.

**Fallback:** move the style out of the text entirely and into a style-reference image with a moderate
strength — Firefly's `strength` is 1–100, default 50 `[verified]`
(developer.adobe.com style-image-reference, retrieved 2026-07-29), so 30–40 is the natural first step
down when style is overpowering content. Or generate the styled background and the clean product
separately and composite.

**Cost of shipping it:** off-brand colour on the hero object. On packaging, a factually wrong product.

### 8.2 Attribute binding errors and catastrophic neglect

These are named, studied failure modes, not user error.

> The Attend-and-Excite paper identifies two semantic issues in Stable Diffusion: **catastrophic
> neglect**, where the model "fails to generate one or more of the subjects from the input prompt",
> and attribute binding errors, where it "fails to correctly bind attributes (e.g., colors) to their
> corresponding subjects."
> `[verified]` — Chefer, Alaluf, Vinker, Wolf, Cohen-Or, "Attend-and-Excite: Attention-Based Semantic
> Guidance for Text-to-Image Diffusion Models", submitted 31 January 2023, revised 31 May 2023,
> accepted to SIGGRAPH 2023 (source: https://arxiv.org/abs/2301.13826, retrieved 2026-07-29). The
> paper's method, "Generative Semantic Nursing (GSN)", intervenes at inference to "refine the
> cross-attention units to attend to all subject tokens in the text prompt and strengthen — or excite —
> their activations".

Why this matters to you even though you will never implement GSN: it tells you the mechanism. Neglect
happens when a subject token's attention activation is weak. Everything you can do from the prompt
side is a crude version of "excite that token":

**First fix (neglect):** move the neglected subject earlier; give it its own sentence; make it more
concrete and more visually distinctive; delete a competing object. Ideogram's documented fix for
"Important words or concepts are not visually present" is to use "more concrete visual language" and
add "explicit visual cues" `[verified]` (docs.ideogram.ai troubleshooting, retrieved 2026-07-29).

**First fix (binding):** separate sentences per object. "A red bowl sits on the left. A blue cup sits
on the right." beats "a red bowl and a blue cup".

**Fallback:** generate the objects in separate passes and composite, or use a composition/layout
control so each object has a region. If the API exposes bounding-box layout control, that is the
strongest available fix `[search-level]` for Ideogram 4.0's bounding-box layout control;
`[UNVERIFIED - needs the structured-prompt reference read directly]`.

**Cost of shipping it:** a colour-swapped product is a factual error; a missing subject is a wasted
placement.

### 8.3 Count errors

**Looks like:** "four slices of beef" arrives as three or six. "Three panels" arrives as two.

**Why:** counting is not represented as arithmetic; number words are weak conditioning signals and
compete with strong visual priors about how much stuff belongs in a bowl.

**Fixes, in order:**
1. Keep counts small. Reliability drops fast above ~4 `[craft]`; I have no citable accuracy-by-count
   curve `[UNVERIFIED - needs a citable counting benchmark read from source]`.
2. Describe the *arrangement*, not just the number: "four beef slices fanned in a row along the far
   rim" gives the model a spatial structure to satisfy, which is easier than a count.
3. Make the items visually distinct if possible.
4. If the count is contractual (e.g. "6 pieces" in a promotional offer), do not generate it —
   composite, or shoot it. A wrong count in a promo image is an advertising claim you cannot support.
5. Accept-and-caption: change the copy to avoid a specific number.

**Cost of shipping it:** a promotional image showing five pieces for a "6 pieces" offer is a consumer
complaint and possibly a regulatory one `[UNVERIFIED - needs your market's advertising rules read
live]`.

### 8.4 Mangled hands, limbs, and faces at small scale

**Looks like:** six fingers, fused knuckles, a wrist that bends the wrong way, a background face that
is a smear.

**Why:** hands are high-articulation, high-variance, and small in frame, so they get few pixels and
enormous pose diversity in training. Small background faces get too few pixels to resolve.

**Fixes:**
1. **Reframe so hands are absent or simple.** Crop at the wrist, hands in pockets, hands wrapped
   around a bowl, one hand holding chopsticks near the top of the frame with fingers together. The
   cheapest fix is always "fewer visible fingers".
2. **Get closer.** Ideogram's documented remedy for distorted facial features, hands or limbs is to
   move subjects closer with framing cues like "close-up" and emphasise the details explicitly
   `[verified]` (docs.ideogram.ai troubleshooting, retrieved 2026-07-29). More pixels, better anatomy.
3. **Inpaint the hand region** at higher effective resolution.
4. **Batch and select.** Anatomy is a lottery per render.
5. On surfaces with a negative field, "extra fingers, deformed hands" is a legitimate use of it —
   concrete nouns, short list (Part 4.3).

**Cost of shipping it:** the single most recognisable "this is AI slop" tell. Audiences spot hands
before they spot anything else.

### 8.5 Mangled text

Covered in depth in Part 5. Diagnostic shortcut: if the string is over ~25 characters `[verified]`
Imagen guidance, or contains diacritics `[verified]` Ideogram guidance, or sits on a curved surface, or
the scene is busy `[verified]` Ideogram guidance — do not debug the prompt. Change the plan: reserve
space and set type externally.

### 8.6 Style collapse and set incoherence

**Two opposite versions, and people confuse them:**

- **Collapse toward the default look.** You asked for a distinctive style; you got the model's house
  aesthetic (glossy, symmetrical, over-lit, teal-and-orange). Usually because the style words were
  vague. Ideogram's documented fix for "The style or visual mood isn't right" is to specify concrete
  styles like "watercolour" rather than vague terms `[verified]` (docs.ideogram.ai troubleshooting,
  retrieved 2026-07-29).
- **Collapse of variety within a set.** Twenty renders that are all the same composition. Usually
  because your prompt over-specifies composition while under-specifying subject variety, or because
  you are re-using one seed.

**Set incoherence** is the inverse and more common commercially: twenty images that each look fine and
nothing like each other. Words cannot hold a look across a set with adequate precision.

**Fix for set coherence, in order of strength `[craft]`:**
1. One style reference image, fixed, at a moderate strength, for every image in the set.
2. A frozen "look block" of text — identical camera, light and grade lines in every prompt, with only
   the subject line varying. This is exactly why the labeled-slot format in Part 1.3 pays off.
3. A fixed post-process (same LUT / grade / grain applied to all outputs afterward). Unglamorous and
   extremely effective — it hides a surprising amount of model-side variation.
4. Fixed aspect ratio and fixed output size across the set.

**Cost of shipping it:** a campaign that reads as a pile of stock images rather than a brand.

### 8.7 Silent parameter drop

**Looks like:** nothing. The image comes back. It is just not what you asked.

**Why:** you sent a field the endpoint does not accept (a negative prompt to a model that dropped it,
a seed to a surface that has none, an aspect ratio in prose to a surface that only reads the
parameter), and it was ignored rather than rejected.

**Detection `[craft]`:** run a **canary test** for every parameter you depend on. Send an absurd value
and check the image changes. Seed canary: same prompt, seeds 1 and 2 — if the images are identical,
seed is being ignored; if they differ wildly *and* re-running seed 1 does not reproduce, seed is being
ignored the other way. Negative-prompt canary: put `bowl` in the negative field on a bowl prompt — if
the bowl remains, the field is dead. Aspect-ratio canary: request 21:9 and measure the returned pixel
dimensions.

**Cost of skipping the canaries:** months of a team believing its house negative-prompt template is
doing something.

### 8.8 Prompt rewriter interference

**Looks like:** your careful minimal prompt returns an over-decorated image; identical requests differ
more than they should; removing a word changes nothing.

**Why:** an upstream LLM expanded your prompt. See 6.4 for the documented surfaces (prompt
upsampling, magic prompt, prompt rewriters — all `[search-level]` / `[UNVERIFIED]` as to exact field
names).

**Fix:** find the toggle and turn it off for iteration. If the surface does not let you, accept that
you are tuning a system with a nondeterministic front end and compensate with larger batches. Do not
draw single-render conclusions.

### 8.9 The physics-consistency failure

**Looks like:** the shadow falls left while the light comes from the left; a reflection shows something
not in the scene; steam rises from a dish with no heat cues; a spoon disappears where it enters the
broth.

**Why:** models learn correlations, not ray optics.

**Fix:** state light direction once and then state its consequences explicitly ("light from camera
left, so shadows fall to the right"). Check reflective surfaces at 100% zoom — glass, chrome, broth
surface, phone screens. For composites, match your inserted product's shadow direction and softness to
the plate's stated light or the fake reads instantly.

**Cost of shipping it:** the image feels "off" to viewers who cannot articulate why, which is worse
than an obvious error because nobody flags it in review.

---

## Part 9 — Worked example: a bún bò Huế campaign, end to end

Brief `[illustrative]` — invented so the workflow is followable, not a real client: a Huế noodle
restaurant needs (a) a menu hero for **Bún bò Huế đặc biệt**, (b) a 4:5 social ad with a headline, and
(c) a bottle shot of their **nước mắm ớt** house sauce whose label must stay exactly as printed.
Budget: one afternoon.

### 9.1 Deliverable A — the menu hero (no text in image)

**Step 0. Fix the frame.** Menu prints at roughly 3:2; generate 3:2 if available (Stability documents
a `3:2` enum value `[verified]`; Gemini's list as retrieved includes `3:2` `[verified]`; Imagen's
documented set does not — it has 4:3, so you would generate 4:3 and crop `[verified]`).

**Step 1. Base prompt (slots 1, 2, 4 only).**
```
Menu photograph. A bowl of bún bò Huế on a dark walnut table in a Huế noodle shop.
```
Batch of 4. Triage: is it recognisably bún bò Huế — round rice noodles, deep red-orange chilli broth,
beef shank, chả lụa — or has the model produced generic ramen? This is the critical checkpoint. Models
have far more ramen and pho in their priors than bún bò Huế `[craft]`, so the most likely failure is a
plausible-looking wrong dish.

**Step 2. If the dish is wrong, fix the dish, not the lighting.** Describe it as a photographer would
describe what is visible, not as a menu would name it:
```
Menu photograph. A bowl of bún bò Huế: thick round rice noodles in a deep red-orange
chilli-and-lemongrass beef broth with a thin chilli-oil sheen, topped with 3 slices of
beef shank, 2 rounds of chả lụa, a slice of huyết, shredded banana blossom and thinly
sliced raw onion. A lime wedge on the rim. Dark walnut table, Huế noodle shop behind.
```
Note what happened: the dish name stayed (it is a real signal) but every diagnostic feature is now
stated visually. If the model does not know the name, it can still draw the description. **This is the
general technique for any regional or niche subject: name it AND describe it.** If you only name it,
you are betting on the model's coverage of your cuisine; if you only describe it, you lose whatever
correct prior exists.

**Step 3. One variable — light.** Add: `One large softbox from camera left, white bounce card right,
soft directional light, no hard speculars.` Compare on the same seed.

**Step 4. One variable — optics.** Add: `50mm equivalent, f/4, three-quarter high angle at 40 degrees.`

**Step 5. One variable — composition.** Add: `Bowl centred, full bowl visible including the rim, chopsticks resting on the far side parallel to the frame edge.` ("Full bowl visible" is the anti-crop
insurance — Ideogram documents explicit framing language as the crop fix `[verified]`.)

**Step 6. Constraints.** `No text, no logos, no watermark, no hands.`

**Step 7. Robustness.** Re-run on 6 seeds. Expect 2–4 usable. Steam, herb scatter and noodle
arrangement will vary; that is fine — the *look* must not.

**Step 8. Upres and inspect at 100%.** Check: noodle shape is round not flat, broth colour is
red-orange not brown, no invented cutlery, chopstick count is two, no melted rim.

### 9.2 Deliverable B — the 4:5 social ad with a headline

Because the headline is **"Bún bò Huế đặc biệt — 65.000 ₫"**, we do not generate the text. Reasons,
all verified: it is 29 characters, over Imagen's documented 25-character guidance `[verified]`; it is
accent-dense and Ideogram documents accented Latin characters as difficult `[verified]`; and it
contains a currency figure where a single wrong digit is a pricing error.

Vietnamese currency formatting to preserve when you set the type: **65.000 ₫** — period as the
thousands separator, space before the đồng sign. Writing it as `65,000 ₫` or `65.000₫` is wrong for
Vietnamese convention. An image model asked to render this will not respect either the separator or
the spacing reliably `[craft]`.

**Prompt (plate only, space reserved):**
```
Mode: social ad background plate, 4:5 vertical, no text.
Subject: a bowl of bún bò Huế [full description block reused verbatim from 9.1].
Scene: dark slate surface, a few chilli slices and rau thơm sprigs scattered at the base
  of the bowl, faint steam.
Camera: 50mm, f/5.6, 35-degree high angle.
Light: one softbox top-left, subtle rim light from behind, no hard speculars.
Composition: the bowl occupies the LOWER 55% of the frame, slightly right of centre.
  The upper 40% is smooth, uncluttered dark slate with gentle falloff — no objects, no
  highlights, no texture detail there.
Constraints: no text, no letters, no numbers, no logos, no watermark, no hands.
```

Then set **Bún bò Huế đặc biệt — 65.000 ₫** in your real brand typeface in a design tool. Benefits
beyond correctness: you get the actual font (Ideogram documents that you cannot specify a typeface by
name `[verified]`), real kerning, and a text layer you can localise or reprice without re-generating
the image.

Note the reuse: the subject description block is *identical* to 9.1. That is set coherence by
construction (Part 8.6, fix #2).

### 9.3 Deliverable C — the nước mắm ớt bottle, product-locked

The label is real, printed, and must not change. Apply Part 3.4:

1. **Preferred route:** generate the environment only, then composite the real bottle cut-out.
   ```
   Product photography background plate. An empty dark slate surface with a soft
   gradient, warm side light from camera left, gentle falloff to near-black at the
   right edge, a faint reflective sheen on the surface where a bottle would stand.
   85mm, f/8. No objects in frame. No text.
   ```
   Place the bottle, then match shadow direction (falling right, since light is from the left) and
   softness. Add contact shadow and a subtle surface reflection manually.
2. **If the model must hold the bottle:** supply the bottle photo as Image 1 with the labeling pattern
   from 3.3, mask the bottle out of the editable region, restate the preserve list every turn, cap at
   3–4 chained edits, and then run the 3.4 QA checklist. Pay special attention to the label's
   Vietnamese text: **nước mắm ớt** has three diacritic-bearing characters in seven letters. Check
   each one at 100% zoom. Remember the documented caveat that masks are guidance and "may not follow
   its exact shape with complete precision" `[verified]` (developers.openai.com image-generation
   guide, retrieved 2026-07-29) — which is precisely why route 1 exists.

### 9.4 What the afternoon actually costs

Rough plan, `[illustrative]` — invented to show proportions, not measured:

| Phase | Renders | Note |
|---|---|---|
| A: dish correctness | 8–16 | Most of your budget. Niche cuisine costs iterations. |
| A: look tuning | 12–20 | 4 per changed slot, same seed |
| A: robustness + upres | 8 | |
| B: plate with reserved space | 8 | Composition is the only new variable |
| B: typesetting | 0 renders | Design tool |
| C: background plate | 4 | Empty plates are easy |
| C: composite + shadow match | 0–4 | Mostly manual |

The distribution is the lesson: subject correctness dominates, and text generation is zero because you
moved it out of the model. If your render count is dominated by re-rolling text, your process is
wrong, not your prompt.

---

## Part 10 — Model-agnostic craft vs. provider-specific mechanics

The most useful thing you can carry between tools is the knowledge of which half of your skill is
portable.

### 10.1 Portable craft (survives every model change)

| Technique | Why it is portable |
|---|---|
| The seven-slot skeleton (intent / subject / detail / scene / rendering / composition / constraints) | It is a taxonomy of *what a picture is*, not of an API |
| Subject-first, style-last ordering | Follows from attention dilution and global style conditioning, both architectural |
| Name it AND describe it, for niche subjects | Hedges against unknown training coverage |
| Describing a photograph (optics + light) rather than stacking quality adjectives | Optical vocabulary is densely and consistently represented in captions everywhere |
| One object per sentence, attribute adjacent to noun | Direct mitigation of a documented binding failure `[verified]` arxiv 2301.13826 |
| Small counts, described arrangements | Counting weakness is architectural |
| Reframe rather than repair hands | Composition beats generation |
| Reserve space and set type externally | Glyph rendering is per-character error-prone everywhere |
| One variable per iteration, with a log | It is experimental method, not a feature |
| Fixed look-block + varying subject-line for set coherence | Works even with zero API controls |
| Fixed post-process grade across a set | Entirely outside the model |
| 100%-zoom QA on text, logos, hands, reflections | Review discipline |
| Cap chained edits at 3–4 | Drift compounds in any latent re-encoding loop |
| Canary-test every parameter you depend on | Defends against silent drops in any API |

### 10.2 Provider-specific mechanics (re-verify on every project)

| Mechanic | Status as of 2026-07-29 |
|---|---|
| Negative-prompt parameter | Present on Stability `[verified]`, Ideogram `[verified]`, Diffusers `[verified]`, legacy-and-removed on newer Imagen `[verified]`, absent on OpenAI `[verified]`, absent on FLUX.2 `[verified]`, absent on Gemini image generation `[verified]`, present on Midjourney as `--no` `[search-level]` |
| Seed | Stability 0–4294967295 `[verified]`; Vertex Imagen 1–2147483647 and requires `addWatermark:false` `[verified]`; FLUX.2 yes `[verified]`; OpenAI not mentioned `[verified]`; Gemini image generation not mentioned `[verified]` |
| Aspect-ratio enum | Differs per provider — see 6.2. Imagen's documented set is the narrowest of those I read (5 values) `[verified]` |
| Output size / resolution tiers | Differs; OpenAI has explicit pixel constraints including multiple-of-16 edges and ≤3:1 ratio `[verified]`; Gemini image generation exposes 0.5K/1K/2K/4K tiers `[verified]`; Imagen exposes 1K/2K on some models `[verified]`; Stability's documented dimension range is 640–1536 px per edge `[verified]` |
| Reference-image role slots | Typed on Firefly (`structure`, `style`, each with `strength` 1–100, default 50) `[verified]`; prose-declared on OpenAI `[verified]` and FLUX.2 `[verified]`; role-budgeted on Gemini (object / character / style counts) `[verified]` |
| Reference-image count limits | FLUX.2 up to 8 at 1MP output `[verified]`; Gemini per-tier object/character/style budgets `[verified]`; others `[UNVERIFIED - needs live doc check]` |
| Mask semantics | OpenAI: prompt-based guidance, alpha channel required, mask applies to first image only, may not follow the exact shape `[verified]`. Other providers' mask hardness `[UNVERIFIED - needs live doc check]` |
| Input-fidelity control | OpenAI `input_fidelity`, to be omitted on the model the page names `gpt-image-2` `[verified]` |
| Prompt length ceiling | Imagen 480 tokens `[verified]`; Stability prompt 10,000 chars and negative_prompt 10,000 chars `[verified]`; others `[UNVERIFIED - needs live doc check]` |
| Prompt rewriting / upsampling | Exists in some form on BFL, Ideogram, Google `[search-level]` for all three; exact field names `[UNVERIFIED]` |
| Watermarking / provenance | Gemini image generation: "All generated images include a SynthID watermark" `[verified]`; Vertex Imagen has `addWatermark` and it conflicts with seed `[verified]`; others `[UNVERIFIED - needs live doc check]` |
| Person-generation policy gates | Imagen `personGeneration` with `dont_allow` / `allow_adult` (default) / `allow_all`, `allow_all` restricted in EU, UK, CH, MENA `[verified]` |
| Named-typeface support | Ideogram documents that naming a typeface is not currently possible `[verified]`; other providers `[UNVERIFIED - needs live doc check]` |
| Numeric prompt weighting `(word:1.4)` | Open-weight pipelines via scaled embeddings `[verified]`; Midjourney `::` weights `[search-level]`; hosted instruction-following models — assume unsupported `[UNVERIFIED - needs live doc check]` |
| Hex colour prompting | FLUX.2 documents `color #FF5733` / `hex #FF5733` with the caveat that hex "works best when clearly associated with specific objects" `[verified]`; other providers `[UNVERIFIED - needs live doc check]` |
| Structured / JSON prompts with bounding boxes | Ideogram 4.0 described this way `[search-level]`; FLUX.2 guide mentions structured JSON prompts for complex scenes `[verified]` that they help, exact schema `[UNVERIFIED - needs the schema read from the provider reference]` |
| Cost model for edits | OpenAI: "Edits often cost more than generations of the same output size, because reference images add input tokens" `[search-level]` from a search summary of the OpenAI guide; `[UNVERIFIED - needs the pricing page read live; no prices are quoted anywhere in this dossier]` |

### 10.3 Explicit non-claims

I am naming these so nobody mistakes silence for endorsement:

- **No prices, credit costs, or rate limits appear anywhere in this dossier.** They change constantly.
  `[UNVERIFIED - needs each provider's live pricing page]`.
- **No claim about which model is "best"** at anything. Vendor docs make claims about their own models
  ("Gemini excels at rendering text" `[verified]` is Google describing Google); those are quoted as
  vendor statements, not as comparative findings. `[UNVERIFIED - needs an independent, methodology-
  disclosed benchmark read from source]`.
- **No named film stocks, no named photographers, no named typefaces** as things that reliably work.
- **No regulatory or advertising-standards rule** is stated as fact. Every mention is flagged.
- **No statistic about failure rates** is real. The compounding table in 5.2 and the render budget in
  9.4 are `[illustrative]` and labelled as such.
- **Midjourney details are all `[search-level]`** because docs.midjourney.com returned HTTP 403 to
  every fetch attempt in this session.

---

## Part 11 — Operating checklists

### 11.1 Before your first render on a new provider (30 minutes, once)

- [ ] Read the current prompting guide. Note the documented prompt *order* — it varies (Part 1.1).
- [ ] Note the prompt length ceiling in tokens or characters.
- [ ] List the aspect ratios and output sizes actually available. Write down which of your deliverable
      formats must be produced by cropping.
- [ ] Determine whether a negative-prompt field exists. **Canary-test it** (Part 8.7).
- [ ] Determine whether a seed exists, its range, and what it conflicts with (watermarking, batching
      order). **Canary-test it.**
- [ ] Determine whether prompt rewriting is on by default and how to turn it off. **Canary-test it**
      by sending a two-word prompt and seeing how much detail comes back.
- [ ] Determine reference-image roles, counts, and whether roles are typed or prose-declared.
- [ ] Determine mask semantics: hard clip or soft guidance? If soft, plan to composite for anything
      that must be exact.
- [ ] Determine provenance/watermarking behaviour and whether it is optional.
- [ ] Determine person-generation and content-policy gates that apply to your market.
- [ ] Save all of the above with the retrieval date next to it. It will be stale in months.

### 11.2 Per-image pre-flight

- [ ] Aspect ratio and output size fixed, set via parameter not prose.
- [ ] Intent/mode stated in the first clause.
- [ ] Subject stated concretely, early, and — for niche subjects — both named and described.
- [ ] Each object's attributes adjacent to that object; one object per sentence where it matters.
- [ ] Counts ≤ 4 and arrangements described.
- [ ] Exactly one focal length, one aperture, one light direction, one light quality.
- [ ] Framing stated ("full bowl visible", "crop at the wrists").
- [ ] Reserved space described positively if type will be overlaid.
- [ ] In-image text ≤ ~25 characters, quoted, Latin script without diacritics — or moved out of the
      model entirely.
- [ ] Constraints line present: no text / no logos / no watermark / no hands, as applicable.
- [ ] Reference images labeled by index with role and an explicit "ignore" list.
- [ ] Seed fixed and recorded; rewriter off.
- [ ] Style handled by reference image if the set must be coherent.

### 11.3 Per-image post-flight (100% zoom, every time)

- [ ] Subject is the correct thing, not a plausible neighbour (bún bò Huế, not ramen).
- [ ] All requested objects present. Count them.
- [ ] Attributes on the right objects. Check colours object by object.
- [ ] Every glyph of every rendered word correct, including diacritics. Read aloud.
- [ ] Currency and numbers correct and correctly formatted (**65.000 ₫**, not `65,000₫`).
- [ ] Hands: finger count, joint direction, no fusion.
- [ ] Product: label text, logo geometry, proportions, brand hex — diffed against source.
- [ ] Shadows consistent with the stated light direction; reflections contain only real scene content.
- [ ] No duplicated subject in the background, no floating objects, no impossible cutlery.
- [ ] Nothing important sits where the deliverable crop will cut.
- [ ] Prompt + seed + all parameters + output filename logged together.

### 11.4 Escalation ladder — when to stop prompting

Stop and change approach when any of these is true `[craft]`:

| Trigger | Escalate to |
|---|---|
| 3 attempts have failed to fix the same defect | Change the *framing* so the defect cannot occur |
| 5 attempts have failed | Split the image: generate parts, composite |
| The defect is rendered text | Composite the type. Immediately, not after five tries. |
| The defect is on a real product's label | Composite the real product. Stop asking the model. |
| The defect is a contractual count, price or claim | Do not generate it at all |
| The set will not hold a look across >8 images | Style reference + frozen look-block + fixed post-grade |
| You cannot tell whether your parameter did anything | Canary test before another render |

The meta-rule: **generative models are for the parts of an image that are allowed to vary.** Anything
that is legally, factually, or typographically fixed should enter the image as a fixed asset. Almost
every expensive failure in commercial AI imaging is someone asking a sampler to reproduce a constant.

---

## Appendix A — Gaps register (what to close first)

Ordered by how much damage the gap can do.

| # | Gap | What would close it |
|---|---|---|
| 1 | Exact request-field paths for Gemini image generation aspect ratio and size — the retrieved page showed them nested in a response-format object, which conflicts with naming conventions elsewhere | `[UNVERIFIED - needs the current REST/SDK reference for the exact surface you call, plus one live request checking the returned pixel dimensions]` |
| 2 | Whether the Imagen product-recontext surface guarantees any product preservation, and its parameter names | `[UNVERIFIED - needs that Google Cloud page fetched successfully; it returned navigation chrome only]` |
| 3 | All Midjourney specifics (`--no`, `::` weights, seed, `--ar`) | `[UNVERIFIED - docs.midjourney.com returns 403 to automated fetch; needs reading in a logged-in browser]` |
| 4 | Whether named typefaces are honoured on any provider | `[UNVERIFIED - needs a per-provider doc statement plus a controlled test]` |
| 5 | Token-limit behaviour on legacy CLIP-conditioned pipelines (the 77-token figure) | `[UNVERIFIED - needs a live tokenizer/pipeline doc page]` |
| 6 | Accuracy-vs-object-count and accuracy-vs-count curves for compositional prompts | `[UNVERIFIED - needs a citable compositional benchmark read from source]` |
| 7 | Per-provider mask hardness (guidance vs. clip) beyond OpenAI | `[UNVERIFIED - needs each provider's edit/mask doc]` |
| 8 | Exact prompt-rewriter toggles and field names on BFL, Ideogram, Google | `[UNVERIFIED - needs each API reference read directly]` |
| 9 | AI-disclosure and labelling obligations for ad platforms and for the Vietnamese market | `[UNVERIFIED - needs the platform policies and national rules read live; consult counsel, not this file]` |
| 10 | Ideogram structured/JSON prompt schema and bounding-box layout fields | `[UNVERIFIED - needs the structured-prompt reference read directly]` |

## Appendix B — One-card summary

```
FRAME FIRST         ratio + size as PARAMETERS, before any prompt tuning
SEVEN SLOTS         intent | subject | detail | scene | rendering | composition | constraints
SUBJECT FIRST       most important thing earliest; style last and short
NAME + DESCRIBE     for niche subjects, give the name AND the visual diagnostics
PHOTOGRAPH MODE     one focal length, one aperture, one light direction, one light quality
                    — beats "8K ultra detailed masterpiece" every time
ONE OBJECT/SENTENCE attributes adjacent to their noun; counts <= 4 with arrangements
REFERENCES          label by index, state the role, state what to IGNORE
PRODUCT LOCK        composite the real asset; masks are guidance, not clips
NEGATIVES           use the field if it exists (nouns, no negation, <=6 terms);
                    otherwise positive substitution + a Constraints line
TEXT                <= ~25 chars, quoted, no diacritics — or reserve space and set type
SEED                hold it; rewriter off; re-roll 4-8 seeds before you call it done
ONE VARIABLE        one slot per render, same seed, write down the effect
CAP EDITS           3-4 chained edits max, then start from the original
QA AT 100%          glyphs, diacritics, counts, fingers, logo geometry, shadows, reflections
STOP RULE           anything legally/factually/typographically fixed does not get generated
```

*End of dossier. Retrieval date for all `[verified]` claims: 2026-07-29. Re-verify Part 10.2 before
each new project; everything in Part 10.1 should still be true next year.*
