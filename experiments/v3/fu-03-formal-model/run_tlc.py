#!/usr/bin/env python3
"""Run TLC on the reduced-bound kernel model and on one mutant.

Deterministic, provider-free, local only. Pins the tla2tools.jar digest before running, so the
run identity cannot silently change. Writes results/ with raw TLC output and a JSON summary.

    python -X utf8 -B experiments/v3/fu-03-formal-model/run_tlc.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JAR = ROOT / "tools" / "tlaplus" / "tla2tools.jar"
PINNED_JAR_SHA256 = "936a262061c914694dfd669a543be24573c45d5aa0ff20a8b96b23d01e050e88"
RESULTS = HERE / "results"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def java_exe() -> str:
    found = shutil.which("java")
    if found:
        return found
    for base in (Path("C:/Program Files/Eclipse Adoptium"), Path("C:/Program Files/Eclipse Foundation")):
        if base.exists():
            for cand in sorted(base.glob("*/bin/java.exe")):
                return str(cand)
    raise SystemExit("java not found on PATH or in Eclipse Adoptium install locations")


def run_model(module: str, config: str) -> dict:
    """Run TLC with an explicit heap cap; return a structured result."""
    out = RESULTS / f"{module}.out"
    metadir = RESULTS / f"metadir_{module}"
    cmd = [java_exe(), "-Xmx1g", "-cp", str(JAR), "tlc2.TLC",
           "-config", config, "-cleanup", "-metadir", str(metadir), module + ".tla"]
    proc = subprocess.run(cmd, cwd=HERE, capture_output=True, encoding="utf-8",
                          errors="replace", timeout=600)
    text = (proc.stdout or "") + (proc.stderr or "")
    out.write_text(text, encoding="utf-8")
    violated = "is violated" in text
    no_error = ("No error has been found" in text) or (proc.returncode == 0 and not violated)
    summary = {
        "module": module,
        "config": config,
        "jar_sha256": sha256(JAR),
        "java": java_exe(),
        "command": cmd,
        "exit_code": proc.returncode,
        "no_error": no_error,
        "invariant_violated": violated,
        "output_file": str(out.relative_to(ROOT)).replace("\\", "/"),
    }
    for line in text.splitlines():
        if "states generated" in line or "distinct states found" in line or "is violated" in line:
            summary.setdefault("notable", []).append(line.strip())
    return summary


def main() -> int:
    if not JAR.exists():
        raise SystemExit(f"missing TLA+ jar: {JAR}")
    actual = sha256(JAR)
    if actual != PINNED_JAR_SHA256:
        raise SystemExit(f"TLA+ jar digest mismatch: {actual} != {PINNED_JAR_SHA256}")
    RESULTS.mkdir(exist_ok=True)
    report = {
        "model": "R kernel reduced bound (CmdIds=1..3, MaxEvents=6)",
        "evidence_class": "inference/design; reduced bound; not the integrated gate",
        "jar_sha256": actual,
        "baseline": run_model("RKernel", "RKernel.cfg"),
        "mutant": run_model("RMutant", "RMutant.cfg"),
    }
    (RESULTS / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
