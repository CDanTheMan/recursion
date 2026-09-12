"""Owner settlement of quiescent unknown holds; no provider launch."""
import tempfile
import unittest
from pathlib import Path

from .contracts import Refused, digest, encoded
from .foundry_settle import classify, remaining_holds, settle_job, settle_root
from .ledger import Ledger
from .tests.test_swarm import plan


def write_unknown(root, job_id='job-0', *, exit_code=0, reason=None, error='Refused: foreign/native tool attempted'):
    ledger = Ledger(root)
    ledger.initialize(plan(1))
    number = ledger.reserve(job_id)
    directory = root / 'attempts' / job_id / str(number)
    directory.mkdir(parents=True)
    receipt = {'job': job_id, 'attempt': number, 'launch_entered': True, 'error': error, 'state': 'unknown'}
    transport = {'exit_code': exit_code, 'reason': reason, 'local_quiescent': True,
                 'broker_errors': [], 'direct_process_exited': True}
    (directory / 'receipt.json').write_bytes(encoded(receipt))
    (directory / 'transport.json').write_bytes(encoded(transport))
    ledger.finish(job_id, number, 'unknown', receipt)
    return ledger, directory


class SettleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_classify_policy_cancel_and_nonzero(self):
        receipt = {'launch_entered': True, 'error': 'Refused: foreign/native tool attempted'}
        self.assertEqual(classify(receipt, {'exit_code': 0, 'reason': None, 'local_quiescent': True}),
                         'failed')
        self.assertEqual(classify(receipt, {'exit_code': -9, 'reason': 'cancelled', 'local_quiescent': True}),
                         'cancelled')
        self.assertEqual(classify(receipt, {'exit_code': 1, 'reason': None, 'local_quiescent': True}),
                         'failed')
        self.assertIsNone(classify(receipt, {'exit_code': 0, 'reason': None, 'local_quiescent': False}))
        self.assertIsNone(classify({'launch_entered': False}, {'exit_code': 1, 'local_quiescent': True}))

    def test_policy_unknown_becomes_failed_and_releases_hold(self):
        ledger, _ = write_unknown(self.root)
        try:
            self.assertEqual(remaining_holds(self.root), 1)
            settle_job(self.root, ledger, 'job-0',
                       'Lucas 2026-09-12 owner settlement; dispatch charges retained')
            self.assertEqual(ledger.rows()[0]['state'], 'failed')
            self.assertEqual(remaining_holds(self.root), 0)
        finally:
            ledger.close()

    def test_cancelled_quiescent_becomes_cancelled(self):
        ledger, _ = write_unknown(self.root, exit_code=-9, reason='cancelled',
                                 error='Refused: native Linux client did not complete normally')
        try:
            settle_job(self.root, ledger, 'job-0',
                       'Lucas 2026-09-12 owner settlement; dispatch charges retained')
            self.assertEqual(ledger.rows()[0]['state'], 'cancelled')
            self.assertEqual(remaining_holds(self.root), 0)
        finally:
            ledger.close()

    def test_non_quiescent_stays_unknown(self):
        ledger, directory = write_unknown(self.root)
        (directory / 'transport.json').write_bytes(encoded({
            'exit_code': 0, 'reason': None, 'local_quiescent': False}))
        try:
            with self.assertRaisesRegex(Refused, 'no terminal cleanup'):
                settle_job(self.root, ledger, 'job-0',
                           'Lucas 2026-09-12 owner settlement; dispatch charges retained')
            self.assertEqual(ledger.rows()[0]['state'], 'unknown')
        finally:
            ledger.close()

    def test_windows_settled_held_is_rewritten(self):
        ledger, _ = write_unknown(self.root)
        ledger.close()
        admission = self.root / 'admission'
        admission.mkdir()
        claim = admission / 'abc.json'
        claim.write_bytes(encoded({'root': str(self.root), 'slots': 8}))
        settled = admission / 'abc.settled.json'
        settled.write_bytes(encoded({'claim_sha256': digest(claim.read_bytes()),
                                    'held': 8, 'native_run': str(self.root)}))
        report = settle_root(self.root, 'Lucas 2026-09-12 owner settlement; dispatch charges retained',
                             admission=admission)
        self.assertEqual(report['remaining_holds'], 0)
        self.assertEqual(strict_json_held(settled), 0)


def strict_json_held(path):
    from .contracts import strict_json
    return strict_json(path.read_bytes())['held']
