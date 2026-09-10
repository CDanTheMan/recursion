"""DRAFT: exhaustive original-profile shards and retained-evidence union audit."""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import check as c

COMMON = ['omitted-schedule', 'duplicate-replaces-schedule', 'violated-dependency',
          'undercharged-initialization', 'dropped-visible-event', 'changed-action-translation',
          'refused-or-invoked-Q-mask-change', 'renumbered-Q-occurrence-positions',
          'response-only-witness-selection']

def read(path): return json.loads(path.read_text(encoding='utf-8'))
def write(path, obj):
    with path.open('x',encoding='utf-8') as stream: stream.write(json.dumps(obj, indent=2) + '\n')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def decode(path): return c.artifact.decode(c.codec.unpack(json.loads(gzip.decompress(path.read_bytes()))))

def facts(case, spec):
    actions, rows = case['source']['actions'], case['rows']
    source = c.t.restore(case['source'])[-1]
    result = dict(incarnation_pairs=len(case['incarnation_pairs']),
                  chronological_index_witness=any(i != int(a.rsplit('@',1)[1]) for i,a in enumerate(actions)))
    if spec['domain'] == 'source-collection-race':
        capture = source['collection']
        current = bool(capture and capture[:2] == (source['source_generation'],source['source_revision']))
        complete = bool(capture and tuple(i for i,raw in source['collected']) == tuple(range(capture[4])))
        result.update(successful_collections=len(source['collected']), capture_current=current,
                      complete_current_inventory=current and complete, attestation_present=bool(source['attestation']))
    else:
        for field, literal in [('publication','pub-commit@19'),('attempt','attempt:2@20'),('append','append:later-start-only:3:normal@21')]:
            row = rows[actions.index(literal)]
            result[field + '_decision'] = row['source_observation']['decision']
            result[field + '_q_invoked'] = row['q_invoked']
        result['restart_chronological_index'] = actions.index('source-restart@22')
    return result

def source_modules():
    manifest = read(c.ROOT / 'docs/v3/construction/cut-source-overnight-20260908/batch-07/manifest.json')
    registered = {x['path'] for x in manifest['inputs']} | set(manifest['sources'])
    registered |= {'experiments/v3/' + c.NAME + '/' + x for x in ('check.py', 'artifact.py', 'sharded.py')}
    actual = set()
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(c.ROOT) and path.suffix == '.py': actual.add(path.relative_to(c.ROOT).as_posix())
    c.d.require(actual <= registered, 'closed local module inventory')
    return sorted(actual)

def declared(spec):
    c.d.require(spec['domain'] in ('source-collection-race', 'publication-source-race'), 'declared original race profile')
    profile = c.domain(spec)
    schedules, count = c.inventory(profile)
    split = spec['prefix_actions']
    core = tuple(spec['core_actions'])
    c.d.require(tuple(profile['actions'][split:]) == core and len(core) == 6, 'exact original six-action core')
    c.d.require(tuple(spec['units']) == c.d.s.UNITS and list(profile['outcomes']) == spec['outcomes'], 'unchanged units/outcomes')
    c.d.require(len(profile['actions']) == spec['actions_per_history'] and count == spec['schedules_per_unit_outcome'] == 720, 'original exhaustive domain count')
    c.d.require(all(s[:split] == tuple(profile['actions'][:split]) for s in schedules), 'fixed original prefix')
    c.d.require(spec['shard_keys'] == list(core) and len(set(core)) == 6, 'complete first-core partition keys')
    visits = 2 * (len(profile['actions']) + 1) * count * len(c.d.s.UNITS) * len(profile['outcomes'])
    c.d.require(visits == spec['exploration_visits'] == spec['reservation'], 'finite whole-domain charge')
    return profile, schedules

def rejection(controls, label, fn):
    try: fn()
    except (ValueError, KeyError, IndexError, TypeError) as error:
        controls.append(dict(control=label, detected=True, reason=str(error)))
    else: raise ValueError('undetected control: ' + label)

def replay_controls(profile, schedules, sample):
    controls = []
    reject = lambda label, fn: rejection(controls, label, fn)
    count = len(schedules)
    reject('omitted-schedule', lambda: c.validate_inventory(profile, schedules[:-1], count))
    reject('duplicate-replaces-schedule', lambda: c.validate_inventory(profile, schedules[:-1] + schedules[:1], count))
    bad = list(schedules[0]); bad[0], bad[1] = bad[1], bad[0]
    reject('violated-dependency', lambda: c.validate_inventory(profile, (tuple(bad),), 1))
    reject('undercharged-initialization', lambda: c.Counter(1).take(2))
    damaged = copy.deepcopy(sample); damaged['source']['events'].pop()
    reject('dropped-visible-event', lambda: c.audit_case(damaged))
    damaged = copy.deepcopy(sample); damaged['rows'][0]['justification'] = {'forged': True}
    reject('changed-action-translation', lambda: c.audit_case(damaged))
    damaged = copy.deepcopy(sample); damaged['rows'][0]['q_invoked'] = not damaged['rows'][0]['q_invoked']
    reject('refused-or-invoked-Q-mask-change', lambda: c.audit_case(damaged))
    damaged = copy.deepcopy(sample)
    damaged['adapter']['q_profile']['actions'] = tuple(reversed(damaged['adapter']['q_profile']['actions']))
    reject('renumbered-Q-occurrence-positions', lambda: c.audit_case(damaged))
    damaged = copy.deepcopy(sample)
    for x in damaged['prefixes']: x['strict_related'] = x['related'] = True
    for x in damaged['rows']: x['responses_related'] = True
    damaged['rows'][0]['responses_related'] = False
    summary = c.summarize(damaged)
    c.d.require(not summary['strict_complete'] and not summary['extended_complete'] and summary['strict_first_gap'] == summary['extended_first_gap'] == 1, 'response-only shortest-prefix witness')
    controls.append(dict(control='response-only-witness-selection', detected=True, reason='response-only evidence gives prefix 1 in both relations'))
    c.d.require([x['control'] for x in controls] == COMMON, 'complete nonvacuous shard controls')
    return controls

def shard(spec, key, output, limit):
    modules = source_modules()
    profile, whole = declared(spec)
    c.d.require(key in spec['shard_keys'], 'preregistered shard key')
    split = spec['prefix_actions']
    selected = tuple((i, s) for i, s in enumerate(whole) if s[split] == key)
    schedules = tuple(s for i, s in selected)
    c.validate_inventory(profile, schedules, 120)
    expected = spec['reservation'] // len(spec['shard_keys'])
    c.d.require(expected == limit == spec['visits_per_shard'], 'finite shard pre-initialization reservation')
    counter, results, sample = c.Counter(limit), [], None
    output.mkdir(parents=True, exist_ok=False)
    original = c.d.digest(c.d.s.PROFILES)
    for completed, (index, schedule) in enumerate(selected, 1):
        for unit in c.d.s.UNITS:
            for outcome in profile['outcomes']:
                name = spec['id'] + '/' + str(index).zfill(6) + '/' + unit + '/' + str(outcome)
                case = c.run_history(profile, schedule, unit, outcome, name, counter)
                target = output / (str(len(results)).zfill(6) + '.json.gz')
                raw = json.dumps(c.codec.pack(c.artifact.encode(case)), sort_keys=True, separators=(',', ':')).encode()
                target.write_bytes(gzip.compress(raw, compresslevel=6, mtime=0))
                restored = decode(target)
                c.d.require(c.d.exact(case, restored) and c.d.exact(c.audit_case(restored), case['prefixes']), 'exact typed retained replay at every prefix')
                summary = c.summarize(case)
                summary.update(artifact=target.name, artifact_sha256=sha(target), unit=unit, outcome=outcome, global_schedule_index=index)
                summary['observed'] = facts(case, spec)
                results.append(summary)
                if sample is None: sample = case
        if completed % 20 == 0: print(json.dumps(dict(shard=key, completed_schedules=completed, total_schedules=120, visits=counter.visits)), flush=True)
    c.d.require(counter.visits == expected and len(results) == 240, 'complete finite shard')
    controls = replay_controls(profile, schedules, sample)
    c.d.require(c.d.digest(c.d.s.PROFILES) == original, 'original profiles unchanged')
    result = dict(status='COMPLETE_DECLARED_SHARD', packet=spec['id'], domain=spec['domain'], shard_key=key,
                  schedules=120, environments=len(results), state_visits_per_representation=counter.visits,
                  reservation=limit, whole_profile_sha256=c.d.digest(profile), whole_inventory_sha256=c.d.digest(whole),
                  shard_inventory_sha256=c.d.digest(schedules), controls=controls, cases=results,
                  registered_local_modules=sorted(set(modules) | set(source_modules())))
    write(output / 'result.json', result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','controls')}), flush=True)

def partition_check(expected, rows, spec):
    keys = [r['shard_key'] for r in rows]
    c.d.require(keys == spec['shard_keys'] and len(set(keys)) == 6, 'complete ordered unique shard inventory')
    actual = []
    for row in rows:
        cases = row['cases']
        ids = {(x['global_schedule_index'], x['unit'], x['outcome']) for x in cases}
        c.d.require(len(ids) == len(cases) == 240, 'unique full shard environment inventory')
        for case in cases:
            index = case['global_schedule_index']
            c.d.require(type(index) is int and 0 <= index < len(expected) and tuple(case['schedule']) == expected[index], 'exact original global schedule/index')
            c.d.require(case['schedule'][spec['prefix_actions']] == row['shard_key'], 'actual shard membership')
            c.d.require(case['case'] == spec['id'] + '/' + str(index).zfill(6) + '/' + case['unit'] + '/' + str(case['outcome']), 'global unique case identity')
            actual.append((index, case['unit'], case['outcome']))
    wanted = {(i,u,o) for i in range(len(expected)) for u in spec['units'] for o in spec['outcomes']}
    c.d.require(len(actual) == len(set(actual)) == spec['environments'] and set(actual) == wanted, 'complete disjoint exhaustive union of every declared environment')

def certificate_summary(summary,case,profile,spec,artifact_hash):
    c.d.require(case['case'] == summary['case'] and case['unit'] == summary['unit'] and case['outcome'] == summary['outcome'], 'actual typed certificate environment identity')
    c.d.require(tuple(case['source']['actions']) == tuple(summary['schedule']) and c.d.exact(case['source']['profile'],profile), 'actual typed certificate original schedule/profile')
    c.d.require(c.d.exact(c.audit_case(case),case['prefixes']), 'every retained certificate independently re-audited without model reducers')
    actual = c.summarize(case)
    actual.update(artifact=summary['artifact'],artifact_sha256=artifact_hash,unit=case['unit'],outcome=case['outcome'],
                  global_schedule_index=summary['global_schedule_index'],observed=facts(case,spec))
    c.d.require(json.loads(json.dumps(actual)) == summary, 'every JSON summary, observation and minimum bound to actual typed evidence')

def audit_shard(spec,key,output):
    modules = source_modules()
    profile,whole = declared(spec)
    c.d.require(key in spec['shard_keys'] and not (output/'audit.json').exists(), 'new retained audit of declared shard')
    path = output/'result.json'; row = read(path)
    result_hash = sha(path)
    c.d.require(row['status']=='COMPLETE_DECLARED_SHARD' and row['packet']==spec['id'] and row['shard_key']==key, 'completed exact shard to audit')
    c.d.require(len(row['cases'])==240, 'bounded retained audit domain')
    files = {}
    for index,summary in enumerate(row['cases']):
        target = (output/summary['artifact']).resolve()
        c.d.require(summary['artifact']==str(index).zfill(6)+'.json.gz' and target.is_relative_to(output.resolve()) and summary['artifact'] not in files and sha(target)==summary['artifact_sha256'], 'unique contained actual certificate')
        case = decode(target)
        certificate_summary(summary,case,profile,spec,sha(target))
        i = summary['global_schedule_index']
        c.d.require(type(i) is int and 0<=i<len(whole) and tuple(summary['schedule'])==whole[i] and whole[i][spec['prefix_actions']]==key, 'actual original shard membership')
        files[summary['artifact']] = sha(target)
        if (index+1)%40==0: print(json.dumps(dict(retained_histories_audited=index+1,total_histories=240,shard=key)),flush=True)
    c.d.require({p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()} == {'result.json'}|set(files), 'exact completed shard artifact membership')
    c.d.require(sha(path)==result_hash, 'retained shard result unchanged through audit')
    write(output/'audit.json',dict(status='COMPLETE_RETAINED_SHARD_AUDIT',packet=spec['id'],shard_key=key,shard_result_sha256=result_hash,
          certificates=files,environments=240,model_reducers_executed=False,checker_sha256=sha(Path(__file__)),
          registered_local_modules=sorted(set(modules)|set(source_modules()))))
    print('COMPLETE_RETAINED_SHARD_AUDIT',flush=True)

def union(spec, output):
    c.d.require(not (output/'result.json').exists(), 'new union evidence; completed result cannot be overwritten')
    modules = source_modules()
    profile, whole = declared(spec)
    rows, bindings, audits = [], [], []
    for index, key in enumerate(spec['shard_keys']):
        path = output / ('shard-' + str(index)) / 'result.json'
        row = read(path)
        c.d.require(row['status'] == 'COMPLETE_DECLARED_SHARD' and row['packet'] == spec['id'] and row['shard_key'] == key, 'successful exact shard result')
        c.d.require(row['whole_profile_sha256'] == c.d.digest(profile) and row['whole_inventory_sha256'] == c.d.digest(whole), 'same original profile and exhaustive schedule inventory')
        c.d.require(row['state_visits_per_representation'] == row['reservation'] == spec['visits_per_shard'], 'exact shard visits')
        selected = tuple(s for s in whole if s[spec['prefix_actions']] == key)
        c.d.require(row['schedules'] == len(selected) == 120 and row['environments'] == 240 and row['shard_inventory_sha256'] == c.d.digest(selected), 'independent exact shard inventory hash and cardinality')
        c.d.require([x['control'] for x in row['controls']] == COMMON and all(x['detected'] for x in row['controls']), 'all declared shard controls detected')
        audit_path = path.parent/'audit.json'; retained = read(audit_path)
        c.d.require(retained['status']=='COMPLETE_RETAINED_SHARD_AUDIT' and retained['packet']==spec['id'] and retained['shard_key']==key
                    and retained['shard_result_sha256']==sha(path) and retained['environments']==240 and retained['model_reducers_executed'] is False
                    and retained['checker_sha256']==sha(Path(__file__)), 'actual separately owned retained shard audit binding')
        c.d.require(set(retained['certificates'])=={x['artifact'] for x in row['cases']}, 'complete retained audit certificate inventory')
        rows.append(row); audits.append(retained)
        bindings.append(dict(path=path.relative_to(output).as_posix(),sha256=sha(path),audit_path=audit_path.relative_to(output).as_posix(),audit_sha256=sha(audit_path)))
    partition_check(whole, rows, spec)
    controls = []
    rejection(controls, 'missing-shard', lambda: partition_check(whole, rows[:-1], spec))
    rejection(controls, 'duplicate-shard', lambda: partition_check(whole, rows[:-1] + rows[:1], spec))
    bad = copy.deepcopy(rows); bad[0]['cases'][0] = copy.deepcopy(rows[1]['cases'][0])
    rejection(controls, 'cross-shard-environment', lambda: partition_check(whole, bad, spec))
    results = []
    for shard_index, row in enumerate(rows):
        for summary in row['cases']:
            target = (output / ('shard-' + str(shard_index)) / summary['artifact']).resolve()
            c.d.require(target.is_relative_to((output/('shard-'+str(shard_index))).resolve()) and sha(target) == summary['artifact_sha256'], 'expected shard-contained retained certificate hash')
            c.d.require(audits[shard_index]['certificates'][summary['artifact']]==sha(target), 'every actual certificate bound by completed retained shard audit')
            item = dict(summary, artifact=target.relative_to(output).as_posix())
            results.append(item)
        print(json.dumps(dict(retained_shard_audits_bound=shard_index+1,retained_histories_bound=len(results))),flush=True)
    results.sort(key=lambda x:(x['global_schedule_index'], spec['units'].index(x['unit']), spec['outcomes'].index(x['outcome'])))
    original_summary = rows[-1]['cases'][-1]
    original_case = decode(output/'shard-5'/original_summary['artifact'])
    damaged = copy.deepcopy(original_summary); damaged['observed']['incarnation_pairs'] += 1
    rejection(controls,'altered-non-witness-summary',lambda:certificate_summary(damaged,original_case,profile,spec,original_summary['artifact_sha256']))
    other_summary = rows[-1]['cases'][-2]
    other_case = decode(output/'shard-5'/other_summary['artifact'])
    rejection(controls,'cross-environment-certificate',lambda:certificate_summary(original_summary,other_case,profile,spec,original_summary['artifact_sha256']))
    def witness(predicate):
        summary = next((x for x in results if predicate(x)), None)
        c.d.require(summary is not None, 'required nonvacuous complete-domain control witness')
        case = decode(output / summary['artifact'])
        c.d.require(c.d.exact(c.audit_case(case),case['prefixes']) and facts(case,spec) == summary['observed'], 'selected retained control witness audited without model transitions')
        return case
    if spec['domain'] == 'source-collection-race':
        case = witness(lambda x:x['observed']['incarnation_pairs'] == 0)
        damaged = copy.deepcopy(case)
        token = c.t.restore(case['source'])[-1]['source_generation']
        damaged['incarnation_pairs'].append(dict(source=token,target=token,reason='fabricated',source_event=0,target_event=0))
        rejection(controls,'fabricated-pair-in-empty-ledger',lambda:c.audit_case(damaged))
        case = witness(lambda x:True)
        states = c.t.restore(case['source']); index = case['source']['actions'].index('collect-open@11')
        bad = copy.deepcopy(states[index+1]); capture = bad['collection']
        c.d.require(bool(capture), 'successful original collection-open witness')
        bad['collection'] = (capture[0],capture[1]+1,*capture[2:])
        rejection(controls,'corrupted-successful-capture',lambda:c.t.sc.check(states[index],'collect-open@11',bad,profile,case['unit'],case['outcome']))
        case = witness(lambda x:x['observed']['chronological_index_witness'])
        damaged = copy.deepcopy(case)
        index = next(i for i,a in enumerate(case['source']['actions']) if i != int(a.rsplit('@',1)[1]))
        damaged['rows'][index]['index'] = int(case['source']['actions'][index].rsplit('@',1)[1])
        rejection(controls,'occurrence-suffix-used-as-row-index',lambda:c.audit_case(damaged))
    else:
        case = witness(lambda x:x['observed']['restart_chronological_index'] != 22)
        damaged = copy.deepcopy(case)
        pair = next((x for x in damaged['incarnation_pairs'] if x['reason']=='paired-restart'),None)
        c.d.require(pair is not None and pair['source_event'] != 22, 'actual shifted restart causal witness')
        pair['source_event'] = 22
        rejection(controls,'occurrence-suffix-used-as-restart-index',lambda:c.audit_case(damaged))
        case = witness(lambda x:x['observed']['publication_decision'] == 'pub-commit:source-boundary-stale')
        states = c.t.restore(case['source']); index = case['source']['actions'].index('pub-commit@19')
        bad = copy.deepcopy(states[index+1]); bad['decision'] = 'pub-commit:ok'
        rejection(controls,'stale-source-refusal-changed-to-success',lambda:c.t.sc.check(states[index],'pub-commit@19',bad,profile,case['unit'],case['outcome']))
        case = witness(lambda x:x['observed']['append_decision'] == 'append:later-start-only:3:normal:ok')
        states = c.t.restore(case['source']); index = case['source']['actions'].index('append:later-start-only:3:normal@21')
        bad = copy.deepcopy(states[index+1]); bad['append_reply'] = ('forged-reply',)
        rejection(controls,'successful-append-reply-corrupted',lambda:c.t.sc.check(states[index],'append:later-start-only:3:normal@21',bad,profile,case['unit'],case['outcome']))
    c.d.require([x['control'] for x in controls] == spec['required_union_controls'] and spec['required_shard_controls'] == COMMON, 'all preregistered union and shard controls')
    census = {}
    for unit in spec['units']:
        cases = [x for x in results if x['unit']==unit]
        unit_counts = {}
        for case in cases:
            for key,value in case['observed'].items():
                counts = unit_counts.setdefault(key,{})
                label = json.dumps(value,sort_keys=True,separators=(',',':'))
                counts[label] = counts.get(label,0) + 1
        census[unit] = unit_counts
    best = {'strict':None,'extended':None}
    for item in results:
        for kind in best:
            prefix = item[kind + '_first_gap']
            if prefix is not None and (best[kind] is None or prefix < best[kind]['prefix']):
                best[kind] = dict(case=item['case'],prefix=prefix,artifact=item['artifact'],prefix_actions=item['schedule'][:prefix],
                                  minimality='earliest failing prefix across all completed histories in this declared domain')
    result = dict(packet=spec['id'],domain=spec['domain'],status='COMPLETE_DECLARED_FINITE_DOMAIN',
                  schedules=len(whole),environments=len(results),state_visits_per_representation=sum(x['state_visits_per_representation'] for x in rows),
                  reservation=spec['reservation'],domain_profile_sha256=c.d.digest(profile),schedule_inventory_sha256=c.d.digest(whole),
                  registered_local_modules=sorted(set(modules)|set(source_modules())),shard_results=bindings,
                  controls=controls,shard_controls_per_shard=len(COMMON),cases=results,minimized_prefixes=best,observed_census_by_unit=census,
                  strict_complete=sum(x['strict_complete'] for x in results),extended_complete=sum(x['extended_complete'] for x in results),
                  visible_events=sum(x['visible_events'] for x in results),matching_responses=sum(x['matching_responses'] for x in results),
                  matching_journals=sum(x['matching_journals'] for x in results),identity_poststates=sum(x['identity_poststates'] for x in results),
                  original_Q_profile_reachability_proved=False,unrestricted_refinement_proved=False,whole_path_composition_proved=False,
                  source_truth_established=False,reductions_used=False,union_model_reducers_executed=False)
    c.d.require(result['state_visits_per_representation']==spec['reservation'], 'complete charged union')
    write(output / 'result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','controls','observed_census_by_unit','minimized_prefixes')}),flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True); parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--shard'); parser.add_argument('--state-limit', type=int); parser.add_argument('--union', action='store_true'); parser.add_argument('--audit-shard')
    args = parser.parse_args()
    def deny(event, arguments):
        if event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
            raise RuntimeError('model network/process operation refused: ' + event)
    sys.addaudithook(deny)
    spec = read(args.spec)
    if args.union:
        c.d.require(args.shard is None and args.state_limit is None and args.audit_shard is None, 'union executes no model exploration')
        union(spec, args.output)
    elif args.audit_shard is not None:
        c.d.require(args.shard is None and args.state_limit is None, 'retained shard audit executes no model exploration')
        audit_shard(spec,args.audit_shard,args.output)
    else: shard(spec, args.shard, args.output, args.state_limit)
