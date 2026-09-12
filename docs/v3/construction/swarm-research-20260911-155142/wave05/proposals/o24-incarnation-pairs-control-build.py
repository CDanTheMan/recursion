"""Retained-certificate check: causal incarnation-pair ledger advancement, prefix
binding and literal source-action translation; the staged-identity disjunct never
authorizes pair creation. Representation anchors (unchanged originals restated
locally; no reducer/guard/semantic-binder/boundary-helper import or execution):
batch-05/semantic.py token(), generation_pair, reasons 'paired-successful-
attestation'/'paired-restart', binder outcomes, typed/exact; digest = sha256 of
sorted compact JSON (s_audit.py/guard_audit.py reproduce q_domain.canonical
digests byte-identically). batch-06/a_domain.py handled verbs + four
justification literals; adapter_traces.py row fields, patch shape, event<=index
causality. batch-07/identity*.py prefix fields, staged rules, identity flag
always False. eight-hour check.py audit_case: prefix i compares under pairs
bound at events <i; rows[i-1] prestate/state_related == strict_related[i-1]/[i];
invocations == q_invoked occurrences. Accounting: charge.take(1) BEFORE every
inspected case prefix, again per repetition (each mutated control replay);
nothing else charged. Status supported|counterexample|unproved|not_applicable;
reachability is the supplied typed cases only; absent witnesses stay
limitations. Controls needing a genuinely reachable witness report
'unwitnessed', never detected."""
import copy
import hashlib
import json

REASONS = ('paired-successful-attestation', 'paired-restart')
BINDINGS = ('new-binding', 'already-bound', 'binding-conflict', 'different-attestation-input', 'unchanged')
RULES = ('strict', 'original-object-identity', 'unrelated')
J = ('Same literal call, parameters and visible reply handled by the initialized adapter source ledger; Q state is unchanged.',
     'Same literal call refused by the adapter source guard; refusal remains visible and Q state is unchanged.',
     'Current complete ledger capture permits the same literal Q attestation; retain actual Q response and commit journal attestation only on Q acceptance.',
     'Same literal Q call and parameters after the declared adapter guard; unchanged Q reducer supplies the actual outcome.')


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def typed(v):
    if isinstance(v, dict):
        return ['dict', [[k, typed(x)] for k, x in sorted(v.items())]]
    if isinstance(v, (list, tuple)):
        return [type(v).__name__, [typed(x) for x in v]]
    return [type(v).__name__, v]


def exact(a, b):
    return typed(a) == typed(b)


def token(v):
    return (type(v) is tuple and len(v) == 4 and type(v[3]) is int and v[3] >= 0
            and v[:3] == ('cut-source', 'collectorA', 'effectA'))


def paired_gen(a, b, pairs):
    return token(a) and token(b) and any(exact(a, r['source']) and exact(b, r['target']) for r in pairs)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def translation(action, delegated):
    k = action.split('@')[0]
    if k.startswith(('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:')) or k in ('append-lose-reply', 'collect-open'):
        return J[0]
    if not delegated:
        return J[1]
    return J[2] if k == 'source-attest' else J[3]


def replay(trace, actions, profile):
    require(trace['side'] in ('source', 'adapter') and len(trace['events']) == len(actions), 'complete visible event inventory')
    adapter, states, done = trace['side'] == 'adapter', [copy.deepcopy(trace['initial'])], []
    for action, event in zip(actions, trace['events']):
        require(event['action'] == action and action not in done and set(profile['requires'][action]) <= set(done), 'literal occurrence/dependency prefix')
        cur = copy.deepcopy(states[-1])
        require(digest(cur) == event['before_sha256'], 'retained prestate hash')
        for key, value in event['patch'].items():
            if adapter and key in ('core', 'journal'):
                cur[key].update(value)
            else:
                cur[key] = value
        done.append(action)
        require(digest(cur) == event['after_sha256'] and cur['done'] == sum(1 << actions.index(a) for a in done), 'retained poststate hash/mask')
        if adapter:
            qp = trace['q_profile']['actions']
            require(cur['core']['done'] == sum(1 << qp.index(a) for a in cur['invocations']), 'actual Q invocation mask')
        states.append(cur)
    return states


def inspect_cases(cases, charge):
    observations, limitations, audited, saw = [], [], 0, set()
    if not cases:
        return {'status': 'not_applicable', 'observations': [], 'limitations': ['no typed case objects supplied'], 'audited_prefixes': 0}
    for case in cases:
        name = case.get('case') if isinstance(case, dict) else str(type(case))
        try:
            st, at = case['source'], case['adapter']
            actions, profile = tuple(st['actions']), st['profile']
            require(actions == tuple(at['actions']) and exact(profile, at['profile']), 'shared literal profile/actions')
            rows, pairs, prefixes = case['rows'], case['incarnation_pairs'], case['prefixes']
            require(len(rows) == len(actions) and len(prefixes) == len(actions) + 1, 'row/prefix census')
            ss, aa = replay(st, actions, profile), replay(at, actions, profile)
            for n, p in enumerate(pairs):
                require(set(p) == {'source', 'target', 'reason', 'source_event', 'target_event'} and token(p['source']) and token(p['target']), 'typed pair endpoints')
                require(p['reason'] in REASONS and type(p['source_event']) is int and p['source_event'] == p['target_event'] and 0 <= p['source_event'] < len(actions), 'causal pair event inside history')
                e, verb = p['source_event'], actions[p['source_event']].split('@')[0]
                if p['reason'] == 'paired-successful-attestation':
                    saw.add('attest')
                    require(verb == 'source-attest' and rows[e]['q_invoked'] and rows[e]['source_observation']['decision'] == rows[e]['adapter_observation']['decision'] == 'source-attest:ok', 'pair authored only by delegated attestation success')
                else:
                    saw.add('restart')
                    require(verb == 'source-restart', 'pair authored only by restart advancement')
                    require(any(q['source_event'] < e and exact(q['source'][:-1] + (q['source'][-1] + 1,), p['source']) and exact(q['target'][:-1] + (q['target'][-1] + 1,), p['target']) for q in pairs[:n]), 'restart pair advances an earlier bound pair')
                require(rows[e]['binding'] == 'new-binding', 'binding label at authoring event')
            if pairs:
                saw.add('pair')
            require(all(not exact(p['source'], q['source']) and not exact(p['target'], q['target']) for i, p in enumerate(pairs) for q in pairs[:i]) and all(pairs[j - 1]['source_event'] <= pairs[j]['source_event'] for j in range(1, len(pairs))), 'unique ordered pair endpoints')
            for i, item in enumerate(prefixes):
                charge.take(1)
                audited += 1
                ledger = [p for p in pairs if p['source_event'] < i]
                ledger_sha = digest(ledger)

                def want(cond, check, expected, observed):
                    if not cond:
                        observations.append({'case': name, 'prefix': i, 'check': check, 'expected': typed(expected), 'observed': typed(observed)})
                want(item['prefix'] == i and item['pairs_sha256'] == ledger_sha and item['incarnation_pair_established_by_identity'] is False, 'prefix-ledger-binding/no-identity-authority', [i, ledger_sha, False], [item['prefix'], item['pairs_sha256'], item['incarnation_pair_established_by_identity']])
                rule, pr = item['staged_rule'], item['identity_proof']
                if rule == 'original-object-identity':
                    saw.add('identity')
                    ei = pr['source_origin']['event_index'] if isinstance(pr, dict) else None
                    ok = (isinstance(pr, dict) and pr['case'] == name and pr['prefix'] == i and type(ei) is int and 0 <= ei < i
                          and ei == pr['adapter_origin']['event_index'] and actions[ei].split('@')[0] == 'stage'
                          and ss[ei + 1]['decision'] == aa[ei + 1]['decision'] == 'stage:ok'
                          and pr['source_state_sha256'] == digest(ss[i]) and pr['adapter_state_sha256'] == digest(aa[i])
                          and pr['source_prefix_sha256'] == digest(st['events'][:i]) and all(p['source_event'] != ei for p in pairs))
                    want(ok, 'identity-proof-origin-not-pair', 'same stage origin <prefix, hash-bound, authors no pair', ei)
                else:
                    want(rule in RULES and pr is None, 'staged-rule-scope', 'strict|unrelated without proof', [rule, pr])
                sg, cg, jg = ss[i]['source_generation'], aa[i]['core']['source_generation'], aa[i]['journal']['source_generation']
                want(token(sg) and token(cg) and token(jg) and exact(sg, jg), 'typed journal-overlaid incarnations', 'tokens; journal==source', [sg, cg, jg])
                want(paired_gen(sg, cg, ledger) or (not ss[i]['source_name'] and not aa[i]['core']['source_name'] and exact(sg, cg)), 'live-incarnation-pair-bound', 'paired or pre-attestation equal', [sg, cg])
                if i:
                    a, row = actions[i - 1], rows[i - 1]
                    want(row['index'] == i - 1 and row['source_action'] == row['adapter_action'] == a and row['pairs_sha256'] == ledger_sha, 'literal action translation/row ledger', [i - 1, a, ledger_sha], [row['index'], row['source_action'], row['adapter_action'], row['pairs_sha256']])
                    want(row['binding'] in BINDINGS and (row['binding'] == 'new-binding') == any(p['source_event'] == i - 1 for p in pairs), 'binding-label-matches-ledger', BINDINGS, [row['binding'], [p['source_event'] for p in pairs]])
                    want(type(row['q_invoked']) is bool and row['justification'] == translation(a, row['q_invoked']), 'source-action-translation', translation(a, row['q_invoked']), [row['q_invoked'], row['justification']])
                    want(row['source_observation']['decision'] == ss[i]['decision'] and row['adapter_observation']['decision'] == aa[i]['decision'] and exact(ss[i]['decision'], aa[i]['decision']), 'visible refusal/decision agreement', [ss[i]['decision'], aa[i]['decision']], [row['source_observation']['decision'], row['adapter_observation']['decision']])
                    want(aa[i]['invocations'] == tuple(actions[j] for j in range(i) if rows[j]['q_invoked']), 'actual Q invocation prefix', [actions[j] for j in range(i) if rows[j]['q_invoked']], aa[i]['invocations'])
                    want(row['prestate_related'] == prefixes[i - 1]['strict_related'] and row['state_related'] == item['strict_related'], 'strict relation baseline', [prefixes[i - 1]['strict_related'], item['strict_related']], [row['prestate_related'], row['state_related']])
        except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
            if 'counter' in str(error) or 'ceiling' in str(error):
                raise
            observations.append({'case': name, 'prefix': None, 'check': 'retained-certificate-structure', 'expected': 'intact typed case', 'observed': str(error)})
    status = 'counterexample' if observations else ('supported' if audited else 'unproved')
    limitations.append('bounded to supplied typed cases; no unexecuted-order or all-order claim')
    if 'pair' not in saw:
        limitations.append('no retained incarnation pair: advancement/binding clauses vacuous on this evidence')
    if 'pair' in saw and 'restart' not in saw:
        limitations.append('no reachable paired-restart witness; chain rule unwitnessed')
    if 'attest' not in saw:
        limitations.append('no reachable successful-attestation pair-creation witness')
    if 'identity' not in saw:
        limitations.append('no original-object-identity prefix; staged non-authorization checked structurally only')
    limitations.append('no reducer/semantic-binder execution; rules are independent restatements over retained fields')
    return {'status': status, 'observations': observations, 'limitations': limitations, 'audited_prefixes': audited}


def run_controls(cases, inspect_cases, charge):
    results = []

    def pick(pred):
        return next((c for c in cases if pred(c)), None)

    def run(label, case, mutate):
        if case is None:
            results.append({'control': label, 'as_expected': None, 'status': 'unwitnessed', 'limitation': 'no genuinely reachable witness in supplied cases'})
            return
        bad = copy.deepcopy(case)
        mutate(bad)
        res = inspect_cases([bad], charge)
        results.append({'control': label, 'as_expected': res['status'] == 'counterexample', 'observed_status': res['status'], 'audited_prefixes': res['audited_prefixes'], 'witnesses': res['observations'][:2]})

    base = inspect_cases(cases, charge)
    results.append({'control': 'unaltered-retained-evidence', 'as_expected': base['status'] == 'supported', 'observed_status': base['status'], 'audited_prefixes': base['audited_prefixes'], 'witnesses': base['observations'][:2]})
    has = lambda c: bool(c.get('incarnation_pairs'))
    stage_i = lambda b: next(i for i, a in enumerate(b['source']['actions']) if a.split('@')[0] == 'stage')
    table = [
        ('dropped-incarnation-pair', has, lambda b: b['incarnation_pairs'].pop()),
        ('pair-causal-event-beyond-history', has, lambda b: b['incarnation_pairs'][0].update(source_event=len(b['source']['actions']), target_event=len(b['source']['actions']))),
        ('stage-event-authors-pair', lambda c: has(c) and any(a.split('@')[0] == 'stage' for a in c['source']['actions']), lambda b: b['incarnation_pairs'][0].update(source_event=stage_i(b), target_event=stage_i(b))),
        ('staged-identity-claims-authority', lambda c: bool(c.get('prefixes')), lambda b: b['prefixes'][-1].update(incarnation_pair_established_by_identity=True)),
        ('forged-pair-reason', has, lambda b: b['incarnation_pairs'][0].update(reason='staged-identity')),
        ('restart-pair-detached-from-parent', lambda c: any(p['reason'] == 'paired-restart' for p in c.get('incarnation_pairs', [])), lambda b: [p.update(source=p['source'][:-1] + (p['source'][-1] + 5,)) for p in b['incarnation_pairs'] if p['reason'] == 'paired-restart']),
        ('adapter-action-mistranslated', lambda c: len(c.get('rows', [])) > 1, lambda b: b['rows'][0].update(adapter_action=b['rows'][1]['adapter_action'])),
        ('false-q-invocation-on-source-handled', lambda c: any(not r['q_invoked'] for r in c.get('rows', [])), lambda b: next(r for r in b['rows'] if not r['q_invoked']).update(q_invoked=True)),
        ('forged-prefix-ledger-digest', lambda c: len(c.get('prefixes', [])) > 1, lambda b: b['prefixes'][-1].update(pairs_sha256='0' * 64)),
        ('binding-label-erased', lambda c: any(r.get('binding') == 'new-binding' for r in c.get('rows', [])), lambda b: next(r for r in b['rows'] if r['binding'] == 'new-binding').update(binding='unchanged')),
        ('erased-q-invocation-record', lambda c: any('invocations' in e.get('patch', {}) for e in c['adapter']['events']), lambda b: next(e['patch'] for e in b['adapter']['events'] if 'invocations' in e.get('patch', {})).update(invocations=())),
    ]
    for label, pred, mutate in table:
        run(label, pick(pred), mutate)
    target = pick(lambda c: has(c) and any(has(o) and not exact(o['incarnation_pairs'], c['incarnation_pairs']) for o in cases))
    donor = target and pick(lambda c: has(c) and not exact(c['incarnation_pairs'], target['incarnation_pairs']))
    run('cross-case-ledger-transplant', target if donor else None, lambda b: b.update(incarnation_pairs=copy.deepcopy(donor['incarnation_pairs'])))
    return {'controls': results, 'expected': sum(1 for r in results if r['as_expected'] is True), 'unwitnessed': [r['control'] for r in results if r.get('status') == 'unwitnessed'], 'undetected': [r['control'] for r in results if r['as_expected'] is False]}
