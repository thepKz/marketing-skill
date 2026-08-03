# Marketing-Minthep

<p align="right">
  <a href="README.md"><kbd> &nbsp; <b>English</b> &nbsp; </kbd></a>
  <a href="README.vi.md"><kbd> &nbsp; Tiếng Việt &nbsp; </kbd></a>
</p>

An all-in-one marketing skill for Claude Code and GPT/Codex. It turns an unfinished brief — including *"I don't know anything about marketing"* — into a system you can actually produce and measure: positioning, offer, copy, campaign, product imagery, menu and layout design, video sequences, and a measurement contract.

One invocation, many workbenches. The skill loads only the knowledge the current job needs instead of pouring all of marketing into one enormous prompt.

```text
$marketing-minthep
```

<table>
  <tr>
    <td width="25%"><a href="docs/assets/generated/minthep-serum-packshot.png"><img src="docs/assets/generated/minthep-serum-packshot.png" alt="Serum packshot, concept packaging" /></a></td>
    <td width="25%"><a href="docs/assets/generated/minthep-serum-key-visual.png"><img src="docs/assets/generated/minthep-serum-key-visual.png" alt="Serum key visual" /></a></td>
    <td width="25%"><a href="docs/assets/generated/bun-bo-menu-quiet-editorial.svg"><img src="docs/assets/generated/bun-bo-menu-quiet-editorial.svg" alt="Menu, quiet editorial direction, drawn by code" /></a></td>
    <td width="25%"><a href="docs/assets/generated/refsheet-palettes.svg"><img src="docs/assets/generated/refsheet-palettes.svg" alt="Palette sheet with measured contrast ratios" /></a></td>
  </tr>
</table>

The two photographs came out of the controlled-branch image pipeline. The menu and the palette sheet did not: `render_mockup.py` and `render_refsheets.py` drew them, and every contrast ratio printed on that sheet is a measurement. Not a style. The rest is on the [live demo page](https://thepkz.github.io/marketing-skill/), including the failures the sheets admit to.

## Does it work? Here is the measurement

The same Vietnamese About-us paragraph, before and after. Both files are in the repository, and a test fails if the bad one ever starts passing or the good one ever stops: [`assets/examples/rewrite-human/`](marketing-minthep/assets/examples/rewrite-human/).

| Measured | Draft | Rewrite | Gate |
|---|--:|--:|---|
| Checkable facts | 1 | 8 | ≥ 3 |
| Sentences a competitor could publish unchanged | 3 of 4 | 2 of 8 | ≤ 50% |
| Sentence-length variation (CV) | 0.10 | 0.85 | ≥ 0.45 |
| Longest ÷ shortest sentence | 1.3× | 19.0× | ≥ 3.0 |
| Empty-evidence adjectives per 150 syllables | 1.55 | 0.0 | ≤ 1.0 |
| Named Vietnamese machine-translation tells | 4 | 0 | none blocking |
| **Verdict** | **failed, 6 blocking** | **passed** | |

The rewrite carries eight checkable facts in 101 syllables. The draft carried one in 97. The facts came from the shop, not from the model — which is the entire difference, and the reason the gate is arithmetic instead of taste. Every number above is printed by a script you can run on your own draft, and the shape that produces them is in [ARCHITECTURE.md](ARCHITECTURE.md).

## Contents

- [Does it work? Here is the measurement](#does-it-work-here-is-the-measurement) · [Architecture](ARCHITECTURE.md)
- [What it produces](#what-it-produces) · [What happens when you invoke it](#what-happens-when-you-invoke-it) · [How it decides](#how-it-decides) · [Quick start](#quick-start)
- [The five things people find confusing](#the-five-things-people-find-confusing) — copywriting, image editing, campaign building, colour, layout
- [The questions behind the other tools](#the-questions-behind-the-other-tools) — pricing, affiliate deals and disclosure law, what a claim is allowed to say, prompt grammar, KPIs, reporting a period, a repeatable person, testing, workload
- [Sample output](#sample-output) · [Reference library](#reference-library) · [Anti-AI-slop gate](#anti-ai-slop-gate)
- [Repository layout](#repository-layout) · [Tests](#tests) · [What it will not do](#what-it-will-not-do)

## What it produces

Nine pipelines, each with a fixed deliverable contract:

| Pipeline | Deliverables | Typical output |
|---|---|---|
| `plan-from-zero` | 16 | Market evidence, audience, positioning, offer, message ladder, copy pack, calendar, budget and measurement |
| `deep-research` | 9 | Question decomposition, tiered sources, sizing arithmetic, triangulation, confidence, source map |
| `image-from-reference` | 10 | Reference role map, locks/freedoms/rejects, provider route, 4–5 controlled branches, QA |
| `design-render` | 9 | Design directions, chosen system, real rendered menu/wireframe/key visual, print and export handoff |
| `video-campaign` | 9 | Shot list with carried continuity, per-shot prompts, audio, edit plan, platform cutdowns |
| `optimize-iterate` | 7 | Asset lineage, experiment log, read-out, next-test recommendation |
| `rewrite-human` | 4 | A measured diagnosis of a draft, the rewrite, and what changed and why |
| `score-kpi` | 4 | Metric definitions, weights, achievement rates, and the branch each rate was scored on |
| `virtual-model` | 6 | A person specified in numbers, a seed that reproduces her, wardrobe looks, compiled prompts |

The last three are short on purpose. A rewrite is not a campaign, and asking someone to open a sixteen-deliverable plan to fix one paragraph is how a tool stops being used.

Ten business jobs route inside those pipelines, defined in [`references/marketing-system-router.md`](marketing-minthep/references/marketing-system-router.md): `strategy-offer`, `campaign-launch`, `content-distribution`, `commerce-merchandising`, `pr-communications`, `sales-enablement`, `creator-ugc`, `lifecycle-retention`, `creative-production`, `measurement-optimization`.

Product families with their own playbook and proof requirements: beauty, fashion, food and beverage, electronics, home, jewelry and luxury, SaaS, local service, education, hospitality.

## What happens when you invoke it

Not a chat. A folder. Here is a real run, from a sentence a shop owner would actually type:

```powershell
python marketing-minthep/scripts/start_workbench.py --request "Tôi mở shop mỹ phẩm nhỏ ở Gò Vấp, không biết gì về marketing, muốn có kế hoạch và ảnh sản phẩm đẹp, ngân sách nhỏ" --root .
```

It scores all nine pipelines against the wording and shows its work — `plan-from-zero` at 3, `deep-research` next at 1 — then writes 34 files. Thirteen deliverables in Vietnamese and English side by side, an intake that quotes your sentence verbatim, `claims.csv` and `sources.md` for anything that will need a citation, a decision log, and a `README.md` index whose second paragraph is the part worth reading:

> Read from the request: horizon **13 weeks** (assumed, not stated); budget **small** (from "ngân sách nhỏ"); product family **beauty** (from "mỹ phẩm"). Correct any of these in `01-intake` first — everything downstream is built on them.

Three inferences, each labelled with the phrase behind it, and the one with nothing behind it labelled as assumed. The calendar file is already named `10-calendar-13w` because the horizon it inherited is a real number rather than a placeholder.

Inside a deliverable, a section either asks you for something only you know, or names the command that settles it:

```markdown
## CAC ceiling

> WRITE: Derive from contribution margin, repeat rate, and acceptable payback period. Show the calculation.

> RUN: python scripts/price_offer.py --price PRICE --variable-cost COST --repeat-purchases N
> --acquisition-cost CAC — two ceilings, and the report names which one binds. Do not hand-calculate this.
```

That second marker exists because of this exact test run. The first version of it asked the shop owner to derive a CAC ceiling by hand while the script that derives it sat unused in the same repository. Twenty-four sections now carry the command that answers them, and the line stays in the finished file as the citation for the number above it.

Nothing in the folder claims to be finished. Every file opens at `status=empty`, every unfilled section is a `> WRITE:` marker, and `run_status.py --strict` counts both those and the filled-but-indefensible ones.

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

```powershell
python marketing-minthep/scripts/find_recipe.py --table ratios --query "reels"
python marketing-minthep/scripts/find_recipe.py --table grids --query "tỉ lệ vàng"
python marketing-minthep/scripts/render_refsheet.py --sheet ratios --output ratios.svg --html-output ratios.html
```

"Should I use the golden ratio?" is the most common layout question and the answer is almost always no — but "no" is not usable, so these two tables answer it with arithmetic instead of taste. `data/frame-ratios.csv` carries 13 ratios keyed by where the asset is going, because the question arrives as *"cho Reels"* or *"in ra giấy A4"* and never as *"9:16"*. `data/composition-grids.csv` grades the seven grids people argue about, and the grades are not flattering: the golden spiral is `myth` — it can be scaled, rotated and mirrored into eight orientations, so something in any photograph lands on some arm of it, and a test that cannot fail is not a test. The phi grid is `myth-adjacent`: the arithmetic is right, and the difference it is asserting is 38.2% against a thirds 33.3%, which is 4.9 percentage points, which is 53 px on a 1080 px width. Rule of thirds is `peer-reviewed-contested` — Amirshahi 2014 found thirds scores barely correlate with aesthetic ratings across 2,415 images, and Hoh & Zhang 2023 found people prefer centred subjects in forced choice.

Only `w` and `h` are stored. Every position is computed by one function, so the table cannot disagree with itself and the sheet cannot disagree with the table. The useful output is the *gap*: on a square the dynamic-symmetry eye is the centre and sits 180 px from the thirds line, on 16:9 it is at 24% and 179 px away, on scope it is at 14.9% and 377 px away, and on 3:2 it is 42 px away — under 5% of the frame, so nobody can point at it and the choice is empty. `--sheet ratios` draws all twelve delivery ratios at true proportion with all three grids on each, which is how the one genuinely surprising result becomes visible: on ISO A4 paper the grey thirds line vanishes underneath the blue eye line, because h² = 2w² puts the eye on exactly ⅓. Root-2 is the one ratio where the two grids are the same grid.

The measurement stops at measuring. It reports the gap and never says which grid to use, because 5:4 has a 5.7% gap and still wants centre — it is nearly square. The advice lives in the row.

The renderer measures text and flows it. Nothing is positioned by a fraction of the canvas height — that approach produced diacritics cutting through a kicker line and a title painted under the hero image. Copy that does not fit raises an error instead of being silently truncated, because a mockup that quietly deletes two thirds of a sentence looks finished, which is what makes it dangerous. The post renderer adds the one constraint a menu does not have: the platform draws its own buttons over the canvas, so each placement declares the bands it may not use and a block that would collide with the CTA raises with the overflow in pixels. Dossiers: [`layout-wireframe-typography.md`](marketing-minthep/references/dossiers/layout-wireframe-typography.md), [`composition-and-layout-vision.md`](marketing-minthep/references/dossiers/composition-and-layout-vision.md), [`menu-design-and-engineering.md`](marketing-minthep/references/dossiers/menu-design-and-engineering.md).

## The questions behind the other tools

The five above are the ones people ask out loud. These are the ones that decide whether a plan survives contact with arithmetic. Each is a command, and each returns a verdict — `passed`, `failed`, `skipped` or `review` — rather than an opinion.

### "Can I afford this discount?"

```powershell
python marketing-minthep/scripts/price_offer.py --price 280000 --variable-cost 112000 --discount 0.20
```

> 20% off the price removes 33% of the contribution, not 20%. Holding the same gross profit takes 1.50x the units.

That is the whole reason this unit exists. A 20% discount does not cost 20%; it costs a share of your contribution, and the share depends on your margin. The same command derives the break-even ROAS as the reciprocal of the contribution ratio — 1.67 here — so a handed-down ROAS target can be checked before it is accepted, and two CAC ceilings when repeat purchases are supplied, naming which one binds. A guarantee is a cost too: put the expected return rate in and read the contribution again. [`references/pricing-and-offers.md`](marketing-minthep/references/pricing-and-offers.md).

### "What does a 10% commission deal actually pay?"

```powershell
python marketing-minthep/scripts/model_affiliate.py --check deal.csv --side creator
python marketing-minthep/scripts/model_affiliate.py --notch
```

> A 10% rate arrives as 5.58% of the value it was attributed.

The rate is charged on ordered value and paid on settled value, and four subtractions sit in between: returns, the 0.98% platform service fee, 10% personal income tax withheld at source, and what the posts cost to make. Both sides are modelled, because they are two different subtractions on one deal and the script refuses to run without being told which. `--notch` prints the consequence nobody publishes: withholding applies to the whole payment once it reaches 250,000 VND rather than to the excess, so every payment between 250,000 and 277,778 takes home less than 249,999 does. Twelve gates, and the three critical ones ask where the numbers came from rather than whether the deal is good — an unsourced return rate blocks before any total is believed, and a fee quoted from a page Shopee superseded in July 2025 is caught by name.

The same unit carries what the person posting the link now owes by law. `data/vn-advertising-law.csv` holds 65 rows across eight instruments, each cited to its gazette PDF: Vietnamese law names the creator personally, sets no follower threshold, requires disclosure immediately before *and during* the advertising, and prescribes no wording — so a brief must mandate a marker without claiming a particular phrase is legally required. Seven rows carry a finding instead of a number, and four of those are open rather than settled: three need a lawyer, and one is an article the research never reached. [`references/affiliate-commerce.md`](marketing-minthep/references/affiliate-commerce.md).

### "Can we legally say this?"

```powershell
python marketing-minthep/scripts/check_claims.py --audit draft.md --sector cosmetics
python marketing-minthep/scripts/check_claims.py --template answers.csv --sector cosmetics
```

> 10 of 12 gates fail, 8 of them blocking. The rows named carry 345,000,000 to 505,000,000 VND if every one is charged separately, which Điều 4 allows.

That is one serum post with a superlative, a comparison, the word `đặc trị`, a dermatologist in frame and an unanswered dossier question. The advice everybody knows — hold evidence for what you claim — is the American question, and it is not the expensive one here. Nghị định 87/2026/NĐ-CP asks five, and `data/claim-evidence.csv` sorts all 41 rows by which: prohibited outright, needs a document, must match the filing, wording dictated by statute, layout dictated by statute. The one this skill had missed is the third. The benchmark named in Điều 50.5.c is the product's own registration or declaration, so a brand can hold a flawless clinical study, be telling the plain truth, and still be fined 30 to 40 million because the function was never written into the Phiếu công bố.

Two of the gates are art direction rather than copy. A doctor, a pharmacist, a uniform or a clinic in a cosmetics frame is banned outright at 15 to 20 million, and consent discharges nothing, because the prohibition is on the category of image — so it belongs in the negative constraints before an image is generated, not in a review afterwards. Nine gates read the draft and six read an answer sheet `--template` writes for you, and a blank row on that sheet fails its gate rather than passing it: a green report earned by nobody having looked is the failure this unit exists to prevent. Four sectors are refused by name instead of half-answered — medicine, chemicals, insecticidal preparations, plant protection products. [`references/claims-proof-ledger.md`](marketing-minthep/references/claims-proof-ledger.md).

### "Will this provider actually do what my prompt asks?"

```powershell
python marketing-minthep/scripts/check_prompt_grammar.py --prompt-file prompt.txt --provider flux
```

`data/prompt-grammar.csv` carries 69 rows across eight axes — encoder window, negative prompt, in-image text, seeds, character consistency, ownership, likeness — each with the vendor URL behind it and a column stating what the row does *not* establish. Five of the nine model families document no negative-prompt field at all, which means sending them an exclusion puts the excluded thing into the prompt. The checker found that bug in this repository's own compiler on its first run: a brief asking for *no plastic skin* was sending the words *plastic skin* to FLUX. Two length limits are kept separate on purpose, because an encoder window silently deletes the tail while an API character limit rejects the request outright. Eleven questions no vendor answers are recorded as gaps rather than filled in, and [`references/prompt-grammar.md`](marketing-minthep/references/prompt-grammar.md) lists nine things the prompt-tips genre gets wrong, including three parameters that no longer exist on the version people cite them for.

### "I have one file. Where can it actually go?"

```powershell
python marketing-minthep/scripts/check_channel_spec.py --survey --width 1080 --height 1920 --duration 22 --file-size 30MB --format mp4
```

> 7 placements take it untouched. 17 refuse it.

One shoot, exported once, posted everywhere — that is how nearly every small-business asset here gets made, and it is where the money leaks. The same 9:16 cut that is right for both Reels surfaces is 78% off the 4:5 that Facebook Feed video documents, so the platform crops it and picks the edges itself, which on a vertical frame means the plate at one end and the price at the other. The seventeen refusals are the more useful half of that answer: four YouTube surfaces want 16:9, two Google Display formats stop at 150KB and 600KB, and five are still surfaces that will not take an mp4 at any size. `data/channel-specs.csv` holds 24 placements across Meta, TikTok, Google Ads, YouTube and Google Merchant, each row stamped with the page it came off and the day somebody read it.

The reason it is a table and not a paragraph is what the pages disagree about. Four Meta placements publish a recommended size and a copy budget and then no technical block at all — no file ceiling, no minimum width, nothing on tolerance — while Facebook Reels video says in words that there is no maximum length. Both are "no number", and only one of them is a fact. The checker never returns a pass against silence; it returns exit 3 and names the page. Instagram Feed wants 4:5 for the still and 9:16 for the video on the same surface, so a resize cannot serve both. Google Merchant's 500x500 floor starts on 2027-01-31, which means a feed that passes today fails then with no change on your side. Rows go to review after ninety days, and that bet has already paid once: the Shopee article an earlier version of this unit cited now returns 404. [`references/channel-spec-registry.md`](marketing-minthep/references/channel-spec-registry.md).

### "Which numbers should I report, and did we actually hit them?"

```powershell
python marketing-minthep/scripts/find_recipe.py --table kpi --query "retention"
python marketing-minthep/scripts/score_kpi.py --input scorecard.json
```

27 measurables in `data/kpi-metrics.csv`, each with the direction that counts as good, whether it leads or lags, and the specific way it gets gamed — because every metric has a way to be hit without the underlying thing improving, and naming it is the difference between a scorecard and a target. An achievement rate has four branches depending on whether higher is better, whether zero is the floor, and whether the target can be exceeded; picking the wrong branch changes the number without changing how plausible it looks. [`references/kpi-scorecards.md`](marketing-minthep/references/kpi-scorecards.md).

### "The month is over. How do I put it on a page?"

```powershell
python marketing-minthep/scripts/build_variance_report.py --input period.json
```

> | Click-through rate | % | 0.9 | 1.2 | -0.3 pp / -25.0% (unfavourable) |
> | Net Promoter Score | No | 44 | - | no figure |
> | Signed-document milestone | Date | 2026-08-05 | 2026-08-01 | +4 days (unfavourable) |

A different job from scoring the card, and it fails differently. Nobody in that meeting recomputes anything. They read the sign, the size and the label, then leave with whatever those said.

CAC down 18% and revenue down 18% are not the same month. So favourability comes off the stored `direction` and prints as a word. Not a colour. A colour survives neither a photocopier nor a paste into email.

Conversion 2.5% to 3.1% is +0.6 pp, and it is also +24%. Those two are a factor of forty apart and both are one keystroke from the truth. NPS 41 to 44 is +3 points rather than +7.3%, because the zero on that scale is a convention somebody chose. A date variance is days and nothing after that.

Three resellers against a plan of two is +50%. It is one person. Under a base of 30 the two raw figures stand instead, and the floor is printed in the output so a reader can see the bet.

A row with no plan has no plan. An absent column gets one line above the table. One hole in a column that is full everywhere else gets a note counting the rows around it, because that is the cell a reader turns into a zero.

Exit 3 means the table is not ready. Never that the month was bad. [`references/report-notation.md`](marketing-minthep/references/report-notation.md) also records the part of ISO 24896 that sits behind an access control this repo will not go round, which is why it quotes no rule number anywhere.

### "Is this test big enough to tell me anything?"

```powershell
python marketing-minthep/scripts/check_test_readout.py --plan --baseline 0.03 --mde 0.20
```

> Detecting a 20% relative lift on 3.00% needs 13911 per arm, 27822 in total.

Worth knowing while the test is still cheap rather than after two weeks of traffic. `--claim` goes the other way and checks a declared winner against the confidence interval instead of the point estimate: a 58% headline lift at p = 0.29 is not a result, and the readout says so in the verdict rather than in a footnote.

### "Will this be the same person in the next photo?"

```powershell
python marketing-minthep/scripts/plan_virtual_person.py
```

Adjectives do not reproduce a face. `data/person-parameters.csv` describes a virtual person on 35 measurable axes, nineteen of them locked as identity, hashed into a stable seed so the same person renders twice — and the run says plainly that exactly one vendor publishes a character-consistency ceiling and it is four characters. The pose unit is the same discipline applied to the body: a pose is cited on named axes rather than described as *elegant*. This is a constructed person, never a real one; the skill will not build a likeness from a photograph of somebody's face, and [`references/virtual-person-system.md`](marketing-minthep/references/virtual-person-system.md) records why as a reason rather than a rule.

### "Does this draft read like a person wrote it?"

```powershell
python marketing-minthep/scripts/check_specificity.py --check draft.md
python marketing-minthep/scripts/rewrite_human.py --check draft.md --channel web
python marketing-minthep/scripts/check_address_register.py --check draft.md
```

In that order, and the order is the point. Rhythm editing deletes specifics, so the checkable facts get counted first: under three of them the draft has a content problem, and every cadence fix from there makes it read better while still saying nothing. The third command is Vietnamese-only and settles a question English style guides cannot — which pronoun register the copy is in, and whether it stays there, because a page that opens with *bạn* and closes with *quý khách* has changed who it thinks it is talking to. The whole layer is indexed in [`references/anti-slop-index.md`](marketing-minthep/references/anti-slop-index.md): each tell family traced to the published literature it comes from, and the Vietnamese tells recorded as this repo's own observation, because no Vietnamese catalogue existed to cite.

### "Who is supposed to do all this on Monday?"

```powershell
python marketing-minthep/scripts/plan_operating_load.py
python marketing-minthep/scripts/plan_composition_set.py --photos 3
```

Thirteen roles, sorted into what runs once and what runs every week, costed in hours. A channel plan nobody has time to execute is a wish list, and this is the file that says so with a number. The second command answers the same question about images: given the photographs that already exist, how many of the frames this plan assumes can be cut from them and how many need another exposure.

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
  SKILL.md                  entry point and router, 203 lines
  references/               66 topic files, each under 150 lines
    dossiers/               15 deep-craft dossiers + index
  data/                     35 lookup tables: image recipes, palettes, layout
                            dials, slop tells, copy formulas, translation and
                            address-register tells, reference axes, frame
                            ratios, composition grids, KPI metrics and aspect
                            weights, colour gates, makeup looks and
                            diagnostics, person parameters, prompt grammar,
                            product compositions, benchmarks, market-data
                            sources, customer-evidence sources, lifecycle
                            duties, lead states, channel specs, command
                            artifacts, VN marketer roles
  scripts/                  48 tools + test suite
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

616 tests, including ones that recompute every contrast ratio in `data/palettes.csv`, fail if a copy example contains a printable number, fail if a capability flag cites a source row that does not exist, fail if any placement check clears an asset against a figure the vendor page never published, and fail if a deliverable names a script that is not in the repository. `evaluate_workbench.py` replays the routing cases in `assets/evals/`. `.github/workflows/deploy-pages.yml` runs structure checks, the planner, the manifest builder, the unit tests and Python compilation, then deploys `docs/` to GitHub Pages.

## What it will not do

- Invent a claim, ingredient, spec, price, review, customer, statistic, certification, scarcity cue or endorsement.
- Copy a celebrity identity, a living artist's style, a specific campaign, photograph or signature layout. References are decomposed into attributes or not used.
- Slim or reshape a real person's body in an edit.
- Present an AI-generated package as a photograph of the real product without an exact reference.
- Publish, contact press or creators, buy ads, or change a live campaign. Those need separate authorization.
- Call a prompt an image, a storyboard a video, or a plan a result.

## Operating limits

Platform specs change; verify the official source live before export or upload. Image results depend on the provider, valid references and whatever rendering capability actually exists at the time. PR, legal, health, finance, comparative and regulated claims need evidence and owner approval. This skill plans and produces artefacts; publishing, media buying, outreach and deployment remain yours.

<p align="center">
  <a href="README.md"><kbd> &nbsp; <b>English</b> &nbsp; </kbd></a>
  <a href="README.vi.md"><kbd> &nbsp; Tiếng Việt &nbsp; </kbd></a>
</p>
