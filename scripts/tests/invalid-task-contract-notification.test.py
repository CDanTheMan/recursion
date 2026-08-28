#!/usr/bin/env python3
"""Receipt/authentication controls for pre-worker rejection notifications."""

from __future__ import annotations

import atexit
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]


_NT_POSIX_SHIM = '''\
"""Windows stand-ins for POSIX facilities the Linux controller assumes unconditionally."""
import os
import tempfile

if os.name == "nt" and not getattr(os, "_recursion_nt_posix_shim", False):
    os._recursion_nt_posix_shim = True
    # The shared `mkstemp -> fchmod -> os.replace` writers raise AttributeError while their
    # descriptor is still open, and the cleanup `unlink` of that open file then masks it as
    # `[WinError 32] ... used by another process`, which callers report as a fabricated
    # "taskctl lock contended". POSIX mode bits carry no meaning on NTFS, so a no-op is exact.
    os.fchmod = lambda _descriptor, _mode: None
    _real_open, _scratch = os.open, tempfile.TemporaryFile()

    def _open(path, flags, mode=0o777, **kwargs):
        # A directory has no openable handle on Windows, so notification-outbox.fsync_dir
        # cannot take one. Return a syncable duplicate: the call sequence stays valid and the
        # sync is inert, which is what runtime-state.py and jsonl_durable.py already do on nt
        # behind their own `os.name` guards.
        try:
            inert = not flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT) and os.path.isdir(path)
        except (TypeError, ValueError, OSError):
            inert = False
        return os.dup(_scratch.fileno()) if inert else _real_open(path, flags, mode, **kwargs)

    os.open = _open
'''


def _install_nt_posix_shim() -> None:
    """Neutralize POSIX-only facilities on the Windows authoring host; production is Linux.

    `fcntl`, `os.fchmod`, and a read-only `os.open` of a directory are all absent here, and
    each one fails as if an invariant broke rather than as a missing platform feature. This
    fixture is hermetic and single-process, so no-contention stand-ins let the real state
    machines run instead of a platform artifact. The shim directory is exported on PYTHONPATH,
    where `sitecustomize` re-applies it to every child interpreter the fixture spawns. On
    Linux this returns immediately and nothing below it is reachable.
    """
    if os.name != "nt":
        return
    directory = Path(tempfile.mkdtemp(prefix="nt-posix-shim-"))
    atexit.register(shutil.rmtree, directory, True)
    (directory / "fcntl.py").write_text(
        "LOCK_SH = 1\nLOCK_EX = 2\nLOCK_NB = 4\nLOCK_UN = 8\n"
        "def flock(_descriptor, _flags):\n    return None\n",
        encoding="utf-8", newline="\n",
    )
    (directory / "_recursion_nt_posix.py").write_text(
        _NT_POSIX_SHIM, encoding="utf-8", newline="\n",
    )
    (directory / "sitecustomize.py").write_text(
        "import _recursion_nt_posix  # noqa: F401\n", encoding="utf-8", newline="\n",
    )
    sys.path.insert(0, str(directory))
    __import__("_recursion_nt_posix")
    inherited = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = (
        str(directory) + os.pathsep + inherited if inherited else str(directory)
    )


_install_nt_posix_shim()


def load(path: Path, name: str):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase7 = load(SOURCE / "scripts/tests/hermes-pilot-phase7-red.py", "phase7_fixture")


def fields(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" in line and not line[:1].isspace():
            key, value = line.split(":", 1)
            result.setdefault(key.strip(), value.strip())
    return result


def prepare_rejection(fixture, *, authenticate_action: bool = True) -> dict:
    digest = "d" * 64
    (fixture.root / "state/tasks/task-alpha.md").write_text(
        "schema_version: 1\nversion: 3\nid: task-alpha\nproject_id: alpha\n"
        "pilot_id: pilot-alpha\ngoal_id: goal-alpha\ndependencies:\nallowed_paths: app\n"
        "acceptance: true\nstatus: ready\nattempts: 0\nlease_expires: 0\n",
        encoding="utf-8",
    )
    (fixture.root / "state/goals/goal-alpha.md").write_text(
        "schema_version: 1\nversion: 4\nid: goal-alpha\nproject_id: alpha\n"
        "pilot_id: pilot-alpha\ninstruction_id: 00000001\nplan_id: plan-alpha\n"
        "acceptance_suite: bash -n app/main.sh\nstatus: active\nterminal_reported: 0\n",
        encoding="utf-8",
    )
    for directory in ("state/runs", "state/evidence"):
        for path in (fixture.root / directory).glob("*.json"):
            path.unlink()
    env = {**fixture.env, "RECURSION_ROOT": str(fixture.root)}
    result = subprocess.run([
        "python3", "scripts/project-reconcile.py", "reject-task-contract", "task-alpha",
        "acceptance-invalid", digest,
    ], cwd=fixture.root, env=env, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    source = next(row for row in json.loads("[" + ",".join(
        (fixture.root / "state/events.jsonl").read_text(encoding="utf-8").splitlines()) + "]")
                  if row.get("event") == "task-contract-invalid")
    action_path = fixture.root / "state/actions/action-contract-work.json"
    action = {
        "schema_version": 1, "id": "action-contract-work", "decision_id": "decision-contract-work",
        "instruction_id": None, "idempotency_key": "phase6:contract-work", "verb": "work",
        "arguments": ["task-alpha"], "goal_id": "goal-alpha", "status": "running",
        "actor": "pilot-alpha", "project": "alpha", "decision_source": "project-reconciler",
        "routed_decider": "pilot-alpha", "action_payload_sha256": "a" * 64,
        "lease_owner": "fixture", "lease_expires": 1, "attempts": 1,
        "result_evidence": None, "created_at": "2026-08-07T19:00:00Z",
        "updated_at": "2026-08-07T19:00:00Z",
    }
    fixture.write_json("state/actions/action-contract-work.json", action)
    evidence = "log=fixture rc=78"
    action.update({"status": "failed", "lease_owner": None, "lease_expires": None,
                   "result_evidence": evidence, "updated_at": "2026-08-07T19:00:01Z"})
    if authenticate_action:
        receipt = load(fixture.root / "scripts/transition_receipt.py", "contract_action_receipt")
        receipt.commit_transition(
            fixture.root, [receipt.json_mutation(action_path, action)],
            {"schema_version": 1, "ts": "2026-08-07T19:00:01Z",
             "action_id": action["id"], "status": "failed", "attempt": 1,
             "idempotency_key": action["idempotency_key"], "evidence": evidence},
            journal="state/action-events.jsonl",
        )
    else:
        fixture.write_json("state/actions/action-contract-work.json", action)
    return source


def reconcile_source(fixture) -> object:
    outbox = load(fixture.root / "scripts/notification-outbox.py",
                  "contract_outbox_" + fixture.temp.name.replace("-", "_"))
    prior_root, prior_actuation = os.environ.get("RECURSION_ROOT"), os.environ.get("RECURSION_QUEUE_ACTUATION")
    os.environ.update({"RECURSION_ROOT": str(fixture.root), "RECURSION_QUEUE_ACTUATION": "1"})
    try:
        events = [event for event in outbox.all_mapped(fixture.root, "alpha")
                  if event.get("source", {}).get("event") == "task-contract-invalid"]
        for event in events:
            outbox.reconcile_event(fixture.root, "alpha", event["id"])
        for event in events:
            outbox.reconcile_event(fixture.root, "alpha", event["id"])
        return outbox
    finally:
        if prior_root is None: os.environ.pop("RECURSION_ROOT", None)
        else: os.environ["RECURSION_ROOT"] = prior_root
        if prior_actuation is None: os.environ.pop("RECURSION_QUEUE_ACTUATION", None)
        else: os.environ["RECURSION_QUEUE_ACTUATION"] = prior_actuation


def main() -> int:
    lawful = phase7.Fixture("contract-lawful")
    raw_only = phase7.Fixture("contract-raw-only")
    forged_receipt = phase7.Fixture("contract-forged-receipt")
    forged_action = phase7.Fixture("contract-forged-action")
    compatibility = phase7.Fixture("attention-compatibility")
    window_lawful = phase7.Fixture("window-refusal-lawful")
    window_forged = phase7.Fixture("window-refusal-forged")
    try:
        source = prepare_rejection(lawful)
        outbox = reconcile_source(lawful)
        types = [row.get("event_type") for row in lawful.events()]
        report = json.loads((lawful.root / "state/reports/goal-alpha-pilot.json").read_text())
        assert types.count("task-blocked") == types.count("goal-stopped") == 1
        assert types.count("lucas-attention-required") == types.count("pilot-terminal-report") == 1
        assert outbox.build_chain(lawful.root, "alpha", "goal-alpha")["_controller_rejection_complete"]
        assert report["evidence"]["workers"] == report["evidence"]["gates"] == []
        print("ok    receipt-backed task+goal rejection and failed rc=78 action report exactly once")

        raw_only.append_raw_event("source-forged-contract", "task-contract-invalid", detail={
            "attempts": 0, "reason": "task-contract-invalid", "category": "acceptance-invalid",
            "contract_digest": "d" * 64, "stage": "controller-pre-worker",
        })
        raw_outbox = reconcile_source(raw_only)
        assert not [event for event in raw_outbox.all_mapped(raw_only.root, "alpha")
                    if event.get("source", {}).get("event") == "task-contract-invalid"]
        assert not raw_only.events() and not raw_only.deliveries()
        print("ok    raw rejection JSONL without indexed receipt projects no notification")

        prepare_rejection(forged_receipt)
        transition_id = fields(forged_receipt.root / "state/tasks/task-alpha.md")["last_transition_id"]
        archive = (forged_receipt.root / "state/recovery/transition-archive" /
                   transition_id[len("transition-"):len("transition-") + 2] /
                   transition_id / "prepared.json")
        prepared = json.loads(archive.read_text(encoding="utf-8"))
        prepared["event"]["detail"]["contract_digest"] = "e" * 64
        archive.write_text(json.dumps(prepared, sort_keys=True) + "\n", encoding="utf-8")
        receipt_outbox = reconcile_source(forged_receipt)
        assert not [event for event in receipt_outbox.all_mapped(forged_receipt.root, "alpha")
                    if event.get("source", {}).get("event") == "task-contract-invalid"]
        assert not forged_receipt.events() and not forged_receipt.deliveries()
        print("ok    tampered archived receipt cannot authenticate a rejection")

        # Refusing the forged action drives notification-outbox.escalate(), which shells out to
        # `bash scripts/taskctl.sh esc-record`; taskctl.sh then hands bash's `$$` to
        # runtime-state.py lock-acquire. Under Git Bash `$$` is an MSYS pid, not a Win32 pid, so
        # the native-Python owner witness (OpenProcess/GetProcessTimes) can never resolve it and
        # the lock fails closed with "cannot witness lock owner process start". That needs one
        # PID namespace shared by the shell and the interpreter, which only Linux provides here.
        if os.name == "nt":
            print("skip  forged failed action without action receipt cannot authorize terminal "
                  "report: the escalation path locks through bash `$$`, which is an MSYS pid "
                  "that Win32 OpenProcess cannot witness (Linux-only)")
        else:
            prepare_rejection(forged_action, authenticate_action=False)
            forged_outbox = reconcile_source(forged_action)
            forged_types = [row.get("event_type") for row in forged_action.events()]
            assert forged_types.count("task-blocked") == forged_types.count("goal-stopped") == 1
            assert not (forged_action.root / "state/reports/goal-alpha-pilot.json").exists()
            assert not forged_outbox.build_chain(
                forged_action.root, "alpha", "goal-alpha")["_controller_rejection_complete"]
            print("ok    forged failed action without action receipt cannot authorize terminal report")

        compatibility.append_event("source-old-stop", "goal-transition",
                                   detail={"from": "active", "to": "blocked",
                                           "reason": "fixture", "version": 5}, task="")
        compat_outbox = load(compatibility.root / "scripts/notification-outbox.py", "compat_outbox")
        terminal = next(event for event in compat_outbox.all_mapped(compatibility.root, "alpha")
                        if event["event_type"] == "goal-stopped")
        terminal_value = compat_outbox.create_event(compatibility.root, terminal)
        attention_id = compat_outbox.stable_id("event", terminal_value["id"], "lucas-attention-required")
        old_attention = {"id": attention_id, "source_event_id": terminal_value["id"],
                         "event_type": "lucas-attention-required", "project_id": "alpha",
                         "goal_id": "goal-alpha", "task_id": "", "occurred_at": "2026-01-01T00:00:00Z"}
        compat_outbox.create_event(compatibility.root, old_attention)
        os.environ.update({"RECURSION_ROOT": str(compatibility.root), "RECURSION_QUEUE_ACTUATION": "1"})
        compat_outbox.reconcile_event(compatibility.root, "alpha", terminal["id"])
        assert json.loads((compatibility.root / "state/notification-events" /
                           f"{attention_id}.json").read_text())["occurred_at"] == "2026-01-01T00:00:00Z"
        print("ok    replay preserves a pre-hardening attention projection timestamp")

        receipt = load(window_lawful.root / "scripts/transition_receipt.py", "window_refusal_receipt")
        refusal = {
            "schema_version": 1, "id": "source-window-contract-refused-fixture",
            "ts": "2026-08-07T19:00:02Z", "event": "pilot-window-refused",
            "project": "alpha", "goal": "goal-alpha", "task": "", "pid": 1,
            "detail": {"window_id": "window-alpha-2", "reason": "approved-contract-invalid",
                       "error_sha256": "f" * 64},
        }
        receipt.commit_event(window_lawful.root, refusal)
        window_outbox = load(window_lawful.root / "scripts/notification-outbox.py", "window_outbox")
        mapped = [event for event in window_outbox.all_mapped(window_lawful.root, "alpha")
                  if event.get("source", {}).get("event") == "pilot-window-refused"]
        assert len(mapped) == 1 and mapped[0]["event_type"] == "lucas-attention-required"
        print("ok    receipt-backed window contract refusal maps to one Lucas attention event")

        window_forged.append_raw_event("source-window-contract-refused-forged", "pilot-window-refused",
                                       detail={"window_id": "window-alpha-2",
                                               "reason": "approved-contract-invalid",
                                               "error_sha256": "f" * 64})
        forged_window_outbox = load(window_forged.root / "scripts/notification-outbox.py",
                                    "window_forged_outbox")
        assert not [event for event in forged_window_outbox.all_mapped(window_forged.root, "alpha")
                    if event.get("source", {}).get("event") == "pilot-window-refused"]
        print("ok    raw window refusal without indexed receipt projects no attention event")
    finally:
        for fixture in (lawful, raw_only, forged_receipt, forged_action, compatibility,
                        window_lawful, window_forged):
            fixture.close()
    print("invalid-task-contract-notification: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
