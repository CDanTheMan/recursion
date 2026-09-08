"""Inclusive concrete reducer. Audit and split reducer are not imported."""
from dataclasses import replace
from wr_domain import available, finish, request_input, REQUESTS

def put(t,i,v): return t[:i]+(v,)+t[i+1:]

def step(s,a,p,design,mutant=None):
    d={}; outcome='ok'; i=int(a[-1]) if a[-1].isdigit() else 0; bit=1<<i
    holder=i if design=='rights' else 0
    if a.startswith('read') and a[-1].isdigit(): d['reads']=put(s.reads,i,s.free[holder])
    elif a.startswith(('reserve','duplicate','wrong_owner','changed_payload','wrong_goal','changed_amount','changed_attempt')):
        request=request_input(a)
        expected=s.bindings[i] if s.issued&bit else REQUESTS[i]
        if request[5]!=expected[5] and mutant!='owner-binding':outcome='owner-refused'
        elif request[4]!=expected[4] and mutant!='payload-binding':outcome='payload-conflict'
        elif any(request[k]!=expected[k] for k in (0,1,2,3,6)) and mutant!='identity-binding':outcome='identity-conflict'
        elif s.issued & bit: outcome='duplicate'
        else:
            balance=s.reads[i] if mutant=='serialization' and s.reads[i]>=0 else s.free[holder]
            if balance<6:outcome='denied'
            else:
                d.update(free=put(s.free,holder,s.free[holder]-6),reserved=put(s.reserved,i,6),issued=s.issued|bit,bindings=put(s.bindings,i,request),revision=s.revision+1);outcome='admitted'
    elif a.startswith('foreign_release'):
        request=request_input(a)
        if request[5]!=s.bindings[i][5] and mutant!='foreign-release':outcome='owner-refused'
        else:d.update(reserved=put(s.reserved,i,0),free=put(s.free,holder,s.free[holder]+s.reserved[i]));outcome='released'
    elif a.startswith('intent'):
        if s.reserved[i]==6 and not s.intent&bit:d.update(intent=s.intent|bit,revision=s.revision+1)
        else: outcome='denied'
    elif a.startswith(('send','resend')):
        if s.intent&bit and s.reserved[i]==6 and (s.sent[i]==0 or mutant=='ambiguity'):
            d.update(sent=put(s.sent,i,s.sent[i]+1),revision=s.revision+1);outcome='sent'
        else:outcome='blocked'
    elif a.startswith(('accept','refuse')):
        if s.sent[i] and not s.remote[i]:d['remote']=put(s.remote,i,1 if a.startswith('accept') else 2)
        else:outcome='unavailable'
    elif a.startswith('lose'):
        if s.remote[i] and not s.receipt[i]:d['quarantine']=s.quarantine|bit
        else:outcome='unavailable'
    elif a.startswith(('receive','query')):
        if s.remote[i]:d.update(receipt=put(s.receipt,i,s.remote[i]),revision=s.revision+1)
        else:outcome='unknown'
    elif a.startswith('classify'):
        if s.receipt[i]:
            d['classification']=put(s.classification,i,s.receipt[i])
            if mutant=='classification-release':d.update(reserved=put(s.reserved,i,0),free=put(s.free,holder,s.free[holder]+s.reserved[i]))
        else:outcome='unknown'
    elif a.startswith('conflict'):
        if s.classification[i]:d.update(conflict=s.conflict|bit,quarantine=s.quarantine|bit)
        else:outcome='unavailable'
    elif a.startswith(('reconcile','settle_again')):
        if s.classification[i] and (not s.conflict&bit or mutant=='conflict-hold') and (s.reserved[i] or mutant=='settlement-idempotence'):
            amount=s.reserved[i] if mutant!='settlement-idempotence' else 6
            d.update(reserved=put(s.reserved,i,0),revision=s.revision+1)
            if s.classification[i]==1:d['consumed']=put(s.consumed,i,s.consumed[i]+amount)
            else:d['free']=put(s.free,holder,s.free[holder]+amount)
            outcome='settled'
        else:outcome='held' if s.reserved[i] else 'duplicate'
    elif a=='transfer_debit':
        if design=='central':outcome='not-applicable'
        elif s.transfer==0 and s.free[p['source']]>=1:
            d.update(transfer=1,revision=s.revision+1)
            if mutant!='durable-debit':d['free']=put(s.free,p['source'],s.free[p['source']]-1)
        else:outcome='denied'
    elif a in ('transfer_install','transfer_duplicate'):
        if design=='central':outcome='not-applicable'
        elif s.transfer==1 or (s.transfer==2 and mutant=='duplicate-credit'):
            dest=1-p['source'];d.update(free=put(s.free,dest,s.free[dest]+1),transfer=2,revision=s.revision+1)
        else:outcome='duplicate' if s.transfer==2 else 'unavailable'
    elif a=='transfer_timeout':
        outcome='held' if design=='rights' and s.transfer else 'not-applicable'
        if mutant=='timeout-reclaim' and design=='rights' and s.transfer:
            src=p['source'];d['free']=put(s.free,src,s.free[src]+1)
    elif a=='transfer_ack':
        if design=='rights' and s.transfer==2:d['ack']=True
        else:outcome='unavailable'
    elif a=='restart':
        d.update(boot=1,ack=False,replay_cursor=0)
        if mutant=='restart-release':d.update(free=(10,0) if design=='central' else (5,5),reserved=(0,0))
    elif a=='replay':
        d['replay_cursor']=s.revision
        if mutant=='replay-reservation':d.update(free=(10,0) if design=='central' else (5,5),reserved=(0,0))
    elif a=='quota_reset':
        d.update(quota_epoch=1,quota_used=0)
        if mutant=='quota-reservation':d.update(reserved=(0,0),free=(10,0) if design=='central' else (5,5))
        if mutant=='quota-lifetime':d['lifetime']=(0,0)
    elif a=='exit':
        d['worker']=1
        if mutant=='exit-reservation':d.update(reserved=(0,0),free=(10,0) if design=='central' else (5,5))
    elif a=='wait':
        if s.worker==1:d['worker']=2
        else:outcome='unavailable'
    elif a=='new_worker':
        if s.worker==2 and s.incarnation==0:d.update(incarnation=1,worker=0)
        else:outcome='denied'
    elif a=='compute':
        if s.incarnation==1 and s.worker==0 and s.lifetime[1]==0:d.update(lifetime=(s.lifetime[0],1),quota_used=s.quota_used+1)
        else:outcome='denied'
    elif a=='publish':d['generation']=2
    elif a=='capture':d.update(snapshot=(s.revision,s.free,s.reserved,s.consumed,s.transfer,s.generation),reader_pin=True)
    elif a=='copy':
        if s.snapshot:d['copied']=True
        else:outcome='unavailable'
    elif a=='reader_wait':
        if s.copied:d['reader_pin']=False
        else:outcome='unavailable'
    elif a=='install':
        if s.copied:
            d.update(installed=s.snapshot,installed_cursor=s.snapshot[0])
            if mutant=='snapshot-reservation':d.update(reserved=s.snapshot[2],free=s.snapshot[1])
        else:outcome='unavailable'
    elif a=='restore_old':
        outcome='stale-rejected' if s.snapshot and s.snapshot[0]!=s.revision else 'no-change'
        if mutant=='snapshot-rights' and s.snapshot:d.update(free=s.snapshot[1],transfer=s.snapshot[4])
    else:raise ValueError(a)
    return outcome,replace(s,**d,done=finish(s,a,p))

def edges(s,p,design,mutant=None):
    yield 'status=ok',s
    for a in available(s,p):
        outcome,n=step(s,a,p,design,mutant)
        yield a+'='+outcome,n
