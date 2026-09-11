"""Retained-certificate check o07: source-attestation guard ordering.

Obligation: the source-attest guard refuses in a fixed order -- missing
capture/cut, stale (non-current) capture, incomplete collected inventory,
incomplete registry -- and the fresh complete-inventory 216-order class must
therefore refuse at the registry stage, never earlier.

Scope: bounded inspection of already-audited typed case objects retained by the
unchanged c.run_history / c.artifact pipeline. This module executes no reducer,
no audit relation and no boundary helper. The only original code invoked is the
frozen typed trace restoration (the same restoration audit_case performs) plus
immutable input encodings (s_domain.records/registration/mapping) and semantic
typed equality/digest, all used strictly as representations of retained states.

Source anchors (unchanged originals):
- s_inclusive.py:63-68 / s_split.py source-attest branch: refusal precedence
  no-captured-source -> stale-collection -> incomplete-inventory ->
  incomplete-registry; identical precedence in s_audit.py 'expected' and in the
  adapter transcriptions batch-06/guard_a.py:64-69, guard_b.py:71-76 (see
  inherited/prestage-correspondence-analysis.md).
- s_inclusive.py:55-62 / s_split.py: collect-open captures
  (source_generation, source_revision, registration, attempts,
  len(append_log)); collect:i retains a sorted (index, append_log[index]) pair.
- batch-06/a_audit.py:17-34 and a_inclusive.py:8-19: a refused attestation
  never invokes Q; core, invocations and journal attestation stay unchanged. An
  accepted guard call is a real Q invocation and commits journal attestation
  only when the Q decision is source-attest:ok.
- inherited/remaining-scale-coverage-analysis.md: the fresh complete-inventory
  class (216 orders per unit) is exactly the class whose first refusing
  attestation stage is the registry comparison.

Finite audit accounting: charge.take(1) is consumed exactly once per inspected
case prefix -- len(case['prefixes']) charges per case including repetitions;
audited_prefixes reports that same count. No other work is charged.

Status semantics: 'supported' requires every inspected source-attest decision
to equal the first failing stage evaluated on the retained pre-state AND at
least one inspected case to witness a current-capture complete-inventory
'incomplete-registry' refusal (the fresh-complete mechanism). Any retained
mismatch is 'counterexample'; conforming evidence without a registry-stage
witness, or unavailable unchanged modules, is 'unproved'; no source-attest
event is 'not_applicable'. This is a bounded certificate check over supplied
cases only -- no global theorem and no accepted-science PASS is claimed.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
_PATHS = ('experiments/v3/cut-source-overnight/batch-07',
          'experiments/v3/cut-source-overnight/batch-06',
          'experiments/v3/cut-source-overnight/batch-05',
          'experiments/v3/cut-source-overnight',
          'experiments/v3/cut-publication')
ATTEST = 'source-attest'
STAGE_NAMES = ('missing capture/cut', 'current capture', 'complete inventory',
               'complete registry')
JOURNAL_FIELDS = ('registration', 'attempts', 'append_log', 'append_receipts',
                  'append_reply', 'source_revision', 'collection', 'collected',
                  'attestation', 'staged_source', 'selected_source',
                  'source_generation')
_MISMATCH_CAP = 200


def _bind():
    for rel in _PATHS:
        path = str(ROOT / rel)
        if path not in sys.path:
            sys.path.insert(0, path)
    try:
        import identity as relation
        return relation.d, relation.frozen
    except ImportError:
        import check as c
        return c.d, c.t


def _j(value):
    if isinstance(value, dict):
        return {str(k): _j(v) for k, v in sorted(value.items(), key=lambda x: str(x[0]))}
    if type(value).__name__ == 'Envelope':
        return {'Envelope': [_j(v) for v in tuple(value)]}
    if isinstance(value, (list, tuple)):
        return [_j(v) for v in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    return repr(value)


def _decision(row, side):
    obs = row.get(side + '_observation') or {}
    if not obs and side == 'adapter':
        obs = row.get('target_observation') or {}
    return obs.get('decision')


def _stages(d, v):
    """First-failure evaluation of the declared guard order on a retained view.

    Returns (stage_rows, reason) with reason in
    {no-captured-source, stale-collection, incomplete-inventory,
    incomplete-registry, ok, None}. None means the retained fields or fixture
    encodings could not be represented; the obligation is then unproved for
    that event. Stage rows stop at the first failure, mirroring the original
    elif chain, and each row retains an expected/observed witness.
    """
    cap = v.get('collection') or ()
    name = v.get('cut_delivery') or ''
    collected = v.get('collected') or ()
    rows = []
    held = bool(cap) and bool(name)
    rows.append({'stage': STAGE_NAMES[0], 'held': held,
                 'expected': 'open collection and delivered cut',
                 'observed': {'capture_present': bool(cap), 'cut': name or None}})
    if not held:
        return rows, 'no-captured-source'
    try:
        held = d.exact(cap[0], v.get('source_generation')) and \
            cap[1] == v.get('source_revision')
        rows.append({'stage': STAGE_NAMES[1], 'held': held,
                     'expected': _j((v.get('source_generation'), v.get('source_revision'))),
                     'observed': _j((cap[0], cap[1]))})
        if not held:
            return rows, 'stale-collection'
        records = d.s.records(name)
        registration = d.s.registration(name)
        mapping = d.s.mapping(name)
        indices = tuple(i for i, _ in collected)
        raws = tuple(raw for _, raw in collected)
        held = indices == tuple(range(cap[4])) and d.exact(raws, records)
        rows.append({'stage': STAGE_NAMES[2], 'held': held,
                     'expected': {'indices': list(range(cap[4])),
                                  'records_sha256': d.digest(records)},
                     'observed': {'indices': list(indices),
                                  'records_sha256': d.digest(raws)}})
        if not held:
            return rows, 'incomplete-inventory'
        reg_ok, map_ok = d.exact(cap[2], registration), d.exact(cap[3], mapping)
        rows.append({'stage': STAGE_NAMES[3], 'held': reg_ok and map_ok,
                     'expected': {'registration_sha256': d.digest(registration),
                                  'attempt_mapping': _j(mapping)},
                     'observed': {'registration_sha256': d.digest(cap[2]),
                                  'captured_attempts': _j(cap[3])},
                     'registration_match': reg_ok,
                     'attempt_mapping_match': map_ok,
                     'captured_attempt_count': len(cap[3]),
                     'declared_mapping_count': len(mapping)})
        if not (reg_ok and map_ok):
            return rows, 'incomplete-registry'
        return rows, 'ok'
    except Exception as error:
        rows.append({'stage': 'representation', 'held': None,
                     'expected': 'evaluable retained capture and fixture encoding',
                     'observed': 'unresolved: %s' % (error,)})
        return rows, None


def _attest(d, ss, aa, rows, k, name, flag):
    src = ss[k]
    view = dict(aa[k].get('core') or {})
    view.update(aa[k].get('journal') or {})
    s_rows, s_reason = _stages(d, src)
    a_rows, a_reason = _stages(d, view)
    row = rows[k] if k < len(rows) else {}
    post_s = ss[k + 1] if k + 1 < len(ss) else None
    post_a = aa[k + 1] if k + 1 < len(aa) else None
    obs = {'expected_first_failure': s_reason,
           'adapter_first_failure': a_reason,
           'source_stages': s_rows, 'adapter_stages': a_rows,
           'source_decision': _decision(row, 'source'),
           'adapter_decision': _decision(row, 'adapter'),
           'q_invoked': row.get('q_invoked'),
           'unresolved': s_reason is None or a_reason is None,
           'registry_stage_witness': s_reason == a_reason == 'incomplete-registry'}
    if None not in (s_reason, a_reason) and s_reason != a_reason:
        flag({'case': name, 'prefix': k, 'kind': 'guard-sides-disagree',
              'expected': s_reason, 'observed': a_reason})
    for side, reason in (('source', s_reason), ('adapter', a_reason)):
        if reason is None:
            continue
        want = ATTEST + ':' + reason
        got = _decision(row, side)
        if got != want:
            flag({'case': name, 'prefix': k,
                  'kind': side + '-decision-not-first-failure',
                  'expected': want, 'observed': got})
    if s_reason not in (None, 'ok'):
        if row.get('q_invoked'):
            flag({'case': name, 'prefix': k, 'kind': 'q-invoked-on-refused-attest'})
        if post_a is not None:
            if not d.exact(post_a.get('core'), aa[k].get('core')):
                flag({'case': name, 'prefix': k, 'kind': 'core-changed-on-refusal'})
            if not d.exact(post_a.get('invocations'), aa[k].get('invocations')):
                flag({'case': name, 'prefix': k, 'kind': 'invocations-changed-on-refusal'})
            if not d.exact((post_a.get('journal') or {}).get('attestation'),
                           (aa[k].get('journal') or {}).get('attestation')):
                flag({'case': name, 'prefix': k,
                      'kind': 'journal-attestation-changed-on-refusal'})
        if post_s is not None:
            if not d.exact(post_s.get('attestation'), src.get('attestation')):
                flag({'case': name, 'prefix': k,
                      'kind': 'source-attestation-changed-on-refusal'})
            if not d.exact(post_s.get('source_name'), src.get('source_name')):
                flag({'case': name, 'prefix': k, 'kind': 'source-name-set-on-refusal'})
    if s_reason == 'ok':
        if not row.get('q_invoked'):
            flag({'case': name, 'prefix': k, 'kind': 'accepted-guard-without-q-call'})
        if post_a is not None:
            committed = (src['collection'][0], src['collection'][1],
                         src.get('cut_delivery'))
            committed_ok = d.exact((post_a.get('journal') or {}).get('attestation'),
                                   committed)
            if (obs['adapter_decision'] == ATTEST + ':ok') != committed_ok:
                flag({'case': name, 'prefix': k,
                      'kind': 'committed-attestation-vs-q-decision',
                      'expected': _j(committed),
                      'observed': _j((post_a.get('journal') or {}).get('attestation'))})
    if obs['registry_stage_witness']:
        reg = s_rows[-1]
        obs['explanation'] = ('current capture and complete collected inventory held at '
                              'attestation; refusal arises only at the registry stage '
                              '(registration_match=%s, attempt_mapping_match=%s, '
                              'captured_attempts=%s, declared_mapping=%s)'
                              % (reg.get('registration_match'),
                                 reg.get('attempt_mapping_match'),
                                 reg.get('captured_attempt_count'),
                                 reg.get('declared_mapping_count')))
    return obs


def inspect_cases(cases, charge):
    """Bounded retained-certificate inspection; see module docstring."""
    limitations, observations = [], []
    mismatches, dropped = [], [0]
    audited, attests, witnesses, unresolved = 0, 0, 0, 0
    tally = {}

    def flag(item):
        if len(mismatches) < _MISMATCH_CAP:
            mismatches.append(item)
        else:
            dropped[0] += 1

    try:
        d, t = _bind()
    except Exception as error:
        return {'status': 'unproved', 'observations': [], 'audited_prefixes': 0,
                'limitations': ['could not bind unchanged original modules: %s' % (error,),
                                'no prefix inspected; obligation unevaluated on this evidence']}
    if isinstance(cases, dict) or cases is None:
        cases = [cases] if cases else []
    for position, case in enumerate(cases):
        name = case.get('case', 'case-%d' % position)
        try:
            ss = t.restore(case['source'])
            aa = t.restore(case['adapter'])
        except Exception as error:
            flag({'case': name, 'kind': 'restore-failed',
                  'detail': str(error)[:200]})
            continue
        prefixes = case.get('prefixes') or []
        actions = tuple(case['source'].get('actions') or ())
        rows = case.get('rows') or []
        if len(ss) != len(prefixes) or len(aa) != len(prefixes):
            limitations.append('%s: restored states %d/%d differ from retained prefixes %d'
                               % (name, len(ss), len(aa), len(prefixes)))
        hits = [i for i, a in enumerate(actions) if a.split('@')[0] == ATTEST]
        k = hits[0] if hits else None
        if len(hits) > 1:
            limitations.append('%s: extra source-attest events at %s' % (name, hits[1:]))
        entry = {'case': name, 'attest_index': k, 'prefixes': len(prefixes)}
        for i in range(len(prefixes)):
            charge.take(1)
            audited += 1
            if i >= len(ss) or i >= len(aa):
                flag({'case': name, 'prefix': i, 'kind': 'missing-restored-state'})
                continue
            src, adp = ss[i], aa[i]
            missing = [f for f in JOURNAL_FIELDS
                       if f not in src or f not in (adp.get('journal') or {})]
            if missing:
                flag({'case': name, 'prefix': i,
                      'kind': 'missing-journal-field', 'fields': missing})
            if not i:
                continue
            row = rows[i - 1] if i - 1 < len(rows) else None
            if row is None:
                flag({'case': name, 'prefix': i, 'kind': 'missing-comparison-row'})
            else:
                if row.get('index') not in (None, i - 1):
                    flag({'case': name, 'prefix': i, 'kind': 'row-index-misaligned',
                          'expected': i - 1, 'observed': row.get('index')})
                s_dec, a_dec = _decision(row, 'source'), _decision(row, 'adapter')
                if s_dec is not None and s_dec != src.get('decision'):
                    flag({'case': name, 'prefix': i, 'kind': 'source-decision-drift',
                          'expected': s_dec, 'observed': src.get('decision')})
                if a_dec is not None and a_dec != adp.get('decision'):
                    flag({'case': name, 'prefix': i, 'kind': 'adapter-decision-drift',
                          'expected': a_dec, 'observed': adp.get('decision')})
            if i == k:
                attests += 1
                entry['attestation'] = _attest(d, ss, aa, rows, k, name, flag)
                if entry['attestation']['expected_first_failure']:
                    tally[entry['attestation']['expected_first_failure']] = \
                        tally.get(entry['attestation']['expected_first_failure'], 0) + 1
                if entry['attestation']['unresolved']:
                    unresolved += 1
                if entry['attestation']['registry_stage_witness']:
                    witnesses += 1
        observations.append(entry)
    if dropped[0]:
        limitations.append('mismatch list truncated; %d further flags dropped' % dropped[0])
    limitations.append('bounded inspection over %d supplied case(s); uninspected '
                       'orders unclaimed' % len(cases))
    limitations.append('no reducer, audit relation or boundary helper executed; '
                       'frozen restoration and input encodings only')
    if mismatches:
        status = 'counterexample'
        observations.insert(0, {'mismatches': mismatches})
    elif not attests:
        status = 'not_applicable'
    elif unresolved:
        status = 'unproved'
        limitations.append('fixture or retained-field representation unresolved for '
                           '%d attestation event(s)' % unresolved)
    elif not witnesses:
        status = 'unproved'
        limitations.append('ordering held on all inspected events, but no inspected case '
                           'reaches the registry stage with current capture and complete '
                           'inventory; the fresh-complete 216-order explanation is '
                           'unwitnessed in this evidence')
    else:
        status = 'supported'
    observations.insert(0, {'summary': {'attestation_events': attests,
                                        'first_failure_tally': tally,
                                        'registry_stage_witnesses': witnesses,
                                        'flags': len(mismatches)}})
    return {'status': status, 'observations': observations,
            'limitations': limitations, 'audited_prefixes': audited}
