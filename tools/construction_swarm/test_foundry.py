"""Adversarial and real Linux isolation gates for the native construction route."""
import contextlib
import socket
import sys
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from .contracts import Refused, digest, encoded, strict_json
from .foundry_coordinator import validate_synthesis
from .foundry_tools import Broker, ToolUncertain, run_command, serve_connection


class BrokerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def broker(self, name='broker', **kwargs):
        return Broker(self.root / name, {'tools/code.py': 'old'}, ['tools/code.py', 'tools/new.py'], {}, **kwargs)

    def test_scoped_compare_and_swap_and_ephemeral_export(self):
        broker = self.broker()
        for name in ['/etc/passwd', '../tools/code.py', 'tools/.env', 'TOOLS/code.py', 'tools/CON.py']:
            result = broker.call('write_file', {'path': name, 'content': 'escape', 'expected_sha256': None})
            self.assertFalse(result['ok'])
        result = broker.call('write_file', {'path': 'tools/code.py', 'content': 'new', 'expected_sha256': digest(b'old')})
        self.assertTrue(result['ok'])
        stale = broker.call('write_file', {'path': 'tools/code.py', 'content': 'lost update', 'expected_sha256': digest(b'old')})
        self.assertFalse(stale['ok'])
        self.assertEqual(broker.proposed_files(), [{'path': 'tools/code.py', 'content': 'new'}])
        self.assertFalse((self.root / 'tools/code.py').exists())

    def test_budget_errors_are_charged_and_receipts_bind_requests(self):
        broker = self.broker(max_calls=2)
        broker.call('read_file', {'path': 'not-present'})
        broker.call('list_files', {})
        with self.assertRaises(Refused):
            broker.call('list_files', {})
        for row in broker.receipts:
            directory = broker.root / str(row['number'])
            data = (directory / 'receipt.json').read_bytes()
            self.assertEqual(digest(data), row['sha256'])
            self.assertEqual(strict_json(data)['request_sha256'], digest((directory / 'request.json').read_bytes()))

    def test_uncertain_cleanup_prevents_further_tools_and_success(self):
        broker = self.broker()
        with patch('tools.construction_swarm.foundry_tools.run_command', side_effect=ToolUncertain({'quiescent': False})):
            result = broker.call('run_command', {'argv': ['true'], 'seconds': 1})
        self.assertFalse(result['ok'])
        self.assertTrue(broker.uncertain)
        with self.assertRaisesRegex(Refused, 'uncertain'):
            broker.call('list_files', {})

    def test_execute_exception_retains_uncertain_scope_cleanup_receipt(self):
        broker = self.broker()
        cleanup_ran = []

        @contextlib.contextmanager
        def uncertain_scope(stop, seconds):
            observation = {'path': '/synthetic/cgroup', 'quiescent': False,
                           'cleanup_error': None}
            try:
                yield Path(observation['path']), observation
            finally:
                observation['cleanup_error'] = 'injected cgroup kill failure'
                cleanup_ran.append(True)

        with patch('tools.construction_swarm.foundry_tools.tool_scope', uncertain_scope), \
                patch('tools.construction_swarm.foundry_tools.bwrap_argv', return_value=['/synthetic/bwrap']), \
                patch('tools.construction_swarm.foundry_tools.execute', side_effect=OSError('injected transport failure')):
            result = broker.call('run_command', {'argv': ['true'], 'seconds': 1})

        self.assertEqual(cleanup_ran, [True])
        self.assertFalse(result['ok'])
        self.assertTrue(result['uncertain'])
        self.assertTrue(broker.uncertain)
        observation = result['observation']
        self.assertEqual(observation['reason'], 'transport-exception')
        self.assertIn('injected transport failure', observation['error'])
        self.assertEqual(observation['isolation']['cleanup_error'], 'injected cgroup kill failure')
        self.assertFalse(observation['local_quiescent'])
        retained = strict_json((broker.root / '1/receipt.json').read_bytes())
        self.assertEqual(retained['result']['observation'], observation)
        self.assertEqual(digest((broker.root / '1/receipt.json').read_bytes()), broker.receipts[0]['sha256'])
        with self.assertRaisesRegex(Refused, 'uncertain'):
            broker.call('list_files', {})

    def test_receipt_io_loss_leaves_unknown(self):
        broker = self.broker()
        from .runner import put
        def fail_receipt(target, data):
            if target.name == 'receipt.json':
                raise OSError('injected disk failure')
            put(target, data)
        with patch('tools.construction_swarm.foundry_tools.put', side_effect=fail_receipt), self.assertRaises(OSError):
            broker.call('list_files', {})
        self.assertTrue(broker.uncertain)
        self.assertTrue((broker.root / '1/request.json').exists())

    def test_independent_workers_and_source_corpus(self):
        first, second = self.broker('a'), self.broker('b')
        first.call('write_file', {'path': 'tools/new.py', 'content': 'worker-a', 'expected_sha256': None})
        self.assertFalse(second.call('read_file', {'path': 'tools/new.py'})['ok'])
        self.assertFalse(second.call('fetch_source', {'url': 'http://127.0.0.1/'})['ok'])

    def test_mcp_large_response_complete_and_strict_request(self):
        broker = self.broker()
        broker.files['tools/code.py'] = 'x' * 262144
        client, server = socket.socketpair()
        self.addCleanup(client.close)
        self.addCleanup(server.close)
        thread = threading.Thread(target=serve_connection, args=(server, broker), daemon=True)
        thread.start()
        client.sendall(encoded({'jsonrpc': '2.0', 'id': 7, 'method': 'tools/call',
                               'params': {'name': 'read_file', 'arguments': {'path': 'tools/code.py'}}}) + b'\n')
        with client.makefile('rb') as stream:
            response = strict_json(stream.readline())
        value = strict_json(response['result']['content'][0]['text'])
        self.assertEqual(value['value']['content'], 'x' * 262144)
        client.shutdown(socket.SHUT_WR)
        thread.join(2)
        self.assertFalse(thread.is_alive())

    def test_coordinator_coverage_evidence_and_unknown_barrier(self):
        packet = {'records': [{'id': 'a', 'state': 'returned', 'filing_ref': 'filing:a@abc'},
                              {'id': 'b', 'state': 'unknown'}]}
        valid = {'summary': 'One returned, one uncertain.', 'assessments': [
            {'id': 'a', 'disposition': 'review', 'reason': 'Inspect actual gates.', 'evidence': ['filing:a@abc']},
            {'id': 'b', 'disposition': 'blocked', 'reason': 'No terminal evidence.', 'evidence': []}]}
        validate_synthesis(valid, packet)
        import copy
        for mutate in [lambda v: v['assessments'].pop(),
                       lambda v: v['assessments'][0].update(evidence=['filing:foreign@bad']),
                       lambda v: v['assessments'][1].update(disposition='review'),
                       lambda v: v['assessments'][0].update(disposition='accepted')]:
            invalid = copy.deepcopy(valid)
            mutate(invalid)
            with self.assertRaises(Refused):
                validate_synthesis(invalid, packet)

    def test_native_claim_holds_survive_missing_settlement(self):
        from .foundry_wsl import native_holds
        directory = self.root / 'native-claims'
        directory.mkdir()
        claim = directory / 'a.json'
        claim.write_bytes(encoded({'slots': 99}))
        self.assertEqual(native_holds(self.root), 99)
        terminal = directory / 'a.settled.json'
        terminal.write_bytes(encoded({'claim_sha256': digest(claim.read_bytes()), 'held': 2}))
        self.assertEqual(native_holds(self.root), 2)
        terminal.write_bytes(encoded({'claim_sha256': 'bad', 'held': 0}))
        with self.assertRaises(Refused):
            native_holds(self.root)

    def test_unicode_output_limit_is_receipted_not_unknown(self):
        broker = self.broker()
        broker.files['tools/code.py'] = '\u00e9' * 600000
        response = broker.call('read_file', {'path': 'tools/code.py'})
        self.assertFalse(response['ok'])
        self.assertFalse(broker.uncertain)
        self.assertTrue((broker.root / '1/oversize-result.json').is_file())
        self.assertTrue(broker.call('list_files', {})['ok'])

    def test_final_filing_parser_rejects_ambiguous_json(self):
        from .foundry_output import parsed_json
        self.assertEqual(parsed_json('Observed gate passed.\n```json\n{"a":1}\n```'), {'a': 1})
        for text in ['```json\n{"a":1}\n```\n```json\n{"b":2}\n```', '{"a":1,"a":2}',
                     'Text with no filing', '```json\n{"a":NaN}\n```']:
            with self.assertRaises(Refused):
                parsed_json(text)

    def test_malformed_filing_cannot_bypass_execution_qualification(self):
        import copy

        from .foundry_client import collect_filing
        from .foundry_output import CompletedFailure

        broker = self.broker()
        broker.call('list_files', {})
        job = {'id': 'worker', 'allowed_paths': []}
        transport = {'exit_code': 0, 'reason': None, 'local_quiescent': True, 'broker_errors': []}
        export = {'agent': {'model_name': 'SWE-2 Max'}, 'steps': [{
            'source': 'agent', 'model_name': 'swe-2-max', 'message': 'Malformed final filing',
            'tool_calls': [{'function_name': 'mcp_call_tool', 'arguments': {
                'server_name': 'foundry', 'tool_name': 'list_files', 'arguments': {}}}]}]}

        with self.assertRaises(CompletedFailure):
            collect_filing(export, broker, job, [], transport)

        for name, mutate, expected_error in [
            ('changed-model', lambda e: e['steps'][0].update(model_name='other-model'), 'model changed'),
            ('native-tool', lambda e: e['steps'][0]['tool_calls'].append({
                'function_name': 'exec', 'arguments': {'command': 'true'}}), 'native tool'),
            ('unreceipted-tool', lambda e: e['steps'][0]['tool_calls'].append({
                'function_name': 'mcp_call_tool', 'arguments': {
                    'server_name': 'foundry', 'tool_name': 'search', 'arguments': {'text': 'x'}}}),
             'differ from durable broker receipts'),
        ]:
            with self.subTest(name=name):
                invalid = copy.deepcopy(export)
                mutate(invalid)
                with self.assertRaisesRegex(Refused, expected_error):
                    collect_filing(invalid, broker, job, [], transport)

        with self.assertRaisesRegex(Refused, 'did not complete normally'):
            collect_filing(export, broker, job, [], {**transport, 'local_quiescent': False})

    def test_dependent_verifier_sees_proposed_bytes_and_conflicts_block(self):
        from .foundry_client import workspace_files
        packet = {'source_inputs': {'tools/code.py': {'content': 'old'}}, 'dependencies': {
            'developer': {'filing': {'files': [{'path': 'tools/code.py', 'content': 'new'},
                                             {'path': 'tools/test_new.py', 'content': 'gate'}]}}}}
        self.assertEqual(workspace_files(packet), {'tools/code.py': 'new', 'tools/test_new.py': 'gate'})
        packet['dependencies']['other'] = {'filing': {'files': [{'path': 'tools/code.py', 'content': 'conflicting'}]}}
        with self.assertRaisesRegex(Refused, 'conflicting'):
            workspace_files(packet)


LINUX_SCOPE = sys.platform == 'linux' and Path('/sys/fs/cgroup/cgroup.subtree_control').exists()


@unittest.skipUnless(LINUX_SCOPE, 'requires delegated Linux cgroups and bwrap')
class LinuxToolsTests(unittest.TestCase):
    def test_actual_isolation_scratch_and_detached_child_cleanup(self):
        code = ('import os,socket,pathlib,subprocess; '
                'assert not any(pathlib.Path(p).exists() for p in ["/mnt/c","/mnt/d","/root/.ssh","/home/agent/.local/share/devin/credentials.toml","/sys/fs/cgroup"]); '
                'assert not os.environ.get("WINDSURF_API_KEY"); '
                'pathlib.Path("temporary.py").write_text("ephemeral"); '
                'subprocess.Popen(["sleep","60"],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); '
                's=socket.socket(); s.settimeout(.2); assert s.connect_ex(("1.1.1.1",443)) != 0; print("ISOLATED")')
        result = run_command({}, ['python3', '-c', code], 5)
        self.assertEqual(result['exit_code'], 0, result)
        self.assertTrue(result['local_quiescent'])
        self.assertIn('ISOLATED', result['stdout'])
        second = run_command({}, ['python3', '-c', 'from pathlib import Path; assert not Path("temporary.py").exists()'], 5)
        self.assertEqual(second['exit_code'], 0)

    def test_cancel_and_timeout_reap_scope(self):
        cancelled = threading.Event()
        timer = threading.Timer(.2, cancelled.set)
        timer.start()
        try:
            result = run_command({}, ['sleep', '60'], 5, cancelled.is_set)
        finally:
            timer.cancel()
        self.assertTrue(result['local_quiescent'])
        self.assertEqual(result['reason'], 'cancelled')
        result = run_command({}, ['sleep', '60'], 1)
        self.assertTrue(result['local_quiescent'])
        self.assertEqual(result['reason'], 'timeout')

    def test_one_hundred_jobs_share_four_real_tool_slots(self):
        def worker(number):
            return run_command({'tools/value.py': f'value={number}\n'}, ['python3', '-c',
                f'from tools.value import value; assert value=={number}; print(value)'], 10)
        with ThreadPoolExecutor(max_workers=100) as executor:
            results = list(executor.map(worker, range(100)))
        events = []
        for number, result in enumerate(results):
            self.assertEqual(result['exit_code'], 0, result)
            self.assertEqual(result['stdout'].strip(), str(number))
            self.assertTrue(result['local_quiescent'])
            observation = result['isolation']
            events.extend([(observation['started_unix'], 1), (observation['ended_unix'], -1)])
        active = peak = 0
        for _, change in sorted(events):
            active += change
            peak = max(peak, active)
        self.assertLessEqual(peak, 4)
        self.assertGreaterEqual(peak, 2)


if __name__ == '__main__':
    unittest.main()
