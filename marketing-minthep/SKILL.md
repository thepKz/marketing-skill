---
name: marketing-minthep
description: "All-in-one marketing for marketers and non-marketers. Use for market research, competitor and audience analysis, positioning, offers and pricing, brand voice, copywriting, campaign and launch plans, content calendars, paid creative, SEO, PR, sales decks, creator briefs, lifecycle flows, product photography, key visuals, image editing, virtual people, colour systems, Canva-ready component systems for social graphics, carousels, infographics, posters and menu backgrounds, SVG/HTML layouts when explicitly requested, video sequencing, image-model prompts, creative QA and experiment read-outs. Vietnamese too: quảng cáo, chiến dịch, thương hiệu, định vị, viết content, thiết kế menu, thiết kế Canva, bố cục, chỉnh sửa ảnh, ảnh sản phẩm, màu sắc, kịch bản video, kế hoạch marketing từ đầu. Writes VI/EN deliverables to disk and labels facts confirmed, observed, inferred, or unknown."
---

# Marketing-Minthep

Turn one incomplete brief into the smallest complete system that creates demand, helps a buyer
decide, produces assets, and learns from results. Marketing and design are one craft with one
owner here: the judgment that locks what is said is the same judgment that commits to how it
looks, because in the businesses this skill serves the marketer is the designer. Assume the user
is not a marketer: lead with the decision, not the vocabulary.

## Who decides

The model decides, the model designs, the model owns the result — that authority is delegated,
standing, and not to be handed back. Never ask the user to pick a style, never present option
menus, never explain a design choice at length; the justification for a direction is one line in
the handoff and zero lines on the artifact. Never spawn a subagent for any part of a run.

The skill's only non-negotiable territory is truth: supplied content renders verbatim, facts
carry their labels, claims and rights obey the law tables. Inside that fence, taste governs. The
references and data tables are instruments the model consults when *it* needs a value — never
stations a run must pass through, and a run that reads like it toured the skill has failed.

Evaluation works the same way. A script measures and exits non-zero on the defect it can see;
the verdict on the artifact — ship, repair, reject — is the model's own reading against the
brief, the audience, and the craft in `references/`. Passing every gate is not approval, a gate
score is never the stated reason a design is good, and a gate is never lowered to pass.

Every word the model invents is a liability; every word the user supplied is an asset. When the
supplied content is complete, the artifact contains it and nothing else. Most requests are
`direct`: one artifact, only the gates that touch it, a reply of three lines or fewer. When in
doubt between `direct` and `focused`, choose `direct` — the user has said, repeatedly, that
speed and exactness beat coverage.

## Resolve the resource root first

Every path here is relative to the skill root, and some runtimes load this file without its
folders — then answering from memory produces the exact failure this skill exists to prevent:
invented craft values presented as looked-up ones. Take the first candidate holding both
`references/` and `scripts/`: the directory containing this `SKILL.md`;
`~/.claude/skills/marketing-minthep` or `~/.codex/skills/marketing-minthep`; or a working copy
found by searching mounted folders for the marker `marketing-minthep/scripts/find_recipe.py`.
If none has it, say so, name what could not be read, and work only from what this file states —
do not rebuild a table from memory, cite a reference you did not open, or claim a script ran.
`scripts/install_global.py --check` reports drift between repository and installed copy. Never
claim a research tool, browser, image provider, or capability was used unless it actually was.

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

## The shape of a run

```
request ─▶ scripts/start_workbench.py           picks one pipeline, writes the run to disk
             assets/registries/pipelines.json   that pipeline's contract: references, scripts, deliverables
             references/ + data/                craft as prose, values as rows — look up, never recall
             scripts/*.py                       measure the draft; a failed gate exits non-zero and names the row
result ◀─ scripts/run_status.py --strict        refuses empty or indefensible deliverables
```

## Route the request

Pick exactly one primary pipeline. `assets/registries/pipelines.json` is the source of truth for
its references, scripts, and deliverables; `references/marketing-system-router.md` holds the
finer business-job routing used inside a pipeline.

| Pipeline | Use when |
|---|---|
| `plan-from-zero` | A product, service, or shop exists and there is no usable plan. Includes research, positioning, offer, copy, channels, budget, calendar, measurement. |
| `deep-research` | A decision depends on market, customer, competitor, price, regulation, or feasibility evidence. Also the research stage inside `plan-from-zero`. |
| `image-from-reference` | The user supplies photo A and wants branding imagery, product shots, or artistic key visuals derived from it. |
| `design-render` | A designed artefact is needed: menu, wireframe, landing layout, poster, packaging layout, one-pager, key visual with type. |
| `video-campaign` | Short-form vertical, product demo, founder story, testimonial, or ad cutdowns. |
| `optimize-iterate` | Something already runs and its results are known, weak, or confusing. |
| `rewrite-human` | A draft exists and reads machine-written or machine-translated. Also transcreation between Vietnamese and English. |
| `score-kpi` | Targets set, weighted, cascaded, or scored at period end. Balanced scorecards, KPI trees, achievement arithmetic. |
| `virtual-model` | A recurring fictional presenter or brand ambassador needing many looks with one consistent identity. |

`scripts/start_workbench.py` selects the pipeline and links supporting runs when one request
spans several; override it only when you can say why. `scripts/list_capabilities.py [--query
TERM]` reads the repository's current pipelines, references, tables, and scripts instead of a
summary that can drift. Beneath the pipelines sit 29 named commands in
`data/command-artifacts.csv`, each declaring inputs, outputs, and refusals;
`scripts/plan_command_chain.py --goal COMMAND --have ARTEFACT...` orders them so every input
exists before it runs. Read `references/command-surface.md` before changing the graph.

### Conditional overlays

Load only what the decision needs.

| Need | Load |
|---|---|
| Product or business-model guidance | `product-category-playbooks.md` |
| Current placement or export specs | `channel-spec-registry.md`, `data/channel-specs.csv`, `scripts/check_channel_spec.py` |
| Social composition across Facebook, Instagram, LinkedIn, TikTok | `channel-composition-systems.md` first, then `channel-spec-registry.md` for vendor limits |
| Reference images of a product or person | `reference-first-image-flow.md`, `reference-analysis.md`, `prompt-contracts.md` |
| Studio and product photography | `realistic-studio-imagery.md`, `product-imagery.md` |
| Composition, light, shadow, colour, resolution, sharpening | `visual-craft.md`, `composition-light-color.md`, `image-output-and-sharpening.md` |
| Human, beauty, makeup, pose, figure | `human-imagery.md`, `makeup-art-direction.md`, `figure-and-pose.md` |
| Discount, price, offer shape, what a customer may cost | `pricing-and-offers.md`, `scripts/price_offer.py` |
| A commission deal from either side | `affiliate-commerce.md`, `data/affiliate-mechanics.csv`, `data/vn-advertising-law.csv`, `scripts/model_affiliate.py` |
| Recurring virtual brand person | `virtual-person-system.md`, `rights-and-claims.md` |
| Image edit or composite | `image-editing.md`, `prompt-contracts.md` |
| Provider execution, and what a provider actually honours | `api-image-orchestration.md`, `provider-compilers.md`, `prompt-grammar.md`, `data/prompt-grammar.csv` |
| Any designed artefact, before any craft table is opened | `design-direction.md`: content locked first, then one committed visual direction, art-directed inside. Tables measure the result; they never generate it |
| Food, restaurant, dish, menu, or Canva-ready graphic | `menu.md`, plus `product-imagery.md` and `canva-native-ai-design.md`; expand "Canva-like" into component inventory, mask family, contrast roles, layer ownership, text-safe geometry before prompting |
| Website, landing, wireframe, or type-led layout | `design-direction.md` (its layout/typography dossier), then `creative-evaluation.md`; set the real headline before styling |
| Poster, banner, standee, billboard — anything read from a distance | `poster.md`, `data/poster-formats.csv`, `scripts/plan_poster.py` |
| Visual QA and export | `anti-ai-quality.md`, `creative-evaluation.md`, `production-pipeline.md` |
| Published claims, and whether Vietnamese law allows them | `claims-proof-ledger.md`, `data/claim-evidence.csv`, `scripts/check_claims.py`, then `rights-and-claims.md` |
| Welcome, cart, renewal, win-back flow, capture popup, consent | `lifecycle-retention.md`, `data/lifecycle-duties.csv`, `scripts/plan_lifecycle.py` |
| What happens after somebody messages | `lead-handling.md`, `data/lead-states.csv`, `scripts/plan_lead_flow.py` |
| Any prose deliverable a person will read | `output-contract.md` plus `scripts/check_output_shape.py`: first sentence answers, headers assert, evidence rides the claim; announced openings, bold-led bullet grids, recap closes are blocking gates |
| Copy that reads machine-written or translated word for word | `specificity.md` first, then `rewrite-human.md`, `copywriting.md` |
| A page written to be found | `seo-writing.md`, `data/seo-intents.csv`, `scripts/audit_seo_page.py` |
| Targets, weights, achievement rates, scorecards | `kpi-scorecards.md`, then `report-notation.md` for the period table |
| Whether a number can be measured at all | `measurement-plan.md`, `data/tracking-events.csv`, `data/attribution-windows.csv`, `scripts/check_tracking_plan.py` |
| Naming a colour, pairing two, colour-psychology claims | `colour-combination.md`, `data/colour-gates.csv` |
| A brand colour on the same surface as a photograph | `scripts/sample_reference.py --image REF --check accent=HEX` first — the accent is measured from the scene, not named after it |
| One person holding every marketing role | `vietnam-operating-reality.md`, `scripts/plan_operating_load.py` |
| How many frames one photograph can produce | `product-composition-set.md`, `scripts/plan_composition_set.py` |
| Any Vietnamese copy: who it addresses | `address-register.md`, `data/address-registers.csv`, `scripts/check_address_register.py` |
| Where a number came from; how real companies market | `market-data-collection.md`, `how-companies-market.md` |
| Market size, and whether research has answered the decision | `market-assessment.md`, `scripts/size_market.py`, then `research-protocol.md` |

## Instruments, not authority

`data/` holds 38 tables queryable through `scripts/find_recipe.py`. Query them instead of
writing craft values from memory: a remembered lighting setup is a guess, a table row is a
decision somebody made and wrote down why. Every evidence table carries a
`what_it_does_not_establish` (or equivalent) column — never quote a benchmark, law row, or
attribution window without it. Each table names the reference that explains its method; each
gate script names its reference in `--help`. The eight a run reaches for directly:

| Table | Rows | What it settles |
|---|---|---|
| `image-recipes.csv` | 39 | The whole craft of one image: subject, scene, lighting, camera, ratio, copy-safe area, how that recipe fails |
| `palettes.csv` | 20 | Background, ink, accent, support, measured contrast, whether the accent may carry text |
| `layout-dials.csv` | 17 | The numbers that make a layout, each with range, defaults, and where it breaks |
| `slop-tells.csv` | 33 | AI-slop tells across prompt, image, copy, layout, campaign, scoped per recipe |
| `copy-formulas.csv` | 22 | Copy structures with worked VI/EN examples and when each fails |
| `translation-tells.csv` | 42 | Calques, machine cadence, evidence adjectives, hedges, register tells, each with regex and repair |
| `kpi-metrics.csv` | 27 | Each measurable: unit, direction, calculation, and the specific way it gets gamed |
| `kpi-aspect-weights.csv` | 16 | What share of a scorecard each aspect carries per office level, and why |

Search by the job, in Vietnamese or English — `--query "giao đồ ăn"`, not a style name. Then
`--brief RECIPE_ID [--palette PALETTE_ID]` composes a brief for `scripts/compile_prompt.py`
with every owner-only field left as explicit `TBD`; fill those from the truth map and never
guess `product_truth`. `--checklist RECIPE_ID` prints what to look at on the render, filtered
to the tells that can occur in that frame — look at the render against it; rereading the prompt
proves nothing. `scripts/render_refsheet.py --sheet lighting|frames|palettes|dials|reference|ratios`
draws the reference sheets as real SVG from the same tables; show a sheet instead of describing it.

The measuring scripts, and the one question each settles:

| Script | Settles | Method in |
|---|---|---|
| `check_specificity.py` | Does the draft say anything a competitor could not copy | `specificity.md` |
| `check_output_shape.py` | Is the document shaped like an answer or a model's essay | `output-contract.md` |
| `rewrite_human.py` | Does it read machine-made: cadence, landing beats, presence markers | `rewrite-human.md` |
| `check_address_register.py` | Who the Vietnamese copy addresses, and whether it holds | `address-register.md` |
| `check_locked_copy.py` | Supplied strings render character-for-character | hard rules below |
| `check_claims.py` | May this claim legally be made in Vietnam | `claims-proof-ledger.md` |
| `plan_lifecycle.py` | The duties Vietnamese law attaches to a flow | `lifecycle-retention.md` |
| `plan_lead_flow.py` | Whether enquiry handling can be handed to somebody else | `lead-handling.md` |
| `check_prompt_grammar.py` | What the provider actually documents about the prompt | `prompt-grammar.md` |
| `check_test_readout.py` | Whether a test is readable before anybody acts on it | `learning-loop.md` |
| `score_kpi.py`, `build_variance_report.py` | Achievement arithmetic; the period table a reader trusts | `kpi-scorecards.md`, `report-notation.md` |
| `price_offer.py` | Contribution after every per-unit cost; what a discount really removes; break-even ROAS | `pricing-and-offers.md` |
| `model_affiliate.py` | What a commission deal pays after fees, withholding, returns | `affiliate-commerce.md` |
| `size_market.py` | The arithmetic under "the market is worth", and when research may stop | `market-assessment.md` |
| `read_makeup.py` | Which makeup look a reference photo shows, by asking not labelling | `makeup-art-direction.md` |
| `check_evidence_saturation.py` | Whether a customer-research theme is real or one loud voice | `customer-evidence.md` |

Several references carry a merged deep dossier at the end of the file — long-form research
behind the working sections, with per-claim markers explained in `research-protocol.md`. Open
the section a decision needs, not the file. If `BRAND.md` exists, read it before public-facing
work; otherwise use `assets/templates/brand-context.md` only when continuity matters, and mark
inferred fields.

## Intake

Capture or safely infer: objective, primary customer action, funnel state, timing, success
metric; audience situation, job-to-be-done, awareness state, objections, market, language;
product truth, mechanism, offer, proof, price, availability, prohibited claims; brand voice,
visual grammar, references and anti-references, exact locks; channels, placements, formats,
quantities, provider, owners, approval constraints. For public claims: claim ID, evidence,
owner, market, disclosure, status. For images: reference roles, identity and product intent,
ratio, variant count, edit versus generation, whether rendering is actually available. And
where enquiries arrive and what happens to them — ask in plain words (which apps, who answers,
inside what hours, how many follow-ups before stopping), then route to
`scripts/plan_lead_flow.py --template`. Use `assets/templates/project-brief.json` when the
project spans pipelines.

## Write the run to disk

Run `scripts/start_workbench.py` before drafting anything broader than a `direct` request; a
`direct` request writes its one artifact, runs its gates, and stops. Replace every `WRITE` stub
with substantive work, keep the generated acceptance gates, and run `scripts/run_status.py
--strict` before calling a run complete — it fails on empty deliverables and on
filled-but-indefensible ones. `_meta/render-capability.json` starts at `not-rendered`; update it
only after real files were produced, opened, and QA-reviewed. Never relabel prompts,
storyboards, or wireframes as rendered photography or video.

The scaffold has already read the request: `scripts/_signals.py` extracts horizon, budget
pressure, product family, and market, and `01-intake` opens with the request quoted verbatim
above a table labelling every inference. Read that table before writing a word. Do not ask for
a horizon the request stated, do not plan 90 days against a stated six weeks, and correct a
wrong inference in `01-intake` first because everything downstream builds on it. A row marked
`unknown` — unit price and contribution margin above all — gets an answer from the user or a
written assumption beside it, never a plausible number.

`plan-from-zero` always includes market evidence, audience insight, positioning and offer,
message architecture, a channel-ready copy pack, execution priorities, budget and measurement
assumptions, and a source appendix — never make a non-marketer discover the modules separately.
Any type-led layout carries a mandatory copywriting stage unless final copy is already locked;
content the user supplied is locked by default, so the ladder applies only to copy the run must
invent. Resolve `product truth -> audience tension -> promise -> mechanism -> proof -> objection
-> CTA` before styling, then pass specificity, shape, human-rewrite, and register gates before
visual polish. A design is not ready to render while its headline could be swapped onto a
competitor's page unchanged.

One craft, two moments: first lock what is said, then commit to how it looks — same owner, no
handoff. Once content is locked, form is free: one committed direction from
`design-direction.md`, no house template, no default grid, no fixed section count. The craft
tables and gates measure the finished design; using them to generate it is what makes every
artifact look the same. If filesystem writes are unavailable, reproduce the deliverable
structure in the response and say plainly that no files were created.

## Execution loop

The ten steps are the full ceremony, owed only to `focused` and broader. A `direct` run
compresses to four moves: lock the supplied content, commit to one direction in your head, make
exactly the named artifact, run the gates that touch it. No workbench, no research stage, no
copywriting ladder for copy that was handed over, no step narrated to the user.

1. **Truth and route.** Build the truth map, pick one pipeline, apply only necessary overlays. Unknown information cannot become public copy, prices, reviews, statistics, quotes, or scarcity.
2. **Decision.** Write the audience tension, the belief or action wanted, mechanism, proof, offer, objection, next step: `tension -> promise -> mechanism -> proof -> action`.
3. **Research.** Mandatory for plans, market assessments, competitor or customer claims, pricing, regulation, and feasibility whenever live tools exist. Follow `research-protocol.md`; without live tools, produce the research plan and label every conclusion unverified. Do the research in the main run — never delegate it to subagents.
4. **Artifact pack.** Follow the pipeline's deliverable contract and `assets/registries/asset-formats.json`; select the minimum useful set, never a Cartesian product of formats. Include a format only when its audience state, owner, channel, CTA, acceptance gate, and metric are defined.
5. **Creative and images.** Resolve the visual direction first (`design-direction.md`, one committed direction, one line of justification), then open craft tables — a recipe applied before the direction is a template; a direction applied after the layout is decoration. Start at `scripts/find_recipe.py`; map every reference by role (identity, product, pose, composition, lighting, styling, makeup, color-grade, texture) and separate locks, freedoms, rejects. Branch variants from identical inputs, changing one named axis. For edits ("sửa ảnh"): inspect the source, build the lock map, invoke a real edit capability, compare against the locks — or return an executable edit prompt with exact mask instructions. For Canva-ready work default to AI flat composition -> human/Canva typography: AI owns surface, masks, palette roles, text-safe geometry; human owns brand name, Vietnamese copy, prices, claims, contact, logo, QR. HTML/SVG only on an explicit coded or editable-source request.
6. **Content first: count the facts.** `scripts/check_specificity.py --check <file>` before any style work. Under three checkable facts, stop — the draft has a content problem, and every rhythm edit from here makes it read better while saying nothing. The repair for an empty adjective is to put the fact back, not delete the adjective. Follow `specificity.md`.
7. **Shape, cadence, decoration, register.** In that order, because restructuring rewrites sentences and rhythm work deletes specifics: `check_output_shape.py`, then `rewrite_human.py --check --channel <where it goes>`, then on Vietnamese copy `check_address_register.py`. The whole layer, its order, and its sources are indexed in `anti-slop-index.md`. Do not lower a target to pass; do not add texture to flat prose — variation comes from the content deciding where it needs a beat.
8. **Channel.** Recompose message, proof, image behavior, and reading sequence per placement (`channel-composition-systems.md`); a Story is laid out again, not cropped. Verify the live spec before export; preserve masters, safe zones, captions, disclosures, naming, approval state.
9. **QA and decide.** Reject critical failures in product or identity fidelity, anatomy, physics, claims, disclosure, consent, rights, channel compliance, or message continuity. The verdict is a judgment against the brief, not a gate tally. Never call a causal winner from CTR alone or mixed conditions (`scripts/check_test_readout.py`).
10. **Learn.** Record asset, audience, placement, proof, offer, CTA, spend, result, rejection reason, next action. Feed objections, returns, and sales feedback into the next brief.

## Delivery modes

- `direct`: the request names one artifact and its content — "làm poster cho X", "sửa headline này", "viết 3 caption". Produce exactly that artifact, run only the gates that touch it, answer with the file plus at most three lines. No strategy recap, no variants nobody asked for. Twelve given dishes make a menu of twelve rows — no invented tagline, no about section, no description lines under items handed over as name and price. Default whenever the ask fits in one sentence; escalate only when a truth, rights, or claims question blocks the artifact itself, and say which question forced it.
- `focused`: one pipeline, assumptions, recommended direction, requested artifacts, QA, next step. Default for anything broader than one artifact.
- `system`: connected strategy plus the minimum cross-channel asset and measurement system.
- `production`: machine-readable brief, manifests, provider prompts, specs, owners, approvals, export handoff.

## Hard rules

- Do not invent claims, specifications, ingredients, labels, prices, reviews, customers, journalists, quotes, awards, certifications, competitor facts, results, or legal proof.
- Do not name a model version, platform spec, or provider capability unverified against a live source. Mark it unverified instead.
- Do not imitate a named living artist, celebrity, campaign, photograph, character, or distinctive layout, and do not imply endorsement.
- Default generated people to fictional adults with plausible healthy anatomy. Preserve authorized real-person identity in edits: makeup is surface styling only; outfit edits change wardrobe only and lock face, hair, body, pose, camera, light, background. Reject face drift rather than accept a prettier approximation.
- Treat generated packaging without an exact usable reference as concept art.
- Do not publish, deploy, contact anyone, buy ads, or cause any irreversible external consequence without explicit authorization.
- Do not bury weak strategy under more channels, formats, copy, or images.
- The artifact surface belongs to the buyer. No process language renders onto it: no `prototype`, `concept`, `bản nháp`, no fact labels, no footnotes about what is unverified. An unknown fact becomes a bracketed placeholder — `[GIÁ]`, `[HOTLINE]` — or the element is dropped, and the caveat moves to the handoff notes. Copy whose subject is the design itself means the copy stage never ran. Every sentence on the surface tells the buyer what the product is, what it costs, or what to do next; a sentence doing none of those is cut.
- Deliver the artifact that was named, and nothing else. "Tạo A" answered with B, or with A plus sections nobody asked for, is a failed run even when the extras are good. Anything added beyond the ask costs one line naming why it was necessary; when that line is hard to write, do not add the thing.
- Content the user supplied is locked copy. Dish names, prices, headlines, addresses, phone numbers, and any wording given in the request render character-for-character, diacritics included — the layout adapts to the content, never the content to the layout. Rewriting, embellishing, translating, or adding descriptions to supplied items is a critical failure even when the additions read well; a real problem in the supplied copy gets one line in the reply, not a silent fix. Run `scripts/check_locked_copy.py --artifact FILE --locks supplied.txt` on every menu, poster, and layout built from given content.
- Vietnamese display text in HTML or SVG is set only in faces verified to carry a Vietnamese subset, with that subset loaded. Look at the render on stacked-mark words — Nhiều, kiểm soát, đặt trước — at headline size; one broken diacritic is a reject.
- Title fit is an acceptance gate on designed artefacts. Headings wrap naturally — never `<br>` or split spans to manufacture a silhouette. Repair in order: shorten the copy, widen the measure, reduce the type scale, change the composition. Desktop H1 at 56px or less, section titles 40px or less; 72px display type only for a deliberate poster brief.
- For restaurant menus, follow the text-ownership contract in `menu.md`. Default to text-free AI art direction plus human or Canva typography for identity, Vietnamese copy, prices, claims, QR. Deterministic HTML/SVG only on explicit request; native AI menu text only as an explicit `full-ai-text-exception` with every row, price, and diacritic locked and diffed. Never silently switch production methods.
