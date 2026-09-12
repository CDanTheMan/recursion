"""Bounded retained-certificate check: obligation o27 (boundary-01 binding).

Scope: case/unit/outcome/global-index/literal-schedule/source-hash binding,
deterministic typed gzip serialization, cross-case identity-proof and stale
artifact reuse detection. No reducer, inventory enumerator or boundary helper
is executed or imported; only unchanged original audit/representation code is
reused (check.artifact/codec typed encoding, adapter_traces.restore replay,
s_domain/a_domain initial constructors, check.audit_case prefix re-audit).

Accounting: charge.take(1) runs exactly once before each inspected case prefix;
every repetition counts. Case-level binding, replay, re-audit and serialization
checks are uncharged per the obligated interface. Budget exhaustion propagates.

Status: 'supported' covers only actually inspected prefixes (never a global
PASS); 'counterexample' keeps a falsifiable expected/observed witness;
'unproved' when no prefix could be audited; 'not_applicable' on empty input.
run_controls labels each mutation 'original-domain' (reachable alternative) or
'unreachable'; controls needing a genuine identity_proof or refused-attestation
witness report 'unwitnessed' with the limitation preserved.

Source anchors: boundary-01 spec (fixed prefix 11 / core 8 / suffix 19, units
event/utf8-byte, outcome 1, subclasses fresh-incomplete=C0;perm(A2,A3,A4,R);O;
perm(C1,C2), stale-complete=O;perm(A2,A3,A4,R);perm(C0,C1,C2)); case identity
boundary-01/<global6>/<unit>/1 and mtime=0 typed gzip bytes (boundary.py);
identity_proof fields (batch-07 identity.py); typed decode (artifact.py).
"""
import copy
import gzip
import hashlib
import json
import sys
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/eight-hour-research-20260910-01a08a22'))
import check as c

PACKET = 'boundary-01'
PREFIX, CORE, SUFFIX, DEPTH = 11, 8, 19, 34
UNITS, OUTCOME = ('event', 'utf8-byte'), 1
OPEN, RESTART = 'collect-open@11', 'source-restart@18'
COLLECTS = ('collect:0@12', 'collect:1@13', 'collect:2@14')
FREE = frozenset(('attempt:2@15', 'attempt:3@16', 'attempt:4@17', RESTART))
ALPHABET = tuple(sorted((*COLLECTS, OPEN, *FREE)))


class _Missing(Exception):
    pass


def _js(x):
    try:
        return json.dumps(x, sort_keys=True, separators=(',', ':'), default=repr)[:300]
    except (TypeError, ValueError):
        return repr(x)[:300]


def _e(ok, check_name, expected, observed):
    if not ok:
        raise ValueError(check_name + '|expected=' + _js(expected) + '|observed=' + _js(observed))


def _subclass(middle):
    if set(middle) != set(ALPHABET):
        return None
    if middle[0] == COLLECTS[0] and set(middle[1:5]) == FREE and middle[5] == OPEN \
            and set(middle[6:]) == set(COLLECTS[1:]):
        return 'fresh-incomplete'
    if middle[0] == OPEN and set(middle[1:5]) == FREE and set(middle[5:]) == set(COLLECTS):
        return 'stale-complete'
    return None


def _index(middle):
    remaining, value = list(ALPHABET), 0
    for action in middle:
        i = remaining.index(action)
        value += i * factorial(len(remaining) - 1)
        del remaining[i]
    return value


def _raw(case):
    packed = c.codec.pack(c.artifact.encode(case))
    return gzip.compress(json.dumps(packed, sort_keys=True, separators=(',', ':')).encode(),
                         compresslevel=6, mtime=0)


def _counterexample(position, prefix, error, observations, limitations, audited):
    observations.append(dict(case_position=position, prefix=prefix, witness=str(error)[:400]))
    return dict(status='counterexample', observations=observations,
                limitations=limitations, audited_prefixes=audited)


def inspect_cases(cases, charge):
    observations, limitations, audited = [], [], 0
    proofs = refused = 0
    if not cases:
        return dict(status='not_applicable', observations=[],
                    limitations=['empty case list'], audited_prefixes=0)
    names, raws = set(), {}
    for position, case in enumerate(cases):
        try:
            parts = str(case['case']).split('/')
            _e(len(parts) == 4 and parts[0] == PACKET and parts[1].isdigit(),
               'case-identity', 'boundary-01/<index>/<unit>/<outcome>', case['case'])
            unit, outcome = parts[2], int(parts[3])
            _e(unit in UNITS and case['unit'] == unit and case['outcome'] == outcome == OUTCOME,
               'environment-binding', (unit, OUTCOME), (case['unit'], case['outcome']))
            profile = case['source']['profile']
            schedule = case['source']['actions']
            _e(type(schedule) is tuple and len(schedule) == DEPTH,
               'literal-schedule', '34-tuple', (type(schedule).__name__, len(schedule)))
            _e(schedule == case['adapter']['actions'], 'side-schedule-agreement',
               'equal literal actions', 'sides differ')
            _e(tuple(schedule[:PREFIX]) == profile['actions'][:PREFIX]
               and tuple(schedule[SUFFIX:]) == profile['actions'][SUFFIX:],
               'fixed-prefix-suffix', 'profile affine frame', 'differs')
            middle = schedule[PREFIX:SUFFIX]
            _e(_subclass(middle) is not None, 'subclass-membership',
               'fresh-incomplete|stale-complete', list(middle))
            c.validate_inventory(profile, (schedule,), 1)
            _e(_index(middle) == int(parts[1]), 'global-index', int(parts[1]), _index(middle))
            raw = _raw(case)
            _e(raw == _raw(case), 'deterministic-gzip', 'stable bytes', 're-encode differs')
            restored = c.artifact.decode(c.codec.unpack(json.loads(gzip.decompress(raw))))
            _e(c.d.exact(restored, case), 'typed-roundtrip', 'original case', 'decoded differs')
            _e(case['case'] not in names, 'duplicate-certificate', 'first occurrence', case['case'])
            _e(raw not in raws, 'stale-artifact-reuse', 'unique bytes',
               'same bytes as ' + str(raws.get(raw)))
            names.add(case['case'])
            raws[raw] = case['case']
            _e(c.d.exact(case['source']['initial'], c.d.s.initial(unit))
               and c.d.exact(case['adapter']['initial'], c.d.initial(unit)),
               'initial-state-unit', unit, 'initial mismatch')
            ss, aa = c.t.restore(case['source']), c.t.restore(case['adapter'])
            _e(len(ss) == len(aa) == len(case['prefixes']) == DEPTH + 1
               and len(case['rows']) == DEPTH, 'prefix-inventory',
               DEPTH + 1, (len(ss), len(case['prefixes'])))
            _e(c.d.exact(c.audit_case(case), case['prefixes']), 'independent-prefix-reaudit',
               'retained prefixes', 'recomputed differ')
        except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
            return _counterexample(position, None, error, observations, limitations, audited)
        for i in range(DEPTH + 1):
            charge.take(1)
            audited += 1
            try:
                item = case['prefixes'][i]
                _e(item['prefix'] == i and item['incarnation_pair_established_by_identity'] is False,
                   'prefix-record', (i, False),
                   (item['prefix'], item['incarnation_pair_established_by_identity']))
                if i:
                    row = case['rows'][i - 1]
                    _e(row['index'] == i - 1 and row['source_action'] == row['adapter_action']
                       == schedule[i - 1], 'literal-row', (i - 1, schedule[i - 1]),
                       (row['index'], row['source_action']))
                    decision = row['source_observation']['decision']
                    if decision.startswith('source-attest:') and decision != 'source-attest:ok':
                        refused += 1
                        _e(row['q_invoked'] is False, 'refused-attestation-mask',
                           False, row['q_invoked'])
                proof = item['identity_proof']
                if proof is not None:
                    proofs += 1
                    _e(proof['case'] == case['case'] and proof['prefix'] == i,
                       'cross-case-proof', (case['case'], i), (proof['case'], proof['prefix']))
                    _e(proof['source_state_sha256'] == c.d.digest(ss[i])
                       and proof['adapter_state_sha256'] == c.d.digest(aa[i]),
                       'proof-state-binding', 'restored digests', 'mismatch')
                    _e(proof['source_prefix_sha256'] == c.d.digest(case['source']['events'][:i])
                       and proof['adapter_prefix_sha256'] == c.d.digest(case['adapter']['events'][:i]),
                       'proof-prefix-binding', 'event digests', 'mismatch')
                    _e(proof['source_origin']['event_index'] == proof['adapter_origin']['event_index'] < i
                       and proof['source_origin']['action'] == proof['adapter_origin']['action'],
                       'shared-stage-origin', 'same prior index/action',
                       (proof['source_origin'], proof['adapter_origin']))
            except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
                return _counterexample(position, i, error, observations, limitations, audited)
    observations.append(dict(cases=len(cases), unique_certificate_bytes=len(raws),
                             identity_proofs_verified=proofs, refused_attestations=refused))
    if not proofs:
        limitations.append('no identity_proof witness; cross-case proof binding unexercised')
    if not refused:
        limitations.append('no refused source-attest row; refused-invocation mask unexercised')
    if not audited:
        return dict(status='unproved', observations=observations,
                    limitations=limitations + ['no case prefix was audited'], audited_prefixes=0)
    return dict(status='supported', observations=observations,
                limitations=limitations, audited_prefixes=audited)


def run_controls(cases, inspect_cases, charge):
    controls, limitations = [], []

    def need(ok, message):
        if not ok:
            raise _Missing(message)

    def rename(bad, index=None, unit=None):
        p = bad['case'].split('/')
        bad['case'] = '/'.join((p[0], str(p[1] if index is None else index).zfill(6),
                                unit or p[2], p[3]))
        if unit is not None:
            bad['unit'] = unit

    def mutate(fn):
        need(len(cases) >= 1, 'requires one supplied case')
        bad = copy.deepcopy(cases[0])
        fn(bad)
        return [bad]

    def b_index():
        need(len(cases) > 1, 'requires two real cases')
        return mutate(lambda b: rename(b, index=cases[1]['case'].split('/')[1]))

    def b_unit():
        return mutate(lambda b: rename(b, unit=next(u for u in UNITS if u != b['unit'])))

    def b_stale():
        need(len(cases) > 1, 'requires two real cases')
        bad = copy.deepcopy(cases[0])
        rename(bad, index=cases[1]['case'].split('/')[1])
        return [cases[0], bad]

    def b_proof():
        holders = [(k, i) for k, cs in enumerate(cases)
                   for i, x in enumerate(cs['prefixes']) if x.get('identity_proof')]
        need(len(holders) > 1, 'requires two real identity_proof witnesses')
        (a, pa), (b, pb) = holders[0], holders[1]
        bad = copy.deepcopy(cases[a])
        bad['prefixes'][pa]['identity_proof'] = copy.deepcopy(cases[b]['prefixes'][pb]['identity_proof'])
        return [bad]

    def b_qmask():
        for k, cs in enumerate(cases):
            for i, row in enumerate(cs['rows']):
                d = row['source_observation']['decision']
                if d.startswith('source-attest:') and d != 'source-attest:ok' \
                        and row['q_invoked'] is False:
                    bad = copy.deepcopy(cs)
                    bad['rows'][i]['q_invoked'] = True
                    return [bad]
        raise _Missing('requires a real refused-attestation row')

    def attempt(label, klass, build):
        try:
            bad = build()
        except _Missing as m:
            controls.append(dict(control=label, status='unwitnessed', mutation_class=klass,
                                 witness=str(m)))
            limitations.append(label + ': ' + str(m))
            return
        result = inspect_cases(bad, charge)
        controls.append(dict(control=label, mutation_class=klass,
                             status='detected' if result['status'] == 'counterexample'
                             else 'undetected:' + result['status'],
                             witness=result['observations'][-1] if result['observations']
                             else result['status']))

    base = inspect_cases(cases, charge)
    controls.append(dict(control='baseline-retained-evidence', mutation_class='none',
                         status='supported' if base['status'] == 'supported'
                         else 'unexpected:' + base['status'], witness=base['status']))
    if base['status'] != 'supported':
        limitations.append('baseline not supported; mutation outcomes are inconclusive')
    attempt('wrong-global-index', 'original-domain', b_index)
    attempt('cross-unit-certificate', 'original-domain', b_unit)
    attempt('stale-artifact-reuse', 'original-domain', b_stale)
    attempt('duplicate-certificate', 'original-domain',
            lambda: [cases[0], copy.deepcopy(cases[0])] if cases else _raise())
    attempt('cross-case-identity-proof', 'original-domain', b_proof)
    attempt('tampered-event-hash', 'unreachable',
            lambda: mutate(lambda b: b['source']['events'][0].update(after_sha256='0' * 64)))
    attempt('tuple-loss-schedule', 'unreachable',
            lambda: mutate(lambda b: b['source'].update(actions=list(b['source']['actions']))))
    attempt('dropped-visible-event', 'unreachable',
            lambda: mutate(lambda b: b['source']['events'].pop()))
    attempt('false-q-invocation-on-refused-attest', 'unreachable', b_qmask)
    attempt('semantic-edit-under-intact-identity', 'unreachable',
            lambda: mutate(lambda b: b['prefixes'][-1].update(
                strict_related=not b['prefixes'][-1]['strict_related'])))
    attempt('outcome-field-mismatch', 'unreachable',
            lambda: mutate(lambda b: b.update(outcome=2)))
    return dict(status='controls-executed', baseline_status=base['status'], controls=controls,
                limitations=limitations,
                detected=sum(x['status'] == 'detected' for x in controls),
                unwitnessed=sum(x['status'] == 'unwitnessed' for x in controls),
                audited_prefixes=base['audited_prefixes'])


def _raise():
    raise _Missing('requires one supplied case')
