#!/usr/bin/env python3
"""FU-03 Session A gate: registry + oracle + reconciled model.

Deterministic and provider-free. Validates the reconciliation artifacts and runs the oracle gate.

    python -X utf8 -B experiments/v3/fu-03-kernel-session-a/check_session_a.py

A pass certifies the artifacts are present and internally consistent and that the independent
oracle gates pass. It is NOT the 36/36 acceptance metric, not a kernel freeze, and not the
integrated bound.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

REQUIRED = [
    "mutants-registry.json", "RECONCILIATION.md", "FIXTURE-QUALIFICATION.md",
    "oracle/refstate.py", "oracle/trace_checker.py", "oracle/check_oracle.py",
    "oracle/vectors/vectors.json", "oracle/README.md",
    "model/RBig.tla", "model/RFixed.tla", "model/mutants.py", "model/check_model.py",
    "model/results/baseline-witness.json", "model/results/mutants.json",
]

ALL_IDS = [f"M{n:02d}" for n in range(1, 37)]


def fail(message: str) -> None:
    print(f"SESSION_A_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    for rel in REQUIRED:
        if not (HERE / rel).exists():
            fail(f"missing artifact: {rel}")

    registry = json.loads((HERE / "mutants-registry.json").read_text(encoding="utf-8"))
    rows = registry if isinstance(registry, list) else registry.get("mutants", registry.get("rows", []))
    ids = [r.get("id") for r in rows]
    if sorted(ids) != ALL_IDS:
        fail(f"registry must contain exactly M01..M36; got {len(ids)} rows")

    model = json.loads((HERE / "model" / "results" / "mutants.json").read_text(encoding="utf-8"))
    receipts = model if isinstance(model, list) else model.get("receipts", model.get("mutants", []))
    model_ids = {r.get("id", r.get("mutant_id")): r.get("disposition") for r in receipts}
    if set(model_ids) != set(ALL_IDS):
        fail(f"model results must disposition all 36 ids; got {len(model_ids)}")
    if model_ids.get("M25") != "KILLED":
        fail("M25 must be KILLED by the reconciled model")
    if not model_ids.get("M31"):
        fail("M31 must carry an explicit disposition")

    witness = json.loads((HERE / "model" / "results" / "baseline-witness.json").read_text(encoding="utf-8"))
    if "NoBlindEffectReplay" not in json.dumps(witness):
        fail("baseline witness must record the NoBlindEffectReplay violation")

    oracle = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(HERE / "oracle" / "check_oracle.py")],
        cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace",
    )
    if oracle.returncode != 0:
        print(oracle.stdout)
        print(oracle.stderr, file=sys.stderr)
        fail("oracle gate failed")

    killed = sum(1 for d in model_ids.values() if d == "KILLED")
    print(f"SESSION_A_PASS registry={len(ids)} model_dispositioned={len(model_ids)} "
          f"killed={killed} M25=KILLED M31={model_ids['M31']} witness=NoBlindEffectReplay "
          f"oracle_exit={oracle.returncode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
