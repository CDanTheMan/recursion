"""Separate authority and broker records, with declarative guarded transactions.

This implementation does not call the inclusive reducer or its update helper.
The shared domain supplies field names and restricted external schedules only.
"""
from dataclasses import dataclass
from sc_domain import State,AUTH,BROKER,PROFILES

@dataclass(frozen=True,slots=True)
class Split:
    authority:tuple
    broker:tuple

def pack(s):return Split(tuple(getattr(s,n) for n in AUTH),tuple(getattr(s,n) for n in BROKER))
def flat(s):return State(**dict(zip(AUTH,s.authority)),**dict(zip(BROKER,s.broker)))
def transaction(s,updates):
    a=dict(zip(AUTH,s.authority));b=dict(zip(BROKER,s.broker))
    for k,v in updates.items():
        (b if k in BROKER else a)[k]=v
    return Split(tuple(a[n] for n in AUTH),tuple(b[n] for n in BROKER))

def edges(record,profile):
    x=flat(record);rows=PROFILES[profile]
    # Values describe one transaction across the component boundary. No broker
    # transaction is allowed to overwrite an authority record during install.
    allowed={
      'status':True,'stop':not x.stopped,'pause':not x.paused,
      'fence':(x.stopped or x.paused) and x.fence==1,
      'stage':True,'replace':True,'writer_boot':True,'refresh':True,
      'publish':True,'publish_old':True,'writer_ack':x.g==2,
      'capsule':True,'return':True,'kill':True,'wait':x.actor==1,
      'release':x.actor in (2,3),'reclaim':True,'reclaim_early':True,
      'execute':x.remote==0,'complete':x.remote==1,
      'receipt':x.cut==0 and x.remote in (2,3),'second':x.cut==1,'conflict':x.cut==1,
      'spawn2':x.actor in (2,3),'finish2':x.incarnation==2,'old_ack':True,
      'reset':True,'fresh_write':True,'capture':bool(x.journal) and not x.snapshot,
      'copy':x.phase==1,'reader_wait':x.copied,'advertise':x.phase==2,
      'emit_reset':x.phase==3,'broker_restart':x.phase==4,
      'install':x.phase==4 and x.copied and bool(x.snapshot) and x.snapshot[1]>=x.view,
      'ingest':x.ingested<len(x.journal) and len(x.queue)<2,
      'lose_ingress':x.loss==0 and x.ingested<len(x.journal),
      'lose_queue':x.loss==0 and bool(x.queue),
      'event':bool(x.queue) and x.credit>0 and x.phase!=4 and x.queue[0]==x.view+1 and x.view>=x.loss
    }
    changes={
      'status':{},'stop':{'stopped':True},'pause':{'paused':True},'fence':{'fence':2},
      'stage':{'staged':True,'residents':x.residents|2},
      'replace':{'serial':2},'writer_boot':{'term':2},'refresh':{'ticket':(x.term,x.serial)},
      'writer_ack':{'reply':True},'capsule':{'capsule':True},'return':{'actor':3},
      'kill':{'actor':1},'wait':{'actor':2},'release':{'pin':False},
      'complete':{'remote':2},'spawn2':{'incarnation':2,'spent':x.spent+1},
      'finish2':{'closed2':True},'old_ack':{'ack':1},'reset':{'reset':True},
      'fresh_write':{'write_result':2 if x.paused else 1},
      'capture':{'snapshot':(x.g,len(x.journal),x.cut),'reader':x.g,'phase':1},
      'copy':{'copied':True,'phase':2},'reader_wait':{'reader':0,'waited':True},
      'advertise':{'phase':3},'emit_reset':{'phase':4},
      'broker_restart':{'phase':2,'restarted':True},
      'ingest':{'ingested':x.ingested+1,'queue':x.queue+(x.ingested+1,)},
      'lose_ingress':{'ingested':x.ingested+1,'loss':x.ingested+1}
    }
    for action,ticket in [('publish',x.ticket),('publish_old',(1,1))]:
        changes[action]={}
        if x.g==1 and x.staged and not(x.stopped or x.paused) and ticket==(x.term,x.serial):
            changes[action]={'g':2,'residents':x.residents|2,'journal':x.journal+((2,x.cut),)}
    can_reclaim=x.g==2 and not x.pin and x.reader!=1 and x.capsule
    for action in ('reclaim','reclaim_early'):changes[action]={'residents':x.residents&2} if can_reclaim else {}
    changes['execute']={'remote':1,'executions':1} if x.fence==1 else {'remote':3,'executions':0}
    terminal=1 if x.remote==2 else 4
    changes['receipt']={'cut':terminal,'hold':False,'journal':x.journal+((x.g,terminal),)}
    for action,c in [('second',2),('conflict',3)]:
        changes[action]={'cut':c,'hold':True,'journal':x.journal+((x.g,c),)}
    if x.snapshot:
        gen,cursor,evidence=x.snapshot
        changes['install']={'view':cursor,'content':(gen,evidence),'phase':5,
          'queue':tuple(i for i in x.queue if i>cursor),'ingested':max(x.ingested,cursor)}
    if x.queue:
        cursor=x.queue[0]
        changes['lose_queue']={'queue':x.queue[1:],'loss':cursor}
        changes['event']={'queue':x.queue[1:],'view':cursor,'content':x.journal[cursor-1],'credit':0}
    for action in ('status','stop','pause','fence'):
        if allowed[action]:yield action,transaction(record,changes[action])
    completed={a for i,(a,_) in enumerate(rows) if x.done>>i&1}
    for i,(action,dependencies) in enumerate(rows):
        if action in completed or not set(dependencies)<=completed:continue
        operation=action.partition(':')[0]
        if allowed[operation]:
            yield action,transaction(record,dict(changes[operation],done=x.done|(1<<i)))
