"""An additive relation for original staged objects; never establishes authority."""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-06'))
import adapter_traces as frozen
d, r = frozen.d, frozen.r


def stage(state, side):
    return state['staged'] if side == 'source' else state['core']['staged']


def identical(left, right):
    """Validate each actual retained object, independent of its current authority."""
    return (type(left) is tuple and type(right) is tuple and len(left) == len(right) == 2
            and type(left[0]) is d.q.Envelope and type(right[0]) is d.q.Envelope
            and d.exact(left, right) and r.signed(left[0]) and r.signed(right[0])
            and left[1] == d.q.raw_cut(left[0].cut) and right[1] == d.q.raw_cut(right[0].cut))


def origin(trace, states, prefix):
    d.require(type(prefix) is int and 0 <= prefix < len(states), 'current audited prefix')
    current = stage(states[prefix], trace['side'])
    if not current:
        return None
    for index in range(prefix - 1, -1, -1):
        event = trace['events'][index]
        if not d.exact(stage(states[index + 1], trace['side']), current):
            return None
        if event['action'].split('@')[0] == 'stage' and states[index + 1]['decision'] == 'stage:ok':
            return {'event_index': index, 'action': event['action'],
                    'before_sha256': event['before_sha256'], 'after_sha256': event['after_sha256']}
    return None


def proof(case, source_states, adapter_states, prefix):
    left = origin(case['source'], source_states, prefix)
    right = origin(case['adapter'], adapter_states, prefix)
    if not left or not right or (left['event_index'], left['action']) != (right['event_index'], right['action']):
        return None
    return {'case': case['case'], 'prefix': prefix, 'source_origin': left, 'adapter_origin': right,
            'source_prefix_sha256': d.digest(case['source']['events'][:prefix]),
            'adapter_prefix_sha256': d.digest(case['adapter']['events'][:prefix]),
            'source_state_sha256': d.digest(source_states[prefix]),
            'adapter_state_sha256': d.digest(adapter_states[prefix])}


def compare(case, source_states, adapter_states, prefix, pairs):
    source, adapter = source_states[prefix], adapter_states[prefix]
    saved = copy.deepcopy(pairs)
    common, journal = frozen.related(source, adapter, pairs)
    certificate = proof(case, source_states, adapter_states, prefix)
    alternative = bool(certificate and identical(source['staged'], adapter['core']['staged']))
    differing = [key for key in common if key != 'staged' or not alternative]
    d.require(d.exact(pairs, saved), 'record identity never mutates incarnation bindings')
    return {'prefix': prefix, 'strict_differing_common_fields': common,
            'differing_common_fields': differing, 'differing_journal_fields': journal,
            'strict_related': not (common or journal), 'related': not (differing or journal),
            'staged_rule': 'strict' if 'staged' not in common else 'original-object-identity' if alternative else 'unrelated',
            'identity_proof': certificate if 'staged' in common and alternative else None,
            'pairs_sha256': d.digest(pairs), 'incarnation_pair_established_by_identity': False}
