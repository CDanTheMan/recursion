"""Windows test-only Job ownership. No shell, global job, service or product runtime.

Creates children suspended, with stdio handle allowlisting and optional at-birth Job
membership. The explicit post-create variant exists only as a fault-test comparator.
"""
import ctypes as C
from ctypes import wintypes as W
import os
import subprocess
import time

if os.name != "nt":
    raise ImportError("Windows-only probe helper")

K = C.WinDLL("kernel32", use_last_error=True)
SIZE = C.c_size_t
HANDLE = W.HANDLE

class STARTUPINFO(C.Structure):
    _fields_ = [("cb", W.DWORD), ("lpReserved", W.LPWSTR), ("lpDesktop", W.LPWSTR),
                ("lpTitle", W.LPWSTR), ("dwX", W.DWORD), ("dwY", W.DWORD),
                ("dwXSize", W.DWORD), ("dwYSize", W.DWORD), ("dwXCountChars", W.DWORD),
                ("dwYCountChars", W.DWORD), ("dwFillAttribute", W.DWORD),
                ("dwFlags", W.DWORD), ("wShowWindow", W.WORD), ("cbReserved2", W.WORD),
                ("lpReserved2", C.POINTER(W.BYTE)), ("hStdInput", HANDLE),
                ("hStdOutput", HANDLE), ("hStdError", HANDLE)]

class STARTUPINFOEX(C.Structure):
    _fields_ = [("StartupInfo", STARTUPINFO), ("lpAttributeList", C.c_void_p)]

class PROCESSINFO(C.Structure):
    _fields_ = [("hProcess", HANDLE), ("hThread", HANDLE), ("dwProcessId", W.DWORD), ("dwThreadId", W.DWORD)]

class BASICLIMIT(C.Structure):
    _fields_ = [("PerProcessUserTimeLimit", C.c_longlong), ("PerJobUserTimeLimit", C.c_longlong),
                ("LimitFlags", W.DWORD), ("MinimumWorkingSetSize", SIZE), ("MaximumWorkingSetSize", SIZE),
                ("ActiveProcessLimit", W.DWORD), ("Affinity", SIZE), ("PriorityClass", W.DWORD),
                ("SchedulingClass", W.DWORD)]

class IOCOUNTERS(C.Structure):
    _fields_ = [(name, C.c_ulonglong) for name in ("ReadOperationCount", "WriteOperationCount", "OtherOperationCount", "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]

class EXTLIMIT(C.Structure):
    _fields_ = [("BasicLimitInformation", BASICLIMIT), ("IoInfo", IOCOUNTERS), ("ProcessMemoryLimit", SIZE),
                ("JobMemoryLimit", SIZE), ("PeakProcessMemoryUsed", SIZE), ("PeakJobMemoryUsed", SIZE)]

class ACCOUNTING(C.Structure):
    _fields_ = [("TotalUserTime", C.c_longlong), ("TotalKernelTime", C.c_longlong),
                ("ThisPeriodTotalUserTime", C.c_longlong), ("ThisPeriodTotalKernelTime", C.c_longlong),
                ("TotalPageFaultCount", W.DWORD), ("TotalProcesses", W.DWORD),
                ("ActiveProcesses", W.DWORD), ("TotalTerminatedProcesses", W.DWORD)]

def declare(name, args, result):
    f = getattr(K, name); f.argtypes = args; f.restype = result; return f

CreateJob = declare("CreateJobObjectW", [C.c_void_p, W.LPCWSTR], HANDLE)
OpenJob = declare("OpenJobObjectW", [W.DWORD, W.BOOL, W.LPCWSTR], HANDLE)
CloseHandle = declare("CloseHandle", [HANDLE], W.BOOL)
SetJob = declare("SetInformationJobObject", [HANDLE, C.c_int, C.c_void_p, W.DWORD], W.BOOL)
QueryJob = declare("QueryInformationJobObject", [HANDLE, C.c_int, C.c_void_p, W.DWORD, C.c_void_p], W.BOOL)
AssignJob = declare("AssignProcessToJobObject", [HANDLE, HANDLE], W.BOOL)
IsInJob = declare("IsProcessInJob", [HANDLE, HANDLE, C.POINTER(W.BOOL)], W.BOOL)
TerminateJob = declare("TerminateJobObject", [HANDLE, W.UINT], W.BOOL)
InitializeAttrs = declare("InitializeProcThreadAttributeList", [C.c_void_p, W.DWORD, W.DWORD, C.POINTER(SIZE)], W.BOOL)
UpdateAttrs = declare("UpdateProcThreadAttribute", [C.c_void_p, W.DWORD, SIZE, C.c_void_p, SIZE, C.c_void_p, C.c_void_p], W.BOOL)
DeleteAttrs = declare("DeleteProcThreadAttributeList", [C.c_void_p], None)
CreateProcess = declare("CreateProcessW", [W.LPCWSTR, W.LPWSTR, C.c_void_p, C.c_void_p, W.BOOL,
                        W.DWORD, C.c_void_p, W.LPCWSTR, C.POINTER(STARTUPINFOEX), C.POINTER(PROCESSINFO)], W.BOOL)
ResumeThread = declare("ResumeThread", [HANDLE], W.DWORD)
Wait = declare("WaitForSingleObject", [HANDLE, W.DWORD], W.DWORD)
ExitCode = declare("GetExitCodeProcess", [HANDLE, C.POINTER(W.DWORD)], W.BOOL)
OpenProcess = declare("OpenProcess", [W.DWORD, W.BOOL, W.DWORD], HANDLE)
TerminateProcess = declare("TerminateProcess", [HANDLE, W.UINT], W.BOOL)
GetTimes = declare("GetProcessTimes", [HANDLE, C.POINTER(W.FILETIME), C.POINTER(W.FILETIME), C.POINTER(W.FILETIME), C.POINTER(W.FILETIME)], W.BOOL)
GetImage = declare("QueryFullProcessImageNameW", [HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD)], W.BOOL)

def ok(value):
    if not value: raise C.WinError(C.get_last_error())
    return value

class Job:
    def __init__(self, name=None, max_processes=16, memory_bytes=2 * 1024**3):
        self.handle = ok(CreateJob(None, name)); self.name = name
        limits = EXTLIMIT(); limits.BasicLimitInformation.LimitFlags = 0x2000 | 0x8 | 0x200
        limits.BasicLimitInformation.ActiveProcessLimit = max_processes
        limits.JobMemoryLimit = memory_bytes
        try: ok(SetJob(self.handle, 9, C.byref(limits), C.sizeof(limits)))
        except BaseException: self.close(); raise

    def assign(self, process): ok(AssignJob(self.handle, process.handle))
    def contains(self, process):
        result = W.BOOL(); ok(IsInJob(process.handle, self.handle, C.byref(result))); return bool(result.value)
    def accounting(self):
        value = ACCOUNTING(); ok(QueryJob(self.handle, 1, C.byref(value), C.sizeof(value), None))
        return {name: int(getattr(value, name)) for name, _ in value._fields_}
    def terminate(self):
        if self.handle: ok(TerminateJob(self.handle, 125))
    def close(self):
        if self.handle: ok(CloseHandle(self.handle)); self.handle = None

class Process:
    def __init__(self, argv, cwd, env, job=None, suspended=False):
        import msvcrt
        self.handle = self.thread = None
        self.stdin = self.stdout = self.stderr = None
        pipes = [os.pipe() for _ in range(3)]
        child_fds = [pipes[0][0], pipes[1][1], pipes[2][1]]
        parent_fds = [pipes[0][1], pipes[1][0], pipes[2][0]]
        for fd in child_fds: os.set_inheritable(fd, True)
        for fd in parent_fds: os.set_inheritable(fd, False)
        handles = (HANDLE * 3)(*[msvcrt.get_osfhandle(fd) for fd in child_fds])
        count = 2 if job is not None else 1
        size = SIZE(); InitializeAttrs(None, count, 0, C.byref(size))
        buffer = C.create_string_buffer(size.value)
        initialized = False
        try:
            ok(InitializeAttrs(buffer, count, 0, C.byref(size))); initialized = True
            ok(UpdateAttrs(buffer, 0, 0x20002, handles, C.sizeof(handles), None, None))
            if job is not None:
                jobs = (HANDLE * 1)(job.handle)
                ok(UpdateAttrs(buffer, 0, 0x2000D, jobs, C.sizeof(jobs), None, None))
            si = STARTUPINFOEX(); si.StartupInfo.cb = C.sizeof(si); si.lpAttributeList = C.cast(buffer, C.c_void_p)
            si.StartupInfo.dwFlags = 0x100
            si.StartupInfo.hStdInput, si.StartupInfo.hStdOutput, si.StartupInfo.hStdError = handles
            pi = PROCESSINFO()
            command = C.create_unicode_buffer(subprocess.list2cmdline([str(x) for x in argv]))
            env_block = C.create_unicode_buffer("\0".join(k + "=" + str(v) for k, v in sorted(env.items(), key=lambda kv: kv[0].upper())) + "\0\0")
            # Always suspended until Python owns handles and has checked membership.
            flags = 0x80000 | 0x400 | 0x08000000 | 0x4
            ok(CreateProcess(str(argv[0]), command, None, None, True, flags, env_block, str(cwd), C.byref(si), C.byref(pi)))
            self.handle, self.thread, self.pid = pi.hProcess, pi.hThread, pi.dwProcessId
            self.stdin = os.fdopen(parent_fds[0], "wb", buffering=0)
            self.stdout = os.fdopen(parent_fds[1], "rb", buffering=0)
            self.stderr = os.fdopen(parent_fds[2], "rb", buffering=0)
            parent_fds.clear()
            if job is not None and not job.contains(self): raise RuntimeError("at-birth membership missing")
            if not suspended: self.resume()
        except BaseException:
            if self.handle: TerminateProcess(self.handle, 126); self.close()
            raise
        finally:
            if initialized: DeleteAttrs(buffer)
            for fd in child_fds + parent_fds:
                try: os.close(fd)
                except OSError: pass

    def resume(self):
        if self.thread and ResumeThread(self.thread) == 0xFFFFFFFF: raise C.WinError(C.get_last_error())
    def poll(self):
        result = Wait(self.handle, 0)
        if result == 258: return None
        if result != 0: raise C.WinError(C.get_last_error())
        value = W.DWORD(); ok(ExitCode(self.handle, C.byref(value))); return int(value.value)
    def wait(self, seconds=10):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            value = self.poll()
            if value is not None: return value
            time.sleep(.01)
        raise TimeoutError("owned process did not exit")
    def terminate(self):
        if self.handle and self.poll() is None: ok(TerminateProcess(self.handle, 125))
    def close(self):
        for f in (self.stdin, self.stdout, self.stderr):
            if f is not None:
                try: f.close()
                except OSError: pass
        for name in ("thread", "handle"):
            handle = getattr(self, name)
            if handle: ok(CloseHandle(handle)); setattr(self, name, None)

def minimal_env():
    keys = ("SystemRoot", "WINDIR", "COMSPEC", "PATH", "PATHEXT", "TEMP", "TMP", "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE", "OS")
    return {k: os.environ[k] for k in keys if k in os.environ}

def process_identity(handle):
    values=[W.FILETIME() for _ in range(4)]
    ok(GetTimes(handle,*[C.byref(x) for x in values]))
    size=W.DWORD(32768);buffer=C.create_unicode_buffer(size.value)
    ok(GetImage(handle,0,buffer,C.byref(size)))
    return {"creation_filetime":(values[0].dwHighDateTime<<32)|values[0].dwLowDateTime,"image":buffer.value}
