#!/usr/bin/env python3
"""Focused tests for the deterministic Marketing Creative Director tools."""

from __future__ import annotations

import csv
import io
import unittest

from analyze_performance import analyze
from build_asset_manifest import build_manifest
from compile_prompt import RAW_HUMAN_OPENING, compile_provider
from scaffold_campaign import build_record
from score_creative import evaluate


class ToolTests(unittest.TestCase):
    def test_scaffold_v2(self) -> None:
        record = build_record("Launch", "product", "beauty", "openai", ["meta", "web"])
        self.assertEqual(record["schema_version"], 2)
        self.assertEqual([lane["name"] for lane in record["concept_lanes"]], ["Clear", "Signature", "Departure"])
        self.assertGreater(len(record["assets"]), 3)

    def test_human_prompt_has_raw_opening(self) -> None:
        prompt = compile_provider({"mode": "human", "brief": {"objective": "Lip tint lifestyle"}}, "openai")
        self.assertIn(RAW_HUMAN_OPENING, prompt)
        self.assertIn("K-pop-inspired makeup", prompt)

    def test_provider_compilers(self) -> None:
        record = {"mode": "product", "brief": {"objective": "Product hero"}}
        for provider in ("generic", "openai", "midjourney", "flux", "ideogram", "firefly"):
            self.assertIn("PROVIDER:", compile_provider(record, provider))

    def test_manifest_lineage(self) -> None:
        rows = build_manifest({"project": "Barrier Reset", "selected_lanes": ["signature"]}, ["meta"])
        self.assertEqual(len(rows), 3)
        self.assertTrue(rows[0]["filename"].startswith("barrier-reset-signature-meta"))

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

