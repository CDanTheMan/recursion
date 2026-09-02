#!/usr/bin/env python3
"""Focused regressions for Windows-only Phase 8 subprocess portability."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from windows_test_support import bash_executable


SOURCE = Path(__file__).resolve().parents[2]


def test_shell_selection() -> None:
    executable = bash_executable()
    if os.name == "nt":
        path = Path(executable)
        assert path.is_file() and path.name.lower() == "bash.exe"
        result = subprocess.run(
            [executable, "-lc", "printf '%s' \\\"$BASH_VERSION\\\""],
            text=True, capture_output=True, check=False, timeout=5,
        )
        assert result.returncode == 0 and result.stdout
    else:
        assert executable == "bash"


def test_native_pid_translation_contract() -> None:
    work = (SOURCE / "scripts/work.sh").read_text(encoding="utf-8")
    conduct = (SOURCE / "scripts/conduct-hermes.sh").read_text(encoding="utf-8")
    assert 'OWNER_PID="$(cat /proc/$$/winpid 2>/dev/null || echo $$)"' in work
    assert 'lock-acquire "$WSLOCK" "$OWNER_PID"' in work
    assert 'lock-release "$WSLOCK" "$OWNER_PID"' in work
    assert 'OWNER_PID="$(cat /proc/$$/winpid 2>/dev/null || echo $$)"' in conduct
    for script in (work, conduct):
        lock_lines = [
            line for line in script.splitlines()
            if 'runtime-state.py" lock-' in line
        ]
        assert lock_lines and all('"$OWNER_PID"' in line for line in lock_lines)
    if os.name == "nt":
        result = subprocess.run(
            [bash_executable(), "-lc", "test -r /proc/$$/winpid && cat /proc/$$/winpid"],
            text=True, capture_output=True, check=False, timeout=5,
        )
        assert result.returncode == 0 and result.stdout.strip().isdigit()


def main() -> int:
    test_shell_selection()
    test_native_pid_translation_contract()
    print("phase8-windows-harness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
