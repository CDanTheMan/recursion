"""Independent complete initial and transition relation; no model imports."""
import epoch_domain as d

def eligible(s,packet):
 if packet is None or s['request'] is None or packet!=s['request'] or s['stopped'] or not s['alias_active']:return False
 if any(type(v[4]) is not int for v in packet[1:5]):return False
 return packet[1:5]==tuple(s['tokens'][x] for x in ['goal','lease','process','delivery'])

def expected(s,a):
 n={**s,'tokens':dict(s['tokens']),'done':tuple(sorted((*s['done'],a))),'decision':a+':accepted'};t=n['tokens'];changes={};reason=None
 if a=='request':
  if s['stopped']:reason='expired-operation'
  else:
   packet=('operation-a',t['goal'],t['lease'],t['process'],t['delivery'],'context-1','payload-1','head','consultant','grant-a');changes.update(request=packet,input_request=packet,alias_active=True)
 elif a in ['duplicate-request','conflict-request']:
  if s['request'] is None:reason='missing-request'
  else:
   incoming=s['request'] if a=='duplicate-request' else s['request'][:6]+('payload-2',)+s['request'][7:];changes['input_request']=incoming;reason='duplicate' if incoming==s['request'] else 'payload-conflict'
 elif a=='wait-held':
  if s['request'] is None:reason='missing-request'
  elif s['executor']=='head':reason='blocked-dependency';changes.update(wait='blocked-dependency',wait_graph=(('head','consultation-a'),('consultation-a','executor-e'),('executor-e','head')))
  else:changes['wait']='waiting-released'
 elif a=='suspend':
  if s['request'] is None:reason='missing-request'
  else:
   changes.update(wait='suspended',wait_graph=())
   if s['executor']=='head':changes.update(executor='free',executor_binding=None)
 elif a=='start':
  reason='stale-or-missing-authority' if not eligible(s,s['request']) else 'executor-unavailable' if s['executor']!='free' else None
  if reason is None:changes.update(started=True,executor='consultation-a',executor_binding=s['request'][2:4])
 elif a=='reply':
  if not s['started']:reason='not-started'
  else:
   changes['reply']=s['request']
   if s['executor']=='consultation-a':changes.update(executor='free',executor_binding=None)
 elif a in ['ingest','duplicate-reply']:
  if s['reply'] is None:reason='missing-reply'
  elif s['evidence'] is not None:reason='duplicate'
  elif s['alias_active'] and s['reply'][4]==s['tokens']['delivery']:changes['evidence']=s['reply']
  else:reason='expired-delivery-missing';changes['missing']=True
 elif a in ['adopt','adopt-again']:
  if s['adopted'] is not None:reason='duplicate'
  elif not eligible(s,s['evidence']):reason='stale-or-missing-authority'
  else:changes.update(adopted=s['evidence'],adoption_count=1)
 elif a in ['wake','wake-again','relaunch']:
  if not eligible(s,s['adopted']):reason='stale-or-missing-authority'
  elif s['wake_count']!=0:reason='duplicate'
  elif s['executor']!='free':reason='executor-unavailable'
  else:changes.update(wake_count=1,executor='head',executor_binding=s['adopted'][2:4],wait='none',wait_graph=())
 elif a in ['lease2','lease3']:
  serial={'lease2':2,'lease3':3}[a];t['lease']=('lease','goal-a',s['tokens']['lease'][2],'head',serial,'lease-identity-'+str(serial))
 elif a=='issuer':t['lease']=s['tokens']['lease'][:2]+('kernel-b',)+s['tokens']['lease'][3:]
 elif a=='restart':
  t['process']=('process','goal-a','kernel-a','head',2,'process-identity-2')
  if s['executor']=='head':changes.update(executor='free',executor_binding=None,wait='recovered',wait_graph=())
 elif a=='expire':changes['alias_active']=False;t['delivery']=('delivery','operation-a','kernel-a','head',2,'delivery-identity-2')
 elif a=='stop':changes['stopped']=True;changes['alias_active']=False;t['delivery']=('delivery','operation-a','kernel-a','head',2,'delivery-identity-2')
 elif a=='cancel-deliver':
  if s['stopped']:changes['cancel_delivered']=True
  else:reason='not-stopped'
 elif a=='unrelated':
  if s['unrelated']=='active':changes['unrelated']='completed'
  else:reason='not-active'
 elif a=='owner-amend':t['goal']=('goal','goal-a','owner','head',2,'goal-identity-2');changes['goal_record']=('goal-a',2,'goal-digest-2')
 elif a=='advice-amend':reason='owner-authority-required'
 elif a=='wrong-domain':
  if s['reply'] is None:reason='missing-reply'
  else:changes['reply']=s['reply'][:2]+(('writer',)+s['reply'][2][1:],)+s['reply'][3:]
 else:raise ValueError('undeclared transition')
 n.update(changes)
 if reason:n['decision']=a+':'+reason
 return n

def enabled(s,name):
 all_actions=d.PROFILES[name];left=[a for a in all_actions if a not in s['done']]
 return left if name=='free-core' else left[:1]

def invariant(s):
 d.require(set(s['tokens'])==set(d.TAGS),'complete typed namespace')
 for tag,t in s['tokens'].items():
  d.require(len(t)==6 and t[0]==tag and type(t[4]) is int and 1<=t[4]<=(3 if tag=='lease' else 2),'typed current tokens')
 d.require(s['reserved']==6 and s['free']==4 and s['remote_outcome']=='unknown','uncertain effect ownership')
 d.require(s['adoption_count'] in (0,1) and s['wake_count'] in (0,1),'idempotent operation accounting')
 d.require((s['adopted'] is not None)==bool(s['adoption_count']),'historical adoption retained')
 d.require(not s['stopped'] or not s['alias_active'],'stopped operation alias retired')
 d.require(s['unrelated'] in ('active','completed'),'borrowed operation scope')
 d.require(s['wait']!='suspended' or s['executor']!='head','suspended wait must release serial executor')
 d.require((s['executor']=='free')==(s['executor_binding'] is None),'executor ownership binding')
 d.require(s['goal_record'][1]==s['tokens']['goal'][4],'immutable goal version binding')

def initialization(s):
 expected={'tokens':{tag:(tag,'operation-a' if tag=='delivery' else 'goal-a','owner' if tag=='goal' else 'kernel-a','head',1,tag+'-identity-1') for tag in d.TAGS},'goal_record':('goal-a',1,'goal-digest-1'),'request':None,'input_request':None,'reply':None,'evidence':None,'adopted':None,'adoption_count':0,'wake_count':0,'started':False,'alias_active':True,'stopped':False,'cancel_delivered':False,'remote_outcome':'unknown','missing':False,'executor':'head','executor_binding':(('lease','goal-a','kernel-a','head',1,'lease-identity-1'),('process','goal-a','kernel-a','head',1,'process-identity-1')),'wait':'none','wait_graph':(),'unrelated':'active','reserved':6,'free':4,'done':(),'decision':'initial'}
 d.require(s==expected,'complete independent initialization');invariant(s)

def check(s,a,n,name):
 if n['wake_count']>s['wake_count']:d.require(eligible(s,s['adopted']) and s['executor']=='free','fresh current authority at continuation admission')
 if a in ('ingest','duplicate-reply') and not s['alias_active']:d.require(n['evidence']==s['evidence'],'retired alias cannot create evidence')
 d.require(a in enabled(s,name),'enabled action');d.require(n==expected(s,a),'complete independent postcondition '+a);invariant(n)
