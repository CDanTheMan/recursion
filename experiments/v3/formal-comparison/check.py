"""Exact-candidate gate for a conditional subsystem, never full formal acceptance."""
import argparse,copy,datetime,hashlib,json,os,pathlib,re,runpy,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[3]
PREFIX='docs/v3/construction/formal-comparison-20260907/'
CODE='experiments/v3/formal-comparison/'
AREA=ROOT/PREFIX
BASE='a497bae10dddc3adf176242aed878f83b4519316'
RESEARCH='51733c48537d91ad17774b0c05c48ec289a75517'
BRANCH='codex/v3-formal-comparison-20260907'
CANONICAL={'docs/v3/'+name for name in 'ARCHITECTURE.md EXECUTION-FABRIC.md TERMINAL-RUNTIME.md ACCEPTANCE.md ROADMAP.md CONSTRUCTION-RUNBOOK.md CLAIM-REGISTRY.json CLAIM-LEDGER.md'.split()}
MODEL_MODULES={'aggregate.py','split.py','inclusive.py','domain.py','explore.py','calibrations.py','experiment.py'}
sys.path.insert(0,str(ROOT/'experiments/v3/interface-probes'))
IP=runpy.run_path(str(ROOT/'experiments/v3/interface-probes/check.py'));HIST=IP['HIST'];strict=HIST['strict']
sys.path.insert(0,str(ROOT/CODE))
import aggregate,split,inclusive
from explore import flat,abstract,physical_type
from domain import LIMIT,CHANNEL,FRAME

def git(*args,root=ROOT,raw=False):
    value=subprocess.check_output(['git',*args],cwd=root)
    return value if raw else value.decode('utf8').strip()
def require(value,message):
    if not value:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return strict(path.read_text(encoding='utf8'))
def read(name):return load(AREA/name)
def common():return pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'))
def cache():return common()/'research-attestations/formal-comparison/discovery'
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)

def goal_check(goal):
    require(goal['id']=='recursion.v3.formal-comparison.construction.20260907' and goal['parent_goal']=='goal-recursion-v2-execution-fabric','goal parent/identity')
    require(goal['start_commit']==BASE and goal['branch']==BRANCH and goal['predecessor']=='recursion.v3.interface-probes.20260907','goal lineage')
    require(set(goal['allowed_paths'])==CANONICAL|{PREFIX+'**',CODE+'**'},'goal allowed scope')
    require(type(goal['new_metered_spend'])is int and goal['new_metered_spend']==0 and goal['usage_resets_allowed'] is False,'spend boundary')
    require(goal['max_concurrent_read_only_workers']==4 and goal['synthesis_review_reserve_minutes']>=90,'worker/review bounds')
    require(goal['deadline_utc']=='2026-09-08T04:39:28Z' and goal['outer_envelope_started_at']=='2026-09-07T22:39:28Z','outer envelope')

def preflight():
    goal=read('goal.json');goal_check(goal)
    require(git('branch','--show-current')==BRANCH,'actual branch')
    for ancestor in [BASE,RESEARCH,'a7cd9458d37f3090079930bf8d79ffd77c4f73e4']:git('merge-base','--is-ancestor',ancestor,'HEAD')
    owners=[e for e in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+BRANCH in e.splitlines()]
    require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree ownership')
    require('status: active' in (ROOT/'state/goals/goal-recursion-v2-execution-fabric.md').read_text(),'active parent')
    prior=common()/'research-attestations/interface-probes'/BASE;completion=load(prior/'completion.json')
    require(completion['candidate']==BASE and completion['status']=='published-scoped-campaign-complete','predecessor accepted')
    receipts=[]
    for name,digest in completion['receipts'].items():
        require(pathlib.Path(name).name==name and sha((prior/name).read_bytes())==digest,'predecessor receipt binding');receipts.append(load(prior/name))
    gates=[r for r in receipts if r.get('status')=='INTERFACE_PROBE_GATE_PASS'];reviews=[r for r in receipts if r.get('verdict')=='approve']
    require(len(gates)==len(reviews)==2 and all(r['candidate']==BASE for r in receipts) and len({r['reviewer'] for r in reviews})==2,'predecessor exact gates/reviews')
    return goal

def candidate_check(candidate):
    require(isinstance(candidate,str) and re.fullmatch('[0-9a-f]{40}',candidate) and candidate==git('rev-parse','HEAD') and not git('status','--porcelain=v1','--untracked-files=all'),'clean exact candidate')

def preservation(changed,overrides=None):
    require(changed and all(p in CANONICAL or p.startswith(PREFIX) or p.startswith(CODE) for p in changed),'protected/out-of-scope change')
    require(not git('diff','--name-only','--diff-filter=D',BASE),'baseline deletion')
    overrides=overrides or {}
    for path in CANONICAL:
        old=git('show',BASE+':'+path);new=overrides.get(path,(ROOT/path).read_text(encoding='utf8'))
        if path.endswith('.json'):
            a,b=strict(old),strict(new)
            require({k:v for k,v in a.items() if k!='ranges'}=={k:v for k,v in b.items() if k!='ranges'},'registry shape')
            require(a['ranges']==[r for r in b['ranges'] if r['prefix']!='FMC'],'historical registry ranges')
        else:
            iterator=iter(new.splitlines())
            for line in old.splitlines():require(any(x==line for x in iterator),'historical canonical content changed: '+path)
    HIST['PRIOR']['document_gate'](changed)
    IP['claim_bindings'](IP['read']('evidence.json'))
    HIST['bindings'](HIST['read']('evidence.json'));HIST['bindings'](HIST['M']['read']('evidence.json'))

def coverage_check(coverage):
    source=HIST['read']('comparison-contract.json')
    require(coverage['source_contract_git_blob_sha256']==sha(git('show',BASE+':'+coverage['source_contract'],raw=True)),'preserved contract digest')
    for key in ['boundaries','obligations','core_bounds','cross_area_bounds','fairness','mapping_checks']:require(canonical(coverage[key])==canonical(source[key]),'full contract '+key)
    require(len(coverage['traces'])==27,'all original trace rows')
    for original,row in zip(source['traces'],coverage['traces']):
        require(canonical({k:v for k,v in row.items() if k not in {'construction_status','construction_result'}})==canonical(original),'historical trace changed')
        selected=row['id'][-2:] in ['01','02','26'];optional=row['id'].endswith('22')
        expected='partial-preventive-slice-checked' if selected else 'not-selected-unrun' if optional else 'unimplemented-unrun'
        require(row['construction_status']==expected,'false corpus coverage')
        if selected:require(row['construction_result']['run']==read('evidence.json')['accepted_run'] and row['construction_result']['status']=='conditional-subsystem-pass' and row['construction_result']['limit'],'partial result binding')
        else:require(row['construction_result'] is None,'unrun trace has result')
    require(coverage['full_comparison_complete'] is False and coverage['formal_freeze'] is False and coverage['rights_extension']=='not-selected-unrun','no premature freeze/rights selection')

def manifest_check():
    manifest=read('manifest.json');require(manifest['start_commit']==BASE and manifest['new_owner_questions']==[],'manifest boundary')
    expected={'CONTROL_PLANE.md','CLAUDE.md','ANCHOR.md','state/goals/goal-recursion-v2-execution-fabric.md'}
    expected|={'docs/v3/'+n for n in 'M1A-WIRE-PROFILE.md M1B-WIRE-PROFILE.md M1B-EXECUTION-CONTRACTS.md M1C-WIRE-PROFILE.md ARCHITECTURE.md EXECUTION-FABRIC.md TERMINAL-RUNTIME.md ACCEPTANCE.md ROADMAP.md CONSTRUCTION-RUNBOOK.md CLAIM-REGISTRY.json CLAIM-LEDGER.md'.split()}
    for folder in ['docs/v3/foundation-research/mark2-research/mark3-comparison','docs/v3/construction/interface-probes-20260907','experiments/v3/interface-probes']:
        expected|={p.relative_to(ROOT).as_posix() for p in (ROOT/folder).iterdir() if p.is_file()}
    expected|={'scripts/tests/v3/execution/reference_oracle.py','scripts/tests/v3/execution/fixtures/F-M1B-020.json','schemas/control-plane/v3/execution/schema.json'}
    require(len(manifest['inputs'])==len(expected) and {x['path'] for x in manifest['inputs']}==expected,'complete frozen input manifest')
    for item in manifest['inputs']:require(sha(git('show',BASE+':'+item['path'],raw=True))==item['git_blob_sha256'],'frozen input bytes')
    domains=read('domains.json')
    require(domains['full_profile_execution']=='unimplemented-unrun' and domains['no_identity_symmetry'] is True and domains['no_internal_transition_depth_cutoff'] is True,'domain limits')
    require(domains['slice']['queue_slot_limit_per_stage']==1 and domains['slice']['total_inflight_messages']==2 and domains['slice']['credit_source_offers']==2,'nonvacuous slice capacities')
    require(domains['slice']['semantic_boundary'] and domains['slice']['loss_assumption'] and domains['slice']['control_assumption'],'named unimplemented mapping assumptions')

def replay(trace,kind,mutant=None):
    state=split.Split() if kind=='split' else inclusive.Inclusive();next_fn=split.successors if kind=='split' else inclusive.successors
    before=state;last=None
    for item in trace:
        label=tuple(item);matches=[target for action,target in next_fn(state,mutant) if action==label]
        require(len(matches)==1,'unreachable/ambiguous retained model trace');before,state,last=state,matches[0],label
    return before,state,last

def result_check(result):
    require(result['kind']=='finite-subsystem-model-experiment' and result['status']=='conditional-subsystem-pass' and result['formal_freeze'] is False and type(result['live_provider_calls'])is int and result['live_provider_calls']==0,'result classification')
    models=result['models'];require(models['status']=='conditional-subsystem-pass' and models['full_comparison_complete'] is False and models['formal_freeze'] is False,'subsystem scope')
    for name in ['split','inclusive']:
        s=models[name];require(all(type(s[k])is int for k in ['reachable_states','transitions','maximum_discovered_depth','frontier','process_peak_working_set_bytes']),'typed graph counters')
        require(s['reachable_states']==444834 and s['transitions']==2644215 and s['maximum_discovered_depth']==35 and s['frontier']==0 and s['internal_transition_depth_cutoff'] is None and s['reductions']==[],'retained complete graph result')
        fair=models['fairness'][name];require(fair['fair_bad_components']==0 and fair['cyclic_components']>0 and fair['excluded_by_named_weak_fairness'].get('stop_apply',0)>0,'nonvacuous named fairness')
    require(models['graph_sha256']=='a4c924f5952cc174aca3284f9d8f6b7ada5da911ec0fc0579e960e00fca08d0c' and all(v is True for v in models['mapping_checks'].values()),'retained graph/relation evidence')
    witnesses=models['positive_witnesses'];expected={'legitimate_event','legitimate_reset','Stop_with_full_inflight','Stop_with_blocked_upstream_pump','Stop_with_full_partial_frame','non_EVENT_gap_refusal','refusal_survives_RESET','loss','framing_unknown/oversize','framing_unknown/eof','local_Stop_preserves_external_unknown','loss_supersedes_flow_recovery'}
    require(set(witnesses)==expected,'all positive witnesses')
    for name,trace in witnesses.items():
        require(trace,'empty positive witness')
        for boundary in ['split','inclusive']:
            before,after,last=replay(trace,boundary);bf,af=flat(before),flat(after)
            require(physical_type(after),'witness physical type')
            condition={'legitimate_event':last==('message','E1','event'),'legitimate_reset':last==('message','RESET','reset'),
                'Stop_with_full_inflight':last==('stop_request',) and sum(map(len,bf[6]))==2,
                'Stop_with_blocked_upstream_pump':last==('stop_request',) and any(bf[6][n] and len(bf[6][n+1])==1 for n in [0,1]),
                'Stop_with_full_partial_frame':last==('stop_request',) and bf[7]==2,
                'non_EVENT_gap_refusal':last==('message','CREDIT','gap-continuation'),'refusal_survives_RESET':last==('message','RESET','refused'),
                'loss':last==('loss',) and af[9] is True,'framing_unknown/oversize':last==('framing_unknown','oversize') and af[9] is True,
                'framing_unknown/eof':last==('framing_unknown','eof') and af[9] is True,
                'local_Stop_preserves_external_unknown':last==('stop_apply',) and af[0]==2 and af[1] is True,
                'loss_supersedes_flow_recovery':last==('loss',) and bf[2]==3 and af[2]==1}[name]
            require(condition,'wrong positive witness '+name)
    mutants=models['mutant_counterexamples'];names={'shared_control','gap_event_only','reset_credit','refusal_reset','hidden_loss','loss_retains_flow','unbounded_frame','queue_overflow','stage_overflow','false_settlement','deny_event'}
    require(len(mutants)==22 and {(m['boundary'],m['mutant']) for m in mutants}=={(b,m) for b in ['split','inclusive'] for m in names},'complete discriminating mutant set')
    for row in mutants:
        counter=row['counterexample'];require(counter['trace'] and counter['violation'],'empty mutant counterexample')
        before,after,last=replay(counter['trace'],row['boundary'],row['mutant'])
        if counter['violation']=='aggregate step/stutter refinement':require(aggregate.step(abstract(before),last)!=abstract(after),'mutant no longer violates refinement')
        elif counter['violation']=='independent Stop admission':
            next_fn=split.successors if row['boundary']=='split' else inclusive.successors
            require(flat(after)[0]==0 and not any(label==('stop_request',) for label,_ in next_fn(after,row['mutant'])),'mutant no longer blocks Stop')
        elif counter['violation']=='bounded pipeline':
            queues=flat(after)[6];require(sum(map(len,queues))>LIMIT or any(len(q)>CHANNEL for q in queues),'mutant no longer exceeds pipeline bound')
        elif counter['violation']=='bounded partial frame':require(not 0<=flat(after)[7]<=FRAME,'mutant no longer exceeds frame bound')
        else:raise ValueError('unexpected mutant class')
    calibrations=result['calibrations'];require(set(calibrations)=={'hidden_choice','weak_fairness','concrete_types','immutable_wire_controls'},'all method/oracle controls')
    hidden=calibrations['hidden_choice'];require(hidden['finite_prefix_inclusion']['included'] is True and hidden['reverse_inclusion']['included'] is True and not any(hidden['naive_state_map'].values()) and hidden['visible_negative']['included'] is False,'hidden-choice discriminator')
    fair=calibrations['weak_fairness'];require(fair['exit_only_Stop']['fair_bad_components']==0 and fair['coarse_broker_fairness']['fair_bad_components']==1 and fair['intermittent_Stop']['fair_bad_components']==1 and fair['internal_action']['fair_bad_components']==1 and fair['acyclic']['cyclic_components']==0,'fairness calibration cases')
    wire=calibrations['immutable_wire_controls'];require(wire['status']=='paired-guard-controls-pass-not-full-wire-refinement' and len(wire['literal_cases'])==14,'literal oracle case inventory')
    seam=wire['unimplemented_RESET_mapping_counterexample'];require(seam['wire_after_omitting_prevented_EVENT']['status']=='refused' and 'unexpected-reset' in seam['wire_after_omitting_prevented_EVENT']['reasons'],'unimplemented adapter seam')

def evidence_check(evidence):
    require(evidence['start_commit']==BASE and evidence['full_comparison_complete'] is False and evidence['formal_freeze'] is False and evidence['actual_live_provider_results']==[] and evidence['new_owner_questions']==[],'evidence boundary')
    index=load(cache()/'index.json');require(len(index['runs'])==len(evidence['retained_runs'])==2,'retain both model runs')
    accepted=[]
    for raw,public in zip(index['runs'],evidence['retained_runs']):
        require(canonical({k:v for k,v in raw.items() if k!='directory'})==canonical(public),'raw/public run projection')
        directory=pathlib.Path(raw['directory']).resolve();require(directory.is_relative_to(cache().resolve()),'run path escape')
        for name in ['admission','result']:require(sha((directory/(name+'.json')).read_bytes())==raw[name+'_sha256'],'retained '+name+' bytes')
        admission=load(directory/'admission.json');require(canonical(admission['sources'])==canonical(raw['sources']) and admission['candidate']==raw['candidate_at_admission'],'admitted source identity')
        require(admission['timeout_seconds']==900 and admission['new_metered_spend']==0 and admission['formal_freeze'] is False,'execution bounds')
        require({CODE+n for n in MODEL_MODULES}<=(set(admission['sources'])),'complete semantic source snapshot')
        for path,digest in admission['sources'].items():
            require(path.startswith(CODE) or path==PREFIX+'domains.json','snapshot source path')
            snapshot=(directory/'snapshot'/path).resolve();require(snapshot.is_relative_to((directory/'snapshot').resolve()) and sha(snapshot.read_bytes())==digest,'executed snapshot bytes')
        if raw['use']=='accepted-scoped-model-evidence':
            accepted.append(raw['id']);require(raw['id']==evidence['accepted_run'],'accepted run identity')
            for path in [*(CODE+n for n in MODEL_MODULES),PREFIX+'domains.json']:
                require((directory/'snapshot'/path).read_text()==(ROOT/path).read_text(),'accepted semantic model/configuration changed')
            require(canonical(load(directory/'result.json'))==canonical(read('results.json')),'published model result differs from executed result')
    require(accepted==[evidence['accepted_run']],'unique accepted model run')
    require(evidence['results_sha256']==sha((AREA/'results.json').read_bytes()),'public results digest')
    result_check(read('results.json'));claim_bindings(evidence)

def claim_bindings(evidence):
    ledger=(ROOT/'docs/v3/CLAIM-LEDGER.md').read_text();registry=load(ROOT/'docs/v3/CLAIM-REGISTRY.json')
    HIST['OLD']['registry_shape'](registry,ledger)
    rows=re.findall(r'^\| (FMC-\d{3}) \| ([^|]*)\| ([^|]*)\|',ledger,re.M)
    require(len(rows)==4 and {r[0] for r in rows}=={f'FMC-{n:03}' for n in range(1,5)},'claim ledger identity set')
    require(len(evidence['claims'])==4 and {c['id'] for c in evidence['claims']}=={r[0] for r in rows},'evidence claim set')
    mapped={r[0]:r for r in rows};expected={'FMC-001':('source-documented','immutable_wire_controls'),'FMC-002':('modeled','calibrations'),'FMC-003':('modeled','models'),'FMC-004':('modeled','unimplemented_RESET_mapping_counterexample')}
    for claim in evidence['claims']:
        row=mapped[claim['id']];require(row[1].strip()==claim['statement'] and row[2].strip()==claim['state'] and (claim['state'],claim['binding'])==expected[claim['id']],'claim statement/state/binding')
        require(claim['canonical'] in CANONICAL and claim['id'] in (ROOT/claim['canonical']).read_text(),'canonical claim owner')

def reject(fn,item,label):
    try:fn(item)
    except (ValueError,KeyError,TypeError,AssertionError):return label
    raise ValueError('accepted adversarial mutation: '+label)

def adversarial():
    labels=[]
    for field,value in [('new_metered_spend',1),('usage_resets_allowed',True),('allowed_paths',['CONTROL_PLANE.md']),('start_commit','0'*40)]:
        value_goal=copy.deepcopy(read('goal.json'));value_goal[field]=value;labels.append(reject(goal_check,value_goal,'goal/'+field))
    labels.append(reject(candidate_check,'0'*40,'wrong candidate'))
    labels.append(reject(preservation,['CONTROL_PLANE.md'],'protected path'))
    for field,value in [('full_comparison_complete',True),('formal_freeze',True),('rights_extension','selected')]:
        bad=copy.deepcopy(read('coverage.json'));bad[field]=value;labels.append(reject(coverage_check,bad,'coverage/'+field))
    for edit in ['omit-obligation','omit-trace','promote-partial']:
        bad=copy.deepcopy(read('coverage.json'))
        if edit=='omit-obligation':bad['obligations'].pop()
        elif edit=='omit-trace':bad['traces'].pop()
        else:bad['traces'][0]['construction_status']='complete'
        labels.append(reject(coverage_check,bad,edit))
    result=read('results.json')
    for boundary in ['split','inclusive']:
        for field,value in [('frontier',1),('reachable_states',0),('reachable_states',True),('internal_transition_depth_cutoff',20)]:
            bad=copy.deepcopy(result);bad['models'][boundary][field]=value;labels.append(reject(result_check,bad,boundary+'/'+field+'/'+str(value)))
    for edit in ['empty-witnesses','unreachable-witness','wrong-witness','missing-mutant','vacuous-mutant','hidden-choice-false-positive','coarse-fairness-false-positive','erase-RESET-seam']:
        bad=copy.deepcopy(result)
        if edit=='empty-witnesses':bad['models']['positive_witnesses']={}
        elif edit=='unreachable-witness':bad['models']['positive_witnesses']['legitimate_event']=[['message','E1','event']]
        elif edit=='wrong-witness':bad['models']['positive_witnesses']['legitimate_event']=bad['models']['positive_witnesses']['legitimate_reset']
        elif edit=='missing-mutant':bad['models']['mutant_counterexamples'].pop()
        elif edit=='vacuous-mutant':bad['models']['mutant_counterexamples'][0]['counterexample']['trace']=[]
        elif edit=='hidden-choice-false-positive':bad['calibrations']['hidden_choice']['naive_state_map']['a0']=True
        elif edit=='coarse-fairness-false-positive':bad['calibrations']['weak_fairness']['coarse_broker_fairness']['fair_bad_components']=0
        else:bad['calibrations']['immutable_wire_controls']['unimplemented_RESET_mapping_counterexample']['wire_after_omitting_prevented_EVENT']['status']='accepted'
        labels.append(reject(result_check,bad,edit))
    bad=copy.deepcopy(read('evidence.json'));bad['claims'][2]['state']='measured';labels.append(reject(claim_bindings,bad,'claim promoted to measured'))
    bad=copy.deepcopy(read('evidence.json'));bad['retained_runs'].pop();labels.append(reject(evidence_check,bad,'earlier run removed'))
    bad=copy.deepcopy(read('evidence.json'));bad['retained_runs'][1]['result_sha256']='0'*64;labels.append(reject(evidence_check,bad,'wrong retained result bytes'))
    return labels

def working_checks():
    preflight();manifest_check();coverage_check(read('coverage.json'));evidence_check(read('evidence.json'))
    changed=sorted(set(git('diff','--name-only',BASE).splitlines()+git('ls-files','--others','--exclude-standard').splitlines()))
    preservation(changed);mutants=adversarial();return changed,mutants

def comparable(value):
    if isinstance(value,dict):return {k:comparable(v) for k,v in value.items() if k not in {'seconds','process_peak_working_set_bytes','elapsed_seconds','started_at','ended_at'}}
    if isinstance(value,list):return [comparable(v) for v in value]
    return value

def run_command(command,root,out,name,timeout=240):
    before=time.perf_counter();r=subprocess.run(command,cwd=root,env=IP['command_env'](),capture_output=True,timeout=timeout)
    raw=r.stdout+r.stderr;(out/(name+'.log')).write_bytes(raw)
    receipt={'command':command,'exit_code':r.returncode,'seconds':round(time.perf_counter()-before,6),'output_sha256':sha(raw)}
    print(json.dumps(receipt),flush=True);require(r.returncode==0,'command failed: '+name);return receipt

def frozen_root(commit,branch):
    found=[]
    for entry in git('worktree','list','--porcelain').split('\n\n'):
        lines=entry.splitlines()
        if 'HEAD '+commit in lines and 'branch refs/heads/'+branch in lines:found.append(pathlib.Path(lines[0][9:]))
    require(len(found)==1 and not git('status','--porcelain=v1','--untracked-files=all',root=found[0]),'required frozen worktree absent/dirty')
    return found[0]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');parser.add_argument('--working',action='store_true');parser.add_argument('--candidate');args=parser.parse_args();preflight()
    if args.preflight:print('FORMAL_CONSTRUCTION_PREFLIGHT_PASS_NOT_FINAL');return
    if not args.working:candidate_check(args.candidate)
    changed,mutants=working_checks()
    if args.working:print(json.dumps({'status':'FORMAL_WORKING_PASS_NOT_FINAL','retained_runs':2,'adversarial_checks':len(mutants),'formal_freeze':False}));return
    git('diff','--check',BASE,args.candidate);inventory=read('validation-inventory.json');prior=HIST['read']('validation-inventory.json')
    require(inventory['regression_commands']==prior['regression_commands']==HIST['OLD']['regression_commands']() and len(inventory['regression_commands'])==25,'unchanged25 regression inventory')
    for item in prior['regression_entrypoints']:
        raw=git('show',args.candidate+':'+item['path'],raw=True);require(sha(raw)==item['sha256'] and raw==git('show',BASE+':'+item['path'],raw=True),'historical entrypoint changed')
    require(set(inventory['artifacts'])==set(changed)-{PREFIX+'validation-inventory.json'},'artifact coverage')
    for path,digest in inventory['artifacts'].items():require(sha(git('show',args.candidate+':'+path,raw=True))==digest,'artifact digest')
    out=common()/'research-attestations/formal-comparison'/args.candidate;out.mkdir(parents=True,exist_ok=True);runid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    model_path=out/(runid+'-model-result.json');model=run_command([sys.executable,'-X','utf8','-B',CODE+'experiment.py','--output',str(model_path)],ROOT,out,runid+'-model',900)
    reproduced=load(model_path);result_check(reproduced);require(canonical(comparable(reproduced))==canonical(comparable(read('results.json'))),'model/calibration reproduction differs')
    frozen=[]
    for commit,branch,script in [(BASE,'codex/v3-interface-probes-20260907','experiments/v3/interface-probes/check.py'),(RESEARCH,'codex/v3-formal-model-experiment','docs/v3/foundation-research/mark2-research/mark3-comparison/check.py')]:
        directory=frozen_root(commit,branch);receipt=run_command([sys.executable,'-X','utf8','-B',script,'--working'],directory,out,runid+'-frozen-'+commit[:7]);receipt['commit']=commit
        require(git('rev-parse','HEAD',root=directory)==commit and not git('status','--porcelain=v1','--untracked-files=all',root=directory),'frozen worktree changed');frozen.append(receipt)
    regressions=[]
    for index,command in enumerate(inventory['regression_commands']):
        receipt=run_command([sys.executable,*command[1:]],ROOT,out,runid+f'-regression-{index:02}');receipt['command']=command;regressions.append(receipt)
    candidate_check(args.candidate)
    receipt={'status':'FORMAL_SUBSYSTEM_GATE_PASS','candidate':args.candidate,'base':BASE,'run_id':runid,'adversarial_checks':mutants,'model_reproduction':model,'model_result_sha256':sha(model_path.read_bytes()),'frozen_validations':frozen,'current_candidate_regressions':regressions,'artifacts':{p:sha(git('show',args.candidate+':'+p,raw=True)) for p in changed},'formal_freeze':False,'full_comparison_complete':False,'live_provider_inference_validated':False}
    raw=(json.dumps(receipt,indent=2)+'\n').encode();(out/(runid+'.json')).write_bytes(raw);print('FORMAL_SUBSYSTEM_GATE_PASS '+json.dumps({'candidate':args.candidate,'run_id':runid,'receipt_sha256':sha(raw)}),flush=True)

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:print('FORMAL_CONSTRUCTION_GATE_FAIL '+str(exc),file=sys.stderr);sys.exit(1)
