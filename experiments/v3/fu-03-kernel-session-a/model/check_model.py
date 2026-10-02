#!/usr/bin/env python3
"""FU-03 Session A enlarged-bound model gate.

Requires a prior run of run_baselines.py and mutants.py. Certifies only:
  * the RBig baseline result is recorded (a recorded NoBlindEffectReplay
    witness, or a clean exit);
  * the RFixed baseline is clean;
  * M25 is KILLED; M31 carries a non-empty disposition;
  * every KILLED row was killed by its expected invariant;
  * all 36 registry ids appear with a disposition.

Diagnostic only: NOT the accepted integrated gate, not a kernel freeze.

    python -X utf8 -B experiments/v3/fu-03-kernel-session-a/model/check_model.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RESULTS = HERE / "results"
REGISTRY = HERE.parent / "mutants-registry.json"
PINNED = "936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"
VALID = {"KILLED", "NOT_KILLED_WITHIN_BOUND", "INCONCLUSIVE", "INCONCLUSIVE_TIMEOUT",
         "NEEDS_LARGER_BOUND", "NOT_YET_IMPLEMENTED"}


def fail(message: str) -> None:
    print(f"MODEL_FAIL: {message}", file=sys.stderr)
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
    for name in ("RBig.tla", "RBig.cfg", "RFixed.tla", "RFixed.cfg",
                 "mutants.py", "run_baselines.py"):
        if not (HERE / name).exists():
            fail(f"missing artifact: {name}")

    witness_path = RESULTS / "baseline-witness.json"
    rbig_out = RESULTS / "RBig.out"
    if not rbig_out.exists():
        fail("missing results/RBig.out; run run_baselines.py first")
    rbig_text = read_text(rbig_out)
    if witness_path.exists():
        witness = json.loads(witness_path.read_text(encoding="utf-8"))
        violated = witness.get("violated_invariant")
        if not violated:
            fail("baseline-witness.json records no violated invariant")
        if violated != "NoBlindEffectReplay":
            fail(f"RBig witness violates {violated}, expected NoBlindEffectReplay")
    elif "No error has been found" not in rbig_text:
        fail("RBig baseline is neither clean nor a recorded witness")

    fixed_out = RESULTS / "RFixed.out"
    if not fixed_out.exists():
        fail("missing results/RFixed.out; run run_baselines.py first")
    fixed_text = read_text(fixed_out)
    if "is violated" in fixed_text or "No error has been found" not in fixed_text:
        fail("RFixed baseline is not clean")

    mutants_path = RESULTS / "mutants.json"
    if not mutants_path.exists():
        fail("missing results/mutants.json; run mutants.py first")
    report = json.loads(mutants_path.read_text(encoding="utf-8"))
    if report.get("jar_sha256") != PINNED:
        fail("unexpected TLA+ jar digest in mutants.json")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registry_ids = [m["id"] for m in registry["mutants"]]
    if len(registry_ids) != 36:
        fail(f"expected 36 registry rows, found {len(registry_ids)}")
    receipts = {r["mutant_id"]: r for r in report.get("receipts", [])}
    missing = [i for i in registry_ids if i not in receipts]
    if missing:
        fail(f"registry ids missing from mutants.json: {missing}")

    for row in receipts.values():
        if row.get("disposition") not in VALID:
            fail(f"{row['mutant_id']} has invalid disposition {row.get('disposition')!r}")
    if receipts["M25"].get("disposition") != "KILLED":
        fail("M25 must be KILLED by the reconciled model")
    if not receipts["M31"].get("disposition"):
        fail("M31 has an empty disposition")
    for row in receipts.values():
        if row["disposition"] == "KILLED" and row.get("violated_invariant") != row.get("expected_invariant"):
            fail(f"{row['mutant_id']} killed by {row.get('violated_invariant')}, "
                 f"expected {row.get('expected_invariant')}")

    killed = sum(1 for r in receipts.values() if r["disposition"] == "KILLED")
    print(f"MODEL_PASS RBig baseline recorded ({'witness' if witness_path.exists() else 'clean'}); "
          f"RFixed clean; M25={receipts['M25']['disposition']} "
          f"M31={receipts['M31']['disposition']}; {killed} killed; "
          f"all {len(registry_ids)} registry ids dispositioned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
