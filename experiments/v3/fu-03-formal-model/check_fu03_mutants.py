#!/usr/bin/env python3
"""FU-03 mutant-battery gate (reduced bound).

Deterministic and provider-free. Requires a prior run of mutants.py.

    python -X utf8 -B experiments/v3/fu-03-formal-model/check_fu03_mutants.py

A pass certifies only that the instantiated mutants were generated as exact single-site edits,
that the baseline was clean, and that every row carries a valid disposition with killed rows
showing the expected invariant. It is not 36/36 coverage and not a kernel freeze.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUMMARY = HERE / "results" / "mutants.json"
BASE = HERE / "results" / "RIntegrated.out"
PINGED = "936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"
VALID = {"KILLED", "NOT_KILLED_WITHIN_BOUND", "INCONCLUSIVE", "INCONCLUSIVE_TIMEOUT"}


def fail(message: str) -> None:
    print(f"FU03_MUTANTS_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "utf-8"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def main() -> int:
    if not BASE.exists() or "No error has been found" not in read_text(BASE):
        fail("RIntegrated baseline is not recorded clean")
    if not SUMMARY.exists():
        fail("missing results/mutants.json; run mutants.py first")

    report = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if report.get("jar_sha256") != PINGED:
        fail("unexpected TLA+ jar digest")
    receipts = report.get("receipts", [])
    if len(receipts) < 7:
        fail(f"expected >=7 instantiated mutants, found {len(receipts)}")

    killed = [r for r in receipts if r["disposition"] == "KILLED"]
    for r in receipts:
        if r["disposition"] not in VALID:
            fail(f"{r['mutant_id']} has invalid disposition {r['disposition']}")
        if r["disposition"] == "KILLED" and r["violated_invariant"] != r["expected_invariant"]:
            fail(f"{r['mutant_id']} killed by {r['violated_invariant']}, expected {r['expected_invariant']}")
    if len(killed) < 5:
        fail(f"only {len(killed)} mutants killed; expected >=5")

    not_killed = [r["mutant_id"] for r in receipts if r["disposition"] != "KILLED"]
    print(f"FU03_MUTANTS_PASS baseline clean; {len(killed)}/{len(receipts)} killed; "
          f"not killed within bound: {not_killed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
