#!/usr/bin/env python3
"""Build a fictional adult virtual person as a parameter sheet, so the same person can be rendered twice.

The commercial requirement for a brand face is not that one image is beautiful. It is that the same
face appears in fifty posts over two years. That is a reproducibility problem, and the version of this
script that this one replaces could not solve it: it described a face as "warm, polished, inviting" and
a build as "slender-light-frame", then recommended one of four fixed bundles by keyword match, with no
seed. Two runs of the same request produced the same adjectives and different people.

Two arguments settle the design, and both are arithmetic rather than taste.

The first is that this skill's own gate condemns adjectives. Feed the old vocabulary to
`check_specificity.py --text` and it comes back `failed`: 41 words, 0 checkable things, fact-floor
failed, brand-swap 100 percent - all three sentences listed as ones a competitor could ship unchanged.
A registry that cannot pass the gate the same skill ships is not a registry, it is a mood board.

The second is that a number is transmissible and an adjective is not. "Slender" survives no round trip:
the person who wrote it, the person who prompts with it and the model that renders it hold three
different pictures. `7.5 head units, shoulders 2.1 head widths, shoulder-to-waist 1.3` survives all
three, can be diffed when a render drifts, and can be hashed.

So `data/person-parameters.csv` carries one row per measurable axis, and this script does four things
with it:

Resolve. Unspecified axes take the table's `neutral_value`. Specified ones are range-checked where the
domain is numeric - and the report says how many axes it could check and how many it could not, because
a validator that quietly passes what it cannot parse teaches you to trust it further than it earns.

Split. Seventeen axes are `locked` and thirteen are `styling`. The locked block is the person. The
styling block is the campaign: pose, camera, makeup. Mixing them is the specific mistake that ends with
a character whose jaw changes when the lipstick does.

Hash. The locked block, canonicalised and sorted, hashes to a `person_id` and a derived seed. Same
locked values, same id, same seed, on any machine, in any order the flags were typed. That is the whole
mechanism: identity is a function of the parameters, not of a saved file someone has to not lose.

Diff. `--verify` recomputes the id from a saved sheet and fails if it moved. `--drift` compares two
sheets and names the axes that changed. When a render stops looking like the character, this answers
which parameter moved instead of inviting another guess at the prompt.

What it will not do. It does not generate anything, call a provider, or hold a key - it emits a prompt
fragment carrying the numbers and stops. It does not judge whether the person is appealing. And it
refuses to build a minor, before parsing anything else.

Makeup is not re-invented here. `data/makeup-looks.csv` already carries 47 looks with a discriminator
column; `--makeup` takes a `look_id` from that table and is validated against it.

Everything is stdlib.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
PARAMS_TABLE = DATA / "person-parameters.csv"
MAKEUP_TABLE = DATA / "makeup-looks.csv"

NUMERIC_DOMAIN = re.compile(r"^([+-]?\d+(?:\.\d+)?)\s+to\s+([+-]?\d+(?:\.\d+)?)$")

EXIT_OK = 0
EXIT_USAGE = 1
EXIT_FAILED = 2
EXIT_REVIEW = 3


def _read(path: Path) -> list[dict]:
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8"))))


def load_parameters() -> dict[str, dict]:
    rows = _read(PARAMS_TABLE)
    return {row["param_id"]: row for row in rows}


def load_makeup_ids() -> dict[str, str]:
    return {row["look_id"]: row["name_en"] for row in _read(MAKEUP_TABLE)}


def check_value(param: dict, value: str) -> str | None:
    """Return an error string, or None when the value is acceptable or uncheckable.

    Uncheckable is not the same as acceptable, and the caller reports the two separately.
    """
    match = NUMERIC_DOMAIN.match(param["input_domain"].strip())
    if match is None:
        return None
    low, high = float(match.group(1)), float(match.group(2))
    try:
        number = float(str(value).strip().lstrip("+"))
    except ValueError:
        return f"{param['param_id']} takes a number in {param['input_domain']} ({param['unit']}), got {value!r}"
    if not low <= number <= high:
        return f"{param['param_id']} = {number} is outside {param['input_domain']} ({param['unit']})"
    return None


def canonical(locked: dict[str, str]) -> str:
    """The exact string that gets hashed. Sorted, so flag order cannot change the identity."""
    return "\n".join(f"{key}={locked[key]}" for key in sorted(locked))


def identity(locked: dict[str, str]) -> dict:
    digest = hashlib.blake2s(canonical(locked).encode("utf-8"), digest_size=8).hexdigest()
    return {
        "person_id": f"vp-{digest[:12]}",
        "seed": int(digest, 16) % (2**31 - 1),
        "hashed_axes": len(locked),
        "hash": f"blake2s-64 over {len(locked)} sorted param=value lines",
    }


def build(request: dict) -> dict:
    if request.get("minor") is True:
        raise ValueError("This workflow supports fictional adults only")

    table = load_parameters()
    supplied = dict(request.get("values") or {})
    unknown = sorted(set(supplied) - set(table))
    if unknown:
        raise ValueError(f"not axes in person-parameters.csv: {', '.join(unknown)}")

    errors, resolved, unchecked = [], {}, []
    for param_id, param in table.items():
        if param_id in supplied:
            value, origin = str(supplied[param_id]), "supplied"
            problem = check_value(param, value)
            if problem:
                errors.append(problem)
            elif NUMERIC_DOMAIN.match(param["input_domain"].strip()) is None:
                unchecked.append(param_id)
        else:
            value, origin = param["neutral_value"], "neutral default"
        resolved[param_id] = {
            "value": value,
            "origin": origin,
            "unit": param["unit"],
            "lock_class": param["lock_class"],
            "group": param["group"],
            "name_en": param["name_en"],
            "phrasing": param["prompt_phrasing"],
            "term_grade": param["term_grade"],
        }

    makeup = request.get("makeup")
    makeup_block = None
    if makeup:
        looks = load_makeup_ids()
        if makeup not in looks:
            errors.append(f"makeup {makeup!r} is not a look_id in makeup-looks.csv")
        else:
            makeup_block = {"look_id": makeup, "name_en": looks[makeup], "table": "data/makeup-looks.csv"}

    locked = {pid: row["value"] for pid, row in resolved.items() if row["lock_class"] == "locked"}
    styling = {pid: row["value"] for pid, row in resolved.items() if row["lock_class"] == "styling"}
    ident = identity(locked)

    unnamed = [pid for pid, row in resolved.items()
               if row["lock_class"] == "locked" and row["origin"] == "neutral default"]

    verdict = "failed" if errors else ("review" if len(unnamed) > len(locked) // 2 else "passed")

    return {
        "verdict": verdict,
        "adult_only": True,
        "purpose": request.get("purpose") or "brand-face",
        "identity": ident,
        "locked_identity": {pid: resolved[pid] for pid in sorted(locked)},
        "campaign_styling": {pid: resolved[pid] for pid in sorted(styling)},
        "makeup": makeup_block,
        "prompt_fragments": {
            "identity": fragment(resolved, "locked"),
            "styling": fragment(resolved, "styling"),
        },
        "coverage": {
            "axes": len(table),
            "locked_axes": len(locked),
            "styling_axes": len(styling),
            "supplied": sorted(supplied),
            "left_at_neutral_default": sorted(unnamed),
            "domain_range_checked": sum(
                1 for p in table.values() if NUMERIC_DOMAIN.match(p["input_domain"].strip())),
            "domain_not_machine_checkable": sorted(
                p["param_id"] for p in table.values()
                if NUMERIC_DOMAIN.match(p["input_domain"].strip()) is None),
        },
        "errors": errors,
        "notes": [
            "A locked axis left at its neutral default is not a decision, it is a value nobody chose. "
            "It still hashes, so the person is reproducible - but every neutral default is an axis the "
            "character shares with every other character built from this table.",
            "The seed reproduces a person only inside one model at one version. Providers do not "
            "guarantee cross-version determinism; the sheet is what survives a version change, not the "
            "seed.",
        ],
        "next_step": "Save this sheet, then re-run with --verify before every campaign so a changed "
                     "locked axis is caught here rather than in the render.",
    }


def phrase(row: dict) -> str:
    """The clause for one axis.

    `prompt_phrasing` in the table is written around that axis's neutral value, so quoting it for a
    value somebody actually chose would print "about seven and a half head heights" for a supplied
    7.4. A sheet whose prompt fragment contradicts its own numbers is worse than no sheet, because the
    numbers are what the render gets checked against. So a supplied value is phrased from the value.
    """
    if row["origin"] != "supplied":
        return row["phrasing"]
    try:
        float(str(row["value"]).lstrip("+"))
    except ValueError:
        # A free-text axis - the distinguishing mark, the posture signature - is already a clause.
        return str(row["value"])
    name = row["name_en"][0].lower() + row["name_en"][1:]
    unit = "" if row["unit"] == "ratio" else f" {row['unit']}"
    return f"{name} {row['value']}{unit}"


def fragment(resolved: dict, lock_class: str) -> str:
    order = ("face", "build", "pose", "camera")
    parts = []
    for group in order:
        parts.extend(phrase(row) for row in resolved.values()
                     if row["lock_class"] == lock_class and row["group"] == group)
    return "; ".join(parts)


def verify(sheet: dict) -> dict:
    locked = {pid: row["value"] for pid, row in (sheet.get("locked_identity") or {}).items()}
    if not locked:
        raise ValueError("sheet has no locked_identity block")
    recomputed = identity(locked)
    claimed = (sheet.get("identity") or {}).get("person_id")
    same = claimed == recomputed["person_id"]
    return {
        "verdict": "passed" if same else "failed",
        "claimed_person_id": claimed,
        "recomputed_person_id": recomputed["person_id"],
        "seed": recomputed["seed"],
        "detail": "locked identity is intact" if same else
                  "a locked axis changed after this sheet was written; run --drift against the "
                  "original sheet to see which one",
    }


def drift(before: dict, after: dict) -> dict:
    lhs = {pid: row["value"] for pid, row in (before.get("locked_identity") or {}).items()}
    rhs = {pid: row["value"] for pid, row in (after.get("locked_identity") or {}).items()}
    moved = {pid: {"before": lhs[pid], "after": rhs[pid]}
             for pid in sorted(set(lhs) & set(rhs)) if lhs[pid] != rhs[pid]}
    only_before = sorted(set(lhs) - set(rhs))
    only_after = sorted(set(rhs) - set(lhs))
    return {
        "verdict": "passed" if not (moved or only_before or only_after) else "failed",
        "moved": moved,
        "dropped": only_before,
        "added": only_after,
        "detail": "the two sheets describe the same person" if not moved else
                  f"{len(moved)} locked {'axis' if len(moved) == 1 else 'axes'} moved: "
                  f"{', '.join(moved)}",
    }


def render_text(payload: dict) -> str:
    lines = [f"# virtual person - verdict {payload['verdict']}"]
    ident = payload["identity"]
    lines.append(f"{ident['person_id']}  seed {ident['seed']}  ({ident['hash']})")
    cov = payload["coverage"]
    lines.append(f"{cov['locked_axes']} locked axes, {cov['styling_axes']} styling axes, "
                 f"{cov['domain_range_checked']} of {cov['axes']} domains range-checkable")
    if cov["left_at_neutral_default"]:
        lines.append(f"left at neutral default: {len(cov['left_at_neutral_default'])} of "
                     f"{cov['locked_axes']} locked axes")
    if payload["makeup"]:
        lines.append(f"makeup: {payload['makeup']['look_id']} ({payload['makeup']['name_en']})")
    lines.append("")
    lines.append("## locked identity")
    for pid, row in payload["locked_identity"].items():
        mark = " " if row["origin"] == "supplied" else "~"
        lines.append(f"{mark} {pid:<30} {row['value']:<24} {row['unit']}")
    lines.append("")
    lines.append("## identity prompt fragment")
    lines.append(payload["prompt_fragments"]["identity"])
    lines.append("")
    lines.append("## styling prompt fragment")
    lines.append(payload["prompt_fragments"]["styling"])
    if payload["errors"]:
        lines.append("")
        lines.append("## errors")
        lines.extend(f"- {problem}" for problem in payload["errors"])
    lines.append("")
    lines.append("~ marks an axis left at the table's neutral default rather than chosen.")
    return "\n".join(lines) + "\n"


def parse_assignment(text: str) -> tuple[str, str]:
    if "=" not in text:
        raise argparse.ArgumentTypeError(f"expected param_id=value, got {text!r}")
    key, value = text.split("=", 1)
    return key.strip(), value.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a reproducible fictional adult virtual person from data/person-parameters.csv.")
    parser.add_argument("--set", nargs="+", default=[], type=parse_assignment, metavar="ID=VALUE",
                        help="assign an axis, e.g. --set stature-head-units=7.4 canthal-tilt=6")
    parser.add_argument("--purpose", help="what job this person does for the brand")
    parser.add_argument("--makeup", metavar="LOOK_ID", help="a look_id from data/makeup-looks.csv")
    parser.add_argument("--input", metavar="PATH", help="JSON request file instead of flags")
    parser.add_argument("--verify", metavar="PATH", help="recompute the person_id of a saved sheet")
    parser.add_argument("--drift", nargs=2, metavar=("BEFORE", "AFTER"),
                        help="name the locked axes that moved between two sheets")
    parser.add_argument("--list-axes", action="store_true", help="print the parameter table and exit")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--output", metavar="PATH")
    args = parser.parse_args(argv)

    use_utf8_stdout()

    if args.list_axes:
        rows = _read(PARAMS_TABLE)
        lines = [f"{len(rows)} axes in person-parameters.csv", ""]
        for row in rows:
            lines.append(f"[{row['lock_class']:<7}] {row['group']:<7} {row['param_id']:<30} "
                         f"{row['input_domain']:<34} {row['unit']}")
        emit("\n".join(lines) + "\n", args.output)
        return EXIT_OK

    try:
        if args.verify:
            payload = verify(json.loads(Path(args.verify).read_text(encoding="utf-8")))
        elif args.drift:
            payload = drift(*(json.loads(Path(p).read_text(encoding="utf-8")) for p in args.drift))
        else:
            request = json.loads(Path(args.input).read_text(encoding="utf-8")) if args.input else {}
            request.setdefault("values", {})
            request["values"].update(dict(args.set))
            if args.purpose:
                request["purpose"] = args.purpose
            if args.makeup:
                request["makeup"] = args.makeup
            payload = build(request)
    except (ValueError, OSError, json.JSONDecodeError) as problem:
        print(f"error: {problem}", file=sys.stderr)
        return EXIT_USAGE

    if args.format == "json" or "locked_identity" not in payload:
        emit_json(payload, args.output)
    else:
        emit(render_text(payload), args.output)

    return {"passed": EXIT_OK, "review": EXIT_REVIEW, "failed": EXIT_FAILED}[payload["verdict"]]


# Kept so callers importing the old entry point still work; the sheet is the return value now.
def plan_virtual_person(request: dict) -> dict:
    return build(request)


if __name__ == "__main__":
    sys.exit(main())
