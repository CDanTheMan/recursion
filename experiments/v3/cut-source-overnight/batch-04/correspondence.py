"""Response-visible local correspondence on the unchanged complete S graph family."""
import ast
import collections
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
DOC = ROOT / 'docs/v3/construction/cut-source-overnight-20260908/batch-04'
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight'))
import s_domain as s
import s_inclusive as source_a
import s_split as source_b
import s_audit as source_check
import q_inclusive as target_a
import q_split as target_b
import q_audit as target_check
import q_artifact as codec

VARIANTS = ('identity', 'first-attestation-floor')
FIELDS = tuple(s.q.AUTH + s.q.FLOW + s.q.VIEW)
STATE_FIELDS = tuple(k for k in FIELDS if k not in ('done', 'decision'))
KINDS = ('matching-step', 'state-gap', 'response-gap', 'state-and-response-gap', 'unmapped-operation')

def require(ok, message):
    if not ok: raise ValueError(message)
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def encoded(x): return s.canonical(x).encode()
def digest(x): return hashlib.sha256(encoded(x)).hexdigest()

def projection(state, variant):
    require(variant in VARIANTS, 'declared relation variant')
    result = {k: state[k] for k in FIELDS}
    if variant == 'first-attestation-floor' and state['source_name']:
        token = state['source_generation']
        result['source_generation'] = token[:-1] + (max(1, token[-1]),)
    return result

def verify_projection(state, variant, result):
    require(set(result) == set(FIELDS), 'complete target state namespace')
    for key in FIELDS:
        expected = state[key]
        if key == 'source_generation' and variant == 'first-attestation-floor':
            expected = ('cut-source', 'collectorA', 'effectA',
                        1 if state['source_name'] and state[key][3] == 0 else state[key][3])
        require(result[key] == expected, 'projection field: ' + key)
    require(result['source_generation'][:3] == state['source_generation'][:3], 'generation namespace retained')

def source_only(action):
    verb = action.partition('@')[0]
    return verb.startswith(('register:', 'attempt:', 'atomic:', 'append:', 'collect:')) or verb in ('append-lose-reply', 'collect-open')

def observe(state): return {key: state[key] for key in STATE_FIELDS}

def response(state, action):
    # All modeled action labels are observable. Source-only replies have no Q counterpart.
    result = {'decision': state['decision']}
    if action.partition('@')[0].startswith('append:') or action.partition('@')[0] == 'append-lose-reply':
        result['append_reply'] = state['append_reply']
    return result

def certificate(before, action, after, target, variant):
    projected = projection(after, variant)
    state_fields = [] if target is None else sorted(k for k in STATE_FIELDS if projected[k] != target[k])
    same_response = target is not None and response(after, action) == response(target, action)
    kind = ('unmapped-operation' if target is None else
            'state-and-response-gap' if state_fields and not same_response else
            'state-gap' if state_fields else 'response-gap' if not same_response else 'matching-step')
    return {'variant': variant, 'kind': kind, 'edge_sha256': digest((before, action, after)),
            'target_prestate_sha256': digest(projection(before, variant)),
            'target_sha256': digest(target) if target is not None else None,
            'differing_state_fields': state_fields, 'source_response': response(after, action),
            'target_response': response(target, action) if target is not None else None}

def verify_certificate(row, before, action, after, target, variant):
    expected_namespace = set(before) - set(s.EXTRA) - {'done', 'decision'}
    require(expected_namespace == set(STATE_FIELDS), 'complete observable state inventory')
    source_view = projection(after, variant)
    verify_projection(after, variant, source_view)
    require((target is None) == source_only(action), 'explicit action translation domain')
    source_response = {'decision': after['decision']}
    if action.split('@')[0].startswith('append:') or action.split('@')[0] == 'append-lose-reply':
        source_response['append_reply'] = after['append_reply']
    target_response = None if target is None else {'decision': target['decision']}
    different = [] if target is None else sorted(k for k in expected_namespace if source_view[k] != target[k])
    if target is None: kind = 'unmapped-operation'
    else:
        equal_state, equal_response = not different, source_response == target_response
        kind = {(True, True): 'matching-step', (False, True): 'state-gap',
                (True, False): 'response-gap', (False, False): 'state-and-response-gap'}[(equal_state, equal_response)]
    require(row == {'variant':variant, 'kind':kind, 'edge_sha256':digest((before, action, after)),
                    'target_prestate_sha256':digest(projection(before, variant)),
                    'target_sha256':None if target is None else digest(target),
                    'differing_state_fields':different, 'source_response':source_response,
                    'target_response':target_response}, 'independent state/response certificate')

def check_coverage(row, expected):
    for field in ('states','edges','terminal_states','graph_sha256'):
        require(row[field] == expected[field], 'unchanged source graph: ' + field)
    require(row['frontier'] == 0 and row['rank_decreases'] == row['edges'], 'complete finite scheduled graph')
    for counts in row['classifications'].values():
        require(set(counts) == set(KINDS) and sum(counts.values()) == row['edges'], 'disjoint complete edge classification')

def barrier(first, stage):
    return {'scope':'retained-two-step-generation-only-same-action-exact-other-fields',
            'profile':first['profile'], 'actions':[first['action'],stage['action']],
            'source_middle_sha256':digest(first['after']),
            'source_edges':[digest((x['before'],x['action'],x['after'])) for x in (first,stage)],
            'target_attestation_sha256':digest(first['target_after']),
            'target_stage_sha256':digest(stage['target_after']),
            'exact_staged_object_required':True, 'single_shared_middle_state_required':True,
            'necessary_middle_generations':[first['target_after']['source_generation'], stage['after']['staged'][0].source_generation],
            'satisfiable':False}

def verify_barrier(row, first, stage):
    for ref in read(DOC/'contract.json')['barrier_function_anchors']:
        source = (ROOT/ref['path']).read_text(encoding='utf-8')
        node = next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name==ref['function'])
        snippet = '\n'.join(source.splitlines()[node.lineno-1:node.end_lineno])
        require(node.lineno==ref['line'] and hashlib.sha256(snippet.encode()).hexdigest()==ref['function_sha256'], 'exact barrier function anchor')
    require(first['after'] == stage['before'] and tuple(stage['prefix']) == tuple(first['prefix'])+(first['action'],), 'consecutive retained source edges')
    require(first['profile']==stage['profile'] and first['profile'].startswith('pending-success/'), 'same retained profile')
    require(first['action'].partition('@')[0] == 'source-attest' and stage['action'].partition('@')[0] == 'stage', 'exact retained action sequence')
    require(first['before']['source_name'] == '' and first['before']['cut_delivery'] == 'success'
            and first['before']['remote'] == 1, 'first successful attestation guards')
    require(s.q.lit.fixture('success')['binding']['body']['reservation'] == list(first['before']['bindings'][0]), 'valid retained reservation guard')
    require(first['certificate']['kind'] == 'matching-step' and first['certificate']['variant'] == 'first-attestation-floor', 'retained matching attestation endpoint')
    require(first['target_after'] == projection(stage['before'],'first-attestation-floor'), 'single concrete target intermediate state')
    require(first['after']['decision']=='source-attest:ok' and first['target_after']['decision']=='source-attest:ok'
            and stage['after']['decision']=='stage:ok' and stage['target_after']['decision']=='stage:ok', 'successful observable responses at both steps')
    required_by_attestation = first['target_after']['source_generation']
    required_by_exact_stage = stage['after']['staged'][0].source_generation
    require(required_by_attestation == ('cut-source','collectorA','effectA',1)
            and required_by_exact_stage == ('cut-source','collectorA','effectA',0), 'contradictory necessary middle generations')
    require(stage['target_after']['staged'][0].source_generation == required_by_attestation, 'Q stage carries the shared middle generation')
    target_check.checked_payload(*stage['after']['staged'])
    target_check.checked_payload(*stage['target_after']['staged'])
    expected = {'scope':'retained-two-step-generation-only-same-action-exact-other-fields',
                    'profile':stage['profile'],'actions':[first['action'],stage['action']],
                    'source_middle_sha256':digest(stage['before']),
                    'source_edges':[digest((first['before'],first['action'],first['after'])),digest((stage['before'],stage['action'],stage['after']))],
                    'target_attestation_sha256':digest(first['target_after']),
                    'target_stage_sha256':digest(stage['target_after']),
                    'exact_staged_object_required':True,'single_shared_middle_state_required':True,
                    'necessary_middle_generations':[required_by_attestation,required_by_exact_stage],
                    'satisfiable':False}
    require(encoded(row)==encoded(expected), 'independent retained two-step contradiction certificate')

def run():
    contract = read(DOC/'contract.json')
    require(contract['variants'] == list(VARIANTS) and contract['hidden_actions'] == []
            and contract['observe_all_decisions'] and contract['preserve_signed_objects'], 'fixed observation and relation contract')
    old = codec.unpack(read(ROOT/'docs/v3/construction/cut-source-overnight-20260908/results.json'))
    require(len(s.PROFILES) == 51 and len(old['profiles']) == 104, 'original profile domain')
    profiles, witnesses, samples, initialization = {}, {}, {}, 0
    required_examples = {}
    required_cases = {'pending-success':('source-attest','stage','pub-commit','reconcile'),
                      'collection-old-incarnation':('source-restart',), 'omitted-record':('source-attest',),
                      'fresh-conflict-retry-stale-source':('pub-retry-conflict',),
                      'publication-duplicate-retired':('pub-retry',)}
    total = 0
    baseline = dict.fromkeys(('same-action','stutter','gap'), 0)
    for name, profile in s.PROFILES.items():
        for unit in s.UNITS:
            for outcome in profile['outcomes']:
                key = name+'/'+unit+'/'+str(outcome)
                initial = s.initial(unit)
                source_check.initialization(initial, unit)
                for variant in VARIANTS:
                    projected = projection(initial, variant)
                    verify_projection(initial, variant, projected)
                    target_check.initialization(projected, unit)
                    require(observe(projected) == observe(s.q.initial(unit)), 'initial relation')
                initialization += 1
                queue = collections.deque([(initial, ())]); seen = {s.canonical(initial)}
                graph = hashlib.sha256(); edges = terminals = 0
                counts = {v:dict.fromkeys(KINDS, 0) for v in VARIANTS}
                while queue:
                    before, prefix = queue.popleft()
                    enabled = set(s.ready_actions(before, profile))
                    require(enabled == source_check.enabled(before, profile), 'source complete enabledness')
                    if not enabled:
                        terminals += 1
                        require(before['done'] == (1 << len(profile['actions']))-1, 'full terminal mask')
                    for action in sorted(enabled):
                        after = source_a.step(before, action, profile, unit, outcome)
                        require(after == s.flatten(source_b.step(s.split(before), action, profile, unit, outcome)), 'both original source reducers')
                        source_check.check(before, action, after, profile, unit, outcome)
                        require(after['done'].bit_count() == before['done'].bit_count()+1, 'finite schedule rank')
                        for variant in VARIANTS:
                            pre = projection(before, variant)
                            verify_projection(before, variant, pre)
                            target = None
                            if not source_only(action):
                                target_check.invariant(pre)
                                target = target_a.step(pre, action, profile, unit, outcome)
                                require(target == s.q.flatten(target_b.step(s.q.split(pre), action, profile, unit, outcome)), 'both original target reducers')
                                target_check.check(pre, action, target, profile, unit, outcome)
                            cert = certificate(before, action, after, target, variant)
                            verify_certificate(cert, before, action, after, target, variant)
                            counts[variant][cert['kind']] += 1
                            if variant == 'identity':
                                category = 'same-action' if target is not None and observe(target) == observe(s.project(after)) else 'stutter' if observe(s.project(before)) == observe(s.project(after)) else 'gap'
                                baseline[category] += 1
                            family = action.partition('@')[0].partition(':')[0]
                            signature = '/'.join((variant, cert['kind'], family, ','.join(cert['differing_state_fields'])))
                            if signature not in witnesses:
                                witnesses[signature] = {'profile':key, 'prefix':prefix, 'action':action,
                                    'before':before, 'after':after, 'target_after':target, 'certificate':cert}
                            if family in required_cases.get(name, ()):
                                example_key = '/'.join((key, variant, family))
                                required_examples.setdefault(example_key, {'profile':key, 'prefix':prefix, 'action':action,
                                    'before':before, 'after':after, 'target_after':target, 'certificate':cert})
                            samples.setdefault(cert['kind'], (before, action, after, target, variant, cert))
                        graph.update(encoded((before, action, after))); edges += 1
                        identity = s.canonical(after)
                        if identity not in seen:
                            seen.add(identity); queue.append((after, prefix+(action,)))
                            require(total+len(seen) <= 17966, 'exact per-invocation reserved source ceiling')
                row = {'states':len(seen), 'edges':edges, 'terminal_states':terminals,
                       'graph_sha256':graph.hexdigest(), 'frontier':0, 'rank_decreases':edges, 'classifications':counts}
                check_coverage(row, old['profiles'][key]); profiles[key] = row; total += len(seen)
    require(set(profiles) == set(old['profiles']) and total == 17966 and sum(r['edges'] for r in profiles.values()) == 31140, 'exact original graph family coverage')
    require(baseline == {'same-action':10292, 'stutter':20794, 'gap':54}, 'unchanged Batch03 baseline classification')
    barriers = {}
    for unit in s.UNITS:
        first = required_examples['pending-success/'+unit+'/1/first-attestation-floor/source-attest']
        require(first['certificate']['kind'] == 'matching-step', 'retained first-attestation endpoint matches under lift')
        restart = required_examples['collection-old-incarnation/'+unit+'/1/first-attestation-floor/source-restart']
        require(restart['certificate']['kind'] == 'state-gap' and restart['certificate']['differing_state_fields'] == ['source_generation'], 'retained lifted restart obstruction')
        stage = required_examples['pending-success/'+unit+'/1/first-attestation-floor/stage']
        require('staged' in stage['certificate']['differing_state_fields'], 'retained signed-envelope obstruction')
        omitted = required_examples['omitted-record/'+unit+'/1/identity/source-attest']
        require(omitted['certificate']['source_response'] != omitted['certificate']['target_response'], 'retained response obstruction')
        barriers[unit] = barrier(first,stage)
        verify_barrier(barriers[unit],first,stage)
    controls = []
    def reject(label, fn):
        try: fn()
        except ValueError as error: controls.append({'control':label, 'detected':True, 'reason':str(error)})
        else: raise ValueError('undetected certificate control: '+label)
    require('unmapped-operation' in samples and 'matching-step' in samples, 'positive action-domain controls')
    example = next(w for w in witnesses.values() if w['certificate']['variant']=='first-attestation-floor' and w['certificate']['kind'] != 'matching-step' and not source_only(w['action']))
    before, action, after, target = (example[k] for k in ('before','action','after','target_after'))
    variant = 'first-attestation-floor'; cert = example['certificate']
    bad = copy.deepcopy(cert); bad['kind'] = 'matching-step'
    reject('gap-promoted-to-match', lambda:verify_certificate(bad,before,action,after,target,variant))
    bad2 = copy.deepcopy(cert); bad2['source_response'] = {}
    reject('hidden-response', lambda:verify_certificate(bad2,before,action,after,target,variant))
    bad3 = copy.deepcopy(cert); bad3['edge_sha256'] = '0'*64
    reject('misbound-edge', lambda:verify_certificate(bad3,before,action,after,target,variant))
    projected = projection(after, variant); del projected['source_generation']
    reject('omitted-generation', lambda:verify_projection(after,variant,projected))
    projected2 = projection(after, variant); projected2['source_generation'] = ('foreign',)+projected2['source_generation'][1:]
    reject('renamed-generation-namespace', lambda:verify_projection(after,variant,projected2))
    stage_after = stage['after']; projected3 = projection(stage_after, variant); projected3['staged'] = ()
    reject('changed-signed-envelope', lambda:verify_projection(stage_after,variant,projected3))
    bad4 = copy.deepcopy(cert); bad4['target_prestate_sha256'] = '0'*64
    reject('misbound-target-prestate', lambda:verify_certificate(bad4,before,action,after,target,variant))
    entry = next(iter(profiles)); incomplete = copy.deepcopy(profiles[entry]); incomplete['classifications']['identity']['unmapped-operation'] -= 1
    reject('omitted-classification', lambda:check_coverage(incomplete,old['profiles'][entry]))
    x = samples['unmapped-operation']; misclassified = copy.deepcopy(x[5]); misclassified['kind'] = 'matching-step'
    reject('source-only-operation-hidden', lambda:verify_certificate(misclassified,*x[:5]))
    proof = barriers[unit]
    bad_proof = copy.deepcopy(proof); bad_proof['necessary_middle_generations'][1] = bad_proof['necessary_middle_generations'][0]
    reject('erased-generation-contradiction', lambda:verify_barrier(bad_proof,first,stage))
    bad_proof2 = copy.deepcopy(proof); bad_proof2['exact_staged_object_required'] = False
    reject('erased-exact-staged-premise', lambda:verify_barrier(bad_proof2,first,stage))
    bad_proof3 = copy.deepcopy(proof); bad_proof3['source_middle_sha256'] = '0'*64
    reject('misbound-shared-middle-state', lambda:verify_barrier(bad_proof3,first,stage))
    return {'status':'RESPONSE_VISIBLE_LOCAL_COMPARISON_COMPLETE', 'states_per_representation':total,
            'edges_per_representation':31140, 'initializations':initialization, 'profiles':profiles,
            'classifications':{v:{k:sum(r['classifications'][v][k] for r in profiles.values()) for k in KINDS} for v in VARIANTS},
            'witnesses':witnesses, 'required_examples':required_examples, 'two_step_obstructions':barriers,
            'controls':controls, 'baseline_classifications':baseline,
            'observable_state_fields':STATE_FIELDS, 'observable_transition_decision':True, 'hidden_actions':[],
            'target_original_graph_reachability_proved':False, 'whole_path_composition_proved':False,
            'generation_relation_proved':False, 'response_equivalence_proved':False,
            'fairness_transfer_proved':False, 'source_truth_established':False, 'deferred_questions_resolved':[]}
