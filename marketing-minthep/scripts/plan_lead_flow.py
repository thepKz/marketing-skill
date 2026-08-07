#!/usr/bin/env python3
"""Grade how a business handles an inbound contact, and compute the funnel from first message to won.

Why this exists at all
----------------------
`vietnam-operating-reality.md` says the command surface is a graph over artefacts, that the inbox and
sales roles produce no artefact, and that they are therefore invisible to it - while being the two
roles that consume the most of the day. That was an honest description of a hole. It was also the
hole: the skill could plan a campaign that generates enquiries and had nothing to say about the
twenty messages the campaign produced on a Tuesday afternoon.

This script closes it by making the handling itself the artefact. A lead process is not words, so
there is nothing to scan - it is a set of decisions about who is worth answering, how fast, how many
times, and what gets written down when the answer is no. So the input is a declaration, the same
shape `plan_lifecycle.py` uses, for the same reason.

What is declared rather than asserted, and why nothing here is imported
----------------------------------------------------------------------
Every response-time number in circulation traces to one of two places: Oldroyd's lead-response study
and the vendor benchmark reports that cite it. That work was measured on business-to-business web
forms answered by telephone in the United States. This corpus has no measurement of chat commerce in
Vietnam, and the retrieval attempt for platform-published response thresholds - Shopee's chat
response rate, the Meta responsiveness badge, Zalo OA reply windows - returned nothing verifiable on
the retrieval date. So no first-response target is shipped here.

`lifecycle-retention.md` already set this precedent for send frequency: an imported rule of thumb
about two sends a week is a deliverability opinion wearing a legal coat. A five-minute reply target
would be the same opinion wearing a stopwatch. The operator declares the target, the script holds
them to what they declared, and the report says plainly that the number is theirs and is certified by
nothing. A tool that invented a target would be measuring compliance with a guess.

The two gates worth reading
---------------------------
  price without a gap      `price` is the loss reason people give, because it ends the conversation
                           politely, and the reason sellers record, because it blames nobody in the
                           room. A loss log where price dominates is usually a log that stopped
                           asking. So declaring price requires the gap and what else was true. This
                           is a house-rule caution, not a cited finding, and the report says so.
  a rate with no base      A stage rate computed on eleven contacts is not a rate. Below the floor
                           the script prints the count and the interval and refuses the point
                           estimate, because 2 of 3 reported as 67% is how a small week becomes a
                           strategy. The interval is Wilson, which does not collapse to zero width
                           when the numerator does.

And one refusal: whether you may contact a silent person again is a legal question about stored
personal data and repeat contact, which `lifecycle-duties.csv` answers and this script does not. It
counts the touches and names the file.

Usage:
    python scripts/plan_lead_flow.py --states
    python scripts/plan_lead_flow.py --states --state lost
    python scripts/plan_lead_flow.py --template sheet.csv
    python scripts/plan_lead_flow.py --audit sheet.csv
    python scripts/plan_lead_flow.py --funnel counts.csv
    python scripts/plan_lead_flow.py --funnel counts.csv --json

Exit codes are 0 clean, 1 usage error, 2 a gate failed, 3 computable but unsettled.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

STATES_CSV = Path(__file__).resolve().parents[1] / "data" / "lead-states.csv"

COLUMNS = ("id", "state_vi", "state_en", "entry_moment", "exit_criterion", "exits_to",
           "stall_exits_to", "declared_field", "may_be_counted", "may_not_be_counted",
           "vn_channel_note", "what_it_does_not_prove")

# The order a contact actually moves through. Terminal and branch states sit outside it.
FUNNEL_ORDER = ("new", "replied", "qualified", "quoted", "negotiating", "won")
TERMINAL = ("won", "lost", "disqualified", "stalled")

# Below this denominator a share is reported as a count and an interval, never as a percentage.
RATE_FLOOR = 30

# Channels an inbound contact actually arrives on here. The last two cannot be exported.
VN_CHANNELS = ("zalo", "messenger", "facebook-comment", "instagram-dm", "tiktok-dm", "phone",
               "web-form", "walk-in", "shopee-chat", "tiktok-shop-chat")
UNEXPORTABLE = ("shopee-chat", "tiktok-shop-chat")

PRICE_TOKENS = ("price", "gia", "giá", "expensive", "dat", "đắt", "cost")

# field, prompt, why it is asked. Blank fails its gate: silence is not an answer.
DECLARED = (
    ("contact_channels", "Which channels an enquiry arrives on, semicolon separated",
     "Decides what can be counted at all. Two of them cannot be exported"),
    ("manual_tally", "yes or no - do you tally marketplace chat by hand",
     "Marketplace chat has no export, so without a tally it drops out of every rate silently"),
    ("first_response_target_minutes", "Your target minutes to a human reply, in business hours",
     "Yours to choose. Nothing in this corpus certifies a number, and this script does not supply one"),
    ("business_hours", "The hours the target applies inside, e.g. 08:00-20:00 Mon-Sat",
     "A target with no hours is a target that fails every night and teaches nothing"),
    ("reply_is_human_written", "yes or no - is the first reply written or approved by a person",
     "An auto-greeting satisfies a platform response metric without answering anybody"),
    ("fit_criteria", "At least two criteria that make an enquiry worth your hours, semicolon separated",
     "Without written criteria, qualification is mood, and disqualification feels like giving up"),
    ("intent_signal", "What in the thread tells you they mean to buy",
     "Fit and intent are different axes. A perfect fit with no intent is a newsletter subscriber"),
    ("disqualify_reason_list", "The reasons you will record for a bad fit, semicolon separated",
     "A disqualification with no recorded reason cannot tell you your targeting is wrong"),
    ("touches_max", "How many follow-ups you send before stopping",
     "Yours to choose. The widely repeated touch counts trace to vendor content, not to evidence"),
    ("touch_gaps_hours", "Hours between follow-ups, semicolon separated, one per touch",
     "A ladder with no gaps is a burst, and a burst is what Điều 10.1.b is about"),
    ("stop_rule", "What ends the ladder besides running out of touches",
     "Without a stop rule the ladder ends when you get bored, which is not a rule"),
    ("quote_in_writing", "yes or no - is the scope written beside the price",
     "A price quoted in chat with no scope beside it is a scope argument scheduled for later"),
    ("quote_expires", "How long a quote stands, e.g. 7 days",
     "A quote that never expires cannot be followed up without inventing a reason"),
    ("loss_reason_list", "The loss reasons you will record, semicolon separated",
     "A free-text loss log converges on price and stops being readable"),
    ("who_answers", "Who actually answers the inbox",
     "plan_operating_load.py counts this person's week. Naming them here is what connects the two"),
)

REQUIRED_ON_LOSS = ("loss_reason", "loss_reason_evidence")


def load_states(path: Path = STATES_CSV) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing data table: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"empty data table: {path}")
    missing = [c for c in COLUMNS if c not in rows[0]]
    if missing:
        raise SystemExit(f"{path} is missing columns: {', '.join(missing)}")
    return rows


def wilson(hits: int, base: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson interval. Does not collapse to zero width when hits is 0 or equals base."""
    if base <= 0:
        return (0.0, 0.0)
    p = hits / base
    denom = 1 + z * z / base
    centre = (p + z * z / (2 * base)) / denom
    half = z * math.sqrt(p * (1 - p) / base + z * z / (4 * base * base)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def render_states(rows: list[dict[str, str]], only: str | None) -> str:
    picked = [r for r in rows if only is None or r["id"] == only]
    if not picked:
        ids = ", ".join(r["id"] for r in rows)
        raise SystemExit(f"unknown state: {only}. Known: {ids}")
    out = ["# Lead states\n"]
    for row in picked:
        out.append(f"\n## {row['id']} - {row['state_vi']} ({row['state_en']})\n")
        out.append(f"Enters when   {row['entry_moment']}\n")
        out.append(f"Leaves when   {row['exit_criterion']}\n")
        nxt = row["exits_to"] if row["exits_to"] != "-" else "terminal"
        stall = row["stall_exits_to"] if row["stall_exits_to"] != "-" else "n/a"
        out.append(f"Goes to       {nxt}   (on stall: {stall})\n")
        if row["declared_field"] != "-":
            out.append(f"Declares      {row['declared_field']}\n")
        out.append(f"May count     {row['may_be_counted']}\n")
        out.append(f"May not count {row['may_not_be_counted']}\n")
        out.append(f"Vietnam       {row['vn_channel_note']}\n")
        out.append(f"Not proof of  {row['what_it_does_not_prove']}\n")
    if only is None:
        out.append(f"\nFunnel order: {' -> '.join(FUNNEL_ORDER)}\n")
        out.append(f"Terminal states: {', '.join(TERMINAL)}\n")
    return "".join(out)


def write_template(path: Path) -> str:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("field", "value", "why_it_is_asked"))
        for field, prompt, why in DECLARED:
            writer.writerow((field, f"WRITE: {prompt}", why))
        for field in REQUIRED_ON_LOSS:
            writer.writerow((field, "WRITE: only if you are declaring a specific lost deal",
                             "Declaring price as the reason requires the gap and what else was true"))
    return (f"Wrote {len(DECLARED) + len(REQUIRED_ON_LOSS)} questions to {path}\n"
            "Fill every value, then run --audit on the same file.\n"
            "A blank value fails its gate. Silence is not an answer.\n")


def read_sheet(path: Path) -> dict[str, str]:
    # utf-8-sig, not utf-8: Excel and PowerShell both write a BOM, which otherwise arrives glued to
    # the first column name and the sheet gets rejected for a header it plainly has.
    if not path.exists():
        raise SystemExit(f"no such sheet: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or "field" not in rows[0] or "value" not in rows[0]:
        raise SystemExit(f"{path} needs a header with at least: field,value")
    return {r["field"].strip(): (r.get("value") or "").strip() for r in rows}


def _blank(value: str) -> bool:
    return value == "" or value == "-" or value.upper().startswith("WRITE:")


def _as_int(value: str) -> int | None:
    try:
        return int(value.strip())
    except (ValueError, AttributeError):
        return None


def audit(sheet: dict[str, str]) -> tuple[list[tuple[str, str, str]], int]:
    """Return (gate, verdict, message) rows and the worst exit code.

    Severity and exit code are deliberately separate. Ranked, a failure outranks a review; as exit
    codes, unsettled is 3 and failed is 2, so taking max() over the codes would let one review hide
    every failure on the sheet. Rank first, translate once.
    """
    results: list[tuple[str, str, str]] = []
    rank = 0
    RANK = {"passed": 0, "review": 1, "failed": 2}

    def record(gate: str, verdict: str, message: str) -> None:
        nonlocal rank
        results.append((gate, verdict, message))
        rank = max(rank, RANK[verdict])

    for field, prompt, _why in DECLARED:
        if _blank(sheet.get(field, "")):
            record(field, "failed", f"not declared. {prompt}")

    channels = [c.strip().lower() for c in sheet.get("contact_channels", "").split(";") if c.strip()]
    if channels:
        unknown = [c for c in channels if c not in VN_CHANNELS]
        if unknown:
            record("channels-known", "review",
                   f"not in the table: {', '.join(unknown)}. Known: {', '.join(VN_CHANNELS)}")
        blind = [c for c in channels if c in UNEXPORTABLE]
        if blind and sheet.get("manual_tally", "").strip().lower() != "yes":
            record("marketplace-tallied", "failed",
                   f"{', '.join(blind)} declared with no manual tally. Marketplace chat has no "
                   "export, so those contacts are missing from every rate below and the funnel "
                   "will read as a collapse that did not happen")

    target = _as_int(sheet.get("first_response_target_minutes", ""))
    if target is not None:
        if target <= 0:
            record("response-target", "failed", "a target must be a positive number of minutes")
        else:
            record("response-target", "review",
                   f"{target} minutes is your declared target. Nothing in this corpus certifies a "
                   "number, so this is recorded and not graded. Read your own platform dashboard "
                   "for what the surface measures you on")
    elif not _blank(sheet.get("first_response_target_minutes", "")):
        record("response-target", "failed", "not a whole number of minutes")

    if sheet.get("reply_is_human_written", "").strip().lower() == "no":
        record("reply-is-human", "review",
               "an auto-greeting satisfies a platform response metric without answering anybody. "
               "The metric will improve and the conversation will not")

    fit = [c for c in sheet.get("fit_criteria", "").split(";") if c.strip()]
    if fit and len(fit) < 2:
        record("fit-criteria", "failed",
               "one criterion is a preference. Two or more is a rule you can apply on a bad day")

    touches = _as_int(sheet.get("touches_max", ""))
    gaps = [g for g in sheet.get("touch_gaps_hours", "").split(";") if g.strip()]
    if touches is not None and gaps:
        if touches != len(gaps):
            record("ladder-shape", "failed",
                   f"{touches} touches declared but {len(gaps)} gaps. One gap per touch")
        else:
            bad = [g for g in gaps if _as_int(g) is None or (_as_int(g) or 0) <= 0]
            if bad:
                record("ladder-shape", "failed", f"gaps must be positive hours: {', '.join(bad)}")
            else:
                span = sum(_as_int(g) or 0 for g in gaps)
                record("ladder-shape", "passed",
                       f"{touches} touches over {span} hours ({span / 24:.1f} days). Whether you may "
                       "send them at all is Điều 10.1.b - see lifecycle-duties.csv, not this script")
    if touches is not None and touches > 0 and _blank(sheet.get("stop_rule", "")):
        record("stop-rule", "failed", "a ladder with no stop rule ends when you get bored")

    reason = sheet.get("loss_reason", "").strip().lower()
    if reason and not _blank(reason):
        if any(token in reason for token in PRICE_TOKENS):
            if _blank(sheet.get("loss_reason_evidence", "")):
                record("price-loss-has-evidence", "failed",
                       "price declared as the loss reason with no evidence. Record the gap and what "
                       "else was true. Price is the reason buyers give because it ends the "
                       "conversation politely and the reason sellers record because it blames nobody "
                       "in the room - a house-rule caution, not a cited finding")
            else:
                record("price-loss-has-evidence", "passed", "price declared with the gap beside it")

    if not results:
        record("sheet", "passed", "every declared field present")
    return results, {0: 0, 1: 3, 2: 2}[rank]


def read_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        raise SystemExit(f"no such counts file: {path}")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or "state" not in rows[0] or "count" not in rows[0]:
        raise SystemExit(f"{path} needs a header: state,count")
    counts: dict[str, int] = {}
    for row in rows:
        state = (row["state"] or "").strip()
        value = _as_int(row.get("count") or "")
        if value is None or value < 0:
            raise SystemExit(f"count for {state!r} is not a non-negative whole number")
        counts[state] = value
    return counts


def funnel(counts: dict[str, int]) -> tuple[dict[str, object], int]:
    known = {r["id"] for r in load_states()}
    unknown = [s for s in counts if s not in known]
    if unknown:
        raise SystemExit(f"unknown states: {', '.join(sorted(unknown))}. "
                         f"Known: {', '.join(sorted(known))}")
    # Rank, not exit code: an impossible count must not be hidden by a too-small base. See audit().
    rank = 0
    steps: list[dict[str, object]] = []
    present = [s for s in FUNNEL_ORDER if s in counts]
    for earlier, later in zip(present, present[1:]):
        base, hits = counts[earlier], counts[later]
        step: dict[str, object] = {"from": earlier, "to": later, "base": base, "hits": hits}
        if hits > base:
            step["verdict"] = "impossible"
            step["note"] = (f"{hits} in {later} from {base} in {earlier}. A later state cannot hold "
                            "more than the one it is entered from. Either the tally is wrong or the "
                            "marketplace contacts were never counted at the top")
            rank = max(rank, 2)
        elif base < RATE_FLOOR:
            low, high = wilson(hits, base)
            step["verdict"] = "too-few"
            step["rate"] = None
            step["interval"] = [round(low, 3), round(high, 3)]
            step["note"] = (f"{hits} of {base}. Below {RATE_FLOOR} the share is not reported as a "
                            f"percentage. The true rate sits somewhere in {low:.0%} to {high:.0%}, "
                            "which is usually wide enough to contain both a good week and a bad one")
            rank = max(rank, 1)
        else:
            low, high = wilson(hits, base)
            step["verdict"] = "measured"
            step["rate"] = round(hits / base, 4)
            step["interval"] = [round(low, 3), round(high, 3)]
            step["note"] = f"{hits} of {base}"
        steps.append(step)

    overall: dict[str, object] = {}
    if "new" in counts and "won" in counts:
        base, hits = counts["new"], counts["won"]
        if hits > base:
            overall = {"verdict": "impossible", "base": base, "hits": hits}
            rank = max(rank, 2)
        else:
            low, high = wilson(hits, base)
            overall = {"base": base, "hits": hits, "interval": [round(low, 3), round(high, 3)],
                       "verdict": "measured" if base >= RATE_FLOOR else "too-few",
                       "rate": round(hits / base, 4) if base >= RATE_FLOOR else None}
            if base < RATE_FLOOR:
                rank = max(rank, 1)

    worst_step = None
    measured = [s for s in steps if s["verdict"] == "measured"]
    if measured:
        worst_step = min(measured, key=lambda s: s["rate"])  # type: ignore[arg-type,return-value]

    return ({"steps": steps, "overall": overall,
             "biggest_measured_drop": worst_step["from"] if worst_step else None,
             "rate_floor": RATE_FLOOR}, {0: 0, 1: 3, 2: 2}[rank])


def render_funnel(report: dict[str, object]) -> str:
    out = ["# Funnel, first message to won\n\n"]
    out.append("| From | To | Base | Reached | Rate | 95% interval | Verdict |\n")
    out.append("|---|---|---|---|---|---|---|\n")
    for step in report["steps"]:  # type: ignore[union-attr]
        rate = step.get("rate")
        shown = f"{rate:.1%}" if isinstance(rate, float) else "-"
        interval = step.get("interval")
        band = f"{interval[0]:.0%} to {interval[1]:.0%}" if interval else "-"
        out.append(f"| {step['from']} | {step['to']} | {step['base']} | {step['hits']} | "
                   f"{shown} | {band} | {step['verdict']} |\n")
    out.append("\n")
    for step in report["steps"]:  # type: ignore[union-attr]
        if step["verdict"] != "measured":
            out.append(f"{step['from']} -> {step['to']}: {step['note']}\n")
    overall = report.get("overall") or {}
    if overall:
        rate = overall.get("rate")
        shown = f"{rate:.1%}" if isinstance(rate, float) else "not reported"
        out.append(f"\nContact to won: {overall.get('hits')} of {overall.get('base')} = {shown}")
        interval = overall.get("interval")
        if interval:
            out.append(f" (95%: {interval[0]:.0%} to {interval[1]:.0%})")
        out.append("\n")
    if report.get("biggest_measured_drop"):
        out.append(f"Biggest measured drop leaves: {report['biggest_measured_drop']}\n")
    out.append("\nNo lead value is computed. tracking-events.csv refuses one unless a verified "
               "average exists, and inventing it is how an assumption becomes a reported number.\n")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="Grade inbound lead handling and compute the funnel from first message to won.")
    parser.add_argument("--states", action="store_true", help="print the state map")
    parser.add_argument("--state", help="print one state only")
    parser.add_argument("--template", help="write the declaration sheet to this path")
    parser.add_argument("--audit", help="grade a filled declaration sheet")
    parser.add_argument("--funnel", help="a CSV of state,count")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)


    if args.states or args.state:
        rows = load_states()
        if args.json:
            picked = [r for r in rows if args.state is None or r["id"] == args.state]
            emit_json(picked)
        else:
            emit(render_states(rows, args.state))
        return 0

    if args.template:
        emit(write_template(Path(args.template)))
        return 0

    if args.audit:
        results, code = audit(read_sheet(Path(args.audit)))
        if args.json:
            emit_json({"gates": [{"gate": g, "verdict": v, "message": m} for g, v, m in results],
                       "exit_code": code})
        else:
            out = ["# Lead handling audit\n\n"]
            for gate, verdict, message in results:
                out.append(f"[{verdict}] {gate}\n    {message}\n")
            counts = {v: sum(1 for _g, vv, _m in results if vv == v)
                      for v in ("passed", "review", "failed")}
            out.append(f"\npassed {counts['passed']}, review {counts['review']}, "
                       f"failed {counts['failed']}\n")
            emit("".join(out))
        return code

    if args.funnel:
        report, code = funnel(read_counts(Path(args.funnel)))
        emit_json(report) if args.json else emit(render_funnel(report))
        return code

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
