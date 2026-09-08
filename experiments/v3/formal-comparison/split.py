"""Asynchronous kernel + broker composition. Does not call aggregate or inclusive rules."""
from typing import NamedTuple
from domain import TOKENS,LIMIT,CHANNEL,FRAME,CREDIT_SOURCES

class Kernel(NamedTuple):
    waiting:bool=False
    fenced:bool=False
    effect_unknown:bool=True
class Broker(NamedTuple):
    sdk:tuple=()
    pump:tuple=()
    inbox:tuple=()
    phase:int=0
    cursor:int=0
    credit:int=0
    pending:tuple=()
    partial:int=0
    loss_used:bool=False
    ingress_unknown:bool=False
    credit_offers:int=0
    acknowledged:int=0
    credit_seen:bool=False
class Split(NamedTuple):
    kernel:Kernel=Kernel()
    broker:Broker=Broker()

def take(k,b,token,mutant):
    if b.phase==2 and mutant!='refusal_reset':return 'refused',b
    if b.phase==2 and token!='RESET':return 'refused',b
    if b.phase==1 and token!='RESET' and not(mutant=='gap_event_only' and not token.startswith('E')):
        return 'gap-continuation',b._replace(phase=2)
    if token=='RESET':
        if b.phase not in ((1,2,3) if mutant=='refusal_reset' else (1,3)):
            return 'unexpected-reset',b._replace(phase=2)
        return 'reset',b._replace(phase=0,credit=b.credit if mutant=='reset_credit' else 0,pending=(),acknowledged=b.cursor,credit_seen=False)
    if token=='CREDIT':return 'credit',b._replace(credit=b.credit+1,credit_seen=True)
    if token in ('E1','E2'):
        if mutant=='deny_event':return 'denied-all-events',b
        cursor=int(token[-1])
        if cursor!=b.cursor+1:return 'cursor-refused',b._replace(phase=2)
        if not b.credit_seen:return 'credit-missing',b._replace(phase=2)
        if b.phase==3 or b.credit==0 or len(b.pending)>=2:return 'flow-exhausted',b._replace(phase=3)
        return 'event',b._replace(cursor=cursor,credit=b.credit-1,pending=b.pending+(cursor,))
    if token[:3]=='ACK':
        ack=int(token[-1])
        if ack<b.acknowledged:return 'ack-backward',b._replace(phase=2)
        if ack>b.cursor:return 'ack-ahead',b._replace(phase=2)
        return 'ack',b._replace(pending=tuple(x for x in b.pending if x>ack),acknowledged=ack)
    if token=='INPUT' and k.fenced:return 'stopped-input',b
    return 'outside-selected-fields',b

def successors(s,mutant=None):
    k,b=s;total=len(b.sdk)+len(b.pump)+len(b.inbox)
    yield ('idle',),s
    if not k.waiting and not k.fenced and not(mutant=='shared_control' and total==LIMIT):
        yield ('stop_request',),Split(k._replace(waiting=True),b)
    if k.waiting:
        yield ('stop_apply',),Split(k._replace(waiting=False,fenced=True,effect_unknown=mutant!='false_settlement'),b)
    if total<(LIMIT+1 if mutant=='queue_overflow' else LIMIT) and len(b.sdk)<CHANNEL and b.partial==0 and b.phase!=2:
        for token in TOKENS:
            if token=='CREDIT' and b.credit_offers>=CREDIT_SOURCES:continue
            yield ('offer',token),Split(k,b._replace(sdk=b.sdk+(token,),credit_offers=b.credit_offers+(token=='CREDIT')))
    if b.sdk and (len(b.pump)<CHANNEL or mutant=='stage_overflow'):
        yield ('pump_sdk',),Split(k,b._replace(sdk=b.sdk[1:],pump=b.pump+(b.sdk[0],)))
    if b.pump and (len(b.inbox)<CHANNEL or mutant=='stage_overflow'):
        yield ('pump_broker',),Split(k,b._replace(pump=b.pump[1:],inbox=b.inbox+(b.pump[0],)))
    if b.inbox:
        token=b.inbox[0];result,after=take(k,b._replace(inbox=b.inbox[1:]),token,mutant)
        yield ('message',token,result),Split(k,after)
        yield ('requeue',),s
    if b.phase==0 and b.cursor==0:yield ('gap',),Split(k,b._replace(phase=1))
    if b.sdk and not b.loss_used:
        change={'sdk':b.sdk[1:],'loss_used':True}
        if mutant!='hidden_loss':change.update(ingress_unknown=True,phase=b.phase if mutant=='loss_retains_flow' and b.phase==3 else 1 if b.phase!=2 else b.phase)
        yield ('loss',),Split(k,b._replace(**change))
    if b.phase!=2:
        if b.partial<FRAME or mutant=='unbounded_frame':
            yield ('fragment',),Split(k,b._replace(partial=b.partial+1))
        else:
            yield ('framing_unknown','oversize'),Split(k,b._replace(partial=0,ingress_unknown=True,phase=1 if b.phase!=2 else b.phase))
        if b.partial:
            yield ('framing_unknown','eof'),Split(k,b._replace(partial=0,ingress_unknown=True,phase=1 if b.phase!=2 else b.phase))
