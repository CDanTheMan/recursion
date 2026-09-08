"""Exact-candidate gate for finite RESET mapping evidence."""
import argparse,copy,datetime,hashlib,json,pathlib,runpy,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='c87f492780087772e3bcb06249ef14d89e812a25'
PREFIX='docs/v3/construction/reset-mapping-20260907/'
CODE='experiments/v3/reset-mapping/'
AREA=ROOT/PREFIX
CANONICAL={'docs/v3/'+n for n in 'EXECUTION-FABRIC.md TERMINAL-RUNTIME.md ACCEPTANCE.md ROADMAP.md CONSTRUCTION-RUNBOOK.md CLAIM-LEDGER.md CLAIM-REGISTRY.json'.split()}
FM=runpy.run_path(str(ROOT/'experiments/v3/formal-comparison/check.py'))
E=runpy.run_path(str(ROOT/CODE/'experiment.py'))
git,require,sha,canonical=FM['git'],FM['require'],FM['sha'],FM['canonical']
def read(name):return FM['strict']((AREA/name).read_text())
def load(path):return FM['strict'](path.read_text())
def common():return pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'))
def candidate_check(candidate):require(candidate==git('rev-parse','HEAD') and len(candidate)==40 and not git('status','--porcelain=v1','--untracked-files=all'),'clean exact candidate')
def goal_check(g):
    require(g['id']=='recursion.v3.reset-mapping.20260907' and g['parent_goal']=='goal-recursion-v2-execution-fabric' and g['start_commit']==BASE,'goal identity/lineage')
    require(g['deadline_utc']=='2026-09-08T01:00:00Z' and type(g['new_metered_spend']) is int and g['new_metered_spend']==0 and g['usage_resets_allowed'] is False,'time/spend bounds')
    require(set(g['allowed_paths'])==CANONICAL|{PREFIX+'**',CODE+'**'},'scope declaration')
def preflight():
    goal_check(read('goal.json'));require(git('branch','--show-current')=='codex/v3-reset-mapping-20260907','branch')
    git('merge-base','--is-ancestor',BASE,'HEAD')
    owners=[r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/codex/v3-reset-mapping-20260907' in r.splitlines()]
    require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree')
    prior=common()/'research-attestations/formal-comparison'/BASE;completion=load(prior/'completion.json')
    require(completion['status']=='published-scoped-campaign-complete' and completion['candidate']==BASE,'accepted predecessor')
    values=[]
    for name,digest in completion['receipts'].items():
        require(pathlib.Path(name).name==name and sha((prior/name).read_bytes())==digest,'predecessor receipt digest');values.append(load(prior/name))
    require(all(v['candidate']==BASE for v in values) and sum(v.get('status')=='FORMAL_SUBSYSTEM_GATE_PASS' for v in values)==2 and len({v['reviewer'] for v in values if v.get('verdict')=='approve'})==2,'two exact predecessor gates/reviews')
def preserve(changed):
    require(changed and all(p in CANONICAL or p.startswith(PREFIX) or p.startswith(CODE) for p in changed),'protected change')
    require(not git('diff','--name-only','--diff-filter=D',BASE),'deletion')
    for path in CANONICAL:
        old=git('show',BASE+':'+path);new=(ROOT/path).read_text()
        if path.endswith('.json'):
            a,b=json.loads(old),json.loads(new);b['ranges']=[r for r in b['ranges'] if r['prefix']!='RSM'];require(a==b,'historical registry changed')
        else:
            lines=iter(new.splitlines())
            for line in old.splitlines():require(any(line==n for n in lines),'historical content changed '+path)
    FM['HIST']['PRIOR']['document_gate'](changed)
    FM['claim_bindings'](FM['read']('evidence.json'));FM['IP']['claim_bindings'](FM['IP']['read']('evidence.json'))
    FM['HIST']['bindings'](FM['HIST']['read']('evidence.json'));FM['HIST']['bindings'](FM['HIST']['M']['read']('evidence.json'))
def result_check(actual,expected):
    require(canonical(actual)==canonical(expected),'executed result differs')
    require(actual['status']=='conditional-mapping-controls-pass' and actual['formal_freeze'] is False and actual['full_formal_comparison_complete'] is False and actual['live_provider_calls']==0,'claim scope')
    require(len(actual['profiles'])==16 and sum(p['schedule_prefixes'] for p in actual['profiles'])==2576 and sum(p['complete_schedules'] for p in actual['profiles'])==544,'profile coverage')
    require(all(p['frontier']==0 and p['unique_states']>0 and p['witnesses']['deferred'] and p['witnesses']['complete'] for p in actual['profiles']),'complete nonvacuous finite schedules')
def claims(evidence):
    ledger=(ROOT/'docs/v3/CLAIM-LEDGER.md').read_text();registry=load(ROOT/'docs/v3/CLAIM-REGISTRY.json')
    FM['HIST']['OLD']['registry_shape'](registry,ledger)
    require(len(evidence['claims'])==3 and {x['id'] for x in evidence['claims']}=={'RSM-001','RSM-002','RSM-003'},'claim identities')
    for claim in evidence['claims']:
        require('| '+claim['id']+' | '+claim['statement']+' | '+claim['state']+' |' in ledger,'claim statement/state binding')
        require(claim['canonical'] in CANONICAL and claim['id'] in (ROOT/claim['canonical']).read_text(),'canonical owner')
    require([c['state'] for c in evidence['claims']]==['modeled','modeled','source-documented'],'evidence state classification')
def evidence_check(e,expected):
    require(e['start_commit']==BASE and e['formal_freeze'] is False and e['full_formal_comparison_complete'] is False and e['new_owner_questions']==[],'evidence scope')
    result_check(read('results.json'),expected);require(e['results_canonical_sha256']==sha(canonical(expected).encode()),'result binding')
    cache=common()/'research-attestations/reset-mapping/discovery'
    require(len(e['retained_runs'])==2,'failure retention')
    for row in e['retained_runs']:
        directory=cache/row['id'];require(directory.resolve().is_relative_to(cache.resolve()),'cache path')
        for name,digest in row['files'].items():require(pathlib.Path(name).name==name and sha((directory/name).read_bytes())==digest,'raw retained evidence digest')
    require(e['retained_runs'][0]['status']=='schema-rejected-development-attempt' and e['retained_runs'][1]['status']=='conditional-mapping-controls-pass','attempt accounting')
    require((cache/e['retained_runs'][1]['id']/'experiment.py').read_text()==(ROOT/CODE/'experiment.py').read_text(),'executed semantic code identity')
    require(canonical(load(cache/e['retained_runs'][1]['id']/'results.json'))==canonical(expected),'raw/public result identity')
    claims(e)
def reject(fn,value):
    try:fn(value)
    except (ValueError,KeyError,TypeError,AssertionError):return
    raise ValueError('adversarial mutation accepted')
def working():
    preflight();changed=sorted(set(git('diff','--name-only',BASE).splitlines()+git('ls-files','--others','--exclude-standard').splitlines()));preserve(changed)
    manifest=read('manifest.json');require(manifest['start_commit']==BASE,'manifest base')
    expected=set(git('diff','--name-only','a497bae10dddc3adf176242aed878f83b4519316',BASE).splitlines())|{'CONTROL_PLANE.md','CLAUDE.md','ANCHOR.md','state/goals/goal-recursion-v2-execution-fabric.md','docs/v3/M1B-WIRE-PROFILE.md','scripts/tests/v3/execution/reference_oracle.py','scripts/tests/v3/execution/fixtures/F-M1B-020.json','schemas/control-plane/v3/execution/schema.json'}
    require({i['path'] for i in manifest['inputs']}==expected and len(manifest['inputs'])==len(expected),'complete frozen manifest')
    for i in manifest['inputs']:require(sha(git('show',BASE+':'+i['path'],raw=True))==i['git_blob_sha256'],'frozen input bytes')
    result=E['run']();evidence_check(read('evidence.json'),result);labels=[]
    for key,value in [('start_commit','0'*40),('new_metered_spend',1),('usage_resets_allowed',True),('deadline_utc','2099-01-01T00:00:00Z')]:
        bad=copy.deepcopy(read('goal.json'));bad[key]=value;reject(goal_check,bad);labels.append('goal/'+key)
    reject(candidate_check,'0'*40);labels.append('wrong-candidate');reject(preserve,['CONTROL_PLANE.md']);labels.append('protected-path')
    for field,value in [('formal_freeze',True),('full_formal_comparison_complete',True),('live_provider_calls',1)]:
        bad=copy.deepcopy(result);bad[field]=value;reject(lambda v:result_check(v,result),bad);labels.append('result/'+field)
    for kind in ['omit-profile','false-frontier','erase-deferred','false-recovery','false-requires-reset']:
        bad=copy.deepcopy(result)
        if kind=='omit-profile':bad['profiles'].pop()
        elif kind=='false-frontier':bad['profiles'][0]['frontier']=1
        elif kind=='erase-deferred':bad['profiles'][0]['witnesses']['deferred']={}
        elif kind=='false-recovery':bad['controls']['literal_cases']['local_deferral_RESET']['decision']['status']='accepted'
        else:bad['controls']['literal_cases']['recorded_gap_reset_resume']['decision']['requires_reset']=False
        reject(lambda v:result_check(v,result),bad);labels.append(kind)
    for kind in ['erase-failure','promote-claim','false-raw-digest']:
        bad=copy.deepcopy(read('evidence.json'))
        if kind=='erase-failure':bad['retained_runs'].pop(0)
        elif kind=='promote-claim':bad['claims'][0]['state']='measured'
        else:bad['retained_runs'][1]['files']['results.json']='0'*64
        reject(lambda v:evidence_check(v,result),bad);labels.append(kind)
    return changed,labels,result
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--working',action='store_true');parser.add_argument('--candidate');args=parser.parse_args()
    if not args.working:candidate_check(args.candidate)
    changed,labels,result=working()
    if args.working:print(json.dumps({'status':'RESET_WORKING_PASS_NOT_FINAL','adversarial_checks':len(labels),'profiles':len(result['profiles'])}));return
    inventory=read('validation-inventory.json');prior=FM['HIST']['read']('validation-inventory.json')
    require(inventory['regression_commands']==prior['regression_commands']==FM['HIST']['OLD']['regression_commands']() and len(inventory['regression_commands'])==25,'unchanged25')
    for item in prior['regression_entrypoints']:
        raw=git('show',args.candidate+':'+item['path'],raw=True);require(sha(raw)==item['sha256'] and raw==git('show',BASE+':'+item['path'],raw=True),'unchanged historical entrypoints')
    require(set(inventory['artifacts'])==set(changed)-{PREFIX+'validation-inventory.json'},'inventory coverage')
    for p,d in inventory['artifacts'].items():require(sha(git('show',args.candidate+':'+p,raw=True))==d,'artifact digest')
    git('diff','--check',BASE,args.candidate)
    out=common()/'research-attestations/reset-mapping'/args.candidate;out.mkdir(parents=True,exist_ok=True);runid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    (out/(runid+'-model.json')).write_text(json.dumps(result,indent=2)+'\n');frozen=[]
    for commit,branch,script in [(BASE,'codex/v3-formal-comparison-20260907','experiments/v3/formal-comparison/check.py'),(FM['BASE'],'codex/v3-interface-probes-20260907','experiments/v3/interface-probes/check.py'),(FM['RESEARCH'],'codex/v3-formal-model-experiment','docs/v3/foundation-research/mark2-research/mark3-comparison/check.py')]:
        directory=FM['frozen_root'](commit,branch);frozen.append(FM['run_command']([sys.executable,'-X','utf8','-B',script,'--working'],directory,out,runid+'-frozen-'+commit[:7]))
        require(git('rev-parse','HEAD',root=directory)==commit and not git('status','--porcelain=v1','--untracked-files=all',root=directory),'frozen state changed')
    regressions=[]
    for n,command in enumerate(inventory['regression_commands']):regressions.append(FM['run_command']([sys.executable,*command[1:]],ROOT,out,runid+'-regression-'+str(n)))
    candidate_check(args.candidate)
    receipt={'status':'RESET_MAPPING_GATE_PASS','candidate':args.candidate,'base':BASE,'run_id':runid,'adversarial_checks':labels,'model_canonical_sha256':sha(canonical(result).encode()),'frozen_validations':frozen,'regressions':regressions,'artifacts':{p:sha(git('show',args.candidate+':'+p,raw=True)) for p in changed},'formal_freeze':False,'full_formal_comparison_complete':False}
    raw=(json.dumps(receipt,indent=2)+'\n').encode();(out/(runid+'.json')).write_bytes(raw);print('RESET_MAPPING_GATE_PASS '+json.dumps({'candidate':args.candidate,'run_id':runid,'receipt_sha256':sha(raw)}))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:print('RESET_MAPPING_GATE_FAIL '+str(exc),file=sys.stderr);sys.exit(1)
