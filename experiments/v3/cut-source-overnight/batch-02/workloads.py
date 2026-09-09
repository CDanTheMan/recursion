"""Finite periodic workload graphs with exact predecessor and three-policy projections."""
from collections import deque
import hashlib
import itertools
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
PRIOR=ROOT/"experiments/v3/cut-source-overnight/append-handoff-01"
sys.path.insert(0,str(PRIOR))
import h_encoding as old_encoding
import h_unified as old_unified
import h_separated as old_separated
import h_relation as old_relation
import h_experiment as old_experiment
import b_encoding
import b_unified
import b_separated
import b_relation
require=old_relation.require
PERIODS=("AC","AAC","ACC")
SIZES=(2,3,4)


def encoded(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def sha(x): return hashlib.sha256(x).hexdigest()
def write(path,x): path.write_bytes(encoded(x)+b"\n")
def project(state): return (*state[:3],state[3][:13],state[4][:13])
def is_complete(s,n): return s[1]==n and all(p[0]==n and p[4]==n and not p[3] for p in s[3:])


def choices(node,n,w):
    phase,k,state=node
    if phase=="prefix" and k<6: return [(a,"prefix",k+1) for a in "OAC"]
    if phase in ("prefix","offer"):
        if state[1]<n: return [("O","offer",0 if phase=="prefix" else k+1)]
        return [(w[0],"service",1)]
    limit=len(w)*((n+1)*(n+2)+1)
    return [(w[k%len(w)],"service",k+1)] if k<limit else []


def schedule_relation(node,options,n,w):
    phase,depth,state=node
    require(w in ("AC","AAC","ACC"),"declared service period")
    if phase=="prefix" and depth<6:
        expected=[(a,"prefix",depth+1) for a in ("O","A","C")]
    elif phase in ("prefix","offer"):
        expected=[("O","offer",0 if phase=="prefix" else depth+1)] if state[1]!=n else [("A","service",1)]
    else:
        bound=len(w)*((n+1)*(n+2)+1)
        require(phase=="service" and 1<=depth<=bound,"periodic phase bounds")
        if depth==bound: expected=[]
        else:
            position=depth%len(w)
            action="C" if (w=="AC" and position==1) or (w=="AAC" and position==2) or (w=="ACC" and position!=0) else "A"
            expected=[(action,"service",depth+1)]
    require(options==expected,"independent complete schedule equation")
    if w=="AC": old_relation.schedule_valid(node,options,n)


def graph(n,w,step,three,budget):
    encoding,relation=(b_encoding,b_relation) if three else (old_encoding,old_relation)
    first=("prefix",0,encoding.initial(n));relation.initial_valid(first[2],n)
    nodes=[first];ids={first:0};edges=[];parents=[None];terminals=[];pending=deque([0])
    while pending:
        source=pending.popleft();node=nodes[source];options=choices(node,n,w);schedule_relation(node,options,n,w)
        if not options:
            relation.complete(node[2],n);terminals.append(source)
        for action,phase,depth in options:
            after=step(node[2],action,n);relation.transition(node[2],action,after,n)
            if three:
                before_projection=project(node[2]);after_projection=project(after)
                require(after_projection==old_unified.step(before_projection,action,n)==old_separated.step(before_projection,action,n),"both unchanged predecessor projections")
                old_relation.transition(before_projection,action,after_projection,n)
            target=(phase,depth,after)
            if target not in ids:
                require(len(nodes)<budget,"cumulative new representation state cap")
                ids[target]=len(nodes);nodes.append(target);parents.append((source,action));pending.append(ids[target])
            edges.append((source,action,ids[target]))
    return nodes,edges,parents,terminals


def witness(g,index,three):
    word=[];current=index
    while g[2][current] is not None:
        current,a=g[2][current];word.append(a)
    state=g[0][index][2];metrics=(b_encoding if three else old_encoding).metrics(state)
    (b_relation if three else old_relation).metric_valid(state,metrics)
    return {"node":index,"actions":"".join(reversed(word)),"metrics":metrics}


def summarize(g,n,w,three):
    nodes,edges,parents,terminals=g;enc,rel=(b_encoding,b_relation) if three else (old_encoding,old_relation)
    labels=("one","drain","two") if three else ("one","drain")
    measured=[];bound=n*(n+1)//2;useful=n-1+2*n+bound
    require((n+1)*(n+2)+1>useful,"period reserve proof arithmetic")
    for phase,depth,state in nodes:
        rel.metric_valid(state,enc.metrics(state))
        require(all(p[7]<=n and sum(p[6])<=bound for p in state[3:]),"all-state finite work bounds")
        if three:
            drain,two=state[4],state[5]
            require(drain[0]>=two[0] and all(drain[12][i]<=two[12][i] for i in range(two[0])),"hypothesized drain matched-record waiting dominance")
            if n<=3: require(drain[:13]==two[:13],"small-inventory exact projected equivalence")
    # Completion edges identify actual completion, not the padded terminal clock.
    completions=[]
    for source,action,target in edges:
        before,after=nodes[source][2],nodes[target][2]
        if not is_complete(before,n) and is_complete(after,n):
            start=max(6,after[2][-1]);require(after[0]<=start+len(w)*useful,"conditional joint completion bound")
            completions.append(after[0]-start)
    require(completions,"positive joint completion witnesses")
    for i in terminals:
        state=nodes[i][2];start=max(6,state[2][-1])
        require(all(p[12][j]<=start-state[2][j]+len(w)*useful for p in state[3:] for j in range(n)),"per-record conditional wait bound")
        if three: require(sum(state[5][6])-sum(state[4][6]) in (0,3),"hypothesized completed read difference")
        measured.append(enc.metrics(state))
    maxima={}
    for label in labels:
        maxima[label]=[]
        for record in range(n):
            value=max(m[label]["completed_waits"][record] for m in measured)
            i=next(t for t,m in zip(terminals,measured) if m[label]["completed_waits"][record]==value)
            maxima[label].append({"record":record,"maximum_wait":value,"attaining_witness":witness(g,i,three)})
    comparisons={}
    for a,b in itertools.combinations(labels,2):
        pairs=[(m[a]["read_work"],m[b]["read_work"]) for m in measured]
        comparisons[a+"_vs_"+b]={"first_fewer":sum(x<y for x,y in pairs),"equal":sum(x==y for x,y in pairs),"second_fewer":sum(x>y for x,y in pairs)}
    return {"records":n,"period":w,"period_ticks":len(w),"states_per_representation":len(nodes),"edges_per_representation":len(edges),
            "terminal_count":len(terminals),"frontier":0,"comparison_count_basis":"distinct complete states, not schedule probabilities",
            "terminal_read_comparisons":comparisons,"read_work_ranges":{k:[min(m[k]["read_work"] for m in measured),max(m[k]["read_work"] for m in measured)] for k in labels},
            "per_record_wait_maxima":maxima,"read_work_bound":bound,"useful_operation_bound":useful,
            "completion_ticks_after_suffix_start_maximum":max(completions),"conditional_completion_ticks_bound":len(w)*useful,
            "small_inventory_drain_two_equivalence":True if three and n<=3 else None,
            "drain_two_wait_dominance":True if three else None,"drain_two_completed_read_difference_0_or_3":True if three else None}


def explore(directory,three=False,baseline=None,used=0):
    directory.mkdir();profiles=[];graphs={};total=used
    previous=json.loads((ROOT/"docs/v3/construction/cut-source-overnight-20260908/append-handoff-01/results.json").read_text())["finite"]["profiles"]
    for n in SIZES:
        for w in PERIODS:
            f,g=(b_unified.step,b_separated.step) if three else (old_unified.step,old_separated.step)
            a=graph(n,w,f,three,500000-total);b=graph(n,w,g,three,500000-total)
            require(a==b,"exact graphs, parents and terminals")
            total+=len(a[0]);graphs[(n,w)]=a
            if three:
                base=baseline[(n,w)];base_ids={v:i for i,v in enumerate(base[0])}
                projection=[base_ids[(phase,k,project(s))] for phase,k,s in a[0]]
                require(set(projection)==set(range(len(base[0]))),"onto complete B node set")
                require({(projection[s],act,projection[t]) for s,act,t in a[1]}==set(base[1]),"exact B edge projection")
            raw=encoded(dict(zip(("nodes","edges","parents","terminals"),a)))+b"\n"
            if not three and w=="AC":require(sha(raw)==next(p["graph_sha256"] for p in previous if p["record_count"]==n),"exact preserved AC graph bytes")
            name=f"N{n}-{w}-graph.json";(directory/name).write_bytes(raw)
            profile=summarize(a,n,w,three);profile.update(graph_file=name,graph_sha256=sha(raw),exact_graph_equality=True,independent_all_edge_relation=True,predecessor_projection_exact=True if three else None)
            profiles.append(profile)
    result={"status":"THREE_POLICY_FINITE_PASS" if three else "PERIODIC_WORKLOAD_FINITE_PASS","profiles":profiles,
            "states_per_representation":total-used,"cumulative_new_states_per_representation":total,"frontier":0,
            "original_stream_counts":[3,2,4,4],"distinct_count_domains":list(SIZES),"periods":list(PERIODS),"prefix_length":6,
            "source_validity_proven":False,"formal_freeze":False,"full_comparison_complete":False}
    return result,graphs


def matched_prefixes(graphs):
    output=[]
    for n in SIZES:
        indexed={}
        for w in PERIODS:
            g=graphs[(n,w)];steps={}
            for src,act,dst in g[1]: steps.setdefault(src,{})[act]=dst
            endpoints={}
            for symbols in itertools.product("OAC",repeat=6):
                prefix="".join(symbols);node=0;actions=prefix
                for a in prefix:node=steps[node][a]
                while node in steps:
                    require(len(steps[node])==1,"unique registered suffix")
                    a,node=next(iter(steps[node].items()));actions+=a
                require(node in g[3],"registered complete endpoint")
                endpoints[prefix]={"actions":actions,"metrics":old_encoding.metrics(g[0][node][2])}
            indexed[w]=endpoints
        for first,second in itertools.combinations(PERIODS,2):
            for policy in ("one","drain"):
                rows=[];examples={}
                for prefix in indexed[first]:
                    a=indexed[first][prefix];b=indexed[second][prefix];ma=a["metrics"][policy];mb=b["metrics"][policy]
                    read_sign=(ma["read_work"]>mb["read_work"])-(ma["read_work"]<mb["read_work"])
                    wait_signs=[(x>y)-(x<y) for x,y in zip(ma["completed_waits"][1:],mb["completed_waits"][1:])]
                    rows.append((read_sign,wait_signs))
                    for label,yes in (("first_fewer_reads",read_sign<0),("second_fewer_reads",read_sign>0),
                                      ("first_earlier_record",-1 in wait_signs),("second_earlier_record",1 in wait_signs)):
                        if yes and label not in examples:examples[label]={"prefix":prefix,"first":a,"second":b}
                output.append({"records":n,"periods":[first,second],"policy":policy,"prefix_words":len(rows),
                               "basis":"same 729 preregistered H6 words; counts are not probabilities",
                               "read_comparison_counts":{str(k):sum(s==k for s,w in rows) for k in (-1,0,1)},
                               "record_wait_comparison_counts":{str(k):sum(t==k for s,ws in rows for t in ws) for k in (-1,0,1)},
                               "sign_meaning":"-1 first smaller,0 equal,1 second smaller","witnesses":examples})
    return output
