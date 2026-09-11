"""Independent adversarial controls for obligation o14-setup-delivery
(parent goal-recursion-v2-execution-fabric; boundary-01 scale-eight-action-race).
The audited claim: fixed setup (@0-@10) and delivery (@19-@20) keep the source
projection and the adapter Q core coupled although outer and inner completion
masks differ. Each control deep-copies a retained typed case (check.py
run_history shape: initials, actions, rows, prefixes, incarnation_pairs,
q_profile, events), applies exactly one corruption and replays it through the
injected inspect_cases. No reducer, guard, boundary helper, trace restore or
model code is imported or executed.
charge.take(1) precedes the baseline replay of every case, every mutation
application and every mutated replay; shared or repeated case objects are
re-paid in full; a refused take is recorded and evaluation stops. 'detected'
requires observed status 'counterexample' verbatim on a mutation that changed
retained bytes; 'discriminating' additionally requires the clean baseline was
not already 'counterexample'. Inspector exceptions, 'unproved' and
'not_applicable' are never counted as detection. Every control binds the
original witness it needs; absent witnesses become missing-witness
limitations, never silent skips. The batch-07 event encoding is unsupplied, so
post-state corruption is limited to one explicitly schema-guarded event
control; attestation is refused in both subclasses, so pair controls needing
an existing pair are expected to report missing witnesses. 'outer-hash-only'
is plumbing: hash rejection alone is not semantic discrimination. Results are
JSON-safe; no scientific PASS or acceptance is claimed.
"""
import copy, hashlib, json

GEN = ('cut-source', 'collectorA', 'effectA')

def tok(g): return type(g) is tuple and len(g) == 4 and g[:3] == GEN and type(g[3]) is int and g[3] >= 0

def verb(a): return a.partition('@')[0] if isinstance(a, str) else ''

def rows(c):
    r = c.get('rows') if isinstance(c, dict) else None
    return r if isinstance(r, (list, tuple)) else ()

def find(c, pred):
    for i, r in enumerate(rows(c)):
        if isinstance(r, dict) and pred(i, r): return r
    return None

def dec(row, side):
    o = row.get(side + '_observation')
    return o.get('decision') if isinstance(o, dict) else None

def refused(row):
    d = dec(row, 'adapter')
    return isinstance(d, str) and ':' in d and not d.endswith(':ok')

def js(x, depth=0):
    if depth > 8 or x is None or isinstance(x, (bool, int, float, str)): return x
    if isinstance(x, dict): return {str(k): js(v, depth + 1) for k, v in sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (list, tuple)): return [js(v, depth + 1) for v in x]
    if isinstance(x, (set, frozenset)): return sorted((js(v, depth + 1) for v in x), key=repr)
    return repr(x)

def dig(x): return hashlib.sha256(json.dumps(js(x), sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def post_state(e):
    if isinstance(e, dict):
        if isinstance(e.get('core'), dict): return e
        for k in ('post', 'state', 'after', 'next', 'new_state', 'post_state', 'to', 'result'):
            v = e.get(k)
            if isinstance(v, dict) and isinstance(v.get('core'), dict): return v
    if isinstance(e, (list, tuple)) and len(e) == 2 and isinstance(e[1], dict): return e[1]
    return None

def m_attest_invoked(c):
    r = find(c, lambda i, x: verb(x.get('source_action')) == 'source-attest' and x.get('q_invoked') is False and refused(x))
    if r is None: return None
    r['q_invoked'] = True; return True

def m_refusal_hidden(c):
    r = find(c, lambda i, x: refused(x) and dec(x, 'adapter') == dec(x, 'source'))
    if r is None: return None
    r['adapter_observation']['decision'] = dec(r, 'adapter').split(':')[0] + ':ok'; return True

def m_delivery_dropped(c):
    hits = [r for r in rows(c) if isinstance(r, dict) and r.get('q_invoked') is True
            and (verb(r.get('source_action')) == 'cut-deliver' or verb(r.get('source_action')).startswith('cut:'))]
    if not hits: return None
    for r in hits: r['q_invoked'] = False
    return True

def m_restart_dropped(c):
    r = find(c, lambda i, x: verb(x.get('source_action')) == 'source-restart' and x.get('q_invoked') is True)
    if r is None: return None
    r['q_invoked'] = False; return True

def m_core_generation0(c):
    core = ((c.get('adapter') or {}).get('initial') or {}).get('core')
    if not isinstance(core, dict): return 'adapter initial core absent'
    if not tok(core.get('source_generation')): return 'initial core generation is not a scoped token'
    core['source_generation'] = GEN + (core['source_generation'][3] + 7,); return True

def m_journal_generation0(c):
    jour = ((c.get('adapter') or {}).get('initial') or {}).get('journal')
    if not isinstance(jour, dict): return 'adapter initial journal absent'
    if not tok(jour.get('source_generation')): return 'initial journal generation is not a scoped token'
    jour['source_generation'] = GEN + (jour['source_generation'][3] + 1,); return True

def m_forged_pair_laundering(c):
    src, core, pairs = (c.get('source') or {}).get('initial'), ((c.get('adapter') or {}).get('initial') or {}).get('core'), c.get('incarnation_pairs')
    if not (isinstance(src, dict) and isinstance(core, dict) and isinstance(pairs, (list, tuple))): return 'initial states or pair ledger absent'
    if not tok(src.get('source_generation')): return 'source initial generation is not a scoped token'
    core['source_generation'] = forged = GEN + (src['source_generation'][3] + 9,)
    pair = {'source': src['source_generation'], 'target': forged, 'reason': 'paired-restart', 'source_event': 0, 'target_event': 0}
    c['incarnation_pairs'] = pairs + (pair,) if isinstance(pairs, tuple) else list(pairs) + [pair]
    return True

def m_pair_event_lie(c):
    pairs = c.get('incarnation_pairs')
    if not pairs: return None
    p = pairs[0]
    if not isinstance(p, dict) or type(p.get('target_event')) is not int: return 'pair event index absent'
    p['target_event'] = p['target_event'] + 1; return True

def m_binding_claim(c):
    r = find(c, lambda i, x: x.get('binding') not in (None, 'new-binding', 'binding-conflict'))
    if r is None: return 'no flippable row binding field'
    r['binding'] = 'new-binding'; return True

def m_row_index(c):
    if len(rows(c)) < 2: return 'row ledger too short'
    r = rows(c)[len(rows(c)) // 2]
    if not isinstance(r, dict) or type(r.get('index')) is not int: return 'row index absent'
    r['index'] = r['index'] + 1; return True

def m_row_dropped(c):
    r = c.get('rows')
    if not isinstance(r, (list, tuple)) or len(r) < 2: return 'row ledger absent'
    c['rows'] = r[:-1]; return True

def m_qprofile_renumbered(c):
    qp = (c.get('adapter') or {}).get('q_profile')
    acts = qp.get('actions') if isinstance(qp, dict) else None
    if not isinstance(acts, (list, tuple)) or len(acts) < 2: return 'q_profile action inventory absent'
    qp['actions'] = tuple(reversed(tuple(acts))); return True

def m_journal_only(c):
    prefs = c.get('prefixes')
    if not isinstance(prefs, (list, tuple)) or len(prefs) < 3: return 'prefix ledger absent'
    item = prefs[len(prefs) // 2]
    if not isinstance(item, dict) or 'differing_journal_fields' not in item: return 'journal-difference field absent'
    item['differing_journal_fields'] = ['source_generation']; return True

def m_outer_divergence(c):
    r = find(c, lambda i, x: verb(x.get('source_action')) == 'cut-deliver' and isinstance(dec(x, 'adapter'), str) and dec(x, 'adapter') == dec(x, 'source'))
    if r is None: return None
    r['adapter_observation']['decision'] = 'cut-deliver:forged-outer-only-decision'; return True

def m_event_decoupled(c):
    events = (c.get('adapter') or {}).get('events')
    if not isinstance(events, (list, tuple)): return 'adapter event ledger absent'
    target = None
    for e in events:
        st = post_state(e)
        if isinstance(st, dict) and tok((st.get('core') or {}).get('source_generation')): target = st['core']
    if target is None: return 'retained event schema unrecognized'
    target['source_generation'] = GEN + (target['source_generation'][3] + 5,); return True

def m_hash_only(c):
    if not rows(c) or not isinstance(rows(c)[0], dict): return 'row ledger absent'
    if not isinstance(rows(c)[0].get('source_sha256'), str): return 'row digest field absent'
    rows(c)[0]['source_sha256'] = '0' * 64; return True

CONTROLS = (
    ('attest-refusal-false-invocation', 'semantic', 'refused source-attest row with q_invoked False', m_attest_invoked),
    ('refusal-hidden', 'semantic', 'refused row with equal source/adapter decisions', m_refusal_hidden),
    ('delivery-not-delegated', 'semantic', 'delegated cut:/cut-deliver delivery rows', m_delivery_dropped),
    ('restart-delegation-dropped', 'semantic', 'delegated source-restart row', m_restart_dropped),
    ('initial-core-generation-decoupled', 'semantic', 'none: adapter initial core always retained', m_core_generation0),
    ('initial-journal-generation-decoupled', 'semantic', 'none: adapter initial journal always retained', m_journal_generation0),
    ('forged-pair-launders-decoupling', 'semantic', 'none: injects even into an empty pair ledger', m_forged_pair_laundering),
    ('pair-event-index-lie', 'semantic', 'existing incarnation pair (unreachable while attestation is refused domain-wide)', m_pair_event_lie),
    ('fabricated-new-binding-claim', 'semantic', 'none: row binding field', m_binding_claim),
    ('row-index-chronology-lie', 'semantic', 'none: row ledger', m_row_index),
    ('row-dropped', 'semantic', 'none: row ledger', m_row_dropped),
    ('q-profile-renumbered', 'semantic', 'none: adapter q_profile', m_qprofile_renumbered),
    ('journal-only-disagreement-claim', 'semantic', 'none: prefix census field', m_journal_only),
    ('outer-decision-divergence', 'semantic', 'delegated cut-deliver row with equal decisions', m_outer_divergence),
    ('event-poststate-core-decoupled', 'semantic', 'recognizable retained adapter post-state event', m_event_decoupled),
    ('outer-hash-only', 'plumbing', 'none: hash rejection alone is not semantic discrimination', m_hash_only))

def run_controls(cases, inspect_cases, charge):
    results, limitations, paid, stop = [], [], 0, False
    if isinstance(cases, dict): cases = [cases]

    def pay(what, label, name):
        nonlocal paid, stop
        try: charge.take(1); paid += 1; return True
        except Exception as e:
            limitations.append({'control': label, 'case': name, 'limitation': what + ' precharge refused: ' + str(e)})
            stop = True
            return False

    for case in cases or ():
        name = case.get('case') if isinstance(case, dict) else None
        if not isinstance(case, dict): limitations.append({'case': name, 'limitation': 'non-dict case object skipped'}); continue
        if not pay('baseline replay', None, name): break
        try:
            baseline = inspect_cases([copy.deepcopy(case)], charge)
            base_status = baseline.get('status') if isinstance(baseline, dict) else 'inspector-non-dict'
        except Exception as e:
            base_status = 'inspector-exception'; limitations.append({'case': name, 'limitation': 'baseline inspector exception: ' + str(e)})
        for label, tier, witness, mutate in CONTROLS:
            if not pay('mutation', label, name): break
            mc = copy.deepcopy(case)
            try: applied = mutate(mc)
            except (AttributeError, KeyError, IndexError, TypeError, ValueError) as e: applied = 'mutation error: ' + str(e)
            if applied is not True:
                limitations.append({'control': label, 'case': name, 'witness': witness,
                                    'limitation': 'no genuinely reachable witness' if applied is None else str(applied)})
                continue
            if not pay('mutated replay', label, name): break
            status, audited = 'inspector-exception', None
            try:
                observed = inspect_cases([mc], charge)
                if isinstance(observed, dict): status, audited = observed.get('status'), observed.get('audited_prefixes')
            except Exception as e:
                limitations.append({'control': label, 'case': name, 'limitation': 'inspector exception: ' + str(e)})
            results.append({'control': label, 'case': name, 'tier': tier, 'witness': witness, 'baseline_status': base_status,
                            'expected': 'counterexample', 'observed': status, 'detected': status == 'counterexample',
                            'discriminating': status == 'counterexample' and base_status != 'counterexample',
                            'mutation_changed_bytes': dig(case) != dig(mc), 'audited_prefixes': audited})
        if stop: break
    det = [x for x in results if x['detected']]; sem = [x for x in results if x['tier'] == 'semantic']
    return {'controls': js(results), 'limitations': js(limitations), 'evaluated': len(results), 'detected': len(det),
            'semantic_evaluated': len(sem), 'semantic_detected': sum(1 for x in sem if x['detected']),
            'discriminating': sum(1 for x in results if x['discriminating']),
            'undetected': sorted({x['control'] for x in results if not x['detected']}),
            'missing_witnesses': sorted({x['control'] for x in limitations if x.get('limitation') == 'no genuinely reachable witness'}),
            'precharge_units': paid, 'all_detected': bool(results) and len(det) == len(results),
            'note': 'bounded adversarial evaluation only; plumbing controls are not semantic discrimination; no scientific PASS or acceptance is claimed'}
