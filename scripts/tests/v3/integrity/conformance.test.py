#!/usr/bin/env python3
"""Reproduce every frozen M1C literal with the independent reference oracle."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
SCHEMA_TEST_PATH = HERE / "schema.test.py"
ORACLE_PATH = HERE / "reference_oracle.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schema_gate = load_module("m1c_conformance_schema", SCHEMA_TEST_PATH)
oracle = load_module("m1c_reference_oracle", ORACLE_PATH)


class M1CConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = sorted(FIXTURES.glob("F-M1C-*.json"))
        cls.bundles = [schema_gate.strict_loads(path.read_bytes()) for path in cls.paths]

    def test_all_literal_outputs_reproduce_twice(self) -> None:
        self.assertEqual(len(self.bundles), 24)
        for bundle in self.bundles:
            expected_bytes = schema_gate.canonical_bytes(bundle["expected"])
            first = oracle.evaluate_bundle(bundle)
            second = oracle.evaluate_bundle(bundle)
            with self.subTest(fixture=bundle["fixture_id"]):
                self.assertEqual(schema_gate.canonical_bytes(first), expected_bytes)
                self.assertEqual(schema_gate.canonical_bytes(second), expected_bytes)

    def test_oracle_outputs_validate_as_closed_decisions(self) -> None:
        definitions = {
            "EvidenceFixtureBundle@1": "EvidenceDecision",
            "EffectFixtureBundle@1": "EffectDecision",
            "PublicationFixtureBundle@1": "PublicationDecision",
            "StateFixtureBundle@1": "StateDecision",
            "RetentionFixtureBundle@1": "RetentionDecision",
        }
        for bundle in self.bundles:
            with self.subTest(fixture=bundle["fixture_id"]):
                schema_gate.validate(oracle.evaluate_bundle(bundle), definitions[bundle["type"]])

    def test_status_inventory_is_exact(self) -> None:
        expected = {
            "F-M1C-001": "supported", "F-M1C-002": "unknown",
            "F-M1C-003": "unknown", "F-M1C-004": "contested",
            "F-M1C-005": "refused", "F-M1C-006": "prepared",
            "F-M1C-007": "succeeded", "F-M1C-008": "ambiguous",
            "F-M1C-009": "ambiguous", "F-M1C-010": "refused",
            "F-M1C-011": "eligible", "F-M1C-012": "blocked",
            "F-M1C-013": "blocked", "F-M1C-014": "blocked",
            "F-M1C-015": "ambiguous", "F-M1C-016": "eligible",
            "F-M1C-017": "blocked", "F-M1C-018": "recovery-required",
            "F-M1C-019": "blocked", "F-M1C-020": "blocked",
            "F-M1C-021": "complete", "F-M1C-022": "incomplete",
            "F-M1C-023": "blocked", "F-M1C-024": "blocked",
        }
        actual = {
            bundle["fixture_id"]: oracle.evaluate_bundle(bundle)["status"]
            for bundle in self.bundles
        }
        self.assertEqual(actual, expected)

    def test_oracle_carries_zero_side_effect_counters(self) -> None:
        for bundle in self.bundles:
            decision = oracle.evaluate_bundle(bundle)
            counters = {
                key: item
                for key, item in decision.items()
                if key.endswith("_count")
            }
            with self.subTest(fixture=bundle["fixture_id"]):
                if bundle["type"] == "EvidenceFixtureBundle@1":
                    self.assertFalse(counters)
                    continue
                self.assertTrue(counters)
                self.assertEqual(set(counters.values()), {0})


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(M1CConformanceTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("M1C_CONFORMANCE_PASS bundles=24 runs=2")
    raise SystemExit(0 if result.wasSuccessful() else 1)
