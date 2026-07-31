#!/usr/bin/env python3
"""Count the recurring work a Vietnamese one-person marketing function is actually carrying.

`plan_command_chain.py` answers "what has to happen before I can do this", and its answer is a
chain: eight commands, sixteen commands. That is arithmetic about dependencies, and it is silent
about the thing that decides whether any of it happens, which is that one person holds every role
at once. A sixteen-command chain and a nine-command chain are the same length to a graph and very
different to somebody whose inbox is open in the next tab.

So this script reads `data/vn-marketer-roles.csv` against the same command surface and reports
three quantities and one refusal.

The three quantities:

- `setup`, the commands that have to run once before the weekly machine can run at all. These are
  upstream of the recurring roles and they are the ones that get postponed, because nothing breaks
  this week if they do not happen.
- `weekly`, the recurring command-runs implied by the cadences the user states. Not estimated:
  a role contributes `cadence x len(its own commands)` and nothing else.
- `dependent_on_strategy`, how many of the selected roles are running against a positioning
  platform that does not exist. This is the compounding cost of the postponement above, stated as
  a count of affected roles rather than as a lecture.

The refusal: no hours, no day-rates, no "this takes three and a half hours a week". A test bans the
shape of that number - digits followed by a time or money unit - from this file, the table and the
reference, and it caught this very sentence on the first run. Nobody measured that figure, it
varies by more than a factor of five between an owner-operator and an agency, and a fabricated
number here would be laundered into a hiring decision. Capacity is whatever the user says it is,
supplied with `--capacity`, and if they do not supply it the fit check is reported as `skipped`
rather than quietly passed. This is the same discipline as `--share` in `plan_palette.py`: an
input nobody gave is not an input that came back clean.

The counts are also a floor, not a total, and the script says so in its own output. Two of the
thirteen roles - answering the inbox, and covering sales - map to no command in the surface,
because they produce no artefact. They are the two that consume the most of the day. Any capacity
model built only from a command graph is therefore wrong in a known direction, and the honest
thing is to name the direction rather than to round the roles away.

Exit codes: 0 clean, 1 usage error, 2 the stated load exceeds the stated capacity, 3 computable
but unsettled - a cadence was not supplied, or the strategy the recurring work depends on does not
exist yet.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402
from plan_command_chain import Surface, split_list  # noqa: E402

ROLES_TABLE = Path(__file__).resolve().parents[1] / "data" / "vn-marketer-roles.csv"

# A role whose `recurs` cell literally states a weekly rhythm has stated its cadence, so defaulting
# it to once a week is reading the table, not guessing. Everything else has to come from the user:
# "per-campaign" is a number only they know, and "continuous" is not a count at all.
DEFAULT_CADENCE = {"weekly": 1.0, "once, then reviewed": 0.0}
UNCOUNTABLE = ("continuous",)

STRATEGY_ROLE = "strategy"
COUNT_IS_NOT = ("a time estimate. A command-run is one distinct piece of work, not a fixed number "
                "of hours, and the two roles that consume the most of the day produce no artefact "
                "and are not counted here at all")


def load_roles(path: Path = ROLES_TABLE) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path} has no roles")
    return rows


def parse_cadence(pairs: list[str]) -> dict[str, float]:
    """Read `role=N` pairs, where N is cycles per week and may be fractional."""
    cadence: dict[str, float] = {}
    for pair in pairs:
        if "=" not in pair:
            raise ValueError(f"--cadence wants role=N, got {pair!r}")
        role, _, value = pair.partition("=")
        try:
            number = float(value)
        except ValueError:
            raise ValueError(f"--cadence {role}: {value!r} is not a number") from None
        if number < 0:
            raise ValueError(f"--cadence {role}: {number} is negative")
        cadence[role.strip()] = number
    return cadence


class OperatingLoad:
    """The roles table joined to the command surface."""

    def __init__(self, roles: list[dict], surface: Surface) -> None:
        self.surface = surface
        self.roles = roles
        self.by_role = {row["role_id"]: row for row in roles}

    def commands_of(self, role_id: str) -> list[str]:
        return split_list(self.by_role[role_id]["commands"])

    def upstream(self, role_id: str, have: set[str]) -> list[str]:
        """The commands that must already have run before this role's own commands can run.

        Taking the chain to the role's output artefact and subtracting the role's own commands
        leaves exactly the scaffolding the role stands on. For the designer that is the brief and
        everything the brief stands on; for the reporter it is the entire campaign that produced
        the numbers. This is the part a weekly cadence must not be multiplied by, because a
        positioning platform written once stays written."""
        artifact = self.by_role[role_id]["artifact_per_cycle"]
        if artifact not in self.surface.producer:
            return []
        chain = self.surface.plan(artifact, have)["commands"]
        return [name for name in chain if name not in set(self.commands_of(role_id))]

    def report(self, role_ids: list[str], cadence: dict[str, float], have: set[str],
               capacity: float | None) -> dict:
        rows: list[dict] = []
        once: list[dict] = []
        uncounted: list[dict] = []
        cadence_missing: list[dict] = []
        upstream: set[str] = set()
        weekly_total = 0.0

        for role_id in role_ids:
            role = self.by_role[role_id]
            commands = self.commands_of(role_id)
            if not commands:
                uncounted.append({
                    "role": role_id,
                    "role_vi": role["role_vi"],
                    "why_not_counted": role["artifact_per_cycle"],
                    "recurs": role["recurs"],
                    "what_breaks_if_dropped": role["what_breaks_if_dropped"],
                })
                continue

            upstream.update(self.upstream(role_id, have))
            rate = cadence.get(role_id, DEFAULT_CADENCE.get(role["recurs"]))
            entry = {
                "role": role_id,
                "role_vi": role["role_vi"],
                "recurs": role["recurs"],
                "commands": commands,
                "runs_per_cycle": len(commands),
                "cycles_per_week": rate,
                "produces": role["artifact_per_cycle"],
                "slips_when_busy": role["slips_when_busy"],
            }
            # A role that recurs zero times a week is not weekly work at zero volume; it is work
            # that runs once and then holds. Listing it at "0 runs/week" beside the weekly roles
            # is the same mistake the whole unit exists to correct, so it goes in its own list.
            if rate == 0:
                once.append(entry)
                continue
            if rate is None:
                entry["weekly_runs"] = None
                reason = ("this role is continuous and has no cycle to count"
                          if role["recurs"] in UNCOUNTABLE
                          else "the table cannot know how many campaigns a month you run")
                cadence_missing.append({"role": role_id, "recurs": role["recurs"],
                                        "supply": f"--cadence {role_id}=N", "why": reason})
            else:
                entry["weekly_runs"] = round(rate * len(commands), 2)
                weekly_total += entry["weekly_runs"]
            rows.append(entry)

        # Upstream work that a selected role performs itself is not extra: it is already listed
        # under that role. Subtract both lists, or the once-only role gets counted twice, which is
        # how the first run of this script reported thirteen setup commands for a seven-command job.
        owned = {c for row in rows + once for c in row["commands"]}
        setup_only = self.surface.order_chain(upstream - owned, have)

        strategy_selected = STRATEGY_ROLE in role_ids
        strategy_artifact = self.by_role[STRATEGY_ROLE]["artifact_per_cycle"]
        if strategy_artifact in have:
            strategy_status = "held"
        elif strategy_selected:
            strategy_status = "planned"
        else:
            strategy_status = "missing"
        strategy_commands = set(self.commands_of(STRATEGY_ROLE))
        dependent = [
            row["role"] for row in rows
            if strategy_commands & set(self.upstream(row["role"], have))
        ]

        fit = self.check_fit(weekly_total, capacity, cadence_missing, counted=bool(rows))
        verdict, exit_code = self.settle(fit, cadence_missing, dependent, strategy_status,
                                        counted=bool(rows))

        return {
            "roles_selected": role_ids,
            "have": sorted(have),
            "setup_roles": once,
            "setup_runs_once": setup_only,
            "setup_count": len(setup_only) + sum(len(row["commands"]) for row in once),
            "weekly": rows,
            "weekly_command_runs": round(weekly_total, 2),
            "weekly_count_is_a_floor_because": COUNT_IS_NOT,
            "not_counted": uncounted,
            "cadence_not_supplied": cadence_missing,
            "strategy": strategy_status,
            "roles_depending_on_strategy": [] if strategy_status == "held" else dependent,
            "capacity_check": fit,
            "verdict": verdict,
            "exit_code": exit_code,
        }

    @staticmethod
    def check_fit(weekly: float, capacity: float | None,
                  cadence_missing: list[dict], counted: bool) -> dict:
        if not counted:
            # Selecting only the roles that produce no artefact and being told the week fits would
            # be the exact error this unit exists to name: an uncounted role reported as a light one.
            return {"status": "skipped",
                    "why": "none of the selected roles maps to a command, so there is nothing to "
                           "count. That is a fact about the roles, not a light week",
                    "supply": "select a role that produces an artefact, or accept that this load "
                              "is real and invisible to every command graph"}
        if capacity is None:
            return {"status": "skipped",
                    "why": "no --capacity was given, so there is nothing to compare against. An "
                           "unmeasured week is not a week that came back clean",
                    "supply": "--capacity N, in command-runs per week you can actually sustain"}
        headroom = round(capacity - weekly, 2)
        status = "failed" if weekly > capacity else "passed"
        if status == "passed" and cadence_missing:
            status = "review"
        return {
            "status": status,
            "stated_capacity": capacity,
            "counted_load": round(weekly, 2),
            "headroom": headroom,
            "why": ("the counted load already exceeds the stated capacity, and the count excludes "
                    "the two roles that consume the most of the day"
                    if status == "failed" else
                    "the counted load fits, but roles whose cadence was not supplied are missing "
                    "from the count, so this is not yet a pass"
                    if status == "review" else
                    "the counted load fits inside the stated capacity"),
        }

    @staticmethod
    def settle(fit: dict, cadence_missing: list[dict], dependent: list[str],
               strategy_status: str, counted: bool) -> tuple[str, int]:
        if fit["status"] == "failed":
            return ("the load does not fit the capacity you stated; decide what to buy in or drop "
                    "before adding anything", 2)
        if not counted:
            return ("nothing here is countable. Every selected role produces work and no artefact, "
                    "which is why it never appears in a plan and never gets resourced", 3)
        if strategy_status == "missing" and dependent:
            return (f"computable, but {len(dependent)} recurring roles stand on a positioning "
                    f"platform that neither exists nor is planned, so each of them is deciding the "
                    f"buyer and the promise again every week, separately", 3)
        if cadence_missing:
            return ("computable for the roles whose cadence you supplied; the rest are unstated "
                    "rather than zero", 3)
        if fit["status"] == "skipped":
            return ("the load is counted; whether it fits is unanswered because no capacity was "
                    "stated", 3)
        if strategy_status == "planned":
            return ("the counted load fits the stated capacity, and the strategy the recurring "
                    "work stands on is in the setup list rather than already written", 3)
        if strategy_status != "held":
            return ("the counted load fits the stated capacity; no selected role stands on the "
                    "positioning platform, so nothing here needed it", 0)
        return ("the counted load fits the stated capacity, and the strategy the recurring work "
                "stands on already exists", 0)


def render(report: dict, load: OperatingLoad) -> str:
    lines: list[str] = ["Operating load", "=" * 14, ""]
    lines.append(f"Roles: {', '.join(report['roles_selected'])}")
    if report["have"]:
        lines.append(f"Already held: {', '.join(report['have'])}")
    lines.append("")

    lines.append(f"Run once, before the weekly machine works ({report['setup_count']} commands)")
    lines.append("-" * 66)
    for row in report["setup_roles"]:
        lines.append(f"  {row['role']:<12} {row['runs_per_cycle']} commands, {row['recurs']}")
        lines.append(f"               {' -> '.join(row['commands'])}")
    if report["setup_runs_once"]:
        lines.append("  upstream     " + " -> ".join(report["setup_runs_once"]))
    if not report["setup_count"]:
        lines.append("  Nothing. Everything upstream is either held or done on a cadence.")
    lines.append("")

    lines.append("Every week")
    lines.append("-" * 66)
    for row in report["weekly"]:
        runs = row["weekly_runs"]
        rate = row["cycles_per_week"]
        shown = f"{runs:g} runs/week" if runs is not None else "not counted"
        lines.append(f"  {row['role']:<12} {shown:<16} {row['runs_per_cycle']} commands"
                     f" x {rate if rate is not None else '?'} cycles")
        lines.append(f"               {' -> '.join(row['commands'])}")
    lines.append("")
    lines.append(f"  Counted total: {report['weekly_command_runs']:g} command-runs per week")
    lines.append(f"  This is a floor, not a total. It is not {report['weekly_count_is_a_floor_because']}.")
    lines.append("")

    if report["not_counted"]:
        lines.append("Carried but not counted")
        lines.append("-" * 66)
        for row in report["not_counted"]:
            lines.append(f"  {row['role']} ({row['role_vi']}), {row['recurs']}")
            lines.append(f"    {row['why_not_counted']}")
        lines.append("")

    if report["cadence_not_supplied"]:
        lines.append("Cadence not supplied")
        lines.append("-" * 66)
        for row in report["cadence_not_supplied"]:
            lines.append(f"  {row['role']}: {row['why']}")
            lines.append(f"    supply {row['supply']}")
        lines.append("")

    if report["roles_depending_on_strategy"]:
        names = ", ".join(report["roles_depending_on_strategy"])
        planned = report["strategy"] == "planned"
        lines.append("Standing on a positioning platform that is "
                     + ("planned but not written yet" if planned else "neither written nor planned"))
        lines.append("-" * 66)
        lines.append(f"  {names}")
        lines.append("  Until it is written, each of these decides the buyer and the promise again,")
        lines.append("  weekly, separately, and they will not agree.")
        lines.append(f"  The role that settles it is `{STRATEGY_ROLE}`"
                     f" ({load.by_role[STRATEGY_ROLE]['role_vi']}), and its own row says:")
        lines.append(f"    {load.by_role[STRATEGY_ROLE]['slips_when_busy']}")
        lines.append("")

    fit = report["capacity_check"]
    lines.append(f"Capacity check: {fit['status']}")
    lines.append("-" * 66)
    lines.append(f"  {fit['why']}")
    if fit["status"] in {"passed", "failed", "review"}:
        lines.append(f"  stated {fit['stated_capacity']:g}, counted {fit['counted_load']:g},"
                     f" headroom {fit['headroom']:g}")
    else:
        lines.append(f"  {fit['supply']}")
    lines.append("")
    lines.append(f"Verdict: {report['verdict']}")
    lines.append("")
    return "\n".join(lines)


def render_roles(load: OperatingLoad) -> str:
    lines = ["Roles one Vietnamese marketing hire is holding", "=" * 45, ""]
    for row in load.roles:
        commands = row["commands"] or "(no command in the surface covers this)"
        lines.append(f"{row['role_id']}  -  {row['role_vi']} / {row['role_en']}")
        lines.append(f"  recurs:   {row['recurs']}")
        lines.append(f"  commands: {commands}")
        lines.append(f"  slips:    {row['slips_when_busy']}")
        lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Count the recurring marketing work one person is carrying, against the "
                    "command surface. Counts work items, never hours.")
    parser.add_argument("--roles", nargs="+", metavar="ROLE",
                        help="role ids to include; default is every role in the table")
    parser.add_argument("--cadence", nargs="+", default=[], metavar="ROLE=N",
                        help="cycles per week for a role, e.g. photo=0.5 koc=0.25")
    parser.add_argument("--capacity", type=float, metavar="N",
                        help="command-runs per week you can sustain; without it the fit check is "
                             "reported as skipped, not passed")
    parser.add_argument("--have", nargs="+", default=[], metavar="ARTIFACT",
                        help="artefacts that already exist, e.g. positioning-platform")
    parser.add_argument("--list-roles", action="store_true",
                        help="print the role table and stop")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--output", metavar="PATH", help="write to this file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        load = OperatingLoad(load_roles(), Surface.load())
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.list_roles:
        emit(render_roles(load), args.output)
        return 0

    role_ids = args.roles or [row["role_id"] for row in load.roles]
    unknown = [name for name in role_ids if name not in load.by_role]
    if unknown:
        print(f"error: no such role: {', '.join(unknown)}", file=sys.stderr)
        print(f"       known roles: {', '.join(load.by_role)}", file=sys.stderr)
        return 1

    try:
        cadence = parse_cadence(args.cadence)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    stray = [name for name in cadence if name not in role_ids]
    if stray:
        print(f"error: --cadence names a role that is not selected: {', '.join(stray)}",
              file=sys.stderr)
        return 1

    have = set(args.have)
    known_artifacts = set(load.surface.producer)
    unknown_have = sorted(have - known_artifacts)
    if unknown_have:
        print(f"error: no command produces: {', '.join(unknown_have)}", file=sys.stderr)
        return 1

    report = load.report(role_ids, cadence, have, args.capacity)
    if args.format == "json":
        emit_json(report, args.output)
    else:
        emit(render(report, load), args.output)
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
