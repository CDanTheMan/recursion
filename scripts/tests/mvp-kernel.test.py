"""Material kernel contract coverage; runnable directly and under pytest."""
from __future__ import annotations

import copy
import hashlib
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
    assignment = copy.deepcopy(assignment)
    assignment.update(source_repository=task["source_repository"],
                      source_branch=task["source_branch"],
                      source_sha=task["source_sha"], assignment_digest="")
    assignment = signed(assignment)
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


def checkpoint_for(p, ident, sequence=0, prev_digest=None):
    return signed({
        "schema_version": 2, "kind": "checkpoint", "id": ident,
        "task_id": p["task"]["id"], "task_digest": p["task"]["task_digest"],
        "packet_digest": p.packet_digest, "context_digest": k._sha(p["context"]),
        "state_digest": "1" * 64, "sequence": sequence,
        "prev_digest": prev_digest, "created_at": "2026-08-31T12:00:00Z",
        "checkpoint_digest": "",
    })


def resigned(record):
    return signed(record)


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
        kept = k.retain_context(p, [{"id": "zz", "summary": "z", "priority": 1, "sequence": 1}, {"id": "aa", "summary": "a", "priority": 1, "sequence": 1}, {"id": "mm", "summary": "m", "mandatory": True}])
        self.assertEqual([x["id"] for x in kept["context"]], ["mm", "aa", "zz"])
        with self.assertRaises(k.KernelError): k.retain_context(p, [{"summary": "x" * 40, "mandatory": True}], limits=k.KernelLimits(max_tokens=1))
        for bad in ({"raw_prompt": "x", "summary": "x"}, {"summary": "chain\u200bof\u200bthought"}, {"summary": "x", "priority": True}, {"summary": "x", "digest": "f" * 64}):
            with self.assertRaises(k.KernelError): packet(context=[bad])

    def test_context_raw_labels_unicode_public_summary_and_ids(self):
        self.assertTrue(packet(context=[{"summary": "Public summary of the conversation."}]))
        for summary in (
            "prompt: answer the user",
            "raw\u200bmessage: all messages",
            "transcript = the full exchange",
            "conversation: every turn",
            "private_output: internal result",
        ):
            with self.assertRaises(k.KernelError):
                packet(context=[{"summary": summary}])
        for ident in ("a", "A1", "a_b", "a.", "éx"):
            with self.assertRaises(k.KernelError):
                packet(context=[{"id": ident, "summary": "safe summary"}])

    def test_context_raw_classifier_scans_bounded_summary_and_unicode_labels(self):
        labels = ("raw prompt", "raw message", "transcript", "prompt", "message", "conversation")
        for label in labels:
            with self.assertRaises(k.KernelError):
                packet(context=[{"summary": label}])
        for summary in (
            "safe prefix; prompt: payload",
            "safe prefix; context prompt: payload",
            ("safe " * 130) + "prompt: payload",
            "CONTEXT\u200bPROMPT\uff1a payload",
            "raw\u2010message\uFF1A payload",
        ):
            with self.assertRaises(k.KernelError):
                packet(context=[{"summary": summary}])
        self.assertTrue(packet(context=[{"summary": "A public conversation summary."}]))

    def test_optional_oversized_context_is_skipped_mandatory_fails(self):
        limits = k.KernelLimits(max_bytes=5000, max_tokens=10000)
        p = packet(limits=limits)
        kept = k.retain_context(p, [
            {"id": "zz", "summary": "x" * 10000},
            {"id": "mm", "summary": "keep", "mandatory": True},
        ])
        self.assertEqual([item["id"] for item in kept["context"]], ["mm"])
        with self.assertRaises(k.KernelError):
            k.retain_context(p, [{"id": "mm", "summary": "x" * 10000, "mandatory": True}])

    def test_validation_rechecks_persisted_aggregate_bytes_and_tokens(self):
        p = packet(context=[{"summary": "small"}])
        for field, value in (("max_bytes", 1), ("max_tokens", 1)):
            body = p.to_dict()
            body["limits"][field] = value
            body.pop("packet_digest")
            digest = hashlib.sha256(k._canonical(body)).hexdigest()
            body["packet_digest"] = digest
            with self.assertRaises(k.KernelError):
                k.validate_packet(k.TaskPacket(body, digest))

    def test_empty_context_is_within_one_token_and_selected_context_is_not_packet(self):
        tiny = k.KernelLimits(max_tokens=1)
        self.assertTrue(packet(limits=tiny))
        self.assertEqual(list(k.retain_context(packet(limits=tiny), [{"summary": "x"}])["context"]), [])
        with self.assertRaises(k.KernelError):
            k.retain_context(packet(limits=tiny), [{"summary": "x", "mandatory": True}])

    def test_cyclic_inputs_raise_kernel_error(self):
        supervisor, task, assignment, budget, grant, _ = fixture()
        cyclic = {}
        cyclic["self"] = cyclic
        with self.assertRaises(k.KernelError):
            packet(context=[{"summary": "safe", "evidence_refs": cyclic}])
        with self.assertRaises(k.KernelError):
            k.TaskPacket(cyclic, "0" * 64)
        with self.assertRaises(k.KernelError):
            k.validate_packet(cyclic)

    def test_pause_epoch_is_strict_current_integer(self):
        self.assertTrue(packet(pause_epoch=0))
        for value in (False, 0.0, -1, 1):
            with self.assertRaises(k.KernelError):
                packet(pause_epoch=value)

    def test_assignment_source_projection_is_strict_and_bound(self):
        _, task, assignment, _, _, _ = fixture()
        projected = copy.deepcopy(assignment)
        projected.update(source_repository=task["source_repository"],
                         source_branch=task["source_branch"],
                         source_sha=task["source_sha"], assignment_digest="")
        projected = resigned(projected)
        self.assertTrue(packet(assignment=projected))
        stale = copy.deepcopy(projected)
        stale["source_sha"] = "b" * 40
        stale = resigned(stale)
        with self.assertRaises(k.KernelError):
            packet(assignment=stale)
        unknown = copy.deepcopy(assignment)
        unknown["source_sha"] = task["source_sha"]
        unknown["assignment_digest"] = c.canonical_digest(unknown)
        unknown["unexpected"] = "x"
        with self.assertRaises(k.KernelError):
            packet(assignment=unknown)

    def test_checkpoint_genesis_chain_packet_and_context_bindings(self):
        p = packet()
        genesis = checkpoint_for(p, "checkpoint-one")
        self.assertTrue(packet(checkpoint=genesis))
        second = checkpoint_for(p, "checkpoint-two", 1, genesis["checkpoint_digest"])
        self.assertEqual(c.validate_checkpoint_chain([genesis, second])[-1]["sequence"], 1)
        with self.assertRaises(c.ContractError):
            c.validate_checkpoint_chain([genesis, {**second, "prev_digest": "2" * 64,
                                                   "checkpoint_digest": c.canonical_digest({**second, "prev_digest": "2" * 64})}])
        with self.assertRaises(c.ContractError):
            c.validate_checkpoint_chain([genesis, {**second, "sequence": 0,
                                                   "prev_digest": None,
                                                   "checkpoint_digest": c.canonical_digest({**second, "sequence": 0, "prev_digest": None})}])
        q = packet(checkpoint=genesis)
        body = q.to_dict()
        body["context"] = [{"summary": "mutated"}]
        body["packet_digest"] = hashlib.sha256(k._canonical({key: value for key, value in body.items() if key != "packet_digest"})).hexdigest()
        with self.assertRaises(k.KernelError):
            k.validate_packet(k.TaskPacket(body, body["packet_digest"]))

    def test_parent_authority_projection_requires_external_lineage_anchor(self):
        root = packet()
        _, task, assignment, budget, grant, _ = fixture()

        def child(parent, depth, suffix):
            child_task = copy.deepcopy(task)
            child_task.update(id=f"task-{suffix}", depth=depth,
                              parent_task_id=parent["task"]["id"],
                              parent_task_digest=parent["task"]["task_digest"],
                              budget_id=f"budget-{suffix}", task_digest="")
            child_task = resigned(child_task)
            child_budget = copy.deepcopy(budget)
            child_budget.update(id=f"budget-{suffix}", task_id=child_task["id"],
                                task_digest=child_task["task_digest"],
                                parent_budget_id=parent["budget"]["id"], budget_digest="")
            child_budget = resigned(child_budget)
            child_assignment = copy.deepcopy(assignment)
            child_assignment.update(task_id=child_task["id"],
                                    task_digest=child_task["task_digest"], assignment_digest="")
            child_assignment = resigned(child_assignment)
            child_grant = copy.deepcopy(grant)
            child_grant.update(task_id=child_task["id"],
                               task_digest=child_task["task_digest"], grant_digest="")
            child_grant = resigned(child_grant)
            return k.spawn_child(parent, task=child_task, assignment=child_assignment,
                                 budget=child_budget, grant=child_grant)

        one = child(root, 1, "child")
        two = child(one, 2, "grandchild")
        body = two.to_dict()
        self.assertNotIn("context", body["parent"])
        with self.assertRaises(k.KernelError):
            k.validate_packet(two)
        self.assertTrue(k.validate_packet(
            two, expected_parent_digest=one.packet_digest,
            expected_lineage=[one.packet_digest, root.packet_digest]))
        body["parent"]["context"] = []
        body["packet_digest"] = hashlib.sha256(k._canonical({key: value for key, value in body.items() if key != "packet_digest"})).hexdigest()
        with self.assertRaises(k.KernelError):
            k.validate_packet(k.TaskPacket(body, body["packet_digest"]),
                              expected_parent_digest=one.packet_digest,
                              expected_lineage=[one.packet_digest, root.packet_digest])
        body = two.to_dict()
        body["parent"]["task"]["id"] = "task-forged"
        body["packet_digest"] = hashlib.sha256(k._canonical({key: value for key, value in body.items() if key != "packet_digest"})).hexdigest()
        with self.assertRaises(k.KernelError):
            k.validate_packet(k.TaskPacket(body, body["packet_digest"]),
                              expected_parent_digest=one.packet_digest,
                              expected_lineage=[{
                                  **one.to_dict(), "packet_digest": one.packet_digest,
                              }, root.packet_digest])

    def test_evidence_must_be_declared_and_bound(self):
        p = packet(); ev = signed({"kind": "evidence", "id": "evidence-one", "task_id": p["task"]["id"], "task_digest": p["task"]["task_digest"]}); ref = {"id": ev["id"], "sha256": ev["evidence_digest"]}
        self.assertTrue(k.build_packet(supervisor=p["supervisor"], task=p["task"], assignment=p["assignment"], budget=p["budget"], grant=p["grant"], evidence=[ev], evidence_refs=[ref]))
        with self.assertRaises(k.KernelError): packet(evidence_refs=[ref])

    def test_receipt_and_verification_cross_bindings_fail_closed(self):
        original = _contracts_fixture()
        self.assertEqual(len(c.validate_cross_records(list(copy.deepcopy(original).values()))),
                         len(original))

        def assert_rejected(kind, ident, mutate):
            records = copy.deepcopy(original)
            target = next(item for item in records.values()
                          if item["kind"] == kind and item["id"] == ident)
            mutate(target)
            target.update({
                {"receipt": "receipt_digest", "verification": "verification_digest"}[kind]:
                c.canonical_digest(target)
            })
            with self.assertRaises(c.ContractError):
                c.validate_cross_records(list(records.values()))

        assert_rejected("receipt", "receipt-one", lambda item: item.update(task_id="task-other"))
        assert_rejected("receipt", "receipt-one", lambda item: item.update(task_digest="1" * 64))
        assert_rejected("receipt", "receipt-one", lambda item: item.update(assignment_digest="1" * 64))
        assert_rejected("receipt", "receipt-one", lambda item: item.update(checkpoint_digests=["1" * 64]))
        assert_rejected("receipt", "receipt-one", lambda item: item.update(candidate_id="candidate-other"))
        assert_rejected("receipt", "receipt-one", lambda item: item.update(candidate_commit="b" * 40))
        assert_rejected("receipt", "receipt-one", lambda item: item.update(result_digest="1" * 64))
        assert_rejected("verification", "verification-one", lambda item: item.update(evidence_digest="1" * 64))

    def test_packet_unknown_limits_and_outer_forgery_fail(self):
        p = packet(); d = p.to_dict(); d["limits"]["max_tokens"] = 1
        with self.assertRaises(k.KernelError): k.validate_packet(k.TaskPacket(d, p.packet_digest))
        d = p.to_dict(); d["task"]["depth"] = 1
        with self.assertRaises(k.KernelError): k.validate_packet(k.TaskPacket(d, p.packet_digest))

    def test_import_is_inert(self):
        self.assertTrue(hasattr(k, "build_packet"))


if __name__ == "__main__":
    unittest.main()
