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
    # Searched by the symptom, because somebody arrives saying the copy "sounds translated" or
    # "nghe như AI viết". They do not arrive knowing the word calque.
    "translation": ("translation-tells.csv", "id", ("tell_vi", "tell_en", "why_it_happens", "fix")),
    # Searched by the question rather than the axis name, because nobody arrives knowing they
    # want the "copy_behavior" axis — they arrive holding a picture and asking whether the words
    # on it are theirs to take.
    "axes": ("reference-axes.csv", "axis", ("question_vi", "question_en", "name_vi", "name_en")),
    # Searched by where the asset is going, because the question arrives as "cho Reels" or "in ra
    # giấy A4", never as "9:16" — and the answer has to carry which grid that ratio wants.
    "ratios": ("frame-ratios.csv", "ratio_id", ("label", "native_home", "communicates", "grid")),
    # Searched by the name someone half-remembers — tỉ lệ vàng, rule of thirds — because that is
    # the form the question takes, and the row's job is to say what the evidence actually supports.
    "grids": ("composition-grids.csv", "grid_id",
              ("name_vi", "name_en", "what_it_claims", "use_when")),
    # Searched by what the person wants to measure — "MER", "tỉ lệ nghỉ việc", "brand awareness" —
    # and the row that comes back carries the trap, because the expensive mistake with a KPI is
    # almost never picking the wrong one. It is scoring the right one the wrong way round.
    "kpis": ("kpi-metrics.csv", "kpi_id", ("name_vi", "name_en", "measurement", "use_when", "trap")),
    # Searched by the block, because the question is "phòng tôi thì chia bao nhiêu" and the answer is
    # a range with a reason rather than a number.
    "kpi_weights": ("kpi-aspect-weights.csv", "aspect",
                    ("block", "name_vi", "name_en", "rationale")),
    # Searched by what is visible rather than by style name, because the person holding the photo
    # does not know it is called mul-gwang. They know the skin looks wet. signature_tell and
    # discriminator are in the search set for the same reason: they carry the sentence that settles
    # which of two near-identical looks this actually is.
    "makeup": ("makeup-looks.csv", "look_id",
               ("name_vi", "name_en", "family", "signature_tell", "discriminator", "use_when")),
    # Searched by the question, because that is how it gets used: somebody wants to know what to
    # ask next, not which q_id to look up.
    "makeup_ask": ("makeup-diagnostics.csv", "q_id",
                   ("question_vi", "question_en", "look_where", "why_it_matters")),
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


PHI = 1.6180339887
PHI_SHORT = 1 / PHI  # 0.618..., so the short side of a phi split is 38.2%


def ratio_lines(w: int, h: int) -> dict[str, float]:
    """Where each grid system puts its lines on a w x h frame, as fractions of the side.

    This is the numeric core. `ratio_geometry` below turns it into sentences and
    `render_refsheet.sheet_ratios` turns it into drawn lines, so a frame's arithmetic exists once
    and the sheet cannot claim a different eye position than the table printed.
    """
    eye = h * h / (w * w + h * h)
    near = min(eye, 1 - eye)
    return {
        "decimal": w / h,
        "thirds": 1 / 3,
        "phi": 1 - PHI_SHORT,
        "eye": eye,
        "eye_near": near,
        # How far the two grids actually sit apart, in pixels of this canvas's width. The gap is the
        # whole argument: below about 5% nobody can point at it, above that it is a visible decision.
        "eye_gap_px": abs(near - 1 / 3) * w,
        "phi_gap_px": abs((1 - PHI_SHORT) - 1 / 3) * w,
    }


def ratio_geometry(row: dict[str, str]) -> dict[str, str]:
    """Compute where each grid actually lands on this frame, instead of storing it in the table.

    Only w and h are source data. Everything below follows from them, so the table cannot disagree
    with itself the way the spreadsheet this replaces did — there a ratio's decimal and its grid
    percentage were two typed cells, and one of them was stale.

    The dynamic-symmetry eye reduces to a single number. For width W and height H the reciprocal
    diagonal meets the full diagonal at x = W·H²/(W²+H²), which as a fraction of the width is
    H²/(W²+H²); the matching y as a fraction of the height is W²/(W²+H²). Those two sum to 1, so
    the four eyes land on the same pair of percentages on both axes, and one number describes the
    whole grid. That identity is why this is computed and not tabulated.

    The distance is measured to the *nearer* thirds line. Comparing the 76% eye against the 33%
    line instead of the 67% one is what made the first version report 460 px of disagreement on a
    9:16 frame, which is not a disagreement between grids — it is two different lines.
    """
    w, h = int(row["w"]), int(row["h"])
    g = ratio_lines(w, h)
    near, eye_px, thirds_px = g["eye_near"], g["eye_gap_px"], g["phi_gap_px"]
    return {
        "computed_decimal": f"{g['decimal']:.4f} ({w} x {h})",
        "computed_thirds": "33.3% and 66.7% of each side, at every ratio",
        "computed_phi": f"38.2% and 61.8% — {thirds_px:.0f} px from the thirds line on this canvas",
        "computed_eye": (
            f"{near * 100:.1f}% and {(1 - near) * 100:.1f}% of each side — "
            f"{eye_px:.0f} px from the nearer thirds line on this canvas"
        ),
        "computed_grid_matters": (
            "No. Every grid lands within 5% of the others here, so pick one and stop arguing"
            if eye_px < w * 0.05 and thirds_px < w * 0.05 else
            f"Yes. Thirds and dynamic symmetry disagree by {eye_px:.0f} px of {w}, which is "
            f"{eye_px / w * 100:.1f}% of the frame and visible"
        ),
    }


def table_lines(table: str, rows: list[dict[str, str]]) -> str:
    """One block per row, labelled, rather than a CSV dump nobody can read in a terminal."""
    if not rows:
        # The tells table is the one people query by symptom ("dịch từng chữ", "sounds translated"),
        # and the rows are written in the vocabulary of the fix rather than the complaint, so the
        # search misses. Point at the matcher, which finds them from the draft itself.
        if table == "translation":
            return ("No row matched. This table is matched against a draft, not searched by symptom: "
                    "run `python scripts/rewrite_human.py --check <file>` and it reports every tell "
                    f"that fired. Run with an empty query to list all {len(load(table))}.\n")
        return "No row matched. Run with an empty query to list the table.\n"
    _, key, _ = TABLES[table]
    blocks = []
    for row in rows:
        lines = [f"## {row[key]}"]
        lines.extend(f"{field}: {value}" for field, value in row.items() if field != key and value)
        if table == "ratios":
            lines.extend(f"{field}: {value}" for field, value in ratio_geometry(row).items())
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
