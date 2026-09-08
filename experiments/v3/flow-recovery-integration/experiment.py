"""Executable controls and bounded integration exploration; no provider calls."""
import argparse,copy,datetime,hashlib,itertools,json,pathlib,runpy,time
from jsonschema import Draft202012Validator
import domain as D
import specification as A
import split_model as S
import inclusive_model as I
from audit import Audit,advance,decision
from explore import graph,fairness,Limit,audit_binding
ROOT=pathlib.Path(__file__).resolve().parents[3]
ORACLE=runpy.run_path(str(ROOT/'scripts/tests/v3/execution/reference_oracle.py'))['replay_broker']
SCHEMA=Draft202012Validator(json.loads((ROOT/'schemas/control-plane/v3/execution/schema.json').read_text()))
FIXTURE=json.loads((ROOT/'scripts/tests/v3/execution/fixtures/F-M1B-020.json').read_text())['input']
def require(ok,message):
    if not ok:raise ValueError(message)
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def literal(messages,qb,qe):
    inp=copy.deepcopy(FIXTURE);inp.update(messages=messages,queue_limit_bytes=qb,queue_limit_events=qe);return ORACLE(inp)
def compact(messages,qb,qe):
    a=Audit()
    for message in messages:a=advance(a,message,qb,qe)
    return decision(a)
def calibrations():
    controls=json.loads((ROOT/'docs/v3/construction/reset-mapping-20260907/results.json').read_text())['controls']['literal_cases']
    long=[]
    for name,row in controls.items():
        messages=row['messages'];inp=copy.deepcopy(FIXTURE);inp['messages']=messages;SCHEMA.validate(inp)
        for length in range(1,len(messages)+1):require(compact(messages[:length],1,1)==literal(messages[:length],1,1),'prior literal control prefix '+name)
        long.append({'name':name,'prefixes':len(messages),'decision':compact(messages,1,1)})
    seed=D.Visible();alphabet=[D.wire(('credit',n),seed,'event') for n in [1,2]]+[D.wire(('emit',n),seed,'event') for n in [1,2]]+[D.wire(('ack',n),seed,'event') for n in [0,1]]
    for n in [0,1]:alphabet.append(D.wire(('hello',),seed._replace(position=n),'event'))
    for n in [0,2]:alphabet.append(D.wire(('welcome',),seed._replace(loss=n,snapshot=n),'event'));alphabet.append(D.wire(('reset',),seed._replace(snapshot=n),'event'))
    # Validate the alphabet and fixed envelope. Every generated trace is a nonempty
    # bounded list from these schema-valid messages; no empty wire fixture is claimed.
    for m in alphabet:SCHEMA.validate(m)
    count=0;digest=hashlib.sha256()
    for qb,qe in [(1,1),(2,2)]:
        for length in range(1,5):
            for sequence in itertools.product(alphabet,repeat=length):
                expected=literal(list(sequence),qb,qe);actual=compact(sequence,qb,qe);require(expected==actual,'compact audit mismatch')
                digest.update(canonical(actual).encode());count+=1
    special=[]
    messages=controls['recorded_gap_reset_resume']['messages']
    wrong=copy.deepcopy(messages[:3]);wrong[-1]['cursor_unit']='utf8-byte'
    cases={'wrong_unit_RESET_clears_with_permanent_reason':wrong,'extra_RESET_after_recovery':messages+[messages[2]],'WELCOME_reuses_last_HELLO':messages[:3]+[messages[1]],'refused_is_not_absorbing':controls['local_deferral_RESET']['messages']+[D.wire(('emit',2),seed,'event')]}
    for name,messages in cases.items():
        inp=copy.deepcopy(FIXTURE);inp['messages']=messages;SCHEMA.validate(inp);expected=literal(messages,1,1);actual=compact(messages,1,1);require(expected==actual,'special '+name);special.append({'name':name,'messages':messages,'decision':actual})
    return {'status':'calibration-pass','alphabet_size':len(alphabet),'exhaustive_nonempty_traces':count,'max_messages':4,'queue_bounds':[[1,1],[2,2]],'decision_digest':digest.hexdigest(),'prior_long_controls':long,'special_controls':special,'limit':'Fixed client/stream/epoch and declared alphabet; generated trace schema closure, not arbitrary M1B proof. Empty logical prefixes are not schema-valid wire inputs.'}
def replay(labels,unit):
    s,i=S.State(),I.State();wire=[D.wire((kind,),D.Visible(),unit) for kind in ('hello','welcome')];a=Audit();observations=[]
    for m in wire:a=advance(a,m,D.QUEUE_BYTES,D.QUEUE_EVENTS)
    for label in labels:
        label=tuple(label);left=[t for l,t in S.successors(s) if l==label];right=[t for l,t in I.successors(i) if l==label]
        require(len(left)==len(right)==1,'unreachable witness '+repr(label));v=S.visible(s);s,i=left[0],right[0]
        require(S.visible(s)==I.visible(i) and A.step(v,label)==S.visible(s),'witness model mismatch')
        message=D.wire(label,v,unit)
        if message is not None:wire.append(message);a=advance(a,message,D.QUEUE_BYTES,D.QUEUE_EVENTS)
        require(audit_binding(S.visible(s),a,unit),'witness audit binding')
        require(decision(a)==literal(wire,D.QUEUE_BYTES,D.QUEUE_EVENTS),'witness literal oracle')
        observations.append({'action':label,'application_position':S.visible(s).position,'audit_cursor':a.cursor,'current_recovery':a.recovery,'historical_requires_reset':decision(a)['requires_reset'],'live_candidates':S.visible(s).live})
    inp=copy.deepcopy(FIXTURE);inp.update(messages=wire,queue_limit_bytes=D.QUEUE_BYTES,queue_limit_events=D.QUEUE_EVENTS);SCHEMA.validate(inp)
    return {'labels':labels,'observations':observations,'wire':wire,'decision':decision(a),'final_visible':list(S.visible(s))}
def combined(unit):
    pipe=[('pump_source',),('pump_sdk',),('pump_broker',)]
    labels=[('offer',1),*pipe,('credit',1),('emit',1),('offer',2),*pipe,('ack',1),('credit',2),('emit',2),('ack',2),('offer',3),('offer',4),*pipe,('evict',3),('snapshot',3),*pipe,('hello',),('welcome',),('stop_request',),('stop_apply',),('reset',),('credit',2),('emit',4),('ack',4)]
    result=replay(labels,unit);require(result['decision']['status']=='accepted-reset' and result['decision']['requires_reset'] is True,'combined recovery witness')
    # E2 reaches the broker with insufficient credit before either ACK/CREDIT arrives.
    before=replay(labels[:10],unit);require(before['final_visible'][1]==(2,) or before['final_visible'][1]==[2],'retained E2 deferral')
    return result
def run():
    calibration=calibrations();print('AUDIT_CALIBRATIONS '+str(calibration['exhaustive_nonempty_traces']),flush=True)
    profiles=[]
    for unit in ['event','utf8-byte']:
        g=graph(unit)
        if g['status']!='graph-pass':return {'status':'counterexample','profile':g,'formal_freeze':False}
        fair=fairness(g);require(fair['fair_bad_components']==0 and fair['pending_Stop_cyclic_components']>0,'named Stop fairness')
        expected={'Stop_full_pipeline','Stop_blocked_pump','Stop_full_partial_frame','Stop_pending_RESET','WELCOME_audit_ahead_of_installation','RESET_preserves_future_candidates','loss_with_earlier_candidate_pending','recovered_delivery_complete','no_loss_delivery_complete','byte_credit_deferral','queue_byte_deferral'}
        require(set(g['witnesses'])==expected,'missing constructive witness')
        receipts={n:replay(trace,unit) for n,trace in g['witnesses'].items()};profiles.append({'unit':unit,'statistics':g['statistics'],'fairness':fair,'witnesses':receipts,'combined_witness':combined(unit)})
        print('INTEGRATED_PROFILE '+json.dumps(g['statistics']),flush=True);del g
    mutants=[]
    for name in ['shared_stop','false_settlement','stage_overflow','false_gap','reset_erases_future','reset_credit','gap_credit','ignore_byte_credit','ignore_queue_bytes']:
        value=graph('event',name);require(value['status']=='counterexample','vacuous mutation '+name);mutants.append(value)
    return {'schema_version':1,'status':'conditional-integration-pass','calibrations':calibration,'profiles':profiles,'mutants':mutants,'formal_freeze':False,'full_formal_comparison_complete':False,'live_provider_calls':0,'limits':['Four source identities and grants; mixed fixed payload costs and selected queue bounds; no cutoff theorem.','Retention eviction and snapshot availability are modeled source facts, not SDK loss detection or authenticated storage.','Emission/application is atomic for admitted events; actual emitted-exhaustion recovery remains in literal audit controls, not the normal-source product.','Independent Stop is logical only; framing faults quarantine new source admission without a physical recovery implementation.','Both concrete definitions checked by exact local correspondence over the reachable split/audit product; stronger than visible trace inclusion and not separate performance measurements.','Full six obligations,27-row corpus and original full profiles remain incomplete.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);args=p.parse_args();path=pathlib.Path(args.output);require(not path.exists(),'output exists');start=time.perf_counter()
    try:result=run()
    except Limit as exc:result={'status':'exploration-limit','detail':str(exc),'formal_freeze':False,'full_formal_comparison_complete':False}
    except Exception as exc:result={'status':'checker-error','detail':type(exc).__name__+': '+str(exc),'formal_freeze':False,'full_formal_comparison_complete':False}
    result['elapsed_seconds']=round(time.perf_counter()-start,6);path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'elapsed_seconds':result['elapsed_seconds']}));raise SystemExit(0 if result['status']=='conditional-integration-pass' else 2)
