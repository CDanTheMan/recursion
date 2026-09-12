"""Account for inherited planning fixture calls around one admitted research entry.

This is a draft execution wrapper. It does not admit itself. The native parent
must reserve the fixture-call limit in addition to every other research unit,
bind all source bytes and execute this inside the existing offline tool sandbox.
Original reducers and historical evidence are unchanged. The profile hook counts
calls before entering planning kernel genesis/admit, including import-time work;
this is not a claim to count all Python operations or unique model states.
"""
import argparse
import contextlib
import ctypes
import hashlib
import io
import json
import math
import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KERNEL = str(ROOT / 'scripts/v3/planning/replay/kernel.py')


class BoundedText(io.TextIOBase):
    def __init__(self, limit):
        self.limit, self.used, self.parts = limit, 0, []
        self.overflowed = False

    def write(self, value):
        size = len(value.encode('utf-8'))
        if self.used + size > self.limit:
            self.overflowed = True
            raise ValueError('research payload exceeds approved stdout bound')
        self.used += size
        self.parts.append(value)
        return len(value)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result

    def reject(value):
        raise ValueError('nonfinite JSON constant: ' + value)

    def finite(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError('nonfinite JSON number')
        return result
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject, parse_float=finite)


def fatal(reason, terminate=os._exit, write=os.write):
    try:
        write(2, ('research-accounting-refusal: ' + reason + '\n').encode())
    finally:
        terminate(86)


def single_process():
    """Add a kernel-enforced no-new-thread/child/exec filter inside the sandbox.

    This narrows the disposable command process only. Accounting still assumes
    the exact reviewed source closure; it is not a general Python security proof.
    """
    library = ctypes.CDLL('libseccomp.so.2')
    library.seccomp_init.argtypes = [ctypes.c_uint32]
    library.seccomp_init.restype = ctypes.c_void_p
    library.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    library.seccomp_syscall_resolve_name.restype = ctypes.c_int
    library.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    library.seccomp_rule_add.restype = ctypes.c_int
    library.seccomp_load.argtypes = [ctypes.c_void_p]
    library.seccomp_load.restype = ctypes.c_int
    library.seccomp_release.argtypes = [ctypes.c_void_p]
    context = library.seccomp_init(0x7fff0000)  # SCMP_ACT_ALLOW
    if not context:
        raise ValueError('seccomp context unavailable')
    try:
        for name in (b'clone', b'clone3', b'fork', b'vfork', b'execve', b'execveat'):
            number = library.seccomp_syscall_resolve_name(name)
            if number < 0 or library.seccomp_rule_add(context, 0x80000000, number, 0):
                raise ValueError('no-child filter unavailable')
        if library.seccomp_load(context):
            raise ValueError('no-child filter not installed')
    finally:
        library.seccomp_release(context)


def mounted_sources():
    """Bind the actual writable execution copy to the tool's read-only input mount."""
    source = Path('/src')
    expected = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in source.rglob('*') if p.is_file()}
    actual = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in ROOT.rglob('*') if p.is_file()}
    if expected != actual or not expected:
        fatal('execution copy differs from read-only mounted sources')
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture-limit', type=int, required=True)
    parser.add_argument('--target', required=True)
    parser.add_argument('--payload-limit', type=int, default=1000000)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not 1 <= args.fixture_limit <= 32768 or not 1 <= args.payload_limit <= 1000000:
        raise ValueError('finite approved fixture/output limits required')
    target = (ROOT / args.target).resolve(strict=True)
    if not target.is_relative_to(ROOT / 'experiments/v3/swarm-research-20260911-155142'):
        raise ValueError('new campaign entry required')
    if target == Path(__file__).resolve() or not target.is_file():
        raise ValueError('distinct regular research entry required')
    before_sources = mounted_sources()
    single_process()
    counts = {'genesis': 0, 'admit': 0}

    def account(frame, event, arg):
        if event == 'call' and frame.f_code.co_name in counts:
            if frame.f_code.co_filename != KERNEL:
                fatal('noncanonical planning fixture entry')
            if sum(counts.values()) >= args.fixture_limit:
                fatal('fixture reservation exhausted before kernel call')
            counts[frame.f_code.co_name] += 1

    sys.setprofile(account)

    def guard(event, arguments):
        if event == 'open':
            mode, flags = arguments[1], arguments[2]
            if (isinstance(mode, str) and any(x in mode for x in 'wax+')) \
                    or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
                fatal('research file writes are not admitted')
        if event in {'os.remove', 'os.rename', 'os.rmdir', 'os.mkdir', 'os.link', 'os.symlink', 'os.truncate'}:
            fatal('research filesystem mutation is not admitted')
        if event in {'sys.setprofile', 'sys.settrace', 'os.system', 'os.posix_spawn', 'os.fork', 'os.forkpty'} \
                or event.startswith(('socket.', 'subprocess.', 'os.exec', 'os.spawn')):
            fatal('research execution operation refused: ' + event)
    sys.addaudithook(guard)
    output = BoundedText(args.payload_limit)
    arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
    sys.argv = [str(target), *arguments]
    with contextlib.redirect_stdout(output):
        runpy.run_path(str(target), run_name='__main__')
    if output.overflowed or sys.getprofile() is not account:
        raise ValueError('fixture accounting interrupted')
    if mounted_sources() != before_sources:
        fatal('executed sources changed')
    result = {'payload': strict_json(''.join(output.parts)), 'fixture_accounting': {
        'unit': 'planning-kernel-genesis-or-admit-call', 'limit': args.fixture_limit,
        'calls': sum(counts.values()), 'by_function': counts,
        'kernel_sha256': hashlib.sha256(Path(KERNEL).read_bytes()).hexdigest(),
        'target_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'executed_source_hashes': before_sources,
        'all_research_units_counted_by_this_hook': False}}
    raw = json.dumps(result, sort_keys=True, separators=(',', ':'), allow_nan=False)
    if len(raw.encode()) > 1048575:
        raise ValueError('wrapped stdout exceeds shared tool output bound')
    print(raw)


if __name__ == '__main__':
    main()
