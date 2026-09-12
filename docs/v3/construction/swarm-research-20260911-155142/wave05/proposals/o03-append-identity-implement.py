"""Bounded retained-certificate check for obligation o03-append-identity.

Scope: setup-append owner/incarnation/request/body idempotency, first-versus-last
receipt lookup, and the reachable unique-request-key ledger invariant, audited on
restored typed case objects retained by the unchanged checker
(c.run_history/c.artifact). No reducer, guard, audit, inventory or boundary
helper is executed inside inspection; per-prefix typed states are reconstructed
from the retained trace by c.t.restore only, and every expectation is recomputed
from the literal action string plus the observed pre-state ledger.

Source anchors (unchanged originals, representation only):
  - experiments/v3/cut-source-overnight/s_inclusive.py:36-53 and
    experiments/v3/cut-source-overnight/batch-06/guard_a.py:37-54: FIRST-match
    lookup next((r for r in s['append_receipts'] if r[0] == request), None) and
    refusal order owner -> existing -> incarnation -> pause -> registration ->
    gap -> attempt -> scope.
  - experiments/v3/cut-source-overnight/s_split.py append branch and
    batch-06/guard_b.py: LAST-match lookup {r[0]: r for r in
    s['append_receipts']}.get(identity).
  - experiments/v3/cut-source-overnight/s_audit.py invariant: unique append IDs,
    receipt[0]/[2]/[3] immutability, retained bytes at the admitted ordinal,
    unique attempt ids; its append branch is the model for the independent
    literal offer decode below (never s_domain.append_request).
  - experiments/v3/cut-source-overnight/s_domain.py:43-71: request spelling
    'append-<index>'/'-fresh', caller and incarnation variants.
  - docs/v3/construction/swarm-research-20260911-155142/inherited/
    prestage-correspondence-analysis.md: first/last lookups agree only under the
    reachable unique-key shape; malformed states are out of scope.

Finite accounting: charge.take(1) is taken once per case prefix BEFORE that
prefix is inspected; repeated cases charge repeatedly. audited_prefixes in the
result is the exact number of charged-and-inspected prefixes. Offer decoding and
both lookup recomputations are bounded scalar work inside the charged prefix.

Verdicts: 'counterexample' retains an expected/observed witness; 'supported'
means every charged prefix passed on both sides; 'unproved' when inspection was
empty or structurally blocked; 'not_applicable' when no append-family action or
receipt exists. This is a retained-evidence check only: no all-order theorem,
no accepted scientific PASS.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHECK_DIR = 'experiments/v3/eight-hour-research-20260910-01a08a22'
sys.path.insert(0, str(ROOT / CHECK_DIR))
import check as c

d, t, r = c.d, c.t, c.r
require = d.require
require(Path(c.__file__).resolve() == ROOT / CHECK_DIR / 'check.py',
        'explicit frozen checker path binding')

GEN0 = ('cut-source', 'collectorA', 'effectA', 0)
SCOPE = ('effect_id', 'idempotency_key', 'payload_digest', 'target_ref',
         'admission_epoch', 'fence_epoch')
LEDGER = ('append_log', 'append_receipts', 'append_reply')
STABLE = ('registration', 'attempts', 'collection', 'collected', 'attestation',
          'staged_source', 'selected_source', 'source_generation')
SOURCE_ONLY = ('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:')
OUTCOMES = ('ok', 'duplicate', 'append-id-conflict', 'wrong-append-owner',
            'stale-append-incarnation', 'E-PAUSED', 'no-registration',
            'append-gap-or-fork', 'unregistered-attempt', 'foreign-record-scope',
            'append-lose-reply')
CATCH = (KeyError, TypeError, IndexError, ValueError, AttributeError)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def offer(action):
    """Independent literal append-offer decode; mirrors s_audit, never append_request."""
    _, name, index, variant = action.split('@')[0].split(':')
    index = int(index)
    record = dict(d.q.lit.fixture(name)['original']['records'][index])
    request, caller, boot = 'append-' + str(index), 'collectorA', GEN0
    if variant == 'foreign':
        caller = 'collectorB'
    if variant == 'new-boot':
        boot = GEN0[:-1] + (1,)
    if variant == 'wrong-attempt':
        record['attempt_id'] = 'attempt:foreign'
    if variant == 'wrong-body':
        record['payload_digest'] = 'sha256:' + '9' * 64
    if variant == 'fresh':
        request += '-fresh'
    return request, (caller, boot, index, encoded(record)), record


def expect(s, action):
    """Expected (reason, patch) recomputed under BOTH retrieval disciplines."""
    request, body, record = offer(action)
    caller, boot, index, raw = body
    receipts = s['append_receipts']
    found = {'first': next((row for row in receipts if row[0] == request), None),
             'last': {row[0]: row for row in receipts}.get(request)}
    out = {}
    for mode in ('first', 'last'):
        existing, reason, patch = found[mode], 'ok', {}
        if caller != 'collectorA':
            reason = 'wrong-append-owner'
        elif existing is not None:
            if existing[1] != body:
                reason = 'append-id-conflict'
            else:
                reason, patch = 'duplicate', {'append_reply': existing[2]}
        elif boot != s['source_generation']:
            reason = 'stale-append-incarnation'
        elif s['paused']:
            reason = 'E-PAUSED'
        elif not s['registration']:
            reason = 'no-registration'
        elif index != len(s['append_log']):
            reason = 'append-gap-or-fork'
        elif all(pair[1] != record['attempt_id'] for pair in s['attempts']):
            reason = 'unregistered-attempt'
        elif any(record[f] != json.loads(s['registration'])[0][f] for f in SCOPE):
            reason = 'foreign-record-scope'
        else:
            receipt = (request, s['source_revision'] + 1, index,
                       hashlib.sha256(encoded(raw).encode()).hexdigest())
            patch = {'append_log': s['append_log'] + (raw,),
                     'source_revision': s['source_revision'] + 1,
                     'append_receipts': receipts + ((request, body, receipt),),
                     'append_reply': receipt}
        out[mode] = (reason, patch)
    return request, found, out


def invariant(v, where, side, problems):
    """Reachable unique-key and immutable-receipt invariant on one ledger view."""
    receipts, log = v['append_receipts'], v['append_log']
    keys = [row[0] for row in receipts]
    if len(set(keys)) != len(keys):
        problems.append(dict(kind='unique-request-key', where=where, side=side,
                             observed=r.typed(keys)))
    revisions = [row[2][1] for row in receipts]
    if len(set(revisions)) != len(revisions):
        problems.append(dict(kind='unique-admission-revision', where=where, side=side,
                             observed=r.typed(revisions)))
    for row in receipts:
        ok = (type(row) is tuple and len(row) == 3 and type(row[1]) is tuple
              and len(row[1]) == 4 and type(row[2]) is tuple and len(row[2]) == 4)
        if ok:
            request, body, receipt = row
            ok = (receipt[0] == request and receipt[2] == body[2]
                  and type(body[2]) is int and 0 <= body[2] < len(log)
                  and d.exact(log[body[2]], body[3])
                  and receipt[3] == hashlib.sha256(encoded(body[3]).encode()).hexdigest()
                  and body[0] == 'collectorA'
                  and type(body[1]) is tuple and len(body[1]) == 4 and body[1][:3] == GEN0[:3]
                  and type(receipt[1]) is int and 1 <= receipt[1] <= v['source_revision'])
        if not ok:
            problems.append(dict(kind='receipt-wellformed', where=where, side=side,
                                 observed=r.typed(row)))
    if v['append_reply'] and all(not d.exact(v['append_reply'], row[2]) for row in receipts):
        problems.append(dict(kind='reply-not-retained', where=where, side=side,
                             observed=r.typed(v['append_reply'])))
    ids = [pair[1] for pair in v['attempts']]
    if len(set(ids)) != len(ids):
        problems.append(dict(kind='unique-attempt-ids', where=where, side=side,
                             observed=r.typed(ids)))
    table = {row[0]: row for row in receipts}
    for key in set(keys):
        if not d.exact(next(row for row in receipts if row[0] == key), table[key]):
            problems.append(dict(kind='first-last-stored-diverge', where=where, side=side,
                                 observed=key))


def transition(s0, s1, action, where, side, problems, cover):
    """Expected-vs-observed append transition on one side's restored ledger view."""
    k = action.split('@')[0]
    if k.startswith('append:'):
        try:
            request, found, out = expect(s0, action)
        except CATCH as error:
            problems.append(dict(kind='offer-undecodable', where=where, side=side,
                                 action=action, observed=str(error)[:120]))
            return
        if not (d.exact(found['first'], found['last']) and d.exact(out['first'], out['last'])):
            problems.append(dict(kind='first-last-offer-diverge', where=where, side=side,
                                 action=action, expected=r.typed(out['first']),
                                 observed=r.typed(out['last'])))
        else:
            cover[side + ':first-last-agree'] = cover.get(side + ':first-last-agree', 0) + 1
        reason, patch = out['first']
        cover[side + ':' + reason] = cover.get(side + ':' + reason, 0) + 1
        want = dict(s0)
        want.update(patch)
        fields = LEDGER + ('source_revision',) + STABLE
        bad = [f for f in fields if not d.exact(s1[f], want[f])]
        if bad or s1['decision'] != k + ':' + reason:
            problems.append(dict(kind='append-postcondition', where=where, side=side,
                                 action=action, expected=r.typed([k + ':' + reason]),
                                 observed=r.typed(s1['decision']), differing=bad))
    elif k == 'append-lose-reply':
        bad = [f for f in ('append_log', 'append_receipts') + STABLE
               if not d.exact(s1[f], s0[f])]
        if bad or s1['append_reply'] != () or s1['decision'] != 'append-lose-reply:ok':
            problems.append(dict(kind='lose-reply-postcondition', where=where, side=side,
                                 action=action, expected='ok decision, cleared reply, ledger kept',
                                 observed=r.typed([s1['decision'], s1['append_reply']]),
                                 differing=bad))
        cover[side + ':append-lose-reply'] = cover.get(side + ':append-lose-reply', 0) + 1
    elif k.startswith('atomic:'):
        kept = (d.exact(s1['append_receipts'], s0['append_receipts'])
                and d.exact(s1['append_reply'], s0['append_reply']))
        grown = (d.exact(s1['append_log'], s0['append_log'])
                 or (len(s1['append_log']) == len(s0['append_log']) + 1
                     and d.exact(s1['append_log'][:-1], s0['append_log'])))
        if not (kept and grown):
            problems.append(dict(kind='atomic-ledger-shape', where=where, side=side,
                                 action=action, expected='receipts/reply kept; log kept or +1',
                                 observed=r.typed([len(s0['append_log']), len(s1['append_log'])])))
    else:
        bad = [f for f in LEDGER if not d.exact(s1[f], s0[f])]
        if bad:
            problems.append(dict(kind='ledger-mutated-by-other-verb', where=where, side=side,
                                 action=action, expected='append fields unchanged under ' + k,
                                 observed=r.typed([s1[f] for f in bad]), differing=bad))


def row_bind(sv, av, outer, row, action, i, where, problems):
    """Bind the retained comparison row to the restored typed states."""
    k = action.split('@')[0]
    checks = [row.get('source_action') == action, row.get('adapter_action') == action,
              row.get('index') == i - 1,
              row['source_observation'].get('decision') == sv['decision'],
              row['adapter_observation'].get('decision') == outer['decision']]
    if k.startswith('append'):
        checks += [d.exact(row['source_observation'].get('append_reply'), sv['append_reply']),
                   d.exact(row['adapter_observation'].get('append_reply'), av['append_reply'])]
    if k.startswith(SOURCE_ONLY) or k in ('append-lose-reply', 'collect-open'):
        checks.append(not row.get('q_invoked'))
    if not all(checks):
        problems.append(dict(kind='row-binding', where=where, action=action,
                             expected='literal action/index/decisions/reply bound to states',
                             observed=r.typed([row.get('source_action'), row.get('index'),
                                               row.get('q_invoked')])))


def inspect_cases(cases, charge):
    problems, blocked, limitations, observations = [], [], [], []
    cover, audited, surface = {}, 0, False
    for ci, case in enumerate([cases] if isinstance(cases, dict) else list(cases)):
        try:
            name, actions = case['case'], case['source']['actions']
            rows, items = case['rows'], case['prefixes']
            require(actions == case['adapter']['actions'], 'one visible schedule')
            require(len(rows) == len(actions) and len(items) == len(actions) + 1,
                    'complete retained rows and prefixes')
            ss, aa = t.restore(case['source']), t.restore(case['adapter'])
            require(len(ss) == len(aa) == len(actions) + 1, 'typed prefix states restored')
        except CATCH as error:
            blocked.append('case[%d]: %s' % (ci, str(error)[:120]))
            continue
        surface = surface or any(a.split('@')[0].startswith('append') for a in actions)
        decisions = {'source': {}, 'adapter': {}}
        for i in range(len(ss)):
            charge.take(1)
            try:
                where = '%s#%d' % (name, i)
                sv = ss[i]
                av = dict(aa[i]['core'], **aa[i]['journal'])
                av['decision'] = aa[i]['decision']
                invariant(sv, where, 'source', problems)
                invariant(av, where, 'adapter', problems)
                claimed = set(items[i].get('differing_journal_fields', ())) & set(LEDGER)
                raw = {f for f in LEDGER if not d.exact(sv[f], av[f])}
                if claimed != raw:
                    problems.append(dict(kind='journal-diff-binding', where=where,
                                         expected=r.typed(sorted(claimed)),
                                         observed=r.typed(sorted(raw))))
                if i:
                    action = actions[i - 1]
                    a0 = dict(aa[i - 1]['core'], **aa[i - 1]['journal'])
                    a0['decision'] = aa[i - 1]['decision']
                    row_bind(sv, av, aa[i], rows[i - 1], action, i, where, problems)
                    transition(ss[i - 1], sv, action, where, 'source', problems, cover)
                    transition(a0, av, action, where, 'adapter', problems, cover)
                    for side, dec in (('source', sv['decision']), ('adapter', av['decision'])):
                        decisions[side][dec] = decisions[side].get(dec, 0) + 1
                audited += 1
            except CATCH as error:
                blocked.append('%s#%d: %s' % (name, i, str(error)[:120]))
                break
        observations.append(dict(
            case=name, prefixes=audited and len(ss), charged_prefixes=len(ss),
            append_actions=sum(1 for a in actions if a.split('@')[0].startswith('append')),
            decisions=decisions))
    if problems:
        status = 'counterexample'
    elif blocked or not audited:
        status = 'unproved'
    elif not surface:
        status = 'not_applicable'
    else:
        status = 'supported'
    if not audited:
        limitations.append('no retained case prefix was inspectable; no evidence obtained')
    limitations += ['inspection blocked at ' + entry for entry in blocked]
    for side in ('source', 'adapter'):
        missing = [w for w in OUTCOMES if cover.get(side + ':' + w, 0) == 0
                   and (side + ':first-last-agree') or True]
        missing = [w for w in OUTCOMES if cover.get(side + ':' + w, 0) == 0]
        if surface and missing:
            limitations.append('unwitnessed %s-side append outcomes: %s' % (side, ','.join(missing)))
    limitations.append('both lookup disciplines re-derived on the single retained adapter '
                       'journal; adapter A/B step equality is producer-side evidence, not re-executed')
    limitations.append('retained-evidence check only: no reducer or audit execution, no '
                       'all-order reachability claim, no accepted PASS')
    if len(problems) > 64:
        limitations.append('problem witnesses truncated at 64 of %d' % len(problems))
    observations.append(dict(coverage=cover))
    return dict(status=status, observations=observations, limitations=limitations,
                audited_prefixes=audited)
