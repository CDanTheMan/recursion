"""Bounded retained-certificate control for o15-stage-identity.

Scope: the additive staged disjunct excuses a strict 'staged' difference only
for typed-identical, individually valid originals (Envelope + payload bound to
its named cut + own-body HMAC + typed incarnation) whose shared incarnation no
active pair binds at that prefix, with one audited shared stage-origin event;
identity never creates pairs or authority. Anchors (unchanged originals,
representation only): identity.py origin/identical/compare, identity_audit.py
valid_objects/expected_proof, semantic.py typed/exact/digest/token/signed,
adapter_traces.py gap_certificate, q_domain/q_audit Envelope/raw_cut/
checked_payload. charge.take(1) before EVERY inspected prefix; witnesses bound
to KEEP; a missing reachable 'original-object-identity' witness stays a
limitation. No reducers/models, boundary helpers, or network; JSON-safe only.
"""
import copy, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as r

q = r.q
KEEP = 25
STRICT, IDENTITY, UNRELATED = 'strict', 'original-object-identity', 'unrelated'


def _views(trace):
    staged, decision, out = (), 'initial', [((), 'initial')]
    for event in trace['events']:
        patch = event['patch']
        body = patch.get('core', {}) if trace['side'] == 'adapter' else patch
        if 'staged' in body: staged = body['staged']
        if 'decision' in patch: decision = patch['decision']
        out.append((staged, decision))
    return out


def _obj(value, bound_payload=True):
    if type(value) is not tuple or len(value) != 2 or type(value[0]) is not q.Envelope:
        return None
    env = value[0]
    if not r.signed(env): return None
    return env if not bound_payload or value[1] == q.raw_cut(env.cut) else None


def _strict_ok(left, right, active):
    if not left and not right: return True
    le, re_ = _obj(left, False), _obj(right, False)
    if le is None or re_ is None or not r.exact(left[1], right[1]): return False
    bound = any(r.exact(p['source'], le.source_generation)
                and r.exact(p['target'], re_.source_generation) for p in active)
    rest = all(r.exact(getattr(le, k), getattr(re_, k)) for k in q.Envelope._fields
               if k not in ('source_generation', 'signature'))
    return bound and rest


def _origin(trace, views, prefix):
    current = views[prefix][0]
    if not current: return None
    for index in range(prefix - 1, -1, -1):
        if not r.exact(views[index + 1][0], current): return None
        event = trace['events'][index]
        if event['action'].split('@')[0] == 'stage' and views[index + 1][1] == 'stage:ok':
            return {'event_index': index, 'action': event['action'],
                    'before_sha256': event['before_sha256'], 'after_sha256': event['after_sha256']}
    return None


def _inspect(case, row, views_s, views_a, pairs):
    prefix = row['prefix']
    active = [p for p in pairs if p['source_event'] < prefix and p['target_event'] < prefix]
    left, right = views_s[prefix][0], views_a[prefix][0]
    bad = []
    if r.digest(active) != row['pairs_sha256']: bad.append('active-pair-ledger-digest-differs')
    if row['incarnation_pair_established_by_identity']: bad.append('identity-claimed-authority')
    strict = _strict_ok(left, right, active)
    if strict == ('staged' in row['strict_differing_common_fields']):
        bad.append('strict-staged-membership-disagrees-with-retained-objects')
    origin_s = _origin(case['source'], views_s, prefix)
    origin_a = _origin(case['adapter'], views_a, prefix)
    shared = bool(origin_s and origin_a and (origin_s['event_index'], origin_s['action'])
                  == (origin_a['event_index'], origin_a['action']))
    valid = bool(_obj(left) and _obj(right) and r.exact(left, right))
    expected = STRICT if strict else IDENTITY if valid and shared else UNRELATED
    if row['staged_rule'] != expected:
        bad.append('staged-rule-' + str(row['staged_rule']) + '-recomputed-' + expected)
    witness = None
    if row['staged_rule'] == IDENTITY:
        env = _obj(left)
        if not (valid and shared):
            bad.append('accepted-without-identical-valid-shared-origin')
        elif any(r.exact(p['source'], env.source_generation)
                 or r.exact(p['target'], env.source_generation) for p in active):
            bad.append('accepted-staged-incarnation-already-paired')
        proof = row['identity_proof']
        if not (proof and proof.get('case') == case['case'] and proof.get('prefix') == prefix
                and proof.get('source_origin') == origin_s
                and proof.get('adapter_origin') == origin_a):
            bad.append('identity-proof-not-the-recomputed-shared-origin')
        if 'staged' in row['differing_common_fields']:
            bad.append('accepted-staged-still-reported-differing')
        witness = {'case': case['case'], 'prefix': prefix, 'active_pairs': len(active),
                   'stage_event_index': origin_s['event_index'] if origin_s else None,
                   'staged_sha256': r.digest(left), 'request': env.request if env else None,
                   'generation': env.generation if env else None,
                   'source_generation': list(env.source_generation) if env else None}
    return bad, witness


def inspect_cases(cases, charge):
    observations, limitations = [], []
    audited = accepted = counterexamples = 0
    for case in cases:
        try:
            rows, pairs = case['prefixes'], case['incarnation_pairs']
            views_s, views_a = _views(case['source']), _views(case['adapter'])
            if case['source']['actions'] != case['adapter']['actions']:
                limitations.append(case['case'] + ': source/adapter actions differ')
        except (KeyError, TypeError) as error:
            limitations.append('uninspectable case: ' + repr(error)); continue
        refused = sum(1 for i, e in enumerate(case['source']['events'])
                      if e['action'].split('@')[0] == 'stage' and views_s[i + 1][1] != 'stage:ok')
        if refused: observations.append({'case': case['case'], 'visible_stage_refusals': refused})
        for position, row in enumerate(rows):
            charge.take(1)
            audited += 1
            try:
                bad, witness = _inspect(case, row, views_s, views_a, pairs)
                if row['prefix'] != position: bad.append('row-prefix-not-chronological')
            except (KeyError, IndexError, TypeError, ValueError) as error:
                limitations.append('uninspectable prefix: ' + repr(error)); continue
            accepted += row['staged_rule'] == IDENTITY
            counterexamples += bool(bad)
            if len(observations) < KEEP and witness:
                observations.append({'accepted_staged_witness': witness})
            if bad and len(observations) < KEEP:
                observations.append({'counterexample': {
                    'case': case['case'], 'prefix': row['prefix'], 'violations': bad,
                    'basis': 'original retained row; this control performs no mutation'}})
    if not cases or audited == 0: status = 'not_applicable'
    elif counterexamples: status = 'counterexample'
    elif not accepted:
        status = 'unproved'
        limitations.append('no inspected prefix reached original-object-identity; '
                           'acceptance-scope checks had no reachable witness')
    else: status = 'supported'
    limitations.append('bounded inspected prefixes only; no global theorem or scientific PASS')
    limitations.append('event state hashes are trusted from retained traces; staged values, '
                       'origins, validity and pair accounting are independently re-derived')
    summary = {'cases_seen': len(cases), 'accepted_staged_prefixes': accepted,
               'prefixes_with_violations': counterexamples}
    return {'status': status, 'limitations': limitations,
            'audited_prefixes': audited, 'observations': [summary] + observations}


def run_controls(cases, inspect_cases, charge):
    """Adversarial controls: semantic deepcopy mutations of real retained cases."""
    labels = ['unmodified-retained-case-baseline', 'forged-staged-signatures-both-sides',
              'staged-payload-detached-from-envelope', 'nonidentical-staged-envelopes',
              'dropped-stage-origin-on-source', 'invented-incarnation-pair',
              'detached-identity-proof-event', 'identity-claims-incarnation-authority']
    target = next(((c, row) for c in cases for row in c['prefixes']
                   if row.get('staged_rule') == IDENTITY and row.get('identity_proof')), None)
    if target is None:
        missing = [{'control': x, 'detected': None,
                    'missing_witness': 'no reachable original-object-identity prefix'}
                   for x in labels]
        return {'controls': missing, 'reachable_identity_witness': False, 'witness_case': None}
    case, row = target
    index = row['identity_proof']['source_origin']['event_index']
    staged = _views(case['source'])[row['prefix']][0]
    gen = tuple(staged[0].source_generation)
    results = []

    def probe(label, mutate, expect=True):
        mutated = copy.deepcopy(case)
        mutate(mutated, row)
        outcome = inspect_cases([mutated], charge)
        results.append({'control': label, 'detected': outcome['status'] == 'counterexample',
                        'expected_detected': expect, 'observed_status': outcome['status'],
                        'note': 'semantic deepcopy; outer event hashes preserved'})

    def both(fn):
        def apply(m, _row):
            for side in ('source', 'adapter'):
                patch = m[side]['events'][index]['patch']
                (patch.setdefault('core', {}) if side == 'adapter' else patch)['staged'] = fn(staged)
        return apply

    probe(labels[0], lambda m, r_: None, expect=False)
    probe(labels[1], both(lambda v: (v[0]._replace(signature='0' * 64), v[1])))
    probe(labels[2], both(lambda v: (v[0], v[1] + '-mutated')))
    probe(labels[3], lambda m, r_: m['adapter']['events'][index]['patch'].setdefault('core', {})
          .update(staged=(staged[0]._replace(generation='forged-generation'), staged[1])))
    probe(labels[4], lambda m, r_: m['source']['events'][index].update(action='not-stage@0'))
    probe(labels[5], lambda m, r_: m['incarnation_pairs'].append(
        {'source': gen, 'target': gen, 'reason': 'invented', 'source_event': 0, 'target_event': 0}))
    probe(labels[6], lambda m, r_: m['prefixes'][r_['prefix']]['identity_proof']
          ['source_origin'].update(event_index=r_['prefix']))
    probe(labels[7], lambda m, r_: m['prefixes'][r_['prefix']]
          .update(incarnation_pair_established_by_identity=True))
    return {'controls': results, 'reachable_identity_witness': True, 'witness_case': case['case'],
            'mutations': 'deepcopies only; supplied typed cases unmodified; mutation '
                         'counterexamples are retained-evidence defects, not '
                         'original-domain counterexamples'}
