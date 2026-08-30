"""Adversarial tests for the JSON loader embedded in worker-sandbox.sh."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SANDBOX = ROOT / "scripts" / "worker-sandbox.sh"


def loader_source() -> str:
    source = SANDBOX.read_text(encoding="utf-8")
    start_marker = "<<'PY' || true\n"
    end_marker = "\nPY\n)"
    start = source.index(start_marker) + len(start_marker)
    end = source.index(end_marker, start)
    return source[start:end]


def run_loader(value: object, label: str) -> subprocess.CompletedProcess[str]:
    plan = Path(tempfile.gettempdir()) / f"worker-sandbox-plan-{os.getpid()}-{label}.json"
    try:
        plan.write_text(json.dumps(value) + "\n", encoding="utf-8")
        return subprocess.run(
            [sys.executable, "-", str(plan), "stubeng"],
            input=loader_source(), capture_output=True, text=True,
        )
    finally:
        plan.unlink(missing_ok=True)


def main() -> int:
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        print(("ok - " if condition else "FAIL - ") + label)
        if not condition:
            failures.append(label)

    for value, label, suffix in (([], "JSON array plan root", "array"),
                                 (None, "JSON null plan root", "null")):
        result = run_loader(value, suffix)
        check(result.returncode == 92, f"{label} exits through controlled invalid-plan path")
        check("Traceback" not in result.stderr, f"{label} does not leak a traceback")

    result = run_loader({"schema_version": True}, "boolean")
    check(result.returncode == 92, "boolean plan schema_version exits through controlled invalid-plan path")
    check("Traceback" not in result.stderr, "boolean plan schema_version does not leak a traceback")

    if failures:
        print(f"worker-sandbox-plan.test: {len(failures)} FAILED")
        return 1
    print("worker-sandbox-plan.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
