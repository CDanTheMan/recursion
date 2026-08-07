#!/usr/bin/env python3
"""Bounded durable control surface for one project pilot per Telegram topic."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path


IDENT = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
PILOT_VERBS = {
    "pilot-plan-propose", "pilot-task-create", "pilot-worker-request",
    "pilot-verifier-request", "pilot-block", "pilot-escalate", "pilot-goal-verify",
}
PILOT_ROUTES = PILOT_VERBS | {"status", "context", "repo", "logs", "evidence"}
HEAD_ONLY = {
    "priority-set", "reprioritize", "portfolio-add", "register", "policy-set", "spending",
    "credentials", "deploy", "merge", "pause", "resume", "model-policy", "control-plane",
}


def root() -> Path:
    return Path(os.environ.get("RECURSION_ROOT") or Path(__file__).resolve().parent.parent)


def fail(message: str, code: int = 4) -> None:
    print(f"project-pilot: {message}", file=sys.stderr)
    raise SystemExit(code)


def compact(value: object) -> None:
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def read_json(path: Path) -> dict:
    try:
        if path.stat().st_size > 262144:
            fail(f"state record exceeds the 256 KiB read bound: {path}")
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read validated state {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"state record is not an object: {path}")
    return value


def fields(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    try:
        if path.stat().st_size > 131072:
            fail(f"state record exceeds the 128 KiB read bound: {path}")
        for line in path.read_text(encoding="utf-8", errors="surrogateescape").splitlines():
            if ":" in line and not line.startswith((" ", "\t")):
                key, value = line.split(":", 1)
                result.setdefault(key.strip(), value.strip())
    except OSError:
        pass
    return result


def rows(base: Path) -> list[dict[str, str]]:
    names = ("id", "path", "remote", "branch", "key", "roadmap", "topic", "status")
    result = []
    try:
        lines = (base / "state/portfolio.tsv").read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        fail(f"portfolio unavailable: {exc}")
    for line in lines:
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 8:
            fail(f"short portfolio row for {cols[0] if cols else '?'}")
        result.append(dict(zip(names, cols[:8])))
    return result


def row_for(base: Path, project: str) -> dict[str, str]:
    matches = [row for row in rows(base) if row["id"] == project]
    if len(matches) != 1:
        fail(f"project {project!r} is not uniquely registered")
    return matches[0]


def records(base: Path, project: str, active: bool = False) -> tuple[dict, dict, dict[str, str]]:
    row = row_for(base, project)
    cfg = read_json(base / "state/project-config" / f"{project}.json")
    pilot_id = cfg.get("pilot_id")
    if not isinstance(pilot_id, str) or not IDENT.fullmatch(pilot_id):
        fail(f"project {project} has no canonical pilot id")
    pilot = read_json(base / "state/pilots" / f"{pilot_id}.json")
    if cfg.get("id") != project or pilot.get("project_id") != project or pilot.get("id") != pilot_id:
        fail(f"project/pilot identity mismatch for {project}")
    if str(cfg.get("topic")) != row["topic"] or str(pilot.get("topic")) != row["topic"]:
        fail(f"topic projection mismatch for {project}")
    if active and (row["status"] != "active" or cfg.get("status") != "active" or pilot.get("status") != "active"):
        fail(f"project pilot {project} is not active")
    return cfg, pilot, row


def scope_allowed(cfg: dict, scope: str) -> bool:
    if not scope or scope.startswith(("/", "\\")) or ".." in Path(scope).parts:
        return False
    allowed = cfg.get("allowed_paths")
    if not isinstance(allowed, list) or not allowed:
        return False
    normalized = scope.replace("\\", "/").strip("/")
    for prefix in allowed:
        if not isinstance(prefix, str):
            continue
        prefix = prefix.replace("\\", "/").strip("/")
        if prefix == "." or normalized == prefix or normalized.startswith(prefix + "/"):
            return True
    return False


def scoped_state(base: Path, project: str) -> dict:
    cfg, pilot, _ = records(base, project, active=True)
    goals = []
    for path in sorted((base / "state/goals").glob("*.md"))[:100]:
        value = fields(path)
        if value.get("project_id") == project:
            goals.append({**value, "file": str(path.relative_to(base))})
    goal_ids = {g.get("id") for g in goals}
    tasks = []
    for path in sorted((base / "state/tasks").glob("*.md"))[:500]:
        value = fields(path)
        if value.get("project_id") == project or value.get("goal_id") in goal_ids:
            tasks.append({**value, "file": str(path.relative_to(base))})
    task_ids = {t.get("id") for t in tasks}
    runs = []
    for path in sorted((base / "state/runs").glob("*.json"))[:500]:
        value = read_json(path)
        if value.get("project_id") == project or value.get("task_id") in task_ids:
            value = dict(value); value["file"] = str(path.relative_to(base)); runs.append(value)
    evidence = []
    for path in sorted((base / "state/evidence").glob("*"))[:100]:
        if path.is_file():
            value = fields(path) if path.suffix == ".md" else read_json(path)
            if value.get("project_id") == project or value.get("task_id") in task_ids:
                evidence.append({"file": str(path.relative_to(base)), "id": value.get("id")})
    needles = {project, *[str(item) for item in task_ids if item]}
    logs = [str(path.relative_to(base)) for path in sorted((base / "loop/logs").glob("*"))[-100:]
            if path.is_file() and any(needle in path.name for needle in needles)][-20:]
    return {"project": cfg, "pilot": pilot, "goals": goals, "tasks": tasks,
            "runs": runs, "evidence": evidence, "logs": logs}


def git_evidence(cfg: dict) -> dict:
    repo = Path(str(cfg["repo"])); branch = str(cfg["default_branch"])
    def git(*args: str, timeout: int = 15) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True,
                              timeout=timeout, check=False)
    if not (repo / ".git").exists():
        return {"verified": False, "error": "clone-absent", "repo": str(repo)}
    head = git("rev-parse", "HEAD").stdout.strip()
    current = git("branch", "--show-current").stdout.strip()
    changed = [line for line in git("status", "--porcelain", "--untracked-files=all").stdout.splitlines() if line]
    env = os.environ.copy(); key = Path(os.path.expanduser(str(cfg["deploy_key_ref"])))
    if str(cfg.get("remote", "")).startswith("git@"):
        env["GIT_SSH_COMMAND"] = f"ssh -i {key} -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"
    remote = subprocess.run(["git", "ls-remote", str(cfg.get("remote") or "origin"), f"refs/heads/{branch}"],
                            text=True, capture_output=True, timeout=20, check=False, env=env)
    remote_head = remote.stdout.split()[0] if remote.returncode == 0 and remote.stdout.split() else None
    return {"verified": bool(head and current), "repo": str(repo), "branch": current, "head": head,
            "default_branch": branch, "remote_head": remote_head, "fresh": remote_head == head,
            "dirty": bool(changed), "changed_paths": changed[:20]}


def repo_read(base: Path, project: str, relative: str | None) -> dict:
    cfg, _, _ = records(base, project, active=True); repo = Path(str(cfg["repo"]))
    tracked = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, check=False)
    if tracked.returncode:
        fail("project clone or tracked-file index is unavailable")
    files = [item.decode("utf-8", "surrogateescape") for item in tracked.stdout.split(b"\0") if item]
    files = [item for item in files if scope_allowed(cfg, item) and not any(
        part == ".env" or part.startswith(".env.") for part in Path(item).parts)]
    if relative is None:
        return {"source": "live-git", "project_id": project, "files": files[:200], "truncated": len(files) > 200}
    relative = relative.replace("\\", "/").strip("/")
    if relative not in files:
        fail("repo read is untracked, secret-shaped, or outside the charter")
    path = repo / relative
    if not path.is_file() or path.stat().st_size > 65536:
        fail("repo read exceeds the 64 KiB text bound")
    raw = path.read_bytes()
    if b"\0" in raw:
        fail("repo read refuses binary content")
    return {"source": "live-git", "project_id": project, "path": relative,
            "head": subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True,
                                   capture_output=True, check=False).stdout.strip(),
            "content": raw.decode("utf-8", "replace")}


def artifact_read(base: Path, project: str, kind: str, relative: str | None) -> dict:
    state = scoped_state(base, project)
    allowed = state["logs"] if kind == "logs" else [row["file"] for row in state["evidence"]]
    if relative is None:
        return {"source": "live-control-state", "project_id": project, kind: allowed}
    relative = relative.replace("\\", "/").strip("/")
    if relative not in allowed:
        fail(f"{kind} read is outside this project")
    path = base / relative; raw = path.read_bytes()[-65536:]
    if b"\0" in raw: fail(f"{kind} read refuses binary content")
    lines = raw.decode("utf-8", "replace").splitlines()[-200:]
    return {"source": "live-control-state", "project_id": project, "path": relative,
            "content": "\n".join(lines), "truncated": path.stat().st_size > len(raw) or len(lines) == 200}


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
            out.write(text); out.flush(); os.fsync(out.fileno())
        os.replace(name, path)
        dfd = os.open(path.parent, os.O_RDONLY); os.fsync(dfd); os.close(dfd)
    except BaseException:
        try: os.unlink(name)
        except FileNotFoundError: pass
        raise


def atomic_json(path: Path, value: dict) -> None:
    atomic_text(path, json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


@contextmanager
def registry_lock(base: Path):
    lock_dir = base / "state/.locks"; lock_dir.mkdir(parents=True, exist_ok=True)
    with (lock_dir / "project-registry.lock").open("a+", encoding="utf-8") as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: fail("project registry lock is contended", 73)
        yield


@contextmanager
def goal_state_lock(base: Path, goal_id: str):
    """Serialize Phase 4 task creation with Phase 6 goal verification/transitions."""
    lock_dir = base / "state/.locks"; lock_dir.mkdir(parents=True, exist_ok=True)
    with (lock_dir / f"reconcile-{goal_id}.lock").open("a+", encoding="utf-8") as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: fail("goal state lock is contended", 73)
        yield


def verify_registry(base: Path) -> None:
    seen: dict[str, set[str]] = {key: set() for key in ("topic", "pilot", "memory", "worktree")}
    for row in rows(base):
        if row["status"] != "active":
            continue
        cfg, pilot, _ = records(base, row["id"], active=True)
        required = {"charter": cfg.get("charter"), "gate": cfg.get("activation_gate"),
                    "model": pilot.get("model_policy"), "budget": pilot.get("budget"),
                    "notifications": pilot.get("notification_targets"), "goal_source": pilot.get("goal_source")}
        if any(value in (None, "", [], {}) for value in required.values()):
            fail(f"active project {row['id']} lacks Phase 4 metadata")
        values = {"topic": str(cfg["topic"]), "pilot": str(pilot["id"]),
                  "memory": str(pilot.get("memory_key", "")), "worktree": str(pilot.get("worktree_root", ""))}
        if not values["topic"].isdigit() or int(values["topic"]) < 1:
            fail(f"active project {row['id']} has no Telegram topic")
        for kind, value in values.items():
            if not value or value in seen[kind]: fail(f"active projects share {kind} {value!r}")
            seen[kind].add(value)


def prepare(base: Path, project: str, remote: str, charter: str) -> None:
    if not IDENT.fullmatch(project) or not charter.strip(): fail("pending registration needs a project id and charter", 2)
    if not (remote.startswith("git@github.com:") or remote.startswith("https://github.com/")):
        fail("pending registration remote must be GitHub", 2)
    with registry_lock(base):
        if any(row["id"] == project for row in rows(base)): fail(f"project {project} already exists", 2)
        repo = f"/opt/{project}"; key = f"~/.ssh/{project}_deploy"; pilot_id = f"pilot-{project}"
        line = f"{project}\t{repo}\t{remote}\tmain\t{key}\t-\t-\tpending\n"
        reg = base / "state/portfolio.tsv"; atomic_text(reg, reg.read_text(encoding="utf-8") + line)
        targets = ["head-hermes", "lucas-direct"]
        cfg = {"schema_version": 1, "id": project, "repo": repo, "remote": remote,
               "default_branch": "main", "deploy_key_ref": key, "charter": charter,
               "allowed_paths": ["."], "topic": "-", "pilot_id": pilot_id,
               "activation_gate": "clone-auth-freshness-v1", "notification_targets": targets,
               "goal_source": "state/goals", "status": "pending"}
        pilot = {"schema_version": 1, "id": pilot_id, "project_id": project, "topic": "-",
                 "charter": charter, "model_policy": "project-pilot", "concurrency_limit": 0,
                 "budget": {"max_inflight_workers": 0, "max_decisions_per_turn": 1},
                 "notification_targets": targets, "goal_source": "state/goals",
                 "memory_key": f"telegram-topic:pending:{project}",
                 "worktree_root": f".worktrees/{project}", "status": "pending"}
        atomic_json(base / "state/project-config" / f"{project}.json", cfg)
        atomic_json(base / "state/pilots" / f"{pilot_id}.json", pilot)


def bind_topic(base: Path, project: str, topic: str) -> None:
    if not topic.isdigit() or int(topic) < 1:
        fail("topic id must be a positive Telegram thread id", 2)
    with registry_lock(base):
        cfg, pilot, row = records(base, project)
        if row["status"] != "pending": fail("topic binding is allowed only while pending", 2)
        if any(other["topic"] == topic and other["id"] != project for other in rows(base)):
            fail(f"topic {topic} already belongs to another project")
        targets = [f"project-topic:{topic}"] + [item for item in cfg.get("notification_targets", [])
                                                if not str(item).startswith("project-topic:")]
        cfg = dict(cfg); cfg.update(topic=int(topic), notification_targets=targets)
        pilot = dict(pilot); pilot.update(topic=int(topic), memory_key=f"telegram-topic:{topic}",
                                          notification_targets=targets)
        atomic_json(base / "state/project-config" / f"{project}.json", cfg)
        atomic_json(base / "state/pilots" / f"{pilot['id']}.json", pilot)
        lines = (base / "state/portfolio.tsv").read_text(encoding="utf-8").splitlines()
        changed = 0
        for index, line in enumerate(lines):
            cols = line.split("\t")
            if len(cols) >= 8 and cols[0] == project and cols[7] == "pending":
                cols[6] = topic; lines[index] = "\t".join(cols); changed += 1
        if changed != 1: fail("pending topic compare-and-swap failed", 73)
        atomic_text(base / "state/portfolio.tsv", "\n".join(lines) + "\n")


def activate(base: Path, project: str) -> dict:
    with registry_lock(base):
        cfg, pilot, row = records(base, project)
        if row["status"] != "pending": fail(f"project {project} is not pending", 2)
        if not str(cfg.get("charter", "")).strip(): fail("project charter is absent")
        if cfg.get("activation_gate") != "clone-auth-freshness-v1": fail("activation gate is absent or unknown")
        if not row["topic"].isdigit() or int(row["topic"]) < 1:
            fail("project topic is not bound")
        if not pilot.get("model_policy") or not pilot.get("goal_source") or not pilot.get("budget"):
            fail("pilot metadata is incomplete")
        key = Path(os.path.expanduser(row["key"])); remote = row["remote"]; branch = row["branch"]
        if not key.is_file(): fail(f"deploy key is absent: {row['key']}")
        env = os.environ.copy()
        if remote.startswith("git@"):
            env["GIT_SSH_COMMAND"] = f"ssh -i {key} -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15"
        probe = subprocess.run(["git", "ls-remote", remote, f"refs/heads/{branch}"], text=True,
                               capture_output=True, timeout=25, check=False, env=env)
        if probe.returncode or not probe.stdout.split(): fail("deploy-key authentication or remote branch proof failed")
        remote_head = probe.stdout.split()[0]; repo = Path(row["path"])
        if not (repo / ".git").exists():
            repo.parent.mkdir(parents=True, exist_ok=True)
            clone = subprocess.run(["git", "clone", "-q", "--branch", branch, "--single-branch", remote, str(repo)],
                                   text=True, capture_output=True, timeout=120, check=False, env=env)
            if clone.returncode: fail("clone failed under the provisioned credential")
        origin = subprocess.run(["git", "-C", str(repo), "remote", "get-url", "origin"], text=True,
                                capture_output=True, check=False).stdout.strip()
        current = subprocess.run(["git", "-C", str(repo), "branch", "--show-current"], text=True,
                                 capture_output=True, check=False).stdout.strip()
        head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True,
                              capture_output=True, check=False).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all"],
                               text=True, capture_output=True, check=False).stdout.strip()
        if origin != remote or current != branch or head != remote_head or dirty:
            fail("clone is stale, dirty, on the wrong branch, or points at the wrong remote")
        proof = {"verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                 "clone_head": head, "remote_head": remote_head, "branch": branch,
                 "credential": "deploy-key", "gate": "clone-auth-freshness-v1"}
        cfg = dict(cfg); cfg["activation_proof"] = proof; cfg["status"] = "active"
        pilot = dict(pilot); pilot["status"] = "active"
        atomic_json(base / "state/project-config" / f"{project}.json", cfg)
        atomic_json(base / "state/pilots" / f"{pilot['id']}.json", pilot)
        lines = (base / "state/portfolio.tsv").read_text(encoding="utf-8").splitlines()
        changed = 0
        for index, line in enumerate(lines):
            cols = line.split("\t")
            if len(cols) >= 8 and cols[0] == project and cols[7] == "pending":
                cols[7] = "active"; lines[index] = "\t".join(cols); changed += 1
        if changed != 1: fail("pending registry compare-and-swap failed", 73)
        atomic_text(base / "state/portfolio.tsv", "\n".join(lines) + "\n")
        return proof


def goal_for(base: Path, project: str, goal_id: str) -> tuple[Path, dict[str, str]]:
    for path in (base / "state/goals").glob("*.md"):
        value = fields(path)
        if value.get("id") == goal_id:
            if value.get("project_id") != project or value.get("status") not in {"approved", "active"}:
                fail("goal is not approved for this project")
            acceptance = value.get("acceptance_suite", "").strip()
            if not acceptance:
                fail("approved goal has no gate")
            if acceptance in {"true", ":", "/bin/true", "exit 0"}:
                fail("approved goal gate is structurally vacuous")
            return path, value
    fail(f"goal {goal_id} is absent")


def execute(base: Path, decision_path: Path) -> dict:
    decision = read_json(decision_path); args = decision.get("args") or decision.get("arguments") or []
    project = str(decision.get("project") or (args[0] if args else "")); verb = str(decision.get("verb") or "")
    cfg, pilot, _ = records(base, project, active=True)
    if decision.get("actor") != pilot["id"] or verb not in PILOT_VERBS:
        fail("decision actor or verb is outside project-pilot authority")
    if not args or args[0] != project: fail("decision target does not match its pilot")
    instruction_id = str(decision.get("instruction_id") or "")
    if not instruction_id: fail("project-pilot decision lacks topic instruction correlation")
    name = f"{int(instruction_id):08d}.md" if instruction_id.isdigit() else f"{instruction_id}.md"
    instruction = fields(base / "state/instructions" / name)
    if instruction.get("project_id") != project or instruction.get("pilot_id") != pilot["id"]:
        fail("instruction is not owned by this project pilot")
    goal_id = str(args[1]) if len(args) > 1 else ""; goal_for(base, project, goal_id)
    if verb == "pilot-task-create":
        if len(args) < 4: fail("task creation needs project, goal, task id, and scope", 2)
        task_id, scope = str(args[2]), str(args[3])
        if not IDENT.fullmatch(task_id) or not scope_allowed(cfg, scope): fail("task is outside the charter")
        dependencies = [] if len(args) < 5 or args[4] in ("", "-") else str(args[4]).split(",")
        state = scoped_state(base, project); owned = {task.get("id") for task in state["tasks"]}
        if any(dep not in owned for dep in dependencies): fail("task dependency crosses project scope")
        text = str(decision.get("text") or "").strip()
        if not text or "\n" in text: fail("task needs bounded one-line intent")
        with goal_state_lock(base, goal_id):
            # Re-read under the same lock Phase 6 uses to enter verifying. A task creation
            # that raced that transition must lose; remembered pilot state is not authority.
            _, goal = goal_for(base, project, goal_id)
            path = base / "state/tasks" / f"{task_id}.md"
            if path.exists(): fail(f"task {task_id} already exists", 2)
            body = (f"schema_version: 1\nversion: 1\nid: {task_id}\nproject_id: {project}\npilot_id: {pilot['id']}\n"
                    f"goal_id: {goal_id}\ndependencies: {','.join(dependencies)}\nallowed_paths: {scope}\n"
                    f"non_goals: portfolio,policy,credentials,merge,deploy\nworker_class: claude\n"
                    f"engine: claude\nmodel_alias: sonnet-routine\nverifier_model_alias: opus-review\n"
                    f"deadline_seconds: 3600\nverifier_deadline_seconds: 1800\n"
                    f"network_policy: provider-only\nevidence_contract: worker-result-v1\n"
                    f"verification: independent\nexpected_change: required\ngate_files:\n"
                    f"acceptance: {goal['acceptance_suite']}\nstatus: proposed\n\n{text}\n")
            atomic_text(path, body); return {"created": str(path.relative_to(base)), "status": "proposed"}
    if verb in {"pilot-worker-request", "pilot-verifier-request", "pilot-block"}:
        if len(args) != 3:
            fail(f"{verb} needs project, goal, and task")
        task_id = str(args[2]); owned = {task.get("id") for task in scoped_state(base, project)["tasks"]}
        if task_id not in owned:
            fail("request names a task outside this project")
    if verb in {"pilot-plan-propose", "pilot-block", "pilot-escalate"}:
        text = str(decision.get("text") or "").strip()
        if not text or "\n" in text or len(text) > 500:
            fail(f"{verb} needs bounded one-line prose")
    payload = {"schema_version": 1, "id": str(decision.get("id") or ""), "actor": pilot["id"],
               "project_id": project, "goal_id": goal_id, "verb": verb, "arguments": args[2:],
               "text": decision.get("text") or "", "instruction_id": instruction_id,
               "status": "requested", "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    identity = str(decision.get("idempotency_key") or json.dumps(payload, sort_keys=True))
    name = hashlib.sha256(identity.encode()).hexdigest()[:24] + ".json"
    path = base / "state/pilot-requests" / project / name
    if not path.exists(): atomic_json(path, payload)
    return {"request": str(path.relative_to(base)), "target": "head-hermes" if verb == "pilot-escalate" else "project-pilot"}


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("verify-registry")
    for name in ("topic", "context", "status"):
        cmd = sub.add_parser(name); cmd.add_argument("value")
    repo_cmd = sub.add_parser("repo"); repo_cmd.add_argument("project"); repo_cmd.add_argument("path", nargs="?")
    for name in ("logs", "evidence"):
        cmd = sub.add_parser(name); cmd.add_argument("project"); cmd.add_argument("path", nargs="?")
    route = sub.add_parser("route"); route.add_argument("project"); route.add_argument("request"); route.add_argument("target", nargs="?")
    auth = sub.add_parser("authorize"); auth.add_argument("project"); auth.add_argument("request"); auth.add_argument("scope"); auth.add_argument("target", nargs="?")
    prep = sub.add_parser("prepare"); prep.add_argument("project"); prep.add_argument("remote"); prep.add_argument("charter")
    bind = sub.add_parser("bind-topic"); bind.add_argument("project"); bind.add_argument("topic")
    activate_cmd = sub.add_parser("activate"); activate_cmd.add_argument("project")
    execute_cmd = sub.add_parser("execute"); execute_cmd.add_argument("decision")
    args = parser.parse_args(); base = root()
    if args.command == "verify-registry": verify_registry(base); print("OK")
    elif args.command == "topic":
        matches = [row for row in rows(base) if row["topic"] == str(args.value) and row["status"] == "active"]
        if len(matches) != 1: fail(f"topic {args.value} is not bound to one active project")
        cfg, pilot, _ = records(base, matches[0]["id"], active=True); compact({"project": cfg, "pilot": pilot})
    elif args.command == "context": compact(scoped_state(base, args.value))
    elif args.command == "status":
        value = scoped_state(base, args.value); value = {"source": "live-control-state", "observed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "git": git_evidence(value["project"]), **value}
        compact(value)
    elif args.command == "repo": compact(repo_read(base, args.project, args.path))
    elif args.command in {"logs", "evidence"}: compact(artifact_read(base, args.project, args.command, args.path))
    elif args.command == "route":
        cfg, pilot, _ = records(base, args.project, active=True)
        target = "project-pilot" if args.request in PILOT_ROUTES and (not args.target or args.target == args.project) else "head-hermes"
        compact({"project_id": cfg["id"], "pilot_id": pilot["id"], "target": target, "request": args.request})
    elif args.command == "authorize":
        cfg, pilot, _ = records(base, args.project, active=True)
        if args.request not in PILOT_VERBS or (args.target and args.target != args.project) or not scope_allowed(cfg, args.scope):
            fail("request is outside the pilot charter")
        compact({"authorized": True, "pilot_id": pilot["id"], "project_id": args.project})
    elif args.command == "prepare": prepare(base, args.project, args.remote, args.charter); print("pending")
    elif args.command == "bind-topic": bind_topic(base, args.project, args.topic); print("bound")
    elif args.command == "activate": compact(activate(base, args.project))
    else: compact(execute(base, Path(args.decision)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
