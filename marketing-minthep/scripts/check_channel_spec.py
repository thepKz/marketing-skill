#!/usr/bin/env python3
"""Check one finished asset against what a placement actually documents.

The failure this exists for is cheap and constant: a shoot is exported once, at one size, and
posted everywhere. It looks fine in the editor and then Facebook crops the price out of a 1:1
because Feed wants 4:5, or Instagram takes the video at 9:16 while the still beside it went out
at 4:5, or a 30-second Reel is rejected for a minimum width that only applies at 30 seconds and
over. None of that is a taste problem and none of it shows up until after the money is spent.

Three statuses, and they mean different things on purpose:

  failed   The page documents a requirement and this asset breaks it. The upload gets rejected
           or the crop gets taken out of your hands.
  review   Either the page documents a *recommendation* and the asset is outside it, or the page
           documents nothing at all. Both need a human, and for opposite reasons.
  passed   The page documents a requirement and the asset clears it.

The distinction that matters most is between the two kinds of review. Meta publishes copy budgets
under "Đề xuất về văn bản" - a recommendation - and pixel floors under "Yêu cầu kỹ thuật" - a
requirement. A tool that failed an asset for a 46-character caption on Instagram Reels would be
lying about who rejects what. And four Meta placements carry no technical block whatsoever: no
file ceiling, no minimum width, no tolerance. That silence is not permission. The uploader still
rejects something; the number simply is not published, so this reports `review` and never `passed`.

data/channel-specs.csv encodes that with three tokens rather than with an empty cell, because an
empty cell reads as a gap somebody forgot to fill:

  undocumented    the page carries no such figure
  unlimited       the page states there is no limit, which is a fact and not an absence
  not-applicable  the field does not exist on this surface - no headline slot, no duration on a still

Usage:
    python check_channel_spec.py --placement meta-facebook-feed-image \\
        --width 1080 --height 1080 --file-size 4MB --format jpg
    python check_channel_spec.py --placement meta-instagram-reels-video \\
        --width 1080 --height 1920 --duration 28 --file-size 60MB --format mp4
    python check_channel_spec.py --survey --width 1080 --height 1920 --duration 22 --format mp4
    python check_channel_spec.py --list-placements
    python check_channel_spec.py --show meta-facebook-feed-image
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import pathlib
import re
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "channel-specs.csv"

UNDOCUMENTED = "undocumented"
UNLIMITED = "unlimited"
NOT_APPLICABLE = "not-applicable"
PER_PLACEMENT = "per-placement"

# How long a row is trusted before it has to be re-read off the page. Ninety days is not a
# platform figure - none of them publishes one - it is a bet, and the bet has already been settled
# once: a Shopee help article cited by an earlier version of this unit returned 404 within a few
# months of being read. The number is here rather than inside the freshness gate so that changing
# it is a visible decision.
STALE_AFTER_DAYS = 90

# 1024, stated rather than assumed. Meta writes "30MB" and Google writes "150KB" and neither says
# which base it means, so the tighter reading is used: at 1024 a 30MB ceiling is 31457280 bytes,
# and an asset that clears this check clears the other reading too.
UNITS = {"B": 1, "KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3}
SIZE = re.compile(r"^\s*([\d.]+)\s*(B|KB|MB|GB)\s*$", re.I)


def parse_size(text: str) -> int:
    """"30MB" -> bytes. Raises rather than guessing, because a silently mis-parsed ceiling passes
    everything."""
    match = SIZE.match(text)
    if not match:
        raise ValueError(f"cannot read {text!r} as a file size; write it like 30MB, 500KB or 4GB")
    return int(float(match.group(1)) * UNITS[match.group(2).upper()])


def human_size(size_bytes: int) -> str:
    for unit in ("GB", "MB", "KB"):
        if size_bytes >= UNITS[unit]:
            value = size_bytes / UNITS[unit]
            return f"{value:.1f}".rstrip("0").rstrip(".") + unit
    return f"{size_bytes}B"


def parse_duration(text: str) -> float:
    """Seconds, or mm:ss. A colon is accepted because that is how an editor displays a timeline
    and retyping it as seconds is where an arithmetic slip gets in."""
    text = text.strip()
    if ":" in text:
        parts = [float(p) for p in text.split(":")]
        if len(parts) > 3:
            raise ValueError(f"cannot read {text!r} as a duration")
        seconds = 0.0
        for part in parts:
            seconds = seconds * 60 + part
        return seconds
    return float(text)


def load_rows() -> list[dict]:
    with DATA.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def resolve(key: str, rows: list[dict]) -> dict:
    wanted = key.strip().lower()
    for row in rows:
        if row["key"] == wanted:
            return row
    # A near miss is the common case - somebody typed the surface without the asset type, which is
    # exactly the mistake that produces one export for a still and a video.
    near = [row["key"] for row in rows if wanted in row["key"] or row["key"].startswith(wanted)]
    hint = f"; did you mean {', '.join(near)}?" if near else ""
    raise ValueError(f"unknown placement {key!r}{hint} Run --list-placements for all "
                     f"{len(rows)} keys.")


def gate(name: str, status: str, detail: str) -> dict:
    return {"gate": name, "status": status, "detail": detail}


def ratio_of(width: int, height: int) -> float:
    return width / height


def declared_ratio(text: str) -> float | None:
    if ":" not in text:
        return None
    left, right = text.split(":", 1)
    return float(left) / float(right)


def named_ratios() -> list[str]:
    """Every ratio this table declares anywhere, e.g. 4:5, 9:16, 1:1, 16:9."""
    return sorted({row["ratio"] for row in load_rows() if ":" in row["ratio"]})


def nearest_named_ratio(actual: float) -> str | None:
    candidates = named_ratios()
    if not candidates:
        return None
    return min(candidates, key=lambda text: abs(actual - declared_ratio(text)) / declared_ratio(text))


def check_ratio(row: dict, width: int | None, height: int | None) -> dict:
    name = "aspect-ratio"
    if width is None or height is None:
        return gate(name, "skipped", "No dimensions given, so there is no ratio to compare.")
    declared = row["ratio"]
    if declared == UNLIMITED:
        return gate(name, "passed",
                    f"{row['surface']} documents no ratio restriction on this format, because the "
                    f"ad is an organic post rather than an upload. Whatever the post already is, is "
                    f"acceptable.")
    if declared == PER_PLACEMENT:
        return gate(name, "review",
                    f"This surface is not ratio-driven: every placement has its own exact pixel "
                    f"size and the page tabulates them. {width}x{height} has to be matched against "
                    f"that table, not against a ratio, and one master will not scale down to the "
                    f"whole set.")
    target = declared_ratio(declared)
    if target is None:
        return gate(name, "review", f"The row records the ratio as {declared!r}, which this check "
                                    f"cannot compare arithmetically. Read the page.")
    actual = ratio_of(width, height)
    drift = abs(actual - target) / target * 100
    tolerance = row["ratio_tolerance_pct"]

    # Where no tolerance is published there is still a fact to check, and it is not a threshold:
    # whether these dimensions are some *other* ratio the table names. 1080x1920 against a
    # placement documenting 4:5 is not a file inside an unpublished tolerance, it is exactly 9:16 -
    # a ratio this table names on eleven other rows. Reporting that as an open question because
    # Meta's video pages omit the tolerance column would be the check hiding behind a missing cell
    # while the crop happens anyway. The comparison uses ratios already in the file, so no figure
    # is borrowed from one vendor's page and applied to another's.
    nearest = nearest_named_ratio(actual)
    if nearest and nearest != declared:
        return gate(name, "failed",
                    f"{width}x{height} is {nearest}, and this placement documents {declared}. That "
                    f"is not a tolerance question, it is a different ratio - off by {drift:.0f} per "
                    f"cent. Something gets cut and the platform decides what, which in practice "
                    f"means the top and bottom of a vertical frame: the plate at one end and the "
                    f"price at the other. Export a {declared} version from the master.")

    if tolerance == UNDOCUMENTED:
        if drift < 0.01:
            return gate(name, "passed",
                        f"{width}x{height} is exactly {declared}. No tolerance is published for "
                        f"this placement, and an exact match does not need one.")
        return gate(name, "review",
                    f"{width}x{height} is {drift:.1f} per cent off {declared}, nearer to it than to "
                    f"any other ratio on the table, and no tolerance is published here to measure "
                    f"that against. Export at {declared} and the question does not arise.")
    allowed = float(tolerance)
    if drift > allowed:
        return gate(name, "failed",
                    f"{width}x{height} is {drift:.1f} per cent off {declared}, past the documented "
                    f"tolerance of {allowed} per cent. The platform will crop this to fit, and it "
                    f"crops from the edges - which is where the price, the logo and the call to "
                    f"action usually sit. Export at {declared} instead.")
    return gate(name, "passed",
                f"{width}x{height} is within {drift:.1f} per cent of {declared}, inside the "
                f"documented {allowed} per cent tolerance.")


def check_resolution(row: dict, width: int | None, height: int | None) -> dict:
    name = "minimum-resolution"
    if width is None or height is None:
        return gate(name, "skipped", "No dimensions given.")
    findings, verdict = [], "passed"
    for axis, value, field in (("width", width, "min_width"), ("height", height, "min_height")):
        floor = row[field]
        if floor == NOT_APPLICABLE:
            continue
        if floor == UNLIMITED:
            findings.append(f"no minimum {axis} is imposed on this format")
            continue
        if floor == UNDOCUMENTED:
            findings.append(f"no minimum {axis} is published")
            verdict = "review" if verdict == "passed" else verdict
            continue
        if value < int(floor):
            findings.append(f"{axis} {value} is below the documented floor of {floor}")
            verdict = "failed"
        else:
            findings.append(f"{axis} {value} clears the documented floor of {floor}")
    if not findings:
        return gate(name, "skipped", "Resolution floors do not apply to this format.")
    detail = "; ".join(findings) + "."
    if verdict == "failed":
        detail += (" A file under the floor is refused at upload, so this is not a quality note. "
                   f"The page also recommends {row['rec_width']}x{row['rec_height']}"
                   if row["rec_width"] != UNDOCUMENTED else
                   " A file under the floor is refused at upload, so this is not a quality note")
        detail = detail.rstrip(".") + "."
    elif verdict == "review":
        detail += (" Silence here is not permission - the uploader still refuses something, the "
                   "figure is simply not published on this page.")
    return gate(name, verdict, detail)


def check_recommended_size(row: dict, width: int | None, height: int | None) -> dict:
    name = "recommended-size"
    if width is None or height is None:
        return gate(name, "skipped", "No dimensions given.")
    rec_w, rec_h = row["rec_width"], row["rec_height"]
    if rec_w in (UNDOCUMENTED, NOT_APPLICABLE):
        return gate(name, "skipped", "No recommended size is published for this placement.")
    rec_w, rec_h = int(rec_w), int(rec_h)
    if width >= rec_w and height >= rec_h:
        return gate(name, "passed",
                    f"{width}x{height} meets or beats the recommended {rec_w}x{rec_h}.")
    short = [axis for axis, value, target in (("width", width, rec_w), ("height", height, rec_h))
             if value < target]
    return gate(name, "review",
                f"{width}x{height} against a recommended {rec_w}x{rec_h}, short on "
                f"{' and '.join(short)}. A recommendation is not a rejection threshold, so this "
                f"uploads - it just gets upscaled by the platform for anyone on a dense screen, and "
                f"upscaling shows first on skin and on small type. Re-export from the master if "
                f"there is one.")


def check_file_size(row: dict, size_bytes: int | None) -> dict:
    name = "file-size"
    if size_bytes is None:
        return gate(name, "skipped", "No file size given.")
    ceiling = row["max_file"]
    if ceiling == NOT_APPLICABLE:
        return gate(name, "skipped", "No file is uploaded on this format.")
    if ceiling == UNLIMITED:
        return gate(name, "passed",
                    "This format documents no file-size ceiling, because the asset is an existing "
                    "post rather than an upload.")
    if ceiling == UNDOCUMENTED:
        return gate(name, "review",
                    f"{human_size(size_bytes)}, against no published ceiling for this placement. "
                    f"Four Meta placements are like this - a recommendation and no technical block "
                    f"at all. Keep the file small anyway: the cost of a heavy asset lands on a "
                    f"viewer on mobile data, not on the uploader.")
    limit = parse_size(ceiling)
    if size_bytes > limit:
        return gate(name, "failed",
                    f"{human_size(size_bytes)} against a documented ceiling of {ceiling} "
                    f"({limit} bytes at 1024). Re-encode rather than re-crop: the dimensions are "
                    f"usually not the problem, the bitrate is.")
    share = size_bytes / limit * 100
    return gate(name, "passed",
                f"{human_size(size_bytes)} against a documented ceiling of {ceiling}, "
                f"{share:.0f} per cent of it.")


def check_duration(row: dict, seconds: float | None) -> dict:
    name = "duration"
    lower, upper = row["duration_min_s"], row["duration_max_s"]
    if lower == NOT_APPLICABLE and upper == NOT_APPLICABLE:
        return gate(name, "skipped", "A still has no duration.")
    if seconds is None:
        return gate(name, "skipped", "No duration given.")
    if upper == UNLIMITED:
        floor = f" The documented floor is {lower}s." if lower not in (UNDOCUMENTED,
                                                                      NOT_APPLICABLE) else ""
        return gate(name, "passed",
                    f"{seconds:g}s, and this placement documents no maximum length.{floor} That is "
                    f"a stated absence of a limit, not a silence - which is worth knowing, because "
                    f"the still variant of this same surface publishes nothing at all.")
    if upper == UNDOCUMENTED:
        return gate(name, "review",
                    f"{seconds:g}s, against no published maximum for this placement. Read the page "
                    f"before committing an edit longer than a minute.")
    ceiling = float(upper)
    if seconds > ceiling:
        return gate(name, "failed",
                    f"{seconds:g}s against a documented maximum of {ceiling:g}s. This is a format "
                    f"boundary rather than a preference: over the line it is a different ad "
                    f"product, bought differently.")
    if lower not in (UNDOCUMENTED, NOT_APPLICABLE) and seconds < float(lower):
        return gate(name, "failed",
                    f"{seconds:g}s against a documented minimum of {float(lower):g}s.")
    return gate(name, "passed",
                f"{seconds:g}s, inside the documented range up to {ceiling:g}s.")


def check_format(row: dict, container: str | None) -> dict:
    name = "file-format"
    if container is None:
        return gate(name, "skipped", "No file format given.")
    declared = row["file_formats"]
    if declared in (UNDOCUMENTED, NOT_APPLICABLE):
        return gate(name, "review",
                    f"No accepted format list is published on this page. On YouTube surfaces that "
                    f"is because the file is an ordinary YouTube upload first and the ad product "
                    f"points at it afterwards, so the constraint lives on a different page.")
    if declared == UNLIMITED:
        return gate(name, "passed", "This format documents no file-type restriction.")
    accepted = [item.strip().lower() for item in declared.split("|")]
    given = container.strip().lower().lstrip(".")
    aliases = {"jpeg": "jpg", "m4v": "mp4", "quicktime": "mov", "tif": "tiff"}
    given = aliases.get(given, given)
    if given in accepted:
        return gate(name, "passed", f".{given} is on the documented list ({declared}).")
    return gate(name, "failed",
                f".{given} is not on the documented list ({declared}). Remux rather than "
                f"re-render if the codec inside is already right - it costs no quality.")


def check_copy(row: dict, field: str, label: str, text: str | None) -> dict:
    name = f"{label}-length"
    budget = row[field]
    if budget == NOT_APPLICABLE:
        if text:
            return gate(name, "review",
                        f"{len(text)} characters of {label} supplied, and this surface documents no "
                        f"{label} field at all. Whatever you wrote has nowhere to go here - fold it "
                        f"into the copy that does have a slot, or it is lost.")
        return gate(name, "skipped", f"This surface has no {label} field.")
    if text is None:
        return gate(name, "skipped", f"No {label} given.")
    if budget == UNDOCUMENTED:
        return gate(name, "review",
                    f"{len(text)} characters, against no published budget for this surface.")
    limit = int(budget)
    if len(text) > limit:
        return gate(name, "review",
                    f"{len(text)} characters against a recommended {limit}. This is a "
                    f"recommendation, not a rejection threshold - the post will publish and then "
                    f"truncate on a phone, which puts your ellipsis wherever the layout wants it "
                    f"rather than after a finished thought. Say it in {limit} or move the tail to "
                    f"the first comment.")
    return gate(name, "passed",
                f"{len(text)} characters inside the recommended {limit}, {limit - len(text)} spare.")


def check_freshness(row: dict, today: dt.date) -> dict:
    name = "row-freshness"
    read_on = dt.date.fromisoformat(row["retrieved"])
    age = (today - read_on).days
    if age < 0:
        return gate(name, "review",
                    f"This row is dated {row['retrieved']}, which is in the future. Somebody's "
                    f"clock is wrong, and until it is fixed the date cannot be trusted as evidence.")
    if age > STALE_AFTER_DAYS:
        return gate(name, "review",
                    f"Read off the page on {row['retrieved']}, {age} days ago, past the "
                    f"{STALE_AFTER_DAYS}-day trust window. Nothing here is wrong yet and nothing "
                    f"here is confirmed either. Open {row['source_url']} and re-read the technical "
                    f"block before you spend on this placement. Platform help pages move without "
                    f"notice: a Shopee article cited by an earlier version of this unit now returns "
                    f"404.")
    return gate(name, "passed",
                f"Read off the page on {row['retrieved']}, {age} days ago, inside the "
                f"{STALE_AFTER_DAYS}-day trust window.")


def build(placement: str, width=None, height=None, duration=None, file_size=None,
          container=None, primary_text=None, headline=None, today=None) -> dict:
    rows = load_rows()
    row = resolve(placement, rows)
    today = today or dt.date.today()
    size_bytes = parse_size(file_size) if file_size else None
    seconds = parse_duration(duration) if duration is not None else None

    gates = [
        check_ratio(row, width, height),
        check_resolution(row, width, height),
        check_recommended_size(row, width, height),
        check_file_size(row, size_bytes),
        check_duration(row, seconds),
        check_format(row, container),
        check_copy(row, "primary_text_chars", "primary-text", primary_text),
        check_copy(row, "headline_chars", "headline", headline),
        check_freshness(row, today),
    ]
    failed = [item for item in gates if item["status"] == "failed"]
    review = [item for item in gates if item["status"] == "review"]
    if failed:
        status = "failed"
        summary = (f"{len(failed)} documented requirement(s) broken. Each one is a rejection or a "
                   f"crop taken out of your hands, not a matter of taste.")
    elif review:
        status = "review"
        summary = (f"Nothing documented is broken, but {len(review)} check(s) rest on something "
                   f"the page does not publish, or on a recommendation rather than a rule. Decide "
                   f"those by reading the page, not by trusting this table.")
    else:
        status = "passed"
        summary = (f"The asset is consistent with everything {row['platform']} documents for "
                   f"{row['surface']}.")

    return {
        "placement": row["key"],
        "platform": row["platform"],
        "surface": row["surface"],
        "asset": row["asset"],
        "source_url": row["source_url"],
        "retrieved": row["retrieved"],
        "caveat": row["caveat"],
        "safe_zone": row["safe_zone"],
        "gates": gates,
        "verdict": {"status": status, "summary": summary},
    }


def survey(width=None, height=None, duration=None, file_size=None, container=None,
           today=None) -> dict:
    """One asset against every placement, which is the question a one-person marketer actually has.

    They do not have a placement in mind and an asset to validate. They have one file, shot once,
    and a week of posting to fill - so the useful answer is the list of surfaces it can go on
    untouched, and the list where it will be cropped.

    Two states here rather than the report's three, and the difference is deliberate. A `review` in
    the report means the page publishes nothing, or publishes a recommendation this asset is under.
    Neither stops the post going up. Carried into a 24-row list they drown the answer: an ordinary
    1080x1920 export is below Meta's recommended 1440x2560 on every vertical surface, so eleven rows
    would come back yellow and the reader would stop reading all of them. Only a broken requirement
    refuses a file, so only that is `refused` here. The open questions are counted rather than
    described, and the per-placement report is where they get read.
    """
    results = []
    for row in load_rows():
        report = build(row["key"], width, height, duration, file_size, container, today=today)
        broken = [item["detail"] for item in report["gates"] if item["status"] == "failed"]
        results.append({"placement": row["key"],
                        "status": "refused" if broken else "clear",
                        "reasons": broken,
                        "open_questions": sum(1 for item in report["gates"]
                                              if item["status"] == "review")})
    results.sort(key=lambda item: (item["status"] != "clear", item["open_questions"],
                                   item["placement"]))
    return {"results": results,
            "counts": {name: sum(1 for item in results if item["status"] == name)
                       for name in ("clear", "refused")}}


def as_text(report: dict) -> str:
    lines = [f"CHANNEL SPEC CHECK: {report['placement']}",
             f"{report['platform']} / {report['surface']} / {report['asset']}",
             f"Source: {report['source_url']} (read {report['retrieved']})",
             ""]
    for item in report["gates"]:
        lines.append(f"[{item['status']}]".ljust(10) + item["gate"])
        lines.append("           " + item["detail"])
        lines.append("")
    if report["safe_zone"] != UNDOCUMENTED:
        lines.append(f"SAFE ZONE  {report['safe_zone']}")
        lines.append("")
    lines.append(f"WORTH KNOWING  {report['caveat']}")
    lines.append("")
    lines.append(f"VERDICT {report['verdict']['status']}: {report['verdict']['summary']}")
    return "\n".join(lines)


def survey_as_text(report: dict) -> str:
    counts = report["counts"]
    lines = [f"ONE ASSET AGAINST {sum(counts.values())} PLACEMENTS: {counts['clear']} will take it "
             f"as it is, {counts['refused']} would crop or refuse it", ""]
    for item in report["results"]:
        open_note = f"  ({item['open_questions']} unpublished figure(s))" \
            if item["open_questions"] else ""
        lines.append(f"[{item['status']}]".ljust(10) + item["placement"] + open_note)
        for reason in item["reasons"]:
            lines.append("           " + reason)
    lines.append("")
    lines.append("A clear row means nothing documented is broken. Where a figure is unpublished it "
                 "is counted, not assumed - run --placement on that key to read what is missing.")
    return "\n".join(lines)


def list_placements() -> str:
    rows = load_rows()
    lines = [f"{'KEY':<34}{'RATIO':<15}{'MIN W/H':<16}{'MAX FILE':<10}{'MAX SEC':<9}READ"]
    for row in rows:
        floors = f"{row['min_width']}/{row['min_height']}"
        lines.append(f"{row['key']:<34}{row['ratio']:<15}{floors[:15]:<16}"
                     f"{row['max_file'][:9]:<10}{row['duration_max_s'][:8]:<9}{row['retrieved']}")
    lines.append("")
    lines.append(f"{len(rows)} placements. 'undocumented' means the page publishes no such figure, "
                 f"'unlimited' means it states there is none, 'not-applicable' means the field does "
                 f"not exist on that surface. The three are not interchangeable.")
    lines.append("Surfaces with no row: Shopee, TikTok Shop Vietnam, Zalo and Lazada, whose spec "
                 "pages are unreadable without an account. See references/channel-spec-registry.md "
                 "for what was tried and what each one returned.")
    return "\n".join(lines)


def show(placement: str) -> str:
    row = resolve(placement, load_rows())
    width = max(len(field) for field in row)
    lines = []
    for field, value in row.items():
        lines.append(f"{field:<{width}}  {value}")
    return "\n".join(lines)


def _raises(thunk) -> bool:
    try:
        thunk()
    except ValueError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--placement")
    parser.add_argument("--survey", action="store_true",
                        help="check one asset against every placement at once")
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--duration", help="seconds, or mm:ss")
    parser.add_argument("--file-size", help="e.g. 4MB, 800KB, 1.2GB")
    parser.add_argument("--format", dest="container", help="container extension, e.g. mp4, jpg")
    parser.add_argument("--primary-text")
    parser.add_argument("--headline")
    parser.add_argument("--output-format", choices=("text", "json"), default="text")
    parser.add_argument("--output")
    parser.add_argument("--list-placements", action="store_true")
    parser.add_argument("--show", metavar="PLACEMENT")
    args = parser.parse_args()

    if args.list_placements:
        print(list_placements())
        return 0
    if args.show:
        try:
            print(show(args.show))
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        return 0

    try:
        if args.survey:
            report = survey(args.width, args.height, args.duration, args.file_size,
                            args.container)
            content = json.dumps(report, indent=2, ensure_ascii=False) \
                if args.output_format == "json" else survey_as_text(report)
            status = "failed" if report["counts"]["clear"] == 0 else "passed"
        else:
            if not args.placement:
                parser.error("supply --placement, or --survey to check every placement at once")
            report = build(args.placement, args.width, args.height, args.duration,
                           args.file_size, args.container, args.primary_text, args.headline)
            content = json.dumps(report, indent=2, ensure_ascii=False) \
                if args.output_format == "json" else as_text(report)
            status = report["verdict"]["status"]
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.output:
        pathlib.Path(args.output).write_text(content + "\n", encoding="utf-8")
    else:
        print(content)
    return {"passed": 0, "failed": 2, "review": 3, "skipped": 3}[status]


if __name__ == "__main__":
    from _emit import run_gate
    run_gate(main)
