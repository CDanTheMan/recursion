"""Adapter-owned state and fixed call encodings; no source transition oracle."""
import copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel
s,q=rel.s,rel.q
require,exact,digest=rel.require,rel.exact,rel.digest
PUB=('pub-commit','pub-rival','pub-retry','pub-retry-conflict','pub-retry-foreign')

def source_only(action):
    k=action.split('@')[0]
    return k.startswith(('register:','attempt:','atomic:','append:','collect:','source:')) or k in ('append-lose-reply','collect-open')

def subprofile(profile):
    p=copy.deepcopy(profile)
    p['actions']=tuple(a for a in profile['actions'] if not source_only(a))
    p['requires']={a:() for a in p['actions']}
    return p

def initial(unit):
    return {'core':q.initial(unit),'journal':dict(copy.deepcopy(s.DEFAULTS),source_generation=q.source_token(0)),
            'done':0,'decision':'initial','invocations':()}

def view(state):
    # Read-only guard input: own journal shadows Q's distinct source incarnation.
    return dict(state['core'],**state['journal'],done=state['done'],decision=state['decision'])

def order(profile):
    result=[]
    while len(result)<len(profile['actions']):
        ready=sorted(a for a in profile['actions'] if a not in result and set(profile['requires'][a])<=set(result))
        require(ready,'acyclic source schedule');result.append(ready[0])
    return tuple(result)

def justification(action,delegated):
    k=action.split('@')[0]
    if source_only(action):return 'Same literal call, parameters and visible reply handled by the initialized adapter source ledger; Q state is unchanged.'
    if not delegated:return 'Same literal call refused by the adapter source guard; refusal remains visible and Q state is unchanged.'
    if k=='source-attest':return 'Current complete ledger capture permits the same literal Q attestation; retain actual Q response and commit journal attestation only on Q acceptance.'
    return 'Same literal Q call and parameters after the declared adapter guard; unchanged Q reducer supplies the actual outcome.'
