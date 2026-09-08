"""Immutable finite fixture inputs, literal evidence join, and synthetic binding codec."""
import pathlib,sys,copy,functools,hashlib,hmac,json
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'experiments/v3/effect-evidence'))
import ee_common as ec,ee_cases as cases,ee_join as joiner,ee_experiment as old
KEYS={k:('PUBLIC-SYNTHETIC-CUT-PAUSE-TEST-KEY/'+k).encode() for k in ('collector','dispatcher','observer')}
REQUESTS=(('pool10','goalA','opA','attemptA','payloadA','ownerA',6),('pool10','goalB','opB','attemptB','payloadB','ownerB',6))
NAMES=tuple(cases.EXPECTED)+('missing-original','contradictory','omitted','reordered','bad-mac','wrong-role','foreign','foreign-attempt','generic-failure','bad-attempt-map','missing-attempt-map','bad-source-version','bool-source-version')
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
 cut=original['cut'];body={'reservation':req,'cut_id':cut['cut_id'],'intent_digest':cut['trace_header']['intent']['intent_digest'],'inventory':cut['ordered_inventory'],'attempt_mapping':[[req[3],'attempt:1']]+([['retained-attemptA2','attempt:2']] if source in ('prior-unresolved','later-unresolved','later-start-only') else []),'source_version':2 if source in ('prior-unresolved','later-unresolved','later-start-only','conflict','late-receipt','late-reconciliation') else 1,'terminal_nonexecution':source=='failure' and name!='generic-failure'}
 if name=='bad-attempt-map':body['attempt_mapping']=[[req[3],'attempt:2']]
 if name=='missing-attempt-map':body['attempt_mapping']=[]
 if name=='bad-source-version':body['source_version']=-100
 if name=='bool-source-version':body['source_version']=True
 return {'original':original,'bundle':bundle,'binding':{'body':body,'mac':seal(body)},'identity':ec.dh({'name':name,'cut':cut,'records':original['records'],'binding':body})}
@functools.lru_cache(None)
def evaluate(name,mutant=None):
 x=fixture(name);b=x['binding']['body']
 try:
  ec.require(hmac.compare_digest(x['binding']['mac'],seal(b)),'reservation-binding-mac')
  r=joiner.join(x['bundle'],KEYS,mutant)
  starts=[a for a in r['trace']['observations'] if a['type']=='AttemptStarted@1']
  mapping=[[b['reservation'][3] if a['attempt_number']==1 else 'retained-attemptA'+str(a['attempt_number']),a['attempt_id']] for a in starts]
  ec.require(b['attempt_mapping']==mapping,'complete-original-attempt-mapping')
  version=2 if len(r['trace']['observations'])>x['original']['cut']['prefix_length'] else 1
  ec.require(type(b['source_version']) is int and b['source_version']==version,'typed-source-version')
  ec.require(type(b['terminal_nonexecution']) is bool,'typed-nonexecution-evidence')
  ec.require(b['cut_id']==r['cut_id'] and b['intent_digest']==r['trace']['intent']['intent_digest'] and b['inventory']==r['ordered_inventory'],'reservation-cut-binding')
  if name in cases.EXPECTED:old.audit(x['original'],r,name)
  return {'accepted':True,'identity':x['identity'],'binding':b,'joined':r}
 except (ValueError,KeyError,TypeError,ec.schema.jsonschema.ValidationError,ec.m1a.M1AError) as e:
  return {'accepted':False,'identity':x['identity'],'binding':b,'error':type(e).__name__+': '+str(e)}
@functools.lru_cache(None)
def controls():
 rows={n:evaluate(n) for n in NAMES}
 for n in cases.EXPECTED:ec.require(rows[n]['accepted'],'positive literal cut '+n)
 for n in ('missing-original','contradictory','omitted','reordered','bad-mac','wrong-role','bad-attempt-map','missing-attempt-map','bad-source-version','bool-source-version'):ec.require(not rows[n]['accepted'],'negative literal cut '+n)
 # The shared oracle is independently challenged by a projection from complete original records.
 for n in cases.EXPECTED:
  x=fixture(n);r=rows[n]['joined'];exact=copy.deepcopy(x['original']['cut']['trace_header']);exact['observations']=x['original']['records'];exact.update({k:x['original']['cut']['assessment'][k] for k in ('current_admission_epoch','current_fence_epoch')});ec.require(r['trace']==exact,'independent full original trace')
 return {'cases':rows,'inputs':{n:fixture(n) for n in NAMES},'literal_pause':old.literal_controls(),'coupled_observations':{n+'/'+str(paused)+'/'+str(duplicate):observation(n,paused,n if duplicate else '') for n in cases.EXPECTED for paused in (False,True) for duplicate in (False,True)},'keys':'Public synthetic fixture keys only; not operational credentials','production_authentication':False}

@functools.lru_cache(None)
def observation(name,paused,previous='',conflict=False,remove_pause=False):
    fixture,state,journal=ec.running();policies=fixture['policy_fixtures']
    def command(which,conflicting=False):
        c=copy.deepcopy(fixture['commands'][-1]);original=globals()['fixture'](which)['original']['cut']['context']['observation'];c['payload']=copy.deepcopy(original)
        if conflicting:c['payload']['payload']['idempotency_key_digest']='f'*64
        return old.authorized(fixture,c,state,20)
    current,authorities=command(name,conflict)
    original_current=copy.deepcopy(current)
    if previous:
        prior,pa=command(previous);state,events,receipt,journal=ec.kernel.admit(state,state['content_digest'],prior,pa,policies,journal)
        ec.require(receipt['disposition']=='accepted' and len(events)==1,'coupled prior observation admitted')
    if paused:
        pc,pa=old.authorized(fixture,fixture['commands'][0],state,30)
        state,events,receipt,journal=ec.kernel.admit(state,state['content_digest'],pc,pa,policies,journal)
        ec.require(receipt['disposition']=='accepted','coupled literal apply-pause')
    current=ec.rebind(current,state);before=copy.deepcopy(state);prior_journal=len(journal);guard=ec.contracts.PAUSE_SENSITIVE
    try:
        if remove_pause:ec.contracts.PAUSE_SENSITIVE=guard-{'record-effect-observation'}
        after,events,receipt,newjournal=ec.kernel.admit(state,state['content_digest'],current,authorities,policies,journal)
    finally:ec.contracts.PAUSE_SENSITIVE=guard
    source=globals()['fixture'](name)['original']['cut']['context']['observation']
    ec.require(original_current['payload']==current['payload'],'otherwise identical running/paused command payload')
    if not conflict:ec.require(source['payload']==current['payload']['payload'],'actual joined observation payload preserved')
    return {'source_observation_digest':source['content_digest'],'source_observation':source,'mapped_command':current,'receipt':receipt,'events':events,'projection_unchanged':before==after,'journal_growth':len(newjournal)-prior_journal,'fixture_epoch_mapping':'model pause serial=M1A pause_epoch+1; original admission stays separate','record_mapping':'Exact retained effect-observation payload; runtime record metadata resealed at synthetic logical time20 and authority fixture bound to that candidate; no production grant'}
