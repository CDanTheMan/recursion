"""Independent whole-product relation and noninterference properties."""
import copy,base64
import c_domain as d

def fresh(domain,n):return (domain,'operationA' if domain=='delivery' else 'goalA','owner' if domain=='goal' else 'kernel','head',n,domain+'-identity-'+str(n))
def authoritative(s,b):
 return bool(b and b==s['request'] and s['alias_active'] and not s['stopped'] and all(type(b[i][4]) is int and b[i]==s['tokens'][name] for i,name in ((1,'goal'),(2,'lease'),(3,'process'),(4,'delivery'))))
def enabled(s,p):
 finished={p['actions'][i] for i in range(len(p['actions'])) if (s['done']>>i)&1}
 return {a for a in p['actions'] if a not in finished and set(p['requires'][a])<=finished}
def invariant(s):
 d.require(s['free']>=0 and s['free']+sum(s['reserved'])+sum(s['consumed'])==10 and sum(s['reserved'])+sum(s['consumed'])<=10,'aggregate cumulative pool conservation')
 d.require(all(x in (0,6) for x in s['reserved']+s['consumed']),'six-unit amounts')
 d.require(s['sent'] in (0,1),'no ambiguous duplicate dispatch')
 if s['sent'] and s['classification']==0:d.require(s['reserved'][0]==6,'uncertain dispatched effect retains reservation')
 for i,b in enumerate(s['bindings']):d.require(not b or b==d.REQUESTS[i],'durable actual request ownership')
 if s['receipt']:d.require(s['receipt_binding']==s['bindings'][0],'receipt binds actual reserved operation')
 if s['evidence']:d.require(s['evidence']==s['request'] and any(s['catalog'][i-1][0]=='advice' and s['catalog'][i-1][2]==s['evidence'] for i in s['received']),'evidence needs actual delivered immutable packet')
 d.require(s['adoptions'] in (0,1) and s['wakes'] in (0,1),'adoption and wake idempotence')
 d.require(s['unrelated'] in ('active-local','completed-local'),'operation scoped Stop')
 physical=s['retained']+sum(s['channels'],())
 d.require(len(s['retained'])<=2 and all(len(q)<=1 for q in s['channels']) and sum(map(len,s['channels']))<=2,'full physical ownership bounds')
 d.require(sorted(physical+s['delivered']+((s['loss'],) if s['loss'] else ()))==list(range(1,s['offered']+1)),'every offered record has one disposition')
 d.require(tuple(sorted(s['received']+s['delivery']))==s['delivered'] and not set(s['received'])&set(s['delivery']),'application ownership survives ACK')
 for ids in (s['pending'],s['delivery']):d.require(len(ids)<=2 and sum((1,2,1,2)[i-1] for i in ids)<=2,'receiver event and byte bounds')
 d.require(set(s['pending'])<=set(s['delivered']) and all(s['acknowledged']<i<=s['wire_sent'] for i in s['pending']),'pending receiver ownership')
 d.require(0<=s['byte_credit']<=8 and 0<=s['event_credit']<=4 and 0<=s['grants']<=4 and 0<=s['frame']<=2,'credit and frame caps')
 d.require(len(s['catalog'])<=4 and 0<=s['offered']<=len(s['catalog']),'catalogue admission bounds')
 d.require(s['catalog'][0]==('boot',(),(),0,0),'immutable boot record')
 for row in s['catalog'][1:]:
  d.require(row[0] in ('reserve','advice','settlement') and row[1]==s['bindings'][0] and 0<row[3]<=s['revision'],'immutable record source binding')
  if row[0]=='advice':d.require(row[2]==s['reply'],'actual reply packet catalogue')
 d.require(not s['installed'] or s['installed']==(1,0,10,(0,0),(0,0),1),'presentation is immutable old snapshot')

def initialization(s,u):
 t={k:fresh(k,1) for k in ('goal','lease','process','delivery')}
 expected=dict(free=10,reserved=(0,0),consumed=(0,0),bindings=((),()),intent=False,sent=0,remote=0,receipt=0,receipt_binding=(),classification=0,conflict=False,revision=0,reads=(10,10),tokens=t,request=(),reply=(),evidence=(),adopted=(),adoptions=0,wakes=0,started=False,executor='head',executor_binding=(t['lease'],t['process']),wait=(),alias_active=True,stopped=False,control=0,cancelled=False,missing=False,unrelated='active-local',worker_exited=False,lifetime=(1,0),quota_epoch=0,quota_used=1,generation=1,pin=False,copied=False,snapshot=(),installed=(),installed_cursor=0,replay_cursor=0,catalog=(('boot',(),(),0,0),),offered=0,retained=(),channels=((),(),()),wire_sent=0,pending=(),delivery=(),received=(),delivered=(),loss=0,covered=0,phase=0,byte_credit=0,event_credit=0,grants=0,acknowledged=0,frame=0,quarantine=False,done=0,decision='initial')
 expected['wire']=(d.canonical({'type':'HELLO','protocol_version':'m1b-broker/1','stream_id':'stream-a','daemon_epoch':2,'client_id':'client-a','last_cursor':0,'cursor_unit':u,'columns':80,'rows':24,'capabilities':['attach']}),)
 d.require(s==expected,'complete independent initialization');invariant(s)

def check(s,a,n,p,u,remote):
 d.require(a in enabled(s,p),'complete offered enabledness')
 k=a.split('@')[0];ch={};reason='ok';message=None
 def change(**x):ch.update(x)
 def reject(x):return x
 def revision():ch['revision']=s['revision']+1
 def append(kind,b=(),packet=(),result=0):ch['catalog']=s['catalog']+((kind,b,packet,ch.get('revision',s['revision']),result),)
 def wire(kind,**fields):return dict(type=kind,protocol_version='m1b-broker/1',stream_id='stream-a',daemon_epoch=2,**fields)
 def cur(ix):return (0,1,3,4,6)[ix] if u=='utf8-byte' else ix
 if k in ('readA','readB'):
  j={'readA':0,'readB':1}[k];v=list(s['reads']);v[j]=s['free'];change(reads=tuple(v))
 elif k in ('admitA','admitB','duplicateA','wrong-owner','wrong-payload'):
  j=1 if k=='admitB' else 0;r=list(d.REQUESTS[j])
  if k=='wrong-owner':r[5]='ownerB'
  if k=='wrong-payload':r[4]='other-payload'
  r=tuple(r)
  if r!=(s['bindings'][j] or d.REQUESTS[j]):reason='identity-conflict'
  elif s['bindings'][j]:reason='duplicate'
  elif 6>s['free']:reason='capacity-denied'
  else:
   b=list(s['bindings']);b[j]=r;v=list(s['reserved']);v[j]=6;change(free=s['free']-6,reserved=tuple(v),bindings=tuple(b));revision();reason='admitted'
   if j==0:append('reserve',r)
 elif k=='foreign-release':reason='owner-refused'
 elif k=='intent':
  if s['reserved'][0]==6 and s['intent'] is False:change(intent=True);revision()
  else:reason='unavailable'
 elif k in ('send','resend'):
  if s['intent'] and s['reserved'][0]==6 and s['sent']==0:change(sent=1);revision()
  else:reason='ambiguous-or-unavailable'
 elif k=='remote':
  if s['sent']!=0 and s['remote']==0:change(remote=remote)
  else:reason='unavailable'
 elif k=='lose':reason='unknown' if s['remote'] else 'unavailable'
 elif k in ('query','query-wrong'):
  received_binding=d.REQUESTS[int(k=='query-wrong')]
  if s['remote'] not in (1,2):reason='unknown'
  elif received_binding!=s['bindings'][0]:reason='receipt-binding-conflict'
  else:change(receipt=s['remote'],receipt_binding=received_binding);revision()
 elif k=='classify':
  if s['receipt'] in (1,2):change(classification=s['receipt'])
  else:reason='unknown'
 elif k=='conflict':change(conflict=True)
 elif k=='reconcile':
  if s['classification'] in (1,2) and s['conflict'] is False and s['reserved'][0]==6:
   change(reserved=(0,s['reserved'][1]));revision()
   if s['classification']==1:change(consumed=(s['consumed'][0]+6,s['consumed'][1]))
   else:change(free=s['free']+6)
   if not any(row[0]=='settlement' for row in s['catalog']):append('settlement',s['bindings'][0],result=s['classification'])
  else:reason='held-or-duplicate'
 elif k=='consult':
  if s['bindings'][0] and not s['stopped']:change(alias_active=True,request=('consultA',s['tokens']['goal'],s['tokens']['lease'],s['tokens']['process'],s['tokens']['delivery'],'contextA','adviceA','head','consultant','grantA',s['bindings'][0]))
  else:reason='unavailable'
 elif k=='wait-held':
  if s['request'] and s['executor']=='head':change(wait=(('head','consultA'),('consultA','executor'),('executor','head')));reason='blocked-dependency'
  else:reason='unavailable'
 elif k=='suspend':
  if s['request']:
   change(wait=())
   if s['executor']=='head':change(executor='free',executor_binding=())
  else:reason='unavailable'
 elif k=='start':
  if authoritative(s,s['request']) and s['executor']=='free':change(started=True,executor='consultA',executor_binding=(s['request'][2],s['request'][3]))
  else:reason='authority-or-executor'
 elif k in ('reply','reply-wrong'):
  if s['started'] and not s['reply']:
   b=s['request'] if k=='reply' else ('consultB',)+s['request'][1:];change(reply=b);append('advice',s['bindings'][0],b)
   if s['executor']=='consultA':change(executor='free',executor_binding=())
  else:reason='unavailable'
 elif k=='ingest':
  candidates=tuple(row for i,row in enumerate(s['catalog'],1) if i in s['received'] and row[0]=='advice')
  if s['evidence']:reason='duplicate'
  elif not candidates:reason='missing-delivery'
  elif candidates[0][1]!=s['bindings'][0] or candidates[0][2]!=s['request']:reason='binding-conflict'
  elif s['alias_active'] is False or candidates[0][2][4]!=s['tokens']['delivery']:change(missing=True);reason='expired-delivery'
  else:change(evidence=candidates[0][2])
 elif k=='adopt':
  if s['adopted']:reason='duplicate'
  elif authoritative(s,s['evidence']):change(adopted=s['evidence'],adoptions=1)
  else:reason='stale-or-missing'
 elif k=='wake':
  if s['wakes']:reason='duplicate'
  elif not authoritative(s,s['adopted']):reason='stale-or-missing'
  elif s['executor']!='free':reason='executor-unavailable'
  else:change(wakes=1,executor='head',executor_binding=(s['adopted'][2],s['adopted'][3]))
 elif k in ('lease','goal','expire','restart'):
  t=dict(s['tokens']);name={'expire':'delivery','restart':'process'}.get(k,k);t[name]=fresh(name,2);change(tokens=t)
  if k=='expire':change(alias_active=False)
  if k=='restart':
   change(replay_cursor=0)
   if s['executor']=='head':change(executor='free',executor_binding=(),wait=())
 elif k=='stop-request':
  if s['control']==0:change(control=1)
  else:reason='duplicate'
 elif k=='stop-apply':
  if s['control']==1:
   t=dict(s['tokens']);t['delivery']=fresh('delivery',2);change(control=2,stopped=True,alias_active=False,tokens=t)
  else:reason='unavailable'
 elif k=='cancel':
  if s['stopped']:change(cancelled=True)
  else:reason='unavailable'
 elif k=='unrelated':
  if s['unrelated']=='active-local':change(unrelated='completed-local')
  else:reason='unavailable'
 elif k=='replay':change(replay_cursor=s['revision'])
 elif k=='quota':change(quota_epoch=1,quota_used=0)
 elif k=='exit':change(worker_exited=True)
 elif k=='compute':
  if s['tokens']['process'][4]==2 and s['lifetime'][1]==0:change(lifetime=(s['lifetime'][0],1),quota_used=s['quota_used']+1)
  else:reason='unavailable'
 elif k=='publish':change(generation=2)
 elif k=='capture':change(snapshot=(1,0,10,(0,0),(0,0),1),pin=True)
 elif k in ('copy','pin-release'):
  if (s['snapshot'] if k=='copy' else s['copied']):ch['copied' if k=='copy' else 'pin']=k=='copy'
  else:reason='unavailable'
 elif k=='offer':
  if s['offered']<len(s['catalog']) and len(s['retained'])<2 and s['quarantine'] is False and s['frame']==0:change(offered=s['offered']+1,retained=(*s['retained'],s['offered']+1))
  else:reason='backpressure-or-unavailable'
 elif k=='pump-source':
  if s['retained'] and not s['channels'][0] and len(sum(s['channels'],()))<2:change(retained=s['retained'][1:],channels=((s['retained'][0],),s['channels'][1],s['channels'][2]))
  else:reason='backpressure-or-unavailable'
 elif k in ('pump-sdk','pump-broker'):
  ix=0 if k=='pump-sdk' else 1;rows=list(s['channels'])
  if len(rows[ix])==1 and len(rows[ix+1])==0:rows[ix+1]=rows[ix];rows[ix]=();change(channels=tuple(rows))
  else:reason='backpressure-or-unavailable'
 elif k=='evict':
  if s['loss']==0 and 1 in s['retained']+sum(s['channels'],()):change(loss=1,retained=tuple(i for i in s['retained'] if i!=1),channels=tuple(tuple(i for i in q if i!=1) for q in s['channels']))
  else:reason='unavailable'
 elif k=='hello':
  if s['loss']==1 and s['covered']==0 and s['wire_sent']==0 and s['snapshot'] and s['copied'] and s['phase']==0:change(phase=1);message=wire('HELLO',client_id='client-a',last_cursor=0,cursor_unit=u,columns=80,rows=24,capabilities=['attach'])
  else:reason='unavailable'
 elif k=='welcome':
  if s['phase']==1:change(phase=2);message=wire('WELCOME',client_id='client-a',replay_floor=cur(1),snapshot_cursor=cur(1),cursor_unit=u,input_lease=None,resize_lease=None,capabilities=['attach'])
  else:reason='unavailable'
 elif k=='reset':
  if s['phase']==2:change(phase=3,covered=1,wire_sent=1,pending=(),acknowledged=1,byte_credit=0,event_credit=0);message=wire('RESET',client_id='client-a',reason='gap',snapshot_cursor=cur(1),cursor_unit=u)
  else:reason='unavailable'
 elif k=='install':
  if s['phase']==3 and s['copied']:change(installed=s['snapshot'],installed_cursor=1)
  else:reason='unavailable'
 elif k.startswith('credit:'):
  amount=int(k[-1])
  if s['phase']!=2 and s['grants']<4:change(grants=s['grants']+1,byte_credit=s['byte_credit']+amount,event_credit=s['event_credit']+1);message=wire('CREDIT',client_id='client-a',bytes=amount,events=1)
  else:reason='unavailable'
 elif k=='emit':
  ix=s['channels'][2][0] if s['channels'][2] else 0;cost=(1,2,1,2)[ix-1] if ix else 0
  room=all(len(ids)<2 and sum((1,2,1,2)[i-1] for i in ids)+cost<=2 for ids in (s['pending'],s['delivery']))
  allowed=ix and ix==s['wire_sent']+1 and s['phase']!=2 and (s['covered']==0 or s['installed_cursor']==s['covered']) and s['byte_credit']>=cost and s['event_credit']>0 and room
  if allowed:
   change(channels=(s['channels'][0],s['channels'][1],s['channels'][2][1:]),wire_sent=ix,delivered=(*s['delivered'],ix),pending=(*s['pending'],ix),delivery=(*s['delivery'],ix),byte_credit=s['byte_credit']-cost,event_credit=s['event_credit']-1)
   payload=(b'a',b'bb',b'c',b'dd')[ix-1];message=wire('EVENT',cursor=cur(ix),cursor_unit=u,event_class='output',process_id='process-a',payload_base64=base64.b64encode(payload).decode(),payload_untrusted=True)
  else:reason='backpressure-or-unavailable'
 elif k=='receive':
  if s['delivery']:change(received=(*s['received'],s['delivery'][0]),delivery=s['delivery'][1:])
  else:reason='unavailable'
 elif k=='ack':
  if s['pending'] and s['phase']!=2:change(pending=(),acknowledged=s['wire_sent']);message=wire('ACK',client_id='client-a',cursor=cur(s['wire_sent']),cursor_unit=u)
  else:reason='unavailable'
 elif k=='lose-ack':reason='lost'
 elif k=='fragment':
  if not s['quarantine'] and s['frame']<2:change(frame=s['frame']+1)
  else:reason='bounded-refusal'
 elif k=='framing-fault':
  if s['frame']>0:change(frame=0,quarantine=True)
  else:reason='unavailable'
 else:raise ValueError('unregistered action '+k)
 if message is not None:ch['wire']=(*s['wire'],d.canonical(message))
 ch.update(done=s['done']|(1<<p['actions'].index(a)),decision=k+':'+reason)
 expected=copy.deepcopy(s);expected.update(ch)
 d.require(n==expected,'complete independent postcondition '+k)
 invariant(n)
 if k!='reconcile':d.require(n['consumed']==s['consumed'],'only reconciliation commits consumption')
 if n['reserved'][0]<s['reserved'][0]:d.require(k=='reconcile' and s['receipt'] in (1,2) and not s['conflict'],'only exact verified reconciliation settles')
 if n['adoptions']>s['adoptions']:d.require(authoritative(s,s['evidence']),'independent fresh adoption')
 if n['wakes']>s['wakes']:d.require(authoritative(s,s['adopted']) and s['executor']=='free','independent fresh continuation')
 if not s['alias_active']:d.require(n['evidence']==s['evidence'],'inactive alias cannot create evidence')
