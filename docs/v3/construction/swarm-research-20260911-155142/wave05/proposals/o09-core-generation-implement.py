"""Bounded retained-certificate check (obligation o09-core-generation).

Question: does the live Q-core ``source_generation`` (``adapter['core']``) stay
exactly coupled to the shadowing adapter journal generation
(``adapter['journal']``) and to the source authority's own field, through the
fixed setup prefix, the single core-window ``source-restart`` and the
delivery/attestation suffix, on retained typed ``c.run_history`` /
``c.audit_case`` restored case objects?

Candidate coupling invariant, verified per audited prefix i (never assumed):

    source_gen[i] == journal_gen[i] == ('cut-source','collectorA','effectA',R_i)
    core_gen[i]   == journal_gen[i]

where R_i counts effective ``source-restart`` actions among the first i actions
(source side: decision ``source-restart:ok``; adapter side: ``q_invoked`` and
``source-restart:ok``). The literal core/journal equality is conditional: a
first successful delegated ``source-attest`` assigns the Q core
``source_token(1)`` outright while the journal only ever advances on delegated
restarts and stores the captured serial inside ``attestation[0]``. The
refused-attestation subclasses exercise exactly the refusal regime in which
literal equality must hold.

Method: per-prefix states are rebuilt solely from the retained event patches of
each trace; every step is re-bound to the recorded ``before_sha256`` /
``after_sha256`` digests, the visible completion mask and the actual-Q
invocation mask. Retained comparison rows (state digests, ``q_invoked``,
``differing_journal_fields``) are re-checked against the rebuilt states. The
captured serial inside ``collection[0]``/``attestation[0]`` is re-bound to the
restart serial live at the retained ``collect-open``. No reducer, guard,
boundary or inventory function is imported or executed; the only domain import
is the unchanged ``semantic`` representation module (``exact``/``token``/
``digest``). ``charge.take(1)`` is taken exactly once before each (case,
prefix) inspection; every repetition is charged again. ``audited_prefixes``
counts all inspected prefixes.

Source anchors (unchanged files, consulted for meaning/representation only):
  a_inclusive.py:10,16 ; a_split.py:8,15,19 ; a_audit.py:16,24,27
      journal serial preserved across calls, +1 only on a delegated restart.
  q_inclusive.py:10,19 ; q_split.py:10,16
      core serial +1 on restart; literal token(1) on first attestation.
  s_inclusive.py:64-69   S attestation leaves ``source_generation`` unchanged.
  semantic.py:22,44-49   typed incarnation token; paired restart binding.
  boundary.py            prefix_census generation fields are the retained facts
                         re-verified here.
"""

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel

exact, token, digest = rel.exact, rel.token, rel.digest
JOURNAL_FIELDS = tuple(rel.s.EXTRA) + ('source_generation',)
NS = ('cut-source', 'collectorA', 'effectA')
RESTART, ATTEST, OPEN = 'source-restart', 'source-attest', 'collect-open'
MAX_WITNESSES, MAX_VIOLATIONS, MAX_FAULTS = 8, 64, 8


class Integrity(Exception):
    """Retained-certificate inconsistency; never a state-space verdict."""


class BudgetExceeded(Exception):
    """Charged prefix budget exhausted mid-case; audit is partial."""


def verb(action):
    return action.partition('@')[0]


def replay(trace):
    """Rebuild per-prefix states from retained patches, bound by digests/masks."""
    actions, events = trace['actions'], trace['events']
    if len(events) != len(actions):
        raise Integrity('event inventory does not cover every literal action')
    requires, order = trace['profile']['requires'], trace['profile']['actions']
    states = [copy.deepcopy(trace['initial'])]
    for index, (action, event) in enumerate(zip(actions, events)):
        if event['action'] != action or set(requires[action]) - set(actions[:index]):
            raise Integrity('literal occurrence or outer dependency broken')
        if digest(states[-1]) != event['before_sha256']:
            raise Integrity('prestate digest binding broken')
        nxt = copy.deepcopy(states[-1])
        for key, value in event['patch'].items():
            if trace['side'] == 'adapter' and key in ('core', 'journal'):
                nxt[key].update(value)
            else:
                nxt[key] = value
        if digest(nxt) != event['after_sha256']:
            raise Integrity('poststate digest binding broken')
        if nxt['done'] != sum(1 << order.index(a) for a in actions[:index + 1]):
            raise Integrity('visible completion mask mismatch')
        if trace['side'] == 'adapter':
            q_actions = trace['q_profile']['actions']
            if nxt['core']['done'] != sum(1 << q_actions.index(a) for a in nxt['invocations']):
                raise Integrity('actual Q invocation mask mismatch')
        states.append(nxt)
    return states


def inspect_case(case, charge, account):
    """Audit one restored case; return (summary, violations)."""
    source_trace, adapter_trace, rows = case['source'], case['adapter'], case['rows']
    if source_trace['side'] != 'source' or adapter_trace['side'] != 'adapter':
        raise Integrity('trace sides mislabeled')
    if list(source_trace['actions']) != list(adapter_trace['actions']):
        raise Integrity('visible literal histories differ')
    actions = list(source_trace['actions'])
    if len(rows) != len(actions):
        raise Integrity('comparison rows do not cover every action')
    sources, adapters = replay(source_trace), replay(adapter_trace)
    serial = {'source': 0, 'journal': 0, 'core': 0}
    open_serial = {'source': None, 'journal': None}
    witnesses, refusals, violations = [], [], []
    restart_index = attest_index = first_break = None
    collection_bound = attestation_bound = None
    for i in range(len(actions) + 1):
        try:
            charge.take(1)
        except Exception as error:
            raise BudgetExceeded(repr(error))
        account['prefixes'] += 1
        s_state, a_state = sources[i], adapters[i]
        observed = {'source': s_state['source_generation'],
                    'core': a_state['core']['source_generation'],
                    'journal': a_state['journal']['source_generation']}
        if not all(token(g) for g in observed.values()):
            raise Integrity('non-token live incarnation in retained state')
        expected = {k: NS + (serial[k],) for k in serial}
        hold = all(exact(observed[k], expected[k]) for k in expected)
        for name in expected:
            if not exact(observed[name], expected[name]):
                violations.append(dict(case=case['case'], prefix=i, field=name,
                                       expected=expected[name], observed=observed[name]))
        if not exact(observed['core'], observed['journal']):
            violations.append(dict(case=case['case'], prefix=i, field='core==journal',
                                   expected=expected['journal'], observed=observed['core']))
        if not hold and first_break is None:
            first_break = i
        for side, ledger in (('source', s_state), ('journal', a_state['journal'])):
            for field in ('collection', 'attestation'):
                value = ledger[field]
                if not value:
                    continue
                bound = open_serial[side] is not None and exact(value[0], NS + (open_serial[side],))
                if field == 'collection':
                    collection_bound = bound if collection_bound is not False else False
                else:
                    attestation_bound = bound if attestation_bound is not False else False
                if not bound and first_break is None:
                    first_break = i
        notable = (not hold) or i in (0, len(actions)) or \
            (i > 0 and verb(actions[i - 1]) in (RESTART, ATTEST, OPEN))
        if notable and len(witnesses) < MAX_WITNESSES:
            witnesses.append(dict(prefix=i, expected=expected, observed=observed,
                                  core_equals_journal=exact(observed['core'], observed['journal'])))
        if i == len(actions):
            break
        row, action = rows[i], actions[i]
        post_s, post_a = sources[i + 1], adapters[i + 1]
        if row['index'] != i or row['source_action'] != action or row['adapter_action'] != action:
            raise Integrity('chronological row binding broken')
        if row['source_sha256'] != digest(post_s) or row['adapter_sha256'] != digest(post_a):
            raise Integrity('row state digests disagree with rebuilt poststates')
        if len(post_a['invocations']) - len(a_state['invocations']) != (1 if row['q_invoked'] else 0):
            raise Integrity('retained q_invoked flag contradicts invocation mask')
        if row['q_invoked'] and post_a['invocations'][-1] != action:
            raise Integrity('invocation inventory tail mismatch')
        diff = sorted(k for k in JOURNAL_FIELDS if not exact(post_s[k], post_a['journal'][k]))
        if sorted(row['differing_journal_fields']) != diff:
            raise Integrity('retained differing journal fields disagree with rebuild')
        if 'prefixes' in case and \
                sorted(case['prefixes'][i + 1]['differing_journal_fields']) != diff:
            raise Integrity('prefix certificate journal fields disagree')
        v = verb(action)
        s_dec, a_dec = row['source_observation']['decision'], row['adapter_observation']['decision']
        if v == RESTART:
            restart_index = i
            serial['source'] += s_dec == 'source-restart:ok'
            bumped = bool(row['q_invoked'] and a_dec == 'source-restart:ok')
            serial['journal'] += bumped
            serial['core'] += bumped
        elif v == OPEN:
            if s_dec == 'collect-open:ok':
                open_serial['source'] = serial['source']
            if a_dec == 'collect-open:ok':
                open_serial['journal'] = serial['journal']
        elif v == ATTEST:
            attest_index = i
            if a_dec != 'source-attest:ok':
                refusals.append(dict(index=i, decision=a_dec, q_invoked=bool(row['q_invoked'])))
            elif row['q_invoked'] and not a_state['core']['source_name']:
                serial['core'] = 1
    summary = dict(case=case['case'], prefixes=len(actions) + 1,
                   restart_index=restart_index, attest_index=attest_index,
                   attestation_refusals=refusals,
                   attestation_delegated_success=bool(attest_index is not None and not refusals),
                   coupling_holds=first_break is None, first_break_prefix=first_break,
                   collection_serial_bound=collection_bound,
                   attestation_serial_bound=attestation_bound, witnesses=witnesses)
    return summary, violations


def inspect_cases(cases, charge):
    """Bounded retained-certificate audit API; returns a JSON-safe dict."""
    result = dict(status='unproved', observations=[], limitations=[], audited_prefixes=0)
    if isinstance(cases, dict) and {'source', 'adapter', 'rows'} <= set(cases):
        cases = [cases]
    if not isinstance(cases, (list, tuple)) or not cases:
        result['status'] = 'not_applicable'
        result['observations'].append(dict(reason='no restored typed case objects supplied'))
        return result
    account = {'prefixes': 0}
    violations, faults = [], []
    recognized = audited = 0
    restart_seen = attest_seen = False
    halted = None
    for case in cases:
        if not isinstance(case, dict) or not {'case', 'source', 'adapter', 'rows'} <= set(case):
            continue
        recognized += 1
        try:
            summary, found = inspect_case(case, charge, account)
        except BudgetExceeded as error:
            halted = 'charged prefix budget exhausted: ' + str(error)
            break
        except Exception as error:
            faults.append('case ' + repr(case.get('case')) + ': ' + repr(error))
            continue
        violations.extend(found[:max(0, MAX_VIOLATIONS - len(violations))])
        restart_seen |= summary['restart_index'] is not None
        attest_seen |= summary['attest_index'] is not None
        result['observations'].append(summary)
        audited += 1
    result['audited_prefixes'] = account['prefixes']
    if violations:
        result['status'] = 'counterexample'
        result['observations'].append(dict(counterexample_witnesses=violations))
    elif not recognized:
        result['status'] = 'not_applicable'
    elif halted or faults or not audited or not restart_seen or not attest_seen:
        result['status'] = 'unproved'
    else:
        result['status'] = 'supported'
    result['observations'].insert(0, dict(
        identified_invariant=('per audited prefix i: journal.source_generation == '
                              'core.source_generation == source.source_generation == '
                              "('cut-source','collectorA','effectA',R_i), R_i the count of "
                              'effective source-restart actions in the first i actions'),
        conditional_boundary=('literal core/journal equality requires attestation refusal; '
                              'a first successful delegated source-attest assigns the Q core '
                              'token(1) while the journal keeps its restart-only serial'),
        cases_recognized=recognized, cases_audited=audited,
        restart_witnessed=restart_seen, attestation_witnessed=attest_seen))
    result['limitations'] = [
        'audit is confined to the supplied restored cases; no reachability or all-order claim',
        'equality claim is the conditional invariant above, not an unconditional identity',
        'expected serials derive from retained decisions and invocation masks, never re-execution',
        'partial audits, integrity faults or vacuous coverage yield unproved',
        'not a global theorem and not scientific acceptance']
    if halted:
        result['limitations'].append(halted)
    result['limitations'].extend(faults[:MAX_FAULTS])
    return result
