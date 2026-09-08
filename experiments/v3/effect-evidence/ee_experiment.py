"""Literal provider-free join tests with retained inputs and independent expectations."""
import argparse,copy,ctypes,datetime,json,os,pathlib,time,tracemalloc
from ee_common import *
from ee_join import join,sign
from ee_cases import EXPECTED,unsigned,package,refresh,reseal_context

def audit(original,result,name):
    # Independent projection from original source records, not adapter output fields.
    exact=copy.deepcopy(original['cut']['trace_header']);exact['observations']=original['records']
    for key in ('current_admission_epoch','current_fence_epoch'):exact[key]=original['cut']['assessment'][key]
    require(result['trace']==exact,'independent exact trace')
    old,new,reasons=EXPECTED[name]
    require(result['historical']['status']==old and result['current']['status']==new,'hand-stated outcomes '+name)
    require(reasons==result['current']['reasons'],'hand-stated reasons '+name)
    old_reasons=(['observation-unverified','receipt-missing','reconciliation-required'] if name=='unverified' else ['receipt-missing','reconciliation-required']) if old=='ambiguous' else []
    require(result['historical']['reasons']==old_reasons,'exact historical reasons '+name)
    require(result['runtime_permission'] is False and result['canonical_write_count']==0,'classification is not permission')
    require(all(result['current'][k]==0 for k in ('effect_count','external_call_count')),'literal zero counters')
    expected_pending={'ambiguous':['attempt:1'],'unverified':['attempt:1'],'prior-unresolved':['attempt:1'],'later-unresolved':['attempt:2'],'later-start-only':['attempt:2']}.get(name,[])
    require(result['unsettled_attempt_ids']==expected_pending,'independent unresolved attempts '+name)
    require(result['runtime_settlement_hold']==(bool(expected_pending) or new=='ambiguous'),'independent runtime hold '+name)

def authorized(fixture,command,state,ordinal):
    """Synthetic candidate-bound fixture attestation, then actual kernel admission."""
    command=copy.deepcopy(command);command['logical_time']=ordinal
    command['payload']['created_logical_time']=ordinal
    command['payload']=m1a.seal(command['payload'])
    command['candidate_digest']=command['payload_digest']=m1a.digest(command['payload'])
    command=rebind(command,state)
    authorities=copy.deepcopy(fixture['authority_fixtures'])
    for i,auth in enumerate(authorities):
        if auth['attestation_id']==command['auth_ref']:
            auth['candidate_digest']=command['candidate_digest'];authorities[i]=m1a.seal(auth)
    return command,authorities

def literal_controls():
    fixture,state,journal=running();policies=fixture['policy_fixtures'];authorities=fixture['authority_fixtures']
    command=rebind(fixture['commands'][-1],state)
    accepted,ae,ar,aj=kernel.admit(state,state['content_digest'],command,authorities,policies,journal)
    paused,pe,pr,pj=kernel.admit(state,state['content_digest'],fixture['commands'][0],authorities,policies,journal)
    fresh=rebind(fixture['commands'][-1],paused)
    refused,re,rr,rj=kernel.admit(paused,paused['content_digest'],fresh,authorities,policies,pj)
    require(ar['disposition']=='accepted' and len(ae)==1 and ae[0]['event_type']=='EffectObservationRecorded','running positive')
    require(pr['disposition']=='accepted' and rr['disposition']=='refused' and rr['primary_error']=='E-PAUSED' and not re and refused==paused and len(rj)==len(pj)+1,'literal pause refusal')
    require(command['payload']==fresh['payload'] and command['candidate_digest']==fresh['candidate_digest'] and command['auth_ref']==fresh['auth_ref'],'otherwise identical pair')
    guard=contracts.PAUSE_SENSITIVE
    try:
        contracts.PAUSE_SENSITIVE=guard-{'record-effect-observation'}
        ms,me,mr,mj=kernel.admit(paused,paused['content_digest'],fresh,authorities,policies,pj)
    finally:contracts.PAUSE_SENSITIVE=guard
    require(mr['disposition']=='accepted' and len(me)==1 and ms!=paused,'actual pause guard mutant')
    pc,pa=authorized(fixture,fixture['commands'][0],accepted,10)
    ds,de,dr,dj=kernel.admit(accepted,accepted['content_digest'],pc,pa,policies,aj)
    require(dr['disposition']=='accepted','pause after accepted command')
    duplicate,dupevents,dupreceipt,dupjournal=kernel.admit(ds,ds['content_digest'],command,authorities,policies,dj)
    require(duplicate==ds and not dupevents and dupreceipt==ar,'duplicate before current pause guard')
    # No mutable legacy file is edited; these are new synthetic records.
    ac=copy.deepcopy(fixture['commands'][-1]);ac['payload']=unsigned('late-receipt')['cut']['context']['observation']
    ac,aa=authorized(fixture,ac,state,20)
    qs,qe,qr,qj=kernel.admit(state,state['content_digest'],ac,aa,policies,journal)
    require(qr['disposition']=='accepted' and qs['ambiguous_effect_refs'],'literal ambiguity admission')
    sc=copy.deepcopy(ac);sc['command_id']='CMD-EFFECT-LATE-SUCCESS';sc['payload']['id']='EFFECT-LATE-SUCCESS';sc['payload']['causation_id']=sc['command_id']
    sc['payload']['payload']=unsigned('success')['cut']['context']['observation']['payload']
    sc,sa=authorized(fixture,sc,qs,21)
    ss,se,sr,sj=kernel.admit(qs,qs['content_digest'],sc,sa,policies,qj)
    require(sr['disposition']=='accepted' and ss['ambiguous_effect_refs']==qs['ambiguous_effect_refs'] and all(item in ss['object_states'] for item in qs['object_states']),'success retains canonical quarantine')
    return {'running':{'receipt':ar,'events':ae},'paused':{'receipt':rr,'events':re,'projection_unchanged':refused==paused,'journal_growth':len(rj)-len(pj)},
        'guard_mutant':{'receipt':mr,'events':me},'duplicate_after_pause':{'receipt':dupreceipt,'events':dupevents,'projection_unchanged':duplicate==ds},
        'quarantine':{'ambiguous_receipt':qr,'success_receipt':sr,'ambiguous_refs':ss['ambiguous_effect_refs'],'prior_object_states_preserved':all(item in ss['object_states'] for item in qs['object_states'])}}

def run(keys,directory,limits):
    outcomes={};raw={};negative=[];mutants=[]
    for name in EXPECTED:
        original=unsigned(name);bundle=package(original,keys);before=canonical(bundle)
        raw[name]={'original':original,'bundle':bundle};write(directory/'cases.json',raw)
        result=join(bundle,keys);audit(original,result,name);require(canonical(bundle)==before,'immutable input')
        raw[name]={'original':original,'bundle':bundle,'result':result};outcomes[name]={k:v for k,v in result.items() if k not in ('trace','ordered_inventory')}
    def rejection(name,bundle,stage,expected_detail=None):
        raw[name]={'bundle':bundle,'expected_failure_stage':stage};write(directory/'cases.json',raw)
        try:join(bundle,keys)
        except schema.jsonschema.ValidationError as e:
            actual='schema';detail=e.message
        except (ValueError,KeyError,TypeError,m1a.M1AError) as e:
            actual='join';detail=str(e)
        else:raise ValueError('negative accepted '+name)
        require(actual==stage,'negative stage '+name+': '+actual)
        if expected_detail is not None:require(detail==expected_detail,'discriminating binding '+name+': '+detail)
        negative.append({'name':name,'stage':actual,'detail':detail});raw[name]['observed_failure']=negative[-1]
    base=unsigned('success')
    for field in ('idempotency_key','target_ref','payload_digest'):
        bad=copy.deepcopy(base);bad['cut']['trace_header']['intent'].pop(field)
        rejection('missing-'+field,package(bad,keys),'join' if field=='idempotency_key' else 'schema')
    for field,value in [('idempotency_key','idempotency:wrong'),('target_ref','target:wrong'),('payload_digest','sha256:'+'9'*64)]:
        bad=copy.deepcopy(base);bad['records'][1][field]=value;refresh(bad)
        rejection('record-'+field,package(bad,keys),'schema')
    for name in ('wrong-role','bad-mac','wrong-domain','missing-mac','omitted-record','reordered','missing-start','duplicate-start','bad-time','wrong-original-key','wrong-receipt-digest','effect-key-is-operation','bad-prefix-label','packet-ref','goal-ref','plan-ref','epoch-domain'):
        bad=copy.deepcopy(base)
        if name=='missing-start':bad['records'].pop(0);bad['cut']['prefix_length']=2;bad['cut']['receipt_index']=bad['cut']['operation_index']=1;refresh(bad)
        elif name=='duplicate-start':bad['records'][1]=copy.deepcopy(bad['records'][0]);refresh(bad)
        elif name=='bad-time':bad['records'][2]['observed_at']='2026-09-04T11:00:00Z';refresh(bad)
        elif name=='wrong-original-key':
            bad['cut']['trace_header']['intent']['idempotency_key']='idempotency:other'
        elif name in ('wrong-receipt-digest','effect-key-is-operation','bad-prefix-label','packet-ref'):
            o=bad['cut']['context']['observation']
            if name=='wrong-receipt-digest':o['payload']['receipt_digest']='0'*64
            elif name=='effect-key-is-operation':o['payload']['provider_operation_id_digest']=rawhash(o['payload']['effect_key'].encode())
            elif name=='packet-ref':o['payload']['work_packet_ref']['content_digest']='0'*64
            else:o['payload'].update(observation='observed-failure',quarantine=False)
            bad['cut']['context']['observation']=m1a.seal(o)
        elif name in ('goal-ref','plan-ref'):
            p=bad['cut']['context']['packet'];p['payload'][name.replace('-','_')]['content_digest']='0'*64
            # M1A packet digest is derived, and its schema may reject; distinguish it as a join failure.
            bad['cut']['context']['packet']=m1a.seal(p)
        elif name=='epoch-domain':bad['cut']['context']['mapping']['admission']['source_domain']='m1a-work-lease'
        bundle=package(bad,keys)
        if name=='wrong-role':bundle['dispatch']=sign(bundle['dispatch']['body'],'observer',keys)
        elif name=='bad-mac':bundle['evidence'][1]['mac']='0'*64
        elif name=='wrong-domain':bundle['cut']['domain']='other'
        elif name=='missing-mac':bundle['cut'].pop('mac')
        elif name=='omitted-record':bundle['evidence'].pop()
        elif name=='reordered':bundle['evidence'].reverse()
        rejection(name,bundle,'schema' if name in ('missing-start','duplicate-start','bad-time') else 'join')
    for kind,field,expected in [('lease','task_ref','lease-task'),('budget','task_ref','budget-task_ref'),('budget','goal_ref','budget-goal_ref'),('budget','plan_ref','budget-plan_ref'),('plan','goal_ref','plan-goal')]:
        bad=copy.deepcopy(base);bad['cut']['context'][kind]['payload'][field]['content_digest']='0'*64
        reseal_context(bad,kind);rejection('cross-'+kind+'-'+field,package(bad,keys),'join',expected)
    bad=copy.deepcopy(base);bad['cut']['context']['route']['payload']['logical_actor_id']='WORKER-OTHER';reseal_context(bad,'route')
    rejection('cross-route-actor',package(bad,keys),'join','route-actor')
    for name in ('bool-epoch','bool-ordinal','bool-grant'):
        bad=copy.deepcopy(base)
        if name=='bool-epoch':bad['cut']['context']['mapping']['fence']['target']=True
        elif name=='bool-grant':bad['cut']['context']['grant']['operational_authority']=0
        bundle=package(bad,keys)
        if name=='bool-ordinal':
            body=bundle['evidence'][0]['body'];body['ordinal']=False;bundle['evidence'][0]=sign(body,'dispatcher',keys)
        rejection(name,bundle,'join')
    # Guard mutants each accept a counterexample rejected by the baseline.
    wrong=package(base,keys);wrong['dispatch']=sign(wrong['dispatch']['body'],'observer',keys)
    role=join(wrong,keys,'role');mutants.append({'guard':'role','counterexample':'wrong-role','accepted_status':role['current']['status']})
    bad=copy.deepcopy(base);o=bad['cut']['context']['observation'];o['payload']['work_packet_ref']['content_digest']='0'*64;bad['cut']['context']['observation']=m1a.seal(o)
    ctx=join(package(bad,keys),keys,'context');mutants.append({'guard':'context','counterexample':'packet-ref','accepted_status':ctx['current']['status']})
    # Remove only a later unknown observation; its start remains in dispatcher history.
    original=unsigned('later-unresolved');bundle=package(original,keys);bundle['evidence'].pop()
    rejection('inventory-omission-control',bundle,'join')
    inv=join(bundle,keys,'inventory');mutants.append({'guard':'inventory','counterexample':'inventory-omission-control','accepted_status':inv['current']['status'],'inventory_length':len(inv['ordered_inventory']),'actual_length':len(inv['trace']['observations'])})
    literal=literal_controls();write(directory/'cases.json',raw);write(directory/'literal-controls.json',literal)
    count=len(outcomes)+len(negative)+len(mutants)+5;require(count<=limits['max_cases'],'case limit')
    return {'status':'literal-effect-evidence-pass','classification':'locally observed','case_count':count,'positive':outcomes,'negative':negative,'mutants':mutants,
        'literal_controls':literal,'formal_freeze':False,'production_authentication':False,'live_provider_calls':0,'new_owner_questions':[]}

def peak_bytes():
    if os.name=='nt':
        class Counters(ctypes.Structure):
            _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ('peak','rss','pp','p','pn','n','pf','ppf')]
        c=Counters();c.cb=ctypes.sizeof(c)
        k=ctypes.WinDLL('kernel32');k.GetCurrentProcess.restype=ctypes.c_void_p
        dll=ctypes.WinDLL('psapi');dll.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
        if not dll.GetProcessMemoryInfo(k.GetCurrentProcess(),ctypes.byref(c),c.cb):raise OSError('memory counter')
        return c.peak
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=pathlib.Path,required=True);parser.add_argument('--keys',type=pathlib.Path,required=True);a=parser.parse_args()
    plan=load(ROOT/'docs/v3/construction/effect-evidence-20260908/plan.json');keys={k:bytes.fromhex(v) for k,v in load(a.keys).items()}
    started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.perf_counter();tracemalloc.start();code=0
    try:result=run(keys,a.output.parent,plan['limits'])
    except Exception as e:result={'status':'experiment-error','detail':type(e).__name__+': '+str(e),'formal_freeze':False};code=1
    peak=peak_bytes();allocated=tracemalloc.get_traced_memory()[1];seconds=time.perf_counter()-t
    if peak>plan['limits']['memory_bytes'] or seconds>plan['limits']['seconds_per_experiment']:result={'status':'limit','formal_freeze':False};code=2
    write(a.output,{'started_at':started,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':seconds,'peak_bytes':peak,'peak_python_allocated_bytes':allocated,'result':result})
    print(json.dumps({'status':result['status'],'seconds':seconds,'detail':result.get('detail')}),flush=True);return code
if __name__=='__main__':raise SystemExit(main())
