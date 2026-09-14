"""Additive certificate construction. Inherited modules load only after admission."""
import copy
import hashlib
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def typed(value):
    if type(value) is dict:
        return ['dict', [[k, typed(v)] for k, v in sorted(value.items())]]
    if type(value) in (tuple, list) or type(value).__name__ == 'Envelope':
        return [type(value).__name__, [typed(v) for v in value]]
    require(type(value) in (str, int, bool, type(None)), 'supported exact scalar')
    return [type(value).__name__, value]


def digest(value):
    return hashlib.sha256(json.dumps(typed(value), sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def exact(a, b):
    return typed(a) == typed(b)


def patch(before, after, adapter=False):
    result = {}
    for key, value in after.items():
        if not exact(before[key], value):
            result[key] = ({k: v for k, v in value.items()
                            if not exact(before[key][k], v)}
                           if adapter and key in ('core', 'journal') else value)
    return result


def trace(states, actions, profile, adapter=False):
    events = [dict(action=action, patch=patch(states[i], states[i + 1], adapter),
                   before_sha256=digest(states[i]), after_sha256=digest(states[i + 1]))
              for i, action in enumerate(actions)]
    return dict(initial=states[0], profile=profile, actions=actions, events=events)


def certificate(case_id, profile, actions, unit, outcome, ss, aa, kernel, binding):
    """No stored verdict is trusted by audit.py; it regenerates all rows."""
    require(len(ss) == len(aa) == len(actions) + 1, 'complete construction states')
    source = trace(ss, actions, profile)
    adapter = trace(aa, actions, profile, True)
    case = dict(case=case_id, unit=unit, outcome=outcome, source=source, adapter=adapter)
    pairs, rows = [], []
    for prefix in range(len(ss)):
        call = None
        if prefix:
            i = prefix - 1
            call = len(aa[prefix]['invocations']) != len(aa[i]['invocations'])
            kernel.advance(pairs, ss[i], aa[i], ss[prefix], aa[prefix], actions[i], i)
        comparison = kernel.compare(case, ss, aa, prefix, pairs)
        response = True if not prefix else kernel.response(ss[prefix], aa[prefix], actions[prefix - 1], pairs)
        rows.append(dict(prefix=prefix, comparison=comparison, response=response, q_invoked=call,
                         source_state=digest(ss[prefix]), adapter_state=digest(aa[prefix]),
                         source_prefix=digest(source['events'][:prefix]),
                         adapter_prefix=digest(adapter['events'][:prefix])))
    return dict(format='delegated-q-certificate/1', binding=copy.deepcopy(binding),
                case=case, rows=rows, pairs=pairs)


def classify(rows):
    failures = [r['prefix'] for r in rows if not r['comparison']['related'] or not r['response']]
    strict = all(r['comparison']['strict_related'] and r['response'] for r in rows)
    return dict(status='semantic-counterexample' if failures else 'finite-domain-pass',
                first_failing_prefix=min(failures) if failures else None,
                strict_complete=strict, staged_identity_complete=not failures,
                inductive_proof=False, unrestricted_refinement_proved=False)


class ScientificKernel:
    """Lazy adapter to unchanged reducers/relations. Never created by a fake gate."""
    def __init__(self):
        directory = ROOT / 'experiments/v3/cut-source-overnight/batch-07'
        sys.path.insert(0, str(directory))
        self.identity = importlib.import_module('identity')
        self.ia = importlib.import_module('identity_audit')
        self.t = self.identity.frozen
        self.d, self.r = self.identity.d, self.identity.r
        self.Envelope = self.d.q.Envelope
        self.fields = tuple(self.r.FIELDS)
        self.journal = (*self.d.s.EXTRA, 'source_generation')

    def initial(self, unit):
        return self.d.s.initial(unit), self.d.initial(unit)

    def initial_audit(self, source, adapter, unit):
        # Frozen auditors use Python == at some initialization sites (1 == True).
        # Add typed equality without changing them; charge both reference states.
        expected_source, expected_adapter = self.initial(unit)
        require(exact(source, expected_source) and exact(adapter, expected_adapter), 'complete typed original initialization')
        self.t.sc.initialization(source, unit)
        self.t.audit.initialization(adapter, unit)

    def step(self, source, adapter, action, profile, unit, outcome):
        ns = self.t.sa.step(source, action, profile, unit, outcome)
        split = self.d.s.flatten(self.t.sb.step(self.d.s.split(source), action, profile, unit, outcome))
        require(exact(ns, split), 'S inclusive/split agreement')
        na = self.t.aa.step(adapter, action, profile, unit, outcome)
        require(exact(na, self.t.ab.step(adapter, action, profile, unit, outcome)), 'adapter inclusive/split agreement')
        self.transition(source, adapter, ns, na, action, profile, unit, outcome)
        return ns, na

    def transition(self, source, adapter, ns, na, action, profile, unit, outcome):
        self.t.sc.check(source, action, ns, profile, unit, outcome)
        return self.t.audit.check(adapter, action, na, profile, unit, outcome)

    def advance(self, pairs, source, adapter, ns, na, action, index):
        self.r.advance(pairs, source, self.t.core_view(adapter), ns, self.t.core_view(na), action, action, index, index)

    def legacy_case(self, case, ss, aa):
        # Original proofs retain their original (untyped JSON) hash convention.
        # The enclosing certificate additionally binds type-sensitive full hashes.
        result = dict(case=case['case'])
        for side, states in (('source', ss), ('adapter', aa)):
            original = case[side]
            events = []
            for i, event in enumerate(original['events']):
                events.append(dict(event, before_sha256=self.d.digest(states[i]),
                                   after_sha256=self.d.digest(states[i + 1])))
            result[side] = dict(original, side=side, events=events)
        return result

    def compare(self, case, ss, aa, prefix, pairs):
        return self.identity.compare(self.legacy_case(case, ss, aa), ss, aa, prefix, pairs)

    def audit_row(self, row, case, ss, aa, prefix, pairs):
        self.ia.check(row, self.legacy_case(case, ss, aa), ss, aa, prefix, pairs)

    def response(self, source, adapter, action, pairs):
        return self.t.response(source, adapter, action, pairs)

    def audit_response(self, source, adapter, action, pairs):
        # Separately computed view relation, never reads the Q core's old decision.
        ok = self.r.typed(source['decision']) == self.r.typed(adapter['decision'])
        verb = action.partition('@')[0]
        if verb.startswith('append:') or verb == 'append-lose-reply':
            ok = ok and self.r.typed(source['append_reply']) == self.r.typed(adapter['journal']['append_reply'])
        if verb.startswith('pub-'):
            ok = ok and self.r.field_view(source, 'publication_reply', 'source', pairs) == self.r.field_view(adapter['core'], 'publication_reply', 'target', pairs)
        return ok


def experiment(plan, binding, kernel, emit):
    """Finite execution body for a future admitted controller; no implicit successor.

    emit must durably retain each certificate before the next history. The controller
    must precharge the complete plan, contain this process and retain partial failures.
    """
    profile = copy.deepcopy(plan['profile'])
    profile['actions'] = tuple(profile['actions'])
    profile['requires'] = {a: tuple(v) for a, v in profile['requires'].items()}
    profile['outcomes'] = tuple(profile['outcomes'])
    if isinstance(kernel, ScientificKernel):
        require(exact(profile, kernel.d.s.PROFILES['scale-eight-action-race']), 'original profile metadata and occurrences')
    results = []
    for entry in plan['cases']:
        source, adapter = kernel.initial(entry['unit'])
        kernel.initial_audit(source, adapter, entry['unit'])
        ss, aa = [source], [adapter]
        for action in entry['actions']:
            source, adapter = kernel.step(source, adapter, action, profile, entry['unit'], 1)
            ss.append(source)
            aa.append(adapter)
        cert = certificate(entry['id'], profile, tuple(entry['actions']), entry['unit'], 1, ss, aa, kernel, binding)
        emit(entry['id'], cert)
        results.append(dict(case=entry['id'], **classify(cert['rows'])))
    require(len(results) == len(plan['cases']), 'complete finite execution inventory')
    return results
