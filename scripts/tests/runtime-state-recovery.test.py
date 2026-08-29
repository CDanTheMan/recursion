#!/usr/bin/env python3
"""Linux crash controls for exact runtime backup and restore."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]


def run_runtime(
    root: Path, *args: str, extra_env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "RECURSION_ROOT": str(root),
        "RECURSION_LOCK_ATTEMPTS": "3",
        "RECURSION_LOCK_DELAY_S": "0.02",
    }
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(SOURCE / "scripts/runtime-state.py"), *args],
        env=env, text=True, capture_output=True, check=False,
    )


def require(condition: bool, message: str, result: subprocess.CompletedProcess[str] | None = None) -> None:
    if condition:
        return
    detail = "" if result is None else (result.stdout + result.stderr)[-1000:]
    raise AssertionError(f"{message}\n{detail}")


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if os.name == "nt" or not Path("/proc/self/stat").is_file():
        print("runtime-state-recovery: SKIP (Linux production control)")
        return 0
    parent = Path(tempfile.mkdtemp(prefix="runtime-recovery-"))
    root = parent / "runtime"
    snapshot = parent / "snapshot"
    recovered = parent / "recovered"
    orphan_destination = parent / "orphan-backup"
    try:
        (root / "state/.locks").mkdir(parents=True)
        (root / "state/goals").mkdir()
        (root / "state/PAUSE").write_text("test pause\n", encoding="utf-8")
        (root / "state/events.jsonl").write_text('{"event":"before"}\n', encoding="utf-8")
        (root / "state/decisions.jsonl").write_text('{"id":"decision-before"}\n', encoding="utf-8")
        (root / "state/.openrouter-usage.json").write_text(
            '{"total_tokens":7}\n', encoding="utf-8"
        )
        (root / "state/goals/goal.md").write_text("status: active\n", encoding="utf-8")

        result = run_runtime(root, "backup", str(snapshot))
        require(result.returncode == 0, "initial backup failed", result)
        manifest = json.loads((snapshot / "manifest.json").read_text(encoding="utf-8"))
        paths = {record["path"] for record in manifest["files"]}
        require("state/.openrouter-usage.json" in paths, "OpenRouter usage was omitted")

        malformed = parent / "malformed-snapshot"
        shutil.copytree(snapshot, malformed)
        (malformed / "manifest.json").write_text("{", encoding="utf-8")
        result = run_runtime(root, "restore", str(malformed))
        require(result.returncode != 0, "malformed backup manifest was accepted", result)
        require("Traceback" not in result.stderr and "JSONDecodeError" not in result.stderr,
                "malformed backup manifest leaked a raw parser exception", result)
        shutil.copytree(snapshot, parent / "boolean-snapshot")
        boolean_manifest = parent / "boolean-snapshot" / "manifest.json"
        boolean_manifest.write_text(
            json.dumps({**manifest, "schema_version": True}) + "\n", encoding="utf-8"
        )
        result = run_runtime(root, "restore", str(parent / "boolean-snapshot"))
        require(result.returncode != 0, "boolean backup manifest schema_version was accepted", result)
        require("Traceback" not in result.stderr, "boolean backup manifest leaked a traceback", result)

        (root / "state/events.jsonl").write_text('{"event":"after"}\n', encoding="utf-8")
        (root / "state/.openrouter-usage.json").unlink()
        (root / "state/goals/goal.md").write_text("status: changed\n", encoding="utf-8")
        (root / "state/goals/extra.md").write_text("must disappear\n", encoding="utf-8")
        result = run_runtime(root, "restore", str(snapshot))
        require(result.returncode == 0, "exact restore failed", result)
        require(
            (root / "state/events.jsonl").read_text(encoding="utf-8") == '{"event":"before"}\n',
            "restore retained a hybrid live journal",
        )
        require(
            (root / "state/.openrouter-usage.json").read_text(encoding="utf-8")
            == '{"total_tokens":7}\n',
            "restore did not recover OpenRouter usage",
        )
        require(not (root / "state/goals/extra.md").exists(), "restore retained an extra file")
        print("ok    restore replaces managed runtime state exactly, including OpenRouter usage")

        escaped = parent / "escaped"
        shutil.copytree(snapshot, escaped)
        escaped_manifest = json.loads((escaped / "manifest.json").read_text(encoding="utf-8"))
        escaped_manifest["files"].append({
            "path": "state/goals/../../README.md",
            "sha256": "0" * 64,
            "size": 0,
            "mode": "0o600",
            "uid": os.getuid(),
            "gid": os.getgid(),
        })
        (escaped / "manifest.json").write_text(
            json.dumps(escaped_manifest, sort_keys=True) + "\n", encoding="utf-8"
        )
        before_pause = file_sha(root / "state/PAUSE")
        result = run_runtime(root, "restore", str(escaped))
        require(result.returncode != 0, "manifest traversal was accepted", result)
        require(file_sha(root / "state/PAUSE") == before_pause, "rejected manifest mutated state")
        print("ok    typed manifest paths cannot escape the managed runtime allowlist")

        (root / "state/events.jsonl").write_text('{"event":"live-preimage"}\n', encoding="utf-8")
        (root / "state/.openrouter-usage.json").write_text(
            '{"total_tokens":999}\n', encoding="utf-8"
        )
        result = run_runtime(
            root, "restore", str(snapshot),
            extra_env={"RECURSION_RESTORE_CRASH_AFTER": "2"},
        )
        require(result.returncode == 92, "restore crash injection did not fire", result)
        transaction = root / "state/.locks/runtime-restore.transaction"
        require(transaction.is_dir(), "crashed restore did not leave a durable transaction")
        result = run_runtime(root, "backup", str(recovered))
        require(result.returncode == 0, "maintenance did not resolve crashed restore", result)
        require(not transaction.exists(), "resolved restore transaction remained visible")
        require(
            (root / "state/events.jsonl").read_text(encoding="utf-8") == '{"event":"before"}\n'
            and (root / "state/.openrouter-usage.json").read_text(encoding="utf-8")
            == '{"total_tokens":7}\n',
            "crash recovery did not roll forward to one exact desired cut",
        )
        print("ok    a mid-restore crash is resolved before later maintenance can take a cut")

        start = Path("/proc/self/stat").read_text(encoding="utf-8").split()[21]
        orphan = parent / f".{orphan_destination.name}.tmp.999999999.{start}.fixture"
        orphan.mkdir()
        (orphan / "partial").write_text("partial\n", encoding="utf-8")
        result = run_runtime(root, "backup", str(orphan_destination))
        require(result.returncode == 0, "backup after orphan staging failed", result)
        require(not orphan.exists(), "dead backup staging was not reclaimed")
        print("ok    dead backup staging is reclaimed without publishing a partial snapshot")
        print("runtime-state-recovery: ALL PASS")
        return 0
    finally:
        shutil.rmtree(parent, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
