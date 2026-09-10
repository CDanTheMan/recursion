"""Small certificates over retained initialized traces; no additional model steps."""
import copy
import ast
import hashlib
import traces as t
r=t.rel


def states(trace):
    t.verify_trace(trace)
    current=copy.deepcopy(trace['initial']);out=[current]
    for event in trace['events']:
        current=copy.deepcopy(current);current.update(event['patch']);out.append(current)
    return out


def anchor(path,needle):
    raw=(r.ROOT/path).read_bytes();lines=raw.decode().splitlines()
    found=[i+1 for i,line in enumerate(lines) if needle in line]
    r.require(len(found)==1,'unique immutable source guard anchor')
    return {'path':path,'working_sha256':hashlib.sha256(raw).hexdigest(),'line':found[0],'text':lines[found[0]-1]}


def first_response(case):
    row=next((x for x in case['rows'] if x.get('responses_related') is False),None)
    if row is None:return None
    si,ti=row['source_event'],row['target_event']
    se,te=case['source']['events'][si],case['target']['events'][ti]
    r.require(r.exact(row['source_observation'],se['observation']) and r.exact(row['target_observation'],te['observation']),'response certificate bound to both retained events')
    r.require(se['action'].split('@')[0]==te['action'].split('@')[0],'same literal operation for response obstruction')
    r.require(se['observation']['decision']!=te['observation']['decision'],'literal decision inequality independent of any record relation')
    return {'case':case['case'],'source_event':si,'target_event':ti,'source_action':se['action'],'target_action':te['action'],
        'source_before_sha256':se['before_sha256'],'target_before_sha256':te['before_sha256'],
        'source_after_sha256':se['after_sha256'],'target_after_sha256':te['after_sha256'],
        'source_observation':se['observation'],'target_observation':te['observation'],
        'prestate_related':row['prestate_related'],'poststate_related':row['state_related'],
        'conclusion':'These two fixed initialized histories cannot have equal literal decisions under the declared identity action translation, regardless of signed-record relation.'}


def focused(case):
    row=first_response(case);r.require(row is not None,'focused response gap')
    a=states(case['source'])[row['source_event']];b=states(case['target'])[row['target_event']]
    name=case['case'].split('/')[1]
    facts={'source_generation':a['source_generation'],'source_revision':a['source_revision'],'attestation':a['attestation'],
        'staged_source':a['staged_source'],'selected_source':a['selected_source'],'source_paused':a['paused'],'target_paused':b['paused']}
    if name=='append-between-collect-and-publish':
        r.require(a['attestation'] and a['attestation'][1]!=a['source_revision'] and r.exact(a['staged_source'],a['attestation']),'append invalidates staged source revision')
        r.require(row['prestate_related'] and row['source_observation']['decision']=='pub-commit:source-boundary-stale' and row['target_observation']['decision']=='pub-commit:ok','related publication prestate has divergent decision')
        facts['retained_publication_request']=any(e.request==r.q.incoming(a,'pub-commit')[0].request for e,receipt in a['publication_receipts'])
        r.require(not facts['retained_publication_request'],'fresh publication does not take retained receipt exception')
    elif name=='pending-after-selected':
        r.require(a['selected_source'] and a['selected_source'][1]!=a['source_revision'],'new attempt invalidates selected source revision')
        r.require(row['prestate_related'] and row['source_observation']['decision']=='reconcile:source-boundary-stale' and row['target_observation']['decision']=='reconcile:ok','related reconciliation prestate has divergent decision')
    else:
        r.require(name=='publication-source-race' and a['paused'] and b['paused'],'both original histories paused')
        r.require(row['prestate_related'] and row['poststate_related'] and row['source_observation']['decision']=='pub-commit:source-boundary-stale' and row['target_observation']['decision']=='pub-commit:E-PAUSED','matching state endpoints still retain distinct rejections')
        r.require(not a['attestation'] or not r.exact(a['attestation'][:2],(a['source_generation'],a['source_revision'])) or not r.exact(a['staged_source'],a['attestation']),'actual source freshness guard precedes pause check')
        r.require(not any(e.request==r.q.incoming(a,'pub-commit')[0].request for e,receipt in a['publication_receipts']),'no retained request skips source guard')
    return {'response':row,'source_guard_facts':facts,'source_state_sha256':r.digest(a),'target_state_sha256':r.digest(b)}


def lifecycle(case):
    r.require(case['all_paired_transitions_related'],'selected positive lifecycle has no paired transition gap')
    name=case['case'].split('/')[1];a=states(case['source'])[-1];b=states(case['target'])[-1]
    pairs=case['incarnation_pairs']
    r.require(len(pairs)==2 and pairs[0]['reason']=='paired-successful-attestation' and pairs[1]['reason']=='paired-restart','historical and restarted incarnations retained')
    if name=='restart-recollect':
        r.require(a['decision']==b['decision']=='pub-commit:ok' and r.pair_envelope(a['selected'],b['selected'],pairs),'recollected signed publication after restart')
        detail={'selected_source_generation':a['selected'].source_generation,'selected_target_generation':b['selected'].source_generation}
    else:
        r.require(name=='publication-duplicate-retired' and a['decision']==b['decision']=='pub-retry-conflict:E-IDEMPOTENCY-CONFLICT','same visible conflicting retry rejection')
        ar,br=r.reply_row(a),r.reply_row(b)
        r.require(ar and br and r.pair_receipt(*ar,*br,pairs),'duplicate reply binds own historical durable receipt')
        r.require(ar[0].generation in a['retired_cuts'] and br[0].generation in b['retired_cuts'],'duplicate reply references actually retired generation')
        r.require(not any(r.exact(e,ar[0]) for e,raw in a['publication_store']) and not any(r.exact(e,br[0]) for e,raw in b['publication_store']),'historical receipt survives removed publication body')
        retry=next(x for x in case['rows'] if x.get('source_action','').split('@')[0]=='pub-retry')
        r.require(retry['source_observation']['decision']==retry['target_observation']['decision']=='pub-retry:duplicate','preceding retry returns duplicate on both sides')
        retry_facts=[]
        for side,index in (('source',retry['source_event']),('target',retry['target_event'])):
            before,after=states(case[side])[index:index+2]
            r.require(after['publication_reads']==before['publication_reads']+1,'duplicate reads retained receipt exactly once')
            r.require(all(r.exact(before[k],after[k]) for k in ('selected','publication_revision','publication_store','publication_receipts')),'duplicate does not republish or reselect')
            r.require(r.exact(after['publication_reply'],before['publication_receipts'][0][1]) and before['publication_receipts'][0][0].generation in before['retired_cuts'],'duplicate returns first retired durable receipt')
            r.require(case[side]['events'][index+1]['observation']['decision']=='pub-retry-conflict:E-IDEMPOTENCY-CONFLICT','following conflict remains visible')
            retry_facts.append({'side':side,'event':index,'before_sha256':r.digest(before),'after_sha256':r.digest(after),'reads_before':before['publication_reads'],'reads_after':after['publication_reads']})
        detail={'retired_source_generation':ar[0].generation,'retired_target_generation':br[0].generation,'source_reply':ar[1],'target_reply':br[1],
            'own_original_receipt_digests_valid':True,'original_signatures_valid':True,'preceding_duplicate':retry_facts}
    return {'case':case['case'],'matching_transitions':case['counts']['matching_transitions'],
        'unmatched_source_events':case['counts']['unmatched_source_events'],'incarnation_pairs':pairs,'detail':detail,
        'complete_visible_trace_correspondence':False}


def twin_publication(cases,unit):
    clean=next(c for c in cases if c['case']=='canonical/pending-success/'+unit+'/1')
    stale=next(c for c in cases if c['case']=='canonical/append-between-collect-and-publish/'+unit+'/1')
    rows=[next(x for x in c['rows'] if x.get('source_action','').split('@')[0]=='pub-commit') for c in (clean,stale)]
    source=[states(c['source'])[x['source_event']] for c,x in zip((clean,stale),rows)]
    target=[states(c['target'])[x['target_event']] for c,x in zip((clean,stale),rows)]
    r.require(r.exact(target[0],target[1]) and rows[0]['target_action']==rows[1]['target_action'],'identical initialized target prestate and literal action')
    r.require(clean['target']['unit']==stale['target']['unit']==unit and clean['target']['outcome']==stale['target']['outcome']==1,'same unit and outcome')
    indices=[c['target']['schedule']['actions'].index(x['target_action']) for c,x in zip((clean,stale),rows)]
    r.require(indices==[10,10],'same own target action ordinal')
    r.require(all(r.exact(source[0][k],source[1][k]) for k in r.FIELDS),'all common source data equal before publication')
    r.require(source[0]['source_revision']!=source[1]['source_revision'] and r.exact(source[0]['attestation'],source[1]['attestation']),'source revision changed while attestation retained')
    decisions=[x['source_observation']['decision'] for x in rows]
    r.require(decisions==['pub-commit:ok','pub-commit:source-boundary-stale'] and all(x['target_observation']['decision']=='pub-commit:ok' for x in rows),'same target input cannot reproduce both distinct literal source decisions')
    return {'unit':unit,'cases':[clean['case'],stale['case']],
        'source_events':[x['source_event'] for x in rows],'target_events':[x['target_event'] for x in rows],
        'source_prestates_sha256':[r.digest(s) for s in source],'target_prestate_sha256':r.digest(target[0]),
        'target_action':rows[0]['target_action'],'source_revisions':[s['source_revision'] for s in source],
        'target_action_ordinals':indices,'unit_and_outcome_equal':True,'complete_target_profile_dictionaries_claimed_equal':False,
        'source_attestations':[s['attestation'] for s in source],'source_decisions':decisions,
        'target_decisions':[x['target_observation']['decision'] for x in rows],
        'source_only_events_remain_unmatched':True,
        'conclusion':'The retained target prestate and identity publication call contain no distinction for these two source revisions. A record relation alone cannot make this fixed target decision equal both literal source decisions.'}


def publication_schedule_anchor():
    path='experiments/v3/cut-publication/q_inclusive.py';raw=(r.ROOT/path).read_text()
    tree=ast.parse(raw);function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='step')
    branches=[n for n in ast.walk(function) if isinstance(n,ast.If) and ast.unparse(n.test)=="k in ('pub-commit', 'pub-rival', 'pub-retry', 'pub-retry-conflict', 'pub-retry-foreign')"]
    r.require(len(branches)==1,'unique original publication branch')
    body=ast.Module(body=branches[0].body,type_ignores=[])
    r.require(not any(isinstance(n,ast.Name) and n.id in ('p','u','outcome') for n in ast.walk(body)),'publication branch does not read schedule suffix/unit/outcome')
    return {'path':path,'branch_line':branches[0].lineno,'publication_body_sha256':hashlib.sha256(ast.dump(body).encode()).hexdigest(),
        'checked_fact':'Publication branch does not reference p/u/outcome; own done bookkeeping is equal at action ordinal10.',
        'source_backed_argument':'Different unused target profile suffixes do not alter this publication branch. This is a scoped source argument and retained fact check, not arbitrary-program noninterference.'}


def run(raw):
    cases=raw['cases'];responses=[first_response(c) for c in cases];responses=[x for x in responses if x]
    r.require(len(responses)==42,'one first-response obstruction for each negative selected trace')
    focus_names={'append-between-collect-and-publish','pending-after-selected','publication-source-race'}
    focus_cases=[c for c in cases if c['case'].startswith('canonical/') and c['case'].split('/')[1] in focus_names]
    focused_rows=[focused(c) for c in focus_cases];r.require(len(focused_rows)==6,'three guard boundaries in both units')
    positive=[lifecycle(c) for c in cases if c['case'].startswith('canonical/') and c['case'].split('/')[1] in {'restart-recollect','publication-duplicate-retired'}]
    r.require(len(positive)==4,'two selected positive lifecycles in both units')
    controls=[]
    def reject(name,fn):
        try:fn()
        except ValueError as error:controls.append({'control':name,'detected':True,'reason':str(error)})
        else:raise ValueError('undetected focused certificate control: '+name)
    example=focus_cases[0];good=focused(example)
    bad=copy.deepcopy(good);bad['source_guard_facts']['source_revision']=-1
    reject('altered-source-freshness-fact',lambda:r.require(r.exact(bad,focused(example)),'reconstructed source guard certificate'))
    bad_response=copy.deepcopy(responses[0]);bad_response['target_observation']=bad_response['source_observation']
    original=next(c for c in cases if c['case']==bad_response['case'])
    reject('equalized-visible-rejection',lambda:r.require(r.exact(bad_response,first_response(original)),'original unequal decisions remain visible'))
    bad_history=copy.deepcopy(example);i=good['response']['source_event'];bad_history['source']['events'][i]['before_sha256']='0'*64
    reject('guard-certificate-detached-from-prefix',lambda:focused(bad_history))
    twins=[twin_publication(cases,unit) for unit in t.s.UNITS]
    bad_twin=copy.deepcopy(twins[0]);bad_twin['source_decisions']=['pub-commit:ok']*2
    reject('collapsed-twin-publication-outcomes',lambda:r.require(r.exact(bad_twin,twin_publication(cases,t.s.UNITS[0])),'two literal source decisions remain distinct'))
    return {'first_response_obstructions':responses,'focused_guard_certificates':focused_rows,'positive_lifecycle_certificates':positive,
        'twin_publication_certificates':twins,
        'publication_schedule_independence':publication_schedule_anchor(),
        'source_anchors':[anchor('experiments/v3/cut-source-overnight/s_inclusive.py',"mutant != 'publication-source-current'"),
            anchor('experiments/v3/cut-source-overnight/s_inclusive.py',"mutant != 'reconcile-source-current'"),
            anchor('experiments/v3/cut-publication/q_inclusive.py',"elif s['paused']")],
        'additional_model_steps':0,'controls':controls,'unrestricted_refinement_impossibility_proved':False}
