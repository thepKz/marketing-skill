#!/usr/bin/env python3
"""Measure the document-level shapes that mark a deliverable as machine-written.

The sentence instruments (check_specificity.py, rewrite_human.py,
check_address_register.py) grade facts, cadence and register. This one grades the
macro-structure — the announced opening, the category-label headers, the bold-led
bullet grid, the symmetric sections, the recap close — which survives even when
every sentence passes. The positive spec is references/output-contract.md: the
first sentence answers, headers assert, evidence rides the claim, form follows
content, no overture, no recap.

Usage:
    python check_output_shape.py --check FILE
    python check_output_shape.py --self-check

Exit 0 clean, 2 failed gate (critical or high), 3 computable but unsettled
(review findings only). Run after check_specificity.py and before
rewrite_human.py: restructuring rewrites sentences, so cadence measured before
shape is a wasted pass.
"""

import argparse
import re
import statistics
import sys
import unicodedata

# ---------------------------------------------------------------- patterns

ANNOUNCE_OPENERS = [
    r"dưới đây là", r"sau đây là", r"bài viết này", r"báo cáo này",
    r"tài liệu này", r"trong bài viết này", r"trong báo cáo này",
    r"chúng ta sẽ", r"hãy cùng", r"cùng tìm hiểu",
    r"here (?:is|are)", r"below (?:is|are)", r"this (?:report|document|article|plan|guide)",
    r"in this (?:report|document|article|plan|guide)", r"let's (?:explore|dive|take a look)",
    r"we (?:will|'ll) (?:explore|cover|look)",
]

RECAP_OPENERS = [
    r"tóm lại", r"nhìn chung", r"như vậy", r"kết luận", r"tựu trung",
    r"in conclusion", r"in summary", r"in short", r"to sum up", r"to conclude",
    r"overall,", r"all in all",
]

GENERIC_HEADINGS = {
    "giới thiệu", "tổng quan", "kết luận", "lời kết", "lợi ích", "tóm tắt",
    "introduction", "overview", "conclusion", "summary", "benefits",
    "key takeaways", "final thoughts", "closing thoughts",
}

BULLET_RE = re.compile(r"^\s*[-*+•]\s+")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
# a bullet whose first move is a bold label: "- **Thương hiệu:** ..." / "- **Term** — ..."
BOLD_LED_RE = re.compile(
    r"^\s*[-*+•]\s+\*\*[^*]+?(?:[::]\s*\*\*|\*\*\s*[::—–-])"
)
BOLD_ONLY_RE = re.compile(r"^\s*[-*+•]\s+\*\*[^*]+\*\*\s*$")

GATES = {
    "announce-open": ("critical", "the first paragraph announces the document instead of answering"),
    "recap-close": ("critical", "the last paragraph restates what the page above it already said"),
    "generic-headers": ("high", "headers name categories every document has, not findings this one made"),
    "bold-led-bullets": ("high", "the bold-label bullet grid — the single most recognisable AI page shape"),
    "uniform-sections": ("review", "sections sized by symmetry, not by what is known"),
    "uniform-bullet-counts": ("review", "every list the same length — content cut to fit a rhythm"),
    "verdict-missing": ("review", "no checkable fact in the opening — the answer may not be at the top"),
    "label-headers": ("review", "short noun-label headers throughout; none asserts anything"),
}

# ---------------------------------------------------------------- parsing


def strip_code_fences(text):
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return out


def parse(text):
    """Return headings, bullets, paragraphs (in order), and level-2 sections."""
    lines = strip_code_fences(unicodedata.normalize("NFC", text))
    headings, bullets, paragraphs = [], [], []
    sections = []          # dicts: heading, words, bullet_groups
    current = {"heading": None, "words": 0, "bullet_groups": []}
    para_buf, group_len = [], 0

    def flush_para():
        nonlocal para_buf
        if para_buf:
            paragraphs.append(" ".join(para_buf).strip())
            para_buf = []

    def flush_group():
        nonlocal group_len
        if group_len:
            current["bullet_groups"].append(group_len)
            group_len = 0

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()
        m = HEADING_RE.match(line)
        if m:
            flush_para()
            flush_group()
            level, title = len(m.group(1)), m.group(2).strip()
            headings.append((level, title))
            if level >= 2:
                sections.append(current)
                current = {"heading": title, "words": 0, "bullet_groups": []}
            continue
        if not stripped:
            flush_para()
            flush_group()
            continue
        if BULLET_RE.match(line):
            flush_para()
            bullets.append(line)
            group_len += 1
            current["words"] += len(stripped.split())
            continue
        flush_group()
        if stripped.startswith(("|", ">")):
            flush_para()
            continue
        para_buf.append(stripped)
        current["words"] += len(stripped.split())
    flush_para()
    flush_group()
    sections.append(current)
    return headings, bullets, paragraphs, sections


def plain(text):
    return re.sub(r"[*_`]", "", text).strip().lower()


def norm_heading(title):
    t = plain(title)
    t = re.sub(r"^[\d.)::\s-]+", "", t)      # strip "1. ", "02 — "
    return t.rstrip(" ::.").strip()

# ---------------------------------------------------------------- gates


def check(text):
    headings, bullets, paragraphs, sections = parse(text)
    findings = []

    def hit(gate, detail):
        sev, desc = GATES[gate]
        findings.append({"gate": gate, "severity": sev, "desc": desc, "detail": detail})

    if paragraphs:
        first = plain(paragraphs[0])
        for pat in ANNOUNCE_OPENERS:
            if re.match(pat, first):
                hit("announce-open", paragraphs[0][:90])
                break
        last = plain(paragraphs[-1])
        for pat in RECAP_OPENERS:
            if re.match(pat, last):
                hit("recap-close", paragraphs[-1][:90])
                break
        if not re.search(r"[\d%$]", paragraphs[0]):
            hit("verdict-missing", paragraphs[0][:90])

    generic = [t for _, t in headings if norm_heading(t) in GENERIC_HEADINGS]
    if generic:
        hit("generic-headers", ", ".join(generic))

    if bullets:
        bold_led = [b for b in bullets if BOLD_LED_RE.match(b) or BOLD_ONLY_RE.match(b)]
        if len(bold_led) >= 4 and len(bold_led) / len(bullets) >= 0.5:
            hit("bold-led-bullets",
                "%d of %d bullets open with a bold label" % (len(bold_led), len(bullets)))

    body = [s for s in sections if s["heading"] and s["words"] >= 40]
    if len(body) >= 4:
        counts = [s["words"] for s in body]
        cv = statistics.pstdev(counts) / statistics.mean(counts)
        if cv < 0.22:
            hit("uniform-sections",
                "%d sections, %s words, cv %.2f" % (len(counts), counts, cv))

    groups = [g for s in sections for g in s["bullet_groups"] if g >= 2]
    if len(groups) >= 3 and len(set(groups)) == 1 and groups[0] >= 3:
        hit("uniform-bullet-counts", "%d lists, every one %d items" % (len(groups), groups[0]))

    subs = [t for lvl, t in headings if lvl >= 2]
    if len(subs) >= 3:
        labels = [t for t in subs
                  if len(norm_heading(t).split()) <= 2 and not re.search(r"\d", t)]
        if len(labels) / len(subs) >= 0.6:
            hit("label-headers", ", ".join(labels[:5]))

    return findings


def verdict(findings):
    if any(f["severity"] in ("critical", "high") for f in findings):
        return 2
    if findings:
        return 3
    return 0


def report(path, findings):
    print("check_output_shape: %s" % path)
    for f in findings:
        print("[%s] %s — %s: %s" % (f["severity"], f["gate"], f["desc"], f["detail"]))
    code = verdict(findings)
    if code == 0:
        print("verdict: clean — the document is shaped like an answer")
    else:
        n = {"critical": 0, "high": 0, "review": 0}
        for f in findings:
            n[f["severity"]] += 1
        word = "fail" if code == 2 else "unsettled"
        print("verdict: %s (%d critical, %d high, %d review)"
              % (word, n["critical"], n["high"], n["review"]))
    return code

# ---------------------------------------------------------------- self-check

AI_VI = """# Kế hoạch marketing quán bún bò

Dưới đây là kế hoạch marketing toàn diện giúp quán tăng trưởng bền vững.

## Tổng quan

- **Thương hiệu:** xây dựng nhận diện nhất quán
- **Khách hàng:** nhắm vào dân văn phòng
- **Kênh:** tập trung mạng xã hội

## Lợi ích

- **Tiết kiệm:** tối ưu ngân sách hiệu quả
- **Nhanh chóng:** triển khai trong thời gian ngắn
- **Bền vững:** tăng trưởng dài hạn ổn định

## Kết luận

- **Hành động:** bắt đầu từ tuần này
- **Theo dõi:** đo lường mỗi tháng
- **Điều chỉnh:** điều chỉnh theo kết quả

Tóm lại, kế hoạch trên sẽ giúp quán phát triển toàn diện và bền vững.
"""

AI_EN = """# Launch strategy

Below is a comprehensive overview of your launch strategy and key considerations.

## Introduction

The market is competitive and the timing matters a great deal for a launch.

## Overview

- **Positioning:** differentiate on speed
- **Channels:** focus on organic reach
- **Budget:** keep spend lean early
- **Timeline:** move in two phases

In conclusion, this strategy positions the product for sustainable growth.
"""

GOOD_VI = """# Giá bún bò 89.000đ: giữ, thêm size sáng 65.000đ

Giữ 89.000đ — quán đứng giữa phân khúc Gò Vấp (12 quán khảo sát ngày 2026-08-01
tính 75.000–120.000đ) và biên đóng góp 41% chịu được khuyến mãi 15% mà không lỗ.

## 12 quán đối thủ tính 75.000–120.000đ

Khảo sát trực tiếp sáng 2026-08-01 trên đường Quang Trung và Phạm Văn Chiêu.
Ba quán đông nhất đều nằm ở 85.000–95.000đ, tức là mức 89.000đ không phải rào cản.

| Quán | Giá tô đặc biệt | Giờ đông nhất |
|---|---|---|
| Bún bò Cô Ba | 95.000đ | 7h-9h |
| Huế 79 | 85.000đ | 11h-13h |

## Size 65.000đ mở ca sáng đang trống

Ca 6h-8h hiện chiếm 9% doanh thu. Một tô nhỏ hơn 25% nguyên liệu bán 65.000đ giữ
biên 38% và cạnh tranh trực tiếp với xe bánh mì 30.000đ cộng cà phê 25.000đ —
cùng một túi tiền bữa sáng. In thêm một dòng vào menu hiện tại, không cần bảng mới.
Bắt đầu từ thứ hai 2026-08-10, đo số tô ca sáng trong 14 ngày trước khi quyết định giữ.
"""

SHORT_ANSWER = "Chạy khuyến mãi 15% là hòa vốn ở 2,1 tô cho mỗi tô cũ — quá 2x, không nên chạy."


def self_check():
    cases = [
        ("ai-vi", AI_VI, 2,
         {"announce-open", "recap-close", "generic-headers",
          "bold-led-bullets", "uniform-bullet-counts", "verdict-missing"}),
        ("ai-en", AI_EN, 2,
         {"announce-open", "recap-close", "generic-headers"}),
        ("good-vi", GOOD_VI, 0, set()),
        ("short-answer", SHORT_ANSWER, 0, set()),
    ]
    for name, text, want_code, want_gates in cases:
        findings = check(text)
        got_gates = {f["gate"] for f in findings}
        code = verdict(findings)
        assert want_gates <= got_gates, \
            "%s: expected gates %s, got %s" % (name, want_gates, got_gates)
        assert code == want_code, \
            "%s: expected exit %d, got %d (%s)" % (name, want_code, code, got_gates)
    assert not check(GOOD_VI), "good-vi must produce zero findings"
    print("self-check passed")


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", metavar="FILE", help="markdown or plain-text deliverable")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    if args.self_check:
        self_check()
        return 0
    if not args.check:
        ap.error("--check FILE or --self-check required")
    with open(args.check, encoding="utf-8") as fh:
        text = fh.read()
    return report(args.check, check(text))


if __name__ == "__main__":
    sys.exit(main())
