"""Independent visible relation. It hides staging and first-deletion details only."""
from typing import NamedTuple
from cm_domain import State
FIELDS=tuple(n for n in State._fields if n not in ('staged','half'))
Abstract=NamedTuple('Abstract',[(n,State.__annotations__[n]) for n in FIELDS])
def project(s):return Abstract(*(getattr(s,n) for n in FIELDS))
def initial():return project(State())
def step(v,event,policy):
    changes=None
    if event in ('status','status_hold'):
        held=v.requested and v.selected<3 and v.candidate==0 and v.resident.bit_count()==2
        if (event=='status_hold')==held:changes={}
    elif event in ('inspect_fork','invalid_receipt_refused','query_same_operation','stale_writer_refused','wrong_operation_refused','wrong_payload_refused','unauthenticated_refused'):changes={}
    elif event=='request_g3' and v.selected==2 and not v.requested:changes={'requested':True}
    elif event=='prepare' and not v.candidate and not v.reply and v.selected<3 and v.resident.bit_count()<2 and (v.selected==1 or v.requested):
        g=v.selected+1;changes={'candidate':g,'resident':v.resident|(1<<(g-1)),'writer':v.term}
    elif event=='stage' and v.candidate:changes={}
    elif event=='publish' and v.candidate and v.writer==v.term:
        changes={'selected':v.candidate,'candidate':0,'writer':0,'reply':True}
    elif event=='reauthorize' and v.candidate and v.writer!=v.term:changes={'writer':v.term}
    elif event in ('publication_ack','publication_reply_lost') and v.reply:changes={'reply':False}
    elif event=='restart_authority' and v.term==1:changes={'term':2}
    elif event=='commit_capsule' and policy=='capsule' and not v.capsule:changes={'capsule':True}
    elif event.startswith(('retire_','delete_first_','reclaim_')):
        g=int(event[-1]);mask=1<<(g-1)
        if g<v.selected and v.resident&mask:
            if event.startswith('retire_') and not v.retiring&mask and (g!=1 or (not v.pin and v.capsule)):changes={'retiring':v.retiring|mask}
            if event.startswith('delete_first_') and v.retiring&mask:changes={}
            if event.startswith('reclaim_') and v.retiring&mask:changes={'resident':v.resident&~mask,'retiring':v.retiring&~mask}
    elif event=='stop' and v.admission==1:changes={'admission':2}
    elif event=='install_fence' and v.admission==2 and v.installed==1:changes={'installed':2}
    elif event in ('execute','execute_exposed') and v.permit==0 and v.installed==1:
        if (event=='execute')==(v.admission==1):changes={'permit':1,'effect':1,'executions':v.executions+1}
    elif event=='stale_permit_refused' and v.permit==0 and v.installed==2:changes={'permit':2,'reserved':False}
    elif event=='remote_complete' and v.effect==1:changes={'effect':2}
    elif event in ('current_receipt','late_receipt') and v.effect==2 and not v.receipt:
        if (event=='current_receipt')==(v.incarnation==1 and v.admission==1):changes={'receipt':True,'reserved':False}
    elif event=='kill_local' and v.actor==0:changes={'actor':2}
    elif event=='return_local' and v.actor==0 and (v.effect==2 or v.permit==2):changes={'actor':1}
    elif event=='wait_local' and v.actor==2:changes={'actor':3}
    elif event=='release_pin' and v.pin and v.actor in (1,3):changes={'pin':False}
    elif event=='close_attempt1' and not v.closed&1 and v.actor in (1,3):changes={'closed':v.closed|1}
    elif event=='new_query_incarnation' and v.incarnation==1 and v.actor in (1,3):changes={'incarnation':2,'spent':v.spent+1}
    elif event=='old_transport_ack' and v.incarnation==2 and not v.ack:changes={'ack':True}
    elif event=='close_attempt2' and v.incarnation==2 and not v.closed&2 and (v.receipt or v.permit==2):changes={'closed':v.closed|2}
    elif event=='pool_reset' and not v.reset:changes={'reset':True}
    return None if changes is None else v._replace(**changes)
