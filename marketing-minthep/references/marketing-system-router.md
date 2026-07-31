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

## Autonomous pipeline router

For requests that must become files on disk, use `scripts/start_workbench.py`. It selects a primary pipeline and creates linked supporting runs when independent jobs score strongly in the same request. Use `scripts/new_run.py` only for a bare single-pipeline scaffold.

| Pipeline | Trigger | Mandatory modules |
|---|---|---|
| `plan-from-zero` | Non-marketer or business has no usable plan | Research, market assessment, audience, positioning/offer, copy, channels, budget, calendar, measurement |
| `deep-research` | Decision depends on market, customer, competitor, price, regulation, or feasibility evidence | `research-protocol.md`, `market-assessment.md`, `customer-evidence.md`, `source-map.md`, `market-data-collection.md`, `how-companies-market.md` |
| `image-from-reference` | Source image A must become branded, commercial, artistic, or edited imagery | Reference locks, `reference-reading.md`, visual craft, edit/generation route, prompts/render, QA/export |
| `design-render` | Menu, poster, layout, wireframe, one-pager, or other designed artifact | Options, recommendation, information architecture, wireframe, copy, render/spec, QA |
| `video-campaign` | Video concept, storyboard, short ad, demo, or AI-video prompt pack | Script, beats, shots, continuity, audio/captions, cutdowns, delivery QA |
| `optimize-iterate` | Existing work has evidence or performance to diagnose | Metric tree, hypotheses, one-variable tests, guardrails, decision log |
| `rewrite-human` | A draft reads machine-written or machine-translated, or approved copy must move between Vietnamese and English | `specificity.md` and `scripts/check_specificity.py` first, then `rewrite-human.md` and `scripts/rewrite_human.py` gates, `data/translation-tells.csv` repairs, `scripts/check_address_register.py` on Vietnamese, re-measurement |

When the user is a non-marketer, do not return a menu of disconnected marketing disciplines. Recommend the smallest coherent pipeline. Explain why in plain language, then create the connected artifact pack. Copywriting is mandatory inside `plan-from-zero`; it is not an optional follow-up.

## Secondary overlays

Load only when relevant:

- Product/business model: `product-category-playbooks.md`.
- Campaign architecture and lanes: `campaign-systems.md`.
- Content engine, pillars, editorial calendar: `content-system.md`.
- Commerce: `commerce-merchandising.md`.
- Paid media: `paid-media-creative.md`.
- PR: `pr-communications.md`.
- Sales: `sales-enablement.md`.
- Creator/UGC: `creator-ugc.md`.
- Lifecycle: `lifecycle-retention.md`.
- Claims and proof: `claims-proof-ledger.md`.
- Current placements/specs: `channel-spec-registry.md`.
- Product/human/virtual imagery: relevant image references.
- Logo, wordmark, favicon, banner grid, type scale: `identity-design.md`.
- Palette, contrast, lightness separation, chroma budget, tonal ramps: `colour-combination.md` plus
  `data/palettes.csv` and `data/colour-gates.csv`. Load this before naming a colour, and before
  quoting a colour-psychology statistic.
- One person holding every marketing role, what the week can actually carry, and which roles are
  silently being dropped: `vietnam-operating-reality.md` plus `data/vn-marketer-roles.csv` and
  `scripts/plan_operating_load.py`. Load this before recommending a plan to a small team, and before
  answering "how do I do marketing for my shop".
- Reading a live reference into pose, light, palette and makeup observations without storing the image:
  `reference-reading.md` plus `data/reference-observations.csv`.
- What professional output actually measures, and which of this skill's own craft rules survived being
  measured: `reference-set-calibration.md` plus `data/reference-set-calibration.csv`. Load this before
  quoting "two hues plus skin", before offering 1:1 for a feed post, and before treating a chroma-budget
  pass on a photograph as meaningful.
- How many frames one existing product photograph can actually produce, which need a second exposure,
  which are legal as a marketplace main image, and what to declare in IPTC metadata:
  `product-composition-set.md` plus `data/product-compositions.csv` and
  `scripts/plan_composition_set.py`. Load this before answering "can AI make the rest of my photos",
  and before promising a full listing set from one file.
- How many checkable facts a draft actually carries, and which of its sentences a competitor could
  publish unchanged: `specificity.md` plus `scripts/check_specificity.py` and the `evidence` and
  `hedge` layers of `data/translation-tells.csv`. Load this before rewriting any draft for cadence,
  because rhythm work deletes specifics - a specific is the awkward part of a sentence - and a draft
  with fewer than three has a content problem that reads worse after it has been made to flow.
- Who a Vietnamese draft is talking to, and whether it holds that decision to the last line:
  `address-register.md` plus `data/address-registers.csv` and `scripts/check_address_register.py`.
  Load this before writing or localising any Vietnamese copy. Vietnamese has no neutral second
  person, so the choice is grammar, not tone, and a translated draft re-invents it every sentence.
- What kind of page can answer a search query at all, and whether the draft answers it before it
  starts talking about the company: `seo-writing.md` plus `data/seo-intents.csv` and
  `scripts/audit_seo_page.py`. Load this before writing anything meant to be found, and before
  quoting a price for `best-of` work - those SERPs are held by aggregators and a brand domain
  usually cannot win them at any length. The script measures the draft and refuses to estimate
  volume, difficulty or position, because those are live facts and inventing them is fabrication.
- Where a number came from and what it actually measures: `market-data-collection.md`.
- How big the market is: `market-assessment.md` plus `scripts/size_market.py`. Load it before a sizing
  figure reaches a slide. The script totals a chain only when every term carries a range, a family and
  a source, and it refuses a platform-reported figure as a population. It reports the geometric centre,
  because the average of a product's low and high sits above its middle.
- Whether you already know enough to decide: the same script, given `--threshold`. It says whether the
  range still holds the number that flips the decision, and which single term would settle it. Terms it
  does not name cannot change the outcome. Research hours die there.
- How to search a Vietnamese question, and what a delegated finding is worth before you re-read it:
  `research-protocol.md`. Load it before treating three agreeing articles as three sources. If two
  trace to one press release, you have two signals.
- Whether a number can be measured at all, and whether the thing measured is the thing promised:
  `measurement-plan.md` plus `data/tracking-events.csv`, `data/attribution-windows.csv` and
  `scripts/check_tracking_plan.py`. Load this before the first campaign ships, because a naming
  convention fixed afterwards does not merge what was already collected, and before anybody adds
  platform-reported conversions across platforms - that sum is a total of claims, not of conversions.
  On cash on delivery, load it before quoting any efficiency figure at all: a `purchase` event is an
  order request, and the gap to delivered orders is the largest correction most Vietnamese reports
  are missing.
- What a commission arrangement actually pays, and what the person posting the link now owes by law:
  `affiliate-commerce.md` plus `data/affiliate-mechanics.csv`, `data/vn-advertising-law.csv` and
  `scripts/model_affiliate.py`. Load this before agreeing a rate from either side. The headline rate is
  charged on ordered value and paid on settled value, and four deductions sit between them, so a 10%
  deal reached 5.58% of attributed value on the worked example. Load it also before briefing a creator
  at all: Vietnamese law names the creator, sets no follower threshold, and prescribes no wording, and
  the same decree that fines partial disclosure also ends the arrangement outright for borrowed content.
- Which customer source can answer the question you actually have, how many people a theme needs before
  it is a theme, and whether a share may be spoken out loud: `customer-evidence.md` plus
  `data/evidence-sources.csv` and `scripts/check_evidence_saturation.py`. Load this before quoting any
  percentage taken from interviews, reviews, tickets or chat threads, and before writing "customers
  said" - twenty interviews close a theme list and license no percentage at all.
- How real organisations run marketing, what the largest advertisers disclose, and which benchmark may be
  quoted at whom: `how-companies-market.md` plus `data/marketing-benchmarks.csv`. Load this before
  answering "how much should we spend" or "how do companies like us do this".

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
