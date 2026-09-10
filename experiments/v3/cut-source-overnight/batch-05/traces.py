"""Initialized retained prefixes and explicitly translated canonical schedules."""
import copy
import semantic as rel
import s_inclusive as sa
import s_split as sb
import s_audit as sc
import q_inclusive as qa
import q_split as qb
import q_audit as qc
s,q=rel.s,rel.q
require,exact,digest=rel.require,rel.exact,rel.digest
MAX_VISITS=10000

def source_only(action):
    verb=action.split('@')[0]
    return verb.startswith(('register:','attempt:','atomic:','append:','collect:')) or verb in ('append-lose-reply','collect-open')

def order(profile):
    result=[]
    while len(result)<len(profile['actions']):
        available=sorted(a for a in profile['actions'] if a not in result and set(profile['requires'][a])<=set(result))
        require(available,'acyclic original schedule')
        result.append(available[0])
    return tuple(result)

def replay(side,profile,unit,outcome,actions,budget):
    require(budget[0]+len(actions)+1<=MAX_VISITS,'pre-execution aggregate prefix state-visit bound')
    budget[0]+=len(actions)+1
    domain,a,b,audit=(s,sa,sb,sc) if side=='source' else (q,qa,qb,qc)
    current=domain.initial(unit);audit.initialization(current,unit)
    initial=copy.deepcopy(current);states=[current];events=[]
    for action in actions:
        enabled=set(domain.ready_actions(current,profile))
        require(enabled==audit.enabled(current,profile) and action in enabled,'own complete enabledness and schedule')
        following=a.step(current,action,profile,unit,outcome)
        require(exact(following,domain.flatten(b.step(domain.split(current),action,profile,unit,outcome))),'original inclusive/split agreement')
        audit.check(current,action,following,profile,unit,outcome)
        require(following['done'].bit_count()==current['done'].bit_count()+1,'own schedule rank')
        patch={k:v for k,v in following.items() if not exact(v,current[k])}
        events.append({'action':action,'before_sha256':digest(current),'after_sha256':digest(following),'patch':patch,'observation':rel.observation(following,action)})
        current=following;states.append(current)
    trace={'side':side,'unit':unit,'outcome':outcome,'schedule':profile,'actions':actions,'initial':initial,'events':events,
        'remaining_actions':tuple(a for a in profile['actions'] if a not in actions),'terminal_sha256':digest(current)}
    verify_trace(trace)
    return trace,states

def verify_trace(trace):
    current=copy.deepcopy(trace['initial']);actions=trace['actions'];profile=trace['schedule']
    require(len(actions)==len(trace['events']) and len(set(actions))==len(actions),'complete nonduplicate retained event inventory')
    executed=[]
    for i,event in enumerate(trace['events']):
        action=actions[i]
        require(event['action']==action and action in profile['actions'] and set(profile['requires'][action])<=set(executed),'retained own schedule dependency')
        require(digest(current)==event['before_sha256'] and set(event['patch'])<=set(current),'single retained state chain')
        current.update(event['patch']);executed.append(action)
        require(digest(current)==event['after_sha256'] and exact(event['observation'],rel.observation(current,action)),'retained state and visible observation')
        require(current['done']==sum(1<<profile['actions'].index(a) for a in executed),'own target/source ordinal bookkeeping')
    require(digest(current)==trace['terminal_sha256'],'retained terminal state')
    require(exact(trace['remaining_actions'],tuple(a for a in profile['actions'] if a not in executed)),'explicit unexecuted suffix')

def verify_pairs(pairs,source,target):
    seen=[]
    for row in pairs:
        si,ti=row['source_event'],row['target_event']
        require(type(si) is int and type(ti) is int and 0<=si<len(source[0]['events']) and 0<=ti<len(target[0]['events']),'binding event bounds')
        ss,st=source[1][si:si+2];qs,qt=target[1][ti:ti+2]
        sv=source[0]['actions'][si].split('@')[0];tv=target[0]['actions'][ti].split('@')[0]
        require(sv==tv and rel.token(row['source']) and rel.token(row['target']),'binding action and token namespace')
        require(exact(row['source'],st['source_generation']) and exact(row['target'],qt['source_generation']),'binding actual immutable successor tokens')
        if row['reason']=='paired-successful-attestation':
            require(sv=='source-attest' and st['decision']==qt['decision']=='source-attest:ok' and exact(ss['cut_delivery'],qs['cut_delivery']),'successful same-input attestation binding')
        else:
            require(row['reason']=='paired-restart' and sv=='source-restart' and rel.generation_pair(ss['source_generation'],qs['source_generation'],seen),'retained predecessor incarnation binding')
            require(st['source_generation'][-1]==ss['source_generation'][-1]+1 and qt['source_generation'][-1]==qs['source_generation'][-1]+1,'both original restarts advance')
        require(not any(exact(row['source'],x['source']) or exact(row['target'],x['target']) for x in seen),'immutable injective incarnation ledger')
        seen.append(row)

def verify_available(pairs,si,ti,include_current=False):
    for row in pairs:
        require(row['source_event']<=si if include_current else row['source_event']<si,'source binding must exist at this prefix')
        require(row['target_event']<=ti if include_current else row['target_event']<ti,'target binding must exist at this prefix')

def compare(name,source,target):
    pairs=[];rows=[];samples=[];ti=0
    require(all(rel.field_pair(source[1][0],target[1][0],k,pairs) for k in rel.FIELDS),'independent initialized common state relation')
    for si,event in enumerate(source[0]['events']):
        action=event['action']
        verify_available(pairs,si,ti)
        if source_only(action):
            rows.append({'source_event':si,'target_event':None,'source_action':action,'status':'unmatched-visible-source-event',
                'justification':'No target operation is declared for this registered-source action; its response remains an unmatched observation.',
                'source_observation':event['observation'],'target_observation':None})
            continue
        require(ti<len(target[0]['events']),'complete declared target action inventory')
        target_action=target[0]['events'][ti]['action']
        require(action.split('@')[0]==target_action.split('@')[0],'exact shared verb and explicit parameters')
        before_s,after_s=source[1][si:si+2];before_q,after_q=target[1][ti:ti+2]
        relation_before=all(rel.field_pair(before_s,before_q,k,pairs) for k in rel.FIELDS)
        binding=rel.advance(pairs,before_s,before_q,after_s,after_q,action,target_action,si,ti)
        verify_pairs(pairs,source,target)
        verify_available(pairs,si,ti,include_current=True)
        row=rel.report(after_s,after_q,pairs,action,target_action)
        row.update(source_event=si,target_event=ti,prestate_related=relation_before,binding=binding,
            justification='Identity translation preserves the literal shared operation and parameters, unit and outcome; differing preconditions/effects remain checked results.')
        rows.append(row)
        samples.append((copy.deepcopy(row),after_s,after_q,copy.deepcopy(pairs),action,target_action))
        ti+=1
    require(ti==len(target[0]['events']),'no target event omitted from comparison')
    counts={'related_poststate_and_response':sum(r.get('state_related',False) and r.get('responses_related',False) for r in rows),
        'matching_transitions':sum(r.get('prestate_related',False) and r.get('state_related',False) and r.get('responses_related',False) for r in rows),
        'prestate_gap':sum('prestate_related' in r and not r['prestate_related'] for r in rows),
        'state_gap':sum('state_related' in r and not r['state_related'] for r in rows),
        'response_gap':sum('responses_related' in r and not r['responses_related'] for r in rows),
        'unmatched_source_events':sum(r.get('status')=='unmatched-visible-source-event' for r in rows),
        'paired_events':ti,'source_events':len(rows)}
    require(counts['paired_events']+counts['unmatched_source_events']==counts['source_events'],'complete visible event accounting')
    return {'case':name,'source':source[0],'target':target[0],'rows':rows,'incarnation_pairs':pairs,'counts':counts,
        'all_paired_transitions_related':counts['prestate_gap']==counts['state_gap']==counts['response_gap']==0,
        'complete_visible_trace_correspondence':counts['unmatched_source_events']==counts['prestate_gap']==counts['state_gap']==counts['response_gap']==0},samples

def prefix(profile):
    stop=next(i for i,a in enumerate(profile['actions']) if a.split('@')[0]=='reconcile')
    return tuple(profile['actions'][:stop+1])

def run(packet):
    cases=[];samples=[];visits=0;budget=[0]
    for cut,outcome in (('success',1),('failure',2)):
        for unit in s.UNITS:
            sp,qp=s.PROFILES['pending-'+cut],q.PROFILES['current-'+cut]
            source=replay('source',sp,unit,outcome,prefix(sp),budget);target=replay('target',qp,unit,outcome,prefix(qp),budget)
            result,found=compare('original-prefix/'+cut+'/'+unit,source,target)
            result['target_schedule_kind']='original Q current-'+cut+' prefix through first reconciliation'
            cases.append(result);samples+=found;visits+=len(source[1])+len(target[1])
    if packet=='C':
        require(len(s.PROFILES)==51,'unchanged source profile domain')
        for name,profile in s.PROFILES.items():
            actions=order(profile)
            translated=q.sequence([a.split('@')[0] for a in actions if not source_only(a)])
            translated['outcomes']=profile['outcomes']
            for unit in s.UNITS:
                for outcome in profile['outcomes']:
                    source=replay('source',profile,unit,outcome,actions,budget)
                    target=replay('target',translated,unit,outcome,translated['actions'],budget)
                    result,found=compare('canonical/'+name+'/'+unit+'/'+str(outcome),source,target)
                    result['target_schedule_kind']='Declared linear schedule: lexicographic topological source order, identity shared operations, source-only events retained unmatched.'
                    require(not source[0]['remaining_actions'] and not target[0]['remaining_actions'],'complete selected schedules')
                    cases.append(result);samples+=found;visits+=len(source[1])+len(target[1])
                    require(visits<=MAX_VISITS,'reserved aggregate prefix state-visit bound')
        require(len(cases)==108,'four original prefixes and104 unchanged source environments')
    controls=[]
    def reject(label,fn):
        try:fn()
        except ValueError as error:controls.append({'control':label,'detected':True,'reason':str(error)})
        else:raise ValueError('undetected checker control: '+label)
    def core(row):return {k:v for k,v in row.items() if k not in ('source_event','target_event','prestate_related','binding','justification')}
    positive=next(x for x in samples if x[0]['state_related'] and x[0]['responses_related'] and x[1]['publication_reply'])
    row,a,b,pairs,action,other=positive;row=core(row)
    for label,key,value in [('hidden-visible-response','source_observation',{}),('misbound-source','source_sha256','0'*64),('misbound-target','target_sha256','0'*64),('lost-incarnation-ledger','pairs_sha256','0'*64)]:
        bad=copy.deepcopy(row);bad[key]=value
        reject(label,lambda bad=bad:rel.verify_report(bad,a,b,pairs,action,other))
    changed=copy.deepcopy(b);changed['selected']=changed['selected']._replace(signature='0'*64)
    reject('unvalidated-original-signature',lambda:require(rel.pair_envelope(a['selected'],changed['selected'],pairs),'each original body signature must validate'))
    changed2=copy.deepcopy(b);r=changed2['publication_reply'];changed2['publication_reply']=(r[0],'0'*64,*r[2:])
    reject('unbound-visible-receipt-digest',lambda:require(rel.own_receipt(b['selected'],changed2['publication_reply']),'reply digest must bind its own original envelope'))
    remapped=copy.deepcopy(pairs);remapped[0]['target']=q.source_token(999)
    reject('rewritten-historical-incarnation',lambda:require(rel.pair_envelope(a['selected'],b['selected'],remapped),'historical envelope requires its original incarnation pair'))
    reject('incarnation-pair-used-before-establishment',lambda:verify_available(pairs,0,0))
    changed3=copy.deepcopy(b);changed3['publication_receipts']=list(changed3['publication_receipts'])
    reject('receipt-container-type-erasure',lambda:require(rel.field_pair(a,changed3,'publication_receipts',pairs),'original receipt container type must remain exact'))
    reject('bool-integer-identity-conflation',lambda:require(exact(('publisher-boot','authority',True),('publisher-boot','authority',1)),'typed identity rejects bool/integer conflation'))
    trace=copy.deepcopy(cases[0]['source']);trace['events'].pop(6)
    reject('dropped-unmatched-source-event',lambda:verify_trace(trace))
    trace2=copy.deepcopy(cases[0]['target']);trace2['events'][0],trace2['events'][1]=trace2['events'][1],trace2['events'][0]
    reject('discontinuous-target-history',lambda:verify_trace(trace2))
    if packet=='C':
        negative=next(x for x in samples if not x[0]['responses_related'])
        nr,na,nb,np,nsa,nta=negative;bad=core(copy.deepcopy(nr));bad['responses_related']=True
        reject('rejection-promoted-to-equivalence',lambda:rel.verify_report(bad,na,nb,np,nsa,nta))
    require(visits==budget[0] and visits<=MAX_VISITS,'conservative no-refund state-visit reservation')
    return {'packet':packet,'cases':cases,'controls':controls,'state_visits_per_representation':visits,'state_visit_reservation':MAX_VISITS,
        'graph_search_performed':False,'canonical_traces_are_all_interleavings':False,
        'original_Q_prefix_cases':4,'translated_target_schedule_cases':len(cases)-4,
        'complete_visible_refinement_proved':False,'whole_path_composition_proved':False,'source_truth_established':False,
        'deferred_questions_resolved':[],'original_models_changed':False}
