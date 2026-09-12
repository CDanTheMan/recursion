"""Bounded retained-certificate control: obligation o18-publication-current.

Claim audited: inside the boundary-01 scale-eight-action-race suffix (cut
delivery, source-attest, stage, pub-commit, reader lifecycle, reconcile) the
source guard refuses publication with 'source-boundary-stale' BEFORE any Q
validity/parent check runs, Q is never invoked for the refused verbs, the
visible refusal is identical on source and adapter, and the staged candidate
is a fresh current-parent/current-generation envelope. Both spec subclasses
are required witnesses: fresh-incomplete must refuse attestation with
'incomplete-inventory', stale-complete with 'stale-collection'.

Source anchors (frozen inputs, referenced not imported):
  s_domain.py add_with_suffix('scale-eight-action-race') - literal suffix.
  s_inclusive.py / s_audit.py - `pub and not retained/duplicate_id` and
  `reconcile` clauses returning 'source-boundary-stale' without delegation.
  guard_a.py / guard_b.py / guard_audit.py - identical adapter boundary.
  a_audit.py check() - refused call leaves the whole Q core unchanged, adds
  no invocation; stage records staged_source := prior attestation.
  q_audit.py - Q order: stale-parent before foreign-publication and
  stale-source-head; the boundary refusal precedes all of them.
  boundary.py spec constants - re-derived locally here, never imported.
  semantic.py typed/exact/digest - representation helpers only.

Audit accounting: charge.take(1) precedes inspection of each of the 35
prefixes of every applicable case, including every run_controls repetition.
No reducer, guard, audit or boundary function is executed; only retained
fields, event hash links and replayed patch state are examined. 'supported'
is local evidence conformance on the supplied cases, never a global theorem.
"""
import copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel
typed,exact,digest=rel.typed,rel.exact,rel.digest
DEPTH=34
JF=('registration','attempts','append_log','append_receipts','append_reply','source_revision','collection','collected','attestation','staged_source','selected_source','source_generation')
SUFFIX=('cut:success','cut-deliver','source-attest','stage','pub-commit','reader-request:0','reader-pin:0','reader-copy:0','reader-wait:0','reader-release:0','reader-install:0','join-cut','classify','reconcile','admitB')
REFUSED=('source-attest','pub-commit','reconcile')
EXPECT={'stage':'ok','pub-commit':'source-boundary-stale','reconcile':'source-boundary-stale','reader-request:0':'no-selection','reader-pin:0':'no-fresh-request','reader-copy:0':'no-owned-pin','reader-wait:0':'no-owned-pin','reader-release:0':'no-owned-pin','reader-install:0':'no-copy'}
JUST='Same literal call refused by the adapter source guard; refusal remains visible and Q state is unchanged.'

def _subclass(actions):
    return {'collect:0@12':'fresh-incomplete','collect-open@11':'stale-complete'}.get(actions[11]) if len(actions)==DEPTH else None

def _extend(states,trace):
    cur=copy.deepcopy(states[-1])
    for k,v in trace['events'][len(states)-1]['patch'].items():
        if trace['side']=='adapter' and k in ('core','journal'):cur[k].update(copy.deepcopy(v))
        else:cur[k]=copy.deepcopy(v)
    states.append(cur)

def _states(trace):
    out=[copy.deepcopy(trace['initial'])]
    while len(out)<=len(trace['events']):_extend(out,trace)
    return out

def _attest(j,c):
    cap=j['collection']
    if not cap or not c['cut_delivery']:return 'no-captured-source'
    if not exact(cap[:2],(j['source_generation'],j['source_revision'])):return 'stale-collection'
    if tuple(i for i,_ in j['collected'])!=tuple(range(cap[4])):return 'incomplete-inventory'
    return 'registry-or-accept'

def _boundary(j,reconcile):
    g=(j['source_generation'],j['source_revision']);v=j['selected_source' if reconcile else 'attestation']
    return (not v) or not exact(v[:2],g) or (not reconcile and not exact(j['staged_source'],v))

def inspect_cases(cases,charge):
    out={'status':'supported','observations':[],'limitations':[],'audited_prefixes':0};cover=set();seen=0
    def fail(**w):
        out['status']='counterexample';out['observations'].append(dict(violation=True,**w))
    for case in cases:
        name=case.get('case','?') if isinstance(case,dict) else '?'
        try:
            actions=case['source']['actions']
            if len(actions)!=DEPTH or tuple(a.split('@')[0] for a in actions[19:])!=SUFFIX:
                out['limitations'].append(name+': outside scale-eight-action-race suffix');continue
            seen+=1;sub=_subclass(actions)
            if not(len(case['rows'])==len(case['source']['events'])==len(case['adapter']['events'])==DEPTH and len(case['prefixes'])==DEPTH+1):
                fail(case=name,expected='complete retained row/event/prefix inventory',observed='truncated');continue
            ss=[copy.deepcopy(case['source']['initial'])];aa=[copy.deepcopy(case['adapter']['initial'])]
            for i in range(DEPTH+1):
                charge.take(1);out['audited_prefixes']+=1
                if i:
                    _extend(ss,case['source']);_extend(aa,case['adapter'])
                    for side,st in (('source',ss),('adapter',aa)):
                        ev=case[side]['events'][i-1]
                        if digest(st[i-1])!=ev['before_sha256'] or digest(st[i])!=ev['after_sha256']:
                            fail(case=name,prefix=i,side=side,expected='event hash link to replayed typed state',observed=ev['after_sha256'])
                got=[k for k in JF if not exact(ss[i][k],aa[i]['journal'][k])];kept=case['prefixes'][i]
                if kept.get('prefix')!=i or got!=kept.get('differing_journal_fields'):
                    fail(case=name,prefix=i,expected={'journal_divergence':got},observed=kept.get('differing_journal_fields'))
                if got:out['observations'].append(dict(case=name,prefix=i,recomputed_journal_divergence=got))
                if not i:continue
                act=actions[i-1];verb=act.split('@')[0];row=case['rows'][i-1]
                inv=len(aa[i]['invocations'])==len(aa[i-1]['invocations'])+1 and aa[i]['invocations'][-1]==act
                if row.get('index')!=i-1 or row.get('source_action')!=act or row.get('adapter_action')!=act:
                    fail(case=name,prefix=i,expected=act,observed=[row.get('index'),row.get('source_action'),row.get('adapter_action')])
                obs=(row.get('source_observation') or {}).get('decision'),(row.get('adapter_observation') or {}).get('decision')
                if list(obs)!=[ss[i]['decision'],aa[i]['decision']]:fail(case=name,prefix=i,action=verb,expected=[ss[i]['decision'],aa[i]['decision']],observed=list(obs))
                if row.get('q_invoked')!=inv:fail(case=name,prefix=i,action=verb,expected=inv,observed=row.get('q_invoked'))
                if row.get('responses_related')!=(ss[i]['decision']==aa[i]['decision']):fail(case=name,prefix=i,action=verb,expected=ss[i]['decision']==aa[i]['decision'],observed=row.get('responses_related'))
                if verb in REFUSED:
                    if inv:fail(case=name,prefix=i,action=verb,expected='no Q invocation',observed='invoked')
                    if not exact(aa[i]['core'],aa[i-1]['core']):fail(case=name,prefix=i,action=verb,expected='unchanged Q core on guard refusal',observed='core changed')
                    if row.get('justification')!=JUST:fail(case=name,prefix=i,action=verb,expected=JUST,observed=row.get('justification'))
                    if not _boundary(aa[i-1]['journal'],verb=='reconcile') or not _boundary(ss[i-1],verb=='reconcile'):
                        fail(case=name,prefix=i,action=verb,expected='retained boundary predicate',observed='refusal not justified by journal fields')
                want=EXPECT.get(verb)
                if verb=='source-attest':
                    if sub is None:fail(case=name,expected='spec subclass core order',observed=list(actions[11:19]))
                    else:
                        want='incomplete-inventory' if sub=='fresh-incomplete' else 'stale-collection'
                        got_r=_attest(aa[i-1]['journal'],aa[i-1]['core'])
                        if got_r!=want or _attest(ss[i-1],ss[i-1])!=want:fail(case=name,prefix=i,expected=want,observed=got_r)
                        out['observations'].append(dict(case=name,subclass=sub,unit=case.get('unit'),expected=verb+':'+want,observed=ss[i]['decision'],q_invoked=inv))
                if verb=='stage' and not exact(aa[i]['journal']['staged_source'],aa[i-1]['journal']['attestation']):
                    fail(case=name,prefix=i,expected='staged_source := prior attestation',observed=typed(aa[i]['journal']['staged_source']))
                if want is not None and ss[i]['decision']!=verb+':'+want:fail(case=name,prefix=i,action=verb,expected=verb+':'+want,observed=ss[i]['decision'])
                if verb not in REFUSED and not inv:fail(case=name,prefix=i,action=verb,expected='delegated Q invocation',observed='not invoked')
                if verb=='pub-commit':
                    c=aa[i-1]['core'];j=aa[i-1]['journal'];env=c['staged'][0] if c['staged'] else None
                    parent_ok=bool(env) and getattr(env,'expected_revision',None)==c['publication_revision'] and getattr(env,'parent',None)==(c['selected'].generation if c['selected'] else '')
                    gen_ok=bool(env) and exact(getattr(env,'source_generation',None),c['source_generation'])
                    out['observations'].append(dict(case=name,subclass=sub,unit=case.get('unit'),staged=bool(env),envelope_parent_current=parent_ok,envelope_generation_current=gen_ok,attestation_empty=not j['attestation'],boundary_refusal=ss[i]['decision'],q_invoked=inv))
                    if not(env and parent_ok and gen_ok):fail(case=name,prefix=i,expected='fresh current-parent/current-generation staged candidate',observed=typed(c['staged']))
            if sub:cover.add((sub,case.get('unit')))
        except(KeyError,IndexError,TypeError,AttributeError) as e:fail(case=name,expected='complete typed retained case',observed=type(e).__name__)
    subs={s for s,_ in cover}
    if out['status']!='counterexample':
        if not seen:out['status']='not_applicable'
        elif subs!={'fresh-incomplete','stale-complete'}:
            out['status']='unproved';out['limitations'].append('no inspected witness for subclass(es) '+repr(sorted({'fresh-incomplete','stale-complete'}-subs)))
    out['limitations']+=['supplied shard only: conformance covers inspected cases, not all 192 orders per unit',
        'duplicate/retained-request exemption and nonempty stale attestation have no reachable witness in this domain',
        'incomplete-registry tail certified only up to the recomputed inventory clause']
    return out

def run_controls(cases,inspect_cases,charge):
    results=[]
    dom=lambda c:isinstance(c,dict) and len(c['source']['actions'])==DEPTH and tuple(a.split('@')[0] for a in c['source']['actions'][19:])==SUFFIX
    idx=lambda c,v:next(i for i,a in enumerate(c['source']['actions']) if a.split('@')[0]==v)
    def rehash(t):
        st=_states(t)
        for i,e in enumerate(t['events']):e['before_sha256']=digest(st[i]);e['after_sha256']=digest(st[i+1])
    def run(label,case,mutate,reach):
        if case is None:results.append(dict(control=label,ran=False,detected=None,reachability=reach,reason='no reachable base case supplied'));return
        m=copy.deepcopy(case);mutate(m);r=inspect_cases([m],charge)
        results.append(dict(control=label,ran=True,detected=r['status']=='counterexample',reachability=reach,first_violation=next((o for o in r['observations'] if o.get('violation')),None)))
    fresh=next((c for c in cases if dom(c) and _subclass(c['source']['actions'])=='fresh-incomplete'),None)
    stale=next((c for c in cases if dom(c) and _subclass(c['source']['actions'])=='stale-complete'),None)
    anyc=fresh or stale or next((c for c in cases if dom(c)),None)
    for tag,c in (('fresh-incomplete',fresh),('stale-complete',stale)):
        def m(case,v='source-attest'):case['rows'][idx(case,v)]['source_observation']['decision']=v+':ok'
        run('relabelled-'+tag+'-refusal',c,m,'evidence-field tamper; detected by decision/state binding, outer hashes untouched')
    run('false-q-invocation-on-boundary-refusal',anyc,lambda c:c['rows'][idx(c,'pub-commit')].update(q_invoked=True),'original-domain defect class; mask recomputed from invocations')
    def m3(c):c['adapter']['events'][idx(c,'pub-commit')]['patch'].update(decision='pub-commit:ok');rehash(c['adapter'])
    run('erased-boundary-refusal',anyc,m3,'original-domain defect class; hashes preserved so only the semantic expectation detects')
    def m4(c):
        i=idx(c,'stage');j=_states(c['adapter'])[i]['journal'];att=(j['source_generation'],j['source_revision'],'success')
        c['adapter']['events'][i]['patch'].setdefault('journal',{}).update(attestation=att,staged_source=att);rehash(c['adapter'])
    run('phantom-current-attestation',anyc,m4,'unreachable mutation (attestation never succeeds here); detector is refusal-not-justified, not a domain counterexample')
    def m5(c):
        i=idx(c,'stage');e,r=c['adapter']['events'][i]['patch']['core']['staged']
        c['adapter']['events'][i]['patch']['core']['staged']=(e._replace(expected_revision=9),r);rehash(c['adapter'])
    run('stale-parent-staged-envelope',anyc,m5,'unreachable mutation (candidate always stages live revision); exercises fresh/current-parent witness requirement')
    def m6(c):c['adapter']['events'][0]['patch'].setdefault('journal',{})['source_generation']=('cut-source','collectorA','effectA',77);rehash(c['adapter'])
    run('journal-generation-divergence',anyc,m6,'original-domain defect class; prefix journal census recomputed from typed fields')
    run('unrebased-event-patch',anyc,lambda c:c['adapter']['events'][0]['patch'].update(decision='admitA:forged'),'evidence tamper; caught at hash-link layer by design')
    run('dropped-boundary-row',anyc,lambda c:c['rows'].pop(idx(c,'pub-commit')),'evidence tamper; retained row inventory')
    return {'controls':results,'limitations':['controls mutate one case per run; unreachable mutations are labelled and must not be read as original-domain counterexamples',
        'a genuinely reachable nonempty stale-attestation witness does not exist in this domain, so that boundary branch is controlled only through unreachable mutation']}
