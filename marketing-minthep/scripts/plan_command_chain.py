#!/usr/bin/env python3
"""Compute the shortest command chain from what somebody already has to what they asked for.

A request almost never arrives at the start of the work. It arrives as "make me marketplace
photos from this one packshot", or "why did last month's campaign do nothing", and the honest
answer depends entirely on which artefacts already exist. Narrating that in prose invites two
failures: skipping a dependency because the chain read plausibly, and padding the chain with
upstream work nobody needed. Both are avoided by resolving it as a graph.

`data/command-artifacts.csv` is that graph. Each command declares what it cannot run without
(`takes`), what would improve it (`also_uses`), and what it produces. This script walks the
required edges backwards from a goal, stops at what the user says they have, and returns the
commands in an order where every command's inputs exist before it runs.

    plan_command_chain.py --goal expand --have source-photograph creative-brief
    plan_command_chain.py --goal composition-set --have source-photograph --format text
    plan_command_chain.py --verify stage shoot produce
    plan_command_chain.py --explain colour

What this script cannot tell you: whether the goal is the right goal. It will happily plan a
faultless chain to a campaign that should not run. Choosing the goal is the director's job and
the reason `refuses` is printed with every command rather than hidden in a reference.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

TABLE = Path(__file__).resolve().parent.parent / "data" / "command-artifacts.csv"

# Artefacts no command produces. They come out of the world: a request in somebody's own words,
# and a photograph taken with a camera. A plan that silently invented either would be a plan to
# fabricate the brief, which is the failure this skill exists to prevent.
ROOT_ARTIFACTS = ("cold-brief", "source-photograph")

CATEGORY_ORDER = ("discover", "decide", "create", "direct", "activate", "evaluate")


def split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


class Surface:
    """The command graph, loaded once and queried by goal."""

    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows
        self.by_command = {row["command"]: row for row in rows}
        self.producer: dict[str, str] = {}
        for row in rows:
            self.producer[row["produces"]] = row["command"]
            # A stand-in is recorded on the producing row rather than in this script, so adding
            # one is a data edit. Generated images are a usable source photograph for `expand`;
            # asserting that in code would hide it from anyone reading the table.
            for alias in split_list(row.get("also_satisfies", "")):
                self.producer.setdefault(alias, row["command"])

    @classmethod
    def load(cls, path: Path = TABLE) -> "Surface":
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            raise ValueError(f"{path} has no commands")
        return cls(rows)

    def resolve_goal(self, goal: str) -> str:
        """Accept either a command name or the artefact somebody wants, and return the command."""
        goal = goal.strip().lower().replace("_", "-")
        if goal in self.by_command:
            return goal
        if goal in self.producer:
            return self.producer[goal]
        raise KeyError(goal)

    def plan(self, goal: str, have: set[str]) -> dict:
        command = self.resolve_goal(goal)
        order: list[str] = []
        weak: list[dict] = []
        supply: list[dict] = []
        visiting: list[str] = []

        def visit(name: str) -> None:
            if name in order:
                return
            if name in visiting:
                # A cycle would mean the table claims a command needs its own output. The graph
                # check in authoring rejects that, so reaching here means the table was edited
                # by hand past the check; say so rather than recursing to a stack overflow.
                raise ValueError(f"circular dependency: {' -> '.join(visiting + [name])}")
            visiting.append(name)
            row = self.by_command[name]
            for artifact in split_list(row["takes"]):
                if artifact in have:
                    continue
                producer = self.producer.get(artifact)
                if producer is None:
                    supply.append({"artifact": artifact, "needed_by": name,
                                   "why": "no command produces this; only you can supply it"})
                    continue
                visit(producer)
            visiting.pop()
            order.append(name)
            for artifact in split_list(row.get("also_uses", "")):
                if artifact in have or artifact in {self.by_command[c]["produces"] for c in order}:
                    continue
                weak.append({"command": name, "missing": artifact,
                             "effect": "the command still runs; this input would make it stronger"})

        visit(command)
        order = self.order_chain(set(order), have)
        steps = []
        for position, name in enumerate(order, start=1):
            row = self.by_command[name]
            steps.append({
                "step": position,
                "command": name,
                "category": row["category"],
                "does": row["does"],
                "needs": split_list(row["takes"]),
                "produces": row["produces"],
                "refuses": row["refuses"],
                "read": split_list(row["machinery"]),
            })
        return {
            "goal": command,
            "goal_artifact": self.by_command[command]["produces"],
            "have": sorted(have),
            "steps": steps,
            "commands": order,
            "you_must_supply": _dedupe(supply, "artifact"),
            "weaker_without": _dedupe(weak, "missing"),
            "shortest_chain": " -> ".join(order),
            "collapse_if_you_have": self.collapse(command, have, order),
        }

    def order_chain(self, required: set[str], have: set[str]) -> list[str]:
        """Sort the required commands so dependencies come first, breaking ties by category.

        Depth-first order is already runnable, but it is not readable: it can legitimately put
        `research` after `segment` because research only needs the opportunity map. A plan is
        read by a person deciding what to do on Monday, and discover-before-decide is how that
        person expects the week to run. So among the commands whose inputs are all satisfied,
        take the earliest category first, and the alphabetically first command within it. The
        result is still a valid topological order; it is just the one a director would write."""
        ready = dict(self.producer)  # artefact -> producing command, for dependency lookup
        satisfied = set(have)
        remaining = set(required)
        chain: list[str] = []
        while remaining:
            available = [
                name for name in remaining
                if all(a in satisfied or ready.get(a) not in remaining
                       for a in split_list(self.by_command[name]["takes"]))
            ]
            if not available:
                # Every remaining command is waiting on another remaining command. The authoring
                # graph check rejects cycles, so this means the table was hand-edited past it.
                raise ValueError(f"cannot order: {sorted(remaining)} block each other")
            available.sort(key=lambda name: (
                CATEGORY_ORDER.index(self.by_command[name]["category"]), name))
            chosen = available[0]
            chain.append(chosen)
            remaining.discard(chosen)
            satisfied.add(self.by_command[chosen]["produces"])
            satisfied.update(split_list(self.by_command[chosen].get("also_satisfies", "")))
        return chain

    def collapse(self, command: str, have: set[str], order: list[str]) -> list[dict]:
        """Rank the artefacts whose existence would shorten this chain the most.

        Somebody arriving with a packshot and the words "just make me marketplace photos" is
        not wrong to resent an eight-command answer. But the honest reply is not to skip the
        strategy; it is to point out that most of the chain is asking for things they already
        know. A shop owner can state their buyer and their promise in two sentences. Saying
        `--have positioning-platform` after that is not a shortcut, it is an accurate
        description of what exists, and it removes five commands. This function computes which
        assertion is worth the most, so the trade is a number the user can weigh rather than a
        negotiation they have to win."""
        savings: list[dict] = []
        for name in order[:-1]:
            artifact = self.by_command[name]["produces"]
            if artifact in have:
                continue
            shorter = self.plan_length(command, have | {artifact})
            if shorter is None or shorter >= len(order):
                continue
            savings.append({"if_you_already_have": artifact,
                            "chain_drops_to": shorter,
                            "commands_saved": len(order) - shorter,
                            "instead_of_running": name})
        savings.sort(key=lambda item: (-item["commands_saved"], item["if_you_already_have"]))
        return savings

    def plan_length(self, command: str, have: set[str]) -> int | None:
        """Chain length only, with no collapse analysis, so `collapse` cannot recurse."""
        order: list[str] = []

        def visit(name: str) -> None:
            if name in order:
                return
            for artifact in split_list(self.by_command[name]["takes"]):
                if artifact in have:
                    continue
                producer = self.producer.get(artifact)
                if producer is not None:
                    visit(producer)
            order.append(name)

        try:
            visit(command)
        except RecursionError:
            return None
        return len(order)

    def verify(self, chain: list[str]) -> dict:
        """Check a chain somebody proposed, rather than inventing one for them."""
        unknown = [name for name in chain if name not in self.by_command]
        if unknown:
            raise KeyError(", ".join(unknown))
        available: set[str] = set(ROOT_ARTIFACTS)
        faults: list[dict] = []
        for position, name in enumerate(chain, start=1):
            row = self.by_command[name]
            for artifact in split_list(row["takes"]):
                if artifact not in available:
                    producer = self.producer.get(artifact, "(nothing)")
                    faults.append({
                        "at_step": position, "command": name, "missing": artifact,
                        "fix": f"run {producer} first" if producer != "(nothing)"
                               else f"supply {artifact} yourself",
                    })
            available.add(row["produces"])
            available.update(split_list(row.get("also_satisfies", "")))
        return {"chain": " -> ".join(chain), "runnable": not faults, "faults": faults,
                "assumed_supplied": list(ROOT_ARTIFACTS)}


def _dedupe(items: list[dict], key: str) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for item in items:
        if item[key] in seen:
            continue
        seen.add(item[key])
        out.append(item)
    return out


def render_plan(plan: dict) -> str:
    lines = [f"Goal: {plan['goal']} -> {plan['goal_artifact']}"]
    if plan["have"]:
        lines.append(f"Already have: {', '.join(plan['have'])}")
    lines.append(f"Chain ({len(plan['steps'])} commands): {plan['shortest_chain']}")
    lines.append("")
    for step in plan["steps"]:
        lines.append(f"{step['step']}. {step['command']} [{step['category']}]")
        lines.append(f"   {step['does']}.")
        lines.append(f"   needs: {', '.join(step['needs']) or '(nothing)'}")
        lines.append(f"   produces: {step['produces']}")
        lines.append(f"   read: {', '.join(step['read'])}")
        lines.append(f"   refuses: {step['refuses']}.")
        lines.append("")
    if plan["you_must_supply"]:
        lines.append("You must supply, because no command can produce it:")
        for item in plan["you_must_supply"]:
            lines.append(f"  {item['artifact']} - needed by {item['needed_by']}")
        lines.append("")
    if plan["collapse_if_you_have"]:
        lines.append("Shorter if these already exist, best saving first:")
        for item in plan["collapse_if_you_have"][:4]:
            lines.append(f"  {item['if_you_already_have']}: {len(plan['steps'])} commands "
                         f"drops to {item['chain_drops_to']}, saving {item['commands_saved']}")
        lines.append("")
    if plan["weaker_without"]:
        lines.append("Runs without these, but weaker:")
        for item in plan["weaker_without"]:
            lines.append(f"  {item['command']} would also use {item['missing']}")
        lines.append("")
    return "\n".join(lines)


def render_surface(surface: Surface) -> str:
    lines = [f"{len(surface.rows)} commands", ""]
    for category in CATEGORY_ORDER:
        rows = [r for r in surface.rows if r["category"] == category]
        lines.append(f"{category.upper()} ({len(rows)})")
        for row in rows:
            lines.append(f"  {row['command']:<11} {row['takes']:<44} -> {row['produces']}")
        lines.append("")
    return "\n".join(lines)


def render_command(row: dict) -> str:
    lines = [f"{row['command']} [{row['category']}]", "", f"{row['does']}.", ""]
    for label, key in (("Cannot run without", "takes"), ("Would also use", "also_uses"),
                       ("Produces", "produces"), ("Also satisfies", "also_satisfies"),
                       ("Usually followed by", "usual_next")):
        value = row.get(key, "")
        if value:
            lines.append(f"{label}: {value}")
    lines += ["", f"Read: {row['machinery']}", "", f"Refuses: {row['refuses']}.",
              f"Does not do: {row['what_it_does_not_do']}."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--goal", help="A command name, or the artefact you want.")
    parser.add_argument("--have", nargs="*", default=[],
                        help="Artefacts that already exist. Each one shortens the chain.")
    parser.add_argument("--verify", nargs="+", metavar="COMMAND",
                        help="Check whether a proposed chain can actually run in that order.")
    parser.add_argument("--explain", metavar="COMMAND", help="Print one command in full.")
    parser.add_argument("--list", action="store_true", help="Print the whole surface by category.")
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--output")
    args = parser.parse_args()

    use_utf8_stdout()
    try:
        surface = Surface.load()
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.list:
        if args.format == "text":
            emit(render_surface(surface), args.output)
        else:
            emit_json({"commands": surface.rows}, args.output)
        return 0

    if args.explain:
        row = surface.by_command.get(args.explain.strip().lower())
        if row is None:
            print(f"error: no command named {args.explain!r}. Try --list.", file=sys.stderr)
            return 1
        emit(render_command(row), args.output) if args.format == "text" \
            else emit_json(row, args.output)
        return 0

    if args.verify:
        try:
            report = surface.verify([c.strip().lower() for c in args.verify])
        except KeyError as exc:
            print(f"error: not a command: {exc}. Try --list.", file=sys.stderr)
            return 1
        emit_json(report, args.output)
        # An unrunnable chain is a finding, not a note. Exit non-zero so a caller that chains
        # on this stops rather than executing a sequence with a missing input.
        return 0 if report["runnable"] else 2

    if not args.goal:
        parser.print_help()
        return 1

    try:
        plan = surface.plan(args.goal, {a.strip().lower() for a in args.have})
    except KeyError as exc:
        print(f"error: no command or artefact named {exc}. Try --list.", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "text":
        emit(render_plan(plan), args.output)
    else:
        emit_json(plan, args.output)
    # A plan with an artefact only the user can supply is not a failure, but it is not runnable
    # as printed either. Exit 3 so the difference survives being piped somewhere.
    return 3 if plan["you_must_supply"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
