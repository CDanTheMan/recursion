"""Exact candidate gate for the bounded composition subsystem; never full freeze."""
import argparse,copy,datetime,hashlib,json,pathlib,re,runpy,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='c6c05ad69e50d4acbeb429dfa3a15a8c3455d2a0'
PREFIX='docs/v3/construction/composition-model-20260908/'
CODE='experiments/v3/composition-model/'
AREA=ROOT/PREFIX
GRA=runpy.run_path(str(ROOT/'experiments/v3/generation-authority/check.py'));FM=GRA['FM']
CANONICAL=GRA['CANONICAL'];git=FM['git'];sha=FM['sha'];load=FM['load'];canonical=FM['canonical'];require=FM['require']
sys.path.insert(0,str(ROOT/CODE))
import cm_explore,cm_domain
ADMIT=runpy.run_path(str(ROOT/CODE/'run_packet.py'))

def read(n):return load(AREA/n)
def common():return pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'))
def cache():return common()/'research-attestations/composition-model'
def bound(directory,name):
    p=directory/name;require(p.resolve().is_relative_to(directory.resolve()),'evidence path escape');return p

def goal_check(g):
    require(g['id']=='recursion.v3.composition-model.20260908' and g['parent_goal']=='goal-recursion-v2-execution-fabric' and g['start_commit']==BASE,'goal identity')
    require(g['branch']=='codex/v3-composition-model-20260908' and g['predecessor']=='recursion.v3.generation-authority.20260907','goal lineage')
    require(type(g['new_metered_spend'])is int and g['new_metered_spend']==0 and g['usage_resets_allowed'] is False,'spend/reset')
    require(g['started_at']=='2026-09-08T06:58:05Z' and g['deadline_utc']=='2026-09-08T10:58:05Z' and g['discovery_cutoff_utc']=='2026-09-08T09:28:05Z' and g['synthesis_review_reserve_minutes']==90,'time envelope')
    require(set(g['allowed_paths'])==CANONICAL|{PREFIX+'**',CODE+'**'} and g['max_active_agents_owner']==10 and g['max_concurrent_read_only_workers']==4,'scope/concurrency')
    require(g['capacity']['no_new_workers_at_remaining_percent']==6 and g['capacity']['checkpoint_at_remaining_percent']==3,'capacity reserve')

def preflight():
    g=read('goal.json');goal_check(g);require(git('branch','--show-current')==g['branch'],'branch')
    for ancestor in [BASE,'a7cd9458d37f3090079930bf8d79ffd77c4f73e4']:git('merge-base','--is-ancestor',ancestor,'HEAD')
    owners=[r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+g['branch'] in r.splitlines()]
    require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree')
    require(not (ROOT/'state/PAUSE').exists() and not (common().parent/'state/PAUSE').exists(),'PAUSE')
    require('status: active' in (ROOT/'state/goals/goal-recursion-v2-execution-fabric.md').read_text(),'active parent')
    prior=common()/'research-attestations/generation-authority'/BASE;c=load(prior/'completion.json');require(c['candidate']==BASE and c['status']=='published-scoped-campaign-complete','predecessor completion')
    rs=[]
    for name,h in c['receipt_sha256'].items():
        raw=bound(prior,name).read_bytes();require(sha(raw)==h,'predecessor receipt hash');rs.append(load(prior/name))
    require(all(r['candidate']==BASE for r in rs) and sum(r.get('status')=='GENERATION_AUTHORITY_GATE_PASS' for r in rs)==2 and len({r['reviewer'] for r in rs if r.get('verdict')=='approve-publication'})==2,'predecessor exact gates/reviews')

def preservation(changed):
    require(changed and all(p in CANONICAL or p.startswith(PREFIX) or p.startswith(CODE) for p in changed),'allowed paths')
    require(not git('diff','--name-only','--diff-filter=D',BASE),'baseline deletion')
    for path in CANONICAL:
        old=git('show',BASE+':'+path);new=(ROOT/path).read_text(encoding='utf-8')
        if path.endswith('.json'):
            a,b=json.loads(old),json.loads(new);b['ranges']=[r for r in b['ranges'] if r['prefix']!='GCM'];require(a==b,'historical registry')
        else:
            it=iter(new.splitlines())
            for line in old.splitlines():require(any(line==x for x in it),'historical canonical content '+path)
    FM['HIST']['PRIOR']['document_gate'](changed)
    GRA['claims'](GRA['read']('evidence.json'));GRA['RSE']['claims'](GRA['RSE']['read']('evidence.json'));GRA['FRI']['claims'](GRA['FRI']['read']('evidence.json'))
    GRA['FRI']['RSM']['claims'](GRA['FRI']['RSM']['read']('evidence.json'));FM['claim_bindings'](FM['read']('evidence.json'));FM['IP']['claim_bindings'](FM['IP']['read']('evidence.json'))
    FM['HIST']['bindings'](FM['HIST']['read']('evidence.json'));FM['HIST']['bindings'](FM['HIST']['M']['read']('evidence.json'))

def manifests():
    m=read('manifest.json');expected={r['path'] for r in GRA['read']('manifest.json')['inputs']}|set(git('diff','--name-only',GRA['BASE'],BASE).splitlines())
    require(m['start_commit']==BASE and m['parent_goal']=='goal-recursion-v2-execution-fabric' and len(m['inputs'])==len(expected) and {r['path'] for r in m['inputs']}==expected,'input closure')
    for row in m['inputs']:require(sha(git('show',BASE+':'+row['path'],raw=True))==row['git_blob_sha256'],'frozen input bytes')
    plan=read('plan.json');require(plan['parent_goal']==m['parent_goal'] and plan['limits']=={'states_per_boundary':500000,'seconds_per_experiment':600,'memory_bytes':1610612736,'artifact_bytes':134217728,'max_processes_per_experiment':1,'network':False},'experiment limits')

def coverage(c):
    prior=FM['read']('coverage.json');require(c['preserved_contract_and_prior_coverage']==prior and c['historical_coverage_sha256']==sha(git('show',BASE+':'+c['historical_coverage_path'],raw=True)),'six obligations and27 historical rows')
    require(c['full_comparison_complete'] is False and c['formal_freeze'] is False,'no formal freeze')
    require(len(c['slice_obligations'])==6 and [r['id'] for r in c['slice_obligations']]==[r['id'] for r in prior['obligations']],'six obligation overlay')
    for r in c['slice_obligations']:require(r['status']==('partial-composition-slice-checked' if r['id'] in ('epoch-types','uncertainty') else 'no-new-coverage') and r['residual'],'obligation limits')
    require(len(c['slice_traces'])==27 and [r['id'] for r in c['slice_traces']]==[r['id'] for r in prior['traces']],'27 trace overlay')
    for r in c['slice_traces']:
        supported=r['id'][-2:] in ('12','17');require(r['status']==('partial-composition-slice-checked' if supported else 'no-new-coverage') and r['result']==('results.json' if supported else None) and r['residual'],'trace boundary')

def result_check(r,expected):
    require(canonical(r)==canonical(expected),'exact semantic results')
    require(r['status']=='conditional-composition-pass' and r['classification']=='modeled' and r['formal_freeze'] is False and r['production_authentication'] is False and r['full_core_cross_profiles'] is False and r['live_provider_calls']==0,'model claim boundary')
    require(set(r['profiles'])==set(cm_domain.POLICIES) and len(r['mutants'])==21 and {m['mutant'] for m in r['mutants']}==set(cm_domain.MUTANTS),'profile/mutant closure')
    for policy,pair in r['profiles'].items():
        require(pair['split']==pair['inclusive'],'independent boundary equality')
        for model in pair.values():require(model['states']==model['expanded'] and model['frontier']==0 and 0<model['states']<=500000 and model['duplicate_projections']==model['states']-model['projected_states'],'complete finite closure')
    for m in r['mutants']:require(all(m[k].get('failure') and m[k]['trace'] for k in ('split','inclusive')),'nonvacuous mutants')
    require(r['ordered_witnesses']==cm_explore.ordered_controls(),'ordered witness independent replay')
    require(r['calibrations']['truncated_graph']=='incomplete' and r['calibrations']['truncated_frontier']>0,'limit calibration')

def admission(a,x,directory,accepted):
    require(a['status']=='admitted-before-execution' and a['new_metered_spend']==0 and a['os_sandbox_claimed'] is False,'prospective allowed effects')
    require(set(a['sources'])==set(ADMIT['SOURCES']),'complete admitted sources')
    require(re.fullmatch('[0-9a-f]{40}',a['source_commit']) is not None,'source commit')
    git('merge-base','--is-ancestor',BASE,a['source_commit']);git('merge-base','--is-ancestor',a['source_commit'],'HEAD')
    for path,hashes in a['sources'].items():
        raw=bound(directory,'source/'+path).read_bytes();blob=git('show',a['source_commit']+':'+path,raw=True)
        require(sha(raw)==hashes['working_sha256'] and sha(blob)==hashes['git_blob_sha256'] and raw.replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),'executed source binding')
        if accepted:require(raw.replace(b'\r\n',b'\n')==(ROOT/path).read_bytes().replace(b'\r\n',b'\n'),'accepted source identity')
    require(a['limits']==read('plan.json')['limits'] and a['command']==[a['host']['executable'],'-X','utf8','-B',CODE+'cm_experiment.py','--output',str(directory/'result.json')],'exact admitted command/limits')
    begin=datetime.datetime.fromisoformat(a['started_at']);finish=datetime.datetime.fromisoformat(x['finished_at']);require(begin.tzinfo is not None and finish.tzinfo is not None and begin<=finish<=datetime.datetime.fromisoformat(read('goal.json')['deadline_utc']),'admission time ordering and completion deadline')
    require(datetime.datetime.fromisoformat(read('goal.json')['started_at'])<=begin<=datetime.datetime.fromisoformat(read('goal.json')['deadline_utc']),'campaign launch envelope')
    if accepted:
        import platform
        require(a['host']=={'system':platform.system(),'release':platform.release(),'version':platform.version(),'machine':platform.machine(),'python':sys.version,'executable':sys.executable} and x['status']=='finished' and x['exit_code']==0,'exact host successful execution')
        envelope=load(directory/'result.json');require(begin<=datetime.datetime.fromisoformat(envelope['started_at'])<=datetime.datetime.fromisoformat(envelope['finished_at'])<=finish,'model execution ordering')
        require(envelope['seconds']<=a['limits']['seconds_per_experiment'] and envelope['peak_bytes']<=a['limits']['memory_bytes'],'observed run bounds')

def claims(e):
    ledger=(ROOT/'docs/v3/CLAIM-LEDGER.md').read_text(encoding='utf-8');FM['HIST']['OLD']['registry_shape'](load(ROOT/'docs/v3/CLAIM-REGISTRY.json'),ledger)
    require(len(e['claims'])==3 and {r['id'] for r in e['claims']}=={'GCM-001','GCM-002','GCM-003'},'claim identities')
    for r in e['claims']:require(r['state']=='modeled' and '| '+r['id']+' | '+r['statement']+' | modeled |' in ledger and r['canonical'] in CANONICAL and r['id'] in (ROOT/r['canonical']).read_text(encoding='utf-8'),'claim provenance')

def evidence(e,expected):
    require(e['start_commit']==BASE and e['formal_freeze'] is False and e['new_owner_questions']==[] and e['semantic_sha256']==sha(canonical(expected).encode()),'evidence scope')
    rows=e['retained_runs'];all_dirs={d.name for d in (cache()/'discovery').iterdir() if d.is_dir() and (d/'admission.json').exists()}
    require(len(rows)==len(all_dirs) and {r['id'] for r in rows}==all_dirs,'all admitted attempts retained');count=0
    for row in rows:
        directory=bound(cache()/'discovery',row['id']);actual={p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()};require(actual==row['files'],'raw file inventory')
        a,x=load(directory/'admission.json'),load(directory/'execution.json');accepted=row['id']==e['accepted_run'];admission(a,x,directory,accepted)
        require(row['source_commit']==a['source_commit'] and row['exit_code']==x['exit_code'] and row['disposition'],'attempt source/outcome/disposition')
        if accepted:
            count+=1;require(e['accepted_source_commit']==a['source_commit'],'accepted identity');result_check(load(directory/'result.json')['result'],expected)
    require(count==1,'one accepted run');result_check(read('results.json'),expected);claims(e)

def reject(fn,value):
    try:fn(value)
    except (ValueError,KeyError,TypeError,AssertionError,OSError,subprocess.SubprocessError):return
    raise ValueError('adversarial mutation accepted')

def adversarial(actual,a,x,directory):
    labels=[]
    for key,value in [('start_commit','0'*40),('usage_resets_allowed',True),('new_metered_spend',1),('deadline_utc','2099-01-01T00:00:00Z')]:
        bad=copy.deepcopy(read('goal.json'));bad[key]=value;reject(goal_check,bad);labels.append('goal/'+key)
    reject(FM['candidate_check'],'0'*40);labels.append('wrong-candidate');reject(preservation,['CONTROL_PLANE.md']);labels.append('protected-path')
    for key,value in [('formal_freeze',True),('classification','locally observed'),('full_core_cross_profiles',True),('production_authentication',True),('mutants',[]),('ordered_witnesses',{})]:
        bad=copy.deepcopy(actual);bad[key]=value;reject(lambda v:result_check(v,actual),bad);labels.append('result/'+key)
    for change in ('frontier','states','graph','missing-witness'):
        bad=copy.deepcopy(actual);m=bad['profiles']['capsule']['split']
        if change=='frontier':m['frontier']=1
        elif change=='states':m['states']-=1
        elif change=='graph':m['graph_sha256']='0'*64
        else:m['witnesses'].pop(next(iter(m['witnesses'])))
        reject(lambda v:result_check(v,actual),bad);labels.append('graph/'+change)
    for change in ('erase-run','bad-hash','bad-source','promote-claim'):
        bad=copy.deepcopy(read('evidence.json'))
        if change=='erase-run':bad['retained_runs'].pop()
        elif change=='bad-hash':bad['retained_runs'][0]['files']['admission.json']='0'*64
        elif change=='bad-source':bad['accepted_source_commit']='0'*40
        else:bad['claims'][0]['state']='measured'
        reject(lambda v:evidence(v,actual),bad);labels.append('evidence/'+change)
    for change in ('missing-source','command','host','time','limit'):
        bad=copy.deepcopy(a)
        if change=='missing-source':bad['sources'].pop(next(iter(bad['sources'])))
        elif change=='command':bad['command'][-1]='elsewhere'
        elif change=='host':bad['host']['python']='unknown'
        elif change=='time':bad['started_at']='2099-01-01T00:00:00+00:00'
        else:bad['limits']['network']=True
        reject(lambda v:admission(v,x,directory,True),bad);labels.append('admission/'+change)
    bad=copy.deepcopy(x);bad['finished_at']='2099-01-01T00:00:00+00:00';reject(lambda v:admission(a,v,directory,True),bad);labels.append('execution/late-finish')
    for change in ('erase-trace','promote-trace','promote-obligation','rewrite-prior'):
        bad=copy.deepcopy(read('coverage.json'))
        if change=='erase-trace':bad['slice_traces'].pop()
        elif change=='promote-trace':bad['slice_traces'][0]['status']='complete'
        elif change=='promote-obligation':bad['slice_obligations'][0]['status']='complete'
        else:bad['preserved_contract_and_prior_coverage']['formal_freeze']=True
        reject(coverage,bad);labels.append('coverage/'+change)
    return labels

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');parser.add_argument('--working',action='store_true');parser.add_argument('--candidate');a=parser.parse_args();preflight()
    if a.preflight:print('COMPOSITION_PREFLIGHT_PASS_NOT_FINAL');return
    candidate=a.candidate or git('rev-parse','HEAD');FM['candidate_check'](candidate);changed=git('diff','--name-only',BASE,candidate).splitlines();preservation(changed);manifests();coverage(read('coverage.json'))
    # Historical working gates may reproduce this packet after its campaign deadline;
    # they verify old evidence and do not admit a new model run.
    if a.working:
        actual=read('results.json');evidence(read('evidence.json'),actual);d=cache()/'discovery'/read('evidence.json')['accepted_run'];labels=adversarial(actual,load(d/'admission.json'),load(d/'execution.json'),d);print('COMPOSITION_WORKING_PASS_NOT_FINAL '+str(len(labels))+' adversarial checks');return
    now=datetime.datetime.now(datetime.timezone.utc);require(now<=datetime.datetime.fromisoformat(read('goal.json')['deadline_utc']),'new execution deadline')
    out=cache()/candidate;out.mkdir(parents=True,exist_ok=True);runid=now.strftime('%Y%m%dT%H%M%S%f');directory=out/runid
    admitted,x=ADMIT['execute'](directory);admission(admitted,x,directory,True);actual=load(directory/'result.json')['result'];evidence(read('evidence.json'),actual);labels=adversarial(actual,admitted,x,directory)
    inv=read('validation-inventory.json');prior=GRA['read']('validation-inventory.json');require(inv['start_commit']==BASE and inv['regression_commands']==prior['regression_commands']==FM['HIST']['OLD']['regression_commands']() and len(inv['regression_commands'])==25,'unchanged25')
    require(set(inv['artifacts'])==set(changed)-{PREFIX+'validation-inventory.json'},'artifact closure')
    for path,h in inv['artifacts'].items():require(sha(git('show',candidate+':'+path,raw=True))==h,'artifact hash')
    expected=[{'commit':BASE,'branch':'codex/v3-generation-authority-20260907','script':'experiments/v3/generation-authority/check.py'}]+prior['frozen_gates'];require(inv['frozen_gates']==expected,'seven frozen gates')
    for row in FM['HIST']['read']('validation-inventory.json')['regression_entrypoints']:require(sha(git('show',candidate+':'+row['path'],raw=True))==row['sha256'] and git('show',candidate+':'+row['path'],raw=True)==git('show',BASE+':'+row['path'],raw=True),'historical validator bytes')
    git('diff','--check',BASE,candidate);logs=[]
    for row in expected:
        d=FM['frozen_root'](row['commit'],row['branch']);name=runid+'-frozen-'+row['commit'][:7];r=FM['run_command']([sys.executable,'-X','utf8','-B',row['script'],'--working'],d,out,name);r['log']=name+'.log';logs.append(r)
        require(git('rev-parse','HEAD',root=d)==row['commit'] and not git('status','--porcelain=v1',root=d),'frozen worktree changed')
    regressions=[]
    for i,cmd in enumerate(inv['regression_commands']):
        name=runid+'-regression-'+str(i);r=FM['run_command']([sys.executable,*cmd[1:]],ROOT,out,name);r['log']=name+'.log';regressions.append(r)
    FM['candidate_check'](candidate);require(datetime.datetime.now(datetime.timezone.utc)<=datetime.datetime.fromisoformat(read('goal.json')['deadline_utc']),'final completion deadline')
    receipt={'status':'COMPOSITION_GATE_PASS','candidate':candidate,'base':BASE,'run_id':runid,'semantic_sha256':sha(canonical(actual).encode()),'adversarial_checks':labels,'profile_counts':{p:{k:v for k,v in pair['split'].items() if k!='witnesses'} for p,pair in actual['profiles'].items()},'mutant_count':len(actual['mutants']),'execution_directory':str(directory),'execution_files':{p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()},'frozen_validations':logs,'regressions':regressions,'formal_freeze':False,'artifacts':{p:sha(git('show',candidate+':'+p,raw=True)) for p in changed}}
    raw=(json.dumps(receipt,indent=2)+'\n').encode();(out/(runid+'.json')).write_bytes(raw);print('COMPOSITION_GATE_PASS '+json.dumps({'candidate':candidate,'run_id':runid,'sha256':sha(raw)}))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as e:print('COMPOSITION_GATE_FAIL '+str(e),file=sys.stderr);raise SystemExit(1)
