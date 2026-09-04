#!/usr/bin/env python3
"""Pure reference evaluators for the Recursion v3 M1C integrity contracts.

The module deliberately has no filesystem, clock, network, environment, random, or
subprocess access.  Callers supply a schema-valid value and receive a deterministic
decision without performing the represented effect.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


SUPPORT_RELATIONS = {"supports", "replicates", "updates"}
PROTECTED_ARTIFACT_CLASSES = {
    "authority-receipt",
    "audit-record",
    "effect-receipt",
    "gate-receipt",
    "publication-receipt",
}
MIGRATION_STAGES = [
    "snapshotted",
    "validated",
    "legacy-writers-quiesced",
    "fence-established",
    "imported",
    "replayed",
    "shadow-read-verified",
    "v3-owner-active",
    "checkpointed",
]


def canonical_bytes(value: Any) -> bytes:
    """Return the M1C canonical representation used by self-digests."""

    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _valid_self_digest(value: dict[str, Any], field: str) -> bool:
    return value.get(field) == _digest(
        {key: item for key, item in value.items() if key != field}
    )


def _sorted(values: set[str] | list[str]) -> list[str]:
    return sorted(set(values))


def assess_evidence(value: dict[str, Any]) -> dict[str, Any]:
    claim = value["claim"]
    sources = {item["source_id"]: item for item in value["sources"]}
    reasons: set[str] = set()
    rejected_sources: set[str] = set()
    source_reasons: dict[str, set[str]] = {}
    claim_stale = (
        claim.get("revalidate_after") is not None
        and value["observed_at"] > claim["revalidate_after"]
    )

    for source_id in claim["required_source_ids"]:
        if source_id not in sources:
            reasons.add("source-missing")

    for source_id, source in sources.items():
        faults: set[str] = set()
        access = source["access_state"]
        editorial = source["editorial_state"]

        if access == "metadata-only":
            faults.add("metadata-only")
        elif access != "accessible":
            faults.add("source-inaccessible")
        elif source["lifecycle"] == "expired":
            faults.add("source-stale")
        elif (
            source["lifecycle"] != "verified"
            or not any(
                identifier["verification_state"] == "verified"
                for identifier in source["persistent_identifiers"]
            )
            or any(
                identifier["verification_state"] == "mismatch"
                for identifier in source["persistent_identifiers"]
            )
        ):
            faults.add("source-unverified")

        if editorial in {"retracted", "withdrawn"}:
            faults.add("source-retracted")
        elif editorial == "superseded":
            faults.add("source-superseded")
        elif editorial not in {"current", "corrected"}:
            faults.add("source-unverified")

        if (
            source.get("revalidate_after") is not None
            and value["observed_at"] > source["revalidate_after"]
        ):
            faults.add("source-stale")
        if claim_stale:
            faults.add("source-stale")
        if (
            source.get("retrieved_at") is not None
            and (
                source["retrieved_at"] > value["observed_at"]
                or (
                    source.get("published_at") is not None
                    and source["published_at"] > source["retrieved_at"]
                )
                or (
                    source.get("revalidate_after") is not None
                    and source["revalidate_after"] < source["retrieved_at"]
                )
            )
        ):
            faults.add("source-unverified")
        if claim["evidence_scope"] not in source["supported_scopes"]:
            faults.add("scope-inapplicable")
        if (
            source["license_state"] in {"unknown", "prohibited"}
            or source["license_state"] not in value["allowed_license_states"]
        ):
            faults.add("license-prohibited")
        if source["privacy_class"] not in value["allowed_privacy_classes"]:
            faults.add("privacy-prohibited")
        if (
            claim["intended_use"] == "public"
            and not value["public_export_authorized"]
            and (
                source["privacy_class"] != "public"
                or source["license_state"] != "permitted"
            )
        ):
            faults.add("export-prohibited")

        if faults:
            rejected_sources.add(source_id)
            reasons.update(faults)
        source_reasons[source_id] = faults

    accepted: set[str] = set()
    contradictions: set[str] = set()
    qualifications: set[str] = set()
    for edge in value["edges"]:
        edge_faults: set[str] = set()
        source = sources.get(edge["source_id"])
        if edge["claim_id"] != claim["claim_id"]:
            edge_faults.add("claim-binding-mismatch")
        if source is None:
            edge_faults.add("source-missing")
        else:
            if edge["source_version"] != source["version"]:
                edge_faults.add("edge-binding-mismatch")
            edge_faults.update(source_reasons[source["source_id"]])
        if edge["applicability"] != "exact" or edge["relation"] == "inapplicable":
            edge_faults.add("scope-inapplicable")
        if not edge["extraction_verified"]:
            edge_faults.add("extraction-unverified")
        if edge["relation"] == "metadata-only":
            edge_faults.add("metadata-only")

        if edge_faults:
            reasons.update(edge_faults)
            if source is not None:
                rejected_sources.add(source["source_id"])
            continue
        if edge["relation"] in SUPPORT_RELATIONS:
            accepted.add(edge["edge_id"])
        elif edge["relation"] == "contradicts":
            contradictions.add(edge["edge_id"])
        elif edge["relation"] == "qualifies":
            qualifications.add(edge["edge_id"])

    if contradictions:
        reasons.add("contradiction-present")
    if qualifications:
        reasons.add("qualification-present")

    refusal_reasons = {
        "claim-binding-mismatch",
        "edge-binding-mismatch",
        "export-prohibited",
        "license-prohibited",
        "privacy-prohibited",
    }
    if reasons & refusal_reasons:
        status = "refused"
        accepted.clear()
    elif accepted and contradictions:
        status = "contested"
    elif accepted:
        status = "supported"
    else:
        status = "unknown"
        reasons.add("support-insufficient")

    return {
        "type": "EvidenceDecision@1",
        "status": status,
        "reasons": _sorted(reasons),
        "accepted_edge_ids": _sorted(accepted),
        "contradiction_edge_ids": _sorted(contradictions),
        "qualification_edge_ids": _sorted(qualifications),
        "rejected_source_ids": _sorted(rejected_sources),
    }


def _effect_observation_binding_reason(kind: str) -> str:
    if kind == "AttemptStarted@1":
        return "attempt-binding-mismatch"
    if kind == "ReceiptRecorded@1":
        return "receipt-binding-mismatch"
    return "observation-binding-mismatch"


def classify_effect_trace(value: dict[str, Any]) -> dict[str, Any]:
    intent = value["intent"]
    admission = value["admission"]
    observations = value["observations"]
    reasons: set[str] = set()

    if not _valid_self_digest(intent, "intent_digest"):
        reasons.add("intent-binding-mismatch")

    identity_fields = (
        "effect_id",
        "intent_digest",
        "actor_id",
        "lease_id",
        "admission_epoch",
        "fence_epoch",
        "goal_spec_digest",
        "policy_digest",
        "grant_digest",
        "privacy_digest",
        "route_digest",
        "budget_digest",
    )
    authority_fields = {
        "actor_id",
        "lease_id",
        "goal_spec_digest",
        "policy_digest",
        "grant_digest",
        "privacy_digest",
        "route_digest",
        "budget_digest",
    }
    for field in identity_fields:
        if admission[field] != intent[field]:
            reasons.add(
                "authority-binding-mismatch"
                if field in authority_fields
                else "intent-binding-mismatch"
            )

    if admission["decision"] != "admitted":
        reasons.add("admission-refused")
    if admission["pause_state"] == "paused":
        reasons.add("paused")
    if admission["pause_profile"] != "current-immediate":
        reasons.add("future-pause-inoperative")
    if (
        admission["admission_epoch"] != value["current_admission_epoch"]
        or intent["admission_epoch"] != value["current_admission_epoch"]
    ):
        reasons.add("stale-admission")
    if (
        admission["fence_epoch"] != value["current_fence_epoch"]
        or intent["fence_epoch"] != value["current_fence_epoch"]
    ):
        reasons.add("stale-fence")

    dependency_states = {
        item["effect_id"]: item["status"] for item in value["dependency_states"]
    }
    if any(
        dependency_states.get(effect_id)
        not in {"succeeded", "reconciled-succeeded"}
        for effect_id in intent["dependency_effect_ids"]
    ):
        reasons.add("dependency-unresolved")
    if (
        intent["compensation_effect_id"] is not None
        and intent["compensation_effect_id"] == intent["effect_id"]
    ):
        reasons.add("compensation-not-separate")

    attempts: dict[int, dict[str, Any]] = {}
    attempt_ids: set[str] = set()
    pending_possible: set[int] = set()
    settled_attempts: set[int] = set()
    valid_externals: list[dict[str, Any]] = []
    valid_receipts: list[dict[str, Any]] = []
    valid_reconciliations: list[dict[str, Any]] = []
    record_ids: dict[str, set[str]] = {
        "observation_id": set(), "receipt_id": set(), "reconciliation_id": set(),
    }
    common_fields = (
        "effect_id",
        "idempotency_key",
        "target_ref",
        "payload_digest",
        "admission_epoch",
        "fence_epoch",
    )
    for observation in observations:
        kind = observation["type"]
        binding_ok = not any(
            observation[field] != intent[field] for field in common_fields
        )
        if not binding_ok:
            reasons.add(_effect_observation_binding_reason(kind))
        number = observation["attempt_number"]
        if kind == "AttemptStarted@1":
            expected_number = max(attempts, default=0) + 1
            if (
                number in attempts
                or observation["attempt_id"] in attempt_ids
                or number != expected_number
            ):
                reasons.add("attempt-binding-mismatch")
            if pending_possible:
                reasons.add("blind-retry-blocked")
            attempts[number] = observation
            attempt_ids.add(observation["attempt_id"])
        else:
            attempt_value = attempts.get(number)
            if (
                attempt_value is None
                or observation["attempt_id"] != attempt_value["attempt_id"]
            ):
                reasons.add(_effect_observation_binding_reason(kind))
                binding_ok = False
            authenticity = observation["authenticity"]
            record_id_field = {
                "ExternalObserved@1": "observation_id",
                "ReceiptRecorded@1": "receipt_id",
                "ReconciliationObserved@1": "reconciliation_id",
            }[kind]
            if observation[record_id_field] in record_ids[record_id_field]:
                reasons.add("observation-conflict")
            record_ids[record_id_field].add(observation[record_id_field])
            if authenticity != "verified":
                reasons.add(
                    "reconciliation-unverified"
                    if kind == "ReconciliationObserved@1"
                    else "observation-unverified"
                )
            if kind == "ExternalObserved@1":
                if binding_ok and authenticity == "verified":
                    valid_externals.append(observation)
                    if (
                        observation["outcome"] in {"accepted", "unknown"}
                        and number not in settled_attempts
                    ):
                        pending_possible.add(number)
            elif kind == "ReceiptRecorded@1":
                if binding_ok and authenticity == "verified":
                    valid_receipts.append(observation)
                    settled_attempts.add(number)
                    pending_possible.discard(number)
            else:
                if binding_ok and authenticity == "verified":
                    valid_reconciliations.append(observation)
                    if observation["outcome"] in {"succeeded", "failed"}:
                        settled_attempts.add(number)
                        pending_possible.discard(number)
                    elif number not in settled_attempts:
                        pending_possible.add(number)

    for number in attempts:
        external_values = [
            item for item in valid_externals if item["attempt_number"] == number
        ]
        receipt_values = [
            item for item in valid_receipts if item["attempt_number"] == number
        ]
        reconciliation_values = [
            item for item in valid_reconciliations if item["attempt_number"] == number
        ]
        settlement_values = [*external_values, *receipt_values, *reconciliation_values]
        remote_refs = {
            item["remote_operation_ref"]
            for item in settlement_values
            if item["remote_operation_ref"] is not None
        }
        result_digests = {
            item["result_digest"]
            for item in settlement_values
            if item["result_digest"] is not None
        }
        observers = {item["observer_ref"] for item in settlement_values}
        receipt_outcomes = {
            (item["result"], item["result_digest"], item["remote_operation_ref"])
            for item in receipt_values
        }
        reconciliation_outcomes = {
            (item["outcome"], item["result_digest"], item["remote_operation_ref"])
            for item in reconciliation_values
            if item["outcome"] in {"succeeded", "failed"}
        }
        external_outcomes = {item["outcome"] for item in external_values}
        settled_succeeded = any(
            item["result"] == "succeeded" for item in receipt_values
        ) or any(
            item["outcome"] == "succeeded" for item in reconciliation_values
        )
        if (
            len(remote_refs) > 1
            or len(result_digests) > 1
            or len(observers) > 1
            or len(receipt_outcomes) > 1
            or len(reconciliation_outcomes) > 1
            or len(external_outcomes) > 1
            or ("rejected" in external_outcomes and settled_succeeded)
        ):
            reasons.add("observation-conflict")

    final_attempt = max(attempts, default=0)
    hard_refusal = reasons & {
        "admission-refused",
        "authority-binding-mismatch",
        "compensation-not-separate",
        "dependency-unresolved",
        "future-pause-inoperative",
        "intent-binding-mismatch",
        "paused",
        "stale-admission",
        "stale-fence",
    }
    verified_reconciliations = [
        item
        for item in valid_reconciliations
        if item["outcome"] in {"succeeded", "failed"}
    ]
    verified_receipts = valid_receipts
    all_remote_refs = {
        item["remote_operation_ref"]
        for item in [*valid_externals, *valid_receipts, *valid_reconciliations]
        if item["remote_operation_ref"] is not None
    }
    all_result_digests = {
        item["result_digest"]
        for item in [*valid_externals, *valid_receipts, *valid_reconciliations]
        if item["result_digest"] is not None
    }
    if len(all_remote_refs) > 1 or len(all_result_digests) > 1:
        reasons.add("observation-conflict")
    if "observation-conflict" in reasons or pending_possible:
        if pending_possible:
            reasons.add("receipt-missing")
        reasons.add("reconciliation-required")
        status = "ambiguous"
        reconcile = True
    else:
        settled = {
            *(item["result"] for item in verified_receipts),
            *(item["outcome"] for item in verified_reconciliations),
        }
        if len(settled) > 1:
            reasons.add("observation-conflict")
            reasons.add("reconciliation-required")
            status = "ambiguous"
            reconcile = True
        elif verified_reconciliations:
            outcome = verified_reconciliations[-1]["outcome"]
            status = "reconciled-succeeded" if outcome == "succeeded" else "reconciled-failed"
            reconcile = False
        elif verified_receipts:
            status = verified_receipts[-1]["result"]
            reconcile = False
        elif any(item["outcome"] == "rejected" for item in valid_externals):
            status = "failed"
            reconcile = False
        elif hard_refusal:
            status = "refused"
            reconcile = False
        else:
            if final_attempt:
                status = "executing"
                reconcile = False
            else:
                status = "prepared"
                reconcile = False

    if status in {"prepared", "executing"} and reasons:
        status = "ambiguous"
        reasons.add("reconciliation-required")
        reconcile = True
    return {
        "type": "EffectDecision@1",
        "status": status,
        "reasons": _sorted(reasons),
        "final_attempt_number": final_attempt,
        "requires_reconciliation": reconcile,
        "effect_count": 0,
        "external_call_count": 0,
    }


def assess_publication(value: dict[str, Any]) -> dict[str, Any]:
    intent = value["intent"]
    reasons: set[str] = set()
    if not _valid_self_digest(intent, "intent_digest"):
        reasons.add("receipt-binding-mismatch")

    review_branch = intent["review_ref"].removeprefix("refs/heads/")
    if review_branch in intent["protected_branch_names"]:
        reasons.add("protected-target")
    if review_branch == intent["target_branch"]:
        reasons.add("publication-kind-prohibited")
    if intent["publication_kind"] != "review-branch":
        reasons.add("publication-kind-prohibited")
        if intent["target_branch"] in intent["protected_branch_names"]:
            reasons.add("protected-target")
    if value["source_ancestry"] == "not-ancestor":
        reasons.add("source-not-ancestor")
    elif value["source_ancestry"] == "unknown":
        reasons.add("source-ancestry-unknown")
    if value["candidate_tree"] == "dirty":
        reasons.add("candidate-dirty")
    elif value["candidate_tree"] == "unknown":
        reasons.add("candidate-state-unknown")
    if value["publication_authority"] != "granted":
        reasons.add("authority-missing")

    artifacts = {item["artifact_id"]: item for item in value["artifacts"]}
    required_artifacts = set(intent["artifact_ids"])
    if not required_artifacts.issubset(artifacts):
        reasons.add("artifact-missing")
    if set(artifacts) != required_artifacts:
        reasons.add("artifact-binding-mismatch")
    for artifact_id in required_artifacts & set(artifacts):
        artifact = artifacts[artifact_id]
        if (
            not artifact["export_authorized"]
            or artifact["classification"] != "public"
            or artifact["redaction_state"] in {"missing", "unknown"}
        ):
            reasons.add("artifact-export-prohibited")
        if artifact["secret_scan"] != "pass":
            reasons.add("secret-scan-failed")
        if artifact["license_state"] != "permitted":
            reasons.add("license-prohibited")

    gates = {item["gate_id"]: item for item in value["gates"]}
    required_gates = set(intent["required_gate_ids"])
    if not required_gates.issubset(gates):
        reasons.add("gate-missing")
    for gate_id in required_gates & set(gates):
        gate = gates[gate_id]
        if gate["source_sha"] != intent["source_sha"] or gate["candidate_sha"] != intent["candidate_sha"]:
            reasons.add("gate-binding-mismatch")
        elif gate["status"] != "pass":
            reasons.add("gate-failed")

    verifiers = {item["verifier_id"]: item for item in value["verifiers"]}
    required_verifiers = set(intent["required_verifier_ids"])
    if not required_verifiers.issubset(verifiers):
        reasons.add("verification-missing")
    independence_rank = {"same-actor": 0, "downgraded": 1, "full": 2}
    for verifier_id in required_verifiers & set(verifiers):
        verifier = verifiers[verifier_id]
        if verifier["source_sha"] != intent["source_sha"] or verifier["candidate_sha"] != intent["candidate_sha"]:
            reasons.add("verification-binding-mismatch")
        elif (
            verifier["status"] != "pass"
            or not verifier["policy_sufficient"]
            or independence_rank[verifier["independence"]]
            < independence_rank[value["required_independence"]]
        ):
            reasons.add("verification-insufficient")

    receipt = value["receipt"]
    published_sha = None
    reconcile = False
    observed_remote_state = None
    if receipt is not None:
        receipt_fields = ("publication_id", "effect_id", "repository_ref", "review_ref", "candidate_sha")
        if (
            not _valid_self_digest(receipt, "receipt_digest")
            or any(receipt[field] != intent[field] for field in receipt_fields)
        ):
            reasons.add("receipt-binding-mismatch")
        elif receipt["remote_state"] == "unknown":
            reasons.add("remote-state-unknown")
            reconcile = True
        elif receipt["remote_state"] == "observed":
            if receipt["remote_commit_sha"] != intent["candidate_sha"]:
                reasons.add("receipt-binding-mismatch")
            else:
                published_sha = receipt["remote_commit_sha"]
                observed_remote_state = "observed"
        else:
            observed_remote_state = "rejected"

    if observed_remote_state == "observed":
        status = "published"
    elif observed_remote_state == "rejected":
        status = "rejected"
    elif "remote-state-unknown" in reasons:
        status = "ambiguous"
    elif reasons:
        status = "blocked"
    else:
        status = "eligible"
    return {
        "type": "PublicationDecision@1",
        "status": status,
        "reasons": _sorted(reasons),
        "publication_id": intent["publication_id"],
        "published_sha": published_sha,
        "requires_reconciliation": reconcile,
        "git_mutation_count": 0,
    }


def assess_state_contract(value: dict[str, Any]) -> dict[str, Any]:
    reasons: set[str] = set()
    if value["aggregate_type"] != "fabric-only":
        reasons.add("aggregate-scope-mismatch")

    expected_writers = set(value["expected_writer_ids"])
    observed_writers = {item["writer_id"]: item for item in value["observed_writers"]}
    if set(observed_writers) != expected_writers:
        reasons.add("writer-inventory-incomplete")
    canonical = observed_writers.get(value["canonical_writer_id"])
    if canonical is None:
        reasons.add("writer-inventory-incomplete")
    for writer_id, writer in observed_writers.items():
        if writer["observation_state"] != "known":
            reasons.add("writer-unknown")
        if writer["configured_fence_epoch"] != value["current_fence_epoch"]:
            reasons.add("stale-fence")
        if writer["source_revision"] != value["source_revision"]:
            reasons.add("deployment-unknown")
        if not writer["can_refuse"]:
            reasons.add("writer-refusal-unproved")
            if writer_id != value["canonical_writer_id"]:
                reasons.add("dual-writer")
    if value["writer_refusal"] != "verified":
        reasons.add("writer-refusal-unproved")

    events = value["events"]
    command_ids: set[str] = set()
    idempotency_keys: set[str] = set()
    event_ids: set[str] = set()
    previous_digest = None
    previous_fence = 0
    previous_logical_time = 0
    for index, event in enumerate(events, start=1):
        if event["aggregate_id"] != value["aggregate_id"]:
            reasons.add("aggregate-scope-mismatch")
        if event["sequence"] != index:
            reasons.add("sequence-gap")
        if event["previous_event_digest"] != previous_digest:
            reasons.add("digest-chain-invalid")
        if not _valid_self_digest(event, "event_digest"):
            reasons.add("digest-chain-invalid")
        if event["authentication_state"] != "verified":
            reasons.add("event-unverified")
        if event["writer_id"] != value["canonical_writer_id"]:
            reasons.add("stale-fence")
        if (
            event["fence_epoch"] < previous_fence
            or event["fence_epoch"] > value["current_fence_epoch"]
        ):
            reasons.add("stale-fence")
        if event["logical_time"] <= previous_logical_time:
            reasons.add("logical-time-regression")
        if (
            event["command_id"] in command_ids
            or event["idempotency_key"] in idempotency_keys
            or event["event_id"] in event_ids
        ):
            reasons.add("duplicate-command-conflict")
        command_ids.add(event["command_id"])
        idempotency_keys.add(event["idempotency_key"])
        event_ids.add(event["event_id"])
        previous_digest = event["event_digest"]
        previous_fence = event["fence_epoch"]
        previous_logical_time = event["logical_time"]

    if value["import_state"] == "lossy":
        reasons.add("lossy-import")
    elif value["import_state"] == "unknown":
        reasons.add("import-unknown")
    if value["actual_replay_digest"] != value["expected_replay_digest"]:
        reasons.add("replay-mismatch")
    projection_matches = value["actual_projection_digest"] == value["expected_projection_digest"]
    if not projection_matches:
        reasons.add("projection-mismatch")

    proofs = {
        "backup": "backup-unverified",
        "restore": "restore-unverified",
        "reverse_reader": "reverse-reader-unverified",
        "rollback": "rollback-unproved",
    }
    for field, reason in proofs.items():
        if value[field] != "verified":
            reasons.add(reason)
    completed = value["completed_stages"]
    if completed != MIGRATION_STAGES[: len(completed)]:
        reasons.add("stage-order-invalid")
    elif completed != MIGRATION_STAGES and projection_matches:
        reasons.add("projection-only")

    open_reasons = {
        "lease": "open-lease",
        "effect": "open-effect",
        "publication": "pending-publication",
        "saga": "saga-incomplete",
    }
    closed_states = {"closed"}
    for item in value["open_work"]:
        if item["state"] not in closed_states:
            reasons.add(open_reasons[item["kind"]])
    if value["deployment_revision_state"] != "known":
        reasons.add("deployment-unknown")

    recovery_reasons = {
        "aggregate-scope-mismatch",
        "digest-chain-invalid",
        "duplicate-command-conflict",
        "event-unverified",
        "import-unknown",
        "lossy-import",
        "logical-time-regression",
        "projection-mismatch",
        "replay-mismatch",
        "sequence-gap",
        "stale-fence",
    }
    if reasons & recovery_reasons:
        status = "recovery-required"
    elif reasons:
        status = "blocked"
    else:
        status = "eligible"
    return {
        "type": "StateDecision@1",
        "status": status,
        "reasons": _sorted(reasons),
        "aggregate_id": value["aggregate_id"],
        "final_sequence": max((event["sequence"] for event in events), default=0),
        "current_fence_epoch": value["current_fence_epoch"],
        "state_write_count": 0,
    }


def assess_retention(value: dict[str, Any]) -> dict[str, Any]:
    reasons: set[str] = set()
    copies = {item["copy_id"]: item for item in value["copies"]}
    tombstone = value["tombstone"]
    tombstone_copies = {
        item["copy_id"]: item for item in tombstone["copy_dispositions"]
    }
    if set(copies) != set(tombstone_copies) or any(
        copies[copy_id] != tombstone_copies[copy_id] for copy_id in set(copies) & set(tombstone_copies)
    ):
        reasons.add("copy-inventory-mismatch")
    if (
        not _valid_self_digest(tombstone, "tombstone_digest")
        or tombstone["artifact_class"] != value["artifact_class"]
        or tombstone["policy_digest"] != value["policy_digest"]
    ):
        reasons.add("tombstone-mismatch")

    resolved: set[str] = set()
    unresolved: set[str] = set()
    for copy_id, item in copies.items():
        evidence_ok = item["evidence_state"] == "verified" and item["evidence_digest"] is not None
        deleted = item["state"] == "deleted" and evidence_ok
        expired = (
            item["state"] == "expiry-bound"
            and item["expiry_reached"]
            and item["expiry_boundary"] is not None
            and evidence_ok
        )
        if deleted or expired:
            resolved.add(copy_id)
        else:
            unresolved.add(copy_id)
            reasons.add("copy-unresolved")
            if not evidence_ok:
                reasons.add("copy-evidence-unverified")
            if item["state"] == "expiry-bound" and not item["expiry_reached"]:
                reasons.add("expiry-not-reached")

    disposed_at = tombstone["disposed_at"]
    if disposed_at is not None and disposed_at < tombstone["requested_at"]:
        reasons.add("tombstone-mismatch")
    if disposed_at is not None and (unresolved or not value["local_content_deleted"]):
        reasons.add("tombstone-mismatch")
    if disposed_at is None and not unresolved and value["local_content_deleted"]:
        reasons.add("tombstone-mismatch")

    if not value["local_content_deleted"]:
        reasons.add("local-content-present")
    if value["key_state"] != "destroyed":
        reasons.add("key-not-destroyed")
    if value["key_scope"] not in {"artifact", "project"}:
        reasons.add("key-not-isolated")
    if value["legal_hold"]:
        reasons.add("legal-hold")
    if (
        tombstone["contains_content"]
        or tombstone["contains_secret"]
        or tombstone["contains_global_content_digest"]
    ):
        reasons.add("tombstone-sensitive")
    if value["artifact_class"] in PROTECTED_ARTIFACT_CLASSES:
        if value["owner_erasure_policy"] == "denied":
            reasons.add("owner-policy-denied")
        elif value["owner_erasure_policy"] != "granted":
            reasons.add("owner-policy-required")

    blocking = {
        "copy-inventory-mismatch",
        "key-not-destroyed",
        "key-not-isolated",
        "legal-hold",
        "owner-policy-denied",
        "owner-policy-required",
        "tombstone-mismatch",
        "tombstone-sensitive",
    }
    if reasons & blocking:
        status = "blocked"
    elif unresolved or "local-content-present" in reasons:
        status = "incomplete"
    else:
        status = "complete"
    return {
        "type": "RetentionDecision@1",
        "status": status,
        "reasons": _sorted(reasons),
        "artifact_id": value["artifact_id"],
        "resolved_copy_ids": _sorted(resolved),
        "unresolved_copy_ids": _sorted(unresolved),
        "deletion_operation_count": 0,
    }


def evaluate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    evaluators = {
        "EvidenceFixtureBundle@1": assess_evidence,
        "EffectFixtureBundle@1": classify_effect_trace,
        "PublicationFixtureBundle@1": assess_publication,
        "StateFixtureBundle@1": assess_state_contract,
        "RetentionFixtureBundle@1": assess_retention,
    }
    return evaluators[bundle["type"]](bundle["input"])
