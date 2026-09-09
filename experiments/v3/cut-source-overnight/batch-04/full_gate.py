"""Fresh enclosing final gate; preserves all historical sources and expired clocks."""
import importlib.util
import json
import gzip
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import run as admission
ROOT, COMMON, OLD, CACHE = admission.ROOT, admission.COMMON, admission.OLD, admission.CACHE
require, read, write, git, now = admission.require, admission.read, admission.write, admission.git, admission.now
sys.path.insert(0, str(ROOT / "experiments/v3/cut-source-overnight/reopen-01"))
spec = importlib.util.spec_from_file_location("historical_document_verification", ROOT / "experiments/v3/cut-source-overnight/reopen-01/check_final.py")
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)


def file_hash(path):
    return admission.digest(path.read_bytes())


def history():
    counts = legacy.history(enforce_live_clock=False)
    for row in read(ROOT / admission.DOC / "historical-closure.json"):
        path = (COMMON / row["path"]).resolve()
        base = (COMMON / row["base"]).resolve()
        require(path.is_relative_to(COMMON) and base.is_relative_to(COMMON), "historical root containment")
        require(file_hash(path) == row["sha256"], "immutable predecessor closing receipt")
        entries = read(path)[row["key"]]
        require(len(entries) == row["count"], "historical closure cardinality")
        for name, expected in entries.items():
            target = (base / name).resolve()
            require(target.is_relative_to(base) and file_hash(target) == expected, "preserved historical evidence: " + name)
        counts[row["path"]] = len(entries)
    return counts


def snapshot(candidate, directory):
    manifest = read(ROOT / admission.DOC / "manifest.json")
    inputs = {r["path"]: r["git_blob_sha256"] for r in manifest["inputs"]}
    sources = manifest["sources"]
    require(len(inputs) == len(manifest["inputs"]) and len(sources) == len(set(sources)), "unique manifest")
    prior = read(ROOT / "docs/v3/construction/cut-source-overnight-20260908/batch-03/manifest.json")
    inherited = {r["path"] for r in prior["inputs"]} | set(prior["sources"])
    additional = set(manifest["additional_inputs"])
    require(len(additional) == len(manifest["additional_inputs"]) and not additional & inherited and set(inputs) == inherited | additional, "exact inherited plus declared static-audit input closure")
    changed = set(git("diff", "--name-only", admission.BASE, candidate).decode().splitlines())
    require(set(sources) == changed and not set(inputs) & set(sources), "every changed source bound exactly once")
    result = {}
    for i, name in enumerate(sorted(set(inputs) | set(sources))):
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), "candidate input containment")
        raw = path.read_bytes(); blob = git("show", candidate + ":" + name)
        require(raw.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), "exact working/committed source")
        if name in inputs:
            require(admission.digest(blob) == inputs[name] == admission.digest(git("show", admission.BASE + ":" + name)), "immutable predecessor source")
        target = directory / "source" / (str(i).zfill(4) + ".bin.gz")
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(gzip.compress(raw, compresslevel=6, mtime=0))
        result[name] = {"git_blob_sha256": admission.digest(blob), "working_sha256": admission.digest(raw), "snapshot_file": target.relative_to(directory).as_posix(), "snapshot_codec": "gzip"}
    return result


def command(candidate, args, root, directory, label):
    end, usage = admission.scope(candidate, final=True)
    if label == "frozen-1": admission.reserve(directory, label, 17968)
    elif label in ("batch03-packet", "batch-packet"): admission.reserve(directory, label, 17966)
    require((end - now()).total_seconds() > 605, "command and cleanup reserve")
    require(admission.helper.free_memory() > 3221225472, "host memory reserve")
    receipt = {"candidate": candidate, "command": args, "root": str(root), "source_commit": legacy.git_at(root, "rev-parse", "HEAD"),
               "started_at": now().isoformat(), "maximum_seconds": 600, "maximum_memory_bytes": 2147483648, "usage": usage, "status": "ADMITTED_BEFORE_EXECUTION"}
    write(directory / (label + "-admission.json"), receipt)
    job, child, errors = None, None, []
    begin = time.monotonic()
    try:
        job = admission.helper.OwnedJob(2147483648)
        with (directory / (label + ".log")).open("wb") as log:
            child = job.launch(args, cwd=root, stdout=log, stderr=subprocess.STDOUT)
            while child.poll() is None:
                admission.scope(candidate, final=True)
                require(time.monotonic() - begin < 600 and admission.size(directory) < 268435456, "owned time/artifact bound")
                time.sleep(0.5)
        require(child.returncode == 0 and job.wait_idle(5), "successful command and owned cleanup")
        require(time.monotonic() - begin < 600 and job.peak() <= 2147483648, "terminal resource bounds")
        admission.scope(candidate, final=True)
        receipt["status"] = "PASS"
    except BaseException as exc:
        receipt.update(status="FAILED_RETAINED", error=repr(exc))
        raise
    finally:
        if job is not None:
            try:
                if job.active(): job.stop()
                receipt.update(peak_memory_bytes=job.peak(), owned_active_after_cleanup=job.active())
            except BaseException as exc: errors.append(repr(exc))
            finally:
                try: job.close()
                except BaseException as exc: errors.append(repr(exc))
        if child is not None:
            try:
                child.wait(timeout=5); receipt["exit_code"] = child.returncode
            except BaseException as exc: errors.append(repr(exc))
        receipt.update(finished_at=now().isoformat(), seconds=time.monotonic()-begin, cleanup_errors=errors)
        if errors: receipt["status"] = "FAILED_RETAINED"
        log = directory / (label + ".log")
        receipt["log_sha256"] = file_hash(log) if log.exists() else None
        write(directory / (label + "-execution.json"), receipt)
        print(json.dumps({"label": label, "status": receipt["status"], "seconds": receipt["seconds"]}), flush=True)
        if errors: raise RuntimeError("owned cleanup failed")
    return receipt


def main(candidate):
    end, usage = admission.scope(candidate, final=True)
    require((end - now()).total_seconds() > 3600, "full validation reserve")
    require(shutil.disk_usage(ROOT).free > 1073741824, "host disk reserve")
    require((ROOT / admission.DOC / "results.json").is_file(), "accepted packet results required")
    inventory = read(ROOT / "docs/v3/construction/cut-source-overnight-20260908/validation-inventory.json")
    rows = [{"commit": "8f457c546e4d85fada73913efb900f921eaf6b1a", "branch": "codex/v3-cut-source-continued-20260909", "script": "experiments/v3/cut-source-overnight/reopen-01/check_final.py"},
            {"commit": "89ea6390774c4ef9b5c3727ad2715c57f12af90a", "branch": "codex/v3-cut-source-overnight-20260908", "script": "experiments/v3/cut-source-overnight/check.py"}] + inventory["frozen_gates"]
    require(len(rows) == 18 and len(inventory["regression_commands"]) == 25, "all historical gates retained")
    roots = legacy.frozen_roots(rows)
    directory = CACHE / candidate / (now().strftime("%Y%m%dT%H%M%S%f") + "-full")
    directory.mkdir(parents=True, exist_ok=False)
    receipt = {"candidate": candidate, "status": "PREPARING", "started_at": now().isoformat(), "usage": usage, "commands": [],
               "scope": "Batch04 A-C plus all preserved predecessor research", "extends_prior_envelope": False,
               "publication_ready": False, "broader_campaign_complete": False, "deferred_questions_resolved": []}
    locks = []
    try:
        for name in ("heavy-gate.lock", "model.lock"):
            lock = OLD / name
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            locks.append(lock)
            with os.fdopen(fd, "w") as f: f.write(str(os.getpid()))
        receipt["sources"] = snapshot(candidate, directory)
        receipt["history"] = history()
        admission.scope(candidate, final=True)
        receipt["status"] = "ADMITTED_BEFORE_EXECUTION"
        write(directory / "admission.json", receipt)
        for i, (row, root) in enumerate(roots):
            receipt["commands"].append(command(candidate, [sys.executable, "-X", "utf8", "-B", row["script"], "--working"], root, directory, "frozen-" + str(i)))
            require(legacy.git_at(root, "rev-parse", "HEAD") == row["commit"] and not legacy.git_at(root, "status", "--porcelain", "--untracked-files=all"), "frozen source unchanged")
        for i, args in enumerate(inventory["regression_commands"]):
            receipt["commands"].append(command(candidate, [sys.executable, *args[1:]], ROOT, directory, "regression-" + str(i)))
        receipt["commands"].append(command(candidate, [sys.executable, "-X", "utf8", "-B", "experiments/v3/cut-source-overnight/append-handoff-01/check.py", str(directory / "predecessor-output")], ROOT, directory, "predecessor-packet"))
        receipt["commands"].append(command(candidate, [sys.executable, "-X", "utf8", "-B", "experiments/v3/cut-source-overnight/batch-02/check.py", str(directory / "batch02-output"), "--packet", "C"], ROOT, directory, "batch02-packet"))
        receipt["commands"].append(command(candidate, [sys.executable, "-X", "utf8", "-B", "experiments/v3/cut-source-overnight/batch-03/check.py", str(directory / "batch03-output"), "--packet", "C"], ROOT, directory, "batch03-packet"))
        receipt["commands"].append(command(candidate, [sys.executable, "-X", "utf8", "-B", admission.CODE + "check.py", str(directory / "output"), "--packet", "C"], ROOT, directory, "batch-packet"))
        admission.scope(candidate, final=True)
        require(history() == receipt["history"], "historical closure unchanged")
        require(len(receipt["commands"]) == 47, "complete 47-item final gate")
        receipt["status"] = "BATCH04_FULL_GATE_PASS"
    except BaseException as exc:
        receipt.update(status="FAILED_RETAINED", error=repr(exc))
        raise
    finally:
        errors = []
        for lock in reversed(locks):
            try: lock.unlink()
            except BaseException as exc: errors.append(repr(exc))
        receipt.update(finished_at=now().isoformat(), lock_cleanup_errors=errors)
        if errors: receipt.update(status="FAILED_RETAINED", error="lock cleanup failed")
        receipt["files"] = {p.relative_to(directory).as_posix(): file_hash(p) for p in directory.rglob("*") if p.is_file()}
        write(directory / "receipt.json", receipt)
        if errors or admission.size(directory) > 268435456:
            receipt.update(status="FAILED_RETAINED", error="cleanup or retained artifact bound")
            write(directory / "receipt.json", receipt)
            raise RuntimeError(receipt["error"])
        print(str(directory / "receipt.json"), flush=True)
