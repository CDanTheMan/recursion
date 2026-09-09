"""Complete finite exploration with independent relation and retained crossing witnesses."""
import argparse,collections,copy,datetime,hashlib,json,pathlib,sys,time,ctypes
import q_domain as d,q_inclusive as inc,q_split as split,q_audit as audit
import q_artifact as artifact
import p_experiment as predecessor,p_literal as lit
MAX_STATES=500000;MAX_SECONDS=600;MAX_MEMORY=2147483648
MUTANTS={'publication-scope':'same-head-foreign','source-scope':'foreign-source-scope','publication-signature':'invalid-signature','publisher-owner':'invalid-owner','publisher-domain':'invalid-domain','publisher-boot':'old-boot-permit','publisher-serial':'same-boot-revocation','publication-parent':'competing-parent','publication-content':'invalid-content','publication-inventory':'invalid-inventory','source-generation':'source-generation-staged','source-head':'stale-source-staged','source-prefix':'same-version-source-fork','publication-pause':'pause-fresh-publication','receipt-durability':'commit-lost-reply-restart','duplicate-body':'same-request-different-cut','duplicate-caller':'duplicate-foreign-caller','duplicate-reselect':'duplicate-after-retirement','fresh-pin-current':'existing-reader-new-selection','old-reader-rights':'existing-reader-new-selection','reader-release-owner':'foreign-reader-release','reader-wait':'reclaim-live-reader','reclaim-pinned':'reclaim-live-reader','reclaim-current':'reclaim-current-selection','global-pin-count':'current-pin-not-old-pin','copy-binding':'corrupt-copy-install','settle-current':'equal-version-stale-install','install-allowance':'installation-no-allowance'}
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
 s=w['final'];events=w['events'];decisions=[x['after']['decision'] for x in events]
 def saw(value):return any(x.endswith(':'+value) for x in decisions)
 if name in ('current-success','current-failure'):
  d.require(s['reserved'][0]==0 and s['consumed'][0]==(6 if outcome==1 else 0) and s['reserved'][1]==(0 if outcome==1 else 6),'current exact cut reaches independent settlement')
 if name=='commit-lost-reply-restart':d.require(s['publication_revision']==1 and len(s['publication_receipts'])==1 and s['publication_reads']==2 and s['publication_reply']==s['publication_receipts'][0][1] and s['reserved']==(6,0),'lost reply exact duplicate after boot')
 if name=='duplicate-after-retirement':d.require(s['publication_revision']==2 and s['selected'].cut=='later-start-only' and len(s['publication_store'])==1 and s['retired_cuts'] and s['publication_reads']==2 and s['publication_reply']==s['publication_receipts'][0][1],'old immutable receipt does not restore retired source or selection')
 if name=='same-boot-revocation':d.require(saw('stale-permit') and s['publication_revision']==1,'revoked staged request rejects and replacement progresses')
 if name=='old-boot-permit':d.require(saw('stale-boot') and s['publication_revision']==0,'old boot cannot publish')
 if name.startswith('invalid-'):d.require(s['publication_revision']==0 and s['reserved'][0]==6,'invalid source/owner content cannot publish')
 if name=='same-request-different-cut':d.require(saw('E-IDEMPOTENCY-CONFLICT') and s['publication_reads']==0 and s['publication_revision']==1,'same records do not imply same cut identity')
 if name=='duplicate-foreign-caller':d.require(saw('wrong-caller') and s['publication_reads']==0,'duplicate caller still authenticated')
 if name=='competing-parent':d.require(saw('stale-parent') and s['publication_revision']==1,'competing parent compare-and-commit')
 if name=='pause-fresh-publication':d.require(saw('E-PAUSED') and s['publication_revision']==0,'fresh publication pause boundary')
 if name=='pause-duplicate-awareness':d.require(s['publication_revision']==1 and s['publication_reads']==1 and s['reserved']==(6,0),'duplicate awareness under pause')
 if name.startswith('same-head-foreign'):d.require(saw('foreign-publication') and s['publication_revision']==1 and s['selected'].cut=='success' and s['consumed'][0]==6 and s['free']==4,'same original head cannot substitute foreign reservation or attempt; valid selected source still settles')
 if name=='foreign-source-scope':d.require(saw('foreign-source') and not s['source_name'] and s['publication_revision']==0 and s['reserved']==(6,0),'foreign source cannot initialize effectA authority')
 if name=='stale-source-staged':d.require(saw('stale-source-head') and s['publication_revision']==0,'old exact candidate after source append')
 if name=='source-generation-staged':d.require(saw('stale-source-generation') and s['publication_revision']==0,'source incarnation distinct from head')
 if name=='same-version-source-fork':d.require(saw('source-fork') and s['source_name']=='later-start-only','equal version source fork rejects')
 if name in ('equal-version-real-append','equal-version-stale-install','latest-head-same-content-family'):d.require(s['publication_revision']==2 and s['reserved']==(6,0),'latest exact source/current publication blocks stale settlement')
 if name=='existing-reader-new-selection':d.require(saw('stale-selection') and s['retired_cuts'] and s['installed_cut'][0].cut=='success' and s['reserved']==(6,0),'old reader right survives boot, fresh old pin refuses, copied old install cannot settle')
 if name=='reclaim-live-reader':d.require(saw('reader-pinned') and saw('reader-live') and s['retired_cuts'] and s['reserved']==(6,0),'copy does not imply wait; wait/release permits reclaim')
 if name=='current-pin-not-old-pin':d.require(s['reader_pins'][1] and s['retired_cuts'] and s['reader_pins'][1][1]==s['selected'],'generation-specific reader ownership')
 if name=='reader-restart-copied':d.require(s['reader_nonce'][0]==2 and s['retired_cuts'] and s['installed_cut'] and s['reserved']==(6,0),'copied exact binding across reader restart')
 if name=='reader-restart-live':d.require(saw('no-owned-pin') and s['reader_pins'][0] and not s['retired_cuts'],'old reader pin not stolen by new incarnation')
 if name=='foreign-reader-release':d.require(s['reader_pins'][0] and not s['retired_cuts'],'foreign release cannot reclaim live reader bytes')
 if name=='corrupt-copy-install':d.require(saw('copy-mismatch') and not s['installed_cut'] and s['reserved']==(6,0),'actual altered copied bytes refuse')
 if name=='historical-copy-pause':d.require(s['paused'] and s['classified_cut']=='success' and s['runtime_observations']==0 and s['reserved']==(6,0),'historical inspection under pause grants no write')
 if name=='late-receipt-current':d.require(s['publication_revision']==2 and s['consumed'][0]==6 and s['reserved']==(0,0),'exact compatible late receipt progresses')
 if name=='installation-no-allowance':d.require(s['reserved']==(6,0) and s['free']==4,'classification/install/replay/restart never manufacture allowance')
 if name=='four-event-publication':
  import c_experiment
  c_experiment.positive('four-literal-events',w,outcome);d.require(s['publication_revision']==1 and s['installed_cut'],'four actual events with publication/reader/settlement coupling')
 if name=='transported-publication':d.require(s['phase']==3 and s['paused'] and s['classified_cut'] and s['runtime_observations']==0 and s['reserved']==(6,0),'actual RESET/flow/typed consultation plus historical PAUSE publication')
 if name=='typed-advice-publication':d.require(s['evidence'] and s['adoptions']==0 and s['wakes']==0 and s['publication_revision']==1,'stale delivered advice remains separate from system publication')
 if name=='reclaim-current-selection':d.require(saw('no-retired-generation') and len(s['publication_store'])==1,'selected generation cannot retire')
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
 if m=='publication-scope':return k=='pub-commit' and n['publication_revision']>s['publication_revision'] and n['selected'].cut=='foreign'
 if m in ('publication-signature','publisher-owner','publisher-domain','publisher-boot','publisher-serial','publication-parent','publication-content','publication-inventory','source-generation','source-head','publication-pause'):return k=='pub-commit' and n['publication_revision']>s['publication_revision']
 if m=='source-scope':return k=='source-attest' and bool(n['source_head'])
 if m=='source-prefix':return k.startswith('source:') and n['source_head']!=s['source_head']
 if m=='receipt-durability':return k=='pub-commit' and n['publication_revision']>len(n['publication_receipts'])
 if m in ('duplicate-body','duplicate-caller'):return k in ('pub-retry-conflict','pub-retry-foreign') and n['publication_reads']>s['publication_reads']
 if m=='duplicate-reselect':return k=='pub-retry' and n['publication_revision']>s['publication_revision']
 if m=='fresh-pin-current':return k=='reader-pin:1' and bool(n['reader_pins'][1]) and n['reader_pins'][1][1]!=s['selected']
 if m=='old-reader-rights':return k=='authority-restart' and any(s['reader_pins']) and not any(n['reader_pins'])
 if m in ('reader-release-owner','reader-wait'):return k in ('reader-release:0','reader-release-foreign:0') and bool(s['reader_pins'][0]) and not n['reader_pins'][0] and (not s['reader_waited'][0] or k=='reader-release-foreign:0')
 if m in ('reclaim-pinned','reclaim-current'):return k=='reclaim' and len(n['publication_store'])<len(s['publication_store'])
 if m=='global-pin-count':return k=='reclaim' and bool(s['reader_pins'][1]) and not s['reader_pins'][0] and n['publication_store']==s['publication_store']
 if m=='copy-binding':return k=='reader-install-corrupt:0' and bool(n['installed_cut'])
 if m=='settle-current':return k=='reconcile' and n['reserved'][0]<s['reserved'][0]
 if m=='install-allowance':return k=='reader-install:0' and n['reserved'][0]<s['reserved'][0]
 return False


def mutant(m,u='event',outcome=2):
 name=MUTANTS[m];p=d.PROFILES[name];outcome=p.get('outcomes',d.OUTCOMES)[-1] if outcome not in p.get('outcomes',d.OUTCOMES) else outcome;s=d.initial(u);events=[];first=None

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
   s=d.initial('event');p=d.PROFILES['current-success'];a=p['actions'][0]
   if label=='wrong-initial':s['free']=9;audit.initialization(s,'event')
   elif label=='missing-edge':d.require(set()==audit.enabled(s,p),'independent complete enabledness')
   elif label=='no-op':audit.check(s,a,s,p,'event',1)
   elif label=='corrupt-catalogue':s['catalog']=(('boot',(),(),0,1),);audit.invariant(s)
   else:explore('current-success','event',1,limit=1)
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
 pairs=[]
 for left,right,expected in [('success','later-start-only',True),('success','conflict',True),('ambiguous','late-receipt',True),('late-receipt','later-start-only',True),('later-start-only','conflict',False)]:
  a=lit.fixture(left)['original'];b=lit.fixture(right)['original'];actual=b['records'][:len(a['records'])]==a['records'] and a['cut']['trace_header']['intent']==b['cut']['trace_header']['intent'] and a['cut']['trace_header']['admission']==b['cut']['trace_header']['admission'];d.require(actual==expected,'original source prefix control');pairs.append(dict(left=left,right=right,prefix=actual,left_head=d.head(left),right_head=d.head(right)))
 d.require(d.head('success')==d.head('late-receipt') and d.raw_cut('success')!=d.raw_cut('late-receipt'),'same source head, different full cut')
 encoded=artifact.pack({'text':'x'*600,'again':'x'*600});d.require(artifact.unpack(encoded)=={'text':'x'*600,'again':'x'*600},'lossless text object roundtrip')
 codec=[]
 for label in ('wrong-hash','missing-object','extra-object'):
  bad=copy.deepcopy(encoded)
  if label=='wrong-hash':bad['objects'][next(iter(bad['objects']))]='changed'
  elif label=='missing-object':bad['objects']={}
  else:bad['objects'][artifact.sha('extra')]='extra'
  try:artifact.unpack(bad)
  except ValueError as e:codec.append({'control':label,'failure':str(e)})
  else:raise ValueError('artifact corruption accepted')
 return dict(source_prefix_controls=pairs,artifact_controls=codec,literal_cut_controls=lit.controls(),flow_constants={k:getattr(d,k) for k in ('COSTS','EVENTS','GRANTS','QUEUE_EVENTS','QUEUE_BYTES','CHANNEL','INFLIGHT','RETAINED','FRAME')},finite_tokens=[base64.b64encode(x).decode() for x in d.TOKENS],decoder=rows)

import base64
def run():
 profiles={}
 for name in d.PROFILES:
  for u in d.UNITS:
   for outcome in d.PROFILES[name].get('outcomes',d.OUTCOMES):
    key=name+'/'+u+'/'+str(outcome);profiles[key]=explore(name,u,outcome);print(key,profiles[key]['states'],profiles[key]['edges'],flush=True)
 states=sum(r['states'] for r in profiles.values());d.require(states<=MAX_STATES,'total admitted states bound')
 return dict(status='cut-publication-pass',classification='modeled',profiles=profiles,states_per_boundary=states,edges_per_boundary=sum(r['edges'] for r in profiles.values()),mutants=[mutant(m,u) for m in MUTANTS for u in d.UNITS],calibrations=calibrate(),controls=controls(),formal_freeze=False,full_comparison_complete=False,runtime_integration_support=False,live_provider_calls=0,new_owner_questions=[])
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=pathlib.Path,required=True);a=parser.parse_args();begin=datetime.datetime.now(datetime.timezone.utc);result=run();end=datetime.datetime.now(datetime.timezone.utc)
 a.output.write_text(json.dumps({'started_at':begin.isoformat(),'finished_at':end.isoformat(),'seconds':time.perf_counter()-START,'peak_bytes':peak(),'result':artifact.pack(result)},sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8');print('CUT_PUBLICATION_EXPERIMENT_PASS')
