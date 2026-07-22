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

