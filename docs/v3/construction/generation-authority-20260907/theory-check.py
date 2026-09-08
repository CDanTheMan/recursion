"""Closed abstract traces challenge shortcuts; no upstream runtime implementation."""
import hashlib,itertools,json,time

def require(ok,why):
    if not ok:raise ValueError(why)
def schedules(names,orders):
    return [list(p) for p in itertools.permutations(names) if all(p.index(a)<p.index(b) for a,b in orders)]

def simulate(family,guard,trace,params):
    bad=[];positive=0;log=[]
    s=dict(current_revision=1,plugin=0,decoder=0,advertised=False,promise=None,child_live=False,reserved=False,current_attempt=1,settled=False,segments={},display_total=0,actual_total=0,proposals={},accepted=None,adoption_revision=0,receipt=None,history=[])
    for event in trace:
        observation={}
        if family=='activation-closure':
            if event=='prepare':s.update(plugin=params['plugin_result'],decoder=1)
            elif event=='advertise':s['advertised']=True
            else:
                admit=s['advertised'] and (not guard or (s['plugin'],s['decoder'])==(1,1));observation['admitted']=admit
                if admit:
                    if (s['plugin'],s['decoder'])!=(1,1):bad.append('admitted mixed or unprepared dependency closure')
                    else:positive+=1
        elif family=='revision-bound-decision':
            if event=='resolve_r1':s['promise']=dict(decision='approve',revision=1)
            elif event=='amend_r2':s['current_revision']=2
            else:
                adopt=s['promise'] is not None and (not guard or s['promise']['revision']==s['current_revision']);observation['adopted']=adopt
                if adopt:
                    if s['promise']['revision']!=s['current_revision']:bad.append('obsolete durable decision adopted')
                    else:positive+=1
        elif family=='detached-settlement':
            if event=='launch':s.update(child_live=True,reserved=True)
            elif event=='parent_stop':
                if not guard:s['reserved']=False
            else:s.update(child_live=False,reserved=False);positive+=1
            if s['child_live'] and not s['reserved']:bad.append('unsettled detached work lost its reservation')
        elif family=='stale-transport-ack':
            if event=='redeliver':s['current_attempt']=2
            elif event=='ack_old':
                accepted=not guard;observation['transport_ack_accepted']=True;observation['current_attempt_settlement_from_old_ack']=accepted
                if accepted:bad.append('old attempt ACK used as current attempt settlement');s['settled']=True
            else:s['settled']=True;positive+=1
        elif family=='incarnation-accounting':
            incarnation,value=event.split(':');value=int(value);s['segments'][incarnation]=value
            s['actual_total']=sum(s['segments'].values());s['display_total']=s['actual_total'] if guard else value
            if s['display_total']!=s['actual_total']:bad.append('friendly identifier replacement erased prior meter segment')
            else:positive+=1
        elif family=='branch-adoption':
            op,actor=event.split(':')
            if op=='propose':
                s['proposals'][actor]=dict(base=0,value=actor)
                if not guard:s['accepted']=actor;bad.append('branch proposal changed canonical decision without adoption')
            else:
                proposal=s['proposals'][actor];admit=not guard or proposal['base']==s['adoption_revision'];observation['adopted']=admit
                if admit:s.update(accepted=actor,adoption_revision=s['adoption_revision']+1);positive+=1
            observation['preserved_proposals']=sorted(s['proposals'])
        elif family=='memory-freshness':
            # Two-dimensional frontier: one coordinate cannot certify the other.
            current=params['auth_epoch']==2;complete=all(a>=b for a,b in zip(params['frontier'],params['required_cut']));historical=params['result_revision']==params['branch_revision'];allowed=current and complete and historical and params['evidence_allowed']
            admit=allowed if guard else True;observation=dict(admitted=admit,content_hash_equal=True,required_cut=params['required_cut'])
            if admit:
                if not allowed:bad.append('hash hit substituted for branch completeness or current authority')
                else:positive+=1
        elif family=='rejected-command-provenance':
            if event=='receive':
                if guard:s['receipt']=dict(command='c1',principal='owner',expected_revision=0,status='received')
            elif event=='reject':
                if guard:s['receipt']['status']='rejected-stale-revision'
                # A validator rejection creates no accepted workflow history entry.
            else:
                visible=s['receipt'] if guard else next(iter(s['history']),None);observation['query_result']=visible
                if visible is None:bad.append('lost rejection reply has no queryable attributable receipt')
                else:positive+=1
        else:raise ValueError('unknown family')
        log.append(dict(event=event,observation=observation))
    return dict(violations=bad,positive_outcomes=positive,observations=log)

def fixtures():
    out=[]
    def add(family,traces,parameters):
        for p in parameters:
            for t in traces:out.append(dict(family=family,trace=t,parameters=p))
    add('activation-closure',schedules(['prepare','advertise','invoke'],[('advertise','invoke')]),[dict(plugin_result=n) for n in (0,1)])
    add('revision-bound-decision',schedules(['resolve_r1','amend_r2','consume'],[('resolve_r1','consume')]),[{}])
    add('detached-settlement',schedules(['launch','parent_stop','child_settle'],[('launch','parent_stop'),('launch','child_settle')]),[{}])
    add('stale-transport-ack',schedules(['redeliver','ack_old','settle_current'],[('redeliver','ack_old'),('redeliver','settle_current')]),[{}])
    for a,b in itertools.product((1,2),repeat=2):add('incarnation-accounting',[[f'i1:{a}',f'i1:{a}',f'i2:{b}',f'i2:{b}']],[{}])
    add('branch-adoption',schedules(['propose:A','propose:B','adopt:A','adopt:B'],[('propose:A','adopt:A'),('propose:B','adopt:B')]),[{}])
    # Branch A needs both updates; preserved B needs only the first. E0 may be
    # retained historically while being forbidden for present disclosure.
    for branch,epoch,frontier,result,allowed in itertools.product((0,1),(1,2),[(1,0),(0,1),(1,1)],(0,1),(False,True)):
        add('memory-freshness',[['hydrate']],[dict(branch_revision=branch,required_cut=[1,branch],auth_epoch=epoch,frontier=list(frontier),result_revision=result,evidence_allowed=allowed)])
    add('rejected-command-provenance',[['receive','reject','query_after_lost_reply']],[{}])
    return out

def run():
    began=time.monotonic();rows=[]
    for n,f in enumerate(fixtures()):
        require(n<256 and time.monotonic()-began<30,'abstract fixture/time bound')
        rows.append(dict(id=n,**f,shortcut=simulate(f['family'],False,f['trace'],f['parameters']),guarded=simulate(f['family'],True,f['trace'],f['parameters'])))
    families=[]
    for name in sorted({r['family'] for r in rows}):
        group=[r for r in rows if r['family']==name];counter=[r for r in group if r['shortcut']['violations']];good=sum(r['guarded']['positive_outcomes'] for r in group)
        require(counter and good>0 and all(not r['guarded']['violations'] for r in group),'vacuous or violated guarded family '+name)
        families.append(dict(family=name,fixtures=len(group),shortcut_counterexamples=len(counter),guarded_violations=0,guarded_positive_outcomes=good,witness_id=counter[0]['id']))
    return dict(status='bounded-abstract-comparison-pass',classification='modeled',fixture_count=len(rows),families=families,rows=rows,upstream_runtime_executed=False,full_formal_freeze=False,performance_measured=False)

if __name__=='__main__':print(json.dumps(run(),sort_keys=True,indent=2))
