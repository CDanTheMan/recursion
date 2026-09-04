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

    def test_schema_valid_semantic_variant_matrix_has_closed_outputs(self) -> None:
        count = 0

        def check(
            bundle: dict[str, Any], input_definition: str,
            decision_definition: str, evaluator: Callable[[dict[str, Any]], dict[str, Any]],
        ) -> None:
            nonlocal count
            schema_gate.validate(bundle["input"], input_definition)
            schema_gate.validate(evaluator(bundle["input"]), decision_definition)
            count += 1

        for editorial in ("current", "corrected", "superseded", "retracted", "withdrawn", "unknown"):
            bundle = load_fixture(1)
            bundle["input"]["sources"][0]["editorial_state"] = editorial
            check(bundle, "EvidenceAssessmentInput", "EvidenceDecision", oracle.assess_evidence)
        for lifecycle in ("discovered", "identified", "retrieved", "verified", "quarantined", "expired"):
            bundle = load_fixture(1)
            bundle["input"]["sources"][0]["lifecycle"] = lifecycle
            check(bundle, "EvidenceAssessmentInput", "EvidenceDecision", oracle.assess_evidence)
        for license_state in ("permitted", "restricted", "prohibited", "unknown"):
            bundle = load_fixture(1)
            bundle["input"]["sources"][0]["license_state"] = license_state
            bundle["input"]["allowed_license_states"] = [license_state]
            check(bundle, "EvidenceAssessmentInput", "EvidenceDecision", oracle.assess_evidence)
        for applicability in ("exact", "partial", "inapplicable", "unknown"):
            bundle = load_fixture(1)
            bundle["input"]["edges"][0]["applicability"] = applicability
            check(bundle, "EvidenceAssessmentInput", "EvidenceDecision", oracle.assess_evidence)

        for outcome in ("accepted", "rejected", "unknown"):
            bundle = load_fixture(8)
            bundle["input"]["observations"][-1]["outcome"] = outcome
            bundle["input"]["observations"][-1]["result_digest"] = (
                None if outcome == "unknown" else "sha256:" + "3" * 64
            )
            check(bundle, "EffectTraceInput", "EffectDecision", oracle.classify_effect_trace)
        for authenticity in ("verified", "unverified", "mismatch"):
            bundle = load_fixture(8)
            bundle["input"]["observations"][-1]["authenticity"] = authenticity
            check(bundle, "EffectTraceInput", "EffectDecision", oracle.classify_effect_trace)
        for result in ("succeeded", "failed"):
            bundle = load_fixture(7)
            bundle["input"]["observations"][-1]["result"] = result
            check(bundle, "EffectTraceInput", "EffectDecision", oracle.classify_effect_trace)

        for publication_kind in ("review-branch", "merge", "release", "deployment"):
            bundle = load_fixture(11)
            bundle["input"]["intent"]["publication_kind"] = publication_kind
            bundle["input"]["intent"] = schema_gate.seal(bundle["input"]["intent"], "intent_digest")
            check(bundle, "PublicationAssessmentInput", "PublicationDecision", oracle.assess_publication)
        for source_ancestry in ("known-ancestor", "not-ancestor", "unknown"):
            bundle = load_fixture(11)
            bundle["input"]["source_ancestry"] = source_ancestry
            check(bundle, "PublicationAssessmentInput", "PublicationDecision", oracle.assess_publication)
        for candidate_tree in ("clean", "dirty", "unknown"):
            bundle = load_fixture(11)
            bundle["input"]["candidate_tree"] = candidate_tree
            check(bundle, "PublicationAssessmentInput", "PublicationDecision", oracle.assess_publication)
        for authority in ("granted", "denied", "unknown"):
            bundle = load_fixture(11)
            bundle["input"]["publication_authority"] = authority
            check(bundle, "PublicationAssessmentInput", "PublicationDecision", oracle.assess_publication)
        for gate_status in ("pass", "fail", "unavailable"):
            bundle = load_fixture(11)
            bundle["input"]["gates"][0]["status"] = gate_status
            check(bundle, "PublicationAssessmentInput", "PublicationDecision", oracle.assess_publication)
        for verifier_status in ("pass", "dissent", "unavailable"):
            bundle = load_fixture(11)
            bundle["input"]["verifiers"][0]["status"] = verifier_status
            check(bundle, "PublicationAssessmentInput", "PublicationDecision", oracle.assess_publication)

        for import_state in ("lossless", "lossy", "unknown"):
            bundle = load_fixture(16)
            bundle["input"]["import_state"] = import_state
            check(bundle, "StateContractAssessmentInput", "StateDecision", oracle.assess_state_contract)
        for field in ("writer_refusal", "backup", "restore", "reverse_reader", "rollback"):
            for proof in ("verified", "failed", "unknown"):
                bundle = load_fixture(16)
                bundle["input"][field] = proof
                check(bundle, "StateContractAssessmentInput", "StateDecision", oracle.assess_state_contract)
        for deployment in ("known", "unknown"):
            bundle = load_fixture(16)
            bundle["input"]["deployment_revision_state"] = deployment
            check(bundle, "StateContractAssessmentInput", "StateDecision", oracle.assess_state_contract)

        for key_state in ("destroyed", "active", "shared", "unknown"):
            bundle = load_fixture(21)
            bundle["input"]["key_state"] = key_state
            check(bundle, "RetentionAssessmentInput", "RetentionDecision", oracle.assess_retention)
        for key_scope in ("artifact", "project", "shared", "unknown"):
            bundle = load_fixture(21)
            bundle["input"]["key_scope"] = key_scope
            check(bundle, "RetentionAssessmentInput", "RetentionDecision", oracle.assess_retention)
        for owner_policy in ("granted", "denied", "unknown", "not-required"):
            bundle = load_fixture(24)
            bundle["input"]["owner_erasure_policy"] = owner_policy
            check(bundle, "RetentionAssessmentInput", "RetentionDecision", oracle.assess_retention)

        self.assertEqual(count, 79)

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

    def test_mismatching_persistent_identifier_cannot_hide_beside_verified_one(self) -> None:
        bundle = load_fixture(1)
        source = bundle["input"]["sources"][0]
        source["persistent_identifiers"].insert(
            0,
            {
                "type": "PersistentIdentifier@1",
                "scheme": "arxiv",
                "value": "mismatch:one",
                "verification_state": "mismatch",
                "verification_evidence_digest": None,
            },
        )
        schema_gate.validate(bundle["input"], "EvidenceAssessmentInput")
        decision = oracle.assess_evidence(bundle["input"])
        self.assert_reason(decision, "source-unverified", "unknown")

    def test_unknown_license_claim_expiry_and_future_retrieval_never_support(self) -> None:
        cases = {
            "license-prohibited": lambda item: (
                item["input"]["sources"][0].update({"license_state": "unknown"}),
                item["input"].update({"allowed_license_states": ["unknown"]}),
            ),
            "claim-expired": lambda item: item["input"]["claim"].update(
                {"revalidate_after": "2026-01-01T00:00:00Z"}
            ),
            "future-retrieval": lambda item: item["input"]["sources"][0].update(
                {"retrieved_at": "2026-09-05T00:00:00Z"}
            ),
            "expired-lifecycle": lambda item: item["input"]["sources"][0].update(
                {"lifecycle": "expired"}
            ),
        }
        for name, change in cases.items():
            bundle = load_fixture(1)
            change(bundle)
            schema_gate.validate(bundle["input"], "EvidenceAssessmentInput")
            decision = oracle.assess_evidence(bundle["input"])
            with self.subTest(case=name):
                self.assertNotEqual(decision["status"], "supported")
                if name == "license-prohibited":
                    self.assertIn("license-prohibited", decision["reasons"])
                elif name in {"claim-expired", "expired-lifecycle"}:
                    self.assertIn("source-stale", decision["reasons"])
                else:
                    self.assertIn("source-unverified", decision["reasons"])

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

        bundle["input"]["observations"][-1].update(
            {"outcome": "unknown", "result_digest": None}
        )
        decision = oracle.classify_effect_trace(bundle["input"])
        self.assert_reason(decision, "reconciliation-required", "ambiguous")

    def test_later_receipt_cannot_erase_blind_retry_or_result_conflict(self) -> None:
        bundle = load_fixture(9)
        receipt = copy.deepcopy(load_fixture(7)["input"]["observations"][-1])
        receipt.update({"attempt_id": "attempt:2", "attempt_number": 2})
        bundle["input"]["observations"].append(receipt)
        schema_gate.validate(bundle["input"], "EffectTraceInput")
        decision = oracle.classify_effect_trace(bundle["input"])
        self.assert_reason(decision, "blind-retry-blocked", "ambiguous")
        self.assertIn("receipt-missing", decision["reasons"])

        bundle = load_fixture(9)
        bundle["input"]["observations"][1]["authenticity"] = "unverified"
        receipt = copy.deepcopy(load_fixture(7)["input"]["observations"][-1])
        receipt.update({"attempt_id": "attempt:2", "attempt_number": 2})
        bundle["input"]["observations"].append(receipt)
        schema_gate.validate(bundle["input"], "EffectTraceInput")
        decision = oracle.classify_effect_trace(bundle["input"])
        self.assert_reason(decision, "blind-retry-blocked", "ambiguous")
        self.assertIn("observation-unverified", decision["reasons"])
        self.assertIn("receipt-missing", decision["reasons"])

        bundle = load_fixture(7)
        bundle["input"]["observations"][-1]["result_digest"] = "sha256:" + "4" * 64
        schema_gate.validate(bundle["input"], "EffectTraceInput")
        decision = oracle.classify_effect_trace(bundle["input"])
        self.assert_reason(decision, "observation-conflict", "ambiguous")

        bundle = load_fixture(7)
        bundle["input"]["observations"][-1]["observer_ref"] = "observer:other"
        schema_gate.validate(bundle["input"], "EffectTraceInput")
        decision = oracle.classify_effect_trace(bundle["input"])
        self.assert_reason(decision, "observation-conflict", "ambiguous")

        bundle = load_fixture(7)
        contradictory = copy.deepcopy(bundle["input"]["observations"][1])
        contradictory.update({"observation_id": "observation:two", "outcome": "rejected"})
        bundle["input"]["observations"].insert(2, contradictory)
        schema_gate.validate(bundle["input"], "EffectTraceInput")
        decision = oracle.classify_effect_trace(bundle["input"])
        self.assert_reason(decision, "observation-conflict", "ambiguous")

    def test_exact_effect_receipt_owns_history_without_erasing_admission_violation(self) -> None:
        bundle = load_fixture(7)
        bundle["input"]["admission"].update(
            {"decision": "refused", "pause_state": "paused", "reasons": ["paused"]}
        )
        schema_gate.validate(bundle["input"], "EffectTraceInput")
        decision = oracle.classify_effect_trace(bundle["input"])
        self.assertEqual(decision["status"], "succeeded")
        self.assertEqual(decision["reasons"], ["admission-refused", "paused"])
        schema_gate.validate(decision, "EffectDecision")

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

    def test_protected_review_ref_blocks_but_observed_remote_history_remains_published(self) -> None:
        bundle = load_fixture(11)
        bundle["input"]["intent"]["review_ref"] = "refs/heads/master"
        bundle["input"]["intent"] = schema_gate.seal(
            bundle["input"]["intent"], "intent_digest"
        )
        schema_gate.validate(bundle["input"], "PublicationAssessmentInput")
        self.assert_reason(
            oracle.assess_publication(bundle["input"]), "protected-target", "blocked"
        )

        bundle = load_fixture(11)
        bundle["input"]["intent"]["target_branch"] = "review/m1c"
        bundle["input"]["intent"] = schema_gate.seal(
            bundle["input"]["intent"], "intent_digest"
        )
        schema_gate.validate(bundle["input"], "PublicationAssessmentInput")
        self.assert_reason(
            oracle.assess_publication(bundle["input"]),
            "publication-kind-prohibited",
            "blocked",
        )

        bundle = load_fixture(15)
        receipt = bundle["input"]["receipt"]
        receipt.update(
            {
                "remote_state": "observed",
                "remote_commit_sha": bundle["input"]["intent"]["candidate_sha"],
            }
        )
        bundle["input"]["receipt"] = schema_gate.seal(receipt, "receipt_digest")
        bundle["input"]["gates"][0]["status"] = "fail"
        schema_gate.validate(bundle["input"], "PublicationAssessmentInput")
        decision = oracle.assess_publication(bundle["input"])
        self.assert_reason(decision, "gate-failed", "published")
        schema_gate.validate(decision, "PublicationDecision")

    def test_state_duplicate_command_fence_and_event_auth_require_recovery(self) -> None:
        cases = {
            "stale-fence": lambda item: item["input"]["events"][0].update({"fence_epoch": 3}),
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

    def test_event_fences_and_logical_time_are_monotonic_without_rewriting_history(self) -> None:
        bundle = load_fixture(16)
        bundle["input"]["events"][0]["fence_epoch"] = 1
        bundle["input"]["events"][0] = schema_gate.seal(
            bundle["input"]["events"][0], "event_digest"
        )
        schema_gate.validate(bundle["input"], "StateContractAssessmentInput")
        decision = oracle.assess_state_contract(bundle["input"])
        self.assertEqual(decision["status"], "eligible")

        bundle = load_fixture(16)
        first = bundle["input"]["events"][0]
        second = copy.deepcopy(first)
        second.update(
            {
                "sequence": 2,
                "event_id": "event:two",
                "command_id": "command:two",
                "idempotency_key": "idempotency:two",
                "causation_id": first["event_id"],
                "logical_time": first["logical_time"],
                "previous_event_digest": first["event_digest"],
            }
        )
        bundle["input"]["events"].append(schema_gate.seal(second, "event_digest"))
        schema_gate.validate(bundle["input"], "StateContractAssessmentInput")
        self.assert_reason(
            oracle.assess_state_contract(bundle["input"]),
            "logical-time-regression",
            "recovery-required",
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
        bundle["input"]["tombstone"]["disposed_at"] = None
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

    def test_local_content_is_independent_incomplete_proof_and_evidence_is_not_receipt(self) -> None:
        bundle = load_fixture(21)
        bundle["input"]["local_content_deleted"] = False
        bundle["input"]["tombstone"]["disposed_at"] = None
        bundle["input"]["tombstone"] = schema_gate.seal(
            bundle["input"]["tombstone"], "tombstone_digest"
        )
        schema_gate.validate(bundle["input"], "RetentionAssessmentInput")
        decision = oracle.assess_retention(bundle["input"])
        self.assert_reason(decision, "local-content-present", "incomplete")
        self.assertEqual(decision["unresolved_copy_ids"], [])
        schema_gate.validate(decision, "RetentionDecision")

        bundle = load_fixture(21)
        bundle["input"]["artifact_class"] = "accepted-evidence"
        bundle["input"]["tombstone"]["artifact_class"] = "accepted-evidence"
        bundle["input"]["tombstone"] = schema_gate.seal(
            bundle["input"]["tombstone"], "tombstone_digest"
        )
        schema_gate.validate(bundle["input"], "RetentionAssessmentInput")
        decision = oracle.assess_retention(bundle["input"])
        self.assertEqual(decision["status"], "complete")
        self.assertNotIn("owner-policy-required", decision["reasons"])

    def test_tombstone_time_and_completion_bind_to_deletion_proof(self) -> None:
        bundle = load_fixture(21)
        bundle["input"]["tombstone"]["disposed_at"] = None
        bundle["input"]["tombstone"] = schema_gate.seal(
            bundle["input"]["tombstone"], "tombstone_digest"
        )
        schema_gate.validate(bundle["input"], "RetentionAssessmentInput")
        self.assert_reason(
            oracle.assess_retention(bundle["input"]), "tombstone-mismatch", "blocked"
        )

        bundle = load_fixture(21)
        bundle["input"]["copies"][0]["expiry_boundary"] = "2026-09-05T00:00:00Z"
        bundle["input"]["tombstone"]["copy_dispositions"] = copy.deepcopy(
            bundle["input"]["copies"]
        )
        bundle["input"]["tombstone"] = schema_gate.seal(
            bundle["input"]["tombstone"], "tombstone_digest"
        )
        with self.assertRaises(jsonschema.ValidationError):
            schema_gate.validate(bundle["input"], "RetentionAssessmentInput")
        decision = oracle.assess_retention(bundle["input"])
        self.assert_reason(decision, "expiry-not-reached", "blocked")
        self.assertIn("copy:backup", decision["unresolved_copy_ids"])

        bundle = load_fixture(21)
        bundle["input"]["artifact_id"] = "artifact:other"
        with self.assertRaises(jsonschema.ValidationError):
            schema_gate.validate(bundle["input"], "RetentionAssessmentInput")
        self.assert_reason(
            oracle.assess_retention(bundle["input"]), "tombstone-mismatch", "blocked"
        )

        bundle = load_fixture(21)
        bundle["input"]["tombstone"]["disposed_at"] = "2026-09-04T11:59:00Z"
        bundle["input"]["tombstone"] = schema_gate.seal(
            bundle["input"]["tombstone"], "tombstone_digest"
        )
        schema_gate.validate(bundle["input"], "RetentionAssessmentInput")
        self.assert_reason(
            oracle.assess_retention(bundle["input"]), "tombstone-mismatch", "blocked"
        )

    def test_unreached_expiry_is_representable_and_incomplete(self) -> None:
        bundle = load_fixture(21)
        bundle["input"]["copies"][0]["expiry_reached"] = False
        bundle["input"]["tombstone"]["copy_dispositions"] = copy.deepcopy(
            bundle["input"]["copies"]
        )
        bundle["input"]["tombstone"]["disposed_at"] = None
        bundle["input"]["tombstone"] = schema_gate.seal(
            bundle["input"]["tombstone"], "tombstone_digest"
        )
        schema_gate.validate(bundle["input"], "RetentionAssessmentInput")
        decision = oracle.assess_retention(bundle["input"])
        self.assert_reason(decision, "expiry-not-reached", "incomplete")
        self.assertEqual(decision["unresolved_copy_ids"], ["copy:backup"])


if __name__ == "__main__":
    suite = unittest.TestSuite(
        (
            unittest.defaultTestLoader.loadTestsFromTestCase(M1CMutationMatrixTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(M1CSemanticAdversarialTests),
        )
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful():
        print("M1C_ADVERSARIAL_PASS structural_mutations=40 semantic_groups=20 output_variants=79")
    raise SystemExit(0 if result.wasSuccessful() else 1)
