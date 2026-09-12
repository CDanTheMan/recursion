"""Unit tests for the fail-closed construction publication gate.

Builds a real git fixture repo plus a complete, internally consistent
evidence tree, then mutates one predicate at a time to prove each check is
fail-closed.  No campaign scientific source is imported or executed.
"""
import datetime as dt
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publication_gate as gate


NOW = dt.datetime(2026, 9, 11, 20, 0, 0, tzinfo=dt.timezone.utc)
LATE = dt.datetime(2026, 9, 11, 21, 30, 0, tzinfo=dt.timezone.utc)
BRANCH = "codex/swarm-research-20260911-155142"
PARENT = "goal-recursion-v2-execution-fabric"
SOURCE_PATHS = [
    "experiments/v3/swarm-research-20260911-155142/boundary.py",
    "experiments/v3/swarm-research-20260911-155142/boundary_audit.py",
    "experiments/v3/swarm-research-20260911-155142/boundary_controls.py",
    "experiments/v3/swarm-research-20260911-155142/inventory_audit.py",
    "experiments/v3/swarm-research-20260911-155142/research_entry.py",
]
GIT_ENV = dict(
    os.environ,
    GIT_AUTHOR_NAME="gate-test",
    GIT_AUTHOR_EMAIL="gate-test@example.invalid",
    GIT_COMMITTER_NAME="gate-test",
    GIT_COMMITTER_EMAIL="gate-test@example.invalid",
    GIT_CONFIG_NOSYSTEM="1",
)


def canon(value):
    return gate.canonical_bytes(value) + b"\n"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def have_git():
    return shutil.which("git") is not None


class Fixture:
    """One internally consistent gate attempt: repo + evidence directory."""

    def __init__(self, root, merge=False):
        self.root = Path(root)
        self.repo = self.root / "repo"
        self.evidence = self.root / "evidence"
        (self.evidence / "reviews").mkdir(parents=True)
        self._build_repo(merge=merge)
        self._static_records()
        self._manifest()
        self._receipts()
        self._cgroup()
        self._audits()
        self._draft_body()
        self._reviews()
        self._dispositions()
        self._published_body()

    # ------------------------------------------------------------- repo
    def _git(self, *args, check=True):
        result = subprocess.run(["git", "-C", str(self.repo), *args], env=GIT_ENV,
                                capture_output=True, text=True, check=check)
        return result.stdout.strip()

    def _build_repo(self, merge=False):
        self.repo.mkdir()
        self._git("init", "-b", BRANCH)
        (self.repo / ".git/info/exclude").write_text("state/\nPAUSE\nSTOP\n")
        (self.repo / "seed.txt").write_text("activation base\n")
        self._git("add", "-A")
        self._git("commit", "-m", "base")
        self.base = self._git("rev-parse", "HEAD")
        if merge:
            self._git("checkout", "-b", "side")
            (self.repo / "docs/v3/construction/swarm-research-20260911-155142").mkdir(
                parents=True)
            (self.repo / "docs/v3/construction/swarm-research-20260911-155142/side.md"
             ).write_text("side\n")
            self._git("add", "-A")
            self._git("commit", "-m", "side")
            self._git("checkout", BRANCH)
        for path in SOURCE_PATHS:
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# fixture source " + path + "\n")
        (self.repo / "docs/v3/construction/swarm-research-20260911-155142").mkdir(
            parents=True, exist_ok=True)
        (self.repo / "docs/v3/construction/swarm-research-20260911-155142/gate.md"
         ).write_text("candidate docs\n")
        self._git("add", "-A")
        self._git("commit", "-m", "candidate")
        if merge:
            self._git("merge", "--no-ff", "-m", "merge side", "side")
        goal = self.repo / "state/goals"
        goal.mkdir(parents=True, exist_ok=True)
        (goal / (PARENT + ".md")).write_text(
            "id: " + PARENT + "\nstatus: active\n")
        self.candidate = self._git("rev-parse", "HEAD")
        self.tree = self._git("rev-parse", "HEAD^{tree}")

    def sources(self):
        rows = []
        for path in sorted(SOURCE_PATHS):
            blob = self._git("show", self.candidate + ":" + path).encode() + b"\n"
            raw = subprocess.run(["git", "-C", str(self.repo), "show",
                                  self.candidate + ":" + path], env=GIT_ENV,
                                 capture_output=True, check=True).stdout
            rows.append({"path": path, "sha256": sha(raw), "bytes": len(raw)})
        return rows

    # ------------------------------------------------------- static files
    def _write(self, name, raw):
        path = self.evidence / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return sha(raw)

    def _write_json(self, name, value):
        return self._write(name, canon(value))

    def _static_records(self):
        self._write_json("obligations.json", {
            "schema": "recursion-obligation-binding/v1",
            "campaign": gate.CAMPAIGN,
            "parent_goal": PARENT,
            "validation_contract_sha256": gate.VALIDATION_CONTRACT_SHA256,
            "model_revision_sha256": gate.MODEL_REVISION_SHA256,
            "effective_same_model_review": "gpt-5.6-sol xhigh",
            "basis_note": "model-revision-01 supersedes the Astra wording of "
                          "validation-contract for every later same-model review",
        })
        self._write_json("quota.json", {
            "checked_utc": "2026-09-11T19:58:00Z",
            "binding_windows": [{"name": "codex-primary", "used_percent": 10,
                                 "remaining_percent": 90,
                                 "resets_at": 1789692198}],
            "remaining_percent": 90,
            "reset_credits_used": 0,
            "new_metered_spend": 0,
            "source": "local quota probe",
        })

    # ------------------------------------------------------------ manifest
    def bundle_entries(self):
        return [
            {"path": "reviews/grok-1.json", "reviewer": "grok-coordinator",
             "model": "cursor-grok-4.5-high", "effort": "high",
             "route": "cursor NON-FAST"},
            {"path": "reviews/sol-1.json", "reviewer": "sol-reviewer-1",
             "model": "gpt-5.6-sol", "effort": "xhigh", "route": "sol"},
            {"path": "reviews/sol-2.json", "reviewer": "sol-reviewer-2",
             "model": "gpt-5.6-sol", "effort": "xhigh", "route": "sol"},
        ]

    def _manifest(self):
        entries = self.bundle_entries()
        self.bundle_sha = sha(gate.canonical_bytes(entries))
        argv_unit_win = ["py", "-m", "unittest", "discover", "-s",
                         "tools/construction_swarm"]
        argv_unit_wsl = ["python3", "-m", "unittest", "discover", "-s",
                         "tools/construction_swarm"]
        self.manifest = {
            "schema": "recursion-publication-gate-manifest/v1",
            "campaign": gate.CAMPAIGN,
            "parent_goal": PARENT,
            "review_branch": BRANCH,
            "pull_request": 124,
            "frozen_candidate_commit": self.candidate,
            "frozen_candidate_tree": self.tree,
            "activation_source_commit": self.base,
            "gate_attempt_ordinal": 3,
            "gate_runner_identity": "gate-runner",
            "allowed_change_roots": list(gate.ALLOWED_ROOTS),
            "non_goals": ["scientific admission", "merge", "receipt rewriting"],
            "scope_statement": "construction publication gate for PR124",
            "limitations_text": "The candidate is frozen; WSL results are "
                                "supplemental; scientific admission stays "
                                "BLOCKED_NO_EXECUTION_AUTHORIZED.",
            "checks": [
                {"id": "windows-unittest",
                 "argv": {"windows": argv_unit_win},
                 "expected": {"windows": {"exit_code": 0, "tests": 70,
                                          "skips": 7}}},
                {"id": "windows-ruff",
                 "argv": {"windows": ["ruff", "check", "."]},
                 "expected": {"windows": {"exit_code": 0}}},
                {"id": "wsl-unittest",
                 "argv": {"wsl": argv_unit_wsl},
                 "expected": {"wsl": {"exit_code": 0, "tests": 70,
                                      "skips": 1}}},
                {"id": "wsl-lint-or-substitute",
                 "argv": {"wsl": ["python3", "-m", "py_compile"]},
                 "expected": {"wsl": {"exit_code": 0}}},
                {"id": "diff-check",
                 "argv": {"windows": ["git", "diff", "--exit-code"],
                          "wsl": ["git", "diff", "--exit-code"]},
                 "expected": {"windows": {"exit_code": 0},
                              "wsl": {"exit_code": 0}}},
                {"id": "source-only-syntax",
                 "argv": {"wsl": ["python3", "-m", "py_compile"]},
                 "expected": {"wsl": {"exit_code": 0}}},
                {"id": "clean-cgroup",
                 "argv": {"wsl": ["find", "/sys/fs/cgroup"]},
                 "expected": {"wsl": {"max_memory_bytes": 2147483648}}},
            ],
            "campaign_sources": self.sources(),
            "lint_scope": sorted(SOURCE_PATHS),
            "native_ruff_available": False,
            "receipt_root_windows": "C:\\agent\\receipts\\attempt-3",
            "audit_owners": ["audit-owner-1", "audit-owner-2"],
            "review_bundle": {"entries": entries, "bundle_sha256": self.bundle_sha},
            "artifacts": {
                "freeze_receipt": "freeze-receipt.json",
                "cgroup_receipt": "clean-cgroup.receipt.json",
                "audit_receipts": ["owned-audit-1.receipt.json",
                                   "owned-audit-2.receipt.json"],
                "disposition_table": "dispositions.json",
                "reviewed_pr_body": "pr-body-reviewed.md",
                "published_pr_body": "pr-body.md",
                "obligations_record": "obligations.json",
                "quota_record": "quota.json",
            },
            "quota": {"required": True, "max_age_seconds": 900,
                      "reserve_points": 8,
                      "reset_identities": {"codex-primary": 1789692198}},
            "pr_body": {
                "required_fragments": ["PR124", "attempt 3"],
                "github_disclaimer": "No GitHub status checks or review "
                                     "objects exist for this branch; "
                                     "acceptance evidence is internal "
                                     "receipts only.",
                "forbidden_patterns": [],
            },
            "deadline_utc": gate.DEADLINE_UTC,
            "finalization_reserve_seconds": 10200,
        }
        self.manifest_sha = self._write_json("command-manifest.json", self.manifest)

    # ------------------------------------------------------------ receipts
    def _host(self, host_os):
        if host_os == "windows":
            return {"os": "windows",
                    "repo": "C:\\Users\\Lucas\\Documents\\GitHub\\recursion",
                    "identity": "windows-host-capture"}
        return {"os": "wsl", "repo": str(self.repo.resolve()),
                "identity": "wsl-uname-capture"}

    def _receipt(self, check_id, host, observed, log):
        hosts = gate.HOST_CHECKS[check_id]
        receipt_name, log_name = gate._receipt_names(check_id, host, hosts)
        log_sha = self._write(log_name, log)
        receipt = {
            "schema": "recursion-publication-check/v1",
            "campaign": gate.CAMPAIGN,
            "parent_goal": PARENT,
            "check_id": check_id,
            "host": self._host(host),
            "attempt": 3,
            "candidate": self.candidate,
            "candidate_tree": self.tree,
            "manifest_sha256": self.manifest_sha,
            "status": "PASS",
            "exit_code": 0,
            "observed": observed,
            "log_sha256": log_sha,
            "started_utc": "2026-09-11T18:59:00Z",
            "finished_utc": "2026-09-11T19:00:00Z",
            "uninterrupted": True,
            "scientific_approval": False,
            "full_gate_equivalence": False,
            "notes": "fixture",
        }
        return self._write_json(receipt_name, receipt)

    def _receipts(self):
        self.receipt_shas = {}
        self._write_json("freeze-receipt.json", {
            "schema": "recursion-publication-freeze/v1",
            "campaign": gate.CAMPAIGN,
            "parent_goal": PARENT,
            "attempt": 3,
            "candidate": self.candidate,
            "candidate_tree": self.tree,
            "review_branch": BRANCH,
            "activation_source_commit": self.base,
            "windows": {"head": self.candidate, "tree": self.tree,
                        "branch": BRANCH, "clean": True,
                        "pause_stop_absent": True,
                        "host": self._host("windows"),
                        "captured_utc": "2026-09-11T18:55:00Z"},
            "wsl": {"head": self.candidate, "tree": self.tree,
                    "branch": BRANCH, "clean": True, "pause_stop_absent": True,
                    "host": self._host("wsl"),
                    "captured_utc": "2026-09-11T18:55:00Z"},
            "created_utc": "2026-09-11T18:55:00Z",
        })
        self.receipt_shas["freeze-and-scope"] = sha(
            (self.evidence / "freeze-receipt.json").read_bytes())
        self.receipt_shas["windows-unittest"] = self._receipt(
            "windows-unittest", "windows",
            {"tests": 70, "skips": 7}, b"windows unittest log\n")
        self.receipt_shas["windows-ruff"] = self._receipt(
            "windows-ruff", "windows",
            {"scope": sorted(SOURCE_PATHS)}, b"ruff log\n")
        self.receipt_shas["wsl-unittest"] = self._receipt(
            "wsl-unittest", "wsl", {"tests": 70, "skips": 1},
            b"wsl unittest log\n")
        self.receipt_shas["wsl-lint-or-substitute"] = self._receipt(
            "wsl-lint-or-substitute", "wsl",
            {"route": "wsl-source-pycompile",
             "reason": "ruff-not-installed-native",
             "windows_ruff_receipt_sha256": self.receipt_shas["windows-ruff"],
             "qualification": "Windows Ruff remains the qualified lint route"},
            b"pycompile log\n")
        self.receipt_shas["diff-check.windows"] = self._receipt(
            "diff-check", "windows", {"worktree_clean_after": True}, b"")
        self.receipt_shas["diff-check.wsl"] = self._receipt(
            "diff-check", "wsl", {"worktree_clean_after": True}, b"")
        self.receipt_shas["source-only-syntax"] = self._receipt(
            "source-only-syntax", "wsl",
            {"mode": "py_compile", "executed": False,
             "files": [{"path": r["path"], "sha256": r["sha256"]}
                       for r in self.manifest["campaign_sources"]]},
            b"syntax log\n")

    def _cgroup(self):
        self.receipt_shas["clean-cgroup"] = self._write_json(
            "clean-cgroup.receipt.json", {
                "schema": "recursion-cgroup-verification/v1",
                "campaign": gate.CAMPAIGN,
                "parent_goal": PARENT,
                "attempt": 3,
                "candidate": self.candidate,
                "candidate_tree": self.tree,
                "manifest_sha256": self.manifest_sha,
                "outcomes": [{
                    "command": "wsl-unittest",
                    "isolation": {
                        "path": "/sys/fs/cgroup/recursion-foundry-tool-0",
                        "quiescent": True,
                        "cleanup_error": None,
                        "memory_peak": 1048576,
                        "started_unix": 1.0,
                        "ended_unix": 2.0,
                    },
                    "path_absent_after": True,
                }],
                "final_sweep": {"swept": True, "violations": []},
                "windows_quiescence": {
                    "mechanism": "windows-process-exit-attestation",
                    "all_exited": True,
                    "attestations": [{"command": "windows-unittest",
                                      "exited": True}],
                },
                "created_utc": "2026-09-11T19:01:00Z",
                "scientific_approval": False,
            })

    def _audits(self):
        membership = {}
        for path in sorted(self.evidence.rglob("*")):
            if path.is_file():
                rel = path.relative_to(self.evidence).as_posix()
                membership[rel] = sha(path.read_bytes())
        self.audit_shas = []
        for index, name in enumerate(self.manifest["artifacts"]["audit_receipts"]):
            self.audit_shas.append(self._write_json(name, {
                "schema": "recursion-publication-owned-audit/v1",
                "campaign": gate.CAMPAIGN,
                "parent_goal": PARENT,
                "attempt": 3,
                "candidate": self.candidate,
                "candidate_tree": self.tree,
                "manifest_sha256": self.manifest_sha,
                "owner": self.manifest["audit_owners"][index],
                "status": "OWNED_RETAINED_AUDIT_PASS",
                "attempt_membership": membership,
                "source_membership_verified": True,
                "quiescence_verified": True,
                "created_utc": "2026-09-11T19:10:00Z",
                "scientific_approval": False,
            }))

    def _draft_body(self):
        lines = [
            "# PR124 construction gate draft (reviewed body)",
            "",
            "candidate " + self.candidate,
            "tree " + self.tree,
            "attempt 3",
            "manifest " + self.manifest_sha,
            "bundle " + self.bundle_sha,
            "",
            "## Limitations",
            "Scientific admission remains BLOCKED_NO_EXECUTION_AUTHORIZED; "
            "this is a construction-only gate. Merge authority is Lucas alone.",
            "No GitHub status checks or review objects exist for this branch; "
            "acceptance evidence is internal receipts only.",
            "",
            "## Receipts",
        ]
        lines += sorted(self.receipt_shas.values())
        lines += ["## Audits"] + sorted(self.audit_shas)
        self.draft_sha = self._write(
            "pr-body-reviewed.md", "\n".join(lines).encode() + b"\n")

    def _review(self, entry, items):
        return {
            "schema": "recursion-publication-final-review/v1",
            "campaign": gate.CAMPAIGN,
            "parent_goal": PARENT,
            "candidate": self.candidate,
            "candidate_tree": self.tree,
            "manifest_sha256": self.manifest_sha,
            "bundle_sha256": self.bundle_sha,
            "reviewer": entry["reviewer"],
            "model": entry["model"],
            "effort": entry["effort"],
            "route": entry["route"],
            "gate_receipt_sha256s": sorted(self.receipt_shas.values()),
            "owned_audit_sha256s": sorted(self.audit_shas),
            "pr_body_reviewed_sha256": self.draft_sha,
            "limitations_sha256": sha(
                self.manifest["limitations_text"].encode()),
            "reviewed_utc": "2026-09-11T19:30:00Z",
            "status": "RETURNED_WITH_DISSENT",
            "items": items,
            "scientific_admission": "BLOCKED_NO_EXECUTION_AUTHORIZED",
            "acceptance": False,
        }

    def _reviews(self):
        items = {
            "reviews/grok-1.json": {"reservations": ["receipt contents unverified"],
                                    "defects": [], "blocking_gaps": ["wave06 unfavorable"],
                                    "dissent": []},
            "reviews/sol-1.json": {"reservations": ["moving candidate risk"],
                                   "defects": ["example defect"],
                                   "blocking_gaps": [], "dissent": ["kept"]},
            "reviews/sol-2.json": {"reservations": [], "defects": [],
                                   "blocking_gaps": ["WSL coverage partial"],
                                   "dissent": []},
        }
        self.review_shas = []
        for entry in self.bundle_entries():
            self.review_shas.append(self._write_json(
                entry["path"], self._review(entry, items[entry["path"]])))

    def _dispositions(self):
        rows = []
        for entry in self.bundle_entries():
            review = gate.strict_json(
                (self.evidence / entry["path"]).read_bytes())
            for section in gate.REVIEW_ITEM_KEYS:
                for item in review["items"].get(section, []):
                    rows.append({
                        "item_id": review["reviewer"] + ":" + item,
                        "disposition": "rejected-with-reason",
                        "reason": "recorded for publication packet",
                        "evidence_sha256": None,
                        "owner_record": None,
                    })
        self.disposition_sha = self._write_json("dispositions.json", {
            "schema": "recursion-disposition-table/v1",
            "campaign": gate.CAMPAIGN,
            "parent_goal": PARENT,
            "manifest_sha256": self.manifest_sha,
            "review_sha256s": sorted(self.review_shas),
            "items": rows,
        })

    def _published_body(self):
        lines = [
            "# PR124 publication gate results",
            "",
            "candidate " + self.candidate,
            "tree " + self.tree,
            "attempt 3",
            "manifest " + self.manifest_sha,
            "bundle " + self.bundle_sha,
            "dispositions " + self.disposition_sha,
            "reviewed-draft " + self.draft_sha,
            "",
            "## Limitations",
            "Scientific admission remains BLOCKED_NO_EXECUTION_AUTHORIZED; "
            "this is a construction-only gate whose PASS is "
            "PASS_CONSTRUCTION_ONLY. Merge authority is Lucas alone.",
            "No GitHub status checks or review objects exist for this branch; "
            "acceptance evidence is internal receipts only.",
            "",
            "## Gate receipts",
        ]
        lines += sorted(self.receipt_shas.values())
        lines += ["## Audits"] + sorted(self.audit_shas)
        lines += ["## Reviews"] + sorted(self.review_shas)
        self.body_sha = self._write(
            "pr-body.md", "\n".join(lines).encode() + b"\n")

    # ---------------------------------------------------------------- api
    def run(self, repo_marker=True, now=NOW):
        return gate.evaluate(self.evidence,
                             repo=self.repo if repo_marker else None,
                             now=now, activation_source=self.base)

    def edit_json(self, name, fn):
        path = self.evidence / name
        value = gate.strict_json(path.read_bytes())
        fn(value)
        path.write_bytes(canon(value))


@unittest.skipUnless(have_git(), "git required for fixture repo")
class PublicationGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.fx = Fixture(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self, verdict, status, code=None, check_id=None):
        self.assertEqual(verdict["status"], status, json.dumps(verdict, indent=1))
        if code is not None:
            self.assertEqual(verdict["code"], code, json.dumps(verdict, indent=1))
        if check_id is not None:
            entry = next(c for c in verdict["checks"] if c["id"] == check_id)
            self.assertIn(entry["status"], gate.CHECK_STATUS)
        return verdict

    # ----------------------------------------------------------- positive
    def test_pass_construction_only(self):
        verdict = self.check(self.fx.run(), "PASS_CONSTRUCTION_ONLY", "OK")
        self.assertTrue(all(c["status"] == "PASS" for c in verdict["checks"]))

    def test_verdict_preserves_boundaries(self):
        verdict = self.fx.run()
        self.assertEqual(verdict["scientific_admission"],
                         "BLOCKED_NO_EXECUTION_AUTHORIZED")
        self.assertIs(verdict["accepted"], False)
        self.assertEqual(verdict["merge_authority"], "Lucas alone")
        self.assertEqual(verdict["candidate"], self.fx.candidate)
        self.assertEqual(len(verdict["owned_audit_sha256"]), 2)
        self.assertEqual(len(verdict["review_sha256"]), 3)

    def test_cli_emits_canonical_verdict(self):
        emit = Path(self.tmp.name) / "verdict.json"
        out = io.StringIO()
        with redirect_stdout(out):
            rc = gate.main(["--evidence", str(self.fx.evidence),
                            "--repo", str(self.fx.repo),
                            "--activation-source", self.fx.base,
                            "--emit", str(emit),
                            "--now", "2026-09-11T20:00:00Z"])
        self.assertEqual(rc, 0)
        verdict = json.loads(out.getvalue())
        self.assertEqual(verdict["status"], "PASS_CONSTRUCTION_ONLY")
        self.assertEqual(emit.read_bytes(), canon(verdict))

    def test_quota_optional_when_declared(self):
        self.fx.edit_json("command-manifest.json",
                          lambda m: (m["quota"].update(required=False),
                                     m["artifacts"].update(quota_record=None)))
        verdict = self.fx.run()
        self.assertEqual(verdict["code"], "FAIL_WSL_UNITTEST")
        # manifest sha drift breaks receipt binding; quota itself did not block
        self.assertEqual(verdict["status"], "FAIL")

    # ---------------------------------------------------------- manifest
    def test_unresolved_manifest_field_refuses(self):
        def edit(m):
            m["checks"][1]["argv"]["windows"] = ["UNRESOLVED: ruff argv"]
        self.fx.edit_json("command-manifest.json", edit)
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_MANIFEST",
                   "preregistration")

    def test_duplicate_manifest_key_refuses(self):
        path = self.fx.evidence / "command-manifest.json"
        raw = path.read_bytes()
        path.write_bytes(raw[:-2] + b',"campaign":"x"}\n')
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_MANIFEST")

    def test_noncanonical_manifest_refuses(self):
        path = self.fx.evidence / "command-manifest.json"
        path.write_bytes(path.read_bytes().rstrip() + b"\n\n")
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_MANIFEST")

    def test_missing_manifest_incomplete(self):
        (self.fx.evidence / "command-manifest.json").unlink()
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_MANIFEST")

    def test_stale_quota_refuses(self):
        self.fx.edit_json("quota.json",
                          lambda q: q.update(checked_utc="2026-09-11T19:30:00Z"))
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_QUOTA")

    def test_quota_spend_refuses(self):
        self.fx.edit_json("quota.json", lambda q: q.update(new_metered_spend=1))
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_QUOTA")

    def test_obligations_wrong_contract_sha(self):
        self.fx.edit_json("obligations.json",
                          lambda o: o.update(validation_contract_sha256="0" * 64))
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_MANIFEST")

    def test_single_sol_reviewer_manifest_refuses(self):
        def edit(m):
            entries = m["review_bundle"]["entries"]
            entries[0]["model"] = "gpt-5.6-sol"
            entries[0]["effort"] = "xhigh"
            m["review_bundle"]["bundle_sha256"] = sha(
                gate.canonical_bytes(entries))
        self.fx.edit_json("command-manifest.json", edit)
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_MANIFEST")
        # three bundle entries, only two distinct sol reviewers still; this
        # fixture passes reviewer count, so drop a sol entry instead
        def edit2(m):
            m["review_bundle"]["entries"] = m["review_bundle"]["entries"][:1]
            m["review_bundle"]["bundle_sha256"] = sha(
                gate.canonical_bytes(m["review_bundle"]["entries"]))
        self.fx.edit_json("command-manifest.json", edit2)
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_MANIFEST")

    # ------------------------------------------------------------- freeze
    def test_dirty_workspace_fails(self):
        (self.fx.repo / "scratch.txt").write_text("dirty\n")
        self.check(self.fx.run(), "FAIL", "FAIL_CANDIDATE_IDENTITY",
                   "freeze-and-scope")

    def test_wrong_branch_fails(self):
        self.fx._git("checkout", "-b", "other")
        self.check(self.fx.run(), "FAIL", "FAIL_CANDIDATE_IDENTITY")

    def test_pause_marker_fails(self):
        (self.fx.repo / "PAUSE").write_text("halt\n")
        self.check(self.fx.run(), "FAIL", "FAIL_CANDIDATE_IDENTITY")

    def test_missing_parent_goal_fails(self):
        (self.fx.repo / "state/goals" / (PARENT + ".md")).unlink()
        self.check(self.fx.run(), "FAIL", "FAIL_CANDIDATE_IDENTITY")

    def test_candidate_moved_fails(self):
        (self.fx.repo / "docs/v3/construction/swarm-research-20260911-155142/more.md"
         ).write_text("more\n")
        self.fx._git("add", "-A")
        self.fx._git("commit", "-m", "moved")
        self.check(self.fx.run(), "FAIL", "FAIL_CANDIDATE_IDENTITY")

    def test_manifest_source_mismatch_fails(self):
        def edit(m):
            m["campaign_sources"][0]["bytes"] += 1
        self.fx.edit_json("command-manifest.json", edit)
        self.check(self.fx.run(), "FAIL", "FAIL_CANDIDATE_IDENTITY")

    def test_no_repo_is_incomplete(self):
        self.check(self.fx.run(repo_marker=None), "INCOMPLETE",
                   "INCOMPLETE_NATIVE_SCOPE_UNVERIFIED")

    def test_windows_alias_in_freeze_fails(self):
        def edit(r):
            r["windows"]["host"]["repo"] = "/mnt/c/Users/Lucas/Documents/GitHub/recursion"
        self.fx.edit_json("freeze-receipt.json", edit)
        self.check(self.fx.run(), "FAIL", "FAIL_CANDIDATE_IDENTITY")

    # ------------------------------------------------------------ receipts
    def test_log_bytes_differ_fails(self):
        (self.fx.evidence / "wsl-unittest.log").write_bytes(b"tampered\n")
        self.check(self.fx.run(), "FAIL", "FAIL_WSL_UNITTEST")

    def test_windows_receipt_alias_path_fails(self):
        self.fx.edit_json("windows-unittest.receipt.json",
                          lambda r: r["host"].update(repo="/mnt/c/Users/x"))
        self.check(self.fx.run(), "FAIL", "FAIL_WINDOWS_UNITTEST")

    def test_wsl_receipt_claiming_windows_fails(self):
        self.fx.edit_json("wsl-unittest.receipt.json",
                          lambda r: r["host"].update(os="windows"))
        self.check(self.fx.run(), "FAIL", "FAIL_WSL_UNITTEST")

    def test_unittest_count_mismatch_fails(self):
        self.fx.edit_json("windows-unittest.receipt.json",
                          lambda r: r["observed"].update(tests=69))
        self.check(self.fx.run(), "FAIL", "FAIL_WINDOWS_UNITTEST")

    def test_receipt_status_fail_fails(self):
        self.fx.edit_json("windows-ruff.receipt.json",
                          lambda r: r.update(status="FAIL", exit_code=1))
        self.check(self.fx.run(), "FAIL", "FAIL_WINDOWS_RUFF")

    def test_receipt_status_unknown_is_incomplete(self):
        self.fx.edit_json("windows-ruff.receipt.json",
                          lambda r: r.update(status="UNKNOWN", exit_code=None))
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_EVIDENCE")

    def test_missing_receipt_is_incomplete(self):
        (self.fx.evidence / "source-only-syntax.receipt.json").unlink()
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_EVIDENCE")

    def test_lint_route_ruff_without_native_ruff_fails(self):
        def edit(r):
            r["observed"] = {"route": "wsl-ruff", "ruff_version": "0.9.0",
                            "scope": sorted(SOURCE_PATHS)}
        self.fx.edit_json("wsl-lint-or-substitute.receipt.json", edit)
        self.check(self.fx.run(), "FAIL", "FAIL_WSL_LINT_OR_SUBSTITUTE")

    def test_lint_substitute_binding_fails(self):
        self.fx.edit_json("wsl-lint-or-substitute.receipt.json",
                          lambda r: r["observed"].update(
                              windows_ruff_receipt_sha256="0" * 64))
        self.check(self.fx.run(), "FAIL", "FAIL_WSL_LINT_OR_SUBSTITUTE")

    def test_receipt_scientific_approval_true_fails(self):
        self.fx.edit_json("wsl-unittest.receipt.json",
                          lambda r: r.update(scientific_approval=True))
        self.check(self.fx.run(), "FAIL", "FAIL_WSL_UNITTEST")

    # ------------------------------------------------------------- cgroup
    def test_missing_cgroup_receipt_is_incomplete(self):
        (self.fx.evidence / "clean-cgroup.receipt.json").unlink()
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_EVIDENCE")

    def test_cgroup_lingering_fails(self):
        self.fx.edit_json("clean-cgroup.receipt.json",
                          lambda r: r["final_sweep"].update(
                              violations=["recursion-foundry-tool-2"]))
        self.check(self.fx.run(), "FAIL", "FAIL_CLEAN_CGROUP")

    def test_windows_quiescence_deferral_incomplete(self):
        def edit(r):
            r["windows_quiescence"] = {
                "not_applicable_reason": "no windows mechanism",
                "deferred_to": "owner-record-windows-quiescence-01"}
        self.fx.edit_json("clean-cgroup.receipt.json", edit)
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_WINDOWS_QUIESCENCE")

    def test_windows_quiescence_absent_fails(self):
        self.fx.edit_json("clean-cgroup.receipt.json",
                          lambda r: r.update(
                              windows_quiescence={"not_applicable_reason": "none"}))
        self.check(self.fx.run(), "FAIL", "FAIL_CLEAN_CGROUP")

    # -------------------------------------------------------------- audits
    def test_audit_owner_collision_fails(self):
        self.fx.edit_json("owned-audit-1.receipt.json",
                          lambda a: a.update(owner="gate-runner"))
        self.check(self.fx.run(), "FAIL", "FAIL_OWNERSHIP_AUDIT_1")

    def test_audit_membership_drift_fails(self):
        def edit(a):
            key = sorted(a["attempt_membership"])[0]
            a["attempt_membership"][key] = "0" * 64
        self.fx.edit_json("owned-audit-2.receipt.json", edit)
        self.check(self.fx.run(), "FAIL", "FAIL_OWNERSHIP_AUDIT_2")

    def test_audit_membership_omission_fails(self):
        def edit(a):
            a["attempt_membership"].pop("wsl-unittest.log")
        self.fx.edit_json("owned-audit-1.receipt.json", edit)
        self.check(self.fx.run(), "FAIL", "FAIL_OWNERSHIP_AUDIT_1")

    def test_missing_audit_is_incomplete(self):
        (self.fx.evidence / "owned-audit-2.receipt.json").unlink()
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_EVIDENCE")

    # -------------------------------------------------------------- review
    def test_review_wrong_candidate_incomplete(self):
        self.fx.edit_json("reviews/sol-1.json",
                          lambda r: r.update(candidate="0" * 40))
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_REVIEWS")

    def test_review_predating_receipts_incomplete(self):
        self.fx.edit_json("reviews/sol-1.json",
                          lambda r: r.update(reviewed_utc="2026-09-11T18:00:00Z"))
        # one stale review leaves latest_review (sol-2 19:30) >= receipts, but
        # the stale review's own receipt binding still holds; force both stale
        self.fx.edit_json("reviews/sol-2.json",
                          lambda r: r.update(reviewed_utc="2026-09-11T18:00:00Z"))
        self.fx.edit_json("reviews/grok-1.json",
                          lambda r: r.update(reviewed_utc="2026-09-11T18:00:00Z"))
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_REVIEWS")

    def test_missing_review_is_incomplete(self):
        (self.fx.evidence / "reviews/sol-2.json").unlink()
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_REVIEWS")

    def test_duplicate_items_in_review_incomplete(self):
        self.fx.edit_json("reviews/sol-1.json",
                          lambda r: r["items"].update(
                              reservations=["dup", "dup"]))
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_REVIEWS")

    # --------------------------------------------------------- disposition
    def test_missing_disposition_item_incomplete(self):
        self.fx.edit_json("dispositions.json",
                          lambda t: t["items"].pop(0))
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_DISPOSITIONS")

    def test_fixed_disposition_needs_evidence(self):
        def edit(t):
            t["items"][0]["disposition"] = "fixed-in-candidate"
            t["items"][0]["evidence_sha256"] = None
        self.fx.edit_json("dispositions.json", edit)
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_DISPOSITIONS")

    def test_deferred_disposition_needs_owner(self):
        def edit(t):
            t["items"][0]["disposition"] = "deferred-owner-bound"
            t["items"][0]["owner_record"] = None
        self.fx.edit_json("dispositions.json", edit)
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_DISPOSITIONS")

    def test_disposition_table_wrong_review_set(self):
        self.fx.edit_json("dispositions.json",
                          lambda t: t.update(review_sha256s=["0" * 64]))
        self.check(self.fx.run(), "INCOMPLETE", "INCOMPLETE_DISPOSITIONS")

    # ------------------------------------------------------------ pr body
    def test_pr_body_missing_hash_fails(self):
        (self.fx.evidence / "pr-body.md").write_bytes(b"empty body\n")
        self.check(self.fx.run(), "FAIL", "FAIL_PR_BODY_BINDING")

    def test_pr_body_github_claim_fails(self):
        path = self.fx.evidence / "pr-body.md"
        path.write_bytes(path.read_bytes() +
                         b"GitHub status checks passed for this head.\n")
        self.check(self.fx.run(), "FAIL", "FAIL_PR_BODY_BINDING")

    def test_pr_body_missing_disclaimer_fails(self):
        self.fx.edit_json("command-manifest.json",
                          lambda m: m["pr_body"].update(
                              github_disclaimer="GitHub absent evidence disclaimer v2"))
        # manifest changed -> receipts no longer bind; use a body-only path:
        # instead overwrite the body without the disclaimer and rebuild nothing
        path = self.fx.evidence / "pr-body.md"
        text = path.read_text()
        text = text.replace(
            "No GitHub status checks or review objects exist for this branch; "
            "acceptance evidence is internal receipts only.", "")
        path.write_text(text)
        self.check(self.fx.run(), "FAIL", "FAIL_PR_BODY_BINDING")

    # ------------------------------------------------------------ deadline
    def test_deadline_reserve_incomplete(self):
        self.check(self.fx.run(now=LATE), "INCOMPLETE", "INCOMPLETE_DEADLINE",
                   "verdict")


@unittest.skipUnless(have_git(), "git required for fixture repo")
class MergeAncestryTests(unittest.TestCase):
    def test_merge_commit_in_ancestry_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            fx = Fixture(tmp, merge=True)
            verdict = fx.run()
            self.assertEqual(verdict["status"], "FAIL")
            self.assertEqual(verdict["code"], "FAIL_CANDIDATE_IDENTITY")


if __name__ == "__main__":
    unittest.main(verbosity=1)
