"""Exact source composition and inert regression gate; no scientific admission."""
import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import select
import signal
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[4]
DIRECTORY = "docs/v3/construction/integration-20260914/"
MANIFEST = ROOT / DIRECTORY / "manifest.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(
        ["git", "-c", "core.longpaths=true", *args], cwd=ROOT, timeout=30
    ).decode("utf8").strip()


def tree(revision):
    result = {}
    for line in git("ls-tree", "-r", revision).splitlines():
        meta, name = line.split("\t", 1)
        mode, kind, oid = meta.split()
        require(kind == "blob" and mode in ("100644", "100755"), "ordinary source blobs only")
        result[name] = (mode, oid)
    return result


def verify_composition(actual, baseline, imported, integration):
    require(set(actual) == set(baseline) | set(imported) | set(integration), "exact combined path union")
    require(not (set(baseline) & set(imported)), "imports must be additive")
    require(not (set(integration) & (set(baseline) | set(imported))), "integration paths must be additive")
    for path, expected in (baseline | imported).items():
        require(actual[path] == expected, "preserved mode/blob changed: " + path)


def composition_controls(actual, baseline, imported, integration):
    cases = {}
    path = next(iter(imported))
    cases["changed-imported-blob"] = actual | {path: (actual[path][0], "0" * 40)}
    path = next(iter(baseline))
    cases["changed-baseline-blob"] = actual | {path: (actual[path][0], "0" * 40)}
    cases["extra-path"] = actual | {"unexpected-integration-file": ("100644", "0" * 40)}
    missing = dict(actual)
    del missing[next(iter(imported))]
    cases["missing-import"] = missing
    for name, forged in cases.items():
        try:
            verify_composition(forged, baseline, imported, integration)
        except ValueError:
            continue
        raise ValueError("composition control not rejected: " + name)
    return list(cases)


def source_check(candidate, evidence_root, manifest):
    require(re.fullmatch("[0-9a-f]{40}", candidate) is not None, "full candidate SHA required")
    require(git("rev-parse", "HEAD") == candidate, "candidate must equal HEAD")
    require(not git("status", "--porcelain=v1", "--untracked-files=all"), "clean candidate required")
    git("merge-base", "--is-ancestor", manifest["observed_master"], manifest["task_base"])
    git("merge-base", "--is-ancestor", manifest["task_base"], candidate)
    git("diff", "--check", manifest["task_base"], candidate)
    baseline = tree(manifest["task_base"])
    imported = {}
    for origin in manifest["origins"]:
        oid = origin["candidate"]
        git("merge-base", "--is-ancestor", manifest["task_base"], oid)
        git("merge-base", "--is-ancestor", oid, candidate)
        require(git("rev-parse", oid + "^{tree}") == origin["tree"], "origin tree pin")
        origin_tree = tree(oid)
        paths = set(origin["paths"])
        require(len(paths) == len(origin["paths"]), "unique origin paths")
        verify_composition(origin_tree, baseline, {p: origin_tree[p] for p in paths}, [])
        require(not paths & set(imported), "disjoint origin changes")
        imported.update({p: origin_tree[p] for p in paths})
    actual = tree(candidate)
    verify_composition(actual, baseline, imported, manifest["integration_paths"])
    controls = composition_controls(actual, baseline, imported, manifest["integration_paths"])
    working_hashes = {}
    for name, (_mode, oid) in actual.items():
        path = ROOT / name
        require(not path.is_symlink(), "no source symlink: " + name)
        readable = Path("\\\\?\\" + str(path)) if os.name == "nt" else path
        raw = readable.read_bytes()
        valid = False
        for content in (raw, raw.replace(b"\r\n", b"\n")):
            blob = b"blob " + str(len(content)).encode() + b"\0" + content
            valid |= hashlib.sha1(blob).hexdigest() == oid
        require(valid, "working bytes differ from candidate: " + name)
        working_hashes[name] = hashlib.sha256(raw).hexdigest()
    evidence = {}
    for item in manifest["intake_evidence"]:
        path = evidence_root / item["name"]
        require(path.is_file() and not path.is_symlink(), "required intake evidence missing")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == item["sha256"], "intake evidence digest: " + item["name"])
        evidence[item["name"]] = digest
    return {
        "candidate": candidate,
        "tree": git("rev-parse", candidate + "^{tree}"),
        "working_digest": hashlib.sha256(json.dumps(working_hashes, sort_keys=True).encode()).hexdigest(),
        "baseline_files": len(baseline),
        "imported_files": len(imported),
        "source_files": len(actual),
        "origins": {x["id"]: x["candidate"] for x in manifest["origins"]},
        "intake_evidence": evidence,
        "composition_controls": controls,
    }


def load_component(path, name):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def component_check(component):
    if component == "ledger":
        module = load_component(ROOT / "experiments/v3/recovery-ledger-20260914/check.py", "ledger_gate")
        tests = module.load_tests()
        prefixes = module.prefix_audit(tests)
        mutants = module.independent_mutations(tests)
        components = module.component_guard_audit(tests)
        resets = module.reset_scope_audit(tests)
        module.subprocess_gate(tests)
        result = dict(prefixes=prefixes, mutations=len(mutants), component_guards=len(components), reset_guards=resets)
        require(result == dict(prefixes=21, mutations=6, component_guards=3, reset_guards=3), "ledger audit inventory")
    else:
        directory = ROOT / "experiments/v3/delegated-q-coupling-20260914"
        checks = load_component(directory / "check.py", "check")
        checks.validate_plan(json.loads((ROOT / "docs/v3/construction/delegated-q-coupling-20260914/plan.json").read_text()))
        tests = load_component(directory / "test_contract.py", "test_contract")
        result = tests.run()
        require(result["status"] == "FAKE_CONTRACT_PASS", "DQ fake gate")
        require(len(result["controls"]) == 40 and all(x["detected"] is True for x in result["controls"]), "DQ controls")
        require(result["valid_fixtures"] == 3 and result["fake_certificates"] == 31, "DQ fixture inventory")
        require(result["inherited_state_visits"] == result["provider_calls"] == 0, "inert DQ only")
        result["plan_validated"] = True
    print(json.dumps(dict(status="COMPONENT_CHECK_PASS", component=component, result=result)))


def require_linux_guard():
    require(sys.platform == "linux" and hasattr(os, "pidfd_open") and
            hasattr(signal, "pidfd_send_signal") and Path("/proc/self/stat").is_file(),
            "full integration gate requires Linux with procfs/pidfds; Windows callers must explicitly invoke it through wsl.exe")
    # Adopt only orphan descendants of this gate so killed grandchildren can be
    # reaped rather than left to an unrelated init. No host/service setting changes.
    libc = ctypes.CDLL(None, use_errno=True)
    require(libc.prctl(36, 1, 0, 0, 0) == 0, "cannot enable process-local child subreaper")


def process_identity(pid):
    # comm may contain spaces and parentheses. Fields after its final ')' start at state.
    try:
        fields = Path("/proc").joinpath(str(pid), "stat").read_text().rsplit(")", 1)[1].split()
    except FileNotFoundError:
        return None
    return dict(pid=pid, start=int(fields[19]), session=int(fields[3]),
                process_group=int(fields[2]), state=fields[0])


class OwnedSession:
    """Contain this command's Linux session, including descendants with a new pgid.

    Children of these fixed inert gates may change process groups, but do not create
    new sessions. The leader remains unreaped until cleanup so its session ID cannot
    be recycled. Signals use pidfds checked against both start time and session ID.
    """

    def __init__(self, process):
        self.process = process
        self.session = process.pid
        self.handles = {}
        self.lock = threading.Lock()
        self.report = None
        identity = process_identity(process.pid)
        require(identity is not None and identity["session"] == self.session,
                "command did not enter its owned session")
        self.leader_start = identity["start"]
        self.discover()
        self.leader_fd = self.handles[(process.pid, self.leader_start)]

    def discover(self):
        members = []
        for entry in Path("/proc").iterdir():
            if not entry.name.isdecimal():
                continue
            identity = process_identity(int(entry.name))
            if identity is None or identity["session"] != self.session:
                continue
            key = (identity["pid"], identity["start"])
            if key not in self.handles:
                try:
                    descriptor = os.pidfd_open(identity["pid"])
                except ProcessLookupError:
                    continue
                current = process_identity(identity["pid"])
                if current is None or current["start"] != identity["start"] or current["session"] != self.session:
                    os.close(descriptor)
                    continue
                self.handles[key] = descriptor
            members.append(identity)
        return members

    def send(self, member, sig):
        current = process_identity(member["pid"])
        if current is None or current["start"] != member["start"] or current["session"] != self.session:
            return
        try:
            signal.pidfd_send_signal(self.handles[(member["pid"], member["start"])], sig)
        except ProcessLookupError:
            pass

    def leader_exited(self):
        return bool(select.select([self.leader_fd], [], [], 0)[0])

    def cleanup(self, reason):
        # Called independently by the deadline thread; no output/file operation is
        # allowed to hold this lock or delay the first termination signal.
        with self.lock:
            if self.report is not None:
                return self.report
            started = time.monotonic()
            initial = self.discover()
            # Freeze every known live member, discover children created during the
            # scan, and repeat before killing. A changed pgid does not escape this.
            previous = None
            while time.monotonic() - started < 0.5:
                members = self.discover()
                live = [x for x in members if x["state"] not in ("Z", "X")]
                for member in live:
                    self.send(member, signal.SIGSTOP)
                keys = {(x["pid"], x["start"]) for x in members}
                if keys == previous and all(x["state"] in ("T", "t", "Z", "X") for x in members):
                    break
                previous = keys
                time.sleep(0.005)
            for member in self.discover():
                self.send(member, signal.SIGKILL)
            survivors = []
            reaped = []
            while time.monotonic() - started < 1.0:
                members = self.discover()
                survivors = [x for x in members if x["state"] not in ("Z", "X")]
                descendants = [x for x in members if x["pid"] != self.process.pid]
                for member in descendants:
                    # waitpid only targets a start/session-verified owned child.
                    current = process_identity(member["pid"])
                    if current is not None and current["start"] == member["start"] and current["session"] == self.session:
                        try:
                            pid, _status = os.waitpid(member["pid"], os.WNOHANG)
                            if pid:
                                reaped.append(member)
                        except ChildProcessError:
                            pass  # Its killed parent has not yet reparented it.
                if not survivors and not descendants:
                    break
                for member in survivors:
                    self.send(member, signal.SIGKILL)
                time.sleep(0.005)
            remaining = self.discover()
            descendants = [x for x in remaining if x["pid"] != self.process.pid]
            survivors = [x for x in remaining if x["state"] not in ("Z", "X")]
            self.report = dict(reason=reason, session=self.session,
                               leader_start=self.leader_start, observed=initial,
                               identities=[dict(pid=p, start=s) for p, s in sorted(self.handles)],
                               live_survivors=survivors,
                               unreaped_descendants=descendants, reaped_descendants=reaped,
                               quiescent=not survivors and not descendants,
                               cleanup_seconds=round(time.monotonic() - started, 4))
            return self.report

    def close(self):
        for descriptor in self.handles.values():
            os.close(descriptor)


def guarded_command(name, arguments, timeout, output, limit=33554432):
    require_linux_guard()
    require(0 < timeout <= 120 and 0 < limit <= 33554432, "finite command bounds")
    started = time.monotonic()
    process = subprocess.Popen([sys.executable, "-X", "utf8", "-B", *arguments],
                               cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               start_new_session=True)
    owned = OwnedSession(process)
    os.set_blocking(process.stdout.fileno(), False)
    expired = threading.Event()
    deadline_error = []

    def deadline():
        expired.set()
        try:
            owned.cleanup("timeout")
        except BaseException as error:
            deadline_error.append(repr(error))

    # Real gate limits include one second of cleanup plus bounded leader reaping.
    # The sub-second fault probes separately require total duration below 2s.
    run_seconds = timeout - 1.5 if timeout >= 2 else timeout
    timer = threading.Timer(max(0, run_seconds - (time.monotonic() - started)), deadline)
    timer.daemon = True
    timer.start()
    captured = bytearray()
    reason = "completed"
    try:
        while True:
            if expired.is_set():
                reason = "timeout"
                break
            ready = select.select([process.stdout], [], [], 0.01)[0]
            if ready:
                chunk = os.read(process.stdout.fileno(), min(65536, limit - len(captured) + 1))
                if chunk:
                    room = limit - len(captured)
                    captured.extend(chunk[:room])
                    if len(chunk) > room:
                        reason = "output_limit"
                        break
                    continue
            if owned.leader_exited():
                # Drain any bytes already buffered, bounded by the same capture cap.
                while True:
                    try:
                        chunk = os.read(process.stdout.fileno(), min(65536, limit - len(captured) + 1))
                    except BlockingIOError:
                        break
                    if not chunk:
                        break
                    room = limit - len(captured)
                    captured.extend(chunk[:room])
                    if len(chunk) > room:
                        reason = "output_limit"
                        break
                break
    finally:
        cleanup = owned.cleanup(reason)
        timer.cancel()
        timer.join()
        process.stdout.close()
        # Cleanup has killed all owned live processes before reaping the leader.
        try:
            exit_code = process.wait(timeout=0.2)
        except subprocess.TimeoutExpired:
            exit_code = None
        owned.close()
        if expired.is_set():
            reason = "timeout"
        if reason == "completed" and any(x["pid"] != process.pid and x["state"] not in ("Z", "X")
                                          for x in cleanup["observed"]):
            reason = "leftover_descendant"
        result = dict(name=name, reason=reason, exit_code=exit_code,
                      elapsed_seconds=round(time.monotonic() - started, 4),
                      timeout_seconds=timeout, execution_deadline_seconds=run_seconds, output_limit=limit,
                      output_bytes=len(captured), output_sha256=hashlib.sha256(captured).hexdigest(),
                      cleanup=cleanup, deadline_errors=deadline_error)
        (output / (name + ".txt")).write_bytes(captured)
        (output / (name + ".cleanup.json")).write_text(json.dumps(result, indent=2) + "\n")
    require(cleanup["quiescent"] and exit_code is not None and not deadline_error,
            name + " cleanup unverified; retained evidence")
    return result, bytes(captured)


def guard_controls(output):
    # Both probes spawn a child in a distinct process group within the owned session.
    child = "import os,time; os.setpgid(0,0); print('DESCENDANT',os.getpid(),flush=True); time.sleep(10)"
    prefix = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c'," + repr(child) + "]); time.sleep(.05); "
    cases = (("guard-timeout", prefix + "print('PARTIAL',flush=True); time.sleep(10)", .4, 4096, "timeout"),
             ("guard-output", prefix + "print('x'*100000,flush=True); time.sleep(10)", 1, 4096, "output_limit"))
    records = []
    for name, source, timeout, limit, expected in cases:
        result, captured = guarded_command(name, ["-c", source], timeout, output, limit)
        require(result["reason"] == expected and b"DESCENDANT" in captured,
                name + " required refusal/descendant evidence")
        require(result["cleanup"]["quiescent"] and len(result["cleanup"]["identities"]) >= 2,
                name + " descendant cleanup evidence")
        require(len({x["process_group"] for x in result["cleanup"]["observed"]}) >= 2,
                name + " must clean distinct process groups")
        require(result["elapsed_seconds"] < 2 and len(captured) <= limit, name + " short bounded control")
        records.append(result)
    positive, captured = guarded_command("guard-completed", ["-c", "print('GUARD_OK')"], 1, output, 4096)
    require(positive["reason"] == "completed" and positive["exit_code"] == 0 and captured == b"GUARD_OK\n",
            "guard must preserve a successful bounded command")
    records.append(positive)
    return records


def run_gate(name, arguments, timeout, output, marker):
    result, captured = guarded_command(name, arguments, timeout, output)
    require(result["reason"] == "completed" and result["exit_code"] == 0,
            name + " failed; retained output and cleanup evidence")
    text = captured.decode("utf8", "replace")
    require(marker in text and "skipped" not in text.lower(), name + " required evidence absent or skipped")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate")
    parser.add_argument("--evidence-root", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--component", choices=("ledger", "dq"))
    parser.add_argument("--guard-controls", action="store_true")
    args = parser.parse_args()
    if args.component:
        component_check(args.component)
        return
    if args.guard_controls:
        require_linux_guard()
        require(args.output is not None, "guard controls require external output")
        output = args.output.resolve()
        require(not output.exists() and not output.is_relative_to(ROOT), "fresh external output directory")
        output.mkdir(parents=True)
        print(json.dumps(dict(status="GUARD_CONTROLS_PASS", controls=guard_controls(output))))
        return
    require_linux_guard()
    require(args.candidate and args.evidence_root and args.output, "candidate, evidence-root and output required")
    output = args.output.resolve()
    require(not output.exists() and not output.is_relative_to(ROOT), "fresh external output directory")
    output.mkdir(parents=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf8"))
    record = dict(status="INTEGRATION_FAILED", candidate=args.candidate, gates=[],
                  scientific_admission=False, fleet_activation=False, provider_calls=0)
    try:
        binding = source_check(args.candidate, args.evidence_root.resolve(), manifest)
        record["binding"] = binding
        record["guard_controls"] = guard_controls(output)
        commands = [
            ("handoff", ["docs/v3/construction/next-work-20260914/check_handoff.py"], 60, "HANDOFF_SOURCE_PASS"),
            ("p1", ["-m", "unittest", "-v", "tools.construction_swarm.test_p1_core"], 60, "Ran 18 tests"),
            ("p2", ["-m", "unittest", "-v", "tools.construction_swarm.test_p2_access"], 120, "Ran 19 tests"),
            ("ledger", [DIRECTORY + "check.py", "--component", "ledger"], 60, "COMPONENT_CHECK_PASS"),
            ("dq", [DIRECTORY + "check.py", "--component", "dq"], 60, "COMPONENT_CHECK_PASS"),
        ]
        for name, arguments, timeout, marker in commands:
            record["gates"].append(run_gate(name, arguments, timeout, output, marker))
        require(binding == source_check(args.candidate, args.evidence_root.resolve(), manifest), "source/evidence changed during gate")
        record["status"] = "INTEGRATION_SOURCE_AND_INERT_PASS"
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        record["reason"] = str(error)
        raise
    finally:
        (output / "receipt.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf8")
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print("INTEGRATION_GATE_FAILED: " + str(error), file=sys.stderr)
        sys.exit(1)
