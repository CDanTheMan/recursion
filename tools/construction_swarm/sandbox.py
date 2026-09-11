"""Linux-only, offline tests of proposed code in a fresh Bubblewrap namespace.

No provider credential or host mount is exposed. Tests run one at a time while the
controller owns its lock; test_slots is an upper bound, not a concurrency promise.
"""
import os
from pathlib import Path
import shutil
import sys
import time
import uuid
import contextlib

from .contracts import digest, encoded, path, require
from .ledger import controller_lock, Ledger
from .process import execute
from .runner import read_inputs, verified_filing, put


def stage(root, ledger, job_id, destination):
    rows = {row['id']: row for row in ledger.rows()}
    require(job_id in rows and rows[job_id]['state'] in {'returned', 'accepted'}, 'no returned proposal')
    row = rows[job_id]
    filing = verified_filing(root, row)
    job = next(j for j in ledger.plan['jobs'] if j['id'] == job_id)
    destination = Path(destination).absolute()
    require(not destination.exists(), 'new staging directory required')
    require(not destination.resolve().is_relative_to(root), 'stage must be outside controller state')
    inputs = read_inputs(root)
    files = {name: inputs[name]['content'] for name in job['inputs']}
    for proposed in filing['files']:
        require(proposed['path'] in job['allowed_paths'], 'proposal widened scope')
        files[proposed['path']] = proposed['content']
    destination.mkdir(parents=True)
    records = {}
    for name, content in files.items():
        target = destination / path(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        data = content.encode()
        put(target, data)
        records[name] = digest(data)
    return {'job': job_id, 'filing_sha256': row['result_hash'], 'files': records,
            'accepted': False, 'destination': str(destination.resolve())}


def bwrap_argv(source, entry, timeout, output_bytes):
    require(sys.platform == 'linux', 'isolated tests require Linux/WSL2')
    bwrap = shutil.which('bwrap')
    require(bwrap, 'bubblewrap missing')
    source = Path(source).resolve(strict=True)
    entry = path(entry)
    require((source / entry).is_file(), 'test entry missing')
    for item in source.rglob('*'):
        require(not item.is_symlink(), 'symlink in test source')
    # Limit address space, CPU and generated file size inside the sandbox. Its
    # workspace is a disposable tmpfs; no host writable directory is bound.
    code = ('import resource,runpy,sys; '
            'resource.setrlimit(resource.RLIMIT_AS,(2147483648,2147483648)); '
            f'resource.setrlimit(resource.RLIMIT_CPU,({int(timeout)},{int(timeout)})); '
            f'resource.setrlimit(resource.RLIMIT_FSIZE,({output_bytes},{output_bytes})); '
            'sys.path.insert(0,"/src"); '
            f'runpy.run_path({"/src/" + entry!r},run_name="__main__")')
    return [bwrap, '--unshare-all', '--die-with-parent', '--new-session', '--cap-drop', 'ALL',
            '--clearenv', '--setenv', 'PATH', '/usr/bin:/bin',
            '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64', '--symlink', 'usr/bin', '/bin',
            '--proc', '/proc', '--dev', '/dev', '--size', '67108864', '--tmpfs', '/tmp',
            '--size', '67108864', '--tmpfs', '/work',
            '--ro-bind', str(source), '/src', '--chdir', '/work',
            '/usr/bin/python3', '-B', '-c', code]


@contextlib.contextmanager
def test_cgroup():
    """Own a new cgroup only; never enable controllers or alter another scope."""
    require(sys.platform == 'linux', 'Linux cgroup required')
    base = Path('/sys/fs/cgroup')
    require({'memory', 'pids', 'cpu'} <= set((base / 'cgroup.subtree_control').read_text().split()),
            'memory/pids/cpu controllers must already be delegated')
    group = base / ('recursion-construction-' + uuid.uuid4().hex)
    group.mkdir()
    try:
        for name, value in [('memory.max', '2147483648'), ('memory.swap.max', '0'),
                            ('pids.max', '64'), ('cpu.max', '200000 100000')]:
            (group / name).write_text(value)
            require((group / name).read_text().strip() == value, f'{name} not enforced')
        require((group / 'cgroup.kill').exists(), 'cgroup.kill required')
        yield group
    finally:
        if (group / 'cgroup.kill').exists():
            (group / 'cgroup.kill').write_text('1')
        until = time.monotonic() + 5
        while time.monotonic() < until and 'populated 1' in (group / 'cgroup.events').read_text():
            time.sleep(.025)
        require('populated 0' in (group / 'cgroup.events').read_text(), 'owned cgroup not quiescent')
        group.rmdir()


def isolated_execute(source, entry, seconds, output_limit, stop=lambda: False):
    argv = bwrap_argv(source, entry, seconds, output_limit)
    with test_cgroup() as group:
        # Trusted launcher joins its scope before any proposed code can execute.
        wrapper = ('import os,sys; from pathlib import Path; '
                   'Path(sys.argv[1]).write_text(str(os.getpid())); '
                   'os.execv(sys.argv[2],sys.argv[2:])')
        launched = ['/usr/bin/python3', '-I', '-c', wrapper, str(group / 'cgroup.procs'), *argv]
        result = execute(launched, source, {}, seconds, output_limit, stop)
        result['cgroup'] = {'memory_bytes': 2147483648, 'pids': 64, 'cpu_cores': 2,
                            'swap_bytes': 0, 'tmpfs_bytes_each': 67108864}
    result['cgroup_quiescent'] = True
    return result


def test_staged(root, staging_manifest, entry):
    root = Path(root).resolve(strict=True)
    with controller_lock(root):
        ledger = Ledger(root)
        try:
            plan = ledger.plan
            source = Path(staging_manifest['destination']).resolve(strict=True)
            expected = staging_manifest['files']
            actual = {}
            for file in source.rglob('*'):
                require(not file.is_symlink(), 'stage symlink')
                if file.is_file():
                    actual[file.relative_to(source).as_posix()] = digest(file.read_bytes())
            require(actual == expected, 'stage differs from frozen manifest')
            require(entry in expected, 'test entry not in frozen source')
            require(not (root / 'STOP').exists(), 'STOP requested')
            from .contracts import timestamp
            seconds = min(plan['limits']['timeout_seconds'], timestamp(plan['deadline_utc']) - time.time())
            require(seconds >= 1, 'deadline reached')
            from .capacity import admit_host
            admit_host(root)
            result = isolated_execute(source, entry, seconds, plan['limits']['output_bytes'],
                                      stop=lambda: (root / 'STOP').exists())
            receipt_dir = root / 'tests' / uuid.uuid4().hex
            receipt_dir.mkdir(parents=True)
            for field in ['stdout', 'stderr']:
                put(receipt_dir / (field + '.txt'), result.pop(field))
            result.update(stage_sha256=digest(encoded(staging_manifest)), entry=entry,
                          evidence_class='offline-linux-bubblewrap', empirical_acceptance=False,
                          limits='cgroup aggregate memory/pids/CPU; bounded tmpfs; wall/output')
            put(receipt_dir / 'receipt.json', encoded(result))
            with ledger.db:
                ledger.event('isolated-test', {'receipt': str(receipt_dir / 'receipt.json')})
            return result
        finally:
            ledger.close()
