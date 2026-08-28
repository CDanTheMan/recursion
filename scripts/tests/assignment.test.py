#!/usr/bin/env python3
"""Hermetic controls for scripts/assignment.py (Phase 3, D-016).

Covers: digest stability/sensitivity, content-addressed idempotent persistence, fail-closed
capacity-pool manifest validation, and the resolve/show CLI end to end. Everything runs under
a disposable tempdir; nothing touches the live repo's state/.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
SCRIPTS = SOURCE / "scripts"
ASSIGNMENT = SCRIPTS / "assignment.py"

sys.path.insert(0, str(SCRIPTS))
import assignment as amod  # noqa: E402

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


BASE_KWARGS = dict(
    task_id="task-001", project_id="proj-001", role="implementer",
    source_repository="/opt/golden-stallion", source_branch="loop/work/task-001",
    source_sha="a" * 40, engine="claude", provider="anthropic-claude-code",
    host="gs-recursion", sandbox_profile="strict-linux", network_profile="provider-only",
    allowed_paths=["apps/api"], publication_policy="verified-integration-only",
)


def test_digest_stable_and_sensitive() -> None:
    first = amod.resolve_assignment(**BASE_KWARGS, created_at="2026-08-28T00:00:00Z")
    second = amod.resolve_assignment(**BASE_KWARGS, created_at="2026-08-28T00:00:00Z")
    check(first["assignment_digest"] == second["assignment_digest"],
          "identical inputs (incl. created_at) produce the identical digest")
    check(amod.canonical_digest(first) == first["assignment_digest"],
          "canonical_digest recomputation matches the stored digest")

    changed_kwargs = dict(BASE_KWARGS)
    changed_kwargs["engine"] = "hermes"
    third = amod.resolve_assignment(**changed_kwargs, created_at="2026-08-28T00:00:00Z")
    check(third["assignment_digest"] != first["assignment_digest"],
          "changing engine changes the digest")

    changed_time = amod.resolve_assignment(**BASE_KWARGS, created_at="2026-08-28T00:00:01Z")
    check(changed_time["assignment_digest"] != first["assignment_digest"],
          "changing created_at changes the digest (each resolution is its own record)")


def test_allowed_paths_normalized() -> None:
    value = amod.resolve_assignment(
        **{**BASE_KWARGS, "allowed_paths": ["b", "a", "a", "b"]},
        created_at="2026-08-28T00:00:00Z",
    )
    check(value["allowed_paths"] == ["a", "b"], "allowed_paths is sorted and deduped")


def test_allowed_paths_fail_closed() -> None:
    for path in ("../escape", "a/../../escape", "/absolute", r"C:\absolute"):
        try:
            amod.resolve_assignment(
                **{**BASE_KWARGS, "allowed_paths": [path]},
                created_at="2026-08-28T00:00:00Z",
            )
            check(False, f"authority-bearing path {path!r} is refused")
        except amod.AssignmentError:
            check(True, f"authority-bearing path {path!r} is refused")

    for path in (r"apps\api", "apps/./api", "apps//api", "./apps/api"):
        try:
            amod.resolve_assignment(**{**BASE_KWARGS, "allowed_paths": [path]}, created_at="2026-08-28T00:00:00Z")
            check(False, f"noncanonical path alias {path!r} is refused")
        except amod.AssignmentError:
            check(True, f"noncanonical path alias {path!r} is refused")


def test_fail_closed_invalid_inputs() -> None:
    for field, bad in (
        ("task_id", "bad id with spaces"),
        ("role", "implementor"),
        ("source_sha", "not-a-sha"),
        ("engine", ""),
        ("provider", "Anthropic Claude Code"),  # spaces/caps not allowed
        ("host", ""),
        ("sandbox_profile", "made-up-profile"),
        ("network_profile", "open"),
        ("publication_policy", "!!!"),
    ):
        kwargs = dict(BASE_KWARGS)
        kwargs[field] = bad
        try:
            amod.resolve_assignment(**kwargs)
            check(False, f"invalid {field}={bad!r} is refused")
        except amod.AssignmentError:
            check(True, f"invalid {field}={bad!r} is refused")


def test_empty_allowed_paths_refused() -> None:
    kwargs = dict(BASE_KWARGS)
    kwargs["allowed_paths"] = []
    try:
        amod.resolve_assignment(**kwargs)
        check(False, "empty allowed_paths is refused")
    except amod.AssignmentError:
        check(True, "empty allowed_paths is refused")


def test_persist_idempotent_and_collision_safe(tmp_path: Path) -> None:
    root = tmp_path / "assignments"
    value = amod.resolve_assignment(**BASE_KWARGS, created_at="2026-08-28T00:00:00Z")
    first_path = amod.persist_assignment(root, value)
    check(first_path.is_file(), "persist_assignment writes the assignment file")
    second_path = amod.persist_assignment(root, dict(value))
    check(second_path == first_path, "persisting identical content twice is a no-op (same path)")
    original = first_path.read_text(encoding="utf-8")

    # Simulate a content-address conflict directly (a real sha256 collision is not producible
    # in a test): overwrite the same digest-addressed path with different bytes, then confirm
    # persist_assignment refuses to reconcile/overwrite it.
    collide_path = amod.assignment_path(root, value["task_id"], value["assignment_digest"])
    collide_path.write_text(json.dumps({**value, "engine": "hermes"}, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    try:
        amod.persist_assignment(root, value)
        check(False, "a content-address collision (same digest path, different bytes) is refused")
    except amod.AssignmentError:
        check(True, "a content-address collision (same digest path, different bytes) is refused")
    finally:
        collide_path.write_text(original, encoding="utf-8")


def test_capacity_pool_validation(tmp_path: Path) -> None:
    pool_dir = tmp_path / "pools"
    pool_dir.mkdir()
    good = {
        "schema_version": 1, "id": "cursor-ultra", "kind": "subscription",
        "billing_basis": "metered", "provider": "cursor",
        "quota": {"period": "weekly", "source": "declared", "limit": 500, "unit": "requests"},
        "on_demand": False,
    }
    (pool_dir / "cursor-ultra.json").write_text(json.dumps(good), encoding="utf-8")
    loaded = amod.load_capacity_pool(pool_dir, "cursor-ultra")
    check(loaded["id"] == "cursor-ultra", "well-formed capacity-pool manifest loads")

    kwargs = dict(BASE_KWARGS)
    kwargs["capacity_pool"] = "cursor-ultra"
    kwargs["engine"] = "cursor"
    kwargs["provider"] = "cursor"
    kwargs["billing_basis"] = "metered"
    kwargs["metered_approved"] = True
    value = amod.resolve_assignment(**kwargs, capacity_pool_dir=pool_dir, created_at="2026-08-28T00:00:00Z")
    check(value["capacity_pool"] == "cursor-ultra", "assignment records a valid capacity_pool")

    kwargs["capacity_pool"] = "does-not-exist"
    try:
        amod.resolve_assignment(**kwargs, capacity_pool_dir=pool_dir)
        check(False, "referencing an unknown capacity_pool is refused")
    except amod.AssignmentError:
        check(True, "referencing an unknown capacity_pool is refused")

    bad = dict(good)
    bad["kind"] = "made-up"
    (pool_dir / "broken.json").write_text(json.dumps(bad), encoding="utf-8")
    try:
        amod.load_capacity_pool(pool_dir, "broken")
        check(False, "capacity-pool manifest with an invalid kind is refused")
    except amod.AssignmentError:
        check(True, "capacity-pool manifest with an invalid kind is refused")

    mismatched_id = dict(good); mismatched_id["id"] = "something-else"
    (pool_dir / "cursor-ultra2.json").write_text(json.dumps(mismatched_id), encoding="utf-8")
    try:
        amod.load_capacity_pool(pool_dir, "cursor-ultra2")
        check(False, "capacity-pool manifest id/filename mismatch is refused")
    except amod.AssignmentError:
        check(True, "capacity-pool manifest id/filename mismatch is refused")


def run_cli(args: list[str], env: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ASSIGNMENT), *args],
                          capture_output=True, text=True, env=env)


def test_cli_resolve_and_persist(tmp_path: Path) -> None:
    import os
    env = dict(os.environ)
    root = tmp_path / "assignments"
    out = tmp_path / "out.json"
    argv = [
        "resolve", "--task-id", "task-cli", "--project-id", "proj-cli", "--role", "implementer",
        "--source-repository", "/opt/x", "--source-branch", "main", "--source-sha", "b" * 40,
        "--engine", "claude", "--provider", "anthropic-claude-code", "--host", "gs-recursion",
        "--sandbox-profile", "strict-linux", "--network-profile", "provider-only",
        "--allowed-paths", "apps/api,apps/bot", "--publication-policy", "verified-integration-only",
        "--root", str(root), "--out", str(out),
    ]
    result = run_cli(argv, env)
    check(result.returncode == 0, f"CLI resolve exits 0 (stderr={result.stderr!r})")
    check(out.is_file(), "CLI resolve writes the --out copy")
    if out.is_file():
        emitted = json.loads(out.read_text(encoding="utf-8"))
        digest = emitted.get("assignment_digest", "")
        persisted = root / "task-cli" / f"{digest}.json"
        check(persisted.is_file(), "CLI resolve persists the content-addressed assignment file")
        check(emitted.get("allowed_paths") == ["apps/api", "apps/bot"],
              "CLI resolve normalizes a comma-separated allowed-paths string")
        index = root / "index.jsonl"
        check(index.is_file(), "CLI resolve appends to the durable assignment index")

        # Idempotent re-resolution with the exact same content-addressed file (created_at
        # differs, so this is really a *new* record; assert it does not clobber the first).
        result2 = run_cli(argv, env)
        check(result2.returncode == 0, "a second CLI resolve with identical arguments also exits 0")
        check(persisted.is_file(), "the first persisted assignment file is untouched by the second call")

        show = subprocess.run(
            [sys.executable, str(ASSIGNMENT), "show", "--task-id", "task-cli",
             "--assignment-digest", digest, "--root", str(root)],
            capture_output=True, text=True, env=env,
        )
        check(show.returncode == 0, "CLI show retrieves a persisted assignment")
        check(json.loads(show.stdout).get("assignment_digest") == digest, "CLI show returns matching content")


def test_cli_refuses_bad_role(tmp_path: Path) -> None:
    import os
    env = dict(os.environ)
    argv = [
        "resolve", "--task-id", "task-bad", "--project-id", "proj-bad", "--role", "not-a-role",
        "--source-repository", "/opt/x", "--source-branch", "main", "--source-sha", "c" * 40,
        "--engine", "claude", "--provider", "anthropic-claude-code", "--host", "gs-recursion",
        "--sandbox-profile", "strict-linux", "--network-profile", "provider-only",
        "--allowed-paths", ".", "--publication-policy", "verified-integration-only",
        "--root", str(tmp_path / "assignments"),
    ]
    result = run_cli(argv, env)
    check(result.returncode == 2, f"CLI resolve refuses an invalid role with exit 2 (got {result.returncode})")


def main() -> int:
    test_digest_stable_and_sensitive()
    test_allowed_paths_normalized()
    test_allowed_paths_fail_closed()
    test_fail_closed_invalid_inputs()
    test_empty_allowed_paths_refused()
    with tempfile.TemporaryDirectory() as tmp:
        test_persist_idempotent_and_collision_safe(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_capacity_pool_validation(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_cli_resolve_and_persist(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_cli_refuses_bad_role(Path(tmp))

    if failures:
        print(f"assignment.test: {len(failures)} FAILED")
        return 1
    print("assignment.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
