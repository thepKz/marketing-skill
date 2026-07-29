# Marketing-Minthep

**🇬🇧 English** · [🇻🇳 Tiếng Việt](README.vi.md)

An all-in-one marketing skill for Claude Code and GPT/Codex. It turns an unfinished brief — including *"I don't know anything about marketing"* — into a system you can actually produce and measure: positioning, offer, copy, campaign, product imagery, menu and layout design, video sequences, and a measurement contract.

One invocation, many workbenches. The skill loads only the knowledge the current job needs instead of pouring all of marketing into one enormous prompt.

```text
$marketing-minthep
```

## Contents

- [What it produces](#what-it-produces) · [How it decides](#how-it-decides) · [Quick start](#quick-start)
- [The five things people find confusing](#the-five-things-people-find-confusing) — copywriting, image editing, campaign building, colour, layout
- [Sample output](#sample-output) · [Reference library](#reference-library) · [Anti-AI-slop gate](#anti-ai-slop-gate)
- [Repository layout](#repository-layout) · [Tests](#tests) · [What it will not do](#what-it-will-not-do)

## What it produces

Six pipelines, each with a fixed deliverable contract:

| Pipeline | Deliverables | Typical output |
|---|---|---|
| `plan-from-zero` | 16 | Market evidence, audience, positioning, offer, message ladder, copy pack, calendar, budget and measurement |
| `deep-research` | 9 | Question decomposition, tiered sources, sizing arithmetic, triangulation, confidence, source map |
| `image-from-reference` | 10 | Reference role map, locks/freedoms/rejects, provider route, 4–5 controlled branches, QA |
| `design-render` | 9 | Design directions, chosen system, real rendered menu/wireframe/key visual, print and export handoff |
| `video-campaign` | 9 | Shot list with carried continuity, per-shot prompts, audio, edit plan, platform cutdowns |
| `optimize-iterate` | 7 | Asset lineage, experiment log, read-out, next-test recommendation |

Eleven workbenches sit across those pipelines: strategy and offer, campaign and launch, content and distribution, commerce and merchandising, paid media, PR, sales enablement, creator and UGC, lifecycle and retention, visual production, measurement.

Product families with their own playbook and proof requirements: beauty, fashion, food and beverage, electronics, home, jewelry and luxury, SaaS, local service, education, hospitality.

## How it decides

The scaffold reads your sentence before it plans anything. `scripts/_signals.py` pulls four facts out of the wording, in Vietnamese or English, accented or not:

| Signal | Read from | Effect |
|---|---|---|
| Campaign horizon | `"trong 6 tuần"`, `"in 8 weeks"`, `"90 ngày"` | Names and divides the calendar deliverable into phases that add up exactly |
| Budget pressure | `"ngân sách nhỏ"`, `"tight budget"` | Caps the asset count and drops channels that tier cannot reach, with a stated reason |
| Product family | `"bún bò"`, `"serum"`, `"homestay"` | Selects the playbook and the proof requirements |
| Market | `"Sài Gòn"`, `"Đà Lạt"` | Switches to Vietnam market context and single-location tactics |

Every one of these is labelled `inferred` and carries the phrase it was read from, because a horizon you stated is not the same kind of fact as one we defaulted to. `01-intake` opens with your request quoted verbatim above that label table. Correct a wrong inference there and everything downstream follows.

Facts are labelled throughout: `confirmed` (you said it), `observed` (found in a cited source), `inferred` (read from wording), `unknown`. A field marked `unknown` — unit price and contribution margin above all — gets an answer from you or a written assumption beside it. It never gets a plausible number.

Three widths: `focused` (smallest usable set, the default), `system` (strategy connected to channels and measurement), `production` (adds JSON manifests, provider prompts, owners, approval, naming, export handoff). Plans from zero and deep research start at `system`. Menu, image edit and video rise to `production` when the request says `render`, `export`, `xuất file`, `MP4`, or asks for print.

## Quick start

Install into both CLIs, globally:

```powershell
python marketing-minthep/scripts/install_global.py
```

That writes to `~/.claude/skills/marketing-minthep` and `~/.codex/skills/marketing-minthep`. The repo also carries project-level adapters at `.claude/skills/` and `.codex/skills/`; both load `marketing-minthep/SKILL.md` as the single source, so never edit marketing content inside an adapter.

Create a real workspace from one sentence:

```powershell
python marketing-minthep/scripts/start_workbench.py --request "Tôi không biết marketing, hãy làm kế hoạch từ đầu cho quán bún bò" --root .
```

A campaign brief derived entirely from the request — horizon, budget, industry and channels all read from it:

```powershell
python marketing-minthep/scripts/scaffold_campaign.py --request "Tôi bán bún bò ở Sài Gòn, muốn lên chiến dịch ra mắt trong 6 tuần cho khách văn phòng, ngân sách nhỏ"
```

Override when you know better than the inference:

```powershell
python marketing-minthep/scripts/scaffold_campaign.py --project "Launch" --job campaign-launch --industry beauty --provider gpt-image-2 --channels meta tiktok web
```

Check a run before calling it finished:

```powershell
python marketing-minthep/scripts/run_status.py --strict
```

`--strict` fails on empty deliverables *and* on filled-but-indefensible ones: unsourced figures, leftover placeholders, sections thin enough to be filler. A scaffold is not a report, and a full file is not automatically a defensible one.

Every run carries `_meta/render-capability.json`, starting at `not-rendered`. Prompts, storyboards, SVG wireframes and provider plans are never described as rendered photography or video.

## The five things people find confusing

Each one has a deep dossier and a command that produces a real artefact.

### Copywriting

The ladder is `tension → promise → mechanism → proof → action`, and it is a ladder because you cannot skip a rung: a promise without a mechanism is a slogan, a mechanism without proof is a claim. Read [`references/copywriting.md`](marketing-minthep/references/copywriting.md) for the channel-ready pack and [`references/dossiers/copywriting-deep.md`](marketing-minthep/references/dossiers/copywriting-deep.md) for sentence-level craft — specificity over adjective stacking, the objection you must name before the reader does, and why "chất lượng cao" is not a benefit.

### Image editing

Editing is not generation. The route is: inspect the source, build a **lock map**, invoke a real edit capability, then compare the result against the locks. On a real person, makeup edits change pigment and finish on the surface only; head shape, eye geometry and spacing, eyelids, nose, lips, jaw, chin, ears, hairline, skin tone, apparent age, asymmetry, expression and gaze are locked. Outfit edits change wardrobe only. If a real edit capability is unavailable, the skill returns an executable edit prompt with exact mask instructions and says plainly that nothing was rendered. See [`references/image-editing.md`](marketing-minthep/references/image-editing.md).

### Campaign building

```powershell
python marketing-minthep/scripts/scaffold_campaign.py --request "..."
```

The brief separates two things that used to both print as `TBD`: **UNKNOWN** means nobody has stated it and the plan is blocked until they do; **TBD** means it is ours to decide and is not decided yet. Assets interleave across channels and carry a funnel stage, rather than being the cartesian product of channels and formats — that is a multiplication, not a plan. See [`references/campaign-systems.md`](marketing-minthep/references/campaign-systems.md).

### Colour

Palettes are built, not picked. The dossier [`references/dossiers/colour-science-and-harmony.md`](marketing-minthep/references/dossiers/colour-science-and-harmony.md) covers perceptual lightness versus hex intuition, contrast ratios that survive a phone screen in sunlight, the difference between a brand colour and an accent that only appears once, and what happens to your palette in CMYK. `references/composition-light-color.md` connects it to camera, light and grade.

### Layout

```powershell
python marketing-minthep/scripts/plan_design_options.py --input marketing-minthep/assets/examples/bun-bo/menu-modern-street.json
python marketing-minthep/scripts/render_mockup.py --input marketing-minthep/assets/examples/bun-bo/menu-modern-street.json --output out.svg --html-output out.html
```

The renderer measures text and flows it. Nothing is positioned by a fraction of the canvas height — that approach produced diacritics cutting through a kicker line and a title painted under the hero image. Copy that does not fit raises an error instead of being silently truncated, because a mockup that quietly deletes two thirds of a sentence looks finished, which is what makes it dangerous. Dossiers: [`layout-wireframe-typography.md`](marketing-minthep/references/dossiers/layout-wireframe-typography.md), [`composition-and-layout-vision.md`](marketing-minthep/references/dossiers/composition-and-layout-vision.md), [`menu-design-and-engineering.md`](marketing-minthep/references/dossiers/menu-design-and-engineering.md).

## Sample output

Three menu directions for the same bún bò shop, rendered by `render_mockup.py` from the specs in `assets/examples/bun-bo/` — no API, no design tool:

| Modern street | Heritage craft | Quiet editorial |
|---|---|---|
| [SVG](docs/assets/generated/bun-bo-menu-modern-street.svg) | [SVG](docs/assets/generated/bun-bo-menu-heritage-craft.svg) | [SVG](docs/assets/generated/bun-bo-menu-quiet-editorial.svg) |

Image directions compiled by `compile_prompt.py` and rendered through a provider:

| Packshot | Key visual | Beauty campaign | Fashion look |
|---|---|---|---|
| <img src="docs/assets/generated/minthep-serum-packshot.png" width="180"> | <img src="docs/assets/generated/minthep-serum-key-visual.png" width="180"> | <img src="docs/assets/generated/minthep-beauty-campaign.png" width="180"> | <img src="docs/assets/generated/minthep-fashion-look.png" width="180"> |

Video shots come from `plan_video_sequence.py`, which carries continuity forward: each shot inherits the previous shot's subject state, wardrobe, light direction, lens and grade, so prompt 4 cannot contradict prompt 3.

```powershell
python marketing-minthep/scripts/plan_video_sequence.py --input marketing-minthep/assets/examples/bun-bo/video-sequence.json --format prompts
```

## Reference library

20 reference photographs in `docs/assets/references/` with attribution in `ATTRIBUTION.txt`, covering makeup macro, expression grids, candid action, full-body negative space, editorial poses and mixed lighting. They exist to be decomposed into transferable attributes — `identity`, `product`, `pose`, `composition`, `lighting`, `styling`, `makeup`, `color-grade`, `texture` — and never to be copied. Using them implies no endorsement and grants no reuse rights for a campaign.

The static handbook explains the whole flow with a VI/EN toggle:

```powershell
python -m http.server 8000 --directory docs
```

## Anti-AI-slop gate

[`references/anti-ai-quality.md`](marketing-minthep/references/anti-ai-quality.md) runs before delivery. The first-order check: could someone predict the palette, model, props, lighting and layout from the product *category* alone? Dark navy and purple glow for AI software, airbrushed face and water splash for beauty, blue gradient and handshake for corporate, black and gold and marble for luxury, beige room and one green leaf for wellness. If yes, the category cue is replaced by a product mechanism, an audience behaviour, or a physical material specific to this brief.

The second-order check catches the escape hatch: having rejected the obvious category look, did the work land in another fashionable default — generic editorial restraint, brutalist utility, maximalist acid graphics — for no reason from the brief? The visual lane has to be named and justified by the product, not by taste.

## Repository layout

```
marketing-minthep/
  SKILL.md                  entry point, under 150 lines
  references/               45 topic files, each under 150 lines
    dossiers/               14 deep-craft dossiers + index
  scripts/                  19 tools + test suite
  assets/
    registries/             pipelines.json, asset-formats.json
    templates/              project-brief.json and deliverable skeletons
    examples/               runnable inputs, including the bún bò case study
    evals/                  routing cases
docs/                       static handbook, VI/EN, deployed to GitHub Pages
.claude/skills/  .codex/skills/    thin adapters over the same SKILL.md
```

## Tests

```powershell
python -m unittest discover -s marketing-minthep/scripts -p "test_*.py"
python marketing-minthep/scripts/evaluate_workbench.py
python marketing-minthep/scripts/plan_marketing_system.py --input marketing-minthep/assets/examples/all-in-one-product-request.json
```

93 tests. `evaluate_workbench.py` replays the routing cases in `assets/evals/`. `.github/workflows/deploy-pages.yml` runs structure checks, the planner, the manifest builder, the unit tests and Python compilation, then deploys `docs/` to GitHub Pages.

## What it will not do

- Invent a claim, ingredient, spec, price, review, customer, statistic, certification, scarcity cue or endorsement.
- Copy a celebrity identity, a living artist's style, a specific campaign, photograph or signature layout. References are decomposed into attributes or not used.
- Slim or reshape a real person's body in an edit.
- Present an AI-generated package as a photograph of the real product without an exact reference.
- Publish, contact press or creators, buy ads, or change a live campaign. Those need separate authorization.
- Call a prompt an image, a storyboard a video, or a plan a result.

## Operating limits

Platform specs change; verify the official source live before export or upload. Image results depend on the provider, valid references and whatever rendering capability actually exists at the time. PR, legal, health, finance, comparative and regulated claims need evidence and owner approval. This skill plans and produces artefacts; publishing, media buying, outreach and deployment remain yours.
