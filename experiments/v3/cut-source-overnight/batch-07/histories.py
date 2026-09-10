"""One preregistered extra history; the original 104 environments stay unchanged."""
import copy
import identity as relation

t, d, r = relation.frozen, relation.d, relation.r
ACTIONS = (
    'admitA@0', 'intent@1', 'send@2', 'remote@3', 'lose@4', 'query@5',
    'register:success@6', 'attempt:1@7', 'append:success:0:normal@8',
    'append:success:1:normal@9', 'append:success:2:normal@10',
    'collect-open@11', 'collect:0@12', 'collect:2@13', 'cut:success@14',
    'cut-deliver@15', 'source-attest@16', 'stage@17', 'collect:1@18',
    'source-attest@19', 'pub-commit@20', 'stage@21', 'pub-commit@22',
)


def run(remaining_visits):
    profile = copy.deepcopy(d.s.PROFILES['delayed-record'])
    profile.update(actions=ACTIONS, requires={action: () if i == 0 else (ACTIONS[i - 1],)
                                             for i, action in enumerate(ACTIONS)})
    d.require(profile['outcomes'] == (1,) and profile['policy'] == 'pending'
              and profile['queue'] == 'source_authority', 'preserved focused profile metadata')
    cases, charged = [], 0
    for unit in d.s.UNITS:
        charged += 2 * (len(ACTIONS) + 1)
        d.require(charged <= remaining_visits, 'pre-initialization additional history visit admission')
        source, adapter = d.s.initial(unit), d.initial(unit)
        t.sc.initialization(source, unit); t.audit.initialization(adapter, unit)
        st = dict(side='source', initial=copy.deepcopy(source), profile=profile, actions=ACTIONS, events=[])
        at = dict(side='adapter', initial=copy.deepcopy(adapter), profile=profile, q_profile=d.subprofile(profile), actions=ACTIONS, events=[])
        pairs, rows = [], []
        for index, action in enumerate(ACTIONS):
            d.require(set(d.s.ready_actions(source, profile)) == t.sc.enabled(source, profile)
                      and action in t.sc.enabled(source, profile), 'unchanged source enabledness')
            ns = t.sa.step(source, action, profile, unit, 1)
            d.require(d.exact(ns, d.s.flatten(t.sb.step(d.s.split(source), action, profile, unit, 1))), 'unchanged S implementations agree')
            t.sc.check(source, action, ns, profile, unit, 1)
            na = t.aa.step(adapter, action, profile, unit, 1)
            d.require(d.exact(na, t.ab.step(adapter, action, profile, unit, 1)), 'unchanged adapter implementations agree')
            call = t.audit.check(adapter, action, na, profile, unit, 1)
            oldpairs = copy.deepcopy(pairs)
            binding = r.advance(pairs, source, t.core_view(adapter), ns, t.core_view(na), action, action, index, index)
            row = t.comparison(source, adapter, ns, na, oldpairs, pairs, action, index, call)
            row['binding'] = binding; rows.append(row)
            st['events'].append(t.trace_event(source, ns, action))
            at['events'].append(t.trace_event(adapter, na, action, True))
            source, adapter = ns, na
        d.require(d.exact(t.restore(st)[-1], source) and d.exact(t.restore(at)[-1], adapter), 'complete retained focused histories')
        cases.append(dict(case='identity-old-stage-first-attestation/' + unit + '/1', source=st, adapter=at,
                          rows=rows, incarnation_pairs=pairs, source_events=len(rows), adapter_events=len(rows),
                          q_invocations=len(adapter['invocations']), unmatched_visible_events=0,
                          complete_selected_trace_correspondence=all(x['prestate_related'] and x['state_related'] and x['responses_related'] for x in rows)))
    return cases
