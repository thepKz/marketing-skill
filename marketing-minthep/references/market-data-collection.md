# Market Data Collection

## Contents

- What this unit is for
- The four measurement families
- Triangulation that actually triangulates
- The three Vietnamese biases
- The renamed-institution trap
- Access tiers and how to record them
- Bottom-up sizing
- Sample size and what a difference has to beat
- Collection log template

## What this unit is for

Finding sources is not the hard part. `data/market-data-sources.csv` lists twenty-three of them with
verified status. The hard part is that the cheapest and most-cited sources measure something
different from what the deck says they measure, and the gap is largest in exactly the market this
skill is most often pointed at.

Load this before `market-assessment.md` when the question is *where do the numbers come from*. Load
`research-protocol.md` for the search procedure and `source-map.md` for creative and craft sources.
This unit is about the numbers and their provenance.

## The four measurement families

Every source belongs to one. The family determines what it can be wrong about.

| Family | What it does | Systematically wrong about |
|---|---|---|
| Official statistic | Counts the economy through census, survey and administrative records | Your product. It has no brand, intent or channel variables |
| Panel | Recruits people, then measures them repeatedly | Who it recruited. Every online panel skews urban, younger, higher-income, more connected |
| Behavioural trace | Records what happened — receipts, scans, listings, search, clicks | What happened somewhere it cannot see |
| Platform self-report | Restates a platform's own commercial estimate of its own inventory | Its own size, in the direction that sells advertising |

## Triangulation that actually triangulates

`research-protocol.md` requires at least three sources from different categories. Tighten that: the
three must come from **different families in the table above**. Three listening vendors are not three
sources; they index overlapping public text and inherit one blindness. DataReportal, a Meta planner
screenshot and a social-listening share-of-voice chart are all downstream of platform self-report,
so agreement between them is not corroboration — it is the same number arriving three times.

The test is mechanical: for each source, name the family. If two of the three share a family,
replace one before you draw a conclusion.

When the families disagree, that is the finding, not a problem to average away. A category where
listening shows silence and marketplace trace shows volume is a category selling in closed channels.
Averaging the two destroys the only useful thing the contradiction told you.

## The three Vietnamese biases

These are the errors that survive into finished decks, in descending order of frequency.

**1. Ad reach quoted as penetration.** The headline social figures in the annual digital reports are
advertising-audience sizes read out of each platform's own campaign planner. They count addressable
ad accounts — including duplicates, dormant accounts, bots, and users whose stated age band is
unverified — with no deduplication across platforms. Dividing that numerator by an official
population denominator produces a percentage whose two halves come from different universes.
Platform ad-reach totals for Viet Nam have at times exceeded the plausible online population of the
relevant age band, which is arithmetically impossible for a penetration figure and unremarkable for
an account count.

Write it as what it is: *addressable ad accounts, platform-reported, month and year*. Never as
*percent of Vietnamese*.

**2. Listening silence read as absence of demand.** Social listening indexes public, indexed,
machine-readable text. Vietnamese purchase conversation concentrates in closed Zalo groups, private
and secret Facebook groups, livestream comment streams, direct messages, and text baked into images
— none of which enter the index. The under-count is not random noise. It falls hardest on the
closed and live channels with the shortest path to a sale, so listening data is biased *against*
exactly the channels worth finding. Treat a quiet channel as unmeasured until a second family says
otherwise.

**3. Marketplace inference read as category size.** Marketplace trackers scrape listing data and
infer revenue from displayed sold and review counts. Those counts are seller-influenceable, the
inferred figure is gross rather than net, and the scrape cannot see direct sales through Zalo,
Facebook and livestream, which is a large share of Vietnamese small-retail revenue. Marketplace data
is strong evidence about the price ladder and the assortment on that marketplace, and weak evidence
about the category.

## The renamed-institution trap

Two of the most-cited Vietnamese government hosts no longer resolve. Checked 2026-07-30:

| Cited host | Status | Where the function went |
|---|---|---|
| `gso.gov.vn` | Does not resolve | National Statistics Office, `nso.gov.vn` |
| `mic.gov.vn` | Does not resolve | Merged into the Ministry of Science and Technology, `mst.gov.vn` |

A citation to a dead host is a reliable tell that nobody opened it. When an institution is renamed
or merged, individual table URLs move too, and tables are sometimes dropped rather than carried
over. Re-verify the specific table, not just the new homepage, and record the date you did it.

The general rule this stands for: **any URL in a deck older than a year is a hypothesis.** Check
status before citing. A 403 means the source is alive and blocking automated access, which is a
different problem from a dead domain and has a different fix — open a browser session.

## Access tiers and how to record them

Record the HTTP status and the date, because it is reproducible and a reader can re-run it.

| Tier | Signal | What to do |
|---|---|---|
| open | 200 to a plain request | Cite with the retrieval date |
| rate-limited | 429 | Alive. Back off and retry; do not conclude it is broken |
| browser-required | 403 | Alive and blocking automation. Use a browser session |
| intermittent | 5xx | Alive but unreliable. Secure a fallback source before you depend on it |
| dead | 000, no resolution | Find where the function moved. Do not cite |

## Bottom-up sizing

Platform reach numbers cannot size a market. This chain can, because every term is separately
checkable and separately arguable:

```text
households or people in scope      <- official statistic, with province and age band stated
  x  incidence of the need         <- panel or survey, with n and fielding date
  x  purchase frequency per year   <- purchase panel or receipt trace
  x  realistic price paid          <- marketplace price ladder, not list price
  =  category value in scope
  x  reachable share               <- your distribution and media footprint, not the total market
  =  addressable value
```

Two disciplines make this honest. First, pull each term from a different family and label which one,
so the weakest link is visible rather than buried in a single confident total. Second, carry a range
rather than a point: state each term as low and high, multiply the lows and multiply the highs. A
five-term chain where each term is comfortably within a factor of 1.3 produces a top-to-bottom spread
of roughly 1.3^5, about 3.7x. That spread is the actual state of your knowledge. A single number is a
claim to precision the inputs cannot support, and the range is usually the more persuasive slide
because it survives the first challenge.

## Sample size and what a difference has to beat

Vietnamese free panel reports commonly field a few hundred respondents. At 95% confidence the
half-width of a proportion near 50% is `1.96 x sqrt(0.25 / n)`:

| n | Margin of error | A reported gap smaller than this is noise |
|---|---|---|
| 300 | 5.7 points | 5.7 |
| 500 | 4.4 points | 4.4 |
| 1000 | 3.1 points | 3.1 |
| 2000 | 2.2 points | 2.2 |

Two independent proportions from the same survey need roughly `1.4x` the single-sample margin before
the difference is defensible, because both carry error. At n = 300 that is about 8 points.

Most brand-tracking movements argued over in review meetings — "we went from 31% to 34%" — sit inside
the noise band of the survey that produced them. Before treating a movement as real, check n, check
the fielding window, and check whether the question wording changed. A wording change between waves
makes the comparison invalid at any sample size.

## Collection log template

Extends the `source-map.md` template with the fields that make a number auditable:

```text
Claim being supported:
Source and URL:
Measurement family:        [official | panel | behavioural trace | platform self-report]
Access tier and status:    [200 / 403 / 000, date checked]
What it literally measures:
Population or universe:    [who is in it, who is excluded]
n and fielding window:     [surveys and panels only]
Known blind spot:
Restated honestly as:
Second family confirming:
Where the families disagree:
```

The last two lines are the ones that get skipped and the ones that carry the value. A claim with no
second family behind it goes into the deck labelled as single-source, or it does not go in.
