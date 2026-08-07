# Affiliate Commerce

## Contents

- What this unit decides
- Commission is a receivable and not revenue
- The deduction chain, in the order it happens
- The withholding notch, where earning more nets less
- Two attribution windows in one document
- There is no rate card
- Indirect orders mean the income is not a read on the content
- The seller side subtracts from contribution, not from revenue
- What Vietnamese law now requires of the person posting the link
- The disclosure nobody can quote a phrase for
- The clause that ends the channel instead of deducting from it
- The thresholds that decide what this channel can become
- What the deliverable has to contain
- What this unit cannot establish
- The handoff
- Creator and UGC system

## What this unit decides

Whether an affiliate arrangement pays, for which side, and on which reading of its inputs. Both sides
are here on purpose. A creator asking what a 10% rate is worth and a seller asking what a 10% rate
costs are running the same subtraction from opposite ends. Neither can negotiate without the other's
number.

The instrument is `scripts/model_affiliate.py`. Platform mechanics sit in
`data/affiliate-mechanics.csv`, and the legal duties, with the gazette URL each was read from, sit in
`data/vn-advertising-law.csv`.

```
python scripts/model_affiliate.py --template creator > deal.csv
python scripts/model_affiliate.py --check deal.csv --side creator --floor <the net that makes it worth doing>
python scripts/model_affiliate.py --mechanics
python scripts/model_affiliate.py --notch
```

The script refuses to total an incomplete deal. It names the missing inputs instead. That refusal is
the contribution, because filling a gap with a default still produces a total, and the total is then a
guess wearing a decimal point.

## Commission is a receivable and not revenue

Affiliate commission is money somebody else owes you, contingent on events that have not finished
happening. The order can be cancelled. A buyer can return the item under the refund policy, after the
commission was already reported to you. Shopee's seller terms state outright that it need not explain
or prove any individual exclusion.

So a return rate is an input and never a footnote. The script makes it a critical gate. No stated
return rate, no total.

Then there is the clock. An individual creator is now paid twice a week. A business partner is paid
monthly, while an MCN reconciles the previous month from the 11th and pays within roughly thirty
working days of holding complete documents. Three clocks, one product.

Documents have deadlines too. They are due within six months of the commission arising for a
non-business individual, and within thirty days for a business. Miss it and Shopee may decline to pay
at all.

The stricter deadline lands on the partner who has an accountant. Below 10,000 VND a payment can
simply be held.

## The deduction chain, in the order it happens

Order matters. The withholding step reads the running figure rather than the original one, and the
headline rate applies to what settles rather than to what was ordered.

| Step | Operation | On the worked example |
|---|---|---|
| Ordered | GMV as reported | 100,000,000 |
| Settled | minus returns and cancellations at 15% | 85,000,000 |
| Commission | at the 10% headline rate | 8,500,000 |
| Service fee | minus 0.98% of everything earned | 8,416,700 |
| Withholding | minus 10% personal income tax | 7,575,030 |
| Content cost | minus what the posts cost to make | 5,575,030 |

A 10% rate arrives as 5.58% of the value it was attributed. Negotiate against that.
It is also the number nobody brings to the negotiation. Run `--self-check` to see the chain asserted
step by step.

Two of those rates were replaced recently and both old values are still published. The service fee ran
at 1% and has been 0.98% since 16 July 2025. The withholding floor was 2,000,000 VND per payment and
became 250,000 VND on 20 November 2025, which matters more than it looks. Payments moved to twice a
week at the same time.

So the same monthly income now crosses the floor on nearly every instalment instead of on none of
them. Shopee's own tax explainer still shows the old floor on another page of the same host. Two pages
disagree. The dated announcement governs.

That 10% is an advance rather than a final tax. Commission is remuneration under Thông tư
111/2013/TT-BTC, so the individual files an annual return on the progressive scale and overpayment is
refundable. A creator who never files is donating the difference.

## The withholding notch, where earning more nets less

Nothing publishes this. It falls out of the rule, and it lands on the beginner whose twice-weekly
payments sit near the floor.

Ten percent is withheld on the whole payment once the payment reaches 250,000 VND. So 249,999 VND
arrives intact and 250,000 VND arrives as 225,000. Earning one dong more costs 25,000. The band runs up
to 277,778, where the withheld figure finally catches up, and inside those 27,778 VND a larger
commission is a smaller payment.

`--notch` prints the band and a gate watches for it. The honest response to a modelled payment landing
inside it is to change the payment size, not to absorb the loss. It is arithmetic. No published rule
states it, and a rate-card conversation never reaches it.

## Two attribution windows in one document

The creator programme attributes an order when the buyer places it within seven days of clicking that
creator's link. Per click. Not per post. A post that keeps earning is one that keeps getting clicked,
rather than one that ranked once.

The seller programme is a different document, carrying two numbers nobody reconciled. Definition 1.2
retains visit information for seven days. Definition 1.4 counts a successful order where the purchase
completes within thirty days of the visitor arriving. Four times the creator-side window, in the same
terms, with no word on which one operates.

Model both. Confirm the operative one with your Shopee contact before a forecast depends on it. This is
the correction that matters most in `data/attribution-windows.csv`, whose Shopee seller row used to
record that nothing at all was published.

Something is published. Two things are, and they disagree.

## There is no rate card

Shopee states that both commission types are set automatically by system algorithm, and may change
from time to time under the programme terms. Commission is computed at the rates in force when the
buyer ordered, not when the creator posted.

Rates move. A screenshot from last week has no contractual life, so model the rate as a range. That is
why every uncertain input in the template takes a low and a high, and why the script reports which
single input owns the largest share of the spread.

Two payers, one number. Shopee funds the base commission and the seller funds Xtra,
which means a creator negotiating with a brand is negotiating only the second. Xtra is earned on shop
and product links alone. Link to a homepage or a category page and the Shopee half still pays while
the seller half silently does not.

## Indirect orders mean the income is not a read on the content

A purchase from a completely different seller after the click is still commissionable. Shopee's own
taxonomy separates direct orders from indirect ones, and discovery orders from conversion orders.

So affiliate earnings do not measure the product you posted about. A creator attributing income to one
video is usually wrong about which basket it came from. A brand reading affiliate revenue as demand
for its own SKU is reading a number that partly belongs to somebody else's.

Use the five dash-separated `sub_id` slots for the taxonomy you do control. The delimiter is a dash, so
a value containing one splits the field.

Where a platform blocks affiliate links, Shopee issues a product code shaped like `BFD-ZBE-BDY` that a
follower pastes into search, and states this records the same as a click. That makes attributed revenue
possible on surfaces which strip links. Which is most of them.

## The seller side subtracts from contribution, not from revenue

A seller's arithmetic is a difference, not a product. That is why the script models the two sides on
separate code paths. Commission comes out of what the order contributes after variable cost.

Which ratio means anything also changes. A creator's take rate is net over GMV, comparable to the rate
on the offer. A seller's is contribution over GMV, and comparing that to a commission rate produces
nonsense.

So the seller report prints a different figure. It gives the share of contribution that commission
consumes. On a 400,000,000 VND programme at a 30% contribution margin and an 11% commission,
commission takes 37% of the contribution those orders generate.

Argue about that share when the Xtra rate rises, rather than about the rate. A move from 11% to 13%
sounds like two points. It is six points of the contribution actually available. The gate that fails
when commission exceeds contribution margin exists because such a deal loses money on every order.

## What Vietnamese law now requires of the person posting the link

Vietnam's instrument chain changed under everybody's feet and most guidance has not caught up. The
advertising statute is Luật 16/2012 as amended four times, most recently by **Luật 75/2025/QH15**, in
force 1 January 2026. Nghị định 38/2021 is repealed from 15 May 2026 by **Nghị định 87/2026/NĐ-CP**,
and that repealed decree is the one every pre-2026 Vietnamese marketing guide cites for advertising
penalties.

Check the citation before repeating any fine figure, including one from a recent source. Commercial
advertising was cut out of Luật Thương mại entirely. Every row in `data/vn-advertising-law.csv` carries
the gazette URL it came from.

Two provisions now bind an affiliate specifically. New **Điều 15a.3.a** says that where the influencer
has not used the product, or does not clearly understand it, they may not introduce it. The conditions
are disjunctive, so either alone is enough. The prohibition is on introducing the product at all,
which is broader than a ban on claiming a result.

That one carries the heaviest influencer penalty in the decree. Điều 51.3 sets 80,000,000 to
100,000,000 VND, at the individual ceiling.

Then **Điều 15a.3.b**: notify that this is advertising immediately before and during the activity.
During is the word. A disclosure sitting in a video's caption, with nothing carrying it while the video
runs, is the ordinary shape of incomplete disclosure. That is 40,000,000 to 60,000,000 VND under Điều
51.1.c, and no disclosure at all is 60,000,000 to 80,000,000 under Điều 51.2.

Whether you are inside the influencer definition is not a follower question. No numeric follower
threshold exists anywhere in Vietnamese law. The definition sits in consumer-protection law, at
Nghị định 55/2024 Điều 2.1, needing sponsorship in any form plus one of three limbs. The third limb is
satisfied by a significant following **or** by holding an account eligible to join advertising or
commerce programmes on digital platforms.

Read that limb again. Qualifying for Shopee Affiliate is itself evidence of the second alternative.

Three further points decide how the risk is shared. Fines under Điều 51 and Điều 56 are individual
baselines and double for an organisation, so an agency carrying its creator's conduct carries twice the
exposure. Điều 51.4.b reaches the proceeds of the sales where a contract with the influencer existed.
That is why a brand should want the disclosure done, not merely require it in a brief.

The third point is the useful one. Luật 19/2023 Điều 22.1 makes the creator jointly liable unless it
proves it took the verification steps the law prescribes. It is the only due-diligence defence in any
of these instruments. So keep a record of the Điều 15a.3.a checks rather than only performing them,
and ask for the documents Điều 15a.1.a entitles you to.

## The disclosure nobody can quote a phrase for

Điều 23.2.a requires a clear identifying marker, expressly by numerals, writing, symbols, images or
sound, distinguishing advertising from other content. Điều 23.2.đ binds the individual account holder
rather than the platform. A missing marker costs 30,000,000 to 40,000,000 VND under Điều 56.2.a, and
that provision is actor-neutral. It reaches an ordinary affiliate with no sponsorship and no influencer
status.

No phrase is mandated. Searches of the statute and both decrees found no required wording, font size,
position or duration for a sponsorship marker, and Nghị định 342/2025 does not implement Điều 15a at
all. The law fixes timing and requires a marker whose words it leaves open.

The same decree does prescribe exact Vietnamese wording for food. So the drafters knew how to mandate a
phrase and declined to here. Mandate a marker in every deliverable. Never tell a client that some
particular Vietnamese phrase is legally required, because no source in this table supports that.

Avoid one transplant. Điều 19.2 does prescribe form, requiring contrasting colour, type no smaller than
the advertisement's own, and delivery at equal speed and volume. It governs mandatory warnings, not
sponsorship disclosure.

## The clause that ends the channel instead of deducting from it

Prohibited conduct carries a charge capped at 10,000,000 VND per instance, VAT included, cumulative
across instances. Shopee decides unilaterally whether to offset it against what it owes you or invoice
you for it. Read the prohibited list properly once. Four items on it describe ordinary agency and
creator practice.

Bidding on the Shopee brand in paid search needs written consent, and the policy says the term must be
a negative keyword. Promotional email needs prior written approval, which puts a newsletter carrying
affiliate links inside the clause. Item (n) makes using another person's content without permission a
fraud violation at the same charge as fake orders. Automation, emulators and purchased engagement sit
in the same family as order fraud.

Note what item (n) implies. The platform's own policy is stricter on image rights than most agency
practice, and it enforces that by withholding money.

One number is not a deduction at all. Under 20% violating orders in a reconciliation window and Shopee
pays on the clean remainder. At 20% or above in one month, or across three months whether consecutive
or not, Shopee may lock the affiliate account and the Shopee account with it. Deleting your own Shopee
account forfeits commission already earned.

## The thresholds that decide what this channel can become

Two thresholds an order of magnitude apart decide what an affiliate operation can grow into, and they
belong to different programmes.

| Threshold | Value | What it gates |
|---|---|---|
| Convert an individual creator account to a company | above 500 orders per day, averaged over 3 consecutive months | Supported once, ever |
| Business eligibility for the seller programme | above 50 orders per day, averaged over 3 months | Then a signed service contract |

Non-business individuals face no threshold on the seller side. Registering as an individual while
operating as a business means being treated as an individual, with an individual's obligations. Plan it
early. The conversion is available exactly one time.

## What the deliverable has to contain

- The model, as the CSV the script reads, with a low and a high on every uncertain input.
- The gate table, including the gates that failed, rather than a summary of it.
- Which input owns the largest share of the spread, and therefore what to pin down next.
- The net at the floor that makes the work worth doing, and whether the range straddles that floor.
- The attribution window used, named, with the side it came from.
- The disclosure plan: what marks the content, before and during, on each surface.
- For a brand brief, the documents handed over under Điều 15a.1.a, and the record kept of the checks.

A straddled floor is a finding. The script exits 3 and says the model has not decided anything, which
is the honest verdict when the answer depends on which end of your own range turns out to be true.

## What this unit cannot establish

Published Shopee terms are the only fully citable affiliate rules here. TikTok Shop's commission and
payout terms are not readable without a login, and that was measured rather than assumed:
`affiliate.tiktok.com` answers 200 with 37 characters of visible text. Plan for one channel whose rules
you can quote, and one whose rules you must screenshot from inside the account.

Two legal questions belong to a Vietnamese lawyer rather than to any agent, and the table records both
as unresolved. Whether advertising-content pre-clearance still exists is genuinely unclear. Nghị định
342/2025 did not re-enact the confirmation regime, yet Nghị định 87/2026 Điều 68.1.b still penalises
advertising without it and Luật 122/2025 Điều 23.2 still requires a seller to hand it over.

The second is a gap rather than a conflict. No dedicated penalty exists for a conveyor who is not an
influencer and fails to disclose. The actor-neutral marker fine reaches them anyway, so do not advise
anybody that non-disclosure goes unpenalised.

One hole is a hole and not a finding. Điều 26 of Nghị định 248/2026 addresses the duties of a person
doing affiliate marketing, and it has not been read. The table records it as unread so it cannot be
mistaken for an established absence.

The script's bounds come from enumerating the corners of the inputs. That is exact where the model is
monotone in each input. Withholding is a step and therefore not monotone, so the maximum can be
understated, by at most the width of the notch. The notch is reported separately rather than smoothed
away.

## The handoff

Read the `Creator and UGC system` section below for selecting and briefing the person, which is a different decision from whether
the arrangement pays. Before agreeing a rate from the seller side, work the subtraction in
`pricing-and-offers.md`, where commission is one of the variable costs it already handles. When the
question is why a platform number and an analytics number disagree, go to `measurement-plan.md` and
`data/attribution-windows.csv`.

Take the disclosure duties into `claims-proof-ledger.md` when a claim needs substantiation, and into
`data/vn-advertising-law.csv` when somebody quotes a fine. Never quote a figure from that table without
the `what_it_does_not_establish` cell beside it.

## Creator and UGC system

### Creator fit

Select by audience trust, content behavior, product relevance, production reliability, brand safety, geography/language, and rights feasibility—not follower count alone.

Record whether the person is a customer, employee, paid creator, affiliate, expert, actor, or fictional virtual person. Never present staged content as organic customer experience.

### Brief contract

- Audience state and one message.
- Product truth and mandatory demonstration.
- Hook options, beats, CTA, and channel behavior.
- Product, label, claim, competitor, identity, location, and music restrictions.
- Deliverables, ratios, duration, raw files, captions, thumbnails, revision rounds, deadline, and approval owner.
- Usage rights, term, territory, placements, editing rights, paid amplification/whitelisting, exclusivity, and credit.
- Required disclosure and prohibited claims.

Give creators room for native language and behavior. A script that removes every authentic choice defeats the format.

### Useful formats

Hook-to-camera, problem/solution, routine, tutorial, demo, unboxing, first-use, review, reaction, comparison, comment reply, founder/employee POV, expert explanation, ASMR, street interview, and behind-the-scenes.

Before/after, testimonial, health, beauty, finance, and performance content require substantiation and appropriate disclosure.

### Approval and handoff

Review product truth, disclosure visibility, identity/consent, music/third-party rights, platform policy, native quality, crop/safe zone, and CTA. Preserve creator ID, asset ID, parent concept, usage rights, claim IDs, approval state, spend, and performance.

### Disclosure, for Vietnam specifically

Use FTC endorsement guidance for US-facing work. Vietnam is stricter. The duties are statutory and
they name the creator, not only the brand.

Luật 75/2025/QH15 Điều 15a.3.b requires disclosure immediately before and during the advertising, which
a caption alone does not satisfy on a video. During is the word. Điều 23.2.đ requires a marker separating advertising from the creator's other posts, and Điều 15a.3.a
bars introducing a product the creator has not used or does not clearly understand.

Penalties reach 100,000,000 VND for an individual under Nghị định 87/2026/NĐ-CP Điều 51, and double for
an organisation. No wording is prescribed. So mandate a marker in the brief, and never tell a client
that a particular Vietnamese phrase is legally required. Every figure is sourced by gazette URL in
`data/vn-advertising-law.csv`.

Read the commission modelling earlier in this file before agreeing commission terms, from either side. Whether the
arrangement pays is a different question from whether the person fits, and it has its own instrument.
