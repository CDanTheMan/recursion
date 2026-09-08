"""Exact-candidate gate; immutable prior gates and unchanged regressions required."""
import argparse,copy,datetime,hashlib,json,pathlib,platform,re,runpy,subprocess,sys,importlib.metadata
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='c9a51c0a0bcfa0946b410733b7910f477d89f1cc'
PREFIX='docs/v3/construction/shared-composition-20260908/'
CODE='experiments/v3/shared-composition/'
AREA=ROOT/PREFIX
EE=runpy.run_path(str(ROOT/'experiments/v3/effect-evidence/check.py'));CM=EE['CM'];FM=EE['FM']
CANONICAL=EE['CANONICAL'];git=EE['git'];sha=EE['sha'];load=EE['load'];canonical=EE['canonical'];require=EE['require']
sys.path.insert(0,str(ROOT/CODE))
import sc_domain as domain,sc_experiment as experiment,sc_explore as explore,sc_audit as audit,sc_inclusive as inclusive,sc_split as split
ADMIT=runpy.run_path(str(ROOT/CODE/'run_packet.py'))
LIMITS={'states_per_boundary':500000,'seconds_per_experiment':600,'memory_bytes':1610612736,'artifact_bytes':134217728,'max_processes_per_experiment':1,'network':False}
def read(n):return load(AREA/n)
def common():return pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'))
def cache():return common()/'research-attestations/shared-composition'
def bound(directory,name):
    p=directory/name;require(p.resolve().is_relative_to(directory.resolve()),'evidence path escape');return p

def goal_check(g):
    require(g['id']=='recursion.v3.shared-composition.20260908' and g['parent_goal']=='goal-recursion-v2-execution-fabric' and g['start_commit']==BASE,'goal identity')
    require(g['branch']=='codex/v3-shared-composition-20260908' and g['predecessor']=='recursion.v3.effect-evidence.20260908','lineage')
    require(type(g['new_metered_spend']) is int and g['new_metered_spend']==0 and g['usage_resets_allowed'] is False,'spend/reset')
    require(g['started_at']=='2026-09-08T15:44:44Z' and g['deadline_utc']=='2026-09-08T19:44:44Z' and g['discovery_cutoff_utc']=='2026-09-08T18:14:44Z' and g['synthesis_review_reserve_minutes']==90,'time envelope')
    require(set(g['allowed_paths'])==CANONICAL|{PREFIX+'**',CODE+'**'} and g['max_active_agents_owner']==10 and g['max_concurrent_read_only_workers']==4,'scope/concurrency')
    require(g['capacity']['no_new_workers_at_remaining_percent']==6 and g['capacity']['checkpoint_at_remaining_percent']==3,'capacity reserve')

def preflight():
    g=read('goal.json');goal_check(g);require(git('branch','--show-current')==g['branch'],'branch')
    for ancestor in (BASE,'a7cd9458d37f3090079930bf8d79ffd77c4f73e4'):git('merge-base','--is-ancestor',ancestor,'HEAD')
    owners=[r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+g['branch'] in r.splitlines()]
    require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree')
    require(not (ROOT/'state/PAUSE').exists() and not (common().parent/'state/PAUSE').exists(),'PAUSE')
    require('status: active' in (ROOT/'state/goals/goal-recursion-v2-execution-fabric.md').read_text(),'active parent')
    prior=common()/'research-attestations/effect-evidence'/BASE;c=load(prior/'completion.json')
    require(c['candidate']==BASE and c['status']=='published-scoped-campaign-complete','predecessor completion')
    receipts=[]
    for name,h in c['receipt_sha256'].items():
        raw=bound(prior,name).read_bytes();require(sha(raw)==h,'predecessor receipt hash');receipts.append(json.loads(raw))
    require(all(r['candidate']==BASE for r in receipts) and sum(r.get('status')=='EFFECT_EVIDENCE_GATE_PASS' for r in receipts)==2 and len({r['reviewer'] for r in receipts if r.get('verdict')=='approve-publication'})==2,'predecessor exact gates/reviews')

def preservation(changed):
    require(changed and all(p in CANONICAL or p.startswith(PREFIX) or p.startswith(CODE) for p in changed),'allowed paths')
    require(not git('diff','--name-only','--diff-filter=D',BASE),'baseline deletion')
    for path in CANONICAL:
        old=git('show',BASE+':'+path);new=(ROOT/path).read_text(encoding='utf-8')
        if path.endswith('.json'):
            a,b=json.loads(old),json.loads(new);b['ranges']=[r for r in b['ranges'] if r['prefix']!='SCM'];require(a==b,'historical registry')
        else:
            it=iter(new.splitlines())
            for line in old.splitlines():require(any(line==x for x in it),'historical canonical content '+path)
    FM['HIST']['PRIOR']['document_gate'](changed)
    for gate in (EE,CM,CM['GRA'],CM['GRA']['RSE'],CM['GRA']['FRI'],CM['GRA']['FRI']['RSM']):gate['claims'](gate['read']('evidence.json'))
    FM['claim_bindings'](FM['read']('evidence.json'));FM['IP']['claim_bindings'](FM['IP']['read']('evidence.json'))
    FM['HIST']['bindings'](FM['HIST']['read']('evidence.json'));FM['HIST']['bindings'](FM['HIST']['M']['read']('evidence.json'))

def manifests():
    m=read('manifest.json');expected={r['path'] for r in EE['read']('manifest.json')['inputs']}|set(git('diff','--name-only',EE['BASE'],BASE).splitlines())
    require(m['start_commit']==BASE and m['parent_goal']=='goal-recursion-v2-execution-fabric' and len(m['inputs'])==len(expected) and {r['path'] for r in m['inputs']}==expected,'input closure')
    for row in m['inputs']:require(sha(git('show',BASE+':'+row['path'],raw=True))==row['git_blob_sha256'],'frozen input bytes')
    require(read('plan.json')['limits']==LIMITS,'prospective experiment bounds')

def coverage(c):
    old=FM['read']('coverage.json')
    require(c['preserved_contract_and_prior_coverage']==old and c['predecessor_coverage']==EE['read']('coverage.json'),'complete historical coverage')
    require(c['full_comparison_complete'] is False and c['formal_freeze'] is False,'no formal freeze')
    require([r['id'] for r in c['slice_obligations']]==[r['id'] for r in old['obligations']] and len(c['slice_obligations'])==6,'six obligations')
    for r in c['slice_obligations']:
        require(r['status']==('no-new-coverage' if r['id']=='writer-pool' else 'partial-modeled-support') and r['residual'],'obligation boundary')
    require([r['id'] for r in c['slice_traces']]==[r['id'] for r in old['traces']] and len(c['slice_traces'])==27,'27 trace identities')
    for r in c['slice_traces']:
        partial=r['id'][-2:] in ('01','02','09','10','12','13','15','17')
        require(r['status']==('partial-modeled-support' if partial else 'no-new-coverage') and r['result']==('results.json' if partial else None) and r['residual'],'trace boundary')

def result_check(r,expected):
    require(canonical(r)==canonical(expected),'exact semantic results')
    require(r['status']=='shared-composition-pass' and r['classification']=='modeled' and r['formal_freeze'] is False and r['full_comparison_complete'] is False and r['runtime_integration_support'] is False and r['live_provider_calls']==0 and r['new_owner_questions']==[],'claim boundary')
    require(set(r['profiles'])==set(domain.PROFILES)==set(experiment.WITNESSES),'profile closure')
    total=0
    for name,row in r['profiles'].items():
        require(row['exact_graph_equal'] is True and row['inclusive']==row['split'],'both complete boundaries')
        g=row['inclusive'];require(type(g['states']) is int and g['states']>0 and g['edges']>=g['states'] and g['frontier']==0 and re.fullmatch('[0-9a-f]{64}',g['graph_sha256']),'finite closure receipt');total+=g['states']
        require(row['witnesses'],'nonvacuous witnesses')
        for w in row['witnesses']:
            state=domain.State();prior=None
            for action in w['trace']:
                edges=dict(inclusive.edges(state,name));audit.enabled(state,name,list(edges));require(action in edges,'witness enabled');n=edges[action];audit.edge(state,action,n,name)
                other=dict(split.edges(split.pack(state),name));require(split.flat(other[action])==n,'witness split correspondence');prior,state=state,n
            require(canonical(w['state'])==canonical(experiment.asdict(state)),'exact witness state')
            if 'before' in w:require(canonical(w['before'])==canonical(experiment.asdict(prior)),'exact witness predecessor')
            if w['name']==name:require(experiment.WITNESSES[name](state),'profile target')
    require(total==r['states_per_boundary']<=LIMITS['states_per_boundary'],'state total admission')
    require([m['guard'] for m in r['mutants']]==list(experiment.MUTANTS),'mutant closure')
    for m in r['mutants']:require(canonical(explore.explore(m['profile'],'inclusive',mutant=m['guard']))==canonical(m),'independent reachable mutant counterexample')
    require(r['calibrations']==explore.calibrate(),'checker calibration closure')
    require(r['literal']==experiment.literal(),'frozen literal controls independently re-executed')

def admission(a,x,directory,accepted):
    require(a['status']=='admitted-before-execution' and a['new_metered_spend']==0 and a['network_operations_in_model'] is False and a['os_sandbox_claimed'] is False,'prospective allowed effects')
    require(set(a['sources'])==set(ADMIT['SOURCES']),'complete admitted sources')
    require(re.fullmatch('[0-9a-f]{40}',a['source_commit']) is not None,'source commit')
    git('merge-base','--is-ancestor',BASE,a['source_commit']);git('merge-base','--is-ancestor',a['source_commit'],'HEAD')
    for path,hashes in a['sources'].items():
        raw=bound(directory,'source/'+path).read_bytes();blob=git('show',a['source_commit']+':'+path,raw=True)
        require(sha(raw)==hashes['working_sha256'] and sha(blob)==hashes['git_blob_sha256'] and raw.replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),'executed source binding')
        if accepted:require(raw.replace(b'\r\n',b'\n')==(ROOT/path).read_bytes().replace(b'\r\n',b'\n'),'accepted source identity')
    require(a['limits']==LIMITS and a['command']==[a['host']['executable'],'-X','utf8','-B',CODE+'sc_experiment.py','--output',str(directory/'result.json')],'exact admitted command/limits')
    begin=datetime.datetime.fromisoformat(a['started_at']);finish=datetime.datetime.fromisoformat(x['finished_at'])
    require(begin.tzinfo is not None and finish.tzinfo is not None and datetime.datetime.fromisoformat(read('goal.json')['started_at'])<=begin<=finish<=datetime.datetime.fromisoformat(read('goal.json')['deadline_utc']),'admission ordering/deadline')
    if accepted:
        require(a['host']=={'system':platform.system(),'release':platform.release(),'version':platform.version(),'machine':platform.machine(),'python':sys.version,'executable':sys.executable} and a['dependencies']=={'jsonschema':importlib.metadata.version('jsonschema')} and x['status']=='finished' and x['exit_code']==0,'exact successful host execution')
        envelope=load(directory/'result.json')
        require(begin<=datetime.datetime.fromisoformat(envelope['started_at'])<=datetime.datetime.fromisoformat(envelope['finished_at'])<=finish,'execution ordering')
        require(envelope['seconds']<=LIMITS['seconds_per_experiment'] and 0<envelope['peak_bytes']<=LIMITS['memory_bytes'],'observed resource bounds')
    require(sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())<=LIMITS['artifact_bytes'],'artifact bound')

def claims(e):
    ledger=(ROOT/'docs/v3/CLAIM-LEDGER.md').read_text(encoding='utf-8');FM['HIST']['OLD']['registry_shape'](load(ROOT/'docs/v3/CLAIM-REGISTRY.json'),ledger)
    require(len(e['claims'])==3 and {r['id'] for r in e['claims']}=={'SCM-001','SCM-002','SCM-003'},'claim identities')
    for r in e['claims']:require(r['state']=='modeled' and '| '+r['id']+' | '+r['statement']+' | modeled |' in ledger and r['canonical'] in CANONICAL and r['id'] in (ROOT/r['canonical']).read_text(encoding='utf-8'),'claim provenance')

def evidence(e,expected):
    require(e['start_commit']==BASE and e['formal_freeze'] is False and e['new_owner_questions']==[] and e['semantic_sha256']==sha(canonical(expected).encode()),'evidence scope')
    rows=e['retained_runs'];all_dirs={d.name for d in (cache()/'discovery').iterdir() if d.is_dir() and (d/'admission.json').exists()}
    require(len(rows)==len(all_dirs) and {r['id'] for r in rows}==all_dirs,'all discovery attempts retained');count=0
    for row in rows:
        directory=bound(cache()/'discovery',row['id']);require({p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()}==row['files'],'raw file inventory')
        a,x=load(directory/'admission.json'),load(directory/'execution.json');accepted=row['id']==e['accepted_run'];admission(a,x,directory,accepted)
        require(row['source_commit']==a['source_commit'] and row['exit_code']==x['exit_code'] and row['disposition'],'attempt source/outcome')
        if accepted:count+=1;require(e['accepted_source_commit']==a['source_commit'],'accepted identity');result_check(load(directory/'result.json')['result'],expected)
    require(count==1,'one accepted run');result_check(read('results.json'),expected);claims(e)
    for row in e['superseded_candidate_validations']:
        directory=bound(cache(),row['candidate']);require(row['candidate']!=git('rev-parse','HEAD') and row['disposition']=='superseded-not-a-pass','superseded candidate')
        require({p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()}==row['files'],'superseded validations retained')

def inventory(inv,changed,candidate):
    prior=EE['read']('validation-inventory.json')
    require(inv['start_commit']==BASE and inv['regression_commands']==prior['regression_commands']==FM['HIST']['OLD']['regression_commands']() and len(inv['regression_commands'])==25,'unchanged25')
    require(set(inv['artifacts'])==set(changed)-{PREFIX+'validation-inventory.json'},'artifact closure')
    for path,h in inv['artifacts'].items():require(sha(git('show',candidate+':'+path,raw=True))==h,'artifact hash')
    expected=[{'commit':BASE,'branch':'codex/v3-effect-evidence-20260908','script':'experiments/v3/effect-evidence/check.py'}]+prior['frozen_gates']
    require(inv['frozen_gates']==expected and len(expected)==9,'nine frozen gates')
    for row in FM['HIST']['read']('validation-inventory.json')['regression_entrypoints']:
        require(sha(git('show',candidate+':'+row['path'],raw=True))==row['sha256'] and git('show',candidate+':'+row['path'],raw=True)==git('show',BASE+':'+row['path'],raw=True),'historical validator bytes')
    return expected

def reject(fn,value):
    try:fn(value)
    except (ValueError,KeyError,TypeError,AssertionError,OSError,subprocess.SubprocessError):return
    raise ValueError('adversarial mutation accepted')

def adversarial(actual,a,x,directory):
    labels=[]
    for key,value in [('start_commit','0'*40),('usage_resets_allowed',True),('new_metered_spend',1),('deadline_utc','2099-01-01T00:00:00Z')]:
        bad=copy.deepcopy(read('goal.json'));bad[key]=value;reject(goal_check,bad);labels.append('goal/'+key)
    reject(FM['candidate_check'],'0'*40);labels.append('wrong-candidate');reject(preservation,['CONTROL_PLANE.md']);labels.append('protected-path')
    for key,value in [('formal_freeze',True),('classification','measured'),('full_comparison_complete',True),('runtime_integration_support',True),('mutants',[]),('states_per_boundary',0)]:
        bad=copy.deepcopy(actual);bad[key]=value;reject(lambda v:result_check(v,actual),bad);labels.append('result/'+key)
    for change in ('frontier','missing-witness','different-boundaries'):
        bad=copy.deepcopy(actual);row=bad['profiles']['old-cut-new-attempt']
        if change=='frontier':row['inclusive']['frontier']=1
        elif change=='missing-witness':row['witnesses']=[]
        else:row['split']['graph_sha256']='0'*64
        reject(lambda v:result_check(v,actual),bad);labels.append('result/'+change)
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
    if a.preflight:print('SHARED_COMPOSITION_PREFLIGHT_PASS_NOT_FINAL');return
    candidate=a.candidate or git('rev-parse','HEAD');FM['candidate_check'](candidate);changed=git('diff','--name-only',BASE,candidate).splitlines();preservation(changed);manifests();coverage(read('coverage.json'))
    actual=read('results.json');evidence(read('evidence.json'),actual);inv=read('validation-inventory.json');frozen=inventory(inv,changed,candidate)
    if a.working:
        directory=cache()/'discovery'/read('evidence.json')['accepted_run'];labels=adversarial(actual,load(directory/'admission.json'),load(directory/'execution.json'),directory)
        print('SHARED_COMPOSITION_WORKING_PASS_NOT_FINAL '+str(len(labels))+' adversarial checks');return
    now=datetime.datetime.now(datetime.timezone.utc);require(now<=datetime.datetime.fromisoformat(read('goal.json')['deadline_utc']),'execution deadline')
    out=cache()/candidate;out.mkdir(parents=True,exist_ok=True);runid=now.strftime('%Y%m%dT%H%M%S%f');directory=out/runid
    admitted,x=ADMIT['execute'](directory);admission(admitted,x,directory,True);fresh=load(directory/'result.json')['result'];result_check(fresh,actual);labels=adversarial(actual,admitted,x,directory)
    git('diff','--check',BASE,candidate);logs=[]
    for row in frozen:
        root=FM['frozen_root'](row['commit'],row['branch']);name=runid+'-frozen-'+row['commit'][:7]
        r=FM['run_command']([sys.executable,'-X','utf8','-B',row['script'],'--working'],root,out,name);r['log']=name+'.log';logs.append(r)
        require(git('rev-parse','HEAD',root=root)==row['commit'] and not git('status','--porcelain=v1',root=root),'frozen worktree changed')
    regressions=[]
    for i,cmd in enumerate(inv['regression_commands']):
        name=runid+'-regression-'+str(i);r=FM['run_command']([sys.executable,*cmd[1:]],ROOT,out,name);r['log']=name+'.log';regressions.append(r)
    FM['candidate_check'](candidate);require(datetime.datetime.now(datetime.timezone.utc)<=datetime.datetime.fromisoformat(read('goal.json')['deadline_utc']),'completion deadline')
    receipt={'status':'SHARED_COMPOSITION_GATE_PASS','candidate':candidate,'base':BASE,'run_id':runid,'semantic_sha256':sha(canonical(actual).encode()),'adversarial_checks':labels,'states_per_boundary':actual['states_per_boundary'],'execution_directory':str(directory),'execution_files':{p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()},'frozen_validations':logs,'regressions':regressions,'formal_freeze':False,'artifacts':{p:sha(git('show',candidate+':'+p,raw=True)) for p in changed}}
    raw=(json.dumps(receipt,indent=2)+'\n').encode();(out/(runid+'.json')).write_bytes(raw);print('SHARED_COMPOSITION_GATE_PASS '+json.dumps({'candidate':candidate,'run_id':runid,'sha256':sha(raw)}))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as e:print('SHARED_COMPOSITION_GATE_FAIL '+str(e),file=sys.stderr);raise SystemExit(1)
