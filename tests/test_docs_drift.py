"""Fail when the user guide drifts from the command or the config."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "USER-GUIDE.md"
CONFIG = ROOT / "config" / "harness.json"


def _guide() -> str:
    assert GUIDE.is_file(), "docs/USER-GUIDE.md is missing"
    return GUIDE.read_text(encoding="utf-8")


def _help_text() -> str:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", "scripts/recursion", "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_guide_mentions_every_subcommand() -> None:
    help_text = _help_text()
    match = re.search(r"usage: recursion \[-h\]\s+\{([^}]+)\}", help_text)
    assert match, "recursion --help did not list subcommands"
    guide = _guide()
    missing = [name.strip() for name in match.group(1).split(",") if name.strip() not in guide]
    if missing:
        pytest.fail(f"user guide omits subcommands: {missing}")


def test_guide_mentions_every_top_level_config_key() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        pytest.fail("config/harness.json has no top-level keys")
    guide = _guide()
    missing = [key for key in payload if key not in guide]
    if missing:
        pytest.fail(f"user guide omits config keys: {missing}")
