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

SENTENCE_END = re.compile(r"(?<=[.!?…])[\s]+|\n{2,}")
# Markdown furniture is not prose and would wreck every length measurement if counted as sentences.
STRIP_LINES = re.compile(r"^\s*(#{1,6}\s|\||[-*+]\s|\d+\.\s|>|```)")


def read_tells(language: str) -> list[dict[str, str]]:
    if not TELLS.exists():
        raise SystemExit(f"missing data table: {TELLS}")
    with TELLS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [row for row in rows if row["language"] in (language, "any")]


def prose_only(text: str) -> str:
    """Drop headings, tables, list markers and fences. What remains is what a reader reads as prose."""
    kept: list[str] = []
    fenced = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        kept.append("" if STRIP_LINES.match(line) else line)
    return "\n".join(kept)


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


def measure(text: str, language: str) -> dict:
    body = prose_only(text)
    sents = sentences(body)
    if len(sents) < 2:
        return {"language": language, "sentences": len(sents), "insufficient": True}

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
    }


def gates(stats: dict) -> list[dict]:
    if stats.get("insufficient"):
        return []
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
    return [{"gate": name, "pass": bool(passed), "severity": severity,
             "observed": observed, "target": want, "why": why}
            for name, passed, severity, observed, want, why in checks]


def find_tells(text: str, language: str) -> list[dict]:
    body = prose_only(text)
    found: list[dict] = []
    for row in read_tells(language):
        try:
            pattern = re.compile(row["detect_regex"], re.MULTILINE)
        except re.error as error:  # a broken row must be visible, not silently skipped
            found.append({"id": row["id"], "count": 0, "error": f"bad regex: {error}"})
            continue
        # Heading tells have to read the raw file: prose_only() strips the headings they look for.
        subject = text if row.get("scope") == "raw" else body
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


def report(stats: dict, gate_rows: list[dict], tells: list[dict]) -> str:
    lines = [f"# rewrite-human check — language {stats['language']}", ""]
    if stats.get("insufficient"):
        return "\n".join(lines + ["Fewer than two sentences of prose. Nothing measurable.", ""])

    lines += [f"{stats['sentences']} sentences, {stats['total_units']} {stats['unit']}.", "", "## Cadence gates", ""]
    lines += ["| Gate | Result | Observed | Target | Why |", "|---|---|---|---|---|"]
    for row in gate_rows:
        mark = "pass" if row["pass"] else f"FAIL ({row['severity']})"
        lines.append(f"| {row['gate']} | {mark} | {row['observed']} | {row['target']} | {row['why']} |")

    lines += ["", "## Translation and slop tells", ""]
    if not tells:
        lines.append("None of the tells in `data/translation-tells.csv` matched.")
    else:
        lines += ["| Tell | Severity | Hits | Found | Fix |", "|---|---|---|---|---|"]
        for row in tells:
            if "error" in row:
                lines.append(f"| {row['id']} | table error | - | {row['error']} | fix the CSV |")
                continue
            samples = "; ".join(sample.strip()[:40] for sample in row["samples"])
            lines.append(f"| {row['id']} | {row['severity']} | {row['count']} | {samples} | {row['fix']} |")

    blocking = [row["gate"] for row in gate_rows if not row["pass"] and row["severity"] in ("critical", "high")]
    blocking += [row["id"] for row in tells if row.get("severity") in ("critical", "high")]
    lines += ["", "## Verdict", "",
              "Blocking: " + (", ".join(blocking) if blocking else "none") + ".",
              "" if blocking else "Cadence and tell gates pass. Truth, claims and rights are checked elsewhere.", ""]
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
             f"| Paragraph length | <= {PARA_SENTENCES_MAX} sentences |", ""]
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

    return "self-check passed\n"


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", help="file to measure")
    parser.add_argument("--text", help="measure this string instead of a file")
    parser.add_argument("--lang", choices=("vi", "en", "auto"), default="auto")
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
    gate_rows = gates(stats)
    tells = find_tells(text, language)

    if args.json:
        emit_json({"stats": stats, "gates": gate_rows, "tells": tells,
                   "blocking": blocking_count(gate_rows, tells)}, args.output)
    else:
        emit(report(stats, gate_rows, tells), args.output)
    return 1 if blocking_count(gate_rows, tells) else 0


if __name__ == "__main__":
    raise SystemExit(main())
