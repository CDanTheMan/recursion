"""Retained-certificate check for obligation o19-publication-duplicate:
publication duplicate/retry bypass and durable receipt/reply correspondence.

inspect_cases(cases, charge) audits typed c.run_history/c.artifact-restored
case objects only: no reducer, model or inventory enumeration is executed, no
boundary helper is imported, nothing outside the supplied cases is read.
Finite accounting: charge.take(1) is consumed once BEFORE each inspected case
prefix (all repetitions count); audited_prefixes equals consumed units.
Violation/refusal lists are capped so the audit itself stays finite.

Per charged prefix, on the source state and adapter core view: durable ledger
(revision == len(receipts), unique request ids, expected_revision/parent
lineage, receipt identity (env.request, sha256(env), index+1, env.generation,
env.content), non-empty reply backed by a retained receipt, selected committed
and store-retained, no retired-generation resurrection); each pub-* transition
(guard 'source-boundary-stale' -> 'wrong-caller' -> 'duplicate'/
'E-IDEMPOTENCY-CONFLICT' -> fresh chain): a 'duplicate' reply must equal the
retained receipt with ledger/revision/selected preserved and reads +1,
refusals mutate no publication field, fresh 'ok' commits append the exact
receipt becoming reply and selection; retained rows' decisions/replies and the
Q-invocation delta must match the replayed typed states.

Reachability is measured, not assumed: pub-verb inventories, retained-branch
entries and bypasses taken while the boundary was stale are counted per case;
if no case enters the retained branch the result is 'unproved' with that
evidence, never a theorem over all orders.

Source anchors (unchanged originals; representation reference only):
  cut-publication/q_audit.py - invariant() and check() retained-request
    ordering/receipt identity.  q_domain.py - incoming(): retry re-reads
    publication_receipts[0] (raw=''); pub-rival uses request+'-rival'.
  cut-source-overnight/s_inclusive.py, s_split.py, s_audit.py and
    batch-06/guard_a.py, guard_b.py, guard_audit.py - 'retained'/'duplicate_id'
    membership bypasses 'source-boundary-stale'.  batch-06/adapter_traces.py -
    patch semantics re-verified by sha256/done-mask bindings only.
  swarm-research-20260911-155142/boundary.py - suffix fixes one 'pub-commit';
    retry-verb absence is verified per case inventory.
"""
import copy
import hashlib
import json

PUB = ('pub-commit', 'pub-rival', 'pub-retry', 'pub-retry-conflict', 'pub-retry-foreign')
RETRY = PUB[2:]
ENVELOPE = ('request', 'principal', 'permit', 'expected_revision', 'parent', 'cut', 'content',
            'inventory', 'source_generation', 'source_head', 'generation', 'signature')
VIOLATION_LIMIT, REFUSAL_LIMIT = 50, 20


class _Corrupt(Exception):
    """Retained bytes failed a typed/hash binding; recorded as a violation."""


def _enc(v):
    return json.dumps(v, sort_keys=True, separators=(',', ':'))


def _digest(v):
    return hashlib.sha256(_enc(v).encode('utf-8')).hexdigest()


def _field(env, name):
    value = getattr(env, name, None)
    return env[ENVELOPE.index(name)] if value is None else value


def _fail(out, where, check, expected, observed):
    if len(out) < VIOLATION_LIMIT:
        out.append({'where': where, 'check': check, 'expected': expected, 'observed': observed})


def _advance(trace, state, index):
    """Apply one retained event patch; verify hash and completion bindings."""
    event = trace['events'][index]
    if event['action'] != trace['actions'][index] or _digest(state) != event['before_sha256']:
        raise _Corrupt('occurrence/prestate binding at event %d' % index)
    nxt = copy.deepcopy(state)
    for key, value in event['patch'].items():
        if trace['side'] == 'adapter' and key in ('core', 'journal'):
            nxt[key].update(value)
        else:
            nxt[key] = value
    if _digest(nxt) != event['after_sha256']:
        raise _Corrupt('poststate sha256 binding at event %d' % index)
    actions = trace['profile']['actions']
    if nxt['done'] != sum(1 << actions.index(a) for a in trace['actions'][:index + 1]):
        raise _Corrupt('completion mask binding at event %d' % index)
    if trace['side'] == 'adapter':
        qp = trace['q_profile']['actions']
        if nxt['core']['done'] != sum(1 << qp.index(a) for a in nxt['invocations']):
            raise _Corrupt('Q invocation mask binding at event %d' % index)
    return nxt


def _ledger(view, where, out):
    """Durable receipt/reply correspondence on one publication view."""
    receipts, revision = view['publication_receipts'], view['publication_revision']
    if type(revision) is not int or revision != len(receipts):
        _fail(out, where, 'revision-cardinality', 'revision == len(receipts)', _enc(revision))
    ids = [_field(e, 'request') for e, _ in receipts]
    if len(set(ids)) != len(receipts):
        _fail(out, where, 'unique-request-identity', 'distinct request ids', _enc(ids))
    parent = ''
    for index, (env, receipt) in enumerate(receipts):
        identity = (_field(env, 'request'), _digest(env), index + 1,
                    _field(env, 'generation'), _field(env, 'content'))
        if (_field(env, 'expected_revision'), _field(env, 'parent')) != (index, parent):
            _fail(out, where, 'parent-lineage', _enc((index, parent)),
                  _enc((_field(env, 'expected_revision'), _field(env, 'parent'))))
        if tuple(receipt) != identity:
            _fail(out, where, 'receipt-identity', _enc(identity), _enc(receipt))
        parent = _field(env, 'generation')
    reply = view['publication_reply']
    if reply and not any(tuple(r) == tuple(reply) for _, r in receipts):
        _fail(out, where, 'reply-without-durable-receipt', 'reply is a retained receipt', _enc(reply))
    selected = view['selected']
    if selected and not (receipts and selected == receipts[-1][0]
                         and any(row[0] == selected for row in view['publication_store'])):
        _fail(out, where, 'selected-committed-retained', 'selected is last retained envelope', _enc(selected))
    for env, _raw in view['publication_store']:
        if _field(env, 'generation') in view['retired_cuts']:
            _fail(out, where, 'retired-resurrection', 'generation not retired', _enc(_field(env, 'generation')))


def _incoming_request(view, verb):
    """Request identity exactly as q_domain.incoming constructs it."""
    receipts, staged = view['publication_receipts'], view['staged']
    if verb in RETRY:
        return _field(receipts[0][0], 'request') if receipts else (
            _field(staged[0], 'request') if staged else None)
    return None if not staged else _field(staged[0], 'request') + ('-rival' if verb == 'pub-rival' else '')


def _boundary_stale(ledger):
    attestation = ledger['attestation']
    return (not attestation or ledger['staged_source'] != attestation
            or tuple(attestation[:2]) != (ledger['source_generation'], ledger['source_revision']))


def _transition(bv, av, ledger, verb, decision, invoked, where, out, stats, record):
    """One publication transition on a single side's publication view."""
    request = _incoming_request(bv, verb)
    prior = next((row for row in bv['publication_receipts'] if _field(row[0], 'request') == request), None)
    stale = _boundary_stale(ledger)
    if prior is None and stale:
        expected, want_invoked = 'source-boundary-stale', False
    elif verb == 'pub-retry-foreign':
        expected, want_invoked = 'wrong-caller', True
    elif prior is not None:
        same = verb == 'pub-retry' or (verb == 'pub-commit' and bv['staged']
                                       and _enc(bv['staged'][0]) == _enc(prior[0]))
        expected, want_invoked = 'duplicate' if same else 'E-IDEMPOTENCY-CONFLICT', True
    else:
        expected, want_invoked = None, True
    if expected is not None and decision != verb + ':' + expected:
        _fail(out, where, 'branch-decision', verb + ':' + expected, decision)
    if invoked is not None and invoked != want_invoked:
        _fail(out, where, 'invocation-vs-branch', want_invoked, invoked)
    if record and prior is not None:
        stats['retained_branch'] += 1
        stats['bypass_boundary_stale'] += int(stale)
    if expected == 'duplicate' and decision == verb + ':duplicate':
        stats['duplicates'] += record
        for holds, check, exp, obs in (
                (av['publication_reply'] == prior[1], 'reply-is-retained-receipt',
                 _enc(prior[1]), _enc(av['publication_reply'])),
                (av['publication_receipts'] == bv['publication_receipts'], 'receipts-preserved',
                 _enc(bv['publication_receipts']), _enc(av['publication_receipts'])),
                (av['publication_revision'] == bv['publication_revision'], 'revision-preserved',
                 _enc(bv['publication_revision']), _enc(av['publication_revision'])),
                (av['publication_reads'] == bv['publication_reads'] + 1, 'reads-incremented',
                 _enc(bv['publication_reads'] + 1), _enc(av['publication_reads'])),
                (av['selected'] == bv['selected'], 'selected-preserved',
                 _enc(bv['selected']), _enc(av['selected']))):
            if not holds:
                _fail(out, where, check, exp, obs)
    elif expected is None and decision == verb + ':ok':
        stats['fresh_commits'] += record
        ra = av['publication_receipts']
        if not (len(ra) == len(bv['publication_receipts']) + 1 and ra[:-1] == bv['publication_receipts']
                and av['publication_revision'] == bv['publication_revision'] + 1
                and av['publication_reply'] == ra[-1][1] and av['selected'] == ra[-1][0]
                and any(row[0] == ra[-1][0] for row in av['publication_store'])):
            _fail(out, where, 'fresh-commit-correspondence',
                  'appended receipt becomes reply and selection', _enc(decision))
    else:
        for key in ('publication_receipts', 'publication_reply', 'publication_revision',
                    'selected', 'publication_store', 'publication_reads'):
            if _enc(av[key]) != _enc(bv[key]):
                _fail(out, where, 'refusal-mutates-' + key, _enc(bv[key]), _enc(av[key]))


def inspect_cases(cases, charge):
    """Audit typed restored cases; consume one charge unit per case prefix."""
    violations, observations = [], []
    totals = {'retained_branch': 0, 'duplicates': 0, 'fresh_commits': 0,
              'bypass_boundary_stale': 0, 'decisions': {}}
    audited = well_formed = 0
    for ci, case in enumerate(cases):
        where = 'case[%d]' % ci
        try:
            src, adp, rows = case['source'], case['adapter'], case.get('rows')
            actions = src['actions']
            if (src['side'] != 'source' or adp['side'] != 'adapter' or list(adp['actions']) != list(actions)
                    or len(src['events']) != len(actions) or len(adp['events']) != len(actions)
                    or (rows is not None and len(rows) != len(actions))):
                raise _Corrupt('mismatched side/action/event/row inventory')
        except (KeyError, TypeError, _Corrupt) as error:
            _fail(violations, where, 'case-shape', 'typed restored run_history case', str(error))
            continue
        stats = dict.fromkeys(('retained_branch', 'duplicates', 'fresh_commits', 'bypass_boundary_stale'), 0)
        decisions, pub_actions, refusals = {}, [], []
        s_now, a_now = copy.deepcopy(src['initial']), copy.deepcopy(adp['initial'])
        s_prev = a_prev = w = None
        case_audited = 0
        try:
            for prefix in range(len(actions) + 1):
                charge.take(1)
                w = '%s/prefix%d' % (where, prefix)
                if prefix:
                    s_prev, s_now = s_now, _advance(src, s_now, prefix - 1)
                    a_prev, a_now = a_now, _advance(adp, a_now, prefix - 1)
                    verb = actions[prefix - 1].partition('@')[0]
                    invoked = len(a_now['invocations']) - len(a_prev['invocations'])
                    if invoked not in (0, 1):
                        _fail(violations, w, 'invocation-delta', '0 or 1', _enc(invoked))
                    if rows is not None:
                        row = rows[prefix - 1]
                        for side, state in (('source', s_now), ('adapter', a_now)):
                            key, view = side + '_observation', (state if side == 'source' else state['core'])
                            if row[key]['decision'] != state['decision']:
                                _fail(violations, w, side + '-recorded-decision',
                                      state['decision'], row[key]['decision'])
                            if verb.startswith('pub-') and _enc(row[key].get('publication_reply')) != _enc(view['publication_reply']):
                                _fail(violations, w, side + '-recorded-reply',
                                      _enc(view['publication_reply']), _enc(row[key].get('publication_reply')))
                        if bool(row['q_invoked']) != bool(invoked):
                            _fail(violations, w, 'recorded-q-mask', bool(invoked), _enc(row['q_invoked']))
                    if verb in PUB:
                        pub_actions.append(verb)
                        decisions[s_now['decision']] = decisions.get(s_now['decision'], 0) + 1
                        _transition(s_prev, s_now, s_prev, verb, s_now['decision'], None,
                                    w + '/source', violations, stats, True)
                        _transition(a_prev['core'], a_now['core'], a_prev['journal'], verb,
                                    a_now['decision'], invoked, w + '/adapter', violations, stats, False)
                        if s_now['decision'] != verb + ':ok':
                            refusals.append(s_now['decision'])
                _ledger(s_now, w + '/source', violations)
                _ledger(a_now['core'], w + '/adapter-core', violations)
                audited += 1
                case_audited += 1
        except (KeyError, TypeError, IndexError, _Corrupt) as error:
            _fail(violations, w or where, 'prefix-inspection', 'intact typed fields', str(error))
        well_formed += 1
        for key in stats:
            totals[key] += stats[key]
        for k, v in decisions.items():
            totals['decisions'][k] = totals['decisions'].get(k, 0) + v
        observations.append({'case': case.get('case'), 'audited_prefixes': case_audited,
                             'publication_actions': pub_actions,
                             'retry_verbs_present': sorted({v for v in pub_actions if v in RETRY}),
                             'retained_branch_entries': stats['retained_branch'],
                             'duplicate_decisions': stats['duplicates'],
                             'fresh_commit_successes': stats['fresh_commits'],
                             'bypass_while_boundary_stale': stats['bypass_boundary_stale'],
                             'publication_refusals': refusals[:REFUSAL_LIMIT]})
    if violations:
        status = 'counterexample'
    elif not well_formed:
        status = 'not_applicable'
    elif totals['retained_branch']:
        status = 'supported'
    else:
        status = 'unproved'
    limitations = [
        'Audit is confined to the supplied restored cases; no new order, history or reducer execution was performed.',
        'charge.take(1) exhaustion propagates to the caller; audited_prefixes counts fully inspected prefixes only.',
        'Retry-verb absence shows the inspected inventories never issue a retained duplicate; not a proof over all orders.']
    if status == 'unproved':
        limitations.append('No inspected case entered the retained-duplicate branch; original-scale reachability of '
                           'this branch is unestablished and correspondence is verified only where data exists.')
    return {'status': status, 'observations': observations, 'limitations': limitations,
            'audited_prefixes': audited, 'violations': violations, 'totals': totals}
