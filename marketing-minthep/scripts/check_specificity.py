#!/usr/bin/env python3
"""Count the checkable things in a draft, and find the sentences a competitor could ship unchanged.

`rewrite_human.py` measures the shape of the prose and `check_address_register.py` measures who it
addresses. Both can pass on copy that says nothing. `Chúng tôi cam kết mang đến trải nghiệm tốt nhất
cho khách hàng` has good length variance, no pictograph, one register, and not one fact in it. That
is the commonest AI-written marketing sentence there is, and the two existing gates approve it.

`rewrite-human.md` already states the rule - a draft with fewer than three checkable facts has a
content problem that rhythm cannot fix - and until this script there was nothing that counted. A rule
with no instrument gets skipped, because counting facts by eye is exactly the kind of work a reader
does badly on their own draft.

So this counts four classes of token that a competitor cannot copy without lying: a number carrying a
unit or a currency, a date, a proper name, and a way to reach somebody. Then it reports the share of
sentences holding none of them. That share is the brand-swap test from `copywriting-deep.md` made
arithmetic: cover the brand name, and if a rival could ship the line unchanged, the line says nothing.

The gate that matters most is not the count, though. It is `empty-adjective`, and it is the reason
this script reads `translation-tells.csv` rather than carrying its own word list. That table already
knows which adjectives stand in for evidence. What it cannot know, matching one string at a time, is
whether a fact is standing next to the adjective. `Cà phê premium ủ 80 giờ` is a summary of a fact.
`Cà phê premium, chất lượng đảm bảo` is the fact's replacement. Same word, opposite defect, and only
a sentence-level reader can tell them apart.

    python scripts/check_specificity.py --check draft.md
    python scripts/check_specificity.py --text "Giao trong 2 giờ ở Gò Vấp, 45.000đ một ly."
    python scripts/check_specificity.py --check draft.md --json
    python scripts/check_specificity.py --targets
    python scripts/check_specificity.py --self-check

Exit codes are 0 clean, 1 usage error, 2 a gate failed, 3 computable but unsettled.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402
from rewrite_human import detect_language, prose_only, read_tells, sentences, units  # noqa: E402

# Below this the piece is a button, a headline or a badge, and copy that short can legitimately carry
# no fact - the fact is in the frame around it. House floor, matched to the address checker's, so the
# two scripts fall silent on the same fragments instead of disagreeing about what counts as copy.
SPECIFIC_FLOOR_UNITS = 40

# Three is the number `rewrite-human.md` step 1 already states, so the floor is not new policy - it
# is the existing rule given an instrument.
FACT_FLOOR = 3

# Per 150 units, matching every other density figure in this skill so the numbers stay comparable.
FACT_PER_150_MIN = 1.5
EMPTY_ADJECTIVE_PER_150_MAX = 1.0

# The share of sentences carrying nothing checkable. Set at half rather than at zero because
# connective and framing sentences are real work: a piece where every single sentence carries a
# number reads like a spec sheet, and that failure is caught separately below.
BRAND_SWAP_MAX = 0.5

# More than one hedge in a sentence is where a claim stops being falsifiable: `có thể giúp bạn tiết
# kiệm khá nhiều` has three and asserts nothing.
HEDGE_PER_SENTENCE_MAX = 1

# Above this, specifics per sentence, the input is a price list or a spec table rather than prose,
# and the brand-swap share stops meaning anything.
SPEC_SHEET_PER_SENTENCE = 3.0

FENCE = re.compile(r"^\s*```")
LINE_LEAD = re.compile(r"^(?:\s|[-*+>]\s*|\d+[.)]\s*|#{1,6}\s*|\|\s*)*")

# A closed list, and the honest consequence is that this undercounts. A number beside a unit nobody
# wrote down here is read as a loose number, so the gate errs toward reporting less specificity than
# the draft has - which is the safe direction for a gate whose failure blocks shipping.
UNITS_VI = (
    "đ|vnđ|vnd|đồng|k|tr|triệu|nghìn|ngàn|tỷ|%|"
    "giây|phút|giờ|ngày|tuần|tháng|năm|buổi|"
    "kg|g|gram|gam|mg|ml|l|lít|cc|"
    "mm|cm|dm|m|km|m2|m²|inch|"
    "độ|kcal|calo|w|kw|v|hz|mah|gb|mb|tb|px|dpi|"
    "người|khách|lần|cái|chiếc|suất|phần|ly|cốc|chai|lon|hộp|túi|gói|"
    "món|bàn|chỗ|đơn|combo|set|sao|tầng|phòng|chi nhánh|cửa hàng|điểm"
)
UNITS_EN = (
    # `percent` and `degrees` spelled out were missing while `%` and `deg` were present, and
    # Vietnamese already had `%` and `độ`. Found by running this gate on a parameter sheet full of
    # `12 degrees` and `30 percent` and getting zero facts back. A closed list undercounts by design;
    # undercounting the written-out form of a unit whose symbol is already listed is just a gap.
    "%|percent|percentage|usd|vnd|eur|"
    "sec|second|seconds|min|minute|minutes|hr|hrs|hour|hours|day|days|week|weeks|month|months|year|years|"
    "kg|g|gram|grams|mg|ml|l|litre|litres|liter|liters|oz|lb|lbs|"
    "mm|cm|m|km|in|ft|inch|inches|"
    "deg|degree|degrees|kcal|cal|w|kw|v|hz|mah|gb|mb|tb|px|dpi|"
    "people|person|customers|guests|seats|orders|times|units|items|servings|"
    "stars|floors|rooms|branches|stores|locations|points"
)
UNIT_WORD = re.compile(rf"(?i)^\s*({UNITS_VI}|{UNITS_EN})\b")

DIGITS = re.compile(r"\d[\d.,]*")
CURRENCY_BEFORE = re.compile(r"[$£€¥₫]\s?$")
CURRENCY_AFTER = re.compile(r"^\s?[$£€¥₫]")

DATE = re.compile(
    r"(?i)\b("
    r"\d{1,2}\s*[/-]\s*\d{1,2}(\s*[/-]\s*\d{2,4})?"          # 12/3, 12/03/2026
    r"|ngày\s+\d{1,2}(\s+tháng\s+\d{1,2})?"                     # ngày 12 tháng 3
    r"|tháng\s+\d{1,2}(\s*[/-]\s*\d{4})?"                       # tháng 3
    r"|quý\s+[1-4iv]+|q[1-4]\b"                                 # quý 3, Q3
    r"|(19|20)\d{2}"                                            # 2026
    r"|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}"
    r"|\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*"
    r"|(mon|tue|wed|thu|fri|sat|sun)[a-z]*day"
    r"|thứ\s+(hai|ba|tư|năm|sáu|bảy)|chủ\s+nhật"
    r")"
)

CONTACT = re.compile(
    r"(?i)("
    r"https?://\S+|www\.[\w.-]+\.\w{2,}"
    r"|[\w.+-]+@[\w-]+\.\w{2,}"
    r"|\b[\w-]{2,}\.(?:vn|com|net|org|shop|store|io|co|me)\b(?:/\S*)?"
    r"|(?<!\d)0\d{8,10}(?!\d)"                                  # a Vietnamese mobile or landline
    r"|(?<!\d)\+\d{1,3}[\d\s.-]{7,14}(?!\d)"
    r")"
)

# `I` is the one capitalised word in English that names nobody. Everything else that survives the
# sentence-initial filter is treated as a name, acronyms included: `TP.HCM` and `GHTK` are exactly
# the kind of thing a rival cannot copy.
NOT_A_NAME = {"I", "I'm", "I've", "I'll", "I'd"}
WORD = re.compile(r"[^\W\d_][\w.'’-]*", re.UNICODE)

# A Vietnamese heading written Như Thế Này produces four capitals and no name. Counting it as
# specificity would let title case buy a passing grade, so a line that is mostly capitalised
# contributes no names at all.
TITLECASE_MIN_WORDS = 4
TITLECASE_SHARE = 0.6

STATUS_EXIT = {"passed": 0, "failed": 2, "review": 3, "skipped": 3}


def _capitalised(word: str) -> bool:
    first = word[0]
    return unicodedata.category(first) == "Lu"


def title_cased(line: str) -> bool:
    """Is this line written In Title Case, rather than containing a name?"""
    words = [m.group(0) for m in WORD.finditer(line)]
    if len(words) < TITLECASE_MIN_WORDS:
        return False
    caps = sum(1 for w in words if _capitalised(w))
    return caps / len(words) >= TITLECASE_SHARE


def quantities(sentence: str) -> list[str]:
    """Numbers that carry a unit, a currency, or a percent - not every number in the string.

    A bare number is not a fact. `3 lý do`, `top 5`, `bước 2` are all structure, and a draft full of
    them is still empty. So the digit has to be attached to something measurable before it counts.
    """
    found = []
    for match in DIGITS.finditer(sentence):
        before = sentence[: match.start()]
        after = sentence[match.end():]
        if CURRENCY_BEFORE.search(before) or CURRENCY_AFTER.match(after):
            found.append(match.group(0))
        elif UNIT_WORD.match(after):
            found.append(match.group(0) + UNIT_WORD.match(after).group(1))
    return found


def names(sentence: str, line_is_title: bool) -> list[str]:
    """Runs of capitalised words that are not the start of the sentence.

    Stated limitation: a capital after a colon or an opening quote is a sentence start that this does
    not model, so `Giao hàng: Nội thành` reads the second half as a name. It usually is one. The
    error runs toward finding a name where the writer put a legitimate capital, which is why the
    title-case guard above exists - that is the case where the error would be systematic.
    """
    if line_is_title:
        return []
    found: list[str] = []
    run: list[str] = []
    run_started_at = -1
    for index, match in enumerate(WORD.finditer(sentence)):
        word = match.group(0)
        if _capitalised(word) and word not in NOT_A_NAME:
            if not run:
                run_started_at = index
            run.append(word)
            continue
        if run and run_started_at > 0:
            found.append(" ".join(run))
        run = []
    if run and run_started_at > 0:
        found.append(" ".join(run))
    return found


def specifics(sentence: str, line_is_title: bool = False) -> dict:
    """The checkable things in one sentence, by class."""
    found = {
        "quantity": quantities(sentence),
        "date": [m.group(0).strip() for m in DATE.finditer(sentence)],
        "name": names(sentence, line_is_title),
        "contact": [m.group(0) for m in CONTACT.finditer(sentence)],
    }
    found["total"] = sum(len(v) for v in found.values() if isinstance(v, list))
    return found


# --- the tell rows this script re-reads per sentence ---------------------------------------------

def phrase_rows(language: str, layer: str) -> list[dict[str, str]]:
    """Rows from `translation-tells.csv` for one layer, in this language plus the language-neutral.

    Reading the table instead of carrying a word list is the point. The table is where a new tell
    gets added, and it already records why each one survives translation and how to repair it. A
    second list here would drift from it within a month.
    """
    rows = []
    for row in read_tells(language):
        if row.get("layer") == layer and row.get("detect_regex"):
            rows.append(row)
    return rows


def phrase_hits(sentence: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    hits = []
    for row in rows:
        try:
            pattern = re.compile(row["detect_regex"])
        except re.error:
            continue
        match = pattern.search(sentence)
        if match:
            hits.append({"id": row["id"], "matched": match.group(0).strip(),
                         "fix": row.get("fix", ""), "severity": row.get("severity", "medium")})
    return hits


SOURCE_MARKER = re.compile(
    r"(?i)\b(theo|nguồn|số liệu|dữ liệu|thống kê|khảo sát|báo cáo|công bố|nghiên cứu"
    r"|according to|source|sourced|per |survey|report|study|data from|measured|audited)\b"
)

# Only two shapes of number are claims about the world: a percentage and a multiplier. A plain count
# is not one. `200 chai mỗi tuần` is the brand's own inventory and `45.000đ` is its own price - asking
# the writer to cite either would fail every honest draft, which is how a gate teaches people to
# switch it off. So this stays deliberately narrow: `87% khách quay lại` and `nhanh hơn 3 lần` assert
# something about people outside the building, and those are the two that need a source.
STATISTIC = re.compile(
    r"(?i)("
    r"\d[\d.,]*\s*%"
    r"|(?:gấp|hơn|bằng)\s*\d[\d.,]*\s*lần\b"
    r"|\b\d[\d.,]*\s*(?:x|times)\s+(?:nhanh|faster|more|higher|better|lower)"
    r")"
)

# A discount is the brand's own offer, not a finding. `giảm giá 20%` needs no citation.
OFFER_MARKER = re.compile(r"(?i)(sale|\boff\b|discount|khuyến mãi|ưu đãi|giảm giá|chiết khấu)")

# A percentage is only a claim about the world when it quantifies people or an outcome. `axit
# azelaic 10%` is a concentration and `cotton 95%` is a fabric - both are the product's own spec, and
# demanding a citation for either is the false positive that gets a gate switched off. So the default
# is exempt and the gate fires only when one of these appears in the same sentence.
CLAIM_CONTEXT = re.compile(
    r"(?i)\b("
    r"khách|khách hàng|người|doanh nghiệp|học viên|phụ huynh|bệnh nhân"
    r"|giảm|tăng|cải thiện|hiệu quả|tiết kiệm|tỷ lệ|chuyển đổi|hài lòng|quay lại|nhanh hơn|tốt hơn"
    r"|customers?|clients?|users?|people|respondents|shoppers?"
    r"|increase[sd]?|reduce[sd]?|improve[sd]?|faster|conversion|satisfaction|retention|growth|rate"
    r")\b"
)

# The multiplier shapes are inherently comparative - `gấp 3 lần`, `3x faster` - so they need no
# context test. Only the percentage does.
PERCENT = re.compile(r"\d[\d.,]*\s*%")


def needs_a_source(sentence: str, matched: str) -> bool:
    if OFFER_MARKER.search(sentence):
        return False
    if PERCENT.fullmatch(matched.strip()):
        return bool(CLAIM_CONTEXT.search(sentence))
    return True


def measure(text: str) -> dict:
    prose = prose_only(text)
    language = detect_language(prose)
    sents = sentences(prose)
    total_units = sum(units(s, language) for s in sents)

    rows_evidence = phrase_rows(language, "evidence")
    rows_hedge = phrase_rows(language, "hedge")

    per_sentence = []
    for sentence in sents:
        # A wrapped source line arrives with its newlines intact, and the report quotes these back
        # as the work list, so they are collapsed here rather than at print time.
        stripped = re.sub(r"\s+", " ", LINE_LEAD.sub("", sentence)).strip()
        in_title = title_cased(stripped)
        found = specifics(stripped, in_title)
        adjectives = phrase_hits(stripped, rows_evidence)
        hedges = phrase_hits(stripped, rows_hedge)
        unsourced = []
        if not SOURCE_MARKER.search(stripped):
            for match in STATISTIC.finditer(stripped):
                if needs_a_source(stripped, match.group(0)):
                    unsourced.append(match.group(0).strip())
        per_sentence.append({
            "sentence": stripped,
            "units": units(sentence, language),
            "specifics": found,
            "empty_adjectives": adjectives if found["total"] == 0 else [],
            "adjectives_beside_a_fact": adjectives if found["total"] else [],
            "hedges": hedges,
            "unsourced": unsourced,
            "title_case": in_title,
        })

    facts = sum(row["specifics"]["total"] for row in per_sentence)
    empty = [row for row in per_sentence if row["specifics"]["total"] == 0]
    return {
        "language": language,
        "sentences": len(sents),
        "total_units": total_units,
        "unit": "syllables" if language == "vi" else "words",
        "insufficient": total_units < SPECIFIC_FLOOR_UNITS,
        "facts": facts,
        "by_class": {name: sum(len(row["specifics"][name]) for row in per_sentence)
                     for name in ("quantity", "date", "name", "contact")},
        "empty_sentences": len(empty),
        "brand_swap_share": round(len(empty) / len(sents), 2) if sents else 0.0,
        "per_sentence": per_sentence,
    }


def _row(gate: str, status: str, observed: str, target: str, grade: str, why: str) -> dict:
    return {"gate": gate, "status": status, "observed": observed, "target": target,
            "evidence_grade": grade, "why": why}


def gates(stats: dict) -> list[dict]:
    if stats["insufficient"]:
        return [_row("fact-floor", "skipped",
                     f"{stats['total_units']} {stats['unit']}",
                     f">= {SPECIFIC_FLOOR_UNITS} {stats['unit']}", "house-rule",
                     "Shorter than a paragraph. A headline or a button carries its fact in the frame "
                     "around it, and demanding one inside the string would fail every good caption.")]

    per150 = (stats["total_units"] / 150) or 1
    rows = stats["per_sentence"]
    density = round(stats["facts"] / per150, 2)
    empty_adj = sum(len(r["empty_adjectives"]) for r in rows)
    adj_density = round(empty_adj / per150, 2)
    worst_hedge = max((len(r["hedges"]) for r in rows), default=0)
    unsourced = [n for r in rows for n in r["unsourced"]]
    per_sentence_specifics = stats["facts"] / max(1, stats["sentences"])

    out = [
        _row("fact-floor", "passed" if stats["facts"] >= FACT_FLOOR else "failed",
             f"{stats['facts']} checkable ({', '.join(f'{k} {v}' for k, v in stats['by_class'].items() if v) or 'none'})",
             f">= {FACT_FLOOR}", "house-rule",
             "The rule rewrite-human.md already states. Under three facts the draft has a content "
             "problem, and every rhythm edit from here makes it read better while still saying "
             "nothing - which is worse, because it removes the signal that it is empty."),
        _row("fact-density", "passed" if density >= FACT_PER_150_MIN else "failed",
             f"{density} per 150 {stats['unit']}", f">= {FACT_PER_150_MIN}", "house-rule",
             "Three facts in a headline is dense. Three facts in a thousand words is decoration "
             "around a claim nobody has to stand behind."),
    ]

    if per_sentence_specifics > SPEC_SHEET_PER_SENTENCE:
        out.append(_row("brand-swap", "review",
                        f"{per_sentence_specifics:.1f} specifics per sentence",
                        f"prose is below {SPEC_SHEET_PER_SENTENCE}", "house-rule",
                        "This is a price list or a spec table, not prose. The share of sentences "
                        "with no number is not a defect here, so the gate declines to rule rather "
                        "than passing a document it cannot read."))
    else:
        share = stats["brand_swap_share"]
        out.append(_row("brand-swap", "passed" if share <= BRAND_SWAP_MAX else "failed",
                        f"{int(share * 100)}% of sentences carry nothing checkable "
                        f"({stats['empty_sentences']} of {stats['sentences']})",
                        f"<= {int(BRAND_SWAP_MAX * 100)}%", "house-rule",
                        "Cover the brand name. A sentence with no number, no date, no place and no "
                        "name is one a competitor could publish unchanged, which means it is not "
                        "about this business at all."))

    review_adj = [h for r in rows for h in r["empty_adjectives"] if r["title_case"]]
    if empty_adj and len(review_adj) == empty_adj:
        out.append(_row("empty-adjective", "review",
                        f"{empty_adj} in title-cased lines "
                        f"({', '.join(h['matched'] for h in review_adj[:3])})",
                        f"<= {EMPTY_ADJECTIVE_PER_150_MAX} per 150", "house-rule",
                        "Every hit sits in a title-cased line, which is where a product name lives. "
                        "`Premium Roast` as a line on a menu is a name; `cà phê premium` in a "
                        "sentence is an adjective doing evidence's job. This script cannot tell "
                        "which, so it asks."))
    else:
        shown = ", ".join(h["matched"] for r in rows for h in r["empty_adjectives"][:1])[:70]
        out.append(_row("empty-adjective", "passed" if adj_density <= EMPTY_ADJECTIVE_PER_150_MAX else "failed",
                        f"{adj_density} per 150 ({empty_adj} with no fact in the sentence"
                        + (f": {shown}" if shown else "") + ")",
                        f"<= {EMPTY_ADJECTIVE_PER_150_MAX} per 150", "house-rule",
                        "An evidence adjective beside a fact is a summary of it and does no harm. "
                        "Alone in its sentence it is the fact's replacement, and that substitution "
                        "is what the reader learns to discount."))

    out.append(_row("hedge-stack", "passed" if worst_hedge <= HEDGE_PER_SENTENCE_MAX else "failed",
                    f"{worst_hedge} hedges in one sentence", f"<= {HEDGE_PER_SENTENCE_MAX}",
                    "house-rule",
                    "One hedge is honest. Two in a sentence makes the claim unfalsifiable, which is "
                    "how a draft avoids ever being wrong and also ever being believed."))
    out.append(_row("sourced-number", "passed" if not unsourced else "failed",
                    f"{len(unsourced)} statistic(s) with no source in the sentence"
                    + (f": {', '.join(unsourced[:3])}" if unsourced else ""),
                    "0", "house-rule",
                    "A percentage or a multiplier asserts something about people outside the "
                    "building. If the source cannot be named in the same clause, the number is "
                    "decoration - delete it or go and measure it. A price, a stock count and a "
                    "discount are exempt: those are the brand's own facts."))
    return out


def settle(gate_rows: list[dict]) -> str:
    statuses = [row["status"] for row in gate_rows]
    if "failed" in statuses:
        return "failed"
    if "review" in statuses:
        return "review"
    if all(status == "skipped" for status in statuses):
        return "skipped"
    return "passed"


def check(text: str) -> dict:
    stats = measure(text)
    gate_rows = gates(stats)
    return {"language": stats["language"], "sentences": stats["sentences"],
            "total_units": stats["total_units"], "unit": stats["unit"], "facts": stats["facts"],
            "by_class": stats["by_class"], "brand_swap_share": stats["brand_swap_share"],
            "gates": gate_rows, "verdict": settle(gate_rows),
            "empty_lines": [r["sentence"] for r in stats["per_sentence"]
                            if r["specifics"]["total"] == 0][:12]}


def as_text(report: dict) -> str:
    lines = [f"# specificity check - language {report['language']}, verdict {report['verdict']}", "",
             f"{report['sentences']} sentences, {report['total_units']} {report['unit']}, "
             f"{report['facts']} checkable things "
             f"({', '.join(f'{k} {v}' for k, v in report['by_class'].items() if v) or 'none'}).", "",
             "| Gate | Result | Observed | Target | Grade | Why |", "|---|---|---|---|---|---|"]
    for row in report["gates"]:
        lines.append(f"| {row['gate']} | {row['status']} | {row['observed']} | {row['target']} "
                     f"| {row['evidence_grade']} | {row['why']} |")
    if report["empty_lines"]:
        lines += ["", "## Sentences a competitor could ship unchanged", ""]
        lines += [f"- {line}" for line in report["empty_lines"]]
        lines += ["", "Give each one a number, a date, a place, or a name - or cut it."]
    return "\n".join(lines) + "\n"


def print_targets() -> str:
    return "\n".join([
        "# specificity targets", "",
        f"- floor: under {SPECIFIC_FLOOR_UNITS} units the check is skipped, not passed",
        f"- fact-floor: at least {FACT_FLOOR} checkable things in the draft",
        f"- fact-density: at least {FACT_PER_150_MIN} per 150 units",
        f"- brand-swap: at most {int(BRAND_SWAP_MAX * 100)}% of sentences carrying nothing checkable",
        f"- empty-adjective: at most {EMPTY_ADJECTIVE_PER_150_MAX} per 150, counting only the ones "
        "alone in their sentence",
        f"- hedge-stack: at most {HEDGE_PER_SENTENCE_MAX} hedge in any one sentence",
        "- sourced-number: no statistic without a source in the same sentence; prices exempt", "",
        "A checkable thing is a number carrying a unit or a currency, a date, a proper name, or a "
        "way to reach somebody. A bare number is not one: `3 lý do` and `bước 2` are structure.", "",
        "Every threshold here is a house rule. No standard governs how specific marketing copy has "
        "to be, so these are this skill's numbers and are open to argument - unlike the contrast "
        "ratios in colour-gates.csv, which are WCAG's.", "",
    ])


def self_check() -> str:
    out: list[str] = []

    # --- what counts as a fact ---
    assert quantities("Giao trong 2 giờ") == ["2giờ"], quantities("Giao trong 2 giờ")
    assert quantities("45.000đ một ly") == ["45.000đ"]
    assert quantities("Delivered in 2 hours") == ["2hours"]
    assert quantities("$12 flat") == ["12"]
    # A bare number is structure, not evidence. This is the distinction the whole gate rests on.
    assert quantities("3 lý do bạn nên chọn chúng tôi") == []
    assert quantities("Bước 2: đặt hàng") == []
    out.append("a number counts only with a unit or a currency beside it")

    assert names("Rang tại Gò Vấp mỗi sáng", False) == ["Gò Vấp"]
    assert names("Gò Vấp là nơi rang", False) == [], "a sentence-initial capital is not a name"
    assert names("I called them", False) == [], "English I names nobody"
    assert names("Giao qua GHTK trong ngày", False) == ["GHTK"], "an acronym is a name"
    # Title case would otherwise buy specificity for free.
    assert title_cased("Cà Phê Rang Mộc Nguyên Chất")
    assert not title_cased("Cà phê rang tại Gò Vấp")
    assert names("Cà Phê Rang Mộc Nguyên Chất", True) == []
    out.append("title case buys no specificity, and an acronym is a name")

    assert DATE.search("ngày 12 tháng 3") and DATE.search("Q3 2026") and DATE.search("12/03/2026")
    assert CONTACT.search("gọi 0901234567") and CONTACT.search("mua tại shop.vn/ca-phe")
    out.append("dates and contact details register")

    # --- the sentence that started this ---
    empty = "Chúng tôi cam kết mang đến trải nghiệm tốt nhất cho khách hàng. " \
            "Sản phẩm của chúng tôi luôn đảm bảo chất lượng và uy tín hàng đầu. " \
            "Đội ngũ chuyên nghiệp, tận tâm sẽ đồng hành cùng bạn trên mọi hành trình. " \
            "Hãy để chúng tôi chứng minh giá trị thực sự mà dịch vụ mang lại cho bạn."
    report = check(empty)
    named = {row["gate"]: row for row in report["gates"]}
    assert report["verdict"] == "failed", report["verdict"]
    assert named["fact-floor"]["status"] == "failed", named["fact-floor"]
    assert named["brand-swap"]["status"] == "failed", named["brand-swap"]
    assert named["empty-adjective"]["status"] == "failed", named["empty-adjective"]
    assert report["facts"] == 0, report["by_class"]
    out.append("the flattest Vietnamese draft there is fails on facts, brand-swap and adjectives")

    # --- the same claims, made checkable ---
    real = "Cà phê rang tại xưởng ở Gò Vấp, mỗi sáng thứ hai và thứ năm. " \
           "Một ly 45.000đ, giao trong 2 giờ nội thành. " \
           "Ngày rang in dưới đáy túi, nên bạn biết túi đang uống rang hôm nào. " \
           "Gọi 0901234567 nếu túi tới muộn hơn 2 giờ, chúng tôi giao lại miễn phí."
    report = check(real)
    named = {row["gate"]: row for row in report["gates"]}
    for gate, row in named.items():
        assert row["status"] == "passed", f"{gate} -> {row['status']}: {row['observed']}"
    assert report["verdict"] == "passed"
    out.append("the same offer written with facts passes every gate")

    # --- the adjective beside a fact is not the defect ---
    substitute = check("Cà phê của chúng tôi là loại premium, chất lượng đảm bảo và rất uy tín. "
                       "Chúng tôi tin rằng bạn sẽ hài lòng với dịch vụ tận tâm này. "
                       "Sản phẩm luôn đạt tiêu chuẩn cao nhất trên thị trường hiện nay. "
                       "Hãy trải nghiệm sự khác biệt mà thương hiệu mang lại cho bạn.")
    beside = check("Cà phê premium này ủ lạnh 80 giờ ở Gò Vấp trước khi vào chai. "
                   "Một chai 250ml giá 65.000đ, đủ cho hai người uống sáng. "
                   "Mẻ đầu ra lò ngày 12 tháng 3, mỗi tuần chỉ 200 chai. "
                   "Đặt qua 0901234567 trước thứ năm nếu muốn nhận cuối tuần.")
    assert {r["gate"]: r["status"] for r in substitute["gates"]}["empty-adjective"] == "failed"
    assert {r["gate"]: r["status"] for r in beside["gates"]}["empty-adjective"] == "passed", \
        [r for r in beside["gates"] if r["gate"] == "empty-adjective"]
    out.append("premium beside 80 giờ passes; premium alone in its sentence fails")

    # --- hedges ---
    hedged = check("Dịch vụ có thể giúp bạn tiết kiệm khá nhiều thời gian mỗi tuần. "
                   "Nhìn chung thì phần lớn khách hàng đều tương đối hài lòng với kết quả. "
                   "Rang tại Gò Vấp mỗi sáng thứ hai, giao trong 2 giờ nội thành. "
                   "Một ly 45.000đ, gọi 0901234567 để đặt trước thứ năm hàng tuần.")
    assert {r["gate"]: r["status"] for r in hedged["gates"]}["hedge-stack"] == "failed", \
        [r for r in hedged["gates"] if r["gate"] == "hedge-stack"]
    out.append("two hedges in one sentence fail even when the draft is otherwise specific")

    # --- an unsourced statistic, and the price that is not one ---
    stat = check("Có tới 87% khách hàng quay lại trong vòng một tháng sau lần mua đầu. "
                 "Cà phê rang tại Gò Vấp mỗi sáng thứ hai, giao trong 2 giờ nội thành. "
                 "Một ly 45.000đ, ngày rang in dưới đáy túi cho bạn tự kiểm tra. "
                 "Gọi 0901234567 trước thứ năm nếu muốn nhận vào cuối tuần này.")
    assert {r["gate"]: r["status"] for r in stat["gates"]}["sourced-number"] == "failed"
    sourced = check("Theo khảo sát 320 đơn tháng 3 của xưởng, 87% khách quay lại trong một tháng. "
                    "Cà phê rang tại Gò Vấp mỗi sáng thứ hai, giao trong 2 giờ nội thành. "
                    "Một ly 45.000đ, ngày rang in dưới đáy túi cho bạn tự kiểm tra. "
                    "Gọi 0901234567 trước thứ năm nếu muốn nhận vào cuối tuần này.")
    assert {r["gate"]: r["status"] for r in sourced["gates"]}["sourced-number"] == "passed", \
        [r for r in sourced["gates"] if r["gate"] == "sourced-number"]
    # The three shapes that must stay exempt, or the gate becomes something people switch off: a
    # price, a plain count of the brand's own stock, and a discount.
    own = check("Một ly 45.000đ, một túi 250g là 180.000đ tại xưởng Gò Vấp. "
                "Mỗi tuần chỉ 200 chai, rang thứ hai và thứ năm, giao trong 2 giờ. "
                "Đang giảm giá 20% cho đơn đầu tiên, tới hết ngày 12 tháng 3. "
                "Gọi 0901234567 nếu túi tới muộn, chúng tôi giao lại miễn phí.")
    assert {r["gate"]: r["status"] for r in own["gates"]}["sourced-number"] == "passed", \
        [r for r in own["gates"] if r["gate"] == "sourced-number"]
    assert not STATISTIC.search("mỗi tuần chỉ 200 chai"), "a plain count is not a statistic"
    assert not STATISTIC.search("một túi 250g là 180.000đ"), "a price is not a statistic"
    assert not STATISTIC.search("gọi 0901234567"), "a phone number is not a statistic"
    assert STATISTIC.search("nhanh hơn 3 lần") and STATISTIC.search("87% khách")
    # A concentration is the product's own spec, not a finding about anybody.
    spec = check("Dùng axit azelaic 10% của Paula's Choice, cùng loại bạn mua ngoài tiệm được. "
                 "Một buổi 450.000đ, 75 phút, ở tiệm trên đường Nguyễn Trãi quận 5. "
                 "Chị Hạnh làm ở đây 9 năm, trước đó 4 năm ở một tiệm trong Gò Vấp. "
                 "Gọi 0901234567 trước 17 giờ nếu bạn muốn giữ chỗ trưa mai.")
    assert {r["gate"]: r["status"] for r in spec["gates"]}["sourced-number"] == "passed", \
        [r for r in spec["gates"] if r["gate"] == "sourced-number"]
    assert not needs_a_source("Dùng axit azelaic 10% trên da", "10%")
    assert needs_a_source("Hiệu quả lên tới 90% sau một liệu trình", "90%")
    out.append("87% khách needs a source; azelaic 10%, a price and a discount do not")

    # --- English behaves the same way ---
    english = check("We are committed to delivering the best possible experience to our customers. "
                    "Our products are always of premium quality and reliable standard. "
                    "Our dedicated team will accompany you on every step of the journey. "
                    "Let us prove the real value that our service brings to you.")
    assert english["language"] == "en", english["language"]
    assert english["verdict"] == "failed" and english["facts"] == 0
    out.append("the English version of the same emptiness fails identically")

    # --- the floor and the spec sheet, the two things it declines to judge ---
    caption = check("Rang mộc, giao nhanh.")
    assert caption["verdict"] == "skipped"
    assert caption["gates"][0]["status"] == "skipped", "a caption is skipped, never passed"
    sheet = check("Ly nhỏ 35.000đ, ly lớn 45.000đ, túi 250g 180.000đ tại Gò Vấp. "
                  "Giao 2 giờ nội thành, 24 giờ đi Đà Nẵng, 48 giờ ra Hà Nội. "
                  "Rang thứ hai và thứ năm, mỗi mẻ 40kg, đóng túi 250g và 1kg. "
                  "Gọi 0901234567 hoặc 0987654321, mở 7 giờ tới 21 giờ mỗi ngày.")
    assert {r["gate"]: r["status"] for r in sheet["gates"]}["brand-swap"] == "review", \
        [r for r in sheet["gates"] if r["gate"] == "brand-swap"]
    assert sheet["verdict"] == "review", "a price list is not prose and is not judged as prose"
    out.append("a caption is skipped and a price list is reviewed, neither is failed")

    # --- the table is the source of truth, not a list in here ---
    assert phrase_rows("vi", "hedge"), "no hedge rows in translation-tells.csv"
    assert phrase_rows("vi", "evidence"), "no evidence rows in translation-tells.csv"
    assert phrase_rows("en", "hedge"), "no English hedge rows in translation-tells.csv"
    out.append("the adjective and hedge lists are read from translation-tells.csv, not hardcoded")

    return "specificity self-check passed:\n" + "\n".join(f"  - {line}" for line in out) + "\n"


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(
        description="Count the checkable things in a draft and find the sentences any competitor "
                    "could ship unchanged.")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--check", metavar="FILE", help="a draft to read")
    source.add_argument("--text", help="copy passed directly")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    parser.add_argument("--targets", action="store_true", help="print the thresholds and stop")
    parser.add_argument("--self-check", action="store_true", help="run the built-in assertions")
    parser.add_argument("--out", metavar="FILE", help="write the report here instead of stdout")
    args = parser.parse_args(argv)

    if args.self_check:
        emit(self_check(), args.out)
        return 0
    if args.targets:
        emit(print_targets(), args.out)
        return 0

    if args.check:
        path = Path(args.check)
        if not path.exists():
            emit(f"no such file: {path}\n")
            return 1
        text = path.read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        parser.print_help()
        return 1

    report = check(text)
    emit_json(report, args.out) if args.json else emit(as_text(report), args.out)
    return STATUS_EXIT[report["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
