"""Independent certificate traversal; no producer or scientific import at module load."""
import argparse
import copy
import hashlib
import json


def demand(condition, message):
    if not condition:
        raise ValueError(message)


def representation(value):
    kind = type(value).__name__
    if kind == 'dict':
        return [kind, [[key, representation(value[key])] for key in sorted(value)]]
    if kind in ('tuple', 'list', 'Envelope'):
        return [kind, list(map(representation, value))]
    demand(type(value) in (str, int, bool, type(None)), 'audit scalar type')
    return [kind, value]


def sha(value):
    raw = json.dumps(representation(value), separators=(',', ':'), sort_keys=True).encode()
    return hashlib.sha256(raw).hexdigest()


def same(left, right):
    return representation(left) == representation(right)


def type_frame(before, after):
    """Strengthen value-only inherited frames on this fixed typed domain.

    No retained numeric leaf changes its int/bool type in DQ-16. A value-equal
    subtree must retain its complete type structure. Changed/growing containers
    still undergo the original complete transition postconditions below.
    """
    if type(before) in (int, bool) and type(after) in (int, bool):
        demand(type(before) is type(after), 'numeric transition type alias')
    if before == after:
        demand(same(before, after), 'value-equal transition must preserve exact types')
    if type(before) is dict and type(after) is dict:
        for key in before.keys() & after.keys():
            type_frame(before[key], after[key])
    elif isinstance(before, (tuple, list)) and isinstance(after, (tuple, list)):
        for old, new in zip(before, after):
            type_frame(old, new)


def decode(node, envelope_type):
    demand(type(node) is list and len(node) == 2, 'typed transport node')
    tag, body = node
    if tag == 'dict':
        demand(type(body) is list and all(type(x) is list and len(x) == 2 and type(x[0]) is str for x in body), 'dictionary entries')
        demand(len({x[0] for x in body}) == len(body), 'duplicate dictionary key')
        return {k: decode(v, envelope_type) for k, v in body}
    if tag in ('tuple', 'list', 'Envelope'):
        demand(type(body) is list, 'sequence body')
        values = [decode(x, envelope_type) for x in body]
        if tag == 'Envelope':
            return envelope_type(*values)
        return tuple(values) if tag == 'tuple' else values
    kinds = {'str': str, 'int': int, 'bool': bool, 'NoneType': type(None)}
    demand(tag in kinds and type(body) is kinds[tag], 'exact transport scalar')
    return body


def restore(trace, side, expected_profile, actions, kernel):
    demand(set(trace) == {'initial', 'profile', 'actions', 'events'}, 'complete trace schema')
    demand(same(trace['profile'], expected_profile) and same(trace['actions'], actions), 'literal profile and order binding')
    demand(len(trace['events']) == len(actions), 'complete event inventory')
    fields = set(kernel.fields) | {'done', 'decision'}
    journal = set(kernel.journal)
    def frame(state):
        demand(type(state['done']) is int and state['done'] >= 0 and type(state['decision']) is str, 'typed outer bookkeeping')
        if side == 'source':
            demand(set(state) == fields | journal, 'all source fields')
        else:
            demand(set(state) == {'core', 'journal', 'done', 'decision', 'invocations'}, 'all adapter fields')
            demand(set(state['core']) == fields and set(state['journal']) == journal, 'all Q and journal fields')
            demand(type(state['core']['done']) is int and state['core']['done'] >= 0 and type(state['core']['decision']) is str, 'typed Q bookkeeping')
            demand(type(state['invocations']) is tuple, 'typed invocation history')
    states = [copy.deepcopy(trace['initial'])]
    frame(states[0])
    executed = []
    for position, event in enumerate(trace['events']):
        demand(set(event) == {'action', 'patch', 'before_sha256', 'after_sha256'}, 'event schema')
        action = actions[position]
        demand(event['action'] == action and action not in executed, 'literal occurrence identity')
        demand(set(expected_profile['requires'][action]) <= set(executed), 'original dependency identity')
        previous = states[-1]
        demand(event['before_sha256'] == sha(previous), 'full typed prestate hash')
        following = copy.deepcopy(previous)
        demand(type(event['patch']) is dict and set(event['patch']) <= set(following), 'patch frame')
        for key, value in event['patch'].items():
            if side == 'adapter' and key in ('core', 'journal'):
                demand(type(value) is dict and set(value) <= set(following[key]), 'nested patch frame')
                following[key].update(value)
            else:
                following[key] = value
        frame(following)
        executed.append(action)
        demand(type(following['done']) is int and following['done'] == sum(1 << expected_profile['actions'].index(a) for a in executed), 'outer occurrence mask')
        if side == 'adapter':
            potential = [a for a in expected_profile['actions'] if not
                         (a.partition('@')[0].startswith(('register:', 'attempt:', 'atomic:', 'append:', 'collect:', 'source:'))
                          or a.partition('@')[0] in ('append-lose-reply', 'collect-open'))]
            calls = following['invocations']
            demand(len(set(calls)) == len(calls) and all(a in potential for a in calls), 'actual call inventory')
            demand(tuple(a for a in executed if a in calls) == calls, 'chronological actual calls')
            demand(type(following['core']['done']) is int and following['core']['done'] == sum(1 << potential.index(a) for a in calls), 'actual Q invocation mask')
        demand(event['after_sha256'] == sha(following), 'full typed poststate hash')
        states.append(following)
    return states


def inspect(cert, binding, entry, profile, kernel):
    demand(set(cert) == {'format', 'binding', 'case', 'rows', 'pairs'}, 'certificate schema')
    demand(cert['format'] == 'delegated-q-certificate/1' and same(cert['binding'], binding), 'fresh candidate/plan/input binding')
    case = cert['case']
    demand(set(case) == {'case', 'unit', 'outcome', 'source', 'adapter'}, 'case schema')
    demand(case['case'] == entry['id'] and case['unit'] == entry['unit'] and type(case['outcome']) is int and case['outcome'] == 1, 'identical declared environment')
    actions = tuple(entry['actions'])
    ss = restore(case['source'], 'source', profile, actions, kernel)
    aa = restore(case['adapter'], 'adapter', profile, actions, kernel)
    kernel.initial_audit(ss[0], aa[0], entry['unit'])
    demand(len(cert['rows']) == len(actions) + 1, 'every pre/post prefix required')
    pairs, failures, strict_failures = [], [], []
    for prefix, row in enumerate(cert['rows']):
        demand(set(row) == {'prefix', 'comparison', 'response', 'q_invoked', 'source_state', 'adapter_state', 'source_prefix', 'adapter_prefix'}, 'row schema')
        demand(type(row['prefix']) is int and row['prefix'] == prefix, 'prefix index')
        demand(row['source_state'] == sha(ss[prefix]) and row['adapter_state'] == sha(aa[prefix]), 'row state bindings')
        demand(row['source_prefix'] == sha(case['source']['events'][:prefix]) and row['adapter_prefix'] == sha(case['adapter']['events'][:prefix]), 'full event prefix bindings')
        call, response = None, True
        if prefix:
            i = prefix - 1
            type_frame(ss[i], ss[prefix])
            type_frame(aa[i], aa[prefix])
            call = kernel.transition(ss[i], aa[i], ss[prefix], aa[prefix], actions[i], profile, entry['unit'], 1)
            demand(type(call) is bool, 'actual call audit result')
            expected_calls = aa[i]['invocations'] + ((actions[i],) if call else ())
            demand(same(aa[prefix]['invocations'], expected_calls), 'one actual call or visible noncall')
            if not call:
                demand(same(aa[i]['core'], aa[prefix]['core']), 'entire Q core preserved on noncall')
            kernel.advance(pairs, ss[i], aa[i], ss[prefix], aa[prefix], actions[i], i)
            response = kernel.audit_response(ss[prefix], aa[prefix], actions[i], pairs)
        demand(same(row['q_invoked'], call) and same(row['response'], response), 'actual visible response and Q call')
        saved = copy.deepcopy(pairs)
        kernel.audit_row(row['comparison'], case, ss, aa, prefix, pairs)
        demand(same(saved, pairs), 'identity cannot create incarnation pairs')
        if not row['comparison']['related'] or not response:
            failures.append(prefix)
        if not row['comparison']['strict_related'] or not response:
            strict_failures.append(prefix)
    demand(same(pairs, cert['pairs']), 'complete causal incarnation ledger')
    return dict(case=entry['id'], certificate_valid=True,
                status='semantic-counterexample' if failures else 'finite-domain-pass',
                first_failing_prefix=min(failures) if failures else None,
                strict_complete=not strict_failures, staged_identity_complete=not failures,
                inductive_proof=False, unrestricted_refinement_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--receipt', required=True)
    args = parser.parse_args()
    # Current bundle has no trusted external controller binding. A file's own
    # assertion that it was admitted cannot bootstrap that trust.
    import check
    check.source_gate(args.candidate, check.ROOT / check.PLAN)
    check.refuse_scientific_admission('audit', args.receipt)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'AUDIT_REFUSED', 'reason': str(error), 'scientific_imports': 0}))
        raise SystemExit(2)
