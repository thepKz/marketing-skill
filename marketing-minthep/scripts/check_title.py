#!/usr/bin/env python3
"""Measure a title, and measure a page of titles against each other.

This is the gate for the one length band the other three copy gates exclude on purpose, and the
exclusions are written into their own constants. `rewrite_human.py` sets `SHORT_FORM_UNITS = 120`
and stops measuring cadence below two sentences. `check_specificity.py` sets
`SPECIFIC_FLOOR_UNITS = 40` with the comment that below it "the piece is a button, a headline or a
badge". `check_address_register.py` matches that floor so the two do not disagree. Every one of
those decisions is right for the reason given. Together they mean nothing in this skill has ever
looked at a headline.

Measured on this repository on 2026-08-05, before this script existed. Three titles from its own
landing page, through all three gates:

    Lấy cấu trúc. Không sao chép dấu vân tay.        rewrite_human FAIL, specificity exit 3, register pass
    Khám phá bí mật đằng sau thành công: 5 điều...   all three pass, exit 0
    Không chỉ là một tô bún, mà còn là cả câu chuyện exit 1 and the printed report named no reason

The middle line is the finding. It is a curiosity gap, an imperative to a stranger, a colon deck and
a listicle number in twelve words, and every existing gate cleared it silently. The first line shows
the other failure mode: the cadence gate does fire, but on burstiness and long-short ratio - the
rhythm of a paragraph, measured across two fragments that were never a paragraph. It answers a
question a title did not ask and stays blind to the one it did. The third line was a bug in
`rewrite_human.report`, fixed the same day.

So what does a title actually fail at? Three things, and only the third is about wording.

It is about the maker. The subject is the artefact or the process - brief, output, hệ thống, cơ chế -
because the title is written last, by whoever just built the thing, and the freshest noun in their
head comes from the workshop. The reader has never been in the workshop.

It reuses one device. This is the measurement that matters most and the reason this script reads a
set rather than a string. No single title is wrong for being `A, không phải B`. A page where five of
thirteen are is one voice with one trick, and repetition is what a reader registers as machine-
written - not any individual sentence, which is precisely why rereading your own titles one at a time
cannot find it. `data/title-devices.csv` therefore carries a `budget_per_set` rather than a verdict.

It carries no noun the reader owns. This one is not computable here and the script says so instead
of pretending. Two judgements are printed as open at the end of every clean run: whether the title
names something the reader has, wants or is losing, and whether any metaphor in it was earned. Exit
3 means everything measurable passed and those two are still somebody's job.

    python scripts/check_title.py --title "Nồi nước dùng bắt đầu từ bốn giờ sáng"
    python scripts/check_title.py --title "..." --title "..." --title "..."
    python scripts/check_title.py --set titles.txt --lang vi
    python scripts/check_title.py --page docs/index.html
    python scripts/check_title.py --page docs/index.html --json
    python scripts/check_title.py --devices
    python scripts/check_title.py --self-check

Exit codes are 0 clean and judged, 1 usage error, 2 a blocking device or a device over its set
budget, 3 measurable gates pass and the two human judgements are still open.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402
from rewrite_human import detect_language  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DEVICES = ROOT / "data" / "title-devices.csv"

# `copy-formulas.csv` one-idea-headline already states the rule: "under nine words". This script does
# not get to invent a second rule, only to express the same one in the unit it actually counts. Nine
# English words is nine tokens; nine Vietnamese words is about twelve, because this script counts
# whitespace tokens and Vietnamese writes its words as separate syllables. Applying nine to both would
# hold Vietnamese to two thirds of the length the formula grants, which is not the formula being
# stricter - it is the formula being mismeasured.
TITLE_WORDS_MAX = {"vi": 12, "en": 9}
# Past this it is a sentence that has been placed where a title goes, and the failure changes from
# medium to high. Same ratio, from the same reasoning.
TITLE_WORDS_HARD = {"vi": 18, "en": 14}

# A sentence short enough to be a fragment, two of them side by side, is the clipped-parallel shape.
# The threshold differs by language and the reason is arithmetic rather than taste: this script counts
# whitespace tokens, and a Vietnamese token is a syllable where an English one is a word. `Không sao
# chép dấu vân tay` is six tokens and three words. A flat five caught the English case and missed the
# Vietnamese case the row was written for, which is how this number came to be measured rather than
# guessed - seven is where the two languages are carrying the same amount of content.
CLIPPED_SENTENCE_WORDS = {"vi": 7, "en": 5}
CLIPPED_MIN_SENTENCES = 2

# Below three titles there is no set, and a concentration figure over two items is noise. Say so
# rather than printing a ratio with a denominator of two.
SET_MIN = 3

# House figures, and there is no external standard for either. What is defensible is the shape:
# a device becomes a voice by repetition, and the third occurrence is where a reader stops reading
# the sentence and starts reading the pattern. At a quarter, a set of twelve titles may share a
# device three times. Anything tighter would forbid a deliberate anaphora across a page, which is a
# real technique somebody chooses on purpose.
CONCENTRATION_MAX = 0.25
# And half the titles in a set must use no listed device at all. Without this floor a page can pass
# concentration by spreading six different devices across six titles, which reads worse than five of
# one - it reads as a tour of every trick available.
DEVICE_FREE_MIN = 0.5

BLOCKING = ("critical", "high")

WORD_SPLIT = re.compile(r"[\s ]+")
SENTENCE_SPLIT = re.compile(r"[.!?…]+")
TAG = re.compile(r"<[^>]+>")
HEADING = re.compile(r"<h([1-3])\b[^>]*>(.*?)</h\1>", re.S | re.I)
ENTITY = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&nbsp;": " ",
          "&rarr;": "→", "&mdash;": "—", "&ldquo;": "“", "&rdquo;": "”"}

# The two things this script refuses to compute, printed on every clean run so that a passing exit
# code never reads as a finished title. Both need somebody who knows the buyer.
JUDGEMENTS = (
    ("names-a-noun-the-reader-owns",
     "Does the title name something the reader has, wants, sells or is losing? A title whose only "
     "nouns belong to you is about you. No word list can settle this, because the same noun is the "
     "reader's in one market and the workshop's in another."),
    ("the-metaphor-was-earned",
     "If the title is figurative - dấu vân tay, hành trình, DNA - has the page introduced that image "
     "anywhere else? A title has no next paragraph in which to repay it."),
)


def read_devices() -> list[dict[str, str]]:
    with DEVICES.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["budget_per_set"] = int(row["budget_per_set"])
    return rows


def words(title: str) -> list[str]:
    """Whitespace tokens. In Vietnamese that is syllables, which is the unit every other script in
    this skill counts, so the numbers stay comparable across gates."""
    return [token for token in WORD_SPLIT.split(title.strip()) if token]


def clauses(title: str) -> list[str]:
    return [part.strip() for part in SENTENCE_SPLIT.split(title) if part.strip()]


def structural_hit(device_id: str, title: str, language: str = "vi") -> str:
    """Return a sample string when the structural device is present, otherwise an empty string.

    Kept separate from the regex path because these two are shapes, not strings, and writing them as
    regexes is how a table acquires a pattern nobody can read or fix."""
    if device_id == "clipped-parallel":
        limit = CLIPPED_SENTENCE_WORDS.get(language, CLIPPED_SENTENCE_WORDS["en"])
        parts = clauses(title)
        short = [part for part in parts if len(words(part)) <= limit]
        if len(parts) >= CLIPPED_MIN_SENTENCES and len(short) >= CLIPPED_MIN_SENTENCES:
            return " / ".join(short[:3])
        return ""
    if device_id == "tricolon":
        items = [part.strip() for part in title.split(",") if part.strip()]
        return ", ".join(items[:3]) if len(items) >= 3 else ""
    raise KeyError(f"no structural detector for {device_id}")


def _window(title: str, match: re.Match, pad: int = 14) -> str:
    """The match with enough of its neighbours to be findable by eye."""
    start, end = max(0, match.start() - pad), min(len(title), match.end() + pad)
    text = ("…" if start else "") + title[start:end].strip() + ("…" if end < len(title) else "")
    return text.replace("|", "\\|")


def devices_in(title: str, language: str, devices: list[dict]) -> list[dict]:
    """Every device the title triggers, with the fragment that triggered it."""
    found = []
    for row in devices:
        if row["language"] not in ("both", language):
            continue
        if row["only_when"] == "no-digit" and re.search(r"\d", title):
            continue
        sample = ""
        if row["detect"] == "regex":
            match = re.search(row["pattern"], title)
            # The match alone is unreadable for the punctuation devices - colon-deck printed `: b` in
            # the first real run, which tells a writer nothing about where to look. Show the match
            # inside its neighbourhood instead.
            sample = _window(title, match) if match else ""
        elif row["detect"] == "structural":
            sample = structural_hit(row["id"], title, language)
        elif row["detect"] == "manual":
            continue
        if sample:
            found.append({"id": row["id"], "severity": row["severity"], "detect": row["detect"],
                          "budget_per_set": row["budget_per_set"], "sample": sample,
                          "device_en": row["device_en"], "fix": row["fix"]})
    return found


def measure_title(title: str, language: str, devices: list[dict]) -> dict:
    counted = words(title)
    return {
        "title": title,
        "language": language,
        "words": len(counted),
        "clauses": len(clauses(title)),
        "devices": devices_in(title, language, devices),
    }


def title_gates(reading: dict) -> list[dict]:
    """Per-title gates. Length first, because a title over the limit is a different artefact."""
    language = reading["language"]
    soft = TITLE_WORDS_MAX.get(language, TITLE_WORDS_MAX["en"])
    hard = TITLE_WORDS_HARD.get(language, TITLE_WORDS_HARD["en"])
    unit = "syllables" if language == "vi" else "words"
    rows = [{
        "gate": "one-idea-length",
        "pass": reading["words"] <= soft,
        "severity": "medium" if reading["words"] <= hard else "high",
        "observed": f"{reading['words']} {unit}",
        "target": f"<= {soft}",
        "why": "copy-formulas.csv one-idea-headline. Past this the title is carrying a second idea, "
               f"and past {hard} it is a sentence standing where a title goes.",
    }]
    for hit in reading["devices"]:
        # A device with a budget above zero cannot fail here, and getting this wrong is how a gate
        # loses its reader. `Mẫu brief.` blocked on workshop-noun in the first real run - one hit,
        # against a budget of one, reported as a failure. If the table grants a device one use per
        # set, then the only place that grant can be checked is the set. Per-title, these are printed
        # as budgeted so the writer can see the device without being told to remove it.
        budgeted = hit["budget_per_set"] >= 1
        rows.append({
            "gate": hit["id"],
            "pass": budgeted or hit["severity"] not in BLOCKING,
            "severity": "budgeted" if budgeted else hit["severity"],
            "observed": hit["sample"],
            "target": "absent" if hit["budget_per_set"] == 0 else f"<= {hit['budget_per_set']} per set",
            "why": hit["fix"],
        })
    return rows


def set_gates(readings: list[dict], devices: list[dict]) -> list[dict]:
    """The gates that only exist across a set. This is the half a writer cannot run by eye."""
    total = len(readings)
    if total < SET_MIN:
        return [{
            "gate": "set-size",
            "pass": True,
            "severity": "info",
            "observed": f"{total} title{'s' if total != 1 else ''}",
            "target": f">= {SET_MIN} for the repetition gates",
            "why": "Repetition is a property of a set. Under three titles there is nothing to "
                   "measure, and a concentration ratio over two items would be theatre.",
        }]

    counts: dict[str, int] = {}
    for reading in readings:
        for hit in reading["devices"]:
            counts[hit["id"]] = counts.get(hit["id"], 0) + 1
    budgets = {row["id"]: row["budget_per_set"] for row in devices}
    severities = {row["id"]: row["severity"] for row in devices}

    rows = []
    for device_id, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        budget = budgets[device_id]
        if count <= budget:
            continue
        rows.append({
            "gate": f"budget:{device_id}",
            "pass": False,
            "severity": severities[device_id],
            "observed": f"{count} of {total} titles",
            "target": f"<= {budget} per set",
            "why": "Over budget. The device is no longer a choice in this set; it is the voice.",
        })

    top = max(counts.values()) if counts else 0
    concentration = top / total
    leader = sorted(item for item, value in counts.items() if value == top)[0] if counts else "none"
    rows.append({
        "gate": "device-concentration",
        "pass": concentration <= CONCENTRATION_MAX,
        "severity": "high",
        "observed": f"{concentration:.2f} ({top}/{total}, {leader})",
        "target": f"<= {CONCENTRATION_MAX}",
        "why": "The share of titles leaning on the single most-used device. A device becomes a voice "
               "by repetition, and no reader can hear that one title at a time.",
    })

    clean = sum(1 for reading in readings if not reading["devices"])
    share = clean / total
    rows.append({
        "gate": "device-free-share",
        "pass": share >= DEVICE_FREE_MIN,
        "severity": "high",
        "observed": f"{share:.2f} ({clean}/{total})",
        "target": f">= {DEVICE_FREE_MIN}",
        "why": "Half the set must say its thing with no device at all. Otherwise a page passes "
               "concentration by using six different tricks once each, which reads as a tour of "
               "every trick available.",
    })
    return rows


def blocking(rows: list[dict]) -> list[str]:
    return [row["gate"] for row in rows if not row["pass"] and row["severity"] in BLOCKING]


def headings(html: str) -> list[str]:
    """Every h1, h2 and h3 on a page, in reading order. That is the set a visitor scans, and it is
    the set the repetition gates are about."""
    out = []
    for _, inner in HEADING.findall(html):
        text = TAG.sub(" ", inner)
        for entity, char in ENTITY.items():
            text = text.replace(entity, char)
        text = re.sub(r"&#\d+;", " ", text)
        text = " ".join(text.split())
        if text:
            out.append(text)
    return out


def _table(rows: list[dict]) -> list[str]:
    lines = ["| Gate | Result | Observed | Target | Why |", "|---|---|---|---|---|"]
    for row in rows:
        verdict = "pass" if row["pass"] else f"FAIL ({row['severity']})"
        lines.append(f"| {row['gate']} | {verdict} | {row['observed']} | {row['target']} | {row['why']} |")
    return lines


def report(readings: list[dict], per_title: list[list[dict]], across: list[dict]) -> str:
    lines = [f"# title check — {len(readings)} title(s), language "
             f"{', '.join(sorted({r['language'] for r in readings}))}", ""]

    lines += ["## Each title", ""]
    for reading, rows in zip(readings, per_title):
        failed = blocking(rows)
        state = "blocked on " + ", ".join(failed) if failed else "no blocking device"
        lines += [f"### {reading['title']}", "",
                  f"{reading['words']} words, {reading['clauses']} clause(s), {state}.", ""]
        lines += _table(rows) + [""]

    lines += ["## Across the set", ""] + _table(across) + [""]

    lines += ["## Left to a person", ""]
    for name, question in JUDGEMENTS:
        lines += [f"- **{name}** — {question}"]
    lines += [""]

    failed = blocking([row for rows in per_title for row in rows]) + blocking(across)
    lines += ["## Verdict", ""]
    if failed:
        lines += ["Blocking: " + ", ".join(dict.fromkeys(failed)) + ".", ""]
    else:
        lines += ["Every measurable gate passes. The two judgements above are open, so this exits 3 "
                  "rather than 0 - a title is not finished until somebody who knows the buyer has "
                  "read it.", ""]
    return "\n".join(lines)


def device_table() -> str:
    rows = read_devices()
    lines = ["# Title devices", "",
             f"{len(rows)} devices from `data/title-devices.csv`. `budget_per_set` is how many times "
             "the device may appear across one set of titles; 0 means never.", "",
             "| id | Language | Device | Detect | Budget | Severity |", "|---|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['id']} | {row['language']} | {row['device_en']} | {row['detect']} | "
                     f"{row['budget_per_set']} | {row['severity']} |")
    lines += ["", "Two devices are checked by a person rather than by this script: "
              "`metaphor-unearned`, which needs the rest of the page, and `khong-chi-ma-con`, which "
              "already lives in `data/translation-tells.csv` and fires through `rewrite_human.py`. "
              "Duplicating it here would give one defect two owners.", ""]
    return "\n".join(lines)


def self_check() -> str:
    """Verify the detectors against inputs whose answers are known by construction."""
    devices = read_devices()
    ids = {row["id"] for row in devices}
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))

    check("table loads", len(devices) > 0, f"{len(devices)} devices")
    check("every pattern compiles", all(
        _compiles(row) for row in devices), "regex rows only")
    check("every structural id has a detector", all(
        _has_detector(row["id"]) for row in devices if row["detect"] == "structural"))

    # The three landing-page titles that started this. Each must name the device it is an example of.
    cases = [
        ("Lấy cấu trúc. Không sao chép dấu vân tay.", "vi",
         {"contrastive-negation", "clipped-parallel"}),
        ("Makeup đổi bề mặt. Không đổi con người.", "vi",
         {"contrastive-negation", "clipped-parallel"}),
        ("Một brief rời rạc đi vào. Một hệ thống có thể vận hành đi ra.", "vi",
         {"workshop-noun", "symmetry-in-out"}),
        ("Khám phá bí mật đằng sau thành công: 5 điều bạn cần biết ngay", "vi",
         {"curiosity-gap-vi", "imperative-discovery-vi", "colon-deck"}),
        ("Unlocking the full potential of your brand", "en", {"gerund-elevation-en"}),
        ("Việc tối ưu hoá quy trình sản xuất nội dung", "vi",
         {"nominalised-opener-vi", "workshop-noun"}),
        ("Dịch vụ giao hàng nhanh nhất khu vực", "vi", {"superlative-unnumbered"}),
        ("Nồi nước dùng bắt đầu từ bốn giờ sáng", "vi", set()),
        ("Bún bò nấu từ xương, bán tới khi hết nồi", "vi", set()),
    ]
    for title, language, expected in cases:
        hit = {item["id"] for item in devices_in(title, language, devices)}
        missing = expected - hit
        check(f"detects in {title[:34]!r}", not missing, f"missing {sorted(missing)}" if missing else
              f"found {sorted(hit)}")

    # A clean title must trigger nothing at all, or the gate is noise and gets switched off.
    for title, language in (("Nồi nước dùng bắt đầu từ bốn giờ sáng", "vi"),
                            ("The pot starts at four in the morning", "en")):
        hit = {item["id"] for item in devices_in(title, language, devices)}
        check(f"clean title is silent {title[:28]!r}", not hit, f"fired {sorted(hit)}")

    # superlative-unnumbered must stay quiet once a figure is present, which is the whole point of
    # only_when. A superlative beside a measurement is a summary of the measurement.
    with_number = devices_in("Giao nhanh nhất trong 20 phút", "vi", devices)
    check("only_when=no-digit suppresses the superlative",
          "superlative-unnumbered" not in {item["id"] for item in with_number})
    without = devices_in("Dịch vụ giao hàng nhanh nhất", "vi", devices)
    check("and fires without one",
          "superlative-unnumbered" in {item["id"] for item in without})

    # The set gates. Four titles all using one device must fail both, and the arithmetic is checkable
    # by hand: concentration 4/4 = 1.00, device-free 0/4 = 0.00.
    same = [measure_title(t, "vi", devices) for t in (
        "Lấy cấu trúc. Không sao chép dấu vân tay.",
        "Makeup đổi bề mặt. Không đổi con người.",
        "Đo ảnh trước. Không đoán màu sau.",
        "Bán tới khi hết nồi, không hết giờ.")]
    rows = set_gates(same, devices)
    named = {row["gate"]: row for row in rows}
    check("four of one device fails concentration",
          named["device-concentration"]["pass"] is False,
          named["device-concentration"]["observed"])
    check("and fails the device-free floor",
          named["device-free-share"]["pass"] is False,
          named["device-free-share"]["observed"])
    check("and names the budget it broke",
          "budget:contrastive-negation" in named)

    # A set of clean titles must pass every set gate, or the gate can never be satisfied.
    clean = [measure_title(t, "vi", devices) for t in (
        "Nồi nước dùng bắt đầu từ bốn giờ sáng",
        "Bốn món trên bảng, không có món phụ",
        "Rau lấy ở chợ Bà Chiểu mỗi sáng",
        "Quán mở từ sáu giờ tới mười một giờ")]
    rows = set_gates(clean, devices)
    failed = blocking(rows)
    check("a clean set passes every set gate", not failed, f"failed {failed}")

    # Under three titles the repetition gates must say so rather than divide by two.
    rows = set_gates(clean[:2], devices)
    check("under three titles the set gates stand down",
          len(rows) == 1 and rows[0]["gate"] == "set-size", rows[0]["gate"])

    # Length reads from the shared constant rather than a second copy of the same rule, and it reads
    # the per-language one. A flat threshold would fail every honest Vietnamese title of nine words.
    for language, limit in TITLE_WORDS_HARD.items():
        gate = title_gates(measure_title(" ".join(["từ"] * (limit + 1)), language, devices))[0]
        check(f"a long {language} title fails length at high severity",
              not gate["pass"] and gate["severity"] == "high", gate["observed"])
        gate = title_gates(measure_title(" ".join(["từ"] * TITLE_WORDS_MAX[language]),
                                         language, devices))[0]
        check(f"and a {language} title at the limit passes", gate["pass"], gate["observed"])

    # Heading extraction, including an entity and a nested tag, because both are in the real page.
    got = headings("<h1>A &amp; <em>B</em></h1><h2 class='x'>C</h2><h4>skip</h4>")
    check("headings strip tags and entities", got == ["A & B", "C"], str(got))

    check("every id is unique", len(ids) == len(devices))

    failures = [name for name, ok, _ in checks if not ok]
    lines = ["# check_title self-check", ""]
    for name, ok, detail in checks:
        lines.append(f"- {'ok' if ok else 'FAIL'} — {name}{(': ' + detail) if detail else ''}")
    lines += ["", f"{len(checks)} checks, {len(failures)} failed.", ""]
    return "\n".join(lines)


def _compiles(row: dict) -> bool:
    if row["detect"] != "regex":
        return True
    try:
        re.compile(row["pattern"])
    except re.error:
        return False
    return True


def _has_detector(device_id: str) -> bool:
    try:
        structural_hit(device_id, "a, b, c")
    except KeyError:
        return False
    return True


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--title", action="append", default=[],
                        help="a title to measure; repeat the flag to measure a set")
    parser.add_argument("--set", dest="set_file", help="file with one title per line")
    parser.add_argument("--page", help="HTML file; every h1, h2 and h3 becomes one title")
    parser.add_argument("--lang", choices=("vi", "en", "auto"), default="auto")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="write the report here instead of stdout")
    parser.add_argument("--devices", action="store_true", help="print the device table and exit")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        text = self_check()
        emit(text)
        return 0 if "0 failed" in text else 2
    if args.devices:
        emit(device_table(), args.output)
        return 0

    titles = list(args.title)
    if args.set_file:
        titles += [line.strip() for line in
                   Path(args.set_file).read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.page:
        titles += headings(Path(args.page).read_text(encoding="utf-8"))
    if not titles:
        parser.error("pass --title, --set FILE, --page FILE, --devices or --self-check")

    devices = read_devices()
    readings = [measure_title(title,
                              detect_language(title) if args.lang == "auto" else args.lang,
                              devices)
                for title in titles]
    per_title = [title_gates(reading) for reading in readings]
    across = set_gates(readings, devices)

    if args.json:
        emit_json({"titles": readings, "per_title": per_title, "across_the_set": across,
                   "left_to_a_person": [name for name, _ in JUDGEMENTS],
                   "blocking": blocking([row for rows in per_title for row in rows]) + blocking(across)},
                  args.output)
    else:
        emit(report(readings, per_title, across), args.output)

    if blocking([row for rows in per_title for row in rows]) or blocking(across):
        return 2
    # Nothing measurable is wrong and two things are still unjudged. Exit 3 rather than 0, because a
    # green headline check is exactly the artefact somebody would wave instead of reading the title.
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
