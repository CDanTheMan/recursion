#!/usr/bin/env python3
"""Adversarial controls for the independent Phase 5 rejection findings."""
from __future__ import annotations

from contextlib import contextmanager
import json
import hashlib
import copy
import importlib.util
import os
import secrets
import stat
import subprocess
import sys
import tempfile
import shutil
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import assignment
try:
    import fcntl  # type: ignore  # noqa: F401
except ImportError:
    sys.modules["fcntl"] = types.SimpleNamespace(LOCK_EX=2, LOCK_NB=4, flock=lambda *_args: None)
reconcile_spec = importlib.util.spec_from_file_location("phase5_reconcile", ROOT / "scripts/project-reconcile.py")
assert reconcile_spec is not None and reconcile_spec.loader is not None
reconcile = importlib.util.module_from_spec(reconcile_spec)
reconcile_spec.loader.exec_module(reconcile)
spec = importlib.util.spec_from_file_location("resolve_engine", ROOT / "scripts/resolve-engine.py")
resolve_engine = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(resolve_engine)
layout_spec = importlib.util.spec_from_file_location("runtime_layout", ROOT / "scripts/runtime-layout.py")
runtime_layout = importlib.util.module_from_spec(layout_spec)
assert layout_spec.loader is not None
layout_spec.loader.exec_module(runtime_layout)


@contextmanager
def test_directory(label: str):
    configured = os.environ.get("PHASE5_TEST_ROOT", "").strip()
    if configured:
        root = Path(configured)
        root.mkdir(parents=True, exist_ok=True)
        path = root / f"{label}-{secrets.token_hex(8)}"
        path.mkdir()
        try:
            yield path
        finally:
            shutil.rmtree(path, ignore_errors=True)
    else:
        with tempfile.TemporaryDirectory() as raw:
            yield Path(raw)


def check(ok: bool, label: str) -> None:
    if not ok:
        raise AssertionError(label)
    print(f"ok - {label}")


def valid_assignment(repo: Path, controller: Path) -> dict:
    source_sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    gate_bytes = subprocess.check_output(["git", "-C", str(repo), "show", "HEAD:scripts/gate.sh"])
    gate_contract = {"acceptance": "bash scripts/gate.sh",
                     "acceptance_sha256": hashlib.sha256(b"bash scripts/gate.sh").hexdigest(),
                     "gate_files": {"scripts/gate.sh": hashlib.sha256(gate_bytes).hexdigest()},
                     "controller_gate_files": {}}
    gate_digest = hashlib.sha256(assignment.canonical_bytes(gate_contract)).hexdigest()
    role = {"engine": "cursor", "provider": "cursor", "model": "cursor-primary",
            "network_policy": "provider-only", "network_profile": "cursor",
            "argv": ["{{EXE}}", "-p", "{{PROMPT}}", "--output-format", "text", "--force",
                     "--model", "{{MODEL}}"],
            "network_endpoints": ["api.cursor.com", "api2.cursor.sh"]}
    controller_sha = subprocess.check_output(["git", "-C", str(controller), "rev-parse", "HEAD"], text=True).strip()
    return {"task_id": "task-1", "project_id": "project-1", "source_repository": str(repo),
            "source_branch": "main", "source_sha": source_sha,
            "controller_repository": str(controller), "controller_sha": controller_sha,
            "seed_manifest_digest": "", "engine": "cursor", "provider": "cursor",
            "capacity_pool": "cursor-ultra-grok-bot", "model": "cursor-primary",
            "host": "gs-recursion", "sandbox_profile": "strict-linux", "network_policy": "provider-only",
            "network_profile": "cursor", "network_endpoints": ["api.cursor.com", "api2.cursor.sh"],
            "argv": list(role["argv"]),
            "allowed_paths": ["scripts"], "gate_digest": gate_digest, "gate_contract": gate_contract,
            "role_assignments": {"implementer": role, "verifier": dict(role)},
            "publication_policy": "verified-integration-only"}


def main() -> int:
    with test_directory("hardening") as tmp:
        source = tmp / "source"; (source / "scripts").mkdir(parents=True)
        # Keep the materialized bytes identical to the committed blob on Windows, where
        # write_text() would otherwise create CRLF while Git's clean filter stores LF.
        (source / "scripts/gate.sh").write_bytes(b"#!/bin/sh\ntest -s result.txt\n")
        subprocess.run(["git", "init", "-q", "-b", "main", str(source)], check=True)
        subprocess.run(["git", "-C", str(source), "config", "core.autocrlf", "false"], check=True)
        subprocess.run(["git", "-C", str(source), "add", "."], check=True)
        subprocess.run(["git", "-C", str(source), "-c", "user.name=t", "-c", "user.email=t@t",
                        "commit", "-qm", "source"], check=True)
        controller = tmp / "controller"; (controller / "scripts" / "engines").mkdir(parents=True)
        (controller / "scripts/validate-gate.py").write_bytes(
            (ROOT / "scripts/validate-gate.py").read_bytes())
        shutil.copy2(ROOT / "scripts" / "phase5_safety.py", controller / "scripts" / "phase5_safety.py")
        shutil.copy2(ROOT / "scripts" / "resolve-engine.py", controller / "scripts" / "resolve-engine.py")
        missing_module = tmp / "missing-phase5-module"; (missing_module / "scripts").mkdir(parents=True)
        shutil.copy2(ROOT / "scripts" / "validate-gate.py", missing_module / "scripts" / "validate-gate.py")
        missing_result = subprocess.run(
            [sys.executable, str(missing_module / "scripts/validate-gate.py"),
             "--acceptance", "test -s result.txt", "--allowed-paths", "scripts"],
            capture_output=True, text=True,
        )
        check(
            missing_result.returncode == 95
            and "first-party import failed" in missing_result.stderr
            and "phase5_safety" in missing_result.stderr
            and str(missing_module / "scripts") in missing_result.stderr
            and "Traceback" not in missing_result.stderr,
            "missing first-party module is a typed, path-named refusal",
        )
        for name in ("provider-egress-profiles.json", "capacity-pools.json"):
            shutil.copy2(ROOT / "scripts" / name, controller / "scripts" / name)
        shutil.copy2(ROOT / "scripts" / "engines" / "cursor.json",
                     controller / "scripts" / "engines" / "cursor.json")
        subprocess.run(["git", "init", "-q", "-b", "main", str(controller)], check=True)
        subprocess.run(["git", "-C", str(controller), "config", "core.autocrlf", "false"], check=True)
        subprocess.run(["git", "-C", str(controller), "add", "."], check=True)
        subprocess.run(["git", "-C", str(controller), "-c", "user.name=t", "-c", "user.email=t@t",
                        "commit", "-qm", "controller"], check=True)
        (controller / "state").mkdir()
        key = controller / "state/.worker-evidence.key"
        key.write_bytes(os.urandom(32)); key.chmod(0o600)
        os.environ["RECURSION_ROOT"] = str(controller)
        executable = source / "cursor-agent"; executable.write_text("#!/bin/sh\n", encoding="utf-8")
        executable.chmod(0o755)
        value = valid_assignment(source, controller)
        first = assignment.digest(value)
        tampered = dict(value); tampered["host"] = "cursor-cloud"
        check(assignment.digest(tampered) != first, "assignment digest changes when host is tampered")
        bad_pool = dict(value); bad_pool["capacity_pool"] = "unassigned"
        try: assignment.validate_assignment(bad_pool)
        except assignment.AssignmentError: pass
        else: raise AssertionError("arbitrary pool accepted")
        fake = dict(value)
        fake["gate_contract"] = {"acceptance": "true",
            "acceptance_sha256": hashlib.sha256(b"true").hexdigest(),
            "gate_files": {}, "controller_gate_files": {}}
        fake["gate_digest"] = hashlib.sha256(assignment.canonical_bytes(fake["gate_contract"])).hexdigest()
        try: assignment.validate_assignment(fake)
        except assignment.AssignmentError: pass
        else: raise AssertionError("fabricated true/empty gate contract accepted")
        bad_role = dict(value); bad_role["role_assignments"] = {"implementer": value["role_assignments"]["implementer"],
            "verifier": {"engine":"gemini", "provider":"google-gemini", "model":"review",
                         "network_profile":"gemini", "network_endpoints":["generativelanguage.googleapis.com"]}}
        try: assignment.validate_assignment(bad_role)
        except assignment.AssignmentError: pass
        else: raise AssertionError("role provider outside pool accepted")
        for label, mutation in (
            ("nonexistent source commit", {"source_sha": "f" * 40}),
            ("wrong provider profile", {"network_profile": "gemini"}),
            ("wrong profile endpoints", {"network_endpoints": ["example.test"]}),
            ("wrong gate digest", {"gate_digest": "0" * 64}),
        ):
            bad = dict(value); bad.update(mutation)
            try: assignment.validate_assignment(bad)
            except assignment.AssignmentError: pass
            else: raise AssertionError(f"{label} accepted")

        wrong_branch = dict(value); wrong_branch["source_branch"] = "develop"
        try: assignment.validate_assignment(wrong_branch)
        except assignment.AssignmentError: pass
        else: raise AssertionError("syntactically valid wrong source branch accepted")

        alternate = tmp / "alternate-controller"
        subprocess.run(["git", "clone", "-q", str(controller), str(alternate)], check=True)
        alternate_value = dict(value); alternate_value["controller_repository"] = str(alternate)
        try: assignment.validate_assignment(alternate_value)
        except assignment.AssignmentError: pass
        else: raise AssertionError("alternate canonical controller root accepted")
        for relative, label in (
            ("scripts/provider-egress-profiles.json", "provider profile"),
            ("scripts/capacity-pools.json", "capacity pool policy"),
            ("scripts/engines/cursor.json", "engine manifest"),
        ):
            tampered_policy = controller / relative
            original_policy = tampered_policy.read_bytes()
            tampered_policy.write_bytes(original_policy + b"\n")
            try:
                assignment.validate_assignment(value)
            except assignment.AssignmentError: pass
            else: raise AssertionError(f"tampered controller {label} accepted")
            tampered_policy.write_bytes(original_policy)

        for field, bad in (("signal", "HUP"), ("overlap", [0])):
            execution = {"structured_output": False, "output_format":"text",
                         "cancellation":{"signal":"TERM", "grace_s":5},
                         "exit_codes":{"success":[0], "auth":[1], "runtime":[126], "egress":[60]}}
            if field == "signal": execution["cancellation"]["signal"] = bad
            else: execution["exit_codes"]["auth"] = bad
            try: resolve_engine.validate_execution(execution)
            except resolve_engine.ManifestError: pass
            else: raise AssertionError(f"invalid execution {field} accepted")
        check("api.anthropic.com" not in (ROOT / "scripts/provider-network.sh").read_text(),
              "provider network helper has no Anthropic-only authority")
        worker = (ROOT / "scripts/worker-sandbox.sh").read_text()
        proxy_start = worker.find('if [ "$NETWORK_POLICY" = provider-only ]; then\n  # Every provider')
        check(proxy_start >= 0 and worker.find("--setenv HTTPS_PROXY", proxy_start) >= 0,
              "proxy injection is not Claude-only")
        check("quarantine=termination-unconfirmed" in worker and "CLEANUP_DONE" in worker,
              "sandbox cleanup quarantines unconfirmed termination")
        work = (ROOT / "scripts/work.sh").read_text()
        check("quarantine: termination was not confirmed" in work and 'arc" = 96' in work,
              "controller retains worktree when process-group cancellation is unconfirmed")
        check(
            'if [ "$STRICT_PHASE5" = 1 ]; then' in work
            and "existing worktree is retained as a quarantine" in work
            and "removing stale legacy worktree before fresh dispatch" in work
            and 'git -C "$REPO_DIR" worktree remove --force "$wt"' in work,
            "strict Phase 5 quarantines existing worktrees while legacy reruns retain forced removal",
        )
        check('[ "$STRICT_PHASE5" != 1 ] || cmd+=(--execution-evidence' in work
              and 'args+=(--execution-evidence "$execution_evidence")' in work,
              "strict worker launch and finish always carry execution evidence")
        arc96 = work.split('if [ "$arc" = "96" ]; then', 1)[1].split('case "$arc" in', 1)[0]
        check("complete_terminal_escalation" not in arc96 and "quarantine_unconfirmed" in arc96,
              "arc=96 records escalation without terminalizing or clearing the lease")
        taskctl = (ROOT / "scripts/taskctl.sh").read_text()
        check("termination-unconfirmed.json" in taskctl and "quarantine-release" in taskctl
              and 'kill -0 -- "-$PGID"' in taskctl,
              "quarantine reuse is blocked until explicit dead-process recovery")

        destination = tmp / "dest"
        runtime_layout._copy_tree(source, destination, "cursor-agent")
        check((destination / "cursor-agent").is_file(), "executable runtime entrypoint stages")
        if os.name != "nt":
            bad = tmp / "bad"; bad.mkdir(); (bad / "cursor-agent").write_text("not executable", encoding="utf-8")
            try: runtime_layout._copy_tree(bad, tmp / "bad-dest", "cursor-agent")
            except runtime_layout.LayoutError: pass
            else: raise AssertionError("non-executable runtime entrypoint staged")
        if hasattr(os, "symlink"):
            outside = tmp / "outside"; outside.mkdir()
            try:
                linked = tmp / "linked"; linked.symlink_to(outside, target_is_directory=True)
            except OSError:
                print("ok - symlink source control skipped (symlink privilege unavailable)")
            else:
                try: runtime_layout._safe_source(linked)
                except runtime_layout.LayoutError: pass
                else: raise AssertionError("symlinked runtime source accepted")

        # Git on Windows may materialize a mode-120000 blob as a regular file when
        # core.symlinks=false.  The staging decision must follow the index, not lstat().
        git_source = tmp / "git-runtime"; git_source.mkdir()
        subprocess.run(["git", "init", "-q", str(git_source)], check=True)
        materialized = git_source / "cursor-agent"
        materialized.write_text("outside-target\n", encoding="utf-8")
        blob = subprocess.check_output(
            ["git", "-C", str(git_source), "hash-object", "-w", "--stdin"],
            input=b"outside-target\n",
        ).decode().strip()
        subprocess.run(["git", "-C", str(git_source), "update-index", "--add",
                        f"--cacheinfo", f"120000,{blob},cursor-agent"], check=True)
        try:
            runtime_layout._copy_tree(git_source, tmp / "git-dest", "cursor-agent")
        except runtime_layout.LayoutError:
            pass
        else:
            raise AssertionError("Git mode-120000 materialized file accepted")
        for entrypoint in (r"..\outside", "foo/../outside", "./cursor-agent"):
            try:
                runtime_layout._copy_tree(source, tmp / ("bad-" + str(len(entrypoint))), entrypoint)
            except runtime_layout.LayoutError:
                pass
            else:
                raise AssertionError(f"unsafe entrypoint accepted: {entrypoint!r}")

        assignment_path = tmp / "assignment.json"
        assignment_path.write_text(json.dumps(value), encoding="utf-8")
        assigned, assigned_digest = assignment.load_assignment(assignment_path)
        check(assigned_digest == first, "assignment file digest is stable after serialization")
        evidence = tmp / "evidence.json"
        cmd = [sys.executable, str(ROOT / "scripts/worker-evidence.py"), "start",
               "--path", str(evidence), "--run-id", "run-1", "--task-id", "task-1",
               "--role", "implementer", "--model-alias", "cursor-primary", "--worktree", str(tmp),
               "--base-commit", "0"*40, "--pid", "1", "--process-group", "1",
               "--deadline-epoch", "2000000000", "--log", "run.log", "--network-policy", "provider-only",
               "--engine", "cursor", "--provider", "cursor", "--capacity-pool", "cursor-ultra-grok-bot",
               "--model", "cursor-primary", "--host", "gs-recursion", "--sandbox-profile", "strict-linux",
               "--assignment-digest", first, "--assignment-file", str(assignment_path)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        check(result.returncode == 0, "evidence start accepts independently recomputed assignment")
        recorded = json.loads(evidence.read_text(encoding="utf-8"))
        check(recorded["assignment_digest"] == first, "evidence records recomputed assignment digest")
        start_evidence = evidence.with_name(f".{evidence.name}.start")
        check(start_evidence.is_file(), "evidence records an independent durable start binding")
        downgraded = dict(recorded)
        for field in ("assignment_file", "assignment_digest", "assignment"):
            downgraded.pop(field, None)
        evidence.write_text(json.dumps(downgraded), encoding="utf-8")
        downgraded_finish = subprocess.run([
            sys.executable, str(ROOT / "scripts/worker-evidence.py"), "finish", str(evidence),
            "succeeded", "downgraded", "0",
        ], capture_output=True, text=True, env=os.environ.copy())
        after_downgrade = json.loads(evidence.read_text(encoding="utf-8"))
        check(downgraded_finish.returncode != 0
              and "execution evidence is required" in downgraded_finish.stderr
              and after_downgrade.get("status") == "running",
              "strict run cannot be downgraded by deleting mutable assignment fields")
        evidence.write_text(json.dumps(recorded), encoding="utf-8")
        mismatch = cmd.copy(); mismatch[mismatch.index("--assignment-digest") + 1] = "f" * 64
        check(subprocess.run(mismatch, capture_output=True).returncode != 0,
              "evidence rejects caller-supplied digest mismatch")
        wrong_gate = [sys.executable, str(ROOT / "scripts/worker-evidence.py"), "gate",
                      str(evidence), "0" * 40, "test -s different-result", "0", "gate.log"]
        check(subprocess.run(wrong_gate, capture_output=True).returncode != 0,
              "evidence recomputes and rejects a wrong gate contract")
        original_gate = (source / "scripts/gate.sh").read_bytes()
        (source / "scripts/gate.sh").write_text("#!/bin/sh\ntrue\n", encoding="utf-8")
        tampered_gate_finish = [sys.executable, str(ROOT / "scripts/worker-evidence.py"), "finish",
                                str(evidence), "failed", "tampered-gate", "1"]
        check(subprocess.run(tampered_gate_finish, capture_output=True).returncode != 0,
              "evidence consumption rejects a post-creation gate-file change")
        (source / "scripts/gate.sh").write_bytes(original_gate)
        original_validator = (controller / "scripts/validate-gate.py").read_bytes()
        (controller / "scripts/validate-gate.py").write_bytes(original_validator + b"\n# post-creation drift\n")
        tampered_controller_finish = [sys.executable, str(ROOT / "scripts/worker-evidence.py"), "finish",
                                      str(evidence), "failed", "tampered-controller", "1"]
        check(subprocess.run(tampered_controller_finish, capture_output=True).returncode != 0,
              "evidence consumption rejects a post-creation controller-file change")
        (controller / "scripts/validate-gate.py").write_bytes(original_validator)
        assignment_path.write_text(json.dumps({**value, "network_profile": "gemini"}), encoding="utf-8")
        tampered_finish = [sys.executable, str(ROOT / "scripts/worker-evidence.py"), "finish",
                           str(evidence), "failed", "tampered", "1"]
        check(subprocess.run(tampered_finish, capture_output=True).returncode != 0,
              "evidence consumption rejects assignment tampering")
        assignment_path.write_text(json.dumps(value), encoding="utf-8")

        execution_path = tmp / "execution.json"
        execution = {
            "engine": "cursor", "provider": "cursor", "profile": "cursor",
            "endpoints": ["api.cursor.com", "api2.cursor.sh"], "model": "cursor-primary",
            "argv": value["role_assignments"]["implementer"]["argv"],
            "assignment_digest": first, "assignment_identity": first,
            "status": "finished", "exit_code": 0,
            "network": {"policy": "provider-only", "profile": "cursor", "provider": "cursor",
                         "endpoints": ["api.cursor.com", "api2.cursor.sh"]},
        }
        execution_path.write_text(json.dumps(execution), encoding="utf-8")
        missing_execution = subprocess.run([
            sys.executable, str(ROOT / "scripts/worker-evidence.py"), "finish", str(evidence),
            "succeeded", "done", "0",
        ], capture_output=True, text=True, env=os.environ.copy())
        check(missing_execution.returncode != 0 and "execution evidence is required" in missing_execution.stderr,
              "strict finish refuses absent execution evidence")
        for field, bad in (
            ("engine", "gemini"), ("provider", "google-gemini"), ("profile", "gemini"),
            ("endpoints", ["generativelanguage.googleapis.com"]), ("model", "wrong-model"),
            ("argv", ["{{EXE}}", "--wrong"]), ("assignment_digest", "0" * 64),
            ("assignment_identity", "0" * 64),
        ):
            mutated = dict(execution); mutated[field] = bad
            execution_path.write_text(json.dumps(mutated), encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts/worker-evidence.py"), "finish", str(evidence),
                "succeeded", "done", "0", "--execution-evidence", str(execution_path),
            ], capture_output=True, text=True, env=os.environ.copy())
            check(result.returncode != 0 and "Traceback" not in result.stderr,
                  f"execution evidence mismatch is rejected deterministically: {field}")
        execution_path.write_text(json.dumps(execution), encoding="utf-8")
        valid_finish = subprocess.run([
            sys.executable, str(ROOT / "scripts/worker-evidence.py"), "finish", str(evidence),
            "succeeded", "done", "0", "--execution-evidence", str(execution_path),
        ], capture_output=True, text=True, env=os.environ.copy())
        check(valid_finish.returncode == 0, "matching execution evidence is accepted")

        claude = copy.deepcopy(value)
        claude["engine"] = "claude"
        claude["provider"] = "anthropic-claude-code"
        claude["capacity_pool"] = "claude-max"
        claude["network_profile"] = "anthropic"
        claude["network_endpoints"] = ["api.anthropic.com"]
        claude["argv"] = list(assignment.CLAUDE_ARGV) + ["--model", "{{MODEL}}"]
        for role_spec in claude["role_assignments"].values():
            role_spec.update(engine="claude", provider="anthropic-claude-code",
                              network_policy="provider-only", network_profile="anthropic",
                              network_endpoints=["api.anthropic.com"],
                              argv=list(claude["argv"]), model="cursor-primary")
        controller_sha = subprocess.check_output(["git", "-C", str(controller), "rev-parse", "HEAD"], text=True).strip()
        check(assignment._engine_binding("claude", str(controller), controller_sha)[4]
              == assignment.CLAUDE_ARGV,
              "builtin Claude binding exposes its exact hardcoded argv")
        try:
            assignment.validate_assignment(claude)
        except assignment.AssignmentError as exc:
            raise AssertionError(f"exact builtin Claude argv was rejected: {exc}")
        attacker_argv = copy.deepcopy(claude)
        attacker_argv["argv"] = ["ATTACKER"]
        try:
            assignment.validate_assignment(attacker_argv)
        except assignment.AssignmentError:
            pass
        else:
            raise AssertionError("builtin Claude accepted attacker-controlled argv")

        source_sha = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        task = {"id": "task-1", "candidate_commit": source_sha, "evidence_contract": "worker-result-v1"}
        implementer_run = {
            "id": "impl-run", "task_id": "task-1", "role": "implementer", "status": "succeeded",
            "exit_code": 0, "assignment_file": str(assignment_path.resolve()),
            "assignment_digest": first, "assignment": assigned, "commit_oid": source_sha,
            "machine_gate": {
                "commit_oid": source_sha, "acceptance": value["gate_contract"]["acceptance"],
                "gate_contract_digest": value["gate_digest"],
                "acceptance_sha256": value["gate_contract"]["acceptance_sha256"],
                "passed": True, "exit_code": 0,
            },
            "verification": {"verifier_run_id": "verify-run", "commit_oid": source_sha, "verdict": "pass"},
            "execution": dict(execution),
        }
        verifier_run = {
            "id": "verify-run", "task_id": "task-1", "role": "verifier", "status": "succeeded",
            "exit_code": 0, "assignment_digest": first, "commit_oid": source_sha,
            "verification": {
                "commit_oid": source_sha, "implementer_run_id": "impl-run", "verdict": "pass",
            },
            "execution": dict(execution),
        }
        runs = [implementer_run, verifier_run]
        valid_reconcile, reconcile_reason, _ = reconcile.task_evidence(
            controller, source, task, runs, require_local_review_ref=False,
        )
        check(valid_reconcile and reconcile_reason == "verified",
              "reconciliation verifies matching execution evidence")
        absent = dict(implementer_run)
        absent.pop("execution")
        absent_valid, _, _ = reconcile.task_evidence(
            controller, source, task, [absent, verifier_run], require_local_review_ref=False,
        )
        check(not absent_valid, "reconciliation refuses absent execution evidence")
        incoherent_run = dict(implementer_run)
        incoherent_execution = dict(execution)
        incoherent_execution["status"] = "started"
        incoherent_run["execution"] = incoherent_execution
        incoherent_valid, _, _ = reconcile.task_evidence(
            controller, source, task, [incoherent_run, verifier_run], require_local_review_ref=False,
        )
        check(not incoherent_valid, "reconciliation refuses execution evidence with incoherent run status")
        for field, bad in (
            ("engine", "gemini"), ("provider", "google-gemini"), ("profile", "gemini"),
            ("endpoints", ["generativelanguage.googleapis.com"]), ("model", "wrong-model"),
            ("argv", ["{{EXE}}", "--wrong"]), ("assignment_digest", "0" * 64),
            ("assignment_identity", "0" * 64),
        ):
            mutated_run = dict(implementer_run)
            mutated_execution = dict(execution)
            mutated_execution[field] = bad
            mutated_run["execution"] = mutated_execution
            mutated_valid, _, _ = reconcile.task_evidence(
                controller, source, task, [mutated_run, verifier_run], require_local_review_ref=False,
            )
            check(not mutated_valid, f"reconciliation rejects mismatched execution field: {field}")

    print("phase5-hardening.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
