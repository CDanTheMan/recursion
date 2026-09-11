"""Adversarial retained-evidence controls for obligation o14-setup-delivery
(parent goal-recursion-v2-execution-fabric): fixed original scale setup and
delivery establish Q-core coupling despite different completion masks; exact
hypotheses enumerated, no assumed success.

Representation only; no reducer/guard/boundary-helper/audit imports or execution.
Anchors: a_domain.initial+view (journal overlays core; boot token GEN+(0,));
a_inclusive/a_split.step (journal serial +1 per delegated restart); a_audit.check
(core.done==invocation bitmask over q_profile; source-only verbs never invoke Q);
s_inclusive.step attest/restart delegation; batch-05 semantic.field_pair/advance
(source_generation equal-or-paired; exact while both source_name empty; reasons
'paired-successful-attestation'/'paired-restart'); check.py run_history/audit_case
typed case+prefix replay; boundary.prefix_census generation/mask fields.

charge.take(1) precedes every inspected prefix of every pass; control repetitions
re-pay in full. Controls needing a genuinely reachable witness:
'paired-generation-decoupled' (post-attestation prefix), 'restart-not-propagated'
(delegated restart), 'refusal-hidden'/'dropped-delivery-invocation' (a refused /
delegated step); absent witnesses become missing-witness limitations, never
silent skips. 'unreachable-token' is labeled unreachable: a plumbing check, not
an original-domain counterexample.
"""
import copy, hashlib, json

GEN = ('cut-source', 'collectorA', 'effectA')
SRC = ('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:')
REASONS = ('paired-successful-attestation', 'paired-restart')
SETUP = ('admitA', 'intent', 'send', 'remote', 'lose', 'query')
POST = ('state', 'post', 'after', 'next', 'new_state', 'post_state', 'to', 'result')


def tok(g): return type(g) is tuple and len(g) == 4 and g[:3] == GEN and type(g[3]) is int

def dig(x): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def sronly(k): return k.startswith(SRC) or k in ('append-lose-reply', 'collect-open')

def js(x):
    if isinstance(x, dict): return {str(k): js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)): return [js(v) for v in x]
    return x if x is None or isinstance(x, (str, int, float, bool)) else str(x)

def ev(t, i):
    if i == 0: return t['initial']
    e = t['events'][i - 1]
    if isinstance(e, dict):
        for k in POST:
            if k in e: return e[k]
        if 'core' in e or 'source_generation' in e: return e
    if isinstance(e, (list, tuple)) and len(e) == 2: return e[1]
    raise ValueError('unrecognized retained event ' + str(i))

def states(t):
    out = [t['initial']] + [ev(t, i) for i in range(1, len(t['actions']) + 1)]
    if not all(isinstance(x, dict) for x in out): raise ValueError('non-dict retained state')
    return out


def inspect_cases(cases, charge):
    st_, lim, aud, cov, skip = {}, [], 0, False, 0
    if not cases: return {'status': 'not_applicable', 'observations': [], 'limitations': ['empty corpus'], 'audited_prefixes': 0}

    def h(n, i, c, e, o, ok):
        s = st_.setdefault(n, {'checked': 0, 'held': 0, 'first_failure': None, 'example': None}); s['checked'] += 1
        if ok:
            s['held'] += 1
            if s['example'] is None: s['example'] = {'case': c, 'prefix': i, 'expected': js(e), 'observed': js(o)}
        elif s['first_failure'] is None: s['first_failure'] = {'case': c, 'prefix': i, 'expected': js(e), 'observed': js(o)}

    masks = set()
    for case in cases:
        nm = case.get('case')
        try:
            ss, aa = states(case['source']), states(case['adapter'])
            acts, rows, pairs = list(case['source']['actions']), list(case['rows']), list(case['incarnation_pairs'])
            qa, pa = list(case['adapter']['q_profile']['actions']), list(case['source']['profile']['actions'])
            for i in range(len(ss)):
                charge.take(1); aud += 1
                s, a, c, j = ss[i], aa[i], aa[i]['core'], aa[i]['journal']
                iv, sg, cg = tuple(a['invocations']), s['source_generation'], c['source_generation']
                sc = [p for p in pairs if type(p.get('target_event')) is int and p['target_event'] < i
                      and tok(p.get('source')) and tok(p.get('target')) and p.get('reason') in REASONS]
                bd = any(p['source'] == sg and p['target'] == cg for p in sc)
                h('generation-coupling', i, nm, 'equal-or-bound', {'source': sg, 'core': cg, 'bound': bd}, sg == cg or bd)
                if not s['source_name'] and not c['source_name']: h('empty-name-exact', i, nm, sg, cg, sg == cg)
                h('name-agreement', i, nm, bool(s['source_name']), bool(c['source_name']), bool(s['source_name']) == bool(c['source_name']))
                nr = sum(1 for x in iv if x.split('@')[0] == 'source-restart')
                h('journal-ledger', i, nm, GEN + (nr,), j['source_generation'], j['source_generation'] == GEN + (nr,))
                try:
                    ok = c['done'] == sum(1 << qa.index(x) for x in iv) and a['done'] == sum(1 << pa.index(x) for x in acts[:i]) \
                        and set(iv) <= set(acts[:i]) and all(not sronly(x.split('@')[0]) for x in iv)
                    h('mask-accounting', i, nm, 'invocation/prefix bitmasks', {'core_done': c['done'], 'done': a['done'], 'inv': iv}, ok)
                except ValueError:
                    h('mask-accounting', i, nm, 'invocations inside q_profile', js(iv), False)
                if sg == cg or bd: masks.add(c['done'])
                if i:
                    at, k = acts[i - 1], acts[i - 1].split('@')[0]
                    if k in SETUP or sronly(k) or k == 'cut-deliver' or k.startswith('cut:'): cov = True
                    rw, ivd = rows[i - 1], at in iv and at not in aa[i - 1]['invocations']
                    h('invocation-flag', i, nm, ivd, rw.get('q_invoked'), 'q_invoked' in rw and rw['q_invoked'] == ivd)
                    so, ao = rw['source_observation']['decision'], rw['adapter_observation']['decision']
                    h('refusal-visibility', i, nm, so, ao, so == ao)
                    np_ = [p for p in pairs if p.get('target_event') == i - 1]
                    h('pair-origin', i, nm, 'new-binding iff pair', {'binding': rw.get('binding'), 'new': len(np_)},
                      'binding' in rw and (rw['binding'] == 'new-binding') == bool(np_))
                    h('pair-wellformed', i, nm, REASONS, [js(p) for p in np_],
                      all(tok(p.get('source')) and tok(p.get('target')) and p.get('reason') in REASONS for p in np_))
                    ps, pc, pj = ss[i - 1]['source_generation'], aa[i - 1]['core']['source_generation'], aa[i - 1]['journal']['source_generation']
                    if k == 'source-restart' and ivd:
                        h('restart-coupling', i, nm, 'all serials +1', {'s': sg, 'core': cg, 'journal': j['source_generation']},
                          sg == ps[:-1] + (ps[3] + 1,) and cg == pc[:-1] + (pc[3] + 1,) and j['source_generation'] == pj[:-1] + (pj[3] + 1,))
                    if k == 'source-attest':
                        if ivd and so == ao == 'source-attest:ok':
                            h('attest-coupling', i, nm, 'paired success', {'names': (s['source_name'], c['source_name']), 'bound': bd},
                              bool(s['source_name']) and s['source_name'] == c['source_name'] and (sg == cg or bd)
                              and any(p.get('reason') == REASONS[0] and p.get('target_event') == i - 1 for p in pairs))
                        else:
                            h('attest-refusal-clean', i, nm, 'no fabrication', {'s': s['source_name'], 'c': c['source_name']},
                              s['source_name'] == ss[i - 1]['source_name'] and c['source_name'] == aa[i - 1]['core']['source_name']
                              and not any(p.get('reason') == REASONS[0] and p.get('target_event') == i - 1 for p in pairs))
                    if not ivd: h('no-phantom-core', i, nm, dig(aa[i - 1]['core']), dig(c), dig(aa[i - 1]['core']) == dig(c))
                    if k == 'cut-deliver' or k.startswith('cut:'): h('delivery-delegated', i, nm, True, ivd, ivd)
        except (KeyError, TypeError, IndexError, ValueError) as e:
            lim.append({'case': nm, 'limitation': 'retained evidence unrestorable/missing fields: ' + str(e)}); skip += 1
    obs = [{'hypothesis': n, **v} for n, v in st_.items()] + [{'hypothesis': 'mask-diversity', 'distinct_core_done_masks': sorted(masks)}]
    if any(v['first_failure'] for v in st_.values()): st = 'counterexample'
    elif not aud: st = 'unproved' if lim else 'not_applicable'
    elif not cov: st = 'not_applicable'
    elif skip or lim: st = 'unproved'
    else: st = 'supported'
    return {'status': st, 'observations': obs, 'limitations': lim, 'audited_prefixes': aud}


def cand(case, f):
    ss, aa = states(case['source']), states(case['adapter'])
    return next((i for i in range(len(ss)) if f(i, ss[i], aa[i])), None)

def m_core_gen(c):
    i = cand(c, lambda n, s, a: n and not s['source_name'] and not a['core']['source_name'])
    if i is None: return None
    e = ev(c['adapter'], i); e['core']['source_generation'] = GEN + (e['core']['source_generation'][3] + 7,); return True

def m_journal(c):
    e = ev(c['adapter'], 1); g = e['journal']['source_generation']
    e['journal']['source_generation'] = GEN + (g[3] + 1,) if tok(g) else GEN + (1,); return True

def m_phantom(c):
    i = cand(c, lambda n, s, a: n and c['source']['actions'][n - 1] not in a['invocations'])
    if i is None: return None
    e = ev(c['adapter'], i); e['core']['publication_reads'] = e['core'].get('publication_reads', 0) + 1; return True

def m_drop_delivery(c):
    aa = states(c['adapter']); acts, qa = c['source']['actions'], list(c['adapter']['q_profile']['actions'])
    d = next((n for n, x in enumerate(acts) if x.split('@')[0] == 'cut-deliver'), None)
    if d is None or acts[d] not in aa[d + 1]['invocations']: return None
    for n in range(d + 1, len(aa)):
        e = ev(c['adapter'], n); e['invocations'] = tuple(x for x in e['invocations'] if x != acts[d])
        e['core']['done'] = sum(1 << qa.index(x) for x in e['invocations'])
    return True

def m_forge(c):
    c['incarnation_pairs'].append({'source': GEN + (0,), 'target': GEN + (0,), 'reason': 'paired-restart',
                                   'source_event': 0, 'target_event': 0}); return True

def m_unreach(c): ev(c['adapter'], 1)['journal']['source_generation'] = ('forged',); return True

def m_hide_refusal(c):
    r = next((r for r in c['rows'] if not r['source_observation']['decision'].endswith(':ok')), None)
    if r is None: return None
    r['adapter_observation']['decision'] = r['source_observation']['decision'].split(':')[0] + ':ok'; return True

def m_mask_lie(c):
    e = ev(c['adapter'], len(c['source']['actions'])); e['core']['done'] ^= 1; return True

def m_pair_dec(c):
    i = cand(c, lambda n, s, a: s['source_name'] and a['core']['source_name'])
    if i is None: return None
    ev(c['adapter'], i)['core']['source_generation'] = GEN + (99,); return True

def m_restart_skip(c):
    i = cand(c, lambda n, s, a: n and c['source']['actions'][n - 1].split('@')[0] == 'source-restart'
             and c['source']['actions'][n - 1] in a['invocations'])
    if i is None: return None
    ev(c['adapter'], i)['core']['source_generation'] = ev(c['adapter'], i - 1)['core']['source_generation']; return True


CONTROLS = (('core-generation-decoupled', 1, m_core_gen), ('journal-boot-serial-decoupled', 1, m_journal),
            ('phantom-core-field', 1, m_phantom), ('dropped-delivery-invocation', 1, m_drop_delivery),
            ('forged-pair-injection', 1, m_forge), ('refusal-hidden', 1, m_hide_refusal),
            ('mask-lie', 1, m_mask_lie), ('paired-generation-decoupled', 1, m_pair_dec),
            ('restart-not-propagated', 1, m_restart_skip), ('unreachable-token', 0, m_unreach))


def run_controls(cases, inspect_cases, charge):
    res, lim = [], []
    for case in cases or ():
        for lb, rc, mu in CONTROLS:
            mc = copy.deepcopy(case)
            try: ap = mu(mc)
            except (KeyError, IndexError, TypeError, ValueError) as e: ap = 'mutation error: ' + str(e)
            if ap is not True:
                lim.append({'control': lb, 'case': case.get('case'),
                            'limitation': 'no genuinely reachable witness' if ap is None else ap})
                continue
            r = inspect_cases([mc], charge)
            res.append({'control': lb, 'case': case.get('case'), 'reachable_shape': bool(rc),
                        'expected': 'counterexample', 'observed': r['status'],
                        'detected': r['status'] == 'counterexample', 'audited_prefixes': r['audited_prefixes']})
    return {'controls': res, 'limitations': lim, 'evaluated': len(res),
            'all_detected': bool(res) and all(x['detected'] for x in res),
            'note': 'no scientific PASS; unreachable mutations are plumbing checks, not domain counterexamples'}
