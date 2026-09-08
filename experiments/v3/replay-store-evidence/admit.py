"""Prospective, source-pinned local admission; retains every attempted execution."""
import ctypes,datetime,hashlib,json,pathlib,platform,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
CODE='experiments/v3/replay-store-evidence/'
AREA='docs/v3/construction/replay-store-evidence-20260907/'
SOURCES=[CODE+n for n in ['fixture.py','reader.py','worker.py','experiment.py','admit.py']]+[AREA+'goal.json',AREA+'plan.json','scripts/tests/v3/execution/reference_oracle.py','schemas/control-plane/v3/execution/schema.json','scripts/tests/v3/execution/fixtures/F-M1B-020.json']
LIMITS={'child_seconds':10,'kill_wait_seconds':5,'whole_seconds':600,'artifact_bytes':67108864,'repetitions':2}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(*args,raw=False):
    b=subprocess.check_output(['git',*args],cwd=ROOT);return b if raw else b.decode().strip()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf8')
def host():
    if sys.platform!='win32':raise ValueError('admitted platform is Windows')
    name=ctypes.create_unicode_buffer(256);flags=ctypes.c_ulong();maximum=ctypes.c_ulong();serial=ctypes.c_ulong()
    ok=ctypes.windll.kernel32.GetVolumeInformationW(str(ROOT.anchor),None,0,ctypes.byref(serial),ctypes.byref(maximum),ctypes.byref(flags),name,len(name))
    if not ok:raise ctypes.WinError()
    import importlib.metadata
    return {'os':platform.platform(),'python':sys.version,'python_executable':sys.executable,'jsonschema_version':importlib.metadata.version('jsonschema'),'filesystem':name.value,'filesystem_flags':flags.value,'volume_root':ROOT.anchor}
def execute(directory):
    if git('status','--porcelain=v1','--untracked-files=all'):raise ValueError('admission requires clean source')
    directory.mkdir(parents=True,exist_ok=False);source=git('rev-parse','HEAD');rows=[]
    for path in SOURCES:
        raw=(ROOT/path).read_bytes();blob=git('show',source+':'+path,raw=True)
        if raw.replace(b'\r\n',b'\n')!=blob.replace(b'\r\n',b'\n'):raise ValueError('source differs from commit')
        dest=directory/'source'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);rows.append({'path':path,'working_sha256':sha(raw),'git_blob_sha256':sha(blob)})
    command=[sys.executable,'-X','utf8','-B',CODE+'experiment.py','--output',str(directory/'cases')]
    admission={'status':'admitted-before-execution','started_at':now(),'source_commit':source,'source_files':rows,'command':command,'host':host(),'limits':LIMITS,'new_metered_spend':0,'network':'helper audit hook denies socket/subprocess/system events; synthetic parent performs no network operation; not OS isolation','cleanup':'Retain forensic fixture files; wait all owned child handles; no service.'};save(directory/'admission.json',admission)
    execution={'status':'started','started_at':now()};save(directory/'execution.json',execution)
    with (directory/'stdout.txt').open('w',encoding='utf8') as output:
        try:r=subprocess.run(command,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,timeout=650);execution.update(status='finished',exit_code=r.returncode)
        except subprocess.TimeoutExpired:execution.update(status='timeout',exit_code=None,cleanup='incomplete: outer timeout cannot prove descendant exit; inspect retained owned PID receipts before any cleanup claim')
    execution['finished_at']=now();save(directory/'execution.json',execution);return admission,execution
if __name__=='__main__':
    common=pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'));name=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f');directory=common/'research-attestations/replay-store-evidence/discovery'/name
    a,x=execute(directory);print(json.dumps({'directory':str(directory),'source_commit':a['source_commit'],**x}));raise SystemExit(x['exit_code'] if x['exit_code'] is not None else 1)
