"""Independent inclusive transition implementation, same declared environment."""
from cm_domain import State

def initial():return State()
def successors(s,policy,mutant=None):
    transitions=[]
    def put(name,**changes):transitions.append((name,s._replace(**changes)))
    hold=s.requested and s.selected!=3 and s.candidate==0 and s.resident.bit_count()==2 and mutant!='hidden_hold'
    put('status_hold' if hold else 'status')
    if mutant=='fork_authority' and s.admission!=1:put('inspect_fork',admission=1)
    else:put('inspect_fork')
    if not s.requested and s.selected==2:put('request_g3',requested=True)
    if s.selected<3 and s.candidate==0 and not s.reply and (s.selected==1 or s.requested):
        if mutant=='capacity' or s.resident.bit_count()<=1:
            n=s.selected+1;put('prepare',candidate=n,resident=s.resident|(2**(n-1)),writer=s.term)
    if s.candidate!=0:
        if mutant=='publish_unstaged' and not s.staged and s.term==s.writer:
            put('publish',selected=s.candidate,candidate=0,writer=0,staged=False,reply=True)
        if not s.staged:
            if mutant=='early_selection':put('stage',staged=True,selected=s.candidate)
            else:put('stage',staged=True)
        elif s.term!=s.writer and mutant!='writer_fence':
            put('stale_writer_refused');put('reauthorize',writer=s.term)
        else:put('publish',selected=s.candidate,candidate=0,writer=0,staged=False,reply=True)
    if s.reply:
        put('publication_ack',reply=False);put('publication_reply_lost',reply=False)
    if s.term<2:put('restart_authority',term=2)
    if not s.capsule and policy=='capsule':put('commit_capsule',capsule=True)
    for generation in range(1,s.selected):
        flag=2**(generation-1)
        if (s.resident&flag)==0:continue
        if s.retiring&flag:
            if s.half&flag or mutant=='skip_first_delete':put('reclaim_'+str(generation),resident=s.resident^flag,retiring=s.retiring^flag,half=s.half&~flag)
            else:put('delete_first_'+str(generation),half=s.half|flag)
        else:
            invocation_blocks=(generation==1 and s.pin and mutant!='live_pin')
            history_blocks=(generation==1 and not s.capsule and mutant!='fork_loss')
            if not invocation_blocks and not history_blocks:
                put('retire_'+str(generation),retiring=s.retiring|flag,fork=s.fork and not(generation==1 and mutant=='fork_loss' and not s.capsule))
    if s.admission!=2:put('stop',admission=2)
    elif s.installed!=2:put('install_fence',installed=2)
    if s.permit==0:
        if s.installed==2 and mutant!='recipient_fence':put('stale_permit_refused',permit=2)
        else:put('execute' if s.admission==1 else 'execute_exposed',permit=1,effect=1,executions=s.executions+1)
    if s.effect==1:put('remote_complete',effect=2)
    if not s.receipt and s.effect==2:
        name='current_receipt' if s.incarnation==1 and s.admission==1 else 'late_receipt'
        if mutant=='receipt_attempt' and s.incarnation==2:put(name,receipt=True,closed=s.closed|2)
        else:put(name,receipt=True)
    for bad_input in ('wrong_operation','wrong_payload','unauthenticated'):
        if mutant==bad_input and s.effect==2 and not s.receipt:put(bad_input+'_refused',receipt=True)
        else:put(bad_input+'_refused')
    if mutant=='receipt_identity' and s.effect!=2:put('invalid_receipt_refused',receipt=True)
    else:put('invalid_receipt_refused')
    if s.actor==0:
        put('kill_local',actor=2)
        if s.permit==2 or s.effect==2:put('return_local',actor=1)
    elif s.actor==2:
        if s.effect==1 and mutant=='death_settlement':put('wait_local',actor=3,receipt=True)
        else:put('wait_local',actor=3)
    if s.actor==1 or s.actor==3:
        if s.pin:put('release_pin',pin=False)
        if s.closed%2==0:put('close_attempt1',closed=s.closed+1)
        if s.incarnation==1:put('new_query_incarnation',incarnation=2,spent=s.spent+1)
    if s.incarnation==2:
        if not s.ack:
            if mutant=='old_ack':put('old_transport_ack',ack=True,closed=s.closed|2)
            else:put('old_transport_ack',ack=True)
        if s.closed<2 and (s.receipt or s.permit==2):put('close_attempt2',closed=s.closed+2)
        if mutant=='blind_retry' and s.executions==1:put('query_same_operation',effect=1,executions=2)
        else:put('query_same_operation')
    if not s.reset:
        if mutant=='reset_budget':put('pool_reset',reset=True,spent=0)
        else:put('pool_reset',reset=True)
    return transitions
