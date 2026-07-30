#!/usr/bin/env python3
"""Score a balanced scorecard, and refuse to score one that cannot honestly be scored.

Three things make this different from dividing actual by target.

First, achievement has four branches, not one. A cost KPI is scored target/actual; scoring it the
other way turns an under-spent budget into a failed year. A count of resellers is scored against
six named rungs, so an actual of 4 against a target of 6 is 75% and not 66.7%. A milestone is
scored on a day axis. The branch is a stored decision on the KPI — `direction` and `calc_method` —
because no unit and no name can tell you which one applies: gross margin and cost-to-revenue are
both denominated in per cent and run in opposite directions.

Second, the cap is arithmetic here rather than a discipline. The workbook this was reconstructed
from states a 130% cap on financial KPIs and 100% on the rest, and then does not apply it: one row
runs at 143.20%, and another was hand-typed down to 120% when its own rule said 100%. Applied
correctly, the 2024 card scores 94.47% instead of the 98.79% it reports. The rank happens not to
move; the gap is 4.32 points and the rank is attached to a bonus.

Third, it refuses. A KPI with no actual scored as 100% is the single most expensive bug in the
source file, and a total that silently skips a missing row is worse than no total, because it looks
finished. Every blocking problem is listed and no score is produced until they are gone.

Everything is Decimal. The workbook leaks `0.9500000000000001` and `0.31749999999999995` into cells
a bonus is calculated from, which is float error surfacing in front of the person being scored.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"

# Caps come from the guideline, and the difference between them is the point: a financial KPI can
# be rewarded for overshooting because the overshoot is money that exists, while a non-financial one
# cannot, because 147% of a count is usually a target that was set too low.
FINANCIAL_CAP = Decimal("1.30")
NON_FINANCIAL_CAP = Decimal("1.00")

# The four aspects are an enum, not a table, at company and individual level. People is G: P was
# already taken by Processes, and every real code in the source file reads G1.1, G2.1. A department
# card carries a fifth, `D` for Dept Function, which is where its bottom-up KPIs live — so the enum
# is per level rather than global, and a card that hardcodes four breaks at department level.
ASPECTS = {
    "F": "Finance",
    "C": "Customer",
    "P": "Processes & System",
    "G": "People",
    "D": "Dept Function",
}
ASPECT_ORDER = ("F", "C", "P", "G", "D")
LEVEL_ASPECTS = {
    "company": ("F", "C", "P", "G"),
    "department": ("F", "C", "P", "G", "D"),
    "individual": ("F", "C", "P", "G"),
}

# The rank boundaries, transcribed from the workbook's own nested IF. A3 is the one rung that uses
# <= rather than <, so exactly 90.0% is A3 and 90.0001% is A2. Rewriting all five with < moves the
# 90% case up a grade, which is why the comparison operator is stored beside the threshold instead
# of being assumed.
RANKS = (
    (Decimal("0.70"), "lt", "C", 1),
    (Decimal("0.80"), "lt", "B", 2),
    (Decimal("0.90"), "le", "A3", 3),
    (Decimal("1.05"), "lt", "A2", 4),
    (None, None, "A1", 5),
)

MIN_OVERALL_WEIGHT = Decimal("0.05")
IDEAL_KPI_COUNT = (10, 12)


class Unscoreable(ValueError):
    """A KPI that cannot be scored from what is stored, with the reason attached.

    Separate from a crash because the answer is a list of problems the person filling the card can
    act on, not a traceback on the first one.
    """


def _dec(value: object, field: str) -> Decimal:
    """Parse to Decimal from the string form, never through float.

    `Decimal(0.1)` is 0.1000000000000000055511151231257827, so a JSON number that arrives already
    parsed as a float has to be re-rendered with repr before it is trusted. This is the whole
    defence against the float error visible in the source workbook.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, bool) or value is None:
        raise Unscoreable(f"{field} is not a number: {value!r}")
    try:
        return Decimal(repr(value) if isinstance(value, float) else str(value))
    except (InvalidOperation, ValueError) as exc:
        raise Unscoreable(f"{field} is not a number: {value!r}") from exc


def _days(value: object, field: str) -> Decimal:
    """A date as an ordinal day count, so the date branch is the scale branch on a number line.

    Compared as ordinals rather than as text. ISO dates happen to sort correctly as strings and
    every other format does not, which makes string comparison a bug that passes its first test.
    """
    if isinstance(value, dt.date):
        return Decimal(value.toordinal())
    try:
        return Decimal(dt.date.fromisoformat(str(value)).toordinal())
    except ValueError as exc:
        raise Unscoreable(f"{field} is not an ISO date (YYYY-MM-DD): {value!r}") from exc


def table(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def catalog() -> dict[str, dict[str, str]]:
    """The metric library keyed by id, so a card can name a metric instead of restating its rules.

    `direction`, `calc_method` and `is_financial` decide the score and cannot be derived from
    anything else on the row. Looking them up means a card and the engine cannot disagree about
    which way a metric runs.
    """
    return {row["kpi_id"]: row for row in table("kpi-metrics.csv")}


def achievement(kpi: dict) -> Decimal:
    """Raw achievement, before any cap. Four branches, chosen by `calc_method` and `direction`."""
    name = kpi.get("code") or kpi.get("kpi_id") or "an unnamed KPI"
    if kpi.get("actual") is None:
        raise Unscoreable(f"{name} has no actual, so it has no achievement")
    method = kpi.get("calc_method", "ratio")

    if method == "scale":
        return _scale_achievement(kpi, name)
    if method == "date":
        return _date_achievement(kpi, name)
    if method != "ratio":
        raise Unscoreable(f"{name} has an unknown calc_method {method!r}")

    actual, target = _dec(kpi["actual"], f"{name} actual"), _dec(kpi["target"], f"{name} target")
    if kpi["direction"] == "higher_better":
        if target == 0:
            raise Unscoreable(f"{name} has a target of zero, so achievement is undefined")
        # An actual of zero is a real case — two 2024 customer KPIs report it — and it scores zero
        # rather than raising, because nothing happened and that is a scoreable fact.
        return actual / target
    if kpi["direction"] == "lower_better":
        if actual == 0:
            # Not the mirror of the case above. Spending nothing is almost always a missing number
            # rather than a perfect year, and treating it as 130% pays a bonus for an empty cell.
            raise Unscoreable(
                f"{name} runs lower-is-better and reports an actual of zero — confirm the figure "
                "before scoring, because an empty cell and a perfect result look identical here"
            )
        return target / actual
    raise Unscoreable(f"{name} has an unknown direction {kpi['direction']!r}")


def _rungs(kpi: dict, name: str, convert) -> list[tuple[Decimal, Decimal]]:
    scale = kpi.get("scale")
    if not scale:
        raise Unscoreable(f"{name} is scored on a scale but carries no rungs")
    rungs = [(_dec(step, f"{name} rung achievement"), convert(value, f"{name} rung threshold"))
             for step, value in scale.items()]
    return sorted(rungs, key=lambda pair: pair[0])


def _highest_rung_reached(rungs, actual: Decimal, direction: str, name: str) -> Decimal:
    hit = Decimal(0)
    for step, threshold in rungs:
        reached = actual >= threshold if direction == "higher_better" else actual <= threshold
        if reached:
            hit = step
    return hit


def _scale_achievement(kpi: dict, name: str) -> Decimal:
    """The highest rung the actual has reached.

    Not a ratio that happens to land on the same rungs. With rungs at 1/2/3/4/6/8 against a target
    of 6, an actual of 4 is 75% here and 66.7% as a ratio, and both numbers look reasonable printed
    next to a target. This is the branch a rewrite silently loses.
    """
    rungs = _rungs(kpi, name, _dec)
    return _highest_rung_reached(rungs, _dec(kpi["actual"], f"{name} actual"),
                                 kpi["direction"], name)


def _date_achievement(kpi: dict, name: str) -> Decimal:
    """The scale branch on a day axis. Landing earlier scores higher, so the rungs run later.

    Direction is forced to lower_better on the converted axis whatever the row says, because an
    earlier ordinal is always the better outcome for a milestone and a card that stored
    higher_better here would score a late delivery as a win.
    """
    rungs = _rungs(kpi, name, _days)
    return _highest_rung_reached(rungs, _days(kpi["actual"], f"{name} actual"),
                                 "lower_better", name)


def cap_for(is_financial: bool) -> Decimal:
    return FINANCIAL_CAP if is_financial else NON_FINANCIAL_CAP


def capped(raw: Decimal, is_financial: bool, override: bool = False) -> tuple[Decimal, bool]:
    """Apply the cap, and report whether it bit.

    Both numbers are kept. A card that stores only the capped figure cannot answer "how far over
    were we", which is the question an override request is made of — and the source file's
    hand-capped cell is unauditable for exactly that reason.
    """
    cap = cap_for(is_financial)
    if override:
        return raw, raw > cap
    return min(raw, cap), raw > cap


def rank(total: Decimal) -> tuple[str, int]:
    for threshold, operator, code, order in RANKS:
        if threshold is None:
            return code, order
        if (total <= threshold) if operator == "le" else (total < threshold):
            return code, order
    raise AssertionError("the rank table must end in an open rung")


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"yes", "true", "1"}


def resolve(kpi: dict, library: dict[str, dict[str, str]]) -> dict:
    """Fill a card row's scoring rules from the metric library, without overwriting what it states.

    A card may override — a company can decide its own CAC takes the financial cap — but it has to
    say so on the row. Silence means the library's answer, which is the one with a source attached.
    """
    resolved = dict(kpi)
    row = library.get(kpi.get("kpi_id", ""))
    if row is None and not {"direction", "calc_method"} <= resolved.keys():
        raise Unscoreable(
            f"{kpi.get('code') or kpi.get('kpi_id') or 'a KPI'} names no metric in "
            "kpi-metrics.csv and does not state its own direction and calc_method"
        )
    if row is not None:
        for field in ("direction", "calc_method", "aspect", "indicator_type", "unit"):
            resolved.setdefault(field, row[field])
        if "is_financial" not in resolved:
            resolved["is_financial"] = _truthy(row["is_financial"])
        resolved.setdefault("name_en", row["name_en"])
        resolved.setdefault("name_vi", row["name_vi"])
    resolved["is_financial"] = _truthy(resolved.get("is_financial"))
    # A card row is identified by its own code — F1.1.1 — not by the library id, because two rows on
    # one card can measure the same metric for different products. Falling back to the metric id
    # keeps a hand-written card scoreable without inventing codes for it.
    resolved.setdefault("code", resolved.get("kpi_id") or "unnamed")
    return resolved


def _weight_problems(rows: list[dict], declared: list[dict], level: str) -> list[str]:
    """Everything about weights that the workbook could not check and therefore did not.

    Weights are summed over every row the card declares, not over the rows that happened to score.
    Summing the scoreable ones instead reports a card with one unscoreable KPI as a weighting error
    as well, which sends the reader to fix the wrong thing — the first run of this function on the
    real 2024 card said "weights sum to 90%" when they sum to exactly 100%.
    """
    problems = []
    total = Decimal(0)
    for row in declared:
        try:
            total += _dec(row.get("overall_weight"), "overall_weight")
        except Unscoreable:
            # Reported by the row's own scoring attempt; not restated as a weighting problem.
            continue
    if total != Decimal(1):
        problems.append(
            f"overall weights sum to {total * 100:.2f}%, not 100% — the workbook this replaces "
            "shipped a block totalling 95% and nothing flagged it"
        )
    for row in rows:
        if row["overall_weight"] < MIN_OVERALL_WEIGHT:
            problems.append(
                f"{row['code']} carries {row['overall_weight'] * 100:.2f}% overall weight, under "
                f"the {MIN_OVERALL_WEIGHT * 100:.0f}% floor — this floor is also what keeps a card "
                "to about twenty KPIs without a separate rule"
            )
    seen: dict[str, int] = {}
    for row in rows:
        seen[row["code"]] = seen.get(row["code"], 0) + 1
    for code, count in sorted(seen.items()):
        if count > 1:
            problems.append(f"KPI code {code} appears {count} times — codes have to be unique")
    allowed = LEVEL_ASPECTS.get(level)
    if allowed is None:
        problems.append(f"unknown scorecard level {level!r}")
    else:
        for row in rows:
            if row["aspect"] not in allowed:
                problems.append(
                    f"{row['code']} sits in aspect {row['aspect']!r}, which a {level} card does "
                    f"not carry — allowed: {', '.join(allowed)}"
                )
    return problems


def score(card: dict) -> dict:
    """Score a whole card, or explain why it cannot be scored.

    Aspect totals are SUMPRODUCT(overall_weight, capped_achievement) and the card total is their
    plain sum. Multiplying an aspect total by its proportion again is the classic error: the
    proportion is already inside every overall weight.
    """
    library = catalog()
    level = card.get("level", "company")
    rows, problems, warnings = [], [], []

    for raw_row in card.get("kpis", []):
        try:
            row = resolve(raw_row, library)
            row["overall_weight"] = _dec(raw_row["overall_weight"], "overall_weight")
            raw_achievement = achievement(row)
        except Unscoreable as exc:
            problems.append(str(exc))
            continue
        except KeyError as exc:
            problems.append(f"{raw_row.get('code', 'a KPI')} is missing field {exc.args[0]}")
            continue
        # A BSC code carries its aspect in the first character, and that placement is the card's
        # decision. The library's aspect is only where the metric usually lives — C1.2 below measures
        # published guidelines, which the library files under Processes, but the card put it in
        # Customer on purpose because the guidelines are for distributors. Letting the library win
        # silently moved 5% of the card between two aspects and changed both subtotals while the
        # total stayed correct, which is why this warns instead of resolving quietly.
        prefix = row["code"][0]
        if prefix in ASPECTS and row["aspect"] != prefix:
            if "aspect" in raw_row:
                warnings.append(
                    f"{row['code']} states aspect {raw_row['aspect']} against a code that reads "
                    f"{prefix} — the code is the one people cite, so make them agree"
                )
            else:
                warnings.append(
                    f"{row['code']} sits in aspect {prefix} by its code while the library files "
                    f"{row.get('kpi_id')} under {row['aspect']} — scored as {prefix}, because the "
                    "card decides placement and the library only suggests it"
                )
                row["aspect"] = prefix
        override = bool(raw_row.get("cap_override_by"))
        final, cap_hit = capped(raw_achievement, row["is_financial"], override)
        if cap_hit and override:
            warnings.append(
                f"{row['code']} is over its {cap_for(row['is_financial']) * 100:.0f}% cap at "
                f"{raw_achievement * 100:.2f}% and scored uncapped on the authority of "
                f"{raw_row['cap_override_by']}"
            )
        rows.append({
            "code": row["code"],
            "kpi_id": row.get("kpi_id"),
            "aspect": row["aspect"],
            # A row that names no library metric still has to print as something a reader
            # recognises, so its own label carries the name rather than the report showing None.
            "name_en": row.get("name_en") or row.get("label") or row["code"],
            "direction": row["direction"],
            "calc_method": row["calc_method"],
            "indicator_type": row.get("indicator_type"),
            "is_financial": row["is_financial"],
            "overall_weight": row["overall_weight"],
            "raw_achievement": raw_achievement,
            "capped_achievement": final,
            "cap_applied": cap_hit and not override,
            "cap_overridden": cap_hit and override,
            "contribution": final * row["overall_weight"],
        })

    declared = card.get("kpis", [])
    problems.extend(_weight_problems(rows, declared, level) if rows else [])
    if not rows:
        problems.append("the card carries no scoreable KPI")

    count = len(rows)
    if rows and not IDEAL_KPI_COUNT[0] <= count <= IDEAL_KPI_COUNT[1]:
        warnings.append(
            f"{count} KPIs against the guideline's ideal {IDEAL_KPI_COUNT[0]}–{IDEAL_KPI_COUNT[1]} "
            "— a warning, not a block, because a real card sometimes has a reason"
        )
    for aspect in sorted({row["aspect"] for row in rows}):
        kinds = {row["indicator_type"] for row in rows if row["aspect"] == aspect}
        if kinds == {"lagging"}:
            warnings.append(
                f"aspect {aspect} carries only lagging KPIs — it can be reported but not steered, "
                "because every number in it arrives after the decisions that moved it"
            )

    report = {
        "level": level,
        "owner": card.get("owner", "UNKNOWN"),
        "fiscal_year": card.get("fiscal_year", "UNKNOWN"),
        "scoreable": not problems,
        "blocking_problems": problems,
        "warnings": warnings,
        "kpis": rows,
    }
    if problems:
        # No total. A card with a missing actual used to score 100% on that row in the workbook,
        # and a partial total presented as a total is the failure this whole script exists to stop.
        report["aspects"] = {}
        report["total_score"] = None
        report["rank"] = None
        return report

    aspects = {}
    for aspect in ASPECT_ORDER:
        members = [row for row in rows if row["aspect"] == aspect]
        if not members:
            continue
        aspects[aspect] = {
            "name": ASPECTS[aspect],
            "weight": sum((row["overall_weight"] for row in members), Decimal(0)),
            "score": sum((row["contribution"] for row in members), Decimal(0)),
        }
    total = sum((entry["score"] for entry in aspects.values()), Decimal(0))
    code, order = rank(total)
    report["aspects"] = aspects
    report["total_score"] = total
    report["rank"] = code
    report["rank_order"] = order
    return report


def _pct(value: Decimal | None) -> str:
    return "—" if value is None else f"{value * 100:.2f}%"


def as_report(result: dict) -> str:
    lines = [
        f"# Scorecard — {result['owner']} · {result['level']} · {result['fiscal_year']}",
        "",
    ]
    if result["blocking_problems"]:
        lines += ["## Not scored", "",
                  "Every line below has to be resolved before this card has a total.", ""]
        lines += [f"- {problem}" for problem in result["blocking_problems"]] + [""]
    else:
        lines += [f"**Total {_pct(result['total_score'])} · rank {result['rank']}**", "", "| Aspect | Weight | Score |",
                  "|---|---|---|"]
        for code, entry in result["aspects"].items():
            lines.append(f"| {code} {entry['name']} | {_pct(entry['weight'])} | {_pct(entry['score'])} |")
        lines.append("")
    if result["warnings"]:
        lines += ["## Warnings", ""] + [f"- {warning}" for warning in result["warnings"]] + [""]
    if result["kpis"]:
        lines += ["## KPIs", "",
                  "| Code | KPI | Weight | Raw | Capped | Cap |", "|---|---|---|---|---|---|"]
        for row in result["kpis"]:
            if row["cap_overridden"]:
                cap = "overridden"
            elif row["cap_applied"]:
                cap = f"applied at {_pct(cap_for(row['is_financial']))}"
            else:
                cap = "—"
            lines.append(
                f"| {row['code']} | {row['name_en'] or row['kpi_id']} | "
                f"{_pct(row['overall_weight'])} | {_pct(row['raw_achievement'])} | "
                f"{_pct(row['capped_achievement'])} | {cap} |"
            )
        lines.append("")
    return "\n".join(lines)


def _jsonable(value):
    if isinstance(value, Decimal):
        return float(round(value, 6))
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score a balanced scorecard, or list what stops it being scoreable.")
    parser.add_argument("--input", required=True, help="scorecard JSON")
    parser.add_argument("--format", choices=("report", "json"), default="report")
    parser.add_argument("--output")
    args = parser.parse_args()

    card = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = score(card)
    if args.format == "json":
        emit_json(_jsonable(result), args.output)
    else:
        emit(as_report(result), args.output)
    # A card that cannot be scored exits non-zero, so a pipeline cannot carry an unscored card
    # forward as though it had passed.
    sys.exit(0 if result["scoreable"] else 1)


if __name__ == "__main__":
    main()
