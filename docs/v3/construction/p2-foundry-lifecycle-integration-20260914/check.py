"""Exact union/scope and bounded native composition gate; no operational admission."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[4]
DIRECTORY = "docs/v3/construction/p2-foundry-lifecycle-integration-20260914"
TASK_BASE = "be3ee96353f16cf84df38397120e324c7204b8f3"
COMMON = "e627cd93bac473094bc99e8fa29c8d62bae526a2"
HOST = "3b4865a19516abd6289d3509077743f65233ca80"
OBSERVATION = "881e3252ee21564da02beba5990fcaf4bfb60b14"
ALLOWED = {
    "tools/construction_swarm/p2_foundry_lifecycle.py",
    "tools/construction_swarm/test_p2_foundry_lifecycle.py",
    DIRECTORY + "/SPEC.md", DIRECTORY + "/PROGRESS.md", DIRECTORY + "/check.py",
}
BRANCH = "codex/p2-foundry-lifecycle-integration-20260914"


def require(value, message):
    if not value:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=15).decode().strip()


def tree(commit):
    result = {}
    for row in git("ls-tree", "-r", commit).splitlines():
        metadata, name = row.split("\t", 1)
        mode, kind, blob = metadata.split()
        require(kind == "blob" and mode in {"100644", "100755"}, "ordinary source blobs only")
        result[name] = (mode, blob)
    return result


def preserve(before, after, additions):
    require(set(after) == set(before) | additions, "exact additive scope required")
    require(not set(before) & additions, "additions overlap inherited source")
    require(all(after[path] == value for path, value in before.items()), "inherited source changed")


def source_check(candidate):
    require(re.fullmatch("[0-9a-f]{40}", candidate), "full candidate SHA required")
    require(git("rev-parse", "HEAD") == candidate, "candidate must equal HEAD")
    require(git("branch", "--show-current") == BRANCH, "integration branch required")
    require(not git("status", "--porcelain=v1", "--untracked-files=all"), "clean candidate required")
    require(git("rev-list", "--parents", "-n", "1", TASK_BASE).split() == [TASK_BASE, HOST, OBSERVATION],
            "exact reviewed merge parents required")
    git("merge-base", "--is-ancestor", TASK_BASE, candidate)
    common, base, actual = tree(COMMON), tree(TASK_BASE), tree(candidate)
    combined = dict(common)
    imported = set()
    for revision, count in ((HOST, 5), (OBSERVATION, 4)):
        original = tree(revision)
        additions = set(original) - set(common)
        require(len(additions) == count and not additions & imported, "disjoint reviewed imports")
        preserve(common, original, additions)
        imported.update(additions)
        combined.update({path: original[path] for path in additions})
    require(base == combined, "combined base differs from reviewed union")
    preserve(base, actual, ALLOWED)
    git("diff", "--check", TASK_BASE, candidate)
    hashes = {}
    for name, (mode, blob) in actual.items():
        path = ROOT / name
        require(not path.is_symlink() and path.is_file(), "source path type changed: " + name)
        data = path.read_bytes()
        require(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == blob,
                "working bytes differ from commit: " + name)
        require(bool(path.stat().st_mode & 0o111) == (mode == "100755"),
                "working executable mode differs: " + name)
        hashes[name] = hashlib.sha256(data).hexdigest()
    controls = 0
    altered = dict(actual)
    altered[next(iter(base))] = ("100644", "0" * 40)
    missing = dict(actual)
    del missing[next(iter(base))]
    for mutant in (altered, missing, actual | {"unexpected": ("100644", "0" * 40)}):
        try:
            preserve(base, mutant, ALLOWED)
        except ValueError:
            controls += 1
        else:
            raise ValueError("source negative control escaped")
    return {
        "candidate": candidate, "tree": git("rev-parse", candidate + "^{tree}"),
        "task_base": TASK_BASE, "reviewed_inputs": [HOST, OBSERVATION],
        "imported_files": len(imported), "preserved_files": len(base),
        "allowed_additions": sorted(ALLOWED), "source_controls": controls,
        "working_sha256": hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(),
    }


def load_guard():
    path = ROOT / "docs/v3/construction/integration-20260914/check.py"
    spec = importlib.util.spec_from_file_location("preserved_integration_guard", path)
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)

    class FixtureSession(guard.OwnedSession):
        """The old guard owns sessions; this addition cleans fixed fixture cgroups.

        Lifecycle service children explicitly start new sessions. Their test-owned
        domains are named by the unreaped gate-child PID, and cannot be confused
        with another concurrent gate's domains. No production cgroup is searched.
        """
        def __init__(self, process):
            self.fixture_lock = threading.Lock()
            self.fixture_report = None
            super().__init__(process)

        def cleanup(self, reason):
            with self.fixture_lock:
                if self.fixture_report is not None:
                    return self.fixture_report
                # First stop/reap the session's controllers so they cannot restart a service.
                result = dict(super().cleanup(reason))
                leftovers, errors = [], []
                root = Path("/sys/fs/cgroup")
                names = (f"p2fi-test-{self.process.pid}-",
                         f"recursion-p2-test-{self.process.pid}-")
                for path in root.iterdir():
                    if not path.is_dir() or not any(path.name.startswith(x) for x in names):
                        continue
                    leftovers.append(str(path))
                    try:
                        children = [child for child in path.iterdir() if child.is_dir()]
                        require(len(children) <= 32, "fixture cleanup domain bound")
                        for domain in children:
                            (domain / "cgroup.kill").write_text("1", encoding="ascii")
                        end = time.monotonic() + 2
                        for domain in children:
                            while "populated 1" in (domain / "cgroup.events").read_text():
                                require(time.monotonic() < end, "fixture cleanup timeout")
                                time.sleep(.01)
                            domain.rmdir()
                        path.rmdir()
                    except Exception as exc:
                        errors.append(str(exc))
                result.update(fixture_cgroups_cleaned=leftovers, fixture_cleanup_errors=errors)
                result["quiescent"] = result["quiescent"] and not errors
                self.fixture_report = result
                return result

    guard.OwnedSession = FixtureSession
    return guard


def run_command(guard, output, name, args, marker, seconds=60):
    # Leave additional time for cgroup cleanup within the packet's 120-second ceiling.
    result, captured = guard.guarded_command(name, args, seconds - 4, output, 2 * 1024 * 1024)
    text = captured.decode("utf-8", "replace")
    require(result["reason"] == "completed" and result["exit_code"] == 0,
            name + " failed; see retained output")
    require(not result["cleanup"]["fixture_cgroups_cleaned"],
            name + " left fixture cgroups; gate cleaned and refused")
    require(marker in text and "skipped" not in text.lower(), name + " missing/skip evidence")
    return result


def cgroup_timeout_control(guard, output):
    # Fixed inert descendant escapes the session, but remains in its owned fixture domain.
    program = (
        "from pathlib import Path; import os,subprocess,sys,time; "
        "r=Path('/sys/fs/cgroup')/('p2fi-test-'+str(os.getpid())+'-guard'); r.mkdir(); "
        "(r/'cgroup.subtree_control').write_text('+pids'); d=r/'service'; d.mkdir(); "
        "(d/'pids.max').write_text('8'); "
        "subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(10)'],"
        "start_new_session=True,preexec_fn=lambda:(d/'cgroup.procs').write_text(str(os.getpid()))); "
        "print('OWNED_CGROUP',flush=True); time.sleep(10)"
    )
    result, captured = guard.guarded_command("guard-cgroup-timeout", ["-c", program], 1, output, 4096)
    require(result["reason"] == "timeout" and b"OWNED_CGROUP" in captured, "cgroup timeout control")
    require(result["cleanup"]["quiescent"] and len(result["cleanup"]["fixture_cgroups_cleaned"]) == 1,
            "escaped fixture session was not cleaned")
    require(result["elapsed_seconds"] < 5, "bounded escaped-session cleanup")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(sys.platform == "linux", "native Linux/WSL required")
    output = args.output.resolve()
    require(not output.exists() and not output.is_relative_to(ROOT), "fresh external evidence directory")
    output.mkdir(parents=True)
    record = {"status": "FAILED_RETAINED", "candidate": args.candidate, "commands": [],
              "provider_calls": 0, "scientific_execution": False, "fleet_activation": False,
              "production_service_activation": False}
    try:
        binding = source_check(args.candidate)
        record["binding"] = binding
        guard = load_guard()
        record["cgroup_guard_control"] = cgroup_timeout_control(guard, output)
        commands = [
            ("handoff", ["docs/v3/construction/next-work-20260914/check_handoff.py"],
             "HANDOFF_SOURCE_PASS", 60),
            ("composition", ["-m", "unittest", "-v",
                             "tools.construction_swarm.test_p2_foundry_lifecycle"],
             "Ran 14 tests", 120),
            ("regressions", ["-m", "unittest", "-v",
                             "tools.construction_swarm.test_p1_core",
                             "tools.construction_swarm.test_p2_access",
                             "tools.construction_swarm.test_p2_host_lifecycle",
                             "tools.construction_swarm.test_p2_foundry_observation.FoundryObservationTests"],
             "Ran 75 tests", 120),
        ]
        for name, arguments, marker, seconds in commands:
            record["commands"].append(run_command(guard, output, name, arguments, marker, seconds))
        require(source_check(args.candidate) == binding, "source changed during gate")
        record["status"] = "FOUNDRY_LIFECYCLE_INTEGRATION_PASS"
        record["composition_tests"] = 14
        record["regression_tests"] = 75
    except BaseException as exc:
        record["error"] = repr(exc)
        raise
    finally:
        (output / "receipt.json").write_text(json.dumps(record, sort_keys=True, indent=2) + "\n")
        print(json.dumps(record, sort_keys=True))


if __name__ == "__main__":
    main()