"""Retained transport and tool evidence must survive independent reporting."""
import tempfile
import unittest
from pathlib import Path

from .contracts import Refused, digest, encoded
from .foundry import verify_attempt_artifacts


class RetainedEvidenceTests(unittest.TestCase):
    def test_missing_or_modified_evidence_cannot_advance_to_coordinator(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files = {'packet.json': b'{}', 'transport.json': b'{"exit_code":0}',
                     'client-output/export.json': b'{"agent":{"model_name":"SWE-2 Max"}}',
                     'tools/1/request.json': encoded({'name': 'read_file', 'arguments': {'path': 'x'}})}
            files['tools/1/receipt.json'] = encoded({'request_sha256': digest(files['tools/1/request.json'])})
            for name, data in files.items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            receipt = {'packet_sha256': digest(files['packet.json']),
                       'transport_sha256': digest(files['transport.json']),
                       'export_sha256': digest(files['client-output/export.json']),
                       'tool_receipts': [{'number': 1, 'name': 'read_file',
                                          'sha256': digest(files['tools/1/receipt.json'])}]}
            verify_attempt_artifacts(root, receipt)
            for name, original in files.items():
                with self.subTest(file=name):
                    target = root / name
                    target.write_bytes(b'changed')
                    with self.assertRaises(Refused):
                        verify_attempt_artifacts(root, receipt)
                    target.unlink()
                    with self.assertRaises(OSError):
                        verify_attempt_artifacts(root, receipt)
                    target.write_bytes(original)
