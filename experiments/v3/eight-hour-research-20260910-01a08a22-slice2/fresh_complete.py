"""Unreduced fresh-complete inventory histories of the unchanged scale profile."""
import argparse,copy,gzip,itertools,json,sys
from pathlib import Path
from baseline import check as c, ROOT, OLD_CODE, OLD_DOC, NEW_CODE, NEW_DOC, added_module_paths
import shared as b
import sharded as old
read,write,typed,decode=b.read,b.write,b.typed,b.decode
require=c.d.require
A2,A3,A4='attempt:2@15','attempt:3@16','attempt:4@17'
O,R='collect-open@11','source-restart@18'
CS=('collect:0@12','collect:1@13','collect:2@14')
CORE=(A2,A3,A4,*CS,O,R)
CONTROLS=old.COMMON+['out-of-subset-order','wrong-global-index','cross-unit-certificate','tuple-loss','altered-non-witness-summary','altered-attestation-census','altered-registry-census','altered-null-or-present-minimum','live-core-generation-not-shadowed','journal-revision-not-erased','cross-case-origin-proof','staged-tuple-became-list','identity-does-not-authorize-selection','refused-attestation-Q-invoked','dropped-refused-event']

def sha(path):return b.sha(Path(path).read_bytes())
def normalize(x):return json.loads(json.dumps(x))
def modules():
    manifest=read(ROOT/'docs/v3/construction/cut-source-overnight-20260908/batch-07/manifest.json');allowed={x['path'] for x in manifest['inputs']}|set(manifest['sources'])|added_module_paths()|{OLD_CODE+'sharded.py',NEW_CODE+'fresh_complete.py'};found=set()
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT) and path.suffix=='.py':found.add(path.relative_to(ROOT).as_posix())
    require(found<=allowed and Path(old.__file__).resolve()==ROOT/OLD_CODE/'sharded.py' and old.c is c,'complete unchanged/additive source closure')
    return sorted(found)

def fresh_complete(schedule):
    p={a:schedule.index(a) for a in CORE}
    successful=[A2]+([A3] if p[A2]<p[A3] else [])+([A4] if p[A2]<p[A3]<p[A4] else [])
    return all(p[a]<p[O] for a in [R,*successful]) and all(p[O]<p[a] for a in CS)

def inventory(profile):
    whole,count=c.inventory(profile);require(count==40320 and len(profile['actions'])==34 and set(profile['actions'][11:19])==set(CORE),'original unchanged scale domain')
    selected=[(i,s) for i,s in enumerate(whole) if fresh_complete(s)];indices=[i for i,s in selected];schedules=tuple(s for i,s in selected)
    # Independent disjoint partial-order construction; no transition results filter membership.
    standard=[left+(O,)+right for left in itertools.permutations((A2,A3,A4,R)) for right in itertools.permutations(CS)]
    exceptional=[left+(O,)+right for left in itertools.permutations((A3,A2,R)) if left.index(A3)<left.index(A2) for right in itertools.permutations((A4,*CS))]
    require(len(standard)==144 and len(exceptional)==72 and not set(standard)&set(exceptional),'independent144+72 disjoint construction')
    expected=tuple(sorted(profile['actions'][:11]+middle+profile['actions'][19:] for middle in standard+exceptional))
    require(schedules==expected and len(schedules)==216,'independent complete fresh-complete selected membership');c.validate_inventory(profile,schedules,216)
    return whole,indices,schedules

def declared(spec_path,output):
    spec=read(spec_path);require(spec_path.resolve()==ROOT/NEW_DOC/'packet-08/spec.json' and spec['id']=='packet-08' and spec['domain']=='scale-eight-action-race','exact preregistered source/spec')
    require(spec['units']==['event','utf8-byte'] and spec['outcomes']==[1] and spec['actions_per_history']==34 and spec['schedules_per_unit_outcome']==216 and spec['environments']==432 and spec['reservation']==spec['exploration_visits']==30240 and spec['required_controls']==CONTROLS,'exact declared finite environments, budget and controls')
    pins={OLD_CODE+'check.py',OLD_CODE+'sharded.py',NEW_CODE+'baseline.py','experiments/v3/cut-source-overnight/s_domain.py','experiments/v3/cut-source-overnight/s_inclusive.py','experiments/v3/cut-source-overnight/batch-06/guard_a.py','experiments/v3/cut-source-overnight/batch-07/identity.py','experiments/v3/cut-source-overnight/batch-07/identity_audit.py'}
    require(set(spec['source_pins'])==pins,'exact source hypothesis set')
    for name,h in spec['source_pins'].items():require(sha(ROOT/name)==h,'actual source hypothesis bytes')
    run=output.resolve().parent;require(output.resolve()==run/'packet-08-output','actual enclosing packet output');ad=read(run/'admission.json')
    require(ad['status']=='ADMITTED_BEFORE_EXECUTION' and 'packet-08' in ad['packets'] and ad['python_executable']==sys.executable and ad['python_sha256']==sha(sys.executable),'actual same candidate owned invocation/interpreter')
    for path in (spec_path,*(ROOT/name for name in modules())):require(ad['sources'][path.resolve().relative_to(ROOT).as_posix()]['working_sha256']==sha(path),'actual committed source/spec snapshot')
    profile=c.domain(spec);whole,indices,schedules=inventory(profile)
    return spec,profile,whole,indices,schedules

def observation(case):
    states=c.t.restore(case['source']);actions=case['source']['actions'];i=next(i for i,a in enumerate(actions) if a.split('@')[0]=='source-attest');source=states[i];row=case['rows'][i];capture=source['collection']
    return dict(attestation_chronological_index=i,attestation_decision=row['source_observation']['decision'],attestation_q_invoked=row['q_invoked'],registry_length=len(source['attempts']),source_revision=source['source_revision'],capture_current=bool(capture and capture[:2]==(source['source_generation'],source['source_revision'])),complete_inventory=bool(capture and source['collected']==tuple(enumerate(c.d.s.records(source['cut_delivery'])))),causal_pairs=len(case['incarnation_pairs']))

def summary(case,name,raw,index):
    row=c.summarize(case);row.update(artifact=name,artifact_sha256=b.sha(raw),global_schedule_index=index,unit=case['unit'],outcome=case['outcome'],observed=observation(case));return normalize(row)

def aggregate(rows):
    result={k:sum(r[k] for r in rows) for k in ('strict_complete','extended_complete','visible_events','matching_responses','matching_journals','identity_poststates')};census={}
    for row in rows:
        unit=census.setdefault(row['unit'],{})
        for field,value in row['observed'].items():
            bins=unit.setdefault(field,{});key=json.dumps(value,sort_keys=True,separators=(',',':'));bins[key]=bins.get(key,0)+1
    result['observed_census_by_unit']=census;best={'strict':None,'extended':None}
    for row in rows:
        for kind in best:
            prefix=row[kind+'_first_gap']
            if prefix is not None and (best[kind] is None or prefix<best[kind]['prefix']):best[kind]=dict(case=row['case'],prefix=prefix,artifact=row['artifact'],prefix_actions=row['schedule'][:prefix],minimality='earliest failing prefix across all432 declared fresh-complete histories')
    result['minimized_prefixes']=best
    result['conditional_guard_prediction_matches']=all(r['observed']['attestation_decision']=='source-attest:incomplete-registry' and r['observed']['attestation_q_invoked'] is False and r['observed']['capture_current'] and r['observed']['complete_inventory'] for r in rows)
    predicted_registry={'2':144,'3':48,'4':24};predicted_revision={'6':144,'7':48,'8':24}
    result['registry_revision_prediction_matches']=all(census[u]['registry_length']==predicted_registry and census[u]['source_revision']==predicted_revision for u in ('event','utf8-byte')) and all(r['observed']['source_revision']==r['observed']['registry_length']+4 for r in rows)
    return result

def mapping(rows,spec,indices,schedules):
    expected=[(i,s,u) for i,s in zip(indices,schedules) for u in spec['units']];require(len(rows)==len(expected)==432,'every declared environment present')
    for ordinal,(row,(index,schedule,unit)) in enumerate(zip(rows,expected)):
        require(row['case']=='packet-08/'+str(index).zfill(6)+'/'+unit+'/1' and row['global_schedule_index']==index and row['unit']==unit and row['outcome']==1 and tuple(row['schedule'])==schedule and row['artifact']==str(ordinal).zfill(6)+'.json.gz','original global case identity and unique local file mapping')

def controls(spec,profile,whole,indices,schedules,rows,output):
    sample=decode((output/rows[0]['artifact']).read_bytes());result=old.replay_controls(profile,schedules,sample);reject=lambda name,fn:old.rejection(result,name,fn)
    outside=next(s for s in whole if not fresh_complete(s));c.validate_inventory(profile,(outside,),1)
    reject('out-of-subset-order',lambda:require(fresh_complete(outside),'declared fresh-complete membership'))
    bad=copy.deepcopy(rows);bad[0]['global_schedule_index']=next(i for i in range(len(whole)) if i not in indices);reject('wrong-global-index',lambda:mapping(bad,spec,indices,schedules))
    bad=copy.deepcopy(rows);bad[0]['unit']=spec['units'][1];reject('cross-unit-certificate',lambda:mapping(bad,spec,indices,schedules))
    bad=copy.deepcopy(sample);bad['source']['actions']=list(bad['source']['actions']);reject('tuple-loss',lambda:c.audit_case(bad))
    bad=copy.deepcopy(rows[-1]);bad['matching_journals']+=1;actual=decode((output/bad['artifact']).read_bytes());raw=(output/bad['artifact']).read_bytes();reject('altered-non-witness-summary',lambda:require(bad==summary(actual,bad['artifact'],raw,bad['global_schedule_index']),'complete actual summary'))
    total=aggregate(rows)
    for label,field in [('altered-attestation-census','attestation_decision'),('altered-registry-census','registry_length')]:
        bad=copy.deepcopy(total);bins=bad['observed_census_by_unit'][spec['units'][0]][field];bins[next(iter(bins))]+=1;reject(label,lambda bad=bad:require(bad==aggregate(rows),'every actual observation census'))
    bad=copy.deepcopy(total);bad['minimized_prefixes']['strict']={'prefix':0};reject('altered-null-or-present-minimum',lambda:require(bad==aggregate(rows),'actual earliest prefix or null'))
    witness=None
    for row in rows:
        case=decode((output/row['artifact']).read_bytes())
        candidates=[i for i,x in enumerate(case['prefixes']) if x['identity_proof'] and x['related']]
        if candidates:witness=(case,candidates[0]);break
    require(witness is not None,'actual accepted staged-object witness for relation discrimination')
    case,prefix=witness;ss=c.t.restore(case['source']);aa=c.t.restore(case['adapter']);pairs=[]
    for i in range(prefix):c.r.advance(pairs,ss[i],c.t.core_view(aa[i]),ss[i+1],c.t.core_view(aa[i+1]),case['source']['actions'][i],case['source']['actions'][i],i,i)
    bad=copy.deepcopy(aa);bad[prefix]['core']['source_generation']=c.d.q.source_token(99)
    reject('live-core-generation-not-shadowed',lambda:require(c.relation.compare(case,ss,bad,prefix,pairs)['related'],'identity must not hide a different live source generation'))
    bad=copy.deepcopy(aa);bad[prefix]['journal']['source_revision']+=1
    reject('journal-revision-not-erased',lambda:require(c.relation.compare(case,ss,bad,prefix,pairs)['related'],'identity must not erase journal disagreement'))
    proof=copy.deepcopy(case['prefixes'][prefix]);proof['identity_proof']['case']='another-history';reject('cross-case-origin-proof',lambda:c.identity_audit.check(proof,case,ss,aa,prefix,pairs))
    bad=copy.deepcopy(aa);bad[prefix]['core']['staged']=list(bad[prefix]['core']['staged']);reject('staged-tuple-became-list',lambda:require(c.relation.compare(case,ss,bad,prefix,pairs)['related'],'only the original typed staged tuple is eligible'))
    require(not pairs,'actual empty authority ledger for staged-only control');bad_s=copy.deepcopy(ss);bad=copy.deepcopy(aa);envelope=bad_s[prefix]['staged'][0];require(type(envelope) is c.d.q.Envelope and c.r.signed(envelope),'actual valid signed unpaired object');bad_s[prefix]['selected']=envelope;bad[prefix]['core']['selected']=copy.deepcopy(envelope)
    reject('identity-does-not-authorize-selection',lambda:require(c.relation.compare(case,bad_s,bad,prefix,pairs)['related'],'identical valid unpaired objects outside staged grant no selected authority'))
    bad=copy.deepcopy(case);i=next(i for i,a in enumerate(bad['source']['actions']) if a.split('@')[0]=='source-attest');require(bad['rows'][i]['q_invoked'] is False,'actual refused attestation witness');bad['rows'][i]['q_invoked']=True;reject('refused-attestation-Q-invoked',lambda:c.audit_case(bad))
    bad=copy.deepcopy(case);bad['source']['events'].pop(i);reject('dropped-refused-event',lambda:c.audit_case(bad))
    require([x['control'] for x in result]==CONTROLS and all(x['detected'] for x in result),'all actual discriminating controls');return result

def explore(spec_path,output,limit):
    spec,profile,whole,indices,schedules=declared(spec_path,output);require(limit==30240,'finite pre-initialization state reservation');before=c.d.digest(c.d.s.PROFILES);counter=c.Counter(limit);rows=[];initial_modules=modules();output.mkdir(parents=True,exist_ok=False)
    for position,(index,schedule) in enumerate(zip(indices,schedules)):
        for unit in spec['units']:
            name='packet-08/'+str(index).zfill(6)+'/'+unit+'/1';case=c.run_history(profile,schedule,unit,1,name,counter);raw=gzip.compress(typed(case),compresslevel=6,mtime=0);filename=str(len(rows)).zfill(6)+'.json.gz'
            with (output/filename).open('xb') as stream:stream.write(raw)
            actual=decode((output/filename).read_bytes());require(c.d.exact(actual,case) and c.d.exact(c.audit_case(actual),actual['prefixes']),'typed actual on-disk replay and every original independent prefix audit');rows.append(summary(actual,filename,raw,index))
        if (position+1)%24==0:print(json.dumps(dict(completed_schedules=position+1,total=216,visits=counter.visits)),flush=True)
    require(counter.visits==30240 and c.d.digest(c.d.s.PROFILES)==before,'complete charge and original profiles unchanged');mapping(rows,spec,indices,schedules);controlrows=controls(spec,profile,whole,indices,schedules,rows,output)
    result=dict(status='COMPLETE_DECLARED_FRESH_COMPLETE_DOMAIN',packet='packet-08',domain=spec['domain'],environments=432,schedules=216,state_visits_per_representation=counter.visits,reservation=limit,cases=rows,controls=controlrows,registered_local_modules=sorted(set(initial_modules)|set(modules())),whole_inventory_sha256=c.d.digest(whole),schedule_inventory_sha256=c.d.digest(schedules),global_indices=indices,domain_profile_sha256=c.d.digest(profile),spec_sha256=sha(spec_path),checker_sha256=sha(__file__),reductions_used=False,complete_original_profile_coverage=False,unrestricted_refinement_proved=False,original_Q_profile_reachability_proved=False,whole_path_composition_proved=False,source_truth_established=False,**aggregate(rows))
    write(output/'result.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('cases','controls','global_indices','registered_local_modules','observed_census_by_unit','minimized_prefixes')}),flush=True)

def audit(spec_path,output):
    spec,profile,whole,indices,schedules=declared(spec_path,output);run=output.resolve().parent;owned=b.bind_owned(run,'packet-08');result=read(output/'result.json');h=sha(output/'result.json');mapping(result['cases'],spec,indices,schedules)
    require(result['status']=='COMPLETE_DECLARED_FRESH_COMPLETE_DOMAIN' and result['packet']=='packet-08' and result['state_visits_per_representation']==result['reservation']==30240 and result['environments']==432 and result['schedules']==216,'complete exact finite generated domain')
    require(result['global_indices']==indices and result['whole_inventory_sha256']==c.d.digest(whole) and result['schedule_inventory_sha256']==c.d.digest(schedules) and result['domain_profile_sha256']==c.d.digest(profile),'independent exact original and selected inventory')
    actual=[];files={}
    for expected in result['cases']:
        target=(output/expected['artifact']).resolve();require(target.is_relative_to(output.resolve()),'contained retained certificate');raw=target.read_bytes();case=decode(raw)
        require(c.d.exact(c.audit_case(case),case['prefixes']) and c.d.exact(case['source']['profile'],profile),'every typed retained certificate and unchanged profile')
        row=summary(case,target.name,raw,expected['global_schedule_index']);require(row==expected,'complete actual retained summary and observations');actual.append(row);files[target.name]=sha(target)
    require({p.name for p in output.iterdir()}=={'result.json'}|set(files),'exact complete generated certificate membership')
    calculated=aggregate(actual);require(all(result[k]==v for k,v in calculated.items()),'all independent complete census, counts, predictions and minima')
    require([x['control'] for x in result['controls']]==CONTROLS and all(x['detected'] is True for x in result['controls']),'all declared controls retained')
    require(result['spec_sha256']==sha(spec_path) and result['checker_sha256']==sha(__file__) and sha(output/'result.json')==h,'unchanged exact spec/checker/result')
    write(output/'audit.json',dict(status='COMPLETE_RETAINED_FRESH_COMPLETE_AUDIT',packet='packet-08',result_sha256=h,certificates=files,environments=432,model_reducers_executed=False,checker_sha256=sha(__file__)))
    write(output/'audit-provenance.json',dict(candidate=read(run/'admission.json')['candidate'],run=str(run),generation_owned_bindings=owned));print('COMPLETE_RETAINED_FRESH_COMPLETE_AUDIT',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--state-limit',type=int);p.add_argument('--audit',action='store_true');a=p.parse_args()
    def deny(event,args):
        if event.startswith(('socket.','subprocess.')) or event in ('os.system','os.posix_spawn'):raise RuntimeError('model network/process operation refused: '+event)
    sys.addaudithook(deny)
    if a.audit:require(a.state_limit is None,'retained audit uses no model reducers');audit(a.spec,a.output)
    else:require(a.state_limit is not None,'finite initialization admission');explore(a.spec,a.output,a.state_limit)
