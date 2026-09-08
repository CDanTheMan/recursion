"""Exact-candidate local replay-store evidence gate with raw receipt reconstruction."""
import argparse,json,pathlib,subprocess,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='03fd11014a5be99006d637ad5eb692faa0557f8f'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def require(value,message):
    if not value:raise ValueError(message)
def preflight():
    goal=json.loads((ROOT/'docs/v3/construction/replay-store-evidence-20260907/goal.json').read_text())
    require(goal['start_commit']==BASE and goal['parent_goal']=='goal-recursion-v2-execution-fabric','goal lineage')
    require(goal['new_metered_spend']==0 and goal['usage_resets_allowed'] is False,'spend/reset boundary')
    require(git('branch','--show-current')==goal['branch'],'branch')
    for ancestor in [BASE,'a7cd9458d37f3090079930bf8d79ffd77c4f73e4']:git('merge-base','--is-ancestor',ancestor,'HEAD')
    owners=[r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+goal['branch'] in r.splitlines()]
    require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree')
    common=pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'));require(not (ROOT/'state/PAUSE').exists() and not (common.parent/'state/PAUSE').exists(),'PAUSE')
    prior=common/'research-attestations/flow-recovery-integration'/BASE;receipt=json.loads((prior/'completion.json').read_text());require(receipt['candidate']==BASE and receipt['status']=='published-scoped-campaign-complete','accepted predecessor')
    records=[]
    for name,digest in receipt['receipts'].items():
        raw=(prior/name).read_bytes();require(hashlib.sha256(raw).hexdigest()==digest,'predecessor receipt digest');records.append(json.loads(raw))
    require(all(r['candidate']==BASE for r in records) and sum(r.get('status')=='FLOW_RECOVERY_GATE_PASS' for r in records)==2 and len({r['reviewer'] for r in records if r.get('verdict')=='approve'})==2,'two exact predecessor gates/reviews')
    print('REPLAY_STORE_CONSTRUCTION_PREFLIGHT_PASS_NOT_FINAL')

import base64,copy,datetime,re,runpy,sys
from jsonschema import Draft202012Validator
FRI=runpy.run_path(str(ROOT/'experiments/v3/flow-recovery-integration/check.py'))
FM=FRI['FM'];git=FM['git'];sha=FM['sha']
ADMIT=runpy.run_path(str(ROOT/'experiments/v3/replay-store-evidence/admit.py'))
PREFIX='docs/v3/construction/replay-store-evidence-20260907/'
CODE='experiments/v3/replay-store-evidence/'
AREA=ROOT/PREFIX
CANONICAL=FRI['CANONICAL']
SOURCE_PATHS=set(ADMIT['SOURCES'])
WRITER=['snapshot_partial','snapshot_ready','retention_changed','manifest_staged','commit_published']
RECEIVER=['RESET_emitted','snapshot_staged','reset_committed']
def load(path):return FM['strict'](path.read_text(encoding='utf8'))
def read(name):return load(AREA/name)
def common():return pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'))
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def bound(directory,path):
    p=directory/path;require(p.resolve().is_relative_to(directory.resolve()),'evidence path escape');return p
def goal_check(g):
    require(g['start_commit']==BASE and g['id']=='recursion.v3.replay-store-evidence.20260907' and g['parent_goal']=='goal-recursion-v2-execution-fabric','goal identity')
    require(type(g['new_metered_spend'])is int and g['new_metered_spend']==0 and g['usage_resets_allowed'] is False,'spend/reset')
    require(g['started_at']=='2026-09-08T04:10:23Z' and g['deadline_utc']=='2026-09-08T07:10:23Z' and g['discovery_cutoff_utc']=='2026-09-08T05:40:23Z' and g['synthesis_review_reserve_minutes']==90,'time envelope')
    require(set(g['allowed_paths'])==CANONICAL|{PREFIX+'**',CODE+'**'} and g['max_concurrent_read_only_workers']==2,'scope/worker bounds')
    require(g['capacity']['checkpoint_at_remaining_percent']==3 and g['capacity']['no_new_workers_at_remaining_percent']==6,'capacity reserve')
def preserve(changed):
    require(changed and all(p in CANONICAL or p.startswith(PREFIX) or p.startswith(CODE) for p in changed),'protected change')
    require(not git('diff','--name-only','--diff-filter=D',BASE),'deletion')
    for path in CANONICAL:
        old=git('show',BASE+':'+path);new=(ROOT/path).read_text(encoding='utf8')
        if path.endswith('.json'):
            a,b=json.loads(old),json.loads(new);b['ranges']=[r for r in b['ranges'] if r['prefix']!='RSE'];require(a==b,'historical registry changed')
        else:
            lines=iter(new.splitlines())
            for line in old.splitlines():require(any(line==n for n in lines),'historical content changed '+path)
    FM['HIST']['PRIOR']['document_gate'](changed)
    FRI['claims'](FRI['read']('evidence.json'));FRI['RSM']['claims'](FRI['RSM']['read']('evidence.json'))
    FM['claim_bindings'](FM['read']('evidence.json'));FM['IP']['claim_bindings'](FM['IP']['read']('evidence.json'))
    FM['HIST']['bindings'](FM['HIST']['read']('evidence.json'));FM['HIST']['bindings'](FM['HIST']['M']['read']('evidence.json'))
def manifests():
    m=read('manifest.json');require(m['start_commit']==BASE and m['parent_goal']=='goal-recursion-v2-execution-fabric','manifest lineage')
    expected={r['path'] for r in FRI['read']('manifest.json')['inputs']}|set(git('diff','--name-only',FRI['BASE'],BASE).splitlines())
    require(len(m['inputs'])==len(expected) and {r['path'] for r in m['inputs']}==expected,'complete frozen inputs')
    for r in m['inputs']:require(sha(git('show',BASE+':'+r['path'],raw=True))==r['git_blob_sha256'],'frozen input hash')
    sources=read('sources.json');require(len(sources['files'])==15 and sources['cpython_commit']=='0cc81280367df838c4b199f8f0378837165071c2' and sources['ui_commit']=='ed5f1c48e11ba7335f1e8f676f228c280196af85','source identities')
    for r in sources['files']:require(sha(bound(common()/'research-attestations/replay-store-evidence/primary-sources',r['file']).read_bytes())==r['sha256'],'primary source bytes')
def admission(a,x,directory,complete=True):
    require(a['status']=='admitted-before-execution' and a['new_metered_spend']==0,'prospective admission')
    dates=[datetime.datetime.fromisoformat(t) for t in [a['started_at'],x['started_at'],x['finished_at']]]
    require(all(t.tzinfo is not None for t in dates) and dates==sorted(dates),'admission timestamps')
    require(re.fullmatch('[0-9a-f]{40}',a['source_commit']) is not None,'source commit')
    git('merge-base','--is-ancestor',BASE,a['source_commit']);git('merge-base','--is-ancestor',a['source_commit'],'HEAD')
    paths={f['path'] for f in a['source_files']}
    require(len(paths)==len(a['source_files']) and (paths==SOURCE_PATHS if complete else paths<=SOURCE_PATHS),'admitted sources')
    for f in a['source_files']:
        raw=bound(directory,'source/'+f['path']).read_bytes();blob=git('show',a['source_commit']+':'+f['path'],raw=True)
        require(sha(raw)==f['working_sha256'] and sha(blob)==f['git_blob_sha256'] and raw.replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),'admitted source bytes')
    require(a['limits']==ADMIT['LIMITS'] and a['command']==[a['host']['python_executable'],'-X','utf8','-B',CODE+'experiment.py','--output',str(directory/'cases')],'admitted command/limits')
    if complete:require(a['host']==ADMIT['host']() and x['status']=='finished' and type(x['exit_code'])is int and x['exit_code']==0,'admitted host/success')
def result_check(value,expected):
    require(canonical(value)==canonical(expected),'semantic result differs')
    require(value['status']=='local-named-cut-pass' and value['case_count']==115 and value['helper_process_count']==435,'closed case/process coverage')
    require(type(value['live_provider_calls'])is int and value['live_provider_calls']==0 and value['formal_freeze'] is False and value['power_loss_durability_established'] is False,'claim boundary')
    require(len(value['rows'])==115 and len({r['case'] for r in value['rows']})==115,'unique cases')
def raw_check(directory,result,observations=None):
    cases=directory/'cases';receipts={};cut_counts={'update':0,'receive':0}
    oracle=runpy.run_path(str(ROOT/'scripts/tests/v3/execution/reference_oracle.py'))['replay_broker']
    schema=Draft202012Validator(load(ROOT/'schemas/control-plane/v3/execution/schema.json'));fixture=load(ROOT/'scripts/tests/v3/execution/fixtures/F-M1B-020.json')['input']
    require({p.name for p in cases.iterdir() if p.is_dir()}=={r['case'] for r in result['rows']},'raw case coverage')
    for row in result['rows']:
        case=bound(cases,row['case']);require((observations or {}).get(row['case'],load(case/'observation.json'))==row,'raw observation binding')
        inv=load(case/'inventory.json');actual={p.relative_to(case).as_posix():sha(p.read_bytes()) for p in case.rglob('*') if p.is_file() and p.name!='inventory.json'}
        require(inv==actual,'case inventory completeness')
        for path in case.glob('*.json'):
            match=re.fullmatch(r'(\d{4})-(init|update|read|receive)\.json',path.name)
            if not match:continue
            n,role=int(match[1]),match[2];require(n not in receipts,'duplicate helper receipt');r=load(path);receipts[n]=r
            require(r['wait_completed'] is True and r['error'] is None and type(r['pid'])is int and r['pid']>0,'owned completed helper')
            command=r['command'];require(command[:7]==[sys.executable,'-X','utf8','-B',str(ROOT/CODE/'worker.py'),role,'--store'] and command[7]==str(case/'store'),'helper command identity')
            options=dict(zip(command[8::2],command[9::2]));require(len(command[8:])==len(options)*2,'helper options duplicate')
            require(set(options)==({'--layout','--unit'} if role in ('init','update') else {'--trust'} if role=='read' else {'--trust','--proof','--app'}),'helper options shape')
            if role in ('init','update'):require(options['--layout'] in ('in-place','staged-generation') and options['--unit'] in ('event','utf8-byte'),'helper profile')
            else:
                for v in options.values():require(pathlib.Path(v).resolve().is_relative_to(case.resolve()),'helper argument path')
            start,end=[datetime.datetime.fromisoformat(r[k]) for k in ('started_at','finished_at')];require(start.tzinfo and end.tzinfo and start<=end,'helper timestamps')
            phases=[v['phase'] for v in r['records'] if 'phase' in v];cut=r['requested_cut'];wire=[v['wire'] for v in r['records'] if 'wire' in v]
            expected=WRITER if role=='update' else RECEIVER if role=='receive' and any(m['type']=='RESET' for m in wire) else []
            if cut is not None:
                require(role in cut_counts and cut in expected and phases==expected[:expected.index(cut)+1] and r['cut_observed'] is True and r['terminated_by_controller'] is True and type(r['exit_code'])is int and r['exit_code']!=0,'named termination evidence');cut_counts[role]+=1
            else:
                refused=bool(r['records'] and r['records'][-1].get('status')=='helper-refused')
                require(phases==expected and r['cut_observed'] is False and r['terminated_by_controller'] is False and r['exit_code']==(2 if refused else 0),'normal helper completion')
            if role=='read':
                require(len(r['records'])==1,'single read report');p=r['records'][0];t=load(pathlib.Path(options['--trust']));require(p['reader_pid']==r['pid'] and p['nonce']==t['nonce'] and p['attempt']==case.name==t['attempt'],'fresh read provenance')
        for key in ('store','reopened'):
            if key not in row:continue
            p=row[key];rr=load(bound(case,p['_reader_receipt']));raw=rr['records'][0];require({k:v for k,v in p.items() if not k.startswith('_')}=={k:v for k,v in raw.items() if k not in ('attempt','nonce','reader_pid')},'row/read receipt')
            snapshot=bound(case,p['_read_snapshot'])
            for path,digest in p['reads'].items():require(sha(bound(snapshot,path).read_bytes())==digest,'read bytes at observation')
            if p['status']!='blocked':
                selected=next(k.rsplit('/',1)[0] for k in p['reads'] if k.endswith('/manifest.json'));names=sorted(q.name for q in (snapshot/selected).iterdir());require(names==p['selected_files'],'complete selected namespace')
                ids={n for n in (1,2,3) if f'event{n}.json' in names};floor=max({1,2,3}-ids,default=0);require(p['derived_floor_event']==floor,'raw replay floor')
                s=load(snapshot/selected/'snapshot.json');n=s['event_cursor'];require(type(n)is int and n>=floor and s==p['snapshot'],'raw snapshot identity')
                content=[b'',b'A',b'A\xc3\xa9',b'A\xc3\xa9B'][n];require(s['state_base64']==base64.b64encode(content).decode() and s['byte_cursor']==len(content) and s['state_sha256']==sha(content),'raw snapshot content')
        for key in ('receiver','at_cut','recovery','repeat_attach'):
            if key not in row:continue
            v=row[key];r=load(bound(case,v['receipt']));wire=[m['wire'] for m in r['records'] if 'wire' in m];require(v['wire']==wire and v['application']==load(bound(case,v['application_file'])),'receiver raw binding')
            a=v['application'];n=a['event_cursor'];require(type(n)is int and 0<=n<=3,'application event cursor');raw=[b'',b'A',b'A\xc3\xa9',b'A\xc3\xa9B'][n]
            require(set(a)==set('version stream epoch generation event_cursor byte_cursor state_base64'.split()) and a['version']==1 and a['stream']=='stream-a' and a['epoch']==2 and a['byte_cursor']==len(raw) and a['state_base64']==base64.b64encode(raw).decode(),'complete application envelope')
            expected_n=(2 if row.get('cut')=='reset_committed' else 1) if key=='at_cut' else 1 if v['refused'] else 3
            expected_g=2 if key in ('recovery','repeat_attach') or (key=='at_cut' and expected_n==2) or (key=='receiver' and any(m['type']=='RESET' for m in wire)) else 1
            require(n==expected_n and a['generation']==expected_g,'application committed stage/generation')
            if wire:
                f=copy.deepcopy(fixture);f.update(messages=wire,queue_limit_bytes=2,queue_limit_events=2);schema.validate(f);require(oracle(f)==v['decision'] and v['decision']['status'] in ('accepted','accepted-reset'),'literal wire decision')
            else:require(v['refused'] is True and v['decision'] is None,'silent refusal')
    require(sorted(receipts)==list(range(1,436)) and cut_counts=={'update':40,'receive':24},'all helper/cut receipts')
def claims(e):
    ledger=(ROOT/'docs/v3/CLAIM-LEDGER.md').read_text(encoding='utf8');FM['HIST']['OLD']['registry_shape'](load(ROOT/'docs/v3/CLAIM-REGISTRY.json'),ledger)
    require(len(e['claims'])==3 and {c['id'] for c in e['claims']}=={'RSE-001','RSE-002','RSE-003'},'claim identities')
    for c in e['claims']:require(c['state']=='locally observed' and '| '+c['id']+' | '+c['statement']+' | '+c['state']+' |' in ledger and c['canonical'] in CANONICAL and c['id'] in (ROOT/c['canonical']).read_text(encoding='utf8'),'claim binding')
def evidence(e,expected):
    require(e['start_commit']==BASE and all(e[k] is False for k in ('formal_freeze','production_authentication_established','power_loss_durability_established')) and e['new_owner_questions']==[],'evidence scope')
    result_check(read('results.json'),expected);require(e['semantic_results_sha256']==sha(canonical(expected).encode()),'semantic hash')
    cache=common()/'research-attestations/replay-store-evidence/discovery';rows=e['retained_runs']
    require(len(rows)==len({r['id'] for r in rows}) and {r['id'] for r in rows}=={p.name for p in cache.iterdir() if p.is_dir() and (p/'admission.json').exists()},'all admitted attempts')
    accepted=[]
    for row in rows:
        directory=bound(cache,row['id']);actual={p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()};require(actual==row['files'],'complete raw evidence hashes')
        a,x=load(directory/'admission.json'),load(directory/'execution.json');admission(a,x,directory,row['id']==e['accepted_run']);require(row['exit_code']==x['exit_code'],'attempt exit binding')
        if row['id']==e['accepted_run']:
            require(e['accepted_source_commit']==a['source_commit'],'accepted source binding')
            for path in SOURCE_PATHS:require(bound(directory,'source/'+path).read_bytes().replace(b'\r\n',b'\n')==(ROOT/path).read_bytes().replace(b'\r\n',b'\n'),'accepted source identity')
            result_check(load(directory/'cases/result.json'),expected);raw_check(directory,expected);accepted.append(row)
    require(len(accepted)==1,'one accepted attempt');claims(e)
def reject(fn,value):
    try:fn(value)
    except (ValueError,KeyError,TypeError,AssertionError,OSError,subprocess.SubprocessError):return
    raise ValueError('adversarial mutation accepted')
def main():
    p=argparse.ArgumentParser();p.add_argument('--preflight',action='store_true');p.add_argument('--working',action='store_true');p.add_argument('--candidate');args=p.parse_args();preflight();goal_check(read('goal.json'))
    if args.preflight:return
    candidate=args.candidate or git('rev-parse','HEAD');FM['candidate_check'](candidate)
    changed=git('diff','--name-only',BASE,candidate).splitlines();preserve(changed);manifests()
    out=common()/'research-attestations/replay-store-evidence'/(candidate if not args.working else 'working');out.mkdir(parents=True,exist_ok=True);runid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f');directory=out/runid
    a,x=ADMIT['execute'](directory);admission(a,x,directory);actual=load(directory/'cases/result.json');raw_check(directory,actual);evidence(read('evidence.json'),actual)
    labels=[]
    for key,value in [('start_commit','0'*40),('new_metered_spend',1),('usage_resets_allowed',True),('deadline_utc','2099-01-01T00:00:00Z')]:
        bad=copy.deepcopy(read('goal.json'));bad[key]=value;reject(goal_check,bad);labels.append('goal/'+key)
    reject(FM['candidate_check'],'0'*40);labels.append('wrong-candidate');reject(preserve,['CONTROL_PLANE.md']);labels.append('protected-path')
    for key,value in [('case_count',114),('helper_process_count',434),('formal_freeze',True),('power_loss_durability_established',True),('live_provider_calls',1),('rows',[])]:
        bad=copy.deepcopy(actual);bad[key]=value;reject(lambda v:result_check(v,actual),bad);labels.append('result/'+key)
    for kind in ['erase-run','empty-digests','bad-digest','bad-source','promote-claim','false-semantic','omit-admission']:
        bad=copy.deepcopy(read('evidence.json'))
        if kind=='erase-run':bad['retained_runs'].pop()
        elif kind=='empty-digests':bad['retained_runs'][-1]['files']={}
        elif kind=='bad-digest':bad['retained_runs'][-1]['files']['execution.json']='0'*64
        elif kind=='bad-source':bad['accepted_source_commit']='0'*40
        elif kind=='promote-claim':bad['claims'][0]['state']='measured'
        elif kind=='false-semantic':bad['semantic_results_sha256']='0'*64
        else:bad['retained_runs'][-1]['files'].pop('admission.json')
        reject(lambda v:evidence(v,actual),bad);labels.append('evidence/'+kind)
    for kind in ['omit-source','duplicate-source','bad-command','bad-time','bad-host','bad-limit']:
        bad=copy.deepcopy(a)
        if kind=='omit-source':bad['source_files'].pop()
        elif kind=='duplicate-source':bad['source_files'][-1]=bad['source_files'][0]
        elif kind=='bad-command':bad['command'][4]='other.py'
        elif kind=='bad-time':bad['started_at']='2099-01-01T00:00:00Z'
        elif kind=='bad-host':bad['host']['filesystem']='unknown'
        else:bad['limits']['child_seconds']=999
        reject(lambda v:admission(v,x,directory),bad);labels.append('admission/'+kind)
    # Rebound observation mutations still fail against independent child records/files.
    for key in ['wire','application','reader','floor']:
        bad=copy.deepcopy(actual)
        if key=='wire':bad['rows'][0]['receiver']['wire'].pop()
        elif key=='application':bad['rows'][0]['receiver']['application']['generation']=2
        elif key=='reader':bad['rows'][0]['store']['reads']['CURRENT.json']='0'*64
        else:bad['rows'][0]['store']['derived_floor_event']=2
        reject(lambda v:raw_check(directory,v,{r['case']:r for r in v['rows']}),bad);labels.append('raw/'+key)
    if args.working:print('REPLAY_STORE_WORKING_PASS_NOT_FINAL '+json.dumps({'run_id':runid,'adversarial_checks':len(labels)}));return
    inv=read('validation-inventory.json');prior=FM['HIST']['read']('validation-inventory.json');require(inv['start_commit']==BASE and inv['regression_commands']==prior['regression_commands']==FM['HIST']['OLD']['regression_commands']() and len(inv['regression_commands'])==25,'unchanged25')
    for item in prior['regression_entrypoints']:require(sha(git('show',candidate+':'+item['path'],raw=True))==item['sha256'] and git('show',candidate+':'+item['path'],raw=True)==git('show',BASE+':'+item['path'],raw=True),'historical validator identity')
    require(set(inv['artifacts'])==set(changed)-{PREFIX+'validation-inventory.json'},'artifact inventory coverage')
    for path,digest in inv['artifacts'].items():require(sha(git('show',candidate+':'+path,raw=True))==digest,'artifact inventory hash')
    git('diff','--check',BASE,candidate);frozen=[]
    for commit,branch,script in [(BASE,'codex/v3-flow-recovery-integration-20260907','experiments/v3/flow-recovery-integration/check.py'),(FRI['BASE'],'codex/v3-reset-mapping-20260907','experiments/v3/reset-mapping/check.py'),(FRI['RSM']['BASE'],'codex/v3-formal-comparison-20260907','experiments/v3/formal-comparison/check.py'),(FM['BASE'],'codex/v3-interface-probes-20260907','experiments/v3/interface-probes/check.py'),(FM['RESEARCH'],'codex/v3-formal-model-experiment','docs/v3/foundation-research/mark2-research/mark3-comparison/check.py')]:
        d=FM['frozen_root'](commit,branch);frozen.append(FM['run_command']([sys.executable,'-X','utf8','-B',script,'--working'],d,out,runid+'-frozen-'+commit[:7]));require(git('rev-parse','HEAD',root=d)==commit and not git('status','--porcelain=v1','--untracked-files=all',root=d),'frozen worktree changed')
    regressions=[FM['run_command']([sys.executable,*cmd[1:]],ROOT,out,runid+'-regression-'+str(n)) for n,cmd in enumerate(inv['regression_commands'])];FM['candidate_check'](candidate)
    receipt={'status':'REPLAY_STORE_GATE_PASS','candidate':candidate,'base':BASE,'run_id':runid,'adversarial_checks':labels,'case_count':actual['case_count'],'helper_process_count':actual['helper_process_count'],'semantic_results_sha256':sha(canonical(actual).encode()),'execution_directory':str(directory),'frozen_validations':frozen,'regressions':regressions,'formal_freeze':False,'artifacts':{p:sha(git('show',candidate+':'+p,raw=True)) for p in changed}}
    raw=(json.dumps(receipt,indent=2)+'\n').encode();(out/(runid+'.json')).write_bytes(raw);print('REPLAY_STORE_GATE_PASS '+json.dumps({'candidate':candidate,'run_id':runid,'receipt_sha256':sha(raw)}))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:print('REPLAY_STORE_GATE_FAIL '+str(exc),file=sys.stderr);raise SystemExit(1)
