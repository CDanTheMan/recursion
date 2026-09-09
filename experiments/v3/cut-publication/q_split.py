"""Independent separated publication authority, retained transport and view reducer."""
import copy,json
import q_domain as d
import p_split as old

def step(state,action,profile,unit,outcome):
 au,fl,vi=copy.deepcopy(state);s=state.authority;k=action.partition('@')[0];why='ok';delegate=False
 if k in ('authority-restart','publisher-revoke','source-restart'):
  if k=='authority-restart':au['publisher_boot']=s['publisher_boot']+1
  elif k=='publisher-revoke':au['publisher_serial']=s['publisher_serial']+1
  else:au['source_generation']=d.source_token(s['source_generation'][-1]+1)
 elif k=='source-attest' or k.startswith('source:'):
  name=s['cut_delivery'] if k=='source-attest' else k[7:]
  if name=='' or s['remote']==0:why='no-source'
  else:
   before=d.record_ids(s['source_name']) if s['source_name'] else ();after=d.record_ids(name)
   if list(s['bindings'][0])!=d.lit.fixture(name)['binding']['body']['reservation']:why='foreign-source'
   elif s['source_name'] and (d.scope(s['source_name'])!=d.scope(name) or after[:len(before)]!=before):why='source-fork'
   else:au.update(source_name=name,source_head=d.head(name),source_generation=s['source_generation'] if s['source_name'] else d.source_token(1),source_version=max(s['source_version'],d.lit.fixture(name)['binding']['body']['source_version']))
 elif k=='stage' or k.startswith('stage-'):
  if s['cut_delivery']=='':why='no-delivered-cut'
  else:au['staged']=d.candidate(s,'normal' if k=='stage' else k[6:]);au['stage_serial']=s['stage_serial']+1
 elif k in ('pub-commit','pub-rival','pub-retry','pub-retry-conflict','pub-retry-foreign'):
  if not s['staged'] and not s['publication_receipts']:why='unstaged'
  else:
   env,payload=d.incoming(s,k);rows=[r for r in s['publication_receipts'] if r[0].request==env.request]
   if k=='pub-retry-foreign':why='wrong-caller'
   elif rows:
    previous=rows[0]
    if d.canonical(env)==d.canonical(previous[0]):au.update(publication_reply=previous[1],publication_reads=s['publication_reads']+1);why='duplicate'
    else:why='E-IDEMPOTENCY-CONFLICT'
   else:
    checks=[(not s['paused'],'E-PAUSED'),(env.principal=='collectorA' and env.permit[2]=='collectorA','wrong-owner'),(env.permit[:2]==('cut-publish','authority'),'wrong-domain'),(d.canonical(env.permit[3])==d.canonical(('publisher-boot','authority',s['publisher_boot'])),'stale-boot'),(type(env.permit[4]) is int and env.permit[4]==s['publisher_serial'],'stale-permit'),(env.signature==d.sign(env).signature,'bad-authentication'),(type(env.expected_revision) is int and env.expected_revision==s['publication_revision'] and env.parent==(s['selected'].generation if s['selected'] else ''),'stale-parent'),(payload==d.raw_cut(env.cut) and d.digest(json.loads(payload))==env.content,'bad-content'),(env.inventory==d.record_ids(env.cut),'bad-inventory'),(bool(s['source_name']) and tuple(d.lit.fixture(env.cut)['binding']['body']['reservation'])==s['bindings'][0] and d.scope(env.cut)==d.scope(s['source_name']),'foreign-publication'),(d.canonical(env.source_generation)==d.canonical(s['source_generation']),'stale-source-generation'),(env.source_head==d.head(env.cut) and env.source_head==s['source_head'],'stale-source-head'),(all(row[0].generation!=env.generation for row in s['publication_store']),'generation-used')]
    why=next((reason for valid,reason in checks if not valid),'ok')
    if why=='ok':
     revision=s['publication_revision']+1;receipt=(env.request,d.digest(env),revision,env.generation,env.content)
     au.update(selected=env,publication_revision=revision,publication_store=s['publication_store']+((env,payload),),publication_receipts=s['publication_receipts']+((env,receipt),),publication_reply=receipt,cut_delivery='')
 elif k=='pub-lose-reply':au['publication_reply']=()
 elif k.startswith('reader-'):
  verb,slot=k.split(':');i=int(slot);pin=s['reader_pins'][i];owner=('reader'+slot,s['reader_nonce'][i])
  if verb=='reader-request':
   if not s['selected']:why='no-selection'
   else:au['reader_requests']=d.replace_at(s['reader_requests'],i,(owner,s['selected']))
  elif verb=='reader-pin':
   pending=s['reader_requests'][i]
   if not pending or pin:why='no-fresh-request'
   elif pending[0]!=owner:why='stale-reader'
   elif pending[1]!=s['selected']:why='stale-selection'
   elif all(x[0]!=pending[1] for x in s['publication_store']):why='retired'
   else:au['reader_pins']=d.replace_at(s['reader_pins'],i,pending);au['reader_waited']=d.replace_at(s['reader_waited'],i,False)
  elif verb in ('reader-copy','reader-wait'):
   if not pin or pin[0]!=owner:why='no-owned-pin'
   elif verb=='reader-wait':au['reader_waited']=d.replace_at(s['reader_waited'],i,True)
   else:
    matching=[row for row in s['publication_store'] if row[0]==pin[1]]
    if not matching:why='retired'
    else:au['reader_copies']=d.replace_at(s['reader_copies'],i,matching[0])
  elif verb in ('reader-release','reader-release-foreign'):
   if not pin or pin[0]!=owner or verb=='reader-release-foreign':why='no-owned-pin'
   elif not s['reader_waited'][i]:why='reader-live'
   else:au['reader_pins']=d.replace_at(s['reader_pins'],i,())
  elif verb=='reader-restart':au['reader_nonce']=d.replace_at(s['reader_nonce'],i,s['reader_nonce'][i]+1)
  elif verb in ('reader-install','reader-install-corrupt'):
   record=s['reader_copies'][i]
   if not record:why='no-copy'
   else:
    env,payload=record
    if verb=='reader-install-corrupt':payload=payload.replace('ownerA','ownerB')
    if payload!=d.raw_cut(env.cut) or d.digest(json.loads(payload))!=env.content or env.inventory!=d.record_ids(env.cut):why='copy-mismatch'
    else:au.update(installed_cut=(env,payload),cut_received=env.cut,joined_cut='',classified_cut='',source_version=max(s['source_version'],d.lit.fixture(env.cut)['binding']['body']['source_version']))
  else:raise ValueError('undeclared reader verb')
 elif k=='reclaim':
  old_generations=[x for x in s['publication_store'] if x[0]!=s['selected']]
  if not old_generations:why='no-retired-generation'
  else:
   item=old_generations[0]
   if any(pin and pin[1]==item[0] for pin in s['reader_pins']):why='reader-pinned'
   else:au['publication_store']=tuple(x for x in s['publication_store'] if x!=item);au['retired_cuts']=s['retired_cuts']+(item[0].generation,)
 elif k=='cut-receive':why='publication-required'
 elif k=='reconcile':
  current=s['installed_cut']
  if not current or current[0]!=s['selected'] or current[0].source_head!=s['source_head'] or current[0].source_generation!=s['source_generation']:why='current-publication-required'
  else:delegate=True
 else:delegate=True
 if delegate:
  before=d.base.split(d.project(d.flatten(state)));after=d.base.flatten(old.step(before,action,profile,unit,outcome))
  au.update({x:after[x] for x in d.base.AUTH});fl.update({x:after[x] for x in d.base.FLOW});vi.update({x:after[x] for x in d.base.VIEW})
 else:vi.update(done=state.view['done']|(1<<profile['actions'].index(action)),decision=k+':'+why)
 return d.Split(au,fl,vi)
