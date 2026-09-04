#!/usr/bin/env python3
"""Materialize the closed Recursion v3 M1B execution-contract schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "schema.json"
SCHEMA_ID = "https://recursion.local/schemas/control-plane/v3/execution/schema.json"


def ref(name: str) -> dict[str, str]:
    return {"$ref": f"#/$defs/{name}"}


def nullable(schema: dict[str, Any]) -> dict[str, Any]:
    return {"anyOf": [schema, {"type": "null"}]}


def obj(properties: dict[str, Any], *, required: list[str] | None = None, **extra: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required if required is not None else list(properties),
    }
    result.update(extra)
    return result


def tagged(tag: str, properties: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return obj({"type": {"const": tag}, **properties}, **extra)


def scalar_set(item: dict[str, Any], *, minimum: int = 0, maximum: int = 128) -> dict[str, Any]:
    return {
        "type": "array",
        "items": item,
        "minItems": minimum,
        "maxItems": maximum,
        "uniqueItems": True,
        "x-strictlySorted": True,
    }


def keyed_set(name: str, *, key: str = "id", minimum: int = 0, maximum: int = 256) -> dict[str, Any]:
    return {
        "type": "array",
        "items": ref(name),
        "minItems": minimum,
        "maxItems": maximum,
        "x-strictlySortedBy": key,
        "x-uniqueBy": key,
    }


def ordered(name: str, *, minimum: int = 0, maximum: int = 256) -> dict[str, Any]:
    return {"type": "array", "items": ref(name), "minItems": minimum, "maxItems": maximum}


def typed_ref(tag: str) -> dict[str, Any]:
    return tagged(tag, {"id": ref("Id")})


def build_schema() -> dict[str, Any]:
    defs: dict[str, Any] = {}

    defs["Id"] = {
        "type": "string",
        "pattern": r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$",
        "minLength": 1,
        "maxLength": 96,
        "x-utf8MaxBytes": 96,
    }
    defs["Capability"] = ref("Id")
    defs["Digest"] = {"type": "string", "pattern": r"^sha256:[0-9a-f]{64}$"}
    defs["OpaqueRef"] = {
        "type": "string",
        "pattern": r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$",
        "minLength": 1,
        "maxLength": 160,
        "x-utf8MaxBytes": 160,
    }
    defs["Timestamp"] = {
        "type": "string",
        "pattern": r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        "x-rfc3339Utc": True,
    }
    defs["Version"] = {
        "type": "string",
        "pattern": r"^[A-Za-z0-9][A-Za-z0-9._/+:-]{0,95}$",
        "maxLength": 96,
        "x-utf8MaxBytes": 96,
    }
    defs["Text"] = {"type": "string", "minLength": 1, "maxLength": 512, "x-utf8MaxBytes": 512}
    defs["Count"] = {"type": "integer", "minimum": 0, "maximum": 2147483647}
    defs["PositiveCount"] = {"type": "integer", "minimum": 1, "maximum": 2147483647}
    defs["Microunits"] = {"type": "integer", "minimum": 0, "maximum": 9007199254740991}
    defs["TriState"] = {"enum": ["supported", "unsupported", "unknown"]}
    defs["PrivacyClass"] = {"enum": ["public", "internal", "private", "restricted"]}
    defs["BillingBasis"] = {"enum": ["subscription", "metered", "local", "unknown"]}
    defs["Platform"] = {"enum": ["windows", "linux", "macos", "unknown"]}
    defs["TrustTier"] = {
        "enum": ["T0-kernel", "T1-signed-built-in", "T2-signed-isolated-third-party",
                 "T3-untrusted-view", "T4-external-engine-provider"]
    }
    defs["IsolationMode"] = {
        "enum": ["typed-in-process", "isolated-subprocess", "remote-protocol", "sandboxed-view", "metadata-only"]
    }
    defs["IdSet"] = scalar_set(ref("Id"))
    defs["NonEmptyIdSet"] = scalar_set(ref("Id"), minimum=1)
    defs["OpaqueRefSet"] = scalar_set(ref("OpaqueRef"))
    defs["PrivacyClassSet"] = scalar_set(ref("PrivacyClass"), minimum=1)
    defs["BillingBasisSet"] = scalar_set(ref("BillingBasis"), minimum=1)

    defs["EvidenceBinding"] = tagged(
        "EvidenceBinding@1",
        {
            "source_ids": ref("NonEmptyIdSet"),
            "observed_at": ref("Timestamp"),
            "expires_at": nullable(ref("Timestamp")),
            "evidence_digest": ref("Digest"),
        },
    )
    defs["CapabilityState"] = tagged(
        "CapabilityState@1", {"name": ref("Capability"), "state": ref("TriState")}
    )
    capability_states = keyed_set("CapabilityState", key="name", minimum=1, maximum=128)

    defs["EngineDescriptor"] = tagged(
        "EngineDescriptor@1",
        {
            "id": ref("Id"),
            "protocol_versions": scalar_set(ref("Version"), minimum=1),
            "capabilities": ref("NonEmptyIdSet"),
        },
    )
    defs["ProviderDescriptor"] = tagged(
        "ProviderDescriptor@1",
        {
            "id": ref("Id"),
            "endpoint_ids": scalar_set(ref("OpaqueRef"), minimum=1),
            "privacy_classes": ref("PrivacyClassSet"),
        },
    )
    defs["ModelDescriptor"] = tagged(
        "ModelDescriptor@1",
        {
            "id": ref("Id"),
            "provider_id": ref("Id"),
            "capabilities": ref("NonEmptyIdSet"),
            "reasoning_modes": scalar_set(ref("Id")),
        },
    )
    defs["CapacityPoolDescriptor"] = tagged(
        "CapacityPoolDescriptor@1",
        {
            "id": ref("Id"),
            "billing_basis": ref("BillingBasis"),
            "account_ref": nullable(ref("OpaqueRef")),
            "model_ids": ref("NonEmptyIdSet"),
            "state": {"enum": ["available", "exhausted", "unknown", "disabled"]},
            "remaining_units": nullable(ref("Count")),
            "metered_limit_microunits": nullable(ref("Microunits")),
        },
        allOf=[
            {
                "if": {"properties": {"billing_basis": {"const": "metered"}}, "required": ["billing_basis"]},
                "then": {"properties": {"account_ref": ref("OpaqueRef"), "metered_limit_microunits": ref("Microunits")}},
                "else": {"properties": {"metered_limit_microunits": {"type": "null"}}},
            },
            {
                "if": {"properties": {"billing_basis": {"enum": ["subscription"]}}, "required": ["billing_basis"]},
                "then": {"properties": {"account_ref": ref("OpaqueRef")}},
            },
            {
                "if": {"properties": {"state": {"enum": ["available", "exhausted"]}}, "required": ["state"]},
                "then": {"properties": {"remaining_units": ref("Count")}},
                "else": {"properties": {"remaining_units": {"type": "null"}}},
            },
        ],
    )
    defs["HostDescriptor"] = tagged(
        "HostDescriptor@1",
        {"id": ref("Id"), "platform": ref("Platform"), "capabilities": ref("NonEmptyIdSet")},
    )
    defs["SandboxDescriptor"] = tagged(
        "SandboxDescriptor@1",
        {
            "id": ref("Id"),
            "filesystem_mode": {"enum": ["none", "read-only", "workspace-write", "full"]},
            "network_mode": {"enum": ["denied", "allowlist", "full"]},
            "process_mode": {"enum": ["denied", "isolated", "full"]},
            "allowed_paths": ref("OpaqueRefSet"),
            "allowed_destinations": ref("OpaqueRefSet"),
            "capabilities": ref("IdSet"),
        },
    )
    defs["RouteComponentCatalog"] = tagged(
        "RouteComponentCatalog@1",
        {
            "engines": keyed_set("EngineDescriptor", minimum=1),
            "providers": keyed_set("ProviderDescriptor", minimum=1),
            "models": keyed_set("ModelDescriptor", minimum=1),
            "pools": keyed_set("CapacityPoolDescriptor", minimum=1),
            "hosts": keyed_set("HostDescriptor", minimum=1),
            "sandboxes": keyed_set("SandboxDescriptor", minimum=1),
        },
    )
    defs["RouteCapabilityDescriptor"] = tagged(
        "RouteCapabilityDescriptor@1",
        {
            "id": ref("Id"),
            "engine_id": ref("Id"),
            "provider_id": ref("Id"),
            "model_id": ref("Id"),
            "pool_id": ref("Id"),
            "account_ref": nullable(ref("OpaqueRef")),
            "host_id": ref("Id"),
            "sandbox_id": ref("Id"),
            "eligibility_state": {
                "enum": ["verified-current", "documented", "observed-uncertain", "stale", "unavailable"]
            },
            "capabilities": capability_states,
            "privacy_classes": ref("PrivacyClassSet"),
            "egress_destinations": ref("OpaqueRefSet"),
            "billing_control": {"enum": ["verified", "unverified", "unknown"]},
            "evidence": ref("EvidenceBinding"),
            "descriptor_digest": ref("Digest"),
        },
    )
    defs["RouteRequirement"] = tagged(
        "RouteRequirement@1",
        {
            "id": ref("Id"),
            "required_capabilities": ref("NonEmptyIdSet"),
            "privacy_class": ref("PrivacyClass"),
            "allowed_billing": ref("BillingBasisSet"),
            "allowed_route_ids": ref("IdSet"),
            "allowed_host_ids": ref("IdSet"),
            "allowed_egress_destinations": ref("OpaqueRefSet"),
            "estimated_metered_microunits": nullable(ref("Microunits")),
            "max_metered_microunits": nullable(ref("Microunits")),
            "required_sandbox_capabilities": ref("IdSet"),
        },
    )
    defs["RoutePolicyEnvelope"] = tagged(
        "RoutePolicyEnvelope@1",
        {
            "id": ref("Id"),
            "goal_spec_digest": ref("Digest"),
            "authority_digest": ref("Digest"),
            "policy_digest": ref("Digest"),
            "permitted_route_ids": ref("IdSet"),
            "permitted_host_ids": ref("IdSet"),
            "permitted_account_refs": ref("OpaqueRefSet"),
            "permitted_egress_destinations": ref("OpaqueRefSet"),
            "metered_authorized": {"type": "boolean"},
            "max_metered_microunits": nullable(ref("Microunits")),
            "pause_epoch": ref("Count"),
        },
        allOf=[
            {
                "if": {"properties": {"metered_authorized": {"const": True}}, "required": ["metered_authorized"]},
                "then": {"properties": {"max_metered_microunits": ref("Microunits")}},
                "else": {"properties": {"max_metered_microunits": {"type": "null"}}},
            }
        ],
    )
    defs["RouteResolutionInput"] = tagged(
        "RouteResolutionInput@1",
        {
            "catalog": ref("RouteComponentCatalog"),
            "descriptors": keyed_set("RouteCapabilityDescriptor", minimum=1),
            "requirement": ref("RouteRequirement"),
            "policy": ref("RoutePolicyEnvelope"),
            "ranked_route_ids": {
                "type": "array", "items": ref("Id"), "minItems": 1, "maxItems": 256,
                "uniqueItems": True,
            },
        },
    )
    route_reasons = [
        "account-mismatch", "billing-basis-denied", "billing-unknown", "capability-unknown",
        "capability-unsupported", "component-mismatch", "descriptor-not-current", "descriptor-stale",
        "egress-denied", "host-denied", "metered-budget-exceeded", "metered-not-authorized",
        "pool-disabled", "pool-exhausted", "pool-unknown", "privacy-mismatch", "route-denied",
        "route-unavailable", "sandbox-capability-missing",
    ]
    defs["RouteReason"] = {"enum": route_reasons}
    defs["RouteCandidateEvaluation"] = tagged(
        "RouteCandidateEvaluation@1",
        {
            "route_id": ref("Id"),
            "eligible": {"type": "boolean"},
            "reasons": scalar_set(ref("RouteReason")),
        },
        allOf=[
            {
                "if": {"properties": {"eligible": {"const": True}}, "required": ["eligible"]},
                "then": {"properties": {"reasons": {"maxItems": 0}}},
                "else": {"properties": {"reasons": {"minItems": 1}}},
            }
        ],
    )
    defs["RouteResolutionDecision"] = tagged(
        "RouteResolutionDecision@1",
        {
            "status": {"enum": ["selected", "blocked"]},
            "selected_route_id": nullable(ref("Id")),
            "candidate_evaluations": {
                **ordered("RouteCandidateEvaluation", minimum=1),
                "x-uniqueBy": "route_id",
            },
        },
        allOf=[
            {
                "if": {"properties": {"status": {"const": "selected"}}, "required": ["status"]},
                "then": {"properties": {"selected_route_id": ref("Id")}},
                "else": {"properties": {"selected_route_id": {"type": "null"}}},
            }
        ],
        **{"x-routeDecisionInvariant": True},
    )

    defs["PluginDependency"] = tagged(
        "PluginDependency@1",
        {"plugin_id": ref("Id"), "artifact_digest": ref("Digest"), "dependency_lock_digest": ref("Digest")},
    )
    defs["PluginGrantDimensions"] = tagged(
        "PluginGrantDimensions@1",
        {
            "functional_capabilities": ref("IdSet"),
            "workspace_paths": ref("OpaqueRefSet"),
            "network_destinations": ref("OpaqueRefSet"),
            "credential_refs": ref("OpaqueRefSet"),
            "model_refs": ref("OpaqueRefSet"),
            "route_account_refs": ref("OpaqueRefSet"),
            "quota_units": nullable(ref("Count")),
            "spend_microunits": nullable(ref("Microunits")),
            "update": {"type": "boolean"},
            "downgrade": {"type": "boolean"},
            "grant_admin": {"type": "boolean"},
        },
    )
    defs["ResourceEnvelope"] = tagged(
        "ResourceEnvelope@1",
        {
            "max_cpu_millis": ref("PositiveCount"),
            "max_memory_bytes": ref("PositiveCount"),
            "max_disk_bytes": ref("PositiveCount"),
            "max_concurrency": ref("PositiveCount"),
            "max_queue_events": ref("PositiveCount"),
            "max_queue_bytes": ref("PositiveCount"),
        },
    )
    defs["PluginManifest"] = tagged(
        "PluginManifest@1",
        {
            "id": ref("Id"),
            "plugin_id": ref("Id"),
            "version": ref("Version"),
            "protocol_version": ref("Version"),
            "artifact_digest": ref("Digest"),
            "dependency_lock_digest": ref("Digest"),
            "trust_tier": ref("TrustTier"),
            "provided_capabilities": ref("NonEmptyIdSet"),
            "required_capabilities": ref("IdSet"),
            "dependencies": keyed_set("PluginDependency", key="plugin_id"),
            "exclusive_resources": ref("IdSet"),
            "conflicts_with_plugin_ids": ref("IdSet"),
            "configuration_schema_digest": ref("Digest"),
            "isolation_mode": ref("IsolationMode"),
            "durable_subscriptions": ref("IdSet"),
            "ephemeral_subscriptions": ref("IdSet"),
            "requested_grants": ref("PluginGrantDimensions"),
            "resource_envelope": ref("ResourceEnvelope"),
            "lifecycle_hooks": scalar_set({"enum": ["verify", "stage", "activate", "health", "drain", "revoke", "retire"]}),
            "health_probe_ids": ref("IdSet"),
            "provenance_digest": ref("Digest"),
            "license_id": ref("OpaqueRef"),
            "update_source": nullable(ref("OpaqueRef")),
            "manifest_digest": ref("Digest"),
        },
    )
    defs["PluginGrantEnvelope"] = tagged(
        "PluginGrantEnvelope@1",
        {
            "id": ref("Id"),
            "plugin_id": ref("Id"),
            "artifact_digest": ref("Digest"),
            "dependency_lock_digest": ref("Digest"),
            "grant_epoch": ref("Count"),
            "goal_spec_digest": ref("Digest"),
            "policy_digest": ref("Digest"),
            "dimensions": ref("PluginGrantDimensions"),
            "revoked": {"type": "boolean"},
            "grant_digest": ref("Digest"),
        },
    )
    defs["PluginPolicyEnvelope"] = tagged(
        "PluginPolicyEnvelope@1",
        {
            "id": ref("Id"),
            "goal_spec_digest": ref("Digest"),
            "policy_digest": ref("Digest"),
            "pause_epoch": ref("Count"),
            "allowed_trust_tiers": scalar_set(ref("TrustTier"), minimum=1),
            "allowed_isolation_modes": scalar_set(ref("IsolationMode"), minimum=1),
            "allowed_capabilities": ref("IdSet"),
            "allowed_workspace_paths": ref("OpaqueRefSet"),
            "allowed_network_destinations": ref("OpaqueRefSet"),
            "allowed_credential_refs": ref("OpaqueRefSet"),
            "allowed_model_refs": ref("OpaqueRefSet"),
            "allowed_route_account_refs": ref("OpaqueRefSet"),
            "max_quota_units": nullable(ref("Count")),
            "max_spend_microunits": nullable(ref("Microunits")),
            "update_allowed": {"type": "boolean"},
            "downgrade_allowed": {"type": "boolean"},
            "grant_admin_allowed": {"type": "boolean"},
        },
    )
    lifecycle_states = [
        "discovered", "verified", "admitted", "staged", "active", "quarantined", "rejected",
        "revoked", "drain-and-fence", "retained-evidence", "retired", "replaced",
    ]
    defs["PluginLifecycleRecord"] = tagged(
        "PluginLifecycleRecord@1",
        {
            "plugin_id": ref("Id"), "artifact_digest": ref("Digest"),
            "state": {"enum": lifecycle_states}, "epoch": ref("Count"),
            "packet_epoch": ref("Count"), "lease_epoch": ref("Count"), "subscription_epoch": ref("Count"),
            "replacement_digest": nullable(ref("Digest")),
        },
    )
    defs["PluginResolutionInput"] = tagged(
        "PluginResolutionInput@1",
        {
            "manifests": keyed_set("PluginManifest", key="plugin_id", minimum=1),
            "grants": keyed_set("PluginGrantEnvelope", key="plugin_id"),
            "policy": ref("PluginPolicyEnvelope"),
            "enabled_plugin_ids": ref("NonEmptyIdSet"),
            "lifecycles": keyed_set("PluginLifecycleRecord", key="plugin_id"),
        },
    )
    plugin_reasons = [
        "ambiguous-capability-provider", "capability-denied", "conflict-declared", "dependency-cycle",
        "dependency-digest-mismatch", "dependency-ineligible", "dependency-missing",
        "exclusive-resource-conflict", "grant-context-mismatch", "grant-digest-mismatch",
        "grant-revoked", "isolation-denied", "lifecycle-digest-mismatch", "lifecycle-missing",
        "lifecycle-state-denied", "manifest-digest-mismatch", "manifest-missing",
        "plugin-not-enabled", "policy-limit-exceeded", "required-capability-missing",
        "sensitive-grant-missing", "stale-plugin-epoch", "trust-tier-denied",
        "unknown-capability", "unknown-protocol",
    ]
    defs["PluginReason"] = {"enum": plugin_reasons}
    defs["PluginRejection"] = tagged(
        "PluginRejection@1",
        {"plugin_id": ref("Id"), "reasons": scalar_set(ref("PluginReason"), minimum=1)},
    )
    defs["EffectivePluginGrant"] = tagged(
        "EffectivePluginGrant@1",
        {"plugin_id": ref("Id"), "artifact_digest": ref("Digest"), "dimensions": ref("PluginGrantDimensions")},
    )
    defs["PluginResolutionDecision"] = tagged(
        "PluginResolutionDecision@1",
        {
            "status": {"enum": ["resolved", "blocked"]},
            "activation_order": {"type": "array", "items": ref("Id"), "maxItems": 256, "uniqueItems": True},
            "effective_grants": keyed_set("EffectivePluginGrant", key="plugin_id"),
            "rejections": keyed_set("PluginRejection", key="plugin_id"),
        },
        allOf=[
            {
                "if": {"properties": {"status": {"const": "resolved"}}, "required": ["status"]},
                "then": {
                    "properties": {
                        "activation_order": {"minItems": 1},
                        "effective_grants": {"minItems": 1},
                        "rejections": {"maxItems": 0},
                    }
                },
                "else": {
                    "properties": {
                        "activation_order": {"maxItems": 0},
                        "effective_grants": {"maxItems": 0},
                        "rejections": {"minItems": 1},
                    }
                },
            }
        ],
    )
    zero = {"const": 0}
    defs["DisabledPluginInput"] = tagged(
        "DisabledPluginInput@1",
        {"manifest": ref("PluginManifest"), "installed": {"type": "boolean"}, "enabled": {"const": False}},
    )
    defs["DisabledActivityTrace"] = tagged(
        "DisabledActivityTrace@1",
        {
            "manifest_reads": {"type": "integer", "minimum": 0, "maximum": 1},
            "implementation_imports": zero, "payload_scans": zero, "processes": zero, "threads": zero,
            "timers": zero, "watchers": zero, "network_calls": zero, "credential_reads": zero,
            "quota_reservations": zero, "spend_actions": zero, "cache_writes": zero,
            "context_injections": zero, "tool_registrations": zero, "callbacks": zero,
            "event_subscriptions": zero,
        },
    )
    defs["DisabledPluginDecision"] = tagged(
        "DisabledPluginDecision@1", {"status": {"const": "resolved-disabled"}, "trace": ref("DisabledActivityTrace")}
    )
    defs["BindingEpochs"] = tagged(
        "BindingEpochs@1", {"packet": ref("Count"), "lease": ref("Count"), "subscription": ref("Count")}
    )
    defs["PluginReloadInput"] = tagged(
        "PluginReloadInput@1",
        {
            "old_lifecycle": ref("PluginLifecycleRecord"), "new_manifest": ref("PluginManifest"),
            "grant": ref("PluginGrantEnvelope"), "policy": ref("PluginPolicyEnvelope"),
            "old_binding_epochs": ref("BindingEpochs"),
        },
    )
    defs["PluginReloadDecision"] = tagged(
        "PluginReloadDecision@1",
        {
            "status": {"enum": ["resolved-reload", "blocked"]},
            "events": {"type": "array", "items": {"enum": ["verified", "staged", "drain-and-fence", "replaced", "active"]}, "maxItems": 5},
            "new_epoch": ref("Count"),
            "old_binding_reasons": scalar_set(ref("PluginReason")),
        },
        allOf=[
            {
                "if": {"properties": {"status": {"const": "resolved-reload"}}, "required": ["status"]},
                "then": {
                    "properties": {
                        "events": {
                            "minItems": 5, "maxItems": 5,
                            "prefixItems": [
                                {"const": "verified"}, {"const": "staged"},
                                {"const": "drain-and-fence"}, {"const": "replaced"},
                                {"const": "active"},
                            ],
                            "items": False,
                        },
                        "old_binding_reasons": {"minItems": 1},
                    }
                },
                "else": {
                    "properties": {
                        "events": {"maxItems": 0},
                        "old_binding_reasons": {"minItems": 1},
                    }
                },
            }
        ],
    )

    transport_names = ["pipe", "pty", "conpty"]
    containment_names = ["job-object", "breakaway-prevention", "process-group", "session", "cgroup-v2", "pidfd", "descendant-capture"]
    cancellation_names = ["cooperative", "interrupt", "tree-terminate", "observe-exit"]
    defs["ProcessTransportCapabilityState"] = tagged(
        "ProcessTransportCapabilityState@1", {"name": {"enum": transport_names}, "state": ref("TriState")}
    )
    defs["ProcessContainmentCapabilityState"] = tagged(
        "ProcessContainmentCapabilityState@1", {"name": {"enum": containment_names}, "state": ref("TriState")}
    )
    defs["ProcessCancellationCapabilityState"] = tagged(
        "ProcessCancellationCapabilityState@1", {"name": {"enum": cancellation_names}, "state": ref("TriState")}
    )
    defs["ProcessCapabilityDescriptor"] = tagged(
        "ProcessCapabilityDescriptor@1",
        {
            "id": ref("Id"), "host_id": ref("Id"), "platform": ref("Platform"),
            "platform_version": ref("Version"),
            "eligibility_state": {"enum": ["verified-current", "documented", "observed-uncertain", "stale", "unavailable"]},
            "transport_capabilities": keyed_set("ProcessTransportCapabilityState", key="name", minimum=1),
            "containment_capabilities": keyed_set("ProcessContainmentCapabilityState", key="name", minimum=1),
            "cancellation_capabilities": keyed_set("ProcessCancellationCapabilityState", key="name", minimum=1),
            "evidence": ref("EvidenceBinding"), "descriptor_digest": ref("Digest"),
        },
    )
    defs["ProcessRequirement"] = tagged(
        "ProcessRequirement@1",
        {
            "id": ref("Id"), "actor_id": ref("Id"), "task_id": ref("Id"),
            "work_packet_digest": ref("Digest"), "route_descriptor_digest": ref("Digest"),
            "host_id": ref("Id"), "platform": ref("Platform"),
            "required_transports": scalar_set({"enum": transport_names}, minimum=1),
            "required_containment": scalar_set({"enum": containment_names}, minimum=1),
            "required_cancellation": scalar_set({"enum": cancellation_names}, minimum=1),
            "stdio_encoding": {"const": "utf-8"}, "max_buffer_bytes": ref("PositiveCount"),
            "attach_allowed": {"type": "boolean"}, "operative_pause_policy": {"const": "current-immediate"},
            "representable_future_pause_policies": scalar_set({"enum": ["checkpoint", "interrupt", "drain", "emergency"]}),
        },
    )
    defs["ProcessAdmissionInput"] = tagged(
        "ProcessAdmissionInput@1", {"requirement": ref("ProcessRequirement"), "descriptor": ref("ProcessCapabilityDescriptor")}
    )
    process_reasons = [
        "cancellation-unknown", "cancellation-unsupported", "containment-unknown",
        "containment-unsupported", "descriptor-not-current", "host-mismatch", "platform-mismatch",
        "transport-unknown", "transport-unsupported",
    ]
    defs["ProcessReason"] = {"enum": process_reasons}
    defs["ProcessAdmissionDecision"] = tagged(
        "ProcessAdmissionDecision@1",
        {"status": {"enum": ["admitted", "blocked"]}, "reasons": scalar_set(ref("ProcessReason"))},
        allOf=[
            {
                "if": {"properties": {"status": {"const": "admitted"}}, "required": ["status"]},
                "then": {"properties": {"reasons": {"maxItems": 0}}},
                "else": {"properties": {"reasons": {"minItems": 1}}},
            }
        ],
    )
    defs["ProcessTerminationObservation"] = tagged(
        "ProcessTerminationObservation@1",
        {
            "process_requirement_id": ref("Id"), "process_epoch": ref("Count"),
            "tree_status": {"enum": ["terminated", "partial", "unknown"]},
            "remaining_process_refs": ref("OpaqueRefSet"), "exit_evidence_digest": ref("Digest"),
            "effect_conclusion": {"const": "not-evaluated"},
        },
        allOf=[
            {
                "if": {"properties": {"tree_status": {"const": "terminated"}}, "required": ["tree_status"]},
                "then": {"properties": {"remaining_process_refs": {"maxItems": 0}}},
            },
            {
                "if": {"properties": {"tree_status": {"const": "partial"}}, "required": ["tree_status"]},
                "then": {"properties": {"remaining_process_refs": {"minItems": 1}}},
            },
        ],
    )

    broker_version = {"const": "m1b-broker/1"}
    cursor_unit = {"enum": ["utf8-byte", "event"]}
    dimensions = {"type": "integer", "minimum": 1, "maximum": 1000}
    payload = {"type": "string", "pattern": r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$", "maxLength": 87384, "x-base64MaxDecodedBytes": 65536}
    message_common = {"protocol_version": broker_version}
    defs["BrokerHello"] = tagged("HELLO", {**message_common, "client_id": ref("Id"), "stream_id": ref("Id"), "daemon_epoch": ref("Count"), "last_cursor": ref("Count"), "cursor_unit": cursor_unit, "columns": dimensions, "rows": dimensions, "capabilities": ref("IdSet")})
    defs["BrokerWelcome"] = tagged("WELCOME", {**message_common, "client_id": ref("Id"), "stream_id": ref("Id"), "daemon_epoch": ref("Count"), "replay_floor": ref("Count"), "snapshot_cursor": ref("Count"), "cursor_unit": cursor_unit, "input_lease": nullable(ref("OpaqueRef")), "resize_lease": nullable(ref("OpaqueRef")), "capabilities": ref("IdSet")})
    defs["BrokerSnapshot"] = tagged("SNAPSHOT", {**message_common, "stream_id": ref("Id"), "daemon_epoch": ref("Count"), "cursor": ref("Count"), "cursor_unit": cursor_unit, "snapshot_digest": ref("Digest")})
    defs["BrokerEvent"] = tagged("EVENT", {**message_common, "stream_id": ref("Id"), "daemon_epoch": ref("Count"), "cursor": ref("Count"), "cursor_unit": cursor_unit, "event_class": ref("Id"), "process_id": nullable(ref("Id")), "payload_base64": payload, "payload_untrusted": {"const": True}})
    defs["BrokerAck"] = tagged("ACK", {**message_common, "client_id": ref("Id"), "stream_id": ref("Id"), "daemon_epoch": ref("Count"), "cursor": ref("Count"), "cursor_unit": cursor_unit})
    defs["BrokerCredit"] = tagged("CREDIT", {**message_common, "client_id": ref("Id"), "stream_id": ref("Id"), "daemon_epoch": ref("Count"), "bytes": {"type": "integer", "minimum": 1, "maximum": 16777216}, "events": {"type": "integer", "minimum": 1, "maximum": 65536}})
    defs["BrokerInput"] = tagged("INPUT", {**message_common, "command_id": ref("Id"), "client_id": ref("Id"), "stream_id": ref("Id"), "daemon_epoch": ref("Count"), "process_epoch": ref("Count"), "input_lease": ref("OpaqueRef"), "bytes_base64": payload})
    defs["BrokerResize"] = tagged("RESIZE", {**message_common, "command_id": ref("Id"), "client_id": ref("Id"), "stream_id": ref("Id"), "daemon_epoch": ref("Count"), "process_epoch": ref("Count"), "resize_lease": ref("OpaqueRef"), "columns": dimensions, "rows": dimensions})
    defs["BrokerReset"] = tagged("RESET", {**message_common, "client_id": ref("Id"), "stream_id": ref("Id"), "daemon_epoch": ref("Count"), "reason": {"const": "gap"}, "snapshot_cursor": ref("Count"), "cursor_unit": cursor_unit})
    broker_types = ["BrokerHello", "BrokerWelcome", "BrokerSnapshot", "BrokerEvent", "BrokerAck", "BrokerCredit", "BrokerInput", "BrokerResize", "BrokerReset"]
    defs["BrokerMessage"] = {"oneOf": [ref(name) for name in broker_types]}
    defs["BrokerTraceInput"] = tagged(
        "BrokerTraceInput@1",
        {
            "initial_daemon_epoch": ref("Count"), "initial_process_epoch": ref("Count"),
            "current_input_lease": nullable(ref("OpaqueRef")), "current_resize_lease": nullable(ref("OpaqueRef")),
            "queue_limit_bytes": {"type": "integer", "minimum": 1, "maximum": 16777216},
            "queue_limit_events": {"type": "integer", "minimum": 1, "maximum": 65536},
            "messages": {"type": "array", "items": ref("BrokerMessage"), "minItems": 1, "maxItems": 256},
            "launch_count": ref("Count"), "model_turn_count": ref("Count"),
            "actor_create_count": ref("Count"), "effect_count": ref("Count"),
        },
    )
    broker_reasons = [
        "ack-ahead", "attach-created-work", "client-mismatch", "credit-exhausted",
        "credit-missing", "cursor-nonmonotonic", "cursor-unit-mismatch",
        "duplicate-command-conflict", "output-command-injection", "passive-client-input",
        "replay-gap", "replay-gap-continuation", "stale-daemon-epoch", "stale-lease",
        "stale-process-epoch", "stream-mismatch", "unexpected-reset",
        "utf8-byte-cursor-mismatch", "welcome-lease-mismatch",
    ]
    defs["BrokerReason"] = {"enum": broker_reasons}
    defs["BrokerTraceDecision"] = tagged(
        "BrokerTraceDecision@1",
        {
            "status": {"enum": ["accepted", "accepted-reset", "refused"]},
            "reasons": scalar_set(ref("BrokerReason")), "final_cursor": ref("Count"),
            "cursor_unit": cursor_unit, "launch_count": ref("Count"),
            "model_turn_count": ref("Count"), "actor_create_count": ref("Count"),
            "effect_count": ref("Count"), "requires_reset": {"type": "boolean"},
        },
        allOf=[
            {
                "if": {"properties": {"status": {"const": "accepted"}}, "required": ["status"]},
                "then": {
                    "properties": {"reasons": {"maxItems": 0}, "requires_reset": {"const": False}}
                },
            },
            {
                "if": {"properties": {"status": {"const": "accepted-reset"}}, "required": ["status"]},
                "then": {
                    "properties": {"reasons": {"minItems": 1}, "requires_reset": {"const": True}}
                },
            },
            {
                "if": {"properties": {"status": {"const": "refused"}}, "required": ["status"]},
                "then": {"properties": {"reasons": {"minItems": 1}}},
            },
        ],
    )

    common_fixture = {
        "fixture_id": {"type": "string", "pattern": r"^F-M1B-[0-9]{3}$"},
        "purpose": ref("Text"), "source_requirement_ids": ref("NonEmptyIdSet"),
    }
    fixture_arms = [
        ("RouteFixtureBundle", "RouteFixtureBundle@1", "RouteResolutionInput", "RouteResolutionDecision", None),
        ("PluginFixtureBundle", "PluginFixtureBundle@1", "PluginResolutionInput", "PluginResolutionDecision", None),
        ("DisabledPluginFixtureBundle", "DisabledPluginFixtureBundle@1", "DisabledPluginInput", "DisabledPluginDecision", None),
        ("PluginReloadFixtureBundle", "PluginReloadFixtureBundle@1", "PluginReloadInput", "PluginReloadDecision", None),
        ("ProcessFixtureBundle", "ProcessFixtureBundle@1", "ProcessAdmissionInput", "ProcessAdmissionDecision", "termination_observation"),
        ("BrokerFixtureBundle", "BrokerFixtureBundle@1", "BrokerTraceInput", "BrokerTraceDecision", None),
    ]
    for name, tag, input_name, decision_name, optional_name in fixture_arms:
        properties = {**common_fixture, "input": ref(input_name), "expected": ref(decision_name)}
        if optional_name:
            properties[optional_name] = nullable(ref("ProcessTerminationObservation"))
        defs[name] = tagged(tag, properties)
        if name == "ProcessFixtureBundle":
            defs[name]["x-processFixtureInvariant"] = True
    defs["M1BFixtureBundle"] = {"oneOf": [ref(row[0]) for row in fixture_arms]}
    defs["FixtureManifestEntry"] = tagged(
        "FixtureManifestEntry@1",
        {"fixture_id": {"type": "string", "pattern": r"^F-M1B-[0-9]{3}$"}, "path": ref("OpaqueRef"), "digest": ref("Digest"), "bundle_type": {"enum": [row[1] for row in fixture_arms]}},
    )
    defs["FixtureManifest"] = tagged(
        "FixtureManifest@1",
        {"schema_digest": ref("Digest"), "fixtures": keyed_set("FixtureManifestEntry", key="fixture_id", minimum=24, maximum=24)},
    )

    public = [
        "RouteComponentCatalog", "RouteCapabilityDescriptor", "RouteRequirement", "RoutePolicyEnvelope",
        "RouteResolutionInput", "RouteResolutionDecision", "PluginManifest", "PluginGrantEnvelope",
        "PluginPolicyEnvelope", "PluginLifecycleRecord", "PluginResolutionInput", "PluginResolutionDecision",
        "DisabledPluginInput", "DisabledPluginDecision", "PluginReloadInput", "PluginReloadDecision",
        "ProcessCapabilityDescriptor", "ProcessRequirement", "ProcessAdmissionInput", "ProcessAdmissionDecision",
        "ProcessTerminationObservation", "BrokerMessage", "BrokerTraceInput", "BrokerTraceDecision",
        "M1BFixtureBundle", "FixtureManifest",
    ]
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_ID,
        "title": "Recursion v3 M1B execution requirement contracts",
        "oneOf": [ref(name) for name in public],
        "$defs": defs,
    }


def encoded() -> bytes:
    return (json.dumps(build_schema(), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def main(argv: list[str]) -> int:
    if argv == ["--write"]:
        OUTPUT.write_bytes(encoded())
        print("M1B_SCHEMA_MATERIALIZED")
        return 0
    if argv == ["--check"]:
        if not OUTPUT.exists() or OUTPUT.read_bytes() != encoded():
            print("M1B_SCHEMA_MATERIALIZATION_MISMATCH", file=sys.stderr)
            return 1
        print("M1B_SCHEMA_MATERIALIZATION_PASS")
        return 0
    print("usage: materialize.py --write | --check", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
