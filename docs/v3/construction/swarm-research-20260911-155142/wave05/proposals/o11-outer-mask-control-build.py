"""o11 outer-mask retained-evidence controls (boundary-01 scale-eight-action-race).

Obligation: original outer done-mask coverage across permuted literal actions.
For every retained prefix of a supplied original typed case (c.run_history /
c.artifact restored objects) the outer done mask of BOTH source and adapter
frames must equal OR(1 << profile['actions'].index(a)) over the literal actions
executed so far, whether accepted or visibly refused.  Three coordinates are
kept distinct: chronological index inside case[side]['actions'], the '@N'
occurrence-suffix text, and the profile position that owns the done bit.  A
defect setting done by chronological index is invisible on canonical orders
and yields a dependency-closed but wrong mask on permuted orders; only
prefixes with expected != chronological are genuine 'supported' witnesses.

Source anchors (representation only; this module imports none of them):
  s_inclusive/s_split.step: done = s['done'] | 1<<p['actions'].index(a), set
      before the guard decision, so refused literals keep their bit
  a_inclusive/a_split.step: identical outer bit on the adapter frame
  adapter_traces.restore: done == sum(1<<profile index per executed literal),
      event['action']==action plus requires-closure per chronological step
  s_domain.add_with_suffix: occurrence suffix text is '@'+profile position
  boundary-01 spec.json: fixed prefix 11, permuted core 8, suffix from 19

Audit accounting: charge.take(1) before every case-level structural read and
every inspected prefix, mutated re-inspections included; audited_prefixes
counts prefixes only.  No reducer/guard/inventory/restore/hash runs or is
imported; prefix done values come solely from retained 'initial' fields and
event 'patch' values, so forged masks preserving original before/after sha256
still reach the semantic comparison.  A forged mask is 'domain-reachable' when
it equals a requires-closed subset of the same profile (legal under another
original order), else 'unreachable'; both classes must be detected.  Controls
needing a discriminating/forward prefix report 'missing-witness', never claim.
"""
import copy


def _position(profile, literal):
    return profile['actions'].index(literal)


def _mask(profile, literals):
    value = 0
    for literal in literals:
        value |= 1 << _position(profile, literal)
    return value


def _closed(profile, mask):
    done = {a for i, a in enumerate(profile['actions']) if mask >> i & 1}
    return all(set(profile['requires'].get(a, ())) <= done for a in done)


def _done(trace, prefix):
    value = trace['initial']['done']
    for event in trace['events'][:prefix]:
        if 'done' in event['patch']:
            value = event['patch']['done']
    return value


def inspect_cases(cases, charge):
    """Bounded per-prefix audit of retained outer done-mask evidence."""
    mismatches, limits, reports, witnesses = [], [], [], []
    audited = discriminating = uninspectable = 0

    def bad(ci, p, side, kind, expected, observed, **extra):
        mismatches.append(dict(case=ci, prefix=p, side=side, kind=kind,
                               expected=expected, observed=observed, **extra))

    for ci, case in enumerate(cases):
        charge.take(1)
        try:
            st, at = case['source'], case['adapter']
            profile, actions = st['profile'], st['actions']
            depth = len(actions)
            intact = (at['actions'] == actions
                      and at['profile']['actions'] == profile['actions']
                      and len(st['events']) == depth == len(at['events'])
                      and all(type(e) is dict and type(e.get('patch')) is dict
                              for e in st['events'] + at['events']))
        except (AttributeError, KeyError, TypeError):
            intact = False
        if not intact:
            uninspectable += 1
            limits.append('case %d: retained trace structure uninspectable' % ci)
            continue
        refusals, local = [], 0
        for p in range(depth + 1):
            charge.take(1)
            audited += 1
            chrono = (1 << p) - 1
            try:
                expected = _mask(profile, actions[:p])
            except ValueError:
                expected = None
                bad(ci, p, 'both', 'unprofiled-literal', None,
                    actions[p - 1] if p else None)
            if expected is not None:
                if expected != chrono:
                    discriminating += 1
                    local += 1
                    if len(witnesses) < 16:
                        witnesses.append(dict(case=ci, prefix=p,
                            expected=expected, chronological=chrono))
                for side, trace in (('source', st), ('adapter', at)):
                    observed = _done(trace, p)
                    if observed != expected:
                        bad(ci, p, side, 'done-mask', expected, observed,
                            chronological=chrono)
            if not p:
                continue
            literal = actions[p - 1]
            suffix = literal.rsplit('@', 1)[-1] if type(literal) is str else ''
            bit = _position(profile, literal) if literal in profile['actions'] else -1
            if not suffix.isdigit() or int(suffix) != bit:
                bad(ci, p, 'both', 'occurrence-suffix', bit, suffix)
            if bit >= 0 and not set(profile['requires'].get(literal, ())) <= set(actions[:p - 1]):
                bad(ci, p, 'both', 'dependency',
                    sorted(profile['requires'].get(literal, ())), literal)
            for side, trace in (('source', st), ('adapter', at)):
                if trace['events'][p - 1].get('action') != literal:
                    bad(ci, p, side, 'literal-occurrence', literal,
                        trace['events'][p - 1].get('action'))
            try:
                decision = case['rows'][p - 1]['source_observation']['decision']
                if type(decision) is str and not decision.endswith(':ok'):
                    refusals.append(decision)
            except (IndexError, KeyError, TypeError):
                pass
        reports.append(dict(case=ci, name=case.get('case'), prefixes=depth + 1,
                            discriminating=local, visible_refusals=refusals[:8]))
    if mismatches:
        status = 'counterexample'
    elif not cases:
        status = 'not_applicable'
    elif uninspectable:
        status = 'unproved'
        limits.append('%d supplied case(s) not fully auditable' % uninspectable)
    elif not discriminating:
        status = 'unproved'
        limits.append('no discriminating prefix: expected==chronological everywhere')
    else:
        status = 'supported'
    return dict(status=status, audited_prefixes=audited, limitations=limits,
                observations=dict(case_reports=reports,
                    discriminating_witnesses=witnesses,
                    mismatches=mismatches[:32], mismatch_total=len(mismatches)))


def _forge(case, prefix, mask):
    profile = case['source']['profile']
    for side in ('source', 'adapter'):
        case[side]['events'][prefix - 1]['patch']['done'] = mask
    return dict(forged_mask=mask,
        reachability='domain-reachable' if _closed(profile, mask) else 'unreachable')


def run_controls(cases, inspect_cases, charge):
    """Adversarial retained-evidence controls against the supplied checker."""
    controls = []

    def find(want):
        for ci, case in enumerate(cases):
            try:
                hits = [p for p in range(1, len(case['source']['actions']) + 1)
                        if want(case, p)]
            except (KeyError, TypeError):
                hits = []
            if hits:
                return ci, hits[0]
        return None

    def probe(label, want, mutate):
        hit = find(want)
        if hit is None:
            controls.append(dict(control=label, expected_status='counterexample',
                observed_status=None, detected=None, as_expected=None,
                audited_prefixes=0,
                limitation='missing-witness: no supplied case reaches it'))
            return
        ci, p = hit
        forged = copy.deepcopy(cases[ci])
        note = mutate(forged, p)
        res = inspect_cases([forged], charge)
        controls.append(dict(control=label, expected_status='counterexample',
            observed_status=res['status'], detected=res['status'] == 'counterexample',
            as_expected=res['status'] == 'counterexample', case=ci, prefix=p,
            audited_prefixes=res['audited_prefixes'], **note))

    def discriminating(case, p):
        try:
            return _mask(case['source']['profile'],
                         case['source']['actions'][:p]) != (1 << p) - 1
        except (KeyError, TypeError, ValueError):
            return False

    def unmet(case, p):
        try:
            done = set(case['source']['actions'][:p])
            return any(not set(case['source']['profile']['requires'].get(b, ())) <= done
                       for b in case['source']['profile']['actions'])
        except (KeyError, TypeError):
            return False

    def forge_unmet(case, p):
        profile = case['source']['profile']
        extra = next(b for b in profile['actions'] if
                     not set(profile['requires'].get(b, ())) <= set(case['source']['actions'][:p]))
        note = _forge(case, p, _mask(profile, case['source']['actions'][:p])
                      | (1 << _position(profile, extra)))
        note['blocked_literal'] = extra
        return note

    def relabel(case, p):
        old = case['source']['actions'][p - 1]
        new = old.rsplit('@', 1)[0] + '@0'
        for side in ('source', 'adapter'):
            order = list(case[side]['actions'])
            order[p - 1] = new
            case[side]['actions'] = tuple(order)
            case[side]['events'][p - 1]['action'] = new
        return dict(original_literal=old, forged_literal=new,
                    reachability='unreachable-literal')

    def substitute(case, p):
        old, other = case['source']['actions'][p - 1], case['source']['actions'][0]
        case['adapter']['events'][p - 1]['action'] = other
        return dict(original_literal=old, forged_literal=other, side='adapter',
                    reachability='domain-reachable-literal')

    base = inspect_cases(cases, charge)
    controls.append(dict(control='unmutated-retained-evidence',
        expected_status='supported', observed_status=base['status'], detected=None,
        as_expected=base['status'] == 'supported',
        audited_prefixes=base['audited_prefixes']))
    probe('chronological-index-mask', discriminating,
          lambda c, p: _forge(c, p, (1 << p) - 1))
    probe('dropped-executed-bit', discriminating, lambda c, p: dict(
          _forge(c, p, _mask(c['source']['profile'], c['source']['actions'][:p])
                 & ~(1 << _position(c['source']['profile'], c['source']['actions'][p - 1]))),
          dropped_literal=c['source']['actions'][p - 1]))
    probe('unreachable-forward-bit', unmet, forge_unmet)
    probe('next-prefix-mask', lambda c, p: discriminating(c, p)
          and p < len(c['source']['actions']),
          lambda c, p: _forge(c, p, _mask(c['source']['profile'],
                                          c['source']['actions'][:p + 1])))
    probe('occurrence-suffix-relabel', discriminating, relabel)
    probe('event-literal-substitution', discriminating, substitute)
    return dict(controls=controls, total=len(controls),
        detected=sum(1 for r in controls if r.get('detected')),
        as_expected=sum(1 for r in controls if r.get('as_expected')),
        missing_witness=sum(1 for r in controls if 'limitation' in r),
        audited_prefixes=sum(r['audited_prefixes'] for r in controls))
