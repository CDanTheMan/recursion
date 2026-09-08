"""Authority, flow and presentation transitions; independent of inclusive reducer."""
import copy,base64
import c_domain as d

def valid(authority,b):
 if b==() or b!=authority['request']:return False
 if authority['stopped'] or authority['alias_active'] is False:return False
 for ix,key in ((1,'goal'),(2,'lease'),(3,'process'),(4,'delivery')):
  if type(b[ix][4])!=int or authority['tokens'][key]!=b[ix]:return False
 return True

def step(state,action,profile,unit,remote_result):
 au,fl,vi=copy.deepcopy(state);old=state.authority;f=state.flow;v=state.view;k=action.partition('@')[0];result='ok';m=None
 def deny(reason):return reason
 def commit():au['revision']=old['revision']+1
 def record(kind,owner=(),packet=(),effect=0):au['catalog']=(*old['catalog'],(kind,owner,packet,au['revision'],effect))
 if k in ('readA','readB'):
  ix=0 if k=='readA' else 1;vals=list(old['reads']);vals[ix]=old['free'];au['reads']=tuple(vals)
 elif k in ('admitA','admitB','duplicateA','wrong-owner','wrong-payload'):
  ix=1 if k=='admitB' else 0;incoming=list(d.REQUESTS[ix]);incoming[5]='ownerB' if k=='wrong-owner' else incoming[5];incoming[4]='other-payload' if k=='wrong-payload' else incoming[4];incoming=tuple(incoming)
  expected=old['bindings'][ix] or d.REQUESTS[ix]
  if incoming!=expected:result='identity-conflict'
  elif old['bindings'][ix]!=():result='duplicate'
  elif old['free']-6<0:result='capacity-denied'
  else:
   amounts=list(old['reserved']);amounts[ix]=6;owners=list(old['bindings']);owners[ix]=incoming;au.update(free=old['free']-6,reserved=tuple(amounts),bindings=tuple(owners));commit();result='admitted'
   if ix==0:record('reserve',incoming)
 elif k=='foreign-release':result='owner-refused'
 elif k=='intent':
  if old['reserved'][0]!=6 or old['intent']:result='unavailable'
  else:au['intent']=True;commit()
 elif k in ('send','resend'):
  if old['intent'] and old['sent']==0 and old['reserved'][0]==6:au['sent']=1;commit()
  else:result='ambiguous-or-unavailable'
 elif k=='remote':
  if old['sent']>0 and old['remote']==0:au['remote']=remote_result
  else:result='unavailable'
 elif k=='lose':result='unknown' if old['remote'] else 'unavailable'
 elif k in ('query','query-wrong'):
  supplied=d.REQUESTS[0] if k=='query' else d.REQUESTS[1]
  if old['remote']==0:result='unknown'
  elif supplied!=old['bindings'][0]:result='receipt-binding-conflict'
  else:au['receipt']=old['remote'];au['receipt_binding']=supplied;commit()
 elif k=='classify':
  if old['receipt']==0:result='unknown'
  else:au['classification']=old['receipt']
 elif k=='conflict':au['conflict']=True
 elif k=='reconcile':
  if old['classification']==0 or old['conflict'] or old['reserved'][0]==0:result='held-or-duplicate'
  else:
   au['reserved']=(0,old['reserved'][1]);commit()
   if old['classification']==2:au['free']=old['free']+old['reserved'][0]
   else:au['consumed']=(old['consumed'][0]+old['reserved'][0],old['consumed'][1])
   if all(row[0]!='settlement' for row in old['catalog']):record('settlement',old['bindings'][0],effect=old['classification'])
 elif k=='consult':
  if old['stopped'] or old['bindings'][0]==():result='unavailable'
  else:
   au['alias_active']=True;au['request']=tuple(['consultA',*(old['tokens'][x] for x in ('goal','lease','process','delivery')),'contextA','adviceA','head','consultant','grantA',old['bindings'][0]])
 elif k=='wait-held':
  if old['request'] and old['executor']=='head':au['wait']=(('head','consultA'),('consultA','executor'),('executor','head'));result='blocked-dependency'
  else:result='unavailable'
 elif k=='suspend':
  if not old['request']:result='unavailable'
  else:
   au['wait']=()
   if old['executor']=='head':au.update(executor='free',executor_binding=())
 elif k=='start':
  if old['executor']=='free' and valid(old,old['request']):au.update(started=True,executor='consultA',executor_binding=(old['request'][2],old['request'][3]))
  else:result='authority-or-executor'
 elif k in ('reply','reply-wrong'):
  if old['reply'] or not old['started']:result='unavailable'
  else:
   packet=list(old['request']);packet[0]='consultB' if k=='reply-wrong' else packet[0];au['reply']=tuple(packet);record('advice',old['bindings'][0],au['reply'])
   if old['executor']=='consultA':au.update(executor='free',executor_binding=())
 elif k=='ingest':
  replies=[old['catalog'][ix-1] for ix in f['received'] if old['catalog'][ix-1][0]=='advice']
  if old['evidence']:result='duplicate'
  elif len(replies)==0:result='missing-delivery'
  elif replies[0][1]!=old['bindings'][0] or replies[0][2]!=old['request']:result='binding-conflict'
  elif not old['alias_active'] or replies[0][2][4]!=old['tokens']['delivery']:au['missing']=True;result='expired-delivery'
  else:au['evidence']=replies[0][2]
 elif k=='adopt':
  if old['adopted']:result='duplicate'
  elif valid(old,old['evidence']):au['adopted']=old['evidence'];au['adoptions']=1
  else:result='stale-or-missing'
 elif k=='wake':
  if old['wakes']>0:result='duplicate'
  elif not valid(old,old['adopted']):result='stale-or-missing'
  elif old['executor']!='free':result='executor-unavailable'
  else:au.update(wakes=1,executor='head',executor_binding=(old['adopted'][2],old['adopted'][3]))
 elif k in ('lease','goal'):au['tokens'][k]=d.token(k,2)
 elif k=='expire':au['tokens']['delivery']=d.token('delivery',2);au['alias_active']=False
 elif k=='stop-request':
  if old['control']==0:au['control']=1
  else:result='duplicate'
 elif k=='stop-apply':
  if old['control']==1:au.update(control=2,stopped=True,alias_active=False);au['tokens']['delivery']=d.token('delivery',2)
  else:result='unavailable'
 elif k=='cancel':
  if old['stopped']:au['cancelled']=True
  else:result='unavailable'
 elif k=='unrelated':
  if old['unrelated']=='active-local':au['unrelated']='completed-local'
  else:result='unavailable'
 elif k=='restart':
  au['tokens']['process']=d.token('process',2);vi['replay_cursor']=0
  if old['executor']=='head':au.update(executor='free',executor_binding=(),wait=())
 elif k=='replay':vi['replay_cursor']=old['revision']
 elif k=='quota':au.update(quota_epoch=1,quota_used=0)
 elif k=='exit':au['worker_exited']=True
 elif k=='compute':
  if old['tokens']['process'][4]==2 and old['lifetime'][1]==0:au.update(lifetime=(old['lifetime'][0],1),quota_used=old['quota_used']+1)
  else:result='unavailable'
 elif k=='publish':au['generation']=2
 elif k=='capture':vi.update(snapshot=(1,0,10,(0,0),(0,0),1),pin=True)
 elif k=='copy':
  if v['snapshot']:vi['copied']=True
  else:result='unavailable'
 elif k=='pin-release':
  if v['copied']:vi['pin']=False
  else:result='unavailable'
 elif k=='offer':
  if f['offered']==len(old['catalog']) or len(f['retained'])==2 or f['quarantine'] or f['frame']:result='backpressure-or-unavailable'
  else:fl['offered']=f['offered']+1;fl['retained']=tuple([*f['retained'],fl['offered']])
 elif k=='pump-source':
  if f['retained'] and not f['channels'][0] and sum(len(q) for q in f['channels'])<2:fl['retained']=f['retained'][1:];fl['channels']=((f['retained'][0],),f['channels'][1],f['channels'][2])
  else:result='backpressure-or-unavailable'
 elif k in ('pump-sdk','pump-broker'):
  ix={'pump-sdk':0,'pump-broker':1}[k];rows=list(f['channels'])
  if rows[ix] and not rows[ix+1]:rows[ix+1]=(rows[ix][0],);rows[ix]=rows[ix][1:];fl['channels']=tuple(rows)
  else:result='backpressure-or-unavailable'
 elif k=='evict':
  places=tuple(f['retained'])+tuple(x for q in f['channels'] for x in q)
  if f['loss']==0 and 1 in places:fl.update(loss=1,retained=tuple(x for x in f['retained'] if x!=1),channels=tuple(tuple(x for x in q if x!=1) for q in f['channels']))
  else:result='unavailable'
 elif k=='hello':
  if f['phase']==0 and f['loss']==1 and f['covered']==0 and f['wire_sent']==0 and v['snapshot'] and v['copied']:fl['phase']=1;m=d.hello(0,unit)
  else:result='unavailable'
 elif k=='welcome':
  if f['phase']!=1:result='unavailable'
  else:fl['phase']=2;m=d.msg('WELCOME',client_id='client-a',replay_floor=d.cursor(1,unit),snapshot_cursor=d.cursor(1,unit),cursor_unit=unit,input_lease=None,resize_lease=None,capabilities=['attach'])
 elif k=='reset':
  if f['phase']!=2:result='unavailable'
  else:fl.update(phase=3,covered=1,wire_sent=1,pending=(),acknowledged=1,byte_credit=0,event_credit=0);m=d.msg('RESET',client_id='client-a',reason='gap',snapshot_cursor=d.cursor(1,unit),cursor_unit=unit)
 elif k=='install':
  if f['phase']==3 and v['copied']:vi['installed']=v['snapshot'];vi['installed_cursor']=1
  else:result='unavailable'
 elif k.startswith('credit:'):
  amount=int(k.partition(':')[2])
  if f['phase']==2 or f['grants']==4:result='unavailable'
  else:fl.update(grants=f['grants']+1,byte_credit=f['byte_credit']+amount,event_credit=f['event_credit']+1);m=d.msg('CREDIT',client_id='client-a',bytes=amount,events=1)
 elif k=='emit':
  ix=f['channels'][2][0] if f['channels'][2] else 0
  def fits(ids):return len(ids)+1<=2 and sum(d.COSTS[j-1] for j in ids)+(d.COSTS[ix-1] if ix else 0)<=2
  if ix==0 or ix!=f['wire_sent']+1 or f['phase']==2 or (f['covered'] and v['installed_cursor']!=f['covered']) or f['byte_credit']<d.COSTS[ix-1] or f['event_credit']==0 or not fits(f['pending']) or not fits(f['delivery']):result='backpressure-or-unavailable'
  else:
   fl.update(channels=(f['channels'][0],f['channels'][1],f['channels'][2][1:]),wire_sent=ix,delivered=(*f['delivered'],ix),pending=(*f['pending'],ix),delivery=(*f['delivery'],ix),byte_credit=f['byte_credit']-d.COSTS[ix-1],event_credit=f['event_credit']-1)
   m=d.msg('EVENT',cursor=d.cursor(ix,unit),cursor_unit=unit,event_class='output',process_id='process-a',payload_base64=base64.b64encode(d.TOKENS[ix-1]).decode(),payload_untrusted=True)
 elif k=='receive':
  if f['delivery']:fl.update(received=(*f['received'],f['delivery'][0]),delivery=f['delivery'][1:])
  else:result='unavailable'
 elif k=='ack':
  if f['pending'] and f['phase']!=2:fl.update(pending=(),acknowledged=f['wire_sent']);m=d.msg('ACK',client_id='client-a',cursor=d.cursor(f['wire_sent'],unit),cursor_unit=unit)
  else:result='unavailable'
 elif k=='lose-ack':result='lost'
 elif k=='fragment':
  if f['quarantine'] or f['frame']==2:result='bounded-refusal'
  else:fl['frame']=f['frame']+1
 elif k=='framing-fault':
  if f['frame']>0:fl.update(frame=0,quarantine=True)
  else:result='unavailable'
 else:raise ValueError(k)
 if m is not None:fl['wire']=(*f['wire'],d.canonical(m))
 vi.update(done=v['done']|(1<<profile['actions'].index(action)),decision=k+':'+result)
 return d.Split(au,fl,vi)
