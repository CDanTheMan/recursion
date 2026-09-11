"""Bounded retained-certificate check: state-merge cache beyond literal prefixes.

Obligation o32-merge-soundness (parent goal-recursion-v2-execution-fabric).
Strongest defensible bounded claim inspected: exact-key merge determinism --
two inspected prefix states (any case, either side) sharing one canonical typed
digest and extended by the same literal action must carry identical retained
post-state digests, observations and Q-invocation flags. Merge key = original
canonical sha256 over the COMPLETE typed state (no quotienting); the only
permitted mutations are retained hash-bound event patches. No performance,
coverage, all-order or reachability claim is made.

Anchors (unchanged originals; representation use only):
- experiments/v3/eight-hour-research-20260910-01a08a22/check.py: run_history/
  audit_case case shape and Counter charging contract.
- experiments/v3/cut-source-overnight/batch-06/adapter_traces.py: event patch
  semantics, journal relation keys (s.EXTRA + source_generation), row fields.
- experiments/v3/cut-source-overnight/batch-05/semantic.py: typed/digest/exact/
  observation/signed representation.
- experiments/v3/cut-source-overnight/batch-07/identity{,_audit}.py: per-prefix
  relation rows and staged identity-proof fields.

Finite accounting: charge.take(1) precedes every inspected (case,prefix) and
every prefix/event scanned inside controls; repetitions charge again. States
regenerate only from retained initial values and event patches; no reducer or
model execution, no t.restore/audit_case calls, no boundary-helper imports.
Witness-dependent controls (a missing genuinely reachable witness is kept as a
limitation, never silently passed): erased-journal-difference,
false-strict-related, detached-identity-proof-hash, conflicting-merge-transition.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/eight-hour-research-20260910-01a08a22'))
import check as c

d, r, Q = c.d, c.r, c.d.q
JKEYS = tuple(d.s.EXTRA) + ('source_generation',)


class _Abort(Exception):
    pass


def _stage(state, side):
    return state['staged'] if side == 'source' else state['core']['staged']


def _view(adapter):
    return dict(adapter['core'], **{k: adapter['journal'][k] for k in d.s.EXTRA},
                decision=adapter['decision'])


def inspect_cases(cases, charge):
    obs, lim, audited = [], [], 0
    if not isinstance(cases, (list, tuple)):
        return dict(status='not_applicable', observations=[],
                    limitations=['cases is not a sequence'], audited_prefixes=0)
    merge, trans = {}, {}
    for ci, case in enumerate(cases):
        name = case.get('case', ci) if isinstance(case, dict) else ci
        def fail(kind, **w):
            obs.append(dict(falsifier=kind, case=name, **w))
            raise _Abort
        try:
            src, adp = case['source'], case['adapter']
            if not (d.exact(src['actions'], adp['actions']) and d.exact(src['profile'], adp['profile'])):
                fail('source-adapter-trace-mismatch')
            acts, prof = src['actions'], src['profile']
            if not (len(src['events']) == len(adp['events']) == len(case['rows']) == len(acts)
                    and len(case['prefixes']) == len(acts) + 1):
                fail('incomplete-evidence-inventory')
            ss, aa = [copy.deepcopy(src['initial'])], [copy.deepcopy(adp['initial'])]
            pairs, bound = case['incarnation_pairs'], 0
            for i in range(len(acts) + 1):
                charge.take(1)
                audited += 1
                if i:
                    a, row = acts[i - 1], case['rows'][i - 1]
                    for side, tr, seq in (('source', src, ss), ('adapter', adp, aa)):
                        ev = tr['events'][i - 1]
                        if not (ev['action'] == a and set(prof['requires'][a]) <= set(acts[:i - 1])):
                            fail('event-occurrence', prefix=i)
                        if d.digest(seq[-1]) != ev['before_sha256']:
                            fail('prestate-hash', prefix=i)
                        seq.append(copy.deepcopy(seq[-1]))
                        for k, v in ev['patch'].items():
                            if side == 'adapter' and k in ('core', 'journal'):
                                seq[-1][k].update(v)
                            else:
                                seq[-1][k] = v
                        if d.digest(seq[-1]) != ev['after_sha256'] or seq[-1]['done'] != \
                                sum(1 << prof['actions'].index(x) for x in acts[:i]):
                            fail('poststate-hash-or-mask', prefix=i)
                    qp = adp['q_profile']
                    if aa[-1]['core']['done'] != sum(1 << qp['actions'].index(x) for x in aa[-1]['invocations']):
                        fail('q-invocation-mask', prefix=i)
                    if not (row['index'] == i - 1 and row['source_action'] == row['adapter_action'] == a):
                        fail('row-identity', prefix=i)
                    if row['justification'] != d.justification(a, row['q_invoked']):
                        fail('justification', prefix=i)
                    dv = len(aa[-1]['invocations']) - len(aa[-2]['invocations'])
                    if not (dv in (0, 1) and row['q_invoked'] == bool(dv)
                            and (not dv or aa[-1]['invocations'][-1] == a)):
                        fail('q-invocation-flag', prefix=i)
                    sobs, aobs = r.observation(ss[-1], a), r.observation(_view(aa[-1]), a)
                    for side, pre, post, ob, qf in (('s', ss[-2], ss[-1], sobs, None),
                                                    ('a', aa[-2], aa[-1], aobs, row['q_invoked'])):
                        sig = (side, d.digest(pre), a)
                        wit = (d.digest(post), repr(r.typed(ob)), qf)
                        if sig in trans and trans[sig][0] != wit:
                            obs.append(dict(falsifier='merge-unsound-transition', case=name,
                                            prefix=i, action=a, prior=trans[sig][1]))
                        else:
                            trans.setdefault(sig, (wit, (name, i)))
                    if not (d.exact(sobs, row['source_observation'])
                            and d.exact(aobs, row['adapter_observation'])):
                        fail('observation', prefix=i)
                    verb = a.split('@')[0]
                    dec = d.exact(ss[-1]['decision'], aa[-1]['decision'])
                    app = d.exact(ss[-1]['append_reply'], aa[-1]['journal']['append_reply'])
                    exp = dec and app if verb.startswith('append:') or verb == 'append-lose-reply' else dec
                    if row['responses_related'] != exp if not verb.startswith('pub-') \
                            else row['responses_related'] and not dec:
                        fail('response-relation', prefix=i)
                    if row['binding'] == 'new-binding':
                        if bound >= len(pairs) or pairs[bound]['source_event'] != i - 1 \
                                or pairs[bound]['target_event'] != i - 1:
                            fail('ledger-causal-index', prefix=i)
                        bound += 1
                p = case['prefixes'][i]
                jd = [k for k in JKEYS if not d.exact(ss[-1][k], aa[-1]['journal'][k])]
                scd, rule = p['strict_differing_common_fields'], p['staged_rule']
                dcd = [k for k in scd if k != 'staged' or rule != 'original-object-identity']
                ok = (p['differing_journal_fields'] == jd and p['differing_common_fields'] == dcd
                      and p['strict_related'] == (not scd and not jd)
                      and p['related'] == (not dcd and not jd)
                      and (rule == 'strict') == ('staged' not in scd)
                      and p['incarnation_pair_established_by_identity'] is False
                      and p['pairs_sha256'] == d.digest(pairs[:bound]))
                if i:
                    ok = ok and row['differing_journal_fields'] == jd \
                         and row['differing_common_fields'] == scd \
                         and row['state_related'] == p['strict_related'] \
                         and row['prestate_related'] == case['prefixes'][i - 1]['strict_related']
                if not ok:
                    fail('relation-row', prefix=i)
                pr = p['identity_proof']
                if rule == 'original-object-identity':
                    L, R = _stage(ss[-1], 'source'), _stage(aa[-1], 'adapter')
                    if not (type(L) is tuple and type(R) is tuple and len(L) == len(R) == 2
                            and type(L[0]) is Q.Envelope and type(R[0]) is Q.Envelope
                            and d.exact(L, R) and r.signed(L[0]) and r.signed(R[0])
                            and L[1] == Q.raw_cut(L[0].cut) and R[1] == Q.raw_cut(R[0].cut) and pr):
                        fail('identity-objects', prefix=i)
                if pr:
                    fix = (pr['case'] == case['case'] and pr['prefix'] == i
                           and pr['source_prefix_sha256'] == d.digest(src['events'][:i])
                           and pr['adapter_prefix_sha256'] == d.digest(adp['events'][:i])
                           and pr['source_state_sha256'] == d.digest(ss[-1])
                           and pr['adapter_state_sha256'] == d.digest(aa[-1]))
                    for side, tr, seq in (('source', src, ss), ('adapter', adp, aa)):
                        o, e = pr[side + '_origin'], pr[side + '_origin']['event_index']
                        fix = fix and (side, e, o['action']) == (side, pr['source_origin']['event_index'], pr['source_origin']['action']) \
                            and 0 <= e < i and tr['events'][e]['action'] == o['action'] \
                            and o['action'].split('@')[0] == 'stage' \
                            and tr['events'][e]['before_sha256'] == o['before_sha256'] \
                            and tr['events'][e]['after_sha256'] == o['after_sha256'] \
                            and all(d.exact(_stage(seq[j], side), _stage(seq[i], side))
                                    for j in range(e + 1, i + 1))
                    if not fix:
                        fail('identity-proof', prefix=i)
                for side, st in (('source', ss[-1]), ('adapter', aa[-1])):
                    key = (side, d.digest(st))
                    ent = merge.setdefault(key, {'t': repr(r.typed(st)), 'l': set()})
                    if ent['t'] != repr(r.typed(st)):
                        fail('merge-key-collision', prefix=i)
                    ent['l'].add(tuple(acts[:i]))
            if bound != len(pairs):
                fail('ledger-tail')
        except _Abort:
            pass
        except (KeyError, IndexError, TypeError, ValueError, AttributeError) as e:
            obs.append(dict(falsifier='malformed-certificate', case=name, error=repr(e)[:200]))
    shared = sum(1 for e in merge.values() if len(e['l']) > 1)
    obs.append(dict(observation='merge-census', merge_keys=len(merge),
                    cross_prefix_keys=shared, transitions=len(trans), cases=len(cases)))
    if not shared:
        lim.append('no merge key recurs across distinct literal prefixes; cross-prefix '
                   'merge determinism is vacuous on the supplied cases')
    lim += ['pair-mediated envelope equality inside strict common fields is trusted from '
            'retained field lists; only journal/exact/flag premises are re-derived',
            'a history rehashed consistently end-to-end is undetectable here; detection '
            'needs reducer replay or an independent retained witness']
    bad = [o for o in obs if 'falsifier' in o]
    return dict(status='counterexample' if bad else ('supported' if audited else 'unproved'),
                observations=obs, limitations=lim, audited_prefixes=audited)


def run_controls(cases, inspect_cases, charge):
    controls, lim = [], []
    if not cases:
        return dict(baseline_status='unproved', controls=[], undetected=[],
                    limitations=['no cases supplied'])
    base = inspect_cases(cases, charge)

    def scan(pred):
        for cs in cases:
            for i in range(len(cs['source']['actions']) + 1):
                charge.take(1)
                if pred(cs, i):
                    return cs, i
        return None

    def dup():
        seen = {}
        for cs in cases:
            for j, ev in enumerate(cs['source']['events']):
                charge.take(1)
                k = (ev['before_sha256'], ev['action'])
                if k in seen and seen[k] is not cs:
                    return cs, j + 1, seen[k]
                seen.setdefault(k, cs)
        return None

    def control(label, mutate, need=None, mate=False):
        t = need() if need else (cases[0], 1)
        if t is None:
            lim.append(label + ': no genuinely reachable witness in supplied cases')
            return
        bad = copy.deepcopy(t[0])
        mutate(bad, t[1])
        res = inspect_cases([bad] + ([t[2]] if mate else []), charge)
        controls.append(dict(control=label, detected=res['status'] == 'counterexample',
                             status=res['status'], reachable_witness=bool(need),
                             falsifiers=[o['falsifier'] for o in res['observations']
                                         if 'falsifier' in o][:6]))

    control('typed-transport-tuple-loss',
            lambda b, i: b['source'].update(actions=list(b['source']['actions'])))
    control('dropped-visible-event', lambda b, i: b['source']['events'].pop())
    control('changed-action-translation',
            lambda b, i: b['rows'][0].update(justification={'forged': True}))
    control('flipped-q-invocation-flag',
            lambda b, i: b['rows'][0].update(q_invoked=not b['rows'][0]['q_invoked']))
    control('altered-source-observation',
            lambda b, i: b['rows'][0]['source_observation'].update(decision='forged:ok'))
    control('fabricated-ledger-entry', lambda b, i: b['incarnation_pairs'].append(
        dict(source='x', target='y', reason='fabricated', source_event=0, target_event=0)))
    control('erased-journal-difference',
            lambda b, i: b['prefixes'][i].update(differing_journal_fields=[]),
            need=lambda: scan(lambda cs, i: bool(cs['prefixes'][i]['differing_journal_fields'])))
    control('false-strict-related',
            lambda b, i: b['prefixes'][i].update(strict_related=True, related=True),
            need=lambda: scan(lambda cs, i: not cs['prefixes'][i]['strict_related']))
    control('detached-identity-proof-hash',
            lambda b, i: b['prefixes'][i]['identity_proof'].update(source_prefix_sha256='0' * 64),
            need=lambda: scan(lambda cs, i: bool(cs['prefixes'][i]['identity_proof'])))
    control('conflicting-merge-transition',
            lambda b, i: b['rows'][i - 1]['source_observation'].update(decision='forged:ok'),
            need=dup, mate=True)
    return dict(baseline_status=base['status'], baseline_audited=base['audited_prefixes'],
                controls=controls,
                undetected=[x['control'] for x in controls if not x['detected']],
                limitations=lim + base['limitations'])
