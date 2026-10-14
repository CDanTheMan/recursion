"""Cancel and timeout stop a live provider process and the child it starts.

The child is a local Python stub. No Claude, Codex, or Grok binary is required.
"""

from __future__ import annotations

import gc
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.errors import ProviderCLIMissing, ProviderTimeout, RunCancelled  # noqa: E402
from scripts.v3.harness.orchestrate import cancel_run, create_run, drive_run, reopen_run  # noqa: E402
from scripts.v3.harness.providers import ProviderRequest, ProviderResult, _run_cli  # noqa: E402
from scripts.v3.harness.state import RunStore  # noqa: E402
from scripts.v3.proc.lifecycle import run_command  # noqa: E402


REQUEST = ProviderRequest(task="héllo 你好", packet_id="PACKET-TEST", route_id="route-a")
ROUTE = {"fixture_id": "F-M1B-001", "selected_route_id": "route-a", "status": "selected"}
_TIMEOUT = 12.0 if os.name == "nt" else 4.0

_STUB = """\
import os
import subprocess
import sys
import time
from pathlib import Path

ready = Path(sys.argv[1])
grandchild_path = Path(sys.argv[2])
parent_path = Path(sys.argv[3])
child = subprocess.Popen(
    [sys.executable, "-X", "utf8", "-B", "-c", "import time; time.sleep(300)"],
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
if os.name == "nt":
    parent_path.write_text(str(os.getpid()), encoding="utf-8")
else:
    parent_path.write_text(f"{os.getpid()} {os.getpgid(0)}", encoding="utf-8")
grandchild_path.write_text(str(child.pid), encoding="utf-8")
ready.write_text("ready", encoding="utf-8")
time.sleep(300)
"""


class _StubAdapter:
    def __init__(self, command: tuple[str, ...], name: str = "claude") -> None:
        self.name = name
        self._command = command

    def argv(self, request: ProviderRequest) -> tuple[str, ...]:
        del request
        return self._command

    def execute(self, request, *, allow_live=False, timeout_seconds=None, should_stop=None):
        del allow_live
        return _run_cli(
            self,
            request,
            stdin_text=None,
            timeout_seconds=timeout_seconds,
            should_stop=should_stop,
        )


def test_cancel_stops_the_provider_process_and_its_child() -> None:
    with tempfile.TemporaryDirectory() as directory:
        command, ready, grandchild, parent = _paths(Path(directory))
        stop = threading.Event()
        box: dict = {}

        def run() -> None:
            try:
                _run_cli(
                    _StubAdapter(command),
                    REQUEST,
                    stdin_text=None,
                    timeout_seconds=30,
                    should_stop=stop.is_set,
                )
            except RunCancelled:
                box["cancelled"] = True
            except Exception as exc:
                box["error"] = exc

        thread = threading.Thread(target=run)
        thread.start()
        parent_pid = 0
        child_pid = 0
        group = 0
        harness = os.getpid()
        harness_group = os.getpgrp() if os.name != "nt" else None
        try:
            _wait_file(ready, thread)
            parent_pid, group = _read_parent(parent)
            child_pid = int(grandchild.read_text(encoding="utf-8").strip())
            assert _alive(parent_pid)
            assert _alive(child_pid)
            assert _alive(harness)
            if os.name != "nt":
                assert parent_pid == group
                assert group != harness_group
                assert os.getpgrp() == harness_group
            stop.set()
            thread.join(15)
            assert not thread.is_alive()
            assert box.get("error") is None
            assert box.get("cancelled") is True
            _wait_dead(parent_pid)
            _wait_dead(child_pid)
            assert _alive(harness)
            if os.name != "nt":
                assert os.getpgrp() == harness_group
        finally:
            stop.set()
            thread.join(10)
            _reap(parent_pid, group)
            _reap(child_pid)


def test_timeout_stops_the_provider_process_and_its_child() -> None:
    with tempfile.TemporaryDirectory() as directory:
        command, ready, grandchild, parent = _paths(Path(directory))
        started = time.monotonic()
        with pytest.raises(ProviderTimeout) as caught:
            _run_cli(
                _StubAdapter(command),
                REQUEST,
                stdin_text=None,
                timeout_seconds=_TIMEOUT,
                should_stop=None,
            )
        elapsed = time.monotonic() - started
        assert "timed out after" in str(caught.value)
        assert elapsed < _TIMEOUT + 15
        assert ready.is_file(), "the provider process exited before it started a child"
        parent_pid, group = _read_parent(parent)
        child_pid = int(grandchild.read_text(encoding="utf-8").strip())
        try:
            _wait_dead(parent_pid)
            _wait_dead(child_pid)
        finally:
            _reap(parent_pid, group)
            _reap(child_pid)


def test_cancel_run_stops_an_in_flight_task_and_resume_can_finish() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        command, ready, grandchild, parent = _paths(root)
        store = RunStore(root / "state")
        record = create_run(
            store,
            goal="sleep",
            planned=[
                {
                    "intent_text": "sleep",
                    "packet_id": "PACKET-sleep",
                    "projection_digest": "digest-sleep",
                }
            ],
            candidates=[["slow"]],
            route=ROUTE,
            concurrency=1,
        )
        holder: dict = {}

        def drive() -> None:
            try:
                holder["result"] = drive_run(
                    store,
                    record["run_id"],
                    allow_live=True,
                    retries=0,
                    backoff_seconds=0,
                    timeout_seconds={"slow": 60},
                    route_id="route-a",
                    open_adapter=lambda name: _StubAdapter(command, name),
                    sleep=lambda seconds: None,
                    max_rounds=0,
                )
            except Exception as exc:
                holder["error"] = exc

        thread = threading.Thread(target=drive)
        thread.start()
        parent_pid = 0
        child_pid = 0
        group = 0
        try:
            _wait_file(ready, thread)
            parent_pid, group = _read_parent(parent)
            child_pid = int(grandchild.read_text(encoding="utf-8").strip())
            assert _alive(parent_pid)
            assert _alive(child_pid)
            cancelled = cancel_run(store, record["run_id"])
            assert cancelled["cancel_requested"] is True
            thread.join(20)
            assert not thread.is_alive()
            assert holder.get("error") is None
            result = holder["result"]
            assert result["status"] == "cancelled"
            assert result["tasks"][0]["status"] == "cancelled"
            assert result["tasks"][0]["error"] == "run cancelled"
            _wait_dead(parent_pid)
            _wait_dead(child_pid)

            reopen_run(store, record["run_id"])

            class Fast:
                name = "fast"

                def execute(self, request, *, allow_live=False, timeout_seconds=None, should_stop=None):
                    del allow_live, timeout_seconds, should_stop
                    return ProviderResult(provider="fast", argv=("fast",), text=request.task, live=False)

            finished = drive_run(
                store,
                record["run_id"],
                allow_live=False,
                retries=0,
                backoff_seconds=0,
                timeout_seconds={"fast": 30},
                route_id="route-a",
                open_adapter=lambda name: Fast(),
                sleep=lambda seconds: None,
                max_rounds=0,
            )
            assert finished["status"] == "completed"
            assert finished["cancel_requested"] is False
            assert finished["tasks"][0]["status"] == "completed"
            assert not _alive(parent_pid)
            assert not _alive(child_pid)
        finally:
            if thread.is_alive():
                cancel_run(store, record["run_id"])
                thread.join(15)
            _reap(parent_pid, group)
            _reap(child_pid)


def test_live_call_round_trips_utf8_and_reports_a_missing_cli() -> None:
    code = "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"

    class Echo:
        name = "claude"

        def argv(self, request: ProviderRequest) -> tuple[str, ...]:
            del request
            return (sys.executable, "-X", "utf8", "-c", code)

    result = _run_cli(Echo(), REQUEST, stdin_text=REQUEST.task, timeout_seconds=15, should_stop=None)
    assert result.live is True
    assert result.text == "héllo 你好"

    class Missing:
        name = "claude"

        def argv(self, request: ProviderRequest) -> tuple[str, ...]:
            del request
            return ("recursion-missing-cli-not-on-path",)

    with pytest.raises(ProviderCLIMissing) as missing:
        _run_cli(Missing(), REQUEST, stdin_text=None, timeout_seconds=5, should_stop=None)
    assert "claude CLI was not found on PATH" in str(missing.value)

    captured = run_command(
        [sys.executable, "-X", "utf8", "-c", "import sys; sys.stderr.buffer.write('café'.encode('utf-8')); raise SystemExit(7)"]
    )
    assert captured.returncode == 7
    assert captured.stderr == "café"


def test_finished_commands_release_pipes_and_keep_utf8() -> None:
    def once() -> None:
        result = run_command(
            [
                sys.executable,
                "-X",
                "utf8",
                "-B",
                "-c",
                "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())",
            ],
            stdin_text="héllo 你好",
        )
        assert result.returncode == 0
        assert result.stdout == "héllo 你好"
        assert isinstance(result.stdout, str)

    once()
    gc.collect()
    baseline = _resource_count()
    for _ in range(15):
        once()
    gc.collect()
    growth = _resource_count() - baseline
    assert growth <= 4, f"process handles grew by {growth}"


def test_live_tree_belongs_to_the_supervisor_container() -> None:
    from scripts.v3.proc import lifecycle

    with tempfile.TemporaryDirectory() as directory:
        command, ready, grandchild, parent = _paths(Path(directory))
        child = lifecycle._spawn(list(command), None, None)
        parent_pid = 0
        child_pid = 0
        group = 0
        try:
            _wait_ready(ready)
            parent_pid, group = _read_parent(parent)
            child_pid = int(grandchild.read_text(encoding="utf-8").strip())
            assert child.container is not None
            kind, ident = child.container
            assert _alive(parent_pid)
            assert _alive(child_pid)
            if kind == "group":
                assert os.name != "nt"
                assert ident == group == parent_pid
                assert ident != os.getpgrp()
            else:
                assert os.name == "nt"
                assert kind == "job"
                pids = _job_pids(child._kernel, ident)
                assert parent_pid in pids
                assert child_pid in pids
            child.kill_tree()
            _wait_dead(parent_pid)
            _wait_dead(child_pid)
        finally:
            child.close()
            _reap(parent_pid, group)
            _reap(child_pid)


def test_cancel_after_the_parent_exits_kills_the_grandchild() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        script = root / "orphan.py"
        script.write_text(_ORPHAN, encoding="utf-8", newline="\n")
        grandchild = root / "grandchild"
        parent = root / "parent"
        command = (
            sys.executable,
            "-X",
            "utf8",
            "-B",
            str(script),
            str(grandchild),
            str(parent),
        )

        def should_stop() -> bool:
            if not parent.is_file() or parent.stat().st_size == 0:
                return False
            pid = int(parent.read_text(encoding="utf-8").split()[0])
            return not _alive(pid)

        parent_pid = 0
        child_pid = 0
        group = 0
        try:
            with pytest.raises(RunCancelled):
                _run_cli(
                    _StubAdapter(command),
                    REQUEST,
                    stdin_text=None,
                    timeout_seconds=20,
                    should_stop=should_stop,
                )
            parent_pid, group = _read_parent(parent)
            child_pid = int(grandchild.read_text(encoding="utf-8").strip())
            _wait_dead(parent_pid)
            _wait_dead(child_pid)
        finally:
            _reap(parent_pid, group)
            _reap(child_pid)


def test_group_kill_refuses_the_harness_process_group(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts.v3.proc import lifecycle

    events: list[tuple] = []

    def killpg(group: int, sig: int) -> None:
        events.append(("killpg", group, sig))

    monkeypatch.setattr(lifecycle.os, "getpgrp", lambda: 4242, raising=False)
    monkeypatch.setattr(lifecycle.os, "killpg", killpg, raising=False)

    class Proc:
        pid = 99

        def kill(self) -> None:
            events.append(("kill", self.pid))

    lifecycle._kill_posix_group(Proc(), 4242)  # type: ignore[arg-type]
    assert events == [("kill", 99)]
    events.clear()
    lifecycle._kill_posix_group(Proc(), 0)  # type: ignore[arg-type]
    assert events == [("kill", 99)]
    events.clear()
    lifecycle._kill_posix_group(Proc(), 777)  # type: ignore[arg-type]
    assert events == [("killpg", 777, getattr(signal, "SIGKILL", 9))]


def test_every_live_adapter_runs_under_the_supervisor(monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts.v3.harness import providers
    from scripts.v3.proc.lifecycle import CommandResult

    calls: list[dict] = []

    def fake_run(argv, **kwargs):
        del argv
        calls.append(kwargs)
        return CommandResult(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr(providers, "run_command", fake_run)
    request = ProviderRequest(task="task text", packet_id="PACKET-TEST", route_id="route-a")
    live = [name for name in providers.adapters() if name != "fixture"]
    assert {"claude", "codex", "grok"} <= set(live)
    for name in live:
        adapter = providers.adapters()[name]()
        result = adapter.execute(request, allow_live=True, timeout_seconds=9, should_stop=lambda: False)
        assert result.live is True
        assert result.provider == name
        assert result.text == "ok"
    assert len(calls) == len(live)
    assert all(call["timeout_seconds"] == 9 for call in calls)
    assert all(callable(call["should_stop"]) for call in calls)
    for name, call in zip(live, calls, strict=True):
        if name == "claude":
            assert call["stdin_text"] == "task text"
        else:
            assert call["stdin_text"] is None
    before = len(calls)
    providers.adapters()["fixture"]().execute(
        request, allow_live=True, timeout_seconds=9, should_stop=lambda: False
    )
    assert len(calls) == before


_ORPHAN = """\
import os
import subprocess
import sys
from pathlib import Path

grandchild_path = Path(sys.argv[1])
parent_path = Path(sys.argv[2])
child = subprocess.Popen(
    [sys.executable, "-X", "utf8", "-B", "-c", "import time; time.sleep(300)"],
    stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
if os.name == "nt":
    parent_path.write_text(str(os.getpid()), encoding="utf-8")
else:
    parent_path.write_text(f"{os.getpid()} {os.getpgid(0)}", encoding="utf-8")
grandchild_path.write_text(str(child.pid), encoding="utf-8")
"""


def _paths(root: Path) -> tuple[tuple[str, ...], Path, Path, Path]:
    script = root / "stub.py"
    script.write_text(_STUB, encoding="utf-8", newline="\n")
    ready = root / "ready"
    grandchild = root / "grandchild"
    parent = root / "parent"
    command = (sys.executable, "-X", "utf8", "-B", str(script), str(ready), str(grandchild), str(parent))
    return command, ready, grandchild, parent


def _wait_ready(path: Path, timeout: float = 20) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file() and path.stat().st_size > 0:
            return
        time.sleep(0.05)
    raise AssertionError(f"provider process did not become ready: {path}")


def _job_pids(kernel, job) -> set[int]:
    import ctypes
    from ctypes import wintypes

    class ProcessList(ctypes.Structure):
        _fields_ = [
            ("NumberOfAssignedProcesses", wintypes.DWORD),
            ("NumberOfProcessIdsInList", wintypes.DWORD),
            ("ProcessIdList", ctypes.c_size_t * 32),
        ]

    info = ProcessList()
    returned = wintypes.DWORD()
    ok = kernel.QueryInformationJobObject(job, 3, ctypes.byref(info), ctypes.sizeof(info), ctypes.byref(returned))
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    count = min(int(info.NumberOfProcessIdsInList), 32)
    return {int(info.ProcessIdList[index]) for index in range(count)}


def _resource_count() -> int:
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        kernel.GetProcessHandleCount.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.GetProcessHandleCount.restype = wintypes.BOOL
        count = wintypes.DWORD()
        if not kernel.GetProcessHandleCount(kernel.GetCurrentProcess(), ctypes.byref(count)):
            raise OSError(ctypes.get_last_error(), "GetProcessHandleCount failed")
        return int(count.value)
    return len(list(Path("/proc/self/fd").iterdir()))


def _wait_file(path: Path, thread: threading.Thread, timeout: float = 20) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file() and path.stat().st_size > 0:
            return
        if not thread.is_alive():
            break
        time.sleep(0.05)
    raise AssertionError(f"provider process did not become ready: {path}")


def _read_parent(path: Path) -> tuple[int, int]:
    parts = path.read_text(encoding="utf-8").strip().split()
    pid = int(parts[0])
    group = int(parts[1]) if len(parts) > 1 else pid
    return pid, group


def _alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        return _windows_alive(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    stat = Path(f"/proc/{pid}/stat")
    try:
        text = stat.read_text(encoding="utf-8")
    except OSError:
        return False
    tail = text.rsplit(")", 1)[-1].split()
    return bool(tail) and tail[0] != "Z"


def _windows_alive(pid: int) -> bool:
    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.OpenProcess(0x1000, False, pid)
    if not handle:
        return False
    try:
        code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
            return False
        return code.value == 259
    finally:
        kernel.CloseHandle(handle)


def _wait_dead(pid: int, timeout: float = 5) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not _alive(pid):
            return
        time.sleep(0.05)
    raise AssertionError(f"pid {pid} is still running")


def _reap(pid: int, group: int = 0) -> None:
    if pid <= 0:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(pid)],
            check=False,
            capture_output=True,
        )
        return
    if group > 0 and group != os.getpgrp():
        try:
            os.killpg(group, signal.SIGKILL)
        except ProcessLookupError:
            return
        return
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return
