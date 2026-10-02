#!/usr/bin/env python3
"""Gate for the FU-03 independent reference oracle.

Runs the normative vector corpus and the bounded trace checker, asserts every expected result,
and asserts that ``RefState`` is deterministic across two invocations and that ``RefProject``
binds aggregate, ordinal and tail.  Fails loudly (non-zero exit, ``ORACLE_FAIL`` on stderr).

    python -X utf8 -B experiments/v3/fu-03-kernel-session-a/oracle/check_oracle.py

A pass means the vectors and the finite trace controls agree with this reference implementation.
It is not acceptance, not a refinement proof, not the integrated-bound TLC gate and not a kernel
freeze.  See README.md.
"""
from __future__ import annotations

import copy
import json
import sys
from dataclasses import replace
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import refstate as R
import trace_checker as TC

VECTORS_PATH = HERE / "vectors" / "vectors.json"


def fail(message: str) -> None:
    print(f"ORACLE_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# Typed value decoding (language-neutral vector encoding)
# ---------------------------------------------------------------------------
def decode_typed(node: dict):
    kind = node.get("t")
    if kind == "uint":
        return int(node["v"])
    if kind == "nint":
        return int(node["v"])
    if kind == "bytes":
        return bytes.fromhex(node["v"])
    if kind == "text":
        return node["v"]
    if kind == "bool":
        return bool(node["v"])
    if kind == "null":
        return None
    if kind == "array":
        return [decode_typed(v) for v in node["v"]]
    if kind == "map":
        result = {}
        for key_node, value_node in node["v"]:
            key = decode_typed(key_node)
            if key in result:
                fail(f"typed map input has duplicate key {key}")
            result[key] = decode_typed(value_node)
        return result
    fail(f"unknown typed encoding {kind!r}")


# ---------------------------------------------------------------------------
# Scenario builders
# ---------------------------------------------------------------------------
def build_descriptor(state, spec, built):
    if "reuse" in spec:
        return built[int(spec["reuse"])]
    return R.command_from_spec(state, spec)


def run_admission(vector):
    state = R.genesis_state()
    built = []
    for step_index, (spec, expected) in enumerate(zip(vector["commands"], vector["expect"])):
        command = build_descriptor(state, spec, built)
        built.append(command)
        admission = R.admit(state, command)
        if admission.outcome != expected["result"]:
            fail(f"vector {vector['id']} step {step_index}: outcome "
                 f"{admission.outcome!r} != {expected['result']!r}")
        if expected["result"] == "refused":
            refusal = admission.refusal
            if refusal is None or refusal.code != expected["code"] or \
                    refusal.detail != expected["detail"]:
                observed = None if refusal is None else [refusal.code, refusal.detail]
                fail(f"vector {vector['id']} step {step_index}: refusal {observed} != "
                     f"[{expected['code']}, {expected['detail']}]")
            if "path" in expected and refusal.path != expected["path"]:
                fail(f"vector {vector['id']} step {step_index}: path {refusal.path} != "
                     f"{expected['path']}")
        if admission.outcome == "fresh":
            state = admission.batch.post_state


def build_log(vector):
    state = R.genesis_state()
    built = []
    log = []
    for step_index, spec in enumerate(vector["commands"]):
        command = build_descriptor(state, spec, built)
        built.append(command)
        admission = R.admit(state, command)
        if admission.outcome != "fresh":
            fail(f"vector {vector['id']} step {step_index}: log command not fresh "
                 f"({admission.outcome})")
        state = admission.batch.post_state
        log.extend(admission.batch.events)
    return state, log, built


def apply_tamper(log, tamper):
    op = tamper["op"]
    index = int(tamper["index"])
    if op == "flip_digest":
        digest = bytearray(log[index].digest)
        bit = int(tamper.get("bit", 0))
        digest[bit // 8] ^= 1 << (bit % 8)
        log[index] = replace(log[index], digest=bytes(digest))
    elif op == "wrong_predecessor":
        log[index] = replace(log[index], previous=b"\x00" * 31 + b"\x01")
    elif op == "ordinal_gap":
        log[index] = replace(log[index], ordinal=log[index].ordinal + int(tamper.get("delta", 1)))
    elif op == "remove":
        del log[index]
    elif op == "duplicate":
        log.insert(index, log[index])
    elif op == "set_schema":
        log[index] = replace(log[index], schema_epoch=int(tamper["value"]))
    else:
        fail(f"unknown tamper op {op!r}")
    return log


def run_log_reduction(vector):
    live_state, log, _built = build_log(vector)
    tamper = vector.get("tamper")
    if tamper:
        log = apply_tamper(log, tamper)

    result = R.validate_log(log)
    expected = vector["expect"]
    if result.valid != expected["valid"]:
        fail(f"vector {vector['id']}: valid={result.valid} != expected={expected['valid']} "
             f"({result.to_dict()})")
    if not expected["valid"]:
        if result.code != expected["code"] or result.detail != expected["detail"] or \
                result.first_index != expected["first_index"]:
            fail(f"vector {vector['id']}: refusal {result.to_dict()} != {expected}")
        return

    state_a = R.RefState(log)
    state_b = R.RefState(log)
    if R.state_digest(state_a) != R.state_digest(state_b):
        fail(f"vector {vector['id']}: RefState not deterministic across two invocations")
    if R.state_digest(state_a) != R.state_digest(live_state):
        fail(f"vector {vector['id']}: folded state differs from live admission state")

    projection = R.RefProject(log)
    if projection[0] != R.AGGREGATE:
        fail(f"vector {vector['id']}: projection aggregate {projection[0]} != 1")
    if projection[1] != len(log):
        fail(f"vector {vector['id']}: projection ordinal {projection[1]} != len(log) {len(log)}")
    if projection[2] != log[-1].digest:
        fail(f"vector {vector['id']}: projection tail does not bind the last event digest")

    if "ordinal" in expected and projection[1] != expected["ordinal"]:
        fail(f"vector {vector['id']}: ordinal {projection[1]} != {expected['ordinal']}")
    if "events" in expected and len(log) != expected["events"]:
        fail(f"vector {vector['id']}: events {len(log)} != {expected['events']}")
    if "status" in expected and state_a.status != expected["status"]:
        fail(f"vector {vector['id']}: status {state_a.status} != {expected['status']}")
    if "attempt" in expected and state_a.attempt != expected["attempt"]:
        fail(f"vector {vector['id']}: attempt {state_a.attempt} != {expected['attempt']}")
    if "effect_status" in expected:
        observed = state_a.effect.status if state_a.effect is not None else R.ES_NONE
        if observed != expected["effect_status"]:
            fail(f"vector {vector['id']}: effect status {observed} != {expected['effect_status']}")
    if "outbox" in expected and len(state_a.outbox) != expected["outbox"]:
        fail(f"vector {vector['id']}: outbox {len(state_a.outbox)} != {expected['outbox']}")


def run_canonical_bytes(vector):
    value = decode_typed(vector["input"])
    encoded = R.cbor_encode(value)
    if encoded.hex() != vector["expect"]["hex"]:
        fail(f"vector {vector['id']}: {encoded.hex()} != {vector['expect']['hex']}")


def run_canonical_decode(vector):
    data = bytes.fromhex(vector["input_hex"])
    if "expect_error" in vector:
        expected = vector["expect_error"]
        try:
            R.cbor_decode(data)
        except R.Refusal as refusal:
            if refusal.code != expected["code"] or refusal.detail != expected["detail"]:
                fail(f"vector {vector['id']}: refusal [{refusal.code},{refusal.detail}] != "
                     f"[{expected['code']},{expected['detail']}]")
            return
        fail(f"vector {vector['id']}: expected refusal but decode succeeded")
    if vector.get("expect_roundtrip"):
        value = R.cbor_decode(data)
        if R.cbor_encode(value) != data:
            fail(f"vector {vector['id']}: roundtrip changed canonical bytes")


def run_trace(vector):
    report = TC.check_trace(vector["trace"])
    expected = vector["expect"]
    if report.verdict != expected["verdict"]:
        fail(f"vector {vector['id']}: verdict {report.verdict} != {expected['verdict']} "
             f"({report.reason})")
    if report.first_divergence_index != expected["first_divergence_index"]:
        fail(f"vector {vector['id']}: first divergence {report.first_divergence_index} != "
             f"{expected['first_divergence_index']}")
    if "steps_checked" in expected and report.steps_checked != expected["steps_checked"]:
        fail(f"vector {vector['id']}: steps_checked {report.steps_checked} != "
             f"{expected['steps_checked']}")


def run_digest_domains(vector):
    value = decode_typed(vector["input"])
    digests = {domain: R.D(domain, 1, value) for domain in R.DOMAINS}
    if len(set(digests.values())) != len(R.DOMAINS):
        fail(f"vector {vector['id']}: distinct domains collide for one value")
    if R.D("state", 1, value) == R.D("state", 2, value):
        fail(f"vector {vector['id']}: schema epochs collide under one domain")


RUNNERS = {
    "canonical_bytes": run_canonical_bytes,
    "canonical_decode": run_canonical_decode,
    "admission": run_admission,
    "log_reduction": run_log_reduction,
    "trace": run_trace,
    "digest_domains": run_digest_domains,
}


# ---------------------------------------------------------------------------
# Additional trace-bridge negative control with observed state digests
# ---------------------------------------------------------------------------
def build_observed_trace():
    state = R.genesis_state()
    steps = []
    for spec in ({"kind": 7}, {"kind": 8, "payload": {"0": 1, "1": 0}},
                 {"kind": 9, "payload": {"0": 1}}):
        command = R.command_from_spec(state, spec)
        admission = R.admit(state, command)
        if admission.outcome != "fresh":
            fail("internal: observed-trace fixture command not fresh")
        state = admission.batch.post_state
        steps.append({"events": [e.to_map() for e in admission.batch.events],
                      "observed_state_digest": R.state_digest_hex(state),
                      "observed_projection": R.projection_json(state)})
    return {"trace_id": "observed-digest", "steps": steps}


def check_trace_bridge_controls():
    trace = build_observed_trace()
    report = TC.check_trace(trace)
    if report.verdict != "VALID_BOUNDED":
        fail(f"observed-digest trace not VALID_BOUNDED ({report.reason})")

    corrupt = copy.deepcopy(trace)
    corrupt["steps"][1]["observed_state_digest"] = "00" * 32
    report = TC.check_trace(corrupt)
    if report.verdict != "INVALID_TRACE" or report.first_divergence_index != 1:
        fail(f"corrupted observed digest not detected at index 1 (got {report.verdict}@"
             f"{report.first_divergence_index})")

    corrupt2 = copy.deepcopy(trace)
    corrupt2["steps"][2]["observed_projection"] = [0, 0, "00", 0, 0, 0, 0, 0, 0, False, 0,
                                                   False, None, None, 0, 0]
    report = TC.check_trace(corrupt2)
    if report.verdict != "INVALID_TRACE" or report.first_divergence_index != 2:
        fail(f"corrupted observed projection not detected at index 2 (got {report.verdict}@"
             f"{report.first_divergence_index})")


def main() -> int:
    payload = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_epoch") != R.SCHEMA_EPOCH:
        fail("vector corpus schema epoch mismatch")
    vectors = payload["vectors"]
    if not vectors:
        fail("empty vector corpus")

    counts: dict[str, int] = {}
    for vector in vectors:
        category = vector["category"]
        runner = RUNNERS.get(category)
        if runner is None:
            fail(f"vector {vector['id']}: unknown category {category!r}")
        runner(vector)
        counts[category] = counts.get(category, 0) + 1

    check_trace_bridge_controls()

    print(f"ORACLE_PASS {len(vectors)} vectors; "
          + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print("ORACLE_PASS RefState deterministic across two invocations on every valid reduction")
    print("ORACLE_PASS RefProject binds aggregate=1, ordinal=len(log), tail=last event digest")
    print("ORACLE_PASS trace bridge rejects corrupted observed digest/projection at first index")
    print("NOTE: bounded OBSERVED-consistency check, not a machine-checked refinement (see README).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
