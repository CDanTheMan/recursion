#!/usr/bin/env python3
"""Structural and digest gates for the frozen M1B fixture corpus."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import unittest
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIXTURES = HERE / "fixtures"
SCHEMA_PATH = ROOT / "schemas" / "control-plane" / "v3" / "execution" / "schema.json"
SCHEMA_TEST_PATH = HERE / "schema.test.py"
MATERIALIZER_PATH = HERE / "materialize_fixtures.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schema_support = load_module("m1b_schema_support", SCHEMA_TEST_PATH)


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


class M1BFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = sorted(FIXTURES.glob("F-M1B-*.json"))
        cls.bundles = [schema_support.strict_loads(path.read_bytes()) for path in cls.paths]
        cls.manifest = schema_support.strict_loads((FIXTURES / "manifest.json").read_bytes())

    def test_exact_closed_fixture_sequence(self) -> None:
        expected = [f"F-M1B-{number:03d}" for number in range(1, 25)]
        self.assertEqual([path.stem for path in self.paths], expected)
        self.assertEqual([bundle["fixture_id"] for bundle in self.bundles], expected)
        self.assertEqual(len(self.manifest["fixtures"]), 24)

    def test_every_bundle_and_manifest_validates(self) -> None:
        for bundle in self.bundles:
            with self.subTest(bundle=bundle["fixture_id"]):
                schema_support.validate(bundle, "M1BFixtureBundle")
        schema_support.validate(self.manifest, "FixtureManifest")

    def test_manifest_binds_schema_and_literal_bytes(self) -> None:
        self.assertEqual(self.manifest["schema_digest"], digest_bytes(SCHEMA_PATH.read_bytes()))
        entries = {entry["fixture_id"]: entry for entry in self.manifest["fixtures"]}
        for path, bundle in zip(self.paths, self.bundles):
            entry = entries[bundle["fixture_id"]]
            self.assertEqual(entry["path"], path.name)
            self.assertEqual(entry["digest"], digest_bytes(path.read_bytes()))
            self.assertEqual(entry["bundle_type"], bundle["type"])

    def test_self_digest_fields_bind_exact_objects(self) -> None:
        digest_fields = {
            "RouteCapabilityDescriptor@1": "descriptor_digest",
            "ProcessCapabilityDescriptor@1": "descriptor_digest",
            "PluginManifest@1": "manifest_digest",
            "PluginGrantEnvelope@1": "grant_digest",
        }
        checked = 0
        for bundle in self.bundles:
            for value in walk(bundle):
                if not isinstance(value, dict) or value.get("type") not in digest_fields:
                    continue
                field = digest_fields[value["type"]]
                expected = digest_bytes(canonical_bytes({key: item for key, item in value.items() if key != field}))
                self.assertEqual(value[field], expected, f"{bundle['fixture_id']} {value['type']}")
                checked += 1
        self.assertEqual(checked, 35)

    def test_fixture_lane_counts_and_types(self) -> None:
        counts: dict[str, int] = {}
        for bundle in self.bundles:
            counts[bundle["type"]] = counts.get(bundle["type"], 0) + 1
        self.assertEqual(counts, {
            "RouteFixtureBundle@1": 8,
            "PluginFixtureBundle@1": 6,
            "DisabledPluginFixtureBundle@1": 1,
            "PluginReloadFixtureBundle@1": 1,
            "ProcessFixtureBundle@1": 4,
            "BrokerFixtureBundle@1": 4,
        })

    def test_materializer_is_byte_identical(self) -> None:
        materializer = load_module("m1b_fixture_materializer", MATERIALIZER_PATH)
        expected = materializer.build_outputs()
        self.assertEqual(set(expected), set(self.paths + [FIXTURES / "manifest.json"]))
        for path, data in expected.items():
            self.assertEqual(path.read_bytes(), data, str(path))

    def test_synthetic_privacy_and_secret_boundary(self) -> None:
        forbidden = [
            re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
            re.compile(r"(?:AKIA|ASIA)[A-Z0-9]{16}"),
            re.compile(r"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"),
            re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
            re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
            re.compile(r"[A-Za-z]:[\\/]Users[\\/]", re.IGNORECASE),
        ]
        for path in self.paths + [FIXTURES / "manifest.json"]:
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                self.assertIsNone(pattern.search(text), f"{pattern.pattern} in {path}")

    def test_source_requirement_ids_are_closed_and_synthetic(self) -> None:
        allowed = {
            "m1b-billing-boundary", "m1b-broker-attach", "m1b-broker-cursor", "m1b-broker-flow",
            "m1b-broker-lease", "m1b-current-pause", "m1b-disabled-path", "m1b-no-substitution",
            "m1b-plugin-conflict", "m1b-plugin-graph", "m1b-plugin-grants", "m1b-plugin-integrity",
            "m1b-plugin-lifecycle", "m1b-privacy", "m1b-process-capability",
            "m1b-process-effect-separation", "m1b-route-capability", "m1b-route-components",
            "m1b-route-eligibility", "m1b-route-freshness",
        }
        observed = {source for bundle in self.bundles for source in bundle["source_requirement_ids"]}
        self.assertEqual(observed, allowed)


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("M1B_FIXTURE_PASS bundles=24")
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
