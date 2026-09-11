"""Bounded retained-certificate check for obligation o22-reader-lineage.

Claim under audit. In the original scale profile 'scale-eight-action-race'
(experiments/v3/cut-source-overnight/s_domain.py add_with_suffix; fixed
suffix start 19; q_domain.py reader() supplies request,pin,copy,wait,
release,install at slot 0) the actual reader fields reader_requests,
reader_pins, reader_copies, reader_waited, reader_nonce, installed_cut and
the frozen Q reader guards preserve typed lineage on every audited retained
prefix: request/pin/copy/install envelopes trace to envelopes retained in
publication_store or retired_cuts, pins bind nonce-typed owners, refused
verbs change no reader field, and delegated adapter Q invocations are
recorded. Unreachable verb variants are marked, never claimed.

Representation anchors (unchanged original sources consulted for semantics
only; this module neither imports nor executes them): frozen reader guard
order and refusal reasons - experiments/v3/cut-publication/q_audit.py
'reader-' branch, q_inclusive.py, q_split.py; retained event/patch shape and
restore binding - cut-source-overnight/batch-06/adapter_traces.py
trace_event/restore; incarnation pair relation shape - batch-05/semantic.py
token/generation_pair/nested_pair; case shape - eight-hour-research-
20260910-01a08a22/check.py run_history and artifact.py decode.

Method. Pure certificate inspection. Per-prefix states are rebuilt only by
applying each retained event patch to the prior state (nested update only
for adapter 'core'/'journal', exactly the retained patch convention) and
re-linking adjacent before_sha256/after_sha256 strings. No reducer, guard,
boundary helper or model is executed; this module has no imports at all.
charge.take(1) is consumed BEFORE each inspected prefix; repetitions count.

Status. 'supported' covers only the supplied cases' audited prefixes: a
bounded certificate fact, not an all-orders theorem and not scientific
acceptance. 'counterexample' reports a concrete retained expected/observed
divergence; 'unproved' means incomplete coverage or malformed retained
structure; 'not_applicable' means no reader verb is reachable.
"""

READER_FIELDS = ('reader_requests', 'reader_pins', 'reader_copies',
                 'reader_waited', 'reader_nonce', 'installed_cut')
NEED = READER_FIELDS + ('selected', 'publication_store', 'retired_cuts')
PAIR_FIELDS = READER_FIELDS + ('selected', 'publication_store')
VERBS = ('reader-request', 'reader-pin', 'reader-copy', 'reader-wait',
         'reader-release', 'reader-release-foreign', 'reader-restart',
         'reader-install', 'reader-install-corrupt')
SUFFIX_ORDER = ('reader-request', 'reader-pin', 'reader-copy',
                'reader-wait', 'reader-release', 'reader-install')


def _envelope(x):
    f = getattr(x, '_fields', None)
    return type(x).__name__ == 'Envelope' and f is not None and len(f) == 12


def _norm(x):
    if isinstance(x, dict):
        return {k: _norm(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return tuple(_norm(v) for v in x)
    return x


def _view(x):
    if _envelope(x):
        return {'Envelope': x.generation, 'request': x.request}
    if isinstance(x, dict):
        return {str(k): _view(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_view(v) for v in x]
    return x if x is None or isinstance(x, (str, int, bool, float)) else type(x).__name__


def _restore(trace):
    """Reconstruct prefix states by applying retained patches only."""
    nested = trace.get('side') == 'adapter'
    state = dict(trace['initial'])
    for key in ('core', 'journal'):
        if isinstance(state.get(key), dict):
            state[key] = dict(state[key])
    states, broken = [state], []
    events = trace['events']
    for index, event in enumerate(events):
        if index and event.get('before_sha256') != events[index - 1].get('after_sha256'):
            broken.append(index)
        nxt = dict(state)
        for key in ('core', 'journal'):
            if isinstance(nxt.get(key), dict):
                nxt[key] = dict(nxt[key])
        for key, value in event.get('patch', {}).items():
            if nested and key in ('core', 'journal') and isinstance(value, dict):
                nxt[key].update(value)
            else:
                nxt[key] = value
        states.append(nxt)
        state = nxt
    return states, broken


def _store_envs(s):
    return [r[0] for r in s['publication_store']
            if isinstance(r, (list, tuple)) and len(r) == 2 and _envelope(r[0])]


def _expected(verb, slot, s):
    """Frozen guard outcome recomputed from the actual before-state fields."""
    owner = ('reader' + str(slot), s['reader_nonce'][slot])
    pin = s['reader_pins'][slot]
    owned = (isinstance(pin, (list, tuple)) and len(pin) == 2
             and _norm(pin[0]) == owner)
    envs = _store_envs(s)
    if verb == 'reader-request':
        return 'ok' if s['selected'] else 'no-selection'
    if verb == 'reader-pin':
        pending = s['reader_requests'][slot]
        if not pending or pin:
            return 'no-fresh-request'
        if _norm(pending[0]) != owner:
            return 'stale-reader'
        if pending[1] != s['selected']:
            return 'stale-selection'
        return 'ok' if any(pending[1] == e for e in envs) else 'retired'
    if verb == 'reader-copy':
        if not owned:
            return 'no-owned-pin'
        return 'ok' if any(pin[1] == e for e in envs) else 'retired'
    if verb == 'reader-wait':
        return 'ok' if owned else 'no-owned-pin'
    if verb == 'reader-release-foreign':
        return 'no-owned-pin'
    if verb == 'reader-release':
        if not owned:
            return 'no-owned-pin'
        return 'ok' if s['reader_waited'][slot] else 'reader-live'
    if verb == 'reader-restart':
        return 'ok'
    row = s['reader_copies'][slot]
    if not row:
        return 'no-copy'
    if verb == 'reader-install-corrupt':
        return 'copy-mismatch'
    env = row[0] if isinstance(row, (list, tuple)) and len(row) == 2 else None
    gens = {e.generation for e in envs} | set(s['retired_cuts'])
    return 'ok' if _envelope(env) and env.generation in gens else 'copy-mismatch'


def _post_ok(verb, slot, before, after):
    """Poststate field lineage required of a successful reader verb."""
    if verb == 'reader-request':
        want = (('reader' + str(slot), before['reader_nonce'][slot]), before['selected'])
        return _norm(after['reader_requests'][slot]) == _norm(want)
    if verb == 'reader-pin':
        return (_norm(after['reader_pins'][slot]) == _norm(before['reader_requests'][slot])
                and after['reader_waited'][slot] is False)
    if verb == 'reader-copy':
        pin = before['reader_pins'][slot]
        row = next((r for r in before['publication_store']
                    if isinstance(r, (list, tuple)) and len(r) == 2 and r[0] == pin[1]), None)
        return row is not None and _norm(after['reader_copies'][slot]) == _norm(row)
    if verb == 'reader-wait':
        return after['reader_waited'][slot] is True
    if verb == 'reader-release':
        return not after['reader_pins'][slot]
    if verb == 'reader-restart':
        return after['reader_nonce'][slot] == before['reader_nonce'][slot] + 1
    if verb == 'reader-install':
        inst = after['installed_cut']
        return (_norm(inst) == _norm(before['reader_copies'][slot])
                and _envelope(inst[0])
                and ('cut_received' not in after or after['cut_received'] == inst[0].cut))
    return True


def _lineage(s, name, prefix, side, copied, findings):
    def bad(field, expected, observed):
        findings.append({'case': name, 'prefix': prefix, 'side': side, 'field': field,
                         'expected': expected, 'observed': _view(observed)})
    missing = [f for f in NEED if f not in s]
    if missing:
        bad('reader_fields', 'complete reader field inventory', 'missing:' + ','.join(missing))
        return
    reqs, pins, copies = s['reader_requests'], s['reader_pins'], s['reader_copies']
    nonces, waited, inst = s['reader_nonce'], s['reader_waited'], s['installed_cut']
    if not all(isinstance(x, (list, tuple)) for x in (reqs, pins, copies, nonces, waited)):
        bad('reader_slots', 'tuple slot vectors', 'non-sequence slot field')
        return
    if len({len(x) for x in (reqs, pins, copies, nonces, waited)}) != 1:
        bad('reader_slots', 'equal slot arity', [len(x) for x in (reqs, pins, copies, nonces, waited)])
        return
    envs, retired = _store_envs(s), set(s['retired_cuts'])
    for i in range(len(reqs)):
        owner = 'reader' + str(i)
        fresh = type(nonces[i]) is int and nonces[i] >= 1
        if not fresh:
            bad('reader_nonce', 'int>=1', nonces[i])
        for field, row in (('reader_requests', reqs[i]), ('reader_pins', pins[i])):
            if not row:
                continue
            ok = (isinstance(row, (list, tuple)) and len(row) == 2
                  and isinstance(row[0], (list, tuple)) and len(row[0]) == 2
                  and row[0][0] == owner and type(row[0][1]) is int
                  and fresh and 1 <= row[0][1] <= nonces[i] and _envelope(row[1]))
            if not ok:
                bad(field, '((readerI,nonce<=current),Envelope)', row)
            elif field == 'reader_pins':
                if not any(row[1] == e for e in envs):
                    bad(field, 'pinned envelope retained in publication_store', row[1].generation)
            elif not (row[1] == s['selected'] or any(row[1] == e for e in envs)
                      or row[1].generation in retired):
                bad(field, 'request envelope selected|stored|retired', row[1].generation)
        row = copies[i]
        if row:
            if not (isinstance(row, (list, tuple)) and len(row) == 2
                    and _envelope(row[0]) and type(row[1]) is str):
                bad('reader_copies', '(Envelope,raw str)', row)
            else:
                copied.add(row[0].generation)
                if not (any(row[0] == e for e in envs) or row[0].generation in retired):
                    bad('reader_copies', 'copied envelope stored|retired', row[0].generation)
        if type(waited[i]) is not bool:
            bad('reader_waited', 'bool', waited[i])
    if inst:
        if not (isinstance(inst, (list, tuple)) and len(inst) == 2
                and _envelope(inst[0]) and type(inst[1]) is str):
            bad('installed_cut', '(Envelope,raw str)', inst)
        else:
            if inst[0].generation not in copied:
                bad('installed_cut', 'installed generation seen in earlier reader copy',
                    inst[0].generation)
            if not (any(inst[0] == e for e in envs) or inst[0].generation in retired):
                bad('installed_cut', 'installed envelope stored|retired', inst[0].generation)
            if 'cut_received' in s and s['cut_received'] != inst[0].cut:
                bad('installed_cut', 'cut_received == installed env.cut', s['cut_received'])


def _env_pair(a, b, pairs):
    if not (_envelope(a) and _envelope(b)):
        return False
    if any(getattr(a, f) != getattr(b, f) for f in a._fields
           if f not in ('source_generation', 'signature')):
        return False
    if a.source_generation == b.source_generation:
        return True
    return any(_norm(p.get('source')) == _norm(a.source_generation)
               and _norm(p.get('target')) == _norm(b.source_generation) for p in pairs)


def _pair(a, b, pairs):
    if _envelope(a) or _envelope(b):
        return _env_pair(a, b, pairs)
    if isinstance(a, dict) or isinstance(b, dict):
        return (isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b)
                and all(_pair(a[k], b[k], pairs) for k in a))
    if isinstance(a, (list, tuple)) or isinstance(b, (list, tuple)):
        return (isinstance(a, (list, tuple)) and isinstance(b, (list, tuple))
                and len(a) == len(b) and all(_pair(x, y, pairs) for x, y in zip(a, b)))
    return a == b


def inspect_cases(cases, charge):
    """Audit retained typed case objects; charge.take(1) precedes each prefix."""
    result = {'status': 'unproved', 'observations': [], 'limitations': [],
              'audited_prefixes': 0}
    findings, gaps, reachable = [], [], set()
    positions, reasons = {}, {}
    case_list = list(cases) if cases else []
    stop = False
    for ordinal, case in enumerate(case_list):
        name = case.get('case', 'case-' + str(ordinal)) if isinstance(case, dict) else 'case-' + str(ordinal)
        try:
            src, adp = case['source'], case['adapter']
            actions = list(src['actions'])
            pairs, rows = case.get('incarnation_pairs') or (), case.get('rows') or ()
            intact = (list(adp['actions']) == actions
                      and [e.get('action') for e in src['events']] == actions
                      and [e.get('action') for e in adp['events']] == actions)
        except (KeyError, TypeError, AttributeError) as exc:
            gaps.append('%s: malformed retained case (%s)' % (name, type(exc).__name__))
            continue
        if not intact:
            findings.append({'case': name, 'observed': 'mismatch',
                             'expected': 'literal action/event inventory equality on both sides'})
            continue
        if rows and len(rows) != len(actions):
            gaps.append('%s: retained row inventory differs from event inventory' % name)
        s_states, s_broken = _restore(src)
        a_states, a_broken = _restore(adp)
        for side, broken in (('source', s_broken), ('adapter', a_broken)):
            for i in broken:
                findings.append({'case': name, 'side': side, 'event_index': i,
                                 'expected': 'adjacent before_sha256 == prior after_sha256',
                                 'observed': 'broken retained chain link'})
        copied = {'source': set(), 'adapter-core': set()}
        for prefix in range(len(actions) + 1):
            try:
                charge.take(1)
            except Exception as exc:
                gaps.append('%s: charge refused before prefix %d (%s)'
                            % (name, prefix, type(exc).__name__))
                stop = True
                break
            result['audited_prefixes'] += 1
            ss, aa = s_states[prefix], a_states[prefix]
            ac = aa['core'] if isinstance(aa.get('core'), dict) else aa
            for side, st in (('source', ss), ('adapter-core', ac)):
                _lineage(st, name, prefix, side, copied[side], findings)
            for f in PAIR_FIELDS:
                if f in ss and f in ac and not _pair(ss[f], ac[f], pairs):
                    findings.append({'case': name, 'prefix': prefix, 'field': f,
                                     'expected': 'cross-side pair-equal under incarnation_pairs',
                                     'observed': {'source': _view(ss[f]), 'adapter': _view(ac[f])}})
            if not prefix:
                continue
            verb, _, tail = actions[prefix - 1].split('@')[0].partition(':')
            if verb not in VERBS:
                continue
            reachable.add(verb)
            positions.setdefault(name, {}).setdefault(verb, []).append(prefix - 1)
            slot = int(tail) if tail.isdigit() else -1
            bs, ba = s_states[prefix - 1], a_states[prefix - 1]
            bc = ba['core'] if isinstance(ba.get('core'), dict) else ba
            if not 0 <= slot < len(bs.get('reader_nonce', ())) if isinstance(bs.get('reader_nonce'), (list, tuple)) else True:
                gaps.append('%s: unreadable reader slot in action %s' % (name, actions[prefix - 1]))
                continue
            expected = actions[prefix - 1].split('@')[0] + ':' + _expected(verb, slot, bs)
            observed = (ss.get('decision'), aa.get('decision'))
            reasons.setdefault(verb, set()).add(str(observed[0]).rsplit(':', 1)[-1])
            for side, obs in (('source', observed[0]), ('adapter', observed[1])):
                if obs != expected:
                    findings.append({'case': name, 'prefix': prefix, 'side': side,
                                     'action': actions[prefix - 1],
                                     'expected': expected, 'observed': obs})
            if expected.endswith(':ok'):
                for side, b, a in (('source', bs, ss), ('adapter-core', bc, ac)):
                    if not _post_ok(verb, slot, b, a):
                        findings.append({'case': name, 'prefix': prefix, 'side': side,
                                         'action': actions[prefix - 1],
                                         'expected': 'poststate lineage for successful ' + verb,
                                         'observed': 'poststate mismatch'})
            else:
                for side, b, a in (('source', bs, ss), ('adapter-core', bc, ac)):
                    if any(f in a and f in b and _norm(a[f]) != _norm(b[f]) for f in READER_FIELDS):
                        findings.append({'case': name, 'prefix': prefix, 'side': side,
                                         'action': actions[prefix - 1],
                                         'expected': 'refused reader verb leaves reader fields unchanged',
                                         'observed': 'reader field mutation on refusal'})
            if rows:
                row = rows[prefix - 1]
                if row.get('q_invoked') is not True:
                    findings.append({'case': name, 'prefix': prefix, 'action': actions[prefix - 1],
                                     'expected': 'delegated adapter Q invocation recorded',
                                     'observed': row.get('q_invoked')})
                if row.get('responses_related') is False:
                    findings.append({'case': name, 'prefix': prefix, 'action': actions[prefix - 1],
                                     'expected': 'retained visible response relation',
                                     'observed': 'responses_related=False'})
        if stop:
            break
    for name, pos in positions.items():
        seen = [i for v in SUFFIX_ORDER for i in pos.get(v, ())]
        if len(seen) == len(SUFFIX_ORDER) and seen != sorted(seen):
            findings.append({'case': name, 'observed': pos,
                             'expected': 'canonical reader suffix order '
                                         + '<'.join(SUFFIX_ORDER)})
    unreachable = [v for v in VERBS if v not in reachable]
    result['observations'] = [
        {'kind': 'audit-accounting', 'cases_seen': len(case_list),
         'charge_units_consumed': result['audited_prefixes']},
        {'kind': 'reachability', 'reachable_reader_verbs': sorted(reachable),
         'unreachable_variants': unreachable, 'reader_event_positions': positions},
        {'kind': 'visible-refusals',
         'observed_reasons': {v: sorted(r) for v, r in sorted(reasons.items())},
         'success_only_verbs': sorted(v for v in reachable if reasons.get(v) == {'ok'})}]
    result['observations'] += [dict(kind='counterexample-witness', **w) for w in findings]
    result['limitations'] = [
        'bounded retained cases and audited prefixes only; no all-orders theorem, no scientific acceptance',
        'states rebuilt from retained patches with adjacent sha256 re-linkage; state digests are not recomputed (no original-source imports)',
        'copy/install raw payload validity bounded to generation membership and exact store-row equality; fixture byte re-derivation is out of scope'] + gaps
    if findings:
        result['status'] = 'counterexample'
    elif gaps or stop:
        result['status'] = 'unproved'
    elif not reachable:
        result['status'] = 'not_applicable'
    else:
        result['status'] = 'supported'
    return result
