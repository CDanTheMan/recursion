import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from mvp_contracts import (ContractError, MAX_DEPTH, canonical_digest,
                           canonical_json, validate, validate_checkpoint_chain,
                           validate_cross_records)

T = "2026-08-31T12:00:00Z"
D = "0" * 64
C = "a" * 40


def signed(record):
    field = {"capability_grant": "grant_digest"}.get(
        record["kind"], record["kind"] + "_digest")
    record[field] = canonical_digest(record)
    return record


def records():
    task = {
        "schema_version": 2, "kind": "task", "id": "task-one",
        "project_id": "project-one", "source_repository": "org/repo",
        "source_branch": "main", "source_sha": C, "parent_goal": "goal-one",
        "parent_task_id": None, "parent_task_digest": None, "depth": 0,
        "allowed_paths": ["src"], "non_goals": ["deploy"],
        "acceptance": "all gates pass", "requested_capabilities": ["workspace-edit"],
        "budget_id": "budget-one", "verification_policy": "independent",
        "gate_digest": D, "created_at": T, "expires_at": None,
        "task_digest": "",
    }
    task = signed(task)
    budget = signed({
        "schema_version": 2, "kind": "budget", "id": "budget-one",
        "task_id": task["id"], "task_digest": task["task_digest"],
        "parent_budget_id": None, "token_limit": 100, "wall_seconds": 60,
        "concurrency_limit": 1, "cost_limit_cents": 0,
        "metered_spend_allowed": False, "approval_digest": None,
        "calendar_month_ceiling_cents": 0, "remaining_tokens": 100,
        "remaining_wall_seconds": 60, "remaining_cost_cents": 0, "budget_digest": "",
    })
    grant = signed({
        "schema_version": 2, "kind": "capability_grant", "id": "grant-one",
        "task_id": task["id"], "task_digest": task["task_digest"],
        "capabilities": ["workspace-edit"], "allowed_paths": ["src"],
        "network_policy": "none", "endpoints": ["none"], "issued_at": T,
        "expires_at": "2030-01-01T00:00:00Z", "grant_digest": "",
    })
    checkpoint = signed({
        "schema_version": 2, "kind": "checkpoint", "id": "checkpoint-one",
        "task_id": task["id"], "task_digest": task["task_digest"],
        "packet_digest": D, "context_digest": D, "state_digest": D,
        "sequence": 0, "prev_digest": None, "created_at": T,
        "checkpoint_digest": "",
    })
    assignment = signed({"kind": "assignment", "id": "assignment-one",
                         "task_id": task["id"], "task_digest": task["task_digest"]})
    candidate = signed({"kind": "candidate", "id": "candidate-one",
                        "task_digest": task["task_digest"],
                        "candidate_id": "candidate-one", "candidate_commit": C,
                        "result_digest": D})
    evidence = signed({"kind": "evidence", "id": "evidence-one",
                       "task_digest": task["task_digest"]})
    receipt = signed({
        "schema_version": 2, "kind": "receipt", "id": "receipt-one",
        "task_id": task["id"], "task_digest": task["task_digest"],
        "assignment_digest": assignment["assignment_digest"], "adapter": "local", "candidate_id": "candidate-one",
        "candidate_commit": C, "result_digest": D, "status": "succeeded",
        "usage": {"tokens": 1, "input_tokens": 1, "output_tokens": 0,
                  "wall_seconds": 1, "cost_cents": 0},
        "checkpoint_digests": [checkpoint["checkpoint_digest"]],
        "started_at": T, "finished_at": T, "receipt_digest": "",
    })
    verifier = signed(copy.deepcopy(task))
    verifier.update(id="task-verifier", parent_task_id=None,
                    parent_task_digest=None, task_digest="")
    verifier = signed(verifier)
    verification = signed({
        "schema_version": 2, "kind": "verification", "id": "verification-one",
        "task_id": task["id"], "task_digest": task["task_digest"],
        "receipt_digest": receipt["receipt_digest"], "candidate_id": "candidate-one",
        "candidate_commit": C, "candidate_digest": candidate["candidate_digest"], "result_digest": D,
        "gate_digest": D, "evidence_digest": evidence["evidence_digest"], "status": "pass",
        "verifier_task_id": verifier["id"],
        "verifier_task_digest": verifier["task_digest"], "verified_at": T,
        "verification_digest": "",
    })
    recovery = signed({
        "schema_version": 2, "kind": "recovery", "id": "recovery-one",
        "task_id": task["id"], "task_digest": task["task_digest"],
        "prior_checkpoint_digest": checkpoint["checkpoint_digest"],
        "prior_receipt_digest": receipt["receipt_digest"], "action": "retry",
        "state": "queued", "failure_class": "timeout", "attempt": 1,
        "created_at": T, "outcome": "requeued", "recovery_digest": "",
    })
    supervisor = signed({
        "schema_version": 2, "kind": "supervisor", "id": "supervisor-one",
        "parent_goal": "goal-one", "final_authority": "lucas",
        "executive_identity": "hermes", "status": "active",
        "pause_observed": True, "pause_epoch": 1, "policy_digest": D,
        "valid_from": "2020-01-01T00:00:00Z",
        "valid_until": "2030-01-01T00:00:00Z", "supervisor_digest": "",
    })
    return {"supervisor": supervisor, "task": task, "budget": budget,
            "capability_grant": grant, "checkpoint": checkpoint,
            "receipt": receipt, "verification": verification,
            "recovery": recovery, "verifier": verifier, "assignment": assignment,
            "candidate": candidate, "evidence": evidence}


class MvpContractsTest(unittest.TestCase):
    def test_all_records_have_immutable_digests_and_cross_bindings(self):
        r = records()
        for key, value in r.items():
            if key not in {"verifier", "assignment", "candidate", "evidence"}:
                validate(value)
        validate_cross_records(list(r.values()))
        tampered = copy.deepcopy(r["receipt"])
        tampered["candidate_commit"] = "b" * 40
        with self.assertRaises(ContractError):
            validate(tampered)

    def test_unknown_missing_null_and_secret_fail_closed(self):
        task = copy.deepcopy(records()["task"])
        task["future"] = True
        with self.assertRaises(ContractError): validate(task)
        task = copy.deepcopy(records()["task"])
        task["acceptance"] = None
        with self.assertRaises(ContractError): validate(task)
        task = copy.deepcopy(records()["task"])
        task["acceptance"] = "chain_of_thought: hidden"
        with self.assertRaises(ContractError): validate(task)

    def test_child_task_grant_and_budget_cannot_escalate(self):
        parent = records()["task"]
        child = copy.deepcopy(parent)
        child.update(id="task-child", parent_task_id=parent["id"],
                     parent_task_digest=parent["task_digest"], depth=1,
                     allowed_paths=["src/lib"], requested_capabilities=["workspace-edit"],
                     budget_id="budget-child", task_digest="")
        child = signed(child)
        validate(child, parent_task=parent)
        bad = copy.deepcopy(child); bad["source_sha"] = "b" * 40; bad["task_digest"] = canonical_digest(bad)
        with self.assertRaises(ContractError): validate(bad, parent_task=parent)
        budget = records()["budget"]
        child_budget = copy.deepcopy(budget)
        child_budget.update(id="budget-child", task_id=child["id"],
                            task_digest=child["task_digest"], parent_budget_id=budget["id"],
                            token_limit=101, budget_digest="")
        child_budget = signed(child_budget)
        with self.assertRaises(ContractError): validate(child_budget, parent_budget=budget)

    def test_integer_money_approval_ceiling_remainders_and_time_reference(self):
        budget = records()["budget"]
        for field, value in (("cost_limit_cents", 1.5),
                             ("calendar_month_ceiling_cents", 2001),
                             ("remaining_cost_cents", 1)):
            bad = copy.deepcopy(budget); bad[field] = value; bad["budget_digest"] = canonical_digest(bad)
            with self.assertRaises(ContractError): validate(bad)
        bad = copy.deepcopy(budget)
        bad.update(metered_spend_allowed=True, approval_digest=None,
                   budget_digest="")
        bad["budget_digest"] = canonical_digest(bad)
        with self.assertRaises(ContractError): validate(bad)
        old = copy.deepcopy(records()["supervisor"])
        old["valid_from"] = "1900-01-01T00:00:00Z"
        old["supervisor_digest"] = canonical_digest(old)
        validate(old)

    def test_checkpoint_verification_recovery_bindings_and_typed_enums(self):
        r = records()
        second = signed({
            "schema_version": 2, "kind": "checkpoint", "id": "checkpoint-two",
            "task_id": r["task"]["id"], "task_digest": r["task"]["task_digest"],
            "packet_digest": D, "context_digest": D, "state_digest": D,
            "sequence": 1, "prev_digest": r["checkpoint"]["checkpoint_digest"],
            "created_at": T, "checkpoint_digest": "",
        })
        validate_checkpoint_chain([r["checkpoint"], second])
        bad = copy.deepcopy(r["verification"])
        bad["verifier_task_id"] = "task-one"
        bad["verification_digest"] = canonical_digest(bad)
        with self.assertRaises(ContractError): validate(bad)
        bad = copy.deepcopy(r["recovery"]); bad["action"] = "launch"; bad["recovery_digest"] = canonical_digest(bad)
        with self.assertRaises(ContractError): validate(bad)
        bad = copy.deepcopy(r["verification"]); bad["candidate_commit"] = "b" * 40
        bad["verification_digest"] = canonical_digest(bad)
        with self.assertRaises(ContractError): validate_cross_records([r["task"], r["receipt"], r["verification"], r["verifier"], bad])

    def test_local_schema_and_hostile_json_limits(self):
        schema = json.loads(Path(__file__).parents[2].joinpath(
            "schemas/control-plane/v2/mvp-contracts.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["oneOf"][0]["$ref"], "#/$defs/supervisor")
        value = "x"
        for _ in range(MAX_DEPTH + 2): value = [value]
        with self.assertRaises(ContractError): canonical_json(value)
        with self.assertRaises(ContractError): canonical_json("x" * 300_000)


if __name__ == "__main__":
    unittest.main()
