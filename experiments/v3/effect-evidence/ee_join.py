"""Restricted evidence-cut adapter. Successful classification never grants authority."""
import copy, hmac, re
from ee_common import canonical,rawhash,dh,ref,pref,tid,m1a,classify,require

DOMAIN='recursion-effect-evidence-fixture-v1'
ISSUERS={'collector':'fixture-ledger','dispatcher':'fixture-dispatch','observer':'fixture-observer'}

def sign(body,role,keys):
    envelope={'domain':DOMAIN,'role':role,'issuer':ISSUERS[role],'body':copy.deepcopy(body)}
    envelope['mac']=hmac.digest(keys[role],canonical(envelope),'sha256').hex()
    return envelope

def verify(envelope,role,keys,mutant=None):
    require(set(envelope)=={'domain','role','issuer','body','mac'},'closed-envelope')
    require(envelope['domain']==DOMAIN,'signature-domain')
    if mutant!='role':require(envelope['role']==role and envelope['issuer']==ISSUERS[role],'issuer-role')
    selected=envelope['role'] if mutant=='role' else role
    unsigned={k:v for k,v in envelope.items() if k!='mac'}
    require(hmac.compare_digest(envelope['mac'],hmac.digest(keys[selected],canonical(unsigned),'sha256').hex()),'signature-mismatch')
    return copy.deepcopy(envelope['body'])

def grant_for(packet):
    return {'type':'SyntheticGrant@1','packet_ref':ref(packet),'authority_ids':packet['payload']['authority_ids'],'operational_authority':False}

def mapping_for(packet):
    p=packet['payload']
    return {'profile':'fixture-explicit-epoch-embedding-v1',
            'admission':{'source_domain':'m1a-pause','source':p['expected_pause_epoch'],'target_domain':'m1c-admission','target':p['expected_pause_epoch']+1},
            'fence':{'source_domain':'m1a-goal-fence','source':p['expected_goal_fence_epoch'],'target_domain':'m1c-fence','target':p['expected_goal_fence_epoch']},
            'work_lease_epoch':p['work_lease_ref']['lease_epoch'],
            'worker_attempt':p['attempt'],'effect_attempt_mapping':'independent-ordered-starts',
            'time_mapping':'supplied-utc-evidence-no-logical-clock-conversion'}

def expected_intent_fields(context):
    p=context['packet']['payload'];o=context['observation']['payload']
    return {'effect_id':tid('effect',o['effect_id']),
        'actor_id':tid('actor',p['logical_worker_actor_id']),
        'lease_id':tid('lease',p['work_lease_ref']['lease_id']),
        'goal_spec_id':tid('goal',context['goal']['id']),
        'goal_spec_digest':pref(context['goal']['content_digest']),
        'plan_digest':pref(context['plan']['content_digest']),
        'policy_digest':pref(p['authority_policy_ref']['content_digest']),
        'privacy_digest':pref(p['privacy_policy_ref']['content_digest']),
        'route_digest':pref(context['route']['content_digest']),
        'budget_digest':pref(context['budget']['content_digest']),
        'grant_digest':dh(grant_for(context['packet'])),
        'admission_epoch':p['expected_pause_epoch']+1,
        'fence_epoch':p['expected_goal_fence_epoch']}

def check_context(c,intent,mutant):
    require(set(c)=={'observation','packet','goal','plan','lease','route','budget','grant','mapping'},'context-shape')
    for kind in ('observation','packet','goal','plan','lease','route','budget'):
        record=c[kind];m1a.validate_domain_record(record)
        require(record['content_digest']==m1a.digest(record,omit_content_digest=True),'m1a-digest')
    p=c['packet']['payload'];o=c['observation']['payload']
    require(canonical(c['grant'])==canonical(grant_for(c['packet'])),'synthetic-grant')
    require(canonical(c['mapping'])==canonical(mapping_for(c['packet'])),'typed-mapping')
    if mutant!='context':
        require(o['work_packet_ref']==ref(c['packet']),'observation-packet')
        for name,field in [('goal','goal_ref'),('plan','plan_ref'),('route','route_assignment_ref'),('budget','budget_reservation_ref')]:
            require(p[field]==ref(c[name]),'packet-'+name)
        lease=c['lease'];require(p['work_lease_ref']=={'lease_id':lease['id'],'lease_epoch':lease['payload']['lease_epoch'],'content_digest':lease['content_digest']},'packet-lease')
        require(lease['payload']['subject_actor_id']==p['logical_worker_actor_id'] and lease['payload']['goal_ref']==p['goal_ref'] and lease['payload']['plan_ref']==p['plan_ref'],'lease-context')
        require(lease['payload']['task_ref']==p['task_ref'],'lease-task')
        require(c['plan']['payload']['goal_ref']==p['goal_ref'],'plan-goal')
        require(p['task_ref'] in c['plan']['payload']['task_node_refs'],'plan-task')
        for field in ('goal_ref','plan_ref','task_ref'):require(c['budget']['payload'][field]==p[field],'budget-'+field)
        require(c['route']['payload']['logical_actor_id']==p['logical_worker_actor_id'],'route-actor')
        require(p['expected_goal_fence_epoch']==c['goal']['payload']['fence_epoch'],'goal-fence')
        require(o['effect_key'] in c['goal']['payload']['allowed_effect_keys'] and o['effect_key'] in c['plan']['payload']['effect_keys'],'goal-plan-effect')
        require(o['effect_key'] in p['effect_keys'],'effect-capability')
        for key,value in expected_intent_fields(c).items():require(intent[key]==value,'intent-context/'+key)
    require(rawhash(intent['idempotency_key'].encode('utf-8'))==o['idempotency_key_digest'],'original-key-digest')

def join(bundle,keys,mutant=None):
    require(set(bundle)=={'cut','dispatch','evidence'},'bundle-shape')
    cut=verify(bundle['cut'],'collector',keys,mutant)
    require(set(cut)=={'cut_id','context','prefix_length','trace_header','ordered_inventory','receipt_index','operation_index','assessment'},'cut-shape')
    require(isinstance(cut['cut_id'],str) and re.fullmatch(r'cut:[A-Za-z0-9._~-]{1,128}',cut['cut_id']) is not None,'cut-identity-profile')
    header=cut['trace_header'];require(set(header)=={'type','intent','admission','dependency_states','current_admission_epoch','current_fence_epoch','effect_count','external_call_count'},'header-shape')
    dispatch=verify(bundle['dispatch'],'dispatcher',keys,mutant)
    require(set(dispatch)=={'cut_id','intent','admission','starts'},'dispatch-shape')
    require(dispatch['cut_id']==cut['cut_id'] and canonical(dispatch['intent'])==canonical(header['intent']) and canonical(dispatch['admission'])==canonical(header['admission']),'original-dispatch-binding')
    records=[]
    for index,envelope in enumerate(bundle['evidence']):
        # Expected signer is derived from the signed record type, then checked.
        raw=envelope['body'];role='dispatcher' if raw['record']['type']=='AttemptStarted@1' else 'observer'
        body=verify(envelope,role,keys,mutant)
        require(set(body)=={'cut_id','ordinal','record'} and body['cut_id']==cut['cut_id'] and type(body['ordinal'])is int and body['ordinal']==index,'ordered-envelope')
        records.append(body['record'])
    starts=[{'ordinal':i,'record':r} for i,r in enumerate(records) if r['type']=='AttemptStarted@1']
    require(canonical(dispatch['starts'])==canonical(starts),'original-starts')
    if mutant!='inventory':require(cut['ordered_inventory']==[dh(r) for r in records],'complete-ordered-cut')
    n=cut['prefix_length'];require(type(n)is int and 0<=n<=len(records),'historical-prefix')
    c=cut['context'];check_context(c,header['intent'],mutant)
    # Header assessment uses the original epochs; supplied current epochs stay outside it.
    require(header['current_admission_epoch']==header['intent']['admission_epoch'] and header['current_fence_epoch']==header['intent']['fence_epoch'],'original-assessment')
    prefix=copy.deepcopy(header);prefix['observations']=records[:n]
    full=copy.deepcopy(header);full['observations']=records
    a=cut['assessment'];require(set(a)=={'current_admission_epoch','current_fence_epoch','current_pause_state'} and a['current_pause_state'] in ('running','paused'),'assessment-shape')
    full.update({k:a[k] for k in ('current_admission_epoch','current_fence_epoch')})
    old=classify(prefix);current=classify(full);o=c['observation']['payload']
    labels={'observed-success':('succeeded','reconciled-succeeded'),'observed-failure':('failed','reconciled-failed'),'ambiguous':('ambiguous','executing')}
    require(old['status'] in labels[o['observation']],'historical-label-mismatch')
    require((o['dispatch_state']=='dispatched')==any(r['type']=='AttemptStarted@1' for r in records[:n]),'historical-dispatch')
    for field,index_field in [('receipt_digest','receipt_index'),('provider_operation_id_digest','operation_index')]:
        index=cut[index_field]
        if o[field] is None:require(index is None,'unexpected-digest-binding');continue
        require(type(index)is int and 0<=index<n,'historical-digest-index')
        record=records[index]
        if field=='receipt_digest':
            require(record['type']=='ReceiptRecorded@1','receipt-record-type');actual=rawhash(canonical(record))
        else:
            operation=record.get('remote_operation_ref');require(isinstance(operation,str),'operation-reference');actual=rawhash(operation.encode('utf-8'))
        require(actual==o[field],'historical-'+field)
    return {'type':'RestrictedEffectJoinResult@1','status':'joined-as-of-trusted-cut',
        'historical':old,'current':current,'current_pause_state':a['current_pause_state'],
        'observation_digest':c['observation']['content_digest'],'cut_id':cut['cut_id'],
        'ordered_inventory':cut['ordered_inventory'],'trace':full,
        'unsettled_attempt_ids':unsettled(records),
        'runtime_settlement_hold':bool(unsettled(records)) or current['requires_reconciliation'],
        'runtime_permission':False,'canonical_write_count':0,'production_authentication':False}

def unsettled(records):
    """Conservative local diagnostic, separate from the unchanged literal oracle."""
    pending=set()
    for r in records:
        key=r['attempt_id'];kind=r['type'];verified=r.get('authenticity')=='verified'
        if kind=='AttemptStarted@1':pending.add(key)
        elif kind=='ExternalObserved@1':
            if verified and r['outcome']=='rejected':pending.discard(key)
            elif r['outcome'] in ('accepted','unknown'):pending.add(key)
        elif verified and ((kind=='ReceiptRecorded@1' and r['result'] in ('succeeded','failed')) or (kind=='ReconciliationObserved@1' and r['outcome'] in ('succeeded','failed'))):pending.discard(key)
    return sorted(pending)
