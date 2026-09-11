"""Bounded native-WSL construction campaigns; all provider and tool processes are Linux."""
from __future__ import annotations

import argparse
import contextlib
import copy
import shutil
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

from .capacity import free_memory
from .contracts import (
    Refused,
    digest,
    encoded,
    file_digest,
    integer,
    keys,
    now,
    require,
    strict_json,
    timestamp,
    validate_plan,
)
from .foundry_client import devin_tools, process_scope, workspace_files
from .foundry_output import CompletedFailure
from .ledger import Ledger, controller_lock
from .runner import git, packet_for, put, verified_filing


def validate(plan):
    keys(plan, ['version', 'run_id', 'parent_goal', 'authorization', 'source_commit',
                'deadline_utc', 'limits', 'route', 'jobs', 'credentials', 'sources', 'legacy_roots'])
    require(plan['version'] == 2, 'native foundry plan version 2 required')
    require(plan['route']['backend'] == 'devin-tools' and plan['route']['model'] == 'swe-2-max',
            'exact native SWE-2 Max route required')
    integer(plan['limits']['model_slots'], 1, 100)
    require(plan['limits']['test_slots'] == 4 and plan['limits']['output_bytes'] == 8 * 1024**2,
            'qualified foundry profile requires four global tool slots and 8 MiB client output cap')
    require(len(plan['jobs']) <= 100, 'at most 100 unreviewed jobs per campaign')
    # Preserve every existing source, DAG, path, deadline and dispatch validation.
    projected = copy.deepcopy(plan)
    for field in ['credentials', 'sources', 'legacy_roots']:
        del projected[field]
    projected['version'] = 1
    projected['limits']['model_slots'] = min(50, plan['limits']['model_slots'])
    projected['route']['backend'] = 'devin'
    validate_plan(projected)
    require(type(plan['credentials']) is str and Path(plan['credentials']).is_absolute(), 'absolute credential mount required')
    require(type(plan['legacy_roots']) is list and len(plan['legacy_roots']) <= 1000 and
            all(type(x) is str and Path(x).is_absolute() for x in plan['legacy_roots']), 'invalid legacy roots')
    require(type(plan['sources']) is dict and len(encoded(plan['sources'])) <= 1024**2, 'bounded source corpus required')
    for url, value in plan['sources'].items():
        require(type(url) is str and url.startswith('https://'), 'HTTPS source identity required')
        keys(value, ['content', 'sha256', 'retrieved_utc'])
        require(type(value['content']) is str and digest(value['content'].encode()) == value['sha256'], 'source digest mismatch')
        timestamp(value['retrieved_utc'])
    return plan


def initialize(repo, root, plan):
    validate(plan)
    root = Path(root).absolute()
    require(sys.platform == 'linux' and not str(root).startswith('/mnt/'), 'run state must use native WSL filesystem')
    require(not root.exists(), 'new campaign directory required')
    require(not root.is_relative_to(Path(repo).resolve()), 'run state outside repository required')
    require(git(repo, 'rev-parse', plan['source_commit'] + '^{commit}').decode().strip() == plan['source_commit'], 'source commit missing')
    inputs = {}
    for name in sorted({p for j in plan['jobs'] for p in j['inputs']}):
        row = git(repo, 'ls-tree', plan['source_commit'], '--', name).decode().strip()
        require(row.startswith(('100644 blob ', '100755 blob ')), 'only tracked regular text inputs')
        data = git(repo, 'show', plan['source_commit'] + ':' + name)
        require(len(data) <= plan['limits']['input_bytes'], 'source too large')
        inputs[name] = {'content': data.decode('utf-8'), 'sha256': digest(data)}
    data = encoded(inputs)
    require(len(data) <= plan['limits']['input_bytes'], 'aggregate source too large')
    root.mkdir(parents=True)
    put(root / 'plan.json', encoded(plan))
    put(root / 'inputs.json', data)
    put(root / 'inputs.sha256', digest(data).encode())
    with controller_lock(root):
        ledger = Ledger(root)
        try:
            ledger.initialize(plan)
        finally:
            ledger.close()


def held_at(root):
    ledger = Ledger.readonly(root)
    try:
        return sum(r['state'] in {'running', 'unknown'} for r in ledger.rows())
    finally:
        ledger.close()


@contextlib.contextmanager
def pool(root, plan):
    """One native campaign at a time; unknown reservations never expire or refund."""
    base = Path('/var/lib/recursion-foundry/pool')
    base.mkdir(parents=True, exist_ok=True)
    with controller_lock(base):
        claims = base / 'claims'
        claims.mkdir(exist_ok=True)
        roots = set(plan['legacy_roots'])
        for file in claims.glob('*.json'):
            roots.add(strict_json(file.read_bytes())['root'])
        holds = sum(held_at(other) for other in roots - {str(root)})
        require(holds < 100, 'all provider slots held by uncertain work')
        claim = claims / (digest(str(root).encode()) + '.json')
        if not claim.exists():
            put(claim, encoded({'root': str(root), 'plan_sha256': digest(encoded(plan))}))
        yield min(plan['limits']['model_slots'], 100 - holds), holds


def run_one(root, plan, job, number, packet, scope_parent, aborted=lambda: False):
    directory = root / 'attempts' / job['id'] / str(number)
    receipt = {'job': job['id'], 'attempt': number, 'started': now(), 'launch_entered': False,
               'packet_sha256': digest(encoded(packet)), 'route': plan['route'], 'accepted': False}
    result_hash = None
    try:
        directory.mkdir(parents=True)
        put(directory / 'packet.json', encoded(packet))
        executable = Path(plan['route']['executable'])
        require(file_digest(executable) == plan['route']['sha256'], 'executable changed')
        require(Path(plan['credentials']).is_file(), 'credential mount missing')
        workspace_files(packet)  # deterministic dependency conflicts fail before provider launch
        until = time.monotonic() + min(plan['limits']['timeout_seconds'], timestamp(plan['deadline_utc']) - time.time())
        stop = lambda: aborted() or (root / 'STOP').exists() or time.monotonic() >= until or free_memory() < 4 * 1024**3
        require(not stop(), 'deadline/STOP/resources before launch')
        receipt['launch_entered'] = True
        value, observation = devin_tools(directory, plan['route'], plan['credentials'], packet,
                                          plan['sources'], scope_parent, until - time.monotonic(), stop)
        receipt.update(observation)
        put(directory / 'filing.json', encoded(value))
        result_hash = digest(encoded(value))
        state = 'returned'
    except CompletedFailure as exc:
        receipt['error'] = str(exc)[:2000]
        state = 'failed'
    except Exception as exc:  # noqa: BLE001 -- unknown never silently retries
        receipt['error'] = f'{type(exc).__name__}: {exc}'[:2000]
        state = 'unknown' if receipt['launch_entered'] else 'failed'
    receipt.update(state=state, ended=now(), filing_sha256=result_hash)
    transport = directory / 'transport.json'
    if transport.is_file():
        receipt['transport_sha256'] = digest(transport.read_bytes())
    try:
        put(directory / 'receipt.json', encoded(receipt))
    except OSError as exc:
        state = 'unknown' if receipt['launch_entered'] else 'failed'
        receipt.update(state=state, receipt_error=str(exc))
    return state, receipt, result_hash


def run(root, host_claim):
    require(sys.platform == 'linux', 'all foundry processes require Linux/WSL')
    root = Path(root).resolve(strict=True)
    require(not str(root).startswith('/mnt/'), 'native WSL run state required')
    with controller_lock(root):
        ledger = Ledger(root)
        try:
            plan = validate(ledger.plan)
            host_claim = Path(host_claim).resolve(strict=True)
            claim = strict_json(host_claim.read_bytes())
            settled = host_claim.with_name(host_claim.stem + '.settled.json')
            require(not settled.exists() and claim['root'] == str(root) and
                    claim['plan_sha256'] == digest(encoded(plan)), 'invalid/settled Windows admission claim')
            integer(claim['slots'], 1, 100)
            ledger.recover()
            require({'memory', 'pids', 'cpu'} <= set(Path('/sys/fs/cgroup/cgroup.subtree_control').read_text().split()), 'cgroup controllers not delegated')
            require(free_memory() >= 8 * 1024**3 and shutil.disk_usage(root).free >= 2 * 1024**3, 'insufficient WSL headroom')
            require(not Path('/sys/fs/cgroup/recursion-foundry-models').exists(), 'unreconciled model cgroup')
            with pool(root, plan) as (slots, holds), process_scope('/sys/fs/cgroup', 'recursion-foundry-models', 24 * 1024**3, 8192) as (group, observation):
                slots = min(slots, claim['slots'])
                (group / 'cgroup.subtree_control').write_text('+memory +pids +cpu')
                (group / 'cpu.max').write_text('1600000 100000')
                with ledger.db:
                    ledger.event('native-admission', {'slots': slots, 'foreign_holds': holds,
                                                      'tool_slots': 4, 'model_memory_bytes': 24 * 1024**3})
                abort = threading.Event()
                with ThreadPoolExecutor(max_workers=slots) as executor:
                    try:
                        pending = {}
                        while True:
                            rows = {r['id']: r for r in ledger.rows()}
                            active = sum(r['state'] in {'running', 'unknown'} for r in rows.values())
                            for job in plan['jobs']:
                                if active >= slots or (root / 'STOP').exists() or time.time() >= timestamp(plan['deadline_utc']):
                                    break
                                if rows[job['id']]['state'] != 'queued' or not all(rows[d]['state'] in {'returned', 'accepted'} for d in job['depends_on']):
                                    continue
                                try:
                                    packet = packet_for(root, plan, job, rows)
                                except Exception as exc:  # noqa: BLE001 -- keep unrelated work drainable
                                    ledger.block(job['id'], str(exc))
                                    continue
                                try:
                                    number = ledger.reserve(job['id'])
                                except Refused:
                                    continue
                                try:
                                    future = executor.submit(run_one, root, plan, job, number, packet, group, abort.is_set)
                                    pending[future] = (job['id'], number)
                                    active += 1
                                except Exception as exc:  # noqa: BLE001 -- enqueue outcome uncertain
                                    ledger.finish(job['id'], number, 'unknown', {'error': str(exc)})
                            if not pending:
                                for row in ledger.rows():
                                    if row['state'] == 'queued':
                                        ledger.block(row['id'], 'dependency, capacity, deadline, STOP or dispatch budget prevented admission')
                                break
                            completed, _ = wait(pending, timeout=.25, return_when=FIRST_COMPLETED)
                            for future in completed:
                                job_id, number = pending.pop(future)
                                try:
                                    state, receipt, result_hash = future.result()
                                except Exception as exc:  # noqa: BLE001 -- terminal evidence missing
                                    state, receipt, result_hash = 'unknown', {'error': str(exc)}, None
                                ledger.finish(job_id, number, state, receipt, result_hash)
                                print(f'{job_id} attempt={number} state={state}', flush=True)
                    finally:
                        abort.set()
            with ledger.db:
                ledger.event('native-cleanup', observation)
            require(observation['quiescent'], 'aggregate model cleanup uncertain')
            put(settled, encoded({'claim_sha256': digest(host_claim.read_bytes()),
                                 'held': sum(r['state'] in {'unknown', 'running'} for r in ledger.rows()),
                                 'native_run': str(root)}))
            return ledger.rows()
        finally:
            ledger.close()


def report(root):
    root = Path(root).resolve(strict=True)
    ledger = Ledger.readonly(root)
    try:
        result = {'run_id': ledger.plan['run_id'], 'source_commit': ledger.plan['source_commit'],
                  'accepted': False, 'jobs': []}
        for row in ledger.rows():
            item = {'id': row['id'], 'state': row['state'], 'attempts': row['attempts']}
            if row['result_hash']:
                try:
                    item['filing'] = verified_filing(root, row)
                    item['filing_sha256'] = row['result_hash']
                    attempt = root / 'attempts' / row['id'] / str(row['attempts'])
                    receipt = strict_json((attempt / 'receipt.json').read_bytes())
                    retained = ledger.db.execute('SELECT receipt FROM attempts WHERE job=? AND number=?',
                                                 (row['id'], row['attempts'])).fetchone()[0]
                    require(encoded(receipt) == encoded(strict_json(retained)), 'attempt receipt differs from ledger')
                    item['tools'] = receipt['tool_receipts']
                    for tool in item['tools']:
                        require(digest((attempt / 'tools' / str(tool['number']) / 'receipt.json').read_bytes()) == tool['sha256'], 'tool receipt changed')
                except (Refused, OSError, KeyError) as exc:
                    item['artifact_error'] = str(exc)
            result['jobs'].append(item)
        return result
    finally:
        ledger.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--repo', required=True)
    init.add_argument('--plan', required=True)
    init.add_argument('--root', required=True)
    for command in ['run', 'report']:
        command_parser = sub.add_parser(command)
        command_parser.add_argument('--root', required=True)
        if command == 'run':
            command_parser.add_argument('--host-claim', required=True)
    args = parser.parse_args()
    if args.command == 'init':
        initialize(args.repo, args.root, strict_json(Path(args.plan).read_bytes()))
    elif args.command == 'run':
        rows = run(args.root, args.host_claim)
        return 0 if all(r['state'] in {'returned', 'accepted'} for r in rows) else 2
    else:
        print(encoded(report(args.root)).decode())
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Refused, OSError, ValueError) as exc:
        print(f'REFUSED: {exc}')
        raise SystemExit(2)
