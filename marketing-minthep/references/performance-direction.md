# Performance and Direction

`kpi-scorecards.md` reads a card that already exists — weights, achievement branches, caps, rank.
This file owns everything before and after that card: which metrics deserve to be on it, what
number the target is, how a finished period is judged, and what the next quarter does about it.
The arithmetic here is arithmetic; every threshold is `craft-heuristic` and says so.

## Contents

- Growth has three sources, and a KPI belongs to one
- From objective to metric
- Target arithmetic
- Reading a period
- Grow, hold, fix, kill
- The quarterly direction
- What this file cannot settle
- Campaign learning loop

## Growth has three sources, and a KPI belongs to one

Revenue moves through exactly three doors: more buyers, buying more often, paying more per order.
Every metric on a scorecard serves one of the three or guards one of them, and a metric that cannot
say which door it serves is decoration — engagement rate, follower count, and impressions all fail
this question until the plan states the door they are supposed to open. The default weighting
follows the canon (`marketing-canon.md`): penetration first, so the more-buyers door gets the
primary metric unless the business is subscription or repeat-purchase, where churn arithmetic
flips the priority to frequency.

## From objective to metric

Build the tree before picking the number: revenue splits into the three doors, each door splits
into what feeds it (buyers = qualified reach × conversion; frequency = repurchase rate × cycle
time; order value = price × attach rate). Then pick the *weakest link the business can actually
influence this quarter* — not the metric that is easiest to report, and not one per branch out of
symmetry. A shop whose conversion is fine and whose reach is starving does not need a CRO metric
this quarter.

Three constraints on the pick:

1. Every chosen metric must exist as a row in `data/kpi-metrics.csv`, and its `trap` column is read
   aloud at selection time — choosing a metric means choosing the way it will be gamed.
2. One primary metric per objective, at most five on the whole card, plus guardrails
   (`kpi-scorecards.md` carries the weighting mechanics). A card with nine primaries has none.
3. Whether the number can be measured at all is settled first in `measurement-plan.md` — a KPI
   without a tracking event is a hope with a deadline.

## Target arithmetic

Never accept a bare target, including one the client supplies with confidence. A target is an
arithmetic claim, and it is built in three steps:

1. **Baseline.** The metric's current value over a comparable period, with provenance. No baseline,
   no percentage target — a new business writes absolute targets derived from capacity, not lifts
   from zero.
2. **Capacity.** What the unit economics allow: break-even CPA and contribution margin from
   `pricing-and-offers.md` cap every acquisition target; production capacity and stock cap every
   volume target. A target above capacity is a plan to fail in public.
3. **The lift, defended.** Target = baseline × (1 + lift), and the lift must be paid for by one of
   exactly three things: a removed constraint (a fixed landing page, a new channel), added spend at
   a known unit cost, or a benchmark range quoted under the two-source rule in
   `how-companies-market.md`. A lift defended by ambition alone is renegotiated before it is
   printed.

Write the target as a range — the sampling slack that `how-companies-market.md` documents in
benchmark surveys applies to internal numbers too. A point target of 12.0% pretends to a precision
the tracking stack does not have; 11–13% is honest and equally actionable. Targets and actuals both
carry provenance on the card (`kpi-scorecards.md` already refuses them without it).

## Reading a period

A period readout compares against three things at once, because each comparison catches a lie the
others miss: against **target** (was the plan met), against the **previous period** (which way is
it moving), and against the **same period last year** (or the same position in the purchase
calendar). In Vietnam the third axis is not optional — Tết distorts January and February in both
directions, the double-day promotions (9/9 through 12/12) spike the fourth quarter, and the rain
season moves delivery F&B — so a May-over-April comparison that ignores the calendar reads
seasonality as performance.

Decompose a miss before explaining it. Volume (fewer buyers than planned), efficiency (buyers cost
more than planned), and mix (the cheap segment grew, the profitable one did not) are three
different failures with three different owners, and a readout that reports only the blended number
has diagnosed nothing. `scripts/build_variance_report.py` produces the factual layer;
`scripts/score_kpi.py` scores the card; neither one is the verdict, which is the reading against
brief and calendar.

Two honesty rules. A single period is a data point, not a trend — direction claims need three
points, and the `Campaign learning loop` section below owns the arithmetic of when a difference is real. And attribution
is imperfect at every company, including well-resourced ones (`how-companies-market.md` carries the
survey evidence), so the readout states which numbers are platform-reported, which are measured on
owned infrastructure, and which are modelled — and never silently mixes the three.

## Grow, hold, fix, kill

The readout becomes direction one cell at a time: each channel-offer pair gets exactly one of four
verdicts, and the verdict is arithmetic plus trend, not affection.

| Verdict | Condition | The move |
|---|---|---|
| Grow | Efficiency clears break-even with room, trend flat or improving, headroom exists | Add budget in steps small enough to detect saturation |
| Hold | At break-even or at capacity; stable | Maintain, and stop attending its meetings |
| Fix | Efficiency worsening, but the diagnosis matrix names a repairable cause | Repair named cause, re-read next period, one fix at a time |
| Kill | Below break-even across three periods with no named repairable cause | Stop, and move the budget to a Grow cell the same week |

The diagnosis that separates Fix from Kill lives in the `Campaign learning loop` diagnosis matrix below — a cell with high view
rates and dead conversion has a message-match problem worth fixing; a cell nobody can diagnose
after three periods is not mysterious, it is answered. Killing is the point of the exercise: a
readout that never kills anything funds every future failure at the expense of every current
success.

## The quarterly direction

"Phương hướng phát triển" is three bets, not a channel list. A direction document that assigns
"tăng cường" to every existing channel has decided nothing — it is a wish list wearing a plan's
clothes, and the canon rule applies: strategy is what you refuse (`marketing-canon.md`). The
quarter gets at most three moves:

1. **One growth bet** — the largest Grow cell, or a new door from the driver tree, funded by
   whatever Kill freed up.
2. **One efficiency fix** — the single Fix cell with the clearest diagnosis, not all of them.
3. **One experiment** — something the current mix cannot answer, sized by
   `scripts/check_test_readout.py --plan` before a dong is spent.

Each bet is written with a hypothesis, a budget, a kill criterion, and a decision date — the same
discipline the `Campaign learning loop` section demands of a creative test, applied to the quarter itself. Below the
three bets, the direction names its refusals: the channels deliberately not entered, the segments
deliberately not chased, the growth deliberately deferred, each with the evidence that would
reverse it. A reader should be able to tell the next quarter's plan from the last one's by what it
declines to do.

## What this file cannot settle

Incrementality — whether the sale would have happened without the spend — is not answerable from a
scorecard, only from a holdout or geo test, and pretending otherwise is the polite name for
double-counting. Brand effects that mature past the quarter boundary are real and will not appear
in these readouts; the canon's emotion-and-reason rule does not become false because the quarter
cannot see it. And no verdict table survives a business whose product is broken —
`marketing-canon.md`'s bucket check runs before any of this, because direction-setting for a
leaking bucket is choreography.

## Campaign learning loop

Treat results as evidence about a hypothesis, not a vote on visual taste.

### Minimum performance record

Capture:

- Asset ID, lane, hook, proof type, channel, audience, offer, and date range.
- Spend, impressions, clicks, three-second views or equivalent, conversions, and revenue when available.
- Landing-page version and conversion event definition.
- Any targeting, bid, placement, or offer differences that confound creative comparison.

### Derived metrics

Calculate only when denominators exist:

- CTR = clicks / impressions.
- Three-second view rate = three-second views / impressions.
- CVR = conversions / clicks.
- CPA = spend / conversions.
- ROAS = revenue / spend.

Never compare percentages without reporting sample size. Never declare a winner from tiny or materially unequal delivery.

### What tiny means

That rule was decoration until it had arithmetic behind it, because nobody can tell from reading it
whether their own test is tiny. Tiny is not a number anyone picks. It falls out of two things: the rate
you are starting from, and the size of the lift that would actually change a decision. At a 3 percent
conversion rate, detecting a 20 percent relative lift needs roughly fourteen thousand clicks per arm.
At 20 percent it needs about nine thousand for half that lift. Those are not opinions and they are not
adjustable by wanting the answer sooner.

```
python scripts/check_test_readout.py --plan --baseline 0.03 --mde 0.30 --daily-clicks 500
python scripts/check_test_readout.py --variant "A:clicks=400,conversions=8" \
    --variant "B:clicks=410,conversions=13" --claim B
python scripts/check_test_readout.py --self-check
```

`--plan` sizes a test before it runs, which is the only time the answer is cheap. `--claim` is the
one to reach for when somebody has already decided: it checks the claimed winner against the
confidence interval rather than against the point estimate, and returns exit 2 when the interval still
contains zero. Exit codes are 0 readable, 2 a gate failed or a claimed winner is unsupported, 3
computable but not readable yet.

Three things it will tell you that are worth hearing:

**A large relative lift is not evidence.** 8 conversions from 400 clicks against 13 from 410 is a 58
percent lift and p = 0.29. That is inside what this much traffic produces on its own. Relative lift is
the most quoted number in marketing reporting and the least informative one at small n, because the
denominator that makes it large is the same denominator that makes it unreliable.

**Significant on a small sample is worse than not significant.** If the test passes p < 0.05 before
reaching its planned size, the script says so and grades it `review`. Stopping there is what makes a
false positive permanent, because the winner then becomes a brand rule.

**Unequal delivery is a result, not a setup.** Arms more than 1.2x apart are confounded whichever way
they land: the platform has decided between them and is spending accordingly, so the split is now an
outcome of the thing being measured.

The complement is also a finding. No difference at adequate size means stop paying to produce the
variant that costs more to make, and that is a decision, not a null result.

### Diagnosis matrix

| Pattern | Likely signal | Next creative action |
|---|---|---|
| High view rate, low CTR | Hook works; promise or relevance weak | Clarify product role and next step |
| High CTR, low CVR | Ad promise, offer, audience, or landing continuity problem | Audit message match and proof |
| Low view rate, high CVR | Strong for qualified users; weak first frame | Preserve proof, test new hook |
| Good CVR, poor CPA | Economics or delivery issue may dominate | Do not blame creative alone |
| Saves/comments high, purchase low | Cultural or educational value without buying urgency | Add mechanism, proof, offer |

### Learning record

For every test, write:

```text
Hypothesis:
Primary variable:
Controlled variables:
Minimum evidence threshold:
Observed result:
Confounders:
What we learned:
Brand rule or campaign-only learning:
Next test:
```

### Promotion to Brand DNA

Promote a learning into `BRAND.md` only when:

- It repeats across more than one meaningful test.
- The effect is not explained by offer, targeting, seasonality, or placement.
- The rule describes durable audience or brand behavior rather than one asset.

Use `scripts/analyze_performance.py` for a factual ranking report. Interpret causality cautiously.
