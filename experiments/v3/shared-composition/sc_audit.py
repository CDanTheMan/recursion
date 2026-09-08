"""Independent obligations, enabledness and action footprints (third relation).

No imports from either concrete transition implementation.
"""
from dataclasses import replace
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
    exact_postcondition(s,op,n)
    invariant(n)

def exact_postcondition(s,op,n):
    """Complete third relation, including broker-only and denied transitions.

The write footprint alone cannot establish that a present Stop edge applies
Stop. These independently specified assignments require every changed AND
unchanged field, including hidden transport stages, to have its exact value.
"""
    fixed={
      'status':{},'stop':{'stopped':True},'pause':{'paused':True},'fence':{'fence':2},
      'replace':{'serial':2},'writer_boot':{'term':2},'writer_ack':{'reply':True},
      'capsule':{'capsule':True},'return':{'actor':3},'kill':{'actor':1},'wait':{'actor':2},
      'release':{'pin':False},'complete':{'remote':2},'finish2':{'closed2':True},
      'old_ack':{'ack':1},'reset':{'reset':True},'copy':{'copied':True,'phase':2},
      'reader_wait':{'reader':0,'waited':True},'advertise':{'phase':3},
      'emit_reset':{'phase':4},'broker_restart':{'phase':2,'restarted':True}
    }
    if op in fixed:expected=fixed[op]
    elif op=='stage':expected={'staged':True,'residents':s.residents|2}
    elif op=='refresh':expected={'ticket':(s.term,s.serial)}
    elif op in ('publish','publish_old'):
        ticket=(1,1) if op=='publish_old' else s.ticket
        admitted=s.g==1 and s.staged and not s.stopped and not s.paused and ticket==(s.term,s.serial)
        expected={'g':2,'residents':3,'journal':s.journal+((2,s.cut),)} if admitted else {}
    elif op in ('reclaim','reclaim_early'):
        admitted=s.g==2 and not s.pin and s.reader!=1 and s.capsule
        expected={'residents':2} if admitted else {}
    elif op=='execute':expected={'remote':3 if s.fence==2 else 1,'executions':0 if s.fence==2 else 1}
    elif op in ('receipt','second','conflict'):
        cut=(1 if s.remote==2 else 4) if op=='receipt' else (2 if op=='second' else 3)
        expected={'cut':cut,'hold':cut in (2,3),'journal':s.journal+((s.g,cut),)}
    elif op=='spawn2':expected={'incarnation':2,'spent':s.spent+1}
    elif op=='fresh_write':expected={'write_result':2 if s.paused else 1}
    elif op=='capture':expected={'reader':s.g,'snapshot':(s.g,len(s.journal),s.cut),'phase':1}
    elif op=='install':
        gen,cursor,cut=s.snapshot
        expected={'view':cursor,'content':(gen,cut),'phase':5,'ingested':max(cursor,s.ingested),'queue':tuple(i for i in s.queue if i>cursor)}
    elif op=='ingest':expected={'ingested':s.ingested+1,'queue':(*s.queue,s.ingested+1)}
    elif op=='lose_ingress':expected={'ingested':s.ingested+1,'loss':s.ingested+1}
    elif op=='lose_queue':expected={'queue':s.queue[1:],'loss':s.queue[0]}
    elif op=='event':expected={'view':s.queue[0],'content':s.journal[s.queue[0]-1],'queue':s.queue[1:],'credit':0}
    else:raise ValueError('unspecified transition '+op)
    need(n==replace(s,done=n.done,**expected),'complete independent postcondition '+op)

def initial(s):need(s==State(),'initial state correspondence')
