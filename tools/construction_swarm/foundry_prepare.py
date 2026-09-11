"""Prepare a reviewable native WSL plan; no inference or worker launch."""
import argparse
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .contracts import digest, encoded, integer, require, strict_json, validate_plan
from .foundry_wsl import linux_path
from .runner import put


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='Windows review checkout with the committed inputs')
    parser.add_argument('--jobs', required=True, help='Frozen job specifications JSON array')
    parser.add_argument('--output', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--authorization', required=True)
    parser.add_argument('--slots', type=int, default=8)
    parser.add_argument('--minutes', type=int, default=30)
    parser.add_argument('--sources', help='Optional reviewed source corpus JSON, with content/SHA256/retrieved_utc')
    parser.add_argument('--devin', default='/opt/recursion-foundry/runtime/devin-3000.10.21/bin/devin')
    args = parser.parse_args()
    require(os.name == 'nt', 'prepare through the Windows admission host')
    integer(args.slots, 1, 100)
    integer(args.minutes, 1, 480)
    jobs = strict_json(Path(args.jobs).read_bytes())
    require(type(jobs) is list and 1 <= len(jobs) <= 100, '1..100 jobs per reviewed campaign')
    commit = subprocess.check_output(['git', '-C', args.repo, 'rev-parse', 'HEAD']).decode().strip()
    sha = subprocess.check_output(['wsl.exe', '-d', 'Ubuntu-24.04', '--', '/usr/bin/sha256sum', args.devin]).decode().split()[0]
    pool = Path(os.environ['LOCALAPPDATA']) / 'recursion-construction/pool'
    roots = set()
    if (pool / 'active.json').exists():
        roots.add(strict_json((pool / 'active.json').read_bytes())['root'])
    for file in (pool / 'claims').glob('*.json'):
        if not file.name.endswith('.closed.json'):
            roots.add(strict_json(file.read_bytes())['root'])
    roots = [other for other in roots if not (pool / 'claims' / (digest(other.encode()) + '.closed.json')).exists()]
    plan = {'version': 1, 'run_id': args.run_id, 'parent_goal': 'goal-recursion-v2-execution-fabric',
            'authorization': args.authorization, 'source_commit': commit,
            'deadline_utc': (datetime.now(timezone.utc) + timedelta(minutes=args.minutes)).isoformat(),
            'limits': {'model_slots': min(50, args.slots), 'test_slots': 4, 'domain_slots': 8,
                       'max_dispatches': len(jobs), 'max_attempts': 1, 'timeout_seconds': 600,
                       'output_bytes': 8 * 1024**2, 'input_bytes': 2 * 1024**2},
            'route': {'backend': 'devin', 'executable': args.devin, 'sha256': sha, 'model': 'swe-2-max',
                      'capacity_basis': 'Owner-authorized SWE-2 Max; independently verify native models listing before launch.'},
            'jobs': jobs}
    validate_plan(plan)
    plan.update(version=2, credentials=linux_path(Path(os.environ['APPDATA']) / 'devin/credentials.toml'),
                sources=strict_json(Path(args.sources).read_bytes()) if args.sources else {},
                legacy_roots=sorted(linux_path(other) for other in roots))
    plan['route']['backend'] = 'devin-tools'
    plan['limits']['model_slots'] = args.slots
    put(args.output, encoded(plan))
    print('Prepared only. Inspect the plan; initialize and run it through the native WSL admission bridge.')


if __name__ == '__main__':
    main()
