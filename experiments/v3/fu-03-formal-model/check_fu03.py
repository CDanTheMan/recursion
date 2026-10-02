#!/usr/bin/env python3
"""FU-03 experiment gate: baseline must pass, mutant M02 must be killed.

Deterministic and provider-free. Requires a prior run of run_tlc.py.

    python -X utf8 -B experiments/v3/fu-03-formal-model/check_fu03.py

A pass certifies only that the reduced-bound baseline checked clean and that one named mutant
produced a counterexample. It is not the integrated-bound acceptance, not 36/36 mutant coverage,
not a byte-vector reproduction, and not a kernel freeze.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUMMARY = HERE / "results" / "summary.json"

REQUIRED = [
    "RKernel.tla", "RKernel.cfg", "RMutant.tla", "RMutant.cfg",
    "run_tlc.py", "check_fu03.py", "README.md",
]


def fail(message: str) -> None:
    print(f"FU03_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    for name in REQUIRED:
        if not (HERE / name).exists():
            fail(f"missing artifact: {name}")
    if not SUMMARY.exists():
        fail("missing results/summary.json; run run_tlc.py first")

    report = json.loads(SUMMARY.read_text(encoding="utf-8"))
    baseline = report.get("baseline", {})
    mutant = report.get("mutant", {})

    if baseline.get("jar_sha256") != "936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88":
        fail("unexpected TLA+ jar digest")
    if not baseline.get("no_error"):
        fail("baseline did not complete without error")
    if not mutant.get("invariant_violated"):
        fail("mutant M02 CHAIN_PREV_DELETE was not killed (no invariant violation)")

    print("FU03_PASS reduced-bound baseline clean; mutant M02 killed by ChainIntegrity")
    print(f"  baseline exit={baseline.get('exit_code')} mutant exit={mutant.get('exit_code')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
