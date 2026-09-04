#!/usr/bin/env python3
"""Strict schema and decoder gates for the inert M1B contracts."""

from __future__ import annotations

import copy
import base64
import importlib.util
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import validators


ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / "schemas" / "control-plane" / "v3" / "execution" / "schema.json"
MATERIALIZER_PATH = SCHEMA_PATH.with_name("materialize.py")
MAX_BYTES = 262_144
MAX_DEPTH = 64
DIGEST = "sha256:" + "1" * 64
DIGEST_2 = "sha256:" + "2" * 64


class StrictJSONError(ValueError):
    pass


def _reject_constant(value: str) -> None:
    raise StrictJSONError(f"non-I-JSON constant: {value}")


def _reject_float(value: str) -> None:
    raise StrictJSONError(f"float not permitted: {value}")


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
        text,
        object_pairs_hook=_object_pairs,
        parse_float=_reject_float,
        parse_constant=_reject_constant,
    )
    if _depth(value) > MAX_DEPTH:
        raise StrictJSONError("object exceeds depth ceiling")
    return value


def canonical_key(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _utf8_max(validator: Any, limit: int, instance: Any, schema: dict[str, Any]):
    del schema
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


def _base64_bound(validator: Any, limit: int, instance: Any, schema: dict[str, Any]):
    del validator, schema
    if not isinstance(instance, str):
        return
    try:
        decoded = base64.b64decode(instance, validate=True)
    except ValueError:
        yield jsonschema.ValidationError("invalid base64")
        return
    if base64.b64encode(decoded).decode("ascii") != instance:
        yield jsonschema.ValidationError("non-canonical base64")
    if len(decoded) > limit:
        yield jsonschema.ValidationError(f"decoded base64 exceeds {limit} bytes")


M1BValidator = validators.extend(
    jsonschema.Draft202012Validator,
    {"x-utf8MaxBytes": _utf8_max, "x-strictlySorted": _strictly_sorted,
     "x-strictlySortedBy": _strictly_sorted_by, "x-uniqueBy": _unique_by,
     "x-rfc3339Utc": _utc_timestamp, "x-base64MaxDecodedBytes": _base64_bound},
)


def load_schema() -> dict[str, Any]:
    return strict_loads(SCHEMA_PATH.read_bytes())


def validate(value: Any, definition: str | None = None) -> None:
    schema = load_schema()
    target = schema if definition is None else {"$ref": f"#/$defs/{definition}", "$defs": schema["$defs"]}
    M1BValidator(target).validate(value)


def evidence() -> dict[str, Any]:
    return {
        "type": "EvidenceBinding@1", "source_ids": ["src-v3-001"],
        "observed_at": "2026-09-04T00:00:00Z", "expires_at": None,
        "evidence_digest": DIGEST,
    }


def capability_state(name: str, state: str = "supported", kind: str = "CapabilityState@1") -> dict[str, Any]:
    return {"type": kind, "name": name, "state": state}


def catalog() -> dict[str, Any]:
    return {
        "type": "RouteComponentCatalog@1",
        "engines": [{"type": "EngineDescriptor@1", "id": "engine-a", "protocol_versions": ["v1"], "capabilities": ["chat"]}],
        "providers": [{"type": "ProviderDescriptor@1", "id": "provider-a", "endpoint_ids": ["endpoint:a"], "privacy_classes": ["private"]}],
        "models": [{"type": "ModelDescriptor@1", "id": "model-a", "provider_id": "provider-a", "capabilities": ["chat"], "reasoning_modes": []}],
        "pools": [{"type": "CapacityPoolDescriptor@1", "id": "pool-a", "billing_basis": "subscription", "account_ref": "account:a", "model_ids": ["model-a"], "state": "available", "remaining_units": 1, "metered_limit_microunits": None}],
        "hosts": [{"type": "HostDescriptor@1", "id": "host-a", "platform": "windows", "capabilities": ["local"]}],
        "sandboxes": [{"type": "SandboxDescriptor@1", "id": "sandbox-a", "filesystem_mode": "read-only", "network_mode": "allowlist", "process_mode": "isolated", "allowed_paths": ["workspace:/repo"], "allowed_destinations": ["endpoint:a"], "capabilities": ["workspace-read"]}],
    }


def route_descriptor() -> dict[str, Any]:
    return {
        "type": "RouteCapabilityDescriptor@1", "id": "route-a", "engine_id": "engine-a",
        "provider_id": "provider-a", "model_id": "model-a", "pool_id": "pool-a",
        "account_ref": "account:a", "host_id": "host-a", "sandbox_id": "sandbox-a",
        "eligibility_state": "verified-current", "capabilities": [capability_state("chat")],
        "privacy_classes": ["private"], "egress_destinations": ["endpoint:a"],
        "billing_control": "verified", "evidence": evidence(), "descriptor_digest": DIGEST,
    }


def dimensions() -> dict[str, Any]:
    return {
        "type": "PluginGrantDimensions@1", "functional_capabilities": ["render"],
        "workspace_paths": ["workspace:/repo"], "network_destinations": [], "credential_refs": [],
        "model_refs": [], "route_account_refs": [], "quota_units": None, "spend_microunits": None,
        "update": False, "downgrade": False, "grant_admin": False,
    }


def resource_envelope() -> dict[str, Any]:
    return {
        "type": "ResourceEnvelope@1", "max_cpu_millis": 1, "max_memory_bytes": 1,
        "max_disk_bytes": 1, "max_concurrency": 1, "max_queue_events": 1, "max_queue_bytes": 1,
    }


def plugin_manifest() -> dict[str, Any]:
    return {
        "type": "PluginManifest@1", "id": "manifest-view", "plugin_id": "plugin-view", "version": "1.0.0",
        "protocol_version": "m1b-plugin/1", "artifact_digest": DIGEST, "dependency_lock_digest": DIGEST_2,
        "trust_tier": "T3-untrusted-view", "provided_capabilities": ["render"], "required_capabilities": [],
        "dependencies": [], "exclusive_resources": [], "conflicts_with_plugin_ids": [],
        "configuration_schema_digest": DIGEST, "isolation_mode": "sandboxed-view",
        "durable_subscriptions": [], "ephemeral_subscriptions": [], "requested_grants": dimensions(),
        "resource_envelope": resource_envelope(), "lifecycle_hooks": ["activate", "retire", "verify"],
        "health_probe_ids": [], "provenance_digest": DIGEST, "license_id": "MIT",
        "update_source": None, "manifest_digest": DIGEST,
    }


def process_descriptor() -> dict[str, Any]:
    return {
        "type": "ProcessCapabilityDescriptor@1", "id": "process-profile-a", "host_id": "host-a",
        "platform": "windows", "platform_version": "11.1", "eligibility_state": "verified-current",
        "transport_capabilities": [capability_state("conpty", kind="ProcessTransportCapabilityState@1")],
        "containment_capabilities": [capability_state("job-object", kind="ProcessContainmentCapabilityState@1")],
        "cancellation_capabilities": [capability_state("tree-terminate", kind="ProcessCancellationCapabilityState@1")],
        "evidence": evidence(), "descriptor_digest": DIGEST,
    }


class M1BSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = load_schema()

    def test_meta_schema_and_materializer(self) -> None:
        jsonschema.Draft202012Validator.check_schema(self.schema)
        spec = importlib.util.spec_from_file_location("m1b_materializer", MATERIALIZER_PATH)
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
        self.assertGreaterEqual(object_count, 50)

    def test_strict_decoder_rejects_ambiguous_json(self) -> None:
        bad = [b'{"a":1,"a":2}', b'{"a":1.0}', b'{"a":NaN}', b'\xef\xbb\xbf{}', b'"\xff"']
        for raw in bad:
            with self.subTest(raw=raw), self.assertRaises((StrictJSONError, UnicodeDecodeError, json.JSONDecodeError)):
                strict_loads(raw)
        value: Any = 0
        for _ in range(MAX_DEPTH + 1):
            value = [value]
        with self.assertRaises(StrictJSONError):
            strict_loads(json.dumps(value).encode())

    def test_route_records_and_conditions(self) -> None:
        validate(catalog(), "RouteComponentCatalog")
        validate(route_descriptor(), "RouteCapabilityDescriptor")
        bad = catalog()
        bad["pools"][0]["billing_basis"] = "metered"
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "RouteComponentCatalog")
        bad = route_descriptor()
        bad["unknown"] = True
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "RouteCapabilityDescriptor")

    def test_route_input_and_decision(self) -> None:
        value = {
            "type": "RouteResolutionInput@1", "catalog": catalog(), "descriptors": [route_descriptor()],
            "requirement": {"type": "RouteRequirement@1", "id": "req-a", "required_capabilities": ["chat"], "privacy_class": "private", "allowed_billing": ["subscription"], "allowed_route_ids": ["route-a"], "allowed_host_ids": ["host-a"], "allowed_egress_destinations": ["endpoint:a"], "estimated_metered_microunits": None, "max_metered_microunits": None, "required_sandbox_capabilities": ["workspace-read"]},
            "policy": {"type": "RoutePolicyEnvelope@1", "id": "policy-a", "goal_spec_digest": DIGEST, "authority_digest": DIGEST, "policy_digest": DIGEST, "permitted_route_ids": ["route-a"], "permitted_host_ids": ["host-a"], "permitted_account_refs": ["account:a"], "permitted_egress_destinations": ["endpoint:a"], "metered_authorized": False, "max_metered_microunits": None, "pause_epoch": 0},
            "ranked_route_ids": ["route-a"],
        }
        validate(value, "RouteResolutionInput")
        decision = {"type": "RouteResolutionDecision@1", "status": "selected", "selected_route_id": "route-a", "candidate_evaluations": [{"type": "RouteCandidateEvaluation@1", "route_id": "route-a", "eligible": True, "reasons": []}]}
        validate(decision, "RouteResolutionDecision")

    def test_plugin_records(self) -> None:
        validate(plugin_manifest(), "PluginManifest")
        bad = plugin_manifest()
        bad["trust_tier"] = "trusted"
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "PluginManifest")
        bad = plugin_manifest()
        bad["lifecycle_hooks"] = ["verify", "activate"]
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "PluginManifest")

    def test_disabled_trace_is_zero_only(self) -> None:
        trace = {"type": "DisabledActivityTrace@1", "manifest_reads": 1}
        for field in ["implementation_imports", "payload_scans", "processes", "threads", "timers", "watchers", "network_calls", "credential_reads", "quota_reservations", "spend_actions", "cache_writes", "context_injections", "tool_registrations", "callbacks", "event_subscriptions"]:
            trace[field] = 0
        validate(trace, "DisabledActivityTrace")
        trace["network_calls"] = 1
        with self.assertRaises(jsonschema.ValidationError):
            validate(trace, "DisabledActivityTrace")

    def test_process_capability_categories_do_not_mix(self) -> None:
        validate(process_descriptor(), "ProcessCapabilityDescriptor")
        bad = process_descriptor()
        bad["transport_capabilities"][0]["name"] = "job-object"
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "ProcessCapabilityDescriptor")

    def test_current_pause_is_only_operative_value(self) -> None:
        requirement = {
            "type": "ProcessRequirement@1", "id": "proc-a", "actor_id": "actor-a", "task_id": "task-a",
            "work_packet_digest": DIGEST, "route_descriptor_digest": DIGEST, "host_id": "host-a",
            "platform": "windows", "required_transports": ["conpty"], "required_containment": ["job-object"],
            "required_cancellation": ["tree-terminate"], "stdio_encoding": "utf-8", "max_buffer_bytes": 4096,
            "attach_allowed": True, "operative_pause_policy": "current-immediate",
            "representable_future_pause_policies": ["checkpoint", "emergency"],
        }
        validate(requirement, "ProcessRequirement")
        requirement["operative_pause_policy"] = "checkpoint"
        with self.assertRaises(jsonschema.ValidationError):
            validate(requirement, "ProcessRequirement")

    def test_all_broker_message_arms_are_exact(self) -> None:
        messages = [
            {"type": "HELLO", "protocol_version": "m1b-broker/1", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 1, "last_cursor": 0, "cursor_unit": "event", "columns": 80, "rows": 24, "capabilities": []},
            {"type": "WELCOME", "protocol_version": "m1b-broker/1", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 1, "replay_floor": 0, "snapshot_cursor": 0, "cursor_unit": "event", "input_lease": None, "resize_lease": None, "capabilities": []},
            {"type": "SNAPSHOT", "protocol_version": "m1b-broker/1", "stream_id": "stream-a", "daemon_epoch": 1, "cursor": 0, "cursor_unit": "event", "snapshot_digest": DIGEST},
            {"type": "EVENT", "protocol_version": "m1b-broker/1", "stream_id": "stream-a", "daemon_epoch": 1, "cursor": 1, "cursor_unit": "event", "event_class": "status", "process_id": None, "payload_base64": "eA==", "payload_untrusted": True},
            {"type": "ACK", "protocol_version": "m1b-broker/1", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 1, "cursor": 1, "cursor_unit": "event"},
            {"type": "CREDIT", "protocol_version": "m1b-broker/1", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 1, "bytes": 1, "events": 1},
            {"type": "INPUT", "protocol_version": "m1b-broker/1", "command_id": "command-a", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 1, "process_epoch": 1, "input_lease": "lease:a", "bytes_base64": "eA=="},
            {"type": "RESIZE", "protocol_version": "m1b-broker/1", "command_id": "command-b", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 1, "process_epoch": 1, "resize_lease": "lease:b", "columns": 80, "rows": 24},
            {"type": "RESET", "protocol_version": "m1b-broker/1", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 1, "reason": "gap", "snapshot_cursor": 2, "cursor_unit": "event"},
        ]
        for message in messages:
            with self.subTest(message=message["type"]):
                validate(message, "BrokerMessage")
        bad = copy.deepcopy(messages[0])
        bad["protocol_version"] = "m1b-broker/2"
        with self.assertRaises(jsonschema.ValidationError):
            validate(bad, "BrokerMessage")

    def test_scalar_bounds_sort_and_boolean_integer(self) -> None:
        validate(["a", "b"], "IdSet")
        for value in (["b", "a"], ["a", "a"]):
            with self.assertRaises(jsonschema.ValidationError):
                validate(value, "IdSet")
        with self.assertRaises(jsonschema.ValidationError):
            validate(True, "Count")
        with self.assertRaises(jsonschema.ValidationError):
            validate("é" * 49, "Id")

    def test_timestamp_and_base64_are_semantically_strict(self) -> None:
        validate("2026-09-04T00:00:00Z", "Timestamp")
        with self.assertRaises(jsonschema.ValidationError):
            validate("2026-99-99T99:99:99Z", "Timestamp")
        event = {"type": "EVENT", "protocol_version": "m1b-broker/1", "stream_id": "stream-a", "daemon_epoch": 1, "cursor": 1, "cursor_unit": "event", "event_class": "status", "process_id": None, "payload_base64": "eA==", "payload_untrusted": True}
        validate(event, "BrokerMessage")
        event["payload_base64"] = "AB=="
        with self.assertRaises(jsonschema.ValidationError):
            validate(event, "BrokerMessage")


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("M1B_SCHEMA_PASS")
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
