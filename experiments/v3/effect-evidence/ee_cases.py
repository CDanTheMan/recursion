"""Synthetic original evidence and hand-stated semantic expectations."""
import copy
from ee_common import ROOT,load,running,ref,m1a,rawhash,canonical,dh,pref
from ee_join import sign,grant_for,mapping_for

EXPECTED={
    'success':('succeeded','succeeded',[]),
    'failure':('failed','failed',[]),
    'ambiguous':('ambiguous','ambiguous',['receipt-missing','reconciliation-required']),
    'late-receipt':('ambiguous','succeeded',[]),
    'late-reconciliation':('ambiguous','reconciled-succeeded',[]),
    'unverified':('ambiguous','ambiguous',['reconciliation-required']),
    'conflict':('succeeded','ambiguous',['observation-conflict']),
    'prior-unresolved':('ambiguous','ambiguous',['blind-retry-blocked','receipt-missing']),
    'later-unresolved':('succeeded','ambiguous',['receipt-missing']),
    'stale-paused':('succeeded','succeeded',['stale-admission','stale-fence']),
}

def unsigned(name):
    fixture,state,journal=running()
    kinds={'packet':'work-packet','goal':'goal-spec','plan':'plan-revision','lease':'work-lease','route':'route-assignment','budget':'budget-reservation'}
    context={key:copy.deepcopy(next(r for r in state['records'] if r['object_type']==kind)) for key,kind in kinds.items()}
    p=context['packet']['payload']
    trace=load(ROOT/'scripts/tests/v3/integrity/fixtures/F-M1C-007.json')['input']
    intent=trace['intent'];intent.update(effect_id='effect:EFFECT-ID-PAUSED',actor_id='actor:'+p['logical_worker_actor_id'],lease_id='lease:'+p['work_lease_ref']['lease_id'],goal_spec_id='goal:'+context['goal']['id'],
        goal_spec_digest=pref(context['goal']['content_digest']),plan_digest=pref(context['plan']['content_digest']),policy_digest=pref(p['authority_policy_ref']['content_digest']),privacy_digest=pref(p['privacy_policy_ref']['content_digest']),
        route_digest=pref(context['route']['content_digest']),budget_digest=pref(context['budget']['content_digest']),grant_digest=dh(grant_for(context['packet'])),
        admission_epoch=1,fence_epoch=1,idempotency_key='idempotency:original-effect',command_id='command:original-dispatch')
    intent['intent_digest']=dh({k:v for k,v in intent.items() if k!='intent_digest'})
    admission=trace['admission']
    for key in admission.keys() & intent.keys()-{'type'}:admission[key]=intent[key]
    trace['current_admission_epoch']=1;trace['current_fence_epoch']=1
    for record in trace['observations']:
        for key in ('effect_id','idempotency_key','target_ref','payload_digest','admission_epoch','fence_epoch'):record[key]=intent[key]
    records=trace.pop('observations');start,external,receipt=copy.deepcopy(records)
    prefix=3;label='observed-success';ri=2;oi=2
    if name=='failure':
        records=[start,receipt];records[1]['result']='failed';prefix=2;label='observed-failure';ri=1;oi=1
    elif name in ('ambiguous','late-receipt','late-reconciliation','unverified','prior-unresolved'):
        records=[start,external];prefix=2;label='ambiguous';ri=None;oi=1
        if name=='late-receipt':records.append(receipt)
        elif name=='late-reconciliation':
            rec=copy.deepcopy(receipt);rec['type']='ReconciliationObserved@1';rec['reconciliation_id']='reconciliation:one';rec['outcome']=rec.pop('result');rec.pop('receipt_id');records.append(rec)
        elif name=='unverified':records[1]['authenticity']='unverified'
        elif name=='prior-unresolved':
            second=copy.deepcopy(start);second.update(attempt_id='attempt:2',attempt_number=2,observed_at='2026-09-04T12:03:00Z')
            last=copy.deepcopy(receipt);last.update(attempt_id='attempt:2',attempt_number=2,observed_at='2026-09-04T12:04:00Z')
            records.extend([second,last])
    elif name=='conflict':
        last=copy.deepcopy(receipt);last.update(receipt_id='receipt:conflict',observed_at='2026-09-04T12:03:00Z',result='failed');records.append(last)
    elif name=='later-unresolved':
        second=copy.deepcopy(start);second.update(attempt_id='attempt:2',attempt_number=2,observed_at='2026-09-04T12:03:00Z')
        unknown=copy.deepcopy(external);unknown.update(attempt_id='attempt:2',attempt_number=2,observed_at='2026-09-04T12:04:00Z',observation_id='observation:later',outcome='unknown')
        records.extend([second,unknown])
    observation=copy.deepcopy(fixture['commands'][-1]['payload'])
    observation['payload'].update(observation=label,quarantine=label=='ambiguous',idempotency_key_digest=rawhash(intent['idempotency_key'].encode()),
        receipt_digest=None if ri is None else rawhash(canonical(records[ri])),provider_operation_id_digest=None if oi is None else rawhash(records[oi]['remote_operation_ref'].encode()))
    context['observation']=m1a.seal(observation);context['grant']=grant_for(context['packet']);context['mapping']=mapping_for(context['packet'])
    assessment={'current_admission_epoch':2 if name=='stale-paused' else 1,'current_fence_epoch':2 if name=='stale-paused' else 1,'current_pause_state':'paused' if name=='stale-paused' else 'running'}
    cut={'cut_id':'cut:'+name,'context':context,'prefix_length':prefix,'trace_header':trace,'ordered_inventory':[dh(r) for r in records],
         'receipt_index':ri,'operation_index':oi,'assessment':assessment}
    return {'cut':cut,'records':records}

def package(original,keys):
    cut=original['cut'];records=original['records'];header=cut['trace_header']
    return {'cut':sign(cut,'collector',keys),
        'dispatch':sign({'cut_id':cut['cut_id'],'intent':header['intent'],'admission':header['admission'],'starts':[{'ordinal':i,'record':r} for i,r in enumerate(records) if r['type']=='AttemptStarted@1']},'dispatcher',keys),
        'evidence':[sign({'cut_id':cut['cut_id'],'ordinal':i,'record':r},'dispatcher' if r['type']=='AttemptStarted@1' else 'observer',keys) for i,r in enumerate(records)]}

def refresh(original):
    original['cut']['ordered_inventory']=[dh(r) for r in original['records']]
    return original
