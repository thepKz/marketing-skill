#!/usr/bin/env python3
"""Multiply a market-sizing chain out loud, and refuse to total it when a term has no evidence behind it.

`market-assessment.md` asked for "bottom-up low/base/high sizing with visible arithmetic" and
`research-protocol.md` said "show arithmetic for bottom-up sizing". Neither shipped a way to do it, so
the arithmetic stayed in somebody's head and arrived as one confident number on a slide. That number
is the most quoted and least checkable object in a marketing plan.

`market-data-collection.md` supplies the chain and the two disciplines this enforces: every term comes
from a named measurement family, and every term carries a range rather than a point. What this script
adds is the part a human will not do by hand.

Three of its checks are worth naming, because they catch defects that look like diligence.

**A survey range narrower than its own sampling error.** Somebody reads 41 percent off a panel report
of 300 respondents and enters 40 to 42 as the range. The 95 percent half-width at n=300 is 5.7 points,
so their band is a quarter of the uncertainty in the number they copied. The tight range reads as
precision and is the opposite. This is the gate that fires most often on real work.

**Platform self-report anywhere in the chain.** Ad-audience sizes come out of a campaign planner and
count addressable accounts, including duplicates and dormant ones. They are the platform's commercial
estimate of its own inventory. They can size an ad buy and they cannot size a market, so they are
refused outright rather than downgraded.

**Where the uncertainty actually lives.** The chain multiplies, so the spreads multiply too, and each
term's share of the total spread is its log ratio over the total log ratio. That number decides where
the next research hour goes. It is usually not the term the team has been arguing about.

`--threshold` answers the question `research-protocol.md` asks and never operationalises: have we
researched enough? Enough is not a source count and it is not a feeling. It is whether the range still
contains the number that flips the decision. If it does not, stop - no further precision can change the
answer. If it does, the script names the terms that would settle it on their own, by collapsing each to
its centre and re-multiplying, so the next research hour goes somewhere that can move an outcome.

The centre is the geometric mean of the low and high products, not their average. In a multiplicative
chain the arithmetic midpoint sits above the middle - the product is symmetric in log space, not in
linear space - and using the average is how a "base case" quietly becomes an optimistic case.

Currency-agnostic and unit-agnostic on purpose. It never converts and never assumes VND.

    python scripts/size_market.py --check chain.csv
    python scripts/size_market.py --check chain.csv --threshold 2000000000
    python scripts/size_market.py --check chain.csv --as-of 2026-07-31 --json
    python scripts/size_market.py --template chain.csv
    python scripts/size_market.py --families
    python scripts/size_market.py --margin 300
    python scripts/size_market.py --self-check

Exit codes are 0 clean, 1 usage error, 2 a gate failed, 3 computable but unsettled.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

COLUMNS = ("term", "role", "low", "high", "unit", "family", "n", "source_url", "retrieved",
           "what_it_measures")

# The four families and what each is systematically wrong about. This restates the table in
# `market-data-collection.md` rather than inventing a taxonomy, so a family is edited in the prose and
# the tokens here follow.
FAMILIES = {
    "official": "Counts the economy through census, survey and administrative records. Systematically "
                "wrong about your product: it has no brand, intent or channel variables.",
    "panel": "Recruits people, then measures them repeatedly. Systematically wrong about who it "
             "recruited - every online panel skews urban, younger, higher-income, more connected.",
    "trace": "Records what happened: receipts, scans, listings, search, clicks. Systematically wrong "
             "about what happened somewhere it cannot see.",
    "platform": "Restates a platform's own commercial estimate of its own inventory. Systematically "
                "wrong about its own size, in the direction that sells advertising.",
}

# The documented chain. `people` through `price` produce the category value; `reach` cuts it to what
# your distribution can actually address. `adjust` exists for a term a specific category needs - a
# wastage rate, a share of occasions eaten out - and is not required.
ROLES = {
    "people": "Households or people in scope, with province and age band stated",
    "incidence": "Share of them with the need, from a survey or panel carrying its n",
    "frequency": "Purchases per year",
    "price": "Realistic price paid, from an observed ladder rather than a list price",
    "reach": "Share your distribution and media footprint can actually address",
    "adjust": "A category-specific multiplier, labelled",
}
CATEGORY_ROLES = ("people", "incidence", "frequency", "price")

# 1.959964 is the two-sided 95 percent normal quantile. p=0.5 is used for the half-width because it is
# the worst case for a proportion and because a panel report rarely publishes the per-question base
# anyway. This is the same arithmetic as the sample-size table in `market-data-collection.md`.
Z95 = 1.959964

# A URL read more than a year ago is a hypothesis, not a citation. Named in the same words in
# `market-data-collection.md`, kept as one number here.
STALE_AFTER_DAYS = 365

# Below this, a five-term chain's ranges are decorative. Compounding a 1.15 ratio across five terms is
# already a 2x spread, so a chain reporting less than that has either extraordinary evidence or
# invented bands, and it is almost never the first.
MIN_GEOMETRIC_TERM_RATIO = 1.15

# Three significant figures on the totals. Not a style choice: the fourth digit of a five-term product
# of ranges is noise, and printing it invites somebody to quote it.
TOTAL_SIGNIFICANT_FIGURES = 3


def sampling_half_width(n: int) -> float:
    """95 percent half-width of a proportion at the worst case, as a share rather than points."""
    if n <= 0:
        raise ValueError("n must be positive")
    return Z95 * math.sqrt(0.25 / n)


def minimum_detectable_gap(n: int) -> float:
    """Two proportions from one survey both carry error, so a defensible gap is wider than one margin.

    The factor is sqrt(2) for two independent proportions of equal n, which is where the "roughly 1.4x"
    in the reference comes from.
    """
    return sampling_half_width(n) * math.sqrt(2)


def significant(value: float, figures: int = TOTAL_SIGNIFICANT_FIGURES) -> float:
    if value == 0:
        return 0.0
    exponent = math.floor(math.log10(abs(value)))
    return round(value, -(exponent - figures + 1))


def group(value: float) -> str:
    """Digit grouping without a currency name, because a helper that guesses the currency will one day
    guess wrong by a factor of twenty-five thousand."""
    if value >= 1000:
        return f"{round(value):,}"
    if value >= 1:
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return f"{value:.6g}"


def read_chain(path: str | Path) -> list[dict]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("the chain file has no rows")
    missing = [column for column in COLUMNS if column not in rows[0]]
    if missing:
        raise ValueError("the chain file is missing columns: " + ", ".join(missing))
    return [row for row in rows if (row.get("term") or "").strip()]


def parse_chain(rows: list[dict]) -> list[dict]:
    terms = []
    for index, row in enumerate(rows, start=1):
        role = (row.get("role") or "").strip().lower()
        if role not in ROLES:
            raise ValueError(f"row {index}: role {role!r} is not one of {', '.join(ROLES)}")
        try:
            low = float(str(row["low"]).replace(",", "").strip())
            high = float(str(row["high"]).replace(",", "").strip())
        except (TypeError, ValueError):
            raise ValueError(f"row {index}: low and high must both be numbers")
        if low <= 0 or high <= 0:
            raise ValueError(f"row {index}: a multiplicative term cannot be zero or negative")
        if high < low:
            raise ValueError(f"row {index}: high {high} is below low {low}")
        raw_n = (row.get("n") or "").strip()
        terms.append({
            "term": (row.get("term") or "").strip(),
            "role": role,
            "low": low,
            "high": high,
            "unit": (row.get("unit") or "").strip(),
            "family": (row.get("family") or "").strip().lower(),
            "n": int(raw_n) if raw_n.isdigit() else None,
            "source_url": (row.get("source_url") or "").strip(),
            "retrieved": (row.get("retrieved") or "").strip(),
            "what_it_measures": (row.get("what_it_measures") or "").strip(),
            "ratio": high / low,
        })
    return terms


def compute(terms: list[dict]) -> dict:
    low = high = 1.0
    running = []
    for term in terms:
        low *= term["low"]
        high *= term["high"]
        running.append({"term": term["term"], "role": term["role"],
                        "running_low": low, "running_high": high})
    # Geometric mean rather than the average of the two products. See the module docstring.
    centre = math.sqrt(low * high)
    total_ratio = high / low

    # Each term's share of the total spread, in log space, because that is the space the chain
    # multiplies in. The shares sum to 1 by construction unless every term is a point.
    log_total = math.log(total_ratio) if total_ratio > 1 else 0.0
    for term in terms:
        term["uncertainty_share"] = (math.log(term["ratio"]) / log_total) if log_total else 0.0

    category = [term for term in terms if term["role"] in CATEGORY_ROLES]
    category_low = category_high = 1.0
    for term in category:
        category_low *= term["low"]
        category_high *= term["high"]

    return {
        "terms": terms,
        "running": running,
        "category_value_low": category_low,
        "category_value_high": category_high,
        "addressable_low": low,
        "addressable_high": high,
        "centre": centre,
        "total_ratio": total_ratio,
        "geometric_term_ratio": total_ratio ** (1 / len(terms)) if terms else 1.0,
        "dominant_term": max(terms, key=lambda t: t["uncertainty_share"])["term"] if terms else None,
    }


def resolve_against(result: dict, threshold: float) -> dict:
    """Answer the question `research-protocol.md` asks and never operationalises: have we researched
    enough?

    Enough is not a feeling and it is not a source count. It is whether the range still contains the
    number that flips the decision. If your go threshold is a category value of 100 and the chain says
    30 to 314, the research has not answered anything - both answers are live. If it says 400 to 900,
    it has, and another week of desk work cannot change it.

    When the range does straddle, the useful next question is not "narrow everything". Each term is
    tested by collapsing it to its own geometric centre and re-multiplying: if the straddle survives,
    knowing that term exactly would not have settled the decision, and researching it is work that
    cannot change an outcome.
    """
    low, high = result["addressable_low"], result["addressable_high"]
    straddles = low <= threshold <= high
    settled_by = []
    if straddles:
        for term in result["terms"]:
            if term["ratio"] <= 1:
                continue
            centre = math.sqrt(term["low"] * term["high"])
            new_low = low * centre / term["low"]
            new_high = high * centre / term["high"]
            if not (new_low <= threshold <= new_high):
                settled_by.append({"term": term["term"],
                                   "uncertainty_share": term["uncertainty_share"],
                                   "range_if_known": (new_low, new_high)})
    return {
        "threshold": threshold,
        "straddles": straddles,
        "verdict": ("below on every reading" if high < threshold else
                    "above on every reading" if low > threshold else "unresolved"),
        "settled_by": sorted(settled_by, key=lambda item: -item["uncertainty_share"]),
    }


def gates(result: dict, as_of: str) -> list[dict]:
    terms = result["terms"]
    rows = []

    def add(gate: str, ok: bool, severity: str, observed: str, target: str, why: str) -> None:
        rows.append({"gate": gate, "pass": ok, "severity": severity, "observed": observed,
                     "target": target, "why": why})

    unsourced = [t["term"] for t in terms
                 if not t["source_url"].startswith("https://") or t["family"] not in FAMILIES
                 or not t["retrieved"]]
    add("every-term-sourced", not unsourced, "critical",
        ", ".join(unsourced) or "all terms carry a family, an https source and a retrieval date",
        "every term",
        "A chain is only as checkable as its weakest term. An unsourced term is where the number came "
        "from somebody's confidence, and it is invisible once the total is computed.")

    platform = [t["term"] for t in terms if t["family"] == "platform"]
    add("no-platform-self-report", not platform, "critical",
        ", ".join(platform) or "no term rests on a platform's own estimate", "no term",
        "Ad-audience figures count addressable accounts, duplicates and dormant ones included, and are "
        "the platform's commercial estimate of its own inventory. They can size an ad buy. They cannot "
        "size a market, and dividing one by an official population mixes two universes.")

    people = [t for t in terms if t["role"] == "people"]
    add("population-is-official", all(t["family"] == "official" for t in people) and bool(people),
        "high",
        ", ".join(f"{t['term']} is {t['family'] or 'unlabelled'}" for t in people) or "no people term",
        "one people term, family official",
        "The denominator is the one term where a census or administrative count exists, so using "
        "anything else is a choice to be less certain for no gain.")

    price = [t for t in terms if t["role"] == "price"]
    add("price-is-observed", all(t["family"] == "trace" for t in price) and bool(price), "high",
        ", ".join(f"{t['term']} is {t['family'] or 'unlabelled'}" for t in price) or "no price term",
        "one price term, family trace",
        "A list price is what the seller asked. A sizing chain needs what buyers paid, which lives in "
        "an observed ladder - marketplace listings, receipts, or your own transactions.")

    narrow = []
    for term in terms:
        if term["n"] is None:
            continue
        half = sampling_half_width(term["n"])
        # Compared as a share when the term is a share, and proportionally otherwise, because a
        # frequency drawn from a survey carries the same relative sampling error.
        stated = (term["high"] - term["low"]) / 2
        reference = half if term["unit"].strip() in ("share", "proportion", "%") else \
            half * 2 * ((term["high"] + term["low"]) / 2)
        if stated < reference:
            narrow.append(f"{term['term']} states +/-{stated:.4g} at n={term['n']}, "
                          f"sampling alone is +/-{reference:.4g}")
    add("survey-range-beats-its-own-margin", not narrow, "high",
        "; ".join(narrow) or "every surveyed term is at least as wide as its sampling error",
        "stated band >= 95 percent sampling half-width",
        "This is the defect that looks like diligence. A band copied off a report's point estimate is "
        "narrower than the uncertainty already inside that estimate, so the chain claims precision the "
        "survey never had.")

    points = [t["term"] for t in terms if t["low"] == t["high"]]
    allowed = [t["term"] for t in terms if t["low"] == t["high"] and t["role"] == "people"]
    add("range-not-point", set(points) <= set(allowed), "medium",
        ", ".join(sorted(set(points) - set(allowed))) or "only the counted term is a point",
        "only the official count may be a point",
        "A term entered as a single number asserts it is known exactly. That is true of a census count "
        "and of nothing else in the chain.")

    ratio = result["geometric_term_ratio"]
    add("spread-is-plausible", len(terms) < 3 or ratio >= MIN_GEOMETRIC_TERM_RATIO, "medium",
        f"geometric mean term ratio {ratio:.3f} across {len(terms)} terms",
        f">= {MIN_GEOMETRIC_TERM_RATIO} with three or more terms",
        "Ranges this tight across a whole chain mean the bands were typed to look careful rather than "
        "read off anything. The total spread is the honest output; a narrow one is a hidden point "
        "estimate.")

    stale = []
    as_of_date = dt.date.fromisoformat(as_of)
    for term in terms:
        try:
            retrieved = dt.date.fromisoformat(term["retrieved"])
        except ValueError:
            continue
        age = (as_of_date - retrieved).days
        if age > STALE_AFTER_DAYS:
            stale.append(f"{term['term']} read {age} days ago")
    add("sources-are-not-stale", not stale, "medium",
        "; ".join(stale) or f"every source read within {STALE_AFTER_DAYS} days",
        f"within {STALE_AFTER_DAYS} days",
        "Institutions get renamed and tables get dropped rather than carried over. A URL older than a "
        "year is a hypothesis about a page, and the fix is to re-open it.")

    present = {t["role"] for t in terms}
    absent = [role for role in CATEGORY_ROLES if role not in present]
    add("chain-is-complete", not absent, "high",
        "missing " + ", ".join(absent) if absent else "all four category terms present",
        "people, incidence, frequency, price",
        "A chain missing a term has not dropped a step, it has silently set that step to one. A sizing "
        "with no frequency term is asserting every buyer buys exactly once a year.")

    return rows


def blocking(gate_rows: list[dict]) -> int:
    return sum(1 for row in gate_rows
               if not row["pass"] and row["severity"] in ("critical", "high"))


def render_resolution(resolution: dict) -> list[str]:
    threshold = group(significant(resolution["threshold"]))
    if not resolution["straddles"]:
        return ["## Against the decision threshold", "",
                f"The threshold is {threshold} and the range is **{resolution['verdict']}**. The "
                f"research is finished. Not because it is exhaustive, but because no achievable "
                f"narrowing of any term can move the decision, and that is the only definition of "
                f"enough that means anything.", ""]
    lines = ["## Against the decision threshold", "",
             f"The threshold is {threshold} and the range contains it, so **the sizing has not decided "
             f"anything yet**. Both answers are still live and a document that quotes the centre here "
             f"is hiding that.", ""]
    if resolution["settled_by"]:
        lines.append("These terms would settle it on their own. Pinning any one of them down moves the "
                     "whole range off the threshold:")
        lines.append("")
        for item in resolution["settled_by"]:
            low, high = item["range_if_known"]
            lines.append(f"- **{item['term']}** - carries "
                         f"{item['uncertainty_share'] * 100:.0f}% of the spread; known exactly the "
                         f"range becomes {group(significant(low))} to {group(significant(high))}")
        lines.append("")
        lines.append("Start with the one carrying the largest share. Research on any term not listed "
                     "here is work that cannot change the outcome, however interesting it is.")
    else:
        lines.append("No single term settles it. Every term would have to narrow together, which means "
                     "desk research is the wrong instrument - the decision needs a test, a pilot or a "
                     "single real customer cohort rather than another source.")
    lines.append("")
    return lines


def render(result: dict, gate_rows: list[dict], as_of: str,
           resolution: dict | None = None) -> str:
    terms = result["terms"]
    lines = ["# Bottom-up sizing", "",
             f"Chain of {len(terms)} terms, checked as of {as_of}.", "",
             "| # | term | role | low | high | ratio | family | share of spread |",
             "|---|---|---|---|---|---|---|---|"]
    for index, term in enumerate(terms, start=1):
        lines.append(f"| {index} | {term['term']} | {term['role']} | {group(term['low'])} | "
                     f"{group(term['high'])} | {term['ratio']:.2f}x | "
                     f"{term['family'] or 'unlabelled'} | "
                     f"{term['uncertainty_share'] * 100:.0f}% |")

    lines += ["", "## The arithmetic, running", "",
              "| after | running low | running high |", "|---|---|---|"]
    for step in result["running"]:
        lines.append(f"| {step['term']} | {group(step['running_low'])} | "
                     f"{group(step['running_high'])} |")

    lines += ["", "## Totals", "",
              f"- Category value in scope: **{group(significant(result['category_value_low']))}** to "
              f"**{group(significant(result['category_value_high']))}**",
              f"- Addressable value: **{group(significant(result['addressable_low']))}** to "
              f"**{group(significant(result['addressable_high']))}**",
              f"- Centre, geometric: **{group(significant(result['centre']))}**",
              f"- Top-to-bottom spread: **{result['total_ratio']:.1f}x**", ""]
    lines += ["The centre is the geometric mean of the two products rather than their average. A "
              "multiplicative chain is symmetric in log space, so the arithmetic midpoint sits above "
              "the middle and a base case computed that way is quietly an optimistic case.", ""]
    if result["dominant_term"]:
        dominant = max(terms, key=lambda t: t["uncertainty_share"])
        lines += [f"Most of the spread is one term. **{dominant['term']}** carries "
                  f"{dominant['uncertainty_share'] * 100:.0f}% of it, so that is where the next "
                  f"research hour belongs - narrowing anything else moves the total barely at all.",
                  ""]

    if resolution is not None:
        lines += render_resolution(resolution)

    lines += ["## Gates", "", "| gate | severity | result | observed |", "|---|---|---|---|"]
    for row in gate_rows:
        lines.append(f"| {row['gate']} | {row['severity']} | {'pass' if row['pass'] else 'FAIL'} | "
                     f"{row['observed']} |")
    failed = [row for row in gate_rows if not row["pass"]]
    if failed:
        lines += ["", "## Why each failure matters", ""]
        for row in failed:
            lines += [f"**{row['gate']}** - target {row['target']}.", "", row["why"], ""]
    count = blocking(gate_rows)
    lines += ["", f"Blocking failures: **{count}**.", ""]
    if count:
        lines += ["Do not put the total in a document yet. A blocking failure means the number is not "
                  "wrong by a knowable amount, it is unsupported, and a reader cannot tell the "
                  "difference from the total alone.", ""]
    else:
        lines += ["Quote the range, not the centre, and carry the family labels with it. The range is "
                  "usually the more persuasive slide because it survives the first challenge.", ""]
    return "\n".join(lines) + "\n"


def render_families() -> str:
    lines = ["# The four measurement families", "",
             "Every source belongs to one, and the family decides what it can be wrong about. Pull the "
             "terms of a chain from different families so the weakest link is visible rather than "
             "buried in one confident total.", "",
             "| family | what it is, and what it is systematically wrong about |", "|---|---|"]
    for name, description in FAMILIES.items():
        lines.append(f"| `{name}` | {description} |")
    lines += ["", "## Roles in the chain", "", "| role | term |", "|---|---|"]
    for name, description in ROLES.items():
        lines.append(f"| `{name}` | {description} |")
    lines += ["", "`people` through `price` give the category value in scope. `reach` cuts that to what "
              "your distribution and media footprint can address, which is the only one of the two a "
              "plan can be held to.", ""]
    return "\n".join(lines) + "\n"


def render_margin(n: int) -> str:
    half = sampling_half_width(n)
    gap = minimum_detectable_gap(n)
    return ("# Sampling error at n = %d\n\n"
            "- 95 percent half-width on a proportion, worst case: **%.1f points**\n"
            "- Two proportions from the same survey: a gap below **%.1f points** is not defensible\n\n"
            "Any range you enter for a term drawn from this survey has to be at least this wide, "
            "because this much uncertainty is already inside the point estimate you read.\n"
            % (n, half * 100, gap * 100))


TEMPLATE = """term,role,low,high,unit,family,n,source_url,retrieved,what_it_measures
households in scope,people,,,households,official,,https://,,
share with the need,incidence,,,share,panel,,https://,,
purchases per year,frequency,,,count,trace,,https://,,
price actually paid,price,,,currency,trace,,https://,,
reachable share,reach,,,share,trace,,https://,,
"""


def self_check() -> str:
    notes = []

    clean = parse_chain(list(csv.DictReader(io.StringIO(
        "term,role,low,high,unit,family,n,source_url,retrieved,what_it_measures\n"
        "urban households,people,8000000,8000000,households,official,,https://nso.gov.vn/x,"
        "2026-07-01,Census household count\n"
        "share buying monthly,incidence,0.18,0.32,share,panel,600,https://example.org/p,"
        "2026-06-01,Claimed monthly purchase\n"
        "purchases per year,frequency,4,7,count,trace,,https://example.org/t,2026-05-01,Receipts\n"
        "price paid,price,45000,70000,currency,trace,,https://shopee.vn/x,2026-07-10,Listing ladder\n"
        "reachable share,reach,0.1,0.25,share,trace,,https://example.org/d,2026-07-10,Our footprint\n"
    ))))
    result = compute(clean)
    rows = gates(result, "2026-07-31")
    assert blocking(rows) == 0, [r for r in rows if not r["pass"]]

    # The product, by hand: 8e6 * 0.18 * 4 * 45000 * 0.1 and the same with the highs.
    expected_low = 8_000_000 * 0.18 * 4 * 45000 * 0.1
    expected_high = 8_000_000 * 0.32 * 7 * 70000 * 0.25
    assert math.isclose(result["addressable_low"], expected_low, rel_tol=1e-9), result
    assert math.isclose(result["addressable_high"], expected_high, rel_tol=1e-9), result
    # The centre is the geometric mean, which sits below the average of the two products. If this ever
    # inverts, the base case has started flattering itself.
    assert result["centre"] < (expected_low + expected_high) / 2
    assert math.isclose(result["centre"], math.sqrt(expected_low * expected_high), rel_tol=1e-9)
    # The shares of spread partition the total, so they sum to one and can be read as percentages.
    assert math.isclose(sum(t["uncertainty_share"] for t in clean), 1.0, rel_tol=1e-9)
    notes.append("a five-term chain multiplies to the hand-computed product, "
                 f"spread {result['total_ratio']:.1f}x, dominant term {result['dominant_term']!r}")

    # n=600 gives a 4.0-point half-width, so a band of +/-0.01 on a share is a quarter of the
    # sampling error and must fail. This is the gate that fires most often on real work.
    narrow = parse_chain(list(csv.DictReader(io.StringIO(
        "term,role,low,high,unit,family,n,source_url,retrieved,what_it_measures\n"
        "urban households,people,8000000,8000000,households,official,,https://nso.gov.vn/x,"
        "2026-07-01,Census\n"
        "share buying,incidence,0.40,0.42,share,panel,300,https://example.org/p,2026-06-01,Claimed\n"
        "purchases per year,frequency,4,7,count,trace,,https://example.org/t,2026-05-01,Receipts\n"
        "price paid,price,45000,70000,currency,trace,,https://shopee.vn/x,2026-07-10,Ladder\n"
    ))))
    rows = gates(compute(narrow), "2026-07-31")
    failed = {row["gate"] for row in rows if not row["pass"]}
    assert "survey-range-beats-its-own-margin" in failed, rows
    half = sampling_half_width(300)
    assert abs(half - 0.0566) < 0.0005, half
    notes.append(f"a +/-1 point band on n=300 fails against its own {half * 100:.1f}-point margin")

    # Platform self-report is refused rather than downgraded, and the refusal is critical.
    planner = parse_chain(list(csv.DictReader(io.StringIO(
        "term,role,low,high,unit,family,n,source_url,retrieved,what_it_measures\n"
        "reachable accounts,people,50000000,52000000,people,platform,,https://facebook.com/x,"
        "2026-07-01,Ad audience size\n"
        "share buying,incidence,0.18,0.32,share,panel,600,https://example.org/p,2026-06-01,Claimed\n"
        "purchases per year,frequency,4,7,count,trace,,https://example.org/t,2026-05-01,Receipts\n"
        "price paid,price,45000,70000,currency,trace,,https://shopee.vn/x,2026-07-10,Ladder\n"
    ))))
    rows = gates(compute(planner), "2026-07-31")
    refused = [row for row in rows if row["gate"] == "no-platform-self-report"]
    assert refused and not refused[0]["pass"] and refused[0]["severity"] == "critical", rows
    assert "population-is-official" in {row["gate"] for row in rows if not row["pass"]}
    notes.append("an ad-planner reach figure used as a denominator fails two gates, one critical")

    # A chain with a term omitted is asserting that term is 1, which is the quiet version of the error.
    short = parse_chain(list(csv.DictReader(io.StringIO(
        "term,role,low,high,unit,family,n,source_url,retrieved,what_it_measures\n"
        "urban households,people,8000000,8000000,households,official,,https://nso.gov.vn/x,"
        "2026-07-01,Census\n"
        "share buying,incidence,0.18,0.32,share,panel,600,https://example.org/p,2026-06-01,Claimed\n"
        "price paid,price,45000,70000,currency,trace,,https://shopee.vn/x,2026-07-10,Ladder\n"
    ))))
    rows = gates(compute(short), "2026-07-31")
    assert "chain-is-complete" in {row["gate"] for row in rows if not row["pass"]}, rows
    notes.append("a chain with no frequency term is caught rather than silently multiplied by one")

    # Staleness is measured against the date passed in, not against the clock, so this assertion does
    # not start failing on its own one year from now.
    rows = gates(compute(clean), "2027-12-31")
    assert "sources-are-not-stale" in {row["gate"] for row in rows if not row["pass"]}
    notes.append("staleness is measured against --as-of, so the suite does not rot")

    # The stop rule. The clean chain runs 25.9bn to 314bn, so a threshold inside that decides nothing
    # and a threshold above it decides the question without another source being read.
    result = compute(clean)
    inside = resolve_against(result, result["centre"])
    assert inside["straddles"] and inside["verdict"] == "unresolved", inside
    # A threshold sitting exactly on the centre can never be settled by narrowing one term, and that is
    # arithmetic rather than a defect. Collapsing a term to its own geometric centre leaves the total's
    # geometric centre where it was, so the threshold stays inside the new range whatever you pin down.
    # A decision balanced on the centre of your own estimate is not a research problem.
    assert inside["settled_by"] == [], inside["settled_by"]
    near_edge = resolve_against(result, result["addressable_high"] * 0.8)
    assert near_edge["straddles"] and near_edge["settled_by"], near_edge
    assert near_edge["settled_by"][0]["uncertainty_share"] >= \
        near_edge["settled_by"][-1]["uncertainty_share"], "settling terms come back widest-first"
    above = resolve_against(result, result["addressable_high"] * 2)
    assert not above["straddles"] and above["verdict"] == "below on every reading", above
    below = resolve_against(result, result["addressable_low"] / 2)
    assert below["verdict"] == "above on every reading", below
    # A term named as settling the threshold has to actually settle it when collapsed, and the check
    # is the same arithmetic run again rather than a heuristic.
    for item in inside["settled_by"]:
        low, high = item["range_if_known"]
        assert not (low <= inside["threshold"] <= high), item
    notes.append(f"a threshold at the centre stays unresolved and lists "
                 f"{len(inside['settled_by'])} term(s) that would settle it; one outside the range "
                 f"ends the research")

    report = ["# size_market self-check", ""]
    report += [f"- {note}" for note in notes]
    report += ["", "self-check passed", ""]
    return "\n".join(report)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Multiply a bottom-up sizing chain out loud and check every term has evidence.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--check", metavar="CHAIN.CSV", help="read a chain and grade it")
    source.add_argument("--template", metavar="CHAIN.CSV", help="write a starter chain file")
    source.add_argument("--families", action="store_true", help="print the families and roles")
    source.add_argument("--margin", type=int, metavar="N", help="sampling error at a sample size")
    source.add_argument("--self-check", action="store_true", help="run the built-in assertions")
    parser.add_argument("--as-of", default=dt.date.today().isoformat(),
                        help="date to measure source staleness against, YYYY-MM-DD")
    parser.add_argument("--threshold", type=float, metavar="VALUE",
                        help="the addressable value that flips the decision; reports whether the range "
                             "still contains it and which term would settle it")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output", help="write to a file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    args = build_parser().parse_args(argv)

    if args.self_check:
        emit(self_check(), args.output)
        return 0
    if args.families:
        emit(render_families(), args.output)
        return 0
    if args.margin is not None:
        if args.margin <= 0:
            print("--margin needs a positive sample size", file=sys.stderr)
            return 1
        emit(render_margin(args.margin), args.output)
        return 0
    if args.template:
        path = Path(args.template)
        if path.exists():
            print(f"{path} already exists; not overwriting", file=sys.stderr)
            return 1
        path.write_text(TEMPLATE, encoding="utf-8")
        emit(f"Wrote {path}. Fill low and high for every term, name the family, and paste the URL you "
             f"actually opened.\n")
        return 0

    try:
        terms = parse_chain(read_chain(args.check))
        dt.date.fromisoformat(args.as_of)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1

    result = compute(terms)
    gate_rows = gates(result, args.as_of)
    resolution = None
    if args.threshold is not None:
        if args.threshold <= 0:
            print("--threshold needs a positive value", file=sys.stderr)
            return 1
        resolution = resolve_against(result, args.threshold)
    if args.json:
        emit_json({"as_of": args.as_of, "resolution": resolution, "totals": {
            "category_value_low": result["category_value_low"],
            "category_value_high": result["category_value_high"],
            "addressable_low": result["addressable_low"],
            "addressable_high": result["addressable_high"],
            "centre": result["centre"],
            "total_ratio": result["total_ratio"]},
            "terms": [{k: v for k, v in term.items()} for term in result["terms"]],
            "gates": gate_rows,
            "blocking": blocking(gate_rows)}, args.output)
    else:
        emit(render(result, gate_rows, args.as_of, resolution), args.output)

    if blocking(gate_rows):
        return 2
    # An unresolved threshold is the definition of "computable but unsettled", which is what exit 3
    # exists for. The arithmetic ran and the decision it was run to make is still open.
    if any(not row["pass"] for row in gate_rows) or (resolution and resolution["straddles"]):
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
