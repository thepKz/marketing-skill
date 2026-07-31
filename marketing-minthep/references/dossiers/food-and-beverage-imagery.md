# Food and beverage imagery — craft dossier

Recurring worked example: Vietnamese noodle soup, principally **bún bò Huế** (annatto-orange
lemongrass beef broth, thick round rice noodle) and **phở** (clear or lightly cloudy beef broth,
flat rice ribbon). Everything here is written so a production decision can be made from it: a
number, a named setting, a decision rule, or an explicit "we do not know."

Retrieval date for all external facts: **2026-07-29**. Claim markers follow the house convention in
`README.md`: `[verified]` = page fetched and read; `[search-level]` = search summary only, re-check
before client use; `[illustrative]` = invented number to make arithmetic followable, never
publishable; `[UNVERIFIED - …]` = named gap.

Physics, optics, colour and arithmetic carry no citation. Every such claim below is shown with its
derivation so it can be re-checked by hand with a calculator.

Cross-references inside this skill: `dossiers/light-and-shadow.md` (falloff, hardness geometry,
shadow taxonomy), `dossiers/materials-and-surfaces.md` (BRDF model, liquid playbooks, row 13 is the
hot-food setup), `dossiers/composition-and-layout-vision.md` (crop grammar, safe zones,
multi-ratio recomposition), `dossiers/resolution-sharpening-output.md` (PPI arithmetic, format
economics), `dossiers/menu-design-and-engineering.md` (the Kasavana & Smith matrix and print specs).
This file does not repeat those; it specialises them to food, and to soup in particular.

---

## 0. The five questions that decide every food image

Answer these before touching a light. Each has a deciding variable, not a preference.

| # | Question | Deciding variable | Consequence if wrong |
|---|---|---|---|
| 1 | What is the **hero surface**? Broth? A seared face? A cut section? | Which surface must carry the specular highlight | The eye lands on the bowl rim or the table, not the food |
| 2 | What is the **dish geometry**? Flat, mounded, tall-layered, or a liquid in a vessel? | Camera elevation (§2) | Relief collapses, or the plan view collapses |
| 3 | What **size will this be seen at**? 96 px thumbnail, 1080 px feed, A3 print? | Luminance contrast budget (§10) and sharpening chain | Bowl reads as one warm blob at thumbnail |
| 4 | Is this an **advertisement or a document**? | The honesty line (§8) | Legal exposure; in Vietnam a fine measured in tens of millions VND |
| 5 | Is the frame **single-ratio or multi-ratio**? | Bowl-to-frame-width ratio (§12) | 9:16 crop amputates the bowl |

If the answers to 2 and 3 conflict — e.g. a mounded bowl that must survive a 96 px delivery-app
thumbnail — question 3 wins. Thumbnail legibility is a hard constraint; angle is a soft one.

---

## 1. What makes food read as appetising, and what the evidence actually supports

This field is thick with confident folklore. Below, the perceptual mechanisms are separated from
the vendor myths, with the evidence for each verdict. §15 collects the folklore ledger.

### 1.1 Luminance statistics: the strongest evidence-backed lever

The single most useful published finding for food imagery is that **the shape of the luminance
histogram inside the food region — not its mean — drives perceived freshness, moistness and
deliciousness.**

Two independent studies:

- Fish-eye freshness. Three horse mackerel were photographed over 3.29 hours; eye patches were cut
  at 0, 1.63 and 3.29 h; 11 participants ran 720 paired comparisons, scored with a Bradley–Terry
  model. Perceived freshness fell with degradation, F(2,40)=36.03, p<.01. A multiple regression on
  four luminance-distribution parameters (mean, standard deviation, skewness, kurtosis) gave
  R²=.74, F=8.43, p<.05, and **only the standard deviation was a significant positive predictor,
  with the largest standardised coefficient, .79**. The authors link this to surface wetness.
  `[verified]` (source: https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0058994,
  retrieved 2026-07-29)
- Direct manipulation. Luminance SD was scaled by K = 0.5, 2.0, 3.0 while holding chromaticity,
  mean luminance and skewness constant, on two Baumkuchen cakes and two tomato ketchups, 13
  participants aged 20–23 per experiment. "Moistness and deliciousness in appearance decreased with
  increasing the magnification factor K" (p<0.01). Ketchup: watery appearance and tomato-flavour
  impression changed (p<0.0001 and p=0.044). Effects carried through to *reported taste*: cake
  moistness and deliciousness of the taste changed significantly (p<0.01); ketchup wateriness in
  taste changed (p=0.017, p=0.027). `[verified]` (source:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC7528116/, retrieved 2026-07-29)

Read those two together carefully, because they point in opposite directions on K and that is the
interesting part. The fish study says *higher* SD correlates with *fresher*. The cake study says
*artificially expanding* SD makes food look *less* moist. There is no contradiction: expanding SD
by a global gamma-like stretch raises contrast everywhere, including in the diffuse body of the
food, which reads as dry and crusty. Freshness comes from **high local SD confined to the specular
layer over a low-SD diffuse body**. That is a spatially structured histogram, not a global one.

**Operational rule for broth.** Do not raise global contrast on a bowl of soup. Raise the SD of a
narrow, bounded region — the sheen band on the broth surface and the wet edges of the meat — and
leave the broth body flat. In practice: a luminosity-masked local-contrast lift restricted to the
top 12–18 % of the tonal range inside the bowl, and nothing outside it. If you take one thing from
this dossier into a retouch brief, take that sentence.

### 1.2 Gloss and wetness

Gloss is the perceptual read-out of the *specular* term of the BRDF (see
`dossiers/materials-and-surfaces.md`). It is not a colour. Shininess contributes to perceived
freshness of strawberries and carrots, and moistness/wateriness can be modulated by altering
luminance information alone, exactly as glossiness can `[search-level]` (source:
https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0058994, retrieved 2026-07-29 —
the strawberry/carrot claims appear in the surrounding literature summary, not in the fish study
itself, so treat them as search-level until the primary papers are pulled).

The important consequence is directional: **you cannot add gloss in post without adding a light
source.** A specular highlight is a mirror image of a light source. If you paint one in, its shape,
colour temperature and position must be consistent with the highlights on every other glossy
surface in the frame. §14 lists this as one of the highest-yield AI/composite detection tests.

### 1.3 Freshness cues that are actually cues

A 2024 *Foods* study, Tran et al., 122 participants (ages 21–61, 72 % female, 70 % European), rated
photographed prepared vegetables on a 7-point freshness scale. Findings `[verified]` (source:
https://pmc.ncbi.nlm.nih.gov/articles/PMC11507573/, retrieved 2026-07-29):

- **Cut geometry beat everything.** Stick shapes scored significantly higher than large or small
  cubes, attributed to easier recognition of the vegetable and association with minimal processing.
- **Number of vegetables did not matter** (p = 0.79).
- **Mixed shapes did not help.** Uniform stick preparation was optimal.
- **Colour mattered only conditionally**: green bell pepper read fresher than yellow *only* in stick
  form.
- Beetroot presence substantially reduced freshness ratings.

Transfer to a noodle-soup bowl: **recognisability of the cut is a freshness cue.** A julienne of
banana blossom that still reads as banana blossom scores; the same volume chopped to confetti does
not. Shred bắp chuối along the grain into visible ribbons 40–60 mm long, not 10 mm chips. Keep the
onion rings whole rings, not diced. Slice the beef against the grain thin enough that the muscle
striation is visible at output size — at 1080 px across a 180 mm bowl, 1 mm of real width is about
6 px, so striation at 1 mm pitch is resolvable; at a 96 px thumbnail it is 0.5 px and gone, so at
thumbnail you rely on outline and colour only (§11).

### 1.4 Garnish: which garnish, and why

A Frontiers in Psychology 2021 study, Kokaji & Nakatani, 15 participants (11 F, 4 M, mean age 22.0),
26 plated stimuli — one ungarnished control plus 25 garnish variants, each garnish sized to "fill
the blank space next to the main dish." Factor analysis then multiple regression. Two factors
affected appetite: Factor 1 "warm and non-sweet" (p<0.01, standardised coefficient 0.27) and
Factor 2 "fresh and refreshing" (p<0.001, standardised coefficient **0.80**). Sudachi citrus was
the best single garnish for balancing taste and appearance of freshness; moist, sour garnishes were
most effective. `[verified]` (source:
https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.699218/full, retrieved
2026-07-29)

Caveat you must carry: n=15, Japanese participants, plated Western/Japanese dishes, and the effect
is on rated appetite for a photograph. Do not present this as a law. But the direction is a gift
for Vietnamese noodle soup, because the canonical garnish set *is* the "fresh and refreshing"
factor: lime wedge, cilantro, spring onion, raw onion, banana blossom, mint, basil, perilla,
Vietnamese coriander, saw-tooth herb, mung bean sprouts `[verified]` (source:
https://en.wikipedia.org/wiki/B%C3%BAn_b%C3%B2_Hu%E1%BA%BF, retrieved 2026-07-29).

**Operational rule.** One garnish decision in a bún bò frame does more than the rest together: a **cut
lime with a visible wet cut face catching a specular highlight**, positioned so its highlight is
the second-brightest specular in the frame after the broth sheen. It delivers Factor 2 (fresh,
sour, moist) and a high-SD micro-region (§1.1) in one object. A whole uncut lime delivers neither.

### 1.5 What makes food read as *repellent*, with the perceptual reason

This list is more useful than the appetising list, because the failures are systematic.

| Repellent cue | Perceptual/physical reason | Fix |
|---|---|---|
| **Skinned-over broth surface** | A cooled fat/protein film raises surface roughness, breaking the coherent specular into scattered micro-glints; reads as "old" via the same SD channel as §1.1, but with SD in the *diffuse* body rather than the specular layer | Skim, then reheat, then shoot within 90 s; or shoot the broth pour separately |
| **Grey meat** | Myoglobin oxidation and surface drying lower chroma and raise diffuse reflectance; the meat loses hue separation from the broth (§10) | Slice from the interior of the cut immediately before the frame; never re-use a slice that has sat |
| **Congealed fat blobs with hard edges** | Solidified fat has a *matte* surface and a hard geometric edge; liquid fat has a circular meniscus and a bright rim highlight. The hard matte edge is the tell | Keep broth ≥ 70 °C at the frame; use a hot-plate under the bowl |
| **Wilted herb** | Loss of turgor collapses the leaf's specular plane into many small facets and lowers the translucency the backlight needs (§5.2) | Garnish last; see the decay clock in §7 |
| **Uniform mid-grey mush at thumbnail** | Broth and herb are near-isoluminant (derived in §10): contrast ratio 1.27:1. Downsampling destroys chroma detail before luminance detail | Force a light element and a dark element into the bowl (§10.3) |
| **Blue or green cast in the broth** | Warm dishes carry a strong learned hue prior; a cyan shift in a 20–30° hue object reads as spoilage, not as style | White-balance on the noodle, not on the bowl rim, then verify broth hue is 18–35° |
| **Cutlery with residue, or a dirty rim** | Contamination cue; also an explicit rejection criterion on delivery platforms — Uber Eats forbids images that "depict an unsanitary environment (including dirty surfaces, plating/packaging, or used cutlery)" `[verified]` (source: https://help.uber.com/en/merchants-and-restaurants/article/merchant-submitted-menu-catalog-photo-guidelines?nodeId=6985355b-0426-4523-94f2-89bb9b0566e9, retrieved 2026-07-29) | Wipe the rim with a cotton bud after the last garnish, on every frame |
| **Steam that looks like smoke** | Smoke has a grey-brown body and slow, coherent, ropy motion; steam is white and dissipates within ~200 mm of the surface. A frame with steam plumes 400 mm tall reads as burnt food or as a fake | Cap plume height (§6) |
| **Visible prop** | Immediate credibility collapse; also a legal issue if the prop carries a product claim (§8) | See the prop legality decision rule in §8.4 |

---

## 2. Angle grammar, derived

The photographic literature offers a rule of thumb — "flat dishes flat-lay, tall dishes eye-level,
everything else starts at 45°" — and asserts 45° is the commonest commercial angle because you see
the top and some of the front, height is visible, texture is readable, depth is implied, and it
matches the diner's own view `[search-level]` (source:
https://expertphotography.com/best-camera-angles-food-photography, retrieved 2026-07-29 — that page
does confirm the 3/4 band as 25–75° with 45° as the common value and 30° as the background-revealing
variant, and states a salad bowl benefits from 45° over 30° "to see deeper into the contents"
`[verified]`).

That is folklore with a real geometric core. Here is the core.

### 2.1 The projection identity

Let **φ** be camera elevation above the plane of the table (φ = 0° is dead level with the rim,
φ = 90° is straight down). Under orthographic projection — which a 100 mm lens at 0.6–0.9 m is close
enough to for this purpose — a feature of **vertical** height *m* (a noodle mound, a standing meat
slice, the bowl wall) projects into the frame with vertical extent

```
relief(φ) = m · cos φ
```

and a feature of **horizontal** length *L* lying in the table plane (the rim diameter, the spread
of garnish across the surface) projects with extent

```
plan(φ) = L · sin φ
```

Both follow from resolving the feature vector onto the image plane, whose normal is tilted φ from
the table normal.

| φ | relief kept | plan kept | product sinφ·cosφ | What this angle is *for* |
|---|---|---|---|---|
| 0° | 100 % | 0 % | 0.000 | Layer stacks: bánh mì cross-section, a glass of cà phê sữa đá, a burger. Zero information about a bowl's contents |
| 15° | 97 % | 26 % | 0.250 | Nothing, for soup. See §3.2 — the broth becomes a mirror here |
| 25° | 91 % | 42 % | 0.383 | Soup where the *build* is the hero: a tall noodle mound, standing pork knuckle, steam column |
| 30° | 87 % | 50 % | 0.433 | Default bún bò hero. Rim ellipse reads 2:1 |
| 35° | 82 % | 57 % | 0.470 | Default phở hero. The sweet spot when both broth surface and topping relief matter |
| 45° | 71 % | 71 % | **0.500** | The maximum of the product. Universal safe default |
| 55° | 57 % | 82 % | 0.470 | Bowls with a busy *surface* pattern and low relief |
| 60° | 50 % | 87 % | 0.433 | Multi-bowl table spreads where you need each rim readable |
| 75° | 26 % | 97 % | 0.250 | Near-plan. Composed sets, chopstick/spoon geometry, colour-block layouts |
| 90° | 0 % | 100 % | 0.000 | Flat-lay. All vertical relief is *mathematically* destroyed. Only colour, outline and shadow survive |

**Why 45° is the default is now a theorem, not a taste.** The product sinφ·cosφ = ½ sin 2φ is
maximised uniquely at φ = 45°, value 0.500. 45° is the elevation that maximises the geometric mean
of relief information and plan information. That is the whole content of the folklore. It also tells
you the cost of deviating: moving from 45° to 30° costs 13 % of the product (0.433/0.500) but buys
you +16 percentage points of relief — a good trade whenever the vertical build is the selling point.

**The corollary photographers get wrong.** Because the product is symmetric about 45°, **30° and
60° carry the same total geometric information.** They differ only in *which* they favour. Anyone
who tells you 30° is "more dramatic" than 60° is describing the reflectance change (§3.2), not the
geometry.

### 2.2 Mapping dish geometry to φ, for real Vietnamese dishes

| Dish | Geometry | φ | Reason |
|---|---|---|---|
| Bún bò Huế, full bowl with knuckle | Liquid + tall relief | **28–32°** | Knuckle and noodle mound are the value signal; broth still 86 % visible (§3.1) |
| Phở bò, thin bowl, rare beef laid flat | Liquid + low relief + surface pattern | **35–42°** | Beef fan and noodle are surface pattern; needs plan |
| Phở gà with quẩy on the side | Liquid + external prop | **35°** and a second frame at **60°** | 60° gets both vessels legible in one rim plane |
| Bún chả cá, clear broth with visible submerged solids | Liquid, hero is *in* the liquid | **45–55°** | Refraction path length through the broth is shortest nearer nadir (§3.4) |
| Bánh mì | Layer stack | **0–8°** | Section is everything |
| Cà phê sữa đá, layered | Layer stack in glass | **0°**, camera axis level with the layer boundary | Any φ > 0 makes the boundary an ellipse and the layers ambiguous |
| Nem nướng platter, flat arrangement | Flat, spread | **75–90°** | Relief is negligible; plan carries it |
| Bánh xèo, folded crêpe | Mounded, matte, texture-led | **20–30°** | Grazing light plus low φ reads the crisp texture |
| Chè in a tall glass | Layer stack, translucent | **0–5°** with backlight | §5.2 transillumination |

### 2.3 Azimuth, which nobody talks about and which matters

Elevation is only half the angle. Azimuth (the compass bearing of the camera around the bowl) sets:

1. **Which garnish is foremost.** Place the lime wedge and the highest-chroma herb on the camera-near
   arc, at 150–210° in bowl coordinates where 180° is nearest camera. Garnish on the far arc is
   occluded by steam and by the noodle mound.
2. **The direction of the noodle grain.** A noodle mound has a lay direction. Rotate the bowl so
   the lay runs 20–35° off the frame horizontal — parallel to the frame reads as manufactured;
   perpendicular reads as a barrier.
3. **Whether the spoon leads the eye in or out.** A Vietnamese soup spoon placed with its bowl at
   the near-left and handle exiting frame-right at roughly 30–40° from horizontal reads as an entry
   vector. Handle exiting toward the top of frame reads as an exit.

Log azimuth in the shot list as a bowl-clock value (12 o'clock = away from camera) so a reshoot is
reproducible. Most food shot lists omit it and are therefore not reproducible.

---

## 3. The specific problem of soup and broth

This is the hardest common subject in food photography, for four reasons that are all physics.

### 3.1 Occlusion: the near rim eats the broth

Take a standard bún bò bowl: inner diameter **D = 180 mm**, broth surface **h = 15 mm** below the
rim (that freeboard is what stops it slopping; you cannot fill to the rim). The near rim occludes a
band of the broth surface against the near wall, of width

```
b(φ) = h / tan φ
```

| φ | b (mm) | Broth diameter still visible | Rim ellipse minor/major = sin φ |
|---|---|---|---|
| 15° | 56.0 | 124 mm (69 %) | 0.259 → 3.9 : 1 slit |
| 20° | 41.2 | 139 mm (77 %) | 0.342 |
| 25° | 32.2 | 148 mm (82 %) | 0.423 |
| 30° | 26.0 | 154 mm (86 %) | 0.500 → 2 : 1 |
| 35° | 21.4 | 159 mm (88 %) | 0.574 |
| 40° | 17.9 | 162 mm (90 %) | 0.643 |
| 45° | 15.0 | 165 mm (92 %) | 0.707 → 1.41 : 1 |
| 60° | 8.7 | 171 mm (95 %) | 0.866 |
| 90° | 0 | 180 mm (100 %) | 1.000 → circle |

Check one row by hand: tan 30° = 0.5774; 15 / 0.5774 = 25.98 mm, which is the tabled value.

**Consequences.**
- Below φ ≈ 22° you lose more than a quarter of the broth surface. Any garnish you laid on the near
  arc is now behind a wall of ceramic.
- The freeboard *h* is a variable you control. Dropping *h* from 15 mm to 8 mm by using a **shallower,
  wider bowl** halves the occluded band at every angle: at 25°, b falls from 32.2 mm to 17.2 mm.
  This is the honest, legal version of the marbles trick (§8.2): change the vessel, not the contents.
  A wide shallow bowl brings solids near the surface *because it is genuinely shallow*, and the
  customer receives the same volume in the same vessel.
- Bowl wall thickness is a second lever. A 4 mm rim reads as a hairline at φ = 30°; a 12 mm rustic
  rim reads as a parapet. For thumbnails prefer a thin rim.

### 3.2 Reflectance: broth is a mirror at low angles

Broth is water plus dissolved solids; take **n ≈ 1.333**. Normal-incidence Fresnel reflectance:

```
R₀ = ((n − 1)/(n + 1))²  =  (0.333 / 2.333)²  =  0.14274²  =  0.0204  →  2.04 %
```

At other angles, Schlick's approximation R(θ) = R₀ + (1 − R₀)(1 − cos θ)⁵, with θ the angle from the
surface normal. Since the broth surface is horizontal, **θ = 90° − φ**.

| Camera elevation φ | Incidence θ | (1 − cos θ)⁵ | R(θ) | Broth behaves as |
|---|---|---|---|---|
| 90° | 0° | 0 | 2.04 % | Nearly pure diffuse — you see the broth's own colour |
| 60° | 30° | 0.0000431 | 2.04 % | Same |
| 45° | 45° | 0.002155 | 2.25 % | Controllable sheen |
| 35° | 55° | 0.014100 | 3.42 % | Distinct sheen band |
| 25° | 65° | 0.064168 | 8.32 % | Strong reflection; ceiling starts to appear |
| 15° | 75° | 0.223674 | 23.9 % | Mirror |
| 10° | 80° | 0.385460 | 39.8 % | Mirror |
| 5° | 85° | 0.633828 | 64.1 % | Mirror; the broth's colour is gone |

Check the 25° row: cos 65° = 0.42262; (1 − 0.42262) = 0.57738; 0.57738² = 0.33337; ⁴ = 0.111136;
× 0.57738 = 0.064168; R = 0.0204 + 0.97963 × 0.064168 = 0.0204 + 0.06286 = 0.0833, which is the tabled value.

**This is the real reason low angles "look dramatic" and also why they fail.** Between φ = 45° and
φ = 25° the broth's mirror term nearly quadruples (2.25 % → 8.32 %). Between 45° and 15° it rises
**10.6×**. Below about 12° you are no longer photographing broth; you are photographing whatever is
above the bowl, tinted by broth. If your ceiling is a white gridded office ceiling, that is what is
in your soup.

**Operational rules that fall straight out.**
- **Ceiling control is not optional below φ = 30°.** Rig a 1.2 × 1.2 m black cloth above and slightly
  camera-side of the bowl. Cost: nothing. Effect: turns the 8 % mirror term into a controlled dark
  field against which you then *place* one intended highlight.
- **Place the intended reflection deliberately.** Angle of incidence = angle of reflection. If the
  camera is at elevation φ on the near side, the broth mirrors whatever sits at elevation φ on the
  far side, in the same vertical plane. So a strip softbox at **elevation 30°, azimuth 170–180°**
  will be seen reflected in the broth by a camera at elevation 30°. That reflected strip *is* the
  broth sheen. Move the strip up and the sheen slides toward the far rim; move it down and the sheen
  slides toward the near rim and grows.
- **Sheen band width is set by the light's angular size, not its power.** A 30 × 90 cm strip at
  0.7 m subtends about 24° along its long axis (2·arctan(0.45/0.7) = 2 × 32.7° = 65° long axis;
  2·arctan(0.15/0.7) = 2 × 12.1° = 24° short axis). The short axis governs the band's depth in the
  broth. Want a narrower ribbon of sheen? Narrow the strip or move it further, not dimmer.

### 3.3 The polariser window, derived

Brewster's angle is where reflected light is fully linearly polarised, so a linear/circular
polariser on the lens can null it completely:

```
θ_B = arctan(n₂/n₁)
water, n = 1.333 :  θ_B = arctan(1.333) = 53.11° from normal  →  camera elevation 36.89°
oil,   n = 1.47  :  θ_B = arctan(1.47)  = 55.77° from normal  →  camera elevation 34.23°
```

**A polariser is maximally effective on a broth surface when the camera sits ≈ 37° above the table,
and on a surface fat film at ≈ 34°.** Those two numbers land inside the 30–40° band that §2 already
identified as the soup default. That is a genuinely useful coincidence: the default soup angle is
also the angle at which you have maximum *optical control* over the broth's specular.

At φ = 90° (flat-lay) θ = 0° and the reflection is unpolarised — **a polariser does essentially
nothing to a flat-lay of soup.** People who report "the polariser didn't help" are usually shooting
overhead. Conversely at φ = 10° the reflection is strong but far from Brewster, so a polariser
reduces it partially and leaves a colour-shifted residue.

**Cost.** A polariser costs light. Practically budget **1.3–2 stops** depending on the filter and
how much of the field is polarised `[UNVERIFIED - I did not fetch a measured transmission figure
for a specific filter; the fetched cross-polarisation reference explicitly gives no f-stop loss
number (source: https://www.allanwallsphotography.com/blog/xpolarization, retrieved 2026-07-29). To
close this, meter a grey card with and without the filter on the actual body and record the delta.]`

**Cross-polarisation** (polariser on every light, aligned; a second polariser on the lens rotated
90° to them) removes specular reflections much more completely, but requires that *all* light in the
scene be polarised — ambient or unpolarised spill defeats it `[verified]` (source:
https://www.allanwallsphotography.com/blog/xpolarization, retrieved 2026-07-29). For soup this is
almost always the wrong tool: killing all specular kills the wet look you came for. Use it only for
a *base layer* in a composite where you will paint the specular back with a second, deliberately
lit pass.

### 3.4 Submerged solids, and the refraction test

Anything below the broth surface is seen through a refracting interface. Two consequences with hard
numbers.

**Apparent depth.** For near-normal viewing, apparent depth = real depth / n = d / 1.333 = **0.75 d**.
A noodle 20 mm below the surface appears 15 mm below it. Broth therefore *always* reads shallower
than it is, which is why deep bowls photograph as though half-empty.

**Lateral kink.** A straight object crossing the surface at angle θ from the vertical appears to
change direction at the surface. Snell: sin θ = n · sin θ′.

| θ (in air, from vertical) | sin θ | sin θ′ = sin θ / 1.333 | θ′ | Visible kink θ − θ′ |
|---|---|---|---|---|
| 30° | 0.50000 | 0.37509 | 22.03° | **7.97°** |
| 45° | 0.70711 | 0.53046 | 32.03° | **12.97°** |
| 60° | 0.86603 | 0.64969 | 40.53° | **19.47°** |
| 75° | 0.96593 | 0.72463 | 46.44° | **28.56°** |

Check the 45° row: 0.70711 / 1.333 = 0.53046; arcsin 0.53046 = 32.03°; 45 − 32.03 = 12.97°, which is the tabled value.

**Use this as a forensic test.** A chopstick or spoon handle entering broth at 45° *must* show a
~13° kink at the surface, and the submerged portion must appear both displaced and slightly
magnified. Composites, hand-painted broth, and generative images almost never render this. It is the
single most reliable physics check for a noodle-soup image (§14.3).

**Use it as a styling instruction too.** If you want the customer to *feel* depth, put a straight
object through the surface at 45–60° so the kink is 13–19° — large enough to read at 1080 px.
Chopsticks entering at 15° from vertical give a kink of only 3.8° and communicate nothing.

### 3.5 Surface fat: how to render it, with the stop difference

Rendered fat (beef tallow, annatto-infused oil, hành phi oil) floats as a film and as lenticular
droplets. Take **n_oil ≈ 1.47**.

```
Air → oil at normal incidence:    R = ((1.47 − 1)/(1.47 + 1))²   = (0.47/2.47)²   = 0.190283² = 3.62 %
Air → water at normal incidence:  R = 2.04 %  (above)
Oil → water at normal incidence:  R = ((1.47 − 1.333)/(1.47 + 1.333))² = (0.137/2.803)² = 0.04888² = 0.24 %
```

Ratio of the top-interface reflectances: 3.62 / 2.04 = **1.775×**, i.e.
log₂(1.775) = **+0.83 stop**.

**So a fat film makes the broth surface reflect about 0.83 stop brighter than bare broth at the same
geometry.** That is the entire visual signal of "rich." It is not colour and it is not texture; it
is a sub-stop specular step. The oil-to-water interface underneath contributes almost nothing
(0.24 %), which is why a *film* looks like a slightly brighter sheet rather than a distinct layer.

**Droplets** are different, and better. A discrete fat droplet on broth has a curved top interface,
so it condenses the reflection of your strip light into a small bright disc with a defined edge —
a high-SD micro-region in exactly the sense §1.1 says drives freshness. A field of 3–8 mm droplets
gives you dozens of them.

**Production controls.**
- Droplet size is set by the fat's surface tension and temperature. Hotter fat spreads to a film;
  cooler fat beads. Practical window: pull the bowl off heat and let surface temperature fall so
  droplets form, then shoot before the fat's edges go matte (§7). At the visual boundary, hard-edged
  matte patches mean the fat has begun to solidify — abort and reheat.
- To *increase* droplet count honestly: spoon the annatto/chilli oil from the pot's surface, where
  the oil that the customer receives already sits, rather than adding oil that is not in the recipe.
  See §8.4.
- To *reduce* an unappetisingly greasy read: skim, don't dilute. Diluting broth to hide fat changes
  the product.

### 3.6 A complete broth-surface setup

Numbers below are a starting point on full-frame; adjust exposure to your body. Setup follows the
logic of `dossiers/materials-and-surfaces.md` row 13, specialised to a 180 mm bowl.

```
Camera        100 mm macro (or 85–105 mm), full-frame, f/5.6, ISO 100
              elevation 30°, distance 0.75 m to bowl centre, bowl centred on a 3:2 master
              polariser fitted, rotated for maximum broth-sheen suppression, then backed off
              15–20° from full null so a controlled sheen survives
Key           30 × 90 cm strip softbox with one layer of diffusion,
              azimuth 175°, elevation 30°, distance 0.70 m from bowl centre, long axis horizontal
              → subtends ~65° × 24°; the 24° short axis sets sheen band depth
Kicker        15 × 60 cm strip, azimuth 240°, elevation 55°, 2 stops under key
              → puts a second, smaller specular on the meat and the lime cut face
Fill          A3 white card, azimuth 340° (camera-near-right), 1.5 m,
              measured 1.5 stops under key on the near rim
Negative      Black flag 1.2 × 1.2 m directly overhead, offset 200 mm camera-side
              (this is the ceiling kill from §3.2 — non-negotiable below φ = 30°)
              Black card at azimuth 0–20°, 250 mm from near rim, to keep the near wall's
              outer face dark and stop the rim glowing
Background    2–3 stops under key. Not pure black (§9.3), not white (§6.2)
Under-bowl    Induction hot plate at low, bowl on a 3 mm cork disc to avoid conducted overheating
              of the ceramic base; broth held 70–80 °C
```

Meter and log: key on broth sheen, fill on near rim, background, and the darkest shadow inside the
bowl. Four readings. Record them; that is what makes the frame repeatable next quarter.

---

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
f = 100 mm that is 1.037 m, as tabled. Then the ratio column is (s + 156 mm)/s.

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

Check one cell: 2 × 5.6 × 0.029 × (1000/100)² = 2 × 5.6 × 0.029 × 100 = 32.5 mm, which is the tabled value.

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
