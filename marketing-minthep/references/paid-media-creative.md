# Paid Media and Creative Operations

## Campaign structure

Define before creative production:

- Objective and conversion event.
- Prospecting, consideration, retargeting, retention, or reactivation role.
- Audience hypothesis, exclusions, geography, and frequency risk.
- Offer, destination, tracking readiness, and budget constraint.
- Creative learning question and guardrail metrics.

Do not recommend budget, bidding, audience size, or attribution certainty without current account data and platform context.

## Creative families

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

## Test hierarchy

Test in this order unless evidence suggests otherwise:

1. Concept/angle.
2. Proof type.
3. Format and product-vs-human lead.
4. Hook/first frame.
5. Offer and CTA.
6. Copy, crop, color, or micro-variation.

Keep a variant parent and change one named variable. Do not call a winner from mixed audiences, unequal spend, different landing pages, or insufficient conversion evidence.

## Production modes

- `from-scratch`: truth → angle → format → asset.
- `grounded-iteration`: use actual performance, comments, objections, and winning elements.
- `controlled-scale`: create a CSV/manifest from approved concepts and locked inputs.
- `diagnose`: separate creative, offer, audience, landing, tracking, and delivery problems.

## Tracking gate

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
