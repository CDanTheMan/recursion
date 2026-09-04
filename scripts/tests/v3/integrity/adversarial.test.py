#!/usr/bin/env python3
"""Fail-closed structural and semantic adversarial gates for M1C."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from typing import Any, Callable

import jsonschema


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schema_gate = load_module("m1c_adversarial_schema", HERE / "schema.test.py")
oracle = load_module("m1c_adversarial_oracle", HERE / "reference_oracle.py")


def load_fixture(number: int) -> dict[str, Any]:
    path = FIXTURES / f"F-M1C-{number:03d}.json"
    return schema_gate.strict_loads(path.read_bytes())


def mutate_first(value: Any, predicate: Callable[[str, Any], bool], replacement: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if predicate(key, item):
                value[key] = replacement
                return True
            if mutate_first(item, predicate, replacement):
                return True
    elif isinstance(value, list):
        for item in value:
            if mutate_first(item, predicate, replacement):
                return True
    return False


class M1CMutationMatrixTests(unittest.TestCase):
    families = {
        "evidence": 1,
        "effect": 6,
        "publication": 11,
        "state": 16,
        "retention": 21,
    }

    @staticmethod
    def mutations(bundle: dict[str, Any]) -> dict[str, dict[str, Any]]:
        values: dict[str, dict[str, Any]] = {}

        changed = copy.deepcopy(bundle)
        changed["unknown_field"] = "denied"
        values["unknown-field"] = changed

        changed = copy.deepcopy(bundle)
        changed["type"] = changed["type"].replace("@1", "@2")
        values["discriminator-version"] = changed

        changed = copy.deepcopy(bundle)
        changed["fixture_id"] = "F-M1C-X"
        values["fixture-id"] = changed

        changed = copy.deepcopy(bundle)
        assert mutate_first(
            changed,
            lambda key, item: key.endswith("digest") and isinstance(item, str),
            "sha256:INVALID",
        )
        values["digest"] = changed

        changed = copy.deepcopy(bundle)
        assert mutate_first(
            changed,
            lambda _key, item: isinstance(item, int) and not isinstance(item, bool),
            True,
        )
        values["exact-integer"] = changed

        changed = copy.deepcopy(bundle)
        changed["source_requirement_ids"] = ["ZZZ", "AAA"]
        values["ordering"] = changed

        changed = copy.deepcopy(bundle)
        changed["source_requirement_ids"] = ["AAA", "AAA"]
        values["uniqueness"] = changed

        changed = copy.deepcopy(bundle)
        changed["source_requirement_ids"] = []
        values["collection-bound"] = changed
        return values

    def test_five_by_eight_structural_mutation_matrix_fails_closed(self) -> None:
        count = 0
        for family, number in self.families.items():
            for mutation, changed in self.mutations(load_fixture(number)).items():
                count += 1
                with self.subTest(family=family, mutation=mutation):
                    with self.assertRaises(jsonschema.ValidationError):
                        schema_gate.validate(changed, "M1CFixtureBundle")
        self.assertEqual(count, 40)


class M1CSemanticAdversarialTests(unittest.TestCase):
    def assert_reason(self, decision: dict[str, Any], reason: str, status: str) -> None:
        self.assertEqual(decision["status"], status)
        self.assertIn(reason, decision["reasons"])

    def test_evidence_stale_inapplicable_and_unverified_never_support(self) -> None:
        cases = {
            "source-stale": lambda item: item["input"]["sources"][0].update(
                {"revalidate_after": "2026-01-01T00:00:00Z"}
            ),
            "scope-inapplicable": lambda item: item["input"]["edges"][0].update(
                {"applicability": "partial"}
            ),
            "extraction-unverified": lambda item: item["input"]["edges"][0].update(
                {"extraction_verified": False}
            ),
        }
        for reason, change in cases.items():
            bundle = load_fixture(1)
            change(bundle)
            decision = oracle.assess_evidence(bundle["input"])
            with self.subTest(reason=reason):
                self.assert_reason(decision, reason, "unknown")
                self.assertEqual(decision["accepted_edge_ids"], [])

    def test_evidence_cross_binding_refuses_and_contradiction_survives(self) -> None:
        bundle = load_fixture(1)
        bundle["input"]["edges"][0]["source_version"] = "v2"
        self.assert_reason(
            oracle.assess_evidence(bundle["input"]), "edge-binding-mismatch", "refused"
        )

        bundle = load_fixture(4)
        decision = oracle.assess_evidence(bundle["input"])
        self.assertEqual(decision["status"], "contested")
        self.assertEqual(decision["contradiction_edge_ids"], ["edge:contradiction"])

    def test_effect_binding_receipt_dependency_and_retry_fail_closed(self) -> None:
        bundle = load_fixture(7)
        bundle["input"]["observations"][-1]["payload_digest"] = "sha256:" + "4" * 64
        self.assert_reason(
            oracle.classify_effect_trace(bundle["input"]),
            "receipt-binding-mismatch",
            "ambiguous",
        )

        bundle = load_fixture(6)
        bundle["input"]["intent"]["dependency_effect_ids"] = ["effect:dependency"]
        bundle["input"]["intent"] = schema_gate.seal(bundle["input"]["intent"], "intent_digest")
        bundle["input"]["admission"]["intent_digest"] = bundle["input"]["intent"]["intent_digest"]
        self.assert_reason(
            oracle.classify_effect_trace(bundle["input"]), "dependency-unresolved", "refused"
        )

        decision = oracle.classify_effect_trace(load_fixture(9)["input"])
        self.assert_reason(decision, "blind-retry-blocked", "ambiguous")

    def test_authenticated_reconciliation_is_new_settled_evidence(self) -> None:
        bundle = load_fixture(8)
        intent = bundle["input"]["intent"]
        bundle["input"]["observations"].append(
            {
                "type": "ReconciliationObserved@1",
                "effect_id": intent["effect_id"],
                "attempt_id": "attempt:1",
                "attempt_number": 1,
                "idempotency_key": intent["idempotency_key"],
                "target_ref": intent["target_ref"],
                "payload_digest": intent["payload_digest"],
                "admission_epoch": intent["admission_epoch"],
                "fence_epoch": intent["fence_epoch"],
                "observed_at": "2026-09-04T12:02:00Z",
                "reconciliation_id": "reconciliation:one",
                "observer_ref": "observer:synthetic",
                "authenticity": "verified",
                "outcome": "succeeded",
                "result_digest": "sha256:" + "3" * 64,
                "remote_operation_ref": "remote:one",
            }
        )
        decision = oracle.classify_effect_trace(bundle["input"])
        self.assertEqual(decision["status"], "reconciled-succeeded")
        self.assertFalse(decision["requires_reconciliation"])

    def test_publication_exact_receipt_and_rejection_are_settled(self) -> None:
        for remote_state, expected in (("observed", "published"), ("rejected", "rejected")):
            bundle = load_fixture(15)
            receipt = bundle["input"]["receipt"]
            receipt["remote_state"] = remote_state
            receipt["remote_commit_sha"] = (
                bundle["input"]["intent"]["candidate_sha"] if remote_state == "observed" else None
            )
            bundle["input"]["receipt"] = schema_gate.seal(receipt, "receipt_digest")
            decision = oracle.assess_publication(bundle["input"])
            with self.subTest(remote_state=remote_state):
                self.assertEqual(decision["status"], expected)
                self.assertFalse(decision["requires_reconciliation"])

    def test_publication_candidate_gate_verifier_and_receipt_bind_exactly(self) -> None:
        cases = {
            "gate-binding-mismatch": lambda item: item["input"]["gates"][0].update(
                {"candidate_sha": "c" * 40}
            ),
            "verification-binding-mismatch": lambda item: item["input"]["verifiers"][0].update(
                {"source_sha": "c" * 40}
            ),
            "candidate-dirty": lambda item: item["input"].update({"candidate_tree": "dirty"}),
        }
        for reason, change in cases.items():
            bundle = load_fixture(11)
            change(bundle)
            decision = oracle.assess_publication(bundle["input"])
            with self.subTest(reason=reason):
                self.assert_reason(decision, reason, "blocked")

        bundle = load_fixture(15)
        bundle["input"]["receipt"]["review_ref"] = "refs/heads/review/other"
        self.assert_reason(
            oracle.assess_publication(bundle["input"]), "receipt-binding-mismatch", "blocked"
        )

    def test_state_duplicate_command_fence_and_event_auth_require_recovery(self) -> None:
        cases = {
            "stale-fence": lambda item: item["input"]["events"][0].update({"fence_epoch": 1}),
            "event-unverified": lambda item: item["input"]["events"][0].update(
                {"authentication_state": "unverified"}
            ),
        }
        for reason, change in cases.items():
            bundle = load_fixture(16)
            change(bundle)
            event = bundle["input"]["events"][0]
            bundle["input"]["events"][0] = schema_gate.seal(event, "event_digest")
            decision = oracle.assess_state_contract(bundle["input"])
            with self.subTest(reason=reason):
                self.assert_reason(decision, reason, "recovery-required")

        bundle = load_fixture(16)
        first = bundle["input"]["events"][0]
        second = copy.deepcopy(first)
        second.update(
            {
                "sequence": 2,
                "event_id": "event:two",
                "command_id": first["command_id"],
                "idempotency_key": "idempotency:two",
                "causation_id": first["event_id"],
                "logical_time": 2,
                "previous_event_digest": first["event_digest"],
                "payload_digest": "sha256:" + "4" * 64,
            }
        )
        bundle["input"]["events"].append(schema_gate.seal(second, "event_digest"))
        self.assert_reason(
            oracle.assess_state_contract(bundle["input"]),
            "duplicate-command-conflict",
            "recovery-required",
        )

    def test_state_unknown_writer_and_projection_only_never_transfer(self) -> None:
        self.assert_reason(
            oracle.assess_state_contract(load_fixture(17)["input"]),
            "writer-inventory-incomplete",
            "blocked",
        )
        self.assert_reason(
            oracle.assess_state_contract(load_fixture(20)["input"]),
            "projection-only",
            "blocked",
        )

    def test_retention_soft_delete_shared_key_and_tombstone_mismatch_fail(self) -> None:
        bundle = load_fixture(21)
        bundle["input"]["copies"][1].update(
            {
                "state": "soft-deleted",
                "evidence_state": "unverified",
                "evidence_digest": None,
            }
        )
        bundle["input"]["tombstone"]["copy_dispositions"] = copy.deepcopy(
            bundle["input"]["copies"]
        )
        bundle["input"]["tombstone"] = schema_gate.seal(
            bundle["input"]["tombstone"], "tombstone_digest"
        )
        self.assert_reason(
            oracle.assess_retention(bundle["input"]), "copy-unresolved", "incomplete"
        )

        self.assert_reason(
            oracle.assess_retention(load_fixture(23)["input"]),
            "key-not-isolated",
            "blocked",
        )
        bundle = load_fixture(21)
        bundle["input"]["tombstone"]["policy_digest"] = "sha256:" + "4" * 64
        self.assert_reason(
            oracle.assess_retention(bundle["input"]), "tombstone-mismatch", "blocked"
        )

    def test_owner_receipt_erasure_requires_explicit_policy(self) -> None:
        decision = oracle.assess_retention(load_fixture(24)["input"])
        self.assert_reason(decision, "owner-policy-required", "blocked")


if __name__ == "__main__":
    suite = unittest.TestSuite(
        (
            unittest.defaultTestLoader.loadTestsFromTestCase(M1CMutationMatrixTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(M1CSemanticAdversarialTests),
        )
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("M1C_ADVERSARIAL_PASS structural_mutations=40 semantic_groups=10")
    raise SystemExit(0 if result.wasSuccessful() else 1)
