"""Independent finite graph, refinement and weak-fair-cycle checker."""
import collections,ctypes,hashlib,json,os,time
import aggregate
import split
import inclusive
from domain import CONFIG,FAIR_ACTIONS,LIMIT,CHANNEL,FRAME,CREDIT_SOURCES,TOKENS

class ExplorationLimit(RuntimeError):pass

def flat(s):
    if isinstance(s,split.Split):
        k,b=s
        return (1 if k.waiting else 2 if k.fenced else 0,k.effect_unknown,b.phase,b.cursor,b.credit,b.pending,
                (b.sdk,b.pump,b.inbox),b.partial,b.loss_used,b.ingress_unknown,b.credit_offers,b.acknowledged,b.credit_seen)
    return tuple(s)

def abstract(s):
    c,u,p,v,credit,pending,channels,fragment,dropped,gap,issued,ack,saw=flat(s)
    return aggregate.Abstract(c==1,c==2,u,p,v,credit,pending,gap,ack,saw)

def resident_peak():
    if os.name=='nt':
        class Counters(ctypes.Structure):
            _fields_=[('cb',ctypes.c_ulong),('faults',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ['peak','current','peak_paged','paged','peak_nonpaged','nonpaged','pagefile','peak_pagefile']]
        value=Counters();value.cb=ctypes.sizeof(value)
        kernel=ctypes.WinDLL('kernel32');kernel.GetCurrentProcess.restype=ctypes.c_void_p
        psapi=ctypes.WinDLL('psapi');psapi.GetProcessMemoryInfo.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_ulong]
        if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(value),value.cb):raise OSError('process memory receipt unavailable')
        return value.peak
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024

def action_class(label):return 'consume' if label[0]=='message' else label[0]

def path(parents,index):
    result=[]
    while parents[index] is not None:
        index,label=parents[index];result.append(label)
    return list(reversed(result))

def physical_type(state):
    if isinstance(state,split.Split):
        if any(type(x)is not bool for x in state.kernel) or (state.kernel.waiting and state.kernel.fenced):return False
    f=flat(state)
    if any(type(f[n])is not bool for n in [1,8,9,12]):return False
    if any(type(f[n])is not int for n in [0,2,3,4,7,10,11]):return False
    return (f[0] in (0,1,2) and f[2] in (0,1,2,3) and type(f[5])is tuple and all(type(x)is int for x in f[5])
            and type(f[6])is tuple and len(f[6])==3 and all(type(q)is tuple and all(type(t)is str and t in TOKENS for t in q) for q in f[6]))

def concrete_invariant(state,edges):
    if not physical_type(state):return 'complete concrete TypeOK'
    f=flat(state);control,unknown,phase,cursor,credit,pending,channels,fragment,dropped,gap,issued,ack,saw=f
    if not aggregate.invariant(abstract(state)):return 'abstract safety'
    if sum(map(len,channels))>LIMIT or any(len(q)>CHANNEL for q in channels):return 'bounded pipeline'
    if not 0<=fragment<=FRAME:return 'bounded partial frame'
    if not 0<=issued<=CREDIT_SOURCES:return 'finite credit-source domain'
    if control==0 and not any(label[0]=='stop_request' for label,_ in edges):return 'independent Stop admission'
    if control==1 and not any(label[0]=='stop_apply' for label,_ in edges):return 'continuously enabled Stop processing'
    return None

def graph(initial,next_fn,*,mutant=None,reference=None):
    started=time.perf_counter();nodes=[initial];lookup={initial:0};relation={flat(initial):0};parents=[None];depths=[0];edges=[];enabled=[]
    witnesses={};transition_count=0;head=0
    if abstract(initial)!=aggregate.Abstract():raise ValueError('initialization mapping')
    while head<len(nodes):
        if head%1024==0:
            if len(nodes)>CONFIG['max_reachable_states_per_machine'] or time.perf_counter()-started>CONFIG['checker_timeout_seconds'] or resident_peak()>CONFIG['checker_memory_budget_bytes']:
                raise ExplorationLimit(json.dumps({'states':len(nodes),'expanded':head,'frontier':len(nodes)-head,'seconds':time.perf_counter()-started}))
        state=nodes[head];out=list(next_fn(state,mutant));failure=concrete_invariant(state,out)
        if failure:return {'violation':failure,'trace':path(parents,head),'state':flat(state),'expanded':head}
        edge_keys={(label,flat(target)) for label,target in out}
        if len(edge_keys)!=len(out):raise ValueError('duplicate transition declaration')
        if reference is not None:
            other=reference['relation'].get(flat(state))
            if other is None:return {'violation':'inclusive state outside split relation','trace':path(parents,head),'state':flat(state)}
            expected={(label,flat(reference['nodes'][target])) for label,target in reference['edges'][other]}
            if edge_keys!=expected:return {'violation':'independent boundary transition mismatch','trace':path(parents,head),'missing':sorted(expected-edge_keys,key=repr),'extra':sorted(edge_keys-expected,key=repr)}
        row=[];classes=set()
        for label,target in out:
            if not physical_type(target):return {'violation':'complete target TypeOK before relation mapping','trace':path(parents,head)+[label],'target':repr(target)}
            projected=aggregate.step(abstract(state),label)
            if projected is None or projected!=abstract(target):
                return {'violation':'aggregate step/stutter refinement','trace':path(parents,head)+[label],'before':flat(state),'after':flat(target),'expected_abstract':projected,'expanded':head}
            key=target
            if key not in lookup:
                if flat(target) in relation:raise ValueError('noninjective concrete boundary relation')
                relation[flat(target)]=len(nodes)
                lookup[key]=len(nodes);nodes.append(target);parents.append((head,label));depths.append(depths[head]+1)
            child=lookup[key];row.append((label,child));classes.add(action_class(label));transition_count+=1
            if label==('message','E1','event'):witnesses.setdefault('legitimate_event',path(parents,head)+[label])
            if label==('message','RESET','reset'):witnesses.setdefault('legitimate_reset',path(parents,head)+[label])
            if label==('stop_request',) and sum(map(len,flat(state)[6]))==LIMIT:witnesses.setdefault('Stop_with_full_inflight',path(parents,head)+[label])
            if label==('stop_request',) and any(flat(state)[6][n] and len(flat(state)[6][n+1])==CHANNEL for n in (0,1)):
                witnesses.setdefault('Stop_with_blocked_upstream_pump',path(parents,head)+[label])
            if label==('stop_request',) and flat(state)[7]==FRAME:witnesses.setdefault('Stop_with_full_partial_frame',path(parents,head)+[label])
            if label==('message','CREDIT','gap-continuation'):witnesses.setdefault('non_EVENT_gap_refusal',path(parents,head)+[label])
            if label==('message','RESET','refused'):witnesses.setdefault('refusal_survives_RESET',path(parents,head)+[label])
            if label[0] in ('loss','framing_unknown'):witnesses.setdefault('/'.join(label),path(parents,head)+[label])
            if label==('loss',) and flat(state)[2]==3 and flat(target)[2]==1:witnesses.setdefault('loss_supersedes_flow_recovery',path(parents,head)+[label])
            if label==('stop_apply',):witnesses.setdefault('local_Stop_preserves_external_unknown',path(parents,head)+[label])
        edges.append(row);enabled.append(classes);head+=1
    if reference is not None and set(relation)!=set(reference['relation']):raise ValueError('boundary reachable-state coverage mismatch')
    return {'nodes':nodes,'lookup':lookup,'relation':relation,'edges':edges,'enabled':enabled,'parents':parents,'depths':depths,'witnesses':witnesses,
            'statistics':{'reachable_states':len(nodes),'transitions':transition_count,'maximum_discovered_depth':max(depths),'frontier':0,'seconds':round(time.perf_counter()-started,6),'process_peak_working_set_bytes':resident_peak(),'reductions':[],'internal_transition_depth_cutoff':None}}

def components(graph,selected):
    """Iterative Kosaraju on the induced bad-state graph, retaining self loops."""
    selected=set(selected);seen=set();order=[]
    for start in sorted(selected):
        if start in seen:continue
        seen.add(start);stack=[(start,0)]
        while stack:
            node,offset=stack[-1];out=graph['edges'][node]
            if offset==len(out):order.append(node);stack.pop();continue
            stack[-1]=(node,offset+1);child=out[offset][1]
            if child in selected and child not in seen:seen.add(child);stack.append((child,0))
    reverse={x:[] for x in selected}
    for source in selected:
        for _,target in graph['edges'][source]:
            if target in selected:reverse[target].append(source)
    seen=set();result=[]
    for start in reversed(order):
        if start in seen:continue
        component=set();stack=[start];seen.add(start)
        while stack:
            node=stack.pop();component.add(node)
            for parent in reverse[node]:
                if parent not in seen:seen.add(parent);stack.append(parent)
        if len(component)>1 or any(target==start for _,target in graph['edges'][start]):result.append(component)
    return result

def fair_bad_cycles(graph,selected,fair=FAIR_ACTIONS):
    cyclic=components(graph,selected);fair_components=[];excluded=collections.Counter()
    for component in cyclic:
        executed={action_class(label) for source in component for label,target in graph['edges'][source] if target in component}
        starving=[action for action in fair if all(action in graph['enabled'][node] for node in component) and action not in executed]
        if starving:excluded.update(starving)
        else:fair_components.append(sorted(component))
    return {'cyclic_components':len(cyclic),'fair_bad_components':len(fair_components),'excluded_by_named_weak_fairness':dict(excluded),'witness_component':fair_components[0] if fair_components else None}

def abstract_graph():
    nodes=[aggregate.Abstract()];seen=set(nodes);transitions=0
    for s in nodes:
        if not aggregate.invariant(s):raise ValueError('abstract invariant')
        for _,t in aggregate.successors(s):
            transitions+=1
            if t not in seen:seen.add(t);nodes.append(t)
    return seen,{'reachable_states':len(nodes),'transitions':transitions,'frontier':0}

def digest_graph(g):
    blocks=[]
    for node,out in zip(g['nodes'],g['edges']):
        row=[flat(node),sorted([(label,flat(g['nodes'][target])) for label,target in out],key=repr)]
        blocks.append(hashlib.sha256(json.dumps(row,separators=(',',':')).encode()).digest())
    return hashlib.sha256(b''.join(sorted(blocks))).hexdigest()

def run():
    a_nodes,a_stats=abstract_graph()
    s=graph(split.Split(),split.successors)
    if 'violation' in s:return {'status':'semantic-counterexample','boundary':'split','counterexample':s}
    if not {abstract(n) for n in s['nodes']}<=a_nodes:raise ValueError('projection outside reachable abstract graph')
    print('SPLIT_GRAPH '+json.dumps(s['statistics']),flush=True)
    i=graph(inclusive.Inclusive(),inclusive.successors,reference=s)
    if 'violation' in i:return {'status':'inadequate-proof-technique' if i['violation'] in ('inclusive state outside split relation','independent boundary transition mismatch') else 'semantic-counterexample','boundary':'inclusive','counterexample':i,'note':'Failure of the chosen internal-state isomorphism alone does not falsify visible trace inclusion.'}
    if not {abstract(n) for n in i['nodes']}<=a_nodes:raise ValueError('inclusive projection outside abstract graph')
    print('INCLUSIVE_GRAPH '+json.dumps(i['statistics']),flush=True)
    fairness={}
    for name,g in [('split',s),('inclusive',i)]:
        fairness[name]=fair_bad_cycles(g,[n for n,state in enumerate(g['nodes']) if flat(state)[0]==1])
        if fairness[name]['fair_bad_components']:raise ValueError('fair local Stop starvation')
        if not fairness[name]['cyclic_components']:raise ValueError('fairness calibration vacuous: no pending-state cycles')
    required={'legitimate_event','legitimate_reset','Stop_with_full_inflight','Stop_with_blocked_upstream_pump','Stop_with_full_partial_frame','non_EVENT_gap_refusal','refusal_survives_RESET','loss','framing_unknown/oversize','framing_unknown/eof','local_Stop_preserves_external_unknown','loss_supersedes_flow_recovery'}
    for g in [s,i]:
        if not required<=set(g['witnesses']):raise ValueError('missing reachable positive trigger')
    mutants=[]
    for name,init,successors in [('split',split.Split(),split.successors),('inclusive',inclusive.Inclusive(),inclusive.successors)]:
        for mutant in ['shared_control','gap_event_only','reset_credit','refusal_reset','hidden_loss','loss_retains_flow','unbounded_frame','queue_overflow','stage_overflow','false_settlement','deny_event']:
            result=graph(init,successors,mutant=mutant)
            if 'violation' not in result:raise ValueError('vacuous mutant '+name+'/'+mutant)
            mutants.append({'boundary':name,'mutant':mutant,'counterexample':result})
    sd,id_=digest_graph(s),digest_graph(i)
    if sd!=id_:raise ValueError('isomorphic graph digest differs')
    return {'status':'conditional-subsystem-pass','abstract_graph':a_stats,'split':s['statistics'],'inclusive':i['statistics'],
            'graph_sha256':sd,'mapping_checks':{'initialization':True,'every_reachable_step_or_visible_stutter':True,'concrete_and_abstract_invariants':True,'split_composition':True,'separate_inclusive_transition_relation_checked':True,'named_weak_fairness_Stop_progress':True},
            'fairness':fairness,'positive_witnesses':s['witnesses'],'mutant_counterexamples':mutants,'full_comparison_complete':False,'formal_freeze':False}

if __name__=='__main__':
    try:print(json.dumps(run(),indent=2))
    except ExplorationLimit as exc:print(json.dumps({'status':'exploration-limit','detail':str(exc),'formal_freeze':False}));raise SystemExit(2)
