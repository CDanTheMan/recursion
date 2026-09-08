"""Concrete authority envelope plus broker state; independently coded commands."""
from dataclasses import dataclass
from wr_domain import State, NAMES, BROKER, available

AUTH = tuple(n for n in NAMES if n not in BROKER)
LOCAL = tuple(n for n in NAMES if n in BROKER)

@dataclass(frozen=True, slots=True)
class Split:
    authority: tuple
    broker: tuple

def pack(s):return Split(tuple(getattr(s,n) for n in AUTH),tuple(getattr(s,n) for n in LOCAL))
def flat(s):return State(**dict(zip(AUTH,s.authority)),**dict(zip(LOCAL,s.broker)))

def edges(s,p,design):
    yield 'status=ok',s
    data=dict(zip(AUTH,s.authority));data.update(zip(LOCAL,s.broker))
    for action in available(flat(s),p):
        v=data.copy();answer='ok'
        goal=int(action[-1]) if action[-1].isdigit() else 0
        flag=2**goal;owner=goal if design=='rights' else 0
        def set_at(name,index,value):
            values=list(v[name]);values[index]=value;v[name]=tuple(values)
        def tick():v['revision']+=1
        if action in ('read0','read1'):
            set_at('reads',goal,v['free'][owner])
        elif action in ('reserve0','reserve1','duplicate0','duplicate1'):
            if v['issued']&flag:answer='duplicate'
            elif v['free'][owner]>=6:
                set_at('free',owner,v['free'][owner]-6);set_at('reserved',goal,6)
                v['issued']|=flag;tick();answer='admitted'
            else:answer='denied'
        elif action.startswith('wrong_owner') or action.startswith('foreign_release'):answer='owner-refused'
        elif action.startswith('changed_payload'):answer='payload-conflict'
        elif action.startswith('intent'):
            if v['reserved'][goal]!=6 or v['intent']&flag:answer='denied'
            else:v['intent']|=flag;tick()
        elif action.startswith('send') or action.startswith('resend'):
            if v['intent']&flag and v['reserved'][goal]==6 and v['sent'][goal]==0:
                set_at('sent',goal,1);tick();answer='sent'
            else:answer='blocked'
        elif action.startswith('accept') or action.startswith('refuse'):
            if v['remote'][goal]!=0 or v['sent'][goal]==0:answer='unavailable'
            else:set_at('remote',goal,2 if action.startswith('refuse') else 1)
        elif action.startswith('lose'):
            if v['remote'][goal]!=0 and v['receipt'][goal]==0:v['quarantine']|=flag
            else:answer='unavailable'
        elif action.startswith('query') or action.startswith('receive'):
            if v['remote'][goal]==0:answer='unknown'
            else:set_at('receipt',goal,v['remote'][goal]);tick()
        elif action.startswith('classify'):
            if v['receipt'][goal]==0:answer='unknown'
            else:set_at('classification',goal,v['receipt'][goal])
        elif action.startswith('conflict'):
            if v['classification'][goal]==0:answer='unavailable'
            else:v['conflict']|=flag;v['quarantine']|=flag
        elif action.startswith('reconcile') or action.startswith('settle_again'):
            amount=v['reserved'][goal]
            if amount==0:answer='duplicate'
            elif v['classification'][goal]==0 or v['conflict']&flag:answer='held'
            else:
                if v['classification'][goal]==2:set_at('free',owner,v['free'][owner]+amount)
                else:set_at('consumed',goal,v['consumed'][goal]+amount)
                set_at('reserved',goal,0);tick();answer='settled'
        elif action=='transfer_debit':
            source=p['source']
            if design=='central':answer='not-applicable'
            elif v['transfer'] or v['free'][source]<1:answer='denied'
            else:set_at('free',source,v['free'][source]-1);v['transfer']=1;tick()
        elif action in ('transfer_install','transfer_duplicate'):
            if design=='central':answer='not-applicable'
            elif v['transfer']==2:answer='duplicate'
            elif v['transfer']==0:answer='unavailable'
            else:
                destination=1-p['source'];set_at('free',destination,v['free'][destination]+1)
                v['transfer']=2;tick()
        elif action=='transfer_timeout':answer='held' if design=='rights' and v['transfer']!=0 else 'not-applicable'
        elif action=='transfer_ack':
            if design=='rights' and v['transfer']==2:v['ack']=True
            else:answer='unavailable'
        elif action=='restart':v['boot']=1;v['ack']=False
        elif action=='quota_reset':v['quota_epoch']=1;v['quota_used']=0
        elif action=='exit':v['worker']=1
        elif action=='wait':
            if v['worker']!=1:answer='unavailable'
            else:v['worker']=2
        elif action=='new_worker':
            if v['worker']==2 and v['incarnation']==0:v['worker']=0;v['incarnation']=1
            else:answer='denied'
        elif action=='compute':
            if v['worker']==0 and v['incarnation']==1 and v['lifetime'][1]==0:
                set_at('lifetime',1,1);v['quota_used']+=1
            else:answer='denied'
        elif action=='publish':v['generation']=2
        elif action=='capture':
            v['snapshot']=(v['revision'],v['free'],v['reserved'],v['consumed'],v['transfer'],v['generation']);v['reader_pin']=True
        elif action=='copy':
            if v['snapshot']:v['copied']=True
            else:answer='unavailable'
        elif action=='reader_wait':
            if v['copied']:v['reader_pin']=False
            else:answer='unavailable'
        elif action=='install':
            if v['copied']:v['installed']=v['snapshot']
            else:answer='unavailable'
        elif action=='restore_old':answer='stale-rejected' if v['snapshot'] and v['snapshot'][0]!=v['revision'] else 'no-change'
        else:raise ValueError(action)
        v['done']|=2**p['actions'].index(action)
        authority=tuple(v[n] for n in AUTH);broker=tuple(v[n] for n in LOCAL)
        yield action+'='+answer,Split(authority,broker)
