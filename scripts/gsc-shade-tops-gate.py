#!/usr/bin/env python3
"""Approval-bound forced-on shade-tops acceptance gate for the GSC pilot.

The candidate repository is untrusted.  This controller-owned gate pins the offline seed
corpus and measurement instrument, invokes native-diff with the reviewed override, validates
every field of its JSON output, and accepts only a strict improvement of the designated
0x6c error.  It never prints subprocess output or corpus bytes.

Exit codes: 0 pass, 1 policy failure, 2 no progress, 3 harness failure, 4 tampering.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from seed_contract import SeedContractError, inspect_repository, validate_contract


SCHEMA = "recursion-gsc-shade-tops-gate/v1"
METRIC_SCHEMA = "native-diff-metric/v1"
EVIDENCE_SCHEMA = "recursion-gsc-shade-tops-evidence/v1"
METRIC_KEYS = {
    "schema", "world", "truth", "jumble", "overrides", "buildDefaultsHash",
    "perSlot", "sumAbs", "uncovered", "ours", "native", "delta", "ratio", "vecDigest",
}
MAX_OUTPUT_BYTES = 1024 * 1024


class GateError(RuntimeError):
    def __init__(self, message: str, returncode: int = 3):
        super().__init__(message)
        self.returncode = returncode


@dataclass
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


CommandRunner = Callable[[list[str], Path, int, dict[str, str] | None], CommandResult]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def actual_runner(
    command: list[str], cwd: Path, timeout: int, extra_env: dict[str, str] | None,
) -> CommandResult:
    environment = os.environ.copy()
    if extra_env:
        environment.update(extra_env)
    try:
        result = subprocess.run(
            command, cwd=cwd, env=environment, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateError("a reviewed gate command could not complete") from exc
    if len(result.stdout.encode("utf-8")) + len(result.stderr.encode("utf-8")) > MAX_OUTPUT_BYTES:
        raise GateError("a reviewed gate command exceeded its output bound")
    return CommandResult(result.returncode, result.stdout, result.stderr)


def git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *arguments], capture_output=True, text=True,
            encoding="utf-8", errors="replace", check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GateError("Git provenance could not be measured") from exc


def require_file_hash(root: Path, relative: str, expected: str, label: str) -> Path:
    path = root / relative
    try:
        resolved_root = root.resolve(strict=True)
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise GateError(f"{label} is absent") from exc
    if resolved_root != resolved and resolved_root not in resolved.parents:
        raise GateError(f"{label} escapes its reviewed root")
    if path.is_symlink() or not path.is_file() or sha256_file(path) != expected:
        raise GateError(f"{label} does not match its reviewed SHA-256")
    return path


def require_profile(profile: dict[str, Any]) -> None:
    required = {
        "schema", "profile_id", "base_commit", "implementation_area", "controller_gate",
        "seed_contract", "native_diff", "conformance", "target", "control_worlds", "worlds",
        "timeouts",
    }
    if set(profile) != required or profile.get("schema") != SCHEMA:
        raise GateError("profile schema or fields are not the reviewed contract")
    base = profile.get("base_commit")
    if not isinstance(base, str) or len(base) != 40 or any(c not in "0123456789abcdef" for c in base):
        raise GateError("profile base commit is malformed")
    native = profile.get("native_diff")
    if not isinstance(native, dict) or set(native) != {
        "path", "sha256", "arguments", "metric_schema", "expected_overrides",
        "build_defaults_sha256",
    } or native.get("expected_overrides") != ["shadeTops"]:
        raise GateError("profile does not force exactly the shadeTops override")
    if native.get("arguments") != ["--shade-tops", "--metric"]:
        raise GateError("profile native-diff arguments are not the reviewed forced-on query")
    if native.get("metric_schema") != METRIC_SCHEMA:
        raise GateError("profile native-diff schema is not reviewed")
    hashes = [native.get("sha256"), native.get("build_defaults_sha256")]
    gate = profile.get("controller_gate")
    conformance = profile.get("conformance")
    seed = profile.get("seed_contract")
    if not isinstance(gate, dict) or set(gate) != {"path", "sha256"}:
        raise GateError("profile controller gate identity is malformed")
    if not isinstance(conformance, dict) or set(conformance) != {
        "path", "sha256", "arguments", "baseline_path", "baseline_sha256",
    } or conformance.get("arguments") != ["--no-progress"]:
        raise GateError("profile conformance contract is malformed")
    hashes.extend([gate.get("sha256"), conformance.get("sha256"), conformance.get("baseline_sha256")])
    if any(not isinstance(value, str) or len(value) != 64
           or any(char not in "0123456789abcdef" for char in value) for value in hashes):
        raise GateError("profile contains a malformed SHA-256")
    if not isinstance(seed, dict) or set(seed) != {
        "schema_version", "manifest_path", "manifest_sha256", "content_sha256", "paths",
        "file_count",
    }:
        raise GateError("profile seed contract is malformed")
    if profile.get("implementation_area") != "user-client/render":
        raise GateError("profile implementation area is not the reviewed renderer root")
    timeouts = profile.get("timeouts")
    if not isinstance(timeouts, dict) or set(timeouts) != {
        "native_diff_seconds", "conformance_seconds",
    } or any(type(value) is not int or value < 1 or value > 1800 for value in timeouts.values()):
        raise GateError("profile timeouts are malformed")
    target = profile.get("target")
    if not isinstance(target, dict) or set(target) != {
        "world", "slot", "baseline_delta", "comparison", "non_target_slots",
    }:
        raise GateError("profile target contract is malformed")
    if target.get("slot") != "0x6c" or target.get("comparison") != "strict_abs_decrease":
        raise GateError("profile target must be a strict absolute 0x6c improvement")
    if target.get("non_target_slots") != "exact":
        raise GateError("profile must hold target-world non-target slots exact")
    if profile.get("control_worlds") != "exact_per_slot":
        raise GateError("profile must hold every control world exact per-slot")
    worlds = profile.get("worlds")
    if not isinstance(worlds, list) or not worlds:
        raise GateError("profile has no measured worlds")
    names = [item.get("world") for item in worlds if isinstance(item, dict)]
    if len(names) != len(worlds) or len(set(names)) != len(names) or target.get("world") not in names:
        raise GateError("profile world identities are malformed")
    roles = {item.get("world"): item.get("role") for item in worlds}
    if roles.get(target.get("world")) != "target" or any(
        role not in {"target", "control"} for role in roles.values()
    ):
        raise GateError("profile world roles are malformed")
    if sum(role == "target" for role in roles.values()) != 1:
        raise GateError("profile must declare exactly one target world")
    for item in worlds:
        if set(item) != {"world", "role", "truth", "per_slot", "sum_abs", "uncovered", "native"}:
            raise GateError("profile world evidence fields are malformed")
        if not isinstance(item["per_slot"], dict) or not item["per_slot"] \
                or any(type(value) is not int for value in item["per_slot"].values()):
            raise GateError("profile world vector is malformed")
        if item["sum_abs"] != sum(abs(value) for value in item["per_slot"].values()):
            raise GateError("profile world aggregate is internally inconsistent")
        if type(item["native"]) is not int or item["native"] < 1 \
                or type(item["uncovered"]) is not int or item["uncovered"] < 0:
            raise GateError("profile world totals are malformed")
    target_world = next(item for item in worlds if item["world"] == target["world"])
    if target.get("baseline_delta") != target_world["per_slot"].get(target["slot"]):
        raise GateError("profile target baseline is inconsistent with its vector")


def metric_digest(per_slot: dict[str, int]) -> str:
    lines = "\n".join(f"{slot} {value}" for slot, value in per_slot.items())
    return hashlib.sha256(lines.encode()).hexdigest()


def parse_metric(output: str, expected: dict[str, Any], native: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for line in output.splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GateError("native-diff emitted malformed JSON") from exc
        if isinstance(value, dict) and value.get("schema") == METRIC_SCHEMA:
            records.append(value)
    if len(records) != 1:
        raise GateError("native-diff did not emit exactly one metric record")
    record = records[0]
    if set(record) != METRIC_KEYS:
        raise GateError("native-diff metric fields drifted")
    if record["world"] != expected["world"] or record["truth"] != expected["truth"]:
        raise GateError("native-diff world/truth identity drifted")
    if record["jumble"] is not True or record["overrides"] != native["expected_overrides"]:
        raise GateError("native-diff override or jumble mode drifted")
    if record["buildDefaultsHash"] != native["build_defaults_sha256"]:
        raise GateError("BUILD_DEFAULTS drifted; the reviewed profile must be re-pinned")
    per_slot = record["perSlot"]
    expected_slots = expected["per_slot"]
    if not isinstance(per_slot, dict) or list(per_slot) != list(expected_slots):
        raise GateError("native-diff slot vector shape drifted")
    if any(type(value) is not int for value in per_slot.values()):
        raise GateError("native-diff slot vector contains a non-integer")
    integers = ("sumAbs", "uncovered", "ours", "native", "delta")
    if any(type(record[key]) is not int for key in integers):
        raise GateError("native-diff metric contains a non-integer aggregate")
    signed = sum(per_slot.values())
    absolute = sum(abs(value) for value in per_slot.values())
    if record["sumAbs"] != absolute or record["delta"] != signed:
        raise GateError("native-diff aggregate cross-check failed")
    if record["ours"] - record["native"] != record["delta"]:
        raise GateError("native-diff total cross-check failed")
    ratio = record["ratio"]
    if record["native"] == 0:
        ratio_valid = ratio is None
    else:
        ratio_valid = type(ratio) in {int, float} and math.isfinite(ratio) and math.isclose(
            ratio, record["ours"] / record["native"], rel_tol=1e-12, abs_tol=0.0,
        )
    if not ratio_valid or record["vecDigest"] != metric_digest(per_slot):
        raise GateError("native-diff ratio/vector digest cross-check failed")
    if record["native"] != expected["native"] or record["uncovered"] != expected["uncovered"]:
        raise GateError("native truth or uncovered count drifted")
    return record


def evaluate_metrics(
    profile: dict[str, Any], observed: dict[str, dict[str, Any]],
) -> tuple[int, str]:
    target = profile["target"]
    target_world = target["world"]
    target_slot = target["slot"]
    baseline_delta = target["baseline_delta"]
    for expected in profile["worlds"]:
        world = expected["world"]
        actual_slots = observed[world]["perSlot"]
        for slot, baseline in expected["per_slot"].items():
            if world == target_world and slot == target_slot:
                continue
            if actual_slots[slot] != baseline:
                return 1, f"declared non-target/control vector drifted in {world}"
    candidate_delta = observed[target_world]["perSlot"][target_slot]
    if abs(candidate_delta) > abs(baseline_delta):
        return 1, "designated 0x6c target worsened"
    if abs(candidate_delta) == abs(baseline_delta):
        return 2, "designated 0x6c target made no strict progress"
    return 0, "strict absolute 0x6c improvement with exact controls"


def _safe_profile(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
        raise GateError("reviewed profile is absent or unsafe")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GateError("reviewed profile is unreadable") from exc
    if not isinstance(value, dict):
        raise GateError("reviewed profile is not an object")
    require_profile(value)
    return value


def require_candidate_scope(repo: Path, base_commit: str, implementation_area: str) -> None:
    dirty = git(repo, "status", "--porcelain", "--untracked-files=all")
    if dirty.returncode or dirty.stdout.strip():
        raise GateError("candidate worktree is not clean at its measured commit", 4)
    changed = git(repo, "diff", "--name-only", base_commit, "--")
    untracked = git(repo, "ls-files", "--others", "--exclude-standard")
    if changed.returncode or untracked.returncode:
        raise GateError("candidate path scope could not be measured")
    paths = {line.strip().replace("\\", "/") for line in (
        changed.stdout.splitlines() + untracked.stdout.splitlines()
    ) if line.strip()}
    prefix = implementation_area.rstrip("/") + "/"
    outside = [path for path in paths if not path.startswith(prefix)]
    protected = [path for path in paths if (
        path.endswith(".test.cjs")
        or path.startswith("user-client/render/data/")
        or path.startswith("user-client/render/tools/")
    )]
    if outside:
        raise GateError("candidate changed a path outside the reviewed implementation area", 4)
    if protected:
        raise GateError("candidate changed protected tests, corpus, fixtures, or measurement tools", 4)


def run_gate(
    repo: Path,
    profile_path: Path,
    controller_root: Path,
    gate_script: Path,
    runner: CommandRunner = actual_runner,
) -> tuple[int, dict[str, Any], str]:
    repo = repo.resolve(strict=True)
    controller_root = controller_root.resolve(strict=True)
    profile_path = profile_path.resolve(strict=True)
    profile = _safe_profile(profile_path)
    gate_spec = profile["controller_gate"]
    require_file_hash(controller_root, gate_spec["path"], gate_spec["sha256"], "controller gate")
    if gate_script.resolve(strict=True) != (controller_root / gate_spec["path"]).resolve(strict=True):
        raise GateError("the invoked controller gate is not the reviewed script")

    head = git(repo, "rev-parse", "HEAD")
    if head.returncode or len(head.stdout.strip()) != 40:
        raise GateError("candidate HEAD could not be measured")
    candidate_commit = head.stdout.strip()
    ancestry = git(repo, "merge-base", "--is-ancestor", profile["base_commit"], candidate_commit)
    if ancestry.returncode:
        raise GateError("candidate is not descended from the reviewed GSC base commit")
    require_candidate_scope(repo, profile["base_commit"], profile["implementation_area"])

    native_spec = profile["native_diff"]
    native_path = require_file_hash(repo, native_spec["path"], native_spec["sha256"], "native-diff")
    conformance = profile["conformance"]
    conformance_path = require_file_hash(
        controller_root, conformance["path"], conformance["sha256"], "conformance gate",
    )
    baseline_path = Path(conformance["baseline_path"])
    if not baseline_path.is_file() or baseline_path.is_symlink() \
            or sha256_file(baseline_path) != conformance["baseline_sha256"]:
        raise GateError("conformance baseline does not match its reviewed SHA-256")

    try:
        seed_before = validate_contract(repo, profile["seed_contract"])
    except (OSError, SeedContractError) as exc:
        raise GateError("approved offline corpus is absent, corrupt, or unsafe") from exc

    conformance_result = runner(
        ["bash", str(conformance_path), *conformance["arguments"]], repo,
        profile["timeouts"]["conformance_seconds"], {"GSC_BASELINE": str(baseline_path)},
    )
    if conformance_result.returncode:
        code = conformance_result.returncode if conformance_result.returncode in {1, 3, 4} else 3
        raise GateError("offline conformance was not green", code)

    observed: dict[str, dict[str, Any]] = {}
    commands: list[list[str]] = []
    for world in profile["worlds"]:
        command = [
            "node", native_spec["path"], f"--world={world['world']}",
            *native_spec["arguments"],
        ]
        commands.append(command)
        result = runner(command, repo, profile["timeouts"]["native_diff_seconds"], None)
        if result.returncode:
            raise GateError(f"native-diff could not measure reviewed world {world['world']}")
        observed[world["world"]] = parse_metric(result.stdout, world, native_spec)

    try:
        seed_after = validate_contract(repo, profile["seed_contract"])
    except (OSError, SeedContractError) as exc:
        raise GateError("offline corpus changed during the acceptance gate") from exc
    if seed_after != seed_before:
        raise GateError("offline corpus evidence changed during the acceptance gate")

    result_code, reason = evaluate_metrics(profile, observed)
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "profile_id": profile["profile_id"],
        "base_commit": profile["base_commit"],
        "candidate_commit": candidate_commit,
        "fingerprints": {
            "profile_sha256": sha256_file(profile_path),
            "controller_gate_sha256": sha256_file(gate_script),
            "conformance_gate_sha256": sha256_file(conformance_path),
            "conformance_baseline_sha256": sha256_file(baseline_path),
            "native_diff_sha256": sha256_file(native_path),
            "seed_manifest_sha256": seed_before["manifest_sha256"],
            "seed_content_sha256": seed_before["content_sha256"],
        },
        "seed_file_count": seed_before["file_count"],
        "query": {"overrides": native_spec["expected_overrides"], "arguments": native_spec["arguments"]},
        "measurements": {
            world: {
                "per_slot": metric["perSlot"], "sum_abs": metric["sumAbs"],
                "vector_sha256": metric["vecDigest"],
            }
            for world, metric in observed.items()
        },
        "result": {"returncode": result_code, "reason": reason},
        "command_count": len(commands),
    }
    return result_code, evidence, reason


def main() -> int:
    script = Path(__file__).resolve()
    controller_root = script.parent.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument(
        "--profile", default=str(controller_root / "scripts/gates/gsc-shade-tops-v1.json"),
    )
    args = parser.parse_args()
    try:
        code, evidence, reason = run_gate(
            Path(args.repo), Path(args.profile), controller_root, script, actual_runner,
        )
    except GateError as exc:
        print(f"GATE: FAIL ({exc.returncode}) - {exc}", file=sys.stderr)
        return exc.returncode
    print(json.dumps(evidence, sort_keys=True, separators=(",", ":")))
    if code:
        print(f"GATE: FAIL ({code}) - {reason}", file=sys.stderr)
    else:
        print("GATE: PASS - strict forced-on shade-tops target improvement; controls exact")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
