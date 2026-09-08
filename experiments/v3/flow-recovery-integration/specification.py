"""Queue-independent specification for candidate ownership and receiver state."""
from domain import *
def step(s,label):
    kind=label[0]
    if kind in ('idle','pump_source','pump_sdk','pump_broker','fragment','requeue'):return s
    if kind=='framing_fault':return s._replace(quarantine=True)
    if kind=='stop_request' and s.control==0:return s._replace(control=1)
    if kind=='stop_apply' and s.control==1:return s._replace(control=2)
    if kind=='offer' and not s.quarantine and s.offered<EVENTS and label[1]==s.offered+1:
        return s._replace(offered=label[1],live=(*s.live,label[1]))
    if kind=='evict' and not s.loss and label[1] in s.live:
        return s._replace(loss=label[1],live=tuple(n for n in s.live if n!=label[1]))
    if kind=='snapshot' and s.loss and not s.snapshot and label[1]==s.loss:return s._replace(snapshot=s.loss)
    ready=s.loss and not s.covered and s.position+1==s.loss and s.snapshot==s.loss
    if kind=='hello' and s.phase==0 and ready:return s._replace(phase=1)
    if kind=='welcome' and s.phase==1 and ready:return s._replace(phase=2)
    if kind=='reset' and s.phase==2 and ready:
        return s._replace(position=s.loss,covered=s.loss,phase=0,byte_credit=0,event_credit=0,pending=(),acknowledged=s.loss)
    if s.phase==2:return None
    if kind=='credit' and s.grants<GRANTS and label[1] in (1,2):
        return s._replace(grants=s.grants+1,byte_credit=s.byte_credit+label[1],event_credit=s.event_credit+1)
    if kind=='ack' and label[1] in s.pending and s.acknowledged<label[1]<=s.position:
        return s._replace(acknowledged=label[1],pending=tuple(n for n in s.pending if n>label[1]))
    if kind=='emit':
        n=label[1]
        if n not in s.live or n!=s.position+1:return None
        if s.byte_credit<COSTS[n-1] or s.event_credit<1:return None
        if len(s.pending)>=QUEUE_EVENTS or sum(COSTS[k-1] for k in s.pending)+COSTS[n-1]>QUEUE_BYTES:return None
        return s._replace(live=tuple(k for k in s.live if k!=n),position=n,delivered=(*s.delivered,n),byte_credit=s.byte_credit-COSTS[n-1],event_credit=s.event_credit-1,pending=(*s.pending,n))
    return None
def invariant(s):
    if any(type(getattr(s,k)) is not int for k in ['offered','loss','snapshot','covered','phase','position','byte_credit','event_credit','grants','acknowledged','control']):return False
    if type(s.external_unknown)is not bool or not s.external_unknown or type(s.quarantine)is not bool:return False
    if not(0<=s.offered<=EVENTS and 0<=s.position<=s.offered and s.phase in (0,1,2) and s.control in (0,1,2) and 0<=s.grants<=GRANTS and 0<=s.byte_credit<=2*GRANTS and 0<=s.event_credit<=GRANTS and 0<=s.acknowledged<=s.position):return False
    if any(type(v)is not tuple or any(type(n)is not int for n in v) or tuple(sorted(set(v)))!=v for v in [s.live,s.delivered,s.pending]):return False
    owned=s.live+s.delivered+((s.loss,) if s.loss else ())
    if sorted(owned)!=list(range(1,s.offered+1)):return False
    if s.snapshot not in (0,s.loss) or s.covered not in (0,s.loss):return False
    if s.covered and (s.snapshot!=s.covered or s.position<s.covered):return False
    if s.phase and not(s.loss and not s.covered and s.snapshot==s.loss and s.position+1==s.loss):return False
    installed=tuple(sorted(s.delivered+((s.covered,) if s.covered else ())))
    if installed!=tuple(range(1,s.position+1)):return False
    return set(s.pending)<=set(s.delivered) and all(s.acknowledged<n<=s.position for n in s.pending) and len(s.pending)<=QUEUE_EVENTS and sum(COSTS[n-1] for n in s.pending)<=QUEUE_BYTES
