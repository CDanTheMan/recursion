"""Six real Windows ownership fault cases. Outer Job prevents abandoned fixtures."""
import argparse
import ctypes as C
from ctypes import wintypes as W
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import threading
import time
import uuid
from win_process import (Job, Process, minimal_env, OpenProcess, OpenJob, CloseHandle,
                         IsInJob, Wait, TerminateProcess, ok, process_identity)

def emit(value):print(json.dumps(value),flush=True)
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def require(condition,message):
    if not condition:raise ValueError(message)

def validate_barrier(value,mode,boundary,name):
    require(isinstance(value,dict),"barrier must be an object")
    require(value.get("boundary")==boundary and value.get("target_job")==name,"wrong barrier identity")
    pids=value.get("pids")
    require(isinstance(pids,list) and len(pids)==(2 if boundary=="descendant" else 1),"wrong PID cardinality")
    require(all(type(x) is int and x>0 for x in pids) and len(set(pids))==len(pids),"invalid or duplicate PID")
    require(len(value.get("identities",[]))==len(pids),"missing creator identities")
    return pids

def descendant():
    child=subprocess.Popen([sys.executable,"-X","utf8","-B","-c","import time; time.sleep(120)"],close_fds=True)
    emit({"descendant_pid":child.pid})
    time.sleep(120)

def broker(mode,boundary,name,cwd):
    target=Job(name=name,max_processes=8,memory_bytes=512*1024**2)
    args=[sys.executable,"-X","utf8","-B",str(pathlib.Path(__file__).resolve()),"--descendant"] if boundary=="descendant" else [sys.executable,"-X","utf8","-B","-c","import time; time.sleep(120)"]
    process=Process(args,cwd,minimal_env(),target if mode=="at_birth" else None,suspended=True)
    if mode=="post_create" and boundary!="created":target.assign(process)
    pids=[process.pid]
    if boundary=="descendant":
        process.resume();value=json.loads(process.stdout.readline(65536));pids.append(value["descendant_pid"])
    identities=[]
    for pid in pids:
        handle=ok(OpenProcess(0x1000,False,pid))
        try:identities.append(process_identity(handle))
        finally:ok(CloseHandle(handle))
    emit({"boundary":boundary,"pids":pids,"identities":identities,"target_job":name,"product_registration":"not_performed"})
    # Driver terminates us externally, bypassing Python cleanup and normal exit.
    sys.stdin.buffer.read(1)
    target.terminate();process.close();target.close()

def observe_case(mode,boundary,folder):
    outer=Job(max_processes=16,memory_bytes=1024**3);process=None;handles=[];errors=[]
    fired=threading.Event()
    def timeout():
        fired.set();outer.terminate()
    timer=threading.Timer(30,timeout);timer.daemon=True;timer.start()
    name="Local\\recursion_probe_"+uuid.uuid4().hex
    result={"mode":mode,"boundary":boundary,"started_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"outer_safety_job":True}
    try:
        args=[sys.executable,"-X","utf8","-B",str(pathlib.Path(__file__).resolve()),"--broker",mode,boundary,name,str(folder)]
        process=Process(args,folder,minimal_env(),outer)
        result["broker_identity"]=process_identity(process.handle)
        value=json.loads(process.stdout.readline(65536));result["barrier"]=value
        for pid in validate_barrier(value,mode,boundary,name):
            handle=ok(OpenProcess(0x100000|0x1000|0x1,False,pid))
            owned=W.BOOL()
            try:
                ok(IsInJob(handle,outer.handle,C.byref(owned)))
                require(owned.value,"PID is outside this test's safety Job")
                require(sha(process_identity(handle)["image"])==sha(sys.executable),"unexpected child executable")
            except BaseException:CloseHandle(handle);raise
            handles.append(handle)
        result["identities"]=[process_identity(h) for h in handles]
        require(result["identities"]==value["identities"],"creator/observer process identity mismatch")
        query=ok(OpenJob(0x4,False,name))
        try:
            membership=[]
            for h in handles:
                member=W.BOOL();ok(IsInJob(h,query,C.byref(member)));membership.append(bool(member.value))
            result["target_membership_before_crash"]=membership
        finally:ok(CloseHandle(query))
        result["observer_job_handle_closed_before_crash"]=True
        result["live_immediately_before_crash"]=[Wait(h,0)==258 for h in handles]
        result["broker_live_before_crash"]=process.poll() is None
        require(all(result["live_immediately_before_crash"]) and result["broker_live_before_crash"],"process exited before causal crash test")
        require(not fired.is_set(),"safety watchdog contaminated observation")
        process.terminate();result["broker_exit"]=process.wait(5)
        survived=[]
        for h in handles:
            wait=Wait(h,2000)
            if wait not in (0,258):raise RuntimeError("wait failed")
            survived.append(wait==258)
        result["survived_broker_death"]=survived
        expected_gap=mode=="post_create" and boundary=="created"
        require(not fired.is_set(),"safety watchdog contaminated termination")
        require(all(x==(not expected_gap) for x in membership),"unexpected target membership")
        require(all(x==expected_gap for x in survived),"unexpected survival")
        result["oracle"]="expected_operation_scope_gap_observed" if expected_gap else "target_scope_contained_and_terminated"
    except BaseException as exc:errors.append(type(exc).__name__+": "+str(exc))
    finally:
        try:
            for h in handles:
                try:
                    if Wait(h,0)==258:ok(TerminateProcess(h,125))
                    if Wait(h,5000)!=0:errors.append("observed child cleanup not signaled")
                except BaseException as exc:errors.append("child cleanup: "+str(exc))
                finally:CloseHandle(h)
        finally:
            try:
                outer.terminate()
                if process:
                    try:process.wait(5)
                    except TimeoutError:errors.append("broker cleanup timeout")
                deadline=time.monotonic()+5
                while outer.accounting()["ActiveProcesses"] and time.monotonic()<deadline:time.sleep(.01)
                result["cleanup"]=outer.accounting()
            except BaseException as exc:
                errors.append("outer cleanup: "+str(exc));result["cleanup"]={"ActiveProcesses":None}
            finally:
                timer.cancel();timer.join(timeout=5)
                result["watchdog_fired"]=fired.is_set()
                if fired.is_set():errors.append("safety watchdog fired; causal oracle invalid")
                if process:process.close()
                if timer.is_alive():errors.append("watchdog callback not settled")
                else:outer.close()
        result["errors"]=errors
        result["ended_at"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
    return result

def packet(lab):
    folder=lab/"private"/("ownership-"+datetime.datetime.now(datetime.timezone.utc).strftime("%H%M%S%f"));folder.mkdir()
    admission={"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"kind":"native-windows-owned-process-fault-probe",
               "tooling":{p.name:sha(p) for p in pathlib.Path(__file__).parent.glob('*.py')},"python_sha256":sha(sys.executable),
               "treatments":["post_create","at_birth"],"executions":[{"mode":mode,"boundary":boundary} for mode in ("post_create","at_birth") for boundary in ("created","associated","descendant")],
               "max_treatments":2,"max_executions":6,"max_seconds_per_execution":30,"external_effects":"owned public fixture processes only",
               "checkpoint_note":"At-birth created and associated are the same membership checkpoint repeated; no separate assignment is performed.",
               "network":"no fixture network code or credentials","outer_safety_job":"distinct from measured operation Job; no orphan left after test",
               "oracle":"specific operation Job membership before crash, retained process handles signaled after broker death, all owned scopes empty after cleanup"}
    (folder/"admission.json").write_text(json.dumps(admission,indent=2)+"\n")
    (folder/"tooling").mkdir()
    for p in pathlib.Path(__file__).parent.glob('*.py'):(folder/"tooling"/p.name).write_bytes(p.read_bytes())
    results=[observe_case(case["mode"],case["boundary"],folder) for case in admission["executions"]]
    result={"admission_sha256":sha(folder/"admission.json"),"results":results,"model_calls":0,"scope":"This host, ordinary descendants and explicit post-return barriers only; not hostile escape or crashes inside CreateProcess."}
    path=folder/"result.json";path.write_text(json.dumps(result,indent=2)+"\n")
    emit({"result":str(path),"cases":len(results),"errors":[r["errors"] for r in results if r["errors"]],"oracles":[r.get("oracle") for r in results],"active_after_cleanup":[r["cleanup"]["ActiveProcesses"] for r in results]})
    return any(r["errors"] or r["cleanup"]["ActiveProcesses"] for r in results)

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--descendant",action="store_true");parser.add_argument("--broker",nargs=4);parser.add_argument("--lab",type=pathlib.Path)
    args=parser.parse_args()
    if args.descendant:descendant()
    elif args.broker:broker(*args.broker)
    else:raise SystemExit(packet(args.lab))
