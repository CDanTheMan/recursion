#!/usr/bin/env python3
"""Hermetic Phase 2 repository-contract tests."""

from __future__ import annotations

import json
import hashlib
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
import repository_contract as rc


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=True)
    return result.stdout.strip()


def git_raw(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=True)
    return result.stdout


class RepositoryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="recursion-v2-contract-")
        self.repo = Path(self.temp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.name", "contract-test")
        git(self.repo, "config", "user.email", "contract-test@example.invalid")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "base.txt").write_text("base\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "base")
        self.source = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "branch", "recursion/integration", self.source)
        self.contract = {
            "schema_version": 1,
            "id": "test-project",
            "repo": str(self.repo),
            "default_branch": "main",
            "integration_branch": "recursion/integration",
            "task_branch_pattern": "recursion/task/{task_id}",
            "external_branch_patterns": ["cursor/*", "recursion/extern/*"],
            "publication_policy": "verified-integration-only",
            "source_policy": "exact-sha",
            "allowed_paths": ["src"],
            "gate_commands": ["python -m unittest"],
            "eligible_hosts": ["gs-recursion"],
            "eligible_pools": ["local"],
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def candidate(self) -> dict[str, object]:
        git(self.repo, "checkout", "-qb", "cursor/task-one")
        (self.repo / "src" / "feature.txt").write_text("candidate\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "candidate")
        commit = git(self.repo, "rev-parse", "HEAD")
        candidate = {
            "project_id": "test-project", "task_id": "task-one", "source_branch": "main",
            "source_sha": self.source, "external_branch": "cursor/task-one",
            "candidate_commit": commit, "idempotency_key": "dispatch-1",
        }
        candidate["verification_receipt"] = self.receipt(candidate)
        return candidate

    def receipt(self, candidate: dict[str, object]) -> dict[str, object]:
        diff = git_raw(self.repo, "diff", "--binary", str(candidate["source_sha"]), str(candidate["candidate_commit"]))
        paths = [item for item in git(self.repo, "diff", "--name-only", str(candidate["source_sha"]), str(candidate["candidate_commit"])).splitlines() if item]
        body = {
            "schema": "recursion-controller-verifier-receipt/v1", "project_id": "test-project",
            "task_id": candidate["task_id"], "source_sha": candidate["source_sha"],
            "candidate_commit": candidate["candidate_commit"],
            "diff_sha256": hashlib.sha256(diff.encode()).hexdigest(),
            "scope_digest": rc._json_digest(paths), "gate_digest": rc._json_digest(self.contract["gate_commands"]),
            "verdict": "pass", "verifier": "controller-verifier", "provenance": "recursion-controller",
        }
        return {**body, "receipt_digest": rc._json_digest(body)}

    def test_descriptor_and_exact_source_admission(self) -> None:
        rc.validate_project_descriptor(self.contract)
        task = rc.admit_task(self.contract, {
            "id": "task-one", "source_branch": "main", "source_sha": self.source,
            "allowed_paths": ["src"],
        }, self.repo)
        self.assertEqual(task["source_sha"], self.source)
        with self.assertRaisesRegex(rc.ContractError, "exact source_sha"):
            rc.admit_task(self.contract, {"id": "task-two", "source_branch": "main"}, self.repo)
        with self.assertRaisesRegex(rc.ContractError, "apps/chiron"):
            rc.admit_task(self.contract, {
                "id": "task-three", "source_branch": "main", "source_sha": self.source,
                "allowed_paths": ["apps/chiron"],
            }, self.repo)
        with self.assertRaisesRegex(rc.ContractError, "widens"):
            rc.admit_task(self.contract, {
                "id": "task-four", "source_branch": "main", "source_sha": self.source,
                "allowed_paths": ["."],
            }, self.repo)

    def test_runtime_descriptor_uniqueness_and_namespace_overlap(self) -> None:
        invalid_repo = dict(self.contract, repo=7)
        with self.assertRaisesRegex(rc.ContractError, "repo"):
            rc.validate_project_descriptor(invalid_repo)
        duplicate_hosts = dict(self.contract, eligible_hosts=["gs-recursion", "gs-recursion"])
        with self.assertRaisesRegex(rc.ContractError, "eligible_hosts"):
            rc.validate_project_descriptor(duplicate_hosts)
        with self.assertRaisesRegex(rc.ContractError, "unique normalized"):
            rc.validate_project_descriptor(dict(self.contract, allowed_paths=["src/", "src"]))
        overlap = dict(self.contract, external_branch_patterns=["recursion/*"])
        with self.assertRaisesRegex(rc.ContractError, "overlaps"):
            rc.validate_project_descriptor(overlap)
        self.assertEqual(rc.branch_kind(self.contract, "recursion/task/task-one"), "task")

    def test_executor_branch_rules(self) -> None:
        with self.assertRaisesRegex(rc.ContractError, "default branch"):
            rc.branch_kind(self.contract, "main")
        with self.assertRaisesRegex(rc.ContractError, "integration branch"):
            rc.branch_kind(self.contract, "recursion/integration")
        self.assertEqual(rc.branch_kind(self.contract, "cursor/task-one"), "external")
        self.assertEqual(rc.task_branch(self.contract, "task-one"), "recursion/task/task-one")

    def test_all_new_generation_fields_reject_legacy_chiron(self) -> None:
        for field in ("workdir", "acceptance", "gate_command", "gate_commands", "seed", "goal"):
            task = {"id": "task-one", "source_branch": "main", "source_sha": self.source,
                    "allowed_paths": ["src"], field: ".\\apps\\chiron/"}
            with self.subTest(field=field), self.assertRaisesRegex(rc.ContractError, "apps/chiron"):
                rc.admit_task(self.contract, task, self.repo)

    def test_verified_import_is_idempotent_and_cas(self) -> None:
        candidate = self.candidate()
        verified = rc.verify_candidate(self.contract, candidate, self.repo)
        self.assertEqual(verified["changed_paths"], ["src/feature.txt"])
        first = rc.import_candidate(self.contract, candidate, self.repo)
        second = rc.import_candidate(self.contract, candidate, self.repo)
        self.assertEqual(first["status"], "imported")
        self.assertEqual(second["status"], "idempotent")
        self.assertEqual(git(self.repo, "rev-parse", "refs/heads/recursion/task/task-one"), candidate["candidate_commit"])
        changed = dict(candidate)
        git(self.repo, "checkout", "-qb", "cursor/other")
        (self.repo / "src" / "other.txt").write_text("other\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "other")
        changed["candidate_commit"] = git(self.repo, "rev-parse", "HEAD")
        changed["external_branch"] = "cursor/other"
        changed["verification_receipt"] = self.receipt(changed)
        with self.assertRaisesRegex(rc.ContractError, "different candidate"):
            rc.import_candidate(self.contract, changed, self.repo)

    def test_import_race_reconciles_identical_winner_and_receipt_is_required(self) -> None:
        candidate = self.candidate()
        missing_receipt = dict(candidate)
        missing_receipt.pop("verification_receipt")
        with self.assertRaisesRegex(rc.ContractError, "verification receipt"):
            rc.verify_candidate(self.contract, missing_receipt, self.repo)
        winner = candidate["candidate_commit"]
        original = rc._git
        raced = {"update": False}

        def race(repo: Path, *args: str):
            if args and args[0] == "update-ref" and not raced["update"]:
                raced["update"] = True
                original(repo, "update-ref", "refs/heads/recursion/task/task-one", winner, "0" * 40)
                return subprocess.CompletedProcess(["git"], 1, "", "simulated CAS loss")
            return original(repo, *args)

        with mock.patch.object(rc, "_git", side_effect=race):
            result = rc.import_candidate(self.contract, candidate, self.repo)
        self.assertEqual(result["status"], "idempotent")

    def test_scope_and_stale_classification(self) -> None:
        candidate = self.candidate()
        no_receipt = dict(candidate)
        no_receipt.pop("verification_receipt")
        self.assertEqual(rc.classify_stale_base(self.contract, no_receipt, self.repo), "unauthorized-result")
        bad = dict(candidate)
        git(self.repo, "checkout", "-qb", "cursor/bad")
        (self.repo / "outside.txt").write_text("no\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "outside")
        bad["candidate_commit"] = git(self.repo, "rev-parse", "HEAD")
        bad["external_branch"] = "cursor/bad"
        with self.assertRaisesRegex(rc.ContractError, "outside allowed_paths"):
            rc.verify_candidate(self.contract, bad, self.repo)
        # Return to the valid external ref and prove a current source is compatible.
        valid = rc.verify_candidate(self.contract, candidate, self.repo)
        self.assertEqual(rc.classify_stale_base(self.contract, valid, self.repo), "current-compatible")
        # Advance default independently; the exact candidate remains reviewable but cannot be
        # silently rebased into the integration ref.
        git(self.repo, "checkout", "main")
        (self.repo / "src" / "main.txt").write_text("main\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "main advances")
        self.assertEqual(rc.classify_stale_base(self.contract, valid, self.repo), "stale-rebase-required")

    def test_plan_is_read_only_and_serialized(self) -> None:
        candidate = self.candidate()
        before = git(self.repo, "rev-parse", "refs/heads/recursion/integration")
        plan = rc.plan_integration(self.contract, candidate, self.repo)
        self.assertTrue(plan["serialized"])
        self.assertEqual(plan["expected_destination_tip"], before)
        self.assertTrue(plan["can_integrate"])
        self.assertEqual(git(self.repo, "rev-parse", "refs/heads/recursion/integration"), before)


if __name__ == "__main__":
    unittest.main()
