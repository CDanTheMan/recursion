"""Order-only guard certificate. No model imports, initialization or reducer execution."""
import argparse
from collections import Counter
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NAME = 'eight-hour-research-20260910-01a08a22-slice2'
CORE = ('A2', 'A3', 'A4', 'C0', 'C1', 'C2', 'O', 'R')
TOTAL = math.factorial(8)
LIMIT = 40500
EXPECTED = {'stale-collection': 31248, 'incomplete-inventory': 8856, 'incomplete-registry': 216}
SOURCE_PATHS = ('experiments/v3/coupled-construction/c_domain.py', 'experiments/v3/coupled-cut-pause/p_literal.py', 'experiments/v3/cut-publication/q_inclusive.py', 'experiments/v3/cut-source-overnight/batch-06/a_inclusive.py', 'experiments/v3/cut-source-overnight/batch-06/a_split.py', 'experiments/v3/cut-source-overnight/batch-06/guard_a.py', 'experiments/v3/cut-source-overnight/batch-06/guard_b.py', 'experiments/v3/cut-source-overnight/s_domain.py', 'experiments/v3/cut-source-overnight/s_experiment.py', 'experiments/v3/cut-source-overnight/s_inclusive.py')
OCCURRENCES = {'A2': 'attempt:2@15', 'A3': 'attempt:3@16', 'A4': 'attempt:4@17', 'C0': 'collect:0@12', 'C1': 'collect:1@13', 'C2': 'collect:2@14', 'O': 'collect-open@11', 'R': 'source-restart@18'}
CONTROL_NAMES = ['missing-occurrence', 'duplicate-occurrence', 'missing-order', 'undercharged-work', 'failed-attempt4-changes-revision', 'attempt4-needs-successful-attempt3', 'restart-ignored', 'inventory-before-freshness', 'registry-bypass', 'capture-after-collection-counted-complete', 'altered-aggregate', 'duplicate-order', 'wrong-outcome', 'wrong-unit-domain', 'changed-source-pin', 'changed-source-path-domain', 'changed-occurrence-mapping', 'changed-source-hypothesis']
EXCEPTION = ('R', 'A3', 'A2', 'O', 'A4', 'C0', 'C1', 'C2')

def require(value, message):
    if not value: raise ValueError(message)

def raw(value): return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()
def sha(value): return hashlib.sha256(value).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))

class Work:
    def __init__(self, limit):
        require(type(limit) is int and limit >= 0, 'finite work limit')
        self.limit, self.used = limit, 0
    def tick(self):
        require(self.used < self.limit, 'precharged symbolic work bound')
        self.used += 1

def positions(order):
    require(type(order) in (list, tuple) and len(order) == 8 and set(order) == set(CORE), 'exact eight distinct occurrences')
    return {name: i for i, name in enumerate(order)}

def rank(order):
    positions(order)
    remaining, value = list(CORE), 0
    for i, name in enumerate(order):
        index = remaining.index(name)
        value += index * math.factorial(7-i)
        remaining.pop(index)
    return value

def by_successful_attempts(order):
    """Source-conditioned successful-registration predicates; not a reducer simulation."""
    p = positions(order)
    successful = ['A2']
    if p['A2'] < p['A3']: successful.append('A3')
    if p['A2'] < p['A3'] < p['A4']: successful.append('A4')
    fresh = all(p[name] < p['O'] for name in [*successful, 'R'])
    inventory = all(p['O'] < p[name] for name in ('C0', 'C1', 'C2'))
    guard = 'stale-collection' if not fresh else 'incomplete-inventory' if not inventory else 'incomplete-registry'
    return dict(order=list(order), successful_attempts=successful, fresh=fresh, complete_inventory=inventory,
                first_refusing_attestation_guard=guard)

def by_partial_orders(order):
    """Independently derived disjoint freshness classes and six attempt-order cases."""
    p = positions(order)
    first = all(p[x] < p['O'] for x in ('A2', 'A3', 'A4', 'R'))
    second = p['A3'] < p['A2'] < p['O'] < p['A4'] and p['R'] < p['O']
    require(not (first and second), 'disjoint freshness classes')
    fresh = first or second
    inventory = p['O'] < min(p['C0'], p['C1'], p['C2'])
    attempts = tuple(x for x in order if x.startswith('A'))
    mapping = {('A2','A3','A4'): ['A2','A3','A4'], ('A2','A4','A3'): ['A2','A3'],
               ('A3','A2','A4'): ['A2'], ('A3','A4','A2'): ['A2'],
               ('A4','A2','A3'): ['A2','A3'], ('A4','A3','A2'): ['A2']}
    guard = 'incomplete-registry' if fresh and inventory else 'incomplete-inventory' if fresh else 'stale-collection'
    return dict(order=list(order), successful_attempts=mapping[attempts], fresh=fresh, complete_inventory=inventory,
                first_refusing_attestation_guard=guard)

def check_row(row, work):
    work.tick()
    require(row == by_partial_orders(row['order']), 'actual symbolic row equals independent partial-order certificate')

def summary(rows):
    counts = dict(Counter(row['first_refusing_attestation_guard'] for row in rows))
    require(counts == EXPECTED and len(rows) == TOTAL, 'closed-form guard counts')
    subtotals = {}
    for order in itertools.permutations(('A2', 'A3', 'A4')):
        selected = [r for r in rows if tuple(x for x in r['order'] if x.startswith('A')) == order]
        value = dict(orders=len(selected), fresh=sum(r['fresh'] for r in selected),
                     fresh_complete=sum(r['fresh'] and r['complete_inventory'] for r in selected))
        exceptional = order == ('A3', 'A2', 'A4')
        require(value == dict(orders=6720, fresh=2352 if exceptional else 1344,
                              fresh_complete=96 if exceptional else 24), 'independent attempt-order subtotals')
        subtotals['<'.join(order)] = value
    return dict(guard_counts=counts, successful_attestation=0, attempt_order_subtotals=subtotals,
                fresh=8064+1008, fresh_complete=144+72,
                closed_form=dict(standard_fresh=math.factorial(8)//5,
                                 exceptional_fresh=3*math.factorial(8)//math.factorial(5),
                                 standard_fresh_complete=math.factorial(4)*math.factorial(3),
                                 exceptional_fresh_complete=3*math.factorial(4)))

def verify_rows(rows, work):
    require(type(rows) is list and len(rows) == TOTAL, 'all 40320 symbolic orders retained')
    ranks = set()
    for row in rows:
        index = rank(row['order'])
        require(index not in ranks, 'no duplicate replacing an order')
        ranks.add(index)
        check_row(row, work)
    require(ranks == set(range(TOTAL)), 'complete rank-bijection domain membership')
    return summary(rows)

def verify_summary(retained, expected):
    require(retained == expected, 'complete retained symbolic summary equality')

def controls(rows, spec, work):
    passed = []
    def rejected(name, action):
        work.tick()
        try: action()
        except ValueError: passed.append(name)
        else: raise ValueError('control unexpectedly accepted: ' + name)
    rejected('missing-occurrence', lambda: positions(CORE[:-1]))
    rejected('duplicate-occurrence', lambda: positions((*CORE[:-1], CORE[0])))
    rejected('missing-order', lambda: verify_rows(rows[:-1], work))
    rejected('undercharged-work', lambda: Work(0).tick())
    probes = [
        ('failed-attempt4-changes-revision', EXCEPTION, 'fresh', False),
        ('attempt4-needs-successful-attempt3', EXCEPTION, 'successful_attempts', ['A2','A4']),
        ('restart-ignored', ('A2','A3','A4','O','R','C0','C1','C2'), 'fresh', True),
        ('inventory-before-freshness', ('C0','O','A2','A3','A4','R','C1','C2'), 'first_refusing_attestation_guard', 'incomplete-inventory'),
        ('registry-bypass', EXCEPTION, 'first_refusing_attestation_guard', 'success'),
        ('capture-after-collection-counted-complete', ('C0','A2','A3','A4','R','O','C1','C2'), 'complete_inventory', True),
    ]
    for name, order, field, replacement in probes:
        row = by_successful_attempts(order); row[field] = replacement
        rejected(name, lambda row=row: check_row(row, work))
    genuine = summary(rows)
    changed = dict(genuine, guard_counts=dict(genuine['guard_counts']))
    changed['guard_counts']['stale-collection'] -= 1
    rejected('altered-aggregate', lambda: verify_summary(changed, genuine))
    duplicate = list(rows); duplicate[1] = duplicate[0]
    rejected('duplicate-order', lambda: verify_rows(duplicate, work))
    wrong = dict(spec, outcomes=[2])
    rejected('wrong-outcome', lambda: check_spec(wrong))
    wrong_unit = dict(spec, units_under_hypotheses=['event'])
    rejected('wrong-unit-domain', lambda: check_spec(wrong_unit))
    changed_pins = dict(spec['source_pins']); changed_pins[next(iter(changed_pins))] = '0'*64
    rejected('changed-source-pin', lambda: check_spec(dict(spec, source_pins=changed_pins)))
    different_paths = dict(spec['source_pins']); different_paths['CONTROL_PLANE.md'] = different_paths.pop(next(iter(different_paths)))
    rejected('changed-source-path-domain', lambda: check_spec(dict(spec, source_pins=different_paths)))
    wrong_mapping = dict(spec['occurrence_mapping'], A2='attempt:2@16')
    rejected('changed-occurrence-mapping', lambda: check_spec(dict(spec, occurrence_mapping=wrong_mapping)))
    rejected('changed-source-hypothesis', lambda: check_spec(dict(spec, hypotheses=[])))
    return passed

def check_spec(spec):
    require(spec['id'] == 'packet-06' and spec['kind'] == 'source-guard-combinatorics', 'source-only packet identity')
    require(spec['core'] == list(CORE) and spec['symbolic_orders'] == TOTAL, 'exact symbolic domain')
    require(spec['units_under_hypotheses'] == ['event','utf8-byte'] and spec['outcomes'] == [1], 'original units and fixed outcome')
    require(spec['per_command_work_limit'] == LIMIT and spec['reservation'] == 2*LIMIT, 'both invocations prospectively precharged')
    require(spec['model_state_visits'] == 0 and spec['hypotheses'] == [
        'successful fixed setup leaves valid registration, attempt1, three append records and no pause',
        'original scale-eight-action-race dependency profile with unchanged fixed successful delivery',
        'fixed success cut maps attempt1 only', 'nonmutant original source and adapter semantics'], 'explicit source hypotheses')
    require(set(spec['source_pins']) == set(SOURCE_PATHS), 'exact declared ten-source grounding')
    require(spec['occurrence_mapping'] == OCCURRENCES, 'original profile occurrence mapping')
    require(spec['required_controls'] == CONTROL_NAMES and spec['expected_symbolic_work_units_per_command'] == 40345, 'exact controls and symbolic work accounting')
    for name, expected in spec['source_pins'].items():
        path = (ROOT/name).resolve()
        require(path.is_relative_to(ROOT) and sha(path.read_bytes()) == expected, 'actual frozen source pin')

def run(spec_path, output, limit, audit=False):
    spec = read(spec_path); check_spec(spec)
    require(limit == LIMIT, 'exact reviewed finite invocation limit')
    work = Work(limit)
    if audit:
        require({p.name for p in output.iterdir()} == {'result.json','orders.json.gz'} and all(p.is_file() for p in output.iterdir()), 'exact generated symbolic artifact membership before audit')
        result = read(output/'result.json')
        data = (output/'orders.json.gz').read_bytes()
        require(sha(data) == result['orders_sha256'], 'retained symbolic artifact hash')
        rows = json.loads(gzip.decompress(data))
        totals = verify_rows(rows, work)
    else:
        require(not output.exists(), 'new owned symbolic output')
        rows = []
        for order in itertools.permutations(CORE):
            row = by_successful_attempts(order)
            check_row(row, work)
            rows.append(row)
        totals = summary(rows)
        data = gzip.compress(raw(rows), compresslevel=6, mtime=0)
    tests = controls(rows, spec, work)
    require(tests == CONTROL_NAMES and work.used == 40345, 'actual exact controls and work count')
    actual = dict(status='COMPLETE_CONDITIONAL_SYMBOLIC_GUARD_CLASSIFICATION', packet='packet-06',
                  symbolic_orders=TOTAL, model_histories_executed=0, model_state_visits=0,
                  symbolic_work_units=work.used, per_command_work_limit=LIMIT,
                  units_under_hypotheses=spec['units_under_hypotheses'], outcomes=[1], occurrence_mapping=OCCURRENCES,
                  hypothesis_sha256=sha(raw(spec['hypotheses'])), source_pins=spec['source_pins'],
                  spec_sha256=sha(spec_path.read_bytes()), checker_sha256=sha(Path(__file__).read_bytes()),
                  orders_sha256=sha(data), controls=tests, **totals,
                  scope='First refusing attestation guard only; no full-history replies, journals, strict/accepted relation, or execution certificates.')
    if audit:
        verify_summary(result, actual)
        require(not (output/'retained-audit.json').exists(), 'new retained audit output')
        (output/'retained-audit.json').write_bytes(raw(dict(status='RETAINED_SYMBOLIC_CERTIFICATE_PASS',
             result_sha256=sha((output/'result.json').read_bytes()), orders_sha256=sha(data),
             symbolic_work_units=work.used, model_state_visits=0)))
    else:
        output.mkdir(parents=True)
        (output/'orders.json.gz').write_bytes(data)
        (output/'result.json').write_bytes(raw(actual))
    print(actual['status'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', type=Path, required=True); parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--work-limit', type=int, required=True); parser.add_argument('--audit', action='store_true')
    args = parser.parse_args(); run(args.spec, args.output, args.work_limit, args.audit)
