#!/usr/bin/env python3
"""Decide whether customer research has heard enough, and what its numbers are allowed to say.

Two sentences do most of the damage in customer research. "We talked to customers and they said X"
and "60 percent of customers want X". The first hides how many, the second hides out of how many.

This reads a coded-verbatim table and answers both. It draws the new-code curve, so "we have heard
enough" becomes a fact about whether the last few conversations taught you anything. And it puts a
95 percent Wilson interval on every theme's prevalence, so a share arrives with the width of its own
uncertainty attached. Six of ten is 60 percent and it is also anywhere from 31 to 83, which is not a
finding, it is a direction.

The gate that matters most is `disconfirmation-recorded`, and it is the reason this script wants a
`stance` column rather than a list of quotes. A research file normally holds only the times somebody
raised a theme. Nobody writes down the customer who was asked and said it was not a problem, so the
denominator quietly becomes the numerator and every theme is unanimous. When a code has no `denied`
row this script prints a count and refuses to print a share, because there is no population to take a
share of. That refusal is the whole point: the arithmetic of an unanimous theme looks identical to the
arithmetic of a well-supported one.

`data/evidence-sources.csv` supplies what each source over-represents, what it structurally cannot
see, and the headcount below which one of its themes is not yet a theme. This script reads that table
rather than carrying its own thresholds, so a source's floor is edited in one place.

    python scripts/check_evidence_saturation.py --check coded.csv
    python scripts/check_evidence_saturation.py --check coded.csv --json
    python scripts/check_evidence_saturation.py --interval 10 0.6
    python scripts/check_evidence_saturation.py --needed 0.5 0.1
    python scripts/check_evidence_saturation.py --sources
    python scripts/check_evidence_saturation.py --self-check

Exit codes are 0 clean, 1 usage error, 2 a gate failed, 3 computable but unsettled.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
SOURCE_TABLE = DATA / "evidence-sources.csv"

# 1.959964 is the two-sided 95 percent normal quantile. The Wilson score interval is used rather than
# the textbook p +- z*sqrt(p(1-p)/n) because the textbook one is wrong exactly where customer research
# lives: small n, and shares near 0 or 1, where it returns bounds below zero or above one.
Z95 = 1.959964

# Guest, Bunce and Johnson 2006 found 12 interviews carried the great majority of the codes their 60
# eventually produced, and Hennink and Kaiser's 2022 review of saturation studies puts code saturation
# in the 9-to-17 range with interpretation stabilising later. 12 and 16 are the two floors that
# literature supports; both are held here rather than one, because they answer different questions.
CODE_SATURATION_MIN = 12
MEANING_SATURATION_MIN = 16

# Consecutive respondents that must teach you nothing new before the code set is called closed. One
# quiet interview is common in the middle of a study and means nothing.
DRY_RESPONDENTS = 3

# A share whose 95 percent interval is wider than this is a direction, not a number. Twenty points is
# a house threshold, set where it is because a 20-point spread still separates "most" from "a few".
MAX_INTERVAL_WIDTH = 0.20

# Frequency and intensity are different axes and collapsing them is the error the old prose named
# without operationalising. These four numbers are the corners of that grid.
COMMON_SHARE = 0.50
RARE_SHARE = 0.25
BLOCKING_SHARE_HIGH = 0.50
PASSING_SHARE_LOW = 0.20

REQUIRED_COLUMNS = ("respondent_id", "sequence", "source_id", "code", "stance", "intensity",
                    "provenance")

# raised is unprompted, confirmed is agreement after being asked, denied is the row nobody writes:
# asked, and said no. Only the third one creates a denominator.
STANCES = {"raised", "confirmed", "denied"}
AFFIRMS = {"raised", "confirmed"}

# Three levels, named rather than scored 1 to 5, because a five-point intensity scale invites a mean
# and the mean of an invented scale is not a measurement.
INTENSITIES = {"passing", "emphasised", "blocking"}

STATUS_EXIT = {"passed": 0, "review": 3, "failed": 2, "skipped": 0}


# --- arithmetic -------------------------------------------------------------------------------

def wilson(successes: int, total: int, z: float = Z95) -> tuple[float, float]:
    """The Wilson score interval for a proportion. Returns (low, high), both inside [0, 1]."""
    if total <= 0:
        return (0.0, 1.0)
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    spread = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return (max(0.0, centre - spread), min(1.0, centre + spread))


def respondents_needed(p: float, width: float) -> int:
    """Smallest n whose 95 percent Wilson interval at observed share p is no wider than width.

    Solved by walking n upward rather than by inverting the formula. The inversion has a closed form
    only if you drop the continuity terms, which is the approximation this function exists to avoid,
    and n is never large enough for the loop to matter.
    """
    for n in range(1, 100001):
        low, high = wilson(round(p * n), n)
        if high - low <= width:
            return n
    return 100001


# --- input ------------------------------------------------------------------------------------

def read_sources() -> dict[str, dict[str, str]]:
    with SOURCE_TABLE.open(encoding="utf-8", newline="") as handle:
        return {row["source_id"]: row for row in csv.DictReader(handle)}


def source_floor(row: dict[str, str]) -> int | None:
    """The source's headcount floor, or None when its floor is an interval rather than a count."""
    value = row.get("theme_floor", "")
    return int(value) if value.isdigit() else None


def read_coded(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"the coded table is missing {', '.join(missing)}")
        return [row for row in reader if any((value or "").strip() for value in row.values())]


# --- measurement ------------------------------------------------------------------------------

def respondent_order(rows: list[dict[str, str]]) -> list[str]:
    """Respondents in collection order. Ties break on id so the curve is deterministic."""
    seen: dict[str, int] = {}
    for row in rows:
        rid = row["respondent_id"].strip()
        try:
            sequence = int(row["sequence"])
        except (TypeError, ValueError):
            sequence = 10**6
        seen.setdefault(rid, sequence)
    return sorted(seen, key=lambda rid: (seen[rid], rid))


def saturation(rows: list[dict[str, str]]) -> dict[str, object]:
    """The new-code curve, and whether the code set has stopped growing."""
    order = respondent_order(rows)
    affirmed: dict[str, set[str]] = {rid: set() for rid in order}
    for row in rows:
        if row["stance"].strip() in AFFIRMS:
            affirmed[row["respondent_id"].strip()].add(row["code"].strip())

    seen: set[str] = set()
    curve = []
    for position, rid in enumerate(order, start=1):
        fresh = sorted(affirmed[rid] - seen)
        seen |= affirmed[rid]
        curve.append({"position": position, "respondent_id": rid,
                      "new_codes": len(fresh), "codes_so_far": len(seen), "first_seen": fresh})

    total = len(seen)
    tail = curve[-DRY_RESPONDENTS:]
    dry = len(curve) >= DRY_RESPONDENTS and all(step["new_codes"] == 0 for step in tail)
    if len(order) < CODE_SATURATION_MIN:
        verdict = "too-few-to-say"
    elif dry:
        verdict = "code-set-closed" if len(order) >= MEANING_SATURATION_MIN else "code-set-closed-early"
    else:
        verdict = "still-growing"

    milestones = {}
    for mark in (6, CODE_SATURATION_MIN, MEANING_SATURATION_MIN, len(order)):
        if mark and mark <= len(order):
            found = curve[mark - 1]["codes_so_far"]
            milestones[mark] = {"codes": found,
                                "share_of_final": round(found / total, 3) if total else 0.0}

    return {"respondents": len(order), "codes": total, "verdict": verdict,
            "last_new_code_at": max((s["position"] for s in curve if s["new_codes"]), default=0),
            "new_codes_in_last_three": sum(step["new_codes"] for step in tail),
            "milestones": milestones, "curve": curve}


def heard_per_source(rows: list[dict[str, str]],
                     sources: dict[str, dict[str, str]]) -> list[dict[str, object]]:
    """How many respondents each source contributed, against the floor that source's row states.

    This is a fact about the source and not about any one theme, which is why it is reported once here
    rather than stamped onto every code the source touched.
    """
    counts: dict[str, set[str]] = {}
    for row in rows:
        counts.setdefault(row["source_id"].strip(), set()).add(row["respondent_id"].strip())
    report = []
    for source_id, people in sorted(counts.items()):
        row = sources.get(source_id)
        floor = source_floor(row) if row else None
        report.append({"source_id": source_id, "respondents": len(people), "floor": floor,
                       "status": "unknown-source" if row is None
                       else "no-headcount-floor" if floor is None
                       else "at-floor" if len(people) >= floor else "below-floor"})
    return report


def prevalence(rows: list[dict[str, str]], sources: dict[str, dict[str, str]]) -> list[dict]:
    """Per code: who affirmed it, who denied it, the share that follows, and what the share may say."""
    codes: dict[str, dict[str, set[str]]] = {}
    for row in rows:
        code = row["code"].strip()
        rid = row["respondent_id"].strip()
        entry = codes.setdefault(code, {"affirm": set(), "deny": set(), "blocking": set(),
                                        "sources": set()})
        entry["sources"].add(row["source_id"].strip())
        if row["stance"].strip() in AFFIRMS:
            entry["affirm"].add(rid)
            if row["intensity"].strip() == "blocking":
                entry["blocking"].add(rid)
        else:
            entry["deny"].add(rid)

    people = len(respondent_order(rows))
    report = []
    for code, entry in sorted(codes.items()):
        affirm, deny = len(entry["affirm"]), len(entry["deny"])
        asked = affirm + deny
        blocking = len(entry["blocking"])
        flags = []

        if deny == 0:
            verdict = "counted-only"
            low = high = None
        else:
            low, high = wilson(affirm, asked)
            verdict = "reportable" if (high - low) <= MAX_INTERVAL_WIDTH else "share-too-wide"

        if len(entry["sources"]) == 1:
            flags.append("single-source")
        share_of_all = affirm / people if people else 0.0
        blocking_share = blocking / affirm if affirm else 0.0
        if share_of_all <= RARE_SHARE and blocking_share >= BLOCKING_SHARE_HIGH:
            flags.append("rare-but-blocking")
        if share_of_all >= COMMON_SHARE and blocking_share <= PASSING_SHARE_LOW:
            flags.append("common-but-passing")

        report.append({
            "code": code, "affirmed": affirm, "denied": deny, "asked": asked,
            "blocking": blocking, "blocking_share": round(blocking_share, 3),
            "share_of_respondents": round(share_of_all, 3),
            # Suppressed with the interval and not merely reported without one. A theme nobody was
            # recorded denying has asked == affirm, so this cell would read 1.0 - which is the exact
            # number the unit refuses, arriving through the machine-readable door. The text output
            # never printed it; a caller reading the JSON would have.
            "share_of_asked": round(affirm / asked, 3) if deny else None,
            "interval": None if low is None else [round(low, 3), round(high, 3)],
            "interval_width": None if low is None else round(high - low, 3),
            "sources": sorted(entry["sources"]), "verdict": verdict, "flags": flags,
        })
    return report


# --- gates ------------------------------------------------------------------------------------

def gates(rows: list[dict[str, str]], sources: dict[str, dict[str, str]],
          curve: dict[str, object], themes: list[dict],
          per_source: list[dict[str, object]]) -> list[dict[str, str]]:
    results = []

    missing = [row["respondent_id"] for row in rows if not row["provenance"].strip()]
    results.append({
        "gate": "provenance-recorded",
        "status": "failed" if missing else "passed",
        "detail": f"{len(missing)} rows carry no provenance" if missing
                  else f"all {len(rows)} rows name where and when they came from"})

    unknown = sorted({row["source_id"].strip() for row in rows} - set(sources))
    results.append({
        "gate": "known-source",
        "status": "failed" if unknown else "passed",
        "detail": f"not in evidence-sources.csv: {', '.join(unknown)}" if unknown
                  else f"{len({r['source_id'] for r in rows})} sources, all in the table"})

    bad = []
    orders: dict[str, str] = {}
    for row in rows:
        if row["stance"].strip() not in STANCES:
            bad.append(f"stance {row['stance']!r}")
        if row["intensity"].strip() not in INTENSITIES:
            bad.append(f"intensity {row['intensity']!r}")
        rid, sequence = row["respondent_id"].strip(), row["sequence"].strip()
        if orders.setdefault(rid, sequence) != sequence:
            bad.append(f"{rid} has two sequence numbers")
    results.append({
        "gate": "input-vocabulary",
        "status": "failed" if bad else "passed",
        "detail": "; ".join(sorted(set(bad))[:4]) if bad
                  else "every stance and intensity is one of the allowed values"})

    denied = sum(1 for row in rows if row["stance"].strip() == "denied")
    counted_only = [theme["code"] for theme in themes if theme["verdict"] == "counted-only"]
    results.append({
        "gate": "disconfirmation-recorded",
        "status": "failed" if denied == 0 else ("review" if counted_only else "passed"),
        "detail": "no row records a customer who was asked and said no, so no theme here has a "
                  "denominator and none of them can carry a share" if denied == 0
                  else (f"{denied} denials recorded, but these were never asked against: "
                        f"{', '.join(counted_only)}" if counted_only
                        else f"{denied} denials recorded across every theme")})

    verdict = curve["verdict"]
    results.append({
        "gate": "code-saturation",
        "status": {"code-set-closed": "passed", "code-set-closed-early": "review",
                   "still-growing": "review", "too-few-to-say": "review"}[verdict],
        "detail": {
            "code-set-closed": f"the last {DRY_RESPONDENTS} respondents added no new code at "
                               f"n={curve['respondents']}",
            "code-set-closed-early": f"no new codes since respondent {curve['last_new_code_at']}, "
                                     f"but n={curve['respondents']} is under {MEANING_SATURATION_MIN}, "
                                     "so the code set is closed and the interpretation is not",
            "still-growing": f"the last {DRY_RESPONDENTS} respondents added "
                             f"{curve['new_codes_in_last_three']} new codes; the set is still growing",
            "too-few-to-say": f"n={curve['respondents']} is under {CODE_SATURATION_MIN}, which is "
                              "a discovery sample: good for finding a theme, no basis for closing "
                              "the list"}[verdict]})

    thin = [f"{entry['source_id']} ({entry['respondents']}/{entry['floor']})"
            for entry in per_source if entry["status"] == "below-floor"]
    results.append({
        "gate": "source-headcount",
        "status": "review" if thin else "passed",
        "detail": "under the floor its own row in evidence-sources.csv states, so a theme seen only "
                  f"here is not yet a theme: {', '.join(thin)}" if thin
                  else "every source with a headcount floor is at or above it"})

    wide = [theme["code"] for theme in themes if theme["verdict"] == "share-too-wide"]
    results.append({
        "gate": "share-precision",
        "status": "review" if wide else "passed",
        "detail": f"interval wider than {int(MAX_INTERVAL_WIDTH * 100)} points, report as a direction "
                  f"not a percentage: {', '.join(wide)}" if wide
                  else "every reportable share has an interval narrower than "
                       f"{int(MAX_INTERVAL_WIDTH * 100)} points"})

    single = [theme["code"] for theme in themes if "single-source" in theme["flags"]]
    results.append({
        "gate": "triangulated",
        "status": "review" if single else "passed",
        "detail": f"seen through one source only, so still indistinguishable from that source's own "
                  f"bias: {', '.join(single)}" if single
                  else "every theme appears in at least two sources"})

    leaked = sorted({row["source_id"].strip() for row in rows
                     if row.get("verbatim", "").strip()
                     and sources.get(row["source_id"].strip(), {}).get("quotable_publicly") == "no"})
    results.append({
        "gate": "stored-quote-rights",
        "status": "failed" if leaked else ("passed" if any("verbatim" in row for row in rows)
                                           else "skipped"),
        "detail": f"quoted text is stored against sources the table marks unquotable: "
                  f"{', '.join(leaked)}" if leaked
                  else ("no stored quote comes from an unquotable source" if rows and
                        "verbatim" in rows[0] else "no verbatim column, so nothing to check")})

    return results


def check(path: Path) -> dict[str, object]:
    sources = read_sources()
    rows = read_coded(path)
    curve = saturation(rows)
    themes = prevalence(rows, sources)
    per_source = heard_per_source(rows, sources)
    checks = gates(rows, sources, curve, themes, per_source)
    statuses = {result["status"] for result in checks}
    verdict = "failed" if "failed" in statuses else ("review" if "review" in statuses else "passed")
    return {"file": str(path), "rows": len(rows), "verdict": verdict,
            "saturation": curve, "themes": themes, "sources": per_source, "gates": checks}


# --- output -----------------------------------------------------------------------------------

def as_text(report: dict[str, object]) -> str:
    curve = report["saturation"]
    lines = [f"Customer evidence: {report['file']}",
             f"  {report['rows']} coded rows, {curve['respondents']} respondents, "
             f"{curve['codes']} distinct themes",
             f"  verdict: {report['verdict']}",
             "",
             "Saturation"]
    for mark, hit in sorted(curve["milestones"].items()):
        lines.append(f"  after {mark:>3} respondents: {hit['codes']:>3} themes "
                     f"({hit['share_of_final']:.0%} of the themes this study eventually found)")
    lines.append(f"  last new theme arrived at respondent {curve['last_new_code_at']}")
    lines.append("")
    lines.append("Sources")
    for entry in report["sources"]:
        floor = entry["floor"]
        against = f"against a floor of {floor}" if floor else "no headcount floor for this source"
        lines.append(f"  {entry['source_id']}: {entry['respondents']} respondents, {against}"
                     f"  [{entry['status']}]")
    lines.append("")
    lines.append("Themes")
    for theme in report["themes"]:
        if theme["interval"]:
            low, high = theme["interval"]
            share = (f"{theme['affirmed']}/{theme['asked']} asked = {theme['share_of_asked']:.0%} "
                     f"(95% CI {low:.0%}-{high:.0%})")
        else:
            share = f"{theme['affirmed']} raised it, nobody was asked against it, so no share"
        lines.append(f"  {theme['code']}")
        lines.append(f"    {share}")
        lines.append(f"    {theme['blocking']} of {theme['affirmed']} called it blocking; "
                     f"sources: {', '.join(theme['sources'])}")
        lines.append(f"    {theme['verdict']}"
                     + (f"; {', '.join(theme['flags'])}" if theme["flags"] else ""))
    lines.append("")
    lines.append("Gates")
    for result in report["gates"]:
        lines.append(f"  [{result['status']:>7}] {result['gate']}: {result['detail']}")
    lines.append("")
    lines.append("What this cannot tell you: whether the people you did not reach would have said "
                 "the same thing. Saturation closes the list of themes you found, not the list that "
                 "exists. Read the source's what_it_cannot_see cell before quoting any of it.")
    return "\n".join(lines) + "\n"


def print_sources(query: str | None = None) -> str:
    rows = read_sources().values()
    if query:
        needle = query.lower()
        rows = [row for row in rows if needle in " ".join(row.values()).lower()]
    lines = [f"{len(list(rows))} customer-evidence sources" if not query
             else f"sources matching {query!r}"]
    for row in read_sources().values():
        if query and query.lower() not in " ".join(row.values()).lower():
            continue
        floor = row["theme_floor"]
        lines.append("")
        lines.append(f"{row['source_id']}  [{row['evidence_type']}]")
        lines.append(f"  is: {row['what_it_is']}")
        lines.append(f"  over-represents: {row['who_it_over_represents']}")
        lines.append(f"  cannot see: {row['what_it_cannot_see']}")
        lines.append(f"  floor: {floor if floor.isdigit() else 'set by the interval you need'}"
                     f" - {row['minimum_before_a_theme_counts']}")
        lines.append(f"  quotable: {row['quotable_publicly']} - {row['rights_note']}")
        lines.append(f"  strongest claim: {row['strongest_claim_it_supports']}")
        lines.append(f"  does not establish: {row['what_it_does_not_establish']}")
    return "\n".join(lines) + "\n"


def print_interval(total: int, share: float) -> str:
    successes = round(share * total)
    low, high = wilson(successes, total)
    width = high - low
    reading = ("a number you can report" if width <= MAX_INTERVAL_WIDTH
               else "a direction, not a number")
    return (f"{successes} of {total} = {successes / total:.0%}\n"
            f"  95% Wilson interval: {low:.1%} to {high:.1%}, {width * 100:.0f} points wide\n"
            f"  that is {reading}\n"
            f"  for an interval {int(MAX_INTERVAL_WIDTH * 100)} points wide at this share you need "
            f"{respondents_needed(share, MAX_INTERVAL_WIDTH)} respondents\n")


def print_needed(share: float, width: float) -> str:
    n = respondents_needed(share, width)
    low, high = wilson(round(share * n), n)
    return (f"to measure a share near {share:.0%} to within {width * 100:.0f} points, "
            f"95 percent confident:\n"
            f"  {n} respondents, which lands the interval at {low:.1%} to {high:.1%}\n"
            f"  this is the count for the arithmetic only. It says nothing about whether those "
            f"respondents are the right ones, and non-response bias does not shrink with n\n")


# --- self-check -------------------------------------------------------------------------------

def self_check() -> str:
    out = []

    low, high = wilson(6, 10)
    assert 0.30 < low < 0.32 and 0.82 < high < 0.84, (low, high)
    out.append(f"six of ten is 60 percent and also anywhere from {low:.0%} to {high:.0%}")

    assert wilson(0, 5) == (0.0, wilson(0, 5)[1]) and wilson(0, 5)[1] < 0.55
    assert wilson(5, 5)[0] > 0.55 and wilson(5, 5)[1] == 1.0
    out.append("a unanimous 5 of 5 still has a lower bound near a half, and neither bound escapes 0..1")

    assert respondents_needed(0.5, 0.2) > respondents_needed(0.5, 0.4)
    assert respondents_needed(0.05, 0.1) < respondents_needed(0.5, 0.1)
    out.append(f"a 20-point interval at a half needs {respondents_needed(0.5, 0.2)} respondents; "
               f"a 10-point one needs {respondents_needed(0.5, 0.1)}")

    sources = read_sources()
    assert len(sources) >= 20, len(sources)
    assert source_floor(sources["switch-interviews"]) == CODE_SATURATION_MIN
    assert source_floor(sources["customer-survey"]) is None, \
        "a survey's floor is an interval width, not a headcount"
    out.append("the floors come from evidence-sources.csv, not from this file")

    # A theme everybody raised and nobody was ever asked against gets a count and no share.
    unanimous = [
        {"respondent_id": f"r{i}", "sequence": str(i), "source_id": "switch-interviews",
         "code": "price-unclear", "stance": "raised", "intensity": "emphasised",
         "provenance": "2026-07-02 interview"} for i in range(1, 6)]
    themes = prevalence(unanimous, sources)
    assert themes[0]["verdict"] == "counted-only" and themes[0]["interval"] is None, themes[0]
    # Withheld from the payload and not only from the printout. This assertion used to read `== 1.0`,
    # on the reasoning that as_text never prints the cell so computing it was harmless. It was not:
    # `--json` is the interface a caller automates against, and the cell said 1.0 for the one theme
    # whose share this whole script exists to refuse.
    assert themes[0]["share_of_asked"] is None, "the trivial 100 percent is still in the payload"
    out.append("five raised it, nobody denied it, so the share is withheld from the text and the JSON")

    # Add two people who were asked and said no, and the same theme becomes reportable arithmetic.
    with_denial = unanimous + [
        {"respondent_id": f"r{i}", "sequence": str(i), "source_id": "switch-interviews",
         "code": "price-unclear", "stance": "denied", "intensity": "passing",
         "provenance": "2026-07-03 interview"} for i in range(6, 8)]
    themes = prevalence(with_denial, sources)
    assert themes[0]["verdict"] == "share-too-wide", themes[0]
    assert themes[0]["asked"] == 7 and themes[0]["affirmed"] == 5
    out.append("two recorded denials turn a count into a share, and the share is still too wide to quote")

    # The curve closes only when several consecutive respondents teach nothing.
    growing = [{"respondent_id": f"r{i}", "sequence": str(i), "source_id": "switch-interviews",
                "code": f"theme-{i}", "stance": "raised", "intensity": "passing",
                "provenance": "2026-07-02 interview"} for i in range(1, 15)]
    assert saturation(growing)["verdict"] == "still-growing"
    settled = growing[:11] + [
        {"respondent_id": f"r{i}", "sequence": str(i), "source_id": "switch-interviews",
         "code": "theme-1", "stance": "raised", "intensity": "passing",
         "provenance": "2026-07-02 interview"} for i in range(12, 18)]
    curve = saturation(settled)
    assert curve["verdict"] == "code-set-closed", curve["verdict"]
    assert curve["respondents"] == 17 and curve["new_codes_in_last_three"] == 0
    short = saturation(growing[:8])
    assert short["verdict"] == "too-few-to-say", short["verdict"]
    out.append("a new theme every time is still-growing; eleven then six quiet ones is closed; "
               "eight is too few to say either way")

    # A theme seen through one source is that source's bias until a second source sees it.
    one_source = prevalence(with_denial, sources)[0]
    assert "single-source" in one_source["flags"]
    two = with_denial + [{"respondent_id": "r9", "sequence": "9", "source_id": "support-tickets",
                          "code": "price-unclear", "stance": "raised", "intensity": "blocking",
                          "provenance": "2026-07-04 ticket 8812"}]
    assert "single-source" not in prevalence(two, sources)[0]["flags"]
    out.append("one source flags single-source; a second source clears it")

    # Rare and blocking is a different instruction from common and passing.
    grid = [{"respondent_id": f"r{i}", "sequence": str(i), "source_id": "switch-interviews",
             "code": "delivery-late", "stance": "raised", "intensity": "passing",
             "provenance": "2026-07-02 interview"} for i in range(1, 13)]
    grid += [{"respondent_id": "r13", "sequence": "13", "source_id": "switch-interviews",
              "code": "no-invoice", "stance": "raised", "intensity": "blocking",
              "provenance": "2026-07-02 interview"}]
    grid += [{"respondent_id": f"r{i}", "sequence": str(i), "source_id": "switch-interviews",
              "code": "no-invoice", "stance": "denied", "intensity": "passing",
              "provenance": "2026-07-02 interview"} for i in range(1, 13)]
    by_code = {theme["code"]: theme for theme in prevalence(grid, sources)}
    assert "common-but-passing" in by_code["delivery-late"]["flags"], by_code["delivery-late"]
    assert "rare-but-blocking" in by_code["no-invoice"]["flags"], by_code["no-invoice"]
    out.append("twelve mentions nobody minded is common-but-passing; one that stopped a purchase "
               "is rare-but-blocking, and they are not ranked against each other")

    # Storing the text of a private message is a rights problem, not a research one, and the table
    # already knows which sources are unquotable.
    leak = [{"respondent_id": "r1", "sequence": "1", "source_id": "support-tickets",
             "code": "packaging-damaged", "stance": "raised", "intensity": "blocking",
             "provenance": "2026-07-02 ticket 41", "verbatim": "hộp bị bẹp, giao lại giúp em"}]
    by_gate = {result["gate"]: result["status"] for result
               in gates(leak, sources, saturation(leak), prevalence(leak, sources),
                        heard_per_source(leak, sources))}
    assert by_gate["stored-quote-rights"] == "failed", by_gate
    clean = [dict(row, verbatim="") for row in leak]
    by_gate = {result["gate"]: result["status"] for result
               in gates(clean, sources, saturation(clean), prevalence(clean, sources),
                        heard_per_source(clean, sources))}
    assert by_gate["stored-quote-rights"] == "passed", by_gate
    out.append("pasting a support ticket's own words into the research file fails the rights gate; "
               "coding it without the text passes")

    # The headcount floor belongs to the source, so it is reported once and not per theme.
    thin = heard_per_source(leak, sources)
    assert thin[0]["status"] == "below-floor" and thin[0]["floor"] == 25, thin
    survey = [dict(row, source_id="customer-survey") for row in leak]
    assert heard_per_source(survey, sources)[0]["status"] == "no-headcount-floor"
    out.append("one ticket is below the support floor of 25; a survey has no headcount floor to be "
               "below, because its floor is an interval width")

    example = Path(__file__).resolve().parent.parent / "assets" / "examples" / \
        "customer-evidence-coded.csv"
    if example.exists():
        report = check(example)
        assert report["verdict"] in {"passed", "review"}, report["verdict"]
        by_gate = {result["gate"]: result["status"] for result in report["gates"]}
        assert by_gate["provenance-recorded"] == "passed", by_gate
        assert by_gate["known-source"] == "passed", by_gate
        assert by_gate["input-vocabulary"] == "passed", by_gate
        out.append(f"the shipped example reads clean and lands on {report['verdict']}")

    return ("evidence saturation self-check passed:\n"
            + "\n".join(f"  - {line}" for line in out) + "\n")


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="Decide whether customer research has heard enough, and what its numbers may say.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", metavar="FILE", help="a coded-verbatim CSV")
    mode.add_argument("--sources", action="store_true", help="print the source table")
    mode.add_argument("--interval", nargs=2, metavar=("N", "SHARE"),
                      help="the 95 percent interval around an observed share")
    mode.add_argument("--needed", nargs=2, metavar=("SHARE", "WIDTH"),
                      help="respondents needed for an interval of that width")
    mode.add_argument("--self-check", action="store_true", help="run the built-in assertions")
    parser.add_argument("--query", help="filter --sources")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    parser.add_argument("--out", metavar="FILE", help="write here instead of stdout")
    args = parser.parse_args(argv)

    if args.self_check:
        emit(self_check(), args.out)
        return 0
    if args.sources:
        emit(print_sources(args.query), args.out)
        return 0
    if args.interval:
        try:
            total, share = int(args.interval[0]), float(args.interval[1])
        except ValueError:
            emit("--interval takes a whole number of respondents and a share between 0 and 1\n")
            return 1
        if total <= 0 or not 0.0 <= share <= 1.0:
            emit("--interval needs N above zero and SHARE between 0 and 1\n")
            return 1
        emit(print_interval(total, share), args.out)
        return 0
    if args.needed:
        try:
            share, width = float(args.needed[0]), float(args.needed[1])
        except ValueError:
            emit("--needed takes a share and an interval width, both between 0 and 1\n")
            return 1
        if not 0.0 <= share <= 1.0 or not 0.0 < width <= 1.0:
            emit("--needed needs SHARE in 0..1 and WIDTH above 0\n")
            return 1
        emit(print_needed(share, width), args.out)
        return 0

    if not args.check:
        parser.print_help()
        return 1
    path = Path(args.check)
    if not path.exists():
        emit(f"no such file: {path}\n")
        return 1
    try:
        report = check(path)
    except ValueError as error:
        emit(f"{error}\n")
        return 1
    emit_json(report, args.out) if args.json else emit(as_text(report), args.out)
    return STATUS_EXIT[report["verdict"]]


if __name__ == "__main__":
    from _emit import run_gate
    run_gate(main)
