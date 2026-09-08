"""Inclusive transition implementation; no comparator or audit predicates imported."""
import copy,base64
import c_domain as d

def current(s,p,skip=None):
 if not p or not s['request'] or p!=s['request'] or s['stopped'] or not s['alias_active']:return False
 return all((skip==k or (type(p[i][4]) is int and p[i]==s['tokens'][k])) for i,k in enumerate(('goal','lease','process','delivery'),1))
def step(s,a,p,u,outcome,mutant=None):
 n=copy.deepcopy(s);k=a.split('@')[0];n['done']=s['done']|(1<<p['actions'].index(a));n['decision']=k+':ok'
 def deny(why):n['decision']=k+':'+why
 def wire(m):n['wire']=s['wire']+(d.canonical(m),)
 def revise():n['revision']=s['revision']+1
 def log(kind,binding=(),packet=(),result=0):
  if len(s['catalog'])>=4:raise ValueError('catalogue bound')
  n['catalog']=s['catalog']+((kind,binding,packet,n['revision'],result),)
 if k in ('readA','readB'):i=k[-1]=='B';n['reads']=s['reads'][:i]+(s['free'],)+s['reads'][i+1:]
 elif k in ('admitA','admitB','duplicateA','wrong-owner','wrong-payload'):
  i=int(k=='admitB');r=list(d.REQUESTS[i])
  if k=='wrong-owner':r[5]='ownerB'
  if k=='wrong-payload':r[4]='other-payload'
  r=tuple(r);expected=s['bindings'][i] or d.REQUESTS[i]
  if r!=expected and mutant!='identity':deny('identity-conflict')
  elif s['bindings'][i]:deny('duplicate')
  elif s['free']<6 and mutant!='serialization':deny('capacity-denied')
  else:
   n['free']-=6;n['reserved']=s['reserved'][:i]+(6,)+s['reserved'][i+1:];n['bindings']=s['bindings'][:i]+(r,)+s['bindings'][i+1:];revise();deny('admitted')
   if i==0:log('reserve',r)
 elif k=='foreign-release':
  deny('owner-refused')
  if mutant=='foreign-release':n['free']+=s['reserved'][0];n['reserved']=(0,s['reserved'][1])
 elif k=='intent':
  if s['reserved'][0]==6 and not s['intent']:n['intent']=True;revise()
  else:deny('unavailable')
 elif k in ('send','resend'):
  if s['intent'] and s['reserved'][0]==6 and (not s['sent'] or mutant=='resend'):
   n['sent']+=1;revise()
  else:deny('ambiguous-or-unavailable')
 elif k=='remote':
  if s['sent'] and not s['remote']:n['remote']=outcome
  else:deny('unavailable')
 elif k=='lose':deny('unknown' if s['remote'] else 'unavailable')
 elif k in ('query','query-wrong'):
  incoming=d.REQUESTS[1 if k=='query-wrong' else 0]
  if not s['remote']:deny('unknown')
  elif incoming!=s['bindings'][0] and mutant!='receipt-binding':deny('receipt-binding-conflict')
  else:n['receipt']=s['remote'];n['receipt_binding']=incoming;revise()
 elif k=='classify':
  if s['receipt']:n['classification']=s['receipt']
  else:deny('unknown')
  if mutant=='classify-release' and s['receipt']:n['free']+=s['reserved'][0];n['reserved']=(0,s['reserved'][1])
 elif k=='conflict':n['conflict']=True
 elif k=='reconcile':
  if s['classification'] and (not s['conflict'] or mutant=='conflict') and (s['reserved'][0] or mutant=='settle-twice'):
   amount=6 if mutant=='settle-twice' else s['reserved'][0];n['reserved']=(0,s['reserved'][1]);revise()
   if s['classification']==1 and mutant!='success-refund':n['consumed']=(s['consumed'][0]+amount,s['consumed'][1])
   else:n['free']+=amount
   if not any(x[0]=='settlement' for x in s['catalog']):log('settlement',s['bindings'][0],result=s['classification'])
  else:deny('held-or-duplicate')
 elif k=='consult':
  if not s['bindings'][0] or s['stopped']:deny('unavailable')
  else:
   t=s['tokens'];n['request']=('consultA',t['goal'],t['lease'],t['process'],t['delivery'],'contextA','adviceA','head','consultant','grantA',s['bindings'][0]);n['alias_active']=True
 elif k=='wait-held':
  if s['request'] and s['executor']=='head':n['wait']=(('head','consultA'),('consultA','executor'),('executor','head'));deny('blocked-dependency')
  else:deny('unavailable')
  if mutant=='hidden-wait':n['wait']=()
 elif k=='suspend':
  if s['request']:
   n['wait']=()
   if s['executor']=='head' and mutant!='hold-executor':n['executor']='free';n['executor_binding']=()
  else:deny('unavailable')
 elif k=='start':
  if current(s,s['request']) and s['executor']=='free':n['started']=True;n['executor']='consultA';n['executor_binding']=(s['request'][2],s['request'][3])
  else:deny('authority-or-executor')
 elif k in ('reply','reply-wrong'):
  if not s['started'] or s['reply']:deny('unavailable')
  else:
   b=s['request']
   if k=='reply-wrong':b=('consultB',)+b[1:]
   n['reply']=b;log('advice',s['bindings'][0],b)
   if s['executor']=='consultA':n['executor']='free';n['executor_binding']=()
 elif k=='ingest':
  candidates=[s['catalog'][i-1] for i in s['received'] if s['catalog'][i-1][0]=='advice']
  if s['evidence']:deny('duplicate')
  elif not candidates:deny('missing-delivery')
  else:
   row=candidates[0];b=row[2]
   if (row[1]!=s['bindings'][0] or b!=s['request']) and mutant!='catalog-binding':deny('binding-conflict')
   elif not s['alias_active'] or b[4]!=s['tokens']['delivery']:n['missing']=True;deny('expired-delivery')
   else:n['evidence']=b
 elif k=='adopt':
  if s['adopted']:deny('duplicate')
  elif not current(s,s['evidence'],'lease' if mutant=='adopt-lease' else None):deny('stale-or-missing')
  else:n['adopted']=s['evidence'];n['adoptions']+=1
 elif k=='wake':
  if s['wakes']:
   deny('duplicate')
   if mutant=='duplicate-wake':n['wakes']+=1
  elif not current(s,s['adopted'],'lease' if mutant=='wake-lease' else None):deny('stale-or-missing')
  elif s['executor']!='free':deny('executor-unavailable')
  else:n['wakes']+=1;n['executor']='head';n['executor_binding']=(s['adopted'][2],s['adopted'][3])
 elif k in ('lease','goal'):n['tokens'][k]=d.token(k,2)
 elif k=='expire':n['tokens']['delivery']=d.token('delivery',2);n['alias_active']=False
 elif k=='stop-request':
  if mutant=='shared-control' and sum(d.COSTS[i-1] for i in s['pending'])>=2:deny('blocked-data-queue')
  elif s['control']==0:n['control']=1
  else:deny('duplicate')
 elif k=='stop-apply':
  if s['control']==1:
   n['control']=2;n['stopped']=True;n['alias_active']=mutant=='alias-retirement';n['tokens']['delivery']=d.token('delivery',2)
   if mutant=='stop-release':n['free']+=s['reserved'][0];n['reserved']=(0,s['reserved'][1])
   if mutant=='cancel-all':n['unrelated']='stopped'
  else:deny('unavailable')
 elif k=='cancel':
  if s['stopped']:n['cancelled']=True
  else:deny('unavailable')
 elif k=='unrelated':
  if s['unrelated']=='active-local':n['unrelated']='completed-local'
  else:deny('unavailable')
 elif k=='restart':
  n['tokens']['process']=d.token('process',2);n['replay_cursor']=0
  if s['executor']=='head':n['executor']='free';n['executor_binding']=();n['wait']=()
  if mutant=='restart-release':n['free']+=s['reserved'][0];n['reserved']=(0,s['reserved'][1])
 elif k=='replay':
  n['replay_cursor']=s['revision']
  if mutant=='replay-release':n['free']+=s['reserved'][0];n['reserved']=(0,s['reserved'][1])
 elif k=='quota':
  n['quota_epoch']=1;n['quota_used']=0
  if mutant=='quota-release':n['free']+=s['reserved'][0];n['reserved']=(0,s['reserved'][1])
 elif k=='exit':n['worker_exited']=True
 elif k=='compute':
  if s['tokens']['process'][4]==2 and s['lifetime'][1]==0:n['lifetime']=(s['lifetime'][0],1);n['quota_used']+=1
  else:deny('unavailable')
 elif k=='publish':n['generation']=2
 elif k=='capture':n['snapshot']=(1,0,10,(0,0),(0,0),1);n['pin']=True
 elif k=='copy':
  if s['snapshot']:n['copied']=True
  else:deny('unavailable')
 elif k=='pin-release':
  if s['copied']:n['pin']=False
  else:deny('unavailable')
 elif k=='offer':
  if s['offered']<len(s['catalog']) and len(s['retained'])<2 and not s['quarantine'] and not s['frame']:
   n['offered']+=1;n['retained']+= (n['offered'],)
  else:deny('backpressure-or-unavailable')
 elif k=='pump-source':
  if s['retained'] and len(s['channels'][0])<1 and sum(map(len,s['channels']))<2:n['channels']=(s['channels'][0]+(s['retained'][0],),*s['channels'][1:]);n['retained']=s['retained'][1:]
  else:deny('backpressure-or-unavailable')
 elif k in ('pump-sdk','pump-broker'):
  i=int(k=='pump-broker');q=list(s['channels'])
  if q[i] and len(q[i+1])<1:q[i+1]+=(q[i][0],);q[i]=q[i][1:];n['channels']=tuple(q)
  else:deny('backpressure-or-unavailable')
 elif k=='evict':
  if not s['loss'] and 1 in s['retained']+sum(s['channels'],()):n['loss']=1;n['retained']=tuple(i for i in s['retained'] if i!=1);n['channels']=tuple(tuple(i for i in q if i!=1) for q in s['channels'])
  else:deny('unavailable')
 elif k=='hello':
  if s['loss']==1 and not s['covered'] and s['wire_sent']==0 and s['snapshot'] and s['copied'] and s['phase']==0:n['phase']=1;wire(d.hello(0,u))
  else:deny('unavailable')
 elif k=='welcome':
  if s['phase']==1:n['phase']=2;wire(d.msg('WELCOME',client_id='client-a',replay_floor=d.cursor(1,u),snapshot_cursor=d.cursor(1,u),cursor_unit=u,input_lease=None,resize_lease=None,capabilities=['attach']))
  else:deny('unavailable')
 elif k=='reset':
  if s['phase']==2:
   n.update(phase=3,covered=1,wire_sent=1,pending=(),acknowledged=1,byte_credit=0,event_credit=0);wire(d.msg('RESET',client_id='client-a',reason='gap',snapshot_cursor=d.cursor(1,u),cursor_unit=u))
   if mutant=='reset-credit':n['byte_credit']=s['byte_credit'];n['event_credit']=s['event_credit']
   if mutant=='erase-future':n['retained']=();n['channels']=((),(),())
  else:deny('unavailable')
 elif k=='install':
  if s['phase']==3 and s['copied']:
   n['installed']=s['snapshot'];n['installed_cursor']=1
   if mutant=='snapshot-ledger':n['free']=s['snapshot'][2];n['reserved']=s['snapshot'][3];n['consumed']=s['snapshot'][4]
  else:deny('unavailable')
 elif k.startswith('credit:'):
  if s['phase']!=2 and s['grants']<4:n['grants']+=1;n['byte_credit']+=int(k[-1]);n['event_credit']+=1;wire(d.msg('CREDIT',client_id='client-a',bytes=int(k[-1]),events=1))
  else:deny('unavailable')
 elif k=='emit':
  q=s['channels'][2];i=q[0] if q else 0;cost=d.COSTS[i-1] if i else 0
  if i and i==s['wire_sent']+1 and s['phase']!=2 and (not s['covered'] or s['installed_cursor']==s['covered'] or mutant=='install-guard') and s['byte_credit']>=cost and s['event_credit']>=1 and len(s['pending'])<2 and sum(d.COSTS[j-1] for j in s['pending'])+cost<=2 and len(s['delivery'])<2 and sum(d.COSTS[j-1] for j in s['delivery'])+cost<=2:
   n['channels']=(*s['channels'][:2],q[1:]);n['wire_sent']=i;n['delivered']+=(i,);n['pending']+=(i,);n['delivery']+=(i,);n['byte_credit']-=cost;n['event_credit']-=1
   wire(d.msg('EVENT',cursor=d.cursor(i,u),cursor_unit=u,event_class='output',process_id='process-a',payload_base64=base64.b64encode(d.TOKENS[i-1]).decode(),payload_untrusted=True))
  else:deny('backpressure-or-unavailable')
 elif k=='receive':
  if s['delivery']:n['received']+=(s['delivery'][0],);n['delivery']=s['delivery'][1:]
  else:deny('unavailable')
 elif k=='ack':
  if s['pending'] and s['phase']!=2:n['pending']=();n['acknowledged']=s['wire_sent'];wire(d.msg('ACK',client_id='client-a',cursor=d.cursor(s['wire_sent'],u),cursor_unit=u))
  else:deny('unavailable')
 elif k=='lose-ack':
  deny('lost')
  if mutant=='lost-ack-release':n['pending']=()
 elif k=='fragment':
  if not s['quarantine'] and s['frame']<2:n['frame']+=1
  else:deny('bounded-refusal')
 elif k=='framing-fault':
  if s['frame']:n['frame']=0;n['quarantine']=True
  else:deny('unavailable')
 else:raise ValueError('unknown action '+k)
 return n
