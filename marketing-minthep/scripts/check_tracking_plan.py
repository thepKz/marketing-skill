#!/usr/bin/env python3
"""Check the two things a measurement plan gets wrong before any data arrives, and do the one honest
piece of arithmetic available on the discrepancy afterwards.

A campaign gets tagged and instrumented once, and both jobs are done by somebody in a hurry. The
mistakes are not judgement calls, they are typos with a three-month delay: a `utm_medium` of `Social`
that lands in a channel the reports call Unassigned, the same campaign spelled two ways so it arrives
as two rows, an event name with a space in it that GA4 drops, a phone number sitting in a query string
where it becomes somebody else's liability. Every one of those is checkable from the string itself,
which is what this script does.

What it will not do is tell you why the platform reported more conversions than your analytics. That
question has structural answers, they are recorded per platform in `data/attribution-windows.csv`, and
choosing between them needs both accounts open. There is one number worth computing, and it is an
inequality rather than an estimate: if three platforms each claim conversions and the sum exceeds what
analytics counted in total, the excess is a floor on how much of it is double-counted. That floor is
arithmetic. Everything past it is a hypothesis.

The GA4 and Google Ads limits enforced here were read off vendor documentation on 2026-07-31 and each
one carries its source in `data/attribution-windows.csv`. They change. `--rules` prints them with the
page to re-read.

    python scripts/check_tracking_plan.py --url "https://a.vn/?utm_source=facebook&utm_medium=cpc..."
    python scripts/check_tracking_plan.py --urls tagged.txt
    python scripts/check_tracking_plan.py --event add_to_cart --params item_id=A1,quantity=2
    python scripts/check_tracking_plan.py --reconcile meta=120,google=80,tiktok=40 --analytics 190
    python scripts/check_tracking_plan.py --delivered 640 --purchases 1000
    python scripts/check_tracking_plan.py --events
    python scripts/check_tracking_plan.py --windows
    python scripts/check_tracking_plan.py --rules

Exit codes are 0 clean, 1 usage error, 2 a blocking gate failed.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, emit_json, use_utf8_stdout  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
EVENT_TABLE = DATA / "tracking-events.csv"
WINDOW_TABLE = DATA / "attribution-windows.csv"

# Every limit below was read on vendor documentation on 2026-07-31. Google publishes no last-updated
# date on its help pages, so treat the date as the date it was checked and nothing more.
# Two pages, and which one supplies what matters, because one of them is the wrong citation for half
# of this block. The numeric ceilings are on `Event collection limits`,
# https://support.google.com/analytics/answer/9267744, which carries the limits table and the
# page_title carve-out. The reserved prefixes and the reserved event names are on `Event naming
# rules`, https://support.google.com/analytics/answer/13316687, which carries no limits table at all -
# citing it for a number would be citing a page that does not contain one.
# The domains a window row is allowed to cite. A vendor fact comes from the vendor, and the one time
# the research could not find a page it recorded that instead of reaching for an agency blog - which
# is why this list has no room for one.
VENDOR_HOSTS = ("support.google.com", "developers.facebook.com", "www.facebook.com",
                "ads.tiktok.com", "seller-vn.tiktok.com", "business-api.tiktok.com",
                "zalo.cloud", "oa.zalo.me", "ads.zalo.me", "developers.zalo.me",
                "seller.shopee.vn", "banhang.shopee.vn",
                "sellercenter.lazada.vn", "open.lazada.com")

EVENT_NAME_MAX = 40
PARAMS_PER_EVENT_MAX = 25
PARAM_NAME_MAX = 40
PARAM_VALUE_MAX = 100
# Three parameters have their own longer ceilings, which is worth encoding rather than flagging a
# legitimate page path as too long.
PARAM_VALUE_MAX_BY_NAME = {"page_title": 300, "page_referrer": 420, "page_location": 1000}
# A key event gets `_c` appended internally, and the vendor text is explicit that a name over 40
# characters loses the suffix and stops being reported as a key event. 40 is therefore the documented
# cliff. 38 is not documented anywhere; it is the margin that leaves room for the two characters, and
# it is reported as a low-severity note rather than a failure so the distinction stays visible.
KEY_EVENT_NAME_SAFE = EVENT_NAME_MAX - 2

# Web-stream reserved event names, verbatim from the vendor list. Sending one of these means the hit
# is dropped or collides with a built-in, and neither failure shows up as an error anywhere.
RESERVED_EVENT_NAMES = frozenset("""
ad_impression app_remove app_store_refund app_store_subscription_cancel app_store_subscription_renew
click error file_download first_open first_visit form_start form_submit in_app_purchase page_view
scroll session_start user_engagement view_complete video_progress video_start view_search_results
""".split())
# Reserved prefixes. `gtag.` and the bare underscore come from the parameter rules; `firebase_`,
# `ga_` and `google_` are reserved across events, parameters and user properties.
RESERVED_PREFIXES = ("_", "firebase_", "ga_", "google_", "gtag.")
# Names that cannot be registered as custom parameters. `currency` and `value` appear on the vendor
# list yet are also GA4's own recommended ecommerce parameters, so sending them on a purchase is
# correct and only registering them as custom is not. The exemption keeps a correct ecommerce
# implementation from failing a gate that was aimed at something else.
RESERVED_PARAM_NAMES = frozenset("""
cid currency customer_id customerid dclid gclid session_id sessionid sfmc_id sid srsltid uid user_id
userid
""".split())
STANDARD_ECOMMERCE_PARAMS = frozenset("""
currency value items item_id item_name transaction_id quantity price coupon shipping tax affiliation
""".split())

# The published default-channel-group rules, medium side only. Google also routes on source, but the
# lists of search and social sites behind that half are published as a spreadsheet rather than as
# text, and the medium is the half the person tagging the link actually controls. A medium matching
# none of these can only be classified by source, and when that fails the traffic arrives unattributed.
#
# Ordered exact matches first, broad patterns last, which is NOT the vendor's own evaluation order.
# The gate's verdict does not depend on the order - a medium either matches some published rule or it
# matches none - but the channel *name* in the report does, and `cpm` is on the Display list while also
# matching the paid pattern's `.*cp.*`. Under the vendor's ordering it is Display. Under a
# first-match loop with the paid rule at the top it came out as Paid Other, which is a wrong label
# printed with total confidence. Specificity-first reproduces the vendor's answer on every medium I
# can construct a conflict for, and where it cannot be sure the label says so.
CHANNEL_BY_MEDIUM = (
    (re.compile(r"^organic$"), "Organic Search"),
    (re.compile(r"^(email|e-mail|e_mail|e mail)$"), "Email"),
    (re.compile(r"^affiliate$"), "Affiliates"),
    (re.compile(r"^(referral|app|link)$"), "Referral"),
    (re.compile(r"^(social|social-network|social-media|sm|social network|social media)$"),
     "Organic Social"),
    (re.compile(r"^(display|banner|expandable|interstitial|cpm)$"), "Display"),
    (re.compile(r"^audio$"), "Audio"),
    (re.compile(r"^sms$"), "SMS"),
    # Three separate published rules rather than one merged pattern. Merging them was tempting and
    # wrong: the push rule matches on a suffix and on two substrings, so a merged exact-match pattern
    # would have quietly rejected `mobile_push` and `web_notification`, both of which route.
    (re.compile(r"(.*push$|.*mobile.*|.*notification.*)"), "Mobile Push Notifications"),
    (re.compile(r"^.*video.*$"), "Organic Video"),
    # Last, because it is the widest. Paid Search needs a search source as well as a paid medium, and
    # the source half needs a site list published as a spreadsheet, so the medium alone cannot tell
    # the two apart and the label refuses to pick one.
    (re.compile(r"^(.*cp.*|ppc|retargeting|paid.*)$"), "Paid Search or Paid Other"),
)

# A campaign name is a filter key that has to survive a year of them. Three segments is the floor
# because two cannot carry channel, offer and period, and a name with no period in it cannot be
# sorted or archived - by month six there are two hundred rows and no way to group them.
CAMPAIGN_SEGMENTS_MIN = 3
YYYYMM = re.compile(r"^(20\d{2})(0[1-9]|1[0-2])$")

REQUIRED_UTM = ("utm_source", "utm_medium", "utm_campaign")
OPTIONAL_UTM = ("utm_id", "utm_term", "utm_content")

# Personal data, caught two ways because the two catch different mistakes. A value that looks like an
# address or a Vietnamese mobile number is the accidental paste. A parameter whose name announces what
# it holds is the deliberate design decision, and that one is the more common of the two.
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# Both boundaries are explicit, and the left one is the whole point. `\b` alone matched inside a
# longer digit run, so the transaction id 20260801123456 contains 0801123456 and was reported as a
# phone number. A critical gate that fires on a legitimate order id gets switched off within a week,
# and then the gate that catches a real leaked number is gone too - a false positive on this gate is
# more expensive than a false negative on any other.
VN_PHONE = re.compile(r"(?<![\d+])(?:\+?84|0)(?:3|5|7|8|9)\d{8}(?!\d)")
IDENTITY_NAMES = frozenset("""
email mail e_mail phone sdt so_dien_thoai tel telephone mobile name fullname full_name ten hoten
ho_ten cccd cmnd id_card national_id passport dob birthday address dia_chi diachi
""".split())

SEVERITIES = ("critical", "high", "medium", "low")
BLOCKING = ("critical", "high")


def load_table(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def event_row(name: str) -> dict | None:
    for row in load_table(EVENT_TABLE):
        if row["event_name"] == name or row["id"] == name:
            return row
    return None


def _row(gate: str, passed: bool, severity: str, observed: str, target: str, why: str) -> dict:
    assert severity in SEVERITIES, severity
    return {"gate": gate, "pass": bool(passed), "severity": severity,
            "observed": observed, "target": target, "why": why}


def blocking_count(rows: list[dict]) -> int:
    return sum(1 for row in rows if not row["pass"] and row["severity"] in BLOCKING)


def personal_data(pairs: list[tuple[str, str]]) -> list[str]:
    """Return every reason this set of key-value pairs carries personal data."""
    found = []
    for key, value in pairs:
        bare = key.lower().lstrip("_")
        if bare in IDENTITY_NAMES:
            found.append(f"parameter named `{key}`")
        if EMAIL.search(value):
            found.append(f"`{key}` holds an email address")
        if VN_PHONE.search(value.replace(" ", "").replace("-", "")):
            found.append(f"`{key}` holds a phone number")
    return found


def channel_for(medium: str) -> str | None:
    """Which default channel a medium routes to. Case-folded, because the published channel
    definitions are not case sensitive even though the reported values are."""
    lowered = medium.strip().lower()
    for pattern, channel in CHANNEL_BY_MEDIUM:
        if pattern.match(lowered):
            return channel
    return None


def read_url(url: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    raw = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query = {key: value for key, value in raw}
    utm = {key: value for key, value in query.items() if key.startswith("utm_")}
    campaign = utm.get("utm_campaign", "")
    separators = {char for char in "-_" if char in campaign}
    segments = re.split(r"[-_]", campaign) if campaign else []
    return {
        "url": url,
        "host": parsed.netloc,
        "pairs": raw,
        "utm": utm,
        "missing": [key for key in REQUIRED_UTM if not utm.get(key, "").strip()],
        "uppercase": sorted(key for key, value in utm.items() if value != value.lower()),
        "whitespace": sorted(key for key, value in utm.items()
                             if value != value.strip() or re.search(r"[\s+]", value)),
        "double_encoded": sorted(key for key, value in utm.items() if "%25" in value.upper()),
        "channel": channel_for(utm.get("utm_medium", "")),
        "campaign": campaign,
        "segments": [segment for segment in segments if segment],
        "separators": sorted(separators),
        "has_period": any(YYYYMM.match(segment) for segment in segments),
        "personal": personal_data(raw),
        "has_id": bool(utm.get("utm_id", "").strip()),
        "fragment_tags": sorted(key for key in
                                dict(urllib.parse.parse_qsl(parsed.fragment)) if key.startswith("utm_")),
    }


def url_gates(stats: dict) -> list[dict]:
    rows: list[dict] = []
    rows.append(_row("personal-data-in-url", not stats["personal"], "critical",
                     "; ".join(stats["personal"]) or "none found",
                     "no personal data in any parameter",
                     "A query string is logged by the server, the analytics tool, every proxy in "
                     "between and the referrer of the next page, so a phone number put there to make "
                     "a report joinable reaches recipients nobody enumerated. That argument needs no "
                     "statute. The Vietnamese one is Law 91/2025/QH15, in force since 1 January 2026, "
                     "and it replaced the Decree 13/2023/ND-CP that most guidance still cites."))
    rows.append(_row("required-parameters", not stats["missing"], "critical",
                     "missing " + ", ".join(stats["missing"]) if stats["missing"]
                     else "source, medium and campaign present",
                     "utm_source, utm_medium and utm_campaign",
                     "Medium decides the channel, source decides the row inside it, campaign is the "
                     "only key that groups the spend. A link missing any of the three cannot be "
                     "reported on and the traffic is not recoverable afterwards."))
    if stats["utm"].get("utm_medium", "").strip():
        rows.append(_row("medium-routes-to-a-channel", stats["channel"] is not None, "high",
                         f"`{stats['utm']['utm_medium']}` routes to "
                         f"{stats['channel'] or 'no published channel rule'}",
                         "a medium matching a published channel definition",
                         "The default channel group is matched against a fixed list of medium "
                         "values. A medium outside it can only be classified by source, against a "
                         "site list Google publishes as a spreadsheet, and when that misses too the "
                         "traffic arrives unattributed. `social` routes. `Social Media` does not."))
    rows.append(_row("lowercase-values", not stats["uppercase"], "high",
                     "mixed case in " + ", ".join(stats["uppercase"]) if stats["uppercase"]
                     else "all lowercase",
                     "lowercase throughout",
                     "Parameter values are case sensitive in reporting, so `Facebook` and `facebook` "
                     "arrive as two rows that have to be added by hand for the rest of the campaign's "
                     "life. The channel rules themselves ignore case, which is why this survives "
                     "review: the traffic is classified correctly and still split in two."))
    rows.append(_row("no-whitespace", not stats["whitespace"], "high",
                     "whitespace in " + ", ".join(stats["whitespace"]) if stats["whitespace"]
                     else "no whitespace",
                     "no spaces or plus signs in a value",
                     "A space becomes `%20` or `+` depending on who built the link, so one campaign "
                     "becomes two rows and neither matches what was written in the brief."))
    rows.append(_row("no-double-encoding", not stats["double_encoded"], "medium",
                     "%25 in " + ", ".join(stats["double_encoded"]) if stats["double_encoded"]
                     else "encoded once",
                     "no %25 in a value",
                     "A link encoded twice usually means it passed through a builder and then a "
                     "shortener. The literal `%20` that arrives in the report is not a value anybody "
                     "will recognise."))
    if stats["campaign"]:
        rows.append(_row("campaign-name-is-a-filter-key",
                         len(stats["segments"]) >= CAMPAIGN_SEGMENTS_MIN, "medium",
                         f"{len(stats['segments'])} "
                         f"segment{'' if len(stats['segments']) == 1 else 's'} in "
                         f"`{stats['campaign']}`",
                         f">= {CAMPAIGN_SEGMENTS_MIN} segments",
                         "A campaign name is the only grouping key in the report, and it has to "
                         "survive a year of its own kind. Two segments cannot carry channel, offer "
                         "and period at once."))
        rows.append(_row("campaign-name-carries-a-period", stats["has_period"], "medium",
                         "no yyyymm segment" if not stats["has_period"] else "period present",
                         "one segment in yyyymm form",
                         "Without a period in the name there is no way to sort, archive or compare "
                         "like with like. By month six there are two hundred rows and no axis."))
        rows.append(_row("one-separator", len(stats["separators"]) <= 1, "low",
                         "both - and _ used" if len(stats["separators"]) > 1
                         else "consistent separator",
                         "one separator, hyphen or underscore",
                         "Mixing them guarantees the next person writes the name the other way and "
                         "creates a second row for the same campaign."))
    rows.append(_row("campaign-id-present", stats["has_id"], "low",
                     "utm_id present" if stats["has_id"] else "no utm_id",
                     "utm_id, when cost is imported",
                     "Cost imported by hand joins on the campaign id, not the campaign name. Without "
                     "it a spend figure cannot be attached to the traffic it bought."))
    if stats["fragment_tags"]:
        rows.append(_row("tags-after-the-fragment", False, "high",
                         "utm parameters after # in " + ", ".join(stats["fragment_tags"]),
                         "tags in the query string, before any #",
                         "Anything after the hash is never sent to the server. The link works, the "
                         "page loads, and the tagging is silently absent from every report."))
    return rows


def read_event(name: str, params: list[tuple[str, str]], key_event: bool) -> dict:
    row = event_row(name)
    required = [item for item in (row["required_params"].split(";") if row else []) if item]
    supplied = {key for key, _ in params}
    long_values = []
    for key, value in params:
        ceiling = PARAM_VALUE_MAX_BY_NAME.get(key, PARAM_VALUE_MAX)
        if len(value) > ceiling:
            long_values.append(f"{key} ({len(value)} > {ceiling})")
    return {
        "event_name": name,
        "known": row is not None,
        "registry_id": row["id"] if row else "",
        "stage": row["funnel_stage"] if row else "",
        "fires_when": row["fires_exactly_when"] if row else "",
        "not_proof_of": row["what_it_does_not_prove"] if row else "",
        "key_event": key_event,
        "charset_ok": bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name)),
        "reserved": name in RESERVED_EVENT_NAMES,
        "reserved_prefix": next((prefix for prefix in RESERVED_PREFIXES
                                 if name.startswith(prefix)), ""),
        "params": params,
        "param_count": len(params),
        "long_names": sorted(key for key, _ in params if len(key) > PARAM_NAME_MAX),
        "long_values": long_values,
        "reserved_params": sorted({key for key, _ in params if key in RESERVED_PARAM_NAMES
                                   and key not in STANDARD_ECOMMERCE_PARAMS}),
        "missing_required": [item for item in required if item not in supplied],
        "personal": personal_data(params),
    }


def event_gates(stats: dict) -> list[dict]:
    name = stats["event_name"]
    rows: list[dict] = []
    rows.append(_row("event-name-charset", stats["charset_ok"], "critical",
                     f"`{name}`", "starts with a letter, then letters, numbers and underscores",
                     "A space or a hyphen in an event name is not rejected loudly. The event is "
                     "dropped or renamed, and the first sign of it is a report with a gap in it."))
    rows.append(_row("event-name-length", len(name) <= EVENT_NAME_MAX, "high",
                     f"{len(name)} characters", f"<= {EVENT_NAME_MAX}",
                     "The documented ceiling. Past it the name is not accepted as given."))
    rows.append(_row("event-name-not-reserved", not stats["reserved"], "critical",
                     f"`{name}` is reserved" if stats["reserved"] else "not a reserved name",
                     "a name outside the reserved list",
                     "A reserved name collides with a built-in event. The number that comes back is "
                     "a mixture of yours and the platform's, and nothing in the interface says so."))
    rows.append(_row("event-name-prefix", not stats["reserved_prefix"], "critical",
                     f"reserved prefix `{stats['reserved_prefix']}`" if stats["reserved_prefix"]
                     else "prefix is free",
                     "not _, firebase_, ga_, google_ or gtag.",
                     "Reserved prefixes are dropped rather than renamed, so the event never arrives "
                     "and the tag reports success."))
    rows.append(_row("event-name-lowercase", name == name.lower(), "medium",
                     f"`{name}`", "lowercase with underscores",
                     "Event names are case sensitive, so `Add_To_Cart` and `add_to_cart` are two "
                     "different events in the same report. Only a convention prevents it, because "
                     "neither one is wrong."))
    if stats["key_event"]:
        rows.append(_row("key-event-name-margin", len(name) <= KEY_EVENT_NAME_SAFE, "low",
                         f"{len(name)} characters",
                         f"<= {KEY_EVENT_NAME_SAFE} for a key event",
                         "A key event gets two characters appended internally, and a name at the "
                         "documented 40-character limit loses them and stops being counted as a key "
                         "event. The two-character margin is not documented anywhere; it is the "
                         "arithmetic of the suffix, which is why this is a note and not a failure."))
    rows.append(_row("parameters-per-event", stats["param_count"] <= PARAMS_PER_EVENT_MAX, "high",
                     f"{stats['param_count']} "
                     f"parameter{'' if stats['param_count'] == 1 else 's'}",
                     f"<= {PARAMS_PER_EVENT_MAX}",
                     "Past the ceiling the surplus parameters are dropped, and which ones survive is "
                     "not something you get to choose."))
    rows.append(_row("parameter-name-length", not stats["long_names"], "high",
                     "too long: " + ", ".join(stats["long_names"]) if stats["long_names"]
                     else "all within limit", f"<= {PARAM_NAME_MAX} characters",
                     "Same failure mode as the event name, one level down."))
    rows.append(_row("parameter-value-length", not stats["long_values"], "high",
                     "truncated: " + ", ".join(stats["long_values"]) if stats["long_values"]
                     else "all within limit",
                     f"<= {PARAM_VALUE_MAX} characters, more for page_title, page_referrer "
                     "and page_location",
                     "A truncated value is worse than a missing one. It looks like data and groups "
                     "wrongly, and a long product name is the usual casualty."))
    rows.append(_row("parameter-name-not-reserved", not stats["reserved_params"], "critical",
                     "reserved: " + ", ".join(stats["reserved_params"]) if stats["reserved_params"]
                     else "no reserved names",
                     "no reserved parameter names",
                     "These cannot be registered as custom parameters, so the dimension never "
                     "appears and the data has nowhere to land. The ecommerce parameters the "
                     "platform recommends itself are exempt: sending `currency` on a purchase is "
                     "correct, registering a custom parameter called `currency` is not."))
    rows.append(_row("personal-data-in-parameters", not stats["personal"], "critical",
                     "; ".join(stats["personal"]) or "none found", "no personal data",
                     "Analytics tools prohibit personal data in their terms, and the platform cannot "
                     "delete what it does not know is there. This is the gate most often failed on "
                     "purpose, to make a report joinable."))
    if stats["known"]:
        rows.append(_row("required-parameters-for-this-event", not stats["missing_required"], "high",
                         "missing " + ", ".join(stats["missing_required"])
                         if stats["missing_required"] else "all present",
                         f"the required set in {EVENT_TABLE.name}",
                         "An event without its parameters is a count. The registry lists what turns "
                         "it back into a number somebody can act on."))
    return rows


def parse_pairs(text: str) -> list[tuple[str, str]]:
    pairs = []
    for chunk in text.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        key, _, value = chunk.partition("=")
        pairs.append((key.strip(), value.strip()))
    return pairs


def reconcile(reported: dict[str, float], analytics: float | None) -> dict:
    """The one honest number available on a platform-versus-analytics gap.

    Each platform reports the conversions it can claim, and a conversion touched by two platforms is
    claimed by both. So the sum across platforms is not a total of anything - it is a total of claims.
    When that sum exceeds what analytics counted, the excess is a lower bound on how many claims are
    duplicates or phantoms. Lower bound, because overlap can also hide inside a sum that happens to
    match, and because analytics undercounts for its own separate reasons.

    That is the whole calculation. It cannot say which platform is wrong, and this script does not
    guess: the structural causes are listed per platform in the windows table, and separating them
    needs both accounts open in front of a person.
    """
    total_claims = sum(reported.values())
    result = {"reported": dict(reported), "total_claims": round(total_claims, 2),
              "analytics": analytics}
    if analytics is None:
        result["minimum_double_counted"] = None
        result["minimum_share"] = None
        return result
    excess = max(0.0, total_claims - analytics)
    result["minimum_double_counted"] = round(excess, 2)
    result["minimum_share"] = round(excess / total_claims, 4) if total_claims else 0.0
    return result


def delivery_gap(purchases: float, delivered: float) -> dict:
    """Purchase events against delivered orders, which on cash on delivery are different numbers.

    A `purchase` event fires when an order is created. On cash on delivery the money arrives days
    later or not at all, so every efficiency figure computed on purchases is overstated by exactly the
    share that never got delivered. This is arithmetic on two numbers the business already has, and it
    is the largest correction most Vietnamese reports are missing.
    """
    if purchases <= 0:
        raise ValueError("purchases must be greater than zero")
    rate = delivered / purchases
    return {"purchases": purchases, "delivered": delivered,
            "delivery_rate": round(rate, 4),
            "overstatement": round(1 - rate, 4),
            "note": "Every return, cost-per-acquisition and revenue figure computed on purchase "
                    "events is overstated by this share. Multiply, or recompute on delivered."}


def report(sections: list[tuple[str, list[dict]]], extra: list[str] | None = None) -> str:
    lines: list[str] = ["# Tracking plan check", ""]
    total = 0
    for title, rows in sections:
        if not rows:
            continue
        total += blocking_count(rows)
        lines += [f"## {title}", "", "| Gate | Verdict | Severity | Observed | Target |",
                  "|---|---|---|---|---|"]
        for row in rows:
            lines.append(f"| {row['gate']} | {'pass' if row['pass'] else 'FAIL'} | "
                         f"{row['severity']} | {row['observed']} | {row['target']} |")
        lines.append("")
        failed = [row for row in rows if not row["pass"]]
        if failed:
            lines.append("### Why these matter")
            lines.append("")
            for row in failed:
                lines.append(f"- **{row['gate']}**: {row['why']}")
            lines.append("")
    lines += [f"Blocking failures: {total}", ""]
    if extra:
        lines += extra + [""]
    lines += ["## Not established by this run", ""]
    for item in ["Whether the tag actually fires. This reads strings, not a browser.",
                 "Whether the event is deduplicated in the destination. That is a server question.",
                 "Which platform is right when two disagree. The windows table lists the structural "
                 "causes; choosing between them needs both accounts open.",
                 "Whether the numbers already collected are usable. A convention fixed today does "
                 "not repair what was tagged last quarter, and both spellings stay in the report."]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def print_events() -> str:
    rows = load_table(EVENT_TABLE)
    lines = ["# Event registry", "",
             "| id | event | stage | fires exactly when | conversion |", "|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['id']} | `{row['event_name']}` | {row['funnel_stage']} | "
                     f"{row['fires_exactly_when']} | {row['counted_as_conversion']} |")
    lines += ["", f"{len(rows)} events. Each row also carries the required parameters, the "
              "deduplication key, the error it usually ships with, a Vietnam note and what the "
              "event does not prove.", ""]
    return "\n".join(lines)


def print_windows() -> str:
    rows = load_table(WINDOW_TABLE)
    lines = ["# Attribution windows and why the numbers disagree", "",
             "| platform | default click | default view | counted at | view-through included |",
             "|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['platform']} | {row['default_click_window']} | "
                     f"{row['default_view_window']} | {row['timestamp_basis']} | "
                     f"{row['view_through_in_default_number']} |")
    lines += ["", "`verify-in-account` is not a gap in the research. It means the vendor publishes no "
              "default for that setting, so the only true answer is the one in the account, and the "
              "row's `where_to_read_it` column says where to find it. A second token, "
              "`path-unpublished`, goes one worse: the vendor does not publish the screen either, so "
              "the row names a person to ask instead of a menu path it would have to invent.", ""]
    for row in rows:
        # The label matches the column name rather than reading "Read it at path-unpublished", which
        # is what it said before Lazada arrived with no readable screen to name. Some cells are one
        # sentence and some are four, so the full stop is added here rather than assumed either way.
        where = row["where_to_read_it"].rstrip(" .")
        lines.append(f"- **{row['platform']}**: {row['why_it_disagrees_with_analytics']} "
                     f"Where to read it: {where}. "
                     f"Source: {row['vendor_page']}")
    return "\n".join(lines) + "\n"


def print_rules() -> str:
    lines = ["# Enforced limits", "",
             "Read off vendor documentation on 2026-07-31. Google publishes no last-updated date on "
             "its help pages, so that is the date it was checked and nothing more. Re-read before "
             "quoting any of it.", "",
             "| Rule | Value |", "|---|---|",
             f"| Event name length | <= {EVENT_NAME_MAX} characters |",
             "| Event name charset | starts with a letter, then letters, numbers, underscores |",
             f"| Parameters per event | <= {PARAMS_PER_EVENT_MAX} |",
             f"| Parameter name length | <= {PARAM_NAME_MAX} characters |",
             f"| Parameter value length | <= {PARAM_VALUE_MAX}, "
             + ", ".join(f"{key} {value}" for key, value in PARAM_VALUE_MAX_BY_NAME.items()) + " |",
             f"| Key-event name margin | <= {KEY_EVENT_NAME_SAFE}, inferred from the appended _c |",
             f"| Reserved event names | {len(RESERVED_EVENT_NAMES)} web-stream names |",
             f"| Reserved prefixes | {', '.join(RESERVED_PREFIXES)} |",
             f"| Campaign name segments | >= {CAMPAIGN_SEGMENTS_MIN}, one of them yyyymm |", "",
             "## Media that route to a channel", "",
             "Medium side only. Google also routes on source, against site lists it publishes as a "
             "spreadsheet rather than as text, and the medium is the half you control.", ""]
    for pattern, channel in CHANNEL_BY_MEDIUM:
        lines.append(f"- `{pattern.pattern}` routes to {channel}")
    lines += ["", "Channel definitions ignore case. Reported values do not. A medium of `CPC` is "
              "classified as paid and still arrives as its own row.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--url", help="one tagged URL to check")
    source.add_argument("--urls", metavar="FILE", help="a file of tagged URLs, one per line")
    source.add_argument("--event", metavar="NAME", help="an event name to check")
    source.add_argument("--reconcile", metavar="PAIRS",
                        help="platform-reported conversions, as name=count,name=count")
    source.add_argument("--events", action="store_true", help="print the event registry")
    source.add_argument("--windows", action="store_true", help="print the attribution table")
    source.add_argument("--rules", action="store_true", help="print the enforced limits")
    parser.add_argument("--params", default="", help="event parameters, as key=value,key=value")
    parser.add_argument("--key-event", action="store_true", help="the event is marked a key event")
    parser.add_argument("--analytics", type=float, help="the analytics total, for --reconcile")
    parser.add_argument("--purchases", type=float, help="purchase events in the period")
    parser.add_argument("--delivered", type=float, help="delivered orders in the same period")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--output", help="write here instead of stdout")
    args = parser.parse_args(argv)

    if args.rules:
        emit(print_rules(), args.output)
        return 0
    if args.events:
        emit(print_events(), args.output)
        return 0
    if args.windows:
        emit(print_windows(), args.output)
        return 0

    if args.reconcile:
        pairs = parse_pairs(args.reconcile)
        try:
            reported = {key: float(value) for key, value in pairs}
        except ValueError:
            parser.error("--reconcile takes name=count pairs, for example meta=120,google=80")
        result = reconcile(reported, args.analytics)
        if args.json:
            emit_json(result, args.output)
            return 0
        lines = ["# Reconciliation", "",
                 f"Platform claims total {result['total_claims']:g} across "
                 f"{len(reported)} platforms."]
        if result["minimum_double_counted"] is None:
            lines.append("No analytics total given, so there is nothing to compare and no floor to "
                         "compute. Pass --analytics.")
        else:
            lines += [f"Analytics counted {result['analytics']:g}.", "",
                      f"At least {result['minimum_double_counted']:g} claims "
                      f"({result['minimum_share'] * 100:.1f} percent) are counted twice or are not "
                      "there. That is a floor, not an estimate: overlap can also hide inside a sum "
                      "that happens to match, and analytics undercounts for its own reasons.", "",
                      "This does not say which platform is wrong. Run --windows for the structural "
                      "causes, then open both accounts."]
        emit("\n".join(lines) + "\n", args.output)
        return 0

    if args.purchases is not None or args.delivered is not None:
        if args.purchases is None or args.delivered is None:
            parser.error("--purchases and --delivered are only meaningful together")
        result = delivery_gap(args.purchases, args.delivered)
        if args.json:
            emit_json(result, args.output)
            return 0
        emit("\n".join([
            "# Orders placed against orders delivered", "",
            f"{result['delivered']:g} delivered out of {result['purchases']:g} ordered, a delivery "
            f"rate of {result['delivery_rate'] * 100:.1f} percent.", "",
            f"Every figure computed on purchase events is overstated by "
            f"{result['overstatement'] * 100:.1f} percent. {result['note']}", "",
            "On cash on delivery a purchase event is an order request. The money arrives days later "
            "or not at all, and the campaign that produced the most requests is not always the one "
            "that produced the most revenue.", ""]), args.output)
        return 0

    sections: list[tuple[str, list[dict]]] = []
    event_stats: dict | None = None
    if args.url or args.urls:
        urls = [args.url] if args.url else [line.strip() for line
                                            in Path(args.urls).read_text(encoding="utf-8").splitlines()
                                            if line.strip() and not line.startswith("#")]
        for url in urls:
            stats = read_url(url)
            title = f"URL: {stats['host'] or url}"
            if stats["campaign"]:
                title += f" ({stats['campaign']})"
            sections.append((title, url_gates(stats)))
    elif args.event:
        event_stats = read_event(args.event, parse_pairs(args.params), args.key_event)
        sections.append((f"Event: {args.event}"
                         + ("" if event_stats["known"] else " (not in the registry)"),
                         event_gates(event_stats)))
    else:
        parser.error("give --url, --urls, --event, --reconcile, --purchases with --delivered, "
                     "--events, --windows or --rules")

    extra: list[str] = []
    if event_stats is not None:
        if event_stats["known"]:
            extra = ["## What the registry says about this event", "",
                     f"- Fires: {event_stats['fires_when']}.",
                     f"- Does not prove: {event_stats['not_proof_of']}."]
        else:
            extra = ["## Not in the registry", "",
                     f"- `{args.event}` was checked against the platform rules only. Add it to "
                     f"{EVENT_TABLE.name} with the moment it fires and what it does not prove, or "
                     "the next person will define it differently."]

    rows = [row for _, section in sections for row in section]
    if args.json:
        emit_json({"sections": [{"title": title, "gates": section} for title, section in sections],
                   "blocking": blocking_count(rows)}, args.output)
    else:
        emit(report(sections, extra), args.output)
    return 2 if blocking_count(rows) else 0


if __name__ == "__main__":
    from _emit import run_gate
    run_gate(main)
