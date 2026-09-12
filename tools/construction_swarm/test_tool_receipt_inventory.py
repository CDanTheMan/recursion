"""Synthetic retained native-v3 evidence bundles for tool_receipt_inventory."""
import json
import unittest

from .contracts import JOB_TOOLS, Refused, digest, encoded, strict_json
from .tool_receipt_inventory import (
    PERMISSION_DIGEST_FIELD,
    TOOL_DIGEST_FIELD,
    _paged_read,
    expected_permission_presentation,
    expected_tool_presentation,
    verify_attempt_inventory,
)

ALLOWED = tuple(name for name in JOB_TOOLS if name != 'fetch_source')
PERMISSION_KNOWN = 'e1d88fc9bc8dd757b568414e88c89225844113102fbfc96fa1355b01792f2c81'
PRESENTATION_KNOWN = '7faf2cb8b55366d50c434571deb1e76b27881b250c3f1330e437032734f2ea4b'
COMMIT = 'f1f803fcc2820afc38df328679c8f3496ed0ef2c'
ROUTE = {'backend': 'devin-tools', 'executable': '/opt/devin/bin/devin',
         'sha256': 'b' * 64, 'model': 'swe-2-max',
         'capacity_basis': 'synthetic test capacity basis'}
SOURCE_CONTENT = 'alpha\nbeta source\n'
NEW_CONTENT = 'line beta\nline alpha\n'
SCRIPT = [
    ('list_files', {}),
    ('read_file', {'path': 'tools/a.txt'}),
    ('write_file', {'path': 'tools/new.txt', 'content': NEW_CONTENT,
                    'expected_sha256': None}),
    ('read_file', {'path': 'tools/new.txt', 'offset': 0, 'limit': 5}),
    ('read_file', {'path': 'tools/new.txt', 'offset': 5, 'limit': 4096}),
    ('search', {'text': 'beta'}),
    ('run_command', {'argv': ['python3', '-c', 'print(1)'], 'seconds': 5}),
]
FIXED = ['packet.json', 'receipt.json', 'transport.json', 'filing.json',
         'client-output/export.json', 'config/config.json',
         'config/tool-presentation.json']


def _dispatch(files, allowed_paths, name, args):
    """Simulated broker dispatch producing (result, new_files)."""
    if name == 'list_files':
        return {'ok': True, 'value': {'files': sorted(files),
                                      'writable': sorted(allowed_paths),
                                      'sources': []}}, files
    if name == 'read_file':
        try:
            return {'ok': True, 'value': _paged_read(files[args['path']], args)}, files
        except Exception:
            return {'ok': False, 'error': 'read failed'}, files
    if name == 'search':
        matches = []
        for target, content in sorted(files.items()):
            for number, line in enumerate(content.splitlines(), 1):
                if args['text'] in line:
                    matches.append({'path': target, 'line': number,
                                    'text': line[:2000]})
        return {'ok': True, 'value': {'matches': matches, 'truncated': False}}, files
    if name == 'write_file':
        old = digest(files[args['path']].encode()) if args['path'] in files else None
        if args.get('expected_sha256') != old:
            return {'ok': False, 'error': 'stale write: read latest file first'}, files
        files = dict(files)
        files[args['path']] = args['content']
        return {'ok': True, 'value': {'path': args['path'],
                                      'sha256': digest(args['content'].encode())}}, files
    if name == 'run_command':
        return {'ok': True, 'value': {
            'exit_code': 0, 'reason': None, 'stdout': 'ok\n', 'stderr': '',
            'direct_process_exited': True, 'local_quiescent': True,
            'isolation': {'quiescent': True, 'cleanup_error': None}}}, files
    raise AssertionError(name)


def _bundle(script=SCRIPT, allowed=ALLOWED, allowed_paths=('tools/new.txt',),
            kind='develop', depends_on=(), deps=None, answer=None,
            export_calls=None, extra_calls=(), discovery=True,
            discovery_args=None, discovery_payload=None, step_model='swe-2-max',
            agent_model='SWE-2 Max', result_override=None, filing_files=None,
            receipt_over=None, transport_over=None, packet_over=None,
            expect_over=None, message=None):
    job = {'id': 'verify-job', 'domain': 'evidence-correspondence',
           'kind': kind, 'brief': 'verify synthetic retained evidence',
           'inputs': ['tools/a.txt'], 'depends_on': list(depends_on),
           'allowed_paths': list(allowed_paths), 'allowed_tools': list(allowed)}
    ordered = tuple(name for name in JOB_TOOLS if name in set(allowed))
    inputs = {'tools/a.txt': {'content': SOURCE_CONTENT,
                              'sha256': digest(SOURCE_CONTENT.encode())}}
    dependencies = deps or {}
    refs = [f'source:tools/a.txt@{inputs["tools/a.txt"]["sha256"]}']
    refs += [f'filing:{d}@{dependencies[d]["sha256"]}' for d in depends_on]
    packet = {'job': job, 'plan_version': 3, 'source_commit': COMMIT,
              'source_inputs': inputs, 'dependencies': dependencies,
              'citation_ids': refs}
    permission = expected_permission_presentation(ordered)
    presentation = expected_tool_presentation(ordered)
    packet[PERMISSION_DIGEST_FIELD] = digest(encoded(permission))
    packet[TOOL_DIGEST_FIELD] = digest(encoded(presentation))
    packet.update(packet_over or {})
    files = {}
    current = {'tools/a.txt': SOURCE_CONTENT}
    for dep in dependencies.values():
        for item in dep['filing']['files']:
            current[item['path']] = item['content']
    initial = dict(current)
    rows = []
    for number, (name, args) in enumerate(script, 1):
        request = {'name': name, 'arguments': args, 'number': number,
                   'snapshot_sha256': digest(encoded(current))}
        request_raw = encoded(request)
        if result_override and number in result_override:
            result = result_override[number]
        elif name not in set(allowed):
            result = {'ok': False, 'error': 'tool not permitted for this job'}
        else:
            result, current = _dispatch(current, set(allowed_paths), name, args)
        record = {'request_sha256': digest(request_raw), 'result': result,
                  'snapshot_sha256': digest(encoded(current)), 'accepted': False}
        record_raw = encoded(record)
        files[f'tools/{number}/request.json'] = request_raw
        files[f'tools/{number}/receipt.json'] = record_raw
        rows.append({'number': number, 'sha256': digest(record_raw), 'name': name})
    proposed = [{'path': p, 'content': c} for p, c in sorted(current.items())
                if p in set(allowed_paths) and initial.get(p) != c]
    if answer is None:
        answer = {'job_id': job['id'], 'summary': 'synthetic filing',
                  'findings': ['observed'],
                  'evidence': refs + [f"tool:{r['number']}@{r['sha256']}"
                                      for r in rows],
                  'dissent': [], 'limitations': ['synthetic'], 'files': []}
    filing = dict(answer, files=proposed if filing_files is None else filing_files)
    filing_raw = encoded(filing)
    if message is None:
        message = encoded(answer).decode()
    calls = []
    if discovery:
        call = {'function_name': 'mcp_list_tools',
                'arguments': discovery_args or {'server_name': 'foundry'}}
        call['result'] = (discovery_payload if discovery_payload is not None
                          else {'tools': presentation['mcp']['tools']})
        calls.append(call)
    calls += (export_calls if export_calls is not None else [
        {'function_name': 'mcp_call_tool',
         'arguments': {'server_name': 'foundry', 'tool_name': name,
                       'arguments': args}} for name, args in script])
    calls += list(extra_calls)
    export = {'agent': {'model_name': agent_model},
              'final_metrics': {'tokens': 3},
              'steps': [{'source': 'agent', 'model_name': step_model,
                         'tool_calls': calls, 'message': message}]}
    export_raw = encoded(export)
    transport = {'exit_code': 0, 'reason': None, 'local_quiescent': True,
                 'broker_errors': [], 'scope': {'quiescent': True},
                 'tool_receipts': rows, 'tools_used': [r['name'] for r in rows],
                 'export_sha256': digest(export_raw),
                 'usage': export['final_metrics'],
                 PERMISSION_DIGEST_FIELD: packet[PERMISSION_DIGEST_FIELD],
                 TOOL_DIGEST_FIELD: packet[TOOL_DIGEST_FIELD]}
    transport.update(transport_over or {})
    transport_raw = encoded(transport)
    packet_raw = encoded(packet)
    receipt = {'job': job['id'], 'attempt': 1,
               'started': '2026-09-12T00:00:00+00:00',
               'ended': '2026-09-12T00:01:00+00:00', 'launch_entered': True,
               'state': 'returned', 'accepted': False, 'route': ROUTE,
               'packet_sha256': digest(packet_raw),
               'transport_sha256': digest(transport_raw),
               'export_sha256': digest(export_raw),
               'filing_sha256': digest(filing_raw),
               'tool_receipts': rows, 'tools_used': [r['name'] for r in rows],
               'exit_code': 0, 'reason': None, 'local_quiescent': True,
               'broker_errors': [], 'scope': {'quiescent': True},
               'usage': export['final_metrics'],
               PERMISSION_DIGEST_FIELD: packet[PERMISSION_DIGEST_FIELD],
               TOOL_DIGEST_FIELD: packet[TOOL_DIGEST_FIELD]}
    receipt.update(receipt_over or {})
    files.update({'packet.json': packet_raw, 'receipt.json': encoded(receipt),
                  'transport.json': transport_raw, 'filing.json': filing_raw,
                  'client-output/export.json': export_raw,
                  'config/config.json': encoded(permission),
                  'config/tool-presentation.json': encoded(presentation)})
    expect = {'source_commit': COMMIT, 'job_id': job['id'], 'attempt': 1,
              'route': ROUTE, 'model': agent_model}
    expect.update(expect_over or {})
    return files, expect, rows


def _edit(files, name, fn):
    value = strict_json(files[name])
    fn(value)
    files[name] = encoded(value)
    if name == 'transport.json':
        receipt = strict_json(files['receipt.json'])
        receipt['transport_sha256'] = digest(files[name])
        files['receipt.json'] = encoded(receipt)


def _retool(files, n, request=None, result=None, record=None):
    """Rewrite tools/<n>/ consistently so only the semantic mutation fires."""
    req = strict_json(files[f'tools/{n}/request.json'])
    req.update(request or {})
    req_raw = encoded(req)
    rec = strict_json(files[f'tools/{n}/receipt.json'])
    if result is not None:
        rec['result'] = result
    rec['request_sha256'] = digest(req_raw)
    rec.update(record or {})
    rec_raw = encoded(rec)
    files[f'tools/{n}/request.json'] = req_raw
    files[f'tools/{n}/receipt.json'] = rec_raw
    row = {'number': n, 'sha256': digest(rec_raw), 'name': req['name']}
    new_rows = [row if r['number'] == n else r
                for r in strict_json(files['transport.json'])['tool_receipts']]
    _edit(files, 'transport.json', lambda t: t.update(
        tool_receipts=new_rows, tools_used=[r['name'] for r in new_rows]))
    _edit(files, 'receipt.json', lambda r: r.update(
        tool_receipts=new_rows, tools_used=[r['name'] for r in new_rows]))


def _script_calls(script=SCRIPT):
    return [{'function_name': 'mcp_call_tool',
             'arguments': {'server_name': 'foundry', 'tool_name': name,
                           'arguments': args}} for name, args in script]


class PresentationDigestTests(unittest.TestCase):
    def test_known_answer_digests(self):
        self.assertEqual(digest(encoded(expected_permission_presentation(ALLOWED))),
                         PERMISSION_KNOWN)
        self.assertEqual(digest(encoded(expected_tool_presentation(ALLOWED))),
                         PRESENTATION_KNOWN)


class ValidBundleTests(unittest.TestCase):
    def test_complete_bundle_with_write_then_paged_read(self):
        files, expect, rows = _bundle()
        info = verify_attempt_inventory(files, expect)
        self.assertEqual(info['tool_calls'], len(SCRIPT))
        self.assertEqual(info['proposed_files'], ['tools/new.txt'])
        self.assertEqual([r['number'] for r in rows],
                         list(range(1, len(SCRIPT) + 1)))

    def test_zero_tool_bundle(self):
        files, expect, _ = _bundle(script=[])
        self.assertEqual(verify_attempt_inventory(files, expect)['tool_calls'], 0)

    def test_denied_tool_receipt_verifies(self):
        files, expect, _ = _bundle(
            script=[('list_files', {}),
                    ('run_command', {'argv': ['true'], 'seconds': 1}),
                    ('read_file', {'path': 'tools/a.txt'})],
            allowed=('list_files', 'read_file'), allowed_paths=(), kind='research')
        self.assertEqual(verify_attempt_inventory(files, expect)['tool_calls'], 3)

    def test_dependency_proposals_are_workspace_inputs(self):
        dep = {'sha256': 'c' * 64,
               'filing': {'files': [{'path': 'tools/dep.txt',
                                     'content': 'dep\n'}]}}
        files, expect, _ = _bundle(
            script=[('read_file', {'path': 'tools/dep.txt'})],
            depends_on=('dep-job',), deps={'dep-job': dep})
        verify_attempt_inventory(files, expect)

    def test_oversize_result_binding(self):
        raw = encoded({'ok': True, 'value': {'big': 'x' * 5000}})
        files, expect, _ = _bundle(result_override={1: {
            'ok': False, 'error': 'encoded tool output exceeds response cap',
            'retained_sha256': digest(raw), 'uncertain': False}})
        files['tools/1/oversize-result.json'] = raw
        verify_attempt_inventory(files, expect)

    def test_noncanonical_export_bytes_still_verify(self):
        files, expect, _ = _bundle()
        export_raw = json.dumps(
            strict_json(files['client-output/export.json']), indent=1).encode()
        files['client-output/export.json'] = export_raw
        _edit(files, 'transport.json',
              lambda t: t.update(export_sha256=digest(export_raw)))
        _edit(files, 'receipt.json',
              lambda r: r.update(export_sha256=digest(export_raw)))
        verify_attempt_inventory(files, expect)


class FileHygieneTests(unittest.TestCase):
    def test_missing_fixed_files_refused(self):
        for name in FIXED:
            with self.subTest(missing=name):
                files, expect, _ = _bundle()
                del files[name]
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)

    def test_extra_files_refused(self):
        for extra in ['notes.md', 'stdout.txt', 'tools/0/request.json',
                      'tools/01/request.json', 'tools/9/request.json',
                      'tools/1/extra.json', 'tools/1/.hidden', 'tools/x']:
            with self.subTest(extra=extra):
                files, expect, _ = _bundle()
                files[extra] = b'{}'
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)

    def test_missing_and_gap_tool_dirs_refused(self):
        files, expect, _ = _bundle()
        del files['tools/2/receipt.json']
        with self.assertRaisesRegex(Refused, 'request/receipt required'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle()
        del files['tools/4/request.json']
        del files['tools/4/receipt.json']
        with self.assertRaisesRegex(Refused, 'contiguous'):
            verify_attempt_inventory(files, expect)

    def test_nonbytes_and_noncanonical_refused(self):
        files, expect, _ = _bundle()
        files['packet.json'] = '{}'
        with self.assertRaises(Refused):
            verify_attempt_inventory(files, expect)
        for name in ['packet.json', 'receipt.json', 'transport.json',
                     'filing.json', 'config/config.json',
                     'config/tool-presentation.json', 'tools/1/request.json',
                     'tools/1/receipt.json']:
            with self.subTest(noncanonical=name):
                files, expect, _ = _bundle()
                files[name] = json.dumps(
                    strict_json(files[name]), indent=1).encode()
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)


class IdentityAndStateTests(unittest.TestCase):
    def test_receipt_field_mutations_refused(self):
        cases = [
            ('unknown', {'state': 'unknown'}),
            ('failed', {'state': 'failed'}),
            ('accepted', {'accepted': True}),
            ('attempt', {'attempt': 2}),
            ('job', {'job': 'other'}),
            ('launch', {'launch_entered': False}),
            ('route', {'route': dict(ROUTE, model='other')}),
            ('packet_sha256', {'packet_sha256': '0' * 64}),
            ('transport_sha256', {'transport_sha256': '0' * 64}),
            ('export_sha256', {'export_sha256': '0' * 64}),
            ('filing_sha256', {'filing_sha256': '0' * 64}),
            ('exit_code', {'exit_code': 1}),
            ('reason', {'reason': 'timeout'}),
            ('quiescent', {'local_quiescent': False}),
            ('broker_errors', {'broker_errors': ['boom']}),
            ('scope', {'scope': {'quiescent': False}}),
            ('usage', {'usage': {'tokens': 9}}),
            ('perm', {PERMISSION_DIGEST_FIELD: '0' * 64}),
            ('tool', {TOOL_DIGEST_FIELD: '0' * 64}),
            ('rows', {'tool_receipts': []}),
            ('error', {'error': 'boom'}),
        ]
        for name, over in cases:
            with self.subTest(receipt=name):
                files, expect, _ = _bundle(receipt_over=over)
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)

    def test_transport_mutations_refused(self):
        cases = [
            ('exit_code', lambda t: t.update(exit_code=1)),
            ('reason', lambda t: t.update(reason='timeout')),
            ('quiescent', lambda t: t.update(local_quiescent=False)),
            ('broker_errors', lambda t: t.update(broker_errors=['x'])),
            ('scope', lambda t: t.update(scope={'quiescent': False})),
            ('export_sha256', lambda t: t.update(export_sha256='0' * 64)),
            ('usage', lambda t: t.update(usage={})),
            ('rows_reversed', lambda t: t.update(
                tool_receipts=list(reversed(t['tool_receipts'])))),
            ('rows_dropped', lambda t: t['tool_receipts'].pop()),
            ('tools_used', lambda t: t.update(tools_used=[])),
            ('perm', lambda t: t.update(
                **{PERMISSION_DIGEST_FIELD: '0' * 64})),
            ('tool', lambda t: t.update(**{TOOL_DIGEST_FIELD: '0' * 64})),
        ]
        for name, fn in cases:
            with self.subTest(transport=name):
                files, expect, _ = _bundle()
                _edit(files, 'transport.json', fn)
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)

    def test_expect_and_packet_mutations_refused(self):
        for name, over in [('attempt', {'attempt': 2}),
                           ('job', {'job_id': 'other-job'}),
                           ('commit', {'source_commit': 'a' * 40}),
                           ('model', {'model': 'other'}),
                           ('route', {'route': dict(ROUTE, model='other')}),
                           ('route-backend', {'route': dict(ROUTE, backend='x')})]:
            with self.subTest(expect=name):
                files, expect, _ = _bundle(expect_over=over)
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)
        for name, over in [('version', {'plan_version': 2}),
                           ('commit', {'source_commit': 'a' * 40}),
                           ('perm', {PERMISSION_DIGEST_FIELD: '0' * 64}),
                           ('tool', {TOOL_DIGEST_FIELD: '0' * 64}),
                           ('citations', {'citation_ids': []})]:
            with self.subTest(packet=name):
                files, expect, _ = _bundle(packet_over=over)
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)

    def test_source_and_presentation_drift_refused(self):
        files, expect, _ = _bundle()
        _edit(files, 'packet.json', lambda p: p['source_inputs'][
            'tools/a.txt'].update(content='tampered'))
        with self.assertRaisesRegex(Refused, 'source input digest'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle()
        _edit(files, 'config/config.json',
              lambda c: c['permissions']['allow'].append('mcp__foundry__exec'))
        with self.assertRaisesRegex(Refused, 'permission presentation'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle()
        _edit(files, 'config/tool-presentation.json',
              lambda c: c['mcp']['tools'].pop())
        with self.assertRaisesRegex(Refused, 'MCP tool presentation'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle()
        _edit(files, 'packet.json', lambda p: p.pop(TOOL_DIGEST_FIELD))
        with self.assertRaises(Refused):
            verify_attempt_inventory(files, expect)


class ToolRowMutationTests(unittest.TestCase):
    def test_request_mutations_refused(self):
        cases = [('number', {'number': 9}),
                 ('name', {'name': 'exec'}),
                 ('snapshot', {'snapshot_sha256': '0' * 64}),
                 ('args', {'arguments': []}),
                 ('extra-key', {'bogus': 1})]
        for name, over in cases:
            with self.subTest(request=name):
                files, expect, _ = _bundle()
                _retool(files, 1, request=over)
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)

    def test_record_mutations_refused(self):
        for name, over in [('accepted', {'accepted': True}),
                           ('request_sha256', {'request_sha256': '0' * 64}),
                           ('snapshot', {'snapshot_sha256': '0' * 64}),
                           ('extra-key', {'bogus': 1})]:
            with self.subTest(record=name):
                files, expect, _ = _bundle()
                _retool(files, 2, record=over)
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)

    def test_result_mutations_refused(self):
        files, expect, _ = _bundle()
        page = dict(strict_json(files['tools/2/receipt.json'])['result']['value'],
                    content='tampered')
        next_off = dict(strict_json(files['tools/2/receipt.json'])['result']['value'],
                        next_offset=99)
        listed = strict_json(files['tools/1/receipt.json'])['result']['value']
        cases = [
            ('read-page', 2, {'ok': True, 'value': page}),
            ('read-page-next', 2, {'ok': True, 'value': next_off}),
            ('write-value', 3, {'ok': True, 'value': {
                'path': 'tools/new.txt', 'sha256': '0' * 64}}),
            ('ok-flip-write', 3, {'ok': False, 'error': 'x'}),
            ('ok-flip-search', 6, {'ok': False, 'error': 'x'}),
            ('ok-flip-list', 1, {'ok': False, 'error': 'x'}),
            ('uncertain', 4, {'ok': False, 'error': 'x', 'uncertain': True}),
            ('extra-field', 1, {'ok': True, 'value': listed, 'extra': 1}),
            ('missing-ok', 1, {'value': {}}),
            ('missing-error', 1, {'ok': False}),
        ]
        for name, n, result in cases:
            with self.subTest(result=name):
                files, expect, _ = _bundle()
                _retool(files, n, result=result)
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)

    def test_stale_write_and_denied_drift_refused(self):
        files, expect, _ = _bundle()
        _retool(files, 3, request={'arguments': {
            'path': 'tools/new.txt', 'content': NEW_CONTENT,
            'expected_sha256': '0' * 64}})
        with self.assertRaisesRegex(Refused, 'broker preconditions'):
            verify_attempt_inventory(files, expect)

        files, expect, _ = _bundle(
            script=[('run_command', {'argv': ['true'], 'seconds': 1})],
            allowed=('list_files',), allowed_paths=(), kind='research')
        verify_attempt_inventory(files, expect)
        _retool(files, 1, result={'ok': False, 'error': 'other error'})
        with self.assertRaisesRegex(Refused, 'denied tool receipt'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle(
            script=[('run_command', {'argv': ['true'], 'seconds': 1})],
            allowed=('list_files',), allowed_paths=(), kind='research')
        _retool(files, 1, result={'ok': True, 'value': {}})
        with self.assertRaisesRegex(Refused, 'denied tool receipt'):
            verify_attempt_inventory(files, expect)

    def test_oversize_mutations_refused(self):
        files, expect, _ = _bundle()
        files['tools/1/oversize-result.json'] = b'{}'
        with self.assertRaisesRegex(Refused, 'unreferenced oversize'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle()
        _retool(files, 1, result={'ok': False, 'error': 'cap',
                                  'retained_sha256': 'a' * 64})
        with self.assertRaisesRegex(Refused, 'oversize result binding'):
            verify_attempt_inventory(files, expect)


class ExportCorrespondenceTests(unittest.TestCase):
    def test_call_sequence_mutations_refused(self):
        calls = _script_calls()
        cases = [
            ('omitted', {'export_calls': calls[:-1]}),
            ('reordered', {'export_calls': list(reversed(calls))}),
            ('duplicated', {'extra_calls': [calls[0]]}),
            ('foreign', {'extra_calls': [{'function_name': 'exec',
                                          'arguments': {'command': 'x'}}]}),
            ('other-server', {'extra_calls': [{'function_name': 'mcp_call_tool',
                'arguments': {'server_name': 'other', 'tool_name': 'list_files',
                              'arguments': {}}}]}),
            ('native-function', {'extra_calls': [{
                'function_name': 'read', 'arguments': {'server_name': 'foundry'}}]}),
            ('bad-tool', {'extra_calls': [{'function_name': 'mcp_call_tool',
                'arguments': {'server_name': 'foundry', 'tool_name': 'exec',
                              'arguments': {}}}]}),
        ]
        for name, kw in cases:
            with self.subTest(calls=name):
                files, expect, _ = _bundle(**kw)
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)

    def test_discovery_binding_refused(self):
        files, expect, _ = _bundle(
            discovery_args={'server_name': 'foundry', 'extra': 1})
        with self.assertRaisesRegex(Refused, 'discovery scope'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle(discovery_payload={'tools': []})
        with self.assertRaisesRegex(Refused, 'differs from retained'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle(discovery_payload={'tools': 'garbage'})
        with self.assertRaisesRegex(Refused, 'malformed discovery'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle(discovery_payload={'unrelated': 1})
        with self.assertRaisesRegex(Refused, 'missing tools'):
            verify_attempt_inventory(files, expect)

    def test_identity_and_answer_refused(self):
        files, expect, _ = _bundle(step_model='other-model')
        with self.assertRaisesRegex(Refused, 'model changed'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle(agent_model='Other Model',
                                   expect_over={'model': 'SWE-2 Max'})
        with self.assertRaisesRegex(Refused, 'model identity'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle(message='')
        with self.assertRaisesRegex(Refused, 'missing final worker answer'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle(message='I hereby accept this work.')
        with self.assertRaisesRegex(Refused, 'ambiguous'):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle(
            message='```json\n{}\n```\n```json\n{}\n```')
        with self.assertRaisesRegex(Refused, 'ambiguous'):
            verify_attempt_inventory(files, expect)


class FilingBindingTests(unittest.TestCase):
    def test_filing_mutations_refused(self):
        cases = [
            ('files-channel', {'answer': {
                'job_id': 'verify-job', 'summary': 's', 'findings': [],
                'evidence': [], 'dissent': [], 'limitations': [],
                'files': [{'path': 'tools/new.txt', 'content': 'x'}]}}),
            ('unbound-evidence', {'answer': {
                'job_id': 'verify-job', 'summary': 's', 'findings': [],
                'evidence': ['tool:99@' + '0' * 64], 'dissent': [],
                'limitations': [], 'files': []}}),
            ('wrong-job', {'answer': {
                'job_id': 'other-job', 'summary': 's', 'findings': [],
                'evidence': [], 'dissent': [], 'limitations': [],
                'files': []}}),
            ('filing-files', {'filing_files': []}),
        ]
        for name, kw in cases:
            with self.subTest(filing=name):
                files, expect, _ = _bundle(**kw)
                with self.assertRaises(Refused):
                    verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle()
        files['filing.json'] = encoded({'job_id': 'verify-job'})
        with self.assertRaises(Refused):
            verify_attempt_inventory(files, expect)
        files, expect, _ = _bundle()
        files['client-output/export.json'] = b'not json'
        with self.assertRaises(Refused):
            verify_attempt_inventory(files, expect)

    def test_dependency_conflict_refused(self):
        deps = {'d-one': {'sha256': 'c' * 64, 'filing': {'files': [
            {'path': 'tools/x.txt', 'content': 'a'}]}},
            'd-two': {'sha256': 'd' * 64, 'filing': {'files': [
            {'path': 'tools/x.txt', 'content': 'b'}]}}}
        files, expect, _ = _bundle(
            script=[], depends_on=('d-one', 'd-two'), deps=deps)
        with self.assertRaisesRegex(Refused, 'conflicting'):
            verify_attempt_inventory(files, expect)


if __name__ == '__main__':
    unittest.main()
