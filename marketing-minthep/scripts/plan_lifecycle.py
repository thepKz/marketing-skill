#!/usr/bin/env python3
"""Grade a lifecycle flow against the duties Vietnamese law attaches to each stage of it.

`lifecycle-retention.md` was thirty-nine lines of welcome-nurture-cart-winback, written from the
American email-marketing playbook: a state map, a trigger matrix, and the advice to diagnose before
discounting. None of it was wrong about email. All of it was silent about the thing that actually
decides whether a Vietnamese flow may be sent at all.

The gap is not thinness, it is subject. A lifecycle flow is the one marketing artefact built entirely
out of stored personal data and scheduled repeat contact, which is exactly what Luat Bao ve quyen loi
nguoi tieu dung so 19/2023/QH15 regulates. Four of its rules have no analogue in the playbook:

  Dieu 18.4.b    Consent to be marketed to has to be its own control, separate from consent to
                 transact. A single checkbox at checkout is not consent to the flow, and the flow is
                 the entire asset.
  Dieu 20.3      The record has to be destroyed when the retention period in your own published
                 policy runs out. So a win-back at month eighteen against a twelve-month policy is
                 not a lapsed-customer campaign, it is unlawful processing - and the number that
                 makes it unlawful is a number you chose and published yourself.
  Dieu 42.2.d    A service of three months or more owes a renewal notice at least 07 working days
                 before expiry, and 42.2.e owes an end-of-contract notice on the same clock. Working
                 days, not days.
  Dieu 10.1.b    Harassment is contact "trai voi y muon" - against the consumer's wishes. That is
                 broader than contact after an unsubscribe, and no article in this corpus converts it
                 into a send-frequency number.

And one rule that reaches the top of the funnel rather than the flow: Nghi dinh 342/2025/ND-CP Dieu
17 governs the capture overlay itself. One interaction to close, no fake close icon, zero wait for a
static image and at most 05 seconds for motion, plus a working control to report the ad. Nghi dinh
87/2026/ND-CP Dieu 56.2.b prices a failure at 30 to 40 million. The email consultant's popup advice
is a design opinion; this is a fine.

Why a flow is declared rather than scanned
------------------------------------------
`check_claims.py` can read a draft, because a claim is words. A flow is not words - it is a schedule,
a consent state, a retention policy and a contract term, none of which appear in the copy. So there
is nothing to scan and no regular expression worth writing. The input is a declaration: `--template`
writes the sheet, a human fills it in, and `--audit` grades it.

That puts the honesty problem in a different place. A scanner over-reports; a declaration sheet
under-reports, because the fastest way to pass is to leave a row blank. So a blank field fails its
gate, an unparseable value fails its gate, and declaring a continuous service while leaving the
renewal date as `-` fails the gate that would have measured the renewal date. Silence is never an
answer.

The arithmetic this does, and the arithmetic it refuses
------------------------------------------------------
Two things here are computed rather than asserted:

  working days   Weekdays strictly between the notice and the deadline, counted exclusively, which
                 is the conservative reading. The script also reports the last lawful send date by
                 walking the calendar backwards, because "07 ngay lam viec" is not a date and the
                 person scheduling the send needs a date.
  retention      The declared longest delay in the flow against the declared retention period. This
                 is subtraction, and it is the single most common way a lifecycle programme built
                 from a global template breaks Vietnamese law.

And one thing it refuses: public holidays are not netted out of the working-day count. Tet moves
against the solar calendar, the holiday list is set by an annual instrument, and hardcoding either
would be a wrong answer with a confident face on it. So the count is weekdays only, the report says
so, and it tells the scheduler to move the send one day earlier for every public holiday inside the
window. A tool that quietly assumed nine fixed holidays would silently approve a Tet renewal notice
that arrives two days late.

The other refusal is a number the flow author will ask for and this table does not carry: how many
messages per week are too many. Luat 19/2023 and Nghi dinh 87/2026 name no ceiling - the test in
Dieu 10.1.b is the consumer's wishes, not a count. The separate decree on advertising messages and
email does set per-day caps and a time window, and it is not in this corpus, so the declared
frequency is reported as context and no gate certifies it.

What the fine column does not measure
-------------------------------------
Only the two advertising instruments carry bands, so nineteen of the twenty-five rows have a fine of
zero. That is not a discount. The consumer-protection law hands the consumer a remedy instead, and
on a distance sale the remedy is bigger than the fine: Dieu 38.3.b opens a 30-day free exit whenever
the pre-contract information was inaccurate or incomplete, and Dieu 10.1.e turns an over-claim into a
duty to refund or replace on every unit sold under it. Give the script `--orders` and `--aov` and it
sizes that against the 30 to 40 million the same over-claim costs as a fine, which is usually the
moment the argument about marketing copy stops being about tone.

Usage:
    python scripts/plan_lifecycle.py --duties
    python scripts/plan_lifecycle.py --duties --stage winback
    python scripts/plan_lifecycle.py --template flow.csv
    python scripts/plan_lifecycle.py --audit flow.csv
    python scripts/plan_lifecycle.py --audit flow.csv --orders 4200 --aov 690000 --json

Exit codes are 0 clean, 1 usage error, 2 a gate failed.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

DUTIES = Path(__file__).resolve().parents[1] / "data" / "lifecycle-duties.csv"

COLUMNS = ("id", "stage", "duty_vi", "duty_en", "timing_rule", "applies_when", "decides_from",
           "instrument", "article", "sanction_article", "fine_low", "fine_high",
           "consumer_remedy", "what_it_does_not_cover", "gazette", "source_url", "verified_at")

# Reading order, not importance. A flow is graded in the order the customer meets it.
STAGES = ("capture", "consent", "send", "purchase", "review", "renewal", "exit", "winback",
          "service")

WORKING_DAYS_NOTICE = 7        # Điều 42.2.đ and 42.2.e
REFUND_DEADLINE_DAYS = 30      # Điều 38.4
DISTANCE_EXIT_DAYS = 30        # Điều 38.3.b
CONTINUOUS_SERVICE_MONTHS = 3  # Điều 3.6
STATIC_OVERLAY_WAIT = 0        # Điều 17.3 of Nghị định 342/2025
MOTION_OVERLAY_WAIT = 5        # Điều 17.3 of Nghị định 342/2025

# Every channel a Vietnamese lifecycle flow runs on is a distance channel, so Điều 38 binds on all of
# them. The list exists to be read, not to be filtered: a reader looking for the exemption will not
# find one here, which is the finding.
CHANNELS = ("zalo-oa", "zns", "sms-brandname", "email", "app-push", "web-onsite",
            "marketplace-chat", "phone")

YES_NO = ("yes", "no")
YES_NO_NA = ("yes", "no", "n/a")

# name, kind, allowed, what the person filling it in needs to know
FIELDS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    ("service_months", "months", (),
     "term of the thing being sold, in months; 0 for a one-off purchase, or the word indefinite"),
    ("contract_in_writing", "choice", YES_NO_NA,
     "is the continuous-service contract in writing with a copy given to the consumer"),
    ("renewal_date", "date", (), "the date the service expires, or - if nothing renews"),
    ("renewal_notice_date", "date", (), "the date the pay-to-continue notice is sent, or -"),
    ("end_date", "date", (), "the date the contract ends, or - if it does not"),
    ("end_notice_date", "date", (), "the date the end-of-contract notice is sent, or -"),
    ("lockin_months", "int", (), "months the consumer cannot leave; 0 if they can leave any time"),
    ("retention_months_declared", "int", (),
     "the retention period your published rule states, in months; 0 if it states none"),
    ("max_delay_months", "int", (),
     "months from last contact to the latest message in the whole flow set, win-back included"),
    ("marketing_consent", "choice", ("separate", "bundled", "none"),
     "separate = its own control; bundled = inside the transaction consent; none = never asked"),
    ("notice_before_collect", "choice", YES_NO,
     "purpose, scope and retention period told before the first field is filled"),
    ("overlay", "choice", ("none", "static", "motion"),
     "the capture unit: none, a static image, or animation or video"),
    ("wait_seconds", "int", (), "seconds before the close control becomes usable"),
    ("close_taps", "int", (), "interactions needed to close it; 1 is the ceiling"),
    ("close_icon", "choice", ("clear", "ambiguous", "absent", "n/a"),
     "clear = unmistakably the close control; ambiguous covers fake and hard-to-find"),
    ("has_report_control", "choice", YES_NO_NA,
     "can the user report unlawful ad content and refuse ads they find unsuitable"),
    ("shares_with_third_party", "choice", YES_NO,
     "is the list disclosed or transferred to anyone outside your own business"),
    ("third_party_consent", "choice", ("separate", "bundled", "none", "n/a"),
     "the allow-or-refuse control for third-party sharing, which is its own control"),
    ("processor", "text", (),
     "the agency or platform that handles the list on your behalf, or - for none"),
    ("processor_written_agreement", "choice", YES_NO_NA,
     "is that engagement in writing, scoping each side's responsibility"),
    ("repurposed_from", "text", (),
     "the purpose the data was originally collected for, if the flow uses it for another, else -"),
    ("renotified_for_new_purpose", "choice", YES_NO_NA,
     "was the consumer told about the new purpose and did they agree to the change"),
    ("sends_after_refusal", "choice", YES_NO,
     "does any message in the flow reach someone who asked not to be contacted"),
    ("messages_per_week", "int", (),
     "commercial messages one person can receive in a week at the flow's peak"),
    ("is_commercial", "choice", YES_NO,
     "does the flow carry advertising, as opposed to only transaction messages"),
    ("has_ad_label", "choice", YES_NO,
     "does every commercial message carry a mark distinguishing it from non-advertising"),
    ("uses_influencer", "choice", YES_NO, "does any message carry a sponsored creator's words"),
    ("discloses_sponsorship", "choice", YES_NO_NA, "is the sponsorship disclosed in advance"),
    ("channel", "choice", CHANNELS, "the primary channel; every option here is a distance channel"),
    ("claims_verified", "choice", YES_NO,
     "has every factual claim in the flow passed check_claims.py"),
    ("refund_window_days", "int", (),
     "days between the consumer's termination notice and the money leaving your account"),
    ("filters_reviews", "choice", YES_NO,
     "does anything prevent negative feedback from displaying, or reorder it dishonestly"),
    ("reuses_reviews_in_ads", "choice", YES_NO,
     "does any message reuse a consumer's review, photograph or words as advertising"),
    ("review_consent_on_file", "choice", YES_NO_NA,
     "is that person's own consent on file, separate from the marketplace terms"),
    ("has_self_service_deletion", "choice", YES_NO,
     "can the consumer check, correct or delete their record without asking a human"),
    ("has_breach_runbook", "choice", YES_NO,
     "is there a route to notify the authority within 24 hours of detecting an attack"),
)

FIELD_NAMES = tuple(name for name, _, _, _ in FIELDS)
TEMPLATE_HEADER = ("field", "value")

# A fine is money, and a nghiêm cấm act under Điều 10 is an act the law forbids outright. Both stop
# the send. A duty whose breach hands the consumer a remedy is graded below them, because the flow
# can ship while the remedy is being built. Derived here rather than typed into the table, so no row
# can quietly grade itself down.
SEVERITY_ORDER = {"critical": 0, "high": 1}

# The Điều 10 citation is read out of the remedy column as well as the duty column, and that is not a
# convenience. Four of the personal-data duties are written elsewhere in the law - notice before
# collection at Điều 17.1, marketing consent at Điều 18.4.b, destruction at Điều 20.3, deletion on
# request at Điều 20.1 - but breaching any of them means processing outside what the law allows, which
# is the prohibited act at Điều 10.1.m. Grading those off the duty article alone let bundled consent
# report as a fixable remedy while the reference called it the load-bearing failure. The table said
# otherwise in its own remedy column and nothing was reading it.
PROHIBITION = "Điều 10."


def read_duties(path: str | Path = DUTIES) -> list[dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(
            line for line in handle
            if line.strip() and not line.lstrip().startswith("#"))]
    if not rows:
        raise ValueError(f"{path} has no rows")
    missing = set(COLUMNS) - set(rows[0])
    if missing:
        raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")
    for row in rows:
        if row["stage"] not in STAGES:
            raise ValueError(f'{row["id"]}: unknown stage {row["stage"]!r}')
    return rows


def severity_of(row: dict[str, str]) -> str:
    if int(row["fine_high"]) > 0:
        return "critical"
    if PROHIBITION in row["article"] or PROHIBITION in row["consumer_remedy"]:
        return "critical"
    return "high"


def duties_for(duties: list[dict[str, str]], stage: str | None) -> list[dict[str, str]]:
    if stage is None:
        return sorted(duties, key=lambda row: (STAGES.index(row["stage"]), row["id"]))
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}; known stages are {', '.join(STAGES)}")
    return [row for row in duties if row["stage"] == stage]


# --------------------------------------------------------------------------- the declaration sheet

def build_template() -> str:
    lines = [
        "# Lifecycle flow declaration. Every field below is a question Vietnamese law lets an",
        "# inspector, or the consumer, ask about this flow. A blank value fails its gate rather",
        "# than passing it, and so does a value this script cannot parse.",
        "#",
        "# Run: python scripts/plan_lifecycle.py --audit this-file.csv",
        "",
        ",".join(TEMPLATE_HEADER),
    ]
    for name, kind, allowed, note in FIELDS:
        lines.append(f"# {note}")
        if allowed:
            lines.append(f"#   one of: {' | '.join(allowed)}")
        elif kind == "date":
            lines.append("#   YYYY-MM-DD, or -")
        elif kind == "months":
            lines.append("#   a whole number of months, or the word indefinite")
        elif kind == "int":
            lines.append("#   a whole number")
        lines.append(f"{name},")
        lines.append("")
    return "\n".join(lines) + "\n"


def read_declaration(path: str | Path) -> dict[str, str]:
    with open(path, encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(
            line for line in handle
            if line.strip() and not line.lstrip().startswith("#"))]
    if not rows or "field" not in rows[0]:
        raise ValueError(f"{path} has no field column; --template writes the sheet this reads")
    declared = {}
    for row in rows:
        name = (row.get("field") or "").strip()
        if not name:
            continue
        if name not in FIELD_NAMES:
            raise ValueError(f"{path} declares unknown field {name!r}")
        declared[name] = (row.get("value") or "").strip()
    return declared


def unanswered(declared: dict[str, str]) -> list[str]:
    return [name for name in FIELD_NAMES if not declared.get(name)]


# ------------------------------------------------------------------------------ reading the values

class Unreadable(Exception):
    """A declared value that cannot be parsed. Raised so a gate fails rather than guesses."""


def whole(declared: dict[str, str], name: str) -> int:
    raw = declared.get(name, "")
    try:
        return int(raw)
    except (TypeError, ValueError):
        raise Unreadable(f"{name} is {raw!r}, which is not a whole number") from None


def choice(declared: dict[str, str], name: str) -> str:
    raw = (declared.get(name) or "").lower()
    allowed = dict((field, options) for field, _, options, _ in FIELDS)[name]
    if raw not in allowed:
        raise Unreadable(f"{name} is {declared.get(name)!r}, not one of {' | '.join(allowed)}")
    return raw


def when(declared: dict[str, str], name: str) -> dt.date | None:
    raw = (declared.get(name) or "").strip()
    if raw == "-":
        return None
    try:
        return dt.date.fromisoformat(raw)
    except ValueError:
        raise Unreadable(f"{name} is {raw!r}, not a YYYY-MM-DD date or -") from None


def is_continuous(declared: dict[str, str]) -> bool:
    raw = (declared.get("service_months") or "").strip().lower()
    if raw == "indefinite":
        return True
    return whole(declared, "service_months") >= CONTINUOUS_SERVICE_MONTHS


# ---------------------------------------------------------------------------- the working-day maths

def working_days_between(start: dt.date, end: dt.date) -> int:
    """Weekdays strictly after `start` and strictly before `end`.

    Counted exclusively on purpose. "Toi thieu 07 ngay lam viec truoc ngay het han" does not say
    whether the notice day or the expiry day counts, and the reading that gives the consumer more
    warning is the one that cannot be wrong. Public holidays are not deducted - see the note in
    `holiday_warning`.
    """
    if end <= start:
        return 0
    days = 0
    cursor = start + dt.timedelta(days=1)
    while cursor < end:
        if cursor.weekday() < 5:
            days += 1
        cursor += dt.timedelta(days=1)
    return days


def last_lawful_notice_date(deadline: dt.date, needed: int = WORKING_DAYS_NOTICE) -> dt.date:
    """The latest date a notice may be sent and still clear `needed` working days.

    Walk backwards from the deadline collecting weekdays. Once the `needed`-th weekday is reached,
    any notice sent strictly before it clears the count, so the answer is the day before it.
    """
    found = 0
    cursor = deadline - dt.timedelta(days=1)
    while True:
        if cursor.weekday() < 5:
            found += 1
            if found == needed:
                return cursor - dt.timedelta(days=1)
        cursor -= dt.timedelta(days=1)


HOLIDAY_WARNING = (
    "Weekdays only. Public holidays are ngày làm việc too, and this script will not guess them: Tết "
    "moves against the solar calendar and the list is set annually. Move the send one day earlier "
    "for every public holiday inside the window."
)


# ----------------------------------------------------------------------------------------- the gates

def _notice_gate(declared: dict[str, str], deadline_field: str, notice_field: str) -> tuple[bool, str]:
    deadline = when(declared, deadline_field)
    notice = when(declared, notice_field)
    if deadline is None:
        return False, f"{deadline_field} is -, so the notice cannot be measured against anything"
    if notice is None:
        return False, f"{deadline_field} is {deadline}, but {notice_field} is -: no notice is planned"
    counted = working_days_between(notice, deadline)
    latest = last_lawful_notice_date(deadline)
    verdict = "clears" if counted >= WORKING_DAYS_NOTICE else "misses"
    plural = "day" if counted == 1 else "days"
    return counted >= WORKING_DAYS_NOTICE, (
        f"{notice} to {deadline} is {counted} working {plural}, which {verdict} the "
        f"{WORKING_DAYS_NOTICE} required. The last lawful send date is {latest}. {HOLIDAY_WARNING}")


def _overlay_wait(declared: dict[str, str]) -> tuple[bool, str]:
    kind = choice(declared, "overlay")
    waited = whole(declared, "wait_seconds")
    ceiling = STATIC_OVERLAY_WAIT if kind == "static" else MOTION_OVERLAY_WAIT
    return waited <= ceiling, (
        f"a {kind} overlay may hold the close control for {ceiling} seconds and this one holds it "
        f"for {waited}")


def _retention(declared: dict[str, str]) -> tuple[bool, str]:
    declared_months = whole(declared, "retention_months_declared")
    latest = whole(declared, "max_delay_months")
    if declared_months <= 0:
        return False, ("no retention period is published, so Điều 20.3 has no period to run against "
                       "and Điều 16.1.c is unmet on its own")
    if latest <= declared_months:
        return True, (f"the last message lands at month {latest}, inside the {declared_months} "
                      f"months published")
    return False, (f"the last message lands at month {latest}, {latest - declared_months} months "
                   f"after the record had to be destroyed")


def _frequency_note(declared: dict[str, str]) -> str:
    return (f"{whole(declared, 'messages_per_week')} messages a week is declared and no article in "
            f"this corpus turns that into a pass or a fail")


# id -> (applies, passes, finding). Each closure reads only the fields its table row declares in
# decides_from, and a test compares the two lists in both directions.
CHECKS: dict[str, object] = {}


def check(duty_id: str):
    def register(function):
        CHECKS[duty_id] = function
        return function
    return register


@check("overlay-closes-in-one-tap")
def _(declared):
    if choice(declared, "overlay") == "none":
        return False, True, "no overlay is used"
    taps, icon = whole(declared, "close_taps"), choice(declared, "close_icon")
    faults = []
    if taps > 1:
        faults.append(f"closing takes {taps} interactions where the article allows one")
    if icon != "clear":
        faults.append(f"the close icon is {icon} where the article requires one the user cannot "
                      f"mistake or miss")
    return True, not faults, ("; ".join(faults) if faults else
                              "one interaction closes it and the close icon is unmistakable")


@check("overlay-wait-is-capped")
def _(declared):
    if choice(declared, "overlay") == "none":
        return False, True, "no overlay is used"
    ok, finding = _overlay_wait(declared)
    return True, ok, finding


@check("overlay-carries-a-report-control")
def _(declared):
    if choice(declared, "overlay") == "none":
        return False, True, "no overlay is used"
    ok = choice(declared, "has_report_control") == "yes"
    return True, ok, ("a report-and-refuse control is present" if ok else
                      "no way to report unlawful ad content or refuse an unsuitable one")


@check("notice-before-the-field-is-filled")
def _(declared):
    ok = choice(declared, "notice_before_collect") == "yes"
    return True, ok, ("purpose, scope and retention are told before collection" if ok else
                      "the form collects before it tells the consumer what for and for how long")


@check("published-rule-names-a-retention-period")
def _(declared):
    months = whole(declared, "retention_months_declared")
    return True, months > 0, (f"the published rule states {months} months" if months > 0 else
                              "the published rule states no retention period")


@check("marketing-consent-is-its-own-choice")
def _(declared):
    state = choice(declared, "marketing_consent")
    return True, state == "separate", {
        "separate": "marketing consent is collected as its own allow-or-refuse control",
        "bundled": "marketing consent rides inside the transaction consent, which Điều 18.4.b "
                   "requires to be a separate mechanism",
        "none": "no allow-or-refuse control for marketing use exists at all",
    }[state]


@check("third-party-sharing-is-a-separate-choice")
def _(declared):
    if choice(declared, "shares_with_third_party") == "no":
        return False, True, "the list goes nowhere outside the business"
    state = choice(declared, "third_party_consent")
    return True, state == "separate", (
        f"the list is shared and the third-party control is {state}; the article requires its own "
        f"allow-or-refuse control, not the marketing one")


@check("a-new-purpose-needs-new-consent")
def _(declared):
    origin = (declared.get("repurposed_from") or "").strip()
    if origin == "-":
        return False, True, "the flow uses the data for the purpose it was collected for"
    ok = choice(declared, "renotified_for_new_purpose") == "yes"
    return True, ok, (f"the data was collected for {origin} and the change of purpose was "
                      f"{'notified and agreed' if ok else 'never notified'}")


@check("an-agency-on-the-list-needs-consent-and-a-contract")
def _(declared):
    who = (declared.get("processor") or "").strip()
    if who == "-":
        return False, True, "nobody outside the business handles the list"
    written = choice(declared, "processor_written_agreement") == "yes"
    consented = choice(declared, "third_party_consent") == "separate"
    return True, written and consented, (
        f"{who} handles the list; the engagement is {'in writing' if written else 'not in writing'} "
        f"and the consumer's consent to it is {'on file' if consented else 'not on file'}")


@check("no-contact-against-the-consumers-wishes")
def _(declared):
    ok = choice(declared, "sends_after_refusal") == "no"
    return True, ok, ((f"nothing in the flow reaches someone who refused. {_frequency_note(declared)}")
                      if ok else
                      (f"at least one message reaches someone who asked not to be contacted, which "
                       f"is a prohibited act rather than a deliverability problem. "
                       f"{_frequency_note(declared)}"))


@check("a-commercial-message-is-marked-as-advertising")
def _(declared):
    if choice(declared, "is_commercial") == "no":
        return False, True, "the flow carries only transaction messages"
    ok = choice(declared, "has_ad_label") == "yes"
    return True, ok, ("every commercial message carries an identifying mark" if ok else
                      "commercial messages carry no mark separating them from non-advertising")


@check("sponsored-influencer-content-is-disclosed")
def _(declared):
    if choice(declared, "uses_influencer") == "no":
        return False, True, "no sponsored creator content appears in the flow"
    ok = choice(declared, "discloses_sponsorship") == "yes"
    return True, ok, ("the sponsorship is disclosed in advance" if ok else
                      "a sponsored creator's recommendation is used without disclosing the "
                      "sponsorship")


@check("an-information-gap-opens-a-thirty-day-exit")
def _(declared):
    channel = choice(declared, "channel")
    ok = choice(declared, "claims_verified") == "yes"
    return True, ok, (
        f"{channel} is a distance channel, so Điều 38 binds. "
        + ("every claim in the flow has been checked against its evidence"
           if ok else
           f"unverified claims travel in the flow, and an inaccurate or incomplete pre-contract "
           f"statement opens a {DISTANCE_EXIT_DAYS}-day free exit on every contract it touched"))


@check("a-refund-lands-inside-thirty-days")
def _(declared):
    days = whole(declared, "refund_window_days")
    ok = days <= REFUND_DEADLINE_DAYS
    return True, ok, (f"refunds settle in {days} days against the {REFUND_DEADLINE_DAYS}-day "
                      f"deadline" + ("" if ok else ", after which interest runs on the balance"))


@check("an-over-claim-becomes-a-refund-duty")
def _(declared):
    if choice(declared, "claims_verified") == "yes":
        return False, True, "no unverified claim is in the flow"
    return True, False, ("an unverified claim is a refund, replacement or compensation duty on every "
                         "unit sold under it, which is a liability that scales with sales rather "
                         "than a single fine")


@check("negative-reviews-may-not-be-suppressed")
def _(declared):
    if choice(declared, "filters_reviews") == "no":
        return False, True, "feedback displays as it arrives"
    return True, False, ("feedback is filtered or reordered, and the only lawful exception is "
                         "feedback that itself breaks the law or offends social morality")


@check("a-testimonial-in-an-ad-needs-the-persons-consent")
def _(declared):
    if choice(declared, "reuses_reviews_in_ads") == "no":
        return False, True, "no consumer's words or image are reused as advertising"
    ok = choice(declared, "review_consent_on_file") == "yes"
    return True, ok, ("the reviewer's own consent is on file" if ok else
                      "a consumer's words or image are advertised without that person's consent, "
                      "and the marketplace terms they accepted are not that consent")


@check("continuous-service-starts-at-three-months")
def _(declared):
    if not is_continuous(declared):
        return False, True, (f"the term is under {CONTINUOUS_SERVICE_MONTHS} months, so Điều 42 "
                             f"does not bind")
    missing = [field for field in ("renewal_date", "end_date") if when(declared, field) is None]
    if missing:
        return True, False, (f"a continuous service is declared, so Điều 42 binds, but "
                             f"{' and '.join(missing)} is - and the notice duties cannot be measured")
    return True, True, "a continuous service is declared and both Điều 42 dates are on the sheet"


@check("a-continuous-service-contract-is-written-and-handed-over")
def _(declared):
    if not is_continuous(declared):
        return False, True, "not a continuous service"
    ok = choice(declared, "contract_in_writing") == "yes"
    return True, ok, ("the contract is in writing and the consumer holds a copy" if ok else
                      "no written contract is given to the consumer")


@check("renewal-notice-at-least-seven-working-days-out")
def _(declared):
    if not is_continuous(declared):
        return False, True, "not a continuous service"
    ok, finding = _notice_gate(declared, "renewal_date", "renewal_notice_date")
    return True, ok, finding


@check("contract-end-notice-at-least-seven-working-days-out")
def _(declared):
    if not is_continuous(declared):
        return False, True, "not a continuous service"
    ok, finding = _notice_gate(declared, "end_date", "end_notice_date")
    return True, ok, finding


@check("cancel-at-any-time-and-pay-only-for-use")
def _(declared):
    if not is_continuous(declared):
        return False, True, "not a continuous service"
    months = whole(declared, "lockin_months")
    return True, months == 0, ("the consumer may leave at any time" if months == 0 else
                               f"a {months}-month lock-in stands against a right to leave at any "
                               f"time, and Điều 25 decides whether it survives as a thỏa thuận khác")


@check("no-message-after-the-declared-retention-period")
def _(declared):
    ok, finding = _retention(declared)
    return True, ok, finding


@check("the-consumer-can-demand-deletion-mid-flow")
def _(declared):
    ok = choice(declared, "has_self_service_deletion") == "yes"
    return True, ok, ("the consumer can check, correct or delete their own record" if ok else
                      "every deletion request needs a human, and the article obliges you either to "
                      "do it or to hand over the tool")


@check("a-breach-notice-goes-out-inside-twenty-four-hours")
def _(declared):
    ok = choice(declared, "has_breach_runbook") == "yes"
    return True, ok, ("a 24-hour notification route exists" if ok else
                      "no route to notify the authority within 24 hours of detecting an attack")


def gates(duties: list[dict[str, str]], declared: dict[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for duty in duties_for(duties, None):
        severity = severity_of(duty)
        try:
            applies, passed, finding = CHECKS[duty["id"]](declared)
        except Unreadable as error:
            applies, passed, finding = True, False, f"undeclared or unreadable: {error}"
        rows.append({
            "gate": duty["id"],
            "stage": duty["stage"],
            "applies": applies,
            "pass": passed,
            "finding": finding,
            "reads": duty["decides_from"],
            "instrument": duty["instrument"],
            "article": duty["article"],
            "sanction_article": duty["sanction_article"],
            "fine_low": int(duty["fine_low"]),
            "fine_high": int(duty["fine_high"]),
            "consumer_remedy": duty["consumer_remedy"],
            "severity": severity,
            "blocks": severity == "critical",
        })
    rows.sort(key=lambda row: (row["pass"] or not row["applies"], SEVERITY_ORDER[row["severity"]],
                               STAGES.index(row["stage"])))
    return rows


def failed(rows: list[dict[str, object]]) -> list[str]:
    return [str(row["gate"]) for row in rows if row["applies"] and not row["pass"]]


def blocking(rows: list[dict[str, object]]) -> list[str]:
    return [str(row["gate"]) for row in rows
            if row["applies"] and not row["pass"] and row["blocks"]]


def exposure(rows: list[dict[str, object]]) -> tuple[int, int]:
    low = sum(int(row["fine_low"]) for row in rows if row["applies"] and not row["pass"])
    high = sum(int(row["fine_high"]) for row in rows if row["applies"] and not row["pass"])
    return low, high


def refund_liability(rows: list[dict[str, object]], orders: int, aov: int) -> int:
    """Money the consumer can reclaim, as opposed to money the state can fine.

    Both Điều 38.3.b and Điều 10.1.e attach to units sold, not to the ad. If either gate fails, every
    order in the window is refundable, so the arithmetic is orders times average order value. It sits
    beside a fine band of at most 40 million and is usually larger by an order of magnitude, which is
    the argument for checking copy before the flow ships rather than after.
    """
    triggers = {"an-information-gap-opens-a-thirty-day-exit", "an-over-claim-becomes-a-refund-duty"}
    if not (orders > 0 and aov > 0):
        return 0
    if any(row["gate"] in triggers and row["applies"] and not row["pass"] for row in rows):
        return orders * aov
    return 0


# --------------------------------------------------------------------------------------- rendering

def money(amount: int) -> str:
    return f"{amount:,}".replace(",", ".")


def render_duties(duties: list[dict[str, str]], stage: str | None) -> str:
    rows = duties_for(duties, stage)
    instruments = len({row["instrument"] for row in rows})
    lines = [f"# Lifecycle duties{f' - {stage}' if stage else ''}", ""]
    lines.append(f"{len(rows)} duties, read out of {instruments} "
                 f"{'instrument' if instruments == 1 else 'instruments'}. Severity is derived: a "
                 f"fine band or a nghiêm cấm act under Điều 10 blocks the send, everything else "
                 f"hands the consumer a remedy.")
    current = None
    for row in rows:
        if row["stage"] != current:
            current = row["stage"]
            lines += ["", f"## {current}", ""]
        band = (f"{money(int(row['fine_low']))}–{money(int(row['fine_high']))} đồng"
                if int(row["fine_high"]) else "no fine in this corpus")
        lines.append(f"- **{row['id']}** ({severity_of(row)}) — {row['duty_en']}")
        lines.append(f"  - {row['instrument']} {row['article']}, {band}, decided from "
                     f"`{row['decides_from']}`")
        if row["timing_rule"] != "-":
            lines.append(f"  - Timing: {row['timing_rule']}")
        if row["consumer_remedy"] != "-":
            lines.append(f"  - Remedy: {row['consumer_remedy']}")
        lines.append(f"  - Does not cover: {row['what_it_does_not_cover']}")
    return "\n".join(lines) + "\n"


def render(duties: list[dict[str, str]], path: str, rows: list[dict[str, object]],
           declared: dict[str, str], orders: int, aov: int) -> str:
    applicable = [row for row in rows if row["applies"]]
    bad = [row for row in applicable if not row["pass"]]
    low, high = exposure(rows)
    lines = [f"# Lifecycle audit: {path}", ""]
    lines.append(f"{len(applicable) - len(bad)} of {len(applicable)} applicable gates pass. "
                 f"{len(blocking(rows))} of the failures block the send.")
    blank = unanswered(declared)
    if blank:
        lines.append("")
        lines.append(f"{len(blank)} of {len(FIELD_NAMES)} fields are blank, and each one fails its "
                     f"gate rather than passing it: {', '.join(blank)}.")
    if high:
        lines.append("")
        lines.append(f"The failing advertising rows total {money(low)} to {money(high)} đồng if each "
                     f"is charged separately.")
    liability = refund_liability(rows, orders, aov)
    if liability:
        lines.append("")
        lines.append(f"Separately, {money(orders)} orders at {money(aov)} đồng puts "
                     f"{money(liability)} đồng of sales inside a refund or free-exit right. That is "
                     f"the number the unverified claim actually costs; the fine is the smaller half.")
    lines += ["", "## Failing gates", ""]
    if not bad:
        lines.append("None.")
    for row in bad:
        mark = "blocks" if row["blocks"] else "remedy"
        lines.append(f"- **{row['gate']}** ({row['stage']}, {row['severity']}, {mark}) — "
                     f"{row['finding']}")
        band = (f"{money(int(row['fine_low']))}–{money(int(row['fine_high']))} đồng"
                if int(row["fine_high"]) else row["consumer_remedy"])
        lines.append(f"  - {row['instrument']} {row['article']}: {band}")
    lines += ["", "## Passing gates", ""]
    for row in applicable:
        if row["pass"]:
            lines.append(f"- {row['gate']} ({row['stage']}) — {row['finding']}")
    skipped = [row for row in rows if not row["applies"]]
    if skipped:
        lines += ["", "## Not applicable", ""]
        for row in skipped:
            lines.append(f"- {row['gate']} — {row['finding']}")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Grade a lifecycle flow against the duties Vietnamese law attaches to it.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit", metavar="FLOW.CSV", help="grade a filled declaration sheet")
    mode.add_argument("--template", metavar="FLOW.CSV", help="write the declaration sheet to fill in")
    mode.add_argument("--duties", action="store_true", help="print every duty, grouped by stage")
    parser.add_argument("--stage", help=f"limit --duties to one stage: {', '.join(STAGES)}")
    parser.add_argument("--orders", type=int, default=0,
                        help="orders in the window, to size the refund liability")
    parser.add_argument("--aov", type=int, default=0, help="average order value in đồng")
    parser.add_argument("--table", default=str(DUTIES), help="override the duty table")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument("--output", help="write to a file instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    use_utf8_stdout()
    args = build_parser().parse_args(argv)


    try:
        duties = read_duties(args.table)
        if args.stage:
            duties_for(duties, args.stage)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1

    if args.duties:
        emit(render_duties(duties, args.stage), args.output)
        return 0

    if args.template:
        target = Path(args.template)
        if target.exists():
            print(f"{target} already exists; refusing to overwrite it", file=sys.stderr)
            return 1
        target.write_text(build_template(), encoding="utf-8")
        emit(f"Wrote {target} with {len(FIELD_NAMES)} fields to declare. A blank field fails its "
             f"gate; it does not pass it.\n")
        return 0

    try:
        declared = read_declaration(args.audit)
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1

    rows = gates(duties, declared)

    if args.json:
        low, high = exposure(rows)
        emit_json({"flow": args.audit, "gates": rows, "failed": failed(rows),
                   "blocking": blocking(rows), "unanswered": unanswered(declared),
                   "fine_vnd": {"low": low, "high": high},
                   "refund_liability_vnd": refund_liability(rows, args.orders, args.aov)},
                  args.output)
    else:
        emit(render(duties, args.audit, rows, declared, args.orders, args.aov), args.output)

    return 2 if failed(rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
