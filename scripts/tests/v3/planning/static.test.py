#!/usr/bin/env python3
"""AST isolation gate for the pure M1A package and its tests."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PACKAGE = ROOT / "scripts" / "v3" / "planning"
TEST_DIR = Path(__file__).resolve().parent
FORBIDDEN_IMPORT_ROOTS = {
    "asyncio", "ctypes", "django", "flask", "git", "http", "importlib", "multiprocessing",
    "mysql", "openai", "os", "psycopg", "requests", "shutil", "socket", "sqlite3",
    "subprocess", "tempfile", "time", "urllib", "webbrowser",
}
FORBIDDEN_CALLS = {
    "breakpoint", "compile", "eval", "exec", "input", "open", "__import__",
}


def _qualified(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _qualified(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _scan(path: Path, *, production: bool) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots = [alias.name.split(".")[0] for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            roots = [(node.module or "").split(".")[0]]
        else:
            roots = []
        for root in roots:
            if root in FORBIDDEN_IMPORT_ROOTS and (production or root != "importlib"):
                findings.append(f"{path}:{node.lineno}: forbidden import {root}")
        if production and isinstance(node, ast.Call):
            name = _qualified(node.func)
            if name.split(".")[-1] in FORBIDDEN_CALLS:
                findings.append(f"{path}:{node.lineno}: forbidden call {name}")
    return findings


def main() -> int:
    production = sorted(PACKAGE.rglob("*.py"))
    tests = sorted(TEST_DIR.glob("*.test.py"))
    findings = []
    for path in production:
        findings.extend(_scan(path, production=True))
    for path in tests:
        findings.extend(_scan(path, production=False))
    if findings:
        raise AssertionError("\n".join(findings))
    imports = set()
    for path in production:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
    assert imports.issubset({
        "__future__", "copy", "hashlib", "json",
        "scripts.v3.planning.validation.canonical",
        "scripts.v3.planning.validation.contracts",
    }), sorted(imports)
    print(f"M1A_STATIC_PASS production_files={len(production)} test_files={len(tests)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"M1A_STATIC_FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from error
