#!/usr/bin/env python3
"""Regression probes for the material TERRA-M1A-02 dissent."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT))

from scripts.v3.planning.replay.kernel import (  # noqa: E402
    _sealed_state, admit, genesis, object_ref, replay,
)
from scripts.v3.planning.validation.canonical import M1AError, decode, digest, seal  # noqa: E402


def _load(fixture: str, case_id: str) -> dict:
    bundle = json.loads((FIXTURE_DIR / fixture).read_text(encoding="utf-8"))
    return next(case for case in bundle["cases"] if case["case_id"] == case_id)


def _run(case: dict, commands: list[dict]) -> tuple[dict, list[dict]]:
    state = genesis(case["genesis"])
    journal = []
    for command in commands:
        state, _, receipt, journal = admit(
            state, state["content_digest"], command,
            case["authority_fixtures"], case["policy_fixtures"], journal,
        )
        assert receipt["disposition"] == "accepted", command["command_id"]
    return state, journal


def _reseal_command(command: dict, state: dict) -> dict:
    command["expected_state_version"] = state["state_version"]
    command["expected_state_digest"] = state["content_digest"]
    command["payload_digest"] = digest(command["payload"])
    command["candidate_digest"] = command["payload_digest"]
    return seal(command)


def _authorized(case: dict, command: dict) -> list[dict]:
    authorities = copy.deepcopy(case["authority_fixtures"])
    for index, authority in enumerate(authorities):
        if authority["attestation_id"] == command["auth_ref"]:
            authority["candidate_digest"] = command["candidate_digest"]
            authorities[index] = seal(authority)
            return authorities
    raise AssertionError("command authority fixture missing")


def _plan_mutation(case: dict, state: dict, mutation: str) -> tuple[dict, list[dict]]:
    command = copy.deepcopy(case["commands"][3])
    task = command["payload"]["task_nodes"][0]
    plan = command["payload"]["plan_revision"]
    if mutation == "unknown-policy":
        task["payload"]["authority_policy_ref"] = {
            "policy_id": "POLICY-UNKNOWN", "policy_version": 1,
            "content_digest": "0" * 64,
        }
    elif mutation == "self-dependency":
        task["payload"]["dependency_node_ids"] = [task["id"]]
        plan["payload"]["dependency_edges"] = [{
            "from_node_id": task["id"], "to_node_id": task["id"],
        }]
    else:
        raise AssertionError(mutation)
    task = seal(task)
    command["payload"]["task_nodes"] = [task]
    plan["payload"]["task_node_refs"] = [object_ref(task)]
    plan["payload"]["graph_digest"] = digest({
        "task_node_refs": plan["payload"]["task_node_refs"],
        "dependency_edges": plan["payload"]["dependency_edges"],
    })
    plan = seal(plan)
    command["payload"]["plan_revision"] = plan
    transition = command["payload"]["plan_transition"]
    transition["payload"]["to_plan_ref"] = object_ref(plan)
    command["payload"]["plan_transition"] = seal(transition)
    command = _reseal_command(command, state)
    return command, _authorized(case, command)


def _assert_refused(case: dict, state: dict, journal: list[dict], command: dict,
                    authorities: list[dict], expected_error: str) -> None:
    frozen = copy.deepcopy(state)
    after, events, receipt, _ = admit(
        state, state["content_digest"], command, authorities,
        case["policy_fixtures"], journal,
    )
    assert after == frozen and not events
    assert receipt["disposition"] == "refused"
    assert receipt["primary_error"] == expected_error


def run_adversarial() -> int:
    probes = 0

    happy = _load("F-M1A-001.json", "happy")
    final_state, final_journal = _run(happy, happy["commands"])
    duplicate_state, events, duplicate, duplicate_journal = admit(
        final_state, final_state["content_digest"], happy["commands"][0],
        happy["authority_fixtures"], happy["policy_fixtures"], final_journal,
    )
    assert duplicate_state == final_state and not events
    assert duplicate == final_journal[0]
    assert duplicate_journal == [*final_journal, final_journal[0]]
    probes += 1

    replay_case = _load("F-M1A-018.json", "replay")
    checkpoint_replay = next(
        item for item in replay_case["replay_cases"]
        if item["replay_id"] == "REPLAY-CHECKPOINT-VALID"
    )
    tampered = copy.deepcopy(checkpoint_replay["checkpoint"])
    tampered["projection_snapshot"]["terminal_status"] = "terminal-failed"
    tampered["projection_snapshot"] = seal(tampered["projection_snapshot"])
    try:
        replay(
            replay_case["genesis"], checkpoint_replay["event_inputs"],
            checkpoint_replay["commands"], checkpoint_replay["receipts"], tampered,
        )
    except M1AError as error:
        assert error.code == "E-DIGEST-MISMATCH"
    else:
        raise AssertionError("tampered checkpoint projection was accepted")
    probes += 1

    genesis_replay = next(
        item for item in replay_case["replay_cases"]
        if item["replay_id"] == "REPLAY-GENESIS-VALID"
    )
    unknown_inputs = copy.deepcopy(genesis_replay["event_inputs"])
    event = json.loads(unknown_inputs[0])
    event["primary_record"]["object_type"] = "unknown-domain"
    event["primary_record"]["schema_version"] = "m1a-unknown-domain-1"
    event["primary_record"] = seal(event["primary_record"])
    event["state_delta_digest"] = digest({
        "event_type": event["event_type"],
        "primary_record": event["primary_record"],
        "related_records": event["related_records"],
    })
    unknown_inputs[0] = json.dumps(seal(event), separators=(",", ":"))
    try:
        replay(
            replay_case["genesis"], unknown_inputs, genesis_replay["commands"],
            genesis_replay["receipts"], None,
        )
    except M1AError as error:
        assert error.code == "E-SCHEMA-UNKNOWN-VERSION"
    else:
        raise AssertionError("unknown domain arm was accepted")
    probes += 1

    plan_state, plan_journal = _run(happy, happy["commands"][:3])
    command, authorities = _plan_mutation(happy, plan_state, "unknown-policy")
    _assert_refused(
        happy, plan_state, plan_journal, command, authorities, "E-POLICY-UNKNOWN"
    )
    probes += 1

    command, authorities = _plan_mutation(happy, plan_state, "self-dependency")
    _assert_refused(
        happy, plan_state, plan_journal, command, authorities, "E-DAG-DEPENDENCY"
    )
    probes += 1

    retry_case = _load("F-M1A-007.json", "novel")
    retry_state, retry_journal = _run(retry_case, retry_case["initial_commands"])
    paused_state = copy.deepcopy(retry_state)
    paused_state["current_pause_epoch"] = 1
    paused_state = _sealed_state(paused_state)
    pause_command = _reseal_command(copy.deepcopy(retry_case["commands"][0]), paused_state)
    _assert_refused(
        retry_case, paused_state, retry_journal, pause_command,
        _authorized(retry_case, pause_command), "E-PAUSED",
    )
    probes += 1

    expiry_command = copy.deepcopy(happy["commands"][3])
    executive = next(
        record for record in plan_state["records"]
        if record["object_type"] == "executive-lease"
    )
    expiry_command["logical_time"] = executive["payload"]["expires_logical_time"]
    expiry_command = _reseal_command(expiry_command, plan_state)
    _assert_refused(
        happy, plan_state, plan_journal, expiry_command,
        _authorized(happy, expiry_command), "E-STALE-LEASE",
    )
    probes += 1

    amend_case = _load("F-M1A-005.json", "amend")
    amend_state, amend_journal = _run(amend_case, amend_case["initial_commands"])
    amend_command = copy.deepcopy(amend_case["commands"][0])
    amendment = amend_command["payload"]["amendment"]
    amendment["payload"]["dispositions"] = []
    amend_command["payload"]["amendment"] = seal(amendment)
    amend_command = _reseal_command(amend_command, amend_state)
    _assert_refused(
        amend_case, amend_state, amend_journal, amend_command,
        _authorized(amend_case, amend_command), "E-AMENDMENT-INCOMPLETE",
    )
    probes += 1

    retry_command = copy.deepcopy(retry_case["commands"][0])
    retry = retry_command["payload"]
    retry["payload"]["next_attempt"] = 1
    retry_command["payload"] = seal(retry)
    retry_command = _reseal_command(retry_command, retry_state)
    _assert_refused(
        retry_case, retry_state, retry_journal, retry_command,
        _authorized(retry_case, retry_command), "E-RETRY-EXHAUSTED",
    )
    probes += 1

    invalid_id = copy.deepcopy(happy["commands"][0])
    invalid_id["payload"]["id"] = "x"
    invalid_id["payload"] = seal(invalid_id["payload"])
    invalid_id = _reseal_command(invalid_id, genesis(happy["genesis"]))
    raw_invalid_id = json.dumps(invalid_id, separators=(",", ":"))
    try:
        decode(raw_invalid_id)
    except M1AError as error:
        assert error.code == "E-SCHEMA-INVALID"
    else:
        raise AssertionError("invalid scalar ID decoded")
    initial = genesis(happy["genesis"])
    _assert_refused(
        happy, initial, [], invalid_id, _authorized(happy, invalid_id), "E-SCHEMA-INVALID"
    )
    probes += 1

    invalid_enum = copy.deepcopy(happy["commands"][0])
    invalid_enum["payload"]["payload"]["source_kind"] = "not-an-owner-source"
    invalid_enum["payload"] = seal(invalid_enum["payload"])
    invalid_enum = _reseal_command(invalid_enum, initial)
    try:
        decode(json.dumps(invalid_enum, separators=(",", ":")))
    except M1AError as error:
        assert error.code == "E-SCHEMA-INVALID"
    else:
        raise AssertionError("invalid scalar enum decoded")
    _assert_refused(
        happy, initial, [], invalid_enum, _authorized(happy, invalid_enum), "E-SCHEMA-INVALID"
    )
    probes += 1

    invalid_bound = copy.deepcopy(happy["commands"][0])
    invalid_bound["payload"]["created_logical_time"] = -1
    invalid_bound["payload"] = seal(invalid_bound["payload"])
    invalid_bound = _reseal_command(invalid_bound, initial)
    try:
        decode(json.dumps(invalid_bound, separators=(",", ":")))
    except M1AError as error:
        assert error.code == "E-SCHEMA-INVALID"
    else:
        raise AssertionError("out-of-bound scalar decoded")
    probes += 1

    invalid_order = copy.deepcopy(happy["commands"][1])
    allowed_actions = invalid_order["payload"]["payload"]["allowed_action_ids"]
    invalid_order["payload"]["payload"]["allowed_action_ids"] = list(reversed(allowed_actions))
    invalid_order["payload"] = seal(invalid_order["payload"])
    invalid_order = _reseal_command(invalid_order, initial)
    try:
        decode(json.dumps(invalid_order, separators=(",", ":")))
    except M1AError as error:
        assert error.code == "E-SCHEMA-INVALID"
    else:
        raise AssertionError("unsorted scalar collection decoded")
    probes += 1

    effect_case = _load("F-M1A-016.json", "ambiguous")
    invalid_conditional = copy.deepcopy(effect_case["commands"][0])
    invalid_conditional["payload"]["payload"]["quarantine"] = False
    invalid_conditional["payload"] = seal(invalid_conditional["payload"])
    effect_state, _ = _run(effect_case, effect_case["initial_commands"])
    invalid_conditional = _reseal_command(invalid_conditional, effect_state)
    try:
        decode(json.dumps(invalid_conditional, separators=(",", ":")))
    except M1AError as error:
        assert error.code == "E-SCHEMA-INVALID"
    else:
        raise AssertionError("invalid nullable conditional decoded")
    probes += 1

    conflict = copy.deepcopy(happy["commands"][0])
    conflict["payload"]["payload"]["intent_text"] = "A different valid owner intent."
    conflict["payload"] = seal(conflict["payload"])
    conflict["payload_digest"] = digest(conflict["payload"])
    conflict["candidate_digest"] = conflict["payload_digest"]
    conflict = seal(conflict)
    unchanged, conflict_events, conflict_receipt, _ = admit(
        final_state, final_state["content_digest"], conflict,
        _authorized(happy, conflict), happy["policy_fixtures"], final_journal,
    )
    assert unchanged == final_state and not conflict_events
    assert conflict_receipt["disposition"] == "conflict"
    assert conflict_receipt["primary_error"] == "E-IDEMPOTENCY-CONFLICT"
    probes += 1

    return probes


def main() -> int:
    probes = run_adversarial()
    print(f"M1A_ADVERSARIAL_PASS probes={probes}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"M1A_ADVERSARIAL_FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from error
