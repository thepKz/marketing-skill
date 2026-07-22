#!/usr/bin/env python3
"""Focused tests for the deterministic Marketing-Minthep tools."""

from __future__ import annotations

import csv
import io
import unittest

from analyze_performance import analyze
from build_asset_manifest import build_manifest
from compile_prompt import compile_provider
from plan_image_generation import route_image_request
from plan_marketing_system import plan_marketing_system
from plan_virtual_person import plan_virtual_person
from scaffold_campaign import build_record
from score_creative import evaluate


class ToolTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
