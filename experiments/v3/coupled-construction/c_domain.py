"""Shared data, finite environments and literal encoding only; no transition rules."""
import base64,copy,json,pathlib,runpy
from typing import NamedTuple
ROOT=pathlib.Path(__file__).resolve().parents[3]
COSTS=(1,2,1,2);EVENTS=4;GRANTS=4;QUEUE_EVENTS=2;QUEUE_BYTES=2;CHANNEL=1;INFLIGHT=2;RETAINED=2;FRAME=2
TOKENS=(b'a',b'bb',b'c',b'dd')
REQUESTS=(('pool10','goalA','opA','attemptA','payloadA','ownerA',6),('pool10','goalB','opB','attemptB','payloadB','ownerB',6))
def token(domain,serial=1):return (domain,'operationA' if domain=='delivery' else 'goalA','owner' if domain=='goal' else 'kernel','head',serial,domain+'-identity-'+str(serial))
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def require(x,m):
 if not x:raise ValueError(m)
def cursor(n,u):return sum(COSTS[:n]) if u=='utf8-byte' else n
def msg(t,**kw):return dict(type=t,protocol_version='m1b-broker/1',stream_id='stream-a',daemon_epoch=2,**kw)
def hello(n,u):return msg('HELLO',client_id='client-a',last_cursor=cursor(n,u),cursor_unit=u,columns=80,rows=24,capabilities=['attach'])
def initial(u):
 return dict(free=10,reserved=(0,0),consumed=(0,0),bindings=((),()),intent=False,sent=0,remote=0,receipt=0,receipt_binding=(),classification=0,conflict=False,revision=0,reads=(10,10),
 tokens={k:token(k) for k in ('goal','lease','process','delivery')},request=(),input_request=(),reply=(),evidence=(),adopted=(),adoptions=0,wakes=0,started=False,executor='head',executor_binding=(token('lease'),token('process')),wait=(),alias_active=True,stopped=False,control=0,cancelled=False,missing=False,unrelated='active-local',
 worker_exited=False,lifetime=(1,0),quota_epoch=0,quota_used=1,generation=1,pin=False,copied=False,snapshot=(),installed=(),installed_cursor=0,replay_cursor=0,
 catalog=(('boot',(),(),0,0),),offered=0,retained=(),channels=((),(),()),wire_sent=0,pending=(),delivery=(),received=(),delivered=(),loss=0,covered=0,phase=0,byte_credit=0,event_credit=0,grants=0,acknowledged=0,frame=0,quarantine=False,wire=(canonical(hello(0,u)),),done=0,decision='initial')
AUTH=('free','reserved','consumed','bindings','intent','sent','remote','receipt','receipt_binding','classification','conflict','revision','reads','tokens','request','input_request','reply','evidence','adopted','adoptions','wakes','started','executor','executor_binding','wait','alias_active','stopped','control','cancelled','missing','unrelated','worker_exited','lifetime','quota_epoch','quota_used','generation','catalog')
FLOW=('offered','retained','channels','wire_sent','pending','delivery','received','delivered','loss','covered','phase','byte_credit','event_credit','grants','acknowledged','frame','quarantine','wire')
VIEW=('pin','copied','snapshot','installed','installed_cursor','replay_cursor','done','decision')
class Split(NamedTuple):authority:dict;flow:dict;view:dict
def split(s):return Split(*({k:s[k] for k in names} for names in (AUTH,FLOW,VIEW)))
def flatten(s):return dict(**s.authority,**s.flow,**s.view) if isinstance(s,Split) else s

def sequence(actions,core=()):
 names=tuple(a+'@'+str(i) for i,a in enumerate(actions));extras=tuple(a+'@'+str(i+len(names)) for i,a in enumerate(core))
 deps={a:((names[i-1],) if i else ()) for i,a in enumerate(names)}
 deps.update({a:((names[-1],) if names else ()) for a in extras})
 return dict(actions=names+extras,requires=deps)
def ready_actions(s,p):
 seen={a for i,a in enumerate(p['actions']) if s['done']&(1<<i)}
 return [a for a in p['actions'] if a not in seen and all(x in seen for x in p['requires'][a])]
def transfer():return ['offer','pump-source','pump-sdk','pump-broker']
def deliver():return ['emit','receive','ack']
A=['capture','copy','pin-release','admitA','intent','send','remote','lose','consult','wait-held','suspend','start','reply']
G=transfer()+['evict','credit:2','hello','welcome','reset','install']
D2=transfer()+['credit:2']+deliver()
D3=transfer()+['credit:1']+deliver()
NORMAL=A+G+D2+D3+['ingest','adopt','wake']
PROFILES={
 'pool-contention':sequence(['readA','readB','admitA','admitB','duplicateA']),
 'old-snapshot-uncertainty':sequence(A+G+['admitB','quota','restart','replay','resend','duplicateA']),
 'transported-stale-advice':sequence(A+G+D2+transfer()+['credit:1','emit','lease','receive','ack','ingest','adopt','wake','admitB']),
 'historical-adoption':sequence(NORMAL[:-1]+['lease','wake','admitB']),
 'stop-saturated':sequence(A+G+transfer()+['credit:2','emit']+transfer()+['stop-request','stop-apply','cancel','admitB','receive','ack','credit:1','emit','receive','ingest','unrelated']),
 'refusal-reconciliation':sequence(NORMAL+['query','classify','admitB','reconcile','reconcile','duplicateA','admitB']+transfer()+['credit:2']+deliver()),
 'success-consumption':sequence(NORMAL+['query','classify','reconcile','reconcile','admitB']),
 'ack-before-ingestion':sequence(A+G+D2+transfer()+['credit:1','emit','ack','receive','ingest','adopt','wake','ingest','adopt','wake','replay','duplicateA','resend','admitB']),
 'reset-future-reply':sequence(A+transfer()+['evict','offer','pump-source','offer','hello','welcome','reset','install','pump-sdk','pump-broker','credit:2']+deliver()+['pump-source','pump-sdk','pump-broker','credit:1']+deliver()+['ingest','adopt','admitB']),
 'alias-reuse':sequence(A[:8]+['expire']+A[8:]+G+D2+transfer()+['credit:1','emit','stop-request','stop-apply','receive','ingest','adopt','unrelated','admitB']),
 'quota-restart-lifetime':sequence(NORMAL+['exit','quota','restart','compute','publish','replay','resend','duplicateA','admitB']),
 'classification-conflict':sequence(NORMAL+['query','classify','conflict','reconcile','admitB']),
 'framing-stop':sequence(A+['fragment','fragment','fragment','framing-fault','stop-request','stop-apply','cancel','admitB']),
 'owner-payload':sequence(A+['wrong-owner','wrong-payload','foreign-release','admitB']),
 'foreign-receipt':sequence(NORMAL+['query-wrong','classify','reconcile','admitB']),
 'wrong-record-binding':sequence(A[:-1]+['reply-wrong']+G+D2+D3+['ingest','adopt','wake','admitB']),
 'free-admission':sequence([],('readA','readB','admitA','admitB','duplicateA','quota','restart','capture')),
 'free-delivery-core':sequence(A+G+D2+transfer()+['credit:1','emit'],('receive','ingest','adopt','wake','lease','stop-request','stop-apply','restart','quota','ack')),
 'free-recovery-core':sequence(A+transfer()+['evict','offer','pump-source','offer'],('hello','welcome','reset','install','quota','restart','admitB','duplicateA','resend','pin-release')),
}
PROFILES.update({
 'installation-before-event':sequence(A+transfer()+['evict','credit:2','hello','welcome','reset']+transfer()+['credit:2','emit','install','emit','receive','ack','admitB']),
 'reset-needs-fresh-credit':sequence(A+transfer()+['evict','credit:2','hello','welcome','reset','install']+transfer()+['emit','credit:2','emit','receive','ack','admitB']),
 'lost-ack-pending':sequence(A+G+D2+transfer()+['credit:1','emit','lose-ack','receive','ingest','adopt','ack','wake','admitB']),
})
PROFILES.update({
 'transported-goal-change':sequence(A+G+D2+transfer()+['credit:1','emit','goal','receive','ack','ingest','adopt','wake','admitB']),
 'four-literal-events':sequence(A+transfer()+['credit:1']+deliver()+transfer()+['credit:2']+deliver()+transfer()+['credit:1']+deliver()+['ingest','adopt','wake','query','classify','reconcile']+transfer()+['credit:2']+deliver()+['admitB']),
 'consultation-duplicates':sequence(NORMAL+['consult-duplicate','consult-conflict','ingest','adopt','wake','admitB']),
})
UNITS=('event','utf8-byte')
# Each environment fixes remote success/refusal; both are explored for every profile.
OUTCOMES=(1,2)
SCHEMA=runpy.run_path(str(ROOT/'scripts/tests/v3/execution/schema.test.py'))
ORACLE=runpy.run_path(str(ROOT/'scripts/tests/v3/execution/reference_oracle.py'))['replay_broker']
FIXTURE=json.loads((ROOT/'scripts/tests/v3/execution/fixtures/F-M1B-020.json').read_text())['input']
def evaluate(history):
 x=copy.deepcopy(FIXTURE);x.update(messages=[json.loads(m) for m in history],queue_limit_events=2,queue_limit_bytes=2)
 x=SCHEMA['strict_loads'](canonical(x).encode());SCHEMA['validate'](x,'BrokerTraceInput');return ORACLE(x)
