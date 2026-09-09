"""Full documentation-slice validation; repeats only unchanged historical checks."""
import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import check_docs as docs

ROOT, PRIOR = docs.ROOT, docs.PRIOR
COMMON = Path(docs.git("rev-parse", "--path-format=absolute", "--git-common-dir"))
OLD = COMMON / "research-attestations/cut-source-overnight"
CACHE = OLD / "reopen-01"
END = dt.datetime.fromisoformat("2026-09-09T15:30:00Z")
require, read, digest = docs.require, docs.read, docs.digest
spec = importlib.util.spec_from_file_location("sc_frozen_owned_job", ROOT / "experiments/v3/cut-source-overnight/run_packet.py")
frozen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frozen)


def now():
    return dt.datetime.now(dt.timezone.utc)


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def scope():
    require(now() < END, "fixed hard deadline")
    require(not (ROOT / "state/PAUSE").exists() and not (COMMON.parent / "state/PAUSE").exists(), "operational PAUSE")
    require("status: active" in (ROOT / "state/goals/goal-recursion-v2-execution-fabric.md").read_text(), "active parent")
    usage = read(CACHE / "usage.json")
    require(0 <= (now() - dt.datetime.fromisoformat(usage["checked_at"])).total_seconds() < 900, "fresh usage required")
    windows = usage["binding_windows"]
    require(windows and all(0 <= w["used_percent"] < 97 and w["remaining_percent"] == 100 - w["used_percent"] for w in windows), "all binding capacity windows")
    require(usage["remaining_percent"] == min(w["remaining_percent"] for w in windows), "binding remaining capacity")
    require(usage["new_metered_spend"] == 0, "no new metered spend")
    ledger = read(CACHE / "reset-ledger.json")
    # This candidate validates the actual unused state. A later reset needs its
    # real receipt incorporated and reviewed, never an invented ledger outcome.
    require(ledger["status"] == "authorized-unused" and ledger["applied_count"] == 0 and ledger["attempts"] == [] and usage["reset_credits_used"] == 0, "actual unused reset ledger; changed state requires revalidation")
    return usage


def history():
    complete = read(OLD / PRIOR / "completion.json")
    counts = {}
    for key, base, count in (("all_external_files_before_completion", OLD / PRIOR, 969), ("parent_external_files", OLD, 14)):
        entries = complete[key]
        require(len(entries) == count, "full historical closure count: " + key)
        for name, expected in entries.items():
            require(now() < END, "deadline during historical verification")
            target = (base / name).resolve()
            require(target.is_relative_to(base.resolve()) and digest(target) == expected, "historical file: " + name)
        counts[key] = len(entries)
    return counts


def git_at(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, timeout=30).decode().strip()


def frozen_roots(rows):
    entries = docs.git("worktree", "list", "--porcelain").split("\n\n")
    output = []
    for row in rows:
        matches = [entry for entry in entries if "branch refs/heads/" + row["branch"] in entry.splitlines()]
        require(len(matches) == 1, "one existing frozen worktree: " + row["branch"])
        root = Path(matches[0].splitlines()[0][9:])
        require(git_at(root, "rev-parse", "HEAD") == row["commit"] and not git_at(root, "status", "--porcelain", "--untracked-files=all"), "clean frozen source: " + row["branch"])
        require(not (root / "state/PAUSE").exists(), "frozen worktree PAUSE")
        output.append((row, root))
    return output


def command(args, root, directory, label):
    usage = scope()
    require((END - now()).total_seconds() > 605, "command and cleanup reserve")
    started = now()
    admission = {"command": args, "root": str(root), "source_commit": git_at(root, "rev-parse", "HEAD"), "started_at": started.isoformat(), "maximum_seconds": 600, "usage": usage, "activity": "unchanged historical validation", "new_counterexample_work": False}
    write(directory / (label + "-admission.json"), admission)
    job, process = None, None
    status, code, error = "not-started", None, None
    begin = time.monotonic()
    try:
        job = frozen.OwnedJob()
        with (directory / (label + ".log")).open("wb") as output:
            process = job.launch(args, cwd=root, stdout=output, stderr=subprocess.STDOUT)
            status = "running"
            while process.poll() is None:
                scope()
                require(time.monotonic() - begin < 600, "historical command timeout")
                require(sum(p.stat().st_size for p in directory.iterdir() if p.is_file()) < 268435456, "validation artifact limit")
                time.sleep(0.5)
            code = process.returncode
            require(job.wait_idle(min(5, max(0, (END - now()).total_seconds()))), "unexpected owned descendant")
            require(code == 0, "historical validation exit code")
            status = "finished"
    except BaseException as exc:
        status, error = "failed", str(exc)
        raise
    finally:
        active = None
        try:
            if job is not None:
                if job.active():
                    job.stop()
                active = job.active()
                job.close()
            if process is not None:
                process.wait(timeout=5)
                code = process.returncode
        finally:
            log = directory / (label + ".log")
            result = {**admission, "status": status, "error": error, "exit_code": code, "finished_at": now().isoformat(), "seconds": time.monotonic() - begin, "owned_active_after_cleanup": active, "log_sha256": digest(log) if log.exists() else None}
            write(directory / (label + "-execution.json"), result)
            print(json.dumps({"label": label, "status": status, "exit_code": code, "seconds": result["seconds"]}), flush=True)
    return result


def main(candidate):
    docs.check(candidate)
    usage = scope()
    require((END - now()).total_seconds() > 3600, "full validation reserve")
    require(shutil.disk_usage(ROOT).free > 1073741824 and frozen.free_memory() > 3221225472, "host capacity reserve")
    prior_inventory = read(ROOT / "docs/v3/construction/cut-source-overnight-20260908/validation-inventory.json")
    rows = [{"commit": PRIOR, "branch": "codex/v3-cut-source-overnight-20260908", "script": "experiments/v3/cut-source-overnight/check.py"}] + prior_inventory["frozen_gates"]
    require(len(rows) == 17 and len(prior_inventory["regression_commands"]) == 25, "full inherited validation inventory")
    roots = frozen_roots(rows)
    run_id = now().strftime("%Y%m%dT%H%M%S%f")
    directory = CACHE / candidate / run_id
    directory.mkdir(parents=True, exist_ok=False)
    receipt = {"candidate": candidate, "run_id": run_id, "started_at": now().isoformat(), "status": "RUNNING", "scope": "documentation slice with unresolved research", "campaign_complete": False, "formal_freeze": False, "new_counterexample_work": False, "usage_at_admission": usage, "commands": []}
    changed = docs.git("diff", "--name-only", PRIOR, candidate).splitlines()
    receipt["candidate_files"] = {p: frozen.sha(frozen.git("show", candidate + ":" + p)) for p in changed}
    receipt["helper_sha256"] = digest(ROOT / "experiments/v3/cut-source-overnight/run_packet.py")
    write(directory / "admission.json", receipt)
    try:
        receipt["historical_closure"] = history()
        for i, (row, root) in enumerate(roots):
            receipt["commands"].append(command([sys.executable, "-X", "utf8", "-B", row["script"], "--working"], root, directory, "frozen-" + str(i)))
            require(git_at(root, "rev-parse", "HEAD") == row["commit"] and not git_at(root, "status", "--porcelain", "--untracked-files=all"), "frozen source changed")
        for i, args in enumerate(prior_inventory["regression_commands"]):
            receipt["commands"].append(command([sys.executable, *args[1:]], ROOT, directory, "regression-" + str(i)))
        docs.check(candidate)
        scope()
        require(history() == receipt["historical_closure"], "historical closure changed")
        require(len(receipt["commands"]) == 42, "all required validations executed")
        receipt["status"] = "DOCUMENTATION_SLICE_FULL_GATE_PASS"
    except BaseException as exc:
        receipt["status"], receipt["error"] = "FAILED_RETAINED", str(exc)
        raise
    finally:
        receipt["finished_at"] = now().isoformat()
        receipt["files"] = {p.name: digest(p) for p in directory.iterdir() if p.is_file()}
        write(directory / "receipt.json", receipt)
        if sum(p.stat().st_size for p in directory.iterdir() if p.is_file()) > 268435456:
            receipt["status"], receipt["error"] = "FAILED_RETAINED", "retained final artifact bound"
            write(directory / "receipt.json", receipt)
            raise ValueError(receipt["error"])
        print(str(directory / "receipt.json"), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    arguments = parser.parse_args()
    acquired = []
    try:
        for name in ("heavy-gate.lock", "model.lock"):
            lock = OLD / name
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            acquired.append(lock)
            with os.fdopen(fd, "w") as handle:
                handle.write(str(os.getpid()))
        main(arguments.candidate)
    finally:
        for lock in reversed(acquired):
            lock.unlink()
