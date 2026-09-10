"""Owned local checks, complete inherited gates and retained-receipt audits."""
import argparse
from pathlib import Path
import re
import sys
import envelope as e

def historical_inventory(directory):
    inv = e.read(e.ROOT / 'docs/v3/construction/cut-source-overnight-20260908/validation-inventory.json')
    rows = [dict(commit='8f457c546e4d85fada73913efb900f921eaf6b1a', branch='codex/v3-cut-source-continued-20260909', script='experiments/v3/cut-source-overnight/reopen-01/check_final.py'),
            dict(commit='89ea6390774c4ef9b5c3727ad2715c57f12af90a', branch='codex/v3-cut-source-overnight-20260908', script='experiments/v3/cut-source-overnight/check.py')] + inv['frozen_gates']
    e.require(len(rows) == 18 and len(inv['regression_commands']) == 25, 'preserved historical command inventory')
    entries = e.git('worktree', 'list', '--porcelain').decode().split('\n\n')
    commands = []
    for i, row in enumerate(rows):
        matches = [x for x in entries if 'branch refs/heads/' + row['branch'] in x.splitlines()]
        e.require(len(matches) == 1, 'unique historical worktree')
        root = Path(matches[0].splitlines()[0][9:])
        e.require(e.git('rev-parse', 'HEAD', root=root).decode().strip() == row['commit']
                  and not e.git('status', '--porcelain', '--untracked-files=all', root=root).strip(), 'clean exact frozen worktree')
        e.require(not (root / 'state/PAUSE').exists(), 'frozen worktree PAUSE')
        commands.append(dict(label='frozen-' + str(i), command=[sys.executable, '-X', 'utf8', '-B', row['script'], '--working'], root=str(root), source_commit=row['commit']))
    for i, args in enumerate(inv['regression_commands']):
        commands.append(dict(label='regression-' + str(i), command=[sys.executable, *args[1:]], root=str(e.ROOT)))
    commands.append(dict(label='predecessor-packet', command=[sys.executable, '-X', 'utf8', '-B', 'experiments/v3/cut-source-overnight/append-handoff-01/check.py', str(directory / 'predecessor-output')], root=str(e.ROOT)))
    for packet, output, label in [('02', 'batch02-output', 'batch02-packet'), ('03', 'batch03-output', 'batch03-packet'), ('04', 'batch04-output', 'batch04-packet'), ('05', 'batch05-output', 'batch05-packet'), ('06', 'batch06-output', 'batch06-packet'), ('07', 'output', 'batch-packet')]:
        commands.append(dict(label=label, command=[sys.executable, '-X', 'utf8', '-B', 'experiments/v3/cut-source-overnight/batch-' + packet + '/check.py', str(directory / output), '--packet', 'C'], root=str(e.ROOT)))
    e.require(len(commands) == 50, 'all 50 Batch07 commands')
    return commands

def packet_spec(packet):
    e.require(type(packet) is str and re.fullmatch(r'packet-[0-9]{2,3}', packet) is not None, 'simple packet identifier')
    spec_path = (e.ROOT / e.DOC / packet / 'spec.json').resolve()
    e.require(spec_path.is_relative_to((e.ROOT / e.DOC).resolve()), 'packet spec containment')
    candidate = e.git('rev-parse', 'HEAD').decode().strip()
    name = spec_path.relative_to(e.ROOT).as_posix()
    e.require(name in e.sources(candidate)[1], 'packet spec bound in candidate snapshot closure')
    raw = spec_path.read_bytes(); blob = e.git('show', candidate + ':' + name)
    e.require(raw.replace(b'\r\n', b'\n') == blob.replace(b'\r\n', b'\n'), 'committed packet spec bytes')
    spec = e.read(spec_path)
    e.require(spec['id'] == packet and spec['parent_goal'] == 'goal-recursion-v2-execution-fabric', 'packet parent/id')
    e.require(type(spec['reservation']) is int and spec['reservation'] >= spec['exploration_visits'] > 0, 'finite packet state admission')
    return spec_path, spec

def packet_command(packet, directory):
    spec_path, spec = packet_spec(packet)
    output = (directory / (packet + '-output')).resolve()
    e.require(output.is_relative_to(directory.resolve()), 'packet output containment')
    return dict(label=packet, root=str(e.ROOT), command=[sys.executable, '-X', 'utf8', '-B', e.CODE + 'check.py', '--spec', str(spec_path), '--output', str(output), '--state-limit', str(spec['reservation'])])

def run(candidate, mode, packets, target=None):
    final = mode in ('full', 'audit')
    e.capacity(candidate, final)
    e.require(packets and len(packets) == len(set(packets)) and set(packets) <= set(e.policy(candidate)['allowed_packets']), 'unique prospectively admitted packets')
    specs = [packet_spec(packet)[1] for packet in packets]
    if mode == 'full': e.require(packets == e.policy(candidate)['allowed_packets'], 'all admitted packet checks included in final gate')
    if mode == 'full':
        e.require((e.END - e.now()).total_seconds() > 3000, 'observed full-gate and cleanup reserve')
    directory = e.CACHE / candidate / (e.now().strftime('%Y%m%dT%H%M%S%f') + '-' + mode)
    directory.mkdir(parents=True, exist_ok=False)
    receipt = dict(candidate=candidate, mode=mode, packets=packets, status='PREPARING', started_at=e.now().isoformat(), commands=[],
                   python_executable=sys.executable, python_sha256=e.sha(Path(sys.executable).read_bytes()))
    locks = []
    try:
        locks = e.acquire()
        states = (83900 if mode == 'full' else 0) + (sum(spec['reservation'] for spec in specs) if mode != 'audit' else 0)
        receipt['reservation'] = e.charge(candidate, directory, mode, states, final)
        receipt['sources'] = e.snapshot(candidate, directory)
        if mode == 'full': receipt['history'] = e.historical()
        commands = historical_inventory(directory) if mode == 'full' else []
        if mode == 'audit':
            e.require(target is not None and target.resolve().is_relative_to(e.CACHE), 'owned audit receipt target')
            commands.append(dict(label='audit', root=str(e.ROOT), command=[sys.executable, '-X', 'utf8', '-B', e.CODE + 'audit.py', str(target.resolve()), str(directory / 'audit.json')]))
        else: commands.extend(packet_command(packet, directory) for packet in packets)
        receipt.update(status='ADMITTED_BEFORE_EXECUTION', admitted_at=e.now().isoformat(), expected_commands=commands, capacity=e.capacity(candidate, final))
        e.write(directory / 'admission.json', receipt)
        for command in commands:
            receipt['commands'].append(e.command(candidate, command['command'], Path(command['root']), directory, command['label'], final))
            if 'source_commit' in command:
                root = Path(command['root'])
                e.require(e.git('rev-parse', 'HEAD', root=root).decode().strip() == command['source_commit']
                          and not e.git('status', '--porcelain', '--untracked-files=all', root=root).strip(), 'frozen source preserved after command')
        if mode == 'full':
            e.require(len(receipt['commands']) == 50 + len(packets), 'complete extended historical gate')
            e.require(e.read(directory / 'output/result.json') == e.read(e.ROOT / e.B7DOC / 'results.json'), 'exact frozen Batch07 result')
            e.require(e.historical() == receipt['history'], 'all historical closure unchanged')
        if mode != 'audit':
            for packet in packets:
                accepted = e.ROOT / e.DOC / packet / 'results.json'
                if mode == 'full': e.require(accepted.is_file(), 'accepted packet evidence required')
                if accepted.exists(): e.require(e.read(accepted) == e.read(directory / (packet + '-output') / 'result.json'), 'exact accepted packet result')
        e.scope(candidate)
        receipt['status'] = {'local': 'LOCAL_PACKET_PASS', 'full': 'EXTENDED_HISTORICAL_GATE_PASS', 'audit': 'OWNED_RECEIPT_AUDIT_PASS'}[mode]
    except BaseException as exc:
        receipt.update(status='FAILED_RETAINED', error=repr(exc))
        raise
    finally:
        try: e.release(locks)
        except BaseException as exc: receipt.update(status='FAILED_RETAINED', cleanup_error=repr(exc))
        receipt['finished_at'] = e.now().isoformat()
        receipt['files'] = {p.relative_to(directory).as_posix(): e.sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()}
        e.write(directory / 'receipt.json', receipt)
        if e.size(directory) >= 268435456:
            receipt.update(status='FAILED_RETAINED', error='post-serialization artifact bound')
            e.write(directory / 'receipt.json', receipt)
        print(str(directory / 'receipt.json'), flush=True)
        e.require(receipt['status'] != 'FAILED_RETAINED', 'retained failed attempt: ' + str(directory))
    return directory

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True); parser.add_argument('--mode', choices=('local', 'full', 'audit'), required=True)
    parser.add_argument('--packets', nargs='+', default=['packet-01']); parser.add_argument('--target', type=Path)
    args = parser.parse_args()
    run(args.candidate, args.mode, args.packets, args.target)
