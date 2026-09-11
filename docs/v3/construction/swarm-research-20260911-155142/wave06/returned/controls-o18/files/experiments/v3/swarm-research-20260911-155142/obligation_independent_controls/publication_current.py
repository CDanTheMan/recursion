"""Independent adversarial controls for obligation o18-publication-current.

Scope: boundary-01 'scale-eight-action-race' retained cases (34 literal
actions: fixed 11-action prefix, 8-action antichain core, fixed suffix at
index 19). run_controls(cases, inspect_cases, charge) deep-copies supplied
cases, applies typed-schema-preserving mutations and re-audits each mutant
through the supplied inspect_cases. No reducer, guard, audit or boundary
function is executed here; only retained fields, event digests and replayed
patch state are examined.

Detection is reported, never asserted: 'detected' is True exactly when the
independent audit returned status 'counterexample'; every other status is
recorded verbatim. A control caught only by the event-digest layer is
labelled 'event-digest' and is never presented as semantic discrimination.

Precharge: every control takes 2*(DEPTH+1) charge before any work - one
reservation for the mutation replay (patch replay plus rehash over the 35
prefixes) and one for the audit replay that inspect_cases then meters per
prefix on top. A refused take is recorded as 'precharge refused'; no
partially charged replay, mutation or repeat is ever reported as a run.

Witness binding: controls with base_witness 'fresh-incomplete' or
'stale-complete' require a reachable original case whose core order
satisfies the full boundary.py PATTERNS membership re-derived in _member;
the wave05 one-action subclass heuristic is not reused, so a non-member
middle can never seed a witness control. Mutations labelled
'unreachable-mutation' or 'fabricated-order' probe states no retained
history reaches: they falsify certificate integrity, not original-domain
claims.

Source anchors (frozen inputs, referenced not imported):
  s_inclusive.py / s_audit.py - 'source-boundary-stale' publication and
    reconcile clauses plus the source-attest capture clauses.
  guard_a.py / guard_b.py / guard_audit.py - identical adapter boundary.
  a_audit.py - refused call leaves the whole Q core unchanged, adds no
    invocation; stage copies attestation into staged_source.
  boundary.py - PREFIX/CORE/SUFFIX/DEPTH and PATTERNS membership.
  semantic.py - exact/digest representation helpers only.
"""
import copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel
exact,digest=rel.exact,rel.digest
DEPTH,PREFIX,SUFFIX=34,11,19
CHARGE=2*(DEPTH+1)
COLLECTS=('collect:0@12','collect:1@13','collect:2@14')
OPEN,RESTART='collect-open@11','source-restart@18'
ATTEMPTS=('attempt:2@15','attempt:3@16','attempt:4@17')
CORESET=frozenset((*COLLECTS,OPEN,RESTART,*ATTEMPTS))
FREE,TAIL2,ALL3=frozenset((*ATTEMPTS,RESTART)),frozenset(COLLECTS[1:]),frozenset(COLLECTS)
PATTERNS={'fresh-incomplete':(COLLECTS[0],FREE,FREE,FREE,FREE,OPEN,TAIL2,TAIL2),
 'stale-complete':(OPEN,FREE,FREE,FREE,FREE,ALL3,ALL3,ALL3)}
SUFFIX_VERBS=('cut:success','cut-deliver','source-attest','stage','pub-commit',
 'reader-request:0','reader-pin:0','reader-copy:0','reader-wait:0','reader-release:0',
 'reader-install:0','join-cut','classify','reconcile','admitB')
REFUSED=('source-attest','pub-commit','reconcile')
REORDER=(0,1,5,2,3,4,6,7)

def _jsafe(x):
    if isinstance(x,dict):return {str(k):_jsafe(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [_jsafe(v) for v in x]
    if isinstance(x,(str,int,float,bool)) or x is None:return x
    return repr(x)

def _dom(c):
    try:
        a=c['source']['actions']
        return len(a)==DEPTH and tuple(x.split('@')[0] for x in a[SUFFIX:])==SUFFIX_VERBS
    except(KeyError,TypeError,IndexError,AttributeError):return False

def _member(c):
    mid=tuple(c['source']['actions'][PREFIX:SUFFIX])
    if len(mid)!=SUFFIX-PREFIX or set(mid)!=CORESET:return None
    for name,pat in PATTERNS.items():
        used=set()
        for want,got in zip(pat,mid):
            if type(want) is str:
                if got!=want:break
            elif got in want and got not in used:used.add(got)
            else:break
        else:return name
    return None

def _idx(c,v):return next(i for i,a in enumerate(c['source']['actions']) if a.split('@')[0]==v)
def _row(c,v):return c['rows'][_idx(c,v)]

def _states(t):
    out=[copy.deepcopy(t['initial'])]
    for e in t['events']:
        cur=copy.deepcopy(out[-1])
        for k,v in e['patch'].items():
            if t['side']=='adapter' and k in('core','journal'):cur[k].update(copy.deepcopy(v))
            else:cur[k]=copy.deepcopy(v)
        out.append(cur)
    return out

def _rehash(t):
    st=_states(t)
    for i,e in enumerate(t['events']):
        e['before_sha256'],e['after_sha256']=digest(st[i]),digest(st[i+1])

def m_relabel(c,verbs):
    for v in verbs:
        row=_row(c,v)
        row['source_observation']['decision']=v+':ok';row['adapter_observation']['decision']=v+':ok'

def m_false_q(c):
    for v in REFUSED:_row(c,v)['q_invoked']=True

def m_erase(c):
    for v in REFUSED:
        i=_idx(c,v)
        c['source']['events'][i]['patch']['decision']=v+':ok'
        c['adapter']['events'][i]['patch']['decision']=v+':ok'
    _rehash(c['source']);_rehash(c['adapter'])

def m_phantom(c):
    i=_idx(c,'stage');st=_states(c['adapter'])[i]
    att=(st['journal']['source_generation'],st['journal']['source_revision'],st['core']['cut_delivery'] or 'success')
    c['adapter']['events'][i]['patch'].setdefault('journal',{}).update(attestation=att,staged_source=att)
    c['source']['events'][i]['patch'].update(attestation=att,staged_source=att)
    _rehash(c['source']);_rehash(c['adapter'])

def m_stale_parent(c):
    i=_idx(c,'stage');env,raw=_states(c['adapter'])[i+1]['core']['staged']
    bad=(env._replace(expected_revision=env.expected_revision+9),raw)
    c['adapter']['events'][i]['patch'].setdefault('core',{})['staged']=bad
    c['source']['events'][i]['patch']['staged']=bad
    _rehash(c['source']);_rehash(c['adapter'])

def m_journal_gen(c):
    c['adapter']['events'][0]['patch'].setdefault('journal',{})['source_generation']=('cut-source','collectorA','effectA',77)
    _rehash(c['adapter'])

def m_core_gen(c):
    c['adapter']['events'][_idx(c,'pub-commit')]['patch'].setdefault('core',{})['source_generation']=('cut-source','collectorA','effectA',88)
    _rehash(c['adapter'])

def m_unrebased(c):
    c['adapter']['events'][_idx(c,'pub-commit')]['patch']['decision']='pub-commit:foreign-rewrite'

def m_drop_row(c):
    c['rows'].pop(_idx(c,'pub-commit'))

def m_reorder(c):
    for t in(c['source'],c['adapter']):
        mid=list(t['actions'][PREFIX:SUFFIX]);ev=t['events'][PREFIX:SUFFIX]
        t['actions']=tuple(t['actions'][:PREFIX])+tuple(mid[i] for i in REORDER)+tuple(t['actions'][SUFFIX:])
        t['events']=t['events'][:PREFIX]+[ev[i] for i in REORDER]+t['events'][SUFFIX:]
        _rehash(t)
    mid=c['rows'][PREFIX:SUFFIX]
    c['rows']=c['rows'][:PREFIX]+[mid[i] for i in REORDER]+c['rows'][SUFFIX:]
    for i,row in enumerate(c['rows']):row['index']=i

def run_controls(cases,inspect_cases,charge):
    results=[]
    def pick(want):
        for c in cases:
            if not _dom(c):continue
            m=_member(c)
            if m is not None and(want is None or m==want):return c
    def run(label,want,mutate,reach,layer,expect):
        base=pick(want)
        e=dict(control=label,base_witness=want or 'any subclass member',
               case=(base or {}).get('case'),reachability=reach,detection_layer=layer,
               expectation=expect,ran=False,detected=None)
        results.append(e)
        if base is None:e['reason']='no reachable original witness case supplied';return
        try:charge.take(CHARGE)
        except Exception as x:e['reason']='full precharge refused before replay/mutation: '+type(x).__name__;return
        m=copy.deepcopy(base)
        try:mutate(m)
        except Exception as x:e['reason']='mutation failed: '+type(x).__name__;return
        try:r=inspect_cases([m],charge)
        except Exception as x:e.update(ran=True,reason='audit raised '+type(x).__name__);return
        if not isinstance(r,dict):e.update(ran=True,reason='non-dict audit result');return
        e.update(ran=True,status=r.get('status'),detected=r.get('status')=='counterexample',
                 audited_prefixes=r.get('audited_prefixes'),
                 first_violation=_jsafe(next((o for o in r.get('observations',[])
                     if isinstance(o,dict) and(o.get('violation') or o.get('mismatches')),None))))
    run('unmodified-witness-reaudit',None,lambda c:None,'original-reachable',
        'none: baseline sanity, detected must stay False','supported or unproved, never counterexample')
    run('relabelled-fresh-incomplete-attestation','fresh-incomplete',lambda c:m_relabel(c,('source-attest',)),
        'original-reachable','recorded decision vs replayed state and subclass attestation expectation','counterexample')
    run('relabelled-stale-complete-attestation','stale-complete',lambda c:m_relabel(c,('source-attest',)),
        'original-reachable','recorded decision vs replayed state and subclass attestation expectation','counterexample')
    run('relabelled-publication-reconcile-refusals',None,lambda c:m_relabel(c,('pub-commit','reconcile')),
        'original-reachable','recorded decision vs replayed state and boundary expectation','counterexample')
    run('false-q-invocation-on-refused-verbs',None,m_false_q,'original-reachable',
        'q_invoked flag vs actual invocation list and Q completion mask','counterexample')
    run('erased-boundary-refusals-rehashed',None,m_erase,'original-reachable',
        'semantic refusal expectation vs replayed decision; event digests stay consistent','counterexample')
    run('changed-q-core-generation-on-refusal',None,m_core_gen,'original-reachable',
        'unchanged-Q-core invariant on a guard-refused call','counterexample')
    run('phantom-current-attestation',None,m_phantom,
        'unreachable-mutation: no retained history here accepts an attestation',
        'ledger postcondition at the stage prefix (attestation written without an accepted attest call); the pub boundary-justification layer is secondary','counterexample')
    run('stale-parent-staged-envelope',None,m_stale_parent,
        'unreachable-mutation: stage always emits the live revision',
        'fresh current-parent/current-generation envelope assertion; detected=False marks that half of the claim unexercised','counterexample only if envelope currency is asserted')
    run('journal-generation-divergence',None,m_journal_gen,'original-reachable',
        'per-prefix journal certificate and ledger generation field','counterexample')
    run('unrebased-event-patch',None,m_unrebased,'original-reachable',
        'event-digest link only: integrity evidence, never semantic discrimination','counterexample at the hash layer')
    run('dropped-boundary-row',None,m_drop_row,'original-reachable',
        'retained row inventory vs literal action inventory','counterexample')
    run('reordered-core-nonmember','fresh-incomplete',m_reorder,
        'fabricated-order: dependency-safe core permutation, not an original history',
        'order/certificate binding: action inventory, journal certificate or per-verb expectation','counterexample')
    return{'controls':results,'limitations':[
        'each run mutates one supplied case; witness controls run only when a full-PATTERNS member is supplied, otherwise recorded not-run',
        'unreachable-mutation and fabricated-order controls falsify retained-certificate integrity only; they are never original-domain counterexamples',
        'the event-digest control detects at the hash-link layer by design and is not evidence of semantic discrimination',
        'no reachable history in this domain has a successful attestation or a durable publication receipt, so the retained/duplicate exemption and nonempty stale-attestation branches admit no witness-based control',
        'every run precharges 2*(DEPTH+1) before its mutation replay and before the audit per-prefix takes; charge exhaustion is reported, never hidden',
        'detected reports the supplied audit verdict verbatim; detected=False on stale-parent-staged-envelope marks the fresh-envelope assertion unexercised, not the mutation valid']}
