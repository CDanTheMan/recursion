"""Reachable product graph, specification simulation and independent relation check."""
import collections,ctypes,hashlib,json,os,time
import domain as D
import specification as A
import split_model as S
import inclusive_model as I
from audit import Audit,advance,decision
class Limit(RuntimeError):pass
def peak():
    class Memory(ctypes.Structure):
        _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ['peak','current','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile']]
    m=Memory();m.cb=ctypes.sizeof(m);k=ctypes.WinDLL('kernel32');k.GetCurrentProcess.restype=ctypes.c_void_p
    p=ctypes.WinDLL('psapi');p.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
    if not p.GetProcessMemoryInfo(k.GetCurrentProcess(),ctypes.byref(m),m.cb):raise OSError('memory observation failed')
    return m.peak
def signature(s,module):return module.visible(s),module.physical(s)
def typed(s,module):
    v=module.visible(s);held,channels,fragment=module.physical(s)
    return (A.invariant(v) and type(fragment)is int and type(held)is tuple and type(channels)is tuple and len(channels)==3 and all(type(q)is tuple and all(type(n)is int for n in q) for q in [held,*channels]))
def bounds(s,module):
    held,channels,fragment=module.physical(s)
    return len(held)<=D.RETAINED and all(len(q)<=D.CHANNEL for q in channels) and sum(map(len,channels))<=D.INFLIGHT and 0<=fragment<=D.FRAME
def audit_binding(v,a,unit):
    expected=D.cursor(v.loss if v.phase==2 else v.position,unit)
    return (a.cursor==expected and a.acknowledged==D.cursor(v.acknowledged,unit) and a.byte_credit==v.byte_credit and a.event_credit==v.event_credit
            and a.pending==tuple((D.cursor(n,unit),D.COSTS[n-1]) for n in v.pending) and a.recovery==(2 if v.phase==2 else 0)
            and a.reasons==(frozenset({'replay-gap'}) if v.phase==2 or v.covered else frozenset()) and a.unit in ('',unit))
def trace(parents,n):
    out=[]
    while parents[n] is not None:n,label=parents[n];out.append(label)
    return list(reversed(out))
def graph(unit,mutant=None):
    start=time.perf_counter();seed=Audit()
    for kind in ['hello','welcome']:seed=advance(seed,D.wire((kind,),D.Visible(),unit),D.QUEUE_BYTES,D.QUEUE_EVENTS)
    initial=(S.State(),I.State(),seed);nodes=[initial];lookup={(initial[0],initial[2]):0};relation={signature(initial[1],I):signature(initial[0],S)}
    parents=[None];depth=[0];edges=[];enabled=[];head=0;transitions=0;witnesses={};digest=hashlib.sha256()
    def failure(reason,path,**details):return dict(status='counterexample',violation=reason,trace=path,unit=unit,mutant=mutant,**details)
    while head<len(nodes):
        if head%512==0 and (len(nodes)>D.MAX_STATES or time.perf_counter()-start>D.TIMEOUT_SECONDS or peak()>D.MEMORY_BYTES):
            raise Limit(json.dumps(dict(unit=unit,states=len(nodes),expanded=head,frontier=len(nodes)-head,seconds=time.perf_counter()-start)))
        s,i,a=nodes[head];v=S.visible(s);out=list(S.successors(s,mutant));other=list(I.successors(i,mutant))
        if not typed(s,S) or not typed(i,I):return failure('source TypeOK/conservation',trace(parents,head))
        if not bounds(s,S) or not bounds(i,I):return failure('physical capacity',trace(parents,head))
        if not audit_binding(v,a,unit):return failure('independent audit product binding',trace(parents,head))
        left={(l,signature(t,S)) for l,t in out};right={(l,signature(t,I)) for l,t in other}
        if left!=right:return failure('inadequate internal correspondence technique',trace(parents,head))
        if len(left)!=len(out):return failure('duplicate transition declaration',trace(parents,head))
        by_label={l:t for l,t in other};classes={l[0] for l,_ in out}
        if v.control==0 and 'stop_request' not in classes:return failure('independent Stop admission',trace(parents,head))
        if v.control==1 and 'stop_apply' not in classes:return failure('continuously enabled Stop',trace(parents,head))
        row=[]
        for label,target in out:
            it=by_label[label];tv=S.visible(target);path=None
            if not typed(target,S) or not typed(it,I):return failure('target TypeOK/conservation',trace(parents,head)+[label])
            if not bounds(target,S) or not bounds(it,I):return failure('target physical capacity',trace(parents,head)+[label])
            projected=A.step(v,label)
            if projected is None or projected!=tv:return failure('specification step/stutter simulation',trace(parents,head)+[label])
            m=D.wire(label,v,unit);aa=advance(a,m,D.QUEUE_BYTES,D.QUEUE_EVENTS)
            if not audit_binding(tv,aa,unit):return failure('independent audit product binding',trace(parents,head)+[label])
            key=(target,aa)
            if key not in lookup:
                sig=signature(it,I);match=signature(target,S)
                if sig in relation and relation[sig]!=match:return failure('noninjective concrete relation',trace(parents,head)+[label])
                relation[sig]=match;lookup[key]=len(nodes);nodes.append((target,it,aa));parents.append((head,label));depth.append(depth[head]+1)
            child=lookup[key];row.append((label,child));transitions+=1
            digest.update(repr((signature(s,S),a,label,signature(target,S),aa)).encode())
            def witness(name):witnesses.setdefault(name,trace(parents,head)+[label])
            if label[0]=='stop_request':
                held,qs,part=S.physical(s)
                if sum(map(len,qs))==D.INFLIGHT:witness('Stop_full_pipeline')
                if any(qs[j] and len(qs[j+1])==D.CHANNEL for j in (0,1)):witness('Stop_blocked_pump')
                if part==D.FRAME:witness('Stop_full_partial_frame')
                if v.phase==2:witness('Stop_pending_RESET')
            if label[0]=='welcome':witness('WELCOME_audit_ahead_of_installation')
            if label[0]=='reset' and tv.live:witness('RESET_preserves_future_candidates')
            if label[0]=='evict' and label[1]>v.position+1:witness('loss_with_earlier_candidate_pending')
            if label[0]=='emit' and tv.position==4 and tv.covered:witness('recovered_delivery_complete')
            if label[0]=='emit' and tv.position==4 and not tv.loss:witness('no_loss_delivery_complete')
            if s.broker.channels[2] and not any(l[0]=='emit' for l,_ in out):
                n=s.broker.channels[2][0]
                if n==v.position+1 and v.event_credit>0 and v.byte_credit<D.COSTS[n-1]:witness('byte_credit_deferral')
                if n==v.position+1 and len(v.pending)<D.QUEUE_EVENTS and sum(D.COSTS[k-1] for k in v.pending)+D.COSTS[n-1]>D.QUEUE_BYTES:witness('queue_byte_deferral')
        edges.append(row);enabled.append(classes);head+=1
    return dict(status='graph-pass',unit=unit,nodes=nodes,edges=edges,enabled=enabled,witnesses=witnesses,statistics=dict(product_states=len(nodes),transitions=transitions,frontier=0,maximum_depth=max(depth),depth_cutoff=None,seconds=round(time.perf_counter()-start,6),peak_memory_bytes=peak(),graph_sha256=digest.hexdigest(),inclusive_method='exact local correspondence checked at every reachable split/audit product state; closure covers both definitions'))
def fairness(g):
    # Standard iterative SCC decomposition, induced on pending-Stop states.
    selected={n for n,(s,_,_) in enumerate(g['nodes']) if S.visible(s).control==1};seen=set();order=[]
    for first in selected:
        if first in seen:continue
        seen.add(first);stack=[(first,0)]
        while stack:
            n,j=stack[-1];row=g['edges'][n]
            if j==len(row):order.append(n);stack.pop();continue
            stack[-1]=(n,j+1);child=row[j][1]
            if child in selected and child not in seen:seen.add(child);stack.append((child,0))
    reverse={n:[] for n in selected}
    for n in selected:
        for _,child in g['edges'][n]:
            if child in selected:reverse[child].append(n)
    seen=set();cyclic=excluded=bad=0
    for first in reversed(order):
        if first in seen:continue
        component=set();todo=[first];seen.add(first)
        while todo:
            n=todo.pop();component.add(n)
            for parent in reverse[n]:
                if parent not in seen:seen.add(parent);todo.append(parent)
        if len(component)>1 or any(child==first for _,child in g['edges'][first]):
            cyclic+=1;internal={label[0] for n in component for label,child in g['edges'][n] if child in component}
            if all('stop_apply' in g['enabled'][n] for n in component) and 'stop_apply' not in internal:excluded+=1
            else:bad+=1
    return dict(pending_Stop_cyclic_components=cyclic,excluded_by_named_Stop_weak_fairness=excluded,fair_bad_components=bad,without_named_fairness_bad_components=cyclic)
