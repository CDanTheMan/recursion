"""preregistered 24-order subset of the unchanged eight-action race."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
from baseline import check as c
from baseline import ROOT, OLD_CODE, NEW_CODE, NEW_DOC, packet_doc, reference_script, added_module_paths
from check import ROOT, NAME, d, t, r, artifact, codec, identity_audit, Counter, domain, validate_inventory, run_history, audit_case, summarize

FIRST_CORE = ('collect:0@12','collect:1@13','attempt:3@16','attempt:4@17')
REMAINING_CORE = ('collect-open@11','collect:2@14','attempt:2@15','source-restart@18')

def inventory(profile):
    original, count = c.inventory(profile)
    d.require(count == 40320 and len(profile['actions']) == 34, 'unchanged original eight-action inventory')
    d.require(set(profile['actions'][11:19]) == set(FIRST_CORE + REMAINING_CORE), 'exact original eight core occurrences')
    selected = tuple(s for s in original if s[11:15] == FIRST_CORE)
    d.require(len(selected) == 24 and all(set(s[15:19]) == set(REMAINING_CORE) and s[:11] == profile['actions'][:11] and s[19:] == profile['actions'][19:] for s in selected), 'exact selected four-action orders and unchanged fixed prefix/suffix')
    # Independent constraint-specific subset enumeration; original requires stay intact.
    def permute(left):
        if not left: yield ()
        for a in sorted(left):
            for rest in permute(tuple(x for x in left if x != a)): yield (a,) + rest
    expected = tuple(sorted(profile['actions'][:11] + FIRST_CORE + middle + profile['actions'][19:] for middle in permute(REMAINING_CORE)))
    d.require(selected == expected, 'independent complete selected schedule enumeration')
    validate_inventory(profile, selected, 24)
    return selected, 24

def validate_selection(profile, schedules):
    validate_inventory(profile,schedules,24)
    d.require(all(s[11:15] == FIRST_CORE for s in schedules), 'every history satisfies the declared selected first-four constraint')

def main(spec_path, output, limit):
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    manifest = json.loads((ROOT / 'docs/v3/construction/cut-source-overnight-20260908/batch-07/manifest.json').read_text())
    registered = {x['path'] for x in manifest['inputs']} | set(manifest['sources'])
    registered |= added_module_paths()
    def modules():
        paths = set()
        for module in tuple(sys.modules.values()):
            source = getattr(module, '__file__', None)
            if source:
                path = Path(source).resolve()
                if path.is_relative_to(ROOT) and path.suffix == '.py': paths.add(path.relative_to(ROOT).as_posix())
        d.require(paths <= registered, 'registered immutable/new local module closure: ' + repr(sorted(paths - registered)))
        return paths
    initial_modules = modules()
    d.require(spec['domain'] == 'scale-eight-action-race' and spec['selected_first_core'] == list(FIRST_CORE) and spec['remaining_permuted_core'] == list(REMAINING_CORE) and spec['original_profile_schedules_per_unit_outcome'] == 40320, 'declared selected original domain')
    profile = domain(spec)
    d.require(list(d.s.UNITS) == spec['units'] and list(profile['outcomes']) == spec['outcomes']
              and len(profile['actions']) == spec['actions_per_history'], 'exact declared environments and action depth')
    schedules, count = inventory(profile)
    expected_visits = 2 * (len(profile['actions']) + 1) * count * len(d.s.UNITS) * len(profile['outcomes'])
    d.require(count == spec['schedules_per_unit_outcome'] and expected_visits == spec['exploration_visits'], 'independent DP/analytical domain count')
    d.require(expected_visits <= limit == spec['reservation'], 'finite declared 24-order subset pre-initialization admission')
    original = d.digest(d.s.PROFILES)
    validate_selection(profile,schedules)
    controls = []
    def reject(label, fn):
        try: fn()
        except (ValueError, KeyError, IndexError, TypeError) as error:
            controls.append(dict(control=label, detected=True, reason=str(error)))
        else: raise ValueError('undetected control: ' + label)
    reject('omitted-schedule', lambda: validate_inventory(profile, schedules[:-1], count))
    reject('duplicate-replaces-schedule', lambda: validate_inventory(profile, schedules[:-1] + schedules[:1], count))
    bad = list(schedules[0]); bad[0], bad[1] = bad[1], bad[0]
    reject('violated-dependency', lambda: validate_inventory(profile, (tuple(bad),), 1))
    reject('undercharged-initialization', lambda: Counter(1).take(2))
    outside = list(schedules[0]); outside[11], outside[12] = outside[12], outside[11]
    validate_inventory(profile,(tuple(outside),),1)
    reject('topologically-valid-out-of-subset-history', lambda: validate_selection(profile,(tuple(outside),)+schedules[1:]))
    output.mkdir(parents=True, exist_ok=False)
    counter, results, sample, identity_sample = Counter(limit), [], None, None
    best = {'strict': None, 'extended': None}
    for schedule_index, schedule in enumerate(schedules):
        for unit in d.s.UNITS:
            for outcome in profile['outcomes']:
                name = spec['id'] + '/' + str(schedule_index).zfill(6) + '/' + unit + '/' + str(outcome)
                case = run_history(profile, schedule, unit, outcome, name, counter)
                summary = summarize(case)
                target = output / (str(len(results)).zfill(6) + '.json.gz')
                raw = json.dumps(codec.pack(artifact.encode(case)), sort_keys=True, separators=(',', ':')).encode()
                target.write_bytes(gzip.compress(raw, compresslevel=6, mtime=0))
                restored = artifact.decode(codec.unpack(json.loads(gzip.decompress(target.read_bytes()))))
                d.require(d.exact(case, restored) and d.exact(audit_case(restored), case['prefixes']), 'typed on-disk replay reproduces every checked prefix')
                summary.update(artifact=target.name, artifact_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
                results.append(summary)
                if sample is None: sample = copy.deepcopy(case)
                if identity_sample is None and any(x['identity_proof'] for x in case['prefixes']): identity_sample = copy.deepcopy(case)
                for kind in best:
                    prefix = summary[kind + '_first_gap']
                    if prefix is not None and (best[kind] is None or prefix < best[kind]['prefix']):
                        best[kind] = dict(case=name, prefix=prefix, artifact=target.name,
                            prefix_actions=schedule[:prefix], minimality='earliest failing prefix across all 48 histories in the declared 24-order subset')
        if schedule_index % 25 == 0:
            print(json.dumps(dict(completed_schedules=schedule_index+1, total_schedules=count, visits=counter.visits)), flush=True)
    d.require(counter.visits == expected_visits and len(results) == spec['environments'], 'complete admitted domain and exact actual visits')
    d.require(d.digest(d.s.PROFILES) == original, 'historical profile registry preserved')
    # Retained-state controls reconstruct evidence; they execute no model reducers.
    damaged = copy.deepcopy(sample); damaged['source']['actions'] = list(damaged['source']['actions'])
    reject('typed-transport-tuple-loss', lambda: audit_case(damaged))
    damaged = copy.deepcopy(sample); damaged['source']['events'].pop()
    reject('dropped-visible-event', lambda: audit_case(damaged))
    damaged = copy.deepcopy(sample); damaged['rows'][0]['justification'] = {'forged': True}
    reject('changed-action-translation', lambda: audit_case(damaged))
    damaged = copy.deepcopy(sample); damaged['rows'][0]['q_invoked'] = not damaged['rows'][0]['q_invoked']
    reject('refused-or-invoked-Q-mask-change', lambda: audit_case(damaged))
    damaged = copy.deepcopy(sample)
    damaged['adapter']['q_profile']['actions'] = tuple(reversed(damaged['adapter']['q_profile']['actions']))
    reject('renumbered-Q-occurrence-positions', lambda: audit_case(damaged))
    synthetic = copy.deepcopy(sample)
    for x in synthetic['prefixes']: x['strict_related'] = x['related'] = True
    for x in synthetic['rows']: x['responses_related'] = True
    synthetic['rows'][0]['responses_related'] = False
    synthetic_summary = summarize(synthetic)
    d.require(not synthetic_summary['strict_complete'] and not synthetic_summary['extended_complete']
              and synthetic_summary['strict_first_gap'] == synthetic_summary['extended_first_gap'] == 1,
              'response-only failure has its earliest prefix witness')
    controls.append(dict(control='response-only-witness-selection', detected=True, reason='response-only retained evidence yields prefix 1 for both relations'))
    d.require(identity_sample is not None, 'required nonvacuous staged identity witness in selected domain')
    damaged = copy.deepcopy(sample)
    index = next(i for i,a in enumerate(damaged['source']['actions']) if i != int(a.rsplit('@',1)[1]))
    damaged['rows'][index]['index'] = int(damaged['source']['actions'][index].rsplit('@',1)[1])
    reject('occurrence-suffix-used-as-row-index', lambda: audit_case(damaged))
    damaged = copy.deepcopy(sample)
    d.require(not damaged['incarnation_pairs'], 'actual empty causal ledger control witness')
    token = t.restore(sample['source'])[-1]['source_generation']
    damaged['incarnation_pairs'].append(dict(source=token,target=token,reason='fabricated',source_event=0,target_event=0))
    reject('fabricated-pair-in-empty-ledger', lambda: audit_case(damaged))
    if identity_sample is not None:
        case = identity_sample
        ss, aa = t.restore(case['source']), t.restore(case['adapter'])
        prefix = next(i for i, x in enumerate(case['prefixes']) if x['identity_proof'])
        pairs = []
        for i in range(prefix):
            action = case['source']['actions'][i]
            r.advance(pairs, ss[i], t.core_view(aa[i]), ss[i+1], t.core_view(aa[i+1]), action, action, i, i)
        for label, mutate in (
            ('cross-schedule-identity-proof', lambda x: x['identity_proof'].update(case='other-schedule')),
            ('future-stage-origin', lambda x: x['identity_proof']['source_origin'].update(event_index=prefix)),
            ('detached-prefix-hash', lambda x: x['identity_proof'].update(source_prefix_sha256='0'*64)),
            ('identity-creates-authority', lambda x: x.update(incarnation_pair_established_by_identity=True))):
            bad = copy.deepcopy(case['prefixes'][prefix]); mutate(bad)
            reject(label, lambda: identity_audit.check(bad, case, ss, aa, prefix, pairs))
    d.require(len(controls) == len(spec['required_controls'])
              and {x['control'] for x in controls} == set(spec['required_controls']), 'complete preregistered control inventory')
    observed = {}
    for item in results:
        decision = next(x for x in item['decisions'] if x.startswith('source-attest:'))
        observed[decision] = observed.get(decision,0)+1
    result = dict(packet=spec['id'], domain=spec['domain'], schedules=count, environments=len(results),
        observed_attestation_decisions=observed,
        registered_local_modules=sorted(initial_modules | modules()),
        state_visits_per_representation=counter.visits, reservation=limit,
        strict_complete=sum(x['strict_complete'] for x in results), extended_complete=sum(x['extended_complete'] for x in results),
        visible_events=sum(x['visible_events'] for x in results), matching_responses=sum(x['matching_responses'] for x in results),
        matching_journals=sum(x['matching_journals'] for x in results), identity_poststates=sum(x['identity_poststates'] for x in results),
        domain_profile_sha256=d.digest(profile), schedule_inventory_sha256=d.digest(schedules),
        controls=controls, cases=results, minimized_prefixes=best, status='COMPLETE_DECLARED_FINITE_DOMAIN',
        original_Q_profile_reachability_proved=False, unrestricted_refinement_proved=False,
        whole_path_composition_proved=False, source_truth_established=False, reductions_used=False,
        original_full_schedules_per_environment=40320, selected_first_core=list(FIRST_CORE),
        complete_original_profile_coverage=False)
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('cases', 'controls', 'minimized_prefixes')}, sort_keys=True), flush=True)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--spec', type=Path, required=True); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--state-limit', type=int, required=True); args = p.parse_args()
    def deny_network_process(event, arguments):
        if event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
            raise RuntimeError('model network/process operation refused: ' + event)
    sys.addaudithook(deny_network_process)
    main(args.spec, args.output, args.state_limit)
