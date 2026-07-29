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

Ten business jobs route inside those pipelines, defined in [`references/marketing-system-router.md`](marketing-minthep/references/marketing-system-router.md): `strategy-offer`, `campaign-launch`, `content-distribution`, `commerce-merchandising`, `pr-communications`, `sales-enablement`, `creator-ugc`, `lifecycle-retention`, `creative-production`, `measurement-optimization`.

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

Each one has a deep dossier, a lookup table under `data/`, and a command that produces something you can look at. Look it up rather than recalling it: a remembered craft value is a guess, a table row is a decision someone already wrote down with its reason.

### Copywriting

```powershell
python marketing-minthep/scripts/find_recipe.py --table copy --query "tiêu đề"
```

22 formulas in `data/copy-formulas.csv`, each with a worked Vietnamese and an English example. No example contains a printable number — every price, hour and percentage is a `[slot]`, because a sample that ships a plausible-looking figure is how an invented claim reaches a customer. The ladder is `tension → promise → mechanism → proof → action`, and it is a ladder because you cannot skip a rung: a promise without a mechanism is a slogan, a mechanism without proof is a claim. Read [`references/copywriting.md`](marketing-minthep/references/copywriting.md) for the channel-ready pack and [`references/dossiers/copywriting-deep.md`](marketing-minthep/references/dossiers/copywriting-deep.md) for sentence-level craft — specificity over adjective stacking, the objection you must name before the reader does, and why "chất lượng cao" is not a benefit.

### Image editing

```powershell
python marketing-minthep/scripts/find_recipe.py --query "giao đồ ăn"
python marketing-minthep/scripts/find_recipe.py --brief dish-delivery --palette paper-cobalt
python marketing-minthep/scripts/find_recipe.py --checklist dish-delivery
```

Search by the job, in Vietnamese or English — not by a style name. `data/image-recipes.csv` carries 39 jobs, including six the Vietnam market needs and nobody else has a row for: a delivery motorbike, a market stall, a Tết composition, a bánh mì cross-section, a bowl counter, grill smoke. `--brief` composes a `compile_prompt.py` payload and leaves what only the owner knows as `TBD` with the reason attached; it will not invent a `product_truth`. `--checklist` filters the 33 tells in `data/slop-tells.csv` down to the ones that apply to that recipe, sorted by severity — the drink checklist asks about condensation, the before-and-after checklist asks whether the "after" is merely better lit. Keep it open while you look at the render; re-reading the prompt proves nothing.

Two more sheets explain the parts of a brief a non-marketer has no vocabulary for. `--sheet lighting` draws the six setups from above as light positions with the shadow computed from where the key sits, so "45/45 soft key" stops being jargon. `--sheet frames` draws the five placements at their real proportions with the reserved bands shaded — the story frame is the one that shows why a story is laid out again rather than cropped from the feed post.

Editing is not generation. The route is: inspect the source, build a **lock map**, invoke a real edit capability, then compare the result against the locks. On a real person, makeup edits change pigment and finish on the surface only; head shape, eye geometry and spacing, eyelids, nose, lips, jaw, chin, ears, hairline, skin tone, apparent age, asymmetry, expression and gaze are locked. Outfit edits change wardrobe only. If a real edit capability is unavailable, the skill returns an executable edit prompt with exact mask instructions and says plainly that nothing was rendered. See [`references/image-editing.md`](marketing-minthep/references/image-editing.md).

### Campaign building

```powershell
python marketing-minthep/scripts/scaffold_campaign.py --request "..."
```

The brief separates two things that used to both print as `TBD`: **UNKNOWN** means nobody has stated it and the plan is blocked until they do; **TBD** means it is ours to decide and is not decided yet. Assets interleave across channels and carry a funnel stage, rather than being the cartesian product of channels and formats — that is a multiplication, not a plan. See [`references/campaign-systems.md`](marketing-minthep/references/campaign-systems.md).

### Colour

```powershell
python marketing-minthep/scripts/render_refsheet.py --sheet palettes --output palettes.svg --html-output palettes.html
```

That draws all 20 palettes in `data/palettes.csv` as real areas with a real button on each, and prints the measured contrast ratios underneath. The last five columns of the table are computed, not claimed: two of the twenty accents genuinely fail 3:1 against their background and are marked `fill only — too close to the background for text or hairlines`, which is more useful than a palette set where everything passes. Palettes are built, not picked. The dossier [`references/dossiers/colour-science-and-harmony.md`](marketing-minthep/references/dossiers/colour-science-and-harmony.md) covers perceptual lightness versus hex intuition, contrast ratios that survive a phone screen in sunlight, the difference between a brand colour and an accent that only appears once, and what happens to your palette in CMYK. `references/composition-light-color.md` connects it to camera, light and grade.

### Layout

```powershell
python marketing-minthep/scripts/plan_design_options.py --input marketing-minthep/assets/examples/bun-bo/menu-modern-street.json
python marketing-minthep/scripts/render_mockup.py --input marketing-minthep/assets/examples/bun-bo/menu-modern-street.json --output out.svg --html-output out.html
python marketing-minthep/scripts/render_social_post.py --input marketing-minthep/assets/examples/bun-bo/post-story.json --output story.svg
python marketing-minthep/scripts/render_refsheet.py --sheet dials --dial margin_ratio --output dials.svg --html-output dials.html
```

The mechanism is a small set of numbers, and the only honest way to explain a number is to show the same thing twice with it changed. `data/layout-dials.csv` names 17 of them — margin ratio, title ratio, row pitch, line leading — each with a minimum, a maximum, three named defaults, what raising it changes and where it breaks. `--sheet dials` draws the same four-item bún bò menu three times at min, default and max, with only the dial under test moving. Show that to someone instead of describing it.

The renderer measures text and flows it. Nothing is positioned by a fraction of the canvas height — that approach produced diacritics cutting through a kicker line and a title painted under the hero image. Copy that does not fit raises an error instead of being silently truncated, because a mockup that quietly deletes two thirds of a sentence looks finished, which is what makes it dangerous. The post renderer adds the one constraint a menu does not have: the platform draws its own buttons over the canvas, so each placement declares the bands it may not use and a block that would collide with the CTA raises with the overflow in pixels. Dossiers: [`layout-wireframe-typography.md`](marketing-minthep/references/dossiers/layout-wireframe-typography.md), [`composition-and-layout-vision.md`](marketing-minthep/references/dossiers/composition-and-layout-vision.md), [`menu-design-and-engineering.md`](marketing-minthep/references/dossiers/menu-design-and-engineering.md).

## Sample output

Three menu directions for the same bún bò shop, rendered by `render_mockup.py` from the specs in `assets/examples/bun-bo/` — no API, no design tool:

| Modern street | Heritage craft | Quiet editorial |
|---|---|---|
| [SVG](docs/assets/generated/bun-bo-menu-modern-street.svg) | [SVG](docs/assets/generated/bun-bo-menu-heritage-craft.svg) | [SVG](docs/assets/generated/bun-bo-menu-quiet-editorial.svg) |

Two sample posts for the same shop, rendered by `render_social_post.py`. The story is not the feed post cropped: it is laid out again at 1080x1920 with the top 250px and the bottom 420px left to the app's own interface, so the CTA cannot end up behind the reply field.

| Feed 4:5 | Story 9:16 |
|---|---|
| [SVG](docs/assets/generated/bun-bo-post-feed.svg) | [SVG](docs/assets/generated/bun-bo-post-story.svg) |

```powershell
python marketing-minthep/scripts/render_social_post.py --input marketing-minthep/assets/examples/bun-bo/post-feed.json --output post.svg --html-output post.html --caption-output post-caption.md
```

`--caption-output` writes the other half of a post — caption, hashtags, alt text, disclosure. Every line nobody supplied comes out as `UNKNOWN` with the reason, because an invented caption fails the same way an invented price does: it looks finished, so someone posts it.

Image directions compiled by `compile_prompt.py` and rendered through a provider:

| Packshot | Key visual | Beauty campaign | Fashion look |
|---|---|---|---|
| <img src="docs/assets/generated/minthep-serum-packshot.png" width="180"> | <img src="docs/assets/generated/minthep-serum-key-visual.png" width="180"> | <img src="docs/assets/generated/minthep-beauty-campaign.png" width="180"> | <img src="docs/assets/generated/minthep-fashion-look.png" width="180"> |

Video shots come from `plan_video_sequence.py`, which carries continuity forward: each shot inherits the previous shot's subject state, wardrobe, light direction, lens and grade, so prompt 4 cannot contradict prompt 3.

```powershell
python marketing-minthep/scripts/plan_video_sequence.py --input marketing-minthep/assets/examples/bun-bo/video-sequence.json --format prompts
```

## Reference library

A reference exists to be decomposed into transferable attributes — `identity`, `product`, `pose`, `composition`, `lighting`, `styling`, `makeup`, `color-grade`, `texture` — and never to be copied.

```powershell
python marketing-minthep/scripts/find_recipe.py --table axes
python marketing-minthep/scripts/render_refsheet.py --sheet reference --output reference.svg
```

Half of any picture you hand over belongs to somebody: the words, the face, the pose, the logo. The other half belongs to nobody — the geometry of the frame, the direction of the key light, the path your eye takes, the crop ratio. `data/reference-axes.csv` splits it on 11 axes and rules on each one: four `keep`, five `transform`, one `reject`, one `avoid`. `--sheet reference` draws the same picture twice — once with the borrowed parts boxed, once reduced to grid, key direction and reading path — so someone with no marketing vocabulary can see which half is which instead of taking it on trust. The rule is to change at least three axes before using a reference; the sheet changes five. If the result is still traceable to one source at a glance, start again.

Three photographs remain in `docs/assets/references/`, CC0 and CC BY, each with creator and source in `ATTRIBUTION.txt`. Seventeen were deleted on 2026-07-29: they were photographs of named living people whose stated licence was "copyright remains with the original creators", which is a disclaimer and not a permission. `test_tools.py` fails the whole suite if a fourth file arrives here without a licence line.

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
  data/                     6 lookup tables: image recipes, palettes, layout
                            dials, slop tells, copy formulas, reference axes
  scripts/                  22 tools + test suite
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

121 tests, including ones that recompute every contrast ratio in `data/palettes.csv` and fail if a copy example contains a printable number. `evaluate_workbench.py` replays the routing cases in `assets/evals/`. `.github/workflows/deploy-pages.yml` runs structure checks, the planner, the manifest builder, the unit tests and Python compilation, then deploys `docs/` to GitHub Pages.

## What it will not do

- Invent a claim, ingredient, spec, price, review, customer, statistic, certification, scarcity cue or endorsement.
- Copy a celebrity identity, a living artist's style, a specific campaign, photograph or signature layout. References are decomposed into attributes or not used.
- Slim or reshape a real person's body in an edit.
- Present an AI-generated package as a photograph of the real product without an exact reference.
- Publish, contact press or creators, buy ads, or change a live campaign. Those need separate authorization.
- Call a prompt an image, a storyboard a video, or a plan a result.

## Operating limits

Platform specs change; verify the official source live before export or upload. Image results depend on the provider, valid references and whatever rendering capability actually exists at the time. PR, legal, health, finance, comparative and regulated claims need evidence and owner approval. This skill plans and produces artefacts; publishing, media buying, outreach and deployment remain yours.
