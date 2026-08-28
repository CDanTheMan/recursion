#!/usr/bin/env python3
"""Adversarial controls for the independent Phase 5 rejection findings."""
from __future__ import annotations

import json
import hashlib
import importlib.util
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import assignment
spec = importlib.util.spec_from_file_location("resolve_engine", ROOT / "scripts/resolve-engine.py")
resolve_engine = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(resolve_engine)
layout_spec = importlib.util.spec_from_file_location("runtime_layout", ROOT / "scripts/runtime-layout.py")
runtime_layout = importlib.util.module_from_spec(layout_spec)
assert layout_spec.loader is not None
layout_spec.loader.exec_module(runtime_layout)


def check(ok: bool, label: str) -> None:
    if not ok:
        raise AssertionError(label)
    print(f"ok - {label}")


def valid_assignment(repo: Path) -> dict:
    source_sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    gate_contract = {"acceptance_sha256": hashlib.sha256(b"test -s result").hexdigest(),
                     "gate_files": {}, "controller_gate_files": {}}
    gate_digest = hashlib.sha256(assignment.canonical_bytes(gate_contract)).hexdigest()
    role = {"engine": "cursor", "provider": "cursor", "model": "cursor-primary",
            "network_profile": "cursor",
            "network_endpoints": ["api.cursor.com", "api2.cursor.sh"]}
    return {"task_id": "task-1", "project_id": "project-1", "source_repository": str(repo),
            "source_branch": "codex/v2-cursor-runtime", "source_sha": source_sha,
            "seed_manifest_digest": "", "engine": "cursor", "provider": "cursor",
            "capacity_pool": "cursor-ultra-grok-bot", "model": "cursor-primary",
            "host": "gs-recursion", "sandbox_profile": "strict-linux", "network_profile": "cursor",
            "network_endpoints": ["api.cursor.com", "api2.cursor.sh"],
            "allowed_paths": ["scripts"], "gate_digest": gate_digest, "gate_contract": gate_contract,
            "role_assignments": {"implementer": role, "verifier": dict(role)},
            "publication_policy": "verified-integration-only"}


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        source = tmp / "source"; source.mkdir()
        executable = source / "cursor-agent"; executable.write_text("#!/bin/sh\n", encoding="utf-8")
        executable.chmod(0o755)
        value = valid_assignment(ROOT)
        first = assignment.digest(value)
        tampered = dict(value); tampered["host"] = "cursor-cloud"
        check(assignment.digest(tampered) != first, "assignment digest changes when host is tampered")
        bad_pool = dict(value); bad_pool["capacity_pool"] = "unassigned"
        try: assignment.validate_assignment(bad_pool)
        except assignment.AssignmentError: pass
        else: raise AssertionError("arbitrary pool accepted")
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
        mismatch = cmd.copy(); mismatch[mismatch.index("--assignment-digest") + 1] = "f" * 64
        check(subprocess.run(mismatch, capture_output=True).returncode != 0,
              "evidence rejects caller-supplied digest mismatch")
        wrong_gate = [sys.executable, str(ROOT / "scripts/worker-evidence.py"), "gate",
                      str(evidence), "0" * 40, "test -s different-result", "0", "gate.log"]
        check(subprocess.run(wrong_gate, capture_output=True).returncode != 0,
              "evidence recomputes and rejects a wrong gate contract")
        assignment_path.write_text(json.dumps({**value, "network_profile": "gemini"}), encoding="utf-8")
        tampered_finish = [sys.executable, str(ROOT / "scripts/worker-evidence.py"), "finish",
                           str(evidence), "failed", "tampered", "1"]
        check(subprocess.run(tampered_finish, capture_output=True).returncode != 0,
              "evidence consumption rejects assignment tampering")

    print("phase5-hardening.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
