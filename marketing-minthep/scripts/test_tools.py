#!/usr/bin/env python3
"""Focused tests for the deterministic Marketing-Minthep tools."""

from __future__ import annotations

import argparse
import contextlib
import csv
import io
import json
import math
import statistics
import sys
import unicodedata
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from unittest import mock

from _signals import BUDGET_TIERS, phase_plan, read_signals
from analyze_performance import analyze
from build_asset_manifest import build_manifest
from compile_prompt import compile_provider
# Imported as modules, not names: both define PLACEMENTS, and `from ... import PLACEMENTS` twice
# would leave one test silently asserting against the other module's table.
import audit_seo_page
import check_address_register
import check_claims
import check_evidence_saturation
import check_prompt_grammar
import check_test_readout
import check_tracking_plan
import price_offer
import check_specificity
import find_recipe
import generate_image
import list_capabilities
import model_affiliate
import plan_command_chain
import plan_composition_set
import plan_identity
import plan_operating_load
import plan_palette
import render_refsheet
import rewrite_human
import score_kpi
import size_market
import run_status
from new_run import build_run, load_registry, route_pipeline, write_run
from plan_image_generation import route_image_request
from plan_design_options import plan_options
from plan_marketing_system import PRODUCT_PROOF, plan_marketing_system
from plan_video_sequence import lock_block, resolve, shot_prompt
from plan_virtual_person import plan_virtual_person
from render_mockup import CAP, DROP, FONTS_WITHOUT_VIETNAMESE, SANS, SERIF, THEMES, advance, render, wrap
from render_social_post import PLACEMENTS, caption_sheet, render as render_post
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

    def test_virtual_person_is_reproducible_from_its_parameters(self) -> None:
        # The one thing a brand face has to do is appear in the next fifty posts as the same person.
        # The version this replaced keyword-matched four adjective bundles with no seed, so two runs
        # of one request produced the same words and different people. Identity is now a function of
        # the locked parameter values, which means flag order cannot change it.
        one = plan_virtual_person({"values": {"canthal-tilt": "6", "stature-head-units": "7.4"}})
        two = plan_virtual_person({"values": {"stature-head-units": "7.4", "canthal-tilt": "6"}})
        self.assertTrue(one["adult_only"])
        self.assertEqual(one["identity"]["person_id"], two["identity"]["person_id"])
        self.assertEqual(one["identity"]["seed"], two["identity"]["seed"])
        self.assertTrue(one["identity"]["person_id"].startswith("vp-"))

        moved = plan_virtual_person({"values": {"canthal-tilt": "9", "stature-head-units": "7.4"}})
        self.assertNotEqual(one["identity"]["person_id"], moved["identity"]["person_id"])

    def test_virtual_person_separates_locked_identity_from_campaign_styling(self) -> None:
        sheet = plan_virtual_person({"values": {}})
        locked = set(sheet["locked_identity"])
        styling = set(sheet["campaign_styling"])
        self.assertFalse(locked & styling, "an axis cannot be both the person and the campaign")
        # Pose and camera are what a campaign changes; face and build are what it must not.
        self.assertIn("canthal-tilt", locked)
        self.assertIn("stature-head-units", locked)
        self.assertIn("camera-height", styling)
        self.assertIn("weight-distribution", styling)
        self.assertEqual(sheet["identity"]["hashed_axes"], len(locked))

    def test_virtual_person_refuses_a_minor_and_rejects_out_of_range_values(self) -> None:
        with self.assertRaises(ValueError):
            plan_virtual_person({"minor": True})
        with self.assertRaises(ValueError):
            plan_virtual_person({"values": {"not-an-axis": "3"}})
        out_of_range = plan_virtual_person({"values": {"stature-head-units": "9.2"}})
        self.assertEqual(out_of_range["verdict"], "failed")
        self.assertTrue(any("9.2" in problem for problem in out_of_range["errors"]))

    def test_virtual_person_prompt_fragment_carries_the_supplied_number(self) -> None:
        # A fragment that quotes the table's neutral phrasing for a value somebody chose would print
        # "about seven and a half head heights" for a supplied 7.4. The numbers are what the render
        # gets checked against, so a fragment contradicting them is worse than no fragment at all.
        sheet = plan_virtual_person({"values": {"stature-head-units": "7.4"}})
        identity_fragment = sheet["prompt_fragments"]["identity"]
        self.assertIn("7.4", identity_fragment)
        self.assertNotIn("seven and a half", identity_fragment)
        # An unspecified axis still has to carry its neutral value into the prompt.
        self.assertIn("1.40", identity_fragment)

    def test_virtual_person_makeup_comes_from_the_makeup_table(self) -> None:
        # The version this replaced carried seven bare strings and never touched the 47-row table on
        # disk, so its makeup vocabulary and the skill's makeup unit could drift apart indefinitely.
        good = plan_virtual_person({"values": {}, "makeup": "kr-crying-eye"})
        self.assertEqual(good["makeup"]["look_id"], "kr-crying-eye")
        bad = plan_virtual_person({"values": {}, "makeup": "douyin-luminous"})
        self.assertEqual(bad["verdict"], "failed")
        self.assertTrue(any("makeup-looks.csv" in problem for problem in bad["errors"]))

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


class DeliverableRunLineTests(unittest.TestCase):
    """A deliverable that asks for arithmetic has to name the script that does the arithmetic.

    This class exists because of a cold customer run. `start_workbench.py` scaffolded sixteen
    deliverables for a shop owner who said she knew nothing about marketing, and `11-budget` asked
    her to "derive the CAC ceiling and show the calculation" while `price_offer.py` sat unnamed in
    the same repository. A hand-calculated margin in a filled deliverable is indistinguishable from
    a remembered one, and that is the failure these tests are pointed at - not an empty stub, a
    confidently full one.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_registry()
        cls.script_dir = Path(__file__).resolve().parent
        cls.lines = []  # (pipeline, deliverable id, section or None, run line)
        for name, pipeline in cls.registry["pipelines"].items():
            for spec in pipeline["deliverables"]:
                if spec.get("run"):
                    cls.lines.append((name, spec["id"], None, spec["run"]))
                for section in spec.get("sections", []):
                    if section.get("run"):
                        cls.lines.append((name, spec["id"], section["en"], section["run"]))

    def _scripts_named(self, line: str) -> set[str]:
        return set(re.findall(r"([a-z_]+\.py)", line))

    def test_the_registry_actually_carries_run_lines(self) -> None:
        self.assertGreaterEqual(len(self.lines), 20, "the wiring was reverted")

    def test_every_script_named_in_a_run_line_exists_on_disk(self) -> None:
        for pipeline, did, section, line in self.lines:
            for script in self._scripts_named(line):
                with self.subTest(pipeline=pipeline, deliverable=did, section=section, script=script):
                    self.assertTrue((self.script_dir / script).exists(), script)

    def test_every_script_named_in_a_run_line_is_in_that_pipelines_script_list(self) -> None:
        """Otherwise the pipeline manifest hides a tool the deliverable depends on."""
        for pipeline, did, section, line in self.lines:
            declared = set(self.registry["pipelines"][pipeline]["scripts"])
            for script in self._scripts_named(line):
                with self.subTest(pipeline=pipeline, deliverable=did, script=script):
                    self.assertIn(script, declared)

    def test_run_status_stays_last_in_every_script_list(self) -> None:
        """It is the gate, not a step, and inserting tools after it would read as an order."""
        for name, pipeline in self.registry["pipelines"].items():
            scripts = pipeline["scripts"]
            if "run_status.py" in scripts:
                with self.subTest(pipeline=name):
                    self.assertEqual(scripts[-1], "run_status.py")

    def test_a_run_line_says_what_the_command_settles_not_just_the_command(self) -> None:
        for pipeline, did, section, line in self.lines:
            with self.subTest(pipeline=pipeline, deliverable=did, section=section):
                self.assertTrue(self._scripts_named(line) or line.startswith("The same command"), line)
                self.assertGreater(len(line), 80, "a bare command teaches nothing about why")

    def test_the_arithmetic_sections_of_a_cold_plan_name_their_tool(self) -> None:
        run = build_run(
            {"request": "Tôi mở shop mỹ phẩm nhỏ, không biết gì về marketing, ngân sách nhỏ",
             "date": "2026-01-01"},
            self.registry,
        )
        self.assertEqual(run["pipeline"], "plan-from-zero")
        with tempfile.TemporaryDirectory() as tmp:
            write_run(run, Path(tmp))
            run_dir = Path(tmp) / "runs" / run["run_id"]
            budget = (run_dir / "11-budget-and-unit-economics.en.md").read_text(encoding="utf-8")
            self.assertIn("price_offer.py", budget)
            self.assertIn("--acquisition-cost", budget)
            self.assertIn("Do not hand-calculate this", budget)
            copy = (run_dir / "08-copy-pack.en.md").read_text(encoding="utf-8")
            self.assertIn("check_specificity.py", copy)
            self.assertIn("rewrite_human.py", copy)
            # Order is load-bearing: rhythm edits delete specifics, so facts get counted first.
            self.assertLess(copy.index("check_specificity.py"), copy.index("rewrite_human.py"))
            index = (run_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("`> RUN:` line is a command", index)

    def test_a_run_line_reaches_a_deliverable_with_no_sections(self) -> None:
        run = build_run({"request": "Sửa ảnh này thành key visual", "date": "2026-01-01"}, self.registry)
        self.assertEqual(run["pipeline"], "image-from-reference")
        with tempfile.TemporaryDirectory() as tmp:
            write_run(run, Path(tmp))
            readme = (Path(tmp) / "runs" / run["run_id"] / "07-prompts" / "README.md")
            text = readme.read_text(encoding="utf-8")
            self.assertIn("> RUN:", text)
            self.assertIn("check_prompt_grammar.py", text)

    def test_a_csv_deliverable_names_its_tool_in_the_run_index(self) -> None:
        """A csv is a bare header row, so the command has nowhere to live inside the file."""
        run = build_run({"request": "Làm video TikTok và shot list", "date": "2026-01-01"}, self.registry)
        with tempfile.TemporaryDirectory() as tmp:
            write_run(run, Path(tmp))
            run_dir = Path(tmp) / "runs" / run["run_id"]
            shot_list = next(
                entry for entry in run["deliverables"] if entry["id"] == "04-shot-list"
            )
            self.assertEqual(shot_list["kind"], "csv")
            index = (run_dir / "README.md").read_text(encoding="utf-8")
            self.assertIn("Do not write these by hand", index)
            self.assertIn("plan_video_sequence.py", index)
            # And the csv itself is still only a header, not prose pretending to be data.
            csv_text = (run_dir / "04-shot-list.csv").read_text(encoding="utf-8")
            self.assertNotIn("RUN:", csv_text)
            self.assertEqual(len(csv_text.strip().splitlines()), 1)

    def test_a_run_line_does_not_trip_the_strict_completeness_gate(self) -> None:
        """`> RUN:` is a citation that stays in the finished file, so it may not read as unfinished."""
        filled = (
            "<!-- minthep:deliverable id=11-budget lang=en status=final -->\n"
            "# Budget\n\n## CAC ceiling\n\n"
            "Contribution is 168,000 VND, so the single-purchase ceiling is 168,000.\n\n"
            "> RUN: python scripts/price_offer.py --price 280000 --variable-cost 112000\n"
        )
        self.assertFalse(run_status.WRITE_MARKER.search(filled))
        self.assertFalse(run_status.PLACEHOLDER.search(filled))

    def test_the_registry_still_roundtrips_byte_identically(self) -> None:
        """The run lines were patched programmatically; the file may not carry formatting drift."""
        path = Path(__file__).resolve().parent.parent / "assets" / "registries" / "pipelines.json"
        raw = path.read_text(encoding="utf-8")
        self.assertEqual(json.dumps(json.loads(raw), ensure_ascii=False, indent=2) + "\n", raw)


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


class SocialPostTests(unittest.TestCase):
    """The post renderer has one failure the menu renderer cannot have: a platform draws its own
    buttons over the canvas. Copy inside those bands is not tight, it is hidden."""

    def _spec(self, **overrides: object) -> dict:
        spec = {
            "placement": "feed-portrait",
            "headline": "Nồi nước dùng bắt đầu từ 4 giờ sáng",
            "subhead": "Bố cục mẫu cho bài feed.",
            "proof": ["Giờ mở nồi: chờ quán xác nhận"],
            "cta": "Xem menu",
        }
        spec.update(overrides)
        return spec

    def test_nothing_is_drawn_inside_the_platform_chrome(self) -> None:
        """A story is 1080x1920 but the app owns the top 250px and the bottom 420px. A headline
        there is behind the avatar row; a CTA there is behind the reply field."""
        svg = render_post(self._spec(placement="story"))
        place = PLACEMENTS["story"]
        top, bottom = place["safe_top"], place["height"] - place["safe_bottom"]
        self.assertGreater(top, 0, "the story placement stopped reserving room for app chrome")
        for node in ET.fromstring(svg).iter():
            if node.tag.endswith("text"):
                y = float(node.get("y"))
                self.assertGreater(y, top, f"{node.get('class')} baseline sits in the top chrome")
                self.assertLess(y, bottom, f"{node.get('class')} baseline sits in the bottom chrome")
            if node.tag.endswith("rect") and node.get("width") != "100%":
                self.assertGreaterEqual(float(node.get("y")), top, "a filled box starts in the top chrome")

    def test_the_cta_button_is_measured_against_its_own_label(self) -> None:
        """A fixed-width chip either clips a long label or floats around a short one, and the
        clipped version looks intentional, which is what makes it ship."""
        widths = []
        for label in ("Đặt bàn", "Xem menu", "Nhắn tin để giữ phần cuối ngày"):
            root = ET.fromstring(render_post(self._spec(cta=label)))
            chip = [node for node in root.iter() if node.tag.endswith("rect") and node.get("rx")][0]
            width = float(chip.get("width"))
            self.assertGreater(width, advance(label, 30, bold=True), f"chip narrower than {label!r}")
            widths.append(width)
        self.assertEqual(sorted(widths), widths, "a longer label did not produce a wider button")

    def test_copy_that_cannot_fit_raises_instead_of_overprinting_the_button(self) -> None:
        long_proofs = ["Một dòng bằng chứng dài để chiếm hết chiều cao còn lại của khối chữ"] * 3
        with self.assertRaises(ValueError) as caught:
            render_post(self._spec(placement="feed-square", hero_share=0.56, proof=long_proofs))
        self.assertIn("CTA", str(caught.exception))

    def test_the_caption_sheet_never_invents_the_caption(self) -> None:
        """The image is half a post. The other half is copy nobody wrote yet, and filler there is
        the same failure as a rendered price: it looks finished, so someone posts it."""
        sheet = caption_sheet(self._spec())
        for label in ("Caption (VI)", "Hashtags", "Disclosure"):
            self.assertIn(label, sheet)
        self.assertEqual(sheet.count("UNKNOWN —"), 6, sheet)
        filled = caption_sheet(self._spec(caption_vi="Bán tới khi hết nồi.", hashtags=["#bunbo"]))
        self.assertIn("Bán tới khi hết nồi.", filled)
        self.assertEqual(filled.count("UNKNOWN —"), 4)

    def test_the_shipped_sample_posts_still_render(self) -> None:
        """The two files the README and the demo page point at are built from these specs, so a
        change that breaks them has to fail here rather than in a browser."""
        examples = SKILL_ROOT / "assets" / "examples" / "bun-bo"
        for name in ("post-feed.json", "post-story.json"):
            spec = json.loads((examples / name).read_text(encoding="utf-8"))
            svg = render_post(spec)
            self.assertIn("CONCEPT", svg, f"{name} lost its unapproved-content footer")


class DataTableTests(unittest.TestCase):
    """The tables are the skill's memory, and a wrong cell is a wrong recommendation that reads
    as data. Two of these assertions exist because the first version of the tables failed them:
    a slop tell scoped to a recipe id that had been renamed, and a palette whose contrast claim
    was typed rather than computed."""

    # (rows, columns). Both, spelled out, because the single number this replaced meant columns for
    # five of these tables and rows for the other two, and nothing had ever compared it to the file.
    TABLES = {
        "image-recipes.csv": (39, 13),
        "palettes.csv": (20, 15),
        "layout-dials.csv": (17, 11),
        "slop-tells.csv": (33, 9),
        "copy-formulas.csv": (22, 9),
        "translation-tells.csv": (42, 10),
        "reference-axes.csv": (11, 9),
        "frame-ratios.csv": (13, 12),
        "composition-grids.csv": (7, 10),
        "kpi-metrics.csv": (27, 14),
        "kpi-aspect-weights.csv": (16, 9),
        "makeup-looks.csv": (47, 22),
        "makeup-diagnostics.csv": (15, 15),
        "mark-scale-ladder.csv": (7, 10),
        "market-data-sources.csv": (38, 12),
        "marketing-benchmarks.csv": (35, 12),
        "reference-observations.csv": (10, 24),
        "person-parameters.csv": (35, 13),
        "command-artifacts.csv": (28, 11),
        "colour-gates.csv": (9, 9),
        "vn-marketer-roles.csv": (13, 11),
        "product-compositions.csv": (18, 18),
        "address-registers.csv": (25, 15),
        "prompt-grammar.csv": (69, 9),
        "reference-set-calibration.csv": (11, 10),
        "evidence-sources.csv": (20, 12),
        "seo-intents.csv": (10, 12),
        "tracking-events.csv": (15, 12),
        "attribution-windows.csv": (9, 12),
        "affiliate-mechanics.csv": (38, 11),
        "vn-advertising-law.csv": (45, 13),
        "claim-evidence.csv": (41, 16),
    }

    # Most of these tables are keyed by their first column. The weights table is keyed by two, and
    # this dict exists rather than a reshuffled header because the natural reading order of that file
    # is block-then-aspect and a uniqueness test should not dictate column order.
    UNIQUE_KEYS = {
        "kpi-aspect-weights.csv": ("block", "aspect"),
    }

    @staticmethod
    def rows(name: str) -> list[dict[str, str]]:
        text = (SKILL_ROOT / "data" / name).read_text(encoding="utf-8")
        return list(csv.DictReader(io.StringIO(text)))

    # Two columns of command-artifacts.csv are allowed to be empty, because emptiness is the
    # answer rather than a gap. Most commands have no optional second input, and only one
    # produces an artefact that stands in for another. Filling those cells with "none" would
    # make the planner test for a magic word instead of for an empty string.
    # Two columns of command-artifacts.csv are allowed to be empty for the reason above. The
    # `commands` column of the roles table is allowed to be empty for a stronger reason: two of the
    # thirteen roles - answering the inbox, and covering sales - genuinely map to no command, because
    # they produce no artefact. That emptiness is the central finding of the unit, so writing "none"
    # into the cell to satisfy a completeness test would delete the finding to please the test.
    MAY_BE_EMPTY = {"command-artifacts.csv": {"also_uses", "also_satisfies"},
                    "vn-marketer-roles.csv": {"commands"}}

    def test_every_cell_is_filled(self) -> None:
        # An empty cell in a lookup table is not a blank, it is a silent omission: the composer
        # writes the key with an empty value and the prompt asks the image model for "lighting: ".
        for name in self.TABLES:
            optional = self.MAY_BE_EMPTY.get(name, set())
            for row in self.rows(name):
                for field, value in row.items():
                    if field in optional:
                        continue
                    self.assertTrue(
                        value and value.strip(),
                        f"{name}: row {list(row.values())[0]!r} has an empty {field}",
                    )

    def test_table_shapes_match_what_this_test_declares(self) -> None:
        # The numbers above were decoration until this existed: nothing read them, so a column
        # quietly added or dropped changed the tables without changing a single test. A count is
        # only a check if something compares it. Running it the first time proved the point — two
        # of the seven numbers were row counts sitting in a dict everyone read as columns.
        for name, (rows, columns) in self.TABLES.items():
            found = self.rows(name)
            self.assertEqual(len(found), rows, f"{name} no longer has {rows} rows")
            self.assertEqual(len(found[0]), columns, f"{name} no longer has {columns} columns")

    def test_ids_are_unique(self) -> None:
        for name in self.TABLES:
            rows = self.rows(name)
            keys = self.UNIQUE_KEYS.get(name) or (list(rows[0])[0],)
            ids = [tuple(row[key] for key in keys) for row in rows]
            self.assertEqual(len(ids), len(set(ids)),
                             f"{name} has a duplicate {'+'.join(keys)}")

    def test_palette_body_contrast_passes_and_is_computed(self) -> None:
        def luminance(hex_colour: str) -> float:
            channels = [int(hex_colour[index:index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        def ratio(one: str, two: str) -> float:
            first, second = luminance(one), luminance(two)
            high, low = max(first, second), min(first, second)
            return (high + 0.05) / (low + 0.05)

        for row in self.rows("palettes.csv"):
            measured = ratio(row["bg"], row["ink"])
            self.assertGreaterEqual(
                measured, 4.5,
                f'{row["id"]}: ink {row["ink"]} on {row["bg"]} is {measured:.2f}:1, under 4.5',
            )
            self.assertAlmostEqual(
                measured, float(row["ratio_ink_on_bg"]), places=1,
                msg=f'{row["id"]}: the table says {row["ratio_ink_on_bg"]} but the colours '
                    f"measure {measured:.2f}. The number was typed, not computed.",
            )
            # An accent under 3:1 may still be a fill, but the table has to say so rather than
            # let a reader set a hairline in it.
            accent = ratio(row["bg"], row["accent"])
            if accent < 3.0:
                self.assertIn("fill only", row["accent_use"],
                              f'{row["id"]}: accent is {accent:.2f}:1 but is not marked fill only')

    def test_slop_tells_point_at_recipes_that_exist(self) -> None:
        known = {row["id"] for row in self.rows("image-recipes.csv")}
        for row in self.rows("slop-tells.csv"):
            if row["applies_to"] == "any":
                continue
            for recipe_id in row["applies_to"].split():
                self.assertIn(recipe_id, known,
                              f'slop tell {row["id"]} scopes itself to unknown recipe {recipe_id}')

    def test_dial_defaults_sit_inside_their_own_range(self) -> None:
        for row in self.rows("layout-dials.csv"):
            low, high = float(row["min"]), float(row["max"])
            self.assertLess(low, high, f'{row["dial"]}: min is not below max')
            for theme in ("quiet_editorial", "modern_street", "heritage_craft"):
                value = float(row[theme])
                self.assertTrue(
                    low <= value <= high,
                    f'{row["dial"]}: {theme} default {value} is outside {low}–{high}',
                )

    def test_every_table_on_disk_is_declared_above(self) -> None:
        # TABLES is an allow-list, so a table not named in it silently skips the three checks above:
        # filled cells, declared shape, unique ids. That is an escape hatch nobody would notice,
        # and it was already open — the two tables added on 2026-07-30 were on disk, reachable from
        # the router, and untested, because adding a file does not add a dict entry.
        self.assertEqual(
            set(self.TABLES),
            {path.name for path in (SKILL_ROOT / "data").glob("*.csv")},
            "a data table is on disk but not declared in TABLES, so it is untested",
        )

    def test_the_stroke_floor_is_the_pixel_arithmetic_and_not_a_taste_judgement(self) -> None:
        # The whole claim of the ladder is that these percentages are derived, not chosen. So they
        # have to be recomputable from the slot size alone. Two tiers, because a slot you render at
        # native size has a one-pixel floor and a slot the platform resamples has a two-pixel one;
        # identity-design.md states both. Running this the first time is what surfaced the split —
        # the prose said 1/px while four of the seven rows had been written at 2/px.
        for row in self.rows("mark-scale-ladder.csv"):
            slot = int(row["px"])
            floor = 1 if slot <= 48 else 2
            stroke = float(row["min_stroke_pct_of_mark_height"])
            self.assertAlmostEqual(
                stroke, 100 * floor / slot, places=1,
                msg=f'{row["slot"]}: stroke floor {stroke}% is not {floor}px at {slot}px '
                    f"({100 * floor / slot:.2f}%). The number was chosen, not derived.",
            )
            # A counter is a hole, and a hole closes under antialiasing at the width that would
            # still render as a line. Twice the stroke is the cheapest rule that survives that.
            self.assertAlmostEqual(
                float(row["min_counter_pct_of_mark_height"]), 2 * stroke, places=1,
                msg=f'{row["slot"]}: counter floor is not twice the stroke floor',
            )
            self.assertEqual(int(row["total_pixels"]), slot * slot,
                             f'{row["slot"]}: total_pixels disagrees with {slot}x{slot}')

    def test_the_maskable_safe_circle_is_the_specified_forty_percent_radius(self) -> None:
        # The maskable-icon specification puts the safe zone at a radius of 40% of the icon width,
        # which is a diameter of 80%. Stating it as a diameter in pixels is what a designer can
        # actually draw, but it stops being a specification the moment the arithmetic drifts.
        for row in self.rows("mark-scale-ladder.csv"):
            if row["safe_circle_px"] == "-":
                # Two slots honestly have no circle: a favicon is rendered at native size and is
                # not masked at all, and iOS applies a rounded rectangle, not a circle. Quoting a
                # circular safe zone at the iOS slot would be invented rigour — but the row still
                # has to say the mask exists, or a designer pre-rounds the corners and the OS
                # rounds them twice.
                self.assertTrue(
                    int(row["px"]) <= 48 or "mask" in row["where_it_appears"].lower(),
                    f'{row["slot"]} declares no safe circle and does not say why',
                )
                continue
            self.assertAlmostEqual(
                float(row["safe_circle_px"]), 0.8 * int(row["px"]), places=1,
                msg=f'{row["slot"]}: safe circle is not 80% of {row["px"]}px',
            )

    def test_every_source_records_its_blind_spot_and_a_status_that_matches_its_tier(self) -> None:
        # A source list without blind spots is a list of things to over-trust. And the access tier
        # is the actionable half: 403 means alive but blocking automation, which a human can open,
        # while 000 means the host is gone and the citation has to be replaced. Collapsing the two
        # into "broken" is what leaves a dead 'gso.gov.vn' in a deck for years.
        expected = {"open": "200", "rate-limited": "429", "browser-required": "403",
                    "intermittent": "503", "dead": "000"}
        for row in self.rows("market-data-sources.csv"):
            self.assertIn(row["access"], expected, f'{row["source_id"]}: unknown access tier')
            self.assertEqual(
                row["http_2026_07_30"], expected[row["access"]],
                f'{row["source_id"]}: access {row["access"]} does not match its recorded status',
            )
            self.assertTrue(row["url"].startswith("http"),
                            f'{row["source_id"]}: url is not resolvable as written')
            # A dead host cannot see anything, and "Everything" is the complete answer rather than a
            # short one. What a dead row still owes the reader is the replacement, which lives in
            # do_not_use_for, so that column is held to the same bar as every other row's.
            fields = ("do_not_use_for",) if row["access"] == "dead" \
                else ("what_it_cannot_see", "do_not_use_for")
            for field in fields:
                self.assertGreater(
                    len(row[field]), 20,
                    f'{row["source_id"]}.{field} is too short to be a real limitation',
                )

    def test_every_benchmark_carries_a_reachable_source_and_names_its_limit(self) -> None:
        """A benchmark without its sample and its limit is how 60:40 became a law. So the table is
        held to: a real URL, a fetch status that says how the source was actually reached, and a
        what_it_does_not_establish column long enough to contain an actual thought."""
        grades = {"regulatory-filing", "survey-self-report", "meta-analysis", "modelled-estimate",
                  "vendor-list-price", "company-self-description", "platform-self-report",
                  "author-heuristic", "peer-reviewed-abstract", "unverified-claim"}
        statuses = {"fetched", "abstract-only", "wayback-only", "paywalled", "blocked",
                    "no-source-found"}
        for row in self.rows("marketing-benchmarks.csv"):
            with self.subTest(row["benchmark_id"]):
                self.assertIn(row["evidence_grade"], grades)
                self.assertIn(row["fetch_status"], statuses)
                self.assertTrue(row["url"].startswith("http"), row["url"])
                for field in ("what_it_does_not_establish", "how_to_use_it"):
                    self.assertGreater(len(row[field]), 40, f'{row["benchmark_id"]}.{field} is a stub')

    def test_a_survey_benchmark_states_the_sample_it_came_from(self) -> None:
        # 9.0% of revenue is a fact about 308 US marketing leaders, and it is quoted at shop owners
        # precisely because the sample gets dropped on the way to the slide.
        for row in self.rows("marketing-benchmarks.csv"):
            if row["evidence_grade"] not in {"survey-self-report", "meta-analysis"}:
                continue
            with self.subTest(row["benchmark_id"]):
                self.assertRegex(row["sample"], r"\d",
                                 f'{row["benchmark_id"]} is survey or meta evidence with no sample size')

    def test_the_unverified_claim_is_not_dressed_up_as_a_number(self) -> None:
        # The 60:40 split was never opened: it is on no free IPA page and the reports are paid. It
        # stays in the table because the useful artefact is the citation everyone repeats blind, but
        # it must not carry a figure that a reader could lift into a plan.
        unverified = [row for row in self.rows("marketing-benchmarks.csv")
                      if row["evidence_grade"] == "unverified-claim"]
        self.assertTrue(unverified, "the unverified row was deleted rather than kept honest")
        for row in unverified:
            with self.subTest(row["benchmark_id"]):
                self.assertNotRegex(row["figure"], r"\d", f'{row["benchmark_id"]} states a figure')
                self.assertIn(row["fetch_status"],
                              {"paywalled", "blocked", "no-source-found"})

    def test_a_search_that_found_nothing_is_not_filed_as_a_paywall(self) -> None:
        """`paywalled` means a document exists and costs money. `no-source-found` means the search
        ran and there is no document. Collapsing the second into the first is how the 80-percent
        colour-recognition claim borrows the credibility of a real paid report, so a row claiming to
        have searched has to hand over the query it ran, and must not name a source it cannot have."""
        searched = [row for row in self.rows("marketing-benchmarks.csv")
                    if row["fetch_status"] == "no-source-found"]
        self.assertTrue(searched, "the verified negative was deleted rather than recorded")
        for row in searched:
            with self.subTest(row["benchmark_id"]):
                self.assertEqual(row["evidence_grade"], "unverified-claim")
                self.assertIn("?", row["url"],
                              f'{row["benchmark_id"]}.url is not a re-runnable search')
                self.assertIn("query", row["url"],
                              f'{row["benchmark_id"]}.url does not carry the query terms')
                self.assertRegex(row["source_name"], r"^no ",
                                 f'{row["benchmark_id"]} names a source the search did not find')
                self.assertRegex(row["what_it_does_not_establish"], r"search",
                                 f'{row["benchmark_id"]} does not say what was searched')

    def test_no_person_parameter_is_described_with_an_adjective(self) -> None:
        # This is the whole reason the table exists, so it is the invariant worth enforcing. The
        # registry it replaced described a face as "warm, polished, inviting" and a build as
        # "slender-light-frame"; check_specificity.py fails that vocabulary at 0 checkable things and
        # 100 percent brand-swap. Without a test, the table drifts straight back to adjectives, because
        # an adjective is quicker to write than a measurement.
        banned = re.compile(r"(?i)\b(soft|slender|elegant|beautiful|pretty|attractive|luxurious|"
                            r"premium|natural-looking|romantic|cool|warm-toned|feminine|delicate)\b")
        groups, locks, grades = set(), set(), set()
        for row in self.rows("person-parameters.csv"):
            pid = row["param_id"]
            groups.add(row["group"])
            locks.add(row["lock_class"])
            grades.add(row["term_grade"])
            self.assertNotRegex(row["neutral_value"], banned,
                                f"{pid}: neutral value is an adjective, not a measurement")
            self.assertNotRegex(row["input_domain"], banned,
                                f"{pid}: input domain is an adjective, not a measurement")
            # A neutral value is a number, or a name the unit column itself enumerates, or the
            # explicit refusal to pick one. It is never a mood. Requiring the name to appear in its
            # own unit column is what stops a fifth pose curve being invented in the value column
            # while the closed set says there are four.
            value = row["neutral_value"].strip()
            named = re.search(rf"\b{re.escape(value)}\b", row["unit"])
            self.assertTrue(re.search(r"\d", value) or named or value == "none until chosen",
                            f"{pid}: neutral value {value!r} is neither a number nor one of the "
                            f"names its unit column lists ({row['unit']!r})")
            self.assertTrue(row["unit"].strip(), f"{pid}: a measurement with no unit is a number")
            # Every axis has to say what it controls and how it fails, because an axis nobody can
            # connect to an outcome is one they will leave at its default forever.
            self.assertGreater(len(row["what_it_controls"]), 40, f"{pid}: what_it_controls is a stub")
            self.assertGreater(len(row["failure_when_wrong"]), 40,
                               f"{pid}: failure_when_wrong is a stub")
            self.assertGreater(len(row["prompt_phrasing"]), 10, f"{pid}: no prompt phrasing")
            self.assertTrue(row["source"].strip(), f"{pid}: no source column")
            # house-axis is this skill's own construction and is allowed. What is not allowed is
            # claiming a standard term while pointing at nothing.
            if row["term_grade"] != "house-axis":
                self.assertGreater(len(row["source"]), 30,
                                   f"{pid}: claims a standard term without saying where to verify it")
                # "verify this with a source" is not a source. Every one of these cells used to say
                # something like that, and the research pass replaced them with URLs or with an
                # admission. A URL or an author-and-year is the only thing a reader can act on.
                self.assertTrue("http" in row["source"] or re.search(r"\b(19|20)\d\d\b", row["source"]),
                                f"{pid}: source names no URL and no year, so nothing can be checked")
                self.assertNotRegex(row["source"], r"(?i)\b(verify|find and cite|to be sourced|TODO)\b",
                                    f"{pid}: source is an instruction to source it later")
            # The reverse direction, which is the one that decays quietly: when a search comes back
            # empty the grade has to drop to house-axis. Leaving it at standard-anatomical-term with
            # "no source found" in the cell is how an unsourced claim keeps borrowing authority.
            if re.search(r"(?i)\bno (primary )?source found\b", row["source"]):
                self.assertEqual(row["term_grade"], "house-axis",
                                 f"{pid}: source records that nothing was found, so the term cannot "
                                 f"be graded {row['term_grade']}")
        self.assertEqual(locks, {"locked", "styling"})
        self.assertEqual(groups, {"face", "build", "pose", "camera"})
        self.assertLessEqual(grades, {"standard-anatomical-term", "art-instruction-term",
                                      "photographic-standard", "house-axis"})

    def test_every_observation_cites_one_post_and_grades_itself(self) -> None:
        # source-map.md's own rule is that a profile is a discovery index and a claim needs a post.
        # This table is what fills that gap, so a row citing only an account is a profile-level guess
        # wearing an observation's clothes. The one honest exception is a comparison ACROSS posts on
        # one account, which cannot cite a single URL and has to be graded as the anecdote it is.
        grades = {"single-post-observation", "two-post-anecdote", "craft-heuristic",
                  "four-post-comparison-confounded"}
        across_posts = {"two-post-anecdote", "four-post-comparison-confounded"}
        for row in self.rows("reference-observations.csv"):
            self.assertIn(row["evidence_grade"], grades,
                          f'{row["obs_id"]}: unknown evidence grade')
            if row["evidence_grade"] in across_posts:
                self.assertIn("instagram.com/", row["post_url"])
            else:
                self.assertIn("/p/", row["post_url"],
                              f'{row["obs_id"]} cites an account, not a post')
            # A comparison grade that says "confounded" has to name the variable that was not held
            # still. Otherwise the grade is a disclaimer, and a disclaimer with no named confound
            # reads as caution while licensing the comparison anyway.
            if row["evidence_grade"].endswith("-confounded"):
                self.assertRegex(row["what_this_cannot_tell_you"],
                                 r"(?i)(not constant|not held|confound)",
                                 f'{row["obs_id"]}: graded confounded without naming the confound')
            # The blind spot is the column that keeps a rule from being applied where it does not
            # hold, so it cannot be a shrug. "Nothing" is not a limitation of a photograph.
            self.assertGreater(len(row["what_this_cannot_tell_you"]), 25,
                               f'{row["obs_id"]}: blind spot is too short to be one')
            self.assertGreater(len(row["do_not_copy"]), 25,
                               f'{row["obs_id"]}: does not say what is off limits')

    def test_reading_a_reference_never_stores_the_reference(self) -> None:
        """The whole stance of reference-reading.md is that a measurement is recordable and the
        photograph is not. Seventeen files were deleted from docs/ for getting this wrong, so the
        table is held to citations only: URLs in a CSV, no image anywhere under data/."""
        stored = [path.name for path in (SKILL_ROOT / "data").iterdir()
                  if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}]
        self.assertEqual(stored, [], f"an image was stored alongside the observations: {stored}")

    def test_copy_examples_carry_no_printable_number(self) -> None:
        # Every figure in an example must be a bracketed slot. An example with a real-looking
        # number is a claim somebody will paste into an ad.
        for row in self.rows("copy-formulas.csv"):
            for field in ("example_vi", "example_en"):
                stripped = re.sub(r"\[[^\]]*\]", "", row[field])
                # A shot timecode is structure, not a claim: "8-12:" tells the editor where the
                # cut goes and there is nothing in it a reader could paste into an ad.
                stripped = re.sub(r"\b\d+-\d+:", "", stripped)
                self.assertFalse(
                    re.search(r"\d", stripped),
                    f'{row["id"]}.{field} contains a bare number: {row[field]!r}',
                )

    def test_confused_with_points_at_a_look_that_exists(self) -> None:
        # The discriminator column is the whole point of the looks table, and it is written as a
        # comparison against a named twin. A twin that is not in the table makes the sentence
        # unreadable, which is exactly what happened first time: a doll-eye row compared itself to
        # a cat eye that had not been written yet.
        known = {row["look_id"] for row in self.rows("makeup-looks.csv")}
        for row in self.rows("makeup-looks.csv"):
            self.assertIn(row["confused_with"], known,
                          f'{row["look_id"]} compares itself to unknown look '
                          f'{row["confused_with"]}')
            self.assertNotEqual(row["confused_with"], row["look_id"],
                                f'{row["look_id"]} is confused with itself')

    def test_diagnostic_option_lists_stay_the_same_length(self) -> None:
        # options_vi, options_en and patterns are three parallel lists read by index. A missing
        # entry in one does not break anything visibly: it pairs a Vietnamese label with the wrong
        # match pattern, and the narrowing comes out confidently wrong rather than empty.
        for row in self.rows("makeup-diagnostics.csv"):
            lengths = {field: len(row[field].split("|"))
                       for field in ("options_vi", "options_en", "patterns")}
            self.assertEqual(len(set(lengths.values())), 1,
                             f'{row["q_id"]}: option lists disagree on length {lengths}')

    def test_every_diagnostic_pattern_actually_divides_the_looks(self) -> None:
        # A question earns its place by cutting the field. A pattern matching no look eliminates
        # nothing when chosen; a pattern matching every look eliminates nothing when chosen either.
        # Both are dead weight that reads as diagnosis. The first run of this found one: three rows
        # phrased overlining three different ways, so no substring covered them all.
        looks = self.rows("makeup-looks.csv")
        columns = set(looks[0])
        for row in self.rows("makeup-diagnostics.csv"):
            if row["field"] == "none":
                # Two honest reasons a question names no column: it is asked of the person rather
                # than the photograph, or it is a whole-face triage question — "could any of this
                # appear on an ordinary street face" — that routes between families instead of
                # reading one axis. Neither has anything to match, so the patterns must be the
                # inert sentinel rather than something that looks queryable and is not.
                self.assertEqual(row["patterns"], row["options_en"],
                                 f'{row["q_id"]}: names no column, so its patterns cannot mean '
                                 f'anything, but they differ from its options')
                continue
            self.assertIn(row["field"], columns,
                          f'{row["q_id"]} names column {row["field"]}, which the looks table '
                          f'does not have')
            for pattern in row["patterns"].split("|"):
                hits = sum(1 for look in looks
                           if pattern.lower() in look[row["field"]].lower())
                self.assertGreater(hits, 0, f'{row["q_id"]}: answer {pattern!r} matches no look, '
                                            f'so choosing it eliminates the whole table')
                self.assertLess(hits, len(looks), f'{row["q_id"]}: answer {pattern!r} matches all '
                                                  f'{len(looks)} looks, so it eliminates nothing')

    def test_diagnostics_are_sequenced_without_gaps(self) -> None:
        # The sequence column decides the order questions get asked in, so a duplicate makes the
        # order arbitrary and a gap usually means a row was deleted rather than renumbered.
        found = sorted(int(row["sequence"]) for row in self.rows("makeup-diagnostics.csv"))
        self.assertEqual(found, list(range(1, len(found) + 1)),
                         "makeup-diagnostics.csv sequence has a gap or a duplicate")

    def test_photo_questions_come_before_the_ones_only_a_person_can_answer(self) -> None:
        # Reading the image is free and asking the client costs a round trip, so every question the
        # photograph can settle is asked first. If a blocking question drifts into the middle, the
        # narrowing stalls waiting on a reply it did not need yet.
        kinds = [row["ask_of"] for row in
                 sorted(self.rows("makeup-diagnostics.csv"), key=lambda r: int(r["sequence"]))]
        self.assertEqual(kinds, sorted(kinds, key=lambda kind: kind == "user"),
                         "a question for the person is sequenced before a question for the photo")


class FindRecipeTests(unittest.TestCase):
    """The composer's job is to fill in what a table can know and refuse to fill in what only
    the owner knows. Both halves are asserted here, because the failure mode of the second is a
    brief full of invented product truth that runs without complaint."""

    def test_person_recipes_all_exist(self) -> None:
        known = {row["id"] for row in find_recipe.load("recipes")}
        for recipe_id in find_recipe.PERSON_RECIPES:
            self.assertIn(recipe_id, known, f"PERSON_RECIPES names {recipe_id}, which is not a recipe")

    def test_search_puts_the_job_match_first(self) -> None:
        hits = find_recipe.search("recipes", "giao đồ ăn")
        self.assertTrue(hits, "a Vietnamese job phrase found nothing")
        self.assertEqual(hits[0]["id"], "dish-delivery")

    def test_the_words_a_shop_owner_types_reach_a_row(self) -> None:
        """Phrases, not keywords. Each of these returned nothing while the query was matched as one
        substring: "bún bò" because no row spelled out the dish, "khuyến mãi" because the offer
        formulas only said "offer". A lookup that needs the right vocabulary to find the row that
        supplies the vocabulary is no use to the person this skill is for."""
        for table, query, expected in (
            ("recipes", "bún bò", "bowl-counter"),
            ("recipes", "tô bún quầy", "bowl-counter"),
            ("recipes", "ảnh món ăn cho app", "dish-delivery"),
            ("copy", "khuyến mãi", {"offer-stack", "scarcity-honest"}),
            ("copy", "ưu đãi", "offer-stack"),
            ("copy", "tiêu đề", "one-idea-headline"),
        ):
            hits = find_recipe.search(table, query)
            self.assertTrue(hits, f"{query!r} found nothing in {table}")
            ids = {row["id"] for row in hits}
            wanted = expected if isinstance(expected, set) else {expected}
            self.assertTrue(wanted <= ids, f"{query!r} did not reach {wanted - ids}")

    def test_brief_leaves_owner_fields_as_tbd_and_compiles(self) -> None:
        payload = find_recipe.brief("dish-delivery", "white-crimson")
        for field in payload["brief"]:
            self.assertEqual(payload["brief"][field], "TBD",
                             f"{field} was filled in by a table that cannot know it")
        compiled = compile_provider(payload, "generic")
        self.assertIn("dish", compiled.lower())

    def test_person_brief_uses_the_mode_compile_prompt_recognises(self) -> None:
        # "person" is not a capture mode; compile_prompt.py falls through to the product wording
        # and a portrait brief silently asks for exact materials and true colour.
        payload = find_recipe.brief("founder-portrait", None)
        self.assertEqual(payload["mode"], "human")
        self.assertIn("body language", compile_provider(payload, "generic"))

    def test_checklist_is_scoped_to_the_recipe(self) -> None:
        drink = find_recipe.checklist("drink-cold")
        self.assertNotIn("skin", drink.lower(), "a drink checklist should not carry a skin tell")
        self.assertIn("condensation", drink.lower())
        before = find_recipe.checklist("before-after")
        self.assertIn("better lit", before, "the one tell this recipe exists to prevent is missing")
        self.assertNotIn("better lit", drink)


class RefSheetTests(unittest.TestCase):
    """Each sheet is parsed as XML and checked for the numbers it claims to show, because an SVG
    that is merely well-formed can still be blank."""

    def sheet(self, name: str, **kwargs: str) -> str:
        svg = render_refsheet.SHEETS[name](**kwargs)
        ET.fromstring(svg)  # a malformed sheet is a broken deliverable, not a warning
        return svg

    def test_every_sheet_parses_and_carries_content(self) -> None:
        for name in render_refsheet.SHEETS:
            svg = self.sheet(name)
            self.assertGreater(svg.count("<text"), 10, f"{name} has almost no type on it")

    def test_dial_sheet_prints_the_three_values_from_the_table(self) -> None:
        for row in DataTableTests.rows("layout-dials.csv"):
            svg = render_refsheet.sheet_dials(row["dial"])
            for value in (row["min"], row["quiet_editorial"], row["max"]):
                printed = f"{float(value):g}"
                self.assertIn(printed, svg,
                              f'{row["dial"]}: the sheet does not print {printed}')

    def test_palette_sheet_prints_every_palette_and_its_measured_ratio(self) -> None:
        svg = self.sheet("palettes")
        for row in DataTableTests.rows("palettes.csv"):
            self.assertIn(row["name_en"], svg)
            self.assertIn(f'{row["ratio_ink_on_bg"]}:1', svg)

    def test_lighting_shadow_falls_away_from_the_key(self) -> None:
        # The diagram would be worthless — and would teach the exact error it warns about — if the
        # shadow were drawn in a fixed direction while the key moved.
        svg = self.sheet("lighting")
        self.assertIn("opacity=\"0.38\"", svg, "no shadow wedge was drawn")
        for _label, _why, lights in render_refsheet.SETUPS:
            self.assertIn(lights[0][2], ("soft", "window", "hard", "strip"),
                          "the first light in a setup must be the key")

    def test_reference_sheet_gives_every_axis_a_verdict_the_legend_explains(self) -> None:
        # The sheet's whole argument is that "can I use this reference" gets a row rather than a
        # feeling. An axis the sheet silently drops, or a verdict no legend glosses, breaks that.
        svg = self.sheet("reference")
        for row in DataTableTests.rows("reference-axes.csv"):
            self.assertIn(row["name_en"], svg, f'{row["axis"]}: missing from the sheet')
            self.assertIn(row["verdict"], render_refsheet.VERDICT_GLOSS,
                          f'{row["axis"]}: verdict {row["verdict"]!r} has no plain-language gloss')
            self.assertIn(row["verdict"], render_refsheet.VERDICT_COLOUR)

    def test_reference_sheet_transforms_at_least_three_axes(self) -> None:
        """references/reference-analysis.md sets the bar: move at least three axes or the result
        can still be traced to one source at a glance. The table has to clear the bar it teaches,
        or the sheet is an illustration of a rule it breaks."""
        rows = DataTableTests.rows("reference-axes.csv")
        moved = [row["axis"] for row in rows if row["verdict"] == "transform"]
        self.assertGreaterEqual(len(moved), 3, f"only {moved} would move; the rule asks for three")

    def test_ratio_geometry_is_derived_from_w_and_h_alone(self) -> None:
        """Recompute every eye position from scratch and compare against `ratio_lines`.

        The formula is the one thing on the ratios sheet nobody can eyeball. It is asserted here
        against an independent construction — actually intersecting the full diagonal with the
        reciprocal diagonal — rather than against itself, because a test that reruns the same
        expression only proves Python is deterministic.
        """
        for row in DataTableTests.rows("frame-ratios.csv"):
            w, h = int(row["w"]), int(row["h"])
            # Full diagonal from (0,0) to (w,h). The reciprocal diagonal leaves (0,h) along the
            # perpendicular to it, so its direction is (h,-w) rotated: slope -w/h through (0,h).
            # Intersect y = (h/w)x with y = h - (w/h)x and solve for x.
            x = h * h * w / (w * w + h * h)
            geometry = find_recipe.ratio_lines(w, h)
            self.assertAlmostEqual(geometry["eye"], x / w, places=9,
                                   msg=f'{row["ratio_id"]}: eye is not the diagonal intersection')
            self.assertAlmostEqual(geometry["decimal"], w / h, places=9)
            self.assertAlmostEqual(
                geometry["eye_gap_px"], abs(min(geometry["eye"], 1 - geometry["eye"]) - 1 / 3) * w,
                places=6, msg=f'{row["ratio_id"]}: the gap is not measured to the nearer thirds line',
            )

    def test_root_two_paper_is_where_the_two_grids_coincide(self) -> None:
        """h squared = 2 w squared puts the eye on exactly 1/3, so on ISO paper thirds and dynamic
        symmetry are the same grid. Both tables now say so in prose, and this is the arithmetic
        they are claiming. It is also the sheet's clearest moment, where the grey line disappears
        under the blue one, so a regression here would silently delete the payoff."""
        # The identity is exact in the reals: h**2 == 2 * w**2 gives eye = 2/3 and near = 1/3. It
        # cannot be tested at full precision through ratio_lines, which takes whole pixels, and
        # sqrt(2) is irrational — so 1000 x 1414 is off by 6.7e-5. Assert the algebra separately
        # from the pixels rather than loosening one test until it covers both.
        w = 1000.0
        self.assertAlmostEqual((2 * w * w) / (w * w + 2 * w * w), 2 / 3, places=12)
        near_pixels = find_recipe.ratio_lines(1000, round(1000 * math.sqrt(2)))["eye_near"]
        self.assertLess(abs(near_pixels - 1 / 3), 1e-4,
                        "rounding 1000·sqrt(2) to a whole pixel should cost well under 0.01%")
        a4 = find_recipe.ratio_lines(1240, 1754)
        self.assertLess(a4["eye_gap_px"], 1.0, "the A4 row should round to 0 px of disagreement")
        for row in DataTableTests.rows("frame-ratios.csv"):
            if row["ratio_id"] == "a4-print":
                self.assertIn("same grid", row["consequence"])

    def test_every_ratio_names_a_grid_the_grid_table_defines(self) -> None:
        # The two tables are only useful joined: a ratio says which grid it wants and the grid table
        # says what the evidence for that grid is. A ratio pointing at a grid_id that does not exist
        # is a dead end the reader only finds by running the lookup and getting nothing.
        grids = {row["grid_id"] for row in DataTableTests.rows("composition-grids.csv")}
        grids.add("phi-as-sizing")  # the sizing use, deliberately not a placement grid
        for row in DataTableTests.rows("frame-ratios.csv"):
            self.assertIn(row["grid"], grids,
                          f'{row["ratio_id"]} wants grid {row["grid"]!r}, which no row defines')

    def test_grids_that_the_evidence_does_not_support_say_so(self) -> None:
        """Every graded row has to carry a grade the vocabulary knows, and the phi rows have to keep
        their retraction. This exists because the honest version of this table is the whole point of
        it: a golden-ratio row that quietly loses its `myth` grade becomes the advice it warns
        against, and reads more authoritative for having a citation next to it."""
        allowed = {"peer-reviewed", "peer-reviewed-contested", "myth", "myth-adjacent",
                   "craft-heuristic", "industry-primary", "third-party-cache", "physics"}
        for name, key in (("composition-grids.csv", "grid_id"), ("frame-ratios.csv", "ratio_id")):
            for row in DataTableTests.rows(name):
                self.assertIn(row["evidence_grade"], allowed,
                              f'{name} {row[key]}: unknown grade {row["evidence_grade"]!r}')
        graded = {row["grid_id"]: row["evidence_grade"]
                  for row in DataTableTests.rows("composition-grids.csv")}
        self.assertEqual(graded["golden-spiral"], "myth")
        self.assertEqual(graded["phi-grid"], "myth-adjacent")

    def test_ratios_sheet_draws_all_three_grids_and_keeps_phi_out_of_the_strip(self) -> None:
        # phi is not a delivery ratio, so drawing it beside 16:9 would teach the error the table
        # spends a paragraph correcting. It gets its own panel instead, and this pins that split.
        svg = self.sheet("ratios")
        for row in DataTableTests.rows("frame-ratios.csv"):
            if row["family"] == "phi":
                self.assertNotIn(f'{row["w"]} x {row["h"]}', svg,
                                 "the phi ratio was drawn as if it were a delivery ratio")
                continue
            self.assertIn(f'{row["w"]} x {row["h"]}', svg, f'{row["ratio_id"]}: missing')
        self.assertIn(render_refsheet.COBALT, svg)
        self.assertIn(render_refsheet.ORANGE, svg)
        self.assertIn("stroke-dasharray", svg, "thirds and phi must be distinguishable from the eye")

    def test_frames_reserve_stays_inside_the_platform_bands(self) -> None:
        for name, _pw, ph, top, bottom, _note, reserve, _why in render_refsheet.PLACEMENTS:
            if reserve is None:
                continue
            self.assertLessEqual(reserve[1] + reserve[3], 1.0 + 1e-9,
                                 f"{name}: the reserve runs past the usable area")
            self.assertLess(top + bottom, ph, f"{name}: the bands cover the whole frame")


class RepoReadmeTests(unittest.TestCase):
    """The README is the only page most people read, so its numbers have to be measured.

    Every count in it was wrong at once: 45 references against 60 on disk, 14 dossiers against 15,
    9 lookup tables against 24, 22 tools against 38, 137 tests against 339, and a table of six
    pipelines in a repository that has nine. Not one of those was a lie when it was written, which
    is the whole problem - a hand-maintained count decays silently and reads as current forever.
    These tests recount from the filesystem, so the next time it drifts the suite says so.
    """

    LANGS = {"en": REPO_ROOT / "README.md", "vi": REPO_ROOT / "README.vi.md"}

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = {lang: path.read_text(encoding="utf-8") for lang, path in cls.LANGS.items()}

    def _count(self, lang: str, pattern: str) -> int:
        found = re.findall(pattern, self.text[lang])
        self.assertTrue(found, f"{lang}: {pattern} no longer appears in the README")
        self.assertEqual(len(set(found)), 1, f"{lang}: {pattern} is stated more than one way: {found}")
        return int(found[0])

    def test_both_language_files_offer_the_switch_at_the_top_and_the_bottom(self) -> None:
        """A reader who scrolls to the end should not have to scroll back to change language."""
        for lang, text in self.text.items():
            with self.subTest(lang=lang):
                for target in ("README.md", "README.vi.md"):
                    self.assertEqual(text.count(f'href="{target}"'), 2, f"{lang} -> {target}")
                # The active language is the bold one, and it is bold in exactly its own file.
                active = "Tiếng Việt" if lang == "vi" else "English"
                self.assertIn(f"<b>{active}</b>", text)
                self.assertNotIn(f"<b>{'English' if lang == 'vi' else 'Tiếng Việt'}</b>", text)

    def test_the_switch_uses_no_remote_image(self) -> None:
        """A badge service is a dependency and an outage away from a broken header."""
        for lang, text in self.text.items():
            head = text.split("\n\n", 3)[0] + text.split("\n\n", 3)[1]
            with self.subTest(lang=lang):
                self.assertNotIn("img.shields.io", head)
                self.assertNotIn("<img", head)
                self.assertIn("<kbd>", head)

    def test_every_registered_pipeline_appears_in_the_pipeline_table(self) -> None:
        """The table listed six of nine, so three whole capabilities were invisible to a customer."""
        registry = load_registry()
        for lang, text in self.text.items():
            for name, pipeline in registry["pipelines"].items():
                with self.subTest(lang=lang, pipeline=name):
                    row = f"| `{name}` | {len(pipeline['deliverables'])} |"
                    self.assertIn(row, text, f"{name} missing from the {lang} table, or its count moved")

    def test_the_stated_pipeline_count_matches_the_registry(self) -> None:
        total = len(load_registry()["pipelines"])
        self.assertIn(f"{_english_number(total).capitalize()} pipelines", self.text["en"])
        self.assertIn(f"{_vietnamese_number(total).capitalize()} pipeline", self.text["vi"])

    def test_the_stated_library_counts_match_the_filesystem(self) -> None:
        measured = {
            "references": len(list((SKILL_ROOT / "references").glob("*.md"))),
            "dossiers": len(list((SKILL_ROOT / "references" / "dossiers").glob("*.md"))),
            "tables": len(list((SKILL_ROOT / "data").glob("*.csv"))),
            # The test file is a harness, not a tool a customer can run.
            "tools": len([p for p in (SKILL_ROOT / "scripts").glob("*.py") if p.stem != "test_tools"]),
            "skill_lines": len((SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").splitlines()),
        }
        patterns = {
            "en": {
                "references": r"(\d+) topic files",
                "dossiers": r"(\d+) deep-craft dossiers",
                "tables": r"(\d+) lookup tables",
                "tools": r"(\d+) tools \+ test suite",
                "skill_lines": r"entry point and router, (\d+) lines",
            },
            "vi": {
                "references": r"(\d+) file chủ đề",
                "dossiers": r"(\d+) dossier craft",
                "tables": r"(\d+) bảng tra",
                "tools": r"(\d+) công cụ \+ bộ test",
                "skill_lines": r"bộ định tuyến, (\d+) dòng",
            },
        }
        for lang, by_key in patterns.items():
            for key, pattern in by_key.items():
                with self.subTest(lang=lang, key=key):
                    self.assertEqual(self._count(lang, pattern), measured[key])

    def test_the_stated_test_count_matches_the_suite(self) -> None:
        """Counted by loading this module, so it cannot be right today and stale next week."""
        suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
        total = suite.countTestCases()
        for lang, pattern in (("en", r"(\d+) tests, including"), ("vi", r"(\d+) test, trong đó")):
            with self.subTest(lang=lang):
                self.assertEqual(self._count(lang, pattern), total)

    def test_every_command_in_a_readme_code_block_names_a_script_that_exists(self) -> None:
        for lang, text in self.text.items():
            for script in set(re.findall(r"marketing-minthep/scripts/([a-z_]+\.py)", text)):
                with self.subTest(lang=lang, script=script):
                    self.assertTrue((SKILL_ROOT / "scripts" / script).exists(), script)

    def test_the_units_a_customer_would_look_for_are_reachable_from_the_readme(self) -> None:
        """A tool nobody can find from the front page is a tool that does not exist.

        Fifteen units were shipped and unmentioned - pricing arithmetic, prompt grammar, KPI
        scoring, sample sizing, the virtual person, workload. This pins the ones a customer
        arrives with a question about.
        """
        required = ("price_offer.py", "check_prompt_grammar.py", "score_kpi.py",
                    "check_test_readout.py", "plan_virtual_person.py", "check_specificity.py",
                    "check_address_register.py", "plan_operating_load.py", "plan_composition_set.py")
        for lang, text in self.text.items():
            for script in required:
                with self.subTest(lang=lang, script=script):
                    self.assertIn(script, text)

    def test_the_two_files_stay_the_same_document(self) -> None:
        """Divergence is how one language quietly becomes the stale one."""
        heads = {lang: len(re.findall(r"^## ", text, re.MULTILINE)) for lang, text in self.text.items()}
        self.assertEqual(heads["en"], heads["vi"])
        blocks = {lang: text.count("```powershell") for lang, text in self.text.items()}
        self.assertEqual(blocks["en"], blocks["vi"])


def _english_number(value: int) -> str:
    names = {6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
    return names.get(value, str(value))


def _vietnamese_number(value: int) -> str:
    names = {6: "sáu", 7: "bảy", 8: "tám", 9: "chín", 10: "mười", 11: "mười một", 12: "mười hai"}
    return names.get(value, str(value))


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
            SKILL_ROOT / "data",
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

    def test_every_reference_image_has_a_licence_line(self) -> None:
        """An image in the demo's reference directory is republished on a public site, so its
        rights have to be resolved before it lands there — not after somebody notices.

        This test exists because seventeen files failed it. They were photographs of named living
        people saved from Instagram, filed under "copyright remains with the original creators",
        which is a disclaimer rather than a permission. The skill's own creative-evaluation.md
        rejects any asset whose source rights are unresolved, so the demo page was arguing against
        the skill it demonstrates. Convenience is the only way an image gets into a directory like
        this one, and convenience is exactly what a test can refuse.
        """
        directory = REPO_ROOT / "docs" / "assets" / "references"
        attribution = directory / "ATTRIBUTION.txt"
        text = attribution.read_text(encoding="utf-8")
        # Entries are blank-line-separated blocks, so the filename and the licence have to sit in
        # the same block. Checking the whole file for both strings separately would pass a file
        # listed under one entry and licensed under another.
        blocks = [block for block in text.split("\n\n") if "License:" in block]
        for image in sorted(directory.glob("*")):
            if image.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                continue
            owning = [block for block in blocks if image.name in block]
            self.assertEqual(
                len(owning), 1,
                f"{image.name}: {len(owning)} blocks in ATTRIBUTION.txt name it with a License "
                "line. Every image here needs exactly one creator, licence and source URL.",
            )
            for field in ("Creator:", "License:", "Source:", "File:"):
                self.assertIn(field, owning[0], f"{image.name}: its entry has no {field} line")
            self.assertIn("http", owning[0], f"{image.name}: its entry has no source URL")

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

    # Raised from 150 to 200 deliberately, and the reason is recorded rather than left to whoever
    # next hits the ceiling. 150 was chosen when the skill had nine pipelines and seventeen tables.
    # It now has 28 commands, 21 tables and 55 references, and the cost of the old budget stopped
    # being brevity: with no room for a command surface, SKILL.md listed pipelines and left the
    # commands reachable only through a reference nothing pointed at. An entry point that omits the
    # entry is not cheaper, it is broken. The peers on this machine sit either side of 200 -
    # impeccable 168, marketing-council 161, brand-guidelines 183, taste-skill 192, design-system
    # 240, skill-creator 298, marketing-psychology 455 - so 200 is not an outlier, and it is a
    # ceiling rather than a target. Detail still belongs in references/, which load on demand.
    LINE_BUDGET = 200

    def test_skill_md_stays_within_the_progressive_disclosure_budget(self) -> None:
        """SKILL.md is loaded on every activation, so its length is a tax on every request.
        Detail belongs in references/, which load only when a decision needs them."""
        skill = SKILL_ROOT / "SKILL.md"
        lines = skill.read_text(encoding="utf-8").splitlines()
        self.assertLess(len(lines), self.LINE_BUDGET, f"SKILL.md is {len(lines)} lines")
        # A budget nobody is near is not a budget, it is a comment. If the file has drifted far below
        # the ceiling, the ceiling was raised for nothing and should come back down.
        self.assertGreater(len(lines), 150,
                           "SKILL.md no longer needs a 200-line budget. Lower it back to 150")
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


class _TextNodes(HTMLParser):
    """The text nodes docs/app.js would hand to its translator, in the same order.

    app.js walks the DOM with a TreeWalker, rejects SCRIPT/STYLE/CODE/PRE, and keys each node on
    its whitespace-collapsed value. This mirrors that exactly, because the only alternative is a
    browser — and without it the two failures below are invisible: a Vietnamese line with no key
    stays Vietnamese in the English edition, and a key whose sentence was reworded silently stops
    matching anything at all.
    """

    SKIP = {"script", "style", "code", "pre"}
    VOID = {"br", "img", "meta", "link", "input", "hr", "source", "area"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.nodes: list[str] = []

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data: str) -> None:
        if any(tag in self.SKIP for tag in self.stack):
            return
        collapsed = re.sub(r"\s+", " ", data).strip()
        if collapsed:
            self.nodes.append(collapsed)


class HandbookTranslationTests(unittest.TestCase):
    """The bilingual demo page is one of the skill's deliverables, so a half-translated page is a
    shipped defect rather than a cosmetic one. Both assertions here failed when they were written:
    eleven Vietnamese lines had no English at all, and 148 of the 227 keys matched nothing on the
    page because their sentences had been reworded in later rounds."""

    DOCS = Path(__file__).resolve().parents[2] / "docs"

    @classmethod
    def setUpClass(cls) -> None:
        walker = _TextNodes()
        walker.feed((cls.DOCS / "index.html").read_text(encoding="utf-8"))
        cls.nodes = dict.fromkeys(walker.nodes)
        source = (cls.DOCS / "i18n.js").read_text(encoding="utf-8")
        # Comment lines are stripped first so a commented-out example key is not read as a real one.
        body = re.sub(r"^\s*//.*$", "", source, flags=re.M)
        cls.keys = {
            match.replace('\\"', '"')
            for match in re.findall(r'\n\s*"((?:[^"\\]|\\.)*)"\s*:', body)
        }
        cls.app = (cls.DOCS / "app.js").read_text(encoding="utf-8")

    @staticmethod
    def vietnamese(text: str) -> bool:
        # Any Latin letter carrying a diacritic, plus đ, which has no combining name. Detecting the
        # language by keyword would miss exactly the short captions that went untranslated.
        return any("WITH" in unicodedata.name(ch, "") or ch in "đĐ" for ch in text)

    def test_every_vietnamese_line_on_the_page_has_an_english_key(self) -> None:
        untranslated = [
            text for text in self.nodes
            if self.vietnamese(text) and text not in self.keys
            # The use-case panel and the prompt block are rendered from app.js, which carries its
            # own vi/en pair per entry, so their initial HTML values are translated by other means.
            and text not in self.app
        ]
        self.assertEqual(untranslated, [], f"no English for: {untranslated}")

    def test_no_translation_key_is_dead(self) -> None:
        """A key that matches nothing is worse than clutter: it reads as coverage. Every one of
        these is a line that was reworded in the HTML while its translation stayed behind, so the
        page it was written for no longer exists and nobody noticed the English went missing."""
        dead = sorted(key for key in self.keys if key not in self.nodes)
        self.assertEqual(dead, [], f"{len(dead)} keys match no text node: {dead[:5]}")


class UseCaseGridTests(unittest.TestCase):
    """The tab grid is the front door, and for months it had nine creative tabs and no commercial
    ones. A visitor asking "can I afford this discount", "which numbers do I report", "is this test
    big enough" or "does this draft read like a person" found nothing, while price_offer.py,
    score_kpi.py, check_test_readout.py and rewrite_human.py all sat finished in the repository. A
    tool that cannot be found from the front page is a tool that does not exist, which is the same
    defect the README carried until it was recounted.

    Three of the Vietnamese panels were also written in English - photoshoot, video and edit - so a
    Vietnamese reader clicked a Vietnamese tab and got English bullets. That is invisible to anyone
    testing the page in English, which is how it survived."""

    DOCS = REPO_ROOT / "docs"
    DECISIONS = {
        "pricing": "price_offer.py",
        "measure": "score_kpi.py",
        "experiment": "check_test_readout.py",
        "rewrite": "rewrite_human.py",
    }

    @classmethod
    def setUpClass(cls) -> None:
        app = (cls.DOCS / "app.js").read_text(encoding="utf-8")
        start = app.index("const useCases = {")
        depth = 0
        end = len(app)
        for index in range(app.index("{", start), len(app)):
            if app[index] == "{":
                depth += 1
            elif app[index] == "}":
                depth -= 1
                if depth == 0:
                    end = index
                    break
        block = app[start:end]
        cls.entries = {}
        for match in re.finditer(r"^  (\w+): \{$(.*?)^  \},$", block, re.M | re.S):
            slug, body = match.group(1), match.group(2)
            cls.entries[slug] = {}
            for lang in ("vi", "en"):
                found = re.search(rf"^    {lang}: \{{(.*)\}},$", body, re.M)
                if not found:
                    continue
                fields = found.group(1)
                entry = {
                    name: (re.search(rf"{name}: '((?:[^'\\]|\\.)*)'", fields) or [None, ""])[1]
                    for name in ("title", "description", "request")
                }
                listed = re.search(r"deliverables: \[(.*?)\]", fields)
                entry["deliverables"] = re.findall(r"'((?:[^'\\]|\\.)*)'", listed.group(1)) if listed else []
                cls.entries[slug][lang] = entry
        html = (cls.DOCS / "index.html").read_text(encoding="utf-8")
        cls.tabs = re.findall(r'data-use-case="(\w+)"', html)

    def test_every_tab_has_a_panel_and_every_panel_has_a_tab(self) -> None:
        """Either half alone is a silent failure: a tab with no entry throws on click, and an entry
        with no tab is content nobody can reach. Order matters too - the tabs are arrow-key
        navigable, so the reading order is the keyboard order."""
        self.assertEqual(self.tabs, list(self.entries), "the tab list and the panel list disagree")

    def test_the_hero_counts_the_tabs_it_is_counting(self) -> None:
        """The hero said nine workbenches because there were nine tabs when it was typed. It is the
        first number a visitor reads and the page shows the tabs a scroll below it, so it cannot be
        the one figure here that is maintained by hand."""
        html = (self.DOCS / "index.html").read_text(encoding="utf-8")
        stated = re.search(r"<strong>(\d+)</strong><span>marketing workbenches</span>", html)
        self.assertIsNotNone(stated, "the hero no longer states a workbench count in the expected shape")
        self.assertEqual(int(stated.group(1)), len(self.tabs))

    def test_the_grid_carries_the_four_decision_questions(self) -> None:
        missing = sorted(slug for slug in self.DECISIONS if slug not in self.entries)
        self.assertEqual(missing, [], f"decision tabs dropped from the grid: {missing}")

    def test_every_panel_is_complete_in_both_languages(self) -> None:
        for slug, langs in self.entries.items():
            self.assertEqual(sorted(langs), ["en", "vi"], f"{slug} is not bilingual")
            for lang, entry in langs.items():
                for field in ("title", "description", "request"):
                    self.assertTrue(entry[field].strip(), f"{slug}.{lang}.{field} is empty")
                # Four bullets is the shape the panel's CSS grid was built around, and a fifth would
                # overflow the card rather than wrap.
                self.assertEqual(len(entry["deliverables"]), 4, f"{slug}.{lang} has {len(entry['deliverables'])} bullets")

    def test_no_vietnamese_panel_is_written_in_english(self) -> None:
        for slug, langs in self.entries.items():
            vi, en = langs["vi"], langs["en"]
            self.assertTrue(
                any(HandbookTranslationTests.vietnamese(item) for item in vi["deliverables"]),
                f"{slug}.vi has no Vietnamese in its bullets - it is the English list",
            )
            # One shared bullet is plausible when the phrase is jargon a Vietnamese marketer says in
            # English anyway. Two is a list that was copied and never translated.
            shared = [item for item in vi["deliverables"] if item in en["deliverables"]]
            self.assertLessEqual(len(shared), 1, f"{slug} shares {len(shared)} untranslated bullets: {shared}")

    def test_every_script_a_panel_names_exists(self) -> None:
        """The request strings are meant to be copied and sent, so a script named in one is a
        promise the repository has to keep. A renamed tool would otherwise fail in the customer's
        session, which is the worst place to find out."""
        named = set()
        for langs in self.entries.values():
            for entry in langs.values():
                named |= set(re.findall(r"scripts/([a-z_]+\.py)", entry["request"]))
        self.assertTrue(named, "no panel names a script")
        for script in sorted(named):
            self.assertTrue((SKILL_ROOT / "scripts" / script).exists(), f"{script} is named on the page but absent")

    def test_each_decision_panel_names_the_tool_that_settles_it(self) -> None:
        for slug, script in self.DECISIONS.items():
            for lang in ("vi", "en"):
                request = self.entries[slug][lang]["request"]
                self.assertIn(script, request, f"{slug}.{lang} does not name {script}")

    def test_the_virtual_panel_no_longer_promises_a_choice_of_adjectives(self) -> None:
        """It used to open on "impression options before facial design", which stopped being true
        when the adjectives became a parameter table. A person described as warm and elegant renders
        as a different face every time, so the panel promised the one thing the unit cannot do."""
        virtual = self.entries["virtual"]
        self.assertNotIn("Impression options", virtual["en"]["deliverables"])
        self.assertIn("person_id", virtual["vi"]["request"])
        self.assertIn("person_id", virtual["en"]["request"])


class RewriteHumanTests(unittest.TestCase):
    """The cadence gates are statistical, which means a human reviewer cannot check them by
    reading and a wrong measurement would go unnoticed for as long as the copy kept passing.
    These tests are the only thing standing between a plausible number and a wrong one."""

    def test_self_check_passes(self) -> None:
        # rewrite_human.self_check() carries the assertions that belong next to the measurement
        # code. Calling it here means one failing measurement fails the whole suite.
        self.assertEqual(rewrite_human.self_check().strip(), "self-check passed")

    def test_uniform_prose_fails_the_burstiness_gate(self) -> None:
        flat = " ".join(["The broth is simmered from bone each morning here."] * 6)
        gates = {row["gate"]: row for row in rewrite_human.gates(rewrite_human.measure(flat, "en"))}
        self.assertFalse(gates["burstiness-cv"]["pass"])
        self.assertEqual(gates["burstiness-cv"]["severity"], "critical")

    def test_every_tell_regex_compiles_and_declares_a_scope(self) -> None:
        # A broken regex would silently stop detecting its tell, and the report would say the
        # draft was clean. A missing scope would make a heading tell look for headings in text
        # that has had its headings stripped.
        for row in DataTableTests.rows("translation-tells.csv"):
            with self.subTest(row["id"]):
                re.compile(row["detect_regex"])
                self.assertIn(row["scope"], ("prose", "raw"))
                self.assertIn(row["language"], ("vi", "en", "any"))
                self.assertIn(row["severity"], ("critical", "high", "medium", "low"))

    def test_no_tell_fires_on_clean_copy_in_either_language(self) -> None:
        """A detector that flags good copy gets ignored, and an ignored gate is worse than none.
        Both samples below are written to the skill's own targets."""
        clean = {
            "vi": ("Trưa nay bạn có bốn mươi phút. Nồi nước dùng nấu từ xương từ bốn giờ sáng. "
                   "Chín năm, cùng một nồi, cùng một góc phố. Ghé trước 11h30 thì khỏi chờ."),
            "en": ("Lunch is forty minutes long. The broth is simmered from bone from four in the "
                   "morning, not made to order one bowl at a time, which is the only reason it holds. "
                   "Nine years at the same corner. Come before eleven thirty and you will not wait."),
        }
        for language, text in clean.items():
            with self.subTest(language):
                blocking = [row for row in rewrite_human.find_tells(text, language)
                            if row.get("severity") in ("critical", "high")]
                self.assertEqual(blocking, [], f"{language}: clean copy tripped {blocking}")

    def test_machine_translated_vietnamese_is_caught(self) -> None:
        draft = ("Trong thế giới ngày nay, việc tìm một quán uy tín là không dễ. Chúng tôi tự hào "
                 "là đơn vị chuyên nghiệp và tận tâm nhất. Món này được nấu bởi đầu bếp trưởng. "
                 "Điều này có nghĩa là bạn sẽ hài lòng. Hơn nữa, giá cả hợp lý.")
        hits = {row["id"] for row in rewrite_human.find_tells(draft, "vi")}
        for expected in ("trong-the-gioi-ngay-nay", "su-viec-nominal", "uy-tin-chuyen-nghiep",
                         "tu-hao", "duoc-boi-passive", "dieu-nay-co-nghia", "hon-nua-stack"):
            self.assertIn(expected, hits)

    def test_language_is_detected_without_a_hint(self) -> None:
        self.assertEqual(rewrite_human.detect_language("Nồi nước dùng nấu từ xương."), "vi")
        self.assertEqual(rewrite_human.detect_language("The broth is simmered from bone."), "en")

    def test_the_pipeline_is_registered_with_its_reference_and_script(self) -> None:
        pipeline = load_registry()["pipelines"]["rewrite-human"]
        self.assertIn("rewrite-human.md", pipeline["references"])
        self.assertIn("rewrite_human.py", pipeline["scripts"])
        self.assertTrue((SKILL_ROOT / "references" / "rewrite-human.md").exists())

    def test_rewrite_requests_route_to_the_rewrite_pipeline(self) -> None:
        registry = load_registry()
        for request in ("viết lại đoạn này cho tự nhiên, đang bị dịch máy",
                        "rewrite this landing page so it does not sound like AI",
                        "bản dịch tiếng Anh nghe như dịch từng chữ, sửa lại giúp"):
            with self.subTest(request):
                routed = route_pipeline({"request": request}, registry)["pipeline"]
                self.assertEqual(routed, "rewrite-human")

    def test_adding_the_route_did_not_steal_other_requests(self) -> None:
        """The trigger list contains "viết" and "dịch", which appear in plenty of requests that
        are not rewrites. This is the regression that would make the new route a net loss."""
        registry = load_registry()
        unchanged = {
            "lên kế hoạch marketing cho quán bún bò": "plan-from-zero",
            "thiết kế menu quán cà phê": "design-render",
            "nghiên cứu thị trường trà sữa": "deep-research",
            "chụp ảnh sản phẩm từ hình này": "image-from-reference",
            "viết kịch bản video TikTok cho sản phẩm": "video-campaign",
        }
        for request, expected in unchanged.items():
            with self.subTest(request):
                self.assertEqual(route_pipeline({"request": request}, registry)["pipeline"], expected)

    def test_the_worked_example_still_demonstrates_what_its_readme_claims(self) -> None:
        """The example is the only place a reader sees the whole loop, so a threshold change that
        made the bad draft pass, or the rewrite fail, would quietly turn it into a lesson in
        nothing. The README quotes these verdicts."""
        folder = SKILL_ROOT / "assets" / "examples" / "rewrite-human"

        def blocking(name: str, language: str) -> int:
            text = (folder / name).read_text(encoding="utf-8")
            return rewrite_human.blocking_count(
                rewrite_human.gates(rewrite_human.measure(text, language)),
                rewrite_human.find_tells(text, language))

        self.assertGreater(blocking("01-draft-vi.md", "vi"), 0, "the bad draft stopped failing")
        self.assertEqual(blocking("02-rewrite-vi.md", "vi"), 0, "the shipped rewrite stopped passing")
        self.assertEqual(blocking("03-transcreation-en.md", "en"), 0, "the shipped English stopped passing")

    # --- decoration ------------------------------------------------------------------------------

    BULLETED = ("## ✨ Ưu điểm\n"
                "- \U0001f680 Giao trong ngày\n"
                "- \U0001f680 Rang tại xưởng\n"
                "- \U0001f680 Đổi trả 7 ngày\n")

    def test_an_icon_bulleted_list_is_measured_even_though_it_has_no_cadence(self) -> None:
        """The draft this gate exists for has fewer than two sentences, which is the branch that
        used to return no gates at all. A checklist with a rocket on every line would have come
        back reported as clean, on the most common bad output there is."""
        stats = rewrite_human.measure(self.BULLETED, "vi")
        self.assertTrue(stats["insufficient"])
        named = {row["gate"] for row in rewrite_human.gates(stats, "deliverable")}
        self.assertEqual(named, {"decoration-as-structure", "decoration-density", "decoration-run"})

    def test_the_default_channel_allows_no_structural_decoration(self) -> None:
        # No argument means `deliverable`, which is what this skill's own artefacts are. The two
        # live callers in this file pass one argument, so the default is what they get.
        gates = {row["gate"]: row for row in
                 rewrite_human.gates(rewrite_human.measure(self.BULLETED, "vi"))}
        self.assertFalse(gates["decoration-as-structure"]["pass"])
        self.assertEqual(gates["decoration-as-structure"]["severity"], "high")

    def test_social_is_different_in_kind_not_in_degree(self) -> None:
        """A Vietnamese seller bulleting a Facebook post with a tick is doing what the surface does.
        A gate that calls that a machine tell is wrong about the channel, and gets switched off."""
        stats = rewrite_human.measure(self.BULLETED, "vi")
        social = {row["gate"]: row for row in rewrite_human.gates(stats, "social")}
        self.assertTrue(social["decoration-as-structure"]["pass"])
        # The run rule still holds, because three identical openers is a generated list anywhere.
        self.assertFalse(social["decoration-run"]["pass"])

    def test_varying_the_icon_per_line_is_a_decision_and_passes_the_run_gate(self) -> None:
        varied = self.BULLETED.replace("- \U0001f680 Rang", "- \U0001f6a9 Rang")
        found = rewrite_human.measure(varied, "vi")["decoration"]
        self.assertEqual(found["longest_icon_opener_run"], 1)

    def test_meaning_bearing_signs_are_never_counted(self) -> None:
        """Every one of these sits in the same Unicode category as the rocket. Flagging the
        registered mark in brand copy is the fastest way to lose the whole gate."""
        for sign in rewrite_human.DECORATION_KEEP:
            with self.subTest(sign):
                self.assertEqual(unicodedata.category(sign), "So")
                self.assertEqual(rewrite_human.pictographs(f"Minh Thép{sign} rang tại xưởng."), [])

    def test_an_emoji_inside_a_sentence_stays_inline(self) -> None:
        # The whole rule: the defect is the slot, not the glyph. One a writer put mid-sentence is a
        # decision; one opening every line is a template.
        mid = ("Chủ quán nhắn lúc bốn giờ sáng \U0001f605 vì nồi nước dùng chưa tới. "
               "Chúng tôi giao lại trong hai tiếng.")
        found = rewrite_human.measure(mid, "vi")["decoration"]
        self.assertEqual((found["structural"], found["inline"]), (0, 1))

    def test_a_heading_emoji_is_structural_wherever_it_sits_in_the_line(self) -> None:
        tail = rewrite_human.measure(
            "## Giao hàng \U0001f69a\n\nGiao trong ngày ở Gò Vấp. Ngoài bán kính tám cây thì hai ngày.",
            "vi")
        self.assertEqual(tail["decoration"]["structural"], 1)

    def test_arrows_and_bullets_are_out_of_scope_on_purpose(self) -> None:
        """`→` is Sm and `•` is Po - ordinary typography with centuries behind it. A gate that
        fires on correctly typeset copy stops being read, so this exclusion is the design."""
        self.assertEqual(rewrite_human.pictographs("Đặt hàng → giao trong ngày • đổi trả 7 ngày"), [])

    def test_the_worked_example_carries_no_decoration(self) -> None:
        # The shipped example is what a reader copies. If it grew an icon list, the unit would be
        # teaching the defect it exists to catch.
        folder = SKILL_ROOT / "assets" / "examples" / "rewrite-human"
        for name in ("02-rewrite-vi.md", "03-transcreation-en.md"):
            with self.subTest(name):
                text = (folder / name).read_text(encoding="utf-8")
                self.assertEqual(rewrite_human.pictographs(text), [])

    # --- list shape ------------------------------------------------------------------------------

    # Four sections, four lists, every list three items long. This is what a generated brief,
    # playbook or landing page looks like, and until `list_blocks()` existed the script read it as
    # a document with no measurable prose and returned nothing but decoration counts.
    THREES = ("## Một\n\nMở đầu ở đây.\n\n- Alpha\n- Beta\n- Gamma\n\n"
              "## Hai\n\nMở đầu thứ hai.\n\n- Delta\n- Epsilon\n- Zeta\n\n"
              "## Ba\n\nMở đầu thứ ba.\n\n- Eta\n- Theta\n- Iota\n\n"
              "## Bốn\n\nMở đầu thứ tư.\n\n- Kappa\n- Lambda\n- Mu\n")

    def test_a_document_of_threes_fails_even_with_no_cadence_to_measure(self) -> None:
        """The reason this gate reads raw text instead of `prose_only()`. Every list line is blanked
        before cadence is measured, so a document that is mostly lists has its worst structural
        habit stripped out before anything looks at it - and lands in the `insufficient` branch,
        where until now only decoration was checked."""
        stats = rewrite_human.measure(self.THREES, "vi")
        self.assertEqual(stats["lists"], {"blocks": 4, "sizes": [3, 3, 3, 3], "threes": 4,
                                         "three_share": 1.0, "longest": 3})
        gates = {row["gate"]: row for row in rewrite_human.gates(stats, "deliverable")}
        self.assertFalse(gates["tricolon-everywhere"]["pass"])
        self.assertEqual(gates["tricolon-everywhere"]["severity"], "high")

    def test_the_gate_is_absent_rather_than_passing_below_the_floor(self) -> None:
        """Two lists of three scores 1.00 and has done nothing wrong. Reporting that as `pass`
        would be a claim the measurement cannot support, and a gate that passes on no evidence
        teaches the reader to trust it where they should not."""
        two = "Mở đầu.\n\n- Alpha\n- Beta\n- Gamma\n\nMở đầu nữa.\n\n- Delta\n- Epsilon\n- Zeta\n"
        self.assertEqual(rewrite_human.list_geometry(two)["three_share"], 1.0)
        named = {row["gate"] for row in rewrite_human.gates(rewrite_human.measure(two, "vi"))}
        self.assertNotIn("tricolon-everywhere", named)
        self.assertLess(rewrite_human.list_geometry(two)["blocks"], rewrite_human.LIST_BLOCKS_MIN)

    def test_varying_the_list_lengths_clears_the_gate(self) -> None:
        # The repair is content, not cosmetics: sections genuinely differ in how many things they
        # hold. Four lists of 3/4/5/2 is the shape that produces.
        varied = (self.THREES.replace("- Beta\n", "- Beta\n- Beta hai\n")
                             .replace("- Zeta\n", "- Zeta\n- Zeta hai\n- Zeta ba\n")
                             .replace("- Iota\n", ""))
        stats = rewrite_human.measure(varied, "vi")
        gates = {row["gate"]: row for row in rewrite_human.gates(stats)}
        self.assertTrue(gates["tricolon-everywhere"]["pass"], stats["lists"])

    def test_nesting_is_two_lists_rather_than_one(self) -> None:
        """Three sub-points under each of three points is a different shape from one list of nine,
        and averaging them together would hide both. An earlier draft kept a single open run and
        silently discarded every deeper item, which turned this document into one list of three."""
        nested = "- Alpha\n  - một\n  - hai\n  - ba\n- Beta\n- Gamma\n"
        self.assertEqual(sorted(len(block) for block in rewrite_human.list_blocks(nested)), [3, 3])

    def test_an_ordered_list_is_the_same_shape_as_a_bulleted_one(self) -> None:
        # `1. 2. 3.` is a tricolon with different punctuation. Both forms and both closers.
        for text in ("1. Alpha\n2. Beta\n3. Gamma\n", "1) Alpha\n2) Beta\n3) Gamma\n"):
            with self.subTest(text):
                self.assertEqual(rewrite_human.list_geometry(text)["threes"], 1)

    def test_a_lone_bullet_is_not_a_list_and_a_loose_list_is_one(self) -> None:
        """One bullet has no geometry, and counting it as a list of one would drag every share
        toward whatever a writer used for a single aside. Blank lines inside a run do not end it,
        because a loose list in Markdown is still one list."""
        self.assertEqual(rewrite_human.list_blocks("Văn xuôi.\n\n- Chỉ một\n\nVăn xuôi nữa.\n"), [])
        self.assertEqual(rewrite_human.list_geometry("- Alpha\n\n- Beta\n\n- Gamma\n")["sizes"], [3])

    def test_no_reference_file_trips_the_list_shape_gate(self) -> None:
        """The corpus this threshold was measured against, standing as the regression test. One
        file scored 0.80 when the gate was written; it held eight identical `Core proofs / Useful
        scenes / Reject` triples and duplicated `product-category-playbooks.md`, so it was folded
        in and deleted rather than reshaped to pass. A new file that fails this is either a
        template or a duplicate, and both wanted rewriting before they wanted a passing number."""
        for path in sorted((SKILL_ROOT / "references").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            rows = {row["gate"]: row for row in
                    rewrite_human.gates(rewrite_human.measure(text, rewrite_human.detect_language(text)))}
            if "tricolon-everywhere" in rows:
                with self.subTest(path.name):
                    self.assertTrue(rows["tricolon-everywhere"]["pass"],
                                    rows["tricolon-everywhere"]["observed"])

    def test_the_two_tricolon_tells_describe_different_defects(self) -> None:
        """Both tables carry `everything arrives in threes`, word for word, and they are not the
        same finding. `tricolon-default` is `scope: prose` and matches three comma-separated
        phrases inside one sentence - which is often correct English, and fires on "physics, claim,
        or rights failure" in `anti-ai-quality.md`. `tricolon-everywhere` counts list lengths
        across a document. If the two ever collapse into one row, the structural half disappears
        and the regex will be left claiming to cover something it cannot see."""
        prose = [row for row in DataTableTests.rows("translation-tells.csv")
                 if row["id"] == "tricolon-default"]
        structural = [row for row in DataTableTests.rows("slop-tells.csv")
                      if row["id"] == "tricolon-everywhere"]
        self.assertEqual((len(prose), len(structural)), (1, 1))
        self.assertEqual(prose[0]["scope"], "prose")

        # The prose regex fires on a correct in-sentence triple and cannot reach a list of three.
        sentence = "Reject it for a physics, claim, or rights failure."
        self.assertTrue(re.search(prose[0]["detect_regex"], sentence), prose[0]["detect_regex"])
        self.assertEqual(rewrite_human.find_tells(self.THREES, "vi"), [])


class AddressRegisterTests(unittest.TestCase):
    """Vietnamese has no neutral second person, so who the copy addresses is grammar rather than
    tone, and a translated draft re-decides it at every sentence. Every assertion below is either a
    documented rule of the language or a false positive this checker would otherwise produce -
    which matters more here than in most gates, because half the forms in the table are also
    ordinary words and one wrong `failed` teaches the copywriter to stop running it."""

    ROWS = staticmethod(lambda: DataTableTests.rows("address-registers.csv"))

    def gates(self, text: str, channel: str | None = None) -> dict[str, dict]:
        report = check_address_register.check(text, self.ROWS(), channel)
        return {gate["gate"]: gate for gate in report["gates"]}

    def test_self_check_passes(self) -> None:
        self.assertEqual(check_address_register.self_check(self.ROWS()).strip(), "self-check passed")

    def test_every_detector_compiles_and_matches_only_its_own_probe(self) -> None:
        """The check the table's own generator cannot do. Nesting - `chúng tôi` inside `tôi`,
        `người ta` inside `ta`, `các bạn` inside `bạn` - is settled by the masking order in the
        script, not by any single regex, so it can only be verified by running the detector."""
        rows = self.ROWS()
        for row in rows:
            if row["probe"] == "-":
                continue
            with self.subTest(row["form"]):
                found = {hit["form"] for hit in check_address_register.detect(row["probe"], rows)}
                self.assertIn(row["form"], found,
                              f"{row['form']}'s own probe resolved to {sorted(found)}")
                # A probe is a natural sentence, and pairing is mandatory in Vietnamese, so
                # `cháu`'s probe has to contain `ông`. What must not appear is a form the row has
                # no relation to: that is nesting resolved the wrong way - `chúng tôi` reported as
                # `tôi`, `người ta` as `ta` - and it is what the masking order exists to prevent.
                allowed = ({row["form"]}
                           | set(check_address_register.cells(row["pairs_with"]))
                           | set(check_address_register.cells(row["composes_with"])))
                self.assertLessEqual(found, allowed,
                                     f"{row['form']}'s probe also matched {sorted(found - allowed)}")

    def test_the_pairing_relation_crosses_person_and_composition_is_symmetric(self) -> None:
        # Both relations are what the gates reason over. A one-sided `composes_with` would fail a
        # clean draft depending only on which form the writer happened to use first.
        forms = {row["form"]: row for row in self.ROWS()}
        for row in forms.values():
            for name in check_address_register.cells(row["composes_with"]):
                with self.subTest(pair=(row["form"], name)):
                    self.assertIn(row["form"],
                                  check_address_register.cells(forms[name]["composes_with"]))
            if row["pairs_with"] == "any":
                continue
            for name in check_address_register.cells(row["pairs_with"]):
                with self.subTest(pair=(row["form"], name)):
                    self.assertNotEqual(row["person"], forms[name]["person"])

    def test_every_row_declares_a_grade_this_skill_recognises(self) -> None:
        # The point of grading each row is that a reader can tell a rule of the language from a
        # house preference. An ungraded row reads as authority it has not earned.
        grades = {"standard-requirement", "standard-requirement-with-house-threshold",
                  "house-rule", "craft-heuristic"}
        for row in self.ROWS():
            with self.subTest(row["form"]):
                self.assertIn(row["evidence_grade"], grades)
                self.assertTrue(row["source"].strip())

    def test_mixing_two_tiers_in_one_piece_fails(self) -> None:
        """The defect in one line: every sentence polite, every sentence grammatical, and nobody
        decided. No sentence-level reader catches it."""
        mixed = ("Kính thưa quý vị, chúng tôi xin giới thiệu sản phẩm mới. Bạn sẽ thấy khác biệt "
                 "ngay lần đầu dùng. Bọn mình giao trong ngày ở Gò Vấp.")
        gates = self.gates(mixed)
        self.assertEqual(gates["one-address-form"]["status"], "failed")

    def test_the_inclusive_plural_trap_is_caught(self) -> None:
        """English `we` collapses a distinction Vietnamese keeps, so "we deliver in one day" comes
        back as `chúng ta giao trong ngày` - with the customer doing the delivering."""
        wrong = ("Chúng ta giao trong ngày ở Gò Vấp. Chúng tôi rang tại xưởng mỗi sáng. "
                 "Bạn nhận hàng trước sáu giờ chiều.")
        self.assertEqual(self.gates(wrong)["inclusive-exclusive"]["status"], "failed")

    def test_a_clean_one_register_draft_passes_every_gate(self) -> None:
        clean = ("Chúng tôi rang cà phê tại xưởng ở Gò Vấp và giao trong ngày. Anh chị đặt trước "
                 "sáu giờ chiều thì hôm sau có hàng. Ngày rang in dưới đáy túi. Không thấy ngày "
                 "rang thì đừng mua.")
        for name, gate in self.gates(clean, "web").items():
            with self.subTest(name):
                self.assertIn(gate["status"], ("passed", "skipped"), gate["why"])

    def test_an_ambiguous_form_reviews_rather_than_fails(self) -> None:
        """`kẻ mày` is an eyebrow pencil. A checker that hard-fails a cosmetics brand's own product
        copy is a checker nobody runs twice, so the answer is `review` and it names the string."""
        brow = ("Bút kẻ mày này giữ nét cả ngày, tôi dùng ba tháng rồi. Anh chị mua ở cửa hàng "
                "nào cũng được. Màu nâu tro phù hợp da sáng.")
        self.assertEqual(self.gates(brow)["no-archaic-or-impolite"]["status"], "review")
        # And the form that can only be the noun is not reported at all.
        self.assertEqual(check_address_register.detect("Lông mày dày tự nhiên.", self.ROWS()), [])

    def test_the_unit_is_registered_where_a_run_would_find_it(self) -> None:
        # A checker nothing points at is a script, not a capability.
        router = (SKILL_ROOT / "references" / "marketing-system-router.md").read_text(encoding="utf-8")
        self.assertIn("address-register.md", router)
        self.assertTrue((SKILL_ROOT / "references" / "address-register.md").exists())
        localise = next(row for row in DataTableTests.rows("command-artifacts.csv")
                        if row["command"] == "localise")
        self.assertIn("check_address_register.py", localise["machinery"])


class SpecificityTests(unittest.TestCase):
    """The gates in `rewrite_human.py` measure the shape of a sentence and can all pass on a sentence
    that says nothing. `Chúng tôi cam kết mang đến trải nghiệm tốt nhất` has good length variance, no
    pictograph and one register, and it is the single commonest machine-written line in Vietnamese
    marketing. This checker is the half that reads content, so the assertions below are mostly about
    the two directions it can be wrong in: passing empty copy, and failing copy that is merely plain.

    The second direction matters more. A checker that demands a citation for `200 chai mỗi tuần`
    teaches the copywriter to stop running it, and then nothing is measured at all."""

    def gates(self, text: str) -> dict[str, dict]:
        return {gate["gate"]: gate for gate in check_specificity.check(text)["gates"]}

    def test_self_check_passes(self) -> None:
        self.assertIn("passed", check_specificity.self_check())

    def test_a_bare_number_is_structure_and_does_not_count_as_a_fact(self) -> None:
        """The distinction the whole unit rests on. `3 lý do` and `bước 2` are how a listicle is
        built, and counting them would let any numbered outline pass as evidence."""
        for structure in ("3 lý do bạn nên chọn chúng tôi", "Bước 2: đặt hàng", "Top 5 mẫu mới"):
            with self.subTest(structure):
                self.assertEqual(check_specificity.quantities(structure), [])
        for fact in ("giao trong 2 giờ", "một ly 45.000đ", "delivered in 2 hours", "$12 flat"):
            with self.subTest(fact):
                self.assertTrue(check_specificity.quantities(fact), f"{fact} carries a unit")

    def test_a_sentence_initial_name_is_not_counted_and_a_mid_sentence_one_is(self) -> None:
        """Vietnamese writes each syllable of a name as its own token, so `Gò Vấp` at the start of a
        sentence is two capitals that mean nothing. Dropping only the first would count `Vấp`."""
        self.assertEqual(check_specificity.names("Gò Vấp là nơi rang", False), [])
        self.assertEqual(check_specificity.names("Rang tại Gò Vấp mỗi sáng", False), ["Gò Vấp"])
        self.assertEqual(check_specificity.names("Giao qua GHTK trong ngày", False), ["GHTK"])
        self.assertEqual(check_specificity.names("I called them twice", False), [])

    def test_title_case_buys_no_specificity(self) -> None:
        """`Cà Phê Rang Mộc Nguyên Chất` is four capitals and no name. Counting it would mean a
        writer could pass the fact floor by capitalising a headline, which is also a tell the
        translation table already flags as `title-case-vi`."""
        self.assertTrue(check_specificity.title_cased("Cà Phê Rang Mộc Nguyên Chất"))
        self.assertFalse(check_specificity.title_cased("Cà phê rang tại Gò Vấp"))
        self.assertEqual(check_specificity.names("Cà Phê Rang Mộc Nguyên Chất", True), [])

    def test_the_commonest_empty_vietnamese_draft_fails_on_content_not_cadence(self) -> None:
        empty = ("Chúng tôi cam kết mang đến trải nghiệm tốt nhất cho khách hàng. "
                 "Sản phẩm của chúng tôi luôn đảm bảo chất lượng và uy tín hàng đầu. "
                 "Đội ngũ chuyên nghiệp, tận tâm sẽ đồng hành cùng bạn trên mọi hành trình. "
                 "Hãy để chúng tôi chứng minh giá trị thực sự mà dịch vụ mang lại cho bạn.")
        report = check_specificity.check(empty)
        self.assertEqual(report["verdict"], "failed")
        self.assertEqual(report["facts"], 0)
        for gate in ("fact-floor", "fact-density", "brand-swap", "empty-adjective"):
            with self.subTest(gate):
                self.assertEqual(self.gates(empty)[gate]["status"], "failed")

    def test_the_cadence_gates_pass_the_draft_this_one_fails(self) -> None:
        """The justification for the unit existing. If `rewrite_human.py` already blocked this
        draft, a second script would be duplication - so this asserts that it does not."""
        empty = ("Bạn xứng đáng có thứ tốt hơn. "
                 "Chúng tôi làm ra sản phẩm này với tất cả sự cẩn thận mà một người thợ có thể dồn "
                 "vào công việc của mình, không hơn không kém. "
                 "Đơn giản là vậy. "
                 "Và nếu bạn thử một lần, chúng tôi tin bạn sẽ hiểu tại sao nhiều người đã ở lại "
                 "lâu như thế.")
        cadence = rewrite_human.gates(rewrite_human.measure(empty, "vi"))
        self.assertTrue(all(row["pass"] for row in cadence),
                        [row["gate"] for row in cadence if not row["pass"]])
        self.assertEqual(check_specificity.check(empty)["verdict"], "failed")

    def test_an_evidence_adjective_beside_a_fact_is_not_the_defect(self) -> None:
        """`slop-tells.csv` calls `adjective-substitute` critical, and the substitution is the whole
        defect. `premium` next to `ủ 80 giờ` summarises a fact the reader can check; `premium` alone
        in its sentence replaces it. One string match cannot tell those apart - only a sentence can,
        and that is why this gate lives here rather than in the phrase table."""
        substitute = ("Cà phê của chúng tôi là loại premium, chất lượng đảm bảo và rất uy tín. "
                      "Chúng tôi tin rằng bạn sẽ hài lòng với dịch vụ tận tâm này. "
                      "Sản phẩm luôn đạt tiêu chuẩn cao nhất trên thị trường hiện nay. "
                      "Hãy trải nghiệm sự khác biệt mà thương hiệu mang lại cho bạn.")
        beside = ("Cà phê premium này ủ lạnh 80 giờ ở Gò Vấp trước khi vào chai. "
                  "Một chai 250ml giá 65.000đ, đủ cho hai người uống sáng. "
                  "Mẻ đầu ra lò ngày 12 tháng 3, mỗi tuần chỉ 200 chai. "
                  "Đặt qua 0901234567 trước thứ năm nếu muốn nhận cuối tuần.")
        self.assertEqual(self.gates(substitute)["empty-adjective"]["status"], "failed")
        self.assertEqual(self.gates(beside)["empty-adjective"]["status"], "passed")

    def test_only_a_claim_about_the_world_needs_a_source(self) -> None:
        """A price, the brand's own stock count and a discount are all facts it owns. Demanding a
        citation for them is the false positive that would get this gate switched off."""
        own = ("Một ly 45.000đ, một túi 250g là 180.000đ tại xưởng Gò Vấp. "
               "Mỗi tuần chỉ 200 chai, rang thứ hai và thứ năm, giao trong 2 giờ. "
               "Đang giảm giá 20% cho đơn đầu tiên, tới hết ngày 12 tháng 3. "
               "Gọi 0901234567 nếu túi tới muộn, chúng tôi giao lại miễn phí.")
        self.assertEqual(self.gates(own)["sourced-number"]["status"], "passed")
        claim = ("Có tới 87% khách quay lại trong vòng một tháng sau lần mua đầu tiên. "
                 "Cà phê rang tại Gò Vấp mỗi sáng thứ hai, giao trong 2 giờ nội thành. "
                 "Một ly 45.000đ, ngày rang in dưới đáy túi cho bạn tự kiểm tra. "
                 "Gọi 0901234567 trước thứ năm nếu muốn nhận vào cuối tuần này.")
        self.assertEqual(self.gates(claim)["sourced-number"]["status"], "failed")
        sourced = claim.replace("Có tới 87%", "Theo khảo sát 320 đơn tháng 3 của xưởng, 87%")
        self.assertEqual(self.gates(sourced)["sourced-number"]["status"], "passed")

    def test_a_concentration_is_a_spec_not_a_finding(self) -> None:
        """The false positive this gate was caught producing on its first real draft. `axit azelaic
        10%` is what is in the bottle; `hiệu quả 90%` is a claim about what happens to people. A
        percentage alone cannot tell them apart, so the default is exempt and the gate fires only
        when the sentence also quantifies a person or an outcome."""
        self.assertFalse(check_specificity.needs_a_source("Dùng axit azelaic 10% trên da", "10%"))
        self.assertFalse(check_specificity.needs_a_source("Áo cotton 95%, dệt tại Nam Định", "95%"))
        self.assertTrue(check_specificity.needs_a_source("Hiệu quả lên tới 90% sau một liệu trình",
                                                        "90%"))
        self.assertTrue(check_specificity.needs_a_source("87% khách quay lại trong một tháng", "87%"))
        # A multiplier is comparative by construction and needs no context test.
        self.assertTrue(check_specificity.needs_a_source("Khô nhanh hơn 3 lần", "hơn 3 lần"))

    def test_stacked_hedges_fail_even_when_the_draft_is_otherwise_specific(self) -> None:
        hedged = ("Dịch vụ có thể giúp bạn tiết kiệm khá nhiều thời gian mỗi tuần. "
                  "Nhìn chung thì phần lớn khách hàng đều tương đối hài lòng với kết quả. "
                  "Rang tại Gò Vấp mỗi sáng thứ hai, giao trong 2 giờ nội thành. "
                  "Một ly 45.000đ, gọi 0901234567 để đặt trước thứ năm hàng tuần.")
        self.assertEqual(self.gates(hedged)["hedge-stack"]["status"], "failed")

    def test_the_word_lists_are_read_from_the_table_not_hardcoded(self) -> None:
        """If this script carried its own copy of the adjective list it would drift from
        `translation-tells.csv` within a month, and the two would then disagree about the same
        draft. Both layers must be reachable from the table in both languages."""
        for language in ("vi", "en"):
            for layer in ("evidence", "hedge"):
                with self.subTest(language=language, layer=layer):
                    self.assertTrue(check_specificity.phrase_rows(language, layer),
                                    f"no {layer} rows for {language} in translation-tells.csv")
        # The real proof is that what the script matches on is exactly what the table declares. A
        # hardcoded list would show up here as an id the table has never heard of, or a missing one.
        for layer in ("evidence", "hedge"):
            declared = {row["id"] for row in DataTableTests.rows("translation-tells.csv")
                        if row["layer"] == layer and row["language"] in ("vi", "any")}
            self.assertEqual({row["id"] for row in check_specificity.phrase_rows("vi", layer)},
                             declared, f"{layer} rows in the script differ from the table")

    def test_it_declines_to_judge_what_it_cannot_read(self) -> None:
        """A caption and a price list are the two inputs where every gate here is meaningless. Both
        have to come back as something other than `failed`, or the unit reports defects in work that
        has none - which is the failure mode the four-status vocabulary exists for."""
        caption = check_specificity.check("Rang mộc, giao nhanh.")
        self.assertEqual(caption["verdict"], "skipped")
        self.assertEqual(caption["gates"][0]["status"], "skipped")
        sheet = ("Ly nhỏ 35.000đ, ly lớn 45.000đ, túi 250g 180.000đ tại Gò Vấp. "
                 "Giao 2 giờ nội thành, 24 giờ đi Đà Nẵng, 48 giờ ra Hà Nội. "
                 "Rang thứ hai và thứ năm, mỗi mẻ 40kg, đóng túi 250g và 1kg. "
                 "Gọi 0901234567 hoặc 0987654321, mở 7 giờ tới 21 giờ mỗi ngày.")
        self.assertEqual(self.gates(sheet)["brand-swap"]["status"], "review")
        self.assertEqual(check_specificity.check(sheet)["verdict"], "review")

    def test_the_same_emptiness_in_english_fails_identically(self) -> None:
        english = ("We are committed to delivering the best possible experience to our customers. "
                   "Our products are always of premium quality and reliable standard. "
                   "Our dedicated team will accompany you on every step of the journey. "
                   "Let us prove the real value that our service brings to you.")
        report = check_specificity.check(english)
        self.assertEqual(report["language"], "en")
        self.assertEqual(report["verdict"], "failed")
        self.assertEqual(report["facts"], 0)

    def test_the_exit_code_matches_the_verdict(self) -> None:
        # A gate that always exits 0 cannot be wired into anything that stops on failure.
        self.assertEqual(check_specificity.STATUS_EXIT["passed"], 0)
        self.assertEqual(check_specificity.STATUS_EXIT["failed"], 2)
        self.assertEqual(check_specificity.STATUS_EXIT["review"], 3)

    def test_the_unit_is_registered_where_a_run_would_find_it(self) -> None:
        router = (SKILL_ROOT / "references" / "marketing-system-router.md").read_text(encoding="utf-8")
        self.assertIn("specificity.md", router)
        self.assertIn("check_specificity.py", router)
        self.assertTrue((SKILL_ROOT / "references" / "specificity.md").exists())
        humanise = next(row for row in DataTableTests.rows("command-artifacts.csv")
                        if row["command"] == "humanise")
        self.assertIn("check_specificity.py", humanise["machinery"])


class KpiScoringTests(unittest.TestCase):
    """Every number in here was read out of BSC_2025_template.xlsx sheet 2024, not invented.

    A scoring engine is the wrong place to be approximately right: the output is attached to
    somebody's bonus, and a formula that is wrong in the fourth branch stays wrong for a year
    because the first three branches keep producing plausible numbers. The fixtures are the real
    2024 card, including its bugs, so a rewrite that loses a branch fails here rather than in front
    of the person being scored.
    """

    EXAMPLES = SKILL_ROOT / "assets" / "examples" / "bsc-2024"

    @staticmethod
    def card(name: str) -> dict:
        return json.loads((KpiScoringTests.EXAMPLES / name).read_text(encoding="utf-8"))

    def test_revenue_ratio_matches_the_workbook_to_the_cent(self) -> None:
        got = score_kpi.achievement({
            "code": "F1.1.1", "direction": "higher_better", "calc_method": "ratio",
            "target": "3400000", "actual": "2890353.4840580029"})
        self.assertEqual(f"{got * 100:.2f}", "85.01")

    def test_cost_is_scored_target_over_actual(self) -> None:
        """The branch that inverts a whole year if it is wrong. F2.1 came in under plan, so it
        scores 143.20%; the higher-is-better formula on the same two numbers returns 69.81% and
        reports a well-run year as a failed one."""
        kpi = {"code": "F2.1", "direction": "lower_better", "calc_method": "ratio",
               "target": "1752681", "actual": "1223952.5694800001"}
        self.assertEqual(f"{score_kpi.achievement(kpi) * 100:.2f}", "143.20")
        inverted = dict(kpi, direction="higher_better")
        self.assertEqual(f"{score_kpi.achievement(inverted) * 100:.2f}", "69.83")

    def test_a_scale_is_not_a_ratio_where_the_rungs_are_misaligned(self) -> None:
        """C3.1: rungs of 0/1/2/3/4 against a target of 3 put the full rung at 4, so an actual of 3
        that met its target scores 75% on the scale and 100% as a ratio. The workbook typed 100%.
        This test exists to keep both numbers visible, because a rewrite that quietly reaches for
        actual/target here would agree with the shipped file and still be wrong."""
        rungs = {"0.00": "0", "0.25": "1", "0.50": "2", "0.75": "3", "1.00": "4"}
        scaled = score_kpi.achievement({
            "code": "C3.1", "direction": "higher_better", "calc_method": "scale",
            "target": "3", "actual": "3", "scale": rungs})
        self.assertEqual(scaled, Decimal("0.75"))
        as_ratio = score_kpi.achievement({
            "code": "C3.1", "direction": "higher_better", "calc_method": "ratio",
            "target": "3", "actual": "3"})
        self.assertEqual(as_ratio, Decimal("1"))

    def test_an_aligned_scale_agrees_with_the_ratio(self) -> None:
        """C2.2, the row where the two formulas give the same answer. Worth pinning: a suite that
        only tested this row would pass with the scale branch deleted."""
        got = score_kpi.achievement({
            "code": "C2.2", "direction": "higher_better", "calc_method": "scale",
            "target": "4", "actual": "3",
            "scale": {"0.00": "0", "0.25": "1", "0.50": "2", "0.75": "3", "1.00": "4"}})
        self.assertEqual(got, Decimal("0.75"))

    def test_dates_score_on_a_day_axis_and_earlier_is_better(self) -> None:
        kpi = {"code": "P2.1", "direction": "lower_better", "calc_method": "date",
               "target": "2024-06-30", "actual": "2024-01-30",
               "scale": {"0.00": "2024-11-30", "0.25": "2024-10-30", "0.50": "2024-09-30",
                         "0.75": "2024-07-30", "1.00": "2024-06-30"}}
        self.assertEqual(score_kpi.achievement(kpi), Decimal("1"))
        # Each rung, walked. A single on-time fixture passes even if the comparison is reversed.
        for actual, expected in (("2024-06-30", "1.00"), ("2024-07-15", "0.75"),
                                 ("2024-08-01", "0.50"), ("2024-10-01", "0.25"),
                                 ("2024-12-25", "0.00")):
            with self.subTest(actual):
                self.assertEqual(score_kpi.achievement(dict(kpi, actual=actual)),
                                 Decimal(expected))

    def test_caps_differ_by_whether_the_kpi_is_financial(self) -> None:
        over = Decimal("1.4319844115729352")
        self.assertEqual(score_kpi.capped(over, True), (Decimal("1.30"), True))
        self.assertEqual(score_kpi.capped(over, False), (Decimal("1.00"), True))
        # An override keeps the raw figure and still reports that the cap was breached, so the
        # decision stays auditable. The workbook's hand-typed 1.2 loses both.
        self.assertEqual(score_kpi.capped(over, False, override=True), (over, True))
        under = Decimal("0.8501")
        self.assertEqual(score_kpi.capped(under, True), (under, False))

    def test_rank_boundaries_including_the_one_that_uses_less_than_or_equal(self) -> None:
        for total, expected in (("0.6999", "C"), ("0.70", "B"), ("0.7999", "B"), ("0.80", "A3"),
                                ("0.90", "A3"), ("0.9001", "A2"), ("1.0499", "A2"),
                                ("1.05", "A1"), ("1.30", "A1")):
            with self.subTest(total):
                self.assertEqual(score_kpi.rank(Decimal(total))[0], expected)
        # A1 has to sort above A3, which it does not do alphabetically. This is why rank_order is
        # stored as an integer rather than the code being sorted.
        self.assertGreater(score_kpi.rank(Decimal("1.10"))[1], score_kpi.rank(Decimal("0.85"))[1])

    def test_a_missing_actual_refuses_instead_of_scoring_full_marks(self) -> None:
        """The most expensive bug in the source file: G1.1 carries a tenth of the card, has no
        actual, and reports 100%."""
        with self.assertRaises(score_kpi.Unscoreable):
            score_kpi.achievement({"code": "G1.1", "direction": "higher_better",
                                   "calc_method": "ratio", "target": "1.00", "actual": None})

    def test_a_zero_actual_on_a_cost_kpi_refuses(self) -> None:
        # Not the mirror of a zero actual on a revenue KPI, which scores zero and is fine. Spending
        # nothing is a missing number far more often than it is a perfect year.
        with self.assertRaises(score_kpi.Unscoreable):
            score_kpi.achievement({"code": "F2.1", "direction": "lower_better",
                                   "calc_method": "ratio", "target": "1752681", "actual": "0"})
        zero_revenue = score_kpi.achievement({"code": "F1.1.1", "direction": "higher_better",
                                              "calc_method": "ratio", "target": "3400000",
                                              "actual": "0"})
        self.assertEqual(zero_revenue, Decimal(0))

    def test_arithmetic_is_decimal_all_the_way_through(self) -> None:
        """The workbook leaks 0.9500000000000001 and 0.31749999999999995 into cells a bonus is read
        from. Float would reproduce both."""
        result = score_kpi.score(self.card("card-repaired.json"))
        self.assertIsInstance(result["total_score"], Decimal)
        customer = result["aspects"]["C"]["score"]
        self.assertEqual(customer, Decimal("0.275"))
        self.assertNotEqual(str(customer), str(0.1 + 0.05 + 0.05 + 0.0375 + 0.0375))

    def test_the_card_as_shipped_refuses_and_names_all_three_faults(self) -> None:
        result = score_kpi.score(self.card("card-as-shipped.json"))
        self.assertFalse(result["scoreable"])
        self.assertIsNone(result["total_score"])
        joined = " ".join(result["blocking_problems"])
        self.assertIn("G1.1 has no actual", joined)
        self.assertIn("F1.2.1 appears 2 times", joined)
        # And the weight sum must NOT be reported as a fault: the weights are exactly 100%, and an
        # earlier version of this engine said 90% because it summed only the rows that scored.
        self.assertNotIn("weights sum to", joined)

    def test_the_repaired_card_reproduces_the_workbook_total_the_workbook_should_have_had(self) -> None:
        """98.79% is what the file reports. 94.47% is what it scores once the caps are applied, and
        also what the engine computes from the raw targets and actuals — by two different routes,
        because the two remaining achievement bugs are both 25 points at a 5% weight with opposite
        signs and cancel exactly. That coincidence is the reason a total agreeing with a spreadsheet
        is not evidence the spreadsheet is right."""
        result = score_kpi.score(self.card("card-repaired.json"))
        self.assertTrue(result["scoreable"], result["blocking_problems"])
        self.assertEqual(f"{result['total_score'] * 100:.2f}", "94.47")
        self.assertEqual(result["rank"], "A2")
        self.assertEqual(f"{result['aspects']['F']['score'] * 100:.2f}", "46.97")
        # The file's own Finance subtotal, for contrast: it uses the uncapped 143.20%.
        self.assertEqual(f"{Decimal('0.482882291706882506') * 100:.2f}", "48.29")

    def test_aspect_weights_match_the_proportions_the_card_declares(self) -> None:
        """The check that caught a live bug: C1.2 names a library metric filed under Processes, so
        the library's aspect silently moved 5% of the card out of Customer and the two subtotals
        were wrong while the total stayed right."""
        result = score_kpi.score(self.card("card-repaired.json"))
        for aspect, share in (("F", "0.50"), ("C", "0.30"), ("P", "0.10"), ("G", "0.10")):
            with self.subTest(aspect):
                self.assertEqual(result["aspects"][aspect]["weight"], Decimal(share))

    def test_an_aspect_of_only_lagging_kpis_is_warned_about_not_blocked(self) -> None:
        result = score_kpi.score(self.card("card-repaired.json"))
        self.assertTrue(any("only lagging" in warning for warning in result["warnings"]))
        self.assertTrue(result["scoreable"])

    def test_every_catalogued_metric_is_scoreable_by_the_engine(self) -> None:
        """A metric row whose calc_method or direction the engine does not implement is a lookup
        that produces an unrunnable answer."""
        for row in score_kpi.catalog().values():
            with self.subTest(row["kpi_id"]):
                self.assertIn(row["calc_method"], ("ratio", "scale", "date"))
                self.assertIn(row["direction"], ("higher_better", "lower_better"))
                self.assertIn(row["aspect"], score_kpi.ASPECTS)
                self.assertIn(row["indicator_type"], ("leading", "lagging"))
                self.assertIn(row["is_financial"], ("yes", "no"))

    def test_guideline_aspect_weights_are_ordered_and_reachable(self) -> None:
        rows = DataTableTests.rows("kpi-aspect-weights.csv")
        for row in rows:
            with self.subTest(f"{row['block']}/{row['aspect']}"):
                low, high = Decimal(row["min_share"]), Decimal(row["max_share"])
                self.assertLessEqual(low, high, "min_share above max_share")
                self.assertIn(row["aspect"], score_kpi.ASPECTS)
        for block in {row["block"] for row in rows}:
            members = [row for row in rows if row["block"] == block]
            with self.subTest(block):
                self.assertEqual(len(members), 4, "a block must allocate all four aspects")
                low = sum(Decimal(row["min_share"]) for row in members)
                high = sum(Decimal(row["max_share"]) for row in members)
                # The band has to contain 100%, or no legal allocation exists inside the guideline.
                self.assertLessEqual(low, Decimal(1), f"{block} cannot reach 100%")
                self.assertGreaterEqual(high, Decimal(1), f"{block} cannot come down to 100%")

    def test_the_pipeline_is_registered_with_its_reference_and_script(self) -> None:
        pipeline = load_registry()["pipelines"]["score-kpi"]
        self.assertIn("kpi-scorecards.md", pipeline["references"])
        self.assertIn("score_kpi.py", pipeline["scripts"])
        self.assertTrue((SKILL_ROOT / "references" / "kpi-scorecards.md").exists())

    def test_kpi_requests_route_to_the_kpi_pipeline(self) -> None:
        registry = load_registry()
        for request in ("xây dựng KPI cho phòng marketing năm nay",
                        "build a balanced scorecard for the company",
                        "chấm điểm BSC 2024 giúp tôi"):
            with self.subTest(request):
                self.assertEqual(route_pipeline({"request": request}, registry)["pipeline"],
                                 "score-kpi")

    def test_adding_the_kpi_route_did_not_steal_other_requests(self) -> None:
        registry = load_registry()
        unchanged = {
            "lên kế hoạch marketing cho quán bún bò": "plan-from-zero",
            "thiết kế menu quán cà phê": "design-render",
            "nghiên cứu thị trường trà sữa": "deep-research",
            "viết lại đoạn này cho tự nhiên, đang bị dịch máy": "rewrite-human",
        }
        for request, expected in unchanged.items():
            with self.subTest(request):
                self.assertEqual(route_pipeline({"request": request}, registry)["pipeline"], expected)


class IdentityPlanTests(unittest.TestCase):
    """identity-design.md claims a logo can be checked before anyone opens a drawing tool. That is
    only true if the checking is arithmetic, so these tests are about the arithmetic being real:
    a mark that fails 16px has to be told so, and a ratio outside the dial has to be clamped with
    the correct reason attached."""

    HAIRLINE = {
        "thinnest_stroke_pct_of_height": 2.0, "smallest_counter_pct_of_height": 9.0,
        "distinct_elements": 4, "content_radius_pct_of_width": 47,
        "mark_colour": "#2b6cb0", "approved_backgrounds": ["#ffffff"],
        "smallest_required_slot": "favicon-16",
    }

    def test_a_hairline_mark_is_failed_at_the_favicon_and_told_which_element_broke(self) -> None:
        plan = plan_identity.plan_identity(dict(self.HAIRLINE))
        favicon = next(slot for slot in plan["slot_report"] if slot["slot"] == "favicon-16")
        self.assertFalse(favicon["passes"])
        # Three independent failures, each named. A single "too detailed" verdict would leave the
        # designer guessing which of the three to fix.
        self.assertEqual(len(favicon["fails"]), 3, favicon["fails"])
        self.assertIn("simplified variant", plan["verdict"])

    def test_a_mark_drawn_to_the_floor_passes_the_slot_it_was_drawn_for(self) -> None:
        plan = plan_identity.plan_identity({
            "thinnest_stroke_pct_of_height": 6.25, "smallest_counter_pct_of_height": 12.5,
            "distinct_elements": 2, "content_radius_pct_of_width": 38,
            "smallest_required_slot": "favicon-16",
        })
        self.assertEqual(plan["derived_minimum_size_px"], 16)
        self.assertIn("descending-render test", plan["verdict"])

    def test_the_logotype_exemption_stops_covering_a_mark_that_is_a_control(self) -> None:
        # The exemption is the trap the reference is written around: a logo cannot fail SC 1.4.3,
        # but the moment it is also the home link, SC 1.4.11 wants 3:1 and the exemption is silent.
        # #8a8a8a is 3.45:1 and would pass, which is the point: mid greys are further from the floor
        # than they look, so the test has to name a colour that genuinely fails.
        low = {"mark_colour": "#a0a0a0", "approved_backgrounds": ["#ffffff"],
               "thinnest_stroke_pct_of_height": 10, "distinct_elements": 1}
        exempt = plan_identity.plan_identity(dict(low))["contrast"][0]
        self.assertTrue(exempt["logotype_exemption_applies"])
        self.assertLess(exempt["ratio"], 3.0)
        self.assertIn("Exempt is not legible", exempt["verdict"])
        as_control = plan_identity.plan_identity({**low, "mark_is_a_link_or_control": True})
        self.assertIn("Fails SC 1.4.11", as_control["contrast"][0]["verdict"])

    def test_sizes_sharing_a_ratio_share_one_master(self) -> None:
        plan = plan_identity.plan_identity({
            "thinnest_stroke_pct_of_height": 10, "distinct_elements": 1,
            "banner_sizes": ["300x250", "336x280", "728x90", "1080x1920"],
        })
        families = {family["design_master"]: family for family in plan["banner_families"]}
        # 300x250 and 336x280 are both close to 6:5, so they are one design and two exports.
        self.assertEqual(families["336x280"]["derive_as_exports"], ["300x250"])
        self.assertEqual(families["336x280"]["orientation"], "square-ish")
        self.assertEqual(families["728x90"]["derive_as_exports"], [])
        self.assertIn("safe band", families["1080x1920"]["note"])

    def test_a_ratio_over_the_dial_is_clamped_with_the_ceiling_explained(self) -> None:
        # The first version of this reported the dial's breaks_at sentence, which describes the
        # BOTTOM of the range, as the reason for clamping at the top. A wrong explanation attached
        # to a correct number is worse than no explanation, because it gets quoted.
        plan = plan_identity.plan_identity({
            "thinnest_stroke_pct_of_height": 10, "distinct_elements": 1,
            "body_px": 16, "headline_ratio": 6.0, "type_steps": 5,
        })["type_scale"]
        self.assertTrue(plan["clamped"])
        self.assertEqual(plan["headline_ratio_used"], 4.5)
        self.assertNotIn("Below 1.6", plan["clamp_reason"])
        self.assertIn("ceiling", plan["clamp_reason"])
        self.assertEqual(plan["ladder_px"][0], 16.0)
        self.assertAlmostEqual(plan["ladder_px"][-1], 16 * 4.5, delta=0.2)


class VirtualModelTests(unittest.TestCase):
    """A recurring identity is a different job from editing one supplied photo, and the two
    pipelines must stay disambiguated by phrasing alone, since a router that guesses wrong
    sends a one-off edit through a whole identity build or vice versa."""

    def test_the_pipeline_is_registered_with_its_references_and_scripts(self) -> None:
        pipeline = load_registry()["pipelines"]["virtual-model"]
        for reference in pipeline["references"]:
            with self.subTest(reference):
                self.assertTrue((SKILL_ROOT / "references" / reference).exists())
        for script in pipeline["scripts"]:
            with self.subTest(script):
                self.assertTrue((SKILL_ROOT / "scripts" / script).exists())

    def test_a_recurring_identity_request_routes_to_the_virtual_model_pipeline(self) -> None:
        registry = load_registry()
        for request in ("build a virtual AI model for our brand's Instagram",
                        "we need a consistent virtual influencer to wear our outfits",
                        "tôi cần một người mẫu ảo nhất quán cho các bộ trang phục mới"):
            with self.subTest(request):
                self.assertEqual(route_pipeline({"request": request}, registry)["pipeline"],
                                 "virtual-model")

    def test_a_one_off_photo_edit_still_routes_to_image_from_reference(self) -> None:
        registry = load_registry()
        for request in ("sửa lại ảnh này, đổi áo cho người trong ảnh",
                        "change the outfit on this photo of our model",
                        "edit this product photo and swap the model outfit"):
            with self.subTest(request):
                self.assertEqual(route_pipeline({"request": request}, registry)["pipeline"],
                                 "image-from-reference")

    def test_adding_the_virtual_model_route_did_not_steal_other_requests(self) -> None:
        registry = load_registry()
        unchanged = {
            "lên kế hoạch marketing cho quán bún bò": "plan-from-zero",
            "thiết kế menu quán cà phê": "design-render",
            "chấm điểm BSC 2024 giúp tôi": "score-kpi",
        }
        for request, expected in unchanged.items():
            with self.subTest(request):
                self.assertEqual(route_pipeline({"request": request}, registry)["pipeline"], expected)


class GenerateImageTests(unittest.TestCase):
    """`generate_image.py` is the one script that can reach a real network endpoint holding a
    real key, so every test here stays offline: the key is mocked to an empty string, the base
    and model are fake, and no test ever inspects `.env` or prints a real credential."""

    def test_a_prompt_must_come_from_somewhere(self) -> None:
        with self.assertRaises(ValueError):
            generate_image._read_prompt(argparse.Namespace(prompt=None, prompt_file=None))

    def test_generate_request_carries_only_the_fields_that_were_set(self) -> None:
        args = argparse.Namespace(n=2, size=None, quality=None, output_format=None)
        body = generate_image._build_generate_request(args, "fake-model", "a red fox in snow")
        self.assertEqual(body, {"model": "fake-model", "prompt": "a red fox in snow", "n": 2})

    def test_edit_request_uses_the_singular_field_for_one_image_and_plural_for_several(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            one = Path(tmp) / "a.png"
            one.write_bytes(b"\x89PNG\r\n\x1a\n")
            two = Path(tmp) / "b.png"
            two.write_bytes(b"\x89PNG\r\n\x1a\n")

            single = argparse.Namespace(input=[str(one)], mask=None, n=1, size=None,
                                        quality=None, output_format=None)
            body, content_type = generate_image._build_edit_request(single, "fake-model", "swap the jacket")
            self.assertIn("multipart/form-data", content_type)
            self.assertIn(b'name="image"', body)
            self.assertNotIn(b'name="image[]"', body)

            several = argparse.Namespace(input=[str(one), str(two)], mask=None, n=1, size=None,
                                         quality=None, output_format=None)
            body_several, _ = generate_image._build_edit_request(several, "fake-model", "swap the jacket")
            self.assertIn(b'name="image[]"', body_several)

    def test_dry_run_builds_the_request_and_needs_no_key(self) -> None:
        argv = ["generate_image.py", "--prompt", "a red fox in snow", "--base", "http://example.test",
                "--model", "fake-model", "--dry-run"]
        with mock.patch.object(generate_image.sys, "argv", argv), \
             mock.patch.object(generate_image, "env_get", return_value=""):
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                exit_code = generate_image.main()
        self.assertEqual(exit_code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["url"], "http://example.test/v1/images/generations")
        self.assertEqual(payload["authorization"], "(none configured)")

    def test_a_missing_key_is_refused_before_any_network_call(self) -> None:
        argv = ["generate_image.py", "--prompt", "a red fox in snow", "--base", "http://example.test",
                "--model", "fake-model"]
        with mock.patch.object(generate_image.sys, "argv", argv), \
             mock.patch.object(generate_image, "env_get", return_value=""):
            buffer = io.StringIO()
            with contextlib.redirect_stderr(buffer):
                exit_code = generate_image.main()
        self.assertEqual(exit_code, 1)
        self.assertIn("MINTHEP_IMAGE_KEY is not configured", buffer.getvalue())


class ListCapabilitiesTests(unittest.TestCase):
    def test_every_pipeline_reference_table_and_script_is_listed(self) -> None:
        capabilities = list_capabilities.build_capabilities()
        registry = load_registry()
        self.assertEqual({p["name"] for p in capabilities["pipelines"]}, set(registry["pipelines"]))
        self.assertEqual({r["file"] for r in capabilities["references"]},
                         {path.name for path in (SKILL_ROOT / "references").glob("*.md")})
        self.assertEqual({d["file"] for d in capabilities["data_tables"]},
                         {path.name for path in (SKILL_ROOT / "data").glob("*.csv")})
        script_files = {s["file"] for s in capabilities["scripts"]}
        self.assertNotIn("test_tools.py", script_files)
        self.assertNotIn("_env.py", script_files)
        self.assertIn("generate_image.py", script_files)

    def test_a_query_narrows_every_section_to_what_it_matches(self) -> None:
        capabilities = list_capabilities.build_capabilities("virtual")
        self.assertEqual([p["name"] for p in capabilities["pipelines"]], ["virtual-model"])
        self.assertTrue(capabilities["references"])
        for reference in capabilities["references"]:
            with self.subTest(reference["file"]):
                self.assertTrue("virtual" in reference["file"].lower()
                               or "virtual" in reference["title"].lower())


class CommandSurfaceTests(unittest.TestCase):
    """The command surface is the only unit whose value is entirely in its graph. A reference can
    be slightly wrong and still be useful; a dependency graph with one bad edge plans work in an
    order that cannot run, and does it confidently. So these tests check the graph, not the prose."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.surface = plan_command_chain.Surface.load()
        cls.rows = cls.surface.rows

    def test_every_declared_input_is_produced_by_something_or_supplied_by_the_user(self) -> None:
        produced = {row["produces"] for row in self.rows}
        for row in self.rows:
            for alias in plan_command_chain.split_list(row["also_satisfies"]):
                produced.add(alias)
        for row in self.rows:
            for column in ("takes", "also_uses"):
                for artifact in plan_command_chain.split_list(row[column]):
                    with self.subTest(command=row["command"], column=column, artifact=artifact):
                        self.assertTrue(
                            artifact in produced
                            or artifact in plan_command_chain.ROOT_ARTIFACTS,
                            f"{row['command']}.{column} needs {artifact!r}, which nothing "
                            "produces and which is not a root the user supplies",
                        )

    def test_only_the_brief_and_the_photograph_come_from_outside(self) -> None:
        """Adding a third root would mean the skill had quietly started accepting an artefact it
        neither produces nor asks for, which is where invented strategy enters a plan."""
        self.assertEqual(plan_command_chain.ROOT_ARTIFACTS,
                         ("cold-brief", "source-photograph"))

    def test_each_artefact_has_exactly_one_producing_command(self) -> None:
        """Two commands producing the same artefact would make the chain ambiguous, and the
        planner would silently pick whichever it walked into first."""
        seen: dict[str, str] = {}
        for row in self.rows:
            with self.subTest(artifact=row["produces"]):
                self.assertNotIn(row["produces"], seen,
                                 f"{row['produces']} is produced by both {row['command']} "
                                 f"and {seen.get(row['produces'])}")
            seen[row["produces"]] = row["command"]

    def test_no_command_can_depend_on_its_own_output(self) -> None:
        for row in self.rows:
            inputs = set(plan_command_chain.split_list(row["takes"]))
            with self.subTest(command=row["command"]):
                self.assertNotIn(row["produces"], inputs)

    def test_every_goal_is_reachable_from_a_cold_brief_and_a_photograph(self) -> None:
        """A command nothing can reach is a command that will never run. This walks all 28 with
        only the two roots supplied, which is also the honest worst case for a new user."""
        have = set(plan_command_chain.ROOT_ARTIFACTS)
        for row in self.rows:
            with self.subTest(command=row["command"]):
                plan = self.surface.plan(row["command"], set(have))
                self.assertEqual(plan["you_must_supply"], [],
                                 f"{row['command']} is unreachable even with both roots")
                self.assertEqual(plan["steps"][-1]["command"], row["command"])

    def test_a_planned_chain_can_actually_run_in_the_order_it_is_printed(self) -> None:
        """The ordering pass re-sorts the depth-first result to read discover-before-decide. That
        rewrite is where a valid plan would most easily become an invalid one, so every plan the
        planner produces is fed back through the independent verifier."""
        have = set(plan_command_chain.ROOT_ARTIFACTS)
        for row in self.rows:
            with self.subTest(command=row["command"]):
                plan = self.surface.plan(row["command"], set(have))
                report = self.surface.verify(plan["commands"])
                self.assertTrue(report["runnable"], f"{row['command']}: {report['faults']}")

    def test_the_ordering_never_puts_a_later_category_before_an_earlier_one(self) -> None:
        order = plan_command_chain.CATEGORY_ORDER
        plan = self.surface.plan("improve", set(plan_command_chain.ROOT_ARTIFACTS))
        indices = [order.index(step["category"]) for step in plan["steps"]]
        self.assertEqual(indices, sorted(indices),
                         "the longest chain in the skill reads out of phase: "
                         f"{[s['command'] for s in plan['steps']]}")

    def test_naming_an_artefact_you_already_have_shortens_the_chain(self) -> None:
        """The collapse trade is the skill's answer to "just make me some photos". If the
        arithmetic behind it stops holding, the offer becomes a false promise."""
        long_plan = self.surface.plan("expand", {"source-photograph"})
        short_plan = self.surface.plan("expand", {"source-photograph", "positioning-platform"})
        self.assertEqual(len(long_plan["steps"]), 8)
        self.assertEqual(len(short_plan["steps"]), 3)
        self.assertEqual(short_plan["commands"], ["brief", "compose", "expand"])
        saving = {item["if_you_already_have"]: item["chain_drops_to"]
                  for item in long_plan["collapse_if_you_have"]}
        self.assertEqual(saving["positioning-platform"], 3)
        self.assertEqual(saving["creative-brief"], 2)

    def test_a_chain_with_a_missing_input_is_reported_as_unrunnable(self) -> None:
        report = self.surface.verify(["produce", "adapt", "approve"])
        self.assertFalse(report["runnable"])
        missing = {fault["missing"] for fault in report["faults"]}
        self.assertIn("creative-brief", missing)
        self.assertIn("campaign-plan", missing)

    def test_production_cannot_be_reached_without_the_strategy_spine(self) -> None:
        """"Production before strategy" is a refusal the unit states in prose. Prose does not
        enforce it; the graph does. Launching has to pull in positioning, offer and plan."""
        plan = self.surface.plan("launch", set(plan_command_chain.ROOT_ARTIFACTS))
        for command in ("position", "offer", "plan", "approve"):
            with self.subTest(command=command):
                self.assertIn(command, plan["commands"])

    def test_every_command_declares_machinery_that_exists_on_disk(self) -> None:
        """A command whose references and scripts do not exist is a promise, not a capability.
        This is the test that stops the surface growing verbs the skill cannot perform."""
        for row in self.rows:
            for item in plan_command_chain.split_list(row["machinery"]):
                target = item.split(" ")[0]
                if target.endswith(".md") and "/" not in target:
                    target = f"references/{target}"
                with self.subTest(command=row["command"], path=target):
                    self.assertTrue((SKILL_ROOT / target).exists(),
                                    f"{row['command']} points at {target}, which is not there")

    def test_every_command_says_what_it_refuses_and_what_it_does_not_do(self) -> None:
        """These two columns are why the plan can be trusted at a glance: a step that lists no
        refusal reads as a step with no judgement in it."""
        for row in self.rows:
            with self.subTest(command=row["command"]):
                self.assertGreater(len(row["refuses"]), 30)
                self.assertGreater(len(row["what_it_does_not_do"]), 30)
                self.assertIn(row["category"], plan_command_chain.CATEGORY_ORDER)

    def test_the_reference_and_the_table_agree_on_the_command_list(self) -> None:
        """The reference groups the commands into a category table by hand. Divergence there is
        how a unit starts documenting a surface it no longer has."""
        text = (SKILL_ROOT / "references" / "command-surface.md").read_text(encoding="utf-8")
        for row in self.rows:
            with self.subTest(command=row["command"]):
                self.assertIn(row["command"], text)

    def test_the_chain_lengths_quoted_in_the_reference_are_the_computed_ones(self) -> None:
        """The reference prints 8, 9, 16 and 19 as worst cases. Those are outputs of the graph,
        so an edge added anywhere upstream changes them, and a stale number in a reference is
        indistinguishable from an invented one."""
        text = (SKILL_ROOT / "references" / "command-surface.md").read_text(encoding="utf-8")
        for goal, expected in (("expand", 8), ("generate", 9), ("launch", 16), ("improve", 19)):
            with self.subTest(goal=goal):
                plan = self.surface.plan(goal, {"source-photograph"})
                self.assertEqual(len(plan["steps"]), expected)
                self.assertIn(f"| {expected} |", text)


class ColourGateTests(unittest.TestCase):
    """The colour unit's arithmetic, and the discipline that keeps its verdicts worth reading.

    Five of the nine gates in `data/colour-gates.csv` are house rules: the shape of the rule is
    defensible and the number is ours. That is survivable only while two things stay true — the
    table says which gates those are, and the gates that do fail mean something. Every test below
    defends one of the two.

    Four of them exist because the first version of the checker failed them. It compared a colour
    to itself and called zero separation a defect; it called an off-white the same hue family as
    lime on the strength of a rounding error; it ruled on a use it cannot see; and it failed a pair
    by 0.0004 against a threshold it had invented. Ten of the twenty shipped palettes came back
    broken, and none of the ten was.
    """

    # Every fifth value, which is 140,608 conversions and about a second. Sampling every third
    # value moves no p90 below by more than 0.1 degrees except in the C 0.00 bucket, where the
    # sample is small either way, so the finer sweep buys nothing but runtime.
    HUE_SWEEP_STEP = 5
    NEAR_NEUTRAL_LIMIT = 0.055

    # Held here rather than in plan_palette because they are the measurement's inputs, not the
    # module's data. Ten hues spread around the wheel plus a neutral, which is the seed that broke
    # the linear-lightness ramp worst.
    RAMP_SEEDS = ("#2A4BD7", "#0F8A5F", "#E8B004", "#00A3AD", "#C1121F",
                  "#6E1420", "#3AB795", "#8A6B1F", "#FF5A5F", "#161616")

    # Which constant each row of the table is quoting. A row that stops quoting its constant has
    # started documenting a threshold the code no longer holds.
    QUOTES = {
        "body-text-contrast": ("WCAG_BODY",),
        "large-text-contrast": ("WCAG_LARGE",),
        "non-text-contrast": ("WCAG_NON_TEXT",),
        "colour-is-not-the-only-cue": ("CVD_COLLAPSE_DISTANCE",),
        "same-hue-lightness-separation": ("SAME_HUE_DEGREES", "HUE_NEEDS_CHROMA",
                                         "LIGHTNESS_SEPARATION", "LIGHTNESS_SEPARATION_FAIL"),
        "no-vibrating-edge": ("VIBRATION_MAX_DELTA_L", "VIBRATION_MIN_CHROMA",
                              "VIBRATION_MIN_HUE_GAP"),
        "chroma-budget-by-count": ("LOUD_CHROMA", "CHROMA_BUDGET_LOUD_MAX"),
        "chroma-budget-by-surface-share": ("LOUD_CHROMA", "CHROMA_SHARE_MAX"),
        "ramp-step-evenness": ("RAMP_EVENNESS_TOLERANCE",),
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.swing = cls.sweep_hue_stability(cls.HUE_SWEEP_STEP, cls.NEAR_NEUTRAL_LIMIT)

    @staticmethod
    def sweep_hue_stability(step: int, limit: float) -> dict[float, dict[str, float]]:
        """How far a near-neutral's OKLCH hue angle moves under the smallest possible colour change.

        Walks the sRGB cube at `step`, keeps everything under `limit` chroma, and for each one adds
        1 to each channel in turn — the smallest change 8-bit colour can express — and measures the
        hue angle it moves. Buckets by chroma rounded to 0.01. This is the derivation of
        `HUE_NEEDS_CHROMA`, re-run rather than read off the comment that records it.
        """
        buckets: dict[float, list[float]] = {}
        values = range(0, 256, step)
        for red in values:
            for green in values:
                for blue in values:
                    measured = plan_palette.to_oklch("#%02X%02X%02X" % (red, green, blue))
                    if measured["C"] > limit:
                        continue
                    bucket = round(measured["C"], 2)
                    for shift in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                        moved = tuple(min(255, channel + delta)
                                      for channel, delta in zip((red, green, blue), shift))
                        if moved == (red, green, blue):
                            continue
                        neighbour = plan_palette.to_oklch("#%02X%02X%02X" % moved)
                        buckets.setdefault(bucket, []).append(
                            plan_palette.hue_gap(measured["h"], neighbour["h"])
                        )
        return {
            bucket: {
                "n": len(swings),
                "median": statistics.median(swings),
                "p90": sorted(swings)[int(0.9 * (len(swings) - 1))],
            }
            for bucket, swings in buckets.items()
        }

    @staticmethod
    def gate(payload: dict, name: str) -> dict:
        return next(g for g in payload["acceptance_gates"] if g["gate"] == name)

    def test_the_case_against_hsv_is_the_one_the_arithmetic_makes(self) -> None:
        """The module docstring justifies the whole choice of space on one worked pair: HSV gives
        pure yellow and pure blue the same value, and they are half the OKLCH lightness scale apart.
        That argument is the reason a designer is being asked to abandon a familiar wheel, so the
        four numbers in it are measured here rather than remembered."""
        yellow, blue = plan_palette.to_oklch("#FFFF00"), plan_palette.to_oklch("#0000FF")
        measured = {
            "0.968": round(yellow["L"], 3),
            "0.452": round(blue["L"], 3),
            "1.07": plan_palette.contrast_ratio("#FFFF00", "#FFFFFF"),
            "8.59": plan_palette.contrast_ratio("#0000FF", "#FFFFFF"),
        }
        source = (SKILL_ROOT / "scripts" / "plan_palette.py").read_text(encoding="utf-8")
        for quoted, value in measured.items():
            self.assertEqual(float(quoted), value, f"the docstring says {quoted}")
            self.assertIn(quoted, source, f"{quoted} is no longer in the docstring")
        # Half the scale apart, and the brighter of the two cannot be seen on white at all.
        self.assertGreater(yellow["L"] - blue["L"], 0.5)
        self.assertLess(measured["1.07"], plan_palette.WCAG_LARGE)

    def test_a_neutrals_hue_angle_is_not_a_property_of_the_colour(self) -> None:
        """The premise of the chroma floor. #F2F2F0 has a hue angle of 106 degrees, and that number
        is what is left of a rounding error rather than a description of the colour."""
        at_zero = self.swing[0.0]
        self.assertGreater(
            at_zero["median"], plan_palette.SAME_HUE_DEGREES,
            "if a neutral's hue angle were stable, the same-hue window would be a meaningful "
            "question to ask about it, and the chroma floor would be an excuse rather than a fix",
        )
        # The off-white that started this: below the floor, and therefore not asked the question.
        off_white = plan_palette.to_oklch(plan_palette.load_palette_row("charcoal-lime")["ink"])
        self.assertLess(off_white["C"], plan_palette.HUE_NEEDS_CHROMA)

    def test_the_chroma_floor_is_where_quantisation_stops_deciding_the_answer(self) -> None:
        """The derivation, not the number. Two colours can each wobble by the p90 amount in
        opposite directions, so 2 x p90 has to stay well inside the 30-degree window — under a
        quarter of it. The floor is the lowest bucket where that holds, and the test checks the
        bucket below it does not, because otherwise any larger number would pass this too."""
        window = plan_palette.SAME_HUE_DEGREES
        floor = round(plan_palette.HUE_NEEDS_CHROMA, 2)
        self.assertIn(floor, self.swing, "the floor is not on the 0.01 bucket grid measured here")
        at_floor = 2 * self.swing[floor]["p90"]
        below = 2 * self.swing[round(floor - 0.01, 2)]["p90"]
        self.assertLess(
            at_floor, window / 4,
            f"at chroma {floor} two colours can differ by {at_floor:.1f} degrees on quantisation "
            f"alone, which is too much of a {window}-degree window",
        )
        self.assertGreater(
            below, window / 4,
            f"chroma {floor - 0.01:.2f} also holds quantisation inside a quarter of the window, so "
            f"{floor} is higher than the measurement requires and excludes colours needlessly",
        )
        # Monotone, or the buckets are measuring something other than what they claim.
        ordered = [self.swing[b]["p90"] for b in sorted(self.swing) if b > 0]
        self.assertEqual(ordered, sorted(ordered, reverse=True))

    def test_the_derivation_table_in_the_source_is_the_one_the_sweep_produces(self) -> None:
        """plan_palette.py prints the median and p90 by chroma in a comment. A comment nothing
        checks is where a measured threshold quietly becomes a remembered one."""
        source = (SKILL_ROOT / "scripts" / "plan_palette.py").read_text(encoding="utf-8")
        quoted = {}
        for line in source.splitlines():
            words = line.split()
            for key in ("med", "p90"):
                if words[:2] == ["#", key]:
                    quoted[key] = [float(word) for word in words[2:] if word != "degrees"]
        self.assertEqual(sorted(quoted), ["med", "p90"], "the derivation table is gone from the source")
        buckets = [round(0.01 * i, 2) for i in range(6)]
        for key, statistic in (("med", "median"), ("p90", "p90")):
            self.assertEqual(len(quoted[key]), len(buckets), f"the {key} row has the wrong width")
            for bucket, claimed in zip(buckets, quoted[key]):
                with self.subTest(row=key, chroma=bucket):
                    self.assertAlmostEqual(
                        self.swing[bucket][statistic], claimed, places=1,
                        msg=f"the comment says {key} {claimed} at chroma {bucket}; the sweep "
                            f"measures {self.swing[bucket][statistic]:.2f}",
                    )

    def test_the_table_names_exactly_the_gates_the_code_has(self) -> None:
        tabled = {row["gate"] for row in DataTableTests.rows("colour-gates.csv")}
        emitted = {g["gate"] for g in
                   plan_palette.check_palette(plan_palette.load_palette_row("paper-cobalt"))
                   ["acceptance_gates"]}
        # The ramp gate is real but lives on `--ramp` rather than on a palette, so it is the one
        # row with no counterpart in check_palette's output.
        self.assertEqual(tabled, emitted | {"ramp-step-evenness"})

    def test_the_evidence_grade_is_the_same_in_the_table_and_in_the_code(self) -> None:
        """A house rule presented as a standard is the failure this whole column exists to stop.
        Both places have to say the same word or the reader is being told two different things
        about how much the number is worth."""
        graded = {row["gate"]: row["evidence_grade"]
                  for row in DataTableTests.rows("colour-gates.csv")}
        allowed = {"standard-requirement", "standard-requirement-with-house-threshold", "house-rule"}
        self.assertTrue(set(graded.values()) <= allowed, f"unknown grade in {set(graded.values())}")
        payload = plan_palette.check_palette(plan_palette.load_palette_row("paper-cobalt"))
        for gate in payload["acceptance_gates"]:
            with self.subTest(gate=gate["gate"]):
                self.assertEqual(gate["evidence_grade"], graded[gate["gate"]])

    def test_every_threshold_in_the_table_is_the_live_constant(self) -> None:
        """The generator imports these rather than retyping them, so this catches a hand-edit to
        the CSV and a constant changed without the table following."""
        rows = {row["gate"]: row for row in DataTableTests.rows("colour-gates.csv")}
        self.assertEqual(set(rows), set(self.QUOTES))
        for gate, constants in self.QUOTES.items():
            text = " ".join(rows[gate].values())
            for constant in constants:
                value = getattr(plan_palette, constant)
                # Percent is how the table spells the two fractions a reader thinks of as percents.
                spellings = {str(value), f"{value:g}"}
                if isinstance(value, float) and value < 1:
                    spellings.add(f"{int(round(value * 100))} percent")
                with self.subTest(gate=gate, constant=constant):
                    self.assertTrue(
                        any(spelling in text for spelling in spellings),
                        f"{gate} quotes none of {sorted(spellings)} for {constant}",
                    )

    def test_one_colour_in_two_roles_is_named_and_not_failed(self) -> None:
        """Zero lightness difference and zero hue gap is what a colour scores against itself, and
        every separation gate fires on it. Two shipped palettes do this deliberately. Reporting
        them as broken is how a checker teaches its reader to stop reading it."""
        for palette_id in ("black-white", "kraft-black"):
            with self.subTest(palette=palette_id):
                payload = plan_palette.check_palette(plan_palette.load_palette_row(palette_id))
                self.assertEqual(payload["same_colour_in_two_roles"], ["ink / accent"])
                self.assertEqual(payload["failing_gates"], [])
                doubled = next(p for p in payload["pairs"] if p["same_colour_in_two_roles"])
                self.assertTrue(doubled["passes"])
                self.assertEqual(doubled["findings"], [])
                # Silence would be wrong too: a palette whose accent equals its ink has no accent.
                self.assertTrue(doubled["notes"])

    def test_a_near_neutral_is_never_called_the_same_hue_as_a_saturated_colour(self) -> None:
        """charcoal-lime's off-white ink sits 18 degrees from its lime accent by hue angle and
        0.03 from it in lightness, which is inside both windows. Without the chroma floor the
        checker announced that an off-white and a lime are one colour printed unevenly."""
        colours = plan_palette.load_palette_row("charcoal-lime")
        pair = plan_palette.check_pair("ink", colours["ink"], "accent", colours["accent"])
        self.assertLessEqual(pair["hue_gap_degrees"], plan_palette.SAME_HUE_DEGREES)
        self.assertLess(pair["delta_lightness"], plan_palette.LIGHTNESS_SEPARATION)
        self.assertEqual(
            [f for f in pair["findings"] if "read as one colour" in f], [],
            "the same-hue finding fired on a colour with no hue",
        )
        payload = plan_palette.check_palette(colours)
        self.assertEqual(self.gate(payload, "same-hue-lightness-separation")["status"], "passed")

    def test_the_separation_band_is_reviewed_and_only_the_floor_fails(self) -> None:
        """0.12 is ours and 0.10 is an independent derivation of the same rule, so the span between
        them is the range over which nobody knows. A pair landing inside it is returned, not judged;
        a pair below both is judged. plum-butter is the case that forced this: it missed 0.12 by
        0.0004."""
        near, _ = plan_palette.from_oklch(0.50, 0.10, 250.0)
        inside, _ = plan_palette.from_oklch(0.61, 0.10, 250.0)
        under, _ = plan_palette.from_oklch(0.55, 0.10, 250.0)
        for other, expected in ((inside, "review"), (under, "failed")):
            with self.subTest(expected=expected):
                payload = plan_palette.check_palette({"one": near, "two": other})
                gate = self.gate(payload, "same-hue-lightness-separation")
                self.assertEqual(gate["status"], expected)
                self.assertIn("decide" if expected == "review" else "one colour",
                              gate["why_this_status"])
        shipped = plan_palette.check_palette(plan_palette.load_palette_row("plum-butter"))
        self.assertEqual(self.gate(shipped, "same-hue-lightness-separation")["status"], "review")
        self.assertEqual(shipped["failing_gates"], [])

    def test_a_colour_vision_collapse_is_reviewed_until_the_caller_declares_the_use(self) -> None:
        """SC 1.4.1 is broken by a use where colour alone carries meaning, and the layout is
        invisible from here. So the collapse is reported with its arithmetic, and declaring the
        pair turns the same finding into a failure."""
        colours = plan_palette.load_palette_row("charcoal-lime")
        undeclared = plan_palette.check_palette(colours)
        self.assertEqual(self.gate(undeclared, "colour-is-not-the-only-cue")["status"], "review")
        self.assertEqual(undeclared["failing_gates"], [])
        declared = plan_palette.check_palette(colours, None, [("accent", "ink")])
        gate = self.gate(declared, "colour-is-not-the-only-cue")
        self.assertEqual(gate["status"], "failed", "declaring the use changed nothing")
        self.assertIn("colour alone cannot carry it", gate["why_this_status"])
        # Order-insensitive, because "accent+ink" and "ink+accent" are the same declaration.
        self.assertEqual(declared["pairs_carrying_meaning"], ["accent / ink", "ink / accent"])

    def test_an_unmeasured_layout_is_skipped_and_never_passed(self) -> None:
        """The count budget cannot tell a 20px accent from a full-bleed panel at the same chroma.
        Surface share closes that hole, and only when somebody measured the layout: a share nobody
        measured is an invented input."""
        colours = plan_palette.load_palette_row("charcoal-lime")
        without = plan_palette.check_palette(colours)
        gate = self.gate(without, "chroma-budget-by-surface-share")
        self.assertEqual(gate["status"], "skipped")
        self.assertIn("chroma-budget-by-surface-share", without["skipped_gates"])
        self.assertEqual(without["failing_gates"], [])
        over = plan_palette.check_palette(
            colours, {"bg": 0.3, "ink": 0.1, "accent": 0.5, "support": 0.1})
        self.assertEqual(
            self.gate(over, "chroma-budget-by-surface-share")["status"], "failed",
            "an accent covering half the layout is the accent becoming the background",
        )
        # The count budget is untouched by either: one loud colour is still one loud colour.
        self.assertEqual(without["chroma_budget"]["count"]["status"], "passed")
        self.assertEqual(over["chroma_budget"]["count"]["status"], "passed")
        with self.assertRaises(ValueError):
            plan_palette.check_chroma_budget(colours, {"nonexistent": 0.5})

    def test_the_exit_code_separates_a_breach_from_a_decision_from_a_gap(self) -> None:
        """2 is a failed gate, 3 is sound-but-needs-a-human, and a skipped gate is neither. If a
        skipped gate exited non-zero, callers would invent shares to get a clean run, which is the
        one outcome this script exists to prevent."""
        cases = (
            (["--palette-id", "paper-cobalt"], 0),
            (["--palette-id", "charcoal-lime"], 3),
            (["--palette-id", "charcoal-lime", "--carries-meaning", "ink+accent"], 2),
            (["--palette-id", "charcoal-lime", "--share", "bg=0.3", "ink=0.1",
              "accent=0.5", "support=0.1"], 2),
            (["--seed", "#E8B004", "--ramp", "12"], 2),
        )
        for arguments, expected in cases:
            with self.subTest(arguments=arguments):
                with tempfile.TemporaryDirectory() as folder:
                    out = Path(folder) / "payload.json"
                    argv = ["plan_palette.py", *arguments, "--output", str(out)]
                    with mock.patch.object(plan_palette.sys, "argv", argv):
                        buffer = io.StringIO()
                        with contextlib.redirect_stdout(buffer):
                            code = plan_palette.main()
                    self.assertEqual(code, expected)
                    json.loads(out.read_text(encoding="utf-8"))
        # The two flags describe a palette, so they are refused where there is no palette to
        # describe rather than silently ignored.
        argv = ["plan_palette.py", "--seed", "#2A4BD7", "--scheme", "triadic", "--share", "bg=0.5"]
        with mock.patch.object(plan_palette.sys, "argv", argv):
            buffer = io.StringIO()
            with contextlib.redirect_stderr(buffer):
                self.assertEqual(plan_palette.main(), 1)
        self.assertIn("only apply to", buffer.getvalue())
        for bad in ("bg", "bg=half", "bg=1.4"):
            argv = ["plan_palette.py", "--palette-id", "paper-cobalt", "--share", bad]
            with mock.patch.object(plan_palette.sys, "argv", argv):
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(plan_palette.main(), 1, f"{bad!r} was accepted as a share")

    def test_relaxing_the_chords_beats_spacing_the_lightness_on_every_seed(self) -> None:
        """Equal arc length along the path is not equal chord distance between neighbours, and the
        chord is what the eye compares. The path curves hardest at the dark end where chroma
        collapses, which is exactly where the equal-arc ramps measured short."""
        def spaced_by_lightness(seed: str, steps: int) -> list[dict]:
            base = plan_palette.to_oklch(seed)
            out = []
            for index in range(steps):
                lightness, chroma = plan_palette._ramp_path(
                    base["C"], base["h"], index / (steps - 1))
                hex_value, _ = plan_palette.from_oklch(lightness, chroma, base["h"])
                out.append({"hex": hex_value})
            return out

        worst_spaced = worst_relaxed = 0.0
        for seed in self.RAMP_SEEDS:
            spaced = plan_palette.check_ramp_evenness(spaced_by_lightness(seed, 9))
            relaxed = plan_palette.check_ramp_evenness(plan_palette.build_ramp(seed, 9))
            with self.subTest(seed=seed):
                self.assertLess(
                    relaxed["worst_deviation"], spaced["worst_deviation"],
                    f"{seed}: relaxing the chords made this seed worse, not better",
                )
                self.assertEqual(relaxed["status"], "passed")
            worst_spaced = max(worst_spaced, spaced["worst_deviation"])
            worst_relaxed = max(worst_relaxed, relaxed["worst_deviation"])
        # The two numbers build_ramp's docstring quotes. Rounded to one decimal in percent, which
        # is how they are written there.
        self.assertEqual(round(worst_spaced * 100, 1), 35.1)
        self.assertEqual(round(worst_relaxed * 100, 1), 5.5)
        source = (SKILL_ROOT / "scripts" / "plan_palette.py").read_text(encoding="utf-8")
        self.assertIn("from up to 35.1 percent", source)
        self.assertIn("to 5.5 percent", source)

    def test_a_ramp_the_path_cannot_hold_fails_rather_than_looking_even(self) -> None:
        """Twelve steps is more than some hues have room for once chroma collapses at the ends.
        The gate says so, which is more use than a ramp that is even in its coordinates and has two
        indistinguishable swatches at the dark end."""
        failures = {seed: plan_palette.check_ramp_evenness(plan_palette.build_ramp(seed, 12))
                    for seed in self.RAMP_SEEDS}
        failed = {seed: result for seed, result in failures.items() if result["status"] == "failed"}
        self.assertTrue(failed, "twelve steps now passes on every seed; the tolerance has moved")
        worst = max(result["worst_deviation"] for result in failures.values())
        self.assertEqual(round(worst * 100, 1), 17.9)
        self.assertIn("the worst case is 17.9 percent",
                      (SKILL_ROOT / "scripts" / "plan_palette.py").read_text(encoding="utf-8"))

    def test_every_shipped_palette_clears_every_gate(self) -> None:
        """The table is the skill's own recommendation, so a failing row is a recommendation to
        break a rule the same file states. Reviews are allowed and counted: they are decisions the
        arithmetic should not make, and six of the twenty carry one."""
        reviewed = []
        for row in DataTableTests.rows("palettes.csv"):
            payload = plan_palette.check_palette(plan_palette.load_palette_row(row["id"]))
            with self.subTest(palette=row["id"]):
                self.assertEqual(
                    payload["failing_gates"], [],
                    f'{row["id"]}: {payload["verdict"]}',
                )
            if payload["gates_for_review"]:
                reviewed.append(row["id"])
        self.assertEqual(len(reviewed), 6, f"reviews moved: {reviewed}")

    def test_the_reference_teaches_the_gates_the_code_actually_runs(self) -> None:
        """A reference is read far more often than a CSV, so prose that has drifted from the code is
        the version people will act on. It has drifted twice already in this file's history. So every
        gate the checker emits has to be named in the reference, every verdict has to be explained,
        and the three evidence grades have to be distinguishable without opening the table."""
        prose = (SKILL_ROOT / "references" / "colour-combination.md").read_text(encoding="utf-8")
        for gate in sorted(self.QUOTES):
            self.assertIn(gate, prose, f"{gate} runs but the reference never names it")
        for verdict in ("passed", "failed", "skipped", "review"):
            self.assertIn(verdict, prose, f"the reference does not explain the {verdict} verdict")
        for grade in {row["evidence_grade"] for row in DataTableTests.rows("colour-gates.csv")}:
            self.assertIn(grade, prose, f"the reference does not distinguish {grade}")

    def test_the_reference_refuses_both_statistics_by_name(self) -> None:
        """`data/command-artifacts.csv` says the colour command refuses the 85-percent and 80-percent
        colour statistics. A refusal held in a table nobody reads is not a refusal, and the second
        one only survives as a refusal if the reference says the search came back empty rather than
        that the source is hard to get."""
        prose = (SKILL_ROOT / "references" / "colour-combination.md").read_text(encoding="utf-8")
        self.assertIn("85 percent", prose)
        self.assertIn("80 percent", prose)
        self.assertIn("62 to 90 percent", prose, "the honest band is missing")
        self.assertIn("no-source-found", prose, "the verified negative is not named as one")
        ids = {row["benchmark_id"] for row in DataTableTests.rows("marketing-benchmarks.csv")}
        for wanted in ("colour-62-90-assessment", "colour-recognition-80-percent",
                       "colour-brand-personality", "colour-product-congruity"):
            self.assertIn(wanted, ids, f"{wanted} left the benchmark table")
            self.assertIn(wanted, prose, f"{wanted} is in the table but not cited in the reference")


class ReferenceSetCalibrationTests(unittest.TestCase):
    """A calibration is only worth the honesty of its verdict column.

    `data/reference-set-calibration.csv` grades eleven axes of this skill's own craft prose against
    244 measured photographs, and the failure mode is not a wrong number - it is a table that agrees
    with itself. A row saying `confirmed` next to a claim the sample never actually tested reads
    exactly like a row saying `confirmed` next to one it did, and the reader cannot tell them apart.
    So the tests below defend the two things that keep the verdicts readable: a graded row has to
    name a claim that really exists where it says it does, and a `confirmed` has to be earned.

    The other thing they defend is the absence of the images. The set was 244 files on this machine
    and none of them are in the repository, which is the same rule that emptied `docs/` of seventeen
    photographs. A calibration is the honest way to keep what those files taught; a folder of them is
    not.
    """

    TABLE = "reference-set-calibration.csv"
    REFERENCE = "reference-set-calibration.md"
    SAMPLE = 244

    # A verdict has to mean one of four things, and the middle two are the ones worth having. Without
    # `consistent-but-untested` the only way to record "nothing broke it, but nothing tried" is to
    # call it confirmed, and that is the overclaim this column exists to stop.
    VERDICTS = {"confirmed", "refined", "consistent-but-untested", "baseline"}

    # The axes that grade a rule the skill actually asserts. Everything else is a baseline, and a
    # baseline is allowed to have no claim - but it is not allowed to be graded as though it had one.
    # Listed here rather than derived from the table, because the split between "we had a rule and
    # measured it" and "we had nothing" is the finding, and a derived set would agree with any edit.
    GRADED = {"loud-surface-share", "loud-colour-count", "frame-ratio-share",
              "ratio-by-account-register", "hue-family-count", "neutral-share"}

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = {row["axis_id"]: row for row in DataTableTests.rows(cls.TABLE)}
        cls.prose = (SKILL_ROOT / "references" / cls.REFERENCE).read_text(encoding="utf-8")

    def test_every_verdict_is_one_of_the_four(self) -> None:
        for axis, row in self.rows.items():
            with self.subTest(axis=axis):
                self.assertIn(row["verdict"], self.VERDICTS)

    def test_a_graded_row_names_a_claim_and_a_baseline_admits_it_has_none(self) -> None:
        """The pairing is what makes the table checkable. A row that grades a claim has to say where
        the claim lives, in a file that exists; a row that grades nothing has to say so in the same
        two columns rather than leaving a plausible-looking citation behind."""
        self.assertEqual({axis for axis, row in self.rows.items() if row["verdict"] != "baseline"},
                         self.GRADED, "an axis changed sides between grading a rule and having none")
        for axis, row in self.rows.items():
            with self.subTest(axis=axis):
                if row["verdict"] == "baseline":
                    self.assertRegex(row["claim_it_grades"], r"^None\b",
                                     "a baseline row is claiming to grade something")
                    self.assertRegex(row["where_that_claim_lives"], r"^Nowhere\b",
                                     "a baseline row cites a home for a claim it says does not exist")
                else:
                    self.assertNotRegex(row["claim_it_grades"], r"^None\b")
                    self.assertNotRegex(row["where_that_claim_lives"], r"^Nowhere\b")

    def test_every_cited_file_exists(self) -> None:
        """A citation to a file or column that has been renamed is worse than no citation, because it
        looks checked. This is the test that catches the calibration going stale when a table moves."""
        for axis, row in self.rows.items():
            cited = re.findall(r"\b(?:data|scripts|references)/[\w./-]+\b",
                               row["where_that_claim_lives"] + " " + row["what_changes"])
            for target in cited:
                with self.subTest(axis=axis, target=target):
                    self.assertTrue((SKILL_ROOT / target).exists(), f"{axis} cites a missing {target}")

    def test_a_graded_claim_is_quoted_from_the_file_it_names(self) -> None:
        """The strongest check available without the images: a graded row's claim has to be findable
        in the file the row says holds it. This is what stops a calibration from grading a rule
        somebody remembered."""
        checkable = {
            "loud-surface-share": ("colour-gates.csv", "20 percent of the visible area"),
            "loud-colour-count": ("colour-gates.csv", "at most 1 colour at or above C 0.19"),
            "frame-ratio-share": ("frame-ratios.csv", "legacy IG feed"),
            "hue-family-count": ("reference-observations.csv", "Two hues plus skin"),
            "neutral-share": ("reference-observations.csv", "without competing"),
        }
        for axis, (table, quoted) in checkable.items():
            with self.subTest(axis=axis):
                self.assertIn(table, self.rows[axis]["where_that_claim_lives"])
                text = (SKILL_ROOT / "data" / table).read_text(encoding="utf-8")
                self.assertIn(quoted, text, f"{axis} grades a claim {table} does not make")

    def test_the_two_chroma_gates_are_graded_and_say_so_in_their_own_table(self) -> None:
        """The calibration is useless if a reader of `colour-gates.csv` never learns it happened. Both
        chroma gates now cite it, and neither was promoted off it: the count gate keeps house-rule
        because the sample never reaches its limit, and the share gate keeps 20 percent because a
        brand panel is not a photograph."""
        gates = {row["gate"]: row for row in DataTableTests.rows("colour-gates.csv")}
        for gate in ("chroma-budget-by-count", "chroma-budget-by-surface-share"):
            with self.subTest(gate=gate):
                self.assertEqual(gates[gate]["evidence_grade"], "house-rule",
                                 "a house rule was promoted on a photograph sample")
                self.assertIn(self.REFERENCE, " ".join(gates[gate].values()),
                              f"{gate} was measured and its row does not say where")

    def test_the_untestable_gate_is_not_recorded_as_confirmed(self) -> None:
        """This is the one overclaim the whole exercise was set up to avoid. No frame in 244 carries
        two loud hue families, which looks like confirmation until you notice almost none of them
        reach the threshold at all. The row has to say that in the cell, not just in the verdict."""
        row = self.rows["loud-colour-count"]
        self.assertEqual(row["verdict"], "consistent-but-untested")
        self.assertRegex(row["what_changes"], r"(?i)cannot confirm|never approached|rarely")
        self.assertIn("house-rule", row["what_changes"])

    def test_every_row_states_a_sample_size_or_a_percentile(self) -> None:
        """A measured cell with no number in it is a sentence about a feeling. Each row has to carry
        arithmetic in `measured` and a spread in `distribution`, because a median with no distribution
        behind it is the statistic that made "two hues plus skin" look like a rule."""
        for axis, row in self.rows.items():
            with self.subTest(axis=axis):
                self.assertRegex(row["measured"], r"\d", "measured carries no number")
                self.assertRegex(row["distribution"], r"\d", "distribution carries no number")
                self.assertGreater(len(row["how_it_was_measured"]), 40,
                                   "the method is too short to be repeatable")

    def test_every_row_names_a_blind_spot_that_is_not_a_shrug(self) -> None:
        for axis, row in self.rows.items():
            with self.subTest(axis=axis):
                self.assertGreater(len(row["what_this_cannot_tell_you"]), 40,
                                   "the blind spot is too short to be one")
                self.assertNotRegex(row["what_this_cannot_tell_you"], r"(?i)^(nothing|n/a|none)\b")

    def test_the_reference_carries_every_axis_and_the_sample_size(self) -> None:
        """Same rule the colour unit is held to: prose is read more often than a CSV, so a reference
        that names ten of eleven axes is teaching a calibration that does not exist."""
        for axis in self.rows:
            self.assertIn(axis, self.prose, f"{axis} is measured and the reference never names it")
        for verdict in sorted(self.VERDICTS):
            self.assertIn(verdict, self.prose, f"the reference does not explain a {verdict} verdict")
        self.assertIn(str(self.SAMPLE), self.prose, "the reference does not state its sample size")

    def test_the_reference_states_the_sample_bias_before_the_findings(self) -> None:
        """A one-industry, one-platform, one-day portrait set produced every number in the table. A
        reader who reaches the findings before the limits will carry them somewhere they do not hold,
        so the order of the sections is part of the content."""
        limits = self.prose.index("The sample, and what it is not")
        findings = self.prose.index("that changed something")
        self.assertLess(limits, findings, "the findings are stated before the sample's limits")
        for admission in ("one platform", "portrait set", "posted frames"):
            self.assertIn(admission, self.prose, f"the sample section does not admit {admission!r}")

    def test_the_calibration_stored_none_of_the_photographs(self) -> None:
        """244 files were read on one machine and none of them are here. The images stay out because
        their own manifest says copyright remains with the original owners, which is the sentence
        that emptied docs/ of seventeen photographs, and the instrument stays out because it needs
        Pillow while all the shipped tools need nothing. The reference has to say both, because an
        absence nobody explained reads as an omission."""
        images = [path.name for path in SKILL_ROOT.rglob("*")
                  if path.suffix.lower() in {".jpg", ".jpeg", ".webp", ".avif"}]
        self.assertEqual(images, [], f"a photograph from the measured set landed here: {images}")
        for reason in ("Pillow", "standard library", "not ours to publish"):
            self.assertIn(reason, self.prose, f"the reference does not explain {reason!r}")
        # This file is excluded because it is a harness rather than a tool a customer runs, and
        # because the two assertions below are themselves the string they are looking for.
        shipped = "\n".join(path.read_text(encoding="utf-8")
                            for path in sorted((SKILL_ROOT / "scripts").glob("*.py"))
                            if path.stem != "test_tools")
        self.assertNotIn("from PIL", shipped, "a shipped tool now needs Pillow")
        self.assertNotIn("import PIL", shipped, "a shipped tool now needs Pillow")

    def test_the_router_sends_a_reader_here_before_they_quote_the_old_rule(self) -> None:
        router = (SKILL_ROOT / "references" / "marketing-system-router.md").read_text(encoding="utf-8")
        self.assertIn(self.REFERENCE, router)
        self.assertIn(self.TABLE, router)
        self.assertIn("two hues plus skin", router.lower(),
                      "the router does not warn the reader off the rule this refined")


class OperatingLoadTests(unittest.TestCase):
    """The Vietnam unit makes one structural claim and then does arithmetic on top of it.

    The claim - that one marketing hire holds thirteen roles - cannot be tested here, and the
    reference says so plainly: it is falsifiable in one conversation and no survey is cited for it.
    What can be tested is everything built on top, and the reason to bother is that the arithmetic
    is the part that will be quoted. Somebody will repeat "seventeen command-runs a week" in a
    hiring conversation, so it has to be re-derived rather than remembered.

    Three of these tests exist because the first version of the script failed them. It counted the
    once-only strategy role twice and reported thirteen setup commands for a seven-command job; it
    printed the upstream chain in alphabetical order while formatting it with arrows, as though it
    were runnable; and asked for the two roles that produce no artefact, it reported a clean pass
    with a verdict claiming the strategy already existed. The last one is the unit's own thesis
    failing in its own output.
    """

    REFERENCE = "vietnam-operating-reality.md"

    @classmethod
    def setUpClass(cls) -> None:
        cls.load = plan_operating_load.OperatingLoad(
            plan_operating_load.load_roles(), plan_command_chain.Surface.load())
        cls.roles = cls.load.roles
        cls.prose = (SKILL_ROOT / "references" / cls.REFERENCE).read_text(encoding="utf-8")
        # Every phrase check below runs against this. Whether a sentence happens to wrap at column
        # 100 is not a fact about the reference, and a test that breaks on reflowing a paragraph
        # teaches people to stop editing the paragraph.
        cls.flat = " ".join(cls.prose.split())

    def report(self, *argv: str) -> tuple[dict, int]:
        """Run the CLI the way a caller does, so the exit code is tested rather than assumed."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = plan_operating_load.main([*argv, "--format", "json"])
        return json.loads(buffer.getvalue()), code

    def test_every_role_names_only_commands_that_exist(self) -> None:
        """The table's whole value is that it joins to the command surface. A role invoking a
        command that was later renamed would make the load arithmetic quietly wrong rather than
        loudly broken."""
        for row in self.roles:
            for command in plan_command_chain.split_list(row["commands"]):
                with self.subTest(role=row["role_id"], command=command):
                    self.assertIn(command, self.load.surface.by_command)

    def test_each_role_output_is_produced_by_one_of_its_own_commands(self) -> None:
        """`artifact_per_cycle` is what the upstream calculation subtracts against, so an invented
        artefact name makes the setup figure meaningless. Three were invented on the first pass -
        placement-set, print-master and launch-package - and all three looked entirely plausible."""
        for row in self.roles:
            commands = plan_command_chain.split_list(row["commands"])
            if not commands:
                continue
            produced = {self.load.surface.by_command[c]["produces"] for c in commands}
            with self.subTest(role=row["role_id"]):
                self.assertIn(row["artifact_per_cycle"], produced)

    def test_the_roles_and_the_surface_describe_the_same_work(self) -> None:
        """A command no role performs is a command nobody will ever run, and a role the surface
        cannot express is work the skill will plan around without noticing. The reference quotes
        this coverage as 28 of 28, so it is measured here rather than asserted there."""
        covered = {c for row in self.roles for c in plan_command_chain.split_list(row["commands"])}
        self.assertEqual(covered, set(self.load.surface.by_command),
                         "the roles table and the command surface have drifted apart")
        self.assertIn("28 of 28", self.flat)

    def test_the_two_roles_with_no_command_are_the_two_that_produce_nothing(self) -> None:
        """This is the finding, so it is the thing most likely to be tidied away by somebody
        filling in a blank cell to make a table look complete."""
        empty = [row["role_id"] for row in self.roles if not row["commands"]]
        self.assertEqual(sorted(empty), ["community", "sales"])
        for row in self.roles:
            starts_with_none = row["artifact_per_cycle"].startswith("none")
            with self.subTest(role=row["role_id"]):
                self.assertEqual(starts_with_none, not row["commands"],
                                 "a role either produces an artefact or explains why it does not")
        for role_id in empty:
            self.assertIn(role_id, self.flat, f"{role_id} is not discussed in the reference")

    def test_no_hour_or_salary_figure_is_smuggled_into_the_unit(self) -> None:
        """The refusal to convert work items into hours is the load-bearing honesty of this unit.
        It is also the easiest thing to undo later, because an hour figure is what people ask for
        and a plausible one is trivial to write. So the shape of that number is banned outright in
        the table, the script and the reference."""
        table = (SKILL_ROOT / "data" / "vn-marketer-roles.csv").read_text(encoding="utf-8")
        code = (SKILL_ROOT / "scripts" / "plan_operating_load.py").read_text(encoding="utf-8")
        # Matches "3 hours", "1.5 hrs", "8 hours a week", "20 man-days", "15m VND".
        smell = re.compile(r"\d+(\.\d+)?\s*(hours?|hrs?|man-days?|VND|USD|million)\b", re.I)
        for name, text in (("table", table), ("script", code), ("reference", self.flat)):
            with self.subTest(name):
                found = smell.search(text)
                self.assertIsNone(
                    found,
                    f"{name} states {found.group(0)!r} as a quantity" if found else "")
        for phrase in ("not an hour", "command-run is one distinct piece of work"):
            self.assertIn(phrase, self.flat, "the reference no longer states the refusal")

    def test_the_setup_figures_the_reference_quotes_are_the_ones_it_computes(self) -> None:
        """The asymmetry between asserting the platform and asserting the brief is the reference's
        central practical claim, and it is the kind of number that rots silently when a command is
        added upstream."""
        base, _ = self.report("--roles", "content", "design", "marketplace", "video", "report")
        platform, _ = self.report("--roles", "content", "design", "marketplace", "video", "report",
                                  "--have", "positioning-platform")
        brief, _ = self.report("--roles", "content", "design", "marketplace", "video", "report",
                               "--have", "creative-brief")
        self.assertEqual((base["setup_count"], base["weekly_command_runs"]), (10, 17.0))
        self.assertEqual(platform["setup_count"], 5)
        self.assertEqual(brief["setup_count"], 9)
        for quoted in ("from 10 commands to 5", "from 10 to 9",
                       "17 per week with 10 commands of setup"):
            self.assertIn(quoted, self.flat, f"the reference no longer says {quoted!r}")
        # The five commands the platform removes are `position` and everything upstream of it.
        removed = set(base["setup_runs_once"]) - set(platform["setup_runs_once"])
        self.assertEqual(len(removed), 5)
        self.assertIn("position", removed)

    def test_the_all_roles_figure_the_reference_quotes_reproduces(self) -> None:
        report, code = self.report("--cadence", "photo=0.25", "koc=0.25", "print=0.25",
                                   "event=0.25", "ads=1")
        self.assertEqual(report["weekly_command_runs"], 22.75)
        self.assertEqual(report["setup_count"], 7)
        self.assertIn("22.75 command-runs per week and 7 commands", self.flat)
        # Every cadence supplied and no capacity stated: the fit is skipped, never passed.
        self.assertEqual(report["capacity_check"]["status"], "skipped")
        self.assertEqual(code, 3)

    def test_the_once_only_role_is_not_listed_as_weekly_work_at_zero(self) -> None:
        """Reporting the strategy role at "0 runs/week" beside the roles that recur is the same
        category error the unit exists to correct, and it double-counted the setup total as well."""
        report, _ = self.report("--roles", "strategy", "content")
        self.assertEqual([row["role"] for row in report["setup_roles"]], ["strategy"])
        self.assertEqual([row["role"] for row in report["weekly"]], ["content"])
        # Seven commands for the strategy role plus `brief`, which nothing selected here performs.
        # The double-counting bug reported thirteen, by adding the strategy chain to itself.
        self.assertEqual(report["setup_runs_once"], ["brief"])
        self.assertEqual(report["setup_count"], 8)
        self.assertEqual(report["strategy"], "planned")

    def test_the_upstream_list_is_printed_in_an_order_that_could_actually_run(self) -> None:
        """It is formatted with arrows, so it reads as a sequence. Sorting it alphabetically and
        formatting it as a chain tells the reader to run `brainstorm -> investigate -> offer`, which
        is not a thing that can happen."""
        report, _ = self.report("--roles", "content", "design", "marketplace", "video", "report")
        chain = report["setup_runs_once"]
        self.assertNotEqual(chain, sorted(chain), "the upstream chain is in alphabetical order")
        available = set(plan_command_chain.ROOT_ARTIFACTS)
        for position, command in enumerate(chain):
            row = self.load.surface.by_command[command]
            for artifact in plan_command_chain.split_list(row["takes"]):
                producer = self.load.surface.producer.get(artifact)
                if producer in chain:
                    with self.subTest(command=command, artifact=artifact):
                        self.assertIn(artifact, available,
                                      f"{command} at position {position} needs {artifact} from "
                                      f"{producer}, which has not run yet")
            available.add(row["produces"])

    def test_selecting_only_the_uncountable_roles_does_not_come_back_clean(self) -> None:
        """Ask for the inbox and sales support alone and the honest answer is that nothing here is
        countable. The first version answered "passed, headroom 5, the strategy already exists",
        which is the unit's own thesis failing inside the unit's own output."""
        report, code = self.report("--roles", "community", "sales", "--capacity", "5")
        self.assertEqual(report["weekly"], [])
        self.assertEqual(report["capacity_check"]["status"], "skipped")
        self.assertEqual(code, 3)
        self.assertNotIn("already exists", report["verdict"])
        self.assertIn("no artefact", report["verdict"])

    def test_a_load_over_the_stated_capacity_fails_and_an_unstated_one_is_skipped(self) -> None:
        """Two failure modes, and only one of them is a failure. Exceeding a capacity the user
        stated is a finding. Having no capacity to compare against is not a pass."""
        over, code = self.report("--roles", "content", "design", "marketplace",
                                 "--have", "offer-architecture", "--capacity", "8")
        self.assertEqual(over["capacity_check"]["status"], "failed")
        self.assertEqual(over["capacity_check"]["headroom"], -4.0)
        self.assertEqual(code, 2)
        unstated, code = self.report("--roles", "content", "--have", "creative-brief")
        self.assertEqual(unstated["capacity_check"]["status"], "skipped")
        self.assertEqual(code, 3)
        self.assertIn("supply", unstated["capacity_check"])

    def test_a_clean_run_is_reachable_and_says_what_made_it_clean(self) -> None:
        """A checker that cannot return zero teaches people to ignore its exit code."""
        report, code = self.report("--roles", "content", "design", "report",
                                   "--have", "offer-architecture", "creative-brief",
                                   "campaign-record", "--capacity", "20")
        self.assertEqual(code, 0)
        self.assertEqual(report["capacity_check"]["status"], "passed")
        self.assertEqual(report["strategy"], "held")

    def test_a_cadence_nobody_stated_is_reported_as_unstated_rather_than_zero(self) -> None:
        """Five of the thirteen roles cannot be defaulted: four recur per campaign, and ads is
        continuous, which is not a count. Defaulting any of them to zero would understate the load
        of exactly the roles a busy person is most likely to forget."""
        report, code = self.report()
        missing = {row["role"] for row in report["cadence_not_supplied"]}
        self.assertEqual(missing, {"photo", "koc", "print", "event", "ads"})
        self.assertEqual(code, 3)
        for row in report["cadence_not_supplied"]:
            with self.subTest(row["role"]):
                self.assertTrue(row["supply"].startswith("--cadence "))
        for row in report["weekly"]:
            if row["role"] in missing:
                self.assertIsNone(row["weekly_runs"], "an unstated cadence became a number")
        self.assertIn("unstated, not as zero", self.flat)

    def test_bad_input_is_refused_rather_than_guessed(self) -> None:
        for argv in (["--roles", "seo"], ["--cadence", "photo"], ["--cadence", "photo=x"],
                     ["--cadence", "photo=-1"], ["--roles", "content", "--cadence", "photo=1"],
                     ["--have", "brand-vibes"]):
            with self.subTest(argv=argv):
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(plan_operating_load.main(argv), 1)

    def test_the_reference_teaches_the_four_verdicts_and_the_exit_codes(self) -> None:
        """The reference is read far more often than the script's docstring, and a verdict the
        reader cannot interpret is a verdict they will ignore."""
        for verdict in ("passed", "failed", "skipped", "review"):
            self.assertIn(f"`{verdict}`", self.flat,
                          f"the reference does not explain the {verdict} verdict")
        lowered = self.flat.lower()
        for fragment in ("0 clean", "1 usage", "2 the stated load exceeds the stated capacity",
                         "3 computable but unsettled"):
            self.assertIn(fragment, lowered, f"the reference no longer documents exit {fragment!r}")
        # `review` is the one a reader will dismiss as a soft pass, so the reference has to say why
        # it exists at all, in the same terms the colour unit uses.
        self.assertIn("A checker that returns a verdict on everything gets ignored on everything",
                      self.flat)

    def test_the_reference_is_reachable_and_says_it_cites_no_survey(self) -> None:
        """`command-surface.md` forward-cites this file by name, so it has to exist and it has to
        be reachable from the router. And because the central claim is structural rather than
        sourced, the reference has to say that in its own words rather than leave a reader to
        assume a survey behind it."""
        router = (SKILL_ROOT / "references" / "marketing-system-router.md").read_text(
            encoding="utf-8")
        self.assertIn(self.REFERENCE, router, "the unit is not reachable from the router")
        surface = (SKILL_ROOT / "references" / "command-surface.md").read_text(encoding="utf-8")
        self.assertIn(self.REFERENCE, surface)
        self.assertIn("Nothing in this unit is a survey finding", self.flat)
        for row in DataTableTests.rows("marketing-benchmarks.csv"):
            with self.subTest(row["benchmark_id"]):
                self.assertNotIn("vn-marketer-roles", row["url"],
                                 "a structural model is being cited as a fetched source")


class TestReadoutTests(unittest.TestCase):
    """The statistics have to be checked against something outside this file.

    A hand-rolled significance check is the easiest thing in a marketing toolkit to get quietly wrong,
    because a wrong answer still looks like an answer and nobody re-derives it. The first draft of
    check_test_readout.py's own self-check asserted a sample size "a little over 6000" from memory and
    the correct answer was 8155 - the exact recalled-number failure this skill gates other people for.
    So the tests here go after properties and independent routes, never remembered outputs.
    """

    def test_self_check_passes(self) -> None:
        report = check_test_readout.self_check()
        self.assertTrue(report.rstrip().endswith("verdict passed"), report)
        self.assertNotIn("FAIL", report)

    def test_sample_size_delivers_the_power_it_was_asked_for(self) -> None:
        # The independent route: invert for n, then run the power function forward on that n. A
        # dropped variance term or a one-tailed critical value fails this even though both produce a
        # plausible-looking number.
        for baseline, mde, power in ((0.01, 0.25, 0.80), (0.05, 0.20, 0.80), (0.30, 0.05, 0.90)):
            with self.subTest(baseline=baseline, mde=mde):
                n = check_test_readout.required_per_arm(baseline, mde, 0.05, power)
                treated = baseline * (1 + mde)
                se = math.sqrt(baseline * (1 - baseline) / n + treated * (1 - treated) / n)
                achieved = check_test_readout.normal_cdf(
                    (treated - baseline) / se - check_test_readout.normal_quantile(0.975))
                self.assertAlmostEqual(achieved, power, delta=0.005)

    def test_a_big_relative_lift_on_thin_traffic_is_refused(self) -> None:
        # 8/400 against 13/410 is a 58 percent relative lift, which is the number that would get
        # reported, and p is about 0.29. If this ever passes, the gate has stopped working.
        report = check_test_readout.read(
            [("A", 400, 8), ("B", 410, 13)], mde=0.20, alpha=0.05, power=0.80,
            daily_clicks=None, claim="B")
        self.assertEqual(report["verdict"]["status"], "failed")
        self.assertGreater(report["statistics"]["relative_lift"], 0.5)
        self.assertTrue(report["statistics"]["interval_crosses_zero"])
        claim_gate = [g for g in report["gates"] if g["gate"] == "claimed-winner"][0]
        self.assertEqual(claim_gate["status"], "failed")

    def test_a_claim_is_checked_against_the_interval_not_the_point_estimate(self) -> None:
        # Same leader, enough traffic to separate the arms. The point estimate has not changed
        # direction between this case and the one above; only the interval has.
        report = check_test_readout.read(
            [("A", 20000, 600), ("B", 20000, 900)], mde=0.20, alpha=0.05, power=0.80,
            daily_clicks=None, claim="B")
        self.assertEqual(report["verdict"]["status"], "passed")
        self.assertFalse(report["statistics"]["interval_crosses_zero"])
        # And claiming the arm that lost fails even though the test itself is readable.
        wrong = check_test_readout.read(
            [("A", 20000, 600), ("B", 20000, 900)], mde=0.20, alpha=0.05, power=0.80,
            daily_clicks=None, claim="A")
        self.assertEqual(wrong["verdict"]["status"], "failed")

    def test_unequal_delivery_is_graded_as_a_confound(self) -> None:
        report = check_test_readout.read(
            [("A", 20000, 600), ("B", 8000, 360)], mde=0.20, alpha=0.05, power=0.80,
            daily_clicks=None, claim=None)
        gate = [g for g in report["gates"] if g["gate"] == "delivery-balance"][0]
        self.assertEqual(gate["status"], "failed")
        self.assertEqual(report["verdict"]["status"], "review")
        self.assertTrue(any("confounded" in note for note in report["notes"]))

    def test_significant_below_the_planned_size_is_not_a_win(self) -> None:
        # The dangerous combination, and the reason peeking is a problem: the p-value is fine and the
        # sample is not. Grading this `passed` is how a false positive becomes a brand rule.
        report = check_test_readout.read(
            [("A", 600, 12), ("B", 600, 40)], mde=0.20, alpha=0.05, power=0.80,
            daily_clicks=None, claim=None)
        self.assertTrue(report["significant"])
        self.assertEqual(report["verdict"]["status"], "review")
        self.assertTrue(any("false positive" in note for note in report["notes"]))

    def test_no_difference_at_adequate_size_is_reported_as_a_decision(self) -> None:
        report = check_test_readout.read(
            [("A", 40000, 2000), ("B", 40000, 2010)], mde=0.20, alpha=0.05, power=0.80,
            daily_clicks=None, claim=None)
        self.assertEqual(report["verdict"]["status"], "passed")
        self.assertFalse(report["significant"])
        self.assertIn("stop paying", report["verdict"]["summary"])

    def test_impossible_and_empty_inputs_are_refused(self) -> None:
        with self.assertRaises(ValueError):
            check_test_readout.parse_variant("A:clicks=100,conversions=200")
        with self.assertRaises(ValueError):
            check_test_readout.parse_variant("A:clicks=0,conversions=0")
        with self.assertRaises(ValueError):
            check_test_readout.parse_variant("A:conversions=5")
        with self.assertRaises(ValueError):
            check_test_readout.read([("A", 100, 5), ("B", 100, 9)], 0.2, 0.05, 0.8, None, "C")
        # A zero baseline cannot be sized against, and saying so beats returning a computed-looking
        # number for a rate that does not exist.
        self.assertIsNone(check_test_readout.required_per_arm(0.0, 0.2, 0.05, 0.8))
        report = check_test_readout.read([("A", 500, 0), ("B", 500, 3)], 0.2, 0.05, 0.8, None, None)
        self.assertIsNone(report["required_per_arm"])
        self.assertTrue(any("no baseline rate" in note for note in report["notes"]))

    def test_the_rule_it_enforces_points_at_it(self) -> None:
        # learning-loop.md carried "never declare a winner from tiny delivery" for a long time with
        # no way to compute tiny. If the prose and the script ever separate again, the rule goes back
        # to being unenforceable.
        text = (SKILL_ROOT / "references" / "learning-loop.md").read_text(encoding="utf-8")
        self.assertIn("check_test_readout.py", text)
        self.assertIn("--plan", text)
        self.assertIn("--claim", text)


class PromptGrammarTests(unittest.TestCase):
    """Every capability flag in the checker has to be traceable to a row somebody read.

    The unit exists because the internet's prompt advice is written as if one grammar covered every
    provider, and the vendor pages disagree with it in nine specific places. The risk in encoding that
    is drift: a flag gets edited to match a newer memory and the row it cites stops saying so. These
    tests pin the direction rather than the wording - a flag must resolve to a row, a recorded gap must
    not be dressed up as a value, and the skill's own compiler must pass the checker, because the first
    thing the checker did was fail it."""

    def test_self_check_passes(self) -> None:
        report = check_prompt_grammar.self_check()
        self.assertTrue(report.rstrip().endswith("verdict passed"), report)
        self.assertNotIn("FAIL", report)

    def test_every_family_flag_cites_a_row_that_exists(self) -> None:
        # build() already raises on a missing id, but only for the family being checked. This walks
        # all nine, so an unreachable family cannot carry a dangling citation indefinitely.
        facts = check_prompt_grammar.load_facts()
        for family in check_prompt_grammar.FAMILIES:
            for fact_id in family.facts():
                with self.subTest(family=family.name, fact_id=fact_id):
                    self.assertIn(fact_id, facts,
                                  f"{family.name} cites {fact_id}, which is not in prompt-grammar.csv")

    def test_a_recorded_gap_is_never_cited_as_a_capability_value(self) -> None:
        """A row graded no-primary-source records that nobody publishes the answer. Reading one as a
        number or a field would turn "we could not find this" into "we checked and it is fine"."""
        facts = check_prompt_grammar.load_facts()
        for family in check_prompt_grammar.FAMILIES:
            for attr, fact_attr in (("token_window", "window_fact"),
                                    ("prompt_char_limit", "char_limit_fact"),
                                    ("text_char_limit", "text_fact")):
                fact_id = getattr(family, fact_attr)
                if fact_id is None or getattr(family, attr) is None:
                    continue
                with self.subTest(family=family.name, fact_id=fact_id):
                    self.assertNotEqual(
                        facts[fact_id]["evidence_grade"], "no-primary-source",
                        f"{family.name}.{attr} is a number sourced from a row that records "
                        f"the absence of a source")

    def test_an_unpublished_value_is_review_and_never_passed(self) -> None:
        # The whole point of the third exit code. FLUX publishes no token window, so a short prompt
        # is unsettled rather than cleared, and nothing in the report may claim otherwise.
        gates = {g["gate"]: g for g in check_prompt_grammar.build("a glass bottle", "flux")["gates"]}
        self.assertEqual(gates["prompt-window"]["status"], "review")
        self.assertEqual(gates["prompt-character-limit"]["status"], "skipped")

    def test_a_negative_block_fails_on_a_family_with_no_such_field(self) -> None:
        """This is the regression that started the unit. FLUX documents no negative-prompt support, so
        a NEGATIVE PROMPT heading is not an unused feature - it is the excluded thing entering the
        prompt as content."""
        report = check_prompt_grammar.build(
            "A glass bottle on stone.\n\nNEGATIVE PROMPT\nplastic skin, extra fingers", "flux")
        gate = [g for g in report["gates"] if g["gate"] == "negative-prompt-field"][0]
        self.assertEqual(gate["status"], "failed")
        self.assertEqual(gate["fact_id"], "flux2-no-negative")
        self.assertEqual(report["verdict"]["status"], "failed")

    def test_the_same_block_passes_where_the_field_is_documented(self) -> None:
        # Otherwise the gate is just banning a string, and the point is that the field exists on some
        # providers and not others.
        report = check_prompt_grammar.build(
            "A glass bottle on stone.\n\nNEGATIVE PROMPT\nplastic skin", "stable-diffusion-3")
        gate = [g for g in report["gates"] if g["gate"] == "negative-prompt-field"][0]
        self.assertEqual(gate["status"], "passed")

    def test_the_compiler_output_passes_its_own_grammar_check(self) -> None:
        """compile_prompt.py failed this when the checker was first pointed at it. Both branches are
        checked: the family with no negative channel must come back clean, and the exclusions must
        still reach the reader, labelled as inspection criteria rather than prompt text."""
        record = {"mode": "product",
                  "prompt": {"capture_mode": "studio-natural",
                             "subject_action": "One glass bottle on wet stone",
                             "negative_constraints": "plastic reflections, extra fingers"}}
        for provider in ("flux", "midjourney", "openai"):
            with self.subTest(provider=provider):
                prompt = compile_provider(record, provider)
                gate = [g for g in check_prompt_grammar.build(prompt, provider)["gates"]
                        if g["gate"] == "negative-prompt-field"][0]
                self.assertNotEqual(gate["status"], "failed", prompt)
        flux = compile_provider(record, "flux")
        self.assertIn("REJECT CHECKLIST - NOT PART OF THE PROMPT", flux)
        body, checklist = flux.split("REJECT CHECKLIST", 1)
        # The exclusions survive - they just stop being prompt content. If they vanished from both
        # halves the compiler would be silently dropping the brief's avoid list.
        self.assertIn("plastic reflections", checklist)
        self.assertNotIn("plastic reflections", body)

    def test_a_recurring_face_is_refused_where_no_mechanism_is_documented(self) -> None:
        # Midjourney's character parameters are version-locked and dead on the current default, so the
        # honest answer is that there is no page to point at - not that the model cannot do it.
        gate = [g for g in check_prompt_grammar.build(
            "the same woman as before", "midjourney", recurring_person=True)["gates"]
            if g["gate"] == "character-consistency"][0]
        self.assertIn(gate["status"], ("failed", "review"))
        self.assertEqual(gate["fact_id"], "midjourney-cref-dead")

    def test_the_only_published_consistency_ceiling_is_the_one_cited(self) -> None:
        gate = [g for g in check_prompt_grammar.build(
            "four women", "nano-banana-2", recurring_person=True)["gates"]
            if g["gate"] == "character-consistency"][0]
        self.assertEqual(gate["fact_id"], "gemini-reference-counts")

    def test_a_seed_promise_is_review_where_no_seed_is_documented(self) -> None:
        for provider in ("openai", "nano-banana-2", "midjourney"):
            with self.subTest(provider=provider):
                gate = [g for g in check_prompt_grammar.build(
                    "a bottle", provider, needs_reproducible=True)["gates"]
                    if g["gate"] == "seed-reproducibility"][0]
                self.assertIn(gate["status"], ("failed", "review"),
                              f"{provider} documents no seed and was allowed to pass one")

    def test_the_two_length_failures_stay_separate(self) -> None:
        """An encoder window drops the tail silently; an API character limit rejects the request.
        Collapsing them would report a rejected request as a truncated prompt."""
        long_prompt = "a photograph of a bottle " * 60
        legacy = {g["gate"]: g for g in check_prompt_grammar.build(long_prompt,
                                                                  "stable-diffusion-legacy")["gates"]}
        self.assertEqual(legacy["prompt-window"]["status"], "failed")
        self.assertEqual(legacy["prompt-character-limit"]["status"], "skipped")
        openai = {g["gate"]: g for g in check_prompt_grammar.build(long_prompt, "openai")["gates"]}
        self.assertEqual(openai["prompt-window"]["status"], "review")
        self.assertEqual(openai["prompt-character-limit"]["status"], "passed")

    def test_every_row_says_what_it_does_not_establish(self) -> None:
        # The column that keeps a vendor sentence from being read as a general law. A row without it
        # is a quote with the caveat removed.
        for row in DataTableTests.rows("prompt-grammar.csv"):
            with self.subTest(fact_id=row["fact_id"]):
                self.assertGreater(len(row["what_it_does_not_establish"].split()), 3, row["fact_id"])
                if row["evidence_grade"] != "no-primary-source":
                    self.assertTrue(row["url"].startswith("http"), row["fact_id"])

    def test_the_gaps_are_recorded_rather_than_filled(self) -> None:
        rows = DataTableTests.rows("prompt-grammar.csv")
        gaps = [r for r in rows if r["evidence_grade"] == "no-primary-source"]
        self.assertGreaterEqual(len(gaps), 8,
                                "the gap rows are the finding; losing them means the table started "
                                "answering questions nobody published")

    def test_the_reference_and_the_script_stay_together(self) -> None:
        text = (SKILL_ROOT / "references" / "prompt-grammar.md").read_text(encoding="utf-8")
        self.assertIn("check_prompt_grammar.py", text)
        self.assertIn("prompt-grammar.csv", text)
        # The corrections and the gaps are the two halves that make this more than a capability table.
        self.assertIn("What has no source", text)
        for correction in ("--cref", "Parti", "32,000"):
            self.assertIn(correction, text)

    def test_provider_compilers_no_longer_promises_a_field_that_does_not_exist(self) -> None:
        """Two lines on that page taught the opposite of what the vendors document, and a reference
        contradicting the checker beside it is worse than no reference."""
        text = (SKILL_ROOT / "references" / "provider-compilers.md").read_text(encoding="utf-8")
        self.assertNotIn("Keep negative constraints short and concrete", text)
        self.assertNotIn("negative prompt if supported", text)
        self.assertIn("no negative-prompt field", text)


class PriceOfferTests(unittest.TestCase):
    """The discount arithmetic is the reason this unit exists, so it is what gets pinned.

    plan-from-zero promised an offer and the skill had no arithmetic behind the word. The specific
    consequence is that a discount gets decided against the price and lands on the margin, and the two
    are not the same number. If the volume multiple ever stops being printed, the unit is back to being
    a word.
    """

    def test_self_check_passes(self) -> None:
        report = price_offer.self_check()
        self.assertTrue(report.rstrip().endswith("verdict passed"), report)
        self.assertNotIn("FAIL", report)

    def test_twenty_percent_off_forty_percent_margin_needs_double_the_units(self) -> None:
        # The case the whole unit is for, and it is checkable by hand: 20 off 40 leaves 20, and 40
        # over 20 is 2. Exactly 2, not approximately.
        effect = price_offer.discount_effect(100.0, 60.0, 0.20)
        self.assertEqual(effect["contribution_after"], 20.0)
        self.assertEqual(effect["volume_multiple_to_hold_gross_profit"], 2.0)
        self.assertEqual(effect["contribution_lost_share"], 0.5)

    def test_the_same_discount_is_a_different_decision_at_a_different_margin(self) -> None:
        # This asymmetry is why a fixed "keep discounts under 20 percent" rule is not a rule. Same
        # discount, same price, different cost, and the volume it demands is nowhere near the same.
        fat = price_offer.discount_effect(100.0, 30.0, 0.20)
        thin = price_offer.discount_effect(100.0, 60.0, 0.20)
        self.assertAlmostEqual(fat["volume_multiple_to_hold_gross_profit"], 1.4, places=4)
        self.assertAlmostEqual(thin["volume_multiple_to_hold_gross_profit"], 2.0, places=4)
        self.assertGreater(thin["volume_multiple_to_hold_gross_profit"],
                           fat["volume_multiple_to_hold_gross_profit"])

    def test_a_discount_below_variable_cost_has_no_survivable_volume(self) -> None:
        effect = price_offer.discount_effect(100.0, 60.0, 0.50)
        self.assertLess(effect["contribution_after"], 0)
        # No multiple is offered, because there is not one. Returning a number here would suggest the
        # promotion is recoverable with enough units, and it is not.
        self.assertIsNone(effect["volume_multiple_to_hold_gross_profit"])
        report = price_offer.build(100.0, 60.0, 0.50, None, None, None, None, 3.0)
        self.assertEqual(report["verdict"]["status"], "failed")

    def test_break_even_roas_is_the_reciprocal_of_the_contribution_ratio(self) -> None:
        for price, cost in ((100.0, 60.0), (390000.0, 234000.0), (49.0, 12.25)):
            with self.subTest(price=price, cost=cost):
                core = price_offer.margin(price, cost)
                # The reported figure is rounded for reading; the identity is what is being pinned.
                self.assertAlmostEqual(core["break_even_roas"],
                                       1.0 / core["contribution_ratio"], places=3)

    def test_a_price_under_cost_is_refused_before_any_other_arithmetic(self) -> None:
        report = price_offer.build(100.0, 130.0, None, None, None, None, None, 3.0)
        self.assertEqual(report["verdict"]["status"], "failed")
        # Nothing downstream is computed, because a break-even unit count against a negative
        # contribution is a number that would only ever mislead.
        self.assertNotIn("break_even_units", report)
        self.assertTrue(any("loses money" in note for note in report["notes"]))

    def test_a_high_volume_multiple_is_unsettled_rather_than_passed(self) -> None:
        # 30 percent off a 40 percent margin leaves 10, so it needs 4x the units. That is not a
        # promotion anybody signed off on.
        report = price_offer.build(100.0, 60.0, 0.30, None, None, None, None, 3.0)
        self.assertEqual(report["verdict"]["status"], "review")
        self.assertAlmostEqual(report["discount"]["volume_multiple_to_hold_gross_profit"], 4.0,
                               places=4)
        self.assertTrue(any("business model" in note for note in report["notes"]))

    def test_break_even_units_are_computed_on_the_discounted_contribution(self) -> None:
        # The trap: recovering a fixed cost at the undiscounted margin while running the discount.
        plain = price_offer.build(100.0, 60.0, None, 4000.0, None, None, None, 3.0)
        cut = price_offer.build(100.0, 60.0, 0.20, 4000.0, None, None, None, 3.0)
        self.assertEqual(plain["break_even_units"], 100)
        self.assertEqual(cut["break_even_units"], 200)

    def test_both_acquisition_ceilings_are_reported_and_the_binding_one_is_named(self) -> None:
        # 40 contribution, 2 purchases, 3x return gives a policy ceiling of 26.67, which is below
        # first-order break-even of 40. A cost between the two is profitable on order one and outside
        # policy, and the report has to say so rather than just failing a gate.
        report = price_offer.build(100.0, 60.0, None, None, None, 2.0, 30.0, 3.0)
        self.assertAlmostEqual(report["max_acquisition_cost"], 80.0 / 3.0, places=3)
        self.assertEqual(report["first_order_acquisition_ceiling"], 40.0)
        self.assertTrue(any("stricter than first-order" in note for note in report["notes"]))
        # And the other direction, where the gap is a bet on the repeat rate.
        generous = price_offer.build(100.0, 60.0, None, None, None, 6.0, 30.0, 3.0)
        self.assertGreater(generous["max_acquisition_cost"],
                           generous["first_order_acquisition_ceiling"])
        self.assertTrue(any("bet that the repeat rate is real" in note
                            for note in generous["notes"]))

    def test_an_acquisition_cost_without_a_repeat_rate_is_first_order_only(self) -> None:
        report = price_offer.build(100.0, 60.0, None, None, None, None, 30.0, 3.0)
        self.assertNotIn("max_acquisition_cost", report)
        self.assertTrue(any("first-order figure only" in note for note in report["notes"]))

    def test_the_unit_refuses_to_guess_a_currency(self) -> None:
        # A margin helper that assumes a currency will one day be wrong by a factor of 25,000. The
        # numbers are printed as numbers and the caller owns the unit.
        text = price_offer.as_text(price_offer.build(390000.0, 234000.0, 0.2, None, None, None,
                                                     None, 3.0))
        for token in ("VND", "USD", "đ", "$", "dong", "dollar"):
            self.assertNotIn(token, text)

    def test_the_reference_and_the_script_stay_together(self) -> None:
        text = (SKILL_ROOT / "references" / "pricing-and-offers.md").read_text(encoding="utf-8")
        self.assertIn("price_offer.py", text)
        # The Vietnam variable-cost lines are the reason a healthy-looking margin goes negative here
        # specifically, so they are part of the unit rather than a nice-to-have.
        for cost in ("commission", "COD", "return"):
            self.assertIn(cost, text)


class CompositionSetTests(unittest.TestCase):
    """The composition unit contradicts the thing every tool in its category promises.

    "One photo becomes your whole listing" is the claim. This unit answers with a count, and the
    count is under half. So the count is what has to be tested: if the table quietly drifts toward
    optimism - a `new-geometry` row marked obtainable, a fill percentage nudged outside the band
    Google documents - the unit stops disagreeing with the marketing and nobody notices, because a
    more encouraging answer is the one a reader wants.

    Three of these tests exist because the script failed them. It passed a material macro at 0.415x,
    having treated the whole product's height as available to a frame that shows fifteen percent of
    it; it returned a clean pass on a scene rebuild whose condition is an edge and a light direction,
    neither of which a resample factor measures; and it collapsed both review causes into one
    sentence telling the user to inspect the output, when half of them need to inspect the source.
    """

    REFERENCE = "product-composition-set.md"
    TABLE = "product-compositions.csv"

    # The band Google Merchant Center documents for a main product image: no less than 75 and no
    # more than 90 percent of the frame. Hard-coded here rather than read from the table, because a
    # test that reads its threshold from the file it is checking checks nothing.
    MAIN_IMAGE_BAND = (75, 90)

    @classmethod
    def setUpClass(cls) -> None:
        cls.unit = plan_composition_set.CompositionSet.load()
        cls.slots = cls.unit.slots
        cls.prose = (SKILL_ROOT / "references" / cls.REFERENCE).read_text(encoding="utf-8")
        # Blockquote markers are stripped before flattening. A sentence quoted verbatim from another
        # unit is set as a blockquote here, and wrapping it at column 100 puts a `>` in the middle
        # of it, so a naive flatten fails on the formatting rather than on the wording.
        cls.flat = " ".join(line.lstrip("> ") if line.startswith(">") else line
                            for line in cls.prose.splitlines()).replace("  ", " ").strip()
        cls.flat = " ".join(cls.flat.split())

    def report(self, *argv: str) -> tuple[dict, int]:
        """Run the CLI as a caller does, so the exit code is tested rather than assumed."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            code = plan_composition_set.main([*argv, "--format", "json"])
        return json.loads(buffer.getvalue()), code

    def test_every_slot_delivers_at_a_ratio_that_exists(self) -> None:
        """The table's delivery sizes are not written in it, they are joined from
        `data/frame-ratios.csv`. An invented ratio id would make the whole pixel arithmetic run
        against a size no platform publishes."""
        for slot in self.slots:
            with self.subTest(slot["slot_id"]):
                self.assertIn(slot["ratio"], self.unit.ratios)

    def test_a_preserving_derivation_is_never_called_impossible(self) -> None:
        """Cropping, relighting and extending the frame do not need information the source lacks,
        so no such row may be marked unobtainable. This and the next test are the same invariant
        from both sides, and together they are what stops the count from drifting."""
        for slot in self.slots:
            if slot["derivation"] in plan_composition_set.PRESERVING:
                with self.subTest(slot["slot_id"]):
                    self.assertNotEqual(slot["obtainable_from_one_photo"], "no")

    def test_inventing_geometry_or_a_subject_is_never_called_possible(self) -> None:
        """A view or a person the file does not contain cannot be derived from it. If one of these
        rows ever reads `yes` or `conditional`, the unit is asserting exactly the thing it exists to
        refuse, and it would read as a feature."""
        for slot in self.slots:
            if slot["derivation"] not in plan_composition_set.PRESERVING:
                with self.subTest(slot["slot_id"]):
                    self.assertEqual(slot["obtainable_from_one_photo"], "no")
                    self.assertNotEqual(slot["needs_present"], "-",
                                        "unobtainable without naming what is missing")

    def test_generative_editing_is_declared_in_the_metadata_column(self) -> None:
        """Google Merchant Center requires generated or substantially edited images to carry an IPTC
        DigitalSourceType. A row that writes new pixels and declares a plain capture is not a
        style lapse, it is an undeclared edit in a commercial feed."""
        generative = {"outpaint", "background-swap", "scene-rebuild"}
        for slot in self.slots:
            composite = slot["iptc_digital_source_type"].startswith(("composite", "trained"))
            with self.subTest(slot["slot_id"]):
                self.assertEqual(slot["derivation"] in generative, composite)

    def test_a_row_is_conditional_exactly_when_it_carries_a_condition(self) -> None:
        """`obtainable_from_one_photo` and `condition_is` are the same statement twice. Letting them
        disagree is how a conditional row starts reporting a clean pass."""
        for slot in self.slots:
            conditional = slot["obtainable_from_one_photo"] == "conditional"
            with self.subTest(slot["slot_id"]):
                self.assertEqual(conditional, slot["condition_is"] != "-")

    def test_a_crop_into_the_product_needs_more_source_pixels_not_fewer(self) -> None:
        """This is the arithmetic that was wrong first, so it is asserted directly rather than
        left to the invariant above. A macro showing fifteen percent of a 2600 px product draws on
        390 px, and a hero showing all of it draws on 2600. If the macro's factor ever comes out
        below the hero's, the fraction has been dropped again."""
        macro = self.unit.by_slot["detail-macro"]
        hero = self.unit.by_slot["main-hero-white"]
        self.assertEqual(int(macro["shows_pct_of_product"]), 15)
        self.assertEqual(int(hero["shows_pct_of_product"]), 100)
        source, product = (3024, 4032), 2600
        self.assertGreater(self.unit.factor(macro, source, product)["factor"],
                           self.unit.factor(hero, source, product)["factor"])
        # And it does not merely lose to the hero, it fails outright on a phone photograph.
        self.assertGreater(self.unit.factor(macro, source, product)["factor"],
                           plan_composition_set.UPSCALE_CEILING)

    def test_both_resample_constraints_are_always_reported(self) -> None:
        """Reporting only the worst factor hides which one to fix, and the two fixes are different
        actions: shoot at higher resolution, or step closer."""
        measured = self.unit.factor(self.unit.by_slot["main-hero-white"], (3024, 4032), 2600)
        self.assertEqual([part["constraint"] for part in measured["parts"]],
                         ["frame", "product-fill"])
        self.assertEqual(measured["factor"], max(part["factor"] for part in measured["parts"]))

    def test_a_slot_the_pixels_cannot_settle_returns_review_not_passed(self) -> None:
        """A scene rebuild on a large source has ample pixels, and the pixels were never the
        condition. Returning `passed` there is the script answering a question it did not ask - the
        same error the Vietnam unit made when it passed two roles it had not counted."""
        judged = self.unit.judge(self.unit.by_slot["in-use-context"], set(), (4000, 6000), 3400,
                                 None)
        self.assertEqual(judged["status"], "review")
        self.assertLess(judged["resample"]["factor"], plan_composition_set.UPSCALE_CEILING)
        self.assertIn("unsettled", judged, "review without naming what is unsettled")

    def test_a_missing_exposure_fails_however_large_the_source(self) -> None:
        """The presence gate has to beat the pixel gate. A 100-megapixel photograph of the front of
        a box contains none of the back of it, and the failure has to say so rather than talk about
        resolution."""
        judged = self.unit.judge(self.unit.by_slot["back-panel"], set(), (12000, 12000), 11000,
                                 None)
        self.assertEqual(judged["status"], "failed")
        self.assertEqual(judged["unlocked_by"], "back-exposure")
        self.assertNotIn("resample", judged, "a presence failure is arguing about pixels")

    def test_naming_the_exposure_unlocks_the_slot(self) -> None:
        """`--have` is the input the user actually answers, so the gate has to open on it. If it
        did not, the reshoot advice would be unfalsifiable: shoot more and nothing changes."""
        slot = self.unit.by_slot["back-panel"]
        judged = self.unit.judge(slot, {"back-exposure"}, (3024, 4032), 2600, None)
        self.assertEqual(judged["status"], "passed")

    def test_no_source_dimensions_is_skipped_and_not_a_pass(self) -> None:
        """The four statuses have to keep meaning what they say. An unjudged slot is `skipped`, and
        the reason has to state that this is not the same as the slot being fine."""
        judged = self.unit.judge(self.unit.by_slot["main-hero-white"], set(), None, None, None)
        self.assertEqual(judged["status"], "skipped")
        self.assertIn("not", judged["why"])

    def test_the_headline_count_in_the_prose_is_re_derived(self) -> None:
        """Seven of eighteen is the sentence that will be quoted out of this unit, so it is counted
        from the table rather than trusted. If somebody adds two croppable slots and the prose still
        says seven, the quoted figure is the stale one."""
        words = {7: "seven", 3: "three", 8: "eight", 18: "eighteen"}
        counts = {value: sum(1 for s in self.slots if s["obtainable_from_one_photo"] == value)
                  for value in ("yes", "conditional", "no")}
        self.assertEqual(counts, {"yes": 7, "conditional": 3, "no": 8})
        self.assertIn(
            f"Of the {words[len(self.slots)]} slots in `data/{self.TABLE}`, "
            f"{words[counts['yes']]} come out of a single front-on exposure with no conditions "
            f"attached, {words[counts['conditional']]} come out of it only if the source allows "
            f"something specific, and {words[counts['no']]} cannot come out of it at all.",
            self.flat, "the prose does not state the counts the table holds")

    def test_the_marketplace_main_image_count_is_re_derived(self) -> None:
        """A composition being good and a composition being submittable are different questions,
        and the second one has a number. Five of eighteen."""
        allowed = [s["slot_id"] for s in self.slots if s["marketplace_main_image"] == "allowed"]
        self.assertEqual(len(allowed), 5)
        self.assertIn("five of the eighteen are valid as a marketplace main image", self.flat)

    def test_whole_product_main_images_sit_inside_the_documented_fill_band(self) -> None:
        """The fill percentages on those rows are Google's documented band, not house taste. The
        one row outside it is `on-model`, which frames a person rather than the product, and it is
        excluded by name so the exception cannot silently widen to cover a drifting row."""
        low, high = self.MAIN_IMAGE_BAND
        for slot in self.slots:
            if slot["marketplace_main_image"] != "allowed" or slot["slot_id"] == "on-model":
                continue
            with self.subTest(slot["slot_id"]):
                self.assertGreaterEqual(int(slot["product_fill_pct"]), low)
                self.assertLessEqual(int(slot["product_fill_pct"]), high)

    def test_every_metadata_code_is_a_real_iptc_qcode(self) -> None:
        """The vocabulary was fetched, and Google's own guidance names three codes in a casing the
        vocabulary does not use - and omits the one that applies to editing a real photograph. So
        the codes are checked against the vocabulary, and the emitted URI has to resolve into it."""
        emitted = self.unit.metadata([self.unit.judge(slot, {slot["needs_present"]}, (6000, 6000),
                                                      5000, None) for slot in self.slots])
        self.assertTrue(emitted)
        for entry in emitted:
            with self.subTest(entry["qcode"]):
                self.assertRegex(entry["qcode"], r"^[a-z][A-Za-z]+$")
                self.assertTrue(entry["uri"].endswith("/" + entry["qcode"]))
                self.assertIn("cv.iptc.org/newscodes/digitalsourcetype", entry["uri"])
        self.assertIn("compositeWithTrainedAlgorithmicMedia",
                      {entry["qcode"] for entry in emitted})

    def test_the_reshoot_advice_is_a_count_of_named_slots(self) -> None:
        """Told that more images convert better, a shop owner does nothing. Told that one exposure
        turns a named failing slot into a producible one, they can decide. So the output has to
        carry the slot names, not a total."""
        report, _ = self.report("--set", "marketplace", "--source", "3024x4032",
                                "--product-px", "2600")
        self.assertTrue(report["reshoot_value"])
        for entry in report["reshoot_value"]:
            with self.subTest(entry["one_more_exposure"]):
                self.assertTrue(entry["unlocks"])
                self.assertEqual(entry["count"], len(entry["unlocks"]))
                self.assertIn(entry["one_more_exposure"], {s["needs_present"] for s in self.slots})

    def test_the_two_review_causes_are_reported_separately(self) -> None:
        """An accepted upscale is settled by looking at the delivered frame; an unsettled condition
        is settled by looking at the source. One sentence covering both sends half the users to the
        wrong file."""
        report, code = self.report("--slots", "in-use-context", "--source", "4000x6000",
                                   "--product-px", "3400")
        self.assertEqual(code, 3)
        self.assertEqual(report["verdict"]["status"], "review")
        self.assertIn("does not measure", report["verdict"]["why"])

    def test_the_exit_codes_match_the_four_statuses(self) -> None:
        """The exit code is the only part of this a shell script reads, so a wrong one turns a
        blocking failure into a green build."""
        _, failing = self.report("--set", "marketplace", "--source", "3024x4032",
                                 "--product-px", "2600")
        self.assertEqual(failing, 2)
        _, clean = self.report("--slots", "main-hero-white", "--source", "3024x4032",
                               "--product-px", "2600")
        self.assertEqual(clean, 0)
        _, unjudged = self.report("--slots", "main-hero-white")
        self.assertEqual(unjudged, 3)

    def test_the_reference_is_reachable_and_shares_the_review_rationale(self) -> None:
        """This is the third unit to use the four-status vocabulary, and the sentence explaining why
        `review` exists is quoted verbatim in each, because a status that means something different
        per unit means nothing across them."""
        router = (SKILL_ROOT / "references" / "marketing-system-router.md").read_text(
            encoding="utf-8")
        self.assertIn(self.REFERENCE, router, "the unit is not reachable from the router")
        self.assertIn("`review` exists so that the gates that do fail mean something. A checker "
                      "that returns a verdict on everything gets ignored on everything.", self.flat)

    def test_the_unsourced_platform_spec_is_declared_rather_than_guessed(self) -> None:
        """Shopee's own image specification could not be retrieved, and the third-party writing
        that fills the gap contradicts itself. Picking the most common figure would have produced a
        plausible number with no provenance, which is the failure mode this skill grades for."""
        self.assertIn("no-source-found", self.flat)
        for slot in self.slots:
            with self.subTest(slot["slot_id"]):
                self.assertNotIn("shopee", slot["source"].lower())


class CustomerEvidenceTests(unittest.TestCase):
    """The unit exists to stop two sentences, and these tests exist to stop the unit relaxing.

    "We talked to customers and they said X" and "sixty percent of customers want X" are both
    written by honest people, and both survive review because the denominator was never recorded.
    `check_evidence_saturation.py` refuses them arithmetically: no `denied` row for a theme means no
    share is printed at all, and a share whose interval is wider than twenty points is returned as a
    direction. Those two refusals are the whole value of the script, and both are easy to soften
    later by somebody who wants a percentage for a slide - so each has a test below built on a file
    written for the purpose rather than on the shipped example, which could be edited to agree.

    The remaining tests hold the reference to the script. A prose file quoting a floor of twelve
    beside a script that fires at ten is worse than either alone: the reader trusts the number they
    read and the tool grades on a different one.
    """

    REFERENCE = "customer-evidence.md"
    TABLE = "evidence-sources.csv"
    EXAMPLE = "customer-evidence-coded.csv"

    # The nine gates, spelled out rather than read from the script, because a test that derives its
    # expectations from the code under test passes on a gate that has been deleted.
    GATES = ("provenance-recorded", "known-source", "input-vocabulary", "disconfirmation-recorded",
             "code-saturation", "source-headcount", "share-precision", "triangulated",
             "stored-quote-rights")

    # The reference sets its numbers in words, because a sentence reading "12 is the floor" in the
    # middle of an argument is a different register from the rest of the file. That is a formatting
    # choice, and it must not become a way for the prose and the script to disagree unnoticed - so
    # each script constant is paired with the words the reference is required to use for it.
    IN_WORDS = {"CODE_SATURATION_MIN": "twelve", "MEANING_SATURATION_MIN": "sixteen"}

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = {row["source_id"]: row for row in DataTableTests.rows(cls.TABLE)}
        cls.prose = (SKILL_ROOT / "references" / cls.REFERENCE).read_text(encoding="utf-8")
        cls.flat = " ".join(cls.prose.split())
        cls.example = SKILL_ROOT / "assets" / "examples" / cls.EXAMPLE
        cls.report = check_evidence_saturation.check(cls.example)

    @staticmethod
    def coded(rows: list[dict[str, str]]) -> Path:
        """Write a coded file for one assertion. Returns a path inside a temporary directory that
        the caller does not have to clean up, because the file is small and the process is short."""
        columns = list(rows[0])
        handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False,
                                             encoding="utf-8", newline="")
        with handle:
            writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        return Path(handle.name)

    @staticmethod
    def row(rid: str, sequence: int, code: str, stance: str, **extra: str) -> dict[str, str]:
        base = {"respondent_id": rid, "sequence": str(sequence), "source_id": "switch-interviews",
                "code": code, "stance": stance, "intensity": "emphasised",
                "provenance": "2026-06-01 test"}
        base.update(extra)
        return base

    def test_the_gate_names_and_statuses_are_the_shared_vocabulary(self) -> None:
        """Fourth unit to use the four-status vocabulary. A fifth status, or a gate that quietly
        stops being emitted, would make a `passed` verdict mean less than the last unit's."""
        emitted = [gate["gate"] for gate in self.report["gates"]]
        self.assertEqual(tuple(emitted), self.GATES, "a gate was added, renamed or dropped")
        for gate in self.report["gates"]:
            with self.subTest(gate=gate["gate"]):
                self.assertIn(gate["status"], {"passed", "failed", "review", "skipped"})
                self.assertTrue(gate["detail"].strip(), "a gate returned no reason")

    def test_a_theme_nobody_denied_gets_a_count_and_no_share(self) -> None:
        """The defect this unit was built for. Five people raised it out of five people who raised
        it is a hundred percent and no information, and the arithmetic of that theme is otherwise
        indistinguishable from a well-supported one. So the share must be absent, not small."""
        rows = [self.row(f"r{i:02d}", i, "unanimous", "raised") for i in range(1, 6)]
        report = check_evidence_saturation.check(self.coded(rows))
        theme = next(t for t in report["themes"] if t["code"] == "unanimous")
        self.assertEqual(theme["verdict"], "counted-only")
        self.assertIsNone(theme["interval"], "a share was printed with no denominator behind it")
        self.assertIsNone(theme["share_of_asked"])
        gate = next(g for g in report["gates"] if g["gate"] == "disconfirmation-recorded")
        self.assertEqual(gate["status"], "failed")

    def test_recording_the_denial_is_what_turns_a_count_into_a_share(self) -> None:
        """The other half of the test above, and the reason the fix is a column rather than a
        warning: the same theme becomes reportable the moment somebody is recorded saying no."""
        rows = [self.row(f"r{i:02d}", i, "asked-both-ways", "raised") for i in range(1, 6)]
        rows.append(self.row("r06", 6, "asked-both-ways", "denied"))
        report = check_evidence_saturation.check(self.coded(rows))
        theme = next(t for t in report["themes"] if t["code"] == "asked-both-ways")
        self.assertIsNotNone(theme["interval"])
        self.assertEqual(theme["asked"], 6)

    def test_a_wide_interval_is_never_returned_as_a_percentage(self) -> None:
        """Six of eight is seventy-five percent and also anywhere from forty-one to ninety-three,
        which is a direction. The gate has to say so rather than rounding it into a finding."""
        rows = [self.row(f"r{i:02d}", i, "loud", "raised") for i in range(1, 7)]
        rows += [self.row(f"r{i:02d}", i, "loud", "denied") for i in range(7, 9)]
        report = check_evidence_saturation.check(self.coded(rows))
        theme = next(t for t in report["themes"] if t["code"] == "loud")
        self.assertEqual(theme["verdict"], "share-too-wide")
        self.assertGreater(theme["interval_width"], check_evidence_saturation.MAX_INTERVAL_WIDTH)
        gate = next(g for g in report["gates"] if g["gate"] == "share-precision")
        self.assertEqual(gate["status"], "review")

    def test_a_stored_quote_from_an_unquotable_source_fails_the_rights_gate(self) -> None:
        """The same rule that keeps the reference set out of this repository, applied to words: the
        platform's terms licence the platform, and a support ticket is not ours to republish. The
        practice is a pointer, and this gate is what makes the practice enforceable."""
        unquotable = [sid for sid, row in self.rows.items() if row["quotable_publicly"] == "no"]
        self.assertTrue(unquotable, "no source is marked unquotable, so the gate guards nothing")
        rows = [self.row("r01", 1, "leaked", "raised", source_id=unquotable[0],
                         verbatim="the actual words the customer typed"),
                self.row("r02", 2, "leaked", "denied", source_id=unquotable[0], verbatim="")]
        report = check_evidence_saturation.check(self.coded(rows))
        gate = next(g for g in report["gates"] if g["gate"] == "stored-quote-rights")
        self.assertEqual(gate["status"], "failed")
        self.assertIn(unquotable[0], gate["detail"])

    def test_the_curve_follows_collection_order_and_not_the_id_column(self) -> None:
        """`sequence` is the load-bearing column and it looks decorative. Saturation is a statement
        about the order you heard things in, so a file written out of order has to produce the same
        curve as the same file sorted - and sorting by respondent id has to be able to change it,
        which is why the ids here run backwards against the sequence."""
        forwards = [self.row("r09", 1, "first", "raised"),
                    self.row("r05", 2, "second", "raised"),
                    self.row("r01", 3, "third", "raised")]
        shuffled = [forwards[1], forwards[2], forwards[0]]
        first = check_evidence_saturation.saturation(forwards)
        second = check_evidence_saturation.saturation(shuffled)
        self.assertEqual(first["curve"], second["curve"], "row order changed the curve")
        self.assertEqual([step["respondent_id"] for step in first["curve"]], ["r09", "r05", "r01"])

    def test_the_floor_column_states_the_number_its_prose_states(self) -> None:
        """`minimum_before_a_theme_counts` is for a reader and `theme_floor` is for the script, and
        the moment they disagree one of them is lying to somebody. The sources whose floor is set by
        the width of an interval rather than a headcount say so in the machine column instead of
        guessing a number a parser would then treat as real."""
        for source_id, row in self.rows.items():
            with self.subTest(source_id=source_id):
                floor = row["theme_floor"]
                if floor.isdigit():
                    self.assertIn(floor, row["minimum_before_a_theme_counts"],
                                  "the floor is not the number the prose gives the reader")
                else:
                    self.assertEqual(floor, "interval-not-a-count")

    def test_every_source_names_a_blindness_that_is_not_a_shrug(self) -> None:
        """The table's whole claim is that each source is blind in a specific and predictable
        direction. A cell reading "various limitations" would satisfy a non-empty check and teach
        nobody which second source to go and find."""
        for source_id, row in self.rows.items():
            with self.subTest(source_id=source_id):
                for column in ("what_it_cannot_see", "what_it_does_not_establish"):
                    cell = row[column]
                    self.assertGreater(len(cell.split()), 6, f"{column} is too short to be a fact")
                    self.assertNotRegex(cell.lower(), r"^(various|many|several|some) ",
                                        f"{column} is a shrug")

    # The sources the reference argues about by name. It deliberately does not paragraph all twenty -
    # that would be the table copied into prose, which this skill's own "look it up, do not recall it"
    # rule exists to prevent. These seven are the ones whose blindness a reader has to know before
    # choosing a source at all, so they are named by id and checked here.
    DISCUSSED = ("public-reviews-own", "support-tickets", "search-and-site-queries",
                 "behaviour-analytics", "own-social-comments", "chat-and-dm-transcripts",
                 "competitor-review-mining")

    def test_the_reference_names_its_sources_by_id_and_invents_none(self) -> None:
        """Checked in the direction that can actually go wrong. The reference is not required to
        paragraph every row, but every id it does cite has to exist - a renamed source leaves prose
        pointing at a `--query` that returns nothing, which is worse than prose that never pointed.
        And the seven whose blindness decides which source to use have to be named, not paraphrased,
        because "reviews are J-shaped" is not something a reader can look up."""
        for source_id in self.DISCUSSED:
            with self.subTest(source_id=source_id):
                self.assertIn(source_id, self.rows, "a discussed source left the table")
                self.assertIn(f"`{source_id}`", self.flat, "discussed but not named as an id")
        # Every other hyphenated code the reference sets in backticks. Three kinds exist and all
        # three can go stale: a source id, a value the script emits, and a theme from the shipped
        # example. The example's codes are read from the file rather than listed, because that is the
        # pairing that rots - the walkthrough discusses a theme and somebody re-authors the example.
        vocabulary = (set(self.rows)
                      | {gate["gate"] for gate in self.report["gates"]}
                      | {theme["code"] for theme in self.report["themes"]}
                      | {flag for theme in self.report["themes"] for flag in theme["flags"]}
                      | {theme["verdict"] for theme in self.report["themes"]}
                      | {row["quotable_publicly"] for row in self.rows.values()}
                      | {row["theme_floor"] for row in self.rows.values()})
        for token in set(re.findall(r"`([a-z]+(?:-[a-z]+){2,})`", self.prose)) - vocabulary:
            with self.subTest(token=token):
                self.fail(f"{token} looks like an id and names nothing that exists")
        self.assertIn("--sources", self.flat, "the reference does not say how to read the other rows")

    def test_the_reference_quotes_the_scripts_numbers_and_not_its_own(self) -> None:
        """The failure this catches is a reference that ages: somebody tunes a constant, the tests
        still pass because they read the constant, and the prose keeps quoting last month's floor."""
        for name, word in self.IN_WORDS.items():
            with self.subTest(constant=name):
                self.assertIn(word, self.flat.lower(),
                              f"{name} is {getattr(check_evidence_saturation, name)} "
                              f"and the reference does not say so")
        # The result that removes a genre of slide, recomputed here rather than quoted: a share near
        # a half needs this many people before its interval is narrow enough to be called a number.
        twenty_points = check_evidence_saturation.respondents_needed(0.5, 0.20)
        ten_points = check_evidence_saturation.respondents_needed(0.5, 0.10)
        self.assertEqual(twenty_points, 93)
        self.assertEqual(ten_points, 381)
        self.assertIn("ninety-three", self.flat.lower(),
                      "the headline number is not in the reference")
        self.assertIn("three hundred and eighty-one", self.flat.lower())
        self.assertIn("A qualitative study cannot produce a percentage", self.flat)

    def test_the_wilson_interval_stays_inside_the_unit_square(self) -> None:
        """The reason this script does not use the textbook interval. At n=5 and p=1 the normal
        approximation returns an upper bound of exactly 1 and a width of zero, which is where
        customer research actually lives - small n, shares against the edge."""
        for total in range(1, 40):
            for successes in (0, 1, total - 1, total):
                if successes < 0:
                    continue
                low, high = check_evidence_saturation.wilson(successes, total)
                with self.subTest(successes=successes, total=total):
                    self.assertGreaterEqual(low, 0.0)
                    self.assertLessEqual(high, 1.0)
                    self.assertLess(low, high, "a degenerate interval claims certainty")

    def test_the_shipped_example_closes_its_themes_and_licenses_no_percentage(self) -> None:
        """The example is the argument in one file: eighteen respondents is ample for closing a
        theme list and buys not one reportable share. If a future edit produces a quotable
        percentage at n=18, the reference's central claim is false and this test says so."""
        self.assertEqual(self.report["verdict"], "review")
        self.assertEqual(self.report["saturation"]["respondents"], 18)
        self.assertEqual(self.report["saturation"]["codes"], 11)
        saturated = next(g for g in self.report["gates"] if g["gate"] == "code-saturation")
        self.assertEqual(saturated["status"], "passed")
        self.assertEqual(self.report["saturation"]["new_codes_in_last_three"], 0)
        reportable = [t["code"] for t in self.report["themes"] if t["verdict"] == "reportable"]
        self.assertEqual(reportable, [], "a qualitative sample produced a quotable share")

    def test_the_example_walkthrough_describes_the_output_it_claims_to(self) -> None:
        """The reference reads the example for the reader, naming two themes and what each licenses.
        Those two sentences are the unit's worked example, and a drifted example makes them fiction."""
        themes = {theme["code"]: theme for theme in self.report["themes"]}
        counterfeit = themes["worried-about-counterfeit"]
        self.assertIn("common-but-passing", counterfeit["flags"])
        self.assertEqual(counterfeit["affirmed"], 10)
        self.assertEqual(counterfeit["blocking"], 2)
        invoice = themes["no-vat-invoice"]
        self.assertIn("rare-but-blocking", invoice["flags"])
        self.assertEqual((invoice["affirmed"], invoice["denied"]), (1, 6))
        self.assertIn("ten of eighteen", self.flat)
        self.assertIn("six people were asked and said it was irrelevant", self.flat)
        # The theme that leaves this unit for another one. Both ends have to exist for the handoff
        # to be real: the finding here, and the rule it triggers over there.
        discount = themes["waited-for-livestream-discount"]
        self.assertEqual((discount["affirmed"], discount["asked"]), (6, 7))
        lifecycle = (SKILL_ROOT / "references" / "lifecycle-retention.md").read_text(
            encoding="utf-8")
        self.assertIn("lifecycle-retention.md", self.flat)
        self.assertIn("Diagnose before discounting", lifecycle)

    def test_the_verbatim_column_of_the_example_holds_pointers_and_not_words(self) -> None:
        """The example has to demonstrate the practice, not just describe it. A quote stored here
        would teach the pattern the rights gate exists to fail, and it would ship customer text in
        a public repository - which is the same decision that keeps the photographs out."""
        rows = list(csv.DictReader(io.StringIO(self.example.read_text(encoding="utf-8"))))
        for row in rows:
            with self.subTest(row["respondent_id"]):
                self.assertRegex(row["verbatim_ref"],
                                 r"(?i)^(rec/|zalo thread|ticket|return|shopee)",
                                 "the verbatim column holds text instead of a locator")

    def test_the_unit_states_what_it_cannot_do_before_it_hands_off(self) -> None:
        """Every reference in this skill that grades evidence carries this section, and here it is
        load-bearing: the gates can all pass on a study built from leading questions, and nothing in
        the script inspects the questionnaire. A reader who does not know that trusts a clean run."""
        self.assertIn("## What this unit cannot do", self.prose)
        limits = self.prose.split("## What this unit cannot do")[1].split("## ")[0]
        self.assertGreaterEqual(len([line for line in limits.splitlines()
                                     if line.startswith("- ")]), 6)
        for admission in ("leading question", "non-responders", "counterfactual"):
            with self.subTest(admission=admission):
                self.assertIn(admission, " ".join(limits.split()))
        # The handoff the old five-line version got right, and the only thing worth keeping from it.
        handoff = self.prose.split("## The handoff")[1]
        for item in ("beachhead", "job to be done", "awareness stage", "evidence gap"):
            with self.subTest(item=item):
                self.assertIn(item, " ".join(handoff.split()))

    def test_the_unit_is_reachable_from_the_router_and_the_lookup(self) -> None:
        """A mandatory module of the `deep-research` pipeline that no overlay routes to is how this
        file spent its first version at five lines: named in a pipeline, described nowhere."""
        router = (SKILL_ROOT / "references" / "marketing-system-router.md").read_text(
            encoding="utf-8")
        self.assertIn(self.REFERENCE, router)
        self.assertIn(self.TABLE, router)
        self.assertIn("check_evidence_saturation.py", router)
        table, key, searched = find_recipe.TABLES["evidence"]
        self.assertEqual((table, key), (self.TABLE, "source_id"))
        header = next(iter(self.rows.values()))
        for column in searched:
            with self.subTest(column=column):
                self.assertIn(column, header, "the lookup searches a column that does not exist")

    def test_the_self_check_passes(self) -> None:
        """The script's own assertions, run in the suite rather than only by hand, because a
        `--self-check` nobody runs is documentation."""
        report = check_evidence_saturation.self_check()
        self.assertIn("passed", report.lower())
        self.assertNotIn("FAIL", report)


class SeoWritingTests(unittest.TestCase):
    """SEO was the skill's loudest false promise, and these tests exist to stop it becoming one again.

    The capability was named in the SKILL.md description and delivered as three bullets in
    `copywriting.md`. The temptation when building the replacement is to make it look complete by
    printing numbers for search volume, difficulty and position - which are live SERP facts no
    offline script can know, so every one of them would be invented. Two tests below hold that line:
    the unknowns block must appear on every run, and no gate may claim to measure competition.

    The rest hold the reference to the script. A prose file quoting a limit of 160 characters beside
    a script that fires at 150 is worse than either alone, because the reader trusts the number they
    read and the tool grades on a different one.
    """

    REFERENCE = "seo-writing.md"
    TABLE = "seo-intents.csv"

    # Spelled out rather than read from the script, because a test that derives its expectations from
    # the code under test still passes after a gate has been deleted.
    ALWAYS = ("title-present", "title-truncation", "meta-description", "single-h1", "heading-ladder",
              "information-gain", "internal-link")
    # Gates that must be absent rather than passing when the evidence for them was never supplied.
    CONDITIONAL = ("query-in-title", "query-in-a-heading", "answer-before-narrative",
                   "phrase-repetition", "proof-count-for-intent", "image-alt")

    # Each script constant paired with the words the reference is required to use for it. The
    # reference sets its numbers in words where a bare digit would break the register of the
    # sentence, which is a formatting choice and must not become a way for the two to drift.
    IN_WORDS = {
        "TITLE_CHARS_MIN": "fifteen characters",
        "TITLE_PIXELS_MAX": "580 pixels",
        "META_CHARS_MIN": "seventy",
        "META_CHARS_MAX": "a hundred and sixty characters",
        "ANSWER_WITHIN_UNITS": "hundred and twenty words",
        "PHRASE_PER_300_MAX": "three times per three hundred words",
        "GAIN_PER_300_MIN": "three specifics per three hundred words",
    }

    # A page that does everything right, used as the control. Front matter declared, query answered
    # in the first sentence, four checkable things, one internal link.
    GOOD = ("---\ntitle: Giá bàn gỗ sồi tháng 7 2026\n"
            "description: Giá bàn gỗ sồi tại xưởng Gò Vấp, cập nhật 12/07/2026, kèm phí giao "
            "và thời gian bảo hành.\nquery: giá bàn gỗ sồi\nintent: price\n---\n\n"
            "# Giá bàn gỗ sồi\n\nGiá bàn gỗ sồi là 4.500.000 đồng, cập nhật ngày 12/07/2026. "
            "Mặt bàn dày 25mm. Giao trong 48 giờ ở TP HCM với phí 150.000 đồng.\n\n"
            "## Giá thay đổi theo gì\n\nBản 1m6 cộng thêm 800.000 đồng. Gọi 0901 234 567.\n\n"
            "Xem thêm [bàn ăn gỗ](/ban-an-go).\n")

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = {row["id"]: row for row in DataTableTests.rows(cls.TABLE)}
        cls.prose = (SKILL_ROOT / "references" / cls.REFERENCE).read_text(encoding="utf-8")
        cls.flat = " ".join(cls.prose.split())

    def gates_for(self, text: str, query: str | None = None, intent: str | None = None) -> dict:
        stats = audit_seo_page.read_page(text, query, intent)
        return {row["gate"]: row for row in audit_seo_page.gates(stats)}

    def test_the_self_check_passes(self) -> None:
        self.assertIn("passed", audit_seo_page.self_check())

    def test_the_control_page_clears_every_gate(self) -> None:
        verdicts = self.gates_for(self.GOOD)
        failed = [name for name, row in verdicts.items() if not row["pass"]]
        self.assertEqual(failed, [], failed)
        self.assertEqual(audit_seo_page.blocking_count(list(verdicts.values())), 0)

    def test_a_gate_with_no_evidence_is_absent_rather_than_passing(self) -> None:
        """A pass on no evidence reads as a clean bill of health, which is the failure mode."""
        bare = "# Bàn gỗ sồi Gò Vấp\n\nXưởng ở Gò Vấp, mở từ 2019. Gọi 0901 234 567.\n"
        named = set(self.gates_for(bare))
        for gate in self.ALWAYS:
            self.assertIn(gate, named, gate)
        for gate in self.CONDITIONAL:
            self.assertNotIn(gate, named, gate)

    def test_naming_the_query_and_intent_turns_the_conditional_gates_on(self) -> None:
        named = set(self.gates_for(self.GOOD))
        for gate in self.CONDITIONAL:
            if gate == "image-alt":
                continue  # the control page carries no images, so this one stays absent
            self.assertIn(gate, named, gate)

    def test_the_narrative_first_page_blocks(self) -> None:
        """`copywriting.md` said satisfy the real query first. That sentence changed no drafts."""
        narrative = ("---\ntitle: Về chúng tôi và hành trình thương hiệu\nquery: giá bàn gỗ sồi\n"
                     "---\n\n# Về chúng tôi\n\n"
                     + ("Chúng tôi là thương hiệu tận tâm với nhiều năm kinh nghiệm trong ngành nội "
                        "thất cao cấp và luôn đặt khách hàng lên hàng đầu. " * 6)
                     + "\n\nGiá bàn gỗ sồi là 4.500.000 đồng.\n")
        verdicts = self.gates_for(narrative)
        self.assertFalse(verdicts["answer-before-narrative"]["pass"])
        self.assertEqual(verdicts["answer-before-narrative"]["severity"], "high")
        self.assertGreaterEqual(audit_seo_page.blocking_count(list(verdicts.values())), 1)

    def test_proof_inside_a_table_row_counts(self) -> None:
        """The regression that made the reader change. Counting prose only scored 26 of the 60
        reference files as carrying nothing, with their numbers sitting in rows it skipped - and on a
        commercial page it is worse, because the winning `comparison` page is a table."""
        table = ("---\ntitle: So sánh bàn gỗ sồi và gỗ cao su\nquery: so sánh bàn gỗ sồi\n"
                 "description: Bảng so sánh hai loại mặt bàn theo giá, độ dày, bảo hành và thời "
                 "gian giao, đo tháng 7 2026.\nintent: comparison\n---\n\n"
                 "# So sánh bàn gỗ sồi và gỗ cao su\n\n"
                 "| Trục | Sồi | Cao su |\n|---|---|---|\n"
                 "| Giá | 4.500.000 đồng | 2.100.000 đồng |\n"
                 "| Độ dày | 25mm | 18mm |\n| Bảo hành | 24 tháng | 12 tháng |\n"
                 "| Giao ở TP HCM | 48 giờ | 24 giờ |\n\nXem [bàn ăn gỗ](/ban-an-go).\n")
        stats = audit_seo_page.read_page(table, None, None)
        self.assertGreaterEqual(stats["checkable_statements"], int(self.rows["comparison"]["proofs_required"]))
        verdicts = {row["gate"]: row for row in audit_seo_page.gates(stats)}
        self.assertTrue(verdicts["information-gain"]["pass"], verdicts["information-gain"])
        self.assertTrue(verdicts["proof-count-for-intent"]["pass"])

    def test_a_code_fence_is_not_proof(self) -> None:
        """A snippet full of numbers must not read as evidence, and a `#` inside one is not a
        heading. Both would let a technical page pass on content nobody claimed."""
        fenced = "# Cấu hình\n\nĐoạn dưới là ví dụ.\n\n```\n# giá\nprice = 4500000\n```\n"
        stats = audit_seo_page.read_page(fenced, None, None)
        self.assertEqual(stats["h1_count"], 1)
        self.assertFalse(any("4500000" in piece for piece in audit_seo_page.reading_stream(fenced)))

    def test_diacritics_do_not_invent_a_missing_keyword(self) -> None:
        """Vietnamese searchers type both forms and phones autocorrect between them, so a matcher
        that separates `giá` from `gia` reports a keyword missing from a page that carries it."""
        self.assertEqual(audit_seo_page.fold("Giá iPhone ở TP HCM"), "gia iphone o tp hcm")
        folded = ("---\ntitle: Gia ban go soi 2026\nquery: giá bàn gỗ sồi\n---\n\n"
                  "# Gia ban go soi\n\nGia ban go soi la 4.500.000 dong.\n")
        self.assertTrue(self.gates_for(folded)["query-in-title"]["pass"])

    def test_the_title_gate_measures_width_rather_than_characters(self) -> None:
        """A character count passes a title of capitals that will be cut in the results."""
        self.assertGreater(audit_seo_page.title_pixels("MMMMMMMMMMMM"),
                           audit_seo_page.title_pixels("iiiiiiiiiiii"))
        wide = "M" * 60
        self.assertFalse(self.gates_for(f"# {wide}\n\nProse here about it.\n")["title-truncation"]["pass"])

    def test_an_inferred_title_is_labelled_rather_than_silently_accepted(self) -> None:
        """A markdown draft has no title tag. Reading the H1 is the only option, and a report that
        did not say so would let a page ship with no title while showing a pass."""
        stats = audit_seo_page.read_page("# Giá bàn gỗ sồi Gò Vấp\n\nGiá là 4.500.000 đồng.\n", None, None)
        self.assertEqual(stats["title_provenance"], "inferred")
        self.assertIn("inferred", self.gates_for(self.GOOD.replace("title: Giá bàn gỗ sồi tháng 7 2026\n", ""))
                      ["title-present"]["observed"])

    def test_every_run_prints_what_it_could_not_establish(self) -> None:
        """The difference between an on-page audit and the SEO audit somebody will assume they got."""
        stats = audit_seo_page.read_page(self.GOOD, None, None)
        block = " ".join(audit_seo_page.unknowns(stats)).lower()
        for owed in ("volume", "difficulty", "indexab", "claims"):
            self.assertIn(owed, block, owed)
        self.assertIn("Not established by this run",
                      audit_seo_page.report(stats, audit_seo_page.gates(stats)))

    def test_no_gate_claims_to_measure_a_live_serp_fact(self) -> None:
        """Volume, difficulty, position and competitor strength change weekly and differ by city.
        A gate reporting any of them would be printing an invented number."""
        forbidden = ("volume", "difficulty", "ranking position", "competitor", "domain authority")
        for row in audit_seo_page.gates(audit_seo_page.read_page(self.GOOD, None, None)):
            for word in forbidden:
                self.assertNotIn(word, row["observed"].lower(), (row["gate"], word))
                self.assertNotIn(word, row["target"].lower(), (row["gate"], word))

    def test_the_reference_uses_the_numbers_the_script_enforces(self) -> None:
        for constant, words in self.IN_WORDS.items():
            self.assertIn(words, self.flat, f"{constant} is not stated as `{words}`")

    def test_the_reference_and_the_table_agree_on_the_proof_counts(self) -> None:
        """The reference names two rows by their count. If a row changes, the prose must change."""
        self.assertEqual(int(self.rows["definition"]["proofs_required"]), 2)
        self.assertEqual(int(self.rows["best-of"]["proofs_required"]), 6)
        self.assertIn("A `definition` query needs two checkable things", self.flat)
        self.assertIn("a `best-of` list needs six", self.flat)

    def test_every_intent_explains_itself_and_an_unknown_one_fails_loudly(self) -> None:
        for intent in self.rows:
            text = audit_seo_page.explain(intent)
            self.assertIn(self.rows[intent]["page_type_that_wins"], text, intent)
            self.assertIn(self.rows[intent]["vn_note"], text, intent)
        missing = audit_seo_page.explain("no-such-intent")
        self.assertIn("No intent", missing)
        self.assertIn("price", missing)  # the available ids are listed rather than just refused

    def test_every_intent_row_names_a_reflex_to_reject_and_an_honest_limit(self) -> None:
        """The two columns that make the table a decision rather than a description."""
        for intent, row in self.rows.items():
            self.assertGreater(len(row["reflex_to_reject"].split()), 4, intent)
            self.assertGreater(len(row["what_it_does_not_establish"].split()), 4, intent)
            self.assertGreaterEqual(int(row["proofs_required"]), 2, intent)

    def test_the_scoping_warning_survives_in_both_the_table_and_the_prose(self) -> None:
        """The most expensive mistake this unit prevents is quoting for work that cannot win."""
        self.assertIn("aggregator", self.rows["best-of"]["vn_note"].lower())
        self.assertIn("aggregators", self.flat)

    def test_the_exit_code_blocks_a_failing_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.md"
            good.write_text(self.GOOD, encoding="utf-8")
            out = Path(tmp) / "report.md"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(audit_seo_page.main(["--check", str(good), "--output", str(out)]), 0)
            self.assertIn("Blocking failures: 0", out.read_text(encoding="utf-8"))
            bad = Path(tmp) / "bad.md"
            bad.write_text("# Nha\n\nChung toi rat tan tam voi khach hang cua minh.\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(audit_seo_page.main(["--check", str(bad)]), 2)

    def test_the_json_report_carries_the_unknowns_and_the_blocking_count(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            audit_seo_page.main(["--text", self.GOOD, "--json"])
        payload = json.loads(buffer.getvalue())
        self.assertEqual(sorted(payload), ["blocking", "gates", "stats", "unknown"])
        self.assertEqual(payload["blocking"], 0)
        self.assertTrue(payload["unknown"])

    def test_the_copywriting_bullets_route_out_instead_of_pretending(self) -> None:
        """Three bullets stood in for the unit. Deleting them without a route would be a worse gap."""
        copy = (SKILL_ROOT / "references" / "copywriting.md").read_text(encoding="utf-8")
        self.assertIn("seo-writing.md", copy)
        self.assertNotIn("Do not stuff keywords or fabricate expertise signals.", copy)

    def test_the_unit_is_reachable_from_the_router_and_a_pipeline(self) -> None:
        registry = json.loads((SKILL_ROOT / "assets" / "registries" / "pipelines.json")
                              .read_text(encoding="utf-8"))["pipelines"]
        self.assertIn(self.REFERENCE, registry["plan-from-zero"]["references"])
        self.assertIn("audit_seo_page.py", registry["rewrite-human"]["scripts"])
        router = (SKILL_ROOT / "references" / "marketing-system-router.md").read_text(encoding="utf-8")
        self.assertIn(self.REFERENCE, router)

    def test_the_reference_clears_the_skill_own_prose_gates(self) -> None:
        """The unit that measures writing cannot ship prose its own sibling would block."""
        stats = rewrite_human.measure(self.prose, "en")
        rows = rewrite_human.gates(stats, "deliverable")
        tells = rewrite_human.find_tells(self.prose, "en")
        blocking = [row["gate"] for row in rows
                    if not row["pass"] and row["severity"] in ("critical", "high")]
        self.assertEqual(blocking, [], blocking)
        self.assertEqual(rewrite_human.blocking_count(rows, tells), 0,
                         [row["gate"] for row in rows if not row["pass"]] + [t["id"] for t in tells])


class MeasurementTests(unittest.TestCase):
    """The measurement unit, and the two things a test can protect here that review cannot.

    The first is the gate list. Every gate name below is spelled out rather than read off the module,
    because a test that derives its expectations from the code under test still passes after a gate has
    been deleted, and the gates most likely to be deleted are the annoying ones - the two critical
    ones about personal data, which fail on links that somebody is already sending.

    The second is harder and matters more. This unit's whole promise is that a number in it can be
    checked, and the failure mode is not a wrong gate but a confident sentence with nothing behind it.
    So several tests below assert an absence: that no window row cites a domain that is not the
    vendor's, that `verify-in-account` always arrives with the screen to read instead of it, that
    `reconcile` never returns a point estimate, and that the worked arithmetic printed in the prose is
    the arithmetic the functions actually produce. That last one caught nothing yet. It exists because
    a worked example is the first thing to drift when a constant changes, and it drifts silently.
    """

    REFERENCE = "measurement-plan.md"
    EVENTS = "tracking-events.csv"
    WINDOWS = "attribution-windows.csv"
    UNPUBLISHED = "verify-in-account"
    NO_PATH = "path-unpublished"

    # Spelled out, in the order the script emits them. The two critical personal-data gates are the
    # point of the list.
    URL_GATES = ["personal-data-in-url", "required-parameters", "medium-routes-to-a-channel",
                 "lowercase-values", "no-whitespace", "no-double-encoding",
                 "campaign-name-is-a-filter-key", "campaign-name-carries-a-period", "one-separator",
                 "campaign-id-present"]
    EVENT_GATES = ["event-name-charset", "event-name-length", "event-name-not-reserved",
                   "event-name-prefix", "event-name-lowercase", "parameters-per-event",
                   "parameter-name-length", "parameter-value-length",
                   "parameter-name-not-reserved", "personal-data-in-parameters"]

    # Each enforced constant paired with the words the reference has to use for it. A limit the prose
    # does not state is a limit the reader meets for the first time as a failure.
    IN_WORDS = {"EVENT_NAME_MAX": "forty", "CAMPAIGN_SEGMENTS_MIN": "three segments"}

    # A link that should clear everything: three required tags, lowercase, three segments, a yyyymm
    # period, one separator, a campaign id, no personal data, no fragment.
    GOOD_URL = ("https://minthep.vn/ao-linen-nam?utm_source=facebook&utm_medium=cpc"
                "&utm_campaign=202608_linen_hcm&utm_id=c-8842")

    @classmethod
    def setUpClass(cls) -> None:
        cls.events = {row["id"]: row for row in DataTableTests.rows(cls.EVENTS)}
        cls.windows = {row["id"]: row for row in DataTableTests.rows(cls.WINDOWS)}
        cls.prose = (SKILL_ROOT / "references" / cls.REFERENCE).read_text(encoding="utf-8")
        cls.flat = " ".join(cls.prose.split())

    def gates(self, url: str) -> dict[str, dict]:
        return {row["gate"]: row for row in check_tracking_plan.url_gates(
            check_tracking_plan.read_url(url))}

    def event_gates(self, name: str, params: str = "", key_event: bool = False) -> dict[str, dict]:
        stats = check_tracking_plan.read_event(
            name, check_tracking_plan.parse_pairs(params), key_event)
        return {row["gate"]: row for row in check_tracking_plan.event_gates(stats)}

    def test_the_self_check_passes(self) -> None:
        self.assertEqual(check_tracking_plan.self_check(), "self-check passed")

    def test_a_correctly_tagged_link_clears_every_gate(self) -> None:
        rows = self.gates(self.GOOD_URL)
        self.assertEqual(sorted(rows), sorted(self.URL_GATES))
        failed = [gate for gate, row in rows.items() if not row["pass"]]
        self.assertEqual(failed, [], failed)

    def test_every_named_url_gate_still_exists(self) -> None:
        """The list is hardcoded so that deleting a gate breaks a test instead of quietly passing."""
        rows = self.gates("https://minthep.vn/x?utm_source=Facebook%2520Ads&utm_medium=paid social"
                          "&utm_campaign=sale-linen_2026")
        for gate in self.URL_GATES:
            self.assertIn(gate, rows, gate)

    def test_a_leaky_link_fails_the_critical_gate_and_blocks(self) -> None:
        """A phone number in a query string, which is the gate most often failed on purpose."""
        rows = self.gates("https://minthep.vn/dat-hang?utm_source=zalo&utm_medium=social"
                          "&utm_campaign=202608_linen_hcm&sdt=0912345678")
        self.assertFalse(rows["personal-data-in-url"]["pass"])
        self.assertEqual(rows["personal-data-in-url"]["severity"], "critical")
        self.assertTrue(check_tracking_plan.blocking_count(list(rows.values())))

    def test_personal_data_is_caught_by_name_and_by_shape(self) -> None:
        """Two detectors, because the accidental paste and the design decision look different."""
        by_shape = check_tracking_plan.personal_data([("ref", "khach@gmail.com")])
        by_name = check_tracking_plan.personal_data([("ho_ten", "Nguyen Van A")])
        self.assertTrue(by_shape)
        self.assertTrue(by_name)
        # A campaign name and an order id must not trip either detector, or the gate gets switched off.
        self.assertEqual(check_tracking_plan.personal_data(
            [("utm_campaign", "202608_linen_hcm"), ("order", "SO-2026-08-0117")]), [])

    def test_a_vietnamese_mobile_number_is_recognised_and_a_long_id_is_not(self) -> None:
        self.assertTrue(check_tracking_plan.personal_data([("x", "0912345678")]))
        self.assertTrue(check_tracking_plan.personal_data([("x", "+84912345678")]))
        # Eleven digits is not a Vietnamese mobile, and a transaction id must survive.
        self.assertEqual(check_tracking_plan.personal_data([("x", "20260801123456")]), [])

    def test_the_medium_routing_conflict_stays_fixed(self) -> None:
        """`cpm` is on the Display list and also matches the paid pattern. A first-match loop with the
        paid rule on top labelled it Paid Other, confidently and wrongly."""
        self.assertEqual(check_tracking_plan.channel_for("cpm"), "Display")
        self.assertEqual(check_tracking_plan.channel_for("cpc"), "Paid Search or Paid Other")
        self.assertEqual(check_tracking_plan.channel_for("cpv"), "Paid Search or Paid Other")

    def test_the_push_rule_is_not_an_exact_match(self) -> None:
        """Merging it with the audio and sms rules would have rejected both of these."""
        self.assertEqual(check_tracking_plan.channel_for("mobile_push"),
                         "Mobile Push Notifications")
        self.assertEqual(check_tracking_plan.channel_for("web_notification"),
                         "Mobile Push Notifications")

    def test_the_underscored_medium_is_the_near_miss(self) -> None:
        """`social media` routes and `social_media` does not, and nothing else about it looks wrong."""
        self.assertEqual(check_tracking_plan.channel_for("social media"), "Organic Social")
        self.assertIsNone(check_tracking_plan.channel_for("social_media"))
        rows = self.gates("https://minthep.vn/x?utm_source=facebook&utm_medium=social_media"
                          "&utm_campaign=202608_linen_hcm&utm_id=c-1")
        self.assertFalse(rows["medium-routes-to-a-channel"]["pass"])
        others = [gate for gate, row in rows.items()
                  if gate != "medium-routes-to-a-channel" and not row["pass"]]
        self.assertEqual(others, [], others)

    def test_the_paid_label_refuses_to_pick_between_two_channels(self) -> None:
        """The source half of the Paid Search rule needs a site list published as a spreadsheet, so
        the medium alone cannot tell them apart and the label says so instead of guessing."""
        self.assertIn(" or ", check_tracking_plan.channel_for("ppc"))

    def test_tags_after_the_fragment_are_absent_rather_than_present(self) -> None:
        rows = self.gates("https://minthep.vn/x#utm_source=facebook&utm_medium=cpc")
        self.assertIn("tags-after-the-fragment", rows)
        self.assertFalse(rows["tags-after-the-fragment"]["pass"])
        self.assertNotIn("tags-after-the-fragment", self.gates(self.GOOD_URL))

    def test_a_reserved_or_malformed_event_name_blocks(self) -> None:
        for name, gate in [("session_start", "event-name-not-reserved"),
                           ("firebase_thing", "event-name-prefix"),
                           ("add to cart", "event-name-charset"),
                           ("a" * 41, "event-name-length")]:
            rows = self.event_gates(name)
            self.assertFalse(rows[gate]["pass"], name)

    def test_a_registry_event_missing_a_required_parameter_blocks(self) -> None:
        rows = self.event_gates("purchase", "currency=VND")
        self.assertIn("required-parameters-for-this-event", rows)
        self.assertFalse(rows["required-parameters-for-this-event"]["pass"])

    def test_the_ecommerce_parameters_are_not_treated_as_reserved(self) -> None:
        """`currency` and `value` are reserved to *register* and correct to *send*. Blocking them
        would have made the gate wrong on every purchase event in the registry."""
        rows = self.event_gates(
            "purchase", "currency=VND,value=450000,transaction_id=SO-1,items=1")
        self.assertTrue(rows["parameter-name-not-reserved"]["pass"])
        self.assertTrue(rows["required-parameters-for-this-event"]["pass"])

    def test_a_long_page_path_is_exempt_and_a_long_ordinary_value_is_not(self) -> None:
        long_url = "https://minthep.vn/" + "a" * 200
        self.assertTrue(self.event_gates("page_view", f"page_location={long_url}")
                        ["parameter-value-length"]["pass"])
        self.assertFalse(self.event_gates("page_view", f"item_name={'a' * 200}")
                         ["parameter-value-length"]["pass"])

    def test_the_key_event_margin_is_a_note_and_never_blocks(self) -> None:
        name = "a" * 39
        rows = self.event_gates(name, key_event=True)
        self.assertFalse(rows["key-event-name-margin"]["pass"])
        self.assertEqual(rows["key-event-name-margin"]["severity"], "low")
        self.assertEqual(check_tracking_plan.blocking_count([rows["key-event-name-margin"]]), 0)
        # Absent when the flag is not passed, because an inference should not appear as a finding.
        self.assertNotIn("key-event-name-margin", self.event_gates(name))

    def test_the_overlap_floor_is_a_floor_and_never_negative(self) -> None:
        result = check_tracking_plan.reconcile({"meta": 120, "google": 80, "tiktok": 40}, 190)
        self.assertEqual(result["minimum_double_counted"], 50)
        self.assertEqual(result["minimum_share"], round(50 / 240, 4))
        # A sum below the analytics total says nothing, and must not report a negative overlap.
        self.assertEqual(check_tracking_plan.reconcile({"meta": 10}, 90)["minimum_double_counted"], 0)

    def test_the_floor_is_absent_rather_than_guessed_without_an_analytics_total(self) -> None:
        result = check_tracking_plan.reconcile({"meta": 120, "google": 80}, None)
        self.assertIsNone(result["minimum_double_counted"])

    def test_no_gate_or_result_claims_to_know_which_platform_is_right(self) -> None:
        """The unit computes one number on the gap and refuses the interesting question, which is the
        only defensible position without both accounts open."""
        rows = (check_tracking_plan.url_gates(check_tracking_plan.read_url(self.GOOD_URL))
                + check_tracking_plan.event_gates(check_tracking_plan.read_event("purchase", [], False)))
        for row in rows:
            self.assertNotIn("which platform", row["why"].lower(), row["gate"])
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            check_tracking_plan.main(["--url", self.GOOD_URL])
        self.assertIn("Which platform is right when two disagree", buffer.getvalue())

    def test_every_run_prints_what_it_did_not_establish(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            check_tracking_plan.main(["--event", "purchase"])
        text = buffer.getvalue()
        self.assertIn("Not established by this run", text)
        self.assertIn("reads strings, not a browser", text)

    def test_an_unknown_event_routes_to_the_table_instead_of_being_accepted(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            check_tracking_plan.main(["--event", "mua_hang"])
        self.assertIn("not in the registry", buffer.getvalue().lower())
        self.assertIn(self.EVENTS, buffer.getvalue())

    def test_every_event_row_names_the_moment_it_fires_and_what_it_does_not_prove(self) -> None:
        for name, row in self.events.items():
            self.assertGreater(len(row["fires_exactly_when"].split()), 4, name)
            self.assertGreater(len(row["what_it_does_not_prove"].split()), 2, name)
            self.assertGreater(len(row["common_error"].split()), 4, name)
            self.assertIn(row["counted_as_conversion"], ("yes", "no", "sometimes"), name)

    def test_the_cash_on_delivery_stages_are_first_class_events(self) -> None:
        """The four stages the platforms do not offer. Without them a purchase event is reported as
        revenue, which on cash on delivery it is not."""
        for name in ("order-confirmed", "order-delivered", "order-returned"):
            self.assertIn(name, self.events, name)
        self.assertIn("revenue", self.events["purchase"]["what_it_does_not_prove"].lower())

    def test_the_outbound_click_is_marked_as_not_a_conversion(self) -> None:
        """A click to Shopee is the last thing this business can see, and calling it a conversion is
        how a marketplace-heavy report reads as though it converted."""
        self.assertEqual(self.events["marketplace-outbound"]["counted_as_conversion"], "no")
        # `contact-click-phone` is deliberately `sometimes`. A lead business may count a tap;
        # what it may not do is call it a call, so the honesty lives in the other column.
        self.assertEqual(self.events["contact-click-phone"]["counted_as_conversion"],
                         "sometimes")
        self.assertIn("call", self.events["contact-click-phone"]["what_it_does_not_prove"]
                      .lower())

    def test_every_window_row_cites_the_vendor_and_only_the_vendor(self) -> None:
        for name, row in self.windows.items():
            pages = row["vendor_page"].split()
            self.assertTrue(pages, name)
            for page in pages:
                self.assertTrue(page.startswith("https://"), (name, page))
                self.assertTrue(any(host in page for host in check_tracking_plan.VENDOR_HOSTS),
                                (name, page))

    def test_an_unpublished_default_names_the_screen_to_read_instead(self) -> None:
        """`verify-in-account` is not a research gap. It is a record that the vendor publishes no
        default, and it is only honest if it arrives with the place to find the real one.

        Lazada is the case that forced the second branch. Every other row can name a menu path,
        because every other vendor documents its own interface. Lazada documents neither the window
        nor the screen, so demanding a `>` here would have made the row invent a navigation path,
        which is a worse defect than admitting there is none. `path-unpublished` is the admission,
        and it costs more than the `>` it replaces: the row has to name a human with an account and
        say what to bring back."""
        unpublished = [row for row in self.windows.values()
                       if self.UNPUBLISHED in row["default_click_window"]]
        self.assertTrue(unpublished, "the token should still be in use")
        for row in unpublished:
            where = row["where_to_read_it"]
            self.assertGreater(len(where.split()), 8, row["id"])
            if self.NO_PATH in where:
                self.assertIn("screenshot", where.lower(), row["id"])
            else:
                self.assertIn(">", where, row["id"])

    def test_the_no_path_token_is_not_a_way_out_of_naming_a_screen(self) -> None:
        """One row may use it. Two would mean the token had become the easy answer, which is how
        `verify-in-account` would have decayed too if nothing counted it."""
        excused = [row for row in self.windows.values() if self.NO_PATH in row["where_to_read_it"]]
        self.assertEqual([row["id"] for row in excused], ["lazada-seller"])

    def test_every_window_row_explains_the_disagreement_in_its_own_terms(self) -> None:
        seen = set()
        for name, row in self.windows.items():
            why = row["why_it_disagrees_with_analytics"]
            self.assertGreater(len(why.split()), 20, name)
            self.assertNotIn(why, seen, f"{name} repeats another row's explanation")
            seen.add(why)

    def test_the_tiktok_contradiction_is_recorded_rather_than_resolved(self) -> None:
        """Three live vendor pages give two different sets of selectable windows. Picking one and
        printing it as the answer is exactly the failure this table exists to prevent."""
        row = self.windows["tiktok-ads-manager"]
        self.assertEqual(len(row["vendor_page"].split()), 3)
        self.assertIn("contradicts itself", row["configurable_click"])
        # The operational fact that outranks the numbers: it is frozen at publish.
        self.assertIn("cannot be changed", row["where_to_read_it"])

    def test_the_view_through_asymmetry_is_recorded_on_both_sides(self) -> None:
        """The single largest source of a gap that looks like fraud. Meta puts view-through inside the
        headline number and Google Ads puts it outside, so the same word means two things."""
        self.assertTrue(self.windows["meta-ads"]["view_through_in_default_number"].startswith("yes"))
        self.assertTrue(self.windows["google-ads"]["view_through_in_default_number"]
                        .startswith("no"))
        self.assertIn("Results column", self.flat)

    def test_the_reference_states_every_number_the_script_enforces(self) -> None:
        for constant, words in self.IN_WORDS.items():
            self.assertTrue(hasattr(check_tracking_plan, constant), constant)
            self.assertIn(words, self.flat.lower(), constant)

    def test_the_worked_arithmetic_in_the_prose_is_what_the_functions_produce(self) -> None:
        """A worked example is the first thing to drift when a constant changes, and it drifts
        silently, so the prose's numbers are recomputed here rather than trusted."""
        gap = check_tracking_plan.delivery_gap(1000, 640)
        self.assertIn(f"{gap['overstatement'] * 100:.0f} percent", self.flat)
        floor = check_tracking_plan.reconcile({"meta": 120, "google": 80, "tiktok": 40}, 190)
        self.assertIn(f"{floor['minimum_double_counted']:g}", self.flat)
        self.assertIn(f"{floor['minimum_share'] * 100:.1f} percent", self.flat)

    def test_the_delivery_rate_is_presented_as_the_reader_own_number(self) -> None:
        """Nobody publishes a Vietnamese cancellation rate - not the white book, which has no such
        figure, and not VECOM. The share of orders paid in cash is published, and the two get quoted
        as though they were one thing."""
        self.assertIn("worked example and not a benchmark", self.flat)
        self.assertIn("76 percent", self.flat)
        self.assertIn("page 47", self.flat)

    def test_the_superseded_decree_is_not_cited_as_current_law(self) -> None:
        """Decree 13/2023/ND-CP stopped being the instrument on 1 January 2026. Naming it as current
        is the same class of error as quoting an attribution default from memory."""
        for path in [SKILL_ROOT / "references" / self.REFERENCE,
                     SKILL_ROOT / "references" / "how-companies-market.md",
                     SKILL_ROOT / "scripts" / "check_tracking_plan.py"]:
            text = path.read_text(encoding="utf-8")
            if "13/2023" in text or "Decree 13" in text:
                self.assertIn("91/2025", text, path.name)
        self.assertIn("replaced Decree 13/2023/ND-CP", self.flat)

    def test_the_url_gate_makes_no_claim_about_an_article_number(self) -> None:
        """The full text of the superseded decree says nothing about query strings, referrers or logs.
        The argument stands without a statute; inventing an article to strengthen it would not."""
        why = self.gates(self.GOOD_URL)["personal-data-in-url"]["why"]
        self.assertNotIn("Article", why)
        self.assertIn("needs no statute", why)

    def test_the_exit_code_blocks_a_leaky_link_and_passes_a_clean_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.md"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check_tracking_plan.main(
                    ["--url", self.GOOD_URL, "--output", str(out)]), 0)
            self.assertIn("Blocking failures: 0", out.read_text(encoding="utf-8"))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check_tracking_plan.main(
                    ["--url", "https://minthep.vn/x?email=a@b.vn"]), 2)

    def test_the_json_report_carries_the_gates_and_the_blocking_count(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            check_tracking_plan.main(["--url", self.GOOD_URL, "--json"])
        payload = json.loads(buffer.getvalue())
        self.assertEqual(sorted(payload), ["blocking", "sections"])
        self.assertEqual(payload["blocking"], 0)
        self.assertEqual(sorted(row["gate"] for row in payload["sections"][0]["gates"]),
                         sorted(self.URL_GATES))

    def test_purchases_and_delivered_are_only_meaningful_together(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                check_tracking_plan.main(["--purchases", "1000"])

    def test_the_tracking_gate_in_paid_media_routes_out_instead_of_listing(self) -> None:
        """It was one checklist bullet ending in "and guardrails before claiming optimization", which
        is the shape of a rule nobody can fail."""
        paid = (SKILL_ROOT / "references" / "paid-media-creative.md").read_text(encoding="utf-8")
        self.assertIn(self.REFERENCE, paid)
        self.assertIn("check_tracking_plan.py", paid)
        self.assertNotIn("attribution limitations, and guardrails", paid)

    def test_the_unit_is_reachable_from_the_router_and_the_skill(self) -> None:
        router = (SKILL_ROOT / "references" / "marketing-system-router.md").read_text(encoding="utf-8")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for name in (self.REFERENCE, self.EVENTS, self.WINDOWS, "check_tracking_plan.py"):
            self.assertIn(name, router, name)
            self.assertIn(name, skill, name)

    def test_the_reference_clears_the_skill_own_prose_gates(self) -> None:
        stats = rewrite_human.measure(self.prose, "en")
        rows = rewrite_human.gates(stats, "deliverable")
        tells = rewrite_human.find_tells(self.prose, "en")
        self.assertEqual(rewrite_human.blocking_count(rows, tells), 0,
                         [row["gate"] for row in rows if not row["pass"]] + [t["id"] for t in tells])


class SizeMarketTests(unittest.TestCase):
    """The refusals are the unit, and the geometric centre is the part nobody would notice breaking.

    `market-assessment.md` had promised a bottom-up chain for as long as it existed and the skill had no
    arithmetic behind it, so the chain got multiplied in somebody's head and arrived as one confident
    number. Two things here are worth more than the total. A term with no source cannot be totalled at
    all, and the middle of a product is its geometric mean - if that ever quietly becomes an average,
    every base case in every deck built on this gets more optimistic and nothing fails.
    """

    CLEAN = ("term,role,low,high,unit,family,n,source_url,retrieved,what_it_measures\n"
             "urban households,people,8000000,8000000,households,official,,https://nso.gov.vn/x,"
             "2026-07-01,Census household count\n"
             "share buying monthly,incidence,0.18,0.32,share,panel,600,https://example.org/p,"
             "2026-06-01,Claimed monthly purchase\n"
             "purchases per year,frequency,4,7,count,trace,,https://example.org/t,2026-05-01,Receipts\n"
             "price paid,price,45000,70000,currency,trace,,https://shopee.vn/x,2026-07-10,Ladder\n"
             "reachable share,reach,0.1,0.25,share,trace,,https://example.org/d,2026-07-10,Footprint\n")
    AS_OF = "2026-07-31"
    REFERENCES = ("market-assessment.md", "research-protocol.md")

    @classmethod
    def setUpClass(cls) -> None:
        cls.terms = size_market.parse_chain(list(csv.DictReader(io.StringIO(cls.CLEAN))))
        cls.result = size_market.compute(cls.terms)
        cls.rows = size_market.gates(cls.result, cls.AS_OF)

    def chain(self, text: str) -> dict:
        return size_market.compute(size_market.parse_chain(list(csv.DictReader(io.StringIO(text)))))

    def test_self_check_passes(self) -> None:
        report = size_market.self_check()
        self.assertIn("passed", report)
        self.assertNotIn("FAIL", report)

    def test_the_centre_is_the_geometric_mean_and_sits_below_the_average(self) -> None:
        """Two terms, both a factor of ten wide, so the answer is checkable without the script: the
        products are 1 and 100 and the middle is 10, not 50.5. The gap is the whole point - an average
        would put the base case five times above the middle of its own distribution."""
        two = self.chain(
            "term,role,low,high,unit,family,n,source_url,retrieved,what_it_measures\n"
            "a,incidence,0.1,1,share,panel,,https://example.org/a,2026-07-01,x\n"
            "b,frequency,10,100,count,trace,,https://example.org/b,2026-07-01,y\n")
        self.assertEqual(two["addressable_low"], 1.0)
        self.assertEqual(two["addressable_high"], 100.0)
        self.assertAlmostEqual(two["centre"], 10.0, places=9)
        self.assertLess(two["centre"], (1.0 + 100.0) / 2)

    def test_the_shares_of_spread_partition_the_total(self) -> None:
        """Printed as percentages beside every row, so they have to sum to a hundred. They are log
        ratios because the chain multiplies, and the point term contributes nothing."""
        shares = [term["uncertainty_share"] for term in self.result["terms"]]
        self.assertAlmostEqual(sum(shares), 1.0, places=9)
        self.assertEqual(self.result["terms"][0]["uncertainty_share"], 0.0)
        self.assertEqual(self.result["dominant_term"],
                         max(self.result["terms"], key=lambda t: t["uncertainty_share"])["term"])

    def test_a_threshold_outside_the_range_ends_the_research(self) -> None:
        low = size_market.resolve_against(self.result, self.result["addressable_low"] / 2)
        high = size_market.resolve_against(self.result, self.result["addressable_high"] * 2)
        self.assertFalse(low["straddles"])
        self.assertEqual(low["verdict"], "above on every reading")
        self.assertEqual(high["verdict"], "below on every reading")
        # Nothing to research, so nothing is offered. A term list here would be work that cannot
        # change an outcome, dressed as a next step.
        self.assertEqual(low["settled_by"], [])

    def test_a_threshold_inside_the_range_names_the_terms_that_would_settle_it(self) -> None:
        near = self.result["addressable_low"] * 1.05
        resolution = size_market.resolve_against(self.result, near)
        self.assertTrue(resolution["straddles"])
        self.assertEqual(resolution["verdict"], "unresolved")
        named = [item["term"] for item in resolution["settled_by"]]
        self.assertTrue(named)
        # Widest uncertainty first, because that is the order the research hours should be spent in.
        shares = [item["uncertainty_share"] for item in resolution["settled_by"]]
        self.assertEqual(shares, sorted(shares, reverse=True))
        # The point term can never settle anything: collapsing a term that is already a point to its
        # centre changes nothing at all.
        self.assertNotIn("urban households", named)

    def test_a_threshold_on_the_centre_has_no_research_answer(self) -> None:
        """The case the prose has to explain or a reader files it as a bug. Collapsing any single term
        to its own centre leaves the total's centre exactly where it was, so a decision balanced on the
        centre of your own estimate cannot be settled by narrowing one term - or by narrowing all of
        them one at a time. Answering it needs a different decision, not more desk work."""
        resolution = size_market.resolve_against(self.result, self.result["centre"])
        self.assertTrue(resolution["straddles"])
        self.assertEqual(resolution["settled_by"], [])
        text = (SKILL_ROOT / "references" / "market-assessment.md").read_text(encoding="utf-8")
        self.assertIn("leaves the", text)
        self.assertIn("centre", text)

    def test_the_clean_chain_clears_every_gate(self) -> None:
        self.assertEqual(size_market.blocking(self.rows), 0,
                         [row["gate"] for row in self.rows if not row["pass"]])
        self.assertEqual(len(self.rows), 9)
        for row in self.rows:
            self.assertIn(row["severity"], ("critical", "high", "medium", "low"), row["gate"])
            # Every gate has to say why in its own words, or it is a rule nobody can argue with.
            self.assertGreater(len(row["why"].split()), 20, row["gate"])

    def test_an_unsourced_term_is_refused_before_the_total_exists(self) -> None:
        chain = self.chain(self.CLEAN.replace("https://example.org/t", ""))
        rows = size_market.gates(chain, self.AS_OF)
        failed = [row for row in rows if not row["pass"]]
        self.assertEqual([row["gate"] for row in failed], ["every-term-sourced"])
        self.assertEqual(failed[0]["severity"], "critical")
        self.assertIn("purchases per year", failed[0]["observed"])

    def test_a_missing_frequency_term_is_not_a_shorter_chain(self) -> None:
        """Dropping a multiplicative term sets it to one, which is an assertion that every buyer buys
        exactly once a year. Nobody would write that down, and the arithmetic still runs."""
        lines = [line for line in self.CLEAN.splitlines(keepends=True)
                 if "purchases per year" not in line]
        rows = size_market.gates(self.chain("".join(lines)), self.AS_OF)
        failed = {row["gate"] for row in rows if not row["pass"]}
        self.assertIn("chain-is-complete", failed)
        self.assertEqual(size_market.blocking(rows), 1)

    def test_a_list_price_and_a_typed_range_both_fail_their_own_gate(self) -> None:
        listed = self.CLEAN.replace("price paid,price,45000,70000,currency,trace",
                                    "list price,price,60000,60000,currency,official")
        rows = size_market.gates(self.chain(listed), self.AS_OF)
        failed = {row["gate"] for row in rows if not row["pass"]}
        self.assertIn("price-is-observed", failed)
        # A point on anything but the counted term claims exactness. Only a census may do that.
        self.assertIn("range-not-point", failed)

    def test_the_sampling_table_in_the_prose_is_what_the_functions_produce(self) -> None:
        """A worked table drifts silently when a constant moves, so it is recomputed rather than read.
        The right column is wider by exactly sqrt(2), which is where the reference's "about 1.4" comes
        from - two proportions from one survey both carry error."""
        text = (SKILL_ROOT / "references" / "market-assessment.md").read_text(encoding="utf-8")
        for n in (300, 500, 1000, 2000):
            half = size_market.sampling_half_width(n)
            gap = size_market.minimum_detectable_gap(n)
            self.assertAlmostEqual(gap / half, math.sqrt(2), places=9)
            self.assertIn(f"| {n} | {half * 100:.1f} points | {gap * 100:.1f} points |", text)

    def test_a_band_narrower_than_its_own_sampling_error_fails(self) -> None:
        """The defect that looks like diligence: 41 percent read off an n=300 report, entered as 40 to
        42, and the tightness reads as care while being a fifth of the uncertainty already inside it."""
        typed = self.CLEAN.replace("share buying monthly,incidence,0.18,0.32,share,panel,600",
                                   "share buying monthly,incidence,0.40,0.42,share,panel,300")
        rows = size_market.gates(self.chain(typed), self.AS_OF)
        failed = {row["gate"] for row in rows if not row["pass"]}
        self.assertIn("survey-range-beats-its-own-margin", failed)
        self.assertGreater(size_market.sampling_half_width(300), (0.42 - 0.40) / 2)

    def test_staleness_is_measured_against_a_stated_date_not_today(self) -> None:
        """Measured against today, a saved chain would ripen into a failure on its own and, worse, a
        re-run with `--as-of` set back would quietly launder it. The date has to be an argument."""
        fresh = size_market.gates(self.result, "2026-07-31")
        later = size_market.gates(self.result, "2028-01-01")
        self.assertTrue(next(r for r in fresh if r["gate"] == "sources-are-not-stale")["pass"])
        self.assertFalse(next(r for r in later if r["gate"] == "sources-are-not-stale")["pass"])

    def test_the_exit_code_separates_unsupported_from_unsettled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            chain = Path(tmp) / "chain.csv"
            chain.write_text(self.CLEAN, encoding="utf-8")
            out = Path(tmp) / "report.md"
            with contextlib.redirect_stdout(io.StringIO()):
                clean = size_market.main(["--check", str(chain), "--as-of", self.AS_OF,
                                          "--output", str(out)])
                # A threshold the range straddles is computable and unsettled: exit 3, not 0, so a
                # wrapper cannot read an open decision as a cleared one.
                straddled = size_market.main(
                    ["--check", str(chain), "--as-of", self.AS_OF, "--output", str(out),
                     "--threshold", str(self.result["centre"])])
                unsourced = Path(tmp) / "bad.csv"
                unsourced.write_text(self.CLEAN.replace("https://shopee.vn/x", ""), encoding="utf-8")
                broken = size_market.main(["--check", str(unsourced), "--as-of", self.AS_OF,
                                          "--output", str(out)])
        self.assertEqual((clean, straddled, broken), (0, 3, 2))

    def test_the_starter_template_cannot_be_graded_by_accident(self) -> None:
        """It ships with empty lows and highs on purpose. An empty term read as zero would make a
        chain that multiplies to nothing and passes for a finished sizing of a dead market."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chain.csv"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(size_market.main(["--template", str(path)]), 0)
                with contextlib.redirect_stderr(io.StringIO()) as err:
                    self.assertEqual(size_market.main(["--check", str(path)]), 1)
                    # And it refuses to overwrite a chain somebody has already filled in.
                    self.assertEqual(size_market.main(["--template", str(path)]), 1)
        self.assertIn("must both be numbers", err.getvalue())

    def test_the_json_report_carries_the_totals_the_gates_and_the_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            chain = Path(tmp) / "chain.csv"
            chain.write_text(self.CLEAN, encoding="utf-8")
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                size_market.main(["--check", str(chain), "--as-of", self.AS_OF, "--json",
                                  "--threshold", "1000000000000"])
        payload = json.loads(buffer.getvalue())
        self.assertEqual(sorted(payload),
                         ["as_of", "blocking", "gates", "resolution", "terms", "totals"])
        self.assertEqual(payload["blocking"], 0)
        self.assertAlmostEqual(payload["totals"]["centre"], self.result["centre"], places=6)
        self.assertIn("verdict", payload["resolution"])

    def test_the_unit_is_reachable_from_the_router_and_the_skill(self) -> None:
        router = (SKILL_ROOT / "references" / "marketing-system-router.md").read_text(encoding="utf-8")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        for name in (*self.REFERENCES, "size_market.py"):
            self.assertIn(name, router, name)
            self.assertIn(name, skill, name)

    def test_the_two_research_pipelines_carry_the_script_and_both_references(self) -> None:
        registry = json.loads((SKILL_ROOT / "assets" / "registries" / "pipelines.json")
                              .read_text(encoding="utf-8"))
        for pipeline in ("deep-research", "plan-from-zero"):
            entry = registry["pipelines"][pipeline]
            self.assertIn("size_market.py", entry["scripts"], pipeline)
            for name in self.REFERENCES:
                self.assertIn(name, entry["references"], (pipeline, name))

    def test_the_three_references_clear_the_skill_own_prose_gates(self) -> None:
        """Two were rewritten for this unit and the third was only edited, and it turned out to have
        been failing four gates before it was touched. Measuring all three is how that stays fixed."""
        for name in (*self.REFERENCES, "market-data-collection.md"):
            with self.subTest(reference=name):
                text = (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
                stats = rewrite_human.measure(text, "en")
                rows = rewrite_human.gates(stats, "deliverable")
                tells = rewrite_human.find_tells(text, "en")
                self.assertEqual(rewrite_human.blocking_count(rows, tells), 0,
                                 [row["gate"] for row in rows if not row["pass"]]
                                 + [tell["id"] for tell in tells])

    def test_the_stop_rule_lives_in_exactly_one_reference(self) -> None:
        """It is the one piece of procedure `research-protocol.md` uniquely owns. Duplicated into the
        assessment unit, the two copies drift and a reader follows whichever they opened first."""
        protocol = (SKILL_ROOT / "references" / "research-protocol.md").read_text(encoding="utf-8")
        self.assertIn("--threshold", protocol)
        self.assertIn("stop rule", protocol.lower())
        collection = (SKILL_ROOT / "references" / "market-data-collection.md").read_text(
            encoding="utf-8")
        self.assertIn("size_market.py", collection)
        self.assertNotIn("--threshold", collection)

class AffiliateModelTests(unittest.TestCase):
    """The two things worth guarding are the notch and the drift between the code and the table.

    `creator-ugc.md` chose the person and never priced the arrangement, so an affiliate deal was agreed
    on its headline rate in a skill that models everything else. The arithmetic here is ordinary. What
    is not ordinary is that five of its constants are platform figures that moved during 2025 while the
    superseded versions stayed live on their own URLs, so a constant edited in the script and left alone
    in `data/affiliate-mechanics.csv` would produce a model that disagrees with its own sources and
    passes every other test. That is what `test_the_constants_match_the_published_table` exists for.
    """

    CLEAN = ("parameter,low,high,unit,source_url,verified_at,what_it_measures\n"
             "gmv,100000000,100000000,VND,https://example.org/reports,2026-07-01,Attributed value\n"
             "commission_rate,0.08,0.12,share,https://help.shopee.vn/portal/10/article/190646,"
             "2026-07-01,Base plus Xtra\n"
             "return_rate,0.10,0.20,share,https://example.org/recon,2026-07-01,Own reconciliation\n"
             "attribution_window_days,7,7,days,https://help.shopee.vn/portal/10/article/122941,"
             "2026-07-01,Creator window\n"
             "days_to_cash,20,40,days,https://help.shopee.vn/portal/10/article/189769,2026-07-01,"
             "Cadence\n"
             "service_fee,0.0098,0.0098,share,https://help.shopee.vn/portal/10/article/174381,"
             "2026-07-01,Service fee\n"
             "withholding_rate,0.10,0.10,share,https://help.shopee.vn/portal/10/article/163104,"
             "2026-07-01,PIT at source\n"
             "withholding_floor,250000,250000,VND,https://help.shopee.vn/portal/10/article/196407,"
             "2026-07-01,Threshold\n"
             "payments_in_period,8,8,count,https://help.shopee.vn/portal/10/article/189769,2026-07-01,"
             "Payments\n"
             "content_cost,2000000,4000000,VND,https://example.org/rate,2026-07-01,Own hours\n")
    SELLER = ("parameter,low,high,unit,source_url,verified_at,what_it_measures\n"
              "gmv,100000000,100000000,VND,https://example.org/reports,2026-07-01,Attributed value\n"
              "commission_rate,0.08,0.12,share,https://help.shopee.vn/portal/10/article/190646,"
              "2026-07-01,What the seller funds\n"
              "return_rate,0.10,0.20,share,https://example.org/recon,2026-07-01,Own reconciliation\n"
              "attribution_window_days,30,30,days,https://help.shopee.vn/portal/10/article/171010,"
              "2026-07-01,Seller window\n"
              "days_to_cash,20,40,days,https://help.shopee.vn/portal/10/article/171010,2026-07-01,"
              "Cadence\n"
              "contribution_margin,0.30,0.40,share,https://example.org/costing,2026-07-01,Own costing\n")
    AS_OF = "2026-07-31"

    @classmethod
    def setUpClass(cls) -> None:
        cls.deal = cls.parse(cls.CLEAN)
        cls.result = model_affiliate.compute("creator", cls.deal)
        cls.rows = model_affiliate.gates("creator", cls.result, cls.AS_OF)

    @staticmethod
    def parse(text: str) -> dict:
        return model_affiliate.parse_deal(list(csv.DictReader(io.StringIO(text))))

    def creator(self, text: str) -> list[dict]:
        deal = self.parse(text)
        return model_affiliate.gates("creator", model_affiliate.compute("creator", deal), self.AS_OF)

    def test_self_check_passes(self) -> None:
        report = model_affiliate.self_check()
        self.assertIn("passed", report)
        self.assertNotIn("FAIL", report)

    def test_the_constants_match_the_published_table(self) -> None:
        """The script and `data/affiliate-mechanics.csv` are two copies of the same figures, and the
        only reason to keep both is that the table carries the URL while the code carries the
        arithmetic. So they have to be pinned to each other. Editing one alone is the realistic
        mistake: it produces a model that contradicts its own cited source and breaks nothing."""
        with io.open(SKILL_ROOT / "data" / "affiliate-mechanics.csv", encoding="utf-8-sig") as handle:
            rows = {row["id"]: row for row in csv.DictReader(handle)}
        pairs = {
            "service-fee-current": model_affiliate.SERVICE_FEE_CURRENT,
            "service-fee-superseded": model_affiliate.SERVICE_FEE_SUPERSEDED,
            "pit-rate": model_affiliate.WITHHOLDING_RATE,
            "pit-withholding-current": model_affiliate.WITHHOLDING_FLOOR_CURRENT,
            "pit-withholding-superseded": model_affiliate.WITHHOLDING_FLOOR_SUPERSEDED,
            "seller-min-payout": model_affiliate.MINIMUM_PAYOUT,
            "seller-violation-threshold": model_affiliate.VIOLATION_LOCK_SHARE,
        }
        for row_id, constant in pairs.items():
            self.assertIn(row_id, rows, f"{row_id} left the table, the constant is still in the code")
            self.assertAlmostEqual(float(rows[row_id]["value"]), float(constant), places=9,
                                   msg=f"{row_id}: the table and the script disagree")
            self.assertTrue(rows[row_id]["source_url"].startswith("https://"), row_id)
        # And the superseded pair really is superseded, in the direction the prose claims.
        self.assertLess(model_affiliate.SERVICE_FEE_CURRENT, model_affiliate.SERVICE_FEE_SUPERSEDED)
        self.assertLess(model_affiliate.WITHHOLDING_FLOOR_CURRENT,
                        model_affiliate.WITHHOLDING_FLOOR_SUPERSEDED)
        self.assertEqual(rows["service-fee-current"]["supersedes"], "service-fee-superseded")
        self.assertEqual(rows["pit-withholding-current"]["supersedes"], "pit-withholding-superseded")

    def test_the_notch_is_a_real_band_and_the_arithmetic_closes(self) -> None:
        """Withholding applies to the whole payment once it reaches the floor, not to the excess, so
        there is a band above the floor where a larger payment nets less than a smaller one. Checked
        by running the model rather than by restating the formula: a payment one dong below the floor
        is kept whole, and the payment at the top of the band nets exactly the floor."""
        band = model_affiliate.notch()
        self.assertGreater(band["top"], band["floor"])
        self.assertAlmostEqual(band["top"] * (1 - band["rate"]), band["floor"], places=6)
        self.assertLess(band["worst_net"], band["best_below"])

        def net_at(payment: float) -> float:
            values = {"gmv": payment, "return_rate": 0.0, "commission_rate": 1.0,
                      "service_fee": 0.0, "withholding_rate": model_affiliate.WITHHOLDING_RATE,
                      "withholding_floor": model_affiliate.WITHHOLDING_FLOOR_CURRENT,
                      "payments_in_period": 1.0, "content_cost": 0.0}
            return model_affiliate.evaluate("creator", values)["net"]

        self.assertGreater(net_at(band["best_below"]), net_at(band["floor"]))
        self.assertAlmostEqual(net_at(band["top"]), band["floor"], places=6)

    def test_a_clean_creator_deal_clears_every_gate(self) -> None:
        self.assertEqual(model_affiliate.blocking(self.rows), 0,
                         [row["gate"] for row in self.rows if not row["pass"]])
        self.assertEqual(len(self.rows), 12)
        for row in self.rows:
            self.assertIn(row["severity"], ("critical", "high", "medium", "low"), row["gate"])
            self.assertGreater(len(row["why"].split()), 20, row["gate"])

    def test_a_clean_seller_deal_clears_every_gate_on_its_own_inputs(self) -> None:
        """Two sides, two different subtractions, and the creator-only gates must not fire on a seller
        deal that legitimately has no service fee or withholding in it."""
        deal = self.parse(self.SELLER)
        result = model_affiliate.compute("seller", deal)
        rows = model_affiliate.gates("seller", result, self.AS_OF)
        self.assertTrue(result["computable"])
        self.assertEqual(model_affiliate.blocking(rows), 0,
                         [row["gate"] for row in rows if not row["pass"]])
        names = {row["gate"] for row in rows}
        self.assertIn("contribution-survives-commission", names)
        self.assertNotIn("net-beats-the-cost-of-making-the-content", names)

    def test_the_headline_rate_is_not_what_arrives(self) -> None:
        """The whole reason the unit exists. The rate is charged on ordered value and paid on settled
        value, with four deductions between, so the take rate has to land materially below the
        headline commission on every reading."""
        centre = self.result["base"]
        self.assertLess(self.result["take_rate_centre"], self.deal["commission_rate"]["low"])
        self.assertLess(centre["settled"], self.deal["gmv"]["low"])
        self.assertLess(centre["after_fee"], centre["commission"])
        self.assertLess(centre["net"], centre["after_fee"])

    def test_a_missing_return_rate_is_refused_rather_than_defaulted(self) -> None:
        """Nothing here may assume zero returns. The programme terms void commission on cancelled,
        refused and returned orders, so a model without the rate is wrong by the rate."""
        lines = [line for line in self.CLEAN.splitlines(keepends=True)
                 if not line.lstrip('"').startswith("return_rate,")]
        rows = self.creator("".join(lines))
        failed = {row["gate"] for row in rows if not row["pass"]}
        self.assertIn("return-rate-is-stated", failed)
        self.assertIn("model-is-complete", failed)
        for gate in ("return-rate-is-stated", "model-is-complete"):
            row = next(r for r in rows if r["gate"] == gate)
            self.assertEqual(row["severity"], "critical")

    def test_an_incomplete_deal_still_gets_graded_and_prints_no_total(self) -> None:
        """The failure mode this replaces is a traceback, and the one it must not become is a total
        computed as though the absent input were zero."""
        lines = [line for line in self.CLEAN.splitlines(keepends=True)
                 if not line.lstrip('"').startswith("content_cost,")]
        deal = self.parse("".join(lines))
        result = model_affiliate.compute("creator", deal)
        self.assertFalse(result["computable"])
        self.assertEqual(result["missing"], ["content_cost"])
        self.assertNotIn("centre", result)
        rows = model_affiliate.gates("creator", result, self.AS_OF)
        self.assertEqual(len(rows), 12)
        cost = next(r for r in rows if r["gate"] == "net-beats-the-cost-of-making-the-content")
        self.assertFalse(cost["pass"])
        self.assertIn("free labour", cost["why"])

    def test_a_superseded_service_fee_or_floor_is_caught(self) -> None:
        """Both stale figures are still live on their own Shopee URLs with no superseded label, so the
        realistic way into a model is a search, not carelessness."""
        stale_fee = self.CLEAN.replace("service_fee,0.0098,0.0098", "service_fee,0.01,0.01")
        failed = {row["gate"] for row in self.creator(stale_fee) if not row["pass"]}
        self.assertIn("service-fee-is-the-current-one", failed)
        stale_floor = self.CLEAN.replace("withholding_floor,250000,250000",
                                         "withholding_floor,2000000,2000000")
        rows = self.creator(stale_floor)
        failed = {row["gate"] for row in rows if not row["pass"]}
        self.assertIn("withholding-floor-is-the-current-one", failed)

    def test_an_undocumented_attribution_window_does_not_pass_as_declared(self) -> None:
        """Seven and thirty are the two windows anybody published. A fourteen is a compromise somebody
        made up, and a range is an assumption hidden rather than made."""
        for value in ("14,14", "7,30"):
            rows = self.creator(self.CLEAN.replace("attribution_window_days,7,7",
                                                   f"attribution_window_days,{value}"))
            failed = {row["gate"] for row in rows if not row["pass"]}
            self.assertIn("attribution-window-is-declared", failed, value)
        self.assertEqual(sorted(model_affiliate.DOCUMENTED_WINDOWS), [7, 30])

    def test_an_unsourced_input_blocks_before_any_number_is_believed(self) -> None:
        rows = self.creator(self.CLEAN.replace("https://example.org/recon", ""))
        failed = [row for row in rows if not row["pass"]]
        self.assertIn("every-input-sourced", {row["gate"] for row in failed})
        row = next(r for r in failed if r["gate"] == "every-input-sourced")
        self.assertEqual(row["severity"], "critical")
        self.assertIn("return_rate", row["observed"])

    def test_a_year_old_source_is_stale_and_says_how_old(self) -> None:
        rows = self.creator(self.CLEAN.replace("recon,2026-07-01", "recon,2024-01-01"))
        row = next(r for r in rows if r["gate"] == "sources-are-not-stale")
        self.assertFalse(row["pass"])
        self.assertIn("return_rate", row["observed"])
        self.assertIn("days ago", row["observed"])

    def test_a_single_point_commission_asserts_a_precision_nobody_publishes(self) -> None:
        """Shopee's own page says both commission types are set by algorithm and may change, so a
        point estimate is a claim the platform contradicts."""
        rows = self.creator(self.CLEAN.replace("commission_rate,0.08,0.12",
                                               "commission_rate,0.1,0.1"))
        row = next(r for r in rows if r["gate"] == "the-uncertain-inputs-are-ranges")
        self.assertFalse(row["pass"])
        self.assertIn("commission_rate", row["observed"])

    def test_the_spread_shares_partition_the_total_and_name_the_driver(self) -> None:
        shares = model_affiliate.shares_of_spread("creator", self.result)
        self.assertAlmostEqual(sum(row["share"] for row in shares), 1.0, places=6)
        self.assertEqual([row["share"] for row in shares],
                         sorted((row["share"] for row in shares), reverse=True))
        # gmv is entered as a point here, so it can own none of the spread.
        self.assertEqual(next(r["share"] for r in shares if r["parameter"] == "gmv"), 0.0)

    def test_a_floor_inside_the_range_names_what_would_settle_it(self) -> None:
        inside = model_affiliate.resolve_against(
            "creator", self.result, (self.result["low"] + self.result["high"]) / 2)
        self.assertTrue(inside["straddles"])
        self.assertEqual(inside["verdict"], "unresolved")
        below = model_affiliate.resolve_against("creator", self.result, self.result["low"] - 1)
        self.assertFalse(below["straddles"])
        self.assertEqual(below["verdict"], "above on every reading")
        self.assertEqual(below["settled_by"], [])

    def test_the_reference_carries_the_deduction_chain_the_script_computes(self) -> None:
        """The table in `affiliate-commerce.md` is a worked example, which makes it a claim about this
        code. If the arithmetic moves, the prose is wrong and nobody reading it would know."""
        text = (SKILL_ROOT / "references" / "affiliate-commerce.md").read_text(encoding="utf-8")
        for step in ("Ordered", "Settled", "Commission", "Service fee", "Withholding", "Content cost"):
            self.assertIn(step, text)
        for figure in ("100,000,000", "85,000,000", "8,500,000", "8,416,700", "7,575,030",
                       "5,575,030"):
            self.assertIn(figure, text)
        # Recompute the chain the table states, at the rates the script holds.
        settled = 100_000_000 * (1 - 0.15)
        commission = settled * 0.10
        after_fee = commission * (1 - model_affiliate.SERVICE_FEE_CURRENT)
        withheld = after_fee * model_affiliate.WITHHOLDING_RATE
        self.assertEqual(round(settled), 85_000_000)
        self.assertEqual(round(commission), 8_500_000)
        self.assertEqual(round(after_fee, -2), 8_416_700)
        self.assertEqual(round(after_fee - withheld, -1), 7_575_030)

    def test_the_law_table_separates_a_finding_from_a_rule(self) -> None:
        """Six rows carry no number because the finding is that no instrument establishes one. Those
        must never read as rules, and the three that are open questions must never read as answers -
        that is the difference between advising a client and inventing a duty for them."""
        with io.open(SKILL_ROOT / "data" / "vn-advertising-law.csv", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        findings = [row for row in rows if row["unit"] == "finding"]
        self.assertGreaterEqual(len(findings), 6)
        self.assertIn("no-follower-threshold", {row["id"] for row in rows})
        for row in rows:
            self.assertTrue(row["source_url"].startswith("https://congbao.chinhphu.vn"), row["id"])
            self.assertTrue(row["what_it_does_not_establish"].strip(), row["id"])
            self.assertGreater(len(row["what_it_actually_says"].split()), 15, row["id"])
        # No instrument prescribes disclosure wording, and the skill must not claim one does.
        creator = (SKILL_ROOT / "references" / "creator-ugc.md").read_text(encoding="utf-8")
        self.assertIn("No wording is prescribed", creator)
        for name in ("affiliate-commerce.md", "creator-ugc.md"):
            text = (SKILL_ROOT / "references" / name).read_text(encoding="utf-8")
            self.assertNotIn("must include the phrase", text)

class ClaimEvidenceTests(unittest.TestCase):
    """What has to be pinned here is the boundary between what a regex decided and what a person did.

    `claims-proof-ledger.md` taught the substantiation question and then handed the Vietnamese
    instrument back to a Vietnamese marketer. The rebuilt unit answers it, which creates two new ways
    to be wrong. A regex over Vietnamese can invent an offence, because `nhat` is both the superlative
    marker and a bound syllable in `thong nhat` - so the false friends are tested by name. And an
    answer sheet can be read as clearance, so the tests assert that silence fails rather than passes,
    and that the sheet never asks a question the scanner already answered.

    The arithmetic in the prose is a claim about the table, so it is recomputed rather than trusted.
    """

    AS_OF = "2026-07-31"
    REFERENCE = SKILL_ROOT / "references" / "claims-proof-ledger.md"
    # The draft that produced the figure quoted in the reference. Kept here rather than in a fixture
    # file so the number in the prose and the input that yields it cannot drift apart.
    SERUM = ("# Serum Vitamin C Glow - bai dang ra mat\n\n"
             "Serum Vitamin C tốt nhất thị trường Việt Nam hiện nay, được bác sĩ da liễu tại phòng "
             "khám\nThẩm mỹ Sài Gòn khuyên dùng.\n\n"
             "Công thức đặc trị nám và kháng viêm, cho hiệu quả rõ rệt sau 7 ngày. Sáng hơn hẳn so "
             "với\ncác loại serum cùng giá.\n\n"
             "Hai bên đã thống nhất giá bán lẻ 390.000đ và giữ nhất quán trên mọi sàn.\n")

    @classmethod
    def setUpClass(cls) -> None:
        cls.ledger = check_claims.read_ledger()
        cls.prose = cls.REFERENCE.read_text(encoding="utf-8")

    def filled_sheet(self, sector: str) -> dict:
        """Every question on the sector's sheet answered the way a diligent person would answer it."""
        return {row["id"]: {"claim_id": row["id"],
                            "status": "absent" if row["id"] in check_claims.MUST_BE_ABSENT
                                      else "present",
                            "document": "Phieu cong bo", "issued_by": "So Y te",
                            "reference": "12345/20/CBMP-HN", "expires": "2030-01-01",
                            "verified_at": self.AS_OF}
                for row in check_claims.rows_needing_an_answer(self.ledger, sector)}

    def test_self_check_passes(self) -> None:
        report = check_claims.self_check()
        self.assertIn("All assertions passed.", report)
        self.assertNotIn("FAIL", report)

    def test_every_row_is_cited_to_the_gazette_at_a_date(self) -> None:
        """A band without an instrument behind it is a number somebody remembered. Every row carries
        the decree, the article, the gazette URL and the day it was read, because the whole unit is
        an argument from the text and the reader has to be able to go and check it."""
        for row in self.ledger:
            self.assertEqual(row["instrument"], "Nghị định 87/2026/NĐ-CP", row["id"])
            self.assertTrue(row["article"].startswith("Điều "), (row["id"], row["article"]))
            self.assertTrue(row["source_url"].startswith("https://congbao.chinhphu.vn/"), row["id"])
            self.assertEqual(row["verified_at"], "2026-07-31", row["id"])
            self.assertGreater(row["fine_high"], 0, row["id"])
            self.assertGreaterEqual(row["fine_high"], row["fine_low"], row["id"])

    def test_every_regex_fires_on_a_trigger_the_table_declares(self) -> None:
        """`trigger_vi` is what a reader consults and `detect_regex` is what the machine runs, so a
        row where the two disagree documents a check that is not the one being made. Three rows had
        exactly that: `asset-advertising` advertised itself as `quang cao tai san` while the scanner
        looked for `can ho` and `so do`. The tokens now sit in the trigger cell beside the
        description."""
        for row in self.ledger:
            if row["detect_regex"] == "-":
                continue
            pattern = re.compile(row["detect_regex"])  # also asserts it compiles
            tokens = [token.strip() for token in row["trigger_vi"].split(";")]
            tokens += [token.strip() for token in row["trigger_en"].split(";")]
            self.assertTrue(any(pattern.search(token) for token in tokens),
                            f"{row['id']}: no declared trigger fires its own regex")

    def test_the_false_friends_do_not_fire_the_superlative_row(self) -> None:
        """`nhat` carries the superlative in `tot nhat` and carries nothing at all in `thong nhat`,
        `nhat quan`, `nhat dinh`. A scanner blind to that fires on every second paragraph of ordinary
        commercial Vietnamese, which trains the reader to ignore it."""
        for phrase in check_claims.FALSE_FRIENDS:
            sentence = f"Hai bên đã {phrase} về điều khoản này trong hợp đồng."
            hits = [hit["id"] for hit in check_claims.scan(sentence, self.ledger, "general")]
            self.assertNotIn("superlative", hits, f"{phrase!r} should not read as a superlative")
        real = "Kem dưỡng tốt nhất thị trường, thương hiệu số 1 Việt Nam."
        self.assertEqual([hit["id"] for hit in
                          check_claims.scan(real, self.ledger, "general")], ["superlative"])
        # And masking preserves length, so the line numbers in the report still point at the copy.
        text = "Hai bên đã thống nhất giá.\nKem tốt nhất thị trường."
        self.assertEqual(len(check_claims.mask_false_friends(text)), len(text))
        self.assertEqual(check_claims.scan(text, self.ledger, "general")[0]["line"], 2)

    def test_a_prohibition_bound_to_one_sector_stays_bound_to_it(self) -> None:
        """The defect this replaces was found by running the tool, not by reading it. `bác sĩ` fired
        both the cosmetics article and the device article on a serum post, so the audit invented an
        offence and printed 20 million more exposure than the copy could incur. Điều 70.3.c binds
        cosmetics, Điều 73.3 binds devices, and no article bans a doctor in a food advertisement."""
        doctor = "Được bác sĩ da liễu tại phòng khám khuyên dùng."
        self.assertEqual([hit["id"] for hit in check_claims.scan(doctor, self.ledger, "cosmetics")],
                         ["banned-medical-staff-cosmetics"])
        self.assertEqual([hit["id"] for hit in check_claims.scan(doctor, self.ledger, "device")],
                         ["banned-medical-staff-device"])
        self.assertEqual(check_claims.scan(doctor, self.ledger, "food"), [])
        # The four closed categories are the exception: they apply whatever sector was declared,
        # because a draft naming a vape is advertising one regardless of the flag passed in.
        for sector in ("general", "food", "cosmetics"):
            hits = [hit["id"] for hit in
                    check_claims.scan("Ưu đãi thuốc lá điện tử cuối tuần.", self.ledger, sector)]
            self.assertEqual(hits, ["banned-tobacco"], sector)
        for row in self.ledger:
            if row["claim_family"] in check_claims.UNIVERSAL_PROHIBITIONS:
                self.assertEqual(row["verdict"], "prohibited_outright", row["id"])

    def test_every_sector_gets_the_same_fourteen_gates(self) -> None:
        """A gate that disappears for a sector is a check nobody notices going missing. They all run
        for every sector; `applies` is what varies, and it is reported."""
        for sector in check_claims.SECTORS:
            rows = check_claims.gates(self.ledger, sector, [], {}, self.AS_OF)
            self.assertEqual(len(rows), 14, sector)
            self.assertEqual(len({row["gate"] for row in rows}), 14, sector)
            for row in rows:
                self.assertIn(row["severity"], check_claims.SEVERITY_ORDER, row["gate"])
                self.assertIn(row["reads"], ("ledger", "draft", "answers", "draft and answers"),
                              row["gate"])
                self.assertGreater(len(row["why"].split()), 25, (sector, row["gate"]))
                self.assertEqual(row["claim_ids"], list(dict.fromkeys(row["claim_ids"])),
                                 f"{row['gate']} lists a claim id twice")

    def test_an_unanswered_sheet_fails_and_a_filled_one_clears(self) -> None:
        """The load-bearing decision in the unit. Six gates read a sheet instead of the copy, and an
        empty cell has to fail, because the alternative is a report that goes green on the strength
        of nobody having looked. `no-expired-approval` is the single gate an empty sheet may clear:
        nothing named is nothing lapsed."""
        empty = check_claims.gates(self.ledger, "cosmetics", [], {}, self.AS_OF)
        sheet_gates = [row for row in empty
                       if row["applies"] and row["reads"].endswith("answers")]
        self.assertEqual(len(sheet_gates), 7)
        self.assertEqual(sum(1 for row in sheet_gates if not row["pass"]), 6)
        for row in sheet_gates:
            if row["gate"] == "no-expired-approval":
                self.assertTrue(row["pass"])
                continue
            self.assertFalse(row["pass"], f"{row['gate']} passed on an empty sheet")
        answered = check_claims.gates(self.ledger, "cosmetics", [], self.filled_sheet("cosmetics"),
                                      self.AS_OF)
        self.assertEqual(check_claims.failed(answered), 0,
                         [row["gate"] for row in answered if row["applies"] and not row["pass"]])
        # A status with no paper behind it is not an answer either.
        vague = {key: dict(value, document="", reference="", issued_by="")
                 for key, value in self.filled_sheet("cosmetics").items()}
        self.assertGreater(check_claims.failed(
            check_claims.gates(self.ledger, "cosmetics", [], vague, self.AS_OF)), 0)

    def test_a_lapsed_approval_fails_where_a_missing_one_would(self) -> None:
        """Điều 70.4.a treats an expired Phiếu công bố receipt exactly like an absent one, and a
        campaign cleared in March and still running in November is the ordinary way that happens."""
        sheet = self.filled_sheet("cosmetics")
        sheet["cosmetic-notice-number"] = dict(sheet["cosmetic-notice-number"],
                                               expires="2026-01-01")
        rows = check_claims.gates(self.ledger, "cosmetics", [], sheet, self.AS_OF)
        stale = next(row for row in rows if row["gate"] == "no-expired-approval")
        self.assertFalse(stale["pass"])
        self.assertIn("cosmetic-notice-number", stale["claim_ids"])
        # The day itself is the boundary: expiring today is expired.
        today = dict(sheet)
        today["cosmetic-notice-number"] = dict(sheet["cosmetic-notice-number"], expires=self.AS_OF)
        self.assertTrue(check_claims.expired(today["cosmetic-notice-number"], self.AS_OF))

    def test_the_sheet_asks_only_what_the_scanner_cannot_read(self) -> None:
        """Two answers to one question is worse than one, because the sheet and the draft can
        disagree and the sheet is the one a person signed. So a row the regex decides is not asked,
        with five deliberate exceptions in `ALWAYS_ASK` where the copy cannot show what matters -
        whether a real face is in the shot, whether the warning is legible at shipping size."""
        for sector in check_claims.SECTORS:
            wanted = check_claims.rows_needing_an_answer(self.ledger, sector)
            ids = [row["id"] for row in wanted]
            self.assertEqual(len(ids), len(set(ids)), sector)
            for row in wanted:
                self.assertIn(row["id"], {ledger_row["id"] for ledger_row in self.ledger})
                if row["detect_regex"] != "-":
                    self.assertIn(row["id"], check_claims.ALWAYS_ASK + check_claims.MUST_BE_ABSENT,
                                  f"{row['id']} is scannable and is being asked as well")
                self.assertNotIn(row["id"], check_claims.NO_ANSWER_DISCHARGES, row["id"])
            template = check_claims.build_template(self.ledger, sector)
            self.assertIn(",".join(check_claims.ANSWER_COLUMNS), template)
            for row_id in ids:
                self.assertIn(row_id, template)
        # Điều 53.2 is the catch-all that names no test, so signing for it would read as clearance.
        for row_id in check_claims.NO_ANSWER_DISCHARGES:
            self.assertIn(row_id, {row["id"] for row in self.ledger})
            self.assertNotIn(row_id, check_claims.build_template(self.ledger, "general"))

    def test_the_sheet_it_writes_is_a_sheet_it_can_read(self) -> None:
        """Found by running the documented workflow end to end. `--template` writes a blank line
        between its instructions and its header; `csv.DictReader` takes the first line handed to it as
        the field names, so the tool rejected the file it had just written and told the user to run
        `--template` to get the right shape. A blank sheet has to parse and then fail, not error."""
        with tempfile.TemporaryDirectory() as folder:
            sheet = Path(folder) / "answers.csv"
            sheet.write_text(check_claims.build_template(self.ledger, "food"), encoding="utf-8")
            answers = check_claims.read_answers(sheet)
            self.assertEqual(sorted(answers),
                             sorted(row["id"] for row in
                                    check_claims.rows_needing_an_answer(self.ledger, "food")))
            for answer in answers.values():
                self.assertEqual(answer["status"], "")
                self.assertFalse(check_claims.documented(answer))
            rows = check_claims.gates(self.ledger, "food", [], answers, self.AS_OF)
            self.assertGreater(check_claims.blocking(rows), 0,
                               "a sheet with every status blank must not clear the answer gates")
            # A status the vocabulary does not contain is refused rather than silently ignored.
            sheet.write_text("claim_id,status\nfood-identity-block,probably\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                check_claims.read_answers(sheet)

    def test_the_four_refused_sectors_are_refused_by_article(self) -> None:
        """Medicine, chemicals and plant protection each carry their own article, their own documents
        and their own bands, none of which is in this table. A partial answer there reads as
        clearance, so the gate fails and names what would have to be read instead."""
        for sector, expected in check_claims.OUT_OF_SCOPE.items():
            rows = check_claims.gates(self.ledger, sector, [], {}, self.AS_OF)
            covered = next(row for row in rows if row["gate"] == "sector-is-covered-by-this-table")
            self.assertFalse(covered["pass"], sector)
            self.assertEqual(covered["severity"], "critical", sector)
            self.assertIn("Dieu", covered["observed"], sector)
            self.assertIn(expected.split()[1], covered["observed"], sector)
        with self.assertRaises(ValueError):
            check_claims.families_for("cars")

    def test_the_verdict_table_in_the_reference_is_recomputed_from_the_csv(self) -> None:
        """Five verdicts, and the reference prints a row count and a worst band for each. Both are
        derived figures, so they rot the first time a row is added. `form_prescribed` was printed at
        20 million while the two Điều 53.2 rows in it reach 40."""
        for verdict in check_claims.VERDICTS:
            rows = [row for row in self.ledger if row["verdict"] == verdict]
            self.assertGreater(len(rows), 0, verdict)
            worst = max(row["fine_high"] for row in rows)
            line = next((candidate for candidate in self.prose.splitlines()
                         if candidate.startswith(f"| `{verdict}`")), None)
            self.assertIsNotNone(line, f"{verdict} is not in the reference table")
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            self.assertEqual(cells[2], str(len(rows)), f"{verdict}: row count in the prose")
            self.assertEqual(cells[3], f"{worst:,}", f"{verdict}: worst band in the prose")
        # And the claim made about that table: one verdict carries the highest band in the decree.
        highest = max(row["fine_high"] for row in self.ledger)
        self.assertEqual(highest, max(row["fine_high"] for row in self.ledger
                                      if row["verdict"] == "must_match_filing"))

    def test_the_exposure_figure_in_the_reference_is_the_sum_of_the_bands(self) -> None:
        """The number in the prose is the argument of the whole unit, so it is recomputed by running
        the audit on the draft that produced it. Fines stack under Điều 4, which is why a single
        non-compliant serum post reaches a figure a marketer will not believe until it is itemised."""
        with tempfile.TemporaryDirectory() as folder:
            draft = Path(folder) / "serum.md"
            draft.write_text(self.SERUM, encoding="utf-8")
            hits = check_claims.scan(self.SERUM, self.ledger, "cosmetics")
            rows = check_claims.gates(self.ledger, "cosmetics", hits, {}, self.AS_OF)
            report = check_claims.render(self.ledger, "cosmetics", str(draft), hits, rows,
                                        self.AS_OF)
        self.assertEqual({hit["id"] for hit in hits},
                         {"superlative", "comparative-named-rival", "banned-cosmetic-as-drug",
                          "banned-medical-staff-cosmetics"})
        exposed = sorted({claim_id for row in rows if row["applies"] and not row["pass"]
                          for claim_id in row["claim_ids"]})
        low, high = check_claims.exposure(self.ledger, exposed)
        self.assertEqual((low, high), (345_000_000, 505_000_000))
        self.assertEqual(len(exposed), 16)
        self.assertIn("345 to 505 million VND across sixteen rows", self.prose)
        self.assertIn(f"{low:,} to {high:,} VND", report)
        # The two false friends in the same draft stay out of the total.
        self.assertNotIn("thống nhất", report)

    def test_the_bands_agree_with_the_wider_law_table(self) -> None:
        """`data/vn-advertising-law.csv` and `data/claim-evidence.csv` both cite Nghị định
        87/2026/NĐ-CP, and three articles appear in both. The law table stores a band as a `value`
        string with a separate `unit`, so the two files record the same fine in two shapes - which is
        exactly the arrangement where one gets corrected and the other does not."""
        with io.open(SKILL_ROOT / "data" / "vn-advertising-law.csv", encoding="utf-8-sig") as handle:
            law = list(csv.DictReader(handle))
        ledger = {}
        for row in self.ledger:
            ledger.setdefault(row["article"], []).append(row)
        shared = 0
        for row in law:
            if row["unit"] != "VND" or row["article"] not in ledger:
                continue
            band = re.fullmatch(r"(\d+) to (\d+)", row["value"].strip())
            if not band:
                continue
            shared += 1
            low, high = int(band.group(1)), int(band.group(2))
            for claim in ledger[row["article"]]:
                self.assertEqual((claim["fine_low"], claim["fine_high"]), (low, high),
                                 f"{claim['id']} and {row['id']} cite {row['article']} differently")
        self.assertGreaterEqual(shared, 3, "the two tables stopped overlapping; check the articles")

    def test_the_reference_names_the_instruments_it_leans_on(self) -> None:
        """The old file's defect was nationality: it taught the FTC substantiation question and handed
        the Vietnamese decree back to the reader. So the articles the unit actually turns on have to
        appear in the prose, and the FTC links may stay only as the outside-Vietnam note."""
        for article in ("Điều 50.5.c", "Điều 70.3.c", "Điều 70.4.a", "Điều 71.4", "Điều 73.3",
                        "Điều 53.1.b", "Điều 50.3.a", "Điều 69"):
            self.assertIn(article, self.prose, f"{article} carries a gate and is not explained")
        self.assertIn("scripts/check_claims.py", self.prose)
        self.assertIn("data/claim-evidence.csv", self.prose)
        head = self.prose.split("## Working outside Vietnam")[0]
        self.assertNotIn("https://www.ftc.gov", head,
                         "the FTC links are back above the Vietnamese law")
        for name in re.findall(r"references/([a-z0-9-]+\.md)", self.prose):
            self.assertTrue((SKILL_ROOT / "references" / name).exists(), name)

    def test_the_cli_refuses_a_bad_call_and_exits_two_on_a_failing_gate(self) -> None:
        """Exit 2 is the whole point of the tool in a pipeline: a draft that fails a blocking gate has
        to stop the run rather than print a warning into a log nobody reads."""
        with tempfile.TemporaryDirectory() as folder:
            draft = Path(folder) / "serum.md"
            draft.write_text(self.SERUM, encoding="utf-8")
            clean = Path(folder) / "clean.md"
            clean.write_text("Serum dưỡng sáng da, dùng buổi sáng và buổi tối.\n", encoding="utf-8")
            sheet = Path(folder) / "answers.csv"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(check_claims.main(
                    ["--template", str(sheet), "--sector", "cosmetics"]), 0)
                self.assertEqual(check_claims.main(
                    ["--audit", str(draft), "--sector", "cosmetics"]), 2)
                with contextlib.redirect_stderr(io.StringIO()) as complaint:
                    self.assertEqual(check_claims.main(
                        ["--audit", str(clean), "--sector", "spaceflight"]), 1)
            self.assertIn("unknown sector", complaint.getvalue())
            rows = list(csv.DictReader(
                line for line in sheet.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.lstrip().startswith("#")))
            self.assertEqual([row["claim_id"] for row in rows],
                             [row["id"] for row in
                              check_claims.rows_needing_an_answer(self.ledger, "cosmetics")])
            # A sheet answered in full turns the same draft's answer gates green and leaves the copy
            # failures standing, which is the split the unit is built on.
            with io.open(sheet, "w", encoding="utf-8", newline="") as handle:
                handle.write(",".join(check_claims.ANSWER_COLUMNS) + "\n")
                for row in rows:
                    answer = self.filled_sheet("cosmetics")[row["claim_id"]]
                    handle.write(",".join(answer[column]
                                          for column in check_claims.ANSWER_COLUMNS) + "\n")
            with contextlib.redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(check_claims.main(
                    ["--audit", str(draft), "--sector", "cosmetics", "--answers", str(sheet)]), 2)
            self.assertIn("nothing-in-the-prohibited-list", printed.getvalue())

if __name__ == "__main__":
    unittest.main()
