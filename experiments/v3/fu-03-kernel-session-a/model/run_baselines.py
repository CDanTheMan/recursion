#!/usr/bin/env python3
"""Run the enlarged FU-03 Session A baselines.

Step 1: RBig (unfixed witness-step guard) -- either clean or a recorded
        NoBlindEffectReplay counterexample in results/baseline-witness.json.
Step 2: RFixed (reconciled guard) -- must be clean.

Diagnostic only, NOT the accepted integrated gate. Pins the tla2tools.jar
digest before running.

    python -X utf8 -B experiments/v3/fu-03-kernel-session-a/model/run_baselines.py
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


def java_exe() -> str:
    found = shutil.which("java")
    if found:
        return found
    for base in (Path("C:/Program Files/Eclipse Adoptium"), Path("C:/Program Files/Eclipse Foundation")):
        if base.exists():
            for cand in sorted(base.glob("*/bin/java.exe")):
                return str(cand)
    raise SystemExit("java not found")


def run_model(module: str, config: str) -> tuple[int, str]:
    out = RESULTS / f"{module}.out"
    metadir = RESULTS / f"metadir_{module}"
    cmd = [java_exe(), "-Xmx4g", "-cp", str(JAR), "tlc2.TLC",
           "-config", config, "-cleanup", "-metadir", str(metadir), module + ".tla"]
    proc = subprocess.run(cmd, cwd=HERE, capture_output=True, encoding="utf-8",
                          errors="replace", timeout=900)
    text = (proc.stdout or "") + (proc.stderr or "")
    out.write_text(text, encoding="utf-8")
    return proc.returncode, text


def parse_violation(text: str) -> str | None:
    match = re.search(r"Error: Invariant (\S+) is violated", text)
    return match.group(1) if match else None


def parse_trace(text: str) -> tuple[list[dict], str]:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if "behavior up to this point is" in line:
            start = index + 1
            break
    if start is None:
        return [], ""
    block: list[str] = []
    for line in lines[start:]:
        if re.match(r"^\d+ states generated", line) or line.startswith("The depth of") or line.startswith("Error:"):
            break
        block.append(line)
    trace = "\n".join(block).rstrip()
    states = []
    for line in block:
        match = re.match(r"^State (\d+): <(.*)>$", line)
        if match:
            states.append({"state": int(match.group(1)), "action": match.group(2)})
    return states, trace


def main() -> int:
    if not JAR.exists() or hashlib.sha256(JAR.read_bytes()).hexdigest() != PINNED:
        raise SystemExit("TLA+ jar missing or digest mismatch")
    RESULTS.mkdir(exist_ok=True)
    report: dict = {"jar_sha256": PINNED,
                    "model": "RBig/RFixed enlarged diagnostic; NOT the integrated gate"}

    rc_big, text_big = run_model("RBig", "RBig.cfg")
    viol_big = parse_violation(text_big)
    report["RBig"] = {"exit_code": rc_big, "violated_invariant": viol_big,
                      "no_error": "No error has been found" in text_big}
    if viol_big:
        states, trace = parse_trace(text_big)
        witness = {
            "model": "RBig", "config": "RBig.cfg", "jar_sha256": PINNED,
            "module_sha256": hashlib.sha256((HERE / "RBig.tla").read_bytes()).hexdigest(),
            "exit_code": rc_big, "violated_invariant": viol_big,
            "trace_length_states": len(states), "steps": len(states) - 1,
            "states": states,
            "packet_claimed_trace": ["GrantLease", "Start", "PrepareEffect", "MarkDispatch",
                                     "SubmitFail", "ArmTimer", "FireTimer"],
            "note": ("TLC breadth-first counterexample; the final state has eff InFlight while "
                     "retryReady = TRUE, violating NoBlindEffectReplay. TLC reached a 7-step "
                     "trace with MarkDispatch last; the packet's inferred order places MarkDispatch "
                     "earlier. Both leave the effect InFlight when the timer arms retry."),
            "trace_text": trace,
        }
        (RESULTS / "baseline-witness.json").write_text(json.dumps(witness, indent=2), encoding="utf-8")
        report["RBig"]["witness_recorded"] = True
    else:
        (RESULTS / "baseline-witness.json").unlink(missing_ok=True)

    rc_fix, text_fix = run_model("RFixed", "RFixed.cfg")
    viol_fix = parse_violation(text_fix)
    report["RFixed"] = {"exit_code": rc_fix, "violated_invariant": viol_fix,
                        "no_error": "No error has been found" in text_fix}

    (RESULTS / "baselines.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
