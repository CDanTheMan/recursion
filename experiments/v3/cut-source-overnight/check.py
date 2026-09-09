"""SC-CUT-SOURCE-01 full gate. Two identical clean passes are required externally."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import runpy
import run_packet as runner

ROOT=runner.ROOT; PREFIX=runner.PREFIX; CODE=runner.CODE
sys.path.insert(0,str(ROOT/'experiments/v3/cut-publication'))
BASE='ec4232e95722d58dc0eff03289fb629b58d29247'
PREVIOUS='e4b844b1af6c309263812c6961ccb50b3e5b8a82'
read=runner.read; sha=runner.sha

def require(ok,message):
    if not ok: raise ValueError(message)

def git(*args): return runner.git(*args).decode('utf-8').strip()
def doc(name): return read(ROOT/PREFIX/name)

def preflight():
    g=doc('goal.json'); a=read(runner.cache()/'activation.json')
    require(g['start_commit']==BASE and g['campaign']=='SC-CUT-SOURCE-01','goal identity')
    require(g['started_at']=='2026-09-09T03:40:33Z' and g['deadline_utc']=='2026-09-09T15:40:33Z' and g['discovery_cutoff_utc']=='2026-09-09T12:40:33Z','fixed absolute clock')
    for key in a['goal']: require(g[key]==a['goal'][key], 'activation mutation '+key)
    require(sha((runner.cache()/'activation.json').read_bytes())==doc('activation.json')['sha256'],'activation receipt')
    require(git('branch','--show-current')==g['branch'],'campaign branch')
    git('merge-base','--is-ancestor',BASE,'HEAD')
    require(not (ROOT/'state/PAUSE').exists() and not (runner.common().parent/'state/PAUSE').exists(),'PAUSE')
    require('status: active' in (ROOT/'state/goals/goal-recursion-v2-execution-fabric.md').read_text(),'active parent')
    rows=[r for r in git('worktree','list','--porcelain').split('\n\n') if 'branch refs/heads/'+g['branch'] in r.splitlines()]
    require(len(rows)==1 and Path(rows[0].splitlines()[0][9:]).resolve()==ROOT,'exclusive worktree')
    previous=runner.common()/'research-attestations/cut-publication'/PREVIOUS
    complete=read(previous/'completion.json')
    require(sha((previous/'completion.json').read_bytes())=='5187d9c0fff0a7077dcf291eda205009d076641c5eda17c4933e9b89eea2a8b1','predecessor completion')
    require(len(complete['all_external_files_before_completion'])==245,'complete predecessor file inventory')
    for name,digest in complete['all_external_files_before_completion'].items():
        path=(previous/name).resolve(); require(path.is_relative_to(previous.resolve()) and sha(path.read_bytes())==digest,'predecessor evidence '+name)
    for row in doc('manifest.json')['inputs']:
        require(sha(runner.git('show',BASE+':'+row['path']))==row['git_blob_sha256'],'baseline input '+row['path'])

def candidate_check(candidate):
    require(candidate==git('rev-parse','HEAD') and len(candidate)==40 and not git('status','--porcelain','--untracked-files=all'),'identical clean candidate required')
    paths=git('diff','--name-only',BASE,candidate).splitlines(); allowed=doc('goal.json')['allowed_paths']
    require(paths and all(p in allowed or any(a.endswith('/**') and p.startswith(a[:-2]) for a in allowed) for p in paths),'allowlist')
    require(not git('diff','--name-only','--diff-filter=D',BASE,candidate),'no historical deletion')
    git('diff','--check',BASE,candidate)
    for path in allowed[:8]:
        old=runner.git('show',BASE+':'+path); new=(ROOT/path).read_bytes()
        # Canonical changes are optional. If present, only append-only Markdown here.
        if path.endswith('.json'): require(old.replace(b'\r\n',b'\n')==new.replace(b'\r\n',b'\n'),'registry unchanged')
        else:
            lines=iter(new.decode('utf-8').splitlines())
            require(all(any(line==n for n in lines) for line in old.decode('utf-8').splitlines()),'preserved canonical history')
    return paths

def validate_result(result):
    import s_domain as domain
    import s_experiment as experiment
    require(result['status']=='cut-source-pass' and result['queue_item']=='all','complete queue result')
    require(result['classification']=='modeled' and all(result[k] is False for k in ('formal_freeze','full_comparison_complete','runtime_integration_support')),'claim boundary')
    require(result['network_operations']==0,'no model network operations')
    keys={n+'/'+u+'/'+str(o) for n,p in domain.PROFILES.items() for u in domain.UNITS for o in p['outcomes']}
    require(set(result['profiles'])==keys,'complete profile domain')
    require(result['frontier']==0 and all(r['frontier']==0 and r['exact_graph_equal'] for r in result['profiles'].values()),'zero finite frontier')
    require(result['states_per_representation']==sum(r['states'] for r in result['profiles'].values())<=500000,'state sum and bound')
    require(result['edges_per_representation']==sum(r['edges'] for r in result['profiles'].values()),'edge sum')
    require({(r['guard'],r['unit']) for r in result['mutants']}=={(g,u) for g in experiment.MUTANTS for u in domain.UNITS},'guard inventory')
    require(len(result['mutants'])==2*len(experiment.MUTANTS) and all(r['rejected'] for r in result['mutants']),'distinguishing mutants')

def verify_run(directory,accepted=False):
    a=read(directory/'admission.json'); x=read(directory/'execution.json')
    require(a['status']=='admitted-before-execution' and a['limits']==doc('goal.json')['experiment_limits'],'run bounds')
    require(set(a['sources'])==set(runner.source_paths()),'complete admitted source closure')
    git('merge-base','--is-ancestor',BASE,a['source_commit']); git('merge-base','--is-ancestor',a['source_commit'],'HEAD')
    for path,hashes in a['sources'].items():
        raw=(directory/'source'/path).read_bytes(); blob=runner.git('show',a['source_commit']+':'+path)
        require(sha(raw)==hashes['working_sha256'] and sha(blob)==hashes['git_blob_sha256'] and raw.replace(b'\r\n',b'\n')==blob.replace(b'\r\n',b'\n'),'admitted source binding')
        if accepted: require(raw.replace(b'\r\n',b'\n')==(ROOT/path).read_bytes().replace(b'\r\n',b'\n'),'accepted current source bytes')
    begin=dt.datetime.fromisoformat(a['started_at']); end=dt.datetime.fromisoformat(x['finished_at'])
    require(dt.datetime.fromisoformat(doc('goal.json')['started_at'])<=begin<=end<=dt.datetime.fromisoformat(doc('goal.json')['deadline_utc']),'run clock')
    require(a['command']==[a['host']['executable'],'-X','utf8','-B',CODE+'s_experiment.py','--queue-item',a['queue_item'],'--output',str(directory/'result.json')],'exact command')
    if accepted:
        require(x['status']=='finished' and x['exit_code']==0 and 0<x['sampled_peak_bytes']<=2147483648 and x['seconds']<=600,'successful bounded execution')
        require(sum(p.stat().st_size for p in directory.rglob('*') if p.is_file())<=268435456,'artifact bound')
    return a,x

def validate_coverage(coverage):
    prior=read(ROOT/'docs/v3/construction/cut-publication-20260908/coverage.json')
    require(coverage['predecessor_coverage']==prior,'preserved six obligations and 27 trace history')
    require([r['id'] for r in coverage['slice_obligations']]==[r['id'] for r in prior['slice_obligations']] and len(coverage['slice_obligations'])==6,'six obligations')
    require([r['id'] for r in coverage['slice_traces']]==[r['id'] for r in prior['slice_traces']] and len(coverage['slice_traces'])==27,'27 trace rows')
    require(coverage['formal_freeze'] is False and coverage['full_comparison_complete'] is False,'coverage residuals')
    for row in coverage['slice_obligations']+coverage['slice_traces']:
        require(row['status'] in ('partial-modeled-support','no-new-coverage') and row['residual'],'bounded row claim')

def adversarial(result):
    import copy
    labels=[]
    def reject(fn,value,label):
        try: fn(value)
        except (ValueError,KeyError,TypeError,AssertionError): labels.append(label); return
        raise ValueError('gate accepted adversarial corruption '+label)
    for key,value in [('profiles',{}),('mutants',[]),('frontier',1),('classification','measured'),('formal_freeze',True),('full_comparison_complete',True),('runtime_integration_support',True),('network_operations',1),('states_per_representation',1),('edges_per_representation',1)]:
        bad=copy.deepcopy(result);bad[key]=value;reject(validate_result,bad,'result/'+key)
    for kind in ('erase-trace','erase-obligation','rewrite-history','promote-support','promote-freeze'):
        bad=copy.deepcopy(doc('coverage.json'))
        if kind=='erase-trace': bad['slice_traces'].pop()
        elif kind=='erase-obligation': bad['slice_obligations'].pop()
        elif kind=='rewrite-history': bad['predecessor_coverage']['formal_freeze']=True
        elif kind=='promote-support': bad['slice_traces'][0]['status']='complete'
        else: bad['formal_freeze']=True
        reject(validate_coverage,bad,'coverage/'+kind)
    reject(candidate_check,'0'*40,'wrong-candidate')
    return labels

def evidence():
    import q_artifact as codec
    e=doc('evidence.json'); actual=codec.unpack(doc('results.json')); validate_result(actual)
    require(e['formal_freeze'] is False and e['semantic_sha256']==sha(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()),'evidence semantic identity')
    directories={p.name for p in (runner.cache()/'discovery').iterdir() if p.is_dir()}
    require({r['id'] for r in e['retained_runs']}==directories and len(e['retained_runs'])==len(directories),'retain all attempts')
    for row in e['retained_runs']:
        path=runner.cache()/'discovery'/row['id']
        require(row['files']=={p.relative_to(path).as_posix():sha(p.read_bytes()) for p in path.rglob('*') if p.is_file()},'full attempt hash closure')
        if (path/'admission.json').exists(): verify_run(path,row['id']==e['accepted_run'])
        require(bool(row['disposition']),'truthful attempt disposition')
    accepted=runner.cache()/'discovery'/e['accepted_run']; raw=codec.unpack(read(accepted/'result.json')['result'])
    require(raw==actual,'accepted retained results')
    for row in e['containment_checks']:
        path=runner.cache()/'containment'/row['id']
        require(row['files']=={p.relative_to(path).as_posix():sha(p.read_bytes()) for p in path.rglob('*') if p.is_file()},'containment evidence closure')
        if row['accepted']:
            result=read(path/'result.json');require(result['status']=='CONTAINMENT_PASS' and len(result['cases'])==3,'executed containment controls')
            require(result['source_sha256']==sha((ROOT/CODE/'run_packet.py').read_bytes()),'current contained wrapper tested')
    require(sum(r['accepted'] for r in e['containment_checks'])==1,'one accepted containment control run')
    validate_coverage(doc('coverage.json'))
    return actual

def command(args,root,out,label,deadline):
    runner.scope(expensive=False,final=True)
    remain=(deadline-runner.now()).total_seconds(); require(remain>0,'hard deadline')
    started=time.monotonic(); status='finished';job=runner.OwnedJob();process=None
    try:
        process=job.launch(args,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        try:
            raw=process.communicate(timeout=min(600,remain))[0];code=process.returncode
            if not job.wait_idle(min(5,max(0,(deadline-runner.now()).total_seconds()))): job.stop();status='unexpected-owned-descendant';code=None
        except subprocess.TimeoutExpired:
            job.stop();raw=process.communicate(timeout=5)[0];code=None;status='timeout-owned-job-terminated-and-waited'
    finally:
        job.close()
    (out/(label+'.log')).write_bytes(raw)
    row={'command':args,'root':str(root),'seconds':time.monotonic()-started,'exit_code':code,'status':status,'log':label+'.log','sha256':sha(raw)}
    runner.write(out/(label+'-execution.json'),row); print(json.dumps(row),flush=True)
    require(code==0,'gate command failure '+label); return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--preflight',action='store_true');p.add_argument('--working',action='store_true');p.add_argument('--candidate');args=p.parse_args()
    preflight()
    if args.preflight: print('CUT_SOURCE_PREFLIGHT_PASS_NOT_FINAL'); return
    candidate=args.candidate or git('rev-parse','HEAD'); paths=candidate_check(candidate)
    actual=evidence(); labels=adversarial(actual); inv=doc('validation-inventory.json')
    previous=read(ROOT/'docs/v3/construction/cut-publication-20260908/validation-inventory.json')
    require(inv['frozen_gates']==[{'commit':PREVIOUS,'branch':'codex/v3-cut-publication-20260908','script':'experiments/v3/cut-publication/check.py'}]+previous['frozen_gates'] and len(inv['frozen_gates'])==16,'sixteen unchanged predecessors')
    require(inv['regression_commands']==previous['regression_commands'] and len(inv['regression_commands'])==25,'unchanged25 regressions')
    require(set(inv['artifacts'])==set(paths)-{PREFIX+'validation-inventory.json'},'candidate artifact closure')
    for path,digest in inv['artifacts'].items(): require(sha(runner.git('show',candidate+':'+path))==digest,'candidate artifact hash')
    import s_experiment as model
    if args.working:
        fresh=model.run('all'); require(fresh==actual,'complete semantic reproduction'); print('CUT_SOURCE_WORKING_PASS_NOT_FINAL'); return
    runner.scope(final=True); out=runner.cache()/candidate; out.mkdir(exist_ok=True)
    runid=runner.now().strftime('%Y%m%dT%H%M%S%f'); directory=out/runid
    controls=out/(runid+'-containment');runner.containment_check(controls)
    a,x=runner.execute(directory,'all',final=True); verify_run(directory,True)
    import q_artifact as codec
    require(codec.unpack(read(directory/'result.json')['result'])==actual,'fresh exact final reproduction')
    historical=runpy.run_path(str(ROOT/'experiments/v3/formal-comparison/check.py'))
    deadline=dt.datetime.fromisoformat(doc('goal.json')['deadline_utc']); frozen=[]; regressions=[]
    for row in inv['frozen_gates']:
        root=historical['frozen_root'](row['commit'],row['branch'])
        frozen.append(command([sys.executable,'-X','utf8','-B',row['script'],'--working'],root,out,runid+'-frozen-'+row['commit'][:7],deadline))
        require(historical['git']('rev-parse','HEAD',root=root)==row['commit'] and not historical['git']('status','--porcelain',root=root),'frozen source unchanged')
    for i,cmd in enumerate(inv['regression_commands']): regressions.append(command([sys.executable,*cmd[1:]],ROOT,out,runid+'-regression-'+str(i),deadline))
    candidate_check(candidate); require(runner.now()<=deadline,'final deadline')
    receipt={'status':'CUT_SOURCE_GATE_PASS','candidate':candidate,'run_id':runid,'semantic_sha256':doc('evidence.json')['semantic_sha256'],
             'frozen_validations':frozen,'regressions':regressions,'adversarial_checks':labels,'execution_directory':str(directory),
             'execution_files':{p.relative_to(directory).as_posix():sha(p.read_bytes()) for p in directory.rglob('*') if p.is_file()},'formal_freeze':False}
    receipt['containment_directory']=str(controls);receipt['containment_files']={p.relative_to(controls).as_posix():sha(p.read_bytes()) for p in controls.rglob('*') if p.is_file()}
    runner.write(out/(runid+'.json'),receipt); print('CUT_SOURCE_GATE_PASS '+candidate,flush=True)

if __name__=='__main__':
    import os
    final='--candidate' in sys.argv and '--working' not in sys.argv and '--preflight' not in sys.argv
    lock=runner.cache()/'heavy-gate.lock'
    if final:
        fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,str(os.getpid()).encode());os.close(fd)
    try: main()
    finally:
        if final: lock.unlink()
