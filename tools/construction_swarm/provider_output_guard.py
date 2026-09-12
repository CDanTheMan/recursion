"""Qualified capture of an exact provider output directory (Linux only).

A writable provider output directory can carry symlink, FIFO or
disk-amplification content. capture() pins the directory by descriptor,
verifies the exact declared inventory, opens each entry relative to that
descriptor without following links, bounds logical and allocated size, and
returns immutable bytes only after the complete aggregate validates. The
module stays importable on unsupported platforms and refuses at call time.
"""
from __future__ import annotations

import errno
import hashlib
import os
import re
import stat
import sys
from types import MappingProxyType
from typing import NamedTuple

_CANONICAL = re.compile(r'[A-Za-z0-9_.-]{1,255}')
_STABLE_FIELDS = ('st_ino', 'st_dev', 'st_mode', 'st_size',
                  'st_mtime_ns', 'st_ctime_ns', 'st_nlink')


class Refused(ValueError):
    """The provider output failed qualification."""


def require(value, reason):
    if not value:
        raise Refused(reason)


class Captured(NamedTuple):
    content: bytes
    size: int
    sha256: str


def _canonical(name):
    return (type(name) is str and _CANONICAL.fullmatch(name) is not None
            and not name.startswith('.') and not name.endswith(('.', ' ')))


def _read_entry(name, dir_fd, file_bytes):
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
    try:
        fd = os.open(name, flags, dir_fd=dir_fd)
    except OSError as exc:
        reason = ('symlink entry refused' if exc.errno == errno.ELOOP
                  else 'cannot open entry')
        raise Refused(f'{reason}: {name}') from exc
    try:
        before = os.fstat(fd)
        require(stat.S_ISREG(before.st_mode), f'not a regular file: {name}')
        require(before.st_nlink == 1, f'not a single-link file: {name}')
        require(before.st_size <= file_bytes, f'logical size overflow: {name}')
        allocated = before.st_blocks * 512
        require(allocated <= file_bytes, f'allocated size overflow: {name}')
        require(before.st_size <= allocated, f'sparse file refused: {name}')
        chunks = []
        remaining = file_bytes + 1
        while remaining:
            chunk = os.read(fd, min(remaining, 1048576))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b''.join(chunks)
        require(len(data) <= file_bytes, f'read overflow: {name}')
        after = os.fstat(fd)
        for field in _STABLE_FIELDS:
            require(getattr(after, field) == getattr(before, field),
                    f'{name} changed during read')
        require(len(data) == after.st_size,
                f'size/content mismatch: {name}')
        return data
    finally:
        os.close(fd)


def capture(directory, names, *, file_bytes, aggregate_bytes, entries):
    """Capture the exact declared inventory or refuse.

    ``names`` is the explicit canonical filename set; ``file_bytes``,
    ``aggregate_bytes`` and ``entries`` are positive bounds with no
    defaults. Returns a read-only mapping of ``Captured`` bytes/size/SHA-256
    only after the complete aggregate validates.
    """
    if sys.platform != 'linux':
        raise Refused('provider output capture requires Linux')
    require(type(file_bytes) is int and file_bytes >= 1,
            'positive per-file byte bound required')
    require(type(aggregate_bytes) is int and aggregate_bytes >= 1,
            'positive aggregate byte bound required')
    require(type(entries) is int and entries >= 1,
            'positive entry-count bound required')
    require(type(names) in (set, frozenset),
            'explicit filename set required')
    require(all(_canonical(name) for name in names),
            'noncanonical expected name')
    casefolds = {name.casefold() for name in names}
    require(len(casefolds) == len(names), 'case-aliased expected names')
    require(len(names) <= entries, 'expected inventory exceeds entry bound')
    path = os.fspath(directory)
    require(type(path) is str, 'directory path must be text')
    try:
        dir_fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY
                         | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as exc:
        raise Refused(
            f'cannot pin output directory: {exc.strerror or exc}') from exc
    try:
        observed = os.listdir(dir_fd)
        require(len(observed) <= entries, 'entry count overflow')
        extras = {}
        for name in observed:
            if name in names:
                continue
            reason = 'extra entry'
            if name.startswith('.'):
                reason = 'hidden entry'
            elif not _canonical(name):
                reason = 'noncanonical name'
            elif name.casefold() in casefolds:
                reason = 'case-aliased name'
            else:
                try:
                    mode = os.stat(name, dir_fd=dir_fd,
                                   follow_symlinks=False).st_mode
                    if stat.S_ISDIR(mode):
                        reason = 'nested entry'
                except OSError:
                    pass
            extras[name] = reason
        if extras:
            name = sorted(extras)[0]
            raise Refused(f'{extras[name]}: {name}')
        missing = sorted(names - set(observed))
        require(not missing, f'missing entries: {",".join(missing)}')
        results = {}
        total = 0
        for name in sorted(names):
            data = _read_entry(name, dir_fd, file_bytes)
            total += len(data)
            require(total <= aggregate_bytes, 'aggregate bytes overflow')
            results[name] = Captured(
                data, len(data), hashlib.sha256(data).hexdigest())
        return MappingProxyType(results)
    finally:
        os.close(dir_fd)
