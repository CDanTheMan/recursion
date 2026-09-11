"""Bounded retained-certificate check: accepted strict-or-staged relation and non-narrowing.

Obligation o26 (parent goal-recursion-v2-execution-fabric): over actual typed restored
case objects (the c.run_history / c.artifact round-trip shape), audit every retained
per-prefix certificate of the additive relation. A prefix is accepted iff it is strictly
related on every common+journal field, or differs only in 'staged' under the
original-object-identity disjunct: a same-index successful stage origin in both retained
traces plus identical, individually valid typed objects. Per validation-contract
relation_non_narrowing, empty source names, empty incarnation ledgers, equal live
generations and current-stage freshness are packet observations, never premises, and the
disjunct never establishes an incarnation pair. This module inspects retained fields,
replays retained trace patches, rebuilds the causal ledger and re-derives each prefix
row through the unchanged original relation and audit. It executes no reducer (no
step/enabled/check/initialization calls), imports no boundary helper, and asserts no
all-order theorem, reachability claim or scientific acceptance.

Representation anchors (unchanged original sources, imported only when present):
  experiments/v3/cut-source-overnight/batch-07/identity.py        compare/origin/identical
  experiments/v3/cut-source-overnight/batch-07/identity_audit.py  independent expected/valid_objects audit
  experiments/v3/cut-source-overnight/batch-05/semantic.py        typed/exact/digest/field_view/advance/FIELDS
  experiments/v3/cut-source-overnight/batch-06/adapter_traces.py  restore/core_view/response replay shape
  experiments/v3/cut-source-overnight/batch-06/a_domain.py        EXTRA journal fields/justification
  experiments/v3/eight-hour-research-20260910-01a08a22/check.py   retained case/prefix chronology shape
  docs/v3/construction/swarm-research-20260911-155142/validation-contract.json  relation_non_narrowing

Accounting: charge.take(1) precedes every individual prefix inspection; audited_prefixes
counts each charged inspection, including a failing one. Trace replay and ledger
reconstruction are deterministic overhead bound to retained digests.
"""
import sys
from pathlib import Path

SCHEMA = ('case', 'source', 'adapter', 'rows', 'incarnation_pairs', 'prefixes')
TRACE = ('side', 'initial', 'profile', 'actions', 'events')


class _Defect(Exception):
    """Retained evidence contradicts the expected strict-or-staged certificate."""


class _Charge(Exception):
    """Finite charge counter refused; inspection is incomplete, not falsified."""


def _need(ok, message, **detail):
    if not ok:
        raise _Defect(message, detail)


def _modules():
    root = Path(__file__).resolve().parents[4]
    path = str(root / 'experiments/v3/cut-source-overnight/batch-07')
    if path not in sys.path:
        sys.path.insert(0, path)
    import identity as relation
    import identity_audit
    return relation, identity_audit, relation.frozen, relation.d, relation.r


def _applicable(case):
    return (isinstance(case, dict) and all(k in case for k in SCHEMA)
            and isinstance(case['source'], dict) and all(k in case['source'] for k in TRACE)
            and isinstance(case['adapter'], dict)
            and all(k in case['adapter'] for k in (*TRACE, 'q_profile')))


def _audit_case(case, charge, audited, mod):
    relation, audit, t, d, r = mod
    name = case['case']
    _need(case['source']['actions'] == case['adapter']['actions'],
          'one-to-one literal visible actions', case=name)
    _need(r.exact(case['source']['profile'], case['adapter']['profile']),
          'same original profile retained', case=name)
    ss, aa = t.restore(case['source']), t.restore(case['adapter'])
    _need(len(ss) == len(aa) == len(case['prefixes']) == len(case['rows']) + 1,
          'retained prefix/row/event cardinality', case=name)
    pairs = []
    stats = {'prefixes': 0, 'strict': 0, 'related': 0, 'journal_gaps': 0, 'identity': 0,
             'identity_with_false_observation': 0, 'observation_only_rejections': 0,
             'unrelated_staged_gaps': 0}
    rules, witnesses = {}, []
    for i in range(len(ss)):
        try:
            charge.take(1)
        except Exception as error:
            raise _Charge(str(error), {'case': name, 'prefix': i})
        audited[0] += 1
        stats['prefixes'] += 1
        if i:
            action, row = case['source']['actions'][i - 1], case['rows'][i - 1]
            _need(action == case['adapter']['actions'][i - 1] == row['source_action']
                  == row['adapter_action'] and row['index'] == i - 1,
                  'literal chronological retained row', case=name, prefix=i)
            binding = r.advance(pairs, ss[i - 1], t.core_view(aa[i - 1]), ss[i],
                                t.core_view(aa[i]), action, action, i - 1, i - 1)
            _need(r.exact(binding, row['binding']), 'retained causal pair binding',
                  case=name, prefix=i)
            _need(type(row['q_invoked']) is bool and r.exact(
                row['justification'], d.justification(action, row['q_invoked'])),
                'retained actual Q invocation mask and translation', case=name, prefix=i)
            _need(t.response(ss[i], aa[i], action, pairs) == row['responses_related'],
                  'retained visible response relation', case=name, prefix=i)
            _need(case['prefixes'][i - 1]['strict_related'] == row['prestate_related'],
                  'strict relation prestate baseline', case=name, prefix=i)
        before = r.digest(pairs)
        item = relation.compare(case, ss, aa, i, pairs)
        audit.check(item, case, ss, aa, i, pairs)
        kept = case['prefixes'][i]
        _need(r.typed(kept) == r.typed(item) and r.digest(pairs) == before,
              'per-prefix strict-or-staged certificate; identity mutates no ledger',
              case=name, prefix=i, differing={
                  k: {'expected': r.typed(item[k]), 'retained': r.typed(kept.get(k))}
                  for k in item if isinstance(kept, dict)
                  and r.typed(kept.get(k)) != r.typed(item[k])})
        _need(item['incarnation_pair_established_by_identity'] is False,
              'identity disjunct never establishes authority', case=name, prefix=i)
        if i:
            _need(item['strict_related'] == case['rows'][i - 1]['state_related'],
                  'strict relation poststate baseline', case=name, prefix=i)
        source, adapter = ss[i], aa[i]
        identical = relation.identical(source['staged'], adapter['core']['staged'])
        staged_s, staged_a = source['staged'], adapter['core']['staged']
        current = bool(staged_s and staged_a and type(staged_s) is tuple
                       and len(staged_s) == 2
                       and r.exact(staged_s[0].source_generation,
                                   source['source_generation'])
                       and r.exact(staged_a[0].source_generation,
                                   adapter['core']['source_generation']))
        packet_observations = {
            'source_names_empty': not source['source_name']
            and not adapter['core']['source_name'],
            'incarnation_pairs_empty': not pairs,
            'live_generations_exact_equal': r.exact(source['source_generation'],
                                                    adapter['core']['source_generation']),
            'staged_is_current_generation': current}
        premises = {'stage_origin_proof': item['identity_proof'] is not None,
                    'identical_valid_objects': identical}
        rule = item['staged_rule']
        rules[rule] = rules.get(rule, 0) + 1
        stats['strict'] += item['strict_related']
        stats['related'] += item['related']
        stats['journal_gaps'] += bool(item['differing_journal_fields'])
        if item['related'] and not item['strict_related']:
            _need(item['strict_differing_common_fields'] == ['staged']
                  and item['differing_common_fields'] == []
                  and not item['differing_journal_fields']
                  and rule == 'original-object-identity' and all(premises.values()),
                  'disjunct rescues exactly the staged field via provenance premises',
                  case=name, prefix=i)
        if rule == 'original-object-identity':
            stats['identity'] += 1
            if not all(packet_observations.values()):
                stats['identity_with_false_observation'] += 1
        elif 'staged' in item['strict_differing_common_fields']:
            stats['unrelated_staged_gaps'] += 1
            if all(packet_observations.values()):
                stats['observation_only_rejections'] += 1
        if rule != 'strict' and len(witnesses) < 4:
            witnesses.append({'case': name, 'prefix': i, 'staged_rule': rule,
                              'premises': premises,
                              'packet_observations': packet_observations,
                              'strict_related': item['strict_related'],
                              'related': item['related'],
                              'identity_proof': item['identity_proof']})
    _need(r.exact(pairs, case['incarnation_pairs']),
          'complete immutable causal pair ledger', case=name)
    return stats, rules, witnesses


def inspect_cases(cases, charge):
    limitations = [
        'Replays retained trace patches and re-derives each prefix via the unchanged '
        'original relation/audit; no reducer is executed, so enabledness, transition '
        'postconditions, actual Q-call mask generation and refused-decision correctness '
        'remain retained generation-time facts.',
        'Verdict covers only the supplied restored cases; no all-order theorem, '
        'reachability claim, source truth, composition or scientific acceptance.']
    observations, audited, applicable = [], [0], 0
    if type(cases) is not list or not cases:
        return {'status': 'unproved', 'observations': [], 'audited_prefixes': 0,
                'limitations': limitations + ['no retained case objects supplied']}
    try:
        mod = _modules()
    except Exception as error:
        return {'status': 'unproved', 'observations': [], 'audited_prefixes': 0,
                'limitations': limitations + [
                    'original audit/semantic representation sources unavailable: '
                    + str(error)]}
    r = mod[4]
    for position, case in enumerate(cases):
        if not _applicable(case):
            observations.append({'index': position, 'disposition': 'not_applicable',
                                 'case': case.get('case') if isinstance(case, dict)
                                 and isinstance(case.get('case'), str) else None,
                                 'reason': 'no retained strict-or-staged prefix '
                                 'certificate schema'})
            continue
        applicable += 1
        try:
            stats, rules, witnesses = _audit_case(case, charge, audited, mod)
            observations.append({'case': case['case'], 'disposition': 'audited',
                                 'staged_rules': rules, 'witnesses': witnesses, **stats})
        except _Charge as error:
            limitations.append('finite charge refused: %s; partial case not claimed'
                               % error)
            return {'status': 'unproved', 'observations': observations,
                    'limitations': limitations, 'audited_prefixes': audited[0]}
        except (_Defect, ValueError, KeyError, TypeError, IndexError,
                AttributeError) as error:
            detail = error.args[1] if error.args and isinstance(
                error.args[-1], dict) else {}
            observations.append({'case': case.get('case'), 'prefix': detail.get('prefix'),
                                 'disposition': 'counterexample',
                                 'reason': error.args[0] if error.args else str(error),
                                 'detail': r.typed(detail)})
            return {'status': 'counterexample', 'observations': observations,
                    'limitations': limitations, 'audited_prefixes': audited[0]}
    if not applicable:
        status = 'not_applicable'
    else:
        status = 'supported'
        if applicable < len(cases):
            limitations.append('%d supplied case(s) lacked the prefix-certificate '
                               'schema and were not inspected'
                               % (len(cases) - applicable))
        totals = {'identity': 0, 'false_obs': 0, 'obs_rej': 0}
        for row in observations:
            if row.get('disposition') == 'audited':
                totals['identity'] += row['identity']
                totals['false_obs'] += row['identity_with_false_observation']
                totals['obs_rej'] += row['observation_only_rejections']
        if not totals['identity']:
            limitations.append('no accepted staged-identity prefix occurred; the '
                               'disjunct side was not exercised in this bound')
        elif not totals['false_obs']:
            limitations.append('every accepted identity prefix shares all four packet '
                               'observations; non-narrowing is separated structurally '
                               'here, not empirically varied')
        if not totals['obs_rej']:
            limitations.append('no prefix held all four packet observations while the '
                               'disjunct was rejected; observation-insufficiency was '
                               'not witnessed in this bound')
    return {'status': status, 'observations': observations,
            'limitations': limitations, 'audited_prefixes': audited[0]}
