"""Retained evidence verification, with no model exploration or reducer execution."""
import gzip
from pathlib import Path
import sys
import envelope as e
import run as runner

def audit_prefix_union(directory,spec,result,candidate):
    output=directory/'packet-05-output';provenance=e.read(output/'provenance.json')
    e.require(spec['reference_packets']==result['reference_packets']==['packet-01','packet-04'] and result['status']=='COMPLETE_DECLARED_SMALL_PREFIX_VALIDATION','complete declared two-domain prefix result')
    e.require(result['environments']==60 and result['state_visits_per_representation']==result['reservation']==spec['reservation']==spec['exploration_visits']==1964,'exact shared union environments and state charge')
    e.require(result['all_certificate_bytes_equal'] is True and result['all_complete_summaries_equal'] is True and result['original_profiles_unchanged'] is True and result['reference_model_states_used'] is False and result['unrestricted_reduction_theorem'] is False and result['reduced_race_packets_validated'] is False,'bounded independent prefix validation claims')
    e.require([x['reference_packet'] for x in result['domains']]==[x['reference_packet'] for x in provenance['domains']]==spec['reference_packets'],'complete unique ordered domain/provenance membership')
    e.require(provenance['candidate']==candidate and provenance['run']==str(directory),'actual union provenance run/candidate')
    e.require([x['control'] for x in result['controls']]==spec['required_union_controls'] and all(x['detected'] is True for x in result['controls']),'declared union controls')
    def bindings(mapping,label):
        expected={'admission.json',label+'-admission.json',label+'-execution.json',label+'.log'}
        e.require(set(mapping)==expected and all(e.sha((directory/name).read_bytes())==h for name,h in mapping.items()),'exact preceding owned stage provenance hashes')
    environments=states=0
    for row,dynamic,visits in zip(result['domains'],provenance['domains'],spec['reference_shared_visits']):
        packet=row['reference_packet'];folder=output/packet;reference=directory/(packet+'-output')
        reference_spec=e.read(e.ROOT/e.packet_doc(packet)/packet/'spec.json');baseline=e.read(reference/'result.json');shared=e.read(folder/'result.json');retained=e.read(folder/'audit.json');generation_provenance=e.read(folder/'provenance.json');retained_provenance=e.read(folder/'audit-provenance.json')
        e.require(row['shared_result_sha256']==retained['shared_result_sha256']==e.sha((folder/'result.json').read_bytes()) and row['retained_audit_sha256']==e.sha((folder/'audit.json').read_bytes()),'actual shared result and retained audit binding')
        e.require(shared['reference_packet']==retained['reference_packet']==packet and shared['status']=='COMPLETE_SMALL_DOMAIN_PREFIX_EQUIVALENCE' and retained['status']=='COMPLETE_RETAINED_SHARED_AUDIT' and retained['model_reducers_executed'] is False,'both completed typed shared domain stages')
        e.require(shared['reference_result_sha256']==retained['reference_result_sha256']==e.sha((reference/'result.json').read_bytes()),'actual same-run reference result')
        e.require(shared['cases']==baseline['cases'] and shared['environments']==retained['environments']==row['environments']==reference_spec['environments'],'complete original case summary/environment equality')
        e.require(shared['state_visits_per_representation']==row['shared_visits']==visits and 2*shared['actual_visited_prefixes']==visits,'checked exact shared domain charge')
        e.require(row['certificate_files']==shared['certificate_files']==retained['certificates']=={x['artifact']:x['artifact_sha256'] for x in baseline['cases']},'complete generated/reference/audit certificate maps')
        e.require(len(shared['controls'])==spec['required_controls_by_reference'][packet] and len({x['control'] for x in shared['controls']})==len(shared['controls']) and all(x['detected'] is True for x in shared['controls']),'all distinct shared controls passed')
        e.require({p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}=={'result.json','provenance.json','audit.json','audit-provenance.json'}|set(row['certificate_files']),'exact complete retained shared domain file inventory')
        for name,h in row['certificate_files'].items():
            generated=(folder/name).resolve();original=(reference/name).resolve()
            e.require(generated.is_relative_to(folder.resolve()) and original.is_relative_to(reference.resolve()) and e.sha(generated.read_bytes())==h==e.sha(original.read_bytes()),'every actual same-run generated/reference certificate remains byte-identical')
        for value in (dynamic['reference'],generation_provenance):
            e.require(value['candidate']==candidate and value['run']==str(directory) and value['reference']==str(reference),'fresh exact source-reference provenance')
            bindings(value['bindings'],packet)
        bindings(dynamic['shared'],'packet-05-'+packet);bindings(dynamic['retained'],'packet-05-retained-'+packet)
        e.require(dynamic['audit_provenance_sha256']==e.sha((folder/'audit-provenance.json').read_bytes()),'actual owned retained provenance binding')
        e.require(retained_provenance['candidate']==candidate and retained_provenance['run']==str(directory) and retained_provenance['reference_bindings']==generation_provenance['bindings'] and retained_provenance['shared_owned_execution_bindings']==dynamic['shared'] and retained_provenance['shared_provenance_sha256']==e.sha((folder/'provenance.json').read_bytes()),'retained audit names actual generated/reference evidence')
        prior=e.read(directory/(packet+'-execution.json'));generated=e.read(directory/('packet-05-'+packet+'-execution.json'));audited=e.read(directory/('packet-05-retained-'+packet+'-execution.json'));union=e.read(directory/'packet-05-union-execution.json')
        time=lambda value:e.dt.datetime.fromisoformat(value)
        e.require(time(prior['finished_at'])<=time(generated['started_at'])<=time(generated['finished_at'])<=time(audited['started_at'])<=time(audited['finished_at'])<=time(union['started_at']),'actual preceding owned reference/generation/audit/union chronology')
        environments+=row['environments'];states+=row['shared_visits']
    e.require(environments==60 and states==1964,'complete two-domain audited union')

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
    states = (83900 if full else 0) + sum(e.read(e.ROOT / e.packet_doc(packet) / packet / 'spec.json')['reservation'] for packet in receipt['packets'])
    e.require(reservation['states'] == states and total <= e.policy(candidate)['ceiling'], 'exact state charge and cumulative budget')
    if full:
        e.require(e.read(directory / 'output/result.json') == e.read(e.ROOT / e.B7DOC / 'results.json'), 'historical Batch07 result')
        e.require(e.historical() == receipt['history'], 'preserved historical file closure')
    for packet in receipt['packets']:
        result = e.read(directory / (packet + '-output') / 'result.json')
        spec = e.read(e.ROOT / e.packet_doc(packet) / packet / 'spec.json')
        if spec.get('kind') == 'source-guard-combinatorics':
            symbolic_output = directory / (packet + '-output')
            e.require({p.relative_to(symbolic_output).as_posix() for p in symbolic_output.rglob('*') if p.is_file()} == {'orders.json.gz','result.json','retained-audit.json'}, 'exact complete symbolic output membership')
            retained = e.read(symbolic_output / 'retained-audit.json')
            e.require(result['status'] == 'COMPLETE_CONDITIONAL_SYMBOLIC_GUARD_CLASSIFICATION' and result['model_state_visits'] == result['model_histories_executed'] == 0, 'explicit symbolic-only result')
            e.require(retained['symbolic_work_units'] == result['symbolic_work_units'] == spec['expected_symbolic_work_units_per_command'] == 40345 and retained['model_state_visits'] == 0, 'actual symbolic accounting')
            e.require(result['controls'] == spec['required_controls'] and len(result['controls']) == 18, 'all declared symbolic controls')
            e.require(result['source_pins'] == spec['source_pins'] and result['units_under_hypotheses'] == spec['units_under_hypotheses'] and result['outcomes'] == spec['outcomes'] and result['occurrence_mapping'] == spec['occurrence_mapping'], 'exact source hypotheses and domain metadata')
            e.require(all(receipt['sources'][name]['working_sha256'] == h for name,h in spec['source_pins'].items()), 'symbolic source hypotheses bind enclosing committed snapshots')
            import json
            canonical_hypotheses = (json.dumps(spec['hypotheses'], sort_keys=True, separators=(',', ':')) + '\n').encode()
            e.require(result['hypothesis_sha256'] == e.sha(canonical_hypotheses), 'source-hypothesis bytes')
            generated = next(x for x in receipt['commands'] if x['label'] == packet+'-symbolic')
            inspected = next(x for x in receipt['commands'] if x['label'] == packet+'-symbolic-retained')
            e.require(e.dt.datetime.fromisoformat(generated['finished_at']) <= e.dt.datetime.fromisoformat(inspected['started_at']), 'fresh generation before owned retained audit')
            e.require(result['symbolic_orders'] == spec['symbolic_orders'] == 40320 and result['symbolic_work_units'] <= spec['per_command_work_limit'], 'bounded symbolic coverage')
            e.require(e.sha((directory / (packet + '-output') / 'orders.json.gz').read_bytes()) == result['orders_sha256'] == retained['orders_sha256'], 'actual symbolic artifact binding')
            e.require(retained['status'] == 'RETAINED_SYMBOLIC_CERTIFICATE_PASS' and retained['result_sha256'] == e.sha((directory / (packet + '-output') / 'result.json').read_bytes()), 'owned retained symbolic summary binding')
            e.require(result['spec_sha256'] == e.sha((e.ROOT / e.packet_doc(packet) / packet / 'spec.json').read_bytes()) and result['checker_sha256'] == e.sha((e.ROOT / e.CODE / 'guard_order.py').read_bytes()), 'actual symbolic spec/checker binding')
            accepted = e.ROOT / e.packet_doc(packet) / packet / 'results.json'
            if accepted.exists(): e.require(e.read(accepted) == result, 'accepted symbolic result equality')
            continue
        e.require(result['state_visits_per_representation'] == spec['exploration_visits'] <= spec['reservation'], 'checked actual packet visits')
        if packet == 'packet-05':
            audit_prefix_union(directory,spec,result,candidate)
        else:
            e.require(result['environments'] == spec['environments'] and result['schedules'] == spec['schedules_per_unit_outcome'], 'complete finite domain')
            for case in result['cases']:
                target = (directory / (packet + '-output') / case['artifact']).resolve()
                e.require(target.is_relative_to((directory / (packet + '-output')).resolve()), 'retained certificate containment')
                e.require(e.sha(target.read_bytes()) == case['artifact_sha256'], 'retained replay certificate binding')
        accepted = e.ROOT / e.packet_doc(packet) / packet / 'results.json'
        if accepted.exists(): e.require(e.read(accepted) == result, 'accepted packet result equality')
    e.require(e.size(directory) < 268435456, 'complete subject artifact bound')
    return dict(status='EXACT_RETAINED_RECEIPT_AUDIT_PASS', candidate=candidate, receipt=str(path), receipt_sha256=e.sha(path.read_bytes()),
                commands=len(expected), retained_files=len(receipt['files']), snapshots=len(receipt['sources']), cumulative_reserved_states=total,
                model_reducers_executed=False, historical_gates_rerun=False, checked_at=e.now().isoformat())

if __name__ == '__main__':
    result = audit(Path(sys.argv[1]))
    e.write(Path(sys.argv[2]), result)
    print(result['status'])
