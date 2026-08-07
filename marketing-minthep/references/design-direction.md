# Design Direction

## Two disciplines, one artifact

Marketing and design are different jobs and this skill used to run them as one. Marketing decides
what is said: the truth map, the message, the offer, the locked copy, the claims that survive
`check_claims.py`. Design decides how it looks and feels — and once the content is locked, design
owns the form completely. No template, no default grid, no reserved percentage of space, no house
aesthetic. The craft tables (`layout-dials.csv`, `palettes.csv`, `slop-tells.csv`) are measuring
instruments pointed at a finished design; the moment one of them is used to *generate* the design,
every artifact converges on the same safe middle, which is the rigidity this file exists to end.

The order is therefore fixed and short: marketing locks the content, design picks one direction and
commits, the mechanism references (`poster.md`, `menu.md`) turn the
message into an observable device, and the tables measure what came out. A direction chosen after
the layout is decoration. A layout chosen before the direction is a template.

## Commit to one direction

Design authority is delegated in full — decide yourself, design yourself, own the result. The
user's standing instruction (2026-08-06): "cho fable tự quyết định tự thiết kế tự chi phối." That
grant is not permission to ask better questions; it is the instruction to stop asking. Read the
brief and infer the strongest direction from product truth, audience, price position, occasion,
and energy. Then commit.

- When the user names a direction — in these words, close phrasing, or Vietnamese ("kiểu tối giản",
  "phong cách Đông Dương", "kiểu chợ", "sang trọng trầm") — that is a strong override, not a hint.
  Route straight in; do not re-ask.
- When the brief is vague, choose yourself. Do not present a style menu, do not ask the user to
  pick, and do not fall back to a generic middle because the prompt is broad. A broad brief gets
  the strongest plausible direction, fully committed.
- Do not default to the same direction every time. A phở shop, a spa, and a phone-accessories
  flash sale are three different worlds; if the last three runs chose the same direction, that is
  a selection failure, not a house style.
- One direction leads. When two neighboring moods genuinely fit, the dominant one structures the
  artifact and the second contributes at most one device. Mashing directions produces the confused
  average that reads as AI.
- The choice costs one line in the run notes — direction plus the product/audience fact that
  justifies it. "Quiet-luxury because the treatment costs 2.000.000đ and the buyer is escaping
  noise" is a decision; "editorial because it looks premium" is a costume, and `STYLE-COSTUME`
  already rejects it.

## The directions

Each block is a world, not a checklist: mood, what it is for, how type, space, color, and
composition behave inside it, and the failure it invites. Fourteen map one-to-one onto the
installed `taste-skill` pack (see interop below); four exist because Vietnamese commercial reality
has surfaces that pack has no word for.

### minimalism
Calm reduction; everything earns its place. For high-clarity landing pages, consulting, quiet
product brands. Type: one family, two weights, generous size contrast between display and body.
Space is the main material — but it must perform figure-ground or reading work, never prestige
emptiness. Color: near-monochrome plus one working accent. Composition: one axis, one focal point,
asymmetric balance. Fails as: an empty page with a centered packshot and nothing to decide.

### editorial-premium
A magazine's confidence: the story leads and the design paces it. For studios, fashion,
hospitality, story-led brands, long menus with provenance worth telling. Type: expressive serif
display against restrained sans body, dateline and caption rhythm, pull-quotes doing real work.
Space: column discipline with deliberate interruptions. Color: paper-and-ink neutrals, imagery
carries the saturation. Composition: sequence and crop tension — the reader is moved through, not
shown everything at once. Fails as: magazine styling with no hierarchy at glance distance.

### swiss-system
Rational grid, typographic clarity, institutional confidence. For systems products, portfolios,
cultural institutions, information-dense menus that must be scanned fast. Type: grotesque sans,
tight scale ladder, flush-left rag-right. Space: the grid is visible in the alignments, never
drawn. Color: functional — one signal color against neutrals. Composition: modular units, strong
horizontals, hierarchy by size and placement alone. Fails as: a grid worshipped so hard the
content has no temperature.

### brutalism
Raw, confrontational, poster-energy. For experimental brands, manifesto pages, campaign concepts
that must be un-ignorable. Type: enormous, structural, the headline is the image. Space: real
breathing room between violent elements — density without air is noise, not brutalism. Color: few,
hard, uncompromising. Composition: one deliberate collision, everything else disciplined. Fails
as: ugliness mistaken for edge, or applied to a product whose buyer wants reassurance.

### soft-brutalism
Bold structure with warm edges; playful severity. For creator tools, trend brands, culture
products, youth F&B. Type: heavy display softened by rounded terminals or off-grid placement.
Space: generous, toy-like. Color: warm saturated fields with dark outlines. Composition: sticker
and card logic, thick borders, honest shadows. Fails as: Memphis clip-art scattered over a layout
with no reading order.

### cinematic-product
The product is the protagonist and light is the story. For hardware, premium tech, launch pages,
hero dishes shot like objects of desire. Type: minimal, deferential, appears between scenes. Space:
darkness and atmosphere are the canvas. Color: one material world — the palette comes from the
product's own surfaces. Composition: dramatic scale, controlled reveal, physical light behavior
(a highlight must have a source). Fails as: generic moody gradient with a floating render and no
physics.

### dark-luxe
Moody, polished, exclusive. For nightlife, premium services, dark brand worlds, cocktail and
dinner menus. Type: refined contrast — a fine serif or a spaced-out sans in warm white on near-
black. Space: intimate, compressed, candle-lit rather than spotlit. Color: deep grounds with one
metallic or jewel accent, used like jewelry — rarely. Composition: vignette logic, the eye moves
through pools of light. Fails as: black background + gold script = luxury, which is the single
most common AI costume in the category.

### gallery-minimal
Images lead, everything else steps back; exhibition pacing. For photographers, agencies, curated
showcases, menus where the food photography is genuinely strong. Type: small, precise, caption-
like. Space: white-wall logic — each image gets a room. Color: none of its own; the imagery is the
palette. Composition: sequence, scale variation between images, one oversized moment. Fails as:
a uniform grid of same-sized images, which is a contact sheet, not a gallery.

### monochrome-modern
Black, white, and discipline; modern product clarity. For portfolios, minimal tech brands, design
products. Type: the whole identity — weight, size, and spacing do everything color would. Space:
architectural. Color: true mono, or mono plus one narrow signal. Composition: strong diagonals or
strict verticals, photography duotoned into the system. Fails as: grayscale applied to a layout
that was designed for color and lost its hierarchy in the conversion.

### premium-bento
Modular cards selling one feature each, polished motion. For modern SaaS, AI products, feature-
driven launches. Type: tight UI scale, numbers celebrated. Space: even gutters, cards breathe
identically. Color: dark or light neutral field, feature cards carry controlled accents.
Composition: varied card sizes with one hero cell; every card earns its slot with a real claim —
a bento of empty labels is card spam. Fails as: twelve identical rounded rectangles saying
"powerful", "seamless", "fast".

### quiet-luxury
Understated wealth; expensive restraint. For spas, wellness, interiors, fine hospitality, premium
services whose buyer distrusts loudness. Type: light weights, wide tracking used sparingly,
lowercase confidence. Space: unhurried — the layout never asks for attention. Color: stone, cream,
clay, moss; contrast kept low but legible. Composition: horizontal calm, materials photographed
close. Fails as: beige emptiness with no information, forgetting the buyer still needs price,
place, and a next step.

### soft
Approachable, optimistic, rounded. For consumer apps, communities, education, family F&B. Type:
friendly geometric sans, generous x-height, no sharp display. Space: cushioned, nothing touches.
Color: light grounds, 2–3 pastel-leaning brand colors with one saturated action color.
Composition: centered comfort, illustration welcome, motion gentle. Fails as: infantile — softness
without a spine of real hierarchy and real facts.

### warm-modern
Contemporary polish that refuses to feel cold. For agencies, service brands, company sites, the
default when a business just wants to look current and human. Type: humanist sans with one
personality moment (an italic, a serif accent) kept at scale. Space: comfortable rhythm, clear
sections. Color: warm neutrals under confident brand color, real photography of real people.
Composition: familiar patterns executed precisely — this direction wins on craft, not surprise.
Fails as: the generic AI landing page; warm-modern chosen by default *and* executed by default.

### street-vernacular
The energy of a Vietnamese bảng hiệu: hand-painted confidence, dense honest information, zero
minimalism. For quán vỉa hè, chợ campaigns, bún/phở/cơm shops whose truth is volume, speed, and
price — and for premium brands deliberately borrowing that honesty. Type: fat slab or brush
display, price as big as the dish name, all-caps carrying real information not decoration. Space:
full — emptiness reads as a failing shop; order comes from color blocking, not whitespace. Color:
primary reds, yellows, blues at full commitment. Composition: stacked bands, starburst allowed if
it names a real offer. Fails as: ironic pastiche looking down on the shop it dresses, or fake
weathering on a brand-new business.

### heritage-craft
Vietnamese material memory — sơn mài lacquer, woodcut, Đông Dương type, indigo and cánh kiến red —
carried by real craft, not a sepia filter. For phở and cà phê brands with actual lineage, gift
boxes, Tết campaigns, premium-traditional menus. Type: a display face with verified Vietnamese
diacritics that echoes hand-lettering or classic Sài Gòn signage; body stays modern and legible.
Space: framed, bordered, symmetric where ceremony fits. Color: lacquer black, deep reds, aged
gold, mother-of-pearl neutrals — pulled from the craft object, not from a "vintage" LUT.
Composition: emblem logic, one central motif with a functional job. Fails as: nostalgia costume on
a business with no story, or French-colonial cosplay where the heritage claimed isn't yours.

### documentary-craft
Process evidence leads: the kitchen at 5 a.m., flour on hands, the broth pot, harsh honest flash.
For craft F&B, farms, workshops, any brand whose proof is how the thing is made. Type: plain,
captional, almost administrative — the design must look like it has nothing to sell because the
evidence sells. Space: edge-to-edge photography, text in reserved strips. Color: whatever the
scene had; correction, not grading. Composition: crop tension and sequence — before/during/after
beats a hero shot. Fails as: staged mess pretending to be documentary; one AI-generated "candid"
destroys the entire claim.

### pop-market
Retail promotion done loudly and well: the discipline inside khuyến mãi. For flash sales, 11.11,
combo pushes, marketplace banners, price-led posters. Type: numbers are the heroes — the discount
and the price get the display treatment, conditions stay honestly legible. Space: compressed but
ranked; exactly one element shouts loudest. Color: high-voltage complementary pairs, signal color
reserved for the offer. Composition: diagonal energy, one product or one number as anchor,
everything pointing at the CTA. Fails as: `EQUAL-SIGNALS` — badge, price, headline, and CTA all at
maximum volume, which reads as a scam even when the offer is real.

## Selection signals

| The brief smells like | Lead with |
|---|---|
| storytelling, provenance, long copy worth reading | `editorial-premium` |
| strict clarity, dense information, fast scanning | `swiss-system` |
| pure calm, few items, confident reduction | `minimalism` |
| feature-by-feature product selling on the web | `premium-bento` |
| campaign shout, manifesto, launch stunt | `brutalism` |
| youth energy with warmth | `soft-brutalism` |
| premium object, launch reveal, hero product | `cinematic-product` |
| night, exclusivity, dark premium mood | `dark-luxe` |
| strong photography carrying the brand | `gallery-minimal` |
| design-literate audience, mono discipline | `monochrome-modern` |
| wellness, escape, expensive restraint | `quiet-luxury` |
| family, community, friendliness | `soft` |
| "just make us look good and current" | `warm-modern` |
| quán ăn thật, chợ, giá là sự thật | `street-vernacular` |
| lineage, Tết, craft materials, premium-traditional | `heritage-craft` |
| the making is the proof | `documentary-craft` |
| sale, số phần trăm, deadline, marketplace | `pop-market` |

## The defaults you carry

Calibration fact, not opinion: AI-generated design clusters around a few looks that appear
regardless of subject, and knowing them by name is the only defense. The three documented by
Anthropic's `frontend-design` skill: a warm cream ground (near `#F4F1EA`) with a high-contrast
serif display and a terracotta accent; a near-black ground with one acid-green or vermilion
accent; and a broadsheet layout of hairline rules, zero border-radius, and dense newspaper
columns. All three are legitimate *when chosen for a reason*. When the brief leaves an axis free,
do not spend that freedom on one of them — arriving there by default is how every AI page ends up
related. The same trap in structure: numbered markers (01/02/03), eyebrows, and dividers must
encode something true about the content — a real sequence, a real taxonomy. The Blackhole Games
page failed exactly here: principle cards numbered 01/02/03 over content that was not a sequence
and not even the product's. Ask of every structural device: what fact does it encode?

## One signature, everything else quiet

Spend the boldness in one place. Decide the single element this artifact will be remembered by —
a type treatment, a scale collision, a material, one motion moment — and keep everything around
it disciplined. The signature comes from the subject's own world: its materials, instruments,
vernacular. A bún bò menu's signature lives in the broth pot, the morning market, the plastic
stool — not in a style name. Scattered boldness reads as noise; one committed risk reads as a
point of view. And before shipping, apply the mirror rule: look at the artifact and remove one
accessory.

## Plan in tokens, critique the plan, then build

Before any rendering, write the design plan small enough to argue with: 4–6 named hex values;
type roles (a characterful display used with restraint, a complementary body, a utility face if
data needs one); the layout concept in one sentence plus a rough wireframe; and the signature
element. Then run the self-test that catches the default before it ships: *would a similar brief
have produced this same plan?* Walk a neighboring product through your head — if it lands on the
same palette and the same hero, that part of the plan is a default wearing this brief's name.
Revise it, note what changed, and only then build, deriving every color and type decision from
the revised plan.

## Refine, do not add

The second pass improves what exists; it never adds. When a draft feels unfinished, the AI
instinct is another graphic, another badge, another section — and that instinct is the failure.
Stop and ask how the existing composition becomes more cohesive: tighter alignment, one fewer
color, more committed scale, better breathing room. The craft floor is non-negotiable and boring:
nothing overlaps, nothing falls off the surface, every element has margin, and the whole thing
looks labored over by someone at the top of their field — because a reader can feel the hours
even when they cannot name them.

## External-skill findings

A 2026-08-06 review of Anthropic's public skills (`github.com/anthropics/skills`) transferred
four things into this file: the named AI-default looks and the structure-is-information rule from
`frontend-design`; the token-plan-then-critique loop from the same; and from `canvas-design` the
philosophy-before-artifact order (its "aesthetic movement manifesto" is this file's
direction-commit wearing gallery clothes) and the refine-don't-add second pass. `canvas-design`'s
own output contract — 90% visual, 10% essential text, minimal type as a visual element — suits
artistic key visuals and poster briefs; it is deliberately wrong for a menu or a price-led
promotion, where the information *is* the design. Borrow its discipline, not its text budget.

## Interop with taste-skill

When the artifact is a website or React/Next build and `~/.claude/skills/taste-skill` is installed,
the first fourteen directions map one-to-one onto its style packs: after committing here, read
`taste-skill/<style>/skill.md` for component-level depth and its `components/style-recipes.md` for
the matching patterns. The four Vietnamese directions have no pack there; this file is their
contract. When taste-skill is absent, the blocks above are sufficient to art-direct any surface —
never block on the missing pack and never claim it was read when it was not.

## What a direction never overrides

Direction is freedom of form, not freedom from truth. Every hard gate stays: locked copy renders
character-for-character (`check_locked_copy.py`), diacritics survive the display face, claims
clear `check_claims.py`, viewing distance still sizes the type (`plan_poster.py`), contrast stays
legible (`palettes.csv` as measurement), and the artifact surface carries no process language.
A direction that needs a gate broken is the wrong direction. And the focal mechanism still comes
first within the chosen world: `street-vernacular` is where the poster lives, "the price painted
larger than the dish" is what it does — a direction without a mechanism is a mood board.


---

<!-- Deep dossier merged from references/dossiers/layout-wireframe-typography.md (2026-08-06). Long-form research behind the working sections above. External facts retrieved 2026-07-29; re-check anything priced, versioned, or platform-specific. PARTIAL: ends at section 5 mid type-scale; grid-to-layout application and responsive behaviour are not written. -->

# Layout, Wireframing & Typography as a Production Discipline

Craft dossier for the `marketing-minthep` skill. Written for an AI agent that must emit concrete
layout and type specs, not admire them.

---

## 0. PROVENANCE AND EVIDENCE STATUS — READ FIRST

**This dossier was written during a total outage of web access.** Both `WebSearch` and `WebFetch`
failed on every call with `There's an issue with the selected model (cc/claude-haiku-4-5-20251001)`
— the auxiliary model those tools depend on was unavailable. I retried both tools on separate URLs
and queries; all four attempts failed identically.

**Consequence: I opened zero web sources. Nothing in this document carries the `[verified]` tag.**
The brief asked for 20+ fetched sources. I could not deliver that and I will not manufacture the
appearance of it. There are no invented URLs, no invented study titles, no invented statistics, no
invented retrieval dates anywhere below.

What I did instead: I replaced web citation with **local instrumented measurement**. This machine has
Python 3.14.6, `fontTools` 4.63.0, the Python Unicode database (UCD 17.0.0), and 507 font binaries in
`C:/Windows/Fonts`. For the two sections where real numbers matter most — Vietnamese diacritics and
type metrics — I measured the actual font binaries rather than quoting anyone. That data is stronger
than a citation: it is reproducible on any machine in seconds, and the reproduction scripts are in
§12.

### Tag vocabulary used in this file

| Tag | Meaning |
|---|---|
| `[measured-local]` | I computed this from font binaries or the Unicode database on this machine. Reproduction command given in §12. Trustworthy and re-checkable; **not** a literature claim. |
| `[derived]` | Pure arithmetic, geometry or optics. Derivation shown inline so you can re-check by hand. Needs no citation. |
| `[recall-unverified]` | Stated from my training knowledge. **No page was fetched.** Treat as weaker than search-level. The named work probably exists and probably says roughly this, but the specific figure, sample size or wording is NOT confirmed. Must be opened before any client-facing use. |
| `[illustrative]` | A number I invented to make arithmetic followable. Never publishable. |
| `[UNVERIFIED - x]` | A named gap: what is missing and what would close it. |
| `[craft-convention]` | Studio practice with no empirical backing claimed. Defensible as convention, not as evidence. |

Where I give a `[recall-unverified]` figure I deliberately give a **range** rather than a false-precision
point value, because my recall of exact effect sizes is not reliable enough to publish.

**Standing instruction to the agent using this file:** you may act on `[measured-local]`, `[derived]`
and `[craft-convention]` immediately. You may **not** put a `[recall-unverified]` figure into a client
deliverable, pitch deck, or public claim without opening the source first. Say "research suggests"
and give the range, or say nothing.

---

## 1. WIREFRAMING: WHAT IT IS FOR

A wireframe is not a cheap drawing of a design. It is a **decision instrument**. Its value is that it
forces a specific, small set of decisions to be made and defended while they are still cheap to
reverse, and explicitly refuses to make the rest.

The failure mode in practice is not "bad wireframes" — it is wireframes that decide the wrong tier.
A wireframe that specifies a drop shadow but has not decided what the page is *for* has inverted its
job and will cost more than it saved.

### 1.1 The decide/defer contract

| Wireframe MUST decide | Wireframe MUST defer |
|---|---|
| The **one job** of the artefact, in one sentence | Typeface choice |
| Content inventory: every block that exists, named | Exact colour values |
| **Reading order** — the numbered sequence you intend | Photography / illustration selection |
| Hierarchy **rank** of each block (1..n, ties allowed) | Corner radii, shadows, borders |
| Block **proportions** and approximate area share | Icon style |
| The **primary action** and its position | Micro-copy polish |
| Responsive **reflow rule** per block (stack / hide / truncate / resize) | Animation and transitions |
| Real **content extremes** (longest plausible string, empty state) | Final image crops |
| What is **above the fold** at the target viewport | Exact type sizes (scale *step* is enough) |
| Every **state** a block can be in (loading, empty, error, overflow) | Letterspacing values |

**The decisive test for "is this a wireframe decision?"**: if getting it wrong forces the *structure*
to change, it belongs in the wireframe. If getting it wrong only forces a *value* to change, defer it.
Typeface is deferred because swapping Inter for Söhne does not move blocks. Measure (characters per
line) is **not** deferred, because it determines column count, which is structure.

### 1.2 Fidelity ladder — pick a rung deliberately

| Rung | Notation | Decides | Time cost | Use when |
|---|---|---|---|---|
| 0 | Prose outline, ordered list | Content inventory, reading order | minutes | Always. Skipping this is the most common error. |
| 1 | Block diagram, grey boxes, no type | + proportion, hierarchy rank, fold | ~15 min | Structural argument with a stakeholder |
| 2 | Greybox + real headline strings + real longest strings | + does the copy physically fit | ~45 min | Before any visual design starts |
| 3 | Type-set greybox: real scale steps, real measure, placeholder greys only | + line counts, vertical rhythm, spacing tokens | ~2 h | Handoff to design or to a generator |
| 4 | Visual comp | everything | hours–days | Not a wireframe. Do not call it one. |

**Rule:** never skip from rung 0 to rung 4. The specific damage is that rung-2 information (does the
Vietnamese headline actually fit on two lines?) gets discovered after colour and imagery are locked,
so the fix comes out of the type instead of the layout, and the type loses.

### 1.3 The content-extremes protocol

Wireframe with the strings that break it, not the strings that flatter it. For every text block,
specify three:

1. **Shortest realistic** — tests whether the block collapses or looks empty.
2. **Typical** — the median case.
3. **Longest plausible** — the p95 case. Not a hypothetical maximum; a real one from the data.

For VI/EN bilingual work this is non-negotiable and asymmetric. Vietnamese running text is
**generally shorter than English for equivalent meaning** — Vietnamese is analytic and monosyllabic,
so it avoids English's polysyllabic derivational morphology — but Vietnamese **formal/institutional**
phrasing frequently runs longer, and Vietnamese has far more inter-word spaces per unit of meaning
(every syllable is space-separated), which changes wrapping behaviour substantially.

`[UNVERIFIED - I do not have a measured VI/EN expansion-ratio corpus. Closing this needs a parallel corpus (e.g. aligned VI/EN product copy from a real client, or an open aligned corpus) measured for character count and word count per segment. Do not use a numeric expansion factor until then.]`

**Operational workaround that needs no corpus:** design the block to survive **±35% character count**
in either direction and specify the reflow rule. This is a `[craft-convention]` safety margin, not a
measurement, and it is cheaper than the research.

The wrapping asymmetry is real and derivable, though:

```
"Bánh mì thịt nướng đặc biệt"     = 27 chars, 5 spaces  -> 6 wrap opportunities
"Special grilled pork banh mi"    = 28 chars, 4 spaces  -> 5 wrap opportunities
```

`[derived]` Vietnamese offers more break points per unit length, so it **rag-wraps more evenly and
overflows fixed-width boxes less catastrophically** than English, which strands long words. The
practical consequence: Vietnamese tolerates *narrower* columns than English at the same size. This
partly offsets the extra line-height Vietnamese demands (§8.5) — you can buy vertical space back by
narrowing the measure.

### 1.4 Reading-order declaration

The wireframe must state the intended order as an explicit numbered list, because that list is the
**testable claim** the design either satisfies or fails:

```
1  Category label      (orientation: "where am I")
2  Headline            (the offer)
3  Hero image          (evidence / desire)
4  Price + unit        (the qualifier)
5  Primary CTA         (the action)
6  Proof line          (risk reduction)
7  Secondary links     (escape hatches)
```

Then verify with the squint test (§6.4). If squinting produces a different order, the hierarchy is
wrong — not the reader.

---

## 2. SPACING SYSTEMS: WHY 4 AND 8, WITH THE ARITHMETIC

The "8pt grid" is usually justified by hand-waving about "consistency." The actual justification is
integer device pixels across display scale factors, and it is checkable arithmetic.

### 2.1 The scale-factor test `[measured-local]` `[derived]`

A spacing unit `u` is safe if `u × s` is an integer for every scale factor `s` the artefact will be
rendered at. Common factors: 1×, 1.25×, 1.5×, 1.75×, 2×, 2.5×, 3×.

```
unit      1x   1.25x    1.5x   1.75x      2x    2.5x      3x   verdict
   1    1.00    1.25    1.50    1.75    2.00    2.50    3.00   fractional at 1.25,1.5,1.75,2.5
   2    2.00    2.50    3.00    3.50    4.00    5.00    6.00   fractional at 1.25,1.75
   3    3.00    3.75    4.50    5.25    6.00    7.50    9.00   fractional at 1.25,1.5,1.75,2.5
   4    4.00    5.00    6.00    7.00    8.00   10.00   12.00   ALL INTEGER
   5    5.00    6.25    7.50    8.75   10.00   12.50   15.00   fractional at 1.25,1.5,1.75,2.5
   6    6.00    7.50    9.00   10.50   12.00   15.00   18.00   fractional at 1.25,1.75
   8    8.00   10.00   12.00   14.00   16.00   20.00   24.00   ALL INTEGER
  10   10.00   12.50   15.00   17.50   20.00   25.00   30.00   fractional at 1.25,1.75
  12   12.00   15.00   18.00   21.00   24.00   30.00   36.00   ALL INTEGER
  16   16.00   20.00   24.00   28.00   32.00   40.00   48.00   ALL INTEGER
```

**Result: 4 is the smallest unit that survives all seven scale factors.** 8 also survives; so do 12
and 16. 5 and 10 — beloved of "round number" spacing systems — fail at 1.25×, 1.5× and 1.75×, which
are exactly the Windows display-scaling settings most non-designers actually run
(125% and 150% are Windows defaults on many laptops).

`[derived]` Why: 1.25 = 5/4 and 1.75 = 7/4, so `u × 1.25` is an integer iff `4 | u`. And 1.5 = 3/2
needs `2 | u`, which `4 | u` implies. So the condition is exactly **u divisible by 4**. That is the
whole theorem. Nothing about 8 is special except that it is the smallest multiple of 4 that also
gives a coarse enough ladder to prevent bikeshedding.

### 2.2 The recommended ladder

Use **8 as the default step, 4 as the permitted half-step, 2 as a hairline exception for optical
correction only.** Never odd numbers.

```
token   px    typical role
sp-0     0    flush
sp-1     4    icon-to-label, tight inline gaps, optical nudges
sp-2     8    intra-component padding, chip padding
sp-3    12    (4-step) list-item vertical, dense table cell
sp-4    16    component padding, paragraph spacing at 16px body
sp-5    24    block separation within a section
sp-6    32    sub-section separation
sp-7    48    section separation (mobile)
sp-8    64    section separation (desktop)
sp-9    96    major section / hero padding (desktop)
sp-10  128    page-level breathing (desktop wide)
```

`[derived]` Note this ladder is *approximately* geometric (ratio ~1.5) but snapped to multiples of 8
(and 4 at the bottom where absolute steps are small). That is the correct compromise: geometric
growth for perceptual evenness, integer snapping for rendering.

### 2.3 The one rule that fixes most amateur spacing

**Proximity must encode relationship.** The gap *inside* a group must be strictly smaller than the
gap *between* groups, with a clear ratio — not a subtle one.

```
label -> value        sp-1 (4)     |
value -> next label   sp-4 (16)    |  ratio 4:1  -> unambiguous grouping
```

If the inner and outer gaps are within ~1.5× of each other the grouping reads as ambiguous and the
reader must use alignment or colour instead. Target **≥2× ratio** between nesting levels
`[craft-convention]`. This single rule resolves more layout complaints than any grid.

---

## 3. COLUMNS AND GUTTERS: REAL ARITHMETIC

### 3.1 The formula

For content width `W`, `n` columns, gutter `g`, column width `c`:

```
W = n·c + (n−1)·g          ->          c = (W − (n−1)·g) / n
```

Span width for `s` adjacent columns (a span absorbs the gutters inside it):

```
span(s) = s·c + (s−1)·g
```

`[derived]` Both follow directly from counting: `n` columns have `n−1` gutters between them.

### 3.2 Computed table `[measured-local]` (generated, see §12)

`YES` in the integer column means the column width is a whole number of pixels — worth engineering
for, because fractional column widths propagate rounding error into every nested element.

```
     W  cols   gut     col w  integer?  span 1 / 2 / 3 / 4 / 6 / 12
  1440    12    24    98.000     YES    98.0 / 220.0 / 342.0 / 464.0 / 708.0 / 1440.0
  1440    12    32    90.667      no    90.7 / 213.3 / 336.0 / 458.7 / 704.0 / 1440.0
  1440    12    20   101.667      no   101.7 / 223.3 / 345.0 / 466.7 / 710.0 / 1440.0
  1280    12    24    84.667      no    84.7 / 193.3 / 302.0 / 410.7 / 628.0 / 1280.0
  1280    12    32    77.333      no    77.3 / 186.7 / 296.0 / 405.3 / 624.0 / 1280.0
  1200    12    24    78.000     YES    78.0 / 180.0 / 282.0 / 384.0 / 588.0 / 1200.0
  1200    12    32    70.667      no    70.7 / 173.3 / 276.0 / 378.7 / 584.0 / 1200.0
  1024    12    32    56.000     YES    56.0 / 144.0 / 232.0 / 320.0 / 496.0 / 1024.0
  1024    12    20    67.000     YES    67.0 / 154.0 / 241.0 / 328.0 / 502.0 / 1024.0
   768    12    24    42.000     YES    42.0 / 108.0 / 174.0 / 240.0 / 372.0 /  768.0
   390    12    24    10.500      no    10.5 /  45.0 /  79.5 / 114.0 / 183.0 /  390.0
   360    12    24     8.000     YES     8.0 /  40.0 /  72.0 / 104.0 / 168.0 /  360.0
```

**Readings from this table:**

- **1440 / 12 / 24 → c = 98.000 exactly.** This is why 1440 with a 24 gutter is the most common
  desktop design width in practice — it is one of the few combinations that divides cleanly.
  Verify: `98×12 = 1176`, `24×11 = 264`, `1176+264 = 1440`, which checks
- **1200 / 12 / 24 → c = 78.000 exactly.** Verify: `78×12 = 936`, `24×11 = 264`, sum `1200`, which checks
- **1280 / 12 / anything common → never integer.** `1280/12 = 106.67`. If you must use 1280, either
  drop to 10 columns (`(1280−9×24)/10 = 106.4`, still not integer) or accept subpixel columns, or
  use a 1264 content width inside 1280 (`(1264−264)/12 = 83.33`, still no). **Cleanest fix: 1272
  content width with 24 gutter → `(1272−264)/12 = 84.000` exactly.** `[derived]` Verify:
  `84×12 = 1008`, `1008+264 = 1272`, which checks
- **A 12-column grid is meaningless at 360–390px.** `c = 8.0px` at 360 is narrower than a single
  character. On mobile, use **4 columns** or no columns at all — just a single measure with padding.
  `(360 − 3×16)/4 = 78.000` exactly with a 16 gutter. `[derived]`

### 3.3 Choosing column count from content, not habit

12 is conventional because it factors as 2·2·3, giving halves, thirds, quarters and sixths. But
choose from the **content's natural divisions**:

| Need | Columns | Why |
|---|---|---|
| Halves, thirds, quarters, sixths | 12 | 12 = 2²·3 |
| Halves, quarters, eighths only | 8 or 16 | powers of 2; no thirds |
| Fifths (5-up product grids) | 10 or 20 | 12 cannot make fifths |
| Editorial single-column + sidebar | 6 | enough for 4+2 or 3+3 |
| Mobile | 4 | 12 collapses to sub-character widths |

**Deciding variable:** does the content ever need thirds *and* fifths? If yes you need 15, 30 or 60
columns, which is unmanageable — instead abandon a single grid and use per-section grids. This is
legitimate and common in editorial work.

### 3.4 Margins vs gutters

Distinct quantities; conflating them is a frequent spec bug.

- **Gutter** — between columns. Constant across breakpoints in most systems.
- **Margin** — between the grid and the viewport edge. Should *grow* with viewport.

```
viewport   margin   content W   grid
   360       16        328      4 col, 16 gut  -> c = (328−48)/4 = 70.000   [derived, checked]
   768       32        704      8 col, 24 gut  -> c = (704−168)/8 = 67.000  [derived, checked]
  1024       40        944     12 col, 24 gut  -> c = (944−264)/12 = 56.667  no
  1440       80       1280     12 col, 24 gut  -> c = (1280−264)/12 = 84.667  no
```

Note the last two fail integrality. Fix by choosing the *content width* first for cleanliness, then
deriving the margin: at 1440 viewport, pick content 1272 → margin `(1440−1272)/2 = 84`. `[derived]`
**Design the grid, then let the margin absorb the remainder.** This inverts the usual order and is
the single change that eliminates fractional columns.

### 3.5 Breakpoints

`[UNVERIFIED - I cannot confirm current Material 3 or Bootstrap 5 breakpoint values without fetching their docs, and these are versioned product facts that change. Closing this requires opening m3.material.io/foundations/layout and getbootstrap.com/docs/5.x/layout/breakpoints.]`

Do not copy a framework's breakpoints from memory (mine or anyone's). Derive them from your own
content instead, which is more defensible anyway:

**Content-derived breakpoint procedure `[craft-convention]`:**
1. Set your body measure target (§7.4). Say 66 CPL at 16px Inter ≈ 480px of text.
2. Single column + margins works up to about `480 + 2×24 = 528px`. Below that, shrink margins.
3. The first breakpoint is where a **second column of usable width** fits:
   `2×480 + gutter(32) + 2×margin(24) = 1040px`.
4. Continue: three columns needs `3×480 + 2×32 + 48 = 1552px` — wider than most screens, which is
   *why* three-column body text is rare on the web. `[derived]`
5. Add breakpoints only where a **reflow decision actually changes**. A breakpoint that changes
   nothing is dead code.

---

## 4. BASELINE GRID

### 4.1 The constraint

A baseline grid holds every line of text on a common horizontal rhythm. The requirement is that
**every line-height in the system is an integer multiple of the baseline unit**, and every vertical
spacing token is too. If one element breaks it, everything below drifts.

```
line-height = k × unit,  k ∈ ℤ⁺
spacing     = m × unit,  m ∈ ℤ⁺
```

### 4.2 Computed feasibility by unit `[measured-local]`

Target body leading 1.40–1.60. Table shows the nearest multiple of the unit at or above 1.40× and
the ratio it produces:

```
unit = 4px
  14px -> 20px (1.429)   16px -> 24px (1.500)   18px -> 28px (1.556)   20px -> 28px (1.400)
  24px -> 36px (1.500)   32px -> 48px (1.500)   40px -> 56px (1.400)   48px -> 68px (1.417)

unit = 6px
  14px -> 24px (1.714)   16px -> 24px (1.500)   18px -> 30px (1.667)   20px -> 30px (1.500)
  24px -> 36px (1.500)   32px -> 48px (1.500)   40px -> 60px (1.500)   48px -> 72px (1.500)

unit = 8px
  14px -> 24px (1.714)   16px -> 24px (1.500)   18px -> 32px (1.778)   20px -> 32px (1.600)
  24px -> 40px (1.667)   32px -> 48px (1.500)   40px -> 56px (1.400)   48px -> 72px (1.500)
```

**Decision rule:**
- **Use a 4px baseline unit.** It is the only unit above that lands inside 1.40–1.60 at *every* size
  tested. It is also the minimum unit for scale-factor safety (§2.1), so it costs nothing.
- **8px baseline fails at 14px and 18px** (1.714 and 1.778 — visibly too loose for body copy). If
  you are committed to an 8px baseline, you must **drop 14px and 18px from the type scale.** That is
  a real, specific cost, and it is why 8px-baseline systems tend to have gappy small text.
- **6px is excellent from 16px up** (1.500 at 16/20/24/32/40/48 — remarkably regular) **but bad at
  14px and 18px.** Use 6px only if your smallest size is 16px.

### 4.3 When to abandon the baseline grid

Baseline grids are expensive on the web because images, videos, embeds and user-generated content
have arbitrary heights that break the rhythm. `[craft-convention]`

**Deciding variable: does the artefact have multi-column text that must align across columns?**
- **Print, PDF, multi-column editorial → yes, hold the baseline grid.** Cross-column misalignment is
  glaringly visible.
- **Single-column web/app → no. Use a vertical-rhythm ladder instead** (all spacing from the 8/4
  token set, line-heights sane, no global baseline snap). You get 90% of the visual benefit for 10%
  of the maintenance.

A cheap middle path: snap **section starts** to the baseline grid, let content inside flow freely.

---

## 5. TYPE SCALE CONSTRUCTION

### 5.1 Modular scale mechanics

A modular scale is `size(n) = base × r^n`. Choose `base` from the body size (the size doing the most
work), and `r` from how much contrast the artefact needs. Step 0 is the base.

### 5.2 Computed scales from a 16px base `[measured-local]`

Raw values, then rounded:

```
ratio                        -1       0       1       2       3       4       5       6
1.125 major second        14.22   16.00   18.00   20.25   22.78   25.63   28.83   32.44
  rounded                    14      16      18      20      23      26      29      32
1.200 minor third         13.33   16.00   19.20   23.04   27.65   33.18   39.81   47.78
  rounded                    13      16      19      23      28      33      40      48
1.250 major third         12.80   16.00   20.00   25.00   31.25   39.06   48.83   61.04
  rounded                    13      16      20      25      31      39      49      61
1.333 perfect fourth      12.00   16.00   21.33   28.44   37.93   50.57   67.42   89.90
  rounded                    12      16      21      28      38      51      67      90
1.414 root two            11.31   16.00   22.63   32.00   45.25   64.00   90.51  128.00
  rounded                    11      16      23      32      45      64      91     128
1.500 perfect fifth       10.67   16.00   24.00   36.00   54.00   81.00  121.50  182.25
  rounded                    11      16      24      36      54      81     122     182
1.618 golden               9.89   16.00   25.89   41.89   67.78  109.67  177.44  287.11
  rounded                    10      16      26      42      68     110     177     287
```

### 5.3 Grid-alignment score `[measured-local]`

How many of steps 0..6, after rounding, are multiples of 4 and of 8:

```
ratio                  values                              on-4px   on-8px
1.125 major second     16 18 20 23 26 29 32                 3/7      2/7
1.200 minor third      16 19 23 28 33 40 48                 4/7      3/7
1.250 major third      16 20 25 31 39 49 61                 2/7      1/7
1.333 perfect fourth   16 21 28 38 51 67 90                 2/7      1/7
1.414 root two         16 23 32 45 64 91 128                4/7      4/7  <- best
1.500 perfect fifth    16 24 36 54 81 122 182               3/7      2/7
1.618 golden           16 26 42 68 110 177 287              2/7      1/7  <- worst, tied
```

**√2 = 1.41421… scores best on grid alignment**, which is not a coincidence: `√2² = 2` exactly, so
every *second* step is an exact doubling (16 → 32 → 64 → 128), and doublings of a multiple of 8 stay
multiples of 8. `[derived]` This is a genuine, checkable reason to prefer √2 for systems that must
live on an 8px grid. It is also the ISO 216 paper ratio (A4→A5 halving), so a √2 type scale and A-series
paper share a ratio — convenient for print work.

### 5.4 Choosing the ratio

| Ratio | Character | Use for |
|---|---|---|
| 1.067–1.125 | Very tight; many steps needed | Dense UI, data tables, dashboards where sizes must be distinguishable but not dramatic |
| 1.200 | Restrained | Product UI, documentation, long-form reading |
| 1.250 | Balanced default | Marketing sites with moderate hierarchy |
| 1.333 | Confident | Editorial, landing pages |
| 1.414 | Strong + grid-friendly | Anything on a strict 8px grid; print/screen dual delivery |
| 1.500 | Dramatic | Posters, hero-driven landing pages |
| 1.618 | Very dramatic, arithmetically awkward | Editorial display; see §11.3 before using |

**Deciding variable: how many distinct sizes does the artefact need, and what is the largest?**
A ratio `r` spanning from `base` to `max` in `n` steps needs `n = ln(max/base) / ln(r)`.

Worked: base 16, max 64, want ~5 steps → `r = (64/16)^(1/5) = 4^0.2 = 1.3195`. `[derived]`
So a 1.32 ratio gives exactly 5 steps from 16 to 64. Round to 1.333 and you get 16, 21, 28, 38, 51,
67 — six steps, max 67. Close enough; adjust the step count, not the ratio.

**Never use more than ~7 sizes in one artefact.** Beyond that, readers cannot perceive the rank
difference and you are paying maintenance cost for nothing. `[craft-convention]`

### 5.5 Snap the scale, then freeze it

A modular scale is a *generator*, not a constraint. Generate, round to the grid, hand-adjust the two
or three sizes that look wrong, then **freeze the list as tokens**. Do not ship the formula — ship
the numbers. Otherwise every consumer recomputes and rounds differently.

```
Recommended production scale (1.25 ratio, 16 base, snapped to 4px grid):
  xs   12      caption, legal, table dense
  sm   14      secondary body, labels
  base 16      body
  md   20      lead paragraph, large label
  lg   24      h4 / card title
  xl   32      h3
  2xl  40      h2
  3xl  56      h1 (desktop)
  4xl  72      display / hero
```
`[derived]` Every value is a multiple of 4; 16/24/32/40/56/72 are multiples of 8. Ratios between
adjacent steps: 1.167, 1.143, 1.25, 1.2, 1.333, 1.25, 1.4, 1.286 — irregular by design, because
snapping beats purity.

### 5.6 Title-fit gate

Treat line count as a production constraint, not a stylistic surprise. Use the real VI and EN
headline at the target viewport before approving the scale.

- Desktop hero: prefer 1–2 lines; 3 is the hard ceiling unless the brief is explicitly poster-led.
- Desktop section title: prefer 1–2 lines.
- Mobile hero or section title: prefer 2–3 lines; 4 requires a genuine content constraint.
- Default desktop H1 to 56px or less and section titles to 40px or less. Use the 72px display token
  only for an intentional poster composition with enough measure, never as an automatic premium cue.
- Never insert line breaks before measuring natural wrap. First rewrite, widen the measure, or step
  the type down. Force a break only when it improves both supported languages at their real widths.
- Reject a title that occupies more than roughly one third of the first viewport before its deck or
  primary action appears.

Record viewport, available measure, font size, and observed line count in the QA note. A title that
fits in Figma but wraps again in the browser has not passed.

## Creative tool interfaces

Use this reference for campaign landing pages and products that expose text-to-image or image-edit workflows.

### Interface principle

Organize the interface around creative decisions and recoverability, not around a giant prompt box. A user should always understand:

- What is being created or changed.
- Which references control identity, product, style, and composition.
- What is locked.
- What will vary.
- What the tool is doing now.
- How to compare, revise, and export without losing work.

### Text-to-image workspace

Use this durable structure:

1. **Brief rail**: purpose, audience, channel, ratio, campaign lane.
2. **Reference dock**: product, person, brand, composition, and mood inputs with visible priority.
3. **Prompt composer**: structured sections that can collapse into a raw prompt view.
4. **Constraint controls**: lock list, copy-safe area, negative constraints, fidelity level.
5. **Canvas**: large output area with generation state and direct selection.
6. **Variant strip**: labeled variants showing which axes changed.
7. **Inspector**: prompt record, seed/settings when available, dimensions, source lineage.
8. **History**: non-destructive generations, branches, favorites, and restore.
9. **Export**: channel crops, format, quality, naming, and rights note.

Do not hide essential state inside tooltips. Do not make every control a card. Use panels, rails, dividers, tabs, and spatial grouping according to task frequency.

### Image-edit workspace

Prioritize precision and before/after trust:

1. Canvas with zoom, pan, mask, and region selection.
2. Side-by-side, split, flicker, or overlay comparison.
3. Visible `Change`, `Lock`, `Match`, and `Reject` sections.
4. Layer or edit history with reversible steps.
5. Reference priority and identity/product fidelity controls.
6. Local regenerate and mask refinement.
7. Full-resolution artifact inspection.
8. Export with crop variants and metadata.

Never make a local edit trigger an unexplained full-image regeneration. Warn before an operation may alter locked identity or product details.

### Campaign planning workspace

Map the campaign system visibly:

- Brief and assumptions.
- Audience tension and message ladder.
- Concept lanes with comparison criteria.
- Asset matrix by funnel stage and channel.
- Shot list and prompt records.
- Review status, comments, and approval.
- Experiment hypotheses and results.

A useful visual relationship is `campaign -> lane -> asset -> variant -> export`. Preserve this lineage in navigation and filenames.

### Marketing landing-page craft

- Carry the ad promise into the first viewport.
- Use real imagery when the brief implies product, people, fashion, beauty, food, travel, or physical space.
- Make typography, imagery, color, and motion express one named campaign idea.
- Vary section rhythm; do not repeat icon-heading-text cards.
- Use purposeful first-load motion or none. Avoid uniform fade-on-scroll scaffolding.
- Design mobile and desktop compositions independently where the imagery requires it.
- Verify text contrast, responsive overflow, loading behavior, keyboard access, and reduced motion.

### Anti-template interface rules

Reject:

- Generic purple-blue AI gradients.
- Decorative grid backgrounds unrelated to a canvas or measurement surface.
- Glass panels everywhere.
- Huge rounded cards nested inside rounded cards.
- Identical feature-card grids.
- Gradient text, random glowing orbs, and meaningless 3D blobs.
- One tiny uppercase eyebrow above every section.
- A dark theme selected only because the product uses AI.

Choose a physical scene before choosing the theme: who uses the tool, where, under what light, during what kind of creative work. Let that scene determine density, contrast, color commitment, and motion.

### Critical states

Design and verify:

- Empty project and first generation.
- Missing or low-quality reference.
- Prompt conflict with lock list.
- Generation queue, progress, cancel, and retry.
- Partial failure or unavailable provider.
- Content or policy rejection with actionable recovery.
- No acceptable variants.
- Unsaved edits or branching conflict.
- Export mismatch, low resolution, or unsupported ratio.
- Mobile review and approval flow.
