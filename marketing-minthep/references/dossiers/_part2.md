
## 4. Optics for a bowl: focal length, aperture, depth of field

### 4.1 Why long lenses, stated as geometry

The trade press advice — avoid wide angles because they distort at close range, prefer 90–105 mm on
full-frame for flattering tight 45° shots, and instead of getting close with a wide lens get further
away with a long one — is correct `[search-level]` (source:
https://twolovesstudio.com/blog/ultimate-guide-lenses-food-photography/ and
https://foodphotographyacademy.co/blog/equipment/equipment-focal-length-explained-the-best-lens-for-food-photography/,
retrieved 2026-07-29, via search summary; I did not open these pages directly). The reason usually
given — "barrel/pincushion distortion" — is mostly wrong, and the real reason changes what you do.

Rectilinear lens distortion is a *lens design* artefact and is correctable in software. The
uncorrectable effect is **perspective divergence from subject distance**. At subject distance *s*,
two features separated in depth by Δ have a projected size ratio (s + Δ)/s. For a 180 mm bowl at
φ = 30°, the depth spread between near rim and far rim is 180 · cos 30° = 156 mm.

| Focal length (FF) | Approx. distance for bowl to fill 80 % of the 24 mm short side | Near-rim / far-rim size ratio |
|---|---|---|
| 35 mm | ≈ 0.36 m | (0.36 + 0.156)/0.36 = **1.43×** |
| 50 mm | ≈ 0.52 m | 1.30× |
| 85 mm | ≈ 0.88 m | 1.18× |
| 100 mm | ≈ 1.04 m | 1.15× |
| 135 mm | ≈ 1.40 m | 1.11× |

Derivation of the distance column: the bowl (180 mm) must span 80 % of 24 mm = 19.2 mm on the sensor,
so magnification M = 19.2/180 = 0.1067, and for a thin lens s ≈ f · (1 + 1/M) = f · 10.37. For
f = 100 mm that is 1.037 m. ✓ Then the ratio column is (s + 156 mm)/s.

**A 43 % near-far size difference is what "wide-angle food looks wrong" actually is.** The near rim
balloons, the far rim shrinks, and the rim stops looking like a circle in perspective and starts
looking like an egg. At 100 mm the difference is 15 % and reads as depth rather than as error.

Practical: **85–105 mm on full-frame; 56–70 mm on APS-C; 42–52 mm on Micro Four Thirds.** On a phone,
use the 2× or 3× telephoto module, never the 1× main camera, and never the ultra-wide. For a
restaurant shooting its own delivery photos this is the largest available quality jump and it costs
nothing.

### 4.2 Depth of field for a 180 mm bowl

At φ = 30°, the depth spread from near rim to the top of a 40 mm noodle mound is roughly 90 mm; near
rim to far rim is 156 mm.

Approximate total DoF for full-frame, circle of confusion c = 0.029 mm, using DoF ≈ 2·N·c·(s/f)² for
s ≫ f:

| f | s | f/4 | f/5.6 | f/8 | f/11 |
|---|---|---|---|---|---|
| 100 mm | 1.0 m | 23 mm | 32 mm | 46 mm | 64 mm |
| 100 mm | 1.4 m | 45 mm | 64 mm | 91 mm | 125 mm |
| 85 mm | 1.0 m | 32 mm | 45 mm | 64 mm | 88 mm |

Check one cell: 2 × 5.6 × 0.029 × (1000/100)² = 2 × 5.6 × 0.029 × 100 = 32.5 mm. ✓

**Decision rule.**
- **Hero, single bowl, everything sharp:** you need ≥ 156 mm of DoF. At 100 mm / 1.0 m that means
  f/22 and beyond — diffraction-soft. **Focus-stack instead:** 5–7 frames at f/5.6, focus stepped
  20 mm through the bowl. This is the correct answer and it is rarely done.
- **Editorial / social, shallow:** f/2.8–f/4, focus plane on the *front third of the noodle mound*,
  not the near rim and not the far garnish. 23–32 mm of DoF puts the sharp band where the eye lands.
- **Menu and delivery thumbnails:** f/8–f/11, no stacking. At 96–320 px the DoF question is moot;
  what matters is that nothing is conspicuously soft, because Uber Eats rejects images that are
  "blurry or out of focus" `[verified]` (source:
  https://help.uber.com/en/merchants-and-restaurants/article/merchant-submitted-menu-catalog-photo-guidelines?nodeId=6985355b-0426-4523-94f2-89bb9b0566e9,
  retrieved 2026-07-29).

Steam adds a shutter-speed constraint that fights aperture: see §6.4.

---

## 5. Lighting for food: why backlight and side-backlight dominate

Front light is nearly absent from professional food photography, for four separate physical reasons.
Naming them lets you decide instead of imitate.

### 5.1 Mechanism 1 — steam only exists in forward-scattered light

Water vapour is invisible; what reads as "steam" is an aerosol of condensed liquid droplets. The
Wikipedia entry states the phase distinction directly: "Superheated or saturated steam is invisible;
however, wet steam, a visible mist or aerosol of water droplets, is often referred to as 'steam'"
`[verified]` (source: https://en.wikipedia.org/wiki/Steam, retrieved 2026-07-29). That page does not
discuss scattering, so the mechanism attribution is separate: droplets of a size comparable to the
wavelength produce **Mie scattering**, which deflects all visible wavelengths roughly equally and so
reads white/opaque `[search-level]` (source: search summary across physics explainers, retrieved
2026-07-29).

Mie scattering from such droplets is strongly **forward-peaked** — far more light continues roughly
in its original direction than is returned toward the source. A droplet cloud is therefore brightest
when the light is *behind* it. Front-light it and you see only the weak back-scatter lobe, and the
steam nearly vanishes.

So: **a hot dish's most distinctive asset is only accessible from behind.** The craft literature
reaches the same conclusion without the mechanism — steam is only visible when side-lit or backlit
`[search-level]`; the same source states, verified, that "a dark background defines steam, whereas
the vapors will completely blend into a white background" `[verified]` (source:
https://phoode.com/blog/the-hot-look-of-the-steam-effect-in-food-photography/, retrieved 2026-07-29).

### 5.2 Mechanism 2 — translucency and subsurface scattering in garnishes

Much food is not opaque: light enters, scatters repeatedly inside, and exits elsewhere. The canonical
model is Jensen's BSSRDF — "A Practical Model for Subsurface Light Transport" — which "introduces a
simple model for subsurface light transport in translucent materials," enabling "effects that BRDF
models cannot capture, such as color bleeding within materials and diffusion of light across shadow
boundaries," and can recover optical properties of milk, marble and skin `[verified]` (source:
https://graphics.stanford.edu/papers/bssrdf/, retrieved 2026-07-29). The page carries no coefficient
table. `[UNVERIFIED - no measured scattering/absorption coefficients for broth, herb leaf, rice
noodle or annatto oil. To close: pull the full BSSRDF PDF material table plus food-optics
literature. Until then all translucency guidance here is qualitative.]`

What matters operationally is the **thickness threshold**: subsurface scattering is visible when
thickness is comparable to the mean free path. Thin food elements meet it — herb leaves 0.2–0.5 mm,
lime slices 2–4 mm, bean sprouts 2–3 mm, thin-sliced raw beef 1–2 mm, rice paper. Thick dense
elements do not — pork knuckle, meatball, noodle mound — and backlight there yields only a rim.

One formula in circulation deserves a warning. "Optimal intensity (%) = 100 − (food thickness in mm
× optical density coefficient)," with coefficients 5–7 for most fruits and 8–12 for pastries, giving
~85 % for a 3 mm lemon slice, is published `[verified as published]` (source:
https://www.replicasurfaces.com/blogs/updates/beyond-the-standard-setup-the-physics-and-psychology-of-food-photography-lighting,
retrieved 2026-07-29) — but it is dimensionally incoherent (a percentage minus a length times a
dimensionless coefficient) and carries no derivation.
`[UNVERIFIED - appears in one vendor blog with no basis. Do not put it in a client deck. The
defensible version: transilluminate thin elements, bracket the backlight across 3 stops, choose by
eye, and record the winning power setting.]`

**Vietnamese noodle-soup specifics.**
- **Perilla (tía tô)** is bicoloured — green obverse, purple-red reverse. Transilluminated from the
  reverse, the anthocyanin layer glows magenta and one leaf delivers two colours. Generic food
  lighting throws this away. Place at least one perilla leaf reverse-to-the-backlight.
- **Banana blossom (bắp chuối)**, shredded thin, transmits broth colour and will read warmer in frame
  than in hand. Expect a hue pull toward the broth and compensate by increasing its physical
  separation from the broth surface.
- **Bean sprouts** transilluminate strongly and are the cheapest way to inject a high-luminance
  element into a warm bowl (§10.3).
- **Rice noodle** is translucent while hot and hydrated, and turns opaque chalk-white as it cools and
  surface-dries. A chalky noodle crown is a visible, customer-legible freshness failure.

### 5.3 Mechanism 3 — specular geometry: the light must be where the mirror points

A glossy surface shows a highlight only if the light lies in the **family of angles** that mirror
into the lens. From §3.2: for a horizontal broth surface and a camera at elevation φ, the light must
sit at elevation φ on the opposite azimuth. Because soup is shot at φ = 25–45°, the light must be at
elevation 25–45° *behind* the bowl. That is not a stylistic choice; the reflection law forces it once
the angle is chosen.

Size relation, from the strobist canon: "As the size of the light source decreases, the intensity of
the specular highlight increases. And vice versa," and "Light, spread out over a large enough area,
becomes less intense per square inch"; consequently form on **dark** objects is revealed by
speculars, and form on **light** objects by shadows `[verified]` (source:
https://strobist.blogspot.com/2007/07/lighting-102-unit-22-specular-highlight.html, retrieved
2026-07-29).

Apply that last clause to a bún bò bowl. The broth is a **dark saturated** object (relative luminance
Y ≈ 0.218, derived in §10.1), so its form is carried by speculars. The noodle is a **light** object
(Y ≈ 0.762), so its form is carried by shadow. **A single bowl therefore requires two lighting logics
at once** — a placed specular for the broth and a raking component to shade the noodle mound. That is
exactly why the §3.6 setup has a 30°-elevation strip plus a 55°-elevation kicker rather than one
light. If you have ever lit a bowl of soup "correctly" and found the noodles looked like a flat pale
mass, this is the reason.

### 5.4 Mechanism 4 — rim separation without touching the background

Back and side-back light draws a bright outline along food edges, separating noodle mound from broth
and wet meat edge from meat body using geometry alone. Front light cannot: it fills the very shadows
that define those edges. On a monochrome-ish warm bowl this is often the *only* thing creating
internal structure.

### 5.5 Named setups, with numbers

Three setups cover almost all Vietnamese noodle-soup work. Distances to bowl centre; elevations from
the table plane; azimuth 180° = directly away from camera.

**A. "Cửa sổ" — window daylight, single source, documentary honesty**
```
Source     North-facing window, ~1.0 × 1.4 m, no direct sun, mid-morning
Bowl       Azimuth 150–165°, 0.6–0.9 m from the glass
Camera     phi = 32 deg, 100 mm, f/5.6
Fill       A3 white foam board at azimuth 330 deg, 0.5 m, metered 1.5-2 stops under key
Negative   Black card overhead — the §3.2 ceiling kill. A window scene still has a ceiling
Contrast   Key-to-fill 1.5-2 stops; shadow side of the bowl retains detail
Use for    Delivery apps, Google Business Profile, honest documentation, menu boards
Caution    Steam will not read: the source is too broad and the room too bright.
           Do not composite steam into a daylight frame (§6.5)
```

**B. "Nồi nước dùng" — hero broth**
Full spec is §3.6. Summary: 30 × 90 cm strip key at azimuth 175° / elevation 30°, 0.70 m; 15 × 60 cm
kicker at 240° / 55°, −2 stops; A3 white fill at 340°, −1.5 stops; overhead black flag; background
−2 to −3 stops; hot plate holding broth at 70–80 °C; polariser rotated to near-null then backed off
15–20°.

**C. "Chiaroscuro" — dark and opulent, for a rich broth or bò kho**
Fetched guidance: use "contrasty, directional lighting" mimicking "a single small window set high up
in the wall"; low-angle light emphasises texture on dark surfaces; hard version is a bare head with
barn doors or honeycomb grids to "keep the spill of light quite narrow"; soft version is a
medium softbox with black flags to "restrain the spread of light"; do **not** merely underexpose —
"you'll probably want some areas of the image to remain correctly exposed, otherwise there'll be
nothing for the viewer's eye to focus on"; avoid pure black backgrounds that leave "a plate of food
floating on a sea of pure black." Suited to rich, earthy, rough-surfaced foods; explicitly unsuited
to anything communicating "clean, lightweight, and healthy eating" `[verified]` (source:
https://phoode.com/blog/the-balance-of-bright-and-dark-as-the-key-to-successful-chiaroscuro-food-photography/,
retrieved 2026-07-29).

```
Key        60 × 60 cm softbox, azimuth 160 deg, elevation 55 deg, 30-deg egg-crate grid,
           plus two black flags 300 mm off the box edges narrowing the beam to ~40 deg
Fill       None; or a 10% silver card at 300 deg if the shadow side goes fully black
Negative   Black flags at 0, 60, 300 deg; black overhead
Background Dark slate or oiled wood with visible texture, raked by a second gridded head
           at elevation 12 deg, azimuth 200 deg, at 5-10% of key
Contrast   Key-to-shadow 4-5 stops, but hold a correctly-exposed zone over at least ~8% of frame
Use for    Hero, PR, packaging, print. Never for delivery apps, which reject
           "strong shadows or insufficient lighting" (Uber Eats, verified above)
```

**Setup selection rule.** If the image will be seen *in a grid next to competitors* (delivery app,
Google, aggregator), use A or a low-contrast B. If it will be seen *alone* (hero banner, poster, menu
cover, PR), C is available. The deciding variable is whether the viewer has a side-by-side luminance
reference.

### 5.6 Colour temperature and CRI

Published guidance: main light "around 5500K," rim light "5700-5900K," a deliberate "controlled
200-300K differential," worked example main dish 5500 K with garnishes at 5800 K
`[verified as published]` (source:
https://www.replicasurfaces.com/blogs/updates/beyond-the-standard-setup-the-physics-and-psychology-of-food-photography-lighting,
retrieved 2026-07-29).

Assessment: **the differential is real craft; the specific 200–300 K figure is not established.** A
cooler kicker does separate garnish from a warm broth because the eye reads temperature difference
as depth. But 200–300 K around 5500 K is roughly a 6–10 mired shift, at or below what most viewers
resolve in print. `[UNVERIFIED - no measurement or study supports 200-300 K. What would close it: a
JND study on colour-temperature separation in food images, or in-house A/B at 0 / 300 / 600 / 1000 K
deltas judged blind at output size.]` Defensible starting point: **500–800 K cooler on the kicker
than the key**, reduced if the garnish starts reading grey-green.

**CRI matters more than CCT for food and is routinely ignored.** A low-CRI LED with deficient R9
(deep red) renders beef, annatto oil and chilli as brown-grey — and the red-orange band *is* the
point of a bún bò frame. Specify **CRI ≥ 95, R9 ≥ 90** for any continuous source on food, and prefer
flash where possible.
`[UNVERIFIED - the R9 mechanism is standard lighting engineering but I am asserting it from
background knowledge, not from a page I opened today. To close: pull CIE 13.3 / IES TM-30
documentation and one measured spectral comparison of a low-R9 vs high-R9 source on red food.]`

**White-balance target.** Do not balance on the bowl rim (Vietnamese glazes often carry a blue-white
cast) and do not balance on the broth (it is the subject). Balance on a grey card placed at the bowl
and removed before the take, then verify the broth hue lands in the band given in §10.2.

---
