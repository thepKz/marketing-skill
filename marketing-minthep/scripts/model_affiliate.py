#!/usr/bin/env python3
"""Work out what an affiliate commission rate actually pays, and when the cash arrives.

`creator-ugc.md` had one sentence about affiliates - the word appears once, in a list of relationship
types - and the skill could plan a creator campaign without ever asking what the creator gets paid.
That gap matters more in Vietnam than anywhere else in this repo, because affiliate is not a side
channel here: it is how a large share of marketplace demand is generated, and the numbers governing it
are published in Vietnamese on Shopee's help centre and almost never read.

A quoted commission rate is not income. Between the rate on the offer and the money in the account sit
four deductions and a delay, and every one of them is documented:

  settled value  = attributed value x (1 - return rate)      returns void the commission retroactively
  gross          = settled value x commission rate
  after fee      = gross x (1 - service fee)                 0.98 percent, offset at reconciliation
  net            = after fee - withholding                   10 percent, at or above 250000 VND a payment
  cash           = net, days_to_cash working days later      a receivable, not revenue

Run it on a plausible creator deal and the headline rate loses about a fifth of itself before the delay
is even counted. The delay is the part that ends businesses: a company partner's order in early month T
is statemented at month end, reconciled within 10 working days of that, and paid within roughly 30
working days of complete documents - a receivable near a quarter long, funded by the creator.

Three things here are worth more than the total.

**The return rate is refused rather than defaulted.** Definition 1.4 of the seller programme terms
excludes cancelled orders, refused deliveries and returns, and says Shopee need not explain any
individual decision. So a model without a return rate is not optimistic, it is arithmetically wrong by
exactly the rate, and there is no honest default to supply. It has to come from the partner's own
reconciliation reports.

**The withholding notch.** Ten percent is withheld on any single payment at or above 250000 VND, and it
is withheld on the whole payment rather than the excess. So a payment of 250000 nets 225000 while a
payment of 249999 nets 249999, and every payment between 250000 and 277778 nets less than one just
below the floor. The band is small money and it lands precisely on the beginner whose per-payment
earnings sit at the floor - the reader this skill is written for. `--notch` prints it.

**Which window is being modelled.** The creator programme gives the buyer 7 days from the click. The
seller programme's own definitions give 30 days for a successful order and 7 days of cookie retention,
in the same document, unreconciled. A forecast that does not say which one it assumed has not made an
assumption, it has hidden one, so the window is a required input and it is gated.

Bounds are the minimum and maximum over the corners of the input intervals. That is exact wherever the
model is monotone in each parameter, and the one place it is not - the withholding step - can only
understate the maximum, by at most the notch, which is reported on its own line. The centre is the
model evaluated at each input's own centre rather than the centre of the output range. That is a
deliberate difference from `size_market.py`, where the output is a pure product and its middle is the
geometric mean: here the output includes a difference and a step, so no closed-form centre exists and
the base case is the model run on the middle of every input.

Every number it checks against is published. Sources are in `data/affiliate-mechanics.csv`, one row per
fact with the article it came from, and the constants below restate them so the script stands alone.

    python scripts/model_affiliate.py --check deal.csv --side creator
    python scripts/model_affiliate.py --check deal.csv --side seller --floor 40000000
    python scripts/model_affiliate.py --check deal.csv --side creator --as-of 2026-07-31 --json
    python scripts/model_affiliate.py --template deal.csv
    python scripts/model_affiliate.py --mechanics
    python scripts/model_affiliate.py --notch
    python scripts/model_affiliate.py --self-check

Exit codes are 0 clean, 1 usage error, 2 a gate failed, 3 computable but unsettled.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

COLUMNS = ("parameter", "low", "high", "unit", "source_url", "verified_at", "what_it_measures")

# Shopee's service fee on everything a partner earns, VAT included, offset at reconciliation rather
# than invoiced. 0.98 percent from the 16-31 July 2025 period; the 1 percent version is still live on
# its own URL with no superseded label, which is why both are checked rather than one assumed.
# help.shopee.vn/portal/10/article/174381 and .../187147
SERVICE_FEE_CURRENT = 0.0098
SERVICE_FEE_SUPERSEDED = 0.01
SERVICE_FEE_FROM = "2025-07-16"

# Personal income tax withheld at source from individual partners. The rate comes from Thong tu
# 111/2013/TT-BTC Article 25.1(i) and has not moved; the threshold did, from 2000000 VND a payment to
# 250000, announced for 20 November 2025 because payment frequency went to twice a week. Shopee's own
# tax explainer still states the old threshold, so a model carrying it is following a stale page on the
# same host. help.shopee.vn/portal/10/article/196407 and .../163104
WITHHOLDING_RATE = 0.10
WITHHOLDING_FLOOR_CURRENT = 250_000.0
WITHHOLDING_FLOOR_SUPERSEDED = 2_000_000.0
WITHHOLDING_FLOOR_FROM = "2025-11-20"

# Below this Shopee reserves the right to hold the payment, including on a locked account. Seller
# programme terms, payment section. help.shopee.vn/portal/10/article/171010
MINIMUM_PAYOUT = 10_000.0

# The two documented windows, in days. 7 is the creator programme: the buyer must order within 7 days
# of clicking that creator's own link. 30 is definition 1.4 of the seller programme, whose definition
# 1.2 sets cookie retention at 7 in the same document without reconciling the two. Both are kept
# because a model must declare which one it used, and neither is a safe default for the other side.
# help.shopee.vn/portal/10/article/122941 and .../171010
DOCUMENTED_WINDOWS = {7: "creator programme: buyer orders within 7 days of clicking that creator's link",
                      30: "seller programme definition 1.4, alongside 7-day cookie retention in 1.2"}

# At or above 20 percent violating orders in one month, or across 3 months consecutive or not since
# approval, Shopee may lock the affiliate account and the Shopee account with it. Below that it pays on
# the clean remainder. help.shopee.vn/portal/10/article/171010
VIOLATION_LOCK_SHARE = 0.20

# A URL read more than a year ago is a hypothesis, not a citation. Same constant and same reason as
# `size_market.py`; affiliate terms move faster than statistics, so this is the generous bound.
STALE_AFTER_DAYS = 365

# What each side must supply. A missing parameter is not a shorter model, it is that parameter silently
# set to its most flattering value, which is how affiliate forecasts get built.
SHARED = ("gmv", "commission_rate", "return_rate", "attribution_window_days", "days_to_cash")
CREATOR_ONLY = ("service_fee", "withholding_rate", "withholding_floor", "payments_in_period",
                "content_cost")
SELLER_ONLY = ("contribution_margin",)

PARAMETERS = {
    "gmv": "Attributed order value in the period, net of shipping and platform vouchers",
    "commission_rate": "Headline commission as a share, Shopee base plus Xtra where both apply",
    "return_rate": "Share of attributed orders cancelled, refused or returned. From your own "
                   "reconciliation reports; there is no honest default",
    "attribution_window_days": "Which documented window this models: 7 creator-side, 30 seller-side",
    "days_to_cash": "Working days from the order to money in the account, per your partner type",
    "service_fee": "Shopee's service fee on partner earnings, offset at reconciliation",
    "withholding_rate": "Personal income tax withheld at source from an individual partner",
    "withholding_floor": "Payment size at or above which withholding applies, per payment",
    "payments_in_period": "How many payments the period is split into. Cadence differs by partner type",
    "content_cost": "What producing the content cost: time at your own rate, samples, editing, media",
    "contribution_margin": "Contribution margin as a share of net order value, before commission",
}

# Which direction each parameter pushes the outcome. Used to name the driver of the spread; the bounds
# themselves come from enumerating corners, so a wrong sign here cannot corrupt a total.
DIRECTION = {"gmv": 1, "commission_rate": 1, "return_rate": -1, "service_fee": -1,
             "withholding_rate": -1, "withholding_floor": 1, "payments_in_period": 0,
             "content_cost": -1, "contribution_margin": 1, "attribution_window_days": 0,
             "days_to_cash": 0}


def required(side: str) -> tuple[str, ...]:
    extra = CREATOR_ONLY if side == "creator" else SELLER_ONLY
    return SHARED + extra


def read_deal(path: str | Path) -> list[dict]:
    text = Path(path).read_text(encoding="utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows:
        raise ValueError("the deal file has a header and no rows")
    missing = [c for c in COLUMNS if c not in (rows[0].keys() or ())]
    if missing:
        raise ValueError("the deal file is missing columns: " + ", ".join(missing))
    return rows


def parse_deal(rows: list[dict]) -> dict:
    """Turn CSV rows into {parameter: {low, high, ...}}, refusing anything unparseable."""
    parsed = {}
    for index, row in enumerate(rows, start=2):
        name = (row.get("parameter") or "").strip()
        if not name:
            continue
        if name not in PARAMETERS:
            raise ValueError(f"line {index}: {name} is not a parameter this model knows. "
                             f"Known: {', '.join(sorted(PARAMETERS))}")
        try:
            low = float((row.get("low") or "").strip())
            high = float((row.get("high") or "").strip())
        except ValueError:
            raise ValueError(f"line {index}: low and high must both be numbers for {name}") from None
        if low > high:
            raise ValueError(f"line {index}: low is above high for {name}")
        parsed[name] = {"parameter": name, "low": low, "high": high,
                        "unit": (row.get("unit") or "").strip(),
                        "source_url": (row.get("source_url") or "").strip(),
                        "verified_at": (row.get("verified_at") or "").strip(),
                        "what_it_measures": (row.get("what_it_measures") or "").strip()}
    return parsed


def evaluate(side: str, values: dict) -> dict:
    """Run the model once, on one reading of every parameter."""
    settled = values["gmv"] * (1 - values["return_rate"])
    commission = settled * values["commission_rate"]
    if side == "creator":
        after_fee = commission * (1 - values["service_fee"])
        payments = max(1.0, values["payments_in_period"])
        per_payment = after_fee / payments
        withheld = after_fee * values["withholding_rate"] \
            if per_payment >= values["withholding_floor"] else 0.0
        net = after_fee - withheld - values["content_cost"]
        return {"settled": settled, "commission": commission, "after_fee": after_fee,
                "per_payment": per_payment, "withheld": withheld, "net": net,
                "take_rate": net / values["gmv"] if values["gmv"] else 0.0}
    contribution_before = settled * values["contribution_margin"]
    net = contribution_before - commission
    return {"settled": settled, "commission": commission, "contribution_before": contribution_before,
            "net": net, "take_rate": net / values["gmv"] if values["gmv"] else 0.0}


def compute(side: str, deal: dict) -> dict:
    """Bound the outcome over the corners of the inputs, and run the base case at their centres.

    An incomplete deal returns a result that says so rather than raising. The gate table is what the
    reader came for, and someone whose model is missing its return rate needs to be told which inputs
    are absent and why each one matters. Not a traceback, and above all not a total computed as though
    the missing input were zero.
    """
    missing = [n for n in required(side) if n not in deal]
    if missing:
        return {"side": side, "deal": deal, "computable": False, "missing": missing}
    names = [n for n in required(side) if n in deal]
    corners = []
    for picks in itertools.product(*[("low", "high") for _ in names]):
        values = {n: deal[n][p] for n, p in zip(names, picks)}
        corners.append(evaluate(side, values))
    centres = {n: (deal[n]["low"] + deal[n]["high"]) / 2 for n in names}
    centre = evaluate(side, centres)
    nets = [c["net"] for c in corners]
    return {"side": side, "deal": deal, "computable": True, "missing": [],
            "low": min(nets), "high": max(nets), "centre": centre["net"],
            "base": centre, "centres": centres, "corners": len(corners),
            "take_rate_low": min(c["take_rate"] for c in corners),
            "take_rate_high": max(c["take_rate"] for c in corners),
            "take_rate_centre": centre["take_rate"]}


def notch(floor: float = WITHHOLDING_FLOOR_CURRENT, rate: float = WITHHOLDING_RATE) -> dict:
    """The payment band where earning more nets less, because the whole payment gets withheld."""
    top = floor / (1 - rate)
    return {"floor": floor, "rate": rate, "top": top, "width": top - floor,
            "worst_net": floor * (1 - rate), "best_below": floor - 1}


def shares_of_spread(side: str, result: dict) -> list[dict]:
    """How much of the total spread each parameter is responsible for, one at a time."""
    deal, centres = result["deal"], dict(result["centres"])
    total = result["high"] - result["low"]
    rows = []
    for name in centres:
        if deal[name]["low"] == deal[name]["high"]:
            rows.append({"parameter": name, "share": 0.0})
            continue
        readings = []
        for pick in ("low", "high"):
            values = dict(centres)
            values[name] = deal[name][pick]
            readings.append(evaluate(side, values)["net"])
        rows.append({"parameter": name, "share": (max(readings) - min(readings)) / total
                     if total else 0.0})
    return sorted(rows, key=lambda r: -r["share"])


def resolve_against(side: str, result: dict, floor: float) -> dict:
    """Does the decision survive every reading, and if not, which input would settle it alone."""
    straddles = result["low"] <= floor <= result["high"]
    if not straddles:
        verdict = "above on every reading" if result["low"] > floor else "below on every reading"
        return {"floor": floor, "straddles": False, "verdict": verdict, "settled_by": []}
    settled = []
    for row in shares_of_spread(side, result):
        name = row["parameter"]
        if row["share"] == 0.0:
            continue
        deal, centres = result["deal"], dict(result["centres"])
        collapsed = {n: dict(deal[n]) for n in deal}
        collapsed[name] = dict(deal[name])
        collapsed[name]["low"] = collapsed[name]["high"] = centres[name]
        narrowed = compute(side, collapsed)
        if not (narrowed["low"] <= floor <= narrowed["high"]):
            settled.append({"parameter": name, "share": row["share"]})
    return {"floor": floor, "straddles": True, "verdict": "unresolved", "settled_by": settled}


def gates(side: str, result: dict, as_of: str) -> list[dict]:
    # Three of these gates read the model output and the rest read only the inputs, so an incomplete
    # deal still gets graded on everything that can be graded. Nothing is skipped silently: the three
    # report that they could not run, which is a failure and not a pass.
    deal, base = result["deal"], result.get("base") or {}
    rows = []

    def add(gate: str, ok: bool, severity: str, observed: str, target: str, why: str) -> None:
        rows.append({"gate": gate, "pass": ok, "severity": severity, "observed": observed,
                     "target": target, "why": why})

    absent = [n for n in required(side) if n not in deal]
    add("model-is-complete", not absent, "critical",
        "missing " + ", ".join(absent) if absent else f"all {len(required(side))} inputs present",
        ", ".join(required(side)),
        "A missing input is not a shorter model. It is that input set to whatever value makes the "
        "answer look best, chosen by omission rather than argued for.")

    unsourced = [n for n, p in deal.items()
                 if not p["source_url"].startswith("https://") or not p["verified_at"]]
    add("every-input-sourced", not unsourced, "critical",
        ", ".join(sorted(unsourced)) or "every input carries an https source and a date",
        "every input",
        "Platform terms change on a schedule nobody is told about, and half of these numbers moved in "
        "2025. An input without a URL and a date cannot be re-checked when the answer starts to drift.")

    stated = deal.get("return_rate")
    add("return-rate-is-stated", bool(stated) and stated["high"] > 0, "critical",
        f"{stated['low']:.1%} to {stated['high']:.1%}" if stated else "absent",
        "present and above zero, from your own reconciliation",
        "The programme terms void commission on cancelled, refused and returned orders and say Shopee "
        "need not justify any single decision. A model with no return rate is wrong by exactly the "
        "return rate, and there is no defensible default to fill in for you.")

    window = deal.get("attribution_window_days")
    known = bool(window) and int(window["low"]) in DOCUMENTED_WINDOWS \
        and window["low"] == window["high"]
    add("attribution-window-is-declared", known, "high",
        f"{int(window['low'])} days" if window and window["low"] == window["high"]
        else "absent or a range", f"one of {sorted(DOCUMENTED_WINDOWS)} days, as a point",
        "Seven days is the creator programme. Thirty is the seller programme's own definition of a "
        "successful order, sitting beside seven days of cookie retention in the same unreconciled "
        "document. A forecast that names neither has hidden an assumption rather than made one.")

    fee = deal.get("service_fee")
    fee_current = side != "creator" or (fee is not None
                                        and abs(fee["high"] - SERVICE_FEE_SUPERSEDED) > 1e-9)
    add("service-fee-is-the-current-one", fee_current, "high",
        f"{fee['high']:.2%}" if fee else "not applicable on this side",
        f"{SERVICE_FEE_CURRENT:.2%} from {SERVICE_FEE_FROM}",
        f"The {SERVICE_FEE_SUPERSEDED:.0%} version is still published on its own URL with no superseded "
        f"label, so it is the one a search finds. Small money, and it is the tell that the rest of the "
        f"model came off the same stale page.")

    floor = deal.get("withholding_floor")
    floor_current = side != "creator" or (floor is not None
                                          and floor["low"] <= WITHHOLDING_FLOOR_CURRENT)
    add("withholding-floor-is-the-current-one", floor_current, "high",
        f"{floor['low']:,.0f} VND" if floor else "not applicable on this side",
        f"{WITHHOLDING_FLOOR_CURRENT:,.0f} VND from {WITHHOLDING_FLOOR_FROM}",
        "The threshold fell from 2,000,000 VND to 250,000 because payments went to twice a week, and "
        "Shopee's own tax explainer was never updated. Carrying the old figure means the model expects "
        "no withholding on payments that all get withheld.")

    if side == "creator":
        # Two ways to fail, and they are different failures, so they get different explanations. An
        # unstated cost means the model has not been built. A negative low reading means it has been
        # built and it says the work loses money in a bad month.
        cost = deal.get("content_cost")
        ok = cost is not None and result["computable"] and result["low"] > 0
        if cost is None:
            seen, why = "no production cost stated", (
                "A creator model with no cost of content is not a model of a business, it is a model "
                "of free labour. The hours are the largest input and the only one fully under the "
                "creator's control, so leaving them out removes the decision this was built to make.")
        elif not result["computable"]:
            seen, why = "not computable yet", (
                "The cost is stated but other inputs are missing, so whether the work pays for itself "
                "is still unknown. Fill the gaps before quoting a rate to anyone.")
        else:
            seen, why = f"net {result['low']:,.0f} to {result['high']:,.0f} against a stated cost", (
                "On the low reading this work is done at a loss - the commission range and the return "
                "rate can combine to less than the cost of making the content, and that combination is "
                "what a bad month is. A deal that only pays on its favourable readings is a deal whose "
                "downside the creator is funding, so either the rate has to rise, the production hours "
                "have to fall, or the answer is no.")
        add("net-beats-the-cost-of-making-the-content", ok, "high", seen,
            "a stated production cost, and net above zero on every reading", why)
    else:
        margin = deal.get("contribution_margin")
        commission = deal.get("commission_rate")
        ok = bool(margin and commission) and commission["high"] < margin["low"]
        add("contribution-survives-commission", ok, "high",
            f"commission up to {commission['high']:.1%} against margin from {margin['low']:.1%}"
            if margin and commission else "margin or commission absent",
            "commission below margin on every reading",
            "Commission is a variable cost on a converted order, so it competes with contribution "
            "margin and not with a media budget. Funding Xtra above margin buys revenue that costs "
            "more than it brings, and it will keep doing so at scale without ever failing.")

    per_payment = base.get("per_payment")
    if side != "creator":
        seen = "not applicable on the seller side"
    elif per_payment is None:
        seen = "not computable yet"
    else:
        seen = f"{per_payment:,.0f} VND a payment"
    clears = side != "creator" or (per_payment is not None and per_payment >= MINIMUM_PAYOUT)
    add("payment-clears-the-minimum", clears, "medium", seen,
        f"at least {MINIMUM_PAYOUT:,.0f} VND",
        "Below the minimum Shopee reserves the right to hold the payment rather than roll it forward "
        "with any published guarantee, so a programme this small may simply never pay out.")

    band = notch()
    outside = side != "creator" or (per_payment is not None
                                    and not band["floor"] <= per_payment < band["top"])
    add("payment-outside-the-withholding-notch", outside, "medium", seen,
        f"below {band['floor']:,.0f} or at least {band['top']:,.0f} VND a payment",
        f"Ten percent is withheld on the whole payment rather than the excess, so every payment between "
        f"{band['floor']:,.0f} and {band['top']:,.0f} VND nets less than one a dong below the floor. "
        f"Fewer, larger payments or one fewer payment in the period both leave the band.")

    days = deal.get("days_to_cash")
    add("days-to-cash-is-modelled", bool(days) and days["high"] > 0, "medium",
        f"{days['low']:.0f} to {days['high']:.0f} working days" if days else "absent",
        "present, from your own partner type's cadence",
        "Affiliate income is a receivable. A company partner's order is statemented at month end, "
        "reconciled within 10 working days of that, and paid within about 30 working days of complete "
        "documents - which the partner funds. Calling it revenue is how a growing programme runs out "
        "of cash.")

    stale, as_of_date = [], dt.date.fromisoformat(as_of)
    for name, parameter in deal.items():
        try:
            verified = dt.date.fromisoformat(parameter["verified_at"])
        except ValueError:
            continue
        age = (as_of_date - verified).days
        if age > STALE_AFTER_DAYS:
            stale.append(f"{name} read {age} days ago")
    add("sources-are-not-stale", not stale, "medium",
        "; ".join(stale) or f"every input verified within {STALE_AFTER_DAYS} days",
        f"within {STALE_AFTER_DAYS} days",
        "Four of the numbers this model depends on changed during 2025, and the superseded versions are "
        "still live on their own URLs with no label saying so. A year-old reading is a guess about a "
        "page.")

    points = [n for n in ("commission_rate", "return_rate")
              if n in deal and deal[n]["low"] == deal[n]["high"]]
    add("the-uncertain-inputs-are-ranges", not points, "medium",
        ", ".join(points) or "commission and returns both carry ranges",
        "commission_rate and return_rate as ranges",
        "Commission is set by algorithm and changes without notice, and a return rate is an average of "
        "a distribution. Entering either as one number asserts a precision the platform does not offer "
        "and your own reports do not support.")

    return rows


def blocking(gate_rows: list[dict]) -> int:
    return sum(1 for row in gate_rows
               if not row["pass"] and row["severity"] in ("critical", "high"))


def group(value: float) -> str:
    return f"{value:,.0f}"


def render_resolution(resolution: dict) -> list[str]:
    floor = group(resolution["floor"])
    if not resolution["straddles"]:
        return ["## Against the decision floor", "",
                f"The floor is {floor} and the outcome is **{resolution['verdict']}**. The deal is "
                f"decided. Nothing you could pin down more precisely changes which way it goes, and "
                f"that is the only kind of finished this question has.", ""]
    lines = ["## Against the decision floor", "",
             f"The floor is {floor} and the range contains it, so **the model has not decided "
             f"anything**. Both answers are live, and a document quoting the base case here is hiding "
             f"that.", ""]
    if resolution["settled_by"]:
        lines.append("Collapsing any one of these to its own centre would settle it on its own:")
        lines.append("")
        for row in resolution["settled_by"]:
            lines.append(f"- `{row['parameter']}` - {row['share']:.0%} of the spread")
        lines.append("")
        lines.append("Anything not on that list cannot move the outcome however precisely you pin it "
                     "down. That is usually where the next hour goes.")
    else:
        lines.append("No single input settles it, because the floor sits on the centre of your own "
                     "range. Collapsing any input to its centre leaves the centre where it was, so "
                     "there is no measurement that resolves this - the decision is balanced on a "
                     "guess, and it needs a different question rather than better numbers.")
    lines.append("")
    return lines


def render_refusal(side: str, result: dict, gate_rows: list[dict], as_of: str) -> str:
    """No totals, because there is no model yet. Say which inputs are missing and what each one is."""
    lines = [f"# Affiliate model, {side} side - not computable", "",
             f"As of {as_of}. {len(result['missing'])} of the "
             f"{len(required(side))} inputs this side needs are absent, so there is no number to print. "
             f"Filling them with defaults would produce a total, and the total would be a guess wearing "
             f"a decimal point.", "",
             "## What is missing", "", "| Input | What it is |", "| --- | --- |"]
    for name in result["missing"]:
        lines.append(f"| `{name}` | {PARAMETERS[name]} |")
    lines += ["", render_gate_table(gate_rows)]
    return "\n".join(lines)


def render_gate_table(gate_rows: list[dict]) -> str:
    lines = ["## Gates", "", "| Gate | Verdict | Observed | Target |", "| --- | --- | --- | --- |"]
    for row in gate_rows:
        mark = "pass" if row["pass"] else f"**FAIL ({row['severity']})**"
        lines.append(f"| `{row['gate']}` | {mark} | {row['observed']} | {row['target']} |")
    lines.append("")
    failed = [r for r in gate_rows if not r["pass"]]
    if failed:
        lines += ["## Why each failure matters", ""]
        for row in failed:
            lines += [f"**`{row['gate']}`** ({row['severity']}) - {row['why']}", ""]
    count = blocking(gate_rows)
    lines += [f"{count} blocking gate{'' if count == 1 else 's'} "
              f"(critical or high) out of {len(gate_rows)}.", ""]
    return "\n".join(lines)


def render(side: str, result: dict, gate_rows: list[dict], as_of: str,
           resolution: dict | None) -> str:
    if not result["computable"]:
        return render_refusal(side, result, gate_rows, as_of)
    base = result["base"]
    lines = [f"# Affiliate model, {side} side", "",
             f"As of {as_of}. Bounds are the extremes over {result['corners']} corners of the inputs; "
             f"the base case is the model run at every input's own centre.", "",
             "## What arrives", "",
             "| | Low | Base | High |", "| --- | --- | --- | --- |",
             f"| Net | {group(result['low'])} | {group(result['centre'])} | "
             f"{group(result['high'])} |",
             f"| Share of attributed value | {result['take_rate_low']:.2%} | "
             f"{result['take_rate_centre']:.2%} | {result['take_rate_high']:.2%} |", ""]

    # The two sides get different sentences here because the same ratio means different things. A
    # creator's take rate is directly comparable to the rate they were quoted, so the gap between them
    # is the whole point. A seller's is contribution over attributed value, which has nothing to do
    # with the commission rate - their question is how much of the contribution the commission eats.
    quoted = result["centres"].get("commission_rate")
    if quoted and side == "creator":
        lines += [f"The offer says {quoted:.2%}. At the base case {result['take_rate_centre']:.2%} of "
                  f"attributed value becomes money, which is "
                  f"{1 - result['take_rate_centre'] / quoted:.0%} less than the rate on the offer.", ""]
    elif quoted and base["contribution_before"] > 0:
        lines += [f"Commission takes {base['commission'] / base['contribution_before']:.0%} of the "
                  f"contribution these orders generate, leaving {group(base['net'])} to cover "
                  f"everything else. That share is the number to argue about when Shopee raises the "
                  f"Xtra rate, not the rate itself.", ""]

    lines += ["## Where it goes", "", "| Step | Amount |", "| --- | --- |",
              f"| Attributed value | {group(result['centres']['gmv'])} |",
              f"| Settled after returns | {group(base['settled'])} |",
              f"| Commission at the quoted rate | {group(base['commission'])} |"]
    if side == "creator":
        lines += [f"| After the service fee | {group(base['after_fee'])} |",
                  f"| Withheld at source | {group(base['withheld'])} |",
                  f"| Per payment | {group(base['per_payment'])} |",
                  f"| Net of production cost | {group(base['net'])} |"]
    else:
        lines += [f"| Contribution before commission | {group(base['contribution_before'])} |",
                  f"| Contribution after commission | {group(base['net'])} |"]
    days = result["centres"].get("days_to_cash")
    if days:
        lines.append(f"| Working days until it is cash | {days:.0f} |")
    lines.append("")

    spread = [r for r in shares_of_spread(side, result) if r["share"] > 0]
    if spread:
        lines += ["## Where the uncertainty lives", ""]
        for row in spread:
            lines.append(f"- `{row['parameter']}` - {row['share']:.0%} of the spread")
        lines += ["", "Narrowing anything below the top of that list is arithmetic, not research.", ""]

    if resolution is not None:
        lines += render_resolution(resolution)

    lines.append(render_gate_table(gate_rows))
    return "\n".join(lines)


def render_mechanics() -> str:
    band = notch()
    lines = ["# Published affiliate mechanics", "",
             "Every figure below was read at its own page on help.shopee.vn on 2026-07-31. Row-level "
             "sources are in `data/affiliate-mechanics.csv`.", "",
             "| What | Value | From |", "| --- | --- | --- |",
             f"| Service fee on partner earnings | {SERVICE_FEE_CURRENT:.2%}, VAT included | "
             f"{SERVICE_FEE_FROM} |",
             f"| Service fee, superseded and still published | {SERVICE_FEE_SUPERSEDED:.0%} | "
             f"2025-05-16 |",
             f"| Withheld at source from an individual | {WITHHOLDING_RATE:.0%} | "
             f"Thong tu 111/2013/TT-BTC |",
             f"| Withholding applies at or above | {WITHHOLDING_FLOOR_CURRENT:,.0f} VND a payment | "
             f"{WITHHOLDING_FLOOR_FROM} |",
             f"| Withholding floor, superseded and still published | "
             f"{WITHHOLDING_FLOOR_SUPERSEDED:,.0f} VND | 2013 |",
             f"| Minimum payment | {MINIMUM_PAYOUT:,.0f} VND | seller programme terms |",
             f"| Violating-order share that locks the account | {VIOLATION_LOCK_SHARE:.0%} | "
             f"seller programme terms |", ""]
    lines += ["## The two windows", ""]
    for days, meaning in sorted(DOCUMENTED_WINDOWS.items()):
        lines.append(f"- **{days} days** - {meaning}")
    lines += ["", "They are not two readings of one rule. They are two programmes, and the seller "
                  "programme states both of them in one document without reconciling them.", "",
              "## The withholding notch", "",
              f"Ten percent comes off the whole payment rather than the excess, so a payment of "
              f"{band['floor']:,.0f} VND nets {band['worst_net']:,.0f} while a payment of "
              f"{band['best_below']:,.0f} nets all of it. Every payment from "
              f"{band['floor']:,.0f} to {band['top']:,.0f} VND is worse than stopping just below the "
              f"floor, a band {band['width']:,.0f} VND wide.", ""]
    return "\n".join(lines)


def render_notch() -> str:
    band = notch()
    return "\n".join([
        "# The withholding notch", "",
        f"Withholding is {band['rate']:.0%} of the payment, charged on the whole payment once it "
        f"reaches {band['floor']:,.0f} VND.", "",
        "| Payment | Withheld | Net |", "| --- | --- | --- |",
        f"| {band['best_below']:,.0f} | 0 | {band['best_below']:,.0f} |",
        f"| {band['floor']:,.0f} | {band['floor'] * band['rate']:,.0f} | "
        f"{band['worst_net']:,.0f} |",
        f"| {band['top']:,.0f} | {band['top'] * band['rate']:,.0f} | {band['floor']:,.0f} |", "",
        f"So the band from {band['floor']:,.0f} to {band['top']:,.0f} VND - "
        f"{band['width']:,.0f} VND wide - nets less than a payment one dong below the floor, and a "
        f"payment of {band['top']:,.0f} exactly matches it.", "",
        "This is not a rounding curiosity. Cadence for individual partners is twice weekly, so a "
        "period's earnings are cut into small payments and a beginner's per-payment figure lands near "
        "the floor by default. Fewer, larger payments leave the band; so does one fewer payment in the "
        "period. Both are worth more than any change to the content.", "",
        f"Source: help.shopee.vn/portal/10/article/196407, the {WITHHOLDING_FLOOR_FROM} threshold "
        f"change, read 2026-07-31.", ""])


TEMPLATE = """parameter,low,high,unit,source_url,verified_at,what_it_measures
gmv,,,VND,,,Attributed order value in the period from your own affiliate report
commission_rate,,,share,,,Shopee base plus Xtra as a share - a range because it is algorithmic
return_rate,,,share,,,Cancelled refused and returned share from your own reconciliation
attribution_window_days,7,7,days,https://help.shopee.vn/portal/10/article/122941,,7 creator-side or 30 seller-side
days_to_cash,,,days,,,Working days from order to cash for your partner type
service_fee,0.0098,0.0098,share,https://help.shopee.vn/portal/10/article/174381,,Shopee service fee on earnings
withholding_rate,0.1,0.1,share,https://help.shopee.vn/portal/10/article/196407,,Tax withheld at source
withholding_floor,250000,250000,VND,https://help.shopee.vn/portal/10/article/196407,,Per-payment withholding floor
payments_in_period,,,count,,,Payments the period is split into - twice weekly for individuals
content_cost,,,VND,,,Your hours at your own rate plus samples editing and media
"""


def self_check() -> str:
    lines = ["# model_affiliate self-check", ""]

    def deal(**overrides) -> dict:
        base = {"gmv": (100_000_000, 100_000_000), "commission_rate": (0.08, 0.12),
                "return_rate": (0.10, 0.20), "attribution_window_days": (7, 7),
                "days_to_cash": (45, 45), "service_fee": (0.0098, 0.0098),
                "withholding_rate": (0.1, 0.1), "withholding_floor": (250_000, 250_000),
                "payments_in_period": (8, 8), "content_cost": (2_000_000, 2_000_000),
                "contribution_margin": (0.30, 0.30)}
        base.update(overrides)
        return {n: {"parameter": n, "low": float(lo), "high": float(hi), "unit": "",
                    "source_url": "https://help.shopee.vn/portal/10/article/174381",
                    "verified_at": "2026-07-31", "what_it_measures": ""}
                for n, (lo, hi) in base.items()}

    # A quoted rate loses a fifth of itself before the delay is counted. Checked by hand:
    # 100,000,000 x (1-0.15) x 0.10 x (1-0.0098) x 0.9 - 2,000,000 = 5,574,015.
    result = compute("creator", deal())
    expected = 100_000_000 * 0.85 * 0.10 * (1 - 0.0098) * 0.9 - 2_000_000
    assert abs(result["base"]["net"] - expected) < 1.0, result["base"]["net"]
    lines.append(f"- base-case net is the deductions applied in order: {expected:,.0f}")

    # The bounds bracket the base case, and the spread is driven by the two ranged inputs.
    assert result["low"] < result["centre"] < result["high"]
    drivers = [r["parameter"] for r in shares_of_spread("creator", result) if r["share"] > 0]
    assert set(drivers) == {"commission_rate", "return_rate"}, drivers
    lines.append(f"- the spread comes from exactly the ranged inputs: {', '.join(sorted(drivers))}")

    # The notch: a payment at the floor nets less than one a dong below it.
    band = notch()
    assert band["worst_net"] < band["best_below"], band
    assert abs(band["top"] - 250_000 / 0.9) < 1e-6, band
    lines.append(f"- the notch runs {band['floor']:,.0f} to {band['top']:,.0f} VND, "
                 f"{band['width']:,.0f} VND wide")

    # A model with no return rate prints no total at all - not a total with the gap defaulted to zero.
    stripped = deal()
    del stripped["return_rate"]
    incomplete = compute("creator", stripped)
    rows = gates("creator", incomplete, "2026-07-31")
    failed = {r["gate"] for r in rows if not r["pass"]}
    assert not incomplete["computable"] and incomplete["missing"] == ["return_rate"], incomplete
    assert "return-rate-is-stated" in failed and "model-is-complete" in failed, failed
    report = render("creator", incomplete, rows, "2026-07-31", None)
    assert "not computable" in report and "## What arrives" not in report, report[:400]
    assert len(rows) == 12, len(rows)
    lines.append("- a model without a return rate refuses to print a total and says which input is gone")

    # The stale withholding floor is caught even though it is published on the same host.
    rows = gates("creator", compute("creator", deal(withholding_floor=(2_000_000, 2_000_000))),
                 "2026-07-31")
    assert not next(r for r in rows if r["gate"] == "withholding-floor-is-the-current-one")["pass"]
    lines.append("- the superseded 2,000,000 VND floor fails its gate")

    # A seller funding commission above margin fails, and it is the gate that fails.
    seller = compute("seller", deal(commission_rate=(0.32, 0.35)))
    rows = gates("seller", seller, "2026-07-31")
    assert not next(r for r in rows if r["gate"] == "contribution-survives-commission")["pass"]
    assert seller["high"] < 0, seller["high"]
    lines.append("- commission above contribution margin fails its gate and nets below zero")

    # A floor outside the range ends the question; one inside it names what would settle it.
    clean = compute("creator", deal())
    assert not resolve_against("creator", clean, clean["high"] * 2)["straddles"]
    middle = resolve_against("creator", clean, clean["centre"])
    assert middle["straddles"] and middle["settled_by"] == [], middle
    off_centre = resolve_against("creator", clean, (clean["centre"] + clean["high"]) / 2)
    assert off_centre["straddles"] and off_centre["settled_by"], off_centre
    lines.append("- a floor on the centre has no research answer; one off centre names the input")

    # Every gate explains itself in more than a clause.
    rows = gates("creator", clean, "2026-07-31")
    assert len(rows) == 12, len(rows)
    assert all(len(r["why"].split()) > 20 for r in rows)
    assert blocking(rows) == 0, [r["gate"] for r in rows if not r["pass"]]
    lines.append(f"- {len(rows)} gates, each explaining itself, and a clean deal clears all of them")

    lines += ["", "All assertions passed."]
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Model what an affiliate commission rate actually pays, and when.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--check", metavar="DEAL.CSV", help="read a deal and grade it")
    source.add_argument("--template", metavar="DEAL.CSV", help="write a starter deal file")
    source.add_argument("--mechanics", action="store_true",
                        help="print the published figures this model checks against")
    source.add_argument("--notch", action="store_true",
                        help="print the payment band where earning more nets less")
    source.add_argument("--self-check", action="store_true", help="run the built-in assertions")
    parser.add_argument("--side", choices=("creator", "seller"),
                        help="whose arithmetic to run, required with --check")
    parser.add_argument("--as-of", default=dt.date.today().isoformat(),
                        help="date to measure source staleness against")
    parser.add_argument("--floor", type=float, metavar="VALUE",
                        help="the net the deal has to beat to be worth doing")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output", help="write to a file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    args = build_parser().parse_args(argv)

    if args.self_check:
        emit(self_check(), args.output)
        return 0
    if args.mechanics:
        emit(render_mechanics() + "\n", args.output)
        return 0
    if args.notch:
        emit(render_notch(), args.output)
        return 0
    if args.template:
        target = Path(args.template)
        if target.exists():
            print(f"{target} already exists; refusing to overwrite it", file=sys.stderr)
            return 1
        target.write_text(TEMPLATE, encoding="utf-8")
        emit(f"Wrote {target}. Fill every blank low and high, then run --check with --side.\n")
        return 0

    if not args.side:
        print("--check needs --side creator or --side seller", file=sys.stderr)
        return 1
    try:
        deal = parse_deal(read_deal(args.check))
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    if "gmv" not in deal:
        print("gmv is the one input with no substitute; add it and run again", file=sys.stderr)
        return 1

    result = compute(args.side, deal)
    gate_rows = gates(args.side, result, args.as_of)
    resolution = resolve_against(args.side, result, args.floor) \
        if args.floor is not None and result["computable"] else None

    if args.json:
        payload = {"as_of": args.as_of, "side": args.side, "computable": result["computable"],
                   "missing": result["missing"], "blocking": blocking(gate_rows), "gates": gate_rows}
        if result["computable"]:
            payload.update({"net": {"low": result["low"], "centre": result["centre"],
                                    "high": result["high"]},
                            "take_rate": {"low": result["take_rate_low"],
                                          "centre": result["take_rate_centre"],
                                          "high": result["take_rate_high"]},
                            "resolution": resolution,
                            "spread": shares_of_spread(args.side, result),
                            "steps": result["base"]})
        emit_json(payload, args.output)
    else:
        emit(render(args.side, result, gate_rows, args.as_of, resolution), args.output)

    if blocking(gate_rows):
        return 2
    if resolution is not None and resolution["straddles"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
