#!/usr/bin/env python3
"""Adversarial, stub-driven tests for the forced-on GSC shade-tops gate."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


SOURCE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SOURCE / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "gsc_shade_tops_gate", SOURCE / "scripts/gsc-shade-tops-gate.py",
)
assert SPEC and SPEC.loader
GATE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GATE
SPEC.loader.exec_module(GATE)

from seed_contract import inspect_repository  # noqa: E402


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def materialize_metric(expected: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    per_slot = copy.deepcopy(expected["per_slot"])
    delta = sum(per_slot.values())
    native = expected["native"]
    ours = native + delta
    return {
        "schema": "native-diff-metric/v1",
        "world": expected["world"],
        "truth": expected["truth"],
        "jumble": True,
        "overrides": ["shadeTops"],
        "buildDefaultsHash": profile["native_diff"]["build_defaults_sha256"],
        "perSlot": per_slot,
        "sumAbs": sum(abs(value) for value in per_slot.values()),
        "uncovered": expected["uncovered"],
        "ours": ours,
        "native": native,
        "delta": delta,
        "ratio": ours / native,
        "vecDigest": GATE.metric_digest(per_slot),
    }


def refresh_metric(metric: dict[str, Any]) -> None:
    metric["sumAbs"] = sum(abs(value) for value in metric["perSlot"].values())
    metric["delta"] = sum(metric["perSlot"].values())
    metric["ours"] = metric["native"] + metric["delta"]
    metric["ratio"] = metric["ours"] / metric["native"]
    metric["vecDigest"] = GATE.metric_digest(metric["perSlot"])


class StubRunner:
    def __init__(
        self,
        metrics: dict[str, dict[str, Any]],
        mutate: Callable[[str, dict[str, Any]], str] | None = None,
        conformance_rc: int = 0,
    ):
        self.metrics = metrics
        self.mutate = mutate
        self.conformance_rc = conformance_rc
        self.commands: list[list[str]] = []

    def __call__(
        self, command: list[str], cwd: Path, timeout: int, env: dict[str, str] | None,
    ) -> GATE.CommandResult:
        self.commands.append(command)
        if command[0] == "bash":
            return GATE.CommandResult(self.conformance_rc, "conformance stub\n", "")
        world = next(arg.split("=", 1)[1] for arg in command if arg.startswith("--world="))
        metric = copy.deepcopy(self.metrics[world])
        if self.mutate:
            output = self.mutate(world, metric)
        else:
            output = json.dumps(metric, separators=(",", ":"))
        return GATE.CommandResult(0, "native-diff prelude\n" + output + "\n", "")


def fixture() -> tuple[Path, Path, Path, dict[str, Any], dict[str, dict[str, Any]]]:
    temp = Path(tempfile.mkdtemp(prefix="gsc-shade-gate-"))
    repo = temp / "product"
    models = repo / "user-client/render/data/models"
    tools = repo / "user-client/render/tools"
    models.mkdir(parents=True)
    tools.mkdir(parents=True)
    (models / "offline.bin").write_bytes(b"offline fixture bytes\n")
    (tools / "native-diff.cjs").write_text("// reviewed measurement stub\n", encoding="utf-8")
    (repo / ".gitignore").write_text("/user-client/render/data/models/\n", encoding="utf-8")
    (repo / ".seedlist").write_text("user-client/render/data/models\n", encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "add", ".gitignore", ".seedlist", "user-client/render/tools/native-diff.cjs")
    git(repo, "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-qm", "reviewed base")

    profile = json.loads((SOURCE / "scripts/gates/gsc-shade-tops-v1.json").read_text())
    # The production profile pins the reviewed committed gate bytes. The hermetic fixture may
    # be authored from a CRLF checkout, so bind its exact local executable without weakening the
    # production profile or runtime verification.
    profile["controller_gate"]["sha256"] = file_hash(SOURCE / "scripts/gsc-shade-tops-gate.py")
    profile["base_commit"] = git(repo, "rev-parse", "HEAD")
    profile["seed_contract"] = inspect_repository(repo)
    profile["native_diff"]["sha256"] = file_hash(tools / "native-diff.cjs")
    baseline = temp / "baseline-pass.txt"
    baseline.write_text("reviewed conformance title\n", encoding="utf-8")
    profile["conformance"]["baseline_path"] = str(baseline)
    profile["conformance"]["baseline_sha256"] = file_hash(baseline)
    profile_path = temp / "profile.json"
    profile_path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    metrics = {item["world"]: materialize_metric(item, profile) for item in profile["worlds"]}
    return temp, repo, profile_path, profile, metrics


def verdict(
    repo: Path, profile_path: Path, runner: StubRunner,
) -> tuple[int, dict[str, Any] | None]:
    try:
        code, evidence, _ = GATE.run_gate(
            repo, profile_path, SOURCE, SOURCE / "scripts/gsc-shade-tops-gate.py", runner,
        )
        return code, evidence
    except GATE.GateError as exc:
        return exc.returncode, None


def main() -> int:
    failures = 0
    temp, repo, profile_path, profile, metrics = fixture()
    try:
        def check(label: str, actual: int, expected: int) -> None:
            nonlocal failures
            good = actual == expected
            print(("ok   " if good else "FAIL ") + f"{label} (rc={actual}, expected={expected})")
            failures += int(not good)

        unchanged = StubRunner(metrics)
        code, evidence = verdict(repo, profile_path, unchanged)
        check("unchanged reviewed base is no-progress", code, 2)
        expected_native = [
            "node", "user-client/render/tools/native-diff.cjs", "--world=furys_storage",
            "--shade-tops", "--metric",
        ]
        shape_ok = len(unchanged.commands) > 1 and unchanged.commands[1] == expected_native and evidence is not None \
            and evidence["query"]["overrides"] == ["shadeTops"]
        check("invocation forces exactly --shade-tops --metric", int(not shape_ok), 0)

        passing = copy.deepcopy(metrics)
        passing["furys_storage"]["perSlot"]["0x6c"] = 775
        refresh_metric(passing["furys_storage"])
        code, evidence = verdict(repo, profile_path, StubRunner(passing))
        fingerprints_ok = evidence is not None and all(
            len(value) == 64 for value in evidence["fingerprints"].values()
        )
        check("designated 0x6c strict improvement passes", code, 0)
        check("pass records profile/script/corpus fingerprints", int(not fingerprints_ok), 0)

        unrelated = copy.deepcopy(metrics)
        unrelated["furys_storage"]["perSlot"]["0x68"] = 20000
        refresh_metric(unrelated["furys_storage"])
        check(
            "unrelated aggregate improvement cannot substitute for target progress",
            verdict(repo, profile_path, StubRunner(unrelated))[0], 1,
        )

        worsening = copy.deepcopy(metrics)
        worsening["furys_storage"]["perSlot"]["0x6c"] = 777
        refresh_metric(worsening["furys_storage"])
        check("target worsening fails", verdict(repo, profile_path, StubRunner(worsening))[0], 1)

        def default_drift(world: str, metric: dict[str, Any]) -> str:
            if world == "furys_storage":
                metric["buildDefaultsHash"] = "0" * 64
            return json.dumps(metric)

        check(
            "BUILD_DEFAULTS drift is a harness failure",
            verdict(repo, profile_path, StubRunner(metrics, default_drift))[0], 3,
        )

        def override_drift(world: str, metric: dict[str, Any]) -> str:
            if world == "furys_storage":
                metric["overrides"] = ["shadeTops", "hsrGeneralOcclude"]
            return json.dumps(metric)

        check(
            "override drift is a harness failure",
            verdict(repo, profile_path, StubRunner(metrics, override_drift))[0], 3,
        )

        control = copy.deepcopy(metrics)
        control["vikings_collection"]["perSlot"]["0x68"] -= 1
        refresh_metric(control["vikings_collection"])
        check("control-world drift fails", verdict(repo, profile_path, StubRunner(control))[0], 1)

        check(
            "malformed native-diff JSON is a harness failure",
            verdict(repo, profile_path, StubRunner(metrics, lambda _w, _m: "{malformed}"))[0], 3,
        )
        check(
            "missing native-diff metric is a harness failure",
            verdict(repo, profile_path, StubRunner(metrics, lambda _w, _m: "no metric"))[0], 3,
        )

        seed_file = repo / "user-client/render/data/models/offline.bin"
        original = seed_file.read_bytes()
        seed_file.write_bytes(b"corrupt\n")
        check("corrupt corpus is a harness failure", verdict(repo, profile_path, StubRunner(metrics))[0], 3)
        seed_file.write_bytes(original)
        seed_file.unlink()
        check("missing corpus is a harness failure", verdict(repo, profile_path, StubRunner(metrics))[0], 3)
        seed_file.write_bytes(original)

        check(
            "conformance must be green",
            verdict(repo, profile_path, StubRunner(metrics, conformance_rc=1))[0], 1,
        )
    finally:
        shutil.rmtree(temp, ignore_errors=True)

    print(f"gsc-shade-tops-gate: {failures} failure(s)")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
