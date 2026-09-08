"""Immutable finite fixture inputs, literal evidence join, and synthetic binding codec."""
import pathlib,sys,copy,functools,hashlib,hmac,json
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'experiments/v3/effect-evidence'))
import ee_common as ec,ee_cases as cases,ee_join as joiner,ee_experiment as old
KEYS={k:('PUBLIC-SYNTHETIC-CUT-PAUSE-TEST-KEY/'+k).encode() for k in ('collector','dispatcher','observer')}
REQUESTS=(('pool10','goalA','opA','attemptA','payloadA','ownerA',6),('pool10','goalB','opB','attemptB','payloadB','ownerB',6))
NAMES=tuple(cases.EXPECTED)+('missing-original','contradictory','omitted','reordered','bad-mac','wrong-role','foreign','foreign-attempt','generic-failure')
def seal(body):return hmac.digest(KEYS['dispatcher'],ec.canonical({'domain':'coupled-cut-binding-v1','body':body}),'sha256').hex()
@functools.lru_cache(None)
def fixture(name):
 source=name if name in cases.EXPECTED else ('failure' if name=='generic-failure' else 'success')
 original=cases.unsigned(source);bundle=cases.package(original,KEYS)
 req=list(REQUESTS[1 if name=='foreign' else 0])
 if name=='foreign-attempt':req[3]='attempt-other'
 if name=='missing-original':
  del original['cut']['trace_header']['intent']['target_ref'];bundle=cases.package(original,KEYS)
 if name=='contradictory':
  body=copy.deepcopy(bundle['dispatch']['body']);body['intent']['payload_digest']='sha256:'+'9'*64;bundle['dispatch']=joiner.sign(body,'dispatcher',KEYS)
 if name=='omitted':bundle['evidence'].pop(1)
 if name=='reordered':bundle['evidence'][0],bundle['evidence'][1]=bundle['evidence'][1],bundle['evidence'][0]
 if name=='bad-mac':bundle['evidence'][-1]['mac']='0'*64
 if name=='wrong-role':bundle['evidence'][-1]=joiner.sign(bundle['evidence'][-1]['body'],'collector',KEYS)
 cut=original['cut'];body={'reservation':req,'cut_id':cut['cut_id'],'intent_digest':cut['trace_header']['intent']['intent_digest'],'inventory':cut['ordered_inventory'],'attempt_mapping':[['attemptA','attempt:1']]+([['retained-attemptA2','attempt:2']] if source in ('prior-unresolved','later-unresolved','later-start-only') else []),'source_version':2 if source in ('prior-unresolved','later-unresolved','later-start-only','conflict','late-receipt','late-reconciliation') else 1,'terminal_nonexecution':source=='failure' and name!='generic-failure'}
 return {'original':original,'bundle':bundle,'binding':{'body':body,'mac':seal(body)},'identity':ec.dh({'name':name,'cut':cut,'records':original['records'],'binding':body})}
@functools.lru_cache(None)
def evaluate(name,mutant=None):
 x=fixture(name);b=x['binding']['body']
 try:
  ec.require(hmac.compare_digest(x['binding']['mac'],seal(b)),'reservation-binding-mac')
  r=joiner.join(x['bundle'],KEYS,mutant)
  ec.require(b['cut_id']==r['cut_id'] and b['intent_digest']==r['trace']['intent']['intent_digest'] and b['inventory']==r['ordered_inventory'],'reservation-cut-binding')
  if name in cases.EXPECTED:old.audit(x['original'],r,name)
  return {'accepted':True,'identity':x['identity'],'binding':b,'joined':r}
 except (ValueError,KeyError,TypeError,ec.schema.jsonschema.ValidationError,ec.m1a.M1AError) as e:
  return {'accepted':False,'identity':x['identity'],'binding':b,'error':type(e).__name__+': '+str(e)}
@functools.lru_cache(None)
def controls():
 rows={n:evaluate(n) for n in NAMES}
 for n in cases.EXPECTED:ec.require(rows[n]['accepted'],'positive literal cut '+n)
 for n in ('missing-original','contradictory','omitted','reordered','bad-mac','wrong-role'):ec.require(not rows[n]['accepted'],'negative literal cut '+n)
 # The shared oracle is independently challenged by a projection from complete original records.
 for n in cases.EXPECTED:
  x=fixture(n);r=rows[n]['joined'];exact=copy.deepcopy(x['original']['cut']['trace_header']);exact['observations']=x['original']['records'];exact.update({k:x['original']['cut']['assessment'][k] for k in ('current_admission_epoch','current_fence_epoch')});ec.require(r['trace']==exact,'independent full original trace')
 return {'cases':rows,'inputs':{n:fixture(n) for n in NAMES},'literal_pause':old.literal_controls(),'keys':'Public synthetic fixture keys only; not operational credentials','production_authentication':False}
