#!/usr/bin/env python3
"""Deterministic gate for the 2026-10-02 follow-up intake.

Verifies the expected reports and syntheses, raw provenance labels, synthesis sections, the
FU-04 machine specifications (valid JSON), resolving relative links, and absence of
foreign-project identifiers or obvious secrets. Reuses the repository's public-scope pattern.

Run from the repository root:

    python -X utf8 -B docs/v3/research-lane/followups-20261002/check_intake.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.check_public_scope import PATTERN as FORBIDDEN  # noqa: E402

SECRET = re.compile(r"sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

RAW = [
    "ds-FU-01-language-runtime.md",
    "ds-FU-02-store-crash-replay.md",
    "ds-FU-03-formal-model-vectors.md",
    "ds-FU-04-os-conformance.md",
    "ds-FU-05-broker-chaos.md",
    "ds-batch-supporting-review.md",
    "ds-architecture-audit.md",
]
SYNTHESIS = [
    "FU-01-language-runtime.md",
    "FU-02-store-crash-replay.md",
    "FU-03-formal-model-vectors.md",
    "FU-04-os-conformance.md",
    "FU-05-broker-chaos.md",
    "batch-supporting-review.md",
    "architecture-audit.md",
]
MACHINE = [
    "platform-manifest.json",
    "platform-manifest.schema.json",
    "negative-traces.json",
    "negative-traces.schema.json",
    "profile-fields.json",
    "source-register.json",
]


def main() -> int:
    errors: list[str] = []

    for name in RAW:
        path = ROOT / "raw" / name
        if not path.exists():
            errors.append(f"missing raw report: raw/{name}")
            continue
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:12])
        if "status: research-evidence-not-a-decision" not in head:
            errors.append(f"raw/{name}: missing provenance label")
        if "verification:" not in head:
            errors.append(f"raw/{name}: missing `verification:` field")

    for name in SYNTHESIS:
        path = ROOT / "synthesis" / name
        if not path.exists():
            errors.append(f"missing synthesis: synthesis/{name}")
            continue
        text = path.read_text(encoding="utf-8")
        for heading in ("## Provenance",):
            if heading not in text:
                errors.append(f"synthesis/{name}: missing heading '{heading}'")
        if ("## What this does not prove" not in text
                and "## What this does not establish" not in text):
            errors.append(f"synthesis/{name}: missing a 'what this does not prove' section")

    for name in MACHINE:
        path = ROOT / "machine" / name
        if not path.exists():
            errors.append(f"missing machine spec: machine/{name}")
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"machine/{name}: invalid JSON ({exc})")

    for name in ("MANIFEST.json", "START-HERE.txt"):
        if not (ROOT / name).exists():
            errors.append(f"missing: {name}")

    scan_paths = (
        list((ROOT / "raw").glob("*.md"))
        + list((ROOT / "synthesis").glob("*.md"))
        + [ROOT / "README.md"]
    )
    for path in scan_paths:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        for match in FORBIDDEN.finditer(text):
            errors.append(f"{rel}: foreign identifier '{match.group(0)}'")
        if SECRET.search(text):
            errors.append(f"{rel}: possible secret material")
        for target in LINK.findall(text):
            target = target.split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not (path.parent / target).exists():
                errors.append(f"{rel}: relative link does not resolve: {target}")

    if errors:
        print("FAIL: follow-up batch intake gate")
        for error in errors:
            print(" -", error)
        return 1
    print(f"PASS: {len(RAW)} raw labeled, {len(SYNTHESIS)} syntheses, {len(MACHINE)} machine specs valid, links/scan clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
