#!/usr/bin/env python3
"""Hermetic Phase 2 repository-contract tests."""

from __future__ import annotations

import json
import hashlib
import hmac
import os
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
        self.key_path = Path(self.temp.name) / "controller.key"
        self.key_path.write_text("hermetic-controller-key\n", encoding="utf-8")
        os.chmod(self.key_path, 0o600)
        self.old_controller_key_path = rc.CONTROLLER_KEY_PATH
        rc.CONTROLLER_KEY_PATH = self.key_path
        self.old_receipt_key = os.environ.get("RECURSION_VERIFIER_RECEIPT_KEY")
        self.old_receipt_key_file = os.environ.get("RECURSION_VERIFIER_RECEIPT_KEY_FILE")
        os.environ["RECURSION_VERIFIER_RECEIPT_KEY"] = "hostile-caller-key"
        os.environ["RECURSION_VERIFIER_RECEIPT_KEY_FILE"] = str(Path(self.temp.name) / "hostile.key")
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
            "gate_commands": ["git diff --check"],
            "eligible_hosts": ["gs-recursion"],
            "eligible_pools": ["local"],
        }

    def tearDown(self) -> None:
        rc.CONTROLLER_KEY_PATH = self.old_controller_key_path
        if self.old_receipt_key is None:
            os.environ.pop("RECURSION_VERIFIER_RECEIPT_KEY", None)
        else:
            os.environ["RECURSION_VERIFIER_RECEIPT_KEY"] = self.old_receipt_key
        if self.old_receipt_key_file is None:
            os.environ.pop("RECURSION_VERIFIER_RECEIPT_KEY_FILE", None)
        else:
            os.environ["RECURSION_VERIFIER_RECEIPT_KEY_FILE"] = self.old_receipt_key_file
        self.temp.cleanup()

    def candidate(self) -> dict[str, object]:
        git(self.repo, "checkout", "-qB", "cursor/task-one")
        (self.repo / "src" / "feature.txt").write_text("candidate\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "candidate")
        commit = git(self.repo, "rev-parse", "HEAD")
        candidate = {
            "project_id": "test-project", "task_id": "task-one", "source_branch": "main",
            "source_sha": self.source, "external_branch": "cursor/task-one",
            "candidate_commit": commit, "idempotency_key": "dispatch-1",
        }
        return candidate

    def plumbed_candidate(self, entry: str, name: str, base_candidate: dict[str, object] | None = None) -> dict[str, object]:
        """Build a candidate tree with an arbitrary mode, independent of checkout symlink support."""
        candidate = base_candidate or self.candidate()
        source_tree = git(self.repo, "rev-parse", f"{candidate['candidate_commit']}:src")
        src_entries = [line.rstrip("\r") for line in git_raw(self.repo, "ls-tree", source_tree).splitlines()]
        src_entries.append(f"{entry}\t{name}")
        made_src = subprocess.run(["git", "-C", str(self.repo), "mktree"],
                                  input=("\n".join(sorted(src_entries)) + "\n").encode(),
                                  capture_output=True, check=True).stdout.decode().strip()
        root_tree = git(self.repo, "rev-parse", f"{candidate['candidate_commit']}^{{tree}}")
        root_entries = [line.rstrip("\r") for line in git_raw(self.repo, "ls-tree", root_tree).splitlines()
                        if not line.rstrip("\r").endswith("\tsrc")]
        root_entries.append(f"040000 tree {made_src}\tsrc")
        made_root = subprocess.run(["git", "-C", str(self.repo), "mktree"],
                                   input=("\n".join(sorted(root_entries)) + "\n").encode(),
                                   capture_output=True, check=True).stdout.decode().strip()
        made_commit = subprocess.run(["git", "-C", str(self.repo), "commit-tree", made_root, "-p", self.source],
                                     input=f"{name}\n", text=True, capture_output=True, check=True).stdout.strip()
        branch = f"cursor/{name}"
        subprocess.run(["git", "-C", str(self.repo), "update-ref", f"refs/heads/{branch}", made_commit], check=True)
        return {**candidate, "external_branch": branch, "candidate_commit": made_commit}

    def receipt(self, candidate: dict[str, object]) -> dict[str, object]:
        diff = git_raw(self.repo, "diff", "--binary", str(candidate["source_sha"]), str(candidate["candidate_commit"]))
        paths = [item for item in git(self.repo, "diff", "--name-only", str(candidate["source_sha"]), str(candidate["candidate_commit"])).splitlines() if item]
        body = {
            "schema": "recursion-controller-verifier-receipt/v1", "project_id": "test-project",
            "task_id": candidate["task_id"], "source_sha": candidate["source_sha"],
            "candidate_commit": candidate["candidate_commit"],
            "diff_sha256": hashlib.sha256(diff.encode()).hexdigest(),
            "scope_digest": rc._json_digest(candidate.get("allowed_paths", self.contract["allowed_paths"])),
            "gate_digest": rc._json_digest(self.contract["gate_commands"]),
            "verdict": "pass", "verifier": "controller-verifier", "provenance": "recursion-controller",
        }
        receipt_digest = rc._json_digest(body)
        signature = hmac.new(b"hermetic-controller-key", receipt_digest.encode("ascii"), hashlib.sha256).hexdigest()
        return {**body, "receipt_digest": receipt_digest, "signature": signature}

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
        wrong = Path(self.temp.name) / "wrong-clone"
        subprocess.run(["git", "clone", "-q", str(self.repo), str(wrong)], check=True)
        with self.assertRaisesRegex(rc.ContractError, "does not match"):
            rc.admit_task(self.contract, {
                "id": "task-five", "source_branch": "main", "source_sha": self.source,
                "allowed_paths": ["src"],
            }, wrong)

    def test_runtime_descriptor_uniqueness_and_namespace_overlap(self) -> None:
        invalid_repo = dict(self.contract, repo=7)
        with self.assertRaisesRegex(rc.ContractError, "repo"):
            rc.validate_project_descriptor(invalid_repo)
        duplicate_hosts = dict(self.contract, eligible_hosts=["gs-recursion", "gs-recursion"])
        with self.assertRaisesRegex(rc.ContractError, "eligible_hosts"):
            rc.validate_project_descriptor(duplicate_hosts)
        with self.assertRaisesRegex(rc.ContractError, "canonical"):
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
            if field == "gate_commands":
                task[field] = [task[field]]
            with self.subTest(field=field), self.assertRaisesRegex(rc.ContractError, "apps/chiron"):
                rc.admit_task(self.contract, task, self.repo)
        punctuation = {"id": "task-one", "source_branch": "main", "source_sha": self.source,
                       "allowed_paths": ["src"], "acceptance": "cd apps/chiron;)&|"}
        with self.assertRaisesRegex(rc.ContractError, "apps/chiron"):
            rc.admit_task(self.contract, punctuation, self.repo)
        dotted = dict(punctuation, acceptance="cd apps/./chiron;", goal="safe")
        with self.assertRaisesRegex(rc.ContractError, "apps/chiron"):
            rc.admit_task(self.contract, dotted, self.repo)

    def test_verified_import_is_idempotent_and_cas(self) -> None:
        candidate = self.candidate()
        verified = rc.verify_candidate(self.contract, candidate, self.repo, receipt=self.receipt(candidate))
        self.assertEqual(verified["changed_paths"], ["src/feature.txt"])
        wrong = Path(self.temp.name) / "verify-wrong-clone"
        subprocess.run(["git", "clone", "-q", str(self.repo), str(wrong)], check=True)
        with self.assertRaisesRegex(rc.ContractError, "does not match"):
            rc.verify_candidate(self.contract, candidate, wrong, receipt=self.receipt(candidate))
        first = rc.import_candidate(self.contract, candidate, self.repo, receipt=self.receipt(candidate))
        second = rc.import_candidate(self.contract, candidate, self.repo, receipt=self.receipt(candidate))
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
        with self.assertRaisesRegex(rc.ContractError, "different candidate"):
            rc.import_candidate(self.contract, changed, self.repo, receipt=self.receipt(changed))

        widened = dict(candidate, allowed_paths=["."])
        with self.assertRaisesRegex(rc.ContractError, "widens"):
            rc.verify_candidate(self.contract, widened, self.repo, receipt=self.receipt(widened))

    def test_allow_canonical_requires_exact_task_branch(self) -> None:
        candidate = self.candidate()
        canonical = dict(candidate, external_branch=rc.task_branch(self.contract, candidate["task_id"]))
        git(self.repo, "branch", canonical["external_branch"], candidate["candidate_commit"])
        with self.assertRaisesRegex(rc.ContractError, "exact task branch"):
            rc.verify_candidate(self.contract, dict(canonical, external_branch="recursion/task/other"),
                                self.repo, receipt=self.receipt(canonical), allow_canonical=True)
        verified = rc.verify_candidate(self.contract, canonical, self.repo,
                                       receipt=self.receipt(canonical), allow_canonical=True)
        self.assertEqual(verified["external_branch"], "recursion/task/task-one")

    def test_controller_key_cannot_be_selected_by_hostile_environment(self) -> None:
        candidate = self.candidate()
        receipt = self.receipt(candidate)
        self.assertEqual(rc.verify_candidate(self.contract, candidate, self.repo, receipt=receipt)["task_id"], "task-one")
        if os.name != "nt":
            os.chmod(self.key_path, 0o666)
            with self.assertRaisesRegex(rc.ContractError, "key"):
                rc.verify_candidate(self.contract, candidate, self.repo, receipt=receipt)

    def test_git_plumbed_symlink_and_submodule_tree_escapes_are_refused(self) -> None:
        # Create the exact unsafe target blob without requiring an OS-level symlink or elevated
        # Windows privilege.
        target = subprocess.run(["git", "-C", str(self.repo), "hash-object", "-w", "--stdin"],
                                input=b"../.GIT/Control-Plane\n", capture_output=True, check=True).stdout.decode().strip()
        base = self.candidate()
        symlink = self.plumbed_candidate(f"120000 blob {target}", "escape", base)
        with self.assertRaisesRegex(rc.ContractError, "symlink"):
            rc.verify_candidate(self.contract, symlink, self.repo, receipt=self.receipt(symlink))
        submodule = self.plumbed_candidate(f"160000 commit {self.source}", "submodule", base)
        with self.assertRaisesRegex(rc.ContractError, "submodule"):
            rc.verify_candidate(self.contract, submodule, self.repo, receipt=self.receipt(submodule))

    def test_malformed_task_fields_are_typed_before_legacy_guard(self) -> None:
        for field in ("acceptance", "goal", "workdir", "gate_command", "seed"):
            task = {"id": "task-one", "source_branch": "main", "source_sha": self.source,
                    "allowed_paths": ["src"], field: {"apps/chiron": True}}
            with self.subTest(field=field), self.assertRaisesRegex(rc.ContractError, "must be a string"):
                rc.admit_task(self.contract, task, self.repo)

    def test_invalid_refs_and_vacuous_gates_are_rejected(self) -> None:
        for field in ("default_branch", "integration_branch"):
            for branch in ("cursor/../main", "cursor//x", "foo.lock"):
                with self.subTest(field=field, branch=branch), self.assertRaises(rc.ContractError):
                    rc.validate_project_descriptor(dict(self.contract, **{field: branch}))
        for pattern in ("cursor//x", "cursor/../*", "cursor/\x00*"):
            with self.assertRaises(rc.ContractError):
                rc.validate_project_descriptor(dict(self.contract, external_branch_patterns=[pattern]))
        for path in ("src\\x", "src/./x", "src\x00x", " src"):
            with self.assertRaises(rc.ContractError):
                rc.validate_project_descriptor(dict(self.contract, allowed_paths=[path]))
        for command in ("", "   ", "true", "echo no-op", "printf nope", "pwd", "false||true",
                        "git diff --check||true", "(true)", "(false)", "{ true; }", "exit 0",
                        "git diff --check\ntrue", "x\x00y"):
            with self.subTest(command=command), self.assertRaises(rc.ContractError):
                rc.validate_project_descriptor(dict(self.contract, gate_commands=[command]))
        rc.validate_project_descriptor(dict(self.contract, gate_commands=["git\tdiff --check"]))

    def test_import_race_reconciles_identical_winner_and_receipt_is_required(self) -> None:
        candidate = self.candidate()
        with self.assertRaisesRegex(rc.ContractError, "verification receipt"):
            rc.verify_candidate(self.contract, candidate, self.repo)
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
            result = rc.import_candidate(self.contract, candidate, self.repo, receipt=self.receipt(candidate))
        self.assertEqual(result["status"], "idempotent")

    def test_forged_receipt_and_malformed_candidates_are_typed_refusals(self) -> None:
        candidate = self.candidate()
        receipt = self.receipt(candidate)
        forged = dict(receipt, signature="0" * 64)
        with self.assertRaisesRegex(rc.ContractError, "authentication"):
            rc.verify_candidate(self.contract, candidate, self.repo, receipt=forged)
        for malformed in (None, [], {"project_id": []}, {"project_id": "test-project", "task_id": []}):
            with self.subTest(malformed=malformed):
                try:
                    rc.verify_candidate(self.contract, malformed, self.repo, receipt=receipt)
                except rc.ContractError:
                    pass
                else:
                    self.fail("malformed candidate was not refused")

    def test_scope_and_stale_classification(self) -> None:
        candidate = self.candidate()
        self.assertEqual(rc.classify_stale_base(self.contract, candidate, self.repo), "unauthorized-result")
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
        valid = rc.verify_candidate(self.contract, candidate, self.repo, receipt=self.receipt(candidate))
        self.assertEqual(rc.classify_stale_base(self.contract, valid, self.repo, receipt=self.receipt(candidate)), "current-compatible")
        # Advance default independently; the exact candidate remains reviewable but cannot be
        # silently rebased into the integration ref.
        git(self.repo, "checkout", "main")
        (self.repo / "src" / "main.txt").write_text("main\n", encoding="utf-8")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "main advances")
        self.assertEqual(rc.classify_stale_base(self.contract, valid, self.repo, receipt=self.receipt(candidate)), "stale-rebase-required")

    def test_plan_is_read_only_and_serialized(self) -> None:
        candidate = self.candidate()
        before = git(self.repo, "rev-parse", "refs/heads/recursion/integration")
        plan = rc.plan_integration(self.contract, candidate, self.repo, receipt=self.receipt(candidate))
        self.assertTrue(plan["serialized"])
        self.assertEqual(plan["expected_destination_tip"], before)
        self.assertTrue(plan["can_integrate"])
        self.assertEqual(git(self.repo, "rev-parse", "refs/heads/recursion/integration"), before)


if __name__ == "__main__":
    unittest.main()
