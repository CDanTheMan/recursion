"""Pure M1A strict JSON decoding and RFC 8785-compatible canonical digests."""

from __future__ import annotations

import copy
import hashlib
import json


MAX_IJSON_INTEGER = 9_007_199_254_740_991
MAX_INPUT_BYTES = 1_048_576
MAX_COLLECTION_ITEMS = 2_048
MAX_DEPTH = 16

COMMAND_FIELDS = {
    "command_schema_version", "command_id", "command_type", "actor_id", "auth_ref",
    "lease_ref", "logical_time", "expected_state_version", "expected_state_digest",
    "goal_ref", "plan_ref", "payload", "payload_digest", "candidate_digest",
    "content_digest",
}
EVENT_FIELDS = {
    "event_schema_version", "event_id", "stream_id", "sequence", "previous_event_digest",
    "logical_time", "command_id", "command_digest", "event_type", "primary_record",
    "related_records", "state_delta_digest", "content_digest",
}
DOMAIN_FIELDS = {
    "object_type", "schema_version", "id", "version", "created_by_actor_id",
    "created_under_lease", "causation_id", "correlation_id", "created_logical_time",
    "payload", "content_digest",
}
RECEIPT_FIELDS = {
    "receipt_schema_version", "receipt_id", "command_id", "command_digest",
    "disposition", "primary_error", "related_errors", "witness",
    "state_before_digest", "state_after_digest", "event_ids",
    "first_event_sequence", "last_event_sequence", "content_digest",
}
PROJECTION_FIELDS = {
    "projection_schema_version", "stream_id", "state_version", "last_event_sequence",
    "last_event_digest", "operative_goal_ref", "active_arm_run_ref", "active_plan_ref",
    "records", "object_states", "processed_command_receipts",
    "consumed_novelty_delta_digests", "open_blocker_refs", "open_escalation_refs",
    "ambiguous_effect_refs", "current_pause_policy_ref", "current_pause_epoch",
    "terminal_status", "content_digest",
}

DOMAIN_VERSIONS = {
    "arm-run": "m1a-arm-run-1",
    "blocker": "m1a-blocker-1",
    "budget-reservation": "m1a-budget-reservation-1",
    "capacity-observation": "m1a-capacity-observation-1",
    "checkpoint": "m1a-checkpoint-1",
    "disposition": "m1a-disposition-1",
    "effect-observation": "m1a-effect-observation-1",
    "escalation": "m1a-escalation-1",
    "executive-lease": "m1a-executive-lease-1",
    "gate-result": "m1a-gate-result-1",
    "goal-spec-amendment": "m1a-goal-spec-amendment-1",
    "goal-spec": "m1a-goal-spec-1",
    "owner-intent": "m1a-owner-intent-1",
    "owner-verifier-exception": "m1a-owner-verifier-exception-1",
    "pause-directive": "m1a-pause-directive-1",
    "plan-revision": "m1a-plan-revision-1",
    "plan-transition": "m1a-plan-transition-1",
    "plan-verifier-decision": "m1a-plan-verifier-decision-1",
    "replan-decision": "m1a-replan-decision-1",
    "retry-decision": "m1a-retry-decision-1",
    "route-assignment": "m1a-route-assignment-1",
    "task-node": "m1a-task-node-1",
    "work-lease": "m1a-work-lease-1",
    "work-packet": "m1a-work-packet-1",
    "worker-result": "m1a-worker-result-1",
}

DOMAIN_PAYLOAD_FIELDS = {
    "arm-run": {"goal_ref", "logical_actor_id", "eligible_route_ids", "eligible_account_class_ids", "eligible_capacity_pool_ids", "budget_limits", "source_digests", "executive_lease_ref", "verifier_policy_ref"},
    "blocker": {"blocked_object_ref", "kind", "evidence_digests", "required_actor_id", "allowed_recovery_ids", "retry_after_observation_ref", "failure_fingerprint_digest", "state"},
    "budget-reservation": {"goal_ref", "plan_ref", "task_ref", "limits", "consumed", "remaining", "state"},
    "capacity-observation": {"route_id", "account_class_id", "capacity_pool_id", "spend_class", "available", "remaining_units", "observation_digest"},
    "checkpoint": {"state_version", "state_digest", "active_goal_ref", "active_plan_ref", "open_packet_refs", "ambiguous_effect_refs", "budget_snapshot_digest", "route_snapshot_digest", "pause_epoch", "lease_epoch_digest"},
    "disposition": {"object_ref", "disposition", "replacement_ref", "reason_digest"},
    "effect-observation": {"effect_id", "effect_key", "work_packet_ref", "idempotency_key_digest", "dispatch_state", "receipt_digest", "provider_operation_id_digest", "observation", "quarantine"},
    "escalation": {"source_blocker_ref", "target_role", "failure_history_digests", "requested_decision", "option_digests", "recommendation_digest", "frozen_scope_digest", "state"},
    "executive-lease": {"subject_actor_id", "goal_ref", "plan_ref", "task_ref", "supersedes_lease_ref", "lease_epoch", "nonce_digest", "issued_logical_time", "expires_logical_time", "allowed_command_types", "state"},
    "gate-result": {"goal_ref", "plan_ref", "task_ref", "work_packet_ref", "candidate_digest", "source_digests", "evidence_digests", "gate_requirement", "procedure_version", "observation_digest", "expected_digest", "actual_digest", "independence", "disposition", "limitation_digests"},
    "goal-spec-amendment": {"old_goal_ref", "new_goal_ref", "changed_field_paths", "rationale_digest", "owner_authority_attestation_id", "effective_fence_epoch", "checkpoint_rule", "compatibility_inputs", "dispositions", "plan_transition_ref"},
    "goal-spec": {"owner_intent_ref", "outcome", "acceptance_gate_ids", "allowed_resource_paths", "non_goals", "authority_ids", "capability_ids", "allowed_action_ids", "prohibition_ids", "authority_policy_ref", "privacy_class_id", "egress_class_id", "privacy_policy_ref", "egress_policy_ref", "route_policy_ref", "allowed_route_ids", "allowed_account_class_ids", "allowed_capacity_pool_ids", "budget_limits", "source_digests", "novelty_policy_ref", "retry_policy_ref", "verifier_policy_ref", "constitution_policy_ref", "pause_policy_ref", "allowed_effect_keys", "publication_allowed", "terminal_owner_seam_ids", "fence_epoch", "state"},
    "owner-intent": {"intent_text", "source_kind", "source_digest", "privacy_policy_ref", "supersedes_ref"},
    "owner-verifier-exception": {"goal_ref", "plan_ref", "candidate_digest", "verifier_policy_ref", "constitution_policy_ref", "missing_dimensions", "reason_digest", "owner_authority_attestation_id", "issued_logical_time", "expires_logical_time"},
    "pause-directive": {"pause_policy_ref", "mode", "new_pause_epoch", "reason_digest"},
    "plan-revision": {"goal_ref", "arm_run_ref", "prior_plan_ref", "trigger", "task_node_refs", "dependency_edges", "graph_digest", "acceptance_gate_ids", "budget_limits", "read_resource_paths", "write_resource_paths", "effect_keys", "source_digests", "verifier_policy_ref", "constitution_policy_ref", "assigned_plan_verifier_actor_id", "change_rationale_digest", "dispositions"},
    "plan-transition": {"from_plan_ref", "to_plan_ref", "trigger_evidence_digests", "dispositions", "executive_lease_ref", "expected_goal_fence_epoch", "checkpoint_ref"},
    "plan-verifier-decision": {"goal_ref", "plan_ref", "candidate_digest", "event_log_digest", "gate_result_digests", "evidence_digests", "verifier_policy_ref", "constitution_policy_ref", "independence", "disposition", "assurance_grade", "owner_exception_ref", "dissent_digest", "limitation_digests"},
    "replan-decision": {"goal_ref", "old_plan_ref", "new_plan_ref", "trigger_evidence_digests", "dispositions", "narrowed_binding_digest", "blocker_ref", "escalation_ref", "disposition"},
    "retry-decision": {"goal_ref", "plan_ref", "task_ref", "failed_gate_result_ref", "prior_work_packet_ref", "novelty_delta", "novelty_delta_digest", "unchanged_binding_digest", "next_attempt", "remaining_budget", "retry_maximum", "disposition"},
    "route-assignment": {"logical_actor_id", "route_id", "route_capability_ids", "account_class_id", "capacity_pool_id", "privacy_policy_ref", "egress_policy_ref", "route_policy_ref", "metered_spend_allowed", "capacity_observation_ref", "supersedes_route_ref", "assigned_logical_time", "expires_logical_time", "state"},
    "task-node": {"plan_ref", "semantic_definition_digest", "output_schema_digest", "dependency_node_ids", "input_digests", "source_digests", "read_resource_paths", "write_resource_paths", "effect_keys", "authority_ids", "capability_ids", "allowed_action_ids", "prohibition_ids", "route_ids", "route_capability_ids", "account_class_ids", "capacity_pool_ids", "authority_policy_ref", "privacy_class_id", "egress_class_id", "privacy_policy_ref", "egress_policy_ref", "budget_limits", "gate_requirements", "retry_policy_ref", "verifier_policy_ref", "constitution_policy_ref", "terminal_contribution_digest", "retry_maximum"},
    "work-lease": {"subject_actor_id", "goal_ref", "plan_ref", "task_ref", "supersedes_lease_ref", "lease_epoch", "nonce_digest", "issued_logical_time", "expires_logical_time", "allowed_command_types", "state"},
    "work-packet": {"goal_ref", "plan_ref", "task_ref", "supersedes_packet_ref", "logical_worker_actor_id", "attempt", "work_lease_ref", "expected_goal_fence_epoch", "expected_pause_epoch", "authority_ids", "capability_ids", "allowed_resource_paths", "effect_keys", "privacy_class_id", "egress_class_id", "authority_policy_ref", "privacy_policy_ref", "egress_policy_ref", "verifier_policy_ref", "constitution_policy_ref", "route_assignment_ref", "budget_reservation_ref", "budget_limits", "source_digests", "gate_requirements", "allowed_action_ids", "prohibition_ids", "inherited_non_goals", "output_schema_digest", "deadline_logical_time", "checkpoint_ref"},
    "worker-result": {"work_packet_ref", "candidate_digest", "evidence_digests", "output_digest", "observed_effect_ref", "disposition"},
}

EVENT_PRIMARY_TYPES = {
    "OwnerIntentRecorded": "owner-intent", "GoalSpecAccepted": "goal-spec",
    "GoalSpecAmended": "goal-spec-amendment",
    "OwnerVerifierExceptionRecorded": "owner-verifier-exception",
    "ArmRunStarted": "arm-run", "PlanRevisionAdmitted": "plan-revision",
    "WorkPacketDerived": "work-packet", "WorkLeaseReplaced": "work-lease",
    "ExecutiveLeaseReplaced": "executive-lease",
    "RouteAssignmentReplaced": "route-assignment",
    "CapacityObservationRecorded": "capacity-observation",
    "CheckpointRecorded": "checkpoint", "BudgetReserved": "budget-reservation",
    "WorkerResultRecorded": "worker-result", "GateResultRecorded": "gate-result",
    "RetryAdmitted": "retry-decision", "ReplanAdmitted": "replan-decision",
    "BlockerRaised": "blocker", "EscalationRaised": "escalation",
    "PlanVerifierDecisionRecorded": "plan-verifier-decision",
    "PauseApplied": "pause-directive", "EffectObservationRecorded": "effect-observation",
    "PlanItemDisposed": "disposition", "PacketFenced": "disposition",
    "LeaseFenced": "disposition", "EffectDisposed": "disposition",
    "EvidenceDisposed": "disposition",
}

SIMPLE_COMMAND_TYPES = {
    "record-owner-intent": "owner-intent", "accept-goal-spec": "goal-spec",
    "propose-retry": "retry-decision", "raise-blocker": "blocker",
    "raise-escalation": "escalation", "submit-worker-result": "worker-result",
    "submit-gate-result": "gate-result",
    "submit-plan-verifier-decision": "plan-verifier-decision",
    "record-owner-verifier-exception": "owner-verifier-exception",
    "record-capacity-observation": "capacity-observation",
    "record-checkpoint": "checkpoint", "reserve-budget": "budget-reservation",
    "record-effect-observation": "effect-observation", "apply-pause": "pause-directive",
}
COMMAND_COMPOSITE_FIELDS = {
    "start-arm-run": {"executive_lease", "arm_run"},
    "amend-goal-spec": {"new_goal_spec", "amendment", "replacement_plan_revision", "plan_transition", "task_nodes", "arm_proposal_attestation_id"},
    "propose-plan-revision": {"plan_revision", "plan_transition", "task_nodes"},
    "derive-work-packet": {"task_ref", "attempt", "work_lease", "route_assignment", "budget_reservation_ref", "expected_work_packet_digest"},
    "replace-work-lease": {"old_lease_ref", "new_lease"},
    "replace-executive-lease": {"old_lease_ref", "new_lease"},
    "replace-route": {"old_route_ref", "new_route", "checkpoint_ref", "expected_new_packet_digest"},
    "propose-replan": {"decision", "new_plan_revision", "transition", "task_nodes", "route_assignments", "budget_reservations"},
}
COMMAND_RECORD_FIELDS = {
    "start-arm-run": {"executive_lease": "executive-lease", "arm_run": "arm-run"},
    "amend-goal-spec": {"new_goal_spec": "goal-spec", "amendment": "goal-spec-amendment", "replacement_plan_revision": "plan-revision", "plan_transition": "plan-transition"},
    "propose-plan-revision": {"plan_revision": "plan-revision", "plan_transition": "plan-transition"},
    "derive-work-packet": {"work_lease": "work-lease", "route_assignment": "route-assignment"},
    "replace-work-lease": {"new_lease": "work-lease"},
    "replace-executive-lease": {"new_lease": "executive-lease"},
    "replace-route": {"new_route": "route-assignment"},
    "propose-replan": {"decision": "replan-decision", "new_plan_revision": "plan-revision", "transition": "plan-transition"},
}
COMMAND_RECORD_LIST_FIELDS = {
    "amend-goal-spec": {"task_nodes": "task-node"},
    "propose-plan-revision": {"task_nodes": "task-node"},
    "propose-replan": {"task_nodes": "task-node", "route_assignments": "route-assignment", "budget_reservations": "budget-reservation"},
}

EVENT_RELATED_RULES = {
    "ArmRunStarted": ({"executive-lease"}, 1, 1),
    "GoalSpecAmended": ({"goal-spec"}, 1, 1),
    "PlanRevisionAdmitted": ({"plan-transition", "task-node"}, 2, 257),
    "ReplanAdmitted": ({"route-assignment", "budget-reservation"}, 2, 512),
    "WorkPacketDerived": ({"route-assignment", "work-lease"}, 0, 2),
}

OBJECT_REF_FIELDS = {"object_type", "id", "version", "content_digest"}
LEASE_REF_FIELDS = {"lease_id", "lease_epoch", "content_digest"}
POLICY_REF_FIELDS = {"policy_id", "policy_version", "content_digest"}
RECEIPT_IDENTITY_FIELDS = {"receipt_id", "command_id", "command_digest"}
BUDGET_FIELDS = {"model_turns", "attempts", "tokens", "money_minor", "cpu_ms", "memory_bytes", "output_bytes"}
DISPOSITION_FIELDS = {"object_ref", "disposition", "replacement_ref", "reason_digest"}
DEPENDENCY_EDGE_FIELDS = {"from_node_id", "to_node_id"}
EVIDENCE_REF_FIELDS = {"evidence_id", "evidence_type", "locator", "content_digest", "schema_digest"}
GATE_REQUIREMENT_FIELDS = {"gate_id", "procedure_digest", "evidence_schema_digest", "candidate_binding_digest", "verifier_policy_digest", "assigned_verifier_actor_id"}
INDEPENDENCE_FIELDS = {"model_family", "provider", "host", "session", "evidence_store", "implementation_actor_id", "verifier_actor_id", "missing_dimensions"}
CANONICAL_DIFF_ENTRY_FIELDS = {"path_segments", "old_value", "new_value"}
CANONICAL_VALUE_FIELDS = {"state", "digest"}
GOAL_COMPATIBILITY_REF_FIELDS = {"goal_id", "version", "content_digest", "fence_epoch"}
PRIOR_RESULT_FIELDS = {"state", "candidate_digest", "evidence_digests", "gate_result_digests", "plan_verifier_decision_digest", "assurance_grade"}
PRIOR_EFFECT_FIELDS = {"state", "effect_id", "intent_digest", "receipt_digest"}
COMPATIBILITY_INPUT_FIELDS = {"compatibility_schema_version", "old_goal_ref", "new_goal_ref", "old_node", "new_node", "replacement_node_id", "replacement_node_digest", "prior_result", "prior_effect", "consumed_budget"}
NODE_COMPATIBILITY_FIELDS = {"node_id", "node_version", "node_digest", "semantic_definition_digest", "output_schema_digest", "dependency_node_ids", "input_digests", "source_digests", "read_resource_paths", "write_resource_paths", "effect_keys", "authority_ids", "capability_ids", "allowed_action_ids", "prohibition_ids", "route_ids", "route_capability_ids", "account_class_ids", "capacity_pool_ids", "privacy_class_id", "egress_class_id", "authority_policy_digest", "privacy_policy_digest", "egress_policy_digest", "budget_limits", "gate_requirements", "retry_policy_digest", "verifier_policy_digest", "constitution_policy_digest", "terminal_contribution_digest", "retry_maximum"}
ERROR_WITNESS_FIELDS = {"witness_schema_version", "error_code", "object_ids", "dependency_edges", "field_paths", "content_digest"}
NOVELTY_COMMON_FIELDS = {"novelty_schema_version", "delta_id", "prior_attempt_digest", "addresses_failure_ids", "old_descriptor_digest", "new_descriptor_digest", "canonical_diff", "canonical_diff_digest", "delta_digest", "kind"}
NOVELTY_KIND_FIELDS = {
    "evidence-added": {"old_evidence_refs", "new_evidence_refs"},
    "hypothesis-replaced": {"old_hypothesis", "new_hypothesis", "changed_proposition_ids"},
    "strategy-changed": {"old_strategy", "new_strategy", "changed_operation_ids"},
    "route-capability-changed": {"old_route_descriptor", "new_route_descriptor", "newly_observed_capability_ids"},
    "task-narrowed": {"old_scope", "new_scope"},
    "dependency-repaired": {"predicate_id", "predicate_version", "predicate_input_schema_digest", "old_input", "new_input", "old_result_digest", "repair_receipt_digest", "new_result_digest"},
    "owner-amended": {"old_goal_ref", "new_goal_ref", "accepted_owner_command_receipt_digest", "amendment_disposition_digest", "retained_node_id", "compatibility_input_digest"},
}


class M1AError(ValueError):
    """A closed, stable M1A failure rather than a host-language parser exception."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(detail or code)
        self.code = code
        self.detail = detail


def _parse_int(raw: str) -> int:
    if raw == "-0":
        raise M1AError("E-SCHEMA-INVALID", "lexical negative zero")
    digits = raw[1:] if raw.startswith("-") else raw
    if len(digits) > 16:
        raise M1AError("E-SCHEMA-BOUND", "integer bound exceeded")
    try:
        value = int(raw)
    except ValueError as exc:
        raise M1AError("E-SCHEMA-INVALID", "invalid integer") from exc
    if abs(value) > MAX_IJSON_INTEGER:
        raise M1AError("E-SCHEMA-BOUND", "integer bound exceeded")
    return value


def _reject_float(_raw: str):
    raise M1AError("E-SCHEMA-INVALID", "floating-point value")


def _reject_constant(raw: str):
    raise M1AError("E-SCHEMA-INVALID", f"non-I-JSON constant {raw}")


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise M1AError("E-SCHEMA-DUPLICATE", f"duplicate key {key}")
        result[key] = value
    return result


def _check_tree(value, *, depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise M1AError("E-SCHEMA-BOUND", "nesting depth exceeded")
    if isinstance(value, str):
        if "\x00" in value:
            raise M1AError("E-SCHEMA-INVALID", "NUL string")
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise M1AError("E-SCHEMA-INVALID", "unpaired surrogate") from exc
    elif isinstance(value, bool) or value is None:
        return
    elif isinstance(value, int):
        if abs(value) > MAX_IJSON_INTEGER:
            raise M1AError("E-SCHEMA-BOUND", "integer bound exceeded")
    elif isinstance(value, list):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise M1AError("E-SCHEMA-BOUND", "array count exceeded")
        for item in value:
            _check_tree(item, depth=depth + 1)
    elif isinstance(value, dict):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise M1AError("E-SCHEMA-BOUND", "object count exceeded")
        for key, item in value.items():
            _check_tree(key, depth=depth + 1)
            _check_tree(item, depth=depth + 1)
    else:
        raise M1AError("E-SCHEMA-INVALID", "unsupported JSON value")


def strict_loads(raw: str | bytes):
    if isinstance(raw, bytes):
        if len(raw) > MAX_INPUT_BYTES:
            raise M1AError("E-SCHEMA-BOUND", "input byte bound exceeded")
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise M1AError("E-SCHEMA-INVALID", "invalid UTF-8") from exc
    elif isinstance(raw, str):
        try:
            size = len(raw.encode("utf-8", errors="strict"))
        except UnicodeEncodeError as exc:
            raise M1AError("E-SCHEMA-INVALID", "unpaired surrogate") from exc
        if size > MAX_INPUT_BYTES:
            raise M1AError("E-SCHEMA-BOUND", "input byte bound exceeded")
        text = raw
    else:
        raise M1AError("E-SCHEMA-INVALID", "input must be bytes or text")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_int=_parse_int,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except M1AError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise M1AError("E-SCHEMA-INVALID", "malformed JSON") from exc
    _check_tree(value)
    return value


def _require_closed(value: dict, allowed: set[str]) -> None:
    unknown = set(value) - allowed
    if unknown:
        raise M1AError("E-SCHEMA-UNKNOWN-FIELD", min(unknown))
    missing = allowed - set(value)
    if missing:
        raise M1AError("E-SCHEMA-MISSING-FIELD", min(missing))


def _require_dict(value, detail: str) -> dict:
    if not isinstance(value, dict):
        raise M1AError("E-SCHEMA-INVALID", detail)
    return value


def _validate_structural_objects(value) -> None:
    """Recursively close the common nested record structures used by M1A."""

    if isinstance(value, list):
        for item in value:
            _validate_structural_objects(item)
        return
    if not isinstance(value, dict):
        return
    keys = set(value)
    if "receipt_schema_version" in value:
        for item in value.values():
            _validate_structural_objects(item)
        return
    if "schema_version" in value and "object_type" in value:
        validate_domain_record(value)
        return
    if "novelty_schema_version" in value:
        if value.get("novelty_schema_version") != "novelty-delta-1":
            raise M1AError("E-SCHEMA-UNKNOWN-VERSION", str(value.get("novelty_schema_version")))
        kind_fields = NOVELTY_KIND_FIELDS.get(value.get("kind"))
        if kind_fields is None:
            raise M1AError("E-SCHEMA-INVALID", "novelty kind")
        _require_closed(value, NOVELTY_COMMON_FIELDS | kind_fields)
    signatures = (
        ("lease_id", LEASE_REF_FIELDS), ("policy_id", POLICY_REF_FIELDS),
        ("receipt_id", RECEIPT_IDENTITY_FIELDS),
        ("evidence_id", EVIDENCE_REF_FIELDS),
        ("gate_id", GATE_REQUIREMENT_FIELDS),
        ("compatibility_schema_version", COMPATIBILITY_INPUT_FIELDS),
        ("node_id", NODE_COMPATIBILITY_FIELDS),
        ("witness_schema_version", ERROR_WITNESS_FIELDS),
    )
    for discriminator, fields in signatures:
        if discriminator in value:
            _require_closed(value, fields)
            break
    else:
        if OBJECT_REF_FIELDS.issubset(keys):
            _require_closed(value, OBJECT_REF_FIELDS)
        elif {"object_type", "id", "version"}.issubset(keys):
            _require_closed(value, {"object_type", "id", "version"})
        elif {"object_ref", "disposition", "replacement_ref", "reason_digest"}.issubset(keys):
            _require_closed(value, DISPOSITION_FIELDS)
        elif {"from_node_id", "to_node_id"}.issubset(keys):
            _require_closed(value, DEPENDENCY_EDGE_FIELDS)
        elif BUDGET_FIELDS.issubset(keys):
            _require_closed(value, BUDGET_FIELDS)
        elif INDEPENDENCE_FIELDS.issubset(keys):
            _require_closed(value, INDEPENDENCE_FIELDS)
        elif CANONICAL_DIFF_ENTRY_FIELDS.issubset(keys):
            _require_closed(value, CANONICAL_DIFF_ENTRY_FIELDS)
        elif CANONICAL_VALUE_FIELDS.issubset(keys):
            _require_closed(value, CANONICAL_VALUE_FIELDS)
        elif GOAL_COMPATIBILITY_REF_FIELDS.issubset(keys):
            _require_closed(value, GOAL_COMPATIBILITY_REF_FIELDS)
        elif PRIOR_RESULT_FIELDS.issubset(keys):
            _require_closed(value, PRIOR_RESULT_FIELDS)
        elif PRIOR_EFFECT_FIELDS.issubset(keys):
            _require_closed(value, PRIOR_EFFECT_FIELDS)
    for item in value.values():
        _validate_structural_objects(item)


def validate_domain_record(value: dict) -> None:
    """Validate a registered domain arm without consulting ambient schema files."""

    record = _require_dict(value, "domain record must be an object")
    object_type = record.get("object_type")
    expected_version = DOMAIN_VERSIONS.get(object_type)
    if expected_version is None or record.get("schema_version") != expected_version:
        raise M1AError(
            "E-SCHEMA-UNKNOWN-VERSION",
            f"{object_type!s}/{record.get('schema_version')!s}",
        )
    _require_closed(record, DOMAIN_FIELDS)
    payload = _require_dict(record.get("payload"), "domain payload must be an object")
    _require_closed(payload, DOMAIN_PAYLOAD_FIELDS[object_type])
    if not isinstance(record.get("version"), int) or isinstance(record.get("version"), bool) or record["version"] < 1:
        raise M1AError("E-SCHEMA-INVALID", "record version")
    if not isinstance(record.get("created_logical_time"), int) or isinstance(record.get("created_logical_time"), bool) or record["created_logical_time"] < 0:
        raise M1AError("E-SCHEMA-INVALID", "record logical time")
    _check_tree(record)
    _validate_structural_objects(payload)


def validate_event_envelope(value: dict) -> None:
    event = _require_dict(value, "event must be an object")
    if event.get("event_schema_version") != "m1a-event-1":
        raise M1AError("E-SCHEMA-UNKNOWN-VERSION", str(event.get("event_schema_version")))
    _require_closed(event, EVENT_FIELDS)
    expected_primary = EVENT_PRIMARY_TYPES.get(event.get("event_type"))
    if expected_primary is None:
        raise M1AError("E-SCHEMA-UNKNOWN-VERSION", str(event.get("event_type")))
    primary = _require_dict(event.get("primary_record"), "primary record")
    validate_domain_record(primary)
    if primary["object_type"] != expected_primary:
        raise M1AError("E-SCHEMA-INVALID", "event primary record discriminator")
    related = event.get("related_records")
    if not isinstance(related, list):
        raise M1AError("E-SCHEMA-INVALID", "related records")
    for record in related:
        validate_domain_record(record)
    rule = EVENT_RELATED_RULES.get(event["event_type"])
    if rule is None:
        if related:
            raise M1AError("E-SCHEMA-INVALID", "event related record cardinality")
    else:
        allowed, minimum, maximum = rule
        related_types = {record["object_type"] for record in related}
        if (not minimum <= len(related) <= maximum
                or not related_types.issubset(allowed)
                or (related and related_types != allowed)
                or (not related and minimum > 0)):
            raise M1AError("E-SCHEMA-INVALID", "event related record discriminator")
    ordered = sorted(related, key=lambda record: (record["object_type"], record["id"], record["version"]))
    if related != ordered:
        raise M1AError("E-SCHEMA-INVALID", "event related record order")


def validate_command_envelope(value: dict) -> None:
    command = _require_dict(value, "command must be an object")
    if command.get("command_schema_version") != "m1a-command-1":
        raise M1AError("E-SCHEMA-UNKNOWN-VERSION", str(command.get("command_schema_version")))
    _require_closed(command, COMMAND_FIELDS)
    _check_tree(command)
    command_type = command.get("command_type")
    payload = _require_dict(command.get("payload"), "command payload")
    simple_type = SIMPLE_COMMAND_TYPES.get(command_type)
    if simple_type is not None:
        validate_domain_record(payload)
        if payload["object_type"] != simple_type:
            raise M1AError("E-SCHEMA-INVALID", "command payload discriminator")
        return
    fields = COMMAND_COMPOSITE_FIELDS.get(command_type)
    if fields is None:
        raise M1AError("E-SCHEMA-UNKNOWN-VERSION", str(command_type))
    _require_closed(payload, fields)
    for field, object_type in COMMAND_RECORD_FIELDS[command_type].items():
        record = _require_dict(payload[field], field)
        validate_domain_record(record)
        if record["object_type"] != object_type:
            raise M1AError("E-SCHEMA-INVALID", f"{field} discriminator")
    for field, object_type in COMMAND_RECORD_LIST_FIELDS.get(command_type, {}).items():
        records = payload[field]
        if not isinstance(records, list):
            raise M1AError("E-SCHEMA-INVALID", field)
        for record in records:
            validate_domain_record(record)
            if record["object_type"] != object_type:
                raise M1AError("E-SCHEMA-INVALID", f"{field} discriminator")
    _validate_structural_objects(payload)


def validate_receipt(value: dict) -> None:
    receipt = _require_dict(value, "receipt must be an object")
    if receipt.get("receipt_schema_version") != "m1a-receipt-1":
        raise M1AError("E-SCHEMA-UNKNOWN-VERSION", str(receipt.get("receipt_schema_version")))
    _require_closed(receipt, RECEIPT_FIELDS)
    if digest(receipt, omit_content_digest=True) != receipt.get("content_digest"):
        raise M1AError("E-DIGEST-MISMATCH", "receipt journal digest")
    disposition = receipt.get("disposition")
    if disposition not in {"accepted", "refused", "duplicate", "conflict"}:
        raise M1AError("E-SCHEMA-INVALID", "receipt disposition")
    if disposition == "accepted":
        if (receipt["primary_error"] is not None or receipt["related_errors"]
                or receipt["witness"] is not None or not receipt["event_ids"]
                or not isinstance(receipt["first_event_sequence"], int)
                or not isinstance(receipt["last_event_sequence"], int)):
            raise M1AError("E-SCHEMA-INVALID", "accepted receipt shape")
    elif disposition in {"refused", "conflict"}:
        if (receipt["primary_error"] is None or receipt["event_ids"]
                or receipt["first_event_sequence"] is not None
                or receipt["last_event_sequence"] is not None):
            raise M1AError("E-SCHEMA-INVALID", "refused receipt shape")
    elif (receipt["primary_error"] is not None or receipt["related_errors"]
          or receipt["witness"] is not None or receipt["event_ids"]
          or receipt["first_event_sequence"] is not None
          or receipt["last_event_sequence"] is not None):
        raise M1AError("E-SCHEMA-INVALID", "duplicate receipt shape")
    _validate_structural_objects(receipt)


def validate_projection(value: dict) -> None:
    projection = _require_dict(value, "projection must be an object")
    if projection.get("projection_schema_version") != "m1a-projection-1":
        raise M1AError("E-SCHEMA-UNKNOWN-VERSION", str(projection.get("projection_schema_version")))
    _require_closed(projection, PROJECTION_FIELDS)
    if digest(projection, omit_content_digest=True) != projection.get("content_digest"):
        raise M1AError("E-DIGEST-MISMATCH", "projection content digest")
    for record in projection.get("records", []):
        validate_domain_record(record)
        if digest(record, omit_content_digest=True) != record.get("content_digest"):
            raise M1AError("E-DIGEST-MISMATCH", "projection record digest")
    _validate_structural_objects(projection)


def decode(raw: str | bytes, schema_epoch: str = "m1a-1"):
    """Decode one closed M1A envelope without observing ambient schema files."""

    if schema_epoch != "m1a-1":
        raise M1AError("E-SCHEMA-UNKNOWN-VERSION", schema_epoch)
    value = strict_loads(raw)
    if not isinstance(value, dict):
        raise M1AError("E-SCHEMA-INVALID", "root must be an object")
    if "command_schema_version" in value:
        validate_command_envelope(value)
    elif "event_schema_version" in value:
        validate_event_envelope(value)
    elif "schema_version" in value or "object_type" in value:
        if "schema_version" not in value:
            raise M1AError("E-SCHEMA-MISSING-FIELD", "schema_version")
        validate_domain_record(value)
    else:
        raise M1AError("E-SCHEMA-MISSING-FIELD", "registered envelope discriminator")
    return value


def _utf16_key(value: str) -> bytes:
    return value.encode("utf-16be")


def canonical_bytes(value) -> bytes:
    """Return the RFC 8785 bytes for M1A's integer-only I-JSON subset."""

    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > MAX_IJSON_INTEGER:
            raise M1AError("E-SCHEMA-BOUND", "integer bound exceeded")
        return str(value).encode("ascii")
    if isinstance(value, str):
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise M1AError("E-SCHEMA-INVALID", "unpaired surrogate") from exc
        return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if isinstance(value, list):
        return b"[" + b",".join(canonical_bytes(item) for item in value) + b"]"
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise M1AError("E-SCHEMA-INVALID", "object key must be text")
        keys = sorted(value, key=_utf16_key)
        return b"{" + b",".join(
            canonical_bytes(key) + b":" + canonical_bytes(value[key]) for key in keys
        ) + b"}"
    raise M1AError("E-SCHEMA-INVALID", "unsupported canonical value")


def digest(value, *, omit_content_digest: bool = False) -> str:
    operand = copy.deepcopy(value)
    if omit_content_digest and isinstance(operand, dict):
        operand.pop("content_digest", None)
    return hashlib.sha256(canonical_bytes(operand)).hexdigest()


def seal(value: dict) -> dict:
    result = copy.deepcopy(value)
    result.pop("content_digest", None)
    result["content_digest"] = digest(result)
    return result
