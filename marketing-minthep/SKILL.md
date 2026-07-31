---
name: marketing-minthep
description: "All-in-one marketing for marketers and non-marketers alike. Use for market research and sizing, competitor and audience analysis, positioning, offer and pricing, brand voice, copywriting (ads, landing page, PDP, email, social, script), campaign and launch planning, content calendar, paid media creative, SEO, PR and press kit, sales deck, creator/UGC briefs, lifecycle and retention flows, product photography and key visual direction, image editing and retouch, virtual person and makeup direction, colour palettes, menu/poster/wireframe layout rendered as real SVG or HTML, video shot sequencing with continuity, provider prompts for GPT Image or Nano Banana, creative QA and experiment read-outs. Vietnamese too: quảng cáo, chiến dịch, thương hiệu, định vị, viết content, thiết kế menu, bố cục, chỉnh sửa ảnh, ảnh sản phẩm, màu sắc, kịch bản video, kế hoạch marketing từ đầu. Writes bilingual VI/EN deliverables to disk and labels every fact confirmed, observed, inferred, or unknown."
---

# Marketing-Minthep

Turn one incomplete brief into the smallest complete system that creates demand, helps a buyer decide, produces assets, and learns from results. Assume the user is not a marketer: lead with the decision, not the vocabulary.

## Resolve the resource root first

Every path here - `references/`, `data/`, `scripts/`, `assets/` - is relative to the skill root, and some runtimes load this file alone without its folders. Then the paths resolve to nothing, and answering from memory produces the exact failure this skill exists to prevent: invented craft values presented as looked-up ones. So resolve the root before anything else. Take the first candidate holding both `references/` and `scripts/`: the directory containing this `SKILL.md`; `~/.claude/skills/marketing-minthep` or `~/.codex/skills/marketing-minthep`; a working copy of the repository, found by searching the mounted folders for the marker `marketing-minthep/scripts/find_recipe.py`. Look for the marker, never a hardcoded path. Then list `references/` and `data/` and confirm the reference your pipeline names is really there.

If none of them has it, say so, name what you could not read, and work only from what this file states. Do not rebuild a table from memory, cite a reference you did not open, or claim a script ran. `scripts/install_global.py --check` reports drift between the repository and an installed copy; a copy behind the source answers with stale knowledge silently. Adapt tool calls to the active runtime, and never claim that a research tool, browser, image provider, or subagent was used unless it was actually available and invoked.

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
| `rewrite-human` | A draft exists and reads machine-written or machine-translated. Also the route for transcreating approved copy between Vietnamese and English. |
| `score-kpi` | Targets have to be set, weighted, cascaded to a team or a person, or scored at period end. Covers balanced scorecards, marketing KPI trees, and the arithmetic of an achievement rate. |
| `virtual-model` | A recurring fictional presenter, brand ambassador, or AI model needs many looks with one consistent identity, dressed in outfits rather than photographed on a real person. |

`scripts/start_workbench.py` selects the pipeline and creates linked supporting runs when one request spans several. Run it rather than choosing by intuition; override it only when you can say why. Run `scripts/list_capabilities.py [--query TERM]` any time the current list of pipelines, references, data tables, and scripts is needed; it reads the repository instead of a written summary that can drift.

### The command surface

A pipeline is a route. Underneath it sit 28 named commands in `data/command-artifacts.csv`, grouped as `discover` (brainstorm, research, investigate, survey), `decide` (segment, position, offer, plan, budget), `create` (brief, write, humanise, localise, schedule), `direct` (compose, colour, identify, stage, shoot, generate, expand), `activate` (produce, adapt, approve, launch) and `evaluate` (measure, diagnose, improve).

Each command declares what it cannot run without, what it produces, what it refuses, and what it does not do. That last column is load-bearing: a request almost never arrives at the start of the work, so the useful answer is which commands are already satisfied and which are missing. Do not narrate that chain — resolve it. `scripts/plan_command_chain.py --goal COMMAND --have ARTEFACT...` returns the commands in an order where every input exists before it runs, and `--explain COMMAND` prints one command's contract. Read `references/command-surface.md` before adding, renaming, or reordering a command; the graph is what several other scripts join against.

Two things the graph cannot see, and both change the answer. It does not know that the person running the chain is also answering the inbox — that is `vietnam-operating-reality.md` plus `scripts/plan_operating_load.py`, which counts the week rather than describing it. And it does not know whether the source material can carry the frames the chain assumes — that is `product-composition-set.md` plus `scripts/plan_composition_set.py`, which answers "can AI make the rest of my photos" with a count instead of a promise: seven of eighteen slots from one photograph, eight needing a second exposure.

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
| Pose, body, figure construction, camera distance | `figure-and-pose.md`, `human-imagery.md` |
| Recurring virtual brand person | `virtual-person-system.md`, `rights-and-claims.md` |
| Image edit or composite | `image-editing.md`, `prompt-contracts.md` |
| Provider execution | `api-image-orchestration.md`, `provider-compilers.md` |
| Food, restaurant, dish, menu | `menu-engineering.md`, `menu-design.md`, `product-imagery.md` |
| Visual QA and export | `anti-ai-quality.md`, `creative-evaluation.md`, `production-pipeline.md` |
| Claims that will be published | `claims-proof-ledger.md`, `rights-and-claims.md` |
| Copy that reads machine-written, or translated word for word | `specificity.md` first, then `rewrite-human.md`, `copywriting.md` |
| A draft that flows well and says nothing a competitor could not say | `specificity.md` plus `scripts/check_specificity.py` |
| Targets, weights, achievement rates, a scorecard to cascade or score | `kpi-scorecards.md`, `claims-proof-ledger.md` |
| Naming a colour, pairing two, or answering a colour-psychology claim | `colour-combination.md` plus `data/colour-gates.csv` |
| One person holding every marketing role, or a plan for a shop with no team | `vietnam-operating-reality.md` |
| How many frames one existing photograph can produce, and what is legal as a marketplace main image | `product-composition-set.md` |
| Any Vietnamese copy: who it addresses, and whether it holds that choice | `address-register.md` plus `data/address-registers.csv` |
| Where a number came from, and how real companies actually market | `market-data-collection.md`, `how-companies-market.md` |

## Look it up, do not recall it

`data/` holds twenty-three tables, all queryable through `scripts/find_recipe.py`. Query them instead of writing craft values from memory, because a remembered lighting setup is a guess and a table row is a decision somebody already made and wrote down why. The eight a run reaches for directly are below; `frame-ratios.csv`, `composition-grids.csv` and `reference-axes.csv` are documented with the reference sheets they draw, and `makeup-looks.csv` (47 looks across thirteen families) and `makeup-diagnostics.csv` (15 questions) with the identification script below and in `makeup-art-direction.md`. Four carry evidence rather than craft: `market-data-sources.csv` (37 sources with the HTTP status each returned and what it cannot see), `marketing-benchmarks.csv` (35 claims, each with its sample, how the source was actually reached, and what it does not establish), `mark-scale-ladder.csv` (the per-slot detail budget behind `identity-design.md`), and `reference-observations.csv` (post-level pose, light and makeup observations cited by URL, no image stored). Six are structural, each read by the script named beside it: `command-artifacts.csv`, `vn-marketer-roles.csv`, `colour-gates.csv`, `product-compositions.csv`, `person-parameters.csv` (35 measurable axes for a virtual person - face and build as ratios and head units, pose and camera as angles and distances, nineteen locked as identity and sixteen free as campaign styling, each row carrying the source of its term or an explicit record that none was found; read by `scripts/plan_virtual_person.py`, which hashes the locked block so the same person renders twice, and explained in `figure-and-pose.md`) and `address-registers.csv` (25 Vietnamese address forms with the first person each takes, the forms it may appear beside, and the channel it fits — read by `scripts/check_address_register.py`, documented in `address-register.md`). Never quote a benchmark without the `what_it_does_not_establish` cell beside it.

| Table | Rows | What it settles |
|---|---|---|
| `image-recipes.csv` | 39 | The whole craft of one image: subject action, scene, lighting, camera, materials, ratio, copy-safe area, what to avoid, and the specific way that recipe fails |
| `palettes.csv` | 20 | Background, ink, accent, support, plus the measured contrast of each pair and whether the accent may carry text at all |
| `layout-dials.csv` | 17 | The numbers that make a layout, each with a range, three theme defaults, what raising it does, and where it breaks |
| `slop-tells.csv` | 33 | Every AI-slop tell across prompt, image, copy, layout, and campaign, scoped to the recipes it can occur in |
| `copy-formulas.csv` | 22 | 22 structures with a worked VI and EN example, when each fails, and a plain-language note for someone who has never written an ad |
| `translation-tells.csv` | 42 | Every calque, machine-cadence, evidence-adjective, hedge and address-register tell in VI and EN, each with a detection regex, why it survives translation, and the specific repair. The `evidence` and `hedge` layers are re-read per sentence by `scripts/check_specificity.py`, which is how `premium` beside a fact is separated from `premium` standing in for one |
| `kpi-metrics.csv` | 27 | Each measurable: its aspect, unit, which direction is good, how it is calculated, whether it is financial, whether it leads or lags, when to use it, and the specific way it gets gamed |
| `kpi-aspect-weights.csv` | 16 | What share of a card each aspect should carry at company, front-office, middle-office and back-office level, with the reason the share differs |

Search by the job, in Vietnamese or English — `--query "giao đồ ăn"`, not a style name. Then `--brief RECIPE_ID [--palette PALETTE_ID]` composes a brief `scripts/compile_prompt.py` accepts, with every field only the owner can know left as an explicit `TBD` and a `_tbd` block saying why each one must come from them; fill those from the truth map and never guess `product_truth`. And `--checklist RECIPE_ID` prints what to look at on the render, filtered to the tells that can actually occur in that frame and ordered by severity — look at the render against it, because re-reading the prompt proves nothing.

`scripts/render_refsheet.py` draws six reference sheets as real SVG from those same tables, with no API key and no image provider: `--sheet lighting` (six setups in plan view, shadow drawn from the key so it always agrees with the light), `--sheet frames` (every placement at true proportion with the copy reserve and the platform's own interface bands shaded), `--sheet palettes` (every palette as a card with its measured ratio printed on it), `--sheet dials --dial NAME` (one layout drawn three times at the minimum, default and maximum of one number), `--sheet reference` (the 11 axes that decide which half of a borrowed picture you may keep), `--sheet ratios` (twelve delivery ratios at true proportion with thirds, the phi line and the dynamic-symmetry eye drawn on each, so the golden-ratio question gets settled by looking instead of asserting). Show a sheet to a non-marketer instead of describing it; the dial sheet is how the layout mechanism gets explained in a second rather than a paragraph.

`scripts/score_kpi.py --input CARD.json` scores a scorecard rather than dividing actual by target. An achievement rate has four branches depending on whether the KPI is a ratio, a rung scale, a date, or already given as a percentage, and choosing the wrong branch changes the number without changing its plausibility. The script picks the branch from the row, applies the cap that belongs to that aspect, and refuses — exit 1, no total printed — when a KPI has no measured actual or two KPIs share a code. A partial total presented as a total looks finished. Read `references/kpi-scorecards.md` before designing a card, and run `assets/examples/bsc-2024/` first: it is a real card whose reported total is right by coincidence, because two opposite errors cancel.

`scripts/check_test_readout.py` decides whether a test is readable before anybody acts on it. `learning-loop.md` has always said never to declare a winner from tiny delivery, which was unenforceable, because tiny is not a number anyone picks — it falls out of the baseline rate and the lift worth detecting, and at a 3% conversion rate a 20% lift needs about fourteen thousand clicks per arm. `--plan --baseline 0.03 --mde 0.30` sizes the test while the answer is still cheap. `--claim B` checks a winner somebody has already decided on against the confidence interval rather than the point estimate, which is what refuses a headline 58% lift sitting at p = 0.29. It also grades two cases nobody reports on themselves: significant below the planned size, which is what a false positive looks like just before it becomes a brand rule, and arms more than 1.2x apart, where the platform has chosen between them so the split is a result rather than a setup. No difference at adequate size is a decision too — stop paying to make the more expensive variant. `--self-check` verifies its own arithmetic by inverting for sample size and then running the power function forward on the answer, because a statistics helper checked against a remembered calculator output is a random number generator with units.

`scripts/read_makeup.py` identifies the makeup in a reference photo by asking rather than labelling, because misidentification — gradient lip briefed as overline, mul-gwang briefed as glass skin — is the failure mode, not ignorance. `--observe "wet skin, no crease, blush under the eye"` (free text, VI or EN, diacritics optional) ranks the looks by which observations each accounts for, prints the discriminator between candidates it cannot yet tell apart, then the question that would cut the shortlist most, recomputed against the shortlist each time. `--brief LOOK_ID` prints the nine-axis contract with the light it needs, when it argues against the product, and the four questions no photograph answers — rights, product-versus-claim, delivery size, market. Exit 2 means several candidates survive: keep asking, do not pick.

`references/dossiers/` holds long-form research behind these references; open one only when a decision needs depth the short reference cannot settle, and read the section rather than the file — its `README.md` lists what each answers. If `BRAND.md` exists, read it before public-facing work; otherwise use `assets/templates/brand-context.md` only when continuity matters, and mark inferred fields.

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
5. **Creative and images.** Start at `scripts/find_recipe.py`: find the recipe by the job, compose the brief, fill in the `TBD` fields from the truth map, and keep its `--checklist` open while you look at the result. Map every reference by `identity`, `product`, `pose`, `composition`, `lighting`, `styling`, `makeup`, `color-grade`, or `texture`, then separate locks, freedoms, and rejects. Use `scripts/plan_design_options.py` for option cards, `scripts/render_mockup.py` to render a real menu or wireframe, `scripts/render_social_post.py` to render a real feed or story post with its caption sheet, `scripts/compile_prompt.py` for provider-ready prompts, and `scripts/generate_image.py` to call a configured provider directly when `MINTHEP_IMAGE_KEY` is set (`--dry-run` needs no key). For variants, branch from identical inputs and change one named axis. When the user asks to change, fix, restyle, retouch, replace, remove, extend, recompose, or "sửa" an image, take the edit route: inspect the source, build the lock map, invoke a real edit capability, and compare the result against the locks. If editing is unavailable, return an executable edit prompt with exact mask instructions.
6. **Content first: count the facts.** Before measuring how a draft reads, run `scripts/check_specificity.py --check <file>` to find out whether it says anything. It counts the four things a competitor could not copy - a number carrying a unit, a date, a proper name, a way to reach somebody - and reports the share of sentences carrying none, which is the brand-swap test made arithmetic. Under three checkable facts, stop: the draft has a content problem, and every rhythm edit from here makes it read better while still saying nothing. Do this in this order and not the other, because rhythm work quietly deletes specifics - a specific is the awkward part of a sentence, and `Giao trong 2 giờ ở Gò Vấp` flows worse than `Giao hàng nhanh chóng, tận tâm`. The gate that repays reading is `empty-adjective`: `premium` next to `ủ 80 giờ` summarises a fact, `premium` alone in its sentence replaced one, so the repair is to put the fact back rather than to delete the adjective. Only a percentage or a multiplier needs a source; a price, a stock count and a discount are the brand's own facts. Follow `specificity.md`.
7. **Cadence, decoration, register.** Then run `scripts/rewrite_human.py --check <file> --channel <where it goes>`. It measures what a reread cannot see - sentence-length uniformity, missing landing beats, em-dash density - and matches the tells in `data/translation-tells.csv` that survive translation between Vietnamese and English while staying grammatical. It also counts pictographs, separating one a writer put in a sentence from one opening every bullet: the default channel is `deliverable`, where the budget is zero, and social and chat are the only surfaces where structural use is native. Repair calques first, then rebuild rhythm; the order matters because deleting a connective changes every length measurement after it. On Vietnamese copy, finish with `scripts/check_address_register.py --check <file> --channel <...>`, because Vietnamese has no neutral second person and a translated draft re-decides who the reader is at every sentence. Follow `rewrite-human.md` and `address-register.md`. Do not lower a target to pass, and do not add texture on top of flat prose: variation comes from the content deciding where it needs a beat.
8. **Channel.** Recompose per ratio and placement; do not blindly crop. A story is laid out again, not cropped from the feed post, and the bands the app draws its own interface over stay empty. Verify the live official spec before export. Preserve masters, safe zones, captions, alt text, disclosures, credits, naming, version, and approval state.
9. **QA and decide.** Reject critical failures in product or identity fidelity, anatomy, physics, claims, disclosure, consent, rights, channel compliance, or message continuity. Tie every test to one hypothesis and guardrail. Never call a causal winner from CTR alone or from mixed conditions.
10. **Learn.** Record asset ID, parent concept, audience, placement, proof, offer, CTA, spend, funnel metrics, result, rejection reason, next action. Feed objections, returns, comments, and sales feedback into the next brief.

## Delivery modes

- `focused`: one pipeline, assumptions, recommended direction, requested artifacts, QA, next step. The default. Expand only when the user asks for a system or production scope, or the work genuinely depends on several pipelines.
- `system`: connected strategy plus the minimum cross-channel asset and measurement system.
- `production`: machine-readable brief, manifests, provider prompts, specs, owners, approvals, export handoff.

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
