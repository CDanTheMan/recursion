"""Separated authority/flow/view extension. Does not call inclusive code."""
import copy
import p_domain as d,p_literal as lit
import c_split as base

def step(state,action,profile,unit,outcome):
 au,fl,vi=copy.deepcopy(state);s=state.authority;k=action.partition('@')[0];decision='ok';delegate=False
 if k=='pause':au.update(paused=True,pause_epoch=('pause','owner','runtime-admission',2))
 elif k=='source-later':
  if s['reserved'][0]!=6:decision='unavailable'
  else:au['source_version']=2
 elif k.startswith('cut:'):
  name=k.partition(':')[2]
  if name=='terminal':name={1:'success',2:'failure'}[outcome]
  if s['remote']==0:decision='no-retained-source'
  elif s['cut_delivery']!='' or s['cut_offer']!='':decision='cut-backpressure'
  else:au['cut_offer']=name
 elif k=='cut-deliver':
  if s['cut_delivery']=='' and s['cut_offer']!='':au.update(cut_delivery=s['cut_offer'],cut_offer='')
  else:decision='unavailable'
 elif k=='cut-receive':
  if s['cut_delivery']=='':decision='unavailable'
  else:
   name=s['cut_delivery'];au.update(cut_received=name,cut_delivery='',joined_cut='',classified_cut='');au['source_version']=max(lit.fixture(name)['binding']['body']['source_version'],s['source_version'])
 elif k=='join-cut':
  if s['cut_received']=='':decision='missing-cut'
  else:
   candidate=lit.evaluate(s['cut_received'])
   if candidate['accepted'] is False:decision='join-rejected'
   elif list(s['bindings'][0])!=candidate['binding']['reservation']:decision='reservation-binding'
   else:au['joined_cut']=s['cut_received']
 elif k=='classify':
  if s['joined_cut']=='':decision='unjoined'
  else:
   r=lit.evaluate(s['joined_cut']);value=r['joined']['current']['status'];au.update(classified_cut=s['joined_cut'],cut_status=value,cut_hold=r['joined']['runtime_settlement_hold'],nonexecution=r['binding']['terminal_nonexecution'])
   if s['reserved'][0]==6:au['classification']={'succeeded':1,'reconciled-succeeded':1,'failed':2,'reconciled-failed':2}.get(value,0)
 elif k=='observe' or k=='observe-conflict':
  if s['joined_cut']=='':decision='unjoined'
  else:
   au['receipt_journal']+=1
   value=lit.evaluate(s['joined_cut'])['joined']['observation_digest']
   if k=='observe-conflict':value+='changed'
   if s['observation_receipt']!='':
    if value==s['observation_payload']:decision='duplicate'
    else:decision='E-IDEMPOTENCY-CONFLICT';au['refusal_journal']+=1
   elif s['paused']:decision='E-PAUSED';au['refusal_journal']+=1
   else:
    decision='accepted';au.update(runtime_observations=s['runtime_observations']+1,observation_receipt='accepted',observation_payload=value)
    au['canonical_quarantine']=s['canonical_quarantine'] or lit.fixture(s['joined_cut'])['original']['cut']['context']['observation']['payload']['quarantine']
 elif k=='reconcile':
  if s['paused']:decision='E-PAUSED'
  elif s['classified_cut']=='' or s['joined_cut']!=s['classified_cut']:decision='unclassified'
  else:
   evidence=lit.evaluate(s['classified_cut'])
   if evidence['binding']['source_version']!=s['source_version']:decision='stale-cut'
   elif s['cut_hold'] or evidence['joined']['current']['reasons']:decision='evidence-hold'
   elif s['canonical_quarantine']:decision='canonical-hold'
   elif s['classification']==2 and s['nonexecution'] is False:decision='nonexecution-unproved'
   else:delegate=True
 elif s['paused'] and k in ('admitA','admitB','duplicateA','wrong-owner','wrong-payload') and not s['bindings'][1 if k=='admitB' else 0]:decision='E-PAUSED'
 elif s['paused'] and k in ('intent','send','resend','consult','start','adopt','wake','query','query-wrong'):decision='E-PAUSED'
 else:delegate=True
 if delegate:
  previous=d.base.split(d.project(d.flatten(state)));b=d.base.flatten(base.step(previous,action,profile,unit,outcome));au.update({x:b[x] for x in d.base.AUTH});fl.update({x:b[x] for x in d.base.FLOW});vi.update({x:b[x] for x in d.base.VIEW})
 else:vi.update(done=state.view['done']|(1<<profile['actions'].index(action)),decision=k+':'+decision)
 return d.Split(au,fl,vi)
