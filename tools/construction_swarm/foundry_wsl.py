"""Windows admission bridge only. Controllers, providers and tools execute in WSL.

The existing Windows pool mutex covers admission and launch. An immutable claim
holds capacity even if this bridge disappears; only native terminal evidence can
settle it. No Windows model process is launched by this module.
"""
import argparse
import os
import subprocess
import uuid
from pathlib import Path

from .contracts import digest, encoded, require, strict_json
from .foundry_supervision import MAX_SLOTS, ceiling
from .ledger import Ledger, controller_lock
from .runner import put


def native_holds(pool):
    held = 0
    for claim in (Path(pool) / 'native-claims').glob('*.json'):
        if claim.name.endswith('.settled.json'):
            continue
        record = strict_json(claim.read_bytes())
        if 'shared_claim' in record:
            claim = Path(record['shared_claim'])
            record = strict_json(claim.read_bytes())
        reservation = record['slots']
        require(type(reservation) is int and 1 <= reservation <= MAX_SLOTS, 'invalid native reservation')
        settled = claim.with_name(claim.stem + '.settled.json')
        if settled.exists():
            terminal = strict_json(settled.read_bytes())
            require(terminal['claim_sha256'] == digest(claim.read_bytes()) and
                    type(terminal['held']) is int and 0 <= terminal['held'] <= reservation,
                    'invalid native settlement')
            reservation = terminal['held']
        held += reservation
    return held


def linux_path(value):
    value = str(value).replace('\\', '/')
    require(len(value) > 3 and value[1:3] == ':/', 'local drive path required')
    return '/mnt/' + value[0].lower() + '/' + value[3:]


def run_native(root, source, distro='Ubuntu-24.04'):
    require(os.name == 'nt', 'use the Windows WSL admission bridge')
    require(distro == 'Ubuntu-24.04', 'unqualified WSL distribution')
    require(root.startswith('/var/lib/recursion-foundry/runs/') and '..' not in root, 'native run root required')
    require(source.startswith('/opt/recursion-foundry/') and '..' not in source, 'native trusted source required')
    native_root = Path('//wsl.localhost') / distro / root.lstrip('/')
    plan = strict_json((native_root / 'plan.json').read_bytes())
    pool = Path(os.environ['LOCALAPPDATA']) / 'recursion-construction' / 'pool'
    pool.mkdir(parents=True, exist_ok=True)
    with controller_lock(pool):
        roots = set()
        active = pool / 'active.json'
        if active.exists():
            roots.add(strict_json(active.read_bytes())['root'])
        for file in (pool / 'claims').glob('*.json'):
            if file.name.endswith('.closed.json') or file.with_name(file.stem + '.closed.json').exists():
                continue
            roots.add(strict_json(file.read_bytes())['root'])
        legacy_held = 0
        imported = []
        for other in roots:
            closure = pool / 'claims' / (digest(other.encode()) + '.closed.json')
            if closure.exists():
                continue
            ledger = Ledger.readonly(other)
            try:
                rows = ledger.rows()
                require(not any(r['state'] == 'running' for r in rows), 'Windows provider work remains active')
                legacy_held += sum(r['state'] == 'unknown' for r in rows)
            finally:
                ledger.close()
            imported.append(linux_path(other))
        require(set(plan['legacy_roots']) == set(imported), 'legacy reservation import changed; prepare a fresh plan')
        from .foundry import validate
        validate(plan)
        slots = min(plan['limits']['model_slots'], ceiling(plan) - legacy_held - native_holds(pool))
        require(slots >= 1, 'shared provider capacity held by uncertain work')
        claims = pool / 'native-claims'
        claims.mkdir(exist_ok=True)
        claim_id = uuid.uuid4().hex
        # MSIX can virtualize AppData writes away from WSL's drive mount. The
        # pool retains a pointer to a claim on the explicitly shared data drive.
        shared = Path('D:/RecursionSwarm/foundry-admission')
        shared.mkdir(parents=True, exist_ok=True)
        claim = shared / (claim_id + '.json')
        put(claim, encoded({'root': root, 'plan_sha256': digest(encoded(plan)), 'slots': slots,
                            'legacy_held': legacy_held, 'source': source}))
        put(claims / (claim_id + '.json'), encoded({'shared_claim': str(claim)}))
        command = ['wsl.exe', '-d', distro, '--cd', source, '--', '/usr/bin/python3', '-B', '-m',
                   'tools.construction_swarm.foundry', 'run', '--root', root, '--host-claim', linux_path(claim)]
        return subprocess.call(command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--source', default='/opt/recursion-foundry/source')
    args = parser.parse_args()
    return run_native(args.root, args.source)


if __name__ == '__main__':
    raise SystemExit(main())
