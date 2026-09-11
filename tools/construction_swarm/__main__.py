import argparse
import json
from pathlib import Path

from .contracts import Refused, encoded, strict_json
from .ledger import Ledger, controller_lock
from .runner import initialize, manifest, put, run
from .sandbox import stage, test_staged


def main():
    parser = argparse.ArgumentParser(description='Bounded Recursion construction swarm')
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('--repo', required=True)
    init.add_argument('--root', required=True)
    init.add_argument('--plan', required=True)
    for command in ['run', 'status', 'manifest', 'retry', 'accept', 'reject', 'stage', 'test']:
        cmd = sub.add_parser(command)
        cmd.add_argument('--root', required=True)
        if command in ['retry', 'accept', 'reject', 'stage']:
            cmd.add_argument('--job', required=True)
        if command in ['retry', 'accept', 'reject']:
            cmd.add_argument('--reason', required=True)
        if command in ['manifest', 'stage']:
            cmd.add_argument('--output', required=True)
        if command == 'stage':
            cmd.add_argument('--destination', required=True)
        if command == 'test':
            cmd.add_argument('--stage-manifest', required=True)
            cmd.add_argument('--entry', required=True)
    args = parser.parse_args()
    root = Path(args.root).absolute()
    if args.command == 'init':
        initialize(args.repo, root, strict_json(Path(args.plan).read_bytes()))
        print(root)
        return 0
    if args.command == 'run':
        rows = run(root)
        return 0 if all(r['state'] in {'returned', 'accepted'} for r in rows) else 2
    if args.command == 'test':
        result = test_staged(root, strict_json(Path(args.stage_manifest).read_bytes()), args.entry)
        print(json.dumps(result, indent=2))
        return 0 if result['exit_code'] == 0 and not result['reason'] and result['local_quiescent'] else 2
    if args.command == 'status':
        ledger = Ledger.readonly(root)
        try:
            print(json.dumps(manifest(root, ledger), indent=2))
        finally:
            ledger.close()
        return 0
    with controller_lock(root):
        ledger = Ledger(root)
        try:
            if args.command == 'status':
                print(json.dumps(manifest(root, ledger), indent=2))
            elif args.command == 'manifest':
                put(args.output, encoded(manifest(root, ledger)))
            elif args.command == 'retry':
                ledger.retry(args.job, args.reason)
            elif args.command in ['accept', 'reject']:
                manifest(root, ledger)  # verify collected bytes before adjudication
                ledger.decision(args.job, args.command == 'accept', args.reason)
            elif args.command == 'stage':
                result = stage(root, ledger, args.job, args.destination)
                put(args.output, encoded(result))
        finally:
            ledger.close()
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Refused, OSError, ValueError) as exc:
        print(f'REFUSED: {exc}')
        raise SystemExit(2)
