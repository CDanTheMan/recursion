"""boundary-01 retained audit: independent replay of one bounded shard against the frozen inventory.

Public API: audit(frozen, result, expected_indices, charge). ``frozen`` and ``result`` are the exact
decoded JSON objects emitted by boundary.py (--mode inventory / --mode explore); ``expected_indices``
are the exact shard ordinals in emitted order; ``charge`` is a checked counter whose take() is called
once before each selected-inventory member is revalidated and35 units before any case is
decoded/restored/audited (one retained-case-prefix-audit-bundle unit per prefix) (expected charge: len(frozen['selected']) + 35 * len(expected_indices) = 192 + 35n).

This module never imports or calls boundary.py. Subclass membership, factoradic global indices,
selected-member validation, summaries, per-prefix censuses, census totals and attestation
observations are all reconstructed here from the unchanged check.py helpers and from decoded typed
cases. Each certificate is decoded under explicit base64/gzip byte bounds and every prefix is
re-audited by the unchanged check.audit_case. No model reducer runs: replay is over retained typed
states only.

PREREQUISITE - separate inventory provenance auditor. This audit binds the frozen inventory only by
its declared profile/subclass fields, by revalidating the 192 selected members (order validity,
factoradic rank, literal subclass, ascending unique indices, 48/144 counts), and by echoing
whole_inventory_sha256. It does NOT recompute the sha256 newline-delimited digest over all 40320
whole orders. A distinct inventory auditor must first recompute that whole-order digest plus the
direct 192-member construction/ranks/subclass counts under an explicit 40512 symbolic budget, bound
to the exact frozen inventory bytes, before this shard audit is admitted as evidence.
"""
import argparse
import base64
import hashlib
import json
import sys
import zlib
from research_entry import strict_json
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHECK_DIR = 'experiments/v3/eight-hour-research-20260910-01a08a22'
sys.path.insert(0, str(ROOT / CHECK_DIR))
import check as c

d = c.d
r = c.r
t = c.t
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
MAX_B64, MAX_GZIP, MAX_JSON = 1048576, 1048576, 8388608
PROVENANCE_PREREQUISITE = ('separate inventory provenance auditor must recompute the sha256 '
    'newline-delimited whole-order digest over all 40320 orders plus the direct 192-member '
    'construction, ranks and subclass counts under an explicit 40512 symbolic budget, bound to '
    'the exact frozen inventory bytes, before this shard audit is admitted')


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def frame(profile):
    require(len(profile['actions']) == DEPTH and len(set(profile['actions'])) == DEPTH,
            'full original literal profile')
    prefix = tuple(profile['actions'][:PREFIX])
    middle = tuple(profile['actions'][PREFIX:SUFFIX])
    suffix = tuple(profile['actions'][SUFFIX:])
    require(set(middle) == set((*COLLECTS, OPEN, RESTART, *ATTEMPTS)),
            'unchanged core occurrence set and literal indices')
    for i, action in enumerate(profile['actions']):
        expected = () if i == 0 else (profile['actions'][i - 1],)
        if PREFIX <= i < SUFFIX:
            expected = (prefix[-1],)
        elif i == SUFFIX:
            expected = middle
        require(set(profile['requires'][action]) == set(expected), 'exact original antichain graph')
    require(tuple(d.s.UNITS) == UNITS and tuple(profile['outcomes']) == (OUTCOME,),
            'unchanged original units and outcome')
    return prefix, tuple(sorted(middle)), suffix


def subclass_of(middle):
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
    remaining, value = list(alphabet), 0
    for action in middle:
        i = remaining.index(action)
        value += i * factorial(len(remaining) - 1)
        del remaining[i]
    return value


def order_ok(profile, schedule):
    if len(schedule) != DEPTH or set(schedule) != set(profile['actions']):
        return False
    done = set()
    for action in schedule:
        if action in done or not set(profile['requires'][action]) <= done:
            return False
        done.add(action)
    return True


def selected_membership(frozen, profile, charge):
    """Revalidate the frozen 192-member selection; the 40320-order digest is NOT recomputed here."""
    require(type(frozen) is dict and frozen.get('packet') == PACKET and frozen.get('domain') == DOMAIN,
            'frozen inventory identity')
    require(type(frozen.get('whole_inventory_sha256')) is str
            and len(frozen['whole_inventory_sha256']) == 64
            and frozen.get('profile_sha256') == d.digest(profile)
            and frozen.get('orders_per_unit') == 192
            and frozen.get('subclass_counts') == SUBCLASS_ORDERS, 'declared inventory fields')
    require(type(frozen.get('selected')) is list and len(frozen['selected']) == 192
            and frozen.get('symbolic_units') == WHOLE + 192
            and type(frozen.get('symbolic_limit')) is int
            and frozen['symbolic_limit'] == WHOLE + 192, 'declared inventory shape and budget')
    prefix, alphabet, suffix = frame(profile)
    selected, counts, previous = [], {name: 0 for name in PATTERNS}, -1
    for item in frozen['selected']:
        charge.take(1)
        require(type(item) is dict and type(item.get('global_index')) is int
                and type(item.get('subclass')) is str and type(item.get('schedule')) is list,
                'frozen selected member shape')
        schedule = tuple(item['schedule'])
        require(order_ok(profile, schedule), 'selected schedule is a complete original order')
        require(schedule[:PREFIX] == prefix and schedule[SUFFIX:] == suffix
                and sorted(schedule[PREFIX:SUFFIX]) == list(alphabet), 'fixed prefix/suffix frame')
        index = rank(schedule[PREFIX:SUFFIX], alphabet)
        name = subclass_of(schedule[PREFIX:SUFFIX])
        require(name is not None and index == item['global_index'] and index > previous
                and name == item['subclass'], 'exact unique rank and literal subclass membership')
        counts[name] += 1
        previous = index
        selected.append(dict(global_index=index, subclass=name, schedule=schedule))
    require(counts == SUBCLASS_ORDERS, 'complete frozen subclass counts')
    return selected


def typed_certificate(item):
    """Bounded base64+gzip decode to a typed case via unchanged codec/artifact only."""
    require(type(item) is dict and type(item.get('artifact')) is str
            and type(item.get('artifact_sha256')) is str
            and type(item.get('certificate_gzip_base64')) is str
            and len(item['certificate_gzip_base64']) <= MAX_B64, 'bounded certificate envelope')
    try:
        raw = base64.b64decode(item['certificate_gzip_base64'], validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError('certificate base64 decode') from error
    require(len(raw) <= MAX_GZIP
            and hashlib.sha256(raw).hexdigest() == item['artifact_sha256'],
            'exact certificate bytes and sha256 binding')
    try:
        stream = zlib.decompressobj(31)
        body = stream.decompress(raw, MAX_JSON + 1)
        # No flush: reject overflow/truncation before any additional expansion.
        require(len(body) <= MAX_JSON and not stream.unconsumed_tail,
                'certificate expansion exceeds bound')
    except zlib.error as error:
        raise ValueError('certificate gzip decode') from error
    require(len(body) <= MAX_JSON and stream.eof and not stream.unconsumed_tail
            and stream.unused_data == b'', 'bounded complete certificate stream')
    return c.artifact.decode(c.codec.unpack(strict_json(body)))


def census(case, prefixes, charge):
    """Independent per-prefix census: actual Q core/journal generation, invocations and masks."""
    adapters = t.restore(case['adapter'])
    sources = t.restore(case['source'])
    require(len(adapters) == len(sources) == len(prefixes) == DEPTH + 1,
            'complete restored prefix sequence')
    rows = []
    for i, state in enumerate(adapters):
        source = sources[i]  # Entire case-prefix audit bundle was precharged.
        row = dict(prefix=i, action=None, q_invoked=None, responses_related=None,
                   decision=state['decision'], invocations=len(state['invocations']),
                   done=state['done'], core_done=state['core']['done'],
                   source_generation=c.artifact.encode(source['source_generation']),
                   source_core_generation_equal=d.exact(source['source_generation'],
                                                        state['core']['source_generation']),
                   source_journal_generation_equal=d.exact(source['source_generation'],
                                                           state['journal']['source_generation']),
                   exact_common_field_differences=[key for key in r.FIELDS
                       if not d.exact(source[key], state['core'][key])],
                   q_core_generation=c.artifact.encode(state['core']['source_generation']),
                   journal_generation=c.artifact.encode(state['journal']['source_generation']),
                   journal_sha256=d.digest(state['journal']),
                   strict_related=prefixes[i]['strict_related'],
                   related=prefixes[i]['related'],
                   differing_journal_fields=prefixes[i]['differing_journal_fields'])
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
                key = canon(row[field])
                slot[field][key] = slot[field].get(key, 0) + 1
    return out


def summarize(case, prefixes):
    rows = case['rows']
    return dict(case=case['case'], schedule=list(case['source']['actions']),
        strict_complete=all(x['strict_related'] for x in prefixes)
            and all(x['responses_related'] for x in rows),
        extended_complete=all(x['related'] for x in prefixes)
            and all(x['responses_related'] for x in rows),
        visible_events=len(rows), matching_responses=sum(x['responses_related'] for x in rows),
        matching_journals=sum(not x['differing_journal_fields'] for x in prefixes[1:]),
        identity_poststates=sum(x['staged_rule'] == 'original-object-identity' for x in prefixes[1:]),
        strict_first_gap=next((i for i, x in enumerate(prefixes)
            if not x['strict_related'] or (i and not rows[i - 1]['responses_related'])), None),
        extended_first_gap=next((i for i, x in enumerate(prefixes)
            if not x['related'] or (i and not rows[i - 1]['responses_related'])), None),
        decisions=[x['source_observation']['decision'] for x in rows],
        original_profile_sha256=d.digest(case['source']['profile']))


def attestation(case, label):
    """Independent attestation observation; completeness compares (index, original record bytes)."""
    sources = t.restore(case['source'])
    adapters = t.restore(case['adapter'])
    index = next(i for i, a in enumerate(case['source']['actions'])
                 if a.split('@')[0] == 'source-attest')
    source, journal, core = sources[index], adapters[index]['journal'], adapters[index]['core']
    def facts(state, name):
        records = ()
        if name:
            try:
                records = d.s.records(name)
            except (KeyError, TypeError, IndexError):
                records = None
        require(records is not None or not state['collected'], 'known original record registry')
        for i, record in state['collected']:
            require(type(i) is int and 0 <= i < len(records or ())
                    and d.exact(record, (records or ())[i]),
                    'actual collected index and original record bytes equality')
        capture = state['collection']
        return dict(capture=c.artifact.encode(capture),
                    live_generation=c.artifact.encode(state['source_generation']),
                    live_revision=state['source_revision'],
                    attempts=c.artifact.encode(state['attempts']),
                    collected_indices=[i for i, _ in state['collected']],
                    collected_sha256=d.digest(state['collected']),
                    current_capture=bool(capture and d.exact(capture[:2],
                        (state['source_generation'], state['source_revision']))))
    actual = case['rows'][index]
    predicted = 'source-attest:' + ('incomplete-inventory' if label == 'fresh-incomplete'
                                  else 'stale-collection')
    return dict(case=case['case'], chronological_index=index, subclass=label,
                source=facts(source, source['cut_delivery']),
                adapter_journal=facts(journal, core['cut_delivery']),
                source_decision=actual['source_observation']['decision'],
                adapter_decision=actual['adapter_observation']['decision'],
                q_invoked=actual['q_invoked'], predicted_decision=predicted,
                prediction_matches=actual['source_observation']['decision'] ==
                    actual['adapter_observation']['decision'] == predicted
                    and not actual['q_invoked'])


def audit(frozen, result, expected_indices, charge, inventory_sha256):
    require(type(expected_indices) is list and 0 < len(expected_indices) <= 24
            and all(type(i) is int and 0 <= i < 384 for i in expected_indices)
            and len(set(expected_indices)) == len(expected_indices),
            'finite distinct exact shard identities')
    before = charge.visits
    profile = c.domain({'domain': DOMAIN})
    selected = selected_membership(frozen, profile, charge)
    flat = [(sel, unit) for sel in selected for unit in UNITS]
    n = len(expected_indices)
    expected_keys = set(('packet domain status history_indices histories total_histories '
        'symbolic_units symbolic_limit state_visits state_limit profile_sha256 '
        'whole_inventory_sha256 inventory_input_sha256 subclass_counts cases summaries prefix_censuses '
        'prefix_census_totals attestation_observations prediction_matches strict_gaps '
        'extended_gaps predicted_acceptance_asserted complete_domain reductions_used '
        'source_truth_established').split())
    require(type(result) is dict and set(result) == expected_keys, 'exact shard result keys')
    for key in ('histories', 'total_histories', 'symbolic_units', 'symbolic_limit',
                'state_visits', 'state_limit'):
        require(type(result[key]) is int, 'exact integer shard field: ' + key)
    require(type(result['history_indices']) is list
            and all(type(v) is int for v in result['history_indices']), 'typed shard ordinals')
    require(type(result['prediction_matches']) is bool, 'typed aggregate verdict')
    require(type(inventory_sha256) is str and len(inventory_sha256) == 64
            and result['inventory_input_sha256'] == inventory_sha256,
            'exact producer inventory input bytes')
    for key in ('strict_gaps', 'extended_gaps'):
        require(type(result[key]) is list and len(result[key]) == n
                and all(v is None or type(v) is int and 0 <= v <= DEPTH for v in result[key]),
                'typed gap ordinals')
    require(type(result) is dict and result.get('packet') == PACKET
            and result.get('domain') == DOMAIN
            and result.get('status') == 'BOUNDED_PARTIAL_SHARD', 'shard result identity')
    require(result.get('history_indices') == expected_indices and result.get('histories') == n
            and result.get('total_histories') == len(flat), 'exact shard cardinalities')
    require(result.get('state_visits') == 2 * (DEPTH + 1) * n == result.get('state_limit'),
            'exact actual representation visits and reservation')
    require(result.get('symbolic_units') == len(selected)
            and type(result.get('symbolic_limit')) is int
            and result['symbolic_limit'] == len(selected)
            and result.get('profile_sha256') == frozen.get('profile_sha256') == d.digest(profile)
            and result.get('whole_inventory_sha256') == frozen.get('whole_inventory_sha256')
            and result.get('subclass_counts') == frozen.get('subclass_counts') == SUBCLASS_ORDERS,
            'frozen inventory fields echoed consistently')
    for flag in ('predicted_acceptance_asserted', 'complete_domain', 'reductions_used',
                 'source_truth_established'):
        require(result.get(flag) is False, 'no overstated claim flag: ' + flag)
    cases, summaries = result.get('cases'), result.get('summaries')
    claimed_censuses, claimed_obs = result.get('prefix_censuses'), result.get('attestation_observations')
    require(type(cases) is type(summaries) is type(claimed_censuses) is type(claimed_obs) is list
            and len(cases) == len(summaries) == len(claimed_censuses) == len(claimed_obs) == n,
            'exact per-history result sections')
    audited_prefixes = 0
    censuses, rebuilt_summaries, observations = [], [], []
    per_case, mismatches = [], []
    for position, ordinal in enumerate(expected_indices):
        sel, unit = flat[ordinal]
        gi, label, schedule = sel['global_index'], sel['subclass'], sel['schedule']
        name = PACKET + '/' + str(gi).zfill(6) + '/' + unit + '/' + str(OUTCOME)
        info = cases[position]
        require(type(info) is dict and set(info) ==
                {'artifact', 'artifact_sha256', 'certificate_gzip_base64'}, 'exact case envelope')
        # One unit per prefix covers this complete retained-case audit bundle:
        # typed restoration, unchanged audit_case, census, summary and observations.
        # It is not a count of primitive operations or newly explored model states.
        charge.take(DEPTH + 1)
        require(info.get('artifact') == str(ordinal).zfill(6) + '.json.gz',
                'exact ordinal artifact filename')
        case = typed_certificate(info)
        require(type(case) is dict and set(case) ==
                {'case', 'unit', 'outcome', 'source', 'adapter', 'rows',
                 'incarnation_pairs', 'prefixes'}, 'exact decoded case keys')
        require(type(case['source']) is dict and set(case['source']) ==
                {'side', 'initial', 'profile', 'actions', 'events'}
                and type(case['adapter']) is dict and set(case['adapter']) ==
                {'side', 'initial', 'profile', 'q_profile', 'actions', 'events'},
                'exact decoded trace keys')
        require(case.get('case') == name and case.get('unit') == unit
                and case.get('outcome') == OUTCOME
                and type(case.get('outcome')) is int
                and type(case['source']['actions']) is tuple
                and type(case['adapter']['actions']) is tuple
                and d.exact(case['source']['actions'], schedule)
                and d.exact(case['adapter']['actions'], schedule)
                and d.exact(case['source']['profile'], case['adapter']['profile'])
                and d.exact(case['source']['profile'], profile),
                'decoded case identity, schedule and original profile')
        require(type(case['rows']) is list and len(case['rows']) == DEPTH
                and type(case['prefixes']) is list and len(case['prefixes']) == DEPTH + 1
                and type(case['source']['events']) is list and len(case['source']['events']) == DEPTH
                and type(case['adapter']['events']) is list and len(case['adapter']['events']) == DEPTH,
                'exact visible events, comparison rows and prefixes')
        prefixes = c.audit_case(case)
        require(d.exact(prefixes, case['prefixes']), 'independent typed replay of every prefix')
        audited_prefixes += len(prefixes)
        rows = census(case, prefixes, charge)
        require(canon(rows) == canon(claimed_censuses[position]),
                'independently reconstructed prefix census')
        censuses.append(rows)
        summary = summarize(case, prefixes)
        summary.update(artifact=info['artifact'], artifact_sha256=info['artifact_sha256'],
                       global_index=gi, subclass=label, unit=unit, outcome=OUTCOME)
        require(canon(summary) == canon(summaries[position]),
                'independently reconstructed summary')
        rebuilt_summaries.append(summary)
        observation = attestation(case, label)
        require(canon(observation) == canon(claimed_obs[position]),
                'independently reconstructed attestation observation')
        observations.append(observation)
        if not observation['prediction_matches']:
            mismatches.append(dict(case=name, ordinal=ordinal,
                                   chronological_index=observation['chronological_index'],
                                   predicted_decision=observation['predicted_decision'],
                                   source_decision=observation['source_decision'],
                                   adapter_decision=observation['adapter_decision'],
                                   q_invoked=observation['q_invoked']))
        per_case.append(dict(ordinal=ordinal, artifact=info['artifact'],
                             artifact_sha256=info['artifact_sha256'], global_index=gi,
                             subclass=label, unit=unit, outcome=OUTCOME, case=name,
                             prefixes=len(prefixes)))
    require(canon(tally(censuses)) == canon(result.get('prefix_census_totals')),
            'independent census totals')
    require(result.get('strict_gaps') == [s['strict_first_gap'] for s in rebuilt_summaries]
            and result.get('extended_gaps') == [s['extended_first_gap'] for s in rebuilt_summaries],
            'exact first-gap ordinal lists')
    require(result.get('prediction_matches') == all(o['prediction_matches'] for o in observations),
            'aggregate attestation prediction verdict')
    require(charge.visits - before == len(selected) + (DEPTH + 1) * n,
            'actual checked audit counter delta')
    return dict(packet=PACKET, domain=DOMAIN, auditor='boundary-retained-auditor',
        prerequisite_inventory_provenance_audit=PROVENANCE_PREREQUISITE,
        inventory_binding=dict(profile_sha256=d.digest(profile),
            whole_inventory_sha256_echo=frozen['whole_inventory_sha256'],
            selected_membership_revalidated=len(selected), whole_order_digest_recomputed=False),
        ordinals=expected_indices, histories=n, audited_prefixes=audited_prefixes,
        charged_units=charge.visits - before,
        charged_unit='selected-inventory-member or retained-case-prefix-audit-bundle',
        cases=per_case, prediction_mismatches=mismatches,
        negative_control_witnesses=[],
        negative_control_execution='separately owned runner required; producer claims not accepted',
        model_execution='none; unchanged check.audit_case typed replay only')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, required=True,
                        help='Decoded frozen inventory JSON from boundary.py --mode inventory')
    parser.add_argument('--result', type=Path, required=True,
                        help='Decoded shard JSON from boundary.py --mode explore')
    parser.add_argument('--indices', required=True,
                        help='Exact comma-separated frozen history ordinals in emitted order')
    parser.add_argument('--charge-limit', type=int, required=True)
    parser.add_argument('--stdout-limit', type=int, default=1048576)
    args = parser.parse_args(argv)
    def deny(event, arguments):
        if event.startswith(('socket.', 'subprocess.')) or event in ('os.system', 'os.posix_spawn'):
            raise RuntimeError('audit network/process operation refused: ' + event)
    sys.addaudithook(deny)
    require(1 <= args.stdout_limit <= 1048576, 'qualified stdout bound')
    input_raw = args.inventory.read_bytes()
    result_raw = args.result.read_bytes()
    require(len(input_raw) <= 1048576 and len(result_raw) <= 1048576,
            'bounded audit input bytes')
    frozen = strict_json(input_raw)
    result = strict_json(result_raw)
    indices = [int(x) for x in args.indices.split(',')]
    require(args.charge_limit == len(frozen['selected']) + (DEPTH + 1) * len(indices),
            'exact retained-audit reservation')
    inventory_sha = hashlib.sha256(input_raw).hexdigest()
    report = audit(frozen, result, indices, c.Counter(args.charge_limit), inventory_sha)
    report['inventory_bytes_sha256'] = hashlib.sha256(input_raw).hexdigest()
    report['result_bytes_sha256'] = hashlib.sha256(result_raw).hexdigest()
    report['auditor_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    payload = json.dumps(report, sort_keys=True, separators=(',', ':'))
    require(len(payload.encode('utf-8')) <= args.stdout_limit, 'bounded audit stdout object')
    print(payload)


if __name__ == '__main__':
    main()
