#!/usr/bin/env python3
"""Audit a draft against what Vietnamese law will actually ask about its claims.

`claims-proof-ledger.md` used to be thirty-three lines with a nine-column table and three links to
ftc.gov. It taught the American question - do you have substantiation - and then handed the reader
back the instrument that governs them, which is not the FTC. That is the wrong question in this
market, and getting it wrong is expensive rather than merely embarrassing.

Nghi dinh 87/2026/ND-CP asks five different questions, and only the first is the one about evidence.

  prohibited_outright   No document helps. Tobacco, spirits at 15 degrees or above, breast-milk
                        substitutes for under-24-months, prescription drugs, a doctor or a clinic in
                        a cosmetics ad, a patient saying a supplement cured them. The imagery itself
                        is the offence, and consent does not discharge it.
  needs_document        The FTC question. A superlative, a comparison against a rival, a person's
                        face, the business itself - each needs a lawful document behind it.
  must_match_filing     The one this skill got wrong. The proof is usually not a test result: it is
                        the product's own registration or declaration, and the claim may not exceed
                        it. A brand can hold a flawless clinical study and still be fined 30 to 40
                        million because the function was never written into the Phieu cong bo.
  mandatory_wording     Text that has to be in the ad because a statute names it, word for word.
                        "Thuc pham nay khong phai la thuoc va khong co tac dung thay the thuoc chua
                        benh" is not a courtesy, and the four category phrases are not optional.
  form_prescribed       The layout is regulated, not the copy. Dieu 53.1.b requires warning text to
                        contrast with its background and to be no smaller than the type in the rest
                        of the advertisement. That makes `data/colour-gates.csv` a legal instrument
                        in this skill and not only a craft one.

Two of those five have no analogue in the substantiation model, and they carry the highest bands in
the decree. Dieu 50.5.c reaches 80 to 100 million for misleading on an attribute "da dang ky hoac da
cong bo" - registered or published. The benchmark named in the statute is the filing, not the truth.

How the two halves of the audit divide, and why it matters
---------------------------------------------------------
A regular expression can read the copy. It cannot see the photograph, and it cannot open the Phieu
cong bo. So the audit has two sources and neither is allowed to stand in for the other:

  the draft      decides the gates a reader of the words can decide - a superlative, a comparative,
                 a drug verb on a cosmetic, a missing mandatory phrase, a treatment testimonial
  the answers    decide the gates only the person with the file can decide - is there a face in the
                 shot, is there a release for it, does the claim sit inside the dossier, is the
                 warning legible at final size

An unanswered question is a failing gate, never a passing one. That is the whole point: this script
cannot make a draft lawful, it can only stop the draft that is obviously not, and name what a human
still has to sign off. `--template` writes the answer sheet for a sector; every row on it is a
question a Vietnamese inspector is entitled to ask.

What over-reports, and deliberately
-----------------------------------
"Nhat" is the Vietnamese superlative marker and also a bound syllable in a dozen ordinary words -
thong nhat, dong nhat, nhat dinh, nhat quan, hop nhat, thu nhat. A scanner that ignores that fires
on every second paragraph; one that requires an adjective in front of it misses "nhat" used alone.
So the known false friends are masked before scanning and listed in `FALSE_FRIENDS`, and what
survives is reported as a candidate rather than a verdict. Over-reporting costs a document
reference. Under-reporting costs 10 to 20 million and a forced takedown.

Usage:
    python scripts/check_claims.py --audit draft.md --sector cosmetics
    python scripts/check_claims.py --audit draft.md --sector food --answers answers.csv
    python scripts/check_claims.py --template answers.csv --sector food
    python scripts/check_claims.py --families
    python scripts/check_claims.py --self-check

Exit codes are 0 clean, 1 usage error, 2 a gate failed.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

LEDGER = Path(__file__).resolve().parents[1] / "data" / "claim-evidence.csv"

COLUMNS = ("id", "claim_family", "verdict", "trigger_vi", "trigger_en", "detect_regex",
           "discharged_by", "who_issues_it", "instrument", "article", "fine_low", "fine_high",
           "extra_sanction", "what_it_does_not_establish", "source_url", "verified_at")

ANSWER_COLUMNS = ("claim_id", "status", "document", "issued_by", "reference", "expires",
                  "verified_at")

# present  - it is in the advertisement, or the required text is there
# absent   - it is not in the advertisement
# n/a      - the row cannot apply to this piece, and `document` has to say why
STATUSES = ("present", "absent", "n/a")

VERDICTS = ("prohibited_outright", "needs_document", "must_match_filing", "mandatory_wording",
            "form_prescribed")

# Which ledger families a sector has to answer for. Every sector also answers the `any` family,
# because a superlative is a superlative whatever is being sold.
SECTORS = {
    "cosmetics": ("cosmetics",),
    "food": ("food",),
    "supplement": ("food",),
    "device": ("medical device",),
    "medical-service": ("medical service",),
    "property": ("property",),
    "general": (),
}

# The decree gives these four their own articles, with their own documents and their own bands. This
# table does not carry them, and saying so is more useful than covering them badly.
OUT_OF_SCOPE = {
    "pharmaceutical": "Dieu 69 governs medicine advertising and is not in this table",
    "pesticide": "Dieu 76 governs plant protection products and is not in this table",
    "biocide": "Dieu 72 governs chemicals and insecticidal preparations and is not in this table",
}

# Vietnamese superlative markers that are also bound syllables in ordinary words, and the English
# collocations where "best" and "only" carry no superlative claim at all. Masked before scanning.
FALSE_FRIENDS = (
    "thống nhất", "đồng nhất", "nhất định", "nhất quán", "hợp nhất", "thứ nhất", "nhất thời",
    "nhất loạt", "phần nhất", "best practice", "best before", "best regards", "the only way",
    "not the only", "first and only child",
)

# Rows every sector answers whatever the copy says, because no scanner can see them.
ALWAYS_ASK = ("person-image-or-words", "business-activity", "product-conformity",
              "warning-legible", "warning-contrast-and-size")

# Prohibitions that bind whatever sector was declared, because the category itself is closed. A draft
# that says thuoc la is advertising tobacco whether or not anyone selected the tobacco sector.
#
# The other prohibitions are sector-bound, and the difference is in the decree rather than a
# convenience: Dieu 70.3.c bans a doctor in a cosmetics ad and Dieu 73.3 bans one in a device ad, but
# no article bans one in a food ad. Applying all ten everywhere would invent two offences and inflate
# the exposure figure by the band of an article that does not reach the piece.
UNIVERSAL_PROHIBITIONS = ("tobacco", "alcohol", "infant nutrition", "pharmaceutical")

# Prohibitions that live in the photograph rather than in the words. No regular expression sees a
# white coat, so these are asked on the answer sheet, and the only acceptable status is absent.
MUST_BE_ABSENT = ("banned-medical-staff-cosmetics", "banned-medical-staff-device",
                  "banned-foetus-imagery")

# The two catch-all rows. Nothing discharges them, so they are not questions on the answer sheet -
# they are the residual the whole exercise leaves behind, and Dieu 53.2 is the article most often
# actually applied. Attesting to them on a form would read as clearance, so the sheet stays silent
# and the reference says why instead.
NO_ANSWER_DISCHARGES = ("truthful-clear-accurate", "no-misleading-on-function")

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2}

TEMPLATE_HEADER = (
    "# Answer sheet for {sector}. Fill status with one of: present, absent, n/a.\n"
    "# A row left blank fails its gate. That is deliberate - an unanswered question is not a pass.\n"
    "# Where status is present and the row needs a document, name the document, who issued it, its\n"
    "# reference number, and when it expires. Where status is n/a, put the reason in document.\n"
)


def read_ledger(path: Path | str = LEDGER) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path} has a header and no rows")
    missing = [column for column in COLUMNS if column not in rows[0]]
    if missing:
        raise ValueError(f"{path} is missing columns: {', '.join(missing)}")
    for row in rows:
        if row["verdict"] not in VERDICTS:
            raise ValueError(f"{row['id']} has verdict {row['verdict']!r}, "
                             f"which is not one of {', '.join(VERDICTS)}")
        for column in ("fine_low", "fine_high"):
            row[column] = int(row[column]) if row[column].isdigit() else 0
    return rows


def families_for(sector: str) -> tuple[str, ...]:
    if sector in OUT_OF_SCOPE:
        return ("any",)
    if sector not in SECTORS:
        raise ValueError(f"unknown sector {sector!r}; pick one of "
                         f"{', '.join(sorted(SECTORS) + sorted(OUT_OF_SCOPE))}")
    return SECTORS[sector] + ("any",)


def in_scope(row: dict, sector: str) -> bool:
    """Sector rows apply to their sector. Closed categories apply to everyone.

    A general-sector draft that says "thuoc la" is advertising tobacco whether or not the person
    running the script picked a tobacco sector, so those four families are never filtered out. The
    sector-bound prohibitions are, because the decree bound them.
    """
    if row["verdict"] == "prohibited_outright" \
            and row["claim_family"] in UNIVERSAL_PROHIBITIONS:
        return True
    return row["claim_family"] in families_for(sector)


def mask_false_friends(text: str) -> str:
    """Blank the known false friends, preserving length so offsets and line numbers survive."""
    masked = text
    for phrase in FALSE_FRIENDS:
        masked = re.sub(re.escape(phrase), "·" * len(phrase), masked, flags=re.IGNORECASE)
    return masked


def scan(text: str, ledger: list[dict], sector: str) -> list[dict]:
    """Return one hit per ledger row the copy appears to trigger, with the line it fired on."""
    masked = mask_false_friends(text)
    lines = masked.split("\n")
    hits = []
    for row in ledger:
        if row["detect_regex"] == "-" or not in_scope(row, sector):
            continue
        pattern = re.compile(row["detect_regex"])
        for number, line in enumerate(lines, start=1):
            found = pattern.search(line)
            if found:
                hits.append({"id": row["id"], "verdict": row["verdict"],
                             "family": row["claim_family"], "article": row["article"],
                             "line": number, "matched": found.group(0).strip(),
                             "fine_low": row["fine_low"], "fine_high": row["fine_high"]})
                break
    return hits


def read_answers(path: Path | str | None) -> dict[str, dict]:
    if path is None:
        return {}
    with open(path, encoding="utf-8", newline="") as handle:
        # Blank lines have to go as well as comments. The template writes one between its
        # instructions and its header, and csv.DictReader takes the first line it is handed as the
        # field names - so leaving it in made the tool reject the sheet it had just written.
        rows = [row for row in csv.DictReader(
            line for line in handle
            if line.strip() and not line.lstrip().startswith("#"))]
    if rows and "claim_id" not in rows[0]:
        raise ValueError(f"{path} has no claim_id column; run --template to get the right shape")
    answers = {}
    for row in rows:
        claim_id = (row.get("claim_id") or "").strip()
        if not claim_id:
            continue
        status = (row.get("status") or "").strip().lower()
        if status and status not in STATUSES:
            raise ValueError(f"{claim_id} has status {status!r}; use one of {', '.join(STATUSES)}")
        answers[claim_id] = {key: (row.get(key) or "").strip() for key in ANSWER_COLUMNS}
        answers[claim_id]["status"] = status
    return answers


def rows_needing_an_answer(ledger: list[dict], sector: str) -> list[dict]:
    """The rows no scanner can decide: everything that must be present, plus the always-ask set."""
    wanted = []
    for row in ledger:
        if not in_scope(row, sector):
            continue
        if row["id"] in NO_ANSWER_DISCHARGES:
            continue
        if row["id"] in MUST_BE_ABSENT and row["claim_family"] in families_for(sector):
            wanted.append(row)
        elif row["verdict"] == "prohibited_outright":
            continue
        elif row["detect_regex"] != "-" and row["id"] not in ALWAYS_ASK:
            # The scanner reads this one out of the copy. Asking a human as well invites a yes that
            # contradicts the draft, and gives two answers to one question.
            continue
        elif row["verdict"] in ("must_match_filing", "mandatory_wording", "form_prescribed") \
                or row["id"] in ALWAYS_ASK:
            wanted.append(row)
    return wanted


def build_template(ledger: list[dict], sector: str) -> str:
    lines = [TEMPLATE_HEADER.format(sector=sector), ",".join(ANSWER_COLUMNS)]
    for row in rows_needing_an_answer(ledger, sector):
        lines.append(f"{row['id']},,,,,,")
    return "\n".join(lines) + "\n"


def documented(answer: dict | None) -> bool:
    """A row is discharged when someone said it is present and named the paper behind it."""
    if not answer or answer["status"] != "present":
        return False
    return bool(answer["document"]) and bool(answer["reference"] or answer["issued_by"])


def expired(answer: dict | None, as_of: str) -> bool:
    if not answer or not answer["expires"]:
        return False
    try:
        return dt.date.fromisoformat(answer["expires"]) <= dt.date.fromisoformat(as_of)
    except ValueError:
        return False


def exposure(ledger: list[dict], ids: list[str]) -> tuple[int, int]:
    """Add up the bands on the rows that failed. Fines under Dieu 4 stack per violation."""
    index = {row["id"]: row for row in ledger}
    low = sum(index[claim_id]["fine_low"] for claim_id in ids if claim_id in index)
    high = sum(index[claim_id]["fine_high"] for claim_id in ids if claim_id in index)
    return low, high


def gates(ledger: list[dict], sector: str, hits: list[dict], answers: dict[str, dict],
          as_of: str) -> list[dict]:
    """Fourteen gates. A gate that cannot apply to this sector says so and is not counted as passed.

    Nine read the draft, five read the answer sheet, and the five report absence of an answer as a
    failure. The severities are not invented: critical is where the decree either bans the thing
    outright or reaches disgorgement of the proceeds of sale.
    """
    index = {row["id"]: row for row in ledger}
    fired = {hit["id"]: hit for hit in hits}
    rows: list[dict] = []

    def add(gate: str, ok: bool | None, severity: str, observed: str, target: str, why: str,
            source: str, ids: list[str] | None = None) -> None:
        rows.append({"gate": gate, "pass": bool(ok), "applies": ok is not None,
                     "severity": severity, "observed": observed, "target": target, "why": why,
                     "reads": source, "claim_ids": list(dict.fromkeys(ids or []))})

    def answer_gate(gate: str, wanted: list[dict], severity: str, target: str, why: str,
                    expect: str) -> None:
        """Answered as expected, or it fails. Silence is the failure this file exists to catch.

        `expect` is one of documented (present and the paper named), present (there, no document
        required) or absent (the thing must not be in the piece at all).
        """
        if not wanted:
            add(gate, None, severity, f"no {sector} row in the ledger asks this", target, why,
                "answers")
            return
        unanswered, wrong = [], []
        for row in wanted:
            answer = answers.get(row["id"])
            if not answer or not answer["status"]:
                unanswered.append(row["id"])
            elif answer["status"] == "n/a" and not answer["document"]:
                unanswered.append(row["id"])
            elif answer["status"] == "n/a":
                continue
            elif expect == "documented" and not documented(answer):
                wrong.append(row["id"])
            elif expect == "present" and answer["status"] != "present":
                wrong.append(row["id"])
            elif expect == "absent" and answer["status"] != "absent":
                wrong.append(row["id"])
        broken = unanswered + wrong
        label = {"documented": "no document", "present": "not in the piece",
                 "absent": "in the piece"}[expect]
        observed = "; ".join(filter(None, [
            "unanswered: " + ", ".join(unanswered) if unanswered else "",
            f"{label}: " + ", ".join(wrong) if wrong else ""])) \
            or f"all {len(wanted)} answered as required"
        add(gate, not broken, severity, observed, target, why, "answers", broken)

    # 1. The sector itself. Answering honestly beats answering badly.
    reason = OUT_OF_SCOPE.get(sector)
    add("sector-is-covered-by-this-table", not reason, "critical",
        reason or f"{sector} maps to families {', '.join(families_for(sector))}",
        "one of " + ", ".join(sorted(SECTORS)),
        "This ledger reads five articles closely and leaves four alone. Medicine, chemicals, "
        "insecticidal preparations and plant protection products each carry their own article, their "
        "own documents and their own bands, and a partial answer on those is worse than none because "
        "it reads as clearance.", "ledger")

    # 2. Prohibitions. No document discharges these, so there is nothing to ask the marketer.
    banned = [claim_id for claim_id, hit in fired.items()
              if hit["verdict"] == "prohibited_outright"]
    add("nothing-in-the-prohibited-list", not banned, "critical",
        ", ".join(f"{claim_id} (line {fired[claim_id]['line']}, {fired[claim_id]['matched']!r})"
                  for claim_id in banned) or "no prohibited category detected",
        "no hit on the ten prohibited rows",
        "These ten are not evidence problems. The category is closed to advertising, so a study, a "
        "release and a licence all fail to help, and the fine sits at 50 to 70 million with forced "
        "removal on top. If one fired, the copy needs a different idea rather than a footnote.",
        "draft", banned)

    # 3 and 4. The FTC question, which is real here too - it is just not the only one.
    superlative = fired.get("superlative")
    add("every-superlative-has-a-document", not superlative or documented(answers.get("superlative")),
        "critical",
        f"line {superlative['line']}: {superlative['matched']!r}" if superlative
        else "no superlative detected",
        "each superlative names a lawful document proving it",
        "Dieu 50.2.a fines nhat, duy nhat, tot nhat, so mot and anything meaning the same at 10 to 20 "
        "million where no lawful proving document exists. The document has to name the comparison "
        "set, which is why most of these claims cannot be saved and have to be cut instead.",
        "draft", ["superlative"] if superlative and not documented(answers.get("superlative")) else [])

    comparative = fired.get("comparative-named-rival")
    add("no-comparative-without-documents",
        not comparative or documented(answers.get("comparative-named-rival")), "critical",
        f"line {comparative['line']}: {comparative['matched']!r}" if comparative
        else "no comparison against another party detected",
        "a like-for-like test on both products",
        "Dieu 50.4.b runs to 40 to 60 million, four times the superlative band, and it does not "
        "require you to name the rival - cung loai is enough. So the safe-looking phrasing that "
        "compares to an unnamed leading brand is inside the article, not outside it.",
        "draft", ["comparative-named-rival"]
        if comparative and not documented(answers.get("comparative-named-rival")) else [])

    # 5. The face. Rights in the photograph and consent from the person are different permissions.
    answer_gate("no-personal-image-without-consent",
                [index[claim_id] for claim_id in ("person-image-or-words",) if claim_id in index],
                "critical", "consent from the person depicted, on file, naming the placements",
                "Dieu 50.3.a fines using a person's image, voice or writing without that person's "
                "consent at 20 to 40 million. This is not the copyright question and buying the "
                "photograph does not answer it: a licence from the photographer or the agency is "
                "permission to use the file, not permission to use the person. For a generated face "
                "the honest answer is that no real person is depicted, and that has to be true.",
                expect="documented")

    # 6. The one the old file missed entirely.
    answer_gate("claims-do-not-exceed-the-filing",
                [row for row in ledger
                 if row["verdict"] == "must_match_filing" and in_scope(row, sector)],
                "critical", "every claim traced to the registration or declaration that carries it",
                "This is the question a Vietnamese inspector asks first and the substantiation model "
                "never asks at all. The benchmark is the product's own filing - Ho so cong bo my "
                "pham, the tu cong bo, the Giay chung nhan dang ky luu hanh - and Dieu 50.5.c reaches "
                "80 to 100 million for exceeding what was da dang ky hoac da cong bo. A brand can "
                "hold a flawless clinical study and still be fined because the function was never "
                "written into the filing.", expect="documented")

    # 7 and 8. Wording the statute dictates, split by whether a scanner can see it.
    phrases = [row for row in ledger if row["verdict"] == "mandatory_wording"
               and in_scope(row, sector) and row["detect_regex"] != "-"]
    absent_phrases = [row["id"] for row in phrases if row["id"] not in fired]
    add("mandatory-wording-present", not absent_phrases if phrases else None, "high",
        ", ".join(absent_phrases) or (f"all {len(phrases)} required phrases found" if phrases
                                      else f"no phrase is prescribed for {sector}"),
        "the exact phrase, in the advertisement",
        "Dieu 71.1 and 71.2.b name these word for word, so this is the one part of the audit where "
        "paraphrase is a violation rather than a style choice. Thuc pham nay khong phai la thuoc va "
        "khong co tac dung thay the thuoc chua benh has to appear even in a broadcast cut under "
        "fifteen seconds, which Dieu 71.2.c says in as many words.",
        "draft", absent_phrases)

    answer_gate("identity-block-is-present",
                [row for row in ledger if row["verdict"] == "mandatory_wording"
                 and in_scope(row, sector) and row["detect_regex"] == "-"],
                "high", "name, address and licence or receipt number, in the advertisement",
                "Every regulated sector requires a block naming the product and the party "
                "responsible for it, and Dieu 75.1 adds the operating licence number, the hours and "
                "the approved scope of practice for a medical service. No article grants a format "
                "exemption for a small placement, so a square social post carries the same block a "
                "billboard does.", expect="present")

    # 9 and 10. Two prohibitions worth their own gates because a generator produces them by default.
    imagery_rows = [index[claim_id] for claim_id in MUST_BE_ABSENT
                    if claim_id in index and index[claim_id]["claim_family"]
                    in families_for(sector)]
    medical = [claim_id for claim_id in ("banned-medical-staff-cosmetics",
                                         "banned-medical-staff-device") if claim_id in fired]
    declared = [row["id"] for row in imagery_rows
                if not answers.get(row["id"]) or not answers[row["id"]]["status"]
                or answers[row["id"]]["status"] == "present"]
    add("no-medical-staff-or-clinic-imagery",
        None if not imagery_rows and not medical else not (medical or declared), "critical",
        "; ".join(filter(None, [
            ", ".join(f"{claim_id} in the copy at line {fired[claim_id]['line']}"
                      for claim_id in medical),
            ", ".join(f"{claim_id} unanswered or present in the shot" for claim_id in declared)]))
        or "declared absent from both the copy and the shot",
        "no doctor, pharmacist, medical staff, uniform, clinic or hospital",
        "A white coat, a stethoscope and a clinic backdrop are the default look for skincare and "
        "device imagery, and for cosmetics they are banned outright at 15 to 20 million under Dieu "
        "70.3.c, for devices 20 to 30 million under Dieu 73.3. The ban covers the image, the "
        "clothing, the name and the written endorsement together, so hiring a real dermatologist "
        "makes it worse rather than better. This is a prompt constraint, not a legal footnote.",
        "draft and answers", medical + declared)

    offenders = [claim_id for claim_id in ("banned-patient-testimonial-food",
                                          "banned-cosmetic-as-drug") if claim_id in fired]
    add("no-treatment-claim-in-a-non-medicine", not offenders, "critical",
        "; ".join(f"{fired[claim_id]['id']} line {fired[claim_id]['line']}: "
                  f"{fired[claim_id]['matched']!r}" for claim_id in offenders)
        or "no treatment language and no patient testimony detected",
        "no cure, no treatment, no before-and-after recovery story",
        "Dieu 71.4 fines a patient describing a treatment effect at 20 to 30 million and truth is "
        "not a defence, because the article prohibits the form of the claim rather than a false one. "
        "Dieu 70.4.b puts a cosmetic that reads as a drug at 30 to 40 million with the proceeds of "
        "sale surrendered on top. The failure mode is ordinary copywriting: dieu tri, dac tri, "
        "khang viem, giam dau all read as medicine.",
        "draft", offenders)

    # 11. Where the craft gates become legal ones.
    answer_gate("warning-is-legible-at-final-size",
                [index[claim_id] for claim_id in ("warning-legible", "warning-contrast-and-size")
                 if claim_id in index],
                "high", "contrasting, and no smaller than the type in the rest of the ad",
                "Dieu 53.1.b sets no ratio and no point size: it says the warning must contrast with "
                "its background and must not be smaller than the advertisement's own type. So the "
                "measurement is yours to take and to record, which is what data/colour-gates.csv is "
                "for. Ten to twenty million, and the ad comes down.", expect="present")

    # 12. Paper with a date on it.
    stale = [claim_id for claim_id, answer in answers.items() if expired(answer, as_of)]
    add("no-expired-approval", not stale, "high",
        ", ".join(f"{claim_id} expired {answers[claim_id]['expires']}" for claim_id in stale)
        or f"no answer names an expiry at or before {as_of}",
        "every named document still in force",
        "Dieu 70.4.a treats an expired Phieu cong bo receipt exactly like a missing one, at 30 to 40 "
        "million with the proceeds surrendered. A campaign that was cleared in March and is still "
        "running in November is the ordinary way this happens, and nothing on the platform notices.",
        "answers", stale)

    # 13. Services can only advertise what the licence lists.
    service_rows = [index[claim_id] for claim_id in ("service-within-scope",
                                                    "medical-service-licence") if claim_id in index]
    answer_gate("service-claim-stays-inside-the-licence",
                service_rows if sector == "medical-service" else [], "critical",
                "the approved pham vi hoat dong chuyen mon on the licence",
                "Dieu 75.4 is 40 to 60 million plus a three to six month suspension for advertising "
                "beyond the approved scope, and Dieu 75.3 is 30 to 40 million for advertising with "
                "no licence at all. The question is never whether the practitioner can perform the "
                "service. It is whether the licence lists it.", expect="documented")

    # 14. The catch-all, which is the article most often actually applied.
    answered = {claim_id for claim_id, answer in answers.items() if answer["status"]}
    wanted = {row["id"] for row in rows_needing_an_answer(ledger, sector)}
    add("every-question-on-the-sheet-is-answered", wanted <= answered, "critical",
        f"{len(wanted & answered)} of {len(wanted)} answered"
        + (f"; missing {', '.join(sorted(wanted - answered))}" if wanted - answered else ""),
        "every row the sector's answer sheet carries",
        "Dieu 53.2 fines content that is not truthful, accurate or clear at 20 to 40 million and "
        "adds surrender of the proceeds of sales made from the advertising, and it names no test at "
        "all. It is the article that catches everything the specific ones miss, so a draft nobody "
        "has answered for is not a draft with unknown risk. It is a draft with the widest article in "
        "the decree pointed at it.",
        "answers", sorted(wanted - answered))

    rows.sort(key=lambda row: (row["pass"] or not row["applies"],
                               SEVERITY_ORDER[row["severity"]]))
    return rows


def blocking(gate_rows: list[dict]) -> int:
    return sum(1 for row in gate_rows
               if row["applies"] and not row["pass"] and row["severity"] == "critical")


def failed(gate_rows: list[dict]) -> int:
    return sum(1 for row in gate_rows if row["applies"] and not row["pass"])


def render_families(ledger: list[dict]) -> str:
    blurbs = {
        "prohibited_outright": "No document helps. The category, the imagery or the form of words is "
                               "closed, and consent does not open it.",
        "needs_document": "The substantiation question. Hold a lawful document proving the claim, "
                          "issued by whoever is entitled to issue it.",
        "must_match_filing": "The claim may not exceed the product's own registration or "
                             "declaration. A perfect study outside the filing does not help.",
        "mandatory_wording": "A statute dictates the words. Paraphrase is a violation.",
        "form_prescribed": "The layout is regulated - contrast, relative type size, reading speed - "
                           "and the copy may be faultless while the placement is not.",
    }
    lines = ["# Five ways a claim fails in Vietnam", "",
             "Only the second is the question the FTC model teaches, and it is not the expensive one.",
             ""]
    for verdict in VERDICTS:
        rows = [row for row in ledger if row["verdict"] == verdict]
        high = max(row["fine_high"] for row in rows)
        lines += [f"## {verdict} - {len(rows)} rows, up to {high:,} VND", "", blurbs[verdict], "",
                  "| id | family | article | band (VND) |", "| --- | --- | --- | --- |"]
        for row in sorted(rows, key=lambda row: -row["fine_high"]):
            lines.append(f"| `{row['id']}` | {row['claim_family']} | {row['article']} | "
                         f"{row['fine_low']:,} to {row['fine_high']:,} |")
        lines.append("")
    families = sorted({row["claim_family"] for row in ledger})
    lines += [f"Families: {', '.join(families)}.",
              "Sectors: " + ", ".join(sorted(SECTORS)) + ".",
              "Out of scope and named as such: " + "; ".join(
                  f"{key} ({value})" for key, value in sorted(OUT_OF_SCOPE.items())) + ".", ""]
    return "\n".join(lines)


def render(ledger: list[dict], sector: str, draft: str, hits: list[dict],
           gate_rows: list[dict], as_of: str) -> str:
    index = {row["id"]: row for row in ledger}
    lines = [f"# Claim audit: {draft}", "",
             f"Sector `{sector}`, as of {as_of}, against "
             f"{sum(1 for row in ledger if in_scope(row, sector))} of {len(ledger)} ledger rows.", ""]

    broken = [row for row in gate_rows if row["applies"] and not row["pass"]]
    exposed = sorted({claim_id for row in broken for claim_id in row["claim_ids"]})
    low, high = exposure(ledger, exposed)
    if broken:
        headline = (f"{len(broken)} of {sum(1 for row in gate_rows if row['applies'])} gates fail, "
                    f"{blocking(gate_rows)} of them blocking.")
        if high:
            headline += (f" The rows named carry {low:,} to {high:,} VND if every one is charged "
                         f"separately, which Dieu 4 allows.")
        lines += [f"> {headline}", ""]
    else:
        lines += ["> Every gate that applies passes. That is not clearance: it means nothing "
                  "mechanical is left, and a human still signs the filing.", ""]

    lines += ["## What the copy triggered", ""]
    if hits:
        lines += ["| line | id | verdict | article | matched | discharged by |",
                  "| --- | --- | --- | --- | --- | --- |"]
        for hit in sorted(hits, key=lambda hit: hit["line"]):
            row = index[hit["id"]]
            lines.append(f"| {hit['line']} | `{hit['id']}` | {hit['verdict']} | {row['article']} | "
                         f"`{hit['matched']}` | {row['discharged_by']} |")
    else:
        lines.append("Nothing in the copy matched a trigger. Nine of the fourteen gates read the "
                     "copy; the other five read the answer sheet, and they are where the work is.")
    lines.append("")

    lines += ["## Gates", "", "| gate | verdict | severity | reads | observed |",
              "| --- | --- | --- | --- | --- |"]
    for row in gate_rows:
        state = "n/a" if not row["applies"] else ("pass" if row["pass"] else "FAIL")
        lines.append(f"| {row['gate']} | {state} | {row['severity']} | {row['reads']} | "
                     f"{row['observed']} |")
    lines.append("")

    if broken:
        lines += ["## Why each failure matters", ""]
        for row in broken:
            lines += [f"### {row['gate']} ({row['severity']})", "",
                      f"Observed: {row['observed']}.  ",
                      f"Target: {row['target']}.", "", row["why"], ""]
            for claim_id in row["claim_ids"]:
                if claim_id in index:
                    ledger_row = index[claim_id]
                    lines.append(f"- `{claim_id}` - {ledger_row['instrument']} "
                                 f"{ledger_row['article']}, {ledger_row['fine_low']:,} to "
                                 f"{ledger_row['fine_high']:,} VND"
                                 + (f", plus: {ledger_row['extra_sanction']}"
                                    if ledger_row["extra_sanction"] != "-" else "")
                                 + f". What it does not establish: "
                                   f"{ledger_row['what_it_does_not_establish']}.")
            lines.append("")

    lines += ["## What this cannot tell you", "",
              "Whether the copy matches the filing, because it has not read the filing. Whether the "
              "face in the shot belongs to someone who agreed to be there. Whether the warning is "
              "legible at the size it will actually ship. Those are the answer-sheet gates, and a "
              "green result on them means a person said so, not that a script checked.", ""]
    return "\n".join(lines)


def self_check() -> str:
    ledger = read_ledger()
    lines = ["# check_claims self-check", ""]

    assert len(ledger) >= 40, len(ledger)
    assert len({row["id"] for row in ledger}) == len(ledger)
    for verdict in VERDICTS:
        assert any(row["verdict"] == verdict for row in ledger), verdict
    lines.append(f"- {len(ledger)} ledger rows, unique ids, all five verdicts populated")

    # Vietnamese false friends do not fire the superlative gate; a real superlative does.
    friendly = "Hai bên đã thống nhất một mức giá và giữ nhất quán trong suốt quý."
    assert not scan(friendly, ledger, "general"), scan(friendly, ledger, "general")
    real = "Đây là loại kem dưỡng tốt nhất thị trường hiện nay."
    assert [hit["id"] for hit in scan(real, ledger, "general")] == ["superlative"]
    lines.append("- thống nhất and nhất quán do not fire; tốt nhất does")

    # A prohibited category fires whatever sector was declared.
    tobacco = scan("Ưu đãi thuốc lá điện tử cuối tuần.", ledger, "general")
    assert [hit["id"] for hit in tobacco] == ["banned-tobacco"], tobacco
    rows = gates(ledger, "general", tobacco, {}, "2026-07-31")
    banned_gate = next(row for row in rows if row["gate"] == "nothing-in-the-prohibited-list")
    assert not banned_gate["pass"] and banned_gate["severity"] == "critical"
    lines.append("- a prohibited category fires under sector general and blocks")

    # The sector-bound prohibitions stay bound. One word firing two articles would invent an offence.
    both = scan("Được bác sĩ khuyên dùng.", ledger, "cosmetics")
    assert [hit["id"] for hit in both] == ["banned-medical-staff-cosmetics"], both
    assert not scan("Được bác sĩ khuyên dùng.", ledger, "food")
    lines.append("- bác sĩ fires the cosmetics article only, and no article at all for food")

    # A dermatologist in a cosmetics ad is a fine, not a creative choice.
    clinical = scan("Được bác sĩ da liễu tại phòng khám khuyên dùng.", ledger, "cosmetics")
    assert "banned-medical-staff-cosmetics" in [hit["id"] for hit in clinical], clinical
    rows = gates(ledger, "cosmetics", clinical, {}, "2026-07-31")
    assert not next(row for row in rows
                    if row["gate"] == "no-medical-staff-or-clinic-imagery")["pass"]
    lines.append("- a dermatologist in a cosmetics ad fails its own gate")

    # An unanswered sheet fails rather than passes.
    rows = gates(ledger, "cosmetics", [], {}, "2026-07-31")
    assert len(rows) == 14, len(rows)
    # no-expired-approval is the one answer gate an empty sheet legitimately clears: nothing named
    # is nothing lapsed. The other five have to fail, because silence is not an answer.
    silent = [row["gate"] for row in rows if row["reads"].endswith("answers") and row["applies"]
              and row["gate"] != "no-expired-approval"]
    passed = [gate for gate in silent if next(r for r in rows if r["gate"] == gate)["pass"]]
    assert not passed, passed
    assert len(silent) == 6, silent
    assert blocking(rows) >= 3, blocking(rows)
    lines.append(f"- an empty answer sheet fails all {len(silent)} answer gates rather than passing")

    # The sector out-of-scope refusal is a gate failure and not a crash.
    rows = gates(ledger, "pharmaceutical", [], {}, "2026-07-31")
    covered = next(row for row in rows if row["gate"] == "sector-is-covered-by-this-table")
    assert not covered["pass"] and "Dieu 69" in covered["observed"], covered
    lines.append("- sector pharmaceutical is refused by name rather than answered badly")

    # A filled sheet clears the answer gates for a sector with no mandatory phrase of its own.
    filled = {row["id"]: {"claim_id": row["id"],
                          "status": "absent" if row["id"] in MUST_BE_ABSENT else "present",
                          "document": "Phieu cong bo", "issued_by": "Cuc Quan ly Duoc",
                          "reference": "12345/20/CBMP-HN", "expires": "2030-01-01",
                          "verified_at": "2026-07-31"}
              for row in rows_needing_an_answer(ledger, "cosmetics")}
    rows = gates(ledger, "cosmetics", [], filled, "2026-07-31")
    assert failed(rows) == 0, [row["gate"] for row in rows if row["applies"] and not row["pass"]]
    lines.append("- a fully answered cosmetics sheet with no triggers clears every gate")

    # An expired document is caught even when everything else is in order.
    stale = dict(filled)
    stale["cosmetic-notice-number"] = dict(filled["cosmetic-notice-number"],
                                           expires="2026-01-01")
    rows = gates(ledger, "cosmetics", [], stale, "2026-07-31")
    assert not next(row for row in rows if row["gate"] == "no-expired-approval")["pass"]
    lines.append("- an approval that lapsed in January fails in July")

    # The mandatory food phrases are required by name, and absence is what fails.
    rows = gates(ledger, "food", [], {}, "2026-07-31")
    phrase_gate = next(row for row in rows if row["gate"] == "mandatory-wording-present")
    assert phrase_gate["applies"] and not phrase_gate["pass"]
    assert "advisory-not-a-medicine" in phrase_gate["claim_ids"], phrase_gate
    lines.append("- a food draft missing the không phải là thuốc advisory fails by row id")

    # Every gate explains itself, and every explanation cites something.
    rows = gates(ledger, "cosmetics", [], {}, "2026-07-31")
    assert all(len(row["why"].split()) > 25 for row in rows), \
        [row["gate"] for row in rows if len(row["why"].split()) <= 25]
    assert sum(1 for row in rows if "Dieu" in row["why"]) >= 11
    lines.append("- all 14 gates explain themselves in more than 25 words, 11 citing an article")

    # The template only asks what a scanner cannot answer.
    template = build_template(ledger, "food")
    assert "advisory-not-a-medicine" not in template, "a scannable phrase should not be asked"
    assert "food-identity-block" in template and "person-image-or-words" in template
    lines.append("- the template asks only what the scanner cannot decide")

    # The sheet this writes has to be readable by the thing that wrote it. It was not: the blank line
    # between the instructions and the header became the header, so the tool rejected its own output
    # and blamed the user for the shape of it.
    with tempfile.TemporaryDirectory() as folder:
        sheet = Path(folder) / "answers.csv"
        sheet.write_text(template, encoding="utf-8")
        blank = read_answers(sheet)
    asked = [row["id"] for row in rows_needing_an_answer(ledger, "food")]
    assert sorted(blank) == sorted(asked), (sorted(blank), sorted(asked))
    assert all(not answer["status"] for answer in blank.values())
    lines.append("- the template it writes is a sheet it can read back, with every status blank")

    lines += ["", "All assertions passed."]
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit a draft against the five ways a claim fails under Vietnamese law.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", metavar="DRAFT", help="read a draft and grade its claims")
    mode.add_argument("--template", metavar="ANSWERS.CSV",
                      help="write the answer sheet a sector has to fill in")
    mode.add_argument("--families", action="store_true",
                      help="print the five verdicts and every row under each")
    mode.add_argument("--self-check", action="store_true", help="run the built-in assertions")
    parser.add_argument("--sector", default="general",
                        help="which sector's articles apply; --families lists them")
    parser.add_argument("--answers", metavar="ANSWERS.CSV",
                        help="the filled answer sheet; without it every answer gate fails")
    parser.add_argument("--ledger", default=str(LEDGER), help="override the claim ledger")
    parser.add_argument("--as-of", default=dt.date.today().isoformat(),
                        help="date to measure document expiry against")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output", help="write to a file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    args = build_parser().parse_args(argv)

    if args.self_check:
        emit(self_check(), args.output)
        return 0

    try:
        ledger = read_ledger(args.ledger)
        families_for(args.sector)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1

    if args.families:
        emit(render_families(ledger), args.output)
        return 0

    if args.template:
        target = Path(args.template)
        if target.exists():
            print(f"{target} already exists; refusing to overwrite it", file=sys.stderr)
            return 1
        target.write_text(build_template(ledger, args.sector), encoding="utf-8")
        emit(f"Wrote {target} with "
             f"{len(rows_needing_an_answer(ledger, args.sector))} questions for {args.sector}. "
             f"Fill status on every row; a blank row fails its gate.\n")
        return 0

    try:
        text = Path(args.audit).read_text(encoding="utf-8")
        answers = read_answers(args.answers)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1

    hits = scan(text, ledger, args.sector)
    gate_rows = gates(ledger, args.sector, hits, answers, args.as_of)

    if args.json:
        exposed = sorted({claim_id for row in gate_rows
                          if row["applies"] and not row["pass"] for claim_id in row["claim_ids"]})
        low, high = exposure(ledger, exposed)
        emit_json({"draft": args.audit, "sector": args.sector, "as_of": args.as_of,
                   "hits": hits, "gates": gate_rows, "failed": failed(gate_rows),
                   "blocking": blocking(gate_rows),
                   "exposure_vnd": {"low": low, "high": high, "rows": exposed}}, args.output)
    else:
        emit(render(ledger, args.sector, args.audit, hits, gate_rows, args.as_of), args.output)

    return 2 if failed(gate_rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
