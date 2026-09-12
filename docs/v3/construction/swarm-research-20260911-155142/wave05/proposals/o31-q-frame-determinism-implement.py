"""Retained-certificate check o31: pure-Q transition dependence and fixed frame.

Obligation (domain o31-q-frame-determinism): every pure Q transition retained
in adapter histories depends only on done/decision, source generation, incoming
staged content and the immutable profile; and at source level the fixed setup
prefix, the free eight-action core and the fixed suffix of the unchanged
'scale-eight-action-race' profile act as a frame: identical states enter the
core after the fixed setup, and identical core-boundary states evolve
identically through the fixed suffix.

inspect_cases(cases, charge) audits actual typed run_history/artifact-restored
case objects. charge.take(1) is consumed BEFORE each inspected case prefix
(state index 0..len(actions)); every repeated inspection is charged again. The
inspector executes no reducer, guard, inventory or boundary helper and imports
none: it replays only the retained literal event patches, links retained event
hashes (event[i].after_sha256 == event[i+1].before_sha256), validates literal
action/dependency order, outer and Q-core completion masks, actual invocation
inventories, per-verb core/journal write frames, staged-envelope dependence
witnesses, cross-case transition determinism and the fixed setup/suffix state
equality groups. Refused decisions remain visible. Finite check over supplied
retained evidence only: not a global theorem, not all-order reachability, not
an accepted scientific result.

Source anchors (representation only; nothing imported or executed):
- cut-publication/q_inclusive.py step(): Q-owned verbs, decision shape k:reason,
  deny() refusals mutating only decision; duplicate reply/read fields.
- cut-publication/q_domain.py candidate()/incoming(): staged envelope fields
  bound to live generation, revision, selected generation, boot and serial.
- cut-source-overnight/batch-06/a_audit.py check(): non-invoked core identity,
  core done == actual invocation mask, adapter decision echoes core on calls.
- cut-source-overnight/batch-06/a_domain.py source_only()/subprofile(): fixed
  potential-Q-call set; a_inclusive.py step(): journal write conditions.
- cut-source-overnight/s_audit.py check(): source delegated frame and
  staged_source/selected_source bookkeeping.
- batch-05/semantic.py typed(): typed representation mirrored by typed().
- batch-06/adapter_traces.py trace_event()/restore(): retained patch format.
- s_domain.py add_with_suffix('scale-eight-action-race') and boundary-01
  spec.json: fixed setup 0..10, free core 11..18, fixed suffix 19..33, depth 34.
"""
import hashlib
import json

DEPTH, PREFIX_END, CORE_END = 34, 11, 19
TOP_LEVEL = ('core', 'journal', 'done', 'decision', 'invocations')
JOURNAL_FIELDS = ('registration', 'attempts', 'append_log', 'append_receipts',
                  'append_reply', 'source_revision', 'collection', 'collected',
                  'attestation', 'staged_source', 'selected_source', 'source_generation')
SOURCE_PREFIXES = ('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:')
SOURCE_EXACT = ('append-lose-reply', 'collect-open')
PUB_VERBS = ('pub-commit', 'pub-rival', 'pub-retry', 'pub-retry-conflict', 'pub-retry-foreign')
REFUSAL_WRITES = frozenset(('done', 'decision', 'publication_reply', 'publication_reads'))
CORE_WRITES = {
    'authority-restart': {'publisher_boot'},
    'publisher-revoke': {'publisher_serial'},
    'source-restart': {'source_generation'},
    'source-attest': {'source_name', 'source_head', 'source_version', 'source_generation'},
    'stage': {'staged', 'stage_serial'},
    'pub-lose-reply': {'publication_reply'},
    'reclaim': {'publication_store', 'retired_cuts'},
    'cut-receive': set(),
}
for _verb in PUB_VERBS:
    CORE_WRITES[_verb] = {'selected', 'publication_revision', 'publication_store',
                          'publication_receipts', 'publication_reply',
                          'publication_reads', 'cut_delivery'}
READER_WRITES = {'reader_requests', 'reader_pins', 'reader_waited', 'reader_copies',
                 'reader_nonce', 'installed_cut', 'cut_received', 'joined_cut',
                 'classified_cut', 'source_version'}


def typed(x):
    """Hashable typed representation of retained values (mirrors semantic.typed)."""
    if isinstance(x, dict):
        return ['dict', [[k, typed(v)] for k, v in sorted(x.items())]]
    if isinstance(x, (list, tuple)):
        return [type(x).__name__, [typed(v) for v in x]]
    return [type(x).__name__, x]


def digest(x):
    return hashlib.sha256(json.dumps(typed(x), sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def verb(action):
    return action.partition('@')[0]


def source_only(action):
    k = verb(action)
    return k in SOURCE_EXACT or any(k.startswith(p) for p in SOURCE_PREFIXES)


def core_writes(k):
    """Core fields a Q-owned verb may write besides done/decision; None = delegated."""
    if k in CORE_WRITES:
        return CORE_WRITES[k]
    if k.startswith('stage-'):
        return CORE_WRITES['stage']
    if k.startswith('reader-'):
        return READER_WRITES
    if k.startswith('source:'):
        return CORE_WRITES['source-attest']
    return None


def journal_writes(k, invoked):
    """Ledger fields the adapter may write for this verb and invocation outcome."""
    if invoked:
        out = set()
        if k == 'source-attest':
            out.add('attestation')
        if k == 'source-restart':
            out.add('source_generation')
        if k.startswith('stage'):
            out.add('staged_source')
        if k in PUB_VERBS:
            out.add('selected_source')
        return out
    if k.startswith('register:'):
        return {'registration', 'source_revision'}
    if k.startswith('attempt:'):
        return {'attempts', 'source_revision'}
    if k.startswith('atomic:'):
        return {'attempts', 'source_revision', 'append_log'}
    if k.startswith('append:'):
        return {'append_log', 'source_revision', 'append_receipts', 'append_reply'}
    if k == 'append-lose-reply':
        return {'append_reply'}
    if k == 'collect-open':
        return {'collection', 'collected'}
    if k.startswith('collect:'):
        return {'collected'}
    return frozenset()


def diff(before, after):
    keys = set(before) | set(after)
    return {k for k in keys if k not in before or k not in after
            or typed(before[k]) != typed(after[k])}


def apply_patch(before, patch, side):
    """One retained literal patch step; never a transition function."""
    nxt = dict(before)
    if side == 'adapter':
        nxt['core'] = dict(before['core'])
        nxt['journal'] = dict(before['journal'])
    for key, value in (patch or {}).items():
        if side == 'adapter' and key in ('core', 'journal'):
            nxt[key].update(value)
        else:
            nxt[key] = value
    return nxt


def shape(case):
    if not isinstance(case, dict):
        return 'case is not a dict'
    for side in ('source', 'adapter'):
        trace = case.get(side)
        if not isinstance(trace, dict):
            return 'missing ' + side + ' trace'
        for key in ('initial', 'profile', 'actions', 'events'):
            if key not in trace:
                return side + ' trace missing ' + key
        if len(trace['events']) != len(trace['actions']):
            return side + ' events/actions length mismatch'
    init = case['adapter']['initial']
    if not isinstance(init.get('core'), dict) or not isinstance(init.get('journal'), dict):
        return 'adapter initial lacks core/journal'
    return None


def frame_hypothesis(case, actions, profile, q_actions, name, limitations):
    """Membership in the declared fixed setup/core/suffix hypothesis."""
    def bad(why):
        limitations.append(name + ': ' + why)
        return False
    adp = case['adapter']
    if len(actions) != DEPTH or len(profile.get('actions', ())) != DEPTH:
        return bad('outside the fixed 34-action frame hypothesis')
    if (tuple(actions[:PREFIX_END]) != tuple(profile['actions'][:PREFIX_END])
            or tuple(actions[CORE_END:]) != tuple(profile['actions'][CORE_END:])
            or sorted(actions[PREFIX_END:CORE_END]) != sorted(profile['actions'][PREFIX_END:CORE_END])):
        return bad('schedule is not fixed-setup x core-permutation x fixed-suffix')
    if len(set(actions)) != DEPTH or sorted(actions) != sorted(profile['actions']):
        return bad('action inventory differs from immutable profile')
    if set(profile.get('requires', ())) < set(actions):
        return bad('profile requires table does not cover every action')
    if typed(adp['profile']) != typed(profile):
        return bad('source and adapter profiles differ')
    if tuple(adp.get('q_profile', {}).get('actions', ())) != q_actions:
        return bad('adapter q_profile differs from fixed potential-call set')
    init = adp['initial']
    if init.get('done') != 0 or tuple(init.get('invocations', (1,))) != ():
        return bad('adapter initial completion or invocation inventory nonzero')
    if set(init['journal']) < set(JOURNAL_FIELDS):
        return bad('initial journal lacks declared ledger fields')
    if typed(init['journal'].get('source_generation')) != typed(('cut-source', 'collectorA', 'effectA', 0)):
        return bad('initial journal generation is not the zero token')
    if case['source']['initial'].get('done') != 0:
        return bad('source initial completion nonzero')
    return True


def deep_witness(k, before, after, row, out):
    """Falsifiable dependence witnesses for the named Q-owned verbs."""
    def fail(check):
        out.append(dict(row, check=check))
    if k == 'source-restart':
        g = before.get('source_generation')
        if not (isinstance(g, tuple) and len(g) == 4
                and typed(after.get('source_generation')) == typed(g[:3] + (g[3] + 1,))):
            fail('source-restart-generation-step')
    elif k.startswith('stage'):
        staged = after.get('staged')
        env = staged[0] if isinstance(staged, tuple) and len(staged) == 2 else None
        got = (lambda f: getattr(env, f, None)) if env is not None else (lambda f: None)
        serial = before.get('stage_serial')
        permit = got('permit')
        checks = (
            ('staged-cut-from-delivery', got('cut') == before.get('cut_delivery')),
            ('staged-generation-dependence',
             typed(got('source_generation')) == typed(before.get('source_generation'))),
            ('staged-revision-dependence', got('expected_revision') == before.get('publication_revision')),
            ('staged-parent-dependence',
             got('parent') == (before['selected'].generation if before.get('selected') else '')),
            ('staged-boot-serial-dependence',
             isinstance(permit, tuple) and len(permit) > 4
             and permit[3] == ('publisher-boot', 'authority', before.get('publisher_boot'))
             and permit[4] == before.get('publisher_serial')),
            ('staged-request-generation-serial',
             type(serial) is int and got('request') == 'publication-' + str(serial + 1)
             and got('generation') == 'cut-generation-' + str(serial + 1)),
            ('stage-serial-advance', type(serial) is int and after.get('stage_serial') == serial + 1),
        )
        for check, holds in checks:
            if not holds:
                fail(check)
    elif k == 'source-attest':
        if after.get('source_name') != before.get('cut_delivery'):
            fail('attest-name-from-delivery')
        want = (before.get('source_generation') if before.get('source_name')
                else ('cut-source', 'collectorA', 'effectA', 1))
        if typed(after.get('source_generation')) != typed(want):
            fail('attest-generation-rule')
    elif k == 'pub-commit':
        env = after.get('selected')
        receipts = after.get('publication_receipts', ())
        rec = receipts[-1] if len(receipts) == len(before.get('publication_receipts', ())) + 1 else None
        holds = bool(before.get('staged')) and rec is not None and env is not None
        if holds:
            mac = hashlib.sha256(json.dumps(tuple(env), sort_keys=True,
                                            separators=(',', ':')).encode()).hexdigest()
            holds = (typed(env) == typed(before['staged'][0])
                     and after.get('publication_revision') == before['publication_revision'] + 1
                     and after.get('cut_delivery') == ''
                     and rec[0] == env.request and rec[1] == mac and rec[2] == before['publication_revision'] + 1
                     and rec[3] == env.generation and rec[4] == env.content
                     and typed(after.get('publication_reply')) == typed(rec)
                     and typed(after.get('publication_store', (None,))[-1]) == typed(before['staged']))
        if not holds:
            fail('pub-commit-receipt-dependence')


def inspect_cases(cases, charge):
    """Audit retained case prefixes; one charge.take(1) before each prefix."""
    observations, limitations, witnesses, refusal_log = [], [], [], []
    audited = transitions = invoked_total = 0
    if not isinstance(cases, (list, tuple)) or not cases:
        return {'status': 'not_applicable', 'observations': ['no retained cases supplied'],
                'limitations': ['empty case inventory'], 'audited_prefixes': 0}
    conforming_units, setup_groups, suffix_groups, boundary_keys, determinism = [], {}, {}, {}, {}
    for position, case in enumerate(cases):
        name = case.get('case') if isinstance(case, dict) else None
        name = name if isinstance(name, str) else 'case-' + str(position)
        why = shape(case)
        if why:
            limitations.append(name + ': ' + why)
            continue
        src, adp = case['source'], case['adapter']
        actions, profile, unit = list(src['actions']), src['profile'], case.get('unit')
        q_actions = tuple(a for a in profile['actions'] if not source_only(a))
        s_states = [dict(src['initial'])]
        a_states = [dict(adp['initial'], core=dict(adp['initial']['core']),
                         journal=dict(adp['initial']['journal']))]
        s_digests, a_digests = [digest(s_states[0])], [digest(a_states[0])]
        last_hash = {'source': None, 'adapter': None}
        for i in range(len(actions) + 1):
            charge.take(1)
            audited += 1
            if i == 0:
                if not frame_hypothesis(case, actions, profile, q_actions, name, limitations):
                    break
            else:
                transitions += 1
                index = i - 1
                action = actions[index]
                k = verb(action)
                row = {'case': name, 'index': index, 'action': action}
                for side, trace, states, digs in (('source', src, s_states, s_digests),
                                                  ('adapter', adp, a_states, a_digests)):
                    event = trace['events'][index]
                    if event.get('action') != action:
                        witnesses.append(dict(row, side=side, check='literal-action'))
                    if action in actions[:index] or set(profile['requires'][action]) - set(actions[:index]):
                        witnesses.append(dict(row, side=side, check='dependency-order'))
                    if last_hash[side] is not None and event.get('before_sha256') != last_hash[side]:
                        witnesses.append(dict(row, side=side, check='retained-hash-linkage'))
                    last_hash[side] = event.get('after_sha256')
                    states.append(apply_patch(states[-1], event.get('patch'), side))
                    digs.append(digest(states[-1]))
                a_before, a_after, s_after = a_states[-2], a_states[-1], s_states[-1]
                want_done = sum(1 << profile['actions'].index(x) for x in actions[:i])
                if a_after.get('done') != want_done or s_after.get('done') != want_done:
                    witnesses.append(dict(row, check='outer-done-mask'))
                if not (isinstance(a_after.get('decision'), str)
                        and a_after['decision'].startswith(k + ':')):
                    witnesses.append(dict(row, check='decision-shape',
                                          observed=a_after.get('decision')))
                inv_before, inv_after = a_before['invocations'], a_after['invocations']
                grew = (len(inv_after) == len(inv_before) + 1
                        and tuple(inv_after[:-1]) == tuple(inv_before))
                if grew and inv_after[-1] != action:
                    grew = False
                    witnesses.append(dict(row, check='invocation-order'))
                if not grew and tuple(inv_after[:len(inv_before)]) != tuple(inv_before):
                    witnesses.append(dict(row, check='invocation-inventory'))
                if grew and action not in q_actions:
                    witnesses.append(dict(row, check='invocation-outside-subprofile'))
                invoked_total += grew
                changed_core = diff(a_before['core'], a_after['core'])
                if not grew:
                    if changed_core:
                        witnesses.append(dict(row, check='non-invoked-core-frame',
                                              fields=sorted(changed_core)))
                else:
                    if a_after['decision'] != a_after['core'].get('decision'):
                        witnesses.append(dict(row, check='delegated-decision-echo'))
                    want_core = sum(1 << q_actions.index(x) for x in inv_after if x in q_actions)
                    if a_after['core'].get('done') != want_core:
                        witnesses.append(dict(row, check='core-done-invocation-mask'))
                    if a_after['decision'] == k + ':ok':
                        allowed = core_writes(k)
                        extra = changed_core - {'done', 'decision'}
                        if allowed is not None and not extra <= allowed:
                            witnesses.append(dict(row, check='q-write-frame',
                                                  fields=sorted(extra - allowed)))
                        deep_witness(k, a_before['core'], a_after['core'], row, witnesses)
                    else:
                        refusal_log.append(dict(row, decision=a_after['decision']))
                        if not changed_core <= REFUSAL_WRITES:
                            witnesses.append(dict(row, check='refusal-write-frame',
                                                  fields=sorted(changed_core - REFUSAL_WRITES)))
                changed_journal = diff(a_before['journal'], a_after['journal'])
                if not changed_journal <= journal_writes(k, grew):
                    witnesses.append(dict(row, check='journal-write-frame',
                                          fields=sorted(changed_journal - journal_writes(k, grew))))
                for side, digs, states in (('source', s_digests, s_states),
                                           ('adapter', a_digests, a_states)):
                    key = (side, unit, action, digs[i - 1])
                    value = (digs[i], states[i].get('decision'))
                    if key in determinism and determinism[key] != value:
                        witnesses.append(dict(row, side=side, check='transition-determinism'))
                    determinism.setdefault(key, value)
            if i <= PREFIX_END:
                setup_groups.setdefault((i, unit), set()).add((s_digests[i], a_digests[i]))
            if i == CORE_END:
                boundary_keys[name] = (unit, s_digests[CORE_END], a_digests[CORE_END])
            if i > CORE_END:
                suffix_groups.setdefault((i,) + boundary_keys[name], set()).add(
                    (s_digests[i], a_digests[i], a_states[i].get('decision')))
        else:
            conforming_units.append(unit)
    for (i, unit), group in setup_groups.items():
        if len(group) > 1:
            witnesses.append({'check': 'fixed-setup-frame', 'prefix': i, 'unit': unit,
                              'distinct_states': len(group)})
    for key, group in suffix_groups.items():
        if len(group) > 1:
            witnesses.append({'check': 'fixed-suffix-frame', 'prefix': key[0], 'unit': key[1],
                              'distinct_states': len(group)})
    boundary_diversity = {}
    for unit, sd, ad in boundary_keys.values():
        boundary_diversity.setdefault(unit, set()).add((sd, ad))
    observations.append({'cases_supplied': len(cases), 'cases_conforming': len(conforming_units),
                         'transitions_checked': transitions, 'q_invocations': invoked_total,
                         'refusals': len(refusal_log), 'determinism_pairs': len(determinism),
                         'charge_units_consumed': audited,
                         'distinct_core_boundary_states':
                             {str(u): len(v) for u, v in boundary_diversity.items()}})
    if refusal_log:
        observations.append({'visible_refusals': refusal_log[:25],
                             'refusal_log_truncated': len(refusal_log) > 25})
    limitations.extend([
        'Scoped to supplied retained cases only; no all-order (40320) or reachability claim.',
        'No reducer, guard, inventory or boundary helper executed or imported; only retained literal patches replayed.',
        'Retained event hashes are linked, not recomputed; equality uses this module typed digest, not original canonical sha256.',
        'Core/journal write tables and envelope witnesses transcribed from cited sources; base-delegated verbs get mask/decision/determinism checks only.',
        'Not a global theorem and not accepted scientific validation.'])
    if witnesses:
        status = 'counterexample'
        observations.append({'violations': witnesses[:25], 'violation_count': len(witnesses)})
    elif not conforming_units:
        status = 'not_applicable'
    elif len(conforming_units) != len(set(conforming_units)) and invoked_total:
        status = 'supported'
    else:
        status = 'unproved'
        limitations.append('cross-case frame or pure-Q invocation evidence is vacuous on supplied cases')
    return {'status': status, 'observations': observations,
            'limitations': limitations, 'audited_prefixes': audited}
