"""Split authority/broker implementation; no inclusive or abstract reducer calls."""
from cm_domain import Authority,Broker,Split,bit

def initial():return Split()
def successors(s,policy,mutant=None):
    a,b=s
    def edge(label,ka=None,ba=None):return (label,Split(a._replace(**(ka or {})),b._replace(**(ba or {}))))
    yield edge('status_hold' if a.requested and a.selected<3 and a.resident.bit_count()==2 else 'status')
    yield edge('inspect_fork',{'admission':1} if mutant=='fork_authority' and a.admission==2 else {})
    if a.selected==2 and not a.requested:yield edge('request_g3',{'requested':True})
    target=a.selected+1
    if target<=3 and not a.candidate and not a.reply and (target==2 or a.requested):
        if a.resident.bit_count()<2 or mutant=='capacity':
            yield edge('prepare',{'candidate':target,'resident':a.resident|bit(target),'writer':a.term})
    if a.candidate and not b.staged:yield edge('stage',{'selected':a.candidate} if mutant=='early_selection' else {},{'staged':True})
    if a.candidate and (b.staged or mutant=='publish_unstaged'):
        if a.writer==a.term or mutant=='writer_fence':
            yield edge('publish',{'selected':a.candidate,'candidate':0,'writer':0,'reply':True},{'staged':False})
        else:
            yield edge('stale_writer_refused')
            yield edge('reauthorize',{'writer':a.term})
    if a.reply:
        yield edge('publication_ack',{'reply':False})
        yield edge('publication_reply_lost',{'reply':False})
    if a.term==1:yield edge('restart_authority',{'term':2})
    if policy=='capsule' and not a.capsule:yield edge('commit_capsule',{'capsule':True})
    for g in (1,2):
        mask=bit(g)
        if g<a.selected and a.resident&mask:
            pin_ok=not(g==1 and a.pin) or mutant=='live_pin'
            fork_ok=g!=1 or a.capsule or mutant=='fork_loss'
            if not a.retiring&mask and pin_ok and fork_ok:yield edge('retire_'+str(g),{'retiring':a.retiring|mask,'fork':False if g==1 and mutant=='fork_loss' and not a.capsule else a.fork})
            if a.retiring&mask:
                if not b.half&mask and mutant!='skip_first_delete':yield edge('delete_first_'+str(g),ba={'half':b.half|mask})
                else:yield edge('reclaim_'+str(g),{'resident':a.resident&~mask,'retiring':a.retiring&~mask},{'half':b.half&~mask})
    if a.admission==1:yield edge('stop',{'admission':2})
    if a.admission==2 and b.installed==1:yield edge('install_fence',ba={'installed':2})
    if b.permit==0:
        if b.installed==1 or mutant=='recipient_fence':yield edge('execute_exposed' if a.admission==2 else 'execute',ba={'permit':1,'effect':1,'executions':b.executions+1})
        else:yield edge('stale_permit_refused',ba={'permit':2})
    if b.effect==1:yield edge('remote_complete',ba={'effect':2})
    if b.effect==2 and not b.receipt:yield edge('late_receipt' if a.incarnation==2 or a.admission==2 else 'current_receipt',{'closed':a.closed|2} if mutant=='receipt_attempt' and a.incarnation==2 else {},{'receipt':True})
    for invalid in ('wrong_operation','wrong_payload','unauthenticated'):
        yield edge(invalid+'_refused',ba={'receipt':True} if mutant==invalid and b.effect==2 and not b.receipt else {})
    yield edge('invalid_receipt_refused',ba={'receipt':True} if mutant=='receipt_identity' and b.effect!=2 else {})
    if b.actor==0:
        yield edge('kill_local',ba={'actor':2})
        if b.effect==2 or b.permit==2:yield edge('return_local',ba={'actor':1})
    if b.actor==2:yield edge('wait_local',ba={'actor':3,'receipt':True} if mutant=='death_settlement' and b.effect==1 else {'actor':3})
    if a.pin and b.actor in (1,3):yield edge('release_pin',{'pin':False})
    if not a.closed&1 and b.actor in (1,3):yield edge('close_attempt1',{'closed':a.closed|1})
    if a.incarnation==1 and b.actor in (1,3):yield edge('new_query_incarnation',{'incarnation':2,'spent':a.spent+1})
    if a.incarnation==2:
        if not b.ack:yield edge('old_transport_ack',{'closed':a.closed|2} if mutant=='old_ack' else {},{'ack':True})
        if not a.closed&2 and (b.receipt or b.permit==2):yield edge('close_attempt2',{'closed':a.closed|2})
        yield edge('query_same_operation',ba={'effect':1,'executions':b.executions+1} if mutant=='blind_retry' and b.executions==1 else {})
    if not b.reset:yield edge('pool_reset',{'spent':0} if mutant=='reset_budget' else {},{'reset':True})
