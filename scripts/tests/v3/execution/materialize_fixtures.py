#!/usr/bin/env python3
"""Materialize the 24 closed, sanitized M1B execution-contract fixtures."""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FIXTURES = HERE / "fixtures"
SCHEMA_PATH = ROOT / "schemas" / "control-plane" / "v3" / "execution" / "schema.json"
D1 = "sha256:" + "1" * 64
D2 = "sha256:" + "2" * 64
D3 = "sha256:" + "3" * 64


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def seal(value: dict[str, Any], field: str) -> dict[str, Any]:
    value[field] = digest_bytes(canonical_bytes({key: item for key, item in value.items() if key != field}))
    return value


def rendered(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def evidence(source: str) -> dict[str, Any]:
    return {
        "type": "EvidenceBinding@1", "source_ids": [source],
        "observed_at": "2026-09-04T00:00:00Z", "expires_at": None,
        "evidence_digest": D1,
    }


def state(name: str, value: str = "supported", kind: str = "CapabilityState@1") -> dict[str, Any]:
    return {"type": kind, "name": name, "state": value}


def route_catalog() -> dict[str, Any]:
    return {
        "type": "RouteComponentCatalog@1",
        "engines": [
            {"type": "EngineDescriptor@1", "id": "engine-a", "protocol_versions": ["v1"], "capabilities": ["chat", "tools"]},
            {"type": "EngineDescriptor@1", "id": "engine-b", "protocol_versions": ["v1"], "capabilities": ["chat"]},
        ],
        "providers": [
            {"type": "ProviderDescriptor@1", "id": "provider-a", "endpoint_ids": ["endpoint:a"], "privacy_classes": ["private", "public"]},
            {"type": "ProviderDescriptor@1", "id": "provider-b", "endpoint_ids": ["endpoint:b"], "privacy_classes": ["public"]},
        ],
        "models": [
            {"type": "ModelDescriptor@1", "id": "model-a", "provider_id": "provider-a", "capabilities": ["chat", "tools"], "reasoning_modes": ["high"]},
            {"type": "ModelDescriptor@1", "id": "model-b", "provider_id": "provider-b", "capabilities": ["chat"], "reasoning_modes": ["medium"]},
        ],
        "pools": [
            {"type": "CapacityPoolDescriptor@1", "id": "pool-a", "billing_basis": "subscription", "account_ref": "account:a", "model_ids": ["model-a"], "state": "available", "remaining_units": 100, "metered_limit_microunits": None},
            {"type": "CapacityPoolDescriptor@1", "id": "pool-b", "billing_basis": "metered", "account_ref": "account:b", "model_ids": ["model-b"], "state": "available", "remaining_units": 100, "metered_limit_microunits": 1000},
        ],
        "hosts": [
            {"type": "HostDescriptor@1", "id": "host-a", "platform": "windows", "capabilities": ["local"]},
            {"type": "HostDescriptor@1", "id": "host-b", "platform": "linux", "capabilities": ["remote"]},
        ],
        "sandboxes": [
            {"type": "SandboxDescriptor@1", "id": "sandbox-a", "filesystem_mode": "workspace-write", "network_mode": "allowlist", "process_mode": "isolated", "allowed_paths": ["workspace:/repo"], "allowed_destinations": ["endpoint:a"], "capabilities": ["network-allowlist", "workspace-write"]},
            {"type": "SandboxDescriptor@1", "id": "sandbox-b", "filesystem_mode": "read-only", "network_mode": "allowlist", "process_mode": "isolated", "allowed_paths": ["workspace:/repo"], "allowed_destinations": ["endpoint:b"], "capabilities": ["network-allowlist"]},
        ],
    }


def route_descriptor(route_id: str) -> dict[str, Any]:
    first = route_id == "route-a"
    value = {
        "type": "RouteCapabilityDescriptor@1", "id": route_id,
        "engine_id": "engine-a" if first else "engine-b",
        "provider_id": "provider-a" if first else "provider-b",
        "model_id": "model-a" if first else "model-b",
        "pool_id": "pool-a" if first else "pool-b",
        "account_ref": "account:a" if first else "account:b",
        "host_id": "host-a" if first else "host-b",
        "sandbox_id": "sandbox-a" if first else "sandbox-b",
        "eligibility_state": "verified-current",
        "capabilities": [state("chat"), state("tools", "supported" if first else "unsupported")],
        "privacy_classes": ["private", "public"] if first else ["public"],
        "egress_destinations": ["endpoint:a" if first else "endpoint:b"],
        "billing_control": "verified", "evidence": evidence("src-v3-001"),
        "descriptor_digest": D1,
    }
    return seal(value, "descriptor_digest")


def route_requirement() -> dict[str, Any]:
    return {
        "type": "RouteRequirement@1", "id": "route-requirement", "required_capabilities": ["chat"],
        "privacy_class": "private", "allowed_billing": ["metered", "subscription"],
        "allowed_route_ids": ["route-a", "route-b"], "allowed_host_ids": ["host-a", "host-b"],
        "allowed_egress_destinations": ["endpoint:a", "endpoint:b"],
        "estimated_metered_microunits": 100, "max_metered_microunits": 500,
        "required_sandbox_capabilities": ["network-allowlist"],
    }


def route_policy() -> dict[str, Any]:
    return {
        "type": "RoutePolicyEnvelope@1", "id": "route-policy", "goal_spec_digest": D1,
        "authority_digest": D2, "policy_digest": D3, "permitted_route_ids": ["route-a", "route-b"],
        "permitted_host_ids": ["host-a", "host-b"], "permitted_account_refs": ["account:a", "account:b"],
        "permitted_egress_destinations": ["endpoint:a", "endpoint:b"], "metered_authorized": False,
        "max_metered_microunits": None, "pause_epoch": 0,
    }


def route_input() -> dict[str, Any]:
    return {
        "type": "RouteResolutionInput@1", "catalog": route_catalog(),
        "descriptors": [route_descriptor("route-a"), route_descriptor("route-b")],
        "requirement": route_requirement(), "policy": route_policy(),
        "ranked_route_ids": ["route-a", "route-b"],
    }


def route_evaluation(route_id: str, reasons: list[str]) -> dict[str, Any]:
    return {"type": "RouteCandidateEvaluation@1", "route_id": route_id, "eligible": not reasons, "reasons": sorted(reasons)}


def route_decision(evaluations: list[dict[str, Any]], selected: str | None = None) -> dict[str, Any]:
    return {"type": "RouteResolutionDecision@1", "status": "selected" if selected else "blocked", "selected_route_id": selected, "candidate_evaluations": evaluations}


def fixture(tag: str, fixture_id: str, purpose: str, source_ids: list[str], input_value: dict[str, Any], expected: dict[str, Any], **extra: Any) -> dict[str, Any]:
    return {"type": tag, "fixture_id": fixture_id, "purpose": purpose, "source_requirement_ids": sorted(source_ids), "input": input_value, "expected": expected, **extra}


def route_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    value = route_input()
    rows.append(fixture("RouteFixtureBundle@1", "F-M1B-001", "Select first explicitly ranked fully eligible subscription route.", ["m1b-route-eligibility"], value, route_decision([route_evaluation("route-a", []), route_evaluation("route-b", ["metered-not-authorized", "privacy-mismatch"])], "route-a")))

    value = route_input()
    value["catalog"]["pools"][0]["state"] = "exhausted"
    value["catalog"]["pools"][0]["remaining_units"] = 0
    value["requirement"]["privacy_class"] = "public"
    rows.append(fixture("RouteFixtureBundle@1", "F-M1B-002", "Exhausted subscription does not authorize metered fallback.", ["m1b-billing-boundary"], value, route_decision([route_evaluation("route-a", ["pool-exhausted"]), route_evaluation("route-b", ["metered-not-authorized"])])))

    value = route_input()
    value["descriptors"] = [value["descriptors"][0]]
    value["descriptors"][0]["eligibility_state"] = "stale"
    value["descriptors"][0] = seal(value["descriptors"][0], "descriptor_digest")
    value["ranked_route_ids"] = ["route-a"]
    rows.append(fixture("RouteFixtureBundle@1", "F-M1B-003", "Stale route evidence blocks autonomous selection.", ["m1b-route-freshness"], value, route_decision([route_evaluation("route-a", ["descriptor-stale"])])))

    value = route_input()
    value["descriptors"] = [value["descriptors"][1]]
    value["ranked_route_ids"] = ["route-b"]
    value["policy"]["metered_authorized"] = True
    value["policy"]["max_metered_microunits"] = 500
    rows.append(fixture("RouteFixtureBundle@1", "F-M1B-004", "Private data cannot use a public-only route.", ["m1b-privacy"], value, route_decision([route_evaluation("route-b", ["privacy-mismatch"])])))

    value = route_input()
    value["descriptors"] = [value["descriptors"][0]]
    value["descriptors"][0]["billing_control"] = "unknown"
    value["descriptors"][0] = seal(value["descriptors"][0], "descriptor_digest")
    value["ranked_route_ids"] = ["route-a"]
    rows.append(fixture("RouteFixtureBundle@1", "F-M1B-005", "Unknown billing evidence is not free or subscription authority.", ["m1b-billing-boundary"], value, route_decision([route_evaluation("route-a", ["billing-unknown"])])))

    value = route_input()
    value["descriptors"] = [value["descriptors"][0]]
    value["descriptors"][0]["eligibility_state"] = "unavailable"
    value["descriptors"][0] = seal(value["descriptors"][0], "descriptor_digest")
    value["ranked_route_ids"] = ["route-a"]
    rows.append(fixture("RouteFixtureBundle@1", "F-M1B-006", "Unavailable preferred route does not create an unlisted substitute.", ["m1b-no-substitution"], value, route_decision([route_evaluation("route-a", ["route-unavailable"])])))

    value = route_input()
    value["descriptors"] = [value["descriptors"][1]]
    value["ranked_route_ids"] = ["route-b"]
    value["requirement"]["privacy_class"] = "public"
    value["requirement"]["required_capabilities"] = ["chat", "tools"]
    value["policy"]["metered_authorized"] = True
    value["policy"]["max_metered_microunits"] = 500
    rows.append(fixture("RouteFixtureBundle@1", "F-M1B-007", "Unsupported required capability blocks with an exact reason.", ["m1b-route-capability"], value, route_decision([route_evaluation("route-b", ["capability-unsupported"])])))

    value = route_input()
    value["descriptors"] = [value["descriptors"][0]]
    value["descriptors"][0]["model_id"] = "model-b"
    value["descriptors"][0] = seal(value["descriptors"][0], "descriptor_digest")
    value["ranked_route_ids"] = ["route-a"]
    rows.append(fixture("RouteFixtureBundle@1", "F-M1B-008", "Cross-component mismatch cannot hide behind a sealed descriptor.", ["m1b-route-components"], value, route_decision([route_evaluation("route-a", ["component-mismatch"])])))
    return rows


def grants(**changes: Any) -> dict[str, Any]:
    value = {
        "type": "PluginGrantDimensions@1", "functional_capabilities": ["render"],
        "workspace_paths": ["workspace:/repo"], "network_destinations": [], "credential_refs": [],
        "model_refs": [], "route_account_refs": [], "quota_units": None, "spend_microunits": None,
        "update": False, "downgrade": False, "grant_admin": False,
    }
    value.update(changes)
    return value


def resources() -> dict[str, Any]:
    return {"type": "ResourceEnvelope@1", "max_cpu_millis": 100, "max_memory_bytes": 1048576, "max_disk_bytes": 1048576, "max_concurrency": 1, "max_queue_events": 64, "max_queue_bytes": 65536}


def plugin_manifest(plugin_id: str, *, provided: list[str] | None = None, dependencies: list[dict[str, Any]] | None = None, exclusive: list[str] | None = None, conflicts: list[str] | None = None, requested: dict[str, Any] | None = None, artifact: str | None = None) -> dict[str, Any]:
    value = {
        "type": "PluginManifest@1", "id": f"manifest-{plugin_id}", "plugin_id": plugin_id,
        "version": "1.0.0", "protocol_version": "m1b-plugin/1", "artifact_digest": artifact or D1,
        "dependency_lock_digest": D2, "trust_tier": "T2-signed-isolated-third-party",
        "provided_capabilities": provided or ["render"], "required_capabilities": [],
        "dependencies": dependencies or [], "exclusive_resources": exclusive or [],
        "conflicts_with_plugin_ids": conflicts or [], "configuration_schema_digest": D3,
        "isolation_mode": "isolated-subprocess", "durable_subscriptions": [],
        "ephemeral_subscriptions": [], "requested_grants": requested or grants(),
        "resource_envelope": resources(), "lifecycle_hooks": ["activate", "drain", "retire", "stage", "verify"],
        "health_probe_ids": [], "provenance_digest": D3, "license_id": "MIT", "update_source": None,
        "manifest_digest": D1,
    }
    return seal(value, "manifest_digest")


def plugin_grant(manifest: dict[str, Any], dimensions: dict[str, Any] | None = None, **changes: Any) -> dict[str, Any]:
    value = {
        "type": "PluginGrantEnvelope@1", "id": f"grant-{manifest['plugin_id']}",
        "plugin_id": manifest["plugin_id"], "artifact_digest": manifest["artifact_digest"],
        "dependency_lock_digest": manifest["dependency_lock_digest"], "grant_epoch": 1,
        "goal_spec_digest": D1, "policy_digest": D2, "dimensions": dimensions or copy.deepcopy(manifest["requested_grants"]),
        "revoked": False, "grant_digest": D1,
    }
    value.update(changes)
    return seal(value, "grant_digest")


def plugin_policy() -> dict[str, Any]:
    return {
        "type": "PluginPolicyEnvelope@1", "id": "plugin-policy", "goal_spec_digest": D1,
        "policy_digest": D2, "pause_epoch": 0,
        "allowed_trust_tiers": ["T1-signed-built-in", "T2-signed-isolated-third-party", "T3-untrusted-view"],
        "allowed_isolation_modes": ["isolated-subprocess", "metadata-only", "sandboxed-view", "typed-in-process"],
        "allowed_capabilities": ["index", "render"], "allowed_workspace_paths": ["workspace:/repo"],
        "allowed_network_destinations": ["endpoint:a"], "allowed_credential_refs": ["credential:a"],
        "allowed_model_refs": ["model:a"], "allowed_route_account_refs": ["route-account:a"],
        "max_quota_units": 100, "max_spend_microunits": 1000, "update_allowed": False,
        "downgrade_allowed": False, "grant_admin_allowed": False,
    }


def lifecycle(manifest: dict[str, Any], epoch: int = 1, state_name: str = "verified") -> dict[str, Any]:
    return {"type": "PluginLifecycleRecord@1", "plugin_id": manifest["plugin_id"], "artifact_digest": manifest["artifact_digest"], "state": state_name, "epoch": epoch, "packet_epoch": epoch, "lease_epoch": epoch, "subscription_epoch": epoch, "replacement_digest": None}


def effective(manifest: dict[str, Any], dims: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"type": "EffectivePluginGrant@1", "plugin_id": manifest["plugin_id"], "artifact_digest": manifest["artifact_digest"], "dimensions": dims or copy.deepcopy(manifest["requested_grants"])}


def rejection(plugin_id: str, reasons: list[str]) -> dict[str, Any]:
    return {"type": "PluginRejection@1", "plugin_id": plugin_id, "reasons": sorted(reasons)}


def plugin_input(manifests: list[dict[str, Any]], grants_list: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    ordered_manifests = sorted(manifests, key=lambda item: item["plugin_id"])
    return {
        "type": "PluginResolutionInput@1", "manifests": ordered_manifests,
        "grants": sorted(grants_list if grants_list is not None else [plugin_grant(item) for item in ordered_manifests], key=lambda item: item["plugin_id"]),
        "policy": plugin_policy(), "enabled_plugin_ids": sorted(item["plugin_id"] for item in ordered_manifests),
        "lifecycles": sorted([lifecycle(item) for item in ordered_manifests], key=lambda item: item["plugin_id"]),
    }


def plugin_decision(status: str, order: list[str] | None = None, effective_grants: list[dict[str, Any]] | None = None, rejections: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"type": "PluginResolutionDecision@1", "status": status, "activation_order": order or [], "effective_grants": sorted(effective_grants or [], key=lambda item: item["plugin_id"]), "rejections": sorted(rejections or [], key=lambda item: item["plugin_id"])}


def plugin_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    core = plugin_manifest("plugin-core", provided=["index"], requested=grants(functional_capabilities=["index"]))
    dep = {"type": "PluginDependency@1", "plugin_id": "plugin-core", "artifact_digest": core["artifact_digest"], "dependency_lock_digest": core["dependency_lock_digest"]}
    view = plugin_manifest("plugin-view", dependencies=[dep])
    value = plugin_input([core, view])
    rows.append(fixture("PluginFixtureBundle@1", "F-M1B-009", "Resolve valid manifest graph in dependency order.", ["m1b-plugin-graph"], value, plugin_decision("resolved", ["plugin-core", "plugin-view"], [effective(core), effective(view)])))

    missing_dep = {"type": "PluginDependency@1", "plugin_id": "plugin-missing", "artifact_digest": D1, "dependency_lock_digest": D2}
    view_missing = plugin_manifest("plugin-view", dependencies=[missing_dep])
    value = plugin_input([view_missing])
    rows.append(fixture("PluginFixtureBundle@1", "F-M1B-010", "Reject missing dependency before import.", ["m1b-plugin-graph"], value, plugin_decision("blocked", rejections=[rejection("plugin-view", ["dependency-missing"])])))

    dep_a = {"type": "PluginDependency@1", "plugin_id": "plugin-b", "artifact_digest": D1, "dependency_lock_digest": D2}
    dep_b = {"type": "PluginDependency@1", "plugin_id": "plugin-a", "artifact_digest": D1, "dependency_lock_digest": D2}
    plugin_a = plugin_manifest("plugin-a", dependencies=[dep_a])
    plugin_b = plugin_manifest("plugin-b", dependencies=[dep_b])
    value = plugin_input([plugin_a, plugin_b])
    rows.append(fixture("PluginFixtureBundle@1", "F-M1B-011", "Reject every member of a dependency cycle.", ["m1b-plugin-graph"], value, plugin_decision("blocked", rejections=[rejection("plugin-a", ["dependency-cycle"]), rejection("plugin-b", ["dependency-cycle"])])))

    plugin_a = plugin_manifest("plugin-a", exclusive=["terminal-input"])
    plugin_b = plugin_manifest("plugin-b", exclusive=["terminal-input"])
    value = plugin_input([plugin_a, plugin_b])
    rows.append(fixture("PluginFixtureBundle@1", "F-M1B-012", "Reject unordered exclusive resource ownership.", ["m1b-plugin-conflict"], value, plugin_decision("blocked", rejections=[rejection("plugin-a", ["exclusive-resource-conflict"]), rejection("plugin-b", ["exclusive-resource-conflict"])])))

    view = plugin_manifest("plugin-view")
    wrong = plugin_grant(view, artifact_digest=D3)
    value = plugin_input([view], [wrong])
    rows.append(fixture("PluginFixtureBundle@1", "F-M1B-013", "Reject digest-bound grant after artifact substitution.", ["m1b-plugin-integrity"], value, plugin_decision("blocked", rejections=[rejection("plugin-view", ["grant-digest-mismatch"])])))

    requested = grants(network_destinations=["endpoint:a"])
    view = plugin_manifest("plugin-view", requested=requested)
    functional_only = grants()
    value = plugin_input([view], [plugin_grant(view, functional_only)])
    rows.append(fixture("PluginFixtureBundle@1", "F-M1B-014", "Functional acknowledgement does not imply sensitive grants.", ["m1b-plugin-grants"], value, plugin_decision("blocked", rejections=[rejection("plugin-view", ["sensitive-grant-missing"])])))

    view = plugin_manifest("plugin-view")
    disabled_input = {"type": "DisabledPluginInput@1", "manifest": view, "installed": True, "enabled": False}
    trace = {"type": "DisabledActivityTrace@1", "manifest_reads": 1}
    for key in ["implementation_imports", "payload_scans", "processes", "threads", "timers", "watchers", "network_calls", "credential_reads", "quota_reservations", "spend_actions", "cache_writes", "context_injections", "tool_registrations", "callbacks", "event_subscriptions"]:
        trace[key] = 0
    disabled_decision = {"type": "DisabledPluginDecision@1", "status": "resolved-disabled", "trace": trace}
    rows.append(fixture("DisabledPluginFixtureBundle@1", "F-M1B-015", "Disabled installed plugin performs metadata work only.", ["m1b-disabled-path"], disabled_input, disabled_decision))

    old = plugin_manifest("plugin-view", artifact=D1)
    new = plugin_manifest("plugin-view", artifact=D3)
    old_lifecycle = lifecycle(old, epoch=1, state_name="active")
    old_lifecycle["replacement_digest"] = new["artifact_digest"]
    grant = plugin_grant(new, grant_epoch=2)
    reload_input = {"type": "PluginReloadInput@1", "old_lifecycle": old_lifecycle, "new_manifest": new, "grant": grant, "policy": plugin_policy(), "old_binding_epochs": {"type": "BindingEpochs@1", "packet": 1, "lease": 1, "subscription": 1}}
    reload_decision = {"type": "PluginReloadDecision@1", "status": "resolved-reload", "events": ["verified", "staged", "drain-and-fence", "replaced", "active"], "new_epoch": 2, "old_binding_reasons": ["stale-plugin-epoch"]}
    rows.append(fixture("PluginReloadFixtureBundle@1", "F-M1B-016", "Reload fences every old binding before new activation.", ["m1b-plugin-lifecycle"], reload_input, reload_decision))
    return rows


def process_descriptor(platform: str = "windows") -> dict[str, Any]:
    windows = platform == "windows"
    value = {
        "type": "ProcessCapabilityDescriptor@1", "id": f"process-profile-{platform}",
        "host_id": f"host-{platform}", "platform": platform, "platform_version": "synthetic-1",
        "eligibility_state": "verified-current",
        "transport_capabilities": [state("conpty" if windows else "pty", kind="ProcessTransportCapabilityState@1")],
        "containment_capabilities": [
            state("breakaway-prevention", kind="ProcessContainmentCapabilityState@1"),
            state("descendant-capture", kind="ProcessContainmentCapabilityState@1"),
            state("job-object" if windows else "cgroup-v2", kind="ProcessContainmentCapabilityState@1"),
        ],
        "cancellation_capabilities": [
            state("observe-exit", kind="ProcessCancellationCapabilityState@1"),
            state("tree-terminate", kind="ProcessCancellationCapabilityState@1"),
        ],
        "evidence": evidence("src-v3-021" if windows else "src-v3-023"), "descriptor_digest": D1,
    }
    value["containment_capabilities"] = sorted(value["containment_capabilities"], key=lambda item: item["name"])
    return seal(value, "descriptor_digest")


def process_requirement(platform: str = "windows") -> dict[str, Any]:
    windows = platform == "windows"
    return {
        "type": "ProcessRequirement@1", "id": f"process-requirement-{platform}", "actor_id": "actor-a",
        "task_id": "task-a", "work_packet_digest": D1, "route_descriptor_digest": D2,
        "host_id": f"host-{platform}", "platform": platform,
        "required_transports": ["conpty" if windows else "pty"],
        "required_containment": sorted(["breakaway-prevention", "descendant-capture", "job-object"] if windows else ["cgroup-v2", "descendant-capture"]),
        "required_cancellation": ["observe-exit", "tree-terminate"], "stdio_encoding": "utf-8",
        "max_buffer_bytes": 65536, "attach_allowed": True, "operative_pause_policy": "current-immediate",
        "representable_future_pause_policies": ["checkpoint", "drain", "emergency", "interrupt"],
    }


def process_decision(reasons: list[str]) -> dict[str, Any]:
    return {"type": "ProcessAdmissionDecision@1", "status": "blocked" if reasons else "admitted", "reasons": sorted(reasons)}


def broker_message(tag: str, **values: Any) -> dict[str, Any]:
    return {"type": tag, "protocol_version": "m1b-broker/1", **values}


def broker_input(messages: list[dict[str, Any]], *, input_lease: str | None = "lease:input:2", resize_lease: str | None = "lease:resize:2", queue_bytes: int = 64, queue_events: int = 4) -> dict[str, Any]:
    return {"type": "BrokerTraceInput@1", "initial_daemon_epoch": 2, "initial_process_epoch": 2, "current_input_lease": input_lease, "current_resize_lease": resize_lease, "queue_limit_bytes": queue_bytes, "queue_limit_events": queue_events, "messages": messages, "launch_count": 0, "model_turn_count": 0, "actor_create_count": 0, "effect_count": 0}


def broker_decision(status: str, reasons: list[str], cursor: int, unit: str, reset: bool) -> dict[str, Any]:
    return {"type": "BrokerTraceDecision@1", "status": status, "reasons": sorted(reasons), "final_cursor": cursor, "cursor_unit": unit, "launch_count": 0, "model_turn_count": 0, "actor_create_count": 0, "effect_count": 0, "requires_reset": reset}


def process_and_broker_fixtures() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    requirement = process_requirement("windows")
    descriptor = process_descriptor("windows")
    value = {"type": "ProcessAdmissionInput@1", "requirement": requirement, "descriptor": descriptor}
    rows.append(fixture("ProcessFixtureBundle@1", "F-M1B-017", "Admit explicit synthetic Windows capability evidence.", ["m1b-process-capability"], value, process_decision([]), termination_observation=None))

    requirement = process_requirement("windows")
    descriptor = process_descriptor("windows")
    next(item for item in descriptor["containment_capabilities"] if item["name"] == "breakaway-prevention")["state"] = "unknown"
    descriptor = seal(descriptor, "descriptor_digest")
    value = {"type": "ProcessAdmissionInput@1", "requirement": requirement, "descriptor": descriptor}
    rows.append(fixture("ProcessFixtureBundle@1", "F-M1B-018", "Unknown Job breakaway protection blocks containment.", ["m1b-process-capability"], value, process_decision(["containment-unknown"]), termination_observation=None))

    requirement = process_requirement("linux")
    descriptor = process_descriptor("linux")
    next(item for item in descriptor["containment_capabilities"] if item["name"] == "cgroup-v2")["state"] = "unsupported"
    descriptor = seal(descriptor, "descriptor_digest")
    value = {"type": "ProcessAdmissionInput@1", "requirement": requirement, "descriptor": descriptor}
    rows.append(fixture("ProcessFixtureBundle@1", "F-M1B-019", "PTY evidence cannot substitute for required cgroup containment.", ["m1b-process-capability"], value, process_decision(["containment-unsupported"]), termination_observation=None))

    messages = [
        broker_message("HELLO", client_id="client-a", stream_id="stream-a", daemon_epoch=2, last_cursor=0, cursor_unit="event", columns=80, rows=24, capabilities=["attach"]),
        broker_message("WELCOME", client_id="client-a", stream_id="stream-a", daemon_epoch=2, replay_floor=0, snapshot_cursor=0, cursor_unit="event", input_lease=None, resize_lease=None, capabilities=["attach"]),
    ]
    value = broker_input(messages, input_lease=None, resize_lease=None)
    rows.append(fixture("BrokerFixtureBundle@1", "F-M1B-020", "Attach and detach are view-only and create no work.", ["m1b-broker-attach"], value, broker_decision("accepted", [], 0, "event", False)))

    messages = [broker_message("INPUT", command_id="command-a", client_id="client-a", stream_id="stream-a", daemon_epoch=2, process_epoch=2, input_lease="lease:input:1", bytes_base64=base64.b64encode(b"x").decode())]
    value = broker_input(messages)
    rows.append(fixture("BrokerFixtureBundle@1", "F-M1B-021", "Stale input lease is refused.", ["m1b-broker-lease"], value, broker_decision("refused", ["stale-lease"], 0, "event", False)))

    messages = [
        broker_message("CREDIT", client_id="client-a", stream_id="stream-a", daemon_epoch=2, bytes=4, events=1),
        broker_message("EVENT", stream_id="stream-a", daemon_epoch=2, cursor=1, cursor_unit="event", event_class="output", process_id="process-a", payload_base64=base64.b64encode(b"overflow").decode(), payload_untrusted=True),
        broker_message("RESET", client_id="client-a", stream_id="stream-a", daemon_epoch=2, reason="gap", snapshot_cursor=1, cursor_unit="event"),
    ]
    value = broker_input(messages, queue_bytes=4, queue_events=1)
    rows.append(fixture("BrokerFixtureBundle@1", "F-M1B-022", "Slow client exhaustion requires explicit reset and gap.", ["m1b-broker-flow"], value, broker_decision("accepted-reset", ["credit-exhausted"], 1, "event", True)))

    snowman = "☃".encode("utf-8")
    messages = [broker_message("EVENT", stream_id="stream-a", daemon_epoch=2, cursor=len(snowman), cursor_unit="utf8-byte", event_class="output", process_id="process-a", payload_base64=base64.b64encode(snowman).decode(), payload_untrusted=True)]
    value = broker_input(messages)
    rows.append(fixture("BrokerFixtureBundle@1", "F-M1B-023", "Raw output cursor counts UTF-8 bytes rather than characters.", ["m1b-broker-cursor"], value, broker_decision("accepted", [], 3, "utf8-byte", False)))

    requirement = process_requirement("windows")
    descriptor = process_descriptor("windows")
    value = {"type": "ProcessAdmissionInput@1", "requirement": requirement, "descriptor": descriptor}
    termination = {"type": "ProcessTerminationObservation@1", "process_requirement_id": requirement["id"], "process_epoch": 2, "tree_status": "terminated", "remaining_process_refs": [], "exit_evidence_digest": D3, "effect_conclusion": "not-evaluated"}
    rows.append(fixture("ProcessFixtureBundle@1", "F-M1B-024", "Immediate PAUSE and termination never infer an external effect outcome.", ["m1b-current-pause", "m1b-process-effect-separation"], value, process_decision([]), termination_observation=termination))
    return rows


def build_fixtures() -> list[dict[str, Any]]:
    values = route_fixtures() + plugin_fixtures() + process_and_broker_fixtures()
    assert [item["fixture_id"] for item in values] == [f"F-M1B-{number:03d}" for number in range(1, 25)]
    return values


def build_outputs() -> dict[Path, bytes]:
    fixtures = build_fixtures()
    outputs = {FIXTURES / f"{item['fixture_id']}.json": rendered(item) for item in fixtures}
    entries = []
    for item in fixtures:
        path = FIXTURES / f"{item['fixture_id']}.json"
        entries.append({"type": "FixtureManifestEntry@1", "fixture_id": item["fixture_id"], "path": path.name, "digest": digest_bytes(outputs[path]), "bundle_type": item["type"]})
    manifest = {"type": "FixtureManifest@1", "schema_digest": digest_bytes(SCHEMA_PATH.read_bytes()), "fixtures": entries}
    outputs[FIXTURES / "manifest.json"] = rendered(manifest)
    return outputs


def write() -> int:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    expected = build_outputs()
    for path, data in expected.items():
        path.write_bytes(data)
    for existing in FIXTURES.glob("F-M1B-*.json"):
        if existing not in expected:
            existing.unlink()
    print(f"M1B_FIXTURES_MATERIALIZED count={len(expected) - 1}")
    return 0


def check() -> int:
    expected = build_outputs()
    mismatches = [str(path) for path, data in expected.items() if not path.exists() or path.read_bytes() != data]
    extras = [str(path) for path in FIXTURES.glob("F-M1B-*.json") if path not in expected]
    if mismatches or extras:
        for path in sorted(mismatches + extras):
            print(path, file=sys.stderr)
        print("M1B_FIXTURE_MATERIALIZATION_MISMATCH", file=sys.stderr)
        return 1
    print(f"M1B_FIXTURE_MATERIALIZATION_PASS count={len(expected) - 1}")
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
