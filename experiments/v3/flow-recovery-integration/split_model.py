"""Kernel, source and broker composition; independent of inclusive/spec reducers."""
from typing import NamedTuple
from domain import *
class Kernel(NamedTuple):
    control:int=0
    external_unknown:bool=True
class Source(NamedTuple):
    offered:int=0
    retained:tuple=()
    loss:int=0
    snapshot:int=0
class Broker(NamedTuple):
    channels:tuple=((),(),())
    delivered:tuple=()
    covered:int=0
    phase:int=0
    position:int=0
    byte_credit:int=0
    event_credit:int=0
    grants:int=0
    pending:tuple=()
    acknowledged:int=0
    fragment:int=0
    quarantine:bool=False
class State(NamedTuple):
    kernel:Kernel=Kernel()
    source:Source=Source()
    broker:Broker=Broker()
def visible(s):
    k,p,b=s
    return Visible(p.offered,tuple(sorted(p.retained+sum(b.channels,()))),b.delivered,p.loss,p.snapshot,b.covered,b.phase,b.position,b.byte_credit,b.event_credit,b.grants,b.pending,b.acknowledged,k.control,k.external_unknown,b.quarantine)
def physical(s):return (s.source.retained,s.broker.channels,s.broker.fragment)
def successors(s,mutant=None):
    k,p,b=s;size=sum(map(len,b.channels));yield ('idle',),s
    if k.control==0 and not(mutant=='shared_stop' and size==INFLIGHT):yield ('stop_request',),s._replace(kernel=k._replace(control=1))
    if k.control==1:yield ('stop_apply',),s._replace(kernel=k._replace(control=2,external_unknown=mutant!='false_settlement'))
    if not b.quarantine and b.fragment==0 and p.offered<EVENTS and len(p.retained)<RETAINED:
        n=p.offered+1;yield ('offer',n),s._replace(source=p._replace(offered=n,retained=p.retained+(n,)))
    if p.retained and len(b.channels[0])<CHANNEL and size<INFLIGHT:
        a,c,d=b.channels;yield ('pump_source',),s._replace(source=p._replace(retained=p.retained[1:]),broker=b._replace(channels=(a+p.retained[:1],c,d)))
    for j,name in [(0,'pump_sdk'),(1,'pump_broker')]:
        q=list(b.channels)
        if q[j] and (len(q[j+1])<CHANNEL or mutant=='stage_overflow'):
            q[j+1]+=q[j][:1];q[j]=q[j][1:];yield (name,),s._replace(broker=b._replace(channels=tuple(q)))
    if not p.loss:
        for n in sorted(p.retained+sum(b.channels,())):
            yield ('evict',n),s._replace(source=p._replace(loss=n,retained=tuple(x for x in p.retained if x!=n)),broker=b._replace(channels=tuple(tuple(x for x in q if x!=n) for q in b.channels)))
    if p.loss and not p.snapshot:yield ('snapshot',p.loss),s._replace(source=p._replace(snapshot=p.loss))
    proof=p.loss and not b.covered and p.snapshot==p.loss and b.position+1==p.loss
    if b.phase==0 and (proof or (mutant=='false_gap' and p.loss and not b.covered and b.position+1==p.loss)):
        yield ('hello',),s._replace(broker=b._replace(phase=1))
    if b.phase==1 and proof:yield ('welcome',),s._replace(broker=b._replace(phase=2))
    if b.phase==2 and proof:
        yield ('reset',),s._replace(source=p._replace(retained=() if mutant=='reset_erases_future' else p.retained),broker=b._replace(channels=((),(),()) if mutant=='reset_erases_future' else b.channels,covered=p.loss,position=p.loss,phase=0,byte_credit=b.byte_credit if mutant=='reset_credit' else 0,event_credit=b.event_credit if mutant=='reset_credit' else 0,pending=(),acknowledged=p.loss))
    if b.phase!=2 or mutant=='gap_credit':
        if b.grants<GRANTS:
            for amount in [1,2]:yield ('credit',amount),s._replace(broker=b._replace(grants=b.grants+1,byte_credit=b.byte_credit+amount,event_credit=b.event_credit+1))
    if b.phase!=2:
        for n in b.pending:
            if n>b.acknowledged:yield ('ack',n),s._replace(broker=b._replace(acknowledged=n,pending=tuple(x for x in b.pending if x>n)))
        if b.channels[2]:
            n=b.channels[2][0];cost=COSTS[n-1]
            funded=(b.byte_credit>=cost or mutant=='ignore_byte_credit') and b.event_credit>=1
            room=len(b.pending)<QUEUE_EVENTS and (sum(COSTS[x-1] for x in b.pending)+cost<=QUEUE_BYTES or mutant=='ignore_queue_bytes')
            if n==b.position+1 and funded and room:
                a,c,d=b.channels;yield ('emit',n),s._replace(broker=b._replace(channels=(a,c,d[1:]),position=n,delivered=b.delivered+(n,),byte_credit=b.byte_credit-cost,event_credit=b.event_credit-1,pending=b.pending+(n,)))
            yield ('requeue',),s
    if not b.quarantine:
        if b.fragment<FRAME:yield ('fragment',),s._replace(broker=b._replace(fragment=b.fragment+1))
        if b.fragment:yield ('framing_fault',),s._replace(broker=b._replace(fragment=0,quarantine=True))
