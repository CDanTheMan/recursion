"""Bounded retained-certificate check for the causal incarnation-pair obligation.

Obligation: causal incarnation pair ledger advancement, prefix binding and
source-action translation; the staged original-object-identity disjunct must
not authorize pair creation.

Method. inspect_cases(cases, charge) inspects already produced, typed, restored
case objects of the check.run_history / artifact-decoded shape. charge.take(1)
is called before auditing each case prefix; every charged prefix is audited
whether or not it passes. All expectations are recomputed declaratively from
retained fields and hash-bound trace patches; no reducer, guard, audit,
inventory or boundary helper is imported or executed inside inspection.

Mirrored semantics (unchanged original anchors):
- experiments/v3/cut-source-overnight/batch-05/semantic.py: token,
  generation_pair, bind and advance field semantics; canonical digest.
- experiments/v3/cut-source-overnight/batch-06/adapter_traces.py: core_view
  journal overlay, restore patch/digest/done-mask binding, comparison rows, and
  advance invoked with si=qi=event index.
- experiments/v3/cut-source-overnight/batch-06/a_domain.py: source_only action
  classes, fixed potential-call subprofile and justification strings.
- experiments/v3/cut-source-overnight/s_domain.py: journal EXTRA inventory.
- experiments/v3/cut-source-overnight/batch-07/identity.py + identity_audit.py:
  staged_rule disjunct, identity_proof, incarnation_pair_established_by_identity
  fixed False; compare never mutates the pair ledger.
- experiments/v3/eight-hour-research-20260910-01a08a22/check.py: audit_case
  ordering (advance for event p-1 before compare at prefix p) and the
  strict_related prestate/poststate row linkage.

Returns a JSON-safe dict {status, observations, limitations, audited_prefixes}.
'supported' covers only the supplied cases under these hypotheses; it is not an
all-order theorem and not scientific acceptance.
"""
import copy
import hashlib
import json


class _Gap(ValueError):
    pass


EXTRA = ('registration', 'attempts', 'append_log', 'append_receipts', 'append_reply',
         'source_revision', 'collection', 'collected', 'attestation', 'staged_source',
         'selected_source')
BINDING_REASONS = ('paired-successful-attestation', 'paired-restart')
PAIR_KEYS = ('source', 'target', 'reason', 'source_event', 'target_event')
SOURCE_ONLY_EXACT = ('append-lose-reply', 'collect-open')
SOURCE_ONLY_PREFIX = ('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:')
SCOPE_LIMIT = 'covers only supplied retained cases; no all-order theorem or scientific acceptance'


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'))


def digest(x):
    return hashlib.sha256(canonical(x).encode()).hexdigest()


def typed(x):
    if isinstance(x, dict):
        return ['dict', [[k, typed(v)] for k, v in sorted(x.items())]]
    if isinstance(x, (list, tuple)):
        return [type(x).__name__, [typed(v) for v in x]]
    return [type(x).__name__, x]


def exact(a, b):
    return typed(a) == typed(b)


def token(x):
    return (type(x) is tuple and len(x) == 4
            and x[:3] == ('cut-source', 'collectorA', 'effectA')
            and type(x[3]) is int and x[3] >= 0)


def generation_pair(a, b, pairs):
    return token(a) and token(b) and any(
        exact(a, row['source']) and exact(b, row['target']) for row in pairs)


def source_only(action):
    k = action.split('@')[0]
    return k.startswith(SOURCE_ONLY_PREFIX) or k in SOURCE_ONLY_EXACT


def justification(action, delegated):
    if source_only(action):
        return ('Same literal call, parameters and visible reply handled by the '
                'initialized adapter source ledger; Q state is unchanged.')
    if not delegated:
        return ('Same literal call refused by the adapter source guard; refusal '
                'remains visible and Q state is unchanged.')
    if action.split('@')[0] == 'source-attest':
        return ('Current complete ledger capture permits the same literal Q '
                'attestation; retain actual Q response and commit journal '
                'attestation only on Q acceptance.')
    return ('Same literal Q call and parameters after the declared adapter guard; '
            'unchanged Q reducer supplies the actual outcome.')


def core_view(state):
    view = dict(state['core'])
    for key in EXTRA:
        view[key] = state['journal'][key]
    view['decision'] = state['decision']
    return view


def bind_sim(pairs, a, b, reason, event):
    if not (token(a) and token(b)):
        return 'typed-pair-violation'
    existing = [row for row in pairs
                if exact(row['source'], a) or exact(row['target'], b)]
    if existing:
        return ('already-bound' if len(existing) == 1
                and generation_pair(a, b, existing) else 'binding-conflict')
    pairs.append(dict(source=a, target=b, reason=reason,
                      source_event=event, target_event=event))
    return 'new-binding'


def advance_sim(pairs, s_before, q_before, s_after, q_after, action, event):
    verb = action.split('@')[0]
    if verb == 'source-attest' and s_after['decision'] == q_after['decision'] == 'source-attest:ok':
        if not exact(s_before['cut_delivery'], q_before['cut_delivery']):
            return 'different-attestation-input'
        return bind_sim(pairs, s_after['source_generation'], q_after['source_generation'],
                        'paired-successful-attestation', event)
    if verb == 'source-restart' and generation_pair(
            s_before['source_generation'], q_before['source_generation'], pairs):
        if not (s_after['source_generation'][-1] == s_before['source_generation'][-1] + 1
                and q_after['source_generation'][-1] == q_before['source_generation'][-1] + 1):
            return 'advancement-violation'
        return bind_sim(pairs, s_after['source_generation'], q_after['source_generation'],
                        'paired-restart', event)
    return 'unchanged'


def restore(trace):
    if (not isinstance(trace, dict)
            or any(k not in trace for k in ('side', 'initial', 'profile', 'actions', 'events'))):
        raise _Gap('trace missing retained fields')
    adapter = trace['side'] == 'adapter'
    actions = list(trace['actions'])
    if len(trace['events']) != len(actions) or len(set(actions)) != len(actions):
        raise _Gap('visible event inventory')
    q_actions = ()
    if adapter:
        q_profile = trace.get('q_profile')
        if not isinstance(q_profile, dict):
            raise _Gap('adapter trace lacks retained q_profile')
        expected = dict(copy.deepcopy(trace['profile']))
        expected['actions'] = tuple(a for a in trace['profile']['actions'] if not source_only(a))
        expected['requires'] = {a: () for a in expected['actions']}
        if not exact(q_profile, expected):
            raise _Gap('q_profile is not the fixed potential-call subprofile')
        q_actions = q_profile['actions']
    current = copy.deepcopy(trace['initial'])
    states, executed = [current], []
    for index, (action, event) in enumerate(zip(actions, trace['events'])):
        reqs = trace['profile']['requires'].get(action)
        if (reqs is None or event.get('action') != action or action in executed
                or not set(reqs) <= set(executed)):
            raise _Gap('literal occurrence or dependency order at event ' + str(index))
        if digest(current) != event.get('before_sha256'):
            raise _Gap('prestate digest at event ' + str(index))
        current = copy.deepcopy(current)
        for key, value in event.get('patch', {}).items():
            if adapter and key in ('core', 'journal'):
                current[key].update(value)
            else:
                current[key] = value
        executed.append(action)
        if digest(current) != event.get('after_sha256'):
            raise _Gap('poststate digest at event ' + str(index))
        if current['done'] != sum(1 << actions.index(a) for a in executed):
            raise _Gap('completion mask at event ' + str(index))
        if adapter:
            if (set(current) != {'core', 'journal', 'done', 'decision', 'invocations'}
                    or not set(EXTRA) <= set(current['journal'])):
                raise _Gap('adapter frame at event ' + str(index))
            if current['core']['done'] != sum(1 << q_actions.index(a) for a in current['invocations']):
                raise _Gap('actual Q invocation mask at event ' + str(index))
        states.append(current)
    return states, q_actions


def _witness(label, index, check, expected, observed):
    return {'case': label, 'index': index, 'check': check,
            'expected': expected, 'observed': observed}


def _audit_event(label, i, action, row, retained, ss, aa, sim, consumed, q_actions, acc):
    v = acc['violations']
    if row.get('index') != i or row.get('source_action') != action or row.get('adapter_action') != action:
        v.append(_witness(label, i, 'literal chronological event equality',
                          {'index': i, 'action': action},
                          {'index': row.get('index'), 'source_action': row.get('source_action'),
                           'adapter_action': row.get('adapter_action')}))
    expected = advance_sim(sim, ss[i], core_view(aa[i]), ss[i + 1], core_view(aa[i + 1]), action, i)
    if row.get('binding') != expected:
        v.append(_witness(label, i, 'causal binding outcome', expected, row.get('binding')))
    if expected == 'new-binding':
        acc['bindings'] += 1
        pair = retained[consumed] if consumed < len(retained) else None
        if pair is None:
            v.append(_witness(label, i, 'causal ledger growth', 'retained pair appended', 'ledger ended'))
        else:
            for key in ('source', 'target', 'reason'):
                if not exact(pair.get(key), sim[-1][key]):
                    v.append(_witness(label, i, 'retained pair ' + key, typed(sim[-1][key]), typed(pair.get(key))))
            for key in ('source_event', 'target_event'):
                if type(pair.get(key)) is not int or pair[key] > i:
                    v.append(_witness(label, i, 'causal ' + key + ' <= binding index', '<= ' + str(i), pair.get(key)))
        consumed += 1
    if row.get('pairs_sha256') != digest(sim):
        v.append(_witness(label, i, 'event ledger digest', digest(sim), row.get('pairs_sha256')))
    invoked = row.get('q_invoked')
    if type(invoked) is not bool:
        v.append(_witness(label, i, 'retained q_invoked flag', 'bool', typed(invoked)))
    growth = aa[i]['invocations'] + ((action,) if invoked else ())
    if aa[i + 1]['invocations'] != growth:
        v.append(_witness(label, i, 'actual Q invocation growth', typed(growth), typed(aa[i + 1]['invocations'])))
    if invoked:
        if action not in q_actions:
            v.append(_witness(label, i, 'invoked action in potential-call set', typed(q_actions), action))
        if aa[i + 1]['decision'] != aa[i + 1]['core'].get('decision'):
            v.append(_witness(label, i, 'outer decision adopts actual Q decision',
                              aa[i + 1]['core'].get('decision'), aa[i + 1]['decision']))
    else:
        if not exact(aa[i]['core'], aa[i + 1]['core']):
            v.append(_witness(label, i, 'non-invoked call leaves Q core unchanged', 'identical core', 'core changed'))
        verb = action.split('@')[0]
        decision = aa[i + 1]['decision']
        if not source_only(action) and not (
                isinstance(decision, str) and decision.startswith(verb + ':') and decision != verb + ':ok'):
            v.append(_witness(label, i, 'visible guard refusal', verb + ':<reason>', decision))
    if row.get('justification') != justification(action, bool(invoked)):
        v.append(_witness(label, i, 'source-action translation justification',
                          justification(action, bool(invoked)), row.get('justification')))
    for side, states in (('source', ss), ('adapter', aa)):
        observed = row.get(side + '_observation')
        if not isinstance(observed, dict) or observed.get('decision') != states[i + 1]['decision']:
            v.append(_witness(label, i, side + ' retained observation decision',
                              states[i + 1]['decision'], typed(observed)))
    return consumed


def _audit_prefix(label, prow, prefix, sim, acc):
    v = acc['violations']
    if not isinstance(prow, dict):
        v.append(_witness(label, prefix, 'prefix identity row', 'dict', typed(prow)))
        return
    if prow.get('prefix') != prefix:
        v.append(_witness(label, prefix, 'prefix ordinal', prefix, prow.get('prefix')))
    if prow.get('pairs_sha256') != digest(sim):
        v.append(_witness(label, prefix, 'prefix causal ledger digest', digest(sim), prow.get('pairs_sha256')))
    if prow.get('incarnation_pair_established_by_identity') is not False:
        v.append(_witness(label, prefix, 'identity never establishes pair authority',
                          False, prow.get('incarnation_pair_established_by_identity')))
    strict = set(prow.get('strict_differing_common_fields') or ())
    differing = set(prow.get('differing_common_fields') or ())
    if not differing <= strict or (strict - differing) - {'staged'}:
        v.append(_witness(label, prefix, 'disjunct removes only the staged field',
                          'removal subset of {staged}', typed(sorted(strict - differing))))
    rule = ('strict' if 'staged' not in strict
            else 'original-object-identity' if 'staged' not in differing else 'unrelated')
    if prow.get('staged_rule') != rule:
        v.append(_witness(label, prefix, 'staged disjunct rule', rule, prow.get('staged_rule')))
    if bool(prow.get('identity_proof')) != (rule == 'original-object-identity'):
        v.append(_witness(label, prefix, 'identity proof iff disjunct applied', rule, typed(prow.get('identity_proof'))))


def _audit_ledger(label, retained, sim, consumed, acc):
    v = acc['violations']
    if consumed != len(retained):
        v.append(_witness(label, None, 'ledger size equals authorized binding events',
                          consumed, len(retained)))
    for pair in retained:
        if not isinstance(pair, dict) or set(pair) != set(PAIR_KEYS):
            v.append(_witness(label, None, 'retained pair shape', list(PAIR_KEYS), typed(pair)))
            continue
        if pair['reason'] not in BINDING_REASONS:
            v.append(_witness(label, pair.get('source_event'), 'authorized pair reason',
                              list(BINDING_REASONS), pair['reason']))
        if not (token(pair['source']) and token(pair['target'])):
            v.append(_witness(label, None, 'typed scoped incarnation tokens',
                              'cut-source token pair', typed((pair['source'], pair['target']))))


def _audit_case(case, label, charge, acc):
    if not isinstance(case, dict) or any(k not in case for k in ('source', 'adapter', 'rows', 'incarnation_pairs')):
        acc['gaps'].append(label + ': missing source/adapter/rows/incarnation_pairs')
        return
    source_trace, adapter_trace = case['source'], case['adapter']
    rows, retained = case['rows'], case['incarnation_pairs']
    if not isinstance(rows, list) or not isinstance(retained, list):
        acc['gaps'].append(label + ': rows/incarnation_pairs not retained lists')
        return
    actions = list(source_trace.get('actions', ()))
    if not exact(adapter_trace.get('actions'), source_trace.get('actions')) \
            or not exact(adapter_trace.get('profile'), source_trace.get('profile')):
        acc['violations'].append(_witness(label, None, 'literal action/profile equality',
                                          'identical inventories', 'differing inventories'))
        return
    if len(rows) != len(actions):
        acc['gaps'].append(label + ': retained rows ' + str(len(rows)) + ' != actions ' + str(len(actions)))
        return
    prefixes = case.get('prefixes')
    if prefixes is None:
        acc['limitations'].append(label + ': no per-prefix identity rows; staged disjunct skipped for this case')
    elif len(prefixes) != len(actions) + 1:
        acc['gaps'].append(label + ': prefix row count ' + str(len(prefixes)))
        return
    else:
        acc['prefix_rows'] = True
    try:
        ss, _ = restore(source_trace)
        aa, q_actions = restore(adapter_trace)
    except _Gap as error:
        acc['gaps'].append(label + ': trace restoration: ' + str(error))
        return
    sim, consumed = [], 0
    for prefix in range(len(actions) + 1):
        try:
            charge.take(1)
        except Exception:
            acc['gaps'].append(label + ': charge exhausted before prefix ' + str(prefix))
            acc['stop'] = True
            return
        acc['audited'] += 1
        if prefix:
            consumed = _audit_event(label, prefix - 1, actions[prefix - 1], rows[prefix - 1],
                                    retained, ss, aa, sim, consumed, q_actions, acc)
            if prefixes is not None and (
                    prefixes[prefix].get('strict_related') != rows[prefix - 1].get('state_related')
                    or prefixes[prefix - 1].get('strict_related') != rows[prefix - 1].get('prestate_related')):
                acc['violations'].append(_witness(label, prefix, 'strict relation prestate/poststate linkage',
                                                'row flags equal adjacent prefix flags',
                                                typed({'pre': prefixes[prefix - 1].get('strict_related'),
                                                       'row': [rows[prefix - 1].get('prestate_related'),
                                                               rows[prefix - 1].get('state_related')],
                                                       'post': prefixes[prefix].get('strict_related')})))
        if prefixes is not None:
            _audit_prefix(label, prefixes[prefix], prefix, sim, acc)
            if prefixes[prefix].get('staged_rule') == 'original-object-identity':
                acc['identity'] += 1
    _audit_ledger(label, retained, sim, consumed, acc)


def inspect_cases(cases, charge):
    acc = {'audited': 0, 'bindings': 0, 'identity': 0, 'prefix_rows': False,
           'violations': [], 'gaps': [], 'limitations': [], 'stop': False}
    if not isinstance(cases, (list, tuple)) or not cases:
        return {'status': 'not_applicable', 'observations': ['no retained case objects supplied'],
                'limitations': [SCOPE_LIMIT], 'audited_prefixes': 0}
    for position, case in enumerate(cases):
        label = case.get('case') if isinstance(case, dict) else None
        if not isinstance(label, str):
            label = 'case[' + str(position) + ']'
        try:
            _audit_case(case, label, charge, acc)
        except (KeyError, IndexError, TypeError, AttributeError) as error:
            acc['gaps'].append(label + ': malformed retained field ' + repr(error))
        if acc['stop']:
            break
    if not acc['prefix_rows']:
        acc['gaps'].append('no case retained per-prefix identity rows; staged disjunct unverifiable')
    observations = [{'cases': len(cases), 'audited_prefixes': acc['audited'],
                     'new_bindings': acc['bindings'], 'identity_poststates': acc['identity']}]
    witnesses = acc['violations'] + acc['gaps']
    observations += witnesses[:24]
    if len(witnesses) > 24:
        observations.append('truncated witnesses: ' + str(len(witnesses) - 24) + ' more')
    limitations = [SCOPE_LIMIT,
                   'expectations recomputed declaratively; no reducer/guard/audit/inventory execution inside inspection',
                   'digest equality assumes unchanged canonical JSON encoding (sort_keys, compact separators)',
                   ] + acc['limitations']
    if acc['violations']:
        status = 'counterexample'
    elif acc['gaps']:
        status = 'unproved'
    elif acc['bindings'] == 0:
        status = 'unproved'
        observations.append('vacuous: no new-binding event retained in supplied cases')
    else:
        status = 'supported'
    return {'status': status, 'observations': observations,
            'limitations': limitations, 'audited_prefixes': acc['audited']}
