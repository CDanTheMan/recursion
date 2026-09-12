"""boundary-01 owned control entry v2: runpy driver for boundary_controls.

PROPOSED SOURCE ONLY.  This module is not admitted for execution and asserts
no scientific approval, no control result and no ledger acceptance.  It exists
because boundary_controls.py deliberately refuses to run as __main__; under
the unchanged research_entry.py runpy contract this module supplies the four
concrete callables that run_controls requires, so one admitted controller
phase can bind one complete fixed control suite to one durable reservation.

V2 REPAIR over the recovered, rejected control_entry.py:
  * The controller-owned durable reservation receipt is MANDATORY.  It is a
    mounted, bounded (<=64KiB), read-only, canonical-JSON file whose exact
    bytes are pinned by --durable-receipt-sha256.  The optional argv-only
    durability path is removed: omission or any byte drift is a hard
    refusal, so DURABLY_PRECHARGED can no longer be produced from argv
    alone.
  * The receipt is hash-bound end to end.  It must carry the reservation
    ordinal, previous_total/reserved_units/new_total with exact arithmetic,
    the previous ledger row hash (null iff ordinal 0), the exact candidate
    commit, the policy sha256, the phase manifest sha256, this suite's
    control-plan sha256, a unique attempt identity and the sha256 of the
    receipt-producing controller source.  ``refundable`` must be exactly
    JSON false and ``retry_of`` must be null, so refundable or retryable
    semantics cannot be represented by any accepted receipt.
  * The duplicate research_entry import is removed; strict_json and
    canonical_bytes come from the pinned boundary_controls module.
  * Additive accounting stays UNRESOLVED: the runner's local precharges are
    cross-check evidence only unless a separately admitted ledger map is
    bound by the controller via --admitted-ledger-map-sha256; this entry
    never asserts that local units collapse into or add to durable global
    units.

EXACT EXECUTION CONTRACT (research_entry.py, unchanged)
    /usr/bin/python3 -B \
        experiments/v3/swarm-research-20260911-155142/research_entry.py \
        --fixture-limit 4096 \
        --target experiments/v3/swarm-research-20260911-155142/control_entry_v2.py \
        --payload-limit 900000 -- \
        --inventory inputs/<inventory-command>.json \
        --inventory-sha256 <sha256 of admitted inventory bytes> \
        --result inputs/<explore-command>.json \
        --result-sha256 <sha256 of admitted shard bytes> \
        --indices <comma-separated expected shard ordinals> \
        --expected-producer-limit 40512 \
        --durable-plan-sha256 <sha256 of canonical control plan bytes> \
        --durable-receipt-id <controller reservation identity> \
        --attempt-id <unique controller attempt identity> \
        --durable-receipt <mounted canonical reservation receipt JSON> \
        --durable-receipt-sha256 <sha256 of its exact bytes> \
        --candidate-commit <40-hex exact candidate commit> \
        --policy-sha256 <sha256 of policy bytes> \
        --phase-manifest-sha256 <sha256 of phase manifest bytes> \
        --receipt-source-sha256 <sha256 of controller source minting the receipt> \
        [--admitted-ledger-map-sha256 <sha256 of a separately admitted map>] \
        --entry-source-sha256 <sha256 of this file> \
        --controls-source-sha256 <sha256 of boundary_controls.py> \
        --inventory-audit-sha256 <sha256 of inventory_audit.py> \
        --retained-audit-sha256 <sha256 of boundary_audit.py> \
        [--stdout-limit <1..1048576>]

research_entry runs this file via runpy as __main__ inside the offline
sandbox, captures stdout under the payload bound and separately accounts the
4096 planning-kernel genesis/admit fixture calls; those calls are reserved
by the wrapper, not by this module.  This module never writes, never
reserves, never calls a provider and never runs an original model or
reducer.

INJECTED CALLABLES
    durable_precharge(plan_bytes)
        Converts the already durable controller reservation into the exact
        receipt run_controls requires: sha256(plan_bytes) must equal both
        --durable-plan-sha256 and the mounted receipt's plan_sha256, the
        conversion is single-use, and the returned receipt is
        {status: DURABLY_PRECHARGED, plan_sha256, receipt_id}.  It performs
        no reservation and no write; the sandbox only binds the identity of
        a reservation the controller already made durable.
    outer_binding(inventory_bytes, result_bytes, expected_indices)
        Exact equality against the admitted input bytes and declared
        indices; drift raises ValueError containing 'outer-binding'.
    inventory_audit -> inventory_audit.audit_inventory (exact campaign
        source)
    retained_audit  -> boundary_audit.audit (exact campaign source)

PROPOSED CONTROLLER PRECONDITIONS (required, not enforceable here)
    1. Before dispatch the controller appended one hash-linked, contiguous,
       fsynced, nonrefundable reservation row covering the complete control
       charge (every baseline and available-mutation precharge plus the
       separate 4096 wrapper fixture reserve) whose reservation_id equals
       --durable-receipt-id; every post-reservation failure is retained
       with no retry identity and no refund.
    2. The controller mounts that exact ledger row as a canonical JSON
       receipt of schema boundary-01-durable-control-receipt/v2, pinned by
       --durable-receipt-sha256 and internally binding ordinal,
       previous_total/reserved_units/new_total, previous_sha256, candidate,
       policy_sha256, phase_manifest_sha256, plan_sha256, attempt_id,
       receipt_source_sha256, status DURABLY_PRECHARGED, refundable false
       and retry_of null.
    3. The controller independently reconstructed the canonical control
       plan bytes (the boundary_controls durable_plan schema over the
       exact admitted inputs and indices) and pinned its digest as
       --durable-plan-sha256.
    4. --inventory and --result mount exact dependency outputs and the
       declared sha flags equal the bound dependency output hashes.
    5. The four source sha flags pin the exact reviewed sources, and the
       phase payload contract binds /status CONTROL_PASS and
       /scientific_approval false.

PASS CRITERION
    CONTROL_PASS requires the complete fixed suite: every baseline passes
    and every fixed control is available and detected.  Unavailable
    reachable witnesses emit CONTROL_INCOMPLETE; undetected, misattributed
    or otherwise failed controls emit CONTROL_FAILED; an exception inside
    the suite emits CONTROL_ERROR.  Because the phase contract binds
    /status to CONTROL_PASS, every non-PASS outcome is a retained
    failure: under this proposal an incomplete suite is campaign-fatal
    unless admitted policy later relaxes it.  This answers the open
    review question conservatively; it is not a settled criterion.

ACCOUNTING HONESTY
    boundary_controls emits reservation_units_are_not_additive=True;
    this entry strips that unverified assertion.  Whether local control
    precharges are the same scientific units as producer/auditor
    reservations (global-additive) or lawfully collapse into already
    reserved units is unresolved: no admitted controller maps local
    labels into one durable global ledger unless a separately admitted
    ledger map is bound, which this module only echoes by hash.  The
    emitted report preserves the local limits, the actual local precharges
    and the inventory auditor's success-only private counter caveat as
    cross-check evidence only.
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path, PurePosixPath

import boundary_audit
import boundary_controls
import inventory_audit


PACKET = 'boundary-01'
HISTORIES = 384
MAX_INDICES = 24
PRODUCER_LIMIT = 40512
MAX_INPUT = 1048576
MAX_PLAN = 65536
MAX_RECEIPT = 65536
MAX_STDOUT = 1048576
DEFAULT_STDOUT_LIMIT = 900000
EXPECTED_EXCEPTIONS = (ValueError, KeyError, IndexError, TypeError)
PAYLOAD_SCHEMA = 'boundary-01-control-entry/v2'
RECEIPT_SCHEMA = 'boundary-01-durable-control-receipt/v2'
RECEIPT_KEYS = {
    'schema', 'status', 'receipt_id', 'attempt_id', 'reservation_ordinal',
    'previous_total', 'reserved_units', 'new_total', 'outstanding_units',
    'previous_sha256', 'candidate', 'policy_sha256', 'phase_manifest_sha256',
    'plan_sha256', 'receipt_source_sha256', 'refundable', 'retry_of',
    'created_utc',
}
HEX64 = re.compile(r'[0-9a-f]{64}')
HEX40 = re.compile(r'[0-9a-f]{40}')
DECIMAL = re.compile(r'0|[1-9][0-9]*')
RECEIPT_ID = re.compile(r'[a-z0-9](?:[a-z0-9/_:.-]{0,126}[a-z0-9])?')
UNRESOLVED_ADDITIVITY = ('UNRESOLVED: local control precharges are a '
    'cross-check only; no admitted controller maps them into the durable '
    'global ledger as additive or non-additive scientific units unless a '
    'separately admitted ledger map is bound')
LIMITATIONS = [
    'The durable reservation receipt is a mandatory mounted canonical JSON '
    'row bound by --durable-receipt-sha256 and internally by its ordinal, '
    'previous/new totals, previous row hash, candidate, policy, phase, '
    'control-plan and receipt-source hashes; this sandbox still cannot '
    'observe ledger fsync, contiguity or the physical durability write.',
    'CONTROL_PASS requires the complete fixed suite; an unavailable '
    'reachable witness emits CONTROL_INCOMPLETE and fails the /status '
    'contract under this proposal.',
    'Global-versus-local reservation additivity is unresolved; local '
    'precharges are cross-checks only; admitted_ledger_map_sha256 echoes '
    'only a controller-declared binding and is not verified here.',
    'No boundary.py producer, original model, reducer, provider or ledger '
    'is imported or invoked by this entry.',
    'Proposed source only: no prospective review, execution admission or '
    'scientific approval is claimed.',
]


def require(condition, message):
    if not condition:
        raise ValueError('control-entry refusal: ' + message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def hex64(value, name):
    require(type(value) is str and HEX64.fullmatch(value) is not None,
            name + ' must be 64 lowercase hex digits')
    return value


def safe_rel(path, name):
    require(type(path) is str and 0 < len(path) <= 240 and '\0' not in path,
            name + ' must be a bounded relative path')
    pure = PurePosixPath(path)
    require(not pure.is_absolute() and '..' not in pure.parts,
            name + ' must be a canonical relative path')
    return path


def read_bounded(path, limit, name):
    resolved = Path(path)
    require(resolved.is_file() and not resolved.is_symlink(),
            name + ' must be a regular non-symlink file')
    raw = resolved.read_bytes()
    require(0 < len(raw) <= limit, name + ' outside byte bound')
    return raw


def parse_indices(text):
    parts = text.split(',') if type(text) is str else []
    require(parts and all(DECIMAL.fullmatch(part) for part in parts),
            'expected indices must be comma-separated decimal ordinals')
    indices = [int(part) for part in parts]
    require(len(set(indices)) == len(indices) <= MAX_INDICES
            and all(index < HISTORIES for index in indices),
            'finite distinct expected shard ordinals')
    return indices


def check_source(module_path, declared_sha, name):
    resolved = Path(module_path).resolve()
    require(resolved.is_file() and not resolved.is_symlink(),
            name + ' source missing or noncanonical')
    require(sha(resolved.read_bytes()) == declared_sha,
            name + ' source identity mismatch')


def load_mounted_receipt(path, declared_sha, receipt_id, attempt_id, plan_sha,
                         candidate, policy_sha, phase_sha, receipt_source_sha):
    """Mandatory canonical controller-owned reservation receipt.

    The receipt is only read; this module never writes it.  Every declared
    identity and ledger field is bound to an argv pin or to exact internal
    arithmetic so an argv-forged or omitted receipt cannot satisfy it.
    """
    raw = read_bounded(path, MAX_RECEIPT, 'durable receipt')
    require(sha(raw) == declared_sha, 'mounted durable receipt bytes mismatch')
    value = boundary_controls.strict_json(raw)
    canonical = boundary_controls.canonical_bytes(value)
    require(raw in (canonical, canonical + b'\n'),
            'mounted durable receipt is not canonical JSON')
    require(type(value) is dict and set(value) == RECEIPT_KEYS,
            'durable receipt exact key set')
    require(value['schema'] == RECEIPT_SCHEMA, 'durable receipt schema')
    require(value['status'] == 'DURABLY_PRECHARGED', 'durable receipt status')
    require(value['refundable'] is False,
            'durable receipt must be explicitly nonrefundable (refundable false)')
    require(value['retry_of'] is None,
            'durable receipt carries no retry identity')
    require(type(value['receipt_id']) is str
            and value['receipt_id'] == receipt_id
            and type(value['attempt_id']) is str
            and RECEIPT_ID.fullmatch(value['attempt_id']) is not None
            and value['attempt_id'] == attempt_id,
            'durable receipt/attempt identity mismatch')
    require(type(value['reservation_ordinal']) is int
            and value['reservation_ordinal'] >= 0, 'reservation ordinal')
    require(type(value['previous_total']) is int and value['previous_total'] >= 0
            and type(value['reserved_units']) is int and value['reserved_units'] > 0
            and type(value['new_total']) is int
            and value['new_total']
            == value['previous_total'] + value['reserved_units'],
            'reservation previous/new total arithmetic')
    require(type(value['outstanding_units']) is int
            and value['outstanding_units'] >= 0,
            'reservation outstanding units')
    if value['reservation_ordinal'] == 0:
        require(value['previous_sha256'] is None,
                'genesis reservation row has no previous hash')
    else:
        require(type(value['previous_sha256']) is str
                and HEX64.fullmatch(value['previous_sha256']) is not None,
                'hash-linked previous reservation row')
    require(type(value['candidate']) is str and value['candidate'] == candidate
            and value['policy_sha256'] == policy_sha
            and value['phase_manifest_sha256'] == phase_sha
            and value['plan_sha256'] == plan_sha
            and value['receipt_source_sha256'] == receipt_source_sha,
            'durable receipt candidate/policy/phase/plan/source binding')
    require(type(value['created_utc']) is str and value['created_utc'],
            'durable receipt timestamp')
    return value


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description='boundary-01 owned control entry v2 (proposed source only)')
    parser.add_argument('--inventory', required=True)
    parser.add_argument('--inventory-sha256', required=True)
    parser.add_argument('--result', required=True)
    parser.add_argument('--result-sha256', required=True)
    parser.add_argument('--indices', required=True)
    parser.add_argument('--expected-producer-limit', type=int, required=True)
    parser.add_argument('--durable-plan-sha256', required=True)
    parser.add_argument('--durable-receipt-id', required=True)
    parser.add_argument('--attempt-id', required=True)
    parser.add_argument('--durable-receipt', required=True)
    parser.add_argument('--durable-receipt-sha256', required=True)
    parser.add_argument('--candidate-commit', required=True)
    parser.add_argument('--policy-sha256', required=True)
    parser.add_argument('--phase-manifest-sha256', required=True)
    parser.add_argument('--receipt-source-sha256', required=True)
    parser.add_argument('--admitted-ledger-map-sha256')
    parser.add_argument('--entry-source-sha256', required=True)
    parser.add_argument('--controls-source-sha256', required=True)
    parser.add_argument('--inventory-audit-sha256', required=True)
    parser.add_argument('--retained-audit-sha256', required=True)
    parser.add_argument('--stdout-limit', type=int,
                        default=DEFAULT_STDOUT_LIMIT)
    return parser.parse_args(argv)


def emit(payload, stdout_limit):
    raw = boundary_controls.canonical_bytes(payload)
    require(len(raw) <= stdout_limit, 'bounded control entry stdout')
    print(raw.decode('utf-8'))


def main(argv=None):
    args = parse_args(argv)

    def deny(event, arguments):
        if event.startswith(('socket.', 'subprocess.')) or event in (
                'os.system', 'os.posix_spawn'):
            raise RuntimeError('control-entry network/process operation '
                               'refused: ' + event)
    sys.addaudithook(deny)

    require(1 <= args.stdout_limit <= MAX_STDOUT, 'bounded stdout limit')
    require(args.expected_producer_limit == PRODUCER_LIMIT,
            'exact admitted producer limit')
    indices = parse_indices(args.indices)
    plan_sha = hex64(args.durable_plan_sha256, '--durable-plan-sha256')
    receipt_id = args.durable_receipt_id
    require(RECEIPT_ID.fullmatch(receipt_id) is not None,
            'well-formed durable receipt identity')
    attempt_id = args.attempt_id
    require(type(attempt_id) is str
            and RECEIPT_ID.fullmatch(attempt_id) is not None,
            'well-formed unique attempt identity')
    candidate = args.candidate_commit
    require(type(candidate) is str and HEX40.fullmatch(candidate) is not None,
            'exact candidate commit')
    policy_sha = hex64(args.policy_sha256, '--policy-sha256')
    phase_sha = hex64(args.phase_manifest_sha256, '--phase-manifest-sha256')
    receipt_source_sha = hex64(args.receipt_source_sha256,
                               '--receipt-source-sha256')
    ledger_map_sha = (hex64(args.admitted_ledger_map_sha256,
                            '--admitted-ledger-map-sha256')
                      if args.admitted_ledger_map_sha256 is not None else None)
    inventory_sha = hex64(args.inventory_sha256, '--inventory-sha256')
    result_sha = hex64(args.result_sha256, '--result-sha256')
    check_source(__file__, hex64(args.entry_source_sha256,
                                 '--entry-source-sha256'), 'control_entry_v2.py')
    check_source(boundary_controls.__file__,
                 hex64(args.controls_source_sha256,
                       '--controls-source-sha256'), 'boundary_controls.py')
    check_source(inventory_audit.__file__,
                 hex64(args.inventory_audit_sha256,
                       '--inventory-audit-sha256'), 'inventory_audit.py')
    check_source(boundary_audit.__file__,
                 hex64(args.retained_audit_sha256,
                       '--retained-audit-sha256'), 'boundary_audit.py')
    receipt_sha = hex64(args.durable_receipt_sha256,
                        '--durable-receipt-sha256')

    inventory_raw = read_bounded(safe_rel(args.inventory, '--inventory'),
                                 MAX_INPUT, 'inventory input')
    result_raw = read_bounded(safe_rel(args.result, '--result'),
                              MAX_INPUT, 'shard result input')
    require(sha(inventory_raw) == inventory_sha,
            'inventory input identity mismatch')
    require(sha(result_raw) == result_sha,
            'shard result input identity mismatch')
    receipt = load_mounted_receipt(safe_rel(args.durable_receipt,
                                            '--durable-receipt'),
                                   receipt_sha, receipt_id, attempt_id,
                                   plan_sha, candidate, policy_sha, phase_sha,
                                   receipt_source_sha)
    durable_reservation = {
        'receipt_id': receipt_id,
        'attempt_id': attempt_id,
        'reservation_ordinal': receipt['reservation_ordinal'],
        'previous_total': receipt['previous_total'],
        'reserved_units': receipt['reserved_units'],
        'new_total': receipt['new_total'],
        'outstanding_units': receipt['outstanding_units'],
        'previous_sha256': receipt['previous_sha256'],
        'candidate': candidate,
        'policy_sha256': policy_sha,
        'phase_manifest_sha256': phase_sha,
        'plan_sha256': plan_sha,
        'receipt_source_sha256': receipt_source_sha,
        'refundable': False,
        'retry_of': None,
        'created_utc': receipt['created_utc'],
    }

    consumed = {'used': False}

    def durable_precharge(plan_bytes):
        require(type(plan_bytes) is bytes and 0 < len(plan_bytes) <= MAX_PLAN,
                'bounded canonical control plan bytes')
        require(sha(plan_bytes) == plan_sha == receipt['plan_sha256'],
                'control plan bytes differ from the durably reserved plan')
        require(not consumed['used'], 'durable precharge already consumed')
        consumed['used'] = True
        return {'status': 'DURABLY_PRECHARGED', 'plan_sha256': plan_sha,
                'receipt_id': receipt_id}

    def outer_binding(inventory_bytes, result_bytes, expected_indices):
        require(type(inventory_bytes) is bytes
                and inventory_bytes == inventory_raw,
                'outer-binding: inventory bytes differ from admitted input')
        require(type(result_bytes) is bytes and result_bytes == result_raw,
                'outer-binding: shard bytes differ from admitted input')
        require(list(expected_indices) == indices,
                'outer-binding: expected indices differ from admitted shard')
        return True

    try:
        report = boundary_controls.run_controls(
            inventory_raw, result_raw, indices,
            durable_precharge=durable_precharge,
            outer_binding=outer_binding,
            inventory_audit=inventory_audit.audit_inventory,
            retained_audit=boundary_audit.audit,
            expected_producer_limit=args.expected_producer_limit)
        require(type(report) is dict, 'control report object required')
        require(report.get('durable_precharge_plan_sha256') == plan_sha
                and report.get('inventory_input_sha256') == inventory_sha
                and report.get('result_input_sha256') == result_sha
                and report.get('expected_indices') == indices
                and report.get('expected_producer_limit') == PRODUCER_LIMIT
                and report.get('durable_precharge_receipt') == {
                    'status': 'DURABLY_PRECHARGED',
                    'plan_sha256': plan_sha, 'receipt_id': receipt_id},
                'control report identity drift')
    except EXPECTED_EXCEPTIONS as error:
        emit({'schema': PAYLOAD_SCHEMA, 'packet': PACKET,
              'runner': 'boundary-control-entry',
              'status': 'CONTROL_ERROR', 'scientific_approval': False,
              'expected_indices': indices,
              'expected_producer_limit': PRODUCER_LIMIT,
              'inventory_input_sha256': inventory_sha,
              'result_input_sha256': result_sha,
              'durable_plan_sha256': plan_sha,
              'durable_receipt_id': receipt_id,
              'durable_receipt_sha256': receipt_sha,
              'durable_reservation': durable_reservation,
              'admitted_ledger_map_sha256': ledger_map_sha,
              'error': (type(error).__name__ + ': ' + str(error))[:2000],
              'reservation_units_additivity': UNRESOLVED_ADDITIVITY,
              'limitations': LIMITATIONS}, args.stdout_limit)
        return

    report = dict(report)
    require(report.pop('reservation_units_are_not_additive', None) is True,
            'expected unverified additivity assertion absent')
    report['reservation_units_additivity'] = UNRESOLVED_ADDITIVITY
    if report['failed_controls']:
        require(report['status'] == 'INCOMPLETE_FIXED_CONTROL_SUITE',
                'control suite status drift')
        status = 'CONTROL_FAILED'
    elif report['unavailable_reachable_witnesses']:
        require(report['status'] == 'INCOMPLETE_FIXED_CONTROL_SUITE',
                'control suite status drift')
        status = 'CONTROL_INCOMPLETE'
    else:
        require(report['status'] == 'COMPLETE_FIXED_CONTROL_SUITE'
                and report['all_required_controls_detected'] is True,
                'control suite status drift')
        status = 'CONTROL_PASS'
    emit({'schema': PAYLOAD_SCHEMA, 'packet': PACKET,
          'runner': 'boundary-control-entry',
          'status': status, 'scientific_approval': False,
          'expected_indices': indices,
          'expected_producer_limit': PRODUCER_LIMIT,
          'inventory_input_sha256': inventory_sha,
          'result_input_sha256': result_sha,
          'durable_plan_sha256': plan_sha,
          'durable_receipt_id': receipt_id,
          'durable_receipt_sha256': receipt_sha,
          'durable_reservation': durable_reservation,
          'admitted_ledger_map_sha256': ledger_map_sha,
          'source_sha256': {
              'control_entry_v2.py': sha(Path(__file__).resolve().read_bytes()),
              'boundary_controls.py': sha(
                  Path(boundary_controls.__file__).resolve().read_bytes()),
              'inventory_audit.py': sha(
                  Path(inventory_audit.__file__).resolve().read_bytes()),
              'boundary_audit.py': sha(
                  Path(boundary_audit.__file__).resolve().read_bytes()),
          },
          'reservation_units_additivity': UNRESOLVED_ADDITIVITY,
          'control_report': report,
          'limitations': LIMITATIONS}, args.stdout_limit)


if __name__ == '__main__':
    main()
