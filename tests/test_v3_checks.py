"""Pytest wrapper for the existing v3 checks.

Runs the orientation contracts, the scope tests, and the schema, fixture, and
M1 programs under ``scripts/tests/v3`` and ``schemas/control-plane/v3``. It does
not replace those programs.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_v3_orientation as gate  # noqa: E402


def _programs() -> list[tuple[str, ...]]:
    programs = gate.contract_programs()
    schemas = [p for p in programs if p[0].endswith("/materialize.py")]
    fixtures = [p for p in programs if p[0].endswith("/materialize_fixtures.py")]
    tests = [p for p in programs if p[0].endswith(".test.py")]
    if len(programs) != 23 or len(schemas) != 3 or len(fixtures) != 3 or len(tests) != 17:
        raise RuntimeError(
            "M1 check inventory changed; inspect instead of reducing coverage: "
            f"programs={len(programs)} schemas={len(schemas)} "
            f"fixtures={len(fixtures)} tests={len(tests)}"
        )
    return programs


def _run(program: tuple[str, ...]) -> None:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", *program],
        cwd=ROOT,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        # The orientation runner bounds each program at 180s. Pytest traces the
        # child for coverage, and that tracing can push the planning red-fixture
        # program past 180s on Windows. The program must still exit 0.
        timeout=600,
    )
    if result.returncode:
        output = (result.stdout + result.stderr).strip()
        pytest.fail(f"{' '.join(program)} exited {result.returncode}\n{output[-4000:]}")


def test_orientation_contracts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["check_v3_orientation.py", "--contracts"])
    gate.main()


def test_scope_checks() -> None:
    path = ROOT / "tools" / "test_check_v3_orientation_scope.py"
    spec = importlib.util.spec_from_file_location("v3_scope_checks", path)
    if spec is None or spec.loader is None:
        pytest.fail(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    assert result.wasSuccessful(), "scope checks failed"


@pytest.mark.parametrize("program", _programs(), ids=lambda program: " ".join(program))
def test_schema_and_fixture_validator(program: tuple[str, ...]) -> None:
    relative = program[0].replace("\\", "/")
    assert relative.startswith(("schemas/control-plane/v3/", "scripts/tests/v3/"))
    assert "scripts/v3/harness/" not in relative
    _run((relative, *program[1:]))
