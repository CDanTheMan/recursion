#!/usr/bin/env python3
"""FU-03 Session A enlarged-bound mutant battery.

Starts from RFixed.tla (reconciled guard applied) and, for every ds-FU-03
mutant the model can instantiate, applies exactly one controlled textual
semantic edit, refuses non-unique sites, runs TLC, and classifies the result
(KILLED / NOT_KILLED_WITHIN_BOUND / INCONCLUSIVE). Rows the model cannot
instantiate are recorded as NEEDS_LARGER_BOUND or NOT_YET_IMPLEMENTED with a
one-line reason. All 36 registry ids receive a receipt.

Diagnostic only, NOT the accepted integrated gate.

    python -X utf8 -B experiments/v3/fu-03-kernel-session-a/model/mutants.py
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
JAR = ROOT / "tools" / "tlaplus" / "tla2tools.jar"
PINNED = "936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"
RESULTS = HERE / "results"
REGISTRY = HERE.parent / "mutants-registry.json"
BASE_MODULE = "RFixed"

INSTANTIABLE = [
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
    {"id": "M19", "name": "RETRY_ATTEMPT_WEAKEN",
     "old": "AttemptBoundOK == attempt < 2", "new": "AttemptBoundOK == attempt <= 2",
     "expect": "RetryBound"},
    {"id": "M20", "name": "RETRY_TIMER_DELETE",
     "old": "RetryTimerOK == retryReady", "new": "RetryTimerOK == TRUE",
     "expect": "RetrySafety"},
    {"id": "M24", "name": "EFFECT_PREPARE_OMIT",
     "old": 'DispatchPreparedOK == eff.status = "Prepared"',
     "new": "DispatchPreparedOK == TRUE", "expect": "EffectSafety"},
    {"id": "M25", "name": "BLIND_EFFECT_REPLAY",
     "old": 'FireTimerEffectOK == eff.status \\in {"None", "KnownNoEffect"}',
     "new": "FireTimerEffectOK == TRUE", "expect": "NoBlindEffectReplay"},
    {"id": "M26", "name": "VERIFIER_SELF_ALLOW",
     "old": 'VerifierOK == producer # "w2"', "new": "VerifierOK == TRUE",
     "expect": "VerifierSafety"},
    {"id": "M27", "name": "VERIFIER_RESULT_UNBOUND",
     "old": "AcceptedVerifierResult == result", "new": 'AcceptedVerifierResult == "R2"',
     "expect": "VerifierSafety"},
    {"id": "M31", "name": "FLOW_OFF_BY_ONE",
     "old": "OutboxOK == Len(outbox) < Cap", "new": "OutboxOK == Len(outbox) <= Cap",
     "expect": "FlowBound"},
]
INSTANTIABLE_BY_ID = {m["id"]: m for m in INSTANTIABLE}


def java_exe() -> str:
    found = shutil.which("java")
    if found:
        return found
    for base in (Path("C:/Program Files/Eclipse Adoptium"), Path("C:/Program Files/Eclipse Foundation")):
        if base.exists():
            for cand in sorted(base.glob("*/bin/java.exe")):
                return str(cand)
    raise SystemExit("java not found")


def final_states_line(text: str) -> str:
    matches = re.findall(r"^\d+ states generated.*$", text, re.MULTILINE)
    return matches[-1].strip() if matches else ""


def run_tlc(module: str) -> tuple[int | None, str]:
    out = RESULTS / f"{module}.out"
    metadir = RESULTS / f"metadir_{module}"
    cmd = [java_exe(), "-Xmx4g", "-cp", str(JAR), "tlc2.TLC",
           "-config", f"{module}.cfg", "-cleanup", "-metadir", str(metadir), f"{module}.tla"]
    try:
        proc = subprocess.run(cmd, cwd=HERE, capture_output=True, encoding="utf-8",
                              errors="replace", timeout=600)
        text = (proc.stdout or "") + (proc.stderr or "")
        rc: int | None = proc.returncode
    except subprocess.TimeoutExpired as exc:
        text = ((exc.stdout or "") + (exc.stderr or "")) if isinstance(exc.stdout, str) else ""
        rc = None
    out.write_text(text, encoding="utf-8")
    return rc, text


def classify(rc: int | None, text: str) -> tuple[str, str | None]:
    match = re.search(r"Error: Invariant (\S+) is violated", text)
    if match:
        return "KILLED", match.group(1)
    if "No error has been found" in text:
        return "NOT_KILLED_WITHIN_BOUND", None
    if rc is None:
        return "INCONCLUSIVE_TIMEOUT", None
    return "INCONCLUSIVE", None


def main() -> int:
    if not JAR.exists() or hashlib.sha256(JAR.read_bytes()).hexdigest() != PINNED:
        raise SystemExit("TLA+ jar missing or digest mismatch")
    if not (HERE / f"{BASE_MODULE}.tla").exists():
        raise SystemExit(f"missing base module {BASE_MODULE}.tla")
    RESULTS.mkdir(exist_ok=True)
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registered = {m["id"]: m for m in registry["mutants"]}
    base = (HERE / f"{BASE_MODULE}.tla").read_text(encoding="utf-8")
    base_cfg = (HERE / f"{BASE_MODULE}.cfg").read_text(encoding="utf-8")

    receipts = []
    for row in registry["mutants"]:
        mutant_id = row["id"]
        if mutant_id not in INSTANTIABLE_BY_ID:
            receipts.append({
                "mutant_id": mutant_id, "name": row["name"],
                "site_old": None, "site_new": None,
                "expected_invariant": row["expected_invariant"],
                "violated_invariant": None,
                "disposition": row["disposition"] if row["disposition"] in
                               ("NEEDS_LARGER_BOUND", "NOT_YET_IMPLEMENTED") else "NOT_YET_IMPLEMENTED",
                "exit_code": None, "states": "", "module_sha256": None,
                "reason": row.get("notes", "model cannot instantiate this site"),
            })
            continue

        spec = INSTANTIABLE_BY_ID[mutant_id]
        if base.count(spec["old"]) != 1:
            raise SystemExit(f"{mutant_id}: mutation site not unique "
                             f"({base.count(spec['old'])}) in {BASE_MODULE}.tla")
        module = f"RMut_{mutant_id}"
        src = base.replace(spec["old"], spec["new"]).replace(
            f"MODULE {BASE_MODULE}", f"MODULE {module}")
        (HERE / f"{module}.tla").write_text(src, encoding="utf-8")
        (HERE / f"{module}.cfg").write_text(base_cfg, encoding="utf-8")

        rc, text = run_tlc(module)
        disposition, violated = classify(rc, text)
        receipts.append({
            "mutant_id": mutant_id, "name": spec["name"],
            "site_old": spec["old"], "site_new": spec["new"],
            "expected_invariant": spec["expect"], "violated_invariant": violated,
            "disposition": disposition, "exit_code": rc,
            "states": final_states_line(text),
            "module_sha256": hashlib.sha256(src.encode("utf-8")).hexdigest(),
            "output_file": f"results/{module}.out",
        })
        print(f"{mutant_id:<4} {spec['name']:<22} {disposition:<22} {final_states_line(text)}")

    killed = sum(1 for r in receipts if r["disposition"] == "KILLED")
    report = {
        "model": "RFixed enlarged bound (CmdIds=1..10, MaxEvents=12, Cap=3; NOT the integrated gate)",
        "jar_sha256": PINNED,
        "registry_ids": len(registered),
        "mutants_instantiated": sum(1 for r in receipts if r.get("module_sha256")),
        "killed": killed,
        "receipts": receipts,
    }
    (RESULTS / "mutants.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n{report['mutants_instantiated']} instantiated; {killed} killed; "
          f"{len(receipts)} registry rows dispositioned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
