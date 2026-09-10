"""Source-aware adapter B, separated ledger/core updates and split Q reducer."""
import copy
import a_domain as d
import guard_b
import q_split as q_impl

def step(state,action,profile,unit,outcome):
    ledger,response,invoke=guard_b.plan(d.view(state),action,profile)
    core=copy.deepcopy(state['core']);calls=state['invocations'];verb=action.partition('@')[0]
    generation=state['journal']['source_generation']
    if invoke:
        core=d.q.flatten(q_impl.step(d.q.split(core),action,d.subprofile(profile),unit,outcome));calls=(*calls,action)
        response=core['decision']
        if verb=='source-attest' and response!='source-attest:ok':ledger['attestation']=state['journal']['attestation']
        if verb=='source-restart':generation=(*generation[:-1],generation[-1]+1)
        if verb=='stage' or verb.startswith('stage-'):ledger['staged_source']=state['journal']['attestation']
        if core['publication_revision']!=state['core']['publication_revision']:ledger['selected_source']=state['journal']['staged_source']
    ledger['source_generation']=generation
    return dict(core=core,journal=ledger,done=state['done']|2**profile['actions'].index(action),decision=response,invocations=calls)
