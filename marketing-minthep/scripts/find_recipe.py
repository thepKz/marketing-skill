#!/usr/bin/env python3
"""Look up the data tables by the words a non-marketer would actually use, and compose the result.

Two things separate this from a grep over the same CSVs.

First, the search is job-first. Somebody who has never done marketing cannot answer "which
aesthetic do you want" — they can only answer "I need to put my dish on a delivery app". So every
row is keyed by the job, in Vietnamese and English, and the query is matched against the job and
the use-when column before anything else. A style-keyed table hands a noodle shop the word
"cyberpunk" and calls that a choice.

Second, `--brief` does not print a row. It writes a brief that `compile_prompt.py` will accept,
with the recipe's craft fields filled in and every field only the owner can know left as an
explicit TBD line. The recipe knows where the light goes; it cannot know what the shop sells. A
composer that guessed those fields would produce a runnable prompt full of invented product
truth, which is the exact failure this whole skill is built to prevent.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"

TABLES = {
    "recipes": ("image-recipes.csv", "id", ("job_vi", "job_en", "use_when", "fails_when")),
    "palettes": ("palettes.csv", "id", ("name_vi", "name_en", "signals", "use_for", "avoid_for")),
    "dials": ("layout-dials.csv", "dial", ("what_it_changes", "raise_it_when", "lower_it_when")),
    "slop": ("slop-tells.csv", "id", ("domain", "tell_vi", "tell_en", "look_where", "fix")),
    "copy": ("copy-formulas.csv", "id", ("name_vi", "name_en", "use_when", "structure")),
    # Searched by the question rather than the axis name, because nobody arrives knowing they
    # want the "copy_behavior" axis — they arrive holding a picture and asking whether the words
    # on it are theirs to take.
    "axes": ("reference-axes.csv", "axis", ("question_vi", "question_en", "name_vi", "name_en")),
}

# The fields of a brief that no lookup table can supply, with the reason each one has to come from
# the person who owns the product. These print as TBD lines rather than being quietly omitted,
# because a missing key in a JSON file is invisible and a TBD line is not.
OWNER_FIELDS = (
    ("project", "the product or shop name, as the owner writes it"),
    ("objective", "what this single image has to achieve, and where it will appear"),
    ("audience", "who is looking, and what they are deciding in that moment"),
    ("product_truth", "what the product actually is — the one field that must never be inferred"),
    ("mechanism", "why it works differently, if it does; delete this line if it does not"),
    ("promise", "the one thing the viewer should believe after looking"),
    ("single_idea", "the one idea the frame carries; if there are two, this is two images"),
)


def load(table: str) -> list[dict[str, str]]:
    filename, _, _ = TABLES[table]
    path = DATA / filename
    if not path.exists():
        raise SystemExit(f"missing data table: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def search(table: str, query: str) -> list[dict[str, str]]:
    """Rank rows by where the query hit, not just whether it hit.

    An id match beats a job match, and a job match beats a hit anywhere else in the row. Without
    the ranking, a query for "food" returns the nineteen rows that mention food in a warning and
    buries the four rows that are about photographing it.

    Every word has to hit, but not adjacently. "bún bò" used to return nothing while "bún" returned
    the right row, because the whole phrase was matched as one substring and no row spells out the
    dish. Someone who does not do this for a living types a phrase, not a keyword.
    """
    _, key, searched = TABLES[table]
    terms = [term for term in query.strip().lower().split() if term]
    if not terms:
        return load(table)

    def hits(text: str) -> bool:
        lowered = text.lower()
        return all(term in lowered for term in terms)

    def joined(row: dict[str, str], fields) -> str:
        # Joined rather than checked field by field, so a two-word query can land one word in
        # job_vi and the other in job_en and still count as a job match.
        return " ".join((row.get(field) or "") for field in fields)

    scored: list[tuple[int, dict[str, str]]] = []
    for row in load(table):
        if hits(row[key]):
            scored.append((0, row))
            continue
        if hits(joined(row, searched[:2])):
            scored.append((1, row))
            continue
        if hits(joined(row, searched)):
            scored.append((2, row))
            continue
        if hits(" ".join(value or "" for value in row.values())):
            scored.append((3, row))
    scored.sort(key=lambda pair: pair[0])
    return [row for _, row in scored]


def one(table: str, row_id: str) -> dict[str, str]:
    _, key, _ = TABLES[table]
    for row in load(table):
        if row[key] == row_id:
            return row
    known = ", ".join(row[key] for row in load(table))
    raise SystemExit(f"no {table} row called {row_id!r}. Known ids: {known}")


def table_lines(table: str, rows: list[dict[str, str]]) -> str:
    """One block per row, labelled, rather than a CSV dump nobody can read in a terminal."""
    if not rows:
        return "No row matched. Run with an empty query to list the table.\n"
    _, key, _ = TABLES[table]
    blocks = []
    for row in rows:
        lines = [f"## {row[key]}"]
        lines.extend(f"{field}: {value}" for field, value in row.items() if field != key and value)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def brief(recipe_id: str, palette_id: str | None) -> dict[str, object]:
    """Compose a `compile_prompt.py` brief from a recipe, leaving owner fields as TBD."""
    recipe = one("recipes", recipe_id)
    prompt: dict[str, str] = {
        "capture_mode": "environmental-editorial",
        "job": recipe["job_en"],
        "subject_action": recipe["subject_action"],
        "scene": recipe["scene"],
        "lighting": recipe["lighting"],
        "camera_geometry": recipe["camera"],
        "materials": recipe["materials"],
        "aspect_ratio": recipe["ratio"],
        "copy_safe_area": recipe["copy_safe"],
        "exact_text": "No generated text of any kind. Every word is set in layout afterwards.",
        "negative_constraints": recipe["avoid"],
    }
    if palette_id:
        palette = one("palettes", palette_id)
        # The palette constrains the set, not the subject. A prompt that hands the image model four
        # hex codes gets a frame graded into them, product colour included — and a graded product
        # colour is a false claim about the product. So the accent and the ink go to the layout
        # stage and only the ground is allowed into the prompt.
        prompt["background_treatment"] = (
            f"Ground and surroundings sit in the {palette['name_en']} range around {palette['bg']}; "
            f"the product keeps its own true colour and is not graded toward the palette"
        )
    payload: dict[str, object] = {
        "schema_version": 2,
        "project": "TBD",
        # "human", not "person": `compile_prompt.py` switches to the person wording for the capture
        # mode on this exact string, and an unrecognised value silently gives a founder portrait
        # the product description. That is how a portrait brief ends up asking for exact materials
        # and true colour instead of skin, hair and posture.
        "mode": "human" if recipe_id in PERSON_RECIPES else "product",
        "brief": {field: "TBD" for field, _ in OWNER_FIELDS if field != "project"},
        "prompt": prompt,
        "_tbd": {field: reason for field, reason in OWNER_FIELDS},
        "_recipe": {
            "id": recipe["id"],
            "fails_when": recipe["fails_when"],
            "use_when": recipe["use_when"],
        },
    }
    payload["brief"].pop("single_idea", None)  # type: ignore[union-attr]
    prompt["single_idea"] = "TBD"
    if palette_id:
        palette = one("palettes", palette_id)
        payload["_palette"] = {
            "id": palette["id"],
            "background": palette["bg"],
            "ink": palette["ink"],
            "accent": palette["accent"],
            "accent_label": palette["accent_label"],
            "accent_use": palette["accent_use"],
            "ink_on_background_contrast": palette["ratio_ink_on_bg"],
        }
    return payload


# Recipes whose subject is a person, so `compile_prompt.py` picks the person wording for the
# capture mode rather than describing skin and posture over a bottle.
PERSON_RECIPES = frozenset(
    {
        "apparel-on-model",
        "beauty-closeup",
        "customer-using",
        "fashion-editorial",
        "founder-portrait",
        "staff-at-work",
        "team-group",
        "testimonial-frame",
        "ugc-selfie",
    }
)


def checklist(recipe_id: str) -> str:
    """What to look at on the render, filtered to the tells that can actually occur here.

    Nobody checks a render against thirty-three generic tells; they check six, if the six are
    named. So `applies_to` in the table scopes each tell to the recipes it can occur in, and the
    rest are dropped. The first version of this ranked by keyword overlap and put "the after frame
    is better lit than the before frame" on a UGC selfie checklist, which teaches the reader to
    skim the list — the one failure mode a checklist cannot survive.
    """
    recipe = one("recipes", recipe_id)
    order = {"critical": 0, "high": 1, "medium": 2}
    picked = [
        row
        for row in load("slop")
        if row["domain"] in ("image", "prompt")
        and (row["applies_to"] == "any" or recipe_id in row["applies_to"].split())
    ]
    picked.sort(key=lambda row: order.get(row["severity"], 3))
    lines = [
        f"# Render check — {recipe['id']}",
        "",
        f"Job: {recipe['job_en']} / {recipe['job_vi']}",
        f"This recipe fails when: {recipe['fails_when']}",
        "",
        "Look at the render, in this order. Reading the prompt again proves nothing.",
        "",
    ]
    for index, row in enumerate(picked, start=1):
        lines.append(f"{index}. {row['tell_en']}")
        lines.append(f"   Look at: {row['look_where']}")
        lines.append(f"   Fix: {row['fix']}")
        lines.append("")
    lines.append(f"Then: {recipe['avoid']}")
    return "\n".join(lines) + "\n"


def main() -> None:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="Search the data tables by job, or compose a brief from a recipe."
    )
    parser.add_argument("--table", choices=sorted(TABLES), default="recipes")
    parser.add_argument("--query", default="", help="Vietnamese or English; matched against job first")
    parser.add_argument("--brief", metavar="RECIPE_ID", help="compose a compile_prompt.py brief")
    parser.add_argument("--palette", metavar="PALETTE_ID", help="constrain the ground of a --brief")
    parser.add_argument("--checklist", metavar="RECIPE_ID", help="what to look at on the render")
    parser.add_argument("--output")
    args = parser.parse_args()

    if args.brief and args.checklist:
        raise SystemExit("--brief and --checklist do different jobs; run one at a time")
    if args.brief:
        emit_json(brief(args.brief, args.palette), args.output)
        return
    if args.checklist:
        emit(checklist(args.checklist), args.output)
        return
    emit(table_lines(args.table, search(args.table, args.query)), args.output)


if __name__ == "__main__":
    main()
