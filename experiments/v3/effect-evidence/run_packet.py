"""Prospective frozen source/host admission with complete failed-attempt retention."""
import argparse,datetime,hashlib,json,pathlib,platform,secrets,subprocess,sys,time,importlib.metadata
ROOT=pathlib.Path(__file__).resolve().parents[3]
PREFIX='docs/v3/construction/effect-evidence-20260908/'
CODE='experiments/v3/effect-evidence/'
FROZEN=json.loads((ROOT/PREFIX/'manifest.json').read_text())['inputs']
SOURCES=[CODE+n for n in ('ee_common.py','ee_join.py','ee_cases.py','ee_experiment.py','run_packet.py')]+[PREFIX+'goal.json',PREFIX+'plan.json',PREFIX+'specification.md',PREFIX+'manifest.json']+[r['path'] for r in FROZEN if r['path'].startswith(('scripts/v3/planning/','scripts/tests/v3/integrity/','schemas/control-plane/v3/integrity/')) or r['path']=='scripts/tests/v3/planning/fixtures/F-M1A-014.json']

def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def execute(directory):
    common=pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir').decode().strip());anchor=common/'research-attestations/effect-evidence'
    if not directory.resolve().is_relative_to(anchor.resolve()) or directory.exists():raise ValueError('fresh bounded external directory required')
    goal=json.loads((ROOT/PREFIX/'goal.json').read_text());now=datetime.datetime.now(datetime.timezone.utc)
    if not datetime.datetime.fromisoformat(goal['started_at'])<=now<=datetime.datetime.fromisoformat(goal['deadline_utc']):raise ValueError('campaign execution window')
    directory.mkdir(parents=True);head=git('rev-parse','HEAD').decode().strip();files={}
    for name in SOURCES:
        raw=(ROOT/name).read_bytes();blob=git('show',head+':'+name)
        if raw.replace(b'\r\n',b'\n')!=blob.replace(b'\r\n',b'\n'):raise ValueError('uncommitted model source '+name)
        target=directory/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        files[name]={'working_sha256':hashlib.sha256(raw).hexdigest(),'git_blob_sha256':hashlib.sha256(blob).hexdigest()}
    command=[sys.executable,'-X','utf8','-B',CODE+'ee_experiment.py','--output',str(directory/'result.json'),'--keys',str(directory/'synthetic-test-keys.json')]
    plan=json.loads((ROOT/PREFIX/'plan.json').read_text());now=datetime.datetime.now(datetime.timezone.utc)
    admission={'status':'admitted-before-execution','source_commit':head,'sources':files,'started_at':now.isoformat(),'command':command,'host':{'system':platform.system(),'release':platform.release(),'version':platform.version(),'machine':platform.machine(),'python':sys.version,'executable':sys.executable},'limits':plan['limits'],'new_metered_spend':0,'network_operations_in_model':False,'os_sandbox_claimed':False}
    admission['dependencies']={'jsonschema':importlib.metadata.version('jsonschema')}
    write(directory/'admission.json',admission)
    write(directory/'synthetic-test-keys.json',{role:secrets.token_hex(32) for role in ('collector','dispatcher','observer')})
    started=time.perf_counter()
    with (directory/'stdout.log').open('wb') as out,(directory/'stderr.log').open('wb') as err:
        try:
            r=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=plan['limits']['seconds_per_experiment']);code=r.returncode;status='finished'
        except subprocess.TimeoutExpired:code=None;status='outer-timeout-owned-model-process-killed-and-waited'
    execution={'status':status,'exit_code':code,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.perf_counter()-started}
    write(directory/'execution.json',execution)
    size=sum(q.stat().st_size for q in directory.rglob('*') if q.is_file())
    if size>plan['limits']['artifact_bytes']:raise ValueError('artifact limit exceeded; evidence retained')
    return admission,execution
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--directory',required=True,type=pathlib.Path);a=parser.parse_args();ad,x=execute(a.directory);print(json.dumps(x));raise SystemExit(0 if x['exit_code']==0 else 1)
