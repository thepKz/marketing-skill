#!/usr/bin/env python3
"""Focused tests for the deterministic Marketing-Minthep tools."""

from __future__ import annotations

import csv
import io
import json
import unicodedata
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from _signals import BUDGET_TIERS, phase_plan, read_signals
from analyze_performance import analyze
from build_asset_manifest import build_manifest
from compile_prompt import compile_provider
from new_run import build_run, load_registry, route_pipeline, write_run
from plan_image_generation import route_image_request
from plan_design_options import plan_options
from plan_marketing_system import PRODUCT_PROOF, plan_marketing_system
from plan_video_sequence import lock_block, resolve, shot_prompt
from plan_virtual_person import plan_virtual_person
from render_mockup import CAP, DROP, FONTS_WITHOUT_VIETNAMESE, SANS, SERIF, THEMES, advance, render, wrap
from research_plan import build_plan, to_markdown
from run_status import audit_file, audit_run
from scaffold_campaign import build_record, to_markdown as to_campaign_markdown
from score_creative import evaluate
from start_workbench import start


class ToolTests(unittest.TestCase):
    def test_research_plan_is_bounded_and_traceable(self) -> None:
        plan = build_plan({"objective": "Đánh giá quán bún bò", "category": "bún bò", "market": "TP.HCM"})
        self.assertEqual(plan["scope"]["market"], "TP.HCM")
        self.assertEqual({item["id"] for item in plan["questions"]}, {"demand", "competition", "buyer-language", "constraints"})
        self.assertTrue(all(item["stop_condition"] for item in plan["questions"]))
        self.assertIn("retrieved_at", plan["evidence_ledger_fields"])
        self.assertIn("Kế hoạch nghiên cứu", to_markdown(plan))

    def test_design_options_are_distinct_and_renderable(self) -> None:
        result = plan_options({"artefact": "menu", "product": "Bún bò Huế"})
        self.assertEqual(result["artefact"], "menu")
        self.assertEqual(len(result["options"]), 3)
        self.assertEqual(len({item["id"] for item in result["options"]}), 3)
        svg = render({"title": "Bún bò Huế", "items": [{"name": "Tô đặc biệt", "price": "79.000đ"}]})
        self.assertIn("<svg", svg)
        self.assertIn("Tô đặc biệt", svg)
        self.assertIn("79.000đ", svg)
        self.assertEqual(ET.fromstring(svg).tag, "{http://www.w3.org/2000/svg}svg")

    def _item_baselines(self, spec: dict) -> list[float]:
        root = ET.fromstring(render(spec))
        return [
            float(node.get("y"))
            for node in root.iter()
            if node.tag.endswith("text") and node.get("class") == "item"
        ]

    def test_mockup_layout_adapts_to_any_canvas(self) -> None:
        """Layout used to be hardcoded to 1080x1350, so any other size drew text off-canvas
        or over the footer rule while still emitting valid SVG — a silent failure."""
        items = [{"name": f"Dish {index}", "description": "d", "price": "—"} for index in range(6)]
        for width, height in ((1080, 1350), (1200, 1600), (1080, 1080), (640, 960)):
            spec = {"title": "Bún bò", "items": items, "width": width, "height": height}
            baselines = self._item_baselines(spec)
            self.assertEqual(len(baselines), len(items))
            footer_rule = height - round(height * 0.0519)
            self.assertLess(
                max(baselines), footer_rule, f"items cross the footer rule at {width}x{height}"
            )
            self.assertGreater(min(baselines), 0)

    def test_mockup_refuses_a_menu_that_cannot_fit(self) -> None:
        """Silently dropping items past a cap would present a partial menu as the whole menu."""
        items = [{"name": f"Dish {index}"} for index in range(20)]
        with self.assertRaises(ValueError) as caught:
            render({"title": "Too long", "items": items, "width": 1080, "height": 700})
        self.assertIn("do not fit", str(caught.exception))

    def test_mockup_tightens_rather_than_overflowing_as_items_grow(self) -> None:
        base = {"title": "Bún bò", "width": 1080, "height": 1350}
        pitches = []
        for count in (4, 8, 11):
            items = [{"name": f"D{index}", "price": "—"} for index in range(count)]
            baselines = self._item_baselines({**base, "items": items})
            pitches.append(baselines[1] - baselines[0])
        self.assertGreater(pitches[0], pitches[-1], "row pitch must compress as items are added")

    def test_mockup_fonts_declare_fallbacks(self) -> None:
        """A bare family name re-flows the whole layout on any machine that lacks it."""
        svg = render({"title": "Bún bò", "items": [{"name": "Tô đặc biệt", "price": "79.000đ"}]})
        self.assertIn("sans-serif", svg)
        self.assertIn("Liberation", svg)

    def test_mockup_fonts_can_render_vietnamese(self) -> None:
        """Georgia led the serif stack and covers no two-diacritic Vietnamese letter, so
        "Nấu theo lối cũ" rendered as "Nâ´u theo lô´i cũ" — the base letter with a loose
        accent beside it. Every deliverable here is bilingual VI/EN, so a font that cannot
        spell Vietnamese must not appear in a stack at all, not even as a fallback."""
        for stack in (SANS, SERIF):
            for family in FONTS_WITHOUT_VIETNAMESE:
                self.assertNotIn(
                    family,
                    stack,
                    f"{family} lacks the U+1EA0-U+1EF9 block and would mangle Vietnamese",
                )
            # A stack whose last resort is a bare generic is fine; one with no generic is not,
            # because the browser then picks a default this layout was never measured against.
            self.assertRegex(stack.strip(), r"(sans-serif|serif)$", f"no generic fallback: {stack}")

    def test_rendered_examples_contain_no_loose_combining_accents(self) -> None:
        """The same bug can also arrive from the other side: text stored decomposed (NFD)
        puts a combining mark in the file itself, which renders identically wrong even in a
        font with full coverage. Precomposed NFC is the only form that survives both paths."""
        for path in sorted((REPO_ROOT / "docs" / "assets" / "generated").glob("*.svg")):
            text = path.read_text(encoding="utf-8")
            loose = sorted({character for character in text if unicodedata.combining(character)})
            self.assertEqual(
                loose,
                [],
                f"{path.name} stores combining marks {[unicodedata.name(c) for c in loose]}; "
                "normalise the source JSON to NFC",
            )

    def test_mockup_themes_differ_in_layout_not_only_palette(self) -> None:
        """plan_design_options.py sells the three themes as different design directions, with
        different margins, type scale and row treatment. They once differed only in colour and
        font, which made the option set a choice in name only. Each must change real geometry."""
        items = [{"name": f"Dish {index}", "price": "—"} for index in range(4)]
        spec = {"title": "Bún bò", "items": items, "width": 1080, "height": 1080}
        indents, pitches, titles = set(), set(), set()
        for theme in ("quiet-editorial", "modern-street", "heritage-craft"):
            svg = render({**spec, "theme": theme})
            names = [
                node for node in ET.fromstring(svg).iter()
                if node.tag.endswith("text") and node.get("class") == "item"
            ]
            baselines = [float(node.get("y")) for node in names]
            indents.add(min(float(node.get("x")) for node in names))
            pitches.add(baselines[1] - baselines[0])
            titles.add(svg.split(".title{font:700 ")[1].split("px")[0])
        self.assertEqual(len(indents), 3, f"themes share a text indent: {indents}")
        self.assertEqual(len(pitches), 3, f"themes share a row pitch: {pitches}")
        self.assertEqual(len(titles), 3, f"themes share a title size: {titles}")

    def test_mockup_price_leader_never_runs_under_the_text(self) -> None:
        """heritage-craft draws a dotted leader between name and price from an estimated text
        width. If the estimate ran short the dots would print through a dish name, so the leader
        must stay clear of both ends at every name length, or be dropped entirely."""
        base = {"theme": "heritage-craft", "title": "Bún bò", "width": 1080, "height": 1080}
        indent = round(1080 * 0.0972) + round(46)
        stem = "Bún bò Huế đặc biệt thêm giò heo và chả cua"
        drawn = 0
        for length in range(6, len(stem) + 1, 4):
            name, price = stem[:length].strip(), "129.000đ"
            root = ET.fromstring(render({**base, "items": [{"name": name, "price": price}]}))
            leaders = [node for node in root.iter() if node.get("stroke-dasharray")]
            if not leaders:
                continue
            drawn += 1
            name_end = indent + advance(name, 28, bold=True)
            price_start = 975 - advance(price, 26, bold=True)
            self.assertGreater(float(leaders[0].get("x1")), name_end, f"leader under {name!r}")
            self.assertLess(float(leaders[0].get("x2")), price_start, f"leader under the price of {name!r}")
        self.assertGreater(drawn, 3, "no leader was drawn at any name length")
        # A name that took two lines has no single baseline to lead from, so it gets nothing.
        wrapped = render({
            **base,
            "items": [{"name": "Bún bò Huế đặc biệt thêm giò heo, chả cua và huyết heo", "price": "129.000đ"}],
        })
        self.assertEqual(
            [node for node in ET.fromstring(wrapped).iter() if node.get("stroke-dasharray")],
            [],
            "leader drawn across a two-line dish name",
        )

    def test_width_estimate_stays_close_to_what_a_browser_draws(self) -> None:
        """Every wrap, every leader and the hero clearance all rest on `advance`. The figures on
        the right were read out of Chrome with getBBox on this exact SVG at 1080 wide; the
        estimate has to stay above them, because erring narrow is what puts type off the page,
        and within a third, because erring wide throws away usable line length."""
        for text, size, bold, measured in (
            ("Bún bò tiêu chuẩn", 28, True, 246.0),
            ("Bún bò mỗi ngày", 64, True, 526.0),
            ("Bản minh họa bố cục — giá và thành phần phải", 24, False, 510.0),
            ("Bún bò Huế đặc biệt thêm giò heo và chả cua", 28, True, 565.5),
        ):
            estimate = advance(text, size, bold=bold)
            self.assertGreater(estimate, measured, f"{text!r} is estimated narrower than it draws")
            self.assertLess(estimate, measured * 1.33, f"{text!r} is estimated far too wide")

    def test_wrapping_measures_pixels_not_characters(self) -> None:
        """The character budget was computed as 48 divided by the scale, so a canvas twice as
        wide got a measure half as long: the 2160px poster wrapped its subtitle after a third of
        the sentence. A wider canvas must fit more per line, never less."""
        sentence = "Bản minh họa bố cục — giá và thành phần phải được quán xác nhận trước khi in"
        first_line = {}
        for width in (1080, 2160):
            lines = wrap(sentence, round(24 * width / 1080), round(width * 0.60), 3, "subtitle")
            first_line[width] = len(lines[0])
        self.assertGreaterEqual(first_line[2160], first_line[1080], f"wrap got tighter as the canvas grew: {first_line}")

    def test_copy_is_never_silently_truncated(self) -> None:
        """The subtitle was cut to two lines and the rest discarded, so a spec ending "...ruốc
        Huế nguyên chất, không dùng bột ngọt" rendered as "...ruốc Huế nguyên chất," — ending on
        a comma, the layout advertising that it ate the sentence. Refusing is the only honest
        answer, the same answer an over-long item list already gets."""
        long_subtitle = (
            "Nước dùng nấu từ xương bò và giò heo trong mười hai giờ, sả tươi giã tay, ruốc Huế "
            "nguyên chất, không dùng bột ngọt hay viên gia vị công nghiệp nào cả"
        )
        with self.assertRaises(ValueError) as caught:
            render({"title": "Bún bò", "subtitle": long_subtitle, "items": [{"name": "Tô"}]})
        self.assertIn("shorten it", str(caught.exception))
        fits = "Nước dùng nấu từ xương bò và giò heo trong mười hai giờ, sả tươi giã tay"
        svg = render({"title": "Bún bò", "subtitle": fits, "items": [{"name": "Tô"}]})
        for word in fits.split():
            self.assertIn(word, svg, f"{word!r} was dropped from the subtitle")

    def test_header_type_never_overlaps_the_line_above_it(self) -> None:
        """Kicker, title and subtitle sat at 11.1, 16.3 and 19.3 percent of the canvas height,
        fractions chosen while the title happened to be one short line. Grow the title and its
        ascenders reach the kicker baseline: "SIGNATURE MENU" rendered with the diacritic of
        "mỗi" cutting through it. Vertical position has to come from the type sizes in use."""
        for theme in THEMES:
            for width, height in ((1080, 1080), (1080, 1350), (1440, 1440), (640, 960)):
                spec = {
                    "theme": theme, "width": width, "height": height,
                    "kicker": "BÚN BÒ / SIGNATURE MENU",
                    "title": "Bún bò Huế gia truyền cô Tám",
                    "subtitle": "Bản minh họa bố cục — giá phải được quán xác nhận",
                    "items": [{"name": "Tô đặc biệt", "price": "—"}],
                }
                svg = render(spec)
                root = ET.fromstring(svg)
                blocks = []
                for name in ("kicker", "title", "subtitle"):
                    node = next(n for n in root.iter() if n.get("class") == name)
                    size = float(re.search(rf"\.{name}{{font:(?:\d+ )?(\d+)px", svg).group(1))
                    top = float(node.get("y")) - size * CAP
                    spans = list(node)
                    step = size * 1.24
                    bottom = float(node.get("y")) + max(0, len(spans) - 1) * step + size * DROP
                    blocks.append((name, top, bottom))
                for (upper, _, upper_bottom), (lower, lower_top, _) in zip(blocks, blocks[1:]):
                    self.assertLess(
                        upper_bottom, lower_top,
                        f"{theme} {width}x{height}: {lower} rides into {upper}",
                    )

    def test_a_long_title_wraps_clear_of_the_hero(self) -> None:
        """The title was one unwrapped line at the left margin and the bowl was a fixed box at
        63.9 percent of the width, so "Bún bò Huế gia truyền cô Tám" ran under the bowl and the
        last two words were painted over. Nothing in the header may reach the hero box."""
        width = 1080
        hero_x = width - round(width * 0.111) - round(width * 0.30)
        svg = render({
            "theme": "quiet-editorial", "width": width, "height": 1350,
            "title": "Bún bò Huế gia truyền cô Tám", "hero_shape": "bowl",
            "items": [{"name": "Tô đặc biệt", "price": "—"}],
        })
        title = next(node for node in ET.fromstring(svg).iter() if node.get("class") == "title")
        lines = [span.text for span in title]
        self.assertGreater(len(lines), 1, "a title this long has to wrap")
        self.assertEqual(" ".join(lines), "Bún bò Huế gia truyền cô Tám")
        size = float(re.search(r"\.title{font:700 (\d+)px", svg).group(1))
        for line in lines:
            end = round(width * 0.111) + advance(line, size, bold=True)
            self.assertLess(end, hero_x, f"{line!r} reaches the hero box")

    def test_a_dish_name_never_runs_under_its_own_price(self) -> None:
        """Item names were emitted as one line at any length. A 45-character dish name at 28px
        crossed the right-aligned price, so the two most important strings in a menu row
        overprinted each other."""
        svg = render({
            "theme": "modern-street", "title": "Bún bò", "width": 1080, "height": 1350,
            "items": [
                {"name": "Bún bò Huế đặc biệt thêm giò heo, chả cua và huyết heo", "price": "129.000đ"},
                {"name": "Trà đá", "price": "3.000đ"},
            ],
        })
        root = ET.fromstring(svg)
        indent = round(1080 * 0.0833) + 46
        price_left = 1080 - round(1080 * 0.0833) - advance("129.000đ", 26, bold=True)
        name = next(node for node in root.iter() if node.get("class") == "item")
        for span in list(name) or [name]:
            self.assertLess(
                indent + advance(span.text, 28, bold=True), price_left,
                f"{span.text!r} crosses the price column",
            )

    def test_items_leave_no_hole_over_the_footer(self) -> None:
        """Rows were top-aligned in a band sized for eleven, so four dishes on a 1350px canvas
        left a 250px gap above the footer rule while the category label sat far above them.
        Label and rows travel together and the slack is split above and below."""
        height = 1350
        svg = render({
            "theme": "modern-street", "title": "Bún bò", "width": 1080, "height": height,
            "items": [{"name": f"Tô {index}", "description": "Chờ xác nhận", "price": "—"} for index in range(4)],
        })
        root = ET.fromstring(svg)
        divider = max(
            float(node.get("y1")) for node in root.iter()
            if node.tag.endswith("line") and node.get("y1") == node.get("y2")
            and float(node.get("y1")) < height * 0.5
        )
        descriptions = [float(node.get("y")) for node in root.iter() if node.get("class") == "desc"]
        label = float(next(node for node in root.iter() if node.get("class") == "category").get("y"))
        footer_rule = height - round(height * 0.0519)
        above, below = label - divider, footer_rule - max(descriptions)
        self.assertLess(
            abs(above - below), max(above, below) * 0.5,
            f"slack is lopsided: {above:.0f}px above the label, {below:.0f}px below the last row",
        )
        self.assertLess(max(descriptions), footer_rule, "a description crosses the footer rule")

    def test_hero_placeholder_reads_as_a_bowl_not_a_disc(self) -> None:
        """The bowl took one radius and derived its height from it, so on a hero box taller than
        it was wide it flattened into two stacked ellipses — a hockey puck. It needs a wall with
        real depth below the rim at every hero shape."""
        for width, height in ((1080, 1080), (1080, 1620), (720, 1280)):
            svg = render({
                "title": "Bún bò", "width": width, "height": height, "hero_shape": "bowl",
                "items": [{"name": "Tô đặc biệt", "price": "—"}],
            })
            rim = next(
                node for node in ET.fromstring(svg).iter()
                if node.tag.endswith("ellipse") and node.get("fill") == "#231f20"
            )
            wall = next(node for node in ET.fromstring(svg).iter() if node.tag.endswith("path")
                        and node.get("fill") == "#231f20")
            rim_ry = float(rim.get("ry"))
            depth = max(float(value) for value in re.findall(r"L[-\d.]+ ([\d.]+)", wall.get("d"))) - float(rim.get("cy"))
            self.assertGreater(depth, rim_ry, f"{width}x{height}: bowl is {depth:.0f}px deep on a {rim_ry:.0f}px rim")

    def test_scaffold_v4_separates_job_and_artifact_mode(self) -> None:
        record = build_record("Launch", "product", "beauty", "gpt-image-2", ["meta", "web"])
        self.assertEqual(record["schema_version"], 4)
        self.assertEqual(record["primary_job"], "campaign-launch")
        self.assertEqual(record["artifact_mode"], "product")
        self.assertEqual([lane["name"] for lane in record["concept_lanes"]], ["Clear", "Signature", "Departure"])
        self.assertGreater(len(record["assets"]), 3)

    # --- The campaign bug: a request states its constraints and the plan ignores them. ---
    #
    # Every test below was written against a real defect in the run produced by the request
    # "Tôi bán bún bò ở Sài Gòn, muốn lên chiến dịch ra mắt trong 6 tuần cho khách văn phòng,
    # ngân sách nhỏ": a 90-day calendar for a six-week campaign, eight assets for a small budget,
    # `product_family: other` for a bowl of bún bò, and an intake file asking to be told the
    # product it had just been told.

    BUN_BO = "Tôi bán bún bò ở Sài Gòn, muốn lên chiến dịch ra mắt trong 6 tuần cho khách văn phòng, ngân sách nhỏ"

    def test_a_stated_horizon_reaches_the_calendar(self) -> None:
        run = build_run({"request": self.BUN_BO})
        self.assertEqual(run["signals"]["horizon"]["weeks"], 6)
        self.assertTrue(run["signals"]["horizon"]["stated"])
        calendar = next(item for item in run["deliverables"] if item["id"] == "10-calendar")
        for path in calendar["paths"]:
            self.assertIn("6w", path, f"a 6-week campaign was given {path}")
            self.assertNotIn("90d", path)
        self.assertIn("6-week", calendar["title"])

    def test_calendar_phases_add_up_to_the_horizon(self) -> None:
        for weeks in (1, 2, 3, 6, 8, 13, 26, 52):
            phases = phase_plan(weeks)
            self.assertEqual(phases[0]["week_from"], 1)
            self.assertEqual(phases[-1]["week_to"], weeks, f"{weeks}w phases end at {phases[-1]['week_to']}")
            for earlier, later in zip(phases, phases[1:]):
                self.assertEqual(later["week_from"], earlier["week_to"] + 1, f"{weeks}w has a gap or overlap")
            self.assertEqual(phases[-1]["day_to"], weeks * 7)

    def test_an_unstated_horizon_is_labelled_as_an_assumption(self) -> None:
        """The default is fine. Printing it as though it were agreed is not."""
        run = build_run({"request": "Tôi muốn lên chiến dịch cho quán bún bò"})
        self.assertFalse(run["signals"]["horizon"]["stated"])
        self.assertEqual(run["signals"]["horizon"]["weeks"], 13)
        with tempfile.TemporaryDirectory() as tmp:
            written = write_run(run, Path(tmp), request={"request": "Tôi muốn lên chiến dịch cho quán bún bò"})
            calendar = (Path(written["run_dir"]) / "10-calendar-13w.en.md").read_text(encoding="utf-8")
            self.assertIn("No horizon", calendar)
            index = (Path(written["run_dir"]) / "README.md").read_text(encoding="utf-8")
            self.assertIn("assumed", index)

    def test_intake_quotes_the_request_instead_of_asking_for_it(self) -> None:
        request = {"request": self.BUN_BO}
        run = build_run(request)
        with tempfile.TemporaryDirectory() as tmp:
            written = write_run(run, Path(tmp), request=request)
            intake = (Path(written["run_dir"]) / "01-intake.md").read_text(encoding="utf-8")
        self.assertIn(self.BUN_BO, intake, "the request the scaffold holds is not in the intake file")
        self.assertNotIn("Quote the user verbatim", intake)
        # Every signal is present with its label, and the two figures nobody stated are named as
        # unknown rather than left out, because the budget deliverable blocks on them.
        for expected in ("6 weeks (42 days)", "`confirmed`", "small", "food-beverage",
                         "Unit price", "Contribution margin", "`unknown`"):
            self.assertIn(expected, intake)

    def test_a_small_budget_does_not_get_a_large_budget_asset_list(self) -> None:
        plan = plan_marketing_system({"request": self.BUN_BO})
        self.assertEqual(plan["budget_tier"], "small")
        self.assertLessEqual(plan["asset_count"], 4, "a shop that said ngân sách nhỏ got more than four assets")
        families = {asset["family"] for asset in plan["selected_assets"]}
        self.assertNotIn("art", families, "a conceptual art still life is not a small-budget asset")
        channels = {channel for asset in plan["selected_assets"] for channel in asset["channels"]}
        self.assertFalse(channels & {"ooh", "linkedin", "pinterest"},
                         f"unaffordable channels survived: {sorted(channels & {'ooh', 'linkedin', 'pinterest'})}")
        self.assertTrue(plan["assets_dropped_for_budget"], "assets were dropped without saying which or why")
        for entry in plan["assets_dropped_for_budget"]:
            self.assertTrue(entry["reason"])

    def test_a_large_budget_is_not_capped_by_the_small_budget_rules(self) -> None:
        plan = plan_marketing_system({"request": "Global launch campaign, large budget", "asset_scope": "system"})
        self.assertEqual(plan["budget_tier"], "large")
        self.assertGreater(plan["asset_count"], 4)
        self.assertEqual(plan["assets_dropped_for_budget"], [])

    def test_product_family_is_read_from_the_words_the_owner_used(self) -> None:
        cases = {
            self.BUN_BO: "food-beverage",
            "Bán serum dưỡng da, muốn chạy quảng cáo": "beauty",
            "We sell a B2B SaaS dashboard": "saas",
            "Mở homestay ở Đà Lạt": "hospitality",
            "Trung tâm dạy tiếng Anh cho trẻ": "education",
        }
        for request, expected in cases.items():
            plan = plan_marketing_system({"request": request})
            self.assertEqual(plan["product_family"], expected, f"{request!r} -> {plan['product_family']}")
            self.assertEqual(plan["product_family_label"], "inferred")
            self.assertNotEqual(plan["proof_requirements"], PRODUCT_PROOF["other"],
                                f"{request!r} got the generic proof list")

    def test_an_explicit_product_family_still_wins(self) -> None:
        plan = plan_marketing_system({"request": self.BUN_BO, "product_family": "hospitality"})
        self.assertEqual(plan["product_family"], "hospitality")
        self.assertEqual(plan["product_family_label"], "confirmed")

    def test_the_plan_does_not_ask_what_it_was_just_told(self) -> None:
        plan = plan_marketing_system({"request": self.BUN_BO})
        for question in plan["questions"]:
            self.assertNotIn("What kind of product", question,
                             "asked what the product is, of a request that opens by saying so")
        # It asks instead for the two numbers that cannot be inferred from any wording.
        self.assertTrue(any("cost you to make" in question for question in plan["questions"]))

    def test_campaign_brief_derives_from_the_request_it_was_given(self) -> None:
        record = build_record("Bún bò", "mixed", "food-cpg", "generic", ["meta", "tiktok", "web"],
                              request=self.BUN_BO)
        self.assertEqual(record["horizon_weeks"], 6)
        self.assertTrue(record["horizon_stated"])
        self.assertEqual(record["budget_tier"], "small")
        self.assertEqual(len(record["assets"]), record["asset_cap"])
        self.assertLessEqual(len(record["assets"]), 4)
        self.assertIn(self.BUN_BO, record["truth_map"]["confirmed"][0])
        self.assertTrue(any("6 tuần" in entry for entry in record["truth_map"]["inferred"]))
        # A stated horizon is not asked for again, and no asset carries "TBD" as its funnel stage.
        self.assertFalse(any("How long" in question for question in record["open_questions"]))
        self.assertEqual([], [asset for asset in record["assets"] if asset["funnel_stage"] == "TBD"])

    def test_campaign_brief_separates_unknown_from_undecided(self) -> None:
        """A brief that prints both as TBD hides the questions that actually block the work."""
        record = build_record("Launch", "mixed", "other", "generic", ["meta"], request="Launch a new product")
        markdown = to_campaign_markdown(record)
        self.assertIn("UNKNOWN", markdown)
        self.assertIn("TBD", markdown)
        self.assertIn("nobody has stated", markdown)
        self.assertIn("Do not fill an `UNKNOWN` with a plausible guess", markdown)
        self.assertEqual(record["brief"]["product_truth"], record["brief"]["proof"])
        self.assertNotEqual(record["brief"]["product_truth"], "TBD")
        # No horizon was stated, so that question comes back — and it comes back only then.
        self.assertTrue(any("How long" in question for question in record["open_questions"]))

    def test_campaign_assets_spread_across_channels_rather_than_filling_the_first(self) -> None:
        record = build_record("Launch", "mixed", "other", "generic", ["meta", "tiktok", "web"],
                              request="Ra mắt sản phẩm, ngân sách nhỏ")
        used = [asset["channel"] for asset in record["assets"]]
        self.assertEqual(len(record["assets"]), 4)
        self.assertEqual({"meta", "tiktok", "web"}, set(used), f"assets clustered on {sorted(set(used))}")

    def test_budget_tier_is_a_tier_and_never_an_invented_amount(self) -> None:
        """A tier can be read from wording. A number in đồng cannot, and it is the one figure the
        budget deliverable exists to derive from."""
        for request in (self.BUN_BO, "large budget campaign", "ngân sách vừa"):
            signals = read_signals(request)
            self.assertIn(signals["budget"]["tier"], BUDGET_TIERS)
            blob = json.dumps(signals, ensure_ascii=False)
            for invented in ("triệu", "VND", "đồng", "$"):
                self.assertNotIn(invented, blob, f"{request!r} produced a currency figure: {blob}")

    def test_human_prompt_uses_physical_capture_contract(self) -> None:
        prompt = compile_provider(
            {
                "mode": "human",
                "brief": {"objective": "Lip tint lifestyle"},
                "prompt": {
                    "capture_mode": "studio-natural",
                    "lens_distance": "85mm behavior from portrait distance",
                    "makeup_skin": "sheer satin base with visible pores",
                    "makeup_eyes": "taupe wash, fine brown liner, separated lashes",
                    "makeup_lips": "rosewood balm with soft edges",
                },
            },
            "openai",
        )
        self.assertIn("CAPTURE MODE", prompt)
        self.assertIn("studio-natural", prompt)
        self.assertIn("85mm behavior", prompt)
        self.assertIn("MAKEUP AND GROOMING", prompt)
        self.assertIn("sheer satin base", prompt)
        self.assertIn("taupe wash", prompt)
        self.assertIn("rosewood balm", prompt)
        self.assertIn("LIGHTING GEOMETRY", prompt)
        self.assertNotIn("K-pop-inspired makeup", prompt)

    def test_product_prompt_does_not_ask_for_skin_hair_or_fabric(self) -> None:
        """Capture modes were written in person vocabulary and emitted for products too, so a
        serum-bottle prompt carried "natural skin, hair, fabric, posture" into the renderer. A
        test render came back with silk drapery filling the copy area the brief reserved."""
        prompt = compile_provider(
            {"mode": "product", "prompt": {"capture_mode": "studio-natural", "subject_action": "One glass bottle"}},
            "generic",
        )
        capture = prompt.split("CAPTURE MODE")[1].split("\n\n")[0].lower()
        for word in ("skin", "hair", "fabric", "posture"):
            self.assertNotIn(word, capture, f"product capture mode invites {word}")
        # The person wording still exists; it is only supposed to be reachable from a person mode.
        person = compile_provider({"mode": "human", "prompt": {"capture_mode": "studio-natural"}}, "generic")
        self.assertIn("natural skin, hair, fabric, posture", person)

    def test_copy_area_is_an_instruction_that_outranks_the_rest_of_the_brief(self) -> None:
        """It used to be emitted as a fact — "Copy-safe area: Upper-left 40 percent" — which a
        renderer cannot act on, and a test render duly filled it. Briefs also contradict
        themselves about it, so the compiled prompt has to say which line wins."""
        prompt = compile_provider(
            {"mode": "product", "prompt": {"copy_safe_area": "Upper-left 40 percent", "aspect_ratio": "4:5"}},
            "generic",
        )
        self.assertIn("Keep this area of the frame deliberately empty: Upper-left 40 percent", prompt)
        self.assertIn("this empty area wins", prompt)
        # A brief with no reserved area must not leave the renderer guessing either.
        full_bleed = compile_provider({"mode": "product", "prompt": {"aspect_ratio": "1:1"}}, "generic")
        self.assertIn("No copy area is reserved", full_bleed)

    def test_known_ratio_carries_the_size_to_set(self) -> None:
        """The ratio in the prompt text does not shape the pixels; the API size parameter does.
        A prompt that says 4:5 rendered at 1:1 crops away the copy area."""
        prompt = compile_provider({"mode": "product", "prompt": {"aspect_ratio": "4:5"}}, "generic")
        self.assertIn("1024x1280", prompt)
        # An unusual ratio has no honest size to name, so none is invented.
        odd = compile_provider({"mode": "product", "prompt": {"aspect_ratio": "37:11"}}, "generic")
        self.assertNotIn("Set the provider's output size", odd)

    def test_house_negatives_are_added_without_replacing_the_brief(self) -> None:
        """A brief author cannot name every trope in advance, and the ones here are credibility
        failures or physical impossibilities rather than style opinions."""
        prompt = compile_provider(
            {"mode": "product", "prompt": {"negative_constraints": "No fake label"}},
            "generic",
        )
        self.assertIn("No fake label", prompt)
        for trope in ("silk or satin drapery", "no object resting on nothing", "no invented logo"):
            self.assertIn(trope, prompt)

    def test_subject_leads_the_prompt(self) -> None:
        """The opening was the provider name and the capture mode, so the highest-attention
        position went to metadata and the thing being photographed arrived seventh."""
        prompt = compile_provider(
            {"mode": "product", "prompt": {"subject_action": "One frosted bottle", "job": "Hero"}},
            "generic",
        )
        self.assertLess(prompt.index("SUBJECT AND ACTION"), prompt.index("CAPTURE MODE"))
        self.assertLess(prompt.index("FRAME AND NEGATIVE SPACE"), prompt.index("SCENE AND ART DIRECTION"))
        self.assertLess(prompt.index("LIGHTING GEOMETRY"), prompt.index("JOB"))

    def test_shipped_bun_bo_key_visual_reserves_an_area_nothing_else_occupies(self) -> None:
        """The contradiction this catches was one I shipped: the scene put the stock pot behind
        camera-left while the copy area reserved the upper-left, and the render filled it."""
        path = SKILL_ROOT / "assets" / "examples" / "bun-bo" / "key-visual.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        brief = record["prompt"]
        reserved = brief["copy_safe_area"].lower()
        side = "left" if "left" in reserved else "right"
        for field in ("scene", "composition"):
            self.assertNotIn(
                f"camera-{side}",
                brief[field].lower(),
                f"{field} places something on the {side} while the copy area reserves the {side}",
            )

    def test_provider_compilers(self) -> None:
        record = {"mode": "product", "brief": {"objective": "Product hero"}}
        for provider in (
            "generic",
            "openai",
            "gpt-image-2",
            "nano-banana-2-lite",
            "nano-banana-2",
            "nano-banana-pro",
            "midjourney",
            "flux",
            "ideogram",
            "firefly",
        ):
            self.assertIn("PROVIDER:", compile_provider(record, provider))

    def test_generic_edit_prompt_has_localized_contract(self) -> None:
        prompt = compile_provider(
            {
                "mode": "product",
                "operation": "edit",
                "prompt": {"change": "background only", "lock": "exact bottle, cap, and label"},
            },
            "gpt-image-2",
        )
        self.assertIn("LOCALIZED EDIT CONTRACT", prompt)
        self.assertIn("CHANGE: background only", prompt)
        self.assertIn("LOCK: exact bottle, cap, and label", prompt)
        self.assertIn("MATCH:", prompt)
        self.assertIn("MASK:", prompt)

    def test_virtual_person_planner_recommends_douyin_direction(self) -> None:
        result = plan_virtual_person(
            {
                "purpose": "Recurring beauty creator",
                "vibe": "Romantic Douyin idol",
                "audience": "Beauty shoppers",
            }
        )
        self.assertTrue(result["adult_only"])
        self.assertEqual(result["recommended_selection"]["build"], "B1")
        self.assertEqual(result["recommended_selection"]["makeup"], "M3")
        self.assertEqual(result["selected_profile"]["makeup"], "douyin-luminous")

    def test_virtual_person_prompt_keeps_identity_separate_from_styling(self) -> None:
        prompt = compile_provider(
            {
                "mode": "virtual-person",
                "brief": {"objective": "Create a recurring virtual beauty creator"},
                "prompt": {
                    "face_impression": "soft-romantic with a small original cheek mole",
                    "body_build": "healthy slender-light-frame adult build",
                    "makeup_eyes": "anatomy-following aegyo-sal, fine brown liner, separated lashes",
                    "allowed_variation": "makeup and wardrobe may vary; biological identity may not",
                },
            },
            "nano-banana-2",
        )
        self.assertIn("VIRTUAL PERSON DESIGN", prompt)
        self.assertIn("healthy slender-light-frame adult build", prompt)
        self.assertIn("anatomy-following aegyo-sal", prompt)
        self.assertIn("biological identity may not", prompt)

    def test_router_uses_openai_n_for_same_prompt_variants(self) -> None:
        result = route_image_request({"description": "Portrait study", "variant_count": 4, "same_prompt_variants": True})
        self.assertEqual(result["model"], "gpt-image-2")
        self.assertEqual(result["api_operation"], "images.generate")
        self.assertEqual(result["request_count"], 1)
        self.assertIn("n=4", result["variant_strategy"])

    def test_router_uses_nano_banana_for_multiple_references(self) -> None:
        result = route_image_request(
            {
                "description": "Fashion campaign",
                "reference_images": [{"role": "lighting"}, {"role": "pose"}, {"role": "styling"}, {"role": "composition"}],
                "variant_count": 5,
            }
        )
        self.assertEqual(result["model"], "gemini-3.1-flash-image")
        self.assertEqual(result["request_count"], 5)
        self.assertIn("independent interactions", result["variant_strategy"])

    def test_router_uses_pro_for_complex_brand_text(self) -> None:
        result = route_image_request({"description": "Localized campaign poster", "complex_layout_or_text": True})
        self.assertEqual(result["model"], "gemini-3-pro-image")

    def test_router_uses_responses_for_conversational_editing(self) -> None:
        result = route_image_request(
            {
                "description": "Refine this portrait conversationally",
                "reference_images": [{"role": "edit-target"}],
                "reference_intent": "preserve-authorized-subject",
                "operation": "edit",
                "multi_turn": True,
            }
        )
        self.assertEqual(result["api_surface"], "OpenAI Responses API image_generation tool")
        self.assertEqual(result["api_operation"], "action=edit")

    def test_identity_sensitive_prompt_locks_face_structure(self) -> None:
        prompt = compile_provider(
            {
                "mode": "outfit-edit",
                "brief": {"objective": "Replace the outfit with an ivory tailored look"},
                "prompt": {"locks": "Keep the supplied person exact"},
            },
            "gpt-image-2",
        )
        self.assertIn("IDENTITY-PRESERVING EDIT CONTRACT", prompt)
        self.assertIn("eye shape and spacing", prompt)
        self.assertIn("Makeup may change pigment", prompt)
        self.assertIn("Reject face drift", prompt)

    def test_manifest_lineage(self) -> None:
        rows = build_manifest({"project": "Barrier Reset", "selected_lanes": ["signature"]}, ["meta"])
        self.assertEqual(len(rows), 3)
        self.assertTrue(rows[0]["filename"].startswith("barrier-reset-signature-meta"))

    def test_all_in_one_planner_routes_commerce_and_limits_scope(self) -> None:
        plan = plan_marketing_system(
            {
                "project": "Ceramic launch",
                "objective": "Sell a new mug through a PDP and marketplace listing",
                "product_family": "home",
                "channels": ["pdp", "marketplace"],
                "asset_scope": "focused",
                "proof": ["Exact dimensions", "Glaze reference"],
            }
        )
        self.assertEqual(plan["primary_job"], "commerce-merchandising")
        self.assertLessEqual(plan["asset_count"], 8)
        self.assertTrue(all(asset["family"] in {"commerce", "owned"} for asset in plan["selected_assets"]))

    def test_vietnamese_plan_routes_to_strategy_workbench(self) -> None:
        plan = plan_marketing_system(
            {"request": "Tôi không biết marketing, hãy làm kế hoạch từ đầu cho quán bún bò"}
        )
        self.assertEqual(plan["primary_job"], "strategy-offer")

    def test_system_scope_connects_multiple_workbenches(self) -> None:
        plan = plan_marketing_system(
            {
                "project": "Beauty launch",
                "objective": "Launch and sell through ecommerce, paid ads, social content and PR",
                "product_family": "beauty",
                "channels": ["pdp", "marketplace", "paid", "instagram", "pr"],
                "asset_scope": "system",
                "proof": ["Exact packshot"],
            }
        )
        active_jobs = {plan["primary_job"], *plan["supporting_jobs"]}
        self.assertIn("campaign-launch", active_jobs)
        self.assertIn("commerce-merchandising", active_jobs)
        self.assertIn("pr-communications", active_jobs)
        self.assertIn("content-distribution", active_jobs)
        self.assertLessEqual(plan["asset_count"], 14)

    def test_manifest_uses_planned_assets_without_cartesian_product(self) -> None:
        request = {
            "project": "Ceramic launch",
            "objective": "Sell through PDP and marketplace",
            "product_family": "home",
            "channels": ["pdp", "marketplace"],
            "asset_scope": "focused",
            "proof": ["Exact dimensions"],
        }
        rows = build_manifest(request, ["pdp", "marketplace"])
        self.assertGreater(len(rows), 0)
        self.assertLessEqual(len(rows), 8)
        self.assertEqual(len({row["asset_type"] for row in rows}), len(rows))

    def test_critical_gate_rejects_high_score(self) -> None:
        record = {
            "asset_id": "A-1",
            "critical_gates": {"product_fidelity": False},
            "scores": {
                "strategy": 20,
                "fidelity": 20,
                "distinction": 20,
                "craft": 20,
                "channel": 10,
                "rights_claims": 10,
            },
        }
        result = evaluate(record)
        self.assertEqual(result["total"], 100)
        self.assertEqual(result["status"], "rejected-critical")

    def test_performance_metrics(self) -> None:
        data = "asset_id,lane,channel,impressions,clicks,views3s,conversions,spend,revenue\nA-1,clear,meta,10000,200,3000,20,100,400\n"
        rows = list(csv.DictReader(io.StringIO(data)))
        result = analyze(rows)[0]
        self.assertAlmostEqual(result["ctr"], 0.02)
        self.assertAlmostEqual(result["cvr"], 0.1)
        self.assertAlmostEqual(result["roas"], 4.0)
        self.assertFalse(result["sample_warning"])


def _sequence(**overrides: object) -> dict:
    """A two-shot sequence whose second shot declares only what changes."""
    spec: dict = {
        "title": "Fixture",
        "duration_s": 6,
        "production_mode": "generative",
        "world": {"product": "A plain white bowl", "location": "A steel counter"},
        "shots": [
            {
                "id": "S1",
                "job": "hook",
                "duration_s": 3.0,
                "action": "Broth pours into the bowl",
                "set": {
                    "screen_direction": "left-to-right",
                    "light_direction": "soft key 45 degrees camera-left",
                    "material_state": "steam rising continuously",
                },
            },
            {
                "id": "S2",
                "job": "proof",
                "duration_s": 3.0,
                "action": "Chopsticks lift the noodles",
                "set": {"material_state": "steam thinning after the pour"},
            },
        ],
    }
    spec.update(overrides)
    return spec


class VideoSequenceTests(unittest.TestCase):
    """The bug these cover: shot prompts that each described the world in their own words, so
    the light jumped sides and the steam reset at every cut. Continuity now has to be broken
    on purpose, and the four guards below are the ones that used to be prose nobody enforced."""

    def test_state_carries_into_a_shot_that_never_mentions_it(self) -> None:
        """S2 says nothing about light or screen direction, and must still be locked to both."""
        sequence = resolve(_sequence())
        second = sequence["shots"][1]
        self.assertEqual(sequence["problems"], [])
        carried = dict(second["carried"])
        self.assertEqual(carried["light_direction"], "soft key 45 degrees camera-left")
        self.assertEqual(carried["screen_direction"], "left-to-right")
        # What it did declare is reported as a change with both sides, so the prompt can say
        # "from this, to that" rather than describing the new state in isolation.
        self.assertEqual(
            second["changed"],
            [("material_state", "steam rising continuously", "steam thinning after the pour")],
        )

    def test_every_shot_shares_one_byte_identical_lock(self) -> None:
        """Two paraphrases of the same bowl are two different bowls to a generative model."""
        sequence = resolve(_sequence())
        lock = lock_block(sequence)
        self.assertIn("A plain white bowl", lock)
        for index in range(len(sequence["shots"])):
            self.assertIn(lock, shot_prompt(sequence, index))

    def test_reject_list_is_derived_from_what_the_shot_carried(self) -> None:
        """A hand-written reject list drifts out of agreement with the locks above it."""
        sequence = resolve(_sequence())
        prompt = shot_prompt(sequence, 1)
        rejects = prompt.split("REJECT")[1]
        self.assertIn("the key light jumping to the opposite side", rejects)
        # material_state changed in S2, so forbidding the change would contradict the brief.
        self.assertNotIn("steam resetting or looping", rejects)

    def test_screen_direction_may_not_reverse_on_a_straight_cut(self) -> None:
        """Crossing the line reads as the subject turning around. Legitimate, but only behind
        a cutaway, so the spec has to declare one and take responsibility for it."""
        spec = _sequence()
        spec["shots"][1]["set"]["screen_direction"] = "right-to-left"
        self.assertTrue(any("screen direction reverses" in p for p in resolve(spec)["problems"]))

        spec["shots"][1]["cutaway"] = True
        self.assertEqual(resolve(spec)["problems"], [])

    def test_misspelled_continuity_key_is_refused(self) -> None:
        """The worst failure available here: the value looks written down and reaches no prompt."""
        spec = _sequence()
        spec["shots"][1]["set"]["light_dir"] = "camera-right"
        self.assertTrue(any("unknown continuity key" in p for p in resolve(spec)["problems"]))

    def test_generative_shots_stay_under_the_drift_ceiling(self) -> None:
        """Drift grows with shot length, so a long generative take is a defect, not a choice."""
        spec = _sequence(duration_s=12)
        spec["shots"][0]["duration_s"] = 9.0
        self.assertTrue(any("generative ceiling" in p for p in resolve(spec)["problems"]))
        # The same shot is fine when it is going to be filmed rather than generated.
        self.assertEqual(resolve({**spec, "production_mode": "live-action"})["problems"], [])

    def test_durations_must_add_up_to_the_placement(self) -> None:
        spec = _sequence()
        spec["shots"][0]["duration_s"] = 4.0
        self.assertTrue(any("will not fit the placement" in p for p in resolve(spec)["problems"]))

    def test_on_screen_numbers_are_flagged_for_verification(self) -> None:
        """The script cannot know whether a price is real, only that somebody must check."""
        spec = _sequence()
        spec["shots"][1]["text"] = "Chỉ 45.000đ"
        sequence = resolve(spec)
        self.assertEqual(sequence["problems"], [])
        self.assertTrue(any("verify before publishing" in note for note in sequence["notes"]))

    def test_shipped_bun_bo_sequence_resolves_clean(self) -> None:
        """The worked example is what a reader copies, so it must pass every guard above."""
        path = SKILL_ROOT / "assets" / "examples" / "bun-bo" / "video-sequence.json"
        sequence = resolve(json.loads(path.read_text(encoding="utf-8")))
        self.assertEqual(sequence["problems"], [])
        self.assertEqual(sequence["total_s"], 15.0)
        # Nothing may be left unspecified, or no shot can lock it.
        self.assertEqual([n for n in sequence["notes"] if "never specified" in n], [])


SUBSTANTIVE_SECTION = (
    "The mid-tier segment competes on taste consistency rather than location, which is where "
    "the gap sits. Three nearby shops describe themselves in nearly identical language and none "
    "of them says anything about how the broth is actually made."
)


def _doc(*sections: tuple[str, str], status: str = "final") -> str:
    head = f"<!-- minthep:deliverable id=05-positioning lang=vi status={status} -->\n# Positioning\n\n"
    return head + "\n".join(f"## {title}\n\n{body}\n" for title, body in sections)


class RunWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_registry()

    def test_vietnamese_phrasing_routes_to_each_pipeline(self) -> None:
        cases = {
            "tôi muốn lên kế hoạch marketing cho quán bún bò": "plan-from-zero",
            "làm menu cho quán, thiết kế wireframe": "design-render",
            "tôi có hình ảnh này, muốn tạo ảnh branding sản phẩm": "image-from-reference",
            "làm video quảng cáo tiktok": "video-campaign",
            "phân tích hiệu quả quảng cáo và tối ưu": "optimize-iterate",
            "nghiên cứu thị trường và đối thủ cạnh tranh": "deep-research",
        }
        for request, expected in cases.items():
            with self.subTest(request=request):
                routing = route_pipeline({"request": request}, self.registry)
                self.assertEqual(routing["pipeline"], expected)

    def test_explicit_pipeline_overrides_keyword_routing(self) -> None:
        routing = route_pipeline(
            {"request": "lên kế hoạch marketing", "pipeline": "video-campaign"}, self.registry
        )
        self.assertEqual(routing["pipeline"], "video-campaign")
        self.assertEqual(routing["reason"], "explicitly requested")

    def test_unmatched_request_falls_back_to_plan_from_zero(self) -> None:
        routing = route_pipeline({"request": "zzzz qqqq"}, self.registry)
        self.assertEqual(routing["pipeline"], "plan-from-zero")
        self.assertIn("no signal", routing["reason"])
        self.assertEqual(max(routing["scores"].values()), 0)

    def test_unsupported_pipeline_and_mode_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            route_pipeline({"pipeline": "make-me-famous"}, self.registry)
        with self.assertRaises(ValueError):
            build_run({"request": "kế hoạch", "mode": "turbo"}, self.registry)
        with self.assertRaises(ValueError):
            build_run({"request": "kế hoạch", "languages": ["fr"]}, self.registry)

    def test_slug_strips_vietnamese_diacritics(self) -> None:
        run = build_run({"request": "kế hoạch", "project": "Bún Bò Huế Đà Nẵng"}, self.registry)
        self.assertEqual(run["run_id"].split("-", 3)[3], "bun-bo-hue-da-nang")

    def test_long_slug_cuts_at_a_word_boundary(self) -> None:
        run = build_run(
            {"request": "tôi muốn lên kế hoạch marketing cho quán bún bò Huế", "date": "2026-01-01"},
            self.registry,
        )
        slug = run["run_id"].removeprefix("2026-01-01-")
        self.assertLessEqual(len(slug), 48)
        self.assertFalse(slug.endswith("-"), slug)
        self.assertEqual(slug, "toi-muon-len-ke-hoach-marketing-cho-quan-bun-bo")

    def test_slug_falls_back_when_the_request_has_no_usable_characters(self) -> None:
        run = build_run({"request": "!!! ???", "date": "2026-01-01"}, self.registry)
        self.assertEqual(run["run_id"], "2026-01-01-run")

    def test_mode_widens_the_deliverable_set(self) -> None:
        counts = {}
        for mode in ("focused", "system", "production"):
            run = build_run({"request": "lên kế hoạch marketing", "mode": mode}, self.registry)
            counts[mode] = len(run["deliverables"])
        self.assertLess(counts["focused"], counts["system"])
        self.assertLessEqual(counts["system"], counts["production"])

    def test_pipeline_defaults_cover_promised_artifacts(self) -> None:
        plan = build_run({"request": "Tôi không biết marketing, làm kế hoạch từ đầu"}, self.registry)
        image = build_run({"request": "Sửa ảnh này thành key visual"}, self.registry)
        design = build_run({"request": "Thiết kế menu cho quán"}, self.registry)
        video = build_run({"request": "Làm video TikTok và shot list"}, self.registry)
        self.assertEqual(plan["mode"], "system")
        self.assertEqual(image["mode"], "system")
        self.assertEqual(design["mode"], "system")
        self.assertEqual(video["mode"], "system")
        self.assertIn("08-copy-pack", {item["id"] for item in plan["deliverables"]})
        self.assertIn("08-qa", {item["id"] for item in image["deliverables"]})
        self.assertIn("08-print-export", {item["id"] for item in design["deliverables"]})
        self.assertIn("07-audio-captions", {item["id"] for item in video["deliverables"]})

    def test_render_request_promotes_visual_pipeline_to_production(self) -> None:
        run = build_run({"request": "Thiết kế menu và render file PNG để in ấn"}, self.registry)
        self.assertEqual(run["mode"], "production")

    def test_mixed_menu_video_request_keeps_a_supporting_pipeline(self) -> None:
        run = build_run(
            {"request": "Làm 3 option menu hiện đại, render option tốt nhất và thêm video TikTok 15s"},
            self.registry,
        )
        self.assertEqual(run["pipeline"], "design-render")
        self.assertIn("video-campaign", run["supporting_pipelines"])

    def test_start_workbench_creates_linked_runs_and_capability_records(self) -> None:
        request = {
            "request": "Làm 3 option menu, render option tốt nhất và thêm video TikTok 15s",
            "date": "2026-01-01",
        }
        with tempfile.TemporaryDirectory() as tmp:
            result = start(request, Path(tmp))
            primary = Path(result["run_dir"])
            self.assertTrue((primary / "_meta" / "render-capability.json").exists())
            self.assertEqual(result["supporting_runs"][0]["pipeline"], "video-campaign")
            supporting = Path(result["supporting_runs"][0]["run_dir"])
            self.assertTrue((supporting / "_meta" / "render-capability.json").exists())
            self.assertTrue((supporting / "production-files" / "exports" / "README.md").exists())

    def test_write_run_creates_bilingual_pairs_and_manifest(self) -> None:
        run = build_run(
            {"request": "lên kế hoạch marketing", "project": "Bun Bo", "mode": "system", "date": "2026-07-29"},
            self.registry,
        )
        with tempfile.TemporaryDirectory() as tmp:
            written = write_run(run, Path(tmp))
            run_dir = Path(tmp) / "runs" / run["run_id"]
            self.assertTrue((run_dir / "run.json").exists())
            self.assertTrue((run_dir / "README.md").exists())
            self.assertGreater(len(written["files_written"]), 20)
            self.assertIn("run.json", written["files_written"])
            bilingual = [item for item in run["deliverables"] if item["bilingual"]]
            self.assertGreater(len(bilingual), 5)
            for entry in bilingual:
                for rel in entry["paths"]:
                    self.assertTrue((run_dir / rel).exists(), rel)
            manifest = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["pipeline"], "plan-from-zero")

    def test_write_run_refuses_to_clobber_without_force(self) -> None:
        run = build_run({"request": "lên kế hoạch marketing", "date": "2026-07-29"}, self.registry)
        with tempfile.TemporaryDirectory() as tmp:
            write_run(run, Path(tmp))
            with self.assertRaises(FileExistsError):
                write_run(run, Path(tmp))
            write_run(run, Path(tmp), force=True)


class RunAuditTests(unittest.TestCase):
    def _audit_doc(self, text: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "05-positioning.vi.md"
            path.write_text(text, encoding="utf-8")
            return audit_file(path)

    def test_fresh_workspace_is_not_filled_and_strict_would_fail(self) -> None:
        run = build_run(
            {"request": "lên kế hoạch marketing", "mode": "system", "date": "2026-07-29"}
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_run(run, Path(tmp))
            report = audit_run(Path(tmp) / "runs" / run["run_id"])
        self.assertFalse(report["filled"])
        self.assertFalse(report["complete"])
        self.assertGreater(report["total_unfilled_sections"], 50)
        self.assertIn("01-intake", report["blocking"])

    def test_unfilled_stub_reports_write_prompts_not_quality_noise(self) -> None:
        result = self._audit_doc(_doc(("Market structure", "> WRITE: describe the segments"), status="empty"))
        self.assertEqual(result["status"], "empty")
        self.assertEqual(result["unfilled_sections"], 1)
        self.assertEqual(result["warnings"], [])

    def test_placeholder_leak_is_flagged(self) -> None:
        result = self._audit_doc(_doc(("Market structure", "Pricing is TBD and the rest is TODO.")))
        self.assertTrue(any("placeholder" in warning for warning in result["warnings"]))

    def test_figures_without_a_source_are_flagged(self) -> None:
        body = "The segment is 1.134.000 people, growing 12,5% with an average ticket of 45.000 VND."
        result = self._audit_doc(_doc(("Market structure", body)))
        self.assertTrue(any("no source URL" in warning for warning in result["warnings"]))

    def test_figures_with_a_source_are_clean(self) -> None:
        body = (
            "The segment is 1.134.000 people, growing 12,5% with an average ticket of 45.000 VND, "
            "per https://danang.gov.vn retrieved 2026-07-29. The arithmetic behind the range is "
            "shown in the sizing appendix so a reader can rebuild it without trusting the number."
        )
        result = self._audit_doc(_doc(("Market structure", body)))
        self.assertEqual(result["warnings"], [])

    def test_one_liner_sections_are_flagged_as_thin(self) -> None:
        result = self._audit_doc(
            _doc(
                ("Market structure", "Three segments exist."),
                ("Nearest rivals", "Three shops nearby."),
                ("Differentiating idea", "Twelve-hour broth."),
                ("Positioning statement", "For office workers."),
            )
        )
        self.assertTrue(any("thin" in warning for warning in result["warnings"]))

    def test_substantive_sections_are_not_flagged_as_thin(self) -> None:
        result = self._audit_doc(
            _doc(
                ("Market structure", SUBSTANTIVE_SECTION),
                ("Nearest rivals", SUBSTANTIVE_SECTION),
                ("Differentiating idea", SUBSTANTIVE_SECTION),
                ("Positioning statement", SUBSTANTIVE_SECTION),
            )
        )
        self.assertEqual(result["warnings"], [])

    def test_csv_with_header_only_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claims.csv"
            path.write_text("claim_id,claim,evidence\n", encoding="utf-8")
            self.assertEqual(audit_file(path)["status"], "empty")
            path.write_text("claim_id,claim,evidence\nC-1,12h broth,kitchen log\n", encoding="utf-8")
            self.assertEqual(audit_file(path)["status"], "final")

    def test_invalid_json_deliverable_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "02-reference-map.json"
            path.write_text("{not json", encoding="utf-8")
            result = audit_file(path)
        self.assertEqual(result["status"], "invalid")
        self.assertTrue(any("invalid JSON" in issue for issue in result["issues"]))


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parent

# Paths a run workspace creates at runtime. They are named in the prose on purpose and are
# not expected to exist in the repository.
RUNTIME_ARTIFACTS = {
    "_meta/render-capability.json",
    # video-craft-and-production.md tells the reader to keep a log of every generation attempt.
    # It is an output of following the dossier, not a cross-reference into this repository.
    "generation_log.csv",
}
# Files the operator may supply, which the skill degrades gracefully without.
OPTIONAL_INPUTS = {"BRAND.md"}

FILE_REFERENCE = re.compile(
    r"`([^`\s]+\.(?:md|json|py|csv|yaml|yml))`"
    r"|\]\(([^)\s]+\.(?:md|json|py|csv|yaml|yml))\)"
)


def _frontmatter_description(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip('"')
    raise AssertionError(f"{path} has no description in its frontmatter")


class ReferenceIntegrityTests(unittest.TestCase):
    """A reference the skill cannot open is worse than no reference: it reads as depth
    that does not ship. This caught three pointers into a gitignored research folder."""

    def test_every_cited_file_exists_somewhere_the_skill_can_reach(self) -> None:
        # REPO_ROOT is a legitimate base: SKILL.md names the .claude/ and .codex/ adapters by
        # their repository-root paths, because that is where an operator installs them from.
        bases = (
            SKILL_ROOT / "references",
            SKILL_ROOT,
            SKILL_ROOT / "scripts",
            SKILL_ROOT / "assets",
            REPO_ROOT,
        )
        unresolved = []
        for document in sorted(SKILL_ROOT.rglob("*.md")):
            text = document.read_text(encoding="utf-8", errors="replace")
            for match in FILE_REFERENCE.finditer(text):
                ref = match.group(1) or match.group(2)
                if any(ch in ref for ch in "*<>{}") or ref in RUNTIME_ARTIFACTS | OPTIONAL_INPUTS:
                    continue
                candidates = (document.parent, *bases)
                if not any((base / ref).exists() for base in candidates):
                    unresolved.append(f"{document.relative_to(SKILL_ROOT)} -> {ref}")
        self.assertEqual(unresolved, [], f"unresolved file references: {unresolved}")

    def test_no_reference_is_unreachable_from_the_router(self) -> None:
        """A reference nothing routes to will never be loaded, so its knowledge is dead
        weight. SKILL.md, the router, and the pipeline registry are the three entry points
        an agent reads; every operational reference must be named by one of them."""
        entries = [
            SKILL_ROOT / "SKILL.md",
            SKILL_ROOT / "references" / "marketing-system-router.md",
            SKILL_ROOT / "assets" / "registries" / "pipelines.json",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in entries)
        orphans = [
            path.name
            for path in sorted((SKILL_ROOT / "references").glob("*.md"))
            # evaluation-suite.md is a maintainer's forward-test harness, not a module an
            # agent loads mid-task. Routing to it would be wrong.
            if path.name != "evaluation-suite.md" and path.name not in text
        ]
        self.assertEqual(orphans, [], f"references nothing routes to: {orphans}")

    def test_skill_md_stays_within_the_progressive_disclosure_budget(self) -> None:
        """SKILL.md is loaded on every activation, so its length is a tax on every request.
        Detail belongs in references/, which load only when a decision needs them."""
        skill = SKILL_ROOT / "SKILL.md"
        lines = skill.read_text(encoding="utf-8").splitlines()
        self.assertLess(len(lines), 150, f"SKILL.md is {len(lines)} lines")
    def test_the_description_is_wide_enough_to_be_found(self) -> None:
        """The description is not prose the user reads; it is the only text a runtime matches a
        request against before loading anything. Holding it to one tidy sentence was a mistake:
        "branding imagery from a reference photo, menu and wireframe design" does not contain
        campaign, palette, retouch, press kit, lifecycle, or a single Vietnamese word, so a man
        typing "giúp tôi lên chiến dịch quảng cáo" matched nothing. Width here costs one
        activation-time string; missing the match costs the whole skill. 1024 characters is the
        documented ceiling, so the test guards that and the coverage rather than brevity."""
        value = _frontmatter_description(SKILL_ROOT / "SKILL.md")
        self.assertLessEqual(len(value), 1024, f"description is {len(value)} chars")
        for term in ("campaign", "copywriting", "colour", "layout", "image editing", "video"):
            self.assertIn(term, value.lower(), f"description never mentions {term}")
        for term in ("chiến dịch", "thiết kế menu", "chỉnh sửa ảnh", "màu sắc"):
            self.assertIn(term, value, f"description never mentions {term}")

    def test_runtime_adapters_advertise_the_canonical_description(self) -> None:
        """The adapters are what each runtime actually indexes for skill discovery. When their
        description drifts from the canonical one, the skill stops being found for the work it
        now does — which is how both adapters ended up advertising a capability set two
        rewrites out of date."""
        canonical = _frontmatter_description(SKILL_ROOT / "SKILL.md")
        for adapter in (".claude", ".codex"):
            path = REPO_ROOT / adapter / "skills" / "marketing-minthep" / "SKILL.md"
            self.assertEqual(
                _frontmatter_description(path),
                canonical,
                f"{adapter} adapter description has drifted from the canonical SKILL.md",
            )

    def test_dossiers_ship_and_are_indexed(self) -> None:
        dossier_dir = SKILL_ROOT / "references" / "dossiers"
        dossiers = sorted(path.name for path in dossier_dir.glob("*.md") if path.name != "README.md")
        self.assertGreaterEqual(len(dossiers), 8)
        index = (dossier_dir / "README.md").read_text(encoding="utf-8")
        for name in dossiers:
            self.assertIn(name, index, f"{name} is not listed in the dossier index")

    def test_dossiers_do_not_present_illustrative_numbers_as_measured(self) -> None:
        """Worked examples invent numbers so the arithmetic can be followed. Any dossier
        that does so must say so, or a reader will publish a fabricated figure."""
        dossier_dir = SKILL_ROOT / "references" / "dossiers"
        for path in sorted(dossier_dir.glob("*.md")):
            if path.name == "README.md":
                continue
            lines = path.read_text(encoding="utf-8", errors="replace").lower().splitlines()
            # What protects the reader is that the convention is explained before they meet a
            # fabricated number — not that it sits in any particular section. An earlier version
            # only searched the scope header, which rejected a dossier that declared it in an
            # evidence-key table instead. A line that both marks and explains counts as the
            # declaration, since that is how a marker glossary is written.
            # Each phrase is a complete instruction to the reader, not a keyword: either the
            # number is declared fake, or the reader is told to swap it for a measured one before
            # anything ships. Both close the hole. Matching only one house style rejected
            # dossiers that chose the other.
            explains = (
                "not real",
                "invented",
                "never quote",
                "never publish",
                "replace illustrative numbers",
                "with measured ones before publishing",
            )
            declared = False
            for number, line in enumerate(lines, start=1):
                if any(phrase in line for phrase in explains):
                    declared = True
                if "[illustrative]" in line:
                    self.assertTrue(
                        declared,
                        f"{path.name}:{number} uses an [illustrative] figure before explaining "
                        "that such numbers are invented and must not be published",
                    )
                    break


if __name__ == "__main__":
    unittest.main()
