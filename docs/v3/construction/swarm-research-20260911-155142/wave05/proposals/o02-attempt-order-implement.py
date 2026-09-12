"""Bounded retained-certificate check for the o02 attempt-order obligation.

Obligation: attempt:2/3/4 gap, duplicate and pause precedence under all six
attempt permutations and restart placements; retain visible refusals.

inspect_cases(cases, charge) audits already-executed typed case objects
produced by the unchanged eight-hour checker (c.run_history) and restored
through c.artifact decode. No reducer, guard, inventory or boundary helper
is executed or imported; per-prefix typed states are reconstructed by the
same frozen t.restore used by c.audit_case, and the attempt precedence
chain is reimplemented so no guard function is imported.

Source anchors (unchanged inputs at the packet source commit, all under
experiments/v3/cut-source-overnight unless noted):
- refusal order no-registration > E-PAUSED > duplicate-attempt >
  attempt-gap; success appends one pair and bumps source_revision:
  s_inclusive.py:21-34, s_audit.py attempt branch, batch-06/guard_a.py:22-35,
  batch-06/guard_b.py ordered checks list.
- atomic: literals share that chain then add atomic-position and
  invalid-atomic-start: s_inclusive.py:26-33, batch-06/guard_audit.py.
- attempt/atomic literals are source-handled, never delegated, and the
  journal ledger is independently postconditioned: batch-06/a_domain.py
  source_only, batch-06/a_audit.py ledger clause.
- source-restart is delegated to the unchanged Q reducer, is recorded in
  the invocation mask and advances only the typed incarnation:
  batch-06/a_inclusive.py and batch-06/a_split.py restart branches.
- typed restoration and JSON-safe witness encoding:
  experiments/v3/eight-hour-research-20260910-01a08a22 check.py audit_case
  (t.restore) and artifact.py encode.

Finite audit accounting: charge.take(1) is consumed once per case prefix
before that prefix is inspected; a repeated case consumes again.
audited_prefixes is the exact number of charged prefix inspections. Trace
restoration precedes prefix inspection and is not separately metered.
Charge exhaustion stops the audit, records a limitation and returns
'unproved' with the partial count.
"""
import json
import sys
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECK_DIR = 'experiments/v3/eight-hour-research-20260910-01a08a22'
sys.path.insert(0, str(ROOT / CHECK_DIR))
import check as c

d = c.d
ATTEMPT = ('attempt:', 'atomic:')
RESTART = 'source-restart'
TOKEN = ('cut-source', 'collectorA', 'effectA')
REASONS = ('no-registration', 'E-PAUSED', 'duplicate-attempt', 'attempt-gap', 'ok')
WITNESS_CAP = 100


def _verb(action):
    return action.partition('@')[0]


def _number(verb):
    """Pending-attempt ordinal carried by one literal verb, or None."""
    try:
        if verb.startswith('attempt:'):
            return int(verb.split(':')[1])
        if verb.startswith('atomic:'):
            _, name, offset = verb.split(':')
            return json.loads(d.s.records(name)[int(offset)])['attempt_number']
    except (ValueError, KeyError, IndexError, TypeError):
        pass
    return None


def _pair(number):
    return ('attemptA' if number == 1 else 'retained-attemptA' + str(number),
            'attempt:' + str(number))


def _conditions(view, verb, policy):
    """Refusal conditions active for one attempt verb, in precedence order."""
    number = _number(verb)
    if number is None:
        return None
    attempts = view.get('attempts', ())
    active = []
    if not view.get('registration'):
        active.append('no-registration')
    if view.get('paused'):
        active.append('E-PAUSED')
    if _pair(number) in attempts:
        active.append('duplicate-attempt')
    if number != len(attempts) + 1:
        active.append('attempt-gap')
    if verb.startswith('atomic:') and not active:
        _, name, offset = verb.split(':')
        if policy != 'atomic-start' or int(offset) != len(view.get('append_log', ())):
            active.append('atomic-position')
        elif view.get('registration'):
            record = json.loads(d.s.records(name)[int(offset)])
            original = json.loads(view['registration'])[0]
            fields = ('effect_id', 'idempotency_key', 'payload_digest',
                      'target_ref', 'admission_epoch', 'fence_epoch')
            if (record.get('type') != 'AttemptStarted@1'
                    or record.get('attempt_id') != 'attempt:' + str(number)
                    or any(record.get(f) != original.get(f) for f in fields)):
                active.append('invalid-atomic-start')
    return active


def _racing(actions, requires):
    """Attempt literals in the restart's dependency class (the racing core);
    falls back to the largest requires-equivalence class of attempts."""
    attempts = [a for a in actions if _verb(a).startswith(ATTEMPT)]
    restarts = [a for a in actions if _verb(a) == RESTART]
    group = []
    if restarts:
        need = tuple(sorted(requires.get(restarts[0], ())))
        group = [a for a in attempts if tuple(sorted(requires.get(a, ()))) == need]
    if not group and attempts:
        classes = {}
        for a in attempts:
            classes.setdefault(tuple(sorted(requires.get(a, ()))), []).append(a)
        group = max(classes.values(), key=len)
    return group, restarts


def _incarnation(value):
    return (type(value) is tuple and len(value) == 4 and value[:3] == TOKEN
            and type(value[3]) is int)


def _row_decision(row, *keys):
    for key in keys:
        item = row.get(key)
        if isinstance(item, dict) and 'decision' in item:
            return item['decision']
    return None


def _result(status, observations, limitations, audited):
    return {'status': status, 'observations': observations,
            'limitations': limitations, 'audited_prefixes': audited}


def inspect_cases(cases, charge):
    """Audit restored typed cases; bounded per-prefix, see module docstring."""
    observations, limitations, witnesses = [], [], []
    per_reason, orders_seen, ranks_seen, signatures = {}, set(), set(), set()
    multisets, by_order = set(), {}
    stats = dict(audited=0, malformed=0, restarts=0, paused=0, competitions=0)
    flags = dict(rows_missing=False, unparsed=False, no_racing=False)
    truncated = [False]

    def witness(kind, case=None, prefix=None, action=None, **extra):
        if len(witnesses) < WITNESS_CAP:
            witnesses.append(dict(kind=kind, case=case, prefix=prefix,
                                  action=action, **extra))
        elif not truncated[0]:
            truncated[0] = True
            limitations.append('witness list truncated at %d entries' % WITNESS_CAP)

    def attempt(ci, i, action, verb, s_pre, s_post, a_pre, a_post, row, policy, decisions):
        a_view = dict(a_pre['core'])
        a_view.update(a_pre['journal'])
        active_s = _conditions(s_pre, verb, policy)
        active_a = _conditions(a_view, verb, policy)
        if active_s is None or active_a is None:
            flags['unparsed'] = True
            return
        if active_s != active_a:
            witness('guard-view-condition-mismatch', ci, i, action,
                    source=list(active_s), adapter=list(active_a))
        expected = verb + ':' + (active_s[0] if active_s else 'ok')
        reason = expected.rpartition(':')[2]
        per_reason[reason] = per_reason.get(reason, 0) + 1
        if len(active_s) > 1:
            stats['competitions'] += 1
        observed = dict(source_state=s_post.get('decision'),
                        adapter_state=a_post.get('decision'),
                        source_row=_row_decision(row, 'source_observation'),
                        adapter_row=_row_decision(row, 'adapter_observation', 'target_observation'))
        if observed['source_row'] is None or observed['adapter_row'] is None:
            flags['rows_missing'] = True
        bad = {k: v for k, v in observed.items() if v is not None and v != expected}
        if bad:
            witness('attempt-decision-mismatch', ci, i, action,
                    expected=expected, observed=bad)
        decisions.append(observed['source_state'] if observed['source_state'] is not None else 'unrecorded')
        pair = _pair(_number(verb))
        for side, pre, post in (('source', s_pre, s_post),
                                ('journal', a_pre['journal'], a_post['journal'])):
            if active_s:
                if not (d.exact(post['attempts'], pre['attempts'])
                        and post['source_revision'] == pre['source_revision']):
                    witness('refused-attempt-ledger-drift', ci, i, action, side=side)
            elif not (d.exact(post['attempts'], pre['attempts'] + (pair,))
                      and post['source_revision'] == pre['source_revision'] + 1):
                witness('accepted-attempt-ledger-mismatch', ci, i, action, side=side)

    def restart(ci, i, action, s_pre, s_post, a_pre, a_post, row):
        stats['restarts'] += 1
        generation = s_pre.get('source_generation')
        want = generation[:-1] + (generation[-1] + 1,) if _incarnation(generation) else None
        if want is None:
            witness('restart-untyped-incarnation', ci, i, action)
        else:
            for side, value in (('source', s_post.get('source_generation')),
                                ('journal', a_post['journal'].get('source_generation')),
                                ('core', a_post['core'].get('source_generation'))):
                if not d.exact(value, want):
                    witness('restart-incarnation-mismatch', ci, i, action, side=side,
                            expected=c.artifact.encode(want), observed=c.artifact.encode(value))
        for key in d.s.EXTRA:
            if not d.exact(s_post.get(key), s_pre.get(key)):
                witness('restart-source-ledger-drift', ci, i, action, field=key)
        for key in a_pre['journal']:
            if key != 'source_generation' and not d.exact(a_post['journal'].get(key), a_pre['journal'].get(key)):
                witness('restart-journal-ledger-drift', ci, i, action, field=key)
        if row.get('q_invoked') is not True:
            witness('restart-not-recorded-delegated', ci, i, action,
                    q_invoked=c.artifact.encode(row.get('q_invoked')))
        if a_post.get('invocations', ()) != a_pre.get('invocations', ()) + (action,):
            witness('restart-invocation-mask', ci, i, action)
        if s_post.get('decision') != a_post.get('decision'):
            witness('restart-decision-divergence', ci, i, action)

    try:
        case_list = list(cases)
    except TypeError:
        return _result('not_applicable', [], ['cases is not an iterable of restored case objects'], 0)
    for ci, case in enumerate(case_list):
        try:
            actions = tuple(case['source']['actions'])
            profile = case['source']['profile']
            rows = list(case['rows'])
            ss, aa = c.t.restore(case['source']), c.t.restore(case['adapter'])
            shaped = (len(ss) == len(aa) == len(actions) + 1 and len(rows) == len(actions)
                      and actions == tuple(case['adapter']['actions']))
        except (KeyError, TypeError, IndexError, ValueError, AttributeError):
            shaped = False
        if not shaped:
            stats['malformed'] += 1
            continue
        racing, restarts = _racing(actions, profile.get('requires', {}))
        if not racing:
            flags['no_racing'] = True
        order = tuple(_number(_verb(a)) for a in actions if a in racing)
        multisets.add(tuple(sorted(n for n in order if n is not None)))
        orders_seen.add(order)
        if restarts:
            first = actions.index(restarts[0])
            ranks_seen.add(sum(1 for a in racing if actions.index(a) < first))
            signatures.add(tuple('R' if a in restarts else _number(_verb(a))
                                 for a in actions if a in racing or a in restarts))
            if len(restarts) > 1:
                limitations.append('case %d has %d source-restart occurrences; rank uses the first'
                                   % (ci, len(restarts)))
        decisions, exhausted = [], None
        for i in range(len(actions) + 1):
            try:
                charge.take(1)
            except Exception as error:  # checked counter raises before inspection
                exhausted = 'charge exhausted at case %d prefix %d: %s' % (ci, i, error)
                break
            stats['audited'] += 1
            if ss[i].get('paused') or aa[i]['core'].get('paused'):
                stats['paused'] += 1
            if i == 0:
                continue
            try:
                verb = _verb(actions[i - 1])
                if verb.startswith(ATTEMPT):
                    attempt(ci, i, actions[i - 1], verb, ss[i - 1], ss[i],
                            aa[i - 1], aa[i], rows[i - 1], profile.get('policy'), decisions)
                elif verb == RESTART:
                    restart(ci, i, actions[i - 1], ss[i - 1], ss[i],
                            aa[i - 1], aa[i], rows[i - 1])
            except (KeyError, TypeError, IndexError, ValueError, AttributeError) as error:
                limitations.append('inspection error at case %d prefix %d (%s)' % (ci, i, error))
        by_order.setdefault(order, set()).add(tuple(decisions))
        if exhausted:
            limitations.append(exhausted + '; partial audit retained')
            break
    numbers = next(iter(multisets)) if len(multisets) == 1 else None
    if len(multisets) > 1:
        limitations.append('inconsistent racing-attempt multisets across cases: %s'
                           % sorted(map(list, multisets)))
    expected_orders = {tuple(p) for p in permutations(numbers)} if numbers and len(numbers) <= 4 else None
    complete_orders = False
    if expected_orders is None:
        limitations.append('expected attempt-order domain not enumerable for the observed multiset')
    else:
        missing = sorted(expected_orders - orders_seen)
        complete_orders = not missing
        if missing:
            limitations.append('attempt permutations without retained evidence: %s' % [list(x) for x in missing])
    expected_ranks = set(range(len(numbers) + 1)) if numbers else set()
    complete_ranks = bool(signatures) and numbers is not None and not (expected_ranks - ranks_seen)
    if not signatures:
        limitations.append('no source-restart inside inspected schedules; placement axis untested')
    elif expected_ranks - ranks_seen:
        limitations.append('restart placements without retained evidence: %s' % sorted(expected_ranks - ranks_seen))
    for order, variants in by_order.items():
        if len(variants) > 1:
            witness('order-signature-decision-divergence', order=list(order),
                    variants=sorted(map(list, variants), key=repr))
    claims = {(r + '-precedence' if r != 'ok' else 'attempt-acceptance-order'):
              dict(status='supported' if per_reason.get(r) else 'unproved',
                   observed=per_reason.get(r, 0)) for r in REASONS}
    claims['precedence-ordering-under-competition'] = dict(
        status='supported' if stats['competitions'] else 'unproved', observed=stats['competitions'])
    claims['restart-placement-invariance'] = dict(
        status='supported' if stats['restarts'] and len(witnesses) == 0 else 'unproved',
        observed=stats['restarts'])
    if not per_reason.get('E-PAUSED'):
        limitations.append('paused held in %d audited prefixes; E-PAUSED precedence has no witness' % stats['paused'])
    if not per_reason.get('duplicate-attempt'):
        limitations.append('no duplicate attempt literal in inspected schedules; duplicate precedence has no witness')
    if stats['malformed']:
        limitations.append('%d of %d supplied objects failed typed restore/shape checks' % (stats['malformed'], len(case_list)))
    if flags['rows_missing']:
        limitations.append('some comparison rows lack source/adapter observation decisions; post-state decisions were used')
    if flags['unparsed']:
        limitations.append('some attempt literals had no parseable ordinal and were skipped')
    if flags['no_racing']:
        limitations.append('some cases exposed no racing attempt group')
    status = ('counterexample' if witnesses else
              'not_applicable' if not case_list or stats['malformed'] == len(case_list) else
              'supported' if complete_orders and complete_ranks and all(v['status'] == 'supported' for v in claims.values()) else
              'unproved')
    if witnesses:
        observations.append(dict(kind='counterexample-witnesses', witnesses=witnesses))
    observations.extend([
        dict(kind='decision-reasons', counts=per_reason),
        dict(kind='attempt-orders', observed=sorted(map(list, orders_seen), key=repr),
             expected=sorted(map(list, expected_orders), key=repr) if expected_orders else None,
             complete=complete_orders),
        dict(kind='restart-placements', observed_ranks=sorted(ranks_seen),
             expected_ranks=sorted(expected_ranks), interleave_signatures=len(signatures),
             complete=complete_ranks),
        dict(kind='claims', **claims),
        dict(kind='accounting', cases=len(case_list), inspected=len(case_list) - stats['malformed'],
             audited_prefixes=stats['audited'], restart_events=stats['restarts'],
             paused_prefixes=stats['paused'], precedence_competitions=stats['competitions'])])
    return _result(status, observations, limitations, stats['audited'])
