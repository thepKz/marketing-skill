# Copywriting System

## Message hierarchy

Build copy in this order:

1. Audience tension or desired progress.
2. Specific promise.
3. Credible mechanism.
4. Proof.
5. Objection resolution.
6. Action and expectation.

Write the clearest true version before creating stylistic variants.

## Titles

The title is not step seven of this list, and writing it last is what produces a title about the work
instead of about the reader. `title-writing.md` owns it, with `data/title-devices.csv` and
`scripts/check_title.py`. Run the check across the whole set of headings rather than one line at a
time: the thing a reader registers as machine-written is repetition across a page, and that is
invisible when you reread each title on its own.

## Copy contract

Capture:

- Audience and awareness level.
- Page or asset job.
- Single message and primary proof.
- Voice traits with concrete examples.
- Terms that must be used or avoided.
- Confirmed claims and prohibited claims.
- CTA and what happens after the action.
- Character, layout, or legal constraints.

## Channel adaptation

### Landing page

- Make the first viewport agree with the traffic source.
- Pair promise with proof or mechanism early.
- Use sections to answer a decision sequence, not to fill a template.
- Keep one dominant action unless the user journey requires a real alternative.

### Social

- Lead with a relevant tension, observation, proof, or unusual specificity.
- Let the body earn the CTA.
- Match native pacing and format while preserving brand voice.

### Email

- Give each email one job.
- Make subject line and opening fulfill the same promise.
- Use plain expectation-setting for transactional or lifecycle content.
- Do not use fake `Re:` prefixes, deceptive urgency, or hidden conditions.

### Paid ads

- Keep the product, benefit, proof, and CTA understandable under fast attention.
- Create variants around one named hypothesis.
- Preserve claim consistency between ad and destination.

### SEO content

Route out to `seo-writing.md`. Three bullets sat here promising a capability the skill advertised in
its own description, which is the worst place to be thin. The unit is ten query intents in
`data/seo-intents.csv` plus `scripts/audit_seo_page.py`, which measures a draft against the intent
you name.

The first of those bullets is now a number. *Satisfy the real query before expanding into brand
narrative* changed no drafts as a sentence; the audit fails a page whose text has not carried every
head term of the query together inside the first hundred and twenty words.

## Editing pass

Run five passes:

1. **Truth**: every claim is supported.
2. **Clarity**: subject, action, and benefit are explicit.
3. **Specificity**: replace category language with mechanism, context, or proof.
4. **Voice**: wording sounds like the brand, not a copy template.
5. **Compression**: remove repetition, throat-clearing, and empty intensifiers.

Delete `revolutionary`, `seamless`, `unlock`, `elevate`, `game-changing`, and `in today's
fast-paced world` outright. No evidence can require them: they are adjectives with no test
attached, which is why every competitor can use the same line. Replace each with the thing that
earned it — `seamless` becomes the number of steps removed, `elevate` becomes the outcome that
changed, `revolutionary` becomes what was impossible before. If nothing can be named, the claim
was empty and the sentence should go, not be softened.

The exception is a phrase the brand already owns in market, where dropping it costs recognition.
That is a brand-guideline decision with a paper trail, not a judgement to make while drafting.


---

<!-- Deep dossier merged from references/dossiers/copywriting-deep.md (2026-08-06). Long-form research behind the working sections above. External facts retrieved 2026-07-29; re-check anything priced, versioned, or platform-specific.  -->

# Copywriting Deep Dossier (EN + VI)

## Scope

Practitioner-depth copywriting craft for a non-writer operator: the two diagnostic ladders (awareness, market sophistication), the message ladder, a 45-pattern headline bank, lead types, body mechanics, proof architecture, offer construction, objection structure, CTA mechanics, 10 channel templates, a 6-pass edit, anti-LLM rewriting, and a full Vietnamese-language section. Every number in a worked example is marked `[illustrative]` unless it carries a citation — the operator must replace illustrative numbers with measured ones before publishing.

Running example products used throughout: **(A) Rota** — rostering software for restaurants, 490.000₫/location/month `[illustrative]`; **(B) Serum 10% niacinamide**, 320.000₫ `[illustrative]`; **(C) Bún Bò Huế Cô Ba** — single-location F&B, Vietnamese-language copy.

---

## 1. The two ladders

Two independent diagnostics. Awareness is about **the reader's head**. Sophistication is about **the market's ear**. You must set both before writing a word. Getting one right and the other wrong is the most common cause of copy that is technically correct and commercially dead.

Both frameworks originate in Eugene Schwartz, *Breakthrough Advertising* (1966) (source: https://www.motiveinmotion.com/market-sophistication/, retrieved 2026-07-29; source: https://copyposse.com/blog/5-levels-of-market-awareness-how-to-speak-to-your-target-audience-part-1/, retrieved 2026-07-29). The book itself is the primary source; the secondary summaries above agree on the five-stage structure and on Schwartz's core position that advertising channels existing desire rather than creating it. Note: no controlled study validates the five-stage model — it is a practitioner taxonomy with 60 years of use, not an experimental finding. Treat it as a **checklist that prevents a specific class of error** (talking about the product to someone who does not yet know they have a problem), not as a law.

### 1.1 Awareness ladder — what changes at each rung

| Stage | Reader's inner sentence | Headline's job | Lead's job | Body's centre of gravity | Length band | Fatal error |
|---|---|---|---|---|---|---|
| 1 Unaware | "Nothing is wrong." | Interrupt with a situation they recognise, never the product | Dramatise the situation until they name it as a problem themselves | Cost of the status quo; 60-70% of words before the product appears | Long: 700-2,500 words | Naming the product in the headline |
| 2 Problem-aware | "This hurts. I don't know what fixes it." | Name the pain in their own words, more precisely than they can | Prove you understand the mechanics of the pain | Diagnosis → the class of solution that works, then your product | Medium-long: 400-1,200 | Jumping to features before the diagnosis lands |
| 3 Solution-aware | "I know what kind of thing fixes this. Which one?" | Name the solution category + your differentiator | Establish your **mechanism** as the reason you are the right instance | Mechanism, then proof, then comparison | Medium: 250-700 | Re-explaining the problem they already accept |
| 4 Product-aware | "I know your product. Not sure it's for me / worth it." | Lead with the offer, the proof, or the objection | Remove the last blocker | Objection resolution, guarantee, price framing, specificity of fit | Short-medium: 150-450 | Selling the problem again; generic benefit language |
| 5 Most-aware | "I want it. Give me a reason to act now." | Offer, price, deadline, or identity | Transact | Terms, logistics, real deadline | Short: 40-200 | Adding persuasion; it reads as a re-pitch and re-opens doubt |

Traffic source is a proxy for awareness when you have no better data:

| Traffic source | Default awareness assumption | Why |
|---|---|---|
| Cold paid social (interest targeting) | 1-2 | No intent signal |
| Cold outreach email / DM | 1-2 | You initiated |
| SEO informational query ("why is my roster always late") | 2 | Problem language in the query |
| SEO commercial query ("rostering software for restaurants") | 3 | Solution category in the query |
| Branded search / "rota alternative" | 3-4 | Category and names known |
| Retargeting after pricing-page view | 4 | Product known, unresolved objection |
| Cart abandon / trial-expiry / renewal | 4-5 | Decision already framed |
| Existing customer upsell | 5 | Trust already priced in |

### 1.2 One product, five awareness headlines (Product A — Rota)

| Stage | Headline | Why it fits |
|---|---|---|
| 1 Unaware | "Your Saturday was fine. Your Tuesday cost you a full-time wage." | Reader does not think rostering is the problem. Opens a gap in a number they already track (labour cost), not in a category they've never shopped. |
| 2 Problem-aware | "You rebuild next week's roster from last week's roster. That's why Saturday is always short." | Names the exact habit and links it causally to the pain. No product. |
| 3 Solution-aware | "Most rostering apps copy your last roster. Rota builds it from 18 months of your own POS covers." | Category accepted; the sentence is 100% mechanism and 100% contrast. |
| 4 Product-aware | "Paste your POS export. If your first roster takes more than 15 minutes, we build it for you." | Removes effort and risk objection; the guarantee *is* the headline. |
| 5 Most-aware | "490.000₫/location. Month-to-month. Cancel in the app." | Terms only. Nothing to re-argue. |

### 1.3 Market sophistication ladder — what changes at each rung

Sophistication asks: how many times has this market already heard a claim like yours? (source: https://nordiccopy.com/market-sophistication/, retrieved 2026-07-29)

| Level | Market state | What the headline must do | What the lead must do | The move |
|---|---|---|---|---|
| 1 Virgin | First entrant; nobody has made the claim | State the claim plainly and be first | Explain what the thing is | Be direct. "Whitens teeth." |
| 2 Copycats | 2-5 competitors making the same claim | Make the claim **bigger, faster, more specific** | Quantify | Escalate the claim: numbers, speed, degree |
| 3 Claim-exhausted | Everyone claims it; claims are discounted | Lead with the **mechanism** — the *how* nobody else has named | Prove the mechanism is real and unique | Name and own a mechanism |
| 4 Mechanism war | Competitors now claim mechanisms too | Lead with a **better/simpler/faster version of the mechanism**, or elaborate it | Show why your mechanism beats theirs on a dimension the buyer cares about | Out-engineer, don't out-shout |
| 5 Saturated | Every claim and every mechanism is discounted | Sell **identity, belonging, or the reader's own experience** | Confirm who they are; product becomes evidence of identity | Stop arguing. Reflect the reader. |

### 1.4 One product, five sophistication headlines (Product B — 10% niacinamide serum)

| Level | Headline | Note |
|---|---|---|
| 1 | "Serum that shrinks oily-skin pores." | Only credible if the market genuinely has not heard this. In 2026 skincare, nowhere is at Level 1. |
| 2 | "Visibly smaller pores in 14 days." `[illustrative — requires a real consumer-panel study before use]` | Bigger, timed claim. This is where most VN skincare copy sits, which is why it converts poorly. |
| 3 | "10% niacinamide + 1% zinc PCA — the pairing that slows oil at the gland, not just on the surface." | Mechanism named, contrast implied. |
| 4 | "Same 10% niacinamide. pH 5.6 and no alcohol, so it doesn't sting the skin barrier you're trying to fix." | Mechanism-on-mechanism. Competes on a second-order attribute. |
| 5 | "For people who have already tried six serums and read every ingredient list. It's the boring one that worked." | Identity, not claim. Uses the reader's fatigue as the hook. |

### 1.5 Cross-table — the combination decides the structure

| Awareness × Sophistication | Structure to use |
|---|---|
| Low awareness (1-2) × Low soph (1-2) | Story or problem-solution lead, plain claim, long body |
| Low awareness (1-2) × High soph (4-5) | Story lead + identity framing; mechanism arrives late; longest form |
| High awareness (3-4) × Low soph (1-2) | Offer lead, short page, price and proof |
| High awareness (3-4) × High soph (3-4) | Mechanism lead, comparison block, objection block; mid-length |
| Any × Soph 5 | Voice and identity carry it; a "better claim" will be ignored |

---

## 2. The message ladder — and why mechanism is the leverage point

Five rungs, in order. Every persuasive asset climbs all five or deliberately skips a rung because the reader has already climbed it.

| Rung | Question it answers | Failure symptom when missing |
|---|---|---|
| 1 Tension | "Why should I care right now?" | Reader agrees and leaves. Copy is "nice". |
| 2 Promise | "What specifically do I get?" | Reader can't repeat the offer back. |
| 3 **Mechanism** | "Why would that actually work?" | Reader believes the promise is *possible* but not *for them from you*. Highest-value rung, most-skipped. |
| 4 Proof | "Why should I believe you?" | Reader nods, then checks reviews elsewhere and never returns. |
| 5 Action | "What do I do, and what happens next?" | Reader intends to act later. Later never comes. |

### 2.1 Why mechanism is skipped

Three structural reasons, all fixable:

1. **The writer knows the mechanism so well it feels obvious.** The curse of knowledge deletes it.
2. **Mechanism requires a fact.** Promises can be written from imagination; mechanisms cannot. A writer without product access defaults to promise + adjectives.
3. **Mechanism feels "technical" and writers are told to write benefits.** But mechanism is what makes a benefit *believable*, and in a Level-3+ sophistication market, believability is the entire game.

### 2.2 Mechanism extraction — 6 questions that always produce one

Ask the operator these, in order. The first non-obvious answer is your mechanism.

| # | Question | What it surfaces |
|---|---|---|
| 1 | "What does the product actually do, in the order it does it?" | Process mechanism |
| 2 | "What input do you use that competitors don't have or don't use?" | Data/ingredient mechanism |
| 3 | "What step have you removed that everyone else still makes the customer do?" | Subtraction mechanism |
| 4 | "What did you have to build/buy/learn that a copycat couldn't do in a week?" | Moat mechanism |
| 5 | "When a customer says 'oh, that's clever' — what were you describing?" | Aha mechanism |
| 6 | "What is the physical or measurable reason the result happens?" | Causal mechanism |

### 2.3 Mechanism naming rules

- Name it in 2-5 words that a customer could repeat. "Demand-forecast rostering." "Cold-brew, then flash-chill." "One-pot, no-blanch broth."
- The name must contain at least one **concrete noun or verb from the real process**, never a coined abstraction ("SmartSync Technology™" is anti-mechanism — it hides the process).
- Say the mechanism, then immediately say the consequence: `mechanism → so → consequence`. "Reads 18 months of POS covers, so Saturday is staffed for 340 covers instead of last Saturday's 260."
- One mechanism per asset. Two mechanisms read as two products.

### 2.4 Worked ladder (Product A, solution-aware landing page)

| Rung | Copy |
|---|---|
| Tension | "Sunday, 9pm. The roster is due, and you're still guessing how busy Saturday will be." |
| Promise | "Next week's roster, built in under 15 minutes." |
| Mechanism | "Rota reads 18 months of covers from your POS export and staffs each section to forecast demand — not to a copy of last week." |
| Proof | "12 locations, 41.000 shifts rostered last month. Average build time 8 minutes 40 seconds, measured in-app." `[illustrative]` |
| Action | "Paste your POS export → see your first roster. No card, no setup call. Takes about 4 minutes." |

---

## 3. Headline bank — 45 patterns organised by job

How to read the table: **Pattern** is the mechanic. **Shape** is the template. **Example** uses Products A/B/C. **Don't use when** is the disqualifier — this column is the reason the bank is useful, because most bad headlines are good patterns in the wrong slot.

### 3.1 Curiosity (open a gap; must be paid off within 2 sentences)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 1 | Withheld mechanism | "The one [thing] that [outcome]" | "The one number that decides your Saturday roster" | Awareness 4-5 — they want price, not intrigue |
| 2 | Contradiction | "Why [good thing] is causing [bad thing]" | "Why your best server is the reason Fridays are short-staffed" | You can't defend the causal link in the next 60 words |
| 3 | Named-unexplained | "[Invented but real label] is costing you [amount]" | "The Tuesday ghost shift is costing you 6.000.000₫ a month" `[illustrative]` | The label has no substance behind it — coining a term you can't define is a credibility leak |
| 4 | Open loop + count | "[N] [things] that look [virtuous] and cost you [amount]" | "3 rostering habits that look efficient and cost you 11 hours a week" | Cold B2B outreach — reads as content marketing, not a business reason to reply |

### 3.2 Benefit (state the payoff)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 5 | Outcome-without-cost | "[Outcome] without [dreaded cost]" | "Full roster for next week without opening a spreadsheet" | The "without" isn't a real objection — then it's noise |
| 6 | Transformation delta | "From [before] to [after]" | "From 4 hours of rostering to 15 minutes" | You have no measured baseline. Invented deltas are the #1 fabrication risk in AI copy |
| 7 | End-state noun phrase | "[A] [noun] that [does the specific thing]" | "A roster that matches Saturday's actual covers" | Sophistication 4-5 — too plain to register |
| 8 | Time-to-value | "[Result] on day one. No [setup pain]." | "Live roster on day one. No data migration." | Onboarding actually takes weeks — this creates a refund |

### 3.3 Problem (make the pain legible)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 9 | Name the enemy | "[Common practice] is why [pain]" | "Copy-paste rostering is why you're overstaffed Tuesday and drowning Saturday" | Awareness 1 — accusation before belief creates defensiveness |
| 10 | Cost of inaction | "Every [event] costs you [amount]" | "Every mis-staffed Saturday costs about one server's monthly wage" `[illustrative]` | You can't show the arithmetic on request |
| 11 | Symptom list | "[Symptom]. [Symptom]. [Symptom]." | "Late rosters. Angry group chat. Two people on the same section." | Enterprise buyer who needs a business frame, not a mood |
| 12 | The unfair situation | "You [did work] on your [protected time]. Again." | "You built the roster on your day off. Again." | The buyer isn't the person doing the work (economic vs. end-user mismatch) |

### 3.4 Proof (lead with evidence)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 13 | Named-customer result | "[Named customer] went from [X] to [Y]" | "A 12-location group cut roster time from 5 hours to 40 minutes" `[illustrative]` | No written permission. In the US, fabricated testimonials now carry civil penalties up to $51,744 per violation under 16 CFR Part 465 (source: https://www.goodwinlaw.com/en/insights/publications/2024/09/alerts-practices-cldr-ftc-finalizes-rule-on-consumer-reviews, retrieved 2026-07-29) |
| 14 | Volume proof | "Used to [verb] [N] [units] a [period]" | "41.000 shifts rostered last month" `[illustrative]` | The number is small enough to look worse than silence — below that threshold, use a named customer instead |
| 15 | Third-party rating | "[Score] on [platform] from [N] [role]" | "4,8 on Capterra from 212 restaurant operators" `[illustrative]` | Score below ~4,3 or count below ~20 — publish the count only when it helps |
| 16 | Guarantee-as-headline | "If [failure], we [remedy]" | "If your first roster takes more than 15 minutes, we build it for you" | Operations can't honour it at scale |

### 3.5 News (something changed)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 17 | Launch | "[Product] now [does thing]" | "Rota now reads your POS export directly" | Cold audience — "now" implies they knew the "before" |
| 18 | Category shift | "[Activity] just stopped being [old burden]" | "Rostering just stopped being a Sunday-night job" | Nothing actually changed — fake news framing is the fastest trust burn |
| 19 | Deadline / regulatory | "[Rule] takes effect [date]. [Consequence for you]." | "New overtime rules apply from 1 Jan. Your roster template doesn't know that." `[illustrative — verify the actual regulation and date]` | You haven't read the primary regulation |

### 3.6 Question (make them answer)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 20 | Self-diagnosis | "How [many/long] did you [action]?" | "How many hours went into next week's roster?" | A large slice of the audience would answer "none" |
| 21 | Yes-question | "Still [old behaviour]?" | "Still building rosters in Excel?" | Cold outreach — this is the single most recognisable SDR template |
| 22 | Either/or | "[Bad A] or [bad B] — which did you pick?" | "Overstaffed or short-handed — which one did you pick this week?" | Both options are strawmen |
| 23 | Permission question | "Want [outcome] before [small time marker]?" | "Want next week's roster done before your coffee goes cold?" | Enterprise B2B — reads unserious |

### 3.7 How-to (teach the path)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 24 | Plain how-to | "How to [outcome]" | "How to build a 40-person roster from POS data" | High-sophistication paid social where every ad is a how-to |
| 25 | How-to-without | "How to [outcome] without [cost]" | "How to cover Saturday without calling in favours" | The cost named isn't feared |
| 26 | How-to-in-time | "How to [outcome] in [time]" | "How to close the roster in 15 minutes, every Sunday" | The time claim isn't measured |
| 27 | How-to-for-identity | "How [small identity] [does what big identity does]" | "How single-location owners roster like a 20-store group" | The audience doesn't aspire to that identity |

### 3.8 List (promise structure)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 28 | Numbered mistakes | "[N] [mistakes] that show up in [metric]" | "7 rostering mistakes that show up on your Saturday P&L" | You only have 3 real ones. Padding to hit a round number is visible |
| 29 | Numbered assets | "[N] [templates/tools] for [audience]" | "12 roster templates for restaurants trading 7 days" | The assets are thin |
| 30 | Small-count specificity | "The [2-4] [things] that decide [outcome]" | "The 3 numbers that decide your Saturday roster" | Never — but note "odd numbers convert better" is folklore, see §4.4 |

### 3.9 Comparison (position against the alternative)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 31 | Versus incumbent behaviour | "[You] vs [current habit]: [same result], [less cost]" | "Rota vs spreadsheets: same roster, 8 minutes instead of 4 hours" | You can't be factually accurate about the alternative |
| 32 | Alternative-to | "The [competitor] alternative for [narrow segment]" | "The 7shifts alternative for single-location Vietnamese restaurants" | You're not a real substitute — high bounce, and comparative claims carry legal exposure |
| 33 | Before/after time-stamped | "[Timestamp]: [before]. Now: [after]." | "Sunday 9pm: four hours. Now: one coffee." | The before is invented |

### 3.10 Objection (lead with the blocker)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 34 | Price pre-empt | "Cheaper than [the waste it prevents]" | "Costs less than the shift you overstaffed last Saturday" | The comparison isn't arithmetically defensible |
| 35 | Complexity pre-empt | "No [setup]. No [migration]. Just [one step]." | "No setup call. No import. Paste your POS export." | Setup genuinely required |
| 36 | Trust/data pre-empt | "[Sensitive thing] never [feared outcome]" | "Your sales data never leaves Vietnam" | You can't evidence the hosting claim |
| 37 | Switching-cost pre-empt | "Keep your [existing thing]. [Product] [works with it]." | "Keep your Excel. Rota reads it." | It doesn't |

### 3.11 Identity (mirror the reader)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 38 | Direct address | "For [specific role] who [specific behaviour]" | "For owners who still do their own rostering" | The segment is too small to fill the media buy |
| 39 | In-group signal | "Built by people who [shared experience]" | "Built by people who've closed at 1am and rostered at 8am" | It isn't true — this is trivially falsifiable |
| 40 | Exclusion | "Not for [segment]" | "Not for chains with a dedicated HR team" | You need volume more than positioning |
| 41 | Aspirational identity | "[Verb] like [aspirational identity], not [current identity]" | "Roster like an operator, not a manager" | The two identities aren't distinct to the reader |

### 3.12 Specificity (the number/object does the work)

| # | Pattern | Shape | Example | Don't use when |
|---|---|---|---|---|
| 42 | Exact count | "[Verb] [N] [units] across [N] [contexts] in [time]" | "Rosters 41 staff across 3 sections in 8 minutes" | You haven't measured it |
| 43 | Named object | "Reads your [exact branded artefact]" | "Reads your KiotViet or iPOS export" | The integration is roadmap, not shipped |
| 44 | Named moment | "[Exact time], when [exact situation]" | "Sunday 9pm, when the roster is due and you're still counting" | The moment isn't universal in the segment |
| 45 | Price-in-headline | "[Price]/[unit]. [Pricing model negation]." | "490.000₫ per location. No per-seat pricing." | Price is a weakness rather than a weapon |

---

## 4. Specificity, numbers, and why AI headlines fail

### 4.1 The specificity principle

Specificity is not "add detail". It is **replacing a category word with the thing itself**. A category word is any word that would still be true if you swapped in a competitor.

Test: cover the brand name. If a competitor could publish the sentence unchanged, it is a category word and carries zero information.

| Before (category language) | After (specific) | What changed |
|---|---|---|
| "Save time on scheduling" | "Closes next week's roster in 8 minutes instead of 4 hours" | Verb → measured delta |
| "Premium ingredients" | "10% niacinamide, 1% zinc PCA, pH 5,6" | Adjective → named quantity |
| "Authentic Huế flavour" | "Broth simmered 6 hours with sả, ruốc Huế and bones from Chợ Đông Ba" | Claim → named process + named source |
| "Trusted by leading restaurants" | "Used by 12 locations in HCMC, three of them trading past 1am" | Vague authority → count + qualifier |
| "Fast delivery" | "Ordered before 15:00 → arrives same day inside Ring Road 2" | Adjective → rule with a boundary |
| "Easy to use" | "Three fields. No onboarding call. Median first-roster time 8m40s" | Judgement → observable |
| "Improve customer experience" | "Cuts the wait between order and first dish from 11 to 4 minutes" | Abstraction → two measured states |
| "Our team of experts" | "Two rostering consultants who ran a 9-store group for six years" | Puffery → biography |
| "Flexible pricing" | "Month-to-month. Cancel in the app. No annual lock-in." | Adjective → three terms |
| "Natural ingredients" | "No fragrance, no alcohol, no essential oils" | Positive vagueness → negative specificity |

**Negative specificity** is under-used and cheap: listing what is *absent* is usually verifiable, legally safer than a benefit claim, and answers an objection at the same time.

### 4.2 The specificity ladder

| Rung | Form | Example |
|---|---|---|
| 0 | Adjective | "fast" |
| 1 | Comparative | "faster than a spreadsheet" |
| 2 | Quantified | "8 minutes" |
| 3 | Quantified + baseline | "8 minutes, down from 4 hours" |
| 4 | Quantified + baseline + source | "8m40s median, measured in-app across 41.000 shifts last month" |

Rule: **never publish rung 0 or 1 in a headline for a sophistication-3+ market.** Rung 2 is the floor. Rung 4 belongs in the proof block, not the headline — it is too heavy to read at headline speed.

### 4.3 The numbers question — rules of use

| Rule | Detail |
|---|---|
| Source-in-one-clause | If you cannot name the number's source in one clause, delete the number. "Measured in-app", "from the 2026 customer survey (n=212)", "from the client's own POS export". |
| Prefer the denominator | "11 of 14 locations" beats "79% of locations" when N is small. Percentages hide small samples; fractions expose them and read as more candid. |
| No percentage under 10 | "7% faster" reads as noise. Convert to absolute time, a multiple, or drop it. |
| One number per headline | Two numbers in a headline halves the memorability of both. |
| Max three numbers per viewport | Beyond three, the reader stops verifying and starts discounting all of them. |
| Absolute beats relative for cost | "6.000.000₫ a month" beats "12% of labour cost" for an owner-operator; reverse for a CFO. |
| Time beats money for time-poor buyers | Owner-operators respond to "your Sunday evening back"; procurement responds to money. |
| Round in the promise, precise in the proof | The promise must be remembered; the proof must be believed. See §4.4. |

### 4.4 Precise vs round numbers — where practitioners disagree

Folklore says "precise numbers are always more believable". The literature is narrower than that and partly contradicts it.

**Evidence for precision:** Janiszewski & Uy (2008), *Psychological Science* 19(2), 121-127 — people adjust *less* away from a precise anchor than a round one; precise anchors are represented on a finer-grained subjective scale (source: https://journals.sagepub.com/doi/10.1111/j.1467-9280.2008.02057.x, retrieved 2026-07-29). Practical read: a precise asking price holds its ground better under negotiation.

**Evidence bounding it:** two high-powered pre-registered experiments (N=284 and N=417, German students; published 2026-06-12) found precise prices (9,87) produced the most favourable *price image* versus just-below (9,99) and round (10,00), d = 0.40-0.55 — but **neither ending reliably moved purchase intention or perceived quality**, contrary to prior literature. Round prices had the highest recall accuracy (84%, then 65% in study 2); precise prices were most under-estimated (65%, 60%). The authors explicitly caution against overstating implications because the studies used imagined purchases (source: https://www.frontiersin.org/journals/behavioral-economics/articles/10.3389/frbhe.2026.1828446/full, retrieved 2026-07-29).

**Operating rule:** precise numbers where the number must be *believed or defended* (proof blocks, quotes, negotiated prices, spec sheets). Round numbers where it must be *remembered or repeated* (headline promise, guarantee, slogan). Never claim a purchase-intent lift from price-ending tactics.

### 4.5 Four widely-repeated claims — status

| Claim | Status | Evidence |
|---|---|---|
| "Odd numbers in listicles convert better" | **Folklore.** [UNVERIFIED - needs check] | No credible published test found. To verify you would need a same-content A/B on list-count parity, powered for a <3% effect. Nobody appears to have published one. |
| "Users only read 20% of your page" | **Real but misquoted.** | NN/g: users have time to read *at most* 28% of words; 20% is more likely. Derived from Weinreich et al., *ACM Trans. Web* 2(1), 2008 — 59,573 page views, 25 instrumented users (source: https://www.nngroup.com/articles/how-little-do-users-read/, retrieved 2026-07-29). It is a time-budget finding, not a claim that length is irrelevant. |
| "You have 8 seconds — less than a goldfish" | **Myth.** | Traces to Statistics Brain via a 2015 Microsoft Canada report that never made the goldfish comparison; a BBC writer could not get the figure substantiated; Microsoft removed the report (source: https://www.linkedin.com/business/marketing/blog/content-marketing/the-great-goldfish-attention-span-myth-and-why-its-killing-cont, retrieved 2026-07-29; source: https://law.temple.edu/aer/2024/01/06/are-we-no-better-than-goldfish/, retrieved 2026-07-29). |
| "Five times as many people read the headline as the body copy" | **Real quote, no dataset.** | David Ogilvy aphorism (source: https://www.goodreads.com/quotes/191457-on-the-average-five-times-as-many-people-read-the, retrieved 2026-07-29). Use for effort allocation; never cite as a statistic. |
| "Long copy always beats short copy" (or the reverse) | **Context-dependent; no universal winner.** | CXL reports paid-search visitors converting better on short-form while organic preferred long-form, and identifies commitment level and traffic source as the moderators (source: https://cxl.com/blog/long-form-or-short-form/, retrieved 2026-07-29 — page returned 403 to direct fetch; figures taken from search-result summary and should be re-verified against the live article before quoting the percentage). |

### 4.6 Why most AI headlines fail — six diagnosable defects

| Defect | What it looks like | Detection test | Fix move |
|---|---|---|---|
| Abstraction | "Transform your workflow with intelligent scheduling" | Cover the brand name: still true for 5 competitors → fail | Force rung 2+ on the specificity ladder; demand a number or a named object |
| Symmetry | "Save time. Cut costs. Grow faster." — three clauses, near-equal length, same grammar | Count syllables per clause; all within ±2 → fail | Break the third clause: make it a fragment, a number, or a question |
| Adjective stacking | "Powerful, intuitive, all-in-one rostering platform" | ≥2 evaluative adjectives before the noun → fail | Delete every adjective; add back at most one, only if measurable |
| Benefit without mechanism | "Get your Sundays back" with no *how* in the fold | Search the first viewport for a process noun or verb → absent → fail | Insert `mechanism → so → consequence` |
| Invented quantification | "Save up to 80% of admin time", no source | Ask "measured where?" → no answer → fail | Replace with a measured number or a bounded qualitative claim |
| Category reflex | Converges to the category's default sentence | Generate 3 competitor headlines from the category alone; if yours is in the set → fail | Swap the category cue for a mechanism, a named object, or a named moment |

---

## 5. Lead types and the first sentence

The lead is the first 30-120 words after the headline. Its only job is to buy the *next* 100 words.

### 5.1 Six lead types, mapped to awareness

| Lead type | Opens with | Best awareness | Best sophistication | First-sentence shape | Risk |
|---|---|---|---|---|---|
| Offer | The deal, price, terms | 4-5 | Any | "490.000₫ a month, month-to-month, cancel in the app." | Reads cheap if the category isn't accepted yet |
| Promise | The outcome | 3-4 | 1-2 | "Next week's roster, done before your coffee goes cold." | Indistinguishable from competitors at soph 3+ |
| Problem-solution | The pain, then the pivot | 2-3 | 2-3 | "You rebuild the roster from last week's roster." | Reads accusatory if the problem isn't admitted |
| Big secret | A withheld mechanism or fact | 2-3 | 3-4 | "One number in your POS predicts Saturday better than your memory does." | Must pay off in ≤2 sentences or it is clickbait |
| Proclamation | A claim about the world or category | 1-2 | 4-5 | "Rostering software has been solving the wrong problem for ten years." | Needs authority or proof immediately behind it |
| Story | A specific scene with a person and a time | 1-2 | 4-5 | "It's 21:40 on a Sunday and Hạnh is on her fourth version of the roster." | Longest runway; wasted on awareness 4-5 |

### 5.2 The first sentence — hard rules

| Rule | Threshold |
|---|---|
| Length | ≤ 12 words (EN) / ≤ 16 syllables (VI) |
| No throat-clearing | Ban: "In today's…", "As a business owner, you know…", "We're excited to…", "Let's face it…", "In an era where…" |
| One concrete noun the reader can picture | A spreadsheet, a group chat, a POS export, 21:40 on a Sunday |
| Does not restate the headline | If headline and first sentence share their main verb, rewrite one |
| Ends with forward pressure | Should feel unfinished as an *idea*, not as grammar |

### 5.3 The lead's structural obligation

By the end of the lead, the reader must be able to answer: *who is this for, what is on offer, and why is this page different from the last one I closed?* A lead that cannot pass that three-question test out loud is decoration.

---

## 6. Body-copy mechanics

### 6.1 One idea per sentence

A sentence contains one idea when removing any clause destroys the meaning. Test: try to split at every "and", "which", "that", comma and dash. If a split produces two sentences that each stand alone, it was two ideas.

| Two ideas (before) | One idea each (after) |
|---|---|
| "Rota reads your POS export and builds a roster that matches forecast demand, which means you don't have to guess how busy Saturday will be." | "Rota reads your POS export. It staffs each section to forecast demand. You stop guessing about Saturday." |

The `X, which is Y, which means Z` chain is the most common LLM tell. Split it, or replace with a dash.

### 6.2 Rhythm and burstiness — numeric calibration targets

Craft calibration targets, not measured findings. They exist because LLM prose defaults to uniform sentence length, and uniformity is the strongest human-detectable AI signal.

| Metric | Target | Why |
|---|---|---|
| Mean sentence length | 12-18 words (EN); 14-22 syllables (VI) | Above 20 mean, mobile comprehension drops |
| Longest ÷ shortest sentence | ≥ 3.0 | Below 2.0 reads machine-flat |
| Sentence-length coefficient of variation (SD ÷ mean) | ≥ 0.45 | Direct burstiness measure |
| Sentences ≤ 4 words | ≥ 1 per 150 words | Provides the landing beats |
| Consecutive sentences within ±2 words of each other | ≤ 2 | Three in a row is audible as a pattern |
| Consecutive sentences starting with the same word | ≤ 2 | Anaphora is a device, not a default |
| Paragraph length | 1-4 sentences; ≥1 single-sentence paragraph per 250 words | Whitespace carries emphasis on mobile |
| Tricolons (three parallel items) | ≤ 1 per 400 words | See §11 |
| Em dashes | ≤ 1 per 150 words | See §11 |
| Passive constructions | ≤ 5% of sentences | Except the three exceptions in §6.5 |

### 6.3 The slippery slide — transitions that actually pull

Weak transitions summarise. Strong transitions **create an unanswered question** the next block answers.

| Type | Device | Example |
|---|---|---|
| Unanswered question | End a block with the question the next answers | "So which 18 months? The ones you already have." |
| Objection voiced | Say the reader's next thought out loud | "Which sounds like more work, not less. It isn't." |
| Numeric handoff | End with a number; open with what it means | "…8 minutes 40 seconds. That number is the whole product." |
| Contrast pivot | Concede, then turn | "That's the part everyone gets right. Here's the part nobody does." |
| Promise of the next block | Preview the count | "Two things happen after you paste the file." |
| Time cue | Put a clock on it | "By Tuesday you'll know if it worked." |
| Single-word bridge | Own paragraph | "Except." / "Then." / "Almost." |

Delete on sight: `Furthermore`, `Additionally`, `Moreover`, `In conclusion`, `That said`, `It's worth noting`, `Ultimately`, `At the end of the day`.

### 6.4 Concrete-over-abstract substitution table

| Abstract (delete) | Concrete replacement |
|---|---|
| efficiency | "8 minutes instead of 4 hours" |
| visibility | "next Saturday's cover forecast sits on the roster screen" |
| scalability | "works the same at 3 locations as at 30" |
| optimisation | "removes the 6 shifts you didn't need" |
| solutions | the actual thing: "software", "the broth", "the sleeve" |
| experience | the observable moment: "the wait between ordering and the first dish" |
| innovation | the mechanism |
| quality | the spec |
| synergy | delete; no replacement exists |
| empowerment | "change the roster from your phone at 23:00 without calling anyone" |
| leverage (verb) / utilise | "use" |
| facilitate | "let" / "make it possible to" |
| robust | "hasn't gone down since March" `[illustrative]` |
| seamless | "no export/import step" |
| comprehensive | list the actual items |
| streamline | name the step you removed |
| elevate / unlock / transform | delete; state the before and the after |

### 6.5 Active voice — three legitimate exceptions

(1) The actor is genuinely unknown ("the file was corrupted"). (2) The object is the topic and should lead ("your data is encrypted at rest"). (3) You are deliberately de-emphasising blame in a neutral incident note ("orders were delayed") — but never to hide agency you should own. If you caused it, write "we delayed".

### 6.6 Where the reader's silent objections occur

Objections arrive in a predictable order as the eye travels. Answer them *at* the objection, not in a bottom-of-page FAQ.

| Position in the read | Silent objection | Where the answer belongs |
|---|---|---|
| Headline | "Is this for me?" | Subhead: name the segment |
| Right after the promise | "That can't be true." | First proof element, inside the first viewport |
| First scroll | "How does it work?" | Mechanism block — the #1 drop-off point |
| Mid-page | "Who else uses this?" | Customer evidence with a name or a count |
| At the price | "Compared to what?" | Price framed against the cost of the status quo, adjacent to the number |
| At the form or button | "What happens after I click?" | Microcopy under the button |
| Final block | "What if it doesn't work?" | Guarantee + exit terms |
| After the final CTA | "I'll do it later." | A real deadline, or a lower-commitment alternative action |

### 6.7 Proof placement rules

- **One proof element inside the first viewport.** NN/g eye-tracking (2018; 120 participants; 1920×1080; >130,000 fixations) found 57% of page-viewing time above the fold, 17% on the second screenful, 26% across the remainder — 74% within the first two screenfuls, up to 2160px. The comparable 2010 study on 1024×768 monitors found 80% above the fold (source: https://www.nngroup.com/articles/scrolling-and-attention/, retrieved 2026-07-29). Proof placed at 3,000px is proof nobody reads.
- Pair each claim with its proof **within two sentences**. A testimonial wall proves you have customers; a testimonial next to a claim proves the claim.
- Never stack more than 3 proof elements consecutively — stacks read as compensation.
- Put the strongest proof against the *least-believed* claim, not against the headline.
- On product pages, answer the questions the images raise: Baymard found 56% of test subjects' first action on a new product page was exploring the images, before titles or descriptions, and that 10% of the largest e-commerce sites have descriptions insufficient for users' needs — the recurring gaps being materials/ingredients, dimensions with units, and compatibility (source: https://baymard.com/blog/product-descriptions, published 2021-03-09, retrieved 2026-07-29; source: https://baymard.com/blog/product-images-descriptive-text, retrieved 2026-07-29).

---

## 7. Proof architecture

### 7.1 The hierarchy — strongest to weakest

Ordered by how much doubt each unit removes per word spent.

| Rank | Tier | Form | Why it ranks here | Cost to produce |
|---|---|---|---|---|
| 1 | **Demonstration** | Video/GIF of the thing working, unedited, in real time; live sandbox; "paste your own data and watch" | Removes belief from the equation entirely — the reader verifies | Low-medium |
| 2 | **Product evidence** | Screenshots with real data, spec sheets, ingredient lists with percentages, dimensions, teardown photos, before/after of the artefact | Verifiable, no third party needed | Low |
| 3 | **Customer evidence** | Named case with a number, review screenshots, photos taken by customers, quantified testimonial, logo wall with role labels | Social + specific; the strongest *persuasive* tier but requires permission and carries legal duty | Medium |
| 4 | **Expert / institutional evidence** | Lab report, certification, licence number, named practitioner endorsement, standards compliance | Transfers authority; weak if the institution is unknown to the buyer | Medium-high |
| 5 | **Data / research** | Your own measured dataset, a published study with n and method | Strong with sophisticated buyers, ignored by impulse buyers | High |
| 6 | **Process transparency** | "Here is exactly what we do, in order"; kitchen cam; changelog; open pricing; published SLA and incident history | Substitutes for social proof when you have none — see §7.3 | Low |
| 7 | **Borrowed proxy** | Category statistics, "as seen in", founder's prior track record, ingredient supplier's reputation | Weakest; must be labelled honestly as proxy, never implied as your own result | Low |

Rules:
- **One tier-1 or tier-2 element must appear above the fold.** Tiers 3-7 can live below.
- A claim's proof must be **at least one tier stronger than the claim is surprising.** A mundane claim needs tier 6; an extraordinary claim needs tier 1 or 2.
- Never present tier 7 in the visual position of tier 3 (e.g. a "featured in" logo bar styled like a customer logo bar). That is the most common inadvertent deception on new-business sites.

### 7.2 Testimonial quality rubric — score before publishing

| Attribute | 0 points | 1 point | 2 points |
|---|---|---|---|
| Attribution | Anonymous / initials | First name + role | Full name, role, company, photo |
| Specificity | "Great product!" | Names the benefit | Names a number and a timeframe |
| Objection coverage | None | Mentions a doubt | Names the doubt they had *and* how it resolved |
| Verifiability | Text only | Screenshot of the source | Link to the public source |

Publish nothing scoring below 4/8. A single 8/8 testimonial outperforms six 2/8 testimonials.

### 7.3 The substitution rule — proof when you have no customers yet

This is the real problem for a new business, and the correct answer is **not** to fabricate. Rank order of substitutes:

| Substitute | How it works | Example (Product C, a new bún bò shop) |
|---|---|---|
| 1. Demonstration | Show the thing working in full, uncut | 40-second single-take video of the broth being strained at 05:40 |
| 2. Process transparency | Publish the method in a level of detail a competitor wouldn't bother with | "6 hours, 14kg bones, sả and ruốc Huế from Chợ Đông Ba, no bột ngọt. Photographed every morning." |
| 3. Provenance | Name suppliers, origins, batch dates | Supplier name and market stall number |
| 4. The founder's own credential | Biography as evidence, stated plainly | "Cô Ba cooked this in Huế for 22 years before opening here." `[illustrative]` |
| 5. Falsifiable guarantee | A promise you'd lose money on if the product were bad | "First bowl: if you don't finish it, you don't pay." |
| 6. Radical specificity | Detail so precise that inventing it would be irrational | "Bowl weight 620g. 95g beef shank. Broth at 82°C when it leaves the pass." `[illustrative]` |
| 7. Public commitment | Publish something checkable that you'd be embarrassed to get wrong | Daily photo of the pot; a public changelog; posted prices that never change |
| 8. Third-party comparison you invite | "Try it next to the bún bò you already like. Tell us which." | Frames the reader as judge, which is itself credibility |
| 9. Pilot / limited cohort framing | Convert absence of proof into a reason to act | "First 20 customers. We want to be corrected early." |
| 10. Borrowed proxy (labelled) | Only with explicit labelling | "We use the same broth method taught at [X]. That's their reputation, not ours yet." |

**Prohibited substitutes** — these create legal exposure, not just risk of embarrassment:
- Writing your own reviews, or having staff/family write undisclosed reviews.
- AI-generated testimonials or fabricated customer photos.
- Buying followers, likes or views.
- Company-controlled "review site" presented as independent.
- Suppressing or threatening over negative reviews.

In the US these are now specifically prohibited by rule, not just by guidance: 16 CFR Part 465 (effective 2024-10-21) covers fake/false reviews and testimonials incl. AI-generated (§465.2), compensated-for-sentiment reviews (§465.4), undisclosed insider reviews (§465.5), company-controlled review sites (§465.6), review suppression (§465.7) and fake social-media indicators (§465.8), with civil penalties up to **$51,744 per violation** (source: https://www.goodwinlaw.com/en/insights/publications/2024/09/alerts-practices-cldr-ftc-finalizes-rule-on-consumer-reviews, retrieved 2026-07-29; rule text index: https://www.ftc.gov/legal-library/browse/federal-register-notices/16-cfr-part-465-trade-regulation-rule-use-consumer-reviews-testimonials-final-rule). Note the penalty amount is inflation-adjusted annually — re-verify the current figure before citing it in client-facing material.

In Vietnam, providing inaccurate, incomplete or misleading information about goods, services, or the seller's reputation and capability is prohibited under the Law on Protection of Consumer Rights No. 19/2023/QH15 (passed 2023-06-20, effective 2024-07-01) (source: https://thuvienphapluat.vn/van-ban/Thuong-mai/Luat-Bao-ve-quyen-loi-nguoi-tieu-dung-2023-19-2023-QH15-500102.aspx, retrieved 2026-07-29; official gazette: https://congbao.chinhphu.vn/van-ban/luat-so-19-2023-qh15-39843.htm). Exact article numbering should be confirmed against the gazette text before it goes into a legal review note.

---

## 8. Offer construction

Copy cannot fix a weak offer. Diagnose the offer first; if the value equation is negative, rewriting the headline is wasted work.

### 8.1 The value equation and its four levers

Alex Hormozi, *$100M Offers*: **Value = (Dream Outcome × Perceived Likelihood of Achievement) ÷ (Time Delay × Effort & Sacrifice)** (source: https://www.beltcourse.com/blog/summary-of-100m-offers-how-to-make-offers-so-good-people-feel-stupid-saying-no-by-alex-hormozi, retrieved 2026-07-29; source: https://maccelerator.la/en/blog/news-2/100m-offers-by-alex-hormozi-a-blueprint-for-startup-success/, retrieved 2026-07-29). It is a heuristic, not a measured model — there is no published validation. Its value is as a **four-lever checklist**: any offer that feels weak is weak on at least one of the four, and naming which one tells you what to write.

| Lever | Direction | Copy moves that actually move it | Anti-pattern |
|---|---|---|---|
| Dream outcome | ↑ | Raise the *altitude* of the outcome one level (not "a roster" → "your Sunday evening"); attach it to a status or identity the buyer already wants; name the second-order consequence | Inflating the claim without changing what's delivered. This raises refunds, not value |
| Perceived likelihood | ↑ | Mechanism (the single biggest mover); proof at the point of doubt; guarantee; "people like you" specificity; showing the failure mode you've already handled | Superlatives. They *lower* perceived likelihood in soph 3+ markets |
| Time delay | ↓ | Name a fast first win separate from the full outcome ("first roster in 8 minutes; full forecast accuracy after 2 weeks of data"); done-for-you onboarding; instant access to one component | Hiding a genuinely long time-to-value. It surfaces as churn |
| Effort & sacrifice | ↓ | Remove steps and say which ones you removed; do the work for them; default settings; accept their existing format; count the fields ("three fields"); name what they *don't* have to give up | "Easy to use" as an adjective. Effort reduction must be enumerated to be believed |

**Which lever to pull, by symptom:**

| Buyer's objection sounds like | Weak lever | Write this |
|---|---|---|
| "I don't really need this" | Dream outcome | Raise altitude; quantify the cost of the status quo |
| "It won't work for me / for my business" | Perceived likelihood | Mechanism + segment-specific proof + guarantee |
| "Not right now" | Time delay | A first win inside 24 hours, named |
| "It looks like a lot of work / we'd have to change everything" | Effort & sacrifice | Enumerate removed steps; accept their existing artefacts |
| "It's too expensive" | Usually **not** price — it is one of the four above | Diagnose before discounting |

### 8.2 Offer anatomy — seven components

| Component | Job | Rule | Example (Product A) |
|---|---|---|---|
| Core | The thing being bought | One sentence, no adjectives | "Rostering for restaurants, per location, month-to-month." |
| Bonuses | Remove a specific blocker, not "add value" | Each bonus must map to a named objection; ≤3; each must have a standalone price | "We import your last 18 months of POS data for you (normally 2.000.000₫)." `[illustrative]` |
| Guarantee | Transfer risk from buyer to seller | Must be specific, time-bound, and operationally honourable | "First roster in 15 minutes or we build it." |
| Scarcity / urgency | Compress the decision | Must be **structurally true** — see §8.4 | "Onboarding cohorts of 10 per month because a human does the import." |
| Naming | Make the offer repeatable | Name the *offer*, not the product; 2-4 words; contains a noun the buyer uses | "The First Roster Setup" |
| Price presentation | Make the number feel proportionate | Anchor against the cost it removes, in the buyer's own unit | "490.000₫/month — less than two hours of a manager's time." `[illustrative]` |
| Terms / next step | Remove ambiguity | State billing cadence, cancellation, what happens on day 1 | "Billed monthly. Cancel in the app. Nothing auto-renews annually." |

### 8.3 Risk reversal by business model

| Model | Best risk reversal | Second choice | Avoid |
|---|---|---|---|
| SaaS, self-serve | Free trial with no card, full feature access, and a named first-win | Month-to-month with in-app cancel | 14-day trial that requires a card and a sales call |
| SaaS, sales-led | Paid pilot with written success criteria and a documented exit | Migration done-for-you at your cost | "Annual contract, 30-day out" — reads as no guarantee at all |
| Physical DTC | Free returns with a prepaid label, 30+ days | "Keep the first unit" on multi-packs | Restocking fees; return shipping paid by buyer |
| Beauty / skincare | Sample or trial size at cost + full-size credit if they continue | Empty-bottle return window (30-60 days) | Results guarantees — regulated claim territory |
| Services / agency | Milestone kill-fee: stop after phase 1, pay only phase 1 | Capped scope with a written change process | Performance-only pricing unless you control the variables |
| Course / info | 14-day no-questions refund | Completion-conditional refund (must submit the work) | "No refunds" — kills conversion more than it saves margin |
| F&B dine-in | Remake it free, no questions, on the spot | First-visit price on one signature dish | Cash refunds (operationally awkward, invites abuse) |
| F&B delivery | Replace or refund on a photo | Credit for next order | Requiring the food to be returned |
| Marketplace | Escrow + a defined buyer-protection window | Verified-seller badge with real criteria | Vague "buyer protection" with undisclosed exclusions |
| Local trades | Fixed written quote; no-fix-no-fee | Warranty with a stated duration and what voids it | Hourly with no cap |
| High-ticket B2B | Proof-of-concept with success criteria agreed in writing before the PO | Reference call with a customer in the same segment | Discount-as-risk-reversal — it signals the product is the risk |

### 8.4 Real vs fabricated scarcity — the hard line

**Structurally true scarcity** derives from a constraint that exists whether or not you are marketing: physical stock, a fixed number of seats, a service capacity ceiling, a supplier batch, a date fixed by something outside your control (a season, an event, a regulation, a class start).

**Fabricated scarcity** is any deadline, count, or counter that resets, does not bind, or was invented for the campaign.

| Device | Real when | Fabricated when | Exposure |
|---|---|---|---|
| Countdown timer | The offer genuinely ends at that timestamp and does not return unchanged | Timer resets on reload, or the price is the same next week | FTC's 2022 staff report *Bringing Dark Patterns to Light* names false countdown timers as a deceptive design pattern under FTC Act §5 (source: https://www.ftc.gov/reports/bringing-dark-patterns-light, retrieved 2026-07-29; press release: https://www.ftc.gov/news-events/news/press-releases/2022/09/ftc-report-shows-rise-sophisticated-dark-patterns-designed-trick-trap-consumers) |
| "Only N left" | Tied live to inventory | Hardcoded, or randomised | Same |
| "X people are viewing this" | Live and accurate | Simulated | Named in the same FTC report family of practices |
| "Enrolment closes Friday" | Cohort genuinely starts and you don't admit late | Rolling admission with a weekly "close" | Same |
| Founding-member pricing | The price genuinely rises and never comes back | Recurs every quarter | Same |
| "Limited edition" | Batch size fixed and published | Restocked identically | Same |

Additional Vietnam-specific exposure: advertising that uses "nhất", "duy nhất", "tốt nhất", "số một" or equivalent superlatives **without lawful documentary proof** is prohibited by the Advertising Law (Law 16/2012/QH13, Art. 8). Qualifying proof is limited to (a) market-survey results from a legally established market-research organisation, or (b) a certificate/award from a regional or national-scale competition or exhibition recognising the product as such. Administrative fines under Decree 38/2021/NĐ-CP are reported as 10-20 million VND for individuals and 20-40 million VND for organisations, within an overall advertising-violation ceiling of 100 million VND (individual) / 200 million VND (organisation) (source: https://thuvienphapluat.vn/van-ban/Thuong-mai/Luat-Quang-cao-2012-142541.aspx, retrieved 2026-07-29; source: https://thuvienphapluat.vn/van-ban/Thuong-mai/Nghi-dinh-38-2021-ND-CP-xu-phat-vi-pham-hanh-chinh-trong-linh-vuc-van-hoa-quang-cao-469165.aspx, retrieved 2026-07-29; official decree text: https://vanban.chinhphu.vn/?pageid=27160&docid=202962). **The specific fine figures came from a search-result summary, not a direct read of the decree article — verify the article number and current amount before relying on them.**

The Advertising Law was substantially amended by **Law 75/2025/QH15**, passed 2025-06-16, **effective 2026-01-01** (source: https://svhttdl.dongnai.gov.vn/vi/news/thong-bao/luat-sua-doi-bo-sung-mot-so-dieu-cua-luat-quang-cao-co-hieu-luc-tu-ngay-01-01-2026-180.html, retrieved 2026-07-29; source: https://thuvienphapluat.vn/phap-luat-doanh-nghiep/bai-viet/luat-quang-cao-2025-sua-doi-co-hieu-luc-tu-01-01-2026-da-duoc-thong-qua-ngay-16-6-2025-12818.html, retrieved 2026-07-29). Reported changes relevant to copy: a defined category of **"người chuyển tải sản phẩm quảng cáo"** (the person conveying the ad — i.e. influencers and anyone wearing/displaying paid promotion) with an obligation to disclose that content is advertising; a requirement that online ads be clearly identifiable as ads and dismissible; a Vietnamese-language clarity requirement; and requirements on how warnings must be displayed (contrasting colour, matching audio speed). One secondary source cites Decree 342/2025/NĐ-CP as the implementing decree for special product categories such as functional foods (source: https://tapchitoaan.vn/mot-so-diem-moi-dang-chu-y-cua-luat-quang-cao-sua-doi-bo-sung-nam-202515012.html, retrieved 2026-07-29). **That same source misstated the law number as 47/2024/QH15, so treat its article numbers and the decree number as [UNVERIFIED - needs check] against the gazette.**

---

## 9. Objection handling as copy structure

### 9.1 The three-move pattern

Every objection gets the same three moves, in this order. Skipping the first move is why most FAQ sections fail — they answer objections the reader hasn't been given permission to have.

| Move | What it does | Shape | Failure if skipped |
|---|---|---|---|
| 1 Surface | Say the objection in the reader's words, before they finish forming it | "You're thinking: we'd have to re-enter every shift." | The answer sounds defensive and the reader doesn't recognise it as their own concern |
| 2 Reframe | Change the frame so the objection becomes irrelevant or becomes a reason to buy | "You don't. Rota reads the file you already export every month." | The objection is only *contradicted*, which triggers argument |
| 3 Prove | Attach the smallest sufficient proof | "Here's the import running on a real KiotViet export — 22 seconds, unedited." | Reframe reads as assertion |

Never do move 2 without move 1. Never do move 1 without move 3.

### 9.2 Common objection sets by business type

Handle in this order; the ranking is by how often the objection is *decisive* rather than how often it is voiced.

| Business type | #1 decisive objection | #2 | #3 | #4 | Where each is answered |
|---|---|---|---|---|---|
| B2B SaaS, self-serve | "Switching cost / migration" | "Will my team actually use it" | "Price vs. current spreadsheet (free)" | "Data security" | Migration → mechanism block; adoption → onboarding block; price → cost-of-status-quo; security → footer + a real page |
| B2B SaaS, enterprise | "Procurement, security review, SLA" | "Integration with our stack" | "Vendor viability" | "Internal champion risk" | Trust centre; integration list with named systems; funding/customer count; a one-page internal business case they can forward |
| Physical DTC | "Will it fit / will it match the photo" | "Return hassle" | "Delivery time and cost" | "Is this the real brand" | Sizing + in-scale image (Baymard: 28% of sites provide no in-scale image, and size misinterpretation caused abandonment — source: https://baymard.com/blog/in-scale-product-images, retrieved 2026-07-29); returns policy at the buy button; delivery estimate above the fold |
| Beauty / skincare | "Will it break me out / irritate me" | "Is it authentic (counterfeit fear)" | "Will it work on my skin type" | "Price vs. the one I already use" | Full INCI + "free from" list; authenticity/verification; segment-specific proof; per-use price |
| F&B dine-in | "Is it actually good" | "Is it clean" | "Price/portion" | "Wait time / parking" | Photo of the real dish and the kitchen; portion weight; posted price; a line about parking |
| F&B delivery | "Will it arrive intact and hot" | "Portion vs. photo" | "Delivery fee" | "Wrong-order risk" | Packaging shot; real-photo policy; fee stated pre-checkout; replacement guarantee |
| Services / agency | "Will I get a senior person or a junior" | "Scope creep and surprise invoices" | "Do you understand my industry" | "What if it doesn't work" | Named team with hours; fixed scope + change process; a same-industry case; kill-fee |
| Course / info | "Will I actually finish it" | "Is this just free content repackaged" | "Is the instructor credible" | "Refund" | Time budget per week; a sample lesson that is genuinely the product; instructor's verifiable track record; refund terms |
| Local trades | "Will they show up" | "Will the price change" | "Is the work guaranteed" | "Are they licensed/insured" | Booking confirmation flow; fixed quote; warranty duration; licence number |
| Marketplace / two-sided | "Is the other side real" | "What if there's a dispute" | "Fees" | "Liquidity in my area" | Verification method; dispute process with timelines; full fee table; local supply count |

### 9.3 Objection placement rule

Answer the #1 decisive objection **in the first viewport**, not in the FAQ. If your #1 objection is unanswered above the fold, the rest of the page is optimising a read that already ended.

---

## 10. CTA mechanics

### 10.1 The five rules

| Rule | Detail | Threshold |
|---|---|---|
| One primary action per view | Secondary actions must be visually subordinate and semantically different (e.g. "See pricing" vs "Start free") | Exactly 1 primary; ≤1 secondary |
| Verb specificity | The verb must name the action *and* the object received | Ban: Submit, Send, Sign Up, Learn More, Get Started, Click Here, Continue (unless in a numbered flow) |
| Friction named and reduced | State what is *not* required | e.g. "No card. No call." |
| Consequence disclosed | Say what happens immediately after the click | Microcopy under the button |
| Repetition cadence | Repeat the CTA every ~1.5 screenfuls on a long page, and always immediately after a proof block | — |

### 10.2 Button copy formula and worked variants

`[Verb] + [the specific thing received] (+ [friction remover if short enough])`

| Weak | Strong | Why |
|---|---|---|
| "Submit" | "Send my roster file" | Names the object |
| "Sign Up" | "Start free — no card" | Names the state change + removes friction |
| "Learn More" | "See the 8-minute build" | Names what they will see |
| "Get Started" | "Build my first roster" | Names the outcome, first-person |
| "Contact Us" | "Get a fixed quote in 1 working day" | Names the deliverable and the latency |
| "Download" | "Download the 12 roster templates (PDF, 1,4 MB)" | Names format and weight — removes a real hesitation |

Length: 2-5 words on mobile primary buttons. Above 5 words, the button wraps and the tap target degrades.

### 10.3 Microcopy under the button — its four jobs

In priority order. Include as many as fit in ≤12 words.

| Job | Example |
|---|---|
| 1. What happens next, immediately | "You'll see your roster on the next screen." |
| 2. What you will *not* do | "No card. No sales call." |
| 3. How long it takes | "About 4 minutes." |
| 4. Reversibility | "Cancel any time in the app." |

Never use microcopy for: legal boilerplate (link it), a second sales claim, or reassurance without content ("We respect your privacy" — say *what* you do).

### 10.4 First-person vs second-person button copy — what is actually verifiable

The widely-repeated claim is that changing "Start **your** free 30 day trial" to "Start **my** free 30 day trial" increased click-through by **90%** in a test run by Michael Aagaard (ContentVerve/Unbounce) (source: https://www.wordstream.com/blog/ws/2015/02/20/call-to-action-buttons, retrieved 2026-07-29; secondary: https://www.campaignmonitor.com/blog/email-marketing/call-to-action-email-marketing/, retrieved 2026-07-29).

Status: **single test, one page, one audience, no published sample size or significance figures found; the original ContentVerve post could not be retrieved live during this research.** A separate, differently-sized claim (~14.8% lift from a one-word change) also circulates under the same author's name, which suggests the "90%" figure has been detached from its original context. Treat as **directional, not a rule** — [UNVERIFIED - needs check: original ContentVerve post, sample size, confidence interval, and whether the 90% was CTR or completed sign-ups].

**What to do operationally:** first-person possessive is a cheap variant worth testing, not a guarantee. It reads badly in two situations regardless of test data: (a) formal/enterprise B2B, where "Start my free trial" is tonally off; (b) Vietnamese, where there is no neutral first-person possessive that works on a button — see §13.7. Do not port this English tactic into Vietnamese by translation.

### 10.5 Form friction — the honest version

"Fewer fields always converts better" is over-claimed. Removing fields reduces friction *and* reduces lead quality; the net effect depends on whether the cost centre is traffic or sales time. Rules that hold regardless: (1) never ask for anything you will not use in the next 48 hours; (2) ask for the hardest field last; (3) explain any field whose purpose is not obvious, inline; (4) never use a field label as the only error message.
