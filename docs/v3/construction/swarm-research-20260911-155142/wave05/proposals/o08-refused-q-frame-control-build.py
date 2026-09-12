"""Retained-evidence controls + independent prefix check, o08-refused-q-frame.

Obligation: every adapter-guard refusal preserves the full actual Q core and the
invocation list while retaining outer done/decision and the visible refusal.
Anchors (unchanged originals, representation only): batch-06/a_audit.py (refused
or source-handled step leaves the entire Q core unchanged; decision, done bit,
invocations and five-key frame checked separately), batch-06/a_domain.py
(adapter frame {core,journal,done,decision,invocations}; q_profile call
positions), batch-06/adapter_traces.py (patch shape: core/journal carry
changed-field subdicts, other fields replace whole; before/after sha256 chain;
rows bind adapter_sha256 and observations), batch-05/semantic.py (exact/digest).

Inspection replays retained patches only: no reducer, guard, audit_case or
boundary helper is imported or executed. charge.take(1) precedes every inspected
case prefix, including all repeated inspections driven by run_controls.
run_controls mutates deepcopies of real cases; most controls then heal the
retained sha256 chain so detection must reach semantic field equality rather
than outer hashes. Controls needing a genuinely reachable adapter-guard refusal
record a missing-witness limitation when supplied cases contain none. A
violation on unmutated evidence is an original-domain counterexample; detections
on mutated evidence are adversarial-mutation controls, not domain
counterexamples. Journal-only tamper is out of scope (journal-drift control).
No global theorem or acceptance is claimed.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel

exact, digest = rel.exact, rel.digest
KEYS = ['core', 'decision', 'done', 'invocations', 'journal']
LIMITS = [
    'bounded to supplied retained case prefixes; no all-order or global reachability claim',
    'retained sha256 binding is verified, but journal contents are not independently re-derived',
    'refusal laundered in state patch and both row observations at once is outside this check',
]


def _states(trace):
    current = copy.deepcopy(trace['initial']); out = [current]
    for event in trace['events']:
        current = copy.deepcopy(current)
        for key, value in event['patch'].items():
            if key in ('core', 'journal'): current[key].update(value)
            else: current[key] = value
        out.append(current)
    return out


def _heal(adapter, rows):
    states = _states(adapter)
    for i, event in enumerate(adapter['events']):
        event['before_sha256'] = digest(states[i]); event['after_sha256'] = digest(states[i + 1])
        rows[i]['adapter_sha256'] = digest(states[i + 1])


def _refusal_index(case):
    for i, row in enumerate(case['rows']):
        action = case['adapter']['actions'][i]
        if not row['q_invoked'] and row['source_observation']['decision'] != action.split('@')[0] + ':ok':
            return i
    return None


def _v(case, prefix, action, field, expected, observed):
    return {'case': case.get('case'), 'prefix': prefix, 'action': action, 'field': field,
            'expected': expected, 'observed': observed}


def inspect_cases(cases, charge):
    out = {'status': 'unproved', 'observations': [], 'limitations': list(LIMITS), 'audited_prefixes': 0}
    violations, refusals, inspected = [], [], 0
    if not isinstance(cases, (list, tuple)) or not cases:
        out.update(status='not_applicable', observations=['no retained cases supplied']); return out
    for case in cases:
        try:
            adapter, rows = case['adapter'], case['rows']
            actions, events, qp = adapter['actions'], adapter['events'], adapter['q_profile']['actions']
            states = _states(adapter)
        except (KeyError, TypeError, AttributeError) as error:
            out['observations'].append({'malformed': repr(error)}); continue
        inspected += 1
        n = min(len(actions), len(rows))
        if len(events) != len(actions) or len(rows) != len(actions):
            violations.append(_v(case, 0, None, 'inventory', len(actions), {'events': len(events), 'rows': len(rows)}))
        elif not all(e['action'] == actions[i] and digest(states[i]) == e['before_sha256']
                     and digest(states[i + 1]) == e['after_sha256'] for i, e in enumerate(events)):
            violations.append(_v(case, 0, None, 'hash-chain', 'digests bind replayed states', 'mismatch'))
        for i, st in enumerate(states):
            charge.take(1); out['audited_prefixes'] += 1
            core = st.get('core') if isinstance(st.get('core'), dict) else {}
            inv = st.get('invocations') if isinstance(st.get('invocations'), (list, tuple)) else ()
            if set(st) != set(KEYS): violations.append(_v(case, i, None, 'frame', KEYS, sorted(map(str, st))))
            try: mask = sum(1 << qp.index(a) for a in inv)
            except (ValueError, TypeError, AttributeError): mask = -1
            if core.get('done') != mask: violations.append(_v(case, i, None, 'core-done-mask', mask, core.get('done')))
            if not i or i - 1 >= n: continue
            try:
                action, row, before = actions[i - 1], rows[i - 1], states[i - 1]
                bound = row['index'] == i - 1 and row['adapter_action'] == action and row['adapter_sha256'] == digest(st)
                invoked = row['q_invoked']; decision = row['source_observation']['decision']
                seen = row['adapter_observation']['decision']
            except (KeyError, TypeError, IndexError) as error:
                violations.append(_v(case, i, None, 'row-shape', 'typed retained row', repr(error))); continue
            if not bound: violations.append(_v(case, i, action, 'row-binding', digest(st), row.get('adapter_sha256')))
            prior = before.get('invocations') or ()
            if invoked:
                if not exact(st.get('invocations'), tuple(prior) + (action,)):
                    violations.append(_v(case, i, action, 'invocations-extended', list(prior) + [action], list(inv)))
                continue
            old = before.get('core') if isinstance(before.get('core'), dict) else {}
            diff = sorted(k for k in set(old) | set(core) if not exact(old.get(k), core.get(k)))
            if diff: violations.append(_v(case, i, action, 'core-preserved', 'entire Q core unchanged', diff))
            if not exact(before.get('invocations'), st.get('invocations')):
                violations.append(_v(case, i, action, 'invocations-preserved', list(prior), list(inv)))
            done = (before.get('done') or 0) | (1 << actions.index(action))
            if st.get('done') != done: violations.append(_v(case, i, action, 'done', done, st.get('done')))
            if not st.get('decision') == decision == seen:
                violations.append(_v(case, i, action, 'decision', decision, [st.get('decision'), seen]))
            if st.get('decision') != action.split('@')[0] + ':ok':
                refusals.append({'case': case.get('case'), 'prefix': i, 'action': action,
                                 'decision': st.get('decision'), 'core_sha256': digest(core)})
    out['observations'].append({'cases': len(cases), 'inspected_cases': inspected,
                                'refusal_witnesses': len(refusals), 'witnesses': refusals[:16],
                                'violation_count': len(violations), 'violations': violations[:16]})
    if violations: out['status'] = 'counterexample'
    elif not inspected:
        out['status'] = 'not_applicable'; out['limitations'].append('no inspectable retained adapter cases')
    elif refusals:
        out['status'] = 'supported'; out['limitations'].append('supported only over supplied retained case prefixes')
    else: out['limitations'].append('no adapter-guard refusal witnessed; obligation unexercised')
    return out


def run_controls(cases, inspect_cases, charge):
    def inspect(payload):
        try: return inspect_cases(payload, charge)
        except Exception as error: return {'status': 'error', 'observations': [repr(error)]}
    results = [{'control': 'baseline-unmutated', 'classification': 'original-domain',
                'observed': inspect([copy.deepcopy(c) for c in cases])}]
    target, index = None, None
    for candidate in cases:
        try: index = _refusal_index(candidate)
        except (KeyError, TypeError, IndexError): index = None
        if index is not None: target = candidate; break
    if target is None:
        return {'controls': results, 'refusal_witness': None,
                'limitations': list(LIMITS) + ['no reachable refusal; every mutation control skipped']}
    action = target['adapter']['actions'][index]; verb = action.split('@')[0]

    def build(patch=None, rowedit=None, heal=True, drop=False):
        case = copy.deepcopy(target); adapter = case['adapter']
        if drop: adapter['events'].pop(index)
        if patch:
            for key, value in patch(adapter, _states(adapter)).items():
                if key in ('core', 'journal'): adapter['events'][index]['patch'].setdefault(key, {}).update(value)
                else: adapter['events'][index]['patch'][key] = value
        if rowedit: rowedit(case['rows'])
        if heal: _heal(adapter, case['rows'])
        return case
    controls = [
        ('refusal-core-drift-healed', True, lambda: build(lambda a, s: {'core': {'paused': not s[index + 1]['core']['paused']}})),
        ('refusal-invocation-injected-healed', True, lambda: build(lambda a, s: {'invocations': s[index]['invocations'] + (action,)})),
        ('refusal-decision-laundered-healed', True, lambda: build(lambda a, s: {'decision': verb + ':ok'})),
        ('refusal-done-bit-dropped-healed', True, lambda: build(lambda a, s: {'done': s[index]['done']})),
        ('refusal-event-dropped', True, lambda: build(drop=True, heal=False)),
        ('refusal-flagged-invoked', True, lambda: build(rowedit=lambda r: r[index].__setitem__('q_invoked', True), heal=False)),
        ('refusal-journal-drift-healed-out-of-scope', False, lambda: build(lambda a, s: {'journal': {'attestation': ('forged', 0, 'x')}})),
    ]
    for name, expected, make in controls:
        observed = inspect([make()])
        results.append({'control': name, 'expected_detected': expected,
                        'classification': 'adversarial-mutation' if expected else 'outside-obligation-scope',
                        'witness': {'case': target.get('case'), 'prefix': index + 1, 'action': action},
                        'detected': observed.get('status') == 'counterexample', 'observed_status': observed.get('status'),
                        'first_violation': next((v for o in observed.get('observations', []) if isinstance(o, dict)
                                                 for v in o.get('violations', [])), None),
                        'audited_prefixes': observed.get('audited_prefixes', 0)})
    return {'controls': results, 'refusal_witness': {'case': target.get('case'), 'event_index': index, 'action': action},
            'limitations': list(LIMITS) + [
                'mutated states may be unreachable in the original domain; detections are evidence-integrity controls, not domain counterexamples',
                'journal-only tamper healed into the retained chain is intentionally outside this obligation']}
