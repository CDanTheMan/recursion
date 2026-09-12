"""Bounded staged-field origin checker + adversarial retained-evidence controls.

Obligation o16-stage-origin: chronological origin identification for every actual
staged-field writer in original scale-eight-action-race retained histories;
distinguish the single reachable writer 'stage@22' (fixed suffix index 22; spec
fixed_prefix_length=11, fixed_suffix_start=19, depth 34) from hypothetical
'stage'-prefixed variants (q_domain invalid-* profiles) unreachable in this domain.

Anchors (unchanged originals, representation only; no reducer, boundary helper or
model executes): batch-07/identity.py origin()/proof(); batch-07/identity_audit.py
expected_proof()/valid_objects(); batch-06/adapter_traces.py restore() patch replay
under before/after sha256 + literal occurrence; s_domain.py fixed-suffix 'stage';
batch-05/semantic.py typed()/exact()/digest()/signed() witnesses.

Accounting: inspect_cases calls charge.take(1) BEFORE inspecting each case prefix;
every repetition (including run_controls calls on mutated copies) counts. Writer
mutations need a genuinely reachable stage@22 witness; without one they are skipped
with a limitation. The unrepaired-digest control stays unreachable -> integrity
failure, never an original-domain counterexample. No staged write -> 'unproved'
(missing witness), never vacuous 'supported'. No global theorem or PASS.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as r

d = r.s
SIDES = ('source', 'adapter')
STAGE_ACTION, STAGE_INDEX = 'stage@22', 22


def stage_of(state, side):
    return state.get('staged') if side == 'source' else state.get('core', {}).get('staged')


def apply_patch(trace, state, patch):
    for key, value in patch.items():
        if trace['side'] == 'adapter' and key in ('core', 'journal'):
            state[key].update(value)
        else:
            state[key] = value


def replay(trace):
    """Retained patch replay under digest binding; return (states, problem)."""
    original = set(trace['actions']) == set(trace['profile']['actions'])
    current, states, seen = copy.deepcopy(trace['initial']), [], set()
    states.append(current)
    for i, event in enumerate(trace['events']):
        if event['action'] != trace['actions'][i] or event['action'] in seen:
            return states, dict(kind='evidence-integrity-failure', index=i, reason='occurrence')
        seen.add(event['action'])
        if r.digest(current) != event['before_sha256']:
            return states, dict(kind='evidence-integrity-failure', index=i, reason='prestate digest')
        current = copy.deepcopy(current)
        apply_patch(trace, current, event['patch'])
        if r.digest(current) != event['after_sha256']:
            return states, dict(kind='evidence-integrity-failure', index=i, reason='poststate digest')
        states.append(current)
    return states, (None if original else dict(kind='foreign-inventory', index=-1,
                                             reason='non-original action inventory'))


def writer_rows(trace, states, side, original):
    rows = []
    for i in range(len(states) - 1):
        if r.exact(stage_of(states[i], side), stage_of(states[i + 1], side)):
            continue
        action, decision = trace['events'][i]['action'], states[i + 1].get('decision', '')
        verb = action.split('@')[0]
        kind = ('visible-refusal-wrote-staged' if decision != verb + ':ok' else
                'reachable-original-stage' if original and action == STAGE_ACTION and i == STAGE_INDEX
                else 'hypothetical-stage-prefixed' if verb.startswith('stage') else 'non-stage-writer')
        rows.append(dict(side=side, index=i, action=action, decision=decision, classification=kind,
                         value_sha256=r.digest(stage_of(states[i + 1], side))))
    return rows


def inspect_cases(cases, charge):
    observations, limitations, audited, witnessed, sev = [], [], 0, 0, set()

    def note(label, prefix, kind, reach, **kw):
        sev.add(reach)
        observations.append(dict(case=label, prefix=prefix, kind=kind, reachability=reach, **kw))

    if not cases:
        return dict(status='not_applicable', observations=[], audited_prefixes=0,
                    limitations=['no case objects supplied'])
    for ci, case in enumerate(cases):
        label = case.get('case', ci) if isinstance(case, dict) else ci
        try:
            seqs, problems = {}, {}
            for side in SIDES:
                seqs[side], problems[side] = replay(case[side])
            original = all(set(case[s]['actions']) == set(case[s]['profile']['actions'])
                           for s in SIDES) and case['source']['profile']['actions'][STAGE_INDEX] == STAGE_ACTION
            rows = {s: writer_rows(case[s], seqs[s], s, original) for s in SIDES}
        except (KeyError, TypeError, IndexError, AttributeError) as error:
            note(label, -1, 'evidence-integrity-failure', 'integrity-failure', reason=repr(error))
            continue
        reach = 'original-domain' if original else 'hypothetical-unreachable'
        for side in SIDES:
            problem = problems[side]
            if problem:
                note(label, problem['index'], problem['kind'],
                     reach if problem['kind'] == 'foreign-inventory' else 'integrity-failure',
                     side=side, reason=problem['reason'])
            for row in rows[side]:
                if row['classification'] != 'reachable-original-stage':
                    note(label, row['index'], row['classification'], reach, **row)
        limit, first = min(len(seqs[s]) for s in SIDES), {}
        for p in range(limit):
            charge.take(1)
            audited += 1
            cur = {s: stage_of(seqs[s][p], s) for s in SIDES}
            if bool(cur['source']) != bool(cur['adapter']) or all(cur.values()) and not r.exact(cur['source'], cur['adapter']):
                note(label, p, 'cross-side-staged-divergence', reach)
            first.update({s: p for s in SIDES if cur[s] and s not in first})
        origins = {s: max([w['index'] for w in rows[s] if w['index'] < first[s]] or [None]) for s in first}
        for s, o in origins.items():
            if o is None:
                note(label, first[s], 'staged-without-origin', reach, side=s)
        witnessed += origins.get('source') is not None
        if len(origins) == 2 and None not in origins.values() and origins['source'] != origins['adapter']:
            note(label, -1, 'cross-side-origin-mismatch', reach, **origins)
        observations.append(dict(case=label, kind='staged-origin-summary', reachability=reach,
                                 writers=rows, inspected_prefixes=limit))
    status = 'counterexample' if 'original-domain' in sev else 'unproved' if sev or not witnessed else 'supported'
    if status == 'unproved':
        limitations.append('only unreachable/foreign anomalies; not original-domain evidence'
                           if sev else 'no reachable staged-field writer observed; origin unsupported')
    return dict(status=status, observations=observations, limitations=limitations,
                audited_prefixes=audited)


def rehash(trace):
    """Recompute retained digests so a mutation stays internally consistent."""
    current = copy.deepcopy(trace['initial'])
    for event in trace['events']:
        event['before_sha256'] = r.digest(current)
        current = copy.deepcopy(current)
        apply_patch(trace, current, event['patch'])
        event['after_sha256'] = r.digest(current)


def run_controls(cases, inspect_cases, charge):
    controls = []

    def call(label, target, expected, kinds):
        try:
            out = inspect_cases(target, charge)
        except Exception as error:
            out = {'error': type(error).__name__}
        got = {o.get('kind') for o in out.get('observations', [])}
        controls.append(dict(control=label, expected=expected, expected_kinds=sorted(kinds),
            observed_status=out.get('status'), observed_kinds=sorted(got),
            detected=out.get('status') == expected and set(kinds) <= got, error=out.get('error')))

    def ok(case):
        try:
            return all(any(w['index'] == STAGE_INDEX for w in writer_rows(case[s], replay(case[s])[0], s, True))
                       for s in SIDES)
        except Exception:
            return False

    def patch(t, i):
        p = t['events'][i]['patch']
        return p.get('core', p) if t['side'] == 'adapter' else p

    def build(fn, sides=SIDES, fix=True):
        m = copy.deepcopy(base)
        for s in sides:
            fn(m[s])
            if fix:
                rehash(m[s])
        return [m]

    def hypothetical(t):
        t['actions'] = list(t['actions'])
        t['actions'][STAGE_INDEX] = t['events'][STAGE_INDEX]['action'] = 'stage-owner@22'
        t['events'][STAGE_INDEX]['patch']['decision'] = 'stage-owner:ok'

    call('unmodified-real-cases', cases, 'supported', {'staged-origin-summary'})
    base = next((c for c in cases or [] if ok(c)), None)
    if base is None:
        controls.append(dict(control='reachable-stage-witness', detected=False, limitation=
            'no supplied case has a stage@22 write; writer mutations need a genuine witness'))
        return dict(controls=controls, witness_present=False)
    for label, expected, kinds, fn in (
            ('hypothetical-stage-prefixed-writer', 'unproved', {'hypothetical-stage-prefixed'}, hypothetical),
            ('non-stage-writer-erases-staged', 'counterexample', {'non-stage-writer'},
             lambda t: patch(t, STAGE_INDEX + 1).__setitem__('staged', ())),
            ('staged-write-dropped-missing-witness', 'unproved', set(),
             lambda t: patch(t, STAGE_INDEX).pop('staged', None))):
        try:
            call(label, build(fn), expected, kinds)
        except Exception as error:
            controls.append(dict(control=label, expected=expected, detected=False,
                                 construction_error=type(error).__name__))
    call('unrepaired-digest-mutation',
         build(lambda t: patch(t, STAGE_INDEX).__setitem__('staged', ()), ('source',), False),
         'unproved', {'evidence-integrity-failure'})
    return dict(controls=controls, witness_present=True)
