"""Finite, explicitly restricted environments; no product or provider operations."""
from dataclasses import dataclass, fields, replace

@dataclass(frozen=True, slots=True)
class State:
    g:int=1
    residents:int=1
    staged:bool=False
    term:int=1
    serial:int=1
    ticket:tuple=(1,1)
    reply:bool=False
    capsule:bool=False
    actor:int=0  # running, killed, waited, returned
    pin:bool=True
    reader:int=0
    copied:bool=False
    waited:bool=False
    stopped:bool=False
    paused:bool=False
    fence:int=1
    remote:int=0  # issued, executed, completed, refused
    executions:int=0
    cut:int=0  # unknown, success, later start, conflict, refusal
    hold:bool=True
    quarantine:bool=True
    incarnation:int=1
    closed2:bool=False
    spent:int=1
    reset:bool=False
    ack:int=0
    write_result:int=0
    journal:tuple=()
    ingested:int=0
    queue:tuple=()
    loss:int=0
    credit:int=1
    view:int=0
    content:tuple=(1,0)
    snapshot:tuple=()
    phase:int=0  # absent, captured, copied, advertised, emitted, installed
    restarted:bool=False
    done:int=0

BROKER=('reader','copied','waited','ingested','queue','loss','credit','view','content','snapshot','phase','restarted')
AUTH=tuple(f.name for f in fields(State) if f.name not in BROKER)
NAMES=tuple(f.name for f in fields(State))
def key(s):return tuple(getattr(s,n) for n in NAMES)
def base(a):return a.split(':')[0]
def fact(s,**kw):
    n=replace(s,**kw)
    return replace(n,journal=s.journal+((n.g,n.cut),))

# Each action instance can be attempted once. Prerequisites constrain only the
# declared external schedule; production guards are independently implemented.
# Stop, status, PAUSE and recipient installation are available in every profile.
PROFILES={
 'free-shared-core':[(a,()) for a in ('stage','publish','execute','complete','receipt','second','capture','copy','reader_wait','advertise','emit_reset','install','return','release','capsule','reclaim')],
 'ownership-probes':[
  ('stage',()),('publish',('stage',)),('return',()),('release:early',()),
  ('release',('return',)),('capsule',()),('reclaim:probe',('publish',))],
 'recipient-refusal': [('execute',()),('complete',('execute',)),('receipt',('execute',))],
 'old-cut-new-attempt':[
  ('execute',()),('complete',('execute',)),('receipt',('complete',)),
  ('capture',('receipt',)),('second',('capture',)),('copy',('capture',)),
  ('advertise',('copy',)),('emit_reset',('advertise',)),('install',('emit_reset','second'))],
 'reader-reclaim-install':[
  ('execute',()),('complete',('execute',)),('receipt',('complete',)),
  ('capture',('receipt',)),('stage',('capture',)),('publish',('stage',)),
  ('return',()),('release',('return',)),('capsule',()),
  ('reclaim_early',('publish','release')),('copy',('capture',)),('reader_wait',('copy',)),
  ('reclaim',('publish','release','reader_wait','capsule')),('advertise',('copy',)),
  ('emit_reset',('advertise',)),('install',('emit_reset','reclaim'))],
 'writer-serial-and-boot':[
  ('stage',()),('replace',()),('publish_old',('replace','stage')),
  ('refresh',('publish_old',)),('publish',('refresh','stage')),
  ('writer_boot',('publish',)),('writer_ack',('writer_boot',))],
 'writer-stale-boot':[
  ('stage',()),('writer_boot',()),('publish_old',('writer_boot','stage')),
  ('refresh',('publish_old',)),('publish',('refresh',))],
 'writer-unstaged': [('publish_old',()),('stage',('publish_old',)),('publish',('stage',))],
 'queue-gap-stop':[
  ('execute',()),('complete',('execute',)),('receipt',('complete',)),
  ('stage',()),('publish',('stage',)),('ingest:1',()),('ingest:2',('ingest:1',)),
  ('lose_queue',('ingest:2',)),('event',('lose_queue',)),
  ('capture',('lose_queue',)),('copy',('capture',)),('advertise',('copy',)),
  ('emit_reset',('advertise',)),('install',('emit_reset',))],
 'late-evidence-local-death':[
  ('execute',()),('complete',('execute',)),('kill',()),('wait',('kill',)),
  ('release',('wait',)),('stage',()),('publish',('stage',)),('capsule',()),
  ('reclaim',('publish','release','capsule')),('capture',('publish',)),
  ('copy',('capture',)),('advertise',('copy',)),('emit_reset',('advertise',)),
  ('install',('emit_reset',)),('receipt',('install','wait','complete'))],
 'conflict-pause':[
  ('execute',()),('complete',('execute',)),('receipt',('complete',)),
  ('conflict',('receipt',)),('capture',('conflict',)),('copy',('capture',)),
  ('advertise',('copy',)),('emit_reset',('advertise',)),('install',('emit_reset',)),
  ('fresh_write',('install',))],
 'reset-restart-future-output':[
  ('execute',()),('complete',('execute',)),('receipt',('complete',)),
  ('capture',('receipt',)),('copy',('capture',)),('advertise',('copy',)),
  ('emit_reset',('advertise',)),('broker_restart',('emit_reset',)),
  ('second',('capture',)),('ingest:1',()),('ingest:2',('ingest:1',)),
  ('event',('emit_reset',)),('advertise:again',('broker_restart',)),
  ('emit_reset:again',('advertise:again',)),('install',('emit_reset:again','second'))],
 'reset-incarnation-accounting':[
  ('return',()),('release',('return',)),('spawn2',('release',)),
  ('reset',()),('old_ack',('spawn2',)),('finish2',('old_ack',)),
  ('execute',()),('complete',('execute',)),('receipt',('complete',)),
  ('capture',('receipt',)),('copy',('capture',)),('advertise',('copy',)),
  ('emit_reset',('advertise',)),('install',('emit_reset',))],
 'pre-ingress-gap':[
  ('stage',()),('publish',('stage',)),('execute',()),('complete',('execute',)),
  ('receipt',('complete',)),('lose_ingress',()),('ingest:1',('lose_ingress',)),
  ('event',('ingest:1',)),('capture',('lose_ingress',)),('copy',('capture',)),
  ('advertise',('copy',)),('emit_reset',('advertise',)),('install',('emit_reset',))]
}
def scheduled(s,profile):
    rows=PROFILES[profile];ids={a:i for i,(a,_) in enumerate(rows)}
    return [(a,1<<i) for i,(a,deps) in enumerate(rows)
            if not s.done&(1<<i) and all(s.done&(1<<ids[d]) for d in deps)]
