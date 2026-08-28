#!/usr/bin/env python3
"""Credential runtime-dir lifecycle: strict files and stale cleanup after a crash."""

from __future__ import annotations

import importlib.util
import os
import stat
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts/secret_runtime.py"


def load_module():
    spec = importlib.util.spec_from_file_location("secret_runtime_test_module", SOURCE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    runtime = load_module()
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary) / "runtime"
        runtime.ensure_directory(directory)
        current_start = runtime.process_start(os.getpid())
        assert current_start
        active = directory / f".secret.{os.getpid()}.{current_start}.0123456789abcdef"
        active.write_text("ACTIVE=1\n", encoding="utf-8")
        stale = directory / ".secret.999999.1.0123456789abcdef"
        stale.write_text("STALE=must-disappear\n", encoding="utf-8")
        malformed = directory / ".secret.untrusted"
        malformed.write_text("SECRET=also-stale\n", encoding="utf-8")
        runtime.scavenge(directory)
        assert active.exists(), "live process credential was scavenged"
        assert not stale.exists(), "stale credential survived startup scavenging"
        assert not malformed.exists(), "malformed credential file survived startup scavenging"
        created = runtime.write_env(directory, b"TOKEN=never-logged\n")
        assert created.exists()
        if os.name != "nt":
            assert stat.S_IMODE(created.stat().st_mode) == 0o600
        assert created.read_bytes() == b"TOKEN=never-logged\n"
        created.unlink()
    print("secret-runtime.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
