"""boundary-01 bounded proposal: fresh-incomplete/stale-complete subclasses of the frozen
scale domain. Execution requires the separate exact admission envelope. Reuses the unchanged earlier checker for
profiles, inventory validation, histories, audits and typed certificates; adds literal
subclass membership, analytic factoradic global indices, an independent symbolic
40320-order enumeration, per-prefix censuses and one bounded base64 JSON stdout export.
"""
import argparse
import base64
import gzip
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
PATTERNS = {
    'fresh-incomplete': (COLLECTS[0], FREE, FREE, FREE, FREE, OPEN, TAIL2, TAIL2),
    'stale-complete': (OPEN, FREE, FREE, FREE, FREE, ALL3, ALL3, ALL3),
}
SUBCLASS_ORDERS = {'fresh-incomplete': factorial(4) * factorial(2),
                   'stale-complete': factorial(4) * factorial(3)}
CENSUS_FIELDS = ('decision', 'q_invoked', 'responses_related', 'strict_related', 'related',
                 'differing_journal_fields', 'invocations', 'done', 'core_done', 'journal_sha256',
                 'source_generation', 'q_core_generation', 'journal_generation',
                 'source_core_generation_equal', 'source_journal_generation_equal',
                 'exact_common_field_differences')


class Symbolic:
    """Checked counter for enumeration work only; never a model-state charge."""
    def __init__(self, limit):
        require(type(limit) is int and limit >= 0, 'finite explicit symbolic limit')
        self.limit, self.taken = limit, 0
    def take(self, n):
        require(self.taken + n <= self.limit, 'symbolic ceiling before enumeration step')
        self.taken += n


def frame(profile):
    require(len(profile['actions']) == DEPTH and len(set(profile['actions'])) == DEPTH,
            'full original literal profile')
    prefix, middle, suffix = (profile['actions'][:PREFIX], profile['actions'][PREFIX:SUFFIX],
                              profile['actions'][SUFFIX:])
    require(set(middle) == set((*COLLECTS, OPEN, RESTART, *ATTEMPTS)),
            'unchanged core occurrence set and literal indices')
    # This exact graph proves the original inventory is prefix x permutations(core) x suffix.
    for i, action in enumerate(profile['actions']):
        expected = (() if i == 0 else (profile['actions'][i - 1],))
        if PREFIX <= i < SUFFIX:
            expected = (prefix[-1],)
        elif i == SUFFIX:
            expected = middle
        require(set(profile['requires'][action]) == set(expected), 'exact original antichain graph')
    require(tuple(d.s.UNITS) == UNITS and tuple(profile['outcomes']) == (OUTCOME,),
            'unchanged original units and outcome')
    return prefix, tuple(sorted(middle)), suffix


def subclass(middle):
    """Literal spec subclass of one core order, or None."""
    if len(middle) != CORE:
        return None
    for name, pattern in PATTERNS.items():
        used = set()
        for want, got in zip(pattern, middle):
            if type(want) is str:
                if got != want:
                    break
            elif got in want and got not in used:
                used.add(got)
            else:
                break
        else:
            return name
    return None


def rank(middle, alphabet):
    """Factoradic lex index of middle among all orders of the sorted core alphabet."""
    remaining, value = list(alphabet), 0
    for action in middle:
        i = remaining.index(action)
        value += i * factorial(len(remaining) - 1)
        del remaining[i]
    return value


def global_index(profile, schedule):
    """Original lexicographic index of a complete 34-action order, computed analytically."""
    prefix, alphabet, suffix = frame(profile)
    require(tuple(schedule[:PREFIX]) == prefix and tuple(schedule[SUFFIX:]) == suffix
            and sorted(schedule[PREFIX:SUFFIX]) == list(alphabet),
            'complete order over the full original profile')
    return rank(tuple(schedule[PREFIX:SUFFIX]), alphabet)


def orders(profile, symbolic):
    """Independent lex enumeration of all core orders inside the fixed prefix/suffix."""
    prefix, alphabet, suffix = frame(profile)
    for middle in itertools.permutations(alphabet):
        symbolic.take(1)
        yield prefix + middle + suffix


def inventory(profile, symbolic_limit):
    """One charged full-order pass plus a separate charged direct192-order construction.

    Unit: one complete34-occurrence candidate construction/validation/classification,
    including bounded dependency checks and eight-element factoradic ranking.
    Sorting, bounded scalar comparisons, hashing and serialization are overhead;
    there is no uninstrumented second enumerator or dynamic-programming call.
    """
    symbolic = Symbolic(symbolic_limit)
    prefix, alphabet, suffix = frame(profile)
    selected, counts = [], {name: 0 for name in PATTERNS}
    whole_hash = hashlib.sha256()
    for index, middle in enumerate(itertools.permutations(alphabet)):
        symbolic.take(1)
        schedule = prefix + middle + suffix
        c.validate_inventory(profile, (schedule,), 1)
        require(rank(middle, alphabet) == index, 'independent lex index versus factoradic rank')
        whole_hash.update(json.dumps(schedule, separators=(',', ':')).encode() + b'\n')
        name = subclass(middle)
        if name:
            counts[name] += 1
            selected.append(dict(global_index=index, subclass=name, schedule=schedule))
    # Independent construction does not call subclass() for membership.
    direct = []
    for left in itertools.permutations((*ATTEMPTS, RESTART)):
        for right in itertools.permutations(COLLECTS[1:]):
            symbolic.take(1)
            direct.append(('fresh-incomplete', prefix + (COLLECTS[0],) + left + (OPEN,) + right + suffix))
        for right in itertools.permutations(COLLECTS):
            symbolic.take(1)
            direct.append(('stale-complete', prefix + (OPEN,) + left + right + suffix))
    require(counts == SUBCLASS_ORDERS and len(selected) == len(direct) == 192,
            'independent48+144 complete membership')
    require({(x['subclass'], x['schedule']) for x in selected} == set(direct),
            'exact equality with independent permutation-product construction')
    # Existing packet04 begins C0,C1,A3,A4; packet08 requires R before O and allC afterO.
    # These necessary original membership conditions suffice to prove disjointness here.
    for item in selected:
        mid = item['schedule'][PREFIX:SUFFIX]
        require(mid[:4] != (COLLECTS[0], COLLECTS[1], ATTEMPTS[1], ATTEMPTS[2]),
                'disjoint from original packet04 necessary prefix')
        require(not (mid.index(RESTART) < mid.index(OPEN) and
                     all(mid.index(OPEN) < mid.index(a) for a in COLLECTS)),
                'disjoint from packet08 necessary fresh-complete conditions')
    require(symbolic.taken == WHOLE + 192, 'all40512 declared symbolic candidate units')
    return dict(packet=PACKET, domain=DOMAIN, profile_sha256=d.digest(profile),
                whole_inventory_sha256=whole_hash.hexdigest(), orders_per_unit=192,
                subclass_counts=counts, selected=selected, symbolic_units=symbolic.taken,
                symbolic_limit=symbolic_limit, symbolic_unit='complete-schedule-candidate',
                inventory_hash_encoding='sha256 newline-delimited compact JSON original schedules',
                complete_original_profile_execution=False)


def validate_frozen(frozen, profile, symbolic_limit):
    symbolic = Symbolic(symbolic_limit)
    require(frozen['packet'] == PACKET and frozen['domain'] == DOMAIN and
            frozen['profile_sha256'] == d.digest(profile), 'frozen inventory profile identity')
    require(frozen['orders_per_unit'] == 192 and frozen['subclass_counts'] == SUBCLASS_ORDERS,
            'complete declared inventory counts')
    require(len(frozen['selected']) == 192 and frozen['symbolic_units'] == WHOLE + 192,
            'exact prevalidated inventory shape and generator work')
    selected, seen, counts = [], set(), {name: 0 for name in PATTERNS}
    for item in frozen['selected']:
        symbolic.take(1)
        schedule = tuple(item['schedule'])
        c.validate_inventory(profile, (schedule,), 1)
        index = global_index(profile, schedule)
        name = subclass(schedule[PREFIX:SUFFIX])
        require(type(item['global_index']) is int and index == item['global_index'] and
                index not in seen and name is not None and name == item['subclass'],
                'exact unique original index and subclass membership')
        seen.add(index); counts[name] += 1
        selected.append(dict(global_index=index, subclass=name, schedule=schedule))
    require(counts == SUBCLASS_ORDERS and [x['global_index'] for x in selected] == sorted(seen),
            'complete ordered frozen membership')
    return selected, symbolic.taken


def certificate(case):
    """Deterministic typed gzip certificate, replayed through unchanged audit_case."""
    packed = c.codec.pack(c.artifact.encode(case))
    raw = gzip.compress(json.dumps(packed, sort_keys=True, separators=(',', ':')).encode(),
                        compresslevel=6, mtime=0)
    restored = c.artifact.decode(c.codec.unpack(json.loads(gzip.decompress(raw))))
    require(d.exact(restored, case) and d.exact(c.audit_case(restored), case['prefixes']),
            'deterministic typed certificate replays every audited prefix')
    return raw


def prefix_census(case):
    """Per-prefix actual Q core/journal generation, outer response, invocation and masks."""
    states = c.t.restore(case['adapter'])
    source_states = c.t.restore(case['source'])
    require(len(states) == len(case['prefixes']) == DEPTH + 1, 'complete per-prefix census')
    rows = []
    for i, state in enumerate(states):
        source = source_states[i]
        row = dict(prefix=i, action=None, q_invoked=None, responses_related=None,
                   decision=state['decision'], invocations=len(state['invocations']),
                   done=state['done'], core_done=state['core']['done'],
                   source_generation=c.artifact.encode(source['source_generation']),
                   source_core_generation_equal=d.exact(source['source_generation'], state['core']['source_generation']),
                   source_journal_generation_equal=d.exact(source['source_generation'], state['journal']['source_generation']),
                   exact_common_field_differences=[key for key in c.r.FIELDS
                       if not d.exact(source[key], state['core'][key])],
                   q_core_generation=c.artifact.encode(state['core']['source_generation']),
                   journal_generation=c.artifact.encode(state['journal']['source_generation']),
                   journal_sha256=d.digest(state['journal']),
                   strict_related=case['prefixes'][i]['strict_related'],
                   related=case['prefixes'][i]['related'],
                   differing_journal_fields=case['prefixes'][i]['differing_journal_fields'])
        if i:
            event = case['rows'][i - 1]
            row.update(action=event['source_action'], q_invoked=event['q_invoked'],
                       responses_related=event['responses_related'])
        rows.append(row)
    return rows


def tally(censuses):
    out = {}
    for rows in censuses:
        for row in rows:
            slot = out.setdefault(str(row['prefix']), {field: {} for field in CENSUS_FIELDS})
            for field in CENSUS_FIELDS:
                key = json.dumps(row[field], sort_keys=True, separators=(',', ':'))
                slot[field][key] = slot[field].get(key, 0) + 1
    return out


def attestation_observation(case, label):
    ss, aa = c.t.restore(case['source']), c.t.restore(case['adapter'])
    index = next(i for i, a in enumerate(case['source']['actions']) if a.split('@')[0] == 'source-attest')
    source, journal = ss[index], aa[index]['journal']
    def facts(state):
        capture = state['collection']
        return dict(capture=c.artifact.encode(capture),
                    live_generation=c.artifact.encode(state['source_generation']),
                    live_revision=state['source_revision'], attempts=c.artifact.encode(state['attempts']),
                    collected_indices=[i for i, _ in state['collected']],
                    collected_sha256=d.digest(state['collected']),
                    current_capture=bool(capture and d.exact(capture[:2],
                        (state['source_generation'], state['source_revision']))))
    actual = case['rows'][index]
    predicted = 'source-attest:' + ('incomplete-inventory' if label == 'fresh-incomplete' else 'stale-collection')
    return dict(case=case['case'], chronological_index=index, subclass=label,
                source=facts(source), adapter_journal=facts(journal),
                source_decision=actual['source_observation']['decision'],
                adapter_decision=actual['adapter_observation']['decision'],
                q_invoked=actual['q_invoked'], predicted_decision=predicted,
                prediction_matches=actual['source_observation']['decision'] ==
                    actual['adapter_observation']['decision'] == predicted and not actual['q_invoked'])


def explore(frozen, indices, state_limit, symbolic_limit, stdout_limit):
    """One exact shard of the 384 frozen histories under a checked c.Counter."""
    profile = c.domain({'domain': DOMAIN})
    selected, symbolic_units = validate_frozen(frozen, profile, symbolic_limit)
    flat = [(sel, unit) for sel in selected for unit in UNITS]
    require(type(indices) is list and 0 < len(indices) <= 24 and
            all(type(i) is int and 0 <= i < len(flat) for i in indices) and
            len(set(indices)) == len(indices), 'finite distinct exact shard identities')
    require(type(state_limit) is int and state_limit == 70 * len(indices),
            'whole-shard reservation checked before any model initialization')
    before = d.digest(d.s.PROFILES)
    counter, cases, summaries, censuses = c.Counter(state_limit), [], [], []
    observations = []
    for ordinal in indices:
        sel, unit = flat[ordinal]
        require(global_index(profile, sel['schedule']) == sel['global_index'],
                'analytic global-index binding')
        name = PACKET + '/' + str(sel['global_index']).zfill(6) + '/' + unit + '/' + str(OUTCOME)
        case = c.run_history(profile, sel['schedule'], unit, OUTCOME, name, counter)
        raw = certificate(case)
        artifact = str(ordinal).zfill(6) + '.json.gz'
        cases.append(dict(artifact=artifact, artifact_sha256=hashlib.sha256(raw).hexdigest(),
                          certificate_gzip_base64=base64.b64encode(raw).decode('ascii')))
        censuses.append(prefix_census(case))
        summary = c.summarize(case)
        summary.update(artifact=artifact, artifact_sha256=cases[-1]['artifact_sha256'],
                       global_index=sel['global_index'], subclass=sel['subclass'],
                       unit=unit, outcome=OUTCOME)
        summaries.append(summary)
        observations.append(attestation_observation(case, sel['subclass']))
    require(counter.visits == 2 * (DEPTH + 1) * len(indices), 'exact actual representation visits')
    require(d.digest(d.s.PROFILES) == before, 'original profile registry unchanged')
    result = dict(packet=PACKET, domain=DOMAIN, status='BOUNDED_PARTIAL_SHARD',
                  history_indices=indices, histories=len(indices), total_histories=len(flat),
                  symbolic_units=symbolic_units, symbolic_limit=symbolic_limit,
                  state_visits=counter.visits, state_limit=state_limit,
                  profile_sha256=frozen['profile_sha256'],
                  whole_inventory_sha256=frozen['whole_inventory_sha256'],
                  subclass_counts=frozen['subclass_counts'], cases=cases, summaries=summaries,
                  prefix_censuses=censuses, prefix_census_totals=tally(censuses),
                  attestation_observations=observations,
                  prediction_matches=all(x['prediction_matches'] for x in observations),
                  strict_gaps=[row['strict_first_gap'] for row in summaries],
                  extended_gaps=[row['extended_first_gap'] for row in summaries],
                  predicted_acceptance_asserted=False, complete_domain=False,
                  reductions_used=False, source_truth_established=False)
    payload = json.dumps(result, sort_keys=True, separators=(',', ':'))
    require(len(payload.encode('utf-8')) <= stdout_limit, 'single bounded stdout object')
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('inventory', 'explore'), required=True)
    parser.add_argument('--symbolic-limit', type=int, required=True)
    parser.add_argument('--inventory', type=Path)
    parser.add_argument('--indices', help='Exact comma-separated frozen history ordinals')
    parser.add_argument('--state-limit', type=int)
    parser.add_argument('--stdout-limit', type=int, default=1048576)
    args = parser.parse_args(argv)
    def deny(event, arguments):
        if event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
            raise RuntimeError('model network/process operation refused: ' + event)
    sys.addaudithook(deny)
    require(1 <= args.stdout_limit <= 1048576, 'qualified stdout bound')
    if args.mode == 'explore':
        require(args.inventory is not None and args.indices and args.state_limit is not None,
                'frozen retained inventory, exact identities and state reservation')
        require(args.inventory.stat().st_size <= 1048576, 'bounded frozen inventory bytes')
        frozen = json.loads(args.inventory.read_text())
        indices = [int(x) for x in args.indices.split(',')]
        print(explore(frozen, indices, args.state_limit, args.symbolic_limit, args.stdout_limit))
    else:
        require(args.inventory is None and args.indices is None and args.state_limit is None,
                'symbolic inventory mode executes no model histories')
        payload = json.dumps(inventory(c.domain({'domain': DOMAIN}), args.symbolic_limit),
                             sort_keys=True, separators=(',', ':'))
        require(len(payload.encode()) <= args.stdout_limit, 'bounded inventory stdout')
        print(payload)


if __name__ == '__main__':
    main()
