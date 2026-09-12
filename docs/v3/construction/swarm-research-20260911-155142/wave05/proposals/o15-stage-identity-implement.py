"""Bounded retained-certificate check: scope of the accepted staged-identity disjunct.

Obligation o15 (parent goal-recursion-v2-execution-fabric): a delegated ``stage``
pass-through can leave byte-identical, individually valid, still-unattested staged
objects on both sides while the strict incarnation-pair relation still flags the
``staged`` field. This module audits supplied retained case certificates to fix the
exact scope in which that strict gap is accepted by original-object identity, and
to confirm the disjunct never invents incarnation pairs or authority.

Inputs are actual typed case objects produced by the unchanged runner
(``c.run_history``) or losslessly restored from its certificates
(``c.artifact``/``q_artifact``). Each case retains ``source``/``adapter`` event
traces, per-transition ``rows``, the final ``incarnation_pairs`` ledger and the
per-prefix relation rows (``prefixes``). No reducer, guard or model step is
executed here: prefix states are reconstructed only by digest-bound replay of the
retained event patches, and the incarnation ledger is rebuilt only through the
unchanged semantic binding law. Nothing from ``boundary.py`` is imported.

Finite audit accounting: ``charge.take(1)`` is called exactly once BEFORE the
inspection of each (case, prefix) pair in iteration order; repeated case objects
are charged and audited again. Patch replay, ledger rebuild, digests and typed
views are bounded work inside the charged prefix unit, matching the convention
that representation work inside a checked visit is not separately billed. A
charge refusal propagates: no prefix is ever inspected uncharged.

Disjunct premises (recomputed, never assumed): both staged values are
typed-identical ``(Envelope, raw)`` two-tuples; each envelope carries a typed
source incarnation token and validates its own body signature against retained
fixture bytes; each raw payload is the exact canonical cut object its own
envelope names; the latest successful literal ``stage`` event below the prefix
has the same event index and literal action on both sides, its recorded
before/after digests bind the replayed states, and the staged value is unchanged
from that event through the prefix. Per the validation contract these are the
only premises: empty ``source_name``, an empty pair ledger, equal live
generations and current-stage freshness are recorded as observations only.
Acceptance additionally requires the retained row to equal the independently
recomputed row, the recorded pairs digest to equal the rebuilt ledger, and the
row's ``incarnation_pair_established_by_identity`` flag to stay false.

Status: ``counterexample`` when an audited prefix applies the disjunct outside
its premises, withholds it where the premises hold, or falsifies a retained
digest or ledger; ``supported`` when every audited prefix is consistent and at
least one applies the disjunct, with every strict ``staged`` gap either accepted
inside scope or visibly retained as ``unrelated``; ``not_applicable`` when no
audited prefix lists ``staged`` among the strict differences; ``unproved``
otherwise, including unreadable evidence and refusal-only coverage. This is a
bounded certificate audit over the supplied histories only: not an all-order
theorem and not scientific acceptance.

Source anchors (unchanged originals):
- batch-07/identity.py:16-21 object validity; :24-36 stage origin; :39-48
  identity proof; :51-64 disjunct row; :58 ledger-immutability require.
- batch-07/identity_audit.py:10-23 independent validity; :26-49 audited origin
  proof; :52-64 the full-row view recomputation re-derived here.
- batch-05/semantic.py:13 common-field inventory; :15-21 typed/exact/digest;
  :25-33 incarnation token and own-signature validity; :35-54 pair-ledger law;
  :83-94 per-field views; :103-112 strict pair predicate incl. :105-106
  pre-attestation equality clause.
- batch-06/adapter_traces.py:15-21 compared core/journal views; :27-42 gap
  diagnostics (unattested/equal-generation facts are observations only);
  :57-73 the digest-bound replay contract mirrored by ``_replay``.
- eight-hour-research-20260910-01a08a22/check.py:75-104 case construction;
  :106-144 per-prefix audit chronology and ledger tail equality.
- docs/v3/construction/swarm-research-20260911-155142/validation-contract.json
  relation_non_narrowing; wave04/review-defects.json boundary controls
  (cross-case stage proofs, staged identity misused as selected authority).
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel  # unchanged original representation primitives only

EXTRA = (*rel.s.EXTRA, 'source_generation')
READ = (ValueError, KeyError, IndexError, TypeError)


def _digest(value):
    return rel.digest(value)


def _staged(state, side):
    return state['staged'] if side == 'source' else state['core']['staged']


def _view(state):
    # Compared adapter-side view: Q core overlaid with the adapter journal fields.
    return dict(state['core'], **{k: state['journal'][k] for k in rel.s.EXTRA},
                decision=state['decision'])


def _replay(trace):
    """Digest-bound replay of retained event patches; executes no reducer."""
    states = [copy.deepcopy(trace['initial'])]
    executed, done = set(), 0
    rel.require(len(trace['events']) == len(trace['actions']),
                'complete visible event inventory')
    for action, event in zip(trace['actions'], trace['events']):
        rel.require(event['action'] == action and action not in executed
                    and set(trace['profile']['requires'][action]) <= executed,
                    'literal occurrence and outer dependency')
        rel.require(_digest(states[-1]) == event['before_sha256'],
                    'retained prestate binding')
        current = copy.deepcopy(states[-1])
        for key, value in event['patch'].items():
            if trace['side'] == 'adapter' and key in ('core', 'journal'):
                current[key].update(value)
            else:
                current[key] = value
        executed.add(action)
        done |= 1 << trace['profile']['actions'].index(action)
        rel.require(_digest(current) == event['after_sha256'] and current['done'] == done,
                    'retained poststate and completion binding')
        if trace['side'] == 'adapter':
            qp = trace['q_profile']
            rel.require(current['core']['done'] ==
                        sum(1 << qp['actions'].index(a) for a in current['invocations']),
                        'retained actual Q invocation mask')
        states.append(current)
    return states


def _valid_object(value):
    """One retained staged object valid on its own, independent of acceptance."""
    if type(value) is not tuple or len(value) != 2 or type(value[0]) is not rel.q.Envelope:
        return False
    try:
        return rel.signed(value[0]) and value[1] == rel.q.raw_cut(value[0].cut)
    except READ:
        return False


def _origin(trace, states, prefix):
    """Latest successful literal stage event below prefix, digest-bound to states."""
    value = _staged(states[prefix], trace['side'])
    if not value:
        return None
    for index in range(prefix - 1, -1, -1):
        if rel.typed(_staged(states[index + 1], trace['side'])) != rel.typed(value):
            return None
        event = trace['events'][index]
        if (event['action'].split('@')[0] == 'stage'
                and states[index + 1]['decision'] == 'stage:ok'):
            rel.require(_digest(states[index]) == event['before_sha256']
                        and _digest(states[index + 1]) == event['after_sha256'],
                        'actual stage-origin state binding')
            return {'event_index': index, 'action': event['action'],
                    'before_sha256': event['before_sha256'],
                    'after_sha256': event['after_sha256']}
    return None


def _proof(case, source_states, adapter_states, prefix):
    left = _origin(case['source'], source_states, prefix)
    right = _origin(case['adapter'], adapter_states, prefix)
    if (not left or not right
            or (left['event_index'], left['action']) != (right['event_index'], right['action'])):
        return None
    return {'case': case['case'], 'prefix': prefix, 'source_origin': left,
            'adapter_origin': right,
            'source_prefix_sha256': _digest(case['source']['events'][:prefix]),
            'adapter_prefix_sha256': _digest(case['adapter']['events'][:prefix]),
            'source_state_sha256': _digest(source_states[prefix]),
            'adapter_state_sha256': _digest(adapter_states[prefix])}


def _expected(case, source_states, adapter_states, prefix, ledger):
    """Independently recomputed retained relation row for one prefix."""
    source, adapter = source_states[prefix], adapter_states[prefix]
    common = [key for key in rel.FIELDS
              if rel.field_view(source, key, 'source', ledger)
              != rel.field_view(adapter['core'], key, 'target', ledger)]
    journal = [key for key in EXTRA
               if rel.typed(source[key]) != rel.typed(adapter['journal'][key])]
    certificate = _proof(case, source_states, adapter_states, prefix)
    permit = (bool(certificate) and _valid_object(source['staged'])
              and _valid_object(adapter['core']['staged'])
              and rel.typed(source['staged']) == rel.typed(adapter['core']['staged']))
    differing = [key for key in common if key != 'staged' or not permit]
    expected = {'prefix': prefix, 'strict_differing_common_fields': common,
                'differing_common_fields': differing,
                'differing_journal_fields': journal,
                'strict_related': not (common or journal),
                'related': not (differing or journal),
                'staged_rule': ('strict' if 'staged' not in common else
                                'original-object-identity' if permit else 'unrelated'),
                'identity_proof': certificate if 'staged' in common and permit else None,
                'pairs_sha256': _digest(ledger),
                'incarnation_pair_established_by_identity': False}
    return expected, permit, certificate


def inspect_cases(cases, charge):
    """Audit retained per-prefix relation rows; see module docstring for scope."""
    witnesses, limitations = [], []
    audited = applied = refused = unverifiable = violations = 0

    def note(entry):
        if len(witnesses) < 16:
            witnesses.append(entry)

    for position, case in enumerate(cases):
        label = case['case'] if isinstance(case, dict) and 'case' in case else 'case-' + str(position)
        try:
            source_states = _replay(case['source'])
            adapter_states = _replay(case['adapter'])
        except READ as error:
            limitations.append({'case': label,
                                'unproved_reason': 'unreadable retained evidence: ' + str(error)[:160]})
            continue
        depth = len(source_states)
        rows = case['prefixes'] if isinstance(case.get('prefixes'), list) else []
        if len(rows) != depth or len(adapter_states) != depth:
            limitations.append({'case': label, 'unproved_reason':
                                'prefix/state cardinality mismatch: prefixes=%s states=%s/%s'
                                % (len(rows), depth, len(adapter_states))})
        ledger, ledger_ok = [], True
        for prefix in range(depth):
            charge.take(1)
            audited += 1
            if prefix and ledger_ok:
                index = prefix - 1
                try:
                    rel.advance(ledger, source_states[index], _view(adapter_states[index]),
                                source_states[prefix], _view(adapter_states[prefix]),
                                case['source']['actions'][index], index, index)
                except READ:
                    ledger_ok = False
            row = rows[prefix] if prefix < len(rows) else None
            if not ledger_ok or type(row) is not dict or prefix >= len(adapter_states):
                unverifiable += 1
                note({'kind': 'unverifiable-prefix', 'case': label, 'prefix': prefix,
                      'reason': 'incarnation ledger rebuild refused or retained row missing/malformed'})
                continue
            try:
                expected, permit, certificate = _expected(case, source_states,
                                                          adapter_states, prefix, ledger)
            except READ as error:
                unverifiable += 1
                note({'kind': 'unverifiable-prefix', 'case': label, 'prefix': prefix,
                      'reason': 'premise recomputation failed: ' + str(error)[:160]})
                continue
            gap = 'staged' in expected['strict_differing_common_fields']
            if gap and permit:
                applied += 1
            elif gap:
                refused += 1
            if rel.typed(row) != rel.typed(expected) or _digest(ledger) != row.get('pairs_sha256'):
                violations += 1
                note({'kind': 'scope-violation', 'case': label, 'prefix': prefix,
                      'observed_staged_rule': row.get('staged_rule'),
                      'expected_staged_rule': expected['staged_rule'],
                      'observed_differing_common_fields': row.get('differing_common_fields'),
                      'expected_differing_common_fields': expected['differing_common_fields'],
                      'retained_row_exact': rel.typed(row) == rel.typed(expected),
                      'ledger_digest_bound': _digest(ledger) == row.get('pairs_sha256'),
                      'identity_flag': row.get('incarnation_pair_established_by_identity')})
            elif gap:
                source, adapter = source_states[prefix], adapter_states[prefix]
                note({'kind': 'staged-disjunct-applied' if permit else 'staged-disjunct-refused',
                      'case': label, 'prefix': prefix,
                      'origin_event_index': certificate['source_origin']['event_index'] if certificate else None,
                      'origin_action': certificate['source_origin']['action'] if certificate else None,
                      'source_staged_sha256': _digest(source['staged']),
                      'adapter_staged_sha256': _digest(adapter['core']['staged']),
                      'both_sources_unattested': not source['source_name'] and not adapter['core']['source_name'],
                      'same_live_generation': rel.typed(source['source_generation']) == rel.typed(adapter['core']['source_generation']),
                      'pairs_at_prefix': len(ledger)})
        if ledger_ok and 'incarnation_pairs' in case and not rel.exact(ledger, case['incarnation_pairs']):
            violations += 1
            note({'kind': 'ledger-tail-mismatch', 'case': label,
                  'rebuilt_pairs_sha256': _digest(ledger),
                  'retained_pairs_sha256': _digest(case['incarnation_pairs'])})

    if violations:
        status = 'counterexample'
    elif unverifiable or limitations:
        status = 'unproved'
    elif applied:
        status = 'supported'
    elif refused:
        status = 'unproved'
    else:
        status = 'not_applicable'
    summary = {'kind': 'audit-summary', 'cases': len(cases), 'audited_prefixes': audited,
               'strict_staged_gap_prefixes': applied + refused,
               'disjunct_applied': applied, 'disjunct_refused_retained': refused,
               'unverifiable_prefixes': unverifiable, 'violations': violations,
               'premises': ['identical-typed-staged-objects',
                            'each-envelope-own-signature-and-payload-binding-valid',
                            'same-latest-successful-literal-stage-origin-event-index-and-action',
                            'staged-unchanged-since-origin-through-prefix',
                            'recomputed-row-equals-retained-row',
                            'rebuilt-ledger-digest-equals-pairs_sha256',
                            'incarnation_pair_established_by_identity-false'],
               'recorded_not_required': ['both_sources_unattested',
                                         'empty-incarnation-ledger',
                                         'same_live_generation',
                                         'current-stage-freshness']}
    limitations.append({'scope': 'bounded retained-certificate audit over supplied histories only; '
                                 'no all-order reachability, source truth, composition or scientific acceptance'})
    return {'status': status, 'observations': [summary] + witnesses,
            'limitations': limitations, 'audited_prefixes': audited}
