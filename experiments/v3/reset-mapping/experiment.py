"""Finite admission/emission mapping controls; no product or transport execution."""
import argparse,copy,hashlib,itertools,json,pathlib,runpy
from typing import NamedTuple
from jsonschema import Draft202012Validator
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='c87f492780087772e3bcb06249ef14d89e812a25'
ORACLE=runpy.run_path(str(ROOT/'scripts/tests/v3/execution/reference_oracle.py'))['replay_broker']
VALIDATOR=Draft202012Validator(json.loads((ROOT/'schemas/control-plane/v3/execution/schema.json').read_text()))
FIXTURE=json.loads((ROOT/'scripts/tests/v3/execution/fixtures/F-M1B-020.json').read_text())['input']
def require(ok,message):
    if not ok:raise ValueError(message)
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'))
def msg(kind,**fields):return dict(type=kind,protocol_version='m1b-broker/1',stream_id='stream-a',daemon_epoch=2,**fields)
def credit(size=1):return msg('CREDIT',client_id='client-a',bytes=size,events=1)
def event(cursor,size=1,unit='event'):
    return msg('EVENT',cursor=cursor,cursor_unit=unit,event_class='output',process_id='process-a',payload_base64='eA==' if size==1 else 'eHg=',payload_untrusted=True)
def ack(cursor,unit='event'):return msg('ACK',client_id='client-a',cursor=cursor,cursor_unit=unit)
def reset(cursor,unit='event'):return msg('RESET',client_id='client-a',reason='gap',snapshot_cursor=cursor,cursor_unit=unit)
def hello(cursor):
    v=copy.deepcopy(FIXTURE['messages'][0]);v['last_cursor']=cursor;return v
def welcome(floor,cursor):
    v=copy.deepcopy(FIXTURE['messages'][1]);v.update(replay_floor=floor,snapshot_cursor=cursor);return v
def evaluate(messages,queue_events=1,queue_bytes=1):
    value=copy.deepcopy(FIXTURE);value.update(messages=messages,queue_limit_events=queue_events,queue_limit_bytes=queue_bytes)
    VALIDATOR.validate(value);return ORACLE(value)

class Producer(NamedTuple):
    offered:int=0
    retained:tuple=()
class Flow(NamedTuple):
    grants:int=0
    byte_credit:int=0
    event_credit:int=0
    sent:int=0
    acknowledged:int=0
    pending:tuple=()
class Split(NamedTuple):
    producer:Producer=Producer()
    flow:Flow=Flow()
class Inclusive(NamedTuple):
    offered:int=0
    retained:tuple=()
    grants:int=0
    byte_credit:int=0
    event_credit:int=0
    sent:int=0
    acknowledged:int=0
    pending:tuple=()
def flat(s):return tuple(s.producer)+tuple(s.flow) if isinstance(s,Split) else tuple(s)
def split_next(state,size,unit,qevents,qbytes):
    p,f=state;delta=size if unit=='utf8-byte' else 1
    if p.offered<2:
        n=p.offered+1;yield ('offer',n),Split(p._replace(offered=n,retained=p.retained+(n,)),f),None
    if f.grants<2:yield ('credit',),Split(p,f._replace(grants=f.grants+1,byte_credit=f.byte_credit+size,event_credit=f.event_credit+1)),credit(size)
    if p.retained and f.byte_credit>=size and f.event_credit>=1 and len(f.pending)<qevents and len(f.pending)*size+size<=qbytes:
        n=p.retained[0];yield ('emit',n),Split(p._replace(retained=p.retained[1:]),f._replace(byte_credit=f.byte_credit-size,event_credit=f.event_credit-1,sent=n,pending=f.pending+(n,))),event(n*delta,size,unit)
    if f.acknowledged<f.sent:yield ('ack',f.sent),Split(p,f._replace(acknowledged=f.sent,pending=())),ack(f.sent*delta,unit)
def inclusive_next(s,size,unit,qevents,qbytes):
    step=size if unit=='utf8-byte' else 1
    if s.offered!=2:
        number=s.offered+1
        yield ('offer',number),s._replace(offered=number,retained=(*s.retained,number)),None
    if s.grants!=2:
        yield ('credit',),s._replace(grants=s.grants+1,byte_credit=s.byte_credit+size,event_credit=s.event_credit+1),credit(size)
    room=(qevents-len(s.pending)>0 and qbytes-sum(size for _ in s.pending)>=size)
    funded=(s.event_credit>0 and s.byte_credit-size>=0)
    if s.retained and room and funded:
        current,*tail=s.retained
        yield ('emit',current),s._replace(retained=tuple(tail),byte_credit=s.byte_credit-size,event_credit=s.event_credit-1,sent=current,pending=tuple([*s.pending,current])),event(current*step,size,unit)
    if s.sent>s.acknowledged:
        yield ('ack',s.sent),s._replace(acknowledged=s.sent,pending=tuple(n for n in s.pending if n>s.sent)),ack(s.sent*step,unit)

def explore(size,unit,qevents,qbytes):
    # Enumerate every finite schedule, not merely one wire history per merged state.
    initial=[hello(0),welcome(0,0)]
    for message in initial:message['cursor_unit']=unit
    todo=[(Split(),Inclusive(),initial,[])];states=set();edges=set();prefixes=0;terminals=0;witnesses={}
    while todo:
        a,b,wire,trace=todo.pop();require(flat(a)==flat(b),'independent mapping state mismatch');states.add(flat(a));prefixes+=1
        decision=evaluate(wire,qevents,qbytes);require(decision['status']=='accepted' and decision['reasons']==[],'preventive schedule emitted invalid wire')
        require(decision['final_cursor']==a.flow.sent*(size if unit=='utf8-byte' else 1),'admitted/emitted/audit cursor mismatch')
        require(tuple(range(a.flow.sent+1,a.producer.offered+1))==a.producer.retained,'candidate evidence erased or reordered')
        aa=list(split_next(a,size,unit,qevents,qbytes));bb=list(inclusive_next(b,size,unit,qevents,qbytes))
        require([(l,flat(t),m) for l,t,m in aa]==[(l,flat(t),m) for l,t,m in bb],'independent transitions mismatch')
        if a.producer.retained and not any(l[0]=='emit' for l,_,_ in aa):
            witnesses.setdefault('deferred',{'schedule':trace,'retained_candidates':a.producer.retained,'wire':wire,'decision':decision})
        if not aa:
            require(a.flow.sent==a.flow.acknowledged==a.producer.offered==2 and not a.producer.retained,'terminal deadlock')
            terminals+=1;witnesses.setdefault('complete',{'schedule':trace,'wire':wire,'decision':decision})
        for (label,target,message),(_,other,_) in zip(aa,bb):
            edges.add(canon([flat(a),label,flat(target),message]));todo.append((target,other,wire+([message] if message else []),trace+[label]))
    require(terminals>0 and 'deferred' in witnesses,'vacuous environment')
    return {'configuration':{'payload_bytes':size,'cursor_unit':unit,'queue_events':qevents,'queue_bytes':qbytes,'candidate_offers':2,'credit_offers':2},'unique_states':len(states),'unique_transitions':len(edges),'schedule_prefixes':prefixes,'complete_schedules':terminals,'frontier':0,'max_actions':8,'graph_sha256':hashlib.sha256('\n'.join(sorted(edges)).encode()).hexdigest(),'witnesses':witnesses}

def gap_sequence(facts):
    # These are modeled store facts, not extra M1B fields or authenticated runtime evidence.
    required={'client_cursor','retention_floor','snapshot_cursor','snapshot_available','retention_loss_recorded'}
    require(set(facts)==required,'exact store fact fields')
    require(all(type(facts[k])is int and 0<=facts[k]<=2 for k in ['client_cursor','retention_floor','snapshot_cursor']),'typed store cursors')
    require(facts['snapshot_available'] is True and facts['retention_loss_recorded'] is True,'missing actual modeled loss/snapshot facts')
    c,f,s=[facts[k] for k in ['client_cursor','retention_floor','snapshot_cursor']]
    require(c<f<=s,'no supported replay gap')
    return [hello(c),welcome(f,s),reset(s),credit(),event(s+1)]

def controls():
    prefix=[hello(0),welcome(0,0),credit(),event(1)]
    rows={}
    cases={
      'defer_ACK_CREDIT_resume':(prefix+[ack(1),credit(),event(2)],'accepted',None),
      'defer_CREDIT_ACK_resume':(prefix+[credit(),ack(1),event(2)],'accepted',None),
      'local_deferral_RESET':(prefix+[ack(1),credit(),reset(1)],'refused','unexpected-reset'),
      'ACK_without_CREDIT':(prefix+[ack(1),event(2)],'refused','credit-exhausted'),
      'CREDIT_without_ACK':(prefix+[credit(),event(2)],'refused','credit-exhausted'),
      'actual_exhaustion_RESET':(prefix+[event(2),reset(2),credit(),event(3)],'accepted-reset','credit-exhausted'),
      'actual_exhaustion_backward_RESET':(prefix+[event(2),reset(1)],'refused','cursor-nonmonotonic'),
      'actual_exhaustion_no_RESET':(prefix+[event(2),ack(2),credit(),event(3)],'refused','credit-exhausted'),
    }
    facts={'client_cursor':1,'retention_floor':2,'snapshot_cursor':2,'snapshot_available':True,'retention_loss_recorded':True}
    gap=gap_sequence(facts);cases['recorded_gap_reset_resume']=(gap,'accepted-reset','replay-gap')
    cases['gap_RESET_without_fresh_CREDIT']=(gap[:3]+[event(3)],'refused','credit-missing')
    cases['gap_continuation_before_RESET']=(gap[:2]+[credit()]+gap[2:],'refused','replay-gap-continuation')
    cases['gap_backward_RESET']=(gap[:2]+[reset(1)],'refused','cursor-nonmonotonic')
    for name,(messages,status,reason) in cases.items():
        decision=evaluate(messages);require(decision['status']==status and (reason is None or reason in decision['reasons']),'control '+name)
        rows[name]={'messages':messages,'decision':decision}
    negatives=[]
    for field,value in [('retention_loss_recorded',False),('snapshot_available',False),('retention_floor',1),('snapshot_cursor',1),('client_cursor',True)]:
        bad=copy.deepcopy(facts);bad[field]=value
        try:gap_sequence(bad)
        except ValueError:negatives.append(field)
        else:raise ValueError('accepted unsupported store facts '+field)
    # Identical wire bytes do not prove the truth of their asserted replay floor.
    forged=evaluate(gap);require(forged['status']=='accepted-reset','wire oracle cannot authenticate omitted store provenance')
    require(rows['recorded_gap_reset_resume']['decision']['requires_reset'] is True,'historical requires_reset meaning')
    return {'literal_cases':rows,'modeled_store_facts':facts,'fact_guard_negatives':negatives,'wire_only_forged_fact_control':{'decision':forged,'finding':'Wire oracle accepts the same bytes without inspecting store facts; store provenance is a separate unimplemented runtime obligation.'},'requires_reset_semantics':'Historical recovery_needed_seen; accepted-reset can still have requires_reset=true. It is not a current-state RESET command.'}

def run():
    profiles=[explore(size,unit,qe,qb*size) for size,unit,qe,qb in itertools.product([1,2],['event','utf8-byte'],[1,2],[1,2])]
    return {'schema_version':1,'kind':'finite-admission-mapping-controls','status':'conditional-mapping-controls-pass','base':BASE,'profiles':profiles,'controls':controls(),'full_formal_comparison_complete':False,'formal_freeze':False,'live_provider_calls':0,'limitations':['Two candidate offers and two CREDIT offers; no cutoff theorem, fairness or full aggregate/broker refinement.','Independent split/inclusive mapper code shares message encoding and immutable oracle, authored by one integrator.','Retained candidate queue is bounded to two offers; upstream overflow/loss detection and durable store/transport implementation are absent.','Store facts are modeled inputs; provenance is not authenticated by M1B wire validation.','Prior c87 full models and their RESET seam counterexample remain unchanged historical evidence.']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output');args=parser.parse_args();result=run();raw=json.dumps(result,indent=2)+'\n'
    if args.output:
        path=pathlib.Path(args.output);require(not path.exists(),'output already exists');path.write_text(raw)
    print(json.dumps({'status':result['status'],'profiles':len(result['profiles']),'prefixes':sum(p['schedule_prefixes'] for p in result['profiles']),'complete_schedules':sum(p['complete_schedules'] for p in result['profiles'])}))
