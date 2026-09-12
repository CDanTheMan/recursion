"""Bounded retained-certificate packet for obligation o15 (v2 repair; parent
goal-recursion-v2-execution-fabric): the exact scope in which the additive
staged disjunct excuses a strict ``staged`` difference for typed-identical,
individually valid staged originals with one audited shared stage-origin
event, while never creating incarnation pairs or authority.

Public API ``inspect_cases(cases, charge)`` / ``run_controls(cases, charge)``;
both return JSON-safe dicts. ``cases`` are typed retained case objects in the
unchanged runner's ``check.run_history``/``audit_case`` shape (or losslessly
restored certificates). No reducer, guard or model step runs here: states come
only from the unchanged digest-bound ``adapter_traces.restore`` replay, the
incarnation ledger is rebuilt only by the unchanged ``semantic.advance`` law,
transitions are re-audited by unchanged ``sc.check``/``audit.check``, and each
retained prefix row is checked by the unchanged ``identity.compare`` +
``identity_audit.check`` pair plus exact typed equality against the retained
row. Nothing from ``boundary.py`` is imported; it was a negative contamination
check only, never semantic ground truth for this obligation.

v2 repairs against reviews/proposal-grok-01/repair-o15.json:

A. Binding/path: originals bind lazily inside each charged public call
   (``_bind``); importing this file has no side effects and imports nothing.
   ``identity``/``identity_audit`` bind to exact batch-07 paths, ``frozen`` to
   exact batch-06 ``adapter_traces.py``, and the ``d``/``r`` aliases bind by
   basename under the cut-source-overnight tree to the cited
   ``a_domain.py``/``semantic.py`` originals. Every used surface is checked
   callable with compatible arity; a missing or divergent export raises
   ``_BindError`` -> ``unproved`` (never a counterexample), and a runtime
   ``AttributeError`` inside a prefix is uninspectable machinery, not a
   violation.
B. Chronology: the ledger snapshot precedes ``identity.compare`` and is
   verified only after ``identity_audit.check`` returns, so audit-side
   ledger/authority mutation cannot escape ``identity-created-authority``;
   the recomputed row is re-verified post-audit (``audit-mutated-relation-
   row``) and the post-``advance`` ledger after ``response``/``comparison``
   (``ledger-mutated-outside-advance``): the ledger is rebuilt only by
   ``semantic.advance``.
C. Charge: ``charge.take(1)`` also precedes the per-case initialization audit
   bundle and the once-per-call binding, matching the accounting below.
D. Observations: each staged-gap witness records all four
   ``recorded_not_required`` facts with matching keys;
   ``current_stage_freshness`` is the proxy ``origin_event_index ==
   prefix-1``. None is ever a premise of the disjunct, which is decided
   solely by the unchanged identity originals (relation_non_narrowing: no
   empty names/pairs/equal generations/freshness as premises).
E. Controls: every probe declares ``intended_layer`` and ``detection_kind``;
   trace-patch forgeries are restore-layer digest rejections (evidence
   rejection, not relation-level semantics) while proof/staged-rule/row/
   ledger forgeries reach ``compare``/``check`` or the retained-row
   recomputation; four relation-row probes (binding, Q invocation, response,
   strict baseline) exercise the chronological row premises. Status priority:
   counterexample > unproved (any uninspectable case, incl. mixed batches) >
   supported > not_applicable.

Retained anchors: ``parents[4]`` root; nine-arg ``semantic.advance``; verbatim
``adapter_traces.restore`` premises incl. ``q_profile == subprofile``; literal
chronological row/Q/relation premises per audit_case; exact typed schemas with
``len(rows) == len(actions)``, ``len(prefixes) == len(actions)+1`` and equal
restored state counts; interop via this module's own ``inspect_cases`` with
``detected == (status != 'supported')`` and ``detection_kind`` split.

Unit accounting: ``charge.take(1)`` BEFORE the per-call binding, each case
schema, each of the two restores, the initialization audit bundle, each
(case, prefix) audit unit, the witness scan, the witness restore and each
probe (which then re-charges its own nested inspection). A full
``inspect_cases`` call on one depth-d case draws ``6 + d`` units;
``run_controls`` draws ``3 + len(CONTROLS)`` outer units plus each probe's
nested call for a maximum total draw of ``3 + len(CONTROLS) * (7 + d)``;
both calls report ``precharged_units`` (this call's own units only;
per-probe nested draws appear as ``nested_units`` on each control entry).
A refusal propagates: nothing is restored, audited, mutated or repeated
uncharged.

Statuses: ``counterexample`` on recomputation disagreement or audit
rejection; ``supported`` only when every supplied case is inspectable, no
violation is found and >=1 audited prefix applies the disjunct; ``unproved``
for uninspectable evidence, missing/divergent originals, refused audits or
refusal-only coverage; ``not_applicable`` when nothing is auditable or no
audited prefix lists ``staged`` among strict differences. Bounded certificate
audit only: not an all-order theorem and not scientific acceptance.
"""
import copy
import inspect as _inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TREE = 'experiments/v3/cut-source-overnight'
IDENTITY = 'original-object-identity'
KEEP = 16
AUDIT_ERRORS = (ValueError, KeyError, IndexError, TypeError, AttributeError)
TRACE_KEYS = {'side', 'initial', 'profile', 'actions', 'events'}
EVENT_KEYS = {'action', 'before_sha256', 'after_sha256', 'patch'}
CASE_KEYS = {'case', 'unit', 'outcome', 'source', 'adapter', 'rows', 'prefixes',
             'incarnation_pairs'}
ROW_KEYS = {'index', 'source_action', 'adapter_action', 'source_sha256',
            'adapter_sha256', 'pairs_sha256', 'prestate_related', 'state_related',
            'responses_related', 'differing_common_fields', 'q_invoked',
            'differing_journal_fields', 'source_observation', 'adapter_observation',
            'justification', 'binding'}
PREFIX_ROW_KEYS = {'prefix', 'strict_differing_common_fields', 'related',
                   'differing_common_fields', 'differing_journal_fields',
                   'strict_related', 'staged_rule', 'identity_proof',
                   'pairs_sha256', 'incarnation_pair_established_by_identity'}
PAIR_KEYS = {'source', 'target', 'reason', 'source_event', 'target_event'}

relation = identity_audit = d = r = frozen = None
_BOUND = False


class _BindError(Exception):
    """An obligation-cited original is absent or divergent; never a counterexample."""


class _Unreadable(Exception):
    """Retained evidence cannot be read or audited; never a counterexample."""


def _arity(function, count, name):
    """Fail-closed positional arity check on one obligation-cited surface."""
    try:
        params = tuple(_inspect.signature(function).parameters.values())
    except (TypeError, ValueError):
        raise _BindError('original surface not introspectable: ' + name)
    pos = [p for p in params if p.kind in (_inspect.Parameter.POSITIONAL_ONLY,
                                           _inspect.Parameter.POSITIONAL_OR_KEYWORD)]
    need = [p for p in pos if p.default is _inspect.Parameter.empty]
    varargs = any(p.kind is _inspect.Parameter.VAR_POSITIONAL for p in params)
    if len(need) > count or (not varargs and len(pos) < count):
        raise _BindError('original ' + name + ' cannot take ' + str(count) + ' arguments')


def _bind():
    """Import and path-bind the unchanged o15 originals once; failure -> unproved."""
    global relation, identity_audit, d, r, frozen, _BOUND
    if _BOUND:
        return
    tree = (ROOT / TREE).resolve()
    batch07 = str(tree / 'batch-07')
    if not (tree / 'batch-07' / 'identity.py').is_file():
        raise _BindError('original batch-07 identity.py absent')
    added = batch07 not in sys.path
    if added:
        sys.path.insert(0, batch07)
    try:
        import identity as _identity
        import identity_audit as _audit_mod
    except Exception as error:
        raise _BindError('original identity import failed: ' + str(error)[:140])
    finally:
        if added and batch07 in sys.path:
            sys.path.remove(batch07)
    try:
        _d, _r, _frozen = _identity.d, _identity.r, _identity.frozen
    except AttributeError as error:
        raise _BindError('identity lacks d/r/frozen exports') from error
    for module, path in ((_identity, tree / 'batch-07' / 'identity.py'),
                         (_audit_mod, tree / 'batch-07' / 'identity_audit.py'),
                         (_frozen, tree / 'batch-06' / 'adapter_traces.py')):
        if Path(getattr(module, '__file__', '')).resolve() != path:
            raise _BindError('original module not bound at ' + path.name)
    for module, name in ((_d, 'a_domain.py'), (_r, 'semantic.py')):
        path = Path(getattr(module, '__file__', '')).resolve()
        if path.name != name or not path.is_relative_to(tree):
            raise _BindError('original ' + name + ' not bound under ' + TREE)
    try:
        surfaces = (
            (_identity.compare, 5, 'identity.compare'),
            (_audit_mod.check, 6, 'identity_audit.check'),
            (_r.advance, 9, 'semantic.advance'), (_r.token, 1, 'semantic.token'),
            (_r.typed, 1, 'semantic.typed'), (_d.exact, 2, 'a_domain.exact'),
            (_d.digest, 1, 'a_domain.digest'),
            (_d.justification, 2, 'a_domain.justification'),
            (_frozen.restore, 1, 'adapter_traces.restore'),
            (_frozen.core_view, 1, 'adapter_traces.core_view'),
            (_frozen.response, 4, 'adapter_traces.response'),
            (_frozen.comparison, 9, 'adapter_traces.comparison'),
            (_frozen.sc.check, 6, 'sc.check'),
            (_frozen.sc.initialization, 2, 'sc.initialization'),
            (_frozen.audit.check, 6, 'audit.check'),
            (_frozen.audit.initialization, 2, 'audit.initialization'))
        envelope = _d.q.Envelope
    except AttributeError as error:
        raise _BindError('missing original surface: ' + str(error)[:140])
    for function, count, name in surfaces:
        if not callable(function):
            raise _BindError('original surface not callable: ' + name)
        _arity(function, count, name)
    if type(envelope) is not type:
        raise _BindError('a_domain.q.Envelope is not a type')
    relation, identity_audit, d, r, frozen = _identity, _audit_mod, _d, _r, _frozen
    _BOUND = True


def _require_schema(case):
    """Exact typed trace/case schema; any failure is uninspectable evidence."""
    if type(case) is not dict or set(case) != CASE_KEYS \
            or type(case['case']) is not str or type(case['unit']) is not str \
            or type(case['outcome']) is not int:
        raise _Unreadable('case keys/label/unit/outcome outside the typed schema')
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
    bad_row = lambda x: not (type(x) is dict and set(x) == ROW_KEYS
        and type(x['index']) is int and type(x['q_invoked']) is bool
        and type(x['source_action']) is type(x['adapter_action']) is str
        and type(x['responses_related']) is type(x['prestate_related']) is bool
        and type(x['state_related']) is bool and type(x['pairs_sha256']) is str)
    bad_prefix = lambda x: not (type(x) is dict and set(x) == PREFIX_ROW_KEYS
        and type(x['prefix']) is int and type(x['staged_rule']) is str
        and type(x['strict_related']) is type(x['related']) is bool
        and type(x['incarnation_pair_established_by_identity']) is bool
        and (x['identity_proof'] is None or type(x['identity_proof']) is dict))
    if type(rows) is not list or len(rows) != depth or any(bad_row(x) for x in rows):
        raise _Unreadable('comparison rows missing or outside the typed schema')
    if type(prefixes) is not list or len(prefixes) != depth + 1 \
            or any(bad_prefix(x) for x in prefixes):
        raise _Unreadable('prefix rows missing or outside the typed schema')
    pairs = case['incarnation_pairs']
    if type(pairs) is not list or any(
            type(p) is not dict or set(p) != PAIR_KEYS or not r.token(p['source'])
            or not r.token(p['target']) or type(p['source_event']) is not int
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
        after_advance = copy.deepcopy(pairs)
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
        if not d.exact(after_advance, pairs):
            bad.append('ledger-mutated-outside-advance')
        if not d.exact(expected_row, row):
            bad.append('comparison-row-differs')
    saved = copy.deepcopy(pairs)
    item = relation.compare(case, source_states, adapter_states, prefix, pairs)
    item_before_audit = copy.deepcopy(item)
    identity_audit.check(item, case, source_states, adapter_states, prefix, pairs)
    if not d.exact(saved, pairs):
        bad.append('identity-created-authority')
    if not d.exact(item_before_audit, item):
        bad.append('audit-mutated-relation-row')
    retained = case['prefixes'][prefix]
    if prefix and not (item['strict_related'] == row['state_related']
                       and prev_strict == row['prestate_related']):
        bad.append('strict-baseline-differs')
    if r.typed(retained) != r.typed(item):
        bad.append('prefix-row-differs')
    return item, bad


def _take(charge, tally):
    charge.take(1)
    tally[0] += 1


def inspect_cases(cases, charge):
    """Audit retained per-prefix relation rows; see the module docstring."""
    witnesses, limitations = [], []
    audited = applied = refused = unverifiable = violations = 0
    taken = [0]

    def note(entry):
        if len(witnesses) < KEEP:
            witnesses.append(entry)

    _take(charge, taken)
    try:
        _bind()
    except _BindError as error:
        return {'status': 'unproved', 'observations': [], 'audited_prefixes': 0,
                'precharged_units': taken[0], 'limitations': [
                {'scope': 'originals not bound: ' + str(error)[:160]}]}
    if not isinstance(cases, (list, tuple)):
        return {'status': 'unproved', 'observations': [], 'audited_prefixes': 0,
                'precharged_units': taken[0], 'limitations': [
                {'scope': 'cases is not a sequence; nothing inspectable'}]}
    for position, case in enumerate(cases):
        label = case['case'] if isinstance(case, dict) and type(case.get('case')) is str \
            else 'case-' + str(position)
        try:
            _take(charge, taken)
            _require_schema(case)
            _take(charge, taken)
            source_states = _restore(case['source'])
            _take(charge, taken)
            adapter_states = _restore(case['adapter'])
            if not (len(source_states) == len(adapter_states)
                    == len(case['source']['actions']) + 1):
                raise _Unreadable('restored state count differs from the action inventory')
            _take(charge, taken)
            frozen.sc.initialization(source_states[0], case['unit'])
            frozen.audit.initialization(adapter_states[0], case['unit'])
        except _Unreadable as error:
            unverifiable += 1
            limitations.append({'case': label, 'unproved_reason': str(error)[:160]})
            continue
        except AUDIT_ERRORS as error:
            unverifiable += 1
            limitations.append({'case': label, 'unproved_reason':
                                'initialization audit rejected: ' + str(error)[:140]})
            continue
        pairs, prev_strict, failed = [], None, False
        for prefix in range(len(source_states)):
            _take(charge, taken)
            audited += 1
            try:
                item, bad = _audit_prefix(case, source_states, adapter_states,
                                          pairs, prefix, prev_strict)
            except AttributeError as error:
                unverifiable += 1
                failed = True
                note({'kind': 'audit-machinery-unavailable', 'case': label,
                      'prefix': prefix, 'reason': str(error)[:160]})
                break
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
                try:
                    proof = item['identity_proof']
                    org = proof.get('source_origin') if type(proof) is dict else None
                    oi = org.get('event_index') if type(org) is dict else None
                    entry = {
                        'kind': 'staged-disjunct-applied'
                        if item['staged_rule'] == IDENTITY else 'staged-disjunct-refused',
                        'case': label, 'prefix': prefix, 'origin_event_index': oi,
                        'origin_action': org.get('action') if type(org) is dict else None,
                        'source_staged_sha256': d.digest(source_states[prefix]['staged']),
                        'adapter_staged_sha256':
                        d.digest(adapter_states[prefix]['core']['staged']),
                        'both_sources_unattested': not source_states[prefix]['source_name']
                        and not adapter_states[prefix]['core']['source_name'],
                        'same_live_generation': d.exact(
                            source_states[prefix]['source_generation'],
                            adapter_states[prefix]['core']['source_generation']),
                        'empty_incarnation_ledger': not pairs,
                        'current_stage_freshness':
                        oi == prefix - 1 if type(oi) is int else None,
                        'pairs_at_prefix': len(pairs)}
                except AUDIT_ERRORS as error:
                    violations += 1
                    failed = True
                    note({'kind': 'scope-violation', 'case': label, 'prefix': prefix,
                          'violations': ['staged-observation-fields-missing'],
                          'reason': str(error)[:140]})
                    break
                if item['staged_rule'] == IDENTITY:
                    applied += 1
                else:
                    refused += 1
                note(entry)
            prev_strict = item['strict_related']
        if not failed and not d.exact(pairs, case['incarnation_pairs']):
            violations += 1
            note({'kind': 'ledger-tail-mismatch', 'case': label,
                  'rebuilt_pairs_sha256': d.digest(pairs),
                  'retained_pairs_sha256': d.digest(case['incarnation_pairs'])})

    if violations:
        status = 'counterexample'
    elif unverifiable:
        status = 'unproved'
        limitations.append({'scope': 'uninspectable supplied cases exist; a mixed '
                            'uninspectable+applied batch is never upgraded to supported'})
    elif applied:
        status = 'supported'
    elif refused:
        status = 'unproved'
        limitations.append({'scope': 'staged strict gaps were audited but no prefix '
                            'reached original-object-identity; no reachable witness'})
    else:
        status = 'not_applicable'
    limitations.append({'scope': 'bounded retained-certificate audit over supplied '
                        'histories only; no all-order reachability, source truth, '
                        'composition or scientific acceptance'})
    summary = {'kind': 'audit-summary', 'cases': len(cases),
               'audited_prefixes': audited,
               'strict_staged_gap_prefixes': applied + refused,
               'disjunct_applied': applied, 'disjunct_refused_retained': refused,
               'violating_prefixes': violations, 'uninspectable_cases': unverifiable,
               'premises': ['identical-typed-staged-objects',
                            'each-envelope-own-signature-and-payload-binding-valid',
                            'same-latest-successful-literal-stage-origin-event-index-and-action',
                            'staged-unchanged-since-origin-through-prefix',
                            'recomputed-row-equals-retained-row',
                            'rebuilt-ledger-equals-retained-incarnation_pairs',
                            'incarnation_pair_established_by_identity-false'],
               'recorded_not_required': ['both_sources_unattested',
                                         'empty_incarnation_ledger',
                                         'same_live_generation',
                                         'current_stage_freshness']}
    return {'status': status, 'observations': [summary] + witnesses,
            'limitations': limitations, 'audited_prefixes': audited,
            'precharged_units': taken[0]}


CONTROLS = (
    ('unmodified-retained-case-baseline', 'baseline'),
    ('forged-staged-signatures-both-sides', 'restore'),
    ('staged-payload-detached-from-envelope', 'restore'),
    ('nonidentical-staged-envelopes', 'restore'),
    ('dropped-stage-origin-on-source', 'restore'),
    ('invented-incarnation-pair', 'ledger-or-schema'),
    ('detached-identity-proof-event', 'relation-row'),
    ('identity-claims-incarnation-authority', 'relation-row'),
    ('cross-case-identity-proof', 'relation-row'),
    ('forged-retained-staged-rule', 'relation-row'),
    ('forged-causal-binding-row', 'relation-row'),
    ('forged-q-invocation-row', 'relation-row'),
    ('forged-response-relation-row', 'relation-row'),
    ('forged-strict-baseline-row', 'relation-row'),
    ('dropped-trailing-prefix-row', 'schema'), ('dropped-source-event', 'schema'))
LAYER_NOTE = {
    'baseline': 'unmodified deepcopy; must reach supported',
    'schema': 'typed retained-evidence schema rejects before any audit',
    'restore': 'digest-bound adapter_traces.restore rejects the forged trace first',
    'relation-row': 'retained row/prefix claims meet the compare/audit recomputation',
    'ledger-or-schema': 'pair rejected at the typed schema or the ledger-tail check'}


def run_controls(cases, charge):
    """Adversarial controls: semantic deepcopy mutations of one real retained case.

    Every probe re-runs this module's own ``inspect_cases`` on a deepcopy; the
    supplied cases are never modified. ``detected`` means the audit refused to
    return ``supported``: ``counterexample`` is a semantic violation of the
    retained certificate claims, while ``unproved``/``not_applicable`` are
    evidence rejection. Neither is an original-domain counterexample, and an
    uninspectable outcome is never treated as a scientific counterexample.
    """
    labels = [name for name, _ in CONTROLS]
    taken = [0]

    def missing(reason, witness_case):
        return {'controls': [{'control': x, 'detected': None,
                              'missing_witness': reason} for x in labels],
                'reachable_identity_witness': False, 'witness_case': witness_case,
                'precharged_units': taken[0]}

    _take(charge, taken)
    try:
        _bind()
    except _BindError as error:
        return missing('originals not bound: ' + str(error)[:120], None)
    _take(charge, taken)
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
        index0 = row['identity_proof']['source_origin']['event_index']
        if type(index0) is not int or not 0 <= index0 < len(case['source']['events']):
            raise KeyError('stage-origin event index out of range')
    except AUDIT_ERRORS:
        return missing('retained identity proof lacks typed origin coordinates',
                       case.get('case'))
    index = prefix - 1 if prefix else None
    _take(charge, taken)
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
    kind = {'counterexample': 'semantic-violation', 'unproved': 'evidence-unverifiable',
            'not_applicable': 'scope-removed', 'supported': 'undetected'}

    def unavailable(label, layer, expected, reason):
        results.append({'control': label, 'intended_layer': layer,
                        'expected_detected': expected, 'detected': None,
                        'consistent': None, 'observed_status': 'unavailable',
                        'detection_kind': 'missing-witness', 'audited_prefixes': 0,
                        'nested_units': 0, 'note': reason})

    def probe(position, mutate, expected=True, needs_row=False):
        label, layer = CONTROLS[position]
        if needs_row and index is None:
            return unavailable(label, layer, expected,
                               'requires a witness prefix above 0')
        _take(charge, taken)
        mutated = copy.deepcopy(case)
        try:
            mutate(mutated)
        except AUDIT_ERRORS as error:
            return unavailable(label, layer, expected,
                               'mutation not reachable: ' + str(error)[:120])
        outcome = inspect_cases([mutated], charge)
        status = outcome['status']
        detected = status != 'supported'
        results.append({'control': label, 'intended_layer': layer,
                        'expected_detected': expected, 'detected': detected,
                        'consistent': detected == expected, 'observed_status': status,
                        'detection_kind': kind[status],
                        'audited_prefixes': outcome['audited_prefixes'],
                        'nested_units': outcome['precharged_units'],
                        'note': LAYER_NOTE[layer]})

    def put_staged(mutated, side, value):
        patch = mutated[side]['events'][index0]['patch']
        if side == 'adapter':
            patch.setdefault('core', {})['staged'] = value
        else:
            patch['staged'] = value

    def both(mutate_value):
        def apply(mutated):
            for side in ('source', 'adapter'):
                put_staged(mutated, side, mutate_value(staged))
        return apply

    def rowedit(field, value_fn):
        def apply(mutated):
            mutated['rows'][index][field] = value_fn(mutated['rows'][index][field])
        return apply

    probe(0, lambda m: None, expected=False)
    probe(1, both(lambda v: (v[0]._replace(signature='0' * 64), v[1])))
    probe(2, both(lambda v: (v[0], v[1] + '-mutated')))
    probe(3, lambda m: put_staged(m, 'adapter',
          (staged[0]._replace(generation='forged-generation'), staged[1])))
    probe(4, lambda m: m['source']['events'][index0].update(
          action='not-stage@' + str(index0)))
    probe(5, lambda m: m['incarnation_pairs'].append(
        {'source': generation, 'target': generation, 'reason': 'invented',
         'source_event': 0, 'target_event': 0}))
    probe(6, lambda m: m['prefixes'][prefix]['identity_proof']
          ['source_origin'].update(event_index=prefix))
    probe(7, lambda m: m['prefixes'][prefix]
          .update(incarnation_pair_established_by_identity=True))
    probe(8, lambda m: m['prefixes'][prefix]['identity_proof']
          .update(case='cross-case-forgery'))
    probe(9, lambda m: m['prefixes'][prefix].update(staged_rule='strict'))
    probe(10, rowedit('binding', lambda v: {'forged-binding': True}), needs_row=True)
    probe(11, rowedit('q_invoked', lambda v: not v), needs_row=True)
    probe(12, rowedit('responses_related', lambda v: not v), needs_row=True)
    probe(13, rowedit('state_related', lambda v: not v), needs_row=True)
    probe(14, lambda m: m['prefixes'].pop())
    probe(15, lambda m: m['source']['events'].pop(index0))

    return {'controls': results, 'reachable_identity_witness': True,
            'witness_case': case['case'], 'witness_prefix': prefix,
            'discriminating': all(entry['consistent'] for entry in results),
            'complete_coverage': all(entry['detected'] is not None for entry in results),
            'precharged_units': taken[0],
            'mutations': 'deepcopies of the supplied typed case only; supplied '
                         'cases are unmodified; a detected mutation is a '
                         'retained-evidence violation or evidence rejection, '
                         'never an original-domain counterexample, and an '
                         'uninspectable outcome is not a scientific '
                         'counterexample'}
