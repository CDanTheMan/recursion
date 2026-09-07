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
from release import reserve

BASE='/root/RecursionProbeLab/interface-20260907'
PIN='693641aa8b4359c602283bdbbc14041e03bc47bc'
WSL='C:/Windows/System32/wsl.exe'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def linux(args,**kwargs):return subprocess.run([WSL,'--distribution','Ubuntu-24.04','--exec',*args],**kwargs)

def run(lab, mode, packet):
    if sys.flags.optimize: raise RuntimeError('Probe oracles require assertions enabled')
    release=reserve(packet,lab,'hermes-'+mode,1)
    ident=datetime.datetime.now(datetime.timezone.utc).strftime('%H%M%S%f')
    output=lab/'private'/('hermes-'+mode+'-'+ident);output.mkdir()
    folder=BASE+'/runs/'+ident; source=BASE+'/hermes-agent-'+PIN
    config='''model:\n  default: synthetic-heavy\n  provider: custom\n  base_url: http://127.0.0.1:9/v1\nauxiliary:\n  title_generation:\n    enabled: false\n  background_review:\n    enabled: false\nmcp_servers: {}\n'''
    if mode=='real':
        config=json.dumps({'model':{'default':'public-fixture-model','provider':'custom','base_url':'http://127.0.0.1:9/v1','api_mode':'chat_completions','api_key':'fixture-only','streaming':True,'context_length':65536,'max_tokens':128},
                           'agent':{'max_turns':2,'api_max_retries':1,'reasoning_effort':False},
                           'compression':{'enabled':False,'micro_compact':False},'fallback_providers':[],'fallback_model':None,
                           'auxiliary':{'title_generation':{'enabled':False},'background_review':{'enabled':False}},
                           'tools':{'tool_search':{'enabled':False}},'mcp_servers':{}})
    setup="import pathlib,sys; p=pathlib.Path(sys.argv[1]); p.mkdir(parents=True,exist_ok=False); [(p/x).mkdir() for x in ('home','hermes','codex','fixture','tmp')]; (p/'hermes/config.yaml').write_text(sys.argv[2]); (p/'entry.py').write_bytes(sys.stdin.buffer.read())"
    wrapper=pathlib.Path(__file__).with_name('hermes_fixture_entry.py')
    r=linux(['python3','-c',setup,folder,config],input=wrapper.read_bytes(),capture_output=True,timeout=30)
    if r.returncode:raise RuntimeError(r.stderr.decode())
    if mode=='real':
        r=linux(['python3','-c','import pathlib,sys;pathlib.Path(sys.argv[1]).write_bytes(sys.stdin.buffer.read())',folder+'/mock_chat.py'],input=wrapper.with_name('mock_chat.py').read_bytes(),capture_output=True,timeout=30)
        if r.returncode:raise RuntimeError(r.stderr.decode())
    inv=linux([BASE+'/venv/bin/python',BASE+'/pip.pyz','freeze','--all'],capture_output=True,text=True,timeout=30)
    if inv.returncode:raise RuntimeError(inv.stderr)
    (output/'dependencies.txt').write_text(inv.stdout)
    env=['PATH=/usr/bin:/bin','HOME='+folder+'/home','HERMES_HOME='+folder+'/hermes','CODEX_HOME='+folder+'/codex','TMPDIR='+folder+'/tmp',
         'HERMES_IGNORE_RULES=1','PYTHONNOUSERSITE=1','PYTHONDONTWRITEBYTECODE=1','PYTHONUNBUFFERED=1','TERM=dumb']
    env+=['HERMES_ISO_CERTIFY_SYNTH_TURN=1'] if mode=='synthetic' else ['RECURSION_PUBLIC_REAL_AGENT=1','HERMES_TUI_PROVIDER=custom','HERMES_TUI_TOOLSETS=bot_room']
    command=[WSL,'--distribution','Ubuntu-24.04','--cd',source,'--exec','unshare','--user','--map-root-user','--net','--pid','--fork','--mount-proc','--kill-child=KILL',
             '/usr/bin/timeout','--signal=TERM','--kill-after=2s','90s','env','-i',*env,BASE+'/venv/bin/python','-X','utf8','-B','-u',folder+'/entry.py',source]
    admission={'at':now(),'packet_release':release,'kind':'unmodified-upstream-entry-with-'+('upstream-synthetic-agent' if mode=='synthetic' else 'real-agent-and-scripted-provider'),'mode':mode,'source_pin':PIN,
               'source_archive_sha256':sha(lab/'sources/hermes-source.tar.gz'),'dependencies_sha256':sha(output/'dependencies.txt'),
               'tooling':{p.name:sha(p) for p in pathlib.Path(__file__).parent.glob('*.py')},'configuration':config,
               'command':command,'max_seconds':110,'model_calls':0,'credentials':'absent' if mode=='synthetic' else 'public dummy string only',
               'allowed_effects':'isolated fixture files and processes; namespace network canary must fail before Gateway import; real mode loopback route finalized and emitted before upstream import',
               'cleanup':'close public sessions and stdin; await unshare namespace owner exit; outer Windows Job fallback and Linux timeout',
               'coverage':('synthetic completion and interrupt lifecycle; history unsupported by seam' if mode=='synthetic' else 'real agent-loop completion, persistence, interrupt and same-process close/resume with scripted provider')+'; malformed protocol negatives; no actual model or quota result'}
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
        submit=rpc.request('prompt.submit',{'session_id':sid,'text':json.dumps(normal) if mode=='synthetic' else 'PUBLIC_PERSISTENCE_PROMPT'});outcomes.append({'check':'normal_submit','result':submit})
        done=rpc.event('event',match=lambda x:x['params'].get('type')=='message.complete' and x['params'].get('session_id')==sid)
        outcomes.append({'check':'normal_terminal','result':done})
        assert (('interrupted=False' in json.dumps(done)) if mode=='synthetic' else done['params']['payload']['status']=='complete'),done
        normal_terminal_seq=done['params']['seq']
        history=rpc.request('session.history',{'session_id':sid});outcomes.append({'check':'history','result':history})
        first_history=history['result']['messages']
        if mode=='synthetic':
            outcomes.append({'check':'history_applicability','status':'unsupported_by_synthetic_seam','reason':'SyntheticHeavyAgent updates RAM only; session.history prefers existing DB even when its message list is empty. This is not a normal-agent persistence test.'})
        else:
            assert 'PUBLIC_PERSISTENCE_PROMPT' in json.dumps(history) and 'PUBLIC_HISTORY_COMPLETE' in json.dumps(history),history
        long={'duration_s':5,'chunk':1000,'delta_interval_s':.02,'tokens_per_delta':1}
        submit=rpc.request('prompt.submit',{'session_id':sid,'text':json.dumps(long) if mode=='synthetic' else 'PUBLIC_INTERRUPT_PROMPT'})
        second_start=rpc.event('event',match=lambda x:x['params'].get('type')=='message.start' and x['params'].get('session_id')==sid and x['params'].get('seq',-1)>normal_terminal_seq)
        delta=rpc.event('event',match=lambda x:x['params'].get('type')=='message.delta' and x['params'].get('session_id')==sid and x['params'].get('seq',-1)>second_start['params']['seq'])
        interrupted=rpc.request('session.interrupt',{'session_id':sid})
        done=rpc.event('event',match=lambda x:x['params'].get('type')=='message.complete' and x['params'].get('session_id')==sid and x['params'].get('seq',-1)>delta['params']['seq'])
        outcomes.append({'check':'interrupt_after_delta','second_start':second_start,'delta':delta,'ack':interrupted,'terminal':done})
        assert (('interrupted=True' in json.dumps(done)) if mode=='synthetic' else done['params']['payload']['status']=='interrupted'),done
        if mode=='real':
            active=rpc.request('session.activate',{'session_id':sid})
            outcomes.append({'check':'postinterrupt_active','result':active})
            assert active['result']['running'] is False and active['result']['info']['running'] is False,'interrupt not settled in session state'
            history=rpc.request('session.history',{'session_id':sid})
            outcomes.append({'check':'postinterrupt_durable_history','result':history})
            assert 'PUBLIC_INTERRUPT_PARTIAL' in json.dumps(history),history
            assert history['result']['messages'][:len(first_history)]==first_history,'interruption dropped prior history'
            durable_ids=[m['row_id'] for m in history['result']['messages']]
            assert all(type(i) is int and i>0 for i in durable_ids) and len(set(durable_ids))==len(durable_ids),'durable row identity missing'
            infos=[e['payload']['params']['payload'] for e in rpc.events if e['direction']=='receive' and isinstance(e['payload'],dict) and e['payload'].get('method')=='event' and e['payload']['params'].get('type')=='session.info' and e['payload']['params'].get('session_id')==sid]
            assert infos and all(info.get('tools',{})=={} for info in infos),infos
            stored=infos[-1]['stored_session_id']
        closed=rpc.request('session.close',{'session_id':sid});outcomes.append({'check':'session_close','result':closed})
        assert closed['result']['closed'] is True,'session did not close'
        if mode=='real':
            resumed=rpc.request('session.resume',{'session_id':stored})
            outcomes.append({'check':'same_process_stored_session_resume','result':resumed})
            resumed_sid=resumed['result']['session_id']
            assert resumed_sid!=sid and resumed['result']['resumed']==stored and resumed['result']['session_key']==stored,'resume identity drift'
            after=rpc.request('session.history',{'session_id':resumed_sid})
            outcomes.append({'check':'same_process_resumed_history','result':after})
            assert after['result']['messages']==history['result']['messages'],after
            rpc.request('session.close',{'session_id':resumed_sid})
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
            if mode=='real':
                receipts=[json.loads(e['payload']) for e in trace['events'] if e['direction']=='stderr' and e['payload'].startswith('{') and 'scripted_chat_receipt' in e['payload']]
                assert len(receipts)==1,'missing or repeated scripted chat receipt'
                assert not receipts[0]['errors'] and receipts[0]['active']==0,receipts[0]['errors']
                assert sum(r['method']=='POST' for r in receipts[0]['requests'])==2,'scripted POST count differs from two'
        except BaseException as exc:failure=(failure or '')+' final observation: '+str(exc)
        result={'admission_sha256':sha(output/'admission.json'),'ended_at':now(),'mode':mode,'failure':failure,'outcomes':outcomes,'trace':trace,'cleanup_job':accounting,'namespace_owner_exit_code':namespace_exit,'watchdog_fired':timed_out.is_set(),'actual_model_calls':0,'usage_counters':'synthetic agent or scripted provider counters, not model usage'}
        (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return {'result':str(output/'result.json'),'failure':failure,'active_owned_processes':accounting['ActiveProcesses']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--lab',type=pathlib.Path,required=True);parser.add_argument('--mode',choices=['synthetic','real'],default='synthetic');parser.add_argument('--packet',type=pathlib.Path,required=True);args=parser.parse_args()
    result=run(args.lab,args.mode,args.packet);print(json.dumps(result));raise SystemExit(bool(result['failure']))
