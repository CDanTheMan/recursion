#!/usr/bin/env python3
"""Intake gate for the 2026-10-02 shared-contracts + extensibility return.

Verifies the delivered files against SHA256SUMS.txt and scans the text for obvious secrets.
Deterministic and provider-free.

    python -X utf8 -B docs/v3/research-lane/shared-contracts-20261002/check_intake.py
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUMS = HERE / "SHA256SUMS.txt"
SECRET = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|"
    r"bearer\s+[A-Za-z0-9._\-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)"
)


def fail(message: str) -> None:
    print(f"INTAKE_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not SUMS.exists():
        fail("missing SHA256SUMS.txt")
    entries = 0
    for line in SUMS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([0-9a-fA-F]{64})\s+\*?(.+)$", line.strip())
        if not m:
            continue
        expected, name = m.group(1).lower(), m.group(2).strip()
        path = HERE / name
        if not path.exists():
            fail(f"missing delivered file: {name}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            fail(f"hash mismatch: {name}")
        entries += 1
    for path in HERE.glob("*.md"):
        found = SECRET.search(path.read_text(encoding="utf-8", errors="replace"))
        if found:
            fail(f"possible secret in {path.name}: {found.group(0)[:40]!r}")
    print(f"PASS: {entries} delivered files sha256-verified; no secret patterns in prose")
    return 0


if __name__ == "__main__":
    sys.exit(main())
