#!/usr/bin/env python3
"""Hermetic Phase 1 controls for v2 contracts and dry resolution."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from v2_contracts import ContractError, digest, load_config, load_registry, read_v1_manifest, read_v1_portfolio_row, read_v1_task_header, resolve_assignment, validate_record, validate_registry  # noqa: E402


def base_records() -> dict[str, list[dict]]:
    return load_config(ROOT / "config" / "v2")


class V2ContractsTest(unittest.TestCase):
    def test_shipped_registries_validate(self):
        cfg = base_records()
        for kind in ("engine", "provider", "capacity_pool", "model", "host", "sandbox_profile", "routing_policy", "project"):
            self.assertTrue(cfg[kind], kind)

    def test_unknown_fields_and_secret_material_fail_closed(self):
        record = copy.deepcopy(base_records()["engine"][0])
        record["future_field"] = True
        with self.assertRaisesRegex(ContractError, "unknown fields"):
            validate_record(record)
        record = copy.deepcopy(base_records()["capacity_pool"][0])
        record["api_key"] = "not-a-ref"
        with self.assertRaisesRegex(ContractError, "secret material"):
            validate_record(record)
        record = copy.deepcopy(base_records()["capacity_pool"][0])
        record["credential_ref"] = "plaintext-token-value"
        with self.assertRaises(ContractError):
            validate_record(record)
        for value in ("ghp_012345678901234567890123", "xoxb-1234567890-abcdef", "AKIA1234567890ABCDEF", "npm_01234567890123456789", "Aa1Bb2Cc3Dd4Ee5Ff6Gg7Hh8Ii9"):
            record = copy.deepcopy(base_records()["engine"][0]); record["description"] = value
            with self.assertRaisesRegex(ContractError, "secret"):
                validate_record(record)

    def test_assignment_digest_and_trace_are_deterministic(self):
        task = {
            "task_id": "task-phase1", "project_id": "recursion", "source_repository": "/opt/recursion",
            "source_branch": "master", "source_sha": "a" * 40, "seed_manifest_digest": "b" * 64,
            "gate_digest": "c" * 64, "allowed_paths": ["docs"], "role": "implementer", "execution_profile": "implementation",
            "requirements": {"capabilities": ["workspace-edit"], "operating_system": "linux"},
            "created_at": "2026-08-28T00:00:00Z",
        }
        first = resolve_assignment(task, base_records())
        second = resolve_assignment(task, base_records())
        self.assertEqual(first.status, "assigned")
        self.assertEqual(first.assignment, second.assignment)
        self.assertEqual(first.trace, second.trace)
        self.assertEqual(first.assignment["assignment_digest"], digest({k: v for k, v in first.assignment.items() if k != "assignment_digest"}))
        self.assertTrue(first.trace)
        changed = copy.deepcopy(first.assignment); changed["host_id"] = "other-host"
        with self.assertRaisesRegex(ContractError, "digest"):
            validate_record(changed)

    def test_manual_pin_is_strict_and_no_metered_fallback(self):
        cfg = base_records()
        task = {"task_id": "pin", "project_id": "recursion", "source_repository": "/opt/recursion", "source_branch": "master", "source_sha": "a" * 40, "seed_manifest_digest": "b" * 64, "gate_digest": "c" * 64, "allowed_paths": ["docs"], "role": "implementer", "execution_profile": "implementation", "requirements": {"capabilities": ["workspace-edit"]}, "manual_pin": {"engine": "missing", "provider": "anthropic", "capacity_pool": "claude-subscription", "model": "claude-sonnet", "host": "gs-recursion", "sandbox_profile": "strict-linux"}}
        result = resolve_assignment(task, cfg, policy="manual-pin")
        self.assertEqual(result.status, "deferred")
        self.assertTrue(any("manual-pin-mismatch" in x["rejections"] for x in result.trace))
        pool = copy.deepcopy(cfg["capacity_pool"][0]); pool["id"] = "metered-pool"; pool["billing_basis"] = "metered"; pool["on_demand"] = True; cfg["capacity_pool"].append(pool)
        result = resolve_assignment(task, cfg, policy="no-metered-fallback")
        self.assertNotEqual(result.assignment and result.assignment["capacity_pool_id"], "metered-pool")
        task["allow_metered"] = True
        with self.assertRaisesRegex(ContractError, "cannot authorize"):
            resolve_assignment(task, base_records())
        cfg = base_records()
        metered = copy.deepcopy(cfg["capacity_pool"][0]); metered["id"] = "metered-pool"; metered["billing_basis"] = "metered"; metered["on_demand"] = True; metered["fallback_policy"] = "approved"; cfg["capacity_pool"] = [metered]
        cfg["execution_profile"][0]["capacity_pool_ids"] = ["metered-pool"]
        cfg["project"][0]["eligible_pools"] = []
        cfg["routing_policy"].append({"schema_version": 2, "kind": "routing_policy", "id": "approved-metered", "policy": "subscription-first", "role": "implementer", "candidate_order": ["billing_basis"], "allow_metered": True, "fallback_policy": "approved"})
        approved_task = dict(task); approved_task.pop("allow_metered")
        approved = resolve_assignment(approved_task, cfg, policy="approved-metered")
        self.assertEqual(approved.assignment["capacity_pool_id"], "metered-pool")

    def test_component_capabilities_and_provider_egress_are_not_unionable(self):
        cfg = base_records()
        cfg["engine"][0]["capabilities"] = ["terminal"]
        task = {"task_id": "caps", "project_id": "recursion", "source_repository": "/opt/recursion", "source_branch": "master", "source_sha": "a" * 40, "seed_manifest_digest": "b" * 64, "gate_digest": "c" * 64, "allowed_paths": ["docs"], "role": "implementer", "execution_profile": "implementation", "requirements": {"capabilities": ["workspace-edit"]}}
        result = resolve_assignment(task, cfg)
        self.assertEqual(result.status, "deferred")
        self.assertTrue(any("missing-engine-capabilities:workspace-edit" in x["rejections"] for x in result.trace))
        cfg = base_records(); cfg["host"][0]["network_endpoints"] = []
        result = resolve_assignment(task, cfg)
        self.assertEqual(result.status, "deferred")
        self.assertTrue(any("provider-endpoint-unavailable-on-host" in x["rejections"] for x in result.trace))

    def test_empty_duplicate_and_traversal_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.json"; path.write_text(json.dumps({"schema_version": 2, "registry": "engine", "entries": []}), encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "empty"):
                load_registry(path, "engine")
            duplicate = copy.deepcopy(base_records()["engine"][0])
            path.write_text(json.dumps({"schema_version": 2, "registry": "engine", "entries": [duplicate, duplicate]}), encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "duplicate"):
                load_registry(path, "engine")
            with self.assertRaisesRegex(ContractError, "unsafe path"):
                load_registry(Path(tmp) / ".." / "empty.json", "engine")
            record = copy.deepcopy(base_records()["engine"][0]); record["runtime_layout"]["runtime_paths"] = ["../escape"]
            with self.assertRaisesRegex(ContractError, "unsafe path"):
                validate_record(record)
            link = Path(tmp) / "link.json"
            try:
                link.symlink_to(path)
            except (OSError, NotImplementedError):
                pass
            else:
                with self.assertRaisesRegex(ContractError, "symlink"):
                    load_registry(link, "engine")

    def test_v1_readers_preserve_legacy_shape(self):
        v1 = {"schema_version": 1, "name": "cursor", "description": "legacy", "executable": "cursor-agent", "argv": ["{{EXE}}", "{{PROMPT}}"], "roles": ["implementer"], "billing": {"basis": "flat-subscription", "provider": "cursor"}, "network": {"policy": "provider-only", "endpoints": ["cursor.com"]}, "env_passthrough": []}
        self.assertEqual(read_v1_manifest(v1)["schema_version"], 1)
        row = read_v1_portfolio_row("demo\t/opt/demo\tgit@example/demo.git\tmain\t~/.ssh/demo\t-\t1\tactive")
        self.assertEqual(row["id"], "demo"); self.assertEqual(row["default_branch"], "main")
        header = read_v1_task_header("schema_version: 1\nid: demo-task\ngoal_id: demo-goal\nproject_id: demo\nworker_class: build\nacceptance: pass\nallowed_paths: docs,src\nstatus: ready\n")
        self.assertEqual(header["task_id"], "demo-task"); self.assertEqual(header["allowed_paths"], ["docs", "src"])

    def test_cli_is_dry_and_emits_trace(self):
        task = {"task_id": "cli", "project_id": "recursion", "source_repository": "/opt/recursion", "source_branch": "master", "source_sha": "a" * 40, "seed_manifest_digest": "b" * 64, "gate_digest": "c" * 64, "allowed_paths": ["docs"], "role": "implementer", "execution_profile": "implementation", "requirements": {"capabilities": ["workspace-edit"]}}
        with tempfile.TemporaryDirectory() as tmp:
            task_file = Path(tmp) / "task.json"; task_file.write_text(json.dumps(task), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "resolve-assignment.py"), "--task", str(task_file), "--config-dir", str(ROOT / "config" / "v2")], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            output = json.loads(proc.stdout)
            self.assertEqual(output["status"], "assigned"); self.assertIn("trace", output); self.assertFalse((Path(tmp) / "assignment.json").exists())

    def test_second_review_adversarial_contracts_fail_closed(self):
        cfg = base_records()
        with self.assertRaisesRegex(ContractError, "unknown fields"):
            validate_registry({"schema_version": 2, "registry": "engine", "entries": [cfg["engine"][0]], "poison": True}, "engine")
        with self.assertRaisesRegex(ContractError, "kind"):
            validate_registry({"schema_version": 2, "registry": "engine", "entries": [cfg["provider"][0]]})
        with self.assertRaisesRegex(ContractError, "billing_basis"):
            bad = copy.deepcopy(cfg["capacity_pool"][0]); bad["billing_basis"] = "free-unlimited"; validate_record(bad)
        with self.assertRaisesRegex(ContractError, "unknown role"):
            bad = copy.deepcopy(cfg["routing_policy"][0]); bad["role"] = "operator"; validate_record(bad)
        with self.assertRaises(ContractError):
            bad = copy.deepcopy(cfg["routing_policy"][0]); bad["candidate_order"] = ["pool_id", "pool_id"]; validate_record(bad)
        with self.assertRaises(ContractError):
            bad = copy.deepcopy(cfg["model"][0]); bad["provider_ids"] = ["../provider"]; validate_record(bad)
        with self.assertRaisesRegex(ContractError, "unknown fields"):
            task = {"task_id": "strict", "project_id": "recursion", "source_repository": "/opt/recursion", "source_branch": "master", "source_sha": "a" * 40, "seed_manifest_digest": "b" * 64, "gate_digest": "c" * 64, "allowed_paths": ["docs"], "role": "implementer", "execution_profile": "implementation", "requirements": {"capabilities": []}, "future": True}
            resolve_assignment(task, cfg)
        with self.assertRaisesRegex(ContractError, "unknown fields"):
            task = {"task_id": "strict", "project_id": "recursion", "source_repository": "/opt/recursion", "source_branch": "master", "source_sha": "a" * 40, "seed_manifest_digest": "b" * 64, "gate_digest": "c" * 64, "allowed_paths": ["docs"], "role": "implementer", "execution_profile": "implementation", "requirements": {"future": True}}
            resolve_assignment(task, cfg)
        bad = copy.deepcopy(cfg["host"][0]); bad["operating_system"] = "windows"; cfg["host"] = [bad]
        task = {"task_id": "os-check", "project_id": "recursion", "source_repository": "/opt/recursion", "source_branch": "master", "source_sha": "a" * 40, "seed_manifest_digest": "b" * 64, "gate_digest": "c" * 64, "allowed_paths": ["docs"], "role": "implementer", "execution_profile": "implementation", "requirements": {"capabilities": ["workspace-edit"]}}
        self.assertEqual(resolve_assignment(task, cfg).status, "deferred")
        cfg = base_records(); task["requirements"]["network_profile"] = "other-egress"
        result = resolve_assignment(task, cfg); self.assertEqual(result.status, "deferred")
        self.assertTrue(any("network-profile-mismatch" in x["rejections"] for x in result.trace))
        task["requirements"]["network_profile"] = "anthropic-provider-only"
        result = resolve_assignment(task, cfg); self.assertEqual(result.status, "assigned")
        self.assertEqual(result.assignment["network_profile"], "anthropic-provider-only")
        task["task_id"] = "not_allowed"
        with self.assertRaisesRegex(ContractError, "invalid format"):
            resolve_assignment(task, cfg)
        duplicate = copy.deepcopy(cfg["routing_policy"][0]); duplicate["id"] = "another-cheapest"; cfg["routing_policy"].append(duplicate)
        with self.assertRaisesRegex(ContractError, "ambiguous"):
            resolve_assignment(task, cfg)

    def test_third_review_scope_profile_and_parity_controls(self):
        cfg = base_records()
        task = {"task_id": "scope", "project_id": "recursion", "source_repository": "/opt/recursion", "source_branch": "master", "source_sha": "a" * 40, "seed_manifest_digest": "b" * 64, "gate_digest": "c" * 64, "allowed_paths": ["docs/sub"], "role": "implementer", "execution_profile": "implementation", "requirements": {"capabilities": ["workspace-edit"]}}
        with self.assertRaisesRegex(ContractError, "allowed_paths"):
            resolve_assignment(dict(task, allowed_paths=["src"]), cfg)
        with self.assertRaisesRegex(ContractError, "source_repository"):
            resolve_assignment(dict(task, source_repository="/other"), cfg)
        with self.assertRaisesRegex(ContractError, "execution_profile"):
            resolve_assignment(dict(task, execution_profile="unknown-profile"), cfg)
        cfg["provider"][0]["data_classification"] = "restricted"
        data_task = copy.deepcopy(task); data_task["requirements"] = {"data_class": "approved-project-data"}
        self.assertEqual(resolve_assignment(data_task, cfg).status, "deferred")
        sandbox = copy.deepcopy(cfg["sandbox_profile"][0]); sandbox["controller_visibility"] = "controller"
        with self.assertRaises(ContractError): validate_record(sandbox)
        cfg = base_records(); cfg["sandbox_profile"][0]["trust_class"] = "isolated"
        self.assertEqual(resolve_assignment(task, cfg).status, "deferred")
        with self.assertRaises(ContractError):
            bad_pool = copy.deepcopy(base_records()["capacity_pool"][0]); bad_pool["cooldown_s"] = -1; validate_record(bad_pool)
        first = resolve_assignment(task, base_records()).assignment
        changed = dict(task, source_sha="d" * 40)
        second = resolve_assignment(changed, base_records()).assignment
        self.assertNotEqual(first["id"], second["id"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "unexpected.txt").write_text("x", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "root file"):
                load_config(root)

    def test_weighted_rotation_survives_candidate_order(self):
        cfg = base_records()
        extra = copy.deepcopy(cfg["capacity_pool"][0]); extra["id"] = "pool-b"; cfg["capacity_pool"].append(extra)
        cfg["project"][0]["eligible_pools"] = []
        cfg["execution_profile"][0]["capacity_pool_ids"] = ["claude-subscription", "pool-b"]
        cfg["routing_policy"].append({"schema_version": 2, "kind": "routing_policy", "id": "weighted", "policy": "weighted-rotation", "role": "implementer", "candidate_order": ["pool_id"], "allow_metered": False, "fallback_policy": "defer", "weights": {"claude-subscription": 1, "pool-b": 100}})
        template = {"task_id": "weighted-0", "project_id": "recursion", "source_repository": "/opt/recursion", "source_branch": "master", "source_sha": "a" * 40, "seed_manifest_digest": "b" * 64, "gate_digest": "c" * 64, "allowed_paths": ["docs"], "role": "implementer", "execution_profile": "implementation", "requirements": {"capabilities": ["workspace-edit"]}}
        chosen = []
        for index in range(40):
            task = dict(template, task_id=f"weighted-{index}")
            result = resolve_assignment(task, cfg, policy="weighted")
            self.assertEqual(result.status, "assigned")
            chosen.append(result.assignment["capacity_pool_id"])
            self.assertEqual(result.assignment, resolve_assignment(task, cfg, policy="weighted").assignment)
        self.assertGreater(chosen.count("pool-b"), chosen.count("claude-subscription"))


if __name__ == "__main__":
    unittest.main()
