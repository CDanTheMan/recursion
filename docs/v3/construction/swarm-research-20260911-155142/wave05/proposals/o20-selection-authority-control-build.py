"""o20 bounded retained-certificate check: selected authority vs staged equality.

Obligation (job o20-selection-authority-control-build). On each restored typed
case object produced by the unchanged eight-hour checker (c.run_history and
c.artifact decode), audit that selected, publication_revision,
publication_store, publication_receipts and the source authority chain
attestation -> staged_source -> selected_source constitute valid selected
authority. Typed equality of a staged object with selected never substitutes
for receipt, store-membership, lineage and provenance proof. No reducer,
guard, relation checker or boundary helper is executed or imported; only
representation helpers of the unchanged semantic source are referenced.

Source anchors (packet inputs): receipt/store/selected contract in
q_audit.py invariant; receipt identity in batch-05/semantic.py own_receipt;
chain updates in s_inclusive.py and s_audit.py (staged_source at stage:ok,
selected_source at commit); adapter journal ledger in a_audit.py; cross-side
field view in adapter_traces.py related; census fields in boundary.py
CENSUS_FIELDS (reference only, never imported).

Finite accounting: charge.take(1) before every inspected prefix of every
call, including control repetitions and witness searches. This module claims
no global theorem, no all-order reachability and no accepted PASS.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel

EXTRA = tuple(rel.s.EXTRA) + ('source_generation',)
SELECTED = ('selected', 'publication_revision', 'publication_store',
            'publication_receipts', 'publication_reply', 'publication_reads')


def _replay(trace):
    """Rebuild prefix states from retained events; verify hash binding."""
    state = copy.deepcopy(trace['initial'])
    states = [state]
    for action, event in zip(trace['actions'], trace['events']):
        if event['action'] != action or rel.digest(state) != event['before_sha256']:
            return states, 'event-prestate-binding'
        state = copy.deepcopy(state)
        for key, patch in event['patch'].items():
            if trace['side'] == 'adapter' and key in ('core', 'journal'):
                state[key].update(patch)
            else:
                state[key] = patch
        if rel.digest(state) != event['after_sha256']:
            return states, 'event-poststate-binding'
        states.append(state)
    if len(states) != len(trace['actions']) + 1:
        return states, 'event-cardinality'
    return states, None


def _view(state, adapter):
    return dict(state['core'], **state['journal']) if adapter else state


def _value_faults(v):
    f = []
    rec, rev = v['publication_receipts'], v['publication_revision']
    if type(rev) is not int or rev != len(rec):
        f.append(('revision-receipt-cardinality', rev, len(rec)))
    try:
        requests = [row[0].request for row in rec]
    except (AttributeError, IndexError, TypeError):
        return f + [('receipt-rows-not-envelope-pairs', rel.typed(rec), '')]
    if len(set(requests)) != len(rec):
        f.append(('duplicate-request-identity', len(set(requests)), len(rec)))
    try:
        previous = ''
        for index, (env, receipt) in enumerate(rec):
            if not rel.own_receipt(env, receipt):
                f.append(('own-receipt-identity', index, rel.digest(receipt)))
            if env.expected_revision != index or env.parent != previous:
                f.append(('exact-parent-lineage', index, rel.digest(receipt)))
            previous = env.generation
    except (AttributeError, IndexError, TypeError, ValueError):
        f.append(('receipt-row-shape', 'envelope-receipt-pair', rel.typed(rec)))
    selected, store = v['selected'], v['publication_store']
    if selected:
        if not rec or not rel.exact(selected, rec[-1][0]):
            f.append(('selected-not-last-receipt', rel.digest(selected), len(rec)))
        if not any(rel.exact(row[0], selected) for row in store):
            f.append(('selected-absent-from-store', rel.digest(selected), len(store)))
        if not rel.signed(selected):
            f.append(('selected-envelope-unsigned', rel.digest(selected), ''))
    if rev > 0 and not v['selected_source']:
        f.append(('committed-without-selected-source', rev, ''))
    for row in store:
        env, raw = row[0], row[1]
        if not rel.signed(env) or not rel.exact(raw, rel.q.raw_cut(env.cut)):
            f.append(('store-payload-invalid', rel.digest(raw), str(getattr(env, 'cut', ''))))
        elif env.generation in v['retired_cuts']:
            f.append(('retired-generation-live', env.generation, ''))
    if v['publication_reply'] and not any(rel.exact(row[1], v['publication_reply']) for row in rec):
        f.append(('reply-without-durable-receipt', rel.digest(v['publication_reply']), ''))
    for key in ('attestation', 'staged_source', 'selected_source'):
        value = v[key]
        if value and not (type(value) is tuple and len(value) == 3 and rel.token(value[0])
                          and type(value[1]) is int and type(value[2]) is str):
            f.append(('authority-token-shape', key, rel.typed(value)))
    return f


def _chain_faults(b, a, action):
    f, verb = [], action.split('@')[0]
    if not rel.exact(b['attestation'], a['attestation']) and verb != 'source-attest':
        f.append(('attestation-without-attest', verb, ''))
    if not rel.exact(b['staged_source'], a['staged_source']):
        if not (verb == 'stage' or verb.startswith('stage-')):
            f.append(('staged-source-without-stage', verb, ''))
        elif a['staged_source'] and not rel.exact(a['staged_source'], b['attestation']):
            f.append(('staged-source-not-attestation', rel.typed(a['staged_source']), rel.typed(b['attestation'])))
    grew = a['publication_revision'] > b['publication_revision']
    if grew and not verb.startswith('pub-'):
        f.append(('revision-grew-off-publication', verb, ''))
    if not rel.exact(b['selected_source'], a['selected_source']):
        if not grew:
            f.append(('selected-source-without-commit', verb, ''))
        elif not rel.exact(a['selected_source'], b['staged_source']):
            f.append(('selected-source-not-staged', rel.typed(a['selected_source']), rel.typed(b['staged_source'])))
    elif grew and not a['selected_source']:
        f.append(('commit-dropped-selected-source', a['publication_revision'], ''))
    return f


def _cross_faults(source, view, pairs):
    faults = [('cross-' + k, 'pair-related', 'unrelated')
              for k in SELECTED if not rel.field_pair(source, k, view, pairs)]
    return faults + [('journal-' + k, rel.typed(source[k]), rel.typed(view[k]))
                     for k in EXTRA if not rel.exact(source[k], view[k])]


def inspect_cases(cases, charge):
    observations, limitations, audited, faults = [], [], 0, 0
    witnesses = {'commit': 0, 'selected_source': 0, 'staged_selected_distinct': 0}
    if not cases:
        return {'status': 'not_applicable', 'observations': [],
                'limitations': ['no cases supplied'], 'audited_prefixes': 0}
    for case in cases:
        try:
            strace, atrace, pairs = case['source'], case['adapter'], case['incarnation_pairs']
        except (KeyError, TypeError):
            limitations.append('case missing trace or pair fields')
            continue
        s_states, s_error = _replay(strace)
        a_states, a_error = _replay(atrace)
        if s_error or a_error:
            faults += 1
            observations.append({'case': case.get('case'), 'prefix': len(s_states) - 1,
                                 'check': 'trace-binding', 'expected': 'digest-chained literal events',
                                 'observed': s_error or a_error})
        for prefix in range(min(len(s_states), len(a_states))):
            charge.take(1)
            audited += 1
            sv, av = s_states[prefix], _view(a_states[prefix], True)
            found = _value_faults(sv) + _value_faults(av) + _cross_faults(sv, av, pairs)
            if prefix:
                action = strace['actions'][prefix - 1]
                found += _chain_faults(s_states[prefix - 1], sv, action)
                found += _chain_faults(_view(a_states[prefix - 1], True), av, action)
            for label, expected, observed in found:
                faults += 1
                observations.append({'case': case.get('case'), 'prefix': prefix, 'check': label,
                                     'expected': expected, 'observed': observed})
            if sv['publication_revision'] > 0 and sv['selected']:
                witnesses['commit'] += 1
            if sv['selected_source']:
                witnesses['selected_source'] += 1
            if sv['selected'] and (not sv['staged'] or not rel.exact(sv['staged'][0], sv['selected'])):
                witnesses['staged_selected_distinct'] += 1
    if faults:
        status = 'counterexample'
    elif not audited:
        status = 'not_applicable'
    elif witnesses['commit'] and witnesses['selected_source']:
        status = 'supported'
        limitations.append('bounded retained evidence only; no reachability or all-order claim')
    else:
        status = 'unproved'
        limitations.append('no inspected prefix holds a committed selection with selected_source')
    limitations.append('witnesses ' + repr(witnesses))
    return {'status': status, 'observations': observations,
            'limitations': limitations, 'audited_prefixes': audited}


def _put(trace, prefix, field, value):
    patch = trace['events'][prefix - 1]['patch']
    if trace['side'] == 'adapter':
        patch.setdefault('journal' if field in EXTRA else 'core', {})[field] = value
    else:
        patch[field] = value


def _rehash(trace):
    """Rewrite the outer digest chain so later detection must be semantic."""
    state = copy.deepcopy(trace['initial'])
    for event in trace['events']:
        event['before_sha256'] = rel.digest(state)
        state = copy.deepcopy(state)
        for key, patch in event['patch'].items():
            if trace['side'] == 'adapter' and key in ('core', 'journal'):
                state[key].update(patch)
            else:
                state[key] = patch
        event['after_sha256'] = rel.digest(state)


def _p_stage(case, ss, aa, i):
    return (i > 0 and ss[i]['staged'] and not ss[i]['selected']
            and ss[i]['decision'] == 'stage:ok' and bool(aa[i]['core']['staged']))


def _p_commit(case, ss, aa, i):
    return (i > 0 and ss[i]['selected']
            and ss[i]['publication_revision'] > ss[i - 1]['publication_revision'])


def _e_staged(case, i, ss, aa):
    _put(case['source'], i, 'selected', ss[i]['staged'][0])
    _put(case['adapter'], i, 'selected', aa[i]['core']['staged'][0])


def _e_receipts(case, i, ss, aa):
    _put(case['source'], i, 'publication_receipts', ())
    _put(case['adapter'], i, 'publication_receipts', ())


def _e_selected_source(case, i, ss, aa):
    bogus = (('cut-source', 'collectorA', 'effectA', 0), 0, 'fabricated-cut')
    _put(case['source'], i, 'selected_source', bogus)
    _put(case['adapter'], i, 'selected_source', bogus)


def _e_skip_staged(case, i, ss, aa):
    for j in range(i, 0, -1):
        if ss[j]['decision'] == 'stage:ok' and ss[j]['staged_source']:
            _put(case['source'], j, 'staged_source', ())
            _put(case['adapter'], j, 'staged_source', ())
            return


def _e_retire(case, i, ss, aa):
    _put(case['source'], i, 'retired_cuts', ss[i]['retired_cuts'] + (ss[i]['selected'].generation,))
    _put(case['adapter'], i, 'retired_cuts',
         aa[i]['core']['retired_cuts'] + (aa[i]['core']['selected'].generation,))


def _e_signature(case, i, ss, aa):
    for trace, view in ((case['source'], ss[i]), (case['adapter'], aa[i]['core'])):
        env, receipt = view['publication_receipts'][-1]
        bad = env._replace(signature='0' * 64)
        _put(trace, i, 'publication_receipts', view['publication_receipts'][:-1]
             + ((bad, (bad.request, rel.digest(bad), receipt[2], receipt[3], receipt[4])),))
        _put(trace, i, 'publication_store',
             tuple((bad, row[1]) if rel.exact(row[0], env) else row for row in view['publication_store']))
        _put(trace, i, 'selected', bad)


def _e_journal(case, i, ss, aa):
    _put(case['adapter'], i, 'selected_source',
         (('cut-source', 'collectorA', 'effectA', 7), 7, 'adapter-only'))


CONTROLS = (
    ('staged-equality-as-selected-authority', 'post-stage prefix, staged set, selected empty', _p_stage, _e_staged),
    ('dropped-receipts-kept-revision', 'commit prefix', _p_commit, _e_receipts),
    ('forged-selected-source-at-commit', 'commit prefix', _p_commit, _e_selected_source),
    ('skipped-staged-source-chain', 'commit prefix with earlier stage:ok', _p_commit, _e_skip_staged),
    ('retired-live-selected-generation', 'commit prefix', _p_commit, _e_retire),
    ('forged-last-receipt-signature', 'commit prefix', _p_commit, _e_signature),
    ('adapter-journal-selected-source-divergence', 'commit prefix', _p_commit, _e_journal),
)


def run_controls(cases, inspect_cases, charge):
    baseline = inspect_cases(list(cases), charge)
    results = []
    for name, need, pred, edit in CONTROLS:
        hit = None
        for index, case in enumerate(cases):
            ss, se = _replay(case['source'])
            aa, ae = _replay(case['adapter'])
            if se or ae:
                continue
            for prefix in range(len(ss)):
                charge.take(1)
                if pred(case, ss, aa, prefix):
                    hit = (index, prefix, ss, aa)
                    break
            if hit:
                break
        if hit is None:
            results.append({'control': name, 'built': False, 'detected': None,
                            'limitation': 'no supplied case exhibits ' + need,
                            'reachable_witness': 'required-not-found'})
            continue
        ci, prefix, ss, aa = hit
        mutant = copy.deepcopy(cases[ci])
        edit(mutant, prefix, ss, aa)
        _rehash(mutant['source'])
        _rehash(mutant['adapter'])
        verdict = inspect_cases([mutant], charge)
        results.append({'control': name, 'case': cases[ci].get('case'), 'prefix': prefix,
                        'built': True, 'detected': verdict['status'] != 'supported',
                        'verdict': verdict['status'],
                        'first_faults': [o['check'] for o in verdict['observations'][:3]],
                        'reachable_witness': 'mutated retained evidence; original-domain reachability unestablished'})
    return {'baseline_status': baseline['status'], 'controls': results}
