"""Bounded retained-certificate check for obligation o04 (append order).

Audited claim, per case prefix transition whose literal verb is
``append:<name>:<index>:<variant>`` or ``append-lose-reply``:

1. The visible decision equals the first failing clause of the documented
   append guard order evaluated on retained pre-state fields:
   wrong-append-owner; retained request row (append-id-conflict or
   duplicate); stale-append-incarnation; E-PAUSED; no-registration;
   append-gap-or-fork; unregistered-attempt; foreign-record-scope; else ok.
2. Acceptance grows append_log by exactly the offered record at the tail
   ordinal, gains exactly one receipt row
   ``(request, (caller, boot, index, raw), (request, revision+1, index,
   sha256(canonical raw)))``, increments source_revision by one, sets
   append_reply to that receipt, and the retained record's attempt_id is
   registered while its six scope fields equal the registration head.
3. Refusals preserve the append ledger; ``duplicate`` additionally restores
   append_reply from the retained receipt (reply-loss repair).
4. ``append-lose-reply`` clears append_reply and changes nothing else.
5. Every prefix keeps: unique request ids, unique attempt ids, each receipt
   row's retained bytes at its admitted ordinal, immutable receipt fields,
   and source_revision covering attempts + receipts + registration. Each
   post-state carries the literal action's completion bit.

Representation anchors (unchanged originals authoritative; this module
imports no project code and executes no reducer, guard or inventory):
  - experiments/v3/cut-source-overnight/s_audit.py: append and
    append-lose-reply audit clauses, invariant() receipt/ordinal rules,
    encoded() canonical JSON bytes.
  - experiments/v3/cut-source-overnight/batch-06/guard_audit.py: identical
    clause over the adapter journal-over-core ledger view.
  - experiments/v3/cut-source-overnight/s_domain.py: append_request literal
    decoding (request id 'append-<index>'['-fresh']; caller 'collectorB' for
    'foreign'; offered incarnation generation 1 only for 'new-boot';
    'wrong-attempt' offers attempt_id 'attempt:foreign'; 'wrong-body' offers
    payload_digest 'sha256:'+'9'*64). append_request is pure in the action
    literal, so a repeated literal provably re-offers identical bytes; that
    is the basis for proving 'duplicate' from retained rows.
  - experiments/v3/cut-source-overnight/batch-05/semantic.py: observation()
    retains decision and append_reply for append verbs.
  - experiments/v3/eight-hour-research-20260910-01a08a22/check.py:
    run_history/audit_case retained case shape (typed traces, rows,
    prefixes) inspected here.

Accounting: charge.take(1) is consumed before each inspected case prefix;
re-inspecting a repeated case charges again. audited_prefixes equals the
number of take(1) calls. A charge overrun propagates rather than returning
a partial verdict. No all-order reachability, delegation correctness or
scientific acceptance is claimed; transitions whose refused offered bytes
are not retained are reported 'consistent' and cap the verdict at
'unproved'.
"""
import hashlib
import json

REASONS = ('ok', 'wrong-append-owner', 'append-id-conflict', 'duplicate',
           'stale-append-incarnation', 'E-PAUSED', 'no-registration',
           'append-gap-or-fork', 'unregistered-attempt', 'foreign-record-scope')
SCOPE = ('effect_id', 'idempotency_key', 'payload_digest', 'target_ref',
         'admission_epoch', 'fence_epoch')
LEDGER = ('append_log', 'append_receipts', 'source_revision')
STABLE = ('registration', 'attempts', 'collection', 'collected', 'attestation',
          'staged_source', 'selected_source')
VIEW_KEYS = ('append_log', 'append_receipts', 'append_reply', 'source_revision',
             'registration', 'attempts', 'paused', 'source_generation',
             'decision', 'done')


def _norm(x):
    if isinstance(x, dict):
        return {str(k): _norm(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_norm(v) for v in x]
    if x is None or type(x) in (str, int, bool, float):
        return x
    return repr(x)


def _digest(raw):
    return hashlib.sha256(json.dumps(raw, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def _find(node, keys, depth):
    if depth < 0:
        return None
    if type(node) is dict:
        if all(k in node for k in keys):
            return node
        for value in node.values():
            hit = _find(value, keys, depth - 1)
            if hit is not None:
                return hit
    elif type(node) in (list, tuple):
        for value in node:
            hit = _find(value, keys, depth - 1)
            if hit is not None:
                return hit
    return None


def _views(trace, side):
    keys = ('core', 'journal', 'done', 'decision') if side == 'adapter' else VIEW_KEYS
    states = [trace['initial']]
    for event in trace['events']:
        found = _find(event, keys, 4)
        if found is None:
            raise ValueError(side + ' trace event has no retained post-state')
        states.append(found)
    if side == 'adapter':
        states = [dict(st['core'], **st['journal'], done=st['done'],
                       decision=st['decision']) for st in states]
    for st in states:
        missing = [k for k in VIEW_KEYS if k not in st]
        if missing:
            raise ValueError(side + ' state missing ' + repr(missing))
    return states


def _invariants(view):
    problems = []
    receipts = view['append_receipts']
    if len({r[0] for r in receipts}) != len(receipts):
        problems.append('non-unique retained request ids')
    if len({p[1] for p in view['attempts']}) != len(view['attempts']):
        problems.append('non-unique retained attempt ids')
    for row in receipts:
        if not (type(row) in (list, tuple) and len(row) == 3
                and type(row[1]) in (list, tuple) and len(row[1]) == 4
                and type(row[2]) in (list, tuple) and len(row[2]) == 4):
            problems.append('malformed append receipt row')
            continue
        request, body, receipt = row
        if not (type(body[2]) is int and 0 <= body[2] < len(view['append_log'])
                and _norm(view['append_log'][body[2]]) == _norm(body[3])):
            problems.append('retained bytes absent at admitted ordinal')
        if not (receipt[0] == request and receipt[2] == body[2]
                and receipt[3] == _digest(body[3])):
            problems.append('receipt not bound to retained bytes')
    floor = len(view['attempts']) + len(receipts) + bool(view['registration'])
    if not (type(view['source_revision']) is int and view['source_revision'] >= floor):
        problems.append('source_revision below attempt/append coverage')
    return problems


def _expected(before, k, origin):
    _, _, index, variant = k.split(':')
    index = int(index)
    request = 'append-' + str(index) + ('-fresh' if variant == 'fresh' else '')
    caller = 'collectorB' if variant == 'foreign' else 'collectorA'
    boot = ('cut-source', 'collectorA', 'effectA', 1 if variant == 'new-boot' else 0)
    if caller != 'collectorA':
        return request, caller, boot, index, ('wrong-append-owner',), True
    rows = [r for r in before['append_receipts'] if r[0] == request]
    if rows:
        if origin.get(request) == k:
            return request, caller, boot, index, ('duplicate',), True
        if _norm(rows[0][1][:3]) != _norm((caller, boot, index)):
            return request, caller, boot, index, ('append-id-conflict',), True
        return request, caller, boot, index, ('append-id-conflict', 'duplicate'), False
    if _norm(boot) != _norm(before['source_generation']):
        return request, caller, boot, index, ('stale-append-incarnation',), True
    if before['paused']:
        return request, caller, boot, index, ('E-PAUSED',), True
    if not before['registration']:
        return request, caller, boot, index, ('no-registration',), True
    if index != len(before['append_log']):
        return request, caller, boot, index, ('append-gap-or-fork',), True
    if variant == 'wrong-attempt' and all(p[1] != 'attempt:foreign' for p in before['attempts']):
        return request, caller, boot, index, ('unregistered-attempt',), True
    possible = ['unregistered-attempt', 'foreign-record-scope', 'ok']
    if variant == 'wrong-body':
        try:
            if json.loads(before['registration'])[0]['payload_digest'] != 'sha256:' + '9' * 64:
                possible.remove('ok')
        except (ValueError, KeyError, IndexError, TypeError):
            pass
    return request, caller, boot, index, tuple(possible), False


def _post(before, after, request, caller, boot, index, reason):
    problems = []
    if reason == 'ok':
        raw = None
        if index != len(before['append_log']):
            problems.append('accepted ordinal is not the log tail')
        elif not (len(after['append_log']) == index + 1 and
                  _norm(after['append_log'][:index]) == _norm(before['append_log'])):
            problems.append('append_log did not gain exactly the offered record')
        else:
            raw = after['append_log'][index]
        if raw is not None:
            try:
                record = json.loads(raw)
                head = json.loads(before['registration'])[0]
                if record['attempt_id'] not in {p[1] for p in before['attempts']}:
                    problems.append('accepted unregistered attempt_id')
                diff = [f for f in SCOPE if _norm(record.get(f)) != _norm(head.get(f))]
                if diff:
                    problems.append('accepted record outside registration scope ' + repr(diff))
            except (ValueError, KeyError, IndexError, TypeError) as error:
                problems.append('retained record undecodable: ' + str(error))
        revision = before['source_revision'] + 1
        if after['source_revision'] != revision:
            problems.append('source_revision not incremented by one')
            receipt, row = None, None
        else:
            receipt = (request, revision, index, _digest(raw))
            row = (request, (caller, boot, index, raw), receipt)
        if row is not None:
            if _norm(after['append_receipts']) != _norm(before['append_receipts']) + [_norm(row)]:
                problems.append('receipts did not gain the exact retained row')
            if _norm(after['append_reply']) != _norm(receipt):
                problems.append('append_reply not set to the new receipt')
    elif reason == 'duplicate':
        rows = [r for r in before['append_receipts'] if r[0] == request]
        if not rows:
            problems.append('duplicate refusal without a retained request row')
        elif _norm(after['append_reply']) != _norm(rows[0][2]):
            problems.append('lost reply not restored from the retained receipt')
        if [_norm(after[f]) for f in LEDGER] != [_norm(before[f]) for f in LEDGER]:
            problems.append('duplicate refusal mutated the append ledger')
    else:
        if [_norm(after[f]) for f in LEDGER + ('append_reply',)] != \
                [_norm(before[f]) for f in LEDGER + ('append_reply',)]:
            problems.append('refusal mutated append fields')
    if [_norm(after[f]) for f in STABLE] != [_norm(before[f]) for f in STABLE]:
        problems.append('non-append journal fields changed')
    return problems


def _lose(before, after):
    problems = []
    if after['decision'] != 'append-lose-reply:ok':
        problems.append('unexpected decision ' + repr(after['decision']))
    if _norm(after['append_reply']) != []:
        problems.append('append_reply not cleared')
    fields = LEDGER + STABLE
    if [_norm(after[f]) for f in fields] != [_norm(before[f]) for f in fields]:
        problems.append('lose-reply mutated non-reply fields')
    return problems


def inspect_cases(cases, charge):
    """Inspect retained typed case objects; see module docstring for the claim."""
    observations, limitations = [], []
    audited = 0
    count = {'cases': 0, 'skipped': 0, 'append_transitions': 0, 'proven': 0,
             'consistent': 0, 'mismatch': 0, 'unverified': 0}
    for pos, case in enumerate(cases):
        label = case.get('case') if type(case) is dict else None
        try:
            actions = tuple(case['source']['actions'])
            order = tuple(case['source']['profile']['actions'])
            sides = {s: _views(case[s], s) for s in ('source', 'adapter')}
            if not (len(sides['source']) == len(sides['adapter']) == len(actions) + 1):
                raise ValueError('trace depth does not match action inventory')
            rows = case['rows'] if type(case.get('rows')) in (list, tuple) else ()
        except (AttributeError, KeyError, IndexError, TypeError, ValueError) as error:
            limitations.append('case %r not inspectable: %s' % (label or pos, error))
            count['skipped'] += 1
            continue
        count['cases'] += 1
        origin = {'source': {}, 'adapter': {}}
        for prefix in range(len(actions) + 1):
            charge.take(1)
            audited += 1
            for side in ('source', 'adapter'):
                view = sides[side][prefix]
                for problem in _invariants(view):
                    count['mismatch'] += 1
                    observations.append(dict(case=label, side=side, prefix=prefix,
                                             result='mismatch', witness=problem))
                if type(view['done']) is not int or view['done'] < 0 or \
                        (prefix == 0 and view['done'] != 0) or (prefix and not
                        view['done'] >> order.index(actions[prefix - 1]) & 1):
                    count['mismatch'] += 1
                    observations.append(dict(case=label, side=side, prefix=prefix,
                        result='mismatch', witness='completion bits inconsistent with prefix'))
            if prefix == 0:
                for side in ('source', 'adapter'):
                    view = sides[side][0]
                    if not (view['append_log'] == view['append_receipts']
                            == view['append_reply'] == ()
                            and view['source_revision'] == 0 and view['registration'] == ''):
                        count['mismatch'] += 1
                        observations.append(dict(case=label, side=side, prefix=0,
                            result='mismatch', witness='initial append fields not empty'))
                continue
            action = actions[prefix - 1]
            k = action.partition('@')[0]
            if k != 'append-lose-reply' and not k.startswith('append:'):
                continue
            count['append_transitions'] += 1
            row = rows[prefix - 1] if prefix - 1 < len(rows) else None
            if type(row) is not dict or row.get('index') != prefix - 1 \
                    or row.get('source_action') != action:
                count['unverified'] += 1
            for side in ('source', 'adapter'):
                before, after = sides[side][prefix - 1], sides[side][prefix]
                observed = after['decision']
                if k == 'append-lose-reply':
                    problems, expected, proven = _lose(before, after), ['append-lose-reply:ok'], True
                else:
                    try:
                        request, caller, boot, index, expected, proven = _expected(before, k, origin[side])
                    except (ValueError, KeyError, IndexError, TypeError) as error:
                        count['unverified'] += 1
                        observations.append(dict(case=label, side=side, prefix=prefix,
                            action=k, result='uninspected', witness='decode failed: %s' % error))
                        continue
                    problems = []
                    reason = observed[len(k) + 1:] if type(observed) is str \
                        and observed.startswith(k + ':') else None
                    if reason is None or reason not in REASONS:
                        problems.append('decision outside append vocabulary ' + repr(observed))
                    elif proven and reason != expected[0]:
                        problems.append('expected %r observed %r' % (expected[0], reason))
                    elif not proven and reason not in expected:
                        problems.append('expected one of %r observed %r' % (expected, reason))
                    if not problems:
                        problems = _post(before, after, request, caller, boot, index, reason)
                    expected = list(expected)
                for r in after['append_receipts']:
                    if r[0] not in {x[0] for x in before['append_receipts']}:
                        origin[side].setdefault(r[0], k)
                key = 'source_observation' if side == 'source' else 'adapter_observation'
                if type(row) is dict and key in row:
                    want = {'decision': observed, 'append_reply': after['append_reply']}
                    if _norm(row[key]) != _norm(want):
                        problems.append('retained row observation disagrees with state')
                else:
                    count['unverified'] += 1
                result = 'mismatch' if problems else \
                    ('proven' if proven or observed == k + ':ok' else 'consistent')
                count[result] += 1
                observations.append(dict(case=label, side=side, prefix=prefix, action=k,
                                         expected=expected, observed=observed, result=result,
                                         problems=problems,
                                         append_reply=_norm(after['append_reply'])))
    if count['mismatch']:
        status = 'counterexample'
    elif count['append_transitions'] == 0:
        status = 'unproved' if count['skipped'] else 'not_applicable'
    elif count['consistent'] or count['unverified'] or count['skipped']:
        status = 'unproved'
    else:
        status = 'supported'
    observations.append(dict(accounting=dict(charge_calls=audited, **count)))
    limitations.extend((
        'Refused offered record bytes are not part of the retained journal; '
        'unregistered-attempt/foreign-record-scope refusals and '
        'id-conflict-versus-duplicate without literal provenance grade only '
        "'consistent'.",
        'Only append-family verbs get transition-level checks; other verbs are '
        'covered solely by per-prefix retained invariants and completion bits.',
        'Adapter states are audited through the documented journal-over-core '
        'overlay view; Q core fields are not re-derived.',
        'Certificate-only evidence: no new executions, all-order reachability '
        'or scientific acceptance is claimed.'))
    return dict(status=status, observations=observations,
                limitations=limitations, audited_prefixes=audited)
