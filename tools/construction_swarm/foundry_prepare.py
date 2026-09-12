"""Prepare a reviewable native WSL plan; no inference or worker launch."""
import argparse
import copy
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .contracts import digest, encoded, integer, require, strict_json, validate_plan
from .foundry_supervision import MAX_SLOTS, MAX_WORKER_SECONDS
from .foundry_wsl import linux_path
from .runner import git, put

MAX_FOUNDRY_WORKTREES = 16


def refuse_operating_git(repo, *, require_foundry_location=True):
    """Foundry review checkouts are dedicated clones, not Recursion's operating git."""
    repo = Path(repo).resolve(strict=True)
    common = git(repo, 'rev-parse', '--git-common-dir').decode().strip()
    common = Path(common)
    if not common.is_absolute():
        common = (repo / common).resolve()
    else:
        common = common.resolve()
    listing = git(repo, 'worktree', 'list', '--porcelain').decode()
    worktrees = listing.count('worktree ')
    require(worktrees <= MAX_FOUNDRY_WORKTREES,
            f'operating git worktree registry ({worktrees}); use a dedicated foundry clone')
    branch = git(repo, 'rev-parse', '--abbrev-ref', 'HEAD').decode().strip()
    require(not branch.startswith('loop/'),
            'foundry review checkout must not use Recursion operating refs')
    if require_foundry_location:
        if os.name == 'nt':
            require(str(repo).replace('\\', '/').lower().startswith('d:/recursionswarm/'),
                    'Windows foundry review checkout must live under D:/RecursionSwarm')
        else:
            require(str(repo).startswith('/opt/recursion-foundry/'),
                    'Linux foundry source clone must live under /opt/recursion-foundry')
    return {'repo': str(repo), 'git_common_dir': str(common),
            'branch': branch, 'worktrees': worktrees}


def version_one_jobs(jobs, campaign):
    """Project v3-only tool policy out for the shared v1 contract check."""
    projected = copy.deepcopy(jobs)
    if campaign:
        for job in projected:
            job.pop('allowed_tools', None)
    return projected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='Windows review checkout with the committed inputs')
    parser.add_argument('--jobs', required=True, help='Frozen job specifications JSON array')
    parser.add_argument('--output', required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--authorization', required=True)
    parser.add_argument('--slots', type=int, default=8)
    parser.add_argument('--minutes', type=int)
    parser.add_argument('--campaign', help='Explicit reviewed v3 campaign window/quota policy JSON')
    parser.add_argument('--worker-seconds', type=int)
    parser.add_argument('--sources', help='Optional reviewed source corpus JSON, with content/SHA256/retrieved_utc')
    parser.add_argument('--devin', default='/opt/recursion-foundry/runtime/devin-3000.10.21/bin/devin')
    args = parser.parse_args()
    args.minutes = args.minutes if args.minutes is not None else (480 if args.campaign else 30)
    args.worker_seconds = (args.worker_seconds if args.worker_seconds is not None
                           else (MAX_WORKER_SECONDS if args.campaign else 600))
    require(os.name == 'nt', 'prepare through the Windows admission host')
    refuse_operating_git(args.repo)
    integer(args.slots, 1, MAX_SLOTS if args.campaign else 100)
    integer(args.worker_seconds, 1, MAX_WORKER_SECONDS if args.campaign else 1200)
    integer(args.minutes, 1, 480)
    jobs = strict_json(Path(args.jobs).read_bytes())
    require(type(jobs) is list and 1 <= len(jobs) <= (MAX_SLOTS if args.campaign else 100),
            'bounded jobs per reviewed campaign')
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
                       'max_dispatches': len(jobs), 'max_attempts': 1,
                       'timeout_seconds': min(1200, args.worker_seconds),
                       'output_bytes': 8 * 1024**2, 'input_bytes': 2 * 1024**2},
            'route': {'backend': 'devin', 'executable': args.devin, 'sha256': sha, 'model': 'swe-2-max',
                      'capacity_basis': 'Owner-authorized SWE-2 Max; independently verify native models listing before launch.'},
            'jobs': version_one_jobs(jobs, args.campaign)}
    validate_plan(plan)
    plan.update(version=2, credentials=linux_path(Path(os.environ['APPDATA']) / 'devin/credentials.toml'),
                sources=strict_json(Path(args.sources).read_bytes()) if args.sources else {},
                legacy_roots=sorted(linux_path(other) for other in roots))
    plan['route']['backend'] = 'devin-tools'
    plan['limits']['model_slots'] = args.slots
    if args.campaign:
        from .contracts import timestamp
        from .foundry import validate
        campaign = strict_json(Path(args.campaign).read_bytes())
        plan.update(version=3, campaign=campaign, jobs=jobs)
        plan['limits']['timeout_seconds'] = args.worker_seconds
        end = min(timestamp(plan['deadline_utc']), timestamp(campaign['hard_deadline_utc'])
                  - campaign['closeout_reserve_seconds'])
        plan['deadline_utc'] = datetime.fromtimestamp(end, timezone.utc).isoformat()
        validate(plan)
    put(args.output, encoded(plan))
    print('Prepared only. Inspect the plan; initialize and run it through the native WSL admission bridge.')


if __name__ == '__main__':
    main()
