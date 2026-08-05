#!/usr/bin/env python3
"""Measure a draft against the human-cadence targets, and name the translation tells in it.

Why a script and not a checklist: the failures this catches are statistical, and a reader — including
the model that wrote the draft — cannot see a statistic by rereading. Uniform sentence length is the
strongest human-detectable machine signal in prose, and it is invisible sentence by sentence. Every
sentence can be good while the paragraph reads flat.

The second half is about translation. A Vietnamese draft rendered word for word from an English one
stays grammatical and reads wrong, and the reverse is worse: `uy tín, chuyên nghiệp` becomes
`prestigious, professional`, which is grammatical English that says nothing. Those failures live in
`data/translation-tells.csv` with a regex each, because a named pattern is repairable and a vague
note that the copy "sounds translated" is not.

    python scripts/rewrite_human.py --check draft.md --lang vi
    python scripts/rewrite_human.py --check draft.md --lang auto --json
    python scripts/rewrite_human.py --targets            # print the targets, no file needed
    python scripts/rewrite_human.py --self-check         # verify the measurements on known inputs

Exit code is 1 when any `critical` or `high` gate fails, so a run can be gated on it.
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TELLS = ROOT / "data" / "translation-tells.csv"
MARKERS = ROOT / "data" / "spoken-markers.csv"

# Everything above this line in this file is subtractive, and so is every table it reads. Delete
# `Hơn nữa`, delete the em dash, delete the icon, break the flat run. That is a complete description
# of what the unit could do until 2026-08-05, and it has a hole in the middle of it: a draft can pass
# every gate here, match no tell in either table, and still be clean flat translationese, because
# nothing in the skill had ever asked what a Vietnamese sentence *has* when a Vietnamese person wrote
# it. The failure was found by a reader on this repository's own copy, in three words - `word by
# word` - after the subtractive gates had all gone green.
#
# `data/spoken-markers.csv` is the positive side, Vietnamese first: final particles, topic-comment
# fronting with `thì`, classifier plus demonstrative, direction verbs glued to the main verb, `bị`
# with the affected party as subject. Each row carries what it makes the sentence carry and what
# arrives in its place when the sentence was translated instead of written.
#
# Two limits, both load-bearing, both stated in references/rewrite-human.md at more length.
# There is no human-written conversational Vietnamese corpus in this repository, so these markers
# are graded as descriptions of the grammar and are NOT frequency-calibrated. And formal human
# Vietnamese - the ND87 text in `data/vn-advertising-law.csv` is the case to hand - scores near zero
# on this table while being entirely human, which is why the floor below is per-channel and absent
# rather than passing on the channels where a particle would be wrong.
#
# The floor is a count of distinct markers and not a rate per 150 units, and it is worth saying why,
# because the first version of this gate was a rate and the rate was backwards. Measured on
# 2026-08-05, distinct markers per 150 syllables:
#
#   ND87 legal Vietnamese      0.00   formal, human, written by a ministry
#   references/rewrite-human   0.00   this unit's own English-language reference prose
#   README.vi.md               0.15   hand-written Vietnamese, 5986 syllables
#   docs/index.html            0.17   hand-written Vietnamese, 2635 syllables
#   a flat translationese ad   0.97   the thing this gate exists to catch, 154 syllables
#
# The rate ranked the translationese six times above the hand-written page, because the numerator is
# capped - there are eleven matchable Vietnamese rows and a document cannot exceed them - while the
# denominator grows without limit. Any per-length normalisation of a bounded count does this. So the
# measurement is a count over the whole document, which separates the same five samples cleanly:
# 0, 0, 6, 3 against 1 for the translationese and 1 for the sprinkled cheat below.
#
# Two distinct markers, and one on anything short enough that two would be unreasonable. The margin
# is thin and stating it is part of the calibration: the landing page clears the floor with three.
SPOKEN_DISTINCT_MIN = 2
SPOKEN_DISTINCT_MIN_SHORT = 1
SPOKEN_SHORT_UNITS = 60
# The anti-gaming half, and the reason it exists is that the floor above is cheatable: put `nhé` on
# the end of five sentences and one marker carries the whole document. Past this share of the hits,
# one marker is being sprinkled rather than a person speaking.
SPOKEN_TOP_SHARE_MAX = 0.5
SPOKEN_VARIETY_MIN_HITS = 4
# Channels where a reader is being spoken to, and so where the absence of every spoken marker is a
# finding. On `deliverable`, `pr` and `sales-deck` the measurement still prints - a writer should see
# a zero - but no gate is emitted, because a spec and a press release are formal on purpose and a
# gate that fails them is a gate that gets switched off in week one.
SPOKEN_CHANNELS = {"social", "chat", "email", "web", "marketplace"}

# From references/dossiers/copywriting-deep.md section 6.2. Craft calibration targets, not measured
# findings: they exist because machine prose defaults to uniform length, and uniformity is the tell.
# Vietnamese is measured in syllables because a Vietnamese "word" is written as separate syllables,
# so a word count says nothing comparable.
TARGETS = {
    # `beat`: at or under this a sentence is a landing beat. It is per-language for the same
    # reason the mean band is: a Vietnamese syllable carries less than an English word, so
    # "Ngày rang in trên đáy túi" is six units and every bit as short as a four-word English line.
    "en": {"mean_low": 12, "mean_high": 18, "unit": "words", "beat": 4},
    "vi": {"mean_low": 14, "mean_high": 22, "unit": "syllables", "beat": 6},
}
RATIO_MIN = 3.0          # longest / shortest sentence
CV_MIN = 0.45            # stdev / mean — the direct burstiness measure
SHORT_PER_150 = 1.0      # landing beats per 150 units
SHORT_SENTENCE = 8       # above this, a run of similar lengths is machine flatness not staccato
FLAT_RUN_MAX = 2         # consecutive sentences within +/-2 units of each other
SAME_OPENER_MAX = 2      # consecutive sentences starting on the same word
EM_DASH_PER_150 = 1.0
PARA_SENTENCES_MAX = 4
# Below this, the piece is short-form copy and a short mean is the point, not a defect.
SHORT_FORM_UNITS = 120

# Pictographs that carry meaning rather than decoration, and so are never counted. Every one of
# these is Unicode general category `So`, the same category the rocket and the tick sit in, which is
# why an allow-list is unavoidable: a gate that flags the registered-trademark sign in brand copy is
# a gate that gets switched off in week one.
DECORATION_KEEP = set("©®™°№℃℉")
# House figures, and there is no standard to defer to here. What is defensible is the *shape* of the
# rule rather than the numbers: the defect is not that a pictograph is present, it is that it arrived
# in a slot nobody chose. An emoji a writer put inside a sentence is a decision. An emoji opening
# every bullet is a template, and on a deliverable it is the single most recognisable sign that
# nobody edited the output.
DECORATION_BUDGET = {
    # Surfaces where a reader does not expect a pictograph at all, this skill's own artifacts among
    # them. Zero, because on these surfaces there is no native use to protect.
    "deliverable": {"structural": 0, "per_150": 0.0},
    "web": {"structural": 0, "per_150": 0.0},
    "email": {"structural": 0, "per_150": 0.0},
    "pr": {"structural": 0, "per_150": 0.0},
    "sales-deck": {"structural": 0, "per_150": 0.0},
    "marketplace": {"structural": 0, "per_150": 0.0},
    # Social and chat are different in kind, not in degree. A Vietnamese seller bulleting a Facebook
    # post with a tick is doing what the surface does, and a gate that calls that a machine tell is
    # simply wrong about the channel. So structure is unbounded here and only density is held.
    "social": {"structural": None, "per_150": 3.0},
    "chat": {"structural": None, "per_150": 3.0},
}
DEFAULT_CHANNEL = "deliverable"
# The one decoration rule that holds on every channel. Three lines opening on the same pictograph is
# a generated list whatever the surface, because a writer choosing an icon per line would vary it.
DECORATION_RUN_MAX = 2

# Measured, not chosen. Across this skill's own reference files - the only corpus to hand where every
# document was written by a person and reviewed - the share of lists holding exactly three items was
# 0.43 or lower in every file but one. The exception scored 0.80, and reading it confirmed the number
# rather than excusing it: eight of ten sections carried the identical
# `Core proofs / Useful scenes / Reject` triple, and the file turned out to duplicate
# `product-category-playbooks.md`, which covered the same nine categories and three more. It was
# folded into that file rather than reshaped, so the 0.80 is now only in this comment and in git.
# The line sits in the middle of a gap from 0.43 to 0.80 rather than at the edge of a narrow one,
# which is the only kind of threshold worth shipping.
TRICOLON_SHARE_MAX = 0.60
# Below four lists the share is noise rather than a signal: a file with two lists, both of three,
# scores 1.00 and has done nothing wrong. Under this floor the gate is absent from the report
# entirely rather than reported as passing, because "passed" would be a claim it cannot support.
LIST_BLOCKS_MIN = 4

SENTENCE_END = re.compile(r"(?<=[.!?…])[\s]+|\n{2,}")
# Markdown furniture is not prose and would wreck every length measurement if counted as sentences.
STRIP_LINES = re.compile(r"^\s*(#{1,6}\s|\||[-*+]\s|\d+\.\s|>|```)")
# Everything a line can carry before its first real character: quote markers, bullets, numbers,
# heading hashes, table pipes, in any order and repeated. What follows is the first thing a reader
# sees on that line, and a pictograph there is being used as structure.
LINE_LEAD = re.compile(r"^(?:\s|[-*+>]\s*|\d+[.)]\s*|#{1,6}\s*|\|\s*)*")
# A list item and its indent. Both bullet and ordered forms, because "1. 2. 3." is the same shape.
LIST_ITEM = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(\S.*)$")
# An inline code span. Non-greedy, and a span may cross a hard line break but not a blank line: every
# reference in this skill is wrapped at about a hundred columns, so `Giao hàng nhanh\nchóng, tận tâm`
# is one span in two lines and a single-line pattern would miss it and read the tail as prose. Stopping
# at a blank line is what keeps an unpaired backtick from swallowing the rest of the section.
CODE_SPAN = re.compile(r"`{1,2}(?:[^`\n]|\n(?!\s*\n))+?`{1,2}")
# Stands in for a removed fenced block where a blank line would be read as continuation. It has to be
# non-blank and not match LIST_ITEM; the text itself is never measured, only its shape.
FENCE_STOP = "fenced block removed"


def read_tells(language: str) -> list[dict[str, str]]:
    if not TELLS.exists():
        raise SystemExit(f"missing data table: {TELLS}")
    with TELLS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if row["language"] in (language, "any")]


def read_markers(language: str) -> list[dict[str, str]]:
    if not MARKERS.exists():
        raise SystemExit(f"missing data table: {MARKERS}")
    with MARKERS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if row["language"] == language]


def spoken_markers(text: str, language: str) -> dict:
    """Which positive markers of somebody speaking this language are present, and how varied.

    Same reading rules as `find_tells`: prose only, code spans stripped. A marker named inside
    backticks in a table of markers is not a marker being used, and this file's own reference is
    full of them.

    `manual` rows are counted separately and never reported as measured. Three of them exist because
    the shape genuinely has no regex - a serial verb chain, a benefactive `cho`, a concrete measure
    standing where a degree adjective would go - and a table that pretended otherwise would claim a
    check it never made. Same convention as the manual row in `data/title-devices.csv`.
    """
    body = unquoted(prose_only(text))
    rows = read_markers(language)
    hits: list[dict] = []
    for row in rows:
        if row["detect"] != "regex":
            continue
        try:
            pattern = re.compile(row["detect_regex"], re.MULTILINE)
        except re.error as error:  # a broken row must be visible, not silently absent
            hits.append({"id": row["id"], "count": 0, "error": f"bad regex: {error}"})
            continue
        found = [match.group(0).strip() for match in pattern.finditer(body)]
        if found:
            hits.append({"id": row["id"], "layer": row["layer"], "count": len(found),
                         "samples": found[:3], "carries": row["what_it_carries"]})
    total = sum(hit["count"] for hit in hits if "error" not in hit)
    top = max((hit["count"] for hit in hits if "error" not in hit), default=0)
    return {
        "hits": sorted(hits, key=lambda hit: -hit["count"]),
        "distinct": len([hit for hit in hits if "error" not in hit]),
        "total": total,
        "top_share": round(top / total, 2) if total else 0.0,
        "top_id": next((hit["id"] for hit in hits if hit.get("count") == top and top), ""),
        "measurable_rows": sum(1 for row in rows if row["detect"] == "regex"),
        "manual_rows": [row["id"] for row in rows if row["detect"] != "regex"],
    }


def spoken_gates(stats: dict, channel: str) -> list[dict]:
    """The positive gates, and the only ones in this file that fail a draft for what it lacks.

    Absent rather than passing on a formal channel, and that scoping was measured rather than
    assumed. The ND87 advertising-law text in `data/vn-advertising-law.csv` is human Vietnamese
    written by a ministry and scores exactly zero distinct markers across 2925 syllables. A universal
    floor would call the one unambiguously institutional Vietnamese in this repository
    machine-written, so the floor stops at the channels where somebody is being spoken to.
    """
    found = stats.get("spoken") or {}
    if channel not in SPOKEN_CHANNELS or not found:
        return []
    total_units = stats.get("total_units", 0)
    short = total_units < SPOKEN_SHORT_UNITS
    floor = SPOKEN_DISTINCT_MIN_SHORT if short else SPOKEN_DISTINCT_MIN
    shown = ", ".join(f"{hit['id']}x{hit['count']}" for hit in found["hits"][:4]) or "none"
    rows = [{
        "gate": "spoken-register-present",
        "pass": found["distinct"] >= floor,
        "severity": "high",
        "observed": f"{found['distinct']} distinct of {found['measurable_rows']} matchable "
                    f"({found['total']} hits: {shown})",
        "target": f">= {floor} distinct"
                  + (f", relaxed under {SPOKEN_SHORT_UNITS} units" if short else ""),
        "why": "Every other gate in this file measures what to delete, so a draft can pass all of "
               "them and still be flat translationese. This one asks what the sentence has: a final "
               "particle, a topic fronted before its comment, a classifier pointing at one real "
               "thing. A count and not a rate, because a rate ranked a flat translated ad above this "
               "repository's hand-written Vietnamese - see the table above the constant. "
               "`data/spoken-markers.csv` carries the rows and the repair each one implies.",
    }]
    if found["total"] >= SPOKEN_VARIETY_MIN_HITS:
        rows.append({
            "gate": "spoken-register-variety",
            "pass": found["top_share"] <= SPOKEN_TOP_SHARE_MAX,
            "severity": "medium",
            "observed": f"{found['top_share']} of {found['total']} hits are {found['top_id']}",
            "target": f"<= {SPOKEN_TOP_SHARE_MAX}, once there are {SPOKEN_VARIETY_MIN_HITS} hits",
            "why": "The gate above is cheatable by putting `nhé` on the end of five sentences, and "
                   "this is what catches the draft that then adds a second marker to clear the "
                   "count. One marker carrying most of the hits is a texture pass applied on top of "
                   "flat prose, not a person talking. references/rewrite-human.md says not to "
                   "rewrite by adding texture; this is that instruction made measurable.",
        })
    return rows


def outside_fences(text: str, fill: str = "") -> str:
    """Everything except fenced code blocks, with fenced lines replaced by `fill` rather than deleted
    so that run-length measurements still see the gap where the block was.

    `fill` is blank for prose and decoration, where an absent line is what a fence should look like.
    Pass `FENCE_STOP` when a blank line would *join* two things the fence separates: a loose Markdown
    list survives a blank line, so blanking a code block between two lists would report one list of
    six where the document has two of three.

    Decoration and list shape are read from the raw file on purpose, because a heading or a bullet is
    exactly where decoration lives. A fenced block is the one place where neither reading holds: a
    box-drawing character or a `- ` line inside a fence is verbatim content somebody typed on
    purpose. Counting a hand-drawn ASCII decision tree as six pictographs used as structure is how a
    gate earns the right to be ignored, and a gate that is ignored is not a gate.
    """
    kept: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            kept.append(fill)
            continue
        kept.append(fill if fenced else line)
    return "\n".join(kept)


def prose_only(text: str) -> str:
    """Drop headings, tables, list markers and fences. What remains is what a reader reads as prose."""
    return "\n".join("" if STRIP_LINES.match(line) else line
                     for line in outside_fences(text).splitlines())


def unquoted(text: str) -> str:
    """Prose with inline code spans removed, for matching word tells only.

    A backticked word is being *named*, not used. `copywriting.md` says to delete `seamless`, and
    the tell for `seamless` matched it - so the file that bans the word failed for banning it, and
    the same trap caught every replacement table and every glossary in the skill. This is the
    difference between a document making a claim and a document quoting one.

    Not applied to cadence, on purpose. A code span is still a thing a reader's eye lands on and
    still occupies a slot in a sentence, so removing it before measuring sentence length would
    report a rhythm nobody reads. Only the word tells care whether a word is being asserted.

    A single space, not nothing: `the ``premium`` band` has to stay two words, or removing the span
    would fuse its neighbours into a token that was never written.
    """
    return CODE_SPAN.sub(" ", text)


def detect_language(text: str) -> str:
    """Vietnamese diacritics are decisive: no English draft carries combining tone marks."""
    decomposed = unicodedata.normalize("NFD", text)
    marks = sum(1 for char in decomposed if unicodedata.combining(char))
    letters = sum(1 for char in decomposed if char.isalpha())
    return "vi" if letters and marks / letters > 0.02 else "en"


def units(sentence: str, language: str) -> int:
    """Words for English, syllables for Vietnamese — which is whitespace-separated tokens either way,
    because Vietnamese orthography already writes each syllable as its own token."""
    return len(re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", sentence, flags=re.UNICODE))


def sentences(text: str) -> list[str]:
    parts = [part.strip() for part in SENTENCE_END.split(text)]
    return [part for part in parts if len(part) > 1]


def paragraphs(text: str) -> list[list[str]]:
    return [sentences(block) for block in re.split(r"\n{2,}", text) if block.strip()]


def pictographs(string: str) -> list[str]:
    """Decorative pictographs in a string, by Unicode general category.

    `So` is the honest stdlib net. It catches every emoji that is a single code point, the regional
    indicators, and the geometric shapes that get used as bullets - the rocket, the tick, the bulb,
    the black square. It is *not* UTS #51 `Extended_Pictographic`, which is the property an emoji
    library would use, and Python's `unicodedata` does not expose that property at all. Two
    consequences worth stating rather than discovering: keycap sequences like the digit-plus-U+20E3
    form slip through, because the combining enclosing keycap is category `Me` and the digit is
    `Nd`; and skin-tone modifiers are `Sk`, so they are not counted separately from the base glyph
    they modify, which is correct here but for the wrong reason.

    Arrows and bullets are deliberately out of scope. `→` is `Sm` and `•` is `Po`, and both are
    ordinary typography with centuries behind them. Counting them would flag correctly typeset copy,
    and this file's whole discipline is that a gate which fires on good work stops being read.
    """
    return [char for char in string
            if unicodedata.category(char) == "So" and char not in DECORATION_KEEP]


def decorations(text: str) -> dict:
    """Count pictographs, and separate the ones standing in for structure from the ones inside prose.

    Read against the raw text on purpose. `prose_only()` strips headings, bullets and table rows,
    which is exactly where decoration lives - measuring decoration on the prose body would report
    zero on the worst possible draft. Fenced blocks are the one exception, because a box-drawing
    character inside a fence is a diagram somebody drew, not a bullet somebody defaulted to.
    """
    structural: list[str] = []
    inline: list[str] = []
    openers: list[str] = []
    for line in outside_fences(text).splitlines():
        icons = pictographs(line)
        if not icons:
            openers.append("")
            continue
        rest = line[LINE_LEAD.match(line).end():]
        lead = pictographs(rest[:1])
        heading = bool(re.match(r"^\s*#{1,6}\s", line))
        # A pictograph in a heading is structure wherever it sits in the line: the heading *is* the
        # structure. Elsewhere only the first character of the line counts, so an emoji a writer put
        # in the middle of a sentence stays inline.
        if heading:
            structural.extend(icons)
        elif lead:
            structural.extend(lead)
            inline.extend(icons[1:])
        else:
            inline.extend(icons)
        openers.append(lead[0] if lead else (icons[0] if heading else ""))

    run = worst_run = 0
    for previous, current in zip([""] + openers, openers):
        run = run + 1 if current and current == previous else (1 if current else 0)
        worst_run = max(worst_run, run)
    return {"structural": len(structural), "inline": len(inline),
            "total": len(structural) + len(inline),
            "longest_icon_opener_run": worst_run,
            "samples": sorted(set(structural + inline))[:8]}


def list_blocks(text: str) -> list[list[str]]:
    """Contiguous runs of list items at one indent level, from the raw text.

    Raw for the same reason decoration is read raw: `prose_only()` blanks every list line, so the
    shape of a list is invisible to every other measurement in this file. That is not a small gap.
    A document built entirely of bullets reaches the `insufficient` branch with no cadence to
    measure, and a document built mostly of bullets - which is most briefs, playbooks and
    checklists - has its worst structural habit stripped out before anything looks at it.

    A block ends at a heading, a paragraph of prose, or a change of indent. Nesting starts a new
    block on purpose: three sub-points under each of three points is a different shape from one
    list of nine, and averaging them together would hide both. Blank lines inside a run do not end
    it, because a loose list in Markdown is still one list.

    Single-item "lists" are dropped. One bullet has no geometry, and counting it as a list of one
    would drag every share in this function toward whatever the writer used for a lone aside.

    Fenced blocks are out. A `- ` line inside a fence is a sample of somebody's YAML.
    """
    found: list[list[str]] = []
    open_runs: dict[int, list[str]] = {}

    def close(deeper_than: int = -1) -> None:
        for level in sorted((lvl for lvl in open_runs if lvl > deeper_than), reverse=True):
            found.append(open_runs.pop(level))

    for line in outside_fences(text, fill=FENCE_STOP).splitlines():
        match = LIST_ITEM.match(line)
        if match:
            indent = len(match.group(1))
            # Returning to a shallower indent ends every nested list under it, and leaves the
            # shallower run open. That is what lets `- Alpha / (three sub-points) / - Beta / - Gamma`
            # read as two lists of three rather than one list of four with three items lost.
            close(indent)
            open_runs.setdefault(indent, []).append(match.group(2).strip())
            continue
        if not line.strip() and open_runs:
            continue
        close()
    close()
    return [block for block in found if len(block) > 1]


def list_geometry(text: str) -> dict:
    """How many lists, how long each, and how many landed on three.

    Only the count is reported. Uniformity *within* a list was measured and deliberately left out -
    see the note in `references/rewrite-human.md`, because the negative result is the part worth
    keeping: even item lengths and a shared opening word are what a glossary, a rejection-code
    table and a deliberate anaphora all look like, and gating on them fires on good writing.
    """
    blocks = list_blocks(text)
    sizes = [len(block) for block in blocks]
    threes = sum(1 for size in sizes if size == 3)
    return {"blocks": len(blocks), "sizes": sizes, "threes": threes,
            "three_share": round(threes / len(sizes), 2) if sizes else 0.0,
            "longest": max(sizes, default=0)}


def measure(text: str, language: str) -> dict:
    body = prose_only(text)
    sents = sentences(body)
    decoration = decorations(text)
    if len(sents) < 2:
        # Cadence needs two sentences. Decoration does not, and a bullet list with a tick on every
        # line is both the commonest form of this defect and a draft with no measurable cadence at
        # all. Returning early without the decoration counts would leave that draft unchecked.
        return {"language": language, "sentences": len(sents), "insufficient": True,
                "total_units": units(body, language), "decoration": decoration,
                "lists": list_geometry(text), "spoken": spoken_markers(text, language)}

    beat = TARGETS[language]["beat"]
    lengths = [units(sentence, language) for sentence in sents]
    lengths = [length for length in lengths if length]
    total = sum(lengths)
    mean = statistics.mean(lengths)
    stdev = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0

    # A run of *short* sentences is a staccato device somebody chose - "Sixty-one restaurants run
    # it. Two have called support. No setup fee." Machine flatness is a run of similar *medium*
    # sentences, which is what nobody writes deliberately. Counting both flagged clean punchy copy,
    # so runs are only counted once past the short-sentence threshold.
    flat_run = worst_flat = 1
    for previous, current in zip(lengths, lengths[1:]):
        near = abs(current - previous) <= 2 and max(current, previous) > SHORT_SENTENCE
        flat_run = flat_run + 1 if near else 1
        worst_flat = max(worst_flat, flat_run)

    openers = [re.sub(r"[^\w]", "", sentence.split()[0].lower()) if sentence.split() else "" for sentence in sents]
    opener_run = worst_opener = 1
    for previous, current in zip(openers, openers[1:]):
        opener_run = opener_run + 1 if previous and current == previous else 1
        worst_opener = max(worst_opener, opener_run)

    per150 = (total / 150) or 1
    return {
        "language": language,
        "insufficient": False,
        "sentences": len(sents),
        "total_units": total,
        "unit": TARGETS[language]["unit"],
        "mean": round(mean, 1),
        "stdev": round(stdev, 1),
        "cv": round(stdev / mean, 2) if mean else 0.0,
        "longest": max(lengths),
        "shortest": min(lengths),
        "ratio": round(max(lengths) / min(lengths), 1) if min(lengths) else 0.0,
        "beat_units": beat,
        "short_sentences": sum(1 for length in lengths if length <= beat),
        "short_per_150": round(sum(1 for length in lengths if length <= beat) / per150, 2),
        "longest_flat_run": worst_flat,
        "longest_same_opener_run": worst_opener,
        "em_dashes": body.count("—"),
        "em_dash_per_150": round(body.count("—") / per150, 2),
        "longest_paragraph_sentences": max((len(block) for block in paragraphs(body)), default=0),
        "single_sentence_paragraphs": sum(1 for block in paragraphs(body) if len(block) == 1),
        "decoration": decoration,
        "lists": list_geometry(text),
        "spoken": spoken_markers(text, language),
    }


def decoration_gates(stats: dict, channel: str) -> list[dict]:
    """The icon gates, which run whether or not there is measurable cadence."""
    found = stats.get("decoration") or decorations("")
    budget = DECORATION_BUDGET[channel]
    per150 = (stats.get("total_units", 0) / 150) or 1
    density = round(found["total"] / per150, 2)
    shown = " ".join(found["samples"]) or "none"
    checks = [
        ("decoration-as-structure",
         budget["structural"] is None or found["structural"] <= budget["structural"], "high",
         f"{found['structural']} in a heading or opening a line ({shown})",
         "unbounded on this channel" if budget["structural"] is None
         else f"<= {budget['structural']}",
         "A pictograph opening a bullet or sitting in a heading is doing a typographic job, and "
         f"nobody chose it. On {channel} the reader is not expecting one, so it reads as an "
         "unedited default rather than as emphasis."),
        ("decoration-density", density <= budget["per_150"], "medium",
         f"{density} per 150 ({found['total']} total: {found['structural']} structural, "
         f"{found['inline']} inline)", f"<= {budget['per_150']} per 150",
         "An emoji a writer put inside a sentence is a decision. Past this rate they are furniture, "
         "and the reader stops reading them as anything."),
        ("decoration-run", found["longest_icon_opener_run"] <= DECORATION_RUN_MAX, "high",
         f"run of {found['longest_icon_opener_run']} lines", f"<= {DECORATION_RUN_MAX}",
         "The same pictograph opening three lines in a row is a generated list on every channel, "
         "including the ones where emoji are native. A writer picking an icon per line would have "
         "picked different ones."),
    ]
    return [{"gate": name, "pass": bool(passed), "severity": severity,
             "observed": observed, "target": want, "why": why}
            for name, passed, severity, observed, want, why in checks]


def structure_gates(stats: dict) -> list[dict]:
    """Shape above the sentence. Runs whether or not there is measurable cadence, because a document
    made of bullets has no cadence and is the likeliest place for this defect to live.

    One gate, and the restraint is the design. `data/slop-tells.csv` has carried
    `tricolon-everywhere` since the table was written, with `look_where` reading "count list lengths
    across the whole document" - an instruction to measure, shipped as advice. Meanwhile
    `data/translation-tells.csv` carries `tricolon-default`, whose `tell_en` is the same sentence
    word for word, but whose regex is `scope: prose` and matches three comma-separated phrases
    inside one sentence. Those are different defects. The regex fires on "physics, claim, or rights
    failure" in `anti-ai-quality.md`, which is a correct English triple, and cannot fire on eight
    identical three-item lists, because list lines are stripped before it looks. This gate is the
    half that was named but never built.
    """
    found = stats.get("lists") or list_geometry("")
    if found["blocks"] < LIST_BLOCKS_MIN:
        return []
    return [{
        "gate": "tricolon-everywhere",
        "pass": found["three_share"] <= TRICOLON_SHARE_MAX,
        "severity": "high",
        "observed": f"{found['threes']} of {found['blocks']} lists hold exactly three items "
                    f"({found['three_share']}); sizes {found['sizes']}",
        "target": f"<= {TRICOLON_SHARE_MAX} of lists, over {LIST_BLOCKS_MIN}+ lists",
        "why": "Three is the most rhetorically satisfying count, which is exactly how it stops being "
               "a count and becomes a template. One list of three is three things. Most of the lists "
               "in a document being three is a form somebody filled in, and it survives every other "
               "gate here because list lines are stripped before the prose is measured.",
    }]


def gates(stats: dict, channel: str = DEFAULT_CHANNEL) -> list[dict]:
    if stats.get("insufficient"):
        return (structure_gates(stats) + decoration_gates(stats, channel)
                + spoken_gates(stats, channel))
    target = TARGETS[stats["language"]]
    unit = target["unit"]
    checks = [
        # Asymmetric on purpose. Long is a real defect: above the band, mobile comprehension drops.
        # Short is a defect only in body prose. Ad copy, headlines and captions are meant to be
        # clipped, and the first clean Vietnamese draft this script was pointed at failed the
        # symmetric version of this gate at a mean of 9.5 while passing every other gate. A gate
        # that fails good short-form copy is a gate people learn to ignore.
        ("mean-length-high", stats["mean"] <= target["mean_high"], "high",
         f"mean {stats['mean']} {unit}", f"<= {target['mean_high']}",
         "Above the band, mobile comprehension drops."),
        ("mean-length-low", stats["mean"] >= target["mean_low"] or stats["total_units"] < SHORT_FORM_UNITS,
         "medium", f"mean {stats['mean']} {unit}",
         f">= {target['mean_low']}, or under {SHORT_FORM_UNITS} {unit} total",
         "Body prose this short reads clipped. In short-form copy it is correct, so this only applies above "
         f"{SHORT_FORM_UNITS} {unit}."),
        ("burstiness-cv", stats["cv"] >= CV_MIN, "critical",
         f"CV {stats['cv']}", f">= {CV_MIN}",
         "The direct uniformity measure. Below it the prose reads machine-flat however good each sentence is."),
        ("long-short-ratio", stats["ratio"] >= RATIO_MIN, "high",
         f"ratio {stats['ratio']}", f">= {RATIO_MIN}",
         "Needs one sentence at least three times the shortest. Deliberate contrast, not accident."),
        ("landing-beats", stats["short_per_150"] >= SHORT_PER_150, "high",
         f"{stats['short_per_150']} per 150", f">= {SHORT_PER_150}",
         f"A sentence of {stats['beat_units']} {stats['unit']} or fewer is where a claim lands. "
         "Without one per 150 units nothing lands."),
        ("flat-run", stats["longest_flat_run"] <= FLAT_RUN_MAX, "high",
         f"run of {stats['longest_flat_run']}", f"<= {FLAT_RUN_MAX}",
         "Three sentences of near-identical length in a row is audible as a pattern."),
        ("opener-repetition", stats["longest_same_opener_run"] <= SAME_OPENER_MAX, "medium",
         f"run of {stats['longest_same_opener_run']}", f"<= {SAME_OPENER_MAX}",
         "Anaphora is a device you choose once, not a default."),
        ("em-dash-density", stats["em_dash_per_150"] <= EM_DASH_PER_150, "medium",
         f"{stats['em_dash_per_150']} per 150", f"<= {EM_DASH_PER_150}",
         "The em dash is a strong rhythmic default and nothing pushes back on repeating it."),
        ("paragraph-length", stats["longest_paragraph_sentences"] <= PARA_SENTENCES_MAX, "medium",
         f"longest {stats['longest_paragraph_sentences']} sentences", f"<= {PARA_SENTENCES_MAX}",
         "Whitespace carries emphasis on mobile."),
    ]
    if stats["language"] == "vi":
        checks.append(("em-dash-vietnamese", stats["em_dashes"] == 0, "medium",
                       f"{stats['em_dashes']} em dashes", "0",
                       "Vietnamese punctuates this with a comma, a colon or a full stop. The em dash arrives with the English draft."))
    rows = [{"gate": name, "pass": bool(passed), "severity": severity,
             "observed": observed, "target": want, "why": why}
            for name, passed, severity, observed, want, why in checks]
    return (rows + structure_gates(stats) + decoration_gates(stats, channel)
            + spoken_gates(stats, channel))


def find_tells(text: str, language: str) -> list[dict]:
    body = unquoted(prose_only(text))
    found: list[dict] = []
    for row in read_tells(language):
        try:
            pattern = re.compile(row["detect_regex"], re.MULTILINE)
        except re.error as error:  # a broken row must be visible, not silently skipped
            found.append({"id": row["id"], "count": 0, "error": f"bad regex: {error}"})
            continue
        # Heading tells have to read the raw file: prose_only() strips the headings they look for.
        # Still unquoted, because a word named in a heading is no more asserted than one in a
        # sentence - a section called `## Deleting "seamless"` is not using the word.
        subject = unquoted(text) if row.get("scope") == "raw" else body
        # group(0), not findall(): a pattern with groups returns the groups, and a report that
        # says the tell was "này" instead of "điều này có nghĩa là" is not a report.
        matches = [match.group(0) for match in pattern.finditer(subject)]
        if matches:
            samples = matches[:3]
            found.append({
                "id": row["id"], "layer": row["layer"], "severity": row["severity"],
                "count": len(matches), "samples": samples,
                "tell": row["tell_vi"] if language == "vi" else row["tell_en"],
                "fix": row["fix"],
            })
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return sorted(found, key=lambda row: (order.get(row.get("severity", "low"), 9), -row["count"]))


def _gate_table(gate_rows: list[dict]) -> list[str]:
    lines = ["| Gate | Result | Observed | Target | Why |", "|---|---|---|---|---|"]
    for row in gate_rows:
        mark = "pass" if row["pass"] else f"FAIL ({row['severity']})"
        lines.append(f"| {row['gate']} | {mark} | {row['observed']} | {row['target']} | {row['why']} |")
    return lines


def _tell_section(tells: list[dict]) -> list[str]:
    lines = ["", "## Translation and slop tells", ""]
    if not tells:
        lines.append("None of the tells in `data/translation-tells.csv` matched.")
        return lines
    lines += ["| Tell | Severity | Hits | Found | Fix |", "|---|---|---|---|---|"]
    for row in tells:
        if "error" in row:
            lines.append(f"| {row['id']} | table error | - | {row['error']} | fix the CSV |")
            continue
        samples = "; ".join(sample.strip()[:40] for sample in row["samples"])
        lines.append(f"| {row['id']} | {row['severity']} | {row['count']} | {samples} | {row['fix']} |")
    return lines


def _spoken_section(stats: dict, channel: str) -> list[str]:
    """Prints on every channel, including the ones that emit no gate.

    A writer working on a `deliverable` should still see the zero. The gate is scoped because a spec
    is formal on purpose; the measurement is not scoped, because a formal document that happens to
    carry a topic-comment fronting is not thereby wrong and the writer deserves to know it is there.
    """
    found = stats.get("spoken") or {}
    if not found:
        return []
    lines = ["", "## Spoken register", ""]
    scoped = channel in SPOKEN_CHANNELS
    if not found["hits"]:
        lines.append(f"None of the {found['measurable_rows']} matchable markers in "
                     "`data/spoken-markers.csv` are present. Every other section of this report "
                     "measures what to delete, so a draft can clear all of them and still read as a "
                     "translation of something. This section is the only one that reads what the "
                     "sentence has.")
    else:
        lines += ["| Marker | Hits | Found | What it carries |", "|---|---|---|---|"]
        for hit in found["hits"]:
            if "error" in hit:
                lines.append(f"| {hit['id']} | table error | {hit['error']} | fix the CSV |")
                continue
            samples = "; ".join(sample[:40] for sample in hit["samples"])
            lines.append(f"| {hit['id']} | {hit['count']} | {samples} | {hit['carries']} |")
    if found["manual_rows"]:
        lines += ["", "Not machine-checked, because the shape has no regex: "
                  + ", ".join(f"`{name}`" for name in found["manual_rows"])
                  + ". Read the rows and decide by eye."]
    if not scoped:
        lines += ["", f"No gate on channel `{channel}`. The floor applies where a reader is being "
                  "spoken to (" + ", ".join(sorted(SPOKEN_CHANNELS)) + "). Formal human Vietnamese "
                  "scores near zero on this table and is still human."]
    return lines


def _verdict_section(gate_rows: list[dict], tells: list[dict]) -> list[str]:
    blocking = [row["gate"] for row in gate_rows if not row["pass"] and row["severity"] in ("critical", "high")]
    blocking += [row["id"] for row in tells if row.get("severity") in ("critical", "high")]
    return ["", "## Verdict", "",
            "Blocking: " + (", ".join(blocking) if blocking else "none") + ".",
            "" if blocking else "Cadence and tell gates pass. Truth, claims and rights are checked elsewhere.", ""]


def report(stats: dict, gate_rows: list[dict], tells: list[dict], channel: str = DEFAULT_CHANNEL) -> str:
    lines = [f"# rewrite-human check — language {stats['language']}, channel {channel}", ""]
    if stats.get("insufficient"):
        # Cadence is unmeasurable here, the icon gates are not. Saying "nothing measurable" over a
        # tick-bulleted list would be the one wrong answer on the commonest bad draft there is.
        #
        # The tells and the verdict print here too, and they did not until 2026-08-05. Before that
        # this branch returned early, so on any input under two sentences - which is every headline,
        # every button, every badge - a blocking tell set the exit code to 1 while the report said
        # three decoration gates passed and nothing else. `Không chỉ là một tô bún, mà còn là cả một
        # câu chuyện` was the case that found it: `khong-chi-ma-con` fired, the run failed, and the
        # printed report named no reason. A gate that fails silently is worse than no gate, because
        # the exit code gets ignored once the report stops explaining it.
        lines += ["Fewer than two sentences of prose, so no cadence to measure. List shape, "
                  "decoration and the tells still count.",
                  "", "## Structure and decoration gates", ""]
        lines += (_gate_table(gate_rows) + _tell_section(tells)
                  + _spoken_section(stats, channel) + _verdict_section(gate_rows, tells))
        return "\n".join(lines)

    lines += [f"{stats['sentences']} sentences, {stats['total_units']} {stats['unit']}.", "",
              "## Cadence, structure and decoration gates", ""]
    lines += _gate_table(gate_rows)
    lines += _tell_section(tells)
    lines += _spoken_section(stats, channel)
    lines += _verdict_section(gate_rows, tells)
    return "\n".join(lines)


def blocking_count(gate_rows: list[dict], tells: list[dict]) -> int:
    return (sum(1 for row in gate_rows if not row["pass"] and row["severity"] in ("critical", "high"))
            + sum(1 for row in tells if row.get("severity") in ("critical", "high")))


def print_targets() -> str:
    lines = ["# Human-cadence targets", "",
             "Source: references/dossiers/copywriting-deep.md section 6.2. Calibration targets, not measured findings.", "",
             "| Metric | Target |", "|---|---|",
             f"| Mean sentence length | {TARGETS['en']['mean_low']}-{TARGETS['en']['mean_high']} words (EN); "
             f"{TARGETS['vi']['mean_low']}-{TARGETS['vi']['mean_high']} syllables (VI) |",
             f"| Longest / shortest | >= {RATIO_MIN} |",
             f"| Coefficient of variation | >= {CV_MIN} |",
             f"| Landing beats (<= {TARGETS['en']['beat']} words EN, <= {TARGETS['vi']['beat']} syllables VI) "
             f"| >= {SHORT_PER_150} per 150 |",
             f"| Consecutive near-equal lengths | <= {FLAT_RUN_MAX} |",
             f"| Consecutive same opening word | <= {SAME_OPENER_MAX} |",
             f"| Em dashes | <= {EM_DASH_PER_150} per 150 (0 in Vietnamese) |",
             f"| Paragraph length | <= {PARA_SENTENCES_MAX} sentences |",
             f"| Lists holding exactly three items | <= {TRICOLON_SHARE_MAX} of lists, "
             f"once a document has {LIST_BLOCKS_MIN} |", "",
             "The list figure is measured rather than chosen: across this skill's own reference files",
             "the share was 0.43 or lower everywhere except one file at 0.80, which turned out to be a",
             "template on inspection. Uniformity inside a single list is deliberately not measured -",
             "a glossary and a rejection-code table both look uniform, and both are correct.", "",
             "# Decoration budget", "",
             "House figures. The defect is not that a pictograph exists, it is that it arrived in a slot",
             "nobody chose - the same icon opening every bullet. Social and chat differ in kind, not in",
             "degree: an emoji there is what the surface does. Meaning-bearing signs "
             f"({''.join(sorted(DECORATION_KEEP))}) are never counted.", "",
             "| Channel | Structural (heading or line-opening) | Density |", "|---|---|---|"]
    for name, budget in sorted(DECORATION_BUDGET.items()):
        cap = "unbounded" if budget["structural"] is None else f"<= {budget['structural']}"
        lines.append(f"| {name} | {cap} | <= {budget['per_150']} per 150 |")
    lines += ["", f"Same icon opening consecutive lines: <= {DECORATION_RUN_MAX}, on every channel.", ""]
    lines += ["# Spoken register", "",
              "The only positive floor in this file. Everything above says what to delete; a draft can",
              "clear all of it and still be a translation of something nobody said. `data/spoken-markers.csv`",
              "carries the markers - Vietnamese final particles, topic-comment fronting with `thì`, a",
              "classifier plus a demonstrative, direction verbs glued to the main verb, `bị` with the",
              "affected party as subject - with the flat form that arrives in each one's place.", "",
              "| Measure | Floor |", "|---|---|",
              f"| Distinct markers present | >= {SPOKEN_DISTINCT_MIN} |",
              f"| Distinct markers, under {SPOKEN_SHORT_UNITS} units | >= {SPOKEN_DISTINCT_MIN_SHORT} |",
              f"| Share of hits held by one marker | <= {SPOKEN_TOP_SHARE_MAX}, once there are "
              f"{SPOKEN_VARIETY_MIN_HITS} hits |",
              f"| Channels gated | {', '.join(sorted(SPOKEN_CHANNELS))} |", "",
              "Two limits, both declared. There is no human-written conversational Vietnamese corpus in",
              "this repository, so the markers are graded as descriptions of the grammar and are not",
              "frequency-calibrated. And the gate is scoped by channel because formal human Vietnamese",
              "scores zero: the ND87 advertising-law text measures 0 distinct markers over 2925",
              "syllables and is entirely human. A floor that fails a ministry is a floor nobody keeps.", ""]
    return "\n".join(lines)


def self_check() -> str:
    """One runnable check. Every assertion below is a bug this script had or could plausibly have."""
    flat = " ".join(["The broth is simmered from bone each morning here."] * 6)
    stats = measure(flat, "en")
    assert stats["cv"] == 0.0, stats["cv"]
    assert stats["longest_flat_run"] >= 6, stats
    assert not any(row["pass"] for row in gates(stats) if row["gate"] == "burstiness-cv")

    bursty = ("Lunch is forty minutes long. The broth is simmered from bone from four in the morning, "
              "not made to order one bowl at a time, which is the only reason it holds. Nine years. "
              "Same pot, same corner, same six tables that were there before the street was paved. Come "
              "before eleven thirty and you will not wait for a seat.")
    stats = measure(bursty, "en")
    assert stats["cv"] >= CV_MIN, stats["cv"]
    assert stats["ratio"] >= RATIO_MIN, stats["ratio"]

    # Language detection must not need a hint.
    assert detect_language("Nồi nước dùng nấu từ xương từ bốn giờ sáng.") == "vi"
    assert detect_language("The broth is simmered from bone.") == "en"

    # Markdown furniture must not be measured as prose.
    assert measure("# Heading Here\n\n| a | b |\n|---|---|\n\nOne. Two words here now.", "en")["sentences"] == 2

    # Vietnamese counts syllables, so the same clause measures longer in VI than a word count would.
    assert units("nồi nước dùng nấu từ xương", "vi") == 6

    # The tells table must load, compile, and actually fire on its own examples.
    vi_hits = {row["id"] for row in find_tells(
        "Điều này có nghĩa là bạn tiết kiệm thời gian. Chúng tôi tự hào là đơn vị uy tín, chuyên nghiệp. "
        "Không chỉ ngon mà còn rẻ. Món này được nấu bởi đầu bếp trưởng.", "vi")}
    for expected in ("dieu-nay-co-nghia", "uy-tin-chuyen-nghiep", "khong-chi-ma-con", "duoc-boi-passive", "tu-hao"):
        assert expected in vi_hits, (expected, vi_hits)

    en_hits = {row["id"] for row in find_tells(
        "We are a prestigious and reputable brand. Furthermore, our premium broth, which is simmered "
        "from bone, which means depth, arrives at a reasonable price.", "en")}
    # One relative clause must not fire: a detector that flags clean copy gets switched off.
    assert "which-means-chain" not in {row["id"] for row in find_tells(
        "The broth is simmered from bone, which is the only reason it holds. Nine years.", "en")}
    for expected in ("prestigious", "furthermore", "which-means-chain", "adjective-for-evidence", "reasonable-price"):
        assert expected in en_hits, (expected, en_hits)

    # A clean Vietnamese draft must not trip the calque gates, or the table is unusable in practice.
    clean = find_tells("Trưa nay bạn có bốn mươi phút. Nồi nước dùng nấu từ xương từ bốn giờ sáng. "
                       "Chín năm, cùng một nồi, cùng một góc phố. Ghé trước 11h30 thì khỏi chờ.", "vi")
    assert not [row for row in clean if row.get("severity") in ("critical", "high")], clean

    # Variants an adversarial draft used and the table originally missed. Each of these was a
    # real escape: the expanded "It is worth noting", "dedicated team" as the cross of two listed
    # phrases, and the English original of the Vietnamese trong-the-gioi-ngay-nay calque.
    escapes = {row["id"] for row in find_tells(
        "In today's fast-paced digital world, our dedicated team delivers. It is worth noting that "
        "we are one of the leading providers. Customer satisfaction is our top priority.", "en")}
    for expected in ("todays-world-en", "prestigious", "furthermore", "one-of-the-most", "top-priority"):
        assert expected in escapes, (expected, escapes)

    # Every regex in the table must compile, in both language passes.
    for language in ("vi", "en"):
        for row in read_tells(language):
            re.compile(row["detect_regex"])

    # Tells must fire mid-paragraph, not only at line start. This regression cost four missed
    # tells on the first real draft the script was pointed at.
    mid = {row["id"] for row in find_tells(
        "Quán mở từ 2015. Hơn nữa, việc phục vụ luôn được chú trọng. Hãy tưởng tượng bạn ngồi đây.", "vi")}
    assert {"hon-nua-stack", "su-viec-nominal", "hay-tuong-tuong"} <= mid, mid

    # The positive side. Every regex in the table must fire on its own human example and on neither
    # translated one, which is the only thing separating a marker from a coincidence.
    for language in ("vi", "en"):
        for row in read_markers(language):
            if row["detect"] != "regex":
                assert not row["detect_regex"], row["id"]
                continue
            pattern = re.compile(row["detect_regex"])
            assert pattern.search(row["example_human"]), ("misses its own example", row["id"])
            assert not pattern.search(row["example_translated"]), ("fires on the flat side", row["id"])

    # A human chat line must clear the floor and a flat translated one must not, on the same channel.
    spoken_pass = measure("Để mình gói riêng phần đá nha. Tiền vận chuyển thì shop chịu. "
                          "Ba giờ chiều là hết rồi. Cái tô đó nặng hơn tô thường. "
                          "Bạn lấy size lớn không?", "vi")
    assert spoken_pass["spoken"]["distinct"] >= SPOKEN_DISTINCT_MIN, spoken_pass["spoken"]
    assert all(row["pass"] for row in spoken_gates(spoken_pass, "chat")), spoken_gates(spoken_pass, "chat")

    flat_vi = measure(
        "Chúng tôi tự hào giới thiệu sản phẩm serum mới nhất của thương hiệu. Sản phẩm được sản xuất "
        "theo tiêu chuẩn cao nhất, với các thành phần được tuyển chọn kỹ lưỡng. Quy trình kiểm định "
        "chất lượng được thực hiện tại phòng thí nghiệm độc lập trước khi sản phẩm được đưa ra thị "
        "trường. Sự hài lòng của khách hàng là ưu tiên hàng đầu của toàn bộ đội ngũ.", "vi")
    assert not [row for row in spoken_gates(flat_vi, "social")
                if row["gate"] == "spoken-register-present" and row["pass"]], flat_vi["spoken"]
    # And the same text on a formal channel emits no gate at all, rather than a passing one. This is
    # the ND87 finding: institutional Vietnamese scores zero here and is still human.
    assert spoken_gates(flat_vi, "deliverable") == []
    assert spoken_gates(flat_vi, "pr") == []

    # The cheat: one particle on every sentence end. Must fail variety, not slip through on count.
    cheat = measure("Hàng về rồi nhé. Bên mình gói cẩn thận nhé. Giao trong ngày nhé. "
                    "Bạn nhớ kiểm tra trước khi nhận nhé. Có gì cứ nhắn nhé.", "vi")
    variety = [row for row in spoken_gates(cheat, "chat") if row["gate"] == "spoken-register-variety"]
    assert variety and not variety[0]["pass"], cheat["spoken"]

    # A heading tell has to read the raw text, because prose_only() removes headings.
    assert "about-us-heading" in {row["id"] for row in find_tells("## About us\n\nOne. Two words now.", "en")}

    # A staccato run of short sentences must not read as machine flatness. This flagged a clean
    # English draft whose closing run was 8, 6, 5, 3 words - four deliberate beats.
    staccato = ("Your kitchen closes at ten and the last order lands at 21:47. Sixty-one restaurants "
                "in Da Nang run it. Two have called support since March. It costs 390,000 dong a "
                "month. No setup fee. Install it Tuesday and you will know by Friday.")
    assert {row["gate"]: row for row in gates(measure(staccato, "en"))}["flat-run"]["pass"]

    # A run of similar medium-length sentences must still fail: that is the actual tell.
    medium = (" ".join(["The broth is simmered from bone every single morning before we open."] * 4))
    assert not {row["gate"]: row for row in gates(measure(medium, "en"))}["flat-run"]["pass"]

    # Short-form copy must not fail on mean length alone. This is the gate that failed the first
    # clean Vietnamese draft the script was ever pointed at, while every other gate passed.
    short = ("Trưa nay bạn có bốn mươi phút.\n\n"
             "Nồi nước dùng bắt đầu từ bốn giờ sáng, nấu từ xương bò và gừng nướng, không pha từng tô "
             "theo khách gọi. Ông chủ mở quán năm 2009 và chưa đổi nồi. Mười bảy năm, cùng một góc "
             "phố Nguyễn Thái Học.\n\n"
             "Menu có bốn món. Không món nào là món phụ.\n\n"
             "Một tô 45.000 đồng, đủ no tới hết giờ chiều. Ghé trước 11h30 thì có chỗ ngồi ngay.")
    short_gates = {row["gate"]: row for row in gates(measure(short, "vi"))}
    assert short_gates["mean-length-low"]["pass"], short_gates["mean-length-low"]
    assert not [row for row in short_gates.values()
                if not row["pass"] and row["severity"] in ("critical", "high")], short_gates

    # A long-winded draft must still fail the high side.
    windy = " ".join(["The broth that we simmer here is carefully prepared from bone and roasted "
                      "ginger every single morning before the shop opens for the day."] * 3)
    assert not {row["gate"]: row for row in gates(measure(windy, "en"))}["mean-length-high"]["pass"]

    # The tricolon tell must need three short parallel items, not merely two commas.
    assert "tricolon-default" in {row["id"] for row in find_tells("The service is fast, clean, and friendly.", "en")}
    assert "tricolon-default" not in {row["id"] for row in find_tells(
        "Nồi nước dùng bắt đầu từ bốn giờ sáng, nấu từ xương bò và gừng nướng, không pha từng tô.", "vi")}

    # The reported sample must be the whole match, not an inner capture group.
    sample = next(row for row in find_tells("Điều này có nghĩa là bạn khỏi chờ. Ngồi xuống.", "vi")
                  if row["id"] == "dieu-nay-co-nghia")["samples"][0]
    assert sample.lower().startswith("điều này có nghĩa"), sample

    # A landing beat is counted per language. Vietnamese writes syllables separately, so a line
    # every bit as short as a four-word English beat measures six units and was scored as no beat
    # at all - the gate reported zero on a draft built out of them.
    beats = ("Cà phê rang tại xưởng ở Gò Vấp, giao trong ngày cho quán trong bán kính tám cây số. "
             "Ngày rang in dưới đáy túi. Không thấy ngày rang thì đừng mua.")
    assert measure(beats, "vi")["short_sentences"] >= 1, measure(beats, "vi")
    # And the English beat stays tight: a six-word sentence is not a beat in English.
    assert measure("The roast date is stamped on the base. No date, no sale.", "en")["short_sentences"] == 1

    # --- list shape ------------------------------------------------------------------------------
    # Blocks are counted from the raw text. Measured off prose_only() this returns zero on every
    # document, because prose_only() blanks list lines - which is how the tell went unmeasured for
    # as long as it did.
    template = ("## One\n\nLead line here.\n\n- Alpha item\n- Beta item\n- Gamma item\n\n"
                "## Two\n\nSecond lead line.\n\n- Delta item\n- Epsilon item\n- Zeta item\n\n"
                "## Three\n\nThird lead line.\n\n- Eta item\n- Theta item\n- Iota item\n\n"
                "## Four\n\nFourth lead line.\n\n- Kappa item\n- Lambda item\n- Mu item\n")
    shape = list_geometry(template)
    assert shape["blocks"] == 4 and shape["threes"] == 4, shape
    assert shape["three_share"] == 1.0, shape
    assert not {row["gate"]: row for row in gates(measure(template, "en"))}["tricolon-everywhere"]["pass"]

    # Under the floor the gate is absent, not passing. Two lists of three is 1.00 and innocent.
    two = "Lead line here.\n\n- Alpha\n- Beta\n- Gamma\n\nAnother lead.\n\n- Delta\n- Epsilon\n- Zeta\n"
    assert list_geometry(two)["three_share"] == 1.0
    assert "tricolon-everywhere" not in {row["gate"] for row in gates(measure(two, "en"))}

    # Varying the counts is the fix, and it has to be enough to pass. Same four lists, real lengths.
    varied = template.replace("- Beta item\n", "- Beta item\n- Beta the second\n") \
                     .replace("- Zeta item\n", "- Zeta item\n- Zeta again\n- Zeta once more\n") \
                     .replace("- Iota item\n", "")
    assert {row["gate"]: row for row in gates(measure(varied, "en"))}["tricolon-everywhere"]["pass"], \
        list_geometry(varied)

    # Nesting is its own block: three sub-points under each of three points is not a list of nine.
    nested = "- Alpha\n  - one\n  - two\n  - three\n- Beta\n- Gamma\n"
    assert sorted(len(block) for block in list_blocks(nested)) == [3, 3], list_blocks(nested)

    # A blank line inside a loose list does not close it, and a lone bullet is not a list.
    assert list_geometry("- Alpha\n\n- Beta\n\n- Gamma\n")["sizes"] == [3]
    assert list_blocks("Prose here.\n\n- Only one\n\nMore prose.\n") == []

    # Ordered lists are the same shape as bulleted ones.
    assert list_geometry("1. Alpha\n2. Beta\n3. Gamma\n")["threes"] == 1

    # --- decoration ------------------------------------------------------------------------------
    # The draft this gate exists for: a checklist where every line opens on a pictograph. It has no
    # measurable cadence at all, which is why `insufficient` had to stop short-circuiting the gates.
    bulleted = ("## ✨ Ưu điểm\n"
                "- \U0001f680 Giao trong ngày\n"
                "- \U0001f680 Rang tại xưởng\n"
                "- \U0001f680 Đổi trả 7 ngày\n")
    stats = measure(bulleted, "vi")
    assert stats.get("insufficient"), stats
    deck = {row["gate"]: row for row in gates(stats, "deliverable")}
    assert set(deck) == {"decoration-as-structure", "decoration-density", "decoration-run"}, deck
    assert not deck["decoration-as-structure"]["pass"], deck["decoration-as-structure"]
    # Four pictographs: one in the heading, three opening bullets. All structural, none inline.
    assert stats["decoration"] == {"structural": 4, "inline": 0, "total": 4,
                                   "longest_icon_opener_run": 3,
                                   "samples": ["✨", "\U0001f680"]}, stats["decoration"]
    # Same draft on social: the surface does this, so structure is unbounded and the gate passes.
    social = {row["gate"]: row for row in gates(stats, "social")}
    assert social["decoration-as-structure"]["pass"], social["decoration-as-structure"]
    # The run rule holds anyway, because three identical openers is a generated list on any surface.
    assert not social["decoration-run"]["pass"], social["decoration-run"]
    assert not deck["decoration-run"]["pass"], deck["decoration-run"]

    # A writer varying the icon per line is making decisions, so the run gate must not fire on it.
    varied = bulleted.replace("- \U0001f680 Rang", "- \U0001f6a9 Rang")
    assert measure(varied, "vi")["decoration"]["longest_icon_opener_run"] == 1, measure(varied, "vi")

    # Meaning-bearing signs are never decoration. Flagging the registered mark in brand copy is the
    # fastest way to get the whole gate switched off.
    marks = ("Cà phê Minh Thép® rang tại xưởng ở Gò Vấp, giao trong ngày. Nhiệt độ rang 210℃, "
             "ghi dưới đáy túi. Không thấy thì đừng mua.")
    assert measure(marks, "vi")["decoration"]["total"] == 0, measure(marks, "vi")["decoration"]
    assert all(row["pass"] for row in gates(measure(marks, "vi"), "deliverable")
               if row["gate"].startswith("decoration"))

    # An emoji inside a sentence is a decision and stays inline; one in a heading is structure
    # wherever it sits in the line.
    mid = ("Chủ quán nhắn lúc bốn giờ sáng \U0001f605 vì nồi nước dùng chưa tới. Chúng tôi giao lại "
           "trong hai tiếng.")
    counted = measure(mid, "vi")["decoration"]
    assert (counted["structural"], counted["inline"]) == (0, 1), counted
    tail = measure("## Giao hàng \U0001f69a\n\nGiao trong ngày ở Gò Vấp. Ngoài bán kính tám cây thì hai ngày.", "vi")
    assert tail["decoration"]["structural"] == 1, tail["decoration"]

    # And prose with no pictographs at all reports nothing, on the strictest channel.
    assert measure(beats, "vi")["decoration"]["total"] == 0
    assert all(row["pass"] for row in gates(measure(beats, "vi"), "deliverable")
               if row["gate"].startswith("decoration"))
    # The cadence gates still run alongside them, rather than being displaced.
    named = {row["gate"] for row in gates(measure(bursty, "en"), "deliverable")}
    assert "burstiness-cv" in named and "decoration-density" in named, named

    return "self-check passed\n"


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", help="file to measure")
    parser.add_argument("--text", help="measure this string instead of a file")
    parser.add_argument("--lang", choices=("vi", "en", "auto"), default="auto")
    parser.add_argument("--channel", choices=sorted(DECORATION_BUDGET), default=DEFAULT_CHANNEL,
                        help="where this copy is going; it sets the decoration budget only "
                             f"(default {DEFAULT_CHANNEL}, which allows none)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="write the report here instead of stdout")
    parser.add_argument("--targets", action="store_true", help="print the targets and exit")
    parser.add_argument("--self-check", action="store_true", help="verify the measurements and exit")
    args = parser.parse_args()

    if args.self_check:
        emit(self_check())
        return 0
    if args.targets:
        emit(print_targets(), args.output)
        return 0
    if not (args.check or args.text):
        parser.error("pass --check FILE, --text STRING, --targets, or --self-check")

    text = args.text if args.text else Path(args.check).read_text(encoding="utf-8")
    language = detect_language(text) if args.lang == "auto" else args.lang
    stats = measure(text, language)
    gate_rows = gates(stats, args.channel)
    tells = find_tells(text, language)

    if args.json:
        emit_json({"stats": stats, "channel": args.channel, "gates": gate_rows, "tells": tells,
                   "blocking": blocking_count(gate_rows, tells)}, args.output)
    else:
        emit(report(stats, gate_rows, tells, args.channel), args.output)
    return 1 if blocking_count(gate_rows, tells) else 0


if __name__ == "__main__":
    raise SystemExit(main())
