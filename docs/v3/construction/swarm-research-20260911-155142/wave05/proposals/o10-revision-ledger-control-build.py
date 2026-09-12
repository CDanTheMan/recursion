"""Bounded retained-certificate controls for the revision-ledger obligation.

Per supplied typed case, without reducer/model/guard/boundary execution:
1) every source_revision change and nonchange equals an independent
   expectation; the ledger is monotonic across register/attempt/atomic/append
   successes, refusals, collection/delegated verbs, and source-restart;
2) the adapter journal equals the source EXTRA ledger exactly at every
   prefix (journal-only disagreement is a first-class violation);
3) journal source_generation advances exactly +1 on an invoked
   source-restart and never otherwise;
4) retained rows (source_action/index/q_invoked/both side decisions) agree
   with recovered post-states, so visible refusals stay bound to evidence.

Anchors (unchanged originals; representation only, never imported):
s_inclusive.py/s_split.py: decision is k+':ok' or k+':'+reason; +1 revision
only on ok register/attempt/atomic/append (identical re-registration is an
ok-noop); guard_a.py/guard_b.py/guard_audit.py/s_audit.py: same independent
ledger rules; a_domain.py/a_inclusive.py/a_split.py/a_audit.py: journal
mirrors every EXTRA field plus source_generation, bumped only inside an
invoked restart; check.py run_history/audit_case: trace shape
(initial + one event per action) and the rows[i] fields used below.

Post-states are recovered per event by unique state-shape match or by
applying a retained field patch; the recovery method is reported and
unrecoverable prefixes yield 'unproved' plus a limitation, never a silent
pass. run_controls deepcopy-mutates real cases only at genuinely reachable
transitions, leaving rows and outer hashes untouched so detection must reach
semantics; controls lacking a reachable witness report 'missing-witness'.
'supported' covers only the supplied, audited prefixes; no global theorem.
"""
JOURNAL = ('registration', 'attempts', 'append_log', 'append_receipts', 'append_reply',
           'source_revision', 'collection', 'collected', 'attestation', 'staged_source',
           'selected_source', 'source_generation')
INC = ('register:', 'attempt:', 'atomic:', 'append:')
GEN = ('cut-source', 'collectorA', 'effectA')
S_NEED = frozenset(JOURNAL) | {'done', 'decision', 'paused', 'staged'}
A_NEED = {'core', 'journal', 'done', 'decision', 'invocations'}


def _is_source(x):
    return isinstance(x, dict) and S_NEED <= set(x)


def _is_adapter(x):
    return (isinstance(x, dict) and A_NEED <= set(x)
            and isinstance(x.get('journal'), dict) and set(JOURNAL) <= set(x['journal']))


def _post(event, pred, prev):
    """Recover (post-state, mutation-carrier, method) from one retained event."""
    if pred(event):
        return event, event, 'event-state'
    if isinstance(event, dict):
        for key in ('after', 'state', 'post', 'next', 'result', 'to'):
            if pred(event.get(key)):
                return event[key], event[key], 'field:' + key
        for key in ('patch', 'delta', 'updates', 'changes', 'diff'):
            if isinstance(event.get(key), dict):
                merged = dict(prev or {}, **event[key])
                if pred(merged) and merged != prev:
                    return merged, event[key], 'patch:' + key
    out = []
    def walk(x, d):
        if d < 0 or len(out) > 2:
            return
        if pred(x):
            out.append(x)
            return
        vals = x.values() if isinstance(x, dict) else x if isinstance(x, (list, tuple)) else ()
        for v in vals:
            walk(v, d - 1)
    walk(event, 4)
    cand = [s for s in out if prev is None or s != prev]
    return (cand[0], cand[0], 'scan') if cand and len({id(s) for s in cand}) == 1 \
        else (None, None, 'missing')


def _chain(trace, pred):
    init = trace.get('initial') if isinstance(trace, dict) else None
    st, car, how = [init], [init], ['initial']
    for e in (trace.get('events') or ()) if isinstance(trace, dict) else ():
        s, c, h = _post(e, pred, st[-1])
        st.append(s); car.append(c); how.append(h)
    return st, car, how


def _expected(verb, before, decision):
    if decision != verb + ':ok':
        return 0
    if verb.startswith('register:'):
        return 0 if before.get('registration') else 1
    return 1 if verb.startswith(INC) else 0


def _gdelta(g0, g1):
    if g0 == g1:
        return 0
    ok = (isinstance(g0, tuple) and isinstance(g1, tuple) and len(g0) == len(g1) == 4
          and g0[:3] == GEN and g1[:3] == GEN and type(g0[3]) is int and type(g1[3]) is int)
    return g1[3] - g0[3] if ok else 'shape-violation'


def inspect_cases(cases, charge):
    out = dict(status='supported', observations=[], limitations=[], audited_prefixes=0)
    if not cases:
        out['status'] = 'not_applicable'
        out['limitations'].append('no retained cases supplied')
        return out
    bad, gaps, meth = [], [], {}
    stats = dict(positive=0, unchanged=0, restarts=0, journal_diffs=0)
    for ci, case in enumerate(cases):
        label = str(case.get('case', ci)) if isinstance(case, dict) else str(ci)
        try:
            ss, _sc, sm = _chain(case['source'], _is_source)
            aa, _ac, am = _chain(case['adapter'], _is_adapter)
            actions = case['source'].get('actions') or ()
            rows = case.get('rows') or ()
        except (AttributeError, KeyError, TypeError) as err:
            gaps.append('%s: unreadable case (%s)' % (label, err))
            continue
        for h in set(sm) | set(am):
            meth[h] = meth.get(h, 0) + 1
        if (len(ss) != len(aa) or len(ss) != len(actions) + 1
                or case['adapter'].get('actions') != actions or len(rows) != len(actions)):
            gaps.append(label + ': trace/action/row inventory mismatch')
        for i in range(min(len(ss), len(aa))):
            charge.take(1)
            s_now, a_now = ss[i], aa[i]
            if not (_is_source(s_now) and _is_adapter(a_now)):
                gaps.append('%s: prefix %s unrecoverable (%s/%s)' % (label, i, sm[i], am[i]))
                continue
            out['audited_prefixes'] += 1
            diff = [k for k in JOURNAL if s_now.get(k) != a_now['journal'].get(k)]
            if diff:
                stats['journal_diffs'] += 1
                bad.append(dict(case=label, prefix=i, control='journal-equality', fields=diff))
            if not i:
                if s_now['source_revision'] or a_now['journal']['source_revision']:
                    bad.append(dict(case=label, prefix=0, control='initial-revision-nonzero'))
                continue
            s_pre, a_pre = ss[i - 1], aa[i - 1]
            if not (_is_source(s_pre) and _is_adapter(a_pre)):
                gaps.append('%s: transition %s prestate missing' % (label, i))
                continue
            action = actions[i - 1] if i - 1 < len(actions) and isinstance(actions[i - 1], str) else ''
            verb = action.split('@')[0]
            row = rows[i - 1] if i - 1 < len(rows) and isinstance(rows[i - 1], dict) else {}
            for side, pre, now, dec in (('source', s_pre, s_now, s_now.get('decision')),
                                        ('journal', a_pre['journal'], a_now['journal'],
                                         a_now.get('decision'))):
                got = now.get('source_revision', 0) - pre.get('source_revision', 0)
                if got in (0, 1):
                    stats['positive' if got else 'unchanged'] += 1
                exp = _expected(verb, pre, dec)
                if got != exp:
                    bad.append(dict(case=label, prefix=i, control='revision-delta', side=side,
                                    action=action, expected=exp, observed=got))
            invoked = row.get('q_invoked')
            stats['restarts'] += verb == 'source-restart'
            if verb == 'source-restart' and invoked is None:
                gaps.append('%s: prefix %s restart invocation unverified' % (label, i))
            else:
                got = _gdelta(a_pre['journal'].get('source_generation'),
                              a_now['journal'].get('source_generation'))
                if got != int(verb == 'source-restart'):
                    bad.append(dict(case=label, prefix=i, control='journal-generation',
                                    action=action, expected=int(verb == 'source-restart'),
                                    observed=got, q_invoked=invoked))
            if row.get('source_action') not in (None, action) or row.get('index') not in (None, i - 1):
                bad.append(dict(case=label, prefix=i, control='row-identity', action=action))
            for key, now in (('source_observation', s_now), ('adapter_observation', a_now)):
                dec = (row.get(key) or {}).get('decision')
                if dec is not None and dec != now.get('decision'):
                    bad.append(dict(case=label, prefix=i, control='row-' + key, action=action,
                                    expected=dec, observed=now.get('decision')))
    out['limitations'] += gaps[:12]
    if not stats['positive']:
        out['limitations'].append('no +1 source_revision transition inspected')
    if not stats['restarts']:
        out['limitations'].append('no source-restart transition inspected')
    out['observations'].append(dict(cases=len(cases), audited_prefixes=out['audited_prefixes'],
                                    recovery_methods=meth, **stats))
    if bad:
        out['status'] = 'counterexample'
        out['observations'].append(dict(violations=bad[:12], total_violations=len(bad)))
    elif gaps or not stats['positive'] or not stats['restarts']:
        out['status'] = 'unproved'
    return out


def _clone(x):
    if isinstance(x, dict):
        return {k: _clone(v) for k, v in x.items()}
    if type(x) is list:
        return [_clone(v) for v in x]
    if isinstance(x, tuple):
        v = [_clone(e) for e in x]
        return type(x)(*v) if hasattr(x, '_fields') else tuple(v)
    return x


def _site(cases, want, charge):
    for ci, case in enumerate(cases):
        try:
            ss, sc, _ = _chain(case['source'], _is_source)
            _a, ac, _ = _chain(case['adapter'], _is_adapter)
            actions = case['source'].get('actions') or ()
        except (AttributeError, KeyError, TypeError):
            continue
        for i in range(len(ss)):
            charge.take(1)
            if not (_is_source(sc[i]) and _is_adapter(ac[i])):
                continue
            if not i:
                if want == 'any':
                    return ci, i
                continue
            verb = actions[i - 1].split('@')[0] if i - 1 < len(actions) else ''
            delta = (ss[i]['source_revision'] - ss[i - 1]['source_revision']
                     if _is_source(ss[i]) and _is_source(ss[i - 1]) else None)
            if {'positive': delta == 1, 'zero': delta == 0, 'restart': verb == 'source-restart',
                    'nonrestart': verb != 'source-restart'}.get(want):
                return ci, i
    return None


def run_controls(cases, inspect_cases, charge):
    out = dict(status='supported', observations=[], limitations=[], audited_prefixes=0)
    base = inspect_cases(cases, charge)
    out['audited_prefixes'] += base['audited_prefixes']
    out['observations'].append(dict(control='original-retained-cases',
                                    observed_status=base['status'],
                                    audited_prefixes=base['audited_prefixes'],
                                    detail=base['observations']))
    out['limitations'] += base['limitations']
    if not cases:
        out['status'] = 'not_applicable'
        return out
    specs = (('skipped-required-increment', 'positive', 'skip', True,
              'journal-mirrored drop of a required +1 (original-domain defect)'),
             ('phantom-increment-on-nonchange', 'zero', 'bump', True,
              'journal-mirrored +1 on a nonchange verb (original-domain defect)'),
             ('restart-resets-revision', 'restart', 'reset', True,
              'journal-mirrored reset to 0 at restart (original-domain defect)'),
             ('journal-only-disagreement', 'any', 'journal', True,
              'adapter shadow ledger drifted from source EXTRA fields'),
             ('generation-advance-without-restart', 'nonrestart', 'gen', True,
              'mirrored incarnation advance absent an invoked restart'),
             ('forged-visible-decision', 'positive', 'decision', False,
              'evidence-integrity defect: post-state decision contradicts retained row'))
    for name, want, how, reach, note in specs:
        entry = dict(control=name, reachable_domain_witness=reach, note=note)
        site = _site(cases, want, charge)
        st = car = mut = None
        if site:
            mut = _clone(cases[site[0]])
            _s, sc, _ = _chain(mut['source'], _is_source)
            _t, ac, _ = _chain(mut['adapter'], _is_adapter)
            st, car = sc[site[1]], ac[site[1]]
        if not (st and car and _is_source(st) and _is_adapter(car)):
            entry.update(detected=None, observed_status='missing-witness')
            out['limitations'].append(name + ': no reachable witness in supplied cases')
        else:
            i = site[1]
            jrn = car['journal']
            try:
                if how == 'skip':
                    pre = _chain(mut['source'], _is_source)[0][i - 1]
                    st['source_revision'] = jrn['source_revision'] = pre['source_revision']
                elif how == 'bump':
                    st['source_revision'] += 1; jrn['source_revision'] += 1
                elif how == 'reset':
                    st['source_revision'] = jrn['source_revision'] = 0
                elif how == 'journal':
                    jrn['attempts'] = tuple(jrn.get('attempts') or ()) + (('forgedA', 'attempt:999'),)
                elif how == 'gen':
                    for h in (st, jrn):
                        g = tuple(h['source_generation'])
                        h['source_generation'] = g[:-1] + (g[-1] + 1,)
                elif how == 'decision':
                    st['decision'] = mut['source']['actions'][i - 1].split('@')[0] + ':forged'
            except (KeyError, IndexError, TypeError) as err:
                entry.update(detected=None, observed_status='mutation-unapplied:%s' % err)
                out['limitations'].append(name + ': mutation could not be applied')
                out['observations'].append(entry)
                continue
            res = inspect_cases([mut], charge)
            out['audited_prefixes'] += res['audited_prefixes']
            entry.update(detected=res['status'] == 'counterexample',
                         observed_status=res['status'],
                         target=dict(case=str(mut.get('case', site[0])), prefix=i))
        out['observations'].append(entry)
    controls = out['observations'][1:]
    if base['status'] == 'counterexample':
        out['status'] = 'counterexample'
    elif base['status'] != 'supported' or any(e.get('detected') is not True for e in controls):
        out['status'] = 'unproved'
        if any(e.get('detected') is False for e in controls):
            out['limitations'].append('a planted mutation escaped detection')
    return out
