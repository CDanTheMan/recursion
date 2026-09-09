"""Read-only documentation gate; never a protocol or publication acceptance gate."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
DOC = "docs/v3/construction/cut-source-overnight-20260908/reopen-01/"
CODE = "experiments/v3/cut-source-overnight/reopen-01/"
PRIOR = "89ea6390774c4ef9b5c3727ad2715c57f12af90a"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, timeout=30).decode().strip()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(candidate=None):
    amendment = read(ROOT / DOC / "amendment.json")
    inventory = read(ROOT / DOC / "work-inventory.json")
    common = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir"))
    require(amendment["campaign"] == inventory["campaign"] == "SC-CUT-SOURCE-01", "campaign identity")
    require(amendment["parent_goal"] == "goal-recursion-v2-execution-fabric", "parent identity")
    require("status: active" in (ROOT / "state/goals/goal-recursion-v2-execution-fabric.md").read_text(), "active parent")
    require(not (ROOT / "state/PAUSE").exists() and not (common.parent / "state/PAUSE").exists(), "PAUSE")
    require(amendment["original_started_at"] == "2026-09-09T03:40:33Z", "preserved activation")
    require(amendment["deadline_utc"] == "2026-09-09T15:30:00Z", "fixed amended deadline")
    require(amendment["discovery_cutoff_utc"] == "2026-09-09T12:30:00Z", "final three-hour reserve")
    require(dt.datetime.now(dt.timezone.utc) < dt.datetime.fromisoformat(amendment["deadline_utc"]), "absolute deadline has expired")
    require(amendment["clock_restart"] is False, "clock cannot restart")
    require(dt.datetime.fromisoformat(amendment["local_deadline"]) == dt.datetime.fromisoformat(amendment["deadline_utc"]), "local/UTC deadline agreement")
    require(amendment["timezone"] == "America/Los_Angeles", "timezone")
    require(amendment["settings"] == {"model": "gpt-6-astra", "reasoning": "high", "speed": "standard", "changes_authorized": False}, "preserved settings")
    require(amendment["maximum_banked_resets"] == 1 and amendment["new_metered_spend"] == 0, "capacity authority")
    receipt = common / amendment["receipt_relative_to_git_common"]
    require(receipt.resolve().is_relative_to(common.resolve()), "receipt containment")
    require(digest(receipt) == amendment["receipt_sha256"], "immutable amendment receipt")
    authority = read(receipt)
    for key in ("original_started_at", "deadline_utc", "discovery_cutoff_utc", "prior_candidate", "branch", "settings", "maximum_banked_resets", "reset_idempotency_key", "new_metered_spend"):
        require(amendment[key] == authority[key], "receipt agreement: " + key)
    ledger = read(receipt.parent / "reset-ledger.json")
    require(ledger["maximum_applied"] == 1 and type(ledger["applied_count"]) is int and 0 <= ledger["applied_count"] <= 1, "reset bound")
    require(ledger["idempotency_key"] == amendment["reset_idempotency_key"], "one reset identity")
    completion = common / "research-attestations/cut-source-overnight" / PRIOR / "completion.json"
    require(digest(completion) == amendment["prior_completion_sha256"], "immutable prior completion")
    require(amendment["prior_candidate"] == PRIOR, "immutable first slice")
    require(git("branch", "--show-current") == amendment["branch"], "continuation branch")
    git("merge-base", "--is-ancestor", PRIOR, "HEAD")
    paths = git("diff", "--name-only", PRIOR).splitlines()
    paths += git("ls-files", "--others", "--exclude-standard").splitlines()
    require(all(p.startswith(DOC) or p in (CODE + "check_docs.py", CODE + "check_final.py") for p in paths), "conservative documentation and validation allowlist")
    require(not git("diff", "--name-only", "--diff-filter=DMRT", PRIOR), "prior files unchanged")
    git("diff", "--check", PRIOR)
    if candidate:
        require(len(candidate) == 40 and candidate == git("rev-parse", "HEAD"), "exact candidate")
        require(not git("status", "--porcelain", "--untracked-files=all"), "clean candidate")
    require(amendment["conservative_resume"]["cause"] == "unknown", "no invented safeguard cause")
    require(amendment["conservative_resume"]["alternate_model_retry"] is False and amendment["conservative_resume"]["safeguard_override"] is False, "no safeguard bypass")
    for document in (amendment, inventory):
        require(all(document[k] is False for k in ("formal_freeze", "full_comparison_complete", "runtime_integration_support")), "no claim promotion")
    require(inventory["campaign_complete"] is False and inventory["publication_ready"] is False, "document validation is not campaign completion/publication")
    questions = inventory["questions"]
    ids = [q["id"] for q in questions]
    require(ids == ["D1", "D2", "D3", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6"], "complete remaining-work inventory")
    for index, question in enumerate(questions):
        require(question["required"] is True and question["question"] and question["acceptance"] and question["residual"], "explicit question obligation")
        require(all(dep in ids[:index] for dep in question["depends_on"]), "ordered dependencies")
        require(question["status"] in ("open", "documented-awaiting-review", "deferred-safeguard"), "review completion requires separate exact-candidate receipts")
        if question["status"] == "documented-awaiting-review":
            require(bool(question["evidence"]), "documented answer requires evidence")
        if question["id"].startswith("Q"):
            require(question["status"] == "deferred-safeguard", "interrupted work remains deferred")
        for name in question["evidence"]:
            evidence = (ROOT / DOC / name).resolve()
            require(evidence.is_relative_to((ROOT / DOC).resolve()) and evidence.is_file(), "existing local evidence")
    require(inventory["prior_finite_result"] == {"candidate": PRIOR, "profiles": 51, "environments": 104, "states_per_representation": 17966, "edges_per_representation": 31140, "frontier": 0, "classification": "modeled", "scope": "Declared finite profiles only; no general convergence claim."}, "preserved finite result scope")
    for name in ("execution-prompt.md", "safeguard-record.md"):
        require((ROOT / DOC / name).is_file(), "required document: " + name)
    return {"status": "DOCUMENTATION_VALID", "candidate": candidate, "prior_candidate": PRIOR, "changed_paths": len(set(paths)), "new_model_executions": 0, "publication_authorized_by_this_gate": False, "campaign_complete": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate")
    args = parser.parse_args()
    print(json.dumps(check(args.candidate), sort_keys=True))
