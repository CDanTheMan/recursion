"""Complete finite exploration with independent relation and retained crossing witnesses."""
import argparse,collections,copy,datetime,hashlib,json,pathlib,sys,time,ctypes
import p_domain as d,p_inclusive as inc,p_split as split,p_audit as audit
import c_experiment as predecessor,p_literal as lit
MAX_STATES=500000;MAX_SECONDS=600;MAX_MEMORY=2147483648
MUTANTS=dict(predecessor.MUTANTS)
MUTANTS.update({'join-validation':'cut-missing-original','cut-owner':'cut-foreign','cut-freshness':'stale-classified-cut','cut-hold':'cut-later-start-only','quarantine':'canonical-quarantine','nonexecution':'cut-generic-failure','pause-admission':'pause-before-reserve','pause-permit':'pause-before-permit','pause-observation':'paused-observation','pause-settle':'paused-observation','duplicate-observation':'duplicate-before-pause','classification-write':'paused-observation'})
START=time.perf_counter()
def peak():
 class MEM(ctypes.Structure):_fields_=[('cb',ctypes.c_ulong),('PageFaultCount',ctypes.c_ulong),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
 x=MEM();x.cb=ctypes.sizeof(x);handle=ctypes.windll.kernel32.GetCurrentProcess;handle.restype=ctypes.c_void_p;fn=ctypes.windll.psapi.GetProcessMemoryInfo;fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong];d.require(fn(handle(),ctypes.byref(x),x.cb),'memory measurement');return x.PeakWorkingSetSize

def witness(name,u,outcome,path):
 s=d.initial(u);events=[];p=d.PROFILES[name]
 for a in path:
  n=inc.step(s,a,p,u,outcome);audit.check(s,a,n,p,u,outcome);events.append(dict(action=a,before=s,after=n));s=n
 return dict(events=events,final=s)

def positive(name,w,outcome):
 if name in d.base.PROFILES:return predecessor.positive(name,w,outcome)
 s=w['final'];ev=w['events'];dec=lambda kind:[e for e in ev if e['action'].split('@')[0]==kind]
 if name=='pause-before-reserve':d.require(s['paused'] and s['reserved']==(0,0) and s['sent']==0,'pause before new reservation')
 if name=='pause-before-permit':d.require(s['reserved']==(6,0) and s['sent']==0,'pause between intent and permit')
 if name=='issued-before-pause':d.require(s['sent']==1 and s['remote']==outcome and s['classified_cut'] and s['runtime_observations']==0 and s['reserved']==(6,0),'already-issued exposure and pure retained classification')
 if name in ('cut-success','cut-failure'):
  d.require(s['reserved'][0]==0 and s['consumed'][0]==(6 if outcome==1 else 0) and s['reserved'][1]==(0 if outcome==1 else 6),'complete authentic positive settlement')
 if name in ('cut-later-start-only','cut-later-unresolved','cut-prior-unresolved','cut-conflict','cut-generic-failure','cut-stale-paused','canonical-quarantine','stale-classified-cut'):d.require(s['reserved'][0]==6 and s['reserved'][1]==0,'independent hold keeps shared allowance')
 if name=='cut-later-start-only':d.require(s['cut_status']=='succeeded' and s['cut_hold'],'literal success plus later-start hold')
 if name=='cut-generic-failure':d.require(s['cut_status']=='failed' and not s['nonexecution'],'generic failure is not nonexecution')
 if name in ('cut-'+n for n in audit.NEGATIVE|{'foreign','foreign-attempt'}):d.require(not s['joined_cut'] and s['reserved'][0]==6,'invalid/foreign join cannot settle')
 if name=='paused-observation':d.require(any(e['after']['decision']=='observe:E-PAUSED' for e in ev) and s['runtime_observations']==0 and s['refusal_journal']==1 and s['classified_cut'] and s['reserved'][0]==6,'otherwise-valid paused refusal and pure classification')
 if name=='duplicate-before-pause':d.require(s['runtime_observations']==1 and any(e['after']['decision']=='observe:duplicate' for e in ev) and any(e['after']['decision']=='observe-conflict:E-IDEMPOTENCY-CONFLICT' for e in ev),'duplicate receipt and conflict remain distinct')
 if name=='canonical-quarantine':d.require(s['canonical_quarantine'] and s['cut_status']=='succeeded','literal historical quarantine retained')
 if name=='cut-after-ack-restart':d.require(s['classified_cut'] and s['reserved']==(6,0) and s['paused'],'cut survives transport/restart without authority')
 return True

def explore(name,u,outcome,limit=MAX_STATES):
 p=d.PROFILES[name];initial=d.initial(u);audit.initialization(initial,u);d.require(set(d.AUTH+d.FLOW+d.VIEW)==set(initial),'split complete field ownership')
 q=collections.deque([(initial,())]);seen={d.canonical(initial)};h=hashlib.sha256();edges=0;terminal=0;sample=None;histories={}
 while q:
  s,path=q.popleft();left=set(d.ready_actions(s,p));d.require(left==audit.enabled(s,p),'independent enabledness')
  key=s['wire']
  if key not in histories:
   result=d.evaluate(key);d.require(set(result['reasons'])<={'replay-gap'} and result['status'] in ('accepted','accepted-reset','refused'),'literal M1B prefix reasons')
   # A pending WELCOME gap is explicitly refused until RESET; no permanent error is permitted.
   d.require(result['status']!='refused' or s['phase']==2,'only pending recovery may refuse')
   histories[key]=result
  if not left:
   terminal+=1
   if sample is None:sample=path
  for a in sorted(left):
   n=inc.step(s,a,p,u,outcome);other=d.flatten(split.step(d.split(s),a,p,u,outcome));d.require(n==other,'independent representations differ '+a);audit.check(s,a,n,p,u,outcome)
   h.update(d.canonical((s,a,n)).encode());edges+=1;key=d.canonical(n)
   if key not in seen:
    seen.add(key);q.append((n,path+(a,)))
    if len(seen)>limit:raise ValueError('incomplete frontier: state bound')
  if edges%2048==0:d.require(time.perf_counter()-START<MAX_SECONDS,'incomplete frontier: time bound');d.require(peak()<MAX_MEMORY,'incomplete frontier: memory bound')
 d.require(sample is not None,'terminal finite witness');w=witness(name,u,outcome,sample);positive(name,w,outcome)
 return dict(states=len(seen),edges=edges,terminal_states=terminal,frontier=0,exact_graph_equal=True,graph_sha256=h.hexdigest(),wire_histories=[{'sha256':hashlib.sha256(d.canonical(k).encode()).hexdigest(),'messages':[json.loads(x) for x in k],'decision':v} for k,v in sorted(histories.items())],witness=w)

def hazard(m,s,k,n):
 if m=='join-validation':return k=='join-cut' and bool(n['joined_cut']) and not audit.facts(n['joined_cut'])['accepted']
 if m=='cut-owner':return k=='join-cut' and bool(n['joined_cut']) and audit.facts(n['joined_cut'])['binding']!=s['bindings'][0]
 if m in ('cut-freshness','cut-hold','quarantine','nonexecution','pause-settle'):return k=='reconcile' and n['reserved'][0]<s['reserved'][0]
 if m=='pause-admission':return s['paused'] and n['reserved']!=s['reserved']
 if m=='pause-permit':return s['paused'] and n['sent']>s['sent']
 if m in ('pause-observation','duplicate-observation','classification-write'):return n['runtime_observations']>s['runtime_observations']
 return predecessor.hazard(m,s,k,n)

def mutant(m,u='event',outcome=2):
 name=MUTANTS[m];p=d.PROFILES[name];outcome=p.get('outcomes',d.OUTCOMES)[-1] if outcome not in p.get('outcomes',d.OUTCOMES) else outcome;s=d.initial(u);events=[];first=None
 if m in ('success-refund','conflict'):outcome=1
 for a in p['actions']:
  n=inc.step(s,a,p,u,outcome,m);k=a.split('@')[0];events.append(dict(action=a,before=s,after=n))
  try:audit.check(s,a,n,p,u,outcome)
  except ValueError as e:
   if first is None:first={'action':a,'failure':str(e)}
  if hazard(m,s,k,n):
   d.require(first is not None,'hazard must be independently rejected');return dict(guard=m,profile=name,unit=u,remote_outcome=outcome,first_relation_failure=first,events=events,hazard_action=a,final=n)
  s=n
 raise ValueError('vacuous guard mutation '+m)

def calibrate():
 rows=[]
 for label in ('wrong-initial','missing-edge','no-op','corrupt-catalogue','truncated'):
  try:
   s=d.initial('event');p=d.PROFILES['pool-contention'];a=p['actions'][0]
   if label=='wrong-initial':s['free']=9;audit.initialization(s,'event')
   elif label=='missing-edge':d.require(set()==audit.enabled(s,p),'independent complete enabledness')
   elif label=='no-op':audit.check(s,a,s,p,'event',1)
   elif label=='corrupt-catalogue':s['catalog']=(('boot',(),(),0,1),);audit.invariant(s)
   else:explore('pool-contention','event',1,limit=1)
  except ValueError as e:rows.append({'calibration':label,'failure':str(e)})
  else:raise ValueError('calibration failed '+label)
 return rows

def controls():
 # Literal parser rejection separate from synthetic two-unit framing transitions.
 rows=[]
 for label,raw in [('duplicate-key',b'{"a":1,"a":2}'),('nonfinite',b'{"a":NaN}')]:
  try:d.SCHEMA['strict_loads'](raw)
  except (ValueError,TypeError) as e:rows.append(dict(control=label,rejected=True,error=str(e)))
  else:raise ValueError('decoder accepted '+label)
 return dict(literal_cut_controls=lit.controls(),flow_constants={k:getattr(d,k) for k in ('COSTS','EVENTS','GRANTS','QUEUE_EVENTS','QUEUE_BYTES','CHANNEL','INFLIGHT','RETAINED','FRAME')},finite_tokens=[base64.b64encode(x).decode() for x in d.TOKENS],decoder=rows)

import base64
def run():
 profiles={}
 for name in d.PROFILES:
  for u in d.UNITS:
   for outcome in d.PROFILES[name].get('outcomes',d.OUTCOMES):
    key=name+'/'+u+'/'+str(outcome);profiles[key]=explore(name,u,outcome);print(key,profiles[key]['states'],profiles[key]['edges'],flush=True)
 states=sum(r['states'] for r in profiles.values());d.require(states<=MAX_STATES,'total admitted states bound')
 return dict(status='coupled-cut-pause-pass',classification='modeled',profiles=profiles,states_per_boundary=states,edges_per_boundary=sum(r['edges'] for r in profiles.values()),mutants=[mutant(m,u) for m in MUTANTS for u in d.UNITS],calibrations=calibrate(),controls=controls(),formal_freeze=False,full_comparison_complete=False,runtime_integration_support=False,live_provider_calls=0,new_owner_questions=[])
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=pathlib.Path,required=True);a=parser.parse_args();begin=datetime.datetime.now(datetime.timezone.utc);result=run();end=datetime.datetime.now(datetime.timezone.utc)
 a.output.write_text(json.dumps({'started_at':begin.isoformat(),'finished_at':end.isoformat(),'seconds':time.perf_counter()-START,'peak_bytes':peak(),'result':result},sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8');print('COUPLED_CUT_PAUSE_EXPERIMENT_PASS')
