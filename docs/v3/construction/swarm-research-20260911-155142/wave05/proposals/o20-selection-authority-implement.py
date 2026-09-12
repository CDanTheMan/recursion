"""Bounded retained-certificate check o20: staged equality is not authority.

Obligation: for `selected`, `publication_revision`, `publication_store`,
`publication_receipts` and the `selected_source` authority link, distinguish
staged-object equality -- including the batch-07 `original-object-identity`
disjunct -- from valid selected authority backed by the durable receipt chain.
For every inspected prefix of every supplied restored case the check
derives expected authority facts from the retained fields themselves and keeps
a falsifiable (expected, observed) witness per predicate. Reachability is
exactly the restored prefixes of the supplied cases; every visible refusal
must leave each authority field unchanged; staged identity is admitted only as
object identity and never as selection authority.

This module executes no reducer and calls no boundary helper. All
representation -- typed encoding, canonical digests, envelope/receipt
validation, incarnation-pair field views, pair advancement and typed trace
restoration -- is taken unchanged from the original audit/semantic sources:
  cut-publication/q_audit.py invariant(): revision == len(receipts), unique
    request identity, exact parent lineage, immutable receipt identity,
    selected == receipts[-1][0] retained in publication_store, no retired
    generation resurrected in the store.
  batch-05/semantic.py signed/own_receipt/pair_envelope/field_view/advance/
    typed/exact/digest; a `staged` strict gap is the documented unpaired-
    incarnation phenomenon, not an authority defect.
  batch-06/adapter_traces.py restore/core_view; journal EXTRA fields must
    equal the source ledger exactly.
  batch-07/identity.py + identity_audit.py staged identity proof shape;
    incarnation_pair_established_by_identity is always False.
  s_inclusive.py/s_audit.py/a_inclusive.py/a_audit.py: staged_source written
    only at stage, selected_source written only on commit, attestation triple
    (captured generation, captured revision, cut name).
  wave04/review-defects.json control "staged identity misused as selected
    authority"; q_inclusive.py commit patch fixes receipt/store/selected.

Finite audit accounting: charge.take(1) is consumed before each inspected
case prefix and every repetition counts; `audited_prefixes` reports only
prefixes whose inspection completed. A charge refusal truncates the audit and
forces 'unproved' unless a failure was already retained. No status here is a
global theorem or an accepted scientific PASS.
"""
import hashlib
import hmac
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-06'))
import semantic as r
import adapter_traces as t

JOURNAL_FIELDS = tuple(r.s.EXTRA) + ('source_generation',)
JOURNAL_ONLY = ('attestation', 'staged_source', 'selected_source', 'source_revision')
OBLIGATION_FIELDS = ('selected', 'publication_revision', 'publication_store',
                     'publication_receipts', 'publication_reply', 'staged',
                     'source_generation', 'retired_cuts')
REFUSAL_STABLE = ('selected', 'publication_revision', 'publication_store',
                  'publication_receipts', 'publication_reply', 'staged',
                  'attestation', 'staged_source', 'selected_source')
CASE_KEYS = ('case', 'unit', 'outcome', 'source', 'adapter', 'rows',
             'prefixes', 'incarnation_pairs')
MAX_FAILURES = 12


def _signature(env):
    body = json.dumps(tuple(env)[:-1], sort_keys=True, separators=(',', ':')).encode()
    return hmac.compare_digest(env.signature,
                               hmac.new(r.q.TEST_KEY, body, hashlib.sha256).hexdigest())


def _stored_valid(env, raw):
    """Original retained-object validity: envelope, payload binding, signature."""
    if type(env) is not r.q.Envelope:
        return False
    try:
        r.qa.checked_payload(env, raw)
    except (ValueError, KeyError, TypeError, IndexError):
        return False
    return _signature(env)


def _pred(name, expected, observed, ok):
    return {'predicate': name, 'expected': r.typed(expected),
            'observed': r.typed(observed), 'ok': bool(ok)}


def _adapter_view(state):
    view = dict(state['core'])
    for key in JOURNAL_ONLY:
        view[key] = state['journal'].get(key)
    return view


def _authority(view):
    """Expected-vs-observed authority predicates over one flat state view."""
    sel, recs = view.get('selected'), view.get('publication_receipts')
    store, reply = view.get('publication_store'), view.get('publication_reply')
    rev, retired = view.get('publication_revision'), view.get('retired_cuts') or ()
    staged, ssrc = view.get('staged'), view.get('selected_source')
    well = (type(recs) is tuple and all(type(x) is tuple and len(x) == 2
                                      and type(x[0]) is r.q.Envelope for x in recs))
    out = [_pred('revision_equals_receipt_count', len(recs) if well else 'malformed',
                 rev, well and type(rev) is int and rev == len(recs)),
           _pred('selected_iff_receipts', bool(recs), bool(sel),
                 bool(sel) == bool(recs))]
    last = recs[-1][0] if well and recs else ()
    out.append(_pred('selected_is_last_receipt', last, sel,
                     not recs or r.exact(sel, last)))
    member = bool(sel) and type(store) is tuple and any(
        type(x) is tuple and len(x) == 2 and r.exact(x[0], sel) for x in store)
    out.append(_pred('selected_retained_in_store', 'member' if sel else 'vacuous',
                     member if sel else 'vacuous', not sel or member))
    own = well and bool(recs) and r.own_receipt(sel, recs[-1][1])
    out.append(_pred('selected_signed_own_receipt', 'signed+own' if sel else 'vacuous',
                     [r.signed(sel), own] if sel else 'vacuous',
                     not sel or (r.signed(sel) and own)))
    prev, bad, requests = '', None, []
    if well:
        for i, (env, rec) in enumerate(recs):
            requests.append(env.request)
            want = (env.request, r.digest(env), i + 1, env.generation, env.content)
            if env.expected_revision != i or env.parent != prev or not r.exact(rec, want):
                bad = i
                break
            prev = env.generation
    out += [_pred('receipt_lineage_identity', 'chain-0..n-1', bad,
                  well and bad is None),
            _pred('unique_request_identity', len(requests), len(set(requests)),
                  well and len(set(requests)) == len(requests))]
    bad_store = None
    if type(store) is tuple:
        for i, row in enumerate(store):
            env, raw = row if type(row) is tuple and len(row) == 2 else (None, None)
            if env is None or not _stored_valid(env, raw) or env.generation in retired:
                bad_store = i
                break
    out.append(_pred('store_payloads_valid_unretired', 'all-valid', bad_store,
                     type(store) is tuple and bad_store is None))
    durable = not reply or (well and any(r.exact(x[1], reply) for x in recs))
    out.append(_pred('reply_backed_by_durable_receipt', 'durable-or-empty', reply,
                     durable))
    if sel:
        link = (type(ssrc) is tuple and len(ssrc) == 3 and r.token(ssrc[0])
                and type(ssrc[1]) is int and ssrc[1] >= 0
                and ssrc[2] == getattr(sel, 'cut', None))
        out.append(_pred('selected_source_binds_selected_cut',
                         ('token', 'revision>=0', getattr(sel, 'cut', None)),
                         ssrc, link))
    else:
        out.append(_pred('selected_source_binds_selected_cut', 'empty', ssrc,
                         not ssrc))
    if staged:
        valid = (type(staged) is tuple and len(staged) == 2
                 and _stored_valid(staged[0], staged[1]))
        out.append(_pred('staged_object_self_valid', True, valid, valid))
    return out


def _identity_check(case, prow, ss, aa, i):
    """Re-bind a retained original-object-identity claim to the actual states."""
    proof = prow.get('identity_proof') or {}
    so, ao = proof.get('source_origin') or {}, proof.get('adapter_origin') or {}
    idx = so.get('event_index')
    left, right = ss[i].get('staged'), aa[i]['core'].get('staged')
    origin_ok = bool(type(idx) is int and 0 <= idx < len(case['source']['events'])
                     and case['source']['events'][idx].get('action', '').split('@')[0]
                     == 'stage' and ss[idx + 1].get('decision') == 'stage:ok')
    checks = {'prefix_matches': proof.get('prefix') == i,
              'same_event_index': type(idx) is int and idx == ao.get('event_index'),
              'same_action': so.get('action') is not None
              and so.get('action') == ao.get('action'),
              'origin_was_stage_ok': origin_ok,
              'no_authority_created': prow.get(
                  'incarnation_pair_established_by_identity') is False,
              'staged_exact': r.exact(left, right),
              'staged_valid': _stored_valid(*left) if type(left) is tuple
              and len(left) == 2 else False,
              'staged_valid_target': _stored_valid(*right) if type(right) is tuple
              and len(right) == 2 else False,
              'source_state_bound': proof.get('source_state_sha256') == r.digest(ss[i]),
              'adapter_state_bound': proof.get('adapter_state_sha256') == r.digest(aa[i]),
              'source_prefix_bound': proof.get('source_prefix_sha256')
              == r.digest(case['source']['events'][:i]),
              'adapter_prefix_bound': proof.get('adapter_prefix_sha256')
              == r.digest(case['adapter']['events'][:i])}
    return _pred('identity_proof_rebinds_actual_states', 'all-true', checks,
                 all(checks.values()))


def _prefix_audit(case, ss, aa, pairs, i):
    """All expected/observed predicates for restored prefix i of one case."""
    src, adp, prow = ss[i], aa[i], case['prefixes'][i]
    results = [('source', p) for p in _authority(src)]
    results += [('adapter', p) for p in _authority(_adapter_view(adp))]
    diffj = [k for k in JOURNAL_FIELDS if not r.exact(src.get(k), adp['journal'].get(k))]
    results.append(('adapter-journal', _pred('journal_fields_exact', [], diffj, not diffj)))
    try:
        diffc = [k for k in OBLIGATION_FIELDS
                 if r.field_view(src, k, 'source', pairs)
                 != r.field_view(adp['core'], k, 'target', pairs)]
    except (ValueError, KeyError, IndexError, TypeError) as error:
        diffc = ['field-view-error:' + str(error)]
    others = [k for k in diffc if k != 'staged']
    results.append(('adapter-core', _pred('obligation_fields_related', [], others,
                                          not others)))
    rule = prow.get('staged_rule')
    if 'staged' in diffc:
        results.append(('adapter-core', _pred('staged_gap_is_identity_only',
                        'original-object-identity', rule,
                        rule == 'original-object-identity')))
    elif rule == 'original-object-identity':
        results.append(('adapter-core', _pred('identity_rule_without_strict_gap',
                        'staged-differs', rule, False)))
    if rule == 'original-object-identity':
        results.append(('identity', _identity_check(case, prow, ss, aa, i)))
    results.append(('pairs', _pred('pairs_digest_matches_retained_row',
                                   prow.get('pairs_sha256'), r.digest(pairs),
                                   prow.get('pairs_sha256') == r.digest(pairs))))
    if i:
        results.append(('adapter', _pred('visible_decisions_exact',
                        src.get('decision'), adp.get('decision'),
                        r.exact(src.get('decision'), adp.get('decision')))))
        for side, cur, prv in (('source', src, ss[i - 1]),
                               ('adapter', _adapter_view(adp), _adapter_view(aa[i - 1]))):
            reason = str(cur.get('decision', '')).partition(':')[2]
            if reason and reason not in ('ok', 'duplicate'):
                changed = [k for k in REFUSAL_STABLE if not r.exact(cur.get(k), prv.get(k))]
                results.append((side, _pred('refusal_preserves_authority_fields',
                                'unchanged', changed, not changed)))
    return results


def _inspect_case(case, charge):
    ss = t.restore(case['source'])
    aa = t.restore(case['adapter'])
    actions = case['source']['actions']
    rows, prows = case['rows'], case['prefixes']
    if not (len(ss) == len(aa) == len(actions) + 1 == len(prows)
            and r.exact(actions, case['adapter']['actions'])):
        raise ValueError('restored prefix cardinality or action mismatch')
    stats = dict(selected_source_side=0, selected_adapter_side=0, staged=0,
                 staged_identity=0, staged_without_selection=0,
                 staged_equals_selected=0, refusals=0)
    obs = {'case': case.get('case'), 'prefixes': 0, 'failure_count': 0,
           'failures': [], 'witnesses': stats}
    pairs = []
    for i in range(len(ss)):
        try:
            charge.take(1)
        except Exception as error:
            obs['charge_refused'] = str(error)
            return obs
        if i:
            j = i - 1
            binding = r.advance(pairs, ss[j], t.core_view(aa[j]), ss[i],
                                t.core_view(aa[i]), actions[j], actions[j], j, j)
            kept = rows[j].get('binding') if j < len(rows) else 'missing-row'
            if not r.exact(kept, binding):
                obs['failure_count'] += 1
                obs['failures'].append({'prefix': i, 'side': 'pairs',
                    'predicate': 'binding_matches_retained_row',
                    'expected': r.typed(kept), 'observed': r.typed(binding),
                    'ok': False})
        for side, pred in _prefix_audit(case, ss, aa, pairs, i):
            if not pred['ok']:
                obs['failure_count'] += 1
                if len(obs['failures']) < MAX_FAILURES:
                    obs['failures'].append(dict(prefix=i, side=side, **pred))
        stats['selected_source_side'] += bool(ss[i].get('selected'))
        stats['selected_adapter_side'] += bool(aa[i]['core'].get('selected'))
        stats['staged'] += bool(ss[i].get('staged') or aa[i]['core'].get('staged'))
        stats['staged_without_selection'] += bool(ss[i].get('staged')
                                                  and not ss[i].get('selected'))
        stats['staged_equals_selected'] += bool(
            ss[i].get('staged') and ss[i].get('selected')
            and r.exact(ss[i]['staged'][0], ss[i]['selected']))
        stats['staged_identity'] += prows[i].get('staged_rule') == 'original-object-identity'
        stats['refusals'] += bool(i and str(ss[i].get('decision', '')).partition(':')[2]
                                  not in ('', 'ok', 'duplicate'))
        obs['prefixes'] += 1
    if not r.exact(pairs, case.get('incarnation_pairs')):
        obs['failure_count'] += 1
        obs['failures'].append({'prefix': len(ss) - 1, 'side': 'pairs',
            'predicate': 'incarnation_pairs_match_retained',
            'expected': r.typed(case.get('incarnation_pairs')),
            'observed': r.typed(pairs), 'ok': False})
    obs['decisions'] = sorted({str(x.get('decision')) for x in ss}
                              | {str(x.get('decision')) for x in aa})[:24]
    return obs


def inspect_cases(cases, charge):
    """Audit restored retained cases for staged-vs-selected authority.

    cases: list of typed case objects produced by c.run_history and restored
    through c.artifact/q_artifact; charge: budget whose take(1) is consumed
    once per inspected prefix, before that prefix's fields are read.
    """
    result = {'status': 'unproved', 'observations': [], 'audited_prefixes': 0,
              'limitations': [
                  'only the supplied retained case prefixes were inspected; no '
                  'all-order reachability and no reducer/model execution',
                  "'supported' is a finite-corpus observation, never a global "
                  'theorem or an accepted scientific PASS',
                  'selected_source is checked for (incarnation token, revision, '
                  'cut name) shape plus selected.cut equality; commit-time '
                  'ancestry is witnessed by exact journal equality and refusal '
                  'preservation, not by re-executing commits',
                  'staged identity is re-verified against restored states and '
                  'admits object identity only; it never creates authority']}
    if type(cases) is not list or not cases:
        result['status'] = 'not_applicable'
        result['limitations'].append('no retained case objects supplied')
        return result
    failures = selected_wit = staged_wit = inspected = 0
    truncated = False
    for case in cases:
        if type(case) is not dict or any(k not in case for k in CASE_KEYS):
            failures += 1
            result['observations'].append({'case': repr(case)[:96],
                'error': 'not a retained restored case object'})
            continue
        try:
            obs = _inspect_case(case, charge)
        except (ValueError, KeyError, IndexError, TypeError, AttributeError) as e:
            failures += 1
            result['observations'].append({'case': case.get('case'),
                'error': 'retained certificate failed inspection: ' + str(e)})
            continue
        inspected += 1
        truncated = truncated or 'charge_refused' in obs
        result['audited_prefixes'] += obs['prefixes']
        failures += obs['failure_count']
        selected_wit += min(obs['witnesses']['selected_source_side'],
                            obs['witnesses']['selected_adapter_side'])
        staged_wit += (obs['witnesses']['staged_without_selection']
                       + obs['witnesses']['staged_identity'])
        result['observations'].append(obs)
        if truncated:
            break
    if truncated:
        result['limitations'].append('audit truncated by charge refusal')
    if failures:
        result['status'] = 'counterexample'
    elif not inspected:
        result['status'] = 'not_applicable'
    elif not truncated and selected_wit and staged_wit:
        result['status'] = 'supported'
    return result
