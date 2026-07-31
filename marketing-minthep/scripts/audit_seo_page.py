#!/usr/bin/env python3
"""Measure the on-page part of an SEO draft, and refuse to guess the rest.

This exists because SEO advice is the most folklore-heavy material this skill touches, and almost
none of the folklore is checkable. Keyword volume, difficulty, ranking position and competitor
strength are all live SERP facts: they change weekly, they differ by device and city, and no
offline script can know them. Anything here that claimed to score "SEO strength" would be
inventing numbers, which is the exact failure `references/anti-ai-quality.md` and the anti-
fabrication protocol exist to stop.

So the split is deliberate. What is measurable from the draft alone gets measured: whether the
page answers the query before the brand narrative, whether the title survives truncation, whether
the headings form a ladder, whether the page carries checkable proof or only fluent sentences.
What is not measurable from the draft gets named as unknown and routed to
`references/market-data-collection.md`, which is where live verification belongs.

The gate that matters most is `information-gain`. A draft can satisfy every keyword rule and still
be the ninth restatement of the same page, and that page has no reason to rank; the only durable
on-page advantage is carrying something the other nine do not. That is countable - a number with a
unit, a date, a name, a way to reach somebody - and `check_specificity.py` already counts it, so
this script reuses those detectors rather than growing a second set that would drift.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_specificity  # noqa: E402
import rewrite_human  # noqa: E402
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "data" / "seo-intents.csv"

# Desktop title truncation. Observed convention rather than a published rule: Google renders titles
# in a fixed pixel box, so the limit is width and not characters, which is why a title of capitals
# truncates sooner than one of lowercase. Treat a failure as truncation risk, not as a ranking
# penalty - and remember Google rewrites a large share of titles regardless, so this gate protects
# the version a human sees in the SERP, not a score.
TITLE_PIXELS_MAX = 580
# Under this a title is not describing a page. No source; it is the floor at which the title stops
# carrying the query plus any qualifier at all.
TITLE_CHARS_MIN = 15
# Meta description bounds. The description is not a ranking input; it is the ad copy for the click,
# and both ends of this band cost clicks - too short wastes the slot, too long truncates mid-clause.
META_CHARS_MIN, META_CHARS_MAX = 70, 160
# The searcher decides whether to stay inside roughly one screen of text. If the sentence that
# addresses the query has not arrived by here, the page opened with narrative.
ANSWER_WITHIN_UNITS = 120
# Exact-phrase repetitions per 300 words. Not a penalty threshold - nobody outside Google knows
# where that sits, and modern ranking does not need the phrase repeated at all. It is a writing
# tell: past three per 300 words, a person reading aloud hears the seam.
PHRASE_PER_300_MAX = 3.0
# A rate has to be extrapolated from whatever is there, and on a short page that extrapolation is
# noise. A 60-word price page carrying its query in the H1 and again in the answering sentence scores
# 10 per 300 and is not stuffed - it is a page doing exactly what the intent asked for, twice. So the
# rate can only fail once the phrase has appeared this many times in absolute terms. Four, because
# nobody hears a seam at three no matter how short the page is, and a page long enough to hold four
# is long enough for the rate to mean something.
PHRASE_HITS_FLOOR = 4
# Checkable specifics per 300 words, which is one per 100 - a floor low enough to state out loud
# and defend. Calibrated on the only corpus available offline, this skill's own 60 reference files:
# median 3.7, range 0 to 34.4, and 21 of the 60 fall below the line. Two honesties about that.
# Documentation is not a commercial page, so this is a floor borrowed from an adjacent corpus rather
# than derived from anything about ranking. And the files that fail are the ones the audit in #16
# already flagged as thin, which is corroboration, not proof.
GAIN_PER_300_MIN = 3.0

FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING = re.compile(r"^(#{1,6})\s+(\S.*?)\s*#*\s*$")
MD_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
MD_IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)")
FENCE = re.compile(r"^\s*```")

# Query words that carry no matching power. Deliberately short: a long stop list starts deleting
# the words a Vietnamese query is actually made of, and `giá` or `mua` is the whole intent.
STOPWORDS = {
    "the", "a", "an", "of", "for", "to", "in", "on", "at", "is", "are", "and", "or", "with",
    "how", "what", "which", "best", "vs",
    "cua", "va", "cho", "voi", "o", "la", "co", "nao", "gi", "the", "nhat", "khong",
}

# A coarse per-character width table at the size Google renders desktop titles. Estimated, not
# measured from a font file: the point is to separate "fits comfortably" from "will be cut", and a
# character-count rule gets that wrong on titles made of capitals or of i's and l's. Vietnamese
# diacritics sit above the glyph and add no width, which is why folding is safe here.
_NARROW = set("iljtfrI.,:;'|!()[]{}-’")
_WIDE = set("mwMW@%—")
_MEDIUM_UPPER = set("ABCDEFGHJKLNOPQRSTUVXYZ")


def fold(text: str) -> str:
    """Lowercase and strip diacritics, so `giá` and `gia` are one token.

    Vietnamese searchers type both, phones autocorrect between them, and a matcher that treats them
    as different words reports a missing keyword that is present on the page.
    """
    stripped = "".join(ch for ch in unicodedata.normalize("NFD", text)
                       if not unicodedata.combining(ch))
    return unicodedata.normalize("NFC", stripped).lower()


def title_pixels(title: str) -> int:
    """Estimated rendered width. See `_NARROW`: an estimate on purpose, reported as one."""
    total = 0.0
    for char in fold(title):
        if char == " ":
            total += 4.5
        elif char in _NARROW:
            total += 4.0
        elif char in _WIDE:
            total += 14.0
        elif char.isdigit():
            total += 9.0
        elif char in _MEDIUM_UPPER or char.isupper():
            total += 10.5
        else:
            total += 8.0
    return round(total)


def load_intents() -> list[dict[str, str]]:
    if not TABLE.exists():
        return []
    return list(csv.DictReader(io.StringIO(TABLE.read_text(encoding="utf-8"))))


def intent_row(intent: str | None) -> dict[str, str] | None:
    if not intent:
        return None
    for row in load_intents():
        if row["id"] == intent:
            return row
    return None


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Read a `title:` / `description:` / `query:` / `intent:` block if the draft carries one.

    A markdown draft has no title tag and no meta description, so those two fields have to be
    declared somewhere or the audit is measuring an H1 and calling it a title. Front matter is
    where a page brief already puts them. When it is absent the fields fall back to the H1 and the
    first paragraph, and the report says `inferred` rather than pretending they were specified -
    which matters, because a fallback title that passes is not a title that will ship.
    """
    match = FRONT_MATTER.match(text)
    if not match:
        return {}, text
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition(":")
            fields[key.strip().lower()] = value.strip().strip("\"'")
    return fields, text[match.end():]


def headings(body: str) -> list[tuple[int, str]]:
    found, fenced = [], False
    for line in body.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = HEADING.match(line)
        if match:
            found.append((len(match.group(1)), match.group(2).strip()))
    return found


def head_terms(query: str) -> list[str]:
    """The query words that have to appear somewhere. Stopwords out, order irrelevant."""
    words = [word for word in re.findall(r"[\wÀ-ỹ]+", fold(query)) if word]
    return [word for word in words if word not in STOPWORDS and len(word) > 1]


def reading_stream(body: str) -> list[str]:
    """Every piece of text a reader passes through, in document order, prose or not.

    The cadence tools in `rewrite_human.py` deliberately blank lists and tables before measuring,
    because a bullet is not a sentence and rhythm gates would read nonsense off a table. Reusing
    that here was a mistake I made and had to undo: on this skill's own reference files it scored
    26 of 60 as carrying no checkable content, when their numbers were all sitting in tables. On an
    SEO page it would be worse than wrong. The winning page for a `comparison` query *is* a
    side-by-side table, and a `price` page's whole proof is one figure in a row - a reader who finds
    the price in row two has been answered, and a gate that reports zero facts there is lying.

    So proof-counting, query placement and repetition all run over this stream: headings included,
    list markers and table pipes stripped, code fences dropped because a snippet is not a claim.
    """
    pieces, fenced = [], False
    for line in body.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        stripped = line.strip()
        if not stripped or set(stripped) <= set("|-: "):
            continue  # blank, or a table's separator rule
        stripped = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", stripped)  # list marker
        stripped = re.sub(r"^#{1,6}\s+", "", stripped)                 # heading hashes
        if "|" in stripped:
            cells = [cell.strip() for cell in stripped.strip("|").split("|") if cell.strip()]
            pieces.extend(cells)
            continue
        pieces.extend(rewrite_human.sentences(stripped) or [stripped])
    return [piece for piece in pieces if piece.strip()]


def read_page(text: str, query: str | None, intent: str | None) -> dict:
    """Everything measurable about the draft, with the provenance of each field attached."""
    fields, body = parse_front_matter(text)
    marks = headings(body)
    h1s = [name for level, name in marks if level == 1]

    title = fields.get("title") or (h1s[0] if h1s else "")
    title_from = "declared" if fields.get("title") else ("inferred" if h1s else "unknown")
    description = fields.get("description", "")
    prose = rewrite_human.prose_only(body)
    paragraphs = [block for block in rewrite_human.paragraphs(prose) if block]
    if not description and paragraphs:
        description = " ".join(paragraphs[0])
    description_from = "declared" if fields.get("description") else (
        "inferred" if paragraphs else "unknown")

    query = query or fields.get("query") or ""
    intent = intent or fields.get("intent") or ""
    terms = head_terms(query)

    language = rewrite_human.detect_language(body)
    stream = reading_stream(body)
    total_units = sum(rewrite_human.units(piece, language) for piece in stream)

    # Where the query is first addressed, measured in words read before it. Every head term in one
    # piece of text is the test: a page can mention `giá` in the intro and `iPhone` in section four
    # without ever having addressed `giá iPhone`.
    answer_at, seen = None, 0
    for piece in stream:
        folded = fold(piece)
        if terms and all(term in folded for term in terms) and answer_at is None:
            answer_at = seen
        seen += rewrite_human.units(piece, language)

    per300 = (total_units / 300) or 1
    phrase_hits = fold(" ".join(stream)).count(fold(query)) if query.strip() else 0

    # Checkable statements, not sentences with facts in them. A name alone is weak evidence - most
    # brand copy is full of names - so a proof here needs a quantity, a date or a contact.
    proofs = 0
    for piece in stream:
        found = check_specificity.specifics(piece)
        if found["quantity"] or found["date"] or found["contact"]:
            proofs += 1
    gain = sum(check_specificity.specifics(piece)["total"] for piece in stream)

    links = [(label, href) for label, href in MD_LINK.findall(body)]
    internal = [href for _, href in links
                if not href.startswith(("http://", "https://", "mailto:", "tel:"))]
    images = MD_IMAGE.findall(body)

    return {
        "language": language,
        "title": title, "title_provenance": title_from,
        "title_chars": len(title), "title_pixels": title_pixels(title),
        "description": description, "description_provenance": description_from,
        "description_chars": len(description),
        "query": query, "head_terms": terms,
        "intent": intent or "unknown",
        "headings": marks, "h1_count": len(h1s),
        "skipped_levels": [(marks[i][0], marks[i + 1][0]) for i in range(len(marks) - 1)
                           if marks[i + 1][0] - marks[i][0] > 1],
        "sentences": len(stream), "total_units": total_units,
        "answer_at_units": answer_at,
        "phrase_hits": phrase_hits, "phrase_per_300": round(phrase_hits / per300, 2),
        "specifics": gain, "gain_per_300": round(gain / per300, 2),
        "checkable_statements": proofs,
        "links": len(links), "internal_links": len(internal),
        "images": len(images),
        "images_without_alt": sum(1 for alt, _ in images if not alt.strip()),
    }


def _row(gate: str, passed: bool, severity: str, observed: str, target: str, why: str) -> dict:
    return {"gate": gate, "pass": passed, "severity": severity,
            "observed": observed, "target": target, "why": why}


def gates(stats: dict) -> list[dict]:
    """The gates the draft alone can settle. Absent beats guessed, so several are conditional."""
    rows = [
        _row("title-present", stats["title_chars"] >= TITLE_CHARS_MIN, "critical",
             f"{stats['title_chars']} characters, {stats['title_provenance']}",
             f">= {TITLE_CHARS_MIN} characters",
             "A page with no title has nothing to show in the result. `inferred` means it was read "
             "off the H1, which passes here and still ships without a title tag, because an H1 and "
             "a title do different jobs and nobody wrote the second one down."),
        _row("title-truncation", stats["title_pixels"] <= TITLE_PIXELS_MAX, "medium",
             f"about {stats['title_pixels']}px estimated",
             f"<= {TITLE_PIXELS_MAX}px",
             "Truncation cuts the qualifier that made the title match the query, and the qualifier "
             "is usually at the end. Width rather than characters, because capitals are wider."),
    ]

    if stats["description_provenance"] == "unknown":
        rows.append(_row("meta-description", False, "medium", "absent",
                         f"{META_CHARS_MIN}-{META_CHARS_MAX} characters",
                         "The description is the ad copy for the click. It is not a ranking input, "
                         "and leaving it to be auto-generated hands the sentence to a machine."))
    else:
        chars = stats["description_chars"]
        rows.append(_row("meta-description", META_CHARS_MIN <= chars <= META_CHARS_MAX, "medium",
                         f"{chars} characters, {stats['description_provenance']}",
                         f"{META_CHARS_MIN}-{META_CHARS_MAX} characters",
                         "Short wastes the slot; long truncates mid-clause and loses the promise."))

    rows.append(_row("single-h1", stats["h1_count"] == 1, "high",
                     f"{stats['h1_count']} H1" + ("" if stats["h1_count"] == 1 else " headings"),
                     "exactly 1",
                     "Two H1s means two pages were merged, or a template is emitting one. Either "
                     "way the reader cannot tell what the page is about from its own structure."))
    rows.append(_row("heading-ladder", not stats["skipped_levels"], "medium",
                     f"skips: {stats['skipped_levels']}" if stats["skipped_levels"] else "no skips",
                     "no level skipped",
                     "A jump from H2 to H4 is decoration standing in for hierarchy. Screen readers "
                     "and outline extraction both read the ladder, so the skip is a real defect."))

    if stats["head_terms"]:
        title_folded = fold(stats["title"])
        rows.append(_row("query-in-title", all(term in title_folded for term in stats["head_terms"]),
                         "high",
                         f"title carries {[t for t in stats['head_terms'] if t in title_folded]}",
                         f"all of {stats['head_terms']}",
                         "Not because density matters, but because a title that does not contain "
                         "the query does not look like an answer to it in the result list."))
        heading_text = fold(" ".join(name for _, name in stats["headings"]))
        rows.append(_row("query-in-a-heading",
                         any(term in heading_text for term in stats["head_terms"]), "low",
                         "present in a heading" if any(
                             term in heading_text for term in stats["head_terms"]) else "absent",
                         "at least one head term in a heading",
                         "A heading is where a skimming reader checks that the page is about their "
                         "question. This is a readability gate wearing an SEO label."))
        answered = stats["answer_at_units"]
        rows.append(_row("answer-before-narrative",
                         answered is not None and answered <= ANSWER_WITHIN_UNITS, "high",
                         "never answered in one sentence" if answered is None
                         else f"first addressed after {answered} words",
                         f"within {ANSWER_WITHIN_UNITS} words",
                         "Satisfy the query, then expand. A page that opens on company narrative "
                         "is asking the searcher to trust it before it has been useful, and the "
                         "back button is one tap away."))
        rows.append(_row("phrase-repetition",
                         stats["phrase_hits"] < PHRASE_HITS_FLOOR
                         or stats["phrase_per_300"] <= PHRASE_PER_300_MAX, "medium",
                         f"{stats['phrase_hits']} exact repeats, {stats['phrase_per_300']} per 300",
                         f"<= {PHRASE_PER_300_MAX} per 300 words, once past "
                         f"{PHRASE_HITS_FLOOR} repeats",
                         "Repetition past this is audible when read aloud. Ranking does not need "
                         "the phrase repeated; a human deciding whether to keep reading does need "
                         "the sentences to sound like a person wrote them. Under four repeats the "
                         "rate is extrapolated from too little text to mean anything, so it is not "
                         "held against the page."))

    rows.append(_row("information-gain", stats["gain_per_300"] >= GAIN_PER_300_MIN, "high",
                     f"{stats['specifics']} specifics, {stats['gain_per_300']} per 300 words",
                     f">= {GAIN_PER_300_MIN} per 300 words",
                     "The only on-page advantage that survives a competitor reading your page. "
                     "Nine pages restating the same summary have no reason to outrank each other, "
                     "and the tenth with a measured number does."))
    rows.append(_row("internal-link", stats["internal_links"] >= 1, "low",
                     f"{stats['internal_links']} internal, {stats['links'] - stats['internal_links']} external",
                     ">= 1 internal link",
                     "An orphan page is one nobody can navigate to, which is a site problem the "
                     "draft can still fix by pointing at the page it belongs beside."))

    if stats["images"]:
        rows.append(_row("image-alt", stats["images_without_alt"] == 0, "medium",
                         f"{stats['images_without_alt']} of {stats['images']} images without alt",
                         "every image has alt text",
                         "Alt text is the accessibility requirement first and the image-search "
                         "input second. Empty alt on a product photo fails both."))

    row = intent_row(stats["intent"])
    if row:
        needed = int(row["proofs_required"])
        rows.append(_row("proof-count-for-intent",
                         stats["checkable_statements"] >= needed, "high",
                         f"{stats['checkable_statements']} statements carrying a number, date or contact, for "
                         f"`{stats['intent']}`",
                         f">= {needed}",
                         f"{row['page_type_that_wins']}. Word count is not the measure - this "
                         f"intent needs {needed} things a reader can check, and that is what is "
                         f"counted. Reflex to reject: {row['reflex_to_reject'].lower()}."))
    return rows


def unknowns(stats: dict) -> list[str]:
    """What this script cannot know, stated every run so it is never mistaken for a full audit."""
    missing = [
        "Search volume, difficulty and seasonality for the query: live SERP facts, "
        "unavailable offline. Verify per `references/market-data-collection.md`.",
        "What currently ranks, and whether this page type can win at all: read the SERP. "
        "`best-of` and `comparison` queries are often held by aggregators.",
        "Whether the page is indexable: robots, canonical, hreflang, status codes and render "
        "behaviour live on the server, not in the draft.",
        "Whether the claims are true or legal. That is `claims-proof-ledger.md` and "
        "`rights-and-claims.md`, and no cadence or structure gate substitutes for it.",
    ]
    if not stats["head_terms"]:
        missing.insert(0, "No query was given, so every query-placement gate was skipped rather "
                          "than passed. Pass --query to get them.")
    if stats["intent"] == "unknown":
        missing.insert(0, "No intent was given, so the proof-count gate was skipped. "
                          "Run --list-intents and pass --intent.")
    return missing


def blocking_count(rows: list[dict]) -> int:
    return sum(1 for row in rows if not row["pass"] and row["severity"] in ("critical", "high"))


def report(stats: dict, rows: list[dict]) -> str:
    lines = ["# SEO on-page audit", "",
             f"Language `{stats['language']}`, {stats['sentences']} sentences, "
             f"{stats['total_units']} words of readable text, intent `{stats['intent']}`.",
             f"Title `{stats['title_provenance']}`, description "
             f"`{stats['description_provenance']}`.", "",
             "## Gates", "", "| Gate | Verdict | Severity | Observed | Target |", "|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['gate']} | {'pass' if row['pass'] else 'FAIL'} | {row['severity']} "
                     f"| {row['observed']} | {row['target']} |")
    failed = [row for row in rows if not row["pass"]]
    if failed:
        lines += ["", "## Why each failure matters", ""]
        for row in failed:
            lines.append(f"- **{row['gate']}** ({row['severity']}): {row['why']}")
    lines += ["", "## Not established by this run", ""]
    lines += [f"- {item}" for item in unknowns(stats)]
    lines += ["", f"Blocking failures: {blocking_count(rows)}.", ""]
    return "\n".join(lines)


def list_intents() -> str:
    lines = ["# Query intents", "",
             "| id | signals (VI) | page type that wins | proofs | reflex to reject |",
             "|---|---|---|---|---|"]
    for row in load_intents():
        lines.append(f"| `{row['id']}` | {row['query_signals_vi']} | {row['page_type_that_wins']} "
                     f"| {row['proofs_required']} | {row['reflex_to_reject']} |")
    lines += ["", "The intent decides the page type, and the page type decides what proof is "
                  "required. Guessing the intent from the product rather than from the query is "
                  "how a product page ends up competing with a listicle.", ""]
    return "\n".join(lines)


def explain(intent: str) -> str:
    row = intent_row(intent)
    if not row:
        available = ", ".join(row["id"] for row in load_intents())
        return f"No intent `{intent}`. Available: {available}\n"
    return "\n".join([
        f"# `{row['id']}` ({row['intent']})", "",
        f"**Searcher state.** {row['searcher_state']}.", "",
        f"**Signals.** VI: {row['query_signals_vi']}. EN: {row['query_signals_en']}.", "",
        f"**Page type that wins.** {row['page_type_that_wins']}.", "",
        f"**Proof required.** {row['proofs_required']} checkable things. "
        f"For example: {row['proof_examples']}.", "",
        f"**Title shape.** {row['title_shape']}.", "",
        f"**Reject.** {row['reflex_to_reject']}.", "",
        f"**Vietnam.** {row['vn_note']}.", "",
        f"**What ranking here would not establish.** {row['what_it_does_not_establish']}.", "",
    ])


def print_targets() -> str:
    return "\n".join([
        "# Thresholds", "",
        "| Measure | Target |", "|---|---|",
        f"| Title width | <= {TITLE_PIXELS_MAX}px estimated |",
        f"| Title length | >= {TITLE_CHARS_MIN} characters |",
        f"| Meta description | {META_CHARS_MIN}-{META_CHARS_MAX} characters |",
        f"| Query addressed within | {ANSWER_WITHIN_UNITS} words |",
        f"| Exact-phrase repeats | <= {PHRASE_PER_300_MAX} per 300 words, "
        f"unenforced under {PHRASE_HITS_FLOOR} repeats |",
        f"| Checkable specifics | >= {GAIN_PER_300_MIN} per 300 words |",
        "| H1 headings | exactly 1 |",
        "| Heading levels | none skipped |", "",
        "The title width is an estimate from a per-character table, not a rendering, and Google",
        "rewrites a large share of titles anyway - so read it as truncation risk rather than as a",
        "rule. None of these are ranking factors and this script does not claim to predict",
        "ranking. Volume, difficulty, competition and indexability are live facts; see the",
        "`Not established` block that every run prints.", "",
    ])


def self_check() -> str:
    use_utf8_stdout()
    rows = load_intents()
    assert len(rows) >= 8, len(rows)
    assert len({row["id"] for row in rows}) == len(rows), "duplicate intent id"
    for row in rows:
        assert int(row["proofs_required"]) >= 2, row["id"]
        assert all(value.strip() for value in row.values()), row["id"]

    # --- folding and width ---
    assert fold("Giá iPhone 15 ở TP HCM") == "gia iphone 15 o tp hcm"
    assert head_terms("giá iPhone 15 là bao nhiêu") == ["gia", "iphone", "15", "bao", "nhieu"]
    # Capitals are wider than lowercase, which is the whole reason width beats character count.
    assert title_pixels("MMMMMMMMMM") > title_pixels("iiiiiiiiii")
    assert title_pixels("Giá iPhone") == title_pixels("Gia iPhone"), "diacritics added width"

    # --- front matter and provenance ---
    declared = ("---\ntitle: Giá iPhone 15 tại Gò Vấp\ndescription: Bảng giá cập nhật.\n"
                "query: giá iPhone 15\nintent: price\n---\n\n# Giá iPhone 15\n\nGiá là 20 triệu.\n")
    fields, body = parse_front_matter(declared)
    assert fields["intent"] == "price" and body.startswith("# Giá"), (fields, body[:20])
    assert read_page(declared, None, None)["title_provenance"] == "declared"

    # An H1 is not a title. The fallback is reported as inferred, because a page whose title was
    # never written down ships without one however well the H1 reads.
    bare = "# Giá iPhone 15 tại Gò Vấp\n\nGiá hôm nay là 20 triệu đồng.\n"
    stats = read_page(bare, "giá iPhone 15", None)
    assert stats["title_provenance"] == "inferred", stats["title_provenance"]
    assert stats["intent"] == "unknown"
    named = {row["gate"] for row in gates(stats)}
    assert "proof-count-for-intent" not in named, "an unknown intent must skip, not pass"
    assert any("intent was given" in item for item in unknowns(stats))

    # --- the narrative-first failure this gate exists for ---
    narrative = ("---\ntitle: Về chúng tôi và hành trình thương hiệu\nquery: giá bàn gỗ sồi\n---\n\n"
                 "# Về chúng tôi\n\n"
                 + ("Chúng tôi là một thương hiệu tận tâm với nhiều năm kinh nghiệm trong ngành nội "
                    "thất cao cấp và luôn đặt khách hàng lên hàng đầu. " * 6)
                 + "\n\nGiá bàn gỗ sồi hiện tại là 4.500.000 đồng.\n")
    verdicts = {row["gate"]: row for row in gates(read_page(narrative, None, None))}
    assert not verdicts["answer-before-narrative"]["pass"], verdicts["answer-before-narrative"]
    assert not verdicts["query-in-title"]["pass"]
    assert not verdicts["information-gain"]["pass"], "one number under 160 words of fluff is not gain"

    # --- the same page, answering first ---
    answered = ("---\ntitle: Giá bàn gỗ sồi 2026\ndescription: "
                + "Giá bàn gỗ sồi tại xưởng Gò Vấp, cập nhật tháng 7 2026, kèm phí giao và bảo hành."
                + "\nquery: giá bàn gỗ sồi\nintent: price\n---\n\n"
                "# Giá bàn gỗ sồi\n\nGiá bàn gỗ sồi là 4.500.000 đồng, cập nhật ngày 12/07/2026. "
                "Mặt bàn dày 25mm. Giao trong 48 giờ ở TP HCM, phí 150.000 đồng.\n\n"
                "## Giá thay đổi theo gì\n\nKích thước 1m6 cộng thêm 800.000 đồng. "
                "Gọi 0901 234 567 để đặt.\n\nXem thêm [bàn ăn gỗ](/ban-an-go).\n")
    verdicts = {row["gate"]: row for row in gates(read_page(answered, None, None))}
    for gate in ("answer-before-narrative", "query-in-title", "information-gain",
                 "proof-count-for-intent", "internal-link", "meta-description", "single-h1"):
        assert verdicts[gate]["pass"], (gate, verdicts[gate])
    assert blocking_count(list(verdicts.values())) == 0, [
        row for row in verdicts.values() if not row["pass"]]

    # --- proof inside a table counts, which is the bug this reader was rewritten to fix ---
    # A comparison page's proof IS the table. Counting prose only scored 26 of this skill's own 60
    # reference files as carrying nothing, with their numbers sitting in rows the reader skipped.
    tabular = ("---\ntitle: So sánh bàn gỗ sồi và gỗ cao su\nquery: so sánh bàn gỗ sồi\n"
               "description: Bảng so sánh hai loại mặt bàn theo giá, độ dày và bảo hành, đo tháng 7.\n"
               "intent: comparison\n---\n\n# So sánh bàn gỗ sồi và gỗ cao su\n\n"
               "| Trục | Sồi | Cao su |\n|---|---|---|\n"
               "| Giá | 4.500.000 đồng | 2.100.000 đồng |\n"
               "| Độ dày mặt | 25mm | 18mm |\n"
               "| Bảo hành | 24 tháng | 12 tháng |\n"
               "| Giao ở TP HCM | 48 giờ | 24 giờ |\n\nXem [bàn ăn gỗ](/ban-an-go).\n")
    stream = reading_stream(tabular.split("---\n")[2])
    assert "4.500.000 đồng" in stream, stream
    assert not any(set(piece) <= set("|-: ") for piece in stream), "separator rule leaked in"
    verdicts = {row["gate"]: row for row in gates(read_page(tabular, None, None))}
    for gate in ("information-gain", "proof-count-for-intent", "answer-before-narrative"):
        assert verdicts[gate]["pass"], (gate, verdicts[gate])

    # A heading is text a reader passes through, so it can be where the query is answered.
    assert reading_stream("## Giá bàn gỗ sồi\n")[0] == "Giá bàn gỗ sồi"
    # A code fence is not a claim, and a snippet full of numbers must not read as proof.
    fenced_out = reading_stream("Prose here.\n\n```\nprice = 4500000\n```\n")
    assert not any("4500000" in piece for piece in fenced_out), fenced_out

    # --- structure ---
    skipped = read_page("# One\n\nProse here about it.\n\n#### Four\n\nMore prose here.\n", None, None)
    assert skipped["skipped_levels"] == [(1, 4)], skipped["skipped_levels"]
    two = read_page("# One\n\nProse.\n\n# Two\n\nProse.\n", None, None)
    assert not {row["gate"]: row for row in gates(two)}["single-h1"]["pass"]

    # Images: the gate is absent when the page has none, rather than passing on no evidence.
    assert "image-alt" not in {row["gate"] for row in gates(read_page("# T\n\nProse.\n", None, None))}
    with_images = read_page("# T\n\nProse.\n\n![](/a.jpg)\n\n![Bàn gỗ sồi](/b.jpg)\n", None, None)
    assert with_images["images_without_alt"] == 1, with_images
    assert not {row["gate"]: row for row in gates(with_images)}["image-alt"]["pass"]

    # A code fence must not contribute headings, or a snippet renames the page.
    fenced = read_page("# Real\n\nProse here.\n\n```\n# not a heading\n```\n", None, None)
    assert fenced["h1_count"] == 1, fenced["headings"]

    # Repetition is counted on the exact phrase, and an external link is not an internal one.
    stuffed = read_page("# Giá bàn gỗ\n\n" + "Giá bàn gỗ là tốt. " * 12
                        + "\n\n[Nguồn](https://example.com)\n", "giá bàn gỗ", None)
    assert stuffed["internal_links"] == 0
    assert not {row["gate"]: row for row in gates(stuffed)}["phrase-repetition"]["pass"], stuffed

    # And the same rate must not fire on a short page that used its query twice, correctly. This one
    # scores well over the per-300 ceiling on eleven words and is not stuffed.
    twice = read_page("# Giá bàn gỗ\n\nGiá bàn gỗ là 4.500.000 đồng.\n", "giá bàn gỗ", None)
    assert twice["phrase_per_300"] > PHRASE_PER_300_MAX, twice["phrase_per_300"]
    assert {row["gate"]: row for row in gates(twice)}["phrase-repetition"]["pass"], twice

    # Every run states what it cannot know. Silence there would read as a clean bill of health.
    assert len(unknowns(stats)) >= 4
    return "self-check passed\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--check", metavar="FILE", help="a draft to measure")
    source.add_argument("--text", help="measure this string instead of a file")
    source.add_argument("--list-intents", action="store_true", help="print the intent table")
    source.add_argument("--explain", metavar="INTENT", help="explain one intent")
    source.add_argument("--targets", action="store_true", help="print the thresholds and stop")
    source.add_argument("--self-check", action="store_true", help="run the built-in assertions")
    parser.add_argument("--query", help="the query the page is written for")
    parser.add_argument("--intent", help="intent id from --list-intents")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    parser.add_argument("--output", help="write the report here instead of stdout")
    args = parser.parse_args(argv)

    if args.self_check:
        emit(self_check(), args.output)
        return 0
    if args.targets:
        emit(print_targets(), args.output)
        return 0
    if args.list_intents:
        emit(list_intents(), args.output)
        return 0
    if args.explain:
        emit(explain(args.explain), args.output)
        return 0 if intent_row(args.explain) else 2
    if not (args.check or args.text):
        parser.error("give --check FILE, --text, --list-intents, --explain or --targets")

    text = args.text if args.text else Path(args.check).read_text(encoding="utf-8")
    stats = read_page(text, args.query, args.intent)
    rows = gates(stats)
    if args.json:
        emit_json({"stats": stats, "gates": rows, "unknown": unknowns(stats),
                   "blocking": blocking_count(rows)}, args.output)
    else:
        emit(report(stats, rows), args.output)
    return 2 if blocking_count(rows) else 0


if __name__ == "__main__":
    use_utf8_stdout()
    raise SystemExit(main())
