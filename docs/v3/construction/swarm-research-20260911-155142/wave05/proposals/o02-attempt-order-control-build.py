"""Bounded retained-evidence check: obligation o02 attempt-order precedence.

Claim: on the frozen scale-eight-action-race profile (boundary-01 spec.json;
fixed prefix 0-10, antichain core collect-open@11, collect:0/1/2@12-14,
attempt:2/3/4@15-17, source-restart@18, fixed suffix 19-33) retained histories
preserve attempt guard precedence (registration, E-PAUSED, duplicate-attempt,
attempt-gap) under all six attempt permutations and every restart placement;
accepted attempts append one pair and bump source_revision, restart advances
the incarnation without resetting the attempt ledger, and refusals stay
visible in both observations with q_invoked False on source-handled verbs.
Method: rebuild an abstract ledger only from retained case['source']['actions']
and per-row observations, recompute each expected local decision, and compare
with retained decisions, invocation masks and journal divergence. No reducer,
audit or boundary helper executes or is imported. Anchors:
batch-06/guard_audit.py expected(), batch-05/semantic.py typed()/exact(),
s_domain.EXTRA journal names. Accounting: charge.take(1) before every
inspected prefix incl. repetitions; audited_prefixes exact. Unmodeled:
fixture bytes (registration equality, atomic payload, append attempt_id/scope)
and delegated Q outcomes; pause/cut state reconstructed from retained
decisions. duplicate-attempt and E-PAUSED attempt refusals have no reachable
witness in this inventory (one occurrence per number; no pause action); they
stay unproved and run_controls marks those mutations unreachable.
"""
import copy

LOCAL = ('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:')
LOCAL_EXACT = ('append-lose-reply', 'collect-open')
JOURNAL = ('registration', 'attempts', 'append_log', 'append_receipts',
           'append_reply', 'source_revision', 'collection', 'collected',
           'attestation', 'staged_source', 'selected_source')
ATT = (2, 3, 4)


def _verb(action):
    return action.split('@')[0]


def _ledger():
    return {'reg': 0, 'paused': 0, 'attempts': [], 'log': 0, 'gen': 0, 'rev': 0,
            'capture': None, 'collected': set(), 'cut': 0, 'receipts': {}}


def _expected(led, v):
    """(allowed reasons tuple, success effect); allowed None = unmodeled."""
    if v.startswith('register:'):
        return (('ok', 'registration-conflict'), None) if led['reg'] else (
            ('ok', 'incomplete-registration', 'foreign-registration'), ('reg',))
    if v.startswith('attempt:'):
        n = int(v[8:])
        pair = ('attemptA' if n == 1 else 'retained-attemptA' + str(n), v)
        for bad, r in ((not led['reg'], 'no-registration'),
                       (led['paused'], 'E-PAUSED'),
                       (pair in led['attempts'], 'duplicate-attempt'),
                       (n != len(led['attempts']) + 1, 'attempt-gap')):
            if bad: return (r,), None
        return ('ok',), ('attempt', pair)
    if v.startswith('atomic:'): return None, ('atomic',)
    if v.startswith('append:'):
        _x, _n, idx, var = v.split(':'); idx = int(idx)
        req = 'append-' + str(idx) + ('-fresh' if var == 'fresh' else '')
        body = ('collectorB' if var == 'foreign' else 'collectorA',
                1 if var == 'new-boot' else 0, idx,
                'base' if var in ('normal', 'new-boot', 'fresh') else var)
        prior = led['receipts'].get(req)
        for bad, r in ((body[0] != 'collectorA', 'wrong-append-owner'),
                       (prior is not None and prior != body, 'append-id-conflict'),
                       (prior is not None, 'duplicate'),
                       (body[1] != led['gen'], 'stale-append-incarnation'),
                       (led['paused'], 'E-PAUSED'), (not led['reg'], 'no-registration'),
                       (idx != led['log'], 'append-gap-or-fork'),
                       (var == 'wrong-attempt' or not led['attempts'], 'unregistered-attempt'),
                       (var == 'wrong-body', 'foreign-record-scope')):
            if bad: return (r,), None
        return ('ok', 'unregistered-attempt', 'foreign-record-scope'), ('append', (req, body))
    if v == 'append-lose-reply': return ('ok',), None
    if v == 'collect-open':
        return (('ok',), ('open',)) if led['reg'] else (('no-registration',), None)
    if v.startswith('collect:'):
        i = int(v[8:]); cap = led['capture']
        if cap is None or not 0 <= i < min(cap[2], led['log']):
            return ('outside-captured-cut',), None
        if i in led['collected']: return ('duplicate-collection',), None
        return ('ok',), ('collect', i)
    if v == 'source-attest':
        cap = led['capture']
        if cap is None: return ('no-captured-source',), None
        if cap[:2] != (led['gen'], led['rev']): main = 'stale-collection'
        elif led['collected'] != set(range(cap[2])): main = 'incomplete-inventory'
        else: return ('ok', 'incomplete-registry'), None
        return ((main,) if led['cut'] else (main, 'no-captured-source')), None
    if v == 'source-restart': return None, ('gen',)
    if v.startswith('source:'): return ('registered-protocol-required',), None
    return None, None


def _advance(led, v, e):
    tag = e[0] if e else None
    if tag == 'reg': led['reg'] = 1; led['rev'] += 1
    elif tag in ('attempt', 'atomic'):
        n = len(led['attempts']) + 1
        led['attempts'].append(e[1] if tag == 'attempt' else (
            'attemptA' if n == 1 else 'retained-attemptA' + str(n), 'attempt:' + str(n)))
        led['rev'] += 1; led['log'] += tag == 'atomic'
    elif tag == 'append':
        led['receipts'][e[1][0]] = e[1][1]; led['log'] += 1; led['rev'] += 1
    elif tag == 'open':
        led['capture'] = (led['gen'], led['rev'], led['log']); led['collected'] = set()
    elif tag == 'collect': led['collected'].add(e[1])
    elif tag == 'gen': led['gen'] += 1
    elif 'deliver' in v: led['cut'] = 1
    elif v == 'pause': led['paused'] = 1
    elif v in ('resume', 'unpause'): led['paused'] = 0


def inspect_cases(cases, charge):
    res = {'status': 'unproved', 'observations': [], 'limitations': [], 'audited_prefixes': 0}
    bad, perms, slots = [], set(), set()
    wit = {'attempt-gap': 0, 'duplicate-attempt': 0, 'E-PAUSED': 0, 'rows': 0}
    for case in cases:
        name = case.get('case') if isinstance(case, dict) else None
        try:
            verbs = [_verb(a) for a in case['source']['actions']]; rows = case['rows']
            prefixes = case.get('prefixes') or (); init = case['source'].get('initial') or {}
            aj = ((case.get('adapter') or {}).get('initial') or {}).get('journal')
        except (AttributeError, KeyError, TypeError):
            charge.take(1); res['audited_prefixes'] += 1
            bad.append({'case': name, 'prefix': None, 'defect': 'unreadable case frame'}); continue
        order = [int(v[8:]) for v in verbs if v.startswith('attempt:') and int(v[8:]) in ATT]
        if len(order) == 3:
            perms.add(tuple(order))
            if 'source-restart' in verbs:
                slots.add(sum(1 for v in verbs[:verbs.index('source-restart')]
                              if v.startswith('attempt:') and int(v[8:]) in ATT))
        led = _ledger()
        for i in range(len(verbs) + 1):
            charge.take(1); res['audited_prefixes'] += 1
            if i == 0:
                if (init.get('attempts') not in (None, (), [])
                        or init.get('registration') not in (None, '')
                        or isinstance(aj, dict) and aj.get('attempts') not in (None, (), [])):
                    bad.append({'case': name, 'prefix': 0, 'defect': 'non-empty initial attempt ledger'})
                continue
            try:
                row = rows[i - 1]; v = verbs[i - 1]
                dec = row['source_observation']['decision']
                other = row['adapter_observation']['decision']; invoked = row['q_invoked']
            except (KeyError, IndexError, TypeError):
                bad.append({'case': name, 'prefix': i, 'defect': 'missing retained row'}); continue
            reason = dec.rsplit(':', 1)[-1]; defect = None
            if dec != other: defect = 'side decisions differ'
            if (v.startswith(LOCAL) or v in LOCAL_EXACT) and invoked is not False:
                defect = defect or 'source-handled action claims Q invocation'
            if v == 'source-restart' and invoked is not True:
                defect = defect or 'restart dropped from invocation mask'
            if v == 'source-attest' and invoked != (reason == 'ok'):
                defect = defect or 'attest mask inconsistent with refusal'
            if invoked and reason == 'source-boundary-stale' and (v.startswith('pub-') or v == 'reconcile'):
                defect = defect or 'guard refusal claims delegated call'
            allowed, effect = _expected(led, v)
            if allowed is not None and reason not in allowed:
                defect = defect or 'guard precedence violation'
            item = prefixes[i] if i < len(prefixes) else None
            diff = [f for f in JOURNAL if isinstance(item, dict)
                    and f in (item.get('differing_journal_fields') or ())]
            if diff: defect = defect or 'journal fields diverge: ' + ','.join(diff)
            if defect:
                bad.append({'case': name, 'prefix': i, 'action': v, 'observed': dec,
                            'expected': [v + ':' + r for r in allowed or ()], 'defect': defect})
            if v.startswith('attempt:') and int(v[8:]) in ATT:
                wit['rows'] += 1
                if reason in wit: wit[reason] += 1
            if reason == 'ok': _advance(led, v, effect)
    res['observations'].append({'attempt_rows': wit['rows'],
        'permutations_seen': sorted(map(list, perms)), 'restart_slots_seen': sorted(slots),
        'gap_witnesses': wit['attempt-gap'], 'duplicate_witnesses': wit['duplicate-attempt'],
        'pause_witnesses': wit['E-PAUSED'], 'mismatches': bad})
    if bad: res['status'] = 'counterexample'
    elif not wit['rows']: res['status'] = 'not_applicable'
    elif (len(perms) == 6 and slots >= {0, 1, 2, 3}
          and wit['duplicate-attempt'] and wit['E-PAUSED']):
        res['status'] = 'supported'
    res['limitations'] = [
        'audit accounting: charge.take(1) before each inspected prefix incl. repetitions; audited_prefixes=' + str(res['audited_prefixes']),
        'unmodeled fixture bytes: registration equality, atomic payload, append attempt_id/scope; allowed reason sets retained',
        'pause/resume and cut-delivery reconstructed only from retained decisions; delegated Q outcomes not predicted',
        'duplicate-attempt/E-PAUSED attempt refusals lack a reachable witness in this inventory unless supplied cases show one; unproved, never claimed',
        'supported covers only supplied retained histories; no global theorem, reachability or acceptance claim']
    return res


def run_controls(cases, inspect_cases, charge):
    """Adversarial retained-evidence controls via deepcopy mutations of real cases."""
    found = {}
    for case in cases:
        try:
            verbs = [_verb(a) for a in case['source']['actions']]; rows = case['rows']
        except (AttributeError, KeyError, TypeError):
            continue
        ri = verbs.index('source-restart') if 'source-restart' in verbs else None
        if ri is not None: found.setdefault('restart', (case, ri, 'source-restart'))
        for i, v in enumerate(verbs):
            if not (v.startswith('attempt:') and int(v[8:]) in ATT): continue
            dec = rows[i]['source_observation']['decision']
            if dec.endswith(':attempt-gap'): found.setdefault('gap', (case, i, v))
            if dec.endswith(':ok'):
                found.setdefault('ok', (case, i, v))
                if ri is not None and i > ri: found.setdefault('post', (case, i, v))
    controls = []

    def emit(label, key, fn, note):
        if key not in found:
            controls.append({'control': label, 'observed_status': 'skipped',
                             'detected': False, 'note': 'no witness supplied: ' + note}); return
        case, i, v = found[key]; mutant = copy.deepcopy(case)
        try: fn(mutant, i, v)
        except (KeyError, IndexError, TypeError) as err:
            controls.append({'control': label, 'case': case.get('case'),
                             'observed_status': 'mutation-inapplicable',
                             'detected': False, 'note': str(err)}); return
        observed = inspect_cases([mutant], charge)
        controls.append({'control': label, 'case': case.get('case'),
                         'expected_effect': 'counterexample',
                         'observed_status': observed.get('status'),
                         'detected': observed.get('status') == 'counterexample', 'note': note})

    def dec(m, i, d):
        m['rows'][i]['source_observation'].update(decision=d)
        m['rows'][i]['adapter_observation'].update(decision=d)

    if cases:
        observed = inspect_cases([copy.deepcopy(cases[0])], charge)
        controls.append({'control': 'unmodified-retained-case', 'case': cases[0].get('case'),
                         'expected_effect': 'no-counterexample', 'observed_status': observed.get('status'),
                         'detected': observed.get('status') != 'counterexample',
                         'note': 'baseline sanity on real supplied case'})
    emit('attempt-gap-refusal-forged-ok', 'gap', lambda m, i, v: dec(m, i, v + ':ok'),
         'reachable-witness mutation: hides a genuine gap refusal')
    emit('attempt-ok-forged-gap', 'ok', lambda m, i, v: dec(m, i, v + ':attempt-gap'),
         'reachable-witness mutation: injects a false gap refusal')
    emit('post-restart-attempt-forged-gap', 'post', lambda m, i, v: dec(m, i, v + ':attempt-gap'),
         'simulates restart resetting the attempt ledger; unreachable original evidence')
    emit('attempt-forged-duplicate', 'ok', lambda m, i, v: dec(m, i, v + ':duplicate-attempt'),
         'duplicate precedence unreachable here: one occurrence per attempt number')
    emit('attempt-forged-paused', 'ok', lambda m, i, v: dec(m, i, v + ':E-PAUSED'),
         'pause precedence unreachable here: no pause action in the inventory')
    emit('refusal-claims-q-invocation', 'gap', lambda m, i, v: m['rows'][i].update(q_invoked=True),
         'source-handled refusals never invoke Q')
    emit('restart-dropped-from-invocation-mask', 'restart', lambda m, i, v: m['rows'][i].update(q_invoked=False),
         'restart is always a delegated call')
    emit('adapter-refusal-hidden', 'gap',
         lambda m, i, v: m['rows'][i]['adapter_observation'].update(decision=v + ':ok'),
         'visible refusal must survive on both sides')
    emit('journal-attempt-divergence-injected', 'gap',
         lambda m, i, v: m['prefixes'][i + 1].update(differing_journal_fields=list(
             m['prefixes'][i + 1].get('differing_journal_fields') or ()) + ['attempts']),
         'semantic journal-field control preserving outer structure')
    return {'controls': controls, 'cases_seen': len(cases)}
