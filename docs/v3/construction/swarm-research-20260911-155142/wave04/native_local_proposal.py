"""Campaign-local admission for NEW native research commands.

Additive proposal under parent goal-recursion-v2-execution-fabric. This is a
narrow controller, not the inherited 87-command gate, and local results are
never final scientific validation (validation-contract full_gate_blocker).
Host Python here performs controller/accounting work only; every supplied
research input executes through the unchanged trusted
tools.construction_swarm.foundry_tools.run_command sandbox (<=60s, <=1MiB
stdout, 2GiB cgroup, 64MiB scratch mounts, four shared slots, native WSL).
No provider launch, no retries, no refunds; uncertain cleanup fails closed.
Root reviews this file before any execution.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
NAME = 'swarm-research-20260911-155142'
CAMPAIGN = 'research-20260911-155142'
PARENT = 'goal-recursion-v2-execution-fabric'
DOC = 'docs/v3/construction/' + NAME + '/'
CODE = 'experiments/v3/' + NAME + '/'
BRANCH = 'codex/' + NAME
START = dt.datetime.fromisoformat('2026-09-11T15:51:42+00:00')
END = dt.datetime.fromisoformat('2026-09-11T23:51:42+00:00')
INHERITED = 3823610
CEILING = 5000000
MAX_SECONDS = 60
MAX_ARGV = 64
MAX_STDOUT = 1024 * 1024
JOB_BYTES = 2 * 1024**3
SCRATCH_BYTES = 64 * 1024**2
SHARED_SLOTS = 4
MAX_ATTEMPT = 256 * 1024**2
MANIFEST = DOC + 'native-manifest.json'
CACHE = Path('/var/lib/recursion-foundry/campaigns') / CAMPAIGN
KIND_FIELD = {'inventory': 'symbolic_events',
              'explore': 'representation_visits',
              'audit': 'audit_states'}


class Refused(ValueError):
    pass


def require(value, reason):
    if not value:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def now():
    return dt.datetime.now(dt.timezone.utc)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def dump(value):
    return json.dumps(value, indent=2, sort_keys=True) + '\n'


def write(path, value):
    Path(path).write_text(dump(value), encoding='utf-8')


def size(path):
    return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file())


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, timeout=30)


def relpath(value):
    p = PurePosixPath(value) if type(value) is str else None
    require(p is not None and 0 < len(value) <= 240 and not p.is_absolute()
            and str(p) == value and all(part not in ('.', '..') and not part.startswith('.')
                                        for part in p.parts), 'canonical relative path')
    return value


def live(cache):
    require(START <= now() < END, 'immutable 15:51:42-23:51:42Z window')
    require(not (ROOT / 'state/PAUSE').exists() and not (cache / 'PAUSE').exists(), 'PAUSE')
    usage = read(cache / 'usage.json')
    checked = dt.datetime.fromisoformat(usage['checked_utc'])
    require(0 <= (now() - checked).total_seconds() <= 900, 'fresh <=900s quota telemetry')
    windows = usage['binding_windows']
    require(windows and all(0 <= w['used_percent'] < 100
            and w['remaining_percent'] == 100 - w['used_percent'] for w in windows),
            'usable included quota')
    require(usage['remaining_percent'] == min(w['remaining_percent'] for w in windows),
            'binding quota minimum')
    require(usage['reset_credits_used'] == usage['new_metered_spend'] == 0,
            'included allowance only')
    require(all(now().timestamp() < w['resets_at'] for w in windows),
            'no post-reset continuation')
    require({w['name']: w['resets_at'] for w in windows} ==
            read(cache / 'activation.json')['quota_reset_identities'],
            'unchanged quota reset identities')
    return usage


def scope(candidate, cache):
    usage = live(cache)
    require(git('rev-parse', 'HEAD').decode().strip() == candidate, 'exact committed candidate')
    require(not git('status', '--porcelain', '--untracked-files=all').strip(), 'clean workspace')
    require(git('branch', '--show-current').decode().strip() == BRANCH, 'own review branch')
    charter = read(ROOT / (DOC + 'charter.json'))
    require(charter['campaign'] == CAMPAIGN and charter['parent_goal'] == PARENT,
            'campaign and parent identity')
    require(charter['start_utc'] == '2026-09-11T15:51:42Z'
            and charter['deadline_utc'] == '2026-09-11T23:51:42Z', 'immutable clock')
    require(charter['allowed_roots'] == [DOC, CODE], 'allowed roots')
    require(charter == read(cache / 'activation.json')['charter'], 'immutable activated charter')
    require('status: active' in (ROOT / 'state/goals' / (PARENT + '.md')).read_text(),
            'active parent goal')
    base = charter['source_commit']
    changed = git('diff', '--name-only', base, candidate).decode().splitlines()
    require(all(p.startswith((DOC, CODE)) for p in changed), 'two-tree write allowlist')
    require(not git('diff', '--name-only', '--diff-filter=D', base, candidate).strip(),
            'no inherited deletion')
    return usage


def policy(cache):
    p = read(cache / 'policy.json')
    require(p['inherited_charged_units'] == INHERITED and p['cumulative_ceiling'] == CEILING,
            'preserved inherited charge and ceiling')
    require(type(p['full_gate_admission_seconds']) is int
            and p['full_gate_admission_seconds'] >= 3000, 'measured full-gate admission')
    require(p['finalization_reserve_seconds'] >= 2 * p['full_gate_admission_seconds'] + 600,
            'two outstanding full gates plus finalization')
    require(type(p['gate_state_reserve']) is int and p['gate_state_reserve'] >= 0,
            'declared gate state reserve')
    require(p['quota_reserve_percentage_points'] > 0, 'rolling quota reserve')
    return p


def reviews(candidate, cache, policy_sha, manifest_sha):
    approval = read(cache / ('method-' + candidate + '.json'))
    require(approval['candidate'] == candidate and approval['policy_sha256'] == policy_sha
            and approval['manifest_sha256'] == manifest_sha,
            'exact candidate/policy/manifest binding')
    require(approval['status'] == 'APPROVED_FOR_EXECUTION' and len(approval['reviews']) == 2,
            'two prospective reviews')
    names = set()
    for row in approval['reviews']:
        path = (cache / row['path']).resolve()
        require(path.is_relative_to(cache) and sha(path.read_bytes()) == row['sha256'],
                'bound review bytes')
        r = read(path)
        require(r['candidate'] == candidate and r['status'] == 'APPROVE_FOR_EXECUTION'
                and r['policy_sha256'] == policy_sha and r['manifest_sha256'] == manifest_sha
                and r['model'] == 'gpt-6-astra', 'prospective same-model Astra approval')
        names.add(r['reviewer'])
    require(len(names) == 2, 'independent reviewers')


def validate_manifest(m):
    require(set(m) >= {'campaign', 'parent_goal', 'commands'}, 'manifest fields')
    require(m['campaign'] == CAMPAIGN and m['parent_goal'] == PARENT, 'manifest identity')
    commands = m['commands']
    require(type(commands) is list and 1 <= len(commands) <= 64, 'bounded command list')
    seen = set()
    for c in commands:
        require(set(c) == {'id', 'kind', 'argv', 'seconds', 'inputs', 'accounting'},
                'command fields')
        require(type(c['id']) is str and 0 < len(c['id']) <= 64 and c['id'] not in seen,
                'unique command id')
        require(c['kind'] in KIND_FIELD, 'inventory/explore/audit kind')
        require(type(c['argv']) is list and 1 <= len(c['argv']) <= MAX_ARGV and all(
            type(x) is str and 0 < len(x) <= 16384 and '\0' not in x for x in c['argv']),
            'finite exact argv')
        require(type(c['seconds']) is int and 1 <= c['seconds'] <= MAX_SECONDS,
                'bounded seconds')
        require(set(c['accounting']) == {KIND_FIELD[c['kind']]} and
                type(c['accounting'][KIND_FIELD[c['kind']]]) is int and
                c['accounting'][KIND_FIELD[c['kind']]] >= 0, 'separate declared accounting')
        for inp in c['inputs']:
            if inp.get('kind') == 'source':
                require(set(inp) == {'kind', 'path', 'git_blob', 'sha256'}, 'source fields')
                relpath(inp['path'])
            elif inp.get('kind') == 'dependency':
                require(set(inp) == {'kind', 'command', 'artifact', 'artifact_sha256',
                                     'mount'}, 'dependency fields')
                relpath(inp['artifact'])
                relpath(inp['mount'])
                require(inp['command'] in seen, 'dependency on earlier command only')
            else:
                require(False, 'unknown input kind')
        seen.add(c['id'])
    return commands


def load_manifest(candidate):
    raw = (ROOT / MANIFEST).read_bytes()
    require(raw.replace(b'\r\n', b'\n') ==
            git('show', candidate + ':' + MANIFEST).replace(b'\r\n', b'\n'),
            'committed command manifest')
    commands = validate_manifest(json.loads(raw))
    for c in commands:
        for inp in c['inputs']:
            if inp['kind'] != 'source':
                continue
            blob = git('show', candidate + ':' + inp['path'])
            require(git('rev-parse', candidate + ':' + inp['path']).decode().strip()
                    == inp['git_blob'] and sha(blob) == inp['sha256'],
                    'input git blob and source SHA256 closure')
    return commands, sha(raw)


def declared(command):
    return command['accounting'][KIND_FIELD[command['kind']]]


def budget_ok(total, states, outstanding):
    return total + states + outstanding <= CEILING


def reservations(cache):
    folder = cache / 'reservations'
    folder.mkdir(parents=True, exist_ok=True)
    rows, total, prev = [], INHERITED, None
    for i, path in enumerate(sorted(folder.glob('*.json'))):
        raw = path.read_bytes()
        r = json.loads(raw)
        require(r['ordinal'] == i and r['previous_total'] == total
                and r['previous_sha256'] == prev and r['refundable'] is False,
                'append-only hash-linked nonrefundable chain')
        require(type(r['states']) is int and r['states'] >= 0,
                'finite nonnegative reservation')
        total += r['states']
        require(r['new_total'] == total, 'reservation arithmetic')
        prev = sha(raw)
        rows.append(r)
    return rows, total, prev


def reserve(cache, candidate, command, remaining, p):
    from tools.construction_swarm.ledger import controller_lock
    (cache / 'reservations').mkdir(parents=True, exist_ok=True)
    with controller_lock(cache):
        rows, total, prev = reservations(cache)
        outstanding = p['gate_state_reserve'] + remaining
        require(budget_ok(total, declared(command), outstanding),
                'budget incl outstanding full-gate/new-check reservations')
        identity = 'attempts/' + command['id']
        require(all(r['identity'] != identity for r in rows),
                'no reused or refunded reservation')
        row = dict(ordinal=len(rows), identity=identity, candidate=candidate,
                   at=now().isoformat(), kind=command['kind'], states=declared(command),
                   previous_total=total, new_total=total + declared(command),
                   previous_sha256=prev, refundable=False,
                   outstanding_reserved=outstanding)
        path = cache / 'reservations' / (str(len(rows)).zfill(6) + '.json')
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(dump(row))
            f.flush()
            os.fsync(f.fileno())
        dirfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
        return row, sha(path.read_bytes())


def closure(candidate, cache, command):
    files, total = {}, 0
    for inp in command['inputs']:
        if inp['kind'] == 'source':
            files[inp['path']] = git('show', candidate + ':' + inp['path']).decode('utf-8')
        else:
            artifact = (cache / inp['artifact']).resolve()
            require(artifact.is_relative_to(cache)
                    and sha(artifact.read_bytes()) == inp['artifact_sha256'],
                    'exact serialized dependency bytes')
            require(inp['mount'] not in files, 'mount collision')
            files[inp['mount']] = artifact.read_bytes().decode('utf-8')
        total += len(files[list(files)[-1]].encode())
    require(total <= 32 * 1024**2, 'bounded input closure')
    return files


def admit(command_id, cache=CACHE):
    from tools.construction_swarm import capacity
    from tools.construction_swarm.foundry_tools import ToolUncertain, run_command
    cache = Path(cache)
    candidate = git('rev-parse', 'HEAD').decode().strip()
    usage = scope(candidate, cache)
    commands, manifest_sha = load_manifest(candidate)
    p = policy(cache)
    policy_sha = sha((cache / 'policy.json').read_bytes())
    reviews(candidate, cache, policy_sha, manifest_sha)
    order = {c['id']: i for i, c in enumerate(commands)}
    require(command_id in order, 'unknown command')
    command = commands[order[command_id]]
    remaining = sum(declared(x) for x in commands[order[command_id] + 1:])
    require(usage['remaining_percent'] > p['quota_reserve_percentage_points'],
            'rolling quota finalization reserve')
    require((END - now()).total_seconds()
            > p['finalization_reserve_seconds'] + command['seconds'] + 60,
            'immutable deadline reserve')
    capacity.admit_host(cache)
    directory = cache / 'attempts' / command['id']
    directory.mkdir(parents=True, exist_ok=False)
    row, reservation_sha = reserve(cache, candidate, command, remaining, p)
    receipt = dict(candidate=candidate, command=command['id'], kind=command['kind'],
                   argv=command['argv'], seconds=command['seconds'],
                   declared=declared(command), manifest_sha256=manifest_sha,
                   policy_sha256=policy_sha, reservation_sha256=reservation_sha,
                   reservation_total=row['new_total'], started_at=now().isoformat(),
                   status='ADMITTED_BEFORE_EXECUTION',
                   limits=dict(max_seconds=MAX_SECONDS, max_stdout_bytes=MAX_STDOUT,
                               memory_bytes=JOB_BYTES, scratch_bytes=SCRATCH_BYTES,
                               shared_slots=SHARED_SLOTS, attempt_bytes=MAX_ATTEMPT),
                   full_gate_equivalence=False)
    write(directory / 'admission.json', receipt)
    errors = []
    begin = time.monotonic()
    try:
        files = closure(candidate, cache, command)
        outcome = run_command(files, command['argv'], command['seconds'],
                              stop=lambda: now() >= END or (ROOT / 'state/PAUSE').exists())
        for name in ('stdout', 'stderr'):
            (directory / (name + '.log')).write_text(outcome[name], encoding='utf-8')
            receipt[name + '_sha256'] = sha(outcome[name].encode())
        receipt.update(exit_code=outcome['exit_code'], reason=outcome['reason'],
                       tool_seconds=outcome['elapsed_seconds'],
                       isolation=outcome['isolation'],
                       local_quiescent=outcome['local_quiescent'])
        require(outcome['local_quiescent'] and outcome['exit_code'] == 0,
                'clean successful execution')
        receipt['status'] = 'PASS_LOCAL_RESEARCH_ONLY'
    except ToolUncertain as exc:
        obs = exc.observation
        for name in ('stdout', 'stderr'):
            if type(obs.get(name)) is str:
                (directory / (name + '.log')).write_text(obs[name], encoding='utf-8')
                receipt[name + '_sha256'] = sha(obs[name].encode())
        receipt.update(status='UNKNOWN_RETAINED', exit_code=obs.get('exit_code'),
                       isolation=obs.get('isolation'), local_quiescent=False)
        errors.append('uncertain cleanup; reservation retained')
    except BaseException as exc:
        receipt.update(status='FAILED_RETAINED', error=repr(exc))
        errors.append(repr(exc))
    finally:
        receipt.update(finished_at=now().isoformat(),
                       seconds=time.monotonic() - begin, cleanup_errors=errors)
        write(directory / 'execution.json', receipt)
        receipt['attempt_bytes'] = size(directory)
        if receipt['attempt_bytes'] > MAX_ATTEMPT:
            receipt['status'] = 'FAILED_RETAINED'
            receipt['cleanup_errors'] = errors + ['attempt exceeds 256MiB incl receipt']
        write(directory / 'execution.json', receipt)
        print(json.dumps({'receipt': (directory / 'execution.json').as_posix(),
                          'receipt_sha256': sha((directory / 'execution.json').read_bytes()),
                          'status': receipt['status']}), flush=True)
    require(not errors, 'retained failed/unknown attempt: ' + command['id'])
    return receipt


if __name__ == '__main__':
    require(len(sys.argv) in (2, 3), 'usage: native_local.py <command-id> [cache-root]')
    admit(sys.argv[1], Path(sys.argv[2]) if len(sys.argv) == 3 else CACHE)
