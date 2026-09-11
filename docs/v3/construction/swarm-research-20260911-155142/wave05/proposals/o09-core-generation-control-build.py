"""o09-core-generation: bounded retained-evidence controls and checker.

Obligation: actual Q-core ``source_generation`` versus the shadowing adapter
journal ``source_generation`` through the fixed 11-action setup, the 8-action
core antichain (collect-open, collect:0-2, attempt:2-4, source-restart) and
the fixed suffix of original domain ``scale-eight-action-race`` (boundary-01
spec.json; s_domain.py add_with_suffix; boundary.py PREFIX/CORE/SUFFIX=11/8/19
constants, which are never imported or executed here).

Exact audited coupling invariant, evaluated at every hash-bound retained
prefix (states reconstructed only from the case's own patch events; no
reducer, guard, model or boundary function is executed):

  shape  both generations are typed tokens ('cut-source','collectorA',
         'effectA',n) with int n>=0 (semantic.token).
  J      journal == token(Jr), Jr = count of 'source-restart@*' entries in
         the prefix's retained ``invocations`` mask.
  C      core == token(Jr); once 'source-attest:ok' is retained with empty
         prior source_name, core == token(max(Jr,1)).
  E      journal changes only where an event appended a source-restart
         invocation; core only at appended source-restart/source-attest.
  S      journal == restored source-side ``source_generation`` (the source
         attestation path never rewrites the live generation).

Source anchors: a_inclusive.py:10,16; a_split.py:10,16,19; a_audit.py:19,25,29
(independent ledger postcondition); q_inclusive.py:13,20 (core token step and
first-attestation token(1)); q_domain.py:18,20 (source_token, initial
token(0)); semantic.py:103-106 (live-generation comparison view);
guard_a.py/guard_b.py fallthrough delegation makes source-restart an actual
Q call in this domain.

Finite accounting: charge.take(1) BEFORE every inspected prefix, all control
repetitions included; <=len(actions)+1 prefixes per case per call. Semantic
controls mutate actual original fields while preserving outer before/after
hashes, so detection must reach clauses J/C/E/S rather than the evidence
binding; evidence-binding controls are labelled separately so unreachable
mutations are never reported as original-domain counterexamples. Every
control anchors on a genuinely reached prefix of a supplied case; a control
finding no such witness reports reachable_witness=False and stays a
limitation. Boundary-01 attestation always refuses (incomplete-inventory /
stale-collection), so the first-attestation arm of clause C is exercised
only through mutation, never on original states; that gap is reported, not
claimed. Local bounded observation only; no global theorem or acceptance.
"""
import copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel
exact,digest,require=rel.exact,rel.digest,rel.require
NS=('cut-source','collectorA','effectA')

def token(n):return rel.q.source_token(n)
def verb(a):return a.partition('@')[0]
def js(x):
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [js(v) for v in x]
    return x if x is None or isinstance(x,(str,int,bool)) else repr(x)

def apply_patch(state,patch,adapter):
    for k,v in patch.items():
        if adapter and k in('core','journal'):state[k].update(v)
        else:state[k]=v

def restore(trace):
    """Replay retained patch events under hash binding; never a reducer."""
    adapter=trace['side']=='adapter'
    require(len(trace['events'])==len(trace['actions']),'complete retained event inventory')
    cur=copy.deepcopy(trace['initial']);states=[cur]
    for action,event in zip(trace['actions'],trace['events']):
        require(event['action']==action and digest(cur)==event['before_sha256'],'retained action and prestate binding')
        cur=copy.deepcopy(cur);apply_patch(cur,event['patch'],adapter)
        require(digest(cur)==event['after_sha256'],'retained poststate binding')
        states.append(cur)
    return states

def inspect_cases(cases,charge):
    audited=0;obs=[];lim=[];saw_restart=saw_attest=False
    def flag(case,i,clause,expected,observed,kind='semantic-invariant'):
        obs.append(dict(case=case.get('case'),prefix=i,clause=clause,kind=kind,expected=js(expected),observed=js(observed)))
    def done(status):return dict(status=status,observations=obs,limitations=lim,audited_prefixes=audited)
    for case in cases:
        try:at=restore(case['adapter']);st=restore(case['source'])
        except Exception as error:
            flag(case,None,'retained-evidence-binding','hash-bound replay',repr(error),'evidence-binding')
            return done('counterexample')
        attested=False;bad=False
        for i,a in enumerate(at):
            charge.take(1);audited+=1
            jg,cg=a['journal']['source_generation'],a['core']['source_generation']
            restarts=sum(verb(x)=='source-restart' for x in a['invocations'])
            attested=attested or bool(a['core']['source_name'])
            want_c=token(max(restarts,1) if attested else restarts)
            if not(rel.token(jg) and rel.token(cg)):flag(case,i,'generation-token-shape',NS+('int>=0',),(jg,cg));bad=True
            if not exact(jg,token(restarts)):flag(case,i,'journal-restart-shadow',token(restarts),jg);bad=True
            if not exact(cg,want_c):flag(case,i,'core-coupling',want_c,cg);bad=True
            if not exact(st[i]['source_generation'],jg):flag(case,i,'source-journal-shadow',st[i]['source_generation'],jg);bad=True
            if i:
                action=case['adapter']['events'][i-1]['action']
                appended=len(a['invocations'])==len(at[i-1]['invocations'])+1 and a['invocations'][-1]==action
                if not exact(at[i-1]['journal']['source_generation'],jg) and not(appended and verb(action)=='source-restart'):
                    flag(case,i,'journal-cause','change only via invoked source-restart',(action,a['invocations']));bad=True
                if not exact(at[i-1]['core']['source_generation'],cg) and not(appended and verb(action)in('source-restart','source-attest')):
                    flag(case,i,'core-cause','change only via invoked source-restart/source-attest',(action,a['invocations']));bad=True
            saw_restart=saw_restart or restarts>0
            saw_attest=saw_attest or a['decision']=='source-attest:ok'
        if bad:return done('counterexample')
        obs.append(dict(case=case.get('case'),prefixes=len(at),restart_witnessed=saw_restart,
            attestation_decisions=[at[j+1]['decision'] for j,e in enumerate(case['adapter']['events']) if verb(e['action'])=='source-attest']))
    if not audited:return dict(status='not_applicable',observations=obs,limitations=['no case prefixes supplied'],audited_prefixes=0)
    if not saw_restart:lim.append('no source-restart invocation witnessed: restart arm of the coupling unexercised')
    if not saw_attest:lim.append('no source-attest:ok witness: token(1) first-attestation arm unexercised on original states')
    lim.append('inspection replays retained hash-bound patches only; no reducer, guard or boundary execution')
    return done('supported' if saw_restart else 'unproved')

def consistent_mutation(trace,states,prefix,mutate):
    """Mutate one reached prefix while preserving every outer event hash."""
    cur=copy.deepcopy(states[prefix]);mutate(cur)
    if prefix==0:trace['initial']=cur
    else:
        event,previous=trace['events'][prefix-1],states[prefix]
        for k in('core','journal'):
            delta={f:v for f,v in cur[k].items() if not exact(v,previous[k][f])}
            if delta:event['patch'].setdefault(k,{}).update(delta)
        for k in cur:
            if k not in('core','journal') and not exact(cur[k],previous[k]):event['patch'][k]=cur[k]
        event['after_sha256']=digest(cur)
    for event in trace['events'][prefix:]:
        event['before_sha256']=digest(cur);cur=copy.deepcopy(cur)
        apply_patch(cur,event['patch'],True);event['after_sha256']=digest(cur)

def first_gen(states,key,want):return next((i for i,s in enumerate(states) if exact(s[key]['source_generation'],want)),None)
def last_gen(states,key,want):return len(states)-1 if exact(states[-1][key]['source_generation'],want) else None

CONTROLS=[
 ('journal-lags-core-after-restart','semantic',lambda s:last_gen(s,'journal',token(1)),lambda s:s['journal'].update(source_generation=token(0))),
 ('core-regresses-below-journal','semantic',lambda s:last_gen(s,'core',token(1)),lambda s:s['core'].update(source_generation=token(0))),
 ('journal-overtakes-restart-count','semantic',lambda s:last_gen(s,'journal',token(1)),lambda s:s['journal'].update(source_generation=token(2))),
 ('foreign-initial-journal-token','semantic',lambda s:0 if exact(s[0]['journal']['source_generation'],token(0)) else None,lambda s:s['journal'].update(source_generation=('cut-source','collectorB','effectA',1))),
 ('invocation-mask-hides-restart','semantic',lambda s:first_gen(s,'journal',token(1)),lambda s:s.update(invocations=())),
 ('dropped-final-adapter-event','evidence-binding',lambda s:len(s)-1,None)]

def run_controls(cases,inspect_cases,charge):
    results=[]
    base=inspect_cases(list(cases),charge)
    results.append(dict(control='unmutated-retained-evidence',level='baseline',status=base['status'],
        held=base['status']=='supported',audited_prefixes=base['audited_prefixes'],reachable_witness=bool(cases)))
    for name,level,select,mutate in CONTROLS:
        hit=None;available=0
        for case in cases:
            try:states=restore(case['adapter'])
            except Exception:continue
            prefix=select(states)
            if prefix is not None:available+=1;hit=hit or (case,states,prefix)
        if hit is None:
            results.append(dict(control=name,level=level,detected=None,reachable_witness=False,
                limitation='requires a genuinely reached prefix; none in supplied cases'));continue
        case,states,prefix=hit;damaged=copy.deepcopy(case)
        if mutate is None:damaged['adapter']['events'].pop()
        else:consistent_mutation(damaged['adapter'],states,prefix,mutate)
        res=inspect_cases([damaged],charge)
        results.append(dict(control=name,level=level,prefix=prefix,available_witnesses=available,
            detected=res['status']=='counterexample',status=res['status'],witness=res['observations'][:2],
            reachable_witness=level=='semantic'))
    return dict(controls=results,inspection=base)
