"""Bounded retained-certificate check: typed full-state restoration from patches.

For each supplied case (a typed object produced by the original run_history /
artifact decode path) this re-walks the retained `source` and `adapter` traces:
the typed `initial` state plus one patch event per literal action. Per prefix it
verifies field inventory, tuple-vs-list types, done and Q-invocation masks, the
sha256 before/after chain, patch minimality, chronological action/dependency
binding, and agreement with any retained comparison rows and prefix
certificates. No reducer, guard or original audit function is executed; only
the unchanged semantic representation (typed/exact/digest) is reused.

Anchors (unchanged originals, representation only): adapter_traces.py:54-75
trace_event/restore patch shape and hash chain; a_audit.py:11-16,39-44 frame and
journal inventories, source-only literal class, independent Q subprofile and
core-done mask; a_domain.py:8-10,20-23 adapter frame and journal defaults;
semantic.py:12-16 typed()/exact() keep type tags while digest() is sha256 over
canonical JSON where tuple and list collide; s_domain.py:10-15 EXTRA fields and
literal defaults; check.py audit_case rows/prefixes; artifact.py + q_artifact.py
typed tag decode preserving tuple/list/Envelope.

Finite audit accounting: charge.take(1) is called once before each (case, side,
prefix) state inspection, prefix 0 included; every repetition is charged again.
A case with E events consumes exactly 2*(E+1) charge units.

Status: 'counterexample' on any falsifiable expected/observed mismatch found on
the retained evidence; 'supported' only when every supplied case was fully
inspected without mismatch; 'unproved' when some case or trace could not be
completely inspected; 'not_applicable' when nothing inspectable was supplied.
'supported' is certificate-internal consistency on the supplied cases only: not
a global theorem and not a scientific PASS.
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel

exact, typed, digest = rel.exact, rel.typed, rel.digest
SOURCE_KEYS = frozenset(rel.s.AUTH + rel.s.FLOW + rel.s.VIEW)
CORE_KEYS = frozenset(rel.q.AUTH + rel.q.FLOW + rel.q.VIEW)
JOURNAL_KEYS = frozenset(rel.s.EXTRA) | {'source_generation'}
ADAPTER_KEYS = frozenset(('core', 'journal', 'done', 'decision', 'invocations'))
EVENT_KEYS = frozenset(('action', 'before_sha256', 'after_sha256', 'patch'))
TOKEN_HEAD = ('cut-source', 'collectorA', 'effectA')
HANDLED = ('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:')
LITERAL = frozenset(('append-lose-reply', 'collect-open'))
TUPLES = ('attempts', 'append_log', 'append_receipts', 'append_reply', 'collection',
          'collected', 'attestation', 'staged_source', 'selected_source')
CORE_TUPLES = ('staged', 'selected', 'publication_receipts', 'publication_reply', 'bindings')
DEFAULTS = dict(registration='', attempts=(), append_log=(), append_receipts=(), append_reply=(),
                source_revision=0, collection=(), collected=(), attestation=(), staged_source=(),
                selected_source=())


def _handled(action):
    k = action.split('@')[0]
    return k.startswith(HANDLED) or k in LITERAL


def _token(x):
    return type(x) is tuple and len(x) == 4 and x[:3] == TOKEN_HEAD and type(x[3]) is int and x[3] >= 0


def _wit(v):
    out = {'type': type(v).__name__}
    try:
        out['sha256'] = digest(v)
    except Exception:
        pass
    try:
        text = json.dumps(v, sort_keys=True)
    except (TypeError, ValueError):
        return out
    if len(text) <= 240:
        out['value'] = json.loads(text)
    return out


def _fields(state, side):
    """Expected/observed inventory and type problems of one restored state."""
    out = []
    if not isinstance(state, dict):
        return [('state-type', 'dict', type(state).__name__)]
    want = SOURCE_KEYS if side == 'source' else ADAPTER_KEYS
    if set(state) != want:
        out.append(('field-inventory', sorted(want), sorted(state)))
    for f, t in (('done', int), ('decision', str)):
        if type(state.get(f)) is not t:
            out.append((f + '-type', t.__name__, type(state.get(f)).__name__))
    journal = state if side == 'source' else state.get('journal')
    core = state if side == 'source' else state.get('core')
    if isinstance(journal, dict):
        if side == 'adapter' and set(journal) != JOURNAL_KEYS:
            out.append(('journal-inventory', sorted(JOURNAL_KEYS), sorted(journal)))
        for f in TUPLES:
            if type(journal.get(f)) is not tuple:
                out.append(('tuple-field-' + f, 'tuple', type(journal.get(f)).__name__))
        if not _token(journal.get('source_generation')):
            out.append(('incarnation-token', 'typed 4-token', journal.get('source_generation')))
    if isinstance(core, dict):
        if side == 'adapter' and set(core) != CORE_KEYS:
            out.append(('core-inventory', sorted(CORE_KEYS), sorted(core)))
        for f in CORE_TUPLES + ('source_generation',):
            if type(core.get(f)) is list:
                out.append(('tuple-to-list-' + f, 'tuple', 'list'))
        if 'source_generation' in core and not _token(core['source_generation']):
            out.append(('core-incarnation-token', 'typed 4-token', core['source_generation']))
        if type(core.get('done')) is not int:
            out.append(('core-done-type', 'int', type(core.get('done')).__name__))
    return out


def _apply(state, patch, side, report):
    """Replay one retained patch under original per-side semantics."""
    if not isinstance(patch, dict):
        report('patch-type', 'dict', type(patch).__name__)
        return state
    nxt = copy.deepcopy(state)
    allowed = ADAPTER_KEYS if side == 'adapter' else SOURCE_KEYS
    for k, v in patch.items():
        if k not in allowed or k not in state:
            report('patch-field-inventory', 'declared state field', k)
            continue
        if side == 'adapter' and k in ('core', 'journal'):
            if not isinstance(v, dict) or not isinstance(state[k], dict):
                report('subpatch-type', 'dict over dict', type(v).__name__)
                continue
            inner = CORE_KEYS if k == 'core' else JOURNAL_KEYS
            for f, fv in v.items():
                if f not in inner or f not in state[k]:
                    report('patch-subfield-inventory', 'declared ' + k + ' field', f)
                elif exact(fv, state[k][f]):
                    report('non-differing-patch-entry', 'changed ' + k + '.' + f, fv)
            merged = dict(state[k])
            merged.update(v)
            nxt[k] = merged
        elif exact(v, state[k]):
            report('non-differing-patch-entry', 'changed ' + k, v)
        else:
            nxt[k] = v
    return nxt


def _trace(name, side, tr, case, charge, note, audited):
    """Replay one retained trace; False when it cannot be fully walked."""
    def report(check, expected, observed, prefix=None):
        note(name, side, prefix, check, expected, observed)
    events, actions = tr.get('events'), tr.get('actions')
    profile = tr.get('profile') if isinstance(tr.get('profile'), dict) else {}
    requires = profile.get('requires') if isinstance(profile.get('requires'), dict) else {}
    rows = case.get('rows') if isinstance(case.get('rows'), list) else None
    prefixes = case.get('prefixes') if isinstance(case.get('prefixes'), list) else None
    if tr.get('side') != side:
        report('side-field', side, tr.get('side'))
    if type(actions) is not tuple:
        report('actions-type', 'tuple', type(actions).__name__)
    if type(events) is not list:
        report('events-type', 'list', type(events).__name__)
    actions = tuple(actions) if isinstance(actions, (list, tuple)) else ()
    events = list(events) if isinstance(events, (list, tuple)) else []
    pos = {a: i for i, a in enumerate(actions)}
    ppos = {a: i for i, a in enumerate(profile.get('actions') or ())}
    if len(pos) != len(actions):
        report('literal-occurrences', 'all distinct', 'duplicates found')
    if set(actions) != set(ppos):
        report('action-inventory', sorted(ppos), sorted(actions))
    if len(events) != len(actions):
        report('event-inventory', len(actions), len(events))
    qpos = {}
    if side == 'adapter':
        want = tuple(a for a in actions if not _handled(a))
        qpos = {a: i for i, a in enumerate(want)}
        qp = tr.get('q_profile')
        ok = (isinstance(qp, dict) and type(qp.get('actions')) is tuple and qp['actions'] == want
              and qp.get('requires') == {a: () for a in want} and set(qp) == set(profile)
              and all(exact(qp[k], profile[k]) for k in set(qp) - {'actions', 'requires'}))
        if not ok:
            report('q-profile', 'exact independent subprofile', qp)
    if not isinstance(tr.get('initial'), dict):
        report('initial-state', 'dict', type(tr.get('initial')).__name__)
        return False
    current, executed = copy.deepcopy(tr['initial']), []
    for p in range(len(events) + 1):
        charge.take(1)
        audited[0] += 1
        for check, expected, observed in _fields(current, side):
            report(check, expected, observed, p)
        if p == 0:
            init = dict(DEFAULTS)
            journal = current if side == 'source' else current.get('journal')
            if side == 'adapter':
                init['source_generation'] = TOKEN_HEAD + (0,)
            sub = {k: journal.get(k) for k in init} if isinstance(journal, dict) else journal
            if not isinstance(sub, dict) or not exact(sub, init):
                report('initial-journal', init, sub, 0)
            if side == 'adapter' and current.get('invocations') != ():
                report('initial-invocations', (), current.get('invocations'), 0)
        done = sum(1 << ppos[a] for a in executed if a in ppos)
        if current.get('done') != done:
            report('done-mask', done, current.get('done'), p)
        if side == 'adapter':
            inv = current.get('invocations')
            if type(inv) is not tuple:
                report('invocations-type', 'tuple', type(inv).__name__, p)
            else:
                ipos = [pos.get(a, -1) for a in inv]
                if (any(x < 0 or x >= p for x in ipos) or ipos != sorted(ipos)
                        or len(set(ipos)) != len(ipos) or any(_handled(a) for a in inv)):
                    report('invocation-chronology', 'ordered Q calls before prefix', list(inv), p)
                if isinstance(current.get('core'), dict):
                    mask = sum(1 << qpos[a] for a in inv if a in qpos)
                    if current['core'].get('done') != mask:
                        report('q-invocation-mask', mask, current['core'].get('done'), p)
        now = digest(current)
        if p:
            ev = events[p - 1]
            if isinstance(ev, dict) and now != ev.get('after_sha256'):
                report('poststate-hash', ev.get('after_sha256'), now, p)
            if rows is not None and p - 1 < len(rows) and isinstance(rows[p - 1], dict):
                row = rows[p - 1]
                kk = ('source_sha256', 'source_action') if side == 'source' else ('adapter_sha256', 'adapter_action')
                want_row = {'index': p - 1, kk[0]: now,
                            kk[1]: actions[p - 1] if p - 1 < len(actions) else None}
                got_row = {'index': row.get('index'), kk[0]: row.get(kk[0]), kk[1]: row.get(kk[1])}
                if got_row != want_row:
                    report('row-binding', want_row, got_row, p)
            if prefixes is not None and p < len(prefixes) and isinstance(prefixes[p], dict):
                pr = prefixes[p]
                k3 = 'source_state_sha256' if side == 'source' else 'adapter_state_sha256'
                proof = pr.get('identity_proof')
                bound = proof.get(k3) if isinstance(proof, dict) else now
                if pr.get('prefix') != p or bound != now:
                    report('prefix-binding', {'prefix': p, k3: now},
                           {'prefix': pr.get('prefix'), k3: bound}, p)
        if p == len(events):
            break
        ev = events[p]
        if not isinstance(ev, dict) or set(ev) != EVENT_KEYS:
            report('event-shape', sorted(EVENT_KEYS),
                   sorted(ev) if isinstance(ev, dict) else type(ev).__name__, p)
        if isinstance(ev, dict):
            if now != ev.get('before_sha256'):
                report('prestate-hash', ev.get('before_sha256'), now, p)
            act = actions[p] if p < len(actions) else None
            if ev.get('action') != act:
                report('chronological-event', act, ev.get('action'), p)
            elif act in executed:
                report('repeated-occurrence', 'first occurrence', act, p)
            elif not set(requires.get(act) or ()) <= set(executed):
                report('dependency-order', sorted(requires.get(act) or ()), list(executed), p)
            current = _apply(current, ev.get('patch'), side,
                             lambda c, e, o: report(c, e, o, p))
        executed.append(actions[p] if p < len(actions) else None)
    return True


def inspect_cases(cases, charge):
    """Bounded per-prefix inspection of retained trace certificates; see module docstring."""
    observations, limitations, failures = [], [], []
    audited = [0]

    def note(case, side, prefix, check, expected, observed):
        row = {'case': case, 'side': side, 'prefix': prefix, 'check': check,
               'expected': _wit(expected), 'observed': _wit(observed)}
        observations.append(row)
        failures.append(row)

    try:
        observations.append({'check': 'representation-semantics',
            'digest_collides_tuple_vs_list': digest((1,)) == digest([1]),
            'typed_distinguishes_tuple_vs_list': typed((1,)) != typed([1])})
    except Exception as error:
        limitations.append('representation self-check failed: ' + repr(error))
    if not isinstance(cases, (list, tuple)) or not cases:
        limitations.append('cases must be a non-empty sequence of retained case objects')
        return {'status': 'not_applicable', 'observations': observations,
                'limitations': limitations, 'audited_prefixes': 0}
    complete, partial = 0, False
    for ci, case in enumerate(cases):
        if not isinstance(case, dict):
            limitations.append('index-' + str(ci) + ': case object is not a dict')
            partial = True
            continue
        name = case.get('case')
        name = name if isinstance(name, str) else 'index-' + str(ci)
        before = audited[0]
        full = True
        for side in ('source', 'adapter'):
            tr = case.get(side)
            if not isinstance(tr, dict):
                limitations.append(name + ': missing ' + side + ' trace')
                full = False
                continue
            try:
                full = _trace(name, side, tr, case, charge, note, audited) and full
            except Exception as error:
                limitations.append(name + '/' + side + ': inspection aborted ' + repr(error))
                full = False
        partial = partial or not full
        ts, ta = case.get('source'), case.get('adapter')
        if isinstance(ts, dict) and isinstance(ta, dict):
            if not exact(ts.get('profile'), ta.get('profile')):
                note(name, 'both', None, 'profile-agreement', 'equal typed profiles', 'differ')
            if ts.get('actions') != ta.get('actions'):
                note(name, 'both', None, 'action-agreement', 'same literal actions', 'differ')
            acts = ts.get('actions') if type(ts.get('actions')) is tuple else ()
            for k, want in (('rows', len(acts)), ('prefixes', len(acts) + 1)):
                got = case.get(k)
                if got is not None and (type(got) is not list or len(got) != want):
                    note(name, 'both', None, k + '-inventory', want,
                         len(got) if type(got) is list else type(got).__name__)
            for j, pr in enumerate(case.get('incarnation_pairs') or ()):
                if not (isinstance(pr, dict) and all(type(pr.get(k)) is int and 0 <= pr[k] < len(acts)
                        for k in ('source_event', 'target_event'))):
                    note(name, 'both', j, 'pair-chronology',
                         'event index in [0,' + str(len(acts)) + ')', pr)
        observations.append({'case': name, 'prefixes_audited': audited[0] - before,
                             'fully_inspected': bool(full)})
        complete += bool(full)
    limitations.extend([
        'supported covers only the supplied retained cases; no reachability or all-orders claim',
        'state/event binding uses sha256 over canonical JSON where tuple and list collide; explicit type assertions counter that mode, other canonical collisions or a sha256 collision stay invisible',
        'a consistently mis-recorded transition (patch plus matching hashes) cannot be detected here; transition correctness belongs to the unchanged reducers and audits, which this check does not execute'])
    status = ('counterexample' if failures else 'unproved' if partial
              else 'supported' if complete else 'not_applicable')
    return {'status': status, 'observations': observations, 'limitations': limitations,
            'audited_prefixes': audited[0]}
