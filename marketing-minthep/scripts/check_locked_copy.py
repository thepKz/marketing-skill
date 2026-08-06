#!/usr/bin/env python3
"""Verify that every string the user supplied renders verbatim on the artifact.

Why a script: the failure it catches is invisible to the writer. When a request hands over dish
names, prices, a headline or a phone number, the model treats them as a draft to improve, and its
own rewrite lands on the artifact - "tạo A nhưng nó tạo B". Rereading the artifact proves nothing,
because the rewrite reads well; only a character-level diff against the supplied strings does.

    python scripts/check_locked_copy.py --artifact menu.html --lock "Bún bò tái 55.000đ"
    python scripts/check_locked_copy.py --artifact menu.html --locks supplied.txt
    python scripts/check_locked_copy.py --self-check

`--locks` reads one supplied string per line; blank lines and lines opening with `#` are skipped.
Matching is exact after NFC normalisation and whitespace collapse, so a lock may span markup - a
menu row split across two table cells still matches - but a changed diacritic, a reworded name or
a reformatted price does not, and the report prints the nearest passage that rendered in its place.
Case-sensitive on purpose: check the source text, because CSS `text-transform` changes the render
without changing the copy. Exit 1 when any lock is missing, so a run can be gated on it.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _emit import emit, use_utf8_stdout  # noqa: E402


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def visible_text(text: str) -> str:
    """The artifact reduced to the words a reader sees, markup replaced by spaces."""
    if re.search(r"<\s*(!doctype|html|body|svg|div|section|p|h[1-6]|text|td|li)\b", text, re.IGNORECASE):
        text = re.sub(r"<(script|style)\b.*?</\1\s*>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
    return normalise(text)


def nearest_passage(lock: str, haystack: str) -> str:
    """The stretch of the artifact most like the missing lock - what rendered in its place."""
    words = haystack.split()
    span = max(len(lock.split()), 1)
    best_start, best_width, best_ratio = 0, span, 0.0
    for width in {span, span + 2, max(span - 1, 1)}:
        for start in range(0, max(len(words) - width + 1, 1)):
            candidate = " ".join(words[start : start + width])
            ratio = SequenceMatcher(None, lock, candidate).ratio()
            if ratio > best_ratio:
                best_start, best_width, best_ratio = start, width, ratio
    if best_ratio < 0.4:
        return ""
    # Three words of context each side, so an embellished rewrite shows its embellishment.
    return " ".join(words[max(best_start - 3, 0) : best_start + best_width + 3])


def check(artifact_text: str, locks: list[str]) -> list[dict]:
    haystack = visible_text(artifact_text)
    results = []
    for raw in locks:
        lock = normalise(raw)
        if not lock:
            continue
        found = lock in haystack
        results.append(
            {
                "lock": lock,
                "found": found,
                "instead": "" if found else nearest_passage(lock, haystack),
            }
        )
    return results


def self_check() -> None:
    page = (
        "<html><body><h1>Nhiều ưu đãi tháng 8</h1>"
        "<table><tr><td>Bún bò tái chín</td><td>55.000đ</td></tr>"
        "<tr><td>Cà phê   sữa</td>\n<td>25.000đ</td></tr></table>"
        "<p>Gọi 0901 234 567 &amp; đặt bàn</p></body></html>"
    )
    # A lock spanning two table cells, one with collapsed whitespace, one crossing an entity.
    clean = check(page, ["Bún bò tái chín 55.000đ", "Cà phê sữa 25.000đ", "Gọi 0901 234 567 & đặt bàn"])
    assert all(row["found"] for row in clean), clean
    # The rewrite failure: same dish, embellished. Must fail and name what rendered instead.
    rewritten = check(
        "<html><body><td>Bún bò tái chín — nước dùng đậm đà</td><td>55K</td></body></html>",
        ["Bún bò tái chín 55.000đ"],
    )
    assert not rewritten[0]["found"] and "nước dùng" in rewritten[0]["instead"], rewritten
    # One dropped diacritic is a different word, not a near miss.
    broken = check("<h1>Nhiêu ưu đãi tháng 8</h1>", ["Nhiều ưu đãi tháng 8"])
    assert not broken[0]["found"], broken
    # Plain-text artifacts are checked as-is, angle brackets in prose left alone.
    assert check("Giá <combo> là 99.000đ", ["Giá <combo> là 99.000đ"])[0]["found"]
    emit("self-check passed")


def main() -> int:
    use_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--artifact", help="the rendered file: HTML, SVG, markdown, or plain text")
    parser.add_argument("--lock", action="append", default=[], help="one supplied string; repeatable")
    parser.add_argument("--locks", help="file with one supplied string per line")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()

    if args.self_check:
        self_check()
        return 0
    if not args.artifact or not (args.lock or args.locks):
        parser.error("--artifact plus --lock or --locks is required")

    locks = list(args.lock)
    if args.locks:
        for line in Path(args.locks).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                locks.append(line)

    results = check(Path(args.artifact).read_text(encoding="utf-8"), locks)
    missing = [row for row in results if not row["found"]]
    for row in results:
        if row["found"]:
            emit(f"ok       {row['lock']}")
        else:
            emit(f"MISSING  {row['lock']}")
            if row["instead"]:
                emit(f"         rendered instead: {row['instead']}")
    emit(f"{len(results) - len(missing)}/{len(results)} supplied strings render verbatim")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
