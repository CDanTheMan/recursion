"""Exhaustive closure of each declared external schedule, with exact graph comparison."""
import hashlib,json,time
from collections import deque
from dataclasses import replace
import sc_domain as d,sc_audit as audit,sc_inclusive as inc,sc_split as split

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def path(parents,index):
    result=[]
    while index:
        index,action=parents[index];result.append(action)
    return list(reversed(result))

def explore(profile,boundary,mutant='',limit=500000,seconds=600):
    start=time.monotonic();seed=d.State();audit.initial(seed)
    values=[seed];indices={seed:0};parents=[None];graph=[];cursor=0
    while cursor<len(values):
        if len(values)>limit or time.monotonic()-start>seconds:
            raise ValueError('incomplete frontier/resource limit '+profile)
        s=values[cursor]
        edges=list(inc.edges(s,profile,mutant)) if boundary=='inclusive' else [(a,split.flat(n)) for a,n in split.edges(split.pack(s),profile)]
        edges.sort(key=lambda row:row[0])
        try:audit.enabled(s,profile,[a for a,_ in edges])
        except ValueError as e:
            if mutant:return {'guard':mutant,'profile':profile,'obligation':str(e),'trace':path(parents,cursor),'before':d.key(s),'after':None}
            raise
        outgoing=[]
        for action,n in edges:
            try:audit.edge(s,action,n,profile)
            except ValueError as e:
                if mutant:return {'guard':mutant,'profile':profile,'obligation':str(e),'trace':path(parents,cursor)+[action],'before':d.key(s),'after':d.key(n)}
                raise ValueError(profile+' '+str(e)+' '+str(path(parents,cursor)+[action])) from e
            if n not in indices:
                indices[n]=len(values);values.append(n);parents.append((cursor,action))
            outgoing.append((action,indices[n]))
        graph.append(tuple(outgoing));cursor+=1
    if mutant:raise ValueError('vacuous mutant '+mutant+' '+profile)
    return values,graph,parents

def graph_receipt(values,graph):
    h=hashlib.sha256()
    for s,edges in zip(values,graph):h.update((canonical([d.key(s),edges])+'\n').encode())
    return {'states':len(values),'edges':sum(map(len,graph)),'frontier':0,'graph_sha256':h.hexdigest()}

def calibrate():
    labels=[]
    def rejects(label,fn):
        try:fn()
        except ValueError:labels.append(label);return
        raise ValueError('checker accepted calibration '+label)
    s=d.State();p='recipient-refusal';actual=list(inc.edges(s,p))
    rejects('wrong-initial',lambda:audit.initial(replace(s,spent=0)))
    rejects('missing-edge',lambda:audit.enabled(s,p,[a for a,_ in actual if a!='stop']))
    rejects('changed-edge',lambda:audit.edge(s,'status',replace(s,quarantine=False),p))
    rejects('truncated-frontier',lambda:explore(p,'inclusive',limit=1))
    return labels
