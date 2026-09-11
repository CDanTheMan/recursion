"""Adversarial retained-evidence controls for o30-guard-prediction: the
conditional 40320-order first-refusing-guard classification versus actual
complete typed histories. Source anchors (unchanged originals keep authority):
experiments/v3/eight-hour-research-20260910-01a08a22-slice2/guard_order.py
(symbolic 40320 classes, four source hypotheses); .../check.py (typed case
shape; c.t.restore decodes retained per-prefix states; no reducer runs here);
experiments/v3/cut-source-overnight/s_audit.py and s_domain.py (refusal
precedence and fixture representation); boundary.py in this campaign
(subclass context only; no boundary helper is imported or called).
charge.take(1) precedes every prefix inspection and every re-inspected
mutant, so charge = inspections x restored prefixes. Reachable-witness
controls mutate retained rows/schedule literals only; corrupting state inside
the opaque trace-event encoding needs its own reachable witness and stays a
recorded limitation, never claimed.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/eight-hour-research-20260910-01a08a22'))
import check as c

d, ATT = c.d, 'source-attest'
CORE = ('collect-open@11', 'collect:0@12', 'collect:1@13', 'collect:2@14',
        'attempt:2@15', 'attempt:3@16', 'attempt:4@17', 'source-restart@18')
HYPOTHESES = ('fixed-successful-setup', 'original-profile-linear-extension',
              'fixed-cut-maps-attempt1-only', 'nonmutant-original-semantics')


def _verb(a): return a.partition('@')[0]
def _att(actions): return next((i for i, a in enumerate(actions) if _verb(a) == ATT), None)
def _swap(seq, i, j):
    seq = list(seq); seq[i], seq[j] = seq[j], seq[i]; return tuple(seq)


def _member(profile, schedule):  # exact linear-extension membership, original profile
    if len(schedule) != len(profile['actions']) or set(schedule) != set(profile['actions']):
        return False
    done = set()
    for a in schedule:
        if not set(profile['requires'][a]) <= done:
            return False
        done.add(a)
    return True


def _predict(schedule):  # first-refusing-guard class from core order, packet-06 hypotheses
    mid = tuple(schedule[11:19])
    if len(mid) != 8 or set(mid) != set(CORE): return None
    p = {a: i for i, a in enumerate(mid)}
    ok = [CORE[4]]
    if p[CORE[4]] < p[CORE[5]]: ok.append(CORE[5])
    if p[CORE[4]] < p[CORE[5]] < p[CORE[6]]: ok.append(CORE[6])
    if not all(p[a] < p[CORE[0]] for a in (*ok, CORE[7])): return 'stale-collection'
    return 'incomplete-registry' if all(p[CORE[0]] < p[a] for a in CORE[1:4]) else 'incomplete-inventory'


def _field_guard(s):  # refusal class re-derived from actual pre-attestation source fields
    cap, name = s['collection'], s['cut_delivery']
    if not cap or not name: return 'no-captured-source'
    if not d.exact(tuple(cap[:2]), (s['source_generation'], s['source_revision'])):
        return 'stale-collection'
    got = sorted(s['collected'])
    if [i for i, _ in got] != list(range(cap[4])) or any(
            i >= len(s['append_log']) or not d.exact(raw, s['append_log'][i])
            for i, raw in got): return 'incomplete-inventory'
    try:
        same = d.exact(cap[2], d.s.registration(name)) and d.exact(cap[3], d.s.mapping(name))
    except Exception:
        return 'registry-unchecked'
    return 'delegated' if same else 'incomplete-registry'


def inspect_cases(cases, charge):
    observations, limitations = [], []
    audited = attested = 0
    cx = unproved = False
    hyp = {h: [0, 0] for h in HYPOTHESES}  # [locally observed, assumed-or-failed]
    for case in cases:
        ss, aa = c.t.restore(case['source']), c.t.restore(case['adapter'])
        actions, rows = case['source']['actions'], case['rows']
        member, att, invoked = _member(case['source']['profile'], actions), _att(actions), 0
        for i in range(len(ss)):
            charge.take(1)
            audited += 1
            if not i: continue
            row = rows[i - 1] if i - 1 < len(rows) else None
            act = actions[i - 1] if i - 1 < len(actions) else None
            invoked += bool(row and row['q_invoked'])
            ok = bool(row) and act is not None and (
                row['index'] == i - 1 and row['source_action'] == act
                and row['adapter_action'] == act and type(row['q_invoked']) is bool
                and ss[i]['decision'] == row['source_observation']['decision']
                and aa[i]['decision'] == row['adapter_observation']['decision']
                and ss[i]['decision'].startswith(_verb(act) + ':')
                and len(aa[i]['invocations']) == invoked)
            if not ok:
                observations.append(dict(case=case['case'], kind='retained-row-inconsistency',
                                         prefix=i, action=act, member=member))
                cx, unproved = cx or member, unproved or not member
        s11 = ss[11] if len(ss) > 11 else {}
        h1 = bool(s11.get('registration')) and len(s11.get('attempts', ())) == 1 \
            and len(s11.get('append_log', ())) == 3 and not s11.get('paused')
        if att is None or att >= len(rows) or att >= len(ss):
            unproved = True
            limitations.append(dict(case=case['case'], kind='attestation-literal-or-row-missing'))
            continue
        attested += 1
        row, state = rows[att], ss[att]
        predicted, derived = _predict(actions), _field_guard(state)
        try:
            h3 = bool(state['cut_delivery']) and \
                len(state['attempts']) > len(d.s.mapping(state['cut_delivery']))
        except Exception:
            h3 = None
        vals = dict(zip(HYPOTHESES, (h1, member, h3, None)))
        for h, v in vals.items(): hyp[h][v is not True] += 1
        obs = dict(case=case['case'], kind='attestation-observation', chronological_index=att,
                   member=member, predicted_guard=predicted, field_derived_guard=derived,
                   observed_decision=row['source_observation']['decision'],
                   adapter_decision=row['adapter_observation']['decision'],
                   q_invoked=row['q_invoked'], hypotheses=vals)
        observations.append(obs)
        if not (predicted is not None and obs['observed_decision'] == ATT + ':' + predicted
                and obs['adapter_decision'] == obs['observed_decision'] and row['q_invoked'] is False):
            if member and h1:
                cx, obs['classification'] = True, 'original-domain-counterexample'
            else:
                unproved, obs['classification'] = True, 'unreachable-or-hypothesis-failed-mismatch'
        if derived != predicted:
            unproved = True
            limitations.append(dict(case=case['case'], predicted=predicted, derived=derived,
                kind='field-derived-delegated-not-decidable' if derived == 'delegated'
                else 'field-derived-guard-differs-from-order-prediction'))
    status = ('counterexample' if cx else 'not_applicable' if not attested
              else 'unproved' if unproved else 'supported')
    return dict(status=status, observations=observations, limitations=limitations,
                audited_prefixes=audited, attested_cases=attested,
                hypothesis_accounting={h: dict(observed=v[0], assumed_or_failed=v[1])
                                       for h, v in hyp.items()})


def run_controls(cases, inspect_cases, charge):
    """Observed control outcomes; each mutant is fully re-inspected/re-charged."""
    base, results, charged = list(cases), [], 0

    def trial(name, mutate, want, note=None):
        nonlocal charged
        mutant = copy.deepcopy(base)
        if mutate: mutate(mutant)
        try:
            out = inspect_cases(mutant, charge)
            got, charged = out['status'], charged + out['audited_prefixes']
        except Exception as error:
            got = 'raised-' + type(error).__name__
        results.append(dict(control=name, expected=sorted(want), observed=got,
                            detected=got in want, note=note))

    def each_att(cs, fn):
        for x in cs:
            i = _att(x['source']['actions'])
            if i is not None: fn(x['rows'][i])

    def resync(x):
        for i, row in enumerate(x['rows']):
            row['source_action'] = x['source']['actions'][i]
            row['adapter_action'] = x['adapter']['actions'][i]

    def reorder(cs):  # swap a prediction-changing reachable middle pair, rows resynced
        for x in cs:
            acts = tuple(x['source']['actions'])
            pair = next(((i, j) for i in range(11, 19) for j in range(i + 1, 19)
                         if _predict(_swap(acts, i, j)) != _predict(acts)), None)
            if pair:
                for side in ('source', 'adapter'):
                    x[side]['actions'] = _swap(x[side]['actions'], *pair)
                resync(x)

    def unreachable(cs):  # non-linear-extension order plus rewritten refusal
        for x in cs:
            for side in ('source', 'adapter'):
                x[side]['actions'] = _swap(x[side]['actions'], 0, 18)
            resync(x)
            each_att([x], lambda r: r['source_observation'].update(decision=ATT + ':ok'))

    trial('deepcopy-baseline', None, {'supported', 'unproved', 'not_applicable'},
          'unmutated re-inspection must not invent counterexample')
    trial('refusal-decision-rewritten',
          lambda cs: each_att(cs, lambda r: r['source_observation'].update(decision=ATT + ':ok')),
          {'counterexample'}, 'prefix flags/stored hashes untouched: detection is semantic')
    trial('adapter-decision-rewritten',
          lambda cs: each_att(cs, lambda r: r['adapter_observation'].update(decision=ATT + ':x')),
          {'counterexample'})
    trial('false-q-invocation-on-refusal',
          lambda cs: each_att(cs, lambda r: r.update(q_invoked=True)), {'counterexample'})
    trial('reachable-core-reorder-prediction', reorder, {'counterexample'},
          'reachable middle permutation; retained refusal then mismatches prediction')
    trial('unreachable-order-not-counterexample', unreachable, {'unproved', 'not_applicable'},
          'broken linear extension is never reported as a domain counterexample')
    trial('dropped-refusal-literal', lambda cs: [
          x[side].update(actions=tuple(a for a in x[side]['actions'] if _verb(a) != ATT))
          for x in cs for side in ('source', 'adapter')], {'not_applicable', 'unproved'},
          'attestation literal removed from schedules; rows still record it')
    if len(base) > 1:
        trial('cross-case-row-graft', lambda cs: cs[0].update(rows=copy.deepcopy(cs[1]['rows'])),
              {'counterexample'})
    return dict(control_results=results, all_detected=all(r['detected'] for r in results),
                charged_prefix_inspections=charged,
                missing_witness='state-level corruption inside opaque trace events needs its own reachable witness; not claimed')
