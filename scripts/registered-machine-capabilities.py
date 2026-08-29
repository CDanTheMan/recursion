#!/usr/bin/env python3
"""Disabled-by-default reader for registered-machine capability records.

Phase 5 only defines the local contract.  It deliberately performs no discovery
on a live host: no SSH, socket, browser, credential, or network operation is
available here.  A later human-owned adapter may replace the record reader while
keeping this fail-closed interface.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

class FirstPartyImportError(ImportError):
    """A required controller module is absent from the importing script's tree."""


try:
    from phase5_safety import (BoundaryError, MAX_FILE_BYTES, atomic_write,
                               decode_json, pinned_directory, read_bytes)
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    import_error = FirstPartyImportError(
        f"first-party module 'phase5_safety' not found; searched {_SCRIPT_DIR}"
    )
    if __name__ == "__main__":
        print(f"registered-machine-capabilities: first-party import failed: {import_error}", file=sys.stderr)
        raise SystemExit(95)
    raise import_error from None

NAME_RE = re.compile(r"[a-z][a-z0-9-]{1,31}")
MACHINE_KEYS = {"schema_version", "id", "kind", "capabilities"}
CAPABILITY_RE = re.compile(r"[a-z][a-z0-9-]{1,63}")


def is_link_or_reparse(path: Path) -> bool:
    try:
        info = os.lstat(path)
    except (OSError, ValueError, TypeError):
        return False
    return os.path.islink(path) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def safe_regular(path: Path) -> None:
    try:
        read_bytes(path, label="machine descriptor", max_bytes=MAX_FILE_BYTES,
                   private=True)
    except BoundaryError as exc:
        raise ValueError("machine descriptor must be a regular non-symlink file") from exc


def fail(message: str, code: int = 2) -> int:
    print(f"registered-machine-capabilities: {message}", file=sys.stderr)
    return code


def descriptor_dir() -> Path:
    override = os.environ.get("RECURSION_MACHINE_DIR", "").strip()
    value = Path(override) if override else Path(__file__).parent / "machines"
    try:
        with pinned_directory(value) as (_, absolute):
            return Path(absolute)
    except (BoundaryError, OSError, ValueError, TypeError) as exc:
        raise ValueError("machine descriptor directory is not a confined directory") from exc


def read_descriptor(machine: str) -> dict:
    path = descriptor_dir() / f"{machine}.json"
    try:
        raw = read_bytes(path, label="machine descriptor", private=True)
        value = decode_json(raw, "machine descriptor")
    except FileNotFoundError:
        raise LookupError("machine descriptor is absent") from None
    except BoundaryError:
        raise ValueError("machine descriptor is unreadable") from None
    if not isinstance(value, dict) or set(value) != MACHINE_KEYS:
        raise ValueError("machine descriptor has invalid fields")
    if not isinstance(value["schema_version"], int) or isinstance(value["schema_version"], bool) \
            or value["schema_version"] != 1 \
            or value["id"] != machine or value["kind"] != "registered-machine":
        raise ValueError("machine descriptor identity or schema is invalid")
    capabilities = value["capabilities"]
    if not isinstance(capabilities, list) or not capabilities \
            or any(not isinstance(item, str) or not CAPABILITY_RE.fullmatch(item)
                   for item in capabilities) \
            or len(set(capabilities)) != len(capabilities):
        raise ValueError("machine capabilities must be a unique nonempty list of names")
    return value


def emit(path: Path, value: dict) -> None:
    try:
        encoded = (json.dumps(value, indent=2, sort_keys=True,
                              allow_nan=False) + "\n").encode("utf-8")
        atomic_write(path, encoded, replace=False, mode=0o600,
                     label="capability output")
    except BoundaryError:
        raise OSError("capability output is unavailable") from None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="registered-machine-capabilities")
    parser.add_argument("machine")
    parser.add_argument("--emit", required=True)
    args = parser.parse_args(argv)
    if not NAME_RE.fullmatch(args.machine):
        return fail("invalid machine name")
    if os.environ.get("RECURSION_REGISTERED_MACHINE_ADAPTER") != "1":
        return fail("adapter is disabled", 3)
    enabled = "RECURSION_REGISTERED_MACHINE_" + args.machine.upper().replace("-", "_") + "_ENABLED"
    if os.environ.get(enabled) != "1":
        return fail(f"{enabled} is not enabled", 3)
    try:
        descriptor = read_descriptor(args.machine)
        value = {"schema_version": 1, "machine_id": args.machine,
                 "source": "declared-local", "capabilities": descriptor["capabilities"],
                 "adapter_enabled": True}
        emit(Path(args.emit), value)
    except LookupError:
        return fail("machine descriptor is absent", 3)
    except ValueError as exc:
        return fail(str(exc), 2)
    except OSError:
        return fail("capability output is unavailable", 2)
    except (TypeError, OverflowError, RecursionError, UnicodeDecodeError,
            json.JSONDecodeError):
        return fail("machine descriptor is unreadable", 2)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except FirstPartyImportError as exc:
        print(f"registered-machine-capabilities: first-party import failed: {exc}", file=sys.stderr)
        raise SystemExit(95)
