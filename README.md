# Marketing-Minthep

<p align="right">
  <a href="README.md"><kbd> &nbsp; <b>English</b> &nbsp; </kbd></a>
  <a href="README.vi.md"><kbd> &nbsp; Tiếng Việt &nbsp; </kbd></a>
</p>

A marketing skill for Claude Code and GPT/Codex. You type what a shop owner would actually type — *"làm cái poster khai trương"*, *"sao không ai mua"* — and it finds the marketing decision hiding inside the ask, makes it, and ships one committed deliverable with its facts labelled `confirmed / observed / inferred / unknown`. It never invents a price, a review, or a statistic.

```text
$marketing-minthep
```

<table>
  <tr>
    <td width="25%"><a href="docs/assets/generated/minthep-serum-packshot.png"><img src="docs/assets/generated/minthep-serum-packshot.png" alt="Serum packshot, concept packaging" /></a></td>
    <td width="25%"><a href="docs/assets/generated/minthep-serum-key-visual.png"><img src="docs/assets/generated/minthep-serum-key-visual.png" alt="Serum key visual" /></a></td>
    <td width="25%"><a href="docs/assets/generated/bun-bo-menu-quiet-editorial.svg"><img src="docs/assets/generated/bun-bo-menu-quiet-editorial.svg" alt="Menu drawn by code, quiet editorial direction" /></a></td>
    <td width="25%"><a href="docs/assets/generated/refsheet-palettes.svg"><img src="docs/assets/generated/refsheet-palettes.svg" alt="Palette sheet with measured contrast ratios" /></a></td>
  </tr>
</table>

Two photographs from the image pipeline; the menu and palette sheet were drawn by scripts, and every contrast ratio printed on them is a measurement. More on the [live demo page](https://thepkz.github.io/marketing-skill/).

## Output, before and after

The same Vietnamese About-us paragraph, drafted then rewritten through the skill. Both texts are kept verbatim in [`rewrite-human-worked-example.md`](marketing-minthep/assets/examples/rewrite-human-worked-example.md), so you can re-run the gate on them yourself and watch the first fail and the second pass:

| Measured | Draft | Rewrite | Gate |
|---|--:|--:|---|
| Checkable facts | 1 | 8 | ≥ 3 |
| Sentences a competitor could publish unchanged | 3 of 4 | 2 of 8 | ≤ 50% |
| Sentence-length variation (CV) | 0.10 | 0.85 | ≥ 0.45 |
| Empty-evidence adjectives per 150 syllables | 1.55 | 0.0 | ≤ 1.0 |
| Vietnamese machine-translation tells | 4 | 0 | 0 blocking |
| **Verdict** | **failed, 6 blocking** | **passed** | |

Every number is printed by a script you can run on your own draft. The facts in the rewrite came from the shop, not from the model — that is the entire difference, and why the gate is arithmetic instead of taste.

## Two full runs, kept verbatim

Simulated user messages, taken end to end, with the real gate readouts at the bottom of each file — including the round each draft failed first:

- [`làm cái poster khai trương`](marketing-minthep/assets/examples/simulated-run-khai-truong-poster.md) — the ask has no offer in it, so the skill builds the offer first (đồng giá 19K, capped at 200 cups, dated) and the poster becomes four lines. First draft failed brand-swap at 76%; final passes 6/6.
- [`sao không ai mua`](marketing-minthep/assets/examples/simulated-run-sao-khong-ai-mua.md) — 2,100 visits, 3 orders: the funnel diagnosis names *trust* as the leak with the arithmetic shown, and orders one free fix before any ad spend. First draft shipped two unsourced percentages; the gate caught both.

## What you can ask it

25 asks are mapped in [`data/ask-diagnosis.csv`](marketing-minthep/data/ask-diagnosis.csv) — each row names the real job hiding inside the words, what a good output is, and the failure it must avoid. A sample:

| You say | What it actually builds |
|---|---|
| "làm cái poster" | The offer first; a poster whose headline IS the offer, readable at 5 m |
| "viết content đi" | Posts each carrying one checkable fact — not ten fluent posts anyone could publish |
| "sao không ai mua" | A four-stage funnel diagnosis ending in one ordered fix |
| "để giá bao nhiêu" | A price with its margin-floor arithmetic shown |
| "lên kế hoạch marketing" | A standing `plan.md` of 10–30 lines with a review cadence, not a deck |

Asks with no marketing decision inside them — resize this, translate that — are done directly, no pipeline.

## Quick start

```powershell
python marketing-minthep/scripts/install_global.py     # installs for Claude Code + Codex
```

Create a working folder from one sentence, then gate any draft before it ships:

```powershell
python marketing-minthep/scripts/start_workbench.py --request "Tôi mở shop mỹ phẩm nhỏ ở Gò Vấp, không biết gì về marketing" --root .
python marketing-minthep/scripts/check_specificity.py --check draft.md
python marketing-minthep/scripts/check_output_shape.py --check draft.md
```

Gates exit `0` clean, `2` failed, `3` unsettled, `4` could-not-run — a crash is never a verdict.

## How it is built

```
marketing-minthep/
  SKILL.md            router: 12 rules, reads the ask before any tool
  references/         51 topic files — doctrine, loaded per job, never all at once
  data/               43 lookup tables — palettes, copy formulas, slop tells, ask map
  scripts/            52 tools — 11 gates that measure; the model owns the verdict
  assets/examples/    runnable inputs + the worked runs above
```

Scripts measure; they never generate content. There is no test suite behind them, on purpose: the gates are the tests, and they run on your draft at the moment it matters — every run is the test. A broken instrument exits `4` instead of passing you, so a crash can never issue a verdict. Depth in [ARCHITECTURE.md](ARCHITECTURE.md).

## What it will not do

- Invent a claim, price, review, statistic, certification, or scarcity cue.
- Copy a celebrity identity, a living artist's style, or a specific campaign. References decompose into attributes or go unused.
- Slim or reshape a real person's body in an edit.
- Call a prompt an image, a storyboard a video, or a plan a result.
- Publish, buy ads, or contact anyone — those stay yours.

<p align="center">
  <a href="README.md"><kbd> &nbsp; <b>English</b> &nbsp; </kbd></a>
  <a href="README.vi.md"><kbd> &nbsp; Tiếng Việt &nbsp; </kbd></a>
</p>
