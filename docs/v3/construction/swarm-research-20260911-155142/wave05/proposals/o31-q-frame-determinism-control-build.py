"""Bounded retained-certificate check: obligation o31 q-frame-determinism.

Claims inspected on retained 'scale-eight-action-race' cases only:
F frame lemma over fixed setup(11)/core(8)/suffix(15): every adapter step
  that did not invoke Q leaves the typed Q core exactly unchanged; the
  retained invocation list and the Q 'done' mask equal the actual calls;
  every visible decision keeps '<verb>:<reason>', equals the Q core
  decision when invoked, and matches recomputed source/adapter
  observations, justification and causal-binding rows.
D pure Q transition dependence: retained Q-invoked steps are grouped by
  typed(core-before, action, unit, outcome, immutable q_profile); equal
  inputs with different typed core-after/decision are a counterexample.
  done/decision, source_generation and incoming staged content are fields
  of the typed core input, so D covers each named dependence.
Reachability: only evidence reachable under the unchanged original profile
is inspected; mutations that break the retained sha256 event binding are
replay-integrity failures, distinguished from original-domain semantic
counterexamples. charge.take(1) runs before EVERY inspected prefix of
every case, control repetitions included; audited_prefixes is the true
total. Controls needing a genuinely reachable witness:
'q-step-recorded-as-source-handled' needs an actually invoked retained
step; 'altered-visible-refusal' needs a refused visible decision; missing
witnesses are reported, never skipped.
Anchors: boundary-01/spec.json (fixed_prefix_length=11, core_length=8,
fixed_suffix_start=19, units, outcomes); s_domain.py add_with_suffix(
'scale-eight-action-race') + sequence() requires; batch-06/a_domain.py
source_only/subprofile/justification; batch-06/a_audit.py check frame
clause; batch-05/semantic.py advance/observation/typed/exact;
eight-hour-research-20260910-01a08a22/check.py restore/audit_case shape;
q_domain.py EXTRA + staged Envelope. No reducer, guard or boundary.py
function is imported or executed; no new model execution; 'supported' is
bounded retained evidence only, never acceptance.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/v3/eight-hour-research-20260910-01a08a22'))
import check as c

d, t, r = c.d, c.t, c.r
J = c.artifact.encode
PREFIX, SUFFIX, DEPTH = 11, 19, 34
UNITS, OUTCOME = ('event', 'utf8-byte'), 1
EXC = (ValueError, KeyError, IndexError, TypeError, AttributeError)


def _shape(case):
    """Fixed setup/core/suffix schedule shape; (profile, schedule) or None."""
    try:
        p, a = case['adapter']['profile'], tuple(case['source']['actions'])
        ok = (len(p['actions']) == DEPTH == len(a) and len(set(p['actions'])) == DEPTH
              and a == tuple(case['adapter']['actions']) and a[:PREFIX] == p['actions'][:PREFIX]
              and a[SUFFIX:] == p['actions'][SUFFIX:]
              and sorted(a[PREFIX:SUFFIX]) == sorted(p['actions'][PREFIX:SUFFIX]))
        return (p, a) if ok else None
    except EXC:
        return None


def _graph(p):
    """Independent reconstruction of the fixed setup/core/suffix requires."""
    for i, a in enumerate(p['actions']):
        want = ((p['actions'][PREFIX - 1],) if PREFIX <= i < SUFFIX else
                p['actions'][PREFIX:SUFFIX] if i == SUFFIX else
                () if i == 0 else (p['actions'][i - 1],))
        if set(p['requires'].get(a, ())) != set(want):
            return False
    return True


def inspect_cases(cases, charge):
    obs, lim, audited = [], [], 0
    fail = lambda name, **w: obs.append(dict(falsified=name, **w))
    if type(cases) is not list or not cases:
        return dict(status='not_applicable', observations=[],
                    limitations=['no typed case objects supplied'], audited_prefixes=0)
    groups, skipped, pdig = {}, 0, None
    for case in cases:
        label, shaped = (case.get('case'), _shape(case)) if type(case) is dict else ('non-dict', None)
        if shaped is None:
            skipped += 1
            continue
        p, sched = shaped
        if pdig is None:
            pdig = d.digest(p)
        if not _graph(p) or d.digest(p) != pdig or not d.exact(p, case['source']['profile']):
            fail('immutable-profile', case=label, observed='altered retained profile',
                 expected='fixed requires graph + single profile identity')
            continue
        if case.get('unit') not in UNITS or case.get('outcome') != OUTCOME:
            fail('domain-identity', case=label, expected=J([UNITS, OUTCOME]),
                 observed=J([case.get('unit'), case.get('outcome')]))
            continue
        try:
            ss, aa = t.restore(case['source']), t.restore(case['adapter'])
            rows, prefixes = case['rows'], case['prefixes']
            xpairs, qp = case['incarnation_pairs'], d.subprofile(p)
        except EXC as e:
            fail('replay-integrity', case=label, observed=type(e).__name__,
                 expected='sha256 event binding + row/prefix/pair sections')
            continue
        if not (len(rows) == DEPTH and len(prefixes) == len(aa) == DEPTH + 1):
            fail('finite-audit-accounting', case=label, expected=J([DEPTH, DEPTH + 1]),
                 observed=J([len(rows), len(prefixes), len(aa)]))
            continue
        pairs = []
        for i in range(len(aa)):
            charge.take(1)
            audited += 1
            try:
                st, called = aa[i], aa[i]['invocations']
                if (len(set(called)) != len(called) or not set(called) <= set(sched[:i])
                        or not all(x in qp['actions'] for x in called)
                        or st['core']['done'] != sum(1 << qp['actions'].index(x) for x in called)):
                    fail('q-completion-mask', case=label, prefix=i,
                         expected='unique scheduled invocations matching Q done mask',
                         observed=J([called, st['core']['done']]))
                if i == 0:
                    continue
                a, before, row = sched[i - 1], aa[i - 1], rows[i - 1]
                invoked = called != before['invocations']
                okcall = not invoked or (len(called) == len(before['invocations']) + 1
                                         and called[:-1] == before['invocations'] and called[-1] == a)
                k = a.split('@')[0]
                binding = r.advance(pairs, ss[i - 1], t.core_view(before), ss[i],
                                    t.core_view(st), a, a, i - 1, i - 1)
                if (row['index'] != i - 1 or row['source_action'] != a or row['adapter_action'] != a
                        or bool(row['q_invoked']) != invoked or not okcall or binding != row.get('binding')
                        or row['justification'] != d.justification(a, invoked)
                        or not st['decision'].startswith(k + ':')
                        or (invoked and st['decision'] != st['core']['decision'])):
                    fail('transition-record', case=label, prefix=i, expected=J([i - 1, a, invoked, k]),
                         observed=J([row['index'], row['source_action'], row['q_invoked'], st['decision']]))
                if not invoked and not d.exact(before['core'], st['core']):
                    fail('frame', case=label, prefix=i, expected='unchanged typed Q core on non-invoked step',
                         observed=[f for f in st['core'] if not d.exact(before['core'][f], st['core'][f])])
                obs_a = r.observation(t.core_view(st), a)
                if not d.exact(obs_a, row['adapter_observation']) or not d.exact(r.observation(ss[i], a), row['source_observation']):
                    fail('visible-observation', case=label, prefix=i, expected=J(obs_a), observed=J(row['adapter_observation']))
                if invoked:
                    key = d.digest([J(before['core']), a, case['unit'], case['outcome'], d.digest(qp)])
                    g = groups.get(key)
                    if g is None:
                        groups[key] = dict(after=st['core'], dec=st['decision'], where=[[label, i]])
                    elif not d.exact(g['after'], st['core']) or g['dec'] != st['decision']:
                        diff = [f for f in st['core'] if not d.exact(g['after'].get(f), st['core'][f])]
                        fail('pure-q-dependence', input_sha256=key, expected=dict(first=g['where'][0],
                             after_sha256=d.digest(g['after']), decision=g['dec']),
                             observed=dict(second=[label, i], after_sha256=d.digest(st['core']),
                             differing_output_fields=diff + (['outer-decision'] if g['dec'] != st['decision'] else [])))
                    else:
                        g['where'].append([label, i])
            except EXC as e:
                fail('prefix-evidence', case=label, prefix=i,
                     expected='inspectable typed prefix', observed=type(e).__name__)
        if not d.exact(pairs, xpairs):
            fail('incarnation-ledger', case=label, expected=J(pairs), observed=J(xpairs))
    falsified = [o for o in obs if 'falsified' in o]
    q_steps = sum(len(g['where']) for g in groups.values())
    repeated = sum(1 for g in groups.values() if len(g['where']) > 1)
    if skipped:
        lim.append('%d case(s) outside fixed setup/core/suffix shape; not inspected' % skipped)
    if falsified:
        status = 'counterexample'
    elif audited == 0:
        status = 'not_applicable'
    elif q_steps == 0:
        status, note = 'unproved', 'no retained Q-invoked transition inspected; pure-dependence untested'
    elif repeated == 0:
        status, note = 'unproved', 'no two inspected Q steps share one typed input; determinism only vacuous'
    else:
        status, note = 'supported', None
    if 'note' in dir() and note:
        lim.append(note)
    lim.append('bounded retained evidence only; no global theorem, reachability or acceptance claim')
    obs.append(dict(audit_summary=dict(cases=len(cases), q_steps=q_steps, repeated_input_groups=repeated)))
    return dict(status=status, observations=obs, limitations=lim, audited_prefixes=audited)


def run_controls(cases, inspect_cases, charge):
    """Observed adversarial controls on real supplied typed cases. Semantic
    controls mutate only derived non-sha-bound sections so detection reaches
    the semantic checks; the replay-integrity control is an unreachable
    mutation, not an original-domain counterexample."""
    base = inspect_cases(list(cases), charge)
    def first(pred):
        for case in cases:
            if _shape(case) is None:
                continue
            for i, row in enumerate(case.get('rows') or []):
                try:
                    if pred(case, i, row):
                        return case, i
                except EXC:
                    pass
        return None, -1
    def apply(name, layer, witness, mutate):
        case, i = witness
        if case is None:
            return dict(control=name, layer=layer, status='unwitnessed', detected=None,
                        limitation='no supplied case carries a genuinely reachable witness')
        bad = copy.deepcopy(case)
        mutate(bad, i)
        res = inspect_cases([bad], charge)
        return dict(control=name, layer=layer, reachable_domain=layer == 'semantic',
                    expected='counterexample', observed=res['status'],
                    detected=res['status'] == 'counterexample',
                    witness=dict(case=case.get('case'), row=i),
                    falsified=[o for o in res['observations'] if 'falsified' in o])
    tok = ('cut-source', 'collectorA', 'effectA', 0)
    spec = [('q-step-recorded-as-source-handled', 'semantic',
             lambda c_, i, row: bool(row['q_invoked']), lambda b, i: b['rows'][i].update(q_invoked=False)),
            ('source-handled-recorded-as-q-step', 'semantic',
             lambda c_, i, row: not row['q_invoked'], lambda b, i: b['rows'][i].update(q_invoked=True)),
            ('altered-visible-refusal', 'semantic',
             lambda c_, i, row: not row['adapter_observation']['decision'].endswith(':ok'),
             lambda b, i: b['rows'][i]['adapter_observation'].update(
                 decision=b['source']['actions'][i].split('@')[0] + ':forged')),
            ('relabeled-unit', 'semantic', lambda c_, i, row: True, lambda b, i: b.update(unit='x')),
            ('weakened-immutable-profile-requires', 'semantic', lambda c_, i, row: True,
             lambda b, i: (b['adapter']['profile']['requires'].update({b['adapter']['profile']['actions'][PREFIX]: ()}),
                           b['source']['profile']['requires'].update({b['source']['profile']['actions'][PREFIX]: ()}))),
            ('injected-incarnation-binding', 'semantic', lambda c_, i, row: True,
             lambda b, i: b.update(incarnation_pairs=[dict(source=tok, target=tok, reason='injected',
                                                         source_event=0, target_event=0)])),
            ('dropped-prefix-certificate', 'semantic', lambda c_, i, row: True, lambda b, i: b['prefixes'].pop()),
            ('corrupted-hash-bound-state', 'replay-integrity', lambda c_, i, row: True,
             lambda b, i: b['source']['initial'].update(decision='forged'))]
    controls = [apply(n, layer, first(pred), mut) for n, layer, pred, mut in spec]
    missing = [x['control'] for x in controls if x.get('status') == 'unwitnessed']
    lim = ['corrupted-hash-bound-state mutates sha256-bound retained state; detection is '
           'replay-integrity, not an original-domain semantic counterexample']
    if missing:
        lim.append('controls lacking a reachable witness in supplied cases: ' + ','.join(missing))
    return dict(status='controls-observed', controls=controls, limitations=lim,
                baseline=dict(status=base['status'], audited_prefixes=base['audited_prefixes']),
                all_detected=all(x['detected'] for x in controls))
