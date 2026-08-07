# Channel Specification Registry

One shoot, exported once, posted everywhere. That is how almost every small-business asset in Vietnam gets made, and it is where the money leaks: Facebook Feed takes a 1:1 still and crops the price off the bottom, the Reel beside it went out at a size Instagram recommends against, and the six-second bumper somebody cut at eight seconds was never going to be accepted at all. None of that is a taste argument. Each one is a published number the exporter did not know about.

This unit is that set of numbers, read off the vendor pages rather than remembered, plus a script that compares a finished file against them.

- `data/channel-specs.csv` — 28 placements across Meta, LinkedIn, TikTok, Google Ads, YouTube and Google Merchant, each row stamped with the URL it came off and the date somebody read it.
- `scripts/check_channel_spec.py` — one asset against one placement, or against every registered placement at once.

## What the earlier version of this file got wrong

It said things like "commonly recommends 2:3", "guidance includes 1200x627", "video supports multiple ratios". Read that back and you can hear what it was: a memory of specs, dressed as a citation. Every hedge in it marked a number nobody had actually looked up, and hedged numbers are worse than no numbers, because they get used.

It also carried Pinterest, LinkedIn and Amazon, then removed all three with the argument that a small local shop does not advertise on LinkedIn. Pinterest and Amazon remain out of scope until a real route needs them. LinkedIn is back because the skill now serves founders, B2B work, agencies and professional services as well as local commerce; removing a channel from a general marketing system because one example business would not use it was a routing error.

## Three states, and why an empty cell is not one of them

Reading vendor pages in one sitting turns up something the hedged version had no way to express. A page can tell you three different things about a limit, and they are not interchangeable:

A **number**. Facebook Feed video caps at 4GB. That is a requirement; break it and the upload is refused.

A **stated absence**. Facebook Reels video documents no maximum length, in those words. TikTok Spark Ads document no restriction on ratio, resolution, file type, duration, bitrate or file size, because the ad *is* an existing organic post rather than an upload. Knowing a limit does not exist is a fact worth having.

**Silence**. Four Meta placements — Facebook Reels image, Instagram Feed image, Instagram Reels image, Facebook Stories video — publish a recommended size and a copy budget and then carry no technical-requirements block at all. No file ceiling. No minimum width. Nothing on tolerance.

That third state is the dangerous one, because silence reads as permission and it is not. The uploader still refuses something. The figure simply is not published, so the only honest answer is *go and find out*, and a table that wrote `0` or left the cell blank would be inventing an answer instead. So the CSV spells all three out:

| token | meaning |
| --- | --- |
| a value | the page publishes this figure |
| `unlimited` | the page states there is no limit |
| `undocumented` | the page publishes no such figure |
| `not-applicable` | the field does not exist here — no headline slot, no duration on a still |
| `per-placement` | not ratio-driven; the page tabulates exact pixel sizes instead |

`check_channel_spec.py` never returns `passed` against `undocumented`; it returns `review`, and it names the page you have to go and read.

## Requirement against recommendation

Meta publishes copy budgets under *Đề xuất về văn bản* and pixel floors under *Yêu cầu kỹ thuật*. One is advice and the other is enforcement, and a tool that failed your ad for a 46-character Instagram Reels caption would be lying to you about who rejects what.

So the script has two failure grades. `failed` means a documented requirement is broken: the upload is refused, or the crop is taken out of your hands. `review` means either the page publishes nothing, or it publishes a recommendation this asset sits outside.

A 200-character caption against a 125-character budget will publish and then truncate on a phone, which puts the ellipsis wherever the layout wants it rather than after a finished thought. Worth fixing, not worth blocking.

## Using it

Check one asset against one placement:

```bash
python scripts/check_channel_spec.py --placement meta-facebook-feed-video \
  --width 1080 --height 1920 --duration 0:42 --file-size 180MB --format mp4 \
  --primary-text "Com tam suon nuong than hoa, 45.000d, giao trong 20 phut"
```

The more useful question is the other way round. You have one file and a week of posting to fill, so ask where it can go untouched:

```bash
python scripts/check_channel_spec.py --survey \
  --width 1080 --height 1920 --duration 22 --file-size 30MB --format mp4
```

Read the resulting pass, fail and review groups as a posting schedule rather than as a score. A new
platform row changes the counts without changing the decision logic, which is why this reference no
longer hardcodes a survey total. Also useful:

- `--list-placements` — every key with its ratio, its floors, its ceilings and the date somebody last read the page it came from.
- `--show KEY` — one row in full, caveat included.
- `--output-format json` — for wiring into a pipeline.

Exit codes follow the rest of the toolkit: 0 clear, 2 a broken requirement, 3 needs a human.

## Rows that carry a warning as well as a number

Half the value of the sweep was in the exceptions, and those live in the `caveat` column rather than in prose here. Four worth knowing before you plan a shoot:

**Instagram Feed wants a different ratio for the still and the video.** 4:5 for the image, 9:16 for the video, on the same surface. One master cannot satisfy both, which is the real reason a still and a cut of the same shoot need separate exports rather than a resize.

**Instagram Reels changes its minimum width at thirty seconds.** 250 px under, 500 px at thirty and over. The table records the looser figure, so a 30-second cut can clear that row and still be refused. Cross the boundary and the rules move under you.

**Facebook Stories tolerates a third of what Feed does.** Three per cent on Feed, one per cent on Stories. The same slightly-off export is legal on one and cropped on the other.

**Google Merchant's 500x500 floor takes effect on 2027-01-31.** It is announced rather than enforced today, so a feed that passes now fails then, with no change on your side.

## Four surfaces with no row, and what each one returned

The domestic platforms are the ones this user needs most and the ones whose specs are hardest to cite. Every attempt is recorded here because a gap somebody documented is worth more than a gap somebody filled from memory. Checked 2026-07-31:

- **Shopee** — the Shopee Uni help article cited by an earlier version of this unit now returns 404 (`Tiếc quá, trang này hiện không tồn tại`). The site is a Vue bundle served from a CDN with no server-side rendering, and its education API answers `403 {"errcode":2,"message":"token not found"}` without a session. `robots.txt` disallows only `/account/`, so reading `/edu/` was permitted; it simply is not readable without an account.
- **TikTok Shop Vietnam university** — `401`.
- **Zalo developer documentation** — a single-page shell; the content arrives by script after load.
- **Lazada University** — the same shape.

Reverse-engineering an internal API to reach a help page was available and was not done. A number obtained that way has no citable source, which puts it in the same class as the hedged figures this rewrite exists to remove.

If you have a seller account on any of the four, the fastest honest path is to read the spec panel in the upload flow itself and add the row with that URL and today's date.

## Ninety days

`STALE_AFTER_DAYS = 90` in the script. It is not a vendor figure, because none of them publishes one. It is a bet, and the bet has already been settled once: the Shopee article above was cited from a live read and was gone within months.

Past ninety days the freshness gate returns `review` on every check against that row and names the page to re-read. Nothing in the row is wrong at that point, and nothing in it is confirmed either.

Re-read a row sooner than that when the placement or objective changes — Meta's URLs are keyed by both, and the specs differ across them — or the moment an upload is rejected against a spec this table says it should have passed.

## Export QA, after the numbers check out

Clearing the table is the floor, not the finish.

Recompose rather than crop. A 4:5 built by trimming a 9:16 has its subject in the wrong third and reads as a mistake even when nobody can say why.

Keep the load-bearing content out of the interface. Product, face, logo, subtitles, disclosure and call to action all need to sit clear of the platform's own furniture. TikTok publishes downloadable overlay files for exactly this, and its safe zone shifts with dimension, caption length and any extra format in play, so there is no single margin to memorise.

Check it at the size people see. Thumbnail, real display size, dark mode where it applies, and on a slow connection. In email, check it with images blocked, because a meaningful share of recipients will see it that way whether they chose to or not.

Keep the master and note every derivative against it. The reason is dull and it is the one that bites: six weeks later something needs a 4:5 and nobody can find the file that was not already 9:16.

## Channel deliverables

Platform specifications change. Verify current platform documentation before final export. Use ratios and safe-zone behavior as durable planning constraints; do not treat these notes as a substitute for live upload requirements.

### Universal master set

Design the composition independently for each master ratio:

- `9:16` vertical: short-form video, stories, reels.
- `4:5` portrait: feed-first product and human ads.
- `1:1` square: flexible feed, catalog, and testing assets.
- `16:9` landscape: video, web hero, presentation, and display contexts.
- Wide web hero: create a dedicated crop with protected copy space; do not stretch a social asset.

Keep logos, faces, product labels, and CTA copy away from UI overlays and crop edges. Preview at thumbnail size and on a narrow phone viewport.

### Meta

Use Meta Ads Library and the current Meta Ads Guide during research. Plan:

- A feed master with fast product recognition.
- A vertical story/reel master with the hook visible before sound or narration matters.
- A proof-led retargeting variant.
- A catalog-friendly product frame when ecommerce is relevant.

Avoid treating a static feed poster as a vertical video. Re-stage the composition for vertical depth and sequence.

### TikTok

Use TikTok Creative Center and TikTok Ads Library. Plan:

- A first-frame interruption tied to audience behavior, not random motion.
- Native pacing, readable captions, and a visible product mechanism.
- Creator or human variants that remain believable rather than over-scripted.
- A direct-response ending that does not invalidate the native tone.

Raw does not mean careless. Preserve clean audio, deliberate framing, and a clear edit rhythm.

### Google

Use the Google Ads Transparency Center and current Google Ads asset guidance. Build modular assets that retain meaning when recombined:

- Product-only visual.
- Product-in-use visual.
- Benefit-led visual.
- Brand or proof visual.
- Short, medium, and long message variants without contradictory claims.

Do not place essential copy only inside the image when the ad system may crop or combine assets.

### LinkedIn

Prioritize professional proof and decision context:

- Single-image insight or proof.
- Document or carousel narrative.
- Executive, customer, or operator viewpoint.
- Clear business outcome and next step.

Avoid generic office stock, staged handshakes, and decorative dashboards without a real claim.

### Pinterest

Use Pinterest Trends to understand query language, seasonality, and visual intent. Favor:

- Vertical discovery compositions.
- Useful, saveable structure.
- Clear product relationship to a desired future state.
- Search-aware titles and descriptions.

Do not copy a trending visual literally; translate the underlying intent into the brand's own materials and composition.

### Website and landing page

Deliver:

- Desktop and mobile hero direction.
- Full-page narrative order.
- Product and human image crop map.
- Loading, responsive, accessibility, and reduced-motion behavior.
- Social-to-page message continuity.

The ad promise and landing-page first viewport must agree. If the campaign uses a distinctive visual device, carry it into the page without repeating the same asset everywhere.

## Channel composition systems

Use this reference before resizing campaign work for Facebook, Instagram, LinkedIn, TikTok, YouTube, or another social placement. Vendor specifications decide whether a file uploads. This reference decides whether the message still works after it uploads.

### Separate three contracts

1. **Message contract:** audience state, tension, promise, proof, CTA, disclosure.
2. **Composition contract:** first attention, image role, copy density, reading order, sequence, interface-safe geometry.
3. **Export contract:** ratio, dimensions, duration, file type, file size, character recommendations, vendor freshness.

Do not substitute one contract for another. A correct 4:5 export can still be a poor Instagram post, and an attractive LinkedIn document can still fail because its PDF pages use mixed sizes.

Read `data/channel-composition.csv` for the default house rules and `data/channel-specs.csv` for vendor-published limits. House rules are labelled as house rules; never present them as platform requirements.

### Platform defaults

#### Facebook Feed

- Use when the reader may know little about the product and the post needs context, an offer, or a direct response.
- Reading order: recognisable subject or situation -> plain promise -> proof or offer -> action.
- Let the caption carry explanation. Keep the image to one decision and one proof cue.
- A Feed still and Feed video can share a campaign idea, but not necessarily the same composition or text field.

#### Facebook Reels and Stories

- Build for vertical interruption and continuation: first frame -> visible mechanism or situation -> proof -> action.
- Keep critical copy away from the platform interface. When the official source publishes no numeric safe zone, mark it `undocumented`; do not invent a universal margin.
- Rebuild from the master. Never crop a Feed still into 9:16 and call it adapted.

#### Instagram Feed

- Let the image establish taste, product recognition, or a save-worthy idea before copy explains it.
- Prefer a low-entropy image field, one compact text role, and a caption that adds meaning rather than repeating the image.
- For carousels, make each slide answer one question. Slide 1 earns the swipe; middle slides prove or teach; the last slide resolves the action.

#### Instagram Reels and Stories

- Use a native 9:16 composition with subtitles or on-screen copy designed around the subject, not placed over it afterwards.
- Establish the subject and tension immediately. Do not spend the opening on a logo animation.
- Story frames need one action each. If the story requires three decisions, use three frames.

#### LinkedIn Single Image

- Lead with a professional consequence, mechanism, market observation, or evidence-backed point of view.
- Compose for feed scanning: one claim, one proof object, one clear next step. Avoid consumer-ad slogans with no business context.
- LinkedIn officially recommends 1:1 and 4:5 templates and also documents a 1.91:1 landscape option. Choose by message shape, not habit.

#### LinkedIn Document

- Treat the document as a proof sequence: tension -> framework -> evidence/example -> implication -> action.
- The cover earns the open; it does not carry the whole argument. Use one thought per page and keep page size consistent.
- PDF, PPT/PPTX, DOC/DOCX are supported in the cited advertising specification; lead-generation document ads require PDF. Flatten layered PDFs before delivery.

#### LinkedIn Video

- Lead with the useful point, not with brand ceremony. LinkedIn's official guidance says to show the most impactful content in the first 10 seconds.
- Prefer 4:5 for a feed-dominant vertical frame when the subject permits it; use 9:16 only when the visual or distribution plan needs the taller canvas.
- Captions are a delivery requirement, not decoration. Export the caption file separately when the platform requires SRT.

#### TikTok and short-form vertical

- Build around action, demonstration, transformation, or a human observation that is visibly connected to the product.
- First frame identifies the situation; the next frames pay off the hook. A hook unrelated to the product is a continuity failure.
- Keep captions readable over motion and re-check against the current platform overlay rather than a memorised safe-zone number.

### Cross-channel adaptation packet

For every selected channel, deliver:

1. placement and objective;
2. audience state and the one belief/action to change;
3. channel-specific headline or hook;
4. frame blueprint with reading order and protected UI zones;
5. caption/body copy and CTA;
6. carousel page plan or video beat sheet when applicable;
7. export row from `data/channel-specs.csv` or an explicit `unverified` state;
8. alt text, disclosure, owner, approval state, and metric.

### Headline and typography gate

- Let titles wrap naturally. Do not insert `<br>` or manual line breaks to manufacture a graphic shape.
- Default to one or two lines in feed graphics and one compact thought per carousel/document page.
- When the title does not fit, shorten it, widen its field, reduce size, then alter the composition.
- Keep the product, person, proof object, and title from competing at equal strength. One leads; the others support.

### Rejection labels

- `BLIND-CROP`: same layout trimmed into another ratio.
- `CHANNEL-SWAP`: same copy and hierarchy pasted across platforms.
- `UI-COLLISION`: subject, title, disclosure, subtitle, or CTA sits under platform controls.
- `TEXT-WALL`: image or first slide carries caption-length copy.
- `EMPTY-HOOK`: hook attracts attention but has no product or argument continuity.
- `DOCUMENT-AS-CAROUSEL`: LinkedIn document has decorative slides but no proof sequence.
- `FORCED-BREAK`: manual headline breaks create unnecessary lines or oversized type.
- `SPEC-AS-STRATEGY`: passing technical limits is presented as evidence the creative works.
