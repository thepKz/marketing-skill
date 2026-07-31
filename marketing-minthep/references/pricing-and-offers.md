# Pricing and Offers

The arithmetic behind the word "offer" in `plan-from-zero`. All of it is one subtraction and one
division, and none of it is optional, because a promotion designed against the price lands on the margin
and those are not the same number.

## Contents

- The one number everything hangs off
- Why a discount costs more than it says
- Break-even ROAS replaces the ROAS target somebody gave you
- What a customer may cost
- Offer shapes that do not cut price
- Vietnam-specific costs that belong in variable cost
- Reject list

## The one number everything hangs off

Contribution per unit: price minus everything that scales with one unit sold. Not gross margin from the
accounts, and not "cost" as the supplier invoice states it. Variable cost has to include goods,
packaging, shipping, payment fees, platform commission and expected returns, because every one of those
scales with the unit and every one of them is routinely left out.

```
python scripts/price_offer.py --price 390000 --variable-cost 234000
```

Contribution as a ratio of price is the figure to carry into every other decision. Everything below is
that one number applied to a different question.

## Why a discount costs more than it says

Twenty percent off a price carrying forty percent contribution removes **half** the contribution. To
hold the same gross profit you need twice the units. Not twenty percent more. Twice.

```
python scripts/price_offer.py --price 390000 --variable-cost 234000 --discount 0.20
```

The general form: the volume multiple needed is contribution before divided by contribution after. The
consequence is that the same discount is a completely different decision at different margins - twenty
percent off a seventy percent margin needs 1.4x the units, which is a promotion; the same twenty percent
off a forty percent margin needs 2.0x, which is a business model change. Nobody running the sale
intended to set a doubled volume target, and that is exactly why it should be printed before the
campaign rather than discovered in the month-end.

Two things follow that are worth saying plainly. If the volume genuinely is available at the lower
price, then the lower price is the price, and calling it a promotion just means giving it away again
next quarter. And if the multiple is above 2, the script grades `review` rather than passing it, because
past that point the honest options are a different product cost, a different price, or not running it.

## Break-even ROAS replaces the ROAS target somebody gave you

Break-even ROAS is the reciprocal of the contribution ratio. At 40 percent contribution it is 2.5. So a
handed-down "hit 2.0 ROAS" target is loss-making on every sale it produces, and no amount of creative
work fixes that, because the target itself is below the floor.

This is the single most common way a campaign is judged against the wrong number. Compute the floor
first, then set a target above it, then talk about creative.

## What a customer may cost

Two ceilings, and they are different questions:

- **First-order break-even**: contribution per unit. Above this, the first order loses money.
- **Lifetime ceiling**: contribution times expected purchases divided by the required return on
  acquisition spend. The required return - 3x is the common convention - is a policy choice and the
  script labels it as one, not as a finding.

```
python scripts/price_offer.py --price 390000 --variable-cost 234000 \
    --repeat-purchases 2.5 --acquisition-cost 90000
```

Which ceiling binds depends on the numbers, and the script says which. At a demanding target return the
policy ceiling can sit *below* first-order break-even, so an acquisition cost can be profitable on order
one and still outside policy. That is the policy working, not an error, but somebody has to decide which
of the two is the real constraint before reading the gate.

Where the gap between the two ceilings is large, that entire gap is a bet that the repeat rate is real.
Spend into it only on repeat data from this product. A category average repeat rate is not evidence about
this shop, and `marketing-benchmarks.csv` exists to make that distinction visible rather than to supply
the number.

## Offer shapes that do not cut price

Price is the last lever, not the first, because it is the only one that is hard to take back - a
discount teaches the customer what the product is worth, and the next full-price week is competing with
the last discounted one. Cheaper levers, roughly in order of how much margin they cost:

- **Threshold offers.** Free shipping or a gift above a basket value set just above current average
  order value. Costs one variable line, raises the denominator on every other metric.
- **Bundles.** Two items at a combined price whose combined contribution is above one item's. Works
  when the second item has high margin and low incremental shipping.
- **Payment terms and timing.** Nothing off the price at all.
- **Volume tiers.** The discount is earned by the units that pay for it, which is the difference between
  a tier and a sale.
- **Guarantee or trial.** Costs the expected return rate, which belongs in variable cost anyway, so
  this is often the cheapest real risk-reversal available.
- **Straight percentage off.** Last. Compute the volume multiple first.

Run any of these through the same script: a bundle is a price and a variable cost, so it has a
contribution and a break-even like anything else.

## Vietnam-specific costs that belong in variable cost

Left out of a margin calculation, each of these turns a healthy-looking contribution into a negative
one, and all of them scale per unit:

- Marketplace commission and payment-gateway fees on Shopee, Lazada and TikTok Shop, which differ by
  category and by seller tier.
- Platform-subsidised shipping that the seller part-funds, and the shipping on the free-shipping
  voucher the platform applied without asking.
- COD failure and return-to-sender freight, which on cash-on-delivery is not a rare event and is paid
  in both directions.
- Livestream and affiliate commission, which is a variable cost of that channel and not a marketing
  overhead.

Get the current rate from the platform's own seller centre. `channel-spec-registry.md` carries the rule
that a rate is quoted from the live official source or not quoted at all, and commission tables move.

## Reject list

- A discount decided without printing the volume multiple it needs.
- A ROAS target used without the break-even ROAS beside it.
- Variable cost that excludes commission, payment fees, shipping or expected returns.
- A lifetime-value ceiling built on a category repeat rate rather than this product's.
- A repeat rate stated without saying where it came from.
- A percentage off chosen before the threshold, bundle and guarantee options were priced.
- "We'll make it up on volume" without the volume figure written down beforehand.
