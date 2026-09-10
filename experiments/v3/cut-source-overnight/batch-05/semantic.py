"""Relations over actual original objects; never re-sign, rewrite, or execute a model."""
import hashlib
import hmac
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/v3/cut-source-overnight'))
import s_domain as s
import q_audit as qa
q=s.q
FIELDS=tuple(k for k in q.AUTH+q.FLOW+q.VIEW if k not in ('done','decision'))

def typed(x):
    if isinstance(x,dict):return ['dict',[[k,typed(v)] for k,v in sorted(x.items())]]
    if isinstance(x,(list,tuple)):return [type(x).__name__,[typed(v) for v in x]]
    return [type(x).__name__,x]

def exact(a,b):return typed(a)==typed(b)
def digest(x):return hashlib.sha256(q.canonical(x).encode()).hexdigest()
def require(ok,message):
    if not ok:raise ValueError(message)

def token(x):
    return type(x) is tuple and len(x)==4 and x[:3]==('cut-source','collectorA','effectA') and type(x[3]) is int and x[3]>=0

def signed(env):
    if type(env) is not q.Envelope or not token(env.source_generation):return False
    try:qa.checked_payload(env,q.raw_cut(env.cut))
    except (ValueError,KeyError,TypeError,IndexError):return False
    body=json.dumps(tuple(env)[:-1],sort_keys=True,separators=(',',':')).encode()
    return hmac.compare_digest(env.signature,hmac.new(q.TEST_KEY,body,hashlib.sha256).hexdigest())

def generation_pair(a,b,pairs):
    return token(a) and token(b) and any(exact(a,row['source']) and exact(b,row['target']) for row in pairs)

def bind(pairs,a,b,reason,source_event,target_event):
    require(token(a) and token(b),'typed scoped incarnation pair')
    existing=[row for row in pairs if exact(row['source'],a) or exact(row['target'],b)]
    if existing:return 'already-bound' if len(existing)==1 and generation_pair(a,b,existing) else 'binding-conflict'
    pairs.append({'source':a,'target':b,'reason':reason,'source_event':source_event,'target_event':target_event})
    return 'new-binding'

def advance(pairs,s_before,q_before,s_after,q_after,s_action,q_action,si,qi):
    sv,qv=s_action.split('@')[0],q_action.split('@')[0]
    require(sv==qv,'identity action translation only')
    if sv=='source-attest' and s_after['decision']==q_after['decision']=='source-attest:ok':
        if not exact(s_before['cut_delivery'],q_before['cut_delivery']):return 'different-attestation-input'
        return bind(pairs,s_after['source_generation'],q_after['source_generation'],'paired-successful-attestation',si,qi)
    if sv=='source-restart' and generation_pair(s_before['source_generation'],q_before['source_generation'],pairs):
        require(s_after['source_generation'][-1]==s_before['source_generation'][-1]+1 and q_after['source_generation'][-1]==q_before['source_generation'][-1]+1,'original paired restart advances')
        return bind(pairs,s_after['source_generation'],q_after['source_generation'],'paired-restart',si,qi)
    return 'unchanged'

def own_receipt(env,receipt):
    return signed(env) and type(receipt) is tuple and len(receipt)==5 and exact(receipt,(env.request,digest(env),env.expected_revision+1,env.generation,env.content))

def pair_envelope(a,b,pairs):
    return signed(a) and signed(b) and generation_pair(a.source_generation,b.source_generation,pairs) and all(exact(getattr(a,k),getattr(b,k)) for k in q.Envelope._fields if k not in ('source_generation','signature'))

def pair_receipt(ea,ra,eb,rb,pairs):
    return pair_envelope(ea,eb,pairs) and own_receipt(ea,ra) and own_receipt(eb,rb) and all(exact(ra[i],rb[i]) for i in (0,2,3,4))

def envelope_view(env,side,pairs):
    indices=[i for i,row in enumerate(pairs) if exact(row[side],env.source_generation)]
    if not signed(env) or len(indices)!=1:return ['unrelated-envelope',side,typed(env)]
    return ['Envelope',[[k,['incarnation-pair',indices[0]] if k=='source_generation' else ['own-body-hmac-valid'] if k=='signature' else typed(getattr(env,k))] for k in q.Envelope._fields]]

def nested_view(x,side,pairs):
    if type(x) is q.Envelope:return envelope_view(x,side,pairs)
    if isinstance(x,dict):return ['dict',[[k,nested_view(v,side,pairs)] for k,v in sorted(x.items())]]
    if isinstance(x,(tuple,list)):return [type(x).__name__,[nested_view(v,side,pairs) for v in x]]
    return typed(x)

def receipt_view(env,r,side,pairs):
    if not own_receipt(env,r):return ['invalid-own-receipt',side,typed(r)]
    return ['receipt',typed(r[0]),['own-envelope',envelope_view(env,side,pairs)],typed(r[2:])]

def reply_row(state):
    return next(((env,r) for env,r in state['publication_receipts'] if exact(r,state['publication_reply'])),None)

def field_view(state,key,side,pairs):
    x=state[key]
    if key=='source_generation':
        indices=[i for i,row in enumerate(pairs) if exact(row[side],x)]
        if len(indices)==1:return ['live-incarnation-pair',indices[0]]
        if not state['source_name']:return ['pre-attestation',typed(x)]
        return ['unbound-live-incarnation',side,typed(x)]
    if key=='publication_receipts':return ['receipts',type(x).__name__,[[type(row).__name__,envelope_view(row[0],side,pairs),receipt_view(row[0],row[1],side,pairs)] for row in x]]
    if key=='publication_reply' and x:
        row=reply_row(state)
        return receipt_view(*row,side,pairs) if row else ['reply-without-durable-receipt',side,typed(x)]
    return nested_view(x,side,pairs)

def nested_pair(a,b,pairs):
    if type(a) is q.Envelope or type(b) is q.Envelope:return type(a) is type(b) and pair_envelope(a,b,pairs)
    if type(a) is not type(b):return False
    if isinstance(a,dict):return set(a)==set(b) and all(nested_pair(a[k],b[k],pairs) for k in a)
    if isinstance(a,(tuple,list)):return len(a)==len(b) and all(nested_pair(x,y,pairs) for x,y in zip(a,b))
    return exact(a,b)

def field_pair(a,b,key,pairs):
    x,y=a[key],b[key]
    if key=='source_generation':
        return generation_pair(x,y,pairs) or (not a['source_name'] and not b['source_name'] and exact(x,y))
    if key=='publication_receipts':
        return type(x) is type(y) and len(x)==len(y) and all(type(left) is type(right) and pair_receipt(left[0],left[1],right[0],right[1],pairs) for left,right in zip(x,y))
    if key=='publication_reply' and (x or y):
        ar,br=reply_row(a),reply_row(b)
        return bool(ar and br and pair_receipt(ar[0],ar[1],br[0],br[1],pairs))
    return nested_pair(x,y,pairs)

def observation(state,action):
    result={'decision':state['decision']}
    verb=action.split('@')[0]
    if verb.startswith('append:') or verb=='append-lose-reply':result['append_reply']=state['append_reply']
    if verb.startswith('pub-'):result['publication_reply']=state['publication_reply']
    return result

def report(a,b,pairs,s_action,q_action):
    require(set(FIELDS)==set(q.AUTH+q.FLOW+q.VIEW)-{'done','decision'},'complete common field inventory')
    bad=[k for k in FIELDS if field_view(a,k,'source',pairs)!=field_view(b,k,'target',pairs)]
    response=exact(a['decision'],b['decision']) and (not s_action.split('@')[0].startswith('pub-') or field_pair(a,b,'publication_reply',pairs))
    result={'source_sha256':digest(a),'target_sha256':digest(b),'pairs_sha256':digest(pairs),
        'source_action':s_action,'target_action':q_action,'differing_fields':bad,'state_related':not bad,'responses_related':response,
        'source_observation':observation(a,s_action),'target_observation':observation(b,q_action)}
    verify_report(result,a,b,pairs,s_action,q_action)
    return result

def verify_report(row,a,b,pairs,sa,ta):
    require(sa.split('@')[0]==ta.split('@')[0],'literal action and parameters preserved')
    bad=[key for key in FIELDS if not field_pair(a,b,key,pairs)]
    response=exact(a['decision'],b['decision'])
    if sa.split('@')[0].startswith('pub-'):
        ar,br=reply_row(a),reply_row(b)
        response=response and ((not a['publication_reply'] and not b['publication_reply']) or bool(ar and br and pair_receipt(*ar,*br,pairs)))
    expected={'source_sha256':digest(a),'target_sha256':digest(b),'pairs_sha256':digest(pairs),
        'source_action':sa,'target_action':ta,'differing_fields':bad,'state_related':not bad,'responses_related':response,
        'source_observation':observation(a,sa),'target_observation':observation(b,ta)}
    require(exact(row,expected),'independent recursive relation and observation certificate')
