"""Bounded campaign gate. Preflight is not final acceptance or probe admission."""
import argparse
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
CAMPAIGN = ROOT / "docs/v3/construction/interface-probes-20260907"

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()

def preflight():
    goal = json.loads((CAMPAIGN / "goal.json").read_text(encoding="utf-8"))
    assert git("branch", "--show-current") == goal["branch"]
    for ref in (goal["start_commit"], goal["required_research_ancestor"]):
        subprocess.run(["git", "merge-base", "--is-ancestor", ref, "HEAD"], cwd=ROOT, check=True)
    assert goal["new_metered_spend"] == 0 and not goal["usage_resets_allowed"]
    assert goal["parent_goal"] == "goal-recursion-v2-execution-fabric"
    assert "status: active" in (ROOT / "state/goals/goal-recursion-v2-execution-fabric.md").read_text()
    return goal

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--candidate")
    args = parser.parse_args()
    preflight()
    if args.preflight:
        print("CAMPAIGN_PREFLIGHT_PASS; final acceptance and execution admission remain separate")
    else:
        raise SystemExit("Final evidence gate is not yet constructed; campaign is incomplete")
