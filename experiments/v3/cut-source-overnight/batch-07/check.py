"""Bounded staged-record identity comparison under the owned Batch07 runner."""
import argparse
import json
import sys
from pathlib import Path
import compare
import q_artifact as codec

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('output', type=Path)
p.add_argument('--packet', choices=('A', 'C'), default='C')
args = p.parse_args()
doc = compare.d.ROOT / 'docs/v3/construction/cut-source-overnight-20260908/batch-07'
contract = json.loads((doc / 'contract.json').read_text())
compare.d.require(contract['canonical_source_environments'] == 104 and contract['additional_environments'] == 2
                  and contract['exception_fields'] == ['staged'] and contract['hidden_actions'] == []
                  and contract['full_gate_commands'] == 50 and contract['state_visit_reservation'] == 10000,
                  'fixed reviewed identity scope')
manifest = json.loads((doc / 'manifest.json').read_text())
registered = {x['path'] for x in manifest['inputs']} | set(manifest['sources'])

def modules():
    paths = set()
    for mod in tuple(sys.modules.values()):
        name = getattr(mod, '__file__', None)
        if name:
            path = Path(name).resolve()
            if path.is_relative_to(compare.d.ROOT) and path.suffix == '.py':
                paths.add(path.relative_to(compare.d.ROOT).as_posix())
    compare.d.require(paths <= registered, 'loaded local module manifest closure: ' + repr(sorted(paths - registered)))
    return paths

before = modules()
result = compare.run(args.packet)
result['registered_local_modules'] = sorted(before | modules())
args.output.mkdir(parents=True, exist_ok=False)
(args.output / 'result.json').write_text(json.dumps(codec.pack(result), sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')
print(json.dumps({key: result[key] for key in ('packet', 'canonical_cases', 'canonical_strict_complete', 'canonical_extended_complete', 'additional_cases', 'additional_extended_complete', 'state_visits_per_representation')} | {'status': 'BATCH07_CHECK_PASS', 'controls': len(result['controls'])}))
