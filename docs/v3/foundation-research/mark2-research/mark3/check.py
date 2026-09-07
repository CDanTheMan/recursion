"""Exact-candidate Mark 3 documentation gate; no provider or product experiments."""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import time
from urllib.parse import urlsplit

AREA = Path(__file__).resolve().parent
ROOT = AREA.parents[4]
START = "ec9c3d1632193e8509e7baf41fa8810165f93c05"
BRANCH = "codex/v3-formal-model-experiment"
PREFIX = "docs/v3/foundation-research/mark2-research/mark3/"
DOCS = "ACCEPTANCE ARCHITECTURE CLAIM-LEDGER CLI CONSTRUCTION-RUNBOOK CONTEXT DECISION-REGISTER EXECUTION-FABRIC EXECUTIVES INTERACTION-SURFACES PERFORMANCE-PLAN PLANNING PLUGINS-AND-EDITIONS PRODUCT README ROADMAP ROUTE-CAPABILITIES SOURCE-REGISTER TELEMETRY TERMINAL-RUNTIME".split()
FILES = set("campaign.md handoff.md owner-answers.md directions.json research-plan.json companion-review.json check.py validation-inventory.json".split())
ALLOWED = {"docs/v3/" + n + ".md" for n in DOCS} | {PREFIX + n for n in FILES}
M = runpy.run_path(str(AREA.parent / "check.py"))
OLD = M["OLD"]
need, closed, strings, rows, refs = [M[n] for n in ("need", "closed", "strings", "rows", "refs")]
git, sha, strict, local = [M[n] for n in ("git", "sha", "strict", "local")]
FAMILIES = M["FAMILIES"]
COMPANION = "e20b5450aeba977d99ad6bb196a43521f739d9c8b5dfe8d3c9f5d89079d576d5"
AREAS = "system cache configuration compatibility communication cli autonomy orchestration headless plugins mcp interactions".split()
CASES = "revision-cache-consultation terminal-stop-remote upstream-helper-scarcity plugin-browser-update checkpoint-replay-pressure inactive-activation".split()


def read(name):
    return strict((AREA / name).read_text(encoding="utf-8"))


def text(ref):
    return (ROOT / ref).read_text(encoding="utf-8")


def nonempty(obj, names):
    for name in names.split(): M["string"](obj[name], name)


def bindings(ev):
    """Extend source/Owner identities without rewriting historical gate code or evidence."""
    sr = re.findall(r"^\| `(SRC-V3-\d{3})` \| ([^|]*)\|", text("docs/v3/SOURCE-REGISTER.md"), re.M)
    need([r[0] for r in sr] == [f"SRC-V3-{n:03}" for n in range(1, 229)], "canonical source sequence")
    smap = {key: re.findall(r"\[[^\]]*\]\((https://[^)]+)\)", cell) for key, cell in sr}
    for source in ev["sources"]: need(source["url"] in smap[source["id"]], "source ID/URL drift")
    ledger = text("docs/v3/CLAIM-LEDGER.md")
    registry = strict(text("docs/v3/CLAIM-REGISTRY.json"))
    registered = OLD["registry_shape"](registry, ledger)
    claims = dict(re.findall(r"^\| (MKR-\d{3}) \| ([^|]*)\|", ledger, re.M))
    for claim in ev["claims"]:
        need(claims.get(claim["id"], "").strip() == claim["statement"], "claim statement drift")
    owner = text("docs/v3/DECISION-REGISTER.md")
    for n in range(1, 40): need(owner.count(f"| OR-{n:03} |") == 1, "Owner ruling uniqueness")
    owner_ids = set(re.findall(r"^\| (OR-\d{3}) \|", owner, re.M))
    for p in (ROOT / "docs/v3").rglob("*"):
        if p.suffix not in {".md", ".json"} or "archive" in p.relative_to(ROOT / "docs/v3").parts: continue
        prose = p.read_text(encoding="utf-8")
        for match in re.finditer(registry["referencePattern"], prose):
            v = match[1]
            need(v in registered or v in owner_ids or v == "SHA-256" or re.fullmatch("H-[0-9]{3}", v), "unregistered claim " + v)
        need(set(re.findall(r"SRC-V3-\d{3}", prose)) <= set(smap), "unregistered source")
    return set(smap), registered


def direction_gate(d, inventory):
    closed(d, "schema_version kind answered_date research_candidate parent_goal status source decisions rulings preserved companion observations", "directions")
    need(type(d["schema_version"]) is int and d["schema_version"] == 1, "schema")
    need(d["kind"] == "owner-answer-integration-not-runtime-evidence" and d["answered_date"] == "2026-09-07", "direction provenance")
    need(d["research_candidate"] == START and d["parent_goal"] == M["CAMPAIGN"], "parent/start")
    need(d["status"] == "both-owner-decisions-approved", "accepted answers")
    closed(d["source"], "record basis quotes", "Owner source")
    need(d["source"]["record"] == PREFIX + "owner-answers.md", "Owner record")
    nonempty(d["source"], "basis")
    quotes = d["source"]["quotes"]
    qids = rows(quotes, "quotes")
    need(len(quotes) == 11 and qids == set(inventory["quote_digests"]), "complete exact passages")
    captured = text(d["source"]["record"])
    for q in quotes:
        closed(q, "id classification text", "quote")
        nonempty(q, "classification text")
        need(sha(q["text"].encode("utf-8")) == inventory["quote_digests"][q["id"]], "quote digest")
        marker = "### " + q["id"]
        need(captured.count(marker) == 1, "quote identity")
        section = captured.split(marker, 1)[1].split("\n### ", 1)[0]
        need("```text\n" + q["text"] + "\n```" in section and q["classification"] in section, "exact quote/classification binding")
    qmap = {q["id"]: q for q in quotes}
    need(qmap["quote.mark3.proposed-extension"]["classification"] == "editorial-compilation-not-verbatim-approved", "editorial approval promotion")
    need(qmap["quote.mark3.foundation"]["classification"] == "verbatim-owner-approved-foundation", "foundation classification")
    need(qmap["quote.mark3.foundation"]["text"] in text("docs/v3/PRODUCT.md"), "accepted foundation wording")
    need([x["id"] for x in d["decisions"]] == ["decision.mark2.proof-boundary", "decision.mark2.delegated-amendments"], "decision inventory")
    for i, x in enumerate(d["decisions"]):
        closed(x, "id selected_option status ruling approval_ref recommendation_ref qualifications next_test technical_completion", "decision")
        need(x["selected_option"] == ["aggregate-refinement", "owner-amendments"][i], "approved option")
        need(x["status"] == "accepted-owner-direction" and x["technical_completion"] is False, "authority/evidence boundary")
        need(x["ruling"] == f"OR-{36+i:03}" and x["approval_ref"] == "quote.mark3.approval", "decision provenance")
        need(x["recommendation_ref"] == ["quote.mark3.model-recommendation", "quote.mark3.delegation-recommendation"][i], "recommendation binding")
        strings(x["qualifications"], "qualifications")
        need(len(x["qualifications"]) == [4, 5][i], "complete qualifications")
        need(x["next_test"] == ["experiment.mark2.simulation", "experiment.mark2.assistants"][i], "decisive test")
    need([r["id"] for r in d["rulings"]] == [f"OR-{n:03}" for n in range(36, 40)], "ruling inventory")
    canonical = text("docs/v3/DECISION-REGISTER.md")
    for r in d["rulings"]:
        closed(r, "id classification summary quote_refs canonical_paths", "ruling")
        need(r["classification"] == "accepted-owner-direction", "ruling classification")
        refs(r["quote_refs"], qids, "ruling provenance")
        refs(r["canonical_paths"], ALLOWED, "ruling canonical paths")
        need("| " + r["id"] + " | " + r["summary"] + " |" in canonical, "canonical ruling binding")
        for path in r["canonical_paths"]: local(path)
    p = d["preserved"]
    closed(p, "mark2_answers critical_names execution_modes priorities hard_floors ordinary_runtime_requires_continuous_inference goal_spec_amendments_delegated m1_changed common_writer_migration_resolved language_selected store_selected framework_selected personal_inventory_required", "preserved requirements")
    need(type(p["mark2_answers"]) is int and p["mark2_answers"] == 10, "ten answers")
    old_d = M["CAPTURE"]["read"]("directions.json") if "read" in M["CAPTURE"] else strict(text("docs/v3/foundation-research/mark2/directions.json"))
    need(p["critical_names"] == old_d["launch_critical_names"], "critical names")
    need(p["execution_modes"] == ["native", "upstream-only", "combined"], "execution paths")
    need(p["priorities"] == ["responsiveness", "subscription_efficiency", "completion"], "ranking")
    need(p["hard_floors"] == ["correctness", "authorization", "privacy", "resource_limits", "recoverability"], "hard floors")
    for key in "ordinary_runtime_requires_continuous_inference goal_spec_amendments_delegated m1_changed common_writer_migration_resolved personal_inventory_required".split(): need(p[key] is False, key)
    for key in "language_selected store_selected framework_selected".split(): need(p[key] is None, "premature selection")
    closed(d["companion"], "title status sha256 claims_imported disposition", "companion")
    need(d["companion"]["sha256"] == COMPANION and d["companion"]["claims_imported"] is True, "companion receipt")
    need(d["companion"]["status"] == "received-read-and-selected-primary-claims-audited", "companion scope")
    nonempty(d["companion"], "title disposition")
    need(d["observations"] == {"integration_runs": [], "model_experiments": [], "performance_measurements": [], "cross_task_questionnaire_exchange_claimed": False}, "invented observations")


def plan_gate(p):
    closed(p, "schema_version status basis families required_capabilities_removable_by_benchmark design_axes comparison_protocol areas cross_area_cases workflow phases parallel_research_rule future_run_admission observed_results", "research plan")
    need(type(p["schema_version"]) is int and p["schema_version"] == 1, "plan schema")
    need(p["status"] == "planned-unrun" and p["observed_results"] == [], "plan evidence boundary")
    need(p["families"] == FAMILIES and p["required_capabilities_removable_by_benchmark"] is False, "capability/family scope")
    need(p["design_axes"] == ["capability_availability", "task_activation", "default_configuration", "kernel_service_plugin_placement"], "four design axes")
    nonempty(p, "basis parallel_research_rule")
    c = p["comparison_protocol"]
    closed(c, "controls evidence_requirements claim_states performance_priority_source required_human_outcomes bounds", "comparison protocol")
    for key, count in [("controls", 3), ("evidence_requirements", 6), ("required_human_outcomes", 6)]:
        strings(c[key], key); need(len(c[key]) == len(set(c[key])) == count, "complete " + key)
    need(c["claim_states"] == ["source-only", "modeled", "observed", "measured", "unresolved"] and c["performance_priority_source"] == "OR-024", "classification/priorities")
    nonempty(c, "bounds")
    need([a["id"] for a in p["areas"]] == ["area.mark3." + a for a in AREAS], "twelve research areas")
    for a in p["areas"]:
        closed(a, "id label question approaches failure_cases metrics families source_ids canonical_path disposition_rule status result", "area")
        nonempty(a, "label question disposition_rule")
        for key in ("approaches", "failure_cases", "metrics"): strings(a[key], key)
        need(len(set(a["approaches"])) >= 3, "competing approaches")
        refs(a["families"], set(FAMILIES), "area families")
        refs(a["source_ids"], {f"SRC-V3-{n:03}" for n in range(1, 229)}, "area sources")
        need(a["canonical_path"] in ALLOWED, "area canonical scope"); local(a["canonical_path"])
        need(a["status"] == "planned-unrun" and a["result"] is None, "unrun area")
    need([a["id"] for a in p["cross_area_cases"]] == ["case.mark3." + a for a in CASES], "cross-area cases")
    for a in p["cross_area_cases"]:
        closed(a, "id trigger families required_outcome status result", "cross-area case")
        nonempty(a, "trigger required_outcome"); refs(a["families"], set(FAMILIES), "cross-area families")
        need(a["status"] == "planned-unrun" and a["result"] is None, "unrun cross-area case")
    w = p["workflow"]
    closed(w, "id status steps proposed_receipts faults families observed_runs", "workflow")
    need(w["id"] == "scenario.mark3.questionnaire-assistant-head" and w["status"] == "required-product-workflow-unrun" and w["observed_runs"] == [], "required workflow")
    for key, count in [("steps", 5), ("proposed_receipts", 8), ("faults", 8)]:
        strings(w[key], key); need(len(w[key]) == count, "workflow coverage")
    refs(w["families"], set(FAMILIES), "workflow families")
    phases = ["phase.mark3." + x for x in ["integration", "source-comparison", "interface-probes", "model", "language", "storage"]]
    need([s["id"] for s in p["phases"]] == phases, "freeze order")
    for i, s in enumerate(p["phases"]):
        closed(s, "id dependencies output", "phase")
        need(s["dependencies"] == ([] if i == 0 else [phases[i-1]]), "phase DAG")
        nonempty(s, "output")
    r = p["future_run_admission"]
    closed(r, "maximum_discovery_workers maximum_discovery_minutes new_metered_spend actual_hosts eligible_routes included_capacity_lease human_review_budget deadline_utc provider_trials_authorized product_implementation_authorized preconditions", "future admission")
    for key, value in [("maximum_discovery_workers", 2), ("maximum_discovery_minutes", 30), ("new_metered_spend", 0)]: need(type(r[key]) is int and r[key] == value, "research limit")
    for key in "actual_hosts eligible_routes included_capacity_lease human_review_budget deadline_utc".split(): need(r[key] is None, "invented resource admission")
    need(r["provider_trials_authorized"] is False and r["product_implementation_authorized"] is False, "unauthorized experiment")
    strings(r["preconditions"], "admission preconditions")


def companion_gate(c):
    closed(c, "schema_version status companion_sha256 private_paths_copied sources findings unrefreshed_comparisons limitations observed_results", "companion audit")
    need(type(c["schema_version"]) is int and c["schema_version"] == 1, "audit schema")
    need(c["status"] == "selected-primary-claims-verified-not-runtime-tested" and c["companion_sha256"] == COMPANION, "audit identity")
    need(c["private_paths_copied"] is False and c["observed_results"] == [], "audit privacy/evidence")
    ids = [f"SRC-V3-{n:03}" for n in range(224, 229)]
    need([s["id"] for s in c["sources"]] == ids, "audit source inventory")
    source_rows = dict(re.findall(r"^\| `(SRC-V3-\d{3})` \| ([^|]*)\|", text("docs/v3/SOURCE-REGISTER.md"), re.M))
    for s in c["sources"]:
        closed(s, "id title publisher url version retrieved_date locator content_sha256 digest_basis status applicability_limit revalidation_trigger contradiction", "audit source")
        for key in s: nonempty(s, key)
        need(M["HEX64"].fullmatch(s["content_sha256"]), "source digest")
        need(s["retrieved_date"] == "2026-09-07" and s["digest_basis"] == "raw-response-bytes" and s["status"] == "source-documented", "source classification")
        u = urlsplit(s["url"])
        need(u.scheme == "https" and u.hostname in {"code.claude.com", "geminicli.com", "raw.githubusercontent.com", "hermes-agent.nousresearch.com"} and not any([u.username, u.password, u.query, u.fragment, u.port]), "public primary URL")
        need("(" + s["url"] + ")" in source_rows[s["id"]], "audit source binding")
        if s["id"] == "SRC-V3-226": need(M["HEX40"].fullmatch(s["version"]) and "/" + s["version"] + "/" in s["url"], "Pi documentation pin")
    need(rows(c["findings"], "findings") == {"finding.mark3." + x for x in ["classifier-context", "headless-ask", "pi-stop", "hermes-redirection", "hermes-host-approval"]}, "five findings")
    for f in c["findings"]:
        closed(f, "id statement status source_ids limits contradictory_evidence confidence decisive_test next_test canonical_path observed_runs", "finding")
        nonempty(f, "statement limits contradictory_evidence confidence decisive_test")
        need(f["status"] == "source-documented" and f["observed_runs"] == [], "finding evidence boundary")
        refs(f["source_ids"], set(ids), "finding sources")
        need(f["next_test"] in {"experiment.mark2." + x for x in FAMILIES}, "finding decisive family")
        need(f["canonical_path"] in ALLOWED, "finding canonical scope")
        for source in f["source_ids"]: need(source in text(f["canonical_path"]), "finding canonical source reference")
    for key in ("unrefreshed_comparisons", "limitations"): strings(c[key], key)


def adversarial(d, p, c, inv):
    rejected = []
    cases = [
        (0, ["schema_version"], True), (0, ["decisions", 0, "selected_option"], "broker-inclusive"),
        (0, ["decisions", 1, "status"], "pending"), (0, ["decisions", 0, "technical_completion"], True),
        (0, ["decisions", 0, "qualifications"], []), (0, ["decisions", 1, "approval_ref"], "peer-advice"),
        (0, ["source", "quotes", 0, "text"], "Silence approves."),
        (0, ["source", "quotes", 10, "classification"], "verbatim-owner-approved-foundation"),
        (0, ["rulings", 0, "summary"], "Other ruling."),
        (0, ["preserved", "goal_spec_amendments_delegated"], True),
        (0, ["preserved", "language_selected"], "selected"),
        (0, ["observations", "cross_task_questionnaire_exchange_claimed"], True),
        (1, ["families"], FAMILIES + ["ninth"]), (1, ["required_capabilities_removable_by_benchmark"], True),
        (1, ["areas"], []), (1, ["areas", 0, "result"], "passed"),
        (1, ["areas", 0, "approaches"], ["only"]), (1, ["cross_area_cases"], []),
        (1, ["workflow", "observed_runs"], ["synthetic"]), (1, ["phases", 3, "dependencies"], []),
        (1, ["future_run_admission", "actual_hosts"], ["invented"]),
        (1, ["future_run_admission", "new_metered_spend"], 1),
        (1, ["future_run_admission", "provider_trials_authorized"], True),
        (2, ["sources", 0, "url"], "https://geminicli.com/docs/reference/policy-engine/"),
        (2, ["sources", 2, "version"], "main"), (2, ["findings", 0, "observed_runs"], ["passed"]),
        (2, ["findings", 0, "source_ids"], []), (2, ["private_paths_copied"], True),
    ]
    for index, path, value in cases:
        data = copy.deepcopy([d, p, c]); node = data[index]
        for key in path[:-1]: node = node[key]
        node[path[-1]] = value
        try:
            [lambda: direction_gate(data[0], inv), lambda: plan_gate(data[1]), lambda: companion_gate(data[2])][index]()
        except (ValueError, KeyError, TypeError): rejected.append(path); continue
        raise ValueError("accepted Mark 3 mutant " + str(path))
    return len(rejected)


def inventory_gate(inv, candidate, changed):
    closed(inv, "schema_version start_commit allowed_files inputs regression_commands regression_entrypoints artifacts quote_digests limitations", "inventory")
    need(type(inv["schema_version"]) is int and inv["schema_version"] == 1 and inv["start_commit"] == START, "inventory identity")
    need(inv["allowed_files"] == sorted(ALLOWED), "closed allowlist")
    commands = OLD["regression_commands"]()
    need(inv["regression_commands"] == commands and len(commands) == 25, "unchanged regression inventory")
    expected = {next(a for a in cmd if a.endswith(".py")) for cmd in commands}
    need(rows(inv["regression_entrypoints"], "entrypoints", "path") == expected, "regression entrypoints")
    for x in inv["regression_entrypoints"]:
        closed(x, "path sha256", "entrypoint")
        base = git("show", START + ":" + x["path"], binary=True)
        need(sha(base) == x["sha256"] and base == git("show", candidate + ":" + x["path"], binary=True), "changed regression code")
    need(rows(inv["inputs"], "inputs", "path") == {"CONTROL_PLANE.md", "CLAUDE.md", "ANCHOR.md", "docs/v3/foundation-research/mark2/handoff.md", "docs/v3/foundation-research/mark2/directions.json", "docs/v3/foundation-research/mark2-research/evidence.json", "docs/v3/foundation-research/mark2-research/decisions.json", "docs/v3/foundation-research/mark2-research/experiments.json", "docs/v3/foundation-research/mark2-research/validation-inventory.json", "docs/v3/prompts/standalone-harness-foundation-deep-research.md"}, "frozen inputs")
    for x in inv["inputs"]:
        closed(x, "path sha256", "input")
        need(sha(git("show", START + ":" + x["path"], binary=True)) == x["sha256"], "input digest")
    need(rows(inv["artifacts"], "artifacts", "path") == set(changed) - {PREFIX + "validation-inventory.json"}, "artifact coverage")
    for x in inv["artifacts"]:
        closed(x, "path git_blob_sha256", "artifact")
        need(sha(git("show", candidate + ":" + x["path"], binary=True)) == x["git_blob_sha256"], "artifact digest " + x["path"])
    strings(inv["limitations"], "limitations")
    return commands


def document_gate(changed):
    OLD["publication_gate"](changed)
    for name in changed:
        raw = text(name); M["public_artifact"](raw, name)
        if not name.endswith(".md"): continue
        p = ROOT / name
        prose = re.sub(r"(?ms)^\x60\x60\x60.*?^\x60\x60\x60[ \t]*\r?$", "", raw)
        for ref in re.findall(r"\[[^\]]*\]\(([^)]+)\)", prose):
            ref = ref.strip().strip("<>")
            if re.match(r"^(https?|mailto|data):", ref): continue
            need((p.parent / ref.split("#", 1)[0]).resolve().is_relative_to(ROOT), "escaping local link")
            OLD["path_ref"](ref, p if ref.startswith("#") else p.parent)
    terminal = text("docs/v3/TERMINAL-RUNTIME.md")
    for feature in M["FEATURES"]: need("| " + feature + " |" in terminal, "ten terminal controls")
    directions = strict(text("docs/v3/foundation-research/mark2/directions.json"))
    for mode in directions["modes"]["software_update"]: need("| " + mode + " |" in text("docs/v3/ARCHITECTURE.md"), "six update modes")
    old_owner = git("show", START + ":docs/v3/DECISION-REGISTER.md")
    for row in re.findall(r"^\| OR-\d{3} \|.*$", old_owner, re.M):
        need(row in text("docs/v3/DECISION-REGISTER.md"), "historical Owner ruling changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True); parser.add_argument("--candidate", required=True)
    args = parser.parse_args()
    need(args.base == START and M["HEX40"].fullmatch(args.candidate), "full frozen hashes")
    need(git("branch", "--show-current") == BRANCH, "branch")
    need(git("rev-parse", "HEAD") == args.candidate and not git("status", "--porcelain=v1", "--untracked-files=all"), "clean exact candidate")
    for ancestor in [START, M["START"], *M["ANCESTORS"]]: git("merge-base", "--is-ancestor", ancestor, args.candidate)
    owners = [x for x in git("worktree", "list", "--porcelain").split("\n\n") if "branch refs/heads/" + BRANCH in x.splitlines()]
    need(len(owners) == 1 and Path(owners[0].splitlines()[0][9:]).resolve() == ROOT, "exclusive worktree")
    changed = git("diff", "--name-only", "--no-renames", START, args.candidate).splitlines()
    need(set(changed) == ALLOWED, "complete bounded diff")
    need(not git("diff", "--name-only", "--diff-filter=D", START, args.candidate), "deleted artifact")
    git("diff", "--check", START, args.candidate)
    need({p.name for p in AREA.iterdir()} == FILES, "closed campaign artifacts")
    inv = read("validation-inventory.json")
    commands = inventory_gate(inv, args.candidate, changed)
    d, p, c = [read(n) for n in ["directions.json", "research-plan.json", "companion-review.json"]]
    direction_gate(d, inv); plan_gate(p); companion_gate(c); document_gate(changed)
    ev, matrix, trials, decisions = [M["read"](n) for n in ["evidence.json", "compatibility.json", "experiments.json", "decisions.json"]]
    M["data_gate"](ev, matrix, trials, decisions)
    sources, claims = bindings(ev)
    historical = M["historical_gate"](sources, claims)
    old_inv = M["read"]("validation-inventory.json")
    arithmetic = M["arithmetic_gate"](old_inv)
    # Use the extended positive binding validator for the unchanged historical mutants too.
    # Otherwise its old source-count guard would make URL/statement mutants fail vacuously.
    M["adversarial"].__globals__["bindings"] = bindings
    old_mutants = M["adversarial"](ev, matrix, trials, decisions, old_inv)
    mutants = adversarial(d, p, c, inv)
    common = Path(git("rev-parse", "--git-common-dir"))
    if not common.is_absolute(): common = (ROOT / common).resolve()
    out = common / "research-attestations" / "mark3" / args.candidate
    out.mkdir(parents=True, exist_ok=True)
    runid = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + str(time.time_ns())[-6:]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    if os.name == "nt":
        bash = Path(os.environ.get("ProgramFiles", "")) / "Git/bin"
        if (bash / "bash.exe").is_file(): env["PATH"] = str(bash) + os.pathsep + env.get("PATH", "")
    receipts = []
    for i, command in enumerate(commands):
        before = time.monotonic()
        result = subprocess.run([sys.executable, *command[1:]], cwd=ROOT, env=env, capture_output=True, timeout=240)
        output = result.stdout + result.stderr
        (out / f"{runid}-{i:02}.log").write_bytes(output)
        row = {"command":command, "exit_code":result.returncode, "seconds":round(time.monotonic()-before, 3), "output_sha256":sha(output)}
        receipts.append(row); print(json.dumps(row), flush=True)
        need(result.returncode == 0, "regression failed: " + " ".join(command))
    need(git("rev-parse", "HEAD") == args.candidate and not git("status", "--porcelain=v1", "--untracked-files=all"), "candidate changed during gate")
    receipt = {"base":START, "candidate":args.candidate, "run_id":runid, "accepted_decisions":2, "new_rulings":4,
        "research_areas":12, "cross_area_cases":6, "experiment_families":8, "new_sources":5,
        "mark3_mutants":mutants, "mark2_mutants":old_mutants, "arithmetic_cases":arithmetic, "historical":historical,
        "artifacts":{name:sha(git("show", args.candidate + ":" + name, binary=True)) for name in changed},
        "regressions":receipts, "privacy_certified":False, "runtime_integration_observed":False}
    raw = json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8")
    (out / (runid + ".json")).write_bytes(raw + b"\n")
    print("MARK3_GATE_PASS " + json.dumps({"candidate":args.candidate, "regressions":len(receipts), "mark3_mutants":mutants, "receipt_sha256":sha(raw), "run_id":runid}), flush=True)


if __name__ == "__main__":
    try: main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as error:
        print("MARK3_GATE_FAIL " + str(error), file=sys.stderr); sys.exit(1)
