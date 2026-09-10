"""Enumerate declared finite schedules; replay unchanged source/adapter semantics."""
import argparse
import copy
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
NAME = 'eight-hour-research-20260910-01a08a22'
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-07'))
import identity as relation
import identity_audit
import histories
import q_artifact as codec
import artifact
t, d, r = relation.frozen, relation.d, relation.r

class Counter:
    def __init__(self, limit):
        d.require(type(limit) is int and limit >= 0, 'finite visit ceiling')
        self.limit, self.visits = limit, 0
    def take(self, n):
        d.require(self.visits + n <= self.limit, 'checked state counter before initialization/transition')
        self.visits += n

def domain(spec):
    before = d.digest(d.s.PROFILES)
    if spec['domain'] == 'first-attestation-antichain':
        p = copy.deepcopy(d.s.PROFILES['delayed-record'])
        actions = histories.ACTIONS
        p.update(actions=actions, requires={a: () if i == 0 else (actions[i-1],) for i, a in enumerate(actions)})
        for a in actions[17:20]: p['requires'][a] = (actions[16],)
        p['requires'][actions[20]] = actions[17:20]
    else:
        p = copy.deepcopy(d.s.PROFILES[spec['domain']])
    d.require(d.digest(d.s.PROFILES) == before, 'original profile registry unchanged')
    return p

def inventory(profile):
    actions = profile['actions']
    d.require(len(actions) == len(set(actions)), 'unique literal occurrence inventory')
    masks = tuple(sum(1 << actions.index(b) for b in profile['requires'][a]) for a in actions)
    full = (1 << len(actions)) - 1
    @lru_cache(None)
    def count(mask):
        if mask == full: return 1
        return sum(count(mask | (1 << i)) for i, dependencies in enumerate(masks)
                   if not mask & (1 << i) and mask & dependencies == dependencies)
    def generate(prefix=()):
        if len(prefix) == len(actions):
            yield prefix
            return
        done = set(prefix)
        for a in sorted(actions):
            if a not in done and set(profile['requires'][a]) <= done:
                yield from generate(prefix + (a,))
    schedules = tuple(generate())
    validate_inventory(profile, schedules, count(0))
    return schedules, count(0)

def validate_inventory(profile, schedules, expected):
    d.require(len(schedules) == expected and len(set(schedules)) == expected, 'complete unique schedule inventory')
    for schedule in schedules:
        d.require(len(schedule) == len(profile['actions']) and set(schedule) == set(profile['actions']), 'exact original action occurrences')
        done = set()
        for a in schedule:
            d.require(set(profile['requires'][a]) <= done, 'schedule dependencies')
            done.add(a)

def run_history(profile, schedule, unit, outcome, name, counter):
    counter.take(2)
    source, adapter = d.s.initial(unit), d.initial(unit)
    t.sc.initialization(source, unit); t.audit.initialization(adapter, unit)
    st = dict(side='source', initial=copy.deepcopy(source), profile=profile, actions=schedule, events=[])
    at = dict(side='adapter', initial=copy.deepcopy(adapter), profile=profile, q_profile=d.subprofile(profile), actions=schedule, events=[])
    pairs, rows = [], []
    for index, action in enumerate(schedule):
        counter.take(2)
        d.require(set(d.s.ready_actions(source, profile)) == t.sc.enabled(source, profile)
                  and action in t.sc.enabled(source, profile), 'complete original enabledness')
        ns = t.sa.step(source, action, profile, unit, outcome)
        d.require(d.exact(ns, d.s.flatten(t.sb.step(d.s.split(source), action, profile, unit, outcome))), 'unchanged S implementations agree')
        t.sc.check(source, action, ns, profile, unit, outcome)
        na = t.aa.step(adapter, action, profile, unit, outcome)
        d.require(d.exact(na, t.ab.step(adapter, action, profile, unit, outcome)), 'unchanged adapter implementations agree')
        call = t.audit.check(adapter, action, na, profile, unit, outcome)
        oldpairs = copy.deepcopy(pairs)
        binding = r.advance(pairs, source, t.core_view(adapter), ns, t.core_view(na), action, action, index, index)
        row = t.comparison(source, adapter, ns, na, oldpairs, pairs, action, index, call)
        row['binding'] = binding
        rows.append(row)
        st['events'].append(t.trace_event(source, ns, action))
        at['events'].append(t.trace_event(adapter, na, action, True))
        source, adapter = ns, na
    case = dict(case=name, unit=unit, outcome=outcome, source=st, adapter=at, rows=rows, incarnation_pairs=pairs)
    case['prefixes'] = audit_case(case)
    return case

def audit_case(case):
    ss, aa = t.restore(case['source']), t.restore(case['adapter'])
    pairs, prefixes = [], []
    d.require(case['source']['actions'] == case['adapter']['actions'], 'all visible actions matched')
    for prefix in range(len(ss)):
        if prefix:
            i = prefix - 1
            action, row = case['source']['actions'][i], case['rows'][i]
            binding = r.advance(pairs, ss[i], t.core_view(aa[i]), ss[prefix], t.core_view(aa[prefix]), action, action, i, i)
            d.require(d.exact(binding, row['binding']), 'actual chronological causal pair binding')
            d.require(row['source_action'] == row['adapter_action'] == action and row['index'] == i, 'literal chronological event equality')
            call = t.audit.check(aa[i], action, aa[prefix], case['source']['profile'], case['unit'], case['outcome'])
            d.require(call == row['q_invoked'] and d.exact(row['justification'], d.justification(action, call)), 'actual Q invocation and translation retained')
            d.require(t.response(ss[prefix], aa[prefix], action, pairs) == row['responses_related'], 'visible response relation retained')
        saved = copy.deepcopy(pairs)
        item = relation.compare(case, ss, aa, prefix, pairs)
        identity_audit.check(item, case, ss, aa, prefix, pairs)
        d.require(d.exact(saved, pairs), 'identity creates no authority')
        if prefix:
            d.require(item['strict_related'] == case['rows'][prefix-1]['state_related'] and prefixes[-1]['strict_related'] == case['rows'][prefix-1]['prestate_related'], 'strict relation baseline retained')
        prefixes.append(item)
    d.require(d.exact(pairs, case['incarnation_pairs']), 'complete immutable causal pair ledger')
    return prefixes

def summarize(case):
    prefixes, rows = case['prefixes'], case['rows']
    return dict(case=case['case'], schedule=case['source']['actions'],
        strict_complete=all(x['strict_related'] for x in prefixes) and all(x['responses_related'] for x in rows),
        extended_complete=all(x['related'] for x in prefixes) and all(x['responses_related'] for x in rows),
        visible_events=len(rows), matching_responses=sum(x['responses_related'] for x in rows),
        matching_journals=sum(not x['differing_journal_fields'] for x in prefixes[1:]),
        identity_poststates=sum(x['staged_rule'] == 'original-object-identity' for x in prefixes[1:]),
        strict_first_gap=next((i for i, x in enumerate(prefixes) if not x['strict_related']), None),
        extended_first_gap=next((i for i, x in enumerate(prefixes) if not x['related'] or (i and not rows[i-1]['responses_related'])), None),
        decisions=[x['patch'].get('decision') for x in case['source']['events']],
        original_profile_sha256=d.digest(case['source']['profile']))

def main(spec_path, output, limit):
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    profile = domain(spec)
    schedules, count = inventory(profile)
    expected_visits = 2 * (len(profile['actions']) + 1) * count * len(d.s.UNITS) * len(profile['outcomes'])
    d.require(count == spec['schedules_per_unit_outcome'] and expected_visits == spec['exploration_visits'], 'independent DP/analytical domain count')
    d.require(expected_visits <= limit == spec['reservation'], 'finite full-domain pre-initialization admission')
    original = d.digest(d.s.PROFILES)
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
    output.mkdir(parents=True, exist_ok=False)
    counter, results, sample, identity_sample, causal_sample = Counter(limit), [], None, None, None
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
                if causal_sample is None and any(x['source_event'] != 19 for x in case['incarnation_pairs']): causal_sample = copy.deepcopy(case)
                for kind in best:
                    prefix = summary[kind + '_first_gap']
                    if prefix is not None and (best[kind] is None or prefix < best[kind]['prefix']):
                        best[kind] = dict(case=name, prefix=prefix, artifact=target.name,
                            prefix_actions=schedule[:prefix], minimality='earliest failing prefix across all completed histories in this declared domain')
        if schedule_index % 25 == 0:
            print(json.dumps(dict(completed_schedules=schedule_index+1, total_schedules=count, visits=counter.visits)), flush=True)
    d.require(counter.visits == expected_visits and len(results) == spec['environments'], 'complete admitted domain and exact actual visits')
    d.require(d.digest(d.s.PROFILES) == original, 'historical profile registry preserved')
    # Retained-state controls reconstruct evidence; they execute no model reducers.
    damaged = copy.deepcopy(sample); damaged['source']['events'].pop()
    reject('dropped-visible-event', lambda: audit_case(damaged))
    damaged = copy.deepcopy(sample); damaged['rows'][0]['justification'] = {'forged': True}
    reject('changed-action-translation', lambda: audit_case(damaged))
    damaged = copy.deepcopy(sample); damaged['rows'][0]['q_invoked'] = not damaged['rows'][0]['q_invoked']
    reject('refused-or-invoked-Q-mask-change', lambda: audit_case(damaged))
    damaged = copy.deepcopy(sample)
    damaged['adapter']['q_profile']['actions'] = tuple(reversed(damaged['adapter']['q_profile']['actions']))
    reject('renumbered-Q-occurrence-positions', lambda: audit_case(damaged))
    if causal_sample is not None:
        damaged = copy.deepcopy(causal_sample); damaged['incarnation_pairs'][0]['source_event'] = 19
        reject('occurrence-suffix-used-as-causal-index', lambda: audit_case(damaged))
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
    result = dict(packet=spec['id'], domain=spec['domain'], schedules=count, environments=len(results),
        state_visits_per_representation=counter.visits, reservation=limit,
        strict_complete=sum(x['strict_complete'] for x in results), extended_complete=sum(x['extended_complete'] for x in results),
        visible_events=sum(x['visible_events'] for x in results), matching_responses=sum(x['matching_responses'] for x in results),
        matching_journals=sum(x['matching_journals'] for x in results), identity_poststates=sum(x['identity_poststates'] for x in results),
        domain_profile_sha256=d.digest(profile), schedule_inventory_sha256=d.digest(schedules),
        controls=controls, cases=results, minimized_prefixes=best, status='COMPLETE_DECLARED_FINITE_DOMAIN',
        original_Q_profile_reachability_proved=False, unrestricted_refinement_proved=False,
        whole_path_composition_proved=False, source_truth_established=False, reductions_used=False)
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
