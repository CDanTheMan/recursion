"""Inclusive reducer. No reducer or authority predicate imported from comparator/audit."""
import copy
import epoch_domain as d

def equal(a,b,mutant):
 if not isinstance(a,tuple) or not isinstance(b,tuple):return a==b
 if len(a)!=6 or len(b)!=6 or type(a[4]) is not int or type(b[4]) is not int:return False
 if mutant=='serial-only':return a[4]==b[4]
 if mutant=='omit-issuer':return a[:2]+a[3:]==b[:2]+b[3:]
 return a==b

def current(s,b,mutant=None):
 if b is None or s['request'] is None:return False
 if any(not equal(b[i],s['request'][i],mutant) for i in (1,2,3,4)):return False
 if b[0]!=s['request'][0] or b[5:]!=s['request'][5:]:return False
 for i,tag in ((1,'goal'),(2,'lease'),(3,'process'),(4,'delivery')):
  if mutant=={'goal':'omit-goal','lease':'omit-lease','process':'omit-incarnation','delivery':'omit-delivery'}[tag]:continue
  if not equal(b[i],s['tokens'][tag],mutant):return False
 return not s['stopped'] and s['alias_active']

def step(s,a,mutant=None):
 n=copy.deepcopy(s);n['done']=tuple(sorted((*s['done'],a)));n['decision']=a+':accepted';t=n['tokens']
 def deny(reason):n['decision']=a+':'+reason
 if a=='request':
  if s['stopped']:deny('expired-operation')
  else:n['request']=('operation-a',t['goal'],t['lease'],t['process'],t['delivery'],'context-1','payload-1','head','consultant','grant-a');n['input_request']=n['request'];n['alias_active']=True
 elif a in ('duplicate-request','conflict-request'):
  if s['request'] is None:deny('missing-request')
  else:
   incoming=list(s['request'])
   if a=='conflict-request':incoming[6]='payload-2'
   n['input_request']=tuple(incoming);deny('duplicate' if n['input_request']==s['request'] or mutant=='payload-conflict' else 'payload-conflict')
 elif a=='wait-held':
  if s['request'] is None:deny('missing-request')
  elif s['executor']=='head':
   n['wait']='blocked-dependency';n['wait_graph']=(('head','consultation-a'),('consultation-a','executor-e'),('executor-e','head'));deny('blocked-dependency')
   if mutant=='invisible-wait':n['wait']='waiting';n['wait_graph']=()
  else:n['wait']='waiting-released'
 elif a=='suspend':
  if s['request'] is None:deny('missing-request')
  else:
   n['wait']='suspended';n['wait_graph']=()
   if s['executor']=='head' and mutant!='hold-executor':n['executor']='free';n['executor_binding']=None
 elif a=='start':
  if not current(s,s['request'],mutant):deny('stale-or-missing-authority')
  elif s['executor']!='free':deny('executor-unavailable')
  else:n['started']=True;n['executor']='consultation-a';n['executor_binding']=(s['request'][2],s['request'][3])
 elif a=='reply':
  if not s['started']:deny('not-started')
  else:
   n['reply']=s['request']
   if s['executor']=='consultation-a':n['executor']='free';n['executor_binding']=None
 elif a in ('ingest','duplicate-reply'):
  if s['reply'] is None:deny('missing-reply')
  elif s['evidence'] is not None:deny('duplicate')
  elif (s['alias_active'] and equal(s['reply'][4],s['tokens']['delivery'],mutant)) or mutant=='omit-delivery':n['evidence']=s['reply']
  else:n['missing']=True;deny('expired-delivery-missing')
 elif a in ('adopt','adopt-again'):
  if s['adopted'] is not None:
   deny('duplicate')
   if mutant=='duplicate-adopt':n['adoption_count']+=1
  elif not current(s,s['evidence'],mutant):deny('stale-or-missing-authority')
  else:n['adopted']=s['evidence'];n['adoption_count']=1
 elif a in ('wake','wake-again','relaunch'):
  if not current(s,s['adopted'],'omit-lease' if mutant=='wake-lease' else mutant):deny('stale-or-missing-authority')
  elif s['wake_count']:
   deny('duplicate')
   if mutant=='duplicate-wake':n['wake_count']+=1
  elif s['executor']!='free':deny('executor-unavailable')
  else:n['wake_count']=1;n['executor']='head';n['executor_binding']=(s['adopted'][2],s['adopted'][3]);n['wait']='none';n['wait_graph']=()
 elif a in ('lease2','lease3'):t['lease']=d.token('lease',2 if a=='lease2' else 3,issuer=t['lease'][2])
 elif a=='issuer':t['lease']=d.token('lease',t['lease'][4],issuer='kernel-b')
 elif a=='restart':
  t['process']=d.token('process',2 if mutant!='restore-incarnation' else 1)
  if s['executor']=='head':n['executor']='free';n['executor_binding']=None;n['wait']='recovered';n['wait_graph']=()
 elif a=='expire':
  t['delivery']=d.token('delivery',2);n['alias_active']=False
  if mutant=='erase-evidence':n['evidence']=None
 elif a=='stop':
  n['stopped']=True;n['alias_active']=(mutant=='alias-retirement')
  if mutant!='stop-generation':t['delivery']=d.token('delivery',2)
  if mutant=='cancel-all':n['unrelated']='stopped'
  if mutant=='release-reservation':n['reserved']=0;n['free']=10
 elif a=='cancel-deliver':
  if not s['stopped']:deny('not-stopped')
  else:
   n['cancel_delivered']=True
   if mutant=='false-settlement':n['remote_outcome']='settled'
 elif a=='unrelated':
  if s['unrelated']=='active':n['unrelated']='completed'
  else:deny('not-active')
 elif a=='owner-amend':t['goal']=d.token('goal',2);n['goal_record']=('goal-a',2,'goal-digest-2')
 elif a=='advice-amend':
  deny('owner-authority-required')
  if mutant=='advice-amend':t['goal']=d.token('goal',2);n['goal_record']=('goal-a',2,'goal-digest-2')
 elif a=='wrong-domain':
  if s['reply'] is None:deny('missing-reply')
  else:
   b=list(s['reply']);v=list(b[2]);v[0]='writer';b[2]=tuple(v);n['reply']=tuple(b)
 else:raise ValueError('unknown action')
 return n
