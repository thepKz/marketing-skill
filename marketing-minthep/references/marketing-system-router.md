# Marketing System Router

## Core rule

Route by the business job first, then apply product/category, channel, visual, and market overlays. Do not load every module or produce every artifact.

## Primary workbenches

| Workbench | Use when | Default output pack |
|---|---|---|
| `strategy-offer` | Positioning, audience, offer, GTM, funnel | Truth map, positioning, offer/proof, channel thesis, measurement contract |
| `campaign-launch` | Launch, seasonal moment, promotion, brand campaign | Campaign architecture, three lanes, rollout, asset matrix, landing continuity, test plan |
| `content-distribution` | Content strategy, SEO, social, editorial engine | Pillars, prioritized topics, briefs, repurposing graph, distribution and refresh loop |
| `commerce-merchandising` | PDP, marketplace, catalog, collection, retail selling | Listing narrative, image sequence, SKU/variant system, copy, trust, return-reduction QA |
| `pr-communications` | Press, earned media, announcement, spokesperson | Newsworthiness gate, angle, release/pitch, press kit, Q&A, measurement |
| `sales-enablement` | One-pager, deck, demo, proposal, objection handling | Sales narrative, artifact pack, proof map, talk track, follow-up |
| `creator-ugc` | Influencer, creator seeding, UGC, whitelisting | Creator criteria, brief, deliverables, rights/disclosure, variants, approval and performance handoff |
| `lifecycle-retention` | Welcome, nurture, cart recovery, post-purchase, win-back | State map, trigger matrix, message sequence, offer rules, suppression and measurement |
| `creative-production` | Product/human images, video concepts, edits, visual system | Reference map, shot/format plan, prompt contracts, provider plan, QA and export |
| `measurement-optimization` | Reporting, creative diagnosis, experiments | Objective-aware report, guardrails, test readout, decision and next experiment |

Run `scripts/plan_marketing_system.py` when the request spans jobs or the correct output pack is unclear.

## Secondary overlays

Load only when relevant:

- Product/business model: `product-category-playbooks.md`.
- Commerce: `commerce-merchandising.md`.
- Paid media: `paid-media-creative.md`.
- PR: `pr-communications.md`.
- Sales: `sales-enablement.md`.
- Creator/UGC: `creator-ugc.md`.
- Lifecycle: `lifecycle-retention.md`.
- Claims and proof: `claims-proof-ledger.md`.
- Current placements/specs: `channel-spec-registry.md`.
- Product/human/virtual imagery: relevant image references.

## Operating modes

Choose one:

1. `create`: Build a new strategy or asset pack.
2. `adapt`: Recompose an existing idea for new channels, markets, formats, or audiences.
3. `scale`: Produce a controlled matrix, registry, manifest, or batch-ready artifact.
4. `diagnose`: Audit weak performance, conversion friction, or creative failure.
5. `iterate`: Use evidence to revise one variable while preserving lineage.

## Output discipline

Every artifact must declare:

- Business job and funnel state.
- Audience state and single message.
- Product truth, mechanism, offer, and proof.
- Channel/placement and native behavior.
- CTA and expected next step.
- Required source assets and locks.
- Claim IDs and rights/disclosure requirements.
- Acceptance gate and metric.

Default to the smallest pack that can achieve or test the objective. Expand only when the user requests a system/production scope or dependencies require it.
