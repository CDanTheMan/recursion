"""Adversarial retained-evidence controls: registration completeness, foreign scope,
conflict precedence (obligation o01, boundary-01 scale-eight-action-race).

inspect_cases(cases, charge) audits typed restored cases; run_controls(cases,
inspect_cases, charge) is the deepcopy-mutation discrimination suite.

Induction premises for the original scale setup
(s_domain.py add_with_suffix 'scale-eight-action-race'; boundary-01 spec fixed
prefix 11, so register:success is the single register inside the fixed prefix):
  P0 init: registration='' and source_revision=0 on both authorities; adapter
     journal source_generation=('cut-source','collectorA','effectA',0);
     decision 'initial'; invocations (). Anchors: s_audit.initialization,
     a_audit.initialization, s_domain.DEFAULTS, a_domain.initial.
  P1 pre-state: the delegated Q-SETUP prefix actions establish remote!=0 and
     bindings[0]==fixture reservation before register:success. Anchors:
     s_domain.setup over q.SETUP; s_audit/guard_audit register clause.
  P2 step: precedence incomplete-registration > foreign-registration >
     registration-conflict > ok; success writes canonical
     (intent,admission,reservation) plus source_revision+1, touches no other
     journal field, invokes no Q call, leaves core/invocations unchanged and
     binds no incarnation pair. Anchors: s_inclusive.py:14-20, s_audit.check,
     guard_audit.expected, guard_a.py:15-21, guard_b.py:13-19,
     semantic.advance 'unchanged'.
  P3 stability/correspondence: registration immutable under every non-register
     action; journal registration == source registration at every prefix
     (inherited/prestage-correspondence-analysis.md Registration row).
  P4 reachability: refusal branches are unreachable in this retained domain;
     refusal witnesses live in s_domain profiles 'incomplete-registration' and
     'foreign-registration', outside boundary-01's 384 histories. Unwitnessed
     clauses remain unproved here (missing-witness limitation), never silently
     supported; no global theorem or accepted scientific PASS is claimed.

Accounting: charge.take(1) is called before every inspected prefix of every
case, including each mutant re-inspection; audited_prefixes is the total. No
reducer, model, inventory or boundary helper is executed; the only reused
machinery is the unchanged typed restore and fixture/encoding representation
(check.t.restore as the boundary census uses it, d.exact/d.digest, s_domain
fixture functions). Controls mutate semantic fields while preserving outer
artifact hashes so detection must reach semantics; mutations whose target is
not exposed by the retained schema are reported 'mutation-unreachable' rather
than counted as detections or original-domain counterexamples.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/v3/eight-hour-research-20260910-01a08a22'))
import check as c

d = c.d
CORRUPT = (ValueError, KeyError, TypeError, IndexError)
EXTRA = tuple(d.s.EXTRA)
JOURNAL = EXTRA + ('source_generation',)
TOKEN0 = ('cut-source', 'collectorA', 'effectA', 0)
REFUSALS = ('incomplete-registration', 'foreign-registration', 'registration-conflict')


def _registers(case):
    return [i for i, a in enumerate(case['source']['actions'])
            if a.split('@')[0].startswith('register:')]


def _reason(pre, value, fixture, required):
    if set(fixture['original']['cut']['trace_header']['intent']) != required:
        return 'incomplete-registration'
    if not pre['remote'] or fixture['binding']['body']['reservation'] != list(pre['bindings'][0]):
        return 'foreign-registration'
    if pre['registration'] and pre['registration'] != value:
        return 'registration-conflict'
    return 'ok'


def inspect_cases(cases, charge):
    cases = list(cases)
    observations, limitations = [], []
    audited, applicable = 0, False
    witnessed = set()
    counterexample = unproved = exhausted = False
    try:
        required = set(d.s.q.lit.fixture('success')['original']['cut']['trace_header']['intent'])
    except CORRUPT as error:
        return dict(status='unproved', observations=[],
                    limitations=['fixture representation unavailable: %s' % error],
                    audited_prefixes=0)

    def bad(case, prefix, control, expected, observed):
        nonlocal counterexample
        counterexample = True
        observations.append(dict(case=str(case.get('case')), prefix=prefix, control=control,
                                 expected=expected, observed=observed))

    for case in cases:
        if exhausted:
            break
        try:
            ss, aa = c.t.restore(case['source']), c.t.restore(case['adapter'])
            actions, profile = case['source']['actions'], case['source']['profile']
            rows, items = case['rows'], case['prefixes']
        except CORRUPT as error:
            unproved = True
            limitations.append('uninspectable retained case %r: %s' % (case.get('case'), error))
            continue
        applicable = applicable or bool(_registers(case))
        if (case['adapter']['actions'] != actions or len(ss) != len(actions) + 1
                or len(aa) != len(ss) or len(rows) != len(actions) or len(items) != len(ss)
                or sorted(actions) != sorted(profile['actions'])):
            bad(case, None, 'broken-retained-frame', 'aligned actions/profile/rows/prefixes/states',
                'actions=%d states=%d rows=%d prefixes=%d'
                % (len(actions), len(ss), len(rows), len(items)))
            continue
        for prefix in range(len(ss)):
            try:
                charge.take(1)
            except CORRUPT:
                unproved = exhausted = True
                limitations.append('charge exhausted at prefix %d of %s'
                                   % (prefix, case.get('case')))
                break
            audited += 1
            try:
                reason = _inspect_prefix(case, ss, aa, actions, profile, rows, items,
                                         prefix, required, bad)
            except CORRUPT as error:
                unproved = True
                limitations.append('prefix %d of %s uninspectable: %s'
                                   % (prefix, case.get('case'), error))
                continue
            if reason:
                witnessed.add(reason)
    if counterexample:
        status = 'counterexample'
    elif unproved:
        status = 'unproved'
    elif not applicable:
        status = 'not_applicable'
    else:
        status = 'supported'
    missing = [b for b in REFUSALS if b not in witnessed]
    if status == 'supported' and missing:
        limitations.append('unwitnessed refusal branches %r: no reachable register refusal in '
                           'the retained domain; those precedence clauses remain unproved' % missing)
    observations.append(dict(control='reachable-branch-coverage', witnessed=sorted(witnessed),
                             cases=len(cases)))
    return dict(status=status, observations=observations, limitations=limitations,
                audited_prefixes=audited)


def _inspect_prefix(case, ss, aa, actions, profile, rows, items, prefix, required, bad):
    src, adp = ss[prefix], aa[prefix]
    journal = adp['journal']
    if not d.exact(src['registration'], journal['registration']):
        bad(case, prefix, 'journal-registration-divergence', 'source==journal',
            d.digest(journal['registration']))
    if not d.exact(src['source_revision'], journal['source_revision']):
        bad(case, prefix, 'journal-revision-divergence', 'source==journal',
            [src['source_revision'], journal['source_revision']])
    if prefix == 0:
        if src['registration'] != '' or src['source_revision'] != 0:
            bad(case, 0, 'source-registration-init', "registration='' revision=0",
                [src['registration'], src['source_revision']])
        if (journal['registration'] != '' or journal['source_revision'] != 0
                or not d.exact(journal['source_generation'], TOKEN0)
                or adp['decision'] != 'initial' or adp['invocations'] != ()):
            bad(case, 0, 'adapter-registration-init', 'empty journal token0 initial',
                d.digest(journal))
        return None
    r, action = prefix - 1, actions[prefix - 1]
    k = action.split('@')[0]
    pre_s, pre_a = ss[r], aa[r]
    pre_j = pre_a['journal']
    if not k.startswith('register:'):
        if not (d.exact(pre_s['registration'], src['registration'])
                and d.exact(pre_j['registration'], journal['registration'])):
            bad(case, prefix, 'registration-mutated-without-register', 'unchanged', k)
        return None
    name = k.split(':', 1)[1]
    fixture, value = d.s.q.lit.fixture(name), d.s.registration(name)
    reason = _reason(pre_s, value, fixture, required)
    success = reason == 'ok' and not pre_s['registration']
    row, item = rows[r], items[prefix]
    expected_decision = k + ':' + reason
    if row.get('source_action') != action or row.get('adapter_action') != action or row.get('index') != r:
        bad(case, prefix, 'register-row-identity', action,
            '%s/%s@%s' % (row.get('source_action'), row.get('adapter_action'), row.get('index')))
    for side in ('source_observation', 'adapter_observation'):
        if row[side].get('decision') != expected_decision:
            bad(case, prefix, 'register-decision-' + side, expected_decision,
                row[side].get('decision'))
    if row.get('q_invoked') is not False:
        bad(case, prefix, 'q-invoked-on-register', False, row.get('q_invoked'))
    if row.get('binding') != 'unchanged':
        bad(case, prefix, 'register-incarnation-binding', 'unchanged', row.get('binding'))
    if not d.exact(pre_a['core'], adp['core']):
        bad(case, prefix, 'core-changed-on-register', 'unchanged', 'changed')
    if not d.exact(pre_a['invocations'], adp['invocations']):
        bad(case, prefix, 'invocations-changed-on-register', 'unchanged', 'changed')
    expect_reg = value if success else pre_s['registration']
    if not (d.exact(src['registration'], expect_reg) and d.exact(journal['registration'], expect_reg)):
        bad(case, prefix, 'registration-value', d.digest(expect_reg),
            [d.digest(src['registration']), d.digest(journal['registration'])])
    expect_rev = pre_s['source_revision'] + (1 if success else 0)
    if src['source_revision'] != expect_rev or journal['source_revision'] != expect_rev:
        bad(case, prefix, 'registration-revision', expect_rev,
            [src['source_revision'], journal['source_revision']])
    changed = sorted(f for f in JOURNAL if not d.exact(pre_j[f], journal[f]))
    if changed != (['registration', 'source_revision'] if success else []):
        bad(case, prefix, 'journal-ledger-footprint',
            ['registration', 'source_revision'] if success else [], changed)
    if adp['done'] != pre_a['done'] | (1 << profile['actions'].index(action)):
        bad(case, prefix, 'register-done-bit', 'pre|bit', adp['done'])
    for key in ('state_related', 'responses_related'):
        if row.get(key) is not True:
            bad(case, prefix, 'retained-' + key, True, row.get(key))
    actual = sorted(f for f in EXTRA if not d.exact(src[f], journal[f]))
    if item.get('differing_journal_fields') != actual:
        bad(case, prefix, 'claimed-journal-diff', actual, item.get('differing_journal_fields'))
    for key in ('strict_related', 'related'):
        if item.get(key) is not True:
            bad(case, prefix, 'prefix-' + key, True, item.get(key))
    return reason


def run_controls(cases, inspect_cases, charge):
    cases = list(cases)
    baseline = inspect_cases(cases, charge)
    audited = baseline['audited_prefixes']
    controls, limitations = [], []

    def reg(m):
        return next((i for i, a in enumerate(m['source']['actions'])
                     if a.split('@')[0].startswith('register:')), None)

    def deep_set(node, key, value):
        hits = 0
        if isinstance(node, dict):
            for k in list(node):
                if k == key and type(node[k]) in (str, int):
                    node[k] = value
                    hits += 1
                else:
                    hits += deep_set(node[k], key, value)
        elif isinstance(node, list):
            for v in node:
                hits += deep_set(v, key, value)
        return hits

    def run(label, reachable, mutate):
        nonlocal audited
        mutants, applied = [], 0
        for case in cases:
            m = copy.deepcopy(case)
            applied += bool(mutate(m))
            mutants.append(m)
        if not applied:
            controls.append(dict(control=label, detected='mutation-unreachable',
                                 reachable_witness=reachable,
                                 detail='retained schema exposed no target field'))
            return
        results = [inspect_cases([m], charge) for m in mutants]
        audited += sum(x['audited_prefixes'] for x in results)
        controls.append(dict(control=label, reachable_witness=reachable,
                             detected=all(x['status'] == 'counterexample' for x in results),
                             statuses=[x['status'] for x in results]))

    def row_mut(key, value):
        def fn(m):
            r = reg(m)
            if r is None:
                return False
            m['rows'][r][key] = value
            return True
        return fn

    def set_decision(reason):
        def fn(m):
            r = reg(m)
            if r is None:
                return False
            k = m['source']['actions'][r].split('@')[0]
            for side in ('source_observation', 'adapter_observation'):
                m['rows'][r][side]['decision'] = k + ':' + reason
            return True
        return fn

    def prefix_mut(m):
        r = reg(m)
        if r is None:
            return False
        m['prefixes'][r + 1]['differing_journal_fields'] = ['registration']
        return True

    def init_mut(side):
        def fn(m):
            if side == 'adapter':
                m['adapter']['initial']['journal']['registration'] = 'forged-registration'
            else:
                m['source']['initial']['registration'] = 'forged-registration'
            return True
        return fn

    def swap_register(m):
        r = reg(m)
        if r is None:
            return False
        for side in ('source', 'adapter'):
            acts = list(m[side]['actions'])
            old = acts[r]
            acts[r] = 'register:missing-original@' + (old.split('@', 1)[1] if '@' in old else str(r))
            m[side]['actions'] = tuple(acts)
        return True

    def drop_register(m):
        r = reg(m)
        if r is None:
            return False
        for side in ('source', 'adapter'):
            acts = list(m[side]['actions'])
            del acts[r]
            m[side]['actions'] = tuple(acts)
        return True

    def deep(key, value):
        def fn(m):
            r = reg(m)
            if r is None:
                return False
            if callable(value):
                value = value(m, r)
            return deep_set(m['source']['events'][r], key, value) + \
                deep_set(m['adapter']['events'][r], key, value)
        return fn

    def foreign_value(m, r):
        return d.s.registration('failure')

    def prior_revision(m, r):
        return c.t.restore(m['source'])[r]['source_revision']

    run('forged-incomplete-registration-decision', False, set_decision('incomplete-registration'))
    run('forged-foreign-registration-decision', False, set_decision('foreign-registration'))
    run('forged-registration-conflict-decision', False, set_decision('registration-conflict'))
    run('false-q-invocation-on-register', True, row_mut('q_invoked', True))
    run('forged-register-incarnation-binding', True, row_mut('binding', 'new-binding'))
    run('forged-retained-verdict', True, row_mut('state_related', False))
    run('phantom-journal-disagreement', True, prefix_mut)
    run('forged-source-initial-registration', True, init_mut('source'))
    run('forged-adapter-initial-registration', True, init_mut('adapter'))
    run('swapped-register-target', False, swap_register)
    run('dropped-register-action', True, drop_register)
    run('silent-registration-erasure', True, deep('registration', ''))
    run('foreign-registration-value', True, deep('registration', foreign_value))
    run('registration-revision-not-bumped', True, deep('source_revision', prior_revision))
    unreachable = [x['control'] for x in controls if x['detected'] == 'mutation-unreachable']
    if unreachable:
        limitations.append('mutation-unreachable controls %r need a retained schema exposing '
                           'the target field; no detection claimed for them' % unreachable)
    if baseline['status'] != 'supported':
        limitations.append('baseline inspection was %s; detections reported verbatim'
                           % baseline['status'])
    undetected = [x['control'] for x in controls if x['detected'] is False]
    if baseline['status'] == 'counterexample':
        status = 'counterexample'
    elif baseline['status'] == 'supported' and not undetected:
        status = 'supported'
    else:
        status = 'unproved'
    return dict(status=status, baseline_status=baseline['status'], controls=controls,
                observations=baseline['observations'], limitations=limitations,
                audited_prefixes=audited)
