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
PHASE8_HEAD_VERBS = {"pilot-plan-approve", "pilot-window-open", "pilot-window-close"}
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
    plans = []
    for path in sorted((base / "state/plans" / project).glob("*.json"))[:100]:
        value = read_json(path); value = dict(value); value["file"] = str(path.relative_to(base)); plans.append(value)
    windows = []
    for path in sorted((base / "state/pilot-windows").glob("*.json"))[:100]:
        value = read_json(path)
        if value.get("project_id") == project:
            value = dict(value); value["file"] = str(path.relative_to(base)); windows.append(value)
    assists = []
    for task_id in task_ids:
        path = base / "state/assists" / f"{task_id}.md"
        if path.is_file():
            assists.append({**fields(path), "file": str(path.relative_to(base))})
    needles = {project, *[str(item) for item in task_ids if item]}
    logs = [str(path.relative_to(base)) for path in sorted((base / "loop/logs").glob("*"))[-100:]
            if path.is_file() and any(needle in path.name for needle in needles)][-20:]
    return {"project": cfg, "pilot": pilot, "plans": plans, "goals": goals, "tasks": tasks,
            "runs": runs, "assists": assists, "pilot_windows": windows,
            "evidence": evidence, "logs": logs}


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
        if os.name != "nt":
            dfd = os.open(path.parent, os.O_RDONLY); os.fsync(dfd); os.close(dfd)
    except BaseException:
        try: os.unlink(name)
        except FileNotFoundError: pass
        raise


def atomic_json(path: Path, value: dict) -> None:
    atomic_text(path, json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def canonical_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_control_state(base: Path, kind: str, value: dict) -> None:
    proc = subprocess.run([sys.executable, str(base / "scripts/validate-control-state.py"), kind],
                          input=json.dumps(value), text=True, capture_output=True, check=False)
    if proc.returncode:
        fail((proc.stderr or proc.stdout or f"{kind} schema validation failed").strip())


def append_event(base: Path, event: str, project: str, goal: str = "", task: str = "",
                 detail: object = "", event_id: str = "") -> None:
    value = {"schema_version": 1, "ts": now_iso(), "event": event, "project": project,
             "goal": goal, "task": task, "pid": os.getpid(), "detail": detail}
    if event_id:
        value["id"] = event_id
    path = base / "state/events.jsonl"; path.parent.mkdir(parents=True, exist_ok=True)
    if event_id and path.is_file():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                if json.loads(line).get("id") == event_id:
                    return
            except (json.JSONDecodeError, AttributeError):
                continue
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode())
        os.fsync(fd)
    finally:
        os.close(fd)


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


@contextmanager
def phase8_lock(base: Path, identity: str):
    lock_dir = base / "state/.locks"; lock_dir.mkdir(parents=True, exist_ok=True)
    with (lock_dir / f"phase8-{identity}.lock").open("a+", encoding="utf-8") as lock:
        try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: fail("Phase 8 state lock is contended", 73)
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


def nonvacuous_gate(value: object, label: str) -> str:
    gate = str(value or "").strip()
    if not gate or "\n" in gate or gate in {"true", ":", "/bin/true", "exit 0"}:
        fail(f"{label} acceptance gate is absent or structurally vacuous")
    return gate


def bounded_line(value: object, label: str, maximum: int = 2000) -> str:
    text = str(value or "").strip()
    if not text or len(text) > maximum or any(ord(char) < 32 for char in text):
        fail(f"{label} must be bounded one-line text")
    return text


def validate_plan(base: Path, cfg: dict, project: str, plan_id: str, value: object) -> dict:
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        fail("pilot plan must be a schema_version 1 object")
    if len(json.dumps(value, sort_keys=True, separators=(",", ":"))) > 65536:
        fail("pilot plan exceeds the 64 KiB bound")
    if value.get("id") != plan_id or value.get("project_id") != project or not IDENT.fullmatch(plan_id):
        fail("pilot plan identity does not match its decision")
    goal = value.get("goal")
    tasks = value.get("tasks")
    if not isinstance(goal, dict) or not isinstance(tasks, list) or not 1 <= len(tasks) <= 16:
        fail("pilot plan needs one goal and 1..16 tasks")
    goal_id = str(goal.get("id") or "")
    if not IDENT.fullmatch(goal_id):
        fail("pilot plan goal identity, outcome, or falsifier is absent")
    bounded_line(goal.get("outcome"), "goal outcome"); bounded_line(goal.get("falsifier"), "goal falsifier")
    nonvacuous_gate(goal.get("acceptance_suite"), "goal")
    budget = goal.get("budget")
    required_budget = {
        "max_concurrency", "max_tokens", "max_cost_usd", "max_wall_clock_seconds",
        "max_task_attempts", "max_failures", "max_review_queue", "max_publish_attempts",
        "publication_required",
    }
    if not isinstance(budget, dict) or not required_budget <= budget.keys():
        fail("pilot plan goal budget is incomplete")
    integer_budget = required_budget - {"max_cost_usd", "publication_required"}
    if any(isinstance(budget.get(key), bool) or not isinstance(budget.get(key), int)
           or int(budget[key]) < 0 for key in integer_budget):
        fail("pilot plan has an invalid integer budget")
    cost = budget.get("max_cost_usd")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or cost < 0 \
            or not isinstance(budget.get("publication_required"), bool):
        fail("pilot plan has an invalid cost or publication budget")
    task_ids: list[str] = []
    for task in tasks:
        if not isinstance(task, dict): fail("pilot plan task is not an object")
        task_id = str(task.get("id") or "")
        if not IDENT.fullmatch(task_id) or task_id in task_ids: fail("pilot plan task id is invalid or duplicate")
        task_ids.append(task_id)
    task_id_set = set(task_ids)
    edges: dict[str, list[str]] = {}
    for task in tasks:
        task_id = str(task["id"]); deps = task.get("dependencies")
        paths = task.get("allowed_paths"); non_goals = task.get("non_goals")
        bounded_line(task.get("intent"), f"task {task_id} intent")
        if not isinstance(deps, list) \
                or len(deps) != len(set(deps)) or any(dep not in task_id_set or dep == task_id for dep in deps):
            fail(f"pilot plan task {task_id} has invalid intent or dependencies")
        if not isinstance(paths, list) or not paths or any(not isinstance(path, str) or not scope_allowed(cfg, path)
                                                          for path in paths):
            fail(f"pilot plan task {task_id} escapes the project charter")
        for path in paths: bounded_line(path, f"task {task_id} allowed path", 512)
        if not isinstance(non_goals, list) or not all(isinstance(item, str) for item in non_goals) \
                or not {"credentials", "merge", "deploy"} <= set(non_goals):
            fail(f"pilot plan task {task_id} lacks required non-goals")
        for item in non_goals: bounded_line(item, f"task {task_id} non-goal", 512)
        nonvacuous_gate(task.get("acceptance"), f"task {task_id}")
        required = {
            "worker_class", "engine", "model_alias", "verifier_model_alias", "deadline_seconds",
            "verifier_deadline_seconds", "network_policy", "evidence_contract", "verification",
            "expected_change", "gate_files",
        }
        if any(key not in task for key in required): fail(f"pilot plan task {task_id} is schema-incomplete")
        if task.get("model_alias") not in {"sonnet-routine", "opus-complex"} \
                or task.get("verifier_model_alias") not in {"opus-review", "opus-complex"} \
                or task.get("network_policy") not in {"provider-only", "none"} \
                or task.get("evidence_contract") != "worker-result-v1" \
                or task.get("verification") != "independent" \
                or task.get("expected_change") not in {"required", "optional"}:
            fail(f"pilot plan task {task_id} has an invalid Phase 5 policy")
        if any(isinstance(task.get(key), bool) or not isinstance(task.get(key), int) or task[key] < 1
               for key in ("deadline_seconds", "verifier_deadline_seconds")):
            fail(f"pilot plan task {task_id} has an invalid deadline")
        if not isinstance(task.get("gate_files"), list) or not all(isinstance(item, str) for item in task["gate_files"]) \
                or len(task["gate_files"]) != len(set(task["gate_files"])):
            fail(f"pilot plan task {task_id} has invalid gate files")
        for item in task["gate_files"]: bounded_line(item, f"task {task_id} gate file", 512)
        source_task_id = str(task.get("source_task_id") or "")
        if source_task_id:
            if not IDENT.fullmatch(source_task_id): fail(f"pilot plan task {task_id} has invalid source task")
            source_path = base / "state/tasks" / f"{source_task_id}.md"
            source = fields(source_path)
            source_goal_id = source.get("goal_id", "")
            try: source_goal = fields(goal_for(base, project, source_goal_id)[0])
            except SystemExit: raise
            if source.get("id") != source_task_id or source_goal.get("project_id") != project \
                    or source.get("status") not in {"proposed", "ready", "queued"}:
                fail(f"pilot plan source task {source_task_id} is absent, terminal, or cross-project")
            if task.get("acceptance") != source.get("acceptance"):
                fail(f"pilot plan task {task_id} changed its source task machine gate")
            source_paths = {item for item in source.get("allowed_paths", "").replace(",", " ").split() if item}
            if not set(paths) <= source_paths:
                fail(f"pilot plan task {task_id} broadens its source task write scope")
        edges[task_id] = list(deps)
    visiting: set[str] = set(); visited: set[str] = set()
    def walk(task_id: str) -> None:
        if task_id in visiting: fail("pilot plan dependency graph contains a cycle")
        if task_id in visited: return
        visiting.add(task_id)
        for dep in edges[task_id]: walk(dep)
        visiting.remove(task_id); visited.add(task_id)
    for task_id in task_ids: walk(task_id)
    return value


def instruction_path(base: Path, instruction_id: str) -> Path:
    name = f"{int(instruction_id):08d}.md" if instruction_id.isdigit() else f"{instruction_id}.md"
    return base / "state/instructions" / name


def require_lucas_instruction(path: Path, instruction: dict[str, str], terms: list[str]) -> None:
    allowed = {item.strip() for item in os.environ.get("RECURSION_INTAKE_ALLOW", "8913126684").split(",")}
    if instruction.get("principal") not in allowed or instruction.get("routing_target") != "head-hermes":
        fail("Phase 8 approval is not an authenticated Lucas-to-Head-Hermes instruction")
    body = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
    if any(term not in body for term in terms):
        fail("Lucas instruction does not name the exact Phase 8 object and digest/window bounds")


def propose_plan(base: Path, cfg: dict, pilot: dict, decision: dict, instruction_id: str) -> dict:
    args = decision.get("args") or decision.get("arguments") or []
    plan_id = str(args[1]) if len(args) > 1 else ""
    plan = validate_plan(base, cfg, str(cfg["id"]), plan_id, decision.get("plan"))
    digest = canonical_digest(plan); goal_id = str(plan["goal"]["id"])
    path = base / "state/plans" / str(cfg["id"]) / f"{plan_id}.json"
    with phase8_lock(base, plan_id):
        if path.exists():
            prior = read_json(path)
            if prior.get("plan_digest") != digest or prior.get("instruction_id") != instruction_id:
                fail("pilot plan id collides with different content or instruction")
            append_event(base, "pilot-plan-proposed", str(cfg["id"]), goal_id,
                         detail={"plan_id": plan_id, "plan_digest": digest, "instruction_id": instruction_id},
                         event_id="source-plan-proposed-" + digest[:24])
            return {"plan": str(path.relative_to(base)), "status": prior.get("status"), "plan_digest": digest}
        for goal_path in (base / "state/goals").glob("*.md"):
            if fields(goal_path).get("id") == goal_id: fail("fresh pilot plan reuses an existing goal id")
        existing_tasks = {fields(task_path).get("id") for task_path in (base / "state/tasks").glob("*.md")}
        if any(task.get("id") in existing_tasks for task in plan["tasks"]):
            fail("fresh pilot plan reuses an existing task id")
        record = {"schema_version": 1, "id": plan_id, "project_id": cfg["id"],
                  "pilot_id": pilot["id"], "instruction_id": instruction_id,
                  "plan_digest": digest, "plan": plan, "status": "proposed", "proposed_at": now_iso()}
        validate_control_state(base, "plan", record)
        atomic_json(path, record)
        append_event(base, "pilot-plan-proposed", str(cfg["id"]), goal_id,
                     detail={"plan_id": plan_id, "plan_digest": digest, "instruction_id": instruction_id},
                     event_id="source-plan-proposed-" + digest[:24])
    return {"plan": str(path.relative_to(base)), "status": "proposed", "plan_digest": digest}


def task_text(cfg: dict, pilot: dict, plan_id: str, digest: str, goal_id: str, task: dict) -> str:
    values = {
        "schema_version": "1", "version": "1", "id": task["id"], "project_id": cfg["id"],
        "project": cfg["id"], "pilot_id": pilot["id"], "goal_id": goal_id,
        "plan_id": plan_id, "plan_digest": digest, "dependencies": ",".join(task["dependencies"]),
        "goal": task["intent"], "allowed_paths": ",".join(task["allowed_paths"]),
        "non_goals": ",".join(task["non_goals"]), "worker_class": task["worker_class"],
        "engine": task["engine"], "model_alias": task["model_alias"],
        "verifier_model_alias": task["verifier_model_alias"], "deadline_seconds": str(task["deadline_seconds"]),
        "verifier_deadline_seconds": str(task["verifier_deadline_seconds"]),
        "network_policy": task["network_policy"], "evidence_contract": task["evidence_contract"],
        "verification": task["verification"], "expected_change": task["expected_change"],
        "gate_files": ",".join(task["gate_files"]), "acceptance": task["acceptance"],
        "repo": str(cfg["repo"]), "workdir": ".", "autonomy": "auto", "status": "proposed",
    }
    if task.get("source_task_id"):
        values["source_task_id"] = task["source_task_id"]
    return "".join(f"{key}: {value}\n" for key, value in values.items()) + f"\n{task['intent']}\n"


def approve_plan(base: Path, cfg: dict, pilot: dict, decision: dict, instruction_id: str,
                 instruction_file: Path, instruction: dict[str, str]) -> dict:
    args = decision.get("args") or decision.get("arguments") or []
    if len(args) != 3: fail("pilot-plan-approve needs project, plan id, and digest", 2)
    plan_id, claimed = str(args[1]), str(args[2]); require_lucas_instruction(instruction_file, instruction, [plan_id, claimed])
    path = base / "state/plans" / str(cfg["id"]) / f"{plan_id}.json"
    with phase8_lock(base, plan_id):
        proposal = read_json(path)
        if proposal.get("project_id") != cfg["id"] or proposal.get("plan_digest") != claimed:
            fail("Lucas approval digest does not match the stored plan")
        plan = validate_plan(base, cfg, str(cfg["id"]), plan_id, proposal.get("plan"))
        digest = canonical_digest(plan)
        if digest != claimed: fail("stored plan bytes do not match the approved digest")
        goal = plan["goal"]; goal_id = str(goal["id"]); goal_path = base / "state/goals" / f"{goal_id}.md"
        if proposal.get("status") == "approved":
            if proposal.get("approval_instruction_id") != instruction_id or not goal_path.is_file():
                fail("approved plan projection is incomplete or approval identity changed")
            append_event(base, "pilot-plan-approved", str(cfg["id"]), goal_id,
                         detail={"plan_id": plan_id, "plan_digest": digest, "instruction_id": instruction_id},
                         event_id="source-plan-approved-" + digest[:24])
            return {"plan": str(path.relative_to(base)), "status": "approved", "plan_digest": digest}
        if proposal.get("status") != "proposed": fail("pilot plan is not approvable")
        if goal_path.exists():
            existing = fields(goal_path)
            if existing.get("plan_id") != plan_id or existing.get("plan_digest") != digest:
                fail("goal materialization collides with unrelated state")
        else:
            goal_body = (f"schema_version: 1\nversion: 1\nid: {goal_id}\nproject_id: {cfg['id']}\n"
                         f"pilot_id: {pilot['id']}\nplan_id: {plan_id}\nplan_digest: {digest}\n"
                         f"instruction_id: {proposal['instruction_id']}\nstatus: draft\noutcome: {goal['outcome']}\n"
                         f"acceptance_suite: {goal['acceptance_suite']}\nfalsifier: {goal['falsifier']}\n"
                         f"budget: {json.dumps(goal['budget'], sort_keys=True, separators=(',', ':'))}\n"
                         f"started_at_epoch: {int(time.time())}\nterminal_reported: 0\n")
            atomic_text(goal_path, goal_body)
        for task in plan["tasks"]:
            task_path = base / "state/tasks" / f"{task['id']}.md"
            if task_path.exists():
                existing = fields(task_path)
                if existing.get("plan_id") != plan_id or existing.get("plan_digest") != digest:
                    fail("task materialization collides with unrelated state")
            else:
                atomic_text(task_path, task_text(cfg, pilot, plan_id, digest, goal_id, task))
        goal_fields = fields(goal_path)
        if goal_fields.get("status") == "draft":
            atomic_text(goal_path, goal_path.read_text(encoding="utf-8").replace("status: draft", "status: active", 1))
        proposal = dict(proposal); proposal.update({"status": "approved", "approval_instruction_id": instruction_id,
                                                    "approved_by": instruction.get("principal"), "approved_at": now_iso()})
        validate_control_state(base, "plan", proposal)
        atomic_json(path, proposal)
        append_event(base, "pilot-plan-approved", str(cfg["id"]), goal_id,
                     detail={"plan_id": plan_id, "plan_digest": digest, "instruction_id": instruction_id},
                     event_id="source-plan-approved-" + digest[:24])
    return {"plan": str(path.relative_to(base)), "status": "approved", "plan_digest": digest}


def window_action(base: Path, cfg: dict, pilot: dict, decision: dict, instruction_id: str,
                  instruction_file: Path, instruction: dict[str, str]) -> dict:
    args = decision.get("args") or decision.get("arguments") or []; verb = str(decision.get("verb") or "")
    if verb == "pilot-window-open":
        if len(args) != 4: fail("pilot-window-open needs project, goal, window, and seconds", 2)
        goal_id, window_id, raw_seconds = map(str, args[1:4])
        if not (base / "state/PAUSE").is_file(): fail("a pilot window may be authorized only while PAUSE is observed")
        if not IDENT.fullmatch(window_id) or not raw_seconds.isdigit() or not 1 <= int(raw_seconds) <= 86400:
            fail("pilot window identity or duration is invalid")
        require_lucas_instruction(instruction_file, instruction, [goal_id, window_id, raw_seconds])
        goal = fields(goal_for(base, str(cfg["id"]), goal_id)[0]); plan_id = goal.get("plan_id", "")
        plan_path = base / "state/plans" / str(cfg["id"]) / f"{plan_id}.json"
        if not plan_id or read_json(plan_path).get("status") != "approved":
            fail("pilot window goal does not come from an approved Phase 8 plan")
        path = base / "state/pilot-windows" / f"{window_id}.json"
        with phase8_lock(base, f"window-{cfg['id']}"):
            for other in (base / "state/pilot-windows").glob("*.json"):
                value = read_json(other)
                if value.get("project_id") == cfg["id"] and value.get("status") in {"armed", "open"} and other != path:
                    fail("project already has an open pilot window")
            record = {"schema_version": 1, "id": window_id, "project_id": cfg["id"], "pilot_id": pilot["id"],
                      "goal_id": goal_id, "plan_id": plan_id, "plan_digest": goal["plan_digest"],
                      "instruction_id": instruction_id, "opened_by": instruction["principal"], "status": "armed",
                      "armed_at": now_iso(), "opened_at_epoch": int(time.time()),
                      "expires_at_epoch": int(time.time()) + int(raw_seconds),
                      "max_inflight_workers": min(int(pilot.get("concurrency_limit") or 0),
                                                  int((pilot.get("budget") or {}).get("max_inflight_workers") or 0))}
            if record["max_inflight_workers"] < 1: fail("pilot window has zero worker capacity")
            if path.exists():
                prior = read_json(path)
                if prior.get("instruction_id") == instruction_id and prior.get("goal_id") == goal_id:
                    append_event(base, "pilot-window-armed", str(cfg["id"]), goal_id,
                                 detail={"window_id": window_id, "instruction_id": instruction_id},
                                 event_id="source-window-armed-" + canonical_digest([window_id, instruction_id])[:24])
                    return prior
                fail("pilot window id collides with different authority")
            atomic_json(path, record)
            append_event(base, "pilot-window-armed", str(cfg["id"]), goal_id,
                         detail={"window_id": window_id, "instruction_id": instruction_id},
                         event_id="source-window-armed-" + canonical_digest([window_id, instruction_id])[:24])
        return record
    if len(args) != 2: fail("pilot-window-close needs project and window", 2)
    window_id = str(args[1]); require_lucas_instruction(instruction_file, instruction, [window_id])
    path = base / "state/pilot-windows" / f"{window_id}.json"
    with phase8_lock(base, f"window-{cfg['id']}"):
        record = read_json(path)
        if record.get("project_id") != cfg["id"]: fail("pilot window is outside this project")
        if record.get("status") == "closed":
            append_event(base, "pilot-window-closed", str(cfg["id"]), str(record.get("goal_id") or ""),
                         detail={"window_id": window_id, "instruction_id": instruction_id},
                         event_id="source-window-close-" + canonical_digest([window_id, instruction_id])[:24])
            return record
        record.update({"status": "closed", "closed_at": now_iso(), "close_reason": "lucas-instruction",
                       "close_instruction_id": instruction_id})
        atomic_json(path, record)
        append_event(base, "pilot-window-closed", str(cfg["id"]), str(record.get("goal_id") or ""),
                     detail={"window_id": window_id, "instruction_id": instruction_id},
                     event_id="source-window-close-" + canonical_digest([window_id, instruction_id])[:24])
    return record


def execute(base: Path, decision_path: Path) -> dict:
    decision = read_json(decision_path); args = decision.get("args") or decision.get("arguments") or []
    project = str(decision.get("project") or (args[0] if args else "")); verb = str(decision.get("verb") or "")
    cfg, pilot, _ = records(base, project, active=True)
    pilot_authority = verb in PILOT_VERBS and decision.get("actor") == pilot["id"]
    head_authority = verb in PHASE8_HEAD_VERBS and decision.get("actor") == "head-hermes"
    if not (pilot_authority or head_authority):
        fail("decision actor or verb is outside project-pilot authority")
    if not args or args[0] != project: fail("decision target does not match its pilot")
    instruction_id = str(decision.get("instruction_id") or "")
    if not instruction_id: fail("project-pilot decision lacks topic instruction correlation")
    source_instruction = instruction_path(base, instruction_id)
    instruction = fields(source_instruction)
    if instruction.get("project_id") != project or instruction.get("pilot_id") != pilot["id"]:
        fail("instruction is not owned by this project pilot")
    if verb == "pilot-plan-propose":
        return propose_plan(base, cfg, pilot, decision, instruction_id)
    if verb == "pilot-plan-approve":
        return approve_plan(base, cfg, pilot, decision, instruction_id, source_instruction, instruction)
    if verb in {"pilot-window-open", "pilot-window-close"}:
        return window_action(base, cfg, pilot, decision, instruction_id, source_instruction, instruction)
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
    if verb in {"pilot-block", "pilot-escalate"}:
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
