#!/usr/bin/env python3
"""Mechanically materialize the closed M1A Draft 2020-12 schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path


MAX_UINT = 9_007_199_254_740_991
MAX_POS_INT = 2_147_483_647


def ref(name: str) -> dict:
    return {"$ref": f"#/$defs/{name}"}


def const(value) -> dict:
    return {"const": value}


def enum(*values: str) -> dict:
    return {"type": "string", "enum": list(values)}


def closed(properties: dict, *, required: list[str] | None = None, **extra) -> dict:
    result = {
        "type": "object",
        "additionalProperties": False,
        "required": required if required is not None else list(properties),
        "properties": properties,
    }
    result.update(extra)
    return result


def array(
    item: dict,
    *,
    minimum: int = 0,
    maximum: int = 256,
    unique: bool = True,
    sorted_by: str | list[str] | None = None,
) -> dict:
    result = {
        "type": "array",
        "minItems": minimum,
        "maxItems": maximum,
        "items": item,
    }
    if unique:
        result["uniqueItems"] = True
    if sorted_by is not None:
        result["x-sortedBy"] = sorted_by
    return result


def nullable(item: dict) -> dict:
    return {"anyOf": [item, {"type": "null"}]}


def record_schema(object_type: str, schema_version: str, payload: dict) -> dict:
    return closed(
        {
            "object_type": const(object_type),
            "schema_version": const(schema_version),
            "id": ref("id"),
            "version": ref("pos_int"),
            "created_by_actor_id": ref("id"),
            "created_under_lease": nullable(ref("lease_ref")),
            "causation_id": ref("id"),
            "correlation_id": ref("id"),
            "created_logical_time": ref("logical_time"),
            "payload": payload,
            "content_digest": ref("digest"),
        },
        **{"x-maxCanonicalBytes": 262144},
    )


def build_schema() -> dict:
    d: dict[str, dict] = {}

    d["id"] = {
        "type": "string",
        "pattern": r"^[A-Z][A-Z0-9]*(?:-[A-Za-z0-9][A-Za-z0-9._-]*)+$",
        "minLength": 3,
        "maxLength": 128,
    }
    d["command_id"] = {**d["id"], "maxLength": 120}
    d["token"] = {
        "type": "string",
        "pattern": r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$",
        "minLength": 1,
        "maxLength": 64,
    }
    d["digest"] = {"type": "string", "pattern": r"^[0-9a-f]{64}$"}
    d["text"] = {
        "type": "string",
        "maxLength": 4096,
        "pattern": r"^[^\u0000\uD800-\uDFFF]*$",
        "x-maxUtf8Bytes": 4096,
    }
    d["nonempty_text"] = {**d["text"], "minLength": 1}
    d["json_input_text"] = {
        "type": "string",
        "maxLength": 262144,
        "pattern": r"^[^\u0000\uD800-\uDFFF]*$",
        "x-maxUtf8Bytes": 262144,
    }
    d["uint"] = {"type": "integer", "minimum": 0, "maximum": MAX_UINT}
    d["pos_int"] = {"type": "integer", "minimum": 1, "maximum": MAX_POS_INT}
    d["logical_time"] = ref("uint")
    d["id_set"] = array(ref("id"), sorted_by="$value")
    d["digest_set"] = array(ref("digest"), sorted_by="$value")
    d["token_set"] = array(ref("token"), sorted_by="$value")
    d["text_set"] = array(ref("text"), sorted_by="$value")
    d["resource_path"] = {
        "type": "string",
        "pattern": r"^[a-z0-9][a-z0-9._-]*(?:/[a-z0-9][a-z0-9._-]*)*$",
        "maxLength": 4096,
        "x-maxUtf8Bytes": 4096,
    }
    d["resource_path_set"] = array(ref("resource_path"), sorted_by="$value")

    command_types = [
        "record-owner-intent",
        "accept-goal-spec",
        "amend-goal-spec",
        "record-owner-verifier-exception",
        "start-arm-run",
        "propose-plan-revision",
        "derive-work-packet",
        "replace-work-lease",
        "replace-executive-lease",
        "replace-route",
        "record-capacity-observation",
        "record-checkpoint",
        "reserve-budget",
        "submit-worker-result",
        "submit-gate-result",
        "propose-retry",
        "propose-replan",
        "raise-blocker",
        "raise-escalation",
        "submit-plan-verifier-decision",
        "apply-pause",
        "record-effect-observation",
    ]
    event_types = [
        "OwnerIntentRecorded",
        "GoalSpecAccepted",
        "GoalSpecAmended",
        "OwnerVerifierExceptionRecorded",
        "ArmRunStarted",
        "PlanRevisionAdmitted",
        "WorkPacketDerived",
        "WorkLeaseReplaced",
        "ExecutiveLeaseReplaced",
        "RouteAssignmentReplaced",
        "CapacityObservationRecorded",
        "CheckpointRecorded",
        "BudgetReserved",
        "WorkerResultRecorded",
        "GateResultRecorded",
        "RetryAdmitted",
        "ReplanAdmitted",
        "BlockerRaised",
        "EscalationRaised",
        "PlanVerifierDecisionRecorded",
        "PauseApplied",
        "EffectObservationRecorded",
        "PlanItemDisposed",
        "PacketFenced",
        "LeaseFenced",
        "EffectDisposed",
        "EvidenceDisposed",
    ]
    error_codes = [
        "E-SCHEMA-UNKNOWN-FIELD",
        "E-SCHEMA-MISSING-FIELD",
        "E-SCHEMA-UNKNOWN-VERSION",
        "E-SCHEMA-DUPLICATE",
        "E-SCHEMA-BOUND",
        "E-DIGEST-MISMATCH",
        "E-AUTH-MISSING",
        "E-AUTH-PARENT-MUTATION",
        "E-AUTH-ROLE",
        "E-SCOPE-WIDEN",
        "E-BUDGET-WIDEN",
        "E-DAG-CYCLE",
        "E-DAG-DEPENDENCY",
        "E-DAG-CONFLICT",
        "E-STALE-GOAL",
        "E-STALE-PLAN",
        "E-STALE-LEASE",
        "E-GATE-MISSING",
        "E-VERIFIER-MISSING",
        "E-RETRY-NONNOVEL",
        "E-RETRY-EXHAUSTED",
        "E-ROUTE-SPEND",
        "E-PAUSED",
        "E-EFFECT-AMBIGUOUS",
        "E-IDEMPOTENCY-CONFLICT",
        "E-AMENDMENT-INCOMPLETE",
        "E-POLICY-UNKNOWN",
    ]
    d["command_type"] = enum(*command_types)
    d["event_type"] = enum(*event_types)
    d["error_code"] = enum(*error_codes)
    d["error_code_set"] = array(ref("error_code"), maximum=64, sorted_by="$value")
    witness_edge = closed({"from_node_id": ref("id"), "to_node_id": ref("id")})
    d["error_witness"] = closed(
        {
            "witness_schema_version": const("m1a-error-witness-1"),
            "error_code": ref("error_code"),
            "object_ids": ref("id_set"),
            "dependency_edges": array(
                witness_edge, sorted_by=["from_node_id", "to_node_id"]
            ),
            "field_paths": ref("text_set"),
            "content_digest": ref("digest"),
        }
    )

    d["object_ref"] = closed(
        {
            "object_type": ref("token"),
            "id": ref("id"),
            "version": ref("pos_int"),
            "content_digest": ref("digest"),
        }
    )
    d["plan_identity_ref"] = closed(
        {"object_type": const("plan-revision"), "id": ref("id"), "version": ref("pos_int")}
    )
    d["receipt_identity"] = closed(
        {"receipt_id": ref("id"), "command_id": ref("command_id"), "command_digest": ref("digest")}
    )
    d["policy_ref"] = closed(
        {"policy_id": ref("id"), "policy_version": ref("pos_int"), "content_digest": ref("digest")}
    )
    d["lease_ref"] = closed(
        {"lease_id": ref("id"), "lease_epoch": ref("uint"), "content_digest": ref("digest")}
    )
    d["budget_vector"] = closed(
        {
            "model_turns": ref("uint"),
            "attempts": ref("uint"),
            "tokens": ref("uint"),
            "money_minor": ref("uint"),
            "cpu_ms": ref("uint"),
            "memory_bytes": ref("uint"),
            "output_bytes": ref("uint"),
        }
    )
    d["gate_requirement"] = closed(
        {
            "gate_id": ref("id"),
            "procedure_digest": ref("digest"),
            "evidence_schema_digest": ref("digest"),
            "candidate_binding_digest": ref("digest"),
            "verifier_policy_digest": ref("digest"),
            "assigned_verifier_actor_id": ref("id"),
        }
    )
    d["gate_requirement_set"] = array(ref("gate_requirement"), sorted_by="gate_id")
    d["independence_projection"] = closed(
        {
            "model_family": ref("token"),
            "provider": ref("token"),
            "host": ref("token"),
            "session": ref("token"),
            "evidence_store": ref("token"),
            "implementation_actor_id": ref("id"),
            "verifier_actor_id": ref("id"),
            "missing_dimensions": ref("token_set"),
        }
    )
    d["disposition"] = closed(
        {
            "object_ref": ref("object_ref"),
            "disposition": enum(
                "retain-definition", "retain-terminal", "invalidate", "quarantine",
                "supersede", "cancel", "fence",
            ),
            "replacement_ref": nullable(ref("object_ref")),
            "reason_digest": ref("digest"),
        }
    )
    d["disposition_set"] = array(
        ref("disposition"), sorted_by=["object_ref.object_type", "object_ref.id", "object_ref.version"]
    )
    d["decode_failure"] = closed(
        {
            "decode_failure_schema_version": const("m1a-decode-failure-1"),
            "schema_epoch": const("m1a-1"),
            "raw_input_digest": ref("digest"),
            "primary_error": ref("error_code"),
            "related_errors": ref("error_code_set"),
            "content_digest": ref("digest"),
        }
    )
    d["genesis_config"] = closed(
        {
            "genesis_schema_version": const("m1a-genesis-1"),
            "stream_id": ref("id"),
            "current_pause_policy_ref": ref("policy_ref"),
            "current_pause_epoch": ref("uint"),
        }
    )
    d["authority_attestation"] = closed(
        {
            "attestation_schema_version": const("m1a-fixture-authority-1"),
            "attestation_id": ref("id"),
            "actor_id": ref("id"),
            "actor_role": enum("owner", "head", "arm", "worker", "verifier", "kernel-fixture-gate"),
            "allowed_command_types": array(ref("command_type")),
            "candidate_digest": ref("digest"),
            "authority_policy_ref": ref("policy_ref"),
            "constitution_policy_ref": ref("policy_ref"),
            "valid_from_logical_time": ref("logical_time"),
            "expires_logical_time": ref("logical_time"),
            "content_digest": ref("digest"),
        }
    )

    relation_edge = closed({"less_or_equal_id": ref("id"), "greater_or_equal_id": ref("id")})
    accepted_evidence = closed({"failure_id": ref("id"), "evidence_types": ref("token_set")})
    failure_capability = closed({"failure_id": ref("id"), "capability_ids": ref("id_set")})
    policy_props = {
        "policy_schema_version": const("m1a-policy-fixture-1"),
        "policy_id": ref("id"),
        "policy_version": ref("pos_int"),
        "policy_kind": enum(
            "authority", "privacy-egress", "route-envelope", "novelty", "verifier",
            "constitution", "pause", "retry",
        ),
        "allowed_roles": ref("token_set"),
        "allowed_command_types": array(ref("command_type")),
        "privacy_class_ids": ref("id_set"),
        "privacy_at_most_edges": array(
            relation_edge, sorted_by=["less_or_equal_id", "greater_or_equal_id"]
        ),
        "egress_class_ids": ref("id_set"),
        "egress_at_most_edges": array(
            relation_edge, sorted_by=["less_or_equal_id", "greater_or_equal_id"]
        ),
        "route_ids": ref("id_set"),
        "account_class_ids": ref("id_set"),
        "capacity_pool_ids": ref("id_set"),
        "allowed_spend_classes": array(enum("none", "included")),
        "accepted_evidence_types": array(accepted_evidence, sorted_by="failure_id"),
        "failure_capability_requirements": array(failure_capability, sorted_by="failure_id"),
        "required_verifier_dimensions": ref("token_set"),
        "owner_verifier_exception_allowed": {"type": "boolean"},
        "operative_pause_mode": const("current-immediate"),
        "representable_future_pause_modes": array(enum("checkpoint", "interrupt", "drain")),
        "retry_maximum": ref("uint"),
        "content_digest": ref("digest"),
    }
    policy = closed(policy_props)
    array_fields = [
        "allowed_roles", "allowed_command_types", "privacy_class_ids", "privacy_at_most_edges",
        "egress_class_ids", "egress_at_most_edges", "route_ids", "account_class_ids",
        "capacity_pool_ids", "allowed_spend_classes", "accepted_evidence_types",
        "failure_capability_requirements", "required_verifier_dimensions",
        "representable_future_pause_modes",
    ]

    def policy_arm(kind: str, active: list[str], *, retry: bool = False, owner_bool: bool = False) -> dict:
        props: dict[str, dict] = {"policy_kind": const(kind)}
        for field in array_fields:
            props[field] = {"minItems": 1} if field in active else {"maxItems": 0}
        props["retry_maximum"] = {"minimum": 1} if retry else const(0)
        if not owner_bool:
            props["owner_verifier_exception_allowed"] = const(False)
        return {"properties": props, "required": ["policy_kind"]}

    policy["allOf"] = [{
        "oneOf": [
            policy_arm("authority", ["allowed_roles", "allowed_command_types"]),
            policy_arm(
                "privacy-egress",
                ["privacy_class_ids", "privacy_at_most_edges", "egress_class_ids", "egress_at_most_edges"],
            ),
            policy_arm(
                "route-envelope",
                ["route_ids", "account_class_ids", "capacity_pool_ids", "allowed_spend_classes"],
            ),
            policy_arm(
                "novelty",
                [
                    "route_ids", "account_class_ids", "capacity_pool_ids", "allowed_spend_classes",
                    "accepted_evidence_types", "failure_capability_requirements",
                ],
            ),
            policy_arm("verifier", ["required_verifier_dimensions"], owner_bool=True),
            policy_arm("constitution", [], owner_bool=True),
            policy_arm("pause", ["representable_future_pause_modes"]),
            policy_arm("retry", [], retry=True),
        ]
    }]
    d["policy_fixture"] = policy

    goal_version_ref = closed(
        {
            "goal_id": ref("id"),
            "version": ref("pos_int"),
            "content_digest": ref("digest"),
            "fence_epoch": ref("uint"),
        }
    )
    node_tuple = closed(
        {
            "node_id": ref("id"),
            "node_version": ref("pos_int"),
            "node_digest": ref("digest"),
            "semantic_definition_digest": ref("digest"),
            "output_schema_digest": ref("digest"),
            "dependency_node_ids": ref("id_set"),
            "input_digests": ref("digest_set"),
            "source_digests": ref("digest_set"),
            "read_resource_paths": ref("resource_path_set"),
            "write_resource_paths": ref("resource_path_set"),
            "effect_keys": ref("id_set"),
            "authority_ids": ref("id_set"),
            "capability_ids": ref("id_set"),
            "allowed_action_ids": ref("id_set"),
            "prohibition_ids": ref("id_set"),
            "route_ids": ref("id_set"),
            "route_capability_ids": ref("id_set"),
            "account_class_ids": ref("id_set"),
            "capacity_pool_ids": ref("id_set"),
            "privacy_class_id": ref("id"),
            "egress_class_id": ref("id"),
            "authority_policy_digest": ref("digest"),
            "privacy_policy_digest": ref("digest"),
            "egress_policy_digest": ref("digest"),
            "budget_limits": ref("budget_vector"),
            "gate_requirements": ref("gate_requirement_set"),
            "retry_policy_digest": ref("digest"),
            "verifier_policy_digest": ref("digest"),
            "constitution_policy_digest": ref("digest"),
            "terminal_contribution_digest": ref("digest"),
            "retry_maximum": ref("uint"),
        }
    )
    d["node_compatibility_tuple"] = node_tuple
    prior_result = closed(
        {
            "state": enum("result-submitted", "gate-pending", "verified", "complete", "failed"),
            "candidate_digest": ref("digest"),
            "evidence_digests": ref("digest_set"),
            "gate_result_digests": ref("digest_set"),
            "plan_verifier_decision_digest": ref("digest"),
            "assurance_grade": enum("full", "downgraded", "none"),
        }
    )
    prior_effect = closed(
        {
            "state": enum(
                "none", "prepared-undispatched", "observed-success", "observed-failure",
                "ambiguous", "reconciled",
            ),
            "effect_id": nullable(ref("id")),
            "intent_digest": nullable(ref("digest")),
            "receipt_digest": nullable(ref("digest")),
        }
    )
    d["compatibility_input"] = closed(
        {
            "compatibility_schema_version": const("compatibility-input-1"),
            "old_goal_ref": goal_version_ref,
            "new_goal_ref": goal_version_ref,
            "old_node": ref("node_compatibility_tuple"),
            "new_node": ref("node_compatibility_tuple"),
            "replacement_node_id": nullable(ref("id")),
            "replacement_node_digest": nullable(ref("digest")),
            "prior_result": nullable(prior_result),
            "prior_effect": prior_effect,
            "consumed_budget": ref("budget_vector"),
        }
    )

    d["evidence_ref"] = closed(
        {
            "evidence_id": {
                "type": "string", "pattern": r"^evidence-[a-z0-9][a-z0-9-]{0,62}$", "maxLength": 72,
            },
            "evidence_type": enum("gate-output", "fixture-observation", "synthetic-source", "repair-receipt"),
            "locator": {
                "type": "string",
                "pattern": r"^fixture://evidence/evidence-[a-z0-9][a-z0-9-]{0,62}$",
                "maxLength": 91,
            },
            "content_digest": ref("digest"),
            "schema_digest": ref("digest"),
        }
    )
    d["evidence_ref_set"] = array(ref("evidence_ref"), minimum=0, sorted_by="evidence_id")
    diff_value = {
        "oneOf": [
            closed({"state": const("present"), "digest": ref("digest")}),
            closed({"state": const("absent"), "digest": const(None)}),
        ]
    }
    d["canonical_diff_entry"] = closed(
        {
            "path_segments": array(ref("text"), maximum=64),
            "old_value": diff_value,
            "new_value": diff_value,
        }
    )
    d["canonical_diff"] = array(
        ref("canonical_diff_entry"), maximum=2048, sorted_by="path_segments"
    )

    proposition = closed(
        {
            "proposition_id": {
                "type": "string", "pattern": r"^proposition-[a-z0-9][a-z0-9-]{0,62}$",
            },
            "proposition_digest": ref("digest"),
        }
    )
    hypothesis = closed(
        {
            "hypothesis_digest": ref("digest"),
            "propositions": array(proposition, minimum=1, sorted_by="proposition_id"),
        }
    )
    operation = closed(
        {
            "operation_id": {"type": "string", "pattern": r"^operation-[a-z0-9][a-z0-9-]{0,62}$"},
            "operation_digest": ref("digest"),
        }
    )
    operation_edge = closed(
        {
            "from_operation_id": {"type": "string", "pattern": r"^operation-[a-z0-9][a-z0-9-]{0,62}$"},
            "to_operation_id": {"type": "string", "pattern": r"^operation-[a-z0-9][a-z0-9-]{0,62}$"},
        }
    )
    strategy = closed(
        {
            "strategy_digest": ref("digest"),
            "operations": array(operation, sorted_by="operation_id"),
            "edges": array(operation_edge, sorted_by=["from_operation_id", "to_operation_id"]),
            "goal_ceiling_digest": ref("digest"),
            "resource_ceiling_digest": ref("digest"),
            "effect_ceiling_digest": ref("digest"),
        }
    )
    route_descriptor = closed(
        {
            "descriptor_digest": ref("digest"),
            "route_id": ref("id"),
            "account_class_id": ref("id"),
            "capacity_pool_id": ref("id"),
            "spend_class": enum("none", "included"),
            "capability_ids": ref("id_set"),
            "observation_digest": ref("digest"),
            "allowed_envelope_digest": ref("digest"),
        }
    )
    task_scope = closed(
        {
            "scope_digest": ref("digest"),
            "authority_ids": ref("id_set"),
            "capability_ids": ref("id_set"),
            "allowed_action_ids": ref("id_set"),
            "prohibition_ids": ref("id_set"),
            "route_ids": ref("id_set"),
            "route_capability_ids": ref("id_set"),
            "account_class_ids": ref("id_set"),
            "capacity_pool_ids": ref("id_set"),
            "read_resource_paths": ref("resource_path_set"),
            "write_resource_paths": ref("resource_path_set"),
            "effect_keys": ref("id_set"),
            "privacy_class_id": ref("id"),
            "egress_class_id": ref("id"),
            "authority_policy_digest": ref("digest"),
            "privacy_policy_digest": ref("digest"),
            "egress_policy_digest": ref("digest"),
            "budget_limits": ref("budget_vector"),
            "required_output_schema_digest": ref("digest"),
            "gate_requirements": ref("gate_requirement_set"),
        }
    )
    dependency_input = closed(
        {"required_artifact_digest": ref("digest"), "observed_artifact_digests": ref("digest_set")}
    )
    novelty_common = {
        "novelty_schema_version": const("novelty-delta-1"),
        "delta_id": {"type": "string", "pattern": r"^delta-[a-z0-9][a-z0-9-]{0,62}$"},
        "prior_attempt_digest": ref("digest"),
        "addresses_failure_ids": array(ref("id"), minimum=1),
        "old_descriptor_digest": ref("digest"),
        "new_descriptor_digest": ref("digest"),
        "canonical_diff": ref("canonical_diff"),
        "canonical_diff_digest": ref("digest"),
        "delta_digest": ref("digest"),
    }
    novelty_payloads = {
        "evidence-added": {
            "old_evidence_refs": ref("evidence_ref_set"),
            "new_evidence_refs": ref("evidence_ref_set"),
        },
        "hypothesis-replaced": {
            "old_hypothesis": hypothesis,
            "new_hypothesis": hypothesis,
            "changed_proposition_ids": array({"type": "string", "pattern": r"^proposition-[a-z0-9][a-z0-9-]{0,62}$"}, minimum=1),
        },
        "strategy-changed": {
            "old_strategy": strategy,
            "new_strategy": strategy,
            "changed_operation_ids": array({"type": "string", "pattern": r"^operation-[a-z0-9][a-z0-9-]{0,62}$"}, minimum=1),
        },
        "route-capability-changed": {
            "old_route_descriptor": route_descriptor,
            "new_route_descriptor": route_descriptor,
            "newly_observed_capability_ids": array(
                {"type": "string", "pattern": r"^capability-[a-z0-9][a-z0-9-]{0,62}$"}, minimum=1,
            ),
        },
        "task-narrowed": {"old_scope": task_scope, "new_scope": task_scope},
        "dependency-repaired": {
            "predicate_id": const("dependency-artifact-present"),
            "predicate_version": const(1),
            "predicate_input_schema_digest": ref("digest"),
            "old_input": dependency_input,
            "new_input": dependency_input,
            "old_result_digest": ref("digest"),
            "repair_receipt_digest": ref("digest"),
            "new_result_digest": ref("digest"),
        },
        "owner-amended": {
            "old_goal_ref": ref("object_ref"),
            "new_goal_ref": ref("object_ref"),
            "accepted_owner_command_receipt_digest": ref("digest"),
            "amendment_disposition_digest": ref("digest"),
            "retained_node_id": ref("id"),
            "compatibility_input_digest": ref("digest"),
        },
    }
    novelty_refs = []
    for kind, payload_props in novelty_payloads.items():
        name = "novelty_" + kind.replace("-", "_")
        d[name] = closed({**novelty_common, "kind": const(kind), **payload_props})
        novelty_refs.append(ref(name))
    d["novelty_delta"] = {"oneOf": novelty_refs}

    policy_ref = ref("policy_ref")
    object_ref = ref("object_ref")
    id_set = ref("id_set")
    digest_set = ref("digest_set")
    resource_set = ref("resource_path_set")
    budget = ref("budget_vector")
    dispositions = ref("disposition_set")
    gate_set = ref("gate_requirement_set")

    payloads: dict[str, dict] = {}
    payloads["owner_intent"] = closed(
        {
            "intent_text": ref("nonempty_text"),
            "source_kind": enum("owner-prompt", "owner-amendment"),
            "source_digest": ref("digest"),
            "privacy_policy_ref": policy_ref,
            "supersedes_ref": nullable(object_ref),
        }
    )
    payloads["goal_spec"] = closed(
        {
            "owner_intent_ref": object_ref,
            "outcome": ref("nonempty_text"),
            "acceptance_gate_ids": id_set,
            "allowed_resource_paths": resource_set,
            "non_goals": ref("text_set"),
            "authority_ids": id_set,
            "capability_ids": id_set,
            "allowed_action_ids": id_set,
            "prohibition_ids": id_set,
            "authority_policy_ref": policy_ref,
            "privacy_class_id": ref("id"),
            "egress_class_id": ref("id"),
            "privacy_policy_ref": policy_ref,
            "egress_policy_ref": policy_ref,
            "route_policy_ref": policy_ref,
            "allowed_route_ids": id_set,
            "allowed_account_class_ids": id_set,
            "allowed_capacity_pool_ids": id_set,
            "budget_limits": budget,
            "source_digests": digest_set,
            "novelty_policy_ref": policy_ref,
            "retry_policy_ref": policy_ref,
            "verifier_policy_ref": policy_ref,
            "constitution_policy_ref": policy_ref,
            "pause_policy_ref": policy_ref,
            "allowed_effect_keys": id_set,
            "publication_allowed": const(False),
            "terminal_owner_seam_ids": id_set,
            "fence_epoch": ref("uint"),
            "state": const("accepted"),
        }
    )
    payloads["goal_spec_amendment"] = closed(
        {
            "old_goal_ref": object_ref,
            "new_goal_ref": object_ref,
            "changed_field_paths": ref("text_set"),
            "rationale_digest": ref("digest"),
            "owner_authority_attestation_id": ref("id"),
            "effective_fence_epoch": ref("uint"),
            "checkpoint_rule": enum("current-immediate", "safe-checkpoint"),
            "compatibility_inputs": array(ref("compatibility_input"), sorted_by="old_node.node_id"),
            "dispositions": dispositions,
            "plan_transition_ref": object_ref,
        }
    )
    payloads["arm_run"] = closed(
        {
            "goal_ref": object_ref,
            "logical_actor_id": ref("id"),
            "eligible_route_ids": id_set,
            "eligible_account_class_ids": id_set,
            "eligible_capacity_pool_ids": id_set,
            "budget_limits": budget,
            "source_digests": digest_set,
            "executive_lease_ref": ref("lease_ref"),
            "verifier_policy_ref": policy_ref,
        }
    )
    edge = closed({"from_node_id": ref("id"), "to_node_id": ref("id")})
    payloads["plan_revision"] = closed(
        {
            "goal_ref": object_ref,
            "arm_run_ref": object_ref,
            "prior_plan_ref": nullable(object_ref),
            "trigger": enum("initial", "retry", "replan", "amendment"),
            "task_node_refs": array(object_ref, sorted_by="id"),
            "dependency_edges": array(edge, sorted_by=["from_node_id", "to_node_id"]),
            "graph_digest": ref("digest"),
            "acceptance_gate_ids": id_set,
            "budget_limits": budget,
            "read_resource_paths": resource_set,
            "write_resource_paths": resource_set,
            "effect_keys": id_set,
            "source_digests": digest_set,
            "verifier_policy_ref": policy_ref,
            "constitution_policy_ref": policy_ref,
            "assigned_plan_verifier_actor_id": ref("id"),
            "change_rationale_digest": ref("digest"),
            "dispositions": dispositions,
        }
    )
    payloads["plan_transition"] = closed(
        {
            "from_plan_ref": nullable(object_ref),
            "to_plan_ref": object_ref,
            "trigger_evidence_digests": digest_set,
            "dispositions": dispositions,
            "executive_lease_ref": ref("lease_ref"),
            "expected_goal_fence_epoch": ref("uint"),
            "checkpoint_ref": nullable(object_ref),
        }
    )
    payloads["task_node"] = closed(
        {
            "plan_ref": ref("plan_identity_ref"),
            "semantic_definition_digest": ref("digest"),
            "output_schema_digest": ref("digest"),
            "dependency_node_ids": id_set,
            "input_digests": digest_set,
            "source_digests": digest_set,
            "read_resource_paths": resource_set,
            "write_resource_paths": resource_set,
            "effect_keys": id_set,
            "authority_ids": id_set,
            "capability_ids": id_set,
            "allowed_action_ids": id_set,
            "prohibition_ids": id_set,
            "route_ids": id_set,
            "route_capability_ids": id_set,
            "account_class_ids": id_set,
            "capacity_pool_ids": id_set,
            "authority_policy_ref": policy_ref,
            "privacy_class_id": ref("id"),
            "egress_class_id": ref("id"),
            "privacy_policy_ref": policy_ref,
            "egress_policy_ref": policy_ref,
            "budget_limits": budget,
            "gate_requirements": gate_set,
            "retry_policy_ref": policy_ref,
            "verifier_policy_ref": policy_ref,
            "constitution_policy_ref": policy_ref,
            "terminal_contribution_digest": ref("digest"),
            "retry_maximum": ref("uint"),
        }
    )
    payloads["work_packet"] = closed(
        {
            "goal_ref": object_ref,
            "plan_ref": object_ref,
            "task_ref": object_ref,
            "supersedes_packet_ref": nullable(object_ref),
            "logical_worker_actor_id": ref("id"),
            "attempt": ref("pos_int"),
            "work_lease_ref": ref("lease_ref"),
            "expected_goal_fence_epoch": ref("uint"),
            "expected_pause_epoch": ref("uint"),
            "authority_ids": id_set,
            "capability_ids": id_set,
            "allowed_resource_paths": resource_set,
            "effect_keys": id_set,
            "privacy_class_id": ref("id"),
            "egress_class_id": ref("id"),
            "authority_policy_ref": policy_ref,
            "privacy_policy_ref": policy_ref,
            "egress_policy_ref": policy_ref,
            "route_assignment_ref": object_ref,
            "budget_reservation_ref": object_ref,
            "budget_limits": budget,
            "source_digests": digest_set,
            "gate_requirements": gate_set,
            "allowed_action_ids": id_set,
            "prohibition_ids": id_set,
            "inherited_non_goals": ref("text_set"),
            "output_schema_digest": ref("digest"),
            "deadline_logical_time": ref("logical_time"),
            "checkpoint_ref": nullable(object_ref),
        }
    )
    payloads["worker_result"] = closed(
        {
            "work_packet_ref": object_ref,
            "candidate_digest": ref("digest"),
            "evidence_digests": digest_set,
            "output_digest": ref("digest"),
            "observed_effect_ref": nullable(object_ref),
            "disposition": enum("submitted", "failed"),
        }
    )
    payloads["gate_result"] = closed(
        {
            "goal_ref": object_ref,
            "plan_ref": object_ref,
            "task_ref": object_ref,
            "work_packet_ref": object_ref,
            "candidate_digest": ref("digest"),
            "source_digests": digest_set,
            "evidence_digests": digest_set,
            "gate_requirement": ref("gate_requirement"),
            "procedure_version": ref("pos_int"),
            "observation_digest": ref("digest"),
            "expected_digest": ref("digest"),
            "actual_digest": ref("digest"),
            "independence": ref("independence_projection"),
            "disposition": enum("pass", "fail", "error", "missing", "ambiguous"),
            "limitation_digests": digest_set,
        }
    )
    payloads["retry_decision"] = closed(
        {
            "goal_ref": object_ref,
            "plan_ref": object_ref,
            "task_ref": object_ref,
            "failed_gate_result_ref": object_ref,
            "prior_work_packet_ref": object_ref,
            "novelty_delta": ref("novelty_delta"),
            "novelty_delta_digest": ref("digest"),
            "unchanged_binding_digest": ref("digest"),
            "next_attempt": ref("pos_int"),
            "remaining_budget": budget,
            "retry_maximum": ref("uint"),
            "disposition": enum("admitted", "refused", "exhausted"),
        }
    )
    payloads["replan_decision"] = closed(
        {
            "goal_ref": object_ref,
            "old_plan_ref": object_ref,
            "new_plan_ref": object_ref,
            "trigger_evidence_digests": digest_set,
            "dispositions": dispositions,
            "narrowed_binding_digest": ref("digest"),
            "blocker_ref": nullable(object_ref),
            "escalation_ref": nullable(object_ref),
            "disposition": enum("admitted", "refused"),
        }
    )
    blocker_payload = closed(
        {
            "blocked_object_ref": object_ref,
            "kind": enum(
                "authority", "capacity", "dependency", "effect-ambiguity", "gate", "policy",
                "provider-refusal", "source", "verifier",
            ),
            "evidence_digests": digest_set,
            "required_actor_id": ref("id"),
            "allowed_recovery_ids": id_set,
            "retry_after_observation_ref": nullable(object_ref),
            "failure_fingerprint_digest": ref("digest"),
            "state": enum("open", "deferred", "resolved", "superseded", "escalated"),
        }
    )
    blocker_payload["allOf"] = [{
        "oneOf": [
            {
                "properties": {
                    "state": const("deferred"),
                    "kind": const("capacity"),
                    "retry_after_observation_ref": ref("object_ref"),
                },
                "required": ["state", "kind", "retry_after_observation_ref"],
            },
            {
                "properties": {
                    "state": enum("open", "resolved", "superseded", "escalated"),
                    "retry_after_observation_ref": const(None),
                },
                "required": ["state", "retry_after_observation_ref"],
            },
        ]
    }]
    payloads["blocker"] = blocker_payload
    payloads["escalation"] = closed(
        {
            "source_blocker_ref": object_ref,
            "target_role": enum("head", "owner"),
            "failure_history_digests": digest_set,
            "requested_decision": ref("nonempty_text"),
            "option_digests": digest_set,
            "recommendation_digest": ref("digest"),
            "frozen_scope_digest": ref("digest"),
            "state": enum("raised", "acknowledged", "resolved", "declined", "superseded"),
        }
    )
    verifier_payload = closed(
        {
            "goal_ref": object_ref,
            "plan_ref": object_ref,
            "candidate_digest": ref("digest"),
            "event_log_digest": ref("digest"),
            "gate_result_digests": digest_set,
            "evidence_digests": digest_set,
            "verifier_policy_ref": policy_ref,
            "constitution_policy_ref": policy_ref,
            "independence": ref("independence_projection"),
            "disposition": enum("pass", "downgraded-pass", "fail", "blocked"),
            "assurance_grade": enum("full", "downgraded", "none"),
            "owner_exception_ref": nullable(object_ref),
            "dissent_digest": nullable(ref("digest")),
            "limitation_digests": digest_set,
        }
    )
    verifier_payload["allOf"] = [{
        "oneOf": [
            {"properties": {"disposition": const("pass"), "assurance_grade": const("full"), "owner_exception_ref": const(None)}},
            {"properties": {"disposition": const("downgraded-pass"), "assurance_grade": const("downgraded"), "owner_exception_ref": ref("object_ref")}},
            {"properties": {"disposition": enum("fail", "blocked"), "assurance_grade": const("none"), "owner_exception_ref": const(None)}},
        ]
    }]
    payloads["plan_verifier_decision"] = verifier_payload
    payloads["owner_verifier_exception"] = closed(
        {
            "goal_ref": object_ref,
            "plan_ref": object_ref,
            "candidate_digest": ref("digest"),
            "verifier_policy_ref": policy_ref,
            "constitution_policy_ref": policy_ref,
            "missing_dimensions": ref("token_set"),
            "reason_digest": ref("digest"),
            "owner_authority_attestation_id": ref("id"),
            "issued_logical_time": ref("logical_time"),
            "expires_logical_time": ref("logical_time"),
        }
    )
    lease_payload = closed(
        {
            "subject_actor_id": ref("id"),
            "goal_ref": object_ref,
            "plan_ref": nullable(object_ref),
            "task_ref": nullable(object_ref),
            "supersedes_lease_ref": nullable(ref("lease_ref")),
            "lease_epoch": ref("uint"),
            "nonce_digest": ref("digest"),
            "issued_logical_time": ref("logical_time"),
            "expires_logical_time": ref("logical_time"),
            "allowed_command_types": array(ref("command_type")),
            "state": enum("active", "expired", "revoked", "replaced"),
        }
    )
    payloads["executive_lease"] = lease_payload
    payloads["work_lease"] = lease_payload
    payloads["checkpoint"] = closed(
        {
            "state_version": ref("uint"),
            "state_digest": ref("digest"),
            "active_goal_ref": nullable(object_ref),
            "active_plan_ref": nullable(object_ref),
            "open_packet_refs": array(object_ref, sorted_by="id"),
            "ambiguous_effect_refs": array(object_ref, sorted_by="id"),
            "budget_snapshot_digest": ref("digest"),
            "route_snapshot_digest": ref("digest"),
            "pause_epoch": ref("uint"),
            "lease_epoch_digest": ref("digest"),
        }
    )
    payloads["route_assignment"] = closed(
        {
            "logical_actor_id": ref("id"),
            "route_id": ref("id"),
            "route_capability_ids": id_set,
            "account_class_id": ref("id"),
            "capacity_pool_id": ref("id"),
            "privacy_policy_ref": policy_ref,
            "egress_policy_ref": policy_ref,
            "route_policy_ref": policy_ref,
            "metered_spend_allowed": const(False),
            "capacity_observation_ref": object_ref,
            "supersedes_route_ref": nullable(object_ref),
            "assigned_logical_time": ref("logical_time"),
            "expires_logical_time": ref("logical_time"),
            "state": enum("assigned", "deferred", "released", "expired"),
        }
    )
    payloads["capacity_observation"] = closed(
        {
            "route_id": ref("id"),
            "account_class_id": ref("id"),
            "capacity_pool_id": ref("id"),
            "spend_class": enum("none", "included"),
            "available": {"type": "boolean"},
            "remaining_units": ref("uint"),
            "observation_digest": ref("digest"),
        }
    )
    payloads["budget_reservation"] = closed(
        {
            "goal_ref": object_ref,
            "plan_ref": object_ref,
            "task_ref": object_ref,
            "limits": budget,
            "consumed": budget,
            "remaining": budget,
            "state": enum("reserved", "released", "consumed"),
        }
    )
    payloads["pause_directive"] = closed(
        {
            "pause_policy_ref": policy_ref,
            "mode": enum("current-immediate", "checkpoint", "interrupt", "drain"),
            "new_pause_epoch": ref("uint"),
            "reason_digest": ref("digest"),
        }
    )
    effect_payload = closed(
        {
            "effect_id": ref("id"),
            "effect_key": ref("id"),
            "work_packet_ref": object_ref,
            "idempotency_key_digest": ref("digest"),
            "dispatch_state": enum("undispatched", "dispatched"),
            "receipt_digest": nullable(ref("digest")),
            "provider_operation_id_digest": nullable(ref("digest")),
            "observation": enum("observed-success", "observed-failure", "ambiguous"),
            "quarantine": {"type": "boolean"},
        }
    )
    effect_payload["allOf"] = [{
        "oneOf": [
            {"properties": {"observation": const("observed-success"), "dispatch_state": const("dispatched"), "receipt_digest": ref("digest"), "provider_operation_id_digest": ref("digest"), "quarantine": const(False)}},
            {"properties": {"observation": const("ambiguous"), "quarantine": const(True)}},
            {"properties": {"observation": const("observed-failure"), "quarantine": const(False)}},
        ]
    }]
    payloads["effect_observation"] = effect_payload
    payloads["disposition_record"] = ref("disposition")

    record_specs = [
        ("owner_intent", "owner-intent", "m1a-owner-intent-1"),
        ("goal_spec", "goal-spec", "m1a-goal-spec-1"),
        ("goal_spec_amendment", "goal-spec-amendment", "m1a-goal-spec-amendment-1"),
        ("arm_run", "arm-run", "m1a-arm-run-1"),
        ("plan_revision", "plan-revision", "m1a-plan-revision-1"),
        ("plan_transition", "plan-transition", "m1a-plan-transition-1"),
        ("task_node", "task-node", "m1a-task-node-1"),
        ("work_packet", "work-packet", "m1a-work-packet-1"),
        ("worker_result", "worker-result", "m1a-worker-result-1"),
        ("gate_result", "gate-result", "m1a-gate-result-1"),
        ("retry_decision", "retry-decision", "m1a-retry-decision-1"),
        ("replan_decision", "replan-decision", "m1a-replan-decision-1"),
        ("blocker", "blocker", "m1a-blocker-1"),
        ("escalation", "escalation", "m1a-escalation-1"),
        ("plan_verifier_decision", "plan-verifier-decision", "m1a-plan-verifier-decision-1"),
        ("owner_verifier_exception", "owner-verifier-exception", "m1a-owner-verifier-exception-1"),
        ("executive_lease", "executive-lease", "m1a-executive-lease-1"),
        ("work_lease", "work-lease", "m1a-work-lease-1"),
        ("checkpoint", "checkpoint", "m1a-checkpoint-1"),
        ("route_assignment", "route-assignment", "m1a-route-assignment-1"),
        ("capacity_observation", "capacity-observation", "m1a-capacity-observation-1"),
        ("budget_reservation", "budget-reservation", "m1a-budget-reservation-1"),
        ("pause_directive", "pause-directive", "m1a-pause-directive-1"),
        ("effect_observation", "effect-observation", "m1a-effect-observation-1"),
        ("disposition_record", "disposition", "m1a-disposition-1"),
    ]
    record_refs = []
    for key, object_type, schema_version in record_specs:
        record_name = key + "_record"
        d[record_name] = record_schema(object_type, schema_version, payloads[key])
        record_refs.append(ref(record_name))
    d["domain_record"] = {"oneOf": record_refs}

    domain_array = array(
        ref("domain_record"), maximum=2048, sorted_by=["object_type", "id", "version"]
    )
    task_record_array = array(ref("task_node_record"), sorted_by="id")
    command_payloads: dict[str, dict] = {
        "record-owner-intent": ref("owner_intent_record"),
        "accept-goal-spec": ref("goal_spec_record"),
        "amend-goal-spec": closed(
            {
                "new_goal_spec": ref("goal_spec_record"),
                "amendment": ref("goal_spec_amendment_record"),
                "replacement_plan_revision": ref("plan_revision_record"),
                "plan_transition": ref("plan_transition_record"),
                "task_nodes": task_record_array,
                "arm_proposal_attestation_id": ref("id"),
            }
        ),
        "record-owner-verifier-exception": ref("owner_verifier_exception_record"),
        "start-arm-run": closed(
            {"executive_lease": ref("executive_lease_record"), "arm_run": ref("arm_run_record")}
        ),
        "propose-plan-revision": closed(
            {
                "plan_revision": ref("plan_revision_record"),
                "plan_transition": ref("plan_transition_record"),
                "task_nodes": task_record_array,
            }
        ),
        "derive-work-packet": closed(
            {
                "task_ref": object_ref,
                "attempt": ref("pos_int"),
                "work_lease": ref("work_lease_record"),
                "route_assignment": ref("route_assignment_record"),
                "budget_reservation_ref": object_ref,
                "expected_work_packet_digest": ref("digest"),
            }
        ),
        "replace-work-lease": closed(
            {"old_lease_ref": ref("lease_ref"), "new_lease": ref("work_lease_record")}
        ),
        "replace-executive-lease": closed(
            {"old_lease_ref": ref("lease_ref"), "new_lease": ref("executive_lease_record")}
        ),
        "replace-route": closed(
            {
                "old_route_ref": object_ref,
                "new_route": ref("route_assignment_record"),
                "checkpoint_ref": object_ref,
                "expected_new_packet_digest": ref("digest"),
            }
        ),
        "record-capacity-observation": ref("capacity_observation_record"),
        "record-checkpoint": ref("checkpoint_record"),
        "reserve-budget": ref("budget_reservation_record"),
        "submit-worker-result": ref("worker_result_record"),
        "submit-gate-result": ref("gate_result_record"),
        "propose-retry": ref("retry_decision_record"),
        "propose-replan": closed(
            {
                "decision": ref("replan_decision_record"),
                "new_plan_revision": ref("plan_revision_record"),
                "transition": ref("plan_transition_record"),
                "task_nodes": task_record_array,
            }
        ),
        "raise-blocker": ref("blocker_record"),
        "raise-escalation": ref("escalation_record"),
        "submit-plan-verifier-decision": ref("plan_verifier_decision_record"),
        "apply-pause": ref("pause_directive_record"),
        "record-effect-observation": ref("effect_observation_record"),
    }
    command_common = {
        "command_schema_version": const("m1a-command-1"),
        "command_id": ref("command_id"),
        "actor_id": ref("id"),
        "auth_ref": ref("id"),
        "lease_ref": nullable(ref("lease_ref")),
        "logical_time": ref("logical_time"),
        "expected_state_version": ref("uint"),
        "expected_state_digest": ref("digest"),
        "goal_ref": nullable(object_ref),
        "plan_ref": nullable(object_ref),
        "payload_digest": ref("digest"),
        "candidate_digest": ref("digest"),
        "content_digest": ref("digest"),
    }
    command_refs = []
    for command_type in command_types:
        name = "command_" + command_type.replace("-", "_")
        d[name] = closed(
            {
                "command_schema_version": command_common["command_schema_version"],
                "command_id": command_common["command_id"],
                "command_type": const(command_type),
                "actor_id": command_common["actor_id"],
                "auth_ref": command_common["auth_ref"],
                "lease_ref": command_common["lease_ref"],
                "logical_time": command_common["logical_time"],
                "expected_state_version": command_common["expected_state_version"],
                "expected_state_digest": command_common["expected_state_digest"],
                "goal_ref": command_common["goal_ref"],
                "plan_ref": command_common["plan_ref"],
                "payload": command_payloads[command_type],
                "payload_digest": command_common["payload_digest"],
                "candidate_digest": command_common["candidate_digest"],
                "content_digest": command_common["content_digest"],
            },
            **{"x-maxCanonicalBytes": 262144},
        )
        command_refs.append(ref(name))
    d["command_envelope"] = {"oneOf": command_refs}

    d["command_receipt"] = closed(
        {
            "receipt_schema_version": const("m1a-receipt-1"),
            "receipt_id": ref("id"),
            "command_id": ref("command_id"),
            "command_digest": ref("digest"),
            "disposition": enum("accepted", "refused", "duplicate", "conflict"),
            "primary_error": nullable(ref("error_code")),
            "related_errors": ref("error_code_set"),
            "witness": nullable(ref("error_witness")),
            "state_before_digest": ref("digest"),
            "state_after_digest": ref("digest"),
            "event_ids": ref("id_set"),
            "first_event_sequence": nullable(ref("uint")),
            "last_event_sequence": nullable(ref("uint")),
            "content_digest": ref("digest"),
        },
        **{"x-maxCanonicalBytes": 262144},
    )
    d["command_receipt"]["allOf"] = [{
        "oneOf": [
            {
                "properties": {
                    "disposition": const("accepted"),
                    "primary_error": const(None),
                    "related_errors": {"maxItems": 0},
                    "witness": const(None),
                    "event_ids": {"minItems": 1},
                    "first_event_sequence": ref("uint"),
                    "last_event_sequence": ref("uint"),
                },
                "required": [
                    "disposition", "primary_error", "related_errors", "witness", "event_ids",
                    "first_event_sequence", "last_event_sequence",
                ],
            },
            {
                "properties": {
                    "disposition": enum("refused", "conflict"),
                    "primary_error": ref("error_code"),
                    "event_ids": {"maxItems": 0},
                    "first_event_sequence": const(None),
                    "last_event_sequence": const(None),
                },
                "required": [
                    "disposition", "primary_error", "event_ids", "first_event_sequence",
                    "last_event_sequence",
                ],
            },
            {
                "properties": {
                    "disposition": const("duplicate"),
                    "primary_error": const(None),
                    "related_errors": {"maxItems": 0},
                    "witness": const(None),
                    "event_ids": {"maxItems": 0},
                    "first_event_sequence": const(None),
                    "last_event_sequence": const(None),
                },
                "required": [
                    "disposition", "primary_error", "related_errors", "witness", "event_ids",
                    "first_event_sequence", "last_event_sequence",
                ],
            },
        ]
    }]

    no_related = array(ref("domain_record"), maximum=0)
    goal_related = array(ref("goal_spec_record"), minimum=1, maximum=1)
    arm_related = array(ref("executive_lease_record"), minimum=1, maximum=1)
    plan_related = {
        "type": "array",
        "minItems": 2,
        "maxItems": 257,
        "uniqueItems": True,
        "items": {"oneOf": [ref("plan_transition_record"), ref("task_node_record")]},
        "contains": ref("plan_transition_record"),
        "minContains": 1,
        "maxContains": 1,
        "x-sortedBy": ["object_type", "id", "version"],
    }
    initial_packet_related = {
        "type": "array",
        "minItems": 2,
        "maxItems": 2,
        "uniqueItems": True,
        "prefixItems": [ref("route_assignment_record"), ref("work_lease_record")],
        "items": False,
    }
    packet_related = {"oneOf": [no_related, initial_packet_related]}
    event_map = {
        "OwnerIntentRecorded": ("owner_intent_record", no_related),
        "GoalSpecAccepted": ("goal_spec_record", no_related),
        "GoalSpecAmended": ("goal_spec_amendment_record", goal_related),
        "OwnerVerifierExceptionRecorded": ("owner_verifier_exception_record", no_related),
        "ArmRunStarted": ("arm_run_record", arm_related),
        "PlanRevisionAdmitted": ("plan_revision_record", plan_related),
        "WorkPacketDerived": ("work_packet_record", packet_related),
        "WorkLeaseReplaced": ("work_lease_record", no_related),
        "ExecutiveLeaseReplaced": ("executive_lease_record", no_related),
        "RouteAssignmentReplaced": ("route_assignment_record", no_related),
        "CapacityObservationRecorded": ("capacity_observation_record", no_related),
        "CheckpointRecorded": ("checkpoint_record", no_related),
        "BudgetReserved": ("budget_reservation_record", no_related),
        "WorkerResultRecorded": ("worker_result_record", no_related),
        "GateResultRecorded": ("gate_result_record", no_related),
        "RetryAdmitted": ("retry_decision_record", no_related),
        "ReplanAdmitted": ("replan_decision_record", no_related),
        "BlockerRaised": ("blocker_record", no_related),
        "EscalationRaised": ("escalation_record", no_related),
        "PlanVerifierDecisionRecorded": ("plan_verifier_decision_record", no_related),
        "PauseApplied": ("pause_directive_record", no_related),
        "EffectObservationRecorded": ("effect_observation_record", no_related),
        "PlanItemDisposed": ("disposition_record_record", no_related),
        "PacketFenced": ("disposition_record_record", no_related),
        "LeaseFenced": ("disposition_record_record", no_related),
        "EffectDisposed": ("disposition_record_record", no_related),
        "EvidenceDisposed": ("disposition_record_record", no_related),
    }
    event_refs = []
    for event_type in event_types:
        primary_name, related_schema = event_map[event_type]
        name = "event_" + event_type
        d[name] = closed(
            {
                "event_schema_version": const("m1a-event-1"),
                "event_id": ref("id"),
                "stream_id": ref("id"),
                "sequence": ref("pos_int"),
                "previous_event_digest": ref("digest"),
                "logical_time": ref("logical_time"),
                "command_id": ref("command_id"),
                "command_digest": ref("digest"),
                "event_type": const(event_type),
                "primary_record": ref(primary_name),
                "related_records": related_schema,
                "state_delta_digest": ref("digest"),
                "content_digest": ref("digest"),
            },
            **{"x-maxCanonicalBytes": 262144},
        )
        event_refs.append(ref(name))
    d["planning_event"] = {"oneOf": event_refs}

    d["replay_checkpoint"] = closed(
        {
            "checkpoint_record": ref("checkpoint_record"),
            "projection_snapshot": ref("projection_state"),
        }
    )
    replay_expectation = closed(
        {
            "replay_id": ref("id"),
            "checkpoint": nullable(ref("replay_checkpoint")),
            "commands": array(ref("command_envelope"), maximum=2048, unique=False),
            "receipts": array(ref("command_receipt"), maximum=2048, unique=False),
            "event_inputs": array(ref("json_input_text"), maximum=2048, unique=False),
            "expected_disposition": enum("accepted", "refused"),
            "primary_error": nullable(ref("error_code")),
            "expected_projection_digest": nullable(ref("digest")),
        }
    )
    replay_expectation["allOf"] = [{
        "oneOf": [
            {
                "properties": {
                    "expected_disposition": const("accepted"),
                    "primary_error": const(None),
                    "expected_projection_digest": ref("digest"),
                },
                "required": ["expected_disposition", "primary_error", "expected_projection_digest"],
            },
            {
                "properties": {
                    "expected_disposition": const("refused"),
                    "primary_error": ref("error_code"),
                    "expected_projection_digest": const(None),
                },
                "required": ["expected_disposition", "primary_error", "expected_projection_digest"],
            },
        ]
    }]
    d["replay_expectation"] = replay_expectation

    object_state = closed({"object_ref": object_ref, "state": ref("token")})
    d["projection_state"] = closed(
        {
            "projection_schema_version": const("m1a-projection-1"),
            "stream_id": ref("id"),
            "state_version": ref("uint"),
            "last_event_sequence": ref("uint"),
            "last_event_digest": ref("digest"),
            "operative_goal_ref": nullable(object_ref),
            "active_arm_run_ref": nullable(object_ref),
            "active_plan_ref": nullable(object_ref),
            "records": domain_array,
            "object_states": array(
                object_state,
                maximum=2048,
                sorted_by=["object_ref.object_type", "object_ref.id", "object_ref.version"],
            ),
            "processed_command_receipts": array(
                ref("receipt_identity"), maximum=2048, sorted_by="receipt_id"
            ),
            "consumed_novelty_delta_digests": ref("digest_set"),
            "open_blocker_refs": array(object_ref, sorted_by="id"),
            "open_escalation_refs": array(object_ref, sorted_by="id"),
            "ambiguous_effect_refs": array(object_ref, sorted_by="id"),
            "current_pause_policy_ref": policy_ref,
            "current_pause_epoch": ref("uint"),
            "terminal_status": enum(
                "nonterminal", "terminal-verified", "terminal-verified-downgraded", "terminal-failed"
            ),
            "content_digest": ref("digest"),
        }
    )
    d["fixture_case"] = closed(
        {
            "case_id": ref("token"),
            "description": ref("nonempty_text"),
            "genesis": ref("genesis_config"),
            "authority_fixtures": array(
                ref("authority_attestation"), maximum=2048, sorted_by="attestation_id"
            ),
            "policy_fixtures": array(
                ref("policy_fixture"), maximum=2048, sorted_by=["policy_id", "policy_version"]
            ),
            "initial_commands": array(ref("command_envelope"), maximum=2048, unique=False),
            "initial_receipts": array(ref("command_receipt"), maximum=2048, unique=False),
            "initial_events": array(ref("planning_event"), maximum=2048, unique=False),
            "decode_inputs": array(ref("json_input_text"), maximum=2048, unique=False),
            "expected_decode_failures": array(ref("decode_failure"), maximum=2048, unique=False),
            "commands": array(ref("command_envelope"), maximum=2048, unique=False),
            "expected_receipts": array(ref("command_receipt"), maximum=2048, unique=False),
            "expected_events": array(ref("planning_event"), maximum=2048, unique=False),
            "replay_cases": array(ref("replay_expectation"), maximum=256, unique=False),
            "expected_final_state": ref("projection_state"),
            "expected_final_digest": ref("digest"),
        }
    )
    d["fixture_bundle"] = closed(
        {
            "fixture_schema_version": const("m1a-fixture-1"),
            "fixture_id": ref("id"),
            "description": ref("nonempty_text"),
            "cases": array(
                ref("fixture_case"), minimum=1, maximum=256, sorted_by="case_id"
            ),
        },
        **{"x-maxCanonicalBytes": 1048576},
    )

    top_refs = [
        ref("domain_record"), ref("command_envelope"), ref("command_receipt"),
        ref("planning_event"), ref("projection_state"), ref("fixture_bundle"),
        ref("decode_failure"), ref("genesis_config"), ref("authority_attestation"),
        ref("policy_fixture"),
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://recursion.invalid/schemas/control-plane/v3/planning/schema.json",
        "title": "Recursion v3 M1A closed planning wire schema",
        "$comment": "Owner-approved M1A profile: 25 domain records, 22 commands, 27 events, 27 errors.",
        "x-maxDepth": 16,
        "oneOf": top_refs,
        "$defs": d,
    }


def main() -> None:
    target = Path(__file__).with_name("schema.json")
    rendered = json.dumps(build_schema(), ensure_ascii=False, indent=2) + "\n"
    if sys.argv[1:] == ["--write"]:
        target.write_text(rendered, encoding="utf-8", newline="\n")
        return
    if sys.argv[1:] == ["--check"]:
        if not target.is_file() or target.read_text(encoding="utf-8") != rendered:
            raise SystemExit("schema.json is not the byte-identical materialized schema")
        print("M1A_SCHEMA_MATERIALIZATION_PASS")
        return
    raise SystemExit("usage: materialize.py --write | --check")


if __name__ == "__main__":
    main()
