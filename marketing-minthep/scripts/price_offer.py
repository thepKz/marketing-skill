#!/usr/bin/env python3
"""Price an offer and price a discount, in contribution margin rather than in revenue.

`plan-from-zero` promises an offer and the skill had no arithmetic behind the word. That gap has one
specific consequence, and it is the most expensive mistake in small-business marketing: a discount is
decided against the price and it lands on the margin. Twenty percent off a price carrying forty percent
gross margin removes half the contribution, so holding the same gross profit needs twice the units - not
twenty percent more. Nobody sets out to double their volume target. They set out to run a sale.

Everything here is one subtraction and one division, which is the point. The arithmetic was never the
hard part; doing it before the campaign was.

What it computes: contribution margin per unit and as a ratio, break-even ROAS, break-even units
against a fixed cost or a campaign spend, the volume multiple a discount needs to stay level, the
maximum acquisition cost the unit economics can carry, and the payback period at a stated repeat rate.

Currency-agnostic on purpose. It never converts, never assumes VND, and never prints a currency name,
because a helper that guesses the currency is a helper that will one day guess wrong by a factor of
twenty-five thousand.

    python scripts/price_offer.py --price 390000 --variable-cost 150000
    python scripts/price_offer.py --price 390000 --variable-cost 150000 --discount 0.20
    python scripts/price_offer.py --price 390000 --variable-cost 150000 --campaign-spend 20000000
    python scripts/price_offer.py --price 390000 --variable-cost 150000 --repeat-purchases 2.5 \\
        --acquisition-cost 90000
    python scripts/price_offer.py --self-check

Exit codes are 0 clean, 1 usage error, 2 a gate failed, 3 computable but unsettled.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

# A discount needing more than double the units is not a promotion, it is a new business model with the
# same product. The threshold is a house convention and is labelled as one; what is not a convention is
# the multiple itself, which is arithmetic.
VOLUME_MULTIPLE_REVIEW = 2.0


def margin(price: float, variable_cost: float) -> dict:
    contribution = price - variable_cost
    return {
        "price": price,
        "variable_cost": variable_cost,
        "contribution_per_unit": round(contribution, 4),
        "contribution_ratio": round(contribution / price, 6) if price else None,
        # Break-even ROAS is the reciprocal of the contribution ratio, and it is the number that should
        # replace every ROAS target somebody was given without one. A 2.0 target is generous at 60
        # percent contribution and loss-making at 40.
        "break_even_roas": round(price / contribution, 4) if contribution > 0 else None,
    }


def discount_effect(price: float, variable_cost: float, discount: float) -> dict:
    """What a percentage off the price does to the contribution behind it."""
    before = price - variable_cost
    new_price = price * (1.0 - discount)
    after = new_price - variable_cost
    out = {
        "discount": discount,
        "discounted_price": round(new_price, 4),
        "contribution_before": round(before, 4),
        "contribution_after": round(after, 4),
        "contribution_lost_share": round((before - after) / before, 6) if before > 0 else None,
        "volume_multiple_to_hold_gross_profit": None,
        "extra_units_per_hundred": None,
    }
    if after > 0 and before > 0:
        multiple = before / after
        out["volume_multiple_to_hold_gross_profit"] = round(multiple, 4)
        out["extra_units_per_hundred"] = round(100 * (multiple - 1.0), 1)
    return out


def max_acquisition_cost(contribution: float, repeat_purchases: float,
                         target_return: float) -> float | None:
    """The most one customer may cost to acquire.

    Contribution times expected lifetime purchases divided by the return the business needs on that
    spend. `target_return` of 3 is the common "spend a third of lifetime value" rule; it is a policy
    input, not a finding, and it is named as one in the output.
    """
    if contribution <= 0 or repeat_purchases <= 0 or target_return <= 0:
        return None
    return contribution * repeat_purchases / target_return


def build(price: float, variable_cost: float, discount: float | None, fixed_cost: float | None,
          campaign_spend: float | None, repeat_purchases: float | None,
          acquisition_cost: float | None, target_return: float) -> dict:
    core = margin(price, variable_cost)
    contribution = core["contribution_per_unit"]
    gates: list[dict] = []
    notes: list[str] = []
    report: dict = {"check": "price-offer", "unit_economics": core, "gates": gates, "notes": notes}

    gates.append({
        "gate": "contribution-positive",
        "status": "passed" if contribution > 0 else "failed",
        "observed": f"{contribution:,.2f} per unit",
        "target": "> 0 before any marketing cost",
    })
    if contribution <= 0:
        notes.append("Every unit sold at this price loses money before a single click is paid for. "
                     "No channel, creative or offer changes that, and a discount makes it faster.")
        report["verdict"] = {"status": "failed",
                            "summary": "The price does not cover the variable cost."}
        return report

    notes.append(f"Contribution is {core['contribution_ratio']:.1%} of price, so break-even ROAS is "
                 f"{core['break_even_roas']:.2f}. Any ROAS target below that loses money on every "
                 f"sale it produces, however good the creative is.")

    if discount is not None:
        effect = discount_effect(price, variable_cost, discount)
        report["discount"] = effect
        if effect["contribution_after"] <= 0:
            gates.append({
                "gate": "discount-survivable",
                "status": "failed",
                "observed": f"contribution {effect['contribution_after']:,.2f} after "
                            f"{discount:.0%} off",
                "target": "> 0",
            })
            notes.append(f"{discount:.0%} off takes the price below the variable cost. This is not a "
                         f"thin promotion, it is paying customers to take the product.")
        else:
            multiple = effect["volume_multiple_to_hold_gross_profit"]
            status = "passed" if multiple <= VOLUME_MULTIPLE_REVIEW else "review"
            gates.append({
                "gate": "discount-survivable",
                "status": status,
                "observed": f"{multiple:.2f}x units needed to stay level",
                "target": f"<= {VOLUME_MULTIPLE_REVIEW:.1f}x, a house limit",
            })
            notes.append(
                f"{discount:.0%} off the price removes {effect['contribution_lost_share']:.0%} of the "
                f"contribution, not {discount:.0%}. Holding the same gross profit takes {multiple:.2f}x "
                f"the units, which is {effect['extra_units_per_hundred']:.0f} more per hundred. That is "
                f"the volume target this promotion actually sets.")
            if status == "review":
                notes.append("A promotion that needs more than double the units is a different "
                             "business model wearing a sale's clothes. If the volume is genuinely "
                             "available at the lower price, the lower price is the price.")
        working_contribution = max(effect["contribution_after"], 0.0)
    else:
        working_contribution = contribution

    if fixed_cost or campaign_spend:
        recoverable = (fixed_cost or 0.0) + (campaign_spend or 0.0)
        units = math.ceil(recoverable / working_contribution) if working_contribution > 0 else None
        report["break_even_units"] = units
        if units is not None:
            notes.append(f"{recoverable:,.0f} of fixed cost and campaign spend needs {units:,} units "
                         f"to clear at {working_contribution:,.2f} contribution each. Everything "
                         f"before that unit is recovery, not profit.")

    if repeat_purchases is not None:
        ceiling = max_acquisition_cost(working_contribution, repeat_purchases, target_return)
        report["max_acquisition_cost"] = round(ceiling, 4) if ceiling else None
        first_order_ceiling = working_contribution
        report["first_order_acquisition_ceiling"] = round(first_order_ceiling, 4)
        notes.append(
            f"At {repeat_purchases:g} expected purchases and a {target_return:g}x return on "
            f"acquisition spend, one customer may cost up to {ceiling:,.2f}. The {target_return:g}x is "
            f"a policy choice, not a finding. Breaking even on the first order alone allows "
            f"{first_order_ceiling:,.2f}.")
        if ceiling > first_order_ceiling:
            notes.append(f"The lifetime ceiling sits {ceiling - first_order_ceiling:,.2f} above the "
                         f"first-order one, and that entire gap is a bet that the repeat rate is "
                         f"real. Spend into it only with repeat data from this product, not from the "
                         f"category.")
        else:
            # The commoner case at a demanding target return, and worth naming, because a gate can
            # fail here on a cost that repays inside the first order. That is a policy decision doing
            # its job, not an arithmetic problem, and it should read that way.
            notes.append(f"The {target_return:g}x policy is stricter than first-order break-even, so "
                         f"the ceiling is {first_order_ceiling - ceiling:,.2f} below what a single "
                         f"order would carry. A cost between the two is profitable on order one and "
                         f"still outside policy; decide which of the two is the constraint before "
                         f"reading the gate.")
        if acquisition_cost is not None:
            over = acquisition_cost > ceiling
            gates.append({
                "gate": "acquisition-ceiling",
                "status": "failed" if over else "passed",
                "observed": f"{acquisition_cost:,.2f} per customer",
                "target": f"<= {ceiling:,.2f}",
            })
            orders = acquisition_cost / working_contribution
            report["orders_to_repay_acquisition"] = round(orders, 3)
            notes.append(f"{acquisition_cost:,.2f} to acquire takes {orders:.2f} orders to repay. "
                         f"{'That is longer than the lifetime being assumed.' if orders > repeat_purchases else 'That is inside the assumed lifetime.'}")
    elif acquisition_cost is not None:
        # Without a repeat rate there is no lifetime to judge the cost against, so the only honest
        # comparison is the first order, and it has to be labelled as that rather than as a verdict.
        orders = acquisition_cost / working_contribution
        report["orders_to_repay_acquisition"] = round(orders, 3)
        notes.append(f"{acquisition_cost:,.2f} to acquire takes {orders:.2f} orders to repay. With no "
                     f"--repeat-purchases given there is no lifetime to judge that against, so this is "
                     f"a first-order figure only.")

    failed = [gate for gate in gates if gate["status"] == "failed"]
    unsettled = [gate for gate in gates if gate["status"] == "review"]
    if failed:
        status = "failed"
        summary = "; ".join(f"{gate['gate']}: {gate['observed']}" for gate in failed)
    elif unsettled:
        status = "review"
        summary = "; ".join(f"{gate['gate']}: {gate['observed']}" for gate in unsettled)
    else:
        status = "passed"
        summary = (f"Contribution {contribution:,.2f} per unit, {core['contribution_ratio']:.1%} of "
                   f"price, break-even ROAS {core['break_even_roas']:.2f}.")
    report["verdict"] = {"status": status, "summary": summary}
    return report


def as_text(report: dict) -> str:
    core = report["unit_economics"]
    lines = [f"# price and offer - verdict {report['verdict']['status']}",
             report["verdict"]["summary"], "",
             f"price              {core['price']:>16,.2f}",
             f"variable cost      {core['variable_cost']:>16,.2f}",
             f"contribution       {core['contribution_per_unit']:>16,.2f}"]
    if core["contribution_ratio"] is not None:
        lines.append(f"contribution ratio {core['contribution_ratio']:>15.1%}")
    if core["break_even_roas"] is not None:
        lines.append(f"break-even ROAS    {core['break_even_roas']:>16.2f}")
    if "discount" in report:
        d = report["discount"]
        lines += ["", f"{d['discount']:.0%} off -> price {d['discounted_price']:,.2f}, "
                      f"contribution {d['contribution_after']:,.2f}"]
        if d["volume_multiple_to_hold_gross_profit"]:
            lines.append(f"units needed to stay level: "
                         f"{d['volume_multiple_to_hold_gross_profit']:.2f}x")
    if report.get("break_even_units"):
        lines.append(f"break-even units   {report['break_even_units']:>16,}")
    if report.get("max_acquisition_cost"):
        lines.append(f"max cost per customer {report['max_acquisition_cost']:>13,.2f}")
    if report.get("gates"):
        lines += ["", "| gate | status | observed | target |", "|---|---|---|---|"]
        for gate in report["gates"]:
            lines.append(f"| {gate['gate']} | {gate['status']} | {gate['observed']} | "
                         f"{gate['target']} |")
    if report.get("notes"):
        lines.append("")
        lines += [f"- {note}" for note in report["notes"]]
    return "\n".join(lines)


def self_check() -> str:
    """Verify the arithmetic on cases whose answers can be checked by hand.

    Every case here is chosen so the right answer is obvious on inspection, which is the only kind of
    self-check worth having in a file full of division. The 40 percent margin case is the one the whole
    script exists for: 20 off 40 leaves 20, and 40 over 20 is 2.
    """
    lines = ["# price_offer self-check"]
    ok = True

    def check(label: str, got: float | None, want: float, tol: float = 1e-9) -> None:
        nonlocal ok
        good = got is not None and abs(got - want) <= tol
        ok = ok and good
        lines.append(f"{'ok  ' if good else 'FAIL'} {label}: {got} vs {want}")

    # Price 100, cost 60. Contribution 40, ratio 0.4, break-even ROAS 2.5.
    core = margin(100.0, 60.0)
    check("contribution at 100/60", core["contribution_per_unit"], 40.0)
    check("ratio at 100/60", core["contribution_ratio"], 0.4)
    check("break-even ROAS at 40% contribution", core["break_even_roas"], 2.5)

    # 20% off 100 is 80; 80 - 60 = 20; holding gross profit needs 40/20 = exactly 2x the units.
    effect = discount_effect(100.0, 60.0, 0.20)
    check("contribution after 20% off", effect["contribution_after"], 20.0)
    check("volume multiple", effect["volume_multiple_to_hold_gross_profit"], 2.0)
    check("share of contribution lost", effect["contribution_lost_share"], 0.5)
    check("extra units per hundred", effect["extra_units_per_hundred"], 100.0)

    # The asymmetry that makes this worth a script: the same 20 points off a 70 percent margin costs
    # under a third of the contribution, so the volume needed is nowhere near double.
    thin = discount_effect(100.0, 30.0, 0.20)
    check("volume multiple at 70% margin", thin["volume_multiple_to_hold_gross_profit"],
          70.0 / 50.0, 1e-4)

    # 50% off a 40% margin goes below cost, so there is no multiple that saves it.
    ruin = discount_effect(100.0, 60.0, 0.50)
    good = (ruin["contribution_after"] < 0
            and ruin["volume_multiple_to_hold_gross_profit"] is None)
    ok = ok and good
    lines.append(f"{'ok  ' if good else 'FAIL'} 50% off a 40% margin has no survivable volume: "
                 f"contribution {ruin['contribution_after']}")

    check("max CAC at 40 contribution, 3 purchases, 3x", max_acquisition_cost(40.0, 3.0, 3.0), 40.0)
    good = max_acquisition_cost(-5.0, 3.0, 3.0) is None
    ok = ok and good
    lines.append(f"{'ok  ' if good else 'FAIL'} negative contribution has no acquisition ceiling")

    report = build(100.0, 120.0, None, None, None, None, None, 3.0)
    good = report["verdict"]["status"] == "failed"
    ok = ok and good
    lines.append(f"{'ok  ' if good else 'FAIL'} price under cost is refused before anything else")

    lines.append("")
    lines.append("verdict passed" if ok else "verdict failed")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--price", type=float)
    parser.add_argument("--variable-cost", type=float,
                        help="everything that scales with one unit sold: goods, packaging, shipping, "
                             "payment fees, platform commission, expected returns")
    parser.add_argument("--discount", type=float, help="as a fraction, 0.20 for twenty percent off")
    parser.add_argument("--fixed-cost", type=float, help="per period, to break even against")
    parser.add_argument("--campaign-spend", type=float)
    parser.add_argument("--repeat-purchases", type=float,
                        help="expected purchases per customer; state where the number came from")
    parser.add_argument("--acquisition-cost", type=float, help="current or proposed cost per customer")
    parser.add_argument("--target-return", type=float, default=3.0,
                        help="required return on acquisition spend, default 3.0, a policy choice")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", help="write here instead of stdout")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)

    if args.self_check:
        report = self_check()
        emit(report)
        return 0 if report.rstrip().endswith("passed") else 2

    if args.price is None or args.variable_cost is None:
        parser.error("pass --price and --variable-cost, or --self-check")
    if args.price <= 0:
        parser.error("--price must be above zero")
    if args.variable_cost < 0:
        parser.error("--variable-cost cannot be negative")
    if args.discount is not None and not 0.0 < args.discount < 1.0:
        parser.error("--discount is a fraction between 0 and 1, so 0.20 for twenty percent off")
    if args.repeat_purchases is not None and args.repeat_purchases <= 0:
        parser.error("--repeat-purchases must be above zero")
    if args.target_return <= 0:
        parser.error("--target-return must be above zero")

    report = build(args.price, args.variable_cost, args.discount, args.fixed_cost,
                   args.campaign_spend, args.repeat_purchases, args.acquisition_cost,
                   args.target_return)
    if args.format == "json":
        emit_json(report, args.output)
    else:
        emit(as_text(report), args.output)
    return {"passed": 0, "failed": 2, "review": 3, "skipped": 3}[report["verdict"]["status"]]


if __name__ == "__main__":
    sys.exit(main())
