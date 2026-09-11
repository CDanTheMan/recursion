"""Bounded retained-certificate check for obligation o08-refused-q-frame.

Obligation: every adapter-guard refusal preserves the full actual Q core and
the actual Q invocation inventory while retaining the outer adapter decision,
the outer done mask, and the visible refusal itself.

API: inspect_cases(cases, charge). cases are actual typed original
c.run_history / c.artifact restored case objects
(experiments/v3/eight-hour-research-20260910-01a08a22/check.py).
charge.take(1) is called exactly once BEFORE each case prefix is inspected;
every repetition counts and audited_prefixes equals the number of takes.

This module executes nothing: no imports, no reducer, guard, restore, or
boundary helper calls. It walks the retained adapter-trace patch format
(batch-06/adapter_traces.py trace_event/restore: 'core'/'journal' patch
entries shallow-merge, other keys replace) to reconstruct prefix states
read-only, then compares actual fields against retained rows/certificates.

Representation anchors (unchanged sources, consulted for shape only):
  - a_audit.check: call==False requires exact core equality, invocations
    unchanged, after['decision']==guard reason, done|action-bit,
    core['done']==mask(q_profile actions, invocations), frame keys exactly
    {core,journal,done,decision,invocations}
  - a_domain.initial/subprofile: journal keys = s_domain.EXTRA plus
    source_generation; potential Q calls are the non-source-only actions
  - guard_a/guard_b/guard_audit: '<verb>:<reason>'; 'ok'=handled, else refusal
  - check.run_history/audit_case rows (index, literal actions, q_invoked,
    adapter_observation['decision']) and per-prefix certificates
  - semantic.typed: typed equality representation used for field diffs

Result is JSON-safe: {status, observations, limitations, audited_prefixes}.
'supported' certifies only the supplied retained cases; it is no global
theorem and no scientific acceptance.
"""

FRAME = ('core', 'journal', 'done', 'decision', 'invocations')
JOURNAL = ('registration', 'attempts', 'append_log', 'append_receipts',
           'append_reply', 'source_revision', 'collection', 'collected',
           'attestation', 'staged_source', 'selected_source', 'source_generation')
MERGED = ('core', 'journal')


def _typed(value):
    if isinstance(value, dict):
        return ['dict', [[k, _typed(value[k])] for k in sorted(value)]]
    if isinstance(value, (list, tuple)):
        return [type(value).__name__, [_typed(v) for v in value]]
    return [type(value).__name__, value]


def _structure(case):
    if not isinstance(case, dict):
        return 'case is not a dictionary'
    adapter = case.get('adapter')
    if not isinstance(adapter, dict) or not isinstance(adapter.get('initial'), dict):
        return 'missing adapter trace/initial'
    for key in ('events', 'actions', 'profile', 'q_profile'):
        if key not in adapter:
            return 'adapter trace lacks ' + key
    if len(adapter['events']) != len(adapter['actions']) or not all(
            isinstance(e, dict) and isinstance(e.get('patch'), dict)
            for e in adapter['events']):
        return 'adapter event inventory/patch mismatch'
    rows, prefixes = case.get('rows'), case.get('prefixes')
    if not isinstance(rows, list) or len(rows) != len(adapter['events']):
        return 'comparison-row inventory mismatch'
    if not isinstance(prefixes, list) or len(prefixes) != len(adapter['events']) + 1:
        return 'audited-prefix inventory mismatch'
    if not all(isinstance(x, dict) for x in rows + prefixes):
        return 'non-dictionary row or prefix certificate'
    return None


def _states(trace):
    out = [dict(trace['initial'])]
    for event in trace['events']:
        nxt = dict(out[-1])
        for key, value in event['patch'].items():
            base = out[-1].get(key)
            nxt[key] = ({**base, **value} if key in MERGED and
                        isinstance(base, dict) and isinstance(value, dict) else value)
        out.append(nxt)
    return out


def _mask(actions, invocations):
    if not isinstance(invocations, (list, tuple)):
        return None
    total = 0
    for action in invocations:
        if action not in actions:
            return None
        total |= 1 << actions.index(action)
    return total


def _diff(before, after):
    if not isinstance(before, dict) or not isinstance(after, dict):
        return ['<non-dict-core>']
    return sorted(k for k in set(before) | set(after)
                  if k not in before or k not in after
                  or _typed(before[k]) != _typed(after[k]))


def inspect_cases(cases, charge):
    observations, limitations = [], []
    audited = inspected = refusals = handled = delegated = 0
    counterexample = None

    def record(kind, name, prefix, expected, observed):
        item = {'kind': kind, 'case': name, 'prefix': prefix,
                'expected': expected, 'observed': observed}
        observations.append(item)
        return item

    for case in cases:
        name = case.get('case') if isinstance(case, dict) else None
        problem = _structure(case)
        if problem:
            limitations.append('case ' + repr(name) + ' not inspected: ' + problem)
            continue
        inspected += 1
        adapter, rows = case['adapter'], case['rows']
        actions = adapter['actions']
        profile_actions = tuple(adapter['profile']['actions'])
        q_actions = tuple(adapter['q_profile']['actions'])
        states = _states(adapter)

        def fail(kind, prefix, expected, observed):
            return record(kind, name, prefix, expected, observed)

        for prefix, state in enumerate(states):
            charge.take(1)
            audited += 1
            if set(state) != set(FRAME):
                counterexample = counterexample or fail(
                    'adapter-frame-keys', prefix, sorted(FRAME), sorted(state))
            journal = state.get('journal')
            if not isinstance(journal, dict) or set(journal) != set(JOURNAL):
                counterexample = counterexample or fail(
                    'journal-frame-keys', prefix, sorted(JOURNAL),
                    sorted(journal) if isinstance(journal, dict) else _typed(journal))
            core, invocations = state.get('core'), state.get('invocations')
            if not isinstance(core, dict) or \
                    _mask(q_actions, invocations) != core.get('done'):
                counterexample = counterexample or fail(
                    'invocation-mask', prefix,
                    'core.done==mask(q_profile,invocations)',
                    {'core_done': core.get('done') if isinstance(core, dict)
                     else _typed(core), 'invocations': _typed(invocations)})
            if case['prefixes'][prefix].get('prefix') != prefix:
                counterexample = counterexample or fail(
                    'prefix-certificate-order', prefix, prefix,
                    case['prefixes'][prefix].get('prefix'))
            if prefix == 0:
                if (state.get('done'), state.get('decision'), invocations) != (0, 'initial', ()):
                    counterexample = counterexample or fail(
                        'initial-frame', prefix, {'done': 0, 'decision': 'initial'},
                        {'done': state.get('done'), 'decision': state.get('decision'),
                         'invocations': _typed(invocations)})
                continue
            i = prefix - 1
            before, event = states[i], adapter['events'][i]
            row, action = rows[i], actions[i]
            verb = action.partition('@')[0]
            if not (event.get('action') == action and row.get('index') == i
                    and row.get('source_action') == action
                    and row.get('adapter_action') == action):
                counterexample = counterexample or fail(
                    'literal-inventory', prefix, action,
                    {'event': event.get('action'), 'row_index': row.get('index'),
                     'row_actions': [row.get('source_action'), row.get('adapter_action')]})
            position = profile_actions.index(action) if action in profile_actions else -1
            bdone = before.get('done')
            expected_done = bdone | (1 << position) if position >= 0 \
                and isinstance(bdone, int) else None
            if position < 0:
                counterexample = counterexample or fail(
                    'action-outside-profile', prefix, action, None)
            elif expected_done is None or state.get('done') != expected_done:
                counterexample = counterexample or fail(
                    'done-bit', prefix, expected_done, state.get('done'))
            calls_before, calls_after = before.get('invocations'), invocations
            grew = (isinstance(calls_before, (list, tuple))
                    and isinstance(calls_after, (list, tuple))
                    and len(calls_after) == len(calls_before) + 1
                    and calls_after[:-1] == calls_before and calls_after[-1] == action)
            if bool(row.get('q_invoked')) != grew:
                counterexample = counterexample or fail(
                    'declared-vs-actual-invocation', prefix, bool(row.get('q_invoked')),
                    {'invocations_before': _typed(calls_before),
                     'invocations_after': _typed(calls_after)})
            if grew:
                delegated += 1
                if isinstance(core, dict) and state.get('decision') != core.get('decision'):
                    counterexample = counterexample or fail(
                        'delegated-decision', prefix, core.get('decision'), state.get('decision'))
                continue
            decision = state.get('decision')
            well_formed = (isinstance(decision, str) and decision.startswith(verb + ':')
                           and len(decision) > len(verb) + 1)
            expected = {'decision_form': verb + ':<reason>', 'core_preserved': True,
                        'invocations_preserved': True, 'done': expected_done}
            observed = {'action': action, 'decision': decision, 'done': state.get('done'),
                        'differing_core_fields': _diff(before.get('core'), core),
                        'invocations_preserved': _typed(calls_before) == _typed(calls_after),
                        'row_q_invoked': row.get('q_invoked'),
                        'row_adapter_decision': (row.get('adapter_observation') or {}).get('decision'),
                        'before_sha256': event.get('before_sha256'),
                        'after_sha256': event.get('after_sha256')}
            reason = decision[len(verb) + 1:] if well_formed else None
            if observed['differing_core_fields'] or not observed['invocations_preserved']:
                counterexample = counterexample or fail(
                    'refusal-q-frame-violation', prefix, expected, observed)
            elif not well_formed:
                counterexample = counterexample or fail(
                    'visible-decision-shape', prefix, expected, observed)
            elif observed['row_adapter_decision'] != decision:
                counterexample = counterexample or fail(
                    'visible-refusal-mismatch', prefix, expected, observed)
            elif reason != 'ok':
                refusals += 1
                record('adapter-guard-refusal', name, prefix, expected, observed)
            else:
                handled += 1

    observations.append({'kind': 'accounting', 'cases_inspected': inspected,
                         'audited_prefixes': audited, 'adapter_guard_refusals': refusals,
                         'guard_handled': handled, 'delegated_calls': delegated})
    limitations += ['supported covers only the supplied retained cases; no '
                    'all-order reachability or scientific acceptance is claimed',
                    'before/after sha256 anchors are retained certificate fields; '
                    'canonical digests are not recomputed here (no helpers executed)',
                    'rows/prefixes are retained hypotheses; declared q_invoked is '
                    'cross-checked against actual invocation growth and refusals '
                    'are classified by the retained decision string']
    if counterexample is not None:
        status = 'counterexample'
    elif inspected == 0:
        status = 'not_applicable'
    elif refusals == 0:
        status = 'unproved'
        limitations.append('no adapter-guard refusal occurred in the inspected cases')
    else:
        status = 'supported'
    return {'status': status, 'observations': observations,
            'limitations': limitations, 'audited_prefixes': audited}
