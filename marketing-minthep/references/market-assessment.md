# Market Assessment

## Contents

- What this unit decides
- A sizing answers a threshold, not a question
- The chain, and the term everybody drops
- A range narrower than its own sampling error
- Where the uncertainty lives decides what to research next
- The centre of a multiplicative chain is not its average
- The alternatives that are not competitors
- A price ladder is evidence and a price list is a wish
- Whitespace is usually empty for a reason
- The Vietnamese denominators that moved
- What the deliverable has to contain
- What this unit cannot establish
- The handoff

## What this unit decides

Whether a market is attractive enough for a stated objective, for whom, and under what conditions.
That is a decision, not a document, and the difference shows up in one place. A decision has a number
that flips it.

Load `market-data-collection.md` first when the question is where the numbers come from. This unit is
about what to do with them once you have them, and its instrument is `scripts/size_market.py`.

```
python scripts/size_market.py --template chain.csv
python scripts/size_market.py --check chain.csv --threshold <the value that flips your decision>
```

The script refuses to total a chain whose terms have no evidence behind them. That refusal is the
whole contribution. An unsupported total is indistinguishable from a supported one once it reaches a
slide.

## A sizing answers a threshold, not a question

"How big is the market" has no answer that anybody can act on. Every real version of the question is a
threshold: is this worth a year of my attention, does it clear the revenue the investor was promised,
can it carry two salaries. Name the threshold before you multiply anything.

Then the arithmetic has a job. It is not producing a number to admire. It is deciding whether the
threshold sits inside your range or outside it.

Outside, and the research is over — no further precision can change the answer. Inside, and you have
learned that you do not yet know, which is a finding and should be written down as one.

`--threshold` prints that verdict. It also names which terms would settle the question on their own,
by collapsing each to its centre and multiplying again. Terms it does not name are terms where more
research cannot change the outcome, however interesting they are.

One case deserves its own sentence. A threshold sitting exactly on the centre of your own estimate can
never be settled by narrowing a single term, because collapsing any term to its centre leaves the
total's centre where it was. That is not a limitation of the script. It means the decision is balanced
on your own guess, and no amount of desk research is going to unbalance it.

## The chain, and the term everybody drops

```text
people or households in scope   <- official statistic, province and age band stated
  x  incidence of the need      <- panel or survey, with n and fielding date
  x  purchases per year         <- purchase panel or receipt trace
  x  price actually paid        <- observed ladder, not list price
  =  category value in scope
  x  reachable share            <- your distribution and media footprint
  =  addressable value
```

Frequency is the term that goes missing. It feels like a detail next to population and price, so it
gets folded into an assumption and disappears.

A chain with no frequency term has not skipped that step. It set it to one. And it is now asserting
that every buyer in the market buys exactly once a year, which is not a thing anybody would say out
loud. The script refuses it.

The last multiplication is the one to defend hardest. Category value is a fact about the world and
addressable value is a claim about you, and only the second is something a plan can be held to.

## A range narrower than its own sampling error

This is the defect that looks like diligence. Somebody reads 41 percent off a panel report, enters 40
to 42 as the range, and the tightness reads as care. At n = 300 the 95 percent half-width on a
proportion is 5.7 points, so a band of one point is roughly a fifth of the uncertainty already sitting
inside the number they copied.

| n | 95% half-width | A gap between two of its own numbers must beat |
|---|---|---|
| 300 | 5.7 points | 8.0 points |
| 500 | 4.4 points | 6.2 points |
| 1000 | 3.1 points | 4.4 points |
| 2000 | 2.2 points | 3.1 points |

The right column is wider because two proportions from one survey both carry error, which costs about
a factor of 1.4. Run `python scripts/size_market.py --margin 300` for any n. The gate is
`survey-range-beats-its-own-margin`. On real work it fires most.

## Where the uncertainty lives decides what to research next

The chain multiplies, so the spreads multiply too. A term's share of the total spread is its log ratio
over the total log ratio, and the script prints that share against every row.

Read the largest one before planning any more research. It is usually not the term the team has been
arguing about, because arguments settle on the term people have opinions about rather than the term
carrying the doubt. Reachable share is the usual culprit. Nobody owns it.

## The centre of a multiplicative chain is not its average

Multiply the lows for the bottom, multiply the highs for the top, and take the geometric mean of those
two products for the middle. Not their average.

A product is symmetric in log space and not in linear space, so the arithmetic midpoint of a chain's
low and high sits above the middle of the distribution. Use it and your base case is quietly an
optimistic case, by a margin that grows with every term. The script computes the geometric mean and
says so in the output, which is there to be read aloud when somebody asks why the base looks
conservative.

Five terms each comfortably within a factor of 1.3 compound to roughly 3.7x top to bottom. Real chains
run wider. That spread is not a failure of the research; it is the honest width of what you know, and
a single number is a claim to precision the inputs cannot support.

## The alternatives that are not competitors

Four things compete for the same money and only one of them shows up in a competitor slide.

- **Direct** — the same product from somebody else.
- **Indirect** — a different product solving the same problem.
- **Substitute** — the improvised version the customer already uses, usually free and usually good
  enough.
- **Do nothing** — the option that wins most often.

Do-nothing deserves the space the others get. It has no marketing, no price and no website, so there
is nothing to screenshot, and it is the incumbent in most categories a small business enters. Write
what the customer currently does instead of buying, and what specifically would have to change.

Compare on axes a switch actually turns on. Not feature counts: price paid, time to first value,
switching cost, trust, and who else the buyer has to convince.

## A price ladder is evidence and a price list is a wish

Collect prices paid, not prices asked. A marketplace listing with sold counts, a receipt, your own
transactions — those are traces. A rate card is a position in a negotiation.

Record the ladder with its ends attached. The ends are where the strategy lives. Cheapest and dearest
tell you what the market believes it is buying at each end, and the gap between them is the room a new
entrant has. A single average price destroys exactly that information.

Discounting is where a price becomes a margin problem, and that arithmetic belongs to
`scripts/price_offer.py`. Do not decide a promotional price in this unit.

## Whitespace is usually empty for a reason

A positioning gap is a hypothesis about why nobody is standing there. Three reasons cover most of
them, and only one is an opportunity: nobody has tried, somebody tried and the economics did not work,
or the demand was never there. Assume the second until evidence separates them.

The cheapest test is whether anybody used to occupy the space. A dead brand in the gap is the strongest
signal you will get for free.

## The Vietnamese denominators that moved

Two traps sit under every Vietnamese sizing chain. Both live in the denominator rather than in the
data, which is why neither one leaves a mark on the number it ruins.

**Provinces went from 63 to 34** in the 2025 administrative merger. Any province-level population,
household count or territory split taken from a pre-2026 table is describing units that no longer
exist, and the arithmetic will still run. See `how-companies-market.md` for the instrument.

**The statistics office moved.** `gso.gov.vn` no longer resolves; the National Statistics Office is at
`nso.gov.vn`. A citation to the dead host is a tell. Nobody opened the page.
`market-data-collection.md` carries the renamed-institution table and the access tiers.

And never build a denominator out of an advertising planner. Platform reach counts addressable ad
accounts, duplicates and dormant ones included, which is why `no-platform-self-report` is a critical
gate rather than a warning.

## What the deliverable has to contain

- The threshold, stated before the arithmetic, and the verdict against it.
- The chain as the script prints it, ranges and family labels intact.
- The dominant uncertainty term and what would narrow it.
- Direct, indirect, substitute and do-nothing alternatives, with do-nothing given real space.
- Competitor comparison on switching-relevant axes.
- The price ladder with its ends and the observed source of each.
- Positioning whitespace with a reason for the emptiness.
- Regulation, supply, seasonality and platform risks.
- What evidence would change the recommendation.

Numbers without a URL and a retrieval date are `inferred` or `unknown`. Never `confirmed`.

## What this unit cannot establish

It cannot tell you whether people will buy. A sizing chain measures how many could, how often they
might, and at what price others transact, and none of those is a willingness to buy from you.
`customer-evidence.md` is the unit for that, and its instrument refuses to print a share when nobody
was recorded disagreeing.

It also cannot price your offer or forecast a launch. Sizing bounds the prize. What you can win of it
in a quarter is a distribution question, not a market question.

## The handoff

A completed assessment hands three things forward: the addressable range to `marketing-foundation.md`,
the dominant uncertainty to whoever owns the next research hour, and the threshold verdict to whoever
asked. An unresolved verdict gets handed over in exactly those words. Not as a number.

That last one is how a plan acquires a foundation nobody can find later. Somebody needed a figure for a
slide, the range got averaged into one, and a year afterwards there is no way to tell whether the
market was ever big enough.
