"""Independent flat transition relation for the same finite environment.

Only domain declarations are shared with the split; no split/aggregate transition calls.
"""
from typing import NamedTuple
from domain import TOKENS,LIMIT,CHANNEL,FRAME,CREDIT_SOURCES

class Inclusive(NamedTuple):
    control:int=0  # 0 available, 1 pending, 2 fenced
    unknown:bool=True
    stream:int=0
    position:int=0
    allowance:int=0
    outstanding:tuple=()
    channels:tuple=((),(),())
    fragment_length:int=0
    dropped:bool=False
    gap_evidence:bool=False
    credit_issued:int=0
    last_ack:int=0
    saw_credit:bool=False

def successors(s,mutant=None):
    yield ('idle',),s
    size=sum(map(len,s.channels))
    if s.control==0 and (mutant!='shared_control' or size!=LIMIT):yield ('stop_request',),s._replace(control=1)
    if s.control==1:yield ('stop_apply',),s._replace(control=2,unknown=mutant!='false_settlement')
    if s.stream!=2 and not s.fragment_length and len(s.channels[0])<CHANNEL and size<LIMIT+(mutant=='queue_overflow'):
        for message in TOKENS:
            if message=='CREDIT' and s.credit_issued==CREDIT_SOURCES:continue
            a,b,c=s.channels
            yield ('offer',message),s._replace(channels=(a+(message,),b,c),credit_issued=s.credit_issued+int(message=='CREDIT'))
    for stage,label in [(0,'pump_sdk'),(1,'pump_broker')]:
        channels=list(s.channels)
        if channels[stage] and (len(channels[stage+1])<CHANNEL or mutant=='stage_overflow'):
            channels[stage+1]+=channels[stage][:1];channels[stage]=channels[stage][1:]
            yield (label,),s._replace(channels=tuple(channels))
    if s.channels[2]:
        message=s.channels[2][0];after=s._replace(channels=(s.channels[0],s.channels[1],s.channels[2][1:]))
        result='outside-selected-fields'
        if s.stream==2 and not(mutant=='refusal_reset' and message=='RESET'):result='refused'
        elif s.stream==1 and message!='RESET' and not(mutant=='gap_event_only' and message not in ('E1','E2')):
            after=after._replace(stream=2);result='gap-continuation'
        elif message=='RESET':
            if s.stream in (1,3) or (mutant=='refusal_reset' and s.stream==2):
                after=after._replace(stream=0,allowance=s.allowance if mutant=='reset_credit' else 0,outstanding=(),last_ack=s.position,saw_credit=False);result='reset'
            else:after=after._replace(stream=2);result='unexpected-reset'
        elif message=='CREDIT':after=after._replace(allowance=s.allowance+1,saw_credit=True);result='credit'
        elif message in ('E1','E2'):
            position={'E1':1,'E2':2}[message]
            if mutant=='deny_event':result='denied-all-events'
            elif position!=s.position+1:after=after._replace(stream=2);result='cursor-refused'
            elif not s.saw_credit:after=after._replace(stream=2);result='credit-missing'
            elif s.stream==3 or not s.allowance or len(s.outstanding)==2:after=after._replace(stream=3);result='flow-exhausted'
            else:after=after._replace(position=position,allowance=s.allowance-1,outstanding=s.outstanding+(position,));result='event'
        elif message in ('ACK0','ACK1','ACK2'):
            ack={'ACK0':0,'ACK1':1,'ACK2':2}[message]
            if ack<s.last_ack:after=after._replace(stream=2);result='ack-backward'
            elif ack>s.position:after=after._replace(stream=2);result='ack-ahead'
            else:after=after._replace(outstanding=tuple(v for v in s.outstanding if v>ack),last_ack=ack);result='ack'
        elif message=='INPUT' and s.control==2:result='stopped-input'
        yield ('message',message,result),after
        yield ('requeue',),s
    if s.stream==0 and not s.position:yield ('gap',),s._replace(stream=1)
    if s.channels[0] and not s.dropped:
        a,b,c=s.channels;next_state=s._replace(channels=(a[1:],b,c),dropped=True)
        if mutant!='hidden_loss':next_state=next_state._replace(gap_evidence=True,stream=1 if s.stream==0 else s.stream)
        yield ('loss',),next_state
    if s.stream!=2:
        length=s.fragment_length+1
        if length<=FRAME or mutant=='unbounded_frame':yield ('fragment',),s._replace(fragment_length=length)
        else:yield ('framing_unknown','oversize'),s._replace(fragment_length=0,gap_evidence=True,stream=1 if s.stream==0 else s.stream)
        if s.fragment_length:yield ('framing_unknown','eof'),s._replace(fragment_length=0,gap_evidence=True,stream=1 if s.stream==0 else s.stream)
