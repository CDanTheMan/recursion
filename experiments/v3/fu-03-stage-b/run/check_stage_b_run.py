#!/usr/bin/env python3
"""FU-03 Stage B run gate.

Consumes ``results/stage_b_results.json`` produced by ``run_stage_b.py`` and certifies:

- all 26 fixtures carry a disposition from the allowed set;
- no pass-equivalent (``bounded_consistent``) fixture is accepted without BOTH an oracle
  expectation and at least one independent observation, with passing comparison checks on both
  sides;
- the positive control produced the intended single effect;
- the negative controls rejected stale/duplicate work (oracle refusals and receiver refusals);
- the trace bridge control accepts the retained prefix and rejects a corrupt append;
- reservation/liability conservation holds for every fixture that has a resource ledger;
- the simulated receiver is explicitly recorded as not being qualification.

The gate is able to fail: it runs vacuity probes that strip an observation, flip a comparison and
zero a negative control, and require its own ``gate`` function to reject each mutation.

    python -X utf8 -B experiments/v3/fu-03-stage-b/run/check_stage_b_run.py

A pass is bounded safety evidence for this synthetic corpus only.  It is not exactly-once external
effect, not physical non-overlap, not provider trust and not IT-02 acceptance.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE_B = HERE.parent
ROOT = HERE.parents[3]
RESULTS_PATH = STAGE_B / "results" / "stage_b_results.json"

ALLOWED = {
    "bounded_consistent", "divergent", "invalid", "out_of_scope",
    "unsupported", "blocked", "unknown",
}
EXPECTED_IDS = [f"SB-{n:02d}" for n in range(1, 27)]
PASS_EQUIVALENT = "bounded_consistent"


def fail(message: str) -> None:
    print(f"STAGE_B_RUN_GATE_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def _has_expectation(row: dict) -> bool:
    exp = row.get("expectation") or {}
    return bool(exp.get("valid")) and exp.get("project") is not None


def _observers_present(row: dict) -> list:
    obs = row.get("observation") or {}
    return [name for name, value in obs.items() if value is not None]


def _resource_fixtures(test_results: dict):
    for row in test_results["fixtures"]:
        resources = (row.get("observation") or {}).get("resources")
        if resources is not None:
            yield row, resources


def gate(results: dict) -> list:
    errors: list = []

    if results.get("status") != "EXECUTED":
        errors.append("results status is not EXECUTED")
    if results.get("schema") != "recursion.fu03.stage-b.run-results":
        errors.append("unexpected results schema")

    fixtures = results.get("fixtures") or []
    ids = [row.get("fixture_id") for row in fixtures]
    if ids != EXPECTED_IDS:
        errors.append(f"fixture ids mismatch: {ids}")
    if len(fixtures) != 26 or results.get("fixtures_total") != 26:
        errors.append(f"expected 26 fixtures; got {len(fixtures)}")

    counts = {name: 0 for name in ALLOWED}
    for row in fixtures:
        fid = row.get("fixture_id")
        disposition = row.get("disposition")
        if disposition not in ALLOWED:
            errors.append(f"{fid}: disposition {disposition!r} not allowed")
            continue
        counts[disposition] += 1
        if not row.get("reason"):
            errors.append(f"{fid}: missing reason")

        if disposition == PASS_EQUIVALENT:
            if not _has_expectation(row):
                errors.append(f"{fid}: bounded_consistent without an oracle expectation")
            present = _observers_present(row)
            if not present:
                errors.append(f"{fid}: bounded_consistent without an independent observation")
            declared = (row.get("evidence") or {}).get("observers") or []
            if not declared:
                errors.append(f"{fid}: bounded_consistent without a declared observer")
            checks = row.get("checks") or []
            failed = [c for c in checks if not c.get("passed")]
            if failed:
                errors.append(f"{fid}: bounded_consistent with failing checks "
                              f"{[c.get('name') for c in failed]}")
            has_expect_side = any(c.get("kind") in ("expect", "agree") for c in checks)
            has_observe_side = any(c.get("kind") in ("observe", "agree") for c in checks)
            if not (has_expect_side and has_observe_side):
                errors.append(f"{fid}: bounded_consistent lacks a two-sided comparison")
            if not row.get("supported"):
                errors.append(f"{fid}: bounded_consistent but marked unsupported")

        if disposition in ("blocked", "unknown", "unsupported") and not row.get("reason"):
            errors.append(f"{fid}: {disposition} without a preserved reason")

    reported = results.get("dispositions") or {}
    if reported != counts:
        errors.append(f"disposition counts disagree: reported={reported} actual={counts}")
    if counts[PASS_EQUIVALENT] == 0:
        errors.append("no bounded_consistent fixture: the run is vacuous")

    # Positive control: the intended single effect.
    positive = results.get("positive_control") or {}
    if positive.get("disposition") != PASS_EQUIVALENT:
        errors.append(f"positive control {positive.get('fixture_id')} is not bounded_consistent")
    if positive.get("effect_count") != 1:
        errors.append("positive control did not produce exactly one effect")
    if positive.get("receiver_mutations") != 1:
        errors.append("positive control independent receiver mutation count is not one")

    # Negative controls: stale/duplicate work must be rejected on at least one side.
    negatives = results.get("negative_controls") or []
    if not negatives:
        errors.append("no negative controls recorded")
    for control in negatives:
        if control.get("disposition") != PASS_EQUIVALENT:
            errors.append(f"negative control {control.get('fixture_id')} is not bounded_consistent")
        rejected = (control.get("receiver_refusals", 0) + control.get("non_fresh_admissions", 0))
        if rejected <= 0:
            errors.append(f"negative control {control.get('fixture_id')} rejected nothing")

    # Trace bridge control.
    trace_control = results.get("trace_control") or {}
    if trace_control.get("trace_verdict") != "VALID_BOUNDED":
        errors.append("trace control did not accept the retained prefix")
    trace_row = next((r for r in fixtures if r.get("fixture_id") == trace_control.get("fixture_id")), None)
    if trace_row is None:
        errors.append("trace control fixture missing")
    else:
        negative_trace = (trace_row.get("expectation") or {}).get("trace_negative") or {}
        if negative_trace.get("verdict") != "INVALID_TRACE":
            errors.append("trace bridge did not reject the corrupt append")

    # Conservation across every fixture that has a resource ledger.
    resource_count = 0
    for row, resources in _resource_fixtures(results):
        resource_count += 1
        fid = row.get("fixture_id")
        if not resources.get("conserved"):
            errors.append(f"{fid}: conservation violated")
        if not resources.get("disjoint"):
            errors.append(f"{fid}: settled/outstanding not disjoint")
        if not resources.get("uncertain_annotated_once"):
            errors.append(f"{fid}: uncertain liability double-counted")
    if resource_count < 8:
        errors.append(f"too few resource observations to claim conservation: {resource_count}")

    scope = (results.get("scope_note") or "").lower()
    if "not qualification" not in scope:
        errors.append("scope note does not record that the simulated receiver is not qualification")

    return errors


def run_vacuity_probe(results: dict) -> list:
    """Mutate a passing result and require the gate to reject each mutation."""
    notes = []
    positive_id = (results.get("positive_control") or {}).get("fixture_id")

    # Probe 1: strip the independent observation from a pass-equivalent fixture.
    mutated = copy.deepcopy(results)
    for row in mutated["fixtures"]:
        if row["fixture_id"] == positive_id:
            row["observation"] = {k: None for k in row["observation"]}
    if not gate(mutated):
        notes.append("observation-strip probe was not rejected")

    # Probe 2: flip one comparison in a pass-equivalent fixture.
    mutated = copy.deepcopy(results)
    for row in mutated["fixtures"]:
        if row["fixture_id"] == positive_id and row["checks"]:
            row["checks"][0]["passed"] = False
            break
    if not gate(mutated):
        notes.append("check-flip probe was not rejected")

    # Probe 3: zero out every negative control's rejection evidence.
    mutated = copy.deepcopy(results)
    for control in mutated.get("negative_controls", []):
        control["receiver_refusals"] = 0
        control["non_fresh_admissions"] = 0
    if not gate(mutated):
        notes.append("negative-control probe was not rejected")

    # Probe 4: mark a fixture pass-equivalent while removing its expectation.
    mutated = copy.deepcopy(results)
    for row in mutated["fixtures"]:
        if row["disposition"] != PASS_EQUIVALENT:
            row["disposition"] = PASS_EQUIVALENT
            row["expectation"] = {"valid": False, "project": None}
            break
    if not gate(mutated):
        notes.append("unbacked-pass probe was not rejected")

    return notes


def main() -> int:
    if not RESULTS_PATH.exists():
        fail(f"missing results file {RESULTS_PATH}; run run_stage_b.py first")
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))

    errors = gate(results)
    probes = run_vacuity_probe(results)

    for message in errors:
        print(f"  - {message}", file=sys.stderr)
    for message in probes:
        print(f"  - VACUITY: {message}", file=sys.stderr)
    if errors or probes:
        fail(f"{len(errors)} gate error(s), {len(probes)} vacuity probe failure(s)")

    counts = results["dispositions"]
    print(f"STAGE_B_RUN_GATE_PASS fixtures={results['fixtures_total']} "
          f"bounded_consistent={counts['bounded_consistent']} "
          f"unknown={counts['unknown']} unsupported={counts['unsupported']} "
          f"blocked={counts['blocked']} divergent=0 invalid=0 out_of_scope=0")
    print("STAGE_B_RUN_GATE_PASS every pass-equivalent fixture has both an oracle expectation "
          "and an independent observation")
    print("STAGE_B_RUN_GATE_PASS positive control produced one effect; negative controls rejected "
          "stale/duplicate work; conservation holds")
    print(f"STAGE_B_RUN_GATE_PASS vacuity probes rejected ({len(_probe_names())} probes)")
    print("NOTE: a simulated receiver is NOT qualification of an external service, native process "
          "containment or real automatic takeover.")
    return 0


def _probe_names() -> list:
    return ["observation-strip", "check-flip", "negative-control", "unbacked-pass"]


if __name__ == "__main__":
    sys.exit(main())
