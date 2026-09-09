"""Inclusive extension. Uses only its own frozen predecessor reducer."""
import copy
import p_domain as d,p_literal as lit
import c_inclusive as base
SENSITIVE={'intent','send','resend','consult','start','adopt','wake','query','query-wrong'}
def step(s,a,p,u,outcome,mutant=None):
 k=a.split('@')[0];n=copy.deepcopy(s);n.update(done=s['done']|(1<<p['actions'].index(a)),decision=k+':ok')
 def deny(x):n['decision']=k+':'+x
 if k=='pause':n['paused']=True;n['pause_epoch']=('pause','owner','runtime-admission',2)
 elif k=='source-later':
  if s['reserved'][0]==6:n['source_version']=2
  else:deny('unavailable')
 elif k.startswith('cut:'):
  name=k[4:];name=('success' if outcome==1 else 'failure') if name=='terminal' else name
  if not s['remote']:deny('no-retained-source')
  elif s['cut_offer'] or s['cut_delivery']:deny('cut-backpressure')
  else:n['cut_offer']=name
 elif k=='cut-deliver':
  if s['cut_offer'] and not s['cut_delivery']:n['cut_delivery']=s['cut_offer'];n['cut_offer']=''
  else:deny('unavailable')
 elif k=='cut-receive':
  if s['cut_delivery']:
   n['cut_received']=s['cut_delivery'];n['cut_delivery']='';n['joined_cut']='';n['classified_cut']=''
   n['source_version']=max(s['source_version'],lit.fixture(n['cut_received'])['binding']['body']['source_version'])
  else:deny('unavailable')
 elif k=='join-cut':
  if not s['cut_received']:deny('missing-cut')
  else:
   row=lit.evaluate(s['cut_received']);b=row['binding']
   if not row['accepted'] and mutant!='join-validation':deny('join-rejected')
   elif tuple(b['reservation'])!=s['bindings'][0] and mutant!='cut-owner':deny('reservation-binding')
   else:n['joined_cut']=s['cut_received']
 elif k=='classify':
  if not s['joined_cut']:deny('unjoined')
  else:
   row=lit.evaluate(s['joined_cut']);r=row['joined'];status=r['current']['status']
   n.update(classified_cut=s['joined_cut'],cut_status=status,cut_hold=r['runtime_settlement_hold'],nonexecution=row['binding']['terminal_nonexecution'])
   if s['reserved'][0]:n['classification']=1 if status in ('succeeded','reconciled-succeeded') else 2 if status in ('failed','reconciled-failed') else 0
   if mutant=='classify-release':n['free']+=s['reserved'][0];n['reserved']=(0,s['reserved'][1])
   if mutant=='classification-write':n['runtime_observations']+=1
 elif k in ('observe','observe-conflict'):
  if not s['joined_cut']:deny('unjoined')
  else:
   n['receipt_journal']+=1
   payload=lit.evaluate(s['joined_cut'])['joined']['observation_digest']+('changed' if k=='observe-conflict' else '')
   if s['observation_receipt'] and payload!=s['observation_payload']:deny('E-IDEMPOTENCY-CONFLICT');n['refusal_journal']+=1
   elif s['observation_receipt']:
    deny('duplicate')
    if mutant=='duplicate-observation':n['runtime_observations']+=1
   elif s['paused'] and mutant!='pause-observation':deny('E-PAUSED');n['refusal_journal']+=1
   else:
    n['runtime_observations']+=1;n['observation_receipt']='accepted';n['observation_payload']=payload;deny('accepted')
    if lit.fixture(s['joined_cut'])['original']['cut']['context']['observation']['payload']['quarantine']:n['canonical_quarantine']=True
 elif k=='reconcile':
  row=lit.evaluate(s['classified_cut']) if s['classified_cut'] else None
  if s['paused'] and mutant!='pause-settle':deny('E-PAUSED')
  elif not row or s['classified_cut']!=s['joined_cut']:deny('unclassified')
  elif row['binding']['source_version']!=s['source_version'] and mutant!='cut-freshness':deny('stale-cut')
  elif (s['cut_hold'] or row['joined']['current']['reasons']) and mutant!='cut-hold':deny('evidence-hold')
  elif s['canonical_quarantine'] and mutant!='quarantine':deny('canonical-hold')
  elif s['classification']==2 and not s['nonexecution'] and mutant!='nonexecution':deny('nonexecution-unproved')
  else:n.update(base.step(d.project(s),a,p,u,outcome,mutant))
 elif k in ('admitA','admitB','duplicateA','wrong-owner','wrong-payload') and s['paused'] and not s['bindings'][int(k=='admitB')] and mutant!='pause-admission':deny('E-PAUSED')
 elif k in SENSITIVE and s['paused'] and mutant!='pause-permit':deny('E-PAUSED')
 else:n.update(base.step(d.project(s),a,p,u,outcome,mutant))
 return n
