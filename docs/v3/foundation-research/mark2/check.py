"""Exact-candidate Owner-answer capture gate; no provider or product runtime."""
from __future__ import annotations
import argparse
import copy
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
AREA = Path(__file__).resolve().parent
BASE = "eca487c986b1a6753e5f785459be8cb73883087e"
PLATFORM = "9d7bacaf54b813e8350caad06cc541c9f9f5a33f"
M1C = "a7cd9458d37f3090079930bf8d79ffd77c4f73e4"
SOURCE = "8a1c40f1a5a127b193997ee36f0365d227b474e34e9763bcb06367b13ff0a264"
DOCS = set("README PRODUCT ARCHITECTURE DECISION-REGISTER CLI EXECUTIVES PLUGINS-AND-EDITIONS PERFORMANCE-PLAN ACCEPTANCE ROADMAP ROUTE-CAPABILITIES".split())
PREFIX = "docs/v3/foundation-research/mark2/"
FILES = {"handoff.md", "directions.json", "check.py"}
ALLOWED = {"docs/v3/" + x + ".md" for x in DOCS} | {PREFIX + x for x in FILES} | {"docs/v3/foundation-research/platform-round/research-brief.md"}
OLD = runpy.run_path(str(AREA.parent / "platform-round/check.py"))
need, closed, strings, strict_json, git = (OLD[x] for x in ("need", "closed", "strings", "strict_json", "git"))

def data_gate(d):
    closed(d, "schema_version kind date base source requested_integrations launch_critical_names reference_candidates modes recovery_cap execution answers")
    need(type(d["schema_version"]) is int and d["schema_version"] == 1, "version")
    need(d["kind"] == "owner-answer-capture-not-integration-evidence" and d["base"] == BASE and d["date"] == "2026-09-06", "capture identity")
    closed(d["source"], "title sha256 questionnaire_complete compiled_owner_review private_transcript_tracked")
    need(d["source"] == {"title": "Recursion Brainstorming Mark 2.md", "sha256": SOURCE, "questionnaire_complete": True, "compiled_owner_review": "not separately recorded", "private_transcript_tracked": False}, "source binding")
    expected = ["BYOK", "ChatGPT OAuth", "Hermes", "DeepSeek Harness", "Muse Code", "Grok Build", "Cursor first-party", "Cursor third-party", "Claude Code", "Gemini CLI", "Antigravity", "Codex", "OpenCode"]
    need(d["requested_integrations"] == expected, "requested coverage")
    need(d["launch_critical_names"] == ["Grok", "Cursor", "Gemini", "Claude", "Hermes", "OpenCode", "ChatGPT"], "critical coverage")
    strings(d["reference_candidates"])
    need(d["modes"] == {
        "stop": ["aggressive", "full", "lazy"],
        "plugin_incompatibility": ["state_incompatibility", "recommend_combinations", "no_action", "notify_and_recommend"],
        "configuration_propagation": ["outstanding_sessions", "new_sessions_only"],
        "software_update": ["interrupt_save_update_resume", "interrupt_update_stop_tasks", "wait_current_tasks", "auto_update_off", "notify_escalate_owner", "stop_everything_wait_update"]
    }, "required mode distinctions")
    r = d["recovery_cap"]
    closed(r, "formula units example_fraction examples universal_default changes_other_limits retained_artifact_fraction")
    need(r["formula"] == "additional_recovery <= configured_fraction * pre_shutdown_task_consumption", "recovery denominator")
    need(r["units"] == ["tokens", "subscription_quota", "api_spending"], "recovery units")
    need(type(r["example_fraction"]) is float and r["example_fraction"] == 0.1, "illustrative fraction")
    need(r["universal_default"] is None and r["changes_other_limits"] is False and r["retained_artifact_fraction"] is False, "no invented recovery policy")
    need(len(r["examples"]) == 3 and [x["unit"] for x in r["examples"]] == r["units"], "examples")
    for x in r["examples"]:
        closed(x, "unit prior additional_max")
        need(all(type(x[k]) in (int, float) and x[k] > 0 for k in ("prior", "additional_max")), "numeric examples")
        need(Decimal(str(x["prior"])) * Decimal(str(r["example_fraction"])) == Decimal(str(x["additional_max"])), "relative-cap arithmetic")
    need(d["execution"] == {"observed_runs": [], "personal_inventory": None, "experiment_budget": None, "resource_question_status": "complete-research-disposition", "sequence": ["integration_mapping_and_bounded_probes", "formal_model", "language_comparison", "storage_comparison"]}, "research disposition and unrun boundary")
    answers = d["answers"]
    need(type(answers) is list and len(answers) == 10, "ten answers")
    expected_status = ["accepted-direction", "accepted-direction-and-research", "accepted-direction", "accepted-direction", "research-disposition", "accepted-direction-and-research", "accepted-direction", "accepted-direction", "accepted-direction-and-research", "research-disposition"]
    for n, a in enumerate(answers, 1):
        closed(a, "question ruling status accepted selected_defaults research_not_selected source_sections affected_docs compatibility_obligations")
        need(type(a["question"]) is int and a["question"] == n and a["ruling"] == "OR-0" + str(25+n), "answer/ruling identity")
        need(a["status"] == expected_status[n-1], "answer disposition")
        for key in ("accepted", "research_not_selected", "source_sections", "affected_docs", "compatibility_obligations"):
            strings(a[key])
        need(set(a["affected_docs"]) <= {x+".md" for x in DOCS}, "canonical map")
        if n in (2, 3, 4, 5, 6, 7, 10):
            need(a["selected_defaults"] == [], "unselected defaults")
        else:
            strings(a["selected_defaults"])
    return len(answers)

def adversarial(d):
    mutations = [
        lambda x: x["launch_critical_names"].pop(),
        lambda x: x["modes"]["stop"].pop(),
        lambda x: x["modes"]["software_update"].pop(),
        lambda x: x["modes"]["configuration_propagation"].pop(),
        lambda x: x["recovery_cap"]["examples"][1].update(additional_max=0.1),
        lambda x: x["recovery_cap"].update(universal_default=0.1),
        lambda x: x["execution"].update(experiment_budget=1),
        lambda x: x["execution"].update(resource_question_status="awaiting-owner-inventory"),
        lambda x: x["answers"][1].update(selected_defaults=["advisory-only"]),
        lambda x: x["source"].update(sha256="0"*64),
    ]
    for mutate in mutations:
        altered = copy.deepcopy(d)
        mutate(altered)
        try:
            data_gate(altered)
        except (ValueError, KeyError, TypeError):
            continue
        raise ValueError("invalid Owner capture accepted")
    return len(mutations)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    need(args.base == BASE and re.fullmatch("[0-9a-f]{40}", args.candidate), "full frozen hashes")
    need(git("branch", "--show-current") == "codex/v3-formal-model-experiment", "branch")
    need(git("rev-parse", "HEAD") == args.candidate and not git("status", "--porcelain=v1", "--untracked-files=all"), "clean exact candidate")
    for ancestor in (BASE, PLATFORM, M1C):
        git("merge-base", "--is-ancestor", ancestor, args.candidate)
    owners = [x for x in git("worktree", "list", "--porcelain").split("\n\n") if "branch refs/heads/codex/v3-formal-model-experiment" in x.splitlines()]
    need(len(owners) == 1 and Path(owners[0].splitlines()[0][9:]).resolve() == ROOT, "exclusive worktree")
    changed = git("diff", "--name-only", "--no-renames", BASE, args.candidate).splitlines()
    need(changed and set(changed) <= ALLOWED, "capture allowlist; historical/M1/runtime unchanged")
    need(not git("diff", "--name-only", "--diff-filter=D", BASE, args.candidate), "no deletion")
    git("diff", "--check", BASE, args.candidate)
    need({p.name for p in AREA.iterdir() if p.is_file()} == FILES, "artifact inventory")
    d = strict_json((AREA / "directions.json").read_text(encoding="utf-8"))
    answers, mutants = data_gate(d), adversarial(d)
    for path in changed:
        p = ROOT / path
        if p.suffix == ".md":
            for link in re.findall(r"\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
                if link.startswith(("https://", "http://")):
                    continue
                rel = link.split("#", 1)[0]
                target = (p.parent / rel).resolve()
                need(target.is_relative_to(ROOT) and target.is_file(), "local link " + link)
    register = (ROOT / "docs/v3/DECISION-REGISTER.md").read_text(encoding="utf-8")
    for n in range(26, 36):
        need(register.count("| OR-0"+str(n)+" |") == 1, "new ruling uniqueness")
    for p in (AREA / "directions.json", AREA / "handoff.md"):
        need(not re.search(r"(?i)(?:C:[/\\]Users[/\\]|PRIVATE KEY-----|sk-[A-Za-z0-9]{20,}|xai-[A-Za-z0-9]{20,})", p.read_text(encoding="utf-8")), "private path/credential pattern")
    oldarea = AREA.parent / "platform-round"
    m = strict_json((oldarea / "integration.json").read_text(encoding="utf-8"))
    t = strict_json((oldarea / "trials.json").read_text(encoding="utf-8"))
    OLD["data_gate"](m,t)
    oldmutants = OLD["adversarial"](m,t)
    OLD["document_gate"]()
    prior = runpy.run_path(str(AREA.parent / "check.py"))
    commands = prior["regression_commands"]()
    need(len(commands) == 25, "frozen regression inventory")
    receipts = []
    for command in commands:
        result = subprocess.run([sys.executable, *command[1:]], cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), capture_output=True, timeout=240)
        row = {"command": command[1:], "exit_code": result.returncode, "output_sha256": hashlib.sha256(result.stdout + result.stderr).hexdigest()}
        receipts.append(row)
        print(json.dumps(row), flush=True)
        need(result.returncode == 0, "regression failed: " + " ".join(command[1:]))
    need(git("rev-parse", "HEAD") == args.candidate and not git("status", "--porcelain=v1", "--untracked-files=all"), "candidate changed")
    receipt = {"base": BASE, "candidate": args.candidate, "source": SOURCE, "artifacts": {x:git("rev-parse", args.candidate+":"+x) for x in changed}, "regressions":receipts}
    print("MARK2_GATE_PASS " + json.dumps({"candidate":args.candidate, "answers":answers, "adversarial":mutants, "platform_adversarial":oldmutants, "regressions":len(receipts), "receipt_sha256":hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest()}),flush=True)

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print("MARK2_GATE_FAIL "+str(error),file=sys.stderr)
        sys.exit(1)
