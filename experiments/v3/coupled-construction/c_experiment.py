"""Complete finite exploration with independent relation and retained crossing witnesses."""
import argparse,collections,copy,datetime,hashlib,json,pathlib,sys,time,ctypes
import c_domain as d,c_inclusive as inc,c_split as split,c_audit as audit
MAX_STATES=500000;MAX_SECONDS=600;MAX_MEMORY=2147483648
MUTANTS={
 'receipt-binding':'foreign-receipt','serialization':'pool-contention','identity':'owner-payload','foreign-release':'owner-payload','resend':'quota-restart-lifetime','classify-release':'refusal-reconciliation','success-refund':'success-consumption','settle-twice':'refusal-reconciliation','conflict':'classification-conflict',
 'snapshot-ledger':'old-snapshot-uncertainty','restart-release':'quota-restart-lifetime','replay-release':'quota-restart-lifetime','quota-release':'quota-restart-lifetime','stop-release':'stop-saturated','adopt-lease':'transported-stale-advice','wake-lease':'historical-adoption','duplicate-wake':'ack-before-ingestion','catalog-binding':'wrong-record-binding','hidden-wait':'old-snapshot-uncertainty','hold-executor':'old-snapshot-uncertainty','shared-control':'stop-saturated','alias-retirement':'alias-reuse','cancel-all':'stop-saturated','reset-credit':'reset-needs-fresh-credit','erase-future':'reset-future-reply','install-guard':'installation-before-event','lost-ack-release':'lost-ack-pending'}
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
 s=w['final'];events=w['events'];dec=lambda k:[e for e in events if e['action'].split('@')[0]==k]
 if name in ('transported-stale-advice','historical-adoption'):
  d.require(s['reserved'][0]==6 and s['evidence'] and s['wakes']==0,'nonvacuous transported stale authority witness')
  d.require(s['adoptions']==(1 if name=='historical-adoption' else 0),'historical versus stale adoption')
 if name in ('refusal-reconciliation','success-consumption'):
  d.require(s['reserved'][0]==0 and s['consumed'][0]==(6 if outcome==1 else 0),'terminal reconciliation positive')
  d.require(s['reserved'][1]==(0 if outcome==1 else 6),'actual B admission depends on nonexecution')
 if name=='old-snapshot-uncertainty':d.require(s['installed'] and s['installed'][2]==10 and s['free']==4 and s['reserved']==(6,0),'old presentation does not change actual pool')
 if name=='alias-reuse':d.require(s['request'][4][4]==2 and s['stopped'] and s['missing'] and not s['evidence'],'transported alias reuse witness')
 if name=='stop-saturated':d.require(s['control']==2 and s['reserved']==(6,0) and s['unrelated']=='completed-local','saturated scoped Stop')
 if name=='reset-future-reply':d.require(s['evidence'] and s['adoptions']==1 and s['wire_sent']==3,'future reply survives reset and pipeline')
 if name=='ack-before-ingestion':d.require(s['wakes']==1 and s['adoptions']==1 and s['sent']==1,'ACK and duplicate ingestion idempotence')
 if name=='wrong-record-binding':d.require(not s['evidence'] and any(e['after']['decision']=='ingest:binding-conflict' for e in events),'actual record mismatch rejection')
 if name=='framing-stop':d.require(s['quarantine'] and s['control']==2 and s['reserved'][0]==6,'framing quarantine/control separation')
 if name=='refusal-reconciliation':d.require(s['offered']==4 and s['wire_sent']==4,'all four mixed-byte notifications actually delivered')
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
 if m=='alias-retirement':return k=='ingest' and s['stopped'] and bool(n['evidence'])
 if m=='hold-executor':return k=='start' and s['executor']=='head' and not n['started']
 if m=='reset-credit':return k=='emit' and n['wire_sent']>s['wire_sent'] and d.evaluate(n['wire'])['status']=='refused'
 if m=='adopt-lease':return n['adoptions']>s['adoptions'] and not audit.authoritative(s,s['evidence'])
 if m=='wake-lease':return n['wakes']>s['wakes'] and not audit.authoritative(s,s['adopted'])
 if m=='identity':return k in ('wrong-owner','wrong-payload') and n['decision'].endswith('duplicate')
 if m=='hidden-wait':return k=='wait-held' and n['decision'].endswith('blocked-dependency') and not n['wait']
 if m=='shared-control':return k=='stop-request' and n['control']==0
 if m=='install-guard':return k=='emit' and n['wire_sent']>s['wire_sent'] and not s['installed_cursor']
 if m=='lost-ack-release':return k=='lose-ack' and bool(s['pending']) and not n['pending']
 if m=='success-refund':return k=='reconcile' and s['classification']==1 and n['free']>s['free']
 if m=='conflict':return k=='reconcile' and s['conflict'] and n['reserved'][0]<s['reserved'][0]
 try:audit.invariant(n)
 except ValueError:return True
 return n['reserved'][0]<s['reserved'][0] and k!='reconcile'

def mutant(m,u='event',outcome=2):
 name=MUTANTS[m];p=d.PROFILES[name];s=d.initial(u);events=[];first=None
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
 return dict(flow_constants={k:getattr(d,k) for k in ('COSTS','EVENTS','GRANTS','QUEUE_EVENTS','QUEUE_BYTES','CHANNEL','INFLIGHT','RETAINED','FRAME')},finite_tokens=[base64.b64encode(x).decode() for x in d.TOKENS],decoder=rows)

import base64
def run():
 profiles={}
 for name in d.PROFILES:
  for u in d.UNITS:
   for outcome in d.OUTCOMES:
    key=name+'/'+u+'/'+str(outcome);profiles[key]=explore(name,u,outcome);print(key,profiles[key]['states'],profiles[key]['edges'],flush=True)
 states=sum(r['states'] for r in profiles.values());d.require(states<=MAX_STATES,'total admitted states bound')
 return dict(status='coupled-construction-pass',classification='modeled',profiles=profiles,states_per_boundary=states,edges_per_boundary=sum(r['edges'] for r in profiles.values()),mutants=[mutant(m,u) for m in MUTANTS for u in d.UNITS],calibrations=calibrate(),controls=controls(),formal_freeze=False,full_comparison_complete=False,runtime_integration_support=False,live_provider_calls=0,new_owner_questions=[])
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=pathlib.Path,required=True);a=parser.parse_args();begin=datetime.datetime.now(datetime.timezone.utc);result=run();end=datetime.datetime.now(datetime.timezone.utc)
 a.output.write_text(json.dumps({'started_at':begin.isoformat(),'finished_at':end.isoformat(),'seconds':time.perf_counter()-START,'peak_bytes':peak(),'result':result},indent=2)+'\n',encoding='utf-8');print('COUPLED_CONSTRUCTION_EXPERIMENT_PASS')
