"""Independent inclusive publication reducer; only own immutable predecessor."""
import copy,json,hmac,hashlib
import q_domain as d
import p_inclusive as old

def step(s,a,p,u,outcome,mutant=None):
 k=a.split('@')[0];n=copy.deepcopy(s);n.update(done=s['done']|(1<<p['actions'].index(a)),decision=k+':ok')
 def deny(reason):n['decision']=k+':'+reason
 if k=='authority-restart':
  n['publisher_boot']+=1
  if mutant=='old-reader-rights':n['reader_pins']=((),())
 elif k=='publisher-revoke':n['publisher_serial']+=1
 elif k=='source-restart':n['source_generation']=d.source_token(s['source_generation'][-1]+1)
 elif k=='source-attest' or k.startswith('source:'):
  name=s['cut_delivery'] if k=='source-attest' else k.partition(':')[2]
  if not name or not s['remote']:deny('no-source')
  else:
   prior=d.record_ids(s['source_name']) if s['source_name'] else ();following=d.record_ids(name)
   compatible=not s['source_name'] or (d.scope(name)==d.scope(s['source_name']) and following[:len(prior)]==prior)
   if tuple(d.lit.fixture(name)['binding']['body']['reservation'])!=s['bindings'][0] and mutant!='source-scope':deny('foreign-source')
   elif not compatible and mutant!='source-prefix':deny('source-fork')
   else:
    n.update(source_name=name,source_head=d.head(name),source_generation=s['source_generation'] if s['source_name'] else d.source_token(1),source_version=max(s['source_version'],d.lit.fixture(name)['binding']['body']['source_version']))
 elif k=='stage' or k.startswith('stage-'):
  if not s['cut_delivery']:deny('no-delivered-cut')
  else:n.update(staged=d.candidate(s,k[6:] if k.startswith('stage-') else 'normal'),stage_serial=s['stage_serial']+1)
 elif k in ('pub-commit','pub-rival','pub-retry','pub-retry-conflict','pub-retry-foreign'):
  if not s['staged'] and not s['publication_receipts']:deny('unstaged')
  else:
   e,raw=d.incoming(s,k);previous=next((r for r in s['publication_receipts'] if r[0].request==e.request),None)
   if k=='pub-retry-foreign' and mutant!='duplicate-caller':deny('wrong-caller')
   elif previous:
    if d.canonical(previous[0])!=d.canonical(e) and mutant!='duplicate-body':deny('E-IDEMPOTENCY-CONFLICT')
    else:
     n.update(publication_reply=previous[1],publication_reads=s['publication_reads']+1);deny('duplicate')
     if mutant=='duplicate-reselect':n.update(selected=previous[0],publication_revision=s['publication_revision']+1)
   elif s['paused'] and mutant!='publication-pause':deny('E-PAUSED')
   elif (e.principal!='collectorA' or e.permit[2]!='collectorA') and mutant!='publisher-owner':deny('wrong-owner')
   elif (e.permit[:2]!=('cut-publish','authority')) and mutant!='publisher-domain':deny('wrong-domain')
   elif d.canonical(e.permit[3])!=d.canonical(('publisher-boot','authority',s['publisher_boot'])) and mutant!='publisher-boot':deny('stale-boot')
   elif (type(e.permit[4]) is not int or e.permit[4]!=s['publisher_serial']) and mutant!='publisher-serial':deny('stale-permit')
   elif e.signature!=d.sign(e).signature and mutant!='publication-signature':deny('bad-authentication')
   elif (type(e.expected_revision) is not int or e.expected_revision!=s['publication_revision'] or e.parent!=(s['selected'].generation if s['selected'] else '')) and mutant!='publication-parent':deny('stale-parent')
   elif (raw!=d.raw_cut(e.cut) or d.digest(json.loads(raw))!=e.content) and mutant!='publication-content':deny('bad-content')
   elif e.inventory!=d.record_ids(e.cut) and mutant!='publication-inventory':deny('bad-inventory')
   elif d.canonical(e.source_generation)!=d.canonical(s['source_generation']) and mutant!='source-generation':deny('stale-source-generation')
   elif (e.source_head!=d.head(e.cut) or e.source_head!=s['source_head']) and mutant!='source-head':deny('stale-source-head')
   elif any(x[0].generation==e.generation for x in s['publication_store']):deny('generation-used')
   else:
    revision=s['publication_revision']+1;receipt=(e.request,d.digest(e),revision,e.generation,e.content)
    n.update(selected=e,publication_revision=revision,publication_store=s['publication_store']+((e,raw),),publication_receipts=s['publication_receipts']+((e,receipt),),publication_reply=receipt,cut_delivery='')
    if mutant=='receipt-durability':n['publication_receipts']=s['publication_receipts']
 elif k=='pub-lose-reply':n['publication_reply']=()
 elif k.startswith('reader-'):
  kind,index=k.split(':');i=int(index);actor=('reader'+str(i),s['reader_nonce'][i]);pin=s['reader_pins'][i]
  if kind=='reader-request':
   if s['selected']:n['reader_requests']=d.replace_at(s['reader_requests'],i,(actor,s['selected']))
   else:deny('no-selection')
  elif kind=='reader-pin':
   request=s['reader_requests'][i]
   if not request or pin:deny('no-fresh-request')
   elif request[0]!=actor:deny('stale-reader')
   elif request[1]!=s['selected'] and mutant!='fresh-pin-current':deny('stale-selection')
   elif not any(x[0]==request[1] for x in s['publication_store']):deny('retired')
   else:n['reader_pins']=d.replace_at(s['reader_pins'],i,request);n['reader_waited']=d.replace_at(s['reader_waited'],i,False)
  elif kind=='reader-copy':
   if not pin or pin[0]!=actor:deny('no-owned-pin')
   else:
    stored=next((x for x in s['publication_store'] if x[0]==pin[1]),None)
    if not stored:deny('retired')
    else:n['reader_copies']=d.replace_at(s['reader_copies'],i,stored)
  elif kind=='reader-wait':
   if not pin or pin[0]!=actor:deny('no-owned-pin')
   else:n['reader_waited']=d.replace_at(s['reader_waited'],i,True)
  elif kind in ('reader-release','reader-release-foreign'):
   if not pin or pin[0]!=actor or (kind=='reader-release-foreign' and mutant!='reader-release-owner'):deny('no-owned-pin')
   elif not s['reader_waited'][i] and mutant!='reader-wait':deny('reader-live')
   else:n['reader_pins']=d.replace_at(s['reader_pins'],i,())
  elif kind=='reader-restart':n['reader_nonce']=d.replace_at(s['reader_nonce'],i,s['reader_nonce'][i]+1)
  elif kind in ('reader-install','reader-install-corrupt'):
   copied=s['reader_copies'][i]
   if not copied:deny('no-copy')
   else:
    e,raw=copied
    if kind=='reader-install-corrupt':raw=raw.replace('ownerA','ownerB')
    if (raw!=d.raw_cut(e.cut) or d.digest(json.loads(raw))!=e.content or e.inventory!=d.record_ids(e.cut)) and mutant!='copy-binding':deny('copy-mismatch')
    else:
     n.update(installed_cut=(e,raw),cut_received=e.cut,joined_cut='',classified_cut='',source_version=max(s['source_version'],d.lit.fixture(e.cut)['binding']['body']['source_version']))
     if mutant=='install-allowance':n['free']+=s['reserved'][0];n['reserved']=(0,s['reserved'][1])
  else:raise ValueError('unknown reader action '+kind)
 elif k=='reclaim':
  target=next((x for x in s['publication_store'] if x[0]!=s['selected']),None)
  if mutant=='reclaim-current':target=next(iter(s['publication_store']),None)
  if not target:deny('no-retired-generation')
  elif any(pin and pin[1]==target[0] for pin in s['reader_pins']) and mutant!='reclaim-pinned':deny('reader-pinned')
  elif mutant=='global-pin-count' and any(s['reader_pins']):deny('reader-pinned')
  else:n.update(publication_store=tuple(x for x in s['publication_store'] if x!=target),retired_cuts=s['retired_cuts']+(target[0].generation,))
 elif k=='cut-receive':deny('publication-required')
 elif k=='reconcile' and mutant!='settle-current' and (not s['installed_cut'] or s['installed_cut'][0]!=s['selected'] or s['installed_cut'][0].source_head!=s['source_head'] or s['installed_cut'][0].source_generation!=s['source_generation']):deny('current-publication-required')
 else:n.update(old.step(d.project(s),a,p,u,outcome,mutant))
 return n
