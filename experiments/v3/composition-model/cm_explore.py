"""Breadth-first closure, per-edge refinement, independent boundary and mutant checks."""
import hashlib,json,time,ctypes,os
import cm_aggregate as abstract
import cm_split,cm_inclusive
from cm_domain import State,BOOLS,POLICIES,MUTANTS,normalize

class Limit(RuntimeError):pass

def peak_bytes():
    if os.name=='nt':
        class Counters(ctypes.Structure):
            _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ('peak','rss','pp','p','pn','n','pf','ppf')]
        c=Counters();c.cb=ctypes.sizeof(c)
        k=ctypes.WinDLL('kernel32');k.GetCurrentProcess.restype=ctypes.c_void_p
        dll=ctypes.WinDLL('psapi');dll.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
        if not dll.GetProcessMemoryInfo(k.GetCurrentProcess(),ctypes.byref(c),c.cb):raise OSError('memory counter')
        return c.peak
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024

def invariant(s):
    if not isinstance(s,State):return 'state type'
    for n,x in zip(s._fields,s):
        if type(x) is not (bool if n in BOOLS else int):return 'typed field '+n
    if s.selected not in (1,2,3) or not 0<s.resident<8 or not s.resident&(1<<(s.selected-1)):return 'selected residency'
    if s.resident.bit_count()>2:return 'resident capacity'
    if s.retiring&~s.resident or s.retiring&(1<<(s.selected-1)) or s.half&~s.retiring:return 'retirement ordering'
    if s.pin and (not s.resident&1 or s.retiring&1):return 'live invocation pin'
    if not s.fork or (not s.resident&1 and not s.capsule):return 'fork continuity'
    if s.candidate not in (0,s.selected+1) or s.candidate>3:return 'candidate selection ordering'
    if s.candidate and not s.resident&(1<<(s.candidate-1)):return 'candidate residency'
    if s.staged and not s.candidate:return 'stage identity'
    if s.term not in (1,2) or s.writer not in (0,1,2) or bool(s.writer)!=bool(s.candidate):return 'writer namespace'
    if s.admission not in (1,2) or s.installed not in (1,2) or s.installed>s.admission:return 'recipient namespace'
    if s.actor not in range(4) or s.permit not in range(3) or s.effect not in range(3):return 'environment type'
    if s.receipt and s.effect!=2:return 'effect evidence identity'
    if s.executions not in (0,1) or (s.permit==1)!=(s.executions==1) or bool(s.effect)!=(s.executions==1):return 'no blind duplicate effect'
    if s.incarnation not in (1,2) or s.spent!=s.incarnation:return 'lifetime accounting'
    if s.closed not in range(4) or (s.closed&2 and s.incarnation!=2) or (s.closed&1 and s.actor not in (1,3)):return 'attempt accounting'
    if not s.pin and s.actor not in (1,3):return 'owned pin release'
    return None

def broker_edge(s,label,t):
    staged=s.staged;half=s.half
    if label=='stage':
        if not s.candidate or s.staged:return 'invalid staging transition'
        staged=True
    if label=='publish':
        if not s.candidate or not s.staged:return 'publication before staging'
        staged=False
    if label.startswith('delete_first_'):
        mask=1<<(int(label[-1])-1)
        if not s.retiring&mask or s.half&mask:return 'invalid first deletion'
        half|=mask
    if label.startswith('reclaim_'):
        mask=1<<(int(label[-1])-1)
        if not s.retiring&mask or not s.half&mask:return 'reclamation before first deletion'
        half&=~mask
    if t.staged!=staged or t.half!=half:return 'hidden broker mutation'
    return None

def trace(parents,i):
    labels=[]
    while parents[i] is not None:i,label=parents[i];labels.append(label)
    return list(reversed(labels))

def signature(edges):return hashlib.sha256(repr(sorted(edges)).encode()).hexdigest()

def witnesses(s,label,t,policy):
    out=[]
    if t.selected==2 and t.pin:out.append('g2_with_live_g1')
    if label=='status_hold' and s.pin:out.append('g3_hold_live_pin')
    if label=='commit_capsule' and t.pin:out.append('capsule_keeps_invocation_pin')
    if label=='wait_local' and t.effect==1 and not t.receipt:out.append('local_death_keeps_effect_unknown')
    if t.selected==3 and t.capsule and t.fork and not t.resident&1:out.append('g3_after_safe_reclaim')
    if label=='status_hold' and not s.pin and policy=='resident':out.append('resident_fork_holds_g3')
    if label=='restart_authority' and s.reply and s.selected>=2 and t.selected==s.selected and t.pin==s.pin:out.append('commit_survives_restart')
    if label=='stale_writer_refused':out.append('stale_writer_refusal')
    if label=='publish' and s.term==2 and s.writer==2:out.append('fresh_writer_publication')
    if label=='execute_exposed':out.append('preinstallation_exposure')
    if label=='stale_permit_refused':out.append('postinstallation_refusal')
    if label=='current_receipt':out.append('valid_current_receipt')
    if label=='late_receipt' and s.incarnation==2 and not t.closed&2:out.append('late_receipt_preserves_attempt2')
    if label=='old_transport_ack' and s.effect==1 and not t.closed&2 and not t.receipt:out.append('old_ack_preserves_unknown_attempt')
    if label=='close_attempt2' and s.receipt:out.append('own_attempt2_completion')
    if label=='pool_reset' and s.incarnation==2 and t.spent==2:out.append('reset_conserves_two_segments')
    if label=='inspect_fork' and s.admission==2 and s.capsule and not s.resident&1 and t.admission==2:out.append('fork_inspection_no_authority_restore')
    if label=='query_same_operation' and s.receipt and t.executions==1:out.append('settled_query_no_reexecution')
    if t.selected==3 and t.effect==1 and not t.receipt and t.capsule and t.fork and not t.resident&1 and t.spent==2:out.append('g3_with_unknown_effect')
    if label=='late_receipt' and s.selected==3 and not s.resident&1 and s.incarnation==2 and not t.closed&2:out.append('late_receipt_after_reclaim')
    return out

def explore(module,policy,limits,mutant=None,reference=None):
    begin=time.perf_counter();initial=module.initial();nodes=[initial];parents=[None];depths=[0];lookup={initial:0};head=0;count=0;found={};projections=set();edges_by_state={};maxdepth=0
    if abstract.project(normalize(initial))!=abstract.initial():return {'failure':'initial projection','trace':[]},{}
    while head<len(nodes):
        if head%512==0:
            if len(nodes)>limits['states_per_boundary'] or time.perf_counter()-begin>limits['seconds_per_experiment'] or peak_bytes()>limits['memory_bytes']:
                raise Limit(json.dumps({'boundary':module.__name__,'policy':policy,'mutant':mutant,'states':len(nodes),'expanded':head,'frontier':len(nodes)-head,'elapsed_seconds':time.perf_counter()-begin,'peak_bytes':peak_bytes()}))
        state=nodes[head];s=normalize(state);a=abstract.project(s);projections.add(a);out=list(module.successors(state,policy,mutant));normal=[(label,normalize(t)) for label,t in out]
        failure=invariant(s)
        if len(set(normal))!=len(normal):failure='duplicate declared edge'
        if s.admission==1 and 'stop' not in [label for label,_ in out]:failure='independent Stop disabled'
        if not any(label in ('status','status_hold') for label,_ in out):failure='status disabled'
        if failure:return {'failure':failure,'trace':trace(parents,head),'state':s._asdict()},{}
        sig=signature(normal)
        if reference is not None and reference.get(s)!=sig:return {'failure':'independent boundary edge mismatch','trace':trace(parents,head),'state':s._asdict()},{}
        edges_by_state[s]=sig
        for label,target in out:
            t=normalize(target);failure=invariant(t)
            expected=abstract.step(a,label,policy)
            if not failure:failure=broker_edge(s,label,t)
            if not failure and (expected is None or expected!=abstract.project(t)):failure='aggregate transition/refinement'
            if failure:return {'failure':failure,'trace':trace(parents,head)+[label],'before':s._asdict(),'after':t._asdict(),'expanded':head},{}
            count+=1
            for name in witnesses(s,label,t,policy):
                if name not in found:found[name]=trace(parents,head)+[label]
            if target not in lookup:
                lookup[target]=len(nodes);nodes.append(target);parents.append((head,label));depths.append(depths[head]+1);maxdepth=max(maxdepth,depths[-1])
        head+=1
    if reference is not None and len(reference)!=len(nodes):return {'failure':'independent boundary state coverage','trace':[]},{}
    digest=hashlib.sha256()
    for s in sorted(edges_by_state):digest.update(repr(s).encode());digest.update(edges_by_state[s].encode())
    result={'status':'closed-finite-subsystem','states':len(nodes),'expanded':head,'transitions':count,'frontier':0,'maximum_depth':maxdepth,'projected_states':len(projections),'duplicate_projections':len(nodes)-len(projections),'graph_sha256':digest.hexdigest(),'witnesses':found}
    return result,edges_by_state

def replay(module,policy,labels):
    state=module.initial();rows=[]
    for label in labels:
        s=normalize(state);options=[t for name,t in module.successors(state,policy) if name==label]
        if len(options)!=1:raise ValueError('ordered witness not executable '+label)
        state=options[0];t=normalize(state)
        failure=invariant(t) or broker_edge(s,label,t)
        if failure or abstract.step(abstract.project(s),label,policy)!=abstract.project(t):raise ValueError('ordered witness safety '+str(failure))
        rows.append({'action':label,'before':s._asdict(),'after':t._asdict()})
    return rows

def ordered_controls():
    traces={
        'committed_reply_lost_after_restart':['prepare','stage','publish','restart_authority','publication_reply_lost'],
        'partial_reclamation_restart':['prepare','stage','publish','publication_ack','commit_capsule','kill_local','wait_local','release_pin','retire_1','delete_first_1','restart_authority','reclaim_1'],
        'composed_retention_revocation_late_receipt':['execute','prepare','stage','publish','publication_ack','request_g3','status_hold','stop','install_fence','commit_capsule','status_hold','kill_local','wait_local','release_pin','close_attempt1','new_query_incarnation','pool_reset','old_transport_ack','retire_1','delete_first_1','reclaim_1','prepare','stage','publish','inspect_fork','query_same_operation','remote_complete','late_receipt','close_attempt2'],
    }
    out={}
    for name,labels in traces.items():
        a=replay(cm_split,'capsule',labels);b=replay(cm_inclusive,'capsule',labels)
        if a!=b:raise ValueError('ordered boundary mismatch')
        out[name]=a
    return out

def calibrations(limits):
    class WrongInitial:
        @staticmethod
        def initial():return State(admission=2)
    r,_=explore(WrongInitial,'capsule',limits)
    if r.get('failure')!='initial projection':raise ValueError('initial calibration')
    initial=State();ref={initial:signature([(l,normalize(t)) for l,t in cm_split.successors(cm_split.initial(),'capsule')])}
    class MissingEdge:
        initial=staticmethod(cm_inclusive.initial)
        @staticmethod
        def successors(s,p,m):return [(l,t) for l,t in cm_inclusive.successors(s,p,m) if l!='prepare']
    r,_=explore(MissingEdge,'capsule',limits,reference=ref)
    if r.get('failure')!='independent boundary edge mismatch':raise ValueError('edge calibration')
    tiny=dict(limits,states_per_boundary=1)
    try:explore(cm_split,'capsule',tiny)
    except Limit as exc:
        detail=json.loads(str(exc))
        if detail['frontier']<=0:raise ValueError('frontier calibration')
    else:raise ValueError('truncation accepted')
    return {'wrong_initial':'rejected','missing_edge':'rejected','truncated_graph':'incomplete','truncated_frontier':detail['frontier']}

COMMON={'g2_with_live_g1','g3_hold_live_pin','local_death_keeps_effect_unknown','commit_survives_restart','stale_writer_refusal','fresh_writer_publication','preinstallation_exposure','postinstallation_refusal','valid_current_receipt','late_receipt_preserves_attempt2','old_ack_preserves_unknown_attempt','own_attempt2_completion','reset_conserves_two_segments','settled_query_no_reexecution'}
def run(limits):
    results={};controls=[]
    for policy in POLICIES:
        left,ref=explore(cm_split,policy,limits)
        if 'failure' in left:raise ValueError(json.dumps(left))
        right,_=explore(cm_inclusive,policy,limits,reference=ref)
        if right!=left:raise ValueError('independent graph/report mismatch '+repr(right))
        required=COMMON|({'capsule_keeps_invocation_pin','g3_after_safe_reclaim','fork_inspection_no_authority_restore','g3_with_unknown_effect','late_receipt_after_reclaim'} if policy=='capsule' else {'resident_fork_holds_g3'})
        if set(left['witnesses'])!=required:raise ValueError('witness coverage '+repr(set(left['witnesses'])^required))
        results[policy]={'split':left,'inclusive':right};del ref
        print('CLOSED '+policy+' '+str(left['states'])+' states',flush=True)
    for mutant in MUTANTS:
        pair=[]
        for module in (cm_split,cm_inclusive):
            r,_=explore(module,'capsule',limits,mutant=mutant)
            if 'failure' not in r:raise ValueError('vacuous mutant '+mutant)
            pair.append(r)
        if pair[0]['failure']!=pair[1]['failure']:raise ValueError('mutant cause mismatch '+mutant)
        controls.append({'mutant':mutant,'split':pair[0],'inclusive':pair[1]})
    return {'ordered_witnesses':ordered_controls(),'calibrations':calibrations(limits),'status':'conditional-composition-pass','classification':'modeled','profiles':results,'mutants':controls,'formal_freeze':False,'liveness':'not-proved; existential recovery witnesses only','production_authentication':False,'full_core_cross_profiles':False,'live_provider_calls':0}
