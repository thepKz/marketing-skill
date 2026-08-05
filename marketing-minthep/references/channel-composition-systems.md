# Channel Composition Systems

Use this reference before resizing campaign work for Facebook, Instagram, LinkedIn, TikTok, YouTube, or another social placement. Vendor specifications decide whether a file uploads. This reference decides whether the message still works after it uploads.

## Separate three contracts

1. **Message contract:** audience state, tension, promise, proof, CTA, disclosure.
2. **Composition contract:** first attention, image role, copy density, reading order, sequence, interface-safe geometry.
3. **Export contract:** ratio, dimensions, duration, file type, file size, character recommendations, vendor freshness.

Do not substitute one contract for another. A correct 4:5 export can still be a poor Instagram post, and an attractive LinkedIn document can still fail because its PDF pages use mixed sizes.

Read `data/channel-composition.csv` for the default house rules and `data/channel-specs.csv` for vendor-published limits. House rules are labelled as house rules; never present them as platform requirements.

## Platform defaults

### Facebook Feed

- Use when the reader may know little about the product and the post needs context, an offer, or a direct response.
- Reading order: recognisable subject or situation -> plain promise -> proof or offer -> action.
- Let the caption carry explanation. Keep the image to one decision and one proof cue.
- A Feed still and Feed video can share a campaign idea, but not necessarily the same composition or text field.

### Facebook Reels and Stories

- Build for vertical interruption and continuation: first frame -> visible mechanism or situation -> proof -> action.
- Keep critical copy away from the platform interface. When the official source publishes no numeric safe zone, mark it `undocumented`; do not invent a universal margin.
- Rebuild from the master. Never crop a Feed still into 9:16 and call it adapted.

### Instagram Feed

- Let the image establish taste, product recognition, or a save-worthy idea before copy explains it.
- Prefer a low-entropy image field, one compact text role, and a caption that adds meaning rather than repeating the image.
- For carousels, make each slide answer one question. Slide 1 earns the swipe; middle slides prove or teach; the last slide resolves the action.

### Instagram Reels and Stories

- Use a native 9:16 composition with subtitles or on-screen copy designed around the subject, not placed over it afterwards.
- Establish the subject and tension immediately. Do not spend the opening on a logo animation.
- Story frames need one action each. If the story requires three decisions, use three frames.

### LinkedIn Single Image

- Lead with a professional consequence, mechanism, market observation, or evidence-backed point of view.
- Compose for feed scanning: one claim, one proof object, one clear next step. Avoid consumer-ad slogans with no business context.
- LinkedIn officially recommends 1:1 and 4:5 templates and also documents a 1.91:1 landscape option. Choose by message shape, not habit.

### LinkedIn Document

- Treat the document as a proof sequence: tension -> framework -> evidence/example -> implication -> action.
- The cover earns the open; it does not carry the whole argument. Use one thought per page and keep page size consistent.
- PDF, PPT/PPTX, DOC/DOCX are supported in the cited advertising specification; lead-generation document ads require PDF. Flatten layered PDFs before delivery.

### LinkedIn Video

- Lead with the useful point, not with brand ceremony. LinkedIn's official guidance says to show the most impactful content in the first 10 seconds.
- Prefer 4:5 for a feed-dominant vertical frame when the subject permits it; use 9:16 only when the visual or distribution plan needs the taller canvas.
- Captions are a delivery requirement, not decoration. Export the caption file separately when the platform requires SRT.

### TikTok and short-form vertical

- Build around action, demonstration, transformation, or a human observation that is visibly connected to the product.
- First frame identifies the situation; the next frames pay off the hook. A hook unrelated to the product is a continuity failure.
- Keep captions readable over motion and re-check against the current platform overlay rather than a memorised safe-zone number.

## Cross-channel adaptation packet

For every selected channel, deliver:

1. placement and objective;
2. audience state and the one belief/action to change;
3. channel-specific headline or hook;
4. frame blueprint with reading order and protected UI zones;
5. caption/body copy and CTA;
6. carousel page plan or video beat sheet when applicable;
7. export row from `data/channel-specs.csv` or an explicit `unverified` state;
8. alt text, disclosure, owner, approval state, and metric.

## Headline and typography gate

- Let titles wrap naturally. Do not insert `<br>` or manual line breaks to manufacture a graphic shape.
- Default to one or two lines in feed graphics and one compact thought per carousel/document page.
- When the title does not fit, shorten it, widen its field, reduce size, then alter the composition.
- Keep the product, person, proof object, and title from competing at equal strength. One leads; the others support.

## Rejection labels

- `BLIND-CROP`: same layout trimmed into another ratio.
- `CHANNEL-SWAP`: same copy and hierarchy pasted across platforms.
- `UI-COLLISION`: subject, title, disclosure, subtitle, or CTA sits under platform controls.
- `TEXT-WALL`: image or first slide carries caption-length copy.
- `EMPTY-HOOK`: hook attracts attention but has no product or argument continuity.
- `DOCUMENT-AS-CAROUSEL`: LinkedIn document has decorative slides but no proof sequence.
- `FORCED-BREAK`: manual headline breaks create unnecessary lines or oversized type.
- `SPEC-AS-STRATEGY`: passing technical limits is presented as evidence the creative works.
