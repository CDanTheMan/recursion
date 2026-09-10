"""Retain strict outcomes and compare a staged-only identity relation on audited histories."""
import copy
import identity as relation
import identity_audit as audit
import histories

t, d, r = relation.frozen, relation.d, relation.r


def run(packet):
    baseline = t.run(packet)
    extra = histories.run()
    visits = baseline['state_visits_per_representation'] + sum(2 * (len(c['rows']) + 1) for c in extra)
    d.require(visits <= 10000, 'combined source and adapter traversal ceiling')
    summaries, samples = [], []
    for family, cases in (('original-canonical', baseline['cases']), ('explicit-additional-history', extra)):
        for case in cases:
            ss, aa = t.restore(case['source']), t.restore(case['adapter'])
            pairs, prefixes = [], []
            for prefix in range(len(ss)):
                if prefix:
                    i = prefix - 1; action = case['source']['actions'][i]
                    row = case['rows'][i]
                    d.require(action == case['adapter']['actions'][i] == row['source_action'] == row['adapter_action'], 'one identical literal action occurrence')
                    binding = r.advance(pairs, ss[i], t.core_view(aa[i]), ss[prefix], t.core_view(aa[prefix]), action, action, i, i)
                    d.require(binding == row['binding'] and all(x['source_event'] <= i and x['target_event'] <= i for x in pairs), 'unchanged causal prefix pair advancement')
                    d.require(d.exact(row['justification'], d.justification(action, row['q_invoked'])), 'retained justification for every action translation')
                    d.require(t.response(ss[prefix], aa[prefix], action, pairs) == row['responses_related'], 'unchanged visible response relation')
                before = copy.deepcopy(pairs)
                item = relation.compare(case, ss, aa, prefix, pairs)
                audit.check(item, case, ss, aa, prefix, pairs)
                d.require(d.exact(before, pairs), 'neither identity comparison nor audit establishes a pair')
                if prefix:
                    d.require(item['strict_related'] == case['rows'][prefix - 1]['state_related']
                              and prefixes[-1]['strict_related'] == case['rows'][prefix - 1]['prestate_related'], 'preserved strict prestate and poststate results')
                prefixes.append(item); samples.append((case, ss, aa, prefix, copy.deepcopy(pairs), item))
            d.require(d.exact(pairs, case['incarnation_pairs']), 'complete immutable original incarnation ledger')
            summaries.append(dict(case=case['case'], family=family, prefixes=prefixes,
                strict_complete=case['complete_selected_trace_correspondence'],
                extended_complete=all(x['related'] for x in prefixes) and all(x['responses_related'] for x in case['rows']),
                visible_responses_matched=sum(x['responses_related'] for x in case['rows']),
                journal_poststates_matched=sum(not x['differing_journal_fields'] for x in prefixes[1:]),
                events=len(case['rows']), identity_poststates=sum(x['staged_rule'] == 'original-object-identity' for x in prefixes[1:])))

    controls = []
    def reject(label, fn):
        try: fn()
        except (ValueError, KeyError, IndexError, TypeError) as error:
            controls.append(dict(control=label, detected=True, reason=str(error)))
        else: raise ValueError('undetected control: ' + label)
    witness = next(x for x in samples if x[5]['staged_rule'] == 'original-object-identity')
    case, ss, aa, prefix, pairs, item = witness
    staged = ss[prefix]['staged']
    def invalid_objects(label, left, right):
        reject(label, lambda: d.require(relation.identical(left, right) or audit.valid_objects(left, right), 'both independent identity predicates reject altered originals'))
    forged = (staged[0]._replace(signature='0' * 64), staged[1])
    invalid_objects('equal-forged-original-signatures', forged, forged)
    corrupt = (staged[0], staged[1] + '-corrupt')
    invalid_objects('equal-corrupt-actual-staged-payloads', corrupt, corrupt)
    invalid_objects('changed-stage-container-type', list(staged), list(staged))
    unequal = next(x for x in samples if x[3] and x[1][x[3]]['staged'] and x[2][x[3]]['core']['staged']
                   and r.pair_envelope(x[1][x[3]]['staged'][0], x[2][x[3]]['core']['staged'][0], x[4])
                   and not d.exact(x[1][x[3]]['staged'], x[2][x[3]]['core']['staged']))
    invalid_objects('unequal-original-incarnations-have-no-identity-shortcut', unequal[1][unequal[3]]['staged'], unequal[2][unequal[3]]['core']['staged'])
    another = next(x[1][x[3]]['staged'] for x in samples if x[1][x[3]]['staged']
                   and r.signed(x[1][x[3]]['staged'][0]) and x[1][x[3]]['staged'][0].request != staged[0].request)
    invalid_objects('different-original-stage-request', staged, another)
    for label, mutate in (
        ('future-stage-origin', lambda x: x['identity_proof']['source_origin'].update(event_index=prefix)),
        ('detached-prefix-hash', lambda x: x['identity_proof'].update(source_prefix_sha256='0' * 64)),
        ('cross-case-origin', lambda x: x['identity_proof'].update(case='different-case')),
        ('identity-falsely-establishes-pair', lambda x: x.update(incarnation_pair_established_by_identity=True)),
    ):
        bad = copy.deepcopy(item); mutate(bad)
        reject(label, lambda: audit.check(bad, case, ss, aa, prefix, pairs))
    for key, value in (('selected', staged[0]), ('installed_cut', staged), ('reader_copies', (staged, ()))):
        left, right = copy.deepcopy(ss), copy.deepcopy(aa)
        left[prefix][key] = copy.deepcopy(value); right[prefix]['core'][key] = copy.deepcopy(value)
        bad = relation.compare(case, left, right, prefix, pairs)
        reject('no-identity-exception-for-' + key, lambda: d.require(bad['related'], 'exception remains confined to staged field'))
    receipt = (staged[0].request, r.digest(staged[0]), staged[0].expected_revision + 1, staged[0].generation, staged[0].content)
    reject('no-identity-exception-for-receipts', lambda: d.require(r.pair_receipt(staged[0], receipt, staged[0], receipt, pairs), 'receipt still requires established incarnation pairing'))
    damaged = copy.deepcopy(case['source']); damaged['events'].pop(0)
    reject('dropped-visible-source-event', lambda: t.restore(damaged))

    focused = []
    for case in extra:
        ss, aa = t.restore(case['source']), t.restore(case['adapter'])
        facts = dict(first_attestation_refused=ss[17]['decision'] == aa[17]['decision'] == 'source-attest:incomplete-inventory',
            first_stage_identical=relation.identical(ss[18]['staged'], aa[18]['core']['staged']),
            later_attestation_succeeds=ss[20]['decision'] == aa[20]['decision'] == 'source-attest:ok',
            old_stage_retained=d.exact(ss[18]['staged'], ss[20]['staged']) and d.exact(aa[18]['core']['staged'], aa[20]['core']['staged']),
            actual_first_pair=d.exact(case['incarnation_pairs'], [dict(source=d.q.source_token(0), target=d.q.source_token(1), reason='paired-successful-attestation', source_event=19, target_event=19)]),
            stale_publication_refused=ss[21]['decision'] == aa[21]['decision'] == 'pub-commit:source-boundary-stale' and not case['rows'][20]['q_invoked'],
            refusal_preserves_Q=d.exact(aa[20]['core'], aa[21]['core']),
            restaged_publication_succeeds=ss[23]['decision'] == aa[23]['decision'] == 'pub-commit:ok' and ss[23]['publication_revision'] == aa[23]['core']['publication_revision'] == 1)
        d.require(all(facts.values()), 'nonvacuous focused original-object / first-attestation / stale-authority boundary')
        focused.append(dict(case=case['case'], facts=facts))
    canonical = [x for x in summaries if x['family'] == 'original-canonical']
    additional = [x for x in summaries if x['family'] == 'explicit-additional-history']
    d.require(baseline['complete_selected_trace_cases'] == (80 if packet == 'C' else 10), 'unchanged strict canonical baseline')
    return dict(packet=packet, frozen_baseline=baseline, additional_histories=extra, comparisons=summaries,
        focused_certificates=focused, controls=controls, inherited_controls=len(baseline['controls']),
        state_visits_per_representation=visits, state_visit_reservation=10000,
        canonical_cases=len(canonical), canonical_strict_complete=sum(x['strict_complete'] for x in canonical),
        canonical_extended_complete=sum(x['extended_complete'] for x in canonical),
        additional_cases=len(additional), additional_strict_complete=sum(x['strict_complete'] for x in additional),
        additional_extended_complete=sum(x['extended_complete'] for x in additional),
        canonical_identity_poststates=sum(x['identity_poststates'] for x in canonical),
        additional_identity_poststates=sum(x['identity_poststates'] for x in additional),
        visible_responses_matched=sum(x['visible_responses_matched'] for x in summaries),
        journal_poststates_matched=sum(x['journal_poststates_matched'] for x in summaries),
        events=sum(x['events'] for x in summaries), original_models_changed=False,
        original_strict_relation_changed=False, identity_grants_authority=False,
        all_interleavings_checked=False, original_Q_profile_reachability_proved=False,
        unrestricted_refinement_proved=False, whole_path_composition_proved=False, source_truth_established=False)
