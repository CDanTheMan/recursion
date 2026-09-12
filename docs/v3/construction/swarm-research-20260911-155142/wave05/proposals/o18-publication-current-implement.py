"""Bounded retained-certificate obligation check: o18-publication-current.

Claim under inspection, evaluated on every prefix of each supplied
original-scale retained case (34-action profile, fixed suffix from index 19):
a FRESH publication call whose incoming request identity is absent from the
durable publication_receipts is refused as ``<verb>:source-boundary-stale``
whenever the attestation is missing, stale against the live
(source_generation, source_revision) pair, or unequal to staged_source; the
same staleness clause guards ``reconcile`` through selected_source. The
refusal is decided at the source boundary BEFORE any Q publication verdict
(paused, owner, domain, boot, permit, signature, stale-parent, content,
inventory, foreign-publication, source-generation, source-head,
generation-used), so precedence is witnessed exactly by the recorded refusal,
a zero Q-invocation delta and an unchanged Q core.

Source anchors (unchanged files; representation only -- this module never
executes a reducer, guard, audit or boundary helper):
- experiments/v3/cut-source-overnight/s_inclusive.py and s_audit.py: the
  retained/duplicate test, the attestation/staged_source boundary clause and
  the reconcile selected_source clause; delegated ``stage`` copies attestation
  into staged_source and publication growth copies staged_source into
  selected_source.
- experiments/v3/cut-source-overnight/batch-06/guard_a.py, guard_b.py and
  guard_audit.py: identical clauses evaluated over the adapter-owned journal.
- experiments/v3/cut-source-overnight/batch-06/a_audit.py: when the guard does
  not delegate, the whole Q core is unchanged and core ``done`` equals the
  bitmask of the actual invocation list over the fixed Q subprofile.
- experiments/v3/cut-publication/q_domain.py, q_audit.py, q_inclusive.py:
  incoming-request identities (pub-rival suffixes the staged request; retries
  reuse the first receipt request) and the Q verdict order this refusal masks.
- experiments/v3/cut-source-overnight/s_domain.py: add_with_suffix
  'scale-eight-action-race' (prefix 11, antichain core 8, suffix at 19).
- experiments/v3/cut-source-overnight/batch-05/semantic.py: exact/digest,
  imported for the retained typed representation only.
- experiments/v3/cut-source-overnight/batch-06/adapter_traces.py: retained
  event/patch trace shape replayed here incrementally; no reducer runs.

Finite audit accounting: charge.take(1) is taken before each per-prefix
inspection of each case (every repetition counts); audited_prefixes reports
the number of completed prefix inspections. Findings cover only the supplied
cases: no all-order reachability, no accepted-relation claim, no scientific
PASS.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel

exact, digest = rel.exact, rel.digest

PUB = ('pub-commit', 'pub-rival', 'pub-retry', 'pub-retry-conflict',
       'pub-retry-foreign')
JOURNAL = ('registration', 'attempts', 'append_log', 'append_receipts',
           'append_reply', 'source_revision', 'collection', 'collected',
           'attestation', 'staged_source', 'selected_source',
           'source_generation')
SOURCE_ONLY = ('register:', 'attempt:', 'atomic:', 'append:', 'collect:',
               'source:')
LOCAL_FIELDS = set(JOURNAL) | {'done', 'decision', 'source_name',
                               'source_head', 'source_version'}


def key(action):
    return action.split('@')[0]


def source_only(k):
    return k.startswith(SOURCE_ONLY) or k in ('append-lose-reply',
                                              'collect-open')


def jsafe(x):
    if isinstance(x, dict):
        return {str(k): jsafe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsafe(v) for v in x]
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return repr(x)


class Corrupt(Exception):
    pass


class Replay:
    """Incremental replay of one retained event/patch trace, binding every
    event digest. Executes no transition function."""

    def __init__(self, trace):
        if trace['side'] not in ('source', 'adapter'):
            raise Corrupt('unknown side')
        if len(trace['actions']) != len(trace['events']) \
                or len(set(trace['actions'])) != len(trace['actions']):
            raise Corrupt('literal occurrence inventory')
        self.trace, self.adapter = trace, trace['side'] == 'adapter'
        self.current, self.position = copy.deepcopy(trace['initial']), 0

    def advance(self):
        action = self.trace['actions'][self.position]
        event = self.trace['events'][self.position]
        if event['action'] != action:
            raise Corrupt('literal occurrence')
        if set(self.trace['profile']['requires'][action]) \
                - set(self.trace['actions'][:self.position]):
            raise Corrupt('outer dependency')
        if digest(self.current) != event['before_sha256']:
            raise Corrupt('prestate binding')
        nxt = copy.deepcopy(self.current)
        for field, value in event['patch'].items():
            if self.adapter and field in ('core', 'journal'):
                nxt[field].update(value)
            else:
                nxt[field] = value
        if digest(nxt) != event['after_sha256']:
            raise Corrupt('poststate binding')
        self.current, self.position = nxt, self.position + 1
        return nxt


def merged(state, adapter):
    return dict(state['core'], **state['journal']) if adapter else state


def incoming_request(k, view):
    staged, receipts = view['staged'], view['publication_receipts']
    if k == 'pub-rival':
        return staged[0].request + '-rival' if staged else None
    if k in ('pub-retry', 'pub-retry-conflict', 'pub-retry-foreign') \
            and receipts:
        return receipts[0][0].request
    return staged[0].request if staged else None


def publication_expectation(k, view):
    """Independent fresh/duplicate + boundary expectation from inspected
    ledger fields only; never a Q verdict."""
    request = incoming_request(k, view)
    if request is not None and any(r[0].request == request
                                   for r in view['publication_receipts']):
        return {'kind': 'delegated-duplicate', 'invoked': True,
                'request': request}
    boundary = (bool(view['attestation'])
                and tuple(view['attestation'][:2]) == (view['source_generation'],
                                                       view['source_revision'])
                and exact(view['staged_source'], view['attestation']))
    if boundary:
        return {'kind': 'delegated', 'invoked': True, 'request': request}
    return {'kind': 'fresh-boundary-refusal', 'invoked': False,
            'request': request, 'decision': k + ':source-boundary-stale'}


def reconcile_expectation(view):
    current = (bool(view['selected_source'])
               and tuple(view['selected_source'][:2])
               == (view['source_generation'], view['source_revision']))
    if current:
        return {'kind': 'delegated', 'invoked': True}
    return {'kind': 'boundary-refusal', 'invoked': False,
            'decision': 'reconcile:source-boundary-stale'}


def attestation_expectation(view):
    """Guard-clause expectation; None where fixture attempt-map bytes decide
    (not re-derived here)."""
    capture = view['collection']
    if not capture or not view['cut_delivery']:
        return 'source-attest:no-captured-source'
    if tuple(capture[:2]) != (view['source_generation'],
                            view['source_revision']):
        return 'source-attest:stale-collection'
    got = tuple(sorted(view['collected']))
    if tuple(i for i, _ in got) != tuple(range(capture[4])) or any(
            i >= len(view['append_log'])
            or not exact(raw, view['append_log'][i]) for i, raw in got):
        return 'source-attest:incomplete-inventory'
    if not exact(capture[2], view['registration']):
        return 'source-attest:incomplete-registry'
    return None


def parent_shadow(view):
    """Descriptive Q stale-parent shadow computed from fields only."""
    envelope = view['staged'][0] if view['staged'] else None
    parent = getattr(envelope, 'parent', None)
    revision = getattr(envelope, 'expected_revision', None)
    live_parent = view['selected'].generation if view['selected'] else ''
    return {'envelope_cut': getattr(envelope, 'cut', None),
            'envelope_parent': parent,
            'envelope_expected_revision': revision,
            'live_parent': live_parent,
            'live_revision': view['publication_revision'],
            'q_stale_parent_would_hold': type(revision) is int
            and revision == view['publication_revision']
            and parent == live_parent}


def journal_delta(k, journal, view, decision, delegated, revision_grew):
    """Expected journal/EXTRA poststate under the documented ledger rules."""
    expected = dict(journal)
    if k == 'source-attest' and decision == 'source-attest:ok':
        expected['attestation'] = (journal['collection'][0],
                                   journal['collection'][1],
                                   view['cut_delivery'])
    if delegated:
        if k == 'source-restart':
            generation = journal['source_generation']
            expected['source_generation'] = generation[:-1] \
                + (generation[-1] + 1,)
        elif k == 'stage' or k.startswith('stage-'):
            expected['staged_source'] = journal['attestation']
        if revision_grew:
            expected['selected_source'] = journal['staged_source']
    return expected


def audit_prefix(i, s_state, a_state, actions, q_actions, prefixes, mismatch):
    expected_done = sum(1 << actions.index(a) for a in actions[:i])
    if s_state['done'] != expected_done or a_state['done'] != expected_done:
        mismatch('done-mask', i)
    expected_core = sum(1 << q_actions.index(a)
                        for a in a_state['invocations'])
    if a_state['core']['done'] != expected_core:
        mismatch('q-invocation-mask', i)
    journal_diff = [f for f in JOURNAL
                    if not exact(s_state[f], a_state['journal'][f])]
    if prefixes is not None and i < len(prefixes) \
            and list(prefixes[i].get('differing_journal_fields', ())) \
            != journal_diff:
        mismatch('journal-certificate',
                 {'prefix': i, 'recomputed': journal_diff,
                  'recorded': prefixes[i].get('differing_journal_fields')})
    if i == 0 and (s_state['decision'] != 'initial'
                   or a_state['decision'] != 'initial'
                   or s_state['attestation']
                   or a_state['journal']['attestation']
                   or s_state['publication_receipts']
                   or a_state['core']['publication_receipts']):
        mismatch('initial-boundary-state')


def audit_transition(i, case, actions, before_s, before_a, after_s, after_a,
                     rows, obs, mismatch):
    action, k = actions[i], key(actions[i])
    row = rows[i] if i < len(rows) else None
    invoked = len(after_a['invocations']) > len(before_a['invocations'])
    if invoked and not exact(after_a['invocations'],
                             before_a['invocations'] + (action,)):
        mismatch('invocation-identity', action)
    if not invoked and not exact(before_a['invocations'],
                                 after_a['invocations']):
        mismatch('invocation-list', action)
    bit = 1 << actions.index(action)
    if after_s['done'] != before_s['done'] | bit \
            or after_a['done'] != before_a['done'] | bit:
        mismatch('done-bit', action)
    if row is not None:
        if row.get('index') != i or row.get('source_action') != action \
                or row.get('adapter_action') != action:
            mismatch('row-identity', action)
        if bool(row.get('q_invoked')) != invoked:
            mismatch('q-invoked-flag', row.get('q_invoked'))
    sdec, adec = after_s['decision'], after_a['decision']
    if sdec != adec:
        mismatch('visible-decision',
                 {'action': action, 'source': sdec, 'adapter': adec})
    if row is not None and (row.get('source_observation', {}).get('decision')
                            != sdec or
                            row.get('adapter_observation', {}).get('decision')
                            != adec):
        mismatch('recorded-decision', action)
    view_s, view_a = merged(before_s, False), merged(before_a, True)
    if k == 'source-attest':
        exp_s, exp_a = (attestation_expectation(v) for v in (view_s, view_a))
        obs['attestations'].append(jsafe({
            'action': action, 'expected_source': exp_s,
            'expected_adapter': exp_a, 'observed': sdec,
            'q_invoked': invoked, 'capture': view_a['collection'],
            'collected_indices': [x[0] for x in view_a['collected']]}))
        for side, exp in (('source', exp_s), ('adapter', exp_a)):
            if exp is not None and sdec != exp:
                mismatch('attestation-' + side,
                         {'expected': exp, 'observed': sdec})
        if (exp_s is not None or exp_a is not None) and invoked:
            mismatch('refused-attestation-invoked-Q', sdec)
    elif k in PUB:
        exp_s = publication_expectation(k, view_s)
        exp_a = publication_expectation(k, view_a)
        if exp_s['invoked'] != invoked or exp_a['invoked'] != invoked:
            mismatch('publication-invocation',
                     {'action': action, 'observed_invoked': invoked,
                      'expected_source': exp_s, 'expected_adapter': exp_a})
        for side, exp in (('source', exp_s), ('adapter', exp_a)):
            if exp.get('decision') and sdec != exp['decision']:
                mismatch('publication-' + side,
                         {'expected': exp['decision'], 'observed': sdec})
        if exp_s['kind'] == exp_a['kind'] == 'fresh-boundary-refusal':
            obs['boundary_witnesses'].append(jsafe({
                'action': action,
                'kind': 'fresh-publication-boundary-refusal',
                'request': exp_s['request'],
                'expected': exp_s['decision'], 'observed_source': sdec,
                'observed_adapter': adec, 'q_invoked': invoked,
                'q_parent_shadow': parent_shadow(view_s)}))
    elif k == 'reconcile':
        exp_s, exp_a = reconcile_expectation(view_s), \
            reconcile_expectation(view_a)
        if exp_s['invoked'] != invoked or exp_a['invoked'] != invoked:
            mismatch('reconcile-invocation', action)
        for side, exp in (('source', exp_s), ('adapter', exp_a)):
            if exp.get('decision') and sdec != exp['decision']:
                mismatch('reconcile-' + side,
                         {'expected': exp['decision'], 'observed': sdec})
        if exp_s['kind'] == exp_a['kind'] == 'boundary-refusal':
            obs['boundary_witnesses'].append(jsafe({
                'action': action, 'kind': 'reconcile-boundary-refusal',
                'expected': exp_s['decision'], 'observed_source': sdec,
                'observed_adapter': adec, 'q_invoked': invoked,
                'selected_source': view_a['selected_source'],
                'live': (view_a['source_generation'],
                         view_a['source_revision'])}))
    delegated_s = not source_only(k) and k != 'source-attest'
    grew_s = after_s['publication_revision'] > before_s['publication_revision']
    grew_a = (after_a['core']['publication_revision']
              > before_a['core']['publication_revision'])
    if invoked or adec != k + ':ok' or k == 'source-attest':
        if not exact(after_a['journal'],
                     journal_delta(k, before_a['journal'], view_a, adec,
                                   invoked, grew_a)):
            mismatch('adapter-ledger', action)
    elif not exact(after_a['journal']['source_generation'],
                   before_a['journal']['source_generation']):
        mismatch('adapter-generation', action)
    if delegated_s or k == 'source-attest' or sdec != k + ':ok':
        if not exact({f: after_s[f] for f in JOURNAL},
                     journal_delta(k, {f: before_s[f] for f in JOURNAL},
                                   before_s, sdec, delegated_s, grew_s)):
            mismatch('source-ledger', action)
    if sdec == k + ':ok' and not delegated_s and k != 'source-attest' \
            and any(not exact(after_s[f], before_s[f])
                    for f in before_s if f not in LOCAL_FIELDS):
        mismatch('source-handled-scope', action)
    if not invoked and not exact(before_a['core'], after_a['core']):
        mismatch('core-changed-without-Q', action)
    if sdec != k + ':ok' and any(not exact(after_s[f], before_s[f])
                                 for f in before_s
                                 if f not in ('done', 'decision')):
        mismatch('refused-source-mutation', action)


def inspect_cases(cases, charge):
    limitations = [
        'only the supplied retained cases are audited; no all-order '
        'reachability, accepted-relation or scientific-PASS claim is made',
        'attestation expectation re-derives capture currency, collected-index '
        'coverage/bytes and registration identity; the fixture attempt-map '
        'equality is not re-derived, so a passing prefix yields no prediction',
        'Q verdicts (including stale-parent) are shadow field computations; '
        'precedence is witnessed only by the recorded refusal, a zero '
        'invocation delta and an unchanged Q core',
        'common-field relation rows need the causal incarnation ledger and are '
        'not re-derived; only journal-field certificates are recomputed',
    ]
    report = {'status': 'unproved', 'observations': [],
              'limitations': limitations, 'audited_prefixes': 0}
    failures, applicable, witnesses, complete = [], 0, 0, True
    for case in cases:
        obs = {'case': case.get('case') if isinstance(case, dict) else None,
               'applicable': False, 'audited_prefixes': 0, 'attestations': [],
               'boundary_witnesses': [], 'suffix_decisions': [],
               'mismatches': []}
        report['observations'].append(obs)

        def mismatch(kind, detail=None, obs=obs):
            obs['mismatches'].append({'kind': kind, 'detail': jsafe(detail)})
            failures.append({'case': obs['case'], 'kind': kind})

        try:
            src, adp = Replay(case['source']), Replay(case['adapter'])
            actions = tuple(case['source']['actions'])
        except (Corrupt, KeyError, TypeError, IndexError) as error:
            mismatch('trace-shape', str(error))
            continue
        if actions != tuple(case['source']['profile']['actions']) \
                or actions != tuple(case['adapter']['actions']):
            mismatch('action-inventory')
        q_actions = tuple(a for a in actions if not source_only(key(a)))
        if tuple(case['adapter'].get('q_profile', {}).get('actions', ())) \
                != q_actions:
            mismatch('q-subprofile')
        rows = case.get('rows') or ()
        if len(rows) != len(actions):
            mismatch('row-inventory',
                     {'rows': len(rows), 'actions': len(actions)})
        obs['applicable'] = (any(key(a) == 'source-attest' for a in actions)
                             and any(key(a) in PUB for a in actions)
                             and any(key(a) == 'reconcile' for a in actions))
        applicable += bool(obs['applicable'])
        previous, broken = None, False
        for i in range(len(actions) + 1):
            try:
                charge.take(1)
            except Exception as error:
                complete = False
                limitations.append('charge exhausted at %r prefix %d: %s'
                                   % (obs['case'], i, error))
                break
            try:
                audit_prefix(i, src.current, adp.current, actions, q_actions,
                             case.get('prefixes'), mismatch)
                if previous is not None:
                    audit_transition(i - 1, case, actions, previous[0],
                                     previous[1], src.current, adp.current,
                                     rows, obs, mismatch)
                if i > 19:
                    obs['suffix_decisions'].append(
                        {'index': i - 1, 'action': actions[i - 1],
                         'decision': src.current['decision']})
                report['audited_prefixes'] += 1
                obs['audited_prefixes'] += 1
            except (Corrupt, KeyError, TypeError, IndexError, ValueError,
                    AttributeError) as error:
                mismatch('inspection-error', 'prefix %d: %s' % (i, error))
                broken = True
                break
            if i < len(actions):
                previous = (src.current, adp.current)
                try:
                    src.advance()
                    adp.advance()
                except (Corrupt, KeyError, TypeError, IndexError) as error:
                    mismatch('trace-integrity', 'event %d: %s' % (i, error))
                    broken = True
                    break
        if broken and not obs['mismatches']:
            mismatch('incomplete-replay')
        witnesses += len(obs['boundary_witnesses'])
        if not complete:
            break
    report['observations'].insert(0, {
        'kind': 'accounting', 'cases': len(cases),
        'applicable_cases': applicable,
        'boundary_refusal_witnesses': witnesses,
        'audited_prefixes': report['audited_prefixes'],
        'mismatches': len(failures)})
    if failures:
        report['status'] = 'counterexample'
    elif not applicable:
        report['status'] = 'not_applicable'
    elif not complete or not witnesses:
        report['status'] = 'unproved'
    else:
        report['status'] = 'supported'
    return report
