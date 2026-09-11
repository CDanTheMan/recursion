"""Strict-or-staged relation disjunct: bounded retained-certificate check (o26).

Audits actual typed c.run_history/c.artifact case objects for the accepted
strict-or-staged relation plus relation_non_narrowing: empty source names,
empty pair ledgers, equal live generations and current-stage freshness are
observations only, never premises of the staged-identity disjunct.

Anchors (unchanged originals; no boundary.py helper imported): identity.py
compare/proof/identical; identity_audit.py expected_proof/valid_objects/check;
adapter_traces.py restore/comparison/response/core_view + gap_certificate
facts; semantic.py advance/field_view/typed; check.py audit_case ordering;
validation-contract.json relation_non_narrowing; review-defects.json
staged-identity-as-authority control family.

No reducer step executes: t.restore replays hash-bound patches; t.sc.check and
t.audit.check are unchanged audit relations over retained states. charge.take(1)
precedes every inspected prefix (all repetitions count); audited_prefixes is
the finite accounting. Witness-dependent controls record missing_witness; gaps
stay limitations, never silent passes.
"""
import copy, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/eight-hour-research-20260910-01a08a22'))
import check as c

d, r, t = c.d, c.r, c.t
identity_audit = c.identity_audit
ERRORS = (ValueError, KeyError, IndexError, TypeError, AttributeError)
NARROWING = ('empty_source_names', 'empty_incarnation_pairs',
             'equal_live_generations', 'current_stage_freshness')

class _Fail(Exception):
    pass

class _Charged(Exception):
    pass

def _facts(source, adapter, pairs):
    core = adapter['core']
    left, right = source['staged'], core['staged']
    return {'empty_source_names': not source['source_name'] and not core['source_name'],
            'empty_incarnation_pairs': not pairs,
            'equal_live_generations': d.exact(source['source_generation'], core['source_generation']),
            'current_stage_freshness': bool(left and right
                and d.exact(left[0].source_generation, source['source_generation'])
                and d.exact(right[0].source_generation, core['source_generation']))}

def inspect_cases(cases, charge):
    out = {'status': 'supported', 'observations': [], 'limitations': [], 'audited_prefixes': 0}
    if not cases:
        out.update(status='not_applicable', limitations=['no typed retained cases supplied'])
        return out
    disjuncts, seen_absent = 0, set()

    def fail(defect, **witness):
        out['observations'].append({'kind': 'counterexample', 'defect': defect, **witness})
        raise _Fail

    try:
        for case in cases:
            ss, aa = t.restore(case['source']), t.restore(case['adapter'])
            t.sc.initialization(ss[0], case['unit'])
            t.audit.initialization(aa[0], case['unit'])
            profile = case['source']['profile']
            if not (d.exact(profile, case['adapter']['profile'])
                    and case['source']['actions'] == case['adapter']['actions']
                    and len(case['prefixes']) == len(ss) and len(case['rows']) == len(ss) - 1):
                fail('case-inventory', case=case.get('case'), states=len(ss),
                     prefixes=len(case.get('prefixes', ())))
            pairs, previous = [], None
            for prefix in range(len(ss)):
                try:
                    charge.take(1)
                except ERRORS as error:
                    raise _Charged(str(error))
                out['audited_prefixes'] += 1
                if prefix:
                    index = prefix - 1
                    action, row = case['source']['actions'][index], case['rows'][index]
                    oldpairs = copy.deepcopy(pairs)
                    t.sc.check(ss[index], action, ss[prefix], profile, case['unit'], case['outcome'])
                    binding = r.advance(pairs, ss[index], t.core_view(aa[index]), ss[prefix],
                                        t.core_view(aa[prefix]), action, action, index, index)
                    call = t.audit.check(aa[index], action, aa[prefix], profile,
                                         case['unit'], case['outcome'])
                    expected = t.comparison(ss[index], aa[index], ss[prefix], aa[prefix],
                                            oldpairs, pairs, action, index, call)
                    expected['binding'] = binding
                    if not (d.exact(expected, row) and call == row['q_invoked']
                            and t.response(ss[prefix], aa[prefix], action, pairs)
                            == row['responses_related']):
                        fail('transition-row', case=case.get('case'), prefix=prefix,
                             expected_sha256=d.digest(expected), observed_sha256=d.digest(row))
                item, saved = case['prefixes'][prefix], copy.deepcopy(pairs)
                try:
                    identity_audit.check(item, case, ss, aa, prefix, pairs)
                except ERRORS as error:
                    src, adp = ss[prefix], aa[prefix]
                    fail('prefix-certificate', case=case.get('case'), prefix=prefix,
                         reason=str(error)[:160], observed_rule=item.get('staged_rule'),
                         observed_related=item.get('related'),
                         recomputed_common=[k for k in r.FIELDS
                             if r.field_view(src, k, 'source', pairs)
                             != r.field_view(adp['core'], k, 'target', pairs)],
                         recomputed_journal=[k for k in (*d.s.EXTRA, 'source_generation')
                             if r.typed(src[k]) != r.typed(adp['journal'][k])])
                if not d.exact(pairs, saved):
                    fail('identity-mutated-incarnation-ledger', case=case.get('case'), prefix=prefix)
                if item['incarnation_pair_established_by_identity'] is not False:
                    fail('identity-claimed-authority', case=case.get('case'), prefix=prefix)
                if prefix and not (item['strict_related'] == case['rows'][prefix - 1]['state_related']
                                   and previous == case['rows'][prefix - 1]['prestate_related']):
                    fail('strict-baseline', case=case.get('case'), prefix=prefix)
                previous = item['strict_related']
                facts = _facts(ss[prefix], aa[prefix], pairs)
                if item['staged_rule'] == 'original-object-identity' and item['related']:
                    disjuncts += 1
                    seen_absent |= {k for k, v in facts.items() if not v}
                    if len(out['observations']) < 16:
                        out['observations'].append({'kind': 'accepted-staged-disjunct',
                            'case': case['case'], 'prefix': prefix,
                            'identity_proof': bool(item['identity_proof']),
                            'narrowing_facts_observed_only': facts})
            if not d.exact(pairs, case['incarnation_pairs']):
                fail('incarnation-ledger', case=case.get('case'))
        out['observations'].append({'kind': 'audit-accounting', 'cases': len(cases),
            'accepted_staged_disjuncts': disjuncts,
            'disjunct_provenance': 'identical typed staged objects + own signature/payload'
            ' binding + same stage-origin event; no narrowing fact consulted'})
        if not disjuncts:
            out['status'] = 'unproved'
            out['limitations'].append('no inspected prefix exercised the staged-identity disjunct')
        for name in NARROWING:
            if name not in seen_absent:
                out['limitations'].append('every accepted disjunct exhibited ' + name + ';'
                    ' non-narrowing rests on recomputation structure, not a counterfactual witness')
    except _Fail:
        out['status'] = 'counterexample'
    except _Charged as error:
        out['status'] = 'unproved'
        out['limitations'].append('charge exhausted during audit: ' + str(error)[:160])
    except ERRORS as error:
        out['status'] = 'counterexample'
        out['observations'].append({'kind': 'counterexample', 'defect': 'audit-failure',
                                    'reason': str(error)[:240]})
    return out

def run_controls(cases, inspect_cases, charge):
    baseline = inspect_cases(cases, charge) if cases else {'status': 'not_applicable'}
    controls = []

    def find(key, pred):
        for ci, case in enumerate(cases):
            for i, x in enumerate(case[key]):
                if pred(x):
                    return ci, i
        return None

    def probe(label, target, mutate, domain='certificate-corruption'):
        entry = {'control': label, 'mutation_domain': domain, 'original_domain_counterexample': False}
        if target is None:
            entry.update(detected=None, missing_witness=True)
        else:
            bad = copy.deepcopy(cases[target[0]])
            mutate(bad, target[1])
            res = inspect_cases([bad], charge)
            witness = next((o for o in res['observations'] if o['kind'] == 'counterexample'), None)
            entry.update(detected=res['status'] == 'counterexample', status=res['status'], witness=witness)
        controls.append(entry)

    disj = find('prefixes', lambda x: x['identity_proof'] and x['staged_rule'] == 'original-object-identity')
    probe('accepted-disjunct-drops-origin-proof', disj, lambda b, i: b['prefixes'][i].update(identity_proof=None))
    probe('identity-proof-cross-case-graft', disj, lambda b, i: b['prefixes'][i]['identity_proof'].update(case='other-case'))
    probe('identity-proof-future-origin', disj, lambda b, i: b['prefixes'][i]['identity_proof']['source_origin'].update(event_index=i + 1))
    probe('identity-claims-incarnation-authority', disj, lambda b, i: b['prefixes'][i].update(incarnation_pair_established_by_identity=True))
    probe('narrowed-relation-denies-valid-disjunct', disj, lambda b, i: b['prefixes'][i].update(staged_rule='unrelated', related=False, identity_proof=None, differing_common_fields=b['prefixes'][i]['strict_differing_common_fields']))
    probe('strict-gap-relabeled-related', find('prefixes', lambda x: not x['strict_related']), lambda b, i: b['prefixes'][i].update(strict_related=True, related=True, differing_common_fields=[], differing_journal_fields=[]))
    probe('journal-only-disagreement-erased', find('prefixes', lambda x: x['differing_journal_fields']), lambda b, i: b['prefixes'][i].update(differing_journal_fields=[], related=True))
    probe('visible-refusal-relabeled-ok', find('rows', lambda x: x['source_observation']['decision'].split(':')[-1] != 'ok'), lambda b, j: b['rows'][j]['source_observation'].update(decision='forged:ok'))
    probe('response-relation-flag-forged', (0, 0) if cases and cases[0]['rows'] else None, lambda b, j: b['rows'][j].update(responses_related=not b['rows'][j]['responses_related']))
    probe('dropped-prefix-certificate', (0, 0) if cases else None, lambda b, i: b['prefixes'].pop())
    probe('corrupted-retained-adapter-state', (0, 0) if cases and cases[0]['adapter']['events'] else None, lambda b, i: b['adapter']['events'][0]['patch'].update(forged='x'), domain='state-binding')
    return {'baseline_status': baseline.get('status'), 'controls': controls,
            'all_detected': all(x['detected'] for x in controls if x['detected'] is not None),
            'missing_witnesses': [x['control'] for x in controls if x.get('missing_witness')],
            'counterexample_domain': 'mutations corrupt retained certificates/states; an undetected'
                ' mutation is a checker defect, not an original-domain counterexample'}
