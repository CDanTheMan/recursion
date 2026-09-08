"""Split authority/transport-resource implementation; no inclusive transition reuse."""
import copy
import epoch_domain as d

def authorized(authority,binding):
 if binding is None or authority['request'] is None or authority['stopped'] or not authority['alias_active']:return False
 if any(not isinstance(v,tuple) or len(v)!=6 or type(v[4]) is not int for v in binding[1:5]):return False
 expected=authority['request']
 if binding!=expected:return False
 pairs=zip(binding[1:5],('goal','lease','process','delivery'))
 return all(value==authority['tokens'][tag] for value,tag in pairs)

def step(state,event):
 au,br=copy.deepcopy(state);br['done']=tuple(sorted(list(br['done'])+[event]));br['decision']=event+':accepted';tokens=au['tokens']
 def refuse(reason):br['decision']=event+':'+reason
 if event=='request':
  if au['stopped']:refuse('expired-operation')
  else:au['request']=tuple(['operation-a',*[tokens[k] for k in ('goal','lease','process','delivery')],'context-1','payload-1','head','consultant','grant-a']);au['input_request']=au['request'];au['alias_active']=True
 elif event=='duplicate-request' or event=='conflict-request':
  if au['request'] is None:refuse('missing-request')
  else:
   packet=list(au['request']);packet[6]='payload-2' if event=='conflict-request' else packet[6];au['input_request']=tuple(packet)
   refuse('duplicate' if au['input_request']==au['request'] else 'payload-conflict')
 elif event=='wait-held':
  if au['request'] is None:refuse('missing-request')
  elif br['executor']=='head':
   br.update(wait='blocked-dependency',wait_graph=(('head','consultation-a'),('consultation-a','executor-e'),('executor-e','head')));refuse('blocked-dependency')
  else:br['wait']='waiting-released'
 elif event=='suspend':
  if au['request'] is None:refuse('missing-request')
  else:
   br['wait']='suspended';br['wait_graph']=()
   if br['executor']=='head':br['executor']='free';br['executor_binding']=None
 elif event=='start':
  if authorized(au,au['request']) and br['executor']=='free':br.update(started=True,executor='consultation-a',executor_binding=(au['request'][2],au['request'][3]))
  else:refuse('executor-unavailable' if authorized(au,au['request']) else 'stale-or-missing-authority')
 elif event=='reply':
  if br['started']:
   br['reply']=au['request']
   if br['executor']=='consultation-a':br['executor']='free';br['executor_binding']=None
  else:refuse('not-started')
 elif event in ('ingest','duplicate-reply'):
  if br['reply'] is None:refuse('missing-reply')
  elif au['evidence'] is not None:refuse('duplicate')
  elif not au['alias_active'] or br['reply'][4]!=tokens['delivery']:br['missing']=True;refuse('expired-delivery-missing')
  else:au['evidence']=br['reply']
 elif event in ('adopt','adopt-again'):
  if au['adopted'] is not None:refuse('duplicate')
  elif authorized(au,au['evidence']):au.update(adopted=au['evidence'],adoption_count=1)
  else:refuse('stale-or-missing-authority')
 elif event in ('wake','wake-again','relaunch'):
  if not authorized(au,au['adopted']):refuse('stale-or-missing-authority')
  elif au['wake_count']>0:refuse('duplicate')
  elif br['executor']=='free':au['wake_count']=1;br.update(executor='head',executor_binding=(au['adopted'][2],au['adopted'][3]),wait='none',wait_graph=())
  else:refuse('executor-unavailable')
 elif event.startswith('lease'):tokens['lease']=('lease','goal-a',tokens['lease'][2],'head',int(event[-1]),'lease-identity-'+event[-1])
 elif event=='issuer':
  old=tokens['lease'];tokens['lease']=(*old[:2],'kernel-b',*old[3:])
 elif event=='restart':
  tokens['process']=('process','goal-a','kernel-a','head',2,'process-identity-2')
  if br['executor']=='head':br.update(executor='free',executor_binding=None,wait='recovered',wait_graph=())
 elif event=='expire':au['alias_active']=False;tokens['delivery']=('delivery','operation-a','kernel-a','head',2,'delivery-identity-2')
 elif event=='stop':au['stopped']=True;au['alias_active']=False;tokens['delivery']=('delivery','operation-a','kernel-a','head',2,'delivery-identity-2')
 elif event=='cancel-deliver':
  if au['stopped']:br['cancel_delivered']=True
  else:refuse('not-stopped')
 elif event=='unrelated':
  if br['unrelated']=='active':br['unrelated']='completed'
  else:refuse('not-active')
 elif event=='owner-amend':tokens['goal']=('goal','goal-a','owner','head',2,'goal-identity-2');au['goal_record']=('goal-a',2,'goal-digest-2')
 elif event=='advice-amend':refuse('owner-authority-required')
 elif event=='wrong-domain':
  if br['reply'] is None:refuse('missing-reply')
  else:
   values=list(br['reply']);wrong=list(values[2]);wrong[0]='writer';values[2]=tuple(wrong);br['reply']=tuple(values)
 else:raise ValueError('unknown event')
 return d.Split(au,br)
