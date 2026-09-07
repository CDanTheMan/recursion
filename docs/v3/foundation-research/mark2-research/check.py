"""Exact-candidate Mark 2 documentation/evidence gate. No provider or product probes."""
from __future__ import annotations
import argparse
import ast
import copy
from functools import lru_cache
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[4]
AREA = Path(__file__).resolve().parent
START = "770dc8f9f68389693717f553a0bc224d781838f6"
BRANCH = "codex/v3-formal-model-experiment"
ANCESTORS = ["eca487c986b1a6753e5f785459be8cb73883087e", "a7cd9458d37f3090079930bf8d79ffd77c4f73e4"]
CAMPAIGN = "recursion.v3.foundation.mark2.research.20260906"
PREFIX = "docs/v3/foundation-research/mark2-research/"
DOCS = "README PRODUCT ARCHITECTURE EXECUTIVES EXECUTION-FABRIC PLANNING CLI TERMINAL-RUNTIME INTERACTION-SURFACES CONTEXT PLUGINS-AND-EDITIONS SECURITY TELEMETRY PERFORMANCE-PLAN ACCEPTANCE ROADMAP CONSTRUCTION-RUNBOOK DECISION-REGISTER CLAIM-LEDGER SOURCE-REGISTER ROUTE-CAPABILITIES RESEARCH-HYPOTHESES".split()
ALLOWED = {"docs/v3/" + x + ".md" for x in DOCS} | {"docs/v3/CLAIM-REGISTRY.json"}
FILES = set("campaign.md manifest.json report-source.md evidence.json compatibility.json experiments.json decisions.json grillme.md check.py validation-inventory.json".split())
FEATURES = "streaming questions approvals queued_messages active_steering interruption resume forks compaction commands_plugins".split()
FAMILIES = "integration performance continuity remote configuration simulation assistants update_recovery".split()
PACKETS = "routes assistants controls plugins recovery value".split()
STATUSES = {"source-documented", "locally-observed", "inferred", "unsupported", "unknown", "proposed"}
HEX40, HEX64 = re.compile("[0-9a-f]{40}"), re.compile("[0-9a-f]{64}")
PUBLIC_HOSTS = set("learn.chatgpt.com developers.openai.com code.claude.com support.claude.com cursor.com docs.cursor.com raw.githubusercontent.com docs.x.ai research.meta.ai antigravity.google ai.google.dev dev.opencode.ai opencode.ai learn.microsoft.com docs.kernel.org agentclientprotocol.com modelcontextprotocol.io playwright.dev developer.chrome.com deepseek-harness.github.io docs.aws.amazon.com specs.openstack.org www.usenix.org arxiv.org metr.org www.anthropic.com pi.dev git-scm.com".split())
OLD = runpy.run_path(str(AREA.parent / "check.py"))
PLATFORM = runpy.run_path(str(AREA.parent / "platform-round/check.py"))
CAPTURE = runpy.run_path(str(AREA.parent / "mark2/check.py"))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def closed(obj, fields, label):
    need(type(obj) is dict and set(obj) == set(fields.split()), label + ": closed fields")


def string(value, label):
    need(type(value) is str and bool(value.strip()), label + ": nonempty string")


def strings(value, label, empty=False):
    need(type(value) is list and (empty or bool(value)), label + ": list")
    for item in value:
        string(item, label)


def rows(value, label, key="id"):
    need(type(value) is list and value, label + ": records")
    ids = [r[key] for r in value]
    need(len(ids) == len(set(ids)), label + ": duplicate identity")
    return set(ids)


def strict(raw):
    return OLD["strict_json"](raw)


def read(name):
    return strict((AREA / name).read_text(encoding="utf-8"))


def git(*args, binary=False):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, timeout=60)
    need(p.returncode == 0, "git failed: " + " ".join(args[:2]))
    return p.stdout if binary else p.stdout.decode("utf-8").strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def refs(value, allowed, label):
    strings(value, label)
    need(len(value) == len(set(value)) and set(value) <= allowed, label + ": missing/duplicate edge")


def local(ref):
    path = (ROOT / ref.split("#", 1)[0]).resolve()
    need(path.is_relative_to(ROOT) and path.is_file(), "missing/escaping local reference " + ref)
    OLD["path_ref"](ref)


def pending(obj):
    need(obj["owner_answer"] is None and obj["status"] == "pending", "invented Owner answer")


@lru_cache(maxsize=1)
def privacy_patterns():
    # Reuse the actual unchanged historical scanner definitions, including in mutants.
    tree = ast.parse((AREA.parent / "check.py").read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "publication_gate")
    assignment = next(n for n in fn.body if isinstance(n, ast.Assign) and n.targets[0].id == "patterns")
    patterns = ast.literal_eval(assignment.value)
    patterns.update({
        "private_field": r'''(?i)\b(?:account[_-]?(?:id|email)|owner[_-]message|private[_-](?:prompt|text)|infrastructure[_-]host)["']?\s*[:=]\s*["']?[^\s"',}]{3,}''',
        "private_host": r"(?i)\b[a-z0-9][a-z0-9.-]*\.(?:internal|local|lan)\b",
        "unc_path": r"\\\\[A-Za-z0-9][A-Za-z0-9.-]*\\[A-Za-z0-9]",
    })
    return patterns


def public_text(value, label):
    for kind, pattern in privacy_patterns().items():
        need(not re.search(pattern, value), "publication scan " + kind + " in " + label)


def public_artifact(raw, name):
    need(not re.search(r"\u00e2[\u0080\u20ac\u2020].|\u00c3[\u0080-\u00bf]|\ufffd", raw), "corrupt document encoding in " + name)
    public_text(raw, name)
    if name.endswith(".json"):
        # Raw-byte scanning alone misses escaped names, paths and credentials.
        def walk(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    need(key.lower().replace("-", "_") not in {
                        "account_id", "account_email", "owner_message", "private_prompt",
                        "private_text", "infrastructure_host"}, "forbidden private provenance field")
                    public_text(key, name)
                    walk(item)
            elif isinstance(value, list):
                for item in value: walk(item)
            elif isinstance(value, str): public_text(value, name)
        walk(strict(raw))


def public_url(url):
    parsed = urlsplit(url)
    need(parsed.scheme == "https" and parsed.hostname in PUBLIC_HOSTS and not any(
        [parsed.username, parsed.password, parsed.query, parsed.fragment, parsed.port]), "public primary URL form")
    public_text(url, "source URL")


def public_query(query):
    public_text(query, "public query")
    need(not re.search(r"(?i)\b(?:recursion|owner|goal[-_]spec)\b|[0-9a-f]{40}", query), "private research context in query")


def data_gate(ev, matrix, trials, decisions):
    closed(ev, "schema_version campaign sources claims packets corrections gaps observations thoughts repository_records searches limitations", "evidence")
    closed(matrix, "schema_version campaign retrieved_utc status feature_inventory launch_critical_names entries observed_runs", "matrix")
    closed(trials, "schema_version status hard_floors priorities scenarios resource_profiles trials results_available", "trials")
    closed(decisions, "schema_version status decisions not_owner_questions", "decisions")
    for obj in (ev, matrix, trials, decisions):
        need(type(obj["schema_version"]) is int and obj["schema_version"] == 1, "schema version")
    need(ev["campaign"] == matrix["campaign"] == CAMPAIGN, "campaign identity")
    sources = rows(ev["sources"], "sources")
    need([s["id"] for s in ev["sources"]] == [f"SRC-V3-{n:03}" for n in range(144, 224)], "frozen source inventory")
    rows(ev["sources"], "source keys", "key")
    for s in ev["sources"]:
        closed(s, "id key title publisher url version retrieved_utc locator status content_sha256 digest_basis applicability_limit contradiction revalidation_trigger freshness", "source")
        for key in set(s) - {"content_sha256", "freshness"}:
            string(s[key], "source " + key)
        need(s["status"] == "source-documented" and s["retrieved_utc"] == "2026-09-07", "source evidence boundary")
        need(s["url"].startswith("https://") and HEX64.fullmatch(s["content_sha256"]), "source URL/digest")
        need(s["digest_basis"] in {"raw-response-bytes", "gzip-decoded-response-bytes"}, "source digest representation")
        public_url(s["url"])
        closed(s["freshness"], "as_of valid_until expiry_basis", "source freshness")
        need(s["freshness"]["as_of"] == s["retrieved_utc"] and s["freshness"]["valid_until"] is None, "invented validity window")
        string(s["freshness"]["expiry_basis"], "expiry basis")
    claims = rows(ev["claims"], "claims")
    need(claims == {f"MKR-{n:03}" for n in range(1, 25)}, "claim inventory")
    experiments = {"experiment.mark2." + f for f in FAMILIES}
    for c in ev["claims"]:
        closed(c, "id statement status packet source_ids canonical_path applicability_limit contradictory_evidence next_test decisive_test owner_answer confidence", "claim")
        for key in ("statement", "applicability_limit", "contradictory_evidence", "decisive_test"):
            string(c[key], "claim " + key)
        need(c["status"] in STATUSES - {"locally-observed"}, "unsupported claim promotion")
        need(c["owner_answer"] is None and c["packet"] in PACKETS, "claim authority/packet")
        need(c["next_test"] in experiments, "claim decisive experiment")
        refs(c["source_ids"], sources, "claim sources")
        local(c["canonical_path"])
        need(c["canonical_path"] in ALLOWED, "claim outside canonical allowlist")
        closed(c["confidence"], "level basis runtime_support", "claim confidence")
        need(c["confidence"]["level"] == {"source-documented":"bounded-primary-source", "inferred":"conditional-inference", "proposed":"untested-proposal"}[c["status"]], "confidence/classification drift")
        need(c["confidence"]["runtime_support"] == "unproven", "confidence promoted to runtime support")
        string(c["confidence"]["basis"], "confidence basis")
    need(rows(ev["packets"], "packets") == {"mark2.packet." + x for x in PACKETS}, "six packets")
    for p in ev["packets"]:
        closed(p, "id route status finding remaining claim_ids worker_writes work_packet", "packet")
        for key in ("route", "finding", "remaining"):
            string(p[key], "packet " + key)
        need(p["status"] == "discovery-complete" and p["worker_writes"] is False, "discovery evidence boundary")
        refs(p["claim_ids"], claims, "packet claims")
        need(set(p["claim_ids"]) == {c["id"] for c in ev["claims"] if c["packet"] == p["id"].split(".")[-1]}, "packet/claim reciprocal edges")
        w = p["work_packet"]
        closed(w, "goal parent plan_revision task dependencies input_manifest start_commit read_only maximum_minutes token_cap token_cap_basis privacy tools non_goals falsifier stop_conditions", "WorkPacket")
        need(w["goal"] == CAMPAIGN and w["parent"] == "goal-recursion-v2-execution-fabric" and w["task"] == p["id"], "WorkPacket identity")
        need(type(w["plan_revision"]) is int and w["plan_revision"] == 1 and w["start_commit"] == START, "WorkPacket frozen plan")
        need(w["input_manifest"] == PREFIX + "manifest.json" and w["read_only"] is True, "WorkPacket inputs/ownership")
        need(type(w["maximum_minutes"]) is int and w["maximum_minutes"] == 30 and w["token_cap"] is None, "WorkPacket budget")
        for key in ("token_cap_basis", "privacy", "falsifier"): string(w[key], "WorkPacket " + key)
        for key in ("dependencies", "tools", "non_goals", "stop_conditions"): strings(w[key], "WorkPacket " + key)
    rows(ev["corrections"], "corrections")
    for c in ev["corrections"]:
        closed(c, "id earlier current source_ids disposition", "correction")
        string(c["earlier"], "correction earlier"); string(c["current"], "correction current")
        refs(c["source_ids"], sources, "correction sources")
        need(c["disposition"] == "supersede-interpretation-preserve-historical-evidence", "historical preservation")
    rows(ev["gaps"], "gaps")
    for g in ev["gaps"]:
        closed(g, "id question impact next_test disposition", "gap")
        string(g["question"], "gap"); string(g["impact"], "gap impact")
        need(g["next_test"] in experiments and g["disposition"] == "unproven-not-campaign-blocker", "gap disposition")
    need(rows(ev["observations"], "observations") == {"observation.mark2.baseline", "observation.mark2.sources"}, "observation inventory")
    for o in ev["observations"]:
        closed(o, "id status scope result", "observation")
        need(o["status"] == "locally-observed", "observation status")
        string(o["scope"], "observation scope"); string(o["result"], "observation result")

    directions = strict((AREA.parent / "mark2/directions.json").read_text(encoding="utf-8"))
    old_thoughts = OLD["read"]("evidence.json")["thoughts"]
    thought_ids = rows(ev["thoughts"], "thoughts")
    need(thought_ids == {"thought.mark2.q" + str(n) for n in range(1, 11)} | {
        "thought.mark2.legacy." + t["id"][8:] for t in old_thoughts}, "complete current and historical thought inventory")
    for t in ev["thoughts"]:
        closed(t, "id prior_thought_id question idea_refs ruling_ids classification disposition finding claim_ids contract_links next_test falsifier", "thought")
        for key in ("finding", "falsifier"): string(t[key], "thought " + key)
        refs(t["claim_ids"], claims, "thought claims")
        refs(t["ruling_ids"], {f"OR-{n:03}" for n in range(21, 36)}, "thought rulings")
        strings(t["contract_links"], "thought contracts")
        for path in t["contract_links"]: local(path)
        need(t["next_test"] in experiments, "thought experiment")
        if t["question"] is not None:
            need(type(t["question"]) is int and 1 <= t["question"] <= 10, "thought question")
            a = directions["answers"][t["question"] - 1]
            need(t["id"] == "thought.mark2.q" + str(a["question"]) and t["prior_thought_id"] is None, "question binding")
            need(t["ruling_ids"] == [a["ruling"]], "answer ruling binding")
            need(t["idea_refs"] == [f"Q{a['question']}.{key}.{n}" for key in (
                "accepted", "selected_defaults", "research_not_selected", "compatibility_obligations")
                for n in range(1, len(a[key]) + 1)], "every substantive answer sub-item")
            need(t["classification"] == "Owner-direction-with-proposed-realization" and t["disposition"] == "direction-preserved-realization-unproven", "reopened answer")
        else:
            need(t["prior_thought_id"] in {x["id"] for x in old_thoughts} and t["idea_refs"] == [], "historical thought binding")
            need(t["id"] == "thought.mark2.legacy." + t["prior_thought_id"][8:], "historical thought identity")
            need(t["classification"] == "historical-evidence-under-current-Owner-direction" and t["disposition"] == "reconciled-historical-record-preserved", "historical authority")
    need(rows(ev["repository_records"], "repository records") == {"repository.mark2." + s for s in ("authority", "model", "interaction", "roadmap")}, "repository coverage")
    for r in ev["repository_records"]:
        closed(r, "id classification path finding", "repository record")
        need(r["classification"] == "verified-repository-fact", "repository classification")
        local(r["path"]); string(r["finding"], "repository finding")
    need(rows(ev["searches"], "searches") == {"search.mark2.packet." + p for p in PACKETS} | {"search.mark2.audit." + str(n) for n in range(1, 4)}, "search inventory")
    for s in ev["searches"]:
        closed(s, "id method query scope source_ids opened_primary stopping_reason provenance_limit", "search")
        refs(s["source_ids"], sources, "search evidence")
        need(s["opened_primary"] is True, "snippet promoted to evidence")
        for k in ("scope", "stopping_reason", "provenance_limit"): string(s[k], "search " + k)
        if s["method"] == "exact-public-query-plus-primary-open":
            string(s["query"], "public query"); public_query(s["query"])
        else:
            need(s["method"] == "reconstructed-primary-followup-summary" and s["query"] is None, "fabricated search transcript")
    strings(ev["limitations"], "research limitations")
    need(matrix["status"] == "source-verified-not-integration-certified" and matrix["observed_runs"] == [], "forged matrix observation")
    need(matrix["retrieved_utc"] == "2026-09-07" and matrix["feature_inventory"] == FEATURES, "matrix date/features")
    need(matrix["launch_critical_names"] == directions["launch_critical_names"], "critical names")
    need([e["requested_name"] for e in matrix["entries"]] == directions["requested_integrations"], "13 requested entries")
    rows(matrix["entries"], "entries", "requested_name")
    allpaths = []
    for e in matrix["entries"]:
        closed(e, "requested_name launch_critical_name identity_status paths features role_closure installation applicability_limits next_test observed_runs", "entry")
        need(e["launch_critical_name"] is None or e["launch_critical_name"] in matrix["launch_critical_names"], "critical binding")
        need(e["identity_status"] in {"resolved-category", "resolved-product"}, "identity resolution")
        need(e["observed_runs"] == [] and e["next_test"] == "experiment.mark2.integration", "entry observation/test")
        string(e["role_closure"], "role closure"); string(e["installation"], "install boundary")
        strings(e["applicability_limits"], "entry limits")
        paths = rows(e["paths"], "paths"); allpaths += list(paths)
        for p in e["paths"]:
            closed(p, "id provider executing_harness supported_interface authentication billing_source host version intended_distribution source_ids tested_build", "path")
            for key in set(p) - {"source_ids", "tested_build"}:
                string(p[key], "path " + key)
            refs(p["source_ids"], sources, "path sources")
            need(p["tested_build"] is None, "forged tested build")
        closed(e["features"], " ".join(FEATURES), "ten controls")
        for c in e["features"].values():
            closed(c, "status detail source_ids path_ids conformance", "feature")
            need(c["status"] in {"source-documented", "inferred", "unknown", "unsupported"} and c["conformance"] == "unproven", "feature evidence promotion")
            string(c["detail"], "feature meaning/limit")
            refs(c["source_ids"], sources, "feature sources")
            refs(c["path_ids"], paths, "feature path")
    need(len(allpaths) == len(set(allpaths)) == 23, "path inventory")
    need({e["launch_critical_name"] for e in matrix["entries"] if e["launch_critical_name"]} == set(matrix["launch_critical_names"]), "critical coverage")

    need(trials["status"] == "preregistered-unrun" and trials["results_available"] is False, "forged trial result")
    need(trials["hard_floors"] == ["correctness", "authorization", "privacy", "resource_limits", "recoverability"], "hard floors")
    need(trials["priorities"] == ["responsiveness", "subscription_efficiency", "completion"], "Owner ranking")
    scenarios = rows(trials["scenarios"], "scenarios")
    need(scenarios == {"website", "bug_fix", "interrupted_refactor", "upstream_only", "research_workflow"}, "scenarios")
    for s in trials["scenarios"]:
        closed(s, "id task success fault", "scenario")
        for value in s.values(): string(value, "scenario field")
    need(rows(trials["trials"], "experiments") == experiments and len(trials["trials"]) == 8, "eight experiment families")
    for n, t in enumerate(trials["trials"]):
        closed(t, "id supersedes_design status question baseline treatments scenarios unit workload version_freeze matched_budget metrics faults analysis stop_rule adoption_rule required_authorization run_plan contract_links result", "trial")
        need(t["id"] == "experiment.mark2." + FAMILIES[n], "family order")
        need(t["supersedes_design"] == ("trial." + FAMILIES[n] if n < 6 else None), "preserved six family mappings")
        need(t["status"] == "preregistered-unrun" and t["result"] is None, "trial observation boundary")
        for k in ("question", "baseline", "unit", "matched_budget", "analysis", "stop_rule", "adoption_rule", "required_authorization"):
            string(t[k], "trial " + k)
        for k in ("treatments", "workload", "version_freeze", "metrics", "faults", "contract_links"):
            strings(t[k], "trial " + k)
        refs(t["scenarios"], scenarios, "trial scenario")
        for ref in t["contract_links"]: local(ref)
        plan = t["run_plan"]
        closed(plan, "maximum_minutes maximum_concurrent_cases new_metered_spend actual_hosts eligible_routes included_capacity_lease human_review_minutes deadline_utc preconditions cleanup", "run plan")
        need(type(plan["maximum_minutes"]) is int and 0 < plan["maximum_minutes"] <= 90, "bounded future run")
        need(plan["maximum_concurrent_cases"] == 2 and type(plan["maximum_concurrent_cases"]) is int, "future concurrency")
        need(type(plan["new_metered_spend"]) is int and plan["new_metered_spend"] == 0, "unapproved spend")
        need(all(plan[k] is None for k in ("actual_hosts", "eligible_routes", "included_capacity_lease", "human_review_minutes", "deadline_utc")), "unrun resource-dependent packet")
        strings(plan["preconditions"], "run preconditions"); string(plan["cleanup"], "cleanup")
    need(rows(trials["resource_profiles"], "resource profiles") == {"controller-design", "worker-design"}, "resource profiles")
    for p in trials["resource_profiles"]:
        closed(p, "id status guaranteed_vcpu maximum_vcpu guaranteed_ram_gib maximum_ram_gib free_disk_gib active_engines purpose", "resource profile")
        need(p["status"] == "unmeasured-experiment-profile-not-product-minimum", "fabricated resource minimum")
        for k in ("guaranteed_vcpu", "maximum_vcpu", "guaranteed_ram_gib", "maximum_ram_gib", "free_disk_gib", "active_engines"):
            need(type(p[k]) is int and p[k] >= 0, "resource bound type")
        need(0 < p["guaranteed_vcpu"] <= p["maximum_vcpu"] and 0 < p["guaranteed_ram_gib"] <= p["maximum_ram_gib"], "resource floor/ceiling")
        string(p["purpose"], "resource purpose")

    need(decisions["status"] == "pending-owner-answers", "decision scope")
    need(rows(decisions["decisions"], "decisions") == {"decision.mark2.proof-boundary", "decision.mark2.delegated-amendments"}, "consequential decision inventory")
    strings(decisions["not_owner_questions"], "closed Owner questions")
    for d in decisions["decisions"]:
        closed(d, "id question why_consequential options recommendation reason source_ids claim_ids next_test owner_answer status classification affected_contracts fixture_implications dependency falsifier", "decision")
        pending(d)
        need(d["classification"] == "proposed-owner-decision", "unclassified recommendation")
        strings(d["affected_contracts"], "affected decision contracts")
        for path in d["affected_contracts"]:
            need(path in ALLOWED, "decision contract scope"); local(path)
        for key in ("fixture_implications", "dependency", "falsifier"): string(d[key], "decision " + key)
        for k in ("question", "why_consequential", "reason"): string(d[k], "decision " + k)
        opts = rows(d["options"], "options")
        need(2 <= len(opts) <= 3 and d["recommendation"] in opts, "reviewable options")
        for option in d["options"]:
            closed(option, "id label tradeoff", "option")
            for value in option.values(): string(value, "option")
        refs(d["source_ids"], sources, "decision sources"); refs(d["claim_ids"], claims, "decision claims")
        need(d["next_test"] in experiments, "decision test")
    return sources, claims


def bindings(ev):
    source_text = (ROOT / "docs/v3/SOURCE-REGISTER.md").read_text(encoding="utf-8")
    sr = re.findall(r"^\| `(SRC-V3-\d{3})` \| ([^|]*)\|", source_text, re.M)
    need([r[0] for r in sr] == [f"SRC-V3-{n:03}" for n in range(1, 224)], "canonical source sequence")
    smap = {key: re.findall(r"\[[^\]]*\]\((https://[^)]+)\)", cell) for key, cell in sr}
    for s in ev["sources"]:
        need(s["url"] in smap[s["id"]], "source ID/URL binding drift")
    ledger = (ROOT / "docs/v3/CLAIM-LEDGER.md").read_text(encoding="utf-8")
    registered = OLD["registry_shape"](strict((ROOT / "docs/v3/CLAIM-REGISTRY.json").read_text(encoding="utf-8")), ledger)
    cm = dict(re.findall(r"^\| (MKR-\d{3}) \| ([^|]*)\|", ledger, re.M))
    for c in ev["claims"]:
        need(cm.get(c["id"], "").strip() == c["statement"], "claim ID/statement binding drift")
    owner = (ROOT / "docs/v3/DECISION-REGISTER.md").read_text(encoding="utf-8")
    for n in range(21, 36):
        need(owner.count(f"| OR-{n:03} |") == 1, "Owner ruling uniqueness")
    owner_ids = set(re.findall(r"^\| (OR-\d{3}) \|", owner, re.M))
    registry = strict((ROOT / "docs/v3/CLAIM-REGISTRY.json").read_text(encoding="utf-8"))
    for p in (ROOT / "docs/v3").rglob("*"):
        if p.suffix not in {".md", ".json"} or "archive" in p.relative_to(ROOT / "docs/v3").parts:
            continue
        text = p.read_text(encoding="utf-8")
        for match in re.finditer(registry["referencePattern"], text):
            v = match[1]
            need(v in registered or v in owner_ids or v == "SHA-256" or re.fullmatch("H-[0-9]{3}", v), "unregistered claim " + v + " in " + p.name)
        need(set(re.findall(r"SRC-V3-\d{3}", text)) <= set(smap), "unregistered source")
    return set(smap), registered


def recovery_admitted(normal, numerator, denominator, committed, reserved, request):
    # A documentation arithmetic oracle on declared integer counter quanta, not a runtime ledger.
    if normal is None:
        return False
    values = (normal, numerator, denominator, committed, reserved, request)
    need(all(type(v) is int for v in values), "integer recovery arithmetic")
    need(all(v >= 0 for v in values) and denominator > 0, "recovery arithmetic domain")
    return committed + reserved + request <= normal * numerator // denominator


def arithmetic_gate(inventory):
    rows(inventory["recovery_cases"], "recovery fixtures")
    for c in inventory["recovery_cases"]:
        closed(c, "id status normal numerator denominator committed reserved request expected", "recovery fixture")
        need(c["status"] == "synthetic-documentation-arithmetic" and type(c["expected"]) is bool, "arithmetic evidence boundary")
        actual = recovery_admitted(*(c[k] for k in ("normal", "numerator", "denominator", "committed", "reserved", "request")))
        need(actual is c["expected"], "recovery fixture mismatch " + c["id"])
    # Unit vectors must all pass; there is no implicit currency or token/quota conversion.
    need(not all([recovery_admitted(100000, 1, 10, 9000, 1000, 1),
                  recovery_admitted(10000, 1, 10, 0, 0, 100)]), "componentwise cap")
    # Shared-pool reservations are additional to per-scope caps.
    need(sum([4000, 5000, 2000]) > 10000, "shared pool over-reservation fixture")
    return len(inventory["recovery_cases"]) + 2


def adversarial(ev, matrix, trials, decisions, inventory):
    rejected = []
    def reject(fn, label):
        try: fn()
        except (ValueError, KeyError, TypeError):
            rejected.append(label); return
        raise ValueError("accepted mutant: " + label)
    reject(lambda: strict('{"a":1,"a":2}'), "duplicate JSON")
    reject(lambda: strict('{"a":NaN}'), "nonfinite JSON")
    cases = []
    for index, key, value, label in [
        (0, "schema_version", True, "boolean schema"),
        (1, "observed_runs", ["synthetic pass"], "false integration observation"),
        (2, "priorities", ["completion", "responsiveness", "subscription_efficiency"], "ranking drift"),
        (2, "results_available", True, "invented trial result")]:
        data = copy.deepcopy([ev, matrix, trials, decisions]); data[index][key] = value; cases.append((data, label))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["claims"][0]["source_ids"] = []; cases.append((data, "unsupported conclusion"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["claims"][0]["contradictory_evidence"] = ""; cases.append((data, "omitted contradiction"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["sources"][0]["revalidation_trigger"] = ""; cases.append((data, "missing source revalidation"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["sources"][0]["freshness"]["valid_until"] = "forever"; cases.append((data, "invented validity window"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["claims"][0]["confidence"]["runtime_support"] = "passed"; cases.append((data, "confidence promotion"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["thoughts"].pop(); cases.append((data, "omitted historical thought"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["thoughts"][0]["idea_refs"].pop(); cases.append((data, "omitted Owner idea"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["searches"][0]["query"] = "unretained"; cases.append((data, "fabricated query transcript"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["searches"][0]["stopping_reason"] = ""; cases.append((data, "missing search stop"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[0]["packets"].pop(); cases.append((data, "missing packet"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[1]["entries"].pop(); cases.append((data, "missing integration"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[1]["entries"][0]["features"].pop("active_steering"); cases.append((data, "missing control"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[1]["entries"][0]["features"]["streaming"]["conformance"] = "passed"; cases.append((data, "source promoted to support"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[1]["entries"][0]["features"]["streaming"]["path_ids"] = ["other"]; cases.append((data, "feature misbound path"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[1]["entries"][0]["paths"][0]["tested_build"] = START; cases.append((data, "forged binary observation"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[2]["trials"].append(copy.deepcopy(data[2]["trials"][0])); cases.append((data, "ninth family"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[2]["trials"][0]["run_plan"]["new_metered_spend"] = 1; cases.append((data, "spend expansion"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[2]["trials"][0]["result"] = {}; cases.append((data, "synthetic result promotion"))
    data = copy.deepcopy([ev, matrix, trials, decisions]); data[3]["decisions"][0]["owner_answer"] = "approved"; cases.append((data, "invented Owner decision"))
    for data, label in cases: reject(lambda d=data: data_gate(*d), label)
    x = copy.deepcopy(ev); x["sources"][0]["url"], x["sources"][1]["url"] = x["sources"][1]["url"], x["sources"][0]["url"]
    reject(lambda: bindings(x), "source URL reassignment")
    x = copy.deepcopy(ev); x["claims"][0]["statement"] = "Different assertion."
    reject(lambda: bindings(x), "claim reassignment")
    x = copy.deepcopy(inventory); x["recovery_cases"][0]["expected"] = not x["recovery_cases"][0]["expected"]
    reject(lambda: arithmetic_gate(x), "recovery expected result drift")
    reject(lambda: recovery_admitted(100, True, 10, 0, 0, 1), "boolean recovery fraction")
    reject(lambda: recovery_admitted(100, 1, 0, 0, 0, 1), "zero denominator")
    # Synthetic values are assembled to avoid placing credential-shaped literals in files.
    privacy_values = [
        ("sk-" + "A" * 24, "token"),
        ("ghp_" + "A" * 24, "repository token"),
        ("Bearer " + "A" * 24, "bearer"),
        ("C:" + chr(92) + "Users" + chr(92) + "synthetic-person", "home path"),
        ("10." + "23.45.67", "private network"),
        ("host" + ".internal", "private hostname"),
        ("account_id" + "=synthetic-account-123", "private account"),
        ("private_prompt" + "=synthetic-private-text", "private prompt"),
        ("https://" + "user:password@example.com", "credential URL"),
    ]
    for value, label in privacy_values:
        reject(lambda v=value: public_artifact(v, "synthetic.md"), "privacy " + label)
        # Exercise decoded JSON scanning even if every ASCII character was escaped.
        encoded = "".join("\\u%04x" % ord(c) for c in value)
        reject(lambda e=encoded: public_artifact('{"note":"' + e + '"}', "synthetic.json"), "escaped privacy " + label)
    reject(lambda: public_artifact(json.dumps(dict([("owner_message", "synthetic")])), "synthetic.json"), "private provenance field")
    reject(lambda: public_url("https://example.com/reference"), "unregistered primary host")
    reject(lambda: public_url(ev["sources"][0]["url"] + "?private=value"), "source query leakage")
    reject(lambda: public_query("Recursion private task"), "private research query")
    reject(lambda: public_artifact(chr(8212).encode("utf-8").decode("cp1252"), "synthetic.md"), "corrupt UTF-8 punctuation")
    public_artifact('{"source":"https://git-scm.com/docs/git-worktree","resource":null}', "synthetic.json")
    return len(rejected)


def historical_gate(sources, claims):
    ev, co, ex, de = [OLD["read"](n) for n in ("evidence.json", "compatibility.json", "experiments.json", "decisions.json")]
    OLD["data_gate"](ev, co, ex, de, sources, claims)
    OLD["source_bindings"](ev, (ROOT / "docs/v3/SOURCE-REGISTER.md").read_text(encoding="utf-8"))
    OLD["claim_bindings"](ev, (ROOT / "docs/v3/CLAIM-LEDGER.md").read_text(encoding="utf-8"))
    OLD["adversarial_gate"](ev, co, ex, de, sources, claims)
    prior = AREA.parent / "platform-round"
    m, t = [strict((prior / n).read_text(encoding="utf-8")) for n in ("integration.json", "trials.json")]
    PLATFORM["data_gate"](m, t)
    platform_mutants = PLATFORM["adversarial"](m, t)
    PLATFORM["document_gate"]()
    d = strict((AREA.parent / "mark2/directions.json").read_text(encoding="utf-8"))
    CAPTURE["data_gate"](d)
    capture_mutants = CAPTURE["adversarial"](d)
    return {"platform_mutants": platform_mutants, "capture_mutants": capture_mutants}


def manifest_gate(manifest, inventory, candidate, changed):
    closed(manifest, "schema_version goal parent start_commit branch ancestors started_utc deadline_utc allowed_files allowed_prefix inputs required_outputs observed_integration_runs", "manifest")
    need(type(manifest["schema_version"]) is int and manifest["schema_version"] == 1, "manifest version")
    need(manifest["goal"] == CAMPAIGN and manifest["parent"] == "goal-recursion-v2-execution-fabric", "parent goal")
    need(manifest["start_commit"] == START and manifest["branch"] == BRANCH and manifest["ancestors"] == ANCESTORS, "frozen start identity")
    need(set(manifest["allowed_files"]) == ALLOWED and len(manifest["allowed_files"]) == len(ALLOWED), "manifest allowlist")
    need(manifest["allowed_prefix"] == PREFIX and set(manifest["required_outputs"]) == FILES, "manifest artifact scope")
    need(manifest["observed_integration_runs"] == [], "manifest observation")
    start = datetime.fromisoformat(manifest["started_utc"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(manifest["deadline_utc"].replace("Z", "+00:00"))
    need((end-start).total_seconds() == 6*3600, "six-hour maximum envelope")
    rows(manifest["inputs"], "frozen inputs", "path")
    need(len(manifest["inputs"]) == 14, "input inventory")
    for item in manifest["inputs"]:
        closed(item, "path sha256", "frozen input")
        need(sha(git("show", START + ":" + item["path"], binary=True)) == item["sha256"], "frozen input bytes")
    closed(inventory, "schema_version start_commit regression_commands regression_entrypoints artifacts recovery_cases publication_policy limitations", "validation inventory")
    need(type(inventory["schema_version"]) is int and inventory["schema_version"] == 1 and inventory["start_commit"] == START, "validation inventory identity")
    commands = OLD["regression_commands"]()
    need(inventory["regression_commands"] == commands and len(commands) == 25, "unchanged full regression inventory")
    rows(inventory["regression_entrypoints"], "regression entrypoints", "path")
    expected_entries = {next(a for a in command if a.endswith(".py")) for command in commands}
    need({x["path"] for x in inventory["regression_entrypoints"]} == expected_entries, "entrypoint inventory")
    for item in inventory["regression_entrypoints"]:
        closed(item, "path sha256", "entrypoint")
        base = git("show", START + ":" + item["path"], binary=True)
        need(sha(base) == item["sha256"] and base == git("show", candidate + ":" + item["path"], binary=True), "changed regression entrypoint")
    rows(inventory["artifacts"], "artifact inventory", "path")
    need({x["path"] for x in inventory["artifacts"]} == set(changed) - {PREFIX + "validation-inventory.json"}, "artifact inventory coverage")
    for item in inventory["artifacts"]:
        closed(item, "path git_blob_sha256", "artifact")
        need(sha(git("show", candidate + ":" + item["path"], binary=True)) == item["git_blob_sha256"], "artifact digest " + item["path"])
    strings(inventory["limitations"], "validation limitations")
    policy = inventory["publication_policy"]
    closed(policy, "scope permitted_forms rejected_forms human_review_required guarantee", "publication policy")
    need(policy["scope"] == "every changed artifact; raw UTF-8 and recursively decoded JSON strings and keys", "publication scope")
    strings(policy["permitted_forms"], "permitted publication forms")
    need(set(policy["rejected_forms"]) == set(privacy_patterns()), "publication pattern inventory")
    need(policy["human_review_required"] is True and policy["guarantee"] == "known-pattern rejection only; no universal privacy certification", "privacy guarantee boundary")
    return commands


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    need(args.base == START and HEX40.fullmatch(args.candidate), "full frozen hashes")
    need(git("branch", "--show-current") == BRANCH, "branch")
    need(git("rev-parse", "HEAD") == args.candidate and not git("status", "--porcelain=v1", "--untracked-files=all"), "clean exact candidate")
    for ancestor in [START, *ANCESTORS]: git("merge-base", "--is-ancestor", ancestor, args.candidate)
    owners = [x for x in git("worktree", "list", "--porcelain").split("\n\n") if "branch refs/heads/" + BRANCH in x.splitlines()]
    need(len(owners) == 1 and Path(owners[0].splitlines()[0][9:]).resolve() == ROOT, "exclusive worktree")
    changed = git("diff", "--name-only", "--no-renames", START, args.candidate).splitlines()
    need(changed and all(p in ALLOWED or (p.startswith(PREFIX) and p[len(PREFIX):] in FILES) for p in changed), "full diff outside allowlist")
    need(not git("diff", "--name-only", "--diff-filter=D", START, args.candidate), "deleted historical artifact")
    git("diff", "--check", START, args.candidate)
    need({p.name for p in AREA.iterdir()} == FILES, "campaign closed artifact inventory")
    # The diff allowlist proves every historical gate/M1/runtime/state/control-plane file unchanged.
    manifest, inventory = read("manifest.json"), read("validation-inventory.json")
    commands = manifest_gate(manifest, inventory, args.candidate, changed)
    ev, matrix, trials, decisions = [read(n) for n in ("evidence.json", "compatibility.json", "experiments.json", "decisions.json")]
    data_gate(ev, matrix, trials, decisions)
    sources, claims = bindings(ev)
    historical = historical_gate(sources, claims)
    arithmetic = arithmetic_gate(inventory)
    mutants = adversarial(ev, matrix, trials, decisions, inventory)
    OLD["publication_gate"](changed)
    for name in changed:
        public_artifact((ROOT / name).read_text(encoding="utf-8"), name)
    for name in changed:
        if not name.endswith(".md"): continue
        p = ROOT / name
        prose = re.sub(r"(?ms)^\x60\x60\x60.*?^\x60\x60\x60[ \t]*\r?$", "", p.read_text(encoding="utf-8"))
        for ref in re.findall(r"\[[^\]]*\]\(([^)]+)\)", prose):
            ref = ref.strip().strip("<>")
            if re.match(r"^(https?|mailto|data):", ref): continue
            target = (p.parent / ref.split("#", 1)[0]).resolve()
            need(target.is_relative_to(ROOT), "escaping local link")
            OLD["path_ref"](ref, p if ref.startswith("#") else p.parent)
    terminal = (ROOT / "docs/v3/TERMINAL-RUNTIME.md").read_text(encoding="utf-8")
    for feature in FEATURES: need("| " + feature + " |" in terminal, "canonical control table")
    architecture = (ROOT / "docs/v3/ARCHITECTURE.md").read_text(encoding="utf-8")
    directions = strict((AREA.parent / "mark2/directions.json").read_text(encoding="utf-8"))
    for mode in directions["modes"]["software_update"]: need("| " + mode + " |" in architecture, "canonical six update modes")
    # Durable receipts stay in Git metadata, outside the reviewed candidate and publication.
    common = Path(git("rev-parse", "--git-common-dir"))
    if not common.is_absolute(): common = (ROOT / common).resolve()
    out = common / "research-attestations" / "mark2" / args.candidate
    out.mkdir(parents=True, exist_ok=True)
    runid = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + str(time.time_ns())[-6:]
    receipts = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    if os.name == "nt":
        bash_dir = Path(os.environ.get("ProgramFiles", "")) / "Git/bin"
        if (bash_dir / "bash.exe").is_file(): env["PATH"] = str(bash_dir) + os.pathsep + env.get("PATH", "")
    for index, command in enumerate(commands):
        before = time.monotonic()
        result = subprocess.run([sys.executable, *command[1:]], cwd=ROOT, env=env, capture_output=True, timeout=240)
        output = result.stdout + result.stderr
        (out / f"{runid}-{index:02}.log").write_bytes(output)
        row = {"command":command, "exit_code":result.returncode, "seconds":round(time.monotonic()-before, 3), "output_sha256":sha(output)}
        receipts.append(row)
        print(json.dumps(row), flush=True)
        need(result.returncode == 0, "regression failed: " + " ".join(command))
    need(git("rev-parse", "HEAD") == args.candidate and not git("status", "--porcelain=v1", "--untracked-files=all"), "candidate changed during gate")
    receipt = {"base":START, "candidate":args.candidate, "run_id":runid, "source_count":80, "claim_count":24,
               "entries":13, "paths":23, "feature_cells":130, "experiment_families":8,
               "adversarial":mutants, "arithmetic_cases":arithmetic, "historical":historical,
               "thoughts":len(ev["thoughts"]), "searches":len(ev["searches"]),
               "publication_artifacts_scanned":len(changed), "privacy_certified":False,
               "artifacts":{p:sha(git("show",args.candidate+":"+p,binary=True)) for p in changed},
               "regressions":receipts, "runtime_integration_observed":False}
    raw = json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8")
    (out / (runid + ".json")).write_bytes(raw + b"\n")
    print("MARK2_RESEARCH_GATE_PASS " + json.dumps({"candidate":args.candidate, "regressions":len(receipts), "adversarial":mutants, "receipt_sha256":sha(raw), "run_id":runid}), flush=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as error:
        print("MARK2_RESEARCH_GATE_FAIL " + str(error), file=sys.stderr)
        sys.exit(1)
