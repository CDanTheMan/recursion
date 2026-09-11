"""Bounded retained-certificate check for obligation o30-guard-prediction.

Conditional40320 first-refusing attestation-guard classification versus
actual complete histories. The packet-06 symbolic certificate (slice2
guard_order.py) conditionally classifies all 40320 orders of the eight-action
core of the unchanged scale-eight-action-race profile by which source-attest
guard refuses first (stale-collection 31248 / incomplete-inventory 8856 /
incomplete-registry 216 / success 0) under four declared hypotheses. This
module independently re-derives that order-conditioned prediction and
compares it with recorded rows/prefixes of actual typed c.run_history /
c.artifact case objects. No reducer executes; no boundary helper is
imported; no packet inventory/census/tally function is reused
(wave04/review-defects.json).

Audit accounting: charge.take(1) is called immediately before inspecting
each case prefix; repeated cases charge again. A complete in-domain
history carries 35 prefixes; audited_prefixes is the exact charged total.

Source anchors: s_domain.py add_with_suffix 'scale-eight-action-race';
s_inclusive.py / s_audit.py attestation precedence no-captured-source ->
stale-collection -> incomplete-inventory -> incomplete-registry ->
delegated success; batch-06/a_audit.py refused calls leave the Q core
unchanged (q_invoked False); fresh_complete.py observed
'source-attest:incomplete-registry' on the executed fresh-complete class.
"""

PREFIX_LEN, SUFFIX_START, DEPTH = 11, 19, 34
OPEN = 'collect-open@11'
COLLECTS = ('collect:0@12', 'collect:1@13', 'collect:2@14')
ATTEMPTS = ('attempt:2@15', 'attempt:3@16', 'attempt:4@17')
RESTART = 'source-restart@18'
CORE_SET = frozenset((OPEN, RESTART) + COLLECTS + ATTEMPTS)
ATTEST_VERB = 'source-attest'
REFUSAL_JUSTIFICATION = ('Same literal call refused by the adapter source '
                         'guard; refusal remains visible and Q state is unchanged.')
DECLARED_CLASS_COUNTS = {'stale-collection': 31248, 'incomplete-inventory': 8856,
                         'incomplete-registry': 216, 'successful-attestation': 0}
HYPOTHESES = ('successful fixed setup leaves valid registration, attempt1, three append records and no pause',
              'original scale-eight-action-race dependency profile with unchanged fixed successful delivery',
              'fixed success cut maps attempt1 only', 'nonmutant original source and adapter semantics')
ATTEMPT_SUCCESS = {(0, 1, 2): (0, 1, 2), (0, 2, 1): (0, 1), (1, 0, 2): (0,),
                   (1, 2, 0): (0,), (2, 0, 1): (0, 1), (2, 1, 0): (0,)}


def safe(value):
    """JSON-safe normalization of restored typed values."""
    if isinstance(value, dict):
        return {str(k): safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe(v) for v in value]
    if value is None or type(value) in (str, int, float, bool):
        return value
    return {'type': type(value).__name__, 'repr': repr(value)}


def _classify(fresh, inventory):
    if not fresh:
        return 'stale-collection'
    return 'incomplete-inventory' if not inventory else 'incomplete-registry'


def _predict(middle):
    """Two independent order->guard rules; they must agree (guard_order.py)."""
    p = {a: i for i, a in enumerate(middle)}
    successful = [ATTEMPTS[0]]
    if p[ATTEMPTS[0]] < p[ATTEMPTS[1]]: successful.append(ATTEMPTS[1])
    if p[ATTEMPTS[0]] < p[ATTEMPTS[1]] < p[ATTEMPTS[2]]: successful.append(ATTEMPTS[2])
    fresh_a = all(p[a] < p[OPEN] for a in (*successful, RESTART))
    inv_a = all(p[OPEN] < p[c] for c in COLLECTS)
    first = all(p[a] < p[OPEN] for a in (*ATTEMPTS, RESTART))
    second = (p[ATTEMPTS[1]] < p[ATTEMPTS[0]] < p[OPEN] < p[ATTEMPTS[2]]
              and p[RESTART] < p[OPEN])
    order3 = tuple(ATTEMPTS.index(a) for a in middle if a in ATTEMPTS)
    inv_b = p[OPEN] < min(p[c] for c in COLLECTS)
    rule_a = {'successful_attempts': successful, 'fresh': fresh_a,
              'complete_inventory': inv_a, 'guard': _classify(fresh_a, inv_a)}
    rule_b = {'successful_attempts': [ATTEMPTS[i] for i in ATTEMPT_SUCCESS[order3]],
              'fresh': first or second, 'complete_inventory': inv_b,
              'guard': _classify(first or second, inv_b)}
    return rule_a, rule_b


def _expected_core(middle, successful):
    """Order-implied visible decisions of the source-handled core calls."""
    p = {a: i for i, a in enumerate(middle)}
    want = {OPEN: 'collect-open:ok'}
    for a in ATTEMPTS:
        want[a] = a.split('@')[0] + (':ok' if a in successful else ':attempt-gap')
    for c in COLLECTS:
        want[c] = c.split('@')[0] + (':ok' if p[OPEN] < p[c] else ':outside-captured-cut')
    return want


def _core_order(case):
    """Exact original 34-action graph and the literal core order, or None."""
    try:
        profile = case['source']['profile']
        actions, requires = profile['actions'], profile['requires']
        schedule = tuple(case['source']['actions'])
        adapter = tuple(case['adapter']['actions'])
    except (KeyError, TypeError):
        return None
    if (not isinstance(requires, dict) or len(actions) != DEPTH or len(schedule) != DEPTH
            or len(set(actions)) != DEPTH or adapter != schedule
            or set(actions[PREFIX_LEN:SUFFIX_START]) != CORE_SET
            or schedule[:PREFIX_LEN] != tuple(actions[:PREFIX_LEN])
            or schedule[SUFFIX_START:] != tuple(actions[SUFFIX_START:])
            or set(schedule[PREFIX_LEN:SUFFIX_START]) != CORE_SET):
        return None
    for i, action in enumerate(actions):
        if i == 0: want = ()
        elif PREFIX_LEN <= i < SUFFIX_START: want = (actions[PREFIX_LEN - 1],)
        elif i == SUFFIX_START: want = tuple(actions[PREFIX_LEN:SUFFIX_START])
        else: want = (actions[i - 1],)
        if set(requires.get(action) or ()) != set(want): return None
    done = set()
    for action in schedule:
        if not set(requires.get(action) or ()) <= done: return None
        done.add(action)
    return schedule[PREFIX_LEN:SUFFIX_START]


def _inspect_case(case, charge):
    """Charge.take(1) per case prefix, then classify one restored typed case."""
    name = safe(case.get('case')) if isinstance(case, dict) else safe(case)
    middle = _core_order(case)
    if middle is None:
        return ('out_of_domain', {'kind': 'case', 'case': name, 'prefixes_audited': 0,
                'verdict': 'out_of_domain', 'reason': 'not an exact scale-eight history'}, 0)
    actions = tuple(case['source']['actions'])
    try:
        rows, prefixes = case['rows'], case['prefixes']
    except (KeyError, TypeError):
        rows, prefixes = (), ()
    problems, observed, seen = [], {}, 0
    for i in range(len(prefixes)):
        charge.take(1)
        seen += 1
        try: item = prefixes[i]
        except (KeyError, IndexError, TypeError): item = None
        if not isinstance(item, dict):
            problems.append({'prefix': i, 'problem': 'non-dict-prefix'}); continue
        for field in ('strict_related', 'related'):
            if type(item.get(field)) is not bool:
                problems.append({'prefix': i, 'problem': field + '-not-bool'})
        if not i: continue
        try:
            row = rows[i - 1]
            aligned = (row['index'] == i - 1 and
                       row['source_action'] == actions[i - 1] == row['adapter_action'])
            observed[i - 1] = dict(decision=row['source_observation']['decision'],
                adapter_decision=row['adapter_observation']['decision'],
                q_invoked=row['q_invoked'], responses_related=row['responses_related'],
                justification=row['justification'])
        except (KeyError, IndexError, TypeError):
            problems.append({'prefix': i, 'problem': 'row-unreadable'}); continue
        if not aligned:
            problems.append({'prefix': i, 'problem': 'literal-action-mismatch'})
            del observed[i - 1]
    attest_i = next((i for i, a in enumerate(actions)
                     if a.split('@')[0] == ATTEST_VERB), None)
    if len(prefixes) != DEPTH + 1 or len(rows) != DEPTH or attest_i is None:
        problems.append({'problem': 'history-shape', 'prefixes': len(prefixes),
                         'rows': len(rows), 'attestation_index': attest_i})
    if problems or len(observed) != DEPTH:
        return ('incomplete', {'kind': 'case', 'case': name, 'prefixes_audited': seen,
                'verdict': 'incomplete', 'problems': safe(problems)}, seen)
    pred_a, pred_b = _predict(middle)
    if pred_a != pred_b:
        return ('incomplete', {'kind': 'case', 'case': name, 'prefixes_audited': seen,
                'verdict': 'incomplete', 'problems': [{'problem': 'predictions-differ',
                'attempts_rule': safe(pred_a), 'partial_rule': safe(pred_b)}]}, seen)
    want = _expected_core(middle, pred_a['successful_attempts'])
    premise_failures, mismatches = [], []
    for i in range(attest_i):
        action, entry = actions[i], observed[i]
        if action in want:
            if entry['decision'] != want[action]:
                mismatches.append({'kind': 'intermediate-decision', 'action': action,
                                   'expected': want[action], 'observed': entry['decision']})
        elif i < PREFIX_LEN or i >= SUFFIX_START:
            ok = action.split('@')[0] + ':ok'
            if entry['decision'] != ok:
                premise_failures.append({'action': action, 'expected': ok, 'observed': entry['decision']})
        if entry['adapter_decision'] != entry['decision']:
            mismatches.append({'kind': 'adapter-decision', 'action': action,
                               'expected': entry['decision'], 'observed': entry['adapter_decision']})
    att = observed[attest_i]
    init = case['source'].get('initial') if isinstance(case['source'], dict) else None
    if (not isinstance(init, dict) or init.get('registration') or init.get('attempts')
            or init.get('append_log') or init.get('source_revision') or init.get('done')
            or init.get('decision') != 'initial'):
        premise_failures.append({'action': '<initial-state>', 'expected': 'empty source ledger',
                                 'observed': safe(init)})
    if not premise_failures:
        predicted = ATTEST_VERB + ':' + pred_a['guard']
        if att['decision'] != predicted:
            mismatches.append({'kind': 'attestation-guard', 'expected': predicted, 'observed': att['decision']})
        if att['adapter_decision'] != predicted:
            mismatches.append({'kind': 'attestation-adapter', 'expected': predicted, 'observed': att['adapter_decision']})
        if att['q_invoked'] is not False:
            mismatches.append({'kind': 'refused-attestation-q-invoked', 'expected': False, 'observed': safe(att['q_invoked'])})
        elif att['justification'] != REFUSAL_JUSTIFICATION:
            mismatches.append({'kind': 'refusal-justification', 'expected': REFUSAL_JUSTIFICATION, 'observed': safe(att['justification'])})
    if mismatches: verdict = 'counterexample'
    elif premise_failures: verdict = 'premise_failed'
    else: verdict = 'match'
    refusals = [{'action': actions[i], 'decision': observed[i]['decision']} for i in sorted(observed)
                if not str(observed[i]['decision']).endswith(':ok')]
    return verdict, {'kind': 'case', 'case': name, 'verdict': verdict, 'prefixes_audited': seen,
        'unit': safe(case.get('unit')), 'outcome': safe(case.get('outcome')),
        'core_order': list(middle), 'attestation_index': attest_i,
        'reachability': 'exact original requires graph; fixed prefix/suffix; core permutation',
        'predicted_guard': pred_a['guard'], 'predicted_decision': ATTEST_VERB + ':' + pred_a['guard'],
        'predicted_successful_attempts': list(pred_a['successful_attempts']),
        'observed_successful_attempts': [a for a in ATTEMPTS if str(observed[actions.index(a)]['decision']).endswith(':ok')],
        'observed_attestation': safe(att), 'premise_failures': safe(premise_failures),
        'mismatches': safe(mismatches), 'visible_refusals': safe(refusals)}, seen


def inspect_cases(cases, charge):
    """Bounded retained-certificate inspection; see module docstring."""
    if isinstance(cases, dict):
        cases = (cases,)
    counts = {'match': 0, 'counterexample': 0, 'premise_failed': 0,
              'incomplete': 0, 'out_of_domain': 0}
    predicted_classes, audited, per_case = {}, 0, []
    for case in cases:
        verdict, obs, seen = _inspect_case(case, charge)
        audited += seen
        counts[verdict] += 1
        if obs.get('predicted_guard'):
            key = obs['predicted_guard']
            predicted_classes[key] = predicted_classes.get(key, 0) + 1
        per_case.append(obs)
    in_domain = sum(counts[k] for k in ('match', 'counterexample', 'premise_failed', 'incomplete'))
    if counts['counterexample']: status = 'counterexample'
    elif not in_domain: status = 'not_applicable'
    elif counts['match'] == in_domain: status = 'supported'
    else: status = 'unproved'
    observations = [
        {'kind': 'obligation', 'scope': 'inspected retained cases only; no global 40320 claim',
         'claim': 'first-refusing source-attest guard is a function of the core order',
         'declared_class_counts': DECLARED_CLASS_COUNTS},
        {'kind': 'hypotheses', 'total': len(HYPOTHESES), 'declared': list(HYPOTHESES),
         'observed': ['exact profile dependency graph', 'fixed setup and delivery decisions'],
         'assumed': [HYPOTHESES[2], HYPOTHESES[3]],
         'falsified_in_cases': counts['premise_failed']},
        {'kind': 'verdict_counts', 'in_domain': in_domain,
         'predicted_class_distribution': predicted_classes, **counts},
        *per_case]
    limitations = [
        'Retained-certificate inspection only; no reducer, inventory or schedule re-enumeration executed.',
        'supported means every in-domain inspected case matched; bounded to supplied cases, not an accepted PASS.',
        'Fixture bytes (success cut attempt mapping) and nonmutant semantics are assumed, not re-derived.',
        'Registry-clause inequality is witnessed by the refusal decision itself; ledger field equality with fixture bytes is not recomputed.']
    return {'status': status, 'observations': observations,
            'limitations': limitations, 'audited_prefixes': audited}
