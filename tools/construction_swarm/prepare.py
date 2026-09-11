"""Generate a reviewable plan; never launches a provider."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys

from .contracts import digest, encoded, require, validate_plan
from .runner import put


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True)
    p.add_argument('--output', required=True)
    p.add_argument('--authorization', required=True)
    p.add_argument('--run-id', required=True)
    p.add_argument('--job-file', required=True, help='JSON array of frozen jobs')
    p.add_argument('--devin', help='Exact installed Devin executable; omit for fixtures')
    p.add_argument('--slots', type=int, default=2)
    p.add_argument('--minutes', type=int, default=30)
    args = p.parse_args()
    require(1 <= args.minutes <= 480, '1..480 minute deadline')
    from .contracts import strict_json
    jobs = strict_json(Path(args.job_file).read_bytes())
    exe = Path(args.devin or sys.executable).resolve(strict=True)
    commit = subprocess.check_output(['git', '-C', args.repo, 'rev-parse', 'HEAD']).decode().strip()
    plan = {'version': 1, 'run_id': args.run_id,
            'parent_goal': 'goal-recursion-v2-execution-fabric',
            'authorization': args.authorization, 'source_commit': commit,
            'deadline_utc': (datetime.now(timezone.utc) + timedelta(minutes=args.minutes)).isoformat(),
            'limits': {'model_slots': args.slots, 'test_slots': 1, 'domain_slots': min(args.slots, 8),
                       'max_dispatches': len(jobs), 'max_attempts': 1, 'timeout_seconds': 600,
                       'output_bytes': 1048576, 'input_bytes': 1048576},
            'route': {'backend': 'devin' if args.devin else 'fixture',
                      'executable': str(exe), 'sha256': digest(exe.read_bytes()),
                      'model': 'swe-2-max' if args.devin else 'fixture',
                      'capacity_basis': ('Owner authorized included SWE-2 Max; verify models list before run.'
                                         if args.devin else 'Provider-free local fixture; no inference.')},
            'jobs': jobs}
    validate_plan(plan)
    put(args.output, encoded(plan))
    print('Prepared only. Inspect source, route, scopes, capacity and deadline before init/run.')


if __name__ == '__main__':
    main()
