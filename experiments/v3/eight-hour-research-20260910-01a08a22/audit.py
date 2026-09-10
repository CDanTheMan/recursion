"""Retained evidence verification, with no model exploration or reducer execution."""
import gzip
from pathlib import Path
import sys
import envelope as e
import run as runner

def audit(path):
    path = path.resolve(); directory = path.parent
    e.require(path.is_relative_to(e.CACHE) and path.name == 'receipt.json', 'campaign receipt containment')
    receipt = e.read(path); candidate = receipt['candidate']
    admission = e.read(directory / 'admission.json')
    e.scope(candidate)
    e.require(receipt['status'] in ('LOCAL_PACKET_PASS', 'EXTENDED_HISTORICAL_GATE_PASS') and 'cleanup_error' not in receipt, 'completed subject receipt')
    e.require(admission['status'] == 'ADMITTED_BEFORE_EXECUTION' and admission['commands'] == [], 'actual pre-execution admission receipt')
    for key in ('candidate', 'mode', 'packets', 'started_at', 'admitted_at', 'python_executable', 'python_sha256', 'sources', 'reservation', 'expected_commands', 'capacity', 'finalization_admission'):
        e.require(admission[key] == receipt[key], 'unchanged admitted field: ' + key)
    e.require(receipt['python_executable'] == sys.executable and receipt['python_sha256'] == e.sha(Path(sys.executable).read_bytes()), 'exact interpreter bytes')
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file() and p != path}
    e.require(actual == set(receipt['files']), 'complete retained file map membership')
    for name, expected in receipt['files'].items():
        target = (directory / name).resolve()
        e.require(target.is_relative_to(directory) and e.sha(target.read_bytes()) == expected, 'retained evidence hash: ' + name)
    inherited, changed = e.sources(candidate)
    e.require(set(receipt['sources']) == inherited | changed, 'exact inherited plus changed source closure')
    for name, source in receipt['sources'].items():
        target = (directory / source['snapshot_file']).resolve()
        e.require(target.is_relative_to(directory) and source['snapshot_codec'] == 'gzip', 'snapshot codec and containment')
        raw, blob = gzip.decompress(target.read_bytes()), e.git('show', candidate + ':' + name)
        e.require(e.sha(raw) == source['working_sha256'] and e.sha(blob) == source['git_blob_sha256'], 'decompressed and committed hashes')
        e.require(raw.replace(b'\r\n', b'\n') == blob.replace(b'\r\n', b'\n') == (e.ROOT / name).read_bytes().replace(b'\r\n', b'\n'), 'actual source equivalence')
        if name in inherited: e.require(blob == e.git('show', e.BASE + ':' + name), 'immutable historical input')
    full = receipt['mode'] == 'full'
    expected = runner.historical_inventory(directory) if full else []
    expected.extend(command for packet in receipt['packets'] for command in runner.packet_commands(packet, directory))
    e.require(expected == receipt['expected_commands'] and len(expected) == len(receipt['commands']), 'independent exact ordered command inventory')
    for wanted, actual in zip(expected, receipt['commands']):
        label = wanted['label']
        e.require(actual['command'] == wanted['command'] and actual['root'] == wanted['root'] and actual['candidate'] == candidate, 'exact argv, root and candidate')
        e.require(actual['source_commit'] == wanted.get('source_commit', candidate), 'historical/candidate commit binding')
        e.require(actual == e.read(directory / (label + '-execution.json')), 'actual per-command receipt equality')
        admitted_command = e.read(directory / (label + '-admission.json'))
        e.require(admitted_command['status'] == 'ADMITTED_BEFORE_EXECUTION', 'command admitted before execution')
        e.require(all(actual[k] == v for k, v in admitted_command.items() if k != 'status'), 'command admission binding')
        e.require(e.dt.datetime.fromisoformat(receipt['admitted_at']) <= e.dt.datetime.fromisoformat(actual['started_at']), 'top-level admission precedes every command')
        e.require(actual['status'] == 'PASS' and actual['exit_code'] == 0 and actual['owned_active_after_cleanup'] == 0 and actual['cleanup_errors'] == [], 'successful owned execution and cleanup')
        e.require(actual['seconds'] < 600 and actual['peak_memory_bytes'] <= 2147483648, 'terminal time/memory bounds')
        e.require(e.sha((directory / (label + '.log')).read_bytes()) == actual['log_sha256'], 'actual command log hash')
    rows, total = e.ledger()
    reservation = receipt['reservation']
    e.require(reservation in rows and reservation['candidate'] == candidate, 'retained precharge')
    identity = directory.relative_to(e.CACHE).as_posix() + '/' + receipt['mode']
    e.require(reservation['identity'] == identity and sum(x['identity'] == identity for x in rows) == 1, 'this exact invocation uniquely precharged')
    e.require(e.dt.datetime.fromisoformat(receipt['started_at']) <= e.dt.datetime.fromisoformat(reservation['at']) <= e.dt.datetime.fromisoformat(receipt['admitted_at']), 'reservation precedes initialization/admission')
    e.require(reservation['policy_sha256'] == receipt['capacity']['policy_sha256'], 'precharge bound to admitted policy')
    states = (83900 if full else 0) + sum(e.read(e.ROOT / e.DOC / packet / 'spec.json')['reservation'] for packet in receipt['packets'])
    e.require(reservation['states'] == states and total <= e.policy(candidate)['ceiling'], 'exact state charge and cumulative budget')
    if full:
        e.require(e.read(directory / 'output/result.json') == e.read(e.ROOT / e.B7DOC / 'results.json'), 'historical Batch07 result')
        e.require(e.historical() == receipt['history'], 'preserved historical file closure')
    for packet in receipt['packets']:
        result = e.read(directory / (packet + '-output') / 'result.json')
        spec = e.read(e.ROOT / e.DOC / packet / 'spec.json')
        e.require(result['state_visits_per_representation'] == spec['exploration_visits'] <= spec['reservation'], 'checked actual packet visits')
        e.require(result['environments'] == spec['environments'] and result['schedules'] == spec['schedules_per_unit_outcome'], 'complete finite domain')
        accepted = e.ROOT / e.DOC / packet / 'results.json'
        if accepted.exists(): e.require(e.read(accepted) == result, 'accepted packet result equality')
        for case in result['cases']:
            target = (directory / (packet + '-output') / case['artifact']).resolve()
            e.require(target.is_relative_to((directory / (packet + '-output')).resolve()), 'retained certificate containment')
            e.require(e.sha(target.read_bytes()) == case['artifact_sha256'], 'retained replay certificate binding')
    e.require(e.size(directory) < 268435456, 'complete subject artifact bound')
    return dict(status='EXACT_RETAINED_RECEIPT_AUDIT_PASS', candidate=candidate, receipt=str(path), receipt_sha256=e.sha(path.read_bytes()),
                commands=len(expected), retained_files=len(receipt['files']), snapshots=len(receipt['sources']), cumulative_reserved_states=total,
                model_reducers_executed=False, historical_gates_rerun=False, checked_at=e.now().isoformat())

if __name__ == '__main__':
    result = audit(Path(sys.argv[1]))
    e.write(Path(sys.argv[2]), result)
    print(result['status'])
