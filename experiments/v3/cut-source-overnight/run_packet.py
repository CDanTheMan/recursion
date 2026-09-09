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

def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,timeout=30)
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
    assert usage['remaining_percent']>3 and (not expensive or final or usage['remaining_percent']>10), 'capacity stop/finalize'
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

def free_memory():
    class Status(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(name,ctypes.c_ulonglong) for name in ('total_physical','available_physical','total_page','available_page','total_virtual','available_virtual','available_extended')]
    status=Status();status.length=ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)): raise OSError('host memory admission telemetry')
    return status.available_physical

class OwnedJob:
    """Anonymous Windows job; assign suspended child before allowing any descendant."""
    def __init__(self, memory=None):
        from ctypes import wintypes as w
        self.k=ctypes.WinDLL('kernel32',use_last_error=True)
        class Basic(ctypes.Structure):
            _fields_=[('process_time',ctypes.c_longlong),('job_time',ctypes.c_longlong),('flags',w.DWORD),('min_ws',ctypes.c_size_t),('max_ws',ctypes.c_size_t),('active_limit',w.DWORD),('affinity',ctypes.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
        class IO(ctypes.Structure): _fields_=[('n'+str(i),ctypes.c_ulonglong) for i in range(6)]
        class Extended(ctypes.Structure):
            _fields_=[('basic',Basic),('io',IO),('process_memory',ctypes.c_size_t),('job_memory',ctypes.c_size_t),('peak_process_memory',ctypes.c_size_t),('peak_job_memory',ctypes.c_size_t)]
        class Accounting(ctypes.Structure):
            _fields_=[('t'+str(i),ctypes.c_longlong) for i in range(4)]+[('faults',w.DWORD),('total',w.DWORD),('active',w.DWORD),('terminated',w.DWORD)]
        class Thread(ctypes.Structure):
            _fields_=[('size',w.DWORD),('usage',w.DWORD),('tid',w.DWORD),('pid',w.DWORD),('base_priority',w.LONG),('delta_priority',w.LONG),('flags',w.DWORD)]
        self.Extended,self.Accounting,self.Thread=Extended,Accounting,Thread
        signatures={'CreateJobObjectW':([ctypes.c_void_p,w.LPCWSTR],w.HANDLE),
            'SetInformationJobObject':([w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD],w.BOOL),
            'QueryInformationJobObject':([w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,ctypes.c_void_p],w.BOOL),
            'AssignProcessToJobObject':([w.HANDLE,w.HANDLE],w.BOOL),'TerminateJobObject':([w.HANDLE,w.UINT],w.BOOL),
            'CloseHandle':([w.HANDLE],w.BOOL),'CreateToolhelp32Snapshot':([w.DWORD,w.DWORD],w.HANDLE),
            'Thread32First':([w.HANDLE,ctypes.c_void_p],w.BOOL),'Thread32Next':([w.HANDLE,ctypes.c_void_p],w.BOOL),
            'OpenThread':([w.DWORD,w.BOOL,w.DWORD],w.HANDLE),'ResumeThread':([w.HANDLE],w.DWORD)}
        for name,(arguments,result) in signatures.items():
            fn=getattr(self.k,name);fn.argtypes=arguments;fn.restype=result
        self.handle=self.k.CreateJobObjectW(None,None)
        if not self.handle: raise ctypes.WinError(ctypes.get_last_error())
        limits=Extended();limits.basic.flags=0x2000  # KILL_ON_JOB_CLOSE; no breakaway.
        if memory is not None:
            limits.basic.flags|=0x100|0x200;limits.process_memory=limits.job_memory=memory
        if not self.k.SetInformationJobObject(self.handle,9,ctypes.byref(limits),ctypes.sizeof(limits)):
            self.k.CloseHandle(self.handle);raise ctypes.WinError(ctypes.get_last_error())

    def launch(self,command,**kwargs):
        process=subprocess.Popen(command,creationflags=subprocess.CREATE_NO_WINDOW|0x4,**kwargs)
        try:
            if not self.k.AssignProcessToJobObject(self.handle,int(process._handle)): raise ctypes.WinError(ctypes.get_last_error())
            snapshot=self.k.CreateToolhelp32Snapshot(0x4,0)
            if snapshot==ctypes.c_void_p(-1).value: raise ctypes.WinError(ctypes.get_last_error())
            try:
                entry=self.Thread();entry.size=ctypes.sizeof(entry);ok=self.k.Thread32First(snapshot,ctypes.byref(entry));resumed=False
                while ok:
                    if entry.pid==process.pid:
                        thread=self.k.OpenThread(0x2,False,entry.tid)
                        if not thread: raise ctypes.WinError(ctypes.get_last_error())
                        try:
                            if self.k.ResumeThread(thread)==0xffffffff: raise ctypes.WinError(ctypes.get_last_error())
                            resumed=True
                        finally: self.k.CloseHandle(thread)
                    ok=self.k.Thread32Next(snapshot,ctypes.byref(entry))
                if not resumed: raise OSError('suspended owned primary thread not found')
            finally: self.k.CloseHandle(snapshot)
            return process
        except BaseException:
            process.kill();process.wait(timeout=5);raise

    def active(self):
        value=self.Accounting()
        if not self.k.QueryInformationJobObject(self.handle,1,ctypes.byref(value),ctypes.sizeof(value),None): raise ctypes.WinError(ctypes.get_last_error())
        return value.active

    def peak(self):
        value=self.Extended()
        if not self.k.QueryInformationJobObject(self.handle,9,ctypes.byref(value),ctypes.sizeof(value),None): raise ctypes.WinError(ctypes.get_last_error())
        return value.peak_job_memory

    def stop(self):
        if not self.k.TerminateJobObject(self.handle,1): raise ctypes.WinError(ctypes.get_last_error())
        if not self.wait_idle(5): raise TimeoutError('owned job termination did not complete')

    def wait_idle(self,seconds):
        until=time.monotonic()+seconds
        while self.active():
            if time.monotonic()>until: return False
            time.sleep(.01)
        return True

    def close(self):
        try:
            if self.active(): self.stop()
        finally: self.k.CloseHandle(self.handle)

def execute(directory,queue_item,final=False):
    goal,end,usage=scope(final=final)
    assert directory.resolve().is_relative_to(cache().resolve()) and not directory.exists(), 'fresh evidence path required'
    assert not git('status','--porcelain','--untracked-files=all').strip(), 'clean committed execution required'
    head=git('rev-parse','HEAD').decode().strip()
    assert shutil.disk_usage(ROOT).free>1073741824, 'disk admission'
    available=free_memory(); assert available>3221225472, 'physical memory admission reserve'
    lock=cache()/'model.lock'; directory.mkdir(parents=True)
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY); os.write(fd,str(os.getpid()).encode()); os.close(fd)
    process=None;job=None
    try:
        sources={}
        for path in source_paths():
            assert now()<end, 'absolute deadline while snapshotting sources'
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
                   'available_physical_bytes':available,
                   'enforcement':'600-second owned-job deadline; suspended child assigned before resume; OS2GiB committed process/job cap plus sampled working/private memory and artifact bound; Python network/process audit refusal; not a network or filesystem sandbox'}
        write(directory/'admission.json',admission)
        begin=time.monotonic(); observed=0; status='finished'
        with (directory/'stdout.log').open('wb') as out,(directory/'stderr.log').open('wb') as err:
            job=OwnedJob(goal['experiment_limits']['memory_bytes']);process=job.launch(command,cwd=ROOT,stdout=out,stderr=err)
            while process.poll() is None:
                observed=max(observed,peak(process))
                size=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())
                if time.monotonic()-begin>600 or now()>=end: status='timeout'
                elif observed>goal['experiment_limits']['memory_bytes']: status='memory-limit'
                elif size>goal['experiment_limits']['artifact_bytes']: status='artifact-limit'
                if status!='finished': job.stop(); process.wait(timeout=5); break
                time.sleep(.1)
        idle=job.wait_idle(min(5,max(0,(end-now()).total_seconds())))
        execution={'status':status,'exit_code':process.returncode,'finished_at':now().isoformat(),'seconds':time.monotonic()-begin,'sampled_peak_bytes':observed,'owned_job_peak_bytes':job.peak(),'owned_job_active_after_exit':job.active(),'pid':process.pid}
        if job.active(): job.stop();execution['status']='unexpected-owned-descendant'
        terminal_size=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())
        if terminal_size>goal['experiment_limits']['artifact_bytes']: execution['status']='artifact-limit'
        elif execution['seconds']>600: execution['status']='timeout'
        execution['terminal_artifact_bytes']=terminal_size
        write(directory/'execution.json',execution)
        # Include the execution receipt itself; iterate until its decimal size stabilizes.
        for _ in range(4):
            total=sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())
            new_status='artifact-limit' if total>goal['experiment_limits']['artifact_bytes'] else execution['status']
            if execution['terminal_artifact_bytes']==total and execution['status']==new_status: break
            execution.update(terminal_artifact_bytes=total,status=new_status); write(directory/'execution.json',execution)
        print(json.dumps(execution),flush=True)
        return admission,execution
    except BaseException as error:
        if process is not None and process.poll() is None: process.kill(); process.wait()
        write(directory/'failure.json',{'error':type(error).__name__+': '+str(error),'at':now().isoformat(),'source_commit':head})
        raise
    finally:
        if job is not None: job.close()
        lock.unlink()

def containment_check(directory):
    scope(final=True)
    assert directory.resolve().is_relative_to(cache().resolve()) and not directory.exists()
    assert not git('status','--porcelain','--untracked-files=all').strip()
    directory.mkdir(parents=True);source=Path(__file__).read_bytes();head=git('rev-parse','HEAD').decode().strip()
    assert source.replace(b'\r\n',b'\n')==git('show',head+':'+CODE+'run_packet.py').replace(b'\r\n',b'\n')
    (directory/'run_packet.py').write_bytes(source)
    write(directory/'admission.json',{'source_commit':head,'source_sha256':sha(source),'started_at':now().isoformat(),'scope':'owned process containment tests only; no source model or historical gate','deadline_seconds':30})
    cases=[]
    try:
        job=OwnedJob()
        try:
            process=job.launch([sys.executable,'-B','-c','print("contained-normal")'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            raw=process.communicate(timeout=10)[0];(directory/'normal.log').write_bytes(raw)
            idle=job.wait_idle(5)
            state={'returncode':process.returncode,'active':job.active(),'output':raw.decode('utf-8',errors='replace'),'settled':idle}
            write(directory/'normal-state.json',state)
            assert process.returncode==0 and raw.strip()==b'contained-normal' and state['active']==0, state
            cases.append('normal-exit-no-descendants')
        finally:job.close()
        job=OwnedJob()
        try:
            program='import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-B","-c","import time; time.sleep(60)"]); print(p.pid,flush=True); time.sleep(60)'
            process=job.launch([sys.executable,'-B','-c',program],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            until=time.monotonic()+10
            while job.active()<2:
                assert time.monotonic()<until,'descendant did not start';time.sleep(.01)
            before=job.active();job.stop();raw=process.communicate(timeout=5)[0]
            (directory/'terminated-tree.log').write_bytes(raw)
            assert before==2 and job.active()==0 and process.returncode!=0, {'before':before,'active':job.active(),'returncode':process.returncode}
            cases.append('owned-parent-and-grandchild-terminated')
        finally:job.close()
        job=OwnedJob(64*1024*1024)
        try:
            process=job.launch([sys.executable,'-B','-c','x=bytearray(128*1024*1024);print("unexpected allocation")'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            raw=process.communicate(timeout=10)[0]
            (directory/'memory-limit.log').write_bytes(raw)
            job.wait_idle(5)
            assert process.returncode!=0 and b'MemoryError' in raw and job.peak()<=64*1024*1024 and job.active()==0, {'returncode':process.returncode,'active':job.active(),'peak':job.peak(),'output':raw.decode('utf-8',errors='replace')}
            cases.append('job-committed-memory-cap-refuses-allocation')
        finally:job.close()
        write(directory/'result.json',{'status':'CONTAINMENT_PASS','source_commit':head,'source_sha256':sha(source),'cases':cases,'finished_at':now().isoformat()})
        print('CONTAINMENT_PASS',flush=True)
    except BaseException as error:
        write(directory/'failure.json',{'error':type(error).__name__+': '+str(error),'at':now().isoformat()});raise

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);p.add_argument('--queue-item');p.add_argument('--containment-check',action='store_true');a=p.parse_args()
    if a.containment_check: containment_check(a.directory)
    else:
        assert a.queue_item is not None
        admission,result=execute(a.directory,a.queue_item);raise SystemExit(0 if result['exit_code']==0 and result['status']=='finished' else 1)
