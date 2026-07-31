# Report notation

The period is over, the numbers exist, and now they have to sit on a page in front of somebody who was not in the room. That is a different job from working out whether the month was good, and it fails differently. `kpi-scorecards.md` decides whether a target was hit. This file decides what the line looks like once it is printed, which is where a correct number turns into a wrong sentence.

Nobody in the meeting recomputes anything. They read the sign, the size and the label, then leave with whatever those said. So the arithmetic is the smaller half. The larger half is that every figure on the page can be read as a different figure, and the reader has no way to tell which one you meant.

## The standard, and the part of it I could not read

ISO 24896 *Notation for business reporting* was published on **2026-06-11**, having passed the enquiry phase unanimously with the ISO member bodies. It sits with ISO/TC 37; project leader Diego Berea, co-editor Dr. Jürgen Faisst.

The text covers written reports, live presentations and analytic dashboards. It specifies the labelling of content, the layout of charts and tables, the representation of data values and the visualization of their characteristics, and it draws mainly on the UNIFY and CHECK parts of the IBCS SUCCESS formula. Read at `https://www.ibcs.com/iso-24896/` on 2026-07-31.

IBCS Standards 2.0 was approved and released the same day, aligned with the ISO text. It **reorganised the standards into a Notation part and a Composition part**, replacing the conceptual, perceptual and semantic structure that almost every third-party summary of IBCS still describes. Anything written from memory about IBCS is now describing the old shape. Read at `https://www.ibcs.com/ibcs-version-2-0/` on 2026-07-31, which is where `ibcs.com/standards/` redirects.

Now the limit on all of this, because it changes what this unit is allowed to claim about itself. IBCS is published free under a Creative Commons licence. The browsable copy, though, is served inside a viewer with printing and downloading switched off and its file path obfuscated. That is an access control.

This repo does not go round access controls, which is the line `channel-spec-registry.md` declined to cross for vendor pages.

**So no rule number is quoted anywhere in this unit, and nothing below is presented as a clause of ISO 24896.** Below is the arithmetic and the presentation discipline that can be checked by running something. If the standard is on your shelf, read it and correct me.

One thing survives without the rule text, because both pages state it plainly and it is the whole reason a notation standard exists. **The same meaning gets the same mark in every report you send.** A convention is worth exactly its repetition. A house that writes `AC` one month and `Actual` the next has no notation, only two months of typing.

`scripts/build_variance_report.py` prints `actual`, `plan` and `prior`. That is this repo's choice, not the standard's abbreviation set, which I could not verify. If your house follows IBCS, map the three onto it once and never mix.

## A minus sign is not bad news

CAC fell 18% and revenue fell 18%. One of those is a good month. Nothing in the unit, the name or the sign tells you which. Only the metric's `direction` does, which is why it is a stored column on every row of `data/kpi-metrics.csv` rather than something a script infers.

Two rows in that file settle the argument on their own. `gross_margin` and `cost_to_revenue` are both denominated in per cent, both talk about money, and they run in opposite directions. So a report that colours negatives red has just told its reader that a fall in cost-to-revenue was a bad month.

The tool derives favourability from `direction` alone and prints the word: `favourable`, `unfavourable`, `on plan`. Words, not colour. A colour survives neither a photocopier, nor a colourblind reader, nor a paste into email.

## A percentage point is not a per cent

Conversion moved from 2.5% to 3.1%. Two true statements come out of that:

- **+0.6 pp**, the movement in percentage points: the difference between the two figures.
- **+24%**, that same movement as a share of the figure compared against, which is `0.6 / 2.5`.

Print `+0.6%` and you have understated your own good month by a factor of forty. Print `+24 pp` and you have claimed conversion tripled. Both are one keystroke from the truth. Neither looks wrong.

The tool prints both figures, suffixes the first `pp`, and states the convention once above the table instead of on every row. A note repeated on every line stops being read by the third one.

## An index is not a quantity

NPS went from 41 to 44. That is **+3 points**, and it is not +7.3%. Points, not per cent.

The zero on that scale is a convention somebody chose rather than an absence of anything, and a percentage of a convention measures nothing at all. The same argument retires a per cent of a temperature, or of a satisfaction score out of five.

Counts sharing the same bare-number unit do have a real zero. Resellers signed, complaints received: a percentage of those means something. The distinction is not derivable from the unit column, so `INDEX_METRICS` in the script names the exceptions explicitly and explains itself in a comment. One name is in it today.

## A date takes days, and no percentage at all

A milestone landed on 5 August against a plan of 1 August. That is **+4 days**, and it is unfavourable. There the arithmetic stops. Four per cent later than a deadline is not a quantity, so the tool computes date variances on the day ordinal and then refuses to divide.

## A per cent of a small base is a true number that misleads

Three resellers signed against a plan of two is +50%. It is one person. Print the percentage and a board reads a strategy. Print `3 against 2` and they read a month.

Below a stated floor the tool prints the two raw figures instead of the percentage. **That floor is 30 by default, it is a presentation choice rather than a statistical test, and the figure used is printed in the output so a reader can see the bet.** Same honesty as the ninety-day expiry in `channel-spec-registry.md`. A number this repo chose gets labelled as a number this repo chose.

What counts as the base depends on the kind of metric, and getting that wrong is how a floor stops protecting anybody. For a quantity, the comparison figure *is* the base: a plan of two resellers is a base of two. For a rate it is not.

A plan CTR of 1.2 is not a base of 1.2. The base is the impressions underneath it, and no CSV in this repo knows that number.

So a rate row with no `base` supplied gets its percentage, and gets named for it in the notes. Better that than being quietly measured against a floor it was never standing on. Otherwise a three-point lift on 40 sessions prints exactly like the same lift on 40,000 sessions, and nothing on the page distinguishes them.

Whether a difference is large enough to act on at all is `scripts/check_test_readout.py` and a different question. This floor governs what a figure looks like, not whether it is real.

## An empty cell is not a zero, and a missing column is not a gap

A row with no plan has no plan. It does not have a plan of zero. It has not missed by 100% either.

The two ways that goes wrong are not the same problem, so the tool separates them.

**No plan column anywhere** is a scope decision. Actuals against last year is a perfectly good report. It gets one line at the top saying so, so a reader is not left hunting for a column that was never there.

**One blank cell in a column that is full everywhere else** is the case that gets misread. It gets a note that counts the rows: *6 of 7 rows carry a plan figure and this one does not.* A blank in a full column reads as a zero, or as a miss, whichever is worse for you. Supply the figure, or move the metric out of the table.

## Two periods of different lengths

July has 31 days and June has 30. Every month-on-month percentage in that pair carries 3% of calendar before anybody sells anything. When the payload declares `days` on both periods and they differ, the tool says so above the table.

Compare per-day figures, or state in the report that you did not. Both are defensible. Silence is not.

## Running it

```bash
python scripts/build_variance_report.py --input period.json
python scripts/build_variance_report.py --metric revenue --actual 312500000 --plan 350000000
python scripts/build_variance_report.py --input period.json --output-format json
python scripts/build_variance_report.py --self-check
```

The payload is one object. `period` and `prior` carry a `label` and optionally `days`. Every row carries a `kpi` id from `data/kpi-metrics.csv`, an `actual`, and whichever of `plan` and `prior` exist. `base` is the count underneath a rate, and `prior_base` the same count for the earlier period.

```json
{
  "period": {"label": "July 2026", "days": 31},
  "prior":  {"label": "June 2026", "days": 30},
  "rows": [
    {"kpi": "revenue", "actual": 312500000, "plan": 350000000, "prior": 288000000},
    {"kpi": "ctr", "actual": 0.9, "plan": 1.2, "base": 184000}
  ]
}
```

Output is a Markdown table, with the notation stated above it and the outstanding items listed below it. Same document. A caveat that travels separately from its table does not travel.

Exit codes, in the toolkit's usual grammar:

| Code | Meaning |
|---|---|
| `0` | Every comparison computed, nothing withheld, no column with a hole in it |
| `2` | The report cannot be built as asked: an unknown metric id, a row with no actual, a figure that is not a figure |
| `3` | Built, and carrying at least one item a person has to settle before it is quoted |

**Exit 3 is not bad news about the business.** An unfavourable month exits 0. Exit 3 means the *table* is not ready: a percentage was withheld, a rate arrived with no denominator, a column has a hole in it. Wire it as a review gate. Never a failure.

Numbers are parsed to `Decimal` through their string form, never through float. These figures get printed rather than compared, and `Decimal(0.1)` is not 0.1.

## What this unit will not do

It does not decide a target, and it does not know whether one was reasonable. Scoring, weighting and cascading are `kpi-scorecards.md` and `scripts/score_kpi.py`, and this file deliberately duplicates none of it: achievement branches, caps and the reason `direction` is stored all live there. Whether a movement is real rather than noise is `scripts/check_test_readout.py`.

It does not know where your numbers came from. That is `measurement-plan.md`. A variance table built on an untracked funnel is a tidy way to present a guess.

It will not write the sentence under the table either. It will tell you which figures cannot carry one.
