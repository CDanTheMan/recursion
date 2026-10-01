#!/usr/bin/env python3
"""Deterministic gate for the cross-lane research synthesis layer.

Verifies the synthesis documents exist, carry their required sections, resolve their relative
links, and contain no foreign-project identifiers or obvious secrets. Reuses the repository's
public-scope pattern so the checks cannot drift. No network, no model.

Run from the repository root:

    python -X utf8 -B docs/v3/research-lane/check_synthesis.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.check_public_scope import PATTERN as FORBIDDEN  # noqa: E402

SECRET = re.compile(r"sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

REQUIRED = {
    "SYNTHESIS.md": [
        "## Decision-first summary",
        "## Lane coverage",
        "## Consolidated open Owner decisions",
        "## Gap register (summary)",
        "## What must be settled before architecture",
    ],
    "GAPS.md": ["## Priority P1 first actions", "## Follow-up prompts"],
    "synthesis/domain-A-kernel-language-platform.md": [],
    "synthesis/domain-B-authority-safety-lifecycle.md": [],
    "synthesis/domain-C-operations-capacity-evaluation.md": [],
    "synthesis/domain-D-context-interaction-product.md": [],
}
DOMAIN_SECTIONS = ["## Lane digests", "## Domain gaps and open unknowns"]


def main() -> int:
    errors: list[str] = []

    for rel, headings in REQUIRED.items():
        path = ROOT / rel
        if not path.exists():
            errors.append(f"missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for heading in headings:
            if heading not in text:
                errors.append(f"{rel}: missing heading '{heading}'")
        if rel.startswith("synthesis/domain-"):
            for heading in DOMAIN_SECTIONS:
                if heading not in text:
                    errors.append(f"{rel}: missing heading '{heading}'")

    for path in [ROOT / r for r in REQUIRED if (ROOT / r).exists()]:
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
        print("FAIL: synthesis gate")
        for error in errors:
            print(" -", error)
        return 1
    print("PASS: master synthesis, gap register and 4 domain syntheses present, sections/links/scan clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
