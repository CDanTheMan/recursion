"""Static fidelity checks; these do not prove source truth or the proposed contracts."""
import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOC = ROOT / 'docs/v3/construction/cut-source-overnight-20260908/batch-03'
IDS = ('SRC-IDENTITY', 'APPEND-IDENTITY-POSITION', 'APPEND-RECEIPT',
       'REGISTRATION-ADMISSION', 'CAPTURE-COVERAGE', 'ATTESTATION-CORRESPONDENCE',
       'PUBLICATION-SELECTION', 'READ-AND-USE', 'CLASSIFICATION-NONINTERFERENCE')


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(value):
    return hashlib.sha256(value).hexdigest()


def pointer(value, path):
    for key in path.strip('/').split('/'):
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def validate(ledger):
    require([r['id'] for r in ledger['rows']] == list(IDS), 'nine exact contract rows')
    questions = [q for q in read(ROOT / ledger['original_question_source'])['questions'] if q['id'].startswith('Q')]
    require(ledger['original_questions'] == questions and len(questions) == 6, 'unchanged original question objects')
    require(all(q['status'] == 'deferred-safeguard' and not q['evidence'] for q in questions), 'deferred question evidence unchanged')
    coverage = read(ROOT / ledger['original_coverage_source'])
    require(ledger['original_obligations'] == coverage['slice_obligations'] and len(ledger['original_obligations']) == 6, 'six unchanged coverage obligations')
    require(ledger['original_trace_rows'] == coverage['slice_traces'] and len(ledger['original_trace_rows']) == 27, '27 unchanged coverage rows')
    require(not ledger['source_truth_established'] and not ledger['full_comparison_complete'] and ledger['deferred_questions_resolved'] == [], 'claim boundary')
    require(ledger['question_links_are_proposed_responsibility_links'] is True, 'responsibility links are not original graph edges')
    manifest = read(DOC / 'manifest.json')
    inputs = {r['path']: r['git_blob_sha256'] for r in manifest['inputs']}
    anchors = 0
    for row in ledger['rows']:
        require(row['classification'] == 'proposed-correspondence-obligation' and row['proof_status'] == 'not-established', 'no contract proof promotion')
        require(row['existing_condition']['classification'] == 'implemented-finite-model-condition', 'code condition separate from sufficiency')
        require(row['required_correspondence'] and row['existing_condition']['description'] and row['external_assumptions'], 'explicit condition and external premises')
        require(not row['new_execution'] and not row['changes_existing_encoding'], 'static ledger only')
        require(set(row['proposed_question_links']) <= {q['id'] for q in questions}, 'declared responsibility links')
        for ref in row['source_refs']:
            path = (ROOT / ref['path']).resolve()
            require(path.is_relative_to(ROOT), 'source containment')
            raw = path.read_bytes().replace(b'\r\n', b'\n')
            require(sha(raw) == ref['git_blob_sha256'] == inputs[ref['path']], 'registered source hash')
            source = raw.decode('utf-8')
            node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == ref['function'])
            snippet = '\n'.join(source.splitlines()[node.lineno - 1:node.end_lineno])
            require(node.lineno == ref['line'] and sha(snippet.encode()) == ref['function_sha256'], 'exact function anchor')
            anchors += 1
        for ref in row['existing_evidence_refs']:
            value = pointer(read(ROOT / ref['path']), ref['pointer'])
            require(ref['path'] in inputs and value['id'] == ref['expected_id'] and value['status'] == ref['expected_status'], 'existing partial evidence pointer')
            require(value['status'] == 'partial-modeled-support' and value['residual'], 'preserved evidence residual')
    return {'status': 'STATIC_LEDGER_FIDELITY_PASS', 'rows': len(IDS), 'function_anchors': anchors,
            'obligations': 6, 'trace_rows': 27, 'questions': 6, 'contract_sufficiency_proved': False}


def controls(ledger):
    trials = []
    bad = copy.deepcopy(ledger); bad['rows'][0]['source_refs'][0]['function_sha256'] = '0' * 64
    trials.append(('misbound-function', bad))
    bad = copy.deepcopy(ledger); bad['original_questions'][0]['status'] = 'resolved'
    trials.append(('promoted-question', bad))
    bad = copy.deepcopy(ledger); bad['original_trace_rows'].pop()
    trials.append(('missing-original-row', bad))
    result = []
    for label, bad in trials:
        try:
            validate(bad)
        except ValueError as error:
            result.append({'control': label, 'detected': True, 'reason': str(error)})
        else:
            raise ValueError('undetected ledger control ' + label)
    return result
