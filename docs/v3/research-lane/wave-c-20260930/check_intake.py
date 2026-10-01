#!/usr/bin/env python3
"""Deterministic gate for the Wave C Deep Research intake.

Verifies expected files, raw provenance labels, synthesis sections, resolving relative links,
and absence of foreign-project identifiers or obvious secrets. Reuses the repository's
public-scope pattern so the checks cannot drift. No network, no model.

Run from the repository root:

    python -X utf8 -B docs/v3/research-lane/wave-c-20260930/check_intake.py
"""
from __future__ import annotations

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
    "ds-DS-05-migration-rollback.md",
    "ds-DS-10-performance.md",
    "ds-DS-11-routing-delegation.md",
    "ds-DS-12-context-cache.md",
    "ds-DS-13-configuration.md",
    "ds-DS-14-scientific-arm.md",
    "ds-DS-30-multi-project-memory.md",
    "ds-DS-32-hitl-approvals.md",
    "ds-DS-33-licensing-ip.md",
    "ds-DS-34-decision-journaling.md",
    "ds-DS-15-arm-conversations.md",
]
SYNTHESIS = [
    "DS-05-migration-rollback.md",
    "DS-10-performance.md",
    "DS-11-routing-delegation.md",
    "DS-12-context-cache.md",
    "DS-13-configuration.md",
    "DS-14-scientific-arm.md",
    "DS-30-multi-project-memory.md",
    "DS-32-hitl-approvals.md",
    "DS-33-licensing-ip.md",
    "DS-34-decision-journaling.md",
    "DS-15-arm-conversations.md",
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
        for heading in ("## Provenance", "## Key findings"):
            if heading not in text:
                errors.append(f"synthesis/{name}: missing heading '{heading}'")
        if "## What this does not prove" not in text and "## What this does not establish" not in text:
            errors.append(f"synthesis/{name}: missing a '## What this does not prove' / '...establish' section")

    scan_paths = (
        list((ROOT / "raw").glob("*.md"))
        + list((ROOT / "synthesis").glob("*.md"))
        + list((ROOT / "failed").glob("*.md"))
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
        print("FAIL: Wave C intake gate")
        for error in errors:
            print(" -", error)
        return 1
    print(f"PASS: {len(RAW)} raw labeled, {len(SYNTHESIS)} syntheses, links/scan clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
