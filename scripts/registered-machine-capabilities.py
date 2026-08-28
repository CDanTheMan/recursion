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
import tempfile
from pathlib import Path

NAME_RE = re.compile(r"[a-z][a-z0-9-]{1,31}")
MACHINE_KEYS = {"schema_version", "id", "kind", "capabilities"}
CAPABILITY_RE = re.compile(r"[a-z][a-z0-9-]{1,63}")


def fail(message: str, code: int = 2) -> int:
    print(f"registered-machine-capabilities: {message}", file=sys.stderr)
    return code


def descriptor_dir() -> Path:
    override = os.environ.get("RECURSION_MACHINE_DIR", "").strip()
    return Path(override) if override else Path(__file__).resolve().parent / "machines"


def read_descriptor(machine: str) -> dict:
    path = descriptor_dir() / f"{machine}.json"
    try:
        raw = path.read_text(encoding="utf-8")
        value = json.loads(raw)
    except FileNotFoundError as exc:
        raise LookupError(f"machine descriptor is absent: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"machine descriptor is unreadable: {path}") from exc
    if not isinstance(value, dict) or set(value) != MACHINE_KEYS:
        raise ValueError("machine descriptor has invalid fields")
    if value["schema_version"] != 1 or value["id"] != machine or value["kind"] != "registered-machine":
        raise ValueError("machine descriptor identity or schema is invalid")
    capabilities = value["capabilities"]
    if not isinstance(capabilities, list) or not capabilities or \
            len(set(capabilities)) != len(capabilities) or \
            not all(isinstance(item, str) and CAPABILITY_RE.fullmatch(item) for item in capabilities):
        raise ValueError("machine capabilities must be a unique nonempty list of names")
    return value


def emit(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            json.dump(value, out, indent=2, sort_keys=True); out.write("\n"); out.flush(); os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


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
    except LookupError as exc:
        return fail(str(exc), 3)
    except (ValueError, OSError) as exc:
        return fail(str(exc), 2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
