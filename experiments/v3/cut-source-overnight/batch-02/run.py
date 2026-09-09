"""Admission for a fresh interactive packet; never invokes an expired campaign wrapper."""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import gzip
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
DOC = "docs/v3/construction/cut-source-overnight-20260908/batch-02/"
CODE = "experiments/v3/cut-source-overnight/batch-02/"
BASE = "0aa6e8e2757eed89673c52ce3fc011f48cc0618b"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=30)


def now():
    return dt.datetime.now(dt.timezone.utc)


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


COMMON = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip())
OLD = COMMON / "research-attestations/cut-source-overnight"
CACHE = COMMON / "research-attestations/batch-02-20260909"
spec = importlib.util.spec_from_file_location("ca_owned_job", ROOT / "experiments/v3/cut-source-overnight/run_packet.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def scope(candidate, final=False):
    require(git("rev-parse", "HEAD").decode().strip() == candidate, "exact candidate")
    require(not git("status", "--porcelain", "--untracked-files=all").strip(), "clean source")
    require(git("branch", "--show-current").decode().strip() == "codex/v3-batch-02-20260909", "scope branch")
    git("merge-base", "--is-ancestor", BASE, candidate)
    changed = git("diff", "--name-only", BASE, candidate).decode().splitlines()
    require(changed and all(p.startswith((DOC, CODE)) for p in changed), "explicit additive allowlist")
    require(not git("diff", "--name-only", "--diff-filter=DMRT", BASE, candidate).strip(), "immutable predecessor tree")
    require(not (ROOT / "state/PAUSE").exists() and not (COMMON.parent / "state/PAUSE").exists(), "PAUSE")
    require("status: active" in (ROOT / "state/goals/goal-recursion-v2-execution-fabric.md").read_text(), "active parent")
    goal = read(ROOT / DOC / "goal.json")
    authority = read(CACHE / "activation.json")
    require(goal == authority["goal"], "unchanged new interactive authority")
    require(goal["parent_goal"] == "goal-recursion-v2-execution-fabric" and goal["base_commit"] == BASE, "scope parent/base")
    require((goal["model"], goal["reasoning"], goal["speed"]) == ("gpt-6-astra", "high", "standard"), "unchanged selected settings")
    require(goal["prior_deadline_utc"] == "2026-09-09T15:30:00Z" and not goal["extends_prior_envelope"], "preserved expired envelope")
    started = dt.datetime.fromisoformat(authority["packet_started_at"])
    end = dt.datetime.fromisoformat(authority["packet_deadline_utc"])
    require((end - started).total_seconds() == 21600 and started <= now() < end, "fixed local packet ceiling")
    require(end.isoformat() == goal["deadline_utc"] and started.isoformat() == goal["started_at"], "fixed authority timestamps")
    require(final or now() < dt.datetime.fromisoformat(goal["discovery_cutoff_utc"]), "discovery cutoff")
    usage = read(CACHE / "usage.json")
    require(0 <= (now() - dt.datetime.fromisoformat(usage["checked_at"])).total_seconds() < 900, "fresh capacity")
    require(usage["remaining_percent"] == min(w["remaining_percent"] for w in usage["binding_windows"]), "binding capacity minimum")
    require(all(w["remaining_percent"] == 100 - w["used_percent"] for w in usage["binding_windows"]), "capacity window consistency")
    require(usage["remaining_percent"] > (3 if final else 10) and usage["new_metered_spend"] == 0 and usage["reset_credits_used"] == 0, "included capacity and finalization reserve")
    ledger = read(OLD / "reopen-01/reset-ledger.json")
    require(ledger["status"] == "authorized-unused" and ledger["applied_count"] == 0 and ledger["attempts"] == [], "actual unused reset ledger")
    return end, usage


def size(directory):
    return sum(p.stat().st_size for p in directory.rglob("*") if p.is_file())


def main(candidate, packet):
    end, usage = scope(candidate)
    require((end - now()).total_seconds() > 605, "execution and cleanup reserve")
    require(helper.free_memory() > 3221225472 and shutil.disk_usage(ROOT).free > 1073741824, "host reserve")
    directory = CACHE / candidate / now().strftime("%Y%m%dT%H%M%S%f")
    directory.mkdir(parents=True)
    receipt = {"candidate": candidate, "status": "PREPARING", "started_at": now().isoformat(),
               "usage": usage, "limits": {"seconds": 600, "memory_bytes": 2147483648, "artifact_bytes": 268435456},
               "publication_ready": False, "full_historical_gate": False, "extends_prior_envelope": False}
    locks, job, child = [], None, None
    started = time.monotonic()
    try:
        for name in ("heavy-gate.lock", "model.lock"):
            path = OLD / name
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            locks.append(path)
            with os.fdopen(fd, "w") as handle:
                handle.write(str(os.getpid()))
        manifest = read(ROOT / DOC / "manifest.json")
        inputs = {row["path"]: row["git_blob_sha256"] for row in manifest["inputs"]}
        require(len(inputs) == len(manifest["inputs"]), "unique input paths")
        paths = sorted(set(inputs) | set(manifest["sources"]))
        require(len(paths) == len(inputs) + len(manifest["sources"]), "disjoint explicit sources")
        prior_manifest = read(ROOT / "docs/v3/construction/cut-source-overnight-20260908/append-handoff-01/manifest.json")
        prior_paths = {r["path"] for r in prior_manifest["inputs"]} | set(prior_manifest["sources"])
        require(prior_paths <= set(inputs), "complete inherited source/input closure")
        actual = {p.relative_to(ROOT).as_posix() for p in (ROOT / CODE).glob("*.py")}
        require(actual <= set(paths) and {DOC + n for n in ("goal.json", "manifest.json", "specification.md")} <= set(paths), "execution defining sources present")
        receipt["sources"] = {}
        for index, name in enumerate(paths):
            require(now() < end, "snapshot deadline")
            path = (ROOT / name).resolve()
            require(path.is_relative_to(ROOT), "source path containment")
            blob, raw = git("show", candidate + ":" + name), path.read_bytes()
            require(raw.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"), "working/committed bytes")
            if name in inputs:
                require(digest(blob) == inputs[name] == digest(git("show", BASE + ":" + name)), "immutable input")
            snapshot_name = "source/" + str(index).zfill(4) + ".bin.gz"
            target = directory / snapshot_name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(gzip.compress(raw, compresslevel=6, mtime=0))
            receipt["sources"][name] = {"git_blob_sha256": digest(blob), "working_sha256": digest(raw), "snapshot_file": snapshot_name, "snapshot_codec": "gzip"}
        end, usage = scope(candidate)
        require((end - now()).total_seconds() > 605 and size(directory) < 268435456, "post-snapshot reserve")
        command = [sys.executable, "-X", "utf8", "-B", CODE + "check.py", str(directory / "output"), "--packet", packet]
        receipt.update(status="ADMITTED_BEFORE_EXECUTION", command=command, usage=usage)
        write(directory / "admission.json", receipt)
        job = helper.OwnedJob(2147483648)
        started = time.monotonic()
        with (directory / "stdout.log").open("wb") as out, (directory / "stderr.log").open("wb") as err:
            child = job.launch(command, cwd=ROOT, stdout=out, stderr=err)
            while child.poll() is None:
                scope(candidate)
                require(time.monotonic() - started < 600 and size(directory) < 268435456, "owned time/artifact bound")
                time.sleep(0.2)
        require(child.returncode == 0 and job.wait_idle(5), "successful owned execution")
        require(time.monotonic() - started < 600 and job.peak() <= 2147483648, "terminal resource bounds")
        scope(candidate)
        receipt["status"] = "BATCH02_PACKET_EXECUTION_PASS"
    except BaseException as error:
        receipt.update(status="FAILED_RETAINED", error=type(error).__name__ + ": " + str(error))
        raise
    finally:
        errors = []
        if job is not None:
            try:
                if job.active():
                    job.stop()
                receipt["peak_memory_bytes"] = job.peak()
                receipt["owned_active_after_cleanup"] = job.active()
            except BaseException as error:
                errors.append("stop/inspect: " + repr(error))
            finally:
                try:
                    job.close()
                except BaseException as error:
                    errors.append("close: " + repr(error))
        if child is not None:
            try:
                child.wait(timeout=5)
                receipt["exit_code"] = child.returncode
            except BaseException as error:
                errors.append("wait: " + repr(error))
        for path in reversed(locks):
            try:
                path.unlink()
            except BaseException as error:
                errors.append("lock cleanup: " + repr(error))
        receipt.update(finished_at=now().isoformat(), seconds=time.monotonic() - started, cleanup_errors=errors)
        if errors:
            receipt.update(status="FAILED_RETAINED", error="owned cleanup failed")
        receipt["files"] = {p.relative_to(directory).as_posix(): digest(p.read_bytes()) for p in directory.rglob("*") if p.is_file()}
        write(directory / "execution.json", receipt)
        if size(directory) > 268435456:
            receipt.update(status="FAILED_RETAINED", error="terminal retained artifact bound")
            write(directory / "execution.json", receipt)
        print(str(directory / "execution.json"), flush=True)
        if errors or size(directory) > 268435456:
            raise RuntimeError(receipt["error"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--mode", choices=("local", "full"), default="local")
    parser.add_argument("--packet", choices=("B", "C"), default="B")
    args = parser.parse_args()
    if args.mode == "full":
        from full_gate import main as full_main
        full_main(args.candidate)
    else:
        main(args.candidate, args.packet)
