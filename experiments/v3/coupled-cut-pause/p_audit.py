"""Third independent complete extension relation and invariants; no reducer imports."""
import copy
import p_domain as d,p_literal as lit
import c_audit as base
fresh=base.fresh;authoritative=base.authoritative;enabled=base.enabled
NEGATIVE={'missing-original','contradictory','omitted','reordered','bad-mac','wrong-role','bad-attempt-map','missing-attempt-map','bad-source-version','bool-source-version'}
def facts(name):
 # Hand-stated expectations independently projected from original retained inputs.
 x=lit.fixture(name);body=x['binding']['body'];source=name if name in lit.cases.EXPECTED else ('failure' if name=='generic-failure' else 'success')
 historical,current,reasons=lit.cases.EXPECTED[source]
 starts=[r for r in x['original']['records'] if r['type']=='AttemptStarted@1']
 expected_map=[[body['reservation'][3] if r['attempt_number']==1 else 'retained-attemptA'+str(r['attempt_number']),r['attempt_id']] for r in starts]
 mapping_ok=body['attempt_mapping']==expected_map
 expected_version=2 if x['original']['cut']['prefix_length']<len(x['original']['records']) else 1
 version_ok=type(body['source_version']) is int and body['source_version']==expected_version
 pending={'ambiguous':('attempt:1',),'unverified':('attempt:1',),'prior-unresolved':('attempt:1',),'later-unresolved':('attempt:2',),'later-start-only':('attempt:2',)}.get(source,())
 return dict(accepted=name not in NEGATIVE and mapping_ok and version_ok,binding=tuple(body['reservation']),status=current,hold=bool(pending) or current=='ambiguous',reasons=reasons,version=body['source_version'],nonexecution=source=='failure' and name!='generic-failure',payload=x['original']['cut']['context']['observation']['content_digest'],quarantine=x['original']['cut']['context']['observation']['payload']['quarantine'])
def initialization(s,u):
 base.initialization(d.project(s),u)
 expected=dict(paused=False,pause_epoch=('pause','owner','runtime-admission',1),plan_accepted=True,cut_offer='',cut_delivery='',cut_received='',joined_cut='',classified_cut='',source_version=1,cut_status='',cut_hold=True,runtime_observations=0,observation_receipt='',observation_payload='',refusal_journal=0,receipt_journal=0,canonical_quarantine=False,nonexecution=False)
 d.require({k:s[k] for k in d.EXTRA}==expected,'complete independent extension initialization');invariant(s)
def invariant(s):
 base.invariant(d.project(s));d.require(s['source_version'] in (1,2) and type(s['paused']) is bool,'cut/admission types')
 d.require(s['pause_epoch']==('pause','owner','runtime-admission',2 if s['paused'] else 1),'separate pause epoch domain')
 for k in ('cut_offer','cut_delivery','cut_received','joined_cut','classified_cut'):d.require(s[k]=='' or s[k] in lit.NAMES,'actual finite cut identity '+k)
 if s['joined_cut']:
  f=facts(s['joined_cut']);d.require(f['accepted'] and f['binding']==s['bindings'][0],'complete authentic cut owns actual reservation')
 d.require(s['runtime_observations'] in (0,1) and s['refusal_journal']>=0,'observation command idempotence/journal')
 if s['classified_cut']:
  f=facts(s['classified_cut']);d.require(s['cut_status']==f['status'] and s['cut_hold']==f['hold'] and s['nonexecution']==f['nonexecution'],'literal status distinct from hold/nonexecution')
def check(s,a,n,p,u,outcome):
 d.require(a in enabled(s,p),'complete extension enabledness');k=a.split('@')[0];changes={};reason='ok';delegated=False
 if k=='pause':changes.update(paused=True,pause_epoch=('pause','owner','runtime-admission',2))
 elif k=='source-later':
  if s['reserved'][0]==6:changes['source_version']=2
  else:reason='unavailable'
 elif k.startswith('cut:'):
  name=k[4:] if k!='cut:terminal' else ('success' if outcome==1 else 'failure')
  if s['remote']==0:reason='no-retained-source'
  elif s['cut_offer']!='' or s['cut_delivery']!='':reason='cut-backpressure'
  else:changes['cut_offer']=name
 elif k=='cut-deliver':
  if s['cut_offer'] and not s['cut_delivery']:changes.update(cut_offer='',cut_delivery=s['cut_offer'])
  else:reason='unavailable'
 elif k=='cut-receive':
  if s['cut_delivery']:changes.update(cut_received=s['cut_delivery'],cut_delivery='',joined_cut='',classified_cut='',source_version=max(s['source_version'],facts(s['cut_delivery'])['version']))
  else:reason='unavailable'
 elif k=='join-cut':
  if not s['cut_received']:reason='missing-cut'
  elif not facts(s['cut_received'])['accepted']:reason='join-rejected'
  elif facts(s['cut_received'])['binding']!=s['bindings'][0]:reason='reservation-binding'
  else:changes['joined_cut']=s['cut_received']
 elif k=='classify':
  if not s['joined_cut']:reason='unjoined'
  else:
   f=facts(s['joined_cut']);changes.update(classified_cut=s['joined_cut'],cut_status=f['status'],cut_hold=f['hold'],nonexecution=f['nonexecution'])
   if s['reserved'][0]==6:changes['classification']={'succeeded':1,'reconciled-succeeded':1,'failed':2,'reconciled-failed':2}.get(f['status'],0)
 elif k in ('observe','observe-conflict'):
  if not s['joined_cut']:reason='unjoined'
  else:
   changes['receipt_journal']=s['receipt_journal']+1
   f=facts(s['joined_cut']);payload=f['payload']+('changed' if k=='observe-conflict' else '')
   if s['observation_receipt'] and s['observation_payload']!=payload:reason='E-IDEMPOTENCY-CONFLICT';changes['refusal_journal']=s['refusal_journal']+1
   elif s['observation_receipt']:reason='duplicate'
   elif s['paused']:reason='E-PAUSED';changes['refusal_journal']=s['refusal_journal']+1
   else:reason='accepted';changes.update(runtime_observations=s['runtime_observations']+1,observation_receipt='accepted',observation_payload=payload,canonical_quarantine=s['canonical_quarantine'] or f['quarantine'])
 elif k=='reconcile':
  if s['paused']:reason='E-PAUSED'
  elif not s['classified_cut'] or s['classified_cut']!=s['joined_cut']:reason='unclassified'
  elif facts(s['classified_cut'])['version']!=s['source_version']:reason='stale-cut'
  elif s['cut_hold'] or facts(s['classified_cut'])['reasons']:reason='evidence-hold'
  elif s['canonical_quarantine']:reason='canonical-hold'
  elif s['classification']==2 and not s['nonexecution']:reason='nonexecution-unproved'
  else:delegated=True
 elif k in ('admitA','admitB','duplicateA','wrong-owner','wrong-payload') and s['paused'] and s['bindings'][int(k=='admitB')]==():reason='E-PAUSED'
 elif k in ('intent','send','resend','consult','start','adopt','wake','query','query-wrong') and s['paused']:reason='E-PAUSED'
 else:delegated=True
 if delegated:
  base.check(d.project(s),a,d.project(n),p,u,outcome)
  d.require(all(n[k]==s[k] for k in d.EXTRA),'unchanged action extension frame')
 else:
  expected=copy.deepcopy(s);expected.update(changes,done=s['done']|(1<<p['actions'].index(a)),decision=k+':'+reason);d.require(n==expected,'complete independent extension postcondition '+k)
 invariant(n)
 if k in ('classify','join-cut','cut-deliver','cut-receive') or k.startswith('cut:'):
  for field in ('free','reserved','consumed','revision','runtime_observations','receipt_journal','canonical_quarantine','sent'):d.require(n[field]==s[field],'pure retained evidence cannot authorize write '+field)
 if s['canonical_quarantine']:d.require(n['canonical_quarantine'],'canonical quarantine is not cleared by evidence')
 if n['reserved'][0]<s['reserved'][0]:d.require(not s['paused'] and not s['cut_hold'] and not s['canonical_quarantine'] and s['classified_cut'] and facts(s['classified_cut'])['version']==s['source_version'],'settlement independent current-cut authority')
 if s['paused']:d.require(n['runtime_observations']==s['runtime_observations'] and n['sent']==s['sent'],'PAUSE closes new runtime writes and permits')

 # Literal coupled observation correspondence, using this exact joined source payload.
 if k in ('observe','observe-conflict') and s['joined_cut']:
  previous=next((name for name in lit.NAMES if lit.fixture(name)['original']['cut']['context']['observation']['content_digest']==s['observation_payload']), '') if s['observation_receipt'] else ''
  actual=lit.observation(s['joined_cut'],s['paused'],previous,k=='observe-conflict')
  d.require(len(actual['events'])==n['runtime_observations']-s['runtime_observations'],'actual joined observation event count')
  d.require(actual['journal_growth']==n['receipt_journal']-s['receipt_journal']==1,'literal receipt journal includes exact duplicates')
  if n['decision'].endswith('E-PAUSED'):d.require(actual['receipt']['primary_error']=='E-PAUSED' and actual['projection_unchanged'] and actual['journal_growth']==1,'actual otherwise-valid joined PAUSE refusal')
  elif n['decision'].endswith('E-IDEMPOTENCY-CONFLICT'):d.require(actual['receipt']['primary_error']=='E-IDEMPOTENCY-CONFLICT' and actual['projection_unchanged'],'actual same command payload conflict')
  else:d.require(actual['receipt']['disposition']=='accepted','actual joined observation/duplicate admitted')
  if n['decision'].endswith('duplicate'):d.require(actual['projection_unchanged'] and not actual['events'],'literal old receipt creates no new event')
