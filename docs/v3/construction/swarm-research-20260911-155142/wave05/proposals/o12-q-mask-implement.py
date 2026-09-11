"""Bounded retained-certificate check o12-q-mask.

Obligation (bounded, per retained adapter trace prefix): the actual Q invocation list and
the Q core done-mask must contain exactly the fixed subprofile positions of actually
delegated calls -- no source-handled action may appear, each delegated call sets exactly
its own subprofile bit, and a guard-refused source-attest keeps its subprofile position
absent from both the invocation tuple and the mask. A call delegated but refused by Q
itself still occupies its position; only non-delegated steps leave the mask unchanged.

Source anchors (unchanged originals; this module imports none of them):
- experiments/v3/cut-source-overnight/batch-06/a_domain.py source_only/subprofile: verbs
  starting register:/attempt:/atomic:/append:/collect:/source: plus append-lose-reply and
  collect-open are source-handled; all other actions, including source-attest and
  source-restart, are potential Q calls in fixed profile order.
- experiments/v3/cut-source-overnight/batch-06/a_audit.py:17-34: invocations accumulate
  exactly the delegated calls; core['done'] equals the bitmask over subprofile indices of
  that tuple; a non-delegated step leaves the whole Q core typed-unchanged.
- experiments/v3/cut-source-overnight/batch-06/adapter_traces.py:54-75: retained replay
  shape -- core/journal patch field-wise, other fields replace, sha256 binds each step,
  and the outer done-mask indexes the FULL profile while the Q mask indexes the subprofile.
- guard_a.py/guard_b.py source-attest refusals (no-captured-source, stale-collection,
  incomplete-inventory, incomplete-registry) never reach Q; boundary-01 predicts exactly
  these refusals per subclass (boundary.py attestation_observation).
- Representation mirrors semantic.typed/exact (batch-05/semantic.py) and the canonical-JSON
  sha256 used by s_audit.encoded / guard_audit.encoded (sort_keys, compact separators).

Finite audit accounting: charge.take(1) is taken exactly once before each (case, prefix)
inspection slot -- one slot per adapter trace prefix including prefix 0; a structurally
uninspectable case consumes exactly one slot. audited_prefixes equals the number of take
calls issued. No reducer, guard, or audit relation is executed: only retained event
patches are replayed and recorded facts recomputed, so every emitted witness is a
falsifiable expected-vs-observed pair.
"""
import copy
import hashlib
import json

SOURCE_PREFIXES = ('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:')
SOURCE_ACTIONS = ('append-lose-reply', 'collect-open')
ADAPTER_FRAME = ('core', 'journal', 'done', 'decision', 'invocations')
MAX_FAILURES = 8


def _verb(a):
    return a.split('@', 1)[0]


def _source_only(a):
    k = _verb(a)
    return k.startswith(SOURCE_PREFIXES) or k in SOURCE_ACTIONS


def _canon(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'))


def _digest(v):
    return hashlib.sha256(_canon(v).encode('utf-8')).hexdigest()


def _typed(x):
    if isinstance(x, dict):
        return ['dict', [[k, _typed(v)] for k, v in sorted(x.items())]]
    if isinstance(x, (list, tuple)):
        return [type(x).__name__, [_typed(v) for v in x]]
    return [type(x).__name__, x]


def _fail(res, i, check, expected, observed):
    res['failure_count'] += 1
    if len(res['failures']) < MAX_FAILURES:
        res['failures'].append({'prefix': i, 'check': check,
                                'expected': expected, 'observed': observed})


def _structure(case):
    if not isinstance(case, dict):
        return {'malformed': 'case object is not a dict'}
    adapter, rows = case.get('adapter'), case.get('rows')
    if not isinstance(adapter, dict) or not isinstance(rows, list):
        return {'malformed': 'missing adapter trace or comparison rows'}
    missing = [k for k in ('initial', 'profile', 'q_profile', 'actions', 'events')
               if k not in adapter]
    if missing:
        return {'malformed': 'adapter trace missing ' + ','.join(missing)}
    profile, qprofile = adapter['profile'], adapter['q_profile']
    actions, events = adapter['actions'], adapter['events']
    problems = []
    if not (len(actions) == len(events) == len(rows)):
        problems.append('action/event/row inventory mismatch')
    if len(set(actions)) != len(actions) or set(actions) != set(profile.get('actions', ())):
        problems.append('schedule is not a permutation of unique profile actions')
    qp = tuple(qprofile.get('actions', ()))
    if qp != tuple(a for a in profile['actions'] if not _source_only(a)):
        problems.append('retained q_profile actions != recomputed subprofile')
    if qprofile.get('requires') != {a: () for a in qp}:
        problems.append('retained q_profile requires != fixed empty mapping')
    return {'problems': problems, 'profile': profile, 'qp': qp, 'actions': actions,
            'events': events, 'rows': rows, 'initial': adapter['initial']}


def _apply(env, current, executed, action, event, res, i):
    positions = env['profile']['actions']
    if event.get('action') != action:
        _fail(res, i, 'event-action', action, _canon(event.get('action')))
    if action in executed:
        _fail(res, i, 'literal-occurrence', 'first occurrence', action)
    need = env['profile'].get('requires', {}).get(action)
    if need is None or not set(need) <= set(executed):
        _fail(res, i, 'outer-requires', 'declared dependencies met', _canon(need))
    if _digest(current) != event.get('before_sha256'):
        _fail(res, i, 'prestate-binding', event.get('before_sha256'), _digest(current))
    nxt = copy.deepcopy(current)
    for k, v in event.get('patch', {}).items():
        if k in ('core', 'journal') and isinstance(nxt.get(k), dict):
            nxt[k].update(v)
        else:
            nxt[k] = v
    executed.append(action)
    if _digest(nxt) != event.get('after_sha256'):
        _fail(res, i, 'poststate-binding', event.get('after_sha256'), _digest(nxt))
    outer = 0
    for a in executed:
        if a in positions:
            outer |= 1 << positions.index(a)
    if nxt.get('done') != outer:
        _fail(res, i, 'outer-done-mask', outer, nxt.get('done'))
    return nxt


def _mask_checks(env, current, prev, executed, i, res, totals):
    qp, positions = env['qp'], env['profile']['actions']
    raw = current.get('invocations')
    if not isinstance(raw, (list, tuple)):
        _fail(res, i, 'invocations-type', 'tuple of action literals', _canon(raw))
        return
    inv = tuple(raw)
    core = current.get('core')
    done = core.get('done') if isinstance(core, dict) else None
    outsiders = [a for a in inv if a not in qp]
    if outsiders:
        _fail(res, i, 'delegated-calls-only', 'invocations within subprofile', _canon(outsiders))
    if len(set(inv)) != len(inv):
        _fail(res, i, 'invocation-distinct', 'unique calls', _canon(inv))
    if tuple(a for a in executed if a in set(inv)) != inv:
        _fail(res, i, 'invocation-order', 'executed-order filtered', _canon(inv))
    expected = 0
    for a in inv:
        if a in qp:
            expected |= 1 << qp.index(a)
    res['final_expected_mask'], res['final_core_done'] = expected, done
    if done != expected:
        _fail(res, i, 'q-done-mask-subprofile', expected, done)
    elif any(qp.index(a) != positions.index(a) for a in inv):
        res['discriminating'] += 1
    if prev is None:
        return
    action, row = env['actions'][i - 1], env['rows'][i - 1]
    prev_inv = tuple(prev['invocations'])
    kept = inv[:len(prev_inv)] == prev_inv
    delta = inv[len(prev_inv):] if kept else inv
    if not kept:
        _fail(res, i, 'invocation-prefix', 'prior invocations preserved', _canon(inv))
    elif delta not in ((), (action,)):
        _fail(res, i, 'invocation-delta', '() or (' + action + ',)', _canon(delta))
    invoked = kept and delta == (action,)
    want = {'index': i - 1, 'source_action': action, 'adapter_action': action}
    if {k: row.get(k) for k in want} != want:
        _fail(res, i, 'row-identity', _canon(want), _canon({k: row.get(k) for k in want}))
    if bool(row.get('q_invoked')) != invoked:
        _fail(res, i, 'q-invoked-flag', bool(row.get('q_invoked')), invoked)
    obs = row.get('adapter_observation')
    decision = obs.get('decision') if isinstance(obs, dict) else None
    visible = decision if decision is not None else current.get('decision')
    if decision is not None and decision != current.get('decision'):
        _fail(res, i, 'visible-decision', decision, current.get('decision'))
    prev_core = prev.get('core')
    prev_done = prev_core.get('done') if isinstance(prev_core, dict) else None
    if invoked:
        res['delegated'] += 1
        if action not in qp:
            _fail(res, i, 'delegated-membership', 'subprofile member', action)
        elif not isinstance(prev_done, int) or prev_done & (1 << qp.index(action)) \
                or done != prev_done | (1 << qp.index(action)):
            _fail(res, i, 'mask-transition', 'set subprofile bit ' + str(qp.index(action)),
                  _canon({'prev': prev_done, 'done': done}))
    else:
        res['nondelegated'] += 1
        if done != prev_done:
            _fail(res, i, 'mask-stable-refusal', prev_done, done)
        if _typed(core) != _typed(prev_core):
            _fail(res, i, 'core-unchanged-refusal', 'typed-equal Q core', 'diverged')
    if _verb(action) != 'source-attest':
        return
    sobs = row.get('source_observation')
    entry = {'event_index': i - 1, 'prefix': i, 'action': action, 'invoked': invoked,
             'adapter_decision': visible,
             'source_decision': sobs.get('decision') if isinstance(sobs, dict) else None,
             'subprofile_position': qp.index(action) if action in qp else None,
             'mask_bit_set': bool(done & (1 << qp.index(action)))
             if action in qp and isinstance(done, int) else None}
    res['attest_witnesses'].append(entry)
    if invoked:
        totals['attest_invoked_accepted' if visible == 'source-attest:ok'
               else 'attest_invoked_refused'] += 1
    else:
        if visible == 'source-attest:ok':
            _fail(res, i, 'refusal-visibility', 'guard refusal decision', visible)
        totals['attest_refused_absent'] += 1


def _inspect_case(case, charge, totals):
    res = {'case': case.get('case') if isinstance(case, dict) else None, 'audited': 0,
           'failures': [], 'failure_count': 0, 'malformed': None, 'attest_witnesses': [],
           'discriminating': 0, 'delegated': 0, 'nondelegated': 0,
           'final_expected_mask': None, 'final_core_done': None}
    try:
        n = len(case['adapter']['actions']) + 1
    except (KeyError, TypeError, AttributeError):
        n = 1
    env, current, prev, executed = None, None, None, []
    for i in range(n):
        charge.take(1)
        res['audited'] += 1
        try:
            if i == 0:
                env = _structure(case)
                if 'malformed' in env:
                    res['malformed'] = env['malformed']
                    break
                for p in env['problems']:
                    _fail(res, 0, 'trace-structure', 'consistent retained inventory', p)
                init = env['initial']
                if not isinstance(init, dict) or sorted(init) != sorted(ADAPTER_FRAME):
                    _fail(res, 0, 'adapter-frame', _canon(ADAPTER_FRAME),
                          _canon(sorted(init) if isinstance(init, dict) else init))
                    break
                if init['done'] != 0 or init['invocations'] != () \
                        or init['core'].get('done') != 0:
                    _fail(res, 0, 'initial-masks', 'done=0 core.done=0 invocations=()',
                          _canon({'done': init['done'], 'core_done': init['core'].get('done'),
                                  'invocations': init['invocations']}))
                current = copy.deepcopy(init)
            else:
                prev = current
                current = _apply(env, current, executed, env['actions'][i - 1],
                                 env['events'][i - 1], res, i)
            _mask_checks(env, current, prev, executed, i, res, totals)
        except (KeyError, TypeError, IndexError, AttributeError, ValueError) as e:
            _fail(res, i, 'inspection-error', 'typed retained case fields', repr(e))
            if env is None:
                break
    return res


def inspect_cases(cases, charge):
    """Audit retained case objects for the o12 Q invocation/mask subprofile obligation."""
    totals = {'attest_refused_absent': 0, 'attest_invoked_refused': 0,
              'attest_invoked_accepted': 0}
    if not isinstance(cases, (list, tuple)) or not cases:
        return {'status': 'not_applicable', 'observations': [], 'audited_prefixes': 0,
                'limitations': ['no retained case objects supplied; nothing inspected']}
    observations, limitations, results, audited = [], [], [], 0
    for case in cases:
        res = _inspect_case(case, charge, totals)
        audited += res['audited']
        results.append(res)
        obs = {'case': res['case'], 'audited_prefixes': res['audited'],
               'charge_take_calls': res['audited'], 'delegated_calls': res['delegated'],
               'nondelegated_steps_core_unchanged': res['nondelegated'],
               'mask_discriminating_prefixes': res['discriminating'],
               'source_attest_witnesses': res['attest_witnesses'],
               'failure_count': res['failure_count'],
               'final_expected_mask': res['final_expected_mask'],
               'final_core_done': res['final_core_done']}
        if res['malformed']:
            obs['malformed'] = res['malformed']
        if res['failures']:
            obs['first_failures'] = res['failures']
        observations.append(obs)
    malformed = sum(1 for r in results if r['malformed'])
    failures = sum(r['failure_count'] for r in results)
    delegated = sum(r['delegated'] for r in results)
    discriminating = sum(r['discriminating'] for r in results)
    observations.insert(0, {'accounting': {
        'cases': len(results), 'inspectable_cases': len(results) - malformed,
        'charge_take_calls': audited, 'delegated_calls': delegated,
        'refused_absent_source_attest': totals['attest_refused_absent'],
        'invoked_refused_source_attest': totals['attest_invoked_refused'],
        'invoked_accepted_source_attest': totals['attest_invoked_accepted'],
        'mask_discriminating_prefixes': discriminating, 'total_failures': failures}})
    if failures:
        status = 'counterexample'
    elif malformed == len(results):
        status = 'unproved'
    elif delegated == 0 or totals['attest_refused_absent'] == 0:
        status = 'unproved'
    else:
        status = 'supported'
    if malformed:
        limitations.append(str(malformed) + ' supplied case object(s) structurally uninspectable')
    limitations.append('supported is bounded to supplied retained prefixes; it is not a '
                       'reachability, all-orders, or scientific-acceptance claim')
    limitations.append('no reducer, guard, or audit relation executed; delegation truth '
                       'comes from retained invocation deltas cross-checked against stored rows')
    if not totals['attest_refused_absent']:
        limitations.append('no guard-refused (absent) source-attest prefix in supplied '
                           'cases; that clause unwitnessed')
    if not delegated:
        limitations.append('no delegated Q call exercised by the supplied cases')
    if not discriminating:
        limitations.append('no inspected prefix separates subprofile from outer-profile '
                           'indexing; position-space discrimination unwitnessed')
    limitations.append('digest/typed representations mirror the unchanged canonical-JSON '
                       'and semantic.typed encodings anchored in the docstring')
    return {'status': status, 'observations': observations,
            'limitations': limitations, 'audited_prefixes': audited}
