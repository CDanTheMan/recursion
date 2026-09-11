"""Adversarial retained-evidence check and controls for the staged_source obligation:
exact staged_source journal capture, persistence, source-restart staleness and the
current-source publication/reconcile guard; the relation gains no stage-freshness premise.
Anchors (unchanged originals used for representation only; no reducer executes here):
  experiments/v3/cut-source-overnight/s_inclusive.py + s_audit.py: stage sets
    staged_source=attestation; attestation=(collection[0],collection[1],cut); pub/reconcile
    deny 'source-boundary-stale' when attestation/staged_source is stale or absent.
  experiments/v3/cut-source-overnight/batch-06/a_inclusive.py + a_audit.py: adapter journal
    performs the same captures; source-restart bumps only the journal source_generation.
  experiments/v3/cut-source-overnight/batch-05/semantic.py: typed/exact representation.
  validation-contract.json relation_non_narrowing: no current-stage freshness premise.
Accounting: charge.take(1) precedes every inspected prefix including repeats; replay only
re-applies retained hash-bound patches. Mutations on unhashed rows/prefixes/pairs are
semantic controls; the trace-patch mutation is integrity-binding; shapes absent from the
supplied cases report missing-witness, never detection."""
import copy
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel
d, exact, enc, require = rel.s, rel.exact, rel.typed, rel.require
PUB = ('pub-commit', 'pub-rival', 'pub-retry', 'pub-retry-conflict', 'pub-retry-foreign')
JF = tuple(d.EXTRA) + ('source_generation',)
REFUSALS = ('no-captured-source', 'stale-collection', 'incomplete-inventory', 'incomplete-registry')
RULES = ('strict', 'original-object-identity', 'unrelated')
GEN = lambda n: ('cut-source', 'collectorA', 'effectA', n)


class _Exhausted(Exception):
    pass


def replay(trace):
    states = [copy.deepcopy(trace['initial'])]
    require(len(trace['events']) == len(trace['actions']), 'complete retained event inventory')
    for action, event in zip(trace['actions'], trace['events']):
        require(event['action'] == action and rel.digest(states[-1]) == event['before_sha256'],
                'retained prestate binding')
        current = copy.deepcopy(states[-1])
        for key, value in event['patch'].items():
            if trace['side'] == 'adapter' and key in ('core', 'journal'):
                current[key].update(copy.deepcopy(value))
            else:
                current[key] = copy.deepcopy(value)
        require(rel.digest(current) == event['after_sha256'], 'retained poststate binding')
        states.append(current)
    return states


def expected(journal, core, verb):
    if verb == 'reconcile':
        sel = journal['selected_source']
        fresh = bool(sel) and sel[:2] == (journal['source_generation'], journal['source_revision'])
    else:
        att = journal['attestation']
        fresh = bool(att) and att[:2] == (journal['source_generation'], journal['source_revision']) \
            and journal['staged_source'] == att
        if (core['staged'] or core['publication_receipts']) and \
           d.q.incoming(dict(core, **journal), verb)[0].request in \
           {row[0].request for row in core['publication_receipts']}:
            return 'delegated'
    return 'delegated' if fresh else 'source-boundary-stale'


def prefix_check(item, case, ss, aa, i, flag, obs):
    if item.get('staged_rule') not in RULES:
        flag(i, 'staged-rule-domain', observed=enc(item.get('staged_rule')))
    if item.get('incarnation_pair_established_by_identity'):
        flag(i, 'identity-created-authority')
    proof = item.get('identity_proof')
    if not proof:
        return
    obs['identity_proofs'] += 1
    for side, states in (('source', ss), ('adapter', aa)):
        origin = proof.get(side + '_origin', {})
        e = origin.get('event_index')
        if not (type(e) is int and 0 <= e < i
                and case[side]['events'][e]['action'] == origin.get('action')
                and origin.get('before_sha256') == rel.digest(states[e])
                and origin.get('after_sha256') == rel.digest(states[e + 1])):
            flag(i, side + '-origin-binding', observed=enc(origin))
    staged = ss[i]['staged']
    if staged and staged[0].source_generation != ss[i]['source_generation']:
        obs['stale_staged_identity'] += 1


def inspect_case(case, charge, obs, bad):
    ss, aa = replay(case['source']), replay(case['adapter'])
    n = len(ss)
    require(len(aa) == n and len(case['rows']) == n - 1, 'matched retained history shape')
    px = case.get('prefixes')
    if px is not None:
        require(len(px) == n, 'complete prefix certificate inventory')
    exp, restarts = {'staged_source': (), 'selected_source': ()}, 0
    flag = lambda i, chk, **kw: bad.append(dict(prefix=i, check=chk, **kw))
    for i in range(n):
        try:
            charge.take(1)
        except Exception:
            raise _Exhausted()
        s, a, j = ss[i], aa[i], aa[i]['journal']
        diff = [k for k in JF if not exact(s[k], j[k])]
        for key in exp:
            if not exact(j[key], exp[key]) or not exact(s[key], exp[key]):
                flag(i, key + '-capture', expected=enc(exp[key]), observed=enc(j[key]))
        if s['source_generation'] != GEN(restarts) or j['source_generation'] != GEN(restarts):
            flag(i, 'restart-generation', expected=enc(GEN(restarts)), observed=enc(j['source_generation']))
        if px is not None and px[i].get('differing_journal_fields') != diff:
            flag(i, 'prefix-journal-diff', expected=diff, observed=px[i].get('differing_journal_fields'))
        if i:
            verb = case['source']['actions'][i - 1].split('@')[0]
            row, pj, pc = case['rows'][i - 1], aa[i - 1]['journal'], aa[i - 1]['core']
            invoked = len(a['invocations']) > len(aa[i - 1]['invocations'])
            if row.get('differing_journal_fields') != diff:
                flag(i, 'journal-diff', expected=diff, observed=row.get('differing_journal_fields'))
            if bool(row.get('q_invoked')) != invoked:
                flag(i, 'q-invocation-mask', expected=invoked, observed=row.get('q_invoked'))
            if row['source_observation']['decision'] != s['decision'] or \
               row['adapter_observation']['decision'] != a['decision']:
                flag(i, 'decision-binding', observed=enc((s['decision'], a['decision'])))
            if verb in PUB or verb == 'reconcile':
                want = expected(pj, pc, verb)
                obs['stale_refusals' if want == 'source-boundary-stale' else 'guard_delegated'] += 1
                obs['post_restart_stale'] += want == 'source-boundary-stale' and restarts > 0
                if want == 'delegated':
                    if not invoked:
                        flag(i, 'delegated-call-not-invoked')
                elif s['decision'] != verb + ':' + want or a['decision'] != s['decision'] \
                        or invoked or not exact(a['core'], pc):
                    flag(i, 'stale-guard', expected=verb + ':' + want,
                         observed=enc((s['decision'], a['decision'], invoked)))
            if verb == 'source-attest' and not invoked and \
               (a['decision'].rsplit(':', 1)[-1] not in REFUSALS
                or not exact(j['attestation'], pj['attestation']) or not exact(a['core'], pc)):
                flag(i, 'attest-refusal-shape', observed=enc(a['decision']))
            if not (verb == 'source-attest' and s['decision'] == 'source-attest:ok') and \
               not exact(j['attestation'], pj['attestation']):
                flag(i, 'attestation-persistence')
            if px is not None:
                prefix_check(px[i], case, ss, aa, i, flag, obs)
        if i < n - 1:
            verb = case['source']['actions'][i].split('@')[0]
            nx, okd = aa[i + 1], aa[i + 1]['decision']
            if verb == 'source-restart':
                restarts += 1
                obs['restarts'] += 1
            if verb.startswith('stage') and okd == verb + ':ok':
                exp['staged_source'] = j['attestation']
                obs['stage_ok'] += 1
            if nx['core']['publication_revision'] > a['core']['publication_revision']:
                exp['selected_source'] = j['staged_source']
            if verb == 'source-attest' and okd == 'source-attest:ok':
                want = (j['collection'][0], j['collection'][1], a['core']['cut_delivery'])
                if not exact(nx['journal']['attestation'], want) or not exact(ss[i + 1]['attestation'], want):
                    flag(i + 1, 'attestation-capture', expected=enc(want),
                         observed=enc(nx['journal']['attestation']))
                obs['attest_ok'] += 1
    for pair in case.get('incarnation_pairs', []):
        obs['pairs'] += 1
        se, te = pair.get('source_event'), pair.get('target_event')
        verb = case['source']['actions'][se].split('@')[0] if type(se) is int and 0 <= se < n - 1 else '?'
        want = 'source-restart' if pair.get('reason') == 'paired-restart' else 'source-attest'
        if not (verb == want and exact(ss[se + 1]['source_generation'], pair.get('source'))
                and type(te) is int and 0 <= te < n - 1
                and exact(aa[te + 1]['core']['source_generation'], pair.get('target'))):
            flag(se, 'incarnation-binding', observed=enc(pair))
    return n


def inspect_cases(cases, charge):
    obs = dict(stage_ok=0, attest_ok=0, restarts=0, stale_refusals=0, guard_delegated=0,
               post_restart_stale=0, identity_proofs=0, stale_staged_identity=0, pairs=0, cases=0)
    bad, limits, total = [], [], 0
    if not cases:
        return dict(status='not_applicable', observations=[], limitations=['no cases supplied'],
                    audited_prefixes=0)
    for case in cases:
        try:
            total += inspect_case(case, charge, obs, bad)
            obs['cases'] += 1
        except _Exhausted:
            limits.append('charge exhausted before all prefixes inspected')
            break
        except (ValueError, KeyError, IndexError, TypeError) as error:
            bad.append(dict(prefix=None, check='retained-evidence', observed=repr(error)[:160]))
    if not all(type(c.get('prefixes')) is list for c in cases):
        limits.append('retained prefix certificates absent; freshness-premise evidence uninspected')
    missing = [label for label, key in (('stage capture', 'stage_ok'), ('attestation capture', 'attest_ok'),
                                        ('source restart', 'restarts'),
                                        ('stale-source guard refusal', 'stale_refusals')) if not obs[key]]
    limits += ['no reachable witness: ' + m for m in missing]
    status = 'counterexample' if bad else 'unproved' if (missing or limits) else 'supported'
    return dict(status=status, observations=[dict(counterexamples=len(bad), **obs)] + bad[:8],
                limitations=limits, audited_prefixes=total)


def run_controls(cases, inspect_cases, charge):
    controls = []

    def locate(pred):
        for case in cases:
            for i in range(1, len(case.get('rows') or ()) + 1):
                if pred(case, i):
                    return case, i
        return None, None

    def attempt(name, pred, mutate, kind):
        case, i = locate(pred)
        if case is None:
            controls.append(dict(control=name, kind=kind, detected=None, status='missing-witness',
                                 note='control needs a genuinely reachable witness; none supplied'))
            return
        mutant = copy.deepcopy(case)
        mutate(mutant, i)
        res = inspect_cases([mutant], charge)
        controls.append(dict(control=name, kind=kind, case=mutant.get('case'), prefix=i,
                             detected=res['status'] == 'counterexample',
                             observed_status=res['status'], evidence=res['observations'][1:3]))

    def proved(case, i):
        p = case.get('prefixes')
        return bool(p and i < len(p) and p[i].get('identity_proof'))

    attempt('prefix-certificate-dropped', lambda c, i: c.get('prefixes'),
            lambda c, i: c['prefixes'].pop(), 'semantic')
    attempt('journal-diff-falsified', lambda c, i: True,
            lambda c, i: c['rows'][i - 1].update(differing_journal_fields=
                list(c['rows'][i - 1].get('differing_journal_fields') or []) + ['staged_source']),
            'semantic')
    attempt('q-invocation-on-source-handled-call', lambda c, i: not c['rows'][i - 1].get('q_invoked'),
            lambda c, i: c['rows'][i - 1].update(q_invoked=True), 'semantic')
    attempt('stale-refusal-relabelled-ok',
            lambda c, i: c['rows'][i - 1]['source_observation']['decision'].endswith('source-boundary-stale'),
            lambda c, i: c['rows'][i - 1]['source_observation'].update(
                decision=c['source']['actions'][i - 1].split('@')[0] + ':ok'), 'semantic')
    attempt('identity-origin-event-shifted', proved,
            lambda c, i: c['prefixes'][i]['identity_proof']['source_origin'].update(event_index=i),
            'semantic')
    attempt('causal-pair-event-shifted', lambda c, i: i == 1 and bool(c.get('incarnation_pairs')),
            lambda c, i: c['incarnation_pairs'][0].update(
                source_event=0 if c['incarnation_pairs'][0]['source_event'] else 1), 'semantic')
    attempt('freshness-premise-smuggled', lambda c, i: bool(c.get('prefixes')),
            lambda c, i: c['prefixes'][i].update(staged_rule='current-stage-required'), 'semantic')
    attempt('journal-patch-rewritten', lambda c, i: True,
            lambda c, i: c['adapter']['events'][i - 1]['patch'].setdefault('journal', {}).update(
                staged_source=('forged',)), 'integrity-binding')
    return dict(controls=controls)
