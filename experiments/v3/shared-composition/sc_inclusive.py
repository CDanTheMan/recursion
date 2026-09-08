"""Inclusive reducer: direct updates of the complete record."""
from dataclasses import replace
from sc_domain import State,base,fact,scheduled

def step(s,name,mutant=''):
    a=base(name)
    if a=='stage':return replace(s,staged=True,residents=s.residents|2)
    if a=='replace':return replace(s,serial=2)
    if a=='writer_boot':return replace(s,term=2)
    if a=='refresh':return replace(s,ticket=(s.term,s.serial))
    if a in ('publish','publish_old'):
        t=s.ticket if a=='publish' else (1,1)
        valid=(t[0]==s.term or mutant=='stale-term') and (t[1]==s.serial or mutant=='stale-serial')
        if s.g==1 and not s.stopped and not s.paused and valid and (s.staged or mutant=='unstaged'):
            return fact(s,g=2,residents=s.residents|2)
        return s
    if a=='writer_ack':return replace(s,reply=True) if s.g==2 else None
    if a=='capsule':return replace(s,capsule=True)
    if a=='return':return replace(s,actor=3)
    if a=='kill':return replace(s,actor=1,hold=False if mutant=='local-death' else s.hold)
    if a=='wait':return replace(s,actor=2) if s.actor==1 else None
    if a=='release':
        if s.actor not in (2,3) and mutant!='invocation-release':return None
        return replace(s,pin=False,reader=0 if mutant=='other-reader-release' else s.reader)
    if a in ('reclaim','reclaim_early'):
        allowed=s.g==2 and not s.pin and s.reader!=1 and s.capsule
        if mutant=='reclaim-reader':allowed=s.g==2 and not s.pin and s.capsule
        if mutant=='reclaim-history':allowed=s.g==2 and not s.pin and s.reader!=1
        if mutant=='reclaim-invocation':allowed=s.g==2 and s.reader!=1 and s.capsule
        return replace(s,residents=s.residents&2) if allowed else s
    if a=='execute':
        if s.remote!=0:return None
        ok=s.fence==1 or mutant=='recipient-fence'
        return replace(s,remote=1 if ok else 3,executions=1 if ok else 0)
    if a=='complete':return replace(s,remote=2) if s.remote==1 else None
    if a=='receipt':
        if s.remote not in (2,3) or s.cut!=0:return None
        return fact(s,cut=1 if s.remote==2 else 4,hold=False)
    if a=='second':
        if s.cut!=1:return None
        return fact(s,cut=2,hold=False if mutant=='status-only-hold' else True)
    if a=='conflict':
        if s.cut!=1:return None
        return fact(s,cut=3,hold=False if mutant=='pending-only-hold' else True)
    if a=='spawn2':
        if s.actor not in (2,3):return None
        return replace(s,incarnation=2,spent=s.spent+1)
    if a=='finish2':return replace(s,closed2=True) if s.incarnation==2 else None
    if a=='old_ack':return replace(s,ack=1,closed2=True if mutant=='ack-completion' else s.closed2)
    if a=='reset':return replace(s,reset=True,spent=0 if mutant=='reset-spend' else s.spent)
    if a=='fresh_write':return replace(s,write_result=2 if s.paused else 1)
    if a=='capture':
        if not s.journal or s.snapshot:return None
        return replace(s,snapshot=(s.g,len(s.journal),s.cut),reader=s.g,phase=1)
    if a=='copy':
        if s.phase!=1:return None
        return replace(s,copied=True,phase=2,reader=0 if mutant=='copy-release' else s.reader)
    if a=='reader_wait':return replace(s,reader=0,waited=True) if s.copied else None
    if a=='advertise':return replace(s,phase=3) if s.phase==2 else None
    if a=='detect_gap':return replace(s,gap=True) if len(s.journal)>s.view else None
    if a=='fresh_credit':return replace(s,credit=1) if s.phase in (4,5) and not s.gap else None
    if a=='emit_reset':
        if s.phase!=3 or (not s.gap and mutant!='unexpected-reset'):return None
        return replace(s,phase=4,gap=False,credit=s.credit if mutant=='reset-keeps-credit' else 0)
    if a=='broker_restart':
        if s.phase!=4:return None
        return replace(s,phase=2,restarted=True,view=s.snapshot[1] if mutant=='emission-install' else s.view)
    if a=='install':
        if s.phase!=4 or not s.copied or s.snapshot[1]<s.view:return None
        g,c,e=s.snapshot
        kw=dict(view=c,content=(g,e),phase=5,queue=tuple(i for i in s.queue if i>c),ingested=max(s.ingested,c))
        if mutant=='replay-settlement':kw.update(cut=e,hold=e not in (1,4))
        if mutant=='quarantine-clear':kw['quarantine']=False
        if mutant=='future-loss':kw['queue']=()
        return replace(s,**kw)
    if a=='ingest':
        if s.ingested>=len(s.journal) or len(s.queue)>=2:return None
        return replace(s,ingested=s.ingested+1,queue=s.queue+(s.ingested+1,))
    if a=='lose_ingress':
        if s.loss or s.ingested>=len(s.journal):return None
        return replace(s,ingested=s.ingested+1,loss=s.ingested+1)
    if a=='lose_queue':
        if s.loss or not s.queue:return None
        return replace(s,queue=s.queue[1:],loss=s.queue[0])
    if a=='event':
        if not s.queue or not s.credit:return None
        if s.gap:return None
        if s.phase==4 and mutant!='reset-order':return None
        if (s.queue[0]!=s.view+1 or s.view<s.loss) and mutant!='gap-order':return None
        i=s.queue[0]
        return replace(s,view=i,content=s.journal[i-1],queue=s.queue[1:],credit=0)
    raise ValueError(a)

def edges(s,profile,mutant=''):
    yield 'status',s
    if not s.stopped and not(mutant=='control-pressure' and (len(s.queue)==2 or s.phase==4)):
        yield 'stop',s if mutant=='control-apply' else replace(s,stopped=True)
    if not s.paused:yield 'pause',replace(s,paused=True)
    if (s.stopped or s.paused) and s.fence==1:yield 'fence',replace(s,fence=2)
    for a,bit in scheduled(s,profile):
        n=step(s,a,mutant)
        if n is not None:yield a,replace(n,done=s.done|bit)
