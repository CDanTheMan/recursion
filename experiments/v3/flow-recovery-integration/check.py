"""Exact-candidate gate for conditional finite flow/recovery integration."""
import argparse,copy,datetime,json,pathlib,re,runpy,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='f86f169c61ca6db4a3d7870353f270e35ef954d6'
PREFIX='docs/v3/construction/flow-recovery-integration-20260907/'
CODE='experiments/v3/flow-recovery-integration/'
BRANCH='codex/v3-flow-recovery-integration-20260907'
AREA=ROOT/PREFIX
CANONICAL={'docs/v3/'+n for n in 'ARCHITECTURE.md EXECUTION-FABRIC.md TERMINAL-RUNTIME.md ACCEPTANCE.md ROADMAP.md CONSTRUCTION-RUNBOOK.md CLAIM-LEDGER.md CLAIM-REGISTRY.json'.split()}
SEMANTIC={'domain.py','specification.py','split_model.py','inclusive_model.py','audit.py','explore.py','experiment.py'}
CHECKPOINT='b3662685f3c6814b3c87208d64d3098ffa2c7681'
ADMITTED_PATHS={CODE+n for n in SEMANTIC|{'check.py'}}|{PREFIX+'goal.json'}
# Historical imports have generic module names. New model execution is isolated
# in a subprocess; never import its domain/explore into this interpreter.
RSM=runpy.run_path(str(ROOT/'experiments/v3/reset-mapping/check.py'))
FM=RSM['FM'];git,require,sha,canonical=FM['git'],FM['require'],FM['sha'],FM['canonical']
def load(path):return FM['strict'](path.read_text(encoding='utf8'))
def read(name):return load(AREA/name)
def common():return pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'))
def candidate_check(candidate):FM['candidate_check'](candidate)

def goal_check(g):
    require(g['id']=='recursion.v3.flow-recovery-integration.20260907' and g['parent_goal']=='goal-recursion-v2-execution-fabric' and g['start_commit']==BASE and g['branch']==BRANCH,'goal lineage')
    require(g['deadline_utc']=='2026-09-08T04:39:28Z' and g['discovery_cutoff_utc']=='2026-09-08T03:09:28Z','outer time/reserve')
    require(type(g['new_metered_spend']) is int and g['new_metered_spend']==0 and g['usage_resets_allowed'] is False and g['stop_on_observed_automatic_reset'] is True,'capacity authorization')
    require(g['capacity']['no_new_workers_at_remaining_percent']==6 and g['capacity']['checkpoint_at_remaining_percent']==3 and g['max_concurrent_read_only_workers']==4,'capacity reserve')
    require(set(g['allowed_paths'])==CANONICAL|{PREFIX+'**',CODE+'**'},'scope declaration')

def resume_check(r):
    require(r['parent_goal']=='goal-recursion-v2-execution-fabric' and r['campaign_goal']==read('goal.json')['id'] and r['checkpoint_commit']==CHECKPOINT,'continuation lineage')
    require(r['started_at']=='2026-09-08T03:40:23Z' and r['deadline_utc']==read('goal.json')['deadline_utc'],'continuation envelope')
    require(type(r['new_metered_spend'])is int and r['new_metered_spend']==0 and r['usage_resets_allowed'] is False and r['new_research_allowed'] is False,'continuation authority')
    require(r['max_concurrent_read_only_workers']==2 and set(r['allowed_paths'])==CANONICAL|{PREFIX+'**',CODE+'**'},'continuation scope')
    require(r['capacity']['baseline_used_percent']==1 and r['capacity']['baseline_reset_timestamp']==1789435401 and r['capacity']['no_new_workers_at_remaining_percent']==6 and r['capacity']['checkpoint_at_remaining_percent']==3,'continuation capacity')

def preflight():
    goal_check(read('goal.json'));resume_check(read('resume.json'));require(git('branch','--show-current')==BRANCH,'branch')
    for ancestor in [BASE,'a7cd9458d37f3090079930bf8d79ffd77c4f73e4']:git('merge-base','--is-ancestor',ancestor,'HEAD')
    owners=[r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+BRANCH in r.splitlines()]
    require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive ownership')
    require('status: active' in (ROOT/'state/goals/goal-recursion-v2-execution-fabric.md').read_text(),'active parent goal')
    require(not (ROOT/'state/PAUSE').exists() and not (common().parent/'state/PAUSE').exists(),'PAUSE state changed')
    prior=common()/'research-attestations/reset-mapping'/BASE;completion=load(prior/'completion.json')
    require(completion['status']=='published-scoped-campaign-complete' and completion['candidate']==BASE,'accepted predecessor')
    receipts=[]
    for name,digest in completion['receipts'].items():
        require(pathlib.Path(name).name==name and sha((prior/name).read_bytes())==digest,'predecessor receipt digest');receipts.append(load(prior/name))
    require(all(v['candidate']==BASE for v in receipts) and sum(v.get('status')=='RESET_MAPPING_GATE_PASS' for v in receipts)==2 and len({v['reviewer'] for v in receipts if v.get('verdict')=='approve'})==2,'two exact predecessor gates/reviews')

def preserve(changed):
    require(changed and all(p in CANONICAL or p.startswith(PREFIX) or p.startswith(CODE) for p in changed),'protected change')
    require(not git('diff','--name-only','--diff-filter=D',BASE),'deletion')
    for path in CANONICAL:
        old=git('show',BASE+':'+path);new=(ROOT/path).read_text(encoding='utf8')
        if path.endswith('.json'):
            a,b=json.loads(old),json.loads(new);b['ranges']=[r for r in b['ranges'] if r['prefix']!='FRI'];require(a==b,'historical registry changed')
        else:
            lines=iter(new.splitlines())
            for line in old.splitlines():require(any(line==n for n in lines),'historical content changed '+path)
    FM['HIST']['PRIOR']['document_gate'](changed)
    RSM['claims'](RSM['read']('evidence.json'));FM['claim_bindings'](FM['read']('evidence.json'));FM['IP']['claim_bindings'](FM['IP']['read']('evidence.json'))
    FM['HIST']['bindings'](FM['HIST']['read']('evidence.json'));FM['HIST']['bindings'](FM['HIST']['M']['read']('evidence.json'))

def semantic(result):
    value=copy.deepcopy(result);value.pop('elapsed_seconds',None)
    for p in value.get('profiles',[]):
        for key in ['seconds','peak_memory_bytes']:p['statistics'].pop(key,None)
    return value

def result_check(actual,expected):
    require(canonical(semantic(actual))==canonical(semantic(expected)),'executed semantic result differs')
    require(actual['status']=='conditional-integration-pass' and actual['formal_freeze'] is False and actual['full_formal_comparison_complete'] is False and type(actual['live_provider_calls'])is int and actual['live_provider_calls']==0,'claim scope')
    require(actual['calibrations']['exhaustive_nonempty_traces']==45240 and len(actual['calibrations']['prior_long_controls'])==12 and len(actual['calibrations']['special_controls'])==4,'literal oracle calibration')
    require([p['unit'] for p in actual['profiles']]==['event','utf8-byte'],'cursor coverage')
    for p in actual['profiles']:
        s=p['statistics'];f=p['fairness'];w=p['combined_witness']
        require(s['product_states']==97500 and s['transitions']==603827 and s['frontier']==0 and s['maximum_depth']==32 and s['depth_cutoff'] is None,'complete declared finite closure')
        require(f['pending_Stop_cyclic_components']==32500 and f['excluded_by_named_Stop_weak_fairness']==32500 and f['fair_bad_components']==0 and f['without_named_fairness_bad_components']==32500,'named fairness nonvacuity')
        require(len(p['witnesses'])==11 and len(w['labels'])==32 and w['decision']['status']=='accepted-reset' and w['decision']['requires_reset'] is True,'constructive witnesses and historical recovery')
        require(w['decision']['final_cursor']==(4 if p['unit']=='event' else 6),'cursor translation')
    require({m['mutant'] for m in actual['mutants']}=={'shared_stop','false_settlement','stage_overflow','false_gap','reset_erases_future','reset_credit','gap_credit','ignore_byte_credit','ignore_queue_bytes'} and all(m['status']=='counterexample' and m['trace'] for m in actual['mutants']),'nonvacuous semantic mutations')

def claims(e):
    ledger=(ROOT/'docs/v3/CLAIM-LEDGER.md').read_text(encoding='utf8');FM['HIST']['OLD']['registry_shape'](load(ROOT/'docs/v3/CLAIM-REGISTRY.json'),ledger)
    require({c['id'] for c in e['claims']}=={'FRI-001','FRI-002','FRI-003'} and len(e['claims'])==3,'claim identities')
    for c in e['claims']:
        require(c['state']=='modeled' and '| '+c['id']+' | '+c['statement']+' | '+c['state']+' |' in ledger,'claim statement/classification binding')
        require(c['canonical'] in CANONICAL and c['id'] in (ROOT/c['canonical']).read_text(encoding='utf8'),'canonical claim owner')

def admission_check(admission,execution,directory):
    require(admission['status']=='admitted-before-execution' and execution['status']=='finished','execution/admission status')
    times=[datetime.datetime.fromisoformat(x) for x in [admission['started_at'],execution['started_at'],execution['finished_at']]]
    require(all(t.tzinfo is not None for t in times) and times[0]<=times[1]<=times[2],'ordered aware execution timestamps')
    require(re.fullmatch('[0-9a-f]{40}',admission['source_commit']) is not None,'admitted commit format')
    git('merge-base','--is-ancestor',BASE,admission['source_commit']);git('merge-base','--is-ancestor',admission['source_commit'],'HEAD')
    require(len(admission['source_files'])==len(ADMITTED_PATHS) and {f['path'] for f in admission['source_files']}==ADMITTED_PATHS,'complete unique admitted sources')
    for f in admission['source_files']:
        target=directory/'source'/f['path'];raw=target.read_bytes()
        require(target.resolve().is_relative_to(directory.resolve()) and sha(raw)==f['sha256'],'prospective source snapshot')
        require(raw==git('show',admission['source_commit']+':'+f['path'],raw=True),'snapshot bytes match admitted commit')
    require(admission['command']==[admission['python'],'-X','utf8','-B',CODE+'experiment.py','--output',str(directory/'result.json')],'admitted command identity')
    require(admission['limits']=={'whole_process_timeout_seconds':900,'graph_states':500000,'graph_seconds':600,'graph_memory_bytes':4294967296},'admitted resource bounds')

def evidence_check(e,expected):
    require(e['start_commit']==BASE and e['formal_freeze'] is False and e['full_formal_comparison_complete'] is False and e['new_owner_questions']==[],'evidence scope')
    result_check(read('results.json'),expected);require(e['semantic_results_sha256']==sha(canonical(semantic(expected)).encode()),'result binding')
    cache=common()/'research-attestations/flow-recovery-integration/discovery'
    require(len(e['retained_runs'])>=1 and len({r['id'] for r in e['retained_runs']})==len(e['retained_runs']),'attempt accounting')
    require({r['id'] for r in e['retained_runs']}=={p.name for p in cache.iterdir() if p.is_dir() and (p/'admission.json').exists()},'all admitted discovery attempts retained')
    accepted=[]
    for row in e['retained_runs']:
        directory=cache/row['id'];require(directory.resolve().is_relative_to(cache.resolve()),'cache path')
        required={'admission.json','execution.json','stdout.txt'}|{'source/'+p for p in ADMITTED_PATHS}
        require(required<=set(row['files']) and set(row['files'])=={p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()},'complete retained file digest coverage')
        for name,digest in row['files'].items():
            target=directory/name;require(target.resolve().is_relative_to(directory.resolve()) and sha(target.read_bytes())==digest,'raw evidence digest')
        admission=load(directory/'admission.json');execution=load(directory/'execution.json')
        admission_check(admission,execution,directory)
        if row['id']==e['accepted_run']:
            require(type(execution['exit_code'])is int and execution['exit_code']==0 and row['status']=='conditional-integration-pass' and 'result.json' in row['files'],'accepted execution')
            require(e['accepted_source_commit']==admission['source_commit'],'accepted source commit binding')
            for name in SEMANTIC:require((directory/'source'/CODE/name).read_bytes()==(ROOT/CODE/name).read_bytes(),'executed semantic source identity')
            result_check(load(directory/'result.json'),expected);accepted.append(row)
    require(len(accepted)==1,'one accepted run');claims(e)

def manifest_check():
    m=read('manifest.json');require(m['start_commit']==BASE and m['parent_goal']=='goal-recursion-v2-execution-fabric' and m['new_owner_questions']==[],'manifest identity')
    expected=set(git('diff','--name-only','a497bae10dddc3adf176242aed878f83b4519316',BASE).splitlines())|{'CONTROL_PLANE.md','CLAUDE.md','ANCHOR.md','state/goals/goal-recursion-v2-execution-fabric.md','docs/v3/M1B-WIRE-PROFILE.md','docs/v3/M1B-EXECUTION-CONTRACTS.md','scripts/tests/v3/execution/reference_oracle.py','scripts/tests/v3/execution/fixtures/F-M1B-020.json','schemas/control-plane/v3/execution/schema.json'}
    require({i['path'] for i in m['inputs']}==expected and len(m['inputs'])==len(expected),'complete frozen manifest')
    for i in m['inputs']:require(sha(git('show',BASE+':'+i['path'],raw=True))==i['git_blob_sha256'],'frozen input bytes')
    for name in ['goal.json','plan.json','checkpoint.json']:
        require((AREA/name).read_bytes()==git('show',CHECKPOINT+':'+PREFIX+name,raw=True),'historical checkpoint/domain declaration changed')

def reject(fn,value):
    try:fn(value)
    except (ValueError,KeyError,TypeError,AssertionError):return
    raise ValueError('adversarial mutation accepted')

def working(out,runid):
    preflight();changed=sorted(set(git('diff','--name-only',BASE).splitlines()+git('ls-files','--others','--exclude-standard').splitlines()));preserve(changed);manifest_check()
    target=out/(runid+'-model.json')
    execution=FM['run_command']([sys.executable,'-X','utf8','-B',CODE+'experiment.py','--output',str(target)],ROOT,out,runid+'-model',timeout=900)
    result=load(target);evidence_check(read('evidence.json'),result);labels=[]
    for key,value in [('start_commit','0'*40),('new_metered_spend',1),('usage_resets_allowed',True),('deadline_utc','2099-01-01T00:00:00Z'),('stop_on_observed_automatic_reset',False)]:
        bad=copy.deepcopy(read('goal.json'));bad[key]=value;reject(goal_check,bad);labels.append('goal/'+key)
    reject(candidate_check,'0'*40);labels.append('wrong-candidate');reject(preserve,['CONTROL_PLANE.md']);labels.append('protected-path')
    for kind in ['formal_freeze','full_formal_comparison_complete','live_provider_calls','omit-profile','false-frontier','erase-witness','false-fairness','false-requires-reset','erase-mutant','corrupt-graph','erase-calibration']:
        bad=copy.deepcopy(result)
        if kind in ['formal_freeze','full_formal_comparison_complete']:bad[kind]=True
        elif kind=='live_provider_calls':bad[kind]=1
        elif kind=='omit-profile':bad['profiles'].pop()
        elif kind=='false-frontier':bad['profiles'][0]['statistics']['frontier']=1
        elif kind=='erase-witness':bad['profiles'][0]['witnesses'].popitem()
        elif kind=='false-fairness':bad['profiles'][0]['fairness']['fair_bad_components']=1
        elif kind=='false-requires-reset':bad['profiles'][0]['combined_witness']['decision']['requires_reset']=False
        elif kind=='erase-mutant':bad['mutants'].pop()
        elif kind=='corrupt-graph':bad['profiles'][0]['statistics']['graph_sha256']='0'*64
        else:bad['calibrations']['prior_long_controls'].pop()
        reject(lambda v:result_check(v,result),bad);labels.append(kind)
    for kind in ['erase-run','promote-claim','false-raw-digest','false-result-binding','false-source-commit','empty-file-digests','omit-admission-digest','omit-result-digest']:
        bad=copy.deepcopy(read('evidence.json'))
        if kind=='erase-run':bad['retained_runs']=[]
        elif kind=='promote-claim':bad['claims'][0]['state']='measured'
        elif kind=='false-raw-digest':bad['retained_runs'][0]['files']['result.json']='0'*64
        elif kind=='false-result-binding':bad['semantic_results_sha256']='0'*64
        elif kind=='false-source-commit':bad['accepted_source_commit']='0'*40
        elif kind=='empty-file-digests':bad['retained_runs'][0]['files']={}
        elif kind=='omit-admission-digest':bad['retained_runs'][0]['files'].pop('admission.json')
        else:bad['retained_runs'][0]['files'].pop('result.json')
        reject(lambda v:evidence_check(v,result),bad);labels.append(kind)
    directory=common()/'research-attestations/flow-recovery-integration/discovery'/read('evidence.json')['accepted_run']
    for kind in ['omit-source','duplicate-source','wrong-command','naive-time','reversed-time','wrong-limit']:
        a,x=load(directory/'admission.json'),load(directory/'execution.json')
        if kind=='omit-source':a['source_files'].pop()
        elif kind=='duplicate-source':a['source_files'][-1]=a['source_files'][0]
        elif kind=='wrong-command':a['command'][4]='unapproved.py'
        elif kind=='naive-time':a['started_at']='2026-09-08T01:21:25'
        elif kind=='reversed-time':x['finished_at']='2026-09-08T00:00:00Z'
        else:a['limits']['graph_states']=999999
        reject(lambda pair:admission_check(*pair,directory),(a,x));labels.append('admission/'+kind)
    for key,value in [('checkpoint_commit','0'*40),('new_metered_spend',1),('usage_resets_allowed',True),('new_research_allowed',True),('deadline_utc','2099-01-01T00:00:00Z')]:
        bad=copy.deepcopy(read('resume.json'));bad[key]=value;reject(resume_check,bad);labels.append('resume/'+key)
    return changed,labels,result,execution

def main():
    p=argparse.ArgumentParser();p.add_argument('--preflight',action='store_true');p.add_argument('--working',action='store_true');p.add_argument('--candidate');args=p.parse_args()
    if args.preflight:preflight();print('FLOW_RECOVERY_CONSTRUCTION_PREFLIGHT_PASS_NOT_FINAL');return
    if not args.working:candidate_check(args.candidate)
    out=common()/'research-attestations/flow-recovery-integration'/(args.candidate or 'working');out.mkdir(parents=True,exist_ok=True);runid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    changed,labels,result,execution=working(out,runid)
    if args.working:print('FLOW_RECOVERY_WORKING_PASS_NOT_FINAL '+json.dumps({'adversarial_checks':len(labels),'run_id':runid}));return
    inventory=read('validation-inventory.json');prior=FM['HIST']['read']('validation-inventory.json')
    require(inventory['start_commit']==BASE and inventory['regression_commands']==prior['regression_commands']==FM['HIST']['OLD']['regression_commands']() and len(inventory['regression_commands'])==25,'unchanged25')
    for item in prior['regression_entrypoints']:
        raw=git('show',args.candidate+':'+item['path'],raw=True);require(sha(raw)==item['sha256'] and raw==git('show',BASE+':'+item['path'],raw=True),'historical validator entrypoint')
    require(set(inventory['artifacts'])==set(changed)-{PREFIX+'validation-inventory.json'},'inventory coverage')
    for path,digest in inventory['artifacts'].items():require(sha(git('show',args.candidate+':'+path,raw=True))==digest,'artifact digest')
    git('diff','--check',BASE,args.candidate);frozen=[]
    for commit,branch,script in [(BASE,'codex/v3-reset-mapping-20260907','experiments/v3/reset-mapping/check.py'),(RSM['BASE'],'codex/v3-formal-comparison-20260907','experiments/v3/formal-comparison/check.py'),(FM['BASE'],'codex/v3-interface-probes-20260907','experiments/v3/interface-probes/check.py'),(FM['RESEARCH'],'codex/v3-formal-model-experiment','docs/v3/foundation-research/mark2-research/mark3-comparison/check.py')]:
        directory=FM['frozen_root'](commit,branch);frozen.append(FM['run_command']([sys.executable,'-X','utf8','-B',script,'--working'],directory,out,runid+'-frozen-'+commit[:7]))
        require(git('rev-parse','HEAD',root=directory)==commit and not git('status','--porcelain=v1','--untracked-files=all',root=directory),'frozen worktree changed')
    regressions=[FM['run_command']([sys.executable,*cmd[1:]],ROOT,out,runid+'-regression-'+str(n)) for n,cmd in enumerate(inventory['regression_commands'])]
    candidate_check(args.candidate)
    receipt={'status':'FLOW_RECOVERY_GATE_PASS','candidate':args.candidate,'base':BASE,'run_id':runid,'adversarial_checks':labels,'semantic_results_sha256':sha(canonical(semantic(result)).encode()),'model_execution':execution,'frozen_validations':frozen,'regressions':regressions,'artifacts':{p:sha(git('show',args.candidate+':'+p,raw=True)) for p in changed},'formal_freeze':False,'full_formal_comparison_complete':False}
    raw=(json.dumps(receipt,indent=2)+'\n').encode();(out/(runid+'.json')).write_bytes(raw);print('FLOW_RECOVERY_GATE_PASS '+json.dumps({'candidate':args.candidate,'run_id':runid,'receipt_sha256':sha(raw)}))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:print('FLOW_RECOVERY_GATE_FAIL '+str(exc),file=sys.stderr);sys.exit(1)
