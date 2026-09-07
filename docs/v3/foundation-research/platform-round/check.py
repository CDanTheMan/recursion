"""Exact-candidate documentation gate; no provider or product runtime execution."""
from __future__ import annotations
import argparse
import copy
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
BASE = "b1b18a1aa59868c4056a730ffc5474ac0f272c10"
M1C = "a7cd9458d37f3090079930bf8d79ffd77c4f73e4"
BRANCH = "codex/v3-formal-model-experiment"
PREFIX = "docs/v3/foundation-research/platform-round/"
DOCS = set("README PRODUCT ARCHITECTURE DECISION-REGISTER CLI EXECUTIVES PLUGINS-AND-EDITIONS PERFORMANCE-PLAN ACCEPTANCE ROADMAP ROUTE-CAPABILITIES".split())
ALLOWED = {"docs/v3/" + name + ".md" for name in DOCS}
REQUIRED = set("campaign.md research-brief.md repository-map.md interaction-contract.md architecture-roadmap.md integration.json trials.json report-source.md check.py".split())
FEATURES = set("streaming questions approvals queued_messages active_steering interruption resume forks compaction commands_plugins".split())
ROUTES = set("native codex claude-binary claude-sdk cursor opencode gemini hermes grok muse deepseek t3".split())
ROLES = set("planning implementation review summarization recovery_analysis".split())
SCENARIOS = set("website bug_fix interrupted_refactor upstream_only".split())
TRIALS = set("integration performance continuity remote configuration simulation".split())
REQUIREMENTS = set("scope audiences native upstream combined roles idle controls coverage configuration plugins setup updates remote resources continuity optimization priorities eligibility innovation sequence later".split())

def need(condition, message):
    if not condition:
        raise ValueError(message)

def closed(obj, fields):
    need(type(obj) is dict and set(obj) == set(fields.split()), "closed record fields differ")

def strings(value):
    need(type(value) is list and value and all(type(v) is str and v.strip() for v in value), "nonempty string list required")

def distinct(rows):
    need(type(rows) is list and rows, "nonempty rows")
    ids = [r["id"] for r in rows]
    need(len(ids) == len(set(ids)), "duplicate IDs")
    return set(ids)

def strict_json(raw):
    def pairs(values):
        result = {}
        for k, v in values:
            need(k not in result, "duplicate JSON key")
            result[k] = v
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))

def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    need(result.returncode == 0, "git failed: " + " ".join(args))
    return result.stdout.decode("utf-8").strip()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def data_gate(matrix, trials):
    closed(matrix, "schema_version scope baseline historical_matrix features reasoning_roles sources route_candidates search_log limitations")
    need(type(matrix["schema_version"]) is int and matrix["schema_version"] == 1, "matrix version")
    need(matrix["baseline"] == BASE and matrix["historical_matrix"] == "../compatibility.json", "historical input binding")
    need(set(matrix["features"]) == FEATURES and len(matrix["features"]) == 10, "feature coverage")
    need(set(matrix["reasoning_roles"]) == ROLES and len(matrix["reasoning_roles"]) == 5, "reasoning role closure")
    source_ids = distinct(matrix["sources"])
    for s in matrix["sources"]:
        closed(s, "id title publisher date_or_version retrieved url section evidence limitation revalidate")
        need(all(type(v) is str and v.strip() for v in s.values()), "source metadata")
        need(s["id"].startswith("platform.source.") and s["url"].startswith("https://"), "source locator")
        need(s["retrieved"] == "2026-09-06", "source date")
    route_ids = distinct(matrix["route_candidates"])
    need(route_ids == {"platform.route." + x for x in ROUTES}, "frontier route coverage")
    for r in matrix["route_candidates"]:
        closed(r, "id mode provider engine integration_interface build version_status authentication billing host technical_status eligibility_status extensions sources capabilities required_probe limitation observed_run")
        need(r["mode"] in {"native", "upstream", "composition-precedent"}, "execution mode")
        need(r["mode"] == ("native" if r["id"].endswith(".native") else "composition-precedent" if r["id"].endswith(".t3") else "upstream"), "mode ownership")
        need(r["build"] is None and r["observed_run"] is None, "no invented observed integration/build")
        need(r["technical_status"] == "documented-candidate" and r["eligibility_status"] == "context-specific-unverified", "evidence/eligibility separation")
        for key in ("provider", "engine", "integration_interface", "authentication", "billing", "host", "version_status", "extensions", "limitation"):
            need(type(r[key]) is str and r[key].strip(), "route field " + key)
        strings(r["sources"])
        need(set(r["sources"]) <= source_ids, "unknown route source")
        need(r["required_probe"] == "trial.integration", "probe link")
        need(len(r["capabilities"]) == 10 and {c["feature"] for c in r["capabilities"]} == FEATURES, "route feature coverage")
        for c in r["capabilities"]:
            closed(c, "feature status scope sources")
            need(c["status"] in {"documented-mechanism", "unknown"}, "invalid capability evidence status")
            need(type(c["scope"]) is str and "trial.integration" in c["scope"], "capability limitation")
            if c["status"] == "documented-mechanism":
                strings(c["sources"])
                need(len(c["sources"]) == len(set(c["sources"])), "duplicate capability source")
                need(set(c["sources"]) <= source_ids, "unknown capability source")
                need(set(c["sources"]) <= set(r["sources"]), "capability source not route-applicable")
            else:
                need(c["sources"] == [], "unknown capability has no supporting claim source")
    strings(matrix["search_log"])
    strings(matrix["limitations"])
    closed(trials, "schema_version status hard_floors priorities scenarios trials results_available")
    need(type(trials["schema_version"]) is int and trials["schema_version"] == 1, "trial version")
    need(trials["status"] == "preregistered-designs-not-run" and trials["results_available"] is False, "no invented results")
    need(trials["priorities"] == ["responsiveness", "subscription_efficiency", "task_completion"], "Owner ranking")
    strings(trials["hard_floors"])
    need(distinct(trials["scenarios"]) == SCENARIOS, "scenario coverage")
    for s in trials["scenarios"]:
        closed(s, "id task success fault")
        need(all(type(v) is str and v.strip() for v in s.values()), "scenario text")
    need(distinct(trials["trials"]) == {"trial." + x for x in TRIALS}, "trial coverage")
    for t in trials["trials"]:
        closed(t, "id status question baseline treatments scenarios unit workload version_freeze matched_budget metrics faults analysis stop_rule adoption_rule required_authorization contract_links result")
        need(t["status"] == "preregistered-design-not-run" and t["result"] is None, "unrun trial")
        need(set(t["scenarios"]) == SCENARIOS and len(t["scenarios"]) == 4, "all four scenarios")
        for key in ("treatments", "metrics", "faults", "contract_links"):
            strings(t[key])
        for key in ("question", "baseline", "unit", "workload", "version_freeze", "matched_budget", "analysis", "stop_rule", "adoption_rule", "required_authorization"):
            need(type(t[key]) is str and t[key].strip(), "trial field " + key)
        for p in t["contract_links"]:
            target = (ROOT / p).resolve()
            need(target.is_relative_to(ROOT) and target.is_file(), "trial contract link")
    return len(source_ids), len(route_ids)

def adversarial(matrix, trials):
    mutants = []
    a = copy.deepcopy(matrix); a["features"].pop(); mutants.append((a, trials))
    a = copy.deepcopy(matrix); a["reasoning_roles"].remove("review"); mutants.append((a, trials))
    a = copy.deepcopy(matrix); a["route_candidates"][0]["observed_run"] = "fabricated"; mutants.append((a, trials))
    a = copy.deepcopy(matrix); a["route_candidates"][0]["sources"] = ["missing"]; mutants.append((a, trials))
    a = copy.deepcopy(matrix); a["route_candidates"].pop(); mutants.append((a, trials))
    a = copy.deepcopy(matrix); a["route_candidates"][3]["mode"] = "native"; mutants.append((a, trials))
    a = copy.deepcopy(matrix); a["route_candidates"][0]["capabilities"][0]["status"] = "observed"; mutants.append((a, trials))
    b = copy.deepcopy(trials); b["scenarios"].pop(); mutants.append((matrix, b))
    b = copy.deepcopy(trials); b["trials"][0]["result"] = {"pass": True}; mutants.append((matrix, b))
    b = copy.deepcopy(trials); b["priorities"].reverse(); mutants.append((matrix, b))
    b = copy.deepcopy(trials); b["trials"][0]["required_authorization"] = ""; mutants.append((matrix, b))
    b = copy.deepcopy(trials); b["extra"] = True; mutants.append((matrix, b))
    # Codex streaming is documented. Exercise missing, empty, unknown and unrelated bindings.
    a = copy.deepcopy(matrix); del a["route_candidates"][1]["capabilities"][0]["sources"]; mutants.append((a, trials))
    a = copy.deepcopy(matrix); a["route_candidates"][1]["capabilities"][0]["sources"] = []; mutants.append((a, trials))
    a = copy.deepcopy(matrix); a["route_candidates"][1]["capabilities"][0]["sources"] = ["missing"]; mutants.append((a, trials))
    a = copy.deepcopy(matrix); a["route_candidates"][1]["capabilities"][0]["sources"] = ["platform.source.gemini-auth"]; mutants.append((a, trials))
    for m, t in mutants:
        try:
            data_gate(m, t)
        except (ValueError, KeyError, TypeError):
            continue
        raise ValueError("adversarial mutant accepted")
    return len(mutants)

def document_gate():
    need({p.name for p in AREA.iterdir() if p.is_file()} == REQUIRED, "artifact inventory")
    for p in AREA.glob("*.md"):
        content = p.read_text(encoding="utf-8")
        for raw in re.findall(r"\]\(([^)]+)\)", content):
            if raw.startswith("https://"):
                continue
            rel = raw.split("#", 1)[0]
            need(bool(rel), "empty local link")
            target = (p.parent / rel).resolve()
            need(target.is_relative_to(ROOT) and target.is_file(), "broken link: " + raw)
    map_text = (AREA / "repository-map.md").read_text(encoding="utf-8")
    for key in REQUIREMENTS:
        need("| " + key + " |" in map_text, "missing mapped requirement: " + key)
    contract = (AREA / "interaction-contract.md").read_text(encoding="utf-8")
    for key in FEATURES:
        need("| " + key + " |" in contract, "missing control contract")
    register = (ROOT / "docs/v3/DECISION-REGISTER.md").read_text(encoding="utf-8")
    for n in range(21, 26):
        need(register.count("| OR-0" + str(n) + " |") == 1, "Owner ruling uniqueness")
    for p in AREA.iterdir():
        if p.suffix in {".md", ".json"}:
            text = p.read_text(encoding="utf-8")
            need(not re.search(r"(?i)(?:C:[/\\]Users[/\\]|PRIVATE KEY-----|sk-[A-Za-z0-9]{20,}|xai-[A-Za-z0-9]{20,})", text), "private path/credential pattern")
    return len(REQUIREMENTS)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    need(args.base == BASE and re.fullmatch("[0-9a-f]{40}", args.candidate), "explicit frozen full hashes")
    need(git("rev-parse", "HEAD") == args.candidate, "exact HEAD")
    need(git("branch", "--show-current") == BRANCH, "branch")
    need(not git("status", "--porcelain=v1", "--untracked-files=all"), "clean candidate required")
    git("merge-base", "--is-ancestor", BASE, args.candidate)
    git("merge-base", "--is-ancestor", M1C, args.candidate)
    worktrees = git("worktree", "list", "--porcelain").split("\n\n")
    owners = [x for x in worktrees if "branch refs/heads/" + BRANCH in x.splitlines()]
    need(len(owners) == 1 and Path(owners[0].splitlines()[0][9:]).resolve() == ROOT, "worktree ownership")
    changed = git("diff", "--name-only", "--no-renames", BASE, args.candidate).splitlines()
    need(changed and all(p in ALLOWED or (p.startswith(PREFIX) and p[len(PREFIX):] in REQUIRED) for p in changed), "full diff allowlist")
    need(not git("diff", "--name-only", "--diff-filter=D", BASE, args.candidate), "no deletion")
    git("diff", "--check", BASE, args.candidate)
    matrix = strict_json((AREA / "integration.json").read_text(encoding="utf-8"))
    trials = strict_json((AREA / "trials.json").read_text(encoding="utf-8"))
    sources, routes = data_gate(matrix, trials)
    mutants = adversarial(matrix, trials)
    requirements = document_gate()
    # This file is unchanged from the reviewed baseline, enforced by the full-diff allowlist.
    prior = runpy.run_path(str(AREA.parent / "check.py"))
    commands = prior["regression_commands"]()
    need(len(commands) == 25, "frozen regression inventory")
    receipts = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for command in commands:
        command = [sys.executable, *command[1:]]
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, timeout=240)
        receipt = {"command": command[1:], "exit_code": result.returncode,
                   "output_sha256": digest(result.stdout + result.stderr)}
        receipts.append(receipt)
        print(json.dumps(receipt), flush=True)
        need(result.returncode == 0, "regression failed; inspect named command")
    need(git("rev-parse", "HEAD") == args.candidate and not git("status", "--porcelain=v1", "--untracked-files=all"), "candidate changed during gate")
    artifacts = {p: git("rev-parse", args.candidate + ":" + p) for p in changed}
    receipt = {"candidate": args.candidate, "base": BASE, "artifacts": artifacts, "regressions": receipts}
    print("PLATFORM_GATE_PASS " + json.dumps({"candidate": args.candidate, "sources": sources,
          "routes": routes, "features": routes * 10, "requirements": requirements,
          "regressions": len(receipts), "adversarial": mutants,
          "receipt_sha256": digest(json.dumps(receipt, sort_keys=True).encode())}), flush=True)

if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print("PLATFORM_GATE_FAIL " + str(error), file=sys.stderr)
        sys.exit(1)
