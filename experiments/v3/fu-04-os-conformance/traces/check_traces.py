#!/usr/bin/env python3
"""FU-04 trace gate (deterministic, provider-free, stdlib only).

    python -X utf8 -B experiments/v3/fu-04-os-conformance/traces/check_traces.py

Certifies only that:

* ``traces.json`` covers all 20 PFxx fixtures, each with every required field;
* every executed (trace, target) run has an outcome in {pass, fail, unknown};
* any destructive trace that was not executed is explicitly ``not_run`` with a reason;
* no run is recorded as ``pass`` without present observation *and* recovery evidence
  (absence of a notification is never promoted to success).

It is not platform qualification and not a certification of any OS build.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACES = HERE / "traces.json"
RESULTS = HERE / "traces_results.json"
ALLOWED = {"pass", "fail", "unknown"}
CATALOG_OUTCOMES = {"pass", "fail", "unknown", "not_run"}
REQUIRED_FIELDS = (
    "id", "title", "target", "destructive", "injected_fault", "observation_oracle",
    "recovery_oracle", "stop_condition", "negative_control", "runs_now",
)
VALID_TARGETS = {"host", "wsl", "both", "none"}


def fail(message: str) -> None:
    print(f"TRACES_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def targets_for(trace: dict) -> list[str]:
    t = trace["target"]
    if t == "both":
        return ["host", "wsl:Debian"]
    if t == "host":
        return ["host"]
    if t == "wsl":
        return ["wsl:Debian"]
    return []


def has_evidence(oracle: object) -> bool:
    return isinstance(oracle, dict) and bool(oracle.get("evidence"))


def main() -> int:
    if not TRACES.exists():
        fail(f"missing {TRACES}")
    if not RESULTS.exists():
        fail(f"missing {RESULTS}; run run_traces.py first")

    catalog = json.loads(TRACES.read_text(encoding="utf-8"))
    traces = catalog.get("traces", [])
    ids = [t.get("id") for t in traces]
    expected = [f"PF{n:02d}" for n in range(1, 21)]
    if sorted(ids) != expected:
        fail(f"traces.json must cover exactly PF01..PF20; got {sorted(ids)}")

    for trace in traces:
        tid = trace.get("id")
        for field in REQUIRED_FIELDS:
            if field not in trace:
                fail(f"{tid}: missing required field {field!r}")
        if not isinstance(trace["destructive"], bool):
            fail(f"{tid}: destructive must be a boolean")
        if not isinstance(trace["runs_now"], bool):
            fail(f"{tid}: runs_now must be a boolean")
        if trace["target"] not in VALID_TARGETS:
            fail(f"{tid}: invalid target {trace['target']!r}")
        for field in ("title", "injected_fault", "observation_oracle", "recovery_oracle",
                      "stop_condition", "negative_control"):
            if not isinstance(trace[field], str) or not trace[field].strip():
                fail(f"{tid}: field {field!r} must be a non-empty string")
        if not trace["runs_now"]:
            reason = trace.get("unsupported_reason")
            if not isinstance(reason, str) or not reason.strip():
                fail(f"{tid}: runs_now is false but unsupported_reason is missing/empty")

    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    runs = results.get("runs", [])
    not_run = results.get("not_run", [])

    if not isinstance(runs, list) or not isinstance(not_run, list):
        fail("results must contain list runs and list not_run")

    executed: dict[str, set[str]] = {}
    for run in runs:
        rid = run.get("id")
        target = run.get("target")
        if rid not in expected:
            fail(f"run references unknown trace {rid!r}")
        if target not in {"host", "wsl:Debian"}:
            fail(f"{rid}: invalid run target {target!r}")
        outcome = run.get("outcome")
        if outcome not in ALLOWED:
            fail(f"{rid}@{target}: outcome {outcome!r} not in {sorted(ALLOWED)}")
        if outcome == "pass":
            if run.get("timed_out"):
                fail(f"{rid}@{target}: pass recorded while the run timed out")
            obs = run.get("observation")
            rec = run.get("recovery")
            if not (isinstance(obs, dict) and obs.get("ok") is True):
                fail(f"{rid}@{target}: pass without a true observation oracle")
            if not (isinstance(rec, dict) and rec.get("ok") is True):
                fail(f"{rid}@{target}: pass without a true recovery oracle")
            if not has_evidence(obs) or not has_evidence(rec):
                fail(f"{rid}@{target}: pass without present observation and recovery evidence")
            basis = run.get("success_basis", "")
            if "absence" in str(basis).lower():
                fail(f"{rid}@{target}: pass basis mentions absence rather than observation")
            if run.get("absence_as_success") is True:
                fail(f"{rid}@{target}: absence of notification recorded as success")
        executed.setdefault(rid, set()).add(target)

    not_run_ids = {n.get("id") for n in not_run}
    for item in not_run:
        if item.get("id") not in expected:
            fail(f"not_run references unknown trace {item.get('id')!r}")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            fail(f"{item.get('id')}: not_run entry without a reason")

    by_id = {t["id"]: t for t in traces}
    for trace in traces:
        tid = trace["id"]
        if trace["runs_now"]:
            for target in targets_for(trace):
                if target not in executed.get(tid, set()):
                    fail(f"{tid}: runs_now is true but no executed run for {target}")
        if trace["destructive"] and tid not in executed:
            if tid not in not_run_ids:
                fail(f"{tid}: destructive trace not executed and not listed as not_run with reason")

    for tid in executed:
        if by_id[tid]["target"] == "none":
            fail(f"{tid}: executed but marked target none in traces.json")

    passes = sum(1 for r in runs if r.get("outcome") == "pass")
    unknowns = sum(1 for r in runs if r.get("outcome") == "unknown")
    fails = sum(1 for r in runs if r.get("outcome") == "fail")
    wsl_runs = sum(1 for r in runs if r.get("target") == "wsl:Debian")
    host_runs = sum(1 for r in runs if r.get("target") == "host")
    print(
        "TRACES_PASS 20/20 fixtures normalized; "
        f"{len(executed)} traces executed ({host_runs} host, {wsl_runs} wsl runs; "
        f"{passes} pass, {fails} fail, {unknowns} unknown); "
        f"{len(not_run)} not_run entries with reasons; every pass has observation+recovery evidence"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
