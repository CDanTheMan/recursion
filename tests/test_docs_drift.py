"""Fail when the README, user guide, or architecture note drifts."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "USER-GUIDE.md"
README = ROOT / "README.md"
ARCHITECTURE = ROOT / "docs" / "ARCHITECTURE.md"
CONFIG = ROOT / "config" / "harness.json"
STAGES = ("plan", "schedule", "worktree", "provider", "review", "landing", "report")


def _guide() -> str:
    assert GUIDE.is_file(), "docs/USER-GUIDE.md is missing"
    return GUIDE.read_text(encoding="utf-8")


def _readme() -> str:
    assert README.is_file(), "README.md is missing"
    return README.read_text(encoding="utf-8")


def _help_text(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", "scripts/recursion", *args, "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def _subcommands(help_text: str) -> list[str]:
    """Return usage-line subcommands, ignoring choices nested in ``[...]``."""

    usage: list[str] = []
    for line in help_text.splitlines():
        if usage and not line.strip():
            break
        if line.startswith("usage:") or usage:
            usage.append(line)
    flat = re.sub(r"\s+", " ", " ".join(usage))
    # ``[--level {info,warning,error}]`` is an option, not a subcommand.
    stripped = re.sub(r"\[[^\[\]]*\]", " ", flat)
    match = re.search(r"\{([^}]+)\}", stripped)
    if match is None:
        return []
    return [name.strip() for name in match.group(1).split(",") if name.strip()]


def _options(help_text: str) -> set[str]:
    return set(re.findall(r"--[a-z0-9][a-z0-9-]*", help_text))


def _command_tree() -> list[tuple[str, ...]]:
    """Top-level commands, plus nested ones such as config validate."""

    tree = [()]
    pending = [()]
    while pending:
        prefix = pending.pop()
        for name in _subcommands(_help_text(*prefix)):
            command = (*prefix, name)
            tree.append(command)
            pending.append(command)
    return tree


def _config_keys(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            found.add(key)
            found.update(_config_keys(item))
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                found.update(_config_keys(item))
    return found


def test_guide_mentions_every_subcommand() -> None:
    names = _subcommands(_help_text())
    if not names:
        pytest.fail("recursion --help did not list subcommands")
    guide = _guide()
    missing = [name for name in names if name not in guide]
    if missing:
        pytest.fail(f"user guide omits subcommands: {missing}")


def test_readme_mentions_every_subcommand_and_provider() -> None:
    readme = _readme()
    missing = [name for name in _subcommands(_help_text()) if name not in readme]
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    providers = [item["name"] for item in payload["providers"]]
    missing.extend(name for name in providers if name not in readme)
    if missing:
        pytest.fail(f"README omits: {missing}")
    assert "docs/ARCHITECTURE.md" in readme
    assert "docs/USER-GUIDE.md" in readme


def test_guide_mentions_every_flag() -> None:
    guide = _guide()
    missing = []
    for command in _command_tree():
        for option in sorted(_options(_help_text(*command))):
            if option not in guide:
                label = "recursion " + " ".join(command) if command else "recursion"
                missing.append(f"{label} {option}")
    if missing:
        pytest.fail(f"user guide omits flags: {missing}")


def test_guide_mentions_every_config_key_and_provider() -> None:
    payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        pytest.fail("config/harness.json has no top-level keys")
    guide = _guide()
    missing = sorted(key for key in _config_keys(payload) if key not in guide)
    providers = [item["name"] for item in payload["providers"] if item["name"] not in guide]
    if missing or providers:
        pytest.fail(f"user guide omits config keys: {missing} providers: {providers}")


def test_architecture_diagram_names_the_run() -> None:
    assert ARCHITECTURE.is_file(), "docs/ARCHITECTURE.md is missing"
    text = ARCHITECTURE.read_text(encoding="utf-8")
    match = re.search(r"```mermaid\n(.*?)```", text, re.DOTALL)
    assert match, "docs/ARCHITECTURE.md has no mermaid diagram"
    body = match.group(1)
    missing = [stage for stage in STAGES if stage not in body]
    if missing:
        pytest.fail(f"architecture diagram omits: {missing}")


def test_guide_has_linux_and_windows_troubleshooting() -> None:
    guide = _guide()
    assert "### Linux" in guide
    assert "### Windows" in guide
