#!/usr/bin/env python3
"""Check the continuous-WSL specification's scope/traceability, never runtime behavior."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "ba6720c262a1293bd132b5c83504fd6a52e9de72"
SPEC = "docs/v3/construction-swarm/CONTINUOUS-OPERATION.md"
CONTRACT = "docs/v3/construction-swarm/continuous-operation-contract.json"
ALLOWED = {
    SPEC, CONTRACT, "docs/v3/START-HERE.md",
    "state/tasks/wsl-autonomy-spec-20260913.md", "tools/check_wsl_autonomy_spec.py",
}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-c", "core.longpaths=true", *args], cwd=ROOT, encoding="utf-8"
    ).strip()


def indexed(rows: list[dict], label: str) -> dict:
    result = {row["id"]: row for row in rows}
    require(len(result) == len(rows), f"duplicate {label} IDs")
    return result


def check_contract(data: dict, document: str) -> tuple[int, int, int]:
    require(data["schema_version"] == 1, "unsupported contract version")
    require(data["status"] == "proposed_not_implemented", "spec cannot claim implementation")
    require(data["activation_enabled"] is False, "spec cannot activate execution")
    require(data["baseline"] == BASELINE, "baseline mismatch")
    require(data["parent_goal"] == "goal-recursion-v2-execution-fabric", "wrong parent")
    require(data["specification"] == Path(SPEC).name, "wrong specification link")
    requirements = indexed(data["requirements"], "requirement")
    phases = indexed(data["phases"], "phase")
    scenarios = indexed(data["scenarios"], "scenario")
    require(set(requirements) == {f"CW-{n:02d}" for n in range(1, 19)}, "requirement inventory")
    require(set(phases) == {f"P{n}" for n in range(1, 9)}, "phase inventory")
    require(set(scenarios) == {f"S{n:02d}" for n in range(1, 27)}, "scenario inventory")
    headings = re.findall(r"\*\*(CW-\d{2}) —", document)
    require(len(headings) == len(requirements) and set(headings) == set(requirements),
            "document and contract requirement IDs differ")
    phase_rows = re.findall(r"^\| (P\d+) \|", document, re.MULTILINE)
    require(len(phase_rows) == len(phases) and set(phase_rows) == set(phases), "phase table differs")
    for key, row in scenarios.items():
        require(row["status"] == "specified_not_run", f"{key} cannot claim a runtime pass")
        require(row["phase"] in phases, f"{key} unknown phase")
        refs = row["requirements"]
        require(bool(refs) and len(set(refs)) == len(refs) and set(refs) <= requirements.keys(),
                f"{key} invalid requirement references")
        require(len(row["trigger"].strip()) >= 20 and len(row["expected"].strip()) >= 20,
                f"{key} needs a concrete trigger and expected outcome")
    for key, row in requirements.items():
        expected = {sid for sid, scenario in scenarios.items() if key in scenario["requirements"]}
        require(bool(expected) and set(row["scenarios"]) == expected
                and len(row["scenarios"]) == len(expected), f"{key} incomplete scenario mapping")
    settled = set()
    for key, row in phases.items():
        require(set(row["depends_on"]) <= settled, f"{key} cycle, unknown or out-of-order dependency")
        expected = {sid for sid, scenario in scenarios.items() if scenario["phase"] == key}
        require(bool(expected) and set(row["scenarios"]) == expected
                and len(row["scenarios"]) == len(expected), f"{key} scenario mapping differs")
        settled.add(key)
    pilot = data["pilot_proposals"]
    require(0 < pilot["reserved_verifier_slots"] < pilot["worker_slots"] <= pilot["burst_ceiling"],
            "pilot must preserve verification capacity")
    require(pilot["command_slots"] == 4 and pilot["command_seconds"] == 60, "unqualified command expansion")
    require(600 <= pilot["closeout_seconds_min"] < pilot["batch_seconds_max"] <= 28800,
            "pilot exceeds bounded campaign envelope")
    require(pilot["unknown_retries"] == 0, "unknown attempt replay is not allowed")
    for flag in ("metered_spend_enabled", "auto_merge", "auto_reset"):
        require(pilot[flag] is False, f"{flag} cannot be enabled by this spec")
    return len(requirements), len(scenarios), len(phases)


def check_links() -> int:
    links = 0
    for name in (SPEC, "docs/v3/START-HERE.md"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"(?ms)^```[^\n]*\n.*?^```[^\n]*$", "", text)
        text = re.sub(r"`[^`\n]*`", "", text)
        for target in re.findall(r"\]\(([^)]+)\)", text):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            require(resolved.is_relative_to(ROOT) and resolved.exists(), f"missing/local escape link: {target}")
            links += 1
    return links


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", help="full current commit; requires a clean worktree")
    args = parser.parse_args()
    head = git("rev-parse", "HEAD")
    require(git("merge-base", BASELINE, head) == BASELINE, "missing orientation baseline")
    if args.candidate:
        require(re.fullmatch(r"[0-9a-f]{40}", args.candidate) is not None
                and args.candidate == head, "candidate must be the full current HEAD")
        require(not git("status", "--porcelain"), "candidate must be clean")
    changed = set(git("diff", "--name-only", BASELINE).splitlines())
    untracked = set(git("ls-files", "--others", "--exclude-standard").splitlines())
    require(not (changed | untracked) - ALLOWED, "out-of-scope changes")
    require(ALLOWED <= set(git("ls-files").splitlines()), "stage all specification files before checking")
    git("diff", "--check", BASELINE)
    require("construction-swarm/CONTINUOUS-OPERATION.md" in (ROOT / "docs/v3/START-HERE.md").read_text(),
            "spec is absent from the current starting guide")
    counts = check_contract(json.loads((ROOT / CONTRACT).read_text(encoding="utf-8")),
                            (ROOT / SPEC).read_text(encoding="utf-8"))
    links = check_links()
    print(f"candidate={head} mode={'clean-candidate' if args.candidate else 'working'}")
    print(f"SCOPE_PASS baseline={BASELINE} changed={len(changed)}")
    print(f"TRACEABILITY_PASS requirements={counts[0]} scenarios={counts[1]} phases={counts[2]} links={links}")
    print("WSL_AUTONOMY_SPEC_PASS_RUNTIME_NOT_TESTED_NOT_ACTIVATED")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"WSL_AUTONOMY_SPEC_FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
