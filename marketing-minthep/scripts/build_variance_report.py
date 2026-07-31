#!/usr/bin/env python3
"""Turn actuals, plan and prior period into a table somebody can paste into a report.

Scoring a period and presenting a period are two different jobs, and the second one is where the
month's work gets misread. `score_kpi.py` answers "did we hit it". This answers "what does the
line look like on the page", which is the question a report is made of, and it is the one that
goes wrong quietly:

  A minus sign is not bad news. CAC fell 18% and revenue fell 18%; one of those is a good month.
  Which one depends on the metric's `direction`, which is a stored column on every row of
  data/kpi-metrics.csv precisely because no unit and no name tells you which way a metric runs.

  A percentage point is not a per cent. Conversion went 2.5% to 3.1%. That is +0.6 points and
  +24% of plan, and a report that prints "+0.6%" has understated the month by a factor of forty.
  Both figures are here, labelled, because either one alone can be read as the other.

  A per cent of a small base is a true number that misleads. Three sign-ups against a plan of two
  is +50%, and it is one person. Below a stated floor this prints the two raw numbers and says why
  rather than printing the percentage.

  A per cent of a date is not a number at all. Date metrics get a variance in days and no
  relative figure, because 4% later than a deadline means nothing.

  An empty plan cell is not a plan of zero. A row with no plan reports that it has no plan.

Where the notation itself comes from, and where it does not: ISO 24896 'Notation for business
reporting' was published on 2026-06-11, and IBCS Standards 2.0 was released aligned with it the
same day. The rule text is not readable from the free web copy - it sits in a viewer with print
and download disabled behind an obfuscated file path - so this tool does not claim to implement
the standard's abbreviations. It prints `actual`, `plan` and `prior`, and it prints them the same
way every time. Consistency is the property that makes a report readable; the specific labels are
a convention, and yours can differ as long as it never differs between two reports.

Exit codes follow the rest of the toolkit:
    0  every comparison computed, nothing suppressed
    2  the report cannot be built as asked - an unknown metric, a missing actual, a number that
       is not a number
    3  built, and carrying at least one figure a person has to settle

Usage:
    python build_variance_report.py --input period.json
    python build_variance_report.py --metric revenue --actual 312500000 --plan 350000000 \\
        --prior 288000000
    python build_variance_report.py --input period.json --output-format json
    python build_variance_report.py --self-check
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import decimal
import json
import pathlib
import sys
from decimal import Decimal

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"

# The base below which a relative variance is printed as raw numbers instead. This is not a
# statistical threshold and it is not anybody's published figure - it is a presentation floor, in
# the same class as the ninety days in check_channel_spec.py. Thirty is the default because a
# tenth of a percentage point on a base of thirty is already smaller than one observation, so the
# percentage is carrying precision the underlying count cannot support. Override it per report
# with --small-base, and the figure used is printed in the output so the reader can see the bet.
SMALL_BASE = Decimal("30")

HIGHER_BETTER = "higher_better"
LOWER_BETTER = "lower_better"

RATE_UNITS = ("%",)
DATE_UNITS = ("Date",)

# Metrics whose unit is a bare number but whose zero is a convention rather than an absence. NPS
# is a net score on a scale somebody chose: 41 to 44 is three points, and "+7.3%" is a percentage
# of a decision, not of a quantity. Counts in the same `No` unit - resellers signed, complaints
# received - do have a real zero, so a percentage of them means something and they are not here.
# This lives in the script rather than as a column on kpi-metrics.csv because it is a fact about
# how a figure may be presented, which is this file's subject, and no other tool needs to ask.
INDEX_METRICS = frozenset({"nps"})

FAVOURABLE = "favourable"
UNFAVOURABLE = "unfavourable"
ON_PLAN = "on plan"
NOT_COMPARABLE = "not comparable"


class Unreportable(ValueError):
    """The report cannot be built from what was supplied, with the reason attached.

    Separate from a crash because the useful answer is the list of rows a person can fix, not a
    traceback on whichever one happened to be read first.
    """


def _dec(value: object, field: str) -> Decimal:
    """Parse to Decimal through the string form, never through float.

    `Decimal(0.1)` is 0.1000000000000000055511151231257827. A JSON number arrives already parsed
    as a float, so it is re-rendered with repr before it is trusted. Same defence as score_kpi.py,
    and it matters more here: these numbers get printed rather than compared.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool) or value is None:
        raise Unreportable(f"{field} is not a number: {value!r}")
    try:
        return Decimal(repr(value) if isinstance(value, float) else str(value))
    except (decimal.InvalidOperation, ValueError) as exc:
        raise Unreportable(f"{field} is not a number: {value!r}") from exc


def catalog() -> dict[str, dict[str, str]]:
    """The metric library keyed by id.

    Read from the same file score_kpi.py reads, so a variance table and a scorecard cannot
    disagree about which way a metric runs. `direction` is the whole reason this lookup exists.
    """
    with (DATA / "kpi-metrics.csv").open(encoding="utf-8-sig", newline="") as handle:
        return {row["kpi_id"]: row for row in csv.DictReader(handle)}


def resolve(kpi: str, library: dict[str, dict[str, str]]) -> dict[str, str]:
    """Look a metric up, and on a miss name the ids it could have meant.

    A typo here is silent otherwise: the row drops out of the table and the total under it still
    adds up, which is the failure mode that makes a wrong report look finished.
    """
    if kpi in library:
        return library[kpi]
    near = [key for key in library if kpi.lower() in key or key in kpi.lower()]
    hint = f" Did you mean: {', '.join(sorted(near))}?" if near else ""
    raise Unreportable(f"no metric with id {kpi!r} in data/kpi-metrics.csv.{hint}")


def _number(value: Decimal) -> str:
    """A figure with thousands separators and no trailing decimal noise."""
    quantised = value.quantize(Decimal("0.01")) if value != value.to_integral_value() else value
    text = f"{quantised.normalize():,f}" if quantised == quantised.to_integral_value() else f"{quantised:,f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def _signed(value: Decimal, suffix: str = "") -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{_number(value)}{suffix}"


def _percent(value: Decimal) -> str:
    return f"{'+' if value > 0 else ''}{value.quantize(Decimal('0.1'))}%"


def is_rate(row: dict[str, str]) -> bool:
    return row["unit"] in RATE_UNITS


def is_date(row: dict[str, str]) -> bool:
    return row["unit"] in DATE_UNITS


def is_index(row: dict[str, str]) -> bool:
    return row["kpi_id"] in INDEX_METRICS


def favourability(delta: Decimal, direction: str) -> str:
    """Whether a movement is good news, from the stored direction and nothing else.

    Guessing from the metric's name is how a cost reduction gets reported as a shortfall. Gross
    margin and cost-to-revenue are both denominated in per cent and run in opposite directions.
    """
    if delta == 0:
        return ON_PLAN
    if direction == HIGHER_BETTER:
        return FAVOURABLE if delta > 0 else UNFAVOURABLE
    if direction == LOWER_BETTER:
        return FAVOURABLE if delta < 0 else UNFAVOURABLE
    raise Unreportable(f"unknown direction {direction!r} - expected {HIGHER_BETTER} or {LOWER_BETTER}")


def _ordinal(value: object, field: str) -> Decimal:
    if isinstance(value, dt.date):
        return Decimal(value.toordinal())
    try:
        return Decimal(dt.date.fromisoformat(str(value)).toordinal())
    except ValueError as exc:
        raise Unreportable(f"{field} is not an ISO date (YYYY-MM-DD): {value!r}") from exc


def compare(metric: dict[str, str], actual: object, against: object, label: str,
            base: object = None, small_base: Decimal = SMALL_BASE) -> dict:
    """One comparison: the difference, whether it is good news, and what is being withheld.

    Returns `absolute`, `relative` and `notes`. A missing `relative` is never a zero - it means
    the figure was not computable or was withheld, and the note says which.

    A missing comparison figure comes back with no note attached, on purpose. Whether it deserves
    a sentence depends on the other rows, and only build() can see those: a report with no prior
    column anywhere is a report about one period, while a prior column that is full everywhere
    except here has a hole in it. The first is a scope decision and the second needs a person.
    """
    if against is None or against == "":
        return {"label": label, "status": "no-figure", "absolute": None, "relative": None,
                "verdict": NOT_COMPARABLE, "kind": "none", "base_known": True, "notes": []}

    notes: list[str] = []
    direction = metric["direction"]

    if is_date(metric):
        delta = _ordinal(actual, "actual") - _ordinal(against, label)
        return {"label": label, "status": "computed", "absolute": delta, "absolute_unit": "days",
                "relative": None, "verdict": favourability(delta, direction), "kind": "date",
                "base_known": True, "notes": []}

    actual_value = _dec(actual, "actual")
    base_value = _dec(against, label)
    delta = actual_value - base_value

    if is_index(metric):
        return {"label": label, "status": "computed", "absolute": delta, "absolute_unit": "pts",
                "relative": None, "verdict": favourability(delta, metric["direction"]),
                "kind": "index", "base_known": True, "notes": []}

    rate = is_rate(metric)

    result = {"label": label, "status": "computed", "absolute": delta,
              "absolute_unit": "pp" if rate else "", "relative": None,
              "verdict": favourability(delta, direction), "kind": "rate" if rate else "quantity",
              "base_known": True, "notes": notes}

    if rate and Decimal(0) < actual_value <= Decimal(1) and Decimal(0) < base_value <= Decimal(1):
        notes.append("Both figures sit at or below 1 on a metric measured in per cent. If these "
                     "are 2.5% and 3.1%, write 2.5 and 3.1. If they really are 0.025%, ignore "
                     "this line - it cannot tell the difference and neither can a reader.")

    if base_value == 0:
        notes.append(f"{label} is zero, so no relative variance exists. Not 0%, and not an "
                     f"infinite improvement either.")
        return result

    # What counts as the base depends on what kind of metric this is, and getting it wrong is how
    # a floor stops protecting anybody. For a quantity the comparison figure IS the base: a plan
    # of 2 resellers is a base of 2. For a rate it is not - a plan CTR of 1.2 is not a base of
    # 1.2, the base is the impressions underneath it, and that number only arrives if the caller
    # supplies it. So a rate with no `base` gets its percentage and gets named for it upstairs,
    # rather than being silently measured against a floor it was never on.
    if base is not None and base != "":
        reference = _dec(base, "base")
    elif rate:
        result["base_known"] = False
        reference = None
    else:
        reference = abs(base_value)

    if reference is not None and reference < small_base:
        notes.append(f"Base of {_number(reference)} is under the {_number(small_base)} floor, so "
                     f"the two raw figures stand instead of a percentage.")
        return result

    result["relative"] = (delta / base_value * 100)
    return result


def build_row(entry: dict, library: dict[str, dict[str, str]],
              small_base: Decimal = SMALL_BASE) -> dict:
    """One metric across actual, plan and prior."""
    kpi = entry.get("kpi") or entry.get("metric")
    if not kpi:
        raise Unreportable("a row has no `kpi` id, so its direction and unit cannot be looked up")
    metric = resolve(str(kpi), library)
    if entry.get("actual") in (None, ""):
        raise Unreportable(f"{kpi} has no actual. A row with no actual is not a variance, it is a gap")

    comparisons = [
        compare(metric, entry["actual"], entry.get("plan"), "plan",
                base=entry.get("base"), small_base=small_base),
        compare(metric, entry["actual"], entry.get("prior"), "prior",
                base=entry.get("prior_base", entry.get("base")), small_base=small_base),
    ]
    return {
        "kpi": kpi,
        "name": metric["name_en"],
        "name_vi": metric["name_vi"],
        "unit": metric["unit"],
        "direction": metric["direction"],
        "actual": entry["actual"] if is_date(metric) else _dec(entry["actual"], "actual"),
        "plan": entry.get("plan"),
        "prior": entry.get("prior"),
        "comparisons": comparisons,
        "trap": metric["trap"],
    }


def build(payload: dict, small_base: Decimal = SMALL_BASE) -> dict:
    """The whole report, plus the state a reader has to settle before quoting it."""
    library = catalog()
    rows = payload.get("rows") or []
    if not rows:
        raise Unreportable("no rows supplied - a report with no metrics on it is not a report")

    built = [build_row(entry, library, small_base=small_base) for entry in rows]
    notes: list[str] = []
    scope: list[str] = []

    # A column census, because an absent column and a hole in a column are different problems and
    # the second one is the one that gets misread. Nobody misreads a report that has no prior
    # period on it. Everybody reads the one empty cell in an otherwise full column as a zero.
    for index, label in enumerate(("plan", "prior")):
        filled = [row for row in built if row["comparisons"][index]["status"] != "no-figure"]
        gaps = [row for row in built if row["comparisons"][index]["status"] == "no-figure"]
        if not gaps:
            continue
        if not filled:
            scope.append(f"No {label} figure on any row. That makes this a report without a "
                         f"{label} column rather than a report with an empty one - fine, and worth "
                         f"one line at the top so a reader is not left looking for it.")
            continue
        for row in gaps:
            row["comparisons"][index]["notes"].append(
                f"{len(filled)} of {len(built)} rows carry a {label} figure and this one does "
                f"not. A blank cell in a column that is otherwise full gets read as a zero, or "
                f"as a miss. Supply the {label}, or move this metric out of the table.")

    # Notation stated once, at the top, instead of once per row. A convention repeated on every
    # line stops being read by the third one, and these are conventions rather than open questions:
    # they tell a reader how to read the table, they do not ask anybody to go and settle a figure.
    conventions: list[str] = []
    kinds = {kind: sorted({row["name"] for row in built for item in row["comparisons"]
                           if item.get("kind") == kind})
             for kind in ("rate", "date", "index")}
    if kinds["rate"]:
        conventions.append(
            f"Measured in per cent: {', '.join(kinds['rate'])}. Their movement is in percentage "
            f"points (pp), and the percentage printed beside it is that movement as a share of the "
            f"figure compared against. 2.5% to 3.1% is +0.6 pp and +24%; both are true and they "
            f"are not the same statement.")
    if kinds["date"]:
        conventions.append(
            f"Measured as a date: {', '.join(kinds['date'])}. A date carries a variance in days "
            f"and no percentage, because 4% later than a deadline is not a quantity.")
    if kinds["index"]:
        conventions.append(
            f"An index rather than a quantity: {', '.join(kinds['index'])}. The zero on that scale "
            f"is a convention, so it moves in points and carries no percentage. 41 to 44 is three "
            f"points up; a percentage there would be a share of a decision somebody made.")
    if suppressed_by_floor := [f"{row['name']} vs {item['label']}" for row in built
                               for item in row["comparisons"]
                               if item["status"] == "computed" and item["relative"] is None
                               and item["kind"] == "quantity" and item["base_known"]]:
        conventions.append(
            f"Percentage withheld, raw figures standing instead: {', '.join(suppressed_by_floor)}. "
            f"The base there is under {_number(small_base)}, which is this report's presentation "
            f"floor and not a significance test. For whether a difference is readable at all, run "
            f"check_test_readout.py.")

    unbased = sorted({row["name"] for row in built for item in row["comparisons"]
                      if not item["base_known"]})
    if unbased:
        notes.append(
            f"Rates with no denominator supplied: {', '.join(unbased)}. A three-point lift on 40 "
            f"sessions and on 40,000 sessions print identically above, so the floor could not be "
            f"applied to either. Add `base` with the count underneath the rate, or say in the "
            f"report that these percentages are unweighted.")

    period = payload.get("period") or {}
    prior = payload.get("prior") or {}
    days_now, days_then = period.get("days"), prior.get("days")
    if days_now and days_then and int(days_now) != int(days_then):
        notes.append(
            f"The two periods are {days_now} and {days_then} days long. That difference is "
            f"{abs(int(days_now) - int(days_then)) * 100 // int(days_then)}% of the shorter one "
            f"before anybody sells anything, so every prior-period percentage below carries it. "
            f"Compare per-day figures, or say in the report that you did not.")

    open_questions = sum(len(item["notes"]) for row in built for item in row["comparisons"]) + len(notes)
    suppressed = sum(1 for row in built for item in row["comparisons"]
                     if item["status"] == "computed" and item["relative"] is None
                     and item["kind"] in ("quantity", "rate"))
    return {
        "period": period.get("label") or payload.get("period_label") or "the period",
        "prior_label": prior.get("label") or "prior period",
        "small_base": small_base,
        "rows": built,
        "notes": notes,
        "conventions": conventions,
        "scope": scope,
        "counts": {"rows": len(built), "suppressed": suppressed, "open_questions": open_questions},
    }


def _cell(item: dict) -> str:
    if item["status"] == "no-figure":
        return "no figure"
    unit = item.get("absolute_unit") or ""
    absolute = _signed(item["absolute"], f" {unit}".rstrip() if unit else "")
    if item["relative"] is None:
        return f"{absolute} ({item['verdict']})"
    return f"{absolute} / {_percent(item['relative'])} ({item['verdict']})"


def as_markdown(report: dict) -> str:
    """A table to paste into the report, and the caveats under it rather than out of sight."""
    lines = [f"## {report['period']}", ""]
    for line in report.get("scope", []):
        lines.append(f"{line}")
        lines.append("")
    lines += [f"| Metric | Unit | Actual | Plan | vs plan | {report['prior_label']} "
              f"| vs prior |", "|---|---|---|---|---|---|---|"]
    for row in report["rows"]:
        plan = row["plan"] if row["plan"] not in (None, "") else "-"
        prior = row["prior"] if row["prior"] not in (None, "") else "-"
        actual = row["actual"] if isinstance(row["actual"], str) else _number(row["actual"])
        plan = plan if isinstance(plan, str) else _number(_dec(plan, "plan"))
        prior = prior if isinstance(prior, str) else _number(_dec(prior, "prior"))
        lines.append(f"| {row['name']} | {row['unit']} | {actual} | {plan} | "
                     f"{_cell(row['comparisons'][0])} | {prior} | {_cell(row['comparisons'][1])} |")

    if report.get("conventions"):
        lines += ["", "### How to read the columns", ""]
        for line in report["conventions"]:
            lines.append(f"- {line}")

    lines += ["", "### Before this table is quoted", ""]
    for note in report["notes"]:
        lines.append(f"- {note}")
    for row in report["rows"]:
        for item in row["comparisons"]:
            for note in item["notes"]:
                lines.append(f"- **{row['name']} vs {item['label']}** - {note}")
    if len(lines) and lines[-1] == "":
        lines.append("- Nothing outstanding. Every variance above is computed from both figures, "
                     "and every column is filled on every row.")
    counts = report["counts"]
    lines += ["", f"Rows {counts['rows']}, relative variances withheld {counts['suppressed']}, "
                  f"open questions {counts['open_questions']}. Small-base floor "
                  f"{_number(report['small_base'])}."]
    return "\n".join(lines)


def _jsonable(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def exit_code(report: dict) -> int:
    return 3 if report["counts"]["open_questions"] else 0


def self_check() -> str:
    """Cases that failed at least once while this was being written, kept as the record.

    Every one of them is a way a variance table can be wrong while looking finished.
    """
    library = catalog()
    results: list[tuple[bool, str]] = []

    def case(condition: bool, description: str) -> None:
        results.append((bool(condition), description))

    # Direction, on the pair that exists in the library to make this exact point.
    margin = library["gross_margin"]
    cost = library["cost_to_revenue"] if "cost_to_revenue" in library else None
    case(favourability(Decimal("-2"), margin["direction"]) == UNFAVOURABLE,
         "margin down two points is unfavourable")
    if cost:
        case(favourability(Decimal("-2"), cost["direction"]) == FAVOURABLE,
             "cost-to-revenue down two points is favourable, on the same unit as margin")

    # A fall in a lower-is-better metric is good news, which is the sign trap in one line.
    cac = next((row for row in library.values() if row["direction"] == LOWER_BETTER
                and row["unit"] in ("$", "No")), None)
    if cac:
        report = compare(cac, 74000, 91000, "prior")
        case(report["verdict"] == FAVOURABLE and report["absolute"] < 0,
             f"{cac['kpi_id']} falling is reported as favourable with a negative absolute")

    # Percentage points against per cent, on a rate metric.
    rate = compare(margin, "57", "56", "plan")
    case(rate["absolute"] == Decimal("1") and rate["absolute_unit"] == "pp",
         "a rate variance is measured in percentage points")
    case(rate["relative"] is not None and rate["relative"].quantize(Decimal("0.1")) == Decimal("1.8"),
         "and carries the relative figure separately: one point on 56 is 1.8%")

    # A missing plan is not a plan of zero.
    empty = compare(margin, "57", None, "plan")
    case(empty["absolute"] is None and empty["verdict"] == NOT_COMPARABLE,
         "a missing plan produces no variance rather than a 100% shortfall")

    # A zero base has no relative variance in either direction.
    zero = compare(library["revenue"], "1200000", "0", "plan")
    case(zero["relative"] is None and any("zero" in note for note in zero["notes"]),
         "a plan of zero yields no percentage, not an infinite one")

    # The small-base floor withholds the percentage and keeps the absolute.
    small = compare(library["revenue"], "3", "2", "plan", base="2")
    case(small["relative"] is None and small["absolute"] == Decimal("1"),
         "three against a plan of two prints the raw figures, not +50%")
    big = compare(library["revenue"], "330", "300", "plan", base="300")
    case(big["relative"] is not None and big["relative"].quantize(Decimal("0.1")) == Decimal("10.0"),
         "and a base over the floor does carry its percentage")

    # An index moves in points. This is the figure most likely to appear in a real board pack
    # anyway, which is why it is worth a case: nobody notices a per cent of NPS is meaningless.
    nps = compare(library["nps"], 44, 41, "prior")
    case(nps["absolute"] == Decimal("3") and nps["relative"] is None
         and nps["absolute_unit"] == "pts",
         "NPS moves three points and carries no percentage")
    case(compare(library["resellers_acquired"], 44, 41, "prior")["relative"] is not None,
         "and a count in the same unit does carry one, because its zero is real")

    # A date variance is days, with no percentage attached.
    date_metric = next((row for row in library.values() if row["unit"] == "Date"), None)
    if date_metric:
        late = compare(date_metric, "2026-08-05", "2026-08-01", "plan")
        case(late["absolute"] == Decimal("4") and late["relative"] is None,
             "a date lands four days out with no percentage of a date")

    # Float never reaches the arithmetic.
    case(_dec(0.1, "x") == Decimal("0.1"), "0.1 as a float parses to exactly 0.1")

    # An unknown id names its near misses instead of dropping the row.
    try:
        resolve("revenu", library)
        case(False, "an unknown metric id raises")
    except Unreportable as exc:
        case("revenue" in str(exc), "an unknown metric id names the row it could have meant")

    # A row with no actual is a gap, not a variance.
    case(_raises(lambda: build_row({"kpi": "revenue", "plan": 100}, library)),
         "a row with no actual refuses to build")

    # The full report exits 3 while anything is withheld, and 0 when nothing is.
    withheld = build({"period": {"label": "test"},
                      "rows": [{"kpi": "revenue", "actual": 3, "plan": 2, "base": 2}]})
    case(exit_code(withheld) == 3, "a withheld percentage makes the report exit 3")
    clean = build({"period": {"label": "test"},
                   "rows": [{"kpi": "revenue", "actual": 330, "plan": 300}]})
    case(exit_code(clean) == 0, "a report with nothing withheld exits 0")
    case(clean["scope"] and "prior" in clean["scope"][0],
         "and a report with no prior column says so in one line without calling it a question")

    # A column that is full except for one row is the case that gets misread.
    holed = build({"period": {"label": "test"}, "rows": [
        {"kpi": "revenue", "actual": 330, "plan": 300, "prior": 310},
        {"kpi": "nps", "actual": 44, "prior": 41},
    ]})
    case(not holed["scope"] and exit_code(holed) == 3,
         "one row missing a plan the others have is an open question, not a scope line")
    case(any("1 of 2 rows" in note for row in holed["rows"]
             for item in row["comparisons"] for note in item["notes"]),
         "and the note counts the rows that do carry the figure")

    # Period length is an artefact the reader has to be told about.
    uneven = build({"period": {"label": "Jul", "days": 31}, "prior": {"label": "Jun", "days": 30},
                    "rows": [{"kpi": "revenue", "actual": 330, "plan": 300, "prior": 300}]})
    case(any("31 and 30 days" in note for note in uneven["notes"]),
         "two periods of different lengths are declared before the percentages are read")

    passed = sum(1 for ok, _ in results if ok)
    lines = [f"{'ok  ' if ok else 'FAIL'} {text}" for ok, text in results]
    lines.append("")
    lines.append(f"verdict {'passed' if passed == len(results) else 'failed'} - "
                 f"{passed}/{len(results)} cases")
    return "\n".join(lines)


def _raises(thunk) -> bool:
    try:
        thunk()
    except Unreportable:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--input", help="JSON file: {period, prior, rows:[{kpi, actual, plan, prior}]}")
    parser.add_argument("--metric", help="one metric id from data/kpi-metrics.csv")
    parser.add_argument("--actual")
    parser.add_argument("--plan")
    parser.add_argument("--prior")
    parser.add_argument("--base", help="the count behind a rate, for the small-base floor")
    parser.add_argument("--small-base", default=str(SMALL_BASE),
                        help=f"below this base a percentage is withheld (default {SMALL_BASE})")
    parser.add_argument("--output-format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        text = self_check()
        print(text)
        return 0 if "verdict passed" in text else 2

    try:
        small_base = _dec(args.small_base, "--small-base")
        if args.input:
            payload = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))
        elif args.metric:
            payload = {"rows": [{"kpi": args.metric, "actual": args.actual, "plan": args.plan,
                                 "prior": args.prior, "base": args.base}]}
        else:
            parser.error("supply --input FILE or --metric with --actual")
            return 2
        report = build(payload, small_base=small_base)
    except Unreportable as exc:
        print(f"cannot build the report: {exc}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read the input: {exc}", file=sys.stderr)
        return 2

    if args.output_format == "json":
        print(json.dumps(_jsonable(report), ensure_ascii=False, indent=2))
    else:
        print(as_markdown(report))
    return exit_code(report)


if __name__ == "__main__":
    sys.exit(main())
