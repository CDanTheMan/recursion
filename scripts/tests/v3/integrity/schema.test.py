#!/usr/bin/env python3
"""Strict schema, decoder and semantic-extension gates for M1C."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import jsonschema
from jsonschema import validators


ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / "schemas" / "control-plane" / "v3" / "integrity" / "schema.json"
MATERIALIZER_PATH = SCHEMA_PATH.with_name("materialize.py")
MAX_BYTES = 1_048_576
MAX_DEPTH = 32
D1 = "sha256:" + "1" * 64
D2 = "sha256:" + "2" * 64
D3 = "sha256:" + "3" * 64
SHA1 = "a" * 40
SHA2 = "b" * 40
NOW = "2026-09-04T12:00:00Z"


class StrictJSONError(ValueError):
    pass


def _reject_constant(value: str) -> None:
    raise StrictJSONError(f"non-I-JSON constant: {value}")


def _reject_float(value: str) -> None:
    raise StrictJSONError(f"float not permitted: {value}")


def _parse_int(value: str) -> int:
    if value == "-0":
        raise StrictJSONError("negative zero is forbidden")
    return int(value, 10)


def _object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise StrictJSONError(f"duplicate key: {key}")
        result[key] = value
    return result


def _depth(value: Any, current: int = 1) -> int:
    if isinstance(value, dict):
        return max([current] + [_depth(item, current + 1) for item in value.values()])
    if isinstance(value, list):
        return max([current] + [_depth(item, current + 1) for item in value])
    return current


def strict_loads(raw: bytes) -> Any:
    if len(raw) > MAX_BYTES:
        raise StrictJSONError("object exceeds byte ceiling")
    if raw.startswith(b"\xef\xbb\xbf"):
        raise StrictJSONError("UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise StrictJSONError("invalid UTF-8") from exc
    value = json.loads(
        text, object_pairs_hook=_object_pairs, parse_int=_parse_int,
        parse_float=_reject_float, parse_constant=_reject_constant,
    )
    if _depth(value) > MAX_DEPTH:
        raise StrictJSONError("object exceeds depth ceiling")
    return value


def canonical_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_bytes(value: Any) -> bytes:
    return (canonical_key(value) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def seal(value: dict[str, Any], field: str) -> dict[str, Any]:
    result = copy.deepcopy(value)
    result[field] = digest({key: item for key, item in result.items() if key != field})
    return result


def _utf8_max(validator: Any, limit: int, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if isinstance(instance, str) and len(instance.encode("utf-8")) > limit:
        yield jsonschema.ValidationError(f"UTF-8 length exceeds {limit}")


def _strictly_sorted(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if enabled and isinstance(instance, list):
        keys = [canonical_key(item) for item in instance]
        if any(left >= right for left, right in zip(keys, keys[1:])):
            yield jsonschema.ValidationError("array is not strictly sorted")


def _strictly_sorted_by(validator: Any, field: str, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if isinstance(instance, list) and all(isinstance(item, dict) and field in item for item in instance):
        keys = [canonical_key(item[field]) for item in instance]
        if any(left >= right for left, right in zip(keys, keys[1:])):
            yield jsonschema.ValidationError(f"array is not strictly sorted by {field}")


def _unique_by(validator: Any, field: str, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if isinstance(instance, list) and all(isinstance(item, dict) and field in item for item in instance):
        keys = [canonical_key(item[field]) for item in instance]
        if len(keys) != len(set(keys)):
            yield jsonschema.ValidationError(f"array is not unique by {field}")


def _strictly_sorted_by_fields(validator: Any, fields: list[str], instance: Any, schema: dict[str, Any]):
    del validator, schema
    if isinstance(instance, list) and all(isinstance(item, dict) and all(f in item for f in fields) for item in instance):
        keys = [canonical_key([item[field] for field in fields]) for item in instance]
        if any(left >= right for left, right in zip(keys, keys[1:])):
            yield jsonschema.ValidationError(f"array is not strictly sorted by {fields}")


def _unique_by_fields(validator: Any, fields: list[str], instance: Any, schema: dict[str, Any]):
    del validator, schema
    if isinstance(instance, list) and all(isinstance(item, dict) and all(f in item for f in fields) for item in instance):
        keys = [canonical_key([item[field] for field in fields]) for item in instance]
        if len(keys) != len(set(keys)):
            yield jsonschema.ValidationError(f"array is not unique by {fields}")


def _utc_timestamp(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if enabled and isinstance(instance, str):
        try:
            parsed = datetime.strptime(instance, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            yield jsonschema.ValidationError("invalid UTC timestamp")
            return
        if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != instance:
            yield jsonschema.ValidationError("non-canonical UTC timestamp")


def _canonical_uri(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, str):
        return
    parts = urlsplit(instance)
    if parts.scheme == "https":
        if not parts.netloc or parts.username is not None or parts.password is not None or parts.fragment:
            yield jsonschema.ValidationError("non-canonical or credential-bearing HTTPS URI")
    elif not (instance.startswith("urn:") or instance.startswith("recursion:")):
        yield jsonschema.ValidationError("unsupported canonical URI scheme")


def _valid_ref_tail(value: str) -> bool:
    return not any(token in value for token in ["..", "//", "@{"]) and not value.endswith(("/", ".", ".lock")) and not value.startswith("/")


def _git_ref_component(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if enabled and isinstance(instance, str) and not _valid_ref_tail(instance):
        yield jsonschema.ValidationError("unsafe Git ref component")


def _git_ref(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if enabled and isinstance(instance, str):
        if not instance.startswith("refs/heads/") or not _valid_ref_tail(instance[len("refs/heads/"):]):
            yield jsonschema.ValidationError("unsafe review ref")


def _stage_prefix(validator: Any, stages: list[str], instance: Any, schema: dict[str, Any]):
    del validator, schema
    if isinstance(instance, list) and instance != stages[:len(instance)]:
        yield jsonschema.ValidationError("completed stages are not an ordered prefix")


def _self_digest(validator: Any, field: str, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if isinstance(instance, dict) and isinstance(instance.get(field), str):
        expected = digest({key: value for key, value in instance.items() if key != field})
        if instance[field] != expected:
            yield jsonschema.ValidationError(f"{field} does not seal the record")


def _source_invariant(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    if instance.get("lifecycle") == "verified":
        identifiers = instance.get("persistent_identifiers", [])
        if not any(item.get("verification_state") == "verified" for item in identifiers if isinstance(item, dict)):
            yield jsonschema.ValidationError("verified source has no verified persistent identifier")


def _evidence_bindings(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    claim = instance.get("claim", {})
    sources = instance.get("sources", [])
    edges = instance.get("edges", [])
    source_ids = {item.get("source_id") for item in sources if isinstance(item, dict)}
    required = set(claim.get("required_source_ids", [])) if isinstance(claim, dict) else set()
    referenced = {item.get("source_id") for item in edges if isinstance(item, dict)}
    if not required <= source_ids or source_ids != referenced:
        yield jsonschema.ValidationError("source inventory does not match required/referenced sources")
    claim_id = claim.get("claim_id") if isinstance(claim, dict) else None
    if any(item.get("claim_id") != claim_id or item.get("source_id") not in source_ids for item in edges if isinstance(item, dict)):
        yield jsonschema.ValidationError("evidence edge binding mismatch")


def _evidence_decision(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    status = instance.get("status")
    accepted = instance.get("accepted_edge_ids", [])
    contradictions = instance.get("contradiction_edge_ids", [])
    reasons = instance.get("reasons", [])
    if status == "supported" and (not accepted or contradictions):
        yield jsonschema.ValidationError("supported decision has no support or retains contradiction")
    if status == "contested" and (not accepted or not contradictions):
        yield jsonschema.ValidationError("contested decision needs support and contradiction")
    if status == "unknown" and accepted:
        yield jsonschema.ValidationError("unknown decision cannot accept support")
    if status == "refused" and not reasons:
        yield jsonschema.ValidationError("refused decision needs a reason")


def _effect_bindings(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    intent = instance.get("intent", {})
    admission = instance.get("admission", {})
    direct = ["effect_id", "intent_digest", "actor_id", "lease_id", "admission_epoch", "fence_epoch",
              "goal_spec_digest", "policy_digest", "grant_digest", "privacy_digest", "route_digest", "budget_digest"]
    if any(intent.get(field) != admission.get(field) for field in direct):
        yield jsonschema.ValidationError("effect admission does not bind the intent")
    identity = ["effect_id", "idempotency_key", "target_ref", "payload_digest", "admission_epoch", "fence_epoch"]
    for observation in instance.get("observations", []):
        if any(observation.get(field) != intent.get(field) for field in identity):
            yield jsonschema.ValidationError("effect observation does not bind the intent")


def _effect_decision(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    status = instance.get("status")
    reasons = instance.get("reasons", [])
    reconcile = instance.get("requires_reconciliation")
    if status in {"prepared", "executing", "succeeded", "failed"} and (reasons or reconcile):
        yield jsonschema.ValidationError("settled/nonterminal effect decision has contradictory reasons")
    if status == "ambiguous" and (not reasons or reconcile is not True):
        yield jsonschema.ValidationError("ambiguous effect decision must require reconciliation")
    if status == "refused" and not reasons:
        yield jsonschema.ValidationError("refused effect decision needs a reason")


def _nondecreasing_times(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if enabled and isinstance(instance, dict):
        times = [item.get("observed_at") for item in instance.get("observations", []) if isinstance(item, dict)]
        if any(left > right for left, right in zip(times, times[1:])):
            yield jsonschema.ValidationError("effect observations are not time ordered")


def _publication_bindings(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    intent = instance.get("intent", {})
    artifact_ids = {item.get("artifact_id") for item in instance.get("artifacts", []) if isinstance(item, dict)}
    gate_ids = {item.get("gate_id") for item in instance.get("gates", []) if isinstance(item, dict)}
    verifier_ids = {item.get("verifier_id") for item in instance.get("verifiers", []) if isinstance(item, dict)}
    if set(intent.get("artifact_ids", [])) != artifact_ids or set(intent.get("required_gate_ids", [])) != gate_ids or set(intent.get("required_verifier_ids", [])) != verifier_ids:
        yield jsonschema.ValidationError("publication evidence inventory mismatch")
    for row in [*instance.get("gates", []), *instance.get("verifiers", [])]:
        if row.get("source_sha") != intent.get("source_sha") or row.get("candidate_sha") != intent.get("candidate_sha"):
            yield jsonschema.ValidationError("publication evidence candidate binding mismatch")
    receipt = instance.get("receipt")
    if isinstance(receipt, dict):
        fields = ["publication_id", "effect_id", "repository_ref", "review_ref", "candidate_sha"]
        if any(receipt.get(field) != intent.get(field) for field in fields):
            yield jsonschema.ValidationError("publication receipt binding mismatch")


def _publication_decision(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    status = instance.get("status")
    reasons = instance.get("reasons", [])
    published = instance.get("published_sha")
    reconcile = instance.get("requires_reconciliation")
    if status == "eligible" and (reasons or published is not None or reconcile):
        yield jsonschema.ValidationError("eligible publication decision is contradictory")
    if status == "published" and (reasons or published is None or reconcile):
        yield jsonschema.ValidationError("published decision lacks an exact settled SHA")
    if status == "ambiguous" and (not reasons or published is not None or reconcile is not True):
        yield jsonschema.ValidationError("ambiguous publication must require reconciliation")
    if status == "blocked" and not reasons:
        yield jsonschema.ValidationError("blocked publication needs a reason")
    if status == "rejected" and (reasons or published is not None or reconcile):
        yield jsonschema.ValidationError("rejected publication decision is contradictory")


def _state_invariant(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    expected = set(instance.get("expected_writer_ids", []))
    if instance.get("canonical_writer_id") not in expected:
        yield jsonschema.ValidationError("canonical writer is absent from the expected inventory")


def _state_decision(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    if instance.get("status") == "eligible" and instance.get("reasons"):
        yield jsonschema.ValidationError("eligible state decision has reasons")
    if instance.get("status") != "eligible" and not instance.get("reasons"):
        yield jsonschema.ValidationError("non-eligible state decision needs reasons")


def _retention_bindings(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    tombstone = instance.get("tombstone", {})
    fields = ["artifact_class", "policy_digest"]
    if any(tombstone.get(field) != instance.get(field) for field in fields):
        yield jsonschema.ValidationError("tombstone binding mismatch")
    copies = [(row.get("copy_id"), row.get("state")) for row in instance.get("copies", []) if isinstance(row, dict)]
    tombstone_copies = [(row.get("copy_id"), row.get("state")) for row in tombstone.get("copy_dispositions", []) if isinstance(row, dict)]
    if copies != tombstone_copies:
        yield jsonschema.ValidationError("tombstone copy inventory mismatch")


def _retention_decision(validator: Any, enabled: bool, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not enabled or not isinstance(instance, dict):
        return
    status = instance.get("status")
    reasons = instance.get("reasons", [])
    unresolved = instance.get("unresolved_copy_ids", [])
    if status == "complete" and (reasons or unresolved):
        yield jsonschema.ValidationError("complete retention decision retains unresolved evidence")
    if status == "incomplete" and (not reasons or not unresolved):
        yield jsonschema.ValidationError("incomplete retention decision needs unresolved copies")
    if status == "blocked" and not reasons:
        yield jsonschema.ValidationError("blocked retention decision needs reasons")


M1CValidator = validators.extend(
    jsonschema.Draft202012Validator,
    {
        "x-utf8MaxBytes": _utf8_max, "x-strictlySorted": _strictly_sorted,
        "x-strictlySortedBy": _strictly_sorted_by, "x-uniqueBy": _unique_by,
        "x-strictlySortedByFields": _strictly_sorted_by_fields, "x-uniqueByFields": _unique_by_fields,
        "x-rfc3339Utc": _utc_timestamp, "x-canonicalUri": _canonical_uri,
        "x-gitRefComponent": _git_ref_component, "x-gitRef": _git_ref,
        "x-stagePrefix": _stage_prefix, "x-selfDigestOmit": _self_digest,
        "x-sourceInvariant": _source_invariant, "x-evidenceBindings": _evidence_bindings,
        "x-evidenceDecisionInvariant": _evidence_decision, "x-effectBindings": _effect_bindings,
        "x-effectDecisionInvariant": _effect_decision,
        "x-nondecreasingObservationTimes": _nondecreasing_times,
        "x-publicationBindings": _publication_bindings, "x-publicationDecisionInvariant": _publication_decision,
        "x-stateContractInvariant": _state_invariant, "x-stateDecisionInvariant": _state_decision,
        "x-retentionBindings": _retention_bindings, "x-retentionDecisionInvariant": _retention_decision,
    },
)


def load_schema() -> dict[str, Any]:
    return strict_loads(SCHEMA_PATH.read_bytes())


def validate(value: Any, definition: str | None = None) -> None:
    schema = load_schema()
    target = schema if definition is None else {"$ref": f"#/$defs/{definition}", "$defs": schema["$defs"]}
    M1CValidator(target).validate(value)


def source(source_id: str = "source:one", *, relation_state: str = "current") -> dict[str, Any]:
    return {
        "type": "SourceRecord@1", "source_id": source_id, "canonical_uri": f"https://example.invalid/{source_id}",
        "persistent_identifiers": [{"type": "PersistentIdentifier@1", "scheme": "doi", "value": f"10.0000/{source_id}", "verification_state": "verified", "verification_evidence_digest": D1}],
        "title_digest": D1, "creator_digests": [D2], "publisher_digest": D3,
        "source_class": "paper", "primary_status": "primary", "supported_scopes": ["external-mechanism"],
        "lifecycle": "verified", "editorial_state": relation_state, "access_state": "accessible",
        "license_state": "permitted", "privacy_class": "public", "version": "v1",
        "published_at": "2026-09-01T00:00:00Z", "retrieved_at": "2026-09-03T00:00:00Z",
        "adapter_ref": "adapter:synthetic", "adapter_revision": "v1", "request_digest": D1,
        "content_digest": D2, "representation_size": 10, "verification_evidence_digest": D3,
        "related_source_ids": [], "revalidate_after": "2026-10-01T00:00:00Z",
    }


def claim() -> dict[str, Any]:
    return {
        "type": "ResearchClaim@1", "claim_id": "claim:one", "goal_spec_id": "goal:one",
        "goal_spec_digest": D1, "proposition_digest": D2, "claim_kind": "fact",
        "evidence_scope": "external-mechanism", "intended_use": "internal",
        "required_source_ids": ["source:one"], "assumption_digests": [], "definition_digests": [],
        "revalidate_after": "2026-10-01T00:00:00Z",
    }


def edge() -> dict[str, Any]:
    return {
        "type": "EvidenceEdge@1", "edge_id": "edge:one", "claim_id": "claim:one",
        "source_id": "source:one", "relation": "supports", "locator": "section:one",
        "extraction_digest": D3, "source_version": "v1", "applicability": "exact",
        "extraction_verified": True,
    }


def evidence_input() -> dict[str, Any]:
    return {
        "type": "EvidenceAssessmentInput@1", "observed_at": NOW, "claim": claim(),
        "sources": [source()], "edges": [edge()], "allowed_privacy_classes": ["public"],
        "allowed_license_states": ["permitted"], "public_export_authorized": False,
    }


def effect_intent() -> dict[str, Any]:
    return seal({
        "type": "EffectIntent@1", "effect_id": "effect:one", "command_id": "command:one",
        "idempotency_key": "idempotency:one", "intent_digest": D1,
        "effect_class": "external-idempotent", "target_ref": "target:one", "payload_digest": D2,
        "goal_spec_id": "goal:one", "goal_spec_digest": D1, "policy_digest": D1,
        "grant_digest": D1, "privacy_digest": D1, "route_digest": D1, "budget_digest": D1,
        "plan_digest": D1, "actor_id": "actor:one", "lease_id": "lease:one",
        "admission_epoch": 2, "fence_epoch": 3, "deadline": "2026-09-05T00:00:00Z",
        "dependency_effect_ids": [], "reversible": False, "compensation_effect_id": None,
    }, "intent_digest")


def effect_admission(intent: dict[str, Any] | None = None) -> dict[str, Any]:
    intent = effect_intent() if intent is None else intent
    return {
        "type": "EffectAdmission@1", "admission_id": "admission:one", "effect_id": intent["effect_id"],
        "intent_digest": intent["intent_digest"], "decision": "admitted", "actor_id": intent["actor_id"],
        "lease_id": intent["lease_id"], "admission_epoch": intent["admission_epoch"],
        "fence_epoch": intent["fence_epoch"], "goal_spec_digest": intent["goal_spec_digest"],
        "policy_digest": intent["policy_digest"], "grant_digest": intent["grant_digest"],
        "privacy_digest": intent["privacy_digest"], "route_digest": intent["route_digest"],
        "budget_digest": intent["budget_digest"], "pause_profile": "current-immediate",
        "pause_state": "running", "admitted_at": NOW, "reasons": [],
    }


def effect_input() -> dict[str, Any]:
    intent = effect_intent()
    return {
        "type": "EffectTraceInput@1", "intent": intent, "admission": effect_admission(intent),
        "observations": [], "dependency_states": [], "current_admission_epoch": 2,
        "current_fence_epoch": 3, "effect_count": 0, "external_call_count": 0,
    }


def publication_intent() -> dict[str, Any]:
    return seal({
        "type": "PublicationIntent@1", "publication_id": "publication:one", "effect_id": "effect:publication",
        "intent_digest": D1, "publication_kind": "review-branch", "repository_ref": "repository:synthetic",
        "source_sha": SHA1, "candidate_sha": SHA2, "review_ref": "refs/heads/review/m1c",
        "target_branch": "master", "protected_branch_names": ["master"], "goal_spec_id": "goal:one",
        "goal_spec_digest": D1, "policy_digest": D1, "grant_digest": D1, "privacy_digest": D1,
        "candidate_tree_digest": D1, "required_gate_ids": ["gate:one"],
        "required_verifier_ids": ["verifier:one"], "artifact_ids": ["artifact:one"],
    }, "intent_digest")


def publication_input() -> dict[str, Any]:
    intent = publication_intent()
    return {
        "type": "PublicationAssessmentInput@1", "intent": intent,
        "artifacts": [{"type": "PublicationArtifact@1", "artifact_id": "artifact:one", "content_digest": D1, "classification": "public", "license_state": "permitted", "redaction_state": "not-required", "secret_scan": "pass", "export_authorized": True}],
        "gates": [{"type": "GateEvidence@1", "gate_id": "gate:one", "source_sha": SHA1, "candidate_sha": SHA2, "status": "pass", "evidence_digest": D1, "observed_at": NOW}],
        "verifiers": [{"type": "VerifierEvidence@1", "verifier_id": "verifier:one", "source_sha": SHA1, "candidate_sha": SHA2, "status": "pass", "independence": "full", "policy_sufficient": True, "evidence_digest": D2, "observed_at": NOW}],
        "source_ancestry": "known-ancestor", "candidate_tree": "clean", "publication_authority": "granted",
        "required_independence": "full", "receipt": None, "git_mutation_count": 0,
    }


def event() -> dict[str, Any]:
    return seal({
        "type": "CanonicalEvent@1", "aggregate_id": "aggregate:fabric", "sequence": 1,
        "event_id": "event:one", "command_id": "command:one", "idempotency_key": "idempotency:one",
        "causation_id": "event:genesis", "correlation_id": "correlation:one",
        "writer_id": "writer:canonical", "fence_epoch": 2, "logical_time": 1,
        "schema_version": "v1", "previous_event_digest": None, "payload_digest": D1,
        "event_digest": D2, "authentication_state": "verified",
    }, "event_digest")


def state_input() -> dict[str, Any]:
    return {
        "type": "StateContractAssessmentInput@1", "migration_id": "migration:one",
        "aggregate_type": "fabric-only", "aggregate_id": "aggregate:fabric", "source_revision": SHA1,
        "source_state_digest": D1, "immutable_assignment_digest": D2,
        "expected_writer_ids": ["writer:canonical"],
        "observed_writers": [{"type": "WriterRecord@1", "writer_id": "writer:canonical", "mutation_path_digest": D1, "observation_state": "known", "can_refuse": True, "configured_fence_epoch": 2, "source_revision": SHA1}],
        "canonical_writer_id": "writer:canonical", "current_fence_epoch": 2, "events": [event()],
        "import_state": "lossless", "expected_replay_digest": D1, "actual_replay_digest": D1,
        "expected_projection_digest": D2, "actual_projection_digest": D2,
        "writer_refusal": "verified", "backup": "verified", "restore": "verified",
        "reverse_reader": "verified", "rollback": "verified",
        "completed_stages": ["snapshotted", "validated", "legacy-writers-quiesced", "fence-established", "imported", "replayed", "shadow-read-verified", "v3-owner-active", "checkpointed"],
        "open_work": [], "deployment_revision_state": "known", "state_write_count": 0,
    }


def copy_disposition(copy_id: str = "copy:local", state: str = "deleted") -> dict[str, Any]:
    return {
        "type": "CopyDisposition@1", "copy_id": copy_id, "kind": "local", "state": state,
        "evidence_state": "verified", "evidence_digest": D1, "expiry_boundary": None,
        "expiry_reached": False,
    }


def retention_input() -> dict[str, Any]:
    copies = [copy_disposition()]
    tombstone = seal({
        "type": "DeletionTombstone@1", "tombstone_id": "tombstone:one", "artifact_class": "raw-session",
        "policy_digest": D1, "responsible_component": "component:retention", "requested_at": NOW,
        "disposed_at": "2026-09-04T12:01:00Z", "copy_dispositions": copy.deepcopy(copies),
        "contains_content": False, "contains_secret": False, "contains_global_content_digest": False,
        "tombstone_digest": D2,
    }, "tombstone_digest")
    return {
        "type": "RetentionAssessmentInput@1", "artifact_id": "artifact:raw", "artifact_class": "raw-session",
        "privacy_class": "private", "policy_digest": D1, "owner_erasure_policy": "not-required",
        "legal_hold": False, "local_content_deleted": True, "key_state": "destroyed", "key_scope": "artifact",
        "copies": copies, "tombstone": tombstone, "deletion_operation_count": 0,
    }


class M1CSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_schema()

    def test_meta_schema_and_materializer(self) -> None:
        jsonschema.Draft202012Validator.check_schema(self.schema)
        spec = importlib.util.spec_from_file_location("m1c_materializer", MATERIALIZER_PATH)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertEqual(SCHEMA_PATH.read_bytes(), module.encoded())

    def test_all_object_definitions_are_closed(self) -> None:
        object_count = 0
        def walk(value: Any) -> None:
            nonlocal object_count
            if isinstance(value, dict):
                if value.get("type") == "object":
                    object_count += 1
                    self.assertIs(value.get("additionalProperties"), False)
                    self.assertEqual(set(value.get("required", [])), set(value.get("properties", {})))
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
        walk(self.schema)
        self.assertGreaterEqual(object_count, 30)

    def test_strict_decoder_rejects_ambiguous_json(self) -> None:
        bad = [b'{"a":1,"a":2}', b'{"a":1.0}', b'{"a":-0}', b'{"a":NaN}', b'\xef\xbb\xbf{}', b'"\xff"']
        for raw in bad:
            with self.subTest(raw=raw), self.assertRaises((StrictJSONError, json.JSONDecodeError)):
                strict_loads(raw)
        value: Any = 0
        for _ in range(MAX_DEPTH + 1):
            value = [value]
        with self.assertRaises(StrictJSONError):
            strict_loads(json.dumps(value).encode())

    def test_scalars_timestamps_uris_refs_and_sorting_are_strict(self) -> None:
        validate(NOW, "Timestamp")
        for bad in ["2026-99-99T00:00:00Z", "2026-09-04T12:00:00+00:00"]:
            with self.assertRaises(jsonschema.ValidationError):
                validate(bad, "Timestamp")
        validate("https://example.invalid/source", "CanonicalUri")
        with self.assertRaises(jsonschema.ValidationError):
            validate("https://user:secret@example.invalid/source", "CanonicalUri")
        for bad in ["feature/../master", "feature//x", "feature/x.lock"]:
            with self.assertRaises(jsonschema.ValidationError):
                validate(bad, "RefName")
        with self.assertRaises(jsonschema.ValidationError):
            validate(True, "Count")
        with self.assertRaises(jsonschema.ValidationError):
            validate(["source:b", "source:a"], "EntityIdSet")

    def test_source_and_evidence_records_bind_exactly(self) -> None:
        validate(source(), "SourceRecord")
        validate(evidence_input(), "EvidenceAssessmentInput")
        bad = source()
        bad["persistent_identifiers"][0]["verification_state"] = "unverified"
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "SourceRecord")
        bad = evidence_input()
        bad["edges"][0]["source_id"] = "source:other"
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "EvidenceAssessmentInput")

    def test_evidence_decision_shapes_are_semantic(self) -> None:
        validate({"type": "EvidenceDecision@1", "status": "supported", "reasons": [], "accepted_edge_ids": ["edge:one"], "contradiction_edge_ids": [], "qualification_edge_ids": [], "rejected_source_ids": []}, "EvidenceDecision")
        bad = {"type": "EvidenceDecision@1", "status": "contested", "reasons": ["contradiction-present"], "accepted_edge_ids": ["edge:one"], "contradiction_edge_ids": [], "qualification_edge_ids": [], "rejected_source_ids": []}
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "EvidenceDecision")

    def test_effect_intent_admission_and_trace_bind_exactly(self) -> None:
        validate(effect_intent(), "EffectIntent")
        validate(effect_input(), "EffectTraceInput")
        bad = effect_input()
        bad["intent"]["payload_digest"] = D3
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "EffectTraceInput")
        bad = effect_input()
        bad["admission"]["pause_profile"] = "future-checkpoint"
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "EffectTraceInput")

    def test_effect_observation_union_is_closed(self) -> None:
        value = effect_input()
        intent = value["intent"]
        attempt = {"type": "AttemptStarted@1", "effect_id": intent["effect_id"], "attempt_id": "attempt:one", "attempt_number": 1, "idempotency_key": intent["idempotency_key"], "target_ref": intent["target_ref"], "payload_digest": intent["payload_digest"], "admission_epoch": 2, "fence_epoch": 3, "observed_at": NOW}
        validate(attempt, "EffectObservation")
        attempt["unknown"] = True
        with self.assertRaises(jsonschema.ValidationError):
            validate(attempt, "EffectObservation")

    def test_publication_records_bind_candidate_and_receipt(self) -> None:
        validate(publication_input(), "PublicationAssessmentInput")
        bad = publication_input()
        bad["gates"][0]["candidate_sha"] = SHA1
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "PublicationAssessmentInput")
        bad = publication_intent()
        bad["intent_digest"] = D1
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "PublicationIntent")

    def test_state_contract_events_inventory_and_stages_bind(self) -> None:
        validate(state_input(), "StateContractAssessmentInput")
        bad = state_input()
        bad["completed_stages"] = ["snapshotted", "legacy-writers-quiesced"]
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "StateContractAssessmentInput")
        bad = state_input()
        bad["events"][0]["event_digest"] = D1
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "StateContractAssessmentInput")

    def test_retention_copy_and_tombstone_bind_exactly(self) -> None:
        validate(retention_input(), "RetentionAssessmentInput")
        bad = retention_input()
        bad["tombstone"]["policy_digest"] = D2
        bad["tombstone"] = seal(bad["tombstone"], "tombstone_digest")
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "RetentionAssessmentInput")
        bad = copy_disposition(state="expiry-bound")
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "CopyDisposition")

    def test_fixture_union_and_manifest_are_closed(self) -> None:
        bundle = {"type": "EvidenceFixtureBundle@1", "fixture_id": "F-M1C-001", "purpose": "synthetic", "source_requirement_ids": ["REQ-M1C-EVIDENCE"], "input": evidence_input(), "expected": {"type": "EvidenceDecision@1", "status": "supported", "reasons": [], "accepted_edge_ids": ["edge:one"], "contradiction_edge_ids": [], "qualification_edge_ids": [], "rejected_source_ids": []}}
        validate(bundle, "M1CFixtureBundle")
        bundle["type"] = "UnknownFixture@1"
        with self.assertRaises(jsonschema.ValidationError):
            validate(bundle, "M1CFixtureBundle")


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("M1C_SCHEMA_PASS tests=12")
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
