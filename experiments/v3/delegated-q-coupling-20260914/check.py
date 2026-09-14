"""Source/fake preflight and fail-closed scientific admission interface."""
import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = '0c908f6833e715af0eaa01b6f6788120eb577efd'
CODE = 'experiments/v3/delegated-q-coupling-20260914'
DOC = 'docs/v3/construction/delegated-q-coupling-20260914'
PLAN = DOC + '/plan.json'
ALLOWED = {CODE + '/' + x for x in ('relation.py', 'check.py', 'audit.py', 'test_contract.py')} | {DOC + '/' + x for x in ('SPEC.md', 'plan.json', 'PROGRESS.md')}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(['git', '-c', 'core.longpaths=true', *args], cwd=ROOT, timeout=15).decode('utf8').strip()


def hash_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def literal(path, name):
    tree = ast.parse((ROOT / path).read_text(encoding='utf8'))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError('missing literal source declaration: ' + path + ':' + name)


def field_inventory():
    c = 'experiments/v3/coupled-construction/c_domain.py'
    p = 'experiments/v3/coupled-cut-pause/p_domain.py'
    q = 'experiments/v3/cut-publication/q_domain.py'
    s = 'experiments/v3/cut-source-overnight/s_domain.py'
    common = literal(c, 'AUTH') + literal(p, 'EXTRA') + literal(q, 'EXTRA') + literal(c, 'FLOW') + literal(c, 'VIEW')
    return dict(common=[x for x in common if x not in ('done', 'decision')],
                journal=list(literal(s, 'EXTRA')) + ['source_generation'],
                separate=['done', 'decision', 'invocations'], exception=['staged'])


def domain():
    setup = ['admitA', 'intent', 'send', 'remote', 'lose', 'query', 'register:success', 'attempt:1',
             'append:success:0:normal', 'append:success:1:normal', 'append:success:2:normal']
    core = ['collect-open', 'collect:0', 'collect:1', 'collect:2', 'attempt:2', 'attempt:3', 'attempt:4', 'source-restart']
    suffix = ['cut:success', 'cut-deliver', 'source-attest', 'stage', 'pub-commit',
              'reader-request:0', 'reader-pin:0', 'reader-copy:0', 'reader-wait:0',
              'reader-release:0', 'reader-install:0', 'join-cut', 'classify', 'reconcile', 'admitB']
    actions = [verb + '@' + str(i) for i, verb in enumerate(setup + core + suffix)]
    dependencies = {}
    for i, action in enumerate(actions):
        dependencies[action] = ([] if i == 0 else [actions[i - 1]] if i < 11 or i > 19
                                else actions[11:19] if i == 19 else [actions[10]])
    profile = dict(actions=actions, requires=dependencies, outcomes=[1], policy='pending', queue='bounded_scaling')
    cases = []
    for slot in range(8):
        local = actions[11:18].copy()
        local.insert(slot, actions[18])
        order = actions[:11] + local + actions[19:]
        for unit in ('event', 'utf8-byte'):
            cases.append(dict(id='restart-slot-' + str(slot) + '/' + unit + '/1', unit=unit, actions=order,
                              order_sha256=hash_json(order)))
    return profile, cases


def expected_plan():
    profile, cases = domain()
    histories, events = len(cases), sum(len(x['actions']) for x in cases)
    prefixes = events + histories
    construction = dict(state_visits_per_representation=2 * prefixes,
                        state_visits_all_representations=4 * prefixes,
                        typed_initial_reference_states=2 * histories,
                        reducer_wrapper_calls=4 * events, transition_audit_calls=2 * events,
                        relation_checks=prefixes, timeout_seconds=2 * histories + 4,
                        output_bytes=(histories + 1) * 1048576)
    audit = dict(restored_state_visits=2 * prefixes, typed_initial_reference_states=2 * histories,
                 material_state_checks=2 * prefixes, transition_audit_calls=2 * events,
                 relation_checks=prefixes, timeout_seconds=histories + 4, output_bytes=1048576)
    return dict(format='delegated-q-plan/1', TASK_BASE=BASE,
                parent='goal-recursion-v2-execution-fabric',
                completeness='all-eight-restart-positions-both-units-all-prefixes',
                input_closure={'kind': 'entire-immutable-TASK_BASE-tree', 'git_tree': git('rev-parse', BASE + '^{tree}'),
                               'external_historical_receipts': 'missing-not-substituted'},
                fields=field_inventory(), profile=profile, cases=cases,
                accounting=dict(histories=histories, events=events, paired_prefixes=prefixes,
                                construction=construction, certificate_audit=audit,
                                scientific_bundles=3, independent_scientific_reviewer_reruns=2,
                                aggregate_new_state_visits=3 * (4 * prefixes + 2 * prefixes + 4 * histories),
                                aggregate_transition_audit_calls=3 * 4 * events,
                                aggregate_material_state_checks=3 * 2 * prefixes,
                                aggregate_reducer_wrapper_calls=3 * 4 * events,
                                aggregate_seconds=3 * (construction['timeout_seconds'] + audit['timeout_seconds']),
                                aggregate_output_bytes=3 * (construction['output_bytes'] + audit['output_bytes']),
                                nonrefundable=True, inherited_inner_calls='requires-controller-metering-proof',
                                historical_charge_total=None, historical_unknown_remainder='unresolved'),
                construction_limits=dict(provider_calls=0, inherited_state_visits=0, fake_certificates=1024,
                                         seconds_per_command=60, output_bytes=33554432),
                admission=dict(status='not-admitted', trusted_controller=None, finite_grant=None,
                               independently_accepted_accounting_proof=None, exact_candidate_reviews=[]),
                proposition=dict(status='unexecuted', inductive_proof=False, conditional_argument=True,
                                 original_scale_coverage=False, accepted_relations_changed=False))


def validate_plan(value):
    require(json.dumps(value, sort_keys=True, allow_nan=False) == json.dumps(expected_plan(), sort_keys=True, allow_nan=False), 'exact typed prospective domain, full fields, closure and additive accounting')
    require(len(value['fields']['common']) == len(set(value['fields']['common'])), 'unique common fields')
    require(len(value['cases']) == 16 and value['accounting']['paired_prefixes'] == 560, 'complete finite domain')
    for case in value['cases']:
        seen = set()
        for action in case['actions']:
            require(action not in seen and set(value['profile']['requires'][action]) <= seen, 'enabled literal schedule')
            seen.add(action)
        require(seen == set(value['profile']['actions']), 'no omitted suffix or setup')


def source_gate(candidate, spec):
    require(re.fullmatch('[0-9a-f]{40}', candidate) is not None, 'full candidate SHA required')
    require(git('rev-parse', 'HEAD') == candidate, 'candidate must equal current HEAD')
    require(not git('status', '--porcelain', '--untracked-files=all'), 'clean exact candidate required')
    require(Path(spec).resolve() == (ROOT / PLAN).resolve(), 'committed plan path only')
    require(not git('diff', '--check', BASE, candidate), 'whitespace gate')
    changes = git('diff', '--name-status', '--no-renames', BASE, candidate).splitlines()
    require({line.split('\t')[1] for line in changes} == ALLOWED and all(line.startswith('A\t') for line in changes), 'seven additive allowed paths only')
    require(subprocess.run(['git', 'merge-base', '--is-ancestor', BASE, candidate], cwd=ROOT, timeout=10).returncode == 0, 'TASK_BASE ancestry')
    # Check actual bytes, including tracked files with assume-unchanged/skip-worktree.
    # Git checkout's CRLF conversion is the only accepted text normalization.
    raw_pins = {}
    for line in git('ls-tree', '-r', candidate).splitlines():
        meta, name = line.split('\t', 1)
        mode, kind, oid = meta.split()
        require(kind == 'blob' and mode in ('100644', '100755'), 'ordinary source file closure')
        path = ROOT / name
        require(not path.is_symlink(), 'no source symlink')
        # Windows checkout supports long paths per-command; the interpreter may
        # still need its explicit extended-length prefix for preserved deep files.
        readable = Path('\\\\?\\' + str(path)) if os.name == 'nt' else path
        raw = readable.read_bytes()
        valid = False
        for data in (raw, raw.replace(b'\r\n', b'\n')):
            blob = b'blob ' + str(len(data)).encode() + b'\0' + data
            valid |= hashlib.sha1(blob).hexdigest() == oid
        require(valid, 'working source bytes changed: ' + name)
        raw_pins[name] = hashlib.sha256(raw).hexdigest()
    value = json.loads((ROOT / PLAN).read_text(encoding='utf8'))
    validate_plan(value)
    contract = json.loads((ROOT / 'docs/v3/foundation-research/mark2-research/mark3-comparison/comparison-contract.json').read_text(encoding='utf8'))
    require(len(contract['obligations']) == 6 and len(contract['traces']) == 27, 'six obligations and 27 trace rows')
    return dict(candidate=candidate, task_base=BASE, plan_sha256=raw_pins[PLAN],
                source_digest=hash_json(raw_pins), source_files=len(raw_pins))


def refuse_scientific_admission(mode, receipt=None):
    raise ValueError(mode + ': no fresh trusted controller/finite grant/accounting proof; historical receipts and charge reconciliation missing; two exact candidate reviews and live resource/account observations required. No scientific import or execution occurred.')


def arm_fake_deadline(output, seconds=59):
    """Own this inert gate and its subprocesses; terminate before the 60s cap.

    This is a short local fake/source gate guard, not scientific admission or the
    historical controller's resource/accounting proof. Windows nested job membership
    contains only this Python process and descendants, never its Codex parent.
    """
    require(0 < seconds <= 59, 'finite fake gate deadline')
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        api = ctypes.WinDLL('kernel32', use_last_error=True)
        api.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        api.CreateJobObjectW.restype = wintypes.HANDLE
        api.GetCurrentProcess.argtypes = []
        api.GetCurrentProcess.restype = wintypes.HANDLE
        api.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        api.AssignProcessToJobObject.restype = wintypes.BOOL
        api.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
        api.TerminateJobObject.restype = wintypes.BOOL
        job = api.CreateJobObjectW(None, None)
        require(bool(job) and bool(api.AssignProcessToJobObject(job, api.GetCurrentProcess())),
                'cannot own fake gate process job: ' + str(ctypes.get_last_error()))
        terminate = lambda: api.TerminateJobObject(job, 124)
    else:
        import signal
        os.setpgid(0, 0)
        require(os.getpgrp() == os.getpid(), 'own fake gate process group')
        terminate = lambda: os.killpg(os.getpid(), signal.SIGKILL)
    def expired():
        # Termination must not wait on a slow output filesystem or stdout pipe.
        killer = threading.Timer(0.25, lambda: (terminate(), os._exit(124)))
        killer.daemon = True
        killer.start()
        record = dict(status='FAKE_GATE_TIMEOUT', deadline_seconds=seconds,
                      inherited_state_visits=0, provider_calls=0, failed_attempt_retained=True)
        try:
            output.mkdir(parents=True, exist_ok=True)
            (output / 'deadline-failure.json').write_text(json.dumps(record) + '\n', encoding='utf8')
            print(json.dumps(record), flush=True)
        finally:
            terminate()
            os._exit(124)
    timer = threading.Timer(seconds, expired)
    timer.daemon = True
    timer.start()
    return timer


def main():
    start = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('preflight', 'execute'), required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--spec', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    require(not output.is_relative_to(ROOT.resolve()) and not output.exists(), 'fresh external output directory')
    output.mkdir(parents=True, exist_ok=False)
    deadline = arm_fake_deadline(output)
    record = dict(candidate=args.candidate, mode=args.mode, status='PREFLIGHT_FAILED',
                  provider_calls=0, inherited_state_visits=0, proposition='unexecuted')
    exit_code = 2
    try:
        binding = source_gate(args.candidate, args.spec)
        record['binding'] = binding
        if args.mode == 'execute':
            refuse_scientific_admission('execute')
        import test_contract
        record['fake_gate'] = test_contract.run()
        require(record['fake_gate']['status'] == 'FAKE_CONTRACT_PASS', 'mandatory fake controls')
        require(binding == source_gate(args.candidate, args.spec), 'candidate changed during gate')
        require(time.monotonic() - start < 60, '60 second preflight bound')
        record.update(status='PROPOSED_EXPERIMENT_PASS', proved_proposition=False, scientific_admission=False)
        exit_code = 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        record['reason'] = str(error)
    finally:
        record['elapsed_seconds'] = round(time.monotonic() - start, 3)
        content = json.dumps(record, sort_keys=True, indent=2) + '\n'
        require(len(content.encode()) < 33554432, 'output byte bound')
        (output / 'receipt.json').write_text(content, encoding='utf8')
        print(json.dumps(record, sort_keys=True))
        deadline.cancel()
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
