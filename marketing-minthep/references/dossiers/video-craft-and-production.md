# Short-Form Video Craft and Production — Deep Reference Dossier

## What this is for

You are not a marketer and not a filmmaker, but you have to ship a 15–30 second vertical video that
makes someone want a bowl of food. This dossier is the operating manual: what shots to get, in what
order, how to cut them against music, how to make them sound edible, where the platform UI will eat
your text, how to grade so five clips look like one film, and what AI video models will and will not
do for you. It is written as decision rules with thresholds, because "it depends" does not get a
video published. Every factual claim carries an evidence marker; where a provider spec or a platform
number could not be confirmed from a primary page, it is named as a gap rather than guessed.

Retrieval date for all sources: **2026-07-29**.

---

## 0. Evidence ledger — what was actually read

Read this first. It tells you which parts of this document you can act on without re-checking, and
which parts you must verify before spending money.

| # | Source | What it grounds | Marker |
|---|--------|-----------------|--------|
| S1 | https://ads.tiktok.com/help/article/creative-best-practices | 9:16, ≥720p, hook in first 6s, proposition in first 3s, 5–10 words/sec text, 3–5 creatives per ad group | [verified] |
| S2 | https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads | 90% of ad recall impact in first six seconds; product-on-screen and CTA-card uplifts; 88% sound; faster scene changes; study attribution | [verified] |
| S3 | https://ads.tiktok.com/help/article/creative-specifications-for-streaming-ads | Streaming-ad video tile: 3:4 or 9:16, 6–15s, ≥720x960, ≥720p, ≥516 kbps | [verified] |
| S4 | https://developers.openai.com/api/docs/guides/video-generation | Sora 2 / Sora 2 Pro model ids, 16s and 20s generations, output sizes, reference-image rule, extension limits, likeness block | [verified] |
| S5 | https://ai.google.dev/gemini-api/docs/veo | Veo 3.1 model ids, 4/6/8s durations, 720p/1080p/4K, 16:9 and 9:16, reference images, extension to 148s, native audio, SynthID, 2-day retention | [verified] |
| S6 | https://ai.google.dev/gemini-api/docs/video | Gemini Omni Flash positioned as default video-gen model; Veo 3.1 for extension/last-frame control | [verified] |
| S7 | https://support.google.com/youtube/answer/10059070 | Shorts up to 3 minutes; max upload resolution 1080p | [verified] |
| S8 | https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | 4.5:1 normal text, 3:1 large text, 18pt / 14pt bold ≈ 24px / 18.5px | [verified] |
| S9 | https://www.reddigitalcinema.com/red-101/shutter-angle-tutorial | 180° shutter ≈ 1/48s at 24 fps; blur behaviour above/below 180° | [verified] |
| S10 | https://www.colborlight.com/blogs/articles/how-to-light-food-for-video | ~45° downward key, backlight halo, side light for form, uniform colour temperature, flags/bounce/gobos, heat warning | [verified] |
| S11 | https://www.socialmediatoday.com/news/tiktok-shares-new-data-on-the-importance-of-audio-elements-in-on-platform-p/603739/ | 68% brand recall / 58% stronger connection when music used; attributed to MRC Data and Flamingo, shared July 2021 | [verified] |

Sources that failed to load and therefore ground nothing here: the TikTok video-ad-specification help
article (404 at the URL tried), Meta Business Help Center Reels/Stories design pages (returned a
Vietnamese Feed-ads heading only, and a 404 on the ads-guide path), Runway's Gen-4 help article
(HTTP 403), the EBU R128 PDF (binary, unparsed), BBC subtitle guidelines (fetch blocked).
Everything that would have come from those is marked [search-level] or [UNVERIFIED] below.

**Marker meanings used throughout**

- `[verified]` — a page was fetched and read; URL and retrieval date given.
- `[search-level]` — only a search summary was seen; treat as a hypothesis, re-check before betting money.
- `[illustrative]` — an invented number used so arithmetic is followable. Not real. Never quote it.
- `[UNVERIFIED - X]` — a named gap; X is the specific check that would close it.
- `[craft rule]` — a production convention derived by reasoning from the verified constraints, not itself sourced. Safe to follow, but it is judgement, not fact.

---

## 1. Shot grammar and coverage

### 1.1 The five shot types you actually need

Short-form food video does not need the full cinematic vocabulary. It needs five shot classes, and
a spot that is missing a class reads as "flat" even when every individual shot is pretty.

| Class | What it shows | Typical framing | Lens/distance behaviour | Job in the edit |
|-------|---------------|-----------------|-------------------------|-----------------|
| **Establishing** | Where you are; that the place is real | Wide; room, counter, storefront, street | Wide, deep focus, hand-held OK | Orientation + credibility. Answers "is this a real shop?" |
| **Insert** | A single action fragment: ladle lifts, chopsticks pull, bottle pours | Medium-close on hands + object; frame excludes faces | Normal to short-tele, tripod or slider | Compresses time. Lets you jump from raw to finished without a jump cut |
| **Macro** | Texture at a scale the eye cannot get naturally: chilli oil beading, sesame on crust, condensation | Very close; subject fills >60% of frame | Macro or close-focus tele; must be stabilised | Appetite trigger. The "I can feel that" shot |
| **Hero** | The finished dish as a product portrait | Centred or slight off-centre; full dish in frame with headroom for text | Normal lens, gentle push-in or turntable | The purchase image. Must survive being paused |
| **Reaction** | A human responding — bite, eyes, laugh, nod, steam-inhale | Medium close-up on face and upper chest | Normal lens, eye-level | Social proof and permission. Converts "looks nice" into "people eat this" |

[craft rule] The coverage floor for a 15–30s spot is: **1 establishing, 3 inserts, 2 macro, 1 hero
(two angles), 1 reaction.** That is 8 distinct setups, ~10 clips. Below this you will be forced to
reuse shots, and reuse inside 30 seconds is the single most visible amateur tell.

**What breaks if you ignore each class**

- No establishing → viewer cannot place the food; ad reads as stock footage; trust drops.
- No inserts → you must cut wide-to-wide, which forces awkward dissolves or long dead-air holds.
- No macro → nothing triggers appetite; the video is *informative* instead of *hungry-making*.
- No hero → nobody can screenshot the dish; you lose the frame that gets shared.
- No reaction → no human presence; product-only spots feel like a catalogue.

### 1.2 Coverage discipline: the 3-2-1 rule per action

[craft rule] For every important action (pouring broth, cutting bánh mì, lifting noodles) shoot:

- **3** sizes: wide-ish context, medium insert, macro.
- **2** speeds: one at normal rate, one at high frame rate for slow motion.
- **1** safety: a repeat of the best size, framed 10–15% looser than you think you need.

The looser safety exists because vertical crops and platform UI (Section 6) will steal edges you did
not plan to lose. Reframing in post costs nothing if you shot loose; it costs the shot if you did not.

### 1.3 Continuity rules that matter at 30 seconds

At feature length, continuity is about plot. At 30 seconds it is about not making the viewer blink.

1. **Screen direction.** If noodles are lifted left-to-right in the wide, lift left-to-right in the
   macro. Reversing direction between adjacent cuts reads as a mistake even to viewers who cannot
   name why. Fix: mark the direction on your shot list before shooting.
2. **Food state monotonic.** Steam, ice, and crispness only ever degrade. Shoot in state order:
   macro of hot/fresh things FIRST, wides and set-dressing later with a stand-in bowl. Breaking this
   means your hero looks colder than the shot after it.
3. **Fill level monotonic.** A glass of cà phê sữa đá that is 80% full in shot 4 cannot be 95% full
   in shot 5. Track fill level as a column on the shot list.
4. **Hands and sleeves.** Same person, same sleeve, same watch across all inserts. A different wrist
   mid-sequence destroys the illusion of one continuous act.
5. **The 20% size jump.** Two adjacent shots at nearly the same size and angle produce a visual
   stutter. Either change size by roughly a third of frame height or change angle by ≥30°. [craft rule]

### 1.4 Camera movement: which moves are worth the risk

| Move | Cost/risk | Use for | Avoid when |
|------|-----------|---------|-----------|
| Locked-off tripod | Lowest | Macro, hero, anything with burned-in text over it | Never a wrong choice; can feel static if held >2s |
| Slow push-in (10–20% over 2s) | Low with a slider, high hand-held | Hero reveal, reaction build | Macro — focus breathing shows |
| Slide left/right | Low | Establishing, ingredient lay-down | When background has vertical lines that strobe |
| Overhead top-down + pivot | Medium (rig) | Assembly steps, ingredient grid | Deep bowls — you lose the broth |
| Whip pan | Medium | Transition between locations | Anything with text on screen |
| Hand-held follow | High (wobble) | "Real shop" energy, walking to table | When you will slow it down; wobble amplifies |

[craft rule] Cap yourself at **two moving shots per 15 seconds**. Movement everywhere reads as
nervous; movement nowhere reads as a slideshow.

### 1.5 Frame rate and shutter

- 180° shutter angle equals a shutter speed near 1/48s at 24 fps, the long-standing cinema norm;
  angles above 180° smear motion, below 180° make it stutter — [verified] (source: https://www.reddigitalcinema.com/red-101/shutter-angle-tutorial, retrieved 2026-07-29).
- [craft rule] Practical short-form settings: shoot the spine at **30 fps, shutter ~1/60** (matches
  the 30 fps delivery most platform guidance assumes) and shoot slow-motion inserts at **120 fps,
  shutter ~1/240**, conformed to 30 fps for 4× slow. Mixing 24 and 30 fps sources in one 30s spot is
  survivable but forces frame-blending on the 24 fps clips; pick one delivery rate and stick to it.
- What breaks: shooting everything at 120 fps to "keep options open" costs you low-light quality and
  makes dialogue/ambience unusable on those clips. Only the intentional slow-mo shots go high.
- [UNVERIFIED - fetch a current TikTok/Meta/YouTube upload-spec page that states an accepted or
  recommended frame-rate list] Whether 60 fps delivery is preferred over 30 fps on any given platform
  in 2026 was not confirmed; the one official TikTok creative page read here specifies resolution
  (≥720p) and 9:16 but not fps (source: https://ads.tiktok.com/help/article/creative-best-practices,
  retrieved 2026-07-29).

---

## 2. Storyboarding a 15–30 second spot

### 2.1 Why a board, when you could just film

A storyboard for a 20-second spot is not art direction. It is a **shot budget**. It forces you to
decide in advance how many distinct images you need, which means you know when to stop shooting and
whether you have enough before you strike the set. Without it, the standard failure is 40 clips of
the same three angles and no reaction shot.

### 2.2 The beat structure

TikTok's own creative guidance recommends a three-part structure — hook, body, close — and to
introduce the content proposition in the first 3 seconds while prioritising the hook in the first 6
[verified] (source: https://ads.tiktok.com/help/article/creative-best-practices, retrieved 2026-07-29).
Its creative blog states that 90% of ad recall impact is captured within the first six seconds
[verified] (source: https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads,
retrieved 2026-07-29).

That gives a defensible allocation:

| Duration | Hook | Body | Close | Distinct clips | Avg clip length |
|----------|------|------|-------|----------------|-----------------|
| 15s | 0.0–3.0s | 3.0–12.0s | 12.0–15.0s | 8–11 | ~1.4–1.9s |
| 20s | 0.0–3.0s | 3.0–16.0s | 16.0–20.0s | 10–14 | ~1.4–2.0s |
| 30s | 0.0–3.0s | 3.0–25.0s | 25.0–30.0s | 14–20 | ~1.5–2.1s |

Clip-count arithmetic worked through: a 20s spot at an average clip length of 1.6s needs
20 ÷ 1.6 = 12.5 → **13 clips**. If your coverage floor is 8 setups (Section 1.1), you must plan
at least 5 clips as second angles or second takes of existing setups. [illustrative arithmetic —
the 1.6s average is a planning convention chosen here, not a measured industry figure.]

### 2.3 Board format that survives contact with a phone

Six columns. Anything more and you will not fill it in on set.

```
| # | Time in–out | Shot class + size | Action (one verb) | Audio | Text on screen |
```

Rules for filling it:

1. **One verb per row.** "Ladle lifts, steam rises, hand reaches" is three rows, not one.
2. **Times must sum exactly** to the target duration. If they do not, you have not finished boarding.
3. **Text column decides framing.** A row with on-screen text needs its subject pushed out of the
   caption band before you shoot (Section 6), not after.
4. **Audio column names the source**, not the vibe. "Broth pour, close mic" not "appetising sound".

### 2.4 Worked board — 20s spot for a bún bò Huế shop

Target: 20.0s, 9:16, delivery 1080×1920 at 30 fps. Music bed at 96 BPM (Section 4 explains why).

| # | In–out | Shot | Action | Audio | Text |
|---|--------|------|--------|-------|------|
| 1 | 0.00–1.25 | Macro | Chilli-satay oil breaks the broth surface, ring spreads | Oil sizzle + broth glug, no music yet | none |
| 2 | 1.25–3.00 | Hero A | Full bowl of **bún bò Huế** lands on table, steam plume | Bowl-on-wood thunk, music enters on beat | "Bún bò Huế — 45.000 ₫" [illustrative price] |
| 3 | 3.00–4.50 | Establishing | Wide of the shop front, morning light, stools filling | Street ambience under music | none |
| 4 | 4.50–5.75 | Insert | Cleaver slices **chả** into rounds | Board knock ×3 | none |
| 5 | 5.75–7.00 | Insert | Ladle pulls broth from the pot, backlit | Deep liquid pour | none |
| 6 | 7.00–8.50 | Macro | Noodles lift, broth strands fall back | Wet noodle release | none |
| 7 | 8.50–9.75 | Insert | Herbs and **giá** dropped in, hand tears **rau** | Leaf rustle | none |
| 8 | 9.75–11.25 | Macro | Beef shank slice lowered onto noodles, gelatin wobble | Soft place | none |
| 9 | 11.25–13.00 | Reaction | Customer first spoonful, eyes close, nod | Slurp, room laugh | none |
| 10 | 13.00–14.50 | Insert | Squeeze of lime, seeds visible, juice hits broth | Citrus squeeze | none |
| 11 | 14.50–16.25 | Hero B | Slow push-in on bowl, chopsticks resting | Music lift | "Nấu từ 4h sáng" (cooked from 4am) |
| 12 | 16.25–18.00 | Establishing (tighter) | Storefront sign with name and hours | Ambience | Address line |
| 13 | 18.00–20.00 | Hero A hold + CTA | Static bowl, steam, chopsticks enter frame | Music resolves | Shop name + "Mở 6:00–11:00" |

Check: 13 clips, average 1.54s, all five classes present, hero used twice with different treatment
(A landing, A hold) plus a distinct hero B — that is legitimate reuse because framing and movement
differ, not lazy repetition.

### 2.5 The three-variant rule

TikTok's creative-best-practices page recommends between 3–5 different creatives per ad group and
3–5 diversified ad groups per campaign [verified] (source:
https://ads.tiktok.com/help/article/creative-best-practices, retrieved 2026-07-29).

Cheapest way to honour that from one shoot: board **one** spot, then plan two alternates that reuse
the same footage with a different first 3 seconds and a different close. Practical variant set:

- V1: macro-oil hook → price close.
- V2: reaction hook (clip 9 moved to position 1) → hours close.
- V3: establishing hook (real shop, real queue) → "nấu từ 4h sáng" close.

This costs zero extra shooting and gives you three hooks to test (Section 3.6).

---

## 3. The first-three-seconds problem

### 3.1 What the evidence actually supports

- Introduce the content proposition in the first 3 seconds; prioritise the hook in the first 6
  [verified] (source: https://ads.tiktok.com/help/article/creative-best-practices, retrieved 2026-07-29).
- 90% of ad recall impact is captured within the first six seconds [verified] (source:
  https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads, retrieved
  2026-07-29). The same page attributes its figures to TikTok Marketing Science studies from
  2020–2022 run with Ipsos, Kantar, Marketcast and Neuro-Insight — so treat them as platform-published
  vendor research, not independent peer review.
- Ads showing the product on screen are stated to drive a 65% increase in brand affinity and 25%
  uplift in recall; CTA cards a 45% lift in recall and 19% increase in likeability [verified] (same page).
- [UNVERIFIED - find a platform-published or independent study that reports view-retention decay by
  second for vertical video] The widely repeated claim that "most viewers drop off within the first
  2–3 seconds" was not confirmed from any page read here. Do not put a specific drop-off percentage
  in a deck.

### 3.2 What a hook must do, mechanically

Three simultaneous jobs in ≤3 seconds:

1. **Stop the thumb** — an image change large enough to register in peripheral vision.
2. **Declare the subject** — the viewer must know it is food, and roughly what food.
3. **Open a loop** — plant a question the next 5 seconds answer.

If a hook does only #1 it gets a view and no watch time. Only #2 and it is a catalogue. Only #3 and
it gets scrolled before the loop lands.

### 3.3 Hook taxonomy for food

| Hook type | Construction | Example (Vietnamese food) | Loop it opens | Risk |
|-----------|--------------|---------------------------|---------------|------|
| **Sensory macro** | Start inside the texture; no context | Chilli oil blooming on broth | "What dish is that?" | Can be too abstract; hold ≤1.2s |
| **Impact/arrival** | Object lands, sound punches | Bowl slammed on wood, steam | "Where is this?" | Needs strong sound; silent = weak |
| **Transformation start** | First frame of a change | Cold sugar hitting a hot pan | "What does it become?" | Must pay off by ~8s |
| **Reaction cold-open** | Face first, food second | Customer's eyes at first bite | "What is she eating?" | Requires a genuine reaction; fake reads instantly |
| **Scale/quantity** | Absurd amount, honest | 40kg pot of broth, whole beef shank | "Can I get that?" | Must be real; exaggeration invites comments calling it out |
| **Constraint/price** | Number as the first image | "45.000 ₫" over the bowl [illustrative price] | "For that?" | Price must be true and current |
| **Process secret** | Show the step nobody sees | Skimming the pot at 4am | "Do all shops do this?" | Boring unless visually distinct |

### 3.4 Hook construction rules

1. **Frame 1 must not be a logo, black frame, or slate.** You are spending your only guaranteed
   frame on nothing.
2. **First cut lands between 0.8s and 1.5s.** Longer and the opening reads as static; shorter and the
   viewer cannot parse the image. [craft rule]
3. **Motion inside the first frame**, not just between frames — steam, pour, a hand entering. A still
   image that starts moving at 0.5s wastes half a second.
4. **Sound on frame 1.** The first sound should be a *diegetic* food sound, not a music downbeat, so
   that muted viewers lose less and unmuted viewers get an immediate physical cue.
5. **Text in the hook ≤ 5 words**, high contrast, off the UI bands. Reading competes with looking.
6. **Say the dish name by 3s** — spoken, written, or unmistakably shown. This is what "introduce the
   proposition in the first 3 seconds" means for a food shop [verified, S1].
7. **No pre-roll ramp.** Music that fades in over 2s wastes your hook window; start the bed at full
   level or start with sound design only.

### 3.5 Hook failure modes and their fixes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Views high, 3s retention low | Hook is a curiosity trick unrelated to the food | Make the hook *be* the product |
| Low views at all | First frame visually flat / low contrast thumbnail-equivalent | Re-cut so frame 1 has a bright subject on a dark ground |
| Good retention, no clicks | Loop never closed; no CTA | Close explicitly in the last 3s; CTA cards are associated with recall lift [verified, S2] |
| Comments say "ad" | Logo-first, studio-clean, no room sound | Lead with hands, ambience, imperfect surfaces |
| Watch time collapses at ~7s | Body has no second hook | Put your second-best shot at ~7s, not your third |

### 3.6 Hook testing protocol (no analytics degree needed)

1. Cut one spot. Produce 3 versions differing **only** in seconds 0–3.
2. Publish/boost all three in the same period, same audience, same budget.
3. Read one metric only: retention at 3s (or, if unavailable, average watch time).
4. Keep the winner's hook; rebuild variants around it. Iterate weekly.
5. Do not change the close, the music, or the caption between variants in the same round — you will
   not know what moved.

[UNVERIFIED - confirm in TikTok Ads Manager / Instagram Insights documentation whether a per-second
retention curve is exposed for organic posts in your market] Whether you can read 3s retention
without paid promotion depends on the analytics surface available to your account.

---

## 4. Pacing and cut rhythm against a music bed

### 4.1 The core idea

Short-form video is edited to a grid, not to feeling. The grid comes from the music's tempo. Cutting
on-grid makes an amateur assembly feel deliberate; cutting off-grid makes even good footage feel
sloppy. TikTok's creative blog states that faster scene changes typically draw viewers in early,
increasing the chance of making an impression [verified] (source:
https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads, retrieved 2026-07-29).

### 4.2 Beat arithmetic you will use every time

Given tempo in BPM:

- Seconds per beat = 60 ÷ BPM
- Seconds per bar (4/4) = 240 ÷ BPM
- Beats available in a spot = duration × BPM ÷ 60

Worked examples (real arithmetic, arbitrary tempos chosen for illustration):

| BPM | Sec/beat | Sec/bar | Beats in 20s | Bars in 20s |
|-----|----------|---------|--------------|-------------|
| 90 | 0.667 | 2.667 | 30.0 | 7.5 |
| 96 | 0.625 | 2.500 | 32.0 | 8.0 |
| 100 | 0.600 | 2.400 | 33.3 | 8.33 |
| 120 | 0.500 | 2.000 | 40.0 | 10.0 |
| 128 | 0.469 | 1.875 | 42.7 | 10.67 |

**Why 96 BPM was used in the Section 2.4 board:** at 96 BPM a bar is exactly 2.5s, so 20s is exactly
8 bars. A spot that is a whole number of bars can end on a resolved musical phrase instead of a hard
mute. Choose tempo so that `duration × BPM ÷ 240` is a whole number: at 15s that is 96 BPM (6 bars),
at 30s that is 96 BPM (12 bars) or 128 BPM (16 bars).

### 4.3 Cut placement rules

1. **Every cut lands on a beat or a clean subdivision** (1/2 or 1/4 beat). At 96 BPM the legal cut
   grid is every 0.156s; in practice use every 0.3125s (half-beat) or coarser. [craft rule]
2. **Cut density follows the section:**
   - Hook (0–3s): 2–3 cuts. Fast enough to signal energy.
   - Body: 1 cut per 1–2 beats, i.e. 0.6–1.3s clips at 96 BPM for high-energy stretches, 2 beats
     (1.25s) as the default.
   - Close: slow to 1 cut per bar or hold a single shot for 2 bars so the CTA can be read.
3. **Never cut on the downbeat of a phrase you want to land.** Cut on the beat *before* it, so the new
   image arrives with the accent. [craft rule]
4. **One accent, one image.** If the bed has a hit at 8.5s, that is where your best macro starts.
5. **Slow-mo is a rhythm tool.** A 4× slowed clip should still start on a beat; its internal motion
   provides contrast against the cut grid.
6. **Reaction shots need ≥1.2s.** Faces read slower than objects; a 0.6s reaction is unreadable.
7. **Text needs ≥1.5s per line** — see Section 7.3 for the reading-speed derivation.

### 4.4 Turning the Section 2.4 board into a beat map

At 96 BPM: beat = 0.625s, bar = 2.5s. Beat numbers from 1 at t=0.

| Clip | In (s) | Beat | Bar | Length (s) | Length in beats |
|------|--------|------|-----|-----------|-----------------|
| 1 | 0.000 | 1 | 1 | 1.250 | 2 |
| 2 | 1.250 | 3 | 1 | 1.750 | 2.8 → snap to 3 beats (1.875) |
| 3 | 3.125 | 6 | 2 | 1.250 | 2 |
| 4 | 4.375 | 8 | 2 | 1.250 | 2 |
| 5 | 5.625 | 10 | 3 | 1.250 | 2 |
| 6 | 6.875 | 12 | 3 | 1.875 | 3 |
| 7 | 8.750 | 15 | 4 | 1.250 | 2 |
| 8 | 10.000 | 17 | 5 | 1.250 | 2 |
| 9 | 11.250 | 19 | 5 | 1.875 | 3 |
| 10 | 13.125 | 22 | 6 | 1.250 | 2 |
| 11 | 14.375 | 24 | 6 | 1.875 | 3 |
| 12 | 16.250 | 27 | 7 | 1.250 | 2 |
| 13 | 17.500 | 29 | 8 | 2.500 | 4 (one bar hold for CTA) |

Total = 20.000s exactly, 32 beats, 8 bars. Note what snapping did: clip 2 grew from 1.75s to 1.875s,
which pushed everything after it by 0.125s. **Always snap first, then re-derive times — never the
reverse.** If you snap after locking times you will end up 0.3–0.5s over and have to trim the CTA,
which is the one thing that must not be short.

### 4.5 What breaks

- **Off-grid cuts:** the video feels "wrong" and viewers cannot say why; typically read as low production value.
- **Uniform clip length throughout:** metronomic and hypnotic in a bad way. Vary between 2 and 3 beats.
- **Cut density constant from hook to close:** the CTA gets cut away before it is read; conversions drop.
- **Music chosen after the edit:** you will have to either re-cut everything or accept off-grid cuts. Choose the bed before the assembly.
- **Bed with a vocal in the CTA window:** the vocal competes with your only spoken/written offer. Pick an instrumental section for the close.

### 4.6 Music rights — the one non-craft rule

[UNVERIFIED - check the licence terms of the specific platform music library and of any commercial
library you use, for your business type and country] Platform-native music libraries frequently
distinguish between personal/creator use and commercial or branded use, and the rules differ by
platform and market. Do not assume that a sound you can add in-app is licensed for your shop's paid
ads. The verifiable position: this dossier cannot tell you your rights; the licence page can.
Consequence of ignoring this: takedown, muted audio on a running ad, or a claim against the account.

---

## 5. Sound design

### 5.1 Why sound is not decoration here

TikTok's creative blog states that 88% of TikTok users consider sound vital to the TikTok experience,
with half of users saying music makes content more uplifting, energizing and entertaining [verified]
(source: https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads, retrieved
2026-07-29). Separately, when brands feature music, 68% of TikTok users say they remember the brand
better and 58% say they feel a stronger connection — attributed to MRC Data and Flamingo research
shared in July 2021 [verified] (source:
https://www.socialmediatoday.com/news/tiktok-shares-new-data-on-the-importance-of-audio-elements-on-platform-p/603739/,
retrieved 2026-07-29; note the article does not report sample size or methodology, and the numbers are
platform-published).

Read the limitation honestly: these are platform-published figures about *sound and music generally*,
on *one platform*, some of them five years old at the time of writing.

### 5.2 The claim about food sound versus voiceover

The brief asserts that on-camera food sound sells more than a voiceover.

**[UNVERIFIED - would be closed by a controlled A/B test on your own account (same edit, two audio
treatments) or by a platform/academic study directly comparing diegetic food sound against voiceover
in short-form food ads]** No source read here compares food sound to voiceover. Do not present it as
a fact.

What *is* defensible, and why the craft convention exists:

1. Sound is stated to be vital to the platform experience for a large majority of users [verified, S2],
   so an audio-forward treatment is aligned with platform norms.
2. A voiceover is *claim-shaped*: it asserts the food is good. A slurp, a crust crack, a broth glug is
   *evidence-shaped*: it demonstrates a property (wetness, crispness, heat) that the viewer verifies
   themselves. Evidence resists scepticism better than assertion. [craft rule]
3. A voiceover occupies the same channel as the platform's cultural default (music + real sound) and
   often reads as "ad", which the same guidance warns against by recommending native, authentic,
   real-people content [verified, S1: "Use real people, movement, and sound" per the creative blog's
   native-content framing].
4. Voiceover is language-locked. Food sound travels across markets with no re-record. Practical, not
   theoretical: one asset serves Vietnamese and English audiences.

**Operational rule:** default to diegetic food sound + music bed + burned-in text. Use voiceover only
when you must state something that cannot be shown (a guarantee, an address, a limited-time offer) and
even then consider putting it in text. If you do use VO, test it against a no-VO cut (Section 3.6).

### 5.3 The four-layer mix

| Layer | Content | Target relationship | Notes |
|-------|---------|--------------------|-------|
| 1. Foreground sound design | Sizzle, pour, crack, slurp, knife-on-board, bowl-on-table | Loudest non-speech element; sits on top of the bed | Record close, 10–20cm, or replace with library/foley |
| 2. Music bed | One track, one tempo | Under layer 1 | Ducks under speech and under key food hits |
| 3. Ambience | Room tone, street, kitchen hum | Barely conscious | Removes the "dead studio" feel; keep a continuous bed so cuts do not click |
| 4. Speech (optional) | On-camera dialogue or VO | Clearest element when present | Everything else ducks |

[craft rule] Mix order of operations: get speech intelligible → place food hits so they punch through
→ set bed level last. Setting the bed first is why beginner mixes end up with music that eats
everything.

### 5.4 Recording food sound in practice

- **Record it separately.** The mic that shoots a wide establishing shot cannot capture a broth pour.
  Do a dedicated audio pass: same actions, mic 10–20cm away, camera irrelevant.
- **Sound is not always the real object.** Crisp fried shallot recorded close is often more convincing
  than the real dish's quiet sound; a wet cloth twisted near the mic reads as noodles. This is foley,
  it is standard practice, and it is not deceptive as long as the food and claims are real. [craft rule]
- **Kill the room.** Fridge, aircon, fan, extractor off for the audio pass. You cannot remove a hum
  without also thinning the sizzle.
- **Get 3 takes of each sound**, and 10 seconds of clean room tone. Room tone is the glue that hides
  edits.
- **What breaks:** using only camera audio means every cut changes the noise floor audibly — the edit
  sounds like a series of clicks. A continuous ambience layer fixes this and costs one file.

### 5.5 Loudness and levels

- EBU R 128 is the European broadcast normalisation recommendation, commonly cited at −23 LUFS
  programme loudness with a true-peak ceiling [search-level] — the PDF at
  https://tech.ebu.ch/docs/r/r128.pdf was fetched but returned unparsed binary, so the exact target,
  tolerance and peak ceiling are **[UNVERIFIED - re-fetch and read the R 128 PDF as text]**.
- Reported social-platform loudness targets in search summaries conflict badly: one source says
  YouTube ~−14 LUFS, Instagram/TikTok ~−10 to −12 LUFS, Facebook ~−13 LUFS; another says social
  platforms normalise around −14 LUFS across the board [search-level]. **[UNVERIFIED - find a
  first-party platform audio spec page stating a loudness target]**
- **Actionable rule that does not depend on the disputed numbers:** mix so that (a) speech is always
  intelligible over the bed, (b) true peaks stay below −1 dBTP so platform transcoding does not clip,
  and (c) the loudest food hit is the loudest thing in the piece after speech. Then listen on a phone
  speaker at half volume. If the slurp does not survive that, nothing else in the mix matters.
- **What breaks:** delivering a mix that peaks at 0 dBFS. Platform re-encoding adds intersample peaks
  and you get audible distortion on exactly the sounds you cared about.

### 5.6 Silence as a tool

[craft rule] One 0.3–0.5s near-silence immediately before the hero shot or the CTA makes the next
sound feel twice as loud without changing a single level. Use it once per spot. Used twice it reads as
a technical fault.

---

## 6. Framing for vertical 9:16 and platform safe zones

### 6.1 The canvas

- 9:16 vertical is the recommended orientation, shooting at least 720p, per TikTok's creative
  best-practices help article [verified] (source:
  https://ads.tiktok.com/help/article/creative-best-practices, retrieved 2026-07-29).
- TikTok's streaming-ads creative spec requires video tiles at 3:4 or 9:16, 6–15s, at least
  720×960 px, resolution ≥720p (HD), bitrate ≥516 kbps [verified] (source:
  https://ads.tiktok.com/help/article/creative-specifications-for-streaming-ads, retrieved 2026-07-29).
  Note this is the *streaming-ads* surface, not in-feed; do not generalise the 6–15s window to all placements.
- YouTube Shorts: up to 3 minutes long, maximum upload resolution 1080p [verified] (source:
  https://support.google.com/youtube/answer/10059070, retrieved 2026-07-29). The page read did not
  state aspect-ratio pixel requirements beyond expecting vertical video.
- **Master at 1080×1920, 9:16.** This is the widely used production resolution and is consistent with
  the 1080p ceiling YouTube states for Shorts [verified for the ceiling, S7; the 1080×1920 convention
  itself is [search-level]].

### 6.2 Safe zones — the honest state of the evidence

Every specific pixel margin below is **[search-level]** and the numbers *disagree with each other*.
The official pages that would settle this could not be loaded (TikTok video-ad-spec article 404;
Meta Business Help Center pages 404 / wrong content).

Reported figures, as seen in search summaries only:

| Platform | Top reserve | Bottom reserve | Left | Right | Source quality |
|----------|-------------|----------------|------|-------|----------------|
| TikTok (set A) | 108 px | 320 px | 60 px | — | [search-level] |
| TikTok (set B) | 120–130 px | 300–320 px | — | ~120 px | [search-level] |
| Instagram Reels (set A) | 220 px | 450 px | — | — | [search-level] |
| Instagram Reels (set B) | — | 400 px right-side / 270 px left | — | — | [search-level] |
| Instagram Reels (set C) | centre safe area given as 1010×1440 | | | | [search-level] |
| Meta unified (claimed 2026 change) | top ~14% | Stories ~20%, Reels ~35% | — | — | [search-level] |
| YouTube Shorts (set A) | 180 px | 390 px | 60 px | 60 px | [search-level] |
| YouTube Shorts (set B) | — | ~250 px | — | ~100 px | [search-level] |

Also seen [search-level]: a claim that as of March 2026 Meta consolidated Facebook Stories, Facebook
Reels, Instagram Stories and Instagram Reels into a single unified 9:16 safe zone; and that Meta Ads
Manager has a "Show Safe Zones" toggle. **[UNVERIFIED - confirm both on a Meta first-party page or in
Ads Manager itself]** If the unified-safe-zone claim is true it simplifies your life considerably, so
it is worth 10 minutes to check.

### 6.3 The rule that survives the uncertainty

Because the reported numbers conflict, do not design to any single set. Design to the **union of the
worst cases**, then verify by screenshot.

[craft rule] **Conservative universal safe area on a 1080×1920 master:**

- Top reserve: **260 px** (covers the 220 px Reels figure with margin)
- Bottom reserve: **480 px** (covers the 450 px Reels figure with margin)
- Left reserve: **80 px**
- Right reserve: **140 px** (right rail carries profile/engagement icons on multiple platforms)

That leaves a **critical-content box of 860 × 1180 px**, positioned x: 80–940, y: 260–1440. Compute:
1080 − 80 − 140 = 860 wide; 1920 − 260 − 480 = 1180 tall. That box is where headlines, price, logo,
CTA and any burned-in caption line must live.

Second, looser box for **subject** (the bowl, the face): keep the subject's essential mass inside
x: 60–1020, y: 180–1560, i.e. **960 × 1380**. Faces and dishes can bleed slightly under UI; text cannot.

**What breaks if ignored:** your price gets covered by the caption block, your logo sits under the
sound-disc, your CTA is behind the Follow button. None of this is visible in your editing timeline —
only on a real phone.

### 6.4 Verification procedure (10 minutes, do it every time)

1. Export the master.
2. Upload as a private/scheduled/draft post on each target platform.
3. Screenshot on a real phone — **two** phones if you can, one small (short viewport) and one large.
4. Overlay the screenshot on your master in any image editor; note where UI lands.
5. Save that overlay as a reusable template PNG for your project.
6. Re-do this every 3–6 months. Platform UI changes and your template silently goes stale.

### 6.5 Composing for vertical specifically

- **Vertical wants stacked depth, not lateral width.** A table shot laterally is a horizontal
  composition; shoot the same table from a 30–45° elevated angle so foreground bowl, mid-ground hands,
  background stove stack up the frame.
- **Subject scale must be larger than you are used to.** On a phone at arm's length, a dish occupying
  25% of frame height is a detail, not a subject. Target 45–70% for hero shots. [craft rule]
- **Headroom is text room.** For any shot that will carry a headline, deliberately compose the subject
  low so the y: 260–700 band is clean.
- **Negative space belongs on one side, consistently.** Alternating which side is empty across cuts
  makes the eye jump; keep the "quiet" side the same for a whole sequence.
- **Never shoot 16:9 planning to crop.** You lose 56% of the pixels and, worse, you lose control of the
  vertical composition. If you absolutely must (an existing camera locked to 16:9), shoot with the
  vertical crop marked on the monitor.
- **9:16 for capture, 4:5 for safety** [search-level suggestion seen for Shorts]: composing the
  critical action inside a centred 4:5 region of the 9:16 frame gives you a version that also works in
  feed placements. Treat as a bonus, not a requirement.

---

## 7. Captions and burned-in text

### 7.1 Two different things, do not confuse them

- **Captions / subtitles** = a transcript of speech, for accessibility and mute viewing.
- **Burned-in text / on-screen titles** = editorial statements: dish name, price, hours, offer.

A food spot with no dialogue needs **no** subtitles and **does** need titles. Auto-generated captions
over a spot with no speech produce nothing and waste your time.

### 7.2 Legibility spec

- WCAG 1.4.3 requires a contrast ratio of at least **4.5:1** for normal text and **3:1** for
  large-scale text, where large-scale means at least 18 point or 14 point bold (≈24 px and ≈18.5 px at
  1 pt = 1.333 px) [verified] (source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html,
  retrieved 2026-07-29). WCAG is a web standard, not a video standard, but it is the only *verified*
  numeric contrast threshold available and it is the right order of magnitude.

[craft rule] Translating that to a 1080×1920 video master:

| Element | Size (px cap-height/font) | Weight | Treatment |
|---------|---------------------------|--------|-----------|
| Headline / dish name | 72–96 px font | Bold / Black | White or near-white on a 60–80% opacity dark plate, or with a 3–4 px stroke |
| Price | 84–120 px | Black | Highest contrast in the frame |
| Subtitle line (speech) | 48–60 px | Medium/Bold | Plate or stroke; never plain white on food |
| Legal/address/hours | 32–40 px | Medium | Bottom of the safe box, not below it |

Non-negotiables:

1. **Never plain white text directly on food.** Broth, rice and crust are mid-to-light and busy;
   contrast fails locally even if it passes on average. Use a stroke, a drop shadow, or a plate.
2. **Test contrast against the brightest frame the text sits over**, not the average.
3. **Minimum size floor: 40 px on a 1080-wide master.** Below that, platform re-compression turns thin
   strokes to mush. [craft rule]
4. **One typeface, two weights.** Three typefaces in 20 seconds looks like a ransom note.

### 7.3 Reading speed and duration

- TikTok's creative best practices recommend displaying **5–10 words per second** when using text
  [verified] (source: https://ads.tiktok.com/help/article/creative-best-practices, retrieved 2026-07-29).
  Read that as a throughput ceiling for the whole piece, not a per-title instruction — 10 words on
  screen in one second is not readable as a single title.
- Broadcast/subtitling conventions reported in search summaries: roughly 12–17 characters per second
  or ~150–200 words per minute, 37–47 characters per line, maximum two lines, and per-subtitle display
  times in the 1–7 second range [search-level] — the BBC guidelines page could not be fetched, so
  **[UNVERIFIED - fetch BBC Subtitle Guidelines or an equivalent broadcaster spec and quote the exact
  reading-speed and duration figures]**.

[craft rule] Working numbers that satisfy both the platform ceiling and the broadcast convention:

- **Minimum on-screen time per title = 0.35s per word, floor 1.2s.** A 4-word title gets 1.4s;
  a 2-word title still gets 1.2s.
- **Maximum 7 words per title card**, maximum 2 lines, maximum ~24 characters per line at 72 px on a
  1080-wide frame (wider lines will not fit inside the 860 px critical box at that size).
- **Never more than one title on screen at a time.**
- Derivation check: a 20s spot with 5 title cards averaging 5 words = 25 words ÷ 20s = 1.25 words/s,
  comfortably under the 5–10 words/s ceiling [verified ceiling, S1]. If you find yourself needing
  60 words, your spot is a different spot.

### 7.4 Vietnamese-specific text rules

These matter and are routinely broken by templates designed for English:

1. **Diacritics need vertical room.** Vietnamese stacks tone marks over vowels that already carry
   diacritics: **ắ, ằ, ẳ, ẵ, ặ, ế, ệ, ỗ, ộ, ữ, ự**. A tight line-height clips the marks off, and
   `bún bò Huế` rendered as `bun bo Hue` or with a chopped `ế` is an instant credibility loss.
   [craft rule] Use line-height ≥ 1.35× font size for Vietnamese, and check every glyph with a mark
   *above* the x-height at the top of a line.
2. **Verify the font has full Vietnamese coverage** before you build a template. Many display faces
   include Latin-1 but drop `ơ ư ữ ự ệ ộ`. Symptom: tofu boxes (□) or a fallback font mid-word.
   Test string to render before committing: `Bún bò Huế — chả, giá, rau thơm — 45.000 ₫`.
3. **ALL-CAPS destroys diacritics' legibility** at small sizes and is harder to read in Vietnamese
   than in English. Prefer sentence case for anything longer than two words.
4. **Currency formatting.** Vietnamese convention uses a dot as thousands separator with the đồng sign
   after the number: `45.000 ₫`. Not `₫45,000`, not `45,000 VND` in consumer-facing creative (`VND` is
   fine in invoices and ad platforms). [craft rule — orthographic convention, confirm against your
   brand's own style sheet]
5. **Dish names are proper nouns of the cuisine — spell them fully.** `bánh mì`, `phở`, `bún bò Huế`,
   `cà phê sữa đá`, `gỏi cuốn`, `cơm tấm`. Dropping diacritics to save template hassle reads as a
   non-local brand.

### 7.5 Placement

- All text inside the **860 × 1180** critical box (Section 6.3).
- Speech subtitles sit **above** the bottom reserve, i.e. baseline no lower than y ≈ 1400 on a
  1080×1920 master.
- Keep text position consistent between cards. Text that jumps position between cards forces a re-fixation
  and effectively resets reading time.
- If the platform will also render its own auto-captions, your burned-in subtitle may collide with them.
  **[UNVERIFIED - check whether auto-captions are on by default and where they render for each target
  platform/market]** Mitigation that always works: no burned-in speech subtitles below the critical box,
  and prefer titles (which do not duplicate speech) over full transcript burn-in.

### 7.6 Animation

[craft rule] Titles should appear on a beat (Section 4), with a ≤6-frame fade or a 1–2 frame hard cut.
Slides, spins, typewriter effects and bounce easing cost readable time and look like template defaults.
A hard cut on the beat is stronger and cheaper than any animation you can buy.

---

## 8. Colour grading basics and shot matching

### 8.1 What grading is for in a 20-second food spot

Three jobs only:

1. **Match** — make 13 clips shot over three hours in changing light look like one piece.
2. **Appetite** — make the food read as fresh, hot, and the right colour.
3. **Consistency across a campaign** — video 8 should look like video 1 so the brand is recognisable.

Anything beyond that is styling for its own sake and will cost you time you do not have.

### 8.2 Order of operations

Do these in order. Doing them out of order means redoing them.

1. **Set exposure** per clip so the brightest important highlight (steam, rim light, a white plate)
   sits just below clipping, and shadows retain some detail.
2. **Set white balance** per clip. Reference: something you know is neutral — a white bowl, a steel
   ladle, a paper napkin. Get the *neutral* neutral before you make anything warm.
3. **Match contrast** across clips (black point and white point first, then mid-tone).
4. **Match saturation** globally, then correct individual hues.
5. **Apply a single look** (curve/LUT) to everything at the end, on a group/adjustment layer — not
   per-clip. This is what makes a spot feel unified.
6. **Local fixes last:** a mask to lift a dark bowl interior, a slight vignette to hold the eye.

### 8.3 The matching procedure that actually works

You cannot match by eye across 13 clips; your eye adapts within seconds.

1. Pick the **anchor shot**: your hero, best-lit, correctly white-balanced. Everything matches to it.
2. Put the anchor and the clip you are matching **side by side** on screen simultaneously.
3. Match in this order: **black level → white level → mid-tone brightness → colour temperature →
   colour tint (green/magenta) → saturation.** Doing colour before levels means redoing the colour.
4. Use scopes, not eyes, for the levels stage: a waveform to align black and white points, a vectorscope
   or parade to align the colour balance. Skin tones sit in a predictable region of a vectorscope;
   aligning the skin cluster across clips fixes reaction-shot mismatch fast.
5. **Check on a phone at 50% brightness.** A grade that looks rich on a laptop often looks muddy on a
   phone in daylight. If in doubt, add contrast and brightness rather than subtlety.

### 8.4 Food-specific colour rules

Grounded in the lighting source read: a key light at roughly 45° angled downward toward the table is
recommended for food; backlighting creates a halo that enhances brightness, depth and surface texture;
side lighting produces shadows that reveal form and detail; and you should keep colour temperature
uniform across all your lights (or deliberately adjust for ambiance), using flags, bounce cards or
gobos to control spill — while avoiding lights hot enough to degrade the food [verified] (source:
https://www.colborlight.com/blogs/articles/how-to-light-food-for-video, retrieved 2026-07-29).

That last point is the one people forget: **the lights cook your set.** Herbs wilt, ice melts, fat
congeals under a hot key. Shoot food-critical shots first and fast.

[craft rule] Grading targets for Vietnamese dishes:

| Dish/element | Read you want | Common failure | Fix |
|--------------|---------------|----------------|-----|
| Beef broth (**bún bò**, **phở**) | Warm amber-red, translucent, glossy | Grades orange-brown = looks like gravy | Lift saturation only in the red-orange range; keep highlights on the surface specular, do not crush them |
| Herbs (**rau thơm**, **giá**) | Cool, bright, unmistakably raw | Yellow-green = looks wilted | Nudge green hue slightly cooler; do not raise global saturation to fix it |
| Chilli oil / **sa tế** | Saturated red with visible separate oil layer | Blows out to a flat red patch | Protect highlights; that layer is only visible if the specular is not clipped |
| Rice / noodles | Clean white-to-cream, not blue, not yellow | Blue = wrong WB; yellow = looks stale | Use the noodles as your neutral reference |
| **Bánh mì** crust | Golden with dark shadow inside the score marks | Loses shadow detail = flat | Contrast in the mid-tones, not the blacks |
| **Cà phê sữa đá** | Distinct dark/light layers, condensation on glass | Layers merge to grey-brown | Backlight when shooting; separate luminance in the grade |
| Steam | Bright against a dark background | Invisible | This is a *lighting* fix — side or backlight — not a grade fix |

### 8.5 Warm ≠ appetising

The reflex is to warm everything. Warming a whole frame also warms the herbs (which then look wilted)
and the plate (which then looks dirty). [craft rule] Grade *selectively*: warm the food, keep the
whites neutral, keep the greens cool. If your tool has no hue-selective control, then warm only very
slightly and get your warmth from lighting instead.

### 8.6 Delivery and codec hygiene

- Master and export at 1080×1920. Do not upscale from a smaller capture — platform re-encoding punishes
  soft, noisy sources hardest.
- TikTok's streaming-ad tile spec requires bitrate ≥516 kbps [verified, S3]; that is a floor for a
  specific placement, not a target. [craft rule] Export short-form vertical at 10–16 Mbps H.264 High
  profile so re-compression has clean data to work from.
- Grain and heavy film emulation cost bitrate. Every bit spent on noise is a bit not spent on the crust.
- **[UNVERIFIED - fetch the current first-party upload/encoding spec pages for each target platform]**
  Container, codec, colour-space handling (in particular whether HDR or wide-gamut sources are
  tone-mapped or clipped) was not confirmed. Practical safety: deliver Rec.709 SDR, H.264, MP4, AAC.

---

## 9. Generated video: what the models can and cannot hold

### 9.1 The one thing to internalise

Current text-to-video and image-to-video generators are **shot machines, not scene machines**. They
produce clips of a few seconds with plausible motion. They do not maintain a world across cuts. Your
edit maintains the world. Every workflow below is built on that division of labour.

### 9.2 Verified capability facts (as of retrieval date)

**Google Veo 3.1 family** [verified] (source: https://ai.google.dev/gemini-api/docs/veo, retrieved 2026-07-29):

- Model IDs: `veo-3.1-generate-preview`, `veo-3.1-fast-generate-preview`, `veo-3.1-lite-generate-preview`.
- Supported durations: **4, 6, or 8 seconds**; 8 seconds is required for 1080p, 4K, or when using reference images.
- Resolutions: 720p / 1080p / 4K for Veo 3.1 and Fast; 720p / 1080p for Lite.
- Aspect ratios: **16:9 (default) and 9:16**.
- Image-to-video: all three support animating an input image as the starting frame.
- Reference images: **up to three** asset images, on 3.1 and 3.1 Fast only.
- Scene extension: supported on 3.1 and 3.1 Fast (not Lite), with combined output up to **148 seconds**.
- Audio: natively generates audio with video across versions.
- Watermarking: outputs are watermarked with **SynthID**.
- Retention: generated videos are stored on the server for **2 days**, then removed.
- Stated failure mode: generation can be blocked by safety filters.

**Google Gemini API video-generation overview** [verified] (source: https://ai.google.dev/gemini-api/docs/video,
retrieved 2026-07-29):

- Two models are presented: **Gemini Omni Flash** (described as fast, multimodal, for video generation
  and conversational video editing) and **Veo 3.1** (video with native audio).
- The docs recommend Gemini Omni Flash as the default for video generation, citing video coherence,
  multi-input reasoning across text/images/audio/video, character consistency, factual accuracy, and
  multi-turn conversational editing.
- Veo 3.1 is recommended when you specifically need scene extension, last-frame control, or integration
  with legacy pipelines.
- The overview page did **not** state Omni Flash's durations, resolutions or aspect ratios.
  **[UNVERIFIED - fetch the Gemini Omni Flash model page for duration/resolution/aspect-ratio limits]**

**OpenAI Sora 2** [verified] (source: https://developers.openai.com/api/docs/guides/video-generation,
retrieved 2026-07-29):

- Model IDs: `sora-2` (speed and flexibility; rapid iteration, concepting, rough cuts) and `sora-2-pro`
  (higher quality; production output).
- Both support **16- and 20-second generations**; maximum per generation is **20 seconds**.
- Supported sizes include **1280×720, 1920×1080, 1080×1920**, plus 480p variants. Pro is recommended for
  1080p exports at 1920×1080 or 1080×1920.
- Input reference image: **must match the target video's `size`**; formats image/jpeg, image/png,
  image/webp; it functions as the **first frame** of the video.
- Extension: continue a completed video into a new stitched result, up to 20 seconds per extension,
  maximum **six extensions (120 seconds total)**.
- Restriction: **character uploads depicting human likeness are blocked by default.**

**Runway** [search-level, and specifically flagged]: search summaries reported Gen-4 image-to-video at
5 or 10 seconds at 24 fps, an extension to longer character-consistent generations at higher credit
cost, and a "Custom Camera" panel in Gen-4.5 exposing focal length, f-stop, ISO and shutter angle as
numeric controls. The official help article returned HTTP 403 when fetched.
**[UNVERIFIED - fetch help.runwayml.com Gen-4 / Gen-4.5 articles or the Runway API reference to confirm
durations, fps, aspect ratios, and whether numeric camera controls exist and on which model]**

**All other providers, tiers, prices, credit costs and version strings: [UNVERIFIED - needs live doc
check].** No pricing appears anywhere in this dossier for that reason.

### 9.3 Capability matrix — what holds and what does not

Rows marked with a verified source apply to that provider only, on the retrieval date. Rows marked
[craft rule] are behavioural generalisations from how these systems work, not vendor claims.

| Capability | State | Practical consequence |
|-----------|-------|----------------------|
| **Clip duration** | Hard-capped: Veo 3.1 = 4/6/8s [verified, S5]; Sora 2 = 16/20s [verified, S4] | You cannot generate a 30s spot as one clip on Veo. Plan to assemble. |
| **Total length via extension** | Veo 3.1: up to 148s combined [verified, S5]; Sora 2: 6 extensions, 120s total [verified, S4] | Length is achievable; *continuity across the joins* is the risk, not the length. |
| **Vertical output** | Veo 3.1 supports 9:16 [verified, S5]; Sora 2 supports 1080×1920 [verified, S4] | Generate natively vertical. Never generate 16:9 and crop — you lose the composition and the resolution. |
| **Image-to-video from your own photo** | Supported: Veo 3.1 animates an input first frame [verified, S5]; Sora 2 reference image acts as the first frame and must match output size [verified, S4] | This is the highest-value use for a food business: your real dish photo, animated. Subject fidelity comes from *your* photo, not the model's imagination. |
| **Subject consistency within one clip** | Generally holds for a few seconds | Fine for a single continuous action. |
| **Subject consistency across separate clips** | Weak; the standard failure | [craft rule] Do not generate "the same bowl" twice and expect a match. Use reference images (Veo 3.1: up to 3 [verified, S5]) or last-frame chaining, and accept that a cut between two generations may need a grade match or a wipe/whip transition to hide drift. |
| **Character/person consistency** | Weak across clips; and Sora 2 blocks human-likeness uploads by default [verified, S4] | Do not plan a generated spokesperson or a recurring generated customer. Film real people for reaction shots. |
| **Camera motion control** | Prompt-level in general; numeric controls claimed for Runway Gen-4.5 [search-level, unconfirmed] | Ask for one simple move per clip ("slow push in", "static"). Compound moves ("push in while orbiting left then tilt down") reliably produce mush. [craft rule] |
| **Last-frame / first-and-last-frame control** | Veo docs list first-frame and first-and-last-frame workflows [verified, S5/S6 navigation and Omni-Flash guidance naming last-frame control for Veo 3.1] | This is your continuity tool: end clip A on the exact frame you begin clip B from. |
| **Legible text rendering in-frame** | Unreliable [craft rule] | **Never** ask the model for your shop name, price, or Vietnamese text with diacritics inside the image. Generate clean plates and add text in the editor. Vietnamese diacritics are the worst case; expect corrupted glyphs. |
| **Native audio** | Veo 3.1 generates audio natively [verified, S5] | Useful for scratch, but you will still want real food sound (Section 5). Generated audio also inherits the model's rhythm, not your bed's tempo. |
| **Physics of liquids, steam, stretch, pour** | Improving but the most common tell [craft rule] | Broth that flows wrong, cheese that stretches impossibly, steam that appears from the wrong place. Keep liquid actions short (<1.5s on screen) or shoot them for real. |
| **Counting and quantity** | Unreliable [craft rule] | "Three slices of chả" may yield two or four. Do not use generated video for anything where quantity is a claim. |
| **Watermarking / provenance** | Veo outputs carry SynthID [verified, S5] | Assume generated footage is detectable as generated. Plan disclosure accordingly. |
| **Output retention** | Veo: 2 days on server [verified, S5] | **Download immediately.** Losing a good generation to a 48-hour window is an avoidable, common, and infuriating mistake. |
| **Safety-filter blocking** | Documented for Veo 3.1 [verified, S5] | Budget extra time; a blocked generation is a schedule risk, not just an annoyance. |

### 9.4 Where generated video earns its place in a food spot

Ranked by risk-adjusted value:

1. **Establishing and atmosphere plates** you cannot shoot: a street at dawn, rain on the awning,
   an aerial. Low continuity burden, no product fidelity risk.
2. **Animating your own hero photo** into a slow push-in or a steam-rise. Product fidelity comes from
   your photograph; the model only adds motion. Best value-per-risk in the whole toolkit.
3. **Abstract texture/transition plates**: smoke, flour dust, oil ripple, used as wipes between real shots.
4. **Impossible camera moves** through a set you have already established with real footage.
5. **The hero dish itself, generated from scratch** — lowest recommendation. If the dish in the ad is
   not the dish you serve, you have an accuracy problem before you have a craft problem.
6. **Human reactions** — do not. Likeness restrictions [verified, S4], weak cross-clip consistency, and
   the uncanny-reaction effect all point the same way.

### 9.5 Prompt structure for one clip

[craft rule] One clip, one sentence-block, six slots, in this order:

```
[SHOT SIZE + LENS] , [SUBJECT with specific material detail] , [ONE ACTION] ,
[ONE CAMERA MOVE or "static camera"] , [LIGHT: direction + quality + colour temp] ,
[GRADE/FILM look] . [NEGATIVES if the tool supports them]
```

Worked example (structure is the deliverable; the model's output is not predictable):

> Macro shot, 100mm, a bowl of Vietnamese beef noodle soup with clear amber broth and a layer of
> red chilli oil on the surface, steam rising steadily, static camera, backlight from behind the bowl
> with soft side fill, warm 3200K key against a dark background, shallow depth of field, natural
> colour, no text, no on-screen writing, no hands.

Rules that reduce waste:

- **One action per clip.** Two actions gets you neither.
- **Name materials, not adjectives.** "Gelatinous beef shank with visible tendon" beats "delicious beef".
- **State the light.** Unstated light produces flat, generic light — and Section 8.4's whole appetite
  argument depends on directional light.
- **Always add "no text" style negatives** if your tool supports them; text rendering is unreliable and
  garbled signage is instantly disqualifying.
- **Fix the aspect ratio in the request** (9:16 where supported [verified, S5]) rather than cropping later.
- **Generate 3–4 variants per shot slot.** [illustrative] If your accept rate is around 1 in 4, a
  9-slot generated sequence needs ~36 generations; budget time and quota accordingly. That 1-in-4
  figure is a planning placeholder, not a measured rate — measure your own.

### 9.6 The hybrid pipeline (recommended default)

```
1. Board the spot (Section 2) and mark each row: FILM / GENERATE / STILL+ANIMATE.
2. Film everything that is (a) the actual product, (b) a human, (c) a liquid action, (d) carries text.
3. Photograph the hero dish properly — one great still is worth five mediocre clips.
4. Generate only: atmosphere plates, impossible moves, texture transitions.
5. Animate the hero still (image-to-video, 9:16, matching output size to the still) for the push-in.
6. Grade generated and filmed footage TOGETHER to one anchor (Section 8.3). Generated footage
   usually arrives more saturated and more contrasty; pull it back to the anchor, never the reverse.
7. Add text in the editor. Never in the model.
8. Build the real audio (Section 5). Discard model-generated audio unless it is genuinely better.
9. Download every accepted generation on the day you make it (2-day retention on Veo [verified, S5]).
10. Keep a generation log: prompt, model id, seed/settings, date, accept/reject. This is the only way
    to reproduce a look next month.
```

### 9.7 Disclosure and honesty

- Generated food imagery for a real menu item is a **misrepresentation risk**, independent of any
  platform policy. If the generated bowl has garnishes the shop does not serve, that is a false claim
  in the strongest sense.
- **[UNVERIFIED - check each platform's current synthetic/AI-content disclosure policy and the
  advertising-standards rules for food claims in your market, including Vietnamese advertising law]**
  This dossier will not name a regulation it has not read. What is certain: Veo outputs are SynthID-watermarked
  [verified, S5], so "nobody will know" is not a strategy.
- Safe default: use generated footage for mood, not for menu; and label AI-generated creative where the
  platform provides a toggle.

---

## 10. Pre-publish QC gate

Run every item. A failure here is cheaper than a failure in feed.

**Technical**
- [ ] 1080×1920, 9:16, single frame rate throughout, no black frames at head or tail.
- [ ] Duration exactly on target; last frame is a held image, not a mid-motion cut.
- [ ] True peaks below −1 dBTP; no clipping on the loudest food hit.
- [ ] Continuous ambience layer under every cut (no audible noise-floor jumps).
- [ ] Export bitrate high enough that a paused hero frame looks clean at 100%.

**Composition and text**
- [ ] All critical text inside the 860×1180 box (Section 6.3).
- [ ] Screenshot test done on at least one real phone per target platform (Section 6.4).
- [ ] Every title on screen ≥1.2s and ≥0.35s per word.
- [ ] Contrast passes against the *brightest* frame under each title (≥4.5:1 normal, ≥3:1 large [verified, S8]).
- [ ] Vietnamese diacritics fully rendered, no clipping at line tops, no tofu glyphs.
- [ ] Currency formatted `45.000 ₫`-style, and the price is the real current price.

**Craft**
- [ ] All five shot classes present (Section 1.1).
- [ ] No two adjacent shots within 20% of the same size and angle.
- [ ] Screen direction consistent; fill levels and steam monotonic.
- [ ] Every cut lands on a beat or half-beat; total is a whole number of bars.
- [ ] Dish name communicated by 3.0s [verified guidance, S1].
- [ ] Hook contains motion in frame 1 and a food sound in frame 1.
- [ ] Close holds ≥1 bar with the offer/CTA readable.

**Truth**
- [ ] Every dish shown is a dish you actually sell, as you actually serve it.
- [ ] Hours, address, price verified against the shop today.
- [ ] Any generated footage is atmosphere, not menu misrepresentation.
- [ ] Music licence checked for commercial use in your market [UNVERIFIED area — Section 4.6].

**Variants**
- [ ] Three cuts differing only in the first 3 seconds, ready to test (Section 3.6, aligned with the
      3–5 creatives per ad group guidance [verified, S1]).

---

## 11. Shot list template for a food business

### 11.1 Blank template (copy this)

**Header block**

```
PROJECT:            ................................  DATE: ..........
SHOP / DISH:        ................................
DELIVERABLE:        20s vertical 9:16 · 1080x1920 · 30 fps · master + 3 hook variants
MUSIC BED:          ........ BPM  (bar = 240/BPM = ...... s)
CREW:               camera .......... / food styling .......... / sound ..........
CALL:               ......  |  FOOD READY: ......  |  WRAP: ......
FOOD STATE ORDER:   macro-hot → hero → inserts → establishing → reaction
```

**Shot rows**

| # | Class | Size | Subject / action (one verb) | Move | Lens | fps | Light | Screen dir | Fill level | Audio pass | Text over | Take ✓ |
|---|-------|------|-----------------------------|------|------|-----|-------|-----------|-----------|-----------|-----------|--------|
| | | | | | | | | | | | | |

**Audio pass list (separate, after picture)**

| # | Sound | Source | Mic distance | Takes | ✓ |
|---|-------|--------|--------------|-------|---|

**Food & prop list**

| Item | Qty | Hero or stand-in | Prep timing | Who brings |
|------|-----|------------------|-------------|-----------|

### 11.2 Filled example — bún bò Huế shop, 20s spot

Header:

```
PROJECT:      Bún bò Huế — morning spot, July round
DELIVERABLE:  20s 9:16 1080x1920 30fps + 3 hook variants
MUSIC BED:    96 BPM (bar = 2.5s; 20s = 8 bars exactly)
FOOD STATE:   macro-hot first, establishing last
CALL:         05:30 (shop opens 06:00 — shoot the real queue)
```

| # | Class | Size | Subject / action | Move | Lens | fps | Light | Dir | Fill | Audio | Text | ✓ |
|---|-------|------|------------------|------|------|-----|-------|-----|------|-------|------|---|
| 1 | Macro | XCU | Sa tế chilli oil spoon breaks broth surface | static | macro | 120 | back + side, dark bg | — | full | oil+broth | — | |
| 2 | Hero A | MW | Bowl lands on wood table, steam plume | static | 35mm | 30 | 45° key, backlight for steam | — | full | bowl thunk | dish name + price | |
| 3 | Estab | W | Shop front, stools filling, morning light | slide L→R | 24mm | 30 | available | L→R | — | street amb | — | |
| 4 | Insert | MCU | Cleaver slices chả into rounds | static | 50mm | 60 | side key | L→R | — | board knock ×3 | — | |
| 5 | Insert | MCU | Ladle lifts broth from pot | static | 50mm | 120 | backlight | up | pot 3/4 | liquid pour | — | |
| 6 | Macro | CU | Chopsticks lift noodles, strands fall | static | macro | 120 | back + fill | up | full | noodle release | — | |
| 7 | Insert | MCU | Hand tears rau thơm, drops giá in | static | 50mm | 30 | side | into frame R | full | leaf rustle | — | |
| 8 | Macro | XCU | Beef shank slice lowered, tendon wobble | static | macro | 120 | side, hard | down | full | soft place | — | |
| 9 | React | MCU | Customer first spoonful, eyes close, nod | static | 50mm | 30 | window light, eye level | facing L | — | slurp + room | — | |
| 10 | Insert | CU | Lime squeezed, juice hits broth | static | macro | 120 | back | down | full | citrus squeeze | — | |
| 11 | Hero B | MCU | Bowl with chopsticks resting | push in 15% | 50mm | 30 | 45° key + back | — | full | (music lift) | "Nấu từ 4h sáng" | |
| 12 | Estab | MW | Sign: shop name + hours | static | 35mm | 30 | available | — | — | ambience | address | |
| 13 | Hero A | MW | Static bowl, steam, chopsticks enter | static | 35mm | 30 | as #2 | into frame R | full | resolve | name + "Mở 6:00–11:00" | |
| S1 | Safety | MW | Repeat #2, 15% looser | static | 35mm | 30 | as #2 | — | full | — | — | |
| S2 | Safety | CU | Repeat #6 at 30 fps for normal-speed option | static | macro | 30 | as #6 | up | full | — | — | |

Audio pass (after picture wrap, room silent, mic 10–20cm):

| # | Sound | Source | Takes |
|---|-------|--------|-------|
| A1 | Broth pour into bowl | real ladle + bowl | 3 |
| A2 | Noodle lift / wet release | real noodles; backup = wet cloth twist | 3 |
| A3 | Cleaver on board | real | 3 |
| A4 | Bowl set on wood | real | 3 |
| A5 | Lime squeeze | real | 3 |
| A6 | Slurp | real, close but off-axis | 3 |
| A7 | Room tone, shop empty | — | 30s |
| A8 | Room tone, shop with customers | — | 30s |

Food & props:

| Item | Qty | Hero / stand-in | Prep timing | Who |
|------|-----|-----------------|-------------|-----|
| Bún bò Huế, full assembly | 4 bowls | 2 hero, 2 stand-in | hero bowls plated 60s before roll | kitchen |
| Chả slices | 1 block | hero | slice on camera | kitchen |
| Beef shank, sliced | 12 slices | hero | cut cold, warm at last minute | kitchen |
| Rau thơm, giá | 1 tray each | hero | keep on ice, dry before frame | styling |
| Lime wedges | 6 | hero | cut fresh on the day | styling |
| Wooden table top / tray | 1 | — | wipe between every take | styling |
| Spray bottle (water) | 1 | — | refresh herbs | styling |
| Cotton balls + kettle | — | steam backup | [search-level trick: microwaved wet cotton hidden behind the dish reportedly yields 30–60s of visible steam; unconfirmed from a primary source] | styling |
| Black card / flag | 2 | — | control spill per [verified, S10] | camera |
| Clean white napkin | 1 | WB reference | every lighting change | camera |

**Shooting-order note.** The list is numbered in *edit* order; shoot in *food-state* order:
1, 8, 6, 10, 5, 2, S1, 11, 13, 4, 7, 9, 3, 12, S2. Rationale: everything hot and wet first, human
reaction while the shop is quiet enough to control, establishing shots last when the queue is real.
Breaking this order is the #1 reason the hero looks colder than the shot before it.

### 11.3 Time budget for the shoot [illustrative]

These durations are planning placeholders, not measured norms.

| Block | Duration | Notes |
|-------|----------|-------|
| Setup, light, WB | 45 min | Longest single block; do it before food |
| Macro/hot block (5 shots) | 40 min | Food degrades; move fast |
| Hero block (3 shots + safety) | 30 min | Re-plate between takes |
| Inserts (3 shots) | 25 min | |
| Reaction | 20 min | Real customer needs consent and patience |
| Establishing | 15 min | Requires the real queue → schedule to opening time |
| Audio pass | 30 min | Room must be silent |
| Contingency | 25 min | Something will spill |
| **Total** | **~3h50** | |

### 11.4 Reusable asset library (build it once)

Every shoot should deposit into a permanent library, because the second video costs half as much if
the first one was filed properly:

- `plates/` — clean texture and transition clips (steam, oil, flour, pour) with no product in frame.
- `ambience/` — room tone, street, kitchen, per time of day, 30s each.
- `foley/` — every food sound, named by action not by dish (`pour_broth_close_03.wav`).
- `hero_stills/` — high-res dish photographs, one per menu item, lit per Section 8.4. These are your
  image-to-video inputs (Section 9.6) and your thumbnail source.
- `templates/` — the safe-zone overlay PNG from Section 6.4, the title style with Vietnamese-safe font
  and ≥1.35 line-height, the grade anchor stills.
- `generation_log.csv` — prompt, model id, settings, date, accept/reject.

---

## 12. Gap register — what is still open

Close these before making decisions that cost money. Each line names the specific check.

1. **Platform safe-zone pixel numbers.** All figures in Section 6.2 are [search-level] and mutually
   inconsistent. *Close by:* loading TikTok's current video-ad-spec help article and Meta's Business
   Help Center Reels/Stories design pages, plus a YouTube Shorts spec page, and recording the first-party numbers.
2. **The claimed March 2026 Meta unified 9:16 safe zone** and the Ads Manager "Show Safe Zones" toggle.
   *Close by:* checking Meta's own help pages / opening Ads Manager.
3. **Frame rate and encoding preferences per platform.** *Close by:* first-party upload spec pages.
4. **Loudness targets for social delivery.** Reported values conflict (−10 to −14 LUFS). *Close by:*
   a first-party platform audio spec; and re-fetch EBU R 128 as readable text for the broadcast baseline.
5. **Subtitle reading-speed and duration standards.** *Close by:* BBC Subtitle Guidelines or an
   equivalent broadcaster document (the BBC fetch was blocked here).
6. **Food sound versus voiceover effectiveness.** No comparative evidence found. *Close by:* your own
   A/B test, or a study that compares the two directly. Until then it is a craft convention with a
   plausible mechanism, not a fact.
7. **Runway's current durations, fps, aspect ratios and whether numeric camera controls exist.**
   *Close by:* help.runwayml.com articles or the Runway API reference (403 on the attempt here).
8. **Gemini Omni Flash's duration / resolution / aspect-ratio limits.** *Close by:* its model page.
9. **All pricing, credit costs and rate limits for every generation provider.** Deliberately absent.
   *Close by:* provider pricing pages on the day you commit.
10. **AI-content disclosure policies per platform, and food-advertising rules in Vietnam.** *Close by:*
    platform policy pages and the applicable Vietnamese advertising regulations — read, not recalled.
11. **Music licensing for commercial use of platform-library sounds in your market.** *Close by:* the
    licence terms attached to the specific library.
12. **Whether per-second retention is visible for organic posts on your accounts.** *Close by:* opening
    the analytics surface for each account.
13. **Verification that any specific typeface you choose has complete Vietnamese coverage.** *Close by:*
    rendering `Bún bò Huế — chả, giá, rau thơm — 45.000 ₫` in the actual font.
14. **The steam-from-hidden-wet-cotton trick's reliability and timing.** [search-level] *Close by:*
    testing it on your own set before you need it.

Every number in this document marked [illustrative] — the 45.000 ₫ price, the 1-in-4 generation accept
rate, the shoot time budget, the 1.6s average clip length — is invented for arithmetic and must be
replaced with your own before it appears in anything anyone else reads.
