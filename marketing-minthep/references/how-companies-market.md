# How Companies Actually Market

## Contents

- What this unit is for
- Read the filing, not the case study
- What the biggest advertisers actually disclose
- Four operating models, from the companies' own words
- The artifact that travels: press release first, budget second
- What an ordinary business does instead
- Viet Nam: the channel the reports omit
- Benchmarks, and why one is never enough
- The laws, and the honest size of what they claim
- Applying this to a brief

## What this unit is for

Every other unit in this skill assumes a marketer. This one is about what marketing looks like inside
real organisations — the artifacts they write, the structures they run, the money they admit to, and the
gap between all of that and what a small shop actually does on a Monday morning.

It exists because the two most common failures in this work are opposite and both expensive. Building an
enterprise plan for a shop owner produces a document nobody can execute. Building a shop plan for an
enterprise produces a document nobody can approve. Telling them apart requires knowing how each one
really operates, and most published material about "how great brands do marketing" is a case study
written by the agency that sold the work.

Numbers live in `data/marketing-benchmarks.csv`, one row per claim, each carrying its source URL, how the
source was actually reached, an `evidence_grade`, and a `what_it_does_not_establish` column that is the
most useful field in the table. Source accessibility lives in `data/market-data-sources.csv`.
`market-data-collection.md` covers how to collect a number; this unit covers what other people's numbers
mean.

## Read the filing, not the case study

A listed company tells a regulator what it spent, under penalty, on a schedule. It tells a conference
whatever helps. So the hierarchy of evidence about marketing practice is:

1. **Regulatory filing.** 10-K, 20-F, annual report. Numbers and structural descriptions.
2. **The company's own operating documentation.** Shareholder letters, engineering blogs, careers pages
   describing a role. Self-serving, but at least first-hand.
3. **Peer-reviewed research.** Slow, narrow, and usually paywalled — but it states its sample.
4. **Industry survey.** Self-reported, sample-dependent, useful only when quoted with its sample size.
5. **Trade press and award case studies.** Written by the seller about the sale. Vocabulary, not evidence.

`data.sec.gov` is the highest-yield endpoint available for tier 1: one request to the XBRL
company-concept API returns the figure, the fiscal period, the form type, the filing date and the
accession number, and it exposes restatements for free. The tag varies by filer, and IFRS filers do not
use one at all, so a 20-F has to be read as HTML.

Two traps found by actually doing this. First, the same figure differs between filings: Coca-Cola's FY2024
10-K put 2024 advertising at 5.0bn USD and the FY2025 filing restates it at 5.1bn. Cite the filing, not
just the year. Second, a corporate newsroom is usually a JavaScript application where a missing page and
a real page return byte-identical responses, so "I found it on their newsroom" often means nothing was
found at all.

## What the biggest advertisers actually disclose

| Company | Line as the company names it | FY | Figure |
|---|---|---|---|
| P&G | Advertising costs | 2025 | 9.2bn USD |
| Unilever | Brand and marketing investment | 2025 | 8,142m EUR, 16.1% of turnover |
| Coca-Cola | Advertising costs | 2025 | 5.4bn USD |
| Nike | Demand creation expense | 2026 | 4,754m USD |

The names are the lesson. These are four different quantities, and using them interchangeably is the most
common error in a competitive-spend slide.

- **P&G's advertising line excludes** consumer promotions, product sampling and sales aids. The filing
  says so. So 9.2bn is a floor, and the missing money is exactly the promotional spend most decks forget.
- **Unilever's BMI includes** media, advertising production, promotional materials and consumer
  engagement — the widest definition of the four, and the only one published as a share of turnover.
- **Nike's demand creation is brand marketing plus sports marketing**, so endorsement contracts and
  complimentary product sit in the same number as media. Nike gives no split. Nike also *capitalises*
  prepaid demand creation, 1,438m USD at FY2026 year end, which is the only public evidence of marketing
  money sitting on a balance sheet rather than an income statement.

The one figure worth internalising: **16.1% of turnover.** That is what a serious FMCG advertiser
actually spends, disclosed, restated, audited. It is well above every survey benchmark in
`marketing-benchmarks.csv`, which is a useful thing to know before quoting a survey at a client who wants
to grow a brand.

## Four operating models, from the companies' own words

**P&G — brand management as general management.** P&G says it invented brand management in 1931 "to
drive a single point of accountability for the brands at the center of the business model," and describes
three brand disciplines: Consumer & Market Knowledge, Communications, and Design. Take the correction
with the claim: the FY2025 10-K puts *direct profit responsibility* at Sector Business Unit level, not at
brand level. The brand manager is accountable, not the P&L owner. The transferable part is the three
disciplines — separating market knowledge, communications and design as distinct crafts under one
accountability is a structure a ten-person company can copy.

**Coca-Cola — category-led, geography-executed, with a marketing shared service.** The 10-K describes
operating units doing regional and local execution, working with "global marketing category leadership
teams," and a "platform services organization" providing scaled global services including data
management, consumer analytics, digital commerce and social/digital hubs. This is the rare primary
description of a marketing operating model. Read it as an answer to the question every scaling company
asks: what stays central? Coca-Cola's answer is *category strategy and analytics infrastructure*, while
local execution stays local.

**Nike — marketing as a named turnaround lever.** The FY2026 10-K lists "Brand Management" as a
turnaround action: increasing investment in demand creation to support key product launches and sports
moments. What is absent is as informative: the filing contains no occurrence of "operating model" or
"marketing organi*". Nike describes marketing as spend and calendar, not as structure.

**Spotify — decisions as experiments.** Spotify's engineering blog states that "almost all product
decisions are made with some input from one or more A/B tests," and documents the governance that makes
that possible: experiments grouped into domains mapped to product surfaces, with exclusivity rules so a
user cannot land in two interacting experiments at once. That second part is the transferable one. Anyone
can run an A/B test; the thing that makes results trustworthy is a register of what else is running.

A warning about the fourth model. The famous "squads and tribes" paper is not published by Spotify, and
Spotify's own engineering posts do not describe marketing squads. Do not attribute agile marketing
structures to Spotify.

## The artifact that travels: press release first, budget second

Amazon's 2017 shareholder letter: "We don't do PowerPoint (or any other slide-oriented) presentations at
Amazon. Instead, we write narratively structured six-page memos. We silently read one at the beginning of
each meeting in a kind of 'study hall.'"

AWS documents the related but separate artifact: before requesting a budget, assembling a team or writing
code, write the press release for the finished product — and it must fit on **one page**. The FAQ comes
in two halves: customer questions first (what happens when it breaks, will my data be secure, why choose
this over the alternative), then internal questions (will it be profitable, might it cannibalise other
products, do we have the resources).

Two corrections worth carrying, because almost every retelling gets them wrong:

- The six-page memo and the press release are **different documents**. There is no "six-page PR/FAQ" in
  Amazon's own words: the memo is six pages, the press release is one.
- Amazon describes this as **product management**, not marketing. The reason it belongs in a marketing
  skill anyway is the sequence: the customer-facing announcement is written before the money is
  committed, so a proposition that cannot be announced clearly is stopped before it is funded.

That sequence is the single most portable practice in this unit, and it costs nothing. For any brief:
write the one-page announcement first. If the announcement is boring, the product is boring, and no
amount of media weight fixes that.

## What an ordinary business does instead

Almost nothing above applies to a business with no marketing function. Naming that honestly is more
useful than a downgraded enterprise plan.

What the evidence supports: **survey benchmarks do not transfer.** The CMO Survey's 9.0%-of-revenue
figure comes from 308 US marketing leaders, 97% of them VP or above. The same report shows small firms
running much higher — 13.7% of budget for firms under 10m USD revenue — which already tells you the
number is a function of size, not a standard. A single-owner shop has no marketing budget line at all, so
a percentage benchmark has nothing to attach to.

What the evidence does **not** support, stated plainly because it is tempting: the familiar claims that
small businesses run on word of mouth, do not measure anything, and have the owner doing the marketing
personally are, on this research pass, **unsourced**. They may well be true. No primary survey data was
obtainable for any of them. So do not put them in a deck as findings. Ask the owner instead — one
conversation with the actual business beats a statistic nobody can produce.

What *is* citable for the small end, and directly useful:

- **Average order value in Vietnamese video commerce is 5.5 to 7 USD.** That single figure caps
  everything. At roughly 6 USD an order, before goods cost, any tactic that needs more than about a
  dollar of work per order is underwater. This is the arithmetic that decides whether a small seller
  should be doing paid acquisition at all.
- **Seller count and transaction volume both grew about 60% year on year** in Vietnamese video commerce —
  in lockstep. There is no per-seller productivity gain in that data. Growth came from more sellers, not
  better sellers.
- **Marketplace take-rates are rising.** Fee increases across Shopee and TikTok Shop through 2026 are a
  live margin problem, which means a plan built on last year's fee schedule is already wrong.

## Viet Nam: the channel the reports omit

**Zalo is absent from every Western-sourced Vietnam deck**, because it publishes no ad-planning API and so
never appears in DataReportal-style summaries. It is a real product with published pricing, and the
pricing is the strategy:

- Official Account tiers: Basic (free, 3 seats), Standard (1,000,000 VND/year, 5 seats, positioned for
  household and small business), Growth (2,500,000 VND/year, 15 seats, chatbot and API), Comprehensive
  (6,000,000 VND/year, 100 seats).
- **Free broadcast: 4 messages per follower per month — on Growth and Comprehensive only.** Basic and
  Standard get zero.
- A **48-hour customer-service window**, after which replies are metered and then billed per message.
  Two-way messaging is permitted only with users who have already interacted with the account.
- Template messages: 200 VND each, 300 VND for authentication, payment-request and voucher classes. First
  call-to-action button free, each additional one 100 VND.

Put those together and most published Zalo playbooks are wrong for the tier a small shop can afford: the
plan they will buy cannot broadcast at all. A Zalo strategy for a small business is therefore a
*conversation* strategy inside the 48-hour window plus paid template messages costed per order — not a
newsletter.

Three more Viet Nam facts that change what a plan may claim:

- **Two credible market sizes, both for 2025 ecommerce: 25bn USD (e-Conomy SEA) and 38.5bn USD (VECOM).**
  Different scope definitions, published seven months apart. Carry both with their scope. Never average
  them, and never cite one as confirming the other. VECOM's more interesting finding is that its 21%
  growth is the lowest of the past decade.
- **Provinces went from 63 to 34** in the 2025 administrative merger. Any province-level benchmark,
  territory plan or regional split built before 2026 is structurally stale.
- **The legal layer moved up a level.** Ecommerce is now governed by Law 122/2025/QH15 with Decree
  248/2026/ND-CP, not the earlier decree alone; Decree 13/2023/ND-CP on personal data protection is in
  force from 1 July 2023 and applies extraterritorially. The live compliance pressure on Vietnamese
  household businesses in 2026 is the tax and e-invoicing wave, not advertising law. Read the instrument
  on `congbao.chinhphu.vn`, and navigate by document id — its search box is client-side and returns the
  newest-documents list whatever you type.

Platform reach figures deserve one more warning. Facebook's reported Vietnam ad reach of 76.2m exceeds
the adult population, because it counts addressable ad accounts. TikTok's reported reach fell 39.7% year
on year, which is a platform restating its own planner methodology, not usage declining. Never divide an
ad-reach number by a population figure and call the result penetration.

## Benchmarks, and why one is never enough

The CMO Survey puts marketing at 9.0% of revenue. Gartner puts it at 7.8%. Both are 2026, both are
credible, and they disagree because they sample different universes and word the question differently.

That gap is the finding. **Any percent-of-revenue benchmark carries roughly 1.5 points of sampling slack
before anything real is measured.** So quote two or quote none, and never present a single survey number
as an industry standard. The CMO Survey series makes the same point on its own: 9.8% in Aug-21, 13.8% in
Sept-22, 9.6% in 2026. That is volatility, not a direction of travel.

Three more numbers from the same source that are worth more than the headline:

- **Acquisition budgets exceed retention budgets by 26.0%**, and 82% of firms spend more on acquisition —
  while 43.7% name loyalty and retention as their main response to economic uncertainty. The report
  contains its own contradiction, and the gap has widened from 14.7% in 2022. Useful in any plan review:
  ask which of the two statements the budget agrees with.
- **33.6% of digital marketing activity is outsourced**, up from 31.6% in 2022. In-housing has not won.
- **Self-rated ability to demonstrate marketing ROI is about 4.4 out of 7**, and no martech capability in
  the battery scores above 5. Attribution is unsolved at firms far better resourced than most clients.
  Plan for a decision rule that survives imperfect attribution rather than promising to fix it.

## The laws, and the honest size of what they claim

The empirical-generalisation literature is the best-founded body of knowledge in marketing, and it is
routinely overstated by people quoting it. Hold each claim to what its own source says.

- **Double jeopardy** — smaller brands have both fewer buyers *and* less loyal buyers. Ehrenberg,
  Goodhardt and Barwise, 1990. Their own abstract covers "known exceptions and deviations." Use it to
  stop a client chasing loyalty while penetration is flat, then go looking for the exception, because a
  brand that violates the law is the interesting case.
- **Brand salience is not awareness** — Romaniuk and Sharp define it as the brand's propensity to be
  noticed or come to mind in buying situations. It is a conceptual and measurement paper with no effect
  size. It is enough to reject an awareness percentage as a brand metric; it is not enough to promise
  what salience is worth.
- **Advertising elasticity: 0.12 short-term, 0.24 long-term** — Sethuraman, Tellis and Briesch, 2011,
  meta-analysis of 751 short-term and 402 long-term elasticities from 56 studies. The strongest available
  caution against planning constants is inside this paper: the previously accepted mean from the same
  literature was 0.22, nearly double. A benchmark the field trusted was wrong by 100% for years.
  Elasticity also varies by durability, life-cycle stage, data frequency and whether advertising was
  measured in GRPs or money, and it is declining over time.
- **95:5** — up to 95% of business buyers are not in the market at any one time. The author calls it a
  heuristic in the article itself, derived from an asserted five-year repurchase cycle. It is wrong for
  fast-cycle categories. Derive your own from your own purchase cycle.
- **60:40 brand to activation** — attributed to Binet and Field. It appears on no accessible IPA page;
  the reports are paid, and the ratio was not verified here. It is graded `unverified-claim` in the table
  for that reason. When citing it, say what it is: an average across self-selected effectiveness-award
  entries — campaigns submitted to a competition, i.e. survivors — which cannot tell one brand which side
  of the average it sits on.
- **Light buyers dominate volume** — the argument is published and sound; the statistic is not on the open
  web. Ehrenberg-Bass's own pages refer the reader to the books. Do not attach a Pareto figure you cannot
  open.

The pattern across all six: the argument is usually free and the evidence is usually paid. Quote the
argument, and either buy the evidence or measure your own.

## Applying this to a brief

1. **Classify the organisation before choosing a method.** Does it have a marketing function, a budget
   line, and someone whose job this is? If not, every benchmark in this unit is context, not a target.
2. **Write the one-page announcement first**, before the budget, the channel plan or the creative. If it
   is boring, stop.
3. **Take structure from the filings, not the case studies.** What stays central, what executes locally,
   and which crafts are separated — those three answers are the operating model.
4. **Quote two benchmarks or none**, always with sample size, and always with what the source does not
   establish. `data/marketing-benchmarks.csv` carries that column for exactly this purpose.
5. **Cost the channel at the unit economics of the market.** At a 6 USD average order, a Vietnamese live
   seller's plan is decided by arithmetic, not by best practice.
6. **State what you could not verify.** A plan that names its gaps is auditable. A plan that is uniformly
   confident is not, and the unverified parts are exactly where it will fail.
