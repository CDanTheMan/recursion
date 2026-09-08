"""Independent abstract authority/stream specification for the named small slice.

This transducer has no concrete queues, partial frames or dispatch algorithm.
Wire fields outside the selected flow/gap projection remain unmodeled.
"""
from typing import NamedTuple
from domain import TOKENS

class Abstract(NamedTuple):
    stop_pending:bool=False
    stopped:bool=False
    external_unknown:bool=True
    phase:int=0  # 0 usable, 1 replay gap, 2 permanently refused, 3 flow recovery
    cursor:int=0
    credit:int=0
    pending:tuple=()
    ingress_unknown:bool=False
    acknowledged:int=0
    credit_seen:bool=False

def wire(s,token):
    if s.phase==2:return 'refused',s
    if s.phase==1 and token!='RESET':return 'gap-continuation',s._replace(phase=2)
    if token=='RESET':
        if s.phase not in (1,3):return 'unexpected-reset',s._replace(phase=2)
        return 'reset',s._replace(phase=0,credit=0,pending=(),acknowledged=s.cursor,credit_seen=False)
    if token=='CREDIT':
        if s.credit==2:return None  # outside abstract finite credit domain
        return 'credit',s._replace(credit=s.credit+1,credit_seen=True)
    if token.startswith('E'):
        cursor=int(token[1:])
        if cursor!=s.cursor+1:return 'cursor-refused',s._replace(phase=2)
        if not s.credit_seen:return 'credit-missing',s._replace(phase=2)
        if s.phase==3 or not s.credit or len(s.pending)==2:return 'flow-exhausted',s._replace(phase=3)
        return 'event',s._replace(cursor=cursor,credit=s.credit-1,pending=(*s.pending,cursor))
    if token.startswith('ACK'):
        cursor=int(token[3:])
        if cursor<s.acknowledged:return 'ack-backward',s._replace(phase=2)
        if cursor>s.cursor:return 'ack-ahead',s._replace(phase=2)
        return 'ack',s._replace(pending=tuple(x for x in s.pending if x>cursor),acknowledged=cursor)
    if token=='INPUT' and s.stopped:return 'stopped-input',s
    return 'outside-selected-fields',s

def step(s,label):
    kind=label[0]
    if kind=='message':
        result=wire(s,label[1])
        return result[1] if result and result[0]==label[2] else None
    if kind=='stop_request':
        return s._replace(stop_pending=True) if not s.stop_pending and not s.stopped else None
    if kind=='stop_apply':
        return s._replace(stop_pending=False,stopped=True) if s.stop_pending else None
    if kind=='gap':return s._replace(phase=1) if s.phase==0 and s.cursor==0 else None
    if kind in ('loss','framing_unknown'):
        return s._replace(phase=1 if s.phase==0 else s.phase,ingress_unknown=True)
    if kind in ('offer','pump_sdk','pump_broker','fragment','idle','requeue'):
        return s
    raise ValueError('Unknown abstract label '+repr(label))

def successors(s):
    yield ('idle',),s
    for token in TOKENS:
        result=wire(s,token)
        if result is not None:yield ('message',token,result[0]),result[1]
    for label in [('stop_request',),('stop_apply',),('gap',),('loss',),('framing_unknown',)]:
        target=step(s,label)
        if target is not None:yield label,target

def invariant(s):
    return (s.external_unknown and not(s.stop_pending and s.stopped) and s.phase in (0,1,2,3)
            and 0<=s.cursor<=2 and 0<=s.credit<=2 and len(s.pending)<=2
            and 0<=s.acknowledged<=s.cursor
            and all(0<x<=s.cursor for x in s.pending) and tuple(sorted(set(s.pending)))==s.pending)
