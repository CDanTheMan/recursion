#!/usr/bin/env python3
"""Credential runtime-dir lifecycle: strict files and stale cleanup after a crash."""

from __future__ import annotations

import importlib.util
import os
import stat
import tempfile
from unittest import mock
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
        os.environ["RECURSION_SECRET_RUNTIME_ROOT"] = str(directory)
        runtime.ensure_directory(directory)
        if os.name != "nt":
            directory.chmod(0o755)
            try:
                runtime.ensure_directory(directory)
            except runtime.SecretRuntimeError:
                pass
            else:
                raise AssertionError("unsafe runtime directory permissions were repaired/accepted")
            directory.chmod(0o700)
            outside = Path(temporary) / "outside"
            outside.mkdir(mode=0o700)
            linked = Path(temporary) / "linked"
            linked.symlink_to(outside, target_is_directory=True)
            os.environ["RECURSION_SECRET_RUNTIME_ROOT"] = str(linked / "runtime")
            try:
                runtime.ensure_directory(linked / "runtime")
            except runtime.SecretRuntimeError:
                pass
            else:
                raise AssertionError("symlinked runtime parent escaped confinement")
            os.environ["RECURSION_SECRET_RUNTIME_ROOT"] = str(directory)
        current_start = runtime.process_start(os.getpid())
        assert current_start
        active = directory / f".secret.{os.getpid()}.{current_start}.0123456789abcdef"
        active.write_text("ACTIVE=1\n", encoding="utf-8")
        stale = directory / ".secret.999999.1.0123456789abcdef"
        stale.write_text("STALE=must-disappear\n", encoding="utf-8")
        malformed = directory / ".secret.untrusted"
        malformed.write_text("SECRET=also-stale\n", encoding="utf-8")
        if os.name != "nt":
            stale.chmod(0o600)
            malformed.chmod(0o644)
            try:
                runtime.scavenge(directory)
            except runtime.SecretRuntimeError:
                pass
            else:
                raise AssertionError("unsafe malformed secret permissions were repaired/accepted")
            malformed.chmod(0o600)
        try:
            hostile_name = Path(f".secret.{'9' * 5000}.1.0123456789abcdef")
            with mock.patch.object(runtime.Path, "iterdir", return_value=[hostile_name]):
                runtime.scavenge(directory)
        except runtime.SecretRuntimeError:
            pass
        except Exception as exc:  # pragma: no cover - diagnostic guard for the regression
            raise AssertionError(f"overlong secret PID raised raw {type(exc).__name__}") from exc
        else:
            raise AssertionError("overlong secret PID was not rejected")
        runtime.scavenge(directory)
        assert active.exists(), "live process credential was scavenged"
        assert not stale.exists(), "stale credential survived startup scavenging"
        assert not malformed.exists(), "malformed credential file survived startup scavenging"
        created = runtime.write_env(directory, b"TOKEN=never-logged\n")
        assert created.exists()
        if os.name != "nt":
            assert stat.S_IMODE(created.stat().st_mode) == 0o600
        assert created.read_bytes() == b"TOKEN=never-logged\n"
        if os.name != "nt":
            created.chmod(0o644)
            try:
                runtime.scavenge(directory)
            except runtime.SecretRuntimeError:
                pass
            else:
                raise AssertionError("unsafe secret file permissions were repaired/accepted")
            created.chmod(0o600)
            with mock.patch.object(Path, "unlink", side_effect=OSError("synthetic cleanup failure")):
                try:
                    runtime.scavenge(directory, current_pid=os.getpid() + 1)
                except runtime.SecretRuntimeCleanupError:
                    pass
                else:
                    raise AssertionError("cleanup failure was hidden")
        created.unlink()
        os.environ.pop("RECURSION_SECRET_RUNTIME_ROOT", None)
    print("secret-runtime.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
