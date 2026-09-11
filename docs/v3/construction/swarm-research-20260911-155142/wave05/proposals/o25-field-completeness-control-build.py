"""Bounded retained-evidence control: exhaustive common-field inventory.

Obligation o25-field-completeness (parent goal-recursion-v2-execution-fabric).
Independently audits that retained source/adapter comparisons account for every
actual typed field on every audited prefix of a restored c.run_history case:
  * common domain = AUTH+FLOW+VIEW minus done/decision (semantic.py FIELDS),
  * adapter journal extras = s_domain.EXTRA + source_generation
    (a_domain.py initial/view journal keys),
  * each prefix row's reported differing-field sets must equal this module's
    independently recomputed sets over the actual retained key unions.

Source anchors (unchanged originals; representation helpers only):
  semantic.py        FIELDS, typed/exact/digest/signed/field_pair, pair rows
  s_domain.py        EXTRA journal fields; source states add EXTRA to Q frame
  a_domain.py        journal = DEFAULTS + source_generation; core = Q frame
  adapter_traces.py  related/comparison/restore: retained row and patch shapes
  identity.py        staged_rule values and identity_proof row shape
  check.py           audit_case chronology: incarnation_pairs grow by at most
                     one row per action; source_event/target_event = index

No reducer, guard, audit-check or boundary helper is executed; states are
reconstructed only by replaying retained sha256-bound event patches.

Finite accounting: inspect_cases calls charge.take(1) BEFORE inspecting each
case prefix; every repetition counts, including repeats inside run_controls.
run_controls additionally takes 1 per case scanned while selecting witnesses.

inspect_cases(cases, charge) -> JSON-safe
  {status, observations, limitations, audited_prefixes}.
  supported       every audited prefix consistent on the full actual key union
  counterexample  falsifiable expected/observed witness retained
  unproved        retained evidence too incomplete to decide
  not_applicable  no usable typed case objects
Fields never observed differing in the retained domain stay in limitations:
dropped-report detection is unwitnessed for them (a genuinely reachable
difference is required). State-hash breaks are reported as unreachable-mutation
detections, distinct from original-domain semantic counterexamples.

run_controls(cases, inspect, charge): deepcopy adversarial mutations of real
typed cases; each control records detection, stage ('semantic' vs 'hash'
binding) and its witness prefix; unwitnessed controls persist as limitations.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel

EXCLUDED = ('done', 'decision')
JOURNAL = tuple(rel.s.EXTRA) + ('source_generation',)
REQUIRED = ('source', 'adapter', 'rows', 'prefixes', 'incarnation_pairs')


class Failure(Exception):
    def __init__(self, stage, witness):
        super().__init__(stage)
        self.stage, self.witness = stage, witness


def _replay(trace):
    adapter = trace.get('side') == 'adapter'
    actions, events = trace['actions'], trace['events']
    if len(actions) != len(events):
        raise Failure('hash', {'check': 'event-cardinality', 'expected': len(actions),
                               'observed': len(events)})
    states, done = [copy.deepcopy(trace['initial'])], 0
    q_actions = trace.get('q_profile', {}).get('actions', ())
    for i, (action, event) in enumerate(zip(actions, events)):
        current = states[-1]
        if event.get('action') != action or rel.digest(current) != event.get('before_sha256'):
            raise Failure('hash', {'event_index': i, 'check': 'prestate-binding'})
        current = copy.deepcopy(current)
        for key, value in event.get('patch', {}).items():
            if adapter and key in ('core', 'journal'):
                current[key].update(copy.deepcopy(value))
            else:
                current[key] = copy.deepcopy(value)
        done |= 1 << actions.index(action)
        if rel.digest(current) != event.get('after_sha256') or current.get('done') != done:
            raise Failure('hash', {'event_index': i, 'check': 'poststate-binding'})
        if adapter and current['core']['done'] != sum(
                1 << q_actions.index(a) for a in current['invocations']):
            raise Failure('hash', {'event_index': i, 'check': 'q-invocation-mask'})
        states.append(current)
    return states


def _prefix_pairs(case, prefix):
    return [row for row in case['incarnation_pairs']
            if row['source_event'] < prefix and row['target_event'] < prefix]


def _staged(state, adapter):
    return state['core']['staged'] if adapter else state['staged']


def _origin(trace, states, prefix):
    adapter = trace.get('side') == 'adapter'
    current = _staged(states[prefix], adapter)
    if not current:
        return None
    for i in range(prefix - 1, -1, -1):
        if not rel.exact(_staged(states[i + 1], adapter), current):
            return None
        event = trace['events'][i]
        if event['action'].split('@')[0] == 'stage' and states[i + 1]['decision'] == 'stage:ok':
            return i, event['action']
    return None


def _identical(a, b):
    if not (type(a) is tuple and type(b) is tuple and len(a) == len(b) == 2):
        return False
    ea, eb = a[0], b[0]
    return (type(ea) is rel.q.Envelope and type(eb) is rel.q.Envelope
            and rel.exact(a, b) and rel.signed(ea) and rel.signed(eb)
            and a[1] == rel.q.raw_cut(ea.cut) and b[1] == rel.q.raw_cut(eb.cut))


def _reported(row, key, allowed, base):
    value = row.get(key)
    if not (type(value) is list and len(value) == len(set(value))
            and all(type(k) is str for k in value)):
        raise Failure('semantic', dict(base, check=key + '-shape', observed=rel.typed(value)))
    if set(value) - set(allowed):
        raise Failure('semantic', dict(base, check=key + '-inventory',
                                       expected='subset of compared domain',
                                       observed=sorted(set(value) - set(allowed))))


def _inspect_prefix(case, ss, aa, prefix):
    s_state, a_state = ss[prefix], aa[prefix]
    core, journal, row = a_state['core'], a_state['journal'], case['prefixes'][prefix]
    base = {'case': case.get('case'), 'prefix': prefix}
    inventories = ((set(core) - set(EXCLUDED), set(rel.FIELDS), 'core-field-inventory'),
                   (set(s_state) - set(EXCLUDED), set(rel.FIELDS) | set(rel.s.EXTRA),
                    'source-field-inventory'),
                   (set(journal), set(JOURNAL), 'journal-field-inventory'))
    for actual, expected, check in inventories:
        if actual != expected:
            raise Failure('semantic', dict(base, check=check, expected=sorted(expected),
                                           observed=sorted(actual)))
    _reported(row, 'strict_differing_common_fields', rel.FIELDS, base)
    _reported(row, 'differing_common_fields', rel.FIELDS, base)
    _reported(row, 'differing_journal_fields', JOURNAL, base)
    pairs = _prefix_pairs(case, prefix)
    if rel.digest(pairs) != row.get('pairs_sha256'):
        raise Failure('semantic', dict(base, check='prefix-pair-ledger',
                                       expected=row.get('pairs_sha256'),
                                       observed=rel.digest(pairs)))
    strict = [k for k in rel.FIELDS if not rel.field_pair(s_state, core, k, pairs)]
    journal_diff = [k for k in JOURNAL if not rel.exact(s_state[k], journal[k])]
    left, right = _origin(case['source'], ss, prefix), _origin(case['adapter'], aa, prefix)
    identity_ok = bool(left and left == right
                       and _identical(s_state['staged'], core['staged']))
    rule = 'strict' if 'staged' not in strict else (
        'original-object-identity' if identity_ok else 'unrelated')
    differing = [k for k in strict if k != 'staged' or not identity_ok]
    expected_row = {'strict_differing_common_fields': strict,
                    'differing_common_fields': differing,
                    'differing_journal_fields': journal_diff,
                    'strict_related': not strict and not journal_diff,
                    'related': not differing and not journal_diff,
                    'staged_rule': rule,
                    'incarnation_pair_established_by_identity': False}
    for key, expected in expected_row.items():
        if row.get(key) != expected:
            raise Failure('semantic', dict(base, check=key, expected=expected,
                                           observed=row.get(key)))
    proof = row.get('identity_proof')
    if rule == 'original-object-identity':
        if not (type(proof) is dict and proof.get('case') == case.get('case')
                and proof.get('prefix') == prefix):
            raise Failure('semantic', dict(base, check='identity-proof-binding'))
    elif proof is not None:
        raise Failure('semantic', dict(base, check='identity-proof-absent',
                                       expected=None, observed='present'))
    if prefix:
        crow = case['rows'][prefix - 1]
        consistent = (crow.get('differing_common_fields') == strict
                      and crow.get('differing_journal_fields') == journal_diff
                      and crow.get('state_related') == expected_row['strict_related']
                      and crow.get('prestate_related')
                      == case['prefixes'][prefix - 1].get('strict_related')
                      and crow.get('pairs_sha256') == row.get('pairs_sha256')
                      and crow.get('index') == prefix - 1
                      and crow.get('source_action') == crow.get('adapter_action')
                      == case['source']['actions'][prefix - 1])
        if not consistent:
            raise Failure('semantic', dict(base, check='row/prefix-agreement'))


def inspect_cases(cases, charge):
    observations, limitations, audited = [], [], 0
    usable = [c for c in cases or ()
              if type(c) is dict and all(k in c for k in REQUIRED)]
    if len(usable) != len(cases or ()):
        limitations.append('cases lacking retained prefix/pair evidence skipped: '
                           + str(len(cases or ()) - len(usable)))
    if not usable:
        return {'status': 'not_applicable', 'observations': [],
                'limitations': limitations or ['no typed retained case objects'],
                'audited_prefixes': 0}
    witnessed = set()
    try:
        for case in usable:
            ss, aa = _replay(case['source']), _replay(case['adapter'])
            if len(case['prefixes']) != len(ss) or len(case['rows']) != len(ss) - 1:
                raise Failure('semantic', {'case': case.get('case'),
                                           'check': 'prefix/row-cardinality',
                                           'expected': len(ss),
                                           'observed': len(case['prefixes'])})
            for prefix in range(len(ss)):
                charge.take(1)
                audited += 1
                _inspect_prefix(case, ss, aa, prefix)
            for row in case['prefixes']:
                witnessed.update(row['strict_differing_common_fields'])
            observations.append({'case': case.get('case'), 'audited_prefixes': len(ss),
                                 'common_fields': len(rel.FIELDS),
                                 'journal_fields': len(JOURNAL)})
    except Failure as failure:
        observations.append({'failure': failure.stage, 'witness': failure.witness})
        return {'status': 'counterexample', 'observations': observations,
                'limitations': limitations, 'audited_prefixes': audited}
    except (KeyError, TypeError, IndexError) as error:
        limitations.append('incomplete retained evidence: ' + repr(error))
        return {'status': 'unproved', 'observations': observations,
                'limitations': limitations, 'audited_prefixes': audited}
    silent = sorted(set(rel.FIELDS) - witnessed)
    if silent:
        limitations.append('no reachable differing witness for fields: ' + ','.join(silent))
    limitations.append('bounded to supplied retained prefixes; no all-order or global claim')
    return {'status': 'supported', 'observations': observations,
            'limitations': limitations, 'audited_prefixes': audited}


def run_controls(cases, inspect, charge):
    controls, limitations, audited = [], [], 0
    pool = [c for c in cases or ()
            if type(c) is dict and all(k in c for k in REQUIRED)]

    def find(predicate):
        for case in pool:
            charge.take(1)
            hit = next((i for i, r in enumerate(case['prefixes']) if predicate(case, r, i)), None)
            if hit is not None:
                return case, hit
        return None

    def attempt(label, found, mutate):
        nonlocal audited
        if found is None:
            controls.append({'control': label, 'detected': None, 'status': 'unwitnessed',
                             'reason': 'no genuinely reachable retained witness'})
            return
        case, prefix = found
        mutant = copy.deepcopy(case)
        mutate(mutant, prefix)
        result = inspect([mutant], charge)
        audited += result.get('audited_prefixes', 0)
        detected = result['status'] == 'counterexample'
        stage = next((o['failure'] for o in result['observations'] if 'failure' in o), None)
        controls.append({'control': label, 'detected': detected, 'status': result['status'],
                         'stage': stage,
                         'witness': {'case': case.get('case'), 'prefix': prefix}})
        if not detected:
            limitations.append(label + ' escaped detection')

    def drop_reported(mutant, i):
        field = mutant['prefixes'][i]['strict_differing_common_fields'][0]
        for key in ('strict_differing_common_fields', 'differing_common_fields'):
            if field in mutant['prefixes'][i][key]:
                mutant['prefixes'][i][key].remove(field)

    def silence_staged(mutant, i):
        for key in ('strict_differing_common_fields', 'differing_common_fields'):
            if 'staged' in mutant['prefixes'][i][key]:
                mutant['prefixes'][i][key].remove('staged')
        mutant['prefixes'][i]['staged_rule'] = 'strict'

    def phantom(mutant, i):
        row = mutant['prefixes'][i]
        row['strict_differing_common_fields'].append(
            next(k for k in rel.FIELDS if k not in row['strict_differing_common_fields']))

    def diverge_row(mutant, i):
        row = mutant['rows'][i - 1]
        row['differing_common_fields'].append(
            next(k for k in rel.FIELDS if k not in row['differing_common_fields']))

    if pool:
        base = inspect([copy.deepcopy(pool[0])], charge)
        audited += base.get('audited_prefixes', 0)
        controls.append({'control': 'unmutated-reinspection',
                         'detected': base['status'] == 'supported', 'status': base['status'],
                         'witness': {'case': pool[0].get('case'), 'prefix': None}})
    attempt('dropped-common-field-report',
            find(lambda c, r, i: r['strict_differing_common_fields']), drop_reported)
    attempt('dropped-journal-field-report',
            find(lambda c, r, i: r['differing_journal_fields']),
            lambda m, i: m['prefixes'][i]['differing_journal_fields'].pop(0))
    attempt('phantom-differing-field', find(lambda c, r, i: True), phantom)
    attempt('excluded-field-entered-report', find(lambda c, r, i: True),
            lambda m, i: m['prefixes'][i]['strict_differing_common_fields'].append('done'))
    attempt('staged-rule-downgrade',
            find(lambda c, r, i: r['staged_rule'] == 'original-object-identity'),
            lambda m, i: m['prefixes'][i].update(staged_rule='unrelated'))
    attempt('staged-difference-silenced',
            find(lambda c, r, i: 'staged' in r['strict_differing_common_fields']),
            silence_staged)
    attempt('identity-proof-forged-on-unrelated',
            find(lambda c, r, i: r['staged_rule'] == 'unrelated'),
            lambda m, i: m['prefixes'][i].update(
                identity_proof={'case': m.get('case'), 'prefix': i}))
    attempt('identity-claims-authority', find(lambda c, r, i: True),
            lambda m, i: m['prefixes'][i].update(incarnation_pair_established_by_identity=True))
    attempt('row-prefix-field-divergence', find(lambda c, r, i: i > 0), diverge_row)
    attempt('pair-ledger-rebase',
            find(lambda c, r, i: bool(c['incarnation_pairs'])),
            lambda m, i: m['incarnation_pairs'][0].update(source_event=10 ** 6))
    attempt('retained-state-patch-rewrite',
            find(lambda c, r, i: bool(c['source']['events'])),
            lambda m, i: m['source']['events'][0]['patch'].update(__forged_field=1))
    escaped = [c['control'] for c in controls if c['detected'] is False]
    return {'status': 'counterexample' if escaped else
            ('supported' if any(c['detected'] for c in controls) else 'unproved'),
            'controls': controls, 'limitations': limitations,
            'audited_prefixes': audited}
