"""Owned local checks, complete inherited gates and retained-receipt audits."""
import argparse
from pathlib import Path
import re
import sys
import envelope as e

def finalization_admission(candidate):
    """Recognize only retained successful exact-candidate gates with owned audits."""
    def closed(path):
        receipt = e.read(path); folder = path.parent
        actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file() and p != path}
        e.require(actual == set(receipt['files']), 'complete prior retained receipt membership')
        for name, expected in receipt['files'].items():
            target = (folder/name).resolve()
            e.require(target.is_relative_to(folder.resolve()) and e.sha(target.read_bytes()) == expected, 'unchanged prior retained evidence')
        return receipt
    prior = {}
    for audit_path in sorted((e.CACHE/candidate).glob('*-audit/receipt.json')):
        row = e.read(audit_path)
        if row.get('status') != 'OWNED_RECEIPT_AUDIT_PASS': continue
        check = e.read(audit_path.parent/'audit.json')
        target = Path(check['receipt']).resolve()
        if not target.is_relative_to((e.CACHE/candidate).resolve()) or not target.parent.name.endswith('-full'): continue
        row, gate = closed(audit_path), closed(target)
        e.require(row['candidate'] == gate['candidate'] == candidate and gate['status']=='EXTENDED_HISTORICAL_GATE_PASS', 'successful prior exact-candidate full gate and audit')
        e.require(check['status']=='EXACT_RETAINED_RECEIPT_AUDIT_PASS' and check['receipt_sha256']==e.sha(target.read_bytes()) and check['candidate']==candidate, 'owned audit binds this actual prior gate')
        commands = row['commands']
        e.require(len(commands)==1 and commands[0]['status']=='PASS' and commands[0]['owned_active_after_cleanup']==0 and commands[0]['cleanup_errors']==[] and commands[0]['candidate']==candidate, 'successful prior owned audit execution')
        e.require(commands[0]==e.read(audit_path.parent/'audit-execution.json') and str(target) in commands[0]['command'], 'actual prior audit command and execution binding')
        expected = historical_inventory(target.parent)
        expected.extend(command for packet in gate['packets'] for command in packet_commands(packet,target.parent))
        e.require(gate['packets']==e.policy(candidate)['allowed_packets'] and gate['expected_commands']==expected and len(gate['commands'])==len(expected), 'complete expanded prior gate')
        e.require(all(x['status']=='PASS' and x['owned_active_after_cleanup']==0 and x['cleanup_errors']==[] for x in gate['commands']), 'all prior commands passed and cleaned')
        prior[str(target)] = dict(gate=str(target),gate_sha256=e.sha(target.read_bytes()),audit=str(audit_path),audit_sha256=e.sha(audit_path.read_bytes()))
    policy = e.policy(candidate)
    outstanding = 2 if not prior else 1
    seconds = outstanding*policy['full_gate_admission_seconds'] + 600
    e.require((e.END-e.now()).total_seconds()>seconds, 'time for every outstanding exact-candidate gate and finalization')
    return dict(prior_audited_gates=list(prior.values()),outstanding_gates_including_this=outstanding,reserved_seconds=seconds,checked_at=e.now().isoformat())

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
    spec_path = (e.ROOT / e.packet_doc(packet) / packet / 'spec.json').resolve()
    e.require(spec_path.is_relative_to((e.ROOT / e.packet_doc(packet)).resolve()), 'packet spec containment')
    candidate = e.git('rev-parse', 'HEAD').decode().strip()
    name = spec_path.relative_to(e.ROOT).as_posix()
    e.require(name in set.union(*e.sources(candidate)), 'packet spec bound in candidate snapshot closure')
    raw = spec_path.read_bytes(); blob = e.git('show', candidate + ':' + name)
    e.require(raw.replace(b'\r\n', b'\n') == blob.replace(b'\r\n', b'\n'), 'committed packet spec bytes')
    spec = e.read(spec_path)
    e.require(spec['id'] == packet and spec['parent_goal'] == 'goal-recursion-v2-execution-fabric', 'packet parent/id')
    e.require(type(spec['reservation']) is int and spec['reservation'] >= spec['exploration_visits'] > 0, 'finite packet state admission')
    return spec_path, spec

def packet_commands(packet, directory):
    spec_path, spec = packet_spec(packet)
    output = (directory / (packet + '-output')).resolve()
    e.require(output.is_relative_to(directory.resolve()), 'packet output containment')
    if spec.get('kind') == 'source-guard-combinatorics':
        e.require(packet == 'packet-06' and spec['model_state_visits'] == 0 and spec['reservation'] == 81000 and spec['per_command_work_limit'] == 40500, 'exact finite symbolic-only admission')
        common = [sys.executable, '-X', 'utf8', '-B', e.CODE + 'guard_order.py', '--spec', str(spec_path), '--output', str(output), '--work-limit', str(spec['per_command_work_limit'])]
        return [dict(label=packet+'-symbolic', root=str(e.ROOT), command=common), dict(label=packet+'-symbolic-retained', root=str(e.ROOT), command=[*common, '--audit'])]
    if packet == 'packet-05':
        e.require(spec['reference_packets'] == ['packet-01','packet-04'] and spec['reference_shared_visits'] == [204,1760] and spec['reservation'] == 1964 and spec['required_controls_by_reference'] == {'packet-01':23,'packet-04':24}, 'exact reviewed small prefix validation definition')
        commands = []
        for reference,limit in zip(spec['reference_packets'],spec['reference_shared_visits']):
            reference_spec,_ = packet_spec(reference)
            args=[sys.executable,'-X','utf8','-B',e.CODE+'shared.py','--spec',str(reference_spec),'--reference',str((directory/(reference+'-output')).resolve()),'--output',str(output/reference),'--state-limit',str(limit)]
            commands.append(dict(label=packet+'-'+reference,root=str(e.ROOT),command=args))
        for reference in spec['reference_packets']:
            reference_spec,_ = packet_spec(reference)
            args=[sys.executable,'-X','utf8','-B',e.CODE+'shared.py','--spec',str(reference_spec),'--reference',str((directory/(reference+'-output')).resolve()),'--output',str(output/reference),'--audit']
            commands.append(dict(label=packet+'-retained-'+reference,root=str(e.ROOT),command=args))
        commands.append(dict(label=packet+'-union',root=str(e.ROOT),command=[sys.executable,'-X','utf8','-B',e.CODE+'shared.py','--spec',str(spec_path),'--output',str(output),'--union']))
        return commands
    if 'shard_keys' not in spec:
        checker = 'selected.py' if packet == 'packet-04' else 'check.py'
        return [dict(label=packet, root=str(e.ROOT), command=[sys.executable, '-X', 'utf8', '-B', e.packet_code(packet) + checker, '--spec', str(spec_path), '--output', str(output), '--state-limit', str(spec['reservation'])])]

    e.require(len(spec['shard_keys']) == len(set(spec['shard_keys'])) == 6 and spec['visits_per_shard'] * 6 == spec['reservation'], 'finite complete shard partition')
    commands = []
    for i, key in enumerate(spec['shard_keys']):
        commands.append(dict(label=packet + '-shard-' + str(i), root=str(e.ROOT), command=[sys.executable, '-X', 'utf8', '-B', e.packet_code(packet) + 'sharded.py', '--spec', str(spec_path), '--output', str(output / ('shard-' + str(i))), '--shard', key, '--state-limit', str(spec['visits_per_shard'])]))
    for i, key in enumerate(spec['shard_keys']):
        commands.append(dict(label=packet + '-retained-' + str(i), root=str(e.ROOT), command=[sys.executable, '-X', 'utf8', '-B', e.packet_code(packet) + 'sharded.py', '--spec', str(spec_path), '--output', str(output / ('shard-' + str(i))), '--audit-shard', key]))
    commands.append(dict(label=packet + '-union', root=str(e.ROOT), command=[sys.executable, '-X', 'utf8', '-B', e.packet_code(packet) + 'sharded.py', '--spec', str(spec_path), '--output', str(output), '--union']))
    return commands

def run(candidate, mode, packets, target=None):
    final = mode in ('full', 'audit')
    e.capacity(candidate, final)
    e.require(packets and len(packets) == len(set(packets)) and set(packets) <= set(e.policy(candidate)['allowed_packets']), 'unique prospectively admitted packets')
    specs = [packet_spec(packet)[1] for packet in packets]
    for i,spec in enumerate(specs):
        if 'reference_packets' in spec:
            e.require(all(reference in packets[:i] for reference in spec['reference_packets']), 'fresh unreduced references declared earlier in the same admitted run')
    if mode == 'full': e.require(packets == e.policy(candidate)['allowed_packets'], 'all admitted packet checks included in final gate')
    finalization = finalization_admission(candidate) if mode == 'full' else None
    if mode == 'local':
        duration = sum(e.policy(candidate)['local_packet_admission_seconds'][packet] for packet in packets)
        e.require(type(duration) is int and duration > 0 and (e.END - e.now()).total_seconds() > e.policy(candidate)['finalization_reserve_seconds'] + duration + 605, 'entire local multi-command packet plus finalization reserve')
    directory = e.CACHE / candidate / (e.now().strftime('%H%M%S%f') + '-' + mode)
    directory.mkdir(parents=True, exist_ok=False)
    receipt = dict(candidate=candidate, mode=mode, packets=packets, status='PREPARING', started_at=e.now().isoformat(), commands=[],
                   python_executable=sys.executable, python_sha256=e.sha(Path(sys.executable).read_bytes()))
    receipt['finalization_admission'] = finalization
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
        else: commands.extend(command for packet in packets for command in packet_commands(packet, directory))
        receipt.update(status='ADMITTED_BEFORE_EXECUTION', admitted_at=e.now().isoformat(), expected_commands=commands, capacity=e.capacity(candidate, final))
        e.write(directory / 'admission.json', receipt)
        for command in commands:
            receipt['commands'].append(e.command(candidate, command['command'], Path(command['root']), directory, command['label'], final))
            if 'source_commit' in command:
                root = Path(command['root'])
                e.require(e.git('rev-parse', 'HEAD', root=root).decode().strip() == command['source_commit']
                          and not e.git('status', '--porcelain', '--untracked-files=all', root=root).strip(), 'frozen source preserved after command')
        if mode == 'full':
            e.require(len(receipt['commands']) == 50 + sum(len(packet_commands(packet, directory)) for packet in packets), 'complete extended historical gate')
            e.require(e.read(directory / 'output/result.json') == e.read(e.ROOT / e.B7DOC / 'results.json'), 'exact frozen Batch07 result')
            e.require(e.historical() == receipt['history'], 'all historical closure unchanged')
        if mode != 'audit':
            for packet in packets:
                accepted = e.ROOT / e.packet_doc(packet) / packet / 'results.json'
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
