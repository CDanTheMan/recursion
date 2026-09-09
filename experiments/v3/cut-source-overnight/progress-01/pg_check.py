"""Exact-candidate full gate for conditional progress; never restarts the campaign clock."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

import pg_admission as runner

ROOT, DOC, CODE = runner.ROOT, runner.DOC, runner.CODE
require, read, write = runner.require, runner.read, runner.write
sys.path.insert(0, str(ROOT / "experiments/v3/cut-source-overnight/reopen-01"))
legacy_spec = importlib.util.spec_from_file_location("pg_frozen_documentation_gate", ROOT / "experiments/v3/cut-source-overnight/reopen-01/check_final.py")
legacy = importlib.util.module_from_spec(legacy_spec)
legacy_spec.loader.exec_module(legacy)


def sha(path):
    return runner.digest(path.read_bytes())


def json_bytes(path):
    # Git may represent line endings differently; preserve all JSON tokens and bytes.
    return path.read_bytes().replace(b"\r\n", b"\n")


def verify_run(reference, mode):
    path = (runner.CACHE / reference["execution_relative"]).resolve()
    require(path.is_relative_to(runner.CACHE.resolve()) and path.name == "execution.json", "retained execution containment")
    require(sha(path) == reference["execution_sha256"], "immutable admitted execution receipt")
    execution = read(path)
    require(execution["status"] == "FINISHED" and execution["mode"] == mode and execution["exit_code"] == 0, "successful declared execution")
    require(execution["owned_active_after_cleanup"] == 0 and execution["cleanup_errors"] == [], "complete owned cleanup")
    require(execution["seconds"] < 600 and execution["owned_job_peak_bytes"] <= 2147483648, "retained resource bounds")
    require(execution["limits"] == read(ROOT / DOC / "goal.json")["limits"], "declared bounds unchanged")
    for name, expected in execution["files"].items():
        target = (path.parent / name).resolve()
        require(target.is_relative_to(path.parent) and sha(target) == expected, "retained execution file: " + name)
    require(runner.artifact_size(path.parent) <= 268435456, "retained artifact bound")
    for name, entry in execution["sources"].items():
        if name.startswith(CODE) or name in (DOC + "specification.md", DOC + "goal.json"):
            require(runner.digest(runner.git("show", "HEAD:" + name)) == entry["git_blob_sha256"], "admitted semantic source unchanged: " + name)
    expected_code = {p.relative_to(ROOT).as_posix() for p in (ROOT / CODE).glob("*.py")}
    require(expected_code <= set(execution["sources"]), "all current measurement and gate code admitted")
    return path.parent


def accepted_evidence():
    inputs = read(ROOT / DOC / "inputs.json")
    provenance = read(ROOT / DOC / "input-provenance.json")
    prepared = verify_run(provenance, "prepare")
    require(json_bytes(prepared / "inputs.json") == json_bytes(ROOT / DOC / "inputs.json"), "complete original factory input byte reproduction")
    evidence = read(ROOT / DOC / "evidence.json")
    explored = verify_run(evidence, "explore")
    result = read(ROOT / DOC / "results.json")
    require(read(explored / "result.json") == result, "complete accepted finite result")
    require(result["status"] == "CONDITIONAL_PROGRESS_FINITE_PASS" and result["frontier"] == 0, "declared finite completion")
    require(result["source_validity_proven"] is False and result["deferred_questions_resolved"] == [], "validity remains a premise and deferred questions unresolved")
    require(all(result[k] is False for k in ("campaign_complete", "formal_freeze", "full_comparison_complete", "runtime_integration_support")), "no claim promotion")
    require(result["states_per_representation"] <= 500000 and len(result["profiles"]) == 4, "finite declared domain")
    for profile in result["profiles"]:
        require(sha(explored / profile["graph_file"]) == profile["graph_sha256"], "complete accepted graph")
    predecessor = read(ROOT / DOC / "predecessor.json")
    completion = runner.REOPEN / runner.BASE / "completion.json"
    require(predecessor["candidate"] == runner.BASE and predecessor["completion_sha256"] == sha(completion), "immutable documentation predecessor completion")
    prior = read(completion)
    require(prior["candidate"] == runner.BASE and prior["status"] == "DOCUMENTATION_SLICE_PUBLISHED" and prior["campaign_complete"] is False, "published bounded documentation predecessor")
    for name, expected in prior["all_external_files_before_completion"].items():
        target = (completion.parent / name).resolve()
        require(target.is_relative_to(completion.parent) and sha(target) == expected, "documentation predecessor evidence: " + name)
    return inputs, result, explored


def main(candidate):
    runner.candidate_check(candidate)
    limit, usage = runner.scope(final=True)
    require((limit - runner.now()).total_seconds() > 3600, "complete final-gate reserve")
    inputs, accepted, accepted_directory = accepted_evidence()
    inventory = read(ROOT / "docs/v3/construction/cut-source-overnight-20260908/validation-inventory.json")
    rows = [{"commit": runner.BASE, "branch": "codex/v3-cut-source-continued-20260909", "script": "experiments/v3/cut-source-overnight/reopen-01/check_final.py"},
            {"commit": legacy.PRIOR, "branch": "codex/v3-cut-source-overnight-20260908", "script": "experiments/v3/cut-source-overnight/check.py"}] + inventory["frozen_gates"]
    require(len(rows) == 18 and len(inventory["regression_commands"]) == 25, "complete flat inherited inventory")
    roots = legacy.frozen_roots(rows)
    directory = runner.CACHE / candidate / (runner.now().strftime("%Y%m%dT%H%M%S%f") + "-final")
    directory.mkdir(parents=True, exist_ok=False)
    receipt = {"candidate": candidate, "status": "RUNNING", "started_at": runner.now().isoformat(),
               "usage_at_admission": usage, "commands": [], "campaign_complete": False,
               "classification": "modeled-conditional-collection-progress", "deferred_questions_resolved": []}
    write(directory / "admission.json", receipt)
    try:
        receipt["historical_closure"] = legacy.history()
        for i, (row, root) in enumerate(roots):
            receipt["commands"].append(legacy.command([sys.executable, "-X", "utf8", "-B", row["script"], "--working"], root, directory, "frozen-" + str(i)))
            require(legacy.git_at(root, "rev-parse", "HEAD") == row["commit"] and not legacy.git_at(root, "status", "--porcelain", "--untracked-files=all"), "frozen predecessor unchanged")
        for i, args in enumerate(inventory["regression_commands"]):
            receipt["commands"].append(legacy.command([sys.executable, *args[1:]], ROOT, directory, "regression-" + str(i)))
        prepared = runner.execute("prepare", final=True)
        require(json_bytes(prepared / "inputs.json") == json_bytes(ROOT / DOC / "inputs.json"), "fresh complete factory input byte equality")
        explored = runner.execute("explore", final=True)
        require(read(explored / "result.json") == accepted, "fresh complete finite result equality")
        for profile in accepted["profiles"]:
            name = profile["graph_file"]
            require((explored / name).read_bytes() == (accepted_directory / name).read_bytes(), "fresh exact graph byte equality")
        receipt["fresh_executions"] = [
            {"execution_relative": str((p / "execution.json").relative_to(runner.CACHE)), "execution_sha256": sha(p / "execution.json")}
            for p in (prepared, explored)]
        accepted_evidence()
        runner.candidate_check(candidate)
        runner.scope(final=True)
        require(legacy.history() == receipt["historical_closure"] and len(receipt["commands"]) == 43, "complete unchanged inherited validation")
        receipt["status"] = "CONDITIONAL_PROGRESS_FULL_GATE_PASS"
    except BaseException as error:
        receipt.update(status="FAILED_RETAINED", error=type(error).__name__ + ": " + str(error))
        raise
    finally:
        receipt["finished_at"] = runner.now().isoformat()
        receipt["files"] = {p.name: sha(p) for p in directory.iterdir() if p.is_file()}
        write(directory / "receipt.json", receipt)
        print(str(directory / "receipt.json"), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True)
    arguments = parser.parse_args()
    acquired = []
    try:
        for name in ("heavy-gate.lock", "model.lock"):
            path = runner.OLD / name
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            acquired.append(path)
            with os.fdopen(fd, "w") as handle:
                handle.write(str(os.getpid()))
        main(arguments.candidate)
    finally:
        for path in reversed(acquired):
            path.unlink()
