# Colour Science and Harmony

## Scope

How to make colour decisions for marketing imagery, brand systems and layout with the arithmetic
shown rather than asserted. Covers the physics and perception of colour, the colour spaces worth
knowing and the exact circumstances in which each one matters, why HSL misleads and OkLCh does not,
the real WCAG 2 contrast maths plus the APCA critique of it, what the colour-harmony literature
actually supports versus what design blogs assert, colour and appetite, warm/cool and depth,
skin-tone reproduction and memory colour, numerically-built brand ramps, colour-vision deficiency,
colour constancy and white balance, gamut mapping and print failure, and a complete decision
procedure that turns one brand hex into a defensible palette.

Every ramp, contrast value, chroma limit, ΔE and colour-blindness simulation in this file was
computed, not estimated. The code path is stated at each step so a reader can reproduce it.
Retrieval date for all external facts: **2026-07-29**.

**Claim markers used throughout:** `[verified]` page fetched and read · `[search-level]` search
summary only, re-check before client use · `[illustrative]` invented number for followable
arithmetic, never publish · `[UNVERIFIED - ...]` named gap.

---

## 1. What colour physically is, and what it is not

### 1.1 Spectral truth vs three numbers

A surface has a **spectral reflectance curve** — a reflectance value at every wavelength across
roughly 380–780 nm. An illuminant has a **spectral power distribution** (SPD) over the same range.
What reaches the eye is the product of the two, wavelength by wavelength. That product is a
continuous function: effectively infinite-dimensional.

The retina throws almost all of it away. Three cone classes (L ≈ 566 nm peak, M ≈ 541 nm, S ≈ 441 nm
in commonly cited estimates) each integrate the incoming spectrum against their own sensitivity
curve, producing exactly **three numbers**. Everything downstream — every colour space, every hex
value, every ICC profile — is a re-parameterisation of those three numbers.

The derivation of the standard three numbers (CIE XYZ tristimulus) is a set of three integrals:

```
X = k ∫ S(λ) · R(λ) · x̄(λ) dλ
Y = k ∫ S(λ) · R(λ) · ȳ(λ) dλ
Z = k ∫ S(λ) · R(λ) · z̄(λ) dλ

S(λ) = illuminant SPD
R(λ) = surface spectral reflectance
x̄ ȳ z̄ = CIE 1931 2° colour-matching functions
k     = normalising constant, usually chosen so a perfect diffuser gives Y = 100
```

Three integrals collapsing an infinite-dimensional input into three scalars. **That compression is
the single most consequential fact in applied colour**, because it is many-to-one.

### 1.2 Metamerism: the direct consequence

**Metamerism** is the phenomenon that two stimuli with *different* spectral compositions produce
*identical* tristimulus values, and therefore look identical to a standard observer
(source: https://en.wikipedia.org/wiki/Metamerism_(color), retrieved 2026-07-29) [search-level].
Two objects with different reflectance curves that happen to intersect at three or more points are
likely to be metameric; two objects with *identical* reflectance curves match under every illuminant
(source: https://www.sciencedirect.com/topics/engineering/metamerism, retrieved 2026-07-29)
[search-level].

The forms that bite in marketing production:

| Type | Mechanism | Where it costs you money |
|---|---|---|
| **Illuminant metamerism** | Two samples match under illuminant A, diverge under illuminant B | Packaging approved in the studio under D50 viewing booth; splits on the shelf under 3000 K retail LED. Fabric swatch matches a printed swatch in the office, mismatches in daylight. |
| **Observer metamerism** | Two observers with different cone sensitivities disagree about a match | Client's marketing director insists two proofs differ; the printer sees them as identical. Both may be telling the truth. |
| **Geometric metamerism** | Match holds at one illumination/viewing geometry, fails at another | Metallic and pearlescent inks; anodised aluminium product shots; satin plastics. |
| **Device metamerism** | Same tristimulus reached by different primaries | A colour matched between an OLED phone and a CMYK sheet is a *metameric* match, not a spectral one. Change the room light and the match dies. |

**Operational rules that follow.**

1. Never approve a colour match under a single light source. Approve under at least two: a
   standardised booth illuminant (D50 for graphic arts, D65 for many product sectors) and a mock-up
   of the real environment (retail LED, phone screen, office fluorescent).
2. When a client's brand colour exists as *both* a printed spot ink and a screen hex, those are two
   separate specifications with two separate tolerances. Treat any claim that they are "the same
   colour" as false. They are a metameric pair at best.
3. If a match must survive arbitrary lighting, you need a **spectral** match — same colourants, same
   substrate — not a colorimetric one. That is a procurement decision, not a design decision.
4. Textiles, coated metal and food are the three categories where illuminant metamerism most often
   destroys a launch. Budget a physical light-box check for each.

### 1.3 Where colour is not in the signal at all

Three appearance phenomena that no hex value encodes, and that will contradict your numbers:

- **Simultaneous contrast.** A patch's apparent lightness and hue shift with its surround. A mid-grey
  logo reads dark on white and light on black at the same hex value. This is why brand guidelines
  that specify a single logo colour without specifying background families are incomplete.
- **Colour constancy.** The visual system discounts the illuminant, so a white shirt looks white in
  tungsten and in daylight even though the light reaching the eye differs enormously in chromaticity.
  The `#theDress` stimulus became famous precisely because its illumination cues are unusually
  ambiguous, so different observers unconsciously correct for different illuminants and end up with
  different percepts; observers' inferred illumination correlates negatively with their dress-colour
  matches — yellower inferred light gives a bluer dress match
  (source: https://jov.arvojournals.org/article.aspx?articleid=2648029, retrieved 2026-07-29)
  [search-level].
- **Helmholtz–Kohlrausch effect.** At equal luminance, more saturated colours look *brighter*. More
  saturated colours therefore need *less* luminance than neutrals to appear equally light, and the
  enhancement is strongest for saturated short (blue) and long (red) wavelengths
  (source: https://en.wikipedia.org/wiki/Helmholtz%E2%80%93Kohlrausch_effect, retrieved 2026-07-29)
  [search-level]. Consequence: a saturated brand red at OkLab L = 0.577 will *look* lighter than a
  grey at the same L. Do not be surprised when a contrast calculator and your eye disagree on a
  highly chromatic colour — the calculator is using luminance, your eye is not.

---

## 2. Colour spaces: which one, and exactly when

### 2.1 The map

| Space | Type | Coordinates | The one thing it is for | The failure mode |
|---|---|---|---|---|
| **CIE XYZ** | Device-independent, linear | X, Y, Z | Hub for all conversions; Y is luminance | Not perceptually uniform in any direction; unusable for design decisions |
| **CIE xyY** | Chromaticity + luminance | x, y, Y | Drawing gamut triangles, stating primaries | xy distances badly misrepresent perceived difference (green over-represented) |
| **sRGB** | Device, encoded | R, G, B 0–255 | Web, social, anything with unknown viewing conditions | Small gamut; **not linear** — arithmetic on 0–255 values is wrong |
| **Display P3** | Device, encoded | R, G, B | Apple hardware, modern phones/monitors, HDR-adjacent delivery | Colours outside sRGB will clip on legacy targets. Needs explicit tagging |
| **Adobe RGB (1998)** | Device, encoded | R, G, B | Photo retouch destined for CMYK; covers more cyan-green | Untagged Adobe RGB on the web renders desaturated — a classic production error |
| **CMYK (a given profile)** | Device, subtractive | C, M, Y, K | Print, and only print | Not one space. `FOGRA51` ≠ `GRACoL` ≠ newsprint. Meaningless without a named profile |
| **CIELAB (L\*a\*b\*)** | Perceptual-ish, device-independent | L\*, a\*, b\* | Print tolerancing, ΔE, spectrophotometer output | Hue non-uniformity, notoriously in blues; L\* ignores H–K effect |
| **CIELCh** | Cylindrical CIELAB | L\*, C\*, h° | Talking to printers about hue/chroma | Inherits CIELAB's blue hue problem |
| **OkLab** | Perceptual, device-independent | L, a, b | Interpolation, gradients, blends | Not a colour *appearance* model — no surround, no adaptation, no H–K |
| **OkLCh** | Cylindrical OkLab | L, C, H° | **Building palettes and ramps** | Large regions of (L, C, H) are outside every real gamut; you must clamp |
| **HSL / HSV** | Convenience transform of sRGB | H, S, L/V | Nothing serious. Legacy pickers | "L" is not lightness. See §2.4 |
| **HCT** | Google's hybrid | H, C, T | Material 3 tonal palettes with contrast guarantees | Proprietary-adjacent; T is CIELAB L\*, so inherits its quirks |

### 2.2 sRGB, exactly

Verified primaries and white point (source: https://en.wikipedia.org/wiki/SRGB, retrieved
2026-07-29) [verified]:

| | x | y |
|---|---|---|
| Red | 0.6400 | 0.3300 |
| Green | 0.3000 | 0.6000 |
| Blue | 0.1500 | 0.0600 |
| White (D65) | 0.3127 | 0.3290 |

Transfer function, decode direction (8-bit value `V` → linear `c`):

```
v = V / 255
c = v / 12.92                      if v <= 0.04045
c = ((v + 0.055) / 1.055) ^ 2.4    otherwise
```

The linear→encoded breakpoint sits at `c = 0.0031308`; slope of the linear toe is 12.92; the power
segment uses exponent 2.4 with a 0.055 offset, giving an *effective* gamma near 2.2 across most of
the range. Linear RGB → XYZ (D65):

```
X   0.4124  0.3576  0.1805   R
Y = 0.2126  0.7152  0.0722 · G
Z   0.0193  0.1192  0.9505   B
```

The middle row is the relative-luminance equation WCAG uses. Note the weights: **green carries
71.5% of luminance, blue 7.2%.** Two immediate operational consequences.

- Changing the blue channel barely moves luminance. A blue-heavy brand colour will be dark in
  luminance terms almost regardless of how "bright" it looks. `#0000FF` has relative luminance
  0.0722 — computed: `0.2126·0 + 0.7152·0 + 0.0722·1.0`.
- Any averaging, blurring, resizing or opacity blend done on **encoded** (gamma-corrected) values is
  physically wrong. Convert to linear, operate, convert back. This is why naive 50% blends of
  complementary colours go muddy.

### 2.3 Gamut sizes, honestly

Coverage of **Pointer's Gamut** — an approximation of the gamut of real diffusely-reflecting surface
colours, from Michael Pointer's research, i.e. roughly "colours real objects can be"
(source: https://tftcentral.co.uk/articles/pointers_gamut, retrieved 2026-07-29) [verified]:

| Space | CIE 1931 xy | CIE 1976 u'v' |
|---|---|---|
| sRGB / Rec. 709 | 69.4% | 70.2% |
| Adobe RGB | 86.2% | 80.3% |
| DCI-P3 | 86.9% | 85.5% |
| Rec. 2020 | 99.9% | 99.7% |

Read that carefully: **sRGB cannot represent about 30% of real surface colours.** Saturated
oranges, deep cyans and vivid greens of actual physical objects are simply outside it. This is not a
rendering opinion; it is why a photograph of a marigold or a lacquered red bowl never looks quite
right in an sRGB JPEG.

Use `u'v'` figures, not `xy`, when comparing spaces. The 1931 xy diagram grossly over-weights the
green region, so xy percentages flatter wide-gamut spaces in green and understate them elsewhere.
Adobe RGB and DCI-P3 look nearly equal in xy (86.2 vs 86.9) but separate in u'v' (80.3 vs 85.5) —
the u'v' figure is the more honest one.

I measured the practical consequence for palette work directly. Maximum achievable OkLCh chroma at
fixed lightness and hue, sRGB vs Display P3, computed by binary search on gamut membership:

| OkLab L | Hue 22.3° (red) | Hue 85° (yellow-olive) | Hue 145° (green) | Hue 245° (blue) |
|---|---|---|---|---|
| 0.500 | 0.2016 → 0.2274 (+12.8%) | 0.1025 → 0.1182 (+15.3%) | 0.1575 → 0.2136 (+35.6%) | 0.1260 → 0.1637 (+30.0%) |
| 0.577 | 0.2326 → 0.2623 (+12.8%) | 0.1183 → 0.1364 (+15.3%) | 0.1817 → 0.2464 (+35.6%) | 0.1454 → 0.1889 (+30.0%) |
| 0.650 | 0.2362 → 0.2955 (+25.1%) | 0.1332 → 0.1536 (+15.3%) | 0.2046 → 0.2775 (+35.6%) | 0.1637 → 0.2128 (+29.9%) |
| 0.750 | 0.1506 → 0.1931 (+28.2%) | 0.1537 → 0.1772 (+15.3%) | 0.2361 → 0.3201 (+35.6%) | 0.1381 → 0.1496 (+8.4%) |

**The gain from P3 is not uniform — it is largest in green (~+36%) and blue (~+30%), smallest in
yellow (+15%).** So "we're going P3" buys you a much more vivid green and a much more vivid blue,
and almost nothing in yellow. If a brand's differentiating colour is a yellow-olive, P3 is nearly
pointless; if it is a vivid green, P3 changes the design space materially.

### 2.4 Why HSL lies about lightness

HSL is a trivial algebraic re-mapping of the sRGB cube. Its "L" is `(max + min) / 2` of the three
*encoded* channel values. It knows nothing about luminance and nothing about perception. Every
fully-saturated hue lands at exactly `L = 50%`.

Computed, all six sRGB corners at `hsl(H 100% 50%)`:

| HSL | Hex | Relative luminance Y | OkLab L | OkLCh C | WCAG vs white | APCA black-on-it (Lc) |
|---|---|---|---|---|---|---|
| `hsl(60 100% 50%)` yellow | `#FFFF00` | 0.9278 | 0.9680 | 0.2109 | 1.07 | 101.4 |
| `hsl(180 100% 50%)` cyan | `#00FFFF` | 0.7874 | 0.9054 | 0.1546 | 1.25 | 91.8 |
| `hsl(120 100% 50%)` green | `#00FF00` | 0.7152 | 0.8664 | 0.2948 | 1.37 | 86.5 |
| `hsl(300 100% 50%)` magenta | `#FF00FF` | 0.2848 | 0.7017 | 0.3225 | 3.14 | 48.5 |
| `hsl(0 100% 50%)` red | `#FF0000` | 0.2126 | 0.6280 | 0.2576 | 4.00 | 40.0 |
| `hsl(240 100% 50%)` blue | `#0000FF` | 0.0722 | 0.4520 | 0.3133 | 8.59 | 18.2 |

HSL calls all six "50% lightness". Their actual luminances span **0.0722 to 0.9278 — a factor of
12.9**. Their OkLab lightnesses span 0.452 to 0.968. Black text on the yellow scores APCA Lc 101
(comfortably readable body text); black text on the blue scores Lc 18 (below the Lc 30 absolute
floor for any text). Same HSL lightness. Opposite accessibility verdicts.

This is not a subtlety. It is the single most common source of broken design-system ramps: someone
builds `--red-500` through `--blue-500` at matched HSL lightness, ships it, and half the ramp fails
contrast while the other half is washed out. Björn Ottosson's colour-picker post makes the same
point with a demonstration image of "colours HSL considers to have the same lightness" that places
bright yellows next to dark blues at 50%
(source: https://bottosson.github.io/posts/colorpicker/, retrieved 2026-07-29) [verified].

Evil Martians document the second HSL failure mode: rotating hue alone changes perceived lightness,
so deriving an error-red from a brand accent by changing only `H` in HSL can silently break text
contrast (source: https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl, retrieved
2026-07-29) [verified].

**Rule: HSL is acceptable for exactly one thing — nudging hue on an already-approved colour while a
human watches. It is never acceptable as the basis of a generated ramp.**

---

## 3. Perceptual uniformity and why OkLCh is the right palette space

### 3.1 What OkLab is

Björn Ottosson published OkLab in December 2020; it entered CSS Color 4/5 drafts and is now
supported across major browsers (source: https://en.wikipedia.org/wiki/Oklab_color_space, retrieved
2026-07-29) [search-level]. It is a direct response to CIELAB's hue non-linearity, particularly the
unexpected hue and lightness excursions CIELAB shows in blues.

The full transform, verified against the specification
(source: https://bottosson.github.io/posts/oklab/, retrieved 2026-07-29) [verified]:

```
Step 1. XYZ (D65) -> cone-like LMS,  M1:
   +0.8189330101  +0.3618667424  -0.1288597137
   +0.0329845436  +0.9293118715  +0.0361456387
   +0.0482003018  +0.2643662691  +0.6338517070

Step 2. nonlinearity:  l' = l^(1/3),  m' = m^(1/3),  s' = s^(1/3)

Step 3. LMS' -> Lab,  M2:
   +0.2104542553  +0.7936177850  -0.0040720468
   +1.9779984951  -2.4285922050  +0.4505937099
   +0.0259040371  +0.7827717662  -0.8086757660
```

Fitted against three datasets: CAM16-generated pairs at constant lightness (varying hue/chroma),
CAM16-generated pairs at constant chroma (varying hue/lightness), and the "uniform perceived hue"
experimental data used to derive IPT — with colours constrained to Pointer's Gamut, i.e. fitted on
*natural surface colours* rather than the whole of colour space [verified, same source]. It uses
D65, which matches sRGB and Display P3, so no chromatic adaptation step is needed for screen work.

OkLCh is OkLab in cylindrical form: `C = √(a² + b²)`, `H = atan2(b, a)` in degrees.

### 3.2 Why it is the right space for palettes — and where it is not

The property that matters: **changing one coordinate changes one perceived attribute.** Change L,
lightness moves and hue does not. Change H, hue moves and lightness does not. That is exactly the
property a ramp generator needs and exactly the property HSL lacks.

Honest limitations, so you do not over-claim:

- **OkLab is not a colour appearance model.** It has no surround, no adaptation state, no
  Helmholtz–Kohlrausch correction. A saturated colour at L = 0.6 will look lighter than a grey at
  L = 0.6. If you need appearance under a specified viewing condition, you need CAM16 or CIECAM02,
  not OkLab.
- Raph Levien's technical review found few fundamental flaws but argued the pure cube-root transfer
  function was "not entirely compelling", preferring a form with more contrast in the near-black
  region (closer to CIELAB). He rates OkLab better than IPT on lightness and chroma prediction, and
  says IPT, ICtCp and OkLab are all similarly good on hue linearity
  (source: https://raphlinus.github.io/color/2021/01/18/oklab-critique.html, retrieved 2026-07-29)
  [verified]. His summary recommendation is positive: use it for gradients and similar tasks.
- Ottosson himself later introduced a corrected lightness `Lr` for the Okhsl/Okhsv pickers because
  plain OkLab L does not match CIELAB L\* well at the dark end [verified, colorpicker source].
- **Most of OkLCh space is imaginary.** At L = 0.97 and hue 22°, the maximum chroma reachable in
  sRGB is only **0.0146** (computed by binary search). You cannot have a vivid near-white. Any
  generator that ignores this produces either out-of-gamut values or silent clipping.

### 3.3 The alternative worth knowing: HCT

Google's Material 3 uses HCT: hue and chroma from CAM16, tone from CIELAB L\* (D65)
(source: https://material3-themes-manual.amoebelabs.com/basics/m3-analysis-introduction/, retrieved
2026-07-29) [verified]. The design motive is a *guarantee*: because L\* is close to linear in
perceived lightness while WCAG contrast ratio is not, a fixed tone difference bounds contrast ratio
from below.

| HCT tone difference | Guaranteed WCAG 2 contrast ratio |
|---|---|
| 40 | ≥ 3.0 |
| 50 | ≥ 4.5 |
| 60 | Material 3's own working minimum |

[verified, same source]. That is a genuinely useful property and OkLCh does not have it — OkLab L is
not CIELAB L\*, so no equivalent clean theorem holds. **Decision rule: if you need a
guarantee-by-construction against WCAG 2 numbers and you are inside a Material-flavoured system, use
HCT tone stops. For everything else — gradients, brand ramps, cross-hue harmony, CSS-native work —
use OkLCh and verify contrast numerically afterwards.**

---

## 4. Contrast and legibility: the real maths, and the real critique

### 4.1 WCAG 2, stated exactly

The formula (source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html, retrieved
2026-07-29) [verified]:

```
contrast ratio = (L1 + 0.05) / (L2 + 0.05)

L1 = relative luminance of the LIGHTER colour
L2 = relative luminance of the DARKER colour
L  = 0.2126·R + 0.7152·G + 0.0722·B   on LINEARISED channels
linearisation: c = v/12.92 if v <= 0.04045 else ((v+0.055)/1.055)^2.4,  v = V8bit/255
```

Range: 1:1 (identical) to 21:1 (black on white — check: `(1.0+0.05)/(0.0+0.05) = 21`).

Thresholds: 4.5:1 for normal text, 3:1 for large-scale text, where large-scale means ≥18 pt or ≥14 pt
bold; the Understanding document notes 1 pt = 1.333 px so those are ≈24 px and ≈18.5 px [verified].
SC 1.4.11 adds 3:1 for non-text UI components and graphical objects.

**Where 4.5 comes from.** This is worth knowing because people treat it as mystical. The stated
rationale: a contrast ratio of 3:1 is the minimum for standard text under ANSI-style
recommendations for normal vision; someone with roughly 20/40 acuity — cited as typical of an
80-year-old — loses about a factor of 1.5 in contrast sensitivity; so `3 × 1.5 = 4.5`
[verified, same source]. It is one multiplication applied to one legacy baseline. Not a
perceptual model.

**Where 0.05 comes from.** It is a flare/ambient-light term: an offset representing light reflected
off the screen surface, which prevents division by zero and compresses ratios at the dark end. Its
side effect is the formula's central defect (§4.3).

### 4.2 Worked contrast, on a real ramp

Computed for the ramp derived in §10 (brand hex `#C8102E`, OkLCh hue 22.31°):

| Stop | Hex | WCAG vs `#FFFFFF` | WCAG vs `#000000` | APCA Lc, black text on it | APCA Lc, white text on it |
|---|---|---|---|---|---|
| 50 | `#FAF3F3` | 1.09 | 19.18 | +99.8 | 0.0 |
| 100 | `#F5E3E2` | 1.24 | 16.97 | +91.8 | −13.6 |
| 200 | `#F2C4C1` | 1.56 | 13.44 | +78.1 | −29.1 |
| 300 | `#F59692` | 2.17 | 9.66 | +61.4 | −47.2 |
| 400 | `#FB585D` | 3.16 | 6.66 | +46.4 | −63.0 |
| 500 | `#E20032` | 4.91 | 4.28 | +33.0 | −76.6 |
| 600 | `#BB0027` | 6.68 | 3.14 | +23.8 | −85.5 |
| 700 | `#93031D` | 9.25 | 2.27 | +15.0 | −93.6 |
| 800 | `#6E0113` | 12.52 | 1.68 | +7.6 | −100.0 |
| 900 | `#4E010B` | 15.75 | 1.33 | 0.0 | −104.2 |
| 950 | `#310105` | 18.47 | 1.14 | 0.0 | −106.6 |

Read the crossover two ways, and note that **the two metrics disagree about where it is.**

- **WCAG 2** puts the pivot at stop 500: vs-white 4.91 and vs-black 4.28 are nearly equal. By that
  reading, black text is viable down to stop 500 (4.28:1 fails 4.5 marginally; stop 400 gives 6.66:1
  against black, comfortably passing).
- **APCA** puts the pivot between stops 300 and 400: black-on-300 is Lc 61.4 (fine for non-body
  text), black-on-400 is Lc 46.4 (only large/heavy text), black-on-500 is Lc 33.0 (barely above the
  absolute floor). White-on-400 is already Lc −63.0.

That gap of one to two ramp stops is exactly the APCA critique made concrete: WCAG 2 says black text
on `#E20032` is acceptable (4.28:1 — a whisker under AA, passing AA-large at 3:1); APCA says it is
near-unreadable at Lc 33. **In practice, believe APCA here.** Black text on a saturated mid-red is a
known-bad pattern, and the reason WCAG 2 tolerates it is the 0.05 offset plus the H–K blindness of a
pure-luminance metric.

Working rule for any ramp: **switch from dark text to light text one stop *earlier* than the WCAG
crossover suggests** — here, at stop 400, not 500.

### 4.3 The APCA critique, and how much of it to believe

APCA (Advanced Perceptual Contrast Algorithm, from Andrew Somers / Myndex) is the candidate
replacement developed for WCAG 3. Its criticisms of WCAG 2, as stated by its authors:

1. **The luminance estimate derives from an obsolete early draft** and the ratio equation is "not
   useful as it is not relative to human perception"; studies show WCAG 2 can pass pairs that are
   unreadable and fail pairs that are very readable
   (source: https://git.apcacontrast.com/documentation/WhyAPCA.html, retrieved 2026-07-29)
   [verified].
2. **WCAG 2 far overstates contrast for dark colours** — "4.5:1 can be functionally unreadable when
   a colour is near black" — which makes it unsuited to dark mode [verified, same source].
3. **Binary pass/fail is wrong for a continuous property** across a continuum of visual impairments
   [verified, same source].
4. **Polarity is ignored.** WCAG 2's ratio is symmetric; human vision is not. Dark-on-light and
   light-on-dark of the same ratio do not read alike [search-level].
5. **Font weight and size are ignored** beyond one coarse large-text threshold; a 300-weight and a
   700-weight at the same colours score identically [search-level].

Claims 1–3 are the strong ones and follow directly from the 0.05 offset. Verify it yourself:
`#000000` vs `#1B1414` (my ramp's grey-950 at L = 0.20) — luminances 0.0 and about 0.0257 — gives
`(0.0757)/(0.05) = 1.51`, but `#000000` vs `#807776` (grey-500, L = 0.577) gives roughly
`(0.1946+0.05)/0.05 = 4.89`. The formula compresses the entire near-black region into a narrow
ratio band while stretching the light region. That is why dark-mode palettes that "pass" often look
muddy.

APCA's own scale (source: https://git.apcacontrast.com/documentation/APCAeasyIntro.html, retrieved
2026-07-29) [verified]:

| Lc | Meaning |
|---|---|
| 90 | Preferred for fluent body text and columns; font ≥ 14 px / weight 400 |
| 75 | Minimum for body-text columns; ≥ 18 px / 400 |
| 60 | Minimum for non-body content text; 24 px normal or 16 px bold |
| 45 | Minimum for large/heavy text (36 px normal / 24 px bold); detailed pictograms |
| 30 | Absolute minimum for any text (placeholders, disabled); large semantic non-text |
| 15 | Minimum for discernible non-text ≥ 5 px; threshold of invisibility for many users |

Negative Lc = light text on dark background. For AAA-equivalent, add Lc 15 [verified, same source].

The APCA-W3 constants, so you can implement it rather than trust a widget
(source: https://github.com/Myndex/SAPC-APCA/blob/master/documentation/APCA-W3-LaTeX.md, retrieved
2026-07-29) [verified]:

```
Ys = 0.2126729·R^2.4 + 0.7151522·G^2.4 + 0.0721750·B^2.4     (R,G,B = V8bit/255)

soft black clamp:  if Y <= 0.022 then Y := Y + (0.022 - Y)^1.414

dark text on light bg:   S = (Ybg^0.56 - Ytxt^0.57) · 1.14 ;  Lc = (S < 0.10) ? 0 : (S - 0.027)·100
light text on dark bg:   S = (Ybg^0.65 - Ytxt^0.62) · 1.14 ;  Lc = (S > -0.10) ? 0 : (S + 0.027)·100
```

Note the deliberate asymmetry: exponents 0.56/0.57 for one polarity, 0.65/0.62 for the other. That
asymmetry *is* the polarity fix. Note also `^2.4` with no linear toe — APCA uses a simple power
curve, not the sRGB piecewise function, on purpose.

**Where to be sceptical.** The oft-repeated "86% of websites fail WCAG 2 contrast, and some failures
are due to the incorrect math of WCAG 2" [verified, WhyAPCA source] is an APCA-authored framing of a
third-party crawl statistic; the crawl measures failures, not which failures are spurious. Treat the
"and it's the formula's fault" half as advocacy, not measurement.
[UNVERIFIED - the underlying WebAIM-style crawl methodology and the share of WCAG 2 failures that
APCA would pass. Closing it needs the original crawl dataset re-scored under APCA.]

Also note: APCA is **not** normative. WCAG 2.1/2.2 remains the standard cited in procurement,
EN 301 549, the ADA-adjacent case law and Vietnam's public-sector accessibility expectations.

**The practical rule I use, and recommend:**

1. **Ship to WCAG 2 numbers.** It is what auditors, contracts and legal exposure use. Non-negotiable.
2. **Use APCA as the tie-breaker and the dark-mode sanity check.** When two options both pass
   WCAG 2 but one looks worse, APCA usually explains why — and the explanation is usually that both
   colours are dark.
3. **In dark mode, treat WCAG 2 as a floor and APCA Lc as the real target.** Aim |Lc| ≥ 75 for body
   text regardless of what the ratio says.
4. **Never rely on colour alone.** SC 1.4.1 requires that colour is "not used as the only visual
   means of conveying information, indicating an action, prompting a response, or distinguishing a
   visual element", and where colour distinguishes a link from surrounding text, keep 3:1 against
   that text *and* add a non-colour cue on hover/focus
   (source: https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html, retrieved 2026-07-29)
   [verified].
