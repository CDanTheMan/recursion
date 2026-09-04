#!/usr/bin/env python3
"""Deterministic attenuation, graph, and purity properties for M1A."""

from __future__ import annotations

import copy
import itertools
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT))

from scripts.v3.planning.replay.kernel import admit, genesis, object_ref  # noqa: E402
from scripts.v3.planning.validation.canonical import digest, seal  # noqa: E402
from scripts.v3.planning.validation.contracts import validate_dag  # noqa: E402


def _load(fixture: str, case_id: str) -> dict:
    bundle = json.loads((FIXTURE_DIR / fixture).read_text(encoding="utf-8"))
    return next(case for case in bundle["cases"] if case["case_id"] == case_id)


def _state_before_plan(case: dict) -> dict:
    state = genesis(case["genesis"])
    for command in case["commands"][:3]:
        state, _, receipt = admit(
            state, state["content_digest"], command,
            case["authority_fixtures"], case["policy_fixtures"],
        )
        assert receipt["disposition"] == "accepted"
    return state


def _mutated_candidate(case: dict, state: dict, field: str, value) -> tuple[dict, list[dict]]:
    command = copy.deepcopy(case["commands"][3])
    task = command["payload"]["task_nodes"][0]
    target = task["payload"] if field not in {"plan_budget", "plan_path", "plan_effect"} else None
    if field == "plan_budget":
        command["payload"]["plan_revision"]["payload"]["budget_limits"]["tokens"] = value
    elif field == "plan_path":
        command["payload"]["plan_revision"]["payload"]["write_resource_paths"] = [value]
    elif field == "plan_effect":
        command["payload"]["plan_revision"]["payload"]["effect_keys"] = [value]
    elif field == "budget_limits":
        target[field]["tokens"] = value
    elif field in {"privacy_class_id", "egress_class_id"}:
        target[field] = value
    elif field in {"read_resource_paths", "write_resource_paths"}:
        target[field] = [value]
    else:
        target[field] = [value]
    command["payload"]["task_nodes"][0] = seal(task)
    plan = command["payload"]["plan_revision"]
    plan["payload"]["task_node_refs"] = [object_ref(command["payload"]["task_nodes"][0])]
    plan["payload"]["graph_digest"] = digest({
        "task_node_refs": plan["payload"]["task_node_refs"],
        "dependency_edges": plan["payload"]["dependency_edges"],
    })
    plan = seal(plan)
    command["payload"]["plan_revision"] = plan
    transition = command["payload"]["plan_transition"]
    transition["payload"]["to_plan_ref"] = object_ref(plan)
    command["payload"]["plan_transition"] = seal(transition)
    command["expected_state_version"] = state["state_version"]
    command["expected_state_digest"] = state["content_digest"]
    command["payload_digest"] = digest(command["payload"])
    command["candidate_digest"] = command["payload_digest"]
    command = seal(command)
    authorities = copy.deepcopy(case["authority_fixtures"])
    authority = next(item for item in authorities if item["attestation_id"] == command["auth_ref"])
    authority["candidate_digest"] = command["candidate_digest"]
    authorities[authorities.index(authority)] = seal(authority)
    return command, authorities


def main() -> int:
    base = _load("F-M1A-001.json", "happy")
    state = _state_before_plan(base)
    mutations = {
        "authority_ids": "AUTHORITY-WIDE", "capability_ids": "CAPABILITY-WIDE",
        "allowed_action_ids": "ACTION-WIDE", "route_ids": "ROUTE-WIDE",
        "account_class_ids": "ACCOUNT-WIDE", "capacity_pool_ids": "CAPACITY-WIDE",
        "effect_keys": "EFFECT-WIDE", "read_resource_paths": "outside/read",
        "write_resource_paths": "outside/write", "privacy_class_id": "PRIVACY-WIDE",
        "egress_class_id": "EGRESS-WIDE", "budget_limits": 1001,
        "plan_budget": 1001, "plan_path": "outside/plan", "plan_effect": "EFFECT-WIDE",
    }
    for field, value in mutations.items():
        command, authorities = _mutated_candidate(base, state, field, value)
        original_state = copy.deepcopy(state)
        after, events, receipt = admit(
            state, state["content_digest"], command, authorities, base["policy_fixtures"]
        )
        assert receipt["primary_error"] in {"E-BUDGET-WIDEN", "E-SCOPE-WIDEN"}, field
        assert after == original_state and not events

    graph_cases = _load("F-M1A-022.json", "ordered-disjoint")
    graph_bundle = json.loads((FIXTURE_DIR / "F-M1A-022.json").read_text(encoding="utf-8"))
    checked_graphs = 0
    for case in graph_bundle["cases"]:
        command = case["commands"][0]
        payload = command["payload"]
        plan = payload.get("new_plan_revision", payload.get("plan_revision"))
        expected = case["expected_receipts"][0]["primary_error"]
        for permutation in itertools.permutations(payload["task_nodes"]):
            error, witness = validate_dag(plan, list(permutation))
            assert error == expected
            assert witness == case["expected_receipts"][0]["witness"]
            checked_graphs += 1

    pure_case = _load("F-M1A-007.json", "novel")
    pure_state = genesis(pure_case["genesis"])
    for command in pure_case["initial_commands"]:
        pure_state, _, _ = admit(
            pure_state, pure_state["content_digest"], command,
            pure_case["authority_fixtures"], pure_case["policy_fixtures"],
        )
    command = pure_case["commands"][0]
    frozen_state, frozen_command = copy.deepcopy(pure_state), copy.deepcopy(command)
    first = admit(
        pure_state, pure_state["content_digest"], command,
        pure_case["authority_fixtures"], pure_case["policy_fixtures"],
    )
    second = admit(
        pure_state, pure_state["content_digest"], command,
        pure_case["authority_fixtures"], pure_case["policy_fixtures"],
    )
    assert first == second and pure_state == frozen_state and command == frozen_command
    print(
        f"M1A_PROPERTY_PASS attenuation={len(mutations)} graph_permutations={checked_graphs} "
        "pure_repeats=2"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as error:
        print(f"M1A_PROPERTY_FAIL: {error}", file=sys.stderr)
        raise SystemExit(1) from error
