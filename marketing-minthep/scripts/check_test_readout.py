#!/usr/bin/env python3
"""Decide whether a marketing test is readable yet, and refuse the winner when it is not.

`performance-direction.md` already carries the rule: never compare percentages without reporting sample size,
and never declare a winner from tiny or materially unequal delivery. That rule was unenforceable as
written, because nobody reading it could work out what tiny means for their own conversion rate. Tiny
is not a number somebody chooses; it falls out of the baseline rate and the size of the difference
worth detecting, and at a 1 percent baseline it is roughly forty times larger than at 20 percent. So
the rule needed arithmetic behind it or it was decoration.

What this does, in order: the observed rates, the lift, a two-proportion test, a confidence interval
on the difference, the sample size each arm needed for the effect the test was set up to detect, and
how many more days of the current delivery that would take. Then it grades the readout. If a winner
was claimed with `--claim`, the claim is checked against the interval rather than against the point
estimate, which is the whole difference between a readout and a hope.

Everything here is stdlib. The normal CDF is `math.erf` and its inverse is a bisection over that CDF,
so there is no dependency to install and no version of this that silently disagrees with itself.

    python scripts/check_test_readout.py --variant "A:clicks=1200,conversions=36" \\
        --variant "B:clicks=1180,conversions=51" --mde 0.20
    python scripts/check_test_readout.py --variant "A:clicks=400,conversions=8" \\
        --variant "B:clicks=410,conversions=13" --claim B
    python scripts/check_test_readout.py --variant "A:clicks=900,conversions=27" \\
        --variant "B:clicks=880,conversions=31" --daily-clicks 300 --format json
    python scripts/check_test_readout.py --plan --baseline 0.03 --mde 0.20
    python scripts/check_test_readout.py --self-check

Exit codes are 0 clean, 1 usage error, 2 a gate failed, 3 computable but unsettled.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

# Delivery this uneven is the case performance-direction.md names separately from sample size, because the
# arms stop being comparable for reasons that have nothing to do with the creative: the platform has
# decided one of them is better and is spending accordingly, so the split is now an outcome.
DELIVERY_SKEW_LIMIT = 1.20

VARIANT = re.compile(r"^\s*([A-Za-z0-9_-]+)\s*:\s*(.+)$")


def normal_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def normal_quantile(p: float) -> float:
    """Inverse normal CDF by bisection.

    Bisection rather than a rational approximation because the approximations are the kind of code
    that gets pasted in with a stale constant and is never checked again. Fifty-two halvings of
    [-10, 10] lands well inside float precision and takes microseconds, and `--self-check` compares
    the result against the standard critical values so a wrong answer here cannot go unnoticed.
    """
    if not 0.0 < p < 1.0:
        raise ValueError(f"quantile needs 0 < p < 1, got {p}")
    low, high = -10.0, 10.0
    for _ in range(200):
        mid = (low + high) / 2.0
        if normal_cdf(mid) < p:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0


def required_per_arm(baseline: float, mde: float, alpha: float, power: float) -> int | None:
    """Sample size per arm to detect a relative lift of `mde` on `baseline`.

    The standard two-proportion formula. `mde` is relative, because that is how the decision is
    actually stated - "worth switching for a 20 percent lift" - and absolute points are what people
    get wrong when the baseline is small.
    """
    if not 0.0 < baseline < 1.0:
        return None
    treated = baseline * (1.0 + mde)
    if not 0.0 < treated < 1.0 or treated == baseline:
        return None
    z_alpha = normal_quantile(1.0 - alpha / 2.0)
    z_beta = normal_quantile(power)
    variance = baseline * (1.0 - baseline) + treated * (1.0 - treated)
    return math.ceil((z_alpha + z_beta) ** 2 * variance / (treated - baseline) ** 2)


def two_proportion(a_conv: int, a_n: int, b_conv: int, b_n: int, alpha: float) -> dict:
    """Pooled z-test for the difference, plus an unpooled interval on that difference.

    Pooled for the test because the null is that the rates are equal; unpooled for the interval
    because under the alternative they are not. Mixing the two is the commonest error in a
    hand-rolled significance check and it moves the interval in the flattering direction.
    """
    p_a, p_b = a_conv / a_n, b_conv / b_n
    pooled = (a_conv + b_conv) / (a_n + b_n)
    se_pooled = math.sqrt(pooled * (1.0 - pooled) * (1.0 / a_n + 1.0 / b_n))
    diff = p_b - p_a
    z = diff / se_pooled if se_pooled else 0.0
    p_value = 2.0 * (1.0 - normal_cdf(abs(z)))
    se_diff = math.sqrt(p_a * (1.0 - p_a) / a_n + p_b * (1.0 - p_b) / b_n)
    half = normal_quantile(1.0 - alpha / 2.0) * se_diff
    return {
        "rate_a": round(p_a, 6),
        "rate_b": round(p_b, 6),
        "absolute_difference": round(diff, 6),
        "relative_lift": round(diff / p_a, 4) if p_a else None,
        "z": round(z, 4),
        "p_value": round(p_value, 6),
        "confidence_interval": [round(diff - half, 6), round(diff + half, 6)],
        "interval_crosses_zero": (diff - half) <= 0.0 <= (diff + half),
    }


def parse_variant(spec: str) -> tuple[str, int, int]:
    match = VARIANT.match(spec)
    if not match:
        raise ValueError(f"cannot read variant {spec!r}, expected NAME:clicks=N,conversions=N")
    name, body = match.group(1), match.group(2)
    fields: dict[str, int] = {}
    for part in body.split(","):
        if "=" not in part:
            raise ValueError(f"cannot read field {part!r} in variant {name}")
        key, _, value = part.partition("=")
        key = key.strip().lower()
        try:
            fields[key] = int(value.strip())
        except ValueError as exc:
            raise ValueError(f"{name}: {key} must be a whole count, got {value.strip()!r}") from exc
    for key in ("clicks", "conversions"):
        if key not in fields:
            raise ValueError(f"{name}: missing {key}")
    clicks, conversions = fields["clicks"], fields["conversions"]
    if clicks <= 0:
        raise ValueError(f"{name}: clicks must be above zero")
    if conversions < 0:
        raise ValueError(f"{name}: conversions cannot be negative")
    if conversions > clicks:
        raise ValueError(f"{name}: {conversions} conversions from {clicks} clicks is impossible")
    return name, clicks, conversions


def read(variants: list[tuple[str, int, int]], mde: float, alpha: float, power: float,
         daily_clicks: int | None, claim: str | None) -> dict:
    (name_a, n_a, c_a), (name_b, n_b, c_b) = variants[0], variants[1]
    stats = two_proportion(c_a, n_a, c_b, n_b, alpha)

    baseline = c_a / n_a
    needed = required_per_arm(baseline, mde, alpha, power)
    notes: list[str] = []
    gates: list[dict] = []

    if needed is None:
        # A zero baseline has no rate to lift, so the sample-size formula has nothing to work on.
        # Saying so beats returning a number that looks computed.
        notes.append(f"{name_a} converted {c_a} times, so there is no baseline rate to size against. "
                     f"Report the counts and keep the test running.")
        powered = False
        shortfall = None
    else:
        smallest = min(n_a, n_b)
        powered = smallest >= needed
        shortfall = max(0, needed - smallest)
        gates.append({
            "gate": "sample-size",
            "status": "passed" if powered else "failed",
            "observed": f"{smallest} in the smaller arm",
            "target": f">= {needed} per arm for a {mde:.0%} lift on {baseline:.2%}",
        })

    skew = max(n_a, n_b) / min(n_a, n_b)
    balanced = skew <= DELIVERY_SKEW_LIMIT
    gates.append({
        "gate": "delivery-balance",
        "status": "passed" if balanced else "failed",
        "observed": f"{skew:.2f}x between arms",
        "target": f"<= {DELIVERY_SKEW_LIMIT:.2f}x",
    })

    significant = stats["p_value"] < alpha
    leader = name_b if stats["absolute_difference"] > 0 else name_a
    if stats["absolute_difference"] == 0:
        leader = None

    claim_gate = None
    if claim is not None:
        names = {name_a, name_b}
        if claim not in names:
            raise ValueError(f"claimed winner {claim!r} is not one of {sorted(names)}")
        # The claim is checked against the interval, not the point estimate. A claim that sits inside
        # an interval containing zero is a claim the data does not distinguish from no difference,
        # and that is the failure this whole script exists to catch.
        supported = significant and claim == leader and not stats["interval_crosses_zero"]
        claim_gate = {
            "gate": "claimed-winner",
            "status": "passed" if supported else "failed",
            "observed": (f"{claim} claimed; p = {stats['p_value']:.4f}, "
                         f"interval {stats['confidence_interval'][0]:+.4f} to "
                         f"{stats['confidence_interval'][1]:+.4f}"),
            "target": f"p < {alpha} and the interval clear of zero on {claim}'s side",
        }
        gates.append(claim_gate)
        if not supported:
            if not significant:
                notes.append(f"{claim} is ahead on the point estimate and that is all. At p = "
                             f"{stats['p_value']:.3f} the difference is inside what this much traffic "
                             f"produces by itself.")
            elif claim != leader:
                notes.append(f"The data leads on {leader}, not {claim}.")

    if shortfall and daily_clicks:
        per_arm_daily = daily_clicks / 2.0
        notes.append(f"At {daily_clicks} clicks a day split evenly, the smaller arm needs about "
                     f"{math.ceil(shortfall / per_arm_daily)} more days to reach {needed}.")
    elif shortfall:
        notes.append(f"The smaller arm is {shortfall} clicks short of {needed}. Pass "
                     f"--daily-clicks to turn that into days.")

    if not balanced:
        notes.append(f"Delivery is {skew:.2f}x apart. The platform is choosing between these arms, "
                     f"so the split is now a result rather than a setup, and the comparison is "
                     f"confounded whichever way it lands.")
    if significant and not powered:
        notes.append("Significant on a sample below the size this test needed. That combination is "
                     "how a false positive looks, and stopping here is what makes it permanent. "
                     "Either run to the size or restate this as a hypothesis.")

    failed = [gate for gate in gates if gate["status"] == "failed"]
    if claim_gate and claim_gate["status"] == "failed":
        status = "failed"
        summary = f"{claim} cannot be called the winner from this readout."
    elif failed:
        status = "review"
        summary = ("Not readable yet: " +
                   ", ".join(gate["gate"] for gate in failed) + ".")
    elif significant:
        status = "passed"
        summary = (f"{leader} wins, {abs(stats['relative_lift']):.1%} relative, "
                   f"p = {stats['p_value']:.4f}.")
    else:
        status = "passed"
        summary = (f"No difference at this size. p = {stats['p_value']:.4f}, interval "
                   f"{stats['confidence_interval'][0]:+.4f} to {stats['confidence_interval'][1]:+.4f}. "
                   f"That is a result: stop paying for the variant that costs more to make.")

    return {
        "check": "test-readout",
        "arms": [
            {"name": name_a, "clicks": n_a, "conversions": c_a, "rate": stats["rate_a"]},
            {"name": name_b, "clicks": n_b, "conversions": c_b, "rate": stats["rate_b"]},
        ],
        "settings": {"mde_relative": mde, "alpha": alpha, "power": power},
        "statistics": stats,
        "required_per_arm": needed,
        "shortfall_in_smaller_arm": shortfall,
        "significant": significant,
        "leader_on_point_estimate": leader,
        "gates": gates,
        "notes": notes,
        "verdict": {"status": status, "summary": summary},
    }


def plan(baseline: float, mde: float, alpha: float, power: float,
         daily_clicks: int | None) -> dict:
    needed = required_per_arm(baseline, mde, alpha, power)
    if needed is None:
        raise ValueError(f"cannot size a test against a baseline of {baseline}")
    out = {
        "check": "test-plan",
        "baseline": baseline,
        "settings": {"mde_relative": mde, "alpha": alpha, "power": power},
        "required_per_arm": needed,
        "required_total": needed * 2,
        "notes": [
            f"Detecting a {mde:.0%} relative lift on {baseline:.2%} needs {needed} per arm, "
            f"{needed * 2} in total. Halving the effect you want to detect roughly quadruples this, "
            f"which is the trade the plan is actually making.",
        ],
        "verdict": {"status": "passed", "summary": f"{needed * 2} clicks total before a readout."},
    }
    if daily_clicks:
        out["notes"].append(f"At {daily_clicks} clicks a day that is about "
                            f"{math.ceil(needed * 2 / daily_clicks)} days.")
    return out


def as_text(report: dict) -> str:
    lines = [f"# {report['check']} - verdict {report['verdict']['status']}",
             report["verdict"]["summary"], ""]
    if "arms" in report:
        for arm in report["arms"]:
            lines.append(f"{arm['name']:<10} {arm['conversions']:>6} / {arm['clicks']:<7} "
                         f"= {arm['rate']:.3%}")
        stats = report["statistics"]
        lift = f"{stats['relative_lift']:+.1%}" if stats["relative_lift"] is not None else "n/a"
        lines += ["",
                  f"difference {stats['absolute_difference']:+.4f} absolute, {lift} relative",
                  f"p = {stats['p_value']:.6f}, 95% interval "
                  f"{stats['confidence_interval'][0]:+.4f} to "
                  f"{stats['confidence_interval'][1]:+.4f}"]
    if report.get("required_per_arm"):
        lines.append(f"required per arm {report['required_per_arm']}")
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
    """Check the arithmetic against values that exist outside this file.

    A statistics helper nobody has checked against a published number is a random number generator
    with units. These three are the standard ones, so a wrong bisection or a swapped tail shows up
    here rather than in somebody's budget decision.
    """
    lines = ["# check_test_readout self-check"]
    cases = [
        ("z for 95% two-sided", normal_quantile(0.975), 1.959964, 1e-5),
        ("z for 80% power", normal_quantile(0.80), 0.841621, 1e-5),
        ("z for 99% two-sided", normal_quantile(0.995), 2.575829, 1e-5),
        ("normal_cdf(0)", normal_cdf(0.0), 0.5, 1e-12),
        ("normal_cdf(1.96)", normal_cdf(1.959964), 0.975, 1e-6),
    ]
    ok = True
    for label, got, want, tol in cases:
        good = abs(got - want) <= tol
        ok = ok and good
        lines.append(f"{'ok  ' if good else 'FAIL'} {label}: {got:.6f} vs {want:.6f}")

    # The sample size is checked by running the power function forward on the size that came back.
    # The first draft of this check asserted "published calculators put this a little over 6000",
    # which was a number from memory, and it failed against the correct answer of 8155. Recalling a
    # calculator output is exactly the move the rest of this skill gates other people for, so the
    # check now goes through a different route instead: invert to get n, then compute the power that
    # n actually delivers. Agreement means the inversion is right without anybody remembering
    # anything, and a swapped tail or a dropped variance term shows up immediately.
    for baseline, mde, power in ((0.05, 0.20, 0.80), (0.03, 0.50, 0.80), (0.20, 0.10, 0.90)):
        n = required_per_arm(baseline, mde, 0.05, power)
        treated = baseline * (1.0 + mde)
        se = math.sqrt(baseline * (1 - baseline) / n + treated * (1 - treated) / n)
        achieved = normal_cdf((treated - baseline) / se - normal_quantile(0.975))
        good = abs(achieved - power) < 0.005
        ok = ok and good
        lines.append(f"{'ok  ' if good else 'FAIL'} {baseline:.0%} baseline, {mde:.0%} lift: "
                     f"n = {n} per arm delivers {achieved:.4f} power against {power:.2f} asked")

    # A real property of the formula rather than a remembered value: it goes as the inverse square of
    # the effect, so halving the detectable lift quadruples the traffic. This is the trade-off the
    # planner is actually making, so it is worth having a test fail if it ever stops holding.
    coarse = required_per_arm(0.05, 0.20, 0.05, 0.80)
    fine = required_per_arm(0.05, 0.10, 0.05, 0.80)
    ratio = fine / coarse
    good = 3.8 <= ratio <= 4.3
    ok = ok and good
    lines.append(f"{'ok  ' if good else 'FAIL'} halving the lift multiplies traffic by "
                 f"{ratio:.2f}, expected about 4")

    # Identical arms must not be significant, and a large clear difference must be.
    flat = two_proportion(50, 1000, 50, 1000, 0.05)
    good = flat["p_value"] > 0.99 and flat["interval_crosses_zero"]
    ok = ok and good
    lines.append(f"{'ok  ' if good else 'FAIL'} identical arms: p = {flat['p_value']:.4f}")
    wide = two_proportion(50, 1000, 100, 1000, 0.05)
    good = wide["p_value"] < 0.001 and not wide["interval_crosses_zero"]
    ok = ok and good
    lines.append(f"{'ok  ' if good else 'FAIL'} 5% against 10%: p = {wide['p_value']:.6f}")

    lines.append("")
    lines.append("verdict passed" if ok else "verdict failed")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--variant", action="append", default=[],
                        metavar="NAME:clicks=N,conversions=N",
                        help="pass twice, control first")
    parser.add_argument("--mde", type=float, default=0.20,
                        help="relative lift the test was set up to detect, default 0.20")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--power", type=float, default=0.80)
    parser.add_argument("--daily-clicks", type=int, help="total across arms, to turn a shortfall "
                                                         "into days")
    parser.add_argument("--claim", metavar="NAME", help="the winner somebody wants to declare")
    parser.add_argument("--plan", action="store_true", help="size a test instead of reading one")
    parser.add_argument("--baseline", type=float, help="current rate, for --plan")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", help="write here instead of stdout")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)

    if args.self_check:
        report = self_check()
        emit(report)
        return 0 if report.rstrip().endswith("passed") else 2

    if not 0.0 < args.alpha < 0.5:
        parser.error("--alpha belongs in (0, 0.5)")
    if not 0.5 < args.power < 1.0:
        parser.error("--power belongs in (0.5, 1)")

    try:
        if args.plan:
            if args.baseline is None:
                parser.error("--plan needs --baseline")
            report = plan(args.baseline, args.mde, args.alpha, args.power, args.daily_clicks)
        else:
            if len(args.variant) != 2:
                parser.error("pass --variant exactly twice, control first, or use --plan")
            variants = [parse_variant(spec) for spec in args.variant]
            if variants[0][0] == variants[1][0]:
                parser.error("the two variants need different names")
            report = read(variants, args.mde, args.alpha, args.power, args.daily_clicks, args.claim)
    except ValueError as exc:
        parser.error(str(exc))

    if args.format == "json":
        emit_json(report, args.output)
    else:
        emit(as_text(report), args.output)
    return {"passed": 0, "failed": 2, "review": 3, "skipped": 3}[report["verdict"]["status"]]


if __name__ == "__main__":
    from _emit import run_gate
    run_gate(main)
