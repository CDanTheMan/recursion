"""Namespace boundary tests for the frozen replay-store reader.

Imports the supplied frozen reader.py/fixture.py via importlib, builds
disposable TemporaryDirectory namespaces, and asserts both accepted
replay/gap outcomes and exact refusal reasons. Linux sandbox only; no
network, subprocess, fsync or power-loss claims.
"""
import importlib.util
import os
import pathlib
import tempfile
import unittest

SRC = pathlib.Path(__file__).resolve().parents[1] / 'replay-store-evidence'


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SRC / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fixture = _load('fixture')
reader = _load('reader')

BUDGET = {'observations': 0, 'bytes': 0}
MAX_OBSERVATIONS = 50
MAX_BYTES = 1 << 20


def observe(store, trust):
    BUDGET['observations'] += 1
    assert BUDGET['observations'] <= MAX_OBSERVATIONS
    assert BUDGET['bytes'] <= MAX_BYTES
    return reader.observe(store, trust)


def put(path, raw):
    BUDGET['bytes'] += len(raw)
    pathlib.Path(path).write_bytes(raw)


def selected_dir(layout, g):
    return 'active' if layout == 'in-place' else 'g' + str(g)


def build_store(root, layout, g, unit, attempt, request_event=1, files=None, pointer=None):
    files = fixture.artifacts(g, unit) if files is None else dict(files)
    pointer = fixture.current(layout, g, files) if pointer is None else pointer
    directory = pathlib.Path(root) / selected_dir(layout, g)
    directory.mkdir(parents=True, exist_ok=True)
    for name in sorted(files):
        put(directory / name, files[name])
    raw_current = fixture.encode(pointer)
    put(pathlib.Path(root) / 'CURRENT.json', raw_current)
    trust = fixture.trust(layout, g, unit, attempt, 'nonce-' + str(attempt), files=files,
                          request_event=request_event)
    trust['current_sha256'] = fixture.digest(raw_current)
    trust['manifest_sha256'] = fixture.digest(files['manifest.json'])
    return trust


class ReplayReaderNamespaceTests(unittest.TestCase):
    _attempt = 0

    def _store(self, layout='in-place', g=1, unit='event', request_event=1):
        type(self)._attempt += 1
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        trust = build_store(tmp.name, layout, g, unit, self._attempt, request_event)
        res = observe(tmp.name, trust)
        self.assertIn(res['status'], ('replay', 'gap'), res)
        return tmp.name, trust, res

    def _refused(self, store, trust, reason):
        res = observe(store, trust)
        self.assertEqual(res['status'], 'blocked', res)
        self.assertEqual(res['reason'], reason, res)
        return res

    def test_baseline_replay(self):
        for layout in ('in-place', 'staged-generation'):
            for unit in ('event', 'utf8-byte'):
                with self.subTest(layout=layout, unit=unit):
                    _, _, res = self._store(layout=layout, g=1, unit=unit)
                    self.assertEqual(res['status'], 'replay', res)
                    self.assertEqual(res['generation'], 1, res)
                    self.assertEqual(res['cursor_unit'], unit, res)
                    self.assertEqual(res['derived_floor_event'], 0, res)
                    self.assertEqual(res['snapshot_event_cursor'], 1, res)
                    self.assertEqual([e['id'] for e in res['replay_events']], [2, 3], res)

    def test_baseline_gap(self):
        for layout in ('in-place', 'staged-generation'):
            for unit in ('event', 'utf8-byte'):
                with self.subTest(layout=layout, unit=unit):
                    _, _, res = self._store(layout=layout, g=2, unit=unit)
                    self.assertEqual(res['status'], 'gap', res)
                    self.assertEqual(res['generation'], 2, res)
                    self.assertEqual(res['cursor_unit'], unit, res)
                    self.assertEqual(res['derived_floor_event'], 2, res)
                    self.assertEqual(res['snapshot_event_cursor'], 2, res)
                    self.assertEqual([e['id'] for e in res['replay_events']], [3], res)

    def test_byte_cursor_inside_multibyte_refuses(self):
        store, trust, _ = self._store(layout='staged-generation', g=1, unit='utf8-byte')
        mutated = dict(trust, request_cursor=2)
        self._refused(store, mutated, 'cursor-inside-payload-or-outside-catalog')

    def test_wrong_generation_refuses(self):
        store, trust, _ = self._store(layout='staged-generation', g=2, unit='event')
        pointer = {'version': 1, 'generation': 1, 'directory': 'g1',
                   'manifest_sha256': trust['manifest_sha256']}
        raw = fixture.encode(pointer)
        put(pathlib.Path(store) / 'CURRENT.json', raw)
        mutated = dict(trust, current_sha256=fixture.digest(raw))
        self._refused(store, mutated, 'selected-generation-mismatch')

    def test_tampered_member_refuses(self):
        store, trust, _ = self._store(layout='in-place', g=1, unit='event')
        target = pathlib.Path(store) / 'active' / 'event2.json'
        raw = bytearray(target.read_bytes())
        raw[40] ^= 1
        put(target, bytes(raw))
        self._refused(store, trust, 'member-digest-mismatch')

    def test_extra_member_refuses(self):
        store, trust, _ = self._store(layout='staged-generation', g=2, unit='event')
        put(pathlib.Path(store) / 'g2' / 'extra.json', b'{}')
        self._refused(store, trust, 'unexpected-namespace-member')

    def test_duplicate_manifest_key_refuses(self):
        store, trust, _ = self._store(layout='in-place', g=1, unit='event')
        directory = pathlib.Path(store) / 'active'
        dup = b'{"version":1,' + (directory / 'manifest.json').read_bytes()[1:]
        put(directory / 'manifest.json', dup)
        files = fixture.artifacts(1, 'event')
        files['manifest.json'] = dup
        pointer = fixture.current('in-place', 1, files)
        put(pathlib.Path(store) / 'CURRENT.json', fixture.encode(pointer))
        type(self)._attempt += 1
        mutated = fixture.trust('in-place', 1, 'event', self._attempt,
                                'nonce-' + str(self._attempt), files=files)
        self._refused(store, mutated, 'duplicate-json-key')

    def test_event_symlink_refuses(self):
        store, trust, _ = self._store(layout='in-place', g=1, unit='event')
        directory = pathlib.Path(store) / 'active'
        (directory / 'event2.json').unlink()
        os.symlink('event3.json', directory / 'event2.json')
        self._refused(store, trust, 'nonregular-artifact')

    def test_generation_directory_symlink_refuses(self):
        store, trust, _ = self._store(layout='staged-generation', g=2, unit='event')
        root = pathlib.Path(store)
        (root / 'g2').rename(root / 'g2-real')
        os.symlink('g2-real', root / 'g2')
        self._refused(store, trust, 'nonregular-namespace')

    def test_missing_snapshot_refuses(self):
        store, trust, _ = self._store(layout='in-place', g=1, unit='event')
        (pathlib.Path(store) / 'active' / 'snapshot.json').unlink()
        self._refused(store, trust, 'namespace-membership-mismatch')

    def test_pointer_pin_mismatch_refuses(self):
        store, trust, _ = self._store(layout='staged-generation', g=2, unit='utf8-byte')
        pointer = {'version': 1, 'generation': 2, 'directory': 'g2',
                   'manifest_sha256': '0' * 64}
        put(pathlib.Path(store) / 'CURRENT.json', fixture.encode(pointer))
        self._refused(store, trust, 'current-pin-mismatch')

    def test_bool_cursor_refuses(self):
        store, trust, _ = self._store(layout='in-place', g=1, unit='event')
        mutated = dict(trust, request_cursor=True)
        self._refused(store, mutated, 'request-type')


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ReplayReaderNamespaceTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    ok = (result.wasSuccessful() and not result.skipped
          and BUDGET['observations'] <= MAX_OBSERVATIONS and BUDGET['bytes'] <= MAX_BYTES)
    print('observations=%d fixture_bytes=%d' % (BUDGET['observations'], BUDGET['bytes']))
    if ok:
        print('V3_REPLAY_READER_PASS')
    raise SystemExit(0 if ok else 1)
