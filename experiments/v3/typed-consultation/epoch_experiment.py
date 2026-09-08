"""Complete finite typed consultation comparisons and immutable M1A controls."""
import argparse,collections,copy,ctypes,datetime,hashlib,json,pathlib,runpy,time
import epoch_domain as d,epoch_inclusive as inc,epoch_split as sp,epoch_audit as audit
ROOT=pathlib.Path(__file__).resolve().parents[3]
MUTANTS={'omit-lease':'stale-lease','omit-goal':'stale-goal','omit-issuer':'stale-issuer','omit-incarnation':'stale-incarnation','serial-only':'wrong-domain','omit-delivery':'alias-before-receipt','erase-evidence':'alias-after-receipt','duplicate-adopt':'duplicates','duplicate-wake':'duplicates','payload-conflict':'duplicates','invisible-wait':'resource-wait','hold-executor':'resource-wait','cancel-all':'stop-borrowed','stop-generation':'stop-borrowed','false-settlement':'stop-borrowed','release-reservation':'stop-borrowed','advice-amend':'owner-only','restore-incarnation':'stale-incarnation'}
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n',encoding='utf-8')
def peak_bytes():
    class Counters(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ('peak','working','pp','p','np','n','page','peakpage')]
    c=Counters();c.cb=ctypes.sizeof(c)
    if not ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(-1),ctypes.byref(c),c.cb):raise OSError('cannot measure process memory')
    return c.peak



def witness(name):
 s=d.initial();rows=[]
 for action in d.PROFILES[name]:
  n=inc.step(s,action);audit.check(s,action,n,name);d.require(n==d.flat(sp.step(d.split(s),action)),'witness comparator')
  rows.append({'action':action,'before':s,'after':n});s=n
 return {'events':rows,'final':s}

def witness_check(name,w):
 s=w['final'];events={x['action']:x for x in w['events']}
 if name=='resource-wait':
  d.require(events['wait-held']['after']['wait_graph']==(('head','consultation-a'),('consultation-a','executor-e'),('executor-e','head')) and events['wait-held']['after']['decision'].endswith('blocked-dependency'),'actual resource wait cycle')
  d.require(events['suspend']['after']['executor']=='free' and events['start']['after']['started'] and s['wake_count']==1,'release permits progress')
 elif name in ('stale-lease','stale-goal','stale-issuer','stale-incarnation','wrong-domain'):
  d.require(s['evidence'] is not None and s['adopted'] is None and s['wake_count']==0 and events['adopt']['after']['decision'].endswith('stale-or-missing-authority'),'stale advice retained and fenced')
 elif name=='alias-before-receipt':d.require(s['missing'] and s['evidence'] is None and s['wake_count']==0,'expired delivery stays missing')
 elif name=='alias-after-receipt':d.require(s['evidence'] is not None and not s['missing'] and s['adopted'] is None,'received evidence survives expiry')
 elif name in ('stop-borrowed','stop-inflight'):
  d.require(events['stop']['before']['unrelated']=='active' and s['unrelated']=='completed' and s['stopped'] and s['cancel_delivered'] and s['remote_outcome']=='unknown' and s['reserved']==6 and s['wake_count']==0,'scoped Stop with unrelated work and uncertainty')
  d.require((s['evidence'] is not None) if name=='stop-borrowed' else s['missing'],'receipt/expiry order')
 elif name in ('historical-adoption','three-leases'):d.require(s['adopted'] is not None and s['adoption_count']==1 and s['wake_count']==0,'historical adoption retained without authority')
 elif name=='duplicates':d.require(s['adoption_count']==s['wake_count']==1 and events['conflict-request']['after']['decision'].endswith('payload-conflict') and events['conflict-request']['after']['input_request']!=s['request'],'actual payload conflict and dedup')
 elif name=='owner-only':d.require(events['advice-amend']['before']['goal_record']==events['advice-amend']['after']['goal_record'] and s['goal_record'][1]==2,'Owner-only amendment')
 elif name=='free-core':pass
 else:raise ValueError('missing witness obligation')

def explore(name,limit=500000,seconds=600,mutant=None,calibration=None):
 initial=d.initial()
 if calibration=='initial':initial['reserved']=0
 if calibration=='initial-wait':initial['wait']='hidden'
 audit.initialization(initial);seen={d.canonical(initial)};todo=collections.deque([(initial,())]);edges=0;graph=hashlib.sha256();start=time.monotonic();terminals=0
 while todo:
  s,trace=todo.popleft();actions=d.environment(s,name)
  if calibration=='missing-edge' and actions:actions=actions[1:]
  d.require(actions==audit.enabled(s,name),'complete enabledness')
  if not actions:terminals+=1
  for a in actions:
   n=inc.step(s,a,mutant)
   if calibration=='no-op':n=s
   try:audit.check(s,a,n,name)
   except ValueError as e:
    if mutant:return {'guard':mutant,'profile':name,'schedule':trace+(a,),'before':s,'after':n,'failure':str(e)}
    raise
   b=d.flat(sp.step(d.split(s),a));audit.check(s,a,b,name);d.require(n==b,'independent representation edge equality')
   edges+=1;graph.update(d.canonical([s,a,n]).encode());graph.update(b'\n');key=d.canonical(n)
   if key not in seen:seen.add(key);todo.append((n,trace+(a,)))
  d.require(len(seen)<=limit and time.monotonic()-start<=seconds,'incomplete resource bound')
  if calibration=='truncated':d.require(not todo,'incomplete frontier')
 if mutant:raise ValueError('vacuous mutant '+mutant)
 d.require(terminals>0,'nonvacuous terminal states');w=witness(name);witness_check(name,w)
 return {'states':len(seen),'edges':edges,'terminal_states':terminals,'frontier':0,'exact_graph_equal':True,'graph_sha256':graph.hexdigest(),'witness':w,'one_shot_environment':d.PROFILES[name]}

def calibrate():
 out=[]
 for k in ('initial','initial-wait','missing-edge','no-op','truncated'):
  try:explore('resource-wait',calibration=k)
  except ValueError as e:out.append({'calibration':k,'failure':str(e)})
  else:raise ValueError('checker accepted '+k)
 return out

def controls():
 rows=[]
 # Every ordered cross-domain collision retains serial1. Data comparisons are
 # checked independently; full workflow substitution is also checked below.
 for wanted in d.TAGS:
  for supplied in d.TAGS:
   a,b=d.token(wanted),d.token(supplied);actual=inc.equal(a,b,None);d.require(actual==(wanted==supplied),'typed numeric collision')
   rows.append({'consumer_domain':wanted,'input_domain':supplied,'serial':1,'accepted':actual})
 s=d.initial()
 for a in d.PREFIX+('ingest',):s=inc.step(s,a)
 substitutions={}
 for label,index,value in [('domain',0,'writer'),('scope',1,'goal-b'),('issuer',2,'kernel-b'),('consumer',3,'other-head'),('identity',5,'lease-other'),('boolean-serial',4,True)]:
  b=list(s['evidence']);t=list(b[2]);t[index]=value;b[2]=tuple(t);b=tuple(b)
  decisions=(inc.current(s,b),sp.authorized(d.split(s).authority,b),audit.eligible(s,b));d.require(decisions==(False,False,False),'full typed substitution '+label)
  substitutions[label]={'input_binding':b,'admitted_by_inclusive_split_audit':decisions}
 helper=runpy.run_path(str(ROOT/'scripts/tests/v3/planning/conformance.test.py'))['_execute_case'];literal={}
 for number in ('006','019','020'):
  path=ROOT/('scripts/tests/v3/planning/fixtures/F-M1A-'+number+'.json');bundle=json.loads(path.read_text());cases=[]
  for case in bundle['cases']:
   counts=helper(case);cases.append({'case_id':case['case_id'],'commands_events_decodes':counts,'actual_expected_errors':[r['primary_error'] for r in case['expected_receipts']]})
  literal['F-M1A-'+number]={'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cases':cases,'status':'literal-frozen-conformance-pass'}
 return {'token_matrix':rows,'workflow_substitutions':substitutions,'literal_m1a':literal,'consultation_literal_m1a_support':False}

def run(directory,limits):
 profiles={};start=time.monotonic()
 for name in d.PROFILES:
  profiles[name]=explore(name,limits['states_per_boundary'],limits['seconds_per_experiment']);print(name,profiles[name]['states'],flush=True)
  d.require(sum(x['states'] for x in profiles.values())<=limits['states_per_boundary'] and time.monotonic()-start<=limits['seconds_per_experiment'] and peak_bytes()<=limits['memory_bytes'],'admitted aggregate resources');write(directory/'progress.json',profiles)
 return {'status':'typed-consultation-pass','classification':'modeled','profiles':profiles,'states_per_boundary':sum(x['states'] for x in profiles.values()),'mutants':[explore(name,mutant=m) for m,name in MUTANTS.items()],'calibrations':calibrate(),'controls':controls(),'formal_freeze':False,'full_comparison_complete':False,'runtime_integration_support':False,'live_provider_calls':0,'new_owner_questions':[]}
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=pathlib.Path);a=parser.parse_args()
    if a.output.exists():raise ValueError('fresh output required')
    limits=json.loads((ROOT/'docs/v3/construction/typed-consultation-20260908/plan.json').read_text())['limits']
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();code=0
    try:result=run(a.output.parent,limits)
    except Exception as e:result={'status':'incomplete-or-checker-failure','detail':type(e).__name__+': '+str(e),'formal_freeze':False};code=1
    write(a.output,{'started_at':start,'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-t,'peak_bytes':peak_bytes(),'result':result})
    print(json.dumps({'status':result['status'],'detail':result.get('detail'),'seconds':time.monotonic()-t}),flush=True);return code
if __name__=='__main__':raise SystemExit(main())
