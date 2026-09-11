"""Bounded retained-evidence controls, obligation o13-outer-response.

Per retained adapter prefix: the outer decision equals the actual retained
Q-core decision on invoked calls; refused or source-handled calls leave the
entire core unchanged; append_reply, publication_reply and the visible
refusal reason are preserved exactly. Local bounded result only.

inspect_cases(cases, charge): cases are typed original c.run_history objects
restored via c.artifact (initial state + hash-bound patches). charge.take(1)
precedes every inspected prefix; repetitions count. No reducer, guard, audit
or boundary helper executes; replay applies recorded patches only. typed,
exact and digest are unchanged batch-05 semantic representations.

run_controls(cases, inspect_cases, charge): deepcopy-mutates real supplied
cases, re-binding outer before/after and row adapter hashes so detection
reaches semantics. Controls needing a genuinely reachable witness (invoked
call, refused call, retained append/publication reply) record a
missing-witness limitation, not detection, when no sample qualifies.

Anchors: batch-05 semantic observation/field_pair; batch-06 a_audit.check;
adapter_traces response/trace_event/restore; check.py run_history/audit_case.
"""
import copy, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel

ROW_KEYS = ('source_action', 'adapter_observation', 'q_invoked')

def replay(trace):
    states = [copy.deepcopy(trace['initial'])]
    for event in trace['events']:
        nxt = copy.deepcopy(states[-1])
        for key, value in event['patch'].items():
            if trace['side'] == 'adapter' and key in ('core', 'journal'):
                nxt[key].update(value)
            else:
                nxt[key] = value
        states.append(nxt)
    return states

def witness(case, prefix, control, expected, observed):
    return {'case': case.get('case'), 'prefix': prefix, 'control': control,
            'expected': rel.typed(expected), 'observed': rel.typed(observed)}

def inspect_cases(cases, charge):
    bad, kept, audited = [], [], 0
    seen = dict.fromkeys(('invoked', 'refused', 'append_reply', 'publication_reply'), 0)
    if not cases:
        return {'status': 'not_applicable', 'observations': [], 'limitations': ['no cases'], 'audited_prefixes': 0}
    for case in cases:
        try:
            src, adp, rows = replay(case['source']), replay(case['adapter']), case['rows']
            assert len(src) == len(adp) == len(case['prefixes']) == len(rows) + 1
            assert len(case['source']['events']) == len(case['adapter']['events']) == len(rows)
        except (KeyError, TypeError, ValueError, IndexError, AssertionError) as error:
            bad.append({'case': case.get('case') if isinstance(case, dict) else None, 'prefix': -1,
                        'control': 'malformed-retained-case', 'expected': 'typed case', 'observed': repr(error)})
            continue
        for i in range(len(rows) + 1):
            charge.take(1)
            audited += 1
            if i == 0:
                continue
            row = rows[i - 1]
            if not isinstance(row, dict) or any(k not in row for k in ROW_KEYS) or not \
                    isinstance(row['source_action'], str) or not isinstance(row['adapter_observation'], dict):
                bad.append(witness(case, i, 'malformed-row', list(ROW_KEYS), sorted(row)))
                continue
            verb = row['source_action'].split('@')[0]
            sides = (('source', src, case['source']['events'][i - 1]), ('adapter', adp, case['adapter']['events'][i - 1]))
            unbound = [s for s, st, ev in sides
                       if (rel.digest(st[i - 1]), rel.digest(st[i])) != (ev['before_sha256'], ev['after_sha256'])]
            if unbound:
                bad.append(witness(case, i, 'trace-hash-binding', 'sha256-bound', unbound))
                continue
            aobs = row['adapter_observation']
            if not rel.exact(adp[i]['decision'], aobs.get('decision')):
                bad.append(witness(case, i, 'outer-decision-field', aobs.get('decision'), adp[i]['decision']))
            if not rel.exact(adp[i]['decision'], src[i]['decision']):
                bad.append(witness(case, i, 'visible-response-equality', src[i]['decision'], adp[i]['decision']))
            if row['q_invoked']:
                seen['invoked'] += 1
                if not rel.exact(adp[i]['decision'], adp[i]['core']['decision']):
                    bad.append(witness(case, i, 'outer-vs-retained-core', adp[i]['core']['decision'], adp[i]['decision']))
            else:
                seen['refused'] += adp[i]['decision'] != verb + ':ok'
                if not rel.exact(adp[i]['core'], adp[i - 1]['core']):
                    bad.append(witness(case, i, 'noninvoked-core-unchanged', adp[i - 1]['core'], adp[i]['core']))
            for tag, match, sval, aval in (
                    ('append_reply', verb.startswith('append:') or verb == 'append-lose-reply',
                     src[i]['append_reply'], adp[i]['journal']['append_reply']),
                    ('publication_reply', verb.startswith('pub-'),
                     src[i]['publication_reply'], adp[i]['core']['publication_reply'])):
                if not match:
                    continue
                seen[tag] += 1
                kept.append(witness(case, i, tag, sval, aval))
                if not rel.exact(aobs.get(tag), aval):
                    bad.append(witness(case, i, tag + '-observation', aval, aobs.get(tag)))
                elif not rel.exact(sval, aval):
                    bad.append(witness(case, i, tag + '-cross-side', sval, aval))
    lim = ['no reachable witness class: ' + k for k, v in seen.items() if not v]
    lim.append('prefix staged/identity relation rows not re-derived; sibling obligations cover them')
    if not bad:
        kept.append({'witness_counts': seen})
    return {'status': 'counterexample' if bad else 'supported' if any(seen.values()) else 'unproved',
            'observations': (bad or kept)[:64], 'limitations': lim, 'audited_prefixes': audited}

def _rebind(case, ei):
    states = replay(case['adapter'])
    for j in range(ei, len(case['adapter']['events'])):
        case['adapter']['events'][j]['before_sha256'] = rel.digest(states[j])
        case['adapter']['events'][j]['after_sha256'] = rel.digest(states[j + 1])
        case['rows'][j]['adapter_sha256'] = rel.digest(states[j + 1])

def run_controls(cases, inspect_cases, charge):
    base = inspect_cases(cases, charge)
    results = [{'control': 'unmutated-retained-evidence', 'observed_status': base['status'],
                'consistent': base['status'] != 'counterexample', 'audited_prefixes': base['audited_prefixes']}]
    limitations = []

    def locate(pred):
        for ci, case in enumerate(cases):
            for ei, row in enumerate(case['rows']):
                if pred(case, ei, row):
                    return ci, ei
        return None

    def control(name, pred, mutate, missing):
        hit = locate(pred)
        if hit is None:
            limitations.append(name + ': ' + missing)
            results.append({'control': name, 'exercised': False, 'limitation': missing})
            return
        mut = copy.deepcopy(cases[hit[0]])
        mutate(mut, hit[1])
        res = inspect_cases([mut], charge)
        results.append({'control': name, 'case': mut['case'], 'mutated_prefix': hit[1] + 1,
                        'observed_status': res['status'], 'detected': res['status'] == 'counterexample',
                        'witnesses': [o for o in res['observations'] if o.get('prefix') == hit[1] + 1][:3],
                        'audited_prefixes': res['audited_prefixes'], 'mutation_class': 'forged; reachability not claimed'})

    def forge_decision(value):
        def apply(mut, ei):
            mut['adapter']['events'][ei]['patch']['decision'] = value
            mut['rows'][ei]['adapter_observation']['decision'] = value
            _rebind(mut, ei)
        return apply

    def forge_field(part, field, value):
        def apply(mut, ei):
            mut['adapter']['events'][ei]['patch'].setdefault(part, {})[field] = value
            _rebind(mut, ei)
        return apply

    def append_state(mut, ei):
        forge_field('journal', 'append_reply', ())(mut, ei)
        mut['rows'][ei]['adapter_observation']['append_reply'] = ()

    def has_reply(prefix, field):
        return lambda c, i, r: r['source_action'].startswith(prefix) and bool(r['adapter_observation'].get(field))

    control('invoked-outer-decision-diverges-from-core',
            lambda c, i, r: r['q_invoked'], forge_decision('forged-outer:ok'),
            'no invoked-call prefix; outer/core binding unexercised')
    control('refused-call-visible-response-changed',
            lambda c, i, r: not r['q_invoked'] and r['adapter_observation'].get('decision') != r['source_action'].split('@')[0] + ':ok',
            forge_decision('forged-refusal:ok'), 'no genuinely refused prefix; refusal preservation unexercised')
    control('append-reply-observation-dropped', has_reply('append:', 'append_reply'),
            lambda m, ei: m['rows'][ei]['adapter_observation'].update(append_reply=()),
            'no retained append_reply witness')
    control('append-reply-state-dropped-hash-preserved', has_reply('append:', 'append_reply'),
            append_state, 'no retained append_reply witness')
    control('publication-reply-observation-dropped', has_reply('pub-', 'publication_reply'),
            lambda m, ei: m['rows'][ei]['adapter_observation'].update(publication_reply=()),
            'no retained publication_reply witness')
    control('noninvoked-call-core-drift', lambda c, i, r: not r['q_invoked'],
            forge_field('core', 'decision', 'injected:ok'), 'no non-invoked prefix; core-unchanged unexercised')
    return {'controls': results, 'limitations': limitations, 'cases': len(cases),
            'total_audited_prefixes': sum(r.get('audited_prefixes', 0) for r in results)}
