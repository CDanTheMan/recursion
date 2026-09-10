"""Finite source-aware adapter comparison under the enclosing owned runner."""
import argparse,json,sys
from pathlib import Path
import adapter_traces as t
import q_artifact as codec
p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('--packet',choices=('A','C'),default='C');args=p.parse_args()
doc=t.d.ROOT/'docs/v3/construction/cut-source-overnight-20260908/batch-06'
contract=json.loads((doc/'contract.json').read_text())
t.d.require(contract['canonical_source_environments']==104 and contract['hidden_actions']==[] and contract['state_visit_reservation_per_invocation']==10000
    and contract['attestation_commit']=='only on actual Q acceptance' and contract['full_gate_commands']==49 and not contract['changed_original_models'],'fixed adapter scope')
manifest=json.loads((doc/'manifest.json').read_text());registered={x['path'] for x in manifest['inputs']}|set(manifest['sources'])
def modules():
    paths=set()
    for mod in tuple(sys.modules.values()):
        f=getattr(mod,'__file__',None)
        if f:
            path=Path(f).resolve()
            if path.is_relative_to(t.d.ROOT) and path.suffix=='.py':paths.add(path.relative_to(t.d.ROOT).as_posix())
    t.d.require(paths<=registered,'loaded local module manifest closure: '+repr(sorted(paths-registered)));return paths
before=modules();result=t.run(args.packet);result['registered_local_modules']=sorted(before|modules())
args.output.mkdir(parents=True,exist_ok=False)
(args.output/'result.json').write_text(json.dumps(codec.pack(result),sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
print(json.dumps(dict(status='BATCH06_CHECK_PASS',packet=args.packet,cases=len(result['cases']),complete_selected_trace_cases=result['complete_selected_trace_cases'],controls=len(result['controls']),state_visits_per_representation=result['state_visits_per_representation'],complete_visible_refinement_proved=False)))
