import contextlib
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from tools.construction_swarm.capacity import JOB_BYTES, RESERVE_BYTES, slot_ceiling
from tools.construction_swarm.contracts import (
    Refused,
    digest,
    encoded,
    path,
    strict_json,
    validate_filing,
    validate_plan,
)
from tools.construction_swarm.ledger import Ledger, controller_lock
from tools.construction_swarm.process import execute
from tools.construction_swarm.runner import (
    devin_result,
    initialize,
    manifest,
    packet_for,
    provider_pool,
    reconcile,
    run,
)
from tools.construction_swarm.sandbox import isolated_execute, stage
from tools.construction_swarm.sandbox import test_staged as run_staged_test


def plan(count=2):
    return {'version': 1, 'run_id': 'fixture-run', 'parent_goal': 'goal-recursion-v2-execution-fabric',
            'authorization': 'Owner-approved provider-free conformance test.', 'source_commit': 'a' * 40,
            'deadline_utc': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            'route': {'backend': 'fixture', 'model': 'fixture', 'executable': sys.executable,
                      'sha256': digest(Path(sys.executable).read_bytes()),
                      'capacity_basis': 'Local fixture only; zero provider consumption.'},
            'limits': {'model_slots': 3, 'test_slots': 1, 'domain_slots': 2, 'max_dispatches': count + 5,
                       'max_attempts': 2, 'timeout_seconds': 15, 'output_bytes': 65536,
                       'input_bytes': 262144},
            'jobs': [{'id': f'job-{i}', 'domain': f'domain-{i // 8}', 'kind': 'research',
                      'brief': 'Analyze this bounded synthetic input.', 'inputs': ['README.md'],
                      'depends_on': [], 'allowed_paths': []} for i in range(count)]}


class Contracts(unittest.TestCase):
    def test_memory_reservations(self):
        self.assertEqual(slot_ceiling(RESERVE_BYTES - 1), 0)
        self.assertEqual(slot_ceiling(RESERVE_BYTES + JOB_BYTES * 3), 3)
    def test_duplicate_and_nonfinite_json(self):
        for value in [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}']:
            with self.assertRaises(Refused):
                strict_json(value)

    def test_bad_paths(self):
        for value in ['../x', '/etc/passwd', 'C:/x', 'a\\b', 'a/../x', 'a//b',
                      '.env', 'docs/.env', 'CON.txt', 'a./b', 'x:stream']:
            with self.subTest(value=value), self.assertRaises(Refused):
                path(value)

    def test_cycles_missing_and_duplicate_jobs(self):
        for change in ['cycle', 'missing', 'duplicate']:
            p = plan()
            if change == 'cycle':
                p['jobs'][0]['depends_on'] = ['job-1']
                p['jobs'][1]['depends_on'] = ['job-0']
            elif change == 'missing':
                p['jobs'][0]['depends_on'] = ['absent']
            else:
                p['jobs'][1]['id'] = 'job-0'
            with self.assertRaises(Refused):
                validate_plan(p)

    def test_route_and_limits(self):
        for section, field, value in [('route', 'model', 'different-model'),
                                       ('route', 'backend', 'shell'),
                                       ('limits', 'model_slots', 51),
                                       ('limits', 'domain_slots', True)]:
            p = plan()
            p[section][field] = value
            with self.assertRaises(Refused):
                validate_plan(p)

    def test_filing_cannot_claim_authority_or_invent_citations(self):
        p = plan()['jobs'][0]
        good = {'job_id': p['id'], 'summary': 'PASS claimed by worker', 'findings': [],
                'evidence': [], 'dissent': [], 'limitations': [], 'files': []}
        validate_filing(good, p, [])
        for field, value in [('accepted', True), ('evidence', ['fabricated']),
                             ('job_id', 'wrong'), ('files', [{'path': 'scripts/publish.sh', 'content': 'x'}])]:
            bad = dict(good)
            bad[field] = value
            with self.assertRaises(Refused):
                validate_filing(bad, p, [])


class DurableQueue(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.ledger = Ledger(self.root)
        self.p = plan(6)
        self.ledger.initialize(self.p)

    def tearDown(self):
        self.ledger.close()
        self.temp.cleanup()

    def test_os_lock_excludes_second_controller(self):
        with controller_lock(self.root), self.assertRaises(Refused), controller_lock(self.root):
            pass

    def test_domain_reservation_and_duplicate_claim(self):
        self.ledger.reserve('job-0')
        self.ledger.reserve('job-1')
        with self.assertRaises(Refused):
            self.ledger.reserve('job-2')
        with self.assertRaises(Refused):
            self.ledger.reserve('job-0')

    def test_recovery_holds_capacity_and_forbids_retry(self):
        self.ledger.reserve('job-0')
        self.ledger.reserve('job-1')
        self.ledger.recover()
        self.assertEqual([r['state'] for r in self.ledger.rows()][:2], ['unknown', 'unknown'])
        with self.assertRaises(Refused):
            self.ledger.retry('job-0', 'No receipt was received')
        with self.assertRaises(Refused):
            self.ledger.reserve('job-2')
        self.assertEqual(self.ledger.db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0], 2)

    def test_retry_preserves_history_and_exhausts(self):
        for attempt in [1, 2]:
            self.assertEqual(self.ledger.reserve('job-0'), attempt)
            self.ledger.finish('job-0', attempt, 'failed', {'exit_code': 1})
            if attempt == 1:
                self.ledger.retry('job-0', 'Corrected fixture input upstream')
        with self.assertRaises(Refused):
            self.ledger.retry('job-0', 'Attempt ceiling is exhausted')
        self.assertEqual(self.ledger.db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0], 2)

    def test_double_settlement_and_self_acceptance(self):
        self.ledger.reserve('job-0')
        self.ledger.finish('job-0', 1, 'returned', {'worker_claim': 'PASS'})
        self.assertEqual(self.ledger.rows()[0]['state'], 'returned')
        with self.assertRaises(Refused):
            self.ledger.finish('job-0', 1, 'returned', {})
        self.ledger.decision('job-0', False, 'Independent review found a counterexample')
        self.assertEqual(self.ledger.rows()[0]['state'], 'rejected')

    def test_stop_before_admission(self):
        (self.root / 'STOP').touch()
        with self.assertRaises(Refused):
            self.ledger.reserve('job-0')

    def test_cumulative_budget_not_refunded(self):
        # A fresh independent fixture uses a two-dispatch total ceiling.
        other = self.root / 'other'
        other.mkdir()
        ledger = Ledger(other)
        try:
            p = plan(3)
            p['limits']['max_dispatches'] = 2
            ledger.initialize(p)
            for job in ['job-0', 'job-1']:
                ledger.reserve(job)
                ledger.finish(job, 1, 'failed', {'known_local_failure': True})
            with self.assertRaises(Refused):
                ledger.reserve('job-2')
        finally:
            ledger.close()

    def test_expired_deadline(self):
        with patch('tools.construction_swarm.ledger.time.time', return_value=10**12), self.assertRaises(Refused):
            self.ledger.reserve('job-0')

    def test_status_reads_during_controller_ownership(self):
        with controller_lock(self.root):
            reader = Ledger.readonly(self.root)
            try:
                self.assertEqual(len(reader.rows()), 6)
            finally:
                reader.close()


class Integration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        (self.repo / 'README.md').write_text('Frozen public research input.', encoding='utf-8')
        self.git('add', 'README.md')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', 'fixture')
        self.commit = self.git('rev-parse', 'HEAD').decode().strip()

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.repo), *args], stderr=subprocess.PIPE)

    def make_run(self, count=2):
        p = plan(count)
        p['source_commit'] = self.commit
        root = self.base / 'run'
        initialize(self.repo, root, p)
        return root, p

    def test_fifty_jobs_and_synthesis_dependencies(self):
        p = plan(51)
        p['source_commit'] = self.commit
        p['limits'].update(model_slots=50, domain_slots=8)
        p['jobs'][-1].update(kind='synthesis', depends_on=[f'job-{i}' for i in range(50)])
        root = self.base / 'run'
        initialize(self.repo, root, p)
        rows = run(root)
        self.assertEqual(len(rows), 51)
        self.assertTrue(all(r['state'] == 'returned' for r in rows))
        again = run(root)
        self.assertTrue(all(r['attempts'] == 1 for r in again))
        ledger = Ledger(root)
        try:
            output = manifest(root, ledger)
            self.assertFalse(output['empirical_pass'])
            active = maximum = 0
            for row in ledger.db.execute('SELECT event FROM events ORDER BY seq'):
                if row[0] == 'reserved':
                    active += 1
                    maximum = max(maximum, active)
                elif row[0] == 'finished':
                    active -= 1
                self.assertLessEqual(active, 50)
            self.assertEqual(maximum, 50)
        finally:
            ledger.close()

    def test_snapshot_uses_commit_and_tamper_refuses(self):
        (self.repo / 'README.md').write_text('Uncommitted replacement')
        root, p = self.make_run()
        snapshot = strict_json((root / 'inputs.json').read_bytes())
        self.assertEqual(snapshot['README.md']['content'], 'Frozen public research input.')
        (root / 'inputs.json').write_bytes(b'{}')
        ledger = Ledger(root)
        try:
            with self.assertRaises(Refused):
                packet_for(root, p, p['jobs'][0], {})
        finally:
            ledger.close()

    def test_bad_packet_does_not_strand_other_dispatches(self):
        root, _ = self.make_run()
        def selective_packet(root, p, job, rows):
            if job['id'] == 'job-1':
                raise Refused('oversized dependency packet')
            return packet_for(root, p, job, rows)
        with patch('tools.construction_swarm.runner.packet_for', side_effect=selective_packet):
            rows = run(root)
        self.assertEqual([r['state'] for r in rows], ['returned', 'blocked'])
        self.assertEqual([r['attempts'] for r in rows], [1, 0])
        ledger = Ledger(root)
        try:
            self.assertIn('oversized', manifest(root, ledger)['jobs'][1]['blocker'])
        finally:
            ledger.close()

    def test_rejected_dependency_is_explicitly_blocked(self):
        p = plan(2)
        p['source_commit'] = self.commit
        p['jobs'][1]['depends_on'] = ['job-0']
        root = self.base / 'run'
        initialize(self.repo, root, p)
        ledger = Ledger(root)
        try:
            ledger.reserve('job-0')
            ledger.finish('job-0', 1, 'returned', {})
            ledger.decision('job-0', False, 'Independent rejection with evidence')
        finally:
            ledger.close()
        rows = run(root)
        self.assertEqual([r['state'] for r in rows], ['rejected', 'blocked'])
        self.assertEqual(rows[1]['attempts'], 0)

    @unittest.skipUnless(os.name == 'nt', 'Windows provider pool')
    def test_pool_retains_unknown_and_archives_completed_history(self):
        root, p = self.make_run(1)
        live = dict(p, route=dict(p['route'], backend='devin', model='swe-2-max'))
        ledger = Ledger(root)
        try:
            ledger.reserve('job-0')
            ledger.finish('job-0', 1, 'unknown', {})
        finally:
            ledger.close()
        other = self.base / 'other'
        initialize(self.repo, other, p)
        with patch.dict(os.environ, {'LOCALAPPDATA': str(self.base / 'appdata')}):
            with provider_pool(root, live) as held:
                self.assertEqual(held, 0)
            wide = dict(live, limits=dict(live['limits'], model_slots=50))
            with self.assertRaises(Refused), provider_pool(other, wide):
                pass
            with provider_pool(other, live) as held:
                self.assertEqual(held, 1)
                run(other)
            # A closed campaign's local database may be archived; unknown root stays.
            (other / 'ledger.sqlite').rename(other / 'ledger.archived')
            third = self.base / 'third'
            initialize(self.repo, third, p)
            with provider_pool(third, live) as held:
                self.assertEqual(held, 1)

    def test_filing_tamper_refuses_synthesis(self):
        root, _ = self.make_run()
        run(root)
        (root / 'attempts/job-0/1/filing.json').write_bytes(b'{}')
        ledger = Ledger(root)
        try:
            with self.assertRaises(Refused):
                manifest(root, ledger)
        finally:
            ledger.close()

    def test_development_stages_without_modifying_checkout(self):
        p = plan(1)
        p['source_commit'] = self.commit
        p['jobs'][0].update(kind='develop', allowed_paths=['experiments/answer.py'])
        root = self.base / 'run'
        initialize(self.repo, root, p)
        run(root)
        ledger = Ledger(root)
        try:
            staged = stage(root, ledger, 'job-0', self.base / 'stage')
            self.assertEqual((self.base / 'stage/experiments/answer.py').read_text(), 'answer = 42\n')
            self.assertFalse((self.repo / 'experiments/answer.py').exists())
            self.assertFalse(staged['accepted'])
            registered = root / 'stages' / (digest(encoded(staged)) + '.json')
            self.assertEqual(registered.read_bytes(), encoded(staged))
            forged = dict(staged, destination=str(root))
            with self.assertRaises(Refused), patch('tools.construction_swarm.sandbox.isolated_execute') as launch:
                run_staged_test(root, forged, 'experiments/answer.py')
            launch.assert_not_called()
            with self.assertRaises(Refused):
                stage(root / '..' / 'run', ledger, 'job-0', root / 'nested')
            self.assertEqual(self.git('status', '--porcelain'), b'')
            with self.assertRaises(Refused):
                stage(root, ledger, 'job-0', self.base / 'stage')
        finally:
            ledger.close()

    def test_positive_reconciliation_retains_original_receipt_and_charge(self):
        p = plan(1)
        p['source_commit'] = self.commit
        p['route'].update(backend='devin', model='swe-2-max')
        root = self.base / 'run'
        initialize(self.repo, root, p)
        ledger = Ledger(root)
        try:
            packet = packet_for(root, p, p['jobs'][0], {})
            ledger.reserve('job-0')
            original = {'job': 'job-0', 'attempt': 1, 'local_quiescent': True,
                        'exit_code': 0, 'reason': None,
                        'packet_sha256': digest(encoded(packet))}
            ledger.finish('job-0', 1, 'unknown', original)
            directory = root / 'attempts/job-0/1'
            directory.mkdir(parents=True)
            (directory / 'receipt.json').write_bytes(encoded(original))
            (directory / 'packet.json').write_bytes(encoded(packet))
            value = {'job_id': 'job-0', 'summary': 'Synthetic complete response', 'findings': [],
                     'evidence': [], 'dissent': [], 'limitations': [], 'files': []}
            export = {'agent': {'model_name': 'SWE-2 Max'},
                      'steps': [{'source': 'agent', 'message': encoded(value).decode()}]}
            (directory / 'export.json').write_bytes(encoded(export))
            interrupted = dict(original, reason='timeout', exit_code=125)
            (directory / 'receipt.json').write_bytes(encoded(interrupted))
            with self.assertRaises(Refused):
                reconcile(root, ledger, 'job-0')
            (directory / 'receipt.json').write_bytes(encoded(original))
            reconcile(root, ledger, 'job-0')
            self.assertEqual(ledger.rows()[0]['state'], 'returned')
            self.assertEqual((directory / 'receipt.json').read_bytes(), encoded(original))
            self.assertEqual(ledger.db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0], 1)
            with self.assertRaises(Refused):
                reconcile(root, ledger, 'job-0')
        finally:
            ledger.close()

    def test_model_substitution_and_tool_calls_refused(self):
        export_path = self.base / 'export.json'
        for data in [{'agent': {'model_name': 'SWE-2 High'}, 'steps': []},
                     {'agent': {'model_name': 'SWE-2 Max'},
                      'steps': [{'source': 'agent', 'tool_calls': [{'name': 'exec'}]}]}]:
            export_path.write_bytes(encoded(data))
            with self.assertRaises(Refused):
                devin_result(export_path)

    def test_source_symlink_refused(self):
        if os.name == 'nt':
            self.skipTest('symlink privilege not assumed')
        (self.repo / 'link').symlink_to('/etc/passwd')
        self.git('add', 'link')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                 'commit', '-qm', 'link')
        p = plan()
        p['source_commit'] = self.git('rev-parse', 'HEAD').decode().strip()
        p['jobs'][0]['inputs'] = ['link']
        with self.assertRaises(Refused):
            initialize(self.repo, self.base / 'run', p)


class ProcessTests(unittest.TestCase):
    def test_timeout_and_output_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            for script, timeout, reason in [('import time; time.sleep(20)', .15, 'timeout'),
                                           ('print("x"*100000)', 5, 'output-limit')]:
                result = execute([sys.executable, '-c', script], tmp, dict(os.environ), timeout, 2048)
                self.assertEqual(result['reason'], reason)
                self.assertLessEqual(len(result['stdout']) + len(result['stderr']), 2048)
                self.assertEqual(result['local_quiescent'], os.name == 'nt')
                self.assertTrue(result['direct_process_exited'])

    def test_stop_kills_child(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = 'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"]); time.sleep(30)'
            result = execute([sys.executable, '-c', script], tmp, dict(os.environ), .3, 2048)
            self.assertEqual(result['local_quiescent'], os.name == 'nt')
            self.assertTrue(result['direct_process_exited'])
            self.assertEqual(result['reason'], 'timeout')

    def test_cleanup_failure_retains_transport_and_scope_evidence(self):
        @contextlib.contextmanager
        def scope():
            yield {'path': '/unused-owned-scope', 'quiescent': False, 'cleanup_error': 'injected rmdir failure'}
        transport = {'stdout': b'evidence', 'stderr': b'', 'exit_code': 0,
                     'reason': None, 'direct_process_exited': True}
        with patch('tools.construction_swarm.sandbox.bwrap_argv', return_value=['/unused']), \
             patch('tools.construction_swarm.sandbox.test_cgroup', scope), \
             patch('tools.construction_swarm.sandbox.execute', return_value=transport):
            result = isolated_execute('.', 'probe.py', 1, 1024)
        self.assertEqual(result['stdout'], b'evidence')
        self.assertFalse(result['local_quiescent'])
        self.assertEqual(result['reason'], 'cgroup-cleanup-unknown')
        self.assertIn('rmdir', result['cgroup_observation']['cleanup_error'])

    @unittest.skipUnless(sys.platform == 'linux', 'Linux sandbox test')
    def test_real_bubblewrap_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'probe.py').write_text('''import os,socket
from pathlib import Path
assert not Path('/mnt/c').exists()
assert not Path('/mnt/d').exists()
assert not Path('/root').exists()
assert socket.if_nameindex() == [(1, 'lo')]
assert os.statvfs('/src').f_flag & os.ST_RDONLY
Path('/work/probe').write_text('ok')
print('isolation-pass')
''')
            result = isolated_execute(root, 'probe.py', 5, 65536)
            self.assertEqual(result['exit_code'], 0, result['stderr'])
            self.assertIn(b'isolation-pass', result['stdout'])
            self.assertTrue(result['cgroup_quiescent'])

    @unittest.skipUnless(sys.platform == 'linux', 'Linux cgroup test')
    def test_fork_limit_and_detached_child_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'probe.py').write_text('''import subprocess,sys,time
children=[]
try:
    for i in range(100):
        children.append(subprocess.Popen([sys.executable,'-c','import os,time;os.setsid();time.sleep(20)']))
except BlockingIOError:
    print('pids-limit-enforced', flush=True)
else:
    raise RuntimeError('pids limit absent')
''')
            result = isolated_execute(root, 'probe.py', 5, 65536)
            self.assertIn(b'pids-limit-enforced', result['stdout'])
            self.assertTrue(result['cgroup_quiescent'])


if __name__ == '__main__':
    unittest.main()
