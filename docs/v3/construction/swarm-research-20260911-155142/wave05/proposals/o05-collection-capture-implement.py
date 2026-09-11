"""Retained-certificate inspection for the collection/capture obligation.

Bounded executable re-inspection of already retained typed case objects produced
by the unchanged original checker ``c.run_history`` or restored through the
unchanged typed codec ``c.artifact.decode`` (check.py run_history/audit_case).
No reducer, guard, enumerator or fixture is executed and no boundary-01 helper
is imported; typed per-prefix states are restored (``c.t.restore``) and actual
fields are compared against the original capture contract.

Obligation: collect-open capture generation/revision/registration/attempts/log
length plus capture reset; the exact stale capture boundary.

Source anchors (unchanged originals):
  * capture five-tuple ``(source_generation, source_revision, registration,
    attempts, len(append_log))`` and ``collected=()`` reset on successful
    collect-open, else visible ``collect-open:no-registration`` refusal:
    s_inclusive.py:55-57, s_audit.py:81-83, guard_a.py:56-58, guard_b.py:61-65.
  * ``collect:<i>`` admits exactly ``0 <= i < min(collection[4],
    len(append_log))`` -- the bound is the CAPTURED log length -- inserts
    ``(i, append_log[i])`` sorted, else ``outside-captured-cut`` or
    ``duplicate-collection``: s_inclusive.py:58-62, s_audit.py:84-88;
    retained-ordinal invariant s_audit.py:24-25.
  * exact stale boundary: ``collection[:2] != (source_generation,
    source_revision)`` at the attestation pre-state yields
    ``source-attest:stale-collection``, after the ``no-captured-source`` guard;
    a committed attestation equals ``(capture[0], capture[1], cut_delivery)``:
    s_inclusive.py:63-69, s_audit.py:89-100, guard_a.py:64-71, guard_b.py:71-78.
    Adapter journal attestation commits only on Q acceptance: a_audit.py:25,
    a_inclusive.py:17-18, a_split.py:19-20.
  * adapter guard view overlays the journal on the Q core: a_domain.py:25-27.
  * ``collection``/``collected`` are written nowhere else in the unchanged
    sources, so every other action must leave the pair unchanged; later
    generation/revision drift is exactly what makes a capture stale.

Finite audit accounting: the caller-owned ``charge`` is debited with
``charge.take(1)`` exactly once BEFORE each inspected case prefix (prefix 0
included; every repetition across all supplied cases counts).  The result field
``audited_prefixes`` equals the number of debits actually performed.
Restoration of typed states is representation, not a new model execution.

Status semantics: ``counterexample`` when any falsifiable expected/observed
witness mismatches; ``supported`` only when every audited prefix passed and the
supplied cases contained at least one successful capture write and one
attestation-boundary evaluation; ``unproved`` for partial coverage or
uninspectable input; ``not_applicable`` when no collection-obligation action
occurs.  Bounded retained-evidence result only: no global theorem and no
accepted scientific PASS is asserted.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # one level deeper than boundary.py
CHECK = 'experiments/v3/eight-hour-research-20260910-01a08a22'
sys.path.insert(0, str(ROOT / CHECK))
import check as c

c.d.require(Path(c.__file__).resolve() == ROOT / CHECK / 'check.py',
            'frozen checker path binding')
exact, encode = c.d.exact, c.artifact.encode

FROZEN = ('registration', 'attempts', 'append_log', 'append_receipts',
          'append_reply', 'source_revision', 'source_generation',
          'attestation', 'staged_source', 'selected_source', 'cut_delivery')
OBS_CAP, BAD_CAP = 40, 25


def _capture_faults(s):
    """Well-formedness faults of one restored state's retained capture pair."""
    cap, got = s['collection'], s['collected']
    if not cap:
        return ['collected-nonempty-without-capture'] if got else []
    if type(cap) is not tuple or len(cap) != 5:
        return ['capture-not-five-tuple']
    faults = []
    if type(cap[1]) is not int or cap[1] < 0:
        faults.append('capture-revision-not-nonnegative-int')
    if type(cap[4]) is not int or not 0 <= cap[4] <= len(s['append_log']):
        faults.append('captured-log-length-out-of-range')
    if not s['registration'] or cap[2] != s['registration']:
        faults.append('capture-registration-mismatch')
    if type(cap[3]) is not tuple or cap[3] != tuple(s['attempts'][:len(cap[3])]):
        faults.append('capture-attempts-not-prefix')
    seen = set()
    for entry in got:
        if type(entry) is not tuple or len(entry) != 2 or type(entry[0]) is not int:
            faults.append('collected-entry-shape')
            continue
        index, raw = entry
        if index in seen or not 0 <= index < cap[4]:
            faults.append('collected-index-outside-captured-cut')
        elif index >= len(s['append_log']) or s['append_log'][index] != raw:
            faults.append('collected-bytes-not-log')
        seen.add(index)
    if all(type(e) is tuple and len(e) == 2 for e in got) and list(got) != sorted(got):
        faults.append('collected-not-sorted')
    return faults


def inspect_cases(cases, charge):
    """Inspect restored case prefixes; contract in the module docstring."""
    observations, limitations, mismatches = [], [], []
    audited, relevant, truncated = 0, False, False
    tally = dict(capture_write=0, capture_open_refused=0, collect_admit=0,
                 collect_refused=0, attest_boundary=0, attest_stale_refusal=0,
                 attest_no_capture=0, stale_prefixes=0, capture_drift=0,
                 frozen_capture_steps=0)

    def note(kind, **fields):
        if len(observations) < OBS_CAP:
            observations.append(dict(kind=kind, **fields))

    def bad(case, prefix, action, check_name, expected, observed):
        nonlocal truncated
        if len(mismatches) < BAD_CAP:
            mismatches.append(dict(case=case, prefix=prefix, action=action,
                                   check=check_name, expected=expected,
                                   observed=observed))
        else:
            truncated = True

    def frozen(case, i, action, side, pre, post, keys):
        for key in keys:
            if not exact(post[key], pre[key]):
                bad(case, i, action, side + '-capture-context-mutated:' + key,
                    encode(pre[key]), encode(post[key]))

    def collect_open(case, i, action, side, pre, post, decision):
        if pre['registration']:
            expected = (pre['source_generation'], pre['source_revision'],
                        pre['registration'], pre['attempts'],
                        len(pre['append_log']))
            if not exact(post['collection'], expected):
                bad(case, i, action, side + '-capture-write',
                    encode(expected), encode(post['collection']))
            if post['collected'] != ():
                bad(case, i, action, side + '-capture-reset', '()',
                    encode(post['collected']))
            if decision != 'collect-open:ok':
                bad(case, i, action, side + '-capture-decision',
                    'collect-open:ok', decision)
            else:
                tally['capture_write'] += 1
                note('capture-write', case=case, prefix=i, side=side,
                     captured_generation=encode(expected[0]),
                     captured_revision=expected[1],
                     captured_attempts=len(expected[3]),
                     captured_log_length=expected[4])
        else:
            if decision != 'collect-open:no-registration':
                bad(case, i, action, side + '-capture-refusal',
                    'collect-open:no-registration', decision)
            if not (exact(post['collection'], pre['collection'])
                    and exact(post['collected'], pre['collected'])):
                bad(case, i, action, side + '-refused-capture-mutated',
                    'unchanged capture pair',
                    [encode(post['collection']), encode(post['collected'])])
            tally['capture_open_refused'] += 1
        frozen(case, i, action, side, pre, post, FROZEN)

    def collect_item(case, i, action, side, pre, post, decision):
        base = action.split('@')[0]
        index = int(base.split(':')[1])
        cap = pre['collection']
        length = cap[4] if type(cap) is tuple and len(cap) == 5 else None
        inside = bool(cap) and length is not None and \
            0 <= index < min(length, len(pre['append_log']))
        if not inside:
            if decision != base + ':outside-captured-cut' or \
                    not exact(post['collected'], pre['collected']):
                bad(case, i, action, side + '-collect-outside-boundary',
                    base + ':outside-captured-cut with unchanged collected',
                    [decision, encode(post['collected'])])
            else:
                tally['collect_refused'] += 1
                note('collect-outside-captured-cut', case=case, prefix=i,
                     side=side, index=index, captured_length=length)
        elif any(type(e) is tuple and len(e) == 2 and e[0] == index
                 for e in pre['collected']):
            if decision != base + ':duplicate-collection' or \
                    not exact(post['collected'], pre['collected']):
                bad(case, i, action, side + '-collect-duplicate-boundary',
                    base + ':duplicate-collection with unchanged collected',
                    [decision, encode(post['collected'])])
            else:
                tally['collect_refused'] += 1
                note('collect-duplicate-refused', case=case, prefix=i,
                     side=side, index=index)
        else:
            expected = tuple(sorted(pre['collected']
                                    + ((index, pre['append_log'][index]),)))
            if decision != base + ':ok' or not exact(post['collected'], expected):
                bad(case, i, action, side + '-collect-admit',
                    [base + ':ok', encode(expected)],
                    [decision, encode(post['collected'])])
            else:
                tally['collect_admit'] += 1
                note('collect-admit', case=case, prefix=i, side=side,
                     index=index, collected_size=len(expected))
        frozen(case, i, action, side, pre, post, FROZEN + ('collection',))

    def attest(case, i, action, side, pre, post, decision):
        cap, cut = pre['collection'], pre['cut_delivery']
        stale = bool(cap) and len(cap) >= 2 and (
            cap[0] != pre['source_generation']
            or cap[1] != pre['source_revision'])
        if not cap or not cut:
            if decision != 'source-attest:no-captured-source':
                bad(case, i, action, side + '-attest-no-capture-boundary',
                    'source-attest:no-captured-source', decision)
            else:
                tally['attest_no_capture'] += 1
                note('attest-no-capture', case=case, prefix=i, side=side)
        elif stale:
            if decision != 'source-attest:stale-collection':
                bad(case, i, action, side + '-attest-stale-boundary',
                    'source-attest:stale-collection', decision)
            if not exact(post['attestation'], pre['attestation']):
                bad(case, i, action, side + '-stale-refusal-attestation-mutated',
                    encode(pre['attestation']), encode(post['attestation']))
            tally['attest_stale_refusal'] += 1
            tally['attest_boundary'] += 1
            note('attest-stale-refusal', case=case, prefix=i, side=side,
                 captured=encode(cap[:2]),
                 live=encode((pre['source_generation'], pre['source_revision'])))
        else:
            if decision in ('source-attest:no-captured-source',
                            'source-attest:stale-collection'):
                bad(case, i, action, side + '-attest-false-stale-refusal',
                    'fresh-capture attestation not refused stale', decision)
            if not exact(post['attestation'], pre['attestation']):
                expected_att = (cap[0], cap[1], cut)
                if not exact(post['attestation'], expected_att):
                    bad(case, i, action, side + '-attest-commit',
                        encode(expected_att), encode(post['attestation']))
                else:
                    note('attest-commit', case=case, prefix=i, side=side,
                         attestation=encode(expected_att))
            if side == 'source' and decision == 'source-attest:ok' and \
                    not exact(post['attestation'], (cap[0], cap[1], cut)):
                bad(case, i, action, 'source-attest-ok-attestation',
                    encode((cap[0], cap[1], cut)), encode(post['attestation']))
            tally['attest_boundary'] += 1
            note('attest-fresh-boundary', case=case, prefix=i, side=side,
                 observed_decision=decision)
        frozen(case, i, action, side, pre, post, ('collection', 'collected'))

    if not cases:
        return dict(status='not_applicable', observations=[],
                    limitations=['no retained case objects supplied'],
                    audited_prefixes=0)

    for position, case in enumerate(cases):
        try:
            name = case['case']
            ss = c.t.restore(case['source'])
            aa = c.t.restore(case['adapter'])
            actions = tuple(case['source']['actions'])
            rows = case['rows']
        except (KeyError, TypeError, IndexError, ValueError, AttributeError) as e:
            limitations.append('uninspectable case %d: %s' % (position, e))
            continue
        if not (len(ss) == len(aa) == len(actions) + 1
                and len(rows) == len(actions)):
            limitations.append('case %s prefix inventory mismatch' % name)
            continue
        for i in range(len(ss)):
            charge.take(1)
            audited += 1
            s_cur = ss[i]
            a_cur = dict(aa[i]['core'], **aa[i]['journal'])
            for side, st in (('source', s_cur), ('adapter', a_cur)):
                for fault in _capture_faults(st):
                    bad(name, i, actions[i - 1] if i else None,
                        side + '-capture-state-invariant', 'well-formed', fault)
                cap = st['collection']
                if cap and len(cap) >= 2 and (cap[0] != st['source_generation']
                                              or cap[1] != st['source_revision']):
                    tally['stale_prefixes'] += 1
            if not (exact(s_cur['collection'], a_cur['collection'])
                    and exact(s_cur['collected'], a_cur['collected'])):
                bad(name, i, actions[i - 1] if i else None,
                    'side-capture-agreement',
                    [encode(s_cur['collection']), encode(s_cur['collected'])],
                    [encode(a_cur['collection']), encode(a_cur['collected'])])
            if i == 0:
                if s_cur['collection'] != () or s_cur['collected'] != ():
                    bad(name, i, None, 'initial-capture', '((), ())',
                        [encode(s_cur['collection']), encode(s_cur['collected'])])
                continue
            action = actions[i - 1]
            verb = action.split('@')[0]
            if verb == 'collect-open' or verb.startswith('collect:') \
                    or verb == 'source-attest':
                relevant = True
            s_prev = ss[i - 1]
            a_prev = dict(aa[i - 1]['core'], **aa[i - 1]['journal'])
            for side, pre, post, dec in (
                    ('source', s_prev, s_cur, s_cur['decision']),
                    ('adapter', a_prev, a_cur, aa[i]['decision'])):
                if verb == 'collect-open':
                    collect_open(name, i, action, side, pre, post, dec)
                elif verb.startswith('collect:'):
                    collect_item(name, i, action, side, pre, post, dec)
                elif verb == 'source-attest':
                    attest(name, i, action, side, pre, post, dec)
                elif not (exact(post['collection'], pre['collection'])
                          and exact(post['collected'], pre['collected'])):
                    bad(name, i, action, side + '-capture-mutated-by-' + verb,
                        [encode(pre['collection']), encode(pre['collected'])],
                        [encode(post['collection']), encode(post['collected'])])
                else:
                    tally['frozen_capture_steps'] += 1
            if s_prev['collection'] and exact(s_cur['collection'],
                                             s_prev['collection']) and (
                    (s_cur['source_generation'], s_cur['source_revision'])
                    != (s_prev['source_generation'], s_prev['source_revision'])):
                tally['capture_drift'] += 1
                note('capture-stale-drift', case=name, prefix=i, action=action,
                     captured=encode(s_cur['collection'][:2]),
                     live=encode((s_cur['source_generation'],
                                  s_cur['source_revision'])))
            row = rows[i - 1]
            if isinstance(row, dict):
                so, ao = row.get('source_observation'), row.get('adapter_observation')
                if isinstance(so, dict) and so.get('decision') not in (
                        None, s_cur['decision']):
                    bad(name, i, action, 'source-retained-observation',
                        s_cur['decision'], so.get('decision'))
                if isinstance(ao, dict) and ao.get('decision') not in (
                        None, aa[i]['decision']):
                    bad(name, i, action, 'adapter-retained-observation',
                        aa[i]['decision'], ao.get('decision'))

    observations.append(dict(kind='finite-census', cases=len(cases),
                             audited_prefixes=audited, **tally))
    if mismatches:
        status = 'counterexample'
    elif not audited:
        status = 'unproved'
        limitations.append('no case could be restored and inspected')
    elif not relevant:
        status = 'not_applicable'
        limitations.append(
            'no collect-open/collect/source-attest action in inspected cases')
    elif tally['capture_write'] and tally['attest_boundary']:
        status = 'supported'
    else:
        status = 'unproved'
        limitations.append('partial coverage: capture_write=%d attest_boundary=%d'
                           % (tally['capture_write'], tally['attest_boundary']))
    if truncated:
        limitations.append('mismatch witness list truncated at %d' % BAD_CAP)
    limitations += (
        'bounded retained-evidence inspection; no reducer, guard or enumerator '
        'was executed and no new histories were created',
        'attestation inventory and registry outcomes are outside this '
        'obligation; only the no-capture/stale boundary and the attestation '
        'commit shape are asserted',
        'Q-delegated outcomes under a fresh capture are recorded as observed, '
        'not predicted',
        'mutant-injection branches of the original guards are not modeled',
        'supported is confined to the supplied restored cases; it is not a '
        'global theorem and not an accepted scientific PASS')
    return dict(status=status, observations=observations,
                limitations=limitations, audited_prefixes=audited)
