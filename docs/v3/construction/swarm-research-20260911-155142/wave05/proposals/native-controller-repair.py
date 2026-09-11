"""Campaign-local admission for NEW native research commands (repaired proposal).

Additive proposal under parent goal-recursion-v2-execution-fabric. Narrow
controller only: never the inherited 87-command gate, and local results are
never final scientific validation (validation-contract full_gate_blocker).
Every supplied research input executes through the unchanged trusted
foundry_tools.run_command sandbox (<=60s, <=1MiB combined decoded output,
2GiB cgroup, 64MiB scratch mounts, four shared slots, native WSL). No
provider launch, no retries, no resets and no refunds; uncertain cleanup
fails closed and retains the charge. Root reviews this file before any
execution.

Repair of the retained wave04 proposal against the seven independent
review-defects.native_local items:

1. Fixed canonical workspace/cache/frozen-runtime paths; no CLI cache
   override. Slug command ids; resolved-path and symlink containment on
   every cache read; reservation chain is anchored at the inherited charge
   with contiguous ordinals, so no independent ledger reset can validate.
2. PASS requires exit_code==0, reason is None, cleanup_error is None,
   pipes_closed, direct_process_exited, local_quiescent AND authoritative
   empty cgroup (isolation.quiescent, no isolation cleanup_error, observed
   memory_peak). Combined decoded stdout+stderr must stay <=1MiB. Logs are
   decoded UTF-8 text, never claimed as raw-byte evidence.
3. Budget covers ALL outstanding commands, the inherited 655520 gate
   reserve and two final full successor-gate repetitions. Exact declared
   accounting: symbolic inventory 40512, per-shard frozen revalidation 192,
   70 model visits per history, audits/controls explicitly charged.
   Deadline check covers command + 120s tool queue + dispatch delay +
   finalization reserve. No hidden refund.
4. Dependency inputs bind a same-candidate prior clean PASS receipt (same
   manifest/policy hashes, chronology, earlier reservation ordinal) and
   exact artifact membership in that receipt cross-checked against the
   retained-bytes manifest; each artifact is read once;
   duplicate/colliding mounts and source paths are refused.
5. PAUSE is checked on native workspace, frozen original source and cache
   roots; STOP on all three; fresh quota with exact reset identities;
   active parent goal; exact candidate/policy/manifest/reviews re-verified
   immediately before execution and polled while queued. Framework-root
   changes need separately bound reviews; immutable original sources stay
   protected by the allowlist. Post-execution source-pin checks rerun.
6. Trusted runtime is imported only from the frozen tree after exact
   interpreter and per-module hash verification against activation pins.
   Mounted source/dependency snapshots and actual review hashes are
   retained in the attempt; admission is fsynced before the run; every
   post-reservation failure is captured immediately, never losing charge.
7. Final whole-attempt size includes the final receipt (fixed-point loop);
   overflow returns failure. Every attempt declares
   PENDING_INDEPENDENT_RETAINED_AUDIT with exact membership for an
   independent auditor; nothing self-trusting is claimed.
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import importlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time

NAME = 'swarm-research-20260911-155142'
CAMPAIGN = 'research-20260911-155142'
PARENT = 'goal-recursion-v2-execution-fabric'
DOC = 'docs/v3/construction/' + NAME + '/'
CODE = 'experiments/v3/' + NAME + '/'
BRANCH = 'codex/' + NAME
ROOT = Path('/opt/recursion-foundry/workspaces/research-20260911-155142')
CACHE = Path('/var/lib/recursion-foundry/campaigns/research-20260911-155142')
FROZEN = Path('/opt/recursion-foundry/source-v3-20260911-155142-r2')
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
MAX_INPUT = 32 * 1024**2
MAX_ARTIFACTS = 384
MAX_ARTIFACT = 1024 * 1024
ARTIFACT_TOTAL = 32 * 1024**2
TOOL_QUEUE_SECONDS = 120
DISPATCH_DELAY_SECONDS = 60
FINAL_REPETITIONS = 2
VISITS_PER_HISTORY = 70
MANIFEST = DOC + 'native-manifest.json'
ID_RE = re.compile(r'[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?')
FILE_RE = re.compile(r'[0-9A-Za-z][0-9A-Za-z_.-]{0,127}')
HEX40 = re.compile(r'[0-9a-f]{40}')
HEX64 = re.compile(r'[0-9a-f]{64}')
WINDOWS_RESERVED = {'con', 'prn', 'aux', 'nul',
                    *(f'com{i}' for i in range(10)), *(f'lpt{i}' for i in range(10))}
KIND_ACCOUNTING = {
    'inventory': {'symbolic_events'},
    'explore': {'symbolic_events', 'representation_visits'},
    'audit': {'audit_states'},
    'control': {'control_checks'},
}
REPORT_TO_FIELD = {'symbolic_units': 'symbolic_events',
                   'state_visits': 'representation_visits',
                   'audit_states': 'audit_states',
                   'control_checks': 'control_checks'}
FIELD_TO_REPORT = {field: key for key, field in REPORT_TO_FIELD.items()}


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


def put_bytes(path, raw, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | (os.O_EXCL if exclusive else os.O_TRUNC)
    fd = os.open(path, flags)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    dirfd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)


def write(path, value):
    put_bytes(path, dump(value).encode('utf-8'))


def size(path):
    return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file())


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, timeout=30)


def canonical(path):
    path = Path(path)
    return path.is_dir() and not path.is_symlink() and path.resolve() == path


def contained(path, root):
    raw = Path(path)
    resolved = raw.resolve()
    return (not raw.is_symlink() and resolved.is_file()
            and resolved.is_relative_to(Path(root).resolve()))


def relpath(value):
    p = PurePosixPath(value) if type(value) is str else None
    require(p is not None and 0 < len(value) <= 240 and not p.is_absolute()
            and str(p) == value
            and all(re.fullmatch(r'[A-Za-z0-9_.-]+', part) and part not in ('.', '..')
                    and not part.startswith('.') and not part.endswith(('.', ' '))
                    and part.lower().split('.')[0] not in WINDOWS_RESERVED
                    for part in p.parts),
            'canonical relative path')
    return value


def pause_paths():
    return (ROOT / 'PAUSE', ROOT / 'state' / 'PAUSE',
            FROZEN / 'PAUSE', FROZEN / 'state' / 'PAUSE', CACHE / 'PAUSE')


def stop_paths():
    return (ROOT / 'STOP', FROZEN / 'STOP', CACHE / 'STOP')


def live(cache):
    require(START <= now() < END, 'immutable 15:51:42-23:51:42Z window')
    for path in (*pause_paths(), *stop_paths()):
        require(not path.exists(), 'pause/stop marker present: ' + str(path))
    activation = read(cache / 'activation.json')
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
    require(all(type(w['resets_at']) in (int, float)
            and now().timestamp() < w['resets_at'] for w in windows),
            'no post-reset continuation')
    require({w['name']: w['resets_at'] for w in windows} ==
            activation['quota_reset_identities'], 'exact quota reset identities')
    return usage, activation


def frozen_runtime(activation):
    """Import trusted modules only from the hash-pinned frozen runtime tree."""
    fr = activation['frozen_runtime']
    require(set(fr) == {'root', 'interpreter', 'interpreter_sha256', 'module_sha256'},
            'frozen runtime fields')
    require(fr['root'] == str(FROZEN), 'fixed frozen runtime root')
    exe = Path(sys.executable).resolve()
    require(str(exe) == fr['interpreter']
            and sha(exe.read_bytes()) == fr['interpreter_sha256'],
            'exact interpreter identity and hash')
    declared = fr['module_sha256']
    require(type(declared) is dict and declared and all(
        type(k) is str and HEX64.fullmatch(v) for k, v in declared.items()),
        'declared frozen module hashes')
    for name in declared:
        relpath(name)
        require(name.startswith('tools/'), 'frozen pins limited to trusted tools tree')
    found = {p.relative_to(FROZEN).as_posix(): sha(p.read_bytes())
             for p in (FROZEN / 'tools').rglob('*.py')}
    require(found == declared, 'exact frozen module set and hashes; no extra/missing')
    sys.path.insert(0, str(FROZEN))
    mods = {}
    for name in ('tools.construction_swarm.contracts', 'tools.construction_swarm.ledger',
                 'tools.construction_swarm.capacity', 'tools.construction_swarm.process',
                 'tools.construction_swarm.foundry_tools'):
        module = importlib.import_module(name)
        origin = Path(module.__file__).resolve()
        require(origin.is_relative_to(FROZEN)
                and declared.get(origin.relative_to(FROZEN).as_posix()) == sha(origin.read_bytes()),
                'trusted module resolved outside frozen runtime')
        mods[name.rsplit('.', 1)[1]] = module
    return mods


def scope(candidate, cache):
    usage, activation = live(cache)
    require(canonical(ROOT) and canonical(FROZEN) and canonical(cache),
            'canonical fixed workspace/runtime/cache roots')
    require(git('rev-parse', 'HEAD').decode().strip() == candidate, 'exact committed candidate')
    require(not git('status', '--porcelain', '--untracked-files=all').strip(), 'clean workspace')
    require(git('branch', '--show-current').decode().strip() == BRANCH, 'own review branch')
    charter = read(ROOT / (DOC + 'charter.json'))
    require(charter['campaign'] == CAMPAIGN and charter['parent_goal'] == PARENT,
            'campaign and parent identity')
    require(charter['start_utc'] == '2026-09-11T15:51:42Z'
            and charter['deadline_utc'] == '2026-09-11T23:51:42Z', 'immutable clock')
    require(charter['allowed_roots'] == [DOC, CODE], 'allowed roots')
    require(charter == activation['charter'], 'immutable activated charter')
    require('status: active' in (ROOT / 'state' / 'goals' / (PARENT + '.md')).read_text(),
            'active parent goal')
    base = charter['source_commit']
    changed = git('diff', '--name-only', base, candidate).decode().splitlines()
    framework_roots = tuple(charter['framework_fix_roots'])
    require(all(p.startswith((DOC, CODE) + framework_roots) for p in changed),
            'campaign write allowlist incl separately reviewed framework roots')
    require(not git('diff', '--name-only', '--diff-filter=D', base, candidate).strip(),
            'no inherited deletion; immutable original sources stay protected')
    framework_changed = any(p.startswith(framework_roots) for p in changed)
    return usage, activation, framework_changed


def policy(cache):
    p = read(cache / 'policy.json')
    require(p['inherited_charged_units'] == INHERITED and p['cumulative_ceiling'] == CEILING,
            'preserved inherited charge and ceiling')
    require(type(p['full_gate_admission_seconds']) is int
            and p['full_gate_admission_seconds'] >= 3000, 'measured full-gate admission')
    require(type(p['finalization_reserve_seconds']) is int
            and p['finalization_reserve_seconds'] >= 10200
            and p['finalization_reserve_seconds'] >= 2 * p['full_gate_admission_seconds'] + 600,
            'two outstanding full gates plus finalization reserve')
    require(type(p['gate_state_reserve']) is int and p['gate_state_reserve'] >= 655520,
            'inherited gate state reserve')
    require(p['quota_reserve_percentage_points'] > 0, 'rolling quota reserve')
    return p


def _review_rows(rows, candidate, cache, policy_sha, manifest_sha):
    require(type(rows) is list and len(rows) == 2, 'two prospective reviews')
    names, members = set(), []
    for row in rows:
        raw_path = cache / row['path']
        require(contained(raw_path, cache), 'contained non-symlink review file')
        resolved = raw_path.resolve()
        require(sha(resolved.read_bytes()) == row['sha256'], 'bound review bytes')
        r = read(resolved)
        require(r['candidate'] == candidate and r['status'] == 'APPROVE_FOR_EXECUTION'
                and r['policy_sha256'] == policy_sha and r['manifest_sha256'] == manifest_sha
                and r['model'] == 'gpt-6-astra', 'prospective same-model Astra approval')
        names.add(r['reviewer'])
        members.append({'path': row['path'], 'sha256': row['sha256'],
                        'reviewer': r['reviewer'], 'model': r['model']})
    require(len(names) == 2, 'independent reviewers')
    return members


def reviews(candidate, cache, policy_sha, manifest_sha, framework_changed):
    approval = read(cache / ('method-' + candidate + '.json'))
    require(approval['candidate'] == candidate and approval['policy_sha256'] == policy_sha
            and approval['manifest_sha256'] == manifest_sha,
            'exact candidate/policy/manifest binding')
    require(approval['status'] == 'APPROVED_FOR_EXECUTION', 'prospective method approval')
    members = _review_rows(approval['reviews'], candidate, cache, policy_sha, manifest_sha)
    if framework_changed:
        members += _review_rows(approval.get('framework_reviews'), candidate, cache,
                                policy_sha, manifest_sha)
    return members


def declared(command):
    return sum(command['accounting'].values())


def validate_manifest(m):
    require(set(m) >= {'campaign', 'parent_goal', 'commands'}, 'manifest fields')
    require(m['campaign'] == CAMPAIGN and m['parent_goal'] == PARENT, 'manifest identity')
    commands = m['commands']
    require(type(commands) is list and 1 <= len(commands) <= 64, 'bounded command list')
    seen = set()
    for c in commands:
        require(set(c) == {'id', 'kind', 'argv', 'seconds', 'inputs', 'accounting'},
                'command fields')
        require(type(c['id']) is str and ID_RE.fullmatch(c['id']) and c['id'] not in seen,
                'unique simple slug command id')
        require(c['kind'] in KIND_ACCOUNTING, 'inventory/explore/audit/control kind')
        acc = c['accounting']
        require(type(acc) is dict and set(acc) == KIND_ACCOUNTING[c['kind']]
                and all(type(v) is int and v >= 0 for v in acc.values()),
                'kind-scoped mixed accounting fields')
        if c['kind'] == 'inventory':
            require(acc == {'symbolic_events': 40512}, 'exact analytic inventory charge')
        elif c['kind'] == 'explore':
            require(acc['symbolic_events'] == 192
                    and acc['representation_visits'] % VISITS_PER_HISTORY == 0
                    and 1 <= acc['representation_visits'] // VISITS_PER_HISTORY <= 24,
                    'per-shard 192 symbolic plus 70 model visits per history')
        else:
            require(list(acc.values())[0] >= 1, 'explicitly charged ' + c['kind'])
        require(type(c['argv']) is list and 1 <= len(c['argv']) <= MAX_ARGV and all(
            type(x) is str and 0 < len(x) <= 16384 and '\0' not in x for x in c['argv']),
            'finite exact argv')
        require(type(c['seconds']) is int and 1 <= c['seconds'] <= MAX_SECONDS,
                'bounded seconds')
        mounts = set()
        for inp in c['inputs']:
            if inp.get('kind') == 'source':
                require(set(inp) == {'kind', 'path', 'git_blob', 'sha256'}, 'source fields')
                relpath(inp['path'])
                require(HEX40.fullmatch(inp['git_blob']) and HEX64.fullmatch(inp['sha256']),
                        'exact source git blob and sha256 pins')
                target = inp['path']
            elif inp.get('kind') == 'dependency':
                require(set(inp) == {'kind', 'command', 'artifact', 'artifact_sha256', 'mount'},
                        'dependency fields')
                require(type(inp['command']) is str and ID_RE.fullmatch(inp['command'])
                        and inp['command'] in seen, 'dependency on earlier slug command only')
                relpath(inp['mount'])
                require(HEX64.fullmatch(inp['artifact_sha256']), 'exact artifact sha256')
                artifact = PurePosixPath(inp['artifact'])
                require(str(artifact) == inp['artifact'] and len(artifact.parts) == 2
                        and artifact.parts[0] == 'artifacts'
                        and FILE_RE.fullmatch(artifact.parts[1])
                        and not artifact.parts[1].endswith(('.', ' ')),
                        'dependency must name one retained artifacts/<file> member')
                target = inp['mount']
            else:
                require(False, 'unknown input kind')
            require(target not in mounts and target != 'foundry_command_gate.py',
                    'duplicate/colliding mount or source path')
            mounts.add(target)
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


def outstanding_reserve(commands, index, p):
    """Remaining commands + inherited gate reserve + two final full repetitions."""
    manifest_total = sum(declared(x) for x in commands)
    remaining = sum(declared(x) for x in commands[index + 1:])
    final = FINAL_REPETITIONS * (p['gate_state_reserve'] + manifest_total)
    return p['gate_state_reserve'] + remaining + final


def reservations(cache):
    folder = cache / 'reservations'
    folder.mkdir(parents=True, exist_ok=True)
    files = sorted(folder.glob('*.json'))
    require([f.name for f in files] ==
            [str(i).zfill(6) + '.json' for i in range(len(files))],
            'contiguous reservation ordinals; no independent ledger reset')
    rows, total, prev, prev_at = [], INHERITED, None, ''
    for i, path in enumerate(files):
        raw = path.read_bytes()
        r = json.loads(raw)
        require(r['ordinal'] == i and r['previous_total'] == total
                and r['previous_sha256'] == prev and r['refundable'] is False,
                'append-only hash-linked nonrefundable chain anchored at inherited charge')
        require(type(r['states']) is int and r['states'] >= 0
                and type(r['at']) is str and r['at'] >= prev_at,
                'finite nonnegative chronological reservation')
        total += r['states']
        require(r['new_total'] == total, 'reservation arithmetic')
        prev, prev_at = sha(raw), r['at']
        rows.append(r)
    identities = [r['identity'] for r in rows]
    require(len(set(identities)) == len(identities), 'unique reservation identities')
    return rows, total, prev


def reserve(cache, candidate, command, outstanding, manifest_sha, policy_sha, ledger):
    (cache / 'reservations').mkdir(parents=True, exist_ok=True)
    with ledger.controller_lock(cache):
        rows, total, prev = reservations(cache)
        require(total + declared(command) + outstanding <= CEILING,
                'budget incl outstanding controls/audits/final repetitions/gate reserve')
        identity = 'attempts/' + command['id']
        require(all(r['identity'] != identity for r in rows),
                'no reused, reset or refunded reservation')
        row = dict(ordinal=len(rows), identity=identity, candidate=candidate,
                   at=now().isoformat(), kind=command['kind'],
                   accounting=command['accounting'], states=declared(command),
                   previous_total=total, new_total=total + declared(command),
                   previous_sha256=prev, refundable=False, reset_or_refund='none',
                   outstanding_reserved=outstanding,
                   manifest_sha256=manifest_sha, policy_sha256=policy_sha)
        path = cache / 'reservations' / (str(len(rows)).zfill(6) + '.json')
        put_bytes(path, dump(row).encode('utf-8'), exclusive=True)
        return row, sha(path.read_bytes())


def pass_dependency(cache, inp, candidate, manifest_sha, policy_sha, current_ordinal):
    """Bind a same-candidate prior clean PASS receipt and exact artifact member."""
    directory = cache / 'attempts' / inp['command']
    require(directory.is_dir() and not directory.is_symlink()
            and directory.resolve().is_relative_to(cache.resolve()),
            'contained dependency attempt directory')
    receipt_path = directory / 'execution.json'
    require(contained(receipt_path, cache), 'contained dependency receipt')
    receipt_raw = receipt_path.resolve().read_bytes()
    rec = json.loads(receipt_raw)
    require(rec.get('status') == 'PASS_LOCAL_RESEARCH_ONLY'
            and rec.get('command') == inp['command']
            and rec.get('candidate') == candidate
            and rec.get('manifest_sha256') == manifest_sha
            and rec.get('policy_sha256') == policy_sha
            and rec.get('cleanup_errors') == [] and rec.get('pass_failures') == []
            and rec.get('local_quiescent') is True
            and rec.get('post_execution_pin_ok') is True,
            'same-candidate prior clean PASS receipt binding')
    started = dt.datetime.fromisoformat(rec['started_at'])
    finished = dt.datetime.fromisoformat(rec['finished_at'])
    require(started < finished <= now(), 'dependency chronology')
    require(type(rec.get('reservation_ordinal')) is int
            and rec['reservation_ordinal'] < current_ordinal,
            'dependency reservation precedes consumer')
    name = PurePosixPath(inp['artifact']).parts[1]
    members = {a['name']: a['sha256'] for a in rec.get('artifacts', [])}
    require(members.get(name) == inp['artifact_sha256'],
            'exact artifact membership in producer receipt')
    require((rec.get('attempt_membership') or {}).get('artifacts/' + name)
            == inp['artifact_sha256'],
            'retained-bytes membership agrees with declared artifact')
    artifact = directory / 'artifacts' / name
    require(contained(artifact, cache), 'contained dependency artifact')
    raw = artifact.read_bytes()
    require(sha(raw) == inp['artifact_sha256'], 'exact dependency artifact bytes')
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        require(False, 'non-UTF8 artifact cannot mount through the text tool honestly')
    member = {'command': inp['command'], 'artifact': inp['artifact'],
              'artifact_sha256': inp['artifact_sha256'],
              'receipt_sha256': sha(receipt_raw),
              'reservation_ordinal': rec['reservation_ordinal'],
              'finished_at': rec['finished_at']}
    return text, member


def closure(candidate, cache, command, current_ordinal, manifest_sha, policy_sha):
    files, sources, deps = {}, {}, []
    for inp in command['inputs']:
        if inp['kind'] == 'source':
            raw = git('show', candidate + ':' + inp['path'])
            require(sha(raw) == inp['sha256'], 'source bytes unchanged at mount')
            files[inp['path']] = raw.decode('utf-8')
            sources[inp['path']] = {'git_blob': inp['git_blob'], 'sha256': inp['sha256'],
                                    'bytes': len(raw)}
        else:
            text, member = pass_dependency(cache, inp, candidate, manifest_sha,
                                           policy_sha, current_ordinal)
            files[inp['mount']] = text
            deps.append(member)
    require(sum(len(t.encode('utf-8')) for t in files.values()) <= MAX_INPUT,
            'bounded input closure')
    return files, sources, deps


def pass_failures(outcome):
    """Pure check of the actual tool result shape; returns observed failure names."""
    failures = []
    if outcome.get('exit_code') != 0:
        failures.append('exit_code')
    if outcome.get('reason') is not None:
        failures.append('reason:' + str(outcome.get('reason')))
    if outcome.get('cleanup_error') is not None:
        failures.append('cleanup_error')
    for field in ('pipes_closed', 'direct_process_exited', 'local_quiescent'):
        if outcome.get(field) is not True:
            failures.append(field)
    isolation = outcome.get('isolation') or {}
    if isolation.get('quiescent') is not True:
        failures.append('authoritative_empty_cgroup')
    if isolation.get('cleanup_error') is not None:
        failures.append('isolation_cleanup_error')
    if type(isolation.get('memory_peak')) is not int or isolation.get('memory_peak') < 0:
        failures.append('memory_peak_unobserved')
    combined = (len((outcome.get('stdout') or '').encode('utf-8'))
                + len((outcome.get('stderr') or '').encode('utf-8')))
    if combined > MAX_STDOUT:
        failures.append('combined_decoded_output_exceeds_1MiB')
    return failures


def verify_report(command, stdout_text):
    """Exact declared-vs-reported unit check on the single stdout JSON object."""
    try:
        report = json.loads(stdout_text)
    except ValueError:
        require(False, 'single strict JSON report on stdout')
    require(type(report) is dict, 'stdout report object')
    for field, declared_value in command['accounting'].items():
        key = FIELD_TO_REPORT[field]
        require(key in report and report[key] == declared_value,
                'reported ' + key + ' must equal declared ' + field)
    for key, field in REPORT_TO_FIELD.items():
        if key in report:
            require(report[key] == command['accounting'].get(field),
                    'undeclared reported unit ' + key)
    return report


def extract_artifacts(report, directory):
    out = []
    for case in list(report.get('cases') or []) + list(report.get('exported_artifacts') or []):
        require({'artifact', 'artifact_sha256', 'certificate_gzip_base64'} <= set(case),
                'artifact export fields')
        name = case['artifact']
        require(type(name) is str and FILE_RE.fullmatch(name)
                and not name.endswith(('.', ' ')), 'artifact filename')
        require(len(out) < MAX_ARTIFACTS, 'bounded artifact count')
        raw = base64.b64decode(case['certificate_gzip_base64'], validate=True)
        require(0 < len(raw) <= MAX_ARTIFACT and sha(raw) == case['artifact_sha256'],
                'exact exported artifact bytes')
        put_bytes(directory / 'artifacts' / name, raw, exclusive=True)
        out.append({'name': name, 'sha256': case['artifact_sha256'], 'bytes': len(raw)})
    require(sum(a['bytes'] for a in out) <= ARTIFACT_TOTAL, 'bounded artifact total')
    return out


def stop_gate(candidate):
    state = {'last': 0.0}

    def stop():
        if now() >= END:
            return True
        if any(p.exists() for p in (*pause_paths(), *stop_paths())):
            return True
        if time.monotonic() - state['last'] >= 1.0:
            state['last'] = time.monotonic()
            try:
                head = git('rev-parse', 'HEAD').decode().strip()
            except Exception:
                return True
            if head != candidate:
                return True
        return False

    return stop


def recheck(candidate, cache, policy_sha, manifest_sha, activation_sha, framework_changed):
    """Full precondition re-verification immediately before execution/queue entry."""
    live(cache)
    require(git('rev-parse', 'HEAD').decode().strip() == candidate,
            'candidate drift before execution')
    require(not git('status', '--porcelain', '--untracked-files=all').strip(),
            'workspace drift before execution')
    require(sha((cache / 'policy.json').read_bytes()) == policy_sha, 'policy drift')
    require(sha((cache / 'activation.json').read_bytes()) == activation_sha,
            'activation drift')
    raw = (ROOT / MANIFEST).read_bytes()
    require(sha(raw) == manifest_sha and raw.replace(b'\r\n', b'\n') ==
            git('show', candidate + ':' + MANIFEST).replace(b'\r\n', b'\n'),
            'manifest drift')
    reviews(candidate, cache, policy_sha, manifest_sha, framework_changed)


def postcheck(candidate, cache, command, policy_sha, manifest_sha, activation_sha):
    """Exact source-pin post-checks after execution."""
    try:
        if git('rev-parse', 'HEAD').decode().strip() != candidate:
            return False
        if sha((cache / 'policy.json').read_bytes()) != policy_sha:
            return False
        if sha((cache / 'activation.json').read_bytes()) != activation_sha:
            return False
        if sha((ROOT / MANIFEST).read_bytes()) != manifest_sha:
            return False
        for inp in command['inputs']:
            if inp['kind'] == 'source':
                if git('rev-parse', candidate + ':' + inp['path']).decode().strip() != inp['git_blob']:
                    return False
                if sha(git('show', candidate + ':' + inp['path'])) != inp['sha256']:
                    return False
        if any(p.exists() for p in (*pause_paths(), *stop_paths())):
            return False
        return True
    except Exception:
        return False


def finalize(directory, receipt, errors):
    receipt['cleanup_errors'] = errors
    receipt['attempt_membership'] = {
        p.relative_to(directory).as_posix(): sha(p.read_bytes())
        for p in sorted(directory.rglob('*'))
        if p.is_file() and p.name != 'execution.json'}
    receipt['independent_audit_required'] = True
    receipt['audit_status'] = 'PENDING_INDEPENDENT_RETAINED_AUDIT'
    for _ in range(6):
        actual = size(directory)
        receipt['attempt_bytes'] = actual
        write(directory / 'execution.json', receipt)
        if size(directory) == actual:
            break
    if receipt['attempt_bytes'] > MAX_ATTEMPT and receipt['status'] != 'UNKNOWN_RETAINED':
        receipt['status'] = 'FAILED_RETAINED'
        errors.append('final whole-attempt bytes incl final receipt exceed 256MiB')
        receipt['cleanup_errors'] = errors
        for _ in range(6):
            actual = size(directory)
            receipt['attempt_bytes'] = actual
            write(directory / 'execution.json', receipt)
            if size(directory) == actual:
                break


def admit(command_id):
    require(type(command_id) is str and ID_RE.fullmatch(command_id), 'slug command id')
    require(canonical(CACHE) and canonical(ROOT) and canonical(FROZEN),
            'fixed canonical campaign cache, workspace and frozen runtime')
    cache = CACHE
    candidate = git('rev-parse', 'HEAD').decode().strip()
    usage, activation, framework_changed = scope(candidate, cache)
    mods = frozen_runtime(activation)
    commands, manifest_sha = load_manifest(candidate)
    p = policy(cache)
    policy_sha = sha((cache / 'policy.json').read_bytes())
    activation_sha = sha((cache / 'activation.json').read_bytes())
    review_members = reviews(candidate, cache, policy_sha, manifest_sha, framework_changed)
    order = {c['id']: i for i, c in enumerate(commands)}
    require(command_id in order, 'unknown command')
    index = order[command_id]
    command = commands[index]
    outstanding = outstanding_reserve(commands, index, p)
    require(usage['remaining_percent'] > p['quota_reserve_percentage_points'],
            'rolling quota finalization reserve')
    require((END - now()).total_seconds()
            > p['finalization_reserve_seconds'] + command['seconds']
            + TOOL_QUEUE_SECONDS + DISPATCH_DELAY_SECONDS,
            'immutable deadline reserve: command + 120s tool queue + dispatch + finalization')
    mods['capacity'].admit_host(cache)
    directory = cache / 'attempts' / command['id']
    directory.mkdir(parents=True, exist_ok=False)
    row, reservation_sha = reserve(cache, candidate, command, outstanding,
                                   manifest_sha, policy_sha, mods['ledger'])
    receipt = dict(candidate=candidate, command=command['id'], kind=command['kind'],
                   argv=command['argv'], seconds=command['seconds'],
                   accounting=command['accounting'], declared=declared(command),
                   manifest_sha256=manifest_sha, policy_sha256=policy_sha,
                   activation_sha256=activation_sha,
                   reservation_sha256=reservation_sha,
                   reservation_ordinal=row['ordinal'], reservation_total=row['new_total'],
                   outstanding_reserved=outstanding,
                   review_membership=review_members,
                   started_at=now().isoformat(),
                   status='ADMITTED_BEFORE_EXECUTION',
                   limits=dict(max_seconds=MAX_SECONDS, max_stdout_bytes=MAX_STDOUT,
                               combined_decoded_output_bytes=MAX_STDOUT,
                               memory_bytes=JOB_BYTES, scratch_bytes=SCRATCH_BYTES,
                               shared_slots=SHARED_SLOTS, attempt_bytes=MAX_ATTEMPT,
                               tool_queue_seconds=TOOL_QUEUE_SECONDS,
                               dispatch_delay_seconds=DISPATCH_DELAY_SECONDS),
                   log_encoding='decoded utf-8 text; not raw byte evidence',
                   decoded_text_evidence=True,
                   refundable=False, reset_or_refund='none',
                   full_gate_equivalence=False, scientific_validation=False,
                   controller_observation_only=True,
                   independent_audit_required=True,
                   audit_status='PENDING_INDEPENDENT_RETAINED_AUDIT')
    write(directory / 'admission.json', receipt)
    errors = []
    begin = time.monotonic()
    try:
        files, sources, deps = closure(candidate, cache, command, row['ordinal'],
                                       manifest_sha, policy_sha)
        mounted = {}
        for name, text in files.items():
            raw = text.encode('utf-8')
            put_bytes(directory / 'mounted' / name, raw)
            mounted[name] = sha(raw)
        receipt.update(source_membership=sources, dependency_membership=deps,
                       mounted_snapshot_sha256=mounted)
        write(directory / 'admission.json', receipt)
        recheck(candidate, cache, policy_sha, manifest_sha, activation_sha, framework_changed)
        outcome = mods['foundry_tools'].run_command(
            files, command['argv'], command['seconds'], stop=stop_gate(candidate))
        for name in ('stdout', 'stderr'):
            text = outcome[name]
            put_bytes(directory / (name + '.log'), text.encode('utf-8'))
            receipt[name + '_decoded_utf8_sha256'] = sha(text.encode('utf-8'))
        isolation = outcome.get('isolation') or {}
        receipt.update(exit_code=outcome.get('exit_code'), reason=outcome.get('reason'),
                       cleanup_error=outcome.get('cleanup_error'),
                       transport_error=outcome.get('error'),
                       tool_seconds=outcome.get('elapsed_seconds'),
                       isolation=isolation, memory_peak=isolation.get('memory_peak'),
                       cgroup_path=isolation.get('path'),
                       pipes_closed=outcome.get('pipes_closed'),
                       direct_process_exited=outcome.get('direct_process_exited'),
                       local_quiescent=outcome.get('local_quiescent'))
        failures = pass_failures(outcome)
        receipt['pass_failures'] = failures
        require(not failures, 'clean successful execution: ' + ','.join(failures))
        report = verify_report(command, outcome['stdout'])
        receipt['artifacts'] = extract_artifacts(report, directory)
        require(postcheck(candidate, cache, command, policy_sha, manifest_sha,
                          activation_sha),
                'post-execution source pin drift')
        receipt['post_execution_pin_ok'] = True
        receipt['status'] = 'PASS_LOCAL_RESEARCH_ONLY'
    except mods['foundry_tools'].ToolUncertain as exc:
        obs = exc.observation
        for name in ('stdout', 'stderr'):
            if type(obs.get(name)) is str:
                put_bytes(directory / (name + '.log'), obs[name].encode('utf-8'))
                receipt[name + '_decoded_utf8_sha256'] = sha(obs[name].encode('utf-8'))
        receipt.update(status='UNKNOWN_RETAINED', exit_code=obs.get('exit_code'),
                       reason=obs.get('reason'), cleanup_error=obs.get('cleanup_error'),
                       isolation=obs.get('isolation'),
                       pipes_closed=obs.get('pipes_closed'),
                       direct_process_exited=obs.get('direct_process_exited'),
                       local_quiescent=False)
        errors.append('uncertain cleanup; reservation retained; no refund')
    except BaseException as exc:
        receipt.update(status='FAILED_RETAINED', error=repr(exc))
        errors.append(repr(exc))
    finally:
        if 'post_execution_pin_ok' not in receipt:
            receipt['post_execution_pin_ok'] = postcheck(
                candidate, cache, command, policy_sha, manifest_sha, activation_sha)
        receipt.update(finished_at=now().isoformat(),
                       seconds=time.monotonic() - begin)
        finalize(directory, receipt, errors)
        print(json.dumps({'receipt': (directory / 'execution.json').as_posix(),
                          'receipt_sha256': sha((directory / 'execution.json').read_bytes()),
                          'status': receipt['status']}), flush=True)
    require(not errors, 'retained failed/unknown attempt: ' + command['id'])
    return receipt


if __name__ == '__main__':
    require(len(sys.argv) == 2, 'usage: native_local.py <command-id>')
    admit(sys.argv[1])
