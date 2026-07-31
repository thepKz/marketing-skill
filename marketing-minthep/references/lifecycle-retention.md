# Lifecycle and Retention

A lifecycle programme is the only marketing artefact built entirely out of stored personal data and
scheduled repeat contact. That is what makes it the most heavily regulated thing in this skill, and
what makes an imported flow diagram the wrong starting point. The state map below is the easy half.
The half that decides whether the flow may be sent is `data/lifecycle-duties.csv`, twenty-five duties
read out of Luật Bảo vệ quyền lợi người tiêu dùng số 19/2023/QH15, Nghị định 342/2025/NĐ-CP and
Nghị định 87/2026/NĐ-CP, and `scripts/plan_lifecycle.py`, which grades a declared flow against them.

## Start here

```powershell
python marketing-minthep/scripts/plan_lifecycle.py --duties
python marketing-minthep/scripts/plan_lifecycle.py --template flow.csv
python marketing-minthep/scripts/plan_lifecycle.py --audit flow.csv --orders 4200 --aov 690000
```

A flow is not words, so there is nothing to scan. It is a schedule, a consent state, a retention
policy and a contract term, none of which appear in the copy. `--template` writes a sheet of
thirty-six questions; a human answers them; `--audit` grades the answers. A blank field fails its
gate rather than passing it, and so does a value the script cannot parse. On the worked flow above,
a six-month skincare subscription assembled from a global template, three of twenty-four applicable
gates passed and eleven failures blocked the send.

## The five rules an imported playbook does not carry

**Consent to be marketed to is its own control.** Điều 18.4.b requires a mechanism letting the
consumer allow or refuse the use of their information for advertising and product introduction, and
it is separate from consent to transact. One checkbox at checkout is not consent to the flow, and the
flow is the entire asset. Bundled consent is the most common single failure, because every commercial
email platform ships the bundled pattern as its default. Điều 18.4.b carries no fine, and reading
that as a soft rule is the trap: sending against it means processing personal data outside what the
law permits, which is the prohibited act at Điều 10.1.m. So the gate blocks the send on a fine of
zero, and the script grades it that way because the table's own remedy column says so.

**Your own published retention period is the legal deadline.** Điều 16.1.c makes you state a
retention period in the published information-protection rule, and Điều 20.3 makes you destroy the
record when it lapses. So a win-back at month eighteen against a twelve-month policy is not a
lapsed-customer campaign, it is unlawful processing, and the number that makes it unlawful is a
number you chose yourself. The script subtracts the declared longest delay in the flow from the
declared period. That subtraction is the single most common way a lifecycle programme built abroad
breaks Vietnamese law.

**A service of three months or more owes two notices, counted in working days.** Điều 3.6 defines
cung cấp dịch vụ liên tục as three months or more, or indefinite, and crossing that line switches on
Điều 42: the pay-to-continue notice at least 07 ngày làm việc before expiry, the end-of-contract
notice on the same clock, a written contract with a copy for the consumer, and a right to leave at
any time paying only for what was used. Working days, not days. On the worked flow, a notice sent
four calendar days out was one working day out, and the script named 2026-08-20 as the last lawful
send date for a 2026-09-01 expiry.

**Harassment is measured against the consumer's wishes, not against your unsubscribe list.** Điều
10.1.b prohibits contact trái với ý muốn của người tiêu dùng to introduce a product or propose a
contract. That is broader than contact after an opt-out, and no article in this corpus converts it
into a send-frequency number. The script reports the declared frequency as context and certifies
nothing, because the decree that does set per-day caps and a time window for advertising messages and
email is not in this corpus. An imported rule of thumb about two sends a week is a deliverability
opinion wearing a legal coat.

**The capture overlay is regulated separately from the flow it feeds.** Nghị định 342/2025 Điều 17
governs it: one interaction to close, no fake or hard-to-distinguish close icon, zero wait on a
static image and at most 05 giây on animation or video, and a working control to report unlawful ad
content or refuse an unsuitable ad. Nghị định 87/2026 Điều 56.2.b prices a failure at 30 to 40
million. Three of those four sub-rules failed on the worked flow, which is 90 to 120 million from the
popup alone, before a single message was written.

## What the fine column does not measure

Only the two advertising instruments carry bands, so twenty of the twenty-five rows show a fine of
zero. That is not a discount. The consumer-protection law hands the consumer a remedy instead, and on
a distance sale the remedy is larger than the fine:

- Điều 38.3.b opens a thirty-day free exit on every contract where the pre-contract information was
  inaccurate or incomplete. An unsupported claim is both.
- Điều 10.1.e turns a mismatch between the product and what was advertised into a duty to refund,
  replace or compensate, on every unit sold under the claim.
- Điều 38.4 gives thirty days to return the money, by the method the consumer paid, with interest
  running after.

Give the script `--orders` and `--aov` and it sizes that. On the worked flow, 4.200 orders at 690.000
đồng put 2.898.000.000 đồng of sales inside a refund or free-exit right, against a fine band of at
most 40 million for the same unverified claim. The fine is the smaller half. That number is usually
the moment an argument about marketing copy stops being an argument about tone, and it is why
`claims-proof-ledger.md` runs before the flow ships rather than after.

## What the working-day count refuses to do

Public holidays are ngày làm việc too, and the script does not net them out. Tết moves against the
solar calendar and the holiday list is set by an annual instrument, so hardcoding either would be a
wrong answer with a confident face on it. The count is weekdays only, the report says so on every
line it appears, and the instruction to the scheduler is to move the send one day earlier for every
public holiday inside the window. A tool that quietly assumed nine fixed holidays would approve a Tết
renewal notice that arrives two days late.

## State map

Design around customer state and trigger. The nine stages in the duty table are the legal view of
this same journey, coarser on purpose, because the law groups by duty rather than by moment:

- Subscriber or lead welcome.
- Education and nurture.
- Browse or cart abandonment.
- Trial activation and onboarding.
- Purchase confirmation and expectation setting.
- Product use, replenishment, and adoption.
- Review or referral request.
- Cross-sell or upsell.
- Churn risk and win-back.
- Service, transactional, or incident communication.

For each message define trigger, eligibility, delay, suppression, one job, proof, CTA, destination,
personalization fields, fallback values, exit condition, and measurement. Declare the flow-level
facts on the sheet the script writes; the per-message fields above are craft and the script does not
read them.

## Creative and copy

- Keep essential meaning in live text; images may be blocked.
- Use product and use visuals that match the lifecycle state.
- Diagnose before discounting. Low activation has distinct causes and a discount only fixes one of
  them: the customer never reached first value (fix onboarding and the first-run path), does not
  believe the value (add proof, demo, or a guarantee), hit a friction wall such as payment or setup
  (fix the wall), or genuinely finds the price too high for the value shown (only here does price
  belong in the answer). Discounting a belief problem teaches the customer to wait for the next offer
  and leaves the belief intact.
- Confirm offer, inventory, expiry, replenishment timing, and personalization data.
- Adapt email, SMS, Zalo, push, in-app, and retargeting instead of pasting one message everywhere.
- Do not send promotional pressure while a service or support issue is unresolved. No article in this
  corpus names that rule, so the table does not carry it and the script does not gate it. It is a
  craft judgement, stated as one.

## Measurement

Measure the behaviour the flow intended: activation, time-to-value, recovered checkout, repeat
purchase, replenishment, adoption, referral, churn, or reactivation. Use deliverability, complaint,
unsubscribe, margin, and support load as guardrails. Treat open rate cautiously where privacy
features distort it. On cash on delivery, read `measurement-plan.md` before quoting any efficiency
figure from a lifecycle flow: a purchase event is an order request, and the gap to delivered orders
is the largest correction most Vietnamese reports are missing.
