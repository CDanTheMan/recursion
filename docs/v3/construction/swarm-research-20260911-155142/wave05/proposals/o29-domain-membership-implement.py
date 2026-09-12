"""Independent retained-certificate check for the boundary-01 domain-membership obligation.

Callers supply already-restored typed c.run_history / c.artifact case objects;
this module recomputes order-level facts only and imports/executes no reducer,
guard, inventory or boundary helper. Every literal below is re-derived here.

Source anchors (unchanged packet inputs):
- boundary-01/spec.json: subclasses "C0;perm(A2,A3,A4,R);O;perm(C1,C2)" (48) and
  "O;perm(A2,A3,A4,R);perm(C0,C1,C2)" (144); fixed_prefix_length 11, core_length
  8, fixed_suffix_start 19; analytic_histories 384; units event/utf8-byte.
- boundary.py frame()/rank()/global_index(): the original 40320 orders are
  prefix x permutations(core8) x suffix once the per-case dependency graph is
  verified; the factoradic core rank equals the lexicographic global index.
- selected.py FIRST_CORE (packet04 head) and fresh_complete.py fresh_complete()
  (packet08 predicate), recomputed on the core window.
- boundary.py attestation_observation(): per-subclass predicted refusal with
  q_invoked False.

Finite audit accounting: charge.take(1) is consumed once before each inspected
case prefix; each case carries DEPTH+1 = 35 prefixes, so a complete 384-case
inspection consumes 13440 units. audited_prefixes reports actual consumption;
charge exhaustion yields unproved, never supported.

Status: "supported" only when every supplied case passes and the supplied set
completes the 384-history inventory (192 distinct original40320 lexicographic
global ranks x 2 units, 48+144 subclass counts per unit); "counterexample"
retains a concrete expected/observed witness; "unproved" for partial coverage
or exhausted charge; "not_applicable" for absent/foreign input.
"""

PACKET, DEPTH, PREFIX, SUFFIX, CORE = 'boundary-01', 34, 11, 19, 8
UNITS, OUTCOME = ('event', 'utf8-byte'), 1
ORDERS_PER_UNIT, HISTORIES, WHOLE = 192, 384, 40320
SUBCLASS_TOTALS = {'fresh-incomplete': 48, 'stale-complete': 144}
O, R = 'collect-open@11', 'source-restart@18'
C = ('collect:0@12', 'collect:1@13', 'collect:2@14')
A = ('attempt:2@15', 'attempt:3@16', 'attempt:4@17')
ALPHABET = tuple(sorted((*C, O, R, *A)))
FREE, TAIL2, ALL3 = frozenset((*A, R)), frozenset(C[1:]), frozenset(C)
PACKET04_HEAD, ATTEST = (C[0], C[1], A[1], A[2]), 'source-attest'
PREDICTED = {'fresh-incomplete': 'source-attest:incomplete-inventory',
             'stale-complete': 'source-attest:stale-collection'}
FACT, MAX_WITNESSES = (1, 1, 2, 6, 24, 120, 720, 5040, 40320), 16


def _subclass(middle):
    """Literal boundary-01 subclass of one core order, or None."""
    if (middle[0] == C[0] and middle[5] == O and set(middle[1:5]) == FREE
            and set(middle[6:8]) == TAIL2):
        return 'fresh-incomplete'
    if middle[0] == O and set(middle[1:5]) == FREE and set(middle[5:8]) == ALL3:
        return 'stale-complete'
    return None


def _fresh_complete(middle):
    """Independent packet08 membership predicate on core-window positions."""
    p = {a: i for i, a in enumerate(middle)}
    ok = [A[0]]
    if p[A[0]] < p[A[1]]: ok.append(A[1])
    if p[A[0]] < p[A[1]] < p[A[2]]: ok.append(A[2])
    return all(p[a] < p[O] for a in (R, *ok)) and all(p[O] < p[c] for c in C)


def _rank(middle):
    """Factoradic lexicographic index of middle over the sorted core alphabet."""
    remaining, value = list(ALPHABET), 0
    for action in middle:
        i = remaining.index(action)
        value += i * FACT[len(remaining) - 1]
        del remaining[i]
    return value


def _graph(profile):
    """Verify the fixed prefix / antichain8 / suffix dependency frame."""
    actions = profile['actions']
    if len(actions) != DEPTH or len(set(actions)) != DEPTH: return 'action-inventory'
    if set(actions[PREFIX:SUFFIX]) != set(ALPHABET): return 'core-set'
    for i, action in enumerate(actions):
        want = (set() if i == 0 else {actions[i - 1]} if i < PREFIX or i > SUFFIX
                else {actions[PREFIX - 1]} if i < SUFFIX else set(actions[PREFIX:SUFFIX]))
        if set(profile['requires'][action]) != want: return 'requires[' + action + ']'
    return None


def _linear_extension(profile, schedule):
    """schedule is a valid original dependency order."""
    done = set()
    for action in schedule:
        requires = profile['requires'].get(action)
        if requires is None or not set(requires) <= done: return False
        done.add(action)
    return len(done) == DEPTH


def inspect_cases(cases, charge):
    """Re-check retained boundary-01 cases; scope/status in module docstring."""
    audited, witnesses, observations = 0, [], []
    seen, decisions, attest_at = {}, {}, {}
    subclass_by_unit = {u: {k: 0 for k in SUBCLASS_TOTALS} for u in UNITS}
    classified = attest_matches = q_at_attest = 0
    rank_lo = rank_hi = exhausted = None

    def fail(case_id, check, expected, observed):
        if len(witnesses) < MAX_WITNESSES:
            witnesses.append({'case': case_id, 'check': check,
                              'expected': expected, 'observed': observed})

    if not isinstance(cases, (list, tuple)) or not cases:
        return {'status': 'not_applicable', 'audited_prefixes': 0,
                'limitations': ['no retained boundary-01 cases supplied'],
                'observations': [{'check': 'input', 'observed': type(cases).__name__}]}
    name0 = cases[0].get('case') if isinstance(cases[0], dict) else None
    if not (type(name0) is str and name0.startswith(PACKET + '/')):
        return {'status': 'not_applicable', 'audited_prefixes': 0,
                'limitations': ['supplied cases are not boundary-01 retained certificates'],
                'observations': [{'check': 'domain', 'expected': PACKET, 'observed': name0}]}
    take = getattr(charge, 'take', None)
    if not callable(take):
        return {'status': 'unproved', 'observations': [], 'audited_prefixes': 0,
                'limitations': ['charge.take(1) unavailable; prefix audit not performable']}

    for ordinal, case in enumerate(cases):
        cid = ordinal
        try:
            cid = case['case'] if type(case['case']) is str else 'case@%d' % ordinal
            parts = cid.split('/')
            if (len(parts) != 4 or parts[0] != PACKET or len(parts[1]) != 6
                    or not parts[1].isdigit() or parts[3] != str(OUTCOME)):
                fail(cid, 'case-name', 'boundary-01/<global-index-6d>/<unit>/1', cid)
                continue
            claimed, unit, outcome = int(parts[1]), parts[2], int(parts[3])
            profile, schedule = case['source']['profile'], case['source']['actions']
            if case['adapter']['profile'] != profile:
                fail(cid, 'shared-profile', 'identical source/adapter profile', 'differing')
            if case['adapter']['actions'] != schedule:
                fail(cid, 'visible-actions', 'identical source/adapter actions', 'differing')
            if type(schedule) is not tuple:
                fail(cid, 'typed-schedule', 'tuple', type(schedule).__name__)
            if (unit not in UNITS or outcome != OUTCOME
                    or (unit, outcome) != (case['unit'], case['outcome'])):
                fail(cid, 'unit-outcome', [case['unit'], case['outcome']], [unit, outcome])
            ev = (len(case['source']['events']), len(case['adapter']['events']))
            if ev != (DEPTH, DEPTH): fail(cid, 'visible-events', [DEPTH, DEPTH], list(ev))
            bad = _graph(profile)
            if bad: fail(cid, 'original-graph', 'fixed prefix + antichain8 + suffix', bad)
            if tuple(profile.get('outcomes', ())) != (OUTCOME,):
                fail(cid, 'profile-outcomes', [OUTCOME], list(profile.get('outcomes', ())))
            actions = profile['actions']
            if (len(schedule) != DEPTH or schedule[:PREFIX] != actions[:PREFIX]
                    or schedule[SUFFIX:] != actions[SUFFIX:]):
                fail(cid, 'fixed-frame', 'profile prefix/suffix preserved', 'changed')
            elif not _linear_extension(profile, schedule):
                fail(cid, 'linear-extension', 'original dependency order', 'violated')
            middle = schedule[PREFIX:SUFFIX] if len(schedule) == DEPTH else ()
            permuted = len(middle) == CORE and set(middle) == set(ALPHABET)
            label = _subclass(middle) if permuted else None
            if label is None:
                fail(cid, 'subclass-membership', sorted(SUBCLASS_TOTALS), list(middle))
            if permuted and middle[:4] == PACKET04_HEAD:
                fail(cid, 'packet04-disjoint', 'outside 24-order subset', list(middle))
            if permuted and _fresh_complete(middle):
                fail(cid, 'packet08-disjoint', 'outside 216-order subset', list(middle))
            rank = _rank(middle) if permuted else None
            if rank != claimed or not 0 <= claimed < WHOLE:
                fail(cid, 'global-rank', claimed, rank)
            if unit in UNITS:
                if unit in seen.setdefault(claimed, set()):
                    fail(cid, 'duplicate-history', 'unique (global-index, unit)', cid)
                seen[claimed].add(unit)
            if label and unit in UNITS:
                subclass_by_unit[unit][label] += 1
                classified += 1
            if type(rank) is int:
                rank_lo = rank if rank_lo is None else min(rank_lo, rank)
                rank_hi = rank if rank_hi is None else max(rank_hi, rank)
            prefixes, rows = case['prefixes'], case['rows']
            if len(prefixes) != DEPTH + 1 or len(rows) != DEPTH:
                fail(cid, 'prefix-inventory', [DEPTH + 1, DEPTH], [len(prefixes), len(rows)])
            for i in range(len(prefixes)):
                try:
                    take(1)
                except Exception as error:
                    exhausted = 'charge.take(1) refused at case %s prefix %d: %s' % (cid, i, error)
                    break
                audited += 1
                item = prefixes[i]
                kinds = (type(item.get('strict_related')) is bool,
                         type(item.get('related')) is bool)
                if kinds != (True, True):
                    fail(cid, 'prefix-relation', 'bool fields at prefix %d' % i, list(kinds))
                if not i: continue
                row = rows[i - 1]
                if (row.get('index') != i - 1 or row.get('source_action') != schedule[i - 1]
                        or row.get('adapter_action') != schedule[i - 1]):
                    fail(cid, 'chronology', [i - 1, schedule[i - 1]],
                         [row.get('index'), row.get('source_action'), row.get('adapter_action')])
                decision = row['source_observation']['decision']
                decisions[decision] = decisions.get(decision, 0) + 1
                if schedule[i - 1].split('@')[0] != ATTEST: continue
                attest_at[i - 1] = attest_at.get(i - 1, 0) + 1
                adapter_decision = row['adapter_observation']['decision']
                if row['q_invoked'] is not False: q_at_attest += 1
                if (label is not None and row['q_invoked'] is False
                        and decision == adapter_decision == PREDICTED[label]):
                    attest_matches += 1
                elif label is not None:
                    fail(cid, 'attestation-witness', [PREDICTED[label], False],
                         [decision, adapter_decision, row['q_invoked']])
        except (KeyError, IndexError, TypeError, AttributeError, ValueError) as error:
            fail(cid, 'case-structure', 'restored typed boundary-01 case', repr(error))
        if exhausted: break

    expected_subclasses = {u: dict(SUBCLASS_TOTALS) for u in UNITS}
    complete = (not exhausted and not witnesses and len(cases) == HISTORIES
                and len(seen) == ORDERS_PER_UNIT and subclass_by_unit == expected_subclasses
                and all(len(u) == len(UNITS) for u in seen.values()))
    observations += [
        {'check': 'case-count', 'expected': HISTORIES, 'observed': len(cases)},
        {'check': 'distinct-global-indices', 'expected': ORDERS_PER_UNIT, 'observed': len(seen)},
        {'check': 'subclass-counts-per-unit', 'expected': expected_subclasses,
         'observed': subclass_by_unit},
        {'check': 'global-rank-range', 'expected': [0, WHOLE - 1], 'observed': [rank_lo, rank_hi]},
        {'check': 'prefix-charge', 'expected': (DEPTH + 1) * len(cases), 'observed': audited},
        {'check': 'attestation-index-census', 'observed': attest_at},
        {'check': 'attestation-predictions', 'expected': classified, 'observed': attest_matches},
        {'check': 'q-invoked-at-attestation', 'expected': 0, 'observed': q_at_attest},
        {'check': 'row-decision-census', 'observed': decisions}] + witnesses
    limitations = [
        'retained-certificate order check only; no reducer/guard/boundary helper executed inside it',
        'global rank is the factoradic index over the sorted core alphabet; it equals the original'
        ' 40320 lexicographic index only where the per-case graph/frame checks passed',
        'packet04 disjointness is the exact first-four-core head under verified permutation; packet08'
        ' disjointness recomputes the fresh-complete predicate on the core window',
        'attestation refusal and Q-invocation facts are witnesses of restored fields under the'
        ' unchanged-profile hypothesis; no new reachability is claimed',
        'a supported result is bounded to the supplied certificates; not a global theorem or accepted PASS']
    if not complete:
        limitations.append('supplied coverage %d/%d histories over %d/%d global indices;'
                           ' whole-inventory arithmetic unproved'
                           % (len(cases), HISTORIES, len(seen), ORDERS_PER_UNIT))
    if exhausted: limitations.append(exhausted)
    return {'status': 'counterexample' if witnesses else 'supported' if complete else 'unproved',
            'observations': observations, 'limitations': limitations, 'audited_prefixes': audited}
