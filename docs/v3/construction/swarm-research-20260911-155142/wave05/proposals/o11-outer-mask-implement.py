"""Bounded retained-certificate check for obligation o11-outer-mask.

Claim under inspection: the original OUTER done-mask of retained source and
adapter states covers permuted literal actions by PROFILE POSITION
(done|(1<<profile['actions'].index(a))), separable from the chronological
index of an occurrence inside a permuted schedule and from the decimal
occurrence suffix after '@'. The adapter INNER Q mask (core['done']) is a
second mask over retained q_profile positions, checked separately against
retained invocations.

Source anchors (unchanged originals; nothing here imports or executes them):
- experiments/v3/cut-source-overnight/s_inclusive.py and s_split.py step:
  done|(1<<profile['actions'].index(action)).
- experiments/v3/cut-source-overnight/batch-06/a_inclusive.py and a_split.py
  step: identical outer mask on adapter frames.
- experiments/v3/cut-source-overnight/batch-06/a_audit.py check:
  after['core']['done']==sum(1<<potential.index(a) for a in calls) plus exact
  invocations; a_domain.py subprofile fixes q_profile['actions'].
- experiments/v3/cut-source-overnight/batch-06/adapter_traces.py
  trace_event/restore: retained initial states and per-event patches;
  adapter core/journal patches are field-level.
- experiments/v3/eight-hour-research-20260910-01a08a22/check.py
  run_history/audit_case: producers of case/rows/prefixes.
- docs/v3/construction/swarm-research-20260911-155142/boundary-01/spec.json:
  34 literal actions, fixed prefix 11, permuted core 8, suffix start 19.

Finite accounting: charge.take(1) runs exactly once before each inspected
(case, prefix) pair, repetitions included; audited_prefixes counts those
charged inspections. Cases failing structural screening consume no prefix
charge. No reducer, guard, audit, inventory or census code is imported or
executed; only retained fields are read.
"""

__all__ = ('inspect_cases',)


def _positions(profile):
    if not isinstance(profile, dict):
        return None
    actions = profile.get('actions')
    if (not isinstance(actions, (list, tuple)) or not actions
            or not all(type(a) is str for a in actions)
            or len(set(actions)) != len(actions)
            or not isinstance(profile.get('requires'), dict)):
        return None
    return {a: i for i, a in enumerate(actions)}


def _suffix(action):
    tail = action.rpartition('@')[2]
    return int(tail) if tail.isdigit() else None


def _mask(actions, positions):
    value = 0
    for action in actions:
        if action in positions:
            value |= 1 << positions[action]
    return value


def _screen(case):
    if not isinstance(case, dict):
        return 'case is not a dict'
    for side in ('source', 'adapter'):
        trace = case.get(side)
        if not isinstance(trace, dict):
            return side + ' trace missing'
        if (not isinstance(trace.get('initial'), dict)
                or not isinstance(trace.get('profile'), dict)
                or not isinstance(trace.get('events'), (list, tuple))
                or not isinstance(trace.get('actions'), (list, tuple))):
            return side + ' trace shape invalid'
    source, adapter = case['source'], case['adapter']
    if not all(type(a) is str for a in source['actions']):
        return 'non-literal scheduled action'
    if tuple(source['actions']) != tuple(adapter['actions']):
        return 'source/adapter literal schedules differ'
    if (len(source['events']) != len(source['actions'])
            or len(adapter['events']) != len(adapter['actions'])):
        return 'visible event inventory does not cover literal occurrences'
    if not isinstance(adapter.get('q_profile'), dict):
        return 'retained adapter q_profile missing'
    if type(source['initial'].get('done')) is not int:
        return 'source initial done not an int'
    core = adapter['initial'].get('core')
    if (not isinstance(core, dict) or type(core.get('done')) is not int
            or type(adapter['initial'].get('done')) is not int
            or not isinstance(adapter['initial'].get('invocations'), (list, tuple))):
        return 'adapter initial masks or invocations invalid'
    return None


def _defect(prefix, kind, expected, observed, side=None):
    row = dict(prefix=prefix, kind=kind, expected=expected, observed=observed)
    if side is not None:
        row['side'] = side
    return row


def _audit_case(case, charge, label, pos, qpos, out):
    source, adapter = case['source'], case['adapter']
    actions = tuple(source['actions'])
    requires = source['profile']['requires']
    rows = case.get('rows')
    rows = rows if isinstance(rows, (list, tuple)) and len(rows) >= len(actions) else None
    prefixes = case.get('prefixes')
    prefixes = prefixes if isinstance(prefixes, (list, tuple)) and len(prefixes) > len(actions) else None
    if rows is None or prefixes is None:
        out['limitations'].append('case %r: retained rows/prefixes unavailable; row-level cross-checks skipped' % (label,))
    s_done = source['initial']['done']
    a_done = adapter['initial']['done']
    c_done = adapter['initial']['core']['done']
    invoked = tuple(adapter['initial']['invocations'])
    executed, seen, defects = [], set(), []
    disc = split = charged = 0
    first_disc = None
    for k in range(len(actions) + 1):
        charge.take(1)
        charged += 1
        if k:
            i = k - 1
            action = actions[i]
            for side, trace in (('source', source), ('adapter', adapter)):
                ev = trace['events'][i]
                if not isinstance(ev, dict) or ev.get('action') != action:
                    defects.append(_defect(k, 'event-action-mismatch', action,
                                           ev.get('action') if isinstance(ev, dict) else None, side))
                elif i and ev.get('before_sha256') != trace['events'][i - 1].get('after_sha256'):
                    defects.append(_defect(k, 'broken-retained-event-chain',
                                           trace['events'][i - 1].get('after_sha256'),
                                           ev.get('before_sha256'), side))
            if action in seen:
                defects.append(_defect(k, 'duplicate-occurrence', 'unique literal occurrence', action))
            reqs = requires.get(action)
            if reqs is None:
                defects.append(_defect(k, 'action-without-requires-entry', 'requires entry', action))
            elif any(r not in seen for r in reqs):
                defects.append(_defect(k, 'unsatisfied-dependency', sorted(reqs),
                                       sorted(r for r in reqs if r not in seen)))
            if action not in pos:
                defects.append(_defect(k, 'literal-outside-profile', 'profile membership', action))
            previous = invoked
            patch = source['events'][i].get('patch') if isinstance(source['events'][i], dict) else None
            if isinstance(patch, dict) and type(patch.get('done')) is int:
                s_done = patch['done']
            patch = adapter['events'][i].get('patch') if isinstance(adapter['events'][i], dict) else None
            if isinstance(patch, dict):
                if type(patch.get('done')) is int:
                    a_done = patch['done']
                core = patch.get('core')
                if isinstance(core, dict) and type(core.get('done')) is int:
                    c_done = core['done']
                if isinstance(patch.get('invocations'), (list, tuple)):
                    invoked = tuple(patch['invocations'])
            seen.add(action)
            executed.append(action)
            if rows is not None:
                row = rows[i]
                if (not isinstance(row, dict) or row.get('index') != i
                        or row.get('source_action') != action
                        or row.get('adapter_action') != action):
                    defects.append(_defect(k, 'row-chronology-mismatch', [i, action],
                                           None if not isinstance(row, dict) else
                                           [row.get('index'), row.get('source_action'), row.get('adapter_action')]))
                else:
                    grew = len(invoked) - len(previous)
                    qi = row.get('q_invoked')
                    if type(qi) is not bool:
                        defects.append(_defect(k, 'q-invoked-flag-not-boolean', 'bool', qi))
                    elif qi and not (grew == 1 and invoked and invoked[-1] == action):
                        defects.append(_defect(k, 'q-invocation-row-mismatch', [action],
                                               list(invoked[len(previous):])))
                    elif not qi and grew:
                        defects.append(_defect(k, 'q-invocation-on-refused-row', [],
                                               list(invoked[len(previous):])))
        if prefixes is not None:
            item = prefixes[k]
            if not isinstance(item, dict) or item.get('prefix') != k:
                defects.append(_defect(k, 'prefix-index-mismatch', k,
                                       item.get('prefix') if isinstance(item, dict) else None))
        expected = _mask(executed, pos)
        chronological = (1 << k) - 1
        if expected != chronological:
            disc += 1
            if first_disc is None:
                first_disc = dict(prefix=k, expected=expected, chronological=chronological,
                                  observed=dict(source=s_done, adapter=a_done))
        bits = [_suffix(a) for a in executed]
        if bits and all(b is not None for b in bits):
            value = 0
            for b in bits:
                value |= 1 << b
            if value != expected:
                split += 1
        for side, observed in (('source', s_done), ('adapter', a_done)):
            if observed != expected:
                kind = ('done-mask-follows-chronological-index'
                        if observed == chronological else 'done-mask-mismatch')
                defects.append(_defect(k, kind, expected, observed, side))
        foreign = [a for a in invoked if a not in qpos]
        if foreign:
            defects.append(_defect(k, 'invocation-outside-q-profile', 'q_profile membership', foreign))
        elif c_done != _mask(invoked, qpos):
            defects.append(_defect(k, 'core-done-mask-mismatch', _mask(invoked, qpos), c_done))
        inv_set = set(invoked)
        if len(inv_set) != len(invoked) or tuple(a for a in executed if a in inv_set) != invoked:
            defects.append(_defect(k, 'invocations-not-chronological-subsequence',
                                   [a for a in executed if a in inv_set], list(invoked)))
    n = len(actions)
    out['observations'].append(dict(
        case=label, literal_actions=n, audited_prefixes=charged,
        schedule_is_permuted=tuple(actions) != tuple(source['profile']['actions']),
        schedule_covers_profile=set(actions) == set(pos),
        occurrence_suffix_equals_profile_position=all(_suffix(a) == pos.get(a) for a in actions),
        discriminating_prefixes=disc, first_discriminating_witness=first_disc,
        suffix_position_split_prefixes=split,
        final_outer_done=dict(expected=_mask(actions, pos), source=s_done, adapter=a_done),
        q_invocations=len(invoked),
        final_core_done=dict(expected=_mask(invoked, qpos), observed=c_done),
        defect_count=len(defects), defect_witnesses=defects[:20]))
    return charged, disc, split, bool(defects)


def inspect_cases(cases, charge):
    """Inspect retained restored case objects; never executes a reducer."""
    out = {'status': 'unproved', 'observations': [], 'limitations': [], 'audited_prefixes': 0}
    if not isinstance(cases, (list, tuple)) or not cases:
        out['status'] = 'not_applicable'
        out['limitations'].append('no retained case sequence supplied')
        return out
    discriminating = suffix_split = skipped = 0
    counterexample = permuted_seen = False
    for index, case in enumerate(cases):
        label = case.get('case', index) if isinstance(case, dict) else index
        defect = _screen(case)
        pos = qpos = None
        if defect is None:
            pos = _positions(case['source']['profile'])
            qpos = _positions(case['adapter']['q_profile'])
            if pos is None or qpos is None:
                defect = 'profile is not a unique literal-action inventory'
        if defect is not None:
            skipped += 1
            out['limitations'].append('case %r skipped: %s' % (label, defect))
            continue
        charged, disc, split, bad = _audit_case(case, charge, label, pos, qpos, out)
        out['audited_prefixes'] += charged
        discriminating += disc
        suffix_split += split
        permuted_seen = permuted_seen or out['observations'][-1]['schedule_is_permuted']
        counterexample = counterexample or bad
    if counterexample:
        out['status'] = 'counterexample'
    elif not out['audited_prefixes']:
        out['status'] = 'not_applicable'
        out['limitations'].append('no supplied case carried an auditable retained trace')
    elif not permuted_seen or not discriminating:
        out['status'] = 'unproved'
        out['limitations'].append('audited orders never separated profile-position masks from chronological masks; mask semantics undecided on this evidence')
    else:
        out['status'] = 'supported'
    out['limitations'].append('supported covers only audited retained prefixes of supplied cases; no claim over unexecuted orders, no global theorem, no scientific PASS')
    out['limitations'].append('mask values are read from retained initial fields and event patches; upstream audit_case hash binding is relied on, not re-verified')
    if out['audited_prefixes'] and not suffix_split:
        out['limitations'].append('occurrence suffix coincides with profile position on audited actions; this domain cannot separate suffix-based from position-based masks')
    if skipped:
        out['limitations'].append('%d supplied case(s) failed structural screening' % skipped)
    return out
