#!/usr/bin/env python3
"""Static purity, independence, and synthetic-boundary gates for M1C."""

from __future__ import annotations

import ast
import importlib.util
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
ORACLE_PATH = HERE / "reference_oracle.py"
MATERIALIZER_PATH = HERE / "materialize_fixtures.py"
FIXTURES = HERE / "fixtures"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schema_gate = load_module("m1c_static_schema", HERE / "schema.test.py")
oracle = load_module("m1c_static_oracle", ORACLE_PATH)


class M1CStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = ORACLE_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source, filename=str(ORACLE_PATH))
        cls.fixture_paths = sorted(FIXTURES.glob("F-M1C-*.json"))

    def test_reference_oracle_imports_only_pure_standard_modules(self) -> None:
        imports: set[str] = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
        self.assertEqual(imports, {"__future__", "hashlib", "json", "typing"})

    def test_reference_oracle_has_no_ambient_or_actuating_api(self) -> None:
        forbidden_names = {
            "__import__", "breakpoint", "compile", "eval", "exec", "input", "open",
            "Path", "socket", "requests", "urlopen", "connect", "system", "popen",
            "getenv", "environ", "time", "sleep", "random", "sqlite3", "subprocess",
        }
        loaded_names = {
            node.id
            for node in ast.walk(self.tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        }
        self.assertFalse(loaded_names & forbidden_names)
        self.assertFalse(any(isinstance(node, (ast.AsyncFunctionDef, ast.Await)) for node in ast.walk(self.tree)))

    def test_reference_oracle_exports_exact_bounded_surface(self) -> None:
        public_functions = {
            node.name
            for node in self.tree.body
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        }
        self.assertEqual(
            public_functions,
            {
                "assess_evidence", "assess_publication", "assess_retention",
                "assess_state_contract", "canonical_bytes", "classify_effect_trace",
                "evaluate_bundle",
            },
        )

    def test_reference_oracle_is_input_immutable_and_repeatable(self) -> None:
        for path in self.fixture_paths:
            bundle = schema_gate.strict_loads(path.read_bytes())
            before = schema_gate.canonical_bytes(bundle)
            first = oracle.evaluate_bundle(bundle)
            second = oracle.evaluate_bundle(bundle)
            with self.subTest(fixture=bundle["fixture_id"]):
                self.assertEqual(schema_gate.canonical_bytes(bundle), before)
                self.assertEqual(
                    schema_gate.canonical_bytes(first), schema_gate.canonical_bytes(second)
                )

    def test_fixture_materializer_cannot_import_or_call_oracle(self) -> None:
        source = MATERIALIZER_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(MATERIALIZER_PATH))
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        )
        self.assertFalse(any("oracle" in name for name in imported))
        self.assertNotIn("reference_oracle", source)

    def test_fixtures_are_literal_synthetic_and_contain_no_secret_marker(self) -> None:
        self.assertEqual(len(self.fixture_paths), 24)
        forbidden = ("BEGIN PRIVATE KEY", "ghp_", "github_pat_", "AKIA", "Bearer ")
        for path in self.fixture_paths:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertFalse(any(marker in text for marker in forbidden))
                self.assertNotRegex(text, r"[A-Za-z]:\\")
                self.assertNotIn("github.com/", text)
                bundle = schema_gate.strict_loads(text.encode("utf-8"))
                encoded = schema_gate.canonical_bytes(bundle).decode("utf-8")
                self.assertNotRegex(encoded, r'https://(?!example\.invalid/)')

    def test_integrity_sources_compile_without_importing_production_modules(self) -> None:
        paths = sorted(HERE.glob("*.py")) + sorted(
            (ROOT / "schemas" / "control-plane" / "v3" / "integrity").glob("*.py")
        )
        for path in paths:
            with self.subTest(path=path.name):
                compile(path.read_text(encoding="utf-8"), str(path), "exec")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(M1CStaticTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("M1C_STATIC_PASS tests=7 fixtures=24")
    raise SystemExit(0 if result.wasSuccessful() else 1)
