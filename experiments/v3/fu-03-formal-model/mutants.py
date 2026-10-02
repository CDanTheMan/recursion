#!/usr/bin/env python3
"""Generate single-site mutants of RIntegrated.tla, run TLC on each, and classify.

Each mutant is exactly one controlled textual semantic edit (ds-FU-03 section 6 style). The
generator refuses if the mutation site is not found exactly once. Writes results/mutants.json
with a kill receipt per row.

    python -X utf8 -B experiments/v3/fu-03-formal-model/mutants.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JAR = ROOT / "tools" / "tlaplus" / "tla2tools.jar"
PINNED = "936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"
RESULTS = HERE / "results"

MUTANTS = [
    {"id": "M02", "name": "CHAIN_PREV_DELETE",
     "old": "p == IF ordinal = 0 THEN GENESIS ELSE log[ordinal].digest",
     "new": "p == GENESIS", "expect": "ChainIntegrity"},
    {"id": "M03", "name": "CHAIN_ORDINAL_WEAKEN",
     "old": "LET n == ordinal + 1", "new": "LET n == ordinal + 2", "expect": "TypeOK"},
    {"id": "M04", "name": "COMMAND_DEDUP_DELETE",
     "old": "Fresh(id) == receipts[id].used = FALSE", "new": "Fresh(id) == TRUE",
     "expect": "NoDuplicateIds"},
    {"id": "M16", "name": "PAUSE_GUARD_DELETE",
     "old": "WorkerProgressGuard == ~paused /\\ ~cancelled",
     "new": "WorkerProgressGuard == ~cancelled", "expect": "PauseNoProgress"},
    {"id": "M25", "name": "BLIND_EFFECT_REPLAY",
     "old": 'RetryEffectOK == eff.status \\in {"None", "KnownNoEffect"}',
     "new": "RetryEffectOK == TRUE", "expect": "NoBlindEffectReplay"},
    {"id": "M26", "name": "VERIFIER_SELF_ALLOW",
     "old": 'VerifierOK == producer # "w2"', "new": "VerifierOK == TRUE",
     "expect": "VerifierSafety"},
    {"id": "M31", "name": "FLOW_OFF_BY_ONE",
     "old": "OutboxOK == Len(outbox) < Cap", "new": "OutboxOK == Len(outbox) <= Cap",
     "expect": "FlowBound"},
]


def java_exe() -> str:
    found = shutil.which("java")
    if found:
        return found
    for base in (Path("C:/Program Files/Eclipse Adoptium"), Path("C:/Program Files/Eclipse Foundation")):
        if base.exists():
            for cand in sorted(base.glob("*/bin/java.exe")):
                return str(cand)
    raise SystemExit("java not found")


def main() -> int:
    if not JAR.exists() or hashlib.sha256(JAR.read_bytes()).hexdigest() != PINNED:
        raise SystemExit("TLA+ jar missing or digest mismatch")
    RESULTS.mkdir(exist_ok=True)
    base = (HERE / "RIntegrated.tla").read_text(encoding="utf-8")
    cfg = (HERE / "RIntegrated.cfg").read_text(encoding="utf-8")
    receipts = []
    for m in MUTANTS:
        if base.count(m["old"]) != 1:
            raise SystemExit(f"{m['id']}: mutation site not unique ({base.count(m['old'])})")
        mutant_src = base.replace(m["old"], m["new"])
        module = f"RMut_{m['id']}"
        mutant_src = mutant_src.replace("MODULE RIntegrated", f"MODULE {module}")
        (HERE / f"{module}.tla").write_text(mutant_src, encoding="utf-8")
        (HERE / f"{module}.cfg").write_text(cfg, encoding="utf-8")
        out = RESULTS / f"{module}.out"
        cmd = [java_exe(), "-Xmx1g", "-cp", str(JAR), "tlc2.TLC",
               "-config", f"{module}.cfg", "-cleanup",
               "-metadir", str(RESULTS / f"metadir_{module}"), f"{module}.tla"]
        try:
            proc = subprocess.run(cmd, cwd=HERE, capture_output=True, encoding="utf-8",
                                  errors="replace", timeout=300)
            text = (proc.stdout or "") + (proc.stderr or "")
            rc = proc.returncode
        except subprocess.TimeoutExpired as exc:
            text = ""
            rc = None
        out.write_text(text, encoding="utf-8")
        violated = None
        for line in text.splitlines():
            if "Error: Invariant" in line and "is violated" in line:
                violated = line.split("Invariant")[1].split("is violated")[0].strip()
        no_error = "No error has been found" in text
        if violated:
            disposition = "KILLED"
        elif no_error:
            disposition = "NOT_KILLED_WITHIN_BOUND"
        elif rc is None:
            disposition = "INCONCLUSIVE_TIMEOUT"
        else:
            disposition = "INCONCLUSIVE"
        states = next((l.strip() for l in text.splitlines() if "states generated" in l), "")
        receipts.append({
            "mutant_id": m["id"], "name": m["name"],
            "site_old": m["old"], "site_new": m["new"],
            "expected_invariant": m["expect"], "violated_invariant": violated,
            "disposition": disposition, "exit_code": rc,
            "states": states, "module_sha256": hashlib.sha256(mutant_src.encode()).hexdigest(),
            "output_file": f"results/{module}.out",
        })
        print(f"{m['id']:<4} {m['name']:<22} {disposition:<22} {states}")

    killed = sum(1 for r in receipts if r["disposition"] == "KILLED")
    report = {
        "model": "RIntegrated (reduced bound; NOT the integrated gate)",
        "jar_sha256": PINNED,
        "mutants_instantiated": len(receipts),
        "killed": killed,
        "receipts": receipts,
    }
    (RESULTS / "mutants.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n{killed}/{len(receipts)} instantiated mutants killed within this reduced bound")
    return 0


if __name__ == "__main__":
    sys.exit(main())
