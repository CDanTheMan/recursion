"""Owner-authorized release of unknown holds that already have terminal cleanup.

Does not delete claims, ledgers, receipts, or exports. Dispatch charges stay.
Never marks returned/accepted. Skips live controllers and running jobs.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .contracts import digest, encoded, require, strict_json
from .ledger import Ledger, controller_lock
from .runner import put


def remaining_holds(root):
    ledger = Ledger.readonly(root)
    try:
        return sum(r['state'] in {'running', 'unknown'} for r in ledger.rows())
    finally:
        ledger.close()


def replace_bytes(path, data):
    path = Path(path)
    require('\r' not in path.name and '\n' not in path.name, 'CR/LF in filename')
    tmp = path.with_name(path.name + '.tmp')
    with tmp.open('xb') as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)

POLICY_MARKERS = (
    'foreign/native tool attempted',
    'invalid JSON',
    'unbound evidence citation',
    'invalid dissent',
    'expected fields',
    'provider tool calls differ from durable broker receipts',
    'final filing invalid',
)


def classify(receipt, transport):
    """Return failed, cancelled, or None (leave unknown)."""
    if not receipt or not receipt.get('launch_entered'):
        return None
    if not transport or transport.get('local_quiescent') is not True:
        return None
    if transport.get('reason') == 'cancelled':
        return 'cancelled'
    if transport.get('exit_code') not in (0, None) or transport.get('reason'):
        return 'failed'
    error = receipt.get('error') or ''
    if any(marker in error for marker in POLICY_MARKERS):
        return 'failed'
    return None


def settle_job(root, ledger, job_id, authorization):
    rows = {r['id']: r for r in ledger.rows()}
    require(job_id in rows and rows[job_id]['state'] == 'unknown', 'job is not unknown')
    row = rows[job_id]
    directory = root / 'attempts' / job_id / str(row['attempts'])
    receipt = strict_json((directory / 'receipt.json').read_bytes())
    transport = {}
    if (directory / 'transport.json').is_file():
        transport = strict_json((directory / 'transport.json').read_bytes())
    terminal = classify(receipt, transport)
    require(terminal is not None, 'no terminal cleanup evidence; unknown retained')
    evidence = {
        'authorization': authorization,
        'basis': 'quiescent native transport plus owner-authorized completed-failure settlement',
        'job': job_id,
        'attempt': row['attempts'],
        'terminal': terminal,
        'receipt_sha256': digest((directory / 'receipt.json').read_bytes()),
        'transport_sha256': digest((directory / 'transport.json').read_bytes()),
        'original_error': (receipt.get('error') or '')[:500],
        'exit_code': transport.get('exit_code'),
        'reason': transport.get('reason'),
        'local_quiescent': True,
        'dispatch_charge_retained': True,
        'accepted': False,
    }
    target = directory / 'owner-settlement.json'
    if target.exists():
        require(target.read_bytes() == encoded(evidence), 'owner-settlement evidence differs')
    else:
        put(target, encoded(evidence))
    ledger.reconcile_failed(job_id, row['attempts'], digest(encoded(evidence)), terminal)
    return terminal


def sync_windows_held(root, held, admission=Path('/mnt/d/RecursionSwarm/foundry-admission')):
    if not admission.is_dir():
        return 0
    updated = 0
    linux_root = str(Path(root).resolve())
    for settled in admission.glob('*.settled.json'):
        record = strict_json(settled.read_bytes())
        native = record.get('native_run')
        if native is None or str(Path(native).resolve()) != linux_root:
            continue
        claim = settled.with_name(settled.name[:-len('.settled.json')] + '.json')
        require(claim.is_file(), 'admission claim missing for settlement')
        require(record['claim_sha256'] == digest(claim.read_bytes()), 'admission claim digest mismatch')
        reservation = strict_json(claim.read_bytes())['slots']
        require(type(held) is int and 0 <= held <= reservation, 'invalid remaining hold')
        replace_bytes(settled, encoded({**record, 'held': held}))
        updated += 1
    for claim in admission.glob('*.json'):
        if claim.name.endswith('.settled.json'):
            continue
        record = strict_json(claim.read_bytes())
        claim_root = record.get('root')
        if claim_root is None or str(Path(claim_root).resolve()) != linux_root:
            continue
        settled = claim.with_name(claim.stem + '.settled.json')
        if settled.exists():
            continue
        if held == 0:
            put(settled, encoded({'claim_sha256': digest(claim.read_bytes()),
                                  'held': 0, 'native_run': linux_root}))
            updated += 1
    return updated


def settle_root(root, authorization, admission=Path('/mnt/d/RecursionSwarm/foundry-admission')):
    root = Path(root).resolve(strict=True)
    with controller_lock(root):
        ledger = Ledger(root)
        try:
            summary = []
            for row in list(ledger.rows()):
                if row['state'] != 'unknown':
                    continue
                try:
                    terminal = settle_job(root, ledger, row['id'], authorization)
                    summary.append({'job': row['id'], 'terminal': terminal})
                except Exception as exc:  # noqa: BLE001 -- leave that job unknown
                    summary.append({'job': row['id'], 'skipped': str(exc)[:300]})
            remaining = remaining_holds(root)
            windows = sync_windows_held(root, remaining, admission)
            return {'root': str(root), 'settled': summary, 'remaining_holds': remaining,
                    'windows_updated': windows}
        finally:
            ledger.close()


def settle_pool(claims, authorization, skip_locked=True, admission=Path('/mnt/d/RecursionSwarm/foundry-admission')):
    claims = Path(claims)
    reports = []
    for claim in sorted(claims.glob('*.json')):
        root = Path(strict_json(claim.read_bytes())['root'])
        try:
            reports.append(settle_root(root, authorization, admission=admission))
        except Exception as exc:  # noqa: BLE001 -- live controller or missing run
            if skip_locked:
                reports.append({'root': str(root), 'skipped': str(exc)[:300]})
            else:
                raise
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authorization', required=True)
    parser.add_argument('--claims', default='/var/lib/recursion-foundry/pool/claims')
    parser.add_argument('--root', help='Settle one run instead of the whole pool')
    args = parser.parse_args()
    require('Lucas' in args.authorization and '2026-09-12' in args.authorization,
            'explicit Lucas owner authorization required')
    require('dispatch' in args.authorization.lower(), 'must retain dispatch charges')
    if args.root:
        report = [settle_root(args.root, args.authorization)]
    else:
        report = settle_pool(args.claims, args.authorization)
    print(json.dumps(report, indent=2))
    released = sum(1 for r in reports_settled(report))
    remaining = sum(r.get('remaining_holds', 0) for r in report if isinstance(r, dict))
    print(f'released {released} remaining_holds_sum {remaining}')
    return 0


def reports_settled(reports):
    for report in reports:
        for item in report.get('settled') or []:
            if item.get('terminal'):
                yield item


if __name__ == '__main__':
    from .contracts import Refused
    try:
        raise SystemExit(main())
    except (Refused, OSError, ValueError) as exc:
        print(f'REFUSED: {exc}')
        raise SystemExit(2)
