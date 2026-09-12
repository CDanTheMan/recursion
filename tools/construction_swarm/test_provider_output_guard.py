"""Synthetic gates for the Linux provider-output capture guard."""
import hashlib
import os
import socket
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from .provider_output_guard import Refused, capture

LINUX = sys.platform == 'linux'


def _write(directory, name, data):
    path = os.path.join(directory, name)
    with open(path, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return path


@unittest.skipUnless(LINUX, 'descriptor capture requires Linux')
class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = self.temp.name

    def collect(self, names, **bounds):
        bounds.setdefault('file_bytes', 4096)
        bounds.setdefault('aggregate_bytes', 262144)
        bounds.setdefault('entries', 8)
        return capture(self.root, names, **bounds)

    def test_exact_boundary_and_immutable_result(self):
        payload = b'x' * 4096
        _write(self.root, 'a.bin', payload)
        _write(self.root, 'empty.bin', b'')
        result = self.collect({'a.bin', 'empty.bin'}, aggregate_bytes=4096,
                              entries=2)
        self.assertEqual(set(result), {'a.bin', 'empty.bin'})
        self.assertEqual(result['a.bin'].content, payload)
        self.assertEqual(result['a.bin'].size, 4096)
        self.assertEqual(result['a.bin'].sha256,
                         hashlib.sha256(payload).hexdigest())
        self.assertEqual(result['empty.bin'].content, b'')
        with self.assertRaises(TypeError):
            result['a.bin'] = None

    def test_one_byte_over_per_file_bound_refused(self):
        _write(self.root, 'a.bin', b'x' * 4097)
        with self.assertRaisesRegex(Refused, 'logical size overflow'):
            self.collect({'a.bin'})

    def test_aggregate_overflow_refused(self):
        _write(self.root, 'a.bin', b'x' * 4096)
        _write(self.root, 'b.bin', b'y' * 4096)
        with self.assertRaisesRegex(Refused, 'aggregate bytes overflow'):
            self.collect({'a.bin', 'b.bin'}, aggregate_bytes=5000)

    def test_entry_count_overflow_refused(self):
        _write(self.root, 'a.bin', b'x')
        _write(self.root, 'b.bin', b'x')
        with self.assertRaisesRegex(Refused, 'entry count overflow'):
            self.collect({'a.bin'}, entries=1)

    def test_inventory_classification(self):
        cases = [
            ('extra', lambda d: _write(d, 'extra.bin', b'x'),
             {'a.bin'}, 'extra entry'),
            ('hidden', lambda d: _write(d, '.env', b'x'),
             {'a.bin'}, 'hidden entry'),
            ('noncanonical', lambda d: _write(d, 'bad name.txt', b'x'),
             {'a.bin'}, 'noncanonical name'),
            ('nested', lambda d: os.mkdir(os.path.join(d, 'sub')),
             {'a.bin'}, 'nested entry'),
            ('case-aliased', lambda d: None,
             {'A.bin'}, 'case-aliased name'),
            ('missing', lambda d: None,
             {'a.bin', 'gone.bin'}, 'missing entries: gone.bin'),
        ]
        for label, setup, names, pattern in cases:
            with self.subTest(case=label), tempfile.TemporaryDirectory() as d:
                _write(d, 'a.bin', b'x')
                setup(d)
                with self.assertRaisesRegex(Refused, pattern):
                    capture(d, names, file_bytes=4096,
                            aggregate_bytes=262144, entries=8)

    def test_symlink_refused(self):
        _write(self.root, 'a.bin', b'x')
        os.symlink('a.bin', os.path.join(self.root, 'b.bin'))
        os.symlink('gone', os.path.join(self.root, 'c.bin'))
        with self.assertRaisesRegex(Refused, 'symlink'):
            self.collect({'a.bin', 'b.bin', 'c.bin'})

    def test_hardlink_refused(self):
        _write(self.root, 'a.bin', b'x')
        os.link(os.path.join(self.root, 'a.bin'),
                os.path.join(self.root, 'b.bin'))
        with self.assertRaisesRegex(Refused, 'single-link'):
            self.collect({'a.bin', 'b.bin'})

    def test_directory_entry_refused(self):
        os.mkdir(os.path.join(self.root, 'a.bin'))
        with self.assertRaisesRegex(Refused, 'regular file'):
            self.collect({'a.bin'})

    def test_fifo_refused_without_blocking(self):
        os.mkfifo(os.path.join(self.root, 'a.bin'))
        started = time.monotonic()
        with self.assertRaisesRegex(Refused, 'regular file'):
            self.collect({'a.bin'})
        self.assertLess(time.monotonic() - started, 10)

    def test_socket_entry_refused(self):
        server = socket.socket(socket.AF_UNIX)
        self.addCleanup(server.close)
        server.bind(os.path.join(self.root, 'a.bin'))
        with self.assertRaisesRegex(Refused, 'cannot open entry'):
            self.collect({'a.bin'})

    def test_sparse_file_refused(self):
        path = os.path.join(self.root, 'a.bin')
        with open(path, 'wb') as stream:
            stream.write(b'x')
            stream.seek(20000)
            stream.write(b'y')
            stream.flush()
            os.fsync(stream.fileno())
        with self.assertRaisesRegex(Refused, 'sparse'):
            self.collect({'a.bin'}, file_bytes=32768)

    def test_allocated_size_overflow_refused(self):
        _write(self.root, 'a.bin', b'x' * 100)
        with self.assertRaisesRegex(Refused, 'allocated size overflow'):
            self.collect({'a.bin'}, file_bytes=200)

    def test_metadata_mutation_race_refused(self):
        _write(self.root, 'a.bin', b'x' * 100)
        real_fstat = os.fstat
        calls = []

        def drifted(fd):
            st = real_fstat(fd)
            calls.append(fd)
            if len(calls) == 1:
                return st
            return os.stat_result(
                (st.st_mode, st.st_ino, st.st_dev, st.st_nlink, st.st_uid,
                 st.st_gid, st.st_size, int(st.st_atime), int(st.st_mtime),
                 int(st.st_ctime)),
                {'st_atime_ns': st.st_atime_ns,
                 'st_mtime_ns': st.st_mtime_ns + 1,
                 'st_ctime_ns': st.st_ctime_ns})

        with patch('os.fstat', drifted):
            with self.assertRaisesRegex(Refused, 'changed during read'):
                self.collect({'a.bin'})

    def test_growth_during_read_race_refused(self):
        _write(self.root, 'a.bin', b'x' * 100)
        real_read = os.read
        fed = []

        def extra(fd, count):
            chunk = real_read(fd, count)
            if not chunk and not fed:
                fed.append(True)
                return b'Z'
            return chunk

        with patch('os.read', extra):
            with self.assertRaisesRegex(Refused, 'size/content mismatch'):
                self.collect({'a.bin'})

    def test_vanishing_entry_race_refused(self):
        _write(self.root, 'a.bin', b'x')
        real_open = os.open

        def vanish(path, flags, *args, **kwargs):
            if kwargs.get('dir_fd') is not None:
                raise FileNotFoundError(2, 'vanished between scan and open')
            return real_open(path, flags, *args, **kwargs)

        with patch('os.open', vanish):
            with self.assertRaisesRegex(Refused, 'cannot open entry'):
                self.collect({'a.bin'})

    def test_explicit_bounds_and_canonical_names_required(self):
        for bound in [{'file_bytes': 0}, {'file_bytes': -1},
                      {'aggregate_bytes': 0}, {'entries': 0}]:
            kwargs = {'file_bytes': 4096, 'aggregate_bytes': 4096,
                      'entries': 1}
            kwargs.update(bound)
            with self.assertRaisesRegex(Refused, 'positive'):
                capture(self.root, {'a.bin'}, **kwargs)
        with self.assertRaisesRegex(Refused, 'filename set'):
            capture(self.root, ['a.bin'], file_bytes=4096,
                    aggregate_bytes=4096, entries=1)
        with self.assertRaisesRegex(Refused, 'noncanonical'):
            capture(self.root, {'sub/a.bin'}, file_bytes=4096,
                    aggregate_bytes=4096, entries=1)
        with self.assertRaisesRegex(Refused, 'case-aliased'):
            capture(self.root, {'a.bin', 'A.BIN'}, file_bytes=4096,
                    aggregate_bytes=4096, entries=2)
        with self.assertRaisesRegex(Refused, 'entry bound'):
            capture(self.root, {'a.bin', 'b.bin'}, file_bytes=4096,
                    aggregate_bytes=4096, entries=1)

    def test_unpinnable_directory_refused(self):
        target = _write(self.root, 'real.bin', b'x')
        link = os.path.join(self.root, 'linked')
        os.symlink(self.root, link)
        with self.assertRaisesRegex(Refused, 'cannot pin'):
            capture(link, {'real.bin'}, file_bytes=4096,
                    aggregate_bytes=4096, entries=1)
        with self.assertRaisesRegex(Refused, 'cannot pin'):
            capture(target, {'x'}, file_bytes=4096, aggregate_bytes=4096,
                    entries=1)


class PlatformTests(unittest.TestCase):
    def test_refuses_non_linux_at_call_time(self):
        with patch.object(sys, 'platform', 'win32'):
            with self.assertRaisesRegex(Refused, 'requires Linux'):
                capture('/does/not/matter', {'a.bin'}, file_bytes=1,
                        aggregate_bytes=1, entries=1)


if __name__ == '__main__':
    unittest.main()
