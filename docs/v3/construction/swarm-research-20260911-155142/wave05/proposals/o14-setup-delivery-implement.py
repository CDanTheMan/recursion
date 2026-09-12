"""Retained-certificate check, obligation o14-setup-delivery (boundary-01).

Claim under audit: the fixed original scale setup (positions @0-@10) and
delivery (@19-@20) establish source-projection/Q-core coupling in the batch-06
adapter even though outer adapter and inner Q-core completion masks differ;
every hypothesis below is enumerated and checked against retained evidence
only, with no assumed success and no global theorem or scientific PASS.

Finite audit accounting: inspect_cases calls charge.take(1) exactly once
BEFORE inspecting each case prefix (one unit per entry of
case['prefixes']; repeated or shared case objects are recharged).
audited_prefixes returns the total charged units actually taken.

No reducer, guard, boundary or trace-restoration helper is imported or
executed; only retained fields of typed c.run_history/c.artifact-restored
case objects are read. Witnesses keep falsifiable expected/observed pairs.

Source anchors (unchanged originals, representation only):
- docs/.../boundary-01/spec.json: fixed_prefix_length=11, core_length=8,
  fixed_suffix_start=19, subclasses fresh-incomplete/stale-complete.
- s_domain.py: q.SETUP, setup(), collect(), add_with_suffix scale profile.
- q_domain.py: deliver(), reader(), source_token(), EXTRA/DEFAULTS.
- a_domain.py: initial(), view() journal overlay, source_only(), subprofile().
- a_audit.py: invocations inventory; core['done'] == sum over actual calls.
- guard_a.py/guard_b.py/s_inclusive.py/s_split.py/s_audit.py: local refusals
  (stale-collection, incomplete-inventory, incomplete-registry,
  source-boundary-stale) never invoke Q; delegated calls always do.
- check.py run_history()/audit_case(): retained rows/prefixes field shapes.
- semantic.py: typed()/exact() representation, advance()/bind() pair reasons.
"""

SETUP = ('admitA', 'intent', 'send', 'remote', 'lose', 'query',
         'register:success', 'attempt:1', 'append:success:1:normal',
         'append:success:2:normal', 'append:success:3:normal')
CORE = frozenset(('collect-open', 'collect:0', 'collect:1', 'collect:2',
                  'attempt:2', 'attempt:3', 'attempt:4', 'source-restart'))
DELIVERY = ('cut:success', 'cut-deliver')
SUFFIX = ('source-attest', 'stage', 'pub-commit', 'reader-request:0',
          'reader-pin:0', 'reader-copy:0', 'reader-wait:0', 'reader-release:0',
          'reader-install:0', 'join-cut', 'classify', 'reconcile', 'admitB')
DEPTH = 34
TOKEN0 = ('cut-source', 'collectorA', 'effectA', 0)
PUBS = frozenset(('pub-commit', 'pub-rival', 'pub-retry',
                  'pub-retry-conflict', 'pub-retry-foreign'))
ATTEST_LOCAL = frozenset(('no-captured-source', 'stale-collection',
                          'incomplete-inventory', 'incomplete-registry'))
BOUNDARY_LOCAL = frozenset(('source-boundary-stale',))
JOURNAL_DEFAULTS = dict(registration='', attempts=(), append_log=(),
    append_receipts=(), append_reply=(), source_revision=0, collection=(),
    collected=(), attestation=(), staged_source=(), selected_source=())
PAIR_REASON = {'source-restart': 'paired-restart',
               'source-attest': 'paired-successful-attestation'}

HYPOTHESES = (
    ('H1-frame', 'schedule == fixed setup x permuted core@11-18 x fixed '
                 'suffix with delivery @19-20'),
    ('H2-initial', 'prefix0 generations all TOKEN0, zero masks, empty '
                   'invocations, default journal fields'),
    ('H3-literal-response', 'each row pairs identical source/adapter action '
                            'at its chronological index with equal decisions'),
    ('H4-invocation-mask', 'q_invoked == delegated-and-not-locally-refused '
                           'per row; setup = 6 delegated then 5 source-only; '
                           'delivery both delegated'),
    ('H5-field-coupling', 'state_related/prestate_related hold on all rows; '
                          'differing_journal_fields empty on all prefixes'),
    ('H6-mask-divergence', 'outer done mask exceeds Q-core mask once '
                           'source-only steps execute (2047 vs 63 at '
                           'prefix 11)'),
    ('H7-refusal-visibility', 'local guard refusals keep identical visible '
                             'decisions and never invoke Q'),
    ('H8-pair-ledger', 'incarnation_pairs entries carry matching events, '
                      'reason-verb agreement and equal incarnation serials'),
)


def _verb(a):
    return a.partition('@')[0] if isinstance(a, str) else ''


def _pos(a):
    try:
        return int(a.rpartition('@')[2])
    except (TypeError, ValueError):
        return -1


def _reason(d):
    return d.rsplit(':', 1)[-1] if isinstance(d, str) else None


def _source_only(k):
    return (k.startswith(('register:', 'attempt:', 'atomic:', 'append:',
                          'collect:', 'source:'))
            or k in ('append-lose-reply', 'collect-open'))


def _expect_invoked(k, decision):
    if _source_only(k):
        return False
    r = _reason(decision)
    if r is None:
        return None
    if k == 'source-attest':
        return r not in ATTEST_LOCAL
    if k in PUBS or k == 'reconcile':
        return r not in BOUNDARY_LOCAL
    return True


def _js(x, depth=0):
    if depth > 8 or x is None or isinstance(x, (bool, int, float, str)):
        return x
    if isinstance(x, dict):
        return {str(k): _js(v, depth + 1) for k, v in
                sorted(x.items(), key=lambda kv: str(kv[0]))}
    if isinstance(x, (list, tuple)):
        return [_js(v, depth + 1) for v in x]
    if isinstance(x, (set, frozenset)):
        return sorted((_js(v, depth + 1) for v in x), key=repr)
    if getattr(x, '_fields', None) is not None:
        return {'namedtuple': type(x).__name__, 'values': _js(list(x), depth + 1)}
    return repr(x)


def _frame(actions):
    if len(actions) != DEPTH:
        return False
    fixed = dict(enumerate(SETUP))
    fixed.update(enumerate(DELIVERY, 19))
    fixed.update(enumerate(SUFFIX, 21))
    if any(actions[i] != v + '@' + str(i) for i, v in fixed.items()):
        return False
    mid = actions[11:19]
    return (sorted(_pos(a) for a in mid) == list(range(11, 19))
            and {_verb(a) for a in mid} == CORE)


def _miss(missing, where, label):
    missing.append([where, label])


def _field(dic, key, exp, bad, missing, where, label, gated):
    if not isinstance(dic, dict) or key not in dic:
        _miss(missing, where, label)
    elif _js(dic[key]) != _js(exp) and gated:
        bad.append([label, where, _js(exp), _js(dic[key])])


def inspect_cases(cases, charge):
    """Audit retained case objects; see module docstring for accounting."""
    observations = [{'kind': 'hypothesis', 'id': h, 'statement': s}
                    for h, s in HYPOTHESES]
    limitations = [
        'per-prefix restored states are not rebuilt (no trace-restore import); '
        'core done/generation integers are derived from retained q_invoked '
        'and q_profile fields, not re-read from state objects',
        'retained relation flags are checked for consistency against expected '
        'masks; the underlying reducers are not re-executed',
        'result is bounded retained-certificate evidence only; it is not the '
        'inherited 87-command gate and not scientific acceptance',
    ]
    audited = 0
    usable = applicable = clean = 0
    counter = False
    partial = False
    for ci, case in enumerate(cases or []):
        if not isinstance(case, dict):
            partial = True
            limitations.append('case %d is not a dict' % ci)
            continue
        src, adp = case.get('source'), case.get('adapter')
        if not isinstance(src, dict) or not isinstance(adp, dict):
            partial = True
            limitations.append('case %s lacks source/adapter sides' % ci)
            continue
        usable += 1
        actions = list(src.get('actions') or ())
        rows = list(case.get('rows') or ())
        prefs = list(case.get('prefixes') or ())
        pairs = list(case.get('incarnation_pairs') or ())
        qacts = tuple(((adp.get('q_profile') or {}).get('actions')) or ())
        derived_q = tuple(a for a in actions if not _source_only(_verb(a)))
        qpos = {a: i for i, a in enumerate(derived_q)}
        name = case.get('case')
        frame = _frame(actions)
        note = 'q_profile differs from derived subprofile' if \
            (qacts and derived_q != qacts) else None
        bad, missing, invoked, refusals, binds = [], [], [], [], []
        witness = {'deliveries': [], 'attestation': None, 'restart': None}
        strict_gaps = []
        for i in range(len(prefs)):
            charge.take(1)
            audited += 1
            item = prefs[i] if isinstance(prefs[i], dict) else {}
            if item.get('strict_related') is not True:
                strict_gaps.append(i)
            if 'differing_journal_fields' not in item:
                _miss(missing, 'prefix%d' % i, 'differing_journal_fields')
            elif item['differing_journal_fields'] != [] and frame:
                bad.append(['H5', 'prefix%d' % i, [],
                            _js(item['differing_journal_fields'])])
            if i == 0:
                si, ai = src.get('initial'), adp.get('initial')
                jour = (ai or {}).get('journal')
                core = (ai or {}).get('core')
                _field(si, 'source_generation', TOKEN0, bad, missing, 'p0',
                       'H2-source-generation', frame)
                _field(jour, 'source_generation', TOKEN0, bad, missing, 'p0',
                       'H2-journal-generation', frame)
                _field(core, 'source_generation', TOKEN0, bad, missing, 'p0',
                       'H2-core-generation', frame)
                _field(si, 'done', 0, bad, missing, 'p0', 'H2-src-done', frame)
                _field(ai, 'done', 0, bad, missing, 'p0', 'H2-ad-done', frame)
                _field(core, 'done', 0, bad, missing, 'p0', 'H2-core-done', frame)
                _field(ai, 'invocations', (), bad, missing, 'p0',
                       'H2-invocations', frame)
                for key, exp in JOURNAL_DEFAULTS.items():
                    _field(jour, key, exp, bad, missing, 'p0',
                           'H2-journal-' + key, frame)
                continue
            row = rows[i - 1] if i - 1 < len(rows) else None
            if not isinstance(row, dict):
                _miss(missing, 'row%d' % (i - 1), 'row')
                continue
            act = actions[i - 1] if i - 1 < len(actions) else None
            sa, aa = row.get('source_action'), row.get('adapter_action')
            idx = row.get('index')
            if sa is None or aa is None:
                _miss(missing, 'row%d' % (i - 1), 'actions')
            elif (sa != aa or sa != act) and frame:
                bad.append(['H3', 'row%d' % (i - 1), _js(act), _js([sa, aa])])
            if idx is not None and idx != i - 1 and frame:
                bad.append(['H3-index', 'row%d' % (i - 1), i - 1, idx])
            sob, aob = row.get('source_observation'), row.get('adapter_observation')
            sdec = sob.get('decision') if isinstance(sob, dict) else None
            adec = aob.get('decision') if isinstance(aob, dict) else None
            if sdec is None or adec is None:
                _miss(missing, 'row%d' % (i - 1), 'decision')
            elif sdec != adec and frame:
                bad.append(['H3-decision', 'row%d' % (i - 1), _js(sdec),
                            _js(adec)])
            k = _verb(act if isinstance(act, str) else sa)
            qi = row.get('q_invoked')
            exp_inv = _expect_invoked(k, adec)
            if qi is None or exp_inv is None:
                _miss(missing, 'row%d' % (i - 1), 'q_invoked')
            else:
                invoked.append((act, bool(qi)))
                if bool(qi) != exp_inv and frame:
                    bad.append(['H4', 'row%d' % (i - 1), exp_inv, bool(qi)])
            for key in ('responses_related', 'state_related', 'prestate_related'):
                if key not in row:
                    _miss(missing, 'row%d' % (i - 1), key)
                elif row[key] is not True and frame:
                    bad.append(['H5-' + key, 'row%d' % (i - 1), True, row[key]])
            if 'differing_fields' in row and row['differing_fields'] != [] \
                    and frame:
                bad.append(['H5-fields', 'row%d' % (i - 1), [],
                            _js(row['differing_fields'])])
            b = row.get('binding')
            if b is not None:
                binds.append(b)
                if b == 'binding-conflict' and frame:
                    bad.append(['H8', 'row%d' % (i - 1), 'no-conflict', b])
            if isinstance(adec, str) and _reason(adec) != 'ok':
                refusals.append({'index': i - 1, 'action': act,
                                 'decision': adec, 'q_invoked': qi})
            if i - 1 in (19, 20):
                witness['deliveries'].append({
                    'index': i - 1, 'action': act, 'expected_invoked': True,
                    'observed_invoked': qi, 'source_decision': sdec,
                    'adapter_decision': adec,
                    'responses_related': row.get('responses_related')})
            if k == 'source-attest':
                witness['attestation'] = {'index': i - 1, 'decision': adec,
                                          'q_invoked': qi, 'binding': b}
            if k == 'source-restart':
                witness['restart'] = {'index': i - 1, 'decision': adec,
                                      'q_invoked': qi, 'binding': b}
            if i == len(prefs) - 1:
                for p in pairs:
                    if not isinstance(p, dict):
                        _miss(missing, 'pairs', 'pair')
                        continue
                    se, te = p.get('source_event'), p.get('target_event')
                    if se != te or not isinstance(se, int) or \
                            not (0 <= se < len(actions)):
                        if frame:
                            bad.append(['H8-event', 'pairs',
                                        'shared-valid-index', _js([se, te])])
                        continue
                    want = PAIR_REASON.get(_verb(actions[se]))
                    if p.get('reason') != want and frame:
                        bad.append(['H8-reason', 'event%d' % se, want,
                                    _js(p.get('reason'))])
                    if _js(p.get('source')) != _js(p.get('target')) and frame:
                        bad.append(['H8-serial', 'event%d' % se,
                                    _js(p.get('source')), _js(p.get('target'))])
        done11 = sum(1 << _pos(actions[j]) for j in range(min(11, len(actions))))
        core11 = sum(1 << qpos[a] for a, ok in invoked[:11] if ok and a in qpos)
        done21 = sum(1 << _pos(actions[j]) for j in range(min(21, len(actions))))
        core21 = sum(1 << qpos[a] for a, ok in invoked[:21] if ok and a in qpos)
        if frame:
            applicable += 1
        verdict = ('not-applicable' if not frame else
                   'counterexample' if bad else 'partial' if missing else 'clean')
        if verdict == 'counterexample':
            counter = True
        elif verdict == 'partial':
            partial = True
        elif verdict == 'clean':
            clean += 1
        observations.append({
            'kind': 'case', 'case': name, 'unit': case.get('unit'),
            'outcome': case.get('outcome'), 'applicable': frame,
            'verdict': verdict, 'prefixes_audited': len(prefs),
            'frame_note': note, 'strict_gaps': strict_gaps,
            'setup_invoked_observed': [ok for _, ok in invoked[:11]],
            'setup_invoked_expected': [j < 6 for j in range(len(invoked[:11]))],
            'outer_done_expected_at_11': done11,
            'core_done_derived_at_11': core11,
            'outer_done_expected_at_21': done21,
            'core_done_derived_at_21': core21,
            'deliveries': _js(witness['deliveries']),
            'attestation': _js(witness['attestation']),
            'restart': _js(witness['restart']),
            'refusals': _js(refusals[:8]), 'bindings': sorted(set(binds)),
            'incarnation_pairs': len(pairs),
            'mismatches': _js(bad[:12]), 'missing': _js(missing[:12])})
    if counter:
        status = 'counterexample'
    elif usable == 0:
        status = 'unproved'
        limitations.append('no usable typed case objects supplied')
    elif applicable == 0:
        status = 'not_applicable'
    elif partial or clean != applicable:
        status = 'unproved'
    else:
        status = 'supported'
    return {'status': status, 'observations': _js(observations),
            'limitations': limitations, 'audited_prefixes': audited}
