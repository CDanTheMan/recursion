"""Independent obligations, enabledness and action footprints (third relation).

No imports from either concrete transition implementation.
"""
from sc_domain import State,NAMES,PROFILES

def need(condition,label):
    if not condition:raise ValueError(label)

FOOTPRINT={
 'status':(), 'stop':('stopped',),'pause':('paused',),'fence':('fence',),
 'stage':('staged','residents'),'replace':('serial',),'writer_boot':('term',),
 'refresh':('ticket',),'publish':('g','residents','journal'),
 'publish_old':('g','residents','journal'),'writer_ack':('reply',),
 'capsule':('capsule',),'return':('actor',),'kill':('actor',),'wait':('actor',),
 'release':('pin',),'reclaim':('residents',),'reclaim_early':('residents',),
 'execute':('remote','executions'),'complete':('remote',),
 'receipt':('cut','hold','journal'),'second':('cut','hold','journal'),
 'conflict':('cut','hold','journal'),'spawn2':('incarnation','spent'),
 'finish2':('closed2',),'old_ack':('ack',),'reset':('reset',),'fresh_write':('write_result',),
 'capture':('snapshot','reader','phase'),'copy':('copied','phase'),
 'reader_wait':('reader','waited'),'advertise':('phase',),'emit_reset':('phase',),
 'broker_restart':('phase','restarted'),
 'install':('view','content','phase','queue','ingested'),
 'ingest':('ingested','queue'),'lose_ingress':('ingested','loss'),
 'lose_queue':('queue','loss'),'event':('view','content','queue','credit')
}

def invariant(s):
    need(s.quarantine,'canonical quarantine is not a replay/receipt output')
    need(s.hold==(s.cut not in (1,4)),'settlement hold differs from literal success/pending-only shortcut')
    need(s.spent==s.incarnation and 1<=s.spent<=2,'lifetime compute is independent of quota reset')
    need(s.residents&(1<<(s.g-1)),'selected generation resident')
    need(not s.pin or s.residents&1,'invocation pin resident')
    need(not s.reader or s.residents&(1<<(s.reader-1)),'reader pin resident')
    need(s.residents&1 or s.capsule,'history retained before reclamation')
    need(not s.snapshot or s.waited or s.reader==s.snapshot[0],'reader ownership survives copy and other completion')
    need(not s.waited or (s.copied and s.reader==0),'owned reader wait after copy')
    need(not s.reply or s.g==2,'reply acknowledges committed publication')
    need(s.executions==(1 if s.remote in (1,2) else 0),'at most one bounded recipient effect')
    need(0<=s.view<=s.ingested<=len(s.journal)<=3,'view/source bounds')
    need(len(s.queue)<=2 and tuple(sorted(set(s.queue)))==s.queue,'bounded unique ordered queue')
    need(all(s.view<i<=s.ingested for i in s.queue),'queue owns only undelivered offered entries')
    need(all(i in s.queue or i==s.loss for i in range(s.view+1,s.ingested+1)),'future presentation ownership')
    need(s.content==((1,0) if not s.view else s.journal[s.view-1]),'installed content matches installed cursor')
    if s.snapshot:
        g,c,e=s.snapshot
        need(1<=c<=len(s.journal) and s.journal[c-1]==(g,e),'snapshot immutable exact source cut')
    need(not s.closed2 or s.incarnation==2,'completion belongs to incarnation')

def permitted(s,op):
    # Requirement-side enabling predicates, independently stated.
    if op=='status':return True
    if op=='stop':return not s.stopped
    if op=='pause':return not s.paused
    if op=='fence':return s.fence<2 and (s.stopped or s.paused)
    if op=='writer_ack':return s.g==2
    if op=='wait':return s.actor==1
    if op=='release':return s.actor>=2
    if op=='execute':return s.remote==0
    if op=='complete':return s.remote==1
    if op=='receipt':return s.cut==0 and s.remote>=2
    if op in ('second','conflict'):return s.cut==1
    if op=='spawn2':return s.actor>=2
    if op=='finish2':return s.incarnation==2
    if op=='capture':return len(s.journal)>0 and len(s.snapshot)==0
    if op=='copy':return s.phase==1
    if op=='reader_wait':return s.copied
    if op=='advertise':return s.phase==2
    if op=='emit_reset':return s.phase==3
    if op=='broker_restart':return s.phase==4
    if op=='install':return s.phase==4 and s.copied and s.snapshot[1]>=s.view
    if op=='ingest':return len(s.queue)<2 and s.ingested<len(s.journal)
    if op=='lose_ingress':return s.loss==0 and s.ingested<len(s.journal)
    if op=='lose_queue':return s.loss==0 and len(s.queue)>0
    if op=='event':return s.credit>0 and len(s.queue)>0 and s.queue[0]==s.view+1 and s.loss<=s.view and s.phase!=4
    return True

def enabled(s,profile,actual):
    expected={a for a in ('status','stop','pause','fence') if permitted(s,a)}
    rows=PROFILES[profile];completed={a for i,(a,_) in enumerate(rows) if s.done&(2**i)}
    for name,deps in rows:
        if name not in completed and all(d in completed for d in deps) and permitted(s,name.partition(':')[0]):expected.add(name)
    need(len(actual)==len(set(actual)) and set(actual)==expected,'complete independent enabledness / responsive Stop')

def edge(s,name,n,profile):
    op=name.partition(':')[0]
    changed={k for k in NAMES if getattr(s,k)!=getattr(n,k)}
    need(changed<=set(FOOTPRINT[op])|{'done'},'authority/ownership write footprint: '+op)
    if op in ('status','stop','pause','fence'):need(n.done==s.done,'control cannot consume environment actions')
    else:
        index=[a for a,_ in PROFILES[profile]].index(name)
        need(n.done==s.done|(1<<index),'exact external action accounting')
    need(n.journal[:len(s.journal)]==s.journal,'append-only presentation facts')
    if op in ('publish','publish_old'):
        ticket=s.ticket if op=='publish' else (1,1)
        allowed=s.g==1 and s.staged and not s.stopped and not s.paused and ticket==(s.term,s.serial)
        need((n.g!=s.g)==allowed,'complete current writer ticket and admission before commit')
    if op.startswith('reclaim') and n.residents!=s.residents:
        need(s.g==2 and not s.pin and s.reader!=1 and s.capsule,'reclamation requires all independent owners')
    if op=='release':need(s.actor in (2,3),'wait or return precedes invocation release')
    if op=='execute':need(n.remote==(1 if s.fence==1 else 3),'installed recipient fence refusal')
    if op=='receipt':need(n.cut==(1 if s.remote==2 else 4),'receipt names actual retained outcome')
    if op in ('second','conflict'):need(n.cut==(2 if op=='second' else 3),'literal inventory extension identity')
    if op=='capture':need(n.snapshot==(s.g,len(s.journal),s.cut) and n.reader==s.g,'snapshot cut and generation-specific pin')
    if op=='install':
        g,c,e=s.snapshot
        need(n.content==(g,e) and n.view==c and n.queue==tuple(i for i in s.queue if i>c) and n.ingested==max(c,s.ingested),'install exact copied cut, retain newer entries')
    if op=='event':need(s.phase!=4 and s.view>=s.loss and n.view==s.view+1,'no EVENT over gap or uninstalled RESET')
    if op=='fresh_write':need(n.write_result==(2 if s.paused else 1),'PAUSE checked by fresh writer separately')
    for flag in ('stopped','paused','quarantine','capsule'):
        need(not getattr(s,flag) or getattr(n,flag),'monotone retained '+flag)
    invariant(n)

def initial(s):need(s==State(),'initial state correspondence')
