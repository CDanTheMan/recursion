"""Finite interface falsifiers, not a product implementation or formal refinement proof.

Enumerate topological schedules; compare each observed prefix with event-fact oracles.
Deliberately broken guards must produce counterexamples, including a deny-all guard.
"""
import copy
import json


def schedules(edges):
    def walk(prefix, remaining):
        if not remaining:
            yield prefix
        for event in sorted(remaining):
            if set(edges[event]) <= set(prefix):
                yield from walk(prefix + (event,), remaining - {event})
    yield from walk((), set(edges))


CONFIG_DAG = {
    'preference_R3': (), 'install_fence_E2': (), 'old_permit_arrival': (),
    'transport_ack': (), 'reconnect': (),
    'receipt_generation_0': ('install_fence_E2', 'transport_ack'),
    'receipt_generation_1': ('install_fence_E2', 'transport_ack', 'reconnect'),
    'independent_work': (),
}


def config_trace(order, mutant=None):
    # Prefix: A's permit was issued at E1, then Owner revoked A at E2.
    # R3 is an unrelated preference revision. B retains its independent grant.
    state = dict(canonical_epoch=2, recipient_epoch=1, preference=1,
                 generation=0, effective_generation=None, outcomes=[],
                 postrevoke_new_A='admitted' if mutant == 'omit_local_admission' else 'rejected')
    trace = []
    for event in order:
        if event == 'preference_R3':
            state['preference'] = 3
            if mutant == 'revision_is_authority': state['recipient_epoch'] = 3
        elif event == 'install_fence_E2':
            if mutant != 'coalesce_away_revocation': state['recipient_epoch'] = 2
        elif event == 'old_permit_arrival':
            permitted = state['recipient_epoch'] == 1 or mutant == 'omit_recipient_fence'
            state['outcomes'].append(('A_old', 'executed_exposed' if permitted else 'rejected'))
        elif event == 'transport_ack':
            if mutant == 'ack_is_effective': state['effective_generation'] = state['generation']
        elif event == 'reconnect':
            state['generation'] = 1
            state['effective_generation'] = None
        elif event.startswith('receipt_generation_'):
            generation = int(event[-1])
            if generation == state['generation'] or mutant == 'accept_stale_receipt':
                state['effective_generation'] = state['generation']
        elif event == 'independent_work':
            state['outcomes'].append(('B_fresh', 'rejected' if mutant == 'deny_all' else 'executed'))
        trace.append({'event': event, 'state': copy.deepcopy(state)})
    return trace


def config_oracle(trace):
    seen = set(); expected_effective = None; generation = 0; expected_outcomes = []
    for row in trace:
        event, state = row['event'], row['state']
        seen.add(event)
        if event == 'reconnect': generation = 1; expected_effective = None
        if event == 'receipt_generation_0' and 'reconnect' not in seen: expected_effective = 0
        if event == 'receipt_generation_1': expected_effective = 1
        if event == 'old_permit_arrival':
            expected_outcomes.append(('A_old', 'rejected' if 'install_fence_E2' in seen else 'executed_exposed'))
        if event == 'independent_work': expected_outcomes.append(('B_fresh', 'executed'))
        expected_epoch = 2 if 'install_fence_E2' in seen else 1
        checks = {
            'authority_not_preference_or_ack': state['recipient_epoch'] == expected_epoch,
            'receipt_generation_and_effective_status': state['effective_generation'] == expected_effective,
            'recipient_fence_and_independent_progress': state['outcomes'] == expected_outcomes,
            'canonical_revocation_preserved': state['canonical_epoch'] == 2,
            'new_local_work_after_revocation_rejected': state['postrevoke_new_A'] == 'rejected',
        }
        for name, passed in checks.items():
            if not passed: return {'obligation': name, 'prefix': [r['event'] for r in trace[:len(seen)]], 'actual': row}
    return None


CONSULT_DAG = {
    'ingress': (), 'replace_goal': (), 'rotate_lease': (), 'expire_reply_alias': (),
    'stop_owned_operation': (), 'adopt': ('ingress',),
    'old_reply_wakeup': ('ingress',),
    'relaunch_owned': ('stop_owned_operation',),
    'independent_work': ('stop_owned_operation',),
}


def consultation_trace(order, mutant=None):
    state = dict(goal=1, lease=1, alias_live=True, stopped=False, evidence=False,
                 adopted=False, wakeups=0, relaunches=0, independent_completed=0,
                 fresh_requested=False, fresh_evidence=False, fresh_adopted=False)
    trace = []
    for event in order:
        if event == 'replace_goal': state['goal'] = 2
        elif event == 'rotate_lease': state['lease'] = 2
        elif event == 'expire_reply_alias': state['alias_live'] = False
        elif event == 'stop_owned_operation':
            state['stopped'] = True
            state['alias_live'] = False
        elif event == 'ingress':
            state['evidence'] = state['alias_live'] or mutant == 'invent_expired_evidence'
        elif event == 'adopt':
            goal_ok = state['goal'] == 1 or mutant == 'omit_goal'
            lease_ok = state['lease'] == 1 or mutant == 'omit_lease'
            stop_ok = not state['stopped'] or mutant == 'omit_stop'
            state['adopted'] = state['evidence'] and goal_ok and lease_ok and stop_ok and mutant != 'deny_all'
        elif event == 'old_reply_wakeup':
            permitted = state['evidence'] and state['alias_live'] and state['goal'] == 1 and state['lease'] == 1 and not state['stopped']
            if permitted or mutant == 'wake_stale_continuation': state['wakeups'] += 1
        elif event == 'relaunch_owned':
            if not state['stopped'] or mutant == 'relaunch_after_stop': state['relaunches'] += 1
        elif event == 'independent_work':
            if mutant not in ('cancel_shared_consultant', 'deny_all'): state['independent_completed'] += 1
        trace.append({'event': event, 'state': copy.deepcopy(state)})
    # A separate operation B receives a fresh request/reply/adoption after all A events.
    # The request carries current goal/lease and a new generation; A's Stop cannot fence B.
    state['fresh_requested'] = True
    trace.append({'event':'fresh_B_request','state':copy.deepcopy(state)})
    state['fresh_evidence'] = True
    trace.append({'event':'fresh_B_ingress','state':copy.deepcopy(state)})
    state['fresh_adopted'] = mutant not in ('deny_all','cancel_all_consultations')
    trace.append({'event':'fresh_B_adopt','state':copy.deepcopy(state)})
    return trace


def consultation_oracle(trace):
    seen = set(); evidence = False; adoption = False; wakeups = 0; independent = 0
    for index, row in enumerate(trace):
        event, state = row['event'], row['state']
        # Evidence survives later replacement/Stop; an expired wire alias cannot create it.
        if event == 'ingress': evidence = not (seen & {'expire_reply_alias','stop_owned_operation'})
        if event == 'adopt': adoption = evidence and not (seen & {'replace_goal', 'rotate_lease', 'stop_owned_operation'})
        if event == 'old_reply_wakeup':
            wakeups += int(evidence and not (seen & {'replace_goal', 'rotate_lease', 'stop_owned_operation', 'expire_reply_alias'}))
        if event == 'independent_work': independent += 1
        seen.add(event)
        expected = {'evidence': evidence, 'adopted': adoption, 'wakeups': wakeups,
                    'relaunches': 0, 'independent_completed': independent,
                    'fresh_requested': 'fresh_B_request' in seen,
                    'fresh_evidence': 'fresh_B_ingress' in seen,
                    'fresh_adopted': 'fresh_B_adopt' in seen}
        for name, value in expected.items():
            if state[name] != value:
                return {'obligation': name, 'prefix': [r['event'] for r in trace[:index+1]], 'actual': row, 'expected': value}
    return None


def campaign():
    cases = [
        ('configuration', CONFIG_DAG, config_trace, config_oracle,
         ['revision_is_authority', 'coalesce_away_revocation', 'omit_recipient_fence', 'ack_is_effective', 'accept_stale_receipt', 'omit_local_admission', 'deny_all']),
        ('consultation', CONSULT_DAG, consultation_trace, consultation_oracle,
         ['invent_expired_evidence', 'omit_goal', 'omit_lease', 'omit_stop', 'wake_stale_continuation', 'relaunch_after_stop', 'cancel_shared_consultant', 'cancel_all_consultations', 'deny_all']),
    ]
    results = []
    for name, dag, reducer, oracle, mutants in cases:
        orders = list(schedules(dag)); witnesses = {}; prefixes = set(); positives = {}
        for order in orders:
            trace = reducer(order)
            failure = oracle(trace)
            if failure: raise ValueError((name, failure))
            actions=tuple(row['event'] for row in trace)
            for i in range(len(actions)+1): prefixes.add(actions[:i])
            final = trace[-1]['state']
            if name == 'configuration':
                if ('A_old','executed_exposed') in final['outcomes']: positives.setdefault('preinstall_exposure', order)
                if ('A_old','rejected') in final['outcomes']: positives.setdefault('postinstall_rejection', order)
                positives.setdefault('independent_progress', order)
            else:
                if final['adopted']: positives.setdefault('fresh_adoption_preserved_after_stop', order)
                if final['evidence'] and not final['adopted']: positives.setdefault('stale_evidence_retained', order)
                if not final['evidence']: positives.setdefault('expired_before_ingress_missing', order)
                if final['independent_completed']: positives.setdefault('poststop_independent_progress', order)
                if final['fresh_adopted']: positives.setdefault('fresh_generation_B_adoption_after_A_stop',actions)
            for mutant in mutants:
                if mutant not in witnesses:
                    failure = oracle(reducer(order, mutant))
                    if failure: witnesses[mutant] = failure
        if set(witnesses) != set(mutants): raise ValueError(('surviving_mutants',name,set(mutants)-set(witnesses)))
        required = 3 if name == 'configuration' else 5
        if len(positives) != required: raise ValueError(('missing_positive_witness',name,positives))
        # Every incomplete prefix is an explicit finite observation, including absent installs/replies.
        results.append({'case':name,'full_schedules':len(orders),'unique_prefixes':len(prefixes),
                        'positive_witnesses':positives,'killed_mutants':witnesses})
    return {'kind':'modeled_interface_falsifiers','model_calls':0,'cases':results,
            'limits':['Finite event DAGs; no fairness or eventual-delivery theorem',
                      'One reducer and separate event-fact oracle, not independent aggregate/broker refinement',
                      'No product, provider, plugin, remote node or quota behavior observed',
                      'Configuration case is a recipient-fence/connection-receipt abstraction, not full requested/validated/staged/NACK lifecycle',
                      'Fresh B consultation is an ordered suffix with assumed independent grant; grant issuance and broker refinement remain unproved',
                      'Pre-install old permit execution remains exposed; local revocation is not remote settlement']}


if __name__ == '__main__':
    print(json.dumps(campaign(),indent=2))
