"""Complete finite closure; a limit is failure, never success."""
import hashlib,json,time
from dataclasses import asdict,replace
import wr_domain as d,wr_audit as audit,wr_inclusive as inc,wr_split as split

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def path(parents,i):
    trace=[]
    while i:
        i,label=parents[i];trace.append(label)
    return trace[::-1]

def explore(name,design,boundary,mutant=None,limit=500000,seconds=600):
    p=d.PROFILES[name];seed=d.initial(design);audit.initial(seed,design)
    states=[seed];index={seed:0};parents=[None];graph=[];cursor=0;began=time.monotonic()
    while cursor<len(states):
        audit.require(len(states)<=limit and time.monotonic()-began<=seconds,'incomplete nonempty frontier/resource limit')
        s=states[cursor]
        edges=list(inc.edges(s,p,design,mutant)) if boundary=='inclusive' else [(a,split.flat(t)) for a,t in split.edges(split.pack(s),p,design)]
        edges.sort(key=lambda e:e[0]);audit.enabled(s,p,[a for a,_ in edges]);row=[]
        for a,t in edges:
            try:audit.edge(s,a,t,p,design)
            except ValueError as e:
                if mutant:return {'guard':mutant,'profile':name,'design':design,'obligation':str(e),'trace':path(parents,cursor)+[a],'before':asdict(s),'after':asdict(t)}
                raise ValueError(name+'/'+design+'/'+boundary+': '+str(e)+' '+repr(path(parents,cursor)+[a])) from e
            if t not in index:index[t]=len(states);states.append(t);parents.append((cursor,a))
            row.append((a,index[t]))
        graph.append(tuple(row));cursor+=1
    audit.require(mutant is None,'vacuous guard mutation '+str(mutant))
    return states,graph

def receipt(states,graph):
    digest=hashlib.sha256()
    for s,row in zip(states,graph):digest.update((canonical([asdict(s),row])+'\n').encode())
    return {'states':len(states),'edges':sum(map(len,graph)),'frontier':0,'graph_sha256':digest.hexdigest()}

def witness(name,design,actions=None):
    p=d.PROFILES[name];s=d.initial(design);events=[];audit.initial(s,design)
    for a in actions or p['actions']:
        matches=[(label,n) for label,n in inc.edges(s,p,design) if label.split('=')[0]==a]
        audit.require(len(matches)==1,'ordered witness enabled '+a)
        label,n=matches[0];audit.edge(s,label,n,p,design)
        other=dict(split.edges(split.pack(s),p,design));audit.require(label in other and split.flat(other[label])==n,'witness split correspondence')
        events.append({'label':label,'before':asdict(s),'after':asdict(n)});s=n
    return {'events':events,'final':asdict(s)}

def calibrate():
    result=[]
    def rejects(name,fn):
        try:fn()
        except ValueError:result.append(name);return
        raise ValueError('ineffective checker calibration '+name)
    s=d.initial('central');p=d.PROFILES['free-admission'];edges=list(inc.edges(s,p,'central'))
    rejects('wrong-initial',lambda:audit.initial(replace(s,free=(9,0)),'central'))
    rejects('missing-edge',lambda:audit.enabled(s,p,[a for a,_ in edges if not a.startswith('reserve0=')]))
    rejects('changed-status',lambda:audit.edge(s,'status=ok',replace(s,reader_pin=True),p,'central'))
    noop=replace(s,done=1<<p['actions'].index('reserve0'))
    rejects('admission-present-but-no-op',lambda:audit.edge(s,'reserve0=admitted',noop,p,'central'))
    rejects('truncated-frontier',lambda:explore('free-admission','central','inclusive',limit=1))
    return result
