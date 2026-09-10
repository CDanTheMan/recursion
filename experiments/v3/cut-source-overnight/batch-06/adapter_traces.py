"""One-to-one visible histories over own initialized source and adapter states."""
import copy
import a_domain as d
import a_inclusive as aa
import a_split as ab
import a_audit as audit
import s_inclusive as sa
import s_split as sb
import s_audit as sc
import guard_audit
r=d.rel
MAX_VISITS=10000
FOCUS=('pending-success','append-between-collect-and-publish','pending-after-selected','publication-source-race','publication-duplicate-retired')

def core_view(adapter):
    return dict(adapter['core'],**{k:adapter['journal'][k] for k in d.s.EXTRA},decision=adapter['decision'])

def related(source,adapter,pairs):
    common=[k for k in r.FIELDS if not r.field_pair(source,adapter['core'],k,pairs)]
    journal=[k for k in (*d.s.EXTRA,'source_generation') if not d.exact(source[k],adapter['journal'][k])]
    return common,journal

def response(source,adapter,action,pairs):
    k=action.split('@')[0]
    return d.exact(source['decision'],adapter['decision']) and (not (k.startswith('append:') or k=='append-lose-reply') or d.exact(source['append_reply'],adapter['journal']['append_reply'])) and (not k.startswith('pub-') or r.field_pair(source,adapter['core'],'publication_reply',pairs))

def gap_certificate(source,adapter,pairs):
    """Diagnose strict relation gaps without extending it or establishing a pair."""
    left,right=source['staged'],adapter['core']['staged']
    both=bool(left and right)
    facts=dict(staged_exact_typed=d.exact(left,right),source_signature_valid=bool(left and r.signed(left[0])),
        target_signature_valid=bool(right and r.signed(right[0])),no_established_pairs=not pairs,
        source_payload_valid=bool(left and left[1]==d.q.raw_cut(left[0].cut)),
        target_payload_valid=bool(right and right[1]==d.q.raw_cut(right[0].cut)),
        both_sources_unattested=not source['source_name'] and not adapter['core']['source_name'],
        same_live_generation=d.exact(source['source_generation'],adapter['core']['source_generation']),
        own_current_stage_generation=bool(both and d.exact(left[0].source_generation,source['source_generation']) and d.exact(right[0].source_generation,adapter['core']['source_generation'])))
    return dict(source_sha256=d.digest(source),adapter_sha256=d.digest(adapter),facts=facts,
        staged_source_generation=left[0].source_generation if left else None,
        staged_target_generation=right[0].source_generation if right else None,
        identical_valid_unattested_objects=all(v for k,v in facts.items() if k!='own_current_stage_generation'),
        acceptance_relation_changed=False,incarnation_pair_established=False)

def comparison(before_s,before_a,after_s,after_a,oldpairs,pairs,action,index,call):
    pre=related(before_s,before_a,oldpairs);post=related(after_s,after_a,pairs)
    semantic=r.report(after_s,core_view(after_a),pairs,action,action)
    d.require(semantic['differing_fields']==post[0],'independent recursive common-field relation')
    d.require(response(after_s,after_a,action,pairs)==(semantic['responses_related'] and (not (action.startswith('append:') or action.startswith('append-lose-reply@')) or d.exact(after_s['append_reply'],after_a['journal']['append_reply']))),'semantic and exact append response relation')
    return dict(index=index,source_action=action,adapter_action=action,source_sha256=d.digest(after_s),adapter_sha256=d.digest(after_a),
        pairs_sha256=d.digest(pairs),prestate_related=not any(pre),state_related=not any(post),responses_related=response(after_s,after_a,action,pairs),
        differing_common_fields=post[0],differing_journal_fields=post[1],source_observation=r.observation(after_s,action),
        adapter_observation=r.observation(core_view(after_a),action),q_invoked=call,justification=d.justification(action,call))

def trace_event(before,after,action,adapter=False):
    if adapter:
        patch={k:({f:v for f,v in after[k].items() if not d.exact(v,before[k][f])} if k in ('core','journal') else after[k]) for k in after if not d.exact(before[k],after[k])}
    else:patch={k:v for k,v in after.items() if not d.exact(v,before[k])}
    return dict(action=action,before_sha256=d.digest(before),after_sha256=d.digest(after),patch=patch)

def restore(trace):
    current=copy.deepcopy(trace['initial']);states=[current];executed=[]
    d.require(len(trace['events'])==len(trace['actions']),'complete visible event inventory')
    for action,event in zip(trace['actions'],trace['events']):
        d.require(event['action']==action and action not in executed and set(trace['profile']['requires'][action])<=set(executed),'literal occurrence and outer dependency')
        d.require(d.digest(current)==event['before_sha256'],'history prestate binding')
        current=copy.deepcopy(current)
        for k,v in event['patch'].items():
            if trace['side']=='adapter' and k in ('core','journal'):current[k].update(v)
            else:current[k]=v
        executed.append(action)
        d.require(d.digest(current)==event['after_sha256'] and current['done']==sum(1<<trace['profile']['actions'].index(a) for a in executed),'history poststate and completion binding')
        if trace['side']=='adapter':
            qp=trace['q_profile'];d.require(d.exact(qp,d.subprofile(trace['profile'])),'fixed Q occurrence positions')
            d.require(current['core']['done']==sum(1<<qp['actions'].index(a) for a in current['invocations']),'retained actual Q invocation mask')
        states.append(current)
    return states

def certificate(before,after,action,index):
    if action.split('@')[0]!='source-attest':return None
    ledger,reason,call=guard_audit.expected(d.view(before),action,{})
    item={'index':index,'before_sha256':d.digest(before),'after_sha256':d.digest(after),'ledger_guard_decision':reason,
          'q_invoked':call,'q_decision':after['core']['decision'] if call else None,'journal_changed':not d.exact(before['journal']['attestation'],after['journal']['attestation'])}
    if call:
        own=before['core'];j=before['journal'];name=own['cut_delivery'];f=d.q.lit.fixture(name)
        prior=d.q.record_ids(own['source_name']) if own['source_name'] else ();new=d.q.record_ids(name)
        facts={'capture_current':d.exact(j['collection'][:2],(j['source_generation'],j['source_revision'])),
            'full_inventory':d.exact(j['collected'],tuple(enumerate(d.s.records(name)))),
            'complete_registry':d.exact(j['collection'][2:4],(d.s.registration(name),d.s.mapping(name))),
            'remote_present':own['remote']!=0,'reservation_matches':list(own['bindings'][0])==f['binding']['body']['reservation'],
            'record_prefix':new[:len(prior)]==prior,'scope_matches':not own['source_name'] or d.q.scope(own['source_name'])==d.q.scope(name)}
        item['facts']=facts
        if after['core']['decision']=='source-attest:ok':d.require(all(facts.values()),'successful actual Q attestation compatibility')
    return item

def run(packet):
    cases=[];samples=[];visits=0
    selected=d.s.PROFILES if packet=='C' else {name:d.s.PROFILES[name] for name in FOCUS}
    for name,profile in selected.items():
        actions=d.order(profile)
        for unit in d.s.UNITS:
            for outcome in profile['outcomes']:
                visits+=2*(len(actions)+1);d.require(visits<=MAX_VISITS,'aggregate pre-execution state-visit ceiling')
                source=d.s.initial(unit);adapter=d.initial(unit);sc.initialization(source,unit);audit.initialization(adapter,unit)
                st=dict(side='source',initial=copy.deepcopy(source),profile=profile,actions=actions,events=[])
                at=dict(side='adapter',initial=copy.deepcopy(adapter),profile=profile,q_profile=d.subprofile(profile),actions=actions,events=[])
                rows=[];pairs=[];certs=[];gaps=[]
                d.require(not any(related(source,adapter,pairs)),'independently initialized complete state relation')
                for index,action in enumerate(actions):
                    d.require(set(d.s.ready_actions(source,profile))==sc.enabled(source,profile) and action in sc.enabled(source,profile),'original complete source enabledness')
                    ns=sa.step(source,action,profile,unit,outcome)
                    d.require(d.exact(ns,d.s.flatten(sb.step(d.s.split(source),action,profile,unit,outcome))),'original S inclusive/split agreement')
                    sc.check(source,action,ns,profile,unit,outcome)
                    na=aa.step(adapter,action,profile,unit,outcome)
                    d.require(d.exact(na,ab.step(adapter,action,profile,unit,outcome)),'adapter inclusive/split agreement')
                    call=audit.check(adapter,action,na,profile,unit,outcome)
                    oldpairs=copy.deepcopy(pairs)
                    binding=r.advance(pairs,source,core_view(adapter),ns,core_view(na),action,action,index,index)
                    d.require(all(p['source_event']<=index and p['target_event']<=index for p in pairs),'causal immutable incarnation ledger')
                    row=comparison(source,adapter,ns,na,oldpairs,pairs,action,index,call);row['binding']=binding
                    rows.append(row)
                    if not row['state_related']:gaps.append(dict(index=index,**gap_certificate(ns,na,pairs)))
                    cert=certificate(adapter,na,action,index)
                    if cert:certs.append(cert)
                    samples.append((name,source,adapter,ns,na,profile,unit,outcome,action,copy.deepcopy(pairs),oldpairs,call,row))
                    st['events'].append(trace_event(source,ns,action));at['events'].append(trace_event(adapter,na,action,True))
                    source,adapter=ns,na
                d.require(d.exact(restore(st)[-1],source) and d.exact(restore(at)[-1],adapter),'retained independently replayable histories')
                cases.append(dict(case=name+'/'+unit+'/'+str(outcome),source=st,adapter=at,rows=rows,incarnation_pairs=pairs,attestation_certificates=certs,state_gap_certificates=gaps,
                    complete_selected_trace_correspondence=all(x['prestate_related'] and x['state_related'] and x['responses_related'] for x in rows),
                    source_events=len(rows),adapter_events=len(rows),q_invocations=len(adapter['invocations']),unmatched_visible_events=0))
    d.require(len(cases)==(104 if packet=='C' else 10),'preregistered selected environment cardinality')
    controls=[]
    def reject(label,fn):
        try:fn()
        except (ValueError,KeyError,IndexError,TypeError) as error:controls.append(dict(control=label,detected=True,reason=str(error)))
        else:raise ValueError('undetected control: '+label)
    def changed_state(label,predicate,mutate):
        sample=next(x for x in samples if predicate(x));_,bs,ba,ns,na,p,u,o,action,pairs,oldpairs,call,row=sample
        bad=copy.deepcopy(na);mutate(bad,sample)
        reject(label,lambda:audit.check(ba,action,bad,p,u,o))
    changed_state('lost-append-reply',lambda x:x[8].startswith('append:') and bool(x[4]['journal']['append_reply']),lambda n,x:n['journal'].update(append_reply=()))
    changed_state('falsely-completed-Q-after-source-handling',lambda x:not x[11],lambda n,x:n['core'].update(done=n['core']['done']|2**100))
    changed_state('source-refusal-overwritten',lambda x:x[8].startswith('pub-') and not x[11],lambda n,x:n.update(decision=x[8].split('@')[0]+':ok'))
    changed_state('lost-retired-publication-receipt',lambda x:x[0]=='publication-duplicate-retired' and x[8].startswith('pub-retry@'),lambda n,x:n['core'].update(publication_receipts=()))
    changed_state('changed-source-generation',lambda x:x[8].startswith('source-restart@'),lambda n,x:n['journal'].update(source_generation=d.q.source_token(999)))
    changed_state('altered-actual-Q-response',lambda x:x[11],lambda n,x:n['core'].update(decision='invented:ok'))
    trace=copy.deepcopy(cases[0]['adapter']);trace['events'].pop(0)
    reject('dropped-visible-adapter-event',lambda:restore(trace))
    trace=copy.deepcopy(cases[0]['adapter']);trace['q_profile']['actions']=tuple(reversed(trace['q_profile']['actions']))
    reject('moved-potential-Q-occurrence',lambda:restore(trace))
    positive=next(x for x in samples if x[3]['selected'] and x[4]['core']['selected'] and r.pair_envelope(x[3]['selected'],x[4]['core']['selected'],x[9]))
    _,bs,ba,ns,na,p,u,o,action,pairs,oldpairs,call,row=positive
    damaged=na['core']['selected']._replace(signature='0'*64)
    reject('forged-original-envelope-signature',lambda:d.require(r.pair_envelope(ns['selected'],damaged,pairs),'each original signature validates'))
    early=copy.deepcopy(pairs);early[0]['source_event']=999
    reject('incarnation-pair-before-establishment',lambda:d.require(all(v['source_event']<=row['index'] for v in early),'causal pair availability'))
    append_sample=next(x for x in samples if x[8].startswith('append:') and x[3]['append_reply'])
    bad=copy.deepcopy(append_sample[4]);bad['journal']['append_reply']=()
    reject('mutated-visible-append-response-relation',lambda:d.require(response(append_sample[3],bad,append_sample[8],append_sample[9]),'exact typed append response relation'))
    if packet=='C':
        gap=next(x for x in samples if not x[12]['state_related']);left,right=copy.deepcopy(gap[3]),copy.deepcopy(gap[4]);ledger=gap[9]
        d.require(gap_certificate(left,right,ledger)['identical_valid_unattested_objects'],'retained diagnostic positive witness')
        right['core']['staged']=(right['core']['staged'][0]._replace(generation='changed-object'),right['core']['staged'][1])
        reject('nonidentical-unattested-record-not-certified',lambda:d.require(gap_certificate(left,right,ledger)['identical_valid_unattested_objects'],'actual unbound staged objects must remain identical and valid'))
        left,right=copy.deepcopy(gap[3]),copy.deepcopy(gap[4]);left['staged']=(left['staged'][0]._replace(signature='0'*64),left['staged'][1]);right['core']['staged']=copy.deepcopy(left['staged'])
        reject('identical-forged-unattested-records-not-certified',lambda:d.require(gap_certificate(left,right,ledger)['identical_valid_unattested_objects'],'equal bytes alone do not authenticate either original object'))
        left,right=copy.deepcopy(gap[3]),copy.deepcopy(gap[4]);left['staged']=(left['staged'][0],left['staged'][1]+'-corrupted');right['core']['staged']=copy.deepcopy(left['staged'])
        reject('identical-corrupt-staged-payloads-not-certified',lambda:d.require(gap_certificate(left,right,ledger)['identical_valid_unattested_objects'],'each actual retained staged payload must bind its own envelope'))
    return dict(packet=packet,cases=cases,controls=controls,state_visits_per_representation=visits,state_visit_reservation=MAX_VISITS,
        complete_selected_trace_cases=sum(c['complete_selected_trace_correspondence'] for c in cases),
        selected_visible_responses_matched=sum(x['responses_related'] for c in cases for x in c['rows']),
        selected_journal_poststates_matched=sum(not x['differing_journal_fields'] for c in cases for x in c['rows']),
        strict_state_gap_rows=sum(not x['state_related'] for c in cases for x in c['rows']),
        diagnosed_identical_valid_unattested_gap_rows=sum(x['identical_valid_unattested_objects'] for c in cases for x in c['state_gap_certificates']),
        canonical_traces_are_all_interleavings=False,original_Q_profile_reachability_proved=False,graph_search_performed=False,
        complete_visible_refinement_proved=False,whole_path_composition_proved=False,source_truth_established=False,
        deferred_questions_resolved=[],original_models_changed=False,guard_lineage='Transcribed frozen S guards; own adapter journal and unchanged Q core; bounded contract conformance only.')
