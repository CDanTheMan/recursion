"""Linux namespace wrapper; upstream entry and synthetic agent remain unmodified."""
import errno
import json
import os
import pathlib
import resource
import runpy
import socket
import sys
import time

source=pathlib.Path(sys.argv[1]).resolve()
resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
resource.setrlimit(resource.RLIMIT_CPU,(30,30))
resource.setrlimit(resource.RLIMIT_NOFILE,(256,256))
resource.setrlimit(resource.RLIMIT_FSIZE,(64*1024**2,64*1024**2))
test=socket.socket();test.settimeout(1)
try:
    test.connect(("192.0.2.1",443))
    raise RuntimeError("network namespace canary unexpectedly connected")
except OSError as exc:
    if exc.errno!=errno.ENETUNREACH:raise
    isolation={"type":"namespace_admission","network_canary_errno":exc.errno,"pid_in_namespace":os.getpid(),
               "route_table":pathlib.Path('/proc/net/route').read_text().splitlines(),"started_monotonic":time.monotonic()}
    print(json.dumps(isolation),file=sys.stderr,flush=True)
finally:test.close()
if (source/'.env').exists():raise RuntimeError("source dotenv not admitted")
os.chdir(source);sys.path.insert(0,str(source))
try:runpy.run_module('tui_gateway.entry',run_name='__main__')
finally:
    usage=resource.getrusage(resource.RUSAGE_SELF)
    print(json.dumps({"type":"fixture_entry_exit","user_cpu_s":usage.ru_utime,"kernel_cpu_s":usage.ru_stime,"max_rss_kib":usage.ru_maxrss}),file=sys.stderr,flush=True)
