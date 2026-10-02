#!/usr/bin/env python3
"""Deterministic gate for the 2026-10-02 overnight research-handoff intake.

Verifies the copied handoff files exist at the same relative paths recorded in
MANIFEST.json, that each copied file matches the SHA-256 the manifest records, and that no
foreign-project identifier or obvious secret material appears in the copied text. The copied
tree preserves the manifest's relative paths, so a manifest entry maps directly onto
'ROOT/path'. Reuses the repository's public-scope pattern. Deterministic and provider-free.

Run from the repository root:

    python -X utf8 -B docs/v3/research-lane/overnight-20261002/check_intake.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SELF = Path(__file__).resolve()
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.check_public_scope import PATTERN as FORBIDDEN  # noqa: E402

TEXT_SUFFIXES = {".md", ".json", ".csv", ".txt"}

SECRET_PATTERNS = [
    ("api-key", re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9]{20,}")),
    ("github-token", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer-token", re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}")),
    ("password-assignment", re.compile(r"(?i)password\s*[=:]\s*[^\s\"'<>]{3,}")),
    ("api_key-assignment", re.compile(r"(?i)api[_-]?key\s*[=:]\s*[^\s\"'<>]{3,}")),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    errors: list[str] = []

    manifest_path = ROOT / "MANIFEST.json"
    if not manifest_path.exists():
        print("FAIL: overnight intake gate")
        print(" - missing: MANIFEST.json")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    entries = manifest.get("files", [])
    present = 0
    hashed = 0
    for entry in entries:
        original = entry["path"]
        path = ROOT / original
        if not path.exists():
            errors.append(f"missing copied file: {original}")
            continue
        present += 1
        expected = entry.get("sha256")
        if expected:
            actual = sha256(path)
            hashed += 1
            if actual != expected:
                errors.append(
                    f"{original}: sha256 mismatch (expected {expected}, got {actual})"
                )

    scanned: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if path.resolve() == SELF:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            scanned.append(path)

    forbidden_hits = 0
    secret_hits = 0
    for path in scanned:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        for match in FORBIDDEN.finditer(text):
            forbidden_hits += 1
            errors.append(f"{rel}: foreign identifier '{match.group(0)}'")
        for label, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                secret_hits += 1
                errors.append(f"{rel}: possible secret ({label}) '{match.group(0)[:40]}'")

    if errors:
        print("FAIL: overnight intake gate")
        for error in errors:
            print(" -", error)
        print(
            f"\n{present}/{len(entries)} files present, {hashed} sha256 checked, "
            f"{len(scanned)} text files scanned, "
            f"{forbidden_hits} foreign-identifier match(es), {secret_hits} possible secret(s)"
        )
        return 1

    print(
        f"PASS: {present}/{len(entries)} files present, {hashed} sha256 verified, "
        f"{len(scanned)} text files scanned (identifiers + secrets)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
