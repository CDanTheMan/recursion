"""Small subprocess helpers for Python tests launched from Windows.

The controller is POSIX/Linux software, but several hermetic tests are authored and run from
Windows.  A bare ``bash`` there can resolve to the WSL app-execution alias instead of Git Bash.
Keep this selection test-only; production scripts continue to invoke the platform's normal
``bash`` command.
"""

from __future__ import annotations

import os
from pathlib import Path


def bash_executable() -> str:
    """Return Git Bash on Windows, and the normal shell name on POSIX."""
    if os.name != "nt":
        return "bash"
    roots = [
        os.environ.get("ProgramFiles"),
        os.environ.get("ProgramW6432"),
        r"C:\Program Files",
    ]
    for root in roots:
        if root:
            # Git/bin/bash.exe is the launcher that supplies Git's POSIX tool PATH (date,
            # cat, etc.) to child scripts; usr/bin/bash.exe is a fallback for installations
            # that do not ship the launcher.
            for relative in ("Git/bin/bash.exe", "Git/usr/bin/bash.exe"):
                candidate = Path(root) / relative
                if candidate.is_file():
                    return str(candidate)
    # Preserve a useful OS-level error if Git is not installed; do not silently use WSL.
    return str(Path(roots[0] or r"C:\Program Files") / "Git/usr/bin/bash.exe")


def prepare_shell_env(env: dict[str, str]) -> dict[str, str]:
    """Make bare ``bash`` child lookups resolve Git Bash on Windows fixtures."""
    if os.name != "nt":
        return env
    git_bin = str(Path(bash_executable()).parent)
    env["PATH"] = git_bin + os.pathsep + env.get("PATH", "")
    return env


def bash_command(*args: str) -> list[str]:
    """Build a subprocess argv whose first element is the selected Bash executable."""
    return [bash_executable(), *args]


def install_real_fcntl_shim(scripts_root: Path) -> None:
    """Install a bounded, cross-process ``flock`` stand-in for Windows-only fixtures.

    This is test infrastructure only.  The production controller still imports and uses
    POSIX ``fcntl`` on Linux.  A byte-range far beyond EOF avoids Windows mandatory-locking
    interference with the fixture's lock-file reads.
    """
    if os.name != "nt":
        return
    (scripts_root / "fcntl.py").write_text(
        "import msvcrt\n"
        "import os\n\n"
        "LOCK_SH, LOCK_EX, LOCK_NB, LOCK_UN = 1, 2, 4, 8\n"
        "_REGION = 1 << 30\n\n"
        "def flock(target, flags):\n"
        "    descriptor = target if isinstance(target, int) else target.fileno()\n"
        "    current = os.lseek(descriptor, 0, os.SEEK_CUR)\n"
        "    os.lseek(descriptor, _REGION, os.SEEK_SET)\n"
        "    try:\n"
        "        if flags & LOCK_UN:\n"
        "            try:\n"
        "                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)\n"
        "            except OSError:\n"
        "                pass\n"
        "            return\n"
        "        try:\n"
        "            msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)\n"
        "        except OSError as exc:\n"
        "            raise BlockingIOError(exc.errno, 'lock is held by another handle') from exc\n"
        "    finally:\n"
        "        os.lseek(descriptor, current, os.SEEK_SET)\n",
        encoding="utf-8",
        newline="\n",
    )


def install_nt_posix_shim(scripts_root: Path) -> None:
    """Stage only the POSIX filesystem no-ops needed by Windows fixture children.

    The deployed controller remains Linux-shaped.  Windows cannot fsync a directory or
    chmod an open temporary file, so this fixture-local sitecustomize preserves the tested
    state-machine paths without changing production imports or lock ownership semantics.
    """
    if os.name != "nt":
        return
    scripts_root.mkdir(parents=True, exist_ok=True)
    (scripts_root / "_recursion_nt_posix.py").write_text(
        "import os\n"
        "import tempfile\n\n"
        "if not getattr(os, '_recursion_nt_posix_shim', False):\n"
        "    os._recursion_nt_posix_shim = True\n"
        "    os.fchmod = lambda _descriptor, _mode: None\n"
        "    _real_open, _scratch = os.open, tempfile.TemporaryFile()\n\n"
        "    def _open(path, flags, mode=0o777, **kwargs):\n"
        "        try:\n"
        "            inert = not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT) and os.path.isdir(path)\n"
        "        except (TypeError, ValueError, OSError):\n"
        "            inert = False\n"
        "        return os.dup(_scratch.fileno()) if inert else _real_open(path, flags, mode, **kwargs)\n\n"
        "    os.open = _open\n",
        encoding="utf-8",
        newline="\n",
    )
    (scripts_root / "sitecustomize.py").write_text(
        "import _recursion_nt_posix  # noqa: F401\n",
        encoding="utf-8",
        newline="\n",
    )


def install_single_process_flock_stub(bin_root: Path) -> None:
    """Provide util-linux ``flock(1)`` syntax for single-process Windows fixtures.

    Git Bash has no util-linux ``flock`` command.  Fixtures that do not test contention can
    inject this bounded command stub; contention-sensitive Python tests must use
    :func:`install_real_fcntl_shim` or a Linux runner instead.
    """
    if os.name != "nt":
        return
    bin_root.mkdir(parents=True, exist_ok=True)
    stub = bin_root / "flock"
    stub.write_text(
        "#!/bin/sh\n"
        "# Windows authoring-host stand-in; production is Linux.\n"
        "while [ \"$#\" -gt 0 ]; do\n"
        "  case \"$1\" in\n"
        "    -w|--wait|--timeout) shift 2 ;;\n"
        "    -*) shift ;;\n"
        "    *[!0-9]*) shift; [ \"$#\" -gt 0 ] && exec \"$@\"; exit 0 ;;\n"
        "    *) shift ;;\n"
        "  esac\n"
        "done\n"
        "exit 0\n",
        encoding="utf-8",
        newline="\n",
    )


def install_python_lf_wrapper(bin_root: Path) -> None:
    """Normalize Python text streams at the fixture boundary for Git Bash ``read``."""
    if os.name != "nt":
        return
    bin_root.mkdir(parents=True, exist_ok=True)
    import sys
    executable = sys.executable.replace("\\", "/")
    (bin_root / "python3").write_text(
        "#!/usr/bin/env bash\n"
        "set -o pipefail\n"
        f'"{executable}" "$@" | tr -d \'\\r\'\n'
        "exit ${PIPESTATUS[0]}\n",
        encoding="utf-8",
        newline="\n",
    )
