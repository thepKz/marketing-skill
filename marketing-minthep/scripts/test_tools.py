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

from analyze_performance import analyze
from build_asset_manifest import build_manifest
from compile_prompt import compile_provider
from new_run import build_run, load_registry, route_pipeline, write_run
from plan_image_generation import route_image_request
from plan_design_options import plan_options
from plan_marketing_system import plan_marketing_system
from plan_virtual_person import plan_virtual_person
from render_mockup import FONTS_WITHOUT_VIETNAMESE, SANS, SERIF, render
from research_plan import build_plan, to_markdown
from run_status import audit_file, audit_run
from scaffold_campaign import build_record
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
        must stay clear of both ends or be dropped entirely."""
        base = {"theme": "heritage-craft", "title": "Bún bò", "width": 1080, "height": 1080}
        crowded = render({
            **base,
            "items": [{"name": "Bún bò Huế đặc biệt thêm giò heo và chả cua", "price": "129.000đ"}],
        })
        leaders = [node for node in ET.fromstring(crowded).iter() if node.get("stroke-dasharray")]
        # A name this long leaves no honest room, so drawing nothing is the correct output.
        self.assertEqual(leaders, [], "leader drawn where there is no room for it")
        roomy = render({**base, "items": [{"name": "Bún bò", "price": "79.000đ"}]})
        leaders = [node for node in ET.fromstring(roomy).iter() if node.get("stroke-dasharray")]
        self.assertEqual(len(leaders), 1, "a short name should get a leader")
        margin = round(1080 * 0.0972)
        self.assertGreater(float(leaders[0].get("x1")), margin, "leader starts inside the name")
        self.assertLess(float(leaders[0].get("x2")), 1080 - margin, "leader crosses the margin")

    def test_scaffold_v3_separates_job_and_artifact_mode(self) -> None:
        record = build_record("Launch", "product", "beauty", "gpt-image-2", ["meta", "web"])
        self.assertEqual(record["schema_version"], 3)
        self.assertEqual(record["primary_job"], "campaign-launch")
        self.assertEqual(record["artifact_mode"], "product")
        self.assertEqual([lane["name"] for lane in record["concept_lanes"]], ["Clear", "Signature", "Departure"])
        self.assertGreater(len(record["assets"]), 3)

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
        value = _frontmatter_description(skill)
        self.assertLess(len(value), 200, f"description is {len(value)} chars")

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
