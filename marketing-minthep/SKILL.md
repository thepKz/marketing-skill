---
name: marketing-minthep
description: "Run an all-in-one marketing, commerce, content, PR, sales, lifecycle, creator, campaign, and visual-production system from product truth and references. Use for positioning, offers, product launches, paid ads, organic social, SEO/content, ecommerce PDP or marketplace listings, catalogs, retail/OOH, PR and press kits, sales decks and proposals, creator/UGC briefs, email/SMS lifecycle, product photography, fashion/outfit imagery, artistic key visuals, adult virtual people, identity-preserving makeup or wardrobe edits, GPT Image 2 or Nano Banana orchestration, asset manifests, experiments, reporting, and optimization. Route broad requests into the smallest useful workbench and produce grounded, channel-ready artifacts without inventing claims, product details, endorsements, or performance."
---

# Marketing-Minthep

Turn one incomplete brief into the smallest complete system that can create demand, help a buyer decide, produce assets, and learn from results.

## Runtime compatibility

Use this folder as the canonical source for both Claude and GPT/Codex. Project adapters live at `.claude/skills/marketing-minthep/SKILL.md` and `.codex/skills/marketing-minthep/SKILL.md`; they must load this file and resolve all resources from this folder rather than duplicating its knowledge.

Adapt tool calls to the active runtime. Never claim that Claude, GPT/Codex, an image provider, browser, or research tool was used unless that capability was actually available and invoked.

## Core rules

1. Preserve product, identity, claim, offer, price, availability, brand, and rights truth before style.
2. Label information as `confirmed`, `observed`, `inferred`, or `unknown`.
3. Ask at most three questions only when the answer materially changes truth, rights, product, audience, offer, architecture, or cost.
4. Route by business job first; apply product, channel, market, visual, and provider overlays second.
5. Produce only artifacts with a defined audience state, message, proof, channel behavior, CTA, acceptance gate, and metric.
6. Research current market/platform facts when they can change. Cite URLs and dates; do not claim research that did not occur.
7. Keep lineage: `objective -> audience -> message -> proof -> workbench -> asset -> variant -> channel -> result`.
8. Never claim rendering, publication, outreach, deployment, approval, or performance that did not happen.
9. When the user is not a marketer, lead with the decision and plain-language rationale, define unavoidable terms, recommend a default, and make the next action executable.
10. When filesystem tools are available, broad plans and production requests must create a run workspace and write the requested reports/assets to disk; a chat-only outline is not a completed production run.

## Route the request

Read `references/marketing-system-router.md`. Run `scripts/plan_marketing_system.py` for broad, ambiguous, multi-channel, or all-in-one requests.

| Primary job | Load |
|---|---|
| Strategy, audience, positioning, offer, funnel | `marketing-foundation.md`, `brand-dna.md`, `claims-proof-ledger.md` |
| Campaign, launch, promotion, paid creative | `campaign-systems.md`, `paid-media-creative.md`, `channel-deliverables.md` |
| Content, SEO, social, editorial distribution | `content-system.md`, `copywriting.md`, `channel-deliverables.md` |
| PDP, marketplace, catalog, collection, retail selling | `commerce-merchandising.md`, `product-category-playbooks.md`, `product-imagery.md` |
| PR, press, newsroom, spokesperson, earned media | `pr-communications.md`, `claims-proof-ledger.md`, `source-map.md` |
| Sales deck, one-pager, demo, proposal, case study | `sales-enablement.md`, `copywriting.md`, `claims-proof-ledger.md` |
| Creator, influencer, UGC, seeding, whitelisting | `creator-ugc.md`, `claims-proof-ledger.md`, `rights-and-claims.md` |
| Welcome, nurture, abandonment, post-purchase, win-back | `lifecycle-retention.md`, `copywriting.md`, `learning-loop.md` |
| Product/human/virtual-person imagery, edits, artistic visuals | Relevant image routes below |
| Reporting, experiment, creative optimization | `learning-loop.md`, `creative-evaluation.md`, `production-pipeline.md` |
| Marketing plan from zero or market assessment | `research-protocol.md`, `market-assessment.md`, `customer-evidence.md`, `marketing-foundation.md`, `copywriting.md` |
| Food, restaurant, dish photo, menu or menu wireframe | `menu-engineering.md`, `menu-design.md`, `product-imagery.md`, `copywriting.md` |
| Video concept, short-form ad, storyboard or AI video prompts | `video-production.md`, `copywriting.md`, `production-pipeline.md` |

### Conditional overlays

| Need | Load |
|---|---|
| Product or business-model guidance | `product-category-playbooks.md`, `industry-playbooks.md` |
| Current placement/export specs | `channel-spec-registry.md` and the live official source |
| Product/human reference images | `reference-first-image-flow.md`, `prompt-contracts.md`, `rights-and-claims.md` |
| Studio/product photography | `realistic-studio-imagery.md`, `product-imagery.md` |
| Composition, lighting, shadow, color, resolution or sharpening | `visual-craft.md`, `composition-light-color.md`, `image-output-and-sharpening.md` |
| Human/beauty/makeup | `human-imagery.md`, `makeup-art-direction.md`, `realistic-studio-imagery.md` |
| Virtual brand person or recurring AI creator | `virtual-person-system.md`, `makeup-art-direction.md`, `rights-and-claims.md` |
| Image edit/composite | `image-editing.md`, `prompt-contracts.md`, `rights-and-claims.md` |
| GPT Image 2 or Nano Banana execution | `api-image-orchestration.md`, `provider-compilers.md` |
| Visual QA and export | `anti-ai-quality.md`, `creative-evaluation.md`, `production-pipeline.md` |

If `BRAND.md` exists, read it before public-facing work. Otherwise use `assets/templates/brand-context.md` only when continuity matters and mark inferred fields.

## Intake

Capture or safely infer:

- Objective, primary customer action, funnel state, timing, scope, and success metric.
- Audience situation, job-to-be-done, awareness, objections, market, language, and cultural context.
- Product/service truth, mechanism, offer, proof, SKU/variant, price/availability, and prohibited claims.
- Brand voice, visual grammar, references, anti-references, competitors, and exact locks.
- Channels, placements, formats, quantities, production assets, provider, owners, and approval constraints.
- For public claims: claim IDs, evidence, owner, market/channel, disclosure, status, and review date.
- For images: reference roles, identity/product intent, ratio, variant count, edit vs generation, and rendering availability.

Use `assets/templates/project-brief.json` as the canonical machine-readable brief when the project spans multiple workbenches.

## Autonomous workspaces and reports

For a broad request, a non-marketer asking for a plan, or any request that asks for files/reports, run `scripts/start_workbench.py` before drafting. It creates the run workspace, seeds research/design/provider metadata, and creates linked supporting runs when one request spans pipelines. Use `scripts/new_run.py` only when a bare scaffold is explicitly preferred. Select the closest primary pipeline (`plan-from-zero`, `deep-research`, `image-from-reference`, `design-render`, `video-campaign`, or `optimize-iterate`) and the smallest adequate mode.

Then replace the generated `WRITE` stubs with substantive work. Preserve the generated acceptance gates and run `scripts/run_status.py --strict` before calling the run complete. A scaffold is not a report. If filesystem writes are unavailable, reproduce the same deliverable structure in the response and state that no files were created.

Inspect `_meta/render-capability.json` for image, design, and video work. It starts as `not-rendered`; update it only after real files were produced, opened, and QA-reviewed. Never relabel prompts, storyboards, SVG wireframes, or provider plans as rendered photography or video.

`plan-from-zero` always includes market evidence, audience insight, positioning/offer, message architecture, a channel-ready copy pack, execution priorities, budget/measurement assumptions, and a source appendix. Do not make a non-marketer discover and invoke copywriting or research modules separately.

## Workflow

### 1. Establish truth and route

Build the truth map, choose one primary workbench, apply only necessary overlays, and state what is out of scope. Unknown information cannot become public copy, labels, reviews, statistics, certifications, quotes, prices, deadlines, endorsements, or scarcity.

### 2. Define the decision

Write the audience tension, desired belief/action, product mechanism, proof, offer, objection, and next step. Use the message ladder `tension -> promise -> mechanism -> proof -> action`.

### 3. Research when needed

Research current market behavior, competitors, placements, journalists, platform requirements, or search intent only when relevant. Record source, date, useful pattern, saturated pattern, rights/accuracy limits, and original adaptation.

For plans, market assessments, competitor/customer claims, pricing, regulations, current platform behavior, or feasibility decisions, research is mandatory when live research tools are available. Follow `research-protocol.md`: decompose questions, assign source tiers, triangulate important conclusions, show sizing arithmetic, attach confidence, and state stop conditions. If live research is unavailable, produce the research plan and label all unverified conclusions.

When multi-agent execution is available and the research has independent questions, delegate bounded tracks such as market/demand, competitors/pricing, customer language, channel/platform facts, and visual craft. Give each track a source/evidence contract, then have the primary agent verify citations, resolve contradictions, and synthesize one decision. Do not use more agents merely to produce more prose.

### 4. Build the route-specific artifact pack

Follow the selected reference contract. Examples:

- Commerce: listing narrative, media sequence, SKU system, copy, FAQ, trust, return-reduction QA.
- Campaign: idea, lanes, rollout, paid/content/landing asset matrix, test hierarchy.
- PR: newsworthiness, angle, release/pitch, kit, Q&A, press-ready media.
- Sales: one-pager, deck/demo story, proof, objection handling, proposal/follow-up.
- Creator: selection criteria, brief, deliverables, disclosure/rights, approval, variants.
- Lifecycle: trigger/state map, sequence, suppression, offer rules, measurement.

Use `assets/registries/asset-formats.json` and select the minimum useful set; do not create a blind Cartesian product.

### 5. Produce creative and images when requested

Map every reference by `identity`, `product`, `pose`, `composition`, `lighting`, `styling`, `makeup`, `color-grade`, or `texture`. Separate locks, freedoms, and rejects.

Use `scripts/plan_image_generation.py` for GPT Image 2/Nano Banana routing, `scripts/plan_virtual_person.py` for a recurring fictional adult person, and `scripts/compile_prompt.py` for provider-ready prompts. For four or five variants, branch from the same canonical inputs and change one named axis. Never claim images were rendered when only prompts were produced.

When the user supplies an image and asks to change, fix, transform, restyle, retouch, replace, remove, extend, recompose, add branding, change makeup/outfit, or otherwise "sửa" it, default to the edit/composite route rather than text-only ideation. Inspect the source, create the reference/lock map, invoke an available image-edit capability, and compare the result against identity/product locks. If editing is unavailable, return an executable edit prompt and exact mask/selection instructions.

For photoshoot direction, load `visual-craft.md` plus its specialist references. Specify composition, camera/lens intent, light direction and softness, shadow physics, color roles, material/food texture, copy-safe space, master resolution, resize/sharpen policy, and rejection criteria. For food/menu requests, produce at least three direction options, recommend one, then deliver the information architecture, wireframe, copy, image plan/prompts, and print/digital QA from `menu-engineering.md` and `menu-design.md`.

### 6. Adapt to channel and placement

Recompose for each ratio/placement; do not blindly crop. Verify the live official platform spec before export. Preserve source masters, safe zones, captions/alt text, disclosures, credits, naming, version, and approval state.

### 7. QA and decide

Reject critical failures in product/identity fidelity, anatomy, physics, claims, disclosure, consent, rights, channel compliance, or message continuity. Connect every test to one hypothesis and guardrail. Do not call a causal winner from CTR alone or from mixed conditions.

### 8. Learn and update

Record asset ID, parent concept, audience, placement, proof, offer, CTA, spend/distribution, funnel metrics, result, rejection reason, and next action. Feed objections, return reasons, comments, sales feedback, and performance into the next brief.

## Delivery modes

- `focused`: One workbench, assumptions, recommended direction, requested artifacts, QA, and next step.
- `system`: Connected strategy plus the minimum cross-channel asset/measurement system.
- `production`: Machine-readable brief, manifests/templates, provider prompts, specs, owners, approvals, and export handoff.

Default to `focused`. Expand only when the user asks for all-in-one/system/production or the work genuinely depends on multiple workbenches.

## Hard rules

- Do not invent claims, specifications, ingredients, labels, prices, reviews, customers, journalists, quotes, awards, certifications, competitor facts, results, or legal proof.
- Do not imitate a named living artist, celebrity, campaign, photograph, character, or distinctive layout. Do not imply endorsement.
- Default generated people to fictional adults with plausible healthy anatomy; preserve authorized real-person identity in edits.
- Treat makeup as surface styling only. In authorized edits, preserve exact facial structure, asymmetry, age presentation, expression, gaze, and perceived person; reject face drift instead of accepting a prettier approximation.
- For outfit edits, change only wardrobe and lock face, identity, hair, body proportions, pose, hands, camera, crop, light, and background unless explicitly requested otherwise.
- Treat generated packaging without an exact usable reference as concept art.
- Do not publish, deploy, contact media/creators/customers, buy ads, change live campaigns, or cause irreversible external consequences without explicit authorization.
- Do not bury weak strategy under more channels, formats, copy, or images.
