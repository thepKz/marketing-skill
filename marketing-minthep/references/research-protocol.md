# Research Protocol

## Contents

- When this protocol runs
- Decision questions, not topics
- Source tiers, and what each tier is allowed to support
- Search in the market's own language first
- Triangulation fails when the three sources share one parent
- A research assistant is a discovery source
- A page that returns a shell is not a page you read
- When the source is behind a login
- Published, checked, and the date that is missing
- The evidence ledger
- The stop rule, made arithmetic
- The report
- What never gets invented

## When this protocol runs

Any time the answer will be used to commit money, headcount or a quarter. Plans, market assessments,
competitor work, feasibility calls, and the awkward ones where somebody has already decided and wants
support.

Two neighbours own things this file does not. `market-data-collection.md` owns where Vietnamese numbers
come from and what each family of measurement can carry; `market-assessment.md` owns the sizing
arithmetic and the alternatives grid. This file owns the search itself, and the decision to stop.

## Decision questions, not topics

Convert the brief into questions that have answers somebody could act differently on. Demand,
audience, the alternatives already in use, willingness to pay, channel access, and the constraints
nobody mentioned.

"Research the coffee market" is a topic. Nothing about it can come back false, which means nothing
about it can come back useful either. Rewrite it as: how many households in these provinces buy ground
coffee at all, and how often, and at what price paid.

A question you cannot imagine a disappointing answer to is not a question. It is a preference wearing
a question's clothes, and the search will find what it was sent to find.

## Source tiers, and what each tier is allowed to support

| Tier | What it is | What it may support |
|---|---|---|
| Official | Statistics office, ministry, regulator, standards body | Denominators, legal constraints, definitions |
| First-party | Your own transactions, CRM, receipts, platform exports | Anything about your own performance |
| Primary evidence | Interviews and observation you ran yourself | Behaviour, language, willingness to pay |
| Reputable secondary | Panel and syndicated research with method disclosed | Incidence and frequency, as ranges |
| Directional | Press, blogs, listicles, agency roundups | Where to look next, and nothing else |

The last row is the one that leaks. A directional source may point you at a fact and may never be the
citation for it. If a blog cites a study, the study is the source, and if you cannot open the study you
do not have the fact.

Platform-published reach and audience figures are their own case, and the rule is harsher: never a
denominator. `market-assessment.md` explains why, and `size_market.py` fails that chain on a critical
gate rather than warning about it.

## Search in the market's own language first

Search in Vietnamese first. Vietnamese sources are usually the only ones carrying the right
denominator, and English-first search finds the English write-up of a Vietnamese report instead — one
translation away from the number and dated later than it.

Record the query. Not just the URL — the words that found it. Six weeks later you will want to know
whether the absence you concluded from was real or was a bad query, and the query is the only part
nobody can reconstruct.

Search silence is not evidence of absence. It is one of the three Vietnamese biases named in
`market-data-collection.md`, and it appears most often as a claim that nobody is talking about a
category when in fact nobody is talking about it in the language you searched.

## Triangulation fails when the three sources share one parent

Three independent signals is the right instinct and the usual self-deception. In practice three
articles trace back to one press release, and the agreement you were reassured by is one source quoted
three times.

Before you count a conclusion as triangulated, check the parents. Open each source and find where its
number came from; if two of them cite the same original, you have two signals at most. One, if the
third is a blog citing the first.

Two genuinely independent sources beat four dependent ones. Prefer a different method rather than
another article — a panel figure and a receipt trace disagree in useful ways, where two panels usually
disagree in ways that only tell you about panels.

Independent means the errors are independent. That is the test.

## A research assistant is a discovery source

This applies to a delegated agent, a junior, and a language model, and the reason is the same for all
of them: what comes back is a claim about a page rather than the page.

Re-read every load-bearing claim at its source before it enters a deliverable. In building this skill,
three researched claims failed that re-reading: a field count that was wrong twice over, an API
behaviour that could not be verified without an account, and a payload description taken from a page
that never rendered. All three were plausible. That is the problem with them.

Load-bearing means the recommendation changes if the claim is false. Anything else can be summarised
without re-reading, and should be marked as summarised.

## A page that returns a shell is not a page you read

Modern documentation sites frequently serve a JavaScript shell to a fetcher and the real text only to a
browser. A fetch that returns a few kilobytes of script has not failed loudly. It has returned
something that looks like a successful read of a nearly empty page, and a careless workflow will
conclude the vendor documents nothing.

Check the byte count. `developers.zalo.me` behaves exactly this way, and the honest record is that the
page could not be read rather than that the platform publishes nothing.

Some sites serve full text to a search-engine user agent and a shell to everything else.
`banhang.shopee.vn/edu/` is one. Getting the text this way is legitimate reading; presenting an
unrendered fetch as a verified absence is not.

## When the source is behind a login

Say so. Put it in the deliverable with the screen that would settle it, because a finding of "the
vendor does not publish this outside the account" is a real finding and belongs in the report.

Then name a person with an account and what they should bring back. Usually a screenshot. This is the
`path-unpublished` discipline from `attribution-windows.csv`, and it costs more than a shrug because
somebody has to actually be asked.

Never fill the gap from memory. A remembered default is indistinguishable, on the page, from a read one
— and the whole reason the row exists is that the two are different.

## Published, checked, and the date that is missing

Record the publication date and the retrieval date, and treat them as different facts. A 2019 panel
report retrieved today is a 2019 fact.

Many vendor help pages publish no last-updated date at all. Google's do not. So the only honest
annotation is the date you checked it, which claims nothing about when it changed, and the note has to
say that rather than dressing a retrieval date as a publication date.

Anything older than a year gets flagged. `size_market.py` fails `sources-are-not-stale` at that
boundary, measured against a stated as-of date rather than against today, so a saved chain does not
quietly rot into a pass.

Institutions rename and their hosts die. `market-data-collection.md` carries the table; the working
tell is that a citation to a dead host proves nobody opened it.

## The evidence ledger

Every finding carries: `finding_id`, the decision question it serves, source URL, publisher,
publication date, retrieval date, the quote or data point, your interpretation held separately from it,
confidence as `high|medium|low`, the bias or limitation, and the allowed use.

Interpretation held separately is the field that does the work. A quote and a reading of a quote merge
within about a week of being written in the same cell, and after that nobody can tell which part the
source actually said.

Confidence is not a feeling about the source. `high` means official or first-party, opened and read;
`medium` means method disclosed and read; `low` means everything else, including anything a directional
source told you.

## The stop rule, made arithmetic

"Stop when the decision threshold is met, not when the search feels exhaustive" is the right rule and
was, for a long time here, unusable advice. Exhaustive is a feeling and so was met. Both are now
computable. This is the one piece of procedure this file uniquely owns.

State the threshold before searching: the number that flips the decision. Build the chain in
`size_market.py`, with a range on every term and a source URL on every range. Then ask the script.

```
python scripts/size_market.py --check chain.csv --threshold 2000000000
```

Three verdicts come back, and each one is an instruction. Entirely above the threshold, or entirely
below it: stop, because no additional precision can change what you do. Straddling it: keep going, and
the script names which terms would settle it on their own, widest uncertainty first.

Terms it does not name cannot change the outcome however precisely you pin them down. That is where
research hours go to die, and it is usually the term the team finds most interesting.

One verdict has no research answer. A threshold sitting on the centre of your own range can never be
settled by narrowing a single term, because collapsing any term to its centre leaves the centre where
it was. Report that as a decision balanced on an estimate, and stop searching.

## The report

Explain the conclusion before the jargon, because the reader is usually a founder who has four other
jobs today. An executive answer first, in the language of the decision. Then the evidence table, the
assumptions, the implications for market and competitors, the recommendation, the risks, and the next
research actions with the dominant uncertainty named.

Cite URLs inline and append the sources. Mark each finding's confidence in the table rather than in a
paragraph about methodology, which nobody reads.

State what remains unknown. A report with no unknowns section is either finished research, which is
rare, or an unfinished search that stopped feeling incomplete.

## What never gets invented

Not sizing figures, not customer quotes, not competitor pricing, not regulations, not trend claims. If
browsing is unavailable, return the research plan and mark the report unverified at the top rather than
in a footnote.

For scientific, health, behavioural, environmental or efficacy claims, prefer systematic reviews,
primary peer-reviewed studies, recognised standards and official regulatory sources. Record population,
method, sample size, outcome, effect size where given, and the limitations the authors state
themselves. Then record whether the design supports correlation or causation. Copy crosses that line
quietly, and once it is crossed in a headline nobody goes back to the method section.

`claims-proof-ledger.md` owns what may then be said in public, which is narrower than what the evidence
supports.


---

<!-- Deep dossier merged from references/dossiers/anti-fabrication-protocol.md (2026-08-06). Long-form research behind the working sections above. External facts retrieved 2026-07-29; re-check anything priced, versioned, or platform-specific.  -->

# Research Protocol — Anti-Fabrication Operating Procedure

## Scope

Operating procedure for an AI agent doing market and creative research for a marketing/photography/AI-image skill, optimised for auditability over speed. Covers question decomposition, search strategy, source tiering, triangulation, voice-of-customer mining, claim-ledger discipline, anti-fabrication self-checks, adversarial verification, and artefact templates. Bias: Vietnamese SME market. Everything here is procedural — no market conclusions are asserted except as cited examples.

---

## 0. The three failure modes this protocol exists to prevent

| Failure | What it looks like | Why the usual fix fails |
|---|---|---|
| **F1 Fabrication** | A plausible URL, statistic, study, price, or quote that does not exist | "Be accurate" instructions do not work. Fabrication is fluent and internally consistent; it must be *mechanically* caught by retrieval, not caught by care |
| **F2 Laundering** | Three "independent" sources that all trace to one unsourced press release | Counting sources without tracing provenance produces false confidence that scales with effort |
| **F3 Silent promotion** | An `inferred` guess appearing in the final deliverable with no marker, then becoming public copy | Confidence labels applied at research time but stripped at writing time. The label must survive into the artefact |

Empirical size of F1: an audit of 111 million references across 2.5 million papers on arXiv, bioRxiv, SSRN and PubMed Central produced a conservative estimate of **146,932 hallucinated citations in 2025 alone** (source: https://arxiv.org/abs/2605.07723, retrieved 2026-07-29). In a controlled test, GPT-4o generating six mental-health literature reviews produced 176 citations of which **35 (19.9%) were entirely fabricated**, and of the 141 real citations **64 (45.4%) contained errors**; among fabricated citations with DOIs, **64% (21/33) were valid DOIs pointing at unrelated articles** and 36% (12/33) were invalid (source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12658395/, retrieved 2026-07-29). The valid-DOI-wrong-article pattern is the dangerous one: it survives a naive link check.

Consequence precedent: in *Mata v. Avianca, Inc.*, 678 F.Supp.3d 443 (S.D.N.Y. 2023), Judge P. Kevin Castel sanctioned two attorneys and their firm **$5,000** on 2023-06-22 for filing a brief citing **six court decisions that did not exist**, generated by ChatGPT (source: https://law.justia.com/cases/federal/district-courts/new-york/nysdce/1:2022cv01461/575368/54/, retrieved 2026-07-29).

**Operating consequence:** a claim is not "probably right until disproven." A claim is `unknown` until a retrieved artefact says otherwise.

---

## 1. Question decomposition

### 1.1 The procedure

Input is almost always a vague business request. Output must be a numbered list of questions each of which is *independently answerable by a bounded search* and each of which has a *named decision it changes*.

Five mechanical steps:

1. **Extract the decision.** Write the sentence "The client will do X or Y depending on the answer." If you cannot write it, the question is decoration — drop it or reclassify as context.
2. **Name the entity, the geography, the time window, and the unit.** A question missing any of the four is not answerable. `"demand for premium bún bò"` → entity `premium bún bò shop`, geo `Da Nang city, post-2025-07-01 boundary`, window `trailing 12 months`, unit `weekly covers and average ticket in VND`.
3. **Split until each question has ONE answer shape.** One number, one date, one yes/no, one list, or one verbatim quote set. "Is there demand and can we charge more?" is two questions with different source strategies.
4. **Assign a question type** from the taxonomy in 1.2. The type dictates source strategy, minimum source count, recency window, and confidence ceiling. This is the routing decision.
5. **Pre-commit the kill criterion.** Write, before searching, what result would make you abandon the direction. A question with no possible disconfirming answer is a question you will answer with your priors.

Worked transformation:

> **Vague request:** "I want to open a premium bún bò shop in Da Nang, is there demand?"

| # | Decomposed question | Type | Decision it changes | Kill criterion |
|---|---|---|---|---|
| Q1 | What is the resident population and administrative boundary of Da Nang as of 2026-07? | Market size | Denominator for every share estimate | — (definitional) |
| Q2 | How many bún bò establishments currently operate in Da Nang, and what price band do they occupy? | Competitor fact | Whether "premium" is an empty slot or a crowded one | ≥15 shops already above the target price → premium is not a gap |
| Q3 | What price do Da Nang diners currently pay for a bowl of bún bò, by tier? | Price point | Whether the premium ticket is a 1.4x or a 3x ask | Top observed tier < 1.3x median → no premium ceiling exists |
| Q4 | In their own words, what do Da Nang diners complain about and praise in bún bò shops? | Customer language | The positioning axis and the menu/service spec | Complaints are all about price → premium positioning fights the grain |
| Q5 | Which delivery platforms matter in Da Nang and what share do they hold? | Platform spec | Whether to build for delivery or dine-in first | — |
| Q6 | What licences must a food-service establishment hold, and what does non-compliance cost? | Regulatory constraint | Opening timeline and capex | — |
| Q7 | Is "premium local noodle soup" a rising or flat category signal in Vietnam? | Trend | Whether to lead with tradition or with modernity | Flat/declining → lead with tradition, not novelty |
| Q8 | What lighting/styling grammar do high-performing Vietnamese food posts use? | Craft technique | The image spec | — |

Note that Q1 through Q8 have **eight different source strategies**. Treating them as one search is the single most common research failure.

### 1.2 Question-type taxonomy and source strategy

`Tier` refers to §3. `Min. ind.` = minimum independent sources for a load-bearing claim. `Rot` = how fast the fact decays (see §3.5). `Ceiling` = highest confidence label achievable by desk research alone.

| Type | Answer shape | Primary source strategy | Tier floor | Min. ind. | Rot | Ceiling |
|---|---|---|---|---|---|---|
| **Market size** | One number + unit + year + geography | National statistics office → ministry release → industry association → research firm *with published methodology* | T1 for the denominator; T2 acceptable for the estimate | 2 (one must be T0/T1) | 12–24 mo | `observed` (almost never `confirmed`; most market sizes are models) |
| **Competitor fact** | Verifiable attribute (price, location, hours, SKU, claim) | The competitor's own page/menu/listing → business registry → marketplace listing → dated screenshot | T0 (their own page) | 1 if T0 and dated; 2 otherwise | 1–3 mo | `confirmed` if T0 + retrieval date + captured artefact |
| **Customer language** | Verbatim quote set + frequency count | Platform-native review/comment search, in local language, sampled by rule (§5.2) | T0 (the customer's own words) | ≥20 items for a theme claim | 3–6 mo | `observed` (never `confirmed` — you observed a sample) |
| **Platform spec** | Exact value (px, ratio, char limit, API field, eligibility rule) | The platform's own developer/help docs ONLY. Never a blog | T0 exclusively | 1 (T0) | 1–3 mo | `confirmed` |
| **Regulatory constraint** | Instrument number + article + effective date + penalty | Official gazette / national legal database → ministry portal → law-firm alert (as a *finder*, not the source) | T0 for the text; T1 to interpret | 1 T0 + 1 T1 interpretation | 6–18 mo (or instantly on amendment) | `confirmed` for the text; `inferred` for the application |
| **Price point** | Range + currency + date + what's included | Live listing/menu with capture date → marketplace → delivery app | T0 (the seller's own price) | 3 sellers minimum for a band | **2–8 weeks** | `observed` |
| **Trend** | Direction + magnitude + window + measurement instrument | Search-interest index → platform trend tool → dated press coverage. Always state the instrument | T1 | 2 with *different instruments* | 1–6 mo | `observed` at best; usually `inferred` |
| **Craft technique** | Named technique + numeric parameters | Manufacturer/optics documentation, standards bodies, physics. Practitioner sources only for aesthetic convention | T0/T1 | 1 for physics; 2 for convention | 3–10 yr (physics: never) | `confirmed` for physics; `observed` for convention |

**Type-boundary trap:** a "market size" question often hides a "price point" question with a much shorter half-life. If your TAM number is `price × volume`, the whole TAM inherits the **2–8 week** rot of the price, not the 24-month rot of the volume. Date the TAM to its fastest-rotting input.

### 1.3 The answerable-question test

Reject or rewrite any question that fails any of these five:

| Check | Threshold |
|---|---|
| **Unit named** | The answer has a stated unit (VND, %, px, count, date). "Is it popular?" fails; "What % of Da Nang delivery orders are noodle soups?" passes |
| **Geography bounded** | Named to the administrative unit *and* dated, because boundaries move (see §3.5) |
| **Window bounded** | "Trailing 12 months" or "as of 2026-07", never "currently" |
| **One answer shape** | If the answer needs both a number and a list, it is two questions |
| **Falsifiable** | You can state a retrieved result that would make the answer "no" |

### 1.4 Unanswerable-question triage

Some questions are genuinely not answerable by desk research. Do not answer them anyway. Route them:

| Situation | Route to |
|---|---|
| No public data exists (e.g. a private shop's revenue) | **Proxy with declared error bars** — name the proxy, name the assumption, mark `inferred`, state the multiplier range |
| Data exists but is paywalled | **State the source, the price, and what it would resolve.** Do not paraphrase a paywalled report from its press release |
| Only obtainable by primary fieldwork | **Convert to a fieldwork instruction** — "count covers at 3 shops, Fri 18:00–20:00, 2 weeks apart" |
| The client already knows it | **Ask one question** rather than researching |

---

## 2. Search-strategy playbook

### 2.1 The seven-angle multi-modal sweep

A single query answers a single framing. Run angles, not queries. For any non-trivial question, run at least **four** of the seven; for a load-bearing claim, run **all seven** or record why an angle is not applicable.

| # | Angle | Query shape | What it uniquely surfaces | Failure if skipped |
|---|---|---|---|---|
| A1 | **By entity** | Exact brand/shop/product name, quoted | Official pages, registry entries, the entity's own claims | You describe a competitor from hearsay |
| A2 | **By category** | Generic category noun + geo | Market overviews, category-level lists, association data | You miss the size of the pool |
| A3 | **By customer complaint language** | The complaint phrased as a customer would type it | Real objections, unmet needs, churn reasons | Your positioning solves a problem nobody has |
| A4 | **By comparison** | `X vs Y`, `X or Y`, `alternative to X`, `thay vì X` | Substitution sets, the real competitive frame, decision criteria | You compete against the wrong set |
| A5 | **By price** | Price token + unit + geo (`"giá" + "bao nhiêu"`, `"bảng giá"`) | Actual transaction prices, not list prices | Your pricing is a guess |
| A6 | **By local-language term** | The native term including regional variants and no-diacritic form | Local operators, local forums, local pricing, local slang | See §2.3 — this is the highest-yield angle for a VN question |
| A7 | **By platform-native search** | Search *inside* the platform, not via a search engine | Reviews, comments, listings, ad creative — content that search engines index poorly or not at all | Your VOC evidence is thin and your competitor creative set is empty |

**Angle-yield rule:** log the number of *new distinct sources* each angle produced. An angle that produced zero new sources across two query variants is exhausted for this question. An angle that produced ≥3 new sources deserves a second pass with narrowed terms.

### 2.2 Operator grammar

Only these operators are documented by Google itself: exact-match `""`, `site:`, exclusion `-`, `before:`, `after:`, and `filetype:` (source: https://support.google.com/websearch/answer/2466433, retrieved 2026-07-29). Everything else is community knowledge and may degrade without notice.

| Operator | Documented by Google | Use it for | Caution |
|---|---|---|---|
| `"exact phrase"` | Yes | Locking a verbatim customer phrase or a legal instrument name | Quotes narrow hard; a zero-result quoted query is information, not failure |
| `site:` | Yes | Restricting to a T0 domain (`site:gso.gov.vn`, `site:developers.tiktok.com`) | No space after the colon |
| `-term` | Yes | Killing an SEO-farm cluster (`-pinterest -listicle -"top 10"`) | Over-exclusion hides the disagreement you need |
| `before:` / `after:` | Yes | Enforcing the recency window (`after:2025-07-01`) | Dates are the *page's* claimed date, which content farms forge |
| `filetype:pdf` | Yes | Reaching methodology annexes, statistical yearbooks, gazettes | The highest-yield operator for T0/T1 primary data |
| `intitle:` / `inurl:` | **Not on the official page** | Finding methodology or price pages | Works in practice; treat as unsupported. `[UNVERIFIED — needs check against Google's current supported list]` |
| `OR` | **Not on the official page** | Regional term variants | Must be uppercase; behaviour inconsistent |
| `cache:`, `related:`, `link:`, `info:`, `+`, `~` | Retired | — | Do not use. `cache:` was withdrawn in 2024; use a web archive instead (retirement dates from secondary SEO sources only — `[UNVERIFIED]` as to exact dates) |

**High-yield operator stacks:**

| Goal | Stack |
|---|---|
| Find the methodology behind a market number | `"market size" "methodology" filetype:pdf <category> <geo>` |
| Find a regulation's actual text | `site:vanban.chinhphu.vn OR site:thuvienphapluat.vn "<instrument number>"` |
| Escape content farms | `<query> -site:pinterest.com -"top 10" -"best of" after:2026-01-01` |
| Find the primary statistic | `site:nso.gov.vn OR site:gso.gov.vn <indicator> filetype:pdf` |
| Find real prices | `"<dish/product>" "giá" <district> site:facebook.com` |

### 2.3 Why Vietnamese-language search returns different — and usually better — local results

For a Vietnamese market question, an English query and a Vietnamese query are **not two attempts at the same search**. They retrieve from largely disjoint corpora. Four mechanisms:

| Mechanism | Effect | Practical rule |
|---|---|---|
| **The supply side writes in Vietnamese** | Menus, price lists, shop pages, local news, forum threads, and reviews for a Da Nang noodle shop exist in Vietnamese and mostly nowhere else. An English query cannot retrieve a document that does not exist | Every entity-, price-, and complaint-angle query must be run in Vietnamese |
| **English results skew to expat/tourist and B2B-export framing** | English queries about Vietnamese food return travel listicles and investment overviews — a different population with different price tolerance | Never source a *local* price band from an English-language source |
| **Diacritic and no-diacritic forms behave differently** | Vietnamese users frequently type without diacritics (`bun bo hue da nang`). The diacritic form (`bún bò Huế Đà Nẵng`) tends toward edited/published content; the bare form tends toward user-generated content | Run **both** forms. Treat them as two angles, not one |
| **Regional lexical variants** | The same object has different words by region. Missing the local variant zeroes out the local corpus | Build a 3–8 term variant list before searching; log it in the research log |

Locale parameters matter as much as language: search-engine results differ by interface language and country. Set both (`hl=vi`, `gl=VN` equivalent) or use a VN-hosted query path. `[UNVERIFIED — no official Google documentation of diacritic normalisation behaviour was located; the dual-form rule is an empirical precaution, not a documented mechanism]`

**Dual-query template** — for every load-bearing local question, log all four cells:

| | Diacritics | No diacritics |
|---|---|---|
| **Vietnamese** | `"bún bò" "Đà Nẵng" giá` | `bun bo da nang gia bao nhieu` |
| **English** | `"bun bo" Da Nang premium restaurant price` | — |

The English row exists to catch international trade press and research-firm coverage. It is never the source for a local price, a local complaint, or a local competitor count.

### 2.4 Platform-native search — and the access reality check

This is where most research plans quietly fail. The tool you assume exists usually does not exist *for you*. Verified constraints as of 2026-07-29:

| Platform surface | Access reality | Verified constraint |
|---|---|---|
| **Meta Content Library / API** | **Unavailable to commercial users.** Eligibility requires "affiliation with an academic institution or other non-university organization, institute, or society which operates as a not-for-profit entity and holds scientific or public interest research as a primary purpose." Coverage thresholds: Facebook Pages need 15,000+ followers for downloadable data; Instagram accounts need 25,000+; profiles/posts need 100+ followers or verification (source: https://transparency.meta.com/researchtools/meta-content-library/, retrieved 2026-07-29) | A marketing agency cannot lawfully use it. A small Da Nang shop would be **below the follower threshold anyway** |
| **TikTok Research API** | **Unavailable.** Applicants must be located in the US, EEA, UK, Switzerland, or Brazil, and must "be independent from commercial interests and be able to conduct research on a not-for-profit or non-commercial basis," with evidence of ethical research review (source: https://developers.tiktok.com/products/research-api/, retrieved 2026-07-29) | Excluded on both geography and commercial status |
| **TikTok Commercial Content API / Ad Library** | **Does not cover Vietnam.** Supported in Continental Europe plus the UK, Norway, Iceland, Liechtenstein and Switzerland. Vietnam is not in the list (source: https://developers.tiktok.com/doc/commercial-content-api-supported-countries, retrieved 2026-07-29) | Any plan that says "check the TikTok ad library for Vietnamese competitors" is void |
| **Meta Ad Library (public UI)** | Searchable by page/advertiser and keyword; no performance metrics for commercial ads. Richer transparency fields (targeting, reach breakdown, payer) apply to EU/UK under the DSA and to political/social-issue ads, not to ordinary Vietnamese commercial ads | `[UNVERIFIED — direct fetch of the Vietnam-filtered Ad Library failed in this session; coverage details come from tertiary SEO sources only. Needs a browser-session check]` |
| **Google Maps / Business Profile reviews** | Publicly readable, local-language, geo-anchored, star-rated, dated. **The single highest-value VOC surface for a Vietnamese physical business** | Manual/observational reading only; see §5.6 on automated collection |
| **Delivery-app listings (ShopeeFood, GrabFood, beFood)** | Live prices, menu structure, ratings, photos, order counts | Prices rot in weeks. Capture with date |
| **Google Trends** | Free, VN geo available. But it is **not search volume**: each data point is divided by total searches in that geography/time, then scaled 0–100; searches "made by very few people" are shown as 0; duplicate searches from the same person in a short period and special characters are removed; and statistical noise is deliberately added, "most noticeable on queries with low or no search interest" (source: https://support.google.com/trends/answer/4365533, retrieved 2026-07-29) | For a city-level Vietnamese dish query you will frequently get 0 or noise. **A Google Trends flat line for a low-volume local term is not evidence of no demand** |
| **Facebook Groups / TikTok comments / Vietnamese forums** | Richest complaint language; effectively unindexed by search engines | In-platform search only; sampling discipline mandatory (§5.2) |

**Rule:** before writing a research plan that names a tool, state its eligibility and coverage in one line. A plan naming an inaccessible tool is a fabricated plan.

### 2.5 Recognising an exhausted search angle

Stop an angle when **two or more** of these fire. Log which fired.

| Signal | Threshold |
|---|---|
| **New-source yield collapse** | Two consecutive query variants return zero sources not already in the source map |
| **Circular provenance** | Three or more results cite the same upstream source, and that source has already been read (or is unreachable) |
| **Farm saturation** | ≥60% of the first page scores ≥3 on the slop rubric (§3.3) |
| **Answer convergence** | Five or more T0/T1 sources agree within your required precision — further search cannot change the decision |
| **Precision achieved** | The remaining uncertainty is smaller than the decision threshold. If ±10% doesn't change the answer, stop at ±10% |
| **Budget exhausted** | The per-type query budget (§2.6) is spent. Record residual uncertainty instead of overrunning |

Anti-signal — **do not** stop because: the first result "looks authoritative"; the answer matches your prior; or you found a number and the number is round. Round numbers in market research are usually rounded *estimates of estimates*.

### 2.6 Query budget by question type

Budgets prevent both under-research and infinite loops. Counts are distinct queries, not results read.

| Question type | Queries | Fetches (full-page reads) | Escalate if unresolved |
|---|---|---|---|
| Platform spec | 1–2 | 1–2 (T0 docs) | Stop and report the doc's silence. Never infer a spec |
| Regulatory constraint | 2–4 | 2–3 (instrument text + 1 interpretation) | Flag for legal review; do not interpret alone |
| Competitor fact | 2–4 per competitor | 1 per competitor (own page) | Mark `unknown`, note what a site visit would resolve |
| Price point | 4–8 | 3+ live listings | Widen geography one step, mark the widening |
| Market size | 6–12 | 3–5 incl. one methodology doc | Deliver a range with named sources, not a point estimate |
| Customer language | 6–15 (multi-language, multi-platform) | 20+ items sampled | Report sample size and star/sentiment distribution |
| Trend | 4–8 | 2+ with different instruments | Report as `inferred` with the instrument named |
| Craft technique | 2–5 | 1–3 (manufacturer/standards) | Distinguish physics (settleable) from convention (not) |

---

## 3. Source tiering

### 3.1 Tier definitions

| Tier | Definition | Examples | Use |
|---|---|---|---|
| **T0 — Primary** | The artefact *is* the fact. The party with authority over the fact published it | Official gazette / legal instrument text; national statistics office release; platform developer or help docs; a company's own product page, menu, price list, filing; a customer's own review text; manufacturer optical specs | May solely support any claim, including client-facing copy, when captured with a retrieval date |
| **T1 — Secondary, methodology-disclosed** | Reputable trade press or a research firm that publishes *how it got the number* — sample, frame, dates, model | State-affiliated legal/business press; ministry-quoted reporting; a research firm's methodology annex; a law-firm alert *interpreting* a named instrument; peer-reviewed study | May support a claim if the number is attributed in-text with source and date. Preferred for interpretation |
| **T2 — Secondary, methodology-opaque** | Real reporting or a real firm, but the number arrives without a traceable method | Press releases announcing "market to reach $X by 2033"; vendor blogs citing their own data; aggregator portals restating others; consultancy summaries | **May not solely support a client-facing claim.** May be used to (a) locate a T0/T1 source, (b) establish that a claim is widely circulated, (c) bound a range with the opacity disclosed |
| **T3 — Tertiary** | SEO content, listicles, content farms, AI-generated articles, unsourced aggregation, engagement-bait | "Top 10 X in 2026" pages, generic "complete guide" blogs, scraped-and-restated content | **Discovery only.** May suggest a search term or a candidate entity. May never appear as a citation in a deliverable |

**Special case — Statista and similar portals.** These are frequently mistaken for T0 because they display a chart and name a government source. Statista's own published methodology describes a six-step pipeline (Sourcing → Processing → Modelling → Forecasting → Quality Control → Updating) using top-down and bottom-up modelling, often hybridised — i.e. Market Insights figures are **modelled**, not measured (source: https://cdn.statcdn.com/static/img/outlook/methodology/methodology-en.pdf, retrieved 2026-07-29; `[UNVERIFIED verbatim — the PDF could not be text-extracted in this session; the six-step and top-down/bottom-up description comes from the search index of that document. Needs a re-fetch to quote the accuracy disclaimer exactly]`).

Correct handling: treat a Statista page as **T2 that names a T0**. Follow the named source. If the underlying source is a national statistics office, cite that office. If the page's own model is the origin, it is T2 and cannot solely support a client-facing number.

### 3.2 The hard rule — what may support a claim in a client-facing document

| Claim stakes | Definition | Required support | Forbidden support |
|---|---|---|---|
| **S3 — Public/legal** | Appears in ads, packaging, PR, a PDP, a price, a certification, a comparative claim, or on-image text | ≥1 T0, retrieval-dated, plus a named owner in the claim ledger. Regulated claims additionally require the client's own evidence | T2, T3, any `inferred` or `unknown` value, any LLM recollection |
| **S2 — Strategic** | Drives spend, pricing, positioning, or opening a location | ≥2 independent sources, at least one T0/T1, with the disagreement written if any | T3 as sole support; a single T2 press release |
| **S1 — Directional** | Shapes a hypothesis or a creative angle to be tested | ≥1 T1/T2, labelled `observed` or `inferred` in-text | Presenting it as fact; omitting the label |
| **S0 — Internal** | Search-term generation, entity discovery, brainstorming | Anything, including T3 | Carrying it forward without re-sourcing |

**The one-line version:** *nothing enters public copy on the strength of a source you would not show the client.* If you would be embarrassed to put the URL in a footnote, it cannot carry the claim.

### 3.3 Spotting an SEO content farm and AI slop

Prevalence justifies aggressive filtering. A random sample of **55,400 English-language URLs from Common Crawl** (≥100 words, published Jan 2020–Mar 2026, classified as articles or listicles, labelled AI-generated when >50% of content was flagged by Pangram, GPTZero and Copyleaks) found AI-generated articles rose from **2.2% in January 2020 to 51.7% in May 2025**, first exceeding human-written articles around **November 2024** (source: https://graphite.io/five-percent/more-articles-are-now-created-by-ai-than-humans, retrieved 2026-07-29; coverage: https://www.axios.com/2025/10/14/ai-generated-writing-humans, retrieved 2026-07-29).

Read that number carefully — it is a good example of the discipline this protocol demands. It covers **English-language articles and listicles only**, not all web content, and the AI/human line is blurred by human-edited AI drafts. Note also that Axios's own headline on the same study was *"AI-written web pages haven't overwhelmed human-authored content"* — the same data supports two framings depending on whether the denominator is "new articles" or "all pages." **Do not quote the 51.7% as "most of the web is AI."**

Google's own spam policies give named, quotable categories (source: https://developers.google.com/search/docs/essentials/spam-policies, last updated 2026-05-15 UTC, retrieved 2026-07-29):

- **Scaled content abuse** — "when many pages are generated for the primary purpose of manipulating search rankings and not helping users."
- **Site reputation abuse** — "a tactic where third-party content is published on a host site mainly because of that host's already-established ranking signals."
- **Expired domain abuse** — "where an expired domain name is purchased and repurposed primarily to manipulate search rankings by hosting content that provides little to no value to users."
- **Thin affiliation** — "publishing content with product affiliate links where the product descriptions and reviews are copied directly from the original merchant without any original content or added value."

The practical consequence of *site reputation abuse* is the nastiest one for research: **a page on a domain you trust may be paid third-party content**. Domain authority is not a source tier.

**Slop rubric — score each candidate page. 0–1 usable; 2 use with caution; ≥3 discard.**

| # | Signal | Threshold |
|---|---|---|
| 1 | **No named author, or an author with no other traceable work** | Byline absent, or "Admin", or a stock-photo headshot with no outbound profile |
| 2 | **No first-hand artefact** | Zero original photographs, screenshots, data tables, or interview quotes. All images are stock or generated |
| 3 | **Numbers with no origin** | Statistics appear with no source, or sourced to another blog, or sourced to a page that doesn't contain the number |
| 4 | **Date laundering** | Title says "2026" but content describes an older state; or the "updated" date changes while the text does not |
| 5 | **Uniform section rhythm** | Every H2 followed by 2–4 sentences and a 3–5 item bullet list, repeated 8+ times, with no varying paragraph length |
| 6 | **Restatement of the question** | The first 150 words define the obvious ("A menu is a list of dishes offered by a restaurant") |
| 7 | **Comparative claims with no comparison** | "Better than competitors" with no named competitor or measured axis |
| 8 | **Hedge stacking** | "can help to potentially improve" — three hedges in one clause, i.e. no commitment to any fact |
| 9 | **Category-generic imagery/examples** | Examples could apply to any industry with a noun swapped |
| 10 | **Conclusion adds nothing** | Final section restates the H2s verbatim |
| 11 | **Affiliate/commercial density** | ≥3 affiliate or product CTAs above the first substantive claim |
| 12 | **Translationese in a local-language page** | Vietnamese text with English syntax and no regional lexical variants — a machine translation of an English farm page, so it carries no local knowledge |

Signal 12 is specific and high-value: a Vietnamese-language page that is a translated English farm page looks like local evidence and is not. Test it by checking whether the page uses regional variant terms and real local place names, or only generic ones.

**Countermeasure queries:** append `-"top 10" -"best of" -"ultimate guide"`; add `filetype:pdf` to jump to methodology documents; add `site:` to pin a T0 domain.

### 3.4 Research-firm credibility screen

Before accepting any firm's number, all five must be answerable **from the document you are reading**. Any "no" demotes it to T2.

| # | Question | If unanswerable |
|---|---|---|
| 1 | What was measured, in what unit, over what period? | T2. You cannot compare it to anything |
| 2 | What was the sample or the frame, and how large? | T2. "Survey shows 73%" with no n is not evidence |
| 3 | Was the figure measured, modelled, or forecast? | T2. Modelled ≠ measured; forecast ≠ fact |
| 4 | Who paid for it, and does the sponsor sell into the finding? | Vendor-sponsored research favouring the vendor's category → T2 and disclose the sponsor in-text |
| 5 | Is the geography the one you need, at the granularity you need? | National data cannot answer a city question. Do not silently downscale |

**Worked application.** The Vietnam food-delivery share figures in §4.4 pass this screen: the VnExpress report names **NielsenIQ** (April 2025 consumer survey on online food ordering) and **Decision Lab** (~1,000 consumers interviewed in Hanoi, Da Nang and Ho Chi Minh City), giving instrument, timing, geography and — for one of them — sample size (source: https://e.vnexpress.net/news/business/data-speaks/shopeefood-and-grabfood-dominate-vietnam-s-food-delivery-market-with-90-share-4911896.html, published 2025-07-09, retrieved 2026-07-29). That earns T1. A press release saying "Vietnam food delivery to reach $9B" with no method earns T2 regardless of how often it is repeated.

**Platform-reported audience data needs the same screen.** DataReportal's Digital 2026 Vietnam report states 102 million total population, 85.6 million internet users (84.2% penetration) and 79.0 million social media user identities (77.6%) as of October 2025, with platform figures including Facebook 79.0M, TikTok 76.1M adults 18+, Zalo 78.3M, YouTube 62.1M, Messenger 57.8M, Instagram 11.7M, LinkedIn 10.0M — and explicitly cautions that these come from **platform advertising tools**, that **advertising reach is not monthly active users**, that Meta made "meaningful revisions" to its methodology, that some penetration rates exceeding 100% of the adult base are reported "as is", and that **year-on-year comparisons are discouraged** (source: https://datareportal.com/reports/digital-2026-vietnam, retrieved 2026-07-29).

That caveat block is *why* DataReportal is T1 rather than T2 — it discloses its own limits. It is also why "TikTok reaches 76.1M Vietnamese adults" must never be written as "76.1M Vietnamese adults use TikTok."

### 3.5 Recency requirements — what rots in weeks, what lasts years

| Claim class | Half-life | Re-verify before | Why |
|---|---|---|---|
| Live price, promo, stock, delivery fee | **2–8 weeks** | Every deliverable | Menu prices and platform fees change without announcement |
| Platform ad spec, character limit, safe-zone, API field | **1–3 months** | Every export | Changed silently; a stale spec produces a rejected asset |
| Platform eligibility/coverage (research APIs, ad libraries) | **3 months** | Every research plan | See §2.4 — coverage and eligibility both moved recently |
| Competitor menu, positioning, ad creative | **1–3 months** | Every competitive claim | Creative rotates on a campaign cycle |
| Social platform audience figures | **6–12 months** | Any audience-size claim | Methodology revisions break comparability (see §3.4) |
| Trend / search-interest reading | **1–6 months** | Any trend claim | Index is relative and seasonal |
| Category market size / GMV | **12–24 months** | Annual | Published annually at best |
| **Administrative geography** | **event-driven** | Any geo claim | See below |
| Regulation | **6–18 months, or instantly on amendment** | Any compliance claim | Amendments have hard effective dates |
| Demographic structure, income distribution | **2–5 years** | Multi-year plans | Census/survey cycles |
| Craft convention (styling, colour trend, aesthetic) | **1–3 years** | Brand refresh | Fashion cycle |
| Optics, colour science, physics | **Never** | — | Not time-sensitive; needs no citation |

**The administrative-geography trap — a live worked case.** Vietnam consolidated from 63 to 34 provincial-level units. Resolution No. 202/2025/QH15 finalised the new names and took effect 2025-06-12, with the new structure operational from 2025-07-01, following Decision No. 759/QD-TTg of 2025-04-14. **Da Nang absorbed Quang Nam province**, retaining the name Da Nang City, producing an area of 11,859 km² and a population of **3.06 million** (source: https://www.vietnam-briefing.com/news/vietnams-government-introduces-official-plan-for-provincial-mergers.html, retrieved 2026-07-29).

Pre-merger Da Nang metro population was estimated at **1,286,000 for 2025** (source: https://www.macrotrends.net/global-metrics/cities/22455/da-nang/population, retrieved 2026-07-29 — T3/modelled, UN-derived series).

So "the population of Da Nang" is either **1.29M or 3.06M** — a **2.4x** difference — turning on a boundary change with a specific effective date. Any market size, per-capita figure, or share-of-population estimate built on the wrong one is wrong by 140%. Every Vietnamese geographic claim after 2025-07-01 must state which boundary it uses. Note also that the 3.06M figure is a merged-unit planning figure including a large rural population that is **not** addressable by a premium urban restaurant — a separate error from the boundary error, and one that averaging cannot fix.

**Institutional churn compounds this.** Vietnam's General Statistics Office now operates as the **National Statistics Office** under the Ministry of Finance, and both `gso.gov.vn` and `nso.gov.vn` currently resolve (source: https://www.nso.gov.vn/en/gso-organizational-chart/ and https://www.gso.gov.vn/en/about-gso/, retrieved 2026-07-29). `[UNVERIFIED — the exact date and instrument of the rename was not located. Needs a check against the Ministry of Finance reorganisation decision.]` Search both domains; a dead link does not mean the data is gone.

---

## 4. Triangulation and conflict resolution

### 4.1 The independence test

Three sources are not three sources if they share an origin. Before counting a source toward a minimum, run the chain:

| Step | Action | Disqualifier |
|---|---|---|
| 1 | Find the number's stated origin in each source | Two sources naming the same origin count as **one** |
| 2 | Follow the origin to its own document | If the origin document does not contain the number, **all** downstream sources are void, not merely weak |
| 3 | Check the measurement instrument | Two sources using the same survey are one source, even if published independently |
| 4 | Check ownership and sponsorship | A vendor's blog and a "research firm" report the vendor commissioned are one source |
| 5 | Check the date of the underlying measurement, not of publication | Two 2026 articles citing one 2023 survey are one 2023 data point |

**Citation laundering** is the named failure: a number originates in an unsourced press release, is restated by three trade outlets, aggregated by a portal, then appears in an AI answer as "widely reported." Confidence rose; evidence did not. Detection: every restatement uses the *same rounded figure* and none states the method.

Independence ladder, strongest first:

1. Two T0 sources with different collection methods (a government census and a platform's own reported figure)
2. One T0 plus one T1 with disclosed, different methodology
3. Two T1 sources with different instruments and different sponsors
4. Two T1 sources with the **same** instrument — counts as one
5. Any number of T2/T3 restatements — counts as **zero**

### 4.2 Triangulation requirement by stakes

| Stakes | Requirement |
|---|---|
| S3 public/legal | 1 T0 that *is* the fact (a price on the seller's own page is the price), or 2 independent T0 if the fact is contested |
| S2 strategic | 2 independent sources, ≥1 T0/T1. If they disagree beyond your decision threshold, run §4.3 |
| S1 directional | 1 source, labelled |
| Any number appearing in a headline, chart title, or slide title | Treat as S2 minimum regardless of intent — numbers in headlines get quoted onward and lose their caveats |

### 4.3 Conflict-resolution decision tree

When two credible sources disagree, **never pick one silently.** Run in order; record which branch resolved it.

| # | Test | If it resolves | If not |
|---|---|---|---|
| 1 | **Same thing measured?** Same unit, population, inclusion rules? | Reconcile — this is a definition mismatch, not a conflict. Report both definitions | → 2 |
| 2 | **Same geography and boundary date?** | Reconcile — restate on a common boundary (see the Da Nang case) | → 3 |
| 3 | **Same time window?** | Reconcile — a 2023 and a 2025 figure are a time series, not a contradiction | → 4 |
| 4 | **Different tiers?** | Prefer the higher tier and say so in one explicit sentence | → 5 |
| 5 | **Different methodology quality?** (disclosed-n survey vs undisclosed model) | Prefer the disclosed method, state n, state the other figure | → 6 |
| 6 | **Sponsorship conflict?** | Prefer the unsponsored; disclose the other's sponsor in-text | → 7 |
| 7 | **Genuinely irreconcilable** | **Report the range with both attributions.** Confidence `observed` at best; state which decision the disagreement affects | — |

**The prohibition:** you may not average two irreconcilable estimates and present the average as a finding. An average of two numbers you cannot reconcile is a third number that no source supports — fabrication by arithmetic.

### 4.4 How to write a disagreement into the deliverable

```
CLAIM: <stated as a range, not a point>
SOURCE A: <figure> — <org>, <instrument>, <n>, <date>, <URL>, retrieved <date>
SOURCE B: <figure> — <org>, <instrument>, <n>, <date>, <URL>, retrieved <date>
LIKELY CAUSE: definition | boundary | window | method | sponsor | unknown
CONFIDENCE: observed | inferred
DECISION IMPACT: <what changes if A is right vs if B is right>
WHAT WOULD SETTLE IT: <the specific artefact needed>
```

**Worked example A — a live disagreement in Vietnamese delivery share.**

```
CLAIM: ShopeeFood and GrabFood together hold ~90% of Vietnam's food-delivery
       market, but the split between them is disputed and flips by city.
SOURCE A: ShopeeFood 56% / GrabFood 36%. NielsenIQ consumer survey on online
       food ordering, April 2025; supplemented by Decision Lab, ~1,000 consumers
       in Hanoi, Da Nang, HCMC. Reported by VnExpress, published 2025-07-09.
       https://e.vnexpress.net/news/business/data-speaks/shopeefood-and-grabfood-dominate-vietnam-s-food-delivery-market-with-90-share-4911896.html
       retrieved 2026-07-29
SOURCE B: ShopeeFood 48% / GrabFood 48% / beFood 4%, described as share of total
       sales rather than share of surveyed orders. Circulated in Vietnamese trade
       coverage; origin not traced to a methodology document in this session.
       [UNVERIFIED - needs the originating report identified before use]
LIKELY CAUSE: definition + method. A is share of *surveyed consumers' orders* in
       three cities; B appears to be share of *sales/GMV* nationally. Order share
       and revenue share diverge whenever average ticket differs by platform.
INDEPENDENT CONTEXT (different instrument): Vietnam online food delivery GMV
       ~USD 2.1bn in 2025, +19% YoY - Momentum Works.
       https://theinvestor.vn/vietnams-online-food-delivery-market-tops-21-bln-as-foreign-apps-dominate-d18259.html
       retrieved 2026-07-29
CITY-LEVEL, WHICH IS WHAT ACTUALLY MATTERS: ShopeeFood ~56% in Hanoi;
       GrabFood ~50% in HCMC (same VnExpress report). Da Nang was in the Decision
       Lab sample but no Da Nang-specific split was published.
CONFIDENCE: observed for "the two platforms dominate nationally";
       unknown for the Da Nang split specifically.
DECISION IMPACT: If launching delivery-first in Da Nang, platform priority
       depends on the Da Nang split, which neither source publishes. The national
       figure cannot substitute - the same report shows the leader flips by city.
WHAT WOULD SETTLE IT: (a) the Decision Lab city breakdown, or (b) 30 days of
       primary observation of order volume at 5 comparable Da Nang shops on
       both apps.
```

What this write-up does that a normal summary does not: it converts an apparent contradiction into a **usable finding** ("the leader flips by city, so the national number is unusable here") and names the specific missing artefact.

**Worked example B — a disagreement inside this dossier's own evidence base.**

Two large 2026 audits of fabricated citations, both examining ~2–2.5M papers and ~100M references, report counts differing by more than an order of magnitude:

| | Study A | Study B |
|---|---|---|
| Corpus | 111M references / 2.5M papers (arXiv, bioRxiv, SSRN, PubMed Central) | 97M citations / 2M+ papers |
| Headline count | **146,932** hallucinated citations in 2025 (conservative estimate) | **~4,000** fabricated citations across ~2,800 papers |
| Trend metric | Per-server rates rising since mid-2024 | 1 in 2,828 papers (2023) → 1 in 458 (2025) → 1 in 277 (first 7 weeks of 2026) |
| Attribution | Zhao, Wang, Stuart, De Vaan, Ginsparg, Yin; arXiv:2605.07723, submitted 2026-05-08 (source: https://arxiv.org/abs/2605.07723, retrieved 2026-07-29) | Columbia University team led by Maxim Topaz, published in *The Lancet*; reported 2026-05-07 (source: https://www.statnews.com/2026/05/07/lancet-study-finds-steep-rise-fraudulent-citations-academic-papers/, retrieved 2026-07-29) |

Likely cause: different detection thresholds and definitions of "fabricated" (unresolvable reference vs. reference verified not to exist). **Correct handling:** cite the *direction* as well-supported by two independent teams, cite the *magnitude* as disputed by roughly 36x, and never blend them. Per-server rates sometimes attributed to Study A (0.39% arXiv, 1.91% SSRN, 0.27% PubMed Central, 0.21% bioRxiv as of August 2025) appear only in secondary coverage, not in the abstract — `[UNVERIFIED — needs the full paper]`.

### 4.5 Named myths — flag these, never restate them

| Myth | Status | What to do |
|---|---|---|
| "Three sources agree, so it's confirmed" | False when all three share an origin (§4.1) | Trace provenance before counting |
| "Statista / an aggregator portal is a primary source" | False by the portal's own methodology (§3.1) | Follow to the named origin |
| "Google Trends shows search volume" | False. It is a normalised 0–100 relative index with low-volume terms zeroed and noise added (verified, §2.4) | Never convert a Trends value into a volume |
| "It ranks #1 on Google, so it's authoritative" | Ranking optimises relevance and quality signals, not truth; and third-party paid content can sit on trusted domains (Google's own *site reputation abuse* definition, §3.3) | Tier the page, not the domain |
| "High ad frequency in an ad library means the ad works" | Ad libraries publish existence, not performance. Meta's library shows no impressions/clicks/spend for ordinary commercial ads | Use for creative patterns only; never infer performance |
| "The menu 'sweet spot' — diners look at the upper-right first, so put the high-margin dish there" | Trade folklore. The most-cited academic test of menu sweet-spot/eye-path claims reported no supporting effect | `[UNVERIFIED — I could not verify the specific study in this session; the commonly cited reference is Sybil Yang's menu-design work in *Cornell Hospitality Quarterly* (c. 2012). Needs a direct read before citing either way.]` Treat as T3. Never state it to a client as fact |
| "Rule of 7 — a buyer needs 7 touches" | Untraceable to any published study | Do not cite. If frequency matters, measure it in the client's own data |
| "55/38/7 — communication is 7% words" | Real study (Mehrabian & Ferris, 1967) but about incongruent single-word vocal/facial cues, not marketing communication | `[UNVERIFIED — original paper not read in this session]`. Do not generalise it to campaigns |
| "Users judge a page in 50ms" | A real finding exists on very fast visual-appeal judgements, but it is about *aesthetic preference*, not comprehension or conversion | `[UNVERIFIED — needs the primary paper]`. Do not use it to justify removing information |

The general rule behind this table: **a claim that circulates without an origin is a claim with no origin.** Popularity is not provenance.

## How merged dossier claims are marked

The deep-dossier sections merged into the references (2026-08-06) mark every claim. Respect the
markers when quoting, and carry the marker forward into any deliverable.

- `[verified]` — the page was fetched and read.
- `[search-level]` — taken from a search-result summary only; re-check before client-facing use.
- `[illustrative]` — an invented number that makes arithmetic followable. Never publish it.
- `[UNVERIFIED - ...]` — a named gap, with what is missing and what would close it.
- Inline `(source: URL, retrieved YYYY-MM-DD)` for external facts; physics and arithmetic show
  their derivation instead.

Retrieval date across the dossier sections: 2026-07-29. No adversarial verification pass has run
over them — treat an unmarked claim as unverified, not verified-by-omission. Three topics have no
deep dossier at all (campaign/channel architecture, optics and lens, brand identity systems);
the working references cover them and the deep evidence audit does not exist.
