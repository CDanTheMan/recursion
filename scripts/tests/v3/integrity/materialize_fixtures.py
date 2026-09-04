#!/usr/bin/env python3
"""Materialize the 24 closed, sanitized M1C integrity fixtures."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIXTURES = HERE / "fixtures"
SCHEMA_PATH = ROOT / "schemas" / "control-plane" / "v3" / "integrity" / "schema.json"
D1 = "sha256:" + "1" * 64
D2 = "sha256:" + "2" * 64
D3 = "sha256:" + "3" * 64
D4 = "sha256:" + "4" * 64
SHA1 = "a" * 40
SHA2 = "b" * 40
T0 = "2026-09-04T12:00:00Z"
T1 = "2026-09-04T12:01:00Z"
T2 = "2026-09-04T12:02:00Z"
T3 = "2026-09-04T12:03:00Z"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def seal(value: dict[str, Any], field: str) -> dict[str, Any]:
    value[field] = digest_bytes(canonical_bytes({key: item for key, item in value.items() if key != field}))
    return value


def rendered(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def fixture(tag: str, number: int, purpose: str, requirements: list[str], input_value: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": tag, "fixture_id": f"F-M1C-{number:03d}", "purpose": purpose,
        "source_requirement_ids": sorted(requirements), "input": input_value, "expected": expected,
    }


def source(
    source_id: str,
    *,
    lifecycle: str = "verified",
    editorial: str = "current",
    access: str = "accessible",
    license_state: str = "permitted",
    privacy: str = "public",
    scopes: list[str] | None = None,
) -> dict[str, Any]:
    metadata_only = access == "metadata-only"
    retrieved = lifecycle in {"retrieved", "verified"}
    return {
        "type": "SourceRecord@1", "source_id": source_id,
        "canonical_uri": f"https://example.invalid/{source_id}",
        "persistent_identifiers": [{
            "type": "PersistentIdentifier@1", "scheme": "doi", "value": f"10.0000/{source_id}",
            "verification_state": "verified" if lifecycle == "verified" else "unverified",
            "verification_evidence_digest": D1 if lifecycle == "verified" else None,
        }],
        "title_digest": D1, "creator_digests": [D2], "publisher_digest": D3,
        "source_class": "paper", "primary_status": "primary",
        "supported_scopes": sorted(scopes or ["external-mechanism"]),
        "lifecycle": lifecycle, "editorial_state": editorial, "access_state": access,
        "license_state": license_state, "privacy_class": privacy, "version": "v1",
        "published_at": "2026-09-01T00:00:00Z", "retrieved_at": T0 if retrieved else None,
        "adapter_ref": "adapter:synthetic", "adapter_revision": "v1",
        "request_digest": D1 if retrieved else None,
        "content_digest": D2 if retrieved and not metadata_only else None,
        "representation_size": 100 if retrieved and not metadata_only else None,
        "verification_evidence_digest": D3 if retrieved else None,
        "related_source_ids": [], "revalidate_after": "2026-10-01T00:00:00Z",
    }


def claim(required_sources: list[str], *, intended_use: str = "internal", scope: str = "external-mechanism") -> dict[str, Any]:
    return {
        "type": "ResearchClaim@1", "claim_id": "claim:one", "goal_spec_id": "goal:m1c",
        "goal_spec_digest": D1, "proposition_digest": D2, "claim_kind": "fact",
        "evidence_scope": scope, "intended_use": intended_use,
        "required_source_ids": sorted(required_sources), "assumption_digests": [],
        "definition_digests": [], "revalidate_after": "2026-10-01T00:00:00Z",
    }


def edge(edge_id: str, source_id: str, relation: str = "supports", *, applicability: str = "exact", verified: bool = True) -> dict[str, Any]:
    return {
        "type": "EvidenceEdge@1", "edge_id": edge_id, "claim_id": "claim:one",
        "source_id": source_id, "relation": relation, "locator": "section:one",
        "extraction_digest": D3, "source_version": "v1", "applicability": applicability,
        "extraction_verified": verified,
    }


def evidence_input(sources: list[dict[str, Any]], edges: list[dict[str, Any]], *, intended_use: str = "internal", public_export: bool = False) -> dict[str, Any]:
    source_ids = [item["source_id"] for item in sources]
    return {
        "type": "EvidenceAssessmentInput@1", "observed_at": T0,
        "claim": claim(source_ids, intended_use=intended_use),
        "sources": sorted(sources, key=lambda item: item["source_id"]),
        "edges": sorted(edges, key=lambda item: item["edge_id"]),
        "allowed_privacy_classes": ["public"], "allowed_license_states": ["permitted"],
        "public_export_authorized": public_export,
    }


def evidence_decision(status: str, reasons: list[str], *, accepted: list[str] | None = None, contradictions: list[str] | None = None, qualifications: list[str] | None = None, rejected: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "EvidenceDecision@1", "status": status, "reasons": sorted(reasons),
        "accepted_edge_ids": sorted(accepted or []), "contradiction_edge_ids": sorted(contradictions or []),
        "qualification_edge_ids": sorted(qualifications or []), "rejected_source_ids": sorted(rejected or []),
    }


def evidence_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    value = evidence_input([source("source:one")], [edge("edge:support", "source:one")])
    rows.append(fixture("EvidenceFixtureBundle@1", 1, "Admit exact current verified primary support for its scoped claim.", ["REQ-M1C-EVIDENCE"], value, evidence_decision("supported", [], accepted=["edge:support"])))

    value = evidence_input([source("source:metadata", lifecycle="identified", access="metadata-only")], [edge("edge:metadata", "source:metadata", "metadata-only")])
    rows.append(fixture("EvidenceFixtureBundle@1", 2, "Metadata-only discovery cannot support a claim.", ["REQ-M1C-EVIDENCE"], value, evidence_decision("unknown", ["metadata-only", "support-insufficient"], rejected=["source:metadata"])))

    value = evidence_input([source("source:retracted", editorial="retracted")], [edge("edge:retracted", "source:retracted")])
    rows.append(fixture("EvidenceFixtureBundle@1", 3, "Retracted material cannot be current support.", ["REQ-M1C-EVIDENCE"], value, evidence_decision("unknown", ["source-retracted", "support-insufficient"], rejected=["source:retracted"])))

    sources = [source("source:contradiction"), source("source:support")]
    edges = [edge("edge:contradiction", "source:contradiction", "contradicts"), edge("edge:support", "source:support")]
    value = evidence_input(sources, edges)
    rows.append(fixture("EvidenceFixtureBundle@1", 4, "Retain applicable verified support and contradiction together.", ["REQ-M1C-CONTRADICTION", "REQ-M1C-EVIDENCE"], value, evidence_decision("contested", ["contradiction-present"], accepted=["edge:support"], contradictions=["edge:contradiction"])))

    private_source = source("source:private", license_state="restricted", privacy="private")
    value = evidence_input([private_source], [edge("edge:private", "source:private")], intended_use="public", public_export=False)
    rows.append(fixture("EvidenceFixtureBundle@1", 5, "Refuse public export of private license-restricted evidence.", ["REQ-M1C-EVIDENCE", "REQ-M1C-PRIVACY"], value, evidence_decision("refused", ["export-prohibited", "license-prohibited", "privacy-prohibited"], rejected=["source:private"])))
    return rows


def effect_intent(effect_id: str = "effect:one") -> dict[str, Any]:
    return seal({
        "type": "EffectIntent@1", "effect_id": effect_id, "command_id": "command:one",
        "idempotency_key": "idempotency:one", "intent_digest": D1,
        "effect_class": "external-idempotent", "target_ref": "target:synthetic", "payload_digest": D2,
        "goal_spec_id": "goal:m1c", "goal_spec_digest": D1, "policy_digest": D1,
        "grant_digest": D1, "privacy_digest": D1, "route_digest": D1, "budget_digest": D1,
        "plan_digest": D1, "actor_id": "actor:one", "lease_id": "lease:one",
        "admission_epoch": 2, "fence_epoch": 3, "deadline": "2026-09-05T00:00:00Z",
        "dependency_effect_ids": [], "reversible": False, "compensation_effect_id": None,
    }, "intent_digest")


def admission(intent: dict[str, Any], *, admitted: bool = True, paused: bool = False) -> dict[str, Any]:
    reasons = [] if admitted else sorted(["paused", "stale-admission"] if paused else ["admission-refused"])
    return {
        "type": "EffectAdmission@1", "admission_id": "admission:one", "effect_id": intent["effect_id"],
        "intent_digest": intent["intent_digest"], "decision": "admitted" if admitted else "refused",
        "actor_id": intent["actor_id"], "lease_id": intent["lease_id"],
        "admission_epoch": intent["admission_epoch"], "fence_epoch": intent["fence_epoch"],
        "goal_spec_digest": intent["goal_spec_digest"], "policy_digest": intent["policy_digest"],
        "grant_digest": intent["grant_digest"], "privacy_digest": intent["privacy_digest"],
        "route_digest": intent["route_digest"], "budget_digest": intent["budget_digest"],
        "pause_profile": "current-immediate", "pause_state": "paused" if paused else "running",
        "admitted_at": T0, "reasons": reasons,
    }


def attempt(intent: dict[str, Any], number: int, when: str) -> dict[str, Any]:
    return {
        "type": "AttemptStarted@1", "effect_id": intent["effect_id"], "attempt_id": f"attempt:{number}",
        "attempt_number": number, "idempotency_key": intent["idempotency_key"],
        "target_ref": intent["target_ref"], "payload_digest": intent["payload_digest"],
        "admission_epoch": intent["admission_epoch"], "fence_epoch": intent["fence_epoch"],
        "observed_at": when,
    }


def external(intent: dict[str, Any], outcome: str, when: str) -> dict[str, Any]:
    return {
        "type": "ExternalObserved@1", "effect_id": intent["effect_id"], "attempt_id": "attempt:1",
        "attempt_number": 1, "idempotency_key": intent["idempotency_key"],
        "target_ref": intent["target_ref"], "payload_digest": intent["payload_digest"],
        "admission_epoch": intent["admission_epoch"], "fence_epoch": intent["fence_epoch"],
        "observed_at": when, "observation_id": "observation:one", "observer_ref": "observer:synthetic",
        "authenticity": "verified", "outcome": outcome,
        "remote_operation_ref": "remote:one", "result_digest": D3 if outcome != "unknown" else None,
    }


def receipt(intent: dict[str, Any], when: str) -> dict[str, Any]:
    return {
        "type": "ReceiptRecorded@1", "effect_id": intent["effect_id"], "attempt_id": "attempt:1",
        "attempt_number": 1, "idempotency_key": intent["idempotency_key"],
        "target_ref": intent["target_ref"], "payload_digest": intent["payload_digest"],
        "admission_epoch": intent["admission_epoch"], "fence_epoch": intent["fence_epoch"],
        "observed_at": when, "receipt_id": "receipt:one", "observer_ref": "observer:synthetic",
        "authenticity": "verified", "result": "succeeded", "result_digest": D3,
        "remote_operation_ref": "remote:one",
    }


def effect_input(observations: list[dict[str, Any]], *, admitted: bool = True, paused: bool = False, current_admission_epoch: int = 2) -> dict[str, Any]:
    intent = effect_intent()
    return {
        "type": "EffectTraceInput@1", "intent": intent,
        "admission": admission(intent, admitted=admitted, paused=paused),
        "observations": observations, "dependency_states": [],
        "current_admission_epoch": current_admission_epoch, "current_fence_epoch": 3,
        "effect_count": 0, "external_call_count": 0,
    }


def effect_decision(status: str, reasons: list[str], final_attempt: int, reconcile: bool) -> dict[str, Any]:
    return {
        "type": "EffectDecision@1", "status": status, "reasons": sorted(reasons),
        "final_attempt_number": final_attempt, "requires_reconciliation": reconcile,
        "effect_count": 0, "external_call_count": 0,
    }


def effect_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    value = effect_input([])
    rows.append(fixture("EffectFixtureBundle@1", 6, "Admitted intent without an attempt remains prepared.", ["REQ-M1C-EFFECT"], value, effect_decision("prepared", [], 0, False)))

    intent = effect_intent()
    observations = [attempt(intent, 1, T0), external(intent, "accepted", T1), receipt(intent, T2)]
    value = effect_input(observations)
    rows.append(fixture("EffectFixtureBundle@1", 7, "Matching authenticated acceptance and receipt complete one effect.", ["REQ-M1C-EFFECT"], value, effect_decision("succeeded", [], 1, False)))

    observations = [attempt(intent, 1, T0), external(intent, "accepted", T1)]
    value = effect_input(observations)
    rows.append(fixture("EffectFixtureBundle@1", 8, "Possible acceptance without a receipt is ambiguous.", ["REQ-M1C-AMBIGUITY", "REQ-M1C-EFFECT"], value, effect_decision("ambiguous", ["receipt-missing", "reconciliation-required"], 1, True)))

    observations = [attempt(intent, 1, T0), external(intent, "accepted", T1), attempt(intent, 2, T2)]
    value = effect_input(observations)
    rows.append(fixture("EffectFixtureBundle@1", 9, "Fence a blind second attempt while the first is ambiguous.", ["REQ-M1C-AMBIGUITY", "REQ-M1C-EFFECT"], value, effect_decision("ambiguous", ["blind-retry-blocked", "receipt-missing", "reconciliation-required"], 2, True)))

    value = effect_input([], admitted=False, paused=True, current_admission_epoch=3)
    rows.append(fixture("EffectFixtureBundle@1", 10, "Current immediate PAUSE and stale admission refuse before attempt.", ["REQ-M1C-EFFECT", "REQ-M1C-PAUSE"], value, effect_decision("refused", ["admission-refused", "paused", "stale-admission"], 0, False)))
    return rows


def publication_intent(*, kind: str = "review-branch") -> dict[str, Any]:
    return seal({
        "type": "PublicationIntent@1", "publication_id": "publication:one", "effect_id": "effect:publication",
        "intent_digest": D1, "publication_kind": kind, "repository_ref": "repository:synthetic",
        "source_sha": SHA1, "candidate_sha": SHA2, "review_ref": "refs/heads/review/m1c",
        "target_branch": "master", "protected_branch_names": ["master"], "goal_spec_id": "goal:m1c",
        "goal_spec_digest": D1, "policy_digest": D1, "grant_digest": D1, "privacy_digest": D1,
        "candidate_tree_digest": D1, "required_gate_ids": ["gate:one"],
        "required_verifier_ids": ["verifier:one"], "artifact_ids": ["artifact:one"],
    }, "intent_digest")


def publication_input(*, kind: str = "review-branch") -> dict[str, Any]:
    intent = publication_intent(kind=kind)
    return {
        "type": "PublicationAssessmentInput@1", "intent": intent,
        "artifacts": [{"type": "PublicationArtifact@1", "artifact_id": "artifact:one", "content_digest": D1, "classification": "public", "license_state": "permitted", "redaction_state": "not-required", "secret_scan": "pass", "export_authorized": True}],
        "gates": [{"type": "GateEvidence@1", "gate_id": "gate:one", "source_sha": SHA1, "candidate_sha": SHA2, "status": "pass", "evidence_digest": D1, "observed_at": T0}],
        "verifiers": [{"type": "VerifierEvidence@1", "verifier_id": "verifier:one", "source_sha": SHA1, "candidate_sha": SHA2, "status": "pass", "independence": "full", "policy_sufficient": True, "evidence_digest": D2, "observed_at": T0}],
        "source_ancestry": "known-ancestor", "candidate_tree": "clean",
        "publication_authority": "granted", "required_independence": "full",
        "receipt": None, "git_mutation_count": 0,
    }


def publication_receipt(intent: dict[str, Any], remote_state: str) -> dict[str, Any]:
    return seal({
        "type": "PublicationReceipt@1", "receipt_id": "receipt:publication",
        "publication_id": intent["publication_id"], "effect_id": intent["effect_id"],
        "repository_ref": intent["repository_ref"], "review_ref": intent["review_ref"],
        "candidate_sha": intent["candidate_sha"], "publisher_ref": "publisher:synthetic",
        "remote_state": remote_state, "remote_commit_sha": intent["candidate_sha"] if remote_state == "observed" else None,
        "observed_at": T1, "receipt_digest": D1,
    }, "receipt_digest")


def publication_decision(status: str, reasons: list[str], *, published_sha: str | None = None, reconcile: bool = False) -> dict[str, Any]:
    return {
        "type": "PublicationDecision@1", "status": status, "reasons": sorted(reasons),
        "publication_id": "publication:one", "published_sha": published_sha,
        "requires_reconciliation": reconcile, "git_mutation_count": 0,
    }


def publication_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    value = publication_input()
    rows.append(fixture("PublicationFixtureBundle@1", 11, "Exact clean review candidate with complete evidence is eligible.", ["REQ-M1C-PUBLICATION"], value, publication_decision("eligible", [])))

    value = publication_input(kind="merge")
    rows.append(fixture("PublicationFixtureBundle@1", 12, "Merge to a protected default target is prohibited.", ["REQ-M1C-PUBLICATION", "REQ-M1C-PROTECTED-BRANCH"], value, publication_decision("blocked", ["protected-target", "publication-kind-prohibited"])))

    value = publication_input()
    value["artifacts"][0].update({"classification": "private", "redaction_state": "missing", "secret_scan": "fail", "export_authorized": False})
    rows.append(fixture("PublicationFixtureBundle@1", 13, "Private unredacted secret-bearing artifact blocks public publication.", ["REQ-M1C-PRIVACY", "REQ-M1C-PUBLICATION"], value, publication_decision("blocked", ["artifact-export-prohibited", "secret-scan-failed"])))

    value = publication_input()
    value["verifiers"][0].update({"status": "unavailable", "policy_sufficient": False})
    rows.append(fixture("PublicationFixtureBundle@1", 14, "Unavailable policy-insufficient verification cannot become pass.", ["REQ-M1C-PUBLICATION", "REQ-M1C-VERIFICATION"], value, publication_decision("blocked", ["verification-insufficient"])))

    value = publication_input()
    value["receipt"] = publication_receipt(value["intent"], "unknown")
    rows.append(fixture("PublicationFixtureBundle@1", 15, "Unknown remote ref state after possible push requires reconciliation.", ["REQ-M1C-AMBIGUITY", "REQ-M1C-PUBLICATION"], value, publication_decision("ambiguous", ["remote-state-unknown"], reconcile=True)))
    return rows


def canonical_event(sequence: int, *, previous: str | None = None) -> dict[str, Any]:
    return seal({
        "type": "CanonicalEvent@1", "aggregate_id": "aggregate:fabric", "sequence": sequence,
        "event_id": f"event:{sequence}", "command_id": f"command:{sequence}",
        "idempotency_key": f"idempotency:{sequence}", "causation_id": "event:genesis" if sequence == 1 else f"event:{sequence - 1}",
        "correlation_id": "correlation:one", "writer_id": "writer:canonical", "fence_epoch": 2,
        "logical_time": sequence, "schema_version": "v1", "previous_event_digest": previous,
        "payload_digest": D1, "event_digest": D2, "authentication_state": "verified",
    }, "event_digest")


def state_input() -> dict[str, Any]:
    first = canonical_event(1)
    return {
        "type": "StateContractAssessmentInput@1", "migration_id": "migration:one",
        "aggregate_type": "fabric-only", "aggregate_id": "aggregate:fabric", "source_revision": SHA1,
        "source_state_digest": D1, "immutable_assignment_digest": D2,
        "expected_writer_ids": ["writer:canonical"],
        "observed_writers": [{"type": "WriterRecord@1", "writer_id": "writer:canonical", "mutation_path_digest": D1, "observation_state": "known", "can_refuse": True, "configured_fence_epoch": 2, "source_revision": SHA1}],
        "canonical_writer_id": "writer:canonical", "current_fence_epoch": 2, "events": [first],
        "import_state": "lossless", "expected_replay_digest": D1, "actual_replay_digest": D1,
        "expected_projection_digest": D2, "actual_projection_digest": D2,
        "writer_refusal": "verified", "backup": "verified", "restore": "verified",
        "reverse_reader": "verified", "rollback": "verified",
        "completed_stages": ["snapshotted", "validated", "legacy-writers-quiesced", "fence-established", "imported", "replayed", "shadow-read-verified", "v3-owner-active", "checkpointed"],
        "open_work": [], "deployment_revision_state": "known", "state_write_count": 0,
    }


def state_decision(status: str, reasons: list[str], final_sequence: int) -> dict[str, Any]:
    return {
        "type": "StateDecision@1", "status": status, "reasons": sorted(reasons),
        "aggregate_id": "aggregate:fabric", "final_sequence": final_sequence,
        "current_fence_epoch": 2, "state_write_count": 0,
    }


def state_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    value = state_input()
    rows.append(fixture("StateFixtureBundle@1", 16, "Complete synthetic fabric-only state evidence is eligible.", ["REQ-M1C-SINGLE-WRITER", "REQ-M1C-STATE"], value, state_decision("eligible", [], 1)))

    value = state_input()
    value["observed_writers"].append({"type": "WriterRecord@1", "writer_id": "writer:unexpected", "mutation_path_digest": D2, "observation_state": "unknown", "can_refuse": True, "configured_fence_epoch": 2, "source_revision": SHA1})
    rows.append(fixture("StateFixtureBundle@1", 17, "Unknown extra writer prevents a complete fence inventory.", ["REQ-M1C-SINGLE-WRITER", "REQ-M1C-STATE"], value, state_decision("blocked", ["writer-inventory-incomplete", "writer-unknown"], 1)))

    value = state_input()
    value["events"].append(canonical_event(3, previous=D4))
    value["actual_replay_digest"] = D3
    rows.append(fixture("StateFixtureBundle@1", 18, "Sequence and digest discontinuity with replay mismatch requires recovery.", ["REQ-M1C-REPLAY", "REQ-M1C-STATE"], value, state_decision("recovery-required", ["digest-chain-invalid", "replay-mismatch", "sequence-gap"], 3)))

    value = state_input()
    value["open_work"] = [
        {"type": "OpenWork@1", "work_id": "work:effect", "kind": "effect", "state": "ambiguous"},
        {"type": "OpenWork@1", "work_id": "work:lease", "kind": "lease", "state": "active"},
        {"type": "OpenWork@1", "work_id": "work:publication", "kind": "publication", "state": "pending"},
        {"type": "OpenWork@1", "work_id": "work:saga", "kind": "saga", "state": "partial"},
    ]
    rows.append(fixture("StateFixtureBundle@1", 19, "Open lease effect publication and saga block ownership transfer.", ["REQ-M1C-EFFECT", "REQ-M1C-STATE"], value, state_decision("blocked", ["open-effect", "open-lease", "pending-publication", "saga-incomplete"], 1)))

    value = state_input()
    value.update({"backup": "unknown", "restore": "unknown", "reverse_reader": "unknown", "rollback": "unknown"})
    value["completed_stages"] = value["completed_stages"][:7]
    rows.append(fixture("StateFixtureBundle@1", 20, "Projection equality without recovery and rollback proof is insufficient.", ["REQ-M1C-MIGRATION", "REQ-M1C-STATE"], value, state_decision("blocked", ["backup-unverified", "projection-only", "restore-unverified", "reverse-reader-unverified", "rollback-unproved"], 1)))
    return rows


def copy_disposition(copy_id: str, kind: str, state: str, *, evidence_state: str = "verified") -> dict[str, Any]:
    expiry = state == "expiry-bound"
    return {
        "type": "CopyDisposition@1", "copy_id": copy_id, "kind": kind, "state": state,
        "evidence_state": evidence_state, "evidence_digest": D1 if evidence_state == "verified" else None,
        "expiry_boundary": "2026-09-01T00:00:00Z" if expiry else None,
        "expiry_reached": expiry,
    }


def retention_input(*, artifact_class: str = "raw-session", owner_policy: str = "not-required", copies: list[dict[str, Any]] | None = None, key_state: str = "destroyed", key_scope: str = "artifact", sensitive_tombstone: bool = False) -> dict[str, Any]:
    copies = sorted(copies or [copy_disposition("copy:backup", "backup", "expiry-bound"), copy_disposition("copy:local", "local", "deleted")], key=lambda item: item["copy_id"])
    tombstone = seal({
        "type": "DeletionTombstone@1", "tombstone_id": "tombstone:one",
        "artifact_class": artifact_class, "policy_digest": D1,
        "responsible_component": "component:retention", "requested_at": T0,
        "disposed_at": T1, "copy_dispositions": copy.deepcopy(copies),
        "contains_content": False, "contains_secret": False,
        "contains_global_content_digest": sensitive_tombstone, "tombstone_digest": D2,
    }, "tombstone_digest")
    return {
        "type": "RetentionAssessmentInput@1", "artifact_id": "artifact:one",
        "artifact_class": artifact_class, "privacy_class": "private", "policy_digest": D1,
        "owner_erasure_policy": owner_policy, "legal_hold": False, "local_content_deleted": True,
        "key_state": key_state, "key_scope": key_scope, "copies": copies,
        "tombstone": tombstone, "deletion_operation_count": 0,
    }


def retention_decision(status: str, reasons: list[str], resolved: list[str], unresolved: list[str]) -> dict[str, Any]:
    return {
        "type": "RetentionDecision@1", "status": status, "reasons": sorted(reasons),
        "artifact_id": "artifact:one", "resolved_copy_ids": sorted(resolved),
        "unresolved_copy_ids": sorted(unresolved), "deletion_operation_count": 0,
    }


def retention_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    value = retention_input()
    rows.append(fixture("RetentionFixtureBundle@1", 21, "Scoped key plus complete copy evidence and minimal tombstone complete deletion proof.", ["REQ-M1C-RETENTION"], value, retention_decision("complete", [], ["copy:backup", "copy:local"], [])))

    copies = [copy_disposition("copy:local", "local", "deleted"), copy_disposition("copy:spool", "disconnected-spool", "disconnected", evidence_state="unverified")]
    value = retention_input(copies=copies)
    value["tombstone"]["disposed_at"] = None
    value["tombstone"] = seal(value["tombstone"], "tombstone_digest")
    rows.append(fixture("RetentionFixtureBundle@1", 22, "Disconnected unresolved copy keeps deletion incomplete.", ["REQ-M1C-RETENTION"], value, retention_decision("incomplete", ["copy-evidence-unverified", "copy-unresolved"], ["copy:local"], ["copy:spool"])))

    copies = [copy_disposition("copy:local", "local", "deleted")]
    value = retention_input(copies=copies, key_state="shared", key_scope="shared", sensitive_tombstone=True)
    rows.append(fixture("RetentionFixtureBundle@1", 23, "Shared key and equality-revealing tombstone invalidate completion.", ["REQ-M1C-RETENTION", "REQ-M1C-SECURITY"], value, retention_decision("blocked", ["key-not-destroyed", "key-not-isolated", "tombstone-sensitive"], ["copy:local"], [])))

    value = retention_input(artifact_class="authority-receipt", owner_policy="unknown", copies=[copy_disposition("copy:local", "local", "deleted")])
    rows.append(fixture("RetentionFixtureBundle@1", 24, "Unresolved Owner policy blocks authority-receipt erasure.", ["REQ-M1C-OWNER-SEAM", "REQ-M1C-RETENTION"], value, retention_decision("blocked", ["owner-policy-required"], ["copy:local"], [])))
    return rows


def build_fixtures() -> list[dict[str, Any]]:
    values = evidence_fixtures() + effect_fixtures() + publication_fixtures() + state_fixtures() + retention_fixtures()
    assert [item["fixture_id"] for item in values] == [f"F-M1C-{number:03d}" for number in range(1, 25)]
    return values


def build_outputs() -> dict[Path, bytes]:
    fixtures = build_fixtures()
    outputs = {FIXTURES / f"{item['fixture_id']}.json": rendered(item) for item in fixtures}
    entries = []
    for item in fixtures:
        path = FIXTURES / f"{item['fixture_id']}.json"
        entries.append({
            "type": "FixtureManifestEntry@1", "fixture_id": item["fixture_id"], "path": path.name,
            "digest": digest_bytes(outputs[path]), "bundle_type": item["type"],
        })
    manifest = {"type": "FixtureManifest@1", "schema_digest": digest_bytes(SCHEMA_PATH.read_bytes()), "fixtures": entries}
    outputs[FIXTURES / "manifest.json"] = rendered(manifest)
    return outputs


def write() -> int:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    expected = build_outputs()
    for path, data in expected.items():
        path.write_bytes(data)
    for existing in FIXTURES.glob("F-M1C-*.json"):
        if existing not in expected:
            existing.unlink()
    print(f"M1C_FIXTURES_MATERIALIZED count={len(expected) - 1}")
    return 0


def check() -> int:
    expected = build_outputs()
    mismatches = [str(path) for path, data in expected.items() if not path.exists() or path.read_bytes() != data]
    extras = [str(path) for path in FIXTURES.glob("F-M1C-*.json") if path not in expected]
    if mismatches or extras:
        for path in sorted(mismatches + extras):
            print(path, file=sys.stderr)
        print("M1C_FIXTURE_MATERIALIZATION_MISMATCH", file=sys.stderr)
        return 1
    print(f"M1C_FIXTURE_MATERIALIZATION_PASS count={len(expected) - 1}")
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--write"]:
        return write()
    if argv == ["--check"]:
        return check()
    print("usage: materialize_fixtures.py --write | --check", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
