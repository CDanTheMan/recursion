"""Bounded retained-certificate check for the staged-source journal obligation.

inspect_cases(cases, charge): cases are typed original c.run_history/c.artifact
restored case objects; charge.take(1) precedes every inspected case prefix and
all repetitions count. Returns a JSON-safe dict {status, observations,
limitations, audited_prefixes}. No reducer, boundary helper, fixture or model
code is imported or executed; retained patch events are replayed and
digest-bound like the unchanged trace-restore evidence model.

Source anchors (unchanged originals, representation only):
s_inclusive.py delegated else-branch: stage writes staged_source=attestation,
publication_revision growth copies staged_source into selected_source, and
non-retained pub/reconcile pre-gates refuse 'source-boundary-stale'.
s_audit.py: identical independent byte-level postconditions.
batch-06/a_inclusive.py + a_audit.py: adapter journal staged_source/
selected_source writes, journal source_generation advance on source-restart,
and the actual Q invocation mask. batch-07/identity.py + identity_audit.py:
identity-row and origin-proof shape, incarnation_pair_established_by_identity
stays False. batch-06/adapter_traces.py: patch/digest trace-event format
reimplemented independently below.

Accounting: audited_prefixes counts charged, fully inspected prefixes. Every
observation keeps expected/observed witnesses. Bounded check only; never a
global theorem or acceptance claim.
"""
import copy
import hashlib
import json

PUB = ('pub-commit', 'pub-rival', 'pub-retry', 'pub-retry-conflict', 'pub-retry-foreign')
MIRROR = ('attestation', 'staged_source', 'selected_source', 'source_generation')
PREFIX_KEYS = frozenset(('prefix', 'strict_differing_common_fields', 'differing_common_fields',
    'differing_journal_fields', 'strict_related', 'related', 'staged_rule', 'identity_proof',
    'pairs_sha256', 'incarnation_pair_established_by_identity'))
PROOF_KEYS = frozenset(('case', 'prefix', 'source_origin', 'adapter_origin', 'source_prefix_sha256',
    'adapter_prefix_sha256', 'source_state_sha256', 'adapter_state_sha256'))
ORIGIN_KEYS = frozenset(('event_index', 'action', 'before_sha256', 'after_sha256'))
MAX_OBS = 64


def _digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _verb(a):
    return a.partition('@')[0]


def _typed(v):
    if isinstance(v, dict):
        return ['dict', [[k, _typed(x)] for k, x in sorted(v.items())]]
    if isinstance(v, (list, tuple)):
        return [type(v).__name__, [_typed(x) for x in v]]
    return [type(v).__name__, v]


def _bump(t):
    return tuple(t[:-1]) + (t[-1] + 1,)


def _envelope(x):
    sig = getattr(x, 'signature', '')
    return (type(x).__name__ == 'Envelope' and len(tuple(x)) == 12 and type(sig) is str
            and len(sig) == 64 and all(c in '0123456789abcdef' for c in sig))


def _identical(a, b):
    # Shape plus typed equality; signature/payload re-verification remains with
    # the unchanged identity_audit representation.
    return (type(a) is type(b) is tuple and len(a) == len(b) == 2 and a == b
            and _envelope(a[0]) and _envelope(b[0]) and type(a[1]) is str and bool(a[1]))


def _request(s, k):
    e = s['staged'][0] if s['staged'] else None
    if k in PUB[2:]:
        return s['publication_receipts'][0][0].request if s['publication_receipts'] else (e.request if e else None)
    return (e.request + '-rival' if k == 'pub-rival' else e.request) if e else None


def _guard(pre):
    a = pre['attestation']
    return bool(a) and tuple(a[:2]) == (pre['source_generation'], pre['source_revision']) and pre['staged_source'] == a


def _origin(tr, snaps, i):
    cur = snaps[i][0]
    if not cur:
        return None
    for x in range(i - 1, -1, -1):
        if snaps[x + 1][0] != cur:
            return None
        if _verb(tr['events'][x]['action']) == 'stage' and snaps[x + 1][1] == 'stage:ok':
            return x
    return None


def _apply(st, ev, side):
    for k, v in ev['patch'].items():
        if side == 'adapter' and k in ('core', 'journal'):
            st[k].update(v)
        else:
            st[k] = v


def _prefix(name, i, s, a, tr_s, tr_a, snaps_s, snaps_a, prefixes, stats, fail, note):
    j = a['journal']
    diffs = [f for f in MIRROR if s[f] != j[f]]
    for f in diffs:
        fail(case=name, prefix=i, check='journal-mirror', field=f,
             expected=_typed(s[f]), observed=_typed(j[f]))
    if not diffs:
        stats['journal_mirror_prefixes'] += 1
    for label, staged, ss in (('source', s['staged'], s['staged_source']),
                              ('adapter', a['core']['staged'], j['staged_source'])):
        if staged and ss and (staged[0].cut != ss[2] or staged[0].source_generation != ss[0]):
            fail(case=name, prefix=i, check=label + '-staged-binding', expected=_typed(ss),
                 observed=_typed((staged[0].source_generation, staged[0].cut)))
    if s['decision'] != a['decision']:
        fail(case=name, prefix=i, check='visible-decision', expected=s['decision'], observed=a['decision'])
    if i >= len(prefixes):
        return
    pr = prefixes[i]
    if set(pr) != PREFIX_KEYS:
        fail(case=name, prefix=i, check='identity-row-keys', expected=sorted(PREFIX_KEYS),
             observed=sorted(pr))
        return
    if pr['incarnation_pair_established_by_identity'] is not False:
        fail(case=name, prefix=i, check='identity-creates-authority', expected=False,
             observed=pr['incarnation_pair_established_by_identity'])
    if sorted(f for f in pr['differing_journal_fields'] if f in MIRROR) != sorted(diffs):
        fail(case=name, prefix=i, check='journal-difference-certificate', expected=diffs,
             observed=list(pr['differing_journal_fields']))
    strict = list(pr['strict_differing_common_fields'])
    if 'staged' not in strict:
        if pr['staged_rule'] != 'strict' or pr['identity_proof'] is not None or list(pr['differing_common_fields']) != strict:
            fail(case=name, prefix=i, check='staged-rule-strict', expected='strict', observed=pr['staged_rule'])
        return
    o_s, o_a = _origin(tr_s, snaps_s, i), _origin(tr_a, snaps_a, i)
    permit = (_identical(s['staged'], a['core']['staged']) and o_s is not None and o_s == o_a
              and _verb(tr_s['events'][o_s]['action']) == _verb(tr_a['events'][o_a]['action']))
    rule = 'original-object-identity' if permit else 'unrelated'
    if pr['staged_rule'] != rule:
        fail(case=name, prefix=i, check='staged-rule', expected=rule, observed=pr['staged_rule'])
    proof = pr['identity_proof']
    if permit:
        stats['identity_rows'] += 1
        bad = not (type(proof) is dict and set(proof) == PROOF_KEYS
                   and type(proof['source_origin']) is dict and set(proof['source_origin']) == ORIGIN_KEYS
                   and type(proof['adapter_origin']) is dict and set(proof['adapter_origin']) == ORIGIN_KEYS
                   and proof['case'] == name and proof['prefix'] == i
                   and proof['source_origin']['event_index'] == o_s
                   and proof['adapter_origin']['event_index'] == o_a)
        if bad or list(pr['differing_common_fields']) != [x for x in strict if x != 'staged']:
            fail(case=name, prefix=i, check='identity-proof-shape', expected=sorted(PROOF_KEYS),
                 observed=_typed(proof))
        env = s['staged'][0]
        if env.source_generation != s['source_generation'] or (s['staged_source']
                and tuple(s['staged_source'][:2]) != (s['source_generation'], s['source_revision'])):
            stats['stale_identity_prefixes'] += 1
            note(case=name, prefix=i, kind='stale-stage-identity-accepted',
                 staged_generation=_typed(env.source_generation), live=_typed(s['source_generation']))
    elif proof is not None or list(pr['differing_common_fields']) != strict:
        fail(case=name, prefix=i, check='identity-proof-absent', expected=None, observed=_typed(proof))


def _transition(i, act, sp, s, ap, a, row, name, stats, fail, note):
    k = _verb(act)
    j, jp = a['journal'], ap['journal']
    invoked = len(a['invocations']) > len(ap['invocations'])
    if k == 'stage' or k.startswith('stage-'):
        stats['stage_events'] += 1
        if s['staged_source'] != sp['attestation']:
            fail(case=name, prefix=i, check='stage-capture-source', action=act,
                 expected=_typed(sp['attestation']), observed=_typed(s['staged_source']))
        if j['staged_source'] != jp['attestation']:
            fail(case=name, prefix=i, check='stage-capture-journal', action=act,
                 expected=_typed(jp['attestation']), observed=_typed(j['staged_source']))
        else:
            note(case=name, prefix=i, kind='stage-capture', action=act,
                 captured=_typed(s['staged_source']), decision=s['decision'])
    else:
        if s['staged_source'] != sp['staged_source']:
            fail(case=name, prefix=i, check='staged-source-persistence', action=act,
                 expected=_typed(sp['staged_source']), observed=_typed(s['staged_source']))
        if j['staged_source'] != jp['staged_source']:
            fail(case=name, prefix=i, check='journal-staged-persistence', action=act,
                 expected=_typed(jp['staged_source']), observed=_typed(j['staged_source']))
    for label, pre, cur, own in (('source', sp, s, s), ('journal', ap['core'], a['core'], j)):
        if cur['publication_revision'] > pre['publication_revision']:
            if own['selected_source'] != pre.get('staged_source', own['staged_source']):
                pass
        # revision-growth copy checked explicitly below to keep witnesses clear
    if s['publication_revision'] > sp['publication_revision']:
        if s['selected_source'] != sp['staged_source']:
            fail(case=name, prefix=i, check='selected-source-copy', action=act,
                 expected=_typed(sp['staged_source']), observed=_typed(s['selected_source']))
    elif s['selected_source'] != sp['selected_source']:
        fail(case=name, prefix=i, check='selected-source-persistence', action=act,
             expected=_typed(sp['selected_source']), observed=_typed(s['selected_source']))
    if a['core']['publication_revision'] > ap['core']['publication_revision']:
        if j['selected_source'] != jp['staged_source']:
            fail(case=name, prefix=i, check='journal-selected-copy', action=act,
                 expected=_typed(jp['staged_source']), observed=_typed(j['selected_source']))
    elif j['selected_source'] != jp['selected_source']:
        fail(case=name, prefix=i, check='journal-selected-persistence', action=act,
             expected=_typed(jp['selected_source']), observed=_typed(j['selected_source']))
    if k == 'source-attest':
        if s['decision'] == 'source-attest:ok':
            stats['attest_commits'] += 1
            want = (sp['collection'][0], sp['collection'][1], sp['cut_delivery'])
            if s['attestation'] != want or j['attestation'] != want:
                fail(case=name, prefix=i, check='attestation-capture', action=act,
                     expected=_typed(want), observed=_typed((s['attestation'], j['attestation'])))
        elif s['attestation'] != sp['attestation'] or j['attestation'] != jp['attestation']:
            fail(case=name, prefix=i, check='refused-attestation-mutated', action=act,
                 expected=_typed((sp['attestation'], jp['attestation'])),
                 observed=_typed((s['attestation'], j['attestation'])))
    if k == 'source-restart' and s['decision'] == 'source-restart:ok':
        stats['restart_events'] += 1
        for label, pre, cur in (('source', sp, s), ('journal', jp, j), ('core', ap['core'], a['core'])):
            if cur['source_generation'] != _bump(pre['source_generation']):
                fail(case=name, prefix=i, check=label + '-generation-advance', action=act,
                     expected=_typed(_bump(pre['source_generation'])), observed=_typed(cur['source_generation']))
        if s['attestation']:
            if tuple(s['attestation'][:2]) == (s['source_generation'], s['source_revision']):
                fail(case=name, prefix=i, check='restart-staleness', action=act,
                     expected='stale-capture', observed='current')
            else:
                note(case=name, prefix=i, kind='restart-retains-stale-capture', action=act,
                     retained=_typed(s['attestation']),
                     live=_typed((s['source_generation'], s['source_revision'])))
    if k in PUB:
        req = _request(sp, k)
        retained = req is not None and any(r[0].request == req for r in sp['publication_receipts'])
        if retained:
            stats['pub_retained_duplicates'] += 1
            if not invoked or s['decision'] == k + ':source-boundary-stale':
                fail(case=name, prefix=i, check='retained-duplicate-delegation', action=act,
                     expected='delegated-duplicate', observed=s['decision'])
        else:
            stats['pub_guard_evaluations'] += 1
            vs, vj = _guard(sp), _guard(jp)
            if vs != vj:
                fail(case=name, prefix=i, check='guard-view-divergence', action=act,
                     expected=vs, observed=vj)
            if vs:
                stats['pub_guard_passes'] += 1
                if not invoked or s['decision'] == k + ':source-boundary-stale':
                    fail(case=name, prefix=i, check='current-source-publication-blocked', action=act,
                         expected='delegated', observed=s['decision'])
            else:
                stats['pub_guard_refusals'] += 1
                want = k + ':source-boundary-stale'
                if s['decision'] != want or a['decision'] != want or invoked:
                    fail(case=name, prefix=i, check='publication-guard-refusal', action=act,
                         expected=want, observed=_typed((s['decision'], a['decision'], invoked)))
                else:
                    note(case=name, prefix=i, kind='current-source-guard-refusal', action=act,
                         expected=want, observed=s['decision'], attestation=_typed(sp['attestation']),
                         staged_source=_typed(sp['staged_source']),
                         live=_typed((sp['source_generation'], sp['source_revision'])))
    if k == 'reconcile':
        stats['reconcile_guards'] += 1
        sel = sp['selected_source']
        valid = bool(sel) and tuple(sel[:2]) == (sp['source_generation'], sp['source_revision'])
        if valid:
            if not invoked or s['decision'] == 'reconcile:source-boundary-stale':
                fail(case=name, prefix=i, check='current-source-reconcile-blocked', action=act,
                     expected='delegated', observed=s['decision'])
        else:
            stats['reconcile_refusals'] += 1
            if s['decision'] != 'reconcile:source-boundary-stale' or invoked:
                fail(case=name, prefix=i, check='reconcile-guard-refusal', action=act,
                     expected='reconcile:source-boundary-stale', observed=_typed((s['decision'], invoked)))
    if row is not None:
        ok = (row.get('index') == i - 1 and row.get('source_action') == act
              and row.get('adapter_action') == act and row.get('q_invoked') == invoked
              and (row.get('source_observation') or {}).get('decision') == s['decision']
              and (row.get('adapter_observation') or {}).get('decision') == a['decision'])
        if not ok:
            fail(case=name, prefix=i, check='comparison-row-binding', action=act,
                 expected=_typed((i - 1, act, invoked, s['decision'], a['decision'])),
                 observed=_typed(row))


def inspect_cases(cases, charge):
    obs, lim = [], []
    stats = {'stage_events': 0, 'attest_commits': 0, 'restart_events': 0,
             'pub_guard_evaluations': 0, 'pub_guard_refusals': 0, 'pub_guard_passes': 0,
             'pub_retained_duplicates': 0, 'reconcile_guards': 0, 'reconcile_refusals': 0,
             'journal_mirror_prefixes': 0, 'identity_rows': 0, 'stale_identity_prefixes': 0,
             'mismatches': 0, 'cases': 0}
    audited, halt = 0, None

    def fail(**w):
        stats['mismatches'] += 1
        w['mismatch'] = True
        if len(obs) < MAX_OBS:
            obs.append(w)

    def note(**w):
        if len(obs) < MAX_OBS:
            obs.append(w)

    for case in cases or []:
        if halt:
            break
        name = case.get('case') if isinstance(case, dict) else None
        try:
            tr_s, tr_a = case['source'], case['adapter']
            actions = list(tr_s['actions'])
            if (len(tr_s['events']) != len(actions) or list(tr_a['actions']) != actions
                    or len(tr_a['events']) != len(actions)):
                fail(case=name, check='trace-inventory', expected=len(actions),
                     observed=_typed((len(tr_s['events']), len(tr_a.get('events', ())))))
                continue
        except (KeyError, TypeError, AttributeError) as e:
            lim.append('case %r lacks typed source/adapter traces: %r' % (name, e))
            continue
        stats['cases'] += 1
        rows, prefixes = case.get('rows') or [], case.get('prefixes') or []
        s, a = copy.deepcopy(tr_s['initial']), copy.deepcopy(tr_a['initial'])
        side_a, sp, ap = tr_a.get('side', 'adapter'), None, None
        snaps_s, snaps_a, seen = [], [], set()
        for i in range(len(actions) + 1):
            try:
                charge.take(1)
            except Exception as e:
                halt = 'charge refused before prefix %d of case %r: %r' % (i, name, e)
                break
            try:
                if i:
                    act = actions[i - 1]
                    for side, tr, st in (('source', tr_s, s), (side_a, tr_a, a)):
                        ev = tr['events'][i - 1]
                        ok = (ev.get('action') == act and act not in seen
                              and set(tr['profile']['requires'][act]) <= seen
                              and _digest(st) == ev.get('before_sha256'))
                        if ok:
                            _apply(st, ev, side)
                            ok = (_digest(st) == ev.get('after_sha256') and st['done'] ==
                                  sum(1 << tr['profile']['actions'].index(x) for x in seen | {act}))
                        if not ok:
                            fail(case=name, prefix=i, check=side + '-event-binding', action=act,
                                 expected=ev.get('after_sha256'), observed=_digest(st))
                    seen.add(act)
                    qp = tr_a.get('q_profile')
                    if qp is not None:
                        want = sum(1 << qp['actions'].index(x) for x in a['invocations'])
                        if a['core']['done'] != want:
                            fail(case=name, prefix=i, check='q-invocation-mask', action=act,
                                 expected=want, observed=a['core']['done'])
                audited += 1
                snaps_s.append((s['staged'], s['decision']))
                snaps_a.append((a['core']['staged'], a['decision']))
                _prefix(name, i, s, a, tr_s, tr_a, snaps_s, snaps_a, prefixes, stats, fail, note)
                if i:
                    _transition(i, act, sp, s, ap, a,
                                rows[i - 1] if i - 1 < len(rows) else None, name, stats, fail, note)
                sp, ap = copy.deepcopy(s), copy.deepcopy(a)
            except (KeyError, TypeError, IndexError, AttributeError) as e:
                fail(case=name, prefix=i, check='retained-row-shape', expected='typed row',
                     observed=repr(e))
                sp, ap = copy.deepcopy(s), copy.deepcopy(a)
    need = {'stage_capture': stats['stage_events'], 'source_restart': stats['restart_events'],
            'publication_guard': stats['pub_guard_evaluations'],
            'journal_mirror': stats['journal_mirror_prefixes']}
    missing = sorted(k for k, v in need.items() if not v)
    if stats['mismatches']:
        status = 'counterexample'
    elif not audited:
        status = 'unproved' if halt else 'not_applicable'
    elif missing:
        status = 'unproved'
        lim.append('unwitnessed obligation classes in supplied cases: ' + ', '.join(missing))
    else:
        status = 'supported'
    if halt:
        lim.append(halt)
        if status == 'supported':
            status = 'unproved'
    if stats['pub_guard_evaluations'] and not stats['pub_guard_passes']:
        lim.append('no delegated current-source publication audited; guard evidenced by refusals only')
    if not stats['identity_rows']:
        lim.append('no staged-identity disjunct row audited; freshness-premise absence verified structurally only')
    obs.insert(0, {'accounting': stats})
    return {'status': status, 'observations': obs, 'limitations': lim, 'audited_prefixes': audited}
