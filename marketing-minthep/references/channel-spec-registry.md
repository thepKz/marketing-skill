# Channel Specification Registry

Platform requirements change. Treat every spec as a cache with source, placement, objective, and verification date—not timeless knowledge.

## Freshness policy

Before final export record:

```text
platform, placement, objective, ratio, dimensions, duration, format,
file-size limit, safe zone, source_url, verified_at, stale_after_days
```

Re-check when the placement/objective changes, the cached spec is stale, upload validation fails, or the platform updates its guide.

## Verified examples

Checked 2026-07-22:

- Meta Ads Guide image placements: Feed currently recommends 4:5; placement/objective can crop; max 30 MB and minimum width 600 px are documented on the live guide. Verify the selected placement: https://www.facebook.com/business/ads-guide/update/image
- TikTok Auction In-Feed: 9:16 recommended at least 540x960; 16:9 at least 960x540; 1:1 at least 640x640; common video formats and up to 500 MB. Safe zones vary with UI/caption: https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads?lang=en
- Google uploaded display: GIF/JPG/PNG up to 150 KB with placement-specific fixed sizes; HTML5 ZIP up to 600 KB: https://support.google.com/google-ads/answer/1722096?hl=en
- YouTube ads: duration depends on format; bumper is up to 6 seconds, Shorts guidance favors vertical under 60 seconds. Verify subtype: https://support.google.com/google-ads/answer/2375464?hl=en
- Google Performance Max: asset groups combine image, logo, copy, video, and extensions around one theme/audience; review automated assets and brand controls: https://support.google.com/google-ads/answer/10724492?hl=en
- Pinterest: standard images support PNG/JPEG and commonly recommend 2:3 or 1000x1500; video commonly recommends 6-15 seconds; collections require a hero plus secondary assets: https://help.pinterest.com/en/business/article/pinterest-product-specs and https://business.pinterest.com/en-in/creative-best-practices/
- LinkedIn: single image guidance includes 1200x627 JPG/PNG under 5 MB; carousel commonly uses 2-10 cards at 1080x1080; video supports multiple ratios and 3 seconds to 30 minutes under 500 MB. Verify placement: https://business.linkedin.com/advertise/ads/ads-guide and https://business.linkedin.com/advertise/ads/sponsored-content/video-ads/specs
- Amazon Advertising maintains placement-specific registries for DSP, video, Stores, ecommerce creative, Fire TV, and more: https://advertising.amazon.com/resources/ad-specs
- Google Merchant product images: stable crawlable URLs and supported formats are required; Google recommends high-resolution images and documents a 500x500 minimum effective 2027-01-31. Verify category and date: https://support.google.com/merchants/answer/6324350?hl=en

## Export QA

- Recompose; do not blindly crop.
- Keep product, face, logo, subtitles, disclosure, and CTA outside placement UI danger zones.
- Test at real display size, thumbnail, low-bandwidth, dark mode when relevant, and with images blocked for email.
- Preserve a source master and record every derivative.
