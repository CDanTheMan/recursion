"""Bounded retained-evidence check + adversarial controls for typed patch restoration.

Obligation o23-trace-patches (parent goal-recursion-v2-execution-fabric). Retained-certificate
inspection only: canonical hashing, typed-shape equality and re-derivation of retained fields.
No reducer, model, or boundary-helper execution; nothing is imported from checked code.

Source anchors (representation reference):
  patch/restore semantics   experiments/v3/cut-source-overnight/batch-06/adapter_traces.py (trace_event, restore)
  retained case shape       experiments/v3/eight-hour-research-20260910-01a08a22/check.py (run_history, audit_case)
  typed/exact/digest/observation  experiments/v3/cut-source-overnight/batch-05/semantic.py
  journal EXTRA fields      experiments/v3/cut-source-overnight/s_domain.py
  required defect classes   docs/v3/construction/swarm-research-20260911-155142/wave04/review-defects.json

digest() is canonical-JSON sha256: blind to tuple-vs-list-vs-namedtuple. typed() is the semantic
equality layer, so outer-hash-preserving mutations still reach detection through typed journal
diffs, the no-list typed-domain scan, invocation masks and observation fields. Controls are tagged
synthetic-unreachable: they cannot arise from original reducers; only a 'counterexample' verdict on
UNMUTATED cases is an original-domain finding.

Accounting: charge.take(1) precedes every inspected case prefix, including every repeated
inspect_cases call; audited_prefixes reports inspected prefixes.

Genuinely-reachable-witness needs: 'tuple-list-loss' needs a source patch carrying a tuple under a
DIFF_FIELDS key; 'rehashed-journal-field-loss' needs an adapter journal 'attempts' patch;
'chronological-event-swap' needs >=2 source events. Missing witnesses are reported as limitations.
"""
import copy, hashlib, json

EXTRA = ('registration', 'attempts', 'append_log', 'append_receipts', 'append_reply',
         'source_revision', 'collection', 'collected', 'attestation', 'staged_source',
         'selected_source')
DIFF_FIELDS = EXTRA + ('source_generation',)


def canonical(x): return json.dumps(x, sort_keys=True, separators=(',', ':'))
def digest(x): return hashlib.sha256(canonical(x).encode()).hexdigest()
def exact(a, b): return typed(a) == typed(b)


def typed(x):
    if isinstance(x, dict): return ['dict', [[k, typed(v)] for k, v in sorted(x.items())]]
    if isinstance(x, (list, tuple)): return [type(x).__name__, [typed(v) for v in x]]
    return [type(x).__name__, x]


class Refusal(Exception):
    def __init__(self, check, expected, observed):
        super().__init__(check)
        self.witness = {'check': check, 'expected': expected, 'observed': observed}


def need(ok, check, expected, observed):
    if not ok: raise Refusal(check, expected, observed)


def source_only(a):
    k = a.split('@')[0]
    return k.startswith(('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:'))
        or k in ('append-lose-reply', 'collect-open')


def list_nodes(x, path):
    if isinstance(x, list): return [path]
    items = x.items() if isinstance(x, dict) else enumerate(x) if isinstance(x, tuple) else ()
    return [p for k, v in items for p in list_nodes(v, path + '/' + str(k))]


def observation(state, action):
    out = {'decision': state['decision']}; k = action.split('@')[0]
    if k.startswith('append:') or k == 'append-lose-reply': out['append_reply'] = state['append_reply']
    if k.startswith('pub-'): out['publication_reply'] = state['publication_reply']
    return out


def core_view(a):
    return dict(a['core'], **{k: a['journal'][k] for k in EXTRA}, decision=a['decision'])


def apply(side, current, patch):
    for k, v in patch.items():
        if side == 'adapter' and k in ('core', 'journal'): current[k].update(v)
        else: current[k] = v


def _inspect_case(case, charge, observations):
    source, adapter, rows = case['source'], case['adapter'], case['rows']
    actions, profile = source['actions'], source['profile']
    need(exact(actions, adapter['actions']), 'literal-visible-schedule',
         typed(actions), typed(adapter['actions']))
    need(len(source['events']) == len(adapter['events']) == len(actions),
         'complete-visible-events', len(actions),
         [len(source['events']), len(adapter['events'])])
    need(len(rows) == len(actions) and len(case['prefixes']) == len(actions) + 1,
         'complete-retained-rows', [len(actions), len(actions) + 1],
         [len(rows), len(case['prefixes'])])
    q_actions = tuple(a for a in profile['actions'] if not source_only(a))
    q_profile = dict(copy.deepcopy(profile), actions=q_actions,
                     requires={a: () for a in q_actions})
    need(exact(adapter['q_profile'], q_profile), 'fixed-q-occurrence-profile',
         typed(q_profile), typed(adapter['q_profile']))
    ss, aa = copy.deepcopy(source['initial']), copy.deepcopy(adapter['initial'])
    executed, invocations, audited, diff = [], (), 0, None
    for i in range(len(actions) + 1):
        charge.take(1)
        audited += 1
        if i:
            action, row = actions[i - 1], rows[i - 1]
            need(row['index'] == i - 1 and row['source_action'] == row['adapter_action'] == action,
                 'chronological-row-binding', [i - 1, action],
                 [row['index'], row['source_action'], row['adapter_action']])
            need(action not in executed and set(profile['requires'][action]) <= set(executed),
                 'occurrence-order-dependencies', sorted(executed), action)
            for side, trace, cur in (('source', source, ss), ('adapter', adapter, aa)):
                ev = trace['events'][i - 1]
                need(ev['action'] == action, 'literal-event-occurrence', action, ev['action'])
                need(digest(cur) == ev['before_sha256'], 'prestate-hash-binding',
                     ev['before_sha256'], digest(cur))
                apply(side, cur, ev['patch'])
                need(digest(cur) == ev['after_sha256'], 'poststate-hash-binding',
                     ev['after_sha256'], digest(cur))
            executed.append(action)
            invocations += (action,) if row['q_invoked'] else ()
            need(digest(ss) == row['source_sha256'] and digest(aa) == row['adapter_sha256'],
                 'retained-row-hash-binding', [row['source_sha256'], row['adapter_sha256']],
                 [digest(ss), digest(aa)])
            need(exact(observation(ss, action), row['source_observation']) and
                 exact(observation(core_view(aa), action), row['adapter_observation']),
                 'visible-observation-fields', typed(row['source_observation']),
                 typed(observation(ss, action)))
        mask = sum(1 << profile['actions'].index(a) for a in executed)
        need(ss['done'] == mask and aa['done'] == mask, 'completion-mask', mask,
             [ss['done'], aa['done']])
        need(exact(aa['invocations'], invocations), 'actual-q-invocation-mask',
             typed(invocations), typed(aa['invocations']))
        need(aa['core']['done'] == sum(1 << q_actions.index(a) for a in aa['invocations']),
             'q-core-completion', 'sum of invoked positions', aa['core']['done'])
        need(set(ss) == set(source['initial']), 'source-frame',
             sorted(source['initial']), sorted(ss))
        need(set(aa) == set(adapter['initial']) and set(aa['journal']) ==
             set(adapter['initial']['journal']) and set(aa['core']) ==
             set(adapter['initial']['core']), 'adapter-frames', 'initial key frames',
             [sorted(aa), sorted(aa['journal']), sorted(aa['core'])])
        stray = list_nodes(ss, 'source') + list_nodes(aa, 'adapter')
        need(not stray, 'tuple-list-typed-domain', 'no list nodes in typed state', stray)
        diff = [k for k in DIFF_FIELDS if not exact(ss[k], aa['journal'][k])]
        need(diff == list(case['prefixes'][i]['differing_journal_fields']),
             'typed-journal-field-diff',
             list(case['prefixes'][i]['differing_journal_fields']), diff)
    observations.append({'case': case['case'], 'prefixes': len(actions) + 1,
                         'q_invocations': len(invocations), 'final_journal_diff': diff})
    return audited


def inspect_cases(cases, charge):
    if not isinstance(cases, list) or not cases:
        return {'status': 'not_applicable', 'observations': [],
                'limitations': ['no typed restored case objects supplied'], 'audited_prefixes': 0}
    observations, failures, audited = [], [], 0
    for case in cases:
        name = case.get('case') if isinstance(case, dict) else None
        try:
            audited += _inspect_case(case, charge, observations)
        except Refusal as r:
            failures.append(dict(case=name, domain='retained-evidence', **r.witness))
        except (KeyError, IndexError, TypeError, AttributeError) as error:
            failures.append({'case': name, 'check': 'retained-evidence-schema',
                             'expected': 'complete typed case object', 'observed': repr(error)})
    return {'status': 'counterexample' if failures else 'supported',
            'observations': observations + failures,
            'limitations': ['typed journal diff covers EXTRA+source_generation only; pair-sensitive '
                            'common-field equality remains certified only by the retained rows'],
            'audited_prefixes': audited}


def _rehash(trace, rows):
    current = copy.deepcopy(trace['initial'])
    for j, event in enumerate(trace['events']):
        event['before_sha256'] = digest(current)
        apply(trace['side'], current, event['patch'])
        event['after_sha256'] = digest(current)
        rows[j][trace['side'] + '_sha256'] = digest(current)


def run_controls(cases, inspect_cases, charge):
    baseline = inspect_cases(cases, charge)
    total, controls, limitations = baseline['audited_prefixes'], [], []

    def control(label, locate, mutate):
        nonlocal total
        hit = locate() if isinstance(cases, list) and cases else None
        if hit is None:
            limitations.append({'control': label, 'limitation':
                                'no genuinely reachable witness in supplied cases'})
            return
        bad = copy.deepcopy(cases)
        mutate(bad, *hit)
        verdict = inspect_cases(bad, charge)
        total += verdict['audited_prefixes']
        detected = verdict['status'] == 'counterexample'
        controls.append({'control': label, 'detected': detected,
                         'attributable': baseline['status'] == 'supported',
                         'domain': 'synthetic-unreachable',
                         'audited_prefixes': verdict['audited_prefixes'],
                         'witness': verdict['observations'][-1:] if detected else []})

    control('dropped-visible-event', lambda: (0,),
            lambda b, ci: b[ci]['adapter']['events'].pop(0))
    control('omitted-patch-field',
            lambda: next(((ci, i) for ci, c in enumerate(cases)
                          for i, e in enumerate(c['source']['events']) if e['patch']), None),
            lambda b, ci, i: b[ci]['source']['events'][i]['patch'].pop(
                next(iter(b[ci]['source']['events'][i]['patch']))))
    control('tuple-list-loss',
            lambda: next(((ci, i, k) for ci, c in enumerate(cases)
                          for i, e in enumerate(c['source']['events'])
                          for k, v in e['patch'].items()
                          if k in DIFF_FIELDS and isinstance(v, tuple)), None),
            lambda b, ci, i, k: b[ci]['source']['events'][i]['patch'].__setitem__(
                k, json.loads(canonical(b[ci]['source']['events'][i]['patch'][k]))))
    control('rehashed-journal-field-loss',
            lambda: next(((ci, i) for ci, c in enumerate(cases)
                          for i, e in enumerate(c['adapter']['events'])
                          if 'attempts' in e['patch'].get('journal', {})), None),
            lambda b, ci, i: (b[ci]['adapter']['events'][i]['patch']['journal']
                              .__setitem__('attempts', ()),
                              _rehash(b[ci]['adapter'], b[ci]['rows'])))
    control('chronological-event-swap',
            lambda: (0,) if len(cases[0]['source']['events']) > 1 else None,
            lambda b, ci: b[ci]['source']['events']
            .__setitem__(slice(0, 2), b[ci]['source']['events'][1::-1]))
    control('invocation-mask-forgery', lambda: (0, 0) if cases[0]['rows'] else None,
            lambda b, ci, i: b[ci]['rows'][i]
            .__setitem__('q_invoked', not b[ci]['rows'][i]['q_invoked']))
    control('prefix-journal-diff-forgery',
            lambda: (0, len(cases[0]['source']['actions'])),
            lambda b, ci, i: b[ci]['prefixes'][i].__setitem__(
                'differing_journal_fields',
                list(b[ci]['prefixes'][i]['differing_journal_fields']) + ['__forged__']))

    return {'baseline_status': baseline['status'], 'controls': controls,
            'control_count': len(controls), 'limitations': limitations,
            'audited_prefixes_total': total,
            'note': 'detections are unreachable synthetic mutations, not original-domain '
                    'counterexamples; no accepted PASS is claimed'}
