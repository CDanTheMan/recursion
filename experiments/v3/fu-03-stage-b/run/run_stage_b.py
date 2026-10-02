#!/usr/bin/env python3
"""FU-03 Stage B runner: execute the crash-cut matrix provider-free.

For each of the 26 fixtures this runner:

1. builds the finite run from :mod:`harness` (canonical committed log + independent observation),
2. calls ``refstate.RefValid`` / ``RefState`` / ``RefProject`` and ``trace_checker.check_trace``
   as the **expectation** side over the supplied committed log,
3. compares the expectation against the harness **observation** side at the declared cut, and
4. classifies the fixture as one of ``bounded_consistent``, ``divergent``, ``invalid``,
   ``out_of_scope``, ``unsupported``, ``blocked`` or ``unknown``.

Per-fixture evidence (log digest, expectation, observation, checks, disposition, reason) is
written to ``results/stage_b_results.json`` and raw logs to ``results/logs/``.

The comparison direction is fixed: the oracle produces expectations from the committed log; the
independent observers produce observations.  The candidate is never used to generate the expected
reference state.  This is bounded safety evidence for one synthetic corpus, not exactly-once
external effect, physical non-overlap or provider trust.

    python -X utf8 -B experiments/v3/fu-03-stage-b/run/run_stage_b.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE_B = HERE.parent
ROOT = HERE.parents[3]
RESULTS = STAGE_B / "results"
LOGS = RESULTS / "logs"

ORACLE_DIR = HERE.parents[1] / "fu-03-kernel-session-a" / "oracle"
if str(ORACLE_DIR) not in sys.path:
    sys.path.insert(0, str(ORACLE_DIR))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import refstate as R  # noqa: E402
import trace_checker as TC  # noqa: E402

import harness as H  # noqa: E402

ALLOWED_DISPOSITIONS = {
    "bounded_consistent", "divergent", "invalid", "out_of_scope",
    "unsupported", "blocked", "unknown",
}


def detect_candidate_commit() -> str:
    """Read the candidate commit without invoking git."""
    git = ROOT / ".git"
    try:
        head = (git / "HEAD").read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"
    if not head.startswith("ref:"):
        return head[:12]
    ref = head.split(" ", 1)[1].strip()
    ref_path = git / ref
    if ref_path.exists():
        return ref_path.read_text(encoding="utf-8").strip()[:12]
    packed = git / "packed-refs"
    if packed.exists():
        for line in packed.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("^"):
                continue
            parts = line.split(" ", 1)
            if len(parts) == 2 and parts[1] == ref:
                return parts[0][:12]
    return "unknown"


def json_object(value):
    return H.jsonable(value)


def compute_expectation(scenario: H.Scenario) -> dict:
    log = scenario.run.log if scenario.run is not None else []
    result = R.validate_log(log)
    expectation = {
        "valid": result.valid,
        "valid_status": result.status,
        "first_index": result.first_index,
        "log_len": len(log),
        "admissions": list(scenario.run.admissions) if scenario.run is not None else [],
        "project": None,
        "digest": None,
        "replay_project": None,
        "replay_digest": None,
        "state_status": None,
        "attempt": None,
        "effect_status": H.ES_NONE,
        "effect_count": 0,
        "effect_unresolved": False,
        "receipt_count": 0,
        "outbox_len": 0,
        "trace": None,
        "trace_negative": None,
    }
    if result.valid:
        state = R.RefState(log)
        project = R.RefProject(log)
        expectation.update({
            "project": project,
            "digest": R.state_digest_hex(state),
            "state_status": state.status,
            "attempt": state.attempt,
            "effect_status": project[14],
            "effect_count": 0 if state.effect is None or project[14] == H.ES_NONE else 1,
            "effect_unresolved": project[14] in (H.ES_INFLIGHT, H.ES_UNKNOWN),
            "receipt_count": len(state.receipts),
            "outbox_len": len(state.outbox),
        })
        if scenario.run is not None:
            replay = scenario.run.replayed()
            rproject = R.RefProject(replay.log)
            expectation["replay_project"] = rproject
            expectation["replay_digest"] = R.state_digest_hex(replay.state)
    if scenario.trace is not None:
        expectation["trace"] = TC.check_trace(scenario.trace).to_dict()
    if scenario.trace_negative is not None:
        expectation["trace_negative"] = TC.check_trace(scenario.trace_negative).to_dict()
    return expectation


def evaluate_checks(scenario: H.Scenario, expectation: dict, observation: dict) -> list:
    evaluated = []
    for check in scenario.checks:
        try:
            passed = bool(check.fn(expectation, observation))
            error = ""
        except Exception as exc:  # noqa: BLE001 - a malformed comparison is a failed check
            passed = False
            error = f"{type(exc).__name__}: {exc}"
        evaluated.append({
            "name": check.name,
            "kind": check.kind,
            "detail": check.detail,
            "passed": passed,
            "error": error,
        })
    return evaluated


def classify(scenario: H.Scenario, expectation: dict, checks: list) -> tuple:
    if not scenario.supported:
        return scenario.fallback_disposition, scenario.reason
    if expectation["valid_status"] == "OUT_OF_SCOPE":
        return "out_of_scope", "materialized prefix exceeds MaxCommittedEvents=20"
    if not expectation["valid"]:
        return "invalid", (
            f"oracle rejects the materialized prefix: {expectation['valid_status']} "
            f"at index {expectation['first_index']}"
        )
    failed = [c for c in checks if not c["passed"]]
    if not scenario.has_expectation() or not scenario.has_observation():
        return "blocked", "missing an expectation or an independent observation at the cut"
    if failed:
        expectation_side = [c for c in failed if c["kind"] in ("expect", "agree")]
        observation_side = [c for c in failed if c["kind"] == "observe"]
        names = ", ".join(f"{c['name']}({c['kind']})" for c in failed)
        side = []
        if expectation_side:
            side.append("expectation")
        if observation_side:
            side.append("observation")
        return "divergent", f"{'/'.join(side)}-side check(s) failed: {names}"
    return "bounded_consistent", scenario.reason or "expectation and independent observation agree at the cut"


def expectation_json(expectation: dict) -> dict:
    def enc(value):
        if isinstance(value, (bytes, bytearray)):
            return value.hex()
        if isinstance(value, (list, tuple)):
            return [enc(v) for v in value]
        if isinstance(value, dict):
            return {str(k): enc(v) for k, v in value.items()}
        return value

    return {
        "valid": expectation["valid"],
        "valid_status": expectation["valid_status"],
        "first_index": expectation["first_index"],
        "log_len": expectation["log_len"],
        "digest": expectation["digest"],
        "project": enc(expectation["project"]),
        "replay_project": enc(expectation["replay_project"]),
        "replay_digest": expectation["replay_digest"],
        "receipt_count": expectation["receipt_count"],
        "outbox_len": expectation["outbox_len"],
        "effect_status": expectation["effect_status"],
        "effect_count": expectation["effect_count"],
        "effect_unresolved": expectation["effect_unresolved"],
        "attempt": expectation["attempt"],
        "admissions": expectation["admissions"],
        "trace": expectation["trace"],
        "trace_negative": expectation["trace_negative"],
    }


def write_raw_log(scenario: H.Scenario, expectation: dict) -> str:
    LOGS.mkdir(parents=True, exist_ok=True)
    payload = {
        "fixture_id": scenario.fixture_id,
        "cut_point": scenario.cut_point,
        "receiver_fence_state": scenario.fence_state,
        "stop_mode": scenario.stop_mode,
        "event_log": scenario.run.event_maps() if scenario.run is not None else [],
        "admissions": expectation["admissions"],
        "trace": json_object(scenario.trace),
        "trace_negative": json_object(scenario.trace_negative),
        "observation": json_object(scenario.observation()),
    }
    path = LOGS / f"{scenario.fixture_id}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return str(path.relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    scenarios = H.build_scenarios()
    if list(scenarios) != H.FIXTURE_ORDER:
        print("STAGE_B_RUN_FAIL: scenario order does not match the fixture matrix", file=sys.stderr)
        return 1

    fixtures = []
    counts = {name: 0 for name in sorted(ALLOWED_DISPOSITIONS)}
    for fixture_id in H.FIXTURE_ORDER:
        scenario = scenarios[fixture_id]
        expectation = compute_expectation(scenario)
        observation = scenario.observation()
        checks = evaluate_checks(scenario, expectation, observation)
        disposition, reason = classify(scenario, expectation, checks)
        if disposition not in ALLOWED_DISPOSITIONS:
            print(f"STAGE_B_RUN_FAIL: {fixture_id} produced unknown disposition {disposition!r}",
                  file=sys.stderr)
            return 1
        counts[disposition] += 1
        log_path = write_raw_log(scenario, expectation)
        log_digest = (scenario.run.log_digest() if scenario.run is not None
                      else hashlib.sha256(b"[]").hexdigest())
        fixtures.append({
            "fixture_id": fixture_id,
            "cut_point": scenario.cut_point,
            "receiver_fence_state": scenario.fence_state,
            "stop_mode": scenario.stop_mode,
            "disposition": disposition,
            "reason": reason,
            "supported": scenario.supported,
            "expectation": expectation_json(expectation),
            "observation": json_object(observation),
            "checks": checks,
            "evidence": {
                "log_digest": log_digest,
                "log_len": len(scenario.run.log) if scenario.run is not None else 0,
                "raw_log": log_path,
                "observers": scenario.observer_names(),
                "expectation_note": scenario.expectation_note,
                "observation_note": scenario.observation_note,
            },
        })

    # Controls: a positive control that yields the intended single effect, plus negative controls
    # that reject stale/duplicate work and a trace control that rejects a corrupt append.
    by_id = {row["fixture_id"]: row for row in fixtures}
    positive = {
        "fixture_id": H.POSITIVE_CONTROL,
        "disposition": by_id[H.POSITIVE_CONTROL]["disposition"],
        "effect_count": by_id[H.POSITIVE_CONTROL]["expectation"]["effect_count"],
        "receiver_mutations": by_id[H.POSITIVE_CONTROL]["observation"]["receiver"]["accepted_total"],
    }
    negatives = []
    for fixture_id in H.NEGATIVE_CONTROLS:
        row = by_id[fixture_id]
        receiver = row["observation"]["receiver"] or {}
        refused = (receiver.get("refused_stale_count", 0)
                   + receiver.get("refused_unqualified_count", 0))
        admissions = row["expectation"]["admissions"]
        refused_admissions = sum(1 for a in admissions if a["outcome"] in ("refused", "cached"))
        negatives.append({
            "fixture_id": fixture_id,
            "disposition": row["disposition"],
            "receiver_refusals": refused,
            "non_fresh_admissions": refused_admissions,
        })
    trace_control = {
        "fixture_id": "SB-03",
        "trace_verdict": by_id["SB-03"]["expectation"]["trace"]["verdict"]
        if by_id["SB-03"]["expectation"]["trace"] else None,
    }

    results = {
        "schema": "recursion.fu03.stage-b.run-results",
        "schema_version": 1,
        "status": "EXECUTED",
        "generated": "2026-10-02",
        "candidate_commit": detect_candidate_commit(),
        "goal": "stale or ambiguous work never becomes a new authorized effect through retry, crash or takeover",
        "scope_note": "provider-free synthetic run; a simulated receiver is not qualification of an "
                      "external service, native process containment or real automatic takeover",
        "dispositions": counts,
        "fixtures_total": len(fixtures),
        "positive_control": positive,
        "negative_controls": negatives,
        "trace_control": trace_control,
        "fixtures": fixtures,
    }
    out = RESULTS / "stage_b_results.json"
    out.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")

    print(f"STAGE_B_RUN fixtures={len(fixtures)} total={sum(counts.values())}")
    for name in sorted(counts):
        print(f"  {name}={counts[name]}")
    print(f"STAGE_B_RUN positive_control={H.POSITIVE_CONTROL} "
          f"disposition={positive['disposition']} effects={positive['effect_count']} "
          f"receiver_mutations={positive['receiver_mutations']}")
    for neg in negatives:
        print(f"STAGE_B_RUN negative_control={neg['fixture_id']} "
              f"disposition={neg['disposition']} receiver_refusals={neg['receiver_refusals']} "
              f"non_fresh_admissions={neg['non_fresh_admissions']}")
    print(f"STAGE_B_RUN trace_control=SB-03 verdict={trace_control['trace_verdict']}")
    print(f"STAGE_B_RUN wrote {out.relative_to(ROOT)}")
    print("NOTE: bounded synthetic evidence over one corpus; not exactly-once external effect, "
          "not provider trust, not IT-02 acceptance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
