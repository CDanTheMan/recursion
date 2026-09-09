"""Exact old graph reproduction and local state-observation correspondence audit."""
import collections
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight'))
import s_domain as s
import s_inclusive as inclusive
import s_split as separated
import s_audit as source_relation
import q_inclusive as target_inclusive
import q_split as target_separated
import q_audit as target_relation
import q_artifact as codec

FIELDS = tuple(s.q.AUTH + s.q.FLOW + s.q.VIEW)
HIDDEN = ('done', 'decision')
VISIBLE = tuple(k for k in FIELDS if k not in HIDDEN)
KINDS = ('same-action', 'stutter', 'gap')


def require(ok, why):
    if not ok:
        raise ValueError(why)


def encoded(value):
    return s.canonical(value).encode()


def sha(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def project(state):
    return {key: state[key] for key in VISIBLE}


def independent_projection(state):
    return {key: value for key, value in state.items() if key not in set(s.EXTRA) | set(HIDDEN)}


def private(action):
    key = action.partition('@')[0]
    return key.startswith(('register:', 'attempt:', 'atomic:', 'append:', 'collect:')) or key in ('append-lose-reply', 'collect-open')


def certificate(before, action, after, target):
    left, right = project(before), project(after)
    exact = target is not None and project(target) == right
    kind = 'same-action' if exact else ('stutter' if left == right else 'gap')
    fields = sorted(k for k in VISIBLE if target is not None and target[k] != after[k])
    return {'kind': kind, 'edge_sha256': sha((before, action, after)), 'before_sha256': sha(before),
            'after_sha256': sha(after), 'target_sha256': sha(target) if target is not None else None,
            'differing_target_fields': fields}


def verify_certificate(row, before, action, after, target, fields=VISIBLE):
    # Independently derive the retained target namespace from the concrete state schema.
    expected_fields = set(before) - set(s.EXTRA) - {'done', 'decision'}
    require(set(fields) == expected_fields and len(fields) == len(expected_fields), 'exact observation namespace')
    left = independent_projection(before); right = independent_projection(after)
    other = independent_projection(target) if target is not None else None
    kind = 'same-action' if other == right else 'stutter' if left == right else 'gap'
    require(row['kind'] == kind, 'mapping category correspondence')
    require(row['before_sha256'] == sha(before) and row['after_sha256'] == sha(after)
            and row['edge_sha256'] == sha((before, action, after)), 'exact mapping edge binding')
    require(row['target_sha256'] == (sha(target) if target is not None else None), 'target response binding')
    require(row['differing_target_fields'] == sorted(k for k in expected_fields if other is not None and other[k] != right[k]), 'complete differing field list')


def coverage(row, original):
    require(row['states'] == original['states'] and row['edges'] == original['edges']
            and row['terminal_states'] == original['terminal_states']
            and row['graph_sha256'] == original['graph_sha256'], 'exact admitted source graph')
    require(sum(row['classification_counts'].values()) == row['edges'], 'every admitted edge classified once')
    require(row['frontier'] == 0 and row['rank_decreases'] == row['edges'] and row['terminal_full_masks'] == row['terminal_states'], 'finite schedule rank evidence')


def run():
    original = codec.unpack(json.loads((ROOT / 'docs/v3/construction/cut-source-overnight-20260908/results.json').read_text()))
    prior_target = codec.unpack(json.loads((ROOT / 'docs/v3/construction/cut-publication-20260908/results.json').read_text()))
    retained_pairs = []
    for unit in s.UNITS:
        source_key = 'pending-success/' + unit + '/1'
        target_key = 'current-success/' + unit + '/1'
        left = next(r for r in original['profiles'][source_key]['trace'] if r['action'].partition('@')[0] == 'source-attest')
        right = next(r for r in prior_target['profiles'][target_key]['trace'] if r['action'].partition('@')[0] == 'source-attest')
        require(project(left['before']) == project(right['before']), 'retained matching observed prestates')
        different = sorted(k for k in VISIBLE if left['after'][k] != right['after'][k])
        require(different == ['source_generation'], 'retained direct-mapping counterexample')
        retained_pairs.append({'source_profile': source_key, 'target_profile': target_key,
                               'source_action': left['action'], 'target_action': right['action'],
                               'source_edge_sha256': sha(left), 'target_edge_sha256': sha(right),
                               'observed_prestate_sha256': sha(project(left['before'])),
                               'differing_fields': different,
                               'source_generation': left['after']['source_generation'],
                               'target_generation': right['after']['source_generation']})
    del prior_target
    require(len(s.PROFILES) == 51 and len(original['profiles']) == 104, 'unchanged original finite domain')
    require(len(FIELDS) == len(set(FIELDS)) and set(HIDDEN) <= set(FIELDS), 'declared projection namespace')
    rows = {}; witnesses = {}; samples = {}; global_count = 0; initialized = 0
    for name, profile in s.PROFILES.items():
        for unit in s.UNITS:
            for outcome in profile['outcomes']:
                key = name + '/' + unit + '/' + str(outcome)
                initial = s.initial(unit)
                source_relation.initialization(initial, unit)
                target_relation.initialization(s.project(initial), unit)
                require(project(initial) == project(s.q.initial(unit)), 'projected initial equality')
                initialized += 1
                queue = collections.deque([(initial, ())]); seen = {s.canonical(initial)}
                digest = hashlib.sha256(); counts = dict.fromkeys(KINDS, 0)
                edges = terminals = rank_steps = full_masks = 0
                while queue:
                    before, prefix = queue.popleft()
                    enabled = set(s.ready_actions(before, profile))
                    require(enabled == source_relation.enabled(before, profile), 'unchanged complete source enabledness')
                    require(project(before) == independent_projection(before), 'independent state projection')
                    if not enabled:
                        terminals += 1
                        require(before['done'] == (1 << len(profile['actions'])) - 1, 'terminal full schedule mask')
                        full_masks += 1
                    for action in sorted(enabled):
                        after = inclusive.step(before, action, profile, unit, outcome)
                        require(after == s.flatten(separated.step(s.split(before), action, profile, unit, outcome)), 'unchanged independent source reducers')
                        source_relation.check(before, action, after, profile, unit, outcome)
                        require(after['done'].bit_count() == before['done'].bit_count() + 1, 'strict finite schedule rank')
                        rank_steps += 1
                        target = None
                        if not private(action):
                            projected = s.project(before)
                            target = target_inclusive.step(projected, action, profile, unit, outcome)
                            other = s.q.flatten(target_separated.step(s.q.split(projected), action, profile, unit, outcome))
                            require(target == other, 'both unchanged target reducers agree locally')
                            target_relation.check(projected, action, target, profile, unit, outcome)
                        row = certificate(before, action, after, target)
                        verify_certificate(row, before, action, after, target)
                        counts[row['kind']] += 1
                        family = action.partition('@')[0].partition(':')[0]
                        witness_key = row['kind'] + '/' + family + '/' + ','.join(row['differing_target_fields'])
                        if witness_key not in witnesses:
                            witnesses[witness_key] = {'profile': key, 'prefix': prefix, 'action': action,
                                                      'before': before, 'after': after, 'target_after': target,
                                                      'certificate': row}
                        samples.setdefault(row['kind'], (before, action, after, target, row))
                        digest.update(encoded((before, action, after))); edges += 1
                        identity = s.canonical(after)
                        if identity not in seen:
                            seen.add(identity); queue.append((after, prefix + (action,)))
                            require(global_count + len(seen) <= 500000, 'registered cumulative state bound')
                result = {'states': len(seen), 'edges': edges, 'terminal_states': terminals, 'frontier': 0,
                          'graph_sha256': digest.hexdigest(), 'classification_counts': counts,
                          'rank_decreases': rank_steps, 'terminal_full_masks': full_masks}
                coverage(result, original['profiles'][key]); rows[key] = result; global_count += len(seen)
    require(set(rows) == set(original['profiles']) and global_count == 17966
            and sum(x['edges'] for x in rows.values()) == 31140, 'complete exact original graph family')
    require(set(samples) == set(KINDS), 'all mapping outcomes positively attained')
    gap = samples['gap']
    require(gap[1].partition('@')[0] == 'source-attest' and gap[4]['differing_target_fields'] == ['source_generation'], 'retained first-attestation mapping obstruction')
    controls = []
    trials = [('missing-observation-field', dict(gap[4]), tuple(k for k in VISIBLE if k != 'source_generation')),
              ('gap-as-stutter', dict(gap[4], kind='stutter'), VISIBLE),
              ('misbound-edge', dict(gap[4], edge_sha256='0' * 64), VISIBLE)]
    for label, cert, fields in trials:
        try:
            verify_certificate(cert, *gap[:4], fields=fields)
        except ValueError as error:
            controls.append({'control': label, 'detected': True, 'reason': str(error)})
        else:
            raise ValueError('undetected mapping control ' + label)
    key = next(iter(rows)); bad = dict(rows[key]); bad['classification_counts'] = dict(bad['classification_counts'])
    bad['classification_counts']['stutter'] -= 1
    try:
        coverage(bad, original['profiles'][key])
    except ValueError as error:
        controls.append({'control': 'omitted-edge-classification', 'detected': True, 'reason': str(error)})
    else:
        raise ValueError('undetected missing edge')
    return {'status': 'FINITE_LOCAL_MAPPING_AUDIT_PASS_WITH_GAPS', 'profiles': rows,
            'states_per_representation': global_count, 'edges_per_representation': 31140,
            'initializations': initialized, 'hidden_observations': HIDDEN, 'visible_fields': VISIBLE,
            'classification_counts': {k: sum(r['classification_counts'][k] for r in rows.values()) for k in KINDS},
            'witnesses': witnesses, 'retained_cross_model_pairs': retained_pairs,
            'controls': controls, 'complete_direct_refinement': False,
            'target_original_graph_reachability_proved': False, 'response_label_equivalence_proved': False,
            'fairness_transfer_proved': False, 'finite_source_schedule_rank_checked': True,
            'source_truth_established': False, 'deferred_questions_resolved': []}
