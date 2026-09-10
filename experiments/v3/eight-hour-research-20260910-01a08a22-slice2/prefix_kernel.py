"""Literal-prefix exploration kernel shared by independently validated finite wrappers."""
import copy
import hashlib
import json
from baseline import check as c
from baseline import ROOT, OLD_CODE, NEW_CODE, NEW_DOC, packet_doc, reference_script, added_module_paths

def fingerprint(value):
    return hashlib.sha256(json.dumps(c.codec.pack(c.artifact.encode(value)),sort_keys=True,separators=(',',':')).encode()).hexdigest()

def traverse(spec,profile,schedules,global_indices,limit,consume):
    c.d.require(len(global_indices)==len(schedules) and len(set(global_indices))==len(global_indices),'one original global identity per selected schedule')
    c.d.require(len(set(schedules))==len(schedules) and all(len(x)==len(profile['actions']) and set(x)==set(profile['actions']) for x in schedules),'unique complete equal-length original schedules')
    c.d.require(all(type(i) is int and 0<=i<spec['schedules_per_unit_outcome'] for i in global_indices),'bounded original global schedule indices')
    counter,seen=c.Counter(limit),set()
    profile_hash=fingerprint(profile)
    trie={}
    for schedule in schedules:
        node=trie
        for action in schedule:node=node.setdefault(action,{})
    positions={s:i for i,s in enumerate(schedules)}
    def record(unit,outcome,prefix):
        key=(unit,outcome,prefix)
        c.d.require(key not in seen,'each literal prefix executed once per fixed environment')
        counter.take(2);seen.add(key)
    for unit_index,unit in enumerate(spec['units']):
        for outcome_index,outcome in enumerate(spec['outcomes']):
            record(unit,outcome,())
            initial_source,initial_adapter=c.d.s.initial(unit),c.d.initial(unit)
            c.t.sc.initialization(initial_source,unit);c.t.audit.initialization(initial_adapter,unit)
            def walk(node,prefix,source,adapter,pairs,source_events,adapter_events,rows):
                parent=(source,adapter,pairs,source_events,adapter_events,rows)
                before=fingerprint(parent)
                if not node:
                    index=positions[prefix]
                    ordinal=(index*len(spec['units'])+unit_index)*len(spec['outcomes'])+outcome_index
                    name=spec['id']+'/'+str(global_indices[index]).zfill(6)+'/'+unit+'/'+str(outcome)
                    st=dict(side='source',initial=copy.deepcopy(initial_source),profile=copy.deepcopy(profile),actions=prefix,events=copy.deepcopy(list(source_events)))
                    at=dict(side='adapter',initial=copy.deepcopy(initial_adapter),profile=copy.deepcopy(profile),q_profile=c.d.subprofile(profile),actions=prefix,events=copy.deepcopy(list(adapter_events)))
                    case=dict(case=name,unit=unit,outcome=outcome,source=st,adapter=at,rows=copy.deepcopy(list(rows)),incarnation_pairs=copy.deepcopy(pairs))
                    case['prefixes']=c.audit_case(case)
                    consume(ordinal,case)
                    c.d.require(fingerprint(profile)==profile_hash,'immutable declared profile after leaf consumer')
                for action,child in sorted(node.items()):
                    child_prefix=prefix+(action,);record(unit,outcome,child_prefix);index=len(prefix)
                    c.d.require(set(c.d.s.ready_actions(source,profile))==c.t.sc.enabled(source,profile) and action in c.t.sc.enabled(source,profile),'complete original enabledness')
                    ns=c.t.sa.step(source,action,profile,unit,outcome)
                    c.d.require(c.d.exact(ns,c.d.s.flatten(c.t.sb.step(c.d.s.split(source),action,profile,unit,outcome))),'unchanged S implementations agree')
                    c.t.sc.check(source,action,ns,profile,unit,outcome)
                    na=c.t.aa.step(adapter,action,profile,unit,outcome)
                    c.d.require(c.d.exact(na,c.t.ab.step(adapter,action,profile,unit,outcome)),'unchanged adapter implementations agree')
                    call=c.t.audit.check(adapter,action,na,profile,unit,outcome)
                    child_pairs=copy.deepcopy(pairs);oldpairs=copy.deepcopy(child_pairs)
                    binding=c.r.advance(child_pairs,source,c.t.core_view(adapter),ns,c.t.core_view(na),action,action,index,index)
                    row=c.t.comparison(source,adapter,ns,na,oldpairs,child_pairs,action,index,call);row['binding']=binding
                    se=c.t.trace_event(source,ns,action);ae=c.t.trace_event(adapter,na,action,True)
                    walk(child,child_prefix,ns,na,child_pairs,source_events+(copy.deepcopy(se),),adapter_events+(copy.deepcopy(ae),),rows+(copy.deepcopy(row),))
                    c.d.require(fingerprint(parent)==before,'typed ancestor states, ledgers and path records unchanged after each child subtree')
            walk(trie,(),initial_source,initial_adapter,[],(),(),())
    c.d.require(fingerprint(profile)==profile_hash,'immutable profile across complete traversal')
    return counter,seen,record
