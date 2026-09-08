"""Prospectively retain an exact local-model execution and every failed attempt."""
import datetime,hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]

def main():
    from check import preflight
    goal=preflight();now=datetime.datetime.now(datetime.timezone.utc)
    deadline=datetime.datetime.fromisoformat(goal['deadline_utc'].replace('Z','+00:00'))
    if now+datetime.timedelta(seconds=900,minutes=goal['synthesis_review_reserve_minutes'])>deadline:
        raise ValueError('Preserve campaign synthesis/review reserve; no new model packet')
    common=pathlib.Path(subprocess.check_output(['git','rev-parse','--path-format=absolute','--git-common-dir'],cwd=ROOT,text=True).strip())
    out=common/'research-attestations/formal-comparison/discovery'/now.strftime('%Y%m%dT%H%M%S%f');out.mkdir(parents=True,exist_ok=False)
    files=[*pathlib.Path(__file__).parent.glob('*.py'),ROOT/'docs/v3/construction/formal-comparison-20260907/domains.json']
    sources={}
    for source in files:
        relative=source.relative_to(ROOT).as_posix();raw=source.read_bytes();sources[relative]=hashlib.sha256(raw).hexdigest()
        target=out/'snapshot'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    command=[sys.executable,'-X','utf8','-B','experiments/v3/formal-comparison/experiment.py','--output',str(out/'result.json')]
    admission={'recorded_at':now.isoformat(),'candidate':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
               'python_version':sys.version,'python_executable_sha256':hashlib.sha256(pathlib.Path(sys.executable).read_bytes()).hexdigest(),
               'command':command,'sources':sources,'timeout_seconds':900,'allowed_effects':'Local deterministic finite-state exploration, immutable oracle inspection and external result writes; no harness/socket/account/provider calls','new_metered_spend':0,'formal_freeze':False}
    (out/'admission.json').write_text(json.dumps(admission,indent=2)+'\n');print('ADMITTED_FINITE_MODEL_RUN '+str(out),flush=True)
    with (out/'output.log').open('wb') as log:
        try:process=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=900,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1'));code=process.returncode
        except subprocess.TimeoutExpired:
            (out/'timeout.json').write_text(json.dumps({'status':'exploration-limit','timeout_seconds':900,'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'child_killed_by_subprocess_timeout':True},indent=2)+'\n');code=2
    print('FINITE_MODEL_RUN_EXIT '+json.dumps({'code':code,'directory':str(out)}),flush=True);return code

if __name__=='__main__':raise SystemExit(main())
