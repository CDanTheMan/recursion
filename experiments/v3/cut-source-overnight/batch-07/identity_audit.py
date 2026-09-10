"""Separate view-based audit of the additive staged-only relation and its prefixes."""
import hashlib
import hmac
import json
import identity as relation

d, r, frozen = relation.d, relation.r, relation.frozen


def valid_objects(a, b):
    if type(a) is not tuple or type(b) is not tuple or len(a) != 2 or len(b) != 2:
        return False
    if type(a[0]) is not d.q.Envelope or type(b[0]) is not d.q.Envelope or r.typed(a) != r.typed(b):
        return False
    try:
        for envelope, payload in (a, b):
            d.require(r.token(envelope.source_generation), 'typed original source incarnation')
            r.qa.checked_payload(envelope, payload)
            body = json.dumps(tuple(envelope)[:-1], sort_keys=True, separators=(',', ':')).encode()
            d.require(hmac.compare_digest(envelope.signature, hmac.new(d.q.TEST_KEY, body, hashlib.sha256).hexdigest()), 'original own-body signature')
    except (ValueError, KeyError, TypeError, IndexError):
        return False
    return True


def expected_proof(case, states, prefix):
    origins = []
    for side in ('source', 'adapter'):
        trace, sequence = case[side], states[side]
        d.require(type(prefix) is int and 0 <= prefix < len(sequence), 'audit prefix bounds')
        value = sequence[prefix]['staged'] if side == 'source' else sequence[prefix]['core']['staged']
        positions = [i for i in range(prefix) if trace['events'][i]['action'].split('@')[0] == 'stage'
                     and sequence[i + 1]['decision'] == 'stage:ok']
        if not positions or not value:
            return None
        index = positions[-1]
        for position in range(index + 1, prefix + 1):
            actual = sequence[position]['staged'] if side == 'source' else sequence[position]['core']['staged']
            if r.typed(actual) != r.typed(value):
                return None
        event = trace['events'][index]
        d.require(d.digest(sequence[index]) == event['before_sha256'] and d.digest(sequence[index + 1]) == event['after_sha256'], 'actual stage-origin state binding')
        origins.append(dict(event_index=index, action=event['action'], before_sha256=event['before_sha256'], after_sha256=event['after_sha256']))
    if origins[0]['event_index'] != origins[1]['event_index'] or origins[0]['action'] != origins[1]['action']:
        return None
    return dict(case=case['case'], prefix=prefix, source_origin=origins[0], adapter_origin=origins[1],
                source_prefix_sha256=d.digest(case['source']['events'][:prefix]),
                adapter_prefix_sha256=d.digest(case['adapter']['events'][:prefix]),
                source_state_sha256=d.digest(states['source'][prefix]), adapter_state_sha256=d.digest(states['adapter'][prefix]))


def check(row, case, source_states, adapter_states, prefix, pairs):
    source, adapter = source_states[prefix], adapter_states[prefix]
    common = [key for key in r.FIELDS if r.field_view(source, key, 'source', pairs) != r.field_view(adapter['core'], key, 'target', pairs)]
    journal = [key for key in (*d.s.EXTRA, 'source_generation') if r.typed(source[key]) != r.typed(adapter['journal'][key])]
    certificate = expected_proof(case, {'source': source_states, 'adapter': adapter_states}, prefix)
    permit = bool(certificate and valid_objects(source['staged'], adapter['core']['staged']))
    extended = [key for key in common if key != 'staged' or not permit]
    expected = dict(prefix=prefix, strict_differing_common_fields=common, differing_common_fields=extended,
                    differing_journal_fields=journal, strict_related=not (common or journal), related=not (extended or journal),
                    staged_rule='strict' if 'staged' not in common else 'original-object-identity' if permit else 'unrelated',
                    identity_proof=certificate if 'staged' in common and permit else None,
                    pairs_sha256=d.digest(pairs), incarnation_pair_established_by_identity=False)
    d.require(r.typed(row) == r.typed(expected), 'independent staged-only relation and actual prefix certificate')
