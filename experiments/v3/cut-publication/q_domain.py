"""Finite retained publication data/encoding; no admission predicates."""
import pathlib,sys,copy,hashlib,hmac,json
from typing import NamedTuple
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'experiments/v3/coupled-cut-pause'))
import p_domain as base,p_literal as lit
from p_domain import canonical,require,sequence,ready_actions,UNITS,OUTCOMES,REQUESTS,COSTS,EVENTS,GRANTS,QUEUE_EVENTS,QUEUE_BYTES,CHANNEL,INFLIGHT,RETAINED,FRAME,TOKENS,SCHEMA,evaluate
class Envelope(NamedTuple):
 request:str;principal:str;permit:tuple;expected_revision:int;parent:str;cut:str;content:str;inventory:tuple;source_generation:tuple;source_head:str;generation:str;signature:str
# Public synthetic fixture material; no product authentication scheme is selected.
TEST_KEY=b'public-cut-publication-fixture-key-v1'
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def raw_cut(name):return canonical(lit.fixture(name))
def record_ids(name):return tuple(digest(r) for r in lit.fixture(name)['original']['records'])
def head(name):return digest(lit.fixture(name)['original']['records'])
def scope(name):
 x=lit.fixture(name);return canonical((x['original']['cut']['trace_header']['intent'],x['original']['cut']['trace_header']['admission'],x['binding']['body']['reservation']))
def sign(e):return e._replace(signature=hmac.new(TEST_KEY,canonical(tuple(e)[:-1]).encode(),hashlib.sha256).hexdigest())
def permit(boot,serial):return ('cut-publish','authority','collectorA',('publisher-boot','authority',boot),serial)
def source_token(serial):return ('cut-source','collectorA','effectA',serial)
EXTRA=('publisher_boot','publisher_serial','source_name','source_generation','source_head','staged','stage_serial','selected','publication_revision','publication_store','publication_receipts','publication_reply','publication_reads','reader_requests','reader_pins','reader_copies','reader_waited','reader_nonce','installed_cut','retired_cuts')
DEFAULTS=dict(publisher_boot=1,publisher_serial=1,source_name='',source_generation=source_token(0),source_head='',staged=(),stage_serial=0,selected=(),publication_revision=0,publication_store=(),publication_receipts=(),publication_reply=(),publication_reads=0,reader_requests=((),()),reader_pins=((),()),reader_copies=((),()),reader_waited=(False,False),reader_nonce=(1,1),installed_cut=(),retired_cuts=())
BASE_FIELDS=base.AUTH+base.FLOW+base.VIEW
AUTH=base.AUTH+EXTRA;FLOW=base.FLOW;VIEW=base.VIEW;Split=base.Split
PROFILES={}
def initial(u):return dict(base.initial(u),**copy.deepcopy(DEFAULTS))
def project(s):return {k:s[k] for k in BASE_FIELDS}
def split(s):return Split(*({k:s[k] for k in names} for names in (AUTH,FLOW,VIEW)))
def flatten(s):return dict(**s.authority,**s.flow,**s.view) if isinstance(s,Split) else s
def replace_at(xs,i,v):return tuple(v if n==i else x for n,x in enumerate(xs))
def candidate(s,variant='normal'):
 name=s['cut_delivery'];raw=raw_cut(name);serial=s['stage_serial']+1
 e=Envelope('publication-'+str(serial),'collectorA',permit(s['publisher_boot'],s['publisher_serial']),s['publication_revision'],s['selected'].generation if s['selected'] else '',name,digest(json.loads(raw)),record_ids(name),s['source_generation'],head(name),'cut-generation-'+str(serial),'')
 if variant=='owner':e=e._replace(principal='collectorB')
 if variant=='domain':e=e._replace(permit=('quota',)+e.permit[1:])
 if variant=='inventory':e=e._replace(inventory=e.inventory[:-1])
 if variant=='head':e=e._replace(source_head='unbound-head')
 if variant=='bool-boot':e=e._replace(permit=e.permit[:3]+(('publisher-boot','authority',True),e.permit[4]))
 if variant=='bool-revision':e=e._replace(expected_revision=False)
 if variant=='content':raw=raw.replace('ownerA','ownerB')
 return (sign(e)._replace(signature='0'*64) if variant=='signature' else sign(e),raw)
def incoming(s,kind):
 if kind=='pub-rival':
  e,raw=s['staged'];return (sign(e._replace(request=e.request+'-rival',generation=e.generation+'-rival')),raw)
 if kind in ('pub-retry','pub-retry-conflict','pub-retry-foreign'):
  e,receipt=s['publication_receipts'][0] if s['publication_receipts'] else (s['staged'][0],())
  raw='' # Durable receipt lookup does not dereference a retired source object.
  if kind=='pub-retry-conflict':
   name='late-receipt' if e.cut=='success' else 'success';e=sign(e._replace(cut=name,content=digest(lit.fixture(name)),inventory=record_ids(name),source_head=head(name)));raw=raw_cut(name)
  return e,raw
 return s['staged']
def add(name,steps,core=(),outcomes=OUTCOMES):
 p=sequence(steps,core);p['outcomes']=outcomes;PROFILES[name]=p
SETUP=['admitA','intent','send','remote','lose','query']
def deliver(name):return ['cut:'+name,'cut-deliver']
def source(name):return deliver(name)+['source-attest','stage']
def pub(name):return source(name)+['pub-commit']
def reader(i=0):return ['reader-request:'+str(i),'reader-pin:'+str(i),'reader-copy:'+str(i),'reader-wait:'+str(i),'reader-release:'+str(i),'reader-install:'+str(i),'join-cut','classify']
for name,out in [('success',1),('failure',2)]:add('current-'+name,SETUP+pub(name)+reader()+['reconcile','reconcile','admitB'],outcomes=(out,))
add('commit-lost-reply-restart',SETUP+pub('terminal')+['pub-lose-reply','authority-restart','pub-retry','pub-retry','admitB'])
add('old-boot-permit',SETUP+source('terminal')+['authority-restart','pub-commit'])
add('same-boot-revocation',SETUP+source('terminal')+['publisher-revoke','pub-commit','stage','pub-commit'])
for variant in ('owner','domain','inventory','head','content','signature','bool-boot','bool-revision'):
 add('invalid-'+variant,SETUP+deliver('terminal')+['source-attest','stage-'+variant,'pub-commit','admitB'])
add('same-request-different-cut',SETUP+pub('success')+['pub-retry-conflict','admitB'],outcomes=(1,))
add('duplicate-foreign-caller',SETUP+pub('terminal')+['pub-retry-foreign'])
add('competing-parent',SETUP+source('terminal')+['pub-rival','pub-commit'])
add('pause-fresh-publication',SETUP+source('terminal')+['pause','pub-commit','admitB'])
add('pause-duplicate-awareness',SETUP+pub('terminal')+['pause','pub-retry','admitB'])
add('stale-source-staged',SETUP+source('success')+['source:later-start-only','pub-commit'],outcomes=(1,))
add('same-version-source-fork',SETUP+pub('later-start-only')+['source:conflict','admitB'],outcomes=(1,))
add('equal-version-real-append',SETUP+pub('late-receipt')+['source:later-start-only']+deliver('later-start-only')+['stage','pub-commit']+reader()+['reconcile','admitB'],outcomes=(1,))
OLD=SETUP+pub('success')+['reader-request:0','reader-pin:0','reader-request:1','source:later-start-only']+deliver('later-start-only')+['stage','pub-commit']
add('existing-reader-new-selection',OLD+['authority-restart','reader-pin:1','reader-copy:0','reader-wait:0','reader-release:0','reclaim','reader-install:0','join-cut','classify','reconcile','admitB'],outcomes=(1,))
add('reclaim-live-reader',OLD+['reclaim','reader-copy:0','reader-release:0','reclaim','reader-wait:0','reader-release:0','reclaim','reader-install:0','join-cut','classify','reconcile','admitB'],outcomes=(1,))
add('current-pin-not-old-pin',OLD+['reader-copy:0','reader-wait:0','reader-release:0','reader-request:1','reader-pin:1','reclaim','reader-install:0','join-cut','classify','admitB'],outcomes=(1,))
add('reader-restart-copied',OLD+['reader-copy:0','reader-wait:0','reader-release:0','reclaim','reader-restart:0','reader-install:0','join-cut','classify','reconcile','admitB'],outcomes=(1,))
add('reader-restart-live',OLD+['reader-restart:0','reader-copy:0','reader-release:0','reclaim','admitB'],outcomes=(1,))
add('foreign-reader-release',OLD+['reader-wait:0','reader-release-foreign:0','reclaim','admitB'],outcomes=(1,))
add('corrupt-copy-install',SETUP+pub('success')+reader()[:5]+['reader-install-corrupt:0','join-cut','classify','reconcile','admitB'],outcomes=(1,))
add('historical-copy-pause',OLD+['reader-copy:0','reader-wait:0','reader-release:0','reclaim','pause','reader-install:0','join-cut','classify','observe','reconcile','admitB'],outcomes=(1,))
add('latest-head-same-content-family',SETUP+pub('success')+reader()+['source:conflict']+deliver('conflict')+['stage','pub-commit','reader-install:0','join-cut','classify','reconcile','admitB'],outcomes=(1,))
add('late-receipt-current',SETUP+pub('ambiguous')+reader()+['source:late-receipt']+deliver('late-receipt')+['stage','pub-commit']+reader(1)+['reconcile','admitB'],outcomes=(1,))
add('installation-no-allowance',SETUP+pub('failure')+reader()+['quota','restart','replay','duplicateA','admitB'],outcomes=(2,))
# Actual complete four-event flow remains a composed new witness, with publication inserted at classification.
four=base.base.PROFILES['four-literal-events']['actions'];steps=[]
for a in four:
 k=a.split('@')[0]
 steps.extend(pub('terminal')+reader() if k=='classify' else [k])
add('four-event-publication',steps)
add('publication-race-core',SETUP+source('terminal'),('pub-commit','authority-restart','publisher-revoke','pause','quota','restart'))
add('reader-retirement-core',OLD+['reader-copy:0'],('reader-wait:0','reader-release:0','reclaim','reader-install:0','authority-restart','reconcile'),outcomes=(1,))

add('equal-version-stale-install',SETUP+pub('late-receipt')+reader()+['source:later-start-only']+deliver('later-start-only')+['stage','pub-commit','reader-install:0','join-cut','classify','reconcile','admitB'],outcomes=(1,))
add('source-generation-staged',SETUP+source('terminal')+['source-restart','pub-commit'])

add('reclaim-current-selection',SETUP+pub('terminal')+['reclaim','admitB'])

add('transported-publication',base.base.NORMAL+['query']+pub('terminal')+reader()+['pause','observe','reconcile','admitB'])
add('typed-advice-publication',[a.split('@')[0] for a in base.base.PROFILES['transported-stale-advice']['actions']]+['query']+pub('terminal')+reader()+['reconcile','admitB'])

add('foreign-source-scope',SETUP+source('foreign')+['pub-commit','admitB'])

add('duplicate-after-retirement',OLD+['reader-copy:0','reader-wait:0','reader-release:0','reclaim','pub-lose-reply','authority-restart','pub-retry','pub-retry'],outcomes=(1,))

for foreign in ('foreign','foreign-attempt'):
 add('same-head-'+foreign,SETUP+pub('success')+deliver(foreign)+['stage','pub-commit']+reader()+['reconcile','admitB'],outcomes=(1,))
