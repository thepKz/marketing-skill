#!/usr/bin/env python3
"""Read a makeup reference: narrow the candidates, then say what is still unanswered.

Somebody arrives holding a photograph and asks what the makeup is. The useless answer is a label --
"clean girl", "K-beauty glam" -- because a label is not executable and is usually wrong. This script
does three separate jobs instead, and keeps them separate on purpose:

  --observe   turn what you can see into a ranked shortlist, with the reason each row survived
  --ask       print the questions that would still cut the shortlist down, in the order that cuts most
  --brief     print one look as the nine-axis contract, ready to execute

Three things make it more than a grep over a CSV.

First, it reports what it cannot tell apart. A shortlist of one is a claim; a shortlist of four with
the discriminating question attached is a next step. Confidently naming one of four is the failure
mode this whole unit exists to prevent.

Second, it orders the remaining questions by how much they would actually cut, computed against the
current shortlist rather than fixed in the table. A question whose answers all keep the same rows is
not worth asking now even if it is marked high value in general.

Third, it will not print a brief without the three questions no photograph can answer -- rights,
what the product claims, and where the image will be seen. Those live in the diagnostics table
marked "blocking", and a brief that skips them is a brief that gets somebody into trouble later.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import pathlib
import sys
import unicodedata

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _emit import use_utf8_stdout  # noqa: E402  most of this table's content is Vietnamese

SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = SKILL_ROOT / "data"

# The nine axes of the makeup contract, in the order references/makeup-art-direction.md states them.
# The order is not cosmetic: base decisions constrain eye and lip decisions, so a brief read top to
# bottom is a brief that can be executed in that sequence.
AXES = (
    "skin_finish", "coverage_texture", "brows", "eyeshadow", "liner_lashes",
    "cheeks", "contour_highlight", "lips", "palette_retouch",
)

# Columns worth searching when somebody types what they see. The axes carry the observable detail;
# signature_tell and discriminator carry the shorthand people actually use, which is why "aegyo-sal"
# or "cut crease" finds anything at all.
SEARCH_FIELDS = AXES + ("name_vi", "name_en", "family", "origin", "signature_tell",
                        "discriminator", "photographs_as")

# Vietnamese and English both arrive, often in the same sentence, and a reader typing "mat meo"
# without diacritics should still find "Mắt mèo".
def fold(text: str) -> str:
    stripped = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in stripped if unicodedata.category(ch) != "Mn")


def table(name: str) -> list[dict[str, str]]:
    text = (DATA / name).read_text(encoding="utf-8")
    return list(csv.DictReader(io.StringIO(text)))


def looks() -> list[dict[str, str]]:
    return table("makeup-looks.csv")


def diagnostics() -> list[dict[str, str]]:
    return sorted(table("makeup-diagnostics.csv"), key=lambda row: int(row["sequence"]))


def terms(raw: str) -> list[str]:
    """Splits an observation string on commas and semicolons, not on spaces, because the useful
    observations are phrases. "outer third" split into two words matches almost every row."""
    parts = [part.strip() for chunk in raw.split(";") for part in chunk.split(",")]
    return [part for part in parts if part]


def score(look: dict[str, str], wanted: list[str]) -> tuple[int, list[str]]:
    """Counts how many observations this look accounts for, and names them.

    Deliberately not a similarity percentage. A percentage invites the reader to treat 62% as a
    finding, when what the number actually means is "four of your six phrases appear somewhere in
    this row". The hit list says that much and no more.
    """
    hits = []
    for term in wanted:
        needle = fold(term)
        for field in SEARCH_FIELDS:
            if needle in fold(look.get(field, "")):
                hits.append(f"{term} -> {field}")
                break
    return len(hits), hits


def shortlist(wanted: list[str], limit: int = 6) -> list[dict]:
    ranked = []
    for look in looks():
        count, hits = score(look, wanted)
        if count:
            ranked.append({"look": look, "matched": count, "hits": hits})
    # Ties broken by look_id so two runs of the same query cannot disagree about the order.
    ranked.sort(key=lambda row: (-row["matched"], row["look"]["look_id"]))
    return ranked[:limit]


def splits(question: dict[str, str], candidates: list[dict[str, str]]) -> dict[str, list[str]]:
    """Which candidates each answer to this question would keep.

    A look whose cell matches none of the offered answers survives every answer. That is not
    generosity, it is the only reading that is true: the options are a handful of phrases and the
    cells are prose, so matching nothing means the table does not say, which is different from the
    table disagreeing. Eliminating those looks would let a question appear to cut thirty candidates
    when what it really did was fail to describe them.
    """
    if question["field"] == "none":
        return {}
    field = question["field"]
    patterns = question["patterns"].lower().split("|")
    silent = [row["look_id"] for row in candidates
              if not any(pattern in row.get(field, "").lower() for pattern in patterns)]
    result = {}
    for option, pattern in zip(question["options_en"].split("|"), patterns):
        result[option] = sorted([row["look_id"] for row in candidates
                                 if pattern in row.get(field, "").lower()] + silent)
    return result


def cutting_power(question: dict[str, str], candidates: list[dict[str, str]]) -> int:
    """How many candidates the worst-case answer would remove.

    Worst case rather than average, because the point is to guarantee progress. A question whose
    best answer eliminates five and whose likeliest answer eliminates none has not earned its turn.
    """
    branches = splits(question, candidates)
    if not branches:
        return 0
    largest = max((len(kept) for kept in branches.values()), default=len(candidates))
    return len(candidates) - largest


def next_questions(candidates: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    """Returns (photo questions worth asking now, questions nothing in a photo can answer)."""
    photo, blocking = [], []
    for question in diagnostics():
        if question["information_value"] == "blocking":
            blocking.append(question)
            continue
        power = cutting_power(question, candidates)
        if power > 0:
            photo.append({"question": question, "cuts": power,
                          "branches": splits(question, candidates)})
    photo.sort(key=lambda row: (-row["cuts"], row["question"]["q_id"]))
    return photo, blocking


def by_id(look_id: str) -> dict[str, str]:
    for look in looks():
        if look["look_id"] == look_id:
            return look
    known = ", ".join(sorted(row["look_id"] for row in looks()))
    raise SystemExit(f"no look called {look_id!r}.\nknown: {known}")


def brief(look_id: str) -> dict:
    look = by_id(look_id)
    _, blocking = next_questions([look])
    return {
        "look_id": look["look_id"],
        "name_en": look["name_en"],
        "name_vi": look["name_vi"],
        "family": look["family"],
        "origin": look["origin"],
        "contract": {axis: look[axis] for axis in AXES},
        "signature_tell": look["signature_tell"],
        "confused_with": look["confused_with"],
        "discriminator": look["discriminator"],
        "photographs_as": look["photographs_as"],
        "use_when": look["use_when"],
        "avoid_when": look["avoid_when"],
        "evidence_grade": look["evidence_grade"],
        "source": look["source"],
        # Carried into the brief rather than mentioned in a doc, because a brief is what gets
        # forwarded, and whatever is not in it does not get asked.
        "before_you_shoot": [
            {"ask": question["question_en"], "ask_vi": question["question_vi"],
             "why": question["why_it_matters"]}
            for question in blocking
        ],
    }


def wrap(text: str, width: int = 92, indent: str = "    ") -> str:
    words, lines, current = text.split(), [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return "\n".join(indent + line for line in lines)


def report_observe(wanted: list[str], ranked: list[dict]) -> str:
    out = [f"Observed: {', '.join(wanted)}", ""]
    if not ranked:
        out += ["Nothing matched.", "",
                wrap("The table is searched by what is visible, not by style names. Describe the "
                     "surface instead: where the liner is thickest, what happens at the lip border, "
                     "whether a crease is built, where the blush sits.", indent="")]
        return "\n".join(out)

    top = ranked[0]["matched"]
    tied = [row for row in ranked if row["matched"] == top]
    out.append(f"{len(ranked)} candidate(s); {len(tied)} tied at the top on {top} observation(s).")
    out.append("")
    # An observation nothing matched is not evidence for the shortlist, and staying quiet about it
    # would let one matched phrase wear the confidence of three.
    unmatched = [term for term in wanted
                 if not any(hit.startswith(f"{term} ->") for row in ranked for hit in row["hits"])]
    if unmatched:
        out.append(f"Matched nothing, so the ranking ignores it: {', '.join(unmatched)}")
        out.append(wrap("The table speaks in surface phrases -- try the words a zoomed-in photo "
                        "would force: where the shine sits, where the liner is thickest, what "
                        "happens at the lip border.", indent="  "))
        out.append("")
    for row in ranked:
        look = row["look"]
        out.append(f"  {look['look_id']:<24} {look['name_en']}  [{row['matched']}]")
        out.append(f"    {look['name_vi']} · {look['family']} · {look['evidence_grade']}")
        out.append(wrap(f"tell: {look['signature_tell']}", indent="      "))
        for hit in row["hits"]:
            out.append(f"      matched {hit}")
        out.append("")

    if len(tied) > 1:
        out += ["Cannot yet tell apart:", ""]
        for row in tied:
            look = row["look"]
            out.append(f"  {look['look_id']} vs {look['confused_with']}")
            out.append(wrap(look["discriminator"], indent="      "))
            out.append("")

    photo, blocking = next_questions([row["look"] for row in ranked])
    if photo:
        out += ["Ask the photograph next, most cutting first:", ""]
        for entry in photo[:4]:
            question = entry["question"]
            out.append(f"  [{question['q_id']}] cuts at least {entry['cuts']} of {len(ranked)}")
            out.append(wrap(question["question_en"], indent="      "))
            out.append(wrap(f"VI: {question['question_vi']}", indent="      "))
            out.append(wrap(f"look at: {question['look_where']}", indent="      "))
            out.append(wrap(f"trap: {question['trap']}", indent="      "))
            out.append("")
    else:
        out += ["No remaining photo question would cut this shortlist further.", ""]

    out += ["Ask the person, because no photograph answers these:", ""]
    for question in blocking:
        out.append(f"  [{question['q_id']}] {question['question_en']}")
        out.append(wrap(f"VI: {question['question_vi']}", indent="      "))
        out.append(wrap(question["why_it_matters"], indent="      "))
        out.append("")
    return "\n".join(out)


def report_ask() -> str:
    out = ["The full diagnostic sequence.", "",
           wrap("Read the photograph for the first eleven. Ask the person the last four -- nothing "
                "in an image answers them, and a brief that skips them is the one that causes "
                "trouble after the shoot rather than during it.", indent=""), ""]
    for question in diagnostics():
        marker = "ASK" if question["ask_of"] == "user" else "SEE"
        out.append(f"[{question['q_id']}] {marker}  ({question['information_value']})")
        out.append(wrap(question["question_en"], indent="    "))
        out.append(wrap(f"VI: {question['question_vi']}", indent="    "))
        out.append(wrap(f"look at: {question['look_where']}", indent="    "))
        out.append(wrap(f"options: {question['options_en'].replace('|', ' / ')}", indent="    "))
        out.append(wrap(f"why: {question['why_it_matters']}", indent="    "))
        out.append(wrap(f"trap: {question['trap']}", indent="    "))
        out.append("")
    return "\n".join(out)


def report_brief(data: dict) -> str:
    out = [f"{data['name_en']}  ({data['look_id']})",
           f"{data['name_vi']} · {data['family']} · {data['origin']}",
           f"evidence: {data['evidence_grade']}", wrap(data["source"], indent="  "), "",
           "Nine-axis contract", ""]
    for axis, value in data["contract"].items():
        out.append(f"  {axis}")
        out.append(wrap(value, indent="      "))
    out += ["", "Identify it by", "", wrap(data["signature_tell"], indent="  "), "",
            f"Confused with {data['confused_with']}", "", wrap(data["discriminator"], indent="  "),
            "", "Light", "", wrap(data["photographs_as"], indent="  "),
            "", "Use when", "", wrap(data["use_when"], indent="  "),
            "", "Avoid when", "", wrap(data["avoid_when"], indent="  "),
            "", "Settle before shooting", ""]
    for item in data["before_you_shoot"]:
        out.append(f"  - {item['ask']}")
        out.append(wrap(f"VI: {item['ask_vi']}", indent="      "))
        out.append(wrap(item["why"], indent="      "))
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--observe", help="what you can see, comma separated, VI or EN")
    parser.add_argument("--ask", action="store_true", help="print the full diagnostic sequence")
    parser.add_argument("--brief", help="a look_id, printed as the nine-axis contract")
    parser.add_argument("--list", action="store_true", help="every look, by family")
    parser.add_argument("--format", choices=("report", "json"), default="report")
    args = parser.parse_args()
    use_utf8_stdout()

    if args.brief:
        data = brief(args.brief)
        print(json.dumps(data, ensure_ascii=False, indent=2) if args.format == "json"
              else report_brief(data))
        return 0

    if args.ask:
        if args.format == "json":
            print(json.dumps(diagnostics(), ensure_ascii=False, indent=2))
        else:
            print(report_ask())
        return 0

    if args.list:
        rows = sorted(looks(), key=lambda row: (row["family"], row["look_id"]))
        if args.format == "json":
            print(json.dumps(rows, ensure_ascii=False, indent=2))
            return 0
        family = None
        for look in rows:
            if look["family"] != family:
                family = look["family"]
                print(f"\n{family}")
            print(f"  {look['look_id']:<24} {look['name_en']:<38} {look['name_vi']}")
        print(f"\n{len(rows)} looks")
        return 0

    if args.observe:
        wanted = terms(args.observe)
        ranked = shortlist(wanted)
        if args.format == "json":
            photo, blocking = next_questions([row["look"] for row in ranked])
            print(json.dumps({
                "observed": wanted,
                "candidates": [{"look_id": row["look"]["look_id"],
                                "name_en": row["look"]["name_en"],
                                "matched": row["matched"], "hits": row["hits"],
                                "discriminator": row["look"]["discriminator"]} for row in ranked],
                "ask_photo": [{"q_id": entry["question"]["q_id"], "cuts": entry["cuts"],
                               "question_en": entry["question"]["question_en"],
                               "branches": entry["branches"]} for entry in photo],
                "ask_user": [{"q_id": question["q_id"],
                              "question_en": question["question_en"]} for question in blocking],
            }, ensure_ascii=False, indent=2))
        else:
            print(report_observe(wanted, ranked))
        # A shortlist that has not been narrowed to one is not a failure, but it is not an answer
        # either, and a pipeline should be able to tell the difference without parsing prose.
        return 0 if len(ranked) == 1 else 2

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
