"""Flat transition definition, without invoking split or specification rules."""
from typing import NamedTuple
from domain import *
class State(NamedTuple):
    issued:int=0
    holding:tuple=()
    buffers:tuple=((),(),())
    delivered:tuple=()
    retired:int=0
    image:int=0
    disposed:int=0
    negotiation:int=0
    applied:int=0
    bytes_left:int=0
    events_left:int=0
    grant_count:int=0
    outstanding:tuple=()
    acked:int=0
    stop:int=0
    unknown:bool=True
    partial:int=0
    quarantined:bool=False
def visible(s):return Visible(s.issued,tuple(sorted(s.holding+sum(s.buffers,()))),s.delivered,s.retired,s.image,s.disposed,s.negotiation,s.applied,s.bytes_left,s.events_left,s.grant_count,s.outstanding,s.acked,s.stop,s.unknown,s.quarantined)
def physical(s):return s.holding,s.buffers,s.partial
def successors(s,mutant=None):
    yield ('idle',),s
    count=sum(len(q) for q in s.buffers)
    if s.stop==0 and (mutant!='shared_stop' or count!=INFLIGHT):yield ('stop_request',),s._replace(stop=1)
    if s.stop==1:yield ('stop_apply',),s._replace(stop=2,unknown=mutant!='false_settlement')
    if not s.quarantined and not s.partial and s.issued<EVENTS and len(s.holding)!=RETAINED:
        n=s.issued+1;yield ('offer',n),s._replace(issued=n,holding=(*s.holding,n))
    if s.holding and count<INFLIGHT and len(s.buffers[0])<CHANNEL:
        head,*tail=s.holding;first,second,third=s.buffers
        yield ('pump_source',),s._replace(holding=tuple(tail),buffers=(first+(head,),second,third))
    for position,label in enumerate(['pump_sdk','pump_broker']):
        rows=list(s.buffers)
        if rows[position] and (len(rows[position+1])<CHANNEL or mutant=='stage_overflow'):
            token,*tail=rows[position];rows[position]=tuple(tail);rows[position+1]=(*rows[position+1],token)
            yield (label,),s._replace(buffers=tuple(rows))
    if not s.retired:
        for token in sorted([*s.holding,*s.buffers[0],*s.buffers[1],*s.buffers[2]]):
            yield ('evict',token),s._replace(retired=token,holding=tuple(x for x in s.holding if x!=token),buffers=tuple(tuple(x for x in q if x!=token) for q in s.buffers))
    if s.retired!=0 and s.image==0:yield ('snapshot',s.retired),s._replace(image=s.retired)
    ready=(s.retired!=0 and s.disposed==0 and s.image==s.retired and s.applied==s.retired-1)
    if s.negotiation==0 and (ready or (mutant=='false_gap' and s.retired!=0 and s.disposed==0 and s.applied==s.retired-1)):
        yield ('hello',),s._replace(negotiation=1)
    if s.negotiation==1 and ready:yield ('welcome',),s._replace(negotiation=2)
    if s.negotiation==2 and ready:
        yield ('reset',),s._replace(holding=() if mutant=='reset_erases_future' else s.holding,buffers=((),(),()) if mutant=='reset_erases_future' else s.buffers,disposed=s.retired,applied=s.retired,negotiation=0,bytes_left=s.bytes_left if mutant=='reset_credit' else 0,events_left=s.events_left if mutant=='reset_credit' else 0,outstanding=(),acked=s.retired)
    if s.negotiation!=2 or mutant=='gap_credit':
        if s.grant_count!=GRANTS:
            for amount in (1,2):yield ('credit',amount),s._replace(grant_count=s.grant_count+1,bytes_left=s.bytes_left+amount,events_left=s.events_left+1)
    if s.negotiation!=2:
        for value in s.outstanding:
            if value>s.acked:yield ('ack',value),s._replace(acked=value,outstanding=tuple(n for n in s.outstanding if n>value))
        tail=s.buffers[2]
        if tail:
            value=tail[0];cost=COSTS[value-1]
            enough=s.events_left>0 and (s.bytes_left-cost>=0 or mutant=='ignore_byte_credit')
            space=len(s.outstanding)+1<=QUEUE_EVENTS and (sum(COSTS[n-1] for n in s.outstanding)+cost<=QUEUE_BYTES or mutant=='ignore_queue_bytes')
            if value==s.applied+1 and enough and space:
                rows=(*s.buffers[:2],tail[1:]);yield ('emit',value),s._replace(buffers=rows,applied=value,delivered=(*s.delivered,value),bytes_left=s.bytes_left-cost,events_left=s.events_left-1,outstanding=(*s.outstanding,value))
            yield ('requeue',),s
    if not s.quarantined:
        if s.partial!=FRAME:yield ('fragment',),s._replace(partial=s.partial+1)
        if s.partial>0:yield ('framing_fault',),s._replace(partial=0,quarantined=True)
