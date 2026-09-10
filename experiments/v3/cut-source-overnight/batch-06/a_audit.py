"""Independent direct-byte journal postcondition and unchanged Q audit."""
import a_domain as d
import guard_audit
import q_audit as qa

def initialization(state,unit):
    qa.initialization(state['core'],unit)
    expected=dict(registration='',attempts=(),append_log=(),append_receipts=(),append_reply=(),source_revision=0,
        collection=(),collected=(),attestation=(),staged_source=(),selected_source=(),source_generation=('cut-source','collectorA','effectA',0))
    d.require(d.exact(state['journal'],expected) and state['done']==0 and state['decision']=='initial' and state['invocations']==(),'complete adapter initialization')

def check(before,action,after,profile,unit,outcome):
    d.require(action in d.s.ready_actions({'done':before['done']},profile),'outer adapter enabledness')
    # Independently construct the guard view and frozen potential-call profile.
    own={**before['core'],**before['journal'],'done':before['done'],'decision':before['decision']}
    ledger,reason,call=guard_audit.expected(own,action,profile)
    potential=tuple(a for a in profile['actions'] if not (a.split('@')[0].startswith(('register:','attempt:','atomic:','append:','collect:','source:')) or a.split('@')[0] in ('append-lose-reply','collect-open')))
    qp={**profile,'actions':potential,'requires':{a:() for a in potential}}
    d.require(d.exact(qp,d.subprofile(profile)),'fixed independent Q invocation profile')
    k=action.partition('@')[0];generation=before['journal']['source_generation'];calls=before['invocations']
    if call:
        d.require(action in qa.enabled(before['core'],qp),'actual Q call enabled')
        qa.check(before['core'],action,after['core'],qp,unit,outcome)
        calls=(*calls,action);reason=after['core']['decision']
        if k=='source-attest' and reason!='source-attest:ok':ledger['attestation']=before['journal']['attestation']
        if k=='source-restart':generation=('cut-source','collectorA','effectA',generation[-1]+1)
        if k=='stage' or k.startswith('stage-'):ledger['staged_source']=before['journal']['attestation']
        if after['core']['publication_revision']>before['core']['publication_revision']:ledger['selected_source']=before['journal']['staged_source']
    else:d.require(d.exact(before['core'],after['core']),'source-handled or refused call leaves entire Q core unchanged')
    ledger['source_generation']=generation
    d.require(d.exact(after['journal'],ledger),'complete independent adapter ledger postcondition '+k)
    d.require(after['decision']==reason and d.exact(after['invocations'],calls),'actual Q response and invocation inventory')
    d.require(after['done']==before['done']|(1<<profile['actions'].index(action)),'separate adapter completion')
    d.require(after['core']['done']==sum(1<<potential.index(a) for a in calls),'Q completion exactly actual invocations')
    d.require(set(after)=={'core','journal','done','decision','invocations'},'complete adapter frame')
    qa.invariant(after['core'])
    return call
