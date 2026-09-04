#!/usr/bin/env python3
"""Deterministic, test-only reference oracle for frozen M1B fixture inputs."""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any


class OracleError(ValueError):
    """The supplied fixture input violates an integrity or cross-record precondition."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_value(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def verify_seal(value: dict[str, Any], field: str) -> None:
    expected = digest_value({key: item for key, item in value.items() if key != field})
    if value.get(field) != expected:
        raise OracleError(f"invalid {field}")


def keyed(values: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    result = {value[field]: value for value in values}
    if len(result) != len(values):
        raise OracleError(f"duplicate {field}")
    return result


def route_evaluation(route_id: str, reasons: set[str]) -> dict[str, Any]:
    return {
        "type": "RouteCandidateEvaluation@1", "route_id": route_id,
        "eligible": not reasons, "reasons": sorted(reasons),
    }


def resolve_route(value: dict[str, Any]) -> dict[str, Any]:
    catalog = value["catalog"]
    routes = keyed(value["descriptors"], "id")
    if any(route_id not in routes for route_id in value["ranked_route_ids"]):
        raise OracleError("ranked route is not described")
    for route in routes.values():
        verify_seal(route, "descriptor_digest")

    engines = keyed(catalog["engines"], "id")
    providers = keyed(catalog["providers"], "id")
    models = keyed(catalog["models"], "id")
    pools = keyed(catalog["pools"], "id")
    hosts = keyed(catalog["hosts"], "id")
    sandboxes = keyed(catalog["sandboxes"], "id")
    requirement = value["requirement"]
    policy = value["policy"]
    evaluations: list[dict[str, Any]] = []
    selected: str | None = None

    for route_id in value["ranked_route_ids"]:
        route = routes[route_id]
        reasons: set[str] = set()
        engine = engines.get(route["engine_id"])
        provider = providers.get(route["provider_id"])
        model = models.get(route["model_id"])
        pool = pools.get(route["pool_id"])
        host = hosts.get(route["host_id"])
        sandbox = sandboxes.get(route["sandbox_id"])
        component_ok = all(item is not None for item in [engine, provider, model, pool, host, sandbox])
        if component_ok:
            component_ok = (
                model["provider_id"] == route["provider_id"]
                and route["model_id"] in pool["model_ids"]
                and route["account_ref"] == pool["account_ref"]
                and set(route["egress_destinations"]).issubset(set(provider["endpoint_ids"]))
                and set(route["egress_destinations"]).issubset(set(sandbox["allowed_destinations"]))
            )
        if not component_ok:
            reasons.add("component-mismatch")

        eligibility = route["eligibility_state"]
        if eligibility == "stale":
            reasons.add("descriptor-stale")
        elif eligibility == "unavailable":
            reasons.add("route-unavailable")
        elif eligibility != "verified-current":
            reasons.add("descriptor-not-current")
        if route["billing_control"] != "verified":
            reasons.add("billing-unknown")

        if pool is not None:
            pool_state = pool["state"]
            if pool_state == "exhausted":
                reasons.add("pool-exhausted")
            elif pool_state == "disabled":
                reasons.add("pool-disabled")
            elif pool_state == "unknown":
                reasons.add("pool-unknown")
            if pool["billing_basis"] not in requirement["allowed_billing"]:
                reasons.add("billing-basis-denied")
            if pool["billing_basis"] == "metered":
                if not policy["metered_authorized"]:
                    reasons.add("metered-not-authorized")
                else:
                    estimate = requirement["estimated_metered_microunits"]
                    limits = [item for item in [pool["metered_limit_microunits"], requirement["max_metered_microunits"], policy["max_metered_microunits"]] if item is not None]
                    if estimate is None:
                        reasons.add("billing-unknown")
                    elif not limits or estimate > min(limits):
                        reasons.add("metered-budget-exceeded")

        if requirement["allowed_route_ids"] and route_id not in requirement["allowed_route_ids"]:
            reasons.add("route-denied")
        if policy["permitted_route_ids"] and route_id not in policy["permitted_route_ids"]:
            reasons.add("route-denied")
        if requirement["allowed_host_ids"] and route["host_id"] not in requirement["allowed_host_ids"]:
            reasons.add("host-denied")
        if policy["permitted_host_ids"] and route["host_id"] not in policy["permitted_host_ids"]:
            reasons.add("host-denied")
        if route["account_ref"] is not None and policy["permitted_account_refs"] and route["account_ref"] not in policy["permitted_account_refs"]:
            reasons.add("account-mismatch")
        if any(destination not in requirement["allowed_egress_destinations"] for destination in route["egress_destinations"]):
            reasons.add("egress-denied")
        if any(destination not in policy["permitted_egress_destinations"] for destination in route["egress_destinations"]):
            reasons.add("egress-denied")
        if requirement["privacy_class"] not in route["privacy_classes"]:
            reasons.add("privacy-mismatch")
        if provider is not None and requirement["privacy_class"] not in provider["privacy_classes"]:
            reasons.add("privacy-mismatch")

        capability_map = {item["name"]: item["state"] for item in route["capabilities"]}
        for capability in requirement["required_capabilities"]:
            state = capability_map.get(capability, "unsupported")
            if state == "unknown":
                reasons.add("capability-unknown")
            elif state != "supported":
                reasons.add("capability-unsupported")
        if sandbox is not None and any(capability not in sandbox["capabilities"] for capability in requirement["required_sandbox_capabilities"]):
            reasons.add("sandbox-capability-missing")

        evaluation = route_evaluation(route_id, reasons)
        evaluations.append(evaluation)
        if selected is None and not reasons:
            selected = route_id

    return {
        "type": "RouteResolutionDecision@1", "status": "selected" if selected else "blocked",
        "selected_route_id": selected, "candidate_evaluations": evaluations,
    }


SENSITIVE_LISTS = ["network_destinations", "credential_refs", "model_refs", "route_account_refs"]
SENSITIVE_SCALARS = ["quota_units", "spend_microunits", "update", "downgrade", "grant_admin"]


def subset_dimensions(requested: dict[str, Any], granted: dict[str, Any], policy: dict[str, Any]) -> set[str]:
    reasons: set[str] = set()
    if not set(requested["functional_capabilities"]).issubset(set(granted["functional_capabilities"])):
        reasons.add("capability-denied")
    if not set(requested["functional_capabilities"]).issubset(set(policy["allowed_capabilities"])):
        reasons.add("capability-denied")
    if not set(requested["workspace_paths"]).issubset(set(granted["workspace_paths"])):
        reasons.add("capability-denied")
    if not set(requested["workspace_paths"]).issubset(set(policy["allowed_workspace_paths"])):
        reasons.add("capability-denied")
    policy_fields = {
        "network_destinations": "allowed_network_destinations", "credential_refs": "allowed_credential_refs",
        "model_refs": "allowed_model_refs", "route_account_refs": "allowed_route_account_refs",
    }
    for field in SENSITIVE_LISTS:
        if not set(requested[field]).issubset(set(granted[field])) or not set(requested[field]).issubset(set(policy[policy_fields[field]])):
            reasons.add("sensitive-grant-missing")
    for field in ["quota_units", "spend_microunits"]:
        amount = requested[field]
        if amount is None:
            continue
        maximum = policy["max_quota_units" if field == "quota_units" else "max_spend_microunits"]
        if granted[field] is None or granted[field] < amount:
            reasons.add("sensitive-grant-missing")
        if maximum is None or amount > maximum:
            reasons.add("policy-limit-exceeded")
    for field, allowed_field in [("update", "update_allowed"), ("downgrade", "downgrade_allowed"), ("grant_admin", "grant_admin_allowed")]:
        if requested[field] and (not granted[field] or not policy[allowed_field]):
            reasons.add("sensitive-grant-missing")
    return reasons


def cycle_members(graph: dict[str, set[str]]) -> set[str]:
    members: set[str] = set()
    visiting: list[str] = []
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            members.update(visiting[visiting.index(node):])
            return
        if node in visited:
            return
        visiting.append(node)
        for dependency in sorted(graph.get(node, set())):
            if dependency in graph:
                visit(dependency)
        visiting.pop()
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return members


def topo_order(graph: dict[str, set[str]]) -> list[str]:
    remaining = {node: set(deps) for node, deps in graph.items()}
    result: list[str] = []
    while remaining:
        ready = sorted(node for node, deps in remaining.items() if not deps)
        if not ready:
            raise OracleError("cycle in accepted graph")
        for node in ready:
            result.append(node)
            remaining.pop(node)
            for deps in remaining.values():
                deps.discard(node)
    return result


def plugin_rejection(plugin_id: str, reasons: set[str]) -> dict[str, Any]:
    return {"type": "PluginRejection@1", "plugin_id": plugin_id, "reasons": sorted(reasons)}


def resolve_plugins(value: dict[str, Any]) -> dict[str, Any]:
    manifests = keyed(value["manifests"], "plugin_id")
    grants = keyed(value["grants"], "plugin_id")
    lifecycles = keyed(value["lifecycles"], "plugin_id")
    policy = value["policy"]
    reasons: dict[str, set[str]] = {plugin_id: set() for plugin_id in manifests}
    graph: dict[str, set[str]] = {plugin_id: set() for plugin_id in manifests}

    for manifest in manifests.values():
        verify_seal(manifest, "manifest_digest")
    for grant in grants.values():
        verify_seal(grant, "grant_digest")

    for plugin_id, manifest in manifests.items():
        if plugin_id not in value["enabled_plugin_ids"]:
            reasons[plugin_id].add("plugin-not-enabled")
        if manifest["protocol_version"] != "m1b-plugin/1":
            reasons[plugin_id].add("unknown-protocol")
        if manifest["trust_tier"] not in policy["allowed_trust_tiers"]:
            reasons[plugin_id].add("trust-tier-denied")
        if manifest["isolation_mode"] not in policy["allowed_isolation_modes"]:
            reasons[plugin_id].add("isolation-denied")
        if any(capability not in policy["allowed_capabilities"] for capability in manifest["provided_capabilities"]):
            reasons[plugin_id].add("capability-denied")
        grant = grants.get(plugin_id)
        if grant is None:
            reasons[plugin_id].add("sensitive-grant-missing")
        else:
            if grant["artifact_digest"] != manifest["artifact_digest"] or grant["dependency_lock_digest"] != manifest["dependency_lock_digest"]:
                reasons[plugin_id].add("grant-digest-mismatch")
            if grant["revoked"]:
                reasons[plugin_id].add("grant-revoked")
            reasons[plugin_id].update(subset_dimensions(manifest["requested_grants"], grant["dimensions"], policy))
        lifecycle = lifecycles.get(plugin_id)
        if lifecycle is not None and grant is not None and lifecycle["epoch"] != grant["grant_epoch"]:
            reasons[plugin_id].add("stale-plugin-epoch")
        for dependency in manifest["dependencies"]:
            dependency_id = dependency["plugin_id"]
            graph[plugin_id].add(dependency_id)
            target = manifests.get(dependency_id)
            if target is None:
                reasons[plugin_id].add("dependency-missing")
            elif dependency["artifact_digest"] != target["artifact_digest"] or dependency["dependency_lock_digest"] != target["dependency_lock_digest"]:
                reasons[plugin_id].add("dependency-digest-mismatch")
        for conflict in manifest["conflicts_with_plugin_ids"]:
            if conflict in manifests:
                reasons[plugin_id].add("conflict-declared")
                reasons[conflict].add("conflict-declared")

    for plugin_id in cycle_members(graph):
        reasons[plugin_id].add("dependency-cycle")
    resource_owners: dict[str, list[str]] = {}
    for plugin_id, manifest in manifests.items():
        for resource in manifest["exclusive_resources"]:
            resource_owners.setdefault(resource, []).append(plugin_id)
    for owners in resource_owners.values():
        if len(owners) > 1:
            for plugin_id in owners:
                reasons[plugin_id].add("exclusive-resource-conflict")

    rejected = [plugin_rejection(plugin_id, problem) for plugin_id, problem in sorted(reasons.items()) if problem]
    if rejected:
        return {"type": "PluginResolutionDecision@1", "status": "blocked", "activation_order": [], "effective_grants": [], "rejections": rejected}
    order = topo_order(graph)
    effective = [
        {"type": "EffectivePluginGrant@1", "plugin_id": plugin_id,
         "artifact_digest": manifests[plugin_id]["artifact_digest"],
         "dimensions": manifests[plugin_id]["requested_grants"]}
        for plugin_id in sorted(manifests)
    ]
    return {"type": "PluginResolutionDecision@1", "status": "resolved", "activation_order": order, "effective_grants": effective, "rejections": []}


def evaluate_disabled(value: dict[str, Any]) -> dict[str, Any]:
    verify_seal(value["manifest"], "manifest_digest")
    trace = {"type": "DisabledActivityTrace@1", "manifest_reads": 1 if value["installed"] else 0}
    for field in ["implementation_imports", "payload_scans", "processes", "threads", "timers", "watchers", "network_calls", "credential_reads", "quota_reservations", "spend_actions", "cache_writes", "context_injections", "tool_registrations", "callbacks", "event_subscriptions"]:
        trace[field] = 0
    return {"type": "DisabledPluginDecision@1", "status": "resolved-disabled", "trace": trace}


def evaluate_reload(value: dict[str, Any]) -> dict[str, Any]:
    old = value["old_lifecycle"]
    new = value["new_manifest"]
    grant = value["grant"]
    verify_seal(new, "manifest_digest")
    verify_seal(grant, "grant_digest")
    if new["plugin_id"] != old["plugin_id"] or new["artifact_digest"] == old["artifact_digest"]:
        return {"type": "PluginReloadDecision@1", "status": "blocked", "events": [], "new_epoch": old["epoch"], "old_binding_reasons": []}
    new_epoch = old["epoch"] + 1
    if grant["plugin_id"] != new["plugin_id"] or grant["artifact_digest"] != new["artifact_digest"] or grant["grant_epoch"] != new_epoch:
        return {"type": "PluginReloadDecision@1", "status": "blocked", "events": [], "new_epoch": old["epoch"], "old_binding_reasons": []}
    stale = any(epoch < new_epoch for epoch in value["old_binding_epochs"].values() if isinstance(epoch, int))
    return {
        "type": "PluginReloadDecision@1", "status": "resolved-reload",
        "events": ["verified", "staged", "drain-and-fence", "replaced", "active"],
        "new_epoch": new_epoch, "old_binding_reasons": ["stale-plugin-epoch"] if stale else [],
    }


def evaluate_process(value: dict[str, Any]) -> dict[str, Any]:
    requirement = value["requirement"]
    descriptor = value["descriptor"]
    verify_seal(descriptor, "descriptor_digest")
    reasons: set[str] = set()
    if descriptor["eligibility_state"] != "verified-current":
        reasons.add("descriptor-not-current")
    if descriptor["host_id"] != requirement["host_id"]:
        reasons.add("host-mismatch")
    if descriptor["platform"] != requirement["platform"]:
        reasons.add("platform-mismatch")
    groups = [
        ("transport", requirement["required_transports"], descriptor["transport_capabilities"]),
        ("containment", requirement["required_containment"], descriptor["containment_capabilities"]),
        ("cancellation", requirement["required_cancellation"], descriptor["cancellation_capabilities"]),
    ]
    for prefix, required, states in groups:
        observed = {item["name"]: item["state"] for item in states}
        for capability in required:
            state = observed.get(capability, "unsupported")
            if state == "unknown":
                reasons.add(f"{prefix}-unknown")
            elif state != "supported":
                reasons.add(f"{prefix}-unsupported")
    return {"type": "ProcessAdmissionDecision@1", "status": "blocked" if reasons else "admitted", "reasons": sorted(reasons)}


def replay_broker(value: dict[str, Any]) -> dict[str, Any]:
    daemon_epoch = value["initial_daemon_epoch"]
    process_epoch = value["initial_process_epoch"]
    current_cursor = 0
    current_unit = "event"
    reasons: set[str] = set()
    credit_bytes: int | None = None
    credit_events: int | None = None
    reset_seen = False
    exhaustion = False

    if any(value[field] for field in ["launch_count", "model_turn_count", "actor_create_count", "effect_count"]):
        reasons.add("attach-created-work")
    for message in value["messages"]:
        if message["daemon_epoch"] != daemon_epoch:
            reasons.add("stale-daemon-epoch")
            continue
        kind = message["type"]
        if kind == "CREDIT":
            credit_bytes = message["bytes"]
            credit_events = message["events"]
            continue
        if kind in {"INPUT", "RESIZE"}:
            if message["process_epoch"] != process_epoch:
                reasons.add("stale-process-epoch")
            lease_field = "input_lease" if kind == "INPUT" else "resize_lease"
            current_field = "current_input_lease" if kind == "INPUT" else "current_resize_lease"
            if value[current_field] is None:
                reasons.add("passive-client-input")
            elif message[lease_field] != value[current_field]:
                reasons.add("stale-lease")
            continue
        if kind == "RESET":
            reset_seen = True
            current_cursor = message["snapshot_cursor"]
            current_unit = message["cursor_unit"]
            continue
        if kind not in {"EVENT", "SNAPSHOT", "ACK", "HELLO", "WELCOME"}:
            continue
        if kind in {"HELLO", "WELCOME"}:
            unit = message["cursor_unit"]
            cursor = message["last_cursor"] if kind == "HELLO" else message["snapshot_cursor"]
            if current_cursor and unit != current_unit:
                reasons.add("cursor-unit-mismatch")
            current_unit = unit
            current_cursor = max(current_cursor, cursor)
            continue
        unit = message["cursor_unit"]
        cursor = message["cursor"]
        if current_cursor and unit != current_unit:
            reasons.add("cursor-unit-mismatch")
        expected = current_cursor
        payload_length = 0
        if kind == "EVENT":
            try:
                payload_length = len(base64.b64decode(message["payload_base64"], validate=True))
            except ValueError as exc:
                raise OracleError("invalid base64 payload") from exc
            expected += payload_length if unit == "utf8-byte" else 1
            if unit == "utf8-byte" and cursor != expected:
                reasons.add("utf8-byte-cursor-mismatch")
            elif unit == "event" and cursor != expected:
                reasons.add("cursor-nonmonotonic")
            if credit_bytes is not None and payload_length > credit_bytes:
                exhaustion = True
                reasons.add("credit-exhausted")
            if credit_events is not None and credit_events < 1:
                exhaustion = True
                reasons.add("credit-exhausted")
            if payload_length > value["queue_limit_bytes"] or value["queue_limit_events"] < 1:
                exhaustion = True
                reasons.add("credit-exhausted")
        elif cursor < current_cursor:
            reasons.add("cursor-nonmonotonic")
        current_cursor = max(current_cursor, cursor)
        current_unit = unit

    refusal_reasons = reasons - {"credit-exhausted"}
    if refusal_reasons or (exhaustion and not reset_seen):
        status = "refused"
    elif exhaustion and reset_seen:
        status = "accepted-reset"
    else:
        status = "accepted"
    return {
        "type": "BrokerTraceDecision@1", "status": status, "reasons": sorted(reasons),
        "final_cursor": current_cursor, "cursor_unit": current_unit,
        "launch_count": value["launch_count"], "model_turn_count": value["model_turn_count"],
        "actor_create_count": value["actor_create_count"], "effect_count": value["effect_count"],
        "requires_reset": exhaustion,
    }


def decide(bundle: dict[str, Any]) -> dict[str, Any]:
    tag = bundle["type"]
    if tag == "RouteFixtureBundle@1":
        return resolve_route(bundle["input"])
    if tag == "PluginFixtureBundle@1":
        return resolve_plugins(bundle["input"])
    if tag == "DisabledPluginFixtureBundle@1":
        return evaluate_disabled(bundle["input"])
    if tag == "PluginReloadFixtureBundle@1":
        return evaluate_reload(bundle["input"])
    if tag == "ProcessFixtureBundle@1":
        return evaluate_process(bundle["input"])
    if tag == "BrokerFixtureBundle@1":
        return replay_broker(bundle["input"])
    raise OracleError(f"unknown fixture arm: {tag!r}")
