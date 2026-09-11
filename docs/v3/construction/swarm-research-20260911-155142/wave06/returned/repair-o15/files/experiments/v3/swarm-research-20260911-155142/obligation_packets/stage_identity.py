"""Bounded retained-certificate packet for obligation o15 (parent
goal-recursion-v2-execution-fabric): the exact scope in which the additive
staged disjunct excuses a strict ``staged`` difference for typed-identical,
individually valid staged originals with one audited shared stage-origin
event, while never creating incarnation pairs or authority.

Public API: ``inspect_cases(cases, charge)`` and ``run_controls(cases,
charge)``; both return JSON-safe dictionaries. ``cases`` are typed retained
case objects in the unchanged runner's ``check.run_history``/``audit_case``
shape (or losslessly restored from its certificates). No reducer, guard or
model step is executed: states come only from the unchanged digest-bound
``adapter_traces.restore`` replay, the incarnation ledger is rebuilt only by
the unchanged ``semantic.advance`` binding law, each transition is re-audited
by the unchanged ``s_audit.check``/``a_audit.check``, and each retained prefix
row is checked by the unchanged ``identity.compare`` + ``identity_audit.check``
independent pair plus exact typed equality against the retained row. Nothing
from ``boundary.py`` is imported.

Fixed findings -> source anchors
------------------------------
1. Repo root for THIS output location (obligation_packets/, four levels below
   the repository root): ``parents[4]``. The recovered checker used
   ``parents[3]``, which resolves to ``experiments/`` and cannot import the
   originals. The three imported original modules are additionally bound by
   absolute path. [wave06/reviews/o15.json import-root BLOCKER; check.py's own
   ROOT=parents[3] convention fits only its three-level location]
2. ``semantic.advance`` is called with its full nine-argument signature
   ``(pairs, s_before, q_before, s_after, q_after, action, action, i, i)``.
   The recovered checker's eight-argument call raised TypeError on every
   prefix >= 1 and could never emit ``supported`` or ``counterexample``.
   [wave06/reviews/o15.json advance-arity BLOCKER; semantic.py advance;
   check.py audit_case call shape]
3. Replay premises are restored verbatim by delegating to the unchanged
   ``adapter_traces.restore``: complete literal event inventory, literal
   occurrence and outer dependency, before/after digest chain, completion
   mask, the ``q_profile == a_domain.subprofile(profile)`` fixed-Q-occurrence
   binding the recovered checker dropped, and the actual-Q invocation mask.
   Equal source/adapter profiles and literal action lists are bound in the
   typed case schema before any restore. [wave06/reviews/o15.json
   dropped-premises finding; adapter_traces.py restore; check.py audit_case
   profile/action equality requires]
4. Literal chronological row/Q/relation premises are audited per prefix in
   the audit_case sequence: the rebuilt causal binding equals the retained
   row's ``binding``; retained ``index`` and both literal actions equal the
   chronological action; the actual Q invocation returned by the unchanged
   ``a_audit.check`` equals ``q_invoked`` and ``a_domain.justification``
   equals the retained translation; the unchanged ``response`` predicate
   equals ``responses_related``; the complete recomputed ``comparison`` row
   (including ``binding``) equals the retained row; the strict baseline ties
   this prefix's recomputed ``strict_related`` to the previous retained
   row's ``state_related`` and the previous recomputed ``strict_related`` to
   its ``prestate_related``; and the rebuilt ledger equals the retained
   ``incarnation_pairs`` tail. [check.py audit_case;
   adapter_traces.comparison/response; a_domain.justification;
   semantic.advance]
5. Complete typed per-branch schemas are enforced before any audit: exact
   trace keys (adapter adds ``q_profile``), exact event keys, exact 16-key
   comparison rows, exact 10-key prefix rows and exact 5-key incarnation
   pairs with ``semantic.token``-typed incarnations. ``len(rows)`` and
   ``len(prefixes)`` are bound to ``len(actions)``/``len(actions)+1`` so a
   case missing trailing rows cannot escape notice.
   [wave06/reviews/o15.json unbound-prefix-cardinality limitation]
6. Interop: ``run_controls`` invokes this module's own ``inspect_cases``
   (signature ``(cases, charge)``; no injected auditor). A probe is
   ``detected`` whenever re-inspection does not return ``supported``;
   ``detection_kind`` separates semantic violations (``counterexample``)
   from evidence rejection (``unproved``/``not_applicable``). An
   uninspectable mutated case is retained-evidence rejection, never a
   scientific counterexample. [wave06/reviews/o15.json INTEROP finding]
7. No relation restrictions are added and the accepted staged identity is
   not broadened: the disjunct is evaluated only by the unchanged
   ``identity``/``identity_audit`` originals; ``both_sources_unattested``,
   ``same_live_generation``, empty-ledger and current-stage freshness are
   recorded as observations only. [validation-contract
   relation_non_narrowing; identity.py; identity_audit.py;
   adapter_traces.gap_certificate]

Unit accounting
---------------
``charge.take(1)`` is called BEFORE: each case preamble (schema plus the
unchanged initializations), each of the two per-case trace restores, each
(case, prefix) audit unit (all unchanged audit calls inside one audited
prefix are bounded representation work inside that charged visit, matching
the checked-visit convention), the ``run_controls`` witness scan, the
witness restore, and each control probe (a deepcopy mutation plus the
repeated single-case inspection, which charges its own units again).
Repeated case objects are charged and audited again. A charge refusal
propagates: nothing is restored, audited, mutated or repeated uncharged.

Statuses: ``counterexample`` when a retained prefix, row or ledger disagrees
with the unchanged recomputation or an unchanged audit rejects it;
``supported`` when every audited prefix is consistent and at least one
applies the disjunct; ``unproved`` for uninspectable evidence, refused
audits without disagreement, or refusal-only coverage; ``not_applicable``
when nothing is auditable or no audited prefix lists ``staged`` among the
strict differences. This is a bounded certificate audit over supplied
histories only: not an all-order theorem and not scientific acceptance.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-07'))
import identity as relation
import identity_audit

d, r, frozen = relation.d, relation.r, relation.frozen

for _module, _relpath in (
        (relation, 'experiments/v3/cut-source-overnight/batch-07/identity.py'),
        (identity_audit, 'experiments/v3/cut-source-overnight/batch-07/identity_audit.py'),
        (frozen, 'experiments/v3/cut-source-overnight/batch-06/adapter_traces.py')):
    if Path(_module.__file__).resolve() != ROOT / _relpath:
        raise ImportError('original module not bound at ' + _relpath)

STRICT, IDENTITY, UNRELATED = 'strict', 'original-object-identity', 'unrelated'
KEEP = 16
AUDIT_ERRORS = (ValueError, KeyError, IndexError, TypeError, AttributeError)

TRACE_KEYS = {'side', 'initial', 'profile', 'actions', 'events'}
EVENT_KEYS = {'action', 'before_sha256', 'after_sha256', 'patch'}
CASE_KEYS = {'case', 'unit', 'outcome', 'source', 'adapter', 'rows', 'prefixes',
             'incarnation_pairs'}
ROW_KEYS = {'index', 'source_action', 'adapter_action', 'source_sha256',
            'adapter_sha256', 'pairs_sha256', 'prestate_related', 'state_related',
            'responses_related', 'differing_common_fields',
            'differing_journal_fields', 'source_observation', 'adapter_observation',
            'q_invoked', 'justification', 'binding'}
PREFIX_ROW_KEYS = {'prefix', 'strict_differing_common_fields',
                   'differing_common_fields', 'differing_journal_fields',
                   'strict_related', 'related', 'staged_rule', 'identity_proof',
                   'pairs_sha256', 'incarnation_pair_established_by_identity'}
PAIR_KEYS = {'source', 'target', 'reason', 'source_event', 'target_event'}


class _Unreadable(Exception):
    """Retained evidence cannot be read or audited; never a counterexample."""


def _require_schema(case):
    """Exact typed trace/case schema; any failure is uninspectable evidence."""
    if type(case) is not dict or not CASE_KEYS <= set(case):
        raise _Unreadable('case lacks the typed audit_case keys')
    if type(case['case']) is not str:
        raise _Unreadable('case label is not a string')
    for side in ('source', 'adapter'):
        trace = case[side]
        want = TRACE_KEYS | ({'q_profile'} if side == 'adapter' else set())
        if type(trace) is not dict or set(trace) != want:
            raise _Unreadable(side + ' trace keys differ from the typed schema')
        if trace['side'] != side or type(trace['initial']) is not dict \
                or type(trace['profile']) is not dict \
                or not isinstance(trace['actions'], (list, tuple)) \
                or type(trace['events']) is not list \
                or not all(type(a) is str for a in trace['actions']):
            raise _Unreadable(side + ' trace fields outside the typed schema')
        profile = trace['profile']
        if not isinstance(profile.get('actions'), (list, tuple)) \
                or type(profile.get('requires')) is not dict:
            raise _Unreadable(side + ' profile lacks a typed action inventory')
        for event in trace['events']:
            if type(event) is not dict or set(event) != EVENT_KEYS \
                    or type(event['action']) is not str \
                    or type(event['patch']) is not dict \
                    or type(event['before_sha256']) is not str \
                    or type(event['after_sha256']) is not str:
                raise _Unreadable(side + ' event outside the typed patch schema')
        if side == 'adapter' and (type(trace['q_profile']) is not dict
                or not isinstance(trace['q_profile'].get('actions'), (list, tuple))):
            raise _Unreadable('adapter trace lacks a typed Q occurrence profile')
    source, adapter = case['source'], case['adapter']
    if not d.exact(source['profile'], adapter['profile']) \
            or source['actions'] != adapter['actions']:
        raise _Unreadable('source/adapter profile or literal actions differ')
    depth = len(source['actions'])
    if len(source['events']) != depth or len(adapter['events']) != depth:
        raise _Unreadable('event inventory does not match the literal actions')
    rows, prefixes = case['rows'], case['prefixes']
    if type(rows) is not list or len(rows) != depth \
            or any(type(x) is not dict or set(x) != ROW_KEYS for x in rows):
        raise _Unreadable('comparison rows missing or outside the typed schema')
    if type(prefixes) is not list or len(prefixes) != depth + 1 \
            or any(type(x) is not dict or set(x) != PREFIX_ROW_KEYS for x in prefixes):
        raise _Unreadable('prefix rows missing or outside the typed schema')
    pairs = case['incarnation_pairs']
    if type(pairs) is not list or any(
            type(p) is not dict or set(p) != PAIR_KEYS
            or not r.token(p['source']) or not r.token(p['target'])
            or type(p['source_event']) is not int
            or type(p['target_event']) is not int for p in pairs):
        raise _Unreadable('incarnation ledger outside the typed pair schema')


def _restore(trace):
    """Unchanged digest-bound replay; any refusal is uninspectable evidence."""
    try:
        return frozen.restore(trace)
    except AUDIT_ERRORS as error:
        raise _Unreadable('digest-bound replay refused the ' + trace['side']
                          + ' trace: ' + str(error)[:120])


def _audit_prefix(case, source_states, adapter_states, pairs, prefix, prev_strict):
    """One charged prefix unit: chronological premises, then the relation row."""
    source, adapter = source_states[prefix], adapter_states[prefix]
    bad = []
    if prefix:
        index = prefix - 1
        action = case['source']['actions'][index]
        row = case['rows'][index]
        profile, unit = case['source']['profile'], case['unit']
        oldpairs = copy.deepcopy(pairs)
        frozen.sc.check(source_states[index], action, source, profile, unit,
                        case['outcome'])
        binding = r.advance(pairs, source_states[index],
                            frozen.core_view(adapter_states[index]), source,
                            frozen.core_view(adapter), action, action, index, index)
        if not d.exact(binding, row['binding']):
            bad.append('causal-binding-differs')
        if not (row['source_action'] == row['adapter_action'] == action
                and row['index'] == index):
            bad.append('literal-chronology-differs')
        call = frozen.audit.check(adapter_states[index], action, adapter, profile,
                                  unit, case['outcome'])
        if call != row['q_invoked']:
            bad.append('actual-q-invocation-differs')
        if not d.exact(row['justification'], d.justification(action, call)):
            bad.append('action-translation-differs')
        if frozen.response(source, adapter, action, pairs) != row['responses_related']:
            bad.append('response-relation-differs')
        expected_row = frozen.comparison(source_states[index], adapter_states[index],
                                         source, adapter, oldpairs, pairs, action,
                                         index, call)
        expected_row['binding'] = binding
        if not d.exact(expected_row, row):
            bad.append('comparison-row-differs')
    saved = copy.deepcopy(pairs)
    item = relation.compare(case, source_states, adapter_states, prefix, pairs)
    if not d.exact(saved, pairs):
        bad.append('identity-created-authority')
    identity_audit.check(item, case, source_states, adapter_states, prefix, pairs)
    retained = case['prefixes'][prefix]
    if prefix and not (item['strict_related'] == row['state_related']
                       and prev_strict == row['prestate_related']):
        bad.append('strict-baseline-differs')
    if r.typed(retained) != r.typed(item):
        bad.append('prefix-row-differs')
    return item, bad


def inspect_cases(cases, charge):
    """Audit retained per-prefix relation rows; see the module docstring."""
    witnesses, limitations = [], []
    audited = applied = refused = unverifiable = violations = 0

    def note(entry):
        if len(witnesses) < KEEP:
            witnesses.append(entry)

    if not isinstance(cases, (list, tuple)):
        return {'status': 'unproved', 'observations': [], 'audited_prefixes': 0,
                'limitations': [{'scope': 'cases is not a sequence; nothing inspectable'}]}
    for position, case in enumerate(cases):
        label = case['case'] if isinstance(case, dict) and type(case.get('case')) is str \
            else 'case-' + str(position)
        try:
            charge.take(1)
            _require_schema(case)
            charge.take(1)
            source_states = _restore(case['source'])
            charge.take(1)
            adapter_states = _restore(case['adapter'])
            frozen.sc.initialization(source_states[0], case['unit'])
            frozen.audit.initialization(adapter_states[0], case['unit'])
        except _Unreadable as error:
            unverifiable += 1
            limitations.append({'case': label, 'unproved_reason': str(error)[:160]})
            continue
        except AUDIT_ERRORS as error:
            unverifiable += 1
            limitations.append({'case': label,
                                'unproved_reason': 'initialization audit rejected: '
                                + str(error)[:140]})
            continue
        pairs, prev_strict, failed = [], None, False
        for prefix in range(len(source_states)):
            charge.take(1)
            audited += 1
            try:
                item, bad = _audit_prefix(case, source_states, adapter_states,
                                          pairs, prefix, prev_strict)
            except AUDIT_ERRORS as error:
                violations += 1
                failed = True
                note({'kind': 'audit-rejected', 'case': label, 'prefix': prefix,
                      'reason': str(error)[:160]})
                break
            if bad:
                violations += 1
                failed = True
                note({'kind': 'scope-violation', 'case': label, 'prefix': prefix,
                      'violations': bad,
                      'observed_staged_rule': case['prefixes'][prefix].get('staged_rule'),
                      'expected_staged_rule': item['staged_rule']})
                break
            if 'staged' in item['strict_differing_common_fields']:
                if item['staged_rule'] == IDENTITY:
                    applied += 1
                else:
                    refused += 1
                certificate = item['identity_proof']
                note({'kind': 'staged-disjunct-applied' if item['staged_rule'] == IDENTITY
                      else 'staged-disjunct-refused',
                      'case': label, 'prefix': prefix,
                      'origin_event_index': certificate['source_origin']['event_index']
                      if certificate else None,
                      'origin_action': certificate['source_origin']['action']
                      if certificate else None,
                      'source_staged_sha256': d.digest(source_states[prefix]['staged']),
                      'adapter_staged_sha256':
                      d.digest(adapter_states[prefix]['core']['staged']),
                      'both_sources_unattested': not source_states[prefix]['source_name']
                      and not adapter_states[prefix]['core']['source_name'],
                      'same_live_generation': d.exact(
                          source_states[prefix]['source_generation'],
                          adapter_states[prefix]['core']['source_generation']),
                      'pairs_at_prefix': len(pairs)})
            prev_strict = item['strict_related']
        if not failed and not d.exact(pairs, case['incarnation_pairs']):
            violations += 1
            note({'kind': 'ledger-tail-mismatch', 'case': label,
                  'rebuilt_pairs_sha256': d.digest(pairs),
                  'retained_pairs_sha256': d.digest(case['incarnation_pairs'])})

    if violations:
        status = 'counterexample'
    elif unverifiable or limitations:
        status = 'unproved'
    elif applied:
        status = 'supported'
    elif refused:
        status = 'unproved'
        limitations.append({'scope': 'staged strict gaps were audited but no prefix '
                            'reached original-object-identity; the acceptance-scope '
                            'checks had no reachable witness'})
    else:
        status = 'not_applicable'
    limitations.append({'scope': 'bounded retained-certificate audit over supplied '
                        'histories only; no all-order reachability, source truth, '
                        'composition or scientific acceptance'})
    summary = {'kind': 'audit-summary', 'cases': len(cases),
               'audited_prefixes': audited,
               'strict_staged_gap_prefixes': applied + refused,
               'disjunct_applied': applied, 'disjunct_refused_retained': refused,
               'violating_prefixes': violations,
               'uninspectable_cases': unverifiable,
               'premises': ['identical-typed-staged-objects',
                            'each-envelope-own-signature-and-payload-binding-valid',
                            'same-latest-successful-literal-stage-origin-event-index-and-action',
                            'staged-unchanged-since-origin-through-prefix',
                            'recomputed-row-equals-retained-row',
                            'rebuilt-ledger-equals-retained-incarnation_pairs',
                            'incarnation_pair_established_by_identity-false'],
               'recorded_not_required': ['both_sources_unattested',
                                         'empty-incarnation-ledger',
                                         'same_live_generation',
                                         'current-stage-freshness']}
    return {'status': status, 'observations': [summary] + witnesses,
            'limitations': limitations, 'audited_prefixes': audited}


def run_controls(cases, charge):
    """Adversarial controls: semantic deepcopy mutations of one real retained case.

    Every probe re-runs this module's own ``inspect_cases`` on a deepcopy; the
    supplied cases are never modified. ``detected`` means the audit refused to
    return ``supported``: ``counterexample`` is a semantic violation of the
    retained certificate claims, while ``unproved``/``not_applicable`` are
    evidence rejection. Neither is an original-domain counterexample, and an
    uninspectable outcome is never treated as a scientific counterexample.
    """
    labels = ['unmodified-retained-case-baseline',
              'forged-staged-signatures-both-sides',
              'staged-payload-detached-from-envelope',
              'nonidentical-staged-envelopes',
              'dropped-stage-origin-on-source',
              'invented-incarnation-pair',
              'detached-identity-proof-event',
              'identity-claims-incarnation-authority',
              'cross-case-identity-proof',
              'forged-retained-staged-rule',
              'dropped-trailing-prefix-row']

    def missing(reason, witness_case):
        return {'controls': [{'control': x, 'detected': None,
                              'missing_witness': reason} for x in labels],
                'reachable_identity_witness': False, 'witness_case': witness_case}

    charge.take(1)
    target = None
    if isinstance(cases, (list, tuple)):
        for candidate in cases:
            if not isinstance(candidate, dict):
                continue
            for position, row in enumerate(candidate.get('prefixes') or ()):
                if (type(row) is dict and row.get('staged_rule') == IDENTITY
                        and type(row.get('identity_proof')) is dict):
                    target = (candidate, position, row)
                    break
            if target:
                break
    if target is None:
        return missing('no reachable original-object-identity prefix', None)
    case, prefix, row = target
    try:
        index = row['identity_proof']['source_origin']['event_index']
        if type(index) is not int or not 0 <= index < len(case['source']['events']):
            raise KeyError('stage-origin event index out of range')
    except AUDIT_ERRORS:
        return missing('retained identity proof lacks typed origin coordinates',
                       case.get('case'))
    charge.take(1)
    try:
        staged = frozen.restore(case['source'])[prefix]['staged']
        if type(staged) is not tuple or len(staged) != 2 \
                or type(staged[0]) is not d.q.Envelope:
            raise ValueError('no staged object at the witness prefix')
        generation = staged[0].source_generation
    except AUDIT_ERRORS as error:
        return missing('claimed witness does not replay: ' + str(error)[:120],
                       case.get('case'))

    results = []
    kind = {'counterexample': 'semantic-violation',
            'unproved': 'evidence-unverifiable',
            'not_applicable': 'scope-removed', 'supported': 'undetected'}

    def probe(label, mutate, expected=True):
        charge.take(1)
        mutated = copy.deepcopy(case)
        mutate(mutated)
        outcome = inspect_cases([mutated], charge)
        status = outcome['status']
        detected = status != 'supported'
        results.append({'control': label, 'detected': detected,
                        'expected_detected': expected,
                        'consistent': detected == expected,
                        'observed_status': status, 'detection_kind': kind[status],
                        'audited_prefixes': outcome['audited_prefixes'],
                        'note': 'semantic deepcopy; outer event hashes retained'})

    def put_staged(mutated, side, value):
        patch = mutated[side]['events'][index]['patch']
        if side == 'adapter':
            patch.setdefault('core', {})['staged'] = value
        else:
            patch['staged'] = value

    def both(mutate_value):
        def apply(mutated):
            for side in ('source', 'adapter'):
                put_staged(mutated, side, mutate_value(staged))
        return apply

    probe(labels[0], lambda m: None, expected=False)
    probe(labels[1], both(lambda v: (v[0]._replace(signature='0' * 64), v[1])))
    probe(labels[2], both(lambda v: (v[0], v[1] + '-mutated')))
    probe(labels[3], lambda m: put_staged(m, 'adapter',
          (staged[0]._replace(generation='forged-generation'), staged[1])))
    probe(labels[4], lambda m: m['source']['events'][index]
          .update(action='not-stage@' + str(index)))
    probe(labels[5], lambda m: m['incarnation_pairs'].append(
        {'source': generation, 'target': generation, 'reason': 'invented',
         'source_event': 0, 'target_event': 0}))
    probe(labels[6], lambda m: m['prefixes'][prefix]['identity_proof']
          ['source_origin'].update(event_index=prefix))
    probe(labels[7], lambda m: m['prefixes'][prefix]
          .update(incarnation_pair_established_by_identity=True))
    probe(labels[8], lambda m: m['prefixes'][prefix]['identity_proof']
          .update(case='cross-case-forgery'))
    probe(labels[9], lambda m: m['prefixes'][prefix].update(staged_rule='strict'))
    probe(labels[10], lambda m: m['prefixes'].pop())

    return {'controls': results, 'reachable_identity_witness': True,
            'witness_case': case['case'], 'witness_prefix': prefix,
            'discriminating': all(entry['consistent'] for entry in results),
            'mutations': 'deepcopies of the supplied typed case only; supplied '
                         'cases are unmodified; a detected mutation is a '
                         'retained-evidence violation or evidence rejection, '
                         'never an original-domain counterexample, and an '
                         'uninspectable outcome is not a scientific '
                         'counterexample'}
