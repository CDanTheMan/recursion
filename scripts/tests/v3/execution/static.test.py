#!/usr/bin/env python3
"""Static isolation checks for all M1B schema and test-only code."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = ROOT / "schemas" / "control-plane" / "v3" / "execution"
TEST_DIR = ROOT / "scripts" / "tests" / "v3" / "execution"
PRODUCTION_DIR = ROOT / "scripts" / "v3" / "execution"

FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp", "asyncio", "boto3", "ctypes", "http", "multiprocessing", "openai", "os",
    "psutil", "random", "requests", "shutil", "socket", "sqlite3", "subprocess", "tempfile",
    "threading", "time", "urllib", "webbrowser",
}
FORBIDDEN_CALLS = {"compile", "eval", "exec", "__import__"}
FORBIDDEN_TEXT = [
    "git push", "git merge", "git checkout", "git reset", "git worktree", "powershell",
    "cmd.exe", "create_subprocess", "popen(", "system(", "socket(", "urlopen(",
]


class M1BStaticTests(unittest.TestCase):
    def test_no_production_runtime_was_created(self) -> None:
        self.assertFalse(PRODUCTION_DIR.exists(), "M1B is contracts/tests only")

    def test_imports_calls_and_source_text_are_inert(self) -> None:
        paths = sorted(SCHEMA_DIR.glob("*.py")) + sorted(TEST_DIR.glob("*.py"))
        self.assertGreaterEqual(len(paths), 6)
        for path in paths:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
            with self.subTest(path=path):
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        roots = {alias.name.split(".")[0] for alias in node.names}
                        self.assertFalse(roots & FORBIDDEN_IMPORT_ROOTS)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        self.assertNotIn(node.module.split(".")[0], FORBIDDEN_IMPORT_ROOTS)
                    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        self.assertNotIn(node.func.id, FORBIDDEN_CALLS)
                if path != Path(__file__).resolve():
                    lowered = source.lower()
                    for text in FORBIDDEN_TEXT:
                        self.assertNotIn(text, lowered)

    def test_oracle_has_no_path_or_importlib_access(self) -> None:
        source = (TEST_DIR / "reference_oracle.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".")[0])
        self.assertEqual(roots, {"__future__", "base64", "hashlib", "json", "typing"})


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("M1B_STATIC_PASS")
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
