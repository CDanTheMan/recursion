"""Bounded retained-certificate audit of the inherited discriminating-control design.

Obligation o28-control-adequacy: a negative control is adequate only when it injects
an actual causal fault into retained typed evidence, the unchanged audit detects that
fault, and a falsifiable expected/observed witness is retained. A control mutating
nothing the audit binds, or "passing" on already-invalid base evidence, is vacuous.

inspect_cases(cases, charge) takes typed case objects as produced by the original
checker (c.run_history results or c.artifact-decoded retained certificates). Per case
it (1) re-runs the unchanged retained-state audit as the positive witness, (2)
re-verifies per-prefix causal-ledger digests, staged-identity proof bindings and
relation verdicts, then (3) replays the inherited control battery as minimal
corruptions, retaining one witness per exercised control. No transition/step reducer
is executed: only retained-evidence audit machinery is reused (restore digest
binding, the s_audit/a_audit checks inside c.audit_case, semantic.advance ledger
replay, identity.compare/identity_audit prefix certificates). boundary.py helpers
are never imported. Verdicts are bounded to the supplied cases: no global theorem,
no new reachability claim, no accepted scientific PASS.

Accounting: charge.take(1) precedes every per-prefix inspection, including each full
prefix re-inspection inside a mutated-variant re-audit; all repetitions count and
audited_prefixes reports every charged inspection. Charge exhaustion => 'unproved'.

Anchors (unchanged originals): c.audit_case/c.run_history/c.Counter and the COMMON
control taxonomy in experiments/v3/eight-hour-research-20260910-01a08a22/{check,
sharded}.py; typed transport artifact.py (same dir); restore/comparison rows in
experiments/v3/cut-source-overnight/batch-06/adapter_traces.py; staged relation and
its audit in batch-07/identity.py + identity_audit.py; required discriminating
controls (journal-only disagreement, actual Q generation, dropped refusal,
cross-case proof, tuple loss; outer-hash rejection is not a semantic control) in
docs/v3/construction/swarm-research-20260911-155142/wave04/review-defects.json.
"""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/eight-hour-research-20260910-01a08a22'))
try:
    import check as c
    _IMPORT_ERROR = None
except Exception as exc:  # missing original closure is itself a limitation
    c, _IMPORT_ERROR = None, exc

FAIL = (ValueError, KeyError, IndexError, TypeError, AssertionError)
REQUIRED = ('case', 'unit', 'outcome', 'source', 'adapter', 'rows',
            'incarnation_pairs', 'prefixes')
MAX_RETAINED = 16


class _Exhausted(Exception):
    """The audit charge refused a take; stop instead of claiming a verdict."""


def _shape(case):
    return (isinstance(case, dict) and all(k in case for k in REQUIRED)
            and type(case['prefixes']) is list and type(case['rows']) is list
            and len(case['rows']) + 1 == len(case['prefixes'])
            and len(case['source'].get('actions', ())) == len(case['rows']))


def _retained_error(case):
    """None iff the unchanged audit exactly reproduces the stored prefix rows."""
    try:
        recomputed = c.audit_case(case)
    except FAIL as exc:
        return 'audit-rejected: ' + str(exc)
    return None if c.d.exact(recomputed, case['prefixes']) else 'prefix-certificate-mismatch'


def _prefix_faults(case, prow, i, pairs, ss, aa):
    f = []
    if prow.get('prefix') != i:
        f.append('prefix-index')
    if prow.get('pairs_sha256') != c.d.digest(pairs):
        f.append('causal-ledger-digest')
    if any(p.get('source_event', i) >= i or p.get('target_event', i) >= i for p in pairs):
        f.append('causal-pair-from-future')
    if prow.get('incarnation_pair_established_by_identity') is not False:
        f.append('identity-grants-authority')
    if prow.get('strict_related') is not (not prow['strict_differing_common_fields']
                                          and not prow['differing_journal_fields']):
        f.append('strict-verdict-vacuous')
    if prow.get('related') is not (not prow['differing_common_fields']
                                 and not prow['differing_journal_fields']):
        f.append('extended-verdict-vacuous')
    if set(prow['differing_common_fields']) - set(prow['strict_differing_common_fields']):
        f.append('extension-wider-than-strict')
    proof = prow.get('identity_proof')
    if prow.get('staged_rule') == 'original-object-identity' and proof is None:
        f.append('identity-without-retained-witness')
    if proof is not None:
        if proof.get('case') != case['case'] or proof.get('prefix') != i:
            f.append('proof-not-bound-to-case-prefix')
        if (proof.get('source_prefix_sha256') != c.d.digest(case['source']['events'][:i])
                or proof.get('adapter_prefix_sha256') != c.d.digest(case['adapter']['events'][:i])):
            f.append('proof-prefix-detached')
        if (proof.get('source_state_sha256') != c.d.digest(ss[i])
                or proof.get('adapter_state_sha256') != c.d.digest(aa[i])):
            f.append('proof-state-detached')
    if i:
        row = case['rows'][i - 1]
        if prow.get('strict_related') is not row.get('state_related'):
            f.append('strict-baseline-mismatch')
        if (row.get('adapter_observation', {}).get('decision') == 'source-attest:ok'
                and row.get('q_invoked') is not True):
            f.append('adapter-accepted-attestation-without-invocation')
    return f


def _info(case, snaps):
    rows = case['rows']
    dec = [x.get('source_observation', {}).get('decision') for x in rows]
    refused = [j for j, x in enumerate(dec) if isinstance(x, str) and not x.endswith(':ok')]
    ident = [x['prefix'] for x in case['prefixes'] if x.get('identity_proof')]
    return dict(refused=refused, n_prefixes=len(case['prefixes']),
                refused_attest=[j for j in refused
                                if rows[j].get('source_action', '').split('@')[0] == 'source-attest'
                                and rows[j].get('q_invoked') is False],
                identity=ident, identity_empty=[i for i in ident if not snaps[i]],
                pairs=bool(case['incarnation_pairs']),
                q_len=len(case['adapter'].get('q_profile', {}).get('actions', ())))


def _m_drop(trace):  # drop last retained event; returns (before, after) regions
    ev = trace['events']; before = list(ev); ev.pop(); return before, ev


def _mutations(m, i):
    return {
        'dropped-visible-source-event': lambda: _m_drop(m['source']),
        'dropped-visible-adapter-event': lambda: _m_drop(m['adapter']),
        'changed-action-translation': lambda: _set(m['rows'][0], 'justification', {'forged': True}),
        'refused-attestation-marked-Q-invoked': lambda: _set(
            m['rows'][i['refused_attest'][0]], 'q_invoked', True),
        'dropped-refused-event': lambda: _pop(m['source']['events'], i['refused'][0]),
        'renumbered-Q-occurrence-positions': lambda: _set(
            m['adapter']['q_profile'], 'actions',
            tuple(reversed(m['adapter']['q_profile']['actions']))),
        'causal-index-from-future': lambda: _set(
            m['incarnation_pairs'][0], 'source_event', 10 ** 9),
        'source-actions-tuple-loss': lambda: _set(
            m['source'], 'actions', list(m['source']['actions'])),
        'forged-stored-prefix-verdict': lambda: _set(
            m['prefixes'][1], 'related', not m['prefixes'][1]['related']),
    }


def _set(obj, key, value):
    before = copy.deepcopy(obj); obj[key] = value; return before, obj


def _pop(seq, index):
    before = list(seq); seq.pop(index); return before, seq


def _mk_full(name, needs, target, expect):
    def run(ent, spend):
        variant = copy.deepcopy(ent['case'])
        before, after = _mutations(variant, ent['info'])[name]()
        changed = not c.d.exact(before, after)
        spend(len(ent['case']['prefixes']))
        err = _retained_error(variant)
        return dict(control=name, case=ent['case']['case'], target=target,
                    expected='detected', expected_invariant=expect, changed=changed,
                    original_sha256=c.d.digest(before), mutated_sha256=c.d.digest(after),
                    observed='detected' if err else 'unchanged' if not changed else 'accepted',
                    attributed=bool(err and expect in err), reason=err or 'variant accepted')
    return name, needs, run


def _mk_compare(name, needs, pick, mutate, field):
    def run(ent, spend):
        i = pick(ent['info']); spend(1)
        ss, aa = list(ent['ss']), list(ent['aa'])
        ss[i], aa[i] = copy.deepcopy(ss[i]), copy.deepcopy(aa[i])
        mutate(ss[i], aa[i])
        out = c.relation.compare(ent['case'], ss, aa, i, copy.deepcopy(ent['snaps'][i]))
        differing = out['differing_common_fields'] + out['differing_journal_fields']
        detected = out['related'] is False and field in differing
        return dict(control=name, case=ent['case']['case'], prefix=i, target=field,
                    expected='detected', changed=True,
                    original_sha256=c.d.digest(ent['aa'][i]),
                    mutated_sha256=c.d.digest(aa[i]),
                    observed='detected' if detected else 'accepted', attributed=detected,
                    reason='differing=%r related=%r' % (differing, out['related']))
    return name, needs, run


def _mk_identity(name, needs, pick, tamper):
    def run(ent, spend):
        i = pick(ent['info']); spend(1)
        row = copy.deepcopy(ent['case']['prefixes'][i])
        w = dict(control=name, case=ent['case']['case'], prefix=i, expected='detected',
                 changed=True, original_sha256=c.d.digest(row))
        tamper(row)
        w['mutated_sha256'] = c.d.digest(row)
        try:
            c.identity_audit.check(row, ent['case'], ent['ss'], ent['aa'], i,
                                   copy.deepcopy(ent['snaps'][i]))
        except FAIL as exc:
            return dict(w, observed='detected', attributed=True, reason=str(exc))
        return dict(w, observed='accepted', attributed=False,
                    reason='tampered prefix certificate accepted')
    return name, needs, run


TWO = lambda i: i['n_prefixes'] >= 2
SPECS = [
    _mk_full('dropped-visible-source-event', lambda i: True,
             'source.events[-1]', 'complete visible event inventory'),
    _mk_full('dropped-visible-adapter-event', lambda i: True,
             'adapter.events[-1]', 'complete visible event inventory'),
    _mk_full('changed-action-translation', lambda i: True,
             'rows[0].justification', 'actual Q invocation and translation retained'),
    _mk_full('refused-attestation-marked-Q-invoked', lambda i: i['refused_attest'],
             'rows[j].q_invoked', 'actual Q invocation and translation retained'),
    _mk_full('dropped-refused-event', lambda i: i['refused'],
             'source.events[j]', 'complete visible event inventory'),
    _mk_full('renumbered-Q-occurrence-positions', lambda i: i['q_len'] >= 2,
             'adapter.q_profile.actions', 'fixed Q occurrence positions'),
    _mk_full('causal-index-from-future', lambda i: i['pairs'],
             'incarnation_pairs[0].source_event', 'complete immutable causal pair ledger'),
    _mk_full('source-actions-tuple-loss', lambda i: True,
             'source.actions(type)', 'all visible actions matched'),
    _mk_full('forged-stored-prefix-verdict', TWO,
             'prefixes[1].related', 'prefix-certificate-mismatch'),
    _mk_compare('journal-only-disagreement', TWO, lambda i: 1,
                lambda s, a: a['journal'].update(
                    source_revision=a['journal']['source_revision'] + 1), 'source_revision'),
    _mk_compare('changed-actual-Q-core-generation', TWO, lambda i: 1,
                lambda s, a: a['core'].update(
                    source_generation=c.d.q.source_token(10 ** 9)), 'source_generation'),
    _mk_compare('staged-identity-authorizes-selection', lambda i: i['identity_empty'],
                lambda i: i['identity_empty'][0],
                lambda s, a: (s.update(selected=s['staged'][0]),
                              a['core'].update(selected=s['staged'][0])), 'selected'),
    _mk_identity('cross-case-identity-proof', lambda i: i['identity'],
                 lambda i: i['identity'][0],
                 lambda row: row['identity_proof'].update(case='other-case')),
    _mk_identity('identity-proof-claims-authority', lambda i: i['identity'],
                 lambda i: i['identity'][0],
                 lambda row: row.update(incarnation_pair_established_by_identity=True)),
]


def inspect_cases(cases, charge):
    observations, limitations, faults = [], [], []
    audited = [0]

    def spend(n=1):
        for _ in range(n):
            try:
                charge.take(1)
            except Exception as exc:
                raise _Exhausted(str(exc))
        audited[0] += n

    def finish(status):
        return dict(status=status, observations=observations,
                    limitations=limitations, audited_prefixes=audited[0])

    if c is None:
        limitations.append('original audit closure unimportable: %r' % (_IMPORT_ERROR,))
        return finish('unproved')
    if not hasattr(charge, 'take'):
        limitations.append('charge object provides no take(n)')
        return finish('unproved')
    try:
        case_list = list(cases)
    except TypeError:
        limitations.append('cases is not an iterable of typed case objects')
        return finish('not_applicable')

    retained, inspected, refusals = [], 0, 0
    try:
        for case in case_list:
            if not _shape(case):
                limitations.append('skipped object without typed case shape')
                continue
            inspected += 1
            spend(len(case['prefixes']))
            err = _retained_error(case)
            if err:
                faults.append(dict(case=case['case'],
                                   fault='unmutated-certificate-rejected', reason=err))
                continue
            try:
                ss = c.t.restore(case['source']); aa = c.t.restore(case['adapter'])
            except FAIL as exc:
                faults.append(dict(case=case['case'], fault='trace-restore', reason=str(exc)))
                continue
            pairs, snaps, nf = [], [], len(faults)
            for i, prow in enumerate(case['prefixes']):
                spend(1)
                if i:
                    action = case['source']['actions'][i - 1]
                    try:
                        c.r.advance(pairs, ss[i - 1], c.t.core_view(aa[i - 1]), ss[i],
                                    c.t.core_view(aa[i]), action, action, i - 1, i - 1)
                    except FAIL as exc:
                        faults.append(dict(case=case['case'], prefix=i,
                                           fault='causal-ledger-replay', reason=str(exc)))
                        break
                snaps.append(copy.deepcopy(pairs))
                try:
                    found = _prefix_faults(case, prow, i, pairs, ss, aa)
                except FAIL as exc:
                    found = ['prefix-row-malformed: ' + str(exc)]
                faults.extend(dict(case=case['case'], prefix=i, fault=f) for f in found)
            if len(snaps) < len(case['prefixes']):
                continue
            info = _info(case, snaps)
            refusals += len(info['refused'])
            if len(faults) == nf and len(retained) < MAX_RETAINED:
                retained.append(dict(case=case, ss=ss, aa=aa, snaps=snaps, info=info))
        for name, needs, run in SPECS:
            ent = next((e for e in retained if needs(e['info'])), None)
            if ent is None:
                limitations.append('control not exercised, no retained witness: ' + name)
                continue
            w = run(ent, spend)
            observations.append(w)
            if w['observed'] == 'accepted' or (w['observed'] == 'detected' and not w['changed']):
                faults.append(dict(case=ent['case']['case'], control=name,
                                   fault='control-not-discriminating', reason=w['reason']))
            elif w['observed'] != 'detected':
                limitations.append('control mutation vacuous on witness: ' + name)
    except _Exhausted as exc:
        limitations.append('audit charge exhausted: ' + str(exc))

    observations.append(dict(kind='summary', supplied=len(case_list), inspected=inspected,
                             retained=len(retained), visible_refusals=refusals,
                             controls_detected=sum(o.get('observed') == 'detected'
                                                   for o in observations),
                             faults=len(faults)))
    degraded = bool(limitations)
    limitations.append('verdict bounded to supplied cases/prefixes; no global theorem, '
                       'no reachability beyond inspected evidence, no scientific PASS')
    if not inspected:
        return finish('not_applicable')
    if faults:
        observations.extend(dict(kind='fault', **f) for f in faults)
        return finish('counterexample')
    if degraded:
        return finish('unproved')
    return finish('supported')
