#!/usr/bin/env python3
"""Offline contract, plan, and disposable restore-drill tooling for Phase 4 backups.

The default policy is disabled. ``validate`` and ``plan`` do not touch the network or
create a snapshot. ``restore-drill`` restores only into a temporary copy of the supplied
fixture root, making it suitable for hermetic CI and review. Production transfer remains
a human deployment seam.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path


class BackupPolicyError(ValueError):
    pass


POLICY_KEYS = {
    "schema_version", "id", "enabled", "source", "destination", "encryption",
    "retention", "log_rotation", "restore_drill",
}


def _object(value: object, keys: set[str], where: str) -> dict:
    if not isinstance(value, dict):
        raise BackupPolicyError(f"{where} must be an object")
    missing = keys - value.keys()
    extra = value.keys() - keys
    if missing:
        raise BackupPolicyError(f"{where} missing key(s): {', '.join(sorted(missing))}")
    if extra:
        raise BackupPolicyError(f"{where} has unknown key(s): {', '.join(sorted(extra))}")
    return value


def _positive(value: object, where: str, maximum: int = 3650) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
        raise BackupPolicyError(f"{where} must be an integer in 1..{maximum}")
    return value


def load_policy(path: Path) -> dict:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BackupPolicyError(f"backup policy is unreadable: {path}") from exc
    policy = _object(policy, POLICY_KEYS, "policy")
    if policy["schema_version"] != 1 or not isinstance(policy["enabled"], bool):
        raise BackupPolicyError("schema_version must be 1 and enabled must be boolean")
    if not isinstance(policy["id"], str) or not policy["id"]:
        raise BackupPolicyError("policy.id must be nonempty")
    source = _object(policy["source"], {"runtime_root", "snapshot_directory"}, "source")
    for key in ("runtime_root", "snapshot_directory"):
        if not isinstance(source[key], str) or not source[key].startswith("/"):
            raise BackupPolicyError(f"source.{key} must be an absolute path")
    destination = _object(
        policy["destination"], {"type", "host", "port", "path", "credential_ref"}, "destination"
    )
    if destination["type"] != "sftp" or not isinstance(destination["host"], str) \
            or not destination["host"] or not isinstance(destination["path"], str) \
            or not destination["path"].startswith("/"):
        raise BackupPolicyError("destination must be an sftp host and absolute path")
    _positive(destination["port"], "destination.port", 65535)
    if not isinstance(destination["credential_ref"], str) \
            or not destination["credential_ref"].startswith("secret:"):
        raise BackupPolicyError("destination.credential_ref must reference a secret, not contain one")
    encryption = _object(
        policy["encryption"], {"tool", "recipient_file", "identity_ref"}, "encryption"
    )
    if encryption["tool"] != "age" or not isinstance(encryption["recipient_file"], str) \
            or not encryption["recipient_file"].startswith("/") \
            or not isinstance(encryption["identity_ref"], str) \
            or not encryption["identity_ref"].startswith("secret:"):
        raise BackupPolicyError("encryption must use age and secret/file references")
    retention = _object(policy["retention"], {"daily", "weekly", "monthly"}, "retention")
    for key, maximum in (("daily", 3650), ("weekly", 520), ("monthly", 240)):
        _positive(retention[key], f"retention.{key}", maximum)
    rotation = _object(policy["log_rotation"], {"directory", "max_size_mb", "keep"}, "log_rotation")
    if not isinstance(rotation["directory"], str) or not rotation["directory"].startswith("/"):
        raise BackupPolicyError("log_rotation.directory must be absolute")
    _positive(rotation["max_size_mb"], "log_rotation.max_size_mb", 10240)
    _positive(rotation["keep"], "log_rotation.keep", 3650)
    drill = _object(policy["restore_drill"], {"cadence_days", "required"}, "restore_drill")
    _positive(drill["cadence_days"], "restore_drill.cadence_days", 3650)
    if drill["required"] is not True:
        raise BackupPolicyError("restore_drill.required must remain true")
    return policy


def runtime_module():
    source = Path(__file__).resolve().with_name("runtime-state.py")
    spec = importlib.util.spec_from_file_location("recursion_runtime_state", source)
    if spec is None or spec.loader is None:
        raise BackupPolicyError("runtime-state helper is absent")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def restore_drill(root: Path, snapshot: Path) -> None:
    runtime = runtime_module()
    if not root.is_dir() or root.is_symlink() or not snapshot.is_dir() or snapshot.is_symlink():
        raise BackupPolicyError("restore drill requires real root and snapshot directories")
    with tempfile.TemporaryDirectory(prefix="recursion-restore-drill-") as temporary:
        target = Path(temporary) / "root"
        shutil.copytree(root, target, symlinks=False)
        # runtime-state's operator output is useful interactively, but the drill's JSON result
        # is the machine-readable receipt and must not be mixed with that progress line.
        with contextlib.redirect_stdout(io.StringIO()):
            runtime.restore(target, snapshot)
        manifest = runtime.load_manifest(snapshot)
        observed = {item.relative_to(target).as_posix(): runtime.digest(item)
                    for item in runtime.collect_files(target)}
        expected = {item["path"]: item["sha256"] for item in manifest["files"]}
        if observed != expected:
            raise BackupPolicyError("restore drill did not reconstruct the manifest inventory")
    print(json.dumps({"status": "passed", "files": len(expected), "temporary_target": "discarded"}, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="backup-offsite")
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parents[1] / "deploy/backup/recursion-offsite.json")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("plan")
    drill = sub.add_parser("restore-drill")
    drill.add_argument("--root", type=Path, required=True)
    drill.add_argument("--snapshot", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        policy = load_policy(args.config)
        if args.command == "validate":
            print(json.dumps({"id": policy["id"], "enabled": policy["enabled"]}, sort_keys=True))
        elif args.command == "plan":
            print(json.dumps({
                "enabled": policy["enabled"],
                "steps": [
                    ["runtime-state.py", "backup", policy["source"]["snapshot_directory"] + "/<timestamp>"],
                    ["age", "--encrypt", "--recipients-file", policy["encryption"]["recipient_file"]],
                    ["sftp", "put", "<encrypted-snapshot>", policy["destination"]["path"]],
                    ["retention", "daily=%d" % policy["retention"]["daily"],
                     "weekly=%d" % policy["retention"]["weekly"], "monthly=%d" % policy["retention"]["monthly"]],
                ],
                "execution": "human-deployment-only",
            }, sort_keys=True))
        else:
            restore_drill(args.root.resolve(), args.snapshot.resolve())
        return 0
    except (OSError, ValueError, BackupPolicyError) as exc:
        print(f"backup-offsite: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
