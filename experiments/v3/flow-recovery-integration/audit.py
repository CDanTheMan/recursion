"""Independent sufficient-state audit for a fixed-client/stream/epoch alphabet.

Calibrated against the immutable literal oracle; not a theorem for the full union.
"""
import base64
from typing import NamedTuple
class Audit(NamedTuple):
    cursor:int=0
    acknowledged:int=0
    unit:str=''
    hello:int=-1
    byte_credit:int=0
    event_credit:int=0
    credit_seen:bool=False
    pending:tuple=()
    reasons:frozenset=frozenset()
    recovery:int=0  # 0 current clean, 1 flow exhaustion/missing credit, 2 replay gap
def advance(a,m,queue_bytes,queue_events):
    if m is None:return a
    reasons=set(a.reasons);kind=m['type']
    if m['daemon_epoch']!=2:return a._replace(reasons=a.reasons|{'stale-daemon-epoch'})
    if m['stream_id']!='stream-a' or m.get('client_id','client-a')!='client-a':raise ValueError('outside declared audit identity domain')
    if a.recovery==2 and kind!='RESET':return a._replace(reasons=a.reasons|{'replay-gap-continuation'})
    if kind=='CREDIT':return a._replace(credit_seen=True,byte_credit=a.byte_credit+m['bytes'],event_credit=a.event_credit+m['events'])
    if kind not in ('EVENT','ACK','HELLO','WELCOME','RESET'):raise ValueError('outside declared audit alphabet')
    unit=m['cursor_unit']
    if a.unit and a.unit!=unit:reasons.add('cursor-unit-mismatch')
    a=a._replace(unit=a.unit or unit)
    if kind=='RESET':
        n=m['snapshot_cursor']
        if a.recovery==0:reasons.add('unexpected-reset')
        if n<a.cursor:reasons.add('cursor-nonmonotonic')
        elif a.recovery:a=a._replace(cursor=n,acknowledged=n,byte_credit=0,event_credit=0,credit_seen=False,pending=(),recovery=0)
    elif kind in ('HELLO','WELCOME'):
        n=m['last_cursor'] if kind=='HELLO' else m['snapshot_cursor']
        if n<a.cursor:reasons.add('cursor-nonmonotonic')
        if kind=='HELLO':a=a._replace(hello=n)
        else:
            if m['input_lease'] is not None or m['resize_lease'] is not None:reasons.add('welcome-lease-mismatch')
            if m['replay_floor']>n:reasons.add('cursor-nonmonotonic')
            if a.hello>=0 and a.hello<m['replay_floor']:reasons.add('replay-gap');a=a._replace(recovery=2)
        a=a._replace(cursor=max(a.cursor,n))
    elif kind=='EVENT':
        n=m['cursor'];size=len(base64.b64decode(m['payload_base64'],validate=True));expected=a.cursor+(size if unit=='utf8-byte' else 1)
        if n!=expected:reasons.add('utf8-byte-cursor-mismatch' if unit=='utf8-byte' else 'cursor-nonmonotonic')
        if not a.credit_seen:reasons.add('credit-missing');a=a._replace(recovery=1)
        elif a.byte_credit<size or a.event_credit<1:reasons.add('credit-exhausted');a=a._replace(recovery=1)
        else:a=a._replace(byte_credit=a.byte_credit-size,event_credit=a.event_credit-1)
        pending=(*a.pending,(n,size));a=a._replace(pending=pending,cursor=max(a.cursor,n))
        if sum(size for _,size in pending)>queue_bytes or len(pending)>queue_events:reasons.add('credit-exhausted');a=a._replace(recovery=1)
    else:
        n=m['cursor']
        if n<a.acknowledged:reasons.add('cursor-nonmonotonic')
        elif n>a.cursor:reasons.add('ack-ahead')
        else:a=a._replace(acknowledged=n,pending=tuple(p for p in a.pending if p[0]>n))
    return a._replace(reasons=frozenset(reasons))
def decision(a):
    historical=bool(a.reasons&{'credit-missing','credit-exhausted','replay-gap'})
    permanent=a.reasons-{'credit-exhausted','replay-gap'}
    return dict(type='BrokerTraceDecision@1',status='refused' if permanent or a.recovery else 'accepted-reset' if historical else 'accepted',reasons=sorted(a.reasons),final_cursor=a.cursor,cursor_unit=a.unit or 'event',launch_count=0,model_turn_count=0,actor_create_count=0,effect_count=0,requires_reset=historical)
