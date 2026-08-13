#!/usr/bin/env python3
"""Portable adversarial tests for the Phase-8 ignored-seed contract."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("seed_contract", SOURCE / "scripts/seed_contract.py")
assert SPEC and SPEC.loader
SEED = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SEED)


def git(repo: Path, *args: str) -> None:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(result.stderr.decode(errors="replace"))


def repository() -> tuple[Path, Path]:
    temp = Path(tempfile.mkdtemp(prefix="seed-contract-"))
    repo = temp / "repo"
    (repo / "data/corpus").mkdir(parents=True)
    (repo / "data/corpus/oracle.bin").write_bytes(b"ignored truth\n")
    (repo / ".gitignore").write_text("/data/corpus/\n", encoding="utf-8")
    (repo / ".seedlist").write_text("# required offline input\ndata/corpus\n", encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "add", ".gitignore", ".seedlist")
    git(repo, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "seed contract")
    return temp, repo


def refused(repo: Path) -> bool:
    try:
        SEED.inspect_repository(repo)
    except SEED.SeedContractError:
        return True
    return False


def main() -> int:
    failures = 0
    observed_timeout: list[object] = []
    original_run = SEED.subprocess.run
    try:
        def capture_timeout(*args, **kwargs):
            observed_timeout.append(kwargs.get("timeout"))
            return subprocess.CompletedProcess(args[0], 0, b"", b"")

        SEED.subprocess.run = capture_timeout
        SEED._git(Path("."), "status")
    finally:
        SEED.subprocess.run = original_run
    bounded_git = observed_timeout == [30]
    print(("ok   " if bounded_git else "FAIL ") + "controller git probes have a bounded timeout")
    failures += int(not bounded_git)
    try:
        SEED.subprocess.run = lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.TimeoutExpired(args[0], kwargs.get("timeout")),
        )
        try:
            SEED._git(Path("."), "status")
        except SEED.SeedContractError:
            timeout_closed = True
        else:
            timeout_closed = False
    finally:
        SEED.subprocess.run = original_run
    print(("ok   " if timeout_closed else "FAIL ") + "timed-out git probes fail closed")
    failures += int(not timeout_closed)

    temp, repo = repository()
    try:
        contract = SEED.inspect_repository(repo)
        target = temp / "target"; target.mkdir()
        copied = SEED.copy_seed_paths(repo, target, contract["paths"], contract["content_sha256"])
        valid = (
            copied["content_sha256"] == contract["content_sha256"]
            and (target / "data/corpus/oracle.bin").read_bytes() == b"ignored truth\n"
        )
        print(("ok   " if valid else "FAIL ") + "tracked manifest binds and copies exact ignored bytes")
        failures += int(not valid)
    finally:
        shutil.rmtree(temp, ignore_errors=True)

    cases = {
        "duplicate paths": "data/corpus\ndata/corpus\n",
        "absolute paths": "/data/corpus\n",
        "parent traversal": "data/../outside\n",
        "backslash ambiguity": "data\\corpus\n",
        "overlapping paths": "data\ndata/corpus\n",
        "secret-shaped paths": ".env\n",
    }
    for label, manifest in cases.items():
        temp, repo = repository()
        try:
            (repo / ".seedlist").write_text(manifest, encoding="utf-8")
            git(repo, "add", ".seedlist")
            git(repo, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                "commit", "-qm", label)
            valid = refused(repo)
            print(("ok   " if valid else "FAIL ") + f"refuses {label}")
            failures += int(not valid)
        finally:
            shutil.rmtree(temp, ignore_errors=True)

    temp, repo = repository()
    try:
        (repo / "data/corpus/oracle.bin").write_bytes(b"tracked\n")
        git(repo, "add", "-f", "data/corpus/oracle.bin")
        git(repo, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "tracked seed")
        valid = refused(repo)
        print(("ok   " if valid else "FAIL ") + "refuses tracked seed content")
        failures += int(not valid)
    finally:
        shutil.rmtree(temp, ignore_errors=True)

    temp, repo = repository()
    try:
        (repo / ".gitignore").write_text("", encoding="utf-8")
        git(repo, "add", ".gitignore")
        git(repo, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-qm", "unignored seed")
        valid = refused(repo)
        print(("ok   " if valid else "FAIL ") + "refuses unignored seed content")
        failures += int(not valid)
    finally:
        shutil.rmtree(temp, ignore_errors=True)

    temp, repo = repository()
    try:
        (repo / ".seedlist").write_text("data/corpus\n# dirty\n", encoding="utf-8")
        valid = refused(repo)
        print(("ok   " if valid else "FAIL ") + "refuses an uncommitted manifest")
        failures += int(not valid)
    finally:
        shutil.rmtree(temp, ignore_errors=True)

    if os.name != "nt":
        temp, repo = repository()
        try:
            shutil.rmtree(repo / "data/corpus")
            os.symlink(temp / "outside", repo / "data/corpus", target_is_directory=True)
            (temp / "outside").mkdir(); (temp / "outside/oracle.bin").write_bytes(b"outside\n")
            valid = refused(repo)
            print(("ok   " if valid else "FAIL ") + "refuses a symlinked seed")
            failures += int(not valid)
        finally:
            shutil.rmtree(temp, ignore_errors=True)

    print(f"seed-contract: {failures} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
