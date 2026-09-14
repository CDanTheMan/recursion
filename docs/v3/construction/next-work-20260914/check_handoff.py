"""Read-only v3 handoff/source check; never imports a scientific model or provider."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PACKETS = Path(__file__).resolve().parent


def git(*args):
    return subprocess.check_output(
        ["git", "-c", "core.longpaths=true", *args], cwd=ROOT, encoding="utf8"
    ).strip()


def require(condition, reason):
    if not condition:
        raise SystemExit("HANDOFF_REFUSED: " + reason)


def tree(ref, prefix):
    rows = {}
    for line in git("ls-tree", "-r", ref, "--", prefix).splitlines():
        entry, path = line.split("\t", 1)
        rows[path] = entry
    return rows


def main():
    require(Path.cwd().resolve() == ROOT.resolve(), "run from this task worktree root")
    audit = json.loads((PACKETS / "spec-preservation.json").read_text(encoding="utf8"))
    current = git("rev-parse", "HEAD")
    base = audit["references"]["reviewed_development"]
    require(subprocess.run(["git", "merge-base", "--is-ancestor", base, current],
                           cwd=ROOT, check=False).returncode == 0,
            "wrong starting tree: reviewed development source is not an ancestor")
    require((ROOT / "docs/v3/START-HERE.md").is_file(), "v3 entry point missing")
    for row in audit["top_level_v3_markdown"]:
        for ref, oid in row["git_blob_ids"].items():
            require(git("rev-parse", audit["references"][ref] + ":" + row["path"]) == oid,
                    "historical source binding changed: " + row["path"])
        if row["identical"]:
            require(git("rev-parse", current + ":" + row["path"]) == row["git_blob_ids"]["reviewed_development"],
                    "product specification changed outside these packet scopes: " + row["path"])
    for prefix, result in audit["preserved_scopes"].items():
        old = tree(audit["references"]["pr118"], prefix)
        new = tree(current, prefix)
        require(len(old) == result["prior_count"], "historical inventory mismatch")
        require(all(new.get(path) == value for path, value in old.items()),
                "historical scientific source/fixture was changed: " + prefix)
        reviewed = tree(base, prefix)
        require(all(new.get(path) == value for path, value in reviewed.items()),
                "reviewed-development scientific source/fixture was changed: " + prefix)
    for name in ["01-sol-service-access.md", "02-astra-product-frontier.md", "03-sol-recovery-ledger.md"]:
        value = (PACKETS / name).read_text(encoding="utf8")
        for marker in ["goal-recursion-v2-execution-fabric", "COMMON.md", "Allowed new paths only:", "NEW acceptance", "independent"]:
            # The comparison task separates preflight from scientific execution explicitly.
            present = marker in value or (marker == "NEW acceptance" and "NEW source/fake-fixture acceptance" in value)
            require(present, name + " lacks task binding: " + marker)
        require("python -X utf8 -B" in value, name + " has no executable gate interface")
    require(audit["identical_top_level_count"] == 49, "unexpected preservation inventory")
    print(json.dumps({"status": "HANDOFF_SOURCE_PASS", "candidate": current,
                      "unchanged_v3_top_level_specs": 49,
                      "packets": 3, "scientific_execution": False,
                      "implementation_gates_executed": False,
                      "provider_calls": 0, "service_activation": False}, sort_keys=True))


if __name__ == "__main__":
    main()
