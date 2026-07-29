# Image Output and Sharpening

Use this reference after image selection and local editing. Resolution, upscaling, sharpening, compression, and color management cannot repair incorrect anatomy, product geometry, text, masks, shadows, or reflections. Fix those first. Detailed calculations and current channel tables live in `../_research/resolution-sharpening-output.md`.

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
