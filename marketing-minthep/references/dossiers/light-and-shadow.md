# Light and Shadow — Research Dossier

## Scope

Physics of light and shadow reduced to numbers a non-expert can specify, and to sentences an image or
video model will actually honour. Covers falloff, hardness geometry, the six-shadow taxonomy, measured
ratios, portrait and product setups with azimuth/elevation/distance, subtraction, colour temperature,
natural-light signatures, forensic detection of impossible lighting, and prompt translation. Excludes
composition, lens optics, retouching, and colour grading (other files).

---

## 1. The four variables. Everything else is a consequence.

Every lighting decision in this dossier collapses to four independent inputs. If a brief specifies these
four, the look is determined. If it specifies adjectives instead, the look is a lottery.

| # | Variable | Unit | Controls | Read it off the image by |
|---|---|---|---|---|
| 1 | **Apparent angular size** of the source, seen from the subject | degrees | shadow-edge softness, catchlight size, specular width | measuring the catchlight as a fraction of the iris |
| 2 | **Direction** — azimuth + elevation | degrees | which planes are lit, shadow pattern, where cast shadows fall | finding the terminator; its surface normal points at the light |
| 3 | **Distance** from source to subject | metres | falloff across the subject, subject-to-background separation | comparing background density to subject density |
| 4 | **Subtraction** — what you take away | stops removed | shadow density, edge definition, "expensive" look | how black the shadow side goes and whether edges hold |

Intensity/power is *not* on this list. Power only sets exposure. Two lights of identical power at
identical positions but different sizes produce completely different images; two lights of different
power at the same position and size produce the same image at different apertures.

**Working rule for the skill:** never emit a lighting instruction that fails to pin down at least
variables 1, 2 and 4.

---

## 2. Inverse-square law: worked falloff and the near-field exception

### 2.1 Formula

Irradiance from a point source: `E ∝ 1/d²`. In photographic stops:

```
Δstops = 2 · log2(d2 / d1)          # equivalently log2((d2/d1)²)
d2/d1  = 2^(Δstops / 2)
```

| Distance multiplier | Δ stops | Distance multiplier | Δ stops |
|---:|---:|---:|---:|
| ×1.09 | 0.25 | ×2.00 | 2.0 |
| ×1.19 | 0.5 | ×2.38 | 2.5 |
| ×1.30 | 0.75 | ×2.83 | 3.0 |
| ×1.41 (√2) | 1.0 | ×4.00 | 4.0 |
| ×1.68 | 1.5 | ×5.66 | 5.0 |
| ×1.83 | 1.75 | ×8.00 | 6.0 |

Memorise one pair: **×1.41 = 1 stop, ×2 = 2 stops.**

### 2.2 The consequence nobody teaches: background separation is set by light *position*, not light power

Hold the subject exposure constant. Hold the subject-to-background gap at 2.0 m. Move only the light.

| Light→subject | Light→background | Ratio | Background falls | What you see on a mid-grey seamless |
|---:|---:|---:|---:|---|
| 0.5 m | 2.5 m | 5.00 | **−4.6 stops** | reads black; product looks cut out |
| 0.8 m | 2.8 m | 3.50 | −3.6 stops | near-black with a faint gradient |
| 1.0 m | 3.0 m | 3.00 | −3.2 stops | deep charcoal; strong separation |
| 1.5 m | 3.5 m | 2.33 | −2.4 stops | dark grey; clean separation |
| 2.0 m | 4.0 m | 2.00 | −2.0 stops | mid-dark grey |
| 3.0 m | 5.0 m | 1.67 | −1.5 stops | grey, subject still separates |
| 5.0 m | 7.0 m | 1.40 | −1.0 stop | grey reads as "the same room" |
| 10.0 m | 12.0 m | 1.20 | −0.5 stop | background merges with subject |

**The 3-stop swing between the top and bottom row costs nothing and uses no extra light.** This is the
one number that buys three stops for free in studio work: *if the background is too bright, move the key closer and
lower its power; if the background is too dark, move the key back and raise its power.*

Practitioner phrasing of the same fact: "Light Close for sharper shadows, bigger catchlights and darker
backgrounds. Light Far for softer shadows, smaller catchlights and brighter backgrounds."
(source: https://www.joeedelman.com/inverse-square-law, retrieved 2026-07-29)

### 2.3 Falloff *across* the subject

| Scenario | Near plane | Far plane | Δ stops | Consequence |
|---|---:|---:|---:|---|
| Face, key close | nose 0.80 m | ear 0.95 m | 0.50 | strong modelling; ear reads as shadow |
| Face, key far | nose 2.50 m | ear 2.65 m | 0.17 | flat; ear same value as nose |
| Two people in depth, key close | 1.00 m | 1.50 m | 1.17 | back person visibly under-lit |
| Two people in depth, key far | 3.00 m | 3.50 m | 0.44 | acceptable for a group |
| Product 25 cm deep, key at 0.6 m | 0.60 m | 0.85 m | 1.00 | back of the product a full stop down |
| Product 25 cm deep, key at 2.0 m | 2.00 m | 2.25 m | 0.34 | even; correct for e-comm |

**Decision rule:** groups and deep products get a *far* light; single faces and cut-out looks get a *close*
light. "Move the light back" is the fix for uneven group exposure, not "add another light."

### 2.4 Where the law breaks — and the honest disagreement

The inverse-square law is exact for point sources only. Wikipedia states the usable threshold precisely:
"when the size of the light source is less than one-fifth of the distance to the subject, the calculation
error is less than 1%," citing A. Ryer, *The Light Measurement Handbook* (1997)
(source: https://en.wikipedia.org/wiki/Inverse-square_law, retrieved 2026-07-29).

So a 1.2 m octabox obeys the law within 1% only beyond **6.0 m** — which is never, in a beauty studio.
Inside that distance an extended source falls off more slowly. A cinematography source states the limiting
case: "If the light source is significantly larger than the distance d to the light source, the light will
fall off as 1/d — in other words: slower than the Inverse Square Law predicts," and repeats the 5×
rule of thumb: "a large source will start to follow the Law above distances equal to about five times the
largest side of the source, so a 4ft Kinoflo would obey the Law very closely after about 20ft"
(source: https://neiloseman.com/inverse-square-law/, retrieved 2026-07-29).

| Regime | Condition | Falloff exponent | Practical note |
|---|---|---|---|
| Far field | d > 5 × source width | `1/d²` (2 stops per doubling) | textbook behaviour |
| Transition | source width < d < 5 × width | between `1/d¹` and `1/d²` | most real studio distances live here |
| Near field | d < source width | approaches `1/d¹` (1 stop per doubling) | large frame very close: nearly even |

**Disagreement, stated plainly.** Practitioner sources split. One camp says the deviation is irrelevant:
the law "applies regardless of modifier type" and doubling distance quarters intensity "or near as damn
it" (sources: joeedelman.com; neiloseman.com, retrieved 2026-07-29). The other camp says photometric
data for large soft sources shows measurably slower near-field falloff. **Both are usable.** Resolution
for this skill: use the inverse-square table to *predict direction and rough magnitude*, and treat the
predicted number as an over-estimate of falloff whenever the source is big and close. When background
separation is critical, meter it; do not compute it.

---

## 3. Hardness is apparent angular size. Nothing else.

### 3.1 The only formula that matters

```
θ  = 2 · arctan( W / (2·D) )        # apparent angular size of a source of width W at distance D
```

Hardness is a monotone function of θ alone. A source's physical size is irrelevant except as an input to
θ. Wikipedia lists three contributing features — "the size of its surface, its distance from the object,
and the thickness of its diffusion material" (source: https://en.wikipedia.org/wiki/Hard_and_soft_light,
retrieved 2026-07-29) — but the first two are just the numerator and denominator of the same fraction,
and the third only changes the *effective* emitting area. The practitioner formulation is blunter:
"Apparent light size is what matters"
(source: https://strobist.blogspot.com/2007/07/lighting-102-unit-21-apparent-light.html ◐, retrieved 2026-07-29).

### 3.2 Angular size of real sources (computed)

| Source | Width | Distance | θ | Class |
|---|---:|---:|---:|---|
| Sun, clear sky | — | 1 AU | **0.53°** | brutally hard |
| Bare speedlight head (~7 cm) | 0.07 m | 2.0 m | 2.0° | hard |
| 18 cm ("7-inch") reflector | 0.18 m | 1.5 m | 6.9° | hard, punchy |
| 60 cm softbox | 0.60 m | 2.0 m | 17.1° | medium |
| 120 cm octabox | 1.20 m | 4.0 m | 17.1° | **medium — identical to the 60 cm at 2 m** |
| 55 cm beauty dish | 0.55 m | 0.8 m | 37.9° | soft with a defined edge |
| 60 cm softbox | 0.60 m | 1.0 m | 33.4° | soft |
| 120 cm octabox | 1.20 m | 2.0 m | 33.4° | soft |
| 120 cm octabox | 1.20 m | 1.0 m | **61.9°** | very soft |
| 100×200 cm strip, long axis | 2.00 m | 1.0 m | 90° / 28° across | wrapping vertically, narrow horizontally |
| 120×240 cm frame | 2.40 m | 1.5 m | 77° / 44° | window-like |
| North window 150×120 cm | 1.50 m | 1.5 m | 53° | soft directional |
| Overcast sky | — | — | ~180° dome | shadowless, formless |

Note rows 4/5 and 7/8: **a 120 cm box at 4 m is exactly as hard as a 60 cm box at 2 m.** This kills the
most common lighting myth in one line.

### 3.3 Penumbra geometry — why θ produces softness

For a source of width `S`, an occluding edge at distance `D` from the source, and a receiving surface at
distance `d` beyond the occluder, similar triangles give the penumbra (half-shadow) width on the receiver:

```
P = S · d / D              # exact for a flat source parallel to the receiver
P ≈ d · tan(θ)             # equivalent form using angular size
```

Umbra = the region from which *no part* of the source is visible (full darkness).
Penumbra = the region from which *part* of the source is visible (gradient).
Antumbra = beyond the point where the occluder no longer covers the source (source visible as a ring;
irrelevant in photography, relevant when a small object is backlit by a huge frame — it stops casting
a shadow at all).

### 3.4 Worked penumbra numbers — this is what "soft" means in millimetres

A nose tip sits roughly **3 cm** in front of the cheek it casts onto.

| Key source | θ | Penumbra on the cheek | Visible result |
|---|---:|---:|---|
| Sun (0.53°) | 0.53° | **0.28 mm** | razor line; the shadow reads as a graphic shape |
| Bare speedlight at 2 m | 2.0° | 1.0 mm | crisp, hard, unforgiving |
| 18 cm dish at 1.5 m | 6.9° | 3.6 mm | defined edge, slight bloom |
| 120 cm octa at 3.0 m | 22.6° | 12 mm | readable loop shadow with a soft edge |
| 120 cm octa at 1.0 m | 61.9° | **36 mm** | no shadow *edge* at all — a 3.6 cm gradient across a ~10 cm cheek |
| Overcast sky | ~180° | undefined | no nose shadow; only under-chin occlusion |

**That last row is the definition of "soft":** at 1 m, a 1.2 m octabox does not produce a soft-edged nose
shadow — it produces *no nose shadow*, because the gradient is wider than the feature. If you want a
visible-but-gentle loop, the same box has to go to 2.5–3.5 m.

Shadow-length note for cast shadows on the ground: a hand held **1.0 m** above the floor in direct sun
gets a **9.3 mm** penumbra (`1000 mm × tan 0.53°`); a person's head at **1.7 m** gets **16 mm**. This is why
noon shadows look hard at the feet and slightly soft at the head — and why a generated image with a
*uniformly* hard-edged full-body shadow is subtly wrong.

### 3.5 The contact-shadow law (derived, and the most useful line in this document)

As `d → 0`, `P → 0`, for **any** value of `S`.

> **Contact-shadow law:** at the point where an object touches a surface, the penumbra width is zero and
> the occlusion is total, regardless of how large or soft the light is. Every object under every light
> has a hard, dark shadow line exactly at its contact point.

Corollaries the skill should enforce:

- A 3×3 m diffusion frame still produces a hairline-crisp black seam under a bottle.
- "Soft light means no shadows" is false. Soft light means *wide-penumbra cast shadows plus a
  full-density contact shadow.*
- A shadow that fades *out* at the contact point and gets darker further away is physically impossible.
  This is the #1 tell of a generated product image.

### 3.6 Catchlight size is a direct readout of θ — and therefore a cross-check on shadow hardness

The anterior cornea behaves as a convex mirror; normal radius of curvature is **7.5–8.0 mm**
(source: https://www.ncbi.nlm.nih.gov/books/NBK580516/ ◐, retrieved 2026-07-29). A convex mirror's focal
length is `R/2 ≈ 3.9 mm`. For a source much farther away than that, the reflected image height is:

```
catchlight diameter ≈ (R/2) · θ_radians ≈ 3.9 mm · θ_rad
fraction of iris     ≈ 3.9 · θ_rad / 12 mm ≈ 0.33 · θ_rad      # visible iris ≈ 11–12 mm
```

| θ | θ (rad) | Catchlight Ø | % of iris width | Matching penumbra at 3 cm gap |
|---:|---:|---:|---:|---:|
| 0.53° (sun) | 0.0093 | 0.036 mm | 0.3% | 0.28 mm |
| 2° | 0.035 | 0.14 mm | 1.1% | 1.0 mm |
| 10° | 0.175 | 0.68 mm | 5.7% | 5.3 mm |
| 20° | 0.349 | 1.4 mm | 11% | 11 mm |
| 35° | 0.611 | 2.4 mm | 20% | 19 mm |
| 62° | 1.08 | 4.2 mm | **35%** | 36 mm |
| 90° | 1.57 | 6.1 mm | 51% (clipped by the cornea) | 60 mm |

> **The catchlight/shadow consistency test.** Catchlight size and shadow-edge width are two readouts of
> the *same* number. A generated portrait with a razor-hard nose shadow **and** a catchlight filling a
> third of the iris is physically impossible. So is a portrait with a 3 cm soft gradient under the nose
> and a pinpoint sparkle catchlight. This test takes five seconds and catches a large fraction of AI
> portrait failures.

### 3.7 What diffusion actually does

Diffusion does not "soften light." It converts a small source into a larger one by making the diffuser
itself the emitting surface. Therefore:

- Softness gained = the diffuser's angular size, **not** the diffuser's grade.
- A 1/4-grade diffusion 5 cm in front of a bare bulb barely changes θ. The same material on a 1.2 m frame
  1 m from the subject changes everything.
- Grade (1/8 → Full → Opal) controls *evenness and transmission loss*, not hardness. Typical loss ranges
  from a fraction of a stop to ~2 stops; measure per material.
- Double-diffusing (two layers, 10–20 cm apart) removes the hot centre and makes the frame's *whole*
  surface emit evenly — which is what actually makes a source behave like its full stated size.

### 3.8 Feathering — with numbers

Feathering means aiming the source so the subject sits in the *edge* of the beam rather than the hot
centre. Practical spec: rotate the box **20–45°** away from the subject so that the near edge of the box
points past the subject, and the subject is illuminated by the box's soft edge.

| Feather amount | Effect on the subject | Effect on the background |
|---|---|---|
| 0° (aimed at subject) | brightest, flattest, most spill | most spill onto background |
| 20° | ~1/3–2/3 stop down, gentler transition | noticeably less spill |
| 45° | 1–1.5 stops down, strong gradient across the subject | large spill reduction |
| Aimed past entirely (edge-only) | 2+ stops down, very gradual, "expensive" | minimal spill |

Feathering is the cheapest way to make one light behave like two: the subject gets a gradient, and the
background stops receiving spill, which sharpens the inverse-square separation from §2.2.

---

## 4. The six shadows. Name them separately or AI will merge them.

| # | Shadow | Physical cause | Where it appears | Appearance | AI failure rate | Words that produce it |
|---|---|---|---|---|---|---|
| 1 | **Form shadow** (core shadow) | surface normal turning away from the light; Lambert's cosine | on the object itself, on the side away from the key | gradient, no defined edge, widest on curved forms | low — models handle this well | "the light wraps around the cheekbone and falls into a gradual gradient on the jaw" |
| 2 | **Terminator** | the boundary of the form shadow | the band between lit and unlit on the object | a *band*, not a line; width = f(θ) | medium — often too narrow for the stated source | "the transition from light to shadow across the cheek is a 3 cm gradient, not a line" |
| 3 | **Cast shadow** | the object occluding light from another surface | on the ground, wall, or a neighbouring object | umbra + penumbra; edge softens with distance from contact | **high — direction disagreement is the #1 error** | "cast shadows fall to camera-right, away from the key" |
| 4 | **Contact / occlusion shadow** | zero-gap occlusion (§3.5) | the seam where object meets surface | hard, dark, thin; densest of all shadows | **highest — most often missing** | "a dark hard-edged contact line where the base meets the marble, densest at the seam" |
| 5 | **Ambient occlusion** | reduction of *ambient* (skydome / bounce) light in creases and corners | nostrils, ear folds, under collars, inside corners, between fingers, under a cap's brim | soft darkening independent of key direction | high — AI renders creases too bright | "soft darkening in the creases: nostrils, ear folds, the seam of the collar" |
| 6 | **Reflected-light fill** | bounce arriving *into* the shadow from nearby surfaces | inside the form shadow, near a bright adjacent surface | a secondary lift inside shadow, coloured by the bouncing surface | high — shadows come out neutral grey | "the shadow side of the jaw is lifted by warm bounce from the wooden table" |

### 4.1 Terminator width: how to specify it in words

The band from §3.4 in language a model can act on. Reference gap: nose→cheek, ~3 cm.

| Penumbra | Say this | Implies θ | Implied source |
|---:|---|---:|---|
| < 1 mm | "razor-sharp shadow edge, no transition" | < 2° | sun, bare flash, fresnel spot |
| 1–4 mm | "crisp shadow edge with a hairline of transition" | 2–8° | small dish, gridded head |
| 5–15 mm | "clearly defined shadow edge with a visible soft border" | 10–28° | mid softbox at working distance |
| 15–40 mm | "soft gradient instead of a shadow edge" | 28–65° | large box close |
| > 40 mm | "no shadow edge; form reads only as a slow gradient" | > 65° | frame/tent, overcast |

Terminology warning: in rendering, **"shadow terminator" names an artifact** — "the abrupt interruption
of the light's smooth cosine falloff at geometric horizons" caused by shading normals disagreeing with
geometric normals (source: https://research.dreamworks.com/wp-content/uploads/2020/08/talk_shadow_terminator.pdf,
retrieved 2026-07-29). In photography and painting, "terminator" simply names the light/shadow boundary
on a form. Diffusion-model images do not have the rendering artifact; they have a *plausibility* problem
in the photographic sense. Do not put the word "terminator" in a prompt — describe the band's width.

### 4.2 Ambient occlusion — the missing 5%

AO in rendering "simulates contact and corner shadows: areas that receive less ambient light are
darkened" and in real-time engines is approximated in screen space (SSAO, HBAO, GTAO)
(sources: https://www.danthree.studio/en/glossary/ambient-occlusion ◐;
https://superrendersfarm.com/article/ambient-occlusion-explained-ssao-hbao-gtao-2026 ◐, retrieved 2026-07-29).

It matters here because AO is *direction-independent*. It is the reason a real photograph looks
"seated" even in flat overcast light. Generated images routinely get key-driven shadows roughly right
and AO completely wrong: bright nostrils, glowing ear canals, no darkening between fingers, a watch
strap with no shadow under it, fabric seams with no depth. The fix is a short explicit clause,
because the model has no geometry to occlude from — it only has your words.

### 4.3 Reflected fill: shadows are never neutral

Shadow-side colour = the colour of whatever is bouncing into it. Concrete, checkable cases:

| Situation | Shadow side is lit by | Shadow colour vs key | Δ mired (approx) |
|---|---|---|---:|
| Clear-sky sunlight outdoors | blue skylight only | markedly cooler | key ≈5400 K (185 mired) vs skylight ≈10000 K (100 mired) → **85 mired cooler** |
| Sunlight + red-brick wall | skylight + warm brick bounce | warmer than the sky case, still cooler than key | +20 to +40 mired vs pure skylight |
| Studio, white cyc | white bounce | neutral | ~0 |
| Studio, black flags on both sides | almost nothing | neutral but very dark | ~0 |
| Restaurant, tungsten practicals + window | mixed | split warm/cool across the same face | 100–140 mired across the face |
| Grass field, midday | green upward bounce | green-shifted shadows on the underside of the chin | off-locus green (Duv), not a Kelvin shift |

> **The blue-shadow test.** A generated "sunny day" image whose shadows are neutral grey is wrong. In
> clear daylight, shadows receive *only* skylight and must read cooler than the sunlit side by a large,
> visible margin. Grey shadows in bright sun are one of the most reliable generated-image tells, and one
> of the easiest to fix with a single clause.

---

## 5. Lighting ratios, expressed properly

### 5.1 The definitional fight — real, and worth knowing

The American Society of Cinematographers defines lighting ratio as **`(key+fill):fill`**, or
`(key+Σfill):Σfill` where Σfill is the sum of all fill lights
(source: https://en.wikipedia.org/wiki/Lighting_ratio, retrieved 2026-07-29). The same page gives the
worked example: "Key light of 200 footcandles + fill light of 100 footcandles = (200 + 100):100" = 3:1.

But the same page also states the stop conversion as "2 to the power of the difference in f stops is
equal to the first factor in the ratio," and gives 2 stops → 4:1, 3 stops → 8:1. That conversion is the
**`key:fill`** reading, not the ASC reading. So a single reference source contains both conventions.
Meanwhile a large share of working photographers set "3:1" by putting the key at 3× the fill's *power*.

| Spoken | Reading A: key power ÷ fill power | Measured lit:shadow under A | Δ stops (A) | Reading B: ASC (key+fill):fill | Δ stops (B) | Ambiguity |
|---|---|---:|---:|---|---:|---:|
| 1:1 | 1÷1 | 2:1 | 1.00 | 1:1 | 0.00 | **1.0 stop** |
| 2:1 | 2÷1 | 3:1 | 1.58 | 2:1 | 1.00 | 0.58 |
| 3:1 | 3÷1 | 4:1 | 2.00 | 3:1 | 1.58 | 0.42 |
| 4:1 | 4÷1 | 5:1 | 2.32 | 4:1 | 2.00 | 0.32 |
| 8:1 | 8÷1 | 9:1 | 3.17 | 8:1 | 3.00 | 0.17 |
| 16:1 | 16÷1 | 17:1 | 4.09 | 16:1 | 4.00 | 0.09 |

**Verdict for this skill: never write a ratio as the primary instruction. Write stops.** "The shadow side
is 1.5 stops under the lit side" is unambiguous, meterable, and translatable to any prompt. Keep the
ratio only as a familiar label in parentheses for human readers.

A third convention exists: metering *reflected* light off the face with a spot meter, which folds skin
reflectance into the number. Useful on set, useless as a written spec, because identical lighting yields
different numbers on different skin.

### 5.2 What each level actually looks like

| Δ stops | Ratio label (ASC) | Shadow side reads as | Fine texture on the shadow side | Canonical use |
|---:|---|---|---|---|
| 0.0 | 1:1 | invisible; form carried only by specular falloff and edges | full | e-comm packshot, pharma, ID, flat lay |
| 0.5 | 1.4:1 | a faint suggestion of a plane change | full | high-key beauty, "clean skincare" |
| 1.0 | 2:1 | present, obviously a shadow, fully legible | full | commercial soft; safest default for faces |
| 1.6 | 3:1 | a real shadow with weight | mostly retained | editorial portrait default |
| 2.0 | 4:1 | dramatic; the eye reads two distinct zones | lost on deep skin, retained on pale | fashion, character portrait, "premium" |
| 3.0 | 8:1 | a *shape*, not a surface | gone | noir, spirits, automotive, drama |
| 4.0+ | 16:1+ | black; the form is defined only by rim/edge | gone | silhouette-adjacent, poster graphics |

### 5.3 Skin-tone correction — a real effect, honestly bounded

Skin's *surface* (specular) reflectance is only about 4–7% across a wide spectral range; the rest of what
a camera records is diffuse light that entered the skin and scattered back out, and that component is
strongly modulated by melanin, "ranging from very low in light complexioned Caucasian skin (type I), to
very high in black African skin (type VI)"
(sources: https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=918494 ◐;
https://www.sciencedirect.com/science/article/pii/S0022202X15414836 ◐, retrieved 2026-07-29).

Consequence: at a fixed key:fill in stops, deeper skin loses shadow-side texture sooner, because the same
stop reduction lands on a lower base luminance and falls below the point where texture survives an 8-bit
delivery file.

| Skin tone | Adjust contrast by | Additional move |
|---|---|---|
| Very light | +0.5 stop more contrast is safe | watch highlight clipping on the lit cheek instead |
| Mid | baseline | — |
| Deep | **−0.5 to −1.0 stop of contrast** | add a *specular* source (silver bounce, small hard kicker) rather than more diffuse fill, to keep the sheen that describes the form |

[UNVERIFIED — exact integrated visible-band reflectance figures per Fitzpatrick type. The mechanism and
direction are confirmed above; a citable table of total reflectance by type is not. To verify I would need
a colour-science paper reporting integrated diffuse reflectance (400–700 nm) per Fitzpatrick or ITA° class.
Do not publish a figure like "dark skin reflects X%" without it.]

### 5.4 Measuring a ratio without a meter

1. Set exposure for the lit side. 2. Turn the key off. 3. Meter the shadow side alone. The difference in
stops *is* the ratio, no arithmetic.

For AI work there is no meter. Substitute test: **count the distinct tonal steps between the lit cheek and
the shadow cheek.** One barely-there step ≈ 1 stop. A clear step with texture on both sides ≈ 1.5–2 stops.
A step where one side has no texture ≈ 3+ stops.

---

## 6. Classic portrait patterns with real geometry

### 6.1 Coordinate convention (state once, reuse everywhere)

- **Azimuth 0°** = the camera–subject axis, measured at the subject's head. Positive = toward camera-left
  as the viewer sees it. 90° = directly to the subject's side. 180° = directly behind.
- **Elevation 0°** = source centre at eye level. Positive = above.
- **Distance** = source centre to the subject's nose.

### 6.2 The pattern table

| Pattern | Azimuth | Elevation | Modifier + distance | Key:shadow | Signature shadow | Catchlight | Fails when |
|---|---:|---:|---|---:|---|---|---|
| **Flat / on-axis** | 0° | 0–10° | ring or box behind camera, 1.0–1.5 m | 0–0.5 st | none; halo shadow on a near wall | dead-centre ring or dot | you need form; it erases structure |
| **Butterfly / Paramount** | 0–10° | **40–60°** | beauty dish or octa, 0.9–1.3 m, tilted down | 1–2 st | small symmetrical shadow *under* the nose | 12 o'clock, both eyes | the shadow reaches the upper lip (light too high) |
| **Loop** | **25–45°** | **25–40°** | 90–120 cm octa, 1.5–2.5 m | 1–2 st | nose shadow loops down onto the cheek, **does not touch** the cheek shadow | 10–11 or 1–2 o'clock | the loop merges with the cheek shadow (that is Rembrandt) |
| **Rembrandt** | **45–60°** | **40–55°** | 60–90 cm box or dish, 1.2–2.0 m | 2–3 st | nose + cheek shadows join, leaving a lit triangle under the shadow-side eye | small, high, one side | triangle too big, or absent |
| **Split** | **85–95°** | 0–10° | strip or gridded box, 1.0–1.5 m | 3–5 st | face divided vertically; only one eye lit | one eye only | you needed both eyes readable |
| **Short light** | key on the side of the face turned **away** from camera | as pattern | as pattern | as pattern | more of the face in shadow → face reads narrower | — | over-narrows an already thin face |
| **Broad light** | key on the side turned **toward** camera | as pattern | as pattern | as pattern | more of the face lit → face reads wider | — | flattens structure |
| **Clamshell** | key 0–15°, fill 0° | key **+30 to +45°**, fill **−30 to −45°** | key 60–90 cm dish at 0.8–1.5 m; fill white board at chest height | **0.5–1.0 st** | almost none; slight under-chin lift | **two**: large at 12, thin at 6 | reads as "no lighting" if the ratio hits 0 |
| **Rim / kicker** | **110–150°** | 10–30° | gridded strip, 1.0–2.0 m, flagged off the lens | rim +0 to +1.5 st **over** key | bright edge on hair, shoulder, jaw | small, far edge of the eye, or absent | flare into the lens; rim brighter than the face |
| **Hair light** | **150–180°** | **45–70°** | small gridded box or dish above and behind | +0.5 to +1.5 st over key | separation across the crown | none | it reaches the nose tip (angle too shallow) |
| **Background light** | behind the subject, aimed at the background | 0–45° | bare head or reflector, gridded, 0.3–0.8 m from the sweep | see §7.4 | pool or gradient behind the subject | none | it spills onto the subject's back |

Verified anchors: butterfly's nose shadow "should not reach the upper lip"; loop "places the light at
roughly a 45-degree angle" producing "a subtle shadow that loops around the side of the nose"; split
"divid[es] the face exactly in half"
(source: https://fstoppers.com/lighting/getting-started-portrait-lighting-4-classic-patterns-explained-901256,
retrieved 2026-07-29). Rembrandt: "the key light is placed high and to one side at the front, and the fill
light or a reflector is placed half-height and on the other side at the front, set to about half the power
of the key light" (source: https://en.wikipedia.org/wiki/Rembrandt_lighting, retrieved 2026-07-29).
Clamshell: "Set the lower fill about one stop weaker than the key — a 2.5:1 ratio suits most headshots,"
with the dish "close to (2.5-5ft), and slightly in front of, the model"
(sources: https://www.photographyshark.com/blog/clam-shell-lighting/ ◐;
https://www.behindtheshutter.com/advanced-beauty-lighting/ ◐, retrieved 2026-07-29).

### 6.3 The Rembrandt triangle: geometry and the size test

The triangle is the residue of three boundaries meeting:

1. **Above:** the shadow cast down by the brow ridge and eye socket.
2. **Medially:** the shadow cast sideways by the nose.
3. **Laterally:** the form-shadow terminator wrapping around the cheekbone.

When (1) and (2) *almost* meet but leave a lit gap, you get the patch. The size test, as stated in the
reference literature: "The triangle should be no longer than the nose and no wider than the eye"
(source: https://en.wikipedia.org/wiki/Rembrandt_lighting, retrieved 2026-07-29).

| Symptom | Diagnosis | Fix |
|---|---|---|
| Triangle wider than the eye | key too frontal (azimuth too low) | swing the key 5–10° further around |
| Triangle longer than the nose | key too low | raise the key 5–10° |
| No triangle, shadows merged | key too far around or too high | reduce azimuth or elevation by 5–10° |
| Triangle present but formless | source too big / too close | move the key back 0.5–1.0 m |

**Sensitivity, computed:** at 1.2 m working distance, moving the light **10 cm** subtends
`arctan(0.10/1.2) = 4.8°`. A hand's-width move flips the pattern. This is why the pattern is described as
requiring "careful, incremental adjustments," and why a prompt that says only "Rembrandt lighting" is a
coin flip — the triangle must be described.

### 6.4 Short vs broad — and where the folklore starts

The narrow side of a turned face is the side away from camera. Lighting it (**short light**) throws the
larger near cheek into shadow → narrower face. Lighting the near, larger side (**broad light**) → wider
face. That part is geometry and is not in dispute. What follows is not:

| Face | Conventional recommendation | Status |
|---|---|---|
| Round / full | short light + Rembrandt or split; higher ratio | **UNVERIFIED FOLKLORE** |
| Long / narrow | broad light + butterfly or loop; lower ratio | **UNVERIFIED FOLKLORE** |
| Square / strong jaw | loop at 35–45°, soft, 1–1.5 stops | **UNVERIFIED FOLKLORE** |
| Older subject | large soft source, low elevation 25–35°, 1 stop ratio | **partly mechanical** — low elevation plus wide penumbra measurably reduces the depth of texture shadows |
| Glasses | raise elevation past 45° or azimuth past 40° | **mechanical** — it moves the source out of the lens's family of angles (§8.2) |

[UNVERIFIED — the face-shape mapping is repeated in effectively every portrait guide surveyed, and I found
**no** controlled study measuring perceived attractiveness, competence, or trust as a function of lighting
pattern × face morphology. Treat it as a professional convention clients expect and a sensible starting
point, not as evidence. To verify I would need a psychophysics or consumer-perception study with
randomised pattern assignment and rated outcomes.]

### 6.5 Catchlight positions — convention, not law

| Setup | Catchlight, right eye as the viewer sees it |
|---|---|
| Key camera-left 40° / +35° | 10–11 o'clock, upper-outer |
| Butterfly | 12 o'clock, symmetrical in both eyes |
| Clamshell | large at 12 plus a thin crescent at 5–7 |
| Split at 90° | one eye has a catchlight at 9; the other has none |
| Ring light | perfect ring, dead centre |
| Window at 60° | large soft rectangle, off-centre, often with visible mullion bars |
| Sun | one pinpoint, ~0.3% of iris width |

"Catchlights must be at 10 or 2 o'clock" is a **consequence** of a 30–45° key, not an independent rule —
butterfly and ring light violate it by construction and are used constantly. What *is* a real rule: **both
eyes must show catchlights at the same clock position** (allowing for head turn and eye convergence).
Mismatched clock positions between the two eyes means two lights, or a fabrication.

---

## 7. Subtraction: negative fill, flags, gobos, cookies

### 7.1 Why subtraction is the professional move

Adding a light adds a second shadow family, a second catchlight, a second colour and a second falloff
curve to reconcile. Subtracting light adds nothing to reconcile. One key plus two black flags is more
controlled, faster and cheaper than three heads, and it is what most high-end beauty and spirits work
actually is.

The physical bound, stated honestly: **negative fill can only remove light that was already arriving.**
Its maximum effect equals the ambient/bounce contribution on that side.

| Environment | Bounce on the shadow side | Max effect of a black flag |
|---|---|---|
| Black-walled studio / black cyc | negligible | **~0 stops — the flag does nothing** |
| Mid-size grey studio | moderate | 0.5–1 stop |
| Small white room, white ceiling | large | 1–2 stops |
| Open shade with a white building opposite | large | 1–2 stops |
| Outdoors, dark surroundings, open field | small | 0.3–0.7 stop |

So the correct instruction is never "add negative fill" alone — it is **"add negative fill *and* state the
environment,"** because in a black studio the same flag is a no-op. This is also why "negative fill" as a
bare prompt token does almost nothing: the model has no room to remove light from.

### 7.2 The tool table

| Tool | What it is | Typical size | Placement | Produces |
|---|---|---|---|---|
| **Negative fill / black card** | matte black absorber | 60×90 cm to 120×240 cm | 0.3–1.0 m from the subject, shadow side, parallel to the face | deeper shadow side, defined jaw and cheek edge, sculpted look |
| **Flag / cutter** | opaque blocker between light and subject | 30×45 cm to 120×120 cm | 0.3–1.5 m from the light | hard-edged control: light off the background, the lens, the top of the head |
| **Teaser / finger / dot** | small flags | 5–30 cm | close to the light | removal of one specific hotspot |
| **Scrim / net** | wire mesh screen | any | in front of the fixture | "reduce the intensity of the light without changing its quality"; single ≈ 0.5 stop, double ≈ 1 stop (verify per net) |
| **Silk / diffusion frame** | translucent fabric | 60 cm to 6 m | between light and subject | enlarges θ (§3.7) |
| **Gobo** | patterned stencil at the fixture's optics; from "go before optics" | fixture-sized | in the gate | hard-edged projected pattern — window bars, blinds, foliage |
| **Cookie / cucoloris** | board with irregular cut-outs, used **farther from the light** than a gobo, so it "generally produce[s] softer edges" | 60×90 cm typical | 1–3 m from the light | dappled organic light — foliage, water, lived-in room texture |

(sources: https://nofilmschool.com/the-gaffers-dictionary ◐; https://en.wikipedia.org/wiki/Cucoloris ◐;
https://www.videomaker.com/how-to/lighting/lighting-equipment-lighting/your-one-stop-guide-for-all-lighting-terminology/ ◐,
retrieved 2026-07-29)

**Nomenclature warning:** in theatre and moving-light fixtures "gobo" means the patterned disc; on US film
sets "gobo" is also used loosely for any light-blocking board, while "cookie" means specifically the
irregular dappling board. Never put either word in a prompt — describe *the pattern that lands on the
surface*.

### 7.3 Subtraction-first checklist

Before adding a second light, in this order:

1. **Feather the key** (§3.8) — free, 0.5–1.5 stops of control.
2. **Move the key** — up to 3 stops of background change (§2.2).
3. **Negative fill on the shadow side** — 0.5–2 stops (§7.1).
4. **Flag the key off the background** — recovers separation without touching the subject.
5. **White or silver bounce as fill** instead of a second head — inherits the key's colour and direction,
   so there is nothing to reconcile.
6. Only then add a head, and only for **rim, hair or background** — never a second frontal key.

### 7.4 Gradient / sweep backgrounds — derived formula

For a background light at perpendicular distance `a` from the background, hot spot directly opposite,
falloff at distance `x` measured along the background from the hot spot:

```
Δstops(x) = log2( 1 + (x/a)² )
```

| `a` (light→background) | at x = 0.5 m | at x = 1.0 m | at x = 1.5 m |
|---:|---:|---:|---:|
| 0.3 m | 1.92 st | 3.60 st | 4.68 st |
| 0.6 m | 0.75 st | 1.92 st | 2.86 st |
| 1.2 m | 0.22 st | 0.76 st | 1.46 st |
| 2.4 m | 0.06 st | 0.22 st | 0.51 st |

Read it as a recipe: a dramatic 3-stop-plus vignette inside one metre requires the background light within
~30 cm of the sweep; an almost-even light grey with a hint of gradient requires it beyond 1.2 m. This one
formula replaces all "move it until it looks right" advice.

---

## 8. Product and material lighting — real geometry

### 8.1 Material decides everything. Sort the product first.

| Material class | What the camera records | Light the... | Key move | Killer detail |
|---|---|---|---|---|
| **Matte opaque** (paper, matte plastic, unglazed ceramic, fabric, bread) | diffuse reflection ∝ cos(angle) | **surface** | direction and ratio | contact shadow; texture needs a raking light at 60–80° azimuth |
| **Semi-gloss opaque** (soft-touch plastic, satin card, painted metal) | diffuse + a broad specular lobe | surface + one controlled highlight | one big source, feathered | the specular lobe must have a *shape*, not a blob |
| **Gloss opaque** (piano black, gloss carton, phone glass) | almost entirely a mirror image of the room | **the reflection** | build what reflects | any untidy studio object appears in the product |
| **Brushed / anisotropic metal** | a specular *streak* perpendicular to the grain | the reflection, elongated along the grain | strip light parallel to the grain | streak direction must match the visible grain direction |
| **Chrome / polished metal** | a complete mirror image | **the whole environment** | light tent + deliberate dark cards | cross-polarisation does **not** remove metal specular (§8.6) |
| **Clear glass / acrylic** | Fresnel reflection at grazing angles + refraction | **the edges and the background** | dark-field or bright-field (§8.5) | the shadow contains a bright caustic, not a dark blob |
| **Translucent** (frosted glass, silicone, thin plastic, jade, citrus slice, noodle) | subsurface scattering | **from behind** | 120–180° azimuth | glow must be brightest where the material is thinnest |
| **Liquid in a clear vessel** | transmission + surface reflection + a lens effect | **from behind, through the liquid** | backlight + white bounce in front | the liquid's colour saturates where the path length is longest |
| **Wet / condensation** | thousands of tiny specular spheres | **the reflection**, with a small hard source | one hard kicker at 120–150° azimuth | droplets need a *small* source; a big softbox erases them |
| **Food, hot** | matte + wet specular + steam | side-back | 100–150° azimuth, plus a dark background for the steam | steam is invisible without backlight **and** a dark background |

### 8.2 The family of angles — the single concept that makes product lighting learnable

For a given camera position and a given point on a surface, there is exactly one region of space a light
can occupy so that its reflection appears at that point. Construct it by **mirroring the camera about the
surface's tangent plane.** That region is the "family of angles."

Consequences, all mechanical:

| Situation | Family of angles is... | Therefore |
|---|---|---|
| Flat label facing the camera | directly behind the camera | frontal light *always* hotspots the label. Either move the light ≥25–30° off axis, or make it big, even, and intentional |
| Curved bottle shoulder | a band sweeping from behind camera around to the side | the highlight *will* be a band; control its width and gradient, not its existence |
| Cylinder, vertical | a vertical band mirrored to the side | a vertical strip light produces a clean vertical highlight; a square box produces a stubby one |
| Horizontal glossy tabletop | above the camera | the ceiling and the top light appear *in* the table |
| Chrome sphere | the entire sphere of directions | you are photographing the whole room; a tent is mandatory |

> **The reframe that unlocks glass and metal:** you do not light a specular object — you *build the thing
> it reflects*, then place the object so the camera sees that construction in it. "Glass can be tricky to
> light, partly because it's transparent and partly because it reflects everything"
> (source: https://medium.com/@dtravisphoto/lighting-glass-d9ddf81eeb8f, retrieved 2026-07-29).

Fresnel gives the quantitative half: at normal incidence a glass surface reflects only ~4%, but reflectance
climbs steeply past ~70° incidence toward 100%. Therefore **the visible tone of a glass object comes
overwhelmingly from its edges**, where the surface is at grazing incidence to the camera. That is why you
light the edges, not the face.

### 8.3 Light tent / cocoon geometry

| Parameter | Spec | Why |
|---|---|---|
| Tent size | ≥ **3×** the product's largest dimension | so the walls subtend ~180° from the product and no wall edge appears as a hard line |
| Wall material | 2 layers of diffusion, 10–20 cm apart | removes the hot spot so the wall emits evenly (§3.7) |
| Lights | 2–4 heads **outside** the tent, 0.5–1.5 m off, aimed at the walls not the gap | prevents a specular image of the head itself |
| Aperture (camera hole) | as small as the lens allows | the hole is a black rectangle in every reflection |
| **Mandatory correction** | cut 2–4 black cards, each ~10–15% of a wall's area, into the walls at the product's 3 and 9 o'clock | **without them the product has no silhouette** |

That last row is the whole point. A naive light tent produces a shadowless, edgeless, *formless* object.
Professional tent work is 30% adding diffusion and 70% putting black back in.

### 8.4 Strip lights on cylinders — sizing spec

| Goal | Strip height | Azimuth | Distance | Extra |
|---|---|---:|---:|---|
| One clean vertical highlight running full height | **≥1.5× the bottle height** | 100–120° | 0.5–0.8 m | grid or flags so it does not spill on the label |
| Two symmetrical edge highlights | ≥1.5× height, one each side | ±100–120° | 0.5–0.8 m | keep powers within 1/3 stop of each other or it reads lopsided |
| A wrapping gradient rather than a stripe | same | 90–110° | 0.3–0.5 m (larger θ) | add 1 layer of diffusion 10–20 cm in front |
| Label legible on top of that | small top-front source | 0–20° azimuth, +40–60° elevation | 0.8–1.2 m | feather so the hotspot lands **below** the bottle's shoulder |

Rule of thumb for the highlight's *width* on the cylinder: the strip's angular width should land in
**10–25°** for a defined stripe. A 30 cm-wide strip hits that at 0.7–1.7 m. Wider (closer) → the stripe
becomes a wash; narrower (farther) → it becomes a hard line that reads as a defect.

### 8.5 Dark field vs bright field for transparent objects

| | **Bright field** | **Dark field** |
|---|---|---|
| Background | lit, bright | unlit, dark/black |
| Glass body reads | bright / white | dark |
| Glass edges read | **dark** | **bright, glowing** |
| Built with | strong light on a white backdrop or through a translucent backdrop; **black flags** at 3 and 9 o'clock just outside the silhouette | dark background; **white cards or strip lights** at 3 and 9 o'clock just outside the silhouette, with the background flagged off |
| Best for | clear spirits, pale liquids, water, minimal e-comm on white | dark liquids (cola, stout, red wine, soy, coffee), moody hero |
| Precision required | the black flags must sit just outside frame; **2–3 cm of movement visibly changes edge weight** | the background must sit **≥5 stops** under the edge cards or it greys out |
| Room condition | stray light tolerable | "the room needs to be very dark to eliminate any reflections" |

Definitions and setup detail: bright field "lights the background so the glass edges appear dark;
dark-field uses a dark background with light skimming the edges so they glow," and bright field "requires
a lot of black fill cards to ensure you get a dark edge to the glass to reveal its shape"
(sources: https://lindylu10.wordpress.com/2014/01/14/week-12-dark-field-bright-field-lighting/ ◐;
https://medium.com/@dtravisphoto/lighting-glass-d9ddf81eeb8f;
https://www.mattbristow.net/index.php/dark-field-lighting/ ◐, retrieved 2026-07-29). Dark-field
illumination originates in microscopy — "blocking light from the center and providing oblique lighting from
the sides."

Third case worth naming: **the glass's own shadow.** A transparent object does not cast a flat dark shadow.
It casts a shadow with a **bright caustic** where refracted rays converge, usually a lens-shaped or
crescent bright band inside a soft dark outline. A generated glass image with an opaque grey shadow is
wrong, and it is a fast tell.

### 8.6 Cross-polarisation — numbers and the two limits nobody mentions

Setup: linear polarising film over **every** light + a linear polariser on the lens; rotate until
extinction. "One filter eliminates horizontally-polarized light, while the other is rotated to block
increasing amounts of the remaining vertically polarized light until, at 90º, all light is blocked"
(source: https://www.photographyattic.com/blog/2025/11/a-practical-guide-to-cross-polarisation-photography/ ◐,
retrieved 2026-07-29).

| Item | Loss | Source |
|---|---:|---|
| Polarising film on the light | **1.5 stops** | proedu, below |
| Polariser on the lens | **1.5 stops** | proedu, below |
| **Total to compensate** | **3 stops** | proedu, below |
| Practitioner range quoted elsewhere | 3–5 stops | (search-surfaced, ◐) |

"The 7300 Polarizing Filter itself reduces the light by 1.5 stops, as do most polarizing camera filters, so
you'll need to push 3 stops in order to compensate," and in one worked case "a simple 45-degree turn of the
filter at the lens knocked down the glare by approximately 98 percent on the bottle's neck and label"
(source: https://proedu.com/blogs/news/crushing-hotspots-cross-polarization-photo, retrieved 2026-07-29).
The same source flags real caveats: colour shifts appear as you approach extinction, and clear plastics and
liquids can produce "browning or spectrums."

**Limit 1 — it does not work on bare metal.** Polarisation-based glare suppression relies on the
polarisation state imposed by reflection from a *dielectric*. Reflection from a conductor largely preserves
the incident polarisation, so cross-polarisation has little effect on bare-metal specular highlights.
Practical consequence: use flags, tents and dark cards for metal, not polarisers.

**Limit 2 — full extinction makes gloss look matte.** Specular highlight *is* the visual cue that says
"this surface is glossy/wet/premium." Kill it entirely and a lacquered box reads as cardboard. The
professional move is **partial cross-pol: rotate to roughly 60–75° instead of 90°**, removing the nuisance
hotspot while keeping a controlled sheen. Reserve full extinction for label copy legibility, varnished
artwork, and sweat on skin.

### 8.7 Translucency, backlighting, liquids and food

| Subject | Key azimuth | Key elevation | Distance | Fill | Extra |
|---|---:|---:|---:|---|---|
| Clear/translucent drink (cocktail, beer, tea, juice) | **135–170°** | 25–40° | 0.5–0.8 m, 60×90 cm box | white bounce at 0° azimuth, 20–30 cm from the glass, **below the frame line** | black card at 45–70° to keep an edge on the glass |
| Opaque drink (latte, smoothie, milkshake) | **90–120°** | 30–45° | 0.6–1.0 m | white bounce at 0–30° | side light, not back light — backlight has nothing to transmit through |
| Thin translucent food (citrus slice 3–5 mm, herb leaf, sashimi, rice paper) | **150–180°** | 10–25° | 0.4–0.7 m | minimal; let it glow | glow must be brightest where thinnest |
| Broth / soup with steam | **150–170°** | 20–30° | 0.6–1.0 m | small bounce at 0° | **background ≥3–4 stops darker than the steam**, or the steam is invisible |
| Thick opaque food (burger, steak, cake slice) | **90–135°** | 35–55° | 0.8–1.2 m | bounce at 0–30°, 1–1.5 st under key | one small hard kicker at 120° for the wet sheen |
| Dry texture (bread crust, granola, powder) | **60–85°** raking | 15–30° | 1.0–1.5 m | very little; let shadows describe texture | negative fill opposite the rake |

Confirmed craft principle: "Transparent and translucent drinks (most cocktails, beer, wine, juice, tea)
want backlight, while opaque drinks (milkshakes, lattes, smoothies, coffee with cream) want side light,"
with backlight/rim placed "behind the subject (90-120° from camera), often slightly above," and a white
bounce card "between the camera and the subject (below the frame)" to lift the front
(sources: https://foodshot.ai/blog/drink-photography-guide ◐; https://foodshot.ai/blog/food-photography-lighting ◐;
https://phoode.com/blog/4-creative-lighting-styles-with-backlighting-in-food-photography/ ◐, retrieved 2026-07-29).

---

## 9. Colour temperature, mixed sources and practicals

### 9.1 Kelvin reference

Verified directly: light "shortly after sunrise or before sunset" is around **2,000 K**; during golden hour
around **3,500 K**; at midday around **5,500 K**
(source: https://en.wikipedia.org/wiki/Golden_hour_(photography), retrieved 2026-07-29).

| Source | Kelvin | Mired (10⁶/K) | Confidence |
|---|---:|---:|---|
| Candle flame | ~1,900 | 526 | ◐ chart value |
| Domestic incandescent | 2,700–2,900 | 370–345 | ◐ chart value |
| Tungsten studio (Type B) | **3,200** | 313 | ◐ chart value |
| Golden hour sun | **~3,500** | 286 | **verified (Wikipedia)** |
| Just after sunrise / before sunset | **~2,000** | 500 | **verified (Wikipedia)** |
| Standard photographic flash / daylight | 5,200–5,600 | 192–179 | conventional |
| Direct sun at noon | **~5,500** (charts: 5,000–5,400) | 182 | **verified (Wikipedia)** |
| Sun through cloud/haze | 5,500–6,500 | 182–154 | ◐ chart value |
| Overcast sky | 6,000–7,500 | 167–133 | ◐ chart value |
| Outdoor shade (clear sky) | 7,000–8,000 | 143–125 | ◐ chart value |
| Blue sky, no direct sun | 11,000–13,000 | 91–77 | ◐ chart value |

(chart values: https://media.cityelectricsupply.com/cesonline/ca/media/Electrical_References/CES_KelvinColourTempChart.pdf ◐;
https://courses2.wccnet.edu/~donw/pdf/onaji/kelvin.pdf ◐ — direct fetch returned binary PDF, values taken
from the search index; ranges differ between published charts, so treat as ±500 K and meter when it matters.)

### 9.2 Use mireds, not Kelvin, to reason about *differences*

`mired = 10⁶ / K`. Perceived colour shift tracks mired difference roughly linearly; Kelvin difference does
not. 3,200 K → 3,700 K is a 42-mired shift and clearly visible. 9,000 K → 9,500 K is 6 mireds and nearly
invisible, despite being the same 500 K.

| Pair | Kelvin gap | Mired gap | Reads as |
|---|---:|---:|---|
| 5,200 vs 5,600 K | 400 | 14 | one source; a WB rounding error |
| 5,600 vs 6,500 K | 900 | 25 | slightly cool; "shade creeping in" |
| 4,300 vs 5,600 K | 1,300 | 54 | two sources, mildly mismatched — the danger zone |
| 3,200 vs 5,600 K | 2,400 | **134** | deliberate warm/cool contrast |
| 2,700 vs 9,000 K | 6,300 | **259** | strong stylised split (neon/dusk look) |

### 9.3 Making mixed light read as intentional — three thresholds

1. **Dominance.** One temperature must own ≥70% of frame area **or** sit ≥1.5 stops above the other. Two
   equal, equally-spread temperatures read as a mistake.
2. **Separation.** The two temperatures must occupy *different roles or different sides* — warm key / cool
   rim, warm interior / cool window, warm foreground / cool background. Interleaved patches of both on the
   same plane read as broken.
3. **Magnitude.** Aim for **≥100 mired** apart (deliberate contrast) or **≤20 mired** apart (one source).
   The band **20–100 mired** is where images look like a white-balance failure rather than a choice.

[Threshold 3 is a working heuristic derived from the mired arithmetic above plus observed practice, not a
measured study. UNVERIFIED as a published rule; the mired maths behind it is standard.]

### 9.4 The green/magenta trap

Warm/cool is one axis; green/magenta (Duv, distance from the blackbody locus) is the other. Fluorescents,
cheap LED panels and some LED practicals sit measurably off the locus. **Kelvin mismatch can be fixed in
white balance; Duv mismatch cannot** — it needs a CC/tint correction per source or gel on the fixture.

Diagnostic: if a mixed-source frame reads "moody," it is a Kelvin split. If it reads "wrong" or "sickly,"
it is almost always a Duv problem — commonly a green cast in the fill or in a background practical.

### 9.5 Practicals in frame as narrative — exposure targets

A practical (lamp, neon, screen, candle, string lights, phone) that is visible in frame is one of the few
things allowed to clip.

| Element | Target relative to key exposure |
|---|---|
| The emitting element itself (filament, LED, tube) | **+2 to +4 stops** — clipped white |
| The glass envelope / shade | **+1 to +2 stops** |
| The practical's spill on the nearest surface, 30–50 cm away | **−1 to −2 stops** |
| The practical's spill at 1.5–2 m | −3 to −5 stops (inverse-square, §2.1) |
| A practical meant to read as *off* | −1 stop or lower |

Below about +0.5 stop, a practical reads as a switched-off prop, which is the most common failure in
generated interiors.

**The motivation rule (this is the big one).** If a practical is the *motivating* source for the scene, the
actual key must arrive from **within ±20° of the practical's azimuth** and match its colour to **within
~150 mired**. A generated interior with a warm table lamp on the left and a cool soft key from the right,
with no window on the right, is physically unmotivated. It is the single most frequent "this looks fake"
error in AI interior and hospitality imagery, and it is fixable with one clause.

Confirmed as production practice in official video guidance, which uses exactly this vocabulary: "warm key
from overhead practical; cool spill from window for contrast" and "Practical: sodium platform lights on dim
fade" (source: https://developers.openai.com/cookbook/examples/sora/sora2_prompting_guide, published
2025-10-06, retrieved 2026-07-29).
