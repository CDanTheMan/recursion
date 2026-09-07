"""Unmodified Hermes Gateway + upstream synthetic agent, isolated Linux network/PID namespace."""
import argparse
import datetime
import hashlib
import json
import pathlib
import subprocess
import threading
import time
import sys
from win_process import Job,Process,minimal_env
from rpc import Rpc,validate_trace

BASE='/root/RecursionProbeLab/interface-20260907'
PIN='693641aa8b4359c602283bdbbc14041e03bc47bc'
WSL='C:/Windows/System32/wsl.exe'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def linux(args,**kwargs):return subprocess.run([WSL,'--distribution','Ubuntu-24.04','--exec',*args],**kwargs)

def run(lab):
    if sys.flags.optimize: raise RuntimeError('Probe oracles require assertions enabled')
    ident=datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S%f')
    output=lab/'private'/('hermes-'+ident);output.mkdir()
    folder=BASE+'/runs/'+ident; source=BASE+'/hermes-agent-'+PIN
    config='''model:\n  default: synthetic-heavy\n  provider: custom\n  base_url: http://127.0.0.1:9/v1\nauxiliary:\n  title_generation:\n    enabled: false\n  background_review:\n    enabled: false\nmcp_servers: {}\n'''
    setup="import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.mkdir(parents=True,exist_ok=False); [(p/x).mkdir() for x in ('home','hermes','codex','fixture','tmp')]; (p/'hermes/config.yaml').write_text(sys.argv[2]); (p/'entry.py').write_bytes(sys.stdin.buffer.read())"
    wrapper=pathlib.Path(__file__).with_name('hermes_fixture_entry.py')
    r=linux(['python3','-c',setup,folder,config],input=wrapper.read_bytes(),capture_output=True,timeout=30)
    if r.returncode:raise RuntimeError(r.stderr.decode())
    inv=linux([BASE+'/venv/bin/python',BASE+'/pip.pyz','freeze','--all'],capture_output=True,text=True,timeout=30)
    if inv.returncode:raise RuntimeError(inv.stderr)
    (output/'dependencies.txt').write_text(inv.stdout)
    env=['PATH=/usr/bin:/bin','HOME='+folder+'/home','HERMES_HOME='+folder+'/hermes','CODEX_HOME='+folder+'/codex','TMPDIR='+folder+'/tmp',
         'HERMES_ISO_CERTIFY_SYNTH_TURN=1','HERMES_IGNORE_RULES=1','PYTHONNOUSERSITE=1','PYTHONDONTWRITEBYTECODE=1','PYTHONUNBUFFERED=1','TERM=dumb']
    command=[WSL,'--distribution','Ubuntu-24.04','--cd',source,'--exec','unshare','--user','--map-root-user','--net','--pid','--fork','--mount-proc','--kill-child=KILL',
             '/usr/bin/timeout','--signal=TERM','--kill-after=2s','90s','env','-i',*env,BASE+'/venv/bin/python','-X','utf8','-B','-u',folder+'/entry.py',source]
    admission={'at':now(),'kind':'unmodified-upstream-entry-with-upstream-synthetic-agent','source_pin':PIN,
               'source_archive_sha256':sha(lab/'sources/hermes-source.tar.gz'),'dependencies_sha256':sha(output/'dependencies.txt'),
               'tooling':{p.name:sha(p) for p in pathlib.Path(__file__).parent.glob('*.py')},'configuration':config,
               'command':command,'max_seconds':110,'model_calls':0,'credentials':'absent','allowed_effects':'isolated fixture files and processes; namespace network canary must fail before Gateway import',
               'cleanup':'close public sessions and stdin; await unshare namespace owner exit; outer Windows Job fallback and Linux timeout',
               'coverage':'synthetic completion and interrupt lifecycle plus malformed protocol negatives; history returned by this seam is observed but cannot certify normal-agent persistence; no actual model or quota result'}
    (output/'admission.json').write_text(json.dumps(admission,indent=2)+'\n');(output/'tooling').mkdir()
    for p in pathlib.Path(__file__).parent.glob('*.py'):(output/'tooling'/p.name).write_bytes(p.read_bytes())
    job=Job();process=rpc=None;failure=None;outcomes=[];timed_out=threading.Event();namespace_exit=None
    def expire():timed_out.set();job.terminate()
    watchdog=threading.Timer(110,expire);watchdog.daemon=True;watchdog.start()
    try:
        process=Process(command,output,minimal_env(),job);rpc=Rpc(process)
        ready=rpc.event('event',seconds=30,match=lambda x:x['params'].get('type')=='gateway.ready');outcomes.append({'check':'gateway_ready','result':ready})
        rpc.send_raw(b'{not-json}\n')
        bad=rpc.wait(lambda x:x.get('error',{}).get('code')==-32700);outcomes.append({'check':'malformed_json','result':bad})
        unknown=rpc.request('public.fixture.unknown',{},allow_error=True);assert unknown['error']['code']==-32601
        invalid=rpc.request('session.create',[],allow_error=True);assert invalid['error']['code']==-32602
        outcomes.extend([{'check':'unknown_method','result':unknown},{'check':'invalid_params','result':invalid}])
        created=rpc.request('session.create',{'cwd':folder+'/fixture','title':'Public synthetic fixture'});sid=created['result']['session_id'];outcomes.append({'check':'session_create','result':created})
        normal={'duration_s':.2,'chunk':1000,'delta_interval_s':.02,'tokens_per_delta':1}
        submit=rpc.request('prompt.submit',{'session_id':sid,'text':json.dumps(normal)});outcomes.append({'check':'normal_submit','result':submit})
        done=rpc.event('event',match=lambda x:x['params'].get('type')=='message.complete' and x['params'].get('session_id')==sid)
        outcomes.append({'check':'normal_terminal','result':done})
        assert 'interrupted=False' in json.dumps(done),done
        normal_terminal_seq=done['params']['seq']
        history=rpc.request('session.history',{'session_id':sid});outcomes.append({'check':'history','result':history})
        outcomes.append({'check':'history_applicability','status':'unsupported_by_synthetic_seam','reason':'SyntheticHeavyAgent updates RAM only; session.history prefers existing DB even when its message list is empty. This is not a normal-agent persistence test.'})
        long={'duration_s':5,'chunk':1000,'delta_interval_s':.02,'tokens_per_delta':1}
        submit=rpc.request('prompt.submit',{'session_id':sid,'text':json.dumps(long)})
        second_start=rpc.event('event',match=lambda x:x['params'].get('type')=='message.start' and x['params'].get('session_id')==sid and x['params'].get('seq',-1)>normal_terminal_seq)
        delta=rpc.event('event',match=lambda x:x['params'].get('type')=='message.delta' and x['params'].get('session_id')==sid and x['params'].get('seq',-1)>second_start['params']['seq'])
        interrupted=rpc.request('session.interrupt',{'session_id':sid})
        done=rpc.event('event',match=lambda x:x['params'].get('type')=='message.complete' and x['params'].get('session_id')==sid and x['params'].get('seq',-1)>delta['params']['seq'])
        outcomes.append({'check':'interrupt_after_delta','second_start':second_start,'delta':delta,'ack':interrupted,'terminal':done})
        assert 'interrupted=True' in json.dumps(done),done
        closed=rpc.request('session.close',{'session_id':sid});outcomes.append({'check':'session_close','result':closed})
        process.stdin.close();namespace_exit=process.wait(15);outcomes.append({'check':'namespace_owner_exit','exit_code':namespace_exit})
        assert namespace_exit==0,namespace_exit
    except BaseException as exc:failure=type(exc).__name__+': '+str(exc)
    finally:
        if process and namespace_exit is None:
            try:
                if not process.stdin.closed:process.stdin.close()
                namespace_exit=process.wait(15)
                outcomes.append({'check':'namespace_owner_exit_on_cleanup','exit_code':namespace_exit})
            except BaseException as exc:
                outcomes.append({'check':'linux_cleanup','status':'unknown_until_scoped_audit','reason':type(exc).__name__})
        watchdog.cancel();watchdog.join(timeout=5)
        job.terminate()
        if process:
            try:process.wait(10)
            except BaseException as exc:failure=(failure or '')+' cleanup: '+str(exc)
        trace=rpc.finish() if rpc else None
        accounting=job.accounting()
        if process:process.close()
        job.close()
        try:
            validate_trace(trace)
            namespace=[json.loads(e['payload']) for e in trace['events'] if e['direction']=='stderr' and e['payload'].startswith('{') and 'namespace_admission' in e['payload']]
            assert len(namespace)==1 and namespace[0]['network_canary_errno']==101
            assert accounting['ActiveProcesses']==0 and not timed_out.is_set() and not watchdog.is_alive()
            assert namespace_exit is not None,'Linux namespace exit unobserved; Windows Job settlement is insufficient'
        except BaseException as exc:failure=(failure or '')+' final observation: '+str(exc)
        result={'admission_sha256':sha(output/'admission.json'),'ended_at':now(),'failure':failure,'outcomes':outcomes,'trace':trace,'cleanup_job':accounting,'namespace_owner_exit_code':namespace_exit,'watchdog_fired':timed_out.is_set(),'actual_model_calls':0,'usage_counters':'upstream synthetic counters, not provider usage'}
        (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return {'result':str(output/'result.json'),'failure':failure,'active_owned_processes':accounting['ActiveProcesses']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--lab',type=pathlib.Path,required=True);args=parser.parse_args()
    result=run(args.lab);print(json.dumps(result));raise SystemExit(bool(result['failure']))
