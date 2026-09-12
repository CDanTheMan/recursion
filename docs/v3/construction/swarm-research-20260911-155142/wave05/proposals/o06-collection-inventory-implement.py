"""Bounded retained-certificate check: collect bounds, duplicates, sorting, inventory.

Obligation o06-collection-inventory. For every restored case object produced by
the unchanged original c.run_history / c.artifact pipeline, this module re-audits
the collection clauses of the source guard using only retained case fields: the
literal schedule and profile, the typed initial state, per-event comparison rows
(visible decisions, Q-invocation masks, justifications), per-prefix relation
items (differing journal fields) and any event payloads that expose ledger
fields. It executes no reducer, guard or audit function and imports no boundary
helper; expected values come from a small pure ledger projection anchored to the
unchanged audit text plus fixture bytes read through s_domain (representation
only). Nothing here is a global theorem or an accepted scientific PASS: results
are bounded to the supplied cases.

Source anchors (unchanged inputs):
  collect-open/collect:/source-attest guard clauses:
    experiments/v3/cut-source-overnight/s_inclusive.py:55-68
    experiments/v3/cut-source-overnight/batch-06/guard_a.py:56-76
    experiments/v3/cut-source-overnight/batch-06/guard_b.py:61-76
  independent audit expectations and refusal ordering:
    experiments/v3/cut-source-overnight/s_audit.py
    experiments/v3/cut-source-overnight/batch-06/guard_audit.py
  adapter ledger/Q-invocation postconditions and justifications:
    experiments/v3/cut-source-overnight/batch-06/a_audit.py
    experiments/v3/cut-source-overnight/batch-06/a_domain.py (source_only, justification)
  retained case shape (rows, prefixes, events):
    experiments/v3/eight-hour-research-20260910-01a08a22/check.py

Finite accounting: charge.take(1) is called once before inspecting each case
prefix; audited_prefixes counts every charged prefix. Statuses: 'supported'
means every applicable check on the retained cases matched with no
underdetermined obligation event; 'counterexample' means at least one
falsifiable expected/observed mismatch; 'unproved' means no mismatch but some
obligation event could not be decided from retained fields; 'not_applicable'
means no collect-family action occurs in any case.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight'))
try:
    import s_domain as D
except Exception:
    D = None

ENC = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':'))
REFUSALS = ('no-captured-source', 'stale-collection', 'incomplete-inventory', 'incomplete-registry')
CUT_NAMES = ('success', 'failure', 'ambiguous', 'later-start-only', 'foreign', 'foreign-attempt',
             'conflict', 'prior-unresolved', 'late-receipt', 'missing-original')
QRESET = ('restart', 'authority-restart', 'replay', 'reclaim')
FIELDS = ('registration', 'attempts', 'append_log', 'collection', 'collected', 'attestation',
          'source_revision', 'source_generation', 'paused', 'cut_delivery')
JUST = {
    'ledger': 'Same literal call, parameters and visible reply handled by the initialized adapter source ledger; Q state is unchanged.',
    'refused': 'Same literal call refused by the adapter source guard; refusal remains visible and Q state is unchanged.',
    'attest': 'Current complete ledger capture permits the same literal Q attestation; retain actual Q response and commit journal attestation only on Q acceptance.',
}


def j(x):
    if isinstance(x, dict):
        return {str(k): j(v) for k, v in sorted(x.items(), key=lambda e: str(e[0]))}
    if isinstance(x, (list, tuple)):
        return [j(v) for v in x]
    return x if x is None or isinstance(x, (str, int, float, bool)) else repr(x)


def dt(x):
    if isinstance(x, (list, tuple)):
        return tuple(dt(v) for v in x)
    if isinstance(x, dict):
        return {k: dt(v) for k, v in x.items()}
    return x


def fix(name):
    try:
        return D.q.lit.fixture(name)
    except Exception:
        return None


def reg_value(name):
    f = fix(name); h = f['original']['cut']['trace_header']
    return ENC([h['intent'], h['admission'], f['binding']['body']['reservation']])


def raw_append(verb):
    # Independent decode of an append:<name>:<index>:<variant> offered record.
    _, name, i, var = verb.split(':'); i = int(i)
    rec = dict(fix(name)['original']['records'][i])
    gen = ('cut-source', 'collectorA', 'effectA', 1 if var == 'new-boot' else 0)
    if var == 'wrong-attempt':
        rec['attempt_id'] = 'attempt:foreign'
    if var == 'wrong-body':
        rec['payload_digest'] = 'sha256:' + '9' * 64
    return ('collectorB' if var == 'foreign' else 'collectorA'), gen, i, ENC(rec)


def seed(init):
    g = lambda k, d: dt(init.get(k, d)) if isinstance(init, dict) else d
    return {'registration': g('registration', ''), 'attempts': g('attempts', ()),
            'append_log': g('append_log', ()), 'collection': g('collection', ()),
            'collected': tuple((p[0], p[1]) for p in g('collected', ())),
            'rev': g('source_revision', 0), 'gen': g('source_generation', ()),
            'paused': g('paused', None), 'lgap': False, 'qgap': False}


def apply_ok(verb, s):
    try:
        if verb.startswith('register:'):
            if s['registration'] == '':
                s['registration'] = reg_value(verb[9:]); s['rev'] += 1
        elif verb.startswith(('attempt:', 'atomic:')):
            if verb.startswith('attempt:'):
                number, raw = int(verb[8:]), None
            else:
                _, name, i = verb.split(':')
                rec = fix(name)['original']['records'][int(i)]
                number, raw = rec['attempt_number'], ENC(rec)
            s['attempts'] += (('attemptA' if number == 1 else 'retained-attemptA' + str(number),
                               'attempt:' + str(number)),)
            s['rev'] += 1
            if raw is not None:
                s['append_log'] += (raw,)
        elif verb.startswith('append:'):
            s['append_log'] += (raw_append(verb)[3],); s['rev'] += 1
        elif verb == 'collect-open':
            s['collection'] = (s['gen'], s['rev'], s['registration'], s['attempts'], len(s['append_log']))
            s['collected'] = ()
        elif verb.startswith('collect:'):
            i = int(verb[8:])
            s['collected'] = tuple(sorted(s['collected'] + ((i, s['append_log'][i]),)))
        elif verb == 'source-restart':
            g = s['gen']
            if isinstance(g, tuple) and g and isinstance(g[-1], int):
                s['gen'] = g[:-1] + (g[-1] + 1,)
            else:
                s['qgap'] = True
        elif verb == 'pause':
            s['paused'] = True
        elif verb in QRESET:
            s['qgap'] = True
    except Exception:
        s['lgap'] = True


def predict(verb, s):
    """Expected guard reason for collect-family verbs, or None when not handled here."""
    if verb == 'collect-open':
        return ('no-registration' if s['registration'] == '' else 'ok'), None
    if verb.startswith('collect:'):
        i = int(verb[8:]); c = s['collection']
        if not c:
            return 'outside-captured-cut', 'no-collection'
        if i < 0:
            return 'outside-captured-cut', 'lower'
        if i >= c[4]:
            return 'outside-captured-cut', 'upper-capture'
        if i >= len(s['append_log']):
            return 'outside-captured-cut', 'upper-log'
        if any(x == i for x, _ in s['collected']):
            return 'duplicate-collection', None
        return 'ok', None
    if verb.startswith('source:'):
        return 'registered-protocol-required', None
    return None, None


def predict_attest(s, name):
    c = s['collection']
    if not c or not name:
        return 'no-captured-source'
    f = fix(name)
    if c[0] != s['gen'] or c[1] != s['rev']:
        return 'stale-collection'
    exp = tuple((i, ENC(r)) for i, r in enumerate(f['original']['records']))
    if len(exp) != c[4] or s['collected'] != exp:
        return 'incomplete-inventory'
    amap = tuple(tuple(r) for r in f['binding']['body']['attempt_mapping'])
    if c[2] != reg_value(name) or c[3] != amap:
        return 'incomplete-registry'
    return 'ok'


def extract(event):
    out = {}
    if isinstance(event, dict):
        for layer in (event,) + tuple(event[k] for k in ('patch', 'state', 'after', 'post', 'fields')
                                      if isinstance(event.get(k), dict)):
            for f in FIELDS:
                if f in layer:
                    out[f] = dt(layer[f])
    return out


def inspect_cases(cases, charge):
    obs, lims, mism = [], [], []
    audit = undet = oevents = 0
    refusals, schedules, names = {}, set(), []
    stopped = None
    for case in cases or []:
        try:
            src = case['source']; acts = list(src['actions']); rows = case['rows']
            prefs = case.get('prefixes') or []
            events = src.get('events') or []
            name = case.get('case', '?'); names.append(name); schedules.add(tuple(acts))
            prof = src.get('profile') or {}
            req = prof.get('requires') or {}
            valid = len(acts) == len(set(acts)) and set(acts) == set(prof.get('actions', ()))
            done = set()
            for a in acts:
                valid = valid and set(req.get(a, ())) <= done
                done.add(a)
            obs.append({'kind': 'schedule', 'case': name, 'actions': len(acts),
                        'valid_linear_extension': valid, 'rows': len(rows), 'prefixes': len(prefs)})
            if not valid:
                mism.append({'kind': 'schedule', 'case': name, 'expected': 'unique dependency-closed order',
                             'observed': acts})
            if len(rows) != len(acts) or len(prefs) != len(acts) + 1:
                lims.append(name + ': rows/prefixes not aligned to schedule length')
                undet += 1
            s = seed(src.get('initial'))
            seen = {}
            for p in range(len(acts) + 1):
                try:
                    charge.take(1)
                except Exception as e:
                    stopped = 'charge.take(1) failed at prefix %d of %s: %r' % (p, name, e)
                    break
                audit += 1
                if p < len(prefs):
                    item = prefs[p] or {}
                    bad = [f for f in item.get('differing_journal_fields', ())
                           if f in ('collection', 'collected', 'attestation')]
                    if bad:
                        mism.append({'kind': 'journal-difference', 'case': name, 'prefix': p,
                                     'expected': 'collection fields absent', 'observed': bad})
                if p == len(acts):
                    continue
                row = rows[p] if p < len(rows) else {}
                a = row.get('source_action', acts[p])
                if a != acts[p] or row.get('index', p) != p:
                    mism.append({'kind': 'chronology', 'case': name, 'prefix': p,
                                 'expected': [acts[p], p], 'observed': [a, row.get('index')]})
                v = a.split('@')[0]
                so = row.get('source_observation') or {}
                ao = row.get('adapter_observation') or row.get('target_observation') or {}
                dec, adec, inv = so.get('decision'), ao.get('decision'), row.get('q_invoked')
                reason = dec[len(v) + 1:] if isinstance(dec, str) and dec.startswith(v + ':') else None
                if reason is None:
                    mism.append({'kind': 'decision-shape', 'case': name, 'prefix': p,
                                 'expected': v + ':<reason>', 'observed': dec})
                if adec is not None and adec != dec:
                    mism.append({'kind': 'decision-divergence', 'case': name, 'prefix': p,
                                 'expected': dec, 'observed': adec})
                obligation = v == 'collect-open' or v.startswith(('collect:', 'source:'))
                if obligation:
                    oevents += 1
                    if reason and reason != 'ok':
                        refusals[reason] = refusals.get(reason, 0) + 1
                    if v == 'source-attest':
                        if not s['collection'] and not s['lgap']:
                            pred = 'no-captured-source'
                            w = {'kind': 'attest-witness', 'case': name, 'prefix': p, 'action': a,
                                 'expected': v + ':' + pred, 'observed': dec}
                            (mism if dec != w['expected'] else obs).append(w)
                        elif s['lgap'] or s['qgap']:
                            undet += 1
                            obs.append({'kind': 'undetermined', 'case': name, 'prefix': p, 'action': a,
                                        'cause': 'ledger/generation projection gap'})
                        else:
                            cands = sorted({n for n in CUT_NAMES if fix(n)} |
                                           {x.split(':')[1] for x in acts
                                            if x.split('@')[0].split(':')[0] in
                                            ('append', 'atomic', 'register') and fix(x.split(':')[1])})
                            preds = {n: predict_attest(s, n) for n in cands}
                            if not cands:
                                undet += 1
                                obs.append({'kind': 'undetermined', 'case': name, 'prefix': p,
                                            'action': a, 'cause': 'no fixture-resolvable cut candidates'})
                            elif reason not in set(preds.values()):
                                mism.append({'kind': 'attest', 'case': name, 'prefix': p,
                                             'expected': preds, 'observed': dec})
                            else:
                                obs.append({'kind': 'inventory-witness', 'case': name, 'prefix': p,
                                            'action': a, 'observed': dec,
                                            'consistent_cuts': [n for n, r in preds.items() if r == reason],
                                            'collected_indices': [i for i, _ in s['collected']],
                                            'captured_cut': s['collection'][4]})
                    elif s['lgap']:
                        undet += 1
                        obs.append({'kind': 'undetermined', 'case': name, 'prefix': p, 'action': a,
                                    'cause': 'ledger projection gap'})
                    else:
                        pred, bound = predict(v, s)
                        exp = v + ':' + pred
                        w = {'kind': 'decision-witness', 'case': name, 'prefix': p, 'action': a,
                             'expected': exp, 'observed': dec}
                        if v.startswith('collect:'):
                            w.update(index=int(v[8:]), captured_cut=s['collection'][4] if s['collection'] else None,
                                     log_length=len(s['append_log']))
                            if bound:
                                w['bound'] = bound
                        (mism if dec != exp else obs).append(w)
                    if inv is not None:
                        expected_inv = (reason not in REFUSALS) if v == 'source-attest' else False
                        if reason is not None and inv != expected_inv:
                            mism.append({'kind': 'invocation-mask', 'case': name, 'prefix': p,
                                         'expected': expected_inv, 'observed': inv, 'decision': dec})
                    jw = row.get('justification')
                    if jw is not None:
                        exp_j = JUST['ledger'] if v != 'source-attest' else JUST['attest' if inv else 'refused']
                        if jw != exp_j:
                            mism.append({'kind': 'justification', 'case': name, 'prefix': p,
                                         'expected': exp_j, 'observed': jw})
                live = extract(events[p]) if p < len(events) else {}
                seen.update(live)
                if 'collection' in seen and v == 'collect-open' and reason == 'ok':
                    w = {'kind': 'capture-witness', 'case': name, 'prefix': p,
                         'expected': j(s['collection']), 'observed': j(seen['collection'])}
                    (mism if seen['collection'] != s['collection'] else obs).append(w)
                if 'collected' in seen and v.startswith('collect:') and reason == 'ok':
                    w = {'kind': 'sorting-witness', 'case': name, 'prefix': p, 'action': a,
                         'expected': j(s['collected']), 'observed': j(seen['collected'])}
                    (mism if seen['collected'] != s['collected'] else obs).append(w)
                if reason == 'ok':
                    apply_ok(v, s)
            if stopped:
                break
        except Exception as e:
            undet += 1
            lims.append('case inspection raised: ' + repr(e))
    if stopped:
        lims.append(stopped)
    obs.append({'kind': 'accounting', 'cases': len(names), 'audited_prefixes': audit,
                'obligation_events': oevents, 'underdetermined': undet, 'mismatches': len(mism),
                'unique_schedules': len(schedules),
                'schedules_sha256': hashlib.sha256(ENC(sorted(map(list, schedules))).encode()).hexdigest()})
    obs.append({'kind': 'refusal-census', 'refusals': refusals})
    lims += ['bounded to the supplied retained cases; no all-order or global theorem claim',
             'fixture-dependent expectations need s_domain/q_domain' + (' (unavailable)' if D is None else ''),
             'event payload field exposure is best-effort; decision witnesses are always retained']
    if mism:
        status = 'counterexample'
    elif stopped or undet:
        status = 'unproved'
    elif oevents == 0:
        status = 'not_applicable'
    else:
        status = 'supported'
    return j({'status': status, 'observations': obs + mism, 'limitations': lims,
              'audited_prefixes': audit})
