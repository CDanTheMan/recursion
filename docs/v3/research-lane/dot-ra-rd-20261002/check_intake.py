#!/usr/bin/env python3
"""Deterministic gate for the 2026-10-02 dot R-A/R-D research-handoff intake.

Verifies the copied handoff files exist, that each copied text/JSON/CSV file matches the
SHA-256 recorded in MANIFEST.json, that raw/ contains no .docx, and that no foreign-project
identifier appears in the copied text. The manifest lists files by their original relative
path, so those paths are mapped onto the raw/ copies ('DIR/FILE' -> 'raw/DIR/FILE'); root
files stay at the root and .docx entries are skipped. Reuses the repository's public-scope
pattern. Deterministic and provider-free.

Run from the repository root:

    python -X utf8 -B docs/v3/research-lane/dot-ra-rd-20261002/check_intake.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.check_public_scope import PATTERN as FORBIDDEN  # noqa: E402

TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv"}


def dest_for(original: str) -> Path:
    """Map a manifest original relative path to its copied location."""
    return (ROOT / "raw" / original) if "/" in original else (ROOT / original)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main() -> int:
    errors: list[str] = []

    manifest_path = ROOT / "MANIFEST.json"
    if not manifest_path.exists():
        print("FAIL: dot RA/RD intake gate")
        print(" - missing: MANIFEST.json")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    copied: list[Path] = []
    present = 0
    for entry in manifest.get("files", []):
        original = entry["path"]
        if original.lower().endswith(".docx"):
            continue
        path = dest_for(original)
        copied.append(path)
        if not path.exists():
            errors.append(
                f"missing copied file: {path.relative_to(ROOT).as_posix()} (from {original})"
            )
            continue
        present += 1
        if path.suffix.lower() in TEXT_SUFFIXES:
            actual = sha256(path)
            expected = entry.get("sha256")
            if actual != expected:
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}: sha256 mismatch "
                    f"(expected {expected}, got {actual})"
                )

    for path in sorted((ROOT / "raw").rglob("*.docx")):
        errors.append(f"unexpected .docx under raw/: {path.relative_to(ROOT).as_posix()}")

    scanned = [p for p in copied if p.exists() and p.suffix.lower() in TEXT_SUFFIXES]
    scanned.append(manifest_path)
    seen: set[Path] = set()
    for path in scanned:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        for match in FORBIDDEN.finditer(text):
            errors.append(f"{rel}: foreign identifier '{match.group(0)}'")

    if errors:
        print("FAIL: dot RA/RD intake gate")
        for error in errors:
            print(" -", error)
        return 1
    print(
        f"PASS: {present} copied files present, {len(seen)} scanned "
        "(sha256 + identifiers), no .docx under raw/"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
