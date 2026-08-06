# Worked example — the 2024 company scorecard

Two files, differing only by three repairs.

- `card-as-shipped.json` — the card transcribed from the source workbook exactly as it was in use. Scoring it produces no total.
- `card-repaired.json` — the same card with the duplicate code renamed and the missing actual supplied. Nothing else differs, so the diff between the two files *is* the audit.

Achievement figures are deliberately not transcribed. Recomputing them from the stored targets and actuals is the entire point of the exercise.

## Run it

```
python scripts/score_kpi.py --input card-as-shipped.json   # save the JSON block below to a file first
python scripts/score_kpi.py --input card-repaired.json     # save the JSON block below to a file first
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


---

## card-as-shipped.json

```json
{
  "_comment": "The 2024 company scorecard exactly as it was shipped, transcribed from BSC_2025_template.xlsx sheet 2024. Targets and actuals are the stored values; achievement is deliberately NOT transcribed, because recomputing it is the point. Scoring this card refuses, and the refusal list is the audit.",
  "level": "company",
  "owner": "Hanoia",
  "fiscal_year": 2024,
  "kpis": [
    {
      "code": "F1.1.1",
      "kpi_id": "revenue",
      "objective": "Increase profit",
      "label": "Revenue Hermes",
      "overall_weight": "0.10",
      "target": "3400000",
      "actual": "2890353.4840580029"
    },
    {
      "code": "F1.1.2",
      "kpi_id": "revenue",
      "objective": "Increase profit",
      "label": "Revenue Hanoia & Others",
      "overall_weight": "0.10",
      "target": "3200000",
      "actual": "1766464.7764399999"
    },
    {
      "code": "F1.2.1",
      "kpi_id": "gross_margin",
      "objective": "Increase profit",
      "label": "Gross profit margin Hermes",
      "overall_weight": "0.10",
      "target": "0.64",
      "actual": "0.53959999999999997"
    },
    {
      "code": "F1.2.1",
      "kpi_id": "gross_margin",
      "objective": "Increase profit",
      "label": "Gross profit margin Hanoia & Others — note the code repeats the row above, which is how the workbook shipped",
      "overall_weight": "0.10",
      "target": "0.40",
      "actual": "0.460635718783591"
    },
    {
      "code": "F2.1",
      "kpi_id": "operating_cost",
      "objective": "Optimise cost",
      "label": "Operating cost",
      "overall_weight": "0.10",
      "target": "1752681",
      "actual": "1223952.5694800001"
    },
    {
      "code": "C1.1",
      "kpi_id": "miv",
      "objective": "Brand awareness",
      "label": "Raise brand awareness by 30% measured by MIV",
      "overall_weight": "0.10",
      "target": "561600",
      "actual": "685000"
    },
    {
      "code": "C1.2",
      "kpi_id": "sop_published",
      "objective": "Issue retail guidelines for distributors",
      "label": "Brand, social and VM guidelines published",
      "overall_weight": "0.05",
      "target": "3",
      "actual": "3",
      "scale": { "0.50": "1", "0.75": "2", "1.00": "3" }
    },
    {
      "code": "C2.1",
      "kpi_id": "new_craft_orders",
      "objective": "New craft orders",
      "label": "Share of new-craft SKUs ordered for 25SS",
      "overall_weight": "0.05",
      "target": "0.10",
      "actual": "0.1475"
    },
    {
      "code": "C2.2",
      "kpi_id": "illustration_collabs",
      "objective": "Illustration products",
      "label": "Artist collaborations proposed for 25FW and 25SS",
      "overall_weight": "0.05",
      "target": "4",
      "actual": "3",
      "scale": { "0.00": "0", "0.25": "1", "0.50": "2", "0.75": "3", "1.00": "4" }
    },
    {
      "code": "C3.1",
      "kpi_id": "resellers_acquired",
      "objective": "Develop international market",
      "label": "Resellers acquired for the international market",
      "overall_weight": "0.05",
      "target": "3",
      "actual": "3",
      "scale": { "0.00": "0", "0.25": "1", "0.50": "2", "0.75": "3", "1.00": "4" }
    },
    {
      "code": "P1.1",
      "objective": "Improve core operational workflow",
      "label": "Participants passing the cross-department workflow test",
      "aspect": "P",
      "direction": "higher_better",
      "calc_method": "scale",
      "indicator_type": "leading",
      "is_financial": "no",
      "overall_weight": "0.05",
      "target": "0.80",
      "actual": "0.80",
      "scale": { "0.25": "0.30", "0.50": "0.50", "0.75": "0.65", "1.00": "0.80" }
    },
    {
      "code": "P2.1",
      "kpi_id": "milestone_date",
      "objective": "Improve core cooperation flow",
      "label": "Retail and corporate agreement signed by TS and HNA",
      "overall_weight": "0.05",
      "target": "2024-06-30",
      "actual": "2024-01-30",
      "scale": {
        "0.00": "2024-11-30",
        "0.25": "2024-10-30",
        "0.50": "2024-09-30",
        "0.75": "2024-07-30",
        "1.00": "2024-06-30"
      }
    },
    {
      "code": "G1.1",
      "objective": "HRMS project fulfilment",
      "label": "HRMS project delivered against the group HR timeline",
      "aspect": "G",
      "direction": "higher_better",
      "calc_method": "ratio",
      "indicator_type": "lagging",
      "is_financial": "no",
      "overall_weight": "0.10",
      "target": "1.00",
      "actual": null
    }
  ]
}

```

## card-repaired.json

```json
{
  "_comment": "The same 2024 card with the three blocking problems repaired and nothing else touched: the duplicate F1.2.1 code renamed to F1.2.2, and G1.1 given the actual it was missing. Targets, actuals and weights are otherwise byte-identical to card-as-shipped.json, so the difference between the two files is exactly the audit and nothing more.",
  "level": "company",
  "owner": "Hanoia",
  "fiscal_year": 2024,
  "kpis": [
    {
      "code": "F1.1.1",
      "kpi_id": "revenue",
      "objective": "Increase profit",
      "label": "Revenue Hermes",
      "overall_weight": "0.10",
      "target": "3400000",
      "actual": "2890353.4840580029"
    },
    {
      "code": "F1.1.2",
      "kpi_id": "revenue",
      "objective": "Increase profit",
      "label": "Revenue Hanoia & Others",
      "overall_weight": "0.10",
      "target": "3200000",
      "actual": "1766464.7764399999"
    },
    {
      "code": "F1.2.1",
      "kpi_id": "gross_margin",
      "objective": "Increase profit",
      "label": "Gross profit margin Hermes",
      "overall_weight": "0.10",
      "target": "0.64",
      "actual": "0.53959999999999997"
    },
    {
      "code": "F1.2.2",
      "kpi_id": "gross_margin",
      "objective": "Increase profit",
      "label": "Gross profit margin Hanoia & Others",
      "overall_weight": "0.10",
      "target": "0.40",
      "actual": "0.460635718783591"
    },
    {
      "code": "F2.1",
      "kpi_id": "operating_cost",
      "objective": "Optimise cost",
      "label": "Operating cost",
      "overall_weight": "0.10",
      "target": "1752681",
      "actual": "1223952.5694800001"
    },
    {
      "code": "C1.1",
      "kpi_id": "miv",
      "objective": "Brand awareness",
      "label": "Raise brand awareness by 30% measured by MIV",
      "overall_weight": "0.10",
      "target": "561600",
      "actual": "685000"
    },
    {
      "code": "C1.2",
      "kpi_id": "sop_published",
      "objective": "Issue retail guidelines for distributors",
      "label": "Brand, social and VM guidelines published",
      "overall_weight": "0.05",
      "target": "3",
      "actual": "3",
      "scale": {
        "0.50": "1",
        "0.75": "2",
        "1.00": "3"
      }
    },
    {
      "code": "C2.1",
      "kpi_id": "new_craft_orders",
      "objective": "New craft orders",
      "label": "Share of new-craft SKUs ordered for 25SS",
      "overall_weight": "0.05",
      "target": "0.10",
      "actual": "0.1475"
    },
    {
      "code": "C2.2",
      "kpi_id": "illustration_collabs",
      "objective": "Illustration products",
      "label": "Artist collaborations proposed for 25FW and 25SS",
      "overall_weight": "0.05",
      "target": "4",
      "actual": "3",
      "scale": {
        "0.00": "0",
        "0.25": "1",
        "0.50": "2",
        "0.75": "3",
        "1.00": "4"
      }
    },
    {
      "code": "C3.1",
      "kpi_id": "resellers_acquired",
      "objective": "Develop international market",
      "label": "Resellers acquired for the international market",
      "overall_weight": "0.05",
      "target": "3",
      "actual": "3",
      "scale": {
        "0.00": "0",
        "0.25": "1",
        "0.50": "2",
        "0.75": "3",
        "1.00": "4"
      }
    },
    {
      "code": "P1.1",
      "objective": "Improve core operational workflow",
      "label": "Participants passing the cross-department workflow test",
      "aspect": "P",
      "direction": "higher_better",
      "calc_method": "scale",
      "indicator_type": "leading",
      "is_financial": "no",
      "overall_weight": "0.05",
      "target": "0.80",
      "actual": "0.80",
      "scale": {
        "0.25": "0.30",
        "0.50": "0.50",
        "0.75": "0.65",
        "1.00": "0.80"
      }
    },
    {
      "code": "P2.1",
      "kpi_id": "milestone_date",
      "objective": "Improve core cooperation flow",
      "label": "Retail and corporate agreement signed by TS and HNA",
      "overall_weight": "0.05",
      "target": "2024-06-30",
      "actual": "2024-01-30",
      "scale": {
        "0.00": "2024-11-30",
        "0.25": "2024-10-30",
        "0.50": "2024-09-30",
        "0.75": "2024-07-30",
        "1.00": "2024-06-30"
      }
    },
    {
      "code": "G1.1",
      "objective": "HRMS project fulfilment",
      "label": "HRMS project delivered against the group HR timeline",
      "aspect": "G",
      "direction": "higher_better",
      "calc_method": "ratio",
      "indicator_type": "lagging",
      "is_financial": "no",
      "overall_weight": "0.10",
      "target": "1.00",
      "actual": "1.00",
      "actual_source": "Group HR confirmation of project fulfilment. The shipped workbook left this cell empty and typed 100% into the achievement column beside it, which is the single most expensive bug in the file: an unmeasured KPI carrying a tenth of the card at full marks."
    }
  ]
}

```
