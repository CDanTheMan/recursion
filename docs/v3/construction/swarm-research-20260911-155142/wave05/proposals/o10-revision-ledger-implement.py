"""Bounded retained-certificate check: o10 revision ledger.

Scope, restated exactly and bounded: for each supplied retained case - an
actual typed ``check.run_history`` product or ``artifact``-restored object -
and for each inspected prefix and transition:

  1. every ``source_revision`` change is exactly ``+1`` and is admitted only
     by a successful ``register:*``/``attempt:*``/``atomic:*``/``append:*``
     action; every other transition, including every visible refusal and
     ``source-restart``, is a nonchange;
  2. ``source_revision`` is monotone nondecreasing in both the source state
     and the adapter journal, including under setup, attempt and
     ``source-restart`` actions;
  3. the adapter journal equals the source authority ledger fields exactly at
     every inspected prefix (the ``a_audit`` ledger postcondition).

Any violation is a ``counterexample`` carrying a falsifiable
expected/observed witness. A clean pass yields ``supported`` for the supplied
cases only; unrestorable material or vacuous coverage yields ``unproved``.
Nothing here is a global theorem, an all-order claim or an accepted
scientific gate.

Source anchors (unchanged originals; representation only - nothing in this
module imports or executes reducer, guard, boundary or model code):
  experiments/v3/cut-source-overnight/s_inclusive.py  +1 revision on
    register/attempt/atomic/append success only; refusals, delegated calls
    and restart leave it unchanged.
  experiments/v3/cut-source-overnight/s_audit.py      independent
    "registration and append revision coverage" invariant.
  experiments/v3/cut-source-overnight/batch-06/a_domain.py   journal shape:
    the EXTRA authority fields plus a typed source-generation token.
  experiments/v3/cut-source-overnight/batch-06/a_audit.py    exact ledger
    postcondition ``d.exact(after['journal'], ledger)``.
  experiments/v3/cut-source-overnight/batch-05/semantic.py   typed
    structural equality mirrored by ``_safe``/``_exact`` below.
  experiments/v3/eight-hour-research-20260910-01a08a22/check.py
    retained case shape: source/adapter traces, actions, rows, prefixes.

Audit accounting: ``charge.take(1)`` is consumed once per case envelope and
once before each inspected case prefix; every repetition counts.
"""

JOURNAL_FIELDS = ('registration', 'attempts', 'append_log', 'append_receipts',
                  'append_reply', 'source_revision', 'collection', 'collected',
                  'attestation', 'staged_source', 'selected_source',
                  'source_generation')
PLUS_ONE = ('register:', 'attempt:', 'atomic:', 'append:')
STATE_KEYS = ('after', 'post', 'next', 'state', 'post_state', 'after_state')
PATCH_KEYS = ('patch', 'changes', 'delta', 'fields')
WITNESS_LIMIT = 24


def _safe(x):
    """JSON-safe typed encoding, mirroring the semantic.typed representation."""
    if hasattr(x, '_fields'):
        return [type(x).__name__, [_safe(v) for v in x]]
    if type(x) is dict:
        return ['dict', [[k, _safe(x[k])] for k in sorted(x, key=repr)]]
    if type(x) in (list, tuple):
        return [type(x).__name__, [_safe(v) for v in x]]
    if type(x) in (str, int, bool, float, type(None)):
        return [type(x).__name__, x]
    return [type(x).__name__, repr(x)]


def _exact(a, b):
    return _safe(a) == _safe(b)


def _state_like(x, adapter):
    if type(x) is not dict:
        return False
    need = ('journal', 'core', 'decision') if adapter else ('source_revision', 'decision')
    return all(k in x for k in need)


def _post_state(event, prev, adapter):
    """Recover one post-state from a retained trace event, or None."""
    if _state_like(event, adapter):
        return event
    if type(event) is dict:
        for key in STATE_KEYS:
            if _state_like(event.get(key), adapter):
                return event[key]
        for key in PATCH_KEYS:
            patch = event.get(key)
            if type(patch) is dict and _state_like(prev, adapter):
                merged = dict(prev)
                merged.update(patch)
                if _state_like(merged, adapter):
                    return merged
        pool = list(event.values())
    elif type(event) in (list, tuple):
        pool = list(event)
    else:
        return None
    found = [v for v in pool if _state_like(v, adapter)]
    return found[0] if len(found) == 1 else None


def _states(trace, adapter):
    """initial plus per-event post-states; unrestorable events count as lost."""
    states, lost = [], 0
    if type(trace) is dict and _state_like(trace.get('initial'), adapter):
        states.append(trace['initial'])
    else:
        lost += 1
    events = trace.get('events') if type(trace) is dict else None
    for event in events or ():
        post = _post_state(event, states[-1] if states else None, adapter)
        if post is None:
            lost += 1
        else:
            states.append(post)
    return states, lost


def _expected_delta(verb, before, decision):
    """Independent ledger rule: +1 only on a successful setup-class action."""
    if not (type(decision) is str and decision.endswith(':ok')):
        return 0
    if verb.startswith('register:'):
        return 0 if before.get('registration') else 1
    return 1 if verb.startswith(PLUS_ONE) else 0


def inspect_cases(cases, charge):
    result = {'status': 'unproved', 'observations': [], 'limitations': [],
              'audited_prefixes': 0}
    if not cases:
        result['status'] = 'not_applicable'
        result['limitations'].append('no retained case objects supplied')
        return result
    witnesses, lost, truncated = [], 0, 0
    categories, refusal_verbs = {}, {}
    total_changes = total_nonchanges = refusals = 0

    def witness(name, prefix, action, field, expected, observed):
        if len(witnesses) < WITNESS_LIMIT:
            witnesses.append({'witness': field, 'case': name, 'prefix': prefix,
                              'action': action, 'expected': expected,
                              'observed': observed})

    for position, case in enumerate(cases):
        charge.take(1)
        name = case.get('case') if type(case) is dict else None
        if type(name) is not str:
            name = 'case-' + str(position)
        if type(case) is not dict or type(case.get('source')) is not dict \
                or type(case.get('adapter')) is not dict:
            lost += 1
            result['limitations'].append(name + ': no typed source/adapter trace')
            continue
        s_states, s_lost = _states(case['source'], False)
        a_states, a_lost = _states(case['adapter'], True)
        lost += s_lost + a_lost
        actions = tuple(case['source'].get('actions') or ())
        if tuple(case['adapter'].get('actions') or ()) != actions:
            witness(name, None, None, 'action-inventory',
                    'adapter actions identical to source actions',
                    _safe(case['adapter'].get('actions')))
        depth, rows = len(actions) + 1, case.get('rows') or ()
        n = min(len(s_states), len(a_states), depth)
        if len(s_states) != depth or len(a_states) != depth:
            truncated += 1
            result['limitations'].append(
                '%s: restored source=%d adapter=%d of %d prefixes'
                % (name, len(s_states), len(a_states), depth))
        audited = changes = nonchanges = mismatched = 0
        for i in range(n):
            charge.take(1)
            s, a = s_states[i], a_states[i]
            journal = a.get('journal')
            if type(journal) is not dict or type(s.get('source_revision')) is not int \
                    or type(journal.get('source_revision')) is not int:
                lost += 1
                continue
            audited += 1
            if set(journal) != set(JOURNAL_FIELDS):
                witness(name, i, None, 'journal-inventory',
                        sorted(JOURNAL_FIELDS), sorted(journal))
            for field in JOURNAL_FIELDS:
                if field in journal and field in s and not _exact(journal[field], s[field]):
                    mismatched += 1
                    witness(name, i, None, 'journal-field:' + field,
                            _safe(s[field]), _safe(journal[field]))
            if i == 0:
                if s['source_revision'] or journal['source_revision']:
                    witness(name, 0, None, 'initial-revision', 0,
                            [s['source_revision'], journal['source_revision']])
                continue
            action = actions[i - 1]
            verb = action.split('@')[0] if type(action) is str else repr(action)
            ps, pj = s_states[i - 1], a_states[i - 1].get('journal') or {}
            prev_s, prev_j = ps.get('source_revision'), pj.get('source_revision')
            if type(prev_s) is not int or type(prev_j) is not int:
                witness(name, i, action, 'revision-shape', 'int',
                        _safe([prev_s, prev_j]))
                continue
            ds, dj = s['source_revision'] - prev_s, journal['source_revision'] - prev_j
            es = _expected_delta(verb, ps, s.get('decision'))
            ej = _expected_delta(verb, pj, a.get('decision'))
            category = 'restart' if verb == 'source-restart' else \
                'revision-action' if verb.startswith(PLUS_ONE) else 'other'
            categories[category] = categories.get(category, 0) + 1
            if not (type(s.get('decision')) is str and s['decision'].endswith(':ok')):
                refusals += 1
                refusal_verbs[verb] = refusal_verbs.get(verb, 0) + 1
            changes, nonchanges = changes + (ds != 0), nonchanges + (ds == 0)
            total_changes, total_nonchanges = total_changes + (ds != 0), \
                total_nonchanges + (ds == 0)
            if ds < 0 or dj < 0:
                witness(name, i, action, 'revision-monotonicity', '>= 0', [ds, dj])
            if ds != es:
                witness(name, i, action, 'source-revision-delta', es, ds)
            if dj != ej:
                witness(name, i, action, 'journal-revision-delta', ej, dj)
            if i - 1 < len(rows) and type(rows[i - 1]) is dict:
                row = rows[i - 1]
                so = (row.get('source_observation') or {}).get('decision')
                ao = (row.get('adapter_observation') or {}).get('decision')
                if (so is not None and so != s.get('decision')) or \
                        (ao is not None and ao != a.get('decision')):
                    witness(name, i, action, 'row-decision-binding',
                            _safe([s.get('decision'), a.get('decision')]),
                            _safe([so, ao]))
        result['observations'].append({
            'case': name, 'prefixes_audited': audited,
            'revision_changes': changes, 'revision_nonchanges': nonchanges,
            'journal_field_mismatches': mismatched,
            'final_source_revision': s_states[n - 1].get('source_revision') if n else None})
        result['audited_prefixes'] += audited

    result['observations'] = witnesses + [{
        'hypotheses': 'reachable typed states; adapter journal shadows source '
                      'authority fields; delegated calls leave the ledger unchanged',
        'transition_categories': categories,
        'refused_decisions_observed': refusals,
        'refusal_verbs': refusal_verbs}] + result['observations']
    if not categories.get('revision-action'):
        result['limitations'].append(
            'no successful register/attempt/atomic/append transition observed; '
            'the change clause is unproved for these cases')
    if not categories.get('restart'):
        result['limitations'].append(
            'no source-restart transition observed; restart monotonicity had no witness')
    if lost:
        result['limitations'].append(
            '%d state(s) unrestorable; affected prefixes uninspected' % lost)
    if truncated:
        result['limitations'].append(
            '%d case(s) with incomplete restored traces' % truncated)
    if witnesses:
        result['status'] = 'counterexample'
    elif not result['audited_prefixes'] or lost or truncated \
            or not total_changes or not total_nonchanges:
        result['status'] = 'unproved'
    else:
        result['status'] = 'supported'
    result['limitations'].append(
        'bounded to the supplied retained cases only; no all-order, reduction '
        'or acceptance claim is made or implied')
    return result
