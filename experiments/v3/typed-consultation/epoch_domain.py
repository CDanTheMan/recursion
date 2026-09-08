"""Typed finite data, profiles and representation projection only."""
import json
from typing import NamedTuple
TAGS=('goal','lease','writer','process','daemon','pause','config','delivery','provider-session')
def token(tag,serial=1,issuer=None):return (tag,'goal-a' if tag!='delivery' else 'operation-a',issuer or ('owner' if tag=='goal' else 'kernel-a'),'head',serial,tag+'-identity-'+str(serial))
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def require(x,m):
 if not x:raise ValueError(m)
def initial():return {'tokens':{t:token(t) for t in TAGS},'goal_record':('goal-a',1,'goal-digest-1'),'request':None,'input_request':None,'reply':None,'evidence':None,'adopted':None,'adoption_count':0,'wake_count':0,'started':False,'stopped':False,'cancel_delivered':False,'remote_outcome':'unknown','missing':False,'executor':'head','executor_binding':(token('lease'),token('process')),'wait':'none','wait_graph':(),'unrelated':'active','reserved':6,'free':4,'done':(),'decision':'initial'}
AUTH=('tokens','goal_record','request','input_request','evidence','adopted','adoption_count','wake_count','stopped','reserved','free')
BROKER=('reply','started','cancel_delivered','remote_outcome','missing','executor','executor_binding','wait','wait_graph','unrelated','done','decision')
class Split(NamedTuple):
 authority:dict
 broker:dict
def split(s):return Split({k:s[k] for k in AUTH},{k:s[k] for k in BROKER})
def flat(s):return dict(**s.authority,**s.broker) if isinstance(s,Split) else s
PREFIX=('request','suspend','start','reply')
PROFILES={
 'resource-wait':('request','wait-held','suspend','start','reply','ingest','adopt','wake'),
 'stale-lease':PREFIX+('lease2','ingest','adopt','wake'),
 'stale-goal':PREFIX+('owner-amend','ingest','adopt','wake'),
 'stale-issuer':PREFIX+('issuer','ingest','adopt','wake'),
 'stale-incarnation':PREFIX+('restart','ingest','adopt','wake'),
 'alias-after-receipt':PREFIX+('ingest','expire','adopt','wake'),
 'alias-before-receipt':PREFIX+('expire','ingest','adopt','wake'),
 'stop-borrowed':PREFIX+('ingest','stop','cancel-deliver','unrelated','adopt','wake','relaunch'),
 'stop-inflight':('request','suspend','start','stop','cancel-deliver','reply','ingest','unrelated','adopt','wake'),
 'historical-adoption':PREFIX+('ingest','adopt','lease2','wake'),
 'duplicates':('request','duplicate-request','conflict-request','suspend','start','reply','ingest','duplicate-reply','adopt','adopt-again','wake','wake-again'),
 'owner-only':PREFIX+('ingest','advice-amend','owner-amend','adopt','wake'),
 'wrong-domain':PREFIX+('wrong-domain','ingest','adopt','wake'),
 'three-leases':PREFIX+('ingest','adopt','lease2','lease3','wake'),
 'free-core':('request','suspend','start','reply','ingest','adopt','lease2','restart','expire','stop','wake','unrelated'),
}
# Ordered profiles are explicit witness environments; only free-core is unordered.
def environment(s,name):
 acts=PROFILES[name];remaining=[a for a in acts if a not in s['done']]
 if name!='free-core':return remaining[:1]
 return remaining
