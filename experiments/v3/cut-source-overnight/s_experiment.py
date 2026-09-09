"""Exact finite comparison; no model network, subprocess or provider operations."""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path
import sys
import time

def deny_network(event, args):
    if event.startswith(('socket.', 'subprocess.', 'os.system', 'os.exec', 'os.spawn')):
        raise RuntimeError('model network/process operation forbidden: '+event)

import s_domain as d
import s_inclusive as inc
import s_split as split
import s_audit as audit
import q_artifact as artifact
import q_experiment as prior

START = time.monotonic()
MUTANTS = {'append-owner':'append-foreign','append-conflict':'equal-position-fork',
           'append-incarnation':'append-fresh-old-boot','append-pause':'pause-append',
           'append-position':'append-gap','append-attempt':'unregistered-append',
           'append-scope':'append-wrong-body','capture-current':'new-attempt-during-collection',
           'complete-collection':'omitted-record','complete-registry':'pending-attempt-before-collect',
           'publication-source-current':'append-between-collect-and-publish',
           'reconcile-source-current':'pending-after-selected'}

def limits(states):
    d.require(states<=500000,'incomplete frontier: states')
    d.require(time.monotonic()-START<600,'incomplete frontier: seconds')
    d.require(prior.peak()<=2147483648,'incomplete frontier: memory')

def positive(name, states, decisions):
    s=states[-1]
    def saw(reason): return any(value.endswith(':'+reason) for value in decisions)
    if name in ('pending-success','atomic-start-success'):
        d.require(s['consumed']==(6,0) and s['reserved']==(0,0), 'positive successful source consumes A6')
    if name in ('pending-failure','atomic-start-failure','quota-worker-independent'):
        d.require(s['reserved']==(0,6) and s['consumed']==(0,0), 'positive nonexecution reconciliation admits B6')
    if name in ('pending-later-start-only','atomic-start-later-start-only','pending-ambiguous','atomic-start-ambiguous','pending-after-selected','append-after-selected'):
        d.require(s['reserved']==(6,0), 'pending or stale source retains A6')
    expectations={'omitted-record':'incomplete-inventory','omitted-tail-current-head':'incomplete-inventory',
        'pending-attempt-before-collect':'incomplete-registry','new-attempt-during-collection':'stale-collection',
        'append-between-collect-and-publish':'source-boundary-stale','pending-after-selected':'source-boundary-stale',
        'append-after-selected':'source-boundary-stale','equal-position-fork':'append-id-conflict',
        'foreign-registration':'foreign-registration','append-foreign':'wrong-append-owner',
        'append-wrong-attempt':'unregistered-attempt','append-wrong-body':'foreign-record-scope',
        'unregistered-append':'unregistered-attempt','append-gap':'append-gap-or-fork',
        'append-fresh-old-boot':'stale-append-incarnation','collection-old-incarnation':'source-boundary-stale',
        'source-oracle-bypass':'registered-protocol-required','pause-append':'E-PAUSED','pause-publication':'E-PAUSED',
        'copy-not-wait':'reader-live','publication-duplicate-retired':'E-IDEMPOTENCY-CONFLICT'}
    if name in expectations: d.require(saw(expectations[name]), 'reachable positive guard '+name)
    if name in ('reverse-collection','delayed-record','restart-recollect'): d.require(s['publication_revision']==1, 'complete source recovery '+name)
    if name=='same-version-real-append': d.require(s['publication_revision']==2 and len(s['append_log'])==4 and s['reserved']==(6,0), 'same-version append advances genuine source')
    if name=='append-duplicate-lost-reply': d.require(len(s['append_log'])==3 and s['source_revision']==5 and s['append_reply']==s['append_receipts'][-1][2], 'retained exact duplicate after restart')
    if name=='four-event':
        import base64
        actual=[json.loads(m) for m in s['wire'] if json.loads(m)['type']=='EVENT']
        d.require(s['delivered']==(1,2,3,4) and s['loss']==0 and [len(base64.b64decode(m['payload_base64'])) for m in actual]==[1,2,1,2], 'full original four-event flow')
    return sorted(set(value.rsplit(':',1)[-1] for value in decisions))

def explore(name,unit,outcome,state_limit=500000):
    profile=d.PROFILES[name]; start=d.initial(unit); audit.initialization(start,unit)
    queue=collections.deque([(start,())]); seen={d.canonical(start)}; edges=0; terminals=0; sample=None; digest=hashlib.sha256(); histories={}
    while queue:
        s,path=queue.popleft(); enabled=set(d.ready_actions(s,profile))
        d.require(enabled==audit.enabled(s,profile), 'complete enabled set')
        if s['wire'] not in histories:
            result=d.q.evaluate(s['wire']); d.require(set(result['reasons'])<={'replay-gap'},'literal inherited wire')
            histories[s['wire']]=result
        if not enabled:
            terminals+=1
            if sample is None: sample=path
        for action in sorted(enabled):
            n=inc.step(s,action,profile,unit,outcome)
            other=d.flatten(split.step(d.split(s),action,profile,unit,outcome))
            d.require(n==other,'independent representations differ '+action)
            audit.check(s,action,n,profile,unit,outcome)
            digest.update(d.canonical((s,action,n)).encode()); edges+=1; identity=d.canonical(n)
            if identity not in seen:
                seen.add(identity); queue.append((n,path+(action,)))
                d.require(len(seen)<=state_limit,'incomplete frontier: explicit state limit')
        if edges%128==0: limits(len(seen))
    d.require(sample is not None,'finite terminal')
    s=start; trace=[]; states=[s]; decisions=[]
    for action in sample:
        n=inc.step(s,action,profile,unit,outcome); audit.check(s,action,n,profile,unit,outcome)
        trace.append({'action':action,'before':s,'after':n}); states.append(n); decisions.append(n['decision']); s=n
    triggers=positive(name,states,decisions)
    return {'states':len(seen),'edges':edges,'terminal_states':terminals,'frontier':0,'graph_sha256':digest.hexdigest(),
            'exact_graph_equal':True,'guard_decisions':triggers,'trace':trace,'final':s,
            'wire_histories':[{'wire':[json.loads(x) for x in key],'decision':value} for key,value in sorted(histories.items())]}

def mutant(guard,unit):
    name=MUTANTS[guard]; p=d.PROFILES[name]; outcome=p['outcomes'][-1]; s=d.initial(unit); trace=[]
    for action in p['actions']:
        n=inc.step(s,action,p,unit,outcome,guard); correct=inc.step(s,action,p,unit,outcome)
        trace.append({'action':action,'before':s,'after':n})
        if n!=correct:
            try: audit.check(s,action,n,p,unit,outcome)
            except ValueError as error:
                return {'guard':guard,'unit':unit,'profile':name,'rejected':True,'reason':str(error),'crossing_action':action,'trace':trace,'correct':correct}
            raise ValueError('independent relation accepted removed guard '+guard)
        s=n
    raise ValueError('vacuous mutant '+guard)

def calibrations():
    rows=[]
    for case in ('initial','no-op','missing-edge','truncated'):
        try:
            p=d.PROFILES['pending-success']; s=d.initial('event'); action=p['actions'][0]
            if case=='initial': s['source_revision']=1; audit.initialization(s,'event')
            elif case=='no-op': audit.check(s,action,s,p,'event',1)
            elif case=='missing-edge': d.require(audit.enabled(s,p)==set(),'missing edge')
            else: explore('pending-success','event',1,1)
        except ValueError as error: rows.append({'case':case,'rejected':True,'reason':str(error)})
        else: raise ValueError('checker calibration did not reject '+case)
    return rows

def run(queue_item):
    profiles={}
    for name,p in d.PROFILES.items():
        if queue_item!='all' and p['queue']!=queue_item: continue
        for unit in d.UNITS:
            for outcome in p['outcomes']:
                key=name+'/'+unit+'/'+str(outcome); profiles[key]=explore(name,unit,outcome)
                print(key,profiles[key]['states'],profiles[key]['edges'],flush=True)
    total=sum(x['states'] for x in profiles.values()); limits(total)
    return {'status':'cut-source-pass','queue_item':queue_item,'profiles':profiles,'states_per_representation':total,
            'edges_per_representation':sum(x['edges'] for x in profiles.values()),'frontier':0,
            'mutants':[mutant(g,u) for g in MUTANTS if queue_item=='all' or d.PROFILES[MUTANTS[g]]['queue']==queue_item for u in d.UNITS],
            'calibrations':calibrations(),'classification':'modeled','formal_freeze':False,
            'full_comparison_complete':False,'runtime_integration_support':False,'network_operations':0}

if __name__=='__main__':
    sys.addaudithook(deny_network)
    parser=argparse.ArgumentParser(); parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--queue-item',choices=('source_authority','coupled_adversarial','bounded_scaling','all'),required=True)
    args=parser.parse_args(); begin=datetime.datetime.now(datetime.timezone.utc)
    result=run(args.queue_item)
    args.output.write_text(json.dumps({'started_at':begin.isoformat(),'finished_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'seconds':time.monotonic()-START,'peak_bytes':prior.peak(),'result':artifact.pack(result)},sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    print('CUT_SOURCE_EXPERIMENT_PASS',flush=True)
