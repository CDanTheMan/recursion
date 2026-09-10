"""Bounded semantic comparison and retained checker controls; no runtime integration."""
import argparse,json,sys
from pathlib import Path
import traces
import q_artifact as codec

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('output',type=Path)
parser.add_argument('--packet',choices=('A','C'),default='C')
args=parser.parse_args()
contract=json.loads((traces.rel.ROOT/'docs/v3/construction/cut-source-overnight-20260908/batch-05/contract.json').read_text(encoding='utf-8'))
traces.require(contract['envelope_exceptions']==['source_generation','signature'] and contract['state_excludes']==['done','decision']
    and contract['hidden_actions']==[] and not contract['graph_search'] and not contract['changed_original_models']
    and not contract['resign_or_rewrite_original_objects'] and contract['state_visit_reservation_per_invocation']==traces.MAX_VISITS
    and contract['action_translation']=='identity of complete literal shared operation and parameters'
    and contract['source_only_disposition']=='unmatched-visible-source-event'
    and contract['decision_retained_as_transition_observation'] and contract['visible_publication_reply_retained']
    and contract['visible_append_reply_retained'],'fixed owner-approved semantic and visible-outcome contract')
args.output.mkdir(parents=True,exist_ok=False)
manifest=json.loads((traces.rel.ROOT/'docs/v3/construction/cut-source-overnight-20260908/batch-05/manifest.json').read_text(encoding='utf-8'))
registered={row['path'] for row in manifest['inputs']}|set(manifest['sources'])
def local_modules():
    loaded=set()
    for module in tuple(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            p=Path(filename).resolve()
            if p.is_relative_to(traces.rel.ROOT) and p.suffix=='.py':loaded.add(p.relative_to(traces.rel.ROOT).as_posix())
    traces.require(loaded<=registered,'loaded local module manifest closure: '+repr(sorted(loaded-registered)))
    return loaded
before_modules=local_modules()
raw=traces.run(args.packet)
raw['registered_local_modules']=sorted(before_modules|local_modules())
result=codec.pack(raw)
(args.output/'result.json').write_text(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
plain=codec.unpack(result)
print(json.dumps({'status':'BATCH05_CHECK_PASS','packet':args.packet,'cases':len(plain['cases']),'controls':len(plain['controls']),
    'state_visits_per_representation':plain['state_visits_per_representation'],
    'all_paired_related_cases':sum(c['all_paired_transitions_related'] for c in plain['cases']),
    'complete_visible_refinement_proved':False}))
