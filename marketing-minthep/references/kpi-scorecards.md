# KPI scorecards

Build a balanced scorecard, weight it, cascade it, and score it from stored targets and actuals. The output is attached to somebody's pay, so the standard here is higher than for a plan: a plan that is wrong gets revised, and a scorecard that is wrong gets paid out.

Everything in this file was reconstructed from a real 2025 BSC workbook and its 2024 predecessor. Every fixture is a figure read out of that file. The ten faults catalogued at the bottom are faults in the source, not hypotheticals — which is the point. That workbook was in use, had been reviewed, and its total was wrong by 4.32 points.

## The shape of a card

Four aspects, and the letters matter because two of them collide:

| Code | Aspect | Note |
|---|---|---|
| `F` | Finance | |
| `C` | Customer | |
| `P` | Processes & System | |
| `G` | People | **Not `P`.** `P` was taken. Every real code in the source file reads `G1.1`. |
| `D` | Dept Function | Department cards only — a fifth aspect for the bottom-up rows |

A department card carries five aspects, not four. Code that hardcodes four works at company and individual level and breaks the moment somebody builds a department card.

## Three weights, and only one of them is real

Every row carries a BSC Proportion (the aspect's share of the card), a Portion Weight (the row's share of its aspect) and an Overall Weight. The relationship is `Overall = Proportion × Portion`.

**Store Overall. Compute Portion.** Not the other way round, and never both.

The reason is in the source file. Its Customer block stores all three, and its Portion column sums to 90% while its Overall column sums correctly to the 30% proportion. The two columns disagree, both look plausible, and there is no way to tell from the file which one somebody meant. A stored column that can be derived is a column that will eventually contradict its own source.

Rules that hold regardless:

- Overall weights across the whole card sum to exactly 100%.
- No KPI carries less than 5%. This floor is also what keeps a card to roughly twenty rows without a separate rule.
- Ten to twelve KPIs is the guideline ideal. Treat a card outside that as a question, not an error — a real card sometimes has a reason.

Guideline allocations per block live in `data/kpi-aspect-weights.csv`, keyed by `block` and `aspect`. Company level is fixed at 50/25/10/15. The three office blocks carry ranges, because a front-office team and a back-office team should not be weighted alike: Finance runs 60% out front and as low as 10% in the back, and People runs the other way, from 5% out front to as much as 50% in the back. A back-office team scored heavily on revenue is being scored on somebody else's work.

Note that the 2024 card used 50/30/10/10, not the guideline's 50/25/10/15. The engine does not enforce the guideline shares — it enforces that they sum to 100% and reports what the card declared. A guideline is a starting point with a reason attached, and a card that departs from it needs a reason of its own, not a blocked run.

## Achievement has four branches

This is where a scoring engine is usually wrong, and it is usually wrong in exactly one branch, which is why it stays wrong: the other three keep producing plausible numbers all year.

**1. Ratio, higher is better.** `actual / target`. Revenue, margin, counts, rates.

**2. Ratio, lower is better.** `target / actual`. Cost, complaints, lead time, turnover, CAC.

Getting this backwards inverts a year. The source file's operating cost came in at 1,223,952 against a 1,752,681 plan — that is 143.20% scored correctly, and 69.83% if you reach for `actual / target`. A well-run year reported as a failure, from one division the wrong way round.

No unit and no name tells you which branch applies. Gross margin and cost-to-revenue are both denominated in per cent and run in opposite directions. This is why `direction` is a stored column on every row of `data/kpi-metrics.csv`.

**3. Scale.** Six named rungs at 0 / 25 / 50 / 75 / 100 / 120%, keyed to threshold *values* rather than to fractions of the target. The score is the highest rung the actual reached.

A scale is not a ratio that happens to land on the same rungs. The source file's reseller KPI had rungs of 0/1/2/3/4 against a target of 3, which puts the full rung at 4 — so an actual of 3 that met its target scores 75% on the scale and 100% as a ratio. The file typed 100%. The rung table was the thing that was wrong, and hand-typing over the output hid that instead of fixing it. A scale whose 100% rung sits above its own target is misaligned; check for that before you check the score.

Its illustration-collaboration KPI, by contrast, had rungs aligned to its target, where the scale and the ratio agree. Both rows are in the test suite deliberately: a suite that only tested the aligned row would pass with the scale branch deleted.

**4. Date.** The scale branch on a day axis. Earlier is better, so the rungs run *later* as achievement falls.

Compare day ordinals, never strings. ISO dates happen to sort correctly as text and no other format does, so a string comparison is a bug that passes its first test. The source file stores these as Excel serials, which is why `45473` and not a date appears in the cell.

A date KPI also scores fully the moment it lands and then says nothing for the rest of the year. It belongs beside a KPI that keeps moving, not alone in an aspect.

## Caps

130% on financial KPIs. 100% on everything else.

The asymmetry is the point. A financial KPI can be rewarded for overshooting, because the overshoot is money that exists. A non-financial one cannot, because 147% of a count is usually a target that was set too low.

The source file states both caps and applies neither. One row runs at 143.20%. Two more were hand-typed down to 120% — and for a non-financial row the cap is 100%, so the hand-cap was wrong in level as well as in method, and it destroyed the raw figure on the way. Keep both numbers. A card that stores only the capped figure cannot answer "how far over were we", which is the question an override request is made of.

An override needs a named approver on the row. The engine then scores uncapped, reports the breach as a warning, and keeps the audit trail the hand-typed cell threw away.

## Totals and rank

Per aspect: `SUMPRODUCT(overall_weight[], capped_achievement[])`. Card total: the plain sum of the four aspect scores.

**Do not multiply an aspect total by its proportion.** The proportion is already inside every overall weight. Doing it twice is the classic error and produces a total in the low twenties that looks like a catastrophic year.

Rank thresholds, transcribed from the workbook's own nested `IF`:

| Total | Rank |
|---|---|
| under 70% | C |
| under 80% | B |
| 80% up to **and including** 90% | A3 |
| above 90%, under 105% | A2 |
| 105% and above | A1 |

A3 is the one rung that uses `≤` rather than `<`, so exactly 90.0% is A3 and 90.0001% is A2. Rewriting all five with `<` moves the 90% case up a grade.

Store rank order as an integer alongside the code. `A1` sorts before `A3` alphabetically, so any ordering, ranking or "top performers" query built on the code string is silently reversed at the top.

## Use Decimal, not float

The source workbook leaks `0.9500000000000001` and `0.31749999999999995` into cells a bonus is read from. That is float error surfacing in front of the person being scored.

Parse from the string form. `Decimal(0.1)` is `0.1000000000000000055511151231257827`, so a JSON number that arrives already parsed as a float has to be re-rendered with `repr` before it is trusted.

## Refuse rather than guess

`scripts/score_kpi.py` produces no total at all while any blocking problem stands. This is deliberate, and it is the single most important behaviour in the script.

Blocking:

- **A KPI with no actual.** The source file's People aspect had one: no actual, 100% typed in the achievement column, a tenth of the card. An unmeasured KPI at full marks is the most expensive bug in the file.
- **A lower-is-better KPI reporting an actual of zero.** Not the mirror of a zero on a revenue KPI, which scores zero and is fine. Spending nothing is a missing number far more often than a perfect year, and scoring it as 130% pays a bonus for an empty cell.
- **A target of zero on a higher-is-better KPI.** Achievement is undefined.
- **Weights that do not sum to 100%,** summed across every declared row.
- **A duplicate KPI code.** The source file has one: two different margin KPIs both coded `F1.2.1`.
- **An aspect the level does not carry.**

Warned, not blocked: a KPI count outside 10–12; a cap override; an aspect carrying only lagging indicators; a card row whose aspect disagrees with its own code prefix; a target set from no baseline.

A partial total presented as a total is worse than no total, because it looks finished.

## The card's aspect wins over the library's

A row's placement is decided by its code. `C1.2` is a Customer row because its code says so.

`data/kpi-metrics.csv` also files each metric under an aspect, but that is only where the metric *usually* lives. The 2024 card measures published retail guidelines and puts them in Customer, on purpose, because the guidelines are for distributors — while the library files a published-document count under Processes. Letting the library win silently moved 5% of the card between two aspects and made both subtotals wrong while the total stayed right. The engine now scores by the code and warns about the disagreement.

## Lagging and leading

A lagging KPI reports what happened. A leading one moves before the thing you care about does.

An aspect made only of lagging KPIs can be reported but not steered, because every number in it arrives after the decisions that moved it. The source file's own worked example: company turnover under 20% is lagging and arrives too late to act on, so HR carries a happiness-survey score above 80% and a flexible-working launch date as its leading pair.

This is also what makes an indirect cascade legitimate. A department KPI that is not the parent KPI in smaller units has to be a stated leading indicator *of* it, which means the link needs a table with a `link_type`, not a self-referential parent field. A self-FK cannot express "this is a leading indicator of that" — it can only express "this is a slice of that".

## Cascading

Roughly 70–80% of a card comes down from the level above, and 20–30% comes up from the level itself. A card that is 100% inherited gives its owner nothing to own; one that is mostly bottom-up is not connected to the strategy.

Direct cascade: the same KPI, a smaller number. Indirect: a different KPI that leads the parent, with the link stated.

## Targets and actuals both need provenance

A target needs a version and, from version two onward, a mandatory reason. The source file moved a margin target from 56% to 57% and logged why; it also moved a COGS-saving target because labour cost was reclassified between two accounts. That second one matters beyond the target: the 2024 and 2025 figures are no longer comparable, and a chart drawing them as one line is wrong even though both numbers are right.

An actual needs three fields: the raw measurement, the adjusted figure, and the reason for the difference. The file's MIV row excludes February, because one unplanned mention by another brand moved the month enough to distort the year. That exclusion is defensible and it is recorded — but a single `actual` column cannot hold it.

## Traps worth knowing before you pick the metric

Every row in `data/kpi-metrics.csv` carries a `trap` column. The expensive mistake with a KPI is almost never picking the wrong one; it is scoring the right one the wrong way round, or reading it without its pair.

- **MIV** is denominated in money and is not revenue. Adding it into a financial total inflates the year. It is also very noisy.
- **ROMI** needs gross profit on the numerator, not revenue. Substituting revenue turns a losing campaign into a winning number, invisibly.
- **MER** is deliberately unattributed, which is its strength and its limit. It says the engine is working, never which part. Do not cascade it to a channel owner as a personal KPI.
- **NPS** runs from −100 to +100, so a ratio breaks across zero: −10 against a target of 20 returns −50%, and −10 against a target of −20 returns +50%. Score it on a scale.
- **CAC** is money-denominated but not booked in the financial statements, so which cap applies is an organisational decision. The source file does not answer it. The catalog grades it non-financial as the safer default, because the lower cap cannot inflate a bonus.
- **Brand awareness** is a survey number with sampling error. Store the sample size, or 80% of 20 people and 80% of 2,000 people print identically.
- **CTR** is cheap to move and easy to mistake for a result. A creative that doubles CTR and halves conversion has made the number better and the business worse.
- **Complaints** fall when logging gets worse as readily as when service improves.
- **On-time delivery** improves when the promise gets looser. Read it beside lead time, or a team hits it by quoting four weeks for everything.
- **Lead time** averages hide the tail. Ten orders at three days and one at forty averages to six, and the one at forty is the complaint.
- **Retention rate** is defined by its window. Monthly and annual retention are different metrics with the same name.
- **Training hours** and **SOPs published** are activity counts, fully achievable while nothing changes. Give each a lagging partner or drop it.

## Procedure

1. **Name the level and the owner.** Company, department or individual. A department card carries the fifth aspect.
2. **Get the baselines.** Last year's actual per proposed KPI. Where there is none, say so — a target set from no baseline is a guess and has to be marked as one.
3. **Allocate the aspects.** `python scripts/find_recipe.py --table kpi_weights --query "<block>"`. State a reason for anything outside the guideline range.
4. **Pick the metrics.** `python scripts/find_recipe.py --table kpis --query "<what you want to measure>"`. Read the `trap` column on every row you take, and record what you did about it.
5. **Set direction and method per row,** from the four branches. Cost rows are `target / actual`. Check that every scale's 100% rung equals its target.
6. **Write the card as JSON** and score it: `python scripts/score_kpi.py --input card.json`. Never type an achievement figure by hand. The exit code is non-zero while the card is unscoreable, so a pipeline cannot carry an unscored card forward as though it passed.
7. **Answer every warning,** with a fix or with a stated reason.
8. **Read the weights back as behaviour.** If the heaviest rows can all be hit without the strategy moving, the card measures the wrong things. Per heavy KPI, name the cheapest way to hit it without doing the work.

## Worked example

`assets/examples/bsc-2024/` holds the real 2024 company card in two files. `assets/examples/bsc-2024/card-as-shipped.json` refuses to score and names its faults; `assets/examples/bsc-2024/card-repaired.json` differs only by those repairs.

Four totals are involved, and the relationship between them is the lesson:

| Total | What it is |
|---|---|
| 98.79% | what the workbook reports |
| 48.29% | its Finance subtotal, using the uncapped 143.20% |
| 94.47% | its own achievement figures with the stated caps applied |
| 94.47% | recomputed by the engine from raw targets and actuals |

The last two agree, and they agree by coincidence. Two achievement bugs survive in the shipped file — a scale row scored as a ratio and a scale row scored one rung low — and both are 25 points at a 5% weight with opposite signs, so they cancel exactly. Two independent errors, equal and opposite, landing on the same total by two different routes.

That is the whole argument for recomputing rather than reconciling. A total that agrees with a spreadsheet is not evidence the spreadsheet is right.

The rank happens not to move: A2 either way. The gap is 4.32 points and the rank is attached to a bonus, so "the rank did not move" is luck, not a defence.

## Faults catalogued in the source workbook

Kept as a list because each one is a test in `scripts/test_tools.py`, and because a reviewer reading this file should expect to find these in any workbook of this kind.

1. A KPI with no actual scored at 100%, carrying 10% of the card.
2. A stated cap never applied; one row scored at 143.20%.
3. Two achievement figures hand-typed over the formula, one of them to a cap level that did not apply to that row.
4. A scale KPI scored as a ratio, where the two formulas disagree.
5. A scale KPI scored one rung below what its own rung table gives.
6. Two different KPIs sharing the code `F1.2.1`.
7. A Portion Weight column that sums to 90% while the Overall column it derives from is correct.
8. Float error visible in stored cells: `0.9500000000000001`, `0.31749999999999995`.
9. A target set from a baseline of zero with no note.
10. Dates stored as bare Excel serials, so the rung table is unreadable without conversion.
