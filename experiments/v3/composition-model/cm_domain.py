"""Shared declarations only; no shared transition reducer."""
from typing import NamedTuple

class State(NamedTuple):
    selected:int=1
    resident:int=1
    retiring:int=0
    half:int=0
    candidate:int=0
    staged:bool=False
    writer:int=0
    term:int=1
    reply:bool=False
    requested:bool=False
    pin:bool=True
    actor:int=0  # live, returned, killed, waited
    capsule:bool=False
    admission:int=1
    installed:int=1
    permit:int=0  # in flight, executed, refused
    effect:int=0  # absent, unknown/in-progress, completed at recipient
    receipt:bool=False
    incarnation:int=1
    closed:int=0  # per-incarnation completion bits
    ack:bool=False
    reset:bool=False
    executions:int=0
    spent:int=1  # lifetime admitted compute units, independent of pool reset
    fork:bool=True
    reserved:bool=True

class Authority(NamedTuple):
    selected:int=1
    resident:int=1
    retiring:int=0
    candidate:int=0
    writer:int=0
    term:int=1
    reply:bool=False
    requested:bool=False
    pin:bool=True
    capsule:bool=False
    admission:int=1
    incarnation:int=1
    closed:int=0
    spent:int=1
    fork:bool=True
    reserved:bool=True

class Broker(NamedTuple):
    half:int=0
    staged:bool=False
    actor:int=0
    installed:int=1
    permit:int=0
    effect:int=0
    receipt:bool=False
    ack:bool=False
    reset:bool=False
    executions:int=0

class Split(NamedTuple):
    authority:Authority=Authority()
    broker:Broker=Broker()

POLICIES=('capsule','resident')
MUTANTS=('capacity','live_pin','fork_loss','writer_fence','early_selection','recipient_fence','receipt_identity','old_ack','receipt_attempt','reset_budget','death_settlement','blind_retry','fork_authority','publish_unstaged','skip_first_delete','wrong_operation','wrong_payload','unauthenticated','hidden_hold')
BOOLS={'staged','reply','requested','pin','capsule','receipt','ack','reset','fork','reserved'}
def bit(g):return 1<<(g-1)
def normalize(s):
    if isinstance(s,State):return s
    a,b=s
    return State(**{n:getattr(a,n) if n in Authority._fields else getattr(b,n) for n in State._fields})
