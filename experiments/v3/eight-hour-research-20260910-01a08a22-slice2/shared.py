"""exact literal-prefix sharing validated against fresh unreduced certificates."""
import argparse
import copy
import datetime as dt
import gzip
import hashlib
import json
from pathlib import Path
import sys
from baseline import check as c
from baseline import ROOT, OLD_CODE, NEW_CODE, NEW_DOC, packet_doc, reference_script, added_module_paths
import selected
import prefix_kernel


CONTROLS=['stale-cross-run-reference','wrong-candidate-reference-job','cross-outcome-certificate','cross-profile-certificate','omitted-leaf','duplicate-replaces-leaf','swapped-schedule-file-mapping','cross-unit-certificate','typed-tuple-loss','chronological-index-corruption','non-witness-summary-corruption','wrong-reference-leaf-mapping','sibling-retained-state-mutation','omitted-root-charge','duplicate-prefix-execution','omitted-prefix-inventory','reused-cross-case-identity-proof','altered-non-witness-certificate','wrong-completion-mask-prefix-key','sibling-nested-state-mutation']

def required_controls(packet):return CONTROLS+(['sibling-causal-ledger-mutation'] if packet=='packet-01' else ['fabricated-pair-in-empty-ledger'])+['altered-reference-aggregate','altered-reference-minimum']+(['altered-reference-attestation-census'] if packet=='packet-04' else [])
def verify_controls(rows,packet):c.d.require([x['control'] for x in rows]==required_controls(packet) and all(x['detected'] is True for x in rows),'all declared nonvacuous shared controls detected')

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(raw): return hashlib.sha256(raw).hexdigest()
def typed(value): return json.dumps(c.codec.pack(c.artifact.encode(value)),sort_keys=True,separators=(',',':')).encode()
def fingerprint(value): return sha(typed(value))
def decode(raw): return c.artifact.decode(c.codec.unpack(json.loads(gzip.decompress(raw))))
def write(path,value):
    with path.open('x',encoding='utf-8') as stream: stream.write(json.dumps(value,indent=2)+'\n')

def declared(spec):
    c.d.require(spec['id'] in ('packet-01','packet-04'),'declared small reference packet')
    profile=c.domain(spec)
    schedules,count=(selected.inventory(profile) if spec['id']=='packet-04' else c.inventory(profile))
    c.d.require(count==spec['schedules_per_unit_outcome'] and len(schedules)*len(spec['units'])*len(spec['outcomes'])==spec['environments'],'exact original reference domain')
    c.d.require(tuple(spec['units'])==c.d.s.UNITS and tuple(spec['outcomes'])==tuple(profile['outcomes']),'same original environments')
    prefixes={()}
    for schedule in schedules:
        prefixes.update(schedule[:i] for i in range(1,len(schedule)+1))
    nodes={'packet-01':51,'packet-04':440}[spec['id']]
    c.d.require(len(prefixes)==nodes,'independent complete literal-prefix count')
    return profile,schedules,prefixes

def checked_owned_records(admission,initial,execution,wanted):
    candidate=admission['candidate']
    c.d.require(initial['status']=='ADMITTED_BEFORE_EXECUTION' and execution['status']=='PASS','admitted and successful owned stage')
    c.d.require(execution['candidate']==initial['candidate']==execution['source_commit']==initial['source_commit']==candidate,'same committed candidate for owned stage')
    c.d.require(execution['command']==initial['command']==wanted['command'] and execution['root']==initial['root']==wanted['root'],'actual exact declared owned command')
    c.d.require(execution['exit_code']==0 and execution['owned_active_after_cleanup']==0 and execution['cleanup_errors']==[],'successful owned stage cleanup')
    c.d.require(execution['seconds']<600 and execution['peak_memory_bytes']<=2147483648,'owned stage time/memory bounds')
    c.d.require(execution['started_at']==initial['started_at'] and dt.datetime.fromisoformat(admission['admitted_at'])<=dt.datetime.fromisoformat(execution['started_at'])<=dt.datetime.fromisoformat(execution['finished_at'])<=dt.datetime.now(dt.timezone.utc),'same-run preceding owned stage chronology')

def bind_owned(run,label):
    admission=read(run/'admission.json')
    wanted=[x for x in admission['expected_commands'] if x['label']==label]
    c.d.require(len(wanted)==1 and wanted[0]['root']==str(c.ROOT),'unique declared current-root owned stage')
    initial=read(run/(label+'-admission.json'));execution=read(run/(label+'-execution.json'))
    checked_owned_records(admission,initial,execution,wanted[0])
    c.d.require(execution['log_sha256']==sha((run/(label+'.log')).read_bytes()),'actual prior owned stage log binding')
    return {name:sha((run/name).read_bytes()) for name in ('admission.json',label+'-admission.json',label+'-execution.json',label+'.log')}

def source_modules():
    manifest=read(c.ROOT/'docs/v3/construction/cut-source-overnight-20260908/batch-07/manifest.json')
    allowed={x['path'] for x in manifest['inputs']}|set(manifest['sources'])
    allowed |= added_module_paths()
    actual=set()
    for module in tuple(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path:
            path=Path(path).resolve()
            if path.is_relative_to(c.ROOT) and path.suffix=='.py':actual.add(path.relative_to(c.ROOT).as_posix())
    c.d.require(actual<=allowed,'complete registered imported source closure')
    return sorted(actual)

def bind_reference(reference,spec_path,output):
    run=output.resolve().parent.parent
    c.d.require(output.resolve()==run/'packet-05-output'/read(spec_path)['id'],'exact shared output in same enclosing run')
    spec=read(spec_path);label=spec['id']
    definition_path=c.ROOT/NEW_DOC/'packet-05/spec.json';definition=read(definition_path)
    c.d.require(definition['id']=='packet-05' and definition['reference_packets']==['packet-01','packet-04'] and definition['reference_shared_visits']==[204,1760] and definition['required_controls_by_reference']=={'packet-01':23,'packet-04':24} and definition['reservation']==1964,'exact declared shared packet definition')
    c.d.require(reference.resolve()==run/(label+'-output'),'fresh same-run reference directory')
    admission=read(run/'admission.json');execution_path=run/(label+'-execution.json');execution=read(execution_path);initial=read(run/(label+'-admission.json'))
    candidate=admission['candidate'];script=reference_script(label)
    c.d.require(spec_path.resolve()==c.ROOT/packet_doc(label)/label/'spec.json','exact inherited or successor reference spec path')
    command=[sys.executable,'-X','utf8','-B',script,'--spec',str(spec_path.resolve()),'--output',str(reference.resolve()),'--state-limit',str(spec['reservation'])]
    c.d.require(admission['status']=='ADMITTED_BEFORE_EXECUTION' and label in admission['packets'] and 'packet-05' in admission['packets'],'same admitted run includes fresh reference and shared validation')
    c.d.require(execution['command']==initial['command']==command and execution['root']==initial['root']==str(c.ROOT),'exact original fresh reference invocation')
    c.d.require(execution['candidate']==initial['candidate']==execution['source_commit']==initial['source_commit']==candidate,'reference same candidate and committed source')
    c.d.require(admission['python_executable']==sys.executable and admission['python_sha256']==sha(Path(sys.executable).read_bytes()),'same exact interpreter')
    c.d.require(execution['status']=='PASS' and execution['exit_code']==0 and execution['owned_active_after_cleanup']==0 and execution['cleanup_errors']==[],'successful preceding owned reference job')
    c.d.require(initial['status']=='ADMITTED_BEFORE_EXECUTION' and execution['started_at']==initial['started_at'],'actual reference admission binding')
    c.d.require(dt.datetime.fromisoformat(admission['admitted_at'])<=dt.datetime.fromisoformat(execution['started_at'])<=dt.datetime.fromisoformat(execution['finished_at'])<=dt.datetime.now(dt.timezone.utc),'reference completed before comparison')
    for path in (spec_path,definition_path,c.ROOT/script,*(c.ROOT/name for name in source_modules())):
        rel=path.resolve().relative_to(c.ROOT).as_posix()
        c.d.require(admission['sources'][rel]['working_sha256']==sha(path.read_bytes()),'committed snapshotted source/spec bytes')
    c.d.require(execution['log_sha256']==sha((run/(label+'.log')).read_bytes()),'actual owned reference log')
    files=bind_owned(run,label)
    return dict(candidate=candidate,run=str(run),reference=str(reference.resolve()),checked_at=dt.datetime.now(dt.timezone.utc).isoformat(),bindings=files)

def aggregate(profile,schedules,rows,spec):
    result=dict(strict_complete=sum(x['strict_complete'] for x in rows),extended_complete=sum(x['extended_complete'] for x in rows),
                visible_events=sum(x['visible_events'] for x in rows),matching_responses=sum(x['matching_responses'] for x in rows),
                matching_journals=sum(x['matching_journals'] for x in rows),identity_poststates=sum(x['identity_poststates'] for x in rows),
                domain_profile_sha256=c.d.digest(profile),schedule_inventory_sha256=c.d.digest(schedules))
    best={'strict':None,'extended':None}
    label=('earliest failing prefix across all 48 histories in the declared 24-order subset' if spec['id']=='packet-04' else 'earliest failing prefix across all completed histories in this declared domain')
    for item in rows:
        for kind in best:
            prefix=item[kind+'_first_gap']
            if prefix is not None and (best[kind] is None or prefix<best[kind]['prefix']):
                best[kind]=dict(case=item['case'],prefix=prefix,artifact=item['artifact'],prefix_actions=item['schedule'][:prefix],minimality=label)
    result['minimized_prefixes']=best
    if spec['id']=='packet-04':
        census={}
        for item in rows:
            decisions=[x for x in item['decisions'] if x.startswith('source-attest:')]
            c.d.require(len(decisions)==1,'one original attestation occurrence per selected history')
            census[decisions[0]]=census.get(decisions[0],0)+1
        result['observed_attestation_decisions']=census
    return result

def verify_aggregate(reference_result,profile,schedules,rows,spec):
    actual=aggregate(profile,schedules,rows,spec)
    c.d.require({k:reference_result[k] for k in actual}==actual,'complete aggregate census and original-order earliest prefix minimum from every independent case')
    return actual

def reference_rows(reference,spec,schedules):
    result=read(reference/'result.json')
    c.d.require(result['packet']==spec['id'] and result['status']=='COMPLETE_DECLARED_FINITE_DOMAIN' and result['environments']==spec['environments'],'completed fresh unreduced reference domain')
    c.d.require(result['state_visits_per_representation']==spec['exploration_visits'] and result['reservation']==spec['reservation'],'unreduced reference charge')
    rows=result['cases']; expected=[]
    for index,schedule in enumerate(schedules):
        for unit in spec['units']:
            for outcome in spec['outcomes']:
                expected.append((spec['id']+'/'+str(index).zfill(6)+'/'+unit+'/'+str(outcome),schedule))
    c.d.require(len(rows)==len(expected),'complete reference case inventory')
    for i,(row,(name,schedule)) in enumerate(zip(rows,expected)):
        c.d.require(row['case']==name and tuple(row['schedule'])==schedule and row['artifact']==str(i).zfill(6)+'.json.gz','original reference case/index/file mapping')
        p=(reference/row['artifact']).resolve()
        c.d.require(p.is_relative_to(reference.resolve()) and sha(p.read_bytes())==row['artifact_sha256'],'actual contained unreduced reference certificate')
    c.d.require({p.relative_to(reference).as_posix() for p in reference.rglob('*') if p.is_file()}=={'result.json'}|{x['artifact'] for x in rows},'exact fresh unreduced reference file membership')
    return rows

def summary(case,name,raw):
    row=c.summarize(case);row.update(artifact=name,artifact_sha256=sha(raw))
    return json.loads(json.dumps(row))

def verify_case(case,raw,expected,reference,spec,schedules):
    c.d.require(c.d.exact(c.audit_case(case),case['prefixes']),'independent complete shared certificate audit')
    c.d.require(case['case']==expected['case'] and tuple(case['source']['actions'])==tuple(expected['schedule']),'original case and chronological literal schedule')
    c.d.require(summary(case,expected['artifact'],raw)==expected,'complete reference summary equality including non-witness cases')
    baseline=(reference/expected['artifact']).read_bytes()
    c.d.require(raw==baseline and c.d.exact(case,decode(baseline)),'independently generated compressed bytes and typed certificate equal unreduced reference')

def reject(controls,label,fn):
    try:fn()
    except ValueError:controls.append(dict(control=label,detected=True))
    else:raise ValueError('undetected prefix sharing control: '+label)

def explore(spec_path,reference,output,limit):
    spec=read(spec_path);provenance=bind_reference(reference,spec_path,output);modules=source_modules()
    profile,schedules,prefixes=declared(spec)
    expected=2*len(prefixes)*len(spec['units'])*len(spec['outcomes'])
    c.d.require(limit==expected,'finite exact shared initialization/edge charge')
    refs=reference_rows(reference,spec,schedules)
    output.mkdir(parents=True,exist_ok=False)
    original=c.d.digest(c.d.s.PROFILES);counter=c.Counter(limit);seen=set();cases={};sample=None;identity_sample=None
    # Reference objects are never transition inputs. Initial states and all edges below are independently generated.
    def consume(ordinal,case):
        nonlocal sample,identity_sample
        raw=gzip.compress(typed(case),compresslevel=6,mtime=0)
        target=output/(str(ordinal).zfill(6)+'.json.gz')
        with target.open('xb') as stream:stream.write(raw)
        actual=decode(target.read_bytes())
        c.d.require(c.d.exact(actual,case),'exact typed shared serialization')
        verify_case(actual,target.read_bytes(),refs[ordinal],reference,spec,schedules)
        cases[ordinal]=summary(actual,target.name,target.read_bytes())
        if sample is None:sample=(copy.deepcopy(actual),target.read_bytes(),ordinal)
        if identity_sample is None and any(x['identity_proof'] for x in actual['prefixes']):identity_sample=copy.deepcopy(actual)
    counter,seen,record=prefix_kernel.traverse(spec,profile,schedules,list(range(len(schedules))),limit,consume)
    wanted={(u,o,p) for u in spec['units'] for o in spec['outcomes'] for p in prefixes}
    c.d.require(seen==wanted and counter.visits==2*len(seen)==limit,'complete exact literal-prefix inventory and checked actual charge')
    c.d.require(set(cases)==set(range(spec['environments'])) and c.d.digest(c.d.s.PROFILES)==original,'every independently generated leaf and original profiles preserved')
    ordered=[cases[i] for i in range(len(cases))]
    c.d.require(ordered==refs,'complete ordered shared case summary equality')
    reference_result=read(reference/'result.json');aggregate_result=verify_aggregate(reference_result,profile,schedules,ordered,spec)
    controls=[];case,raw,ordinal=sample
    reject(controls,'stale-cross-run-reference',lambda:bind_reference(reference.parent.parent/reference.name,spec_path,output))
    run=output.resolve().parent.parent;admission=read(run/'admission.json');label=spec['id'];initial=read(run/(label+'-admission.json'));execution=read(run/(label+'-execution.json'));reference_command=next(x for x in admission['expected_commands'] if x['label']==label)
    wrong=copy.deepcopy(execution);wrong['candidate']='0'*40
    reject(controls,'wrong-candidate-reference-job',lambda:checked_owned_records(admission,initial,wrong,reference_command))
    wrong=copy.deepcopy(case);wrong['outcome']=2
    reject(controls,'cross-outcome-certificate',lambda:verify_case(wrong,raw,refs[ordinal],reference,spec,schedules))
    wrong=copy.deepcopy(case);wrong['source']['profile']['policy']='forged-policy'
    reject(controls,'cross-profile-certificate',lambda:verify_case(wrong,raw,refs[ordinal],reference,spec,schedules))
    def check_leaves(rows):c.d.require(rows==refs,'complete ordered independently generated leaf inventory')
    reject(controls,'omitted-leaf',lambda:check_leaves(ordered[:-1]))
    reject(controls,'duplicate-replaces-leaf',lambda:check_leaves(ordered[:-1]+ordered[:1]))
    bad=copy.deepcopy(ordered);bad[0]['artifact']=bad[1]['artifact'];reject(controls,'swapped-schedule-file-mapping',lambda:check_leaves(bad))
    bad=copy.deepcopy(case);bad['unit']=spec['units'][1-spec['units'].index(case['unit'])]
    reject(controls,'cross-unit-certificate',lambda:verify_case(bad,raw,refs[ordinal],reference,spec,schedules))
    bad=copy.deepcopy(case);bad['source']['actions']=list(bad['source']['actions'])
    reject(controls,'typed-tuple-loss',lambda:c.audit_case(bad))
    bad=copy.deepcopy(case);i=next(i for i,a in enumerate(bad['source']['actions']) if i!=int(a.rsplit('@',1)[1]));bad['rows'][i]['index']=int(bad['source']['actions'][i].rsplit('@',1)[1])
    reject(controls,'chronological-index-corruption',lambda:c.audit_case(bad))
    bad=copy.deepcopy(ordered[-1]);bad['matching_journals']+=1
    reject(controls,'non-witness-summary-corruption',lambda:c.d.require(bad==refs[-1],'every retained summary equality'))
    reject(controls,'wrong-reference-leaf-mapping',lambda:c.d.require(raw==(reference/refs[1-ordinal]['artifact']).read_bytes(),'independent output must match designated actual reference'))
    original_state=copy.deepcopy(case['source']['initial']);h=fingerprint(original_state);original_state['source_revision']+=1
    reject(controls,'sibling-retained-state-mutation',lambda:c.d.require(fingerprint(original_state)==h,'unchanged typed ancestor'))
    reject(controls,'omitted-root-charge',lambda:c.Counter(1).take(2))
    reject(controls,'duplicate-prefix-execution',lambda:record(spec['units'][0],spec['outcomes'][0],()))
    reject(controls,'omitted-prefix-inventory',lambda:c.d.require(seen==wanted-set([next(iter(wanted))]),'complete visited prefix inventory'))
    c.d.require(identity_sample is not None,'actual leaf identity proof control witness')
    bad=copy.deepcopy(identity_sample);prefix=next(i for i,x in enumerate(bad['prefixes']) if x['identity_proof']);bad['prefixes'][prefix]['identity_proof']['case']='other-case'
    reject(controls,'reused-cross-case-identity-proof',lambda:c.d.require(c.d.exact(c.audit_case(bad),bad['prefixes']),'fresh case-specific prefix identity audit'))
    last=decode((output/refs[-1]['artifact']).read_bytes());bad=copy.deepcopy(last);bad['rows'][-1]['responses_related']=not bad['rows'][-1]['responses_related']
    reject(controls,'altered-non-witness-certificate',lambda:c.audit_case(bad))
    wrong_keys={(u,o,frozenset(p)) for u,o,p in seen}
    reject(controls,'wrong-completion-mask-prefix-key',lambda:c.d.require(len(wrong_keys)==len(seen),'literal prefix order cannot collapse to completion mask'))
    nested=copy.deepcopy(case['adapter']['initial']);h=fingerprint(nested);nested['core']['forged-retained-field']=True
    reject(controls,'sibling-nested-state-mutation',lambda:c.d.require(fingerprint(nested)==h,'nested ancestor state unchanged'))
    bad=copy.deepcopy(case)
    if spec['id']=='packet-01':
        c.d.require(bool(bad['incarnation_pairs']),'nonempty actual causal ledger mutation witness')
        bad['incarnation_pairs'][0]['source_event']+=1
        reject(controls,'sibling-causal-ledger-mutation',lambda:c.audit_case(bad))
    else:
        c.d.require(not bad['incarnation_pairs'],'actual empty generation-one causal ledger witness')
        token=c.t.restore(case['source'])[-1]['source_generation'];bad['incarnation_pairs'].append(dict(source=token,target=token,reason='fabricated',source_event=0,target_event=0))
        reject(controls,'fabricated-pair-in-empty-ledger',lambda:c.audit_case(bad))
    bad=copy.deepcopy(reference_result);bad['strict_complete']+=1
    reject(controls,'altered-reference-aggregate',lambda:verify_aggregate(bad,profile,schedules,ordered,spec))
    bad=copy.deepcopy(reference_result);c.d.require(bad['minimized_prefixes']['strict'] is not None,'actual strict minimum control witness');bad['minimized_prefixes']['strict']['prefix']+=1
    reject(controls,'altered-reference-minimum',lambda:verify_aggregate(bad,profile,schedules,ordered,spec))
    if spec['id']=='packet-04':
        bad=copy.deepcopy(reference_result);key=next(iter(bad['observed_attestation_decisions']));bad['observed_attestation_decisions'][key]+=1
        reject(controls,'altered-reference-attestation-census',lambda:verify_aggregate(bad,profile,schedules,ordered,spec))
    verify_controls(controls,spec['id'])
    write(output/'result.json',dict(status='COMPLETE_SMALL_DOMAIN_PREFIX_EQUIVALENCE',reference_packet=spec['id'],reference_result_sha256=sha((reference/'result.json').read_bytes()),
          environments=len(ordered),prefix_nodes_per_environment=len(prefixes),state_visits_per_representation=counter.visits,actual_visited_prefixes=len(seen),visited_prefix_inventory_sha256=fingerprint(sorted(seen)),
          certificate_files={x['artifact']:x['artifact_sha256'] for x in ordered},aggregate=aggregate_result,cases=ordered,controls=controls,checker_sha256=sha(Path(__file__).read_bytes()),
          registered_local_modules=sorted(set(modules)|set(source_modules())),independent_initialization=True,reference_states_used_for_transitions=False,certificate_bytes_equal=True,unrestricted_reduction_theorem=False))
    after=bind_reference(reference,spec_path,output)
    c.d.require(after['bindings']==provenance['bindings'],'reference execution provenance unchanged through sharing')
    write(output/'provenance.json',provenance)
    print('COMPLETE_SMALL_DOMAIN_PREFIX_EQUIVALENCE',flush=True)

def audit_shared(spec_path,reference,output):
    spec=read(spec_path);provenance=bind_reference(reference,spec_path,output)
    run=output.resolve().parent.parent;owned=bind_owned(run,'packet-05-'+spec['id'])
    profile,schedules,prefixes=declared(spec);refs=reference_rows(reference,spec,schedules)
    result_path=output/'result.json';result=read(result_path);result_hash=sha(result_path.read_bytes())
    c.d.require(result['status']=='COMPLETE_SMALL_DOMAIN_PREFIX_EQUIVALENCE' and result['reference_packet']==spec['id'] and result['reference_result_sha256']==sha((reference/'result.json').read_bytes()),'actual complete shared result and fresh reference')
    expected_files={'result.json','provenance.json'}|{x['artifact'] for x in refs}
    c.d.require({p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}==expected_files,'complete shared output membership before retained audit')
    original_provenance=read(output/'provenance.json')
    c.d.require(all(provenance[k]==original_provenance[k] for k in ('candidate','run','reference','bindings')),'same actual shared reference execution provenance')
    seen={(u,o,p) for u in spec['units'] for o in spec['outcomes'] for p in prefixes}
    c.d.require(result['prefix_nodes_per_environment']==len(prefixes) and result['state_visits_per_representation']==2*len(seen) and result['actual_visited_prefixes']==len(seen) and result['visited_prefix_inventory_sha256']==fingerprint(sorted(seen)),'independent exact prefix inventory and visit arithmetic')
    actual=[];files={}
    for expected in refs:
        path=output/expected['artifact'];raw=path.read_bytes();case=decode(raw)
        verify_case(case,raw,expected,reference,spec,schedules)
        actual.append(summary(case,path.name,raw));files[path.name]=sha(raw)
    c.d.require(actual==result['cases']==refs and files==result['certificate_files'] and result['environments']==len(refs),'every actual certificate, summary and exhaustive environment inventory audited')
    c.d.require(result['aggregate']==verify_aggregate(read(reference/'result.json'),profile,schedules,actual,spec),'all retained actual aggregate and minimum values')
    verify_controls(result['controls'],spec['id'])
    c.d.require(sha(result_path.read_bytes())==result_hash and result['checker_sha256']==sha(Path(__file__).read_bytes()),'shared result unchanged and exact checker')
    write(output/'audit.json',dict(status='COMPLETE_RETAINED_SHARED_AUDIT',reference_packet=spec['id'],shared_result_sha256=result_hash,reference_result_sha256=sha((reference/'result.json').read_bytes()),certificates=files,environments=len(refs),model_reducers_executed=False,checker_sha256=sha(Path(__file__).read_bytes())))
    write(output/'audit-provenance.json',dict(candidate=provenance['candidate'],run=str(run),reference_bindings=provenance['bindings'],shared_owned_execution_bindings=owned,shared_provenance_sha256=sha((output/'provenance.json').read_bytes())))
    print('COMPLETE_RETAINED_SHARED_AUDIT',flush=True)

def union(spec_path,output):
    spec=read(spec_path);run=output.resolve().parent
    c.d.require(spec['id']=='packet-05' and spec['reference_packets']==['packet-01','packet-04'] and output.resolve()==run/'packet-05-output','exact declared two-domain union')
    results=[];provenance=[]
    for packet,visits in zip(spec['reference_packets'],spec['reference_shared_visits']):
        folder=output/packet;result=read(folder/'result.json');audit=read(folder/'audit.json');ap=read(folder/'audit-provenance.json')
        original_spec=c.ROOT/packet_doc(packet)/packet/'spec.json';reference=run/(packet+'-output')
        expected_members={'result.json','provenance.json','audit.json','audit-provenance.json'}|set(audit['certificates'])
        c.d.require({p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}==expected_members,'exact domain membership after retained audits')
        bound=bind_reference(reference,original_spec,folder);owned=bind_owned(run,'packet-05-'+packet);audited=bind_owned(run,'packet-05-retained-'+packet)
        c.d.require(ap['candidate']==bound['candidate'] and ap['run']==str(run) and ap['reference_bindings']==bound['bindings'] and ap['shared_owned_execution_bindings']==owned and ap['shared_provenance_sha256']==sha((folder/'provenance.json').read_bytes()),'retained audit binds actual shared/reference jobs')
        c.d.require(audit['status']=='COMPLETE_RETAINED_SHARED_AUDIT' and audit['reference_packet']==packet and audit['shared_result_sha256']==sha((folder/'result.json').read_bytes()) and audit['reference_result_sha256']==sha((reference/'result.json').read_bytes()) and audit['checker_sha256']==sha(Path(__file__).read_bytes()) and audit['model_reducers_executed'] is False,'complete exact retained shared audit')
        verify_controls(result['controls'],packet)
        c.d.require(audit['certificates']==result['certificate_files'] and audit['environments']==result['environments'] and result['state_visits_per_representation']==visits,'complete same-domain audit and state accounting')
        for name,h in audit['certificates'].items():c.d.require(sha((folder/name).read_bytes())==h==sha((reference/name).read_bytes()),'every actual generated/reference certificate still identical')
        results.append(dict(reference_packet=packet,shared_result_sha256=sha((folder/'result.json').read_bytes()),retained_audit_sha256=sha((folder/'audit.json').read_bytes()),environments=result['environments'],shared_visits=visits,certificate_files=audit['certificates']))
        provenance.append(dict(reference_packet=packet,reference=bound,shared=owned,retained=audited,audit_provenance_sha256=sha((folder/'audit-provenance.json').read_bytes())))
    c.d.require(sum(r['shared_visits'] for r in results)==spec['reservation']==spec['exploration_visits']==1964 and sum(r['environments'] for r in results)==60,'complete declared small-domain union')
    controls=[]
    def domains(rows):c.d.require([x['reference_packet'] for x in rows]==spec['reference_packets'],'complete ordered unique shared domain union')
    domains(results);reject(controls,'missing-reference-domain',lambda:domains(results[:-1]));reject(controls,'duplicate-reference-domain',lambda:domains(results[:-1]+results[:1]))
    write(output/'result.json',dict(status='COMPLETE_DECLARED_SMALL_PREFIX_VALIDATION',packet=spec['id'],reference_packets=spec['reference_packets'],environments=60,state_visits_per_representation=1964,reservation=1964,domains=results,controls=controls,all_certificate_bytes_equal=True,all_complete_summaries_equal=True,original_profiles_unchanged=True,reference_model_states_used=False,unrestricted_reduction_theorem=False,reduced_race_packets_validated=False,union_model_reducers_executed=False))
    write(output/'provenance.json',dict(candidate=read(run/'admission.json')['candidate'],run=str(run),domains=provenance))
    print('COMPLETE_DECLARED_SMALL_PREFIX_VALIDATION',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--spec',type=Path,required=True);parser.add_argument('--reference',type=Path);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--state-limit',type=int);parser.add_argument('--audit',action='store_true');parser.add_argument('--union',action='store_true');args=parser.parse_args()
    def deny(event,arguments):
        if event.startswith(('socket.','subprocess.')) or event in ('os.system','os.posix_spawn'):raise RuntimeError('model network/process operation refused: '+event)
    sys.addaudithook(deny)
    if args.union:
        c.d.require(not args.audit and args.reference is None and args.state_limit is None,'union executes no model reducers');union(args.spec,args.output)
    elif args.audit:
        c.d.require(args.reference is not None and args.state_limit is None,'retained audit executes no model reducers');audit_shared(args.spec,args.reference,args.output)
    else:
        c.d.require(args.reference is not None and args.state_limit is not None,'finite exploration inputs');explore(args.spec,args.reference,args.output,args.state_limit)
