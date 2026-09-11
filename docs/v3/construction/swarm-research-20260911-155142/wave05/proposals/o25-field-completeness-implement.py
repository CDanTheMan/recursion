"""Bounded retained-certificate check: exhaustive common-Q field inventory.

Obligation o25-field-completeness. For every audited prefix of each retained,
previously restored case object, verify that the actual source state, adapter
core, adapter journal and adapter outer frame key sets exactly equal the
declared inventories, and that the retained per-prefix/per-event difference
lists stay inside those inventories and recompute from actual typed field
values, so a dropped or phantom field comparison is detected, not trusted.

Declared inventories (restated independently here, then compared against the
relation's own field list):
  common  = q.AUTH + q.FLOW + q.VIEW minus ('done','decision')
  journal = s.EXTRA + ('source_generation',)          # adapter journal extras
  source  = q.AUTH + q.FLOW + q.VIEW + s.EXTRA        # whole source state
  adapter = {'core','journal','done','decision','invocations'}

Representation only: the unchanged semantic source supplies typed equality,
the canonical digest and the AUTH/FLOW/VIEW/EXTRA constants. No reducer, guard,
audit, relation, inventory or boundary helper function is executed; per-prefix
states are rebuilt by literal patch replay of retained trace events, rebound to
the retained per-event state hashes.

Source anchors (unchanged original sources):
  FIELDS/typed/exact/digest ..... experiments/v3/cut-source-overnight/batch-05/semantic.py
  AUTH/FLOW/VIEW/EXTRA constants  experiments/v3/cut-publication/q_domain.py
  source EXTRA journal extras ... experiments/v3/cut-source-overnight/s_domain.py
  adapter frame/journal keys .... experiments/v3/cut-source-overnight/batch-06/a_audit.py, a_domain.py
  journal comparison list ....... batch-06/adapter_traces.py related()
  retained difference lists ..... batch-07/identity.py compare(), identity_audit.py check(),
                                  batch-06/adapter_traces.py comparison(), check.py audit_case()

Accounting: charge.take(1) is consumed exactly once per inspected case prefix
before any field of that prefix is read; audited_prefixes reports the count.
Local retained-evidence result only: no global theorem, no all-order
reachability, no accepted scientific PASS.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel

exact, digest = rel.exact, rel.digest
Q, S = rel.q, rel.s
OUTER = ('core', 'journal', 'done', 'decision', 'invocations')
EXCLUDED = ('done', 'decision')          # carried by visible decisions, not FIELDS
JOURNAL = tuple(S.EXTRA) + ('source_generation',)
WITNESS_CAP = 8


def _require(ok, message):
    if not ok:
        raise ValueError('field-completeness: ' + message)


def _defect(severity, kind, case, prefix, side, detail):
    return dict(severity=severity, kind=kind, case=case, prefix=prefix,
                side=side, detail=detail)


def _universes():
    common = tuple(k for k in Q.AUTH + Q.FLOW + Q.VIEW if k not in EXCLUDED)
    return dict(common=common, common_set=set(common),
                q_all=set(Q.AUTH + Q.FLOW + Q.VIEW), journal_set=set(JOURNAL),
                source_all=set(Q.AUTH + Q.FLOW + Q.VIEW) | set(S.EXTRA))


def _replay(trace):
    """Literal patch replay of retained events; no transition predicate runs."""
    _require(type(trace) is dict and trace.get('side') in ('source', 'adapter'),
             'retained trace side')
    _require(len(trace['events']) == len(trace['actions']),
             'complete retained event inventory')
    current = copy.deepcopy(trace['initial'])
    states = [current]
    adapter = trace['side'] == 'adapter'
    for i, event in enumerate(trace['events']):
        _require(event['action'] == trace['actions'][i],
                 'literal retained action occurrence')
        _require(digest(current) == event['before_sha256'],
                 'retained prestate hash binding')
        current = copy.deepcopy(current)
        for key, value in event['patch'].items():
            if adapter and key in ('core', 'journal'):
                current[key].update(value)
            else:
                current[key] = value
        _require(digest(current) == event['after_sha256'],
                 'retained poststate hash binding')
        states.append(current)
    return states


def _keys(case, index, side, observed, expected):
    """Dropped-field detector: missing fields break coverage; extra fields sit
    outside every compared inventory, so no retained comparison can see them."""
    out = []
    missing, extra = sorted(expected - observed), sorted(observed - expected)
    if missing:
        out.append(_defect('counterexample', 'missing-inventory-field', case,
                           index, side, {'missing': missing}))
    if extra:
        out.append(_defect('counterexample', 'uncompared-state-field', case,
                           index, side, {'extra': extra}))
    return out


def _prefix(case, name, index, s, a, prev, uni):
    defects, info = [], {'abstracted': []}
    core = a.get('core', {}) if type(a) is dict else {}
    journal = a.get('journal', {}) if type(a) is dict else {}
    defects += _keys(name, index, 'source', set(s), uni['source_all'])
    defects += _keys(name, index, 'adapter', set(a), set(OUTER))
    defects += _keys(name, index, 'adapter.core', set(core), uni['q_all'])
    defects += _keys(name, index, 'adapter.journal', set(journal),
                     uni['journal_set'])
    common_exact = sorted(k for k in uni['common']
                          if k in s and k in core and not exact(s[k], core[k]))
    journal_exact = sorted(k for k in JOURNAL
                           if k in s and k in journal and not exact(s[k], journal[k]))
    info['common_exact'], info['journal_exact'] = common_exact, journal_exact
    profile = case['source'].get('profile') or {}
    if type(profile.get('actions')) in (list, tuple):
        wanted = sum(1 << list(profile['actions']).index(x)
                     for x in case['source']['actions'][:index])
        for side, state in (('source', s), ('adapter', a)):
            if 'done' in state and state['done'] != wanted:
                defects.append(_defect('counterexample', 'done-mask-mismatch',
                                       name, index, side,
                                       {'expected': wanted,
                                        'observed': state['done']}))
    qp = case['adapter'].get('q_profile') or {}
    if type(qp.get('actions')) in (list, tuple) and 'done' in core:
        invocations = a.get('invocations', ())
        wanted = sum(1 << list(qp['actions']).index(x) for x in invocations)
        if core['done'] != wanted:
            defects.append(_defect('counterexample', 'core-invocation-mask-mismatch',
                                   name, index, 'adapter.core',
                                   {'expected': wanted, 'observed': core['done']}))
    prefixes = case.get('prefixes')
    if type(prefixes) is list and index < len(prefixes):
        p = prefixes[index]
        strict = set(p.get('strict_differing_common_fields') or ())
        ext = set(p.get('differing_common_fields') or ())
        jd = set(p.get('differing_journal_fields') or ())
        if not strict <= uni['common_set']:
            defects.append(_defect('counterexample', 'prefix-field-outside-inventory',
                                   name, index, 'prefix',
                                   {'fields': sorted(strict - uni['common_set'])}))
        if not ext <= strict or strict - ext - {'staged'}:
            defects.append(_defect('counterexample', 'extended-not-staged-narrowing',
                                   name, index, 'prefix',
                                   {'strict_only': sorted(strict - ext),
                                    'extended_only': sorted(ext - strict)}))
        phantom = sorted(strict - set(common_exact))
        if phantom:
            defects.append(_defect('counterexample', 'phantom-common-difference',
                                   name, index, 'prefix',
                                   {'fields': phantom,
                                    'source_sha256': {k: digest(s[k])
                                                      for k in phantom},
                                    'core_sha256': {k: digest(core[k])
                                                    for k in phantom if k in core}}))
        if jd != set(journal_exact):
            defects.append(_defect('counterexample', 'journal-difference-mismatch',
                                   name, index, 'prefix.journal',
                                   {'expected': journal_exact,
                                    'observed': sorted(jd)}))
        info['abstracted'] = sorted(set(common_exact) - strict)
    rows = case.get('rows')
    if type(rows) is list and 0 < index <= len(rows):
        r = rows[index - 1]
        action = case['source']['actions'][index - 1]
        if not (r.get('source_action') == r.get('adapter_action') == action):
            defects.append(_defect('counterexample', 'literal-action-mismatch',
                                   name, index, 'row',
                                   {'expected': action,
                                    'observed': [r.get('source_action'),
                                                 r.get('adapter_action')]}))
        rc = set(r.get('differing_common_fields') or ())
        if not rc <= set(common_exact):
            defects.append(_defect('counterexample', 'row-difference-not-backed',
                                   name, index, 'row',
                                   {'fields': sorted(rc - set(common_exact))}))
        rj = sorted(r.get('differing_journal_fields') or ())
        if rj != journal_exact:
            defects.append(_defect('counterexample', 'journal-difference-mismatch',
                                   name, index, 'row.journal',
                                   {'expected': journal_exact, 'observed': rj}))
        so, ao = r.get('source_observation') or {}, r.get('adapter_observation') or {}
        if so.get('decision') != s.get('decision'):
            defects.append(_defect('counterexample',
                                   'source-decision-observation-mismatch', name,
                                   index, 'row', {'expected': s.get('decision'),
                                                  'observed': so.get('decision')}))
        if ao.get('decision') != a.get('decision'):
            defects.append(_defect('counterexample',
                                   'adapter-decision-observation-mismatch', name,
                                   index, 'row', {'expected': a.get('decision'),
                                                  'observed': ao.get('decision')}))
        invocations = a.get('invocations')
        if prev is not None and type(invocations) in (list, tuple):
            grew = (len(invocations) == len(prev['invocations']) + 1
                    and invocations[-1] == action)
            if bool(r.get('q_invoked')) != grew:
                defects.append(_defect('counterexample', 'invocation-mask-mismatch',
                                       name, index, 'row',
                                       {'expected_invocation': grew,
                                        'observed_q_invoked': r.get('q_invoked')}))
    return defects, info


def _shape(case):
    return (type(case) is dict and type(case.get('source')) is dict
            and type(case.get('adapter')) is dict
            and case['source'].get('side') == 'source'
            and case['adapter'].get('side') == 'adapter'
            and type(case['source'].get('actions')) in (list, tuple)
            and type(case['source'].get('events')) is list
            and type(case['adapter'].get('events')) is list)


def inspect_cases(cases, charge):
    """Retained-certificate field-inventory audit over restored case objects.

    cases: typed case dicts produced by the original run_history / typed
    artifact restoration. charge: bounded counter; take(1) is consumed before
    each inspected prefix. Returns a JSON-safe dict; never claims acceptance.
    """
    uni = _universes()
    out = {'status': 'unproved', 'observations': [], 'limitations': [],
           'audited_prefixes': 0}
    _require(callable(getattr(charge, 'take', None)), 'bounded charge object required')
    out['observations'].append({
        'kind': 'declared-inventory',
        'common_fields': list(uni['common']), 'journal_fields': list(JOURNAL),
        'excluded_from_common': list(EXCLUDED), 'adapter_frame': list(OUTER),
        'relation_fields_equal': tuple(rel.FIELDS) == uni['common']})
    defects = []
    if tuple(rel.FIELDS) != uni['common']:
        defects.append(_defect('counterexample', 'relation-inventory-mismatch',
                               None, None, 'semantic.FIELDS',
                               {'expected': list(uni['common']),
                                'observed': list(rel.FIELDS)}))
    if uni['q_all'] - uni['common_set'] != set(EXCLUDED):
        defects.append(_defect('counterexample', 'exclusion-set-mismatch', None,
                               None, 'static',
                               {'observed': sorted(uni['q_all'] - uni['common_set'])}))
    if cases is None:
        out['status'] = 'not_applicable'
        out['limitations'].append(
            'no retained case objects supplied; nothing was inspected')
        return out
    for position, case in enumerate(cases):
        name = case.get('case', position) if type(case) is dict else position
        if not _shape(case):
            defects.append(_defect('unproved', 'case-shape-uninspectable', name,
                                   None, 'case', {}))
            continue
        try:
            s_states = _replay(case['source'])
            a_states = _replay(case['adapter'])
        except (ValueError, KeyError, TypeError, IndexError) as error:
            defects.append(_defect('unproved', 'replay-refusal', name, None,
                                   'case', {'reason': str(error)}))
            continue
        if len(s_states) != len(a_states) or list(case['source']['actions']) != list(
                case['adapter'].get('actions', ())):
            defects.append(_defect('unproved', 'prefix-inventory-mismatch', name,
                                   None, 'case',
                                   {'source_prefixes': len(s_states),
                                    'adapter_prefixes': len(a_states)}))
        if type(case.get('prefixes')) is not list or type(case.get('rows')) is not list:
            defects.append(_defect('unproved', 'retained-difference-rows-missing',
                                   name, None, 'case', {}))
        union_common, union_journal, abstracted = set(), set(), set()
        prev = None
        for index in range(min(len(s_states), len(a_states))):
            charge.take(1)
            try:
                found, info = _prefix(case, name, index, s_states[index],
                                      a_states[index], prev, uni)
            except (ValueError, KeyError, TypeError, IndexError) as error:
                defects.append(_defect('unproved', 'prefix-inspection-refusal',
                                       name, index, 'case',
                                       {'reason': str(error)}))
            else:
                defects += found
                union_common |= set(info['common_exact'])
                union_journal |= set(info['journal_exact'])
                abstracted |= set(info.get('abstracted', ()))
            out['audited_prefixes'] += 1
            prev = a_states[index]
        out['observations'].append({
            'kind': 'case-field-inventory', 'case': name,
            'audited_prefixes': min(len(s_states), len(a_states)),
            'common_fields': len(uni['common']), 'journal_fields': len(JOURNAL),
            'exact_differing_common': sorted(union_common),
            'exact_differing_journal': sorted(union_journal),
            'abstracted_common': sorted(abstracted),
            'source_final_sha256': digest(s_states[-1]),
            'adapter_final_sha256': digest(a_states[-1])})
    out['limitations'] += [
        'states are rebuilt from retained trace patches only; transition '
        'correctness itself is not re-established by this check',
        'pair/identity abstractions may legitimately relate exact-differing '
        'fields (incarnations, envelopes); such abstraction is reported in '
        'observations, not faulted',
        'coverage is bounded to the supplied cases and prefixes; all-order '
        'reachability, source truth and scientific acceptance are out of scope']
    grouped = {}
    for d in defects:
        grouped.setdefault((d['severity'], d['kind']), []).append(d)
    for (severity, kind), rows in sorted(grouped.items()):
        out['observations'].append({'kind': kind, 'severity': severity,
                                    'count': len(rows),
                                    'witnesses': rows[:WITNESS_CAP]})
    out['observations'].append({
        'kind': 'scope',
        'claim': 'bounded retained-certificate inventory check only; no global '
                 'theorem, no all-order reachability, no accepted scientific PASS'})
    if any(severity == 'counterexample' for severity, _ in grouped):
        out['status'] = 'counterexample'
    elif grouped:
        out['status'] = 'unproved'
    elif out['audited_prefixes']:
        out['status'] = 'supported'
    else:
        out['status'] = 'not_applicable'
    return out
