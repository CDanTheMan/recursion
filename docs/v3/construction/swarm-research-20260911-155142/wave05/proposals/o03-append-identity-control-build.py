"""Bounded retained-certificate check + adversarial controls, obligation o03.

Setup append owner/incarnation/request/body idempotency, first-versus-last
append_receipts lookup and the reachable unique-request-key invariant over
actual typed restored cases. Anchors (representation only; no reducer
execution, no boundary-helper imports): s_domain.py append_request (request
id 'append-<i>'['-fresh'], caller, boot incarnation, ordinal, raw bytes);
s_inclusive.py/guard_a.py first-match lookup vs s_split.py/guard_b.py
last-entry dict lookup, equal only under unique request keys (prestage
correspondence analysis, reachable-shape qualification); s_audit.py
invariant (unique ids, retained bytes at admitted ordinal, sha256-bound
receipt); check.py audit_case restore and Counter charge convention.

charge.take(1) precedes EVERY inspected prefix of every case, repetitions
included; audited_prefixes equals charges. 'supported' only means every
audited prefix passed every check and >=1 append witness was inspected;
never a global theorem. 'unproved' marks vacuous scope; 'counterexample'
returns falsifiable expected/observed witnesses. run_controls deepcopy-
mutates retained cases, then re-seals outer digests (every stored copy of
a mutated state's old digest is replaced) so detection must reach
semantics, not integrity. Mutations are constructed corruptions, never
original-domain reachability claims. 'duplicate-replays-last-match' needs
a genuinely reachable post-duplicate witness; missing witnesses are kept
as limitations, as are absent duplicate/lose-reply decisions.
"""
import copy, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/eight-hour-research-20260910-01a08a22'))
try:
    import check as c  # frozen checker: trace restore/digest only, never reducers
except ImportError:
    c = None

TOKEN = ('cut-source', 'collectorA', 'effectA')
APPEND_FIELDS = ('registration', 'attempts', 'append_log', 'append_receipts', 'append_reply', 'source_revision')


def _typed(x):
    if isinstance(x, dict): return ['dict', [[k, _typed(v)] for k, v in sorted(x.items())]]
    if isinstance(x, (list, tuple)): return [type(x).__name__, [_typed(v) for v in x]]
    return [type(x).__name__, x]


def _exact(a, b): return _typed(a) == _typed(b)
def _digest(raw): return hashlib.sha256(json.dumps(raw, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
def _rows(s): return list(s.get('append_receipts') or ())


def _js(x):
    if isinstance(x, dict): return {str(k): _js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [_js(v) for v in x]
    return x if x is None or isinstance(x, (bool, int, float, str)) else repr(x)


def _bad(ci, i, side, check, expected, observed):
    return dict(case=ci, prefix=i, side=side, check=check, expected=_js(expected), observed=_js(observed))


def _state(s, ci, i, side, v, w):
    rs = _rows(s)
    w['receipt_rows'] += len(rs); w['states_with_receipts'] += bool(rs)
    keys = [r[0] for r in rs]
    if len(set(keys)) != len(keys):
        v.append(_bad(ci, i, side, 'unique-request-key', 'distinct request ids', keys))
    last = {r[0]: r for r in rs}
    diff = {k: (f, last[k]) for k, f in {r[0]: r for r in reversed(rs)}.items() if not _exact(f, last[k])}
    if diff: v.append(_bad(ci, i, side, 'first-vs-last-lookup', 'first==last per request', diff))
    reply = s.get('append_reply') or ()
    if reply and not any(_exact(reply, r[2]) for r in rs):
        v.append(_bad(ci, i, side, 'reply-is-retained-receipt', 'member of receipts', reply))
    gen, log = s.get('source_generation') or (), s.get('append_log') or ()
    live = gen[3] if len(gen) == 4 and type(gen[3]) is int else None
    for r in rs:
        if not (isinstance(r, (list, tuple)) and len(r) == 3 and isinstance(r[1], (list, tuple))
                and len(r[1]) == 4 and isinstance(r[2], (list, tuple)) and len(r[2]) == 4):
            v.append(_bad(ci, i, side, 'receipt-row-shape', '(request,body,receipt)', r)); continue
        req, body, rc = r
        if body[0] != 'collectorA': v.append(_bad(ci, i, side, 'append-owner', 'collectorA', body[0]))
        if not (isinstance(body[1], (list, tuple)) and len(body[1]) == 4 and tuple(body[1][:3]) == TOKEN
                and type(body[1][3]) is int and 0 <= body[1][3] <= (live if live is not None else body[1][3])):
            v.append(_bad(ci, i, side, 'append-incarnation', 'local token <= live index', body[1]))
        names = ('append-%d' % body[2], 'append-%d-fresh' % body[2]) if type(body[2]) is int else ()
        if req not in names: v.append(_bad(ci, i, side, 'request-key-binds-ordinal', 'append-<int>[-fresh]', req))
        if not (type(body[2]) is int and 0 <= body[2] < len(log) and _exact(log[body[2]], body[3])):
            v.append(_bad(ci, i, side, 'retained-bytes-at-ordinal', 'log[index]==bytes', (body[2], len(log))))
        if not (rc[0] == req and type(rc[1]) is int and 1 <= rc[1] <= (s.get('source_revision') or 0)
                and rc[2] == body[2] and rc[3] == _digest(body[3])):
            v.append(_bad(ci, i, side, 'immutable-receipt', 'sha256-bound receipt', rc))


def _edge(case, ss, aa, i, ci, v, w, adm):
    actions = case['source'].get('actions') or ()
    if i - 1 >= len(actions):
        v.append(_bad(ci, i, 'both', 'action-cardinality', 'action per prefix', len(actions))); return
    s, ps = ss[i], ss[i - 1]
    j = (aa[i].get('journal') or {}) if i < len(aa) else {}
    pj = (aa[i - 1].get('journal') or {}) if i - 1 < len(aa) else {}
    sdec = s.get('decision'); jdec = aa[i].get('decision') if i < len(aa) else None
    rows = case.get('rows') or []
    if i - 1 < len(rows) and (rows[i - 1].get('source_observation') or {}).get('decision') != sdec:
        v.append(_bad(ci, i, 'source', 'row-binds-decision', sdec, rows[i - 1].get('source_observation')))
    if sdec != jdec: v.append(_bad(ci, i, 'both', 'decision-agreement', sdec, jdec))
    verb = actions[i - 1].split('@')[0]
    if verb == 'append-lose-reply':
        w['lose_reply'] += 1
        if s.get('append_reply') != () or j.get('append_reply') != ():
            v.append(_bad(ci, i, 'both', 'lose-reply-clears', (), (s.get('append_reply'), j.get('append_reply'))))
        return
    if not verb.startswith('append:'): return
    p = verb.split(':')
    req = 'append-' + (p[2] if len(p) > 2 else '') + ('-fresh' if len(p) > 3 and p[3] == 'fresh' else '')
    for side, cur, prev, dec in (('source', s, ps, sdec), ('journal', j, pj, jdec)):
        prs, crs = _rows(prev), _rows(cur)
        if dec == verb + ':ok':
            w['ok_appends'] += 1; adm[side] += 1
            if not (len(crs) == len(prs) + 1 and crs[-1][0] == req and _exact(cur.get('append_reply'), crs[-1][2])):
                v.append(_bad(ci, i, side, 'append-ok-admits-once', 'one receipt+reply', (req, cur.get('append_reply'))))
        elif dec == verb + ':duplicate':
            w['duplicate_decisions'] += 1
            pf, pl = {r[0]: r for r in reversed(prs)}, {r[0]: r for r in prs}
            if not (req in pf and _exact(crs, prs) and _exact(cur.get('append_reply'), pf[req][2])
                    and _exact(pf[req][2], pl[req][2])):
                v.append(_bad(ci, i, side, 'duplicate-replays-first-match', pf.get(req), cur.get('append_reply')))
        elif isinstance(dec, str) and dec.startswith(verb + ':'):
            if not (_exact(crs, prs) and _exact(cur.get('append_reply'), prev.get('append_reply'))):
                v.append(_bad(ci, i, side, 'refusal-preserves-receipts', 'receipts+reply unchanged', dec))
        else:
            v.append(_bad(ci, i, side, 'decision-names-verb', verb + ':*', dec))


def inspect_cases(cases, charge):
    if not cases or c is None:
        why = 'no supplied typed cases' if not cases else 'frozen checker import unavailable'
        return dict(status='not_applicable' if not cases else 'unproved', observations=[],
                    limitations=[why], audited_prefixes=0)
    v, lim, audited = [], [], 0
    w = dict(receipt_rows=0, states_with_receipts=0, ok_appends=0, duplicate_decisions=0, lose_reply=0)
    for ci, case in enumerate(cases):
        try:
            ss, aa = list(c.t.restore(case['source'])), list(c.t.restore(case['adapter']))
        except Exception as e:
            v.append(_bad(ci, None, 'both', 'typed-restore', 'restored prefixes', repr(e)[:160])); continue
        if len(ss) != len(case['source'].get('actions') or ()) + 1 or len(aa) != len(ss):
            v.append(_bad(ci, None, 'both', 'prefix-cardinality', len(case['source'].get('actions') or ()) + 1,
                          (len(ss), len(aa))))
        adm = {'source': 0, 'journal': 0}
        for i in range(len(ss)):
            charge.take(1); audited += 1
            s, j = ss[i], (aa[i].get('journal') or {}) if i < len(aa) else {}
            _state(s, ci, i, 'source', v, w); _state(j, ci, i, 'adapter-journal', v, w)
            for k in APPEND_FIELDS:
                if not _exact(s.get(k), j.get(k)):
                    v.append(_bad(ci, i, 'journal-vs-source', k, (s.get(k), j.get(k))))
            if i: _edge(case, ss, aa, i, ci, v, w, adm)
            for side, cur in (('source', s), ('journal', j)):
                if len(_rows(cur)) != adm[side]:
                    v.append(_bad(ci, i, side, 'receipts-equal-admissions', adm[side], len(_rows(cur))))
    status = 'counterexample' if v else 'supported' if (w['receipt_rows'] or w['ok_appends']) else 'unproved'
    if status == 'unproved': lim.append('no append receipts or admissions inspected')
    if not w['duplicate_decisions']: lim.append('no reachable append:*:duplicate decision; replay claim unwitnessed')
    if not w['lose_reply']: lim.append('no reachable append-lose-reply inspected')
    obs = v[:40] + [dict(audited_witnesses=w, cases=len(cases), truncated_violations=max(0, len(v) - 40))]
    return dict(status=status, observations=_js(obs), limitations=lim, audited_prefixes=audited)


def _walk(node, out):
    if isinstance(node, dict):
        if 'append_receipts' in node and 'append_log' in node: out.append(node)
        for x in node.values(): _walk(x, out)
    elif isinstance(node, (list, tuple)):
        for x in node: _walk(x, out)


def _rehash(node, old, new):
    items = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else ()
    for k, x in items:
        if x == old: node[k] = new
        else: _rehash(x, old, new)


def _mut(case, fn, scope):
    m, states, seals = copy.deepcopy(case), [], {}
    _walk(m if scope is None else m.get(scope) or {}, states)
    for st in states:
        old = c.d.digest(st) if c else None
        try: changed = fn(st)
        except (KeyError, IndexError, TypeError, ValueError): changed = False
        if changed and old is not None: seals[old] = c.d.digest(st)
    for old, new in seals.items(): _rehash(m, old, new)
    return m, bool(seals)


def _apply(st, f):
    patch = f(st)
    if patch is None: return False
    st.update(patch); return True


def _row1(st, f):
    rs = _rows(st)
    return {'append_receipts': (f(*rs[0]),) + tuple(rs[1:])} if rs else None


def run_controls(cases, inspect_cases, charge):
    base = inspect_cases(cases, charge)
    out = [dict(control='baseline-clean-evidence', expected='no counterexample', observed=base['status'],
                detected=None, ok=base['status'] != 'counterexample', audited_prefixes=base['audited_prefixes'],
                original_domain_counterexample=base['status'] == 'counterexample')]
    dup = lambda s: {'append_receipts': tuple(_rows(s)) + ((_rows(s)[0][0], ('collectorA', _rows(s)[0][1][1],
        _rows(s)[0][1][2], str(_rows(s)[0][1][3]) + ' '), ('x', 0, 0, '0' * 64)),)} if _rows(s) else None
    phantom = lambda s: {'append_receipts': tuple(_rows(s)) + (('append-0-fresh', ('collectorA', TOKEN + (0,),
        0, s['append_log'][0]), ('append-0-fresh', 1, 0, _digest(s['append_log'][0]))),)} if s.get(
        'append_log') and 'append-0-fresh' not in {r[0] for r in _rows(s)} else None
    specs = [
        ('duplicate-request-key', None, lambda s: _apply(s, dup), 'unique-request-key', False),
        ('journal-only-receipt-dropped', 'adapter',
         lambda s: _apply(s, lambda t: {'append_receipts': tuple(_rows(t)[1:])} if _rows(t) else None),
         'journal-vs-source', False),
        ('foreign-append-owner', None,
         lambda s: _apply(s, lambda t: _row1(t, lambda q, b, r: (q, ('collectorB',) + tuple(b[1:]), r))),
         'append-owner', False),
        ('foreign-append-incarnation', None,
         lambda s: _apply(s, lambda t: _row1(t, lambda q, b, r: (q, ('foreign', 'boot', 'token', 0), r))),
         'append-incarnation', False),
        ('retained-bytes-corrupted', None, lambda s: _apply(s, lambda t: {'append_log': tuple(
            t['append_log'][:-1]) + (str(t['append_log'][-1]) + 'x',)} if t.get('append_log') else None),
         'retained-bytes-at-ordinal', False),
        ('phantom-unadmitted-receipt', None, lambda s: _apply(s, phantom), 'receipts-equal-admissions', False),
        ('stray-append-reply', None, lambda s: _apply(s, lambda t: None if t.get('append_reply') else
            {'append_reply': ('forged', 0, 0, '0' * 64)}), 'reply-is-retained-receipt', False),
        ('duplicate-replays-last-match', None, lambda s: _apply(s, lambda t: {'append_reply': _rows(t)[-1][2]}
            if _rows(t) and t.get('append_reply') and not _exact(t['append_reply'], _rows(t)[-1][2]) else None),
         'duplicate-replays-first-match', True),
    ]
    for name, scope, fn, check, needs in specs:
        rec = dict(control=name, kind='constructed-retained-corruption', scope=scope or 'both',
                   claims_reachability=False, requires_reachable_witness=needs, expected_check=check)
        for ci, case in enumerate(cases):
            m, applied = _mut(case, fn, scope)
            if not applied: continue
            res = inspect_cases([m], charge)
            seen = [o.get('check') for o in res['observations'] if isinstance(o, dict) and o.get('check')]
            rec.update(case=ci, applied=True, expected='counterexample', observed=res['status'],
                       detected=res['status'] == 'counterexample', expected_check_seen=check in seen,
                       observed_checks=seen[:8], audited_prefixes=res['audited_prefixes'])
            break
        else:
            rec.update(applied=False, observed='not_applicable', detected=None,
                       limitation='required witness state absent from supplied cases; control unproved')
        out.append(rec)
    lim = ['digests inside immutable tuple containers are not re-sealed; detection there surfaces via typed-restore']
    return dict(controls=out, limitations=lim,
                note='mutations are constructed corruptions re-sealed at outer digests, never reachability claims')
