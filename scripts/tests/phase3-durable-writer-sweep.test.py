#!/usr/bin/env python3
"""Class-wide Phase 3 durability and schema/runtime differential harness.

The cases intentionally use one explicit directory below the system temp directory.  Each
writer receives the same leaf, post-open hardlink, leaf-junction, ancestor-junction, and root-
junction battery; every refusal must be typed and the outside sentinel must remain unchanged.
"""

from __future__ import annotations

import copy
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
SCRIPTS = SOURCE / "scripts"
sys.path.insert(0, str(SCRIPTS))

import assignment as amod  # noqa: E402
import jsonl_durable as jd  # noqa: E402
import run_contract  # noqa: E402

WORKER_SPEC = importlib.util.spec_from_file_location("phase3_worker_evidence", SCRIPTS / "worker-evidence.py")
if WORKER_SPEC is None or WORKER_SPEC.loader is None:
    raise SystemExit("phase3 sweep: worker-evidence loader unavailable")
worker = importlib.util.module_from_spec(WORKER_SPEC)
WORKER_SPEC.loader.exec_module(worker)

USAGE_SPEC = importlib.util.spec_from_file_location("phase3_usage_reconcile", SCRIPTS / "usage-reconcile.py")
if USAGE_SPEC is None or USAGE_SPEC.loader is None:
    raise SystemExit("phase3 sweep: usage-reconcile loader unavailable")
usage = importlib.util.module_from_spec(USAGE_SPEC)
USAGE_SPEC.loader.exec_module(usage)

try:
    from jsonschema import Draft7Validator, Draft202012Validator, validators
except ImportError as exc:  # pragma: no cover - the required verification environment has it.
    raise SystemExit(f"phase3 sweep: jsonschema unavailable: {exc}")


STRICT_INTEGER_CHECKER = Draft7Validator.TYPE_CHECKER.redefine(
    "integer", lambda _checker, value: isinstance(value, int) and not isinstance(value, bool)
)
StrictDraft7Validator = validators.extend(Draft7Validator, type_checker=STRICT_INTEGER_CHECKER)
STRICT_RUN_INTEGER_CHECKER = Draft202012Validator.TYPE_CHECKER.redefine(
    "integer", lambda _checker, value: isinstance(value, int) and not isinstance(value, bool)
)
StrictDraft202012Validator = validators.extend(
    Draft202012Validator, type_checker=STRICT_RUN_INTEGER_CHECKER
)


failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def expect_refusal(action, label: str, error_types: tuple[type[BaseException], ...]) -> None:
    try:
        action()
    except error_types as exc:
        check("Traceback" not in str(exc), f"{label} is refused with a typed error")
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeError, sqlite3.DatabaseError) as exc:
        check(False, f"{label} leaked raw {type(exc).__name__}: {exc}")
    else:
        check(False, f"{label} was accepted")


def outside_sentinel(path: Path) -> bytes:
    value = b"outside-sentinel\n"
    path.write_bytes(value)
    return value


def make_link(link: Path, target: Path, *, directory: bool, reparse: bool = False) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        command = ["cmd.exe", "/d", "/c", "mklink"]
        if directory:
            command.append("/J")
        elif not reparse:
            command.append("/H")
        command.extend([str(link), str(target)])
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise AssertionError(f"could not create Windows link: {result.stderr or result.stdout}")
    else:
        if directory or reparse:
            link.symlink_to(target, target_is_directory=directory)
        else:
            link.hardlink_to(target)


def base_assignment(task_id: str) -> dict:
    return amod.resolve_assignment(
        task_id=task_id, project_id="project", role="implementer",
        source_repository="/repo", source_branch="main", source_sha="a" * 40,
        engine="claude", provider="anthropic-claude-code", host="gs-recursion",
        sandbox_profile="strict-linux", network_profile="provider-only", allowed_paths=["app"],
        publication_policy="verified-integration-only", created_at="2026-08-28T00:00:00Z",
    )


def test_jsonl_battery(root: Path) -> None:
    error_types = (jd.JsonlDurabilityError,)
    normal = root / "jsonl-normal" / "events.jsonl"
    outcome = jd.append_jsonl(normal, {"id": "normal"})
    check(outcome.appended and jd.read_jsonl_objects(normal) == [{"id": "normal"}],
          "JSONL normal append/read still succeeds")

    hardlink_root = root / "jsonl-hardlink"
    path = hardlink_root / "events.jsonl"
    outside = hardlink_root / "outside.jsonl"
    path.parent.mkdir(parents=True)
    original = outside_sentinel(outside)
    make_link(path, outside, directory=False)
    expect_refusal(lambda: jd.append_jsonl(path, {"id": "pre-existing-hardlink"}),
                   "JSONL pre-existing hardlinked journal", error_types)
    check(outside.read_bytes() == original, "JSONL pre-existing hardlink leaves outside untouched")

    race_root = root / "jsonl-race"
    race_path = race_root / "events.jsonl"
    race_path.parent.mkdir(parents=True)
    race_path.write_bytes(b'{"id":"prior"}\n')
    race_outside = race_root / "outside.jsonl"
    armed = True

    def race_hook(stage: str) -> None:
        nonlocal armed
        if armed and stage == "pre-journal-write":
            armed = False
            make_link(race_outside, race_path, directory=False)

    expect_refusal(lambda: jd.append_jsonl(race_path, {"id": "race"}, hook=race_hook),
                   "JSONL post-validation journal hardlink", error_types)
    check(not armed and race_outside.read_bytes() == b'{"id":"prior"}\n',
          "JSONL post-validation hardlink hook executed without outside bytes")

    quarantine_root = root / "jsonl-quarantine-race"
    quarantine_path = quarantine_root / "events.jsonl"
    quarantine_path.parent.mkdir(parents=True)
    quarantine_path.write_bytes(b'{"id":"complete"}\ntruncated-tail')
    quarantine_alias = quarantine_root / "outside-quarantine.bin"
    armed = True

    def quarantine_hook(stage: str) -> None:
        nonlocal armed
        if armed and stage == "pre-quarantine-payload-write":
            armed = False
            temp = next((quarantine_root / "jsonl-quarantine").glob(".jsonl-tail.tmp.*"))
            make_link(quarantine_alias, temp, directory=False)

    expect_refusal(lambda: jd.append_jsonl(
        quarantine_path, {"id": "after-tail"}, hook=quarantine_hook
    ), "JSONL quarantine payload post-validation hardlink", error_types)
    check(not armed and quarantine_alias.read_bytes() == b"",
          "JSONL quarantine hardlink is refused before outside publication")
    quarantine_alias.unlink(missing_ok=True)

    junction_leaf = root / "jsonl-junction-leaf"
    jpath = junction_leaf / "events.jsonl"
    jtarget = junction_leaf / "outside-target.jsonl"
    jtarget.parent.mkdir(parents=True)
    joriginal = outside_sentinel(jtarget)
    make_link(jpath, jtarget, directory=False, reparse=True)
    expect_refusal(lambda: jd.append_jsonl(jpath, {"id": "junction-leaf"}),
                   "JSONL junction/reparse leaf", error_types)
    check(jtarget.read_bytes() == joriginal, "JSONL junction leaf receives no bytes")

    ancestor = root / "jsonl-junction-ancestor"
    atarget = ancestor / "outside-target"
    atarget.mkdir(parents=True)
    make_link(ancestor / "store", atarget, directory=True)
    expect_refusal(lambda: jd.append_jsonl(ancestor / "store" / "events.jsonl", {"id": "ancestor"}),
                   "JSONL junction/reparse ancestor", error_types)
    check(not (atarget / "events.jsonl").exists(), "JSONL junction ancestor receives no bytes")

    store_root = root / "jsonl-junction-root"
    store_target = root / "jsonl-root-outside"
    store_target.mkdir()
    make_link(store_root, store_target, directory=True)
    expect_refusal(lambda: jd.append_jsonl(store_root / "events.jsonl", {"id": "root"}),
                   "JSONL junction/reparse store root", error_types)
    check(not (store_target / "events.jsonl").exists(), "JSONL junction store root receives no bytes")

    atomic_root = root / "jsonl-atomic"
    atomic_path = atomic_root / "record.json"
    atomic_root.mkdir(parents=True)
    atomic_outside = atomic_root / "outside.json"
    atomic_original = outside_sentinel(atomic_outside)
    make_link(atomic_path, atomic_outside, directory=False)
    expect_refusal(lambda: jd.atomic_bytes(atomic_path, b"new\n"),
                   "JSONL atomic replacement pre-existing hardlink", error_types)
    check(atomic_outside.read_bytes() == atomic_original, "JSONL atomic hardlink leaves outside untouched")

    race_atomic = root / "jsonl-atomic-race"
    race_atomic.mkdir(parents=True)
    race_target = race_atomic / "record.json"
    race_alias = race_atomic / "outside.json"
    armed = True

    def atomic_hook(stage: str) -> None:
        nonlocal armed
        if armed and stage == "pre-write":
            armed = False
            temp = next(race_atomic.glob(".record.json.tmp.*"))
            make_link(race_alias, temp, directory=False)

    expect_refusal(lambda: jd.atomic_bytes(race_target, b"race\n", hook=atomic_hook),
                   "JSONL atomic replacement post-validation hardlink", error_types)
    check(not armed and not race_target.exists(), "JSONL atomic post-validation race leaves no target")

    atomic_junction_leaf = root / "jsonl-atomic-junction-leaf"
    atomic_junction_target = atomic_junction_leaf / "outside-target.json"
    atomic_junction_target.parent.mkdir(parents=True)
    atomic_junction_original = outside_sentinel(atomic_junction_target)
    make_link(atomic_junction_leaf / "record.json", atomic_junction_target,
              directory=False, reparse=True)
    expect_refusal(lambda: jd.atomic_bytes(atomic_junction_leaf / "record.json", b"junction\n"),
                   "JSONL atomic replacement junction leaf", error_types)
    check(atomic_junction_target.read_bytes() == atomic_junction_original,
          "JSONL atomic junction leaf receives no bytes")

    atomic_ancestor = root / "jsonl-atomic-junction-ancestor"
    atomic_ancestor_target = atomic_ancestor / "outside-target"
    atomic_ancestor_target.mkdir(parents=True)
    make_link(atomic_ancestor / "store", atomic_ancestor_target, directory=True)
    expect_refusal(lambda: jd.atomic_bytes(atomic_ancestor / "store" / "record.json", b"ancestor\n"),
                   "JSONL atomic replacement junction ancestor", error_types)
    check(not (atomic_ancestor_target / "record.json").exists(),
          "JSONL atomic junction ancestor receives no bytes")

    atomic_root_link = root / "jsonl-atomic-junction-root"
    atomic_root_target = root / "jsonl-atomic-root-outside"
    atomic_root_target.mkdir()
    make_link(atomic_root_link, atomic_root_target, directory=True)
    expect_refusal(lambda: jd.atomic_bytes(atomic_root_link / "record.json", b"root\n"),
                   "JSONL atomic replacement junction store root", error_types)
    check(not (atomic_root_target / "record.json").exists(),
          "JSONL atomic junction store root receives no bytes")

    rebuild_root = root / "jsonl-rebuild"
    rebuild_path = rebuild_root / "events.jsonl"
    jd.append_jsonl(rebuild_path, {"id": "one"})
    indexes = list((rebuild_root / "jsonl-index").glob("*.sqlite3"))
    check(len(indexes) == 1, "JSONL creates a verification SQLite index")
    if indexes:
        index = indexes[0]
        rebuild_outside = rebuild_root / "outside-index.sqlite3"
        rebuild_original = index.read_bytes()
        rebuild_outside.write_bytes(rebuild_original)
        index.unlink()
        make_link(index, rebuild_outside, directory=False)
        expect_refusal(lambda: jd.read_jsonl_objects(rebuild_path),
                       "JSONL pre-existing hardlinked SQLite index", error_types)
        check(rebuild_outside.read_bytes() == rebuild_original,
              "JSONL hardlinked SQLite index leaves outside untouched")

    rebuild_race = root / "jsonl-rebuild-race"
    rebuild_race_path = rebuild_race / "events.jsonl"
    jd.append_jsonl(rebuild_race_path, {"id": "one"})
    rebuild_indexes = list((rebuild_race / "jsonl-index").glob("*.sqlite3"))
    if rebuild_indexes:
        rebuild_indexes[0].write_bytes(b"not-a-sqlite-cache")
    rebuild_alias = rebuild_race / "outside-rebuild.sqlite3"
    armed = True

    def rebuild_hook(stage: str) -> None:
        nonlocal armed
        if armed and stage == "pre-write":
            temps = list((rebuild_race / "jsonl-index").glob("*.sqlite3.tmp.*"))
            if not temps:
                temps = list((rebuild_race / "jsonl-index").glob(".*.tmp.*"))
            if not temps:
                return
            armed = False
            make_link(rebuild_alias, temps[0], directory=False)

    expect_refusal(lambda: jd.append_jsonl(rebuild_race_path, {"id": "two"}, hook=rebuild_hook),
                   "JSONL SQLite index rebuild post-validation hardlink", error_types)
    check(not armed and rebuild_alias.read_bytes() == b"",
          "JSONL SQLite rebuild hardlink is refused before outside publication")

    rebuild_positive = root / "jsonl-rebuild-positive"
    rebuild_positive_path = rebuild_positive / "events.jsonl"
    jd.append_jsonl(rebuild_positive_path, {"id": "one"})
    positive_index = next((rebuild_positive / "jsonl-index").glob("*.sqlite3"))
    positive_index.unlink()
    check(jd.read_jsonl_objects(rebuild_positive_path) == [{"id": "one"}],
          "JSONL normal SQLite index rebuild succeeds")

    rebuild_in_place_root = root / "jsonl-rebuild-in-place"
    rebuild_in_place_path = rebuild_in_place_root / "events.jsonl"
    in_place_calls = 0
    original_rebuild_in_place = jd._rebuild_index_in_place

    def tracked_rebuild_in_place(*args, **kwargs):
        nonlocal in_place_calls
        in_place_calls += 1
        return original_rebuild_in_place(*args, **kwargs)

    jd._rebuild_index_in_place = tracked_rebuild_in_place
    try:
        jd.append_jsonl(rebuild_in_place_path, {"id": "one"}, rebuild_in_place=True)
        jd.append_jsonl(rebuild_in_place_path, {"id": "two"}, rebuild_in_place=True)
        in_place_index = next((rebuild_in_place_root / "jsonl-index").glob("*.sqlite3"))
        in_place_index.write_bytes(b"not-a-sqlite-cache")
        jd.append_jsonl(rebuild_in_place_path, {"id": "three"}, rebuild_in_place=True)
    finally:
        jd._rebuild_index_in_place = original_rebuild_in_place
    check(in_place_calls == 2 and jd.read_jsonl_objects(rebuild_in_place_path) == [
        {"id": "one"}, {"id": "two"}, {"id": "three"}
    ], "JSONL retained rebuild_in_place=True branch rebuilds missing/corrupt caches")

    index_junction_leaf = root / "jsonl-index-junction-leaf"
    index_journal = index_junction_leaf / "events.jsonl"
    index_identity = "phase3/junction-leaf"
    jd.append_jsonl(index_journal, {"id": "one"},
                    index_root=index_junction_leaf / "cache", index_identity=index_identity)
    index_leaf = index_junction_leaf / "cache" / jd.index_cache_name(index_identity)
    index_target = index_junction_leaf / "outside-index-target.sqlite3"
    index_original = index_leaf.read_bytes()
    index_target.write_bytes(index_original)
    index_leaf.unlink()
    make_link(index_leaf, index_target, directory=False, reparse=True)
    expect_refusal(lambda: jd.append_jsonl(index_journal, {"id": "two"},
                                            index_root=index_junction_leaf / "cache",
                                            index_identity=index_identity),
                   "JSONL SQLite index junction leaf", error_types)
    check(index_target.read_bytes() == index_original,
          "JSONL SQLite index junction leaf receives no bytes")

    index_junction_ancestor = root / "jsonl-index-junction-ancestor"
    index_ancestor_target = index_junction_ancestor / "outside-index-target"
    index_ancestor_target.mkdir(parents=True)
    make_link(index_junction_ancestor / "store", index_ancestor_target, directory=True)
    expect_refusal(lambda: jd.append_jsonl(
        index_junction_ancestor / "events.jsonl", {"id": "ancestor"},
        index_root=index_junction_ancestor / "store" / "cache", index_identity="phase3/ancestor"
    ), "JSONL SQLite index junction ancestor", error_types)
    check(not (index_ancestor_target / "cache").exists(),
          "JSONL SQLite index junction ancestor receives no bytes")

    index_junction_root = root / "jsonl-index-junction-root"
    index_root_target = root / "jsonl-index-root-outside"
    index_root_target.mkdir()
    make_link(index_junction_root, index_root_target, directory=True)
    expect_refusal(lambda: jd.append_jsonl(
        root / "jsonl-index-root-journal" / "events.jsonl", {"id": "root"},
        index_root=index_junction_root, index_identity="phase3/root"
    ), "JSONL SQLite index junction store root", error_types)
    check(not (index_root_target / jd.index_cache_name("phase3/root")).exists(),
          "JSONL SQLite index junction store root receives no bytes")


def test_assignment_battery(root: Path) -> None:
    error_types = (amod.AssignmentError,)
    valid_root = root / "assignment-valid"
    value = base_assignment("task-valid")
    persisted = amod.persist_assignment(valid_root, value)
    loaded = amod.load_assignment(valid_root, value["task_id"], value["assignment_digest"])
    check(persisted.is_file() and loaded == value, "valid assignment persists and loads")
    validated = False
    try:
        amod.validate_assignment(loaded, require_source_evidence=True)
        validated = True
    except amod.AssignmentError:
        validated = False
    check(validated, "valid assignment validates after durable load")
    forged_after_read = valid_root / "forged-after-read.json"
    forged_after_read.write_text('{"forged":true}\n', encoding="utf-8")
    original_read = amod.jsonl_durable.read_durable_bytes

    def swap_after_authoritative_read(path: Path, **kwargs):
        raw = original_read(path, **kwargs)
        if Path(path) == persisted:
            persisted.unlink()
            make_link(persisted, forged_after_read, directory=False)
        return raw

    amod.jsonl_durable.read_durable_bytes = swap_after_authoritative_read
    try:
        loaded_after_swap = amod.load_assignment(
            valid_root, value["task_id"], value["assignment_digest"]
        )
    finally:
        amod.jsonl_durable.read_durable_bytes = original_read
    check(loaded_after_swap == value, "load_assignment uses the atomically read authority bytes")
    persisted.unlink(missing_ok=True)

    load_hardlink_root = root / "assignment-load-hardlink"
    load_task = load_hardlink_root / value["task_id"]
    load_task.mkdir(parents=True)
    load_outside = load_hardlink_root / "outside.json"
    load_original = outside_sentinel(load_outside)
    load_leaf = load_task / f"{value['assignment_digest']}.json"
    make_link(load_leaf, load_outside, directory=False)
    check(amod.load_assignment(
        load_hardlink_root, value["task_id"], value["assignment_digest"]
    ) is None, "load_assignment refuses a pre-existing hardlinked leaf")
    check(load_outside.read_bytes() == load_original, "assignment load hardlink leaves outside untouched")

    load_leaf_root = root / "assignment-load-junction-leaf"
    load_leaf_task = load_leaf_root / value["task_id"]
    load_leaf_task.mkdir(parents=True)
    load_leaf_target = load_leaf_root / "outside-target.json"
    load_leaf_original = json.dumps(value, sort_keys=True).encode("utf-8")
    load_leaf_target.write_bytes(load_leaf_original)
    make_link(load_leaf_task / f"{value['assignment_digest']}.json", load_leaf_target,
              directory=False, reparse=True)
    check(amod.load_assignment(
        load_leaf_root, value["task_id"], value["assignment_digest"]
    ) is None, "load_assignment refuses a junction/reparse leaf")
    check(load_leaf_target.read_bytes() == load_leaf_original,
          "load_assignment reparse leaf leaves the target untouched")

    load_ancestor_root = root / "assignment-load-junction-ancestor"
    load_ancestor_target = load_ancestor_root / "outside-target"
    load_ancestor_target.mkdir(parents=True)
    make_link(load_ancestor_root / "store", load_ancestor_target, directory=True)
    check(amod.load_assignment(
        load_ancestor_root / "store", value["task_id"], value["assignment_digest"]
    ) is None, "load_assignment refuses a junction/reparse ancestor")

    load_root_link = root / "assignment-load-junction-root"
    load_root_target = root / "assignment-load-root-outside"
    load_root_target.mkdir()
    make_link(load_root_link, load_root_target, directory=True)
    check(amod.load_assignment(
        load_root_link, value["task_id"], value["assignment_digest"]
    ) is None, "load_assignment refuses a junction/reparse store root")

    for field, bad in {
        "schema_version": True, "task_id": [], "role": 1, "source_repository": [],
        "source_branch": [], "source_sha": 7, "engine": [], "provider": [],
        "capacity_pool": [], "billing_basis": 1, "metered_approved": 1,
        "model": [], "model_parameters": [], "host": [], "sandbox_profile": [],
        "network_profile": [], "allowed_paths": [1], "gate_digest": [],
        "publication_policy": [], "default_branch": [], "integration_branch": [],
        "created_at": 1, "source_evidence": [],
    }.items():
        forged = copy.deepcopy(value)
        forged[field] = bad
        forged["assignment_digest"] = amod.canonical_digest(forged)
        expect_refusal(lambda forged=forged: amod.validate_assignment(
            forged, require_source_evidence=True
        ), f"assignment constructor/validator rejects typed {field}", error_types)

    constructor_args = {
        "task_id": value["task_id"], "project_id": value["project_id"], "role": value["role"],
        "source_repository": value["source_repository"], "source_branch": value["source_branch"],
        "source_sha": value["source_sha"], "engine": value["engine"],
        "provider": value["provider"], "host": value["host"],
        "sandbox_profile": value["sandbox_profile"], "network_profile": value["network_profile"],
        "allowed_paths": value["allowed_paths"], "publication_policy": value["publication_policy"],
        "seed_manifest_digest": value["seed_manifest_digest"], "capacity_pool": value["capacity_pool"],
        "model": value["model"], "model_parameters": value["model_parameters"],
        "gate_digest": value["gate_digest"], "source_evidence": value["source_evidence"],
        "billing_basis": value["billing_basis"], "metered_approved": value["metered_approved"],
        "default_branch": value["default_branch"], "integration_branch": value["integration_branch"],
        "created_at": value["created_at"],
    }
    for parameter, bad in {
        "task_id": [], "project_id": [], "role": 1, "source_repository": [],
        "source_branch": [], "source_sha": 7, "engine": [], "provider": [], "host": [],
        "sandbox_profile": [], "network_profile": [], "allowed_paths": [1],
        "publication_policy": [], "seed_manifest_digest": [], "capacity_pool": [],
        "model": [], "model_parameters": [], "gate_digest": [], "source_evidence": [],
        "billing_basis": 1, "metered_approved": 1, "default_branch": [],
        "integration_branch": [], "created_at": 1,
    }.items():
        bad_args = dict(constructor_args)
        bad_args[parameter] = bad
        expect_refusal(lambda bad_args=bad_args: amod.resolve_assignment(**bad_args),
                       f"assignment constructor rejects typed {parameter}", error_types)

    forged_provider = copy.deepcopy(value)
    forged_provider["provider"] = "evil-provider"
    forged_provider["assignment_digest"] = amod.canonical_digest(forged_provider)
    expect_refusal(lambda: amod.validate_assignment(forged_provider, require_source_evidence=True),
                   "assignment recomputed-digest provider forgery", error_types)

    forged_source = copy.deepcopy(value)
    forged_source["source_repository"] = "/other-repository"
    forged_source["assignment_digest"] = amod.canonical_digest(forged_source)
    expect_refusal(lambda: amod.validate_assignment(forged_source, require_source_evidence=True),
                   "assignment recomputed-digest source forgery", error_types)

    authority = root / "assignment-authority"
    pool_dir = authority / "pools"
    pool_dir.mkdir(parents=True)
    (pool_dir / "cursor-pool.json").write_text(json.dumps({
        "schema_version": 1, "id": "cursor-pool", "kind": "subscription",
        "billing_basis": "metered", "provider": "cursor",
        "quota": {"period": "weekly", "source": "declared", "limit": 10.0, "unit": "usd"},
        "on_demand": False, "roles": ["implementer"], "host_id": "gs-recursion",
    }), encoding="utf-8")
    bound = amod.resolve_assignment(
        task_id="task-bound-authority", project_id="project", role="implementer",
        source_repository="/repo", source_branch="main", source_sha="a" * 40,
        engine="cursor", provider="cursor", capacity_pool="cursor-pool",
        capacity_pool_dir=pool_dir, billing_basis="metered", metered_approved=True,
        host="gs-recursion", sandbox_profile="strict-linux", network_profile="provider-only",
        allowed_paths=["app"], publication_policy="verified-integration-only",
        created_at="2026-08-28T00:00:00Z",
    )
    forged_host = copy.deepcopy(bound)
    forged_host["host"] = "other-host"
    forged_host["assignment_digest"] = amod.canonical_digest(forged_host)
    expect_refusal(lambda: amod.validate_assignment(
        forged_host, require_source_evidence=True, capacity_pool_dir=pool_dir
    ), "assignment recomputed-digest capacity-host forgery", error_types)
    forged_role = copy.deepcopy(bound)
    forged_role["role"] = "verifier"
    forged_role["assignment_digest"] = amod.canonical_digest(forged_role)
    expect_refusal(lambda: amod.validate_assignment(
        forged_role, require_source_evidence=True, capacity_pool_dir=pool_dir
    ), "assignment recomputed-digest capacity-role forgery", error_types)

    hardlink_root = root / "assignment-record-hardlink"
    record_value = base_assignment("task-record-hardlink")
    task = hardlink_root / record_value["task_id"]
    task.mkdir(parents=True)
    outside = hardlink_root / "outside-record.json"
    original = outside_sentinel(outside)
    make_link(task / f"{record_value['assignment_digest']}.json", outside, directory=False)
    expect_refusal(lambda: amod.persist_assignment(hardlink_root, record_value),
                   "assignment pre-existing hardlinked record", error_types)
    check(outside.read_bytes() == original, "assignment hardlinked record leaves outside untouched")

    race_root = root / "assignment-record-race"
    race_value = base_assignment("task-record-race")
    race_task = race_root / race_value["task_id"]
    race_alias = race_root / "outside-record.json"
    armed = True

    def assignment_hook(stage: str) -> None:
        nonlocal armed
        if armed and stage == "pre-record-write":
            armed = False
            temps = list(race_task.glob(".*.json.*.tmp"))
            if not temps:
                temps = list(race_task.glob(".*"))
            if not temps:
                raise AssertionError("assignment hook did not observe its private record temporary")
            make_link(race_alias, temps[0], directory=False)

    previous = amod._assignment_persistence_hook
    amod._assignment_persistence_hook = assignment_hook
    try:
        expect_refusal(lambda: amod.persist_assignment(race_root, race_value),
                       "assignment post-validation record hardlink", error_types)
    finally:
        amod._assignment_persistence_hook = previous
    check(not armed and race_alias.read_bytes() == b"", "assignment record race creates no outside bytes")
    race_alias.unlink(missing_ok=True)

    output_root = root / "assignment-output"
    output_root.mkdir(parents=True)
    output = output_root / "copy.json"
    output_outside = output_root / "outside-copy.json"
    original = outside_sentinel(output_outside)
    make_link(output, output_outside, directory=False)
    expect_refusal(lambda: amod._atomic_write(output, "new\n"),
                   "assignment atomic output pre-existing hardlink", error_types)
    check(output_outside.read_bytes() == original, "assignment atomic output leaves outside untouched")

    output_race = root / "assignment-output-race"
    output_race.mkdir(parents=True)
    race_output = output_race / "copy.json"
    race_alias = output_race / "outside-copy.json"
    armed = True

    def output_hook(stage: str) -> None:
        nonlocal armed
        if armed and stage == "pre-write":
            armed = False
            temp = next(output_race.glob(".copy.json.tmp.*"))
            make_link(race_alias, temp, directory=False)

    previous = amod._assignment_persistence_hook
    amod._assignment_persistence_hook = output_hook
    try:
        expect_refusal(lambda: amod._atomic_write(race_output, "race\n"),
                       "assignment atomic output post-validation hardlink", error_types)
    finally:
        amod._assignment_persistence_hook = previous
    check(not armed and not race_output.exists(), "assignment atomic output race leaves no target")

    output_junction_leaf = root / "assignment-output-junction-leaf"
    output_junction_target = output_junction_leaf / "outside-target.json"
    output_junction_target.parent.mkdir(parents=True)
    output_junction_original = outside_sentinel(output_junction_target)
    make_link(output_junction_leaf / "copy.json", output_junction_target,
              directory=False, reparse=True)
    expect_refusal(lambda: amod._atomic_write(output_junction_leaf / "copy.json", "junction\n"),
                   "assignment atomic output junction leaf", error_types)
    check(output_junction_target.read_bytes() == output_junction_original,
          "assignment atomic output junction leaf receives no bytes")

    output_ancestor = root / "assignment-output-junction-ancestor"
    output_ancestor_target = output_ancestor / "outside-target"
    output_ancestor_target.mkdir(parents=True)
    make_link(output_ancestor / "store", output_ancestor_target, directory=True)
    expect_refusal(lambda: amod._atomic_write(output_ancestor / "store" / "copy.json", "ancestor\n"),
                   "assignment atomic output junction ancestor", error_types)
    check(not (output_ancestor_target / "copy.json").exists(),
          "assignment atomic output junction ancestor receives no bytes")

    output_root_link = root / "assignment-output-junction-root"
    output_root_target = root / "assignment-output-root-outside"
    output_root_target.mkdir()
    make_link(output_root_link, output_root_target, directory=True)
    expect_refusal(lambda: amod._atomic_write(output_root_link / "copy.json", "root\n"),
                   "assignment atomic output junction store root", error_types)
    check(not (output_root_target / "copy.json").exists(),
          "assignment atomic output junction store root receives no bytes")

    # Index and SQLite cache leaves are independently pinned and validated by the assignment
    # writer; exercise both the pre-existing hardlink and rebuild temporary paths.
    index_root = root / "assignment-index-cache"
    first = base_assignment("task-index-one")
    amod.persist_assignment(index_root, first)
    index = index_root / "index.jsonl"
    index_alias = index_root / "outside-index.jsonl"
    index_original = index.read_bytes()
    index_alias.write_bytes(index_original)
    index.unlink()
    make_link(index, index_alias, directory=False)
    expect_refusal(lambda: amod.persist_assignment(index_root, base_assignment("task-index-two")),
                   "assignment pre-existing hardlinked index leaf", error_types)
    check(index_alias.read_bytes() == index_original,
          "assignment hardlinked index remains outside-owned")

    # A normal new assignment after a clean cache proves the legitimate index/cache path.
    clean = root / "assignment-clean-cache"
    amod.persist_assignment(clean, base_assignment("task-clean-cache"))
    check(list((clean / ".jsonl-index").glob("*.sqlite3")),
          "assignment SQLite cache is durably created on the positive path")

    cache_root = root / "assignment-cache-hardlink"
    cache_value = base_assignment("task-cache-hardlink")
    amod.persist_assignment(cache_root, cache_value)
    cache_identity = f"assignment-root/{cache_value['task_id']}/index.jsonl"
    cache_file = cache_root / ".jsonl-index" / jd.index_cache_name(cache_identity)
    cache_alias = cache_root / "outside-cache.sqlite3"
    cache_original = cache_file.read_bytes()
    cache_alias.write_bytes(cache_original)
    cache_file.unlink()
    make_link(cache_file, cache_alias, directory=False)
    cache_value_two = copy.deepcopy(cache_value)
    cache_value_two["created_at"] = "2026-08-28T00:01:00Z"
    cache_value_two["assignment_digest"] = amod.canonical_digest(cache_value_two)
    expect_refusal(lambda: amod.persist_assignment(cache_root, cache_value_two),
                   "assignment pre-existing hardlinked SQLite cache", error_types)
    check(cache_alias.read_bytes() == cache_original,
          "assignment hardlinked SQLite cache remains outside-owned")

    junction_leaf = root / "assignment-junction-leaf"
    jvalue = base_assignment("task-junction-leaf")
    jtask = junction_leaf / jvalue["task_id"]
    jtarget = junction_leaf / "outside-target"
    jtarget.mkdir(parents=True)
    make_link(jtask, jtarget, directory=True)
    expect_refusal(lambda: amod.persist_assignment(junction_leaf, jvalue),
                   "assignment junction/reparse task leaf", error_types)
    check(not (jtarget / f"{jvalue['assignment_digest']}.json").exists(),
          "assignment junction task receives no bytes")

    ancestor = root / "assignment-junction-ancestor"
    atarget = ancestor / "outside-target"
    atarget.mkdir(parents=True)
    make_link(ancestor / "store", atarget, directory=True)
    avalue = base_assignment("task-junction-ancestor")
    expect_refusal(lambda: amod.persist_assignment(ancestor / "store", avalue),
                   "assignment junction/reparse ancestor", error_types)
    check(not (atarget / avalue["task_id"]).exists(), "assignment junction ancestor receives no bytes")

    root_link = root / "assignment-junction-root"
    root_target = root / "assignment-root-outside"
    root_target.mkdir()
    make_link(root_link, root_target, directory=True)
    rvalue = base_assignment("task-junction-root")
    expect_refusal(lambda: amod.persist_assignment(root_link, rvalue),
                   "assignment junction/reparse store root", error_types)
    check(not (root_target / rvalue["task_id"]).exists(), "assignment junction root receives no bytes")


def test_worker_battery(root: Path) -> None:
    error_types = (worker.WorkerEvidenceError,)
    valid = root / "worker-valid" / "run.json"
    worker.atomic(valid, {"id": "normal", "status": "running"})
    check(json.loads(valid.read_text(encoding="utf-8"))["id"] == "normal",
          "worker evidence normal publish succeeds")

    load_root = root / "worker-load"
    load_assignment = base_assignment("task-worker-load")
    amod.persist_assignment(load_root / "assignments", load_assignment)
    load_run = load_root / "runs" / "run.json"
    load_projection = amod.assignment_projection(load_assignment)
    load_value = {
        "schema_version": 1, "id": "run-worker-load", "task_id": load_assignment["task_id"],
        "worker": "implementer:sonnet-routine", "worktree": "/tmp/wt",
        "base_commit": load_assignment["source_sha"], "pid": 1, "process_group": 1,
        "lease_expires": "2026-08-28T00:10:00Z", "deadline": "2026-08-28T00:10:00Z",
        "usage": {}, "result": {}, "status": "running",
        "assignment_digest": load_assignment["assignment_digest"],
        "assignment": copy.deepcopy(load_projection),
    }
    load_value.update(copy.deepcopy(load_projection))
    worker.atomic(load_run, load_value)
    check(worker.load(load_run) == load_value,
          "worker.load validates and returns a valid assignment-bound run")
    for label, bad in (("verified-int", 1), ("schema-version-float", 1.0)):
        forged = copy.deepcopy(load_value)
        if label == "schema-version-float":
            # Keep the top-level run field valid so this case reaches the nested
            # projection comparator instead of being rejected by run_contract.
            forged["assignment"]["schema_version"] = bad
        else:
            forged["assignment"]["source_evidence"]["verified"] = bad
            forged["source_evidence"]["verified"] = bad
        worker.atomic(load_run, forged)
        expect_refusal(lambda: worker.load(load_run),
                       f"worker.load rejects projection type laundering ({label})", error_types)
    worker.atomic(load_run, load_value)

    hardlink_root = root / "worker-hardlink"
    hardlink_root.mkdir(parents=True)
    path = hardlink_root / "run.json"
    outside = hardlink_root / "outside.json"
    original = outside_sentinel(outside)
    make_link(path, outside, directory=False)
    expect_refusal(lambda: worker.atomic(path, {"id": "pre-existing"}),
                   "worker evidence pre-existing hardlinked leaf", error_types)
    check(outside.read_bytes() == original, "worker hardlinked leaf leaves outside untouched")

    race_root = root / "worker-race"
    race_root.mkdir(parents=True)
    race_path = race_root / "run.json"
    race_alias = race_root / "outside.json"
    armed = True

    def worker_hook(stage: str) -> None:
        nonlocal armed
        if armed and stage == "pre-write":
            armed = False
            temp = next(race_root.glob(".run.json.tmp.*"))
            make_link(race_alias, temp, directory=False)

    previous = worker._atomic_publish_hook
    worker._atomic_publish_hook = worker_hook
    try:
        expect_refusal(lambda: worker.atomic(race_path, {"id": "race"}),
                       "worker evidence post-validation hardlink", error_types)
    finally:
        worker._atomic_publish_hook = previous
    check(not armed and not race_path.exists(), "worker evidence race leaves no target")

    worker_junction_leaf = root / "worker-atomic-junction-leaf"
    worker_junction_target = worker_junction_leaf / "outside-target.json"
    worker_junction_target.parent.mkdir(parents=True)
    worker_junction_original = outside_sentinel(worker_junction_target)
    make_link(worker_junction_leaf / "run.json", worker_junction_target,
              directory=False, reparse=True)
    expect_refusal(lambda: worker.atomic(worker_junction_leaf / "run.json", {"id": "junction"}),
                   "worker evidence junction leaf", error_types)
    check(worker_junction_target.read_bytes() == worker_junction_original,
          "worker evidence junction leaf receives no bytes")

    worker_ancestor = root / "worker-atomic-junction-ancestor"
    worker_ancestor_target = worker_ancestor / "outside-target"
    worker_ancestor_target.mkdir(parents=True)
    make_link(worker_ancestor / "store", worker_ancestor_target, directory=True)
    expect_refusal(lambda: worker.atomic(worker_ancestor / "store" / "run.json", {"id": "ancestor"}),
                   "worker evidence junction ancestor", error_types)
    check(not (worker_ancestor_target / "run.json").exists(),
          "worker evidence junction ancestor receives no bytes")

    worker_root_link = root / "worker-atomic-junction-root"
    worker_root_target = root / "worker-atomic-root-outside"
    worker_root_target.mkdir()
    make_link(worker_root_link, worker_root_target, directory=True)
    expect_refusal(lambda: worker.atomic(worker_root_link / "run.json", {"id": "root"}),
                   "worker evidence junction store root", error_types)
    check(not (worker_root_target / "run.json").exists(),
          "worker evidence junction store root receives no bytes")

    junction_leaf = root / "worker-junction-leaf"
    jpath = junction_leaf / "run.json"
    jtarget = junction_leaf / "outside-target.json"
    jtarget.parent.mkdir(parents=True)
    joriginal = outside_sentinel(jtarget)
    make_link(jpath, jtarget, directory=False, reparse=True)
    expect_refusal(lambda: worker.atomic(jpath, {"id": "junction"}),
                   "worker evidence junction/reparse leaf", error_types)
    check(jtarget.read_bytes() == joriginal, "worker junction leaf receives no bytes")

    ancestor = root / "worker-junction-ancestor"
    atarget = ancestor / "outside-target"
    atarget.mkdir(parents=True)
    make_link(ancestor / "store", atarget, directory=True)
    expect_refusal(lambda: worker.atomic(ancestor / "store" / "run.json", {"id": "ancestor"}),
                   "worker evidence junction/reparse ancestor", error_types)
    check(not (atarget / "run.json").exists(), "worker junction ancestor receives no bytes")

    store_root = root / "worker-junction-root"
    store_target = root / "worker-root-outside"
    store_target.mkdir()
    make_link(store_root, store_target, directory=True)
    expect_refusal(lambda: worker.atomic(store_root / "run.json", {"id": "root"}),
                   "worker evidence junction/reparse store root", error_types)
    check(not (store_target / "run.json").exists(), "worker junction root receives no bytes")


def test_capacity_pool_differential() -> None:
    schema_path = SOURCE / "schemas" / "control-plane" / "v1" / "capacity-pool-manifest.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = StrictDraft7Validator(schema)
    base = {
        "schema_version": 1, "id": "pool", "kind": "subscription",
        "billing_basis": "metered", "provider": "cursor",
        "quota": {"period": "weekly", "source": "declared", "limit": 10.0, "unit": "usd"},
        "on_demand": False,
    }
    corpus: list[dict] = [copy.deepcopy(base)]
    for key, bad_values in {
        # JSON Schema's numeric model cannot distinguish lexical 1.0 from integer 1;
        # the runtime deliberately rejects the Python float as an input-boundary type.
        "schema_version": [True, "1", 2],
        "id": ["", "bad id", 7, "pool/child", "pool\n"],
        "kind": ["", "unknown", 7, []],
        "billing_basis": ["", "unknown", 7, []],
        "provider": ["", "Cursor", "c", 7, [], "cursor\n"],
        "on_demand": [1, "false", None],
    }.items():
        for bad in bad_values:
            candidate = copy.deepcopy(base)
            candidate[key] = bad
            corpus.append(candidate)
    for required_key in ("schema_version", "id", "kind", "billing_basis", "provider", "quota", "on_demand"):
        candidate = copy.deepcopy(base)
        candidate.pop(required_key)
        corpus.append(candidate)
    candidate = copy.deepcopy(base)
    candidate["unexpected"] = True
    corpus.append(candidate)
    candidate = copy.deepcopy(base)
    candidate["quota"]["unexpected"] = True
    corpus.append(candidate)
    for key, bad_values in {
        "period": ["", "yearly", 7, []],
        "source": ["", "unknown", 7, []],
        "limit": [-1, "10", True, float("inf"), 10 ** 400],
        "unit": ["", 7, None, " "],
    }.items():
        for bad in bad_values:
            candidate = copy.deepcopy(base)
            candidate["quota"][key] = bad
            corpus.append(candidate)
    for required_key in ("period", "source"):
        candidate = copy.deepcopy(base)
        candidate["quota"].pop(required_key)
        corpus.append(candidate)
    for key, bad in {
        "roles": [[], [""], [1], "implementer"],
        "host_id": [7, [], ""],
        "fallback_policy": ["other", 7, []],
    }.items():
        candidate = copy.deepcopy(base)
        candidate[key] = bad
        corpus.append(candidate)
    for optional in (
        {"roles": None}, {"roles": ["implementer", "verifier"]}, {"host_id": " "},
        {"fallback_policy": None}, {"quota": {"period": "daily", "source": "observed"}},
    ):
        candidate = copy.deepcopy(base)
        if "quota" in optional:
            candidate["quota"] = optional["quota"]
        else:
            candidate.update(optional)
        corpus.append(candidate)

    schema_only = 0
    runtime_only = 0
    for candidate in corpus:
        schema_valid = not list(validator.iter_errors(candidate))
        pool_id = candidate.get("id") if isinstance(candidate.get("id"), str) else "pool"
        try:
            amod.validate_capacity_pool(candidate, pool_id)
        except amod.AssignmentError:
            runtime_valid = False
        except (OSError, TypeError, ValueError, OverflowError, RecursionError,
                UnicodeError, sqlite3.DatabaseError) as exc:
            runtime_valid = False
            check(False, f"capacity-pool differential leaked {type(exc).__name__}: {exc}")
        else:
            runtime_valid = True
        if schema_valid and not runtime_valid:
            schema_only += 1
            print(f"mismatch: capacity-pool schema=true runtime=false candidate={candidate!r}")
        elif runtime_valid and not schema_valid:
            runtime_only += 1
            print(f"mismatch: schema={schema_valid} runtime={runtime_valid} candidate={candidate!r}")
    check(schema_only == 0 and runtime_only == 0,
          f"capacity-pool schema/runtime differential has zero mismatches in both directions "
          f"({len(corpus)} cases; schema-only={schema_only}, runtime-only={runtime_only})")
    float_version = copy.deepcopy(base)
    float_version["schema_version"] = 1.0
    expect_refusal(lambda: amod.validate_capacity_pool(float_version, "pool"),
                   "capacity-pool runtime rejects float-for-integer schema version", (amod.AssignmentError,))


def test_run_schema_differential() -> None:
    schema_path = SOURCE / "schemas" / "control-plane" / "v1" / "schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    wrapper = {"$schema": schema["$schema"], "$defs": schema["$defs"], "$ref": "#/$defs/run"}
    validator = StrictDraft202012Validator(wrapper)
    base = {
        "schema_version": 1, "id": "run", "task_id": "task", "worker": "implementer:legacy",
        "worktree": "C:/work", "base_commit": "a" * 40, "pid": 1, "process_group": 0,
        "lease_expires": "2026-08-28T00:10:00Z", "deadline": "2026-08-28T00:10:00Z",
        "usage": {}, "result": {}, "status": "running",
    }
    corpus: list[dict] = [copy.deepcopy(base)]
    for required_key in ("schema_version", "id", "task_id", "worker", "worktree", "base_commit",
                         "pid", "lease_expires", "deadline", "usage", "result", "status"):
        candidate = copy.deepcopy(base)
        candidate.pop(required_key)
        corpus.append(candidate)
    for key, bad_values in {
        "schema_version": [True, 1.0, 2],
        "id": ["", "run\n", "bad id", 7],
        "task_id": ["", "task\n", "bad/task", None],
        "worker": ["", 7],
        "worktree": ["", None], "base_commit": ["", "a" * 40 + "\n", "not-a-sha", 7],
        "pid": [True, 1.0, -1, "1"], "process_group": [True, 0.0, -1, "0"],
        "lease_expires": ["", 7], "deadline": ["", None], "usage": [[], None],
        "result": [None, 7, True], "status": ["unknown", 7],
        "role": ["", "worker", 7], "model_alias": ["", "model\n", "A", 7],
        "network_policy": ["internet", 7],
        "assignment_digest": ["", "b" * 64 + "\n", "x", 7],
        "assignment": [[], None], "project_id": ["", "project\n", "bad/id", 7],
        "capacity_pool": ["", 7, []], "billing_basis": ["", 7], "model": ["", 7],
        "metered_approved": [1, "true"], "allowed_paths": [[], [7]],
        "engine": ["", 7], "provider": ["", 7], "host": ["", 7],
        "sandbox_profile": ["", 7], "source_repository": ["", 7],
        "source_branch": ["", 7], "source_sha": ["a" * 40 + "\n", "", 7],
        "publication_policy": ["", 7], "default_branch": ["", 7],
        "integration_branch": ["", 7],
    }.items():
        for bad in bad_values:
            candidate = copy.deepcopy(base)
            candidate[key] = bad
            corpus.append(candidate)
    bound = copy.deepcopy(base)
    bound.update({
        "assignment_digest": "b" * 64,
        "project_id": "project", "engine": "claude", "provider": "anthropic-claude-code",
        "capacity_pool": None, "billing_basis": "flat-subscription", "metered_approved": False,
        "host": "host", "model": None, "sandbox_profile": "strict-linux",
        "network_profile": "provider-only", "source_repository": "/repo", "source_branch": "main",
        "source_sha": "a" * 40, "source_evidence": {}, "allowed_paths": ["app"],
        "publication_policy": "verified-integration-only", "default_branch": "main",
        "integration_branch": "integration", "assignment": {},
    })
    corpus.append(bound)
    missing_projection = copy.deepcopy(bound)
    missing_projection.pop("provider")
    corpus.append(missing_projection)

    schema_only = 0
    runtime_only = 0
    for candidate in corpus:
        schema_valid = not list(validator.iter_errors(candidate))
        try:
            run_contract.validate_run(candidate)
        except run_contract.RunContractError:
            runtime_valid = False
        except (OSError, TypeError, ValueError, OverflowError, RecursionError, UnicodeError) as exc:
            runtime_valid = False
            check(False, f"run differential leaked {type(exc).__name__}: {exc}")
        else:
            runtime_valid = True
        if schema_valid and not runtime_valid:
            schema_only += 1
            print(f"mismatch: run schema=true runtime=false candidate={candidate!r}")
        elif runtime_valid and not schema_valid:
            runtime_only += 1
            print(f"mismatch: run schema=false runtime=true candidate={candidate!r}")
    check(schema_only == 0 and runtime_only == 0,
          f"run schema/runtime differential has zero mismatches in both directions "
          f"({len(corpus)} cases; schema-only={schema_only}, runtime-only={runtime_only})")
    nonfinite = copy.deepcopy(base)
    nonfinite["extra"] = float("nan")
    expect_refusal(lambda: run_contract.validate_run(nonfinite),
                   "run runtime rejects non-finite extension values", (run_contract.RunContractError,))


def test_quota_receipt_boundary(root: Path) -> None:
    pool_dir = root / "quota-pools"
    pool_dir.mkdir(parents=True)
    (pool_dir / "quota-pool.json").write_text(json.dumps({
        "schema_version": 1, "id": "quota-pool", "kind": "subscription",
        "billing_basis": "metered", "provider": "cursor",
        "quota": {"period": "weekly", "source": "declared", "limit": 1.0, "unit": "usd"},
        "on_demand": False,
    }), encoding="utf-8")
    ledger = root / "quota-ledger" / "ledger.jsonl"
    timestamp = usage.now_iso()
    jd.append_jsonl(ledger, {
        "schema_version": 1, "record": "run", "run_id": "receipt-run",
        "task_id": "receipt-task", "capacity_pool": "quota-pool", "provider": "cursor",
        "billing_basis": "metered", "cost_basis": "receipt", "evidence_source": "receipt-v1",
        "tokens": 10, "cost_usd": 1.5, "started_at": timestamp, "finished_at": timestamp,
    })
    args = type("QuotaArgs", (), {
        "capacity_pool_dir": str(pool_dir), "pool_id": "quota-pool",
        "ledger": str(ledger), "period": None,
    })()
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        status = usage.command_quota(args)
    report = json.loads(output.getvalue())
    check(status == 0 and report["consumed"] == 1.5 and report["status"] == "exceeded",
          "legitimate provider receipt counts and an exceeded pool reports exceeded")
    forged = {
        "schema_version": 1, "record": "run", "run_id": "forged-receipt-claim",
        "task_id": "receipt-task", "capacity_pool": "quota-pool", "provider": "cursor",
        "billing_basis": "metered", "cost_basis": "receipt",
        "evidence_source": "engine-manifest-v1", "tokens": 10, "cost_usd": 99.0,
        "started_at": timestamp, "finished_at": timestamp,
    }
    jd.append_jsonl(ledger, forged)
    with contextlib.redirect_stdout(io.StringIO()):
        forged_status = usage.command_quota(args)
    check(forged_status == 2,
          "a ledger row that forges cost_basis=receipt without a provider receipt is refused")
    args.period = "1900-W01"
    with contextlib.redirect_stdout(io.StringIO()):
        override_status = usage.command_quota(args)
    check(override_status == 2, "quota refuses an arbitrary historical period override")


def main() -> int:
    configured_root = os.environ.get("RECURSION_PHASE3_ROOT", "").strip()
    root = Path(configured_root) if configured_root else (
        Path(tempfile.gettempdir()) / f"recursion-phase3-sweep-{uuid.uuid4().hex}"
    )
    if root.exists():
        if any(root.iterdir()):
            raise SystemExit("phase3 sweep: configured root must be empty")
    else:
        root.mkdir(parents=True, exist_ok=False)
    try:
        test_jsonl_battery(root)
        test_assignment_battery(root)
        test_worker_battery(root)
        test_capacity_pool_differential()
        test_run_schema_differential()
        test_quota_receipt_boundary(root)
    except (OSError, TypeError, ValueError, OverflowError, RecursionError,
            UnicodeError, sqlite3.DatabaseError, AssertionError) as exc:
        failures.append(f"harness leaked raw {type(exc).__name__}: {exc}")
        print(f"FAIL - harness leaked raw {type(exc).__name__}: {exc}")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    if failures:
        print(f"phase3-durable-writer-sweep.test: {len(failures)} FAILED")
        return 1
    print("phase3-durable-writer-sweep.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
