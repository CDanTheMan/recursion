"""Owned Batch03 static-contract and finite local-mapping acceptance."""
import argparse
import json
from pathlib import Path
import contracts
import mapping


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    ledger = contracts.read(contracts.DOC / 'contracts.json')
    a = contracts.validate(ledger)
    a['controls'] = contracts.controls(ledger)
    b = mapping.run()
    result = {'status': 'BATCH03_CONTRACT_AND_LOCAL_MAPPING_PASS_WITH_GAPS', 'A': a, 'B': b,
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
