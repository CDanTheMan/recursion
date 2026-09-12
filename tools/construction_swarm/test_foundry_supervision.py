"""Adversarial admission/live-observation tests; no provider or research execution."""
import contextlib
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from .contracts import Refused, digest, encoded
from .foundry import validate
from .foundry_supervision import (
    campaign_live,
    ceiling,
    progress_packet,
    validate_advice,
)
from .tests.test_swarm import plan as legacy_plan


def native_plan(version=3):
    p = legacy_plan()
    p.update(version=version, credentials='/synthetic/auth', sources={}, legacy_roots=[])
    p['route'].update(backend='devin-tools', model='swe-2-max')
    p['limits'].update(model_slots=200 if version == 3 else 100,
                       test_slots=4, output_bytes=8*1024**2,
                       timeout_seconds=28800 if version == 3 else 1200)
    p['deadline_utc'] = '2026-09-11T21:01:42Z'
    if version == 3:
        for job in p['jobs']:
            job['allowed_tools'] = ['list_files', 'read_file', 'search', 'run_command',
                                    'fetch_source']
            if job['kind'] == 'develop':
                job['allowed_tools'].append('write_file')
        p['campaign'] = {'start_utc': '2026-09-11T15:51:42Z',
                        'hard_deadline_utc': '2026-09-11T23:51:42Z',
                        'closeout_reserve_seconds': 10200,
                        'quota_path': '/var/lib/recursion-foundry/campaigns/synthetic/usage.json',
                        'quota_max_age_seconds': 1800, 'quota_reserve_percent': 8,
                        'max_supervision_dispatches': 100, 'pause_paths': ['/synthetic/PAUSE'],
                        'quota_reset_identities': {'codex-primary': 1789692198}}
    return p


class SupervisionTests(unittest.TestCase):
    def test_coordinator_rejects_missing_or_changed_external_plan(self):
        from .foundry_coordinator import reviewed_plan
        from .ledger import Ledger
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ledger = Ledger(root)
            ledger.initialize(native_plan())
            ledger.close()
            with self.assertRaises(OSError): reviewed_plan(root)
            p = native_plan()
            p['version'] = 2
            (root/'plan.json').write_bytes(encoded(p))
            with self.assertRaises(Refused): reviewed_plan(root)
            (root/'plan.json').write_bytes(encoded(native_plan()))
            self.assertEqual(reviewed_plan(root), native_plan())

    def test_long_worker_reaches_client_with_campaign_stop_predicate(self):
        from .contracts import timestamp
        from .foundry import run_one
        p = native_plan()
        job = p['jobs'][0]
        observed = []
        clock = [100.0]
        monitor = [True]

        def client(directory, route, credentials, packet, sources, group, seconds, stop):
            observed.append(seconds)
            self.assertGreater(seconds, 1200)
            clock[0] += 1201
            self.assertFalse(stop())
            monitor[0] = False
            self.assertTrue(stop())
            return {'synthetic': 'no inference'}, {}

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prefix = 'tools.construction_swarm.foundry.'
            with patch(prefix+'file_digest', return_value=p['route']['sha256']), \
                    patch(prefix+'workspace_files'), patch(prefix+'free_memory', return_value=30*1024**3), \
                    patch(prefix+'time.monotonic', side_effect=lambda: clock[0]), \
                    patch(prefix+'time.time', return_value=timestamp('2026-09-11T17:00:00Z')), \
                    patch(prefix+'devin_tools', side_effect=client):
                (root/'attempts'/job['id']).mkdir(parents=True)
                # Credentials need only a real empty fixture; its contents are never read.
                credential = root/'synthetic-auth'
                credential.write_bytes(b'')
                p['credentials'] = str(credential)
                state, _, _ = run_one(root, p, job, 1, {}, root/'synthetic-group',
                                      monitor=lambda: monitor[0])
            self.assertEqual(state, 'returned')
            self.assertEqual(len(observed), 1)

    def test_above100_reservations_keep_all_uncertain_capacity(self):
        from .foundry_wsl import native_holds
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            claims = root/'native-claims'
            claims.mkdir()
            claim = claims/'one.json'
            claim.write_bytes(encoded({'slots': 200}))
            self.assertEqual(native_holds(root), 200)
            claim.with_name('one.settled.json').write_bytes(encoded({
                'claim_sha256': digest(claim.read_bytes()), 'held': 62}))
            self.assertEqual(native_holds(root), 62)
            self.assertEqual(ceiling(native_plan()) - native_holds(root), 138)
            self.assertEqual(ceiling(native_plan(2)) - native_holds(root), 38)
            claim.with_name('one.settled.json').write_bytes(encoded({
                'claim_sha256': '0'*64, 'held': 0}))
            with self.assertRaises(Refused): native_holds(root)

    def test_live_advice_does_not_require_worker_controller_lock(self):
        from .foundry_coordinator import packet_for_report, synthesize
        from .ledger import Ledger, controller_lock
        manifest = {'run_id': 'synthetic', 'source_commit': '0'*40,
                    'jobs': [{'id': 'worker', 'state': 'running', 'attempts': 1}]}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'plan.json').write_bytes(encoded(native_plan()))
            ledger = Ledger(root)
            ledger.initialize(native_plan())
            ledger.close()
            runtime = root/'runtime'
            runtime.mkdir()
            for name in ('node', 'index.js'): (runtime/name).write_bytes(b'synthetic, never executed')
            credential = root/'synthetic-auth.json'
            credential.write_bytes(b'{}')
            packet = progress_packet(root, packet_for_report(manifest))
            answer = {'summary': 'No completed tools yet; do not infer a stall.', 'assessments': [{
                'id': 'worker', 'disposition': 'continue', 'reason': 'Await real evidence.',
                'evidence': [packet['records'][0]['progress_ref']]}]}
            events = [{'type': 'system', 'subtype': 'init', 'model': 'Cursor Grok 4.5 High'},
                      {'type': 'result', 'subtype': 'success', 'is_error': False,
                       'result': encoded(answer).decode()}]
            observation = {'quiescent': True, 'cleanup_error': None}

            @contextlib.contextmanager
            def scoped(*args):
                yield root/'synthetic-cgroup', observation

            outcome = {'exit_code': 0, 'reason': None, 'direct_process_exited': True,
                       'pipes_closed': True, 'stdout': b'\n'.join(encoded(e) for e in events),
                       'stderr': b''}
            prefix = 'tools.construction_swarm.foundry_coordinator.'
            with controller_lock(root), patch(prefix+'campaign_live', return_value=True), \
                    patch(prefix+'report', return_value=manifest), \
                    patch(prefix+'client_argv', return_value=['synthetic']), \
                    patch(prefix+'process_scope', scoped), \
                    patch(prefix+'execute_scoped', return_value=outcome):
                result = synthesize(root, 'cursor', runtime, credential, live_revision=0)
            self.assertEqual(result['state'], 'returned')
            self.assertFalse(result['accepted'])
            self.assertTrue((root/'supervision/0-cursor-0/reservation.json').is_file())
            self.assertFalse((root/'STOP').exists())

    def test_explicit_version_preserves_legacy_bounds_and_finite_campaign(self):
        validate(native_plan())
        validate(native_plan(2))
        for change in ('legacy-cap', 'legacy-time', 'new-cap', 'new-time', 'late', 'long-window'):
            p = native_plan(2 if change.startswith('legacy') else 3)
            if change == 'legacy-cap': p['limits']['model_slots'] = 101
            if change == 'legacy-time': p['limits']['timeout_seconds'] = 1201
            if change == 'new-cap': p['limits']['model_slots'] = 201
            if change == 'new-time': p['limits']['timeout_seconds'] = 28801
            if change == 'late': p['deadline_utc'] = '2026-09-11T21:01:43Z'
            if change == 'long-window': p['campaign']['hard_deadline_utc'] = '2026-09-12T23:51:42Z'
            with self.subTest(change=change), self.assertRaises(Refused): validate(p)
        self.assertEqual(ceiling(native_plan()), 200)
        self.assertEqual(ceiling(native_plan(2)), 100)

    def test_v3_requires_machine_enforced_job_tool_policy(self):
        for mutation in ('missing', 'duplicate', 'unknown', 'write-research', 'writable-without-write'):
            p = native_plan()
            job = p['jobs'][0]
            if mutation == 'missing':
                del job['allowed_tools']
            if mutation == 'duplicate':
                job['allowed_tools'].append(job['allowed_tools'][0])
            if mutation == 'unknown':
                job['allowed_tools'].append('native_exec')
            if mutation == 'write-research':
                job['allowed_tools'].append('write_file')
            if mutation == 'writable-without-write':
                job.update(kind='develop', allowed_paths=['tools/output.py'])
                job['allowed_tools'] = [name for name in job['allowed_tools']
                                        if name != 'write_file']
            with self.subTest(mutation=mutation), self.assertRaises(Refused):
                validate(p)
        tool_free = native_plan()
        tool_free['jobs'][0]['allowed_tools'] = []
        validate(tool_free)
        validate(native_plan(2))
        v2_with_policy = native_plan(2)
        v2_with_policy['jobs'][0]['allowed_tools'] = []
        with self.assertRaises(Refused):
            validate(v2_with_policy)

    def test_campaign_preparation_strips_then_restores_only_v3_tool_policy(self):
        from .foundry_prepare import version_one_jobs
        jobs = native_plan()['jobs']
        projected = version_one_jobs(jobs, campaign=True)
        self.assertTrue(all('allowed_tools' not in job for job in projected))
        self.assertTrue(all('allowed_tools' in job for job in jobs))
        self.assertEqual(version_one_jobs(jobs, campaign=False), jobs)

    def test_v3_packet_binds_plan_version_to_worker_tool_policy(self):
        from .foundry_client import worker_allowed_tools
        from .runner import packet_for
        p = native_plan()
        job = p['jobs'][0]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inputs = {'README.md': {'content': 'frozen', 'sha256': digest(b'frozen')}}
            data = encoded(inputs)
            (root/'inputs.json').write_bytes(data)
            (root/'inputs.sha256').write_text(digest(data))
            packet = packet_for(root, p, job, {})
        self.assertEqual(packet['plan_version'], 3)
        self.assertEqual(worker_allowed_tools(packet), tuple(job['allowed_tools']))

    def test_quota_stop_and_reserve_override_long_worker_window(self):
        from .contracts import timestamp
        p = native_plan()
        at = timestamp('2026-09-11T17:00:00Z')
        usage = {'checked_utc': '2026-09-11T17:00:00Z', 'reset_credits_used': 0, 'remaining_percent': 94,
                 'new_metered_spend': 0, 'binding_windows': [
                     {'name': 'codex-primary', 'used_percent': 6, 'remaining_percent': 94, 'resets_at': 1789692198}]}
        with patch.object(Path, 'read_bytes', return_value=encoded(usage)), \
                patch.object(Path, 'exists', return_value=False):
            self.assertTrue(campaign_live(p, at=at))
            self.assertFalse(campaign_live(p, at=at+1801))
            self.assertFalse(campaign_live(p, at=timestamp(p['deadline_utc'])))
            self.assertFalse(campaign_live(p, at=at-1))
        for mutation in ('spent', 'reset', 'inconsistent', 'empty', 'exhausted', 'renamed', 'next-reset', 'minimum'):
            bad = copy.deepcopy(usage)
            if mutation == 'spent': bad['new_metered_spend'] = 1
            if mutation == 'reset': bad['reset_credits_used'] = 1
            if mutation == 'inconsistent': bad['binding_windows'][0]['remaining_percent'] = 95
            if mutation == 'empty': bad['binding_windows'] = []
            if mutation == 'renamed': bad['binding_windows'][0]['name'] = 'omitted-original-window'
            if mutation == 'next-reset': bad['binding_windows'][0]['resets_at'] += 604800
            if mutation == 'minimum': bad['remaining_percent'] = 95
            if mutation == 'exhausted': bad['binding_windows'][0].update(used_percent=92, remaining_percent=8)
            with self.subTest(mutation=mutation), patch.object(Path, 'read_bytes', return_value=encoded(bad)), \
                    patch.object(Path, 'exists', return_value=False):
                self.assertFalse(campaign_live(p, at=at))
        with patch.object(Path, 'exists', return_value=True):
            self.assertFalse(campaign_live(p, at=at))
        with patch.object(Path, 'exists', return_value=False), patch.object(Path, 'read_bytes', side_effect=OSError):
            self.assertFalse(campaign_live(p, at=at))

    def test_partial_or_tampered_tools_are_not_completed_progress(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for n in (1, 2, 3):
                directory = root/'attempts/worker/1/tools'/str(n)
                directory.mkdir(parents=True)
                request = encoded({'name': 'read_file', 'arguments': {'path': 'tools/example.py'}})
                (directory/'request.json').write_bytes(request)
                if n != 2:
                    (directory/'receipt.json').write_bytes(encoded({
                        'request_sha256': digest(request) if n == 1 else '0'*64,
                        'result': {'content': 'untrusted source excerpt'}}))
            packet = progress_packet(root, {'records': [{'id': 'worker', 'state': 'running', 'attempts': 1}]})
            row = packet['records'][0]
            self.assertEqual(row['progress']['completed_tools'], 1)
            self.assertEqual(row['progress']['pending_or_unreadable'], 2)
            self.assertTrue(row['progress']['liveness_is_not_scientific_progress'])
            advice = {'summary': 'Inspect bounded progress.', 'assessments': [{
                'id': 'worker', 'disposition': 'inspect', 'reason': 'Two incomplete observations.',
                'evidence': [row['progress_ref']]}]}
            validate_advice(advice, packet)
            for state in ('unknown', 'blocked', 'failed'):
                row['state'] = state
                with self.assertRaises(Refused): validate_advice(advice, packet)
            row['state'] = 'running'
            advice['assessments'][0]['disposition'] = 'accept'
            with self.assertRaises(Refused): validate_advice(advice, packet)
            advice['assessments'][0].update(disposition='continue', evidence=[])
            with self.assertRaises(Refused): validate_advice(advice, packet)


if __name__ == '__main__':
    unittest.main()
