#!/usr/bin/env python3
"""Materialize the closed Recursion v3 M1C integrity-contract schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "schema.json"
SCHEMA_ID = "https://recursion.local/schemas/control-plane/v3/integrity/schema.json"


def ref(name: str) -> dict[str, str]:
    return {"$ref": f"#/$defs/{name}"}


def nullable(schema: dict[str, Any]) -> dict[str, Any]:
    return {"anyOf": [schema, {"type": "null"}]}


def obj(properties: dict[str, Any], *, required: list[str] | None = None, **extra: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required if required is not None else list(properties),
    }
    value.update(extra)
    return value


def tagged(tag: str, properties: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return obj({"type": {"const": tag}, **properties}, **extra)


def scalar_set(item: dict[str, Any], *, minimum: int = 0, maximum: int = 128) -> dict[str, Any]:
    return {
        "type": "array", "items": item, "minItems": minimum, "maxItems": maximum,
        "uniqueItems": True, "x-strictlySorted": True,
    }


def keyed_set(name: str, *, key: str, minimum: int = 0, maximum: int = 128) -> dict[str, Any]:
    return {
        "type": "array", "items": ref(name), "minItems": minimum, "maxItems": maximum,
        "x-strictlySortedBy": key, "x-uniqueBy": key,
    }


def ordered(name: str, *, minimum: int = 0, maximum: int = 128) -> dict[str, Any]:
    return {"type": "array", "items": ref(name), "minItems": minimum, "maxItems": maximum}


def build_schema() -> dict[str, Any]:
    defs: dict[str, Any] = {}

    defs["EntityId"] = {
        "type": "string", "pattern": r"^[a-z][a-z0-9-]{1,31}:[A-Za-z0-9._~-]{1,128}$",
        "minLength": 3, "maxLength": 160, "x-utf8MaxBytes": 160,
    }
    defs["OpaqueRef"] = {
        "type": "string", "pattern": r"^[\x21-\x7e]{1,192}$",
        "minLength": 1, "maxLength": 192, "x-utf8MaxBytes": 192,
    }
    defs["Digest"] = {"type": "string", "pattern": r"^sha256:[0-9a-f]{64}$"}
    defs["GitSha"] = {"type": "string", "pattern": r"^[0-9a-f]{40}$"}
    defs["Timestamp"] = {
        "type": "string", "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        "x-rfc3339Utc": True,
    }
    defs["Count"] = {"type": "integer", "minimum": 0, "maximum": 1000000}
    defs["PositiveCount"] = {"type": "integer", "minimum": 1, "maximum": 1000000}
    defs["Epoch"] = ref("PositiveCount")
    defs["Token"] = {
        "type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$",
        "minLength": 1, "maxLength": 96, "x-utf8MaxBytes": 96,
    }
    defs["Text"] = {"type": "string", "minLength": 1, "maxLength": 512, "x-utf8MaxBytes": 512}
    defs["CanonicalUri"] = {
        "type": "string", "pattern": r"^(?:https://|urn:|recursion:)[^\s#]+$",
        "minLength": 1, "maxLength": 512, "x-utf8MaxBytes": 512, "x-canonicalUri": True,
    }
    defs["RequirementId"] = {
        "type": "string", "pattern": r"^[A-Z][A-Z0-9-]{2,95}$", "maxLength": 96,
    }
    defs["EntityIdSet"] = scalar_set(ref("EntityId"))
    defs["NonEmptyEntityIdSet"] = scalar_set(ref("EntityId"), minimum=1)
    defs["DigestSet"] = scalar_set(ref("Digest"))
    defs["NonEmptyDigestSet"] = scalar_set(ref("Digest"), minimum=1)
    defs["RequirementIdSet"] = scalar_set(ref("RequirementId"), minimum=1)
    defs["PrivacyClass"] = {"enum": ["public", "internal", "private", "restricted"]}
    defs["PrivacyClassSet"] = scalar_set(ref("PrivacyClass"), minimum=1)
    defs["LicenseState"] = {"enum": ["permitted", "restricted", "prohibited", "unknown"]}
    defs["LicenseStateSet"] = scalar_set(ref("LicenseState"), minimum=1)
    defs["EvidenceScope"] = {"enum": ["external-mechanism", "local-structural", "empirical-fit"]}
    defs["EvidenceScopeSet"] = scalar_set(ref("EvidenceScope"), minimum=1)

    defs["PersistentIdentifier"] = tagged(
        "PersistentIdentifier@1",
        {
            "scheme": {"enum": ["doi", "arxiv", "isbn", "rfc", "repo-commit", "dataset-doi", "other"]},
            "value": ref("OpaqueRef"),
            "verification_state": {"enum": ["verified", "unverified", "mismatch"]},
            "verification_evidence_digest": nullable(ref("Digest")),
        },
        allOf=[{
            "if": {"properties": {"verification_state": {"const": "verified"}}, "required": ["verification_state"]},
            "then": {"properties": {"verification_evidence_digest": ref("Digest")}},
        }],
    )
    persistent_identifiers = ordered("PersistentIdentifier", minimum=1, maximum=16)
    persistent_identifiers["x-strictlySortedByFields"] = ["scheme", "value"]
    persistent_identifiers["x-uniqueByFields"] = ["scheme", "value"]
    defs["SourceRecord"] = tagged(
        "SourceRecord@1",
        {
            "source_id": ref("EntityId"), "canonical_uri": ref("CanonicalUri"),
            "persistent_identifiers": persistent_identifiers,
            "title_digest": ref("Digest"), "creator_digests": scalar_set(ref("Digest"), minimum=1, maximum=64),
            "publisher_digest": nullable(ref("Digest")),
            "source_class": {"enum": ["paper", "standard", "dataset", "repository", "official-documentation", "web-secondary", "experiment"]},
            "primary_status": {"enum": ["primary", "secondary"]},
            "supported_scopes": ref("EvidenceScopeSet"),
            "lifecycle": {"enum": ["discovered", "identified", "retrieved", "verified", "quarantined", "expired"]},
            "editorial_state": {"enum": ["current", "corrected", "superseded", "retracted", "withdrawn", "unknown"]},
            "access_state": {"enum": ["accessible", "inaccessible", "metadata-only", "unknown"]},
            "license_state": ref("LicenseState"), "privacy_class": ref("PrivacyClass"),
            "version": ref("Token"), "published_at": nullable(ref("Timestamp")),
            "retrieved_at": nullable(ref("Timestamp")), "adapter_ref": ref("OpaqueRef"),
            "adapter_revision": ref("Token"), "request_digest": nullable(ref("Digest")),
            "content_digest": nullable(ref("Digest")), "representation_size": nullable(ref("Count")),
            "verification_evidence_digest": nullable(ref("Digest")),
            "related_source_ids": ref("EntityIdSet"), "revalidate_after": nullable(ref("Timestamp")),
        },
        allOf=[
            {
                "if": {"properties": {"lifecycle": {"enum": ["retrieved", "verified"]}}, "required": ["lifecycle"]},
                "then": {"properties": {
                    "retrieved_at": ref("Timestamp"), "request_digest": ref("Digest"),
                    "content_digest": ref("Digest"), "representation_size": ref("Count"),
                    "verification_evidence_digest": ref("Digest"),
                }},
            },
            {
                "if": {"properties": {"access_state": {"const": "metadata-only"}}, "required": ["access_state"]},
                "then": {"properties": {"content_digest": {"type": "null"}, "representation_size": {"type": "null"}}},
            },
        ],
        **{"x-sourceInvariant": True},
    )
    defs["ResearchClaim"] = tagged(
        "ResearchClaim@1",
        {
            "claim_id": ref("EntityId"), "goal_spec_id": ref("EntityId"), "goal_spec_digest": ref("Digest"),
            "proposition_digest": ref("Digest"),
            "claim_kind": {"enum": ["fact", "inference", "hypothesis", "proposal", "owner-direction"]},
            "evidence_scope": ref("EvidenceScope"), "intended_use": {"enum": ["internal", "public"]},
            "required_source_ids": scalar_set(ref("EntityId"), minimum=1, maximum=64),
            "assumption_digests": scalar_set(ref("Digest"), maximum=64),
            "definition_digests": scalar_set(ref("Digest"), maximum=64),
            "revalidate_after": nullable(ref("Timestamp")),
        },
    )
    defs["EvidenceEdge"] = tagged(
        "EvidenceEdge@1",
        {
            "edge_id": ref("EntityId"), "claim_id": ref("EntityId"), "source_id": ref("EntityId"),
            "relation": {"enum": ["supports", "contradicts", "qualifies", "replicates", "updates", "mentions", "metadata-only", "inapplicable"]},
            "locator": ref("OpaqueRef"), "extraction_digest": ref("Digest"), "source_version": ref("Token"),
            "applicability": {"enum": ["exact", "partial", "inapplicable", "unknown"]},
            "extraction_verified": {"type": "boolean"},
        },
    )
    defs["EvidenceAssessmentInput"] = tagged(
        "EvidenceAssessmentInput@1",
        {
            "observed_at": ref("Timestamp"), "claim": ref("ResearchClaim"),
            "sources": keyed_set("SourceRecord", key="source_id", minimum=1),
            "edges": keyed_set("EvidenceEdge", key="edge_id", minimum=1),
            "allowed_privacy_classes": ref("PrivacyClassSet"),
            "allowed_license_states": ref("LicenseStateSet"),
            "public_export_authorized": {"type": "boolean"},
        },
        **{"x-evidenceBindings": True},
    )
    evidence_reasons = [
        "claim-binding-mismatch", "contradiction-present", "edge-binding-mismatch",
        "export-prohibited", "extraction-unverified", "license-prohibited", "metadata-only",
        "privacy-prohibited", "qualification-present", "scope-inapplicable", "source-inaccessible",
        "source-missing", "source-retracted", "source-stale", "source-superseded",
        "source-unverified", "support-insufficient",
    ]
    defs["EvidenceReason"] = {"enum": evidence_reasons}
    defs["EvidenceDecision"] = tagged(
        "EvidenceDecision@1",
        {
            "status": {"enum": ["supported", "contested", "unknown", "refused"]},
            "reasons": scalar_set(ref("EvidenceReason")), "accepted_edge_ids": ref("EntityIdSet"),
            "contradiction_edge_ids": ref("EntityIdSet"), "qualification_edge_ids": ref("EntityIdSet"),
            "rejected_source_ids": ref("EntityIdSet"),
        },
        **{"x-evidenceDecisionInvariant": True},
    )

    digest_fields = {
        "goal_spec_digest": ref("Digest"), "policy_digest": ref("Digest"), "grant_digest": ref("Digest"),
        "privacy_digest": ref("Digest"), "route_digest": ref("Digest"), "budget_digest": ref("Digest"),
    }
    defs["EffectIntent"] = tagged(
        "EffectIntent@1",
        {
            "effect_id": ref("EntityId"), "command_id": ref("EntityId"), "idempotency_key": ref("OpaqueRef"),
            "intent_digest": ref("Digest"),
            "effect_class": {"enum": ["local-reversible", "local-irreversible", "external-idempotent", "external-reconciliation-only", "publication"]},
            "target_ref": ref("OpaqueRef"), "payload_digest": ref("Digest"),
            "goal_spec_id": ref("EntityId"), **digest_fields, "plan_digest": ref("Digest"),
            "actor_id": ref("EntityId"), "lease_id": ref("EntityId"),
            "admission_epoch": ref("Epoch"), "fence_epoch": ref("Epoch"), "deadline": ref("Timestamp"),
            "dependency_effect_ids": ref("EntityIdSet"), "reversible": {"type": "boolean"},
            "compensation_effect_id": nullable(ref("EntityId")),
        },
        allOf=[
            {
                "if": {"properties": {"effect_class": {"const": "local-reversible"}}, "required": ["effect_class"]},
                "then": {"properties": {"reversible": {"const": True}, "compensation_effect_id": ref("EntityId")}},
                "else": {"properties": {"reversible": {"const": False}, "compensation_effect_id": {"type": "null"}}},
            }
        ],
        **{"x-selfDigestOmit": "intent_digest"},
    )
    defs["EffectReason"] = {"enum": [
        "admission-refused", "attempt-binding-mismatch", "authority-binding-mismatch",
        "blind-retry-blocked", "compensation-not-separate", "dependency-unresolved",
        "future-pause-inoperative", "intent-binding-mismatch", "observation-binding-mismatch",
        "observation-conflict", "observation-unverified", "paused", "receipt-binding-mismatch",
        "receipt-missing", "reconciliation-required", "reconciliation-unverified",
        "stale-admission", "stale-fence",
    ]}
    defs["EffectAdmission"] = tagged(
        "EffectAdmission@1",
        {
            "admission_id": ref("EntityId"), "effect_id": ref("EntityId"), "intent_digest": ref("Digest"),
            "decision": {"enum": ["admitted", "refused"]}, "actor_id": ref("EntityId"),
            "lease_id": ref("EntityId"), "admission_epoch": ref("Epoch"), "fence_epoch": ref("Epoch"),
            **digest_fields,
            "pause_profile": {"enum": ["current-immediate", "future-checkpoint", "future-interrupt", "future-drain"]},
            "pause_state": {"enum": ["running", "paused"]}, "admitted_at": ref("Timestamp"),
            "reasons": scalar_set(ref("EffectReason")),
        },
        allOf=[{
            "if": {"properties": {"decision": {"const": "admitted"}}, "required": ["decision"]},
            "then": {"properties": {
                "pause_profile": {"const": "current-immediate"}, "pause_state": {"const": "running"},
                "reasons": {"maxItems": 0},
            }},
            "else": {"properties": {"reasons": {"minItems": 1}}},
        }],
    )
    observation_common = {
        "effect_id": ref("EntityId"), "attempt_id": ref("EntityId"), "attempt_number": {"type": "integer", "minimum": 1, "maximum": 64},
        "idempotency_key": ref("OpaqueRef"), "target_ref": ref("OpaqueRef"), "payload_digest": ref("Digest"),
        "admission_epoch": ref("Epoch"), "fence_epoch": ref("Epoch"), "observed_at": ref("Timestamp"),
    }
    defs["AttemptStarted"] = tagged("AttemptStarted@1", observation_common)
    defs["ExternalObserved"] = tagged(
        "ExternalObserved@1",
        {
            **observation_common, "observation_id": ref("EntityId"), "observer_ref": ref("OpaqueRef"),
            "authenticity": {"enum": ["verified", "unverified", "mismatch"]},
            "outcome": {"enum": ["accepted", "rejected", "unknown"]},
            "remote_operation_ref": nullable(ref("OpaqueRef")), "result_digest": nullable(ref("Digest")),
        },
    )
    defs["ReceiptRecorded"] = tagged(
        "ReceiptRecorded@1",
        {
            **observation_common, "receipt_id": ref("EntityId"), "observer_ref": ref("OpaqueRef"),
            "authenticity": {"enum": ["verified", "unverified", "mismatch"]},
            "result": {"enum": ["succeeded", "failed"]}, "result_digest": ref("Digest"),
            "remote_operation_ref": nullable(ref("OpaqueRef")),
        },
    )
    defs["ReconciliationObserved"] = tagged(
        "ReconciliationObserved@1",
        {
            **observation_common, "reconciliation_id": ref("EntityId"), "observer_ref": ref("OpaqueRef"),
            "authenticity": {"enum": ["verified", "unverified", "mismatch"]},
            "outcome": {"enum": ["succeeded", "failed", "unknown"]},
            "result_digest": nullable(ref("Digest")), "remote_operation_ref": nullable(ref("OpaqueRef")),
        },
    )
    defs["EffectObservation"] = {"oneOf": [ref(name) for name in ["AttemptStarted", "ExternalObserved", "ReceiptRecorded", "ReconciliationObserved"]]}
    defs["DependencyEffectState"] = tagged(
        "DependencyEffectState@1",
        {"effect_id": ref("EntityId"), "status": {"enum": ["succeeded", "failed", "ambiguous", "reconciled-succeeded", "reconciled-failed"]}},
    )
    defs["EffectTraceInput"] = tagged(
        "EffectTraceInput@1",
        {
            "intent": ref("EffectIntent"), "admission": ref("EffectAdmission"),
            "observations": ordered("EffectObservation", maximum=128),
            "dependency_states": keyed_set("DependencyEffectState", key="effect_id", maximum=128),
            "current_admission_epoch": ref("Epoch"), "current_fence_epoch": ref("Epoch"),
            "effect_count": {"const": 0}, "external_call_count": {"const": 0},
        },
        **{"x-effectBindings": True, "x-nondecreasingObservationTimes": True},
    )
    defs["EffectDecision"] = tagged(
        "EffectDecision@1",
        {
            "status": {"enum": ["refused", "prepared", "executing", "succeeded", "failed", "ambiguous", "reconciled-succeeded", "reconciled-failed"]},
            "reasons": scalar_set(ref("EffectReason")), "final_attempt_number": ref("Count"),
            "requires_reconciliation": {"type": "boolean"}, "effect_count": {"const": 0},
            "external_call_count": {"const": 0},
        },
        **{"x-effectDecisionInvariant": True},
    )

    defs["PublicationArtifact"] = tagged(
        "PublicationArtifact@1",
        {
            "artifact_id": ref("EntityId"), "content_digest": ref("Digest"), "classification": ref("PrivacyClass"),
            "license_state": ref("LicenseState"),
            "redaction_state": {"enum": ["not-required", "verified", "missing", "unknown"]},
            "secret_scan": {"enum": ["pass", "fail", "unknown"]}, "export_authorized": {"type": "boolean"},
        },
    )
    defs["GateEvidence"] = tagged(
        "GateEvidence@1",
        {
            "gate_id": ref("EntityId"), "source_sha": ref("GitSha"), "candidate_sha": ref("GitSha"),
            "status": {"enum": ["pass", "fail", "unavailable"]}, "evidence_digest": ref("Digest"),
            "observed_at": ref("Timestamp"),
        },
    )
    defs["VerifierEvidence"] = tagged(
        "VerifierEvidence@1",
        {
            "verifier_id": ref("EntityId"), "source_sha": ref("GitSha"), "candidate_sha": ref("GitSha"),
            "status": {"enum": ["pass", "dissent", "unavailable"]},
            "independence": {"enum": ["full", "downgraded", "same-actor"]},
            "policy_sufficient": {"type": "boolean"}, "evidence_digest": ref("Digest"),
            "observed_at": ref("Timestamp"),
        },
    )
    defs["RefName"] = {
        "type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,159}$",
        "minLength": 1, "maxLength": 160, "x-gitRefComponent": True,
    }
    defs["ReviewRef"] = {
        "type": "string", "pattern": r"^refs/heads/[A-Za-z0-9][A-Za-z0-9._/-]{0,159}$",
        "minLength": 12, "maxLength": 171, "x-gitRef": True,
    }
    defs["PublicationIntent"] = tagged(
        "PublicationIntent@1",
        {
            "publication_id": ref("EntityId"), "effect_id": ref("EntityId"), "intent_digest": ref("Digest"),
            "publication_kind": {"enum": ["review-branch", "merge", "release", "deployment"]},
            "repository_ref": ref("OpaqueRef"), "source_sha": ref("GitSha"), "candidate_sha": ref("GitSha"),
            "review_ref": ref("ReviewRef"), "target_branch": ref("RefName"),
            "protected_branch_names": scalar_set(ref("RefName"), minimum=1, maximum=64),
            "goal_spec_id": ref("EntityId"), "goal_spec_digest": ref("Digest"), "policy_digest": ref("Digest"),
            "grant_digest": ref("Digest"), "privacy_digest": ref("Digest"), "candidate_tree_digest": ref("Digest"),
            "required_gate_ids": ref("NonEmptyEntityIdSet"), "required_verifier_ids": ref("NonEmptyEntityIdSet"),
            "artifact_ids": ref("NonEmptyEntityIdSet"),
        },
        **{"x-selfDigestOmit": "intent_digest"},
    )
    defs["PublicationReceipt"] = tagged(
        "PublicationReceipt@1",
        {
            "receipt_id": ref("EntityId"), "publication_id": ref("EntityId"), "effect_id": ref("EntityId"),
            "repository_ref": ref("OpaqueRef"), "review_ref": ref("ReviewRef"), "candidate_sha": ref("GitSha"),
            "publisher_ref": ref("OpaqueRef"), "remote_state": {"enum": ["observed", "rejected", "unknown"]},
            "remote_commit_sha": nullable(ref("GitSha")), "observed_at": ref("Timestamp"),
            "receipt_digest": ref("Digest"),
        },
        allOf=[{
            "if": {"properties": {"remote_state": {"const": "observed"}}, "required": ["remote_state"]},
            "then": {"properties": {"remote_commit_sha": ref("GitSha")}},
            "else": {"properties": {"remote_commit_sha": {"type": "null"}}},
        }],
        **{"x-selfDigestOmit": "receipt_digest"},
    )
    defs["PublicationAssessmentInput"] = tagged(
        "PublicationAssessmentInput@1",
        {
            "intent": ref("PublicationIntent"),
            "artifacts": keyed_set("PublicationArtifact", key="artifact_id", minimum=1),
            "gates": keyed_set("GateEvidence", key="gate_id", minimum=1),
            "verifiers": keyed_set("VerifierEvidence", key="verifier_id", minimum=1),
            "source_ancestry": {"enum": ["known-ancestor", "not-ancestor", "unknown"]},
            "candidate_tree": {"enum": ["clean", "dirty", "unknown"]},
            "publication_authority": {"enum": ["granted", "denied", "unknown"]},
            "required_independence": {"enum": ["full", "downgraded"]},
            "receipt": nullable(ref("PublicationReceipt")), "git_mutation_count": {"const": 0},
        },
        **{"x-publicationBindings": True},
    )
    defs["PublicationReason"] = {"enum": [
        "artifact-binding-mismatch", "artifact-export-prohibited", "artifact-missing",
        "authority-missing", "candidate-dirty", "candidate-state-unknown", "gate-binding-mismatch",
        "gate-failed", "gate-missing", "license-prohibited", "protected-target",
        "publication-kind-prohibited", "receipt-binding-mismatch", "remote-state-unknown",
        "secret-scan-failed", "source-ancestry-unknown", "source-not-ancestor",
        "verification-binding-mismatch", "verification-insufficient", "verification-missing",
    ]}
    defs["PublicationDecision"] = tagged(
        "PublicationDecision@1",
        {
            "status": {"enum": ["eligible", "blocked", "published", "rejected", "ambiguous"]},
            "reasons": scalar_set(ref("PublicationReason")), "publication_id": ref("EntityId"),
            "published_sha": nullable(ref("GitSha")), "requires_reconciliation": {"type": "boolean"},
            "git_mutation_count": {"const": 0},
        },
        **{"x-publicationDecisionInvariant": True},
    )

    defs["WriterRecord"] = tagged(
        "WriterRecord@1",
        {
            "writer_id": ref("EntityId"), "mutation_path_digest": ref("Digest"),
            "observation_state": {"enum": ["known", "unknown"]}, "can_refuse": {"type": "boolean"},
            "configured_fence_epoch": ref("Epoch"), "source_revision": ref("GitSha"),
        },
    )
    defs["CanonicalEvent"] = tagged(
        "CanonicalEvent@1",
        {
            "aggregate_id": ref("EntityId"), "sequence": ref("PositiveCount"), "event_id": ref("EntityId"),
            "command_id": ref("EntityId"), "idempotency_key": ref("OpaqueRef"),
            "causation_id": ref("EntityId"), "correlation_id": ref("EntityId"),
            "writer_id": ref("EntityId"), "fence_epoch": ref("Epoch"), "logical_time": ref("PositiveCount"),
            "schema_version": ref("Token"), "previous_event_digest": nullable(ref("Digest")),
            "payload_digest": ref("Digest"), "event_digest": ref("Digest"),
            "authentication_state": {"enum": ["verified", "unverified", "mismatch"]},
        },
        allOf=[{
            "if": {"properties": {"sequence": {"const": 1}}, "required": ["sequence"]},
            "then": {"properties": {"previous_event_digest": {"type": "null"}}},
            "else": {"properties": {"previous_event_digest": ref("Digest")}},
        }],
        **{"x-selfDigestOmit": "event_digest"},
    )
    defs["OpenWork"] = tagged(
        "OpenWork@1",
        {
            "work_id": ref("EntityId"), "kind": {"enum": ["lease", "effect", "publication", "saga"]},
            "state": {"enum": ["closed", "active", "open", "ambiguous", "pending", "partial"]},
        },
    )
    stage_values = ["snapshotted", "validated", "legacy-writers-quiesced", "fence-established", "imported", "replayed", "shadow-read-verified", "v3-owner-active", "checkpointed"]
    proof_state = {"enum": ["verified", "failed", "unknown"]}
    defs["StateContractAssessmentInput"] = tagged(
        "StateContractAssessmentInput@1",
        {
            "migration_id": ref("EntityId"), "aggregate_type": {"const": "fabric-only"},
            "aggregate_id": ref("EntityId"), "source_revision": ref("GitSha"),
            "source_state_digest": ref("Digest"), "immutable_assignment_digest": ref("Digest"),
            "expected_writer_ids": ref("NonEmptyEntityIdSet"),
            "observed_writers": keyed_set("WriterRecord", key="writer_id", minimum=1),
            "canonical_writer_id": ref("EntityId"), "current_fence_epoch": ref("Epoch"),
            "events": ordered("CanonicalEvent", minimum=1, maximum=512),
            "import_state": {"enum": ["lossless", "lossy", "unknown"]},
            "expected_replay_digest": ref("Digest"), "actual_replay_digest": ref("Digest"),
            "expected_projection_digest": ref("Digest"), "actual_projection_digest": ref("Digest"),
            "writer_refusal": proof_state, "backup": proof_state, "restore": proof_state,
            "reverse_reader": proof_state, "rollback": proof_state,
            "completed_stages": {"type": "array", "items": {"enum": stage_values}, "minItems": 1, "maxItems": len(stage_values), "uniqueItems": True, "x-stagePrefix": stage_values},
            "open_work": keyed_set("OpenWork", key="work_id", maximum=128),
            "deployment_revision_state": {"enum": ["known", "unknown"]}, "state_write_count": {"const": 0},
        },
        **{"x-stateContractInvariant": True},
    )
    defs["StateReason"] = {"enum": [
        "aggregate-scope-mismatch", "backup-unverified", "deployment-unknown", "digest-chain-invalid",
        "dual-writer", "event-unverified", "import-unknown", "logical-time-regression", "lossy-import", "open-effect",
        "duplicate-command-conflict", "open-lease", "pending-publication", "projection-mismatch", "projection-only",
        "replay-mismatch", "restore-unverified", "reverse-reader-unverified", "rollback-unproved",
        "saga-incomplete", "sequence-gap", "stage-order-invalid", "stale-fence", "writer-inventory-incomplete",
        "writer-refusal-unproved", "writer-unknown",
    ]}
    defs["StateDecision"] = tagged(
        "StateDecision@1",
        {
            "status": {"enum": ["eligible", "blocked", "recovery-required"]},
            "reasons": scalar_set(ref("StateReason")), "aggregate_id": ref("EntityId"),
            "final_sequence": ref("Count"), "current_fence_epoch": ref("Epoch"),
            "state_write_count": {"const": 0},
        },
        **{"x-stateDecisionInvariant": True},
    )

    defs["CopyDisposition"] = tagged(
        "CopyDisposition@1",
        {
            "copy_id": ref("EntityId"), "kind": {"enum": ["local", "cache", "replica", "backup", "disconnected-spool"]},
            "state": {"enum": ["deleted", "expiry-bound", "pending", "soft-deleted", "delete-marker", "disconnected", "unknown"]},
            "evidence_state": {"enum": ["verified", "unverified", "mismatch"]},
            "evidence_digest": nullable(ref("Digest")), "expiry_boundary": nullable(ref("Timestamp")),
            "expiry_reached": {"type": "boolean"},
        },
        allOf=[{
            "if": {"properties": {"state": {"const": "expiry-bound"}}, "required": ["state"]},
            "then": {"properties": {"expiry_boundary": ref("Timestamp")}},
            "else": {"properties": {
                "expiry_boundary": {"type": "null"}, "expiry_reached": {"const": False},
            }},
        }],
    )
    artifact_classes = ["raw-session", "temporary", "cache", "accepted-evidence", "gate-receipt", "publication-receipt", "effect-receipt", "authority-receipt", "audit-record"]
    tombstone_copies = ordered("CopyDisposition", minimum=1, maximum=128)
    tombstone_copies["x-strictlySortedBy"] = "copy_id"
    tombstone_copies["x-uniqueBy"] = "copy_id"
    defs["DeletionTombstone"] = tagged(
        "DeletionTombstone@1",
        {
            "tombstone_id": ref("EntityId"), "artifact_id": ref("EntityId"),
            "artifact_class": {"enum": artifact_classes},
            "policy_digest": ref("Digest"), "responsible_component": ref("EntityId"),
            "requested_at": ref("Timestamp"), "disposed_at": nullable(ref("Timestamp")),
            "copy_dispositions": tombstone_copies, "contains_content": {"type": "boolean"},
            "contains_secret": {"type": "boolean"}, "contains_global_content_digest": {"type": "boolean"},
            "tombstone_digest": ref("Digest"),
        },
        **{"x-selfDigestOmit": "tombstone_digest"},
    )
    defs["RetentionAssessmentInput"] = tagged(
        "RetentionAssessmentInput@1",
        {
            "artifact_id": ref("EntityId"), "artifact_class": {"enum": artifact_classes},
            "privacy_class": ref("PrivacyClass"), "policy_digest": ref("Digest"),
            "owner_erasure_policy": {"enum": ["granted", "denied", "unknown", "not-required"]},
            "legal_hold": {"type": "boolean"}, "local_content_deleted": {"type": "boolean"},
            "key_state": {"enum": ["destroyed", "active", "shared", "unknown"]},
            "key_scope": {"enum": ["artifact", "project", "shared", "unknown"]},
            "copies": keyed_set("CopyDisposition", key="copy_id", minimum=1),
            "tombstone": ref("DeletionTombstone"), "deletion_operation_count": {"const": 0},
        },
        **{"x-retentionBindings": True},
    )
    defs["RetentionReason"] = {"enum": [
        "copy-evidence-unverified", "copy-inventory-mismatch", "copy-unresolved",
        "expiry-not-reached", "key-not-destroyed", "key-not-isolated", "legal-hold",
        "local-content-present", "owner-policy-denied", "owner-policy-required",
        "tombstone-mismatch", "tombstone-sensitive",
    ]}
    defs["RetentionDecision"] = tagged(
        "RetentionDecision@1",
        {
            "status": {"enum": ["complete", "incomplete", "blocked"]},
            "reasons": scalar_set(ref("RetentionReason")), "artifact_id": ref("EntityId"),
            "resolved_copy_ids": ref("EntityIdSet"), "unresolved_copy_ids": ref("EntityIdSet"),
            "deletion_operation_count": {"const": 0},
        },
        **{"x-retentionDecisionInvariant": True},
    )

    common_fixture = {
        "fixture_id": {"type": "string", "pattern": r"^F-M1C-[0-9]{3}$"},
        "purpose": ref("Text"), "source_requirement_ids": ref("RequirementIdSet"),
    }
    fixture_arms = [
        ("EvidenceFixtureBundle", "EvidenceFixtureBundle@1", "EvidenceAssessmentInput", "EvidenceDecision"),
        ("EffectFixtureBundle", "EffectFixtureBundle@1", "EffectTraceInput", "EffectDecision"),
        ("PublicationFixtureBundle", "PublicationFixtureBundle@1", "PublicationAssessmentInput", "PublicationDecision"),
        ("StateFixtureBundle", "StateFixtureBundle@1", "StateContractAssessmentInput", "StateDecision"),
        ("RetentionFixtureBundle", "RetentionFixtureBundle@1", "RetentionAssessmentInput", "RetentionDecision"),
    ]
    for name, tag, input_name, output_name in fixture_arms:
        defs[name] = tagged(
            tag,
            {**common_fixture, "input": ref(input_name), "expected": ref(output_name)},
            **{"x-fixtureBindings": True},
        )
    defs["M1CFixtureBundle"] = {"oneOf": [ref(name) for name, *_ in fixture_arms]}
    defs["FixtureManifestEntry"] = tagged(
        "FixtureManifestEntry@1",
        {
            "fixture_id": {"type": "string", "pattern": r"^F-M1C-[0-9]{3}$"},
            "path": ref("OpaqueRef"), "digest": ref("Digest"),
            "bundle_type": {"enum": [tag for _, tag, _, _ in fixture_arms]},
        },
    )
    defs["FixtureManifest"] = tagged(
        "FixtureManifest@1",
        {"schema_digest": ref("Digest"), "fixtures": keyed_set("FixtureManifestEntry", key="fixture_id", minimum=24, maximum=24)},
    )

    public = [
        "SourceRecord", "ResearchClaim", "EvidenceEdge", "EvidenceAssessmentInput", "EvidenceDecision",
        "EffectIntent", "EffectAdmission", "EffectObservation", "EffectTraceInput", "EffectDecision",
        "PublicationIntent", "PublicationReceipt", "PublicationAssessmentInput", "PublicationDecision",
        "CanonicalEvent", "StateContractAssessmentInput", "StateDecision", "RetentionAssessmentInput",
        "RetentionDecision", "M1CFixtureBundle", "FixtureManifest",
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": SCHEMA_ID,
        "title": "Recursion v3 M1C integrity requirement contracts",
        "oneOf": [ref(name) for name in public], "$defs": defs,
    }


def encoded() -> bytes:
    return (json.dumps(build_schema(), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main(argv: list[str]) -> int:
    if argv == ["--write"]:
        OUTPUT.write_bytes(encoded())
        print("M1C_SCHEMA_MATERIALIZED")
        return 0
    if argv == ["--check"]:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != encoded():
            print("M1C_SCHEMA_MATERIALIZATION_MISMATCH", file=sys.stderr)
            return 1
        print("M1C_SCHEMA_MATERIALIZATION_PASS")
        return 0
    print("usage: materialize.py --write | --check", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
