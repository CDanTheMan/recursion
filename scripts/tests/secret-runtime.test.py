#!/usr/bin/env python3
"""Credential runtime-dir lifecycle: strict files and stale cleanup after a crash."""

from __future__ import annotations

import importlib.util
import os
import shutil
import stat
import tempfile
import time
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


def create_secret(path: Path, content: str) -> None:
    """Create a fixture secret owner-only at the instant its directory entry exists."""
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            descriptor = -1
            output.write(content.encode("utf-8"))
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def main() -> int:
    runtime = load_module()
    scratch_parent = os.environ.get("RECURSION_SECRET_RUNTIME_TEST_TMPDIR")
    if os.name == "nt":
        # tempfile.mkdtemp creates a mode=0700 ACL this review host cannot reopen.  Use the same
        # tempfile root with a collision-resistant name and a traversable fixture ACL on Windows;
        # POSIX still exercises tempfile.mkdtemp's owner-only scratch creation below.
        temporary = Path(scratch_parent or tempfile.gettempdir()) / (
            f"secret-runtime-test-{os.getpid()}-{time.time_ns()}"
        )
        temporary.mkdir(mode=0o777)
    else:
        temporary = Path(tempfile.mkdtemp(prefix="secret-runtime-test-", dir=scratch_parent))
    try:
        directory = Path(temporary) / "runtime"
        os.environ["RECURSION_SECRET_RUNTIME_ROOT"] = str(directory)
        if os.name == "nt":
            # Keep the product's Windows tolerance exercised without asking this review host to
            # reopen a mode=0700-created ACL.
            directory.mkdir(mode=0o777)
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
        create_secret(active, "ACTIVE=1\n")
        stale = directory / ".secret.999999.1.0123456789abcdef"
        create_secret(stale, "STALE=must-disappear\n")
        malformed = directory / ".secret.untrusted"
        create_secret(malformed, "SECRET=also-stale\n")
        if os.name != "nt":
            assert stat.S_IMODE(active.stat().st_mode) == 0o600
            assert stat.S_IMODE(stale.stat().st_mode) == 0o600
            assert stat.S_IMODE(malformed.stat().st_mode) == 0o600
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
        if os.name != "nt":
            previous_umask = os.umask(0)
            try:
                created = runtime.write_env(directory, b"TOKEN=never-logged\n")
            finally:
                os.umask(previous_umask)
        else:
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
            cleanup_candidate = directory / ".secret.999999.1.0123456789abcdef"
            create_secret(cleanup_candidate, "STALE=cleanup-test\n")
            with mock.patch.object(Path, "unlink", side_effect=OSError("synthetic cleanup failure")):
                try:
                    runtime.scavenge(directory)
                except runtime.SecretRuntimeCleanupError as exc:
                    assert str(exc) == "secret cleanup failed"
                    assert "synthetic cleanup failure" not in str(exc)
                    assert str(temporary) not in str(exc)
                else:
                    raise AssertionError("cleanup failure was hidden")
            cleanup_candidate.unlink()

            with mock.patch.object(
                runtime, "_validate_secret_file",
                side_effect=runtime.SecretRuntimeError("synthetic body failure"),
            ), mock.patch.object(Path, "unlink", side_effect=OSError("synthetic cleanup failure")):
                try:
                    runtime.write_env(directory, b"TOKEN=body-failure\n")
                except runtime.SecretRuntimeError as exc:
                    assert not isinstance(exc, runtime.SecretRuntimeCleanupError)
                    assert str(exc) == "synthetic body failure"
                    notes = getattr(exc, "__notes__", [])
                    assert "secret runtime cleanup failed after the primary operation error" in notes
                    assert "synthetic cleanup failure" not in " ".join(notes)
                    assert str(temporary) not in " ".join(notes)
                else:
                    raise AssertionError("body exception was not preserved")
            for leftover in directory.iterdir():
                if leftover != created:
                    leftover.unlink()

            runtime._remove_secret(created)
            assert not created.exists()
        else:
            created.unlink()
        os.environ.pop("RECURSION_SECRET_RUNTIME_ROOT", None)
    finally:
        shutil.rmtree(temporary, ignore_errors=True)
    print("secret-runtime.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
