"""Operator-invoked lifecycle controller for the P2 read-only access service.

This Linux/WSL controller owns only the foreground p2_access serve process
tree that it starts. Its monotonically increasing read-service fence is an
incarnation identifier, never canonical Hermes or P1 writer authority.
"""
from __future__ import annotations

import argparse
import datetime as dt
import errno
import fcntl
import hashlib
import json
import os
import re
import select
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path


TASK_BASE = "e627cd93bac473094bc99e8fa29c8d62bae526a2"
ALLOWED_PATHS = (
    "docs/v3/construction/p2-host-lifecycle-20260914/PROGRESS.md",
    "docs/v3/construction/p2-host-lifecycle-20260914/README.md",
    "tools/construction_swarm/p2_host_lifecycle.py",
    "tools/construction_swarm/p2_windows_watchdog.ps1",
    "tools/construction_swarm/test_p2_host_lifecycle.py",
)
STATE_VERSION = 1
MAX_JSON_BYTES = 1024 * 1024
MAX_FIXTURE_BYTES = 32 * 1024 * 1024


class LifecycleRefused(RuntimeError):
    def __init__(self, code, message, **detail):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail


def _require(value, code, message, **detail):
    if not value:
        raise LifecycleRefused(code, message, **detail)


def _json_bytes(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def _strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    return json.loads(
        raw,
        object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError("non-finite JSON number")
        ),
    )


def _utc_now():
    return (
        dt.datetime.now(dt.timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _absolute_path(value, field):
    _require(
        isinstance(value, str)
        and 0 < len(value) <= 4096
        and "\x00" not in value
        and "\r" not in value
        and "\n" not in value,
        "configuration_refused",
        f"{field} is invalid",
    )
    path = Path(value)
    _require(path.is_absolute(), "configuration_refused", f"{field} must be absolute")
    return path


def _load_json(path, maximum=MAX_JSON_BYTES):
    path = Path(path)
    try:
        _require(path.is_file() and not path.is_symlink(), "input_unavailable", "JSON input is not a regular file")
        raw = path.read_bytes()
    except LifecycleRefused:
        raise
    except OSError as exc:
        raise LifecycleRefused("input_unavailable", "JSON input is unavailable") from exc
    _require(len(raw) <= maximum, "input_refused", "JSON input exceeds byte bound")
    try:
        value = _strict_json(raw)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise LifecycleRefused("input_refused", "JSON input is malformed") from exc
    _require(isinstance(value, dict), "input_refused", "JSON input must be an object")
    return value


def _atomic_write(path, value):
    path = Path(path)
    encoded = _json_bytes(value)
    _require(len(encoded) <= MAX_JSON_BYTES, "state_refused", "state exceeds byte bound")
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
        0o600,
    )
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _private_directory(path):
    path = Path(path)
    if path.exists():
        _require(path.is_dir() and not path.is_symlink(), "state_refused", "state root is unsafe")
    else:
        try:
            path.mkdir(parents=True, mode=0o700)
        except FileExistsError:
            _require(path.is_dir() and not path.is_symlink(), "state_refused", "state root is unsafe")
    os.chmod(path, 0o700)
    information = path.stat()
    _require(information.st_uid == os.getuid(), "state_refused", "state root owner differs")
    return path


def _boot_id():
    return Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii").strip()


def process_identity(pid):
    _require(type(pid) is int and pid > 1, "process_unavailable", "PID is invalid")
    try:
        raw_stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
        closing = raw_stat.rfind(")")
        _require(closing > 0, "process_unavailable", "process stat is malformed")
        fields = raw_stat[closing + 2 :].split()
        _require(len(fields) >= 20, "process_unavailable", "process stat is incomplete")
        _require(fields[0] != "Z", "process_unavailable", "process is a zombie")
        command = Path(f"/proc/{pid}/cmdline").read_bytes()
        pgid = os.getpgid(pid)
    except (FileNotFoundError, ProcessLookupError, PermissionError) as exc:
        raise LifecycleRefused("process_unavailable", "process identity is unavailable") from exc
    return {
        "pid": pid,
        "boot_id": _boot_id(),
        "start_ticks": int(fields[19]),
        "process_group": pgid,
        "cmdline_sha256": hashlib.sha256(command).hexdigest(),
    }


def identity_matches(expected):
    if not isinstance(expected, dict):
        return False
    required = {"pid", "boot_id", "start_ticks", "process_group", "cmdline_sha256"}
    if set(expected) != required:
        return False
    try:
        return process_identity(expected["pid"]) == expected
    except LifecycleRefused:
        return False


def _open_verified_pidfd(identity):
    _require(hasattr(os, "pidfd_open") and hasattr(signal, "pidfd_send_signal"),
             "platform_unavailable", "Linux pidfd support is required")
    try:
        descriptor = os.pidfd_open(identity["pid"], 0)
    except (OSError, TypeError, KeyError) as exc:
        raise LifecycleRefused("process_unavailable", "process handle is unavailable") from exc
    if not identity_matches(identity):
        os.close(descriptor)
        raise LifecycleRefused("process_unavailable", "process identity changed before handle binding")
    return descriptor


def _pidfd_alive(descriptor):
    poller = select.poll()
    poller.register(descriptor, select.POLLIN)
    return not poller.poll(0)


class CgroupDomain:
    """A cgroup-v2 ownership domain inherited by every service descendant."""

    MAX_PROCESSES = 256

    def __init__(self, delegated_root, state_root):
        root = Path(delegated_root).resolve(strict=True)
        cgroup_mount = Path("/sys/fs/cgroup")
        _require(root == cgroup_mount or cgroup_mount in root.parents,
                 "platform_unavailable", "cgroup root is outside the cgroup-v2 mount")
        _require((root / "cgroup.procs").is_file() and (root / "cgroup.events").is_file(),
                 "platform_unavailable", "delegated cgroup-v2 root is unavailable")
        name = "recursion-p2-" + hashlib.sha256(str(state_root).encode("utf-8")).hexdigest()[:20]
        self.root = root
        self.path = root / name

    def ensure(self):
        try:
            self.path.mkdir(mode=0o700)
        except FileExistsError:
            pass
        except OSError as exc:
            raise LifecycleRefused("platform_unavailable", "service cgroup cannot be created") from exc
        _require(self.path.is_dir() and not self.path.is_symlink(),
                 "state_refused", "service cgroup path is unsafe")
        for name in ("cgroup.procs", "cgroup.events", "cgroup.kill"):
            _require((self.path / name).is_file(), "platform_unavailable",
                     "service cgroup lacks required control files")
        limit = self.path / "pids.max"
        if limit.is_file():
            try:
                limit.write_text(str(self.MAX_PROCESSES), encoding="ascii")
            except OSError as exc:
                raise LifecycleRefused("platform_unavailable", "service cgroup process bound cannot be set") from exc

    def join_current(self):
        # Executed in the Popen child before exec; all later forks inherit the domain.
        (self.path / "cgroup.procs").write_text(str(os.getpid()), encoding="ascii")

    def populated(self):
        try:
            fields = dict(
                line.split(None, 1)
                for line in (self.path / "cgroup.events").read_text(encoding="ascii").splitlines()
                if line.strip()
            )
        except (OSError, ValueError) as exc:
            raise LifecycleRefused("cleanup_unknown", "service cgroup state is unavailable") from exc
        _require(fields.get("populated") in {"0", "1"},
                 "cleanup_unknown", "service cgroup populated state is invalid")
        return fields["populated"] == "1"

    def process_count(self):
        try:
            values = (self.path / "cgroup.procs").read_text(encoding="ascii").splitlines()
        except OSError as exc:
            raise LifecycleRefused("cleanup_unknown", "service cgroup membership is unavailable") from exc
        _require(len(values) <= self.MAX_PROCESSES, "cleanup_unknown", "service cgroup exceeds process bound")
        return len(values)

    def cleanup(self, timeout, process=None):
        self.ensure()
        before = self.process_count()
        kill_sent = False
        if self.populated():
            try:
                (self.path / "cgroup.kill").write_text("1", encoding="ascii")
                kill_sent = True
            except OSError as exc:
                raise LifecycleRefused("cleanup_unknown", "service cgroup kill failed") from exc
        deadline = time.monotonic() + timeout
        while self.populated() and time.monotonic() < deadline:
            if process is not None:
                process.poll()
            time.sleep(0.02)
        if process is not None:
            process.poll()
        return {
            "term_sent": False,
            "kill_sent": kill_sent,
            "quiescent": not self.populated(),
            "member_count": before,
            "ownership_domain": "cgroup_v2",
            "domain": str(self.path),
        }


class WatchdogLock:
    def __init__(self, root):
        self.root = Path(root)
        self.stream = None

    def acquire(self):
        _private_directory(self.root)
        self.stream = (self.root / "watchdog.lock").open("a+b")
        os.chmod(self.root / "watchdog.lock", 0o600)
        try:
            fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            self.stream.close()
            self.stream = None
            raise LifecycleRefused("watchdog_busy", "another lifecycle controller owns the lock") from exc

    def release(self):
        if self.stream is not None:
            fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
            self.stream.close()
            self.stream = None


class StateStore:
    def __init__(self, root):
        self.root = _private_directory(root)
        self.path = self.root / "state.json"
        self.mutex_path = self.root / "state.lock"

    def read(self):
        if not self.path.exists():
            return None
        value = _load_json(self.path)
        _require(value.get("state_version") == STATE_VERSION, "state_refused", "state version differs")
        return value

    def write(self, value, *, expected_controller=None, expected_incarnation=None):
        with self.mutex_path.open("a+b") as mutex:
            os.chmod(self.mutex_path, 0o600)
            fcntl.flock(mutex.fileno(), fcntl.LOCK_EX)
            current = self.read()
            if expected_controller is not None:
                _require(
                    current is not None
                    and current.get("controller_id") == expected_controller
                    and current.get("service_incarnation") == expected_incarnation,
                    "stale_incarnation",
                    "state writer no longer owns the current incarnation",
                )
            _atomic_write(self.path, value)

    def publish_health(self, controller_id, incarnation, service_identity, health):
        _require(
            health in {"starting", "running", "backoff", "outage", "stopping", "stopped"},
            "state_refused",
            "health value is invalid",
        )
        with self.mutex_path.open("a+b") as mutex:
            fcntl.flock(mutex.fileno(), fcntl.LOCK_EX)
            current = self.read()
            _require(
                current is not None
                and current.get("controller_id") == controller_id
                and current.get("service_incarnation") == incarnation
                and current.get("service_identity") == service_identity,
                "stale_incarnation",
                "health update belongs to an old service incarnation",
            )
            updated = dict(current)
            updated["health"] = health
            updated["unavailable"] = health != "running"
            if health == "outage" and not updated.get("outage_reason"):
                updated["outage_reason"] = "health_published_outage"
            updated["observation_time"] = _utc_now()
            _atomic_write(self.path, updated)
            return updated


def _repository_head(root):
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    _require(result.returncode == 0, "configuration_refused", "repository HEAD is unavailable")
    return result.stdout.strip()


def load_config(filename):
    value = _load_json(filename)
    expected = {
        "version",
        "enabled",
        "source_commit",
        "repository_root",
        "python_executable",
        "socket_path",
        "grants_file",
        "state_root",
        "cgroup_root",
        "pause_path",
        "restart_cap",
        "backoff_initial_seconds",
        "backoff_max_seconds",
        "startup_timeout_seconds",
        "shutdown_timeout_seconds",
    }
    _require(set(value) == expected, "configuration_refused", "lifecycle config fields differ")
    _require(value["version"] == 1, "configuration_refused", "lifecycle config version differs")
    _require(type(value["enabled"]) is bool, "configuration_refused", "enabled must be boolean")
    source = value["source_commit"]
    _require(
        isinstance(source, str) and re.fullmatch(r"[0-9a-f]{40}", source),
        "configuration_refused",
        "source commit is invalid",
    )
    for name in (
        "repository_root",
        "python_executable",
        "socket_path",
        "grants_file",
        "state_root",
        "cgroup_root",
        "pause_path",
    ):
        value[name] = str(_absolute_path(value[name], name))
    root = Path(value["repository_root"])
    python = Path(value["python_executable"])
    grants = Path(value["grants_file"])
    _require(
        root.is_dir()
        and (root / "tools/construction_swarm/p2_access.py").is_file()
        and _repository_head(root) == source,
        "configuration_refused",
        "repository source binding differs",
    )
    _require(python.is_file() and os.access(python, os.X_OK), "configuration_refused", "Python executable unavailable")
    _require(grants.is_file() and not grants.is_symlink(), "configuration_refused", "grant file unavailable")
    _require(
        type(value["restart_cap"]) is int and 0 <= value["restart_cap"] <= 10,
        "configuration_refused",
        "restart_cap is invalid",
    )
    for name in (
        "backoff_initial_seconds",
        "backoff_max_seconds",
        "startup_timeout_seconds",
        "shutdown_timeout_seconds",
    ):
        _require(
            type(value[name]) in {int, float} and 0.01 <= value[name] <= 15,
            "configuration_refused",
            f"{name} is invalid",
        )
        value[name] = float(value[name])
    _require(
        value["backoff_initial_seconds"] <= value["backoff_max_seconds"],
        "configuration_refused",
        "backoff bounds are reversed",
    )
    return value


def startup_prohibition(config):
    if not config["enabled"]:
        return "disabled"
    pause = Path(config["pause_path"])
    if pause.exists():
        _require(pause.is_file() and not pause.is_symlink(), "startup_refused", "PAUSE input is unsafe")
        return "paused"
    return None


def _socket_active(path):
    channel = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    channel.settimeout(0.2)
    try:
        channel.connect(str(path))
        return True
    except OSError as exc:
        if exc.errno in {errno.ENOENT, errno.ECONNREFUSED}:
            return False
        raise LifecycleRefused(
            "socket_unknown",
            "socket ownership could not be determined",
            errno=exc.errno,
        ) from exc
    finally:
        channel.close()


def reconcile_socket(path):
    path = Path(path)
    try:
        before = path.lstat()
    except FileNotFoundError:
        return "absent"
    _require(stat.S_ISSOCK(before.st_mode), "socket_refused", "socket path is not a socket")
    _require(not _socket_active(path), "socket_in_use", "socket is served by an unowned process")
    try:
        after = path.lstat()
    except FileNotFoundError:
        return "disappeared"
    _require(
        (before.st_dev, before.st_ino, before.st_mode)
        == (after.st_dev, after.st_ino, after.st_mode),
        "socket_refused",
        "socket changed during reconciliation",
    )
    path.unlink()
    return "stale_socket_removed"


def _fixture_counter(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="ascii") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.seek(0)
        text = stream.read().strip()
        count = int(text) if text else 0
        count += 1
        stream.seek(0)
        stream.truncate()
        stream.write(str(count))
        stream.flush()
        os.fsync(stream.fileno())
        return count


def fixture_grandchild():
    while True:
        time.sleep(1)


def fixture_child(socket_path, spec_path, incarnation):
    spec = _load_json(spec_path, MAX_FIXTURE_BYTES)
    expected = {"mode", "launch_count_path", "grandchild_pid_path", "exit_delay_seconds"}
    _require(set(spec) == expected, "fixture_refused", "fixture spec fields differ")
    _require(spec["mode"] in {"stable", "crash_once", "always_crash", "fork_then_crash_once"},
             "fixture_refused", "fixture mode differs")
    launch_count = _fixture_counter(_absolute_path(spec["launch_count_path"], "launch_count_path"))
    delay = spec["exit_delay_seconds"]
    _require(type(delay) in {int, float} and 0 <= delay <= 2, "fixture_refused", "fixture delay is invalid")
    if spec["mode"] == "fork_then_crash_once" and launch_count == 1:
        grandchild = subprocess.Popen(
            [sys.executable, "-X", "utf8", "-B", "-m",
             "tools.construction_swarm.p2_host_lifecycle", "fixture-grandchild"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        Path(spec["grandchild_pid_path"]).write_text(str(grandchild.pid), encoding="ascii")
        time.sleep(delay)
        return 23
    if spec["mode"] == "always_crash" or (spec["mode"] == "crash_once" and launch_count == 1):
        time.sleep(delay)
        return 23
    path = Path(socket_path)
    _require(not path.exists(), "fixture_refused", "fixture socket already exists")
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda _number, _frame: stop.set())
    grandchild = None
    grandchild_path = spec["grandchild_pid_path"]
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as listener:
        listener.bind(str(path))
        os.chmod(path, 0o600)
        socket_identity = path.lstat()
        listener.listen(8)
        listener.settimeout(0.1)
        if grandchild_path:
            grandchild = subprocess.Popen(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "-B",
                    "-m",
                    "tools.construction_swarm.p2_host_lifecycle",
                    "fixture-grandchild",
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
            Path(grandchild_path).write_text(str(grandchild.pid), encoding="ascii")
        try:
            while not stop.is_set():
                try:
                    connection, _ = listener.accept()
                except TimeoutError:
                    continue
                with connection:
                    connection.settimeout(0.1)
        finally:
            if grandchild is not None:
                try:
                    grandchild.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
            try:
                current = path.lstat()
                if (current.st_dev, current.st_ino) == (socket_identity.st_dev, socket_identity.st_ino):
                    path.unlink()
            except FileNotFoundError:
                pass
    return 0


class Controller:
    def __init__(self, config, fixture_spec=None):
        self.config = config
        self.fixture_spec = fixture_spec
        self.root = Path(config["state_root"])
        self.lock = None
        self.store = None
        self.controller_id = uuid.uuid4().hex
        self.stop = threading.Event()
        self.process = None
        self.service_identity = None
        self.domain = None
        self.last_cleanup = None
        self.state = None

    def _base_state(self, incarnation, restart_count, health, **detail):
        value = {
            "state_version": STATE_VERSION,
            "source_commit": self.config["source_commit"],
            "controller_id": self.controller_id,
            "controller_identity": process_identity(os.getpid()),
            "service_incarnation": incarnation,
            "service_fence": incarnation,
            "canonical_writer_authority": False,
            "service_identity": self.service_identity,
            "service_domain": str(self.domain.path) if self.domain is not None else None,
            "socket_path": self.config["socket_path"],
            "health": health,
            "unavailable": health != "running",
            "observation_time": _utc_now(),
            "restart_count": restart_count,
            "restart_cap": self.config["restart_cap"],
        }
        if self.last_cleanup is not None:
            value["last_cleanup"] = self.last_cleanup
        value.update(detail)
        return value

    def _write(self, incarnation, restart_count, health, **detail):
        self.state = self._base_state(incarnation, restart_count, health, **detail)
        self.store.write(self.state)

    def _child_argv(self, incarnation):
        python = self.config["python_executable"]
        if self.fixture_spec is not None:
            return [
                python,
                "-X",
                "utf8",
                "-B",
                "-m",
                "tools.construction_swarm.p2_host_lifecycle",
                "fixture-child",
                "--socket",
                self.config["socket_path"],
                "--fixture-spec",
                str(self.fixture_spec),
                "--incarnation",
                str(incarnation),
            ]
        return [
            python,
            "-X",
            "utf8",
            "-B",
            "-m",
            "tools.construction_swarm.p2_access",
            "serve",
            "--socket",
            self.config["socket_path"],
            "--source-commit",
            self.config["source_commit"],
            "--grants",
            self.config["grants_file"],
            "--instance-id",
            f"p2-host-{incarnation}",
            "--fence",
            str(incarnation),
        ]

    def _environment(self):
        result = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
        for name in ("LANG", "LC_ALL"):
            if name in os.environ:
                result[name] = os.environ[name]
        return result

    def _launch(self, incarnation):
        argv = self._child_argv(incarnation)
        try:
            self.process = subprocess.Popen(
                argv,
                cwd=self.config["repository_root"],
                env=self._environment(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                preexec_fn=self.domain.join_current,
                close_fds=True,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise LifecycleRefused("launch_refused", "service could not enter its ownership domain") from exc
        try:
            self.service_identity = process_identity(self.process.pid)
        except LifecycleRefused:
            if self.process.poll() is not None:
                self.service_identity = None
                return
            raise
        _require(
            self.service_identity["process_group"] == self.process.pid,
            "launch_refused",
            "service did not become process-group leader",
        )

    def _ready(self):
        deadline = time.monotonic() + self.config["startup_timeout_seconds"]
        path = Path(self.config["socket_path"])
        while time.monotonic() < deadline and not self.stop.is_set():
            if self.process.poll() is not None:
                return False
            if path.exists() and _socket_active(path):
                return True
            time.sleep(0.02)
        return False

    def _cleanup_current(self):
        _require(self.domain is not None, "cleanup_unknown", "service ownership domain is unavailable")
        return self.domain.cleanup(self.config["shutdown_timeout_seconds"], self.process)

    def _reconcile_previous(self, previous):
        notes = []
        prior_incarnation = 0
        if previous is not None:
            _require(
                previous.get("source_commit") == self.config["source_commit"],
                "state_refused",
                "prior state source differs",
            )
            prior_incarnation = previous.get("service_incarnation")
            _require(
                type(prior_incarnation) is int and prior_incarnation >= 0,
                "state_refused",
                "prior incarnation is invalid",
            )
            identity = previous.get("service_identity")
            recorded_domain = previous.get("service_domain")
            _require(recorded_domain in {None, str(self.domain.path)},
                     "state_refused", "prior service ownership domain differs")
            if self.domain.populated():
                cleanup = self.domain.cleanup(self.config["shutdown_timeout_seconds"])
                _require(cleanup["quiescent"], "cleanup_unknown", "prior owned service did not quiesce")
                notes.append("prior_owned_service_quiesced")
            elif isinstance(identity, dict):
                try:
                    process_identity(identity.get("pid"))
                    notes.append("stale_pid_unrelated_preserved")
                except LifecycleRefused:
                    notes.append("prior_service_absent")
        notes.append(reconcile_socket(self.config["socket_path"]))
        return prior_incarnation, notes

    def run(self):
        prohibition = startup_prohibition(self.config)
        _require(prohibition is None, "startup_refused", f"lifecycle startup is {prohibition}")
        self.lock = WatchdogLock(self.root)
        self.lock.acquire()
        old_handlers = {}
        try:
            self.store = StateStore(self.root)
            self.domain = CgroupDomain(self.config["cgroup_root"], self.root)
            self.domain.ensure()
            previous = self.store.read()
            incarnation, reconciliation = self._reconcile_previous(previous)
            restart_count = 0
            for number in (signal.SIGTERM, signal.SIGINT):
                old_handlers[number] = signal.signal(number, lambda _number, _frame: self.stop.set())
            while True:
                prohibition = startup_prohibition(self.config)
                if prohibition is not None:
                    self.service_identity = None
                    self._write(
                        incarnation,
                        restart_count,
                        "outage",
                        outage_reason=prohibition,
                        reconciliation=reconciliation,
                    )
                    return 5
                incarnation += 1
                self.service_identity = None
                self._write(
                    incarnation,
                    restart_count,
                    "starting",
                    reconciliation=reconciliation,
                )
                try:
                    self._launch(incarnation)
                except LifecycleRefused as exc:
                    self._write(
                        incarnation,
                        restart_count,
                        "outage",
                        reconciliation=reconciliation,
                        outage_reason=exc.code,
                    )
                    return 6
                self._write(
                    incarnation,
                    restart_count,
                    "starting",
                    reconciliation=reconciliation,
                )
                ready = self._ready()
                if ready:
                    self._write(
                        incarnation,
                        restart_count,
                        "running",
                        reconciliation=reconciliation,
                    )
                while ready and not self.stop.is_set() and self.process.poll() is None:
                    time.sleep(0.03)
                if self.stop.is_set():
                    self._write(incarnation, restart_count, "stopping", reconciliation=reconciliation)
                    cleanup = self._cleanup_current()
                    self.last_cleanup = cleanup
                    health = "stopped" if cleanup["quiescent"] else "outage"
                    self._write(
                        incarnation,
                        restart_count,
                        health,
                        reconciliation=reconciliation,
                        cleanup=cleanup,
                        outage_reason=None if cleanup["quiescent"] else "cleanup_unknown",
                    )
                    return 0 if cleanup["quiescent"] else 6
                exit_code = self.process.poll()
                cleanup = self._cleanup_current()
                self.last_cleanup = cleanup
                exit_code = self.process.poll() if self.process is not None else exit_code
                if not cleanup["quiescent"]:
                    self._write(
                        incarnation,
                        restart_count,
                        "outage",
                        reconciliation=reconciliation,
                        outage_reason="cleanup_unknown",
                        last_exit_code=exit_code,
                        cleanup=cleanup,
                    )
                    return 6
                try:
                    socket_note = reconcile_socket(self.config["socket_path"])
                    reconciliation = reconciliation + ["restart_" + socket_note]
                except LifecycleRefused as exc:
                    self._write(
                        incarnation,
                        restart_count,
                        "outage",
                        reconciliation=reconciliation,
                        outage_reason=exc.code,
                        last_exit_code=exit_code,
                        cleanup=cleanup,
                    )
                    return 6
                if restart_count >= self.config["restart_cap"]:
                    self._write(
                        incarnation,
                        restart_count,
                        "outage",
                        reconciliation=reconciliation,
                        outage_reason="restart_exhausted",
                        last_exit_code=exit_code,
                        cleanup=cleanup,
                    )
                    return 4
                restart_count += 1
                backoff = min(
                    self.config["backoff_initial_seconds"] * (2 ** (restart_count - 1)),
                    self.config["backoff_max_seconds"],
                )
                self._write(
                    incarnation,
                    restart_count,
                    "backoff",
                    reconciliation=reconciliation,
                    backoff_seconds=backoff,
                    last_exit_code=exit_code,
                    cleanup=cleanup,
                )
                if self.stop.wait(backoff):
                    self._write(
                        incarnation,
                        restart_count,
                        "stopped",
                        reconciliation=reconciliation,
                        cleanup={"term_sent": False, "kill_sent": False, "quiescent": True},
                    )
                    return 0
        finally:
            try:
                populated = self.domain is not None and self.domain.populated()
            except LifecycleRefused:
                populated = False
            if populated:
                try:
                    self._cleanup_current()
                except LifecycleRefused:
                    pass
            for number, handler in old_handlers.items():
                signal.signal(number, handler)
            self.lock.release()


def request_stop(state_root, timeout):
    state_root = Path(state_root)
    _require(
        state_root.is_dir() and not state_root.is_symlink(),
        "stop_refused",
        "lifecycle state root is unavailable",
    )
    store = StateStore(state_root)
    state = store.read()
    _require(state is not None, "stop_refused", "lifecycle state is unavailable")
    identity = state.get("controller_identity")
    controller_id = state.get("controller_id")
    incarnation = state.get("service_incarnation")
    try:
        descriptor = _open_verified_pidfd(identity)
    except LifecycleRefused as exc:
        raise LifecycleRefused("stop_refused", "recorded controller identity does not match") from exc
    try:
        signal.pidfd_send_signal(descriptor, signal.SIGTERM)
    except ProcessLookupError as exc:
        os.close(descriptor)
        raise LifecycleRefused("stop_refused", "controller exited before stop signal") from exc
    deadline = time.monotonic() + timeout
    receipt = None
    try:
        while time.monotonic() < deadline:
            current = store.read()
            matching_receipt = (
                current is not None
                and current.get("controller_id") == controller_id
                and current.get("service_incarnation") == incarnation
                and current.get("health") == "stopped"
                and current.get("unavailable") is True
                and isinstance(current.get("cleanup"), dict)
                and current["cleanup"].get("quiescent") is True
            )
            if matching_receipt:
                receipt = current
            if not _pidfd_alive(descriptor):
                if receipt is not None:
                    return {
                        "status": "STOPPED",
                        "controller_pid": identity["pid"],
                        "service_incarnation": incarnation,
                        "cleanup": receipt["cleanup"],
                    }
                raise LifecycleRefused(
                    "stop_cleanup_unknown",
                    "controller exited without a matching quiescent cleanup receipt",
                )
            time.sleep(0.02)
    finally:
        os.close(descriptor)
    raise LifecycleRefused("stop_timeout", "controller did not stop within bound")


def source_scope_check(repository, candidate):
    _require(
        isinstance(candidate, str) and re.fullmatch(r"[0-9a-f]{40}", candidate),
        "source_scope_refused",
        "candidate must be a full commit",
    )

    def git(*arguments):
        result = subprocess.run(
            ["git", "-C", str(repository), *arguments],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        _require(
            result.returncode == 0,
            "source_scope_refused",
            "Git source/scope check failed",
            command=list(arguments),
            stderr=result.stderr.strip(),
        )
        return result.stdout

    resolved = git("rev-parse", "--verify", candidate + "^{commit}").strip()
    _require(resolved == candidate, "source_scope_refused", "candidate resolution differs")
    _require(git("rev-parse", "HEAD").strip() == candidate,
             "source_scope_refused", "checked-out HEAD differs from candidate")
    _require(not git("status", "--porcelain=v1", "--untracked-files=all").strip(),
             "source_scope_refused", "candidate worktree is not clean")
    git("merge-base", "--is-ancestor", TASK_BASE, candidate)
    changed = tuple(sorted(line for line in git("diff", "--name-only", TASK_BASE, candidate).splitlines() if line))
    _require(changed == ALLOWED_PATHS, "source_scope_refused", "changed path set differs", changed=list(changed))
    statuses = tuple(sorted(line for line in git("diff", "--name-status", TASK_BASE, candidate).splitlines() if line))
    expected_statuses = tuple(sorted("A\t" + path for path in ALLOWED_PATHS))
    _require(statuses == expected_statuses, "source_scope_refused",
             "packet paths are not exactly five additions", statuses=list(statuses))
    git("diff", "--check", TASK_BASE, candidate)
    return {
        "status": "SOURCE_SCOPE_PASS",
        "task_base": TASK_BASE,
        "candidate": candidate,
        "changed_paths": list(changed),
        "path_statuses": list(statuses),
        "head_and_worktree_bound": True,
        "integration_gate_modified": False,
    }


def _print(value):
    print(json.dumps(value, sort_keys=True, ensure_ascii=True), flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--config", required=True)
    run_parser.add_argument("--fixture-spec", help="TEST ONLY: run the inert lifecycle fixture child")
    stop_parser = subparsers.add_parser("stop")
    stop_parser.add_argument("--state-root", required=True)
    stop_parser.add_argument("--timeout", type=float, default=10)
    scope_parser = subparsers.add_parser("source-scope")
    scope_parser.add_argument("--repository", required=True)
    scope_parser.add_argument("--candidate", required=True)
    child_parser = subparsers.add_parser("fixture-child")
    child_parser.add_argument("--socket", required=True)
    child_parser.add_argument("--fixture-spec", required=True)
    child_parser.add_argument("--incarnation", type=int, required=True)
    subparsers.add_parser("fixture-grandchild")
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            config = load_config(args.config)
            fixture = _absolute_path(args.fixture_spec, "fixture_spec") if args.fixture_spec else None
            if fixture is not None:
                _load_json(fixture, MAX_FIXTURE_BYTES)
            return Controller(config, fixture_spec=fixture).run()
        if args.command == "stop":
            _require(0.1 <= args.timeout <= 15, "stop_refused", "stop timeout is invalid")
            _print(request_stop(_absolute_path(args.state_root, "state_root"), args.timeout))
            return 0
        if args.command == "source-scope":
            _print(source_scope_check(_absolute_path(args.repository, "repository"), args.candidate))
            return 0
        if args.command == "fixture-child":
            return fixture_child(args.socket, args.fixture_spec, args.incarnation)
        fixture_grandchild()
        return 0
    except LifecycleRefused as exc:
        _print({"status": "REFUSED", "error": {"code": exc.code, "message": exc.message, **exc.detail}})
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
