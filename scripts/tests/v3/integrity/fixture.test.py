#!/usr/bin/env python3
"""Literal fixture, manifest and independence gates for M1C."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
MANIFEST_PATH = FIXTURES / "manifest.json"
SCHEMA_PATH = ROOT / "schemas" / "control-plane" / "v3" / "integrity" / "schema.json"
MATERIALIZER_PATH = HERE / "materialize_fixtures.py"
SCHEMA_TEST_PATH = HERE / "schema.test.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schema_gate = load_module("m1c_schema_gate", SCHEMA_TEST_PATH)
materializer = load_module("m1c_fixture_materializer", MATERIALIZER_PATH)


def digest_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = schema_gate.strict_loads(path.read_bytes())
    if not isinstance(value, dict):
        raise AssertionError(f"{path} is not an object")
    return value


class M1CFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = read_json(MANIFEST_PATH)
        cls.paths = sorted(FIXTURES.glob("F-M1C-*.json"))
        cls.bundles = [read_json(path) for path in cls.paths]

    def test_every_bundle_and_manifest_validates(self) -> None:
        schema_gate.validate(self.manifest, "FixtureManifest")
        for bundle in self.bundles:
            with self.subTest(fixture=bundle["fixture_id"]):
                schema_gate.validate(bundle, "M1CFixtureBundle")

    def test_exact_closed_fixture_sequence(self) -> None:
        expected = [f"F-M1C-{number:03d}" for number in range(1, 25)]
        self.assertEqual([path.stem for path in self.paths], expected)
        self.assertEqual([bundle["fixture_id"] for bundle in self.bundles], expected)

    def test_fixture_lane_counts_and_types(self) -> None:
        expected_counts = {
            "EvidenceFixtureBundle@1": 5, "EffectFixtureBundle@1": 5,
            "PublicationFixtureBundle@1": 5, "StateFixtureBundle@1": 5,
            "RetentionFixtureBundle@1": 4,
        }
        actual = {key: 0 for key in expected_counts}
        for bundle in self.bundles:
            self.assertIn(bundle["type"], actual)
            actual[bundle["type"]] += 1
        self.assertEqual(actual, expected_counts)

    def test_manifest_binds_schema_and_literal_bytes(self) -> None:
        self.assertEqual(self.manifest["schema_digest"], digest_bytes(SCHEMA_PATH.read_bytes()))
        self.assertEqual(len(self.manifest["fixtures"]), 24)
        for entry, path, bundle in zip(self.manifest["fixtures"], self.paths, self.bundles):
            with self.subTest(fixture=entry["fixture_id"]):
                self.assertEqual(entry["fixture_id"], bundle["fixture_id"])
                self.assertEqual(entry["path"], path.name)
                self.assertEqual(entry["bundle_type"], bundle["type"])
                self.assertEqual(entry["digest"], digest_bytes(path.read_bytes()))

    def test_materializer_is_byte_identical_and_oracle_independent(self) -> None:
        expected = materializer.build_outputs()
        self.assertEqual(set(expected), set(self.paths + [MANIFEST_PATH]))
        for path, raw in expected.items():
            self.assertEqual(path.read_bytes(), raw)
        source = MATERIALIZER_PATH.read_text(encoding="utf-8")
        self.assertNotIn("reference_oracle", source)
        self.assertNotRegex(source, r"\boracle\s*\(")

    def test_self_digest_fields_bind_exact_objects(self) -> None:
        for bundle in self.bundles:
            raw = json.dumps(bundle, sort_keys=True)
            with self.subTest(fixture=bundle["fixture_id"]):
                if "intent_digest" in raw or "event_digest" in raw or "receipt_digest" in raw or "tombstone_digest" in raw:
                    schema_gate.validate(bundle, "M1CFixtureBundle")

    def test_source_requirement_ids_are_closed(self) -> None:
        allowed = {
            "REQ-M1C-AMBIGUITY", "REQ-M1C-CONTRADICTION", "REQ-M1C-EFFECT",
            "REQ-M1C-EVIDENCE", "REQ-M1C-MIGRATION", "REQ-M1C-OWNER-SEAM",
            "REQ-M1C-PAUSE", "REQ-M1C-PRIVACY", "REQ-M1C-PROTECTED-BRANCH",
            "REQ-M1C-PUBLICATION", "REQ-M1C-REPLAY", "REQ-M1C-RETENTION",
            "REQ-M1C-SECURITY", "REQ-M1C-SINGLE-WRITER", "REQ-M1C-STATE",
            "REQ-M1C-VERIFICATION",
        }
        seen: set[str] = set()
        for bundle in self.bundles:
            identifiers = bundle["source_requirement_ids"]
            self.assertEqual(identifiers, sorted(set(identifiers)))
            self.assertTrue(set(identifiers) <= allowed)
            seen.update(identifiers)
        self.assertEqual(seen, allowed)

    def test_synthetic_privacy_and_secret_boundary(self) -> None:
        forbidden = re.compile(
            r"(?:AKIA[0-9A-Z]{16}|-----BEGIN .*PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{20,}|"
            r"sk-[A-Za-z0-9]{20,}|xox[baprs]-|C:\\Users\\|/home/|NotSkittlz|github\.com/NotSkittlz)",
            re.IGNORECASE,
        )
        for path in self.paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIsNone(forbidden.search(text))
                self.assertNotIn("example.com", text)
                self.assertIn("example.invalid", text) if path.stem <= "F-M1C-005" else None

    def test_expected_status_inventory_is_exact(self) -> None:
        expected = [
            "supported", "unknown", "unknown", "contested", "refused",
            "prepared", "succeeded", "ambiguous", "ambiguous", "refused",
            "eligible", "blocked", "blocked", "blocked", "ambiguous",
            "eligible", "blocked", "recovery-required", "blocked", "blocked",
            "complete", "incomplete", "blocked", "blocked",
        ]
        self.assertEqual([bundle["expected"]["status"] for bundle in self.bundles], expected)


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("M1C_FIXTURE_PASS bundles=24 tests=9")
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
