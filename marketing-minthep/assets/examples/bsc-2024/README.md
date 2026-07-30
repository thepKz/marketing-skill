# Worked example — the 2024 company scorecard

Two files, differing only by three repairs.

- `card-as-shipped.json` — the card transcribed from the source workbook exactly as it was in use. Scoring it produces no total.
- `card-repaired.json` — the same card with the duplicate code renamed and the missing actual supplied. Nothing else differs, so the diff between the two files *is* the audit.

Achievement figures are deliberately not transcribed. Recomputing them from the stored targets and actuals is the entire point of the exercise.

## Run it

```
python scripts/score_kpi.py --input assets/examples/bsc-2024/card-as-shipped.json
python scripts/score_kpi.py --input assets/examples/bsc-2024/card-repaired.json
```

The first exits non-zero and lists three blocking problems. The second scores **94.47%, rank A2**.

## What the refusal catches

```
- G1.1 has no actual, so it has no achievement
- KPI code F1.2.1 appears 2 times — codes have to be unique
```

`G1.1` is the expensive one. It carries 10% of the card, has no measured actual, and the shipped workbook typed 100% into the achievement column beside the empty cell. A tenth of a bonus paid on an unmeasured KPI.

`F1.2.1` appears twice because two different gross-margin KPIs — one per brand — were given the same code. Any query that groups, ranks or joins on that code silently merges them.

Note what is *not* reported: a weighting error. The weights sum to exactly 100%. An earlier version of the engine said 90%, because it summed only the rows that managed to score and the dropped row took its 10% with it. That sent the reader to fix the wrong thing.

## The four totals

| Total | What it is |
|---|---|
| 98.79% | what the workbook reports |
| 48.29% | its Finance subtotal, using the uncapped 143.20% |
| 94.47% | its own achievement figures with the stated caps applied |
| 94.47% | recomputed here from raw targets and actuals |

The last two agree by coincidence, and that coincidence is the lesson. Two achievement bugs survive in the shipped file: a scale KPI scored as a ratio (`C3.1`, 100% instead of 75%) and a scale KPI scored a rung low (`P1.1`, 75% instead of 100%). Both are 25 points at a 5% weight, with opposite signs. They cancel exactly.

So two independent errors, equal and opposite, land on the same total by two different routes. A total that agrees with a spreadsheet is not evidence the spreadsheet is right.

The rank is A2 whichever number you use. The gap is 4.32 points, and the rank is attached to a bonus — so "the rank did not move" is luck rather than a defence.

## Which branch each row exercises

| Code | Branch | Why it is here |
|---|---|---|
| `F1.1.1` | ratio, higher better | The plain case, pinned to the cent: 85.01% |
| `F2.1` | ratio, lower better | 143.20% scored correctly; 69.83% if reversed |
| `C1.1` | ratio, capped | 121.97% raw, 100% scored, non-financial cap |
| `C2.1` | ratio, capped | 147.50% raw — the row the workbook hand-typed to 120% |
| `C2.2` | scale, aligned | Scale and ratio agree here, which is why it is not the only scale test |
| `C3.1` | scale, misaligned | Scale says 75%, ratio says 100%, target says met |
| `P1.1` | scale | Card-declared rather than looked up: exercises the fallback path |
| `P2.1` | date | Landed five months early; rungs run later as achievement falls |
| `G1.1` | ratio | The refusal |

## What to change if you are adapting this

The weights and the aspect proportions. This card runs 50/30/10/10, while the guideline in `data/kpi-aspect-weights.csv` says 50/25/10/15 at company level. That departure is real and the engine allows it — it enforces that the weights sum to 100%, not that they match the guideline. A guideline is a starting point with a reason attached; a card that departs from it needs a reason of its own.
