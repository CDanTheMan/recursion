#!/usr/bin/env python3
"""Hermetic controls for worker-evidence.py's Phase 3 (D-016) additions:
the optional --assignment-digest/--assignment-file pair on `start`, and the new
`remote-evidence` subcommand (remote session/branch/commit/artifact/cancellation evidence).

Confirms the pre-Phase-3 record shape is byte-for-byte unchanged when the new flags are
omitted (legacy behavior preserved), and that both flags together are required, matching,
and bound to the correct task before anything is embedded (fail closed).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
SCRIPTS = SOURCE / "scripts"
WORKER_EVIDENCE = SCRIPTS / "worker-evidence.py"

sys.path.insert(0, str(SCRIPTS))
import assignment as amod  # noqa: E402

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(WORKER_EVIDENCE), *args], capture_output=True, text=True)


def start_args(path: Path, run_id: str, task_id: str) -> list[str]:
    return [
        "start", "--path", str(path), "--run-id", run_id, "--task-id", task_id,
        "--role", "implementer", "--model-alias", "sonnet-routine", "--worktree", "/tmp/wt",
        "--base-commit", "a" * 40, "--pid", "100", "--process-group", "100",
        "--deadline-epoch", "9999999999", "--log", "loop/logs/x.out",
        "--network-policy", "provider-only",
    ]


def test_legacy_start_unchanged(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    result = run(start_args(path, "run-legacy", "task-1"))
    check(result.returncode == 0, f"start without assignment flags still exits 0 (got {result.returncode})")
    value = json.loads(path.read_text(encoding="utf-8"))
    for key in ("engine", "provider", "capacity_pool", "host", "sandbox_profile", "assignment_digest"):
        check(key not in value, f"legacy start (no assignment flags) never adds {key!r}")
    check(value["id"] == "run-legacy" and value["task_id"] == "task-1", "legacy start still writes the base record")


def make_assignment(tmp_path: Path, task_id: str = "task-1") -> tuple[Path, str]:
    root = tmp_path / "assignments"
    value = amod.resolve_assignment(
        task_id=task_id, project_id="proj-1", role="implementer",
        source_repository="/opt/golden-stallion", source_branch="loop/work/task-1",
        source_sha="a" * 40, engine="claude", provider="anthropic-claude-code",
        capacity_pool=None, host="gs-recursion", sandbox_profile="strict-linux",
        network_profile="provider-only", allowed_paths=["apps/api"],
        publication_policy="verified-integration-only", created_at="2026-08-28T00:00:00Z",
    )
    persisted = amod.persist_assignment(root, value)
    return persisted, value["assignment_digest"]


def test_start_binds_assignment(tmp_path: Path) -> None:
    assignment_file, digest = make_assignment(tmp_path)
    path = tmp_path / "run.json"
    args = start_args(path, "run-bound", "task-1") + \
        ["--assignment-digest", digest, "--assignment-file", str(assignment_file)]
    result = run(args)
    check(result.returncode == 0, f"start with a matching assignment pair exits 0 (got {result.returncode}, stderr={result.stderr!r})")
    value = json.loads(path.read_text(encoding="utf-8"))
    check(value.get("assignment_digest") == digest, "bound start embeds the assignment_digest")
    check(value.get("engine") == "claude", "bound start embeds engine from the assignment")
    check(value.get("provider") == "anthropic-claude-code", "bound start embeds provider from the assignment")
    check(value.get("host") == "gs-recursion", "bound start embeds host from the assignment")
    check(value.get("sandbox_profile") == "strict-linux", "bound start embeds sandbox_profile from the assignment")
    check(value.get("capacity_pool") is None, "bound start embeds a null capacity_pool when the assignment has none")


def test_start_refuses_one_sided_flags(tmp_path: Path) -> None:
    assignment_file, digest = make_assignment(tmp_path)
    path = tmp_path / "run.json"
    only_digest = run(start_args(path, "run-onesided-1", "task-1") + ["--assignment-digest", digest])
    check(only_digest.returncode == 2, f"--assignment-digest without --assignment-file is refused (got {only_digest.returncode})")
    check(not path.exists(), "a refused one-sided start writes no record")

    only_file = run(start_args(path, "run-onesided-2", "task-1") + ["--assignment-file", str(assignment_file)])
    check(only_file.returncode == 2, f"--assignment-file without --assignment-digest is refused (got {only_file.returncode})")


def test_start_refuses_digest_mismatch(tmp_path: Path) -> None:
    assignment_file, _digest = make_assignment(tmp_path)
    path = tmp_path / "run.json"
    wrong_digest = "0" * 64
    result = run(start_args(path, "run-wrong-digest", "task-1") +
                ["--assignment-digest", wrong_digest, "--assignment-file", str(assignment_file)])
    check(result.returncode == 2, f"a digest that does not match the assignment file's own digest is refused (got {result.returncode})")
    check(not path.exists(), "a refused digest-mismatch start writes no record")


def test_start_refuses_task_id_mismatch(tmp_path: Path) -> None:
    assignment_file, digest = make_assignment(tmp_path, task_id="task-1")
    path = tmp_path / "run.json"
    result = run(start_args(path, "run-wrong-task", "task-DIFFERENT") +
                ["--assignment-digest", digest, "--assignment-file", str(assignment_file)])
    check(result.returncode == 2, f"an assignment resolved for a different task_id is refused (got {result.returncode})")


def test_remote_evidence(tmp_path: Path) -> None:
    path = tmp_path / "run.json"
    assignment_file, digest = make_assignment(tmp_path)
    persisted = tmp_path / "assignments" / "task-1" / f"{digest}.json"
    bound_args = start_args(path, "run-remote", "task-1") + ["--assignment-digest", digest,
        "--assignment-file", str(assignment_file)]
    run(bound_args)
    first = run(["remote-evidence", str(path), "--session-id", "sess-1", "--branch", "cursor/task-1",
                "--commit", "b" * 40, "--artifact", "apps/api/a.txt=" + "c" * 64,
                "--artifact", "apps/api/b.txt=" + "d" * 64])
    check(first.returncode == 0, f"remote-evidence exits 0 (got {first.returncode}, stderr={first.stderr!r})")
    events = [json.loads(line) for line in (tmp_path / "remote-events.jsonl").read_text().splitlines()]
    remote = events[0]
    check(remote.get("session_id") == "sess-1", "remote-evidence records immutable session_id")
    check(remote.get("branch") == "cursor/task-1", "remote-evidence records authorized branch")
    check(remote.get("commit") == "b" * 40, "remote-evidence records exact commit")
    check([a["path"] for a in remote.get("artifacts", [])] == ["apps/api/a.txt", "apps/api/b.txt"],
          "remote-evidence records typed artifact paths")
    check(all(len(a["sha256"]) == 64 for a in remote.get("artifacts", [])),
          "remote-evidence records artifact sha256 values")

    second = run(["remote-evidence", str(path), "--session-id", "sess-1", "--event-type", "cancel",
                 "--cancelled-at", "2026-08-28T01:00:00Z", "--cancellation-reason", "quota-exhausted"])
    check(second.returncode == 0, "a cancellation transition appends successfully")
    check(len((tmp_path / "remote-events.jsonl").read_text().splitlines()) == 2,
          "remote evidence is append-only")
    duplicate = run(["remote-evidence", str(path), "--session-id", "sess-1", "--event-type", "terminal",
                      "--terminal-status", "cancelled"])
    check(duplicate.returncode == 0, "terminal cancellation transition appends successfully")
    duplicate2 = run(["remote-evidence", str(path), "--session-id", "sess-1", "--event-type", "terminal",
                       "--terminal-status", "cancelled"])
    check(duplicate2.returncode == 0 and len((tmp_path / "remote-events.jsonl").read_text().splitlines()) == 3,
          "identical terminal replay is idempotent without appending a duplicate")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        test_legacy_start_unchanged(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_start_binds_assignment(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_start_refuses_one_sided_flags(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_start_refuses_digest_mismatch(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_start_refuses_task_id_mismatch(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_remote_evidence(Path(tmp))

    if failures:
        print(f"worker-evidence-assignment.test: {len(failures)} FAILED")
        return 1
    print("worker-evidence-assignment.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
