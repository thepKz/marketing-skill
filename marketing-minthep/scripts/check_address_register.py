#!/usr/bin/env python3
"""Check who a Vietnamese draft thinks it is talking to, and whether it holds that decision.

Why this is a separate check from cadence: Vietnamese has no neutral second person. English `you`
carries no age, no rank and no distance, so a translated draft has to invent all three, and the
inventing happens per sentence. The result is a piece that opens on `quý khách`, explains in `bạn`,
and closes on `mọi người` - every sentence grammatical, every sentence polite, and the reader can
feel that nobody decided. That is the loudest machine tell in Vietnamese marketing copy, and no
sentence-level reader catches it because each sentence is fine.

Two of the four gates here are grammar rather than taste. The reference grammar records that, with
the single exception of `tôi`, pronouns go in pairs: pick a form for the speaker and the form for the
hearer is determined. And it records that first-person plurals split into exclusive (`chúng tôi`,
us-not-you) and inclusive (`chúng ta`, you-and-me). Machine translation cannot see the second
distinction at all, because English `we` is both - which is how "we deliver in one day" comes back
as `chúng ta giao trong ngày`, where the customer is now doing the delivering.

    python scripts/check_address_register.py --check draft.md
    python scripts/check_address_register.py --text "Quý khách yên tâm, bạn nhé" --channel social
    python scripts/check_address_register.py --list-forms
    python scripts/check_address_register.py --explain "bạn"
    python scripts/check_address_register.py --self-check

Exit codes are 0 clean, 1 usage error, 2 a gate failed, 3 computable but unsettled.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TABLE = ROOT / "data" / "address-registers.csv"

# Below this the piece is a caption or a button, and copy that short can address nobody and still
# work. House figure: `bạn` in a three-word headline is often the wrong choice precisely because the
# headline has no room to place the reader.
ADDRESS_FLOOR_UNITS = 60

FENCE = re.compile(r"^\s*```")
SECOND_PERSON = {"2", "1-or-2"}
FIRST_PERSON = {"1", "1-or-2"}


def cells(value: str) -> list[str]:
    """A semicolon list, with `-` and `any` meaning no members rather than one member called `-`."""
    if value in ("-", "any"):
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def load() -> list[dict[str, str]]:
    if not TABLE.exists():
        raise SystemExit(f"missing data table: {TABLE}")
    return list(csv.DictReader(io.StringIO(TABLE.read_text(encoding="utf-8"))))


def prose(text: str) -> str:
    """Drop fenced code only. Unlike the cadence check this keeps headings and list items, because a
    heading addressing `quý khách` above body copy addressing `bạn` is the exact defect being
    measured - stripping the heading would hide it."""
    kept, fenced = [], False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        kept.append("" if fenced else line)
    return "\n".join(kept)


def units(text: str) -> int:
    """Syllables, which in Vietnamese orthography are whitespace-separated tokens."""
    return len(re.findall(r"[^\W\d_]+", text, flags=re.UNICODE))


def detect(text: str, rows: list[dict[str, str]]) -> list[dict]:
    """Find every address form, longest form first, masking what has been claimed.

    Masking is not an optimisation, it is the whole correctness argument. `chúng tôi` contains
    `tôi`, `người ta` contains `ta`, and `các bạn` contains `bạn`. Without masking a draft that says
    `chúng tôi` once reports two first-person forms, one of them a tier it never used, and the
    register gate then fails a clean draft. Matched spans are blanked to a character that no pattern
    can match, so later patterns see the right absence at the right offset.
    """
    body = prose(text)
    working = body
    hits: list[dict] = []
    # Longest surface form first. The form string, not the regex, is what nests.
    detectable = [row for row in rows if row["detect_regex"] != "-"]
    for row in sorted(detectable, key=lambda row: -len(row["form"])):
        pattern = re.compile(row["detect_regex"], re.IGNORECASE)
        spans, samples = [], []
        for match in pattern.finditer(working):
            spans.append(match.span())
            if len(samples) < 3:
                start = max(0, match.start() - 18)
                samples.append(body[start:match.end() + 18].replace("\n", " ").strip())
        if not spans:
            continue
        chars = list(working)
        for start, end in spans:
            chars[start:end] = "\x00" * (end - start)
        working = "".join(chars)
        hits.append({"form": row["form"], "person": row["person"], "tier": row["tier"],
                     "count": len(spans), "samples": samples,
                     "ambiguous": row["ambiguous_with"] != "-", "row": row})
    return sorted(hits, key=lambda hit: (hit["person"], -hit["count"]))


def _verdict(violations: list[str], hits: list[dict], involved: set[str]) -> str:
    """`failed` when the evidence is unambiguous, `review` when it rests on an ambiguous form.

    Half the forms in this table are also ordinary words. `em` is a younger sibling and a term of
    endearment, `cháu` is a grandchild, `mày` is inside `lông mày`, and `mình` is the reflexive
    pronoun in all three persons. A gate that reports `failed` on a testimonial quoting a customer
    who said `em` teaches people to switch the gate off, so when every piece of evidence for a
    violation runs through an ambiguous form the answer is `review` and the script names the string
    to go and look at.
    """
    if not violations:
        return "passed"
    ambiguous = {hit["form"] for hit in hits if hit["ambiguous"]}
    return "review" if involved and involved <= ambiguous else "failed"


def gate_address_present(hits: list[dict], total: int) -> dict:
    second = [hit for hit in hits if hit["person"] in SECOND_PERSON]
    if second:
        status, why = "passed", (f"addresses the reader as "
                                f"{', '.join(hit['form'] for hit in second)}")
    elif total < ADDRESS_FLOOR_UNITS:
        status, why = "skipped", (f"{total} syllables is short-form copy, and copy this short can "
                                 f"address nobody and still work. The floor is "
                                 f"{ADDRESS_FLOOR_UNITS}")
    else:
        status, why = "failed", (f"{total} syllables and no second-person form anywhere. The copy "
                                f"describes rather than addresses, which is the shape of a product "
                                f"sheet, not of something someone reads and acts on")
    return {"gate": "address-present", "status": status, "why": why,
            "evidence_grade": "house-rule"}


def gate_one_address_form(hits: list[dict], rows: list[dict[str, str]]) -> dict:
    by_form = {row["form"]: row for row in rows}
    second = [hit for hit in hits if hit["person"] in SECOND_PERSON]
    if len(second) < 2:
        return {"gate": "one-address-form", "status": "skipped",
                "why": ("fewer than two second-person forms, so there is no mixture to measure"
                        if second else "no second-person form to measure"),
                "evidence_grade": "standard-requirement-with-house-threshold"}
    violations, involved = [], set()
    for index, left in enumerate(second):
        for right in second[index + 1:]:
            composes = (right["form"] in cells(by_form[left["form"]]["composes_with"])
                        or left["form"] in cells(by_form[right["form"]]["composes_with"]))
            if composes:
                continue
            violations.append(f"{left['form']} ({left['tier']}) beside {right['form']} "
                              f"({right['tier']})")
            involved.update({left["form"], right["form"]})
    status = _verdict(violations, hits, involved)
    tiers = sorted({hit["tier"] for hit in second})
    if status == "passed":
        why = (f"{len(second)} second-person forms and every combination is one the table allows: "
               f"{', '.join(hit['form'] for hit in second)}")
    else:
        why = (f"the copy addresses the reader at {len(tiers)} different tiers "
               f"({', '.join(tiers)}): " + "; ".join(violations))
    return {"gate": "one-address-form", "status": status, "why": why,
            "unsettled": sorted(involved) if status == "review" else [],
            "evidence_grade": "standard-requirement-with-house-threshold"}


def gate_pair_holds(hits: list[dict], rows: list[dict[str, str]]) -> dict:
    by_form = {row["form"]: row for row in rows}
    first = [hit for hit in hits if hit["person"] in FIRST_PERSON]
    second = [hit for hit in hits if hit["person"] in SECOND_PERSON]
    if not first or not second:
        return {"gate": "pair-holds", "status": "skipped",
                "why": ("no first-person form, so there is no pair to check"
                        if not first else "no second-person form, so there is no pair to check"),
                "evidence_grade": "standard-requirement"}
    violations, involved, exempt = [], set(), []
    for speaker in first:
        speaker_row = by_form[speaker["form"]]
        if speaker_row["pairs_with"] == "any":
            exempt.append(speaker["form"])
            continue
        for hearer in second:
            if speaker["form"] == hearer["form"]:  # `em` is both sides of itself
                continue
            if (hearer["form"] in cells(speaker_row["pairs_with"])
                    or speaker["form"] in cells(by_form[hearer["form"]]["pairs_with"])):
                continue
            violations.append(f"{speaker['form']} does not take {hearer['form']}")
            involved.update({speaker["form"], hearer["form"]})
    status = _verdict(violations, hits, involved)
    if status == "passed":
        note = f" ({', '.join(exempt)} takes any second person)" if exempt else ""
        why = f"every speaker form is paired with a hearer form the grammar allows{note}"
    else:
        why = ("the pairing rule is broken: " + "; ".join(violations)
               + ". Pick the speaker form first, and the hearer form is then determined")
    return {"gate": "pair-holds", "status": status, "why": why,
            "unsettled": sorted(involved) if status == "review" else [],
            "evidence_grade": "standard-requirement"}


def gate_inclusive_exclusive(hits: list[dict], rows: list[dict[str, str]]) -> dict:
    by_form = {row["form"]: row for row in rows}
    marked = {hit["form"]: by_form[hit["form"]]["inclusive"] for hit in hits
              if by_form[hit["form"]]["inclusive"] in ("inclusive", "exclusive")}
    if not marked:
        return {"gate": "inclusive-exclusive", "status": "skipped",
                "why": "no first-person plural, so the distinction does not arise",
                "evidence_grade": "standard-requirement"}
    inclusive = sorted(form for form, kind in marked.items() if kind == "inclusive")
    exclusive = sorted(form for form, kind in marked.items() if kind == "exclusive")
    if inclusive and exclusive:
        return {"gate": "inclusive-exclusive", "status": "failed",
                "why": (f"{', '.join(exclusive)} excludes the reader and "
                        f"{', '.join(inclusive)} includes them, and both refer to the seller in "
                        f"one piece. Decide whether the reader is inside the company or outside it"),
                "evidence_grade": "standard-requirement"}
    kind = "inclusive" if inclusive else "exclusive"
    return {"gate": "inclusive-exclusive", "status": "passed",
            "why": (f"first-person plural is consistently {kind} "
                    f"({', '.join(inclusive or exclusive)})"),
            "evidence_grade": "standard-requirement"}


def gate_no_archaic_or_impolite(hits: list[dict]) -> dict:
    bad = [hit for hit in hits if hit["tier"] in ("archaic", "impolite")]
    if not bad:
        return {"gate": "no-archaic-or-impolite", "status": "passed",
                "why": "no obsolete or superior-to-inferior form",
                "evidence_grade": "standard-requirement"}
    involved = {hit["form"] for hit in bad}
    status = _verdict([hit["form"] for hit in bad], hits, involved)
    detail = "; ".join(f"{hit['form']} ({hit['tier']}) x{hit['count']}" for hit in bad)
    return {"gate": "no-archaic-or-impolite", "status": status,
            "why": (f"{detail}. These do not belong in commercial copy: the obsolete forms arrive "
                    f"through machine translation of period fiction, and the familiar ones assign "
                    f"the reader a lower rank"),
            "unsettled": sorted(involved) if status == "review" else [],
            "evidence_grade": "standard-requirement"}


def gate_channel_fit(hits: list[dict], rows: list[dict[str, str]], channel: str | None) -> dict:
    by_form = {row["form"]: row for row in rows}
    if channel is None:
        return {"gate": "channel-fit", "status": "skipped",
                "why": "no --channel given, so nothing to fit against",
                "evidence_grade": "craft-heuristic"}
    if not hits:
        return {"gate": "channel-fit", "status": "skipped",
                "why": "no address form found", "evidence_grade": "craft-heuristic"}
    wrong = [(hit["form"], by_form[hit["form"]]["fits_channel"]) for hit in hits
             if channel not in cells(by_form[hit["form"]]["fits_channel"])]
    if not wrong:
        return {"gate": "channel-fit", "status": "passed",
                "why": f"every form found is listed for {channel}",
                "evidence_grade": "craft-heuristic"}
    detail = "; ".join(f"{form} fits {fits}" for form, fits in wrong)
    return {"gate": "channel-fit", "status": "failed",
            "why": f"{len(wrong)} form(s) are not written for {channel}: {detail}",
            "evidence_grade": "craft-heuristic"}


def settle(gates: list[dict]) -> dict:
    counts = {status: sum(1 for gate in gates if gate["status"] == status)
              for status in ("passed", "failed", "review", "skipped")}
    failed = [gate["gate"] for gate in gates if gate["status"] == "failed"]
    review = [gate["gate"] for gate in gates if gate["status"] == "review"]
    if failed:
        status, why = "failed", (f"{len(failed)} gate(s) failed: {', '.join(failed)}")
    elif review:
        unsettled = sorted({form for gate in gates for form in gate.get("unsettled", [])})
        status = "review"
        why = (f"{len(review)} gate(s) turn on a form that is also an ordinary word "
               f"({', '.join(unsettled)}). Read those lines and settle whether the form is "
               f"addressing the reader or describing somebody")
    elif counts["passed"]:
        status, why = "passed", "the copy picks one reader and holds them"
    else:
        status, why = "skipped", "nothing measurable: no address form and no text to measure"
    return {"status": status, "why": why, "counts": counts}


def check(text: str, rows: list[dict[str, str]], channel: str | None) -> dict:
    hits = detect(text, rows)
    total = units(prose(text))
    gates = [
        gate_address_present(hits, total),
        gate_one_address_form(hits, rows),
        gate_pair_holds(hits, rows),
        gate_inclusive_exclusive(hits, rows),
        gate_no_archaic_or_impolite(hits),
        gate_channel_fit(hits, rows, channel),
    ]
    return {"syllables": total, "channel": channel,
            "forms": [{key: hit[key] for key in ("form", "person", "tier", "count", "samples",
                                                 "ambiguous")} for hit in hits],
            "gates": gates, "verdict": settle(gates)}


def as_text(report: dict) -> str:
    lines = ["# address-register check", "",
             f"{report['syllables']} syllables of prose"
             + (f", channel {report['channel']}" if report["channel"] else "") + ".", ""]
    if not report["forms"]:
        lines += ["No address form in `data/address-registers.csv` was found.", ""]
    else:
        lines += ["## Forms found", "",
                  "| Form | Person | Tier | Hits | Also an ordinary word | Where |",
                  "|---|---|---|---|---|---|"]
        for hit in report["forms"]:
            sample = hit["samples"][0][:52] if hit["samples"] else "-"
            lines.append(f"| {hit['form']} | {hit['person']} | {hit['tier']} | {hit['count']} "
                         f"| {'yes' if hit['ambiguous'] else 'no'} | {sample} |")
        lines.append("")
    lines += ["## Gates", "", "| Gate | Status | Grade | Why |", "|---|---|---|---|"]
    for gate in report["gates"]:
        lines.append(f"| {gate['gate']} | {gate['status']} | {gate['evidence_grade']} "
                     f"| {gate['why']} |")
    verdict = report["verdict"]
    lines += ["", "## Verdict", "", f"**{verdict['status']}** - {verdict['why']}", ""]
    return "\n".join(lines)


def list_forms(rows: list[dict[str, str]]) -> str:
    lines = ["# Address forms", "",
             "| Form | Person | Number | Tier | Takes | Sits beside | Fits |",
             "|---|---|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['form']} | {row['person']} | {row['number']} | {row['tier']} "
                     f"| {row['pairs_with']} | {row['composes_with']} | {row['fits_channel']} |")
    advisory = [row["form"] for row in rows if row["detect_regex"] == "-"]
    lines += ["", f"{len(rows)} forms. Advisory rows with no detector: "
                  f"{', '.join(advisory) or 'none'}.", ""]
    return "\n".join(lines)


def explain(form: str, rows: list[dict[str, str]]) -> str:
    row = next((row for row in rows if row["form"] == form), None)
    if row is None:
        raise SystemExit(f"no such form: {form}. Run --list-forms")
    lines = [f"# {row['form']}", "",
             f"Person {row['person']}, {row['number']}, tier `{row['tier']}`"
             + (f", {row['inclusive']}" if row["inclusive"] != "-" else "") + ".", "",
             f"**Why it matters.** {row['why_it_matters']}.", "",
             f"**Wrong when.** {row['wrong_when']}.", "",
             f"**Takes as the other side.** {row['pairs_with']}.",
             f"**Can sit beside.** {row['composes_with']}.",
             f"**Also an ordinary word.** {row['ambiguous_with']}.",
             f"**Fits.** {row['fits_channel']}.",
             f"**Detector.** `{row['detect_regex']}`" +
             (f" - probe `{row['probe']}`" if row["probe"] != "-" else " (advisory row)"), "",
             f"Grade `{row['evidence_grade']}`, source: {row['source']}.", ""]
    return "\n".join(lines)


def self_check(rows: list[dict[str, str]]) -> str:
    """Every assertion here is a bug this script had, or one the design invites."""
    # Masking. `chúng tôi` must not also report `tôi`, and `người ta` must not report `ta`.
    found = {hit["form"] for hit in detect("Chúng tôi giao trong ngày cho các bạn.", rows)}
    assert found == {"chúng tôi", "các bạn"}, found
    assert {hit["form"] for hit in detect("Người ta nói vậy.", rows)} == {"người ta"}

    # Every probe in the table must resolve to exactly the form that owns it. This is the check the
    # generator cannot do, because nesting is settled by the masking order in this file.
    for row in rows:
        if row["probe"] == "-":
            continue
        got = {hit["form"] for hit in detect(row["probe"], rows)}
        assert row["form"] in got, (row["form"], row["probe"], got)

    # The documented tôi exception: it takes any second person, so no pairing failure.
    clean = check("Tôi mở quán năm 2009. Quý khách ghé trước 11h30 thì có chỗ.", rows, None)
    by_gate = {gate["gate"]: gate for gate in clean["gates"]}
    assert by_gate["pair-holds"]["status"] == "passed", by_gate["pair-holds"]
    assert clean["verdict"]["status"] == "passed", clean["verdict"]

    # The headline defect: elevated and peer address in one piece.
    mixed = check("Quý khách vui lòng giữ hoá đơn. Bạn cần hỗ trợ thì gọi bọn mình nha.", rows, None)
    mixed_gates = {gate["gate"]: gate for gate in mixed["gates"]}
    assert mixed_gates["one-address-form"]["status"] == "failed", mixed_gates["one-address-form"]
    assert mixed["verdict"]["status"] == "failed", mixed["verdict"]

    # bạn and các bạn are the one allowed switch: number, not tier.
    number = check("Bạn có bốn mươi phút. Các bạn ghé trước 11h30 nhé. Bọn mình mở từ 7h sáng.",
                   rows, None)
    number_gates = {gate["gate"]: gate for gate in number["gates"]}
    assert number_gates["one-address-form"]["status"] == "passed", number_gates["one-address-form"]

    # Inclusive against exclusive, which is the calque of English `we` and a grammatical error.
    both = check("Chúng tôi giao trong ngày. Chúng ta cùng giữ chất lượng đó cho bạn.", rows, None)
    both_gates = {gate["gate"]: gate for gate in both["gates"]}
    assert both_gates["inclusive-exclusive"]["status"] == "failed", both_gates["inclusive-exclusive"]

    # An obsolete form is unambiguous, so it fails rather than reviews.
    old = check("Ngươi muốn mua gì? Chúng tôi có đủ.", rows, None)
    old_gates = {gate["gate"]: gate for gate in old["gates"]}
    assert old_gates["no-archaic-or-impolite"]["status"] == "failed", old_gates
    # And an ambiguous one reviews rather than fails. This is cosmetics copy: `kẻ mày` is eyebrow
    # pencil, and the detector cannot know that. `lông mày` is excluded outright because it can only
    # be the noun; `kẻ mày` is left to `review` because it could be either, and a checker that
    # hard-fails a brow product's description is a checker the copywriter turns off on day one.
    brow = check("Bút kẻ mày này giữ nét cả ngày, tôi dùng ba tháng rồi.", rows, None)
    brow_gates = {gate["gate"]: gate for gate in brow["gates"]}
    assert brow_gates["no-archaic-or-impolite"]["status"] == "review", brow_gates
    assert brow["verdict"]["status"] == "review", brow["verdict"]
    assert "mày" in brow["verdict"]["why"], brow["verdict"]
    # `lông mày` on the other hand is settled, and must not even be reported.
    assert not [hit for hit in detect("Chì kẻ lông mày lâu trôi.", rows) if hit["form"] == "mày"]
    # Two impolite forms together are not ambiguous at all, and must hard-fail.
    rude = check('Khách nhắn: "Mày tư vấn giúp tao với."', rows, None)
    assert {gate["gate"]: gate for gate in
            rude["gates"]}["no-archaic-or-impolite"]["status"] == "failed", rude["gates"]

    # Short copy must not fail for addressing nobody. A button is allowed to address nobody.
    short = check("Đặt trước 11h30.", rows, None)
    short_gates = {gate["gate"]: gate for gate in short["gates"]}
    assert short_gates["address-present"]["status"] == "skipped", short_gates["address-present"]
    # Long copy that never addresses anyone is a product sheet pretending to be an ad.
    sheet = check(" ".join(["Sản phẩm được làm từ gỗ sồi tự nhiên và sơn phủ gốc nước."] * 8),
                  rows, None)
    sheet_gates = {gate["gate"]: gate for gate in sheet["gates"]}
    assert sheet_gates["address-present"]["status"] == "failed", sheet_gates["address-present"]

    # Channel fit only runs when asked, and it must catch ceremonial register on social.
    social = check("Kính thưa quý vị, chúng tôi xin thông báo.", rows, "social")
    social_gates = {gate["gate"]: gate for gate in social["gates"]}
    assert social_gates["channel-fit"]["status"] == "failed", social_gates["channel-fit"]
    assert {gate["gate"]: gate for gate in
            check("Kính thưa quý vị.", rows, None)["gates"]}["channel-fit"]["status"] == "skipped"

    # A clean Vietnamese draft in one consistent register must pass everything that runs.
    good = check("Bọn mình rang cà phê ở Gò Vấp và giao trong ngày cho quán trong bán kính tám cây "
                 "số. Ngày rang in dưới đáy túi. Bạn không thấy ngày rang thì đừng mua. Bạn đặt "
                 "trước 4h chiều thì mai có hàng.", rows, "social")
    assert good["verdict"]["status"] == "passed", good
    assert not [gate for gate in good["gates"] if gate["status"] == "failed"], good["gates"]

    # `em` sits on both sides of the conversation, so it must not fail against `anh`.
    retail = check("Em gửi anh ảnh sản phẩm. Anh xem giúp em nhé.", rows, "chat")
    retail_gates = {gate["gate"]: gate for gate in retail["gates"]}
    assert retail_gates["one-address-form"]["status"] == "passed", retail_gates["one-address-form"]
    assert retail_gates["pair-holds"]["status"] == "passed", retail_gates["pair-holds"]

    # Fenced code must not contribute address forms: a code sample is not copy.
    fenced = check("```\nban = 'quý khách'\n```\n\nBạn đặt trước nhé. Bọn mình giao hôm sau.",
                   rows, None)
    assert {hit["form"] for hit in fenced["forms"]} == {"bạn", "bọn mình"}, fenced["forms"]

    return "self-check passed\n"


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    rows = load()
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", help="file to measure")
    parser.add_argument("--text", help="measure this string instead of a file")
    parser.add_argument("--channel", choices=sorted(
        {channel for row in rows for channel in cells(row["fits_channel"])}),
        help="check the forms against what this channel takes")
    parser.add_argument("--list-forms", action="store_true")
    parser.add_argument("--explain", metavar="FORM")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--output", help="write here instead of stdout")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)

    if args.self_check:
        emit(self_check(rows))
        return 0
    if args.list_forms:
        emit(list_forms(rows), args.output)
        return 0
    if args.explain:
        emit(explain(args.explain, rows), args.output)
        return 0
    if not (args.check or args.text):
        parser.error("pass --check FILE, --text STRING, --list-forms, --explain FORM, "
                     "or --self-check")

    text = args.text if args.text else Path(args.check).read_text(encoding="utf-8")
    report = check(text, rows, args.channel)
    if args.format == "json":
        emit_json(report, args.output)
    else:
        emit(as_text(report), args.output)
    return {"passed": 0, "failed": 2, "review": 3, "skipped": 3}[report["verdict"]["status"]]


if __name__ == "__main__":
    from _emit import run_gate
    run_gate(main)
