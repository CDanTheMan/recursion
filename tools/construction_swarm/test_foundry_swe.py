"""Generated unittest coverage for foundry_tools.Broker and run_command.

Contract under test, observed only through Broker.call receipts:
- write_file requires the current digest; stale writes are refused and the
  frozen workspace is preserved.
- Every path argument must be a canonical relative POSIX path; scope escapes,
  hidden components and traversal are refused identically for read and write.
- The cumulative tool budget charges every dispatched call, including failed
  ones, while envelope refusals (unknown tool, oversized request) are free.
- A tool outcome whose cleanup cannot be observed latches the broker: every
  later call is refused so a worker cannot build on an unobserved state.
- run_command executes argv in a disposable offline Linux copy with no host
  mounts or network. That real check is skipped unless delegated cgroup
  controllers are visible, which nested offline sandboxes do not provide.
"""
from __future__ import annotations

import contextlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.construction_swarm import foundry_tools
from tools.construction_swarm.contracts import Refused, digest

ALLOWED = ('docs/allowed.txt', 'docs/out.txt', 'docs/new.txt')
GATE = 'foundry_command_gate.py'


def linux_tool_prereqs():
    """Prerequisites for a real run_command: delegated v2 controllers,
    bubblewrap, and a writable /run slot pool. Inside the offline sandbox
    /sys/fs/cgroup is not even mounted, so this returns False there."""
    if sys.platform != 'linux' or not hasattr(os, 'geteuid'):
        return False
    base = Path('/sys/fs/cgroup')
    try:
        control = base / 'cgroup.subtree_control'
        if not control.is_file():
            return False
        if not {'memory', 'pids', 'cpu'} <= set(control.read_text().split()):
            return False
        if shutil.which('bwrap') is None:
            return False
        if not (os.access('/run', os.W_OK) or Path('/run/recursion-foundry-tools').is_dir()):
            return False
        return os.geteuid() == 0 or os.access(base, os.W_OK)
    except OSError:
        return False


class BrokerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix='foundry-broker-test-')
        self.addCleanup(self._tmp.cleanup)

    def broker(self, name='run', files=None, allowed=ALLOWED, sources=None, **kw):
        return foundry_tools.Broker(Path(self._tmp.name) / name, dict(files or {}),
                                    list(allowed), dict(sources or {}), **kw)

    def test_stale_write_rejected_and_workspace_preserved(self):
        broker = self.broker(files={'docs/out.txt': 'original'})
        seen = broker.call('read_file', {'path': 'docs/out.txt'})
        self.assertTrue(seen['ok'])
        self.assertEqual(seen['value']['sha256'], digest(b'original'))
        stale = broker.call('write_file', {'path': 'docs/out.txt', 'content': 'changed',
                                         'expected_sha256': digest(b'wrong-idea')})
        self.assertFalse(stale['ok'])
        self.assertIn('stale', stale['error'])
        self.assertEqual(broker.files['docs/out.txt'], 'original')
        self.assertEqual(broker.proposed_files(), [])
        current = broker.call('write_file', {'path': 'docs/out.txt', 'content': 'changed',
                                           'expected_sha256': seen['value']['sha256']})
        self.assertTrue(current['ok'])
        self.assertEqual(current['value']['sha256'], digest(b'changed'))
        again = broker.call('write_file', {'path': 'docs/out.txt', 'content': 'x',
                                          'expected_sha256': seen['value']['sha256']})
        self.assertFalse(again['ok'])
        self.assertEqual(broker.files['docs/out.txt'], 'changed')
        forged = broker.call('write_file', {'path': 'docs/new.txt', 'content': 'n',
                                          'expected_sha256': digest(b'n')})
        self.assertFalse(forged['ok'])
        fresh = broker.call('write_file', {'path': 'docs/new.txt', 'content': 'n',
                                         'expected_sha256': None})
        self.assertTrue(fresh['ok'])
        self.assertEqual({f['path'] for f in broker.proposed_files()},
                         {'docs/out.txt', 'docs/new.txt'})
        self.assertEqual(len(broker.receipts), broker.count)

    def test_path_scope_hidden_and_traversal_refused(self):
        broker = self.broker(files={'docs/out.txt': 'data'})
        bad = ['../escape.txt', 'a/../b.txt', '/etc/passwd', '.hidden',
               'docs/.secret/x.txt', 'docs//x.txt', 'docs/./x.txt',
               'docs/trailing.txt.', 'docs/trail .txt', 'docs\\win.txt',
               'con.txt', 'COM3.txt', 'lpt9/x.txt', 'x' * 241, None, 7]
        for value in bad:
            with self.subTest(path=repr(value)):
                r = broker.call('read_file', {'path': value})
                self.assertFalse(r['ok'])
                self.assertTrue(r['error'])
                w = broker.call('write_file', {'path': value, 'content': 'x',
                                             'expected_sha256': None})
                self.assertFalse(w['ok'])
        r = broker.call('read_file', {'path': 'docs/absent.txt'})
        self.assertFalse(r['ok'])
        self.assertIn('frozen workspace', r['error'])
        w = broker.call('write_file', {'path': 'docs/absent.txt', 'content': 'x',
                                     'expected_sha256': None})
        self.assertFalse(w['ok'])
        self.assertIn('allowed paths', w['error'])
        self.assertEqual(set(broker.files), {'docs/out.txt'})
        self.assertTrue(broker.call('list_files', {})['ok'])

    def test_cumulative_budget_charges_dispatched_calls_only(self):
        broker = self.broker(max_calls=3)
        with self.assertRaises(Refused):
            broker.call('made_up_tool', {})
        with self.assertRaises(Refused):
            broker.call('read_file', {'path': 'x' * (foundry_tools.MAX_BYTES + 1)})
        self.assertEqual(broker.count, 0)
        self.assertTrue(broker.call('list_files', {})['ok'])
        self.assertFalse(broker.call('read_file', {'path': 'docs/absent.txt'})['ok'])
        self.assertTrue(broker.call('list_files', {})['ok'])
        with self.assertRaises(Refused) as ctx:
            broker.call('list_files', {})
        self.assertIn('budget', str(ctx.exception))
        self.assertEqual(broker.count, 3)
        self.assertEqual(len(broker.receipts), 3)

    def test_uncertain_outcome_blocks_all_further_calls(self):
        broker = self.broker()

        @contextlib.contextmanager
        def fake_scope(stop, seconds):
            yield Path('/nonexistent-cgroup'), {'path': '/nonexistent-cgroup',
                                                'quiescent': True,
                                                'cleanup_error': None}

        killed = {'exit_code': None, 'reason': 'timeout', 'cleanup_error': None,
                  'local_quiescent': False, 'direct_process_exited': False,
                  'pipes_closed': True, 'elapsed_seconds': 0.5,
                  'stdout': b'', 'stderr': b'still running'}
        with mock.patch.object(foundry_tools, 'bwrap_argv', return_value=['bwrap', 'test-only']), \
             mock.patch.object(foundry_tools, 'tool_scope', fake_scope), \
             mock.patch.object(foundry_tools, 'execute', return_value=dict(killed)):
            result = broker.call('run_command', {'argv': ['sleep', '30'], 'seconds': 10})
        self.assertFalse(result['ok'])
        self.assertTrue(result['uncertain'])
        self.assertTrue(result['observation']['isolation']['quiescent'])
        self.assertTrue(broker.uncertain)
        for name, args in [('list_files', {}), ('read_file', {'path': 'x.txt'}),
                           ('write_file', {'path': 'docs/out.txt', 'content': 'x',
                                           'expected_sha256': None}),
                           ('run_command', {'argv': ['true'], 'seconds': 1})]:
            with self.subTest(tool=name):
                with self.assertRaises(Refused) as ctx:
                    broker.call(name, args)
                self.assertIn('uncertain', str(ctx.exception))
        self.assertEqual(len(broker.receipts), 1)
        self.assertTrue((Path(self._tmp.name) / 'run' / '1' / 'receipt.json').is_file())

    def test_run_command_validation_happens_before_sandbox(self):
        broker = self.broker(seconds=10)
        for argv in [[], ['x'] * 65, [''], ['ok', 'a\0b'], 'ls', [3]]:
            with self.subTest(argv=repr(argv)[:60]):
                r = broker.call('run_command', {'argv': argv, 'seconds': 5})
                self.assertFalse(r['ok'])
        for seconds in [0, 61, '30', None, 30]:
            with self.subTest(seconds=seconds):
                r = broker.call('run_command', {'argv': ['true'], 'seconds': seconds})
                self.assertFalse(r['ok'])
        self.assertFalse(broker.uncertain)
        self.assertTrue(broker.call('list_files', {})['ok'])

    def test_reserved_gate_path_refused_before_launch(self):
        broker = self.broker(files={GATE: 'print(1)'})
        r = broker.call('run_command', {'argv': ['true'], 'seconds': 5})
        self.assertFalse(r['ok'])
        self.assertIn('gate', r['error'])
        self.assertFalse(broker.uncertain)

    def test_run_command_stages_current_workspace(self):
        broker = self.broker(files={'a.txt': 'v1'})
        self.assertTrue(broker.call('write_file', {
            'path': 'docs/out.txt', 'content': 'v2', 'expected_sha256': None})['ok'])
        staged = {}

        @contextlib.contextmanager
        def fake_scope(stop, seconds):
            yield Path('/nonexistent-cgroup'), {'path': '/nonexistent-cgroup',
                                                'quiescent': True,
                                                'cleanup_error': None}

        def fake_execute(argv, cwd, env, timeout, output_limit, stop):
            staged['a.txt'] = (Path(cwd) / 'a.txt').read_text()
            staged['docs/out.txt'] = (Path(cwd) / 'docs' / 'out.txt').read_text()
            staged[GATE] = (Path(cwd) / GATE).read_text()
            staged['argv'] = list(argv)
            return {'exit_code': 0, 'reason': None, 'cleanup_error': None,
                    'local_quiescent': True, 'direct_process_exited': True,
                    'pipes_closed': True, 'elapsed_seconds': 0.01,
                    'stdout': b'hello', 'stderr': b''}

        with mock.patch.object(foundry_tools, 'bwrap_argv', return_value=['bwrap', 'test-only']), \
             mock.patch.object(foundry_tools, 'tool_scope', fake_scope), \
             mock.patch.object(foundry_tools, 'execute', fake_execute):
            r = broker.call('run_command', {'argv': ['cat', 'a.txt'], 'seconds': 15})
        self.assertTrue(r['ok'])
        self.assertEqual(staged['a.txt'], 'v1')
        self.assertEqual(staged['docs/out.txt'], 'v2')
        self.assertIn('subprocess.call', staged[GATE])
        self.assertIn("['cat', 'a.txt']", staged[GATE])
        self.assertIn('cgroup.procs', ' '.join(staged['argv']))
        self.assertEqual(r['value']['stdout'], 'hello')
        self.assertTrue(r['value']['local_quiescent'])
        self.assertEqual(r['value']['isolation']['path'], '/nonexistent-cgroup')
        self.assertEqual(broker.files['a.txt'], 'v1')

    def test_search_is_literal_and_bounded(self):
        body = 'hit line\n' * 150 + 'other\n'
        broker = self.broker(files={'a.txt': body, 'b.txt': 'x.hit.y\n'})
        r = broker.call('search', {'text': 'hit'})
        self.assertTrue(r['ok'])
        self.assertTrue(r['value']['truncated'])
        self.assertEqual(len(r['value']['matches']), 100)
        self.assertEqual(r['value']['matches'][0]['path'], 'a.txt')
        self.assertEqual(r['value']['matches'][0]['line'], 1)
        literal = broker.call('search', {'text': 'x.hit.y'})
        self.assertTrue(literal['ok'])
        self.assertEqual(len(literal['value']['matches']), 1)
        regex = broker.call('search', {'text': 'x.*y'})
        self.assertTrue(regex['ok'])
        self.assertEqual(regex['value']['matches'], [])

    def test_fetch_source_limited_to_reviewed_corpus(self):
        broker = self.broker(sources={'https://reviewed.example/spec':
                                    {'content': 'spec', 'sha256': 'x'}})
        ok = broker.call('fetch_source', {'url': 'https://reviewed.example/spec'})
        self.assertTrue(ok['ok'])
        self.assertEqual(ok['value']['content'], 'spec')
        denied = broker.call('fetch_source', {'url': 'https://other.example/x'})
        self.assertFalse(denied['ok'])
        self.assertIn('reviewed corpus', denied['error'])

    def test_stop_flag_refuses_before_any_dispatch(self):
        halted = self.broker(stop=lambda: True)
        with self.assertRaises(Refused):
            halted.call('list_files', {})
        self.assertEqual(halted.count, 0)

    @unittest.skipUnless(linux_tool_prereqs(),
                         'delegated cgroup controllers + bwrap required; '
                         'absent inside the offline sandbox')
    def test_run_command_real_linux_isolation(self):
        broker = self.broker(files={'data.txt': 'original'})
        tamper = broker.call('run_command', {'seconds': 30, 'argv': [
            'sh', '-c', 'echo tampered > data.txt; echo loot > created.txt; cat data.txt']})
        self.assertTrue(tamper['ok'], tamper)
        self.assertEqual(tamper['value']['exit_code'], 0)
        self.assertIn('tampered', tamper['value']['stdout'])
        self.assertTrue(tamper['value']['local_quiescent'])
        self.assertTrue(tamper['value']['isolation']['quiescent'])
        self.assertIsNone(tamper['value']['isolation']['cleanup_error'])
        self.assertEqual(broker.files, {'data.txt': 'original'})
        self.assertFalse(broker.call('read_file', {'path': 'created.txt'})['ok'])
        verify = broker.call('run_command', {'seconds': 30, 'argv': [
            'sh', '-c', ('cat data.txt; '
                        'test -e created.txt && echo persisted || echo ephemeral')]})
        self.assertTrue(verify['ok'])
        self.assertIn('original', verify['value']['stdout'])
        self.assertIn('ephemeral', verify['value']['stdout'])
        mounts = broker.call('run_command', {'seconds': 30, 'argv': [
            'sh', '-c', ('for d in /etc /home /root /sys/fs/cgroup /run; do '
                        'test -e $d && echo "exposed:$d"; done; '
                        'test -n "$HOME" && echo "exposed:home"; echo done')]})
        self.assertTrue(mounts['ok'])
        self.assertIn('done', mounts['value']['stdout'])
        self.assertNotIn('exposed:', mounts['value']['stdout'])
        net = broker.call('run_command', {'seconds': 30, 'argv': [
            'python3', '-c',
            ('import socket; s = socket.socket(); s.settimeout(3); '
            'print(s.connect_ex(("1.1.1.1", 443)))')]})
        self.assertTrue(net['ok'])
        self.assertNotEqual(net['value']['stdout'].strip(), '0')
        self.assertEqual(broker.files, {'data.txt': 'original'})


if __name__ == '__main__':
    unittest.main()
