"""Stop a live provider process and the children it starts.

Linux puts the child in its own session and, on cancel or timeout, signals
that process group. The recorded group is not the harness group, so the
signal cannot hit the harness. Windows places the child in a job object
before any of its code runs and terminates the job, so grandchildren die
with the CLI. Captured output is UTF-8.
"""

from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Callable

POLL_SECONDS = 0.05
_SIGKILL = getattr(signal, "SIGKILL", 9)
_KERNEL32 = None
_KERNEL32_LOCK = threading.Lock()


class ProcessCancelled(Exception):
    """The caller asked for the process tree to stop, and it has been killed."""


@dataclass(frozen=True)
class CommandResult:
    """UTF-8 output from a finished process tree."""

    returncode: int
    stdout: str
    stderr: str


def run_command(
    argv: list[str],
    *,
    cwd: str | None = None,
    stdin_text: str | None = None,
    timeout_seconds: float | None = None,
    should_stop: Callable[[], bool] | None = None,
    poll_seconds: float = POLL_SECONDS,
) -> CommandResult:
    """Run ``argv`` and return its UTF-8 output.

    ``should_stop`` is polled until the process exits. When it returns true,
    or when ``timeout_seconds`` elapses, the whole process tree is killed.
    ``FileNotFoundError`` means the executable is missing.
    ``subprocess.TimeoutExpired`` means the timeout fired.
    ``ProcessCancelled`` means ``should_stop`` fired.
    """

    if not argv:
        raise FileNotFoundError("provider command is empty")
    if timeout_seconds is not None and timeout_seconds < 0:
        timeout_seconds = 0
    if should_stop is not None and should_stop():
        raise ProcessCancelled("run cancelled")
    child = _spawn(argv, cwd, stdin_text)
    try:
        reason = _supervise(child, timeout_seconds=timeout_seconds, should_stop=should_stop, poll_seconds=poll_seconds)
        decoding = "strict" if reason == "ok" else "replace"
        stdout = bytes(child.stdout).decode("utf-8", errors=decoding)
        stderr = bytes(child.stderr).decode("utf-8", errors=decoding)
        if reason == "cancel":
            raise ProcessCancelled("run cancelled")
        if reason == "timeout":
            raise subprocess.TimeoutExpired(cmd=argv, timeout=0 if timeout_seconds is None else timeout_seconds)
        code = child.returncode if child.returncode is not None else 1
        return CommandResult(returncode=code, stdout=stdout, stderr=stderr)
    finally:
        child.close()


def _spawn(argv: list[str], cwd: str | None, stdin_text: str | None) -> _Child:
    if os.name == "nt":
        return _spawn_windows(argv, cwd, stdin_text)
    return _spawn_posix(argv, cwd, stdin_text)


def _supervise(
    child: _Child,
    *,
    timeout_seconds: float | None,
    should_stop: Callable[[], bool] | None,
    poll_seconds: float,
) -> str:
    deadline = None if timeout_seconds is None else time.monotonic() + timeout_seconds
    while True:
        if _asked_to_stop(child, should_stop):
            return "cancel"
        if deadline is not None and time.monotonic() >= deadline:
            _stop_tree(child)
            return "timeout"
        wait = poll_seconds if poll_seconds > 0 else 0.01
        if deadline is not None:
            wait = min(wait, max(0.0, deadline - time.monotonic()))
        if child.wait_for(wait):
            child.finish_io()
            if should_stop is not None and should_stop():
                # The direct child can exit and leave grandchildren behind.
                _stop_tree(child)
                return "cancel"
            return "ok"


def _asked_to_stop(child: _Child, should_stop: Callable[[], bool] | None) -> bool:
    if should_stop is None:
        return False
    try:
        stop = should_stop()
    except Exception:
        _stop_tree(child)
        raise
    if stop:
        _stop_tree(child)
        return True
    return False


def _stop_tree(child: _Child) -> None:
    child.kill_tree()
    child.finish_io()


class _Child:
    """One running process tree and the pipes that capture it."""

    def __init__(self) -> None:
        self.stdout = bytearray()
        self.stderr = bytearray()
        self.returncode: int | None = None
        self._threads: list[threading.Thread] = []
        self._io_errors: list[BaseException] = []
        self._closed = False
        self._killed = False
        self.container: tuple[str, int] | None = None

    def wait_for(self, seconds: float) -> bool:
        raise NotImplementedError

    def kill_tree(self) -> None:
        raise NotImplementedError

    def finish_io(self) -> None:
        for thread in self._threads:
            thread.join(5)
        if self._io_errors and self.returncode is None:
            raise self._io_errors[0]

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            if self.returncode is None:
                self.kill_tree()
        finally:
            try:
                self.finish_io()
            finally:
                self._release()

    def _release(self) -> None:
        return None

    def _track(self, target, args: tuple) -> None:
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()
        self._threads.append(thread)


def _read_stream(stream, sink: bytearray, errors: list[BaseException]) -> None:
    try:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            if isinstance(chunk, str):
                chunk = chunk.encode("utf-8")
            sink.extend(chunk)
    except OSError as exc:
        errors.append(exc)
    finally:
        try:
            stream.close()
        except OSError:
            pass


def _write_stream(stream, text: str, errors: list[BaseException]) -> None:
    try:
        stream.write(text.encode("utf-8"))
    except OSError as exc:
        errors.append(exc)
    finally:
        try:
            stream.close()
        except OSError:
            pass


class _PopenChild(_Child):
    def __init__(self, proc: subprocess.Popen, killer) -> None:
        super().__init__()
        self.proc = proc
        self._killer = killer
        if proc.stdout is not None:
            self._track(_read_stream, (proc.stdout, self.stdout, self._io_errors))
        if proc.stderr is not None:
            self._track(_read_stream, (proc.stderr, self.stderr, self._io_errors))

    def start_stdin(self, stdin_text: str | None) -> None:
        if stdin_text is None or self.proc.stdin is None:
            return
        self._track(_write_stream, (self.proc.stdin, stdin_text, self._io_errors))

    def wait_for(self, seconds: float) -> bool:
        if self.returncode is not None:
            return True
        try:
            self.proc.wait(timeout=seconds)
        except subprocess.TimeoutExpired:
            return False
        self.returncode = self.proc.returncode
        return True

    def kill_tree(self) -> None:
        if self._killed:
            return
        self._killed = True
        self._killer(self.proc)
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                self.proc.kill()
            except OSError:
                pass
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        self.returncode = self.proc.returncode


def _spawn_posix(argv: list[str], cwd: str | None, stdin_text: str | None) -> _PopenChild:
    proc = subprocess.Popen(
        argv,
        cwd=cwd,
        stdin=subprocess.PIPE if stdin_text is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        pgid = os.getpgid(proc.pid)
    except ProcessLookupError:
        pgid = proc.pid if isinstance(proc.pid, int) else -1
    if isinstance(pgid, int) and pgid > 0 and pgid == os.getpgrp():
        proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        raise OSError("provider process stayed in the harness process group")
    child = _PopenChild(proc, lambda process, group=pgid: _kill_posix_group(process, group))
    child.container = ("group", pgid if isinstance(pgid, int) else -1)
    child.start_stdin(stdin_text)
    return child


def _kill_posix_group(proc: subprocess.Popen, pgid: int | None = None) -> None:
    """Signal ``pgid`` unless that group is the harness group.

    ``killpg(0)`` and ``killpg`` of the harness group would stop this process.
    A missing or matching group kills only the direct child.
    """

    if pgid is None:
        pid = proc.pid
        try:
            pgid = os.getpgid(pid) if isinstance(pid, int) and pid > 0 else -1
        except ProcessLookupError:
            pgid = -1
    try:
        harness_group = os.getpgrp()
    except AttributeError:
        harness_group = -1
    if not isinstance(pgid, int) or pgid <= 0 or pgid == harness_group:
        try:
            proc.kill()
        except OSError:
            pass
        return
    try:
        os.killpg(pgid, _SIGKILL)
    except ProcessLookupError:
        try:
            proc.kill()
        except OSError:
            pass
    except PermissionError:
        try:
            proc.kill()
        except OSError:
            pass


def _spawn_windows(argv: list[str], cwd: str | None, stdin_text: str | None) -> _Child:
    kernel = _kernel32()
    job = _create_kill_job(kernel)
    try:
        return _spawn_windows_in_job(kernel, job, argv, cwd, stdin_text)
    except Exception:
        _close_handle(kernel, job)
        raise


def _spawn_windows_in_job(kernel, job, argv: list[str], cwd: str | None, stdin_text: str | None) -> _Child:
    try:
        return _spawn_windows_at_creation(kernel, job, argv, cwd, stdin_text)
    except FileNotFoundError:
        raise
    except OSError as first:
        try:
            return _spawn_windows_suspended(kernel, job, argv, cwd, stdin_text)
        except FileNotFoundError:
            raise
        except OSError as second:
            raise second from first


def _spawn_windows_suspended(kernel, job, argv: list[str], cwd: str | None, stdin_text: str | None) -> _WindowsPipeChild:
    """Start suspended, assign the job, then resume.

    The process cannot spawn a grandchild until ``AssignProcessToJobObject``
    has succeeded, so a failed assignment does not leave an uncontained tree.
    """

    import ctypes

    pipes = _WindowsEnds(stdin_text is not None)
    process_info = None
    child = None
    try:
        startup = _plain_startup(pipes)
        command = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        application = argv[0] if os.path.isfile(argv[0]) else None
        process_info = _process_information()
        created = kernel.CreateProcessW(
            application,
            command,
            None,
            None,
            True,
            0x00000004,  # CREATE_SUSPENDED
            None,
            cwd,
            ctypes.byref(startup),
            ctypes.byref(process_info),
        )
        if not created:
            raise _windows_spawn_error(argv[0])
        if not kernel.AssignProcessToJobObject(job, process_info.hProcess):
            error = ctypes.get_last_error()
            kernel.TerminateProcess(process_info.hProcess, 1)
            raise _WindowsSpawnFailed(error, f"AssignProcessToJobObject failed ({error})", argv[0])
        resumed = kernel.ResumeThread(process_info.hThread)
        _close_handle(kernel, process_info.hThread)
        process_info.hThread = None
        if resumed == 0xFFFFFFFF:
            kernel.TerminateProcess(process_info.hProcess, 1)
            raise _WindowsSpawnFailed(ctypes.get_last_error(), "ResumeThread failed", argv[0])
        pipes.close_child_ends()
        child = _WindowsPipeChild(kernel, job, process_info.hProcess, None, int(process_info.dwProcessId))
        process_info = None
        child.container = ("job", job)
        _attach_pipe(child, pipes, "stdout_parent", child.stdout, "rb")
        _attach_pipe(child, pipes, "stderr_parent", child.stderr, "rb")
        if stdin_text is not None:
            _attach_pipe(child, pipes, "stdin_parent", None, "wb", stdin_text)
        return child
    except Exception:
        if child is not None:
            child.kill_tree()
            _close_handle(kernel, child._thread)
            _close_handle(kernel, child._process)
            child._thread = None
            child._process = None
            child._job = None
            child._closed = True
        elif process_info is not None and process_info.hProcess:
            kernel.TerminateProcess(process_info.hProcess, 1)
            _close_handle(kernel, process_info.hThread)
            _close_handle(kernel, process_info.hProcess)
        pipes.close_all()
        raise


def _kernel32():
    import ctypes
    from ctypes import wintypes

    global _KERNEL32
    with _KERNEL32_LOCK:
        if _KERNEL32 is not None:
            return _KERNEL32
        kernel = _bind_kernel32(ctypes, wintypes)
        _KERNEL32 = kernel
        return kernel


def _bind_kernel32(ctypes, wintypes):
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.TerminateJobObject.restype = wintypes.BOOL
    kernel.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE,
        ctypes.c_int,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel.QueryInformationJobObject.restype = wintypes.BOOL
    kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.TerminateProcess.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetExitCodeProcess.restype = wintypes.BOOL
    kernel.ResumeThread.argtypes = [wintypes.HANDLE]
    kernel.ResumeThread.restype = wintypes.DWORD
    kernel.InitializeProcThreadAttributeList.argtypes = [
        ctypes.c_void_p,
        wintypes.DWORD,
        wintypes.DWORD,
        ctypes.POINTER(ctypes.c_size_t),
    ]
    kernel.InitializeProcThreadAttributeList.restype = wintypes.BOOL
    kernel.UpdateProcThreadAttribute.argtypes = [
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.c_size_t,
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    kernel.UpdateProcThreadAttribute.restype = wintypes.BOOL
    kernel.DeleteProcThreadAttributeList.argtypes = [ctypes.c_void_p]
    kernel.DeleteProcThreadAttributeList.restype = None
    kernel.CreateProcessW.argtypes = [
        wintypes.LPCWSTR,
        wintypes.LPWSTR,
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.BOOL,
        wintypes.DWORD,
        ctypes.c_void_p,
        wintypes.LPCWSTR,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    kernel.CreateProcessW.restype = wintypes.BOOL
    return kernel


def _create_kill_job(kernel):
    import ctypes

    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    info = _extended_limits()
    info.BasicLimitInformation.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    # TerminateJobObject still stops the tree when this limit cannot be set.
    kernel.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))
    return job


def _extended_limits():
    import ctypes
    from ctypes import wintypes

    class BasicLimits(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class IoCounters(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", BasicLimits),
            ("IoInfo", IoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    return ExtendedLimits()


def _close_handle(kernel, handle) -> None:
    if handle:
        kernel.CloseHandle(handle)


def _unsigned_handle(value: int) -> int:
    import ctypes

    if value < 0:
        value &= (1 << (ctypes.sizeof(ctypes.c_void_p) * 8)) - 1
    return value


class _WindowsPipeChild(_Child):
    """A process created inside a job before any of its code runs."""

    def __init__(self, kernel, job, process, thread, pid: int) -> None:
        super().__init__()
        self._kernel = kernel
        self._job = job
        self._process = process
        self._thread = thread
        self.pid = pid

    def wait_for(self, seconds: float) -> bool:
        import ctypes
        from ctypes import wintypes

        if self.returncode is not None:
            return True
        millis = max(0, min(int(seconds * 1000), 0xFFFFFFFF))
        waited = self._kernel.WaitForSingleObject(self._process, millis)
        if waited != 0:
            return False
        code = wintypes.DWORD()
        if not self._kernel.GetExitCodeProcess(self._process, ctypes.byref(code)):
            self.returncode = 1
        else:
            self.returncode = int(code.value)
        return True

    def kill_tree(self) -> None:
        if self._killed:
            return
        self._killed = True
        if self._job:
            self._kernel.TerminateJobObject(self._job, 1)
        if self.returncode is None and self._process:
            self._kernel.TerminateProcess(self._process, 1)
            self.wait_for(5)

    def _release(self) -> None:
        _close_handle(self._kernel, self._thread)
        _close_handle(self._kernel, self._process)
        _close_handle(self._kernel, self._job)
        self._thread = None
        self._process = None
        self._job = None


class _WindowsSpawnFailed(OSError):
    """CreateProcess did not start a process. Another launch path may run."""


def _spawn_windows_at_creation(kernel, job, argv: list[str], cwd: str | None, stdin_text: str | None) -> _WindowsPipeChild:
    import ctypes
    import msvcrt

    pipes = _WindowsEnds(stdin_text is not None)
    attribute = None
    process_info = None
    child = None
    try:
        attribute, handles = _attribute_list(kernel, job, pipes)
        startup = _startup_info(attribute, pipes, msvcrt)
        command = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        application = argv[0] if os.path.isfile(argv[0]) else None
        process_info = _process_information()
        created = kernel.CreateProcessW(
            application,
            command,
            None,
            None,
            True,
            0x00080000,  # EXTENDED_STARTUPINFO_PRESENT
            None,
            cwd,
            ctypes.byref(startup),
            ctypes.byref(process_info),
        )
        if not created:
            raise _windows_spawn_error(argv[0])
        # Keep the handle arrays alive until CreateProcess returns.
        del handles
        pipes.close_child_ends()
        _close_handle(kernel, process_info.hThread)
        child = _WindowsPipeChild(
            kernel,
            job,
            process_info.hProcess,
            None,
            int(process_info.dwProcessId),
        )
        process_info = None
        child.container = ("job", job)
        _attach_pipe(child, pipes, "stdout_parent", child.stdout, "rb")
        _attach_pipe(child, pipes, "stderr_parent", child.stderr, "rb")
        if stdin_text is not None:
            _attach_pipe(child, pipes, "stdin_parent", None, "wb", stdin_text)
        return child
    except Exception:
        if child is not None:
            child.kill_tree()
            _close_handle(kernel, child._thread)
            _close_handle(kernel, child._process)
            child._thread = None
            child._process = None
            child._job = None
            child._closed = True
        elif process_info is not None and process_info.hProcess:
            kernel.TerminateProcess(process_info.hProcess, 1)
            _close_handle(kernel, process_info.hThread)
            _close_handle(kernel, process_info.hProcess)
        pipes.close_all()
        raise
    finally:
        if attribute is not None:
            kernel.DeleteProcThreadAttributeList(attribute)


class _WindowsEnds:
    def __init__(self, pipe_stdin: bool) -> None:
        import msvcrt

        self._msvcrt = msvcrt
        self._owned: list[int] = []
        if pipe_stdin:
            self.stdin_child, self.stdin_parent = _pipe_ends(child_reads=True)
        else:
            self.stdin_child = _nul_read_fd()
            self.stdin_parent = None
        self._owned.append(self.stdin_child)
        if self.stdin_parent is not None:
            self._owned.append(self.stdin_parent)
        self.stdout_parent, self.stdout_child = _pipe_ends(child_reads=False)
        self.stderr_parent, self.stderr_child = _pipe_ends(child_reads=False)
        self._owned.extend((self.stdout_parent, self.stdout_child, self.stderr_parent, self.stderr_child))

    def handle(self, fd: int) -> int:
        return _unsigned_handle(self._msvcrt.get_osfhandle(fd))

    def close_child_ends(self) -> None:
        for fd in (self.stdin_child, self.stdout_child, self.stderr_child):
            _close_fd(fd)
        self.stdin_child = None
        self.stdout_child = None
        self.stderr_child = None

    def close_all(self) -> None:
        for fd in (
            self.stdin_child,
            self.stdin_parent,
            self.stdout_parent,
            self.stdout_child,
            self.stderr_parent,
            self.stderr_child,
        ):
            _close_fd(fd)
        self.stdin_child = None
        self.stdin_parent = None
        self.stdout_parent = None
        self.stdout_child = None
        self.stderr_parent = None
        self.stderr_child = None


def _pipe_ends(*, child_reads: bool) -> tuple[int, int]:
    read_fd, write_fd = os.pipe()
    if child_reads:
        os.set_inheritable(read_fd, True)
        os.set_inheritable(write_fd, False)
        return read_fd, write_fd
    os.set_inheritable(write_fd, True)
    os.set_inheritable(read_fd, False)
    return read_fd, write_fd


def _nul_read_fd() -> int:
    fd = os.open(os.devnull, os.O_RDONLY)
    os.set_inheritable(fd, True)
    return fd


def _close_fd(fd: int | None) -> None:
    if fd is None:
        return
    try:
        os.close(fd)
    except OSError:
        pass


def _attribute_list(kernel, job, pipes: _WindowsEnds):
    import ctypes
    from ctypes import wintypes

    # ProcThreadAttributeValue(number, thread, input, additive) with input set.
    job_attribute = 0x0002000D  # 13 | PROC_THREAD_ATTRIBUTE_INPUT
    handle_attribute = 0x00020002  # 2 | PROC_THREAD_ATTRIBUTE_INPUT
    size = ctypes.c_size_t(0)
    kernel.InitializeProcThreadAttributeList(None, 2, 0, ctypes.byref(size))
    if size.value <= 0:
        raise _windows_spawn_error("attribute list")
    block = ctypes.create_string_buffer(size.value)
    if not kernel.InitializeProcThreadAttributeList(block, 2, 0, ctypes.byref(size)):
        raise _windows_spawn_error("attribute list")
    jobs = (wintypes.HANDLE * 1)(job)
    if not kernel.UpdateProcThreadAttribute(
        block,
        0,
        job_attribute,
        ctypes.cast(jobs, ctypes.c_void_p),
        ctypes.sizeof(jobs),
        None,
        None,
    ):
        kernel.DeleteProcThreadAttributeList(block)
        raise _windows_spawn_error("job list")
    std_handles = (wintypes.HANDLE * 3)(
        pipes.handle(pipes.stdin_child),
        pipes.handle(pipes.stdout_child),
        pipes.handle(pipes.stderr_child),
    )
    if not kernel.UpdateProcThreadAttribute(
        block,
        0,
        handle_attribute,
        ctypes.cast(std_handles, ctypes.c_void_p),
        ctypes.sizeof(std_handles),
        None,
        None,
    ):
        kernel.DeleteProcThreadAttributeList(block)
        raise _windows_spawn_error("handle list")
    return block, (jobs, std_handles)


def _startup_info(attribute, pipes: _WindowsEnds, msvcrt):
    import ctypes
    from ctypes import wintypes

    class StartupInfoW(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("lpReserved", wintypes.LPWSTR),
            ("lpDesktop", wintypes.LPWSTR),
            ("lpTitle", wintypes.LPWSTR),
            ("dwX", wintypes.DWORD),
            ("dwY", wintypes.DWORD),
            ("dwXSize", wintypes.DWORD),
            ("dwYSize", wintypes.DWORD),
            ("dwXCountChars", wintypes.DWORD),
            ("dwYCountChars", wintypes.DWORD),
            ("dwFillAttribute", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("wShowWindow", wintypes.WORD),
            ("cbReserved2", wintypes.WORD),
            ("lpReserved2", ctypes.POINTER(ctypes.c_byte)),
            ("hStdInput", wintypes.HANDLE),
            ("hStdOutput", wintypes.HANDLE),
            ("hStdError", wintypes.HANDLE),
        ]

    class StartupInfoExW(ctypes.Structure):
        _fields_ = [("StartupInfo", StartupInfoW), ("lpAttributeList", ctypes.c_void_p)]

    info = StartupInfoExW()
    info.StartupInfo.cb = ctypes.sizeof(StartupInfoExW)
    info.StartupInfo.dwFlags = 0x00000100  # STARTF_USESTDHANDLES
    info.StartupInfo.hStdInput = pipes.handle(pipes.stdin_child)
    info.StartupInfo.hStdOutput = pipes.handle(pipes.stdout_child)
    info.StartupInfo.hStdError = pipes.handle(pipes.stderr_child)
    info.lpAttributeList = ctypes.addressof(attribute)
    del msvcrt
    return info


def _plain_startup(pipes: _WindowsEnds):
    import ctypes
    from ctypes import wintypes

    class StartupInfoW(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("lpReserved", wintypes.LPWSTR),
            ("lpDesktop", wintypes.LPWSTR),
            ("lpTitle", wintypes.LPWSTR),
            ("dwX", wintypes.DWORD),
            ("dwY", wintypes.DWORD),
            ("dwXSize", wintypes.DWORD),
            ("dwYSize", wintypes.DWORD),
            ("dwXCountChars", wintypes.DWORD),
            ("dwYCountChars", wintypes.DWORD),
            ("dwFillAttribute", wintypes.DWORD),
            ("dwFlags", wintypes.DWORD),
            ("wShowWindow", wintypes.WORD),
            ("cbReserved2", wintypes.WORD),
            ("lpReserved2", ctypes.POINTER(ctypes.c_byte)),
            ("hStdInput", wintypes.HANDLE),
            ("hStdOutput", wintypes.HANDLE),
            ("hStdError", wintypes.HANDLE),
        ]

    info = StartupInfoW()
    info.cb = ctypes.sizeof(StartupInfoW)
    info.dwFlags = 0x00000100  # STARTF_USESTDHANDLES
    info.hStdInput = pipes.handle(pipes.stdin_child)
    info.hStdOutput = pipes.handle(pipes.stdout_child)
    info.hStdError = pipes.handle(pipes.stderr_child)
    return info


def _process_information():
    import ctypes
    from ctypes import wintypes

    class ProcessInformation(ctypes.Structure):
        _fields_ = [
            ("hProcess", wintypes.HANDLE),
            ("hThread", wintypes.HANDLE),
            ("dwProcessId", wintypes.DWORD),
            ("dwThreadId", wintypes.DWORD),
        ]

    return ProcessInformation()


def _attach_pipe(child: _WindowsPipeChild, pipes: _WindowsEnds, name: str, sink, mode: str, text: str | None = None) -> None:
    fd = getattr(pipes, name)
    if fd is None:
        return
    setattr(pipes, name, None)
    stream = os.fdopen(fd, mode, buffering=0)
    if text is None:
        child._track(_read_stream, (stream, sink, child._io_errors))
    else:
        child._track(_write_stream, (stream, text, child._io_errors))


def _windows_spawn_error(name: str) -> OSError:
    import ctypes

    error = ctypes.get_last_error()
    if error in (2, 3):
        return FileNotFoundError(error, f"No such file or directory: {name!r}")
    win = ctypes.WinError(error)
    return _WindowsSpawnFailed(win.errno, str(win), name)
