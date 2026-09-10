"""Source-aware adapter A. Q core is mutated only by unchanged Q calls."""
import copy
import a_domain as d
import guard_a
import q_inclusive as q_impl

def step(state,action,profile,unit,outcome):
    n=copy.deepcopy(state);k=action.split('@')[0]
    journal,decision,call=guard_a.plan(d.view(state),action,profile)
    journal['source_generation']=state['journal']['source_generation']
    if call:
        n['core']=q_impl.step(state['core'],action,d.subprofile(profile),unit,outcome)
        n['invocations']=state['invocations']+(action,)
        decision=n['core']['decision']
        if k=='source-attest' and decision!='source-attest:ok':journal['attestation']=state['journal']['attestation']
        if k=='source-restart':journal['source_generation']=d.q.source_token(journal['source_generation'][-1]+1)
        if k=='stage' or k.startswith('stage-'):journal['staged_source']=state['journal']['attestation']
        if n['core']['publication_revision']>state['core']['publication_revision']:journal['selected_source']=state['journal']['staged_source']
    n.update(journal=journal,decision=decision,done=state['done']|(1<<profile['actions'].index(action)))
    return n
