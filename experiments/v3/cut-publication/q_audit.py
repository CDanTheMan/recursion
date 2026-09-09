"""Third complete relation. No implementation reducer imported."""
import copy,functools,json,hashlib,hmac
import q_domain as d
import p_audit as old
enabled=old.enabled

def hash_value(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
@functools.lru_cache(maxsize=None)
def material(name):
 x=d.lit.fixture(name);records=x['original']['records']
 return (json.dumps(x,sort_keys=True,separators=(',',':')),hash_value(x),tuple(hash_value(r) for r in records),hash_value(records))
@functools.lru_cache(maxsize=None)
def checked_payload(env,raw):
 canonical_text,content,inventory,source_head=material(env.cut)
 d.require(raw==canonical_text and env.content==content and env.inventory==inventory and env.source_head==source_head,'actual retained publication bytes/inventory/head')
 mac=hmac.new(d.TEST_KEY,json.dumps(tuple(env)[:-1],sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
 d.require(env.signature==mac and env.principal=='collectorA' and env.permit[:3]==('cut-publish','authority','collectorA'),'synthetic publication issuer/body proof')
 d.require(type(env.expected_revision) is int and env.expected_revision>=0 and env.source_generation[:3]==('cut-source','collectorA','effectA'),'publication namespaces')
 return True

def initialization(s,u):
 old.initialization(d.project(s),u)
 expected=dict(publisher_boot=1,publisher_serial=1,source_name='',source_generation=('cut-source','collectorA','effectA',0),source_head='',staged=(),stage_serial=0,selected=(),publication_revision=0,publication_store=(),publication_receipts=(),publication_reply=(),publication_reads=0,reader_requests=((),()),reader_pins=((),()),reader_copies=((),()),reader_waited=(False,False),reader_nonce=(1,1),installed_cut=(),retired_cuts=())
 d.require({k:s[k] for k in d.EXTRA}==expected,'complete independent publication initialization');invariant(s)

def invariant(s):
 old.invariant(d.project(s))
 d.require(type(s['publication_revision']) is int and s['publication_revision']==len(s['publication_receipts']),'durable commit and receipt cardinality')
 d.require(len({r[0].request for r in s['publication_receipts']})==len(s['publication_receipts']),'unique publication request identity')
 previous=''
 for index,(env,receipt) in enumerate(s['publication_receipts']):
  d.require(env.expected_revision==index and env.parent==previous,'publication exact parent lineage')
  d.require(receipt==(env.request,hash_value(env),index+1,env.generation,env.content),'immutable publication result identity');previous=env.generation
 if s['selected']:d.require(s['publication_receipts'] and s['selected']==s['publication_receipts'][-1][0] and any(row[0]==s['selected'] for row in s['publication_store']),'selected committed current generation retained')
 for env,raw in s['publication_store']:checked_payload(env,raw);d.require(env.generation not in s['retired_cuts'],'no reclaimed object resurrection')
 if s['source_name']:d.require(s['source_head']==material(s['source_name'])[3],'source head exact original records')
 for i,pin in enumerate(s['reader_pins']):
  if pin:d.require(pin[0][0]=='reader'+str(i) and any(x[0]==pin[1] for x in s['publication_store']),'durable existing reader retains exact object')
 for copied in s['reader_copies']:
  if copied:checked_payload(*copied)
 if s['installed_cut']:checked_payload(*s['installed_cut'])

def check(s,a,n,p,u,outcome):
 d.require(a in enabled(s,p),'complete publication enabledness');k=a.partition('@')[0];patch={};reason='ok';delegate=False
 if k=='authority-restart':patch['publisher_boot']=s['publisher_boot']+1
 elif k=='publisher-revoke':patch['publisher_serial']=s['publisher_serial']+1
 elif k=='source-restart':patch['source_generation']=('cut-source','collectorA','effectA',s['source_generation'][-1]+1)
 elif k=='source-attest' or k.startswith('source:'):
  name=s['cut_delivery'] if k=='source-attest' else k[7:]
  if not name or s['remote']==0:reason='no-source'
  else:
   current=d.lit.fixture(name)['original'];prior=d.lit.fixture(s['source_name'])['original'] if s['source_name'] else None
   same_scope=not prior or (current['intent']==prior['intent'] and current['admission']==prior['admission'] and d.lit.fixture(name)['binding']['body']['reservation']==d.lit.fixture(s['source_name'])['binding']['body']['reservation'])
   # Compare complete original record bytes, independently of implementation digest-prefix checks.
   prefix_ok=not prior or [json.dumps(r,sort_keys=True,separators=(',',':')) for r in current['records'][:len(prior['records'])]]==[json.dumps(r,sort_keys=True,separators=(',',':')) for r in prior['records']]
   if d.lit.fixture(name)['binding']['body']['reservation']!=list(s['bindings'][0]):reason='foreign-source'
   elif not same_scope or not prefix_ok:reason='source-fork'
   else:patch.update(source_name=name,source_head=material(name)[3],source_generation=s['source_generation'] if prior else ('cut-source','collectorA','effectA',1),source_version=max(s['source_version'],d.lit.fixture(name)['binding']['body']['source_version']))
 elif k=='stage' or k.startswith('stage-'):
  if not s['cut_delivery']:reason='no-delivered-cut'
  else:
   # Candidate construction is data encoding, verified against complete original bytes on commit.
   patch.update(staged=d.candidate(s,k[6:] if k!='stage' else 'normal'),stage_serial=s['stage_serial']+1)
 elif k in ('pub-commit','pub-rival','pub-retry','pub-retry-conflict','pub-retry-foreign'):
  if not s['staged'] and not s['publication_receipts']:reason='unstaged'
  else:
   env,raw=d.incoming(s,k);prior={row[0].request:row for row in s['publication_receipts']}.get(env.request)
   if k=='pub-retry-foreign':reason='wrong-caller'
   elif prior is not None:
    if json.dumps(prior[0],sort_keys=True)!=json.dumps(env,sort_keys=True):reason='E-IDEMPOTENCY-CONFLICT'
    else:reason='duplicate';patch.update(publication_reply=prior[1],publication_reads=s['publication_reads']+1)
   else:
    facts=material(env.cut);mac=hmac.new(d.TEST_KEY,json.dumps(tuple(env)[:-1],sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
    requirements=[(s['paused'] is False,'E-PAUSED'),(env.principal=='collectorA' and env.permit[2]=='collectorA','wrong-owner'),(env.permit[0]=='cut-publish' and env.permit[1]=='authority','wrong-domain'),(json.dumps(env.permit[3])==json.dumps(('publisher-boot','authority',s['publisher_boot'])),'stale-boot'),(type(env.permit[4]) is int and env.permit[4]==s['publisher_serial'],'stale-permit'),(env.signature==mac,'bad-authentication'),(type(env.expected_revision) is int and env.expected_revision==s['publication_revision'] and env.parent==(s['selected'].generation if s['selected'] else ''),'stale-parent'),(raw==facts[0] and env.content==facts[1],'bad-content'),(env.inventory==facts[2],'bad-inventory'),(json.dumps(env.source_generation)==json.dumps(s['source_generation']),'stale-source-generation'),(env.source_head==facts[3] and env.source_head==s['source_head'],'stale-source-head'),(env.generation not in [r[0].generation for r in s['publication_store']],'generation-used')]
    reason=next((failure for holds,failure in requirements if not holds),'ok')
    if reason=='ok':
     rev=s['publication_revision']+1;receipt=(env.request,hash_value(env),rev,env.generation,env.content)
     patch.update(selected=env,publication_revision=rev,publication_store=s['publication_store']+((env,raw),),publication_receipts=s['publication_receipts']+((env,receipt),),publication_reply=receipt,cut_delivery='')
 elif k=='pub-lose-reply':patch['publication_reply']=()
 elif k.startswith('reader-'):
  verb,idx=k.split(':');i=int(idx);owner=('reader'+idx,s['reader_nonce'][i]);pin=s['reader_pins'][i]
  def set_slot(key,value):patch[key]=tuple(value if j==i else old_value for j,old_value in enumerate(s[key]))
  if verb=='reader-request':
   if not s['selected']:reason='no-selection'
   else:set_slot('reader_requests',(owner,s['selected']))
  elif verb=='reader-pin':
   pending=s['reader_requests'][i]
   if not pending or pin:reason='no-fresh-request'
   elif pending[0]!=owner:reason='stale-reader'
   elif pending[1]!=s['selected']:reason='stale-selection'
   elif pending[1] not in [x[0] for x in s['publication_store']]:reason='retired'
   else:set_slot('reader_pins',pending);set_slot('reader_waited',False)
  elif verb=='reader-copy':
   if not pin or pin[0]!=owner:reason='no-owned-pin'
   else:
    item=next((pair for pair in s['publication_store'] if pair[0]==pin[1]),None)
    if item is None:reason='retired'
    else:set_slot('reader_copies',item)
  elif verb=='reader-wait':
   if not pin or pin[0]!=owner:reason='no-owned-pin'
   else:set_slot('reader_waited',True)
  elif verb in ('reader-release','reader-release-foreign'):
   if not pin or pin[0]!=owner or verb=='reader-release-foreign':reason='no-owned-pin'
   elif not s['reader_waited'][i]:reason='reader-live'
   else:set_slot('reader_pins',())
  elif verb=='reader-restart':set_slot('reader_nonce',s['reader_nonce'][i]+1)
  elif verb in ('reader-install','reader-install-corrupt'):
   pair=s['reader_copies'][i]
   if not pair:reason='no-copy'
   else:
    env,raw=pair;facts=material(env.cut)
    if verb=='reader-install-corrupt':raw=raw.replace('ownerA','ownerB')
    if raw!=facts[0] or env.content!=facts[1] or env.inventory!=facts[2]:reason='copy-mismatch'
    else:patch.update(installed_cut=(env,raw),cut_received=env.cut,joined_cut='',classified_cut='',source_version=max(s['source_version'],d.lit.fixture(env.cut)['binding']['body']['source_version']))
  else:raise ValueError('independent relation lacks reader action')
 elif k=='reclaim':
  candidates=[x for x in s['publication_store'] if x[0]!=s['selected']]
  if not candidates:reason='no-retired-generation'
  elif any(pin and pin[1]==candidates[0][0] for pin in s['reader_pins']):reason='reader-pinned'
  else:patch.update(publication_store=tuple(x for x in s['publication_store'] if x!=candidates[0]),retired_cuts=s['retired_cuts']+(candidates[0][0].generation,))
 elif k=='cut-receive':reason='publication-required'
 elif k=='reconcile':
  installed=s['installed_cut']
  if not installed or installed[0]!=s['selected'] or installed[0].source_head!=s['source_head'] or installed[0].source_generation!=s['source_generation']:reason='current-publication-required'
  else:delegate=True
 else:delegate=True
 if delegate:
  old.check(d.project(s),a,d.project(n),p,u,outcome);d.require(all(s[x]==n[x] for x in d.EXTRA),'complete publication frame on inherited action')
 else:
  expected=copy.deepcopy(s);expected.update(patch,done=s['done']|(1<<p['actions'].index(a)),decision=k+':'+reason)
  d.require(n==expected,'independent complete publication postcondition '+k)
 invariant(n)
 # Publication, source attestation and copied historical installation never settle effects.
 if not delegate:
  for field in ('free','reserved','consumed','revision','runtime_observations','receipt_journal','canonical_quarantine','sent','lifetime','quota_used','generation','pin','installed_cursor','replay_cursor'):
   d.require(n[field]==s[field],'publication/reader noninterference '+field)
 if n['reserved'][0]<s['reserved'][0]:d.require(s['installed_cut'] and s['installed_cut'][0]==s['selected'] and s['installed_cut'][0].source_head==s['source_head'],'exact current publication before effect settlement')
