"""Exact-candidate generation authority gate with independent raw trace reconstruction."""
import argparse,hashlib,json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE='04b664c58bddb72674d297f4bcf4bef5435bda0f'
AREA=ROOT/'docs/v3/construction/generation-authority-20260907'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def require(ok,message):
    if not ok:raise ValueError(message)
def preflight():
    g=json.loads((AREA/'goal.json').read_text());require(g['start_commit']==BASE and g['parent_goal']=='goal-recursion-v2-execution-fabric','goal lineage')
    require(g['new_metered_spend']==0 and g['usage_resets_allowed'] is False,'capacity boundary');require(git('branch','--show-current')==g['branch'],'branch')
    for a in [BASE,'a7cd9458d37f3090079930bf8d79ffd77c4f73e4']:git('merge-base','--is-ancestor',a,'HEAD')
    owners=[r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+g['branch'] in r.splitlines()];require(len(owners)==1 and pathlib.Path(owners[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive ownership')
    common=pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'));require(not (ROOT/'state/PAUSE').exists() and not (common.parent/'state/PAUSE').exists(),'PAUSE')
    p=common/'research-attestations/replay-store-evidence'/BASE;c=json.loads((p/'completion.json').read_text());require(c['status']=='published-scoped-campaign-complete' and c['candidate']==BASE,'predecessor')
    rs=[]
    for n,h in c['receipts'].items():
        raw=(p/n).read_bytes();require(hashlib.sha256(raw).hexdigest()==h,'receipt hash');rs.append(json.loads(raw))
    require(all(r['candidate']==BASE for r in rs) and sum(r.get('status')=='REPLAY_STORE_GATE_PASS' for r in rs)==2 and len({r['reviewer'] for r in rs if r.get('verdict')=='approve'})==2,'two exact predecessor gates/reviews')
    print('GENERATION_AUTHORITY_PREFLIGHT_PASS_NOT_FINAL')

import copy,datetime,re,runpy,sys
RSE=runpy.run_path(str(ROOT/'experiments/v3/replay-store-evidence/check.py'))
FRI=RSE['FRI']
FM=FRI['FM'];git=FM['git'];sha=FM['sha']
ADMIT=runpy.run_path(str(ROOT/'experiments/v3/generation-authority/admit.py'))
PREFIX='docs/v3/construction/generation-authority-20260907/'
CODE='experiments/v3/generation-authority/'
AREA=ROOT/PREFIX
CANONICAL=FRI['CANONICAL']
SOURCE_PATHS=set(ADMIT['SOURCES'])
def load(path):return FM['strict'](path.read_text(encoding='utf8'))
def read(name):return load(AREA/name)
def common():return pathlib.Path(git('rev-parse','--path-format=absolute','--git-common-dir'))
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def bound(directory,path):
    p=directory/path;require(p.resolve().is_relative_to(directory.resolve()),'evidence path escape');return p
def goal_check(g):
    require(g['start_commit']==BASE and g['id']=='recursion.v3.generation-authority.20260907' and g['parent_goal']=='goal-recursion-v2-execution-fabric','goal identity')
    require(type(g['new_metered_spend'])is int and g['new_metered_spend']==0 and g['usage_resets_allowed'] is False,'spend/reset')
    require(g['started_at']=='2026-09-08T05:01:52Z' and g['deadline_utc']=='2026-09-08T08:01:52Z' and g['discovery_cutoff_utc']=='2026-09-08T06:31:52Z' and g['synthesis_review_reserve_minutes']==90,'time envelope')
    require(set(g['allowed_paths'])==CANONICAL|{PREFIX+'**',CODE+'**'} and g['max_concurrent_read_only_workers']==2,'scope/worker bounds')
    require(g['capacity']['checkpoint_at_remaining_percent']==3 and g['capacity']['no_new_workers_at_remaining_percent']==6,'capacity reserve')
def preserve(changed):
    require(changed and all(p in CANONICAL or p.startswith(PREFIX) or p.startswith(CODE) for p in changed),'protected change')
    require(not git('diff','--name-only','--diff-filter=D',BASE),'deletion')
    for path in CANONICAL:
        old=git('show',BASE+':'+path);new=(ROOT/path).read_text(encoding='utf8')
        if path.endswith('.json'):
            a,b=json.loads(old),json.loads(new);b['ranges']=[r for r in b['ranges'] if r['prefix']!='GRA'];require(a==b,'historical registry changed')
        else:
            lines=iter(new.splitlines())
            for line in old.splitlines():require(any(line==n for n in lines),'historical content changed '+path)
    FM['HIST']['PRIOR']['document_gate'](changed)
    RSE['claims'](RSE['read']('evidence.json'));FRI['claims'](FRI['read']('evidence.json'));FRI['RSM']['claims'](FRI['RSM']['read']('evidence.json'))
    FM['claim_bindings'](FM['read']('evidence.json'));FM['IP']['claim_bindings'](FM['IP']['read']('evidence.json'))
    FM['HIST']['bindings'](FM['HIST']['read']('evidence.json'));FM['HIST']['bindings'](FM['HIST']['M']['read']('evidence.json'))
def manifests():
    m=read('manifest.json');require(m['start_commit']==BASE and m['parent_goal']=='goal-recursion-v2-execution-fabric','manifest lineage')
    expected={r['path'] for r in RSE['read']('manifest.json')['inputs']}|set(git('diff','--name-only',RSE['BASE'],BASE).splitlines())
    require(len(m['inputs'])==len(expected) and {r['path'] for r in m['inputs']}==expected,'complete frozen inputs')
    for r in m['inputs']:require(sha(git('show',BASE+':'+r['path'],raw=True))==r['git_blob_sha256'],'frozen input hash')
    rows=read('sources.json')['sources'];require(len(rows)==26 and len({r['file'] for r in rows})==26,'source identities')
    for r in rows:
        require(re.fullmatch('[0-9a-f]{40}',r['commit']) and r['url']=='https://raw.githubusercontent.com/'+r['repository']+'/'+r['commit']+'/'+r['path'],'pinned primary source')
        require(sha(bound(common()/'research-attestations/generation-authority/primary-sources',r['file']).read_bytes())==r['sha256'],'primary source bytes')

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
AUDIT=runpy.run_path(str(ROOT/CODE/'audit.py'))
raw_check=AUDIT['audit']
EXPECTED_AUDIT={'case_count':128,'helpers':400,'commits':764,'completed_reads':56,'killed_helpers':80,'overlap_publications':24,'reclaimed_with_current_reader':8}

def result_check(value,expected):
    require(canonical(value)==canonical(expected),'semantic result differs')
    require(value['status']=='named-concurrent-schedules-pass' and value['case_count']==128 and value['helper_process_count']==400 and value['all_helpers_waited'] is True,'closed process coverage')
    require(type(value['live_provider_calls']) is int and value['live_provider_calls']==0 and all(value[k] is False for k in ('formal_freeze','production_authentication_established','power_loss_durability_established')),'claim boundary')

def claims(e):
    ledger=(ROOT/'docs/v3/CLAIM-LEDGER.md').read_text(encoding='utf8');FM['HIST']['OLD']['registry_shape'](load(ROOT/'docs/v3/CLAIM-REGISTRY.json'),ledger)
    require(len(e['claims'])==3 and {c['id'] for c in e['claims']}=={'GRA-001','GRA-002','GRA-003'},'claim identities')
    for c in e['claims']:require(c['state']=='locally observed' and '| '+c['id']+' | '+c['statement']+' | '+c['state']+' |' in ledger and c['canonical'] in CANONICAL and c['id'] in (ROOT/c['canonical']).read_text(encoding='utf8'),'claim binding')
def evidence(e,expected):
    require(e['start_commit']==BASE and all(e[k] is False for k in ('formal_freeze','production_authentication_established','power_loss_durability_established')) and e['new_owner_questions']==[],'evidence scope')
    result_check(read('results.json'),expected);require(e['semantic_results_sha256']==sha(canonical(expected).encode()),'semantic hash')
    cache=common()/'research-attestations/generation-authority/discovery';rows=e['retained_runs']
    require(len(rows)==len({r['id'] for r in rows}) and {r['id'] for r in rows}=={p.name for p in cache.iterdir() if p.is_dir() and (p/'admission.json').exists()},'all admitted attempts')
    accepted=[]
    for row in rows:
        directory=bound(cache,row['id']);actual={p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()};require(actual==row['files'],'complete raw evidence hashes')
        a,x=load(directory/'admission.json'),load(directory/'execution.json');admission(a,x,directory,row['id']==e['accepted_run']);require(row['exit_code']==x['exit_code'],'attempt exit binding')
        if row['id']==e['accepted_run']:
            require(e['accepted_source_commit']==a['source_commit'],'accepted source binding')
            for path in SOURCE_PATHS:require(bound(directory,'source/'+path).read_bytes().replace(b'\r\n',b'\n')==(ROOT/path).read_bytes().replace(b'\r\n',b'\n'),'accepted source identity')
            result_check(load(directory/'cases/result.json'),expected);require(raw_check(directory,expected)==EXPECTED_AUDIT,'independent raw counts');accepted.append(row)
    require(len(accepted)==1,'one accepted attempt');claims(e)
def reject(fn,value):
    try:fn(value)
    except (ValueError,KeyError,TypeError,AssertionError,OSError,subprocess.SubprocessError):return
    raise ValueError('adversarial mutation accepted')

def adversarial(a,x,directory,actual):
    labels=[]
    for key,value in [('start_commit','0'*40),('new_metered_spend',1),('usage_resets_allowed',True),('deadline_utc','2099-01-01T00:00:00Z')]:
        bad=copy.deepcopy(read('goal.json'));bad[key]=value;reject(goal_check,bad);labels.append('goal/'+key)
    reject(FM['candidate_check'],'0'*40);labels.append('wrong-candidate');reject(preserve,['CONTROL_PLANE.md']);labels.append('protected-path')
    for key,value in [('case_count',127),('helper_process_count',399),('formal_freeze',True),('production_authentication_established',True),('power_loss_durability_established',True),('live_provider_calls',1),('rows',[])]:
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
        else:bad['limits']['command_seconds']=999
        reject(lambda v:admission(v,x,directory),bad);labels.append('admission/'+kind)
    # Mutated journals/blobs bypass outer digest inventories to challenge semantics.
    for kind in ['erase-wait','wrong-pid','transplant-ticket','uncommitted-reply','early-delete','changed-read','changed-staging','wrong-lock','erase-cut','fake-death','erase-refusal','invented-phase','invented-fault']:
        name='r0-pinned-generation-event-'+('negative_tokens' if kind in ('erase-refusal','invented-fault') else 'overlap_manifest' if kind=='invented-phase' else 'reader_death' if kind=='fake-death' else 'publish_reply_loss' if kind=='erase-cut' else 'overlap_pin')
        journal=[AUDIT['strict'](line) for line in (directory/'cases'/name/'journal.jsonl').read_bytes().splitlines()];bad=copy.deepcopy(journal);blobs={}
        if kind=='erase-refusal':bad=[e for e in bad if not(e['kind']=='receive' and e['value'].get('response',{}).get('status')=='refused')]
        elif kind=='invented-phase':
            for e in bad:
                if e['kind']=='receive' and e['value'].get('phase')=='reader:manifest':e['value']['phase']='reader:invented'
                if e['kind']=='snapshot' and e['label'].endswith('/reader:manifest'):e['label']=e['label'].replace('reader:manifest','reader:invented')
        elif kind=='invented-fault':next(e for e in bad if e['kind']=='injected-stage-fault')['path']='store/g1/UNAUTHORIZED'
        elif kind=='erase-wait':bad.remove(next(e for e in bad if e['kind']=='wait'))
        elif kind=='wrong-pid':next(e for e in bad if e['kind']=='wait')['pid']=-1
        elif kind=='transplant-ticket':next(e for e in bad if e['kind']=='receive' and 'ticket' in e['value'])['value']['ticket']['actor_nonce']='0'*32
        elif kind=='uncommitted-reply':next(e for e in bad if e['kind']=='receive' and 'response' in e['value'])['value']['response']['writer']['serial']=99
        elif kind=='early-delete':next(e for e in bad if e['kind']=='snapshot' and e['label'].endswith('/reader:pinned'))['files'].pop('store/g1/event1.json')
        elif kind=='changed-read':next(e for e in bad if e['kind']=='receive' and 'observation' in e['value'])['value']['observation']['generation']=2
        elif kind=='changed-staging':
            e=next(e for e in bad if e['kind']=='snapshot' and e['label'].endswith('/publish:staged'));h=e['files']['authority.tmp'];v=load(directory/'cases/blobs'/h);v['pins']={};blobs[h]=AUDIT['encode'](v)
        elif kind=='wrong-lock':next(e for e in bad if e['kind']=='receive' and e['value'].get('lock_acquired'))['value']['offset']=1
        elif kind=='erase-cut':next(e for e in bad if e['kind']=='wait' and e['killed'])['killed']=False
        else:
            e=next(e for e in bad if e['kind']=='wait' and e['killed']);e['killed']=False;e['exit_code']=0
        reject(lambda _:raw_check(directory,actual,{name:bad},blobs),None);labels.append('raw/'+kind)
    return labels

def main():
    p=argparse.ArgumentParser();p.add_argument('--preflight',action='store_true');p.add_argument('--working',action='store_true');p.add_argument('--candidate');args=p.parse_args();preflight();goal_check(read('goal.json'))
    if args.preflight:return
    candidate=args.candidate or git('rev-parse','HEAD');FM['candidate_check'](candidate);changed=git('diff','--name-only',BASE,candidate).splitlines();preserve(changed);manifests()
    out=common()/'research-attestations/generation-authority'/(candidate if not args.working else 'working');out.mkdir(parents=True,exist_ok=True);runid=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%f');directory=out/runid
    a,x=ADMIT['execute'](directory);admission(a,x,directory);actual=load(directory/'cases/result.json');counts=raw_check(directory,actual);require(counts==EXPECTED_AUDIT,'independent raw counts');evidence(read('evidence.json'),actual);labels=adversarial(a,x,directory,actual)
    if args.working:print('GENERATION_AUTHORITY_WORKING_PASS_NOT_FINAL '+json.dumps({'run_id':runid,'adversarial_checks':len(labels),'raw_audit':counts}));return
    inv=read('validation-inventory.json');prior=FM['HIST']['read']('validation-inventory.json');require(inv['start_commit']==BASE and inv['regression_commands']==prior['regression_commands']==FM['HIST']['OLD']['regression_commands']() and len(inv['regression_commands'])==25,'unchanged25')
    for item in prior['regression_entrypoints']:require(sha(git('show',candidate+':'+item['path'],raw=True))==item['sha256'] and git('show',candidate+':'+item['path'],raw=True)==git('show',BASE+':'+item['path'],raw=True),'historical validator identity')
    require(set(inv['artifacts'])==set(changed)-{PREFIX+'validation-inventory.json'},'artifact inventory coverage')
    for path,digest in inv['artifacts'].items():require(sha(git('show',candidate+':'+path,raw=True))==digest,'artifact inventory hash')
    git('diff','--check',BASE,candidate);frozen=[]
    configurations=[(BASE,'codex/v3-replay-store-evidence-20260907','experiments/v3/replay-store-evidence/check.py'),(RSE['BASE'],'codex/v3-flow-recovery-integration-20260907','experiments/v3/flow-recovery-integration/check.py'),(FRI['BASE'],'codex/v3-reset-mapping-20260907','experiments/v3/reset-mapping/check.py'),(FRI['RSM']['BASE'],'codex/v3-formal-comparison-20260907','experiments/v3/formal-comparison/check.py'),(FM['BASE'],'codex/v3-interface-probes-20260907','experiments/v3/interface-probes/check.py'),(FM['RESEARCH'],'codex/v3-formal-model-experiment','docs/v3/foundation-research/mark2-research/mark3-comparison/check.py')]
    require(inv['frozen_gates']==[{'commit':c,'branch':b,'script':s} for c,b,s in configurations],'six frozen gate inventory')
    for commit,branch,script in configurations:
        d=FM['frozen_root'](commit,branch);frozen.append(FM['run_command']([sys.executable,'-X','utf8','-B',script,'--working'],d,out,runid+'-frozen-'+commit[:7]));require(git('rev-parse','HEAD',root=d)==commit and not git('status','--porcelain=v1','--untracked-files=all',root=d),'frozen worktree changed')
    regressions=[FM['run_command']([sys.executable,*cmd[1:]],ROOT,out,runid+'-regression-'+str(n)) for n,cmd in enumerate(inv['regression_commands'])];FM['candidate_check'](candidate)
    receipt={'status':'GENERATION_AUTHORITY_GATE_PASS','candidate':candidate,'base':BASE,'run_id':runid,'adversarial_checks':labels,'raw_audit':counts,'semantic_results_sha256':sha(canonical(actual).encode()),'execution_directory':str(directory),'execution_files':{p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in sorted(directory.rglob('*')) if p.is_file()},'frozen_validations':frozen,'regressions':regressions,'formal_freeze':False,'artifacts':{p:sha(git('show',candidate+':'+p,raw=True)) for p in changed}}
    raw=(json.dumps(receipt,indent=2)+'\n').encode();(out/(runid+'.json')).write_bytes(raw);print('GENERATION_AUTHORITY_GATE_PASS '+json.dumps({'candidate':candidate,'run_id':runid,'receipt_sha256':sha(raw)}))
if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as exc:print('GENERATION_AUTHORITY_GATE_FAIL '+str(exc),file=sys.stderr);raise SystemExit(1)
