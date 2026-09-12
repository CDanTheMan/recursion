"""Bounded retained-certificate check for obligation o21-reconcile-current.

Obligation: reconcile selected-source currentness and Q state coupling; exact
retained refusal/outer response in the original scale suffix.  This inspector
consumes restored typed case objects produced by the unchanged eight-hour
checker (c.run_history / c.artifact decode).  It executes no reducer, guard or
model, imports nothing, and never mutates its inputs; every verdict is a finite
per-prefix observation over actual retained fields.

Finite audit accounting: charge.take(1) is issued exactly once before any
inspection of each case prefix, including repeated case objects; total charge
equals the sum over cases of len(actions)+1, and an exhausted charge aborts
inspection by propagation.  Remaining work is bounded by retained state size
per prefix; there is no other accounting unit.

Source anchors (representation reference only; this module imports nothing):
- s_domain.py add_with_suffix 'scale-eight-action-race' and boundary-01
  spec.json: fixed prefix 0..10, antichain core 11..18, fixed suffix 19..33.
- s_inclusive.py / s_split.py / s_audit.py: source-attest refusal precedence
  no-captured-source -> stale-collection -> incomplete-inventory ->
  incomplete-registry; 'source-boundary-stale' guard on fresh publication and
  reconcile; delegated-frame staged_source/selected_source ledger updates.
- batch-06/guard_a.py, guard_b.py, guard_audit.py: the same refusal order over
  the journal-overlaid guard view; guard refusals return delegate=False.
- batch-06/a_domain.py source_only/subprofile/view; batch-06/a_audit.py:
  refused or source-handled calls leave the entire Q core unchanged and Q
  completion equals exactly the actual invocation mask.
- batch-05/semantic.py typed() representation; batch-06/adapter_traces.py
  comparison rows, the journal mirror over (*s_domain.EXTRA,
  'source_generation') and the responses_related definition.
- boundary.py prefix_census: per-prefix source/journal/Q-core generation
  coupling fields independently recomputed here.

Status values: 'counterexample' on a concrete expected/observed mismatch,
'unproved' when retained evidence cannot decide, 'supported' only for
non-vacuous audited coverage with every applicable check passing, and
'not_applicable' when no cases are supplied.  Nothing here is a global theorem
or an accepted scientific PASS; unaudited orders remain uncovered.
"""

EXTRA = ('registration', 'attempts', 'append_log', 'append_receipts',
         'append_reply', 'source_revision', 'collection', 'collected',
         'attestation', 'staged_source', 'selected_source')
JOURNAL_FIELDS = EXTRA + ('source_generation',)
PUB = ('pub-commit', 'pub-rival', 'pub-retry', 'pub-retry-conflict',
       'pub-retry-foreign')
GUARD_VERBS = ('source-attest', 'reconcile') + PUB
SUFFIX_START = 19
FREE = frozenset(('attempt:2@15', 'attempt:3@16', 'attempt:4@17',
                  'source-restart@18'))
COLLECTS = frozenset(('collect:0@12', 'collect:1@13', 'collect:2@14'))
CORE_SET = FREE | COLLECTS | frozenset(('collect-open@11',))


def typed(x):
    if isinstance(x, dict):
        return ['dict', [[k, typed(v)] for k, v in sorted(x.items())]]
    if isinstance(x, (list, tuple)):
        return [type(x).__name__, [typed(v) for v in x]]
    return [type(x).__name__, x]


def exact(a, b):
    return typed(a) == typed(b)


def safe(x):
    if type(x).__name__ == 'Envelope':
        return {'Envelope': {f: safe(getattr(x, f)) for f in x._fields}}
    if isinstance(x, dict):
        return {str(k): safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [safe(v) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return repr(x)


def verb(action):
    return action.split('@')[0]


def source_only(action):
    k = verb(action)
    return (k.startswith(('register:', 'attempt:', 'atomic:', 'append:',
                          'collect:', 'source:'))
            or k in ('append-lose-reply', 'collect-open'))


def restore(trace, adapter):
    states = [trace['initial']]
    for event in trace['events']:
        prev = states[-1]
        nxt = dict(prev)
        for key, value in event['patch'].items():
            base = prev.get(key)
            if adapter and key in ('core', 'journal') and isinstance(base, dict) and isinstance(value, dict):
                merged = dict(base)
                merged.update(value)
                nxt[key] = merged
            else:
                nxt[key] = value
        states.append(nxt)
    return states


def structural(case):
    if not isinstance(case, dict):
        return 'case is not a dict'
    for key in ('source', 'adapter', 'rows'):
        if not isinstance(case.get(key), (dict, list)):
            return 'missing ' + key
    source, adapter = case['source'], case['adapter']
    for key in ('initial', 'events', 'actions', 'profile'):
        if key not in source or key not in adapter:
            return 'trace missing ' + key
    if 'core' not in adapter['initial'] or 'journal' not in adapter['initial'] or 'invocations' not in adapter['initial']:
        return 'adapter initial state lacks core/journal/invocations'
    if tuple(source['actions']) != tuple(adapter['actions']):
        return 'source/adapter action inventories differ'
    profile_actions = tuple(source['profile']['actions'])
    if set(profile_actions) != set(source['actions']) or len(profile_actions) != len(source['actions']):
        return 'executed actions are not a permutation of the profile inventory'
    n = len(source['actions'])
    if len(source['events']) != n or len(adapter['events']) != n:
        return 'event inventory incomplete'
    if len(case['rows']) != n:
        return 'comparison row inventory incomplete'
    if 'prefixes' in case and len(case['prefixes']) != n + 1:
        return 'prefix inventory incomplete'
    return None


def subclass(actions):
    middle = tuple(actions[11:19])
    if len(middle) != 8 or frozenset(middle) != CORE_SET:
        return None
    if middle[0] == 'collect:0@12' and middle[5] == 'collect-open@11' and frozenset(middle[1:5]) == FREE and frozenset(middle[6:]) == COLLECTS - {'collect:0@12'}:
        return 'fresh-incomplete'
    if middle[0] == 'collect-open@11' and frozenset(middle[1:5]) == FREE and frozenset(middle[5:]) == COLLECTS:
        return 'stale-complete'
    return 'other'


def attest_expectation(core, journal):
    capture = journal.get('collection')
    if not capture or not core.get('cut_delivery'):
        return 'no-captured-source'
    if not exact(capture[:2], (journal['source_generation'], journal['source_revision'])):
        return 'stale-collection'
    collected = journal['collected']
    indices = sorted(i for i, _ in collected)
    log = journal['append_log']
    complete = (len(collected) == capture[4] and indices == list(range(capture[4]))
                and all(0 <= i < len(log) and exact(raw, log[i]) for i, raw in collected))
    if not complete:
        return 'incomplete-inventory'
    return None


def suffix_expectation(action, adapter):
    """(expected decision, expected q_invoked); None means undecidable here."""
    k = verb(action)
    core, journal = adapter['core'], adapter['journal']
    if k == 'source-attest':
        reason = attest_expectation(core, journal)
        return (k + ':' + reason, False) if reason else (None, None)
    if k in PUB:
        if core.get('publication_receipts'):
            return (None, None)
        live = (journal['source_generation'], journal['source_revision'])
        att = journal['attestation']
        if not att or not exact(att[:2], live) or not exact(journal['staged_source'], att):
            return (k + ':source-boundary-stale', False)
        return (None, True)
    if k == 'reconcile':
        sel = journal['selected_source']
        if not sel or not exact(sel[:2], (journal['source_generation'], journal['source_revision'])):
            return (k + ':source-boundary-stale', False)
        return (None, True)
    if k.startswith('reader-'):
        return (k + ':' + reader_expectation(core, k) if reader_expectation(core, k) else None, True)
    return (None, True)


def reader_expectation(core, key):
    name, slot = key.split(':')
    i = int(slot)
    pins = core.get('reader_pins') or ((), ())
    requests = core.get('reader_requests') or ((), ())
    waited = core.get('reader_waited') or (False, False)
    copies = core.get('reader_copies') or ((), ())
    nonces = core.get('reader_nonce') or (1, 1)
    selected = core.get('selected')
    if i >= len(pins):
        return None
    owner, pin = ('reader' + slot, nonces[i]), pins[i]
    if name == 'reader-request':
        return None if selected else 'no-selection'
    if name == 'reader-pin':
        if not requests[i] or pin:
            return 'no-fresh-request'
        if not exact(requests[i][0], owner):
            return 'stale-reader'
        if not exact(requests[i][1], selected):
            return 'stale-selection'
        return None if any(exact(row[0], requests[i][1]) for row in core.get('publication_store', ())) else 'retired'
    if name in ('reader-copy', 'reader-wait', 'reader-release'):
        if not pin or not exact(pin[0], owner):
            return 'no-owned-pin'
        if name == 'reader-wait':
            return None
        if name == 'reader-release':
            return None if waited[i] else 'reader-live'
        return None if any(exact(row[0], pin[1]) for row in core.get('publication_store', ())) else 'retired'
    if name == 'reader-release-foreign':
        return 'no-owned-pin'
    if name in ('reader-install', 'reader-install-corrupt'):
        return None if copies[i] else 'no-copy'
    return None


def inspect_cases(cases, charge):
    limitations = [
        'attestation registry bytes (collection[2:4] versus fixture registration/mapping) are not recomputed: fixture data requires the unchanged domain module and this inspector imports nothing',
        'retained-duplicate publication expectations are decided only when core publication_receipts is empty; the duplicate path needs q_domain.incoming()',
        'trace before/after sha256 bindings are not recomputed (no hashing without imports); prefix states are reconstructed solely by applying retained event patches',
        'the semantic incarnation-pair field relation on common fields is not recomputed; journal mirror and generation checks use strict typed equality',
        'publication_reply pair relation is not recomputed; only definite divergences are flagged',
    ]
    if not cases:
        return {'status': 'not_applicable', 'observations': ['no restored case objects supplied'],
                'limitations': limitations, 'audited_prefixes': 0}
    observations, mismatches, undecided_guard = [], [], []
    audited = structural_failures = decided_refusals = 0
    suffix_cases = 0
    subclasses = set()
    for position, case in enumerate(cases):
        label = case.get('case') if isinstance(case, dict) else None
        label = label if isinstance(label, str) else 'case-' + str(position)
        problem = structural(case)
        if problem:
            structural_failures += 1
            observations.append({'case': label, 'verdict': 'unverifiable', 'reason': problem})
            continue
        actions = tuple(case['source']['actions'])
        rows = case['rows']
        prefixes = case.get('prefixes')
        s_states = restore(case['source'], False)
        a_states = restore(case['adapter'], True)
        profile_actions = tuple(case['source']['profile']['actions'])
        computed_q = tuple(a for a in profile_actions if not source_only(a))
        q_actions = tuple(case['adapter'].get('q_profile', {}).get('actions') or ()) or computed_q
        if q_actions != computed_q:
            mismatches.append({'case': label, 'kind': 'q-profile', 'expected': list(computed_q), 'observed': list(q_actions)})
        sub = subclass(actions)
        if sub:
            subclasses.add(sub)
        if len(actions) > SUFFIX_START:
            suffix_cases += 1
        witnesses = []
        for i in range(len(actions) + 1):
            charge.take(1)
            audited += 1
            s, a = s_states[i], a_states[i]
            journal, core = a['journal'], a['core']
            diff = [f for f in JOURNAL_FIELDS if not exact(s.get(f), journal.get(f))]
            if diff:
                mismatches.append({'case': label, 'prefix': i, 'kind': 'journal-mirror', 'fields': diff})
            if not (exact(s.get('source_generation'), journal.get('source_generation')) and exact(journal.get('source_generation'), core.get('source_generation'))):
                mismatches.append({'case': label, 'prefix': i, 'kind': 'generation-coupling',
                                   'expected': safe(s.get('source_generation')),
                                   'journal': safe(journal.get('source_generation')),
                                   'core': safe(core.get('source_generation'))})
            invocations = tuple(a.get('invocations') or ())
            if len(set(invocations)) != len(invocations) or any(x not in actions[:i] for x in invocations):
                mismatches.append({'case': label, 'prefix': i, 'kind': 'invocation-inventory', 'observed': list(invocations)})
            elif all(x in q_actions for x in invocations) and core.get('done') != sum(1 << q_actions.index(x) for x in invocations):
                mismatches.append({'case': label, 'prefix': i, 'kind': 'core-completion-mask', 'observed': core.get('done')})
            if a.get('done') != sum(1 << profile_actions.index(x) for x in actions[:i]) or s.get('done') != a.get('done'):
                mismatches.append({'case': label, 'prefix': i, 'kind': 'completion-mask', 'observed': safe(a.get('done'))})
            if isinstance(prefixes, (list, tuple)):
                item = prefixes[i]
                if isinstance(item, dict):
                    if item.get('prefix') != i:
                        mismatches.append({'case': label, 'prefix': i, 'kind': 'prefix-ordinal', 'observed': safe(item.get('prefix'))})
                    if sorted(item.get('differing_journal_fields', ())) != sorted(diff):
                        mismatches.append({'case': label, 'prefix': i, 'kind': 'prefix-journal-diff',
                                           'expected': sorted(diff), 'observed': sorted(item.get('differing_journal_fields', ()))})
            if i == 0:
                continue
            action, row, prev = actions[i - 1], rows[i - 1], a_states[i - 1]
            if row.get('index') != i - 1 or row.get('source_action') != action or row.get('adapter_action') != action:
                mismatches.append({'case': label, 'index': i - 1, 'kind': 'row-identity', 'expected': action,
                                   'observed': safe((row.get('index'), row.get('source_action'), row.get('adapter_action')))})
            invoked = row.get('q_invoked')
            prev_invocations = tuple(prev.get('invocations') or ())
            grew = len(invocations) == len(prev_invocations) + 1 and invocations[-1] == action
            if invoked not in (True, False) or invoked != grew or (not invoked and invocations != prev_invocations):
                mismatches.append({'case': label, 'index': i - 1, 'action': action, 'kind': 'invocation-mask',
                                   'row_claim': safe(invoked), 'observed_delta': grew})
            if invoked is False and not exact(prev['core'], core):
                mismatches.append({'case': label, 'index': i - 1, 'action': action, 'kind': 'nondelegated-core-changed'})
            if s['decision'] != a['decision']:
                mismatches.append({'case': label, 'index': i - 1, 'action': action, 'kind': 'outer-response',
                                   'expected': s['decision'], 'observed': a['decision']})
            if row.get('responses_related') is True and (s['decision'] != a['decision'] or (
                    (verb(action).startswith('append:') or verb(action) == 'append-lose-reply')
                    and not exact(s.get('append_reply'), journal.get('append_reply')))):
                mismatches.append({'case': label, 'index': i - 1, 'action': action, 'kind': 'response-relation-over-divergence'})
            if sorted(row.get('differing_journal_fields', ())) != sorted(diff):
                mismatches.append({'case': label, 'index': i - 1, 'action': action, 'kind': 'row-journal-diff',
                                   'expected': sorted(diff), 'observed': sorted(row.get('differing_journal_fields', ()))})
            if row.get('state_related') is True and diff:
                mismatches.append({'case': label, 'index': i - 1, 'action': action, 'kind': 'state-related-over-journal-diff'})
            if core.get('publication_revision') != prev['core'].get('publication_revision') and not exact(journal.get('selected_source'), prev['journal'].get('staged_source')):
                mismatches.append({'case': label, 'index': i - 1, 'action': action, 'kind': 'selected-source-not-committed-stage'})
            if verb(action).startswith('stage') and a['decision'] == verb(action) + ':ok' and not exact(journal.get('staged_source'), prev['journal'].get('attestation')):
                mismatches.append({'case': label, 'index': i - 1, 'action': action, 'kind': 'staged-source-not-attestation'})
            if i - 1 < SUFFIX_START:
                continue
            expected_decision, expected_invoked = suffix_expectation(action, a)
            bad = (invoked not in (True, False)
                   or (expected_decision is not None and (s['decision'] != expected_decision or a['decision'] != expected_decision))
                   or (expected_invoked is not None and invoked is not expected_invoked))
            witness = {'index': i - 1, 'action': action, 'expected_decision': expected_decision,
                       'observed_source_decision': s['decision'], 'observed_adapter_decision': a['decision'],
                       'expected_q_invoked': expected_invoked, 'observed_q_invoked': invoked,
                       'verdict': 'mismatch' if bad else 'exact-refusal-confirmed' if expected_decision else 'invocation-confirmed' if expected_invoked is not None else 'undecidable'}
            if bad:
                mismatches.append(dict(case=label, kind='suffix-expectation', **witness))
            elif expected_decision:
                decided_refusals += 1
            elif expected_invoked is None and verb(action) in GUARD_VERBS:
                undecided_guard.append({'case': label, 'index': i - 1, 'action': action,
                                        'observed': a['decision'], 'q_invoked': invoked})
            witnesses.append(witness)
        pairs_ok = True
        for pair in case.get('incarnation_pairs') or ():
            if not (isinstance(pair, dict) and all(isinstance(pair.get(side), (list, tuple)) and len(pair[side]) == 4
                    and tuple(pair[side][:3]) == ('cut-source', 'collectorA', 'effectA')
                    and type(pair[side][3]) is int and pair[side][3] >= 0 for side in ('source', 'target'))
                    and type(pair.get('source_event')) is int and type(pair.get('target_event')) is int
                    and 0 <= pair['source_event'] < len(actions) and 0 <= pair['target_event'] < len(actions)):
                pairs_ok = False
        if not pairs_ok:
            mismatches.append({'case': label, 'kind': 'incarnation-pair-shape'})
        observations.append({'case': label, 'subclass': sub, 'actions': len(actions),
                             'prefixes_audited': len(actions) + 1, 'suffix_event_witnesses': witnesses})
    if mismatches:
        status = 'counterexample'
    elif structural_failures or undecided_guard or not suffix_cases or not decided_refusals:
        status = 'unproved'
    else:
        status = 'supported'
    summary = {'cases': len(cases), 'subclasses_observed': sorted(subclasses), 'suffix_cases': suffix_cases,
               'decided_guard_refusal_witnesses': decided_refusals,
               'undecided_guard_events': undecided_guard[:40], 'mismatches': mismatches[:40],
               'mismatches_truncated': max(0, len(mismatches) - 40),
               'hypotheses_checked': [
                   'adapter journal mirrors every source ledger field at every audited prefix',
                   'source/journal/Q-core source generations are typed-equal at every audited prefix',
                   'a guard-refused or source-handled action leaves the entire Q core unchanged and adds no invocation',
                   'Q completion mask equals exactly the retained invocation set',
                   'source and adapter outer decisions are equal at every audited event',
                   'suffix guard refusals match the refusal order recomputed from actual collection/attestation/selection fields',
                   'selected_source/staged_source ledger rules hold on committed publications and successful stages'],
               'reachability': 'evidence covers only the supplied restored cases; no order coverage beyond them is claimed'}
    return {'status': status, 'observations': [summary] + observations,
            'limitations': limitations, 'audited_prefixes': audited}
