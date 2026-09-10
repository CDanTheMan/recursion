"""Campaign-only admission; historical authority, reducers and receipts stay immutable."""
import datetime as dt
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
NAME = 'eight-hour-research-20260910-01a08a22'
DOC = 'docs/v3/construction/' + NAME + '/'
CODE = 'experiments/v3/' + NAME + '/'
BASE = 'f5f0519c2c2357c110a198461bf19c4081c45ad1'
START = dt.datetime.fromisoformat('2026-09-10T07:05:20Z')
END = dt.datetime.fromisoformat('2026-09-10T15:05:20Z')
B7DOC = 'docs/v3/construction/cut-source-overnight-20260908/batch-07/'

def require(value, message):
    if not value:
        raise ValueError(message)

def git(*args, root=ROOT):
    return subprocess.check_output(['git', *args], cwd=root, timeout=30)

def now(): return dt.datetime.now(dt.timezone.utc)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
def size(path): return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file())

COMMON = Path(git('rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip())
CACHE = COMMON / 'research-attestations' / NAME
OLD = COMMON / 'research-attestations/cut-source-overnight'
B7 = COMMON / 'research-attestations/batch-07-20260910'
spec = importlib.util.spec_from_file_location('unchanged_owned_job', ROOT / 'experiments/v3/cut-source-overnight/run_packet.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)

def live():
    require(START <= now() < END, 'immutable eight-hour deadline')
    require(not (ROOT / 'state/PAUSE').exists() and not (COMMON.parent / 'state/PAUSE').exists(), 'PAUSE')
    require('status: active' in (ROOT / 'state/goals/goal-recursion-v2-execution-fabric.md').read_text(), 'active parent')
    usage = read(CACHE / 'usage.json')
    require(0 <= (now() - dt.datetime.fromisoformat(usage['checked_at'])).total_seconds() < 900, 'fresh quota telemetry')
    windows = usage['binding_windows']
    require(windows and all(0 <= w['used_percent'] < 100 and w['remaining_percent'] == 100 - w['used_percent'] for w in windows), 'usable included quota')
    require(usage['remaining_percent'] == min(w['remaining_percent'] for w in windows), 'binding quota minimum')
    require(usage['reset_credits_used'] == usage['new_metered_spend'] == 0, 'included allowance only')
    require(all(now().timestamp() < w['resets_at'] for w in windows), 'no post-reset continuation')
    require({w['name']: w['resets_at'] for w in windows} == read(CACHE / 'activation.json')['quota_reset_identities'], 'unchanged quota reset identities')
    return usage

def scope(candidate):
    usage = live()
    require(git('rev-parse', 'HEAD').decode().strip() == candidate, 'exact committed candidate')
    require(not git('status', '--porcelain', '--untracked-files=all').strip(), 'clean source')
    require(git('branch', '--show-current').decode().strip() == 'codex/' + NAME, 'own review branch')
    git('merge-base', '--is-ancestor', BASE, candidate)
    changed = git('diff', '--name-only', BASE, candidate).decode().splitlines()
    require(changed and all(p.startswith((DOC, CODE)) for p in changed), 'explicit two-tree write allowlist')
    require(not git('diff', '--name-only', '--diff-filter=D', BASE, candidate).strip(), 'no historical deletion')
    charter = read(ROOT / DOC / 'charter.json')
    require(charter == read(CACHE / 'activation.json')['charter'], 'immutable campaign charter')
    require(charter['started_at'] == START.isoformat().replace('+00:00', 'Z') and charter['deadline_utc'] == END.isoformat().replace('+00:00', 'Z'), 'immutable launch clock')
    require(charter['settings'] == {'model': 'gpt-6-astra', 'reasoning': 'high', 'speed': 'standard', 'change_settings': False}, 'selected settings preserved')
    return usage

def policy(candidate):
    p = read(CACHE / 'policy.json')
    approval = read(CACHE / ('method-' + candidate + '.json'))
    require(approval['candidate'] == candidate and approval['policy_sha256'] == sha((CACHE / 'policy.json').read_bytes()), 'exact policy/candidate review')
    require(approval['status'] == 'APPROVED_FOR_EXECUTION' and len(approval['reviews']) == 2, 'two prospective independent reviews')
    reviewers = set()
    for row in approval['reviews']:
        path = (CACHE / row['path']).resolve()
        require(path.is_relative_to(CACHE) and sha(path.read_bytes()) == row['sha256'], 'bound review bytes')
        r = read(path)
        require(r['candidate'] == candidate and r['status'] == 'APPROVE_FOR_EXECUTION', 'prospective approval')
        require(r['policy_sha256'] == approval['policy_sha256'], 'reviewed policy')
        reviewers.add(r['reviewer'])
    require(len(reviewers) == 2, 'independent same-model reviewers')
    require(p['inherited_charge'] == 756966 and p['ceiling'] >= p['inherited_charge'], 'preserved inherited charge')
    require(p['finalization_reserve_seconds'] >= 4500 and p['quota_reserve_percent'] > 0, 'explicit rolling finalization reserve')
    return p

def capacity(candidate, final=False):
    usage, p = scope(candidate), policy(candidate)
    require((END - now()).total_seconds() > (605 if final else p['finalization_reserve_seconds'] + 605), 'time for execution and outstanding finalization')
    require(final or usage['remaining_percent'] > p['quota_reserve_percent'], 'rolling quota finalization reserve')
    ram, disk = helper.free_memory(), shutil.disk_usage(ROOT).free
    require(ram > 3221225472 and disk > 1073741824, 'host RAM/disk reserve')
    return {'usage': usage, 'free_ram_bytes': ram, 'free_disk_bytes': disk, 'policy_sha256': sha((CACHE / 'policy.json').read_bytes())}

def acquire():
    owned = []
    try:
        for name in ('heavy-gate.lock', 'model.lock'):
            p = OLD / name
            value = json.dumps({'pid': os.getpid(), 'campaign': NAME, 'started_at': now().isoformat()})
            fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, 'w') as f: f.write(value)
            owned.append((p, value))
        return owned
    except BaseException:
        release(owned)
        raise

def release(owned):
    errors = []
    for path, value in reversed(owned):
        try:
            require(path.read_text() == value, 'lock ownership changed')
            path.unlink()
        except BaseException as e: errors.append(repr(e))
    require(not errors, 'owned lock cleanup: ' + repr(errors))

def ledger():
    folder = CACHE / 'reservations'
    folder.mkdir(exist_ok=True)
    rows = sorted((read(p) for p in folder.glob('*.json')), key=lambda r: r['ordinal'])
    total = 756966
    for i, r in enumerate(rows):
        require(r['ordinal'] == i and r['previous_total'] == total and r['refundable'] is False, 'append-only reservation chain')
        require(type(r['states']) is int and r['states'] >= 0, 'finite nonnegative reservation')
        total += r['states']
        require(r['new_total'] == total, 'reservation arithmetic')
    return rows, total

def charge(candidate, directory, label, states, final=False):
    p = policy(candidate)
    rows, total = ledger()
    require(type(states) is int and states >= 0, 'finite precharge')
    require(total + states + (0 if final else p['outstanding_gate_state_reserve']) <= p['ceiling'], 'cumulative budget and outstanding gates')
    identity = directory.relative_to(CACHE).as_posix() + '/' + label
    require(all(r['identity'] != identity for r in rows), 'no reused or refunded reservation')
    row = dict(ordinal=len(rows), identity=identity, candidate=candidate, at=now().isoformat(), states=states,
               previous_total=total, new_total=total + states, refundable=False, policy_sha256=sha((CACHE / 'policy.json').read_bytes()))
    path = CACHE / 'reservations' / (str(len(rows)).zfill(6) + '.json')
    with path.open('x', encoding='utf-8') as f: f.write(json.dumps(row, indent=2) + '\n')
    return row

def historical():
    completion = B7 / 'completion.json'
    require(sha(completion.read_bytes()) == '3afa7e5df84281a609e0bdddc92f92034076c488e28d3b07e127711b108d0ad4', 'sealed Batch07 completion')
    c = read(completion)
    rows = read(ROOT / B7DOC / 'historical-closure.json')
    counts = {}
    for row in rows:
        path, base = (COMMON / row['path']).resolve(), (COMMON / row['base']).resolve()
        require(path.is_relative_to(COMMON) and base.is_relative_to(COMMON), 'historical root containment')
        require(sha(path.read_bytes()) == row['sha256'], 'historical closure binding')
        entries = read(path)[row['key']]
        require(len(entries) == row['count'], 'historical cardinality')
        for name, expected in entries.items():
            target = (base / name).resolve()
            require(target.is_relative_to(base) and sha(target.read_bytes()) == expected, 'preserved history: ' + name)
        counts[row['path']] = len(entries)
    # Original completion has two maps beyond the later closing-map list.
    original = read(OLD / '89ea6390774c4ef9b5c3727ad2715c57f12af90a/completion.json')
    for key, base in [('all_external_files_before_completion', OLD / '89ea6390774c4ef9b5c3727ad2715c57f12af90a'), ('parent_external_files', OLD)]:
        entries = original[key]
        for name, expected in entries.items():
            target = (base / name).resolve()
            require(target.is_relative_to(base) and sha(target.read_bytes()) == expected, 'original historical map')
        counts[key] = len(entries)
    for name, expected in c['files'].items():
        target = (B7 / name).resolve()
        require(target.is_relative_to(B7) and sha(target.read_bytes()) == expected, 'Batch07 file map: ' + name)
    seal = B7 / c['seal_receipt']
    require(sha(seal.read_bytes()) == c['seal_receipt_sha256'] == '6be72ddb931f5bed2509cb66f886a94f1db952bce40bb973b7f7f95f15f527fd', 'separate Batch07 seal')
    require(read(seal)['status'] == 'COMPLETION_SEAL_PASS' and c['source_family_reserved_states'] == 756966, 'completed inherited evidence')
    counts['batch07-completion'] = len(c['files'])
    return counts

def sources(candidate):
    manifest = read(ROOT / B7DOC / 'manifest.json')
    inherited = {r['path'] for r in manifest['inputs']} | set(manifest['sources'])
    changed = set(git('diff', '--name-only', BASE, candidate).decode().splitlines())
    require(len(inherited) == 394 and not inherited & changed, 'complete immutable Batch07 source closure')
    return inherited, changed

def snapshot(candidate, directory):
    inherited, changed = sources(candidate)
    result = {}
    for i, name in enumerate(sorted(inherited | changed)):
        require(now() < END, 'snapshot deadline')
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), 'source containment')
        raw, blob = path.read_bytes(), git('show', candidate + ':' + name)
        require(raw.replace(b'\r\n', b'\n') == blob.replace(b'\r\n', b'\n'), 'working/committed source equality')
        if name in inherited:
            require(blob == git('show', BASE + ':' + name), 'unchanged historical input')
        target = directory / 'source' / (str(i).zfill(4) + '.bin.gz')
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(gzip.compress(raw, compresslevel=6, mtime=0))
        result[name] = dict(git_blob_sha256=sha(blob), working_sha256=sha(raw), snapshot_file=target.relative_to(directory).as_posix(), snapshot_codec='gzip')
    return result

def command(candidate, args, root, directory, label, final=False):
    host = capacity(candidate, final)
    receipt = dict(candidate=candidate, label=label, command=args, root=str(root), source_commit=git('rev-parse', 'HEAD', root=root).decode().strip(),
                   started_at=now().isoformat(), capacity=host, status='ADMITTED_BEFORE_EXECUTION', maximum_seconds=600, maximum_memory_bytes=2147483648, maximum_artifact_bytes=268435456)
    write(directory / (label + '-admission.json'), receipt)
    job, child, errors = None, None, []
    begin, sampled = time.monotonic(), 0
    try:
        job = helper.OwnedJob(2147483648)
        with (directory / (label + '.log')).open('wb') as log:
            child = job.launch(args, cwd=root, stdout=log, stderr=subprocess.STDOUT)
            receipt['owned_pid'] = child.pid
            next_source_check = time.monotonic()
            while child.poll() is None:
                live()
                if time.monotonic() >= next_source_check:
                    scope(candidate)
                    next_source_check = time.monotonic() + 5
                sampled = max(sampled, helper.peak(child), job.peak())
                require(sampled <= 2147483648 and time.monotonic() - begin < 600 and size(directory) < 268435456, 'owned execution resource bounds')
                time.sleep(.5)
        require(child.returncode == 0 and job.wait_idle(5), 'successful command and zero owned descendants')
        scope(candidate)
        receipt['status'] = 'PASS'
    except BaseException as exc:
        receipt.update(status='FAILED_RETAINED', error=repr(exc))
        raise
    finally:
        if job is not None:
            try:
                if job.active(): job.stop()
                receipt.update(peak_memory_bytes=max(sampled, job.peak()), owned_active_after_cleanup=job.active())
            except BaseException as exc: errors.append(repr(exc))
            finally:
                try: job.close()
                except BaseException as exc: errors.append(repr(exc))
        if child is not None:
            try: receipt['exit_code'] = child.wait(timeout=5)
            except BaseException as exc: errors.append(repr(exc))
        receipt.update(finished_at=now().isoformat(), seconds=time.monotonic() - begin, cleanup_errors=errors)
        if receipt['seconds'] >= 600 or receipt.get('peak_memory_bytes', 0) > 2147483648 or receipt.get('owned_active_after_cleanup', 0) != 0:
            errors.append('terminal process/time/memory bounds')
        log = directory / (label + '.log')
        receipt['log_sha256'] = sha(log.read_bytes()) if log.exists() else None
        if errors: receipt['status'] = 'FAILED_RETAINED'
        write(directory / (label + '-execution.json'), receipt)
        if size(directory) >= 268435456:
            errors.append('post-serialization artifact bound'); receipt['status'] = 'FAILED_RETAINED'
            write(directory / (label + '-execution.json'), receipt)
        print(json.dumps({k: receipt[k] for k in ('label', 'status', 'seconds')}), flush=True)
        if errors: raise RuntimeError('owned cleanup/resource failure: ' + repr(errors))
    return receipt
