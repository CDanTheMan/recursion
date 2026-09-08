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
import subprocess

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
mock=None
if os.environ.get('RECURSION_PUBLIC_REAL_AGENT')=='1':
    subprocess.run(['/usr/sbin/ip','link','set','lo','up'],check=True,timeout=3)
    with socket.socket() as external:
        external.settimeout(1)
        try:
            external.connect(('192.0.2.1',443))
            raise RuntimeError('external route appeared after loopback activation')
        except OSError as exc:
            if exc.errno!=errno.ENETUNREACH:raise
            print(json.dumps({'type':'post_loopback_network_canary','errno':exc.errno}),file=sys.stderr,flush=True)
    from mock_chat import MockChat
    mock=MockChat();mock.start()
    # Final route is frozen and emitted before importing/launching the gateway.
    import yaml
    config_path=pathlib.Path(os.environ['HERMES_HOME'])/'config.yaml'
    config=yaml.safe_load(config_path.read_text());config['model']['base_url']=mock.url
    config_path.write_text(yaml.safe_dump(config,sort_keys=True))
    import hashlib
    print(json.dumps({'type':'effective_fixture_route','provider':'custom','interface':'chat_completions',
                      'url':mock.url,'config_sha256':hashlib.sha256(config_path.read_bytes()).hexdigest(),
                      'configuration':config,'inference':False}),file=sys.stderr,flush=True)
os.chdir(source);sys.path.insert(0,str(source))
try:runpy.run_module('tui_gateway.entry',run_name='__main__')
finally:
    if mock:
        mock.close()
        print(json.dumps({'type':'scripted_chat_receipt','requests':mock.requests,'errors':mock.errors,'active':mock.active,'simulated_usage':True}),file=sys.stderr,flush=True)
    usage=resource.getrusage(resource.RUSAGE_SELF)
    print(json.dumps({"type":"fixture_entry_exit","user_cpu_s":usage.ru_utime,"kernel_cpu_s":usage.ru_stime,"max_rss_kib":usage.ru_maxrss}),file=sys.stderr,flush=True)
