"""Linux-only, offline tests of proposed code in a fresh Bubblewrap namespace.

No provider credential or host mount is exposed. Tests run one at a time while the
controller owns its lock; test_slots is an upper bound, not a concurrency promise.
"""
import contextlib
import shutil
import sys
import tempfile
import time
import uuid
from pathlib import Path

from .contracts import Refused, digest, encoded, path, require
from .ledger import Ledger, controller_lock
from .process import execute
from .runner import put, read_inputs, verified_filing


def stage(root, ledger, job_id, destination):
    root = Path(root).resolve(strict=True)
    require(root == ledger.root, 'controller root mismatch')
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
    result = {'job': job_id, 'filing_sha256': row['result_hash'], 'files': records,
              'accepted': False, 'destination': str(destination.resolve())}
    registry = root / 'stages'
    registry.mkdir(exist_ok=True)
    put(registry / (digest(encoded(result)) + '.json'), encoded(result))
    return result


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
    import os
    pool = Path(tempfile.gettempdir()) / f'recursion-construction-tests-{os.getuid()}'
    pool.mkdir(exist_ok=True)
    with controller_lock(pool), _test_cgroup_scope() as observation:
        yield observation


@contextlib.contextmanager
def _test_cgroup_scope():
    base = Path('/sys/fs/cgroup')
    require({'memory', 'pids', 'cpu'} <= set((base / 'cgroup.subtree_control').read_text().split()),
            'memory/pids/cpu controllers must already be delegated')
    require(not any(base.glob('recursion-construction-*')), 'unreconciled test cgroup exists; no new test admitted')
    group = base / ('recursion-construction-' + uuid.uuid4().hex)
    group.mkdir()
    observation = {'path': str(group), 'quiescent': False, 'cleanup_error': None}
    try:
        for name, value in [('memory.max', '2147483648'), ('memory.swap.max', '0'),
                            ('pids.max', '64'), ('cpu.max', '200000 100000')]:
            (group / name).write_text(value)
            require((group / name).read_text().strip() == value, f'{name} not enforced')
        require((group / 'cgroup.kill').exists(), 'cgroup.kill required')
        yield observation
    finally:
        try:
            if (group / 'cgroup.kill').exists():
                (group / 'cgroup.kill').write_text('1')
            until = time.monotonic() + 5
            while time.monotonic() < until and 'populated 1' in (group / 'cgroup.events').read_text():
                time.sleep(.025)
            require('populated 0' in (group / 'cgroup.events').read_text(), 'owned cgroup not quiescent')
            group.rmdir()
            observation['quiescent'] = True
        except (OSError, Refused) as exc:
            observation['cleanup_error'] = str(exc)


def isolated_execute(source, entry, seconds, output_limit, stop=lambda: False):
    argv = bwrap_argv(source, entry, seconds, output_limit)
    with test_cgroup() as observation:
        group = Path(observation['path'])
        # Trusted launcher joins its scope before any proposed code can execute.
        wrapper = ('import os,sys; from pathlib import Path; '
                   'Path(sys.argv[1]).write_text(str(os.getpid())); '
                   'os.execv(sys.argv[2],sys.argv[2:])')
        launched = ['/usr/bin/python3', '-I', '-c', wrapper, str(group / 'cgroup.procs'), *argv]
        try:
            result = execute(launched, source, {}, seconds, output_limit, stop)
        except Exception as exc:  # noqa: BLE001 -- retain cleanup observation and failed launch evidence
            result = {'stdout': b'', 'stderr': b'', 'exit_code': None,
                      'reason': 'transport-exception', 'error': f'{type(exc).__name__}: {exc}',
                      'direct_process_exited': False, 'local_quiescent': False}
        result['cgroup'] = {'memory_bytes': 2147483648, 'pids': 64, 'cpu_cores': 2,
                            'swap_bytes': 0, 'tmpfs_bytes_each': 67108864}
    result['cgroup_observation'] = observation
    result['cgroup_quiescent'] = observation['quiescent']
    result['local_quiescent'] = observation['quiescent'] and result['direct_process_exited']
    if not observation['quiescent']:
        result['reason'] = 'cgroup-cleanup-unknown'
    return result


def test_staged(root, staging_manifest, entry):
    root = Path(root).resolve(strict=True)
    with controller_lock(root):
        ledger = Ledger(root)
        try:
            plan = ledger.plan
            registered = root / 'stages' / (digest(encoded(staging_manifest)) + '.json')
            require(registered.is_file() and registered.read_bytes() == encoded(staging_manifest),
                    'unregistered staging manifest')
            row = next((r for r in ledger.rows() if r['id'] == staging_manifest['job']), None)
            require(row and row['state'] in {'returned', 'accepted'} and
                    row['result_hash'] == staging_manifest['filing_sha256'], 'stage/filing binding mismatch')
            verified_filing(root, row)
            source = Path(staging_manifest['destination']).resolve(strict=True)
            require(not source.is_relative_to(root), 'test source exposes controller state')
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
