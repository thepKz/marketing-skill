# Image Output and Sharpening

Use this reference after image selection and local editing. Resolution, upscaling, sharpening, compression, and color management cannot repair incorrect anatomy, product geometry, text, masks, shadows, or reflections. Fix those first. Detailed calculations and current channel tables live in the deep dossier section at the end of this file.

## Output decision

Capture:

- final channel and placement;
- pixel dimensions or physical size;
- expected viewing distance;
- source pixel dimensions and crop;
- transparency, text, and color-profile requirements;
- byte/file-size limit;
- whether the asset is a master, working file, or derivative.

For print:

```text
pixels = physical inches * target PPI
target PPI at 20/20 acuity ~= 3438 / viewing distance in inches
```

Use device pixels for screens. Changing PPI metadata without resampling does not add detail.

## Master and derivative rules

- Preserve a full-resolution, versioned master before resizing or sharpening.
- Recompose first, then resize; do not crop a sharpened derivative into another ratio.
- Keep exact logos and typography as vectors or add them after image generation.
- Work in a wide enough source space when needed, then convert deliberately to the delivery profile, commonly sRGB for web/marketplaces unless the channel specifies otherwise.
- Never upscale a broken or tiny asset and label it production-ready.

## Three-stage sharpening

1. `capture correction`: restrained deconvolution or detail recovery for the source's softness.
2. `creative/local`: selective emphasis on product edges, eyes, texture, or food detail; protect skin, noise, halos, reflections, and text.
3. `output`: apply only after final resize, tuned to medium, dimensions, compression, and viewing distance.

Inspect at 100%, final delivery size, and thumbnail size. Reject halos, double edges, crunchy skin, amplified noise, moire, ringing around logos, and oversharpened bokeh.

## Upscaling gate

Upscaling is acceptable when it restores plausible texture and edges from a reasonably detailed source. It is not acceptable when it invents label text, packaging structure, facial identity, ingredients, jewelry, fabric patterns, or other truth-critical detail. Compare against the source and re-lock critical regions after upscaling.

## Format guidance

| Use | Starting format | Notes |
|---|---|---|
| Photographic web asset | AVIF or WebP with fallback where required | Tune by visual and byte QA, not quality number alone |
| Marketplace/zoom master | High-quality JPEG or required platform format | Verify live dimensions, background, and file-size rules |
| Transparency | PNG or supported lossless format | Check edge fringing on light and dark backgrounds |
| Email | JPEG or PNG | Assume image blocking; message must survive without the image |
| Print handoff | Printer-approved PDF/TIFF/JPEG workflow | Confirm bleed, profile, ink/black rules, and proofing |
| Logo/type/flat graphic | SVG or vector PDF where supported | Sanitize SVG and outline/embed fonts as required |

## Export QA record

Record `asset ID`, source dimensions, crop, output dimensions, profile, format, compression, sharpening pass, byte size, channel, and reviewer. Re-verify current official placement and marketplace specifications immediately before delivery.


---

<!-- Deep dossier merged from references/dossiers/resolution-sharpening-output.md (2026-08-06). Long-form research behind the working sections above. External facts retrieved 2026-07-29; re-check anything priced, versioned, or platform-specific.  -->

# Resolution, Sharpening, and Output Specification

## Scope

How to decide the pixel dimensions, colour space, file format, compression level and sharpening recipe for
every marketing deliverable — from a 1063x591 px business card to a 6x3 m billboard — with the arithmetic
shown rather than asserted. Covers the acuity maths behind PPI, DPI/PPI/LPI, three-stage sharpening,
resampling and ML upscaling limits, format economics with measured byte savings, colour management, print
prepress, and how to express all of it inside a text-to-image prompt. Retrieval date for all external
facts: 2026-07-29.

---

## 1. The resolution question, answered properly

### 1.1 The one thing to internalise

**An image file has exactly one intrinsic size measure: its pixel dimensions (W x H).** "PPI" (pixels per
inch) is not a property of the file — it is a *ratio* between the pixel dimensions and a chosen physical
output size. It appears in file metadata only as a *suggestion* to layout software about default placement
size. Changing the PPI number without resampling changes nothing about the image data.

The three quantities are locked together by one equation, and you always know two of them:

```
pixel dimension  =  physical size (inches)  x  PPI
PPI              =  pixel dimension / physical size (inches)
physical size    =  pixel dimension / PPI

Metric form:  pixels = mm / 25.4 x PPI
```

So the real question is never "what DPI should this be?" It is: **"at what physical size will this be
seen, and from how far away?"** Answer those two and the pixel count falls out.

### 1.2 The acuity maths that sets required PPI

Clinical 20/20 (6/6) vision is defined as resolving detail subtending **1 arcminute** of visual angle.
One arcminute = 1/60 degree = 2.9089 x 10^-4 radians.

At viewing distance `d`, the smallest resolvable feature has physical size `s = d x 2.9089e-4`. If you want
one pixel to be no larger than that feature:

```
PPI_required = 1 / (d_inches x 2.9089e-4) = 3438 / d_inches
PPI_required = 8732 / d_cm
PPI_required = 87.3 / d_metres
```

Equivalent framing: **20/20 acuity = 60 pixels per degree (PPD)** of visual angle. A 30 cycles-per-degree
grating (= 20/20) needs 60 samples/degree by Nyquist, and one degree subtends `d x tan(1 deg) = d x 0.017455`,
giving `60 / (d x 0.017455) = 3438/d`. Same number, two derivations — the "one pixel per arcminute"
convention is already Nyquist-correct, so **do not double it.** People who double it to "600 PPI for print"
have double-counted.

Two honest caveats:

| Caveat | Effect | Practical handling |
|---|---|---|
| Best human eyes reach ~50-60 cpd, not 30 | Required PPI up to 2x higher for a small minority under ideal light | Irrelevant for print (ink spread dominates); marginally relevant for phone displays |
| Vernier / hyperacuity resolves misalignment down to ~5 arcseconds | Aliased staircase edges and 1-px line jitter are visible *below* the 1-arcmin limit | This is why anti-aliasing and correct downscaling matter even when PPI is "sufficient" |

So: `3438/d` is the right target for **tonal detail**. **Hard geometric edges (type, logos, hairlines)
need more headroom** — that is a rendering problem, not a resolution problem, and the fix is vector, not
pixels.

### 1.3 Viewing-distance table (the one to memorise)

| Deliverable | Typical viewing distance | Required PPI at 20/20 (`8732/d_cm`) | Practical spec | Why the practical number differs |
|---|---|---|---|---|
| Business card, packaging small print, cosmetic label | 25 cm | 349 | **300-400 PPI** | Read at arm's tuck; type is the limiting element |
| Product held in hand, magazine, brochure | 30-35 cm | 291-249 | **300 PPI** | 300 is also 2x a 150 lpi screen — two constraints agree |
| Menu held at table | 40 cm | 218 | **250-300 PPI** | Cheap: sheet is small, file cost is trivial |
| Laptop screen | 50 cm | 175 | n/a — use device px | See 1.5 |
| Desktop monitor | 60 cm | 146 | n/a — use device px | See 1.5 |
| Menu board / A-frame / counter card | 1.0-1.5 m | 87-58 | **150 PPI** | Someone always leans in; 150 buys forgiveness |
| A1/A2 poster in a corridor | 1.0 m | 87 | **150 PPI** | Same |
| Poster, roll-up banner, window graphic | 2 m | 44 | **100-150 PPI** | First 2 m of a banner is where people stand |
| Trade-show backdrop, wall mural | 3 m | 29 | **72-100 PPI** | Print head native resolution becomes the floor |
| Bus shelter / metro 6-sheet | 3-4 m | 29-22 | **72-100 PPI** | Pedestrians pass within 1.5 m — protect the type |
| Building wrap / mesh | 10 m | 8.7 | **20-30 PPI** | Mesh weave, not pixels, is the limit |
| Roadside billboard | 20 m | 4.4 | **15-30 PPI** | Practitioner range for large-format billboards is roughly 10-30 PPI at full size (source: https://picturesizes.com/specs/print/billboard/, retrieved 2026-07-29, via search snippet) |
| Highway billboard | 50 m+ | 1.7 | **10-15 PPI** | Below this, ink dot structure dominates anyway |
| Cinema screen, mid-house | 12 m | 7.3 | Delivered as DCP 2K/4K | Frame is 12-20 m wide; 4096 px / 480 in ≈ 8.5 PPI |

**Worked check on a billboard.** A 6 m x 3 m board at 15 PPI:
`6 m = 236.2 in x 15 = 3543 px`; `3 m = 118.1 in x 15 = 1772 px`. Total **3543 x 1772 px = 6.3 MP.**
A 4K AI generation (3840 x 2160) is *already enough pixels* for a 6x3 m billboard. This is the single most
useful fact in this dossier: the "you need enormous files for billboards" belief is backwards. What
billboards actually need is **compositional simplicity and huge type**, not pixels.

### 1.4 Pixel-count arithmetic for standard print sizes

Formula: `px = mm / 25.4 x PPI`.

| Size | mm | @150 PPI | @200 PPI | @300 PPI | @400 PPI |
|---|---|---|---|---|---|
| Business card | 90 x 50 | 531 x 295 | 709 x 394 | **1063 x 591** | 1417 x 787 |
| Business card + 3 mm bleed | 96 x 56 | 567 x 331 | 756 x 441 | **1134 x 661** | 1512 x 882 |
| A6 postcard | 105 x 148 | 620 x 874 | 827 x 1165 | **1240 x 1748** | 1654 x 2331 |
| A5 flyer | 148 x 210 | 874 x 1240 | 1165 x 1654 | **1748 x 2480** | 2331 x 3307 |
| A4 | 210 x 297 | 1240 x 1754 | 1654 x 2339 | **2480 x 3508** | 3307 x 4677 |
| A4 + 3 mm bleed | 216 x 303 | 1276 x 1789 | 1701 x 2386 | **2551 x 3579** | 3402 x 4772 |
| A3 | 297 x 420 | 1754 x 2480 | 2339 x 3307 | **3508 x 4961** | — |
| A2 | 420 x 594 | 2480 x 3508 | **3307 x 4677** | 4961 x 7016 | — |
| A1 | 594 x 841 | **3508 x 4967** | 4677 x 6622 | 7016 x 9933 | — |
| A0 | 841 x 1189 | **4967 x 7022** | 6622 x 9362 | — | — |
| Roll-up banner | 850 x 2000 | **5019 x 11811** | 6693 x 15748 | — | — |
| Roll-up banner @100 PPI | 850 x 2000 | **3346 x 7874** | — | — | — |
| X-banner | 600 x 1600 | 3543 x 9449 | — | — | — |
| Billboard 6 x 3 m @15 PPI | 6000 x 3000 | — | — | — | **3543 x 1772** |
| Billboard 6 x 3 m @30 PPI | 6000 x 3000 | — | — | — | **7087 x 3543** |

Bold = the default to use unless the job says otherwise.

**Note on bleed:** bleed multiplies pixel count more than people expect on small items. A business card
gains 6.7% width and 12% height from 3 mm bleed. On an A0 it is negligible.

### 1.5 Screens: forget PPI, count device pixels

For screens, PPI is a red herring because you do not control the physical size — the device does. What you
control is the pixel count you hand the browser or app, and the CSS-pixel-to-device-pixel ratio (DPR).

```
device pixels needed = CSS layout width x DPR
```

DPR is 1 on legacy desktop, 2 on most phones and "Retina"-class laptops, 3 on flagship phones.

| Context | CSS width | DPR to serve | Device px to export |
|---|---|---|---|
| Full-bleed desktop hero | 1440-1920 | 1.5-2 (capped) | **2400-2880** (cap at 2560) |
| Content-column image | 720 | 2 | **1440** |
| Mobile full-bleed | 390-430 | 3 | **1170-1290** |
| Product thumbnail grid | 240 | 2 | **480** |
| Avatar | 48 | 3 | **144** |

**Why you cap at 2x and not 3x for large images:** perceptual gain from 2x to 3x on a large photograph is
near zero (the 2x version is already at or past acuity — see below) while bytes grow ~2.25x. Serve 3x only
for small elements where the byte cost is trivial and edges are hard (icons, logos, avatars).

**Screens are already past acuity.** Concrete checks using `3438/d_in`:

| Display | Width (in) | Native px | Actual PPI | Distance at which pixels become invisible |
|---|---|---|---|---|
| 27" 4K monitor | 23.5 | 3840 | 163 | 21 in / **53 cm** — so a normal 60-70 cm desk distance is already past acuity |
| 27" 1440p monitor | 23.5 | 2560 | 109 | 31.5 in / **80 cm** — visibly pixelated at desk distance |
| 55" 4K TV | 48.0 | 3840 | 80 | 43 in / **1.09 m** |
| 65" 4K TV | 56.7 | 3840 | 68 | 51 in / **1.29 m** |
| 65" 8K TV | 56.7 | 7680 | 135 | 25 in / **0.65 m** — nobody sits there; this is why 8K broadcast has no perceptual case |
| Any display above ~300 PPI | — | — | 300+ | Past acuity at 30 cm hand-held distance |

**The single most counter-intuitive screen fact.** A photograph viewed so it fills 30 degrees of horizontal
field of view (a comfortable, immersive-but-framed size) needs only `30 x 60 = 1800 px` of width to be at
the acuity limit. That is why a 2000-2500 px web hero looks flawless and why 24 MP camera files are
massively over-specified for screen delivery. Extra pixels buy **cropping latitude and print options**,
not screen quality.

### 1.6 Resolution myths, flagged

| Myth | Reality | Evidence / reasoning |
|---|---|---|
| "Web images should be 72 DPI" | Meaningless. Browsers ignore the PPI tag entirely and render 1 image pixel to 1 CSS pixel (scaled by DPR). 72 PPI is a fossil of the 1984 Macintosh display. | Physics: there is no inch in a browser. Notably, Etsy's own seller help still recommends "2000px for the shortest side, at a resolution of 72PPI" — a marketplace repeating the fossil in current documentation (source: https://help.etsy.com/hc/en-us/articles/115015663347-Requirements-and-Best-Practices-for-Images-in-Your-Etsy-Shop, retrieved 2026-07-29 via search snippet; the page returns 403 to direct fetch). Read it as "2000 px, and ignore the PPI clause." |
| "Print is always 300 DPI" | 300 PPI is correct for hand-held reading at ~30 cm on a 150 lpi coated press — two constraints that happen to agree. It is 7x over-specified for a poster at 2 m and 20x for a billboard. | See 1.3. Sending a 300 PPI file for a 6x3 m billboard means a 70,866 x 35,433 px file (2.5 gigapixels) that no RIP will accept. |
| "Set the file to 300 DPI in Photoshop and it's print ready" | Changing the PPI field *without resampling* changes only metadata. Changing it *with* resampling invents pixels by interpolation and adds zero information. | The equation in 1.1 |
| "You need 2 pixels per arcminute" | Double-counting. The 1-arcmin figure already corresponds to 60 PPD, which is the Nyquist rate for 30 cpd acuity. | Derivation in 1.2 |
| "More megapixels = better image" | Above the acuity requirement for the delivery size, extra pixels change nothing visible. They change crop latitude, upscale headroom, and storage cost. | 1.5 |
| "Higher DPI fixes a soft image" | Resolution and sharpness are orthogonal. A 100 MP file from a soft lens at f/22 has less resolved detail than a 12 MP file at f/5.6. | Diffraction: the Airy disc diameter grows linearly with f-number |

---

## 2. DPI vs PPI vs LPI vs SPI

### 2.1 Definitions that actually differ

| Term | Expands to | Belongs to | Typical values | What it controls |
|---|---|---|---|---|
| **PPI** | Pixels per inch | An image *at a chosen print size* | 72-400 | How much image data per unit of paper |
| **DPI** | Dots per inch | A **printing device** | Inkjet 720-2880; laser 600-1200; large-format 300-720 | The device's marking grid. Not yours to choose from the image side |
| **LPI** | Lines per inch | A **halftone screen** on a press | 45-200 | The frequency of the halftone cell grid used to fake continuous tone with solid ink |
| **SPI** | Samples per inch | A **scanner** | 300-9600 optical | Capture sampling rate |
| **PPD** | Pixels per degree | A **display + viewer** | 60 = 20/20 | The only device-independent sharpness measure |

Everyone says "DPI" when they mean "PPI". Accept the vocabulary drift when talking to clients; keep the
distinction internally, because **the number the press cares about is LPI and the number the file has is
pixel count**.

### 2.2 Halftone screen ruling and the quality factor

Offset lithography cannot print grey ink. It prints solid ink dots of varying size on a fixed grid. The
grid frequency is the **screen ruling** in LPI. Each halftone cell must be reconstructed from image data,
and Adobe's guidance is explicit:

> "The image resolution should generally be 1.5 to 2 times the screen frequency for the best halftone
> results."
> (source: https://helpx.adobe.com/photoshop/desktop/crop-resize-transform/resize-adjust-resolution/printer-resolution.html,
> retrieved 2026-07-29 via search snippet; direct fetch timed out)

**Quality Factor (QF) = image PPI / screen LPI.** Target QF 1.5-2.0.

| Press / stock | Screen ruling (LPI) | PPI at QF 1.5 | PPI at QF 2.0 | Spec this |
|---|---|---|---|---|
| Newsprint, coldset web | 85 | 128 | 170 | **170 PPI** |
| Newsprint, better quality | 100 | 150 | 200 | **200 PPI** |
| Uncoated sheetfed | 133 | 200 | 266 | **250 PPI** |
| Coated sheetfed, magazine interior (SWOP) | 133-150 | 200-225 | 266-300 | **300 PPI** |
| Premium coated, art book, cosmetics carton | 175 | 263 | 350 | **350 PPI** |
| Ultra-premium / stochastic-equivalent | 200 | 300 | 400 | **400 PPI** |
| Screen printing (textile, apparel) | 55-65 | 83-98 | 110-130 | **150 PPI** |
| Flexo, corrugated / kraft packaging | 45-85 | 68-128 | 90-170 | **200 PPI** |
| Pad printing, small-object | 100-133 | 150-200 | 200-266 | **300 PPI** |

Newsprint at 85 LPI and magazine interiors at 133 LPI per SWOP are the conventional reference points;
coated stock accepts 150 LPI and above because dot gain is lower (source:
https://helpx.adobe.com/photoshop/desktop/crop-resize-transform/resize-adjust-resolution/printer-resolution.html
and http://facweb.cs.depaul.edu/sgrais/color_line_screen.htm, retrieved 2026-07-29 via search snippet).
Screen-print and flexo rulings above are **practitioner-typical ranges, not standards** — always ask the
specific printer.

**Where QF > 2 actively hurts:** the RIP throws away the extra data, the file is 2-4x larger for nothing,
and — importantly — **output sharpening applied at the higher PPI gets downsampled by the RIP, softening
the result.** More is not free.

### 2.3 Inkjet and large format: no halftone screen

Photo inkjet and large-format printers use FM/stochastic dithering, not an AM halftone grid, so there is no
LPI to double. They have a **native input resolution** the driver resamples to:

| Device class | Native input PPI | Send this | Notes |
|---|---|---|---|
| Epson photo inkjet | 360 (or 720 in "Finest Detail") | **360 PPI** | 300 works; 360 avoids a resample |
| Canon / HP photo inkjet | 300 (or 600) | **300 PPI** | |
| Latex / UV large format | 150-300 driver-dependent | **100-150 PPI at final size** | Above 150 PPI at 3 m^2+ is waste |
| Dye-sublimation fabric | 150-200 | **150 PPI** | Fabric weave is the real limit |
| Digital press (HP Indigo, Xerox iGen) | 812-1200 DPI device | **300 PPI** | Behaves like coated sheetfed |

**Do not send a large-format print at 300 PPI "to be safe."** A 3 x 2 m banner at 300 PPI is
35,433 x 23,622 px = 837 MP. It will be rejected, and if accepted it will be downsampled with an unknown
kernel and no output sharpening — worse than a correctly prepared 150 PPI file.

---

## 3. Deliverable pixel-dimension registry (verified 2026-07-29)

Every platform spec below was retrieved on 2026-07-29. **Treat this as a dated cache, not knowledge.**
Re-verify before any final export; the existing skill reference
`../channel-spec-registry.md` already mandates recording `source_url` and
`verified_at` — this table supplies the pixel-dimension layer it was missing.

### 3.1 Social and paid media

| Placement | Ratio | Recommended px | Minimum | Max file | Formats | Source |
|---|---|---|---|---|---|---|
| Meta / Facebook Feed image ad | **4:5** | **1440 x 1800** | 600 x 750 (aspect tolerance 3%) | **30 MB** | JPG, PNG | https://www.facebook.com/business/ads-guide/image |
| LinkedIn single image, horizontal | 1.91:1 | **1200 x 628** | 640 x 360 (max 7680 x 4320) | **5 MB** | JPG, PNG, GIF | https://business.linkedin.com/advertise/ads/sponsored-content/single-image-ads-specs |
| LinkedIn single image, square | 1:1 | **1200 x 1200** | 360 x 360 (max 4320 x 4320) | 5 MB | JPG, PNG, GIF | same |
| LinkedIn single image, vertical | 1:1.91 | **628 x 1200** | 360 x 640 (max 2430 x 4320) | 5 MB | JPG, PNG, GIF | same |
| LinkedIn vertical alternates | 2:3 / 4:5 | **600 x 900 / 720 x 900** | as above | 5 MB | JPG, PNG, GIF | same |
| YouTube custom thumbnail | 16:9 | **3840 x 2160** | 640 px width | **2 MB mobile / 50 MB desktop** | JPG, GIF, PNG | https://support.google.com/youtube/answer/72431?hl=en |
| YouTube podcast playlist thumbnail | 1:1 | — | — | 10 MB mobile / 50 MB desktop | JPG, GIF, PNG | same |
| TikTok auction in-feed | 9:16 / 1:1 / 16:9 | — | **540 x 960 / 640 x 640 / 960 x 540** | 500 MB (video) | common video formats | https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads?lang=en (previously verified 2026-07-22) |
| Google uploaded display | fixed set | placement-specific | — | **150 KB** (GIF/JPG/PNG); 600 KB HTML5 ZIP | GIF, JPG, PNG | https://support.google.com/google-ads/answer/1722096?hl=en (previously verified 2026-07-22) |

**Two things worth flagging on this table.**

1. **YouTube's recommended thumbnail is now 3840 x 2160, not 1280 x 720.** The 1280x720/2MB figure is
   repeated in essentially every third-party "social media size guide" and is out of date as a
   *recommendation* (1280x720 still clears the 640 px minimum). The 2 MB limit now applies to mobile
   uploads only; desktop allows 50 MB.
2. **Google display's 150 KB ceiling is the tightest constraint in mainstream marketing.** It forces
   format and compression decisions that no other placement does — see 7.7.

Instagram Feed / Stories / Reels placements are documented per-placement inside the Meta Ads Guide and were
**not individually retrievable** on 2026-07-29 (the per-placement URLs 404). `[UNVERIFIED - needs check]`:
the widely-used 1080 x 1350 (Feed 4:5) and 1080 x 1920 (Stories/Reels 9:16) figures are consistent with the
Facebook Feed spec above and with the 3% aspect tolerance, but must be re-read from
https://www.facebook.com/business/ads-guide/update/image per placement before a paid delivery.

### 3.2 Marketplace / PDP listing minimums

| Marketplace | Minimum | Recommended | Maximum | File size | Formats | Notes | Source |
|---|---|---|---|---|---|---|---|
| **Google Merchant Center** | **500 x 500 px** | **1500 x 1500 px or above** | 64 megapixels | **16 MB** | JPEG, WebP, PNG, GIF, BMP, TIFF | New 500x500 minimum applies to **all products from 2027-01-31**; URL must be ASCII, RFC 3986, <=2000 chars, extension must match actual format | https://support.google.com/merchants/answer/6324350?hl=en |
| **Shopify** | — | **2048 x 2048 px** (square) | **5000 x 5000 px / 25 MP** | **20 MB** | PNG, JPEG, PSD, TIFF, BMP, GIF, SVG, HEIC, WebP (+ animated GIF/WebP) | Shopify's Imagery service auto-negotiates delivery format per client | https://help.shopify.com/en/manual/products/product-media/product-media-types |
| **Amazon** | 500 px shortest / **1000 px longest side** (zoom threshold) | **1600 px+ longest side**; 2000-3000 px common practice | 10,000 px | ~10 MB | JPEG (preferred), TIFF, PNG, GIF | Main image: pure white RGB 255,255,255; product fills **85%** of frame; no text/logo/border/watermark on main; sRGB; naming `ASIN.MAIN.jpg`, `ASIN.PT01.jpg` | Authoritative page is login-gated: https://sellercentral.amazon.com/help/hub/reference/external/G1881 — figures above from https://www.squareshot.com/post/amazon-product-image-dimensions, retrieved 2026-07-29 |
| **Etsy** | 635 px on first photo's width and height | **2000 px shortest side** | — | keep under 1 MB | .jpg, .gif, .png, .svg, .heic | Help doc's "72 PPI" clause is meaningless — ignore it | https://help.etsy.com/hc/en-us/articles/115015663347-Requirements-and-Best-Practices-for-Images-in-Your-Etsy-Shop (403 to direct fetch; via search snippet) |
| **Shopee** | 500 x 500 px, 1:1 | 1024 x 1024 px+ for zoom | — | 5 MB | JPG, PNG | Up to 9 images incl. cover; product should occupy a substantial share of frame | `[UNVERIFIED - needs check]` — official Shopee seller pages (banhang.shopee.vn/edu/article/3525) require login and returned no content. Figures from third-party guides https://www.fit.photos/en/blog/shopee-image-size-specifications and https://www.golocad.com/blog/sellers-guide-to-shopee-product-images/ |

**Amazon's specs carry a compliance edge the others do not.** Non-compliant main images can cause listing
suppression from search, not just a rejected upload. Verify against Seller Central directly (logged in)
before any Amazon delivery. Also note the numbers reported for Amazon are *internally inconsistent across
third-party sources* (500 vs 1000 px minimum, 1600 vs 2000-3000 recommended) — a strong signal that only
the gated primary source should be trusted.

**A single master that satisfies every marketplace above:** **2048 x 2048 px, sRGB, JPEG q88, 4:4:4, white
RGB 255,255,255 background, product at 85% frame fill, <2 MB.** It clears Amazon's 1600 px
recommendation, Google's 1500 px recommendation, Shopify's 2048 preference, Etsy's 2000 px, and Shopee's
1024 px, and it enables zoom everywhere. Derive every smaller crop from it; never upload the derivative
as the master.

### 3.3 Web

| Deliverable | Export px | Serve as | Byte budget |
|---|---|---|---|
| Full-bleed desktop hero | 2560 x 1440 (cap) | AVIF + WebP fallback, `srcset` at 2560/1920/1440/1080/720 | **<200 KB** at 1920w |
| Mobile hero | 1290 x 1720 | same | **<120 KB** |
| Content-column photo | 1440 wide | AVIF/WebP | <90 KB |
| PDP gallery main | 2048 x 2048 | JPEG q88 for zoom source; AVIF for the display size | <400 KB zoom source |
| Thumbnail grid | 480 x 480 | AVIF q55 | <15 KB |
| Logo / icon / flat graphic | vector | **SVG** (sanitised) or PNG-8 | <5 KB |
| Email header (images often blocked) | 1200 wide, 600 CSS | **JPEG q80 or PNG-8** — not AVIF/WebP | <100 KB; alt text carries the message |
| Open Graph / Twitter card | 1200 x 630 | JPEG q85 | <300 KB (some scrapers cap at 5 MB, some at 1 MB) |
| Favicon set | 32/48/180/192/512 | PNG + SVG | — |

**Email is the one place you regress deliberately.** Email client format support and image-blocking
behaviour is far behind the browser; ship JPEG or PNG, never AVIF/WebP, and design the layout to still
carry the offer with images off.

## Image editing

### Automatic edit-mode trigger

When the user supplies an image/reference and asks to `edit`, `fix`, `replace`, `remove`, `change`, `extend`, `reframe`, `restyle`, `retouch`, or create variants from that exact asset, treat the job as image editing rather than fresh generation. Preserve the supplied pixels and identity/product truth outside the named change. Use masks or localized edits when available; if the active runtime cannot edit or render images, return an executable edit contract and state that no edit was rendered.

### Build an edit contract

Before editing, separate the request into four lists:

1. **Change**: the exact regions, objects, colors, text, background, lighting, or composition to modify.
2. **Lock**: everything that must remain unchanged.
3. **Match**: perspective, grain, light direction, depth of field, reflection, material, and color behavior the new content must inherit.
4. **Reject**: artifacts or unintended transformations that invalidate the edit.

If the user supplies multiple references, rank them: identity, product, style, environment, composition.

### Identity-preserving makeup and outfit edits

When the edit target is an authorized real person, identity is a critical lock rather than a soft preference. Start every variant from the original target, not from another exploration output.

Preserve exactly:

- Head shape, facial width and height, cheek structure, jawline, chin, ears, and hairline.
- Eye shape, spacing, size, canthal direction, eyelid folds, brows, and natural asymmetry.
- Nose bridge, width, tip, nostrils, philtrum, lip boundary, cupid's bow, and resting closure.
- Skin tone, age presentation, identity marks, expression, gaze, head angle, and perceived person.
- Body proportions, pose, hands, camera, crop, lighting, and background unless explicitly listed under `Change`.

For makeup, allow pigment, finish, liner, lashes, blush, highlight, and lip-surface changes only. Reject eye enlargement, nose narrowing, jaw slimming, V-line creation, age change, skin replacement, ethnicity change, pore erasure, or any output that resembles a different person.

For wardrobe, use this contract:

```text
Change: wardrobe only
Lock: face, identity, hair, makeup unless requested, body proportions,
pose, hands, camera, crop, lighting, and background
Match: garment fit, seams, fabric behavior, folds, shadows, contact, and occlusion
Mask: visible clothing below the neck; preserve skin and flyaway-hair edges
Reject: face drift, body reshaping, pose drift, extra accessories,
beautification, skin replacement, copied logos, or full-image restyling
```

Run makeup and wardrobe as separate localized passes when both are requested. Pass the identity gate after makeup before changing wardrobe.

### Common edit workflows

#### Background replacement

- Preserve subject edges, flyaway hair, transparent materials, contact shadows, and reflected color.
- Match camera height, horizon, perspective, depth of field, and light direction.
- Rebuild realistic floor or surface contact; do not leave a cutout floating.

#### Product compositing

- Lock product geometry, logo, label, cap, color, and material.
- Match scene reflections to glossy or metallic packaging.
- Preserve real scale relative to hands, furniture, or environment.
- Add only claims and label text supplied by the user.

#### Human retouching

- Preserve identity and realistic skin texture by default.
- Make local corrections instead of globally smoothing skin.
- Keep natural facial asymmetry, hair detail, eye reflections, and hand anatomy.
- Do not change body shape, skin tone, age presentation, or facial structure unless explicitly requested.
- Reject rather than lightly score any output that is merely similar to the source person.

#### Object removal

- Reconstruct hidden texture and perspective rather than blurring the region.
- Check repeated patterns, edges, shadows, and reflections where the object existed.

#### Color or material change

- Preserve luminance, folds, highlights, texture scale, and reflected environment.
- Update secondary color spill and reflections caused by the changed surface.

#### Text and packaging change

- Prefer adding exact typography in design software after image generation.
- If image editing must render text, provide the exact string, position, hierarchy, and reference, then inspect every character.
- Reject pseudo-text, misspellings, duplicated logos, and inconsistent perspective.

### Multi-pass strategy

Use the smallest edit per pass when fidelity matters:

1. Establish composition or background.
2. Fix subject integration and light.
3. Correct product or identity details.
4. Add typography outside the image model when possible.
5. Export channel crops from the verified master.

Do not repeatedly regenerate the entire image for a local defect. Use masks or localized edits when the tool supports them.

### Edit QA

Inspect at full size and thumbnail size:

- Edges and masks.
- Hands, face, hair, logos, labels, and small repeated details.
- Contact shadows, reflections, and light direction.
- Perspective and scale.
- Color spill and white balance.
- Compression, grain, sharpness, and depth-of-field continuity.
- Differences from the lock list.
