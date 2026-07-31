# Campaign Learning Loop

Treat results as evidence about a hypothesis, not a vote on visual taste.

## Minimum performance record

Capture:

- Asset ID, lane, hook, proof type, channel, audience, offer, and date range.
- Spend, impressions, clicks, three-second views or equivalent, conversions, and revenue when available.
- Landing-page version and conversion event definition.
- Any targeting, bid, placement, or offer differences that confound creative comparison.

## Derived metrics

Calculate only when denominators exist:

- CTR = clicks / impressions.
- Three-second view rate = three-second views / impressions.
- CVR = conversions / clicks.
- CPA = spend / conversions.
- ROAS = revenue / spend.

Never compare percentages without reporting sample size. Never declare a winner from tiny or materially unequal delivery.

## What tiny means

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

## Diagnosis matrix

| Pattern | Likely signal | Next creative action |
|---|---|---|
| High view rate, low CTR | Hook works; promise or relevance weak | Clarify product role and next step |
| High CTR, low CVR | Ad promise, offer, audience, or landing continuity problem | Audit message match and proof |
| Low view rate, high CVR | Strong for qualified users; weak first frame | Preserve proof, test new hook |
| Good CVR, poor CPA | Economics or delivery issue may dominate | Do not blame creative alone |
| Saves/comments high, purchase low | Cultural or educational value without buying urgency | Add mechanism, proof, offer |

## Learning record

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

## Promotion to Brand DNA

Promote a learning into `BRAND.md` only when:

- It repeats across more than one meaningful test.
- The effect is not explained by offer, targeting, seasonality, or placement.
- The rule describes durable audience or brand behavior rather than one asset.

Use `scripts/analyze_performance.py` for a factual ranking report. Interpret causality cautiously.

