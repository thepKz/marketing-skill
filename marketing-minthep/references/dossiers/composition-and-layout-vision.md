# Composition and Layout Vision — Research Dossier

## Scope

Composition for commercial still and moving imagery: grid systems and their actual evidence base, visual weight, Gestalt as framing moves, gaze vectors, negative space, depth cues, eye-path models, aspect-ratio semantics, shot size, camera angle, crop grammar, platform safe zones, and multi-ratio recomposition. Written so an AI can pick a composition without taste, and express it inside a text-to-image or text-to-video prompt.

Out of scope: lighting geometry, colour grading, retouching, and copywriting (covered by `realistic-studio-imagery.md`, `makeup-art-direction.md`, `copywriting.md`).

---

## How to use this file

1. Read section 16 (decision table) first. It maps communication job -> shot size + angle + placement + negative-space budget.
2. If a grid is needed, use section 1.4 to choose one, not all.
3. Before export, run section 19 (numeric QA gates).
4. Anything about a platform pixel spec: re-verify against the live doc. Section 14 says exactly which numbers are cached third-party consensus and which are primary.

Evidence labels used throughout:

| Label | Meaning |
|---|---|
| **[PHYSICS]** | Optics/geometry/perception fundamentals. No citation needed. |
| **[PEER-REVIEWED]** | Traced to a named journal paper. |
| **[INDUSTRY-PRIMARY]** | Vendor/platform doc, cited with URL. |
| **[THIRD-PARTY CACHE]** | Number circulating in trade blogs; primary doc not machine-readable. Must re-verify. |
| **[CRAFT HEURISTIC]** | Production convention. Works, but is not a measured constant. |
| **[MYTH]** | Widely repeated, evidence absent or falsified. |

---

## 1. The grid rules, honestly

### 1.1 Rule of thirds — what it is

Divide the frame into 9 equal cells with lines at 33.33% and 66.67% of width and height. Four intersections at (33.3, 33.3), (66.7, 33.3), (33.3, 66.7), (66.7, 66.7).

**Origin.** The phrase was first written down by John Thomas Smith in *Remarks on Rural Scenery* (1797), where he quotes a 1783 remark by Joshua Reynolds about the balance of dark and light, then generalises it to proportions of land/water/sky. Smith named it; he did not invent it — thirds-based division appears in 17th-century landscape painting (source: https://en.wikipedia.org/wiki/Rule_of_thirds, retrieved 2026-07-29). **[PEER-REVIEWED]** for the naming, **[CRAFT HEURISTIC]** for the modern photographic version.

**The evidence that it is a heuristic, not a law.**

| Study | Design | Result |
|---|---|---|
| Amirshahi, Hayn-Leichsenring, Denzler & Redies, "Evaluating the Rule of Thirds in Photographs and Paintings", *Art & Perception* 2(1-2), 2014, 163-182 | Computed rule-of-thirds (ROT) scores across large image sets: a set split into 679 ROT-following vs 403 non-following photographs; 606 near-random scene photos; 200 simple-object photos; 200 Photo.net high-quality photos; 727 Western paintings (188 abstract, 191 portrait, 54 natural scenes, 151 complex scenes with persons) | Aesthetic ratings correlated only weakly with subjective ROT scores and **not at all** with computed ROT values. Authors conclude ROT "seems to play only a minor role, if any" in large sets of high-quality photographs and paintings (source: https://brill.com/view/journals/artp/2/1-2/article-p163_11.xml, retrieved 2026-07-29) |
| Hoh & Zhang, "Rule-of-Thirds or Centered? A study in preference in photo composition", SIGGRAPH Asia 2023 Posters | Forced-choice preference between centred and thirds-placed subject | Participants overwhelmingly preferred the **centred** object (source: https://dl.acm.org/doi/10.1145/3610542.3626121, retrieved 2026-07-29 — abstract-level only, full text 403) |

Contrary evidence worth keeping: eye-tracking work reports that viewers **with photographic training** rate thirds-compliant images as more interesting while novices are insensitive to it (source: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.786977/full, retrieved 2026-07-29). Read together: thirds is a **producer-side convention that reads as "competently shot" to trained eyes**, not a driver of lay preference.

**Operational conclusion.** Thirds is a tie-breaker for where to put a subject when nothing else decides it, and a reliable way to leave a copy field. It is not a reason to move a subject off centre when centring does a job.

### 1.2 When centring beats thirds

| Condition | Why centring wins | Threshold |
|---|---|---|
| Single hero product on seamless | Symmetry reads as authority + product fills more of the frame; ecommerce platforms crop centrally | Product occupancy >=60% of frame area |
| Frame is square or near-square (1:1, 4:5, 3:4) | Thirds intersections sit only 8-13% of frame width from centre in these ratios, so the "off-centre" gesture is too small to read; it just looks like a mistake | Ratio between 0.75 and 1.33 |
| Direct-address portrait, eyes to lens | Centred eyes maximise the parasocial read; off-centre implies the subject is attending to something else | Gaze vector within 10 deg of lens axis |
| Comparison / range / grid-of-SKUs | Centre position gets more fixations and more choices (see 9.4) | Any array of 3+ options |
| The asset will be centre-cropped by a platform | Blind central crop destroys thirds placement; see section 15 | Any auto-cropping placement |
| Radial subject (bowl of soup top-down, watch face, wheel) | The subject's own symmetry axis is the composition; offsetting fights it | Subject has 2+ axes of symmetry |

### 1.3 Golden ratio and the phi grid

**Construction.** phi = (1 + sqrt(5)) / 2 = 1.6180339887. Its reciprocal 1/phi = 0.6180339887. The phi grid places lines at **38.2%** and **61.8%** of each dimension (0.382 = 1 - 0.618).

**Why it barely differs from thirds.** 0.382 vs 0.333 = 4.9 percentage points. On a 1080 px wide frame: 412.6 px vs 359.6 px, a **53 px** difference — roughly one finger-width at phone viewing size. On a 1920 px frame: 94 px. **[PHYSICS]** Any claim that one is visibly superior to the other has to survive a 5%-of-frame perturbation, and none of the studies in 1.1 do.

**Construction of the golden rectangle** (ruler-and-compass, for building an overlay): start with a unit square ABCD. Take the midpoint M of the base. Swing an arc of radius M-to-opposite-top-corner from M down to the extended base; that point E gives base length 1.618. Rectangle on base 1.618 x height 1 is the golden rectangle. Removing the unit square leaves a 0.618 x 1 rectangle, which is golden again (a **gnomon** relationship) — this self-similarity is why the spiral overlay exists.

**The myth layer. [MYTH]** Markowsky, "Misconceptions about the Golden Ratio", *The College Mathematics Journal* 23(1), 1992, 2-19, shows that while the mathematics is usually stated correctly, most claims about phi in art, architecture, literature and aesthetics are false or seriously misleading. On the Parthenon specifically: dimensions differ between sources because authors measure between different points, and parts of the building fall **outside** the golden rectangle that enthusiasts sketch over it (source: https://www.tandfonline.com/doi/abs/10.1080/07468342.1992.11973428 and full text at https://www.goldennumber.net/wp-content/uploads/George-Markowsky-Golden-Ratio-Misconceptions-MAA.pdf, retrieved 2026-07-29).

Related claims to refuse: that phi governs the "ideal face", that Da Vinci or the Great Pyramid encode it deliberately, or that a phi spiral overlay validates a photograph after the fact. Overlaying a spiral on a finished image is unfalsifiable — a spiral can be scaled, rotated and mirrored into 8+ orientations until something lands on it.

**Where phi is legitimately useful.** As a **ratio generator for sizing**, not for placing: type scale (16 -> 26 -> 42 px), margin-to-column ratio, product-to-negative-space split (61.8% / 38.2%). Here it functions as a consistent, non-arbitrary modular scale, which is a real design benefit independent of any aesthetic claim.

### 1.4 Dynamic symmetry (Jay Hambidge) — the actual construction

Hambidge published the system in *The Diagonal* (1919-20) and *The Elements of Dynamic Symmetry* (1926), reverse-engineered from measurements of Greek vases and the Parthenon (source: https://en.wikipedia.org/wiki/Dynamic_rectangle, retrieved 2026-07-29). Same caveat as 1.3: the **historical** claim is contested; the **construction** is a genuinely useful ratio-aware grid.

A **root rectangle** has long side = sqrt(n) x short side.

| Rectangle | Ratio (decimal) | Reciprocal short side | Property | Real-world instance |
|---|---:|---:|---|---|
| Square (root-1) | 1.000 | 1.000 | Static | 1:1 social post |
| Root-2 | 1.4142 | 0.7071 | Halves into two identical root-2 rectangles | ISO 216 paper: A4 = 210 x 297 mm, 297/210 = 1.4143 |
| Golden (phi) | 1.6180 | 0.6180 | Removing the square leaves a golden rectangle | 1.618:1 |
| Root-3 | 1.7321 | 0.5774 | Thirds into three root-3 rectangles | close to 16:9 = 1.7778 |
| Root-4 | 2.0000 | 0.5000 | Two squares | 2:1 |
| Root-5 | 2.2361 | 0.4472 | phi + 1/phi laid side by side | close to 21:9 = 2.3333 |

**Construction of the reciprocal and the "eyes":**

1. Draw both **full diagonals** corner-to-corner. They cross at the exact centre.
2. From one corner, draw a line **perpendicular** to the opposite full diagonal until it meets an edge. The rectangle it cuts off is the **reciprocal** — a scaled, rotated copy of the whole (source: https://en.wikipedia.org/wiki/Dynamic_rectangle, retrieved 2026-07-29).
3. Do this from all four corners. The four **reciprocal diagonals** plus the two full diagonals produce 4 primary intersections — Hambidge's "**eyes**" — plus a set of secondary crossings.
4. Drop verticals and horizontals through the eyes. You now have a grid whose lines are all in whole-number relationships to the frame, so **every subdivision is commensurate with the frame ratio** — the practical advantage over thirds, which imposes 3x3 on any ratio regardless of its proportions.

**Eye positions, computed.** For a rectangle of width W and height H with H < W, the reciprocal-diagonal / full-diagonal intersection sits at:

```
x = W * H^2 / (W^2 + H^2)      y = H * W^2 / (W^2 + H^2)   (measured from the corner)
```

| Ratio | Eye x (% of width) | Eye y (% of height) | Compare: thirds line |
|---|---:|---:|---|
| 1:1 | 50.0 | 50.0 | 33.3 |
| 4:5 (0.8 w/h) | 39.0 | 61.0 | 33.3 |
| 3:2 (1.5) | 30.8 | 69.2 | 33.3 |
| 16:9 (1.778) | 24.0 | 76.0 | 33.3 |
| 2.39:1 | 14.9 | 85.1 | 33.3 |

Read the second column: **the wider the frame, the further from centre dynamic symmetry pushes the anchor** — 24% in 16:9, 15% in scope. Thirds says 33.3% regardless. This is why widescreen cinema composition looks "wrong" on a thirds grid and right on a root grid: **[CRAFT HEURISTIC]**, but a mathematically motivated one.

**Practical shortcut for 16:9 and 2.39:1:** place the primary subject edge on the **24% / 76%** verticals for 16:9 and **15% / 85%** for scope, rather than 33/67.

### 1.5 Grid selection decision table

| Situation | Grid | Anchor to use | Do not use |
|---|---|---|---|
| Ecommerce hero packshot | None — optical centre | Product optical centre on frame centre | Thirds |
| Lifestyle 4:5 feed still with copy | Thirds | Subject eyes on upper third line | Phi spiral |
| 16:9 / 2.39:1 key art | Dynamic symmetry root grid | Subject edge on 24% (16:9) or 15% (scope) | Thirds |
| 9:16 vertical video | Platform safe band (section 14) | Eyes at 38-42% frame height | Any grid that ignores UI chrome |
| Range / SKU array | Centre + equal spacing | Hero SKU dead centre | Off-axis |
| Editorial / fashion spread | Diagonal armature (corner-to-corner) | Subject along the diagonal | Symmetry |
| Type-led poster where image is a field | Phi as a **sizing** ratio | 61.8/38.2 image-to-copy split | Phi as placement mysticism |

---

## 2. Visual weight: a working scoring model

Visual weight = how strongly an element competes for the first three fixations. There is no published unit for it. What follows is an **[CRAFT HEURISTIC]** ordinal scale built so a machine can compute a rough "attention budget" and detect competition; the multipliers are operational, not measured constants.

### 2.1 Relative strength ordering

Ranked strongest to weakest, with the empirical anchor where one exists.

| Rank | Weight driver | Heuristic multiplier | Empirical anchor |
|---:|---|---:|---|
| 1 | **Human face, frontal, eyes visible** | x5.0 | Saccades toward faces begin at **100-110 ms**, mean RT ~140 ms, and are not fully under instructional control — when faces were paired with vehicles, fast saccades were still biased toward faces even when subjects were told to target vehicles. Crouzet, Kirchner & Thorpe, "Fast saccades toward faces: face detection in just 100 ms", *Journal of Vision* 10(4), 2010 (source: https://pubmed.ncbi.nlm.nih.gov/20465335/, retrieved 2026-07-29) **[PEER-REVIEWED]** |
| 2 | **Legible text / numerals** | x4.0 | Text is a learned attentional magnet; **[CRAFT HEURISTIC]** — treat any headline as competing directly with the face |
| 3 | **Isolation (an element alone in a field)** | x3.5 | Feature-contrast / pop-out; consistent with centre-surround saliency in Itti, Koch & Niebur, *IEEE TPAMI* 20(11), 1998, 1254-1259 (source: https://www.cse.psu.edu/~rtc12/CSE597E/papers/Itti_etal98pami.pdf, retrieved 2026-07-29) **[PEER-REVIEWED]** for the mechanism |
| 4 | **Luminance contrast against local surround** | x3.0 | Intensity is one of the three feature channels in Itti-Koch (intensity, colour, orientation), same source |
| 5 | **Sharpness against blur** | x2.5 | **[PHYSICS]** — high spatial frequency survives peripheral low-pass filtering better; this is why DOF separation works |
| 6 | **Size / frame occupancy** | x2.0 (scales with sqrt of area) | **[PHYSICS]** |
| 7 | **Saturation / hue contrast** | x2.0 | Colour channel in Itti-Koch; note saturation alone loses to luminance when both are present |
| 8 | **Hands, especially holding or pointing** | x1.8 | **[CRAFT HEURISTIC]** — second-strongest biological cue after faces |
| 9 | **Convergence of lines on a point** | x1.6 | **[PHYSICS]** (linear perspective) |
| 10 | **Implied motion / diagonal orientation** | x1.4 | Orientation channel in Itti-Koch |
| 11 | **Position: horizontal centre** | x1.3 | Central fixation bias + central gaze cascade, see 9.4 **[PEER-REVIEWED]** |
| 12 | **Position: upper half** | x1.15 | **[CRAFT HEURISTIC]**; interacts with reading direction |
| 13 | **Texture / detail density** | x1.1 | Note: **feature density hurts brand attention**, see 6.3 |

**Important asymmetry:** a face at x5.0 beats a product at x2.0 by 2.5:1. This is the single most common commercial composition failure — a model's face outcompeting the product it is holding. Fixes, in order of strength: (a) turn the gaze onto the product (section 4.3), (b) crop the face out or to partial, (c) reduce face size below 8% of frame area, (d) throw the face 1.5-2 stops darker than the product, (e) put the face out of focus.

### 2.2 Weight arithmetic — worked

Scenario: 4:5 feed still, model holding a 200 ml serum bottle.

| Element | Area % | Base | Multipliers applied | Score |
|---|---:|---:|---|---:|
| Face, frontal, 14% of frame | 14 | 14 | face x5.0, centre x1.3 | 91.0 |
| Bottle, 6% of frame, sharp, isolated on skin | 6 | 6 | isolation x3.5, sharpness x2.5 | 52.5 |
| Headline, 5% | 5 | 5 | text x4.0 | 20.0 |
| Background, 60% | 60 | 60 | blurred (x0.3 penalty) | 18.0 |

Face:bottle = 91:52.5 = **1.73:1** -> the product loses. Remediation: rotate the model's gaze down to the bottle (bottle gains a x1.6 gaze-vector bonus -> 84) and reduce face area to 9% (face -> 58.5). New ratio 84:58.5 = **1.44:1 in the product's favour**. Target ratio for a product-led asset: **hero >= 1.3x the next strongest element**.

### 2.3 What the saliency literature does not cover

Itti-Koch style bottom-up models use intensity, colour and orientation. They do **not** model faces, text, semantic interest, or brand memory. Do not treat a saliency heat-map plugin as a prediction of commercial attention — it systematically underweights faces and text, which are ranks 1 and 2 above. **[PEER-REVIEWED]** limitation of the model class.

---

## 3. Gestalt principles translated into concrete framing moves

Wertheimer's grouping factors were published as "Untersuchungen zur Lehre von der Gestalt II", *Psychologische Forschung* 4, 1923, 301-350; the named factors include proximity, similarity, uniform destiny ("common fate"), good continuation and closure, under the meta-principle of **Praegnanz** (source: https://psychclassics.yorku.ca/Wertheimer/Forms/forms.htm, retrieved 2026-07-29). **[PEER-REVIEWED]** Figure-ground is usually credited to Rubin (1915).

Each row gives the perceptual fact, then the framing move with a number, then the failure mode.

| Principle | Perceptual fact | Concrete framing move (with threshold) | Failure mode |
|---|---|---|---|
| **Proximity** | Elements closer together group before elements that merely look alike | Gap **inside** a group <= 0.5x the element's own width; gap **between** groups >= 2.0x. A 4:1 inner-to-outer gap ratio is where grouping becomes unambiguous | 1.2:1 ratio reads as one sloppy row instead of two groups; classic in 6-SKU range shots |
| **Similarity** | Like form/colour/size band together across distance | For a range shot hold **one** variable constant (silhouette) and vary exactly **one** (cap colour). Keep all product heights within 3% and all label baselines within 1% of frame height | Vary two attributes and the range reads as unrelated SKUs, not a family |
| **Closure** | The system completes an interrupted contour | You may cut a recognisable silhouette by up to **~30% of its area** at a frame edge and it still reads whole, provided the cut does not remove a defining feature (a bottle's cap, a face's second eye). Beyond ~40% it reads as a fragment | Cutting 25% off a round jar is fine; cutting 25% that includes the pump head is not |
| **Continuity (good continuation)** | The eye prefers the smoothest path | Build one continuous path: countertop edge -> forearm -> bottle -> headline baseline. Keep direction changes along that path under **45 deg**; a change over ~90 deg terminates the path | Two competing paths crossing at 60-90 deg produce a fixation stall at the crossing |
| **Common fate** | Elements moving the same way group, overriding proximity and similarity | Motion only: give the hero and the CTA **the same** motion vector (both drift +4% frame width over 12 frames). Anything moving differently visually secedes | Product pushes in while text slides across, so text is read as UI rather than part of the scene |
| **Figure-ground** | One region becomes object, the rest becomes field; ambiguity is expensive | Require **>= 1.5 stops** of luminance separation between subject edge and the background immediately behind it (>= 2.5 stops for a dark product on dark ground), or **>= 20%** difference in blur radius | Black bottle on black seamless with 0.5 stop separation: the silhouette dissolves at thumbnail size |
| **Praegnanz (simplicity)** | The percept resolves to the simplest stable interpretation available | Cap distinct nameable objects in a commercial frame at **<= 5** (hero + 3 props + ground). Cap distinct hues at **<= 3** plus neutrals | Six props each demanding a reading: viewer resolves the image as "clutter" and disengages |

Additional operational Gestalt moves:

| Move | Number |
|---|---|
| **Common region** — grouped items on a shared tray/plinth/mat | Tray extends 8-12% of frame width beyond the outermost item |
| **Symmetry as grouping** — mirrored pairs group faster than asymmetric pairs | Mirror tolerance within 2% of frame width, or the mirror reads as an error |
| **Element connectedness** — a physical connector beats proximity | A shadow bridging two objects groups them even at 3x element-width separation |

---

## 4. Leading lines, implied lines, and gaze vectors

### 4.1 Leading lines — angles that work

**[PHYSICS]** for perspective, **[CRAFT HEURISTIC]** for the ranges.

| Line type | Angle from horizontal | Read | Typical use |
|---|---:|---|---|
| Horizontal | 0-5 deg | Stability, calm, product on a shelf | Luxury, still life, corporate |
| Shallow diagonal | 10-20 deg | Gentle movement without drama | Lifestyle, food-on-table |
| Working diagonal | 25-40 deg | Energy, direction, scroll-stop | Fashion, sport, beverage pour |
| Steep diagonal | 45-60 deg | Instability, urgency | Action, disruption campaigns |
| Vertical | 85-90 deg | Height, authority, aspiration | Architecture, bottle-as-monument |
| Converging pair | 15-35 deg each, meeting inside the frame | Forces the eye to the vanishing point | Put the hero at or within 5% of frame width of the convergence point |

Rules with numbers:

- A leading line should **enter the frame from an edge** and terminate on the hero. A line that starts and ends inside the frame does not lead; it decorates.
- Keep the line's terminus **>= 8% of frame width inside** the opposite edge, or the eye exits the frame.
- A line entering from the **bottom-left corner** rising to the right is the common commercial choice in left-to-right reading markets. **[CRAFT HEURISTIC]** — there is no strong published effect size for it, so do not claim one.
- **Horizon placement**: landscape-preference research has specifically tested horizon position against golden-section division (source: https://www.sciencedirect.com/science/article/abs/pii/S0272494414000085, retrieved 2026-07-29, abstract-level only). Treat "horizon on a third" as convention, not a validated preference.

### 4.2 Implied lines

- **Alignment of discrete points**: 3+ objects whose centres fall within 2% of a straight path read as a line. Use it to link hero -> prop -> logo.
- **Shadow edge** — often stronger than the object, because a cast shadow can span 40-60% of the frame's longest dimension.
- **Limb direction** — a forearm at 30 deg is a leading line with a x1.8 hand bonus at its end.
- **Gaze** — see 4.3.

### 4.3 Gaze vectors: what is actually measured

**The lab effect is real but small. [PEER-REVIEWED]** McKay et al., "Visual attentional orienting by eye gaze: a meta-analytic review of the gaze-cueing effect", *Psychological Bulletin* 147(12), 2021, 1269-1289: **112 independent samples, 3,693 healthy adults, pooled g = 0.23** (source: https://www.researchgate.net/publication/358701907_Visual_Attentional_Orienting_by_Eye_Gaze_A_Meta-Analytic_Review_of_the_Gaze-Cueing_Effect, retrieved 2026-07-29).

Mechanism and timing: Friesen & Kingstone, "The eyes have it! Reflexive orienting is triggered by nonpredictive gaze", *Psychonomic Bulletin & Review* 5, 1998 — a schematic face looking left/right/straight followed by a target letter; response times were reliably faster when gaze pointed **toward** the target even though subjects were told gaze did not predict location (source: https://link.springer.com/article/10.3758/BF03208827, retrieved 2026-07-29). The effect appears at cue-target intervals as short as **100 ms** and can persist to **600-700 ms** (source: https://pmc.ncbi.nlm.nih.gov/articles/PMC5775299/, retrieved 2026-07-29).

**The advertising version is weaker than its reputation. [THIRD-PARTY CACHE]** The famous "baby looking at the copy" heat-map is James Breeze's 2009 commercial study, **106 subjects**, published on a consultancy blog, not peer-reviewed (source: https://www.neurosciencemarketing.com/blog/articles/baby-heat-maps.htm, retrieved 2026-07-29). Commentary notes contradictory findings and that in that ad the baby's face dominated a sparse white composition, so the cue faced almost no visual competition (source: https://www.brainsight.app/post/gaze-cueing-two-stage-attention-flow-design, retrieved 2026-07-29).

**Honest operational statement.** Direct a model's gaze at the product or the copy field because (a) it costs nothing, (b) the lab effect is robust in direction if small in size, and (c) it removes the direct-address competition that otherwise traps the viewer on the face. Do **not** claim a percentage lift.

| Gaze configuration | Effect | When to use | Number |
|---|---|---|---|
| **Direct to lens** | Maximum face weight; viewer stays on the face | Brand-trust portrait, testimonial, founder | Iris centred within 2 deg of lens axis; catchlight at 10-11 o'clock |
| **To the product** | Transfers weight to the product; adds ~x1.6 to product score | Any product-led asset with a person | Head turn 15-30 deg, eye rotation a further 5-15 deg toward the product |
| **To the copy field** | Pulls reading into the text block | Text-heavy ad, promo | Gaze line must terminate inside the copy field's bounding box, not past it |
| **Out of frame** | Creates off-screen space and tension; leaks attention | Editorial, aspirational | Requires **>= 20% of frame width** of look-room on the gaze side, else it reads claustrophobic |
| **Averted, downcast** | Introspection, calm, product-as-ritual | Skincare, wellness, luxury | Eyelid 40-60% closed; head pitched 5-15 deg down |

**Nose room / look room / lead room. [CRAFT HEURISTIC]**

| Framing | Space on the gaze side | Space behind the head |
|---|---:|---:|
| CU, head turned 30 deg | 20-30% frame width | 10-15% |
| MS, walking into frame | 25-35% (lead room ahead of motion) | 10-20% |
| Full shot, static, 3/4 turn | 15-25% | 15-25% |
| Direct address, centred | equal | equal |

Headroom: **CU 2-6%** of frame height above the head; **MS 5-10%**; **FS 8-12%**. Over 15% headroom in a CU reads as a framing error. Negative headroom (skull cropped) is a deliberate editorial move — valid in beauty and fashion, invalid in ecommerce.

---

## 5. Framing devices and vignetting

| Device | Construction | Frame budget | Reads as |
|---|---|---:|---|
| **Frame within frame** (doorway, window, arch) | Surround occupies the outer band | 15-35% of frame area; over 45% the device becomes the subject | Depth, voyeurism, found moment |
| **Foreground occluder, defocused** | Object at 0.3-0.8x the subject distance, thrown out of focus | 10-25% of frame area, ideally one edge plus one corner | Presence, candour, "I am in the room" |
| **Natural vignette from a modifier** | Light falloff, not post | 0.5-1.5 stops darker at corners | Believable |
| **Post vignette** | Radial darkening | Keep **under 1.0 stop (about -0.7 EV)** at the corner. Over ~1.5 stops it looks artificial and can band on OLED phone screens | Cheap when overdone |
| **Negative-fill vignette** | Black flags at frame edges | 1-2 stops on the outer 10% | Premium, controlled |
| **Colour vignette** (cool corners, warm centre) | 100-300K difference | Hue shift under 5 deg | Filmic |
| **Hard geometric frame** (product inside a printed shape) | Graphic overlay | Inner window 55-70% of frame | Editorial, campaign system |

**Vignette warning for social:** a post vignette applied to a 1:1 master becomes off-centre after any 9:16 or 16:9 crop, producing lopsided darkening. Apply vignettes **per-derivative**, after recomposition. **[CRAFT HEURISTIC]**, but treat as a hard production rule.

---

## 6. Negative space as a message

### 6.1 Subject-occupancy bands

Definition used here: **subject occupancy** = bounding-box area of all hero elements (product + person + logo + copy) as a percentage of frame area. Negative space = 100 minus that. **[CRAFT HEURISTIC]** bands, calibrated against the platform specs in 6.2.

| Subject occupancy | Negative space | Reads as | Category fit | Risk |
|---:|---:|---|---|---|
| 85-95% | 5-15% | Urgency, value, volume, everything-must-go | Discount retail, grocery flyer, FMCG promo | Reads cheap; fails at thumbnail because nothing dominates |
| 70-85% | 15-30% | Confident, catalogue-clear, informative | Ecommerce hero, marketplace listing | Little room for copy |
| 55-70% | 30-45% | Balanced editorial | Lifestyle feed, DTC brand | Safe but unremarkable |
| 35-55% | 45-65% | Considered, designed, premium | Fashion, beauty, tech, hospitality | Needs a strong single subject or it reads as empty |
| 15-35% | 65-85% | Luxury, calm, reverence, ritual | Fine jewellery, fragrance, watches, spirits | Fails on small screens; do not use below 4:5 at feed size |
| < 15% | > 85% | Art / conceptual | Brand film stills, gallery | Unreadable as commerce |

Cross-check against the two hard platform numbers below: they force occupancy far above the "premium" band, which is why marketplace listings and brand campaigns must be **different assets**, not crops of each other.

### 6.2 Platform-mandated occupancy (the constraint that overrides taste)

| Platform | Requirement | Implied negative space | Status |
|---|---|---:|---|
| Amazon main image | Product must fill **>= 85%** of the frame; pure white background RGB 255,255,255; centred, not cropped at edges; no text/logo/watermark/border; >= 1,000 px on the long side for zoom, 2,000+ recommended | <= 15% | **[THIRD-PARTY CACHE]** (sources: https://www.sellerlabs.com/blog/amazon-product-image-requirements-2026/ and https://www.squareshot.com/post/amazon-product-image-requirements-guide, retrieved 2026-07-29). Primary doc is Seller Central Help; the hub page did not render for machine fetch. **Re-verify.** |
| Google Merchant Center | Product should occupy **no less than 75% and no more than 90%** of the full image | 10-25% | **[THIRD-PARTY CACHE]** (source: https://www.datafeedwatch.com/blog/google-shopping-images, retrieved 2026-07-29). Primary: https://support.google.com/merchants/answer/6324350 — **re-verify.** The *upper* bound exists because Google may crop. |

The 75-90% window is the most useful number in this section: it is **two-sided**, and the upper bound is the one people break.

### 6.3 What the evidence actually says about visual complexity

**[PEER-REVIEWED] — the strongest finding in this dossier.** Pieters, Wedel & Batra, "The Stopping Power of Advertising: Measures and Effects of Visual Complexity", *Journal of Marketing* 74(5), 2010, 48-60. **249 advertisements tested with eye-tracking.** They separate two kinds of complexity:

- **Feature complexity** — dense perceptual features (many edges, textures, colours, small elements). **Hurts** attention to the brand and attitude toward the ad.
- **Design complexity** — an elaborate but *ordered* creative design. **Helps** attention to the pictorial and to the ad as a whole.

(source: https://journals.sagepub.com/doi/abs/10.1509/jmkg.74.5.048, retrieved 2026-07-29)

**Translation into a rule:** the goal is not emptiness. It is **low feature complexity with high design complexity**. Concretely:

- Reduce the count of independent small details, textures and hues (feature).
- Keep or increase deliberate structure: layering, unusual viewpoint, considered asymmetry, a designed relationship between elements (design).
- An image can be 65% occupied and still read simple if the occupancy is one large ordered mass. An image can be 30% occupied and still read complex if that 30% is confetti.

### 6.4 Negative space and perceived luxury

Directional support exists: consumers exposed to ads featuring white space perceived the product as higher quality and more prestigious; brands with simpler packaging (more white space around the logo) are perceived as more expensive and more successful; and preferred white-space ratio **varies by tier** — lower ratio preferred for low-end products (potato chips), higher ratio for high-end (fine chocolate). A 2025 *Journal of Sensory Studies* paper examines white space, typeface and visual texture together (sources: https://onlinelibrary.wiley.com/doi/10.1111/joss.70026 — paywalled, HTTP 402 at retrieval; and https://www.joebm.com/vol11/730-CE4004.pdf — PDF not text-extractable; both retrieved 2026-07-29). **[PEER-REVIEWED but abstract-level only.]**

**[UNVERIFIED - needs check]** I could not extract the **exact white-space percentages tested** in either paper. To close the gap, obtain the full text of *Journal of Sensory Studies* 2025 (DOI 10.1111/joss.70026) and the JOEBM white-space-ratio paper, and record their experimental levels. Until then the bands in 6.1 remain craft heuristics, not measured thresholds.

### 6.5 Two negative-space myths to refuse

| Claim | Status |
|---|---|
| "White space between paragraphs and in margins increases comprehension by almost 20% (Lin, 2004)" | **[MYTH] — falsified at the source.** The citation propagated from Galitz (2007) p.158. The actual Lin (2004) paper, *Computers in Human Behavior* 20(4), is about older adults' retention in hypertext perusal (24 participants aged 62-80, Chinese-language UIs). Lin himself is quoted: "The said publication of mine has nothing to do with whitespace, not to mention the so-called increase of comprehension by 20%." (source: https://www.linkedin.com/pulse/lin-2004-did-discover-margins-white-space-increase-20-carl-myhill, retrieved 2026-07-29). Never cite this number. |
| "Whitespace increases perceived value by up to 300%" | **[MYTH] / [UNVERIFIED]** — surfaced in trade summaries during retrieval on 2026-07-29 with no citation attached. No primary study located. Treat as fabricated until a source is produced. |

---

## 7. Balance and tension

### 7.1 The moment-arm model

**[CRAFT HEURISTIC]**, but it makes balance computable. Treat the frame as a beam pivoting on the vertical centre line. For each element compute:

```
moment = visual_weight * horizontal_distance_from_centre (as a fraction of half-frame-width)
```

Sum moments left and right. **Balance index = |sum_left - sum_right| / (sum_left + sum_right)**.

| Balance index | Read | Use |
|---:|---|---|
| 0.00-0.10 | Symmetric / static | Luxury, authority, catalogue, radial subjects |
| 0.10-0.30 | Asymmetric but resolved | Default for editorial and lifestyle |
| 0.30-0.55 | Tense, dynamic, deliberate | Fashion, sport, campaign key art |
| 0.55-0.80 | Unstable; needs a counterweight or it reads as an error | Only with a strong second element (copy block, shadow mass) |
| > 0.80 | Broken; reads as a bad crop | Avoid unless the emptiness is literally the message |

Worked example: hero product weight 40 at 0.25 right of centre (moment 10.0); copy block weight 20 at 0.60 left (moment 12.0). Index = |12 - 10| / 22 = **0.09** — symmetric-feeling despite a visibly off-centre product. This is why a text block is the cheapest counterweight in commercial layout.

### 7.2 Three balance types

| Type | Construction | Numbers | Communicates | Risk |
|---|---|---|---|---|
| **Symmetric (bilateral)** | Mirror across the vertical axis | Mirror error <= 2% of frame width; horizon/plinth within 1% of true level | Authority, heritage, trust, ritual, premium | Static; low scroll-stop in feed |
| **Asymmetric** | Unequal masses balanced by weight x distance | Target balance index 0.10-0.30; hero occupies the smaller area but the higher weight | Modern, editorial, human | Easy to get to 0.6 by accident |
| **Radial** | Elements distributed around a centre | Use 3, 5, 6 or 8 spokes; keep angular spacing within 2 deg of equal; centre element 1.4-2.0x the diameter of spokes | Abundance, community, ingredient story, top-down food | Reads as a clock face if spokes are identical; break one spoke |

### 7.3 Tension as a deliberate tool

Tension = an unresolved expectation the viewer wants to close. Concrete generators, with the number that makes each read as intentional rather than accidental:

| Tension device | Threshold for "intentional" |
|---|---|
| Subject pressed to one edge | Margin **<= 5%** of frame width on that side, and **>= 35%** on the other. Between 10% and 25% it reads as a mistake |
| Deliberate horizon tilt | **>= 4 deg** (below 3 deg reads as sloppy levelling); dutch angle for video 8-15 deg |
| Cropped through the subject | Cut **>= 15%** of the subject away; a 3% nick reads as an error |
| Empty foreground | Foreground occupies **>= 40%** of frame height with nothing in it |
| Colour clash | Complementary pair at **>= 60% saturation** both, occupying **>= 15%** each |
| Scale disruption | Size mismatch of **>= 3x** against the expected relationship |
| Off-balance stance | Weight-bearing leg produces hip displacement **>= 8%** of body width from the centre of support |

**Rule:** one tension device per frame. Two competing tensions read as incompetence, not intent.

---

## 8. Depth cues ranked by strength

### 8.1 The nine sources and where each dominates

Cutting & Vishton, "Perceiving layout and knowing distances: the integration, relative potency, and contextual use of different information about depth", in Epstein & Rogers (eds), *Perception of Space and Motion*, Academic Press, 1995, 69-117, assess nine sources — **occlusion, relative size, relative density, height in the visual field, aerial perspective, motion perspective, binocular disparity, convergence, accommodation** — and their relative utility at different distances, postulating three zones: **personal space, action space, vista space** (sources: https://www.sciencedirect.com/science/article/pii/B9780122405303500055 and https://ntrs.nasa.gov/api/citations/20180007277/downloads/20180007277.pdf, retrieved 2026-07-29). **[PEER-REVIEWED]**

**[UNVERIFIED - needs check]** The commonly quoted zone boundaries (personal <= ~2 m, action ~2-30 m, vista > ~30 m) did not appear verbatim in retrievable text. To confirm, obtain the chapter itself; the Cornell mirror (http://cutting.psych.cornell.edu/space_layout.htm) refused connection and the ResearchGate/Academia copies were not text-extractable on 2026-07-29.

### 8.2 Working rank for a single 2D commercial image

For a flat image, binocular disparity, convergence and accommodation are unavailable — which is why the pictorial cues below carry the entire burden. Ranked by how reliably each one creates depth in a still frame:

| Rank | Cue | Why it is strong | How to specify it, concretely |
|---:|---|---|---|
| 1 | **Occlusion (interposition)** | Ordinal and near-absolute: if A covers B, A is nearer, at every distance. The one cue that never inverts | Overlap the hero over the ground plane and let one prop overlap the hero by **5-15%** of the hero's width |
| 2 | **Relative size / familiar size** | Strong whenever object identity is known | Include one known-size referent (hand, coin, spoon, phone). For product-in-hand, the hand should be **1.5-3x** the product's largest dimension |
| 3 | **Height in the visual field** | Objects further away sit higher relative to the ground line | Place the far object's contact point **12-30%** of frame height above the near object's contact point |
| 4 | **Texture / density gradient** | Compression of surface detail with distance | Detail spacing should compress by roughly **50% per doubling of distance**; a table top should show visible grain in front and none at the back |
| 5 | **Linear perspective / convergence** | Parallel edges converge | 24-35mm behaviour exaggerates convergence; 85-135mm flattens it. Choose deliberately |
| 6 | **DOF separation (blur gradient)** | Not a natural depth cue in the Cutting sense but a very strong pictorial one | See 8.3 |
| 7 | **Aerial perspective (atmospheric haze)** | Contrast and saturation fall with distance; blue shift | Reduce background contrast by **30-60%** and saturation by **20-40%**; add a **+200 to +600K** cool shift. Only credible at **> 30 m** — haze on a tabletop is a tell |
| 8 | **Cast shadow / contact shadow** | Anchors an object to a plane; its absence makes objects float | Contact shadow **0.5-2 stops** darker than the ground at the contact point, softening over **10-30%** of the object's height |
| 9 | **Shading / form shadow** | Reveals volume, not distance | Terminator (light-to-shadow transition) should span **15-35%** of the form's width for a soft look, **<5%** for hard |
| 10 | **Relative brightness** | Weakest; easily inverted by lighting choices | Do not rely on it alone |

**Motion perspective (parallax)** ranks very high but only exists in video: a dolly of **1-3% of subject distance per second** produces readable parallax without visible camera drama.

### 8.3 DOF separation numbers

| Goal | Subject-to-background distance | Aperture intent | Background result |
|---|---|---|---|
| Product label fully legible, background suggested | 1.5-3 m | f/8-f/11 | Recognisable but not sharp |
| Portrait separation, environment readable | 3-5 m | f/4-f/5.6 | Soft shapes, readable place |
| Strong isolation, background as colour field | > 6 m | f/1.8-f/2.8 | Unrecognisable wash |
| Flat studio, no depth wanted | Subject 1-2 m from seamless | f/8-f/11 | Even field |

Additional numeric levers, independent of aperture: put the background **1.5-2.5 stops** darker than the subject for separation without blur; **2.5-3.5 stops** for a "floating in black" look. **[PHYSICS]** for the falloff, **[CRAFT HEURISTIC]** for the stop targets.

---

## 9. Eye-path models: evidence audit

This is where most composition advice is folklore. Verdicts below.

### 9.1 The audit table

| Model | The claim | Evidence | Verdict |
|---|---|---|---|
| **F-pattern** | Users scan two horizontal sweeps then down the left edge | NN/g 2006 original eyetracking; 232 users, thousands of pages; re-confirmed 11 years later (sources: https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/ and https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/, retrieved 2026-07-29) | **Real but conditional.** NN/g explicitly names three designer misconceptions: that it is universal, that it is inevitable, and that it applies to navigation. It emerges only when text is unformatted, the user is optimising for efficiency, and motivation is low. It does **not** occur when users are highly motivated |
| **Layer-cake, spotted, commitment patterns** | Three other scanning patterns exist | Kara Pernice, NN/g, 25 Aug 2019: **layer-cake** (headings only, produced by clear heading/body contrast), **spotted** (keyword hunting, produced by styled links and bullets), **commitment** (near-full reading, produced by high motivation) (source: https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/, retrieved 2026-07-29) | **Real, and the useful part.** Design chooses the pattern. Headings and bolding *convert* an F into a layer-cake |
| **Z-pattern** | Eye traces top-left -> top-right -> diagonal -> bottom-right | No primary eyetracking study located. Trade sources describe it as occurring on "simpler layouts" and note that scan patterns are outcomes of design and purpose, not laws (source: https://medium.com/@ux.spotlight/rethinking-eye-tracking-patterns-with-purpose-e9621cc3b834, retrieved 2026-07-29) | **[MYTH] as stated.** It is a *layout recipe* (put logo TL, nav TR, hero image, CTA BR) that works because it distributes weight sensibly — not a measured gaze path. Use it as a template, never cite it as research |
| **Gutenberg diagram** | Page splits into primary optical area (TL), strong fallow (TR), weak fallow (BL), terminal anchor (BR); reading gravity flows TL->BR | Originates in newspaper layout practice. Design sources concede there is "little empirical evidence" for the specific claims about fallow areas and terminal anchor (source: https://vanseodesign.com/web-design/3-design-layouts/, retrieved 2026-07-29) | **[MYTH] as science, useful as a template.** Applies only to *evenly distributed, homogeneous* content — which almost no commercial image is. Any visual hierarchy overrides it |
| **Centre-stage effect** | The middle option in an array gets more attention and more choices | Atalay, Bodur & Rasolofoarison, "Shining in the Center: Central Gaze Cascade Effect on Product Choice", *Journal of Consumer Research* 39(4), 2012, 848-866. Eye-tracking found brands in the **horizontal centre** received more visual attention and were more likely to be chosen, via an **initial central fixation bias** plus a **central gaze cascade** — progressively increasing attention on the central option right before the decision (source: https://academic.oup.com/jcr/article-abstract/39/4/848/1798298, retrieved 2026-07-29) | **[PEER-REVIEWED] and actionable.** For any array of 3+ options, put the SKU you want chosen in the horizontal centre |
| **Restaurant menu "golden triangle" / sweet spot (upper-right)** | Eyes go to centre, then upper-right, then upper-left | Sybil Yang, "Eye movements on restaurant menus: a revisitation on gaze motion and consumer scanpaths", *International Journal of Hospitality Management*, 2012. Subjects wore an infrared eye tracker reading mock menus. Result: people read menus **sequentially, left to right and down the page, like a book**. No sweet spot found; she did identify a "sour spot" (restaurant general-information sections and the salad list). Yang described the sweet-spot theory as "like a bad rumour that just kept perpetuating" (sources: https://www.researchgate.net/publication/257118038_Eye_movements_on_restaurant_menus_A_revisitation_on_gaze_motion_and_consumer_scanpaths and https://www.restaurant-hospitality.com/how/menu-engineering-gets-makeover, retrieved 2026-07-29) | **[MYTH] — actively falsified.** Do not design menus, price lists, or feature grids around a "golden triangle" |

### 9.2 What to use instead

For any composition containing text or an array:

1. **Hierarchy beats pattern.** Give one element >= 1.3x the visual weight of the next (section 2.2). The eye goes there first regardless of position.
2. **Then** use position as a tie-breaker: horizontal centre for choice (9.1 centre-stage), upper band for identity, lower band for action.
3. For text-bearing images, convert F-scanning into layer-cake scanning: **one** headline at >= 2.2x body size, in a field with < 10% local feature complexity.
4. Never promise a gaze path. Promise a **weight order**.

---

## 10. Aspect ratio semantics

### 10.1 The table

| Ratio | Decimal | Native home | Communicates | Composition consequence |
|---|---:|---|---|---|
| **1:1** | 1.000 | Legacy IG feed, ad units, carousels, marketplace tiles | Neutral, product-first, systematic, "catalogue" | No dominant axis, so symmetry or centring wins; thirds offsets are only 16.7% of width from centre and read weakly |
| **4:5** | 0.800 | Meta feed (Meta's recommended feed ratio), IG portrait post | Human, editorial, mobile-optimal; maximum feed real-estate without being a Story | Vertical subject fits; leaves a genuine top or bottom copy band of 20-25% height |
| **3:4** | 0.750 | IG **profile grid thumbnail** since Jan 2025; native 3:4 photo support added May 2025 | Same as 4:5 but taller | See 10.3 — this creates a double-crop trap |
| **2:3** | 0.667 | Pinterest standard (commonly 1000x1500) | Discovery, editorial, "pin" | Tall enough for a text lockup plus a full product |
| **3:2** | 1.500 | 35mm still, print, web hero | Classic photographic, documentary, "shot by a photographer" | Dynamic-symmetry eye at 30.8% of width |
| **16:9** | 1.778 | YouTube, web hero, in-stream, TV, presentations | Cinematic-lite, informational, landscape context, "broadcast" | Dynamic-symmetry eye at 24% of width; large horizontal negative space is easy and cheap |
| **9:16** | 0.5625 | Reels, TikTok, Shorts, Stories | Immersive, personal, first-person, immediate | Subject must be vertical or the frame is 60% background; UI chrome consumes the top and bottom (section 14) |
| **21:9** | 2.333 | Ultrawide display, some AI model presets | Panoramic, luxury, architectural, "epic" | Extreme; hero must be small or the frame must be layered |
| **2.39:1** | 2.387 | Cinema scope | Prestige, film, drama, spectacle | The widest ratio that still reads as "a film". Dynamic-symmetry eye at 14.9% of width — subjects go near the edges |
| **1.85:1** | 1.850 | Cinema flat | Contemporary film, understated prestige | A wider 16:9; behaves the same |
| **5:4** | 1.250 | Large-format still, some print | Formal, still-life, "plate" | Nearly square; symmetry-friendly |

**2.39:1 is a real standard, not a stylistic guess.** SMPTE standardised the scope ratio at 2.39:1; the DCI 2K Scope container is **2048 x 858** px, and 2048/858 = 2.3869, which rounds to 2.39 not 2.35 (sources: https://postfactory.co.uk/knowledge/what-is-scope-aspect-ratio/ and https://dcpmaker.com/docs/scope-2-391/, retrieved 2026-07-29). **[INDUSTRY-PRIMARY]** via secondary restatement — the DCI spec itself is the authority. Writing "2.35:1" in a spec is a 1970s-and-earlier ratio and marks the author as imprecise.

### 10.2 What each ratio costs you

| Ratio | Negative-space cost | Text-field capacity | Thumbnail survival |
|---|---|---|---|
| 1:1 | Low | Medium (one band, 20-30% height) | Excellent |
| 4:5 | Low | Good (band up to 25% height) | Excellent |
| 9:16 | **High** — a vertical subject leaves 2 large side voids | Poor after UI chrome: ~42% of frame usable (section 14) | Good if the subject is large |
| 16:9 | Medium | Excellent (side third = 33% width) | Poor — becomes a letterbox strip in feed |
| 2.39:1 | **Very high** | Excellent horizontally, none vertically | Very poor; do not use as a primary social asset |

### 10.3 The Instagram 4:5 / 3:4 double-crop trap

**[THIRD-PARTY CACHE — re-verify]** In January 2025 Instagram changed profile-grid thumbnails from 1:1 to **3:4** (1080 x 1440), and added native 3:4 photo support in May 2025, while **4:5** remains the widely recommended feed ratio (sources: https://www.kapwing.com/resources/instagrams-new-grid-layout-size-and-dimensions-2025/ and https://socialbee.com/blog/instagram-aspect-ratio-and-image-size/, retrieved 2026-07-29). Consequence: a 4:5 upload displays uncropped **in feed** but is cropped to 3:4 **on the profile grid**.

Arithmetic: a 1080 x 1350 (4:5) image centre-cropped to 3:4 keeps width 1080 and needs height 1440 — it cannot, so the crop instead reduces **width** to 1350 x 0.75 = 1012.5 px, cutting **67.5 px total (6.25% of width, 3.1% per side)**. Small, but it is exactly where an edge-placed logo lives.

**Operational rule:** keep logos and edge-critical elements **>= 7% of width** inside the left and right edges of any 4:5 asset intended for a profile grid, or author 3:4 and accept top/bottom letterbox in feed. Verify against Instagram help before relying on the ratio numbers.

---

## 11. Shot size ladder mapped to narrative job

**[CRAFT HEURISTIC]** — these are production conventions. The head-height fractions make them machine-checkable.

| Shot | Abbrev | Head height as % of frame height | Cut line on the body | Narrative job | Commercial use |
|---|---|---:|---|---|---|
| Extreme close-up | ECU | > 100 (skull and chin cropped) | eyes-to-lips only | Intensity, texture, detail as evidence | Skin texture, lipstick payoff, fabric weave, ingredient |
| Big close-up | BCU | 75-100 | top of head cropped, chin included | Emotion, intimacy, "look at this face" | Beauty, testimonial reaction |
| Close-up | CU | 50-75 | mid-chest or collarbone | Identity, trust, sincerity | Founder portrait, product-in-hand at face height |
| Medium close-up | MCU | 30-45 | mid-chest / armpit | Conversation, explanation | Talking head, tutorial, UGC review |
| Medium shot | MS | 18-25 | waist | Action with hands, social read | Product demo, application, unboxing |
| Medium long / cowboy | MLS | 12-18 | mid-thigh | Full gesture, wardrobe, stance | Fashion, sportswear |
| Full shot | FS | 8-12 | complete body, feet included | Whole person, silhouette, outfit | Apparel, footwear, dance |
| Wide shot | WS | 4-8 | body plus environment | Person in place | Lifestyle, hospitality, retail interior |
| Extreme wide / establishing | EWS | < 4 | environment dominant | Scale, place, aspiration | Travel, real estate, architecture |
| Insert / detail | — | n/a | product only | Proof of a specific feature | Zip, seam, pump mechanism, label |
| Macro | — | n/a | 1:1 magnification or greater | Material truth | Powder grain, serum viscosity, coffee crema |

**Product occupancy equivalent** for product-only shots:

| Shot | Product occupancy of frame area | Job |
|---|---:|---|
| Hero packshot | 60-85% | Recognition, listing compliance |
| Three-quarter pedestal | 45-65% | Depth + label |
| Environmental product | 15-35% | Context and use |
| Product-in-scene (lifestyle) | 6-18% | Belonging, aspiration |
| Detail insert | 70-95% (of the *feature*, not the product) | Proof |
| Macro | Feature fills frame | Material |

**Ladder rule:** a campaign needs **at least three rungs apart** between any two adjacent assets in a sequence, or the set reads as repetition. ECU -> MCU -> WS is a set; MCU -> MS is the same shot twice.

---

## 12. Camera height and angle as a power/relationship signal

### 12.1 Height (where the lens sits) and angle (where it points)

**[CRAFT HEURISTIC]** for degrees; **[PEER-REVIEWED]** for the advertising effect in 12.2.

| Camera height | Angle to subject | Degrees below/above subject centre | Signals | Commercial use |
|---|---|---:|---|---|
| Ground / floor level | Looking up steeply | 30-60 deg up | Monumentality, dominance, heroism | Sneakers, spirits bottle as monument, architecture |
| Low, knee-to-hip | Mild up | 10-25 deg up | Aspiration, confidence, "bigger than you" | Sportswear, automotive, energy drinks |
| Chest height | Level | 0-5 deg | Neutral, honest, observational | Lifestyle, documentary, UGC |
| Eye level | Level | 0 deg | Equality, trust, direct relationship | Testimonial, founder, beauty, ecommerce apparel |
| Slightly high | Mild down | 10-20 deg down | Approachability, invitation, "come in" | Food on a table, skincare flat-ish, UGC selfie |
| High | Down | 25-45 deg down | Overview, vulnerability, smallness, control | Tablescape, retail floor plan, "system" shots |
| Overhead / top-down | Straight down | 85-90 deg | Diagram, order, knolling, recipe | Flat-lay, food, tool kits, ingredient breakdown |
| Dutch (roll axis) | any | 8-15 deg roll | Unease, energy, disruption | Music, youth, disruptive positioning |

**Product-specific heights:**

| Product type | Lens height | Reason |
|---|---|---|
| Bottle, jar, tube with a front label | **Label centre height**, 0-5 deg down | Keeps the label rectangle undistorted |
| Bowl of food (soup, noodles) | 25-40 deg down | Shows the contents *and* the vessel; 90 deg loses depth, 0 deg loses contents |
| Plated flat dish (pizza, tart) | 75-90 deg down | Full geometry |
| Layered drink | **Rim height, 0-8 deg down** | Shows strata without a foreshortened ellipse |
| Footwear | 15-25 deg down, 3/4 turn | Shows profile, toe box and outsole edge |
| Watch face | 60-80 deg down | Dial legible, case profile visible |
| Electronics with a screen | 10-20 deg down | Screen readable, no keystone on the bezel |

### 12.2 The advertising evidence, which is conditional

**[PEER-REVIEWED]** Meyers-Levy & Peracchio, "Getting an Angle in Advertising: The Effect of Camera Angle on Product Evaluations", *Journal of Marketing Research* 29(4), 1992, 454-461. Findings:

- Camera-angle effects emerge when viewers' **motivation to process is low or moderate**, not high.
- Under **low** motivation: evaluations were **most favourable looking up** at the product, least favourable looking **down**, moderate at eye level.
- Under **moderate** motivation: **eye-level** shots produced the most favourable evaluations.

(source: https://psycnet.apa.org/record/1993-15751-001 and https://www.semanticscholar.org/paper/Getting-an-angle-in-advertising:-The-effect-of-on-Meyers-Levy-Peracchio/180eec9a3878c953626510e62b94b00b853673e8, retrieved 2026-07-29)

**Operational translation, which is genuinely counter-intuitive:**

| Placement | Likely processing motivation | Angle to choose |
|---|---|---|
| Feed / scroll-past display, cold audience | Low | **Low angle, 10-25 deg up** |
| Considered browsing, category page, retargeting | Moderate | **Eye level** |
| PDP, spec comparison, high-intent | High | Angle is not the lever — go for information clarity |

Do not over-claim: this is a single 1992 study on print-style stimuli. Cite it as directional, not as a guaranteed lift.

---

## 13. Crop grammar

### 13.1 Human body — where you may cut and where you must not

**[CRAFT HEURISTIC]**, but near-universal in professional practice. The underlying reason is perceptual: cutting **at** a joint reads as amputation because the joint is the contour's inflection point and closure cannot complete it; cutting **through a limb segment** lets closure extend the limb out of frame.

| Landmark | Verdict | Reason |
|---|---|---|
| Mid-forehead / above the hairline | **Allowed** (editorial, beauty) | Reads as a deliberate tight crop |
| Eyebrows | **Never** | Truncates the face's key expressive band |
| Chin | **Never** (unless full ECU on lips only) | Makes the head look severed |
| Neck | **Never** | The single worst cut in portraiture |
| Mid-chest / between armpit and nipple line | **Allowed** | Standard MCU |
| Shoulder joint | **Never** | Amputates the arm |
| Mid-upper-arm | **Allowed** | Arm continues out of frame |
| Elbow | **Never** | Amputation read |
| Mid-forearm | **Allowed** | Fine |
| Wrist | **Never** | Removes the hand, which the viewer looks for |
| Fingers | **Avoid**; if unavoidable cut all fingers at the same depth | Ragged finger cuts read as injury |
| Waist / natural waist | **Allowed** | Standard MS |
| Hip joint | **Never** | Amputation read |
| Mid-thigh | **Allowed** | Standard cowboy shot |
| Knee | **Never** | Amputation read |
| Mid-calf | **Allowed** | Fine |
| Ankle | **Never** | Removes the foot; also destabilises the figure |
| Feet | Include fully or crop **above mid-calf** | Half-feet read as an error |
| Through the torso vertically (one side of the body) | **Allowed** if >= 15% of body width is cut | See 7.3 — under 15% reads as sloppiness |

**Additional numeric rules:**
- If a **full shot** includes feet, leave **>= 3% of frame height** of floor below the soles, or the figure appears to be standing on the frame edge.
- **Never** crop so that the subject's contact with the ground is invisible in a full or wide shot; the figure will float.
- For groups, cut all subjects at the **same anatomical landmark**, not the same pixel row.

### 13.2 Product — where you may cut

| Product element | Verdict | Threshold |
|---|---|---|
| Bottom edge / base | **Never crop** in an ecommerce hero | Amazon-style rules require no edge cropping; a floating base destroys weight |
| Contact shadow | **Never crop away** | Product will float |
| Cap, pump, closure, spout | **Never crop** | It is the recognition feature |
| Logo / brand mark | **Never crop** | Non-negotiable |
| Primary label rectangle | **Never crop** in a hero; may crop up to 20% in a detail insert | Legibility |
| Body of the product (side) | **Allowed** in editorial crop-intrusion compositions: cut 20-35% | Below 15% reads as an error; above 45% loses recognition |
| Bottom of a tall product entering from the frame edge | **Allowed** if 55-80% of the silhouette remains | Closure limit from section 3 |
| Secondary/bundled items | **Allowed** freely | Not the hero |
| Ingredient or texture in a macro | **Allowed** freely | The crop *is* the shot |

**Edge margin standard for commerce:** keep the product's bounding box **>= 5% of the shorter frame dimension** away from every edge in a hero packshot, which also satisfies the "not cropped at edges" requirement in 6.2.

### 13.3 Food and beverage crops

| Element | Rule |
|---|---|
| Bowl rim | Cut it, or show it whole — never leave a 2-5% sliver of rim |
| Steam / condensation | Must have room above; leave **>= 10% frame height** above a hot dish |
| Garnish | May exit the frame; the hero protein/noodle may not |
| Pour / splash | Leave **>= 15%** of frame in the direction of motion (lead room) |
| Glass base | Never crop; the base carries the contact shadow |

---

## 14. Safe zones and text-field composition for vertical social formats

### 14.1 Standing warning

**Every number in this section is [THIRD-PARTY CACHE].** Meta's and TikTok's official help pages did not render machine-readable content on 2026-07-29 (Meta Business Help returned title-only Vietnamese shells; the TikTok safe-zone help article returned "no longer exists or failed to load"). The figures below are the consensus across multiple independent trade sources, and they **conflict with each other**, which is itself the finding. Treat them as a starting cache with a **30-day staleness window**, and re-verify at:

- Meta: https://www.facebook.com/business/help/980593475366490 ("About text overlays and the Safe Zone for ads in Stories and Reels") and https://www.facebook.com/business/help/103816146375741 (aspect ratios by placement)
- TikTok: https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads?lang=en plus TikTok's downloadable safe-zone template ZIPs in Ads Manager
- YouTube/Google: https://support.google.com/google-ads/answer/2375464

Meta also ships a **Safe Zone Guardrail** overlay inside Ads Manager during ad setup — use the live tool in preference to any cached number (source: https://www.1clickreport.com/blog/meta-ads-creative-safe-zones-2026-guide, retrieved 2026-07-29).

### 14.2 Cached figures, per platform (1080 x 1920 canvas)

| Platform | Top | Bottom | Left | Right | Usable height | Source (retrieved 2026-07-29) |
|---|---:|---:|---:|---:|---:|---|
| **Meta (IG/FB Reels + Stories, unified)** | 14% (269 px) | 35% (672 px) | 6% (65 px) | 6% (65 px) | **51%** | https://behaviour.digital/post/meta-reels-safe-zone-14-top-35-bottom-6-sides-the-2026-official-guide |
| Meta, alternate pixel statement | 250 px | 672 px | — | — | ~51% (band 250-1248 px) | https://www.1clickreport.com/blog/meta-ads-creative-safe-zones-2026-guide |
| **TikTok organic** | 108 px (5.6%) | 320 px (16.7%) | 60 px (5.6%) | 120 px (11.1%) | **77.7%** | https://www.ignitesocialmedia.com/content-creation/what-are-the-safe-zones-for-tiktoks-and-instagram-reels/ |
| TikTok paid (adds CTA button) | 108 px | ~370 px | 60 px | 120 px | ~75% | https://zeely.ai/blog/tiktok-safe-zones/ |
| TikTok, conservative alternate | 120 px | 120 px | — | — | ~87.5% | https://predis.ai/resources/tiktok-safe-zone-guide/ |
| **YouTube Shorts** | 180 px (9.4%) | 390 px (20.3%) | 60 px (5.6%) | 60 px (5.6%) | **70.3%** | https://www.pod2reels.com/blog/youtube-shorts-safe-zone-guide |
| YouTube Shorts, alternate | 180 px | 350 px | 48 px | 192 px | ~72% | https://kreatli.com/guides/youtube-shorts-safe-zone |

Note the disagreement: TikTok bottom margin is quoted as anywhere from 120 px to 370 px. TikTok's own guidance reportedly says the safe zone **varies with video dimension, caption length and ad format**, so there is no single pixel-perfect answer — which is why the template ZIPs exist.

### 14.3 The universal vertical safe rectangle (derived)

Take the **most restrictive** margin from each side across all three platforms above (Meta top/bottom, TikTok right, Meta sides):

| Edge | Governing platform | Margin (px) | Margin (%) |
|---|---|---:|---:|
| Top | Meta 14% | 269 | 14.0 |
| Bottom | Meta 35% | 672 | 35.0 |
| Left | Meta 6% | 65 | 6.0 |
| Right | TikTok | 120 | 11.1 |

**Result — the "all-platform vertical core":**

```
x: 65 px  ->  960 px      (895 px wide  = 82.9% of width)
y: 269 px -> 1248 px      (979 px tall  = 51.0% of height)
Area = 82.9% x 51.0% = 42.3% of the 9:16 frame
Centre of the core = (512.5, 758.5) px = 47.5% width, 39.5% height
```

**The single most useful number here: the optical centre of a vertical social frame is at ~39.5% of frame height, not 50%.** Place eyes, hero product and headline centroid around **38-42% of frame height**, and about **1-3% left of horizontal centre**. Anything composed on the geometric centre sits too low and drifts into the caption/CTA zone.

Cross-check: TikTok's own band centre computes to (108 + 1492/2)/1920 = **44.5%** height and (60+450)/1080 = **47.2%** width. YouTube Shorts computes to (180+675)/1920 = **44.5%**. All three converge in the **39-45%** range. Use **40%** as the default target.

### 14.4 Text-field composition rules

| Rule | Number |
|---|---|
| Text block position in 9:16 | Inside y = 269-1248 px; prefer y = 400-1100 px |
| Max text coverage of the frame | **<= 20%** of frame area. Meta historically penalised heavy text overlay; even without a hard rule, feature complexity (6.3) argues for restraint |
| Minimum body size for mobile legibility | **>= 2.5% of frame height** (48 px on 1920) for body; **>= 5%** (96 px) for a headline |
| Contrast for overlaid text | **>= 4.5:1** luminance contrast against the local background patch, measured on the darkest/lightest 10% of the patch, not the average |
| Text field local complexity | Background under text should have **< 10%** local edge density; if not, add a scrim at 30-50% opacity |
| Subtitles / burned-in captions | Keep inside the same core; never below y = 1248 px |
| Logo | Top-left or top-right inside x/y core, occupying 3-6% of frame area |
| CTA | Do **not** burn in a CTA in the bottom 35% — the platform draws its own there |

---

## 15. Composing one master that survives recomposition

### 15.1 The arithmetic of nested crops

For centred crops from a master of width W and height H:

```
To take ratio r = width/height at full height:   crop_width  = H * r
To take ratio r at full width:                   crop_height = W / r
```

**Case A — 1:1 master, side S, deriving {1:1, 4:5, 3:4, 9:16, 16:9}:**

| Derivative | Crop from S x S | Uses |
|---|---|---|
| 1:1 | S x S | 100% |
| 4:5 (0.800) | 0.800S x S | 80.0% of width |
| 3:4 (0.750) | 0.750S x S | 75.0% of width |
| 9:16 (0.5625) | 0.5625S x S | **56.25% of width** |
| 16:9 (1.778) | S x 0.5625S | **56.25% of height** |

Intersection of all five = the central square of side **56.25%** -> area **0.5625 x 0.5625 = 31.6% of the master**.

**Case B — 4:5 master (W = 0.8H), deriving {4:5, 3:4, 1:1, 9:16} (no 16:9):**

| Derivative | Crop | Uses |
|---|---|---|
| 4:5 | full | 100% |
| 3:4 | 0.75H wide = 93.75% W | 93.8% of width |
| 1:1 | W x W, height = 0.8H | 80.0% of height |
| 9:16 | 0.5625H wide = 70.3% W | 70.3% of width |

Intersection = 70.3% W x 80.0% H -> area **56.3% of the master**.

**Conclusion with a number: dropping 16:9 from the derivative set nearly doubles the usable core, from 31.6% to 56.3%.** One master cannot serve both the 9:16 and 16:9 families without wasting two-thirds of the frame. **Author two masters** — a vertical-family master (9:16 / 4:5 / 3:4 / 1:1) and a horizontal-family master (16:9 / 3:2 / 2.39:1) — and treat 1:1 as the hinge that both can produce.

### 15.2 The three-ring construction

Compose in concentric rings and assign content by ring.

| Ring | Extent (of a 1:1 master) | Content allowed |
|---|---|---|
| **Ring 1 — mission-critical core** | Central 56.25% x 56.25% (31.6% of area) | Face/eyes, hero product with its logo and closure, headline centroid. Nothing here may be lost |
| **Ring 2 — supporting band** | 56.25% to 80% of each dimension | Secondary props, hands, gradient falloff, brand colour field. May be cut in the tightest crop |
| **Ring 3 — sacrificial margin** | Outer 20% | Environment, extra negative space, atmosphere. Expected to be cut in most derivatives |

Then apply the vertical UI offset from 14.3: **in the 9:16 derivative, shift Ring 1 upward so its centre lands at 40% of the derivative's height**, not 50%. Concretely, when generating or shooting the master, place the hero centroid at **~44-46% of master height** so that after the vertical crop and UI-aware reposition it lands at 40%.

### 15.3 Recomposition checklist (per derivative)

1. Recompose; do not blind-centre-crop.
2. Verify Ring 1 is intact and inside the platform core (14.3).
3. Re-check the balance index (7.1) for the new frame — a 0.15 index in 1:1 can become 0.55 in 9:16.
4. Re-apply the vignette (section 5 warning).
5. Re-check subject occupancy against the band table (6.1) — cropping *raises* occupancy, so a 45% "premium" 1:1 becomes ~80% "catalogue" in 9:16.
6. Re-check text size as a percentage of the *new* frame height.
7. Confirm no forbidden crop line from section 13 has been introduced by the new frame edges.

---

## 16. DECISION TABLE: communication job -> composition spec

Read left to right. Every row is a complete, unambiguous composition brief. NS = negative space budget.

| # | Communication job | Shot size | Camera height / angle | Placement + grid | NS budget | Ratio | Key constraint |
|---:|---|---|---|---|---:|---|---|
| 1 | "This exact product, buy it" (marketplace listing) | Hero packshot, product 75-85% | Label height, 0-5 deg down | Optical centre, no grid | 15-25% | 1:1 | Product 75-90% (6.2); >=5% edge margin; white ground |
| 2 | "This brand is expensive" | Product 20-30%, MLS if a person | Eye level, 0 deg | Centred or dynamic-symmetry eye | 65-80% | 4:5 or 3:2 | One tension device max; feature complexity minimal |
| 3 | "Stop scrolling" (cold feed) | MCU or bold detail | **Low, 10-25 deg up** (12.2 low-motivation) | Subject centroid at 40% frame height | 30-45% | 9:16 | Hero >= 1.3x next element; read at 120 px tall |
| 4 | "Trust this person" | CU, head 50-75% | Eye level, 0 deg | Centred, eyes on upper third | 25-40% | 4:5 | Gaze direct to lens within 2 deg; headroom 2-6% |
| 5 | "Here is how it works" | MS, hands visible | Chest height, 0-10 deg down | Hands at frame centre, product in the near third | 20-35% | 1:1 or 4:5 | Hands unoccluded; contact shadow present |
| 6 | "This one, not the others" (range/choice) | Full range, WS | Eye level | **Hero SKU in the horizontal centre** (9.1 centre-stage) | 25-40% | 16:9 or 1:1 | Equal heights within 3%; hero 1.15-1.3x scale |
| 7 | "This belongs in your life" | WS, person 25-40% of height | Chest height, 0-5 deg | Off-axis, thirds, subject moving into space | 45-60% | 4:5 | Lead room 25-35%; environment legible |
| 8 | "Look at the material" | Macro / detail insert | Perpendicular to the surface | Feature fills frame | 5-15% | 1:1 | One sharp plane named; raking light |
| 9 | "This is a system / process" | Top-down knolling | 88-90 deg down | Radial or grid, equal spacing +/-2 deg | 30-45% | 1:1 or 16:9 | <= 5 nameable object groups |
| 10 | "This is appetising" | MCU of the dish | **25-40 deg down** for bowls, 75-90 deg for flat plates | Bowl centre at 45% frame height | 20-35% | 4:5 | >=10% headroom for steam; garnish may exit |
| 11 | "This is powerful / heroic" | FS or MLS | Ground level, 30-60 deg up | Subject on the dynamic-symmetry eye | 40-60% | 9:16 or 2.39:1 | Converging verticals kept, not corrected |
| 12 | "This is calm / restorative" | MS, subject small | Eye level, 0 deg | Subject at 38-42% height, large empty upper field | 60-75% | 4:5 | Balance index <= 0.15; hues <= 2 plus neutrals |
| 13 | "Urgent, limited, cheap" | Product 85%+ plus burst copy | Eye level | Full-bleed, centre | 5-15% | 1:1 | Accept low prestige; keep one dominant element |
| 14 | "Prestige film moment" | WS or EWS | Eye level or slightly low | Subject at 15% of width (scope eye) | 70-85% | 2.39:1 | Do not use as the primary social asset |
| 15 | "Explain a spec to a high-intent buyer" | Detail insert plus callouts | Perpendicular | Product left 40%, callout field right 60% | 30-40% | 16:9 | Angle is not the lever (12.2 high motivation) |
| 16 | "Creator recommends this" | MCU, phone-distance | Slightly high, 10-20 deg down | Face at 35-42% height, product entering lower third | 25-35% | 9:16 | Framing imperfect on purpose; product inside the 14.3 core |

---

## 17. Worked examples

Format: scenario, then the exact composition spec that would be written.

### 17.1 Vietnamese bun bo hue, 9:16 Reels hero for a cold audience

**Scenario:** Independent restaurant, first paid Reel, needs scroll-stop plus appetite appeal, one bowl, no model.

**Spec:**
```
Ratio 9:16, 1080x1920. Shot: MCU of a single bowl, bowl occupying 46% of frame area.
Camera height: rim height plus 32 deg down (shows broth surface, noodle strata and the
vessel's silhouette). Lens behaviour 85-100mm to avoid rim keystone.
Placement: bowl centroid at 40% of frame height, 48% of frame width (per the derived
all-platform core, 14.3). Rim top edge at y=560 px. Steam volume occupies y=270-560 px.
Negative space budget: 54%, distributed as a dark wooden table surface below and a
low-entropy warm shadow field above.
Depth cues, ranked implementation: chopsticks resting across the rim occlude the broth
(occlusion, rank 1); a hand-sized spoon at the lower right gives familiar size (rank 2);
a second out-of-focus bowl 40 cm behind sits 18% of frame height higher (height in field,
rank 3); table grain compresses toward the back (texture gradient, rank 4).
DOF: f/4-5.6 intent; sharp plane = the near noodle strata and the beef slice edge.
Balance: bowl right of centre by 6% (moment 0.28), counterweighted by a 3-line copy block
on the left occupying 11% of area. Balance index target 0.12.
Text field: x 65-960 px, y 400-1000 px. Headline 96 px, body 48 px, 4.5:1 contrast on a
40% scrim. No burned-in CTA below y=1248 px.
Tension: exactly one - the chopstick diagonal at 28 deg.
Crop locks: bowl base and its contact shadow never cropped; steam has >=10% headroom;
garnish may exit the frame.
```
**Why:** row 3 + row 10 of the decision table, resolved. Low-motivation audience -> upward-tilted framing is not available for a top-down food subject, so scroll-stop is bought with occupancy and one strong diagonal instead.

### 17.2 200 ml serum, Amazon main image

**Scenario:** DTC skincare going onto a marketplace. Compliance is the whole job.

**Spec:**
```
Ratio 1:1, 2000x2000 px (above the 1,000 px zoom threshold, at the recommended 2,000+).
Product occupancy 86% of the shorter dimension's square - inside the >=85% requirement and
below the point where any auto-crop clips it. Edge margin 5.5% on all four sides.
Camera: label centre height, 2 deg down, 100mm behaviour, f/8-f/11 intent with the full
label plane, cap threads and pump collar all sharp.
Placement: optical centre - the label's visual centroid on the frame centre, which for a
tapered bottle sits ~2% above the geometric centre of the silhouette.
Background: pure white RGB 255,255,255. Contact shadow retained, 1 stop under the ground
at the contact point, softening over 18% of bottle height.
Negative space: 14%. No props, no text, no logo overlay, no border, no watermark.
Crop locks: base, cap, pump, logo and primary label all fully inside frame.
```
**Why:** row 1. Note the direct conflict with the premium band in 6.1 (which would want 65-80% negative space). That conflict is why the brand campaign asset must be a **separate shot**, not a crop of this one.

### 17.3 One master, five ratios: apparel lookbook

**Scenario:** Fashion label needs 9:16, 4:5, 1:1, 16:9 and 2.39:1 from one shoot day.

**Spec:**
```
Author TWO masters, per 15.1.
Vertical master: 4:5 at 4000x5000. Derivatives 4:5, 3:4, 1:1, 9:16. Usable core after
intersection = 70.3% width x 80.0% height = 56.3% of the master.
  Ring 1 (mission-critical): face, hands, garment neckline and hem, at 4000*0.703 = 2812 px
  wide x 5000*0.80 = 4000 px tall, centred, then shifted so Ring 1's centre sits at 45% of
  master height (so the 9:16 derivative lands it at 40%).
  Ring 2: arms, secondary garment detail, prop.
  Ring 3: outer 20% - studio floor, cyc falloff.
Horizontal master: 16:9 at 5120x2880. Derivatives 16:9, 3:2, 2.39:1.
  2.39:1 from 16:9 full width: crop height = 5120/2.387 = 2145 px, i.e. 74.5% of height.
  Subject edge on the 24% vertical for 16:9; re-place to the 14.9% vertical for the 2.39:1
  derivative (dynamic-symmetry eye, 1.4).
Shot ladder across the set: ECU (fabric weave) -> MCU (face + neckline) -> MLS (full look)
-> WS (person in place). Three rungs apart minimum.
Vignettes applied per derivative, never on the master.
```

### 17.4 Model holding a product where the face is winning

**Scenario:** First render came back with the face dominating; the client cannot see the product.

**Diagnosis using 2.2:** face 14% area x 5.0 x 1.3 = 91.0; product 6% x 3.5 x 2.5 = 52.5; ratio 1.73:1 against the product.

**Spec revision:**
```
1. Rotate gaze: head turn 22 deg toward the product, eye rotation a further 10 deg, gaze
   line terminating on the product's label, not past it. Product gains x1.6 -> 84.0.
2. Reduce face area from 14% to 9% by recomposing to a wider MS (head 20% of frame height).
   Face -> 9 x 5.0 x 1.3 = 58.5.
3. Add 1.5 stops of separation: product lit 1.5 stops above the face plane.
4. Product moves to the horizontal centre (centre-stage, 9.1); face moves to 62% of width.
New ratio 84.0 : 58.5 = 1.44:1 in the product's favour. Target >=1.3:1 met.
Verify: eyes still inside the 14.3 core; no crop at shoulder, elbow, wrist or knee.
```

### 17.5 Range shot of six SKUs where the client wants one to sell

**Scenario:** Six flavour variants; the margin-leading SKU must be chosen.

**Spec:**
```
Ratio 16:9, 3840x2160. Shot: WS, all six SKUs, combined occupancy 38% of frame area.
Camera: label height, 0 deg, 120mm behaviour to minimise perspective size differences
across the row (a 35mm lens would make the outer SKUs read as smaller).
Arrangement: single row of six. Hero SKU at the exact horizontal centre - with six items
the centre falls between positions 3 and 4, so use FIVE in the back row and place the hero
alone in front, on the centre line, 1.2x apparent scale via 12 cm closer placement.
This satisfies the central fixation bias and central gaze cascade (9.1).
Gestalt: proximity gap inside the group 0.45x element width; the hero separated from the
row by 2.2x element width (4.9:1 ratio) so it reads as figure against a group of ground.
Similarity: all six heights within 3%, all label baselines within 1% of frame height,
only the cap colour varies.
Depth: hero occludes the row behind it by 8% of its own width (occlusion, rank 1).
Negative space 62%, with a copy field on the left third (33% of width).
Balance: hero centred (moment 0), row symmetric, copy block left -> index 0.22.
```

### 17.6 Luxury watch, 2.39:1 brand key art

**Scenario:** Heritage watch brand, cinema-ratio key art for a launch page hero.

**Spec:**
```
Ratio 2.39:1, 2048x858 (DCI 2K Scope container - the standardised dimension, 10.1).
Shot: detail insert. Watch occupies 11% of frame area.
Camera: 68 deg down (dial fully legible, case profile visible), 100mm macro behaviour,
f/8 intent, sharp plane = dial and bezel edge; crown deliberately at the edge of focus.
Placement: watch centroid on the dynamic-symmetry eye at x = 14.9% of width (305 px) and
y = 85.1% inverted to 38% of height (326 px) - i.e. upper-left region, per 1.4.
Negative space 89%: a graduated stone surface falling 2.5 stops from the watch to the
right-hand edge. Aerial perspective NOT used (the scene is under 1 m; haze would be a tell).
Depth cues used: occlusion (a linen edge overlaps the strap by 9%), texture gradient on the
stone, contact shadow 1.5 stops under the ground.
Balance: watch far left (weight 30 at 0.70 -> moment 21.0) counterweighted by a wordmark at
0.55 right (weight 14 -> moment 7.7). Index = 0.46 - deliberately tense, inside the
"tense, dynamic" band for campaign key art (7.1).
Tension: exactly one - extreme edge placement with 4% left margin and 58% right margin
(satisfies the <=5% / >=35% intentionality threshold, 7.3).
Do not derive social assets from this frame. Author a 4:5 sibling.
```

### 17.7 Rebuilding a "golden triangle" menu layout

**Scenario:** Client asks for a price list designed on the restaurant menu "golden triangle".

**Response spec:**
```
Refuse the premise, cite the evidence (9.1, Yang 2012: menu reading is sequential,
left-to-right and down, like a book; no sweet spot was found).
Design instead for sequential reading plus weight hierarchy:
- Single-column, sequential order. Put the margin-leading item FIRST in its section, not
  in a corner.
- Give the target item >=1.3x the visual weight of its neighbours: a 1.25x type size,
  a 12% tint panel, and one 40x40 px illustration. Nothing else in the section gets art.
- Avoid the identified "sour spot": do not place anything commercially important adjacent
  to general restaurant-information blocks or the salad list.
- For a 3-option price array (not a list), the centre-stage effect DOES apply: put the
  target tier in the horizontal centre (9.1, Atalay et al. 2012).
```

---

## 18. AI-generation translation

The output of this skill is usually a prompt, not a camera. This section converts each principle into prompt language, and states what current models can and cannot honour.

### 18.1 Verified model capabilities that constrain composition

| Capability | Verified fact | Source (retrieved 2026-07-29) |
|---|---|---|
| **OpenAI image models** | Models: `gpt-image-2`, `gpt-image-1.5`, `gpt-image-1`, `gpt-image-1-mini`. Documented sizes include 1024x1024, 1536x1024, 1024x1536, 2048x2048, 2048x1152, 3840x2160, 2160x3840, plus `auto`. Constraints: max edge <= 3840 px; both edges multiples of 16; **aspect ratio cannot exceed 3:1**; total pixels 655,360 to 8,294,400 | https://developers.openai.com/api/docs/guides/image-generation |
| **Gemini 2.5 Flash Image ("Nano Banana")** | 10 aspect ratios: 21:9, 16:9, 4:3, 3:2, 1:1, 9:16, 3:4, 2:3, 5:4, 4:5. Generally available; $0.039 per image; post dated 2 Oct 2025 | https://developers.googleblog.com/en/gemini-2-5-flash-image-now-ready-for-production-with-new-aspect-ratios/ |
| **Imagen (Gemini API)** | Supported ratios 1:1, 3:4, 4:3, 9:16, 16:9. Imagen models are deprecated with shutdown stated for 17 Aug 2026; Google directs users to Nano Banana | https://ai.google.dev/gemini-api/docs/imagen |
| **FLUX** | Black Forest Labs recommends a `Subject + Action + Style + Context` structure and states that word order matters | https://docs.bfl.ai/guides/prompting_guide_flux2 |

**Composition consequences of those facts:**

- **2.39:1 is not a native preset anywhere above.** 2.387 exceeds Gemini's widest ratio (21:9 = 2.333). Generate at 21:9 and crop the height by 2.2%, or generate 16:9 and crop to 2.39:1 losing 25.5% of height (compose knowing that loss).
- **4:5 exists on Gemini/Nano Banana but not in OpenAI's documented size list.** For OpenAI, generate 1024x1536 (2:3) and crop to 4:5, losing 20% of height — so place Ring 1 accordingly.
- **3:4 is native on Gemini, not documented for OpenAI.** Relevant to the Instagram grid issue in 10.3.
- The 3:1 ratio ceiling on OpenAI means panoramic work above 3:1 must be stitched or outpainted.
- **Never state a ratio the target model does not support** and expect it. Generate at the nearest supported ratio, then recompose per section 15.

### 18.2 Principle -> prompt phrasing bank

Models respond to described *geometry and relationships*, not to grid names. "Rule of thirds" is a weak token; "subject positioned one third from the left edge, facing right into open space" is strong.

| Principle | Weak prompt token (avoid) | Strong prompt phrasing |
|---|---|---|
| Thirds placement | "rule of thirds" | "subject placed one third in from the left edge, the right two thirds an empty wall" |
| Dynamic symmetry in 16:9 | "dynamic symmetry" | "subject's leading edge about one quarter in from the left edge; wide empty right side" |
| Centring | "centered composition" | "single subject dead centre, perfectly symmetrical, equal margins on both sides" |
| Shot size | "close up" | "head and shoulders framing, head filling about two thirds of the frame height, cropped at mid-chest" |
| Camera height | "low angle" | "camera at knee height looking up at about twenty degrees, converging vertical lines kept" |
| Occlusion depth | "depth" | "a defocused linen edge overlaps the near corner of the bottle, partly covering it" |
| Texture gradient | "perspective" | "wood grain sharp and wide in the foreground, compressing to smooth at the back of the table" |
| Aerial perspective | "atmospheric" | "distant hills lower in contrast and slightly blue, near foreground fully saturated" |
| DOF separation | "bokeh" | "focus on the near iris, background six metres away rendered as unrecognisable soft colour" |
| Figure-ground | "good contrast" | "matte black bottle against a mid-grey背 background two stops brighter, clean silhouette" |
| Negative space | "minimalist" | "the product occupies roughly one fifth of the frame, the remaining four fifths an unbroken gradient" |
| Gaze vector | "looking at product" | "her eyes are directed down and to the right, focused on the jar in her hand, not at the camera" |
| Balance / tension | "dynamic" | "subject pressed against the left edge with only a sliver of margin, wide empty space to the right" |
| Leading line | "leading lines" | "the table edge runs from the bottom-left corner up at about thirty degrees, ending at the glass" |
| Copy space | "space for text" | "the upper third is an even, unbroken surface with no detail, reserved for text" |
| Contact shadow | "realistic shadow" | "a soft contact shadow directly beneath the base, darkest at the contact point, fading over a third of the object's height" |
| Crop grammar | "cropped" | "framed so the arms are cut mid-forearm, not at the elbows or wrists" |
| Radial balance | "circular arrangement" | "six identical bowls evenly spaced around a central larger bowl, equal gaps, viewed straight down" |

Fix the one accidental non-ASCII token above: use "mid-grey background".

### 18.3 Prompt ordering for composition

Given that word order matters (BFL guidance, 18.1), put composition **after** subject locks but **before** style:

```
1  SUBJECT + LOCKS            (what must not change)
2  ACTION / GAZE VECTOR       (where attention goes)
3  SHOT SIZE + CROP LINE      (head fills X, cut at mid-forearm)
4  PLACEMENT + NEGATIVE SPACE (one third from left; four fifths empty)
5  CAMERA HEIGHT + ANGLE      (knee height, twenty degrees up)
6  DEPTH CUES                 (occlusion, texture gradient, contact shadow)
7  FOCUS PLANE + SEPARATION   (sharp on X, background N metres back)
8  LIGHT GEOMETRY             (see realistic-studio-imagery.md)
9  RATIO + COPY-SAFE FIELD    (9:16; upper region y 400-1000 kept clean)
10 REJECT LIST                (no cut at elbows/wrists/knees, no floating base)
```

### 18.4 What models reliably fail at, with the mitigation

| Failure | Mitigation |
|---|---|
| Exact percentage placement ("38.2% from left") | State it as a fraction in words plus a relational cue ("about one third in, with the right side empty"). Then **verify and crop in post** — do not trust the generator for placement precision |
| Preserving a text-safe field | Generate at a wider ratio and crop the copy band in; or generate the field as an explicit described surface ("an unbroken concrete wall fills the upper third") |
| Reliable crop lines on bodies | Generate looser than needed and crop to the correct landmark manually |
| Aspect-ratio-exact scope framing | Generate 21:9 or 16:9 and crop; see 18.1 |
| Contact shadows on transparent/glass products | Name the shadow explicitly with its density and falloff; check for floating |
| Six-SKU range with equal heights | Do not generate; composite from individual generations. Multi-object equal-scale arrays are a known weak point |
| Legible small text | Never ask for it. Add type in design software (already the rule in `product-imagery.md`) |
| Consistent composition across a set | Generate a single master, then recompose (section 15), rather than re-prompting for each ratio |

### 18.5 Video-specific translation

| Principle | Prompt phrasing |
|---|---|
| Common fate | "the bottle and the caption drift together to the right at the same slow speed" |
| Motion perspective | "slow lateral dolly left to right, near table edge sweeping past faster than the back wall" |
| Lead room | "she walks in from the left, always kept in the left third with open space ahead of her" |
| Dutch angle | "camera rolled about ten degrees clockwise, held" |
| Safe-zone-aware framing | "her eyes stay in the upper 40 percent of the vertical frame throughout; the bottom third stays empty" |
| Shot ladder in a sequence | "cut from macro texture, to head-and-shoulders, to a wide shot of the room" (three rungs apart) |

---

## 19. Numeric QA gates

Reject the composition if any gate fails.

| # | Gate | Threshold |
|---:|---|---|
| 1 | Dominance | Hero weight >= 1.3x the next strongest element (2.2) |
| 2 | Figure-ground | >= 1.5 stops luminance separation at the subject edge (>= 2.5 for dark-on-dark) |
| 3 | Object count | <= 5 nameable object groups; <= 3 hues plus neutrals |
| 4 | Balance | Balance index inside the band chosen for the job (7.1) |
| 5 | Tension | Exactly 0 or 1 tension devices, each above its intentionality threshold (7.3) |
| 6 | Occupancy | Inside the band for the intent (6.1), and inside any platform requirement (6.2) |
| 7 | Crop grammar | No cut at eyebrows, chin, neck, shoulder, elbow, wrist, hip, knee or ankle (13.1); no cropped product base, cap or logo (13.2) |
| 8 | Grounding | Contact shadow present and explicable; nothing floats |
| 9 | Depth | At least 3 of the top-5 pictorial depth cues implemented (8.2) |
| 10 | Headroom / look room | Inside the ranges in 4.3 |
| 11 | Vertical safe core | All mission-critical content inside x 65-960, y 269-1248 on a 1080x1920 frame (14.3) |
| 12 | Vertical centroid | Hero centroid at 38-42% of frame height in 9:16 |
| 13 | Text | <= 20% frame area; body >= 2.5% frame height; contrast >= 4.5:1; background edge density < 10% |
| 14 | Thumbnail | One message survives at 120 px on the long edge |
| 15 | Recompose | Ring 1 intact in every derivative; gates 1, 4, 6, 7, 13 re-run per derivative |
| 16 | Ratio validity | Requested ratio is natively supported by the target model, or a documented crop path exists (18.1) |
| 17 | Citation hygiene | No claim in the delivered rationale cites the Lin (2004) whitespace figure, the 300% whitespace figure, the menu golden triangle, or a golden-ratio historical claim |

---

## Open questions

1. **Exact white-space percentages that flip a "premium" read.** Blocked by paywall (10.1111/joss.70026, HTTP 402) and a non-extractable PDF (JOEBM). Needs full texts to convert 6.1 from craft heuristic to measured thresholds.
2. **Primary-source platform safe zones.** Meta and TikTok help pages returned no machine-readable body on 2026-07-29. The "14% / 35% / 6%" Meta figure appears only in trade blogs; the TikTok bottom margin ranges from 120 px to 370 px across sources. Needs a human to open the live docs and the TikTok template ZIPs, and to run Meta's in-product Safe Zone Guardrail.
3. **Cutting & Vishton zone boundaries.** The 2 m / 30 m numbers for personal/action/vista space are widely repeated but were not confirmed in retrievable text (Cornell mirror refused connection; repository copies not extractable). Needs the book chapter.
4. **Instagram 3:4 grid behaviour.** The Jan 2025 grid change and May 2025 native 3:4 support come from third-party guides only. Needs verification against Instagram Help, plus a live test upload to measure the actual crop.
5. **Whether the centre-stage effect holds in vertical scroll feeds.** Atalay et al. (2012) tested horizontal shelf-like arrays. No study located for vertical single-item feeds. Would need original testing.
6. **Effect size for reading-direction leading lines.** No published effect size located for the bottom-left-to-upper-right convention. Currently unsupported craft.
7. **Dynamic symmetry vs thirds, head to head.** No study located that tests root-rectangle placement against thirds placement in the same experiment. The 24%-vs-33% claim in 1.4 is geometric reasoning, not measured preference.
8. **SIGGRAPH Asia 2023 "Rule-of-Thirds or Centered?" details.** Full text 403; participant count and stimuli unknown. Needs the ACM PDF to report the strength of the centring preference.
9. **Model-side placement fidelity.** No benchmark located that measures how accurately gpt-image-2 or Nano Banana honour explicit placement instructions. Worth building a small internal eval: 20 prompts specifying a placement fraction, then measure the delivered centroid.

---

## Sources

Deduped. All retrieved 2026-07-29 unless noted.

**Composition rules and their evidence**
- Rule of thirds origin (Smith 1797): https://en.wikipedia.org/wiki/Rule_of_thirds
- Amirshahi, Hayn-Leichsenring, Denzler & Redies, "Evaluating the Rule of Thirds in Photographs and Paintings", *Art & Perception* 2(1-2), 2014, 163-182: https://brill.com/view/journals/artp/2/1-2/article-p163_11.xml (403 on fetch; details via https://www.researchgate.net/publication/259620557_Evaluating_the_Rule_of_Thirds_in_Photographs_and_Paintings)
- Hoh & Zhang, "Rule-of-Thirds or Centered?", SIGGRAPH Asia 2023 Posters: https://dl.acm.org/doi/10.1145/3610542.3626121 (403 on fetch)
- Expertise moderation of thirds sensitivity: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2022.786977/full
- Horizon position / golden section in landscape preference: https://www.sciencedirect.com/science/article/abs/pii/S0272494414000085
- Markowsky, "Misconceptions about the Golden Ratio", *The College Mathematics Journal* 23(1), 1992, 2-19: https://www.tandfonline.com/doi/abs/10.1080/07468342.1992.11973428 and https://www.goldennumber.net/wp-content/uploads/George-Markowsky-Golden-Ratio-Misconceptions-MAA.pdf
- Hambidge dynamic symmetry / root rectangles: https://en.wikipedia.org/wiki/Dynamic_rectangle
- Hambidge, *The Elements of Dynamic Symmetry*: https://books.google.com/books/about/The_Elements_of_Dynamic_Symmetry.html?id=Qy6Y5c6ELlIC

**Perception and attention**
- Wertheimer, "Untersuchungen zur Lehre von der Gestalt II", *Psychologische Forschung* 4, 1923, 301-350 (English translation): https://psychclassics.yorku.ca/Wertheimer/Forms/forms.htm
- Crouzet, Kirchner & Thorpe, "Fast saccades toward faces: face detection in just 100 ms", *Journal of Vision* 10(4), 2010: https://pubmed.ncbi.nlm.nih.gov/20465335/
- Itti, Koch & Niebur, "A Model of Saliency-Based Visual Attention for Rapid Scene Analysis", *IEEE TPAMI* 20(11), 1998, 1254-1259: https://www.cse.psu.edu/~rtc12/CSE597E/papers/Itti_etal98pami.pdf
- Friesen & Kingstone, "The eyes have it! Reflexive orienting is triggered by nonpredictive gaze", *Psychonomic Bulletin & Review* 5, 1998: https://link.springer.com/article/10.3758/BF03208827
- McKay et al., gaze-cueing meta-analysis (112 samples, 3,693 participants, g = 0.23): https://www.researchgate.net/publication/358701907_Visual_Attentional_Orienting_by_Eye_Gaze_A_Meta-Analytic_Review_of_the_Gaze-Cueing_Effect
- Gaze-cueing SOA range (100-700 ms), cross-cultural replication: https://pmc.ncbi.nlm.nih.gov/articles/PMC5775299/
- Cutting & Vishton, "Perceiving layout and knowing distances", in *Perception of Space and Motion*, 1995, 69-117: https://www.sciencedirect.com/science/article/pii/B9780122405303500055 and NASA summary https://ntrs.nasa.gov/api/citations/20180007277/downloads/20180007277.pdf

**Eye-path models**
- NN/g, original F-pattern eyetracking (232 users, 2006): https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/
- NN/g, "F-Shaped Pattern: Misunderstood, But Still Relevant" (2017) — the three designer misconceptions and the conditions that suppress the pattern: https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/
- Pernice (NN/g, 25 Aug 2019), "Text Scanning Patterns" — F, spotted, layer-cake, commitment: https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/
- Gutenberg diagram, admission of thin evidence: https://vanseodesign.com/web-design/3-design-layouts/
- Z/F patterns as design outcomes rather than laws: https://medium.com/@ux.spotlight/rethinking-eye-tracking-patterns-with-purpose-e9621cc3b834
- Atalay, Bodur & Rasolofoarison, "Shining in the Center: Central Gaze Cascade Effect on Product Choice", *JCR* 39(4), 2012, 848-866: https://academic.oup.com/jcr/article-abstract/39/4/848/1798298 and open copy http://eprints.aston.ac.uk/17612/1/Shining_in_the_Center.pdf
- Yang, "Eye movements on restaurant menus: a revisitation on gaze motion and consumer scanpaths", 2012: https://www.researchgate.net/publication/257118038_Eye_movements_on_restaurant_menus_A_revisitation_on_gaze_motion_and_consumer_scanpaths
- Yang quoted on the sweet-spot myth ("a bad rumour that just kept perpetuating"): https://www.restaurant-hospitality.com/how/menu-engineering-gets-makeover

**Complexity, white space, luxury**
- Pieters, Wedel & Batra, "The Stopping Power of Advertising: Measures and Effects of Visual Complexity", *Journal of Marketing* 74(5), 2010, 48-60 (249 ads, eye-tracked): https://journals.sagepub.com/doi/abs/10.1509/jmkg.74.5.048
- Iseki et al., white space / typeface / visual texture and perceived luxury, *Journal of Sensory Studies*, 2025: https://onlinelibrary.wiley.com/doi/10.1111/joss.70026 (paywalled, HTTP 402)
- White-space ratio by product tier (JOEBM): https://www.joebm.com/vol11/730-CE4004.pdf (PDF not text-extractable)
- Myhill, debunking the "Lin (2004) whitespace increases comprehension by 20%" citation, including Lin's own denial: https://www.linkedin.com/pulse/lin-2004-did-discover-margins-white-space-increase-20-carl-myhill

**Camera angle**
- Meyers-Levy & Peracchio, "Getting an Angle in Advertising: The Effect of Camera Angle on Product Evaluations", *JMR* 29(4), 1992, 454-461: https://psycnet.apa.org/record/1993-15751-001 and https://www.semanticscholar.org/paper/Getting-an-angle-in-advertising:-The-effect-of-on-Meyers-Levy-Peracchio/180eec9a3878c953626510e62b94b00b853673e8

**Aspect ratios and platform specs**
- SMPTE 2.39:1 scope, DCI 2K Scope container 2048x858: https://postfactory.co.uk/knowledge/what-is-scope-aspect-ratio/ and https://dcpmaker.com/docs/scope-2-391/
- Netflix DCP specifications: https://partnerhelp.netflixstudios.com/hc/en-us/articles/4417542010387-Digital-Cinema-Package-DCP-Specifications-Requirements
- Instagram 3:4 grid (Jan 2025) and native 3:4 photo support (May 2025): https://www.kapwing.com/resources/instagrams-new-grid-layout-size-and-dimensions-2025/ and https://socialbee.com/blog/instagram-aspect-ratio-and-image-size/
- Meta primary docs to re-verify: https://www.facebook.com/business/help/980593475366490 and https://www.facebook.com/business/help/103816146375741
- Meta Reels safe zone 14/35/6 (third-party): https://behaviour.digital/post/meta-reels-safe-zone-14-top-35-bottom-6-sides-the-2026-official-guide
- Meta safe-zone pixel band 250-1248 px and the in-product Safe Zone Guardrail: https://www.1clickreport.com/blog/meta-ads-creative-safe-zones-2026-guide
- TikTok safe zone 108/320/60/120 px: https://www.ignitesocialmedia.com/content-creation/what-are-the-safe-zones-for-tiktoks-and-instagram-reels/
- TikTok paid safe zone and template ZIPs: https://zeely.ai/blog/tiktok-safe-zones/
- TikTok conservative alternate (120 px top/bottom): https://predis.ai/resources/tiktok-safe-zone-guide/
- TikTok Auction In-Feed primary spec: https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads?lang=en
- YouTube Shorts safe zone 180/390/60: https://www.pod2reels.com/blog/youtube-shorts-safe-zone-guide
- YouTube Shorts alternate margins: https://kreatli.com/guides/youtube-shorts-safe-zone
- Amazon main image >= 85% frame fill, pure white RGB 255,255,255: https://www.sellerlabs.com/blog/amazon-product-image-requirements-2026/ and https://www.squareshot.com/post/amazon-product-image-requirements-guide
- Google Merchant Center 75-90% product fill: https://www.datafeedwatch.com/blog/google-shopping-images (primary to re-verify: https://support.google.com/merchants/answer/6324350)

**AI image generation capabilities**
- OpenAI image generation guide — models, sizes, 3:1 ratio ceiling, multiple-of-16 rule: https://developers.openai.com/api/docs/guides/image-generation
- Gemini 2.5 Flash Image, 10 aspect ratios, GA, $0.039/image, 2 Oct 2025: https://developers.googleblog.com/en/gemini-2-5-flash-image-now-ready-for-production-with-new-aspect-ratios/
- Imagen ratios and 17 Aug 2026 shutdown: https://ai.google.dev/gemini-api/docs/imagen
- Black Forest Labs FLUX.2 prompting guide — Subject + Action + Style + Context, word order matters: https://docs.bfl.ai/guides/prompting_guide_flux2
