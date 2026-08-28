#!/usr/bin/env python3
"""Adversarial Phase 4 backup tests using fake age and SFTP executables."""

from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "scripts/backup-offsite.py"


def run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, env=env)


FAKE_TOOLS = r'''
import os, shutil, sys
from pathlib import Path
mode = sys.argv[1]
if mode == "age":
    decrypt = "--decrypt" in sys.argv
    output = Path(sys.argv[sys.argv.index("--output") + 1])
    source = Path(sys.argv[-1])
    data = source.read_bytes()
    if decrypt:
        assert data.startswith(b"FAKE-AGE\n")
        data = data[len(b"FAKE-AGE\n"):]
    else:
        data = b"FAKE-AGE\n" + data
    output.write_bytes(data)
elif mode == "sftp":
    state = Path(os.environ["FAKE_SFTP_STATE"]); state.mkdir(exist_ok=True)
    batch = sys.stdin.read().splitlines()
    for line in batch:
        words = line.split()
        if not words: continue
        if words[0] == "put": shutil.copyfile(words[1], state / Path(words[2]).name)
        elif words[0] == "get": shutil.copyfile(state / Path(words[1]).name, words[2])
        elif words[0] == "rm": (state / Path(words[1]).name).unlink()
        elif words[0] == "ls":
            for path in sorted(state.iterdir()): print("/remote/" + path.name)
        else: raise SystemExit("unsupported fake sftp command")
else: raise SystemExit("unsupported fake tool")
'''


def main() -> int:
    failures: list[str] = []

    def check(condition: bool, label: str) -> None:
        print(("ok - " if condition else "FAIL - ") + label)
        if not condition:
            failures.append(label)

    policy = run("validate")
    check(policy.returncode == 0, "shipped backup policy validates")
    check('"enabled": false' in policy.stdout, "shipped backup policy is disabled")
    plan = run("plan")
    check(plan.returncode == 0, "backup plan is generated without side effects")
    check('"explicit_execute_required": true' in plan.stdout, "plan requires explicit execution")
    check('"off_host_restore": "pending live evidence"' in plan.stdout,
          "plan does not claim an off-host restore")
    disabled = run("backup", "--execute")
    check(disabled.returncode == 2 and "disabled" in disabled.stderr,
          "disabled defaults refuse execution")

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        fixture = base / "fixture"
        (fixture / "state/.locks").mkdir(parents=True)
        (fixture / "state/actions").mkdir()
        (fixture / "state/PAUSE").write_text("paused for test\n", encoding="utf-8")
        (fixture / "state/events.jsonl").write_text("event\n", encoding="utf-8")
        snapshot = base / "snapshot"
        env = dict(os.environ, RECURSION_ROOT=str(fixture))
        runtime = subprocess.run([sys.executable, str(ROOT / "scripts/runtime-state.py"), "backup", str(snapshot)],
                                 capture_output=True, text=True, env=env)
        check(runtime.returncode == 0, "runtime snapshot fixture is created")
        (fixture / "state/goals").mkdir()
        (fixture / "state/goals/extra.md").write_text("not in snapshot\n", encoding="utf-8")
        drill = run("restore-drill", "--root", str(fixture), "--snapshot", str(snapshot))
        check(drill.returncode == 0 and '"status": "prepared"' in drill.stdout,
              "local restore drill is labeled prepared, not production-proven")
        spec = importlib.util.spec_from_file_location("backup_offsite_test_module", TOOL)
        assert spec and spec.loader
        backup_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(backup_module)
        with backup_module.pause_transfer(fixture):
            contender = subprocess.run(
                [sys.executable, "-c", """
import importlib.util, sys
spec = importlib.util.spec_from_file_location('backup_offsite', sys.argv[1])
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
try:
    with module.pause_transfer(__import__('pathlib').Path(sys.argv[2])):
        raise SystemExit(0)
except Exception:
    raise SystemExit(73)
""", str(TOOL), str(fixture)], capture_output=True, text=True)
            check(contender.returncode != 0,
                  "PAUSE transfer admission lock rejects a concurrent transfer")
        bounded = base / "bounded.tar"
        with tarfile.open(bounded, "w") as archive:
            for index in range(2):
                item = base / f"bounded-{index}"
                item.write_bytes(b"x")
                archive.add(item, arcname=f"snapshot/{item.name}")
        try:
            backup_module.validate_archive_bounds(bounded, {"max_files": 1, "max_bytes": 100})
        except backup_module.BackupPolicyError:
            check(True, "archive file-count bound refuses oversized manifests")
        else:
            check(False, "archive file-count bound refuses oversized manifests")
        check(backup_module.artifact_time("backup-20261399T999999Z.tar.age") is None,
              "impossible backup timestamp is rejected without raising")
        original_sftp = backup_module.sftp
        try:
            backup_module.sftp = lambda *_args, **_kwargs: b"/remote/" + b"x" * (backup_module.MAX_SFTP_OUTPUT + 1)
            try:
                backup_module._remote_listing({"destination": {"path": "/remote"}})
            except backup_module.BackupPolicyError:
                check(True, "remote listing output is bounded before splitlines memory growth")
            else:
                check(False, "remote listing output is bounded before splitlines memory growth")
        finally:
            backup_module.sftp = original_sftp

        tools = base / "fake-tools.py"
        tools.write_text(FAKE_TOOLS, encoding="utf-8")
        credentials = base / "credentials"; credentials.mkdir()
        for name, value in (("sftp-key", "fake-sftp-key"), ("age-id", "fake-age-id"),
                            ("config-key", "config-secret")):
            path = credentials / name
            path.write_text(value, encoding="utf-8")
            try: path.chmod(stat.S_IRUSR | stat.S_IWUSR)
            except OSError: pass
        recipient = base / "recipient.age"; recipient.write_text("age1-test", encoding="ascii")
        signature = base / "policy.sig"
        config = base / "policy.json"
        value = {
            "schema_version": 1, "id": "test-offsite", "enabled": True,
            "source": {"runtime_root": str(fixture), "snapshot_directory": str(base / "snapshots"),
                        "runtime_directory": str(base / "runtime")},
            "destination": {"type": "sftp", "user": "backup", "host": "backup.test",
                            "port": 22, "path": "/remote", "credential_ref": "secret:sftp-key"},
            "encryption": {"tool": "age", "recipient_file": str(recipient),
                           "identity_ref": "secret:age-id"},
            "authentication": {"type": "hmac-sha256", "key_ref": "secret:config-key",
                                "signature_file": str(signature)},
            "retention": {"daily": 2, "weekly": 2, "monthly": 2},
            "log_rotation": {"directory": str(base / "evidence"), "max_size_mb": 50, "keep": 14},
            "restore_drill": {"cadence_days": 30, "required": True},
            "archive_limits": {"max_files": 10000, "max_bytes": 104857600},
        }
        config.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        signature.write_text(hmac.new(b"config-secret", config.read_bytes(), hashlib.sha256).hexdigest(),
                             encoding="ascii")
        exec_env = dict(os.environ, CREDENTIALS_DIRECTORY=str(credentials),
                        RECURSION_SECRET_RUNTIME_ROOT=str(base / "runtime"),
                        FAKE_SFTP_STATE=str(base / "sftp-state"),
                        RECURSION_AGE_TOOL=sys.executable, RECURSION_SFTP_TOOL=sys.executable,
                        RECURSION_AGE_TOOL_ARGS_JSON=json.dumps([str(tools), "age"]),
                        RECURSION_SFTP_TOOL_ARGS_JSON=json.dumps([str(tools), "sftp"]))
        sftp_state = base / "sftp-state"
        sftp_state.mkdir()
        for old in ("20000101", "20010101", "20020101"):
            (sftp_state / f"backup-{old}T000000Z.tar.age").write_bytes(b"old-ciphertext")
        backup = run("--config", str(config), "backup", "--execute", env=exec_env)
        check(backup.returncode == 0, f"fake age/SFTP backup executes ({backup.stderr.strip()})")
        if backup.returncode == 0:
            evidence = json.loads(backup.stdout)
            check(evidence["encrypted"] and evidence["remote_uploaded"],
                  "backup evidence is encrypted and transfer-acknowledged")
            check(evidence["restore_evidence"] == "pending live evidence",
                  "backup evidence does not claim an off-host restore")
            check(evidence["retention"]["deleted"] == 0
                  and len(evidence["retention"]["invalid_deleted"]) == 3,
                  "reconciliation deletes bounded nonconforming encrypted artifacts")
            remote = max((base / "sftp-state").glob("backup-*.tar.age"), default=None)
            check(remote is not None and remote.read_bytes().startswith(b"FAKE-AGE\n"),
                  "SFTP fixture receives ciphertext rather than plaintext")
            check((base / "snapshots" / remote.name).is_file() if remote else False,
                  "canonical snapshot directory durably retains the encrypted artifact")
            evidence_path = Path(evidence["evidence_path"])
            check(evidence_path.is_file() and b"config-secret" not in evidence_path.read_bytes(),
                  "evidence is atomically written without secret values")
            check(not any((base / "runtime").glob(".backup.*")),
                  "plaintext workspace is removed after successful execution")
            (fixture / "state/events.jsonl").write_text("changed\n", encoding="utf-8")
            restore = run("--config", str(config), "restore", "--execute", env=exec_env)
            check(restore.returncode == 0, f"fake SFTP/age restore executes ({restore.stderr.strip()})")
            check((fixture / "state/events.jsonl").read_text(encoding="utf-8") == "event\n",
                  "restore reconstructs the encrypted snapshot")
            check('"off_host_restore": "pending live evidence"' in restore.stdout,
                  "restore output records pending live evidence")
            pause = fixture / "state/PAUSE"
            pause.unlink()
            blocked = run("--config", str(config), "reconcile", "--execute", env=exec_env)
            check(blocked.returncode == 2 and "PAUSE admission" in blocked.stderr,
                  "reconcile refuses before any remote contact without PAUSE")
            pause.write_text("paused for test\n", encoding="utf-8")
        tampered = json.loads(config.read_text(encoding="utf-8")); tampered["destination"]["host"] = "evil.test"
        config.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")
        refused = run("--config", str(config), "reconcile", "--execute", env=exec_env)
        check(refused.returncode == 2 and "signature" in refused.stderr,
              "tampered configuration is refused before SFTP")

    if failures:
        print(f"backup-offsite.test: {len(failures)} FAILED")
        return 1
    print("backup-offsite.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
