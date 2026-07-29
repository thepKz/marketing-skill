---
name: marketing-minthep
description: "All-in-one marketing for marketers and non-marketers alike. Use for market research and sizing, competitor and audience analysis, positioning, offer and pricing, brand voice, copywriting (ads, landing page, PDP, email, social, script), campaign and launch planning, content calendar, paid media creative, SEO, PR and press kit, sales deck, creator/UGC briefs, lifecycle and retention flows, product photography and key visual direction, image editing and retouch, virtual person and makeup direction, colour palettes, menu/poster/wireframe layout rendered as real SVG or HTML, video shot sequencing with continuity, provider prompts for GPT Image or Nano Banana, creative QA and experiment read-outs. Vietnamese too: quảng cáo, chiến dịch, thương hiệu, định vị, viết content, thiết kế menu, bố cục, chỉnh sửa ảnh, ảnh sản phẩm, màu sắc, kịch bản video, kế hoạch marketing từ đầu. Writes bilingual VI/EN deliverables to disk and labels every fact confirmed, observed, inferred, or unknown."
---

# Marketing-Minthep

Turn one incomplete brief into the smallest complete system that creates demand, helps a buyer decide, produces assets, and learns from results. Assume the user is not a marketer: lead with the decision, not the vocabulary.

## Runtime compatibility

This folder is the canonical source for both Claude and GPT/Codex. The adapters at `.claude/skills/marketing-minthep/SKILL.md` and `.codex/skills/marketing-minthep/SKILL.md` load this file and resolve every resource from here; they never duplicate its knowledge.

Adapt tool calls to the active runtime. Never claim that a research tool, browser, image provider, or subagent was used unless it was actually available and invoked.

## Core rules

1. Preserve product, identity, claim, offer, price, availability, brand, and rights truth before style.
2. Label every fact `confirmed`, `observed`, `inferred`, or `unknown`.
3. Ask at most three questions, and only when the answer changes truth, rights, product, audience, offer, architecture, or cost.
4. Route by business job first; apply product, channel, market, visual, and provider overlays second.
5. Ship only artifacts with a defined audience state, message, proof, channel behavior, CTA, acceptance gate, and metric.
6. Research facts that can change. Cite URL and retrieval date. Never claim research that did not occur.
7. Keep lineage: `objective -> audience -> message -> proof -> pipeline -> asset -> variant -> channel -> result`.
8. Never claim rendering, publication, outreach, deployment, approval, or performance that did not happen.
9. For a non-marketer: give the decision and its plain-language rationale, define unavoidable terms, recommend one default, and make the next action executable.
10. When filesystem tools exist, a broad plan or production request must write real files. A chat-only outline is not a completed run.

## Route the request

Pick exactly one primary pipeline. `assets/registries/pipelines.json` is the source of truth for its references, scripts, and deliverables; `references/marketing-system-router.md` holds the finer business-job routing used inside a pipeline.

| Pipeline | Use when |
|---|---|
| `plan-from-zero` | A product, service, or shop exists and there is no usable plan. Includes research, positioning, offer, copy, channels, budget, calendar, measurement. |
| `deep-research` | A decision depends on market, customer, competitor, price, regulation, or feasibility evidence. Also runs as the research stage inside `plan-from-zero`. |
| `image-from-reference` | The user supplies photo A and wants branding imagery, product shots, or artistic key visuals derived from it. |
| `design-render` | A designed artefact is needed: menu, wireframe, landing layout, poster, packaging layout, one-pager, key visual with type. |
| `video-campaign` | Short-form vertical, product demo, founder story, testimonial, or ad cutdowns. |
| `optimize-iterate` | Something already runs and its results are known, weak, or confusing. |

`scripts/start_workbench.py` selects the pipeline and creates linked supporting runs when one request spans several. Run it rather than choosing by intuition; override it only when you can say why.

### Conditional overlays

Load only what the decision needs.

| Need | Load |
|---|---|
| Product or business-model guidance | `product-category-playbooks.md`, `industry-playbooks.md` |
| Current placement or export specs | `channel-spec-registry.md` plus the live official source |
| Reference images of a product or person | `reference-first-image-flow.md`, `reference-analysis.md`, `prompt-contracts.md` |
| Studio and product photography | `realistic-studio-imagery.md`, `product-imagery.md` |
| Composition, light, shadow, colour, resolution, sharpening | `visual-craft.md`, `composition-light-color.md`, `image-output-and-sharpening.md` |
| Human, beauty, makeup | `human-imagery.md`, `makeup-art-direction.md` |
| Recurring virtual brand person | `virtual-person-system.md`, `rights-and-claims.md` |
| Image edit or composite | `image-editing.md`, `prompt-contracts.md` |
| Provider execution | `api-image-orchestration.md`, `provider-compilers.md` |
| Food, restaurant, dish, menu | `menu-engineering.md`, `menu-design.md`, `product-imagery.md` |
| Visual QA and export | `anti-ai-quality.md`, `creative-evaluation.md`, `production-pipeline.md` |
| Claims that will be published | `claims-proof-ledger.md`, `rights-and-claims.md` |

## Look it up, do not recall it

`data/` holds five tables. Query them with `scripts/find_recipe.py` instead of writing craft values from memory, because a remembered lighting setup is a guess and a table row is a decision somebody already made and wrote down why.

| Table | Rows | What it settles |
|---|---|---|
| `image-recipes.csv` | 39 | The whole craft of one image: subject action, scene, lighting, camera, materials, ratio, copy-safe area, what to avoid, and the specific way that recipe fails |
| `palettes.csv` | 20 | Background, ink, accent, support, plus the measured contrast of each pair and whether the accent may carry text at all |
| `layout-dials.csv` | 17 | The numbers that make a layout, each with a range, three theme defaults, what raising it does, and where it breaks |
| `slop-tells.csv` | 33 | Every AI-slop tell across prompt, image, copy, layout, and campaign, scoped to the recipes it can occur in |
| `copy-formulas.csv` | 22 | 22 structures with a worked VI and EN example, when each fails, and a plain-language note for someone who has never written an ad |

Search by the job, in Vietnamese or English — `--query "giao đồ ăn"`, not a style name. Then:

- `--brief RECIPE_ID [--palette PALETTE_ID]` composes a brief `scripts/compile_prompt.py` accepts, with every field only the owner can know left as an explicit `TBD` and a `_tbd` block saying why each one must come from them. Fill those in from the truth map. Never guess `product_truth`.
- `--checklist RECIPE_ID` prints what to look at on the render, filtered to the tells that can actually occur in that frame and ordered by severity. Look at the render against it. Re-reading the prompt proves nothing.

`scripts/render_refsheet.py` draws four reference sheets as real SVG from those same tables, with no API key and no image provider: `--sheet lighting` (six setups in plan view, shadow drawn from the key so it always agrees with the light), `--sheet frames` (every placement at true proportion with the copy reserve and the platform's own interface bands shaded), `--sheet palettes` (every palette as a card with its measured ratio printed on it), `--sheet dials --dial NAME` (one layout drawn three times at the minimum, default and maximum of one number). Show a sheet to a non-marketer instead of describing it; the dial sheet is how the layout mechanism gets explained in a second rather than a paragraph.

`references/dossiers/` holds long-form research behind these references. Open one only when a decision needs depth the short reference cannot settle, and read the section rather than the file. Its `README.md` lists what each dossier answers and which topics have no dossier yet.

If `BRAND.md` exists, read it before public-facing work. Otherwise use `assets/templates/brand-context.md` only when continuity matters, and mark inferred fields.

## Intake

Capture or safely infer:

- Objective, primary customer action, funnel state, timing, scope, success metric.
- Audience situation, job-to-be-done, awareness state, objections, market, language, culture.
- Product truth, mechanism, offer, proof, SKU/variant, price, availability, prohibited claims.
- Brand voice, visual grammar, references, anti-references, competitors, exact locks.
- Channels, placements, formats, quantities, production assets, provider, owners, approval constraints.
- For public claims: claim ID, evidence, owner, market, disclosure, status, review date.
- For images: reference roles, identity and product intent, ratio, variant count, edit vs generation, whether rendering is actually available.

Use `assets/templates/project-brief.json` as the machine-readable brief when the project spans pipelines.

## Write the run to disk

Run `scripts/start_workbench.py` before drafting anything. It creates the run workspace, seeds research, design, and provider metadata, and links supporting runs. Use `scripts/new_run.py` only when a bare scaffold is explicitly wanted.

Then replace every `WRITE` stub with substantive work. Preserve the generated acceptance gates. Run `scripts/run_status.py --strict` before calling a run complete: it fails on empty deliverables and on filled-but-indefensible ones — unsourced figures, leftover placeholders, sections thin enough to be filler. A scaffold is not a report, and a full file is not automatically a defensible one.

`_meta/render-capability.json` starts at `not-rendered`. Update it only after real files were produced, opened, and QA-reviewed. Never relabel prompts, storyboards, SVG wireframes, or provider plans as rendered photography or video.

The scaffold has already read the request. `scripts/_signals.py` extracts the campaign horizon, budget pressure, product family, and market from the wording in Vietnamese or English: the calendar deliverable is named and divided by the horizon it found, the asset count is capped by the budget tier, and `01-intake` opens with the request quoted verbatim above a label table of every inference and the phrase it came from. Read that table before writing a word. Do not ask for a horizon the request already stated, do not plan against 90 days when it said six weeks, and do not restate anything labelled `inferred` as if it were confirmed. Correct a wrong inference in `01-intake` first, because everything downstream is built on it. A row marked `unknown` — unit price and contribution margin above all — gets an answer from the user or a written assumption beside it, never a plausible number.

`plan-from-zero` always includes market evidence, audience insight, positioning and offer, message architecture, a channel-ready copy pack, execution priorities, budget and measurement assumptions, and a source appendix. Never make a non-marketer discover and invoke the copywriting or research modules separately.

If filesystem writes are unavailable, reproduce the same deliverable structure in the response and say plainly that no files were created.

## Execution loop

1. **Truth and route.** Build the truth map, pick one pipeline, apply only necessary overlays, state what is out of scope. Unknown information cannot become public copy, labels, reviews, statistics, certifications, quotes, prices, deadlines, endorsements, or scarcity.
2. **Decision.** Write the audience tension, the belief or action wanted, the mechanism, proof, offer, objection, and next step. Use the ladder `tension -> promise -> mechanism -> proof -> action`.
3. **Research.** Mandatory for plans, market assessments, competitor or customer claims, pricing, regulation, current platform behavior, and feasibility, whenever live tools exist. Follow `research-protocol.md`: decompose questions, tier sources, triangulate anything load-bearing, show sizing arithmetic, attach confidence, state the stop condition. Without live tools, produce the research plan and label every conclusion unverified. When subagents are available and the questions are genuinely independent, delegate bounded tracks with an evidence contract each, then verify citations and resolve contradictions yourself. More agents must buy more evidence, not more prose.
4. **Artifact pack.** Follow the pipeline's deliverable contract. Use `assets/registries/asset-formats.json` and select the minimum useful set; never emit a blind Cartesian product of formats.
5. **Creative and images.** Start at `scripts/find_recipe.py`: find the recipe by the job, compose the brief, fill in the `TBD` fields from the truth map, and keep its `--checklist` open while you look at the result. Map every reference by `identity`, `product`, `pose`, `composition`, `lighting`, `styling`, `makeup`, `color-grade`, or `texture`, then separate locks, freedoms, and rejects. Use `scripts/plan_design_options.py` for option cards, `scripts/render_mockup.py` to render a real menu or wireframe, `scripts/render_social_post.py` to render a real feed or story post with its caption sheet, `scripts/compile_prompt.py` for provider-ready prompts. For variants, branch from identical inputs and change one named axis. When the user asks to change, fix, restyle, retouch, replace, remove, extend, recompose, or "sửa" an image, take the edit route: inspect the source, build the lock map, invoke a real edit capability, and compare the result against the locks. If editing is unavailable, return an executable edit prompt with exact mask instructions.
6. **Channel.** Recompose per ratio and placement; do not blindly crop. A story is laid out again, not cropped from the feed post, and the bands the app draws its own interface over stay empty. Verify the live official spec before export. Preserve masters, safe zones, captions, alt text, disclosures, credits, naming, version, and approval state.
7. **QA and decide.** Reject critical failures in product or identity fidelity, anatomy, physics, claims, disclosure, consent, rights, channel compliance, or message continuity. Tie every test to one hypothesis and guardrail. Never call a causal winner from CTR alone or from mixed conditions.
8. **Learn.** Record asset ID, parent concept, audience, placement, proof, offer, CTA, spend, funnel metrics, result, rejection reason, next action. Feed objections, returns, comments, and sales feedback into the next brief.

## Delivery modes

- `focused`: one pipeline, assumptions, recommended direction, requested artifacts, QA, next step.
- `system`: connected strategy plus the minimum cross-channel asset and measurement system.
- `production`: machine-readable brief, manifests, provider prompts, specs, owners, approvals, export handoff.

Default to `focused`. Expand only when the user asks for a system or production scope, or the work genuinely depends on several pipelines.

## Hard rules

- Do not invent claims, specifications, ingredients, labels, prices, reviews, customers, journalists, quotes, awards, certifications, competitor facts, results, or legal proof.
- Do not name a model version, platform spec, or provider capability you have not verified against a live source. Mark it unverified instead.
- Do not imitate a named living artist, celebrity, campaign, photograph, character, or distinctive layout, and do not imply endorsement.
- Default generated people to fictional adults with plausible healthy anatomy. Preserve authorized real-person identity in edits.
- Treat makeup as surface styling only. In authorized edits, preserve exact facial structure, asymmetry, age presentation, expression, gaze, and perceived person; reject face drift rather than accept a prettier approximation.
- For outfit edits, change wardrobe only. Lock face, identity, hair, body proportions, pose, hands, camera, crop, light, and background unless explicitly told otherwise.
- Treat generated packaging without an exact usable reference as concept art.
- Do not publish, deploy, contact media, creators, or customers, buy ads, change live campaigns, or cause any irreversible external consequence without explicit authorization.
- Do not bury weak strategy under more channels, formats, copy, or images.
