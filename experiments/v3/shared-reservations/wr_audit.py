"""Independent obligations: no concrete transition implementation imports."""
from wr_domain import NAMES

def require(condition,message):
    if not condition:raise ValueError(message)

def invariant(s,design):
    for name in ('free','reserved','consumed','sent','remote','receipt','classification','reads','lifetime'):
        t=getattr(s,name);require(type(t) is tuple and len(t)==2 and all(type(x) is int for x in t),'typed '+name)
    require(all(x in (0,6) for x in s.reserved+s.consumed),'six-unit original demand')
    require(sum(s.reserved)+sum(s.consumed)<=10,'aggregate admitted capacity <= ten')
    require(all(0<=x<=10 for x in s.free),'nonnegative owned allowance')
    inflight=int(design=='rights' and s.transfer==1)
    require(sum(s.free)+inflight+sum(s.reserved)+sum(s.consumed)==10,'durable conservation')
    require(s.transfer in (0,1,2) and (design=='rights' or s.transfer==0),'transfer domain')
    require(s.lifetime[0]==1 and s.lifetime[1] in (0,1),'lifetime is not quota allowance')
    require(s.incarnation in (0,1) and s.quota_epoch in (0,1) and 0<=s.quota_used<=2,'local domains')
    require(s.worker in (0,1,2) and s.generation in (1,2) and s.boot in (0,1),'lifecycle domains')
    for i in range(2):
        bit=1<<i
        suffix='AB'[i];binding=('pool10','goal'+suffix,'op'+suffix,'attempt'+suffix,'payload'+suffix,'owner'+suffix,6)
        require(s.bindings[i]==(binding if s.issued&bit else ()),'immutable reservation identity/owner')
        require(s.sent[i] in (0,1),'no blind ambiguous redispatch')
        require(s.remote[i] in (0,1,2) and s.receipt[i] in (0,1,2) and s.classification[i] in (0,1,2),'evidence domains')
        require(not s.receipt[i] or s.receipt[i]==s.remote[i],'exact-operation retained receipt')
        require(not s.classification[i] or s.classification[i]==s.receipt[i],'classification requires receipt')
        require(not s.intent&bit or s.issued&bit,'intent requires durable reservation identity')
        require(not s.sent[i] or s.intent&bit,'send requires intent')
        if s.sent[i] and (not s.classification[i] or s.conflict&bit):require(s.reserved[i]==6,'uncertainty retains effect reservation')
        if s.consumed[i]:require(s.classification[i]==1 and s.reserved[i]==0,'settled consumption backing')
        if s.issued&bit and s.reserved[i]==0 and s.consumed[i]==0:
            require(s.classification[i]==2 and not s.conflict&bit,'only proven nonexecution frees budget')
    require(not s.installed or s.copied,'installation needs independent copied snapshot')
    require(s.installed_cursor==(s.installed[0] if s.installed else 0) and 0<=s.replay_cursor<=s.revision,'separate installed/replayed cursors')

def initial(s,design):
    expected={n:0 for n in NAMES}
    expected.update(free=(10,0) if design=='central' else (5,5),reserved=(0,0),consumed=(0,0),bindings=((),()),sent=(0,0),remote=(0,0),receipt=(0,0),classification=(0,0),reads=(-1,-1),ack=False,lifetime=(1,0),quota_used=1,generation=1,reader_pin=False,snapshot=(),copied=False,installed=())
    require(all(getattr(s,n)==v for n,v in expected.items()),'independent initial relation');invariant(s,design)

def enabled(s,p,labels):
    allowed={'status'}
    for j,a in enumerate(p['actions']):
        if s.done&(1<<j):continue
        if all(s.done&(1<<p['actions'].index(dep)) for dep in p['requires'][a]):allowed.add(a)
    actual=[label.split('=')[0] for label in labels]
    require(len(actual)==len(set(actual)) and set(actual)==allowed,'complete independent enabledness')

def edge(s,label,t,p,design):
    """Full postconditions and unchanged-field check, separately expressed."""
    invariant(t,design)
    a,out=label.split('=');changes={};expected='ok'
    def at(name,index,value):
        old=getattr(s,name);changes[name]=tuple(value if j==index else old[j] for j in range(2))
    i=int(a[-1]) if a[-1].isdigit() else 0;b=1<<i;h=i if design=='rights' else 0
    if a=='status':pass
    elif a in ('read0','read1'):at('reads',i,s.free[h])
    elif a in ('reserve0','reserve1','duplicate0','duplicate1'):
        expected='duplicate' if s.issued&b else ('admitted' if s.free[h]>=6 else 'denied')
        if expected=='admitted':
            suffix='AB'[i];at('bindings',i,('pool10','goal'+suffix,'op'+suffix,'attempt'+suffix,'payload'+suffix,'owner'+suffix,6))
            at('free',h,s.free[h]-6);at('reserved',i,6);changes.update(issued=s.issued|b,revision=s.revision+1)
    elif a.startswith(('wrong_owner','foreign_release')):expected='owner-refused'
    elif a.startswith('changed_payload'):expected='payload-conflict'
    elif a.startswith(('wrong_goal','changed_amount','changed_attempt')):expected='identity-conflict'
    elif a.startswith('intent'):
        expected='ok' if s.reserved[i]==6 and not s.intent&b else 'denied'
        if expected=='ok':changes.update(intent=s.intent|b,revision=s.revision+1)
    elif a.startswith(('send','resend')):
        expected='sent' if s.intent&b and s.sent[i]==0 and s.reserved[i]==6 else 'blocked'
        if expected=='sent':at('sent',i,1);changes['revision']=s.revision+1
    elif a.startswith(('accept','refuse')):
        expected='ok' if s.sent[i] and s.remote[i]==0 else 'unavailable'
        if expected=='ok':at('remote',i,1 if a.startswith('accept') else 2)
    elif a.startswith('lose'):
        expected='ok' if s.remote[i] and not s.receipt[i] else 'unavailable'
        if expected=='ok':changes['quarantine']=s.quarantine|b
    elif a.startswith(('receive','query')):
        expected='ok' if s.remote[i] else 'unknown'
        if expected=='ok':at('receipt',i,s.remote[i]);changes['revision']=s.revision+1
    elif a.startswith('classify'):
        expected='ok' if s.receipt[i] else 'unknown'
        if expected=='ok':at('classification',i,s.receipt[i])
    elif a.startswith('conflict'):
        expected='ok' if s.classification[i] else 'unavailable'
        if expected=='ok':changes.update(conflict=s.conflict|b,quarantine=s.quarantine|b)
    elif a.startswith(('reconcile','settle_again')):
        expected='duplicate' if s.reserved[i]==0 else ('settled' if s.classification[i] and not s.conflict&b else 'held')
        if expected=='settled':
            at('reserved',i,0);changes['revision']=s.revision+1
            if s.classification[i]==1:at('consumed',i,s.consumed[i]+6)
            else:at('free',h,s.free[h]+6)
    elif a=='transfer_debit':
        expected='not-applicable' if design=='central' else ('ok' if s.transfer==0 and s.free[p['source']]>=1 else 'denied')
        if expected=='ok':at('free',p['source'],s.free[p['source']]-1);changes.update(transfer=1,revision=s.revision+1)
    elif a in ('transfer_install','transfer_duplicate'):
        expected='not-applicable' if design=='central' else {0:'unavailable',1:'ok',2:'duplicate'}[s.transfer]
        if expected=='ok':at('free',1-p['source'],s.free[1-p['source']]+1);changes.update(transfer=2,revision=s.revision+1)
    elif a=='transfer_timeout':expected='held' if design=='rights' and s.transfer else 'not-applicable'
    elif a=='transfer_ack':
        expected='ok' if design=='rights' and s.transfer==2 else 'unavailable'
        if expected=='ok':changes['ack']=True
    elif a=='restart':changes.update(boot=1,ack=False,replay_cursor=0)
    elif a=='replay':changes['replay_cursor']=s.revision
    elif a=='quota_reset':changes.update(quota_epoch=1,quota_used=0)
    elif a=='exit':changes['worker']=1
    elif a=='wait':
        expected='ok' if s.worker==1 else 'unavailable'
        if expected=='ok':changes['worker']=2
    elif a=='new_worker':
        expected='ok' if s.worker==2 and s.incarnation==0 else 'denied'
        if expected=='ok':changes.update(incarnation=1,worker=0)
    elif a=='compute':
        expected='ok' if s.worker==0 and s.incarnation==1 and not s.lifetime[1] else 'denied'
        if expected=='ok':at('lifetime',1,1);changes['quota_used']=s.quota_used+1
    elif a=='publish':changes['generation']=2
    elif a=='capture':changes.update(snapshot=(s.revision,s.free,s.reserved,s.consumed,s.transfer,s.generation),reader_pin=True)
    elif a=='copy':
        expected='ok' if s.snapshot else 'unavailable'
        if expected=='ok':changes['copied']=True
    elif a=='reader_wait':
        expected='ok' if s.copied else 'unavailable'
        if expected=='ok':changes['reader_pin']=False
    elif a=='install':
        expected='ok' if s.copied else 'unavailable'
        if expected=='ok':changes.update(installed=s.snapshot,installed_cursor=s.snapshot[0])
    elif a=='restore_old':expected='stale-rejected' if s.snapshot and s.snapshot[0]!=s.revision else 'no-change'
    else:raise ValueError('unknown independent action '+a)
    if a!='status':changes['done']=s.done|(1<<p['actions'].index(a))
    require(out==expected,'independent outcome '+a)
    for n in NAMES:require(getattr(t,n)==changes.get(n,getattr(s,n)),'independent postcondition/ownership '+a+'/'+n)
