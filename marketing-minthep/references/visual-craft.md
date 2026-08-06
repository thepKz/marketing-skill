# Visual Craft System

Turn a reference image or product truth into a controlled photoshoot direction. Separate immutable locks from creative freedoms and list rejects before prompting.

Load `composition-light-color.md` for the detailed composition, lighting, shadow, and color method. Load `image-output-and-sharpening.md` for resolution, upscale, sharpening, export, and output QA. This file is the short routing contract, not a substitute for those craft references.

## Composition

Choose one dominant subject, one focal hierarchy, and one reading path. Specify camera height, lens/field of view, distance, crop, negative space, horizon, and rule-of-thirds/centered/diagonal rationale. For a menu or ad, reserve explicit text-safe zones; never ask an image model to render final small type.

## Light and shadow

Name source size, direction, height, softness, color temperature, fill ratio, contact shadow, cast-shadow direction, and background separation. Shadows must agree with the light; use a real reference or a simple diagram when physical consistency matters.

## Color and finish

Define 3-5 role-based colors (background, subject, accent, type, CTA), contrast intent, saturation ceiling, white balance, and grade. Preserve product color and food appetite cues; never grade an edible product into an inaccurate color.

## Detail and resolution

Specify master aspect ratio, intended output pixels, crop-safe margin, texture/detail priority, and upscale/sharpen policy. Generate a clean high-resolution master, then resize and sharpen per placement; do not use sharpening to hide blur, anatomy, or product-label errors.

## QA gate

Reject identity/product drift, impossible shadows, plastic texture, halos, over-sharpening, unreadable text, unsafe food/health claims, and a composition that leaves no usable copy area. Provide an executable prompt plus a human retouch/export checklist when rendering is unavailable.


---

<!-- Deep dossier merged from references/dossiers/materials-and-surfaces.md (2026-08-06). Long-form research behind the working sections above. External facts retrieved 2026-07-29; re-check anything priced, versioned, or platform-specific.  -->

# Materials and Surfaces — Research Dossier

## Scope

How real surfaces behave under light, expressed as numbers, thresholds and named setups, for product and food imagery that is either photographed or generated. Covers the practical BRDF model, per-material playbooks (glass, metal, plastic, paper, ceramic, fabric, leather, skin, hair, liquids, food), the translation of each into text-to-image prompt language, and the physics QA checks that catch floating products, impossible reflections and fake steam. Assumes the reader knows nothing about optics and needs to decide, not to admire.

Citation convention: `(source: URL, retrieved 2026-07-29)`. Where a page could be fetched and read, it is marked **[verified]**. Where the fact came from a search-result summary only, it is marked **[search-level]** and should be re-checked before being stated as fact in a client deliverable. Physics, optics and colour-science fundamentals (Fresnel, Snell, surface tension, microfacet behaviour) are stated without citation; derived arithmetic is shown so it can be re-checked by hand.

---

## Part 1 — The practical BRDF mental model

### 1.1 Every surface is at most three layers

| Layer | What it is | Colour of the light it returns | Which materials have it |
|---|---|---|---|
| **Specular / interface** | The first reflection off the boundary between air and the material. Nothing has entered the material yet. | For **dielectrics**: the colour of the *light source*, never the colour of the object. For **metals**: the colour of the *metal*. | Everything |
| **Body / diffuse** | Light that entered, bounced around inside among pigment particles, and came back out. | The colour of the *object*. | Dielectrics only. **Metals have none.** |
| **Coat** | A second clear layer on top (glaze, varnish, clearcoat, sebum, water film, lamination) | Colour of the source, with its own separate roughness | Glazed ceramic, car paint, spot UV, wet anything, oily skin, patent leather |

Three sentences that do most of the work:

1. **A white highlight on a red plastic object is correct. A white highlight on red-gold metal is wrong.** Dielectric speculars carry the source colour; metal speculars are tinted by the metal.
2. **Metal has no diffuse layer.** A metal object with a mid-grey body tone and a Fresnel-bright rim is being rendered as glossy grey plastic. This is the single most common material error in generated product images.
3. **The more specular the material, the more you light the *environment*; the more diffuse the material, the more you light the *object*.** Glass and chrome are photographs of the room. Flour and matte cardboard are photographs of the thing.

### 1.2 F0 — how reflective a material is when you look at it face-on

For dielectrics, the normal-incidence reflectance is fixed by refractive index alone:

```
F0 = ((n - 1) / (n + 1))^2
```

| Material | n (refractive index) | F0, computed | Reads as |
|---|---:|---:|---|
| Air/vacuum | 1.000 | 0% | — |
| **Ice** | 1.31 | 1.8% | Duller than glass. See §4.12 for why this matters. |
| **Water** | 1.333 | 2.0% | Faint sheen face-on, mirror at grazing |
| **Vegetable / chilli oil** | ~1.47 | 3.6% | Slightly glossier than water |
| **Skin (dermis)** | 1.36–1.41 | 2.3–2.9% | Very faint |
| **Skin (epidermis)** | 1.41–1.49 | 2.9–3.9% | Faint — any brighter highlight is sebum or product |
| **Acrylic / PMMA** (fake ice, display blocks) | 1.49 | 3.9% | Glass-like |
| **Soda-lime glass** | 1.52 | 4.3% | The canonical "4%" |
| **Hair keratin** | 1.55 | 4.7% | See §4.10 |
| **Polycarbonate / PET** | 1.575–1.585 | 5.0–5.1% | Slightly "wetter" than glass |
| **Ceramic glaze** | 1.5–1.6 | 4.3–5.3% | Glass on top of clay |
| **Diamond / high-index crystal** | 2.417 | 17.2% | Reads as jewellery, not glass |

Skin refractive index values from Ding et al. 2006, *Physics in Medicine and Biology* 51(6), measured at eight wavelengths 325–1557 nm; approximately 1.41–1.49 for epidermis and 1.36–1.41 for dermis (source: https://iopscience.iop.org/article/10.1088/0031-9155/51/6/008, retrieved 2026-07-29) **[search-level — the per-wavelength table could not be extracted; the PDF at bmlaser.physics.ecu.edu returned unparseable binary]**.

Metals do not follow this formula and their F0 is both high and wavelength-dependent:

| Metal | Spectral behaviour | F0 magnitude | Art-direction consequence |
|---|---|---|---|
| **Silver** | Near-flat across visible | ~0.95–0.98 | Reflections arrive at nearly the source's own brightness and colour. Darkness in silver is just a dark reflection. |
| **Aluminium** | Near-flat, very slightly cooler | ~0.90–0.92 | Reads as "honest" neutral metal. Best default for tech products. |
| **Chrome** | Lower and slightly cool/green | ~0.55–0.65 | **Darker and higher-contrast than silver.** Chrome needs both bright *and* pure-black elements around it or it reads as grey plastic. |
| **Gold** | Suppresses blue steeply below ~500 nm; near-full above ~600 nm | Warm-biased, high in red | A gold surface reflecting a cool sky reads muddy grey-green. Gold **cannot** produce a neutral-white highlight unless the source is clipping. |
| **Copper / brass** | Even stronger warm bias | Warm-biased | Oxide patina behaves as a *dielectric layer on top* — it reintroduces a diffuse component |

Numeric sRGB F0 triplets for metals circulate widely in PBR documentation (e.g. gold ≈ 1.00/0.77/0.34). **[UNVERIFIED — I could not fetch a primary source for specific triplets. The spectral *behaviour* above is standard optics and safe; treat the triplets as convention, not measurement. To verify I would need the Filament materials documentation or a published spectral reflectance dataset.]**

### 1.3 Fresnel — the one law that changes how you light every edge

Schlick's approximation, accurate enough for all art direction:

```
F(theta) = F0 + (1 - F0) * (1 - cos theta)^5
```

Worked out for a typical dielectric (F0 = 0.04, i.e. glass, plastic, paint, skin):

| Angle from surface normal | Reflectance | In practice |
|---:|---:|---|
| 0° (face-on) | **4.0%** | You barely see the surface at all |
| 45° | 4.2% | Still negligible |
| 60° | **7.0%** | Starting to lift |
| 70° | **15.8%** | Clearly visible sheen |
| 80° | **41%** | Brighter than most diffuse surfaces |
| 85° | **65%** | Effectively a mirror |
| 90° (grazing) | 100% | Perfect mirror |

**What this means operationally.** Every curved dielectric object — bottle, tube, jar, apple, cheek, ceramic mug — has a bright band where its surface turns away from the camera, because there the light is arriving at 75–88° and 40–65% of it is being mirrored. That band is *not* a rim light. It is the object mirroring **whatever is beside and behind it**. Therefore:

- To make a plastic bottle's edges read, you do not add a backlight. You put a **tall bright card or strip source outside the frame, roughly in the plane of the bottle's edge**, and let the edge mirror it.
- A generated bottle whose edges are dark against a dark background has failed Fresnel. There is nothing physically able to make an edge dark unless the object is surrounded by black — which is a valid, deliberate choice (see negative fill), but must be consistent on both sides.
- **Metals barely ramp.** F0 is already 0.6–0.98, so there is little headroom. A "metal" object with a dull middle and a bright thin rim is plastic pretending. This is a fast, reliable QA test.
- **Brewster angle:** `theta_B = arctan(n)`. Glass n=1.52 → **56.7°**. Water n=1.333 → **53.1°**. At that angle the reflected light is fully polarised in one plane, so a single polariser on the lens can null it completely. This is why glare on a tabletop or a wine surface disappears at a specific camera height and not at others. Formula and the 30–50° practical window from (source: https://www.vision-doctor.com/en/filters/polarising-filters.html, retrieved 2026-07-29) **[verified]**.

### 1.4 Microfacet intuition without the maths

Think of any rough surface as **a mirror smashed into microscopic tiles**. Roughness is the spread of tile angles. Four consequences, all directly usable:

1. **Highlight blur is proportional to tile spread.** Sharp highlight = smooth surface. There is no such thing as "a rough surface with a sharp highlight".
2. **Energy is conserved.** A rough surface gets a *bigger but dimmer* highlight, not a bigger and equally bright one. If a generated matte surface has a large *and* blown-out highlight, that is impossible.
3. **At grazing angles tiles shadow each other**, so the highlight stretches into a streak running away from the viewer. This is why wet asphalt shows long vertical light streaks and why a satin tabletop shows a long smear rather than a round blob.
4. **Anisotropy** = all tiles tilted along one axis (brushing, weaving, extrusion, hair, vinyl record grooves). The highlight becomes a line instead of a spot. See §4.3 for the two-part visual signature this creates on brushed metal.

Two named additions worth knowing because they are exposed as sliders in most 3D tools and appear in some prompt vocabularies:

- **Sheen** — an extra grazing-angle lobe added specifically for cloth, because fabric surface fibres retro-reflect. It is why velvet's silhouette glows brighter than its centre. The Disney principled BRDF exposes `sheen` and `sheen tint` for exactly this reason (source: https://blog.selfshadow.com/publications/s2015-shading-course/burley/s2015_pbs_disney_bsdf_notes.pdf, retrieved 2026-07-29) **[UNVERIFIED — the PDF exceeded the fetch size limit at 10 MB. The parameter list and the roughness-squared remap are widely reproduced in Blender, Arnold and Unity documentation; the specific wording in Burley's notes was not read.]**
- **Roughness is usually squared** before it reaches the microfacet distribution (`alpha = roughness^2`). Practical effect: the slider is perceptually linear, so **doubling the number does not double the blur**. Moving 0.2 → 0.4 is a much bigger visual change than 0.7 → 0.9.

### 1.5 The roughness ladder — the single most useful table in this dossier

Values are on the standard 0–1 roughness scale used by Blender, Substance, Unreal, Arnold and most "PBR" vocabularies.

| Roughness | Real-world analogue | Highlight appearance | How to light it | Prompt words that land |
|---:|---|---|---|---|
| 0.00–0.05 | Chrome, mirror, still water, wet glass, patent leather, foil stamp | Source shape reproduced **exactly**, sharp-edged | Build the environment; shape the reflection, not the object | `mirror-polished`, `chrome`, `liquid-mirror` |
| 0.05–0.15 | Piano-black lacquer, polished glass, glazed ceramic, SPI A-1/A-2 plastic, wet hair | Source shape **recognisable**, slight edge bloom | One large source in the mirror family + black flags for structure | `high-gloss lacquer`, `glazed`, `wet-look` |
| 0.15–0.30 | Gloss injection plastic (SPI A-3), satin lacquer, silk, foil, oiled food, leather finish coat | Source shape blurred but its **orientation is readable** | Medium source, feathered; keep one clean gradient across the form | `satin`, `semi-gloss`, `polished` |
| 0.30–0.50 | Semi-gloss plastic (SPI B), eggshell paint, coated matte paper, broad sebum sheen | Soft oval glow, no discernible source shape | Large soft source; contrast comes from ratio, not reflection | `eggshell`, `soft satin`, `low-sheen` |
| 0.50–0.70 | Matte plastic (SPI C), uncoated paper, unglazed stoneware, cotton, brushed metal across grain | Broad low-contrast sheen only at grazing | Direction matters more than size; use a raking source to reveal texture | `matte`, `uncoated`, `bisque` |
| 0.70–1.00 | Soft-touch coating, velvet, flocking, suede, chalk, flour, cocoa powder, matte-laminated board | No highlight; only a **grazing-angle sheen halo** | Raking light at 10–25° above the surface plane, plus fill to keep shadows open | `soft-touch`, `velvety`, `chalky`, `flocked` |

**Diagnostic use:** if you can see a *source-shaped* highlight on something described as matte, the render is wrong. If you can see *no* grazing sheen on something described as soft-touch, the render is also wrong (soft-touch is not the absence of specular, it is specular pushed entirely to the silhouette).

---

## Part 2 — The five controls that actually set material appearance

Everything else is decoration. These five, with their formulas, determine the result.

### 2.1 Angular source size (not physical size)

```
angular size = 2 * arctan(W / (2 * D))
```

| Source | Distance | Angular size | Character |
|---|---:|---:|---|
| 1.0 m octabox | 0.6 m | 79° | Very soft, huge wrap |
| 1.0 m octabox | 1.0 m | 53° | Soft, classic beauty |
| 1.0 m octabox | 3.0 m | 19° | Noticeably harder than most people expect |
| 1.0 m octabox | 6.0 m | 9.5° | Effectively a hard light |
| 60 cm softbox | 0.5 m | 62° | Softer than the 1 m box at 3 m |
| Bare speedlight (~7 cm) | 1.5 m | 2.7° | Hard, crisp shadows |
| The sun | 150 million km | 0.53° | The reference "hard" source |

**This kills the "bigger softbox is softer" folklore.** A 60 cm box at 0.5 m (62°) is softer than a 1.5 m box at 4 m (21°). Softness is angular, full stop.

### 2.2 Shadow penumbra — predict contact-shadow softness before you shoot

```
penumbra width ≈ (source width × object-to-surface distance) / source-to-object distance
```

| Setup | Object height above surface | Penumbra |
|---|---:|---:|
| 1 m box at 1 m | 5 mm (a box sitting on a table) | **5 mm** |
| 1 m box at 1 m | 100 mm (a bottle's shoulder) | 100 mm |
| 1 m box at 2 m | 5 mm | 2.5 mm |
| Bare flash (7 cm) at 1.5 m | 5 mm | 0.23 mm — essentially hard |

**The key corollary: at the actual point of contact, distance = 0, so penumbra = 0.** Every real object resting on a surface has a **razor-sharp dark line exactly at the contact**, which then softens as the surface recedes from the object. Generated images almost always give a uniformly soft blob instead. This is QA check #1 in §6.5.

### 2.3 The family of angles (the reflection rule)

For any patch of a glossy surface, there is a cone of directions that will reflect into the lens. That cone is the **family of angles** for that patch.

- To fill a **flat glossy label** with even white, the source must be at least as wide as the label *and* positioned at the mirror image of the camera about the label's plane.
- To make the same label read **dark and graphic**, put black there instead. Black flags are lights.
- Curved surfaces have a family that sweeps: a cylindrical bottle needs a source that is **tall** (covering the vertical extent) and **narrow** (so the highlight is a defined band, not a wash). Hence strip lights for bottles.
- Rule of thumb for a cylinder: a strip source whose width covers about **20–35% of the visible cylinder width** in the reflection gives a highlight that reads as "premium glass" rather than "flashed". Wider looks cheap; narrower looks like a laser line.

### 2.4 Background and surround luminance, in stops relative to the key on the subject

| Background reading vs key | Effect | Typical use |
|---:|---|---|
| +1 to +2 stops | Pure white, blows out, gives Fresnel edges to feed on | E-commerce white, bright-field glass |
| 0 stops | Background reads as light grey, product separates by contrast only | Editorial neutral |
| −1 to −2 stops | Mid-grey, "studio" look | Catalogue with mood |
| −3 to −4 stops | Near-black but with tonal information | Dark-field glass, dark cosmetics |
| −5 stops or more | True black, no information | Dark-field, jewellery, foil (needs the reflections to carry everything) |

### 2.5 Polarisation

Two distinct techniques, routinely confused:

| | Single polariser on the lens | Cross-polarisation (polariser on light **and** lens) |
|---|---|---|
| Removes | Glare from **dielectrics** near the Brewster angle only | Nearly all specular from dielectrics, at any angle |
| Effect on diffuse | Almost none | Almost none (diffuse light is depolarised by scattering) |
| Effect on **bare metal** | **Very little.** Metals do not polarise reflection the way dielectrics do (source: https://www.vision-doctor.com/en/filters/polarising-filters.html, retrieved 2026-07-29) **[verified]** | Metal specular retains the incident polarisation and gets extinguished — but metal has **no diffuse layer**, so the metal goes near-**black and dead**. Do not do this. |
| Light cost | ~1 to 1.5 stops | Substantial; the source page states only "a lot of light is absorbed by the filters" **[verified]**. A commonly quoted figure is a combined filter factor of about 3.5 stops **[UNVERIFIED — traced only to a USPTO patent text surfaced in search, not to a measurement. To verify I would need a manufacturer transmission spec for the specific film.]** |
| Setup | CPL on lens, rotate to null | Linear polarising gel on each light, CPL on lens, rotate to null (source: https://petapixel.com/2021/01/19/cross-polarization-what-it-is-and-why-it-matters/, retrieved 2026-07-29) **[verified]** |

**The professional move is almost never full cross-pol.** Full null removes the specular layer, and the specular layer *is* the material identity — a fully cross-polarised leather bag looks like painted cardboard. Rotate **15–30° off the null** to knock glare down 50–80% while keeping the material readable. Use full null only when you need flat colour data (colour matching, e-commerce colour truth, texture capture for 3D).

---

## Part 3 — Decision table: intent → setting

An AI or a junior can pick a row without taste.

| # | Intent | Material family | Key source | Position / distance | Fill & ratio | Background | Reflection control | Camera |
|---:|---|---|---|---|---|---|---|---|
| 1 | E-commerce white, truthful | Matte plastic, board, fabric | 1–1.5 m diffusion overhead + front | 45° above front, 1–1.5 m | White V-flats both sides, ratio 1.5:1 | White, +1.5 stops | None needed | 85–120 mm, f/8–f/11 |
| 2 | E-commerce white, glossy pack | Gloss plastic, coated carton | 1.2 m top-front diffusion | Directly above-front, 0.8 m | Two white cards at 40 cm, 30° | White, +1.5 stops | Black gobo strips 4–8 cm to draw edge lines | 100 mm, f/9 |
| 3 | Premium glass hero, dark | Clear glass, spirits | Large source behind, blocked by black patch | Patch 5–15 cm behind subject | Two white cards at 15 cm each side, 35–45° | Black flock, −5 stops | Full darkness in room | 100–135 mm, f/11 |
| 4 | Premium glass hero, bright | Clear glass, water, oils | Translucent panel behind, evenly lit | 0.8–1.2 m behind subject | None; black cards do the work | White panel, +2 stops | Black cards 15–30 cm each side to draw dark edges | 100–135 mm, f/11 |
| 5 | Metal hero, honest | Aluminium, steel | Tent (60–100 cm) fully diffused | Enclosing | Inherent | Whatever shows through the tent hole | **Black strips 3–10 cm inside the tent** — mandatory | 100 mm, f/11 |
| 6 | Metal hero, dramatic | Chrome, polished steel | Two strip lights, 30×120 cm | Left and right at 45°, 40–60 cm | Black centrally | Black or graduated | Large black flags to create the dark bands | 100 mm, f/11 |
| 7 | Gold / brass warmth | Gold foil, brass, copper | Warm-neutral source, ~3200–4300 K or gelled | In the mirror family of the gold plane | Warm gold/silver reflector | Warm mid-tone, never cool | White card exactly where gold must be bright | 100 mm, f/8–f/11 |
| 8 | Texture reveal (emboss, weave, grain, paper fibre) | Board, fabric, unglazed clay, soft-touch | Small-to-medium hard-ish source | **Raking, 10–25° above the surface plane** | Fill 2–3 stops under, opposite side | Matches surface | Negative fill on the fill side to deepen relief | Macro-behaviour, f/11–f/16 |
| 9 | Soft-touch / velvet / suede | Soft-touch plastic, velvet, nubuck | Medium source **behind and to the side** | 100–140° from camera axis | 1.5–2 stops under | Darker than subject | Nothing; the sheen halo is the subject | 85–100 mm, f/5.6–f/8 |
| 10 | Beauty skin, dewy | Skin, gloss lip | 1.0–1.2 m octabox | 0.8–1.2 m, feathered so the near edge points past the nose | Silver or white bounce 1 stop under (ratio 2:1) | −1 stop, seamless | Nothing; sebum map does it | 85–105 mm, f/4–f/5.6 |
| 11 | Beauty skin, matte editorial | Skin, powder finish | 90 cm beauty dish with sock | 1.0 m, on-axis above | White fill 1.5 stops under | −2 stops | Nothing | 105 mm, f/5.6 |
| 12 | Hair as hero | Hair | Key 45° front + **two rim sources at 120–140°** | Rims 1.5–2.5 m, hard-ish | Fill 2 stops under | −2 to −3 stops so rims read | Flag rims off the face | 85–135 mm, f/4–f/5.6 |
| 13 | Hot food, appetising | Broth, rice, noodles, sear | Medium diffusion **behind at 135–160°** | 0.6–1.0 m, at or slightly above plate height | White card in front, 1–1.5 stops under | 2–3 stops under, darker than steam | Small mirror to kick one specular where the eye should land | 50–100 mm, f/4–f/8 |
| 14 | Cold drink, refreshing | Glass, ice, condensation | Backlight or 3/4 back strip | 0.5–0.8 m behind | Minimal; keep the glass moody | 1–2 stops under, or bright for bright-field | Black card front-left to keep beads defined | 90–135 mm, f/8–f/11 |
| 15 | Liquid pour / splash | Water, milk, spirits | Strobe with **t0.1 ≤ 1/5000 s** | Back or side, 0.5–1 m | White cards to fill the stream | Bright for silhouette, dark for specular | Two strips to draw the stream edges | 100 mm, f/11–f/16 |
| 16 | Fabric drape, apparel | Silk, satin, knit, denim | 1.5 m source + long throw | Side at 60–75°, 1.5–2.5 m | 2 stops under | Neutral, −1 stop | Feather so the sheen band crosses the garment diagonally | 85–135 mm, f/5.6–f/8 |
| 17 | Print finish showcase (foil, spot UV, emboss) | Board with finishes | **Two separate exposures**: one for the sheet, one aimed at the finish plane | Finish source in the mirror family of the foil/UV plane | — | Neutral, controlled | This is the whole job | 100 mm macro, f/11, composite |
| 18 | Lifestyle in-hand, honest | Mixed | Window or 2 m bounced source | Side at 60–90°, 1–2 m | Natural bounce, 2–3 stops | Real environment | None | 35–50 mm, f/2.8–f/4 |

---

## Part 4 — Per-material playbooks

Each block: **what the material does to light → the setup that reveals it → the failure mode → prompt language → the specific AI failure to check for.**

### 4.1 Glass and transparent packaging

**Physics.** Glass has effectively **no diffuse layer**. Light either reflects (4.3% face-on, rising to 65% at 85° per §1.3) or refracts through. So there is nothing to "light". You are photographing (a) what the glass reflects and (b) what is behind it, distorted.

Refraction numbers that decide the shot:

- n = 1.52, so Snell's law bends rays hard at curved walls. A **cylindrical bottle acts as a strong lens**: whatever is behind the central band is **magnified vertically, compressed horizontally, and laterally inverted**. A rear label seen through the front of a round bottle appears **smaller, horizontally mirrored, and shifted**. AI models almost always render the rear label upright, unmirrored and full size.
- Wall thickness 2–4 mm on a typical bottle means the silhouette carries a **dense edge stack** 1–3 mm wide in the image: outer Fresnel bright line, then a dark refracted band, then the interior. A single flat outline means the glass is being drawn, not refracted.
- **Caustics are mandatory.** A clear filled glass concentrates light and must throw a **bright caustic patch 1–3× its own footprint**, usually offset away from the light, ringed by a softer shadow. A clear glass with only a dark shadow under it is a hard physics failure.

**Dark-field setup (glass reads as a bright outline on black).** Large source behind the subject; a **black "dark-field patch"** between source and subject, sized just larger than the subject's silhouette as seen from the light, placed **5–15 cm** behind the subject; light spills around the patch and grazes the glass edges. Base is black foam core or flocked material; the room must be **very dark** to kill stray reflections; reflective umbrellas turned black-side-in on both sides at close range act as flags (source: https://www.mattbristow.net/index.php/dark-field-lighting/, retrieved 2026-07-29) **[verified — the page gives the method and the black-flag technique but states no numeric distances; the 5–15 cm and patch-sizing figures are standard practice offered as a starting point]**. The technique comes from dark-field microscopy: block the centre, illuminate obliquely (source: https://westcottu.com/dark-field-imaging-tips-techniques, retrieved 2026-07-29) **[search-level]**.

**Bright-field setup (glass reads as a dark outline on white).** Translucent panel behind, lit to **+1 to +2 stops** over the glass. The glass body goes white; edges are drawn by **black cards at 15–30 cm each side**. The width of each dark edge line equals the angular width of the card as mirrored by the glass — so you control edge thickness by moving the card, not by dimming it. Bright field is the inverse of dark field: background lit, body white, edges defined by negative light (source: https://advancedillumination.com/lighting-education/bright-field-dark-field-lighting/, retrieved 2026-07-29) **[search-level]**.

**Edge definition with strip lights.** A 30 × 120 cm strip at **20–40 cm** from a 30 cm bottle, feathered so only the near third of the strip's width covers the glass, yields a clean vertical band occupying **10–20% of the bottle's width**. Two strips = the classic symmetric double edge. Three sources (two strips plus one top) = the "wrap" used for spirits.

**Failure mode on set.** Reflections of the studio — light stands, the photographer, the ceiling grid — appearing inside the glass. Cure: full blackout, longer lens from further back, black card with a lens-sized hole in front of the camera.

**Prompt language.** `clear soda-lime glass bottle, dark-field lighting, black flocked background, two narrow vertical white edge highlights defining the left and right shoulders, the rear label visible through the glass appearing smaller and horizontally mirrored, bright caustic pooling on the surface just right of the base, 2 mm wall thickness reading as a dense bright-dark-bright stack at the silhouette`

**AI failures to check.** (a) Rear label upright and same size. (b) Dark shadow, no caustic. (c) Uniform grey "glass" with a single white outline. (d) Left and right edge highlights that are perfect mirror images — real glass is never that symmetric because the room is not. (e) The background seen through the glass matching the background beside the glass exactly, with no displacement.

### 4.2 Liquid in glass — meniscus, fill line, and the second lens

**Meniscus rise** for a wetting liquid in a cylinder:

```
h = 2 * gamma * cos(theta) / (rho * g * r)
```

| Vessel | Radius | Liquid | Computed rise |
|---|---:|---|---:|
| Standard tumbler | 30 mm | Water (γ = 0.072 N/m, θ ≈ 0°) | **0.98 mm** |
| Wine glass bowl | 40 mm | Wine (γ ≈ 0.045) | 0.46 mm |
| Shot glass | 15 mm | Water | 1.96 mm |
| Narrow vial / test tube | 5 mm | Water | **2.9 mm** |

So the fill line in a normal glass curves up by about **1 mm** at the walls. Visible at product-macro scale, invisible at lifestyle scale — which tells you whether to specify it at all.

**Surface tension by liquid** (γ at ~25 °C, standard physical-chemistry values):

| Liquid | γ (mN/m) | Visual consequence |
|---|---:|---|
| Water | 72 | Tall beads, strong meniscus, clean crown splashes |
| Milk | 45–50 | Flatter beads, more stable foam, softer splash crowns |
| Vegetable oil | 30–35 | Spreads into lenses and films; does not bead |
| 40% ABV spirit | ~30 | Wets glass readily; produces visible legs/tears on the inner wall |
| Ethanol | 22 | Extreme wetting; almost no visible meniscus curvature |
| Water + surfactant | 25–35 | Beads collapse — this is why a trace of washing-up liquid ruins a condensation shot |

**The second-lens problem.** The filled and empty parts of a glass are **two different lenses**. The background seen through the wine is inverted and displaced differently from the background seen through the headspace, so the fill line shows a **visible jog of 1–4 mm** in whatever is behind it. AI renders the background continuous straight through the fill line. That single check catches most fake drink images.

**Prompt language.** `red wine filled to two-thirds, concave meniscus rising about 1 mm where the wine meets the glass wall, the background visibly jogging and inverting where it crosses from headspace into wine, thin wine legs clinging to the inner wall above the surface, one specular ellipse on the wine surface reflecting the strip light`

### 4.3 Polished metal, brushed metal, and the spectral personalities

**Physics.** No diffuse layer at all. F0 is 0.55–0.98 depending on the metal (§1.2). Therefore **a metal object's appearance is 100% the environment**. If the environment is featureless, the metal is featureless.

**Tenting — the standard solution.** Surround the object with a diffusing shell (white nylon, tracing paper, 200–250 g/m² diffusion) forming a **60–100 cm** enclosure; light the shell from outside; shoot through a hole **1.5–2× the lens barrel diameter**. Every direction the metal looks toward is now white.

**The mandatory second step everyone skips.** A fully tented metal object reads as **flat grey plastic**, because uniform white reflected in a mirror is uniform grey. You must add **black strips 3–10 cm wide inside the tent** to create dark structural lines. The strips are the drawing; the tent is only the paper.

**Polished flat panels.** By the family-of-angles rule (§2.3), a mirror-flat panel needs a source **as large as its own mirror image**. A 200 mm lid needs a source that appears at least 200 mm wide in the reflection, or you will see the source's edge crossing the panel.

**Brushed / anisotropic metal — the two-part signature.** This is where most renders and most prompts fail. Brushed metal shows **both**:

1. **Fine streaking along the grain direction** — each micro-groove is a tiny cylinder, and a cylinder's highlight runs *along* its own axis.
2. **A broad soft sheen band running perpendicular to the grain** — across the whole field, the set of grooves that happens to satisfy the mirror condition forms a band crossing the grain.

Linear-brushed aluminium under a strip light therefore shows **fine horizontal grain lines plus one wide vertical sheen band** (for horizontal brushing). Circular or radial brushing — watch casebacks, rice-cooker lids, speaker grilles — produces a **two-lobe "bowtie" sheen** or a rotating gradient that sweeps as the camera moves. Anisotropic highlights are the standard model for brushed metal, hair and fibres, classically via the Heidrich–Seidel distribution for parallel-groove surfaces (source: https://en.wikibooks.org/wiki/GLSL_Programming/Unity/Brushed_Metal, retrieved 2026-07-29) **[search-level]**.

**Generated images almost always draw the grain lines and omit the cross-band.** Check for that specifically.

**Spectral behaviour, art-directed.**

| Metal | Light it with | Never | Tell that it is wrong |
|---|---|---|---|
| Silver / aluminium | Anything; reflections arrive near-true | — | A grey diffuse midtone |
| Chrome | Bright **and** pure-black elements; it needs both | A tent with no black in it | Chrome reading as light grey — chrome is *darker* than silver |
| Gold | Warm-neutral sources, warm surrounds, gold or white cards | Cool sky, blue rim light, cool background | A **neutral-white** highlight on gold; gold cannot produce one |
| Copper / brass | Warm sources; if patinated, treat the patina as a separate matte dielectric layer | — | Patina rendered as tinted metal rather than as a diffuse coat |

**Do not cross-polarise metal.** Metal has no diffuse layer, so extinguishing the specular leaves nothing (§2.5).

**Prompt language.** `brushed 6000-series aluminium body, horizontal grain, fine parallel grain streaks running left to right plus one broad vertical sheen band crossing them where the strip light satisfies the mirror angle, no diffuse grey midtone, reflections showing a white softbox above and a black flag on the left, chamfered edge reading as a single thin bright line, anodised matte end caps for contrast`

**AI failures to check.** (a) Fresnel-bright rim plus dull centre — that is plastic. (b) Grain lines with no cross-band. (c) White highlight on gold. (d) Chrome as light grey. (e) Metal reflecting an environment that is not in the scene, or reflecting nothing at all. (f) Grain direction changing across a single continuous panel.

### 4.4 Plastics — and the mould marks you must keep

SPI (Plastics Industry Association) mould finish grades with the roughness that produces them (source: https://www.rpproto.com/blog/injection-molding-surface-finish-standards-spi, retrieved 2026-07-29) **[verified]**:

| Grade | Ra (µm) | Method | Reads as | Roughness slider |
|---|---:|---|---|---:|
| A-1 | 0.012–0.025 | 6000 grit diamond | Optical / mirror | 0.02–0.05 |
| A-2 | 0.012–0.025 | 3000 grit diamond | High-gloss transparent | 0.03–0.06 |
| A-3 | 0.05–0.10 | 1200 grit diamond | Premium gloss | 0.08–0.15 |
| B-1 | 0.05–0.10 | 600 grit paper | Semi-gloss | 0.15–0.22 |
| B-2 | 0.10–0.15 | 400 grit paper | Semi-gloss | 0.22–0.30 |
| B-3 | 0.28–0.32 | 320 grit paper | Low semi-gloss | 0.30–0.38 |
| C-1 | 0.35–0.40 | 600 grit stone | Matte | 0.40–0.48 |
| C-2 | 0.45–0.55 | 400 grit stone | Matte | 0.48–0.55 |
| C-3 | 0.63–0.70 | 320 grit stone | Deep matte | 0.55–0.62 |
| D-1 | 0.80–1.00 | Dry blast, glass bead | Fine texture | 0.62–0.70 |
| D-2 | 1.00–2.80 | Dry blast | Visible texture | 0.70–0.82 |
| D-3 | 3.20–18.0 | Dry blast | Coarse texture | 0.82–0.95 |

**Soft-touch.** Either a sprayed polyurethane coating or a laminated textured film. The trade describes the hand feel as velvet-, suede-, peach-skin- or rubber-soft (source: https://pakfactory.com/blog/soft-touch-coating-vs-soft-touch-lamination/, retrieved 2026-07-29) **[search-level]**. Optically it is **roughness 0.75–0.90 with a strong sheen lobe** — no highlight anywhere except a halo at the silhouette. It absorbs light, so a soft-touch black box needs **+1 to +1.5 stops** over a gloss black box for the same exposure. Fingerprints and skin oils appear as **darker, glossier patches** because they locally fill the micro-texture.

**Contested.** Sources disagree on whether soft-touch resists or attracts fingerprints. One states the coating "forms a durable layer that resists fingerprints, scratches, and moisture"; another states soft-touch lamination "may exhibit greater sensitivity to fingerprints, smudges, and surface abrasions compared to other finishes" (sources: https://pakfactory.com/blog/soft-touch-coating-vs-soft-touch-lamination/ and https://refinepackaging.com/blog/soft-touch-coating-vs-soft-touch-lamination/, both retrieved 2026-07-29) **[search-level, in conflict]**. Practical reading: sprayed coatings are more durable, laminated films mark more readily. Shoot soft-touch with cotton gloves regardless.

**Injection-moulding marks that must be preserved.**

| Feature | Real dimension | Where it is | Why it matters |
|---|---|---|---|
| **Parting line** | 0.05–0.3 mm ridge or witness line | Around the geometric widest silhouette (the draw line), continuous, never interrupted | The single most reliable "this is a real product" tell for hardgoods |
| **Draft angle** | 0.5°–3° typical; **+1° per 0.001 in of texture depth** on textured walls | All side walls | Perfectly vertical walls read as CGI |
| **Ejector pin marks** | Circular, ~3–8 mm, slightly proud or recessed | Non-cosmetic face, usually the base | Confirms a real tool |
| **Sink marks** | Soft dimples 0.05–0.3 mm deep | Opposite thick sections: ribs, bosses, handle roots | Only visible under grazing light |
| **Wall thickness** | 2–5 mm, uniform | Everywhere | Uneven walls cause the sinks above |
| **Gate vestige** | Small nub or scar, 1–3 mm | Hidden — inside a cap skirt, under a base | Real tools leave one |

Draft-angle and wall-thickness figures from (source: https://blog.epectec.com/design-guidelines-for-injection-molding-parts, retrieved 2026-07-29) and (source: https://texasinjectionmolding.com/design-guide/, retrieved 2026-07-29) **[search-level]**; parting-line placement practice from (source: https://evokpoly.com/feeds/blog/injection-molding-parting-line, retrieved 2026-07-29) **[search-level]**.

**Prompt language.** `soft-touch matte black cosmetic tube, velvety surface with no specular highlight except a faint sheen halo along the left silhouette, glossy black injection-moulded cap at SPI A-2 finish showing one crisp vertical strip reflection, a visible 0.2 mm mould parting line running vertically down each side of the cap at its widest point, 1 degree draft on the tube walls, faint ejector-pin witness circle on the base, one thumbprint reading as a slightly glossier darker patch on the tube`

**AI failures.** (a) Soft-touch rendered as flat grey with no grazing halo, or as rubber with a bright highlight. (b) No parting line anywhere on an injection-moulded object. (c) Parting line drawn as a decorative groove that stops halfway. (d) Perfectly vertical walls with sharp 90° base corners. (e) Gloss cap whose highlight shape does not match the highlight shape on any other glossy surface in the frame.

### 4.5 Paper, board and print finishes

| Stock | Roughness | Ink / colour behaviour | Grazing-light signature |
|---|---:|---|---|
| **Uncoated** (offset, laid, wove) | 0.60–0.85 | Ink absorbs into exposed fibres; tones soften and sharpness drops (source: https://www.printing.com.sg/knowledge-base/coated-vs-uncoated-paper/, retrieved 2026-07-29) **[verified]** | Directional fibre texture; the cut edge shows a fuzzy fibre halo |
| **Coated gloss** | 0.10–0.25 | Pigments stay on the surface — sharper detail, higher contrast **[verified, same source]**; reflects strongly and shows fingerprints | The whole sheet acts as a slightly wavy mirror; you see the softbox as one large soft rectangle |
| **Coated silk / matte** | 0.35–0.50 | As sharp as gloss without the mirror | Broad even glow, no source shape |
| **Kraft / recycled board** | 0.65–0.85 | Fibre specks 0.2–2 mm, visible colour variance | Matte with speck-level micro-shadows |
| **Matte / soft-touch lamination** | 0.70–0.90 | Deepens blacks, mutes colour | Sheen only at the silhouette |

| Finish | Physical spec | Optical behaviour | Lighting required | Prompt phrase |
|---|---|---|---|---|
| **Foil stamp** (hot foil) | Metallised film transferred under heat and pressure; typically leaves a 0.02–0.1 mm deboss where the die pressed **[UNVERIFIED — deboss depth is practitioner-typical; the primary source at madegooddesigns.com returned HTTP 401]** | A **true mirror in a small area**, roughness < 0.05 | **The #1 foil failure: gold foil goes brown and dead because nothing bright sits in its mirror family.** Add a dedicated small source or white card angled at the foil plane, separate from the key | `hot-stamped gold foil logo behaving as a small mirror, reflecting one bright warm card so it reads as metal rather than brown ink, sitting in a shallow deboss` |
| **Spot UV** | Raised clear gloss varnish; needs **157 gsm or heavier**, works best over matte or soft-touch lamination; on uncoated stock the varnish absorbs and definition drops (coated-preference point verified at https://www.printing.com.sg/knowledge-base/coated-vs-uncoated-paper/, retrieved 2026-07-29 **[verified]**; the 157 gsm minimum is **[search-level]** — madegooddesigns.com returned 401) | Pure specular contrast; the ink underneath is unchanged | **Spot UV is invisible under flat frontal light.** It appears only when a source sits in its family of angles — use one raking or one narrow strip source | `clear raised spot-UV gloss over soft-touch matte, invisible in the shadow half of the sheet, catching a single soft strip reflection on the lit half` |
| **Emboss / deboss** | Depth typically **0.2–1.0 mm** | Pure geometry, no material change | **Raking source 10–25° above the sheet plane**, casting a 0.5–3 mm shadow on the far side and a highlight on the near side. Under flat light emboss vanishes | `blind deboss 0.5 mm deep, raking light from the left so each letter casts a 1 mm shadow along its right edge and a bright edge on its left` |
| **Die-cut edge** | Cut edge shows substrate colour, not print | Uncoated edges are fuzzy; coated edges clean; laminated edges show a hairline of film | Needs a low source to separate it from the background | `die-cut window with a clean coated edge showing the white paper core as a hairline` |
| **Corrugated flute** | E-flute ≈ 1.6 mm, B ≈ 3.2 mm, C ≈ 4 mm board thickness **[UNVERIFIED — standard packaging-trade figures, not page-verified here]** | Regular ridge telegraphing through the liner under grazing light; the exposed edge shows the flute profile | Rake across the flute direction | `E-flute corrugated edge visible at the box opening, faint regular flute ridges telegraphing through the printed liner under raking light` |

**The rule for all print finishes: they are specular events, not colour events.** They exist only when there is something for them to mirror. Photograph them with a **second exposure aimed at the finish plane** and composite, or accept that key-lighting the sheet will kill the finish.

### 4.6 Ceramic — glazed and unglazed

**Glazed.** A glass layer (n ≈ 1.5–1.6, F0 4.3–5.3%) over an opaque diffuse body. Two-layer signature:

- Small, well-defined specular (roughness 0.05–0.20) sitting **on top of** a bright diffuse.
- **Glaze pools thicker at concave transitions** — the inside of a bowl's curve, the handle-to-body junction, the ring above the foot. Pooled glaze is **darker, more saturated and glossier**. This is the detail that separates real ceramic from plastic in a render.
- **Crazing**: a fine crack network of 0.1–0.3 mm lines, **in the glaze only**, following no directional pattern.
- Kiln artefacts: pinholes 0.2–1 mm, iron specks, a bare unglazed foot ring, one small kiln-stilt mark.

**Unglazed stoneware / bisque / terracotta.** Roughness 0.60–0.80, mineral grain 0.1–0.5 mm, sheen only at grazing. **Porous**: a wet ring darkens the clay locally and takes minutes to dry. A drip on unglazed clay does not bead — it soaks in and leaves a dark halo with a soft edge. Terracotta has a warm, slightly translucent 1–2 mm surface layer.

**Setup.** Glazed: medium source, feathered, so the specular is a defined shape and the diffuse carries the form; black card on the shadow side to give the glaze an edge to read against. Unglazed: raking source at 15–25° to bring out grain, plus 2 stops of fill so the texture does not crush.

**Prompt language.** `hand-thrown glazed stoneware bowl, celadon glaze pooling darker and glossier in the interior curve and in the ring above the unglazed foot, fine crazing network in the glaze only, three small iron specks, exposed grey clay foot ring with visible 0.3 mm mineral grain and no gloss, one soft specular ellipse on the rim reflecting a single overhead diffusion panel`

**AI failures.** (a) Glaze specular too broad, so it reads as plastic. (b) No glaze pooling — uniform gloss everywhere. (c) Unglazed clay rendered as concrete: too grey, too uniform, wrong grain scale. (d) Crazing drawn on the clay body instead of in the glaze. (e) A fully glazed foot ring — real pots are unglazed where they touch the kiln shelf.
