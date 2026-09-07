"""Local documentation gate. Preflight is not final campaign acceptance."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

AREA = Path(__file__).resolve().parent
ROOT = AREA.parents[4]
START = "6d24f93741ccfd05d6f473e1d50123d7c6e20a8a"

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)

def preflight():
    m = json.loads((AREA / "manifest.json").read_text(encoding="utf-8"))
    assert m["start_commit"] == START
    assert git("branch", "--show-current").decode().strip() == m["branch"]
    assert m["parent"] == "goal-recursion-v2-execution-fabric"
    assert m["maximum_concurrent_readonly_workers"] == 2
    assert m["maximum_discovery_minutes"] == 30
    assert m["new_metered_spend"] == 0
    assert m["provider_trials_authorized"] is False
    assert m["product_implementation_authorized"] is False
    for ancestor in m["required_ancestors"] + [START]:
        git("merge-base", "--is-ancestor", ancestor, "HEAD")
    for record in m["inputs"]:
        assert hashlib.sha256(git("show", START + ":" + record["path"])).hexdigest() == record["git_blob_sha256"]
    print("PREFLIGHT_PASS: frozen scope and inputs; final acceptance remains incomplete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    if not args.preflight:
        sys.exit("FINAL_GATE_INCOMPLETE: campaign synthesis and acceptance tooling pending")
    preflight()
