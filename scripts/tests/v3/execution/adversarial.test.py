#!/usr/bin/env python3
"""Adversarial and monotonicity probes for the inert M1B reference contract."""

from __future__ import annotations

import base64
import copy
import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any

import jsonschema


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


schema_support = load_module("m1b_schema_adversarial", HERE / "schema.test.py")
oracle = load_module("m1b_oracle_adversarial", HERE / "reference_oracle.py")


def bundle(number: int) -> dict[str, Any]:
    path = FIXTURES / f"F-M1B-{number:03d}.json"
    return schema_support.strict_loads(path.read_bytes())


class M1BAdversarialTests(unittest.TestCase):
    def assert_schema_rejects(self, value: Any, definition: str = "M1BFixtureBundle") -> None:
        with self.assertRaises(jsonschema.ValidationError):
            schema_support.validate(value, definition)

    def test_closed_shape_version_digest_integer_and_sort_probes(self) -> None:
        cases = []
        value = bundle(1); value["unknown"] = True; cases.append(value)
        value = bundle(1); value["type"] = "RouteFixtureBundle@2"; cases.append(value)
        value = bundle(1); value["input"]["descriptors"][0]["descriptor_digest"] = "sha256:ABC"; cases.append(value)
        value = bundle(1); value["input"]["policy"]["pause_epoch"] = True; cases.append(value)
        value = bundle(1); value["source_requirement_ids"] = ["z", "a"]; cases.append(value)
        for value in cases:
            self.assert_schema_rejects(value)

    def test_strict_decoder_rejects_duplicate_float_constant_and_utf8(self) -> None:
        raws = [b'{"a":1,"a":2}', b'{"a":1.25}', b'{"a":-0}', b'{"a":Infinity}', b'"\xff"']
        for raw in raws:
            with self.subTest(raw=raw), self.assertRaises(Exception):
                schema_support.strict_loads(raw)

    def test_tampered_route_seal_fails_before_resolution(self) -> None:
        value = bundle(1)["input"]
        value["descriptors"][0]["privacy_classes"] = ["public"]
        with self.assertRaises(oracle.OracleError):
            oracle.resolve_route(value)

    def test_expiry_preceding_observation_fails_without_clock_access(self) -> None:
        value = bundle(1)["input"]
        value["descriptors"][0]["evidence"]["expires_at"] = "2026-09-03T23:59:59Z"
        value["descriptors"][0]["descriptor_digest"] = oracle.digest_value({key: item for key, item in value["descriptors"][0].items() if key != "descriptor_digest"})
        with self.assertRaises(oracle.OracleError):
            oracle.resolve_route(value)

    def test_ranked_undescribed_route_fails_instead_of_substitution(self) -> None:
        value = bundle(1)["input"]
        value["ranked_route_ids"] = ["route-missing"]
        with self.assertRaises(oracle.OracleError):
            oracle.resolve_route(value)

    def test_route_restrictions_never_create_eligibility(self) -> None:
        base = bundle(1)["input"]
        mutations = []
        value = copy.deepcopy(base); value["policy"]["permitted_route_ids"] = ["route-b"]; mutations.append((value, "route-denied"))
        value = copy.deepcopy(base); value["policy"]["permitted_host_ids"] = ["host-b"]; mutations.append((value, "host-denied"))
        value = copy.deepcopy(base); value["policy"]["permitted_account_refs"] = ["account:b"]; mutations.append((value, "account-mismatch"))
        value = copy.deepcopy(base); value["policy"]["permitted_egress_destinations"] = ["endpoint:b"]; mutations.append((value, "egress-denied"))
        for value, reason in mutations:
            decision = oracle.resolve_route(value)
            first = decision["candidate_evaluations"][0]
            self.assertFalse(first["eligible"])
            self.assertIn(reason, first["reasons"])

    def test_empty_requirement_allowlists_add_no_restriction(self) -> None:
        value = bundle(1)["input"]
        value["requirement"]["allowed_route_ids"] = []
        value["requirement"]["allowed_host_ids"] = []
        value["requirement"]["allowed_egress_destinations"] = []
        decision = oracle.resolve_route(value)
        self.assertEqual(decision["status"], "selected")
        self.assertEqual(decision["selected_route_id"], "route-a")

    def test_empty_policy_sets_grant_no_route_authority(self) -> None:
        for field, reason in [
            ("permitted_route_ids", "route-denied"),
            ("permitted_host_ids", "host-denied"),
            ("permitted_account_refs", "account-mismatch"),
            ("permitted_egress_destinations", "egress-denied"),
        ]:
            value = bundle(1)["input"]
            value["policy"][field] = []
            first = oracle.resolve_route(value)["candidate_evaluations"][0]
            self.assertFalse(first["eligible"])
            self.assertIn(reason, first["reasons"])

    def test_supported_route_capability_requires_component_backing(self) -> None:
        value = bundle(1)["input"]
        value["catalog"]["engines"][0]["capabilities"] = ["tools"]
        first = oracle.resolve_route(value)["candidate_evaluations"][0]
        self.assertFalse(first["eligible"])
        self.assertIn("component-mismatch", first["reasons"])

    def test_all_noncurrent_descriptor_states_block(self) -> None:
        for descriptor_state in ["documented", "observed-uncertain", "stale", "unavailable"]:
            value = bundle(1)["input"]
            value["descriptors"] = [value["descriptors"][0]]
            value["ranked_route_ids"] = ["route-a"]
            value["descriptors"][0]["eligibility_state"] = descriptor_state
            value["descriptors"][0]["descriptor_digest"] = oracle.digest_value({key: item for key, item in value["descriptors"][0].items() if key != "descriptor_digest"})
            decision = oracle.resolve_route(value)
            self.assertEqual(decision["status"], "blocked")

    def test_metered_estimate_must_be_known_and_inside_every_ceiling(self) -> None:
        for estimate, reason in [(None, "billing-unknown"), (501, "metered-budget-exceeded")]:
            value = bundle(4)["input"]
            value["requirement"]["estimated_metered_microunits"] = estimate
            decision = oracle.resolve_route(value)
            self.assertEqual(decision["status"], "blocked")
            self.assertIn(reason, decision["candidate_evaluations"][0]["reasons"])

    def test_tampered_manifest_and_grant_seals_fail(self) -> None:
        value = bundle(9)["input"]
        value["manifests"][0]["provided_capabilities"] = ["render"]
        with self.assertRaises(oracle.OracleError):
            oracle.resolve_plugins(value)
        value = bundle(9)["input"]
        value["grants"][0]["revoked"] = True
        with self.assertRaises(oracle.OracleError):
            oracle.resolve_plugins(value)

    def test_dependency_cycle_is_complete_not_root_only(self) -> None:
        decision = oracle.resolve_plugins(bundle(11)["input"])
        self.assertEqual({row["plugin_id"] for row in decision["rejections"]}, {"plugin-a", "plugin-b"})
        self.assertTrue(all("dependency-cycle" in row["reasons"] for row in decision["rejections"]))

    def test_trust_tier_does_not_supply_sensitive_grant(self) -> None:
        value = bundle(14)["input"]
        value["manifests"][0]["trust_tier"] = "T1-signed-built-in"
        value["manifests"][0]["manifest_digest"] = oracle.digest_value({key: item for key, item in value["manifests"][0].items() if key != "manifest_digest"})
        decision = oracle.resolve_plugins(value)
        self.assertIn("sensitive-grant-missing", decision["rejections"][0]["reasons"])

    def test_grant_context_must_match_active_policy(self) -> None:
        for field in ["goal_spec_digest", "policy_digest"]:
            value = bundle(9)["input"]
            value["grants"][0][field] = "sha256:" + "9" * 64
            value["grants"][0]["grant_digest"] = oracle.digest_value({key: item for key, item in value["grants"][0].items() if key != "grant_digest"})
            decision = oracle.resolve_plugins(value)
            matching = next(row for row in decision["rejections"] if row["plugin_id"] == value["grants"][0]["plugin_id"])
            self.assertIn("grant-context-mismatch", matching["reasons"])

    def test_required_plugin_capability_must_have_one_dependency_provider(self) -> None:
        value = bundle(9)["input"]
        core = next(item for item in value["manifests"] if item["plugin_id"] == "plugin-core")
        core["provided_capabilities"] = ["render"]
        core["manifest_digest"] = oracle.digest_value({key: item for key, item in core.items() if key != "manifest_digest"})
        decision = oracle.resolve_plugins(value)
        matching = next(row for row in decision["rejections"] if row["plugin_id"] == "plugin-view")
        self.assertIn("required-capability-missing", matching["reasons"])

    def test_manifest_lifecycle_binding_is_required(self) -> None:
        value = bundle(9)["input"]
        value["lifecycles"][0]["artifact_digest"] = "sha256:" + "9" * 64
        decision = oracle.resolve_plugins(value)
        matching = next(row for row in decision["rejections"] if row["plugin_id"] == value["lifecycles"][0]["plugin_id"])
        self.assertIn("lifecycle-digest-mismatch", matching["reasons"])
        value = bundle(9)["input"]
        removed = value["lifecycles"].pop(0)
        decision = oracle.resolve_plugins(value)
        matching = next(row for row in decision["rejections"] if row["plugin_id"] == removed["plugin_id"])
        self.assertIn("lifecycle-missing", matching["reasons"])

    def test_enabled_plugin_without_manifest_blocks(self) -> None:
        value = bundle(9)["input"]
        value["enabled_plugin_ids"].append("plugin-z")
        decision = oracle.resolve_plugins(value)
        matching = next(row for row in decision["rejections"] if row["plugin_id"] == "plugin-z")
        self.assertIn("manifest-missing", matching["reasons"])

    def test_each_sensitive_grant_dimension_is_independent(self) -> None:
        fields = ["network_destinations", "credential_refs", "model_refs", "route_account_refs", "quota_units", "spend_microunits", "update", "downgrade", "grant_admin"]
        for field in fields:
            value = bundle(9)["input"]
            manifest = value["manifests"][0]
            grant = next(item for item in value["grants"] if item["plugin_id"] == manifest["plugin_id"])
            policy = value["policy"]
            if field in ["network_destinations", "credential_refs", "model_refs", "route_account_refs"]:
                requested_value = {"network_destinations": ["endpoint:a"], "credential_refs": ["credential:a"], "model_refs": ["model:a"], "route_account_refs": ["route-account:a"]}[field]
                manifest["requested_grants"][field] = requested_value
                grant["dimensions"][field] = []
            elif field in ["quota_units", "spend_microunits"]:
                manifest["requested_grants"][field] = 1
                grant["dimensions"][field] = None
            else:
                manifest["requested_grants"][field] = True
                grant["dimensions"][field] = False
                policy[{"update": "update_allowed", "downgrade": "downgrade_allowed", "grant_admin": "grant_admin_allowed"}[field]] = True
            manifest["manifest_digest"] = oracle.digest_value({key: item for key, item in manifest.items() if key != "manifest_digest"})
            grant["artifact_digest"] = manifest["artifact_digest"]
            grant["grant_digest"] = oracle.digest_value({key: item for key, item in grant.items() if key != "grant_digest"})
            decision = oracle.resolve_plugins(value)
            matching = next(row for row in decision["rejections"] if row["plugin_id"] == manifest["plugin_id"])
            self.assertIn("sensitive-grant-missing", matching["reasons"], field)

    def test_disabled_activity_cannot_be_nonzero(self) -> None:
        expected = bundle(15)["expected"]
        for field in ["implementation_imports", "processes", "threads", "network_calls", "credential_reads", "quota_reservations", "spend_actions", "context_injections", "tool_registrations", "event_subscriptions"]:
            value = copy.deepcopy(expected)
            value["trace"][field] = 1
            self.assert_schema_rejects(value, "DisabledPluginDecision")

    def test_reload_without_new_digest_or_epoch_blocks(self) -> None:
        value = bundle(16)["input"]
        value["new_manifest"]["artifact_digest"] = value["old_lifecycle"]["artifact_digest"]
        value["new_manifest"]["manifest_digest"] = oracle.digest_value({key: item for key, item in value["new_manifest"].items() if key != "manifest_digest"})
        value["grant"]["artifact_digest"] = value["new_manifest"]["artifact_digest"]
        value["grant"]["grant_digest"] = oracle.digest_value({key: item for key, item in value["grant"].items() if key != "grant_digest"})
        self.assertEqual(oracle.evaluate_reload(value)["status"], "blocked")

    def test_reload_grant_context_must_match_policy(self) -> None:
        value = bundle(16)["input"]
        value["grant"]["policy_digest"] = "sha256:" + "9" * 64
        value["grant"]["grant_digest"] = oracle.digest_value({key: item for key, item in value["grant"].items() if key != "grant_digest"})
        decision = oracle.evaluate_reload(value)
        self.assertEqual(decision["status"], "blocked")
        self.assertIn("grant-context-mismatch", decision["old_binding_reasons"])
        value = bundle(16)["input"]
        value["grant"]["grant_epoch"] = 1
        value["grant"]["grant_digest"] = oracle.digest_value({key: item for key, item in value["grant"].items() if key != "grant_digest"})
        self.assertEqual(oracle.evaluate_reload(value)["status"], "blocked")

    def test_process_unknown_and_unsupported_are_distinct_failures(self) -> None:
        for number, reason in [(18, "containment-unknown"), (19, "containment-unsupported")]:
            decision = oracle.evaluate_process(bundle(number)["input"])
            self.assertEqual(decision["status"], "blocked")
            self.assertEqual(decision["reasons"], [reason])

    def test_process_platform_and_host_labels_are_not_capabilities(self) -> None:
        value = bundle(17)["input"]
        value["requirement"]["host_id"] = "host-other"
        decision = oracle.evaluate_process(value)
        self.assertEqual(decision["status"], "blocked")
        self.assertIn("host-mismatch", decision["reasons"])

    def test_termination_cannot_claim_effect_outcome(self) -> None:
        observation = bundle(24)["termination_observation"]
        observation["effect_conclusion"] = "success"
        self.assert_schema_rejects(observation, "ProcessTerminationObservation")

    def test_future_pause_policy_cannot_become_operative(self) -> None:
        requirement = bundle(24)["input"]["requirement"]
        requirement["operative_pause_policy"] = "checkpoint"
        self.assert_schema_rejects(requirement, "ProcessRequirement")

    def test_stale_daemon_process_and_input_leases_refuse(self) -> None:
        base = bundle(21)["input"]
        mutations = []
        value = copy.deepcopy(base); value["messages"][0]["daemon_epoch"] = 1; mutations.append((value, "stale-daemon-epoch"))
        value = copy.deepcopy(base); value["messages"][0]["process_epoch"] = 1; mutations.append((value, "stale-process-epoch"))
        value = copy.deepcopy(base); value["current_input_lease"] = None; mutations.append((value, "passive-client-input"))
        for value, reason in mutations:
            decision = oracle.replay_broker(value)
            self.assertEqual(decision["status"], "refused")
            self.assertIn(reason, decision["reasons"])

    def test_mixed_units_and_nonmonotonic_cursors_refuse(self) -> None:
        first = {"type": "EVENT", "protocol_version": "m1b-broker/1", "stream_id": "stream-a", "daemon_epoch": 2, "cursor": 1, "cursor_unit": "event", "event_class": "output", "process_id": "process-a", "payload_base64": base64.b64encode(b"a").decode(), "payload_untrusted": True}
        second = copy.deepcopy(first)
        second["cursor_unit"] = "utf8-byte"
        second["cursor"] = 2
        value = bundle(20)["input"]
        value["messages"] = [first, second]
        self.assertIn("cursor-unit-mismatch", oracle.replay_broker(value)["reasons"])
        value["messages"] = [first, copy.deepcopy(first)]
        self.assertIn("cursor-nonmonotonic", oracle.replay_broker(value)["reasons"])

    def test_utf8_cursor_uses_encoded_bytes(self) -> None:
        value = bundle(23)["input"]
        event = next(item for item in value["messages"] if item["type"] == "EVENT")
        event["cursor"] = 1
        decision = oracle.replay_broker(value)
        self.assertIn("utf8-byte-cursor-mismatch", decision["reasons"])
        self.assertEqual(decision["status"], "refused")

    def test_output_that_spells_command_remains_untrusted_data(self) -> None:
        value = bundle(23)["input"]
        raw = b"INPUT command-a"
        credit = next(item for item in value["messages"] if item["type"] == "CREDIT")
        event = next(item for item in value["messages"] if item["type"] == "EVENT")
        credit["bytes"] = len(raw)
        event["payload_base64"] = base64.b64encode(raw).decode()
        event["cursor"] = len(raw)
        decision = oracle.replay_broker(value)
        self.assertEqual(decision["status"], "accepted")
        self.assertEqual([decision[field] for field in ["launch_count", "model_turn_count", "actor_create_count", "effect_count"]], [0, 0, 0, 0])

    def test_attach_cannot_arrive_with_created_work(self) -> None:
        value = bundle(20)["input"]
        value["launch_count"] = 1
        decision = oracle.replay_broker(value)
        self.assertEqual(decision["status"], "refused")
        self.assertIn("attach-created-work", decision["reasons"])

    def test_credit_is_required_and_consumed_cumulatively(self) -> None:
        event = {"type": "EVENT", "protocol_version": "m1b-broker/1", "stream_id": "stream-a", "daemon_epoch": 2, "cursor": 1, "cursor_unit": "event", "event_class": "output", "process_id": "process-a", "payload_base64": base64.b64encode(b"a").decode(), "payload_untrusted": True}
        value = bundle(20)["input"]
        value["messages"] = [copy.deepcopy(event)]
        decision = oracle.replay_broker(value)
        self.assertEqual(decision["status"], "refused")
        self.assertIn("credit-missing", decision["reasons"])

        credit = {"type": "CREDIT", "protocol_version": "m1b-broker/1", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 2, "bytes": 1, "events": 1}
        second = copy.deepcopy(event); second["cursor"] = 2
        value["messages"] = [credit, event, second]
        decision = oracle.replay_broker(value)
        self.assertEqual(decision["status"], "refused")
        self.assertIn("credit-exhausted", decision["reasons"])

        value = bundle(20)["input"]
        value["queue_limit_events"] = 1
        credit = copy.deepcopy(credit); credit["bytes"] = 2; credit["events"] = 2
        value["messages"] = [credit, event, second]
        self.assertIn("credit-exhausted", oracle.replay_broker(value)["reasons"])

        ack = {"type": "ACK", "protocol_version": "m1b-broker/1", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 2, "cursor": 1, "cursor_unit": "event"}
        value["messages"] = [credit, event, ack, second]
        self.assertEqual(oracle.replay_broker(value)["status"], "accepted")

    def test_ack_command_stream_and_welcome_bindings_fail_closed(self) -> None:
        value = bundle(20)["input"]
        value["messages"] = [{"type": "ACK", "protocol_version": "m1b-broker/1", "client_id": "client-a", "stream_id": "stream-a", "daemon_epoch": 2, "cursor": 1, "cursor_unit": "event"}]
        self.assertIn("ack-ahead", oracle.replay_broker(value)["reasons"])

        command = copy.deepcopy(bundle(21)["input"]["messages"][0])
        conflicting = copy.deepcopy(command); conflicting["bytes_base64"] = base64.b64encode(b"y").decode()
        value["messages"] = [command, conflicting]
        self.assertIn("duplicate-command-conflict", oracle.replay_broker(value)["reasons"])

        value = bundle(20)["input"]
        value["messages"][1]["stream_id"] = "stream-b"
        self.assertIn("stream-mismatch", oracle.replay_broker(value)["reasons"])

        value = bundle(20)["input"]
        value["messages"][1]["input_lease"] = "lease:unexpected"
        self.assertIn("welcome-lease-mismatch", oracle.replay_broker(value)["reasons"])


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False)
    if result.result.wasSuccessful():
        print("M1B_ADVERSARIAL_PASS probes=33 grant_dimensions=9")
    raise SystemExit(0 if result.result.wasSuccessful() else 1)
