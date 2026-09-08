"""Independent small proof-method controls and immutable M1B guard evidence."""
import copy,collections,json,pathlib,runpy
import aggregate,split,inclusive
from explore import fair_bad_cycles,physical_type,graph
ROOT=pathlib.Path(__file__).resolve().parents[3]

def require(value,message):
    if not value:raise ValueError(message)

def epsilon_closure(g,states):
    found=set(states);todo=list(states)
    for state in todo:
        for label,target in g[state]:
            if label=='tau' and target not in found:found.add(target);todo.append(target)
    return frozenset(found)

def trace_inclusion(concrete,c_initial,abstract,a_initial):
    queue=collections.deque((c,epsilon_closure(abstract,a_initial),()) for c in c_initial);seen=set();count=0
    while queue:
        c,possibilities,trace=queue.popleft();key=(c,possibilities)
        if key in seen:continue
        seen.add(key)
        for label,target in concrete[c]:
            count+=1
            if label=='tau':next_set=possibilities;next_trace=trace
            else:
                next_set=epsilon_closure(abstract,{a2 for a in possibilities for action,a2 in abstract[a] if action==label})
                next_trace=trace+(label,)
            if not next_set:return {'included':False,'trace':next_trace,'pairs':len(seen),'transitions':count}
            queue.append((target,next_set,next_trace))
    return {'included':True,'pairs':len(seen),'transitions':count,'frontier':0}

def hidden_choice():
    a={'a0':[('reveal0','end0')],'a1':[('reveal1','end1')],'end0':[('tau','end0')],'end1':[('tau','end1')]}
    c={'u':[('reveal0','c0'),('reveal1','c1')],'c0':[('tau','c0')],'c1':[('tau','c1')]}
    forward=trace_inclusion(c,['u'],a,['a0','a1']);reverse=trace_inclusion(a,['a0','a1'],c,['u'])
    require(forward['included'] and reverse['included'],'hidden-choice visible behavior')
    naive={initial:all(any(alabel==label for alabel,_ in a[initial]) for label,_ in c['u']) for initial in ['a0','a1']}
    require(not any(naive.values()),'naive initial-state map must fail')
    bad=copy.deepcopy(c);bad['u'].append(('reveal2','c0'));negative=trace_inclusion(bad,['u'],a,['a0','a1'])
    require(not negative['included'] and negative['trace']==('reveal2',),'visible counterexample sensitivity')
    auxiliary={'p0':[('reveal0','p_end0')],'p1':[('reveal1','p_end1')],'p_end0':[('tau','p_end0')],'p_end1':[('tau','p_end1')]}
    hidden_forward=trace_inclusion(auxiliary,['p0','p1'],c,['u']);hidden_reverse=trace_inclusion(c,['u'],auxiliary,['p0','p1'])
    require(hidden_forward['included'] and hidden_reverse['included'],'auxiliary hiding changed finite-prefix behavior')
    return {'status':'calibration-pass','naive_state_map':naive,'finite_prefix_inclusion':forward,'reverse_inclusion':reverse,
            'visible_negative':negative,'auxiliary_hiding_forward':hidden_forward,'auxiliary_hiding_reverse':hidden_reverse,
            'limit':'Finite labeled-prefix languages only; no unbounded liveness, general prophecy theorem or product proof.'}

def fair_calibrations():
    g={'edges':[[ (('requeue',),0),(('stop_apply',),1) ],[(('idle',),1)]],
       'enabled':[{'requeue','stop_apply'},{'idle'}]}
    exit_only=fair_bad_cycles(g,[0],['stop_apply']);unfair=fair_bad_cycles(g,[0],[])
    require(exit_only['fair_bad_components']==0 and unfair['fair_bad_components']==1,'named Stop fairness')
    coarse={'edges':[[ (('broker','requeue'),0),(('broker','stop'),1) ],[(('idle',),1)]],
            'enabled':[{'broker'},{'idle'}]}
    coarse_result=fair_bad_cycles(coarse,[0],['broker']);require(coarse_result['fair_bad_components']==1,'coarse broker fairness must permit starvation')
    intermittent={'edges':[[ (('toggle',),1),(('stop_apply',),2) ],[(('toggle',),0)],[(('idle',),2)]],
                  'enabled':[{'toggle','stop_apply'},{'toggle'},{'idle'}]}
    intermittent_result=fair_bad_cycles(intermittent,[0,1],['stop_apply']);require(intermittent_result['fair_bad_components']==1,'weak fairness cannot imply strong fairness')
    internal={'edges':[[(('stop_apply',),0)]],'enabled':[{'stop_apply'}]}
    internal_result=fair_bad_cycles(internal,[0],['stop_apply']);require(internal_result['fair_bad_components']==1,'internal fair action cycle')
    acyclic={'edges':[[(('move',),1)],[]],'enabled':[{'move'},set()]}
    acyclic_result=fair_bad_cycles(acyclic,[0,1],[]);require(acyclic_result['cyclic_components']==0,'acyclic path cannot be an infinite witness')
    return {'status':'calibration-pass','exit_only_Stop':exit_only,'without_fairness':unfair,'coarse_broker_fairness':coarse_result,
            'intermittent_Stop':intermittent_result,'internal_action':internal_result,'acyclic':acyclic_result,
            'explicit_cycles':{'unfair_or_coarse':[0,0],'intermittent':[0,1,0],'internal':[0,0]},
            'limit':'Weak fairness of named action classes on a finite graph; one monotone pending-Stop monitor, not arbitrary LTL or strong fairness.'}

def type_calibrations():
    bad=split.Split(kernel=split.Kernel(waiting=True,fenced=True))
    require(not physical_type(bad),'raw Kernel flag alias')
    require(not physical_type(split.Split(broker=split.Broker(pending=(True,)))),'boolean pending cursor alias')
    require(not physical_type(inclusive.Inclusive(outstanding=(True,))),'inclusive boolean cursor alias')
    def corrupted(state,mutant):yield ('stop_request',),bad
    receipt=graph(split.Split(),corrupted)
    require(receipt['violation']=='complete target TypeOK before relation mapping','invalid target must not alias an existing relation state')
    return {'status':'calibration-pass','invalid_flags_rejected':True,'boolean_cursor_rejected_in_both_boundaries':True,'raw_target_counterexample':receipt}

def wire_controls():
    from jsonschema import Draft202012Validator
    module=runpy.run_path(str(ROOT/'scripts/tests/v3/execution/reference_oracle.py'));oracle=module['replay_broker']
    schema=json.loads((ROOT/'schemas/control-plane/v3/execution/schema.json').read_text())
    validator=Draft202012Validator(schema)
    fixture=json.loads((ROOT/'scripts/tests/v3/execution/fixtures/F-M1B-020.json').read_text())['input']
    def message(kind,**fields):return dict(type=kind,protocol_version='m1b-broker/1',stream_id='stream-a',daemon_epoch=2,**fields)
    def credit():return message('CREDIT',client_id='client-a',bytes=1,events=1)
    def event(cursor):return message('EVENT',cursor=cursor,cursor_unit='event',event_class='output',process_id='process-a',payload_base64='eA==',payload_untrusted=True)
    def ack(cursor):return message('ACK',client_id='client-a',cursor=cursor,cursor_unit='event')
    def reset(cursor):return message('RESET',client_id='client-a',reason='gap',snapshot_cursor=cursor,cursor_unit='event')
    def evaluate(messages):
        value=copy.deepcopy(fixture);value['messages']=messages;validator.validate(value);return oracle(value)
    rows={}
    cases={'legitimate':[credit(),event(1)],'cursor_skip':[credit(),event(2)],'ack_rollback':[credit(),event(1),ack(1),ack(0)],
           'credit_missing_permanent':[event(1),reset(1)],'flow_exhaustion_credit_RESET':[credit(),event(1),event(2),credit(),reset(2)]}
    for name,messages in cases.items():rows[name]={'messages':messages,'decision':evaluate(messages)}
    require(rows['legitimate']['decision']['status']=='accepted','literal positive prefix')
    for name,reason in [('cursor_skip','cursor-nonmonotonic'),('ack_rollback','cursor-nonmonotonic'),('credit_missing_permanent','credit-missing')]:
        require(rows[name]['decision']['status']=='refused' and reason in rows[name]['decision']['reasons'],'literal negative '+name)
    require(rows['flow_exhaustion_credit_RESET']['decision']['status']=='accepted-reset' and 'replay-gap-continuation' not in rows['flow_exhaustion_credit_RESET']['decision']['reasons'],'flow exhaustion differs from replay gap')
    gap=copy.deepcopy(fixture['messages']);gap[1].update(replay_floor=1,snapshot_cursor=1)
    messages=[credit(),event(2),ack(1),copy.deepcopy(gap[0]),copy.deepcopy(gap[1]),
              message('SNAPSHOT',cursor=1,cursor_unit='event',snapshot_digest='sha256:'+'1'*64),
              message('INPUT',client_id='client-a',command_id='command-a',process_epoch=2,input_lease='lease:input:2',bytes_base64='eA=='),
              message('RESIZE',client_id='client-a',command_id='command-b',process_epoch=2,resize_lease='lease:resize:2',columns=80,rows=24)]
    for item in messages:
        decision=evaluate(gap+[item,reset(1)]);require(decision['status']=='refused' and 'replay-gap-continuation' in decision['reasons'],'all same-stream continuations fenced')
        rows['gap_then_'+item['type']]={'messages':gap+[item,reset(1)],'decision':decision}
    rows['gap_RESET_positive']={'messages':gap+[reset(1)],'decision':evaluate(gap+[reset(1)])}
    require(rows['gap_RESET_positive']['decision']['status']=='accepted-reset','literal reset positive')
    # Intentional negative mapping control: deleting a locally prevented EVENT cannot
    # invent a wire-level recovery reason for RESET.
    model=aggregate.Abstract();model_labels=[]
    for token in ['CREDIT','E1','E2','CREDIT','RESET']:
        result,model=aggregate.wire(model,token);model_labels.append(('message',token,result))
    actual=evaluate([credit(),event(1),credit(),reset(1)])
    require(model.phase==0 and actual['status']=='refused' and 'unexpected-reset' in actual['reasons'],'unimplemented prevention-to-audit RESET seam must remain exposed')
    return {'status':'paired-guard-controls-pass-not-full-wire-refinement','literal_cases':rows,
            'unimplemented_RESET_mapping_counterexample':{'model_candidate_trace':model_labels,'model_admitted_cursor':model.cursor,'wire_after_omitting_prevented_EVENT':actual},
            'limit':'Literal oracle is unchanged; these finite guard/prefix controls do not map all preventive model traces to immutable M1B audit state.'}

def run():return {'hidden_choice':hidden_choice(),'weak_fairness':fair_calibrations(),'concrete_types':type_calibrations(),'immutable_wire_controls':wire_controls()}

if __name__=='__main__':print(json.dumps(run(),indent=2))
