"""Owned Batch03 static-contract and finite local-mapping acceptance."""
import argparse
import json
from pathlib import Path
import sys
import contracts
import mapping


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    manifest = contracts.read(contracts.DOC / 'manifest.json')
    registered = {r['path'] for r in manifest['inputs']} | set(manifest['sources'])
    local_modules = set()
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename:
            path = Path(filename).resolve()
            if path.is_relative_to(contracts.ROOT) and path.suffix == '.py':
                local_modules.add(path.relative_to(contracts.ROOT).as_posix())
    contracts.require(local_modules <= registered, 'complete loaded module closure: ' + repr(sorted(local_modules - registered)))
    ledger = contracts.read(contracts.DOC / 'contracts.json')
    a = contracts.validate(ledger)
    a['controls'] = contracts.controls(ledger)
    b = mapping.run()
    result = {'status': 'BATCH03_CONTRACT_AND_LOCAL_MAPPING_PASS_WITH_GAPS', 'registered_local_modules': sorted(local_modules), 'A': a, 'B': b,
              'full_comparison_complete': False, 'runtime_selection': None, 'deferred_questions_resolved': []}
    packed = mapping.codec.pack(result)
    accepted = contracts.DOC / 'results.json'
    if accepted.exists():
        contracts.require(packed == contracts.read(accepted), 'exact accepted Batch03 result reproduction')
    (output / 'result.json').write_text(json.dumps(packed, sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'states': b['states_per_representation'],
                      'edges': b['edges_per_representation'], 'mapping': b['classification_counts']}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--packet', choices=('C',), required=True)
    args = parser.parse_args()
    main(args.output)
