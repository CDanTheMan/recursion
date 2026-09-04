#!/usr/bin/env python3
"""Run the test-only M1B reference oracle against all frozen literal outcomes."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schema_support = load_module("m1b_schema_conformance", HERE / "schema.test.py")
oracle = load_module("m1b_reference_oracle", HERE / "reference_oracle.py")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


class M1BConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundles = [schema_support.strict_loads(path.read_bytes()) for path in sorted(FIXTURES.glob("F-M1B-*.json"))]

    def test_all_literal_outcomes_match_reference_oracle_twice(self) -> None:
        run_digests: list[str] = []
        for run in range(2):
            decisions = []
            for bundle in self.bundles:
                with self.subTest(run=run, fixture=bundle["fixture_id"]):
                    schema_support.validate(bundle, "M1BFixtureBundle")
                    actual = oracle.decide(bundle)
                    schema_support.validate(actual)
                    self.assertEqual(canonical_bytes(actual), canonical_bytes(bundle["expected"]))
                    if bundle["type"] == "ProcessFixtureBundle@1" and bundle["termination_observation"] is not None:
                        self.assertEqual(bundle["termination_observation"]["effect_conclusion"], "not-evaluated")
                decisions.append(actual)
            run_digests.append(hashlib.sha256(canonical_bytes(decisions)).hexdigest())
        self.assertEqual(run_digests[0], run_digests[1])

    def test_expected_status_inventory_is_closed(self) -> None:
        observed = {bundle["expected"]["status"] for bundle in self.bundles}
        self.assertEqual(observed, {"accepted", "accepted-reset", "admitted", "blocked", "refused", "resolved", "resolved-disabled", "resolved-reload", "selected"})


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("M1B_CONFORMANCE_PASS bundles=24 runs=2")
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
