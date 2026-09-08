"""Shared declarations/encoding only; no transition reducer shared by models."""
import base64
from typing import NamedTuple
COSTS=(1,2,1,2)
EVENTS=4
GRANTS=4
QUEUE_EVENTS=2
QUEUE_BYTES=2
CHANNEL=1
INFLIGHT=2
RETAINED=2
FRAME=2
MAX_STATES=500000
TIMEOUT_SECONDS=600
MEMORY_BYTES=4*1024**3
def cursor(identity,unit):return sum(COSTS[:identity]) if unit=='utf8-byte' else identity
def message(kind,**fields):return dict(type=kind,protocol_version='m1b-broker/1',stream_id='stream-a',daemon_epoch=2,**fields)
def wire(label,before,unit):
    kind=label[0]
    if kind=='credit':return message('CREDIT',client_id='client-a',bytes=label[1],events=1)
    if kind=='emit':
        n=label[1];return message('EVENT',cursor=cursor(n,unit),cursor_unit=unit,event_class='output',process_id='process-a',payload_base64=base64.b64encode(b'x'*COSTS[n-1]).decode(),payload_untrusted=True)
    if kind=='ack':return message('ACK',client_id='client-a',cursor=cursor(label[1],unit),cursor_unit=unit)
    if kind=='hello':return message('HELLO',client_id='client-a',last_cursor=cursor(before.position,unit),cursor_unit=unit,columns=80,rows=24,capabilities=['attach'])
    if kind=='welcome':return message('WELCOME',client_id='client-a',replay_floor=cursor(before.loss,unit),snapshot_cursor=cursor(before.snapshot,unit),cursor_unit=unit,input_lease=None,resize_lease=None,capabilities=['attach'])
    if kind=='reset':return message('RESET',client_id='client-a',reason='gap',snapshot_cursor=cursor(before.snapshot,unit),cursor_unit=unit)
    return None
class Visible(NamedTuple):
    offered:int=0
    live:tuple=()
    delivered:tuple=()
    loss:int=0
    snapshot:int=0
    covered:int=0
    phase:int=0
    position:int=0
    byte_credit:int=0
    event_credit:int=0
    grants:int=0
    pending:tuple=()
    acknowledged:int=0
    control:int=0
    external_unknown:bool=True
    quarantine:bool=False
