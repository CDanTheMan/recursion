"""Material kernel contract coverage; runnable directly and under pytest."""
from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import mvp_contracts as c
import mvp_kernel as k


def _contracts_fixture():
    path = ROOT / "scripts/tests/mvp-contracts.test.py"
    spec = importlib.util.spec_from_file_location("mvp_contract_fixture", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.records()


def signed(record):
    value = copy.deepcopy(record)
    field = {"capability_grant": "grant_digest"}.get(value["kind"], value["kind"] + "_digest")
    value[field] = c.canonical_digest(value)
    return value


def fixture():
    values = _contracts_fixture()
    task, budget, grant, assignment = (values[x] for x in ("task", "budget", "capability_grant", "assignment"))
    supervisor = signed({
        "schema_version": 2, "kind": "supervisor", "id": "supervisor-one",
        "parent_goal": task["parent_goal"], "final_authority": "lucas",
        "executive_identity": "hermes", "status": "active", "pause_observed": False,
        "pause_epoch": 0, "policy_digest": "0" * 64,
        "valid_from": "2020-01-01T00:00:00Z", "valid_until": "2030-01-01T00:00:00Z",
        "supervisor_digest": "",
    })
    return supervisor, task, assignment, budget, grant, values


def packet(**kwargs):
    supervisor, task, assignment, budget, grant, _ = fixture()
    args = dict(supervisor=supervisor, task=task, assignment=assignment, budget=budget,
                grant=grant, supervisor_digest=supervisor["supervisor_digest"])
    args.update(kwargs)
    return k.build_packet(**args)


class KernelTest(unittest.TestCase):
    def test_valid_root_and_mapping_thaw_mutation_isolation(self):
        p = packet()
        self.assertEqual(k.validate_packet(p).packet_digest, p.packet_digest)
        with self.assertRaises(TypeError):
            p.value["task"] = {}  # type: ignore[index]
        thawed = p.to_dict(); thawed["task"]["id"] = "changed"
        self.assertEqual(p["task"]["id"], "task-one")

    def test_valid_child_depth_one_two_and_depth_two_rejected(self):
        root = packet(); _, task, assignment, budget, grant, _ = fixture(); parent = root
        for depth in (1, 2):
            child_task = copy.deepcopy(task)
            child_task.update(id=f"task-child-{depth}", depth=depth,
                              parent_task_id=parent["task"]["id"], parent_task_digest=parent["task"]["task_digest"],
                              budget_id=f"budget-child-{depth}", task_digest="")
            child_task = signed(child_task)
            child_budget = copy.deepcopy(budget)
            child_budget.update(id=f"budget-child-{depth}", task_id=child_task["id"], task_digest=child_task["task_digest"],
                                parent_budget_id=parent["budget"]["id"], budget_digest="")
            child_budget = signed(child_budget)
            child_assignment = copy.deepcopy(assignment)
            child_assignment.update(task_id=child_task["id"], task_digest=child_task["task_digest"], assignment_digest="")
            child_assignment = signed(child_assignment)
            child_grant = copy.deepcopy(grant)
            child_grant.update(task_id=child_task["id"], task_digest=child_task["task_digest"], grant_digest="")
            child_grant = signed(child_grant)
            parent = k.spawn_child(parent, task=child_task, assignment=child_assignment, budget=child_budget, grant=child_grant)
        with self.assertRaises(k.KernelError):
            k.spawn_child(parent, task=task, assignment=assignment, budget=budget, grant=grant)

    def test_rejects_semantic_digest_forgery_and_bindings(self):
        _, task, _, _, grant, _ = fixture()
        bad = copy.deepcopy(task); bad["acceptance"] = "changed"; bad["task_digest"] = c.canonical_digest(bad)
        with self.assertRaises(k.KernelError): packet(task=bad)
        with self.assertRaises(k.KernelError): packet(supervisor_digest="f" * 64)
        bad_grant = copy.deepcopy(grant); bad_grant["task_id"] = "task-other"; bad_grant["grant_digest"] = c.canonical_digest(bad_grant)
        with self.assertRaises(k.KernelError): packet(grant=bad_grant)

    def test_path_boundary_capability_grant_and_budget_escalation(self):
        root = packet(); _, task, assignment, budget, grant, _ = fixture()
        child_task = copy.deepcopy(task); child_task.update(id="task-child", depth=1, parent_task_id=task["id"], parent_task_digest=task["task_digest"], budget_id="budget-child", allowed_paths=["src2"], task_digest=""); child_task = signed(child_task)
        child_budget = copy.deepcopy(budget); child_budget.update(id="budget-child", task_id=child_task["id"], task_digest=child_task["task_digest"], parent_budget_id=budget["id"], token_limit=101, budget_digest=""); child_budget = signed(child_budget)
        child_assignment = copy.deepcopy(assignment); child_assignment.update(task_id=child_task["id"], task_digest=child_task["task_digest"], assignment_digest=""); child_assignment = signed(child_assignment)
        child_grant = copy.deepcopy(grant); child_grant.update(task_id=child_task["id"], task_digest=child_task["task_digest"], allowed_paths=["src2"], grant_digest=""); child_grant = signed(child_grant)
        with self.assertRaises(k.KernelError): k.spawn_child(root, task=child_task, assignment=child_assignment, budget=child_budget, grant=child_grant)

    def test_pause_root_late_and_inherited(self):
        supervisor, _, _, _, _, _ = fixture()
        paused = copy.deepcopy(supervisor); paused["pause_observed"] = True; paused["pause_epoch"] = 1; paused["supervisor_digest"] = c.canonical_digest(paused)
        with self.assertRaises(k.KernelError): packet(supervisor=paused, supervisor_digest=paused["supervisor_digest"])
        p = packet()
        with self.assertRaises(k.KernelError): k.validate_packet(p, pause_observed=True)
        with self.assertRaises(k.KernelError): k.retain_context(p, [], pause_epoch=1)

    def test_context_order_ties_overflow_token_boundary_and_strict_scan(self):
        p = packet()
        kept = k.retain_context(p, [{"id": "z", "summary": "z", "priority": 1, "sequence": 1}, {"id": "a", "summary": "a", "priority": 1, "sequence": 1}, {"id": "m", "summary": "m", "mandatory": True}])
        self.assertEqual([x["id"] for x in kept["context"]], ["m", "a", "z"])
        with self.assertRaises(k.KernelError): k.retain_context(p, [{"summary": "x" * 40, "mandatory": True}], limits=k.KernelLimits(max_tokens=1))
        for bad in ({"raw_prompt": "x", "summary": "x"}, {"summary": "chain\u200bof\u200bthought"}, {"summary": "x", "priority": True}, {"summary": "x", "digest": "f" * 64}):
            with self.assertRaises(k.KernelError): packet(context=[bad])

    def test_evidence_must_be_declared_and_bound(self):
        p = packet(); ev = signed({"kind": "evidence", "id": "evidence-one", "task_id": p["task"]["id"], "task_digest": p["task"]["task_digest"]}); ref = {"id": ev["id"], "sha256": ev["evidence_digest"]}
        self.assertTrue(k.build_packet(supervisor=p["supervisor"], task=p["task"], assignment=p["assignment"], budget=p["budget"], grant=p["grant"], evidence=[ev], evidence_refs=[ref]))
        with self.assertRaises(k.KernelError): packet(evidence_refs=[ref])

    def test_packet_unknown_limits_and_outer_forgery_fail(self):
        p = packet(); d = p.to_dict(); d["limits"]["max_tokens"] = 1
        with self.assertRaises(k.KernelError): k.validate_packet(k.TaskPacket(d, p.packet_digest))
        d = p.to_dict(); d["task"]["depth"] = 1
        with self.assertRaises(k.KernelError): k.validate_packet(k.TaskPacket(d, p.packet_digest))

    def test_import_is_inert(self):
        self.assertTrue(hasattr(k, "build_packet"))


if __name__ == "__main__":
    unittest.main()
