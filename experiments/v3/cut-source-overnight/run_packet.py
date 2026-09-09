"""Commit-bound admission and bounded owned-process execution; retains every attempt."""
import argparse
import ctypes
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
CODE='experiments/v3/cut-source-overnight/'
PREFIX='docs/v3/construction/cut-source-overnight-20260908/'

def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path,obj): path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')
def sha(raw): return hashlib.sha256(raw).hexdigest()
def now(): return dt.datetime.now(dt.timezone.utc)
def common(): return Path(git('rev-parse','--path-format=absolute','--git-common-dir').decode().strip())
def cache(): return common()/'research-attestations/cut-source-overnight'

def scope(expensive=True, final=False):
    goal=read(ROOT/PREFIX/'goal.json'); activation=read(cache()/'activation.json')['goal']
    for field in ('parent_goal','started_at','deadline_utc','discovery_cutoff_utc','allowed_paths','model','reasoning','speed','experiment_limits','new_metered_spend','usage_resets_allowed','resume_after_quota_reset'):
        assert goal[field]==activation[field], 'immutable activation '+field
    assert goal['parent_goal']=='goal-recursion-v2-execution-fabric'
    assert 'status: active' in (ROOT/'state/goals/goal-recursion-v2-execution-fabric.md').read_text()
    assert not (ROOT/'state/PAUSE').exists() and not (common().parent/'state/PAUSE').exists(), 'operational PAUSE'
    end=dt.datetime.fromisoformat(goal['deadline_utc'] if final else goal['discovery_cutoff_utc'])
    assert now()<end, 'absolute envelope expired'
    usage=read(cache()/'usage.json')
    assert 0<=(now()-dt.datetime.fromisoformat(usage['checked_at'])).total_seconds()<900, 'fresh capacity telemetry required'
    assert usage['remaining_percent']>3 and (not expensive or usage['remaining_percent']>10), 'capacity stop/finalize'
    assert usage['new_metered_spend']==0 and usage['reset_credits_used']==0
    assert git('branch','--show-current').decode().strip()==goal['branch'], 'source branch'
    changed=git('diff','--name-only',goal['start_commit']).decode().splitlines()
    allowed=goal['allowed_paths']
    assert all(p in allowed or any(x.endswith('/**') and p.startswith(x[:-2]) for x in allowed) for p in changed), 'scope paths'
    return goal,end,usage

def source_paths():
    paths={r['path'] for r in read(ROOT/PREFIX/'manifest.json')['inputs']}
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT/CODE).glob('*.py'))
    paths.update(PREFIX+n for n in ('goal.json','plan.json','specification.md','preflight.json','research-queue.json'))
    return sorted(paths)

def peak(process):
    class Memory(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
    value=Memory(); value.cb=ctypes.sizeof(value)
    fn=ctypes.windll.psapi.GetProcessMemoryInfo; fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    if not fn(int(process._handle),ctypes.byref(value),value.cb):
        if process.poll() is None: raise OSError('owned process memory telemetry failed')
        return 0
    return max(value.PeakWorkingSetSize,value.PeakPagefileUsage)

def execute(directory,queue_item,final=False):
    goal,end,usage=scope(final=final)
    assert directory.resolve().is_relative_to(cache().resolve()) and not directory.exists(), 'fresh evidence path required'
    assert not git('status','--porcelain','--untracked-files=all').strip(), 'clean committed execution required'
    head=git('rev-parse','HEAD').decode().strip()
    assert shutil.disk_usage(ROOT).free>1073741824, 'disk admission'
    lock=cache()/'model.lock'; directory.mkdir(parents=True)
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY); os.write(fd,str(os.getpid()).encode()); os.close(fd)
    process=None
    try:
        sources={}
        for path in source_paths():
            raw=(ROOT/path).read_bytes(); blob=git('show',head+':'+path)
            assert raw.replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'), 'source differs from commit '+path
            target=directory/'source'/path; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(raw)
            sources[path]={'working_sha256':sha(raw),'git_blob_sha256':sha(blob)}
        command=[sys.executable,'-X','utf8','-B',CODE+'s_experiment.py','--queue-item',queue_item,'--output',str(directory/'result.json')]
        assert (end-now()).total_seconds()>600, 'insufficient experiment reserve'
        admission={'status':'admitted-before-execution','source_commit':head,'sources':sources,'command':command,
                   'started_at':now().isoformat(),'queue_item':queue_item,'usage':usage,'limits':goal['experiment_limits'],
                   'host':{'python':sys.version,'executable':sys.executable,'system':platform.system(),'machine':platform.machine()},
                   'dependencies':{'jsonschema':importlib.metadata.version('jsonschema')},'model_network':False,
                   'enforcement':'600-second owned process deadline; 100ms sampled peak working/private bytes and artifact bound; Python network/process audit refusal; not an OS sandbox'}
        write(directory/'admission.json',admission)
        begin=time.monotonic(); observed=0; status='finished'
        with (directory/'stdout.log').open('wb') as out,(directory/'stderr.log').open('wb') as err:
            process=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
            while process.poll() is None:
                observed=max(observed,peak(process))
                size=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())
                if time.monotonic()-begin>600 or now()>=end: status='timeout'
                elif observed>goal['experiment_limits']['memory_bytes']: status='memory-limit'
                elif size>goal['experiment_limits']['artifact_bytes']: status='artifact-limit'
                if status!='finished': process.kill(); process.wait(); break
                time.sleep(.1)
        execution={'status':status,'exit_code':process.returncode,'finished_at':now().isoformat(),'seconds':time.monotonic()-begin,'sampled_peak_bytes':observed,'pid':process.pid}
        terminal_size=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())
        if terminal_size>goal['experiment_limits']['artifact_bytes']: execution['status']='artifact-limit'
        elif execution['seconds']>600: execution['status']='timeout'
        execution['terminal_artifact_bytes']=terminal_size
        write(directory/'execution.json',execution)
        print(json.dumps(execution),flush=True)
        return admission,execution
    except BaseException as error:
        if process is not None and process.poll() is None: process.kill(); process.wait()
        write(directory/'failure.json',{'error':type(error).__name__+': '+str(error),'at':now().isoformat(),'source_commit':head})
        raise
    finally:
        lock.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--queue-item',required=True);a=p.parse_args()
    admission,result=execute(a.directory,a.queue_item);raise SystemExit(0 if result['exit_code']==0 and result['status']=='finished' else 1)
