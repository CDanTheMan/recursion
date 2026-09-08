"""Finite product data and exact retained-input identities; no transition predicates."""
import pathlib,sys,copy
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'experiments/v3/coupled-construction'))
import c_domain as base
from c_domain import canonical,require,ready_actions,sequence,UNITS,OUTCOMES,COSTS,EVENTS,GRANTS,QUEUE_EVENTS,QUEUE_BYTES,CHANNEL,INFLIGHT,RETAINED,FRAME,TOKENS,SCHEMA,evaluate,REQUESTS
import p_literal as lit
EXTRA=('paused','pause_epoch','plan_accepted','cut_offer','cut_delivery','cut_received','joined_cut','classified_cut','source_version','cut_status','cut_hold','runtime_observations','observation_receipt','observation_payload','refusal_journal','canonical_quarantine','nonexecution')
BASE_FIELDS=base.AUTH+base.FLOW+base.VIEW
AUTH=base.AUTH+EXTRA;FLOW=base.FLOW;VIEW=base.VIEW;Split=base.Split
DEFAULTS=dict(paused=False,pause_epoch=('pause','owner','runtime-admission',1),plan_accepted=True,cut_offer='',cut_delivery='',cut_received='',joined_cut='',classified_cut='',source_version=1,cut_status='',cut_hold=True,runtime_observations=0,observation_receipt='',observation_payload='',refusal_journal=0,canonical_quarantine=False,nonexecution=False)
def initial(u):return dict(base.initial(u),**copy.deepcopy(DEFAULTS))
def project(s):return {k:s[k] for k in BASE_FIELDS}
def split(s):return Split(*({k:s[k] for k in names} for names in (AUTH,FLOW,VIEW)))
def flatten(s):return dict(**s.authority,**s.flow,**s.view) if isinstance(s,Split) else s
# Historical profiles retain their old dependency DAG; insert actual supplemental stages before each classify.
def extend(p):
 old=p['actions'];actions=[];deps={};last={}
 for a in old:
  prefix=['cut:terminal','cut-deliver','cut-receive','join-cut'] if a.split('@')[0]=='classify' else []
  chain=prefix+[a.split('@')[0]];previous=tuple(last[x] for x in p['requires'][a])
  for k in chain:
   new=k+'@'+str(len(actions));actions.append(new);deps[new]=previous;previous=(new,)
  last[a]=new
 return {'actions':tuple(actions),'requires':deps,'outcomes':OUTCOMES}
PROFILES={name:extend(p) for name,p in base.PROFILES.items()}
# A deliberately foreign receipt profile does not silently receive a valid replacement cut.
p=PROFILES['foreign-receipt'];p['requires']={k.replace('cut:terminal','cut:foreign'):tuple(v.replace('cut:terminal','cut:foreign') for v in values) for k,values in p['requires'].items()};p['actions']=tuple(k.replace('cut:terminal','cut:foreign') for k in p['actions'])
A=base.A;G=base.G;D2=base.D2;D3=base.D3;NORMAL=base.NORMAL
CUT=lambda n:['cut:'+n,'cut-deliver','cut-receive','join-cut','classify']
SETUP=NORMAL+['query']
def add(name,steps,core=(),outcomes=OUTCOMES):
 p=sequence(steps,core);p['outcomes']=outcomes;PROFILES[name]=p
add('pause-before-reserve',['pause','admitA','intent','send','admitB'])
add('pause-before-permit',['admitA','intent','pause','send','admitB'])
add('issued-before-pause',['admitA','intent','send','pause','remote','lose','query']+CUT('terminal')+['observe','reconcile','admitB'])
for name in ('success','failure','late-receipt','conflict','prior-unresolved','later-unresolved','later-start-only','stale-paused','missing-original','contradictory','omitted','reordered','bad-mac','wrong-role','foreign','foreign-attempt','generic-failure','bad-attempt-map','missing-attempt-map','bad-source-version','bool-source-version'):
 add('cut-'+name,SETUP+CUT(name)+['reconcile','admitB'],outcomes=(2,) if name in ('failure','generic-failure') else (1,))
add('paused-observation',SETUP+CUT('terminal')+['pause','observe','classify','reconcile','admitB'])
add('duplicate-before-pause',SETUP+CUT('terminal')+['observe','pause','observe','observe-conflict','reconcile'])
add('canonical-quarantine',SETUP+CUT('ambiguous')+['observe']+CUT('late-receipt')+['reconcile','admitB'],outcomes=(1,))
add('stale-classified-cut',SETUP+CUT('success')+['source-later','reconcile','admitB']+CUT('later-start-only')+['reconcile'],outcomes=(1,))
add('cut-after-ack-restart',SETUP+['cut:terminal','cut-deliver','ack','restart','quota','install','cut-receive','join-cut','classify','pause','observe','reconcile','admitB'])
add('cut-pause-core',SETUP+CUT('terminal')[:-1],('classify','pause','observe','reconcile','quota','restart'))
add('cut-source-core',SETUP+CUT('success'),('source-later','reconcile','pause','observe','admitB','replay'),outcomes=(1,))
