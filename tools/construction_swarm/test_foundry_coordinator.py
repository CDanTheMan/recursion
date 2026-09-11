"""Coordinator settlement combines native scope cleanup and transport evidence."""
import contextlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .contracts import digest, encoded, strict_json
from .foundry_coordinator import coordinator_batch_size, synthesize


class CoordinatorTests(unittest.TestCase):
    def test_v3_uses_smaller_batches_for_filing_and_progress_evidence(self):
        self.assertEqual(coordinator_batch_size({'version': 2}), 20)
        self.assertEqual(coordinator_batch_size({'version': 3}), 8)

    def test_synthesis_receipt_requires_empty_scope_and_direct_exit(self):
        manifest = {'run_id': 'synthetic', 'source_commit': '0' * 40, 'jobs': [
            {'id': 'missing', 'state': 'blocked', 'attempts': 0}]}
        synthesis = {'summary': 'Evidence is missing.', 'assessments': [
            {'id': 'missing', 'disposition': 'blocked', 'reason': 'No filing was returned.', 'evidence': []}]}
        events = [
            {'type': 'system', 'subtype': 'init', 'model': 'Cursor Grok 4.5 High'},
            {'type': 'result', 'subtype': 'success', 'is_error': False,
             'result': encoded(synthesis).decode()},
        ]
        stdout = b'\n'.join(encoded(event) for event in events) + b'\n'

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            runtime = base / 'runtime'
            runtime.mkdir()
            for name in ['node', 'index.js']:
                (runtime / name).write_bytes(b'synthetic runtime, never executed')
            credential = base / 'synthetic-auth.json'
            credential.write_bytes(b'{}')

            for case, empty_scope, direct_exit in [
                ('complete', True, True), ('uncertain-cleanup', False, True), ('not-exited', True, False),
            ]:
                with self.subTest(case=case):
                    root = base / case
                    root.mkdir()
                    observation = {'path': '/synthetic/cgroup', 'quiescent': False, 'cleanup_error': None}

                    @contextlib.contextmanager
                    def scope(*args, observation=observation, empty_scope=empty_scope):
                        try:
                            yield Path(observation['path']), observation
                        finally:
                            observation['quiescent'] = empty_scope
                            observation['cleanup_error'] = None if empty_scope else 'injected cleanup uncertainty'

                    transport = {'exit_code': 0, 'reason': None, 'direct_process_exited': direct_exit,
                                 'local_quiescent': False, 'pipes_closed': True,
                                 'stdout': stdout, 'stderr': b''}
                    with patch('tools.construction_swarm.foundry_coordinator.report', return_value=manifest), \
                            patch('tools.construction_swarm.foundry_coordinator.reviewed_plan', return_value={'version': 2}), \
                            patch('tools.construction_swarm.foundry_coordinator.client_argv', return_value=['synthetic']), \
                            patch('tools.construction_swarm.foundry_coordinator.process_scope', scope), \
                            patch('tools.construction_swarm.foundry_coordinator.execute_scoped', return_value=transport):
                        result = synthesize(root, 'cursor', runtime, credential)

                    directory = root / 'coordinator-cursor-0'
                    retained = strict_json((directory / 'receipt.json').read_bytes())
                    self.assertEqual(retained, result)
                    self.assertEqual(retained['local_quiescent'], empty_scope and direct_exit)
                    self.assertEqual(retained['scope'], observation)
                    self.assertTrue(retained['pipes_closed'])
                    self.assertEqual((directory / 'stdout.txt').read_bytes(), stdout)
                    reservation = strict_json((directory / 'reservation.json').read_bytes())
                    self.assertEqual(reservation['dispatches_charged'], 1)
                    filing = directory / 'synthesis.json'
                    if empty_scope and direct_exit:
                        self.assertEqual(result['state'], 'returned')
                        self.assertEqual(strict_json(filing.read_bytes())['synthesis'], synthesis)
                        self.assertEqual(result['synthesis_sha256'], digest(filing.read_bytes()))
                    else:
                        self.assertEqual(result['state'], 'unknown')
                        self.assertIn('did not complete normally', result['error'])
                        self.assertFalse(filing.exists())


if __name__ == '__main__':
    unittest.main()
