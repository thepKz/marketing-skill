# Campaign Systems

## Contents

- Campaign architecture
- Concept lane construction
- Creative matrix
- Landing-page structures
- Testing and measurement
- Handoff format
- Paid media and creative operations
- Grand opening (khai trương)

## Campaign architecture

Start from a behavior change, not a visual style.

1. Define the current audience belief or friction.
2. Define the new belief or action the campaign must create.
3. Identify the product mechanism that makes the promise credible.
4. Select one primary proof type: demonstration, comparison, testimonial, data, process, ingredient, craft, or cultural signal.
5. Build one campaign idea that can survive across multiple assets without repeating one layout.

Use this message ladder:

| Layer | Question |
|---|---|
| Tension | What does the audience feel, lose, or struggle with now? |
| Promise | What meaningful change does the product enable? |
| Mechanism | Why does this product produce that change? |
| Proof | What evidence makes the mechanism believable? |
| Action | What should the audience do next? |

Avoid unsupported superlatives, invented statistics, and claims that are not present in user-provided evidence.

## Concept lane construction

Make lanes different at the idea level, not only by palette.

### Clear lane

- Lead with the product and benefit.
- Use one dominant proof device.
- Keep the first three seconds or first viewport immediately understandable.
- Best for conversion, retargeting, ecommerce, and unfamiliar products.

### Distinctive lane

- Turn the product mechanism into a visual grammar.
- Use a memorable crop, prop system, recurring gesture, material contrast, or narrative rule.
- Ensure the device scales to stills, motion, landing pages, and social cutdowns.

### Departure lane

- Break one category convention deliberately.
- Keep offer, hierarchy, and CTA conventional enough to remain usable.
- State the risk and the channel where the departure is safest to test.

Reject lanes that can be described only as `premium`, `modern`, `minimal`, `futuristic` or `luxury`.

## Creative matrix

Build variation through controlled axes:

- 3 concept lanes.
- 3 hooks per lane: problem, aspiration, proof.
- 2 formats per hook: product-led and human/context-led.
- 2 CTA treatments when conversion is the goal.

Do not generate every combination blindly. Select the smallest matrix that answers a real hypothesis. Label the variable being tested and keep other variables stable.

Example hypotheses:

- Product demonstration beats lifestyle aspiration for cold traffic.
- A founder or expert proof frame increases consideration.
- An unusual crop improves stopping power without reducing product recognition.
- Raw human photography produces more trust than polished studio imagery.

## Landing-page structures

Choose the structure based on the decision the visitor must make.

### Product launch

1. Hero: product, promise, primary action.
2. Immediate proof strip or demonstration.
3. Problem and category tension.
4. Product mechanism.
5. Feature-to-outcome story.
6. Use cases or audience moments.
7. Social or technical proof.
8. Offer, FAQ, and final action.

### Campaign story

1. Campaign statement or visual event.
2. Cultural or audience tension.
3. Narrative reveal.
4. Product role in the story.
5. Participation, collection, or action.
6. Proof and conversion path.

### Lead generation

1. Specific outcome and qualification cue.
2. What the visitor receives.
3. Why it is credible.
4. Preview or sample.
5. Low-friction form.
6. Privacy expectation and next step.

### Comparison or switching

1. Switching promise.
2. Transparent comparison criteria.
3. Demonstrated advantage.
4. Migration or risk reduction.
5. Customer proof.
6. Offer and action.

Do not force every section into a card. Vary pacing, density, image scale, and alignment. Keep one dominant idea per viewport when the campaign calls for drama.

## Testing and measurement

Connect creative tests to funnel behavior:

| Stage | Primary signals | Creative questions |
|---|---|---|
| Awareness | Thumb-stop, view rate, reach quality | Does the first frame create relevant curiosity? |
| Consideration | Hold rate, saves, clicks, engaged visits | Is the promise understandable and credible? |
| Conversion | CTA clicks, add-to-cart, lead, purchase | Does proof reduce the final objection? |
| Retention | Repeat use, upsell, referral | Does the creative reinforce value already experienced? |

Do not optimize only for click-through rate when the downstream conversion quality worsens.

## Handoff format

For each asset specify:

- Asset ID and campaign lane.
- Funnel stage and hypothesis.
- Channel, aspect ratio, duration, and safe zone.
- Hook, message, proof, CTA.
- Visual composition and shot requirements.
- Prompt or edit instruction.
- Required product, logo, model, legal, or source assets.
- Review owner and acceptance criteria.

## Paid media and creative operations

### Campaign structure

Define before creative production:

- Objective and conversion event.
- Prospecting, consideration, retargeting, retention, or reactivation role.
- Audience hypothesis, exclusions, geography, and frequency risk.
- Offer, destination, tracking readiness, and budget constraint.
- Creative learning question and guardrail metrics.

Do not recommend budget, bidding, audience size, or attribution certainty without current account data and platform context.

### Creative families

Build the smallest set needed to answer a real hypothesis:

1. Problem or tension.
2. Aspiration or desired state.
3. Product demonstration.
4. Mechanism or feature proof.
5. Testimonial/creator proof with authorization and disclosure.
6. Comparison or selection guide with supported criteria.
7. Objection handling.
8. Offer/urgency with confirmed terms.
9. Founder/expert explanation.
10. Retargeting reminder or product revisit.

Use visual formats such as product-led static, human/context static, demo, unboxing, routine, ASMR, founder POV, expert explainer, carousel, reaction, comment reply, VSL, or motion key visual only when native to the channel and suitable for the product.

### Test hierarchy

Test in this order unless evidence suggests otherwise:

1. Concept/angle.
2. Proof type.
3. Format and product-vs-human lead.
4. Hook/first frame.
5. Offer and CTA.
6. Copy, crop, color, or micro-variation.

Keep a variant parent and change one named variable. Do not call a winner from mixed audiences, unequal spend, different landing pages, or insufficient conversion evidence.

### Production modes

- `from-scratch`: truth → angle → format → asset.
- `grounded-iteration`: use actual performance, comments, objections, and winning elements.
- `controlled-scale`: create a CSV/manifest from approved concepts and locked inputs.
- `diagnose`: separate creative, offer, audience, landing, tracking, and delivery problems.

### Tracking gate

A creative test is only as trustworthy as the event it is scored on, so this gate is not a checklist
here. It is `measurement-plan.md`, and the two things it blocks on are the two that invalidate a
result rather than degrade it: the winning variant scored on an event that fires on a button click
instead of a successful write, and two spellings of the campaign name splitting one test across two
rows.

```
python scripts/check_tracking_plan.py --url "<one real tagged link from this campaign>"
python scripts/check_tracking_plan.py --event <the event this test is scored on>
```

Run both before the first ad goes live. A naming convention fixed afterwards does not merge what was
already collected. Then connect each asset to `campaign_id`, `asset_id`, placement, concept, angle,
hook, proof, offer, CTA, and variant parent.

Then check the export before it goes anywhere near the upload flow. `channel-spec-registry.md`
explains the three states a vendor page can be in and why an unpublished figure is not a pass;
`data/channel-specs.csv` holds the current placement registry with the URL and retrieval date for every published limit. Count the rows at runtime; do not hardcode a total that will drift when a platform is added.

```
python scripts/check_channel_spec.py --survey --width 1080 --height 1920 \
  --duration 22 --file-size 30MB --format mp4
```

That is the useful direction. You have one file and a week of posting to fill, so the answer worth
having is which surfaces take it untouched and which crop it. Exit 2 means a documented requirement
is broken and the upload is refused or the crop is taken out of your hands. Exit 3 means the page
publishes nothing on that axis, which is the state that reads as permission and is not — go and read
the placement's own panel before you spend on it.

## Grand opening (khai trương)

An opening is the one campaign a business runs exactly once with no baseline, and the standard
failure is structural: the budget peaks on day one, week three is empty, and the emptiness gets
misread as market rejection and answered with panic discounts. The correct shape spends **before**
the doors open and **after** the ribbon, with opening day as the hinge rather than the point.

**Before (two to three weeks).** The catchment learns the place exists while it is still being
built: the construction fence carries the name, the offer, and the date rather than blank hoarding;
the owner posts the build in local Facebook groups (the group is the local channel —
`vietnam-operating-reality.md` on why); a **soft open** for friends, neighbours, and a few KOC
guests runs the kitchen and the till at forgiving load. The soft open is a rehearsal, not a preview
campaign — its output is fixed processes and a first batch of photos and reviews, not revenue.
Check the date against the occasion calendar in `vietnam-operating-reality.md` §7.3 before
anything is printed: openings do not go in tháng cô hồn, and a date adjacent to Tết inherits
Tết's logistics.

**The day.** One offer, capped and dated, designed to cause a *second* visit: a voucher for the
next visit outperforms a deeper discount on the first, because the opening's real product is a
repeat customer, not a queue. The queue itself is the day's content — photograph it, post it,
pin it. Claims discipline still applies ("khai trương giảm 50%" is a price claim with a
documented floor in `pricing-and-offers.md`).

**Weeks two to eight — the actual campaign.** This is where the centre of gravity sits: the
voucher redemptions come due, the review count gets built (ask at the table, not in a message
three days later), the local-group posts shift from "we opened" to the shop's ordinary content
system, and the owner's weekly loop (`how-companies-market.md`, Direction by scale, level 1)
starts running as the permanent operating rhythm. The scoreboard for the whole opening is
**week-four return rate and review count** — day-one revenue measures the discount, not the
business.
