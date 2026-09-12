"""Retained-evidence controls for obligation o04-append-order.

Binds supplied restored typed cases (c.run_history/c.artifact pipeline) only;
no all-order, Q-reachability or acceptance claim. Independent representation
mirrors unchanged originals: literal append decode and guard precedence
s_audit.py/guard_audit.py append branch; request/body/variant map s_domain.py
append_request; receipt (request, revision, index, sha256(encoded raw));
invariant surface s_audit.py invariant; adapter ledger mirror a_audit.py;
row observations batch-05/semantic.py; typed prefix states c.t.restore.
No reducer/model or boundary-helper execution. charge.take(1) precedes every
inspected prefix of every inspection, control repetitions included;
audited_prefixes equals units taken. Controls needing a genuinely reachable
witness (else a missing-witness limitation and the claim stays unproved):
append-accepted, append-gap-or-fork, unregistered-attempt,
foreign-record-scope, append-lose-reply, reply-restored-after-loss.
"""
import copy, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/eight-hour-research-20260910-01a08a22'))
import check as c

d = c.d
FIELDS = ('registration', 'attempts', 'append_log', 'append_receipts', 'append_reply', 'source_revision')
SCOPE = ('effect_id', 'idempotency_key', 'payload_digest', 'target_ref', 'admission_epoch', 'fence_epoch')
REQUIRED = ('append-accepted', 'append-gap-or-fork', 'unregistered-attempt', 'foreign-record-scope',
            'append-lose-reply', 'reply-restored-after-loss')

def enc(v): return json.dumps(v, sort_keys=True, separators=(',', ':'))

def js(x):
    if isinstance(x, dict): return {str(k): js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [js(v) for v in x]
    return x if type(x) in (str, int, float, bool, type(None)) else repr(x)

def expected(s, k):
    _, name, idx, var = k.split(':')
    idx, rec = int(idx), dict(d.q.lit.fixture(name)['original']['records'][int(idx)])
    req, caller = 'append-' + str(idx), 'collectorB' if var == 'foreign' else 'collectorA'
    boot = ('cut-source', 'collectorA', 'effectA', 1 if var == 'new-boot' else 0)
    rec.update({'wrong-attempt': {'attempt_id': 'attempt:foreign'},
                'wrong-body': {'payload_digest': 'sha256:' + '9' * 64}}.get(var, {}))
    if var == 'fresh': req += '-fresh'
    body, rows = (caller, boot, idx, enc(rec)), [r for r in s['append_receipts'] if r[0] == req]
    reason = ('wrong-append-owner' if caller != 'collectorA' else
              ('duplicate' if d.exact(rows[0][1], body) else 'append-id-conflict') if rows else
              'stale-append-incarnation' if not d.exact(boot, s['source_generation']) else
              'E-PAUSED' if s['paused'] else 'no-registration' if not s['registration'] else
              'append-gap-or-fork' if idx != len(s['append_log']) else
              'unregistered-attempt' if all(p[1] != rec['attempt_id'] for p in s['attempts']) else
              'foreign-record-scope' if any(rec[f] != json.loads(s['registration'])[0][f] for f in SCOPE)
              else 'ok')
    return reason, req, body, rows[0][2] if rows else (
        req, s['source_revision'] + 1, idx, hashlib.sha256(enc(body[3]).encode()).hexdigest())

def invariant_bad(s):
    bad = []
    if len({r[0] for r in s['append_receipts']}) != len(s['append_receipts']): bad.append('dup-request-id')
    for req, body, receipt in s['append_receipts']:
        ok = (type(body) is tuple and len(body) == 4 and type(receipt) is tuple and len(receipt) == 4
              and receipt[0] == req and receipt[2] == body[2] and 0 < receipt[1] <= s['source_revision']
              and receipt[3] == hashlib.sha256(enc(body[3]).encode()).hexdigest()
              and 0 <= body[2] < len(s['append_log']) and d.exact(s['append_log'][body[2]], body[3]))
        if not ok: bad.append('receipt-or-position:' + str(req))
    if s['source_revision'] < len(s['attempts']) + len(s['append_receipts']) + bool(s['registration']):
        bad.append('revision-coverage')
    if s['append_reply'] and not any(d.exact(r[2], s['append_reply']) for r in s['append_receipts']):
        bad.append('reply-not-durable')
    return bad

def event_bad(s, n, action):
    k, delta = action.split('@')[0], n['source_revision'] - s['source_revision']
    if k.startswith('append:'):
        reason, req, body, receipt = expected(s, k)
        bad = [] if n['decision'] == k + ':' + reason else ['decision=' + str(n['decision'])]
        want = {f: s[f] for f in FIELDS}
        if reason == 'ok':
            want.update(append_log=s['append_log'] + (body[3],), source_revision=s['source_revision'] + 1,
                        append_receipts=s['append_receipts'] + ((req, body, receipt),))
        want['append_reply'] = receipt if reason in ('ok', 'duplicate') else s['append_reply']
        return reason, bad + [f for f in want if not d.exact(n[f], want[f])]
    if k == 'append-lose-reply':
        bad = [f for f in FIELDS if f != 'append_reply' and not d.exact(n[f], s[f])]
        if n['append_reply'] != () or n['decision'] != k + ':ok': bad.append('reply-not-cleared')
        return 'append-lose-reply', bad
    if k.startswith(('attempt:', 'atomic:')):
        num = json.loads(d.s.records(k.split(':')[1])[int(k.split(':')[2])])['attempt_number'] \
            if k.startswith('atomic:') else int(k.split(':')[1])
        pair = ('attemptA' if num == 1 else 'retained-attemptA' + str(num), 'attempt:' + str(num))
        grew = n['attempts'] == s['attempts'] + (pair,) and delta == 1
        return 'attempt', [] if (n['decision'] == k + ':ok') == grew else ['attempt-record-or-revision']
    inc = n['decision'] == k + ':ok' and not s['registration'] if k.startswith('register:') else False
    return 'other', [] if delta == inc else ['revision-drift']

def inspect_cases(cases, charge):
    seen, reasons, bad, audited = {w: 0 for w in REQUIRED}, {}, [], 0
    for case in cases:
        try:
            ss, aa = c.t.restore(case['source']), c.t.restore(case['adapter'])
            actions, rows = tuple(case['source']['actions']), case['rows']
            shape = tuple(case['adapter']['actions']) == actions and len(rows) == len(actions) \
                and len(ss) == len(aa) == len(actions) + 1
        except Exception as e:
            bad.append(dict(case=case.get('case'), control='typed-restore', observed=repr(e)))
            continue
        if not shape:
            bad.append(dict(case=case.get('case'), control='case-frame', observed='lengths disagree'))
        for i in range(len(actions) + 1):
            charge.take(1)
            audited += 1
            if not shape: continue
            s, a = ss[i], aa[i]
            def flag(control, **kw): bad.append(dict(case=case.get('case'), prefix=i, control=control, **kw))
            for f in invariant_bad(s): flag('append-invariant', observed=f)
            for f in FIELDS:
                if not d.exact(a['journal'].get(f), s[f]): flag('journal-mirror', observed=f)
            if i == 0:
                if any(s[f] for f in FIELDS[1:5]) or s['source_revision']: flag('initial-append-state')
                continue
            action, k, row = actions[i - 1], actions[i - 1].split('@')[0], rows[i - 1]
            sobs, aobs = row.get('source_observation', {}), row.get('adapter_observation', {})
            if not (row.get('source_action') == row.get('adapter_action') == action):
                flag('literal-action', observed=row.get('source_action'))
            for side, obs, dec in (('source', sobs, s['decision']), ('adapter', aobs, a['decision'])):
                if not d.exact(obs.get('decision'), dec):
                    flag(side + '-decision', expected=dec, observed=obs.get('decision'))
            if row.get('q_invoked') and (k.startswith(('register:', 'attempt:', 'atomic:', 'append:',
                    'collect:', 'source:')) or k in ('append-lose-reply', 'collect-open')):
                flag('false-q-invocation', observed=action)
            if (k.startswith('append:') or k == 'append-lose-reply') \
                    and not d.exact(sobs.get('append_reply'), s['append_reply']):
                flag('reply-observation', expected=s['append_reply'], observed=sobs.get('append_reply'))
            try:
                reason, errors = event_bad(ss[i - 1], s, action)
            except Exception as e:
                reason, errors = 'decode-error', [repr(e)]
            for f in errors: flag('append-order', action=action, observed=f)
            seen['append-accepted'] += reason == 'ok'
            if reason in seen: seen[reason] += 1
            seen['reply-restored-after-loss'] += reason == 'duplicate' and ss[i - 1]['append_reply'] == ()
            if reason not in ('ok', 'attempt', 'other', 'decode-error', 'append-lose-reply'):
                reasons[reason] = reasons.get(reason, 0) + 1
    missing = [w for w in REQUIRED if not seen[w]]
    status = ('counterexample' if bad else 'not_applicable' if not any(seen.values())
              else 'unproved' if missing else 'supported')
    lim = ['register/collect/atomic bodies audited only via revision and invariant surface',
           'observations bind supplied cases only; no statement about unexecuted orders',
           *(['no reachable witness in supplied cases: ' + ','.join(missing)] if missing else [])]
    return dict(status=status, limitations=lim, audited_prefixes=audited,
                observations=js(dict(cases=len(cases), witnesses=seen, refusal_reasons=reasons,
                                     violation_count=len(bad), violations=bad[:8])))

def run_controls(cases, inspect_cases, charge):
    controls, charged = [], 0
    def dep_ok(profile, actions):
        done = set()
        for a in actions:
            if not set(profile['requires'].get(a, ())) <= done: return False
            done.add(a)
        return True
    def trial(label, domain, pred, mutate):
        nonlocal charged
        case = i = None
        for cand in cases:
            try: i = next((j for j, a in enumerate(cand['source']['actions']) if pred(cand, j, a.split('@')[0])), None)
            except Exception: i = None
            if i is not None: case = cand; break
        if case is None:
            controls.append(dict(control=label, status='not_applicable', mutation_domain=domain))
            return
        mutant = copy.deepcopy(case)
        mutate(mutant, i)
        r = inspect_cases([mutant], charge)
        charged += r['audited_prefixes']
        try: dep = dep_ok(mutant['source']['profile'], mutant['source']['actions'])
        except Exception: dep = None
        controls.append(dict(control=label, case=case.get('case'), event_index=i, mutation_domain=domain,
                             dependency_valid=dep, detected=r['status'] == 'counterexample',
                             observed_status=r['status'],
                             first_violations=r['observations'].get('violations', [])[:2]))
    sob = lambda m, i: m['rows'][i]['source_observation']
    trial('baseline-unmodified', 'original-domain', lambda c, i, k: True, lambda m, i: None)
    trial('forged-reply-loss-on-accepted-append', 'original-domain',
          lambda c, i, k: k.startswith('append:') and str(sob(c, i).get('decision')).endswith(':ok'),
          lambda m, i: sob(m, i).update(append_reply=()))
    trial('dropped-append-refusal', 'original-domain',
          lambda c, i, k: k.startswith('append:') and not str(sob(c, i).get('decision')).endswith(':ok'),
          lambda m, i: sob(m, i).update(decision=m['source']['actions'][i].split('@')[0] + ':ok'))
    trial('false-q-invocation-on-append', 'original-domain',
          lambda c, i, k: k.startswith('append:'), lambda m, i: m['rows'][i].update(q_invoked=True))
    trial('restored-duplicate-reply-erased', 'original-domain',
          lambda c, i, k: str(sob(c, i).get('decision')).endswith(':duplicate'),
          lambda m, i: sob(m, i).update(append_reply=()))
    trial('reply-loss-erased', 'original-domain', lambda c, i, k: k == 'append-lose-reply',
          lambda m, i: sob(m, i).update(append_reply=('append-0', 1, 0, '0' * 64)))
    def swap(m, i):
        acts = list(m['source']['actions'])
        acts[i - 1], acts[i] = acts[i], acts[i - 1]
        m['source']['actions'] = m['adapter']['actions'] = tuple(acts)
    trial('swapped-append-order', 'unreachable-dependency-violation',
          lambda c, i, k: k.startswith('append:') and i > 0, swap)
    return dict(controls=js(controls), audited_prefixes=charged,
                limitations=['mutations touch retained rows/schedule literals only; typed event bytes unchanged',
                             'detection exercises the checker surface, not a refutation of the original relation'])
