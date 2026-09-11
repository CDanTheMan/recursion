"""Independent retained audit of the boundary-01 frozen inventory record.

Recomputes the complete 40320-order core antichain enumeration, the literal
fresh-incomplete / stale-complete memberships, the 192x2 unit flat index map,
factoradic global ranks and every provenance field carried by the actual frozen
format.  Imports the unchanged earlier checker only (c.domain, original schema
validation, d.require/d.digest); never imports boundary.py or calls its
inventory/census/tally/observation helpers, never mutates the original profile
registry and explores no new source/adapter histories.  Work is charged in
symbolic complete-schedule-candidate units, taken before each candidate.
Importing the original checker constructs inherited planning fixtures; admitted
execution must use research_entry.py and separately reserve those kernel calls.
"""
import argparse
import hashlib
import itertools
import json
import sys
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHECK_DIR = 'experiments/v3/eight-hour-research-20260910-01a08a22'
sys.path.insert(0, str(ROOT / CHECK_DIR))
import check as c

d = c.d
require = d.require
require(Path(c.__file__).resolve() == ROOT / CHECK_DIR / 'check.py',
        'explicit frozen checker path binding')

PACKET, DOMAIN = 'boundary-01', 'scale-eight-action-race'
PREFIX, CORE, SUFFIX, DEPTH = 11, 8, 19, 34
WHOLE = factorial(CORE)
UNITS, OUTCOME = ('event', 'utf8-byte'), 1
COLLECTS = ('collect:0@12', 'collect:1@13', 'collect:2@14')
OPEN, RESTART = 'collect-open@11', 'source-restart@18'
ATTEMPTS = ('attempt:2@15', 'attempt:3@16', 'attempt:4@17')
FREE = frozenset((*ATTEMPTS, RESTART))
TAIL2, ALL3 = frozenset(COLLECTS[1:]), frozenset(COLLECTS)
SUBCLASS_ORDERS = {'fresh-incomplete': 48, 'stale-complete': 144}
SELECTED = 192
FROZEN_KEYS = frozenset(('packet', 'domain', 'profile_sha256', 'whole_inventory_sha256',
                         'orders_per_unit', 'subclass_counts', 'selected',
                         'symbolic_units', 'symbolic_limit', 'symbolic_unit',
                         'inventory_hash_encoding', 'complete_original_profile_execution'))
ITEM_KEYS = frozenset(('global_index', 'subclass', 'schedule'))
ENCODING = 'sha256 newline-delimited compact JSON original schedules'
UNIT_NAME = 'complete-schedule-candidate'
INITIAL_ORDINALS = (0, 1, 288, 289)


class Symbolic:
    """Audit-local enumeration counter; candidate units only, never a model-state charge."""
    def __init__(self, limit):
        require(type(limit) is int and limit >= 0, 'finite explicit symbolic limit')
        self.limit, self.taken = limit, 0

    def take(self, n):
        require(self.taken + n <= self.limit, 'symbolic ceiling before candidate unit')
        self.taken += n


def frame(profile):
    """Re-derived structural proof: original profile is prefix x antichain x suffix."""
    require(type(profile) is dict and len(profile['actions']) == DEPTH
            and len(set(profile['actions'])) == DEPTH, 'full original literal profile')
    prefix, middle, suffix = (tuple(profile['actions'][:PREFIX]),
                              tuple(profile['actions'][PREFIX:SUFFIX]),
                              tuple(profile['actions'][SUFFIX:]))
    require(set(middle) == set((*COLLECTS, OPEN, RESTART, *ATTEMPTS)),
            'unchanged core occurrence set and literal indices')
    for i, action in enumerate(profile['actions']):
        expected = () if i == 0 else (profile['actions'][i - 1],)
        if PREFIX <= i < SUFFIX:
            expected = (prefix[-1],)
        elif i == SUFFIX:
            expected = middle
        require(set(profile['requires'][action]) == set(expected),
                'exact original antichain dependency graph')
    require(tuple(d.s.UNITS) == UNITS and tuple(profile['outcomes']) == (OUTCOME,),
            'unchanged original units and outcome')
    return prefix, tuple(sorted(middle)), suffix


def classify(middle):
    """Independent literal membership: fixed head, one free block, anchored tail sets."""
    if len(middle) != CORE:
        return None
    head, free, tail = middle[0], middle[1:5], middle[5:]
    if set(free) != FREE or len(set(free)) != 4:
        return None
    if head == COLLECTS[0] and tail[0] == OPEN and set(tail[1:]) == TAIL2:
        return 'fresh-incomplete'
    if head == OPEN and set(tail) == ALL3:
        return 'stale-complete'
    return None


def rank(middle, alphabet):
    """Factoradic position of middle among lex orders of the sorted core alphabet."""
    remaining, value = list(alphabet), 0
    for action in middle:
        i = remaining.index(action)
        value += i * factorial(len(remaining) - 1)
        del remaining[i]
    return value


def audit_inventory(frozen, symbolic_limit=40512, expected_producer_limit=40512):
    """Independently recompute and bind every field of the frozen inventory record.

    Charges one symbolic unit before each of the 40320 full candidates and each
    of the 192 permutation-product candidates.  Explores no new S/adapter
    history; inherited planning fixture construction is accounted by the wrapper; rejects a changed whole-inventory digest and any provenance drift.
    """
    require(type(symbolic_limit) is int and symbolic_limit == 40512,
            'exact independent auditor symbolic reservation')
    require(type(frozen) is dict and frozenset(frozen) == FROZEN_KEYS,
            'exact frozen inventory provenance keys')
    require(type(expected_producer_limit) is int and expected_producer_limit == 40512,
            'exact externally admitted producer reservation required')
    symbolic = Symbolic(symbolic_limit)
    before = d.digest(d.s.PROFILES)
    profile = c.domain({'domain': DOMAIN})
    prefix, alphabet, suffix = frame(profile)
    profile_sha = d.digest(profile)

    counts = {name: 0 for name in SUBCLASS_ORDERS}
    audited = []
    whole_hash = hashlib.sha256()
    for index, middle in enumerate(itertools.permutations(alphabet)):
        symbolic.take(1)
        schedule = prefix + middle + suffix
        c.validate_inventory(profile, (schedule,), 1)
        require(rank(middle, alphabet) == index,
                'factoradic global rank equals enumeration position')
        whole_hash.update(json.dumps(schedule, separators=(',', ':')).encode() + b'\n')
        name = classify(middle)
        if name:
            counts[name] += 1
            audited.append(dict(global_index=index, subclass=name, schedule=schedule))
    require(counts == SUBCLASS_ORDERS and len(audited) == SELECTED,
            'independent complete 48+144 membership')

    direct = set()
    for left in itertools.permutations(sorted(FREE)):
        for right in itertools.permutations(sorted(TAIL2)):
            symbolic.take(1)
            direct.add(('fresh-incomplete',
                        prefix + (COLLECTS[0],) + left + (OPEN,) + right + suffix))
        for right in itertools.permutations(sorted(ALL3)):
            symbolic.take(1)
            direct.add(('stale-complete', prefix + (OPEN,) + left + right + suffix))
    require(len(direct) == SELECTED
            and {(x['subclass'], x['schedule']) for x in audited} == direct,
            'identical independent permutation-product membership')
    require(symbolic.taken == WHOLE + SELECTED, 'all40512 charged candidate units')

    for item in audited:
        mid = item['schedule'][PREFIX:SUFFIX]
        require(mid[:4] != (COLLECTS[0], COLLECTS[1], ATTEMPTS[1], ATTEMPTS[2]),
                'disjoint from original packet04 necessary prefix')
        require(not (mid.index(RESTART) < mid.index(OPEN)
                     and all(mid.index(OPEN) < mid.index(a) for a in COLLECTS)),
                'disjoint from packet08 necessary fresh-complete conditions')

    require(frozen['packet'] == PACKET and frozen['domain'] == DOMAIN,
            'frozen inventory packet and domain identity')
    require(frozen['profile_sha256'] == profile_sha, 'frozen original profile digest')
    require(frozen['whole_inventory_sha256'] == whole_hash.hexdigest(),
            'changed whole inventory digest rejected')
    require(type(frozen['orders_per_unit']) is int and frozen['orders_per_unit'] == SELECTED
            and type(frozen['subclass_counts']) is dict
            and set(frozen['subclass_counts']) == set(counts)
            and all(type(v) is int for v in frozen['subclass_counts'].values())
            and frozen['subclass_counts'] == counts, 'frozen declared counts')
    require(type(frozen['symbolic_units']) is int and frozen['symbolic_units'] == WHOLE + SELECTED
            and type(frozen['symbolic_limit']) is int
            and frozen['symbolic_limit'] == expected_producer_limit
            and frozen['symbolic_unit'] == UNIT_NAME, 'frozen charged-work provenance')
    require(frozen['inventory_hash_encoding'] == ENCODING,
            'declared digest encoding matches audited encoding')
    require(frozen['complete_original_profile_execution'] is False,
            'frozen record asserts no original execution')
    require(type(frozen['selected']) is list and len(frozen['selected']) == SELECTED,
            'frozen selected cardinality')
    seen = set()
    for expected, item in zip(audited, frozen['selected']):
        require(type(item) is dict and frozenset(item) == ITEM_KEYS,
                'exact frozen selected provenance keys')
        require(type(item['global_index']) is int
                and item['global_index'] == expected['global_index']
                and item['global_index'] not in seen
                and item['subclass'] == expected['subclass']
                and type(item['schedule']) is list and len(item['schedule']) == DEPTH
                and all(type(x) is str for x in item['schedule'])
                and tuple(item['schedule']) == expected['schedule'],
                'exact frozen membership, subclass and global rank')
        seen.add(item['global_index'])

    flat = [(item, unit) for item in audited for unit in UNITS]
    require(len(flat) == 2 * SELECTED == 384
            and all(flat[2 * i + j] == (audited[i], UNITS[j])
                    for i in range(SELECTED) for j in (0, 1)),
            'complete flat index map: ordinal//2 selects schedule, ordinal%2 selects unit')
    initial = {str(o): dict(global_index=flat[o][0]['global_index'],
                           subclass=flat[o][0]['subclass'], unit=flat[o][1])
               for o in INITIAL_ORDINALS}
    stale = [x['global_index'] for x in audited if x['subclass'] == 'stale-complete']
    fresh = [x['global_index'] for x in audited if x['subclass'] == 'fresh-incomplete']
    require(max(stale) < min(fresh), 'lexicographic class separation of global ranks')
    require(initial['0']['subclass'] == initial['1']['subclass'] == 'stale-complete'
            and initial['288']['subclass'] == initial['289']['subclass'] == 'fresh-incomplete'
            and initial['0']['unit'] == initial['288']['unit'] == 'event'
            and initial['1']['unit'] == initial['289']['unit'] == 'utf8-byte'
            and initial['0']['global_index'] == initial['1']['global_index'] == min(stale)
            and initial['288']['global_index'] == initial['289']['global_index'] == min(fresh),
            'initial ordinals analytically select both classes and both units')
    require(d.digest(d.s.PROFILES) == before,
            'original profile registry unchanged by audit')
    return dict(packet=PACKET, domain=DOMAIN, status='INDEPENDENT_INVENTORY_MATCH',
                profile_sha256=profile_sha,
                whole_inventory_sha256=whole_hash.hexdigest(),
                orders_per_unit=len(audited), subclass_counts=counts,
                total_histories=len(flat), units=list(UNITS), outcome=OUTCOME,
                flat_index_map='selected[ordinal//2] paired with UNITS[ordinal%2]',
                initial_ordinals=initial,
                stale_rank_range=[min(stale), max(stale)],
                fresh_rank_range=[min(fresh), max(fresh)],
                symbolic_units=symbolic.taken, symbolic_limit=symbolic_limit,
                symbolic_unit=UNIT_NAME,
                membership_basis='full40320 enumeration identical to 48+144 permutation product',
                disjoint_from=('packet04-prefix', 'packet08-fresh-complete'),
                source_adapter_histories_executed=0,
                planning_fixture_construction_requires_separate_accounting=True,
                expected_producer_limit=expected_producer_limit,
                complete_original_profile_execution=False,
                source_truth_established=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True,
                        help='Frozen boundary-01 inventory JSON record')
    parser.add_argument('--symbolic-limit', type=int, default=40512)
    parser.add_argument('--expected-producer-limit', type=int, required=True)
    parser.add_argument('--stdout-limit', type=int, default=1048576)
    args = parser.parse_args(argv)
    def deny(event, arguments):
        if event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
            raise RuntimeError('audit network/process operation refused: ' + event)
    sys.addaudithook(deny)
    require(args.inventory.stat().st_size <= 1048576, 'bounded frozen inventory bytes')
    require(1 <= args.stdout_limit <= 1048576, 'qualified stdout bound')
    from research_entry import strict_json
    input_raw = args.inventory.read_bytes()
    frozen = strict_json(input_raw)
    result = audit_inventory(frozen, args.symbolic_limit, args.expected_producer_limit)
    result['inventory_input_sha256'] = hashlib.sha256(input_raw).hexdigest()
    result['auditor_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    payload = json.dumps(result,
                         sort_keys=True, separators=(',', ':'))
    require(len(payload.encode('utf-8')) <= args.stdout_limit, 'single bounded stdout object')
    print(payload)


if __name__ == '__main__':
    main()
