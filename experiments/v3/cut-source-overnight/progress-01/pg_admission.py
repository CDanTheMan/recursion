"""Commit-bound resource admission for this conditional progress study only."""
import argparse
import datetime as dt
import hashlib
import importlib.util
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
CODE = "experiments/v3/cut-source-overnight/progress-01/"
DOC = "docs/v3/construction/cut-source-overnight-20260908/progress-01/"
BASE = "8f457c546e4d85fada73913efb900f921eaf6b1a"
END = dt.datetime.fromisoformat("2026-09-09T15:30:00Z")
CUTOFF = dt.datetime.fromisoformat("2026-09-09T12:30:00Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def now():
    return dt.datetime.now(dt.timezone.utc)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=30)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


COMMON = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip())
OLD = COMMON / "research-attestations/cut-source-overnight"
CACHE = OLD / "progress-01"
REOPEN = OLD / "reopen-01"
helper_spec = importlib.util.spec_from_file_location("pg_frozen_owned_job", ROOT / "experiments/v3/cut-source-overnight/run_packet.py")
helper = importlib.util.module_from_spec(helper_spec)
helper_spec.loader.exec_module(helper)


def scope(final=False):
    limit = END if final else CUTOFF
    require(now() < limit, "fixed scope deadline")
    require(not (ROOT / "state/PAUSE").exists() and not (COMMON.parent / "state/PAUSE").exists(), "operational PAUSE")
    require("status: active" in (ROOT / "state/goals/goal-recursion-v2-execution-fabric.md").read_text(), "active parent")
    authority = read(REOPEN / "amendment-receipt.json")
    require(digest((REOPEN / "amendment-receipt.json").read_bytes()) == "64113d7f98be7688d9e8acc149fb3679c93c3b15191d76dd333bedf4240a2afa", "immutable amended authority")
    require(authority["original_started_at"] == "2026-09-09T03:40:33Z" and authority["deadline_utc"] == END.isoformat().replace("+00:00", "Z"), "original clock and fixed deadline")
    usage = read(REOPEN / "usage.json")
    require(0 <= (now() - dt.datetime.fromisoformat(usage["checked_at"])).total_seconds() < 900, "fresh usage telemetry")
    windows = usage["binding_windows"]
    require(windows and all(0 <= w["used_percent"] <= 100 and w["remaining_percent"] == 100 - w["used_percent"] for w in windows), "binding capacity windows")
    require(usage["remaining_percent"] == min(w["remaining_percent"] for w in windows), "binding minimum")
    require(usage["remaining_percent"] > (3 if final else 10), "included capacity reserve")
    require(usage["new_metered_spend"] == 0, "zero new metered spend")
    ledger = read(REOPEN / "reset-ledger.json")
    require(ledger["idempotency_key"] == authority["reset_idempotency_key"] and ledger["maximum_applied"] == 1, "preserved single reset identity")
    require(ledger["status"] == "authorized-unused" and ledger["applied_count"] == 0 and ledger["attempts"] == [] and usage["reset_credits_used"] == 0, "actual unused reset; redemption requires its real receipt and revalidation")
    return limit, usage


def candidate_check(candidate=None):
    head = git("rev-parse", "HEAD").decode().strip()
    require(candidate is None or candidate == head, "exact candidate")
    require(not git("status", "--porcelain", "--untracked-files=all").strip(), "clean committed source")
    require(git("branch", "--show-current").decode().strip() == "codex/v3-cut-source-progress-20260909", "bounded progress branch")
    git("merge-base", "--is-ancestor", BASE, head)
    changes = git("diff", "--name-only", BASE, head).decode().splitlines()
    require(all(p.startswith(DOC) or p.startswith(CODE) for p in changes), "progress-only additive allowlist")
    require(not git("diff", "--name-only", "--diff-filter=DMRT", BASE, head).strip(), "immutable prior tree")
    activation = read(ROOT / DOC / "activation.json")
    receipt = CACHE / "activation-receipt.json"
    require(activation["receipt_sha256"] == digest(receipt.read_bytes()), "immutable progress scope receipt")
    goal = read(ROOT / DOC / "goal.json")
    require(read(receipt)["goal"] == goal, "prospective scope unchanged")
    require(goal["base_commit"] == BASE and goal["parent_goal"] == "goal-recursion-v2-execution-fabric", "bounded parent and base")
    require((goal["model"], goal["reasoning"], goal["speed"], goal["settings_changes"]) == ("gpt-6-astra", "high", "standard", False), "unchanged selected settings")
    require(goal["original_started_at"] == "2026-09-09T03:40:33Z" and dt.datetime.fromisoformat(goal["deadline_utc"]) == END and dt.datetime.fromisoformat(goal["discovery_cutoff_utc"]) == CUTOFF and goal["clock_restart"] is False, "same absolute envelope")
    return head


def snapshot(directory, head, limit):
    manifest = read(ROOT / DOC / "manifest.json")
    inputs = {r["path"]: r["git_blob_sha256"] for r in manifest["inputs"]}
    require(len(inputs) == len(manifest["inputs"]), "unique explicit immutable inputs")
    paths = sorted(set(inputs) | set(manifest["sources"]))
    require(len(paths) == len(inputs) + len(manifest["sources"]), "explicit unique input/source closure")
    actual_code = {p.relative_to(ROOT).as_posix() for p in (ROOT / CODE).rglob("*.py")}
    require(actual_code <= set(paths), "all nested model and runner sources included")
    historical_manifest = read(ROOT / "docs/v3/construction/cut-source-overnight-20260908/manifest.json")
    required_inputs = {r["path"] for r in historical_manifest["inputs"] if not r["path"].startswith("docs/v3/construction/")}
    require(required_inputs <= set(inputs) and manifest["input_reference_commit"] == BASE, "complete nonconstruction path closure at frozen continuation base")
    require({DOC + name for name in ("goal.json", "specification.md", "manifest.json", "activation.json")} <= set(paths), "all execution-defining documents included")
    if (ROOT / DOC / "inputs.json").exists():
        require(DOC + "inputs.json" in paths, "prepared original input bytes included")
    files = {}
    for name in paths:
        require(now() < limit, "fixed deadline during source snapshot")
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT.resolve()), "input containment")
        blob, raw = git("show", head + ":" + name), path.read_bytes()
        require(raw.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), "working source equals commit: " + name)
        require(name not in inputs or digest(blob) == inputs[name], "frozen input identity: " + name)
        if name in inputs:
            require(digest(git("show", BASE + ":" + name)) == inputs[name], "input identity at immutable continuation base: " + name)
        copy = directory / "source" / name
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(raw)
        files[name] = {"git_blob_sha256": digest(blob), "working_sha256": digest(raw)}
    return files


def artifact_size(directory):
    return sum(p.stat().st_size for p in directory.rglob("*") if p.is_file())


def execute(mode, final=False):
    limit, usage = scope(final)
    head = candidate_check()
    require((limit - now()).total_seconds() > 605, "command and cleanup reserve")
    require(helper.free_memory() > 3221225472 and shutil.disk_usage(ROOT).free > 1073741824, "host reserve")
    require(mode in ("prepare", "explore"), "declared bounded activity")
    if mode == "explore":
        require((ROOT / DOC / "inputs.json").is_file(), "committed original inputs before exploration")
    directory = CACHE / head / now().strftime("%Y%m%dT%H%M%S%f")
    directory.mkdir(parents=True, exist_ok=False)
    job, process = None, None
    started, observed = time.monotonic(), 0
    receipt = {"source_commit": head, "mode": mode, "started_at": now().isoformat(), "status": "ADMISSION_PENDING",
               "limits": {"seconds": 600, "memory_bytes": 2147483648, "artifact_bytes": 268435456, "states_per_representation": 500000},
               "usage": usage, "new_metered_spend": 0, "model_network": False, "deferred_research_executed": False}
    try:
        receipt["sources"] = snapshot(directory, head, limit)
        receipt["host"] = {"python": sys.version, "executable": sys.executable,
                           "jsonschema": importlib.metadata.version("jsonschema")}
        limit, refreshed_usage = scope(final)
        require((limit - now()).total_seconds() > 605, "post-snapshot command and cleanup reserve")
        require(artifact_size(directory) < 268435456, "source snapshot artifact bound")
        command = [sys.executable, "-X", "utf8", "-B", CODE + "pg_experiment.py", mode, "--output", str(directory)]
        receipt.update(status="ADMITTED_BEFORE_EXECUTION", command=command, usage=refreshed_usage)
        write(directory / "admission.json", receipt)
        started = time.monotonic()
        job = helper.OwnedJob(2147483648)
        with (directory / "stdout.log").open("wb") as out, (directory / "stderr.log").open("wb") as err:
            process = job.launch(command, cwd=ROOT, stdout=out, stderr=err)
            while process.poll() is None:
                scope(final)
                observed = max(observed, helper.peak(process))
                require(time.monotonic() - started < 600, "owned execution timeout")
                require(observed <= 2147483648, "sampled process memory bound")
                require(artifact_size(directory) < 268435456, "retained artifact bound")
                time.sleep(0.2)
        require(job.wait_idle(min(5, max(0, (limit - now()).total_seconds()))), "unexpected owned descendant")
        require(process.returncode == 0, "bounded child exit code")
        require(time.monotonic() - started < 600 and job.peak() <= 2147483648, "terminal resource bounds")
        candidate_check(head)
        scope(final)
        receipt["status"] = "FINISHED"
    except BaseException as error:
        receipt.update(status="FAILED_RETAINED", error=type(error).__name__ + ": " + str(error))
        raise
    finally:
        cleanup_errors = []
        if job is not None:
            try:
                if job.active():
                    job.stop()
                receipt["owned_job_peak_bytes"] = job.peak()
                receipt["owned_active_after_cleanup"] = job.active()
            except BaseException as error:
                cleanup_errors.append("inspect/stop: " + repr(error))
            finally:
                try:
                    job.close()
                except BaseException as error:
                    cleanup_errors.append("close: " + repr(error))
        if process is not None:
            try:
                process.wait(timeout=5)
                receipt["exit_code"] = process.returncode
            except BaseException as error:
                cleanup_errors.append("wait: " + repr(error))
        receipt["cleanup_errors"] = cleanup_errors
        if cleanup_errors:
            receipt.update(status="FAILED_RETAINED", error="owned cleanup failed; inspect retained cleanup_errors")
        receipt.update(finished_at=now().isoformat(), seconds=time.monotonic() - started, sampled_peak_bytes=observed)
        receipt["files"] = {p.relative_to(directory).as_posix(): digest(p.read_bytes()) for p in directory.rglob("*") if p.is_file()}
        write(directory / "execution.json", receipt)
        if artifact_size(directory) > 268435456:
            receipt.update(status="FAILED_RETAINED", error="terminal retained artifact bound")
            write(directory / "execution.json", receipt)
            raise ValueError(receipt["error"])
        print(str(directory / "execution.json"), flush=True)
        if cleanup_errors:
            raise RuntimeError(receipt["error"])
    return directory


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "explore"))
    args = parser.parse_args()
    locks = []
    try:
        for name in ("heavy-gate.lock", "model.lock"):
            path = OLD / name
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            locks.append(path)
            with os.fdopen(fd, "w") as handle:
                handle.write(str(os.getpid()))
        execute(args.mode)
    finally:
        for path in reversed(locks):
            path.unlink()
