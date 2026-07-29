#!/usr/bin/env python3
"""Read the constraints a request already states, so the plan stops asking for them back.

A request like "muốn lên chiến dịch ra mắt trong 6 tuần cho khách văn phòng, ngân sách nhỏ"
carries four facts: a six-week horizon, a launch job, an office-worker audience, and a small
budget. Every one of those was being dropped. The run came back with a 90-day calendar, eight
assets including out-of-home and a conceptual art still life, `product_family: other` for a bowl
of bún bò, and the question "What kind of product, service, or offer is being promoted?" — asked
of a man who had just said he sells bún bò. That is the whole of the campaign bug: the request is
parsed for routing, then thrown away.

Everything here is an inference from wording, so everything here is labelled `inferred` and
carries the phrase it was read from. A horizon the user stated is not the same kind of fact as a
horizon we defaulted to, and the difference has to survive into the intake document; otherwise
the plan asserts a schedule nobody agreed to. Nothing in this module invents a number: a budget
tier is a tier, never a figure in đồng, because the amount is the user's to say.
"""

from __future__ import annotations

import re
import unicodedata

# Horizon wording, longest unit first so "tháng" is not shadowed by a bare digit match.
_HORIZON_UNITS = (
    (("năm", "nam", "year", "years"), 52),
    (("tháng", "thang", "month", "months"), 4),
    (("tuần", "tuan", "week", "weeks", "wk"), 1),
)
_DAY_WORDS = ("ngày", "ngay", "day", "days")

_WRITTEN_NUMBERS = {
    "một": 1, "mot": 1, "one": 1, "hai": 2, "two": 2, "ba": 3, "three": 3,
    "bốn": 4, "bon": 4, "four": 4, "năm": 5, "nam": 5, "five": 5, "sáu": 6, "sau": 6, "six": 6,
    "bảy": 7, "bay": 7, "seven": 7, "tám": 8, "tam": 8, "eight": 8, "chín": 9, "chin": 9, "nine": 9,
    "mười": 10, "muoi": 10, "ten": 10, "mười hai": 12, "twelve": 12,
}

BUDGET_TIERS = ("shoestring", "small", "mid", "large", "unstated")

_BUDGET_WORDS = {
    "shoestring": (
        "không có ngân sách", "khong co ngan sach", "zero budget", "no budget", "miễn phí",
        "mien phi", "free only", "organic only", "không tiền", "khong tien",
    ),
    "small": (
        "ngân sách nhỏ", "ngan sach nho", "ngân sách thấp", "ngan sach thap", "ít ngân sách",
        "it ngan sach", "small budget", "low budget", "tight budget", "shop nhỏ", "shop nho",
        "quán nhỏ", "quan nho", "tiết kiệm", "tiet kiem", "bootstrap", "hạn hẹp", "han hep",
    ),
    "mid": (
        "ngân sách vừa", "ngan sach vua", "ngân sách trung bình", "ngan sach trung binh",
        "medium budget", "moderate budget",
    ),
    "large": (
        "ngân sách lớn", "ngan sach lon", "large budget", "big budget", "significant budget",
        "ngân sách dồi dào", "ngan sach doi dao", "không giới hạn ngân sách",
    ),
}

# Product families, keyed to the vocabulary a Vietnamese owner actually uses. The families
# themselves match PRODUCT_PROOF in plan_marketing_system.py; the point of this table is that
# "bún bò" has to reach "food-beverage" without the user having to know the taxonomy exists.
_FAMILY_WORDS = {
    "food-beverage": (
        "bún", "bun bo", "phở", "pho", "cơm", "com tam", "bánh", "banh mi", "chè", "quán ăn",
        "quan an", "nhà hàng", "nha hang", "cà phê", "ca phe", "coffee", "cafe", "trà sữa",
        "tra sua", "restaurant", "food", "beverage", "drink", "bakery", "đồ ăn", "do an",
        "thức uống", "thuc uong", "menu", "thực đơn", "thuc don", "ẩm thực", "am thuc",
        "kitchen", "bếp", "catering", "snack", "bia", "beer", "juice", "nước ép",
    ),
    "beauty": (
        "mỹ phẩm", "my pham", "cosmetic", "skincare", "serum", "kem chống nắng", "son",
        "lipstick", "makeup", "trang điểm", "trang diem", "spa", "dưỡng da", "duong da",
    ),
    "fashion": (
        "quần áo", "quan ao", "thời trang", "thoi trang", "fashion", "apparel", "áo", "váy",
        "dress", "shoes", "giày", "giay", "túi", "bag", "clothing",
    ),
    "electronics": (
        "điện tử", "dien tu", "electronics", "laptop", "phone", "điện thoại", "dien thoai",
        "tai nghe", "headphone", "gadget", "camera", "thiết bị", "thiet bi",
    ),
    "home": (
        "nội thất", "noi that", "furniture", "gia dụng", "gia dung", "đồ gia dụng", "decor",
        "bếp từ", "chăn ga", "mattress", "đồ nhà", "household", "home decor", "homeware",
    ),
    "jewelry-luxury": (
        "trang sức", "trang suc", "jewelry", "jewellery", "vàng", "bạc", "kim cương",
        "diamond", "đồng hồ", "dong ho", "watch", "luxury", "cao cấp xa xỉ",
    ),
    "saas": (
        "saas", "phần mềm", "phan mem", "software", "app", "ứng dụng", "ung dung", "platform",
        "b2b", "dashboard", "api", "subscription", "nền tảng", "nen tang",
    ),
    "education": (
        "khóa học", "khoa hoc", "course", "dạy", "day hoc", "học viên", "hoc vien", "education",
        "training", "đào tạo", "dao tao", "trung tâm", "trung tam", "tutor", "lớp", "workshop",
    ),
    "hospitality": (
        "khách sạn", "khach san", "hotel", "homestay", "resort", "villa", "du lịch", "du lich",
        "travel", "tour", "phòng nghỉ", "phong nghi", "booking",
    ),
    "service": (
        "dịch vụ", "dich vu", "service", "sửa", "sua chua", "repair", "cleaning", "vệ sinh",
        "ve sinh", "consulting", "tư vấn", "tu van", "agency", "phòng khám", "phong kham",
        "clinic", "salon", "cắt tóc", "cat toc", "giặt", "laundry", "vận chuyển", "logistics",
    ),
}

# Vietnamese cities and the wording that says "this is one physical location", which is what
# decides whether out-of-home and national paid media are even candidates.
_VN_PLACES = (
    "sài gòn", "sai gon", "saigon", "hồ chí minh", "ho chi minh", "hcm", "tp.hcm", "hà nội",
    "ha noi", "hanoi", "đà nẵng", "da nang", "huế", "hue", "cần thơ", "can tho", "hải phòng",
    "hai phong", "nha trang", "đà lạt", "da lat", "vũng tàu", "vung tau", "bình dương",
    "binh duong", "biên hòa", "bien hoa", "việt nam", "viet nam", "vietnam",
)
_LOCAL_WORDS = (
    "quán", "quan an", "shop", "cửa hàng", "cua hang", "tiệm", "tiem", "chi nhánh", "chi nhanh",
    "counter", "storefront", "gần", "gan day", "trong khu", "khu vực", "khu vuc", "phường",
    "quận", "quan ", "street", "kiosk", "walk-in", "khách quanh", "văn phòng gần",
)


def _fold(text: str) -> str:
    """Lowercase and strip diacritics, keeping the original text searchable both ways."""
    stripped = "".join(
        ch for ch in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(ch)
    )
    return stripped.replace("đ", "d")


def _contains(haystack: str, folded: str, needle: str) -> bool:
    return needle in haystack or _fold(needle) in folded


def read_horizon(text: str) -> dict:
    """Find a stated campaign horizon and return it in weeks and days.

    Returns `stated: False` with a 90-day default when the request says nothing. The caller has
    to keep that distinction: a defaulted horizon must be presented as an assumption to confirm,
    not printed as a schedule. This is why the calendar deliverable used to be wrong in a way
    nobody noticed — `10-calendar-90d` reads like a decision, and it was a hardcoded filename.
    """
    lowered = str(text).lower()
    folded = _fold(lowered)
    best: tuple[int, str] | None = None

    for words, weeks_per_unit in _HORIZON_UNITS:
        for word in words:
            for pattern in (rf"(\d+)\s*{re.escape(word)}", rf"{re.escape(word)}\s*(\d+)"):
                for source in (lowered, folded):
                    match = re.search(pattern, source)
                    if match:
                        count = int(match.group(1))
                        if 1 <= count <= 104:
                            weeks = count * weeks_per_unit
                            if best is None or weeks < best[0]:
                                best = (weeks, match.group(0).strip())
            # "trong sáu tuần" — a written number in front of the unit.
            for spelled, count in _WRITTEN_NUMBERS.items():
                phrase = f"{spelled} {word}"
                if _contains(lowered, folded, phrase):
                    weeks = count * weeks_per_unit
                    if best is None or weeks < best[0]:
                        best = (weeks, phrase)
        if best is not None:
            break

    if best is None:
        for word in _DAY_WORDS:
            match = re.search(rf"(\d+)\s*{re.escape(word)}", folded)
            if match:
                days = int(match.group(1))
                if 7 <= days <= 730:
                    best = (max(1, round(days / 7)), match.group(0).strip())
                    break

    if best is None:
        return {"weeks": 13, "days": 90, "stated": False, "evidence": "", "label": "inferred"}
    weeks, evidence = best
    return {"weeks": weeks, "days": weeks * 7, "stated": True, "evidence": evidence, "label": "confirmed"}


def read_budget(text: str) -> dict:
    """Classify budget pressure into a tier. Never into an amount.

    A tier is enough to decide how many assets a plan may ask for, and it is the most that can
    be honestly read from "ngân sách nhỏ". Turning that into "15 triệu/tháng" would be inventing
    the one number the whole budget deliverable is supposed to derive from.
    """
    lowered = str(text).lower()
    folded = _fold(lowered)
    for tier in ("shoestring", "small", "mid", "large"):
        for phrase in _BUDGET_WORDS[tier]:
            if _contains(lowered, folded, phrase):
                return {"tier": tier, "stated": True, "evidence": phrase, "label": "inferred"}
    return {"tier": "unstated", "stated": False, "evidence": "", "label": "unknown"}


def read_product_family(text: str) -> dict:
    """Map the words the owner used onto a proof family.

    Scored rather than first-match, because "quán cà phê bán bánh" hits two food words and one
    service word and should still be food-beverage. Scored by matched length as well as count,
    because a short token can sit inside a longer one belonging to another family: "homestay" hit
    both `home` and `hospitality` at one word each, and the tie went to whichever family happened
    to be declared first, which put a Đà Lạt homestay in the furniture business.
    """
    lowered = str(text).lower()
    folded = _fold(lowered)
    hits: dict[str, list[str]] = {}
    for family, words in _FAMILY_WORDS.items():
        found = sorted(
            (word for word in words if _contains(lowered, folded, word)), key=len, reverse=True
        )
        if found:
            hits[family] = found
    if not hits:
        return {"family": "other", "stated": False, "evidence": [], "label": "unknown"}
    family = max(
        hits,
        key=lambda key: (max(len(word) for word in hits[key]), len(hits[key]), -list(_FAMILY_WORDS).index(key)),
    )
    return {"family": family, "stated": True, "evidence": hits[family][:3], "label": "inferred"}


def read_market(text: str) -> dict:
    """Detect a Vietnamese market and whether the business is one physical location."""
    lowered = str(text).lower()
    folded = _fold(lowered)
    places = [place for place in _VN_PLACES if _contains(lowered, folded, place)]
    local = [word for word in _LOCAL_WORDS if _contains(lowered, folded, word)]
    return {
        "market": "vietnam" if places else "unstated",
        "places": places[:3],
        "single_location": bool(places and local) or bool(local),
        "label": "inferred" if places or local else "unknown",
    }


# How many creative assets a plan may ask for at each budget tier, and which channel families
# stop being candidates. A small-budget shop that is handed an out-of-home key visual and a
# LinkedIn carousel has been given a plan for a company it is not.
BUDGET_ASSET_CAP = {"shoestring": 3, "small": 4, "mid": 8, "large": 14, "unstated": 8}
# Whole asset families that a tier cannot carry. Channel filtering alone was not enough: the
# selector guarantees one asset per family before it fills the remainder, so with a cap of four a
# small-budget shop was still handed a conceptual art still life, because that family had a
# reserved slot. It took the place of something the shop could shoot on a phone at lunchtime.
BUDGET_EXCLUDED_FAMILIES = {
    "shoestring": ("art", "pr"),
    "small": ("art", "pr"),
    "mid": (),
    "large": (),
    "unstated": (),
}

BUDGET_EXCLUDED_CHANNELS = {
    "shoestring": ("ooh", "pr", "paid", "linkedin", "pinterest", "editorial"),
    "small": ("ooh", "linkedin", "pinterest", "editorial"),
    "mid": ("ooh",),
    "large": (),
    "unstated": (),
}


def read_signals(text: str) -> dict:
    """Read every constraint at once. This is what the scripts call."""
    return {
        "horizon": read_horizon(text),
        "budget": read_budget(text),
        "product_family": read_product_family(text),
        "market": read_market(text),
    }


def phase_plan(weeks: int) -> list[dict]:
    """Split a horizon into named phases that add up to it exactly.

    The old calendar had three fixed sections — days 1-30, 31-60, 61-90 — so a six-week campaign
    was handed sixty days it did not have and a launch date two thirds of the way through a
    schedule it never asked for.
    """
    weeks = max(1, int(weeks))
    if weeks <= 2:
        spans = [weeks]
    elif weeks <= 6:
        first = max(1, weeks // 3)
        spans = [first, first, weeks - 2 * first]
    else:
        first = weeks // 3
        spans = [first, first, weeks - 2 * first]

    names_vi = ["Khởi động", "Mở rộng", "Củng cố"]
    names_en = ["Ignite", "Expand", "Consolidate"]
    goals_vi = [
        "Ra mắt và tìm tín hiệu đầu tiên. Mục tiêu là học, không phải doanh số.",
        "Nhân cái đã chạy, cắt cái không chạy, nêu rõ bằng chứng nào quyết định.",
        "Việc có tích lũy, kênh thứ hai, và tài sản thuộc sở hữu của mình.",
    ]
    goals_en = [
        "Launch and find the first signal. The goal is learning, not revenue.",
        "Scale what ran, cut what did not, and name the evidence that decided.",
        "Compounding work, the second channel, and the audience you own.",
    ]

    phases = []
    cursor = 1
    for index, span in enumerate(spans):
        if span <= 0:
            continue
        last = cursor + span - 1
        phases.append(
            {
                "index": index,
                "name_vi": names_vi[index],
                "name_en": names_en[index],
                "week_from": cursor,
                "week_to": last,
                "day_from": (cursor - 1) * 7 + 1,
                "day_to": last * 7,
                "goal_vi": goals_vi[index],
                "goal_en": goals_en[index],
            }
        )
        cursor = last + 1
    return phases
