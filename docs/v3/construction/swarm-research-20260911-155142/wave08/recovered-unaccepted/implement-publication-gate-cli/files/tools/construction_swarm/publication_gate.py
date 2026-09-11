"""Fail-closed construction publication gate for the Recursion review branch.

This tool is a verifier, never a runner.  It re-executes a fixed set of git
identity predicates against the native workspace and validates separately
produced evidence: the preregistered command manifest, per-host check
receipts and retained logs, two distinctly owned audit receipts, the final
review bundle, the adversarial disposition table, and the reviewed/published
PR bodies.  It never executes manifest argv, never imports campaign sources,
and emits exactly one canonical verdict record whose status is one of
PASS_CONSTRUCTION_ONLY, FAIL or INCOMPLETE.  Any unresolved manifest field,
missing artifact, hash mismatch or drifting candidate refuses PASS.

It is not the inherited 87-command Windows full gate, claims no equivalence
with it, confers no scientific admission (which remains
BLOCKED_NO_EXECUTION_AUTHORIZED) and grants no merge authority; Lucas alone
merges.

Hash-binding order (acyclic; the returned design's literal three-way cycle
is unconstructible): manifest -> check receipts -> owned audits -> reviewed
PR draft -> reviews -> disposition table -> published body -> verdict.
Reviews bind the reviewed draft; the published body embeds every content
hash.  The manifest pins review paths and reviewer identities (the bundle
hash); review content hashes bind through the verdict, disposition table
and published body.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


CAMPAIGN = "research-20260911-155142"
PARENT = "goal-recursion-v2-execution-fabric"
BRANCH = "codex/swarm-research-20260911-155142"
PULL_REQUEST = 124
ACTIVATION_SOURCE = "235aaa7e76095ee18460d9b7ba7a6a8bad1005ac"
ALLOWED_ROOTS = (
    "docs/v3/construction/swarm-research-20260911-155142/",
    "experiments/v3/swarm-research-20260911-155142/",
    "tools/construction_swarm/",
    "docs/v3/construction-swarm/",
)
REQUIRED_SOURCES = (
    "experiments/v3/swarm-research-20260911-155142/boundary.py",
    "experiments/v3/swarm-research-20260911-155142/inventory_audit.py",
    "experiments/v3/swarm-research-20260911-155142/boundary_audit.py",
    "experiments/v3/swarm-research-20260911-155142/boundary_controls.py",
    "experiments/v3/swarm-research-20260911-155142/research_entry.py",
)
DEADLINE_UTC = "2026-09-11T23:51:42Z"
FINALIZATION_RESERVE_SECONDS = 10_200
QUOTA_MAX_AGE_SECONDS = 900
QUOTA_RESERVE_POINTS = 8
VALIDATION_CONTRACT_SHA256 = "39184142c00a1a55d66ca0700f26b78245593e51f78130550714f3fa547c34da"
MODEL_REVISION_SHA256 = "81a0624af95c15bdf9b9e342d706b9fa4d1b4c39ff048249f27d0dca259aaecf"
SAME_MODEL_REVIEW = {"model": "gpt-5.6-sol", "effort": "xhigh"}
SAME_MODEL_REVIEW_LABEL = "gpt-5.6-sol xhigh"
SCIENTIFIC_ADMISSION = "BLOCKED_NO_EXECUTION_AUTHORIZED"
MERGE_AUTHORITY = "Lucas alone"

CHECK_ORDER = (
    "freeze-and-scope", "preregistration", "windows-unittest", "windows-ruff",
    "wsl-unittest", "wsl-lint-or-substitute", "diff-check", "source-only-syntax",
    "clean-cgroup", "ownership-audit-1", "ownership-audit-2", "final-reviews-bound",
    "disposition-completeness", "pr-body-hash-binding", "verdict",
)
CHECK_STATUS = {"PASS", "FAIL", "UNKNOWN", "SKIPPED_NOT_RUN"}
DISPOSITIONS = {"fixed-in-candidate", "rejected-with-reason", "deferred-owner-bound"}
REVIEW_ITEM_KEYS = {"reservations", "defects", "blocking_gaps", "dissent"}

# Manifest host checks: id -> fixed host set.  The manifest records argv only;
# this tool never executes it.  clean-cgroup uses a dedicated receipt schema.
HOST_CHECKS = {
    "windows-unittest": ("windows",),
    "windows-ruff": ("windows",),
    "wsl-unittest": ("wsl",),
    "wsl-lint-or-substitute": ("wsl",),
    "diff-check": ("windows", "wsl"),
    "source-only-syntax": ("wsl",),
    "clean-cgroup": ("wsl",),
}
MANIFEST_CHECK_ORDER = tuple(HOST_CHECKS)

HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
CGROUP_RE = re.compile(r"/sys/fs/cgroup/recursion-foundry-tool-[0-3]")
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:[\\/]")
WINDOWS_RESERVED = {"con", "prn", "aux", "nul",
                    *(f"com{i}" for i in range(10)), *(f"lpt{i}" for i in range(10))}

PRESERVED_LIMITATIONS = (
    "This gate is construction-only; it is not the inherited 87-command "
    "Windows full gate and no native receipt satisfies or impersonates it.",
    "Scientific admission remains BLOCKED_NO_EXECUTION_AUTHORIZED; a "
    "PASS_CONSTRUCTION_ONLY verdict is not execution authorization, not "
    "control results and not merge approval.",
    "Windows evidence is host-qualified: receipts must declare Windows host "
    "identity and native-Windows path form; /mnt/c aliases are observation "
    "paths only and never executing-path claims.",
    "Receipt presence or hash identity is not proof of contents; the two "
    "separately owned audits exist because internal receipts carry acceptance.",
    "Zero GitHub status checks or review objects never fail this gate; "
    "claiming them in the PR body does.",
    "Merge authority is Lucas alone.",
)

RECEIPT_KEYS = {
    "schema", "campaign", "parent_goal", "check_id", "host", "attempt",
    "candidate", "candidate_tree", "manifest_sha256", "status", "exit_code",
    "observed", "log_sha256", "started_utc", "finished_utc", "uninterrupted",
    "scientific_approval", "full_gate_equivalence", "notes",
}
FREEZE_KEYS = {
    "schema", "campaign", "parent_goal", "attempt", "candidate",
    "candidate_tree", "review_branch", "activation_source_commit",
    "windows", "wsl", "created_utc",
}
FREEZE_HOST_KEYS = {
    "head", "tree", "branch", "clean", "pause_stop_absent", "host",
    "captured_utc",
}
HOST_BLOCK_KEYS = {"os", "repo", "identity"}
CGROUP_KEYS = {
    "schema", "campaign", "parent_goal", "attempt", "candidate",
    "candidate_tree", "manifest_sha256", "outcomes", "final_sweep",
    "windows_quiescence", "created_utc", "scientific_approval",
}
AUDIT_KEYS = {
    "schema", "campaign", "parent_goal", "attempt", "candidate",
    "candidate_tree", "manifest_sha256", "owner", "status",
    "attempt_membership", "source_membership_verified",
    "quiescence_verified", "created_utc", "scientific_approval",
}
REVIEW_KEYS = {
    "schema", "campaign", "parent_goal", "candidate", "candidate_tree",
    "manifest_sha256", "bundle_sha256", "reviewer", "model", "effort",
    "route", "gate_receipt_sha256s", "owned_audit_sha256s",
    "pr_body_reviewed_sha256", "limitations_sha256", "reviewed_utc",
    "status", "items", "scientific_admission", "acceptance",
}
DISPOSITION_KEYS = {
    "schema", "campaign", "parent_goal", "manifest_sha256",
    "review_sha256s", "items",
}
DISPOSITION_ITEM_KEYS = {
    "item_id", "disposition", "reason", "evidence_sha256", "owner_record",
}
QUOTA_KEYS = {
    "checked_utc", "binding_windows", "remaining_percent",
    "reset_credits_used", "new_metered_spend", "source",
}
QUOTA_WINDOW_KEYS = {"name", "used_percent", "remaining_percent", "resets_at"}
OBLIGATION_KEYS = {
    "schema", "campaign", "parent_goal", "validation_contract_sha256",
    "model_revision_sha256", "effective_same_model_review", "basis_note",
}
MANIFEST_KEYS = {
    "schema", "campaign", "parent_goal", "review_branch", "pull_request",
    "frozen_candidate_commit", "frozen_candidate_tree",
    "activation_source_commit", "gate_attempt_ordinal",
    "gate_runner_identity", "allowed_change_roots", "non_goals",
    "scope_statement", "limitations_text", "checks", "campaign_sources",
    "lint_scope", "native_ruff_available", "receipt_root_windows",
    "audit_owners", "review_bundle", "artifacts", "quota", "pr_body",
    "deadline_utc", "finalization_reserve_seconds",
}
MANIFEST_CHECK_KEYS = {"id", "argv", "expected"}
MANIFEST_SOURCE_KEYS = {"path", "sha256", "bytes"}
BUNDLE_KEYS = {"entries", "bundle_sha256"}
BUNDLE_ENTRY_KEYS = {"path", "reviewer", "model", "effort", "route"}
ARTIFACT_KEYS = {
    "freeze_receipt", "cgroup_receipt", "audit_receipts", "disposition_table",
    "reviewed_pr_body", "published_pr_body", "obligations_record",
    "quota_record",
}
QUOTA_MANIFEST_KEYS = {
    "required", "max_age_seconds", "reserve_points", "reset_identities",
}
PR_BODY_MANIFEST_KEYS = {
    "required_fragments", "github_disclaimer", "forbidden_patterns",
}

# Affirmative-claim patterns; negated disclosures ("no GitHub status checks
# exist") must not match.  The PR body is required to say evidence is
# internal-only, so an affirmative GitHub claim is a binding failure.
PR_BODY_FORBIDDEN = (
    re.compile(r"(?i)\bgithub\b[^\n]{0,120}"
               r"\b(status[ -]?checks?|checks?|reviews?|statuscheckrollup)\b"
               r"[^\n]{0,60}\b(passed|pass|green|approved|satisfied|succeeded|enforced)\b"),
    re.compile(r"(?i)\b(passed|approved|green|satisfied|succeeded)\b[^\n]{0,60}"
               r"\bgithub\b[^\n]{0,120}\b(checks?|reviews?|statuscheckrollup)\b"),
    re.compile(r"(?i)\brequired[ -]?checks?\b[^\n]{0,60}"
               r"\b(passed|green|enforced|satisfied)\b"),
)
PR_BODY_BUILTIN_FRAGMENTS = (
    SCIENTIFIC_ADMISSION,
    "construction-only",
    "Lucas alone",
)


class Refused(ValueError):
    """A single evidence or identity predicate failed."""


class Abort(Exception):
    """Verdict-deciding abort: status (FAIL/INCOMPLETE), code, detail."""

    def __init__(self, status, code, detail):
        super().__init__(detail)
        require(status in {"FAIL", "INCOMPLETE"}, "abort status")
        self.status, self.code, self.detail = status, code, str(detail)[:4000]


def require(value, reason):
    if not value:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _now():
    return dt.datetime.now(dt.timezone.utc)


def utc(value):
    require(type(value) is str, "UTC timestamp string required")
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Refused("invalid UTC timestamp") from exc
    require(parsed.utcoffset() == dt.timedelta(0), "timestamp must be UTC")
    return parsed


def strict_json(raw):
    require(type(raw) is bytes and not raw.startswith(b"\xef\xbb\xbf"),
            "UTF-8 JSON without BOM required")

    def pairs(items):
        result = {}
        for key, value in items:
            require(type(key) is str and key not in result, "duplicate/non-string JSON key")
            result[key] = value
        return result

    def finite(value):
        number = float(value)
        require(math.isfinite(number), "nonfinite JSON number")
        return number

    try:
        text = raw.decode("utf-8", errors="strict")
        return json.loads(text, object_pairs_hook=pairs, parse_float=finite,
                          parse_constant=lambda value: require(False, "nonfinite JSON constant"))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise Refused("invalid strict JSON: " + str(exc)) from exc


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def exact_keys(value, keys, reason):
    require(type(value) is dict and set(value) == set(keys), reason)


def safe_rel(value):
    require(type(value) is str and 0 < len(value) <= 240, "bounded relative path required")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value and all(
        re.fullmatch(r"[A-Za-z0-9_.-]+", part) and part not in {".", ".."}
        and not part.startswith(".") and not part.endswith((".", " "))
        and part.lower().split(".")[0] not in WINDOWS_RESERVED for part in path.parts),
        "canonical portable relative path required: " + str(value))
    return value


def scan_unresolved(value, trail=""):
    """Fail if any nested string/flag marks a preregistered field unresolved."""
    if type(value) is str:
        require("UNRESOLVED" not in value,
                "unresolved placeholder at " + (trail or "<root>"))
    elif type(value) is list:
        for index, item in enumerate(value):
            scan_unresolved(item, f"{trail}[{index}]")
    elif type(value) is dict:
        for key, item in value.items():
            require(not (key == "resolved" and item is False),
                    "unresolved flag at " + trail + ".resolved")
            scan_unresolved(item, f"{trail}.{key}" if trail else key)


def file_bytes(evidence, name, limit=40 * 1024**2):
    safe_rel(name)
    path = Path(evidence) / name
    require(path.is_file() and not path.is_symlink(),
            "missing/nonregular evidence file: " + name)
    resolved = path.resolve(strict=True)
    require(resolved.is_relative_to(Path(evidence).resolve(strict=True)),
            "evidence file escapes root: " + name)
    size = resolved.stat().st_size
    require(0 < size <= limit, "evidence file outside byte bound: " + name)
    return resolved.read_bytes()


def json_file(evidence, name, limit=4 * 1024**2, canonical=True):
    raw = file_bytes(evidence, name, limit)
    value = strict_json(raw)
    if canonical:
        require(raw == canonical_bytes(value) + b"\n",
                "evidence record is not exact canonical JSON: " + name)
    return value, raw


def put_exclusive(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    require(path.parent.resolve() == path.parent and not path.parent.is_symlink(),
            "noncanonical output parent")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        raise
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def git(repo, *args):
    """Fixed plumbing only; manifest argv is never executed."""
    try:
        return subprocess.check_output(["git", "-C", str(repo), *args],
                                       stderr=subprocess.STDOUT, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Refused("git observation failed: " + " ".join(args)) from exc


def git_text(repo, *args):
    return git(repo, *args).decode("utf-8", errors="strict").strip()


def marker_paths(evidence, repo):
    roots = [Path(evidence)]
    if repo is not None:
        roots.append(Path(repo))
    return tuple(path for root in roots for path in (
        root / "PAUSE", root / "STOP", root / "state/PAUSE", root / "state/STOP"))


def parent_active(repo):
    path = Path(repo) / "state/goals" / (PARENT + ".md")
    require(path.is_file() and not path.is_symlink(), "active parent goal record missing")
    fields = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            if key in {"id", "status"}:
                fields[key] = value
    require(fields == {"id": PARENT, "status": "active"}, "parent goal is not active")


class Ctx:
    """One gate attempt evaluation: collected check records and bindings."""

    def __init__(self, evidence, repo, now, activation_source):
        self.evidence = Path(evidence)
        require(self.evidence.is_dir() and not self.evidence.is_symlink(),
                "evidence root must be a real directory")
        self.repo = Path(repo) if repo is not None else None
        self.now = now
        self.activation_source = activation_source
        self.checks = {}
        self.receipt_shas = {}
        self.manifest = None
        self.manifest_name = None
        self.manifest_sha = None
        self.audit_shas = []
        self.review_shas = []
        self.disposition_sha = None
        self.pr_body_sha = None
        self.cgroup_verification = {"swept": False, "violations": []}
        self.limitations = list(PRESERVED_LIMITATIONS)

    def record(self, check_id, status, detail="", receipts=()):
        require(status in CHECK_STATUS, "unknown check status")
        entry = {"id": check_id, "status": status,
                 "receipt_sha256": receipts[0][1] if len(receipts) == 1 else None,
                 "receipts": [{"path": p, "sha256": s} for p, s in receipts],
                 "detail": str(detail)[:2000]}
        self.checks[check_id] = entry
        return entry

    def fail(self, check_id, detail, receipts=(), code=None):
        self.record(check_id, "FAIL", detail, receipts)
        raise Abort("FAIL", code or ("FAIL_" + check_id.upper().replace("-", "_")), detail)

    def incomplete(self, check_id, detail, receipts=(), code=None):
        self.record(check_id, "UNKNOWN", detail, receipts)
        raise Abort("INCOMPLETE", code or ("INCOMPLETE_" + check_id.upper().replace("-", "_")),
                    detail)


# ---------------------------------------------------------------- manifest

def load_manifest(ctx, manifest_name):
    try:
        manifest, raw = json_file(ctx.evidence, manifest_name, limit=2 * 1024**2,
                                  canonical=True)
    except Refused as exc:
        ctx.incomplete("preregistration", "manifest unreadable/noncanonical: " + str(exc),
                       code="INCOMPLETE_MANIFEST")
    ctx.manifest, ctx.manifest_name, ctx.manifest_sha = manifest, manifest_name, sha(raw)
    try:
        scan_unresolved(manifest)
        exact_keys(manifest, MANIFEST_KEYS, "manifest schema changed")
        require(manifest["schema"] == "recursion-publication-gate-manifest/v1",
                "manifest schema id")
        require(manifest["campaign"] == CAMPAIGN and manifest["parent_goal"] == PARENT
                and manifest["review_branch"] == BRANCH
                and manifest["pull_request"] == PULL_REQUEST, "manifest identity")
        require(HEX40.fullmatch(str(manifest["frozen_candidate_commit"]))
                and HEX40.fullmatch(str(manifest["frozen_candidate_tree"])),
                "frozen candidate commit/tree")
        require(manifest["activation_source_commit"] == ctx.activation_source
                and HEX40.fullmatch(ctx.activation_source), "activation source binding")
        require(type(manifest["gate_attempt_ordinal"]) is int
                and manifest["gate_attempt_ordinal"] >= 1, "attempt ordinal")
        require(type(manifest["gate_runner_identity"]) is str
                and manifest["gate_runner_identity"], "gate runner identity")
        require(manifest["allowed_change_roots"] == list(ALLOWED_ROOTS),
                "allowed change roots")
        require(type(manifest["non_goals"]) is list and manifest["non_goals"]
                and all(type(x) is str and x for x in manifest["non_goals"])
                and any("merge" in x for x in manifest["non_goals"])
                and any("scientific" in x for x in manifest["non_goals"]),
                "non-goals must retain merge and scientific exclusions")
        require(type(manifest["scope_statement"]) is str
                and 0 < len(manifest["scope_statement"]) <= 8000, "scope statement")
        require(type(manifest["limitations_text"]) is str
                and 0 < len(manifest["limitations_text"]) <= 32000, "limitations text")
        require(manifest["deadline_utc"] == DEADLINE_UTC
                and manifest["finalization_reserve_seconds"] == FINALIZATION_RESERVE_SECONDS,
                "manifest clock bounds differ from policy")
        _manifest_checks(manifest)
        _manifest_sources(manifest)
        _manifest_reviewers(manifest)
        _manifest_artifacts(manifest)
        _manifest_quota(ctx, manifest)
        _manifest_obligations(ctx, manifest)
        require(type(manifest["native_ruff_available"]) is bool, "native ruff flag")
        require(type(manifest["receipt_root_windows"]) is str
                and WINDOWS_PATH_RE.match(manifest["receipt_root_windows"])
                and "/mnt/" not in manifest["receipt_root_windows"],
                "Windows receipt root must be native Windows form")
        owners = manifest["audit_owners"]
        require(type(owners) is list and len(owners) == 2
                and all(type(o) is str and o for o in owners)
                and owners[0] != owners[1]
                and manifest["gate_runner_identity"] not in owners,
                "two audit owners distinct from gate runner")
    except Refused as exc:
        ctx.incomplete("preregistration", str(exc), code="INCOMPLETE_MANIFEST")
    ctx.record("preregistration", "PASS", "manifest canonical and bound")


def _manifest_checks(manifest):
    checks = manifest["checks"]
    require(type(checks) is list and len(checks) == len(MANIFEST_CHECK_ORDER)
            and all(type(c) is dict for c in checks)
            and [c["id"] for c in checks] == list(MANIFEST_CHECK_ORDER),
            "manifest must list exactly the ordered host checks")
    for entry in checks:
        exact_keys(entry, MANIFEST_CHECK_KEYS, "manifest check schema")
        check_id = entry["id"]
        hosts = HOST_CHECKS[check_id]
        argv, expected = entry["argv"], entry["expected"]
        require(type(argv) is dict and set(argv) == set(hosts)
                and type(expected) is dict and set(expected) == set(hosts),
                "check argv/expected must cover exactly its hosts: " + check_id)
        for host in hosts:
            args = argv[host]
            require(type(args) is list and 1 <= len(args) <= 64 and all(
                type(a) is str and 0 < len(a) <= 16384 and "\0" not in a
                for a in args), "bounded recorded argv: " + check_id + "/" + host)
            exp = expected[host]
            require(type(exp) is dict, "expected record: " + check_id)
            if check_id == "clean-cgroup":
                exact_keys(exp, {"max_memory_bytes"}, "cgroup expectation")
                require(type(exp["max_memory_bytes"]) is int
                        and 0 < exp["max_memory_bytes"] <= 8 * 1024**3,
                        "bounded cgroup memory expectation")
            else:
                require(exp.get("exit_code") == 0, "expected exit code 0 required")
                extra = set(exp) - {"exit_code"}
                if check_id in {"windows-unittest", "wsl-unittest"}:
                    require(extra == {"tests", "skips"}
                            and type(exp["tests"]) is int and 1 <= exp["tests"] <= 200000
                            and type(exp["skips"]) is int and 0 <= exp["skips"] <= exp["tests"],
                            "unittest expectations must carry test/skip counts")
                else:
                    require(not extra, "unexpected expectation fields: " + check_id)


def _manifest_sources(manifest):
    sources = manifest["campaign_sources"]
    require(type(sources) is list and 5 <= len(sources) <= 400, "campaign source list")
    paths = []
    for row in sources:
        exact_keys(row, MANIFEST_SOURCE_KEYS, "campaign source schema")
        paths.append(safe_rel(row["path"]))
        require(HEX64.fullmatch(str(row["sha256"]))
                and type(row["bytes"]) is int and 0 < row["bytes"] <= 2 * 1024**2,
                "campaign source identity")
    require(paths == sorted(paths) and len(set(paths)) == len(paths),
            "sorted unique campaign sources")
    require(set(REQUIRED_SOURCES) <= set(paths), "required campaign sources omitted")
    lint = manifest["lint_scope"]
    require(type(lint) is list and lint
            and all(type(p) is str for p in lint), "lint scope")
    for entry in lint:
        safe_rel(entry)


def _manifest_reviewers(manifest):
    bundle = manifest["review_bundle"]
    exact_keys(bundle, BUNDLE_KEYS, "review bundle schema")
    entries = bundle["entries"]
    require(type(entries) is list and len(entries) >= 2, "at least two reviewers")
    reviewers = set()
    sol = set()
    for entry in entries:
        exact_keys(entry, BUNDLE_ENTRY_KEYS, "review bundle entry")
        safe_rel(entry["path"])
        require(type(entry["reviewer"]) is str and entry["reviewer"]
                and entry["reviewer"] not in reviewers, "distinct reviewer identity")
        require(type(entry["model"]) is str and type(entry["effort"]) is str
                and type(entry["route"]) is str and entry["route"], "reviewer route")
        reviewers.add(entry["reviewer"])
        if entry["model"] == SAME_MODEL_REVIEW["model"] \
                and entry["effort"] == SAME_MODEL_REVIEW["effort"]:
            sol.add(entry["reviewer"])
    require(len(sol) >= 2, "two distinct gpt-5.6-sol xhigh reviewers required")
    require(bundle["bundle_sha256"] == sha(canonical_bytes(entries)),
            "review bundle identity hash")


def _manifest_artifacts(manifest):
    artifacts = manifest["artifacts"]
    exact_keys(artifacts, ARTIFACT_KEYS, "artifacts schema")
    for name in ("freeze_receipt", "cgroup_receipt", "disposition_table",
                 "obligations_record", "reviewed_pr_body", "published_pr_body"):
        safe_rel(artifacts[name])
    require(artifacts["freeze_receipt"] == "freeze-receipt.json",
            "freeze receipt must be freeze-receipt.json")
    audits = artifacts["audit_receipts"]
    require(type(audits) is list and len(audits) == 2
            and audits[0] != audits[1], "two audit receipt paths")
    for name in audits:
        safe_rel(name)
    quota_record = artifacts["quota_record"]
    require(quota_record is None or type(quota_record) is str,
            "quota record path or null")
    if quota_record is not None:
        safe_rel(quota_record)
    body = manifest["pr_body"]
    exact_keys(body, PR_BODY_MANIFEST_KEYS, "pr_body policy schema")
    fragments = body["required_fragments"]
    require(type(fragments) is list
            and all(type(f) is str and f for f in fragments), "required fragments")
    require(type(body["github_disclaimer"]) is str
            and "GitHub" in body["github_disclaimer"],
            "github disclaimer fragment required")
    patterns = body["forbidden_patterns"]
    require(type(patterns) is list and len(patterns) <= 32
            and all(type(p) is str and 0 < len(p) <= 500 for p in patterns),
            "bounded forbidden patterns")
    for pattern in patterns:
        try:
            re.compile(pattern)
        except re.error as exc:
            raise Refused("invalid forbidden pattern") from exc


def _manifest_quota(ctx, manifest):
    quota = manifest["quota"]
    exact_keys(quota, QUOTA_MANIFEST_KEYS, "quota schema")
    require(type(quota["required"]) is bool, "quota required flag")
    require(type(quota["max_age_seconds"]) is int
            and 0 < quota["max_age_seconds"] <= QUOTA_MAX_AGE_SECONDS,
            "quota freshness bound must not exceed 900s")
    require(type(quota["reserve_points"]) is int
            and quota["reserve_points"] >= QUOTA_RESERVE_POINTS,
            "quota reserve must not drop below the 8-point rolling reserve")
    resets = quota["reset_identities"]
    require(type(resets) is dict and resets and all(
        type(k) is str and type(v) is int and v > 0 for k, v in resets.items()),
        "quota reset identities")
    if quota["required"]:
        require(type(manifest["artifacts"]["quota_record"]) is str,
                "quota required but no record named")
        name = manifest["artifacts"]["quota_record"]
        try:
            record, _ = json_file(ctx.evidence, name, limit=64 * 1024, canonical=True)
        except Refused as exc:
            ctx.incomplete("preregistration", "quota record: " + str(exc),
                           code="INCOMPLETE_QUOTA")
        try:
            exact_keys(record, QUOTA_KEYS, "quota record schema")
            checked = utc(record["checked_utc"])
            age = (ctx.now - checked).total_seconds()
            require(0 <= age <= quota["max_age_seconds"], "quota telemetry not fresh")
            windows = record["binding_windows"]
            require(type(windows) is list and len(windows) == 1, "one binding quota window")
            window = windows[0]
            exact_keys(window, QUOTA_WINDOW_KEYS, "quota window schema")
            require(type(window["used_percent"]) is int
                    and type(window["remaining_percent"]) is int
                    and 0 <= window["used_percent"] < 100
                    and window["remaining_percent"] == 100 - window["used_percent"],
                    "usable exact quota percentages")
            require({window["name"]: window["resets_at"]} == resets
                    and ctx.now.timestamp() < window["resets_at"],
                    "unchanged pre-reset quota identity")
            require(record["remaining_percent"] == window["remaining_percent"]
                    and record["remaining_percent"] > quota["reserve_points"],
                    "rolling quota reserve")
            require(record["reset_credits_used"] == 0
                    and record["new_metered_spend"] == 0, "included capacity only")
            require(type(record["source"]) is str and record["source"], "quota source")
        except Refused as exc:
            ctx.incomplete("preregistration", "quota record: " + str(exc),
                           code="INCOMPLETE_QUOTA")


def _manifest_obligations(ctx, manifest):
    name = manifest["artifacts"]["obligations_record"]
    try:
        record, _ = json_file(ctx.evidence, name, limit=64 * 1024, canonical=True)
        exact_keys(record, OBLIGATION_KEYS, "obligation record schema")
        require(record["schema"] == "recursion-obligation-binding/v1"
                and record["campaign"] == CAMPAIGN and record["parent_goal"] == PARENT,
                "obligation record identity")
        require(record["validation_contract_sha256"] == VALIDATION_CONTRACT_SHA256
                and record["model_revision_sha256"] == MODEL_REVISION_SHA256,
                "obligation record must bind the packet contract and model revision")
        require(record["effective_same_model_review"] == SAME_MODEL_REVIEW_LABEL,
                "obligation record must state Sol xhigh supersession")
        require(type(record["basis_note"]) is str
                and "supersed" in record["basis_note"], "supersession note required")
    except Refused as exc:
        ctx.incomplete("preregistration", "obligations record: " + str(exc),
                       code="INCOMPLETE_MANIFEST")


# ------------------------------------------------------------- freeze/scope

def native_scope(ctx):
    """Re-run the fixed git identity predicates on the native workspace."""
    manifest = ctx.manifest
    candidate = manifest["frozen_candidate_commit"]
    failures = []

    def probe(fn, label):
        try:
            fn()
        except Refused as exc:
            failures.append(label + ": " + str(exc))

    repo = ctx.repo
    require(repo.is_dir() and not repo.is_symlink(), "native workspace must be a real directory")
    probe(lambda: require(git_text(repo, "rev-parse", "HEAD") == candidate,
                          "exact candidate HEAD"), "head")
    probe(lambda: require(git_text(repo, "rev-parse", candidate + "^{tree}")
                          == manifest["frozen_candidate_tree"], "exact candidate tree"), "tree")
    probe(lambda: require(git_text(repo, "branch", "--show-current") == BRANCH,
                          "review branch"), "branch")
    probe(lambda: require(git(repo, "status", "--porcelain=v1", "-z",
                                "--untracked-files=all") == b"",
                          "workspace not exactly clean"), "clean")
    probe(lambda: require(git_text(repo, "cat-file", "-t", candidate) == "commit",
                          "candidate commit missing"), "commit")
    base = ctx.activation_source
    probe(lambda: require(git_text(repo, "merge-base", base, candidate) == base,
                          "activation merge-base changed"), "merge-base")

    def ancestry():
        subprocess.check_call(["git", "-C", str(repo), "merge-base", "--is-ancestor",
                               base, candidate], stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, timeout=30)
    try:
        ancestry()
    except (OSError, subprocess.SubprocessError) as exc:
        failures.append("ancestor: " + str(exc))
    probe(lambda: require(git(repo, "rev-list", "--merges", base + ".." + candidate)
                          .strip() == b"", "merge commit in campaign ancestry"), "linear")

    def scope_diff():
        changed = git_text(repo, "diff", "--name-only", base, candidate).splitlines()
        require(all(path.startswith(ALLOWED_ROOTS) for path in changed),
                "candidate changed protected path")
    probe(scope_diff, "scope")
    probe(lambda: require(git(repo, "diff", "--name-only", "--diff-filter=D",
                                base, candidate).strip() == b"",
                          "candidate deletes inherited path"), "deletes")
    probe(lambda: parent_active(repo), "parent")
    probe(lambda: require(not any(path.exists() for path in marker_paths(ctx.evidence, repo)),
                          "PAUSE/STOP marker present"), "markers")

    def sources():
        for row in manifest["campaign_sources"]:
            blob = git(repo, "show", candidate + ":" + row["path"])
            require(len(blob) == row["bytes"] and sha(blob) == row["sha256"],
                    "campaign source differs from manifest: " + row["path"])
    probe(sources, "sources")
    require(not failures, "; ".join(failures))


def freeze_block(value, host_os, ctx):
    exact_keys(value, FREEZE_HOST_KEYS, "freeze host block schema")
    require(value["head"] == ctx.manifest["frozen_candidate_commit"]
            and value["tree"] == ctx.manifest["frozen_candidate_tree"]
            and value["branch"] == BRANCH, "freeze " + host_os + " identity")
    require(value["clean"] is True, "freeze " + host_os + " cleanliness")
    require(value["pause_stop_absent"] is True, "freeze " + host_os + " markers")
    utc(value["captured_utc"])
    host = value["host"]
    exact_keys(host, HOST_BLOCK_KEYS, "freeze host identity schema")
    require(host["os"] == host_os and type(host["identity"]) is str and host["identity"],
            "freeze " + host_os + " host identity")
    if host_os == "windows":
        require(type(host["repo"]) is str
                and WINDOWS_PATH_RE.match(host["repo"]) and "/mnt/" not in host["repo"],
                "Windows repo must be native form, never /mnt alias")
    else:
        require(type(host["repo"]) is str and host["repo"].startswith("/")
                and not host["repo"].startswith("/mnt/"),
                "WSL repo must be a native POSIX path, never the /mnt alias")
        if ctx.repo is not None:
            require(host["repo"] == str(ctx.repo.resolve()),
                    "freeze wsl repo differs from verified workspace")


def check_freeze(ctx):
    check_id = "freeze-and-scope"
    name = ctx.manifest["artifacts"]["freeze_receipt"]
    try:
        receipt, raw = json_file(ctx.evidence, name, limit=256 * 1024, canonical=True)
    except Refused as exc:
        ctx.incomplete(check_id, "freeze receipt: " + str(exc))
    receipt_sha = sha(raw)
    try:
        exact_keys(receipt, FREEZE_KEYS, "freeze receipt schema")
        require(receipt["schema"] == "recursion-publication-freeze/v1"
                and receipt["campaign"] == CAMPAIGN and receipt["parent_goal"] == PARENT
                and receipt["attempt"] == ctx.manifest["gate_attempt_ordinal"]
                and receipt["review_branch"] == BRANCH
                and receipt["activation_source_commit"] == ctx.activation_source,
                "freeze receipt binding")
        require(receipt["candidate"] == ctx.manifest["frozen_candidate_commit"]
                and receipt["candidate_tree"] == ctx.manifest["frozen_candidate_tree"],
                "freeze receipt candidate")
        utc(receipt["created_utc"])
        freeze_block(receipt["windows"], "windows", ctx)
        freeze_block(receipt["wsl"], "wsl", ctx)
    except Refused as exc:
        ctx.fail(check_id, str(exc), receipts=((name, receipt_sha),),
                 code="FAIL_CANDIDATE_IDENTITY")
    ctx.receipt_shas[check_id] = receipt_sha
    if ctx.repo is None:
        ctx.limitations.append("native workspace not supplied; git identity "
                               "predicates verified from freeze receipt only")
        ctx.incomplete(check_id,
                       "freeze receipt valid but native git predicates not re-executed",
                       receipts=((name, receipt_sha),),
                       code="INCOMPLETE_NATIVE_SCOPE_UNVERIFIED")
    try:
        native_scope(ctx)
    except Refused as exc:
        ctx.fail(check_id, str(exc), receipts=((name, receipt_sha),),
                 code="FAIL_CANDIDATE_IDENTITY")
    ctx.record(check_id, "PASS", "exact candidate/tree/branch/clean/ancestry/scope",
               receipts=((name, receipt_sha),))


# -------------------------------------------------------------- host checks

def _receipt_names(check_id, host, hosts):
    base = check_id if len(hosts) == 1 else check_id + "." + host
    return base + ".receipt.json", base + ".log"


def _host_block(receipt, host, check_id):
    block = receipt["host"]
    exact_keys(block, HOST_BLOCK_KEYS, "receipt host schema: " + check_id)
    require(block["os"] == host, "receipt host mismatch: " + check_id)
    require(type(block["identity"]) is str and block["identity"],
            "host identity capture required: " + check_id)
    if host == "windows":
        require(type(block["repo"]) is str and WINDOWS_PATH_RE.match(block["repo"])
                and "/mnt/" not in block["repo"],
                "Windows receipt must carry native path form: " + check_id)
    else:
        require(type(block["repo"]) is str and block["repo"].startswith("/")
                and not block["repo"].startswith("/mnt/"),
                "WSL receipt must not claim Windows/alias path: " + check_id)


def _load_check_receipt(ctx, check_id, host, hosts):
    receipt_name, log_name = _receipt_names(check_id, host, hosts)
    try:
        receipt, raw = json_file(ctx.evidence, receipt_name, limit=256 * 1024,
                                 canonical=True)
    except Refused as exc:
        ctx.incomplete(check_id, "receipt missing/invalid: " + str(exc),
                       code="INCOMPLETE_EVIDENCE")
    receipt_sha = sha(raw)
    try:
        exact_keys(receipt, RECEIPT_KEYS, "check receipt schema: " + check_id)
        manifest = ctx.manifest
        require(receipt["schema"] == "recursion-publication-check/v1"
                and receipt["campaign"] == CAMPAIGN and receipt["parent_goal"] == PARENT
                and receipt["check_id"] == check_id
                and receipt["attempt"] == manifest["gate_attempt_ordinal"]
                and receipt["candidate"] == manifest["frozen_candidate_commit"]
                and receipt["candidate_tree"] == manifest["frozen_candidate_tree"]
                and receipt["manifest_sha256"] == ctx.manifest_sha,
                "receipt binding: " + check_id + "/" + host)
        require(receipt["scientific_approval"] is False
                and receipt["full_gate_equivalence"] is False,
                "receipt must disclaim approval/equivalence: " + check_id)
        require(receipt["status"] in CHECK_STATUS, "receipt status: " + check_id)
        _host_block(receipt, host, check_id)
        started, finished = utc(receipt["started_utc"]), utc(receipt["finished_utc"])
        require(started <= finished <= ctx.now, "receipt clock: " + check_id)
        require(HEX64.fullmatch(str(receipt["log_sha256"])), "log digest: " + check_id)
        log_raw = file_bytes(ctx.evidence, log_name, limit=64 * 1024**2)
        require(sha(log_raw) == receipt["log_sha256"], "log bytes differ: " + check_id)
    except Refused as exc:
        ctx.fail(check_id, str(exc), receipts=((receipt_name, receipt_sha),))
    return receipt, receipt_name, receipt_sha


def _check_expected(ctx, check_id, host, receipt):
    index = list(MANIFEST_CHECK_ORDER).index(check_id)
    expected = ctx.manifest["checks"][index]["expected"][host]
    require(receipt["exit_code"] == expected["exit_code"] == 0,
            "exit code: " + check_id)
    observed = receipt["observed"]
    require(type(observed) is dict, "observed record: " + check_id)
    if check_id in {"windows-unittest", "wsl-unittest"}:
        require(observed.get("tests") == expected["tests"]
                and observed.get("skips") == expected["skips"]
                and receipt["uninterrupted"] is True,
                "observed test/skip counts differ from manifest: " + check_id)
    elif check_id == "windows-ruff":
        require(observed.get("scope") == ctx.manifest["lint_scope"],
                "lint scope differs from manifest: " + check_id)
    elif check_id == "diff-check":
        require(observed.get("worktree_clean_after") is True
                and receipt["uninterrupted"] is True,
                "diff check must observe a clean worktree after host checks")
    elif check_id == "source-only-syntax":
        require(observed.get("mode") in {"ast.parse", "py_compile"}
                and observed.get("executed") is False,
                "source syntax check must not execute files")
        rows = observed.get("files")
        require(type(rows) is list and len(rows) == len(ctx.manifest["campaign_sources"])
                and all(type(r) is dict for r in rows)
                and [{"path": r["path"], "sha256": r["sha256"]} for r in rows]
                == [{"path": r["path"], "sha256": r["sha256"]}
                    for r in ctx.manifest["campaign_sources"]],
                "syntax check must cover every manifest source with matching sha256")
    elif check_id == "wsl-lint-or-substitute":
        _lint_route(ctx, receipt)


def _lint_route(ctx, receipt):
    observed = receipt["observed"]
    route = observed.get("route")
    if route == "wsl-ruff":
        require(ctx.manifest["native_ruff_available"] is True,
                "manifest declares no native ruff; wsl-ruff route repeats the "
                "checkpoint-gate-01 defect")
        require(type(observed.get("ruff_version")) is str
                and observed["ruff_version"], "wsl-ruff route needs ruff_version")
        require(observed.get("scope") == ctx.manifest["lint_scope"],
                "wsl-ruff scope differs from manifest")
    elif route == "wsl-source-pycompile":
        require(observed.get("reason") == "ruff-not-installed-native",
                "substitute route must record ruff-not-installed-native")
        require(ctx.manifest["native_ruff_available"] is False,
                "substitute route while manifest claims native ruff")
        require(HEX64.fullmatch(str(observed.get("windows_ruff_receipt_sha256")))
                and observed["windows_ruff_receipt_sha256"]
                == ctx.receipt_shas.get("windows-ruff"),
                "substitute route must bind the windows-ruff receipt")
        require("Windows Ruff remains the qualified lint route"
                in str(observed.get("qualification")),
                "substitute must state Windows Ruff remains qualified")
    else:
        raise Refused("wsl-lint-or-substitute must record exactly one route")


def host_checks(ctx):
    for check_id in MANIFEST_CHECK_ORDER:
        if check_id == "clean-cgroup":
            cgroup_check(ctx)
            continue
        hosts = HOST_CHECKS[check_id]
        receipts = []
        for host in hosts:
            receipt, name, receipt_sha = _load_check_receipt(ctx, check_id, host, hosts)
            receipts.append((name, receipt_sha))
            key = check_id + "." + host if len(hosts) > 1 else check_id
            ctx.receipt_shas[key] = receipt_sha
            if receipt["status"] == "PASS":
                try:
                    _check_expected(ctx, check_id, host, receipt)
                except Refused as exc:
                    ctx.fail(check_id, str(exc), receipts=receipts)
            elif receipt["status"] == "FAIL":
                ctx.fail(check_id, "check receipt reports FAIL: " + check_id + "/" + host,
                         receipts=receipts)
            else:
                ctx.incomplete(check_id,
                               "check did not produce a PASS receipt: "
                               + check_id + "/" + host + " status=" + receipt["status"],
                               receipts=receipts, code="INCOMPLETE_EVIDENCE")
        ctx.record(check_id, "PASS", "all host receipts verified", receipts=receipts)


def cgroup_check(ctx):
    check_id = "clean-cgroup"
    name = ctx.manifest["artifacts"]["cgroup_receipt"]
    try:
        receipt, raw = json_file(ctx.evidence, name, limit=256 * 1024, canonical=True)
    except Refused as exc:
        ctx.incomplete(check_id, "cgroup receipt: " + str(exc), code="INCOMPLETE_EVIDENCE")
    receipt_sha = sha(raw)
    try:
        exact_keys(receipt, CGROUP_KEYS, "cgroup receipt schema")
        manifest = ctx.manifest
        require(receipt["schema"] == "recursion-cgroup-verification/v1"
                and receipt["campaign"] == CAMPAIGN and receipt["parent_goal"] == PARENT
                and receipt["attempt"] == manifest["gate_attempt_ordinal"]
                and receipt["candidate"] == manifest["frozen_candidate_commit"]
                and receipt["candidate_tree"] == manifest["frozen_candidate_tree"]
                and receipt["manifest_sha256"] == ctx.manifest_sha
                and receipt["scientific_approval"] is False, "cgroup receipt binding")
        utc(receipt["created_utc"])
        expected = manifest["checks"][list(MANIFEST_CHECK_ORDER).index(check_id)][
            "expected"]["wsl"]
        outcomes = receipt["outcomes"]
        require(type(outcomes) is list and outcomes, "cgroup outcomes required")
        for outcome in outcomes:
            require(type(outcome) is dict and type(outcome.get("command")) is str,
                    "cgroup outcome identity")
            isolation = outcome.get("isolation")
            require(type(isolation) is dict
                    and CGROUP_RE.fullmatch(str(isolation.get("path")))
                    and isolation.get("quiescent") is True
                    and isolation.get("cleanup_error") is None
                    and type(isolation.get("memory_peak")) is int
                    and 0 <= isolation["memory_peak"] <= expected["max_memory_bytes"]
                    and type(isolation.get("started_unix")) in {int, float}
                    and type(isolation.get("ended_unix")) in {int, float},
                    "owned cgroup outcome not cleanly isolated")
            require(outcome.get("path_absent_after") is True,
                    "owned cgroup path not absent after command")
        sweep = receipt["final_sweep"]
        require(type(sweep) is dict and sweep.get("swept") is True
                and sweep.get("violations") == [], "final cgroup sweep must be clean")
        windows_q = receipt["windows_quiescence"]
        require(type(windows_q) is dict, "windows quiescence record required")
        if windows_q.get("not_applicable_reason") is not None:
            deferral = windows_q.get("deferred_to")
            require(type(deferral) is str and deferral,
                    "windows-side not-applicable requires an owner-bound deferral record")
            ctx.incomplete(
                check_id,
                "windows-side quiescence deferred to " + deferral
                + "; deferral blocks PASS while Windows checks ran",
                receipts=((name, receipt_sha),), code="INCOMPLETE_WINDOWS_QUIESCENCE")
        else:
            require(type(windows_q.get("mechanism")) is str and windows_q["mechanism"]
                    and windows_q.get("all_exited") is True
                    and type(windows_q.get("attestations")) is list,
                    "windows quiescence attestation mechanism required")
    except Refused as exc:
        ctx.fail(check_id, str(exc), receipts=((name, receipt_sha),))
    ctx.receipt_shas[check_id] = receipt_sha
    violations = []
    base = Path("/sys/fs/cgroup")
    if base.is_dir():
        violations = sorted(p.name for p in base.glob("recursion-foundry-tool-*"))
    else:
        ctx.limitations.append("native cgroup sysfs not observable on this host; "
                               "verdict relies on the retained sweep record")
    ctx.cgroup_verification = {"swept": base.is_dir(), "violations": violations}
    if violations:
        ctx.fail(check_id, "lingering owned cgroups: " + ",".join(violations),
                 receipts=((name, receipt_sha),), code="FAIL_CGROUP_LINGER")
    ctx.record(check_id, "PASS", "clean native cgroup evidence", receipts=((name, receipt_sha),))


# ---------------------------------------------------------------- audits

def audits(ctx):
    manifest = ctx.manifest
    required_members = {ctx.manifest_name,
                        manifest["artifacts"]["freeze_receipt"],
                        manifest["artifacts"]["cgroup_receipt"]}
    for check_id in MANIFEST_CHECK_ORDER:
        if check_id == "clean-cgroup":
            continue
        for host in HOST_CHECKS[check_id]:
            receipt_name, log_name = _receipt_names(check_id, host, HOST_CHECKS[check_id])
            required_members.add(receipt_name)
            required_members.add(log_name)
    owners = set()
    for index, name in enumerate(manifest["artifacts"]["audit_receipts"]):
        check_id = f"ownership-audit-{index + 1}"
        try:
            audit, raw = json_file(ctx.evidence, name, limit=2 * 1024**2, canonical=True)
        except Refused as exc:
            ctx.incomplete(check_id, "audit receipt: " + str(exc), code="INCOMPLETE_EVIDENCE")
        audit_sha = sha(raw)
        try:
            exact_keys(audit, AUDIT_KEYS, "owned audit schema")
            require(audit["schema"] == "recursion-publication-owned-audit/v1"
                    and audit["campaign"] == CAMPAIGN and audit["parent_goal"] == PARENT
                    and audit["attempt"] == manifest["gate_attempt_ordinal"]
                    and audit["candidate"] == manifest["frozen_candidate_commit"]
                    and audit["candidate_tree"] == manifest["frozen_candidate_tree"]
                    and audit["manifest_sha256"] == ctx.manifest_sha,
                    "owned audit binding")
            require(audit["status"] == "OWNED_RETAINED_AUDIT_PASS",
                    "owned audit status")
            owner = audit["owner"]
            require(type(owner) is str and owner == manifest["audit_owners"][index]
                    and owner not in owners
                    and owner != manifest["gate_runner_identity"],
                    "audit owner identity must be distinct and manifest-bound")
            owners.add(owner)
            utc(audit["created_utc"])
            require(audit["source_membership_verified"] is True
                    and audit["quiescence_verified"] is True
                    and audit["scientific_approval"] is False, "audit assertions")
            membership = audit["attempt_membership"]
            require(type(membership) is dict and membership, "audit membership map")
            require(set(required_members) <= set(membership),
                    "audit membership omits gate evidence: "
                    + ",".join(sorted(set(required_members) - set(membership))))
            for rel, digest_value in membership.items():
                safe_rel(rel)
                require(HEX64.fullmatch(str(digest_value)), "membership digest")
                member_raw = file_bytes(ctx.evidence, rel)
                require(sha(member_raw) == digest_value,
                        "audit membership bytes differ: " + rel)
        except Refused as exc:
            ctx.fail(check_id, str(exc), receipts=((name, audit_sha),))
        ctx.audit_shas.append(audit_sha)
        ctx.record(check_id, "PASS", "owned retained audit verified " + owner,
                   receipts=((name, audit_sha),))


# ---------------------------------------------------------------- reviews

def reviews(ctx):
    check_id = "final-reviews-bound"
    manifest = ctx.manifest
    gate_shas = sorted(ctx.receipt_shas.values())
    limitations_sha = sha(manifest["limitations_text"].encode("utf-8"))
    latest_review = None
    seen_reviewers = set()
    sol_reviewers = set()
    review_shas = []
    review_files = []
    for entry in manifest["review_bundle"]["entries"]:
        name = entry["path"]
        try:
            review, raw = json_file(ctx.evidence, name, limit=256 * 1024, canonical=True)
        except Refused as exc:
            ctx.incomplete(check_id, "review file: " + str(exc), code="INCOMPLETE_REVIEWS")
        review_sha = sha(raw)
        try:
            exact_keys(review, REVIEW_KEYS, "review schema")
            require(review["schema"] == "recursion-publication-final-review/v1"
                    and review["campaign"] == CAMPAIGN and review["parent_goal"] == PARENT
                    and review["candidate"] == manifest["frozen_candidate_commit"]
                    and review["candidate_tree"] == manifest["frozen_candidate_tree"]
                    and review["manifest_sha256"] == ctx.manifest_sha
                    and review["bundle_sha256"] == manifest["review_bundle"]["bundle_sha256"],
                    "review binding: " + name)
            require(review["reviewer"] == entry["reviewer"]
                    and review["model"] == entry["model"]
                    and review["effort"] == entry["effort"]
                    and review["route"] == entry["route"], "review identity: " + name)
            require(review["reviewer"] not in seen_reviewers, "duplicate reviewer")
            seen_reviewers.add(review["reviewer"])
            if (review["model"], review["effort"]) == (SAME_MODEL_REVIEW["model"],
                                                      SAME_MODEL_REVIEW["effort"]):
                sol_reviewers.add(review["reviewer"])
            require(sorted(review["gate_receipt_sha256s"]) == gate_shas
                    and len(set(review["gate_receipt_sha256s"]))
                    == len(review["gate_receipt_sha256s"]),
                    "review must bind every gate receipt: " + name)
            require(sorted(review["owned_audit_sha256s"]) == sorted(ctx.audit_shas),
                    "review must bind both owned audits: " + name)
            body_raw = file_bytes(ctx.evidence,
                                  manifest["artifacts"]["reviewed_pr_body"],
                                  limit=2 * 1024**2)
            require(review["pr_body_reviewed_sha256"] == sha(body_raw),
                    "review must bind the reviewed PR body draft: " + name)
            require(review["limitations_sha256"] == limitations_sha,
                    "review must bind the limitations text: " + name)
            require(review["scientific_admission"] == SCIENTIFIC_ADMISSION
                    and review["acceptance"] is False, "review honesty flags: " + name)
            require(type(review["status"]) is str and review["status"], "review status")
            reviewed = utc(review["reviewed_utc"])
            require(reviewed <= ctx.now, "review timestamp: " + name)
            if latest_review is None or reviewed > latest_review:
                latest_review = reviewed
            items = review["items"]
            require(type(items) is dict and set(items) <= REVIEW_ITEM_KEYS,
                    "review item sections: " + name)
            for section, values in items.items():
                require(type(values) is list
                        and all(type(v) is str and v for v in values)
                        and len(set(values)) == len(values),
                        "review items must be unique strings: " + name)
        except Refused as exc:
            ctx.incomplete(check_id, str(exc), code="INCOMPLETE_REVIEWS")
        review_shas.append(review_sha)
        review_files.append((name, review_sha))
    try:
        require(len(sol_reviewers) >= 2,
                "two distinct gpt-5.6-sol xhigh reviews required")
        latest_receipt = None
        for inner in MANIFEST_CHECK_ORDER:
            if inner == "clean-cgroup":
                continue
            for host in HOST_CHECKS[inner]:
                receipt_name, _ = _receipt_names(inner, host, HOST_CHECKS[inner])
                receipt, _ = json_file(ctx.evidence, receipt_name, limit=256 * 1024,
                                       canonical=True)
                finished = utc(receipt["finished_utc"])
                if latest_receipt is None or finished > latest_receipt:
                    latest_receipt = finished
        require(latest_review is not None and latest_receipt is not None
                and latest_review >= latest_receipt,
                "reviews must postdate the latest gate receipt they cite")
    except Refused as exc:
        ctx.incomplete(check_id, str(exc), receipts=tuple(review_files),
                       code="INCOMPLETE_REVIEWS")
    ctx.review_shas = review_shas
    ctx.record(check_id, "PASS", "reviews bound to candidate/manifest/receipts/audits/body",
               receipts=tuple(review_files))


# ------------------------------------------------------------ dispositions

def dispositions(ctx):
    check_id = "disposition-completeness"
    manifest = ctx.manifest
    name = manifest["artifacts"]["disposition_table"]
    try:
        table, raw = json_file(ctx.evidence, name, limit=2 * 1024**2, canonical=True)
    except Refused as exc:
        ctx.incomplete(check_id, "disposition table: " + str(exc),
                       code="INCOMPLETE_DISPOSITIONS")
    table_sha = sha(raw)
    try:
        exact_keys(table, DISPOSITION_KEYS, "disposition table schema")
        require(table["schema"] == "recursion-disposition-table/v1"
                and table["campaign"] == CAMPAIGN and table["parent_goal"] == PARENT
                and table["manifest_sha256"] == ctx.manifest_sha
                and sorted(table["review_sha256s"]) == sorted(ctx.review_shas),
                "disposition table binding")
        rows = table["items"]
        require(type(rows) is list, "disposition items")
        seen = set()
        for row in rows:
            exact_keys(row, DISPOSITION_ITEM_KEYS, "disposition row schema")
            item_id = row["item_id"]
            require(type(item_id) is str and item_id and item_id not in seen,
                    "unique disposition item id")
            seen.add(item_id)
            require(row["disposition"] in DISPOSITIONS, "disposition value")
            require(type(row["reason"]) is str and row["reason"], "disposition reason")
            evidence = row["evidence_sha256"]
            owner = row["owner_record"]
            if row["disposition"] == "fixed-in-candidate":
                require(type(evidence) is str
                        and (HEX64.fullmatch(evidence) or HEX40.fullmatch(evidence)),
                        "fixed-in-candidate requires commit/artifact evidence")
            else:
                require(evidence is None or (type(evidence) is str
                        and (HEX64.fullmatch(evidence) or HEX40.fullmatch(evidence))),
                        "evidence must be null or a digest")
            if row["disposition"] == "deferred-owner-bound":
                require(type(owner) is str and owner,
                        "deferred-owner-bound requires the owning record")
        required = set()
        for entry in manifest["review_bundle"]["entries"]:
            review, _ = json_file(ctx.evidence, entry["path"], limit=256 * 1024,
                                  canonical=True)
            reviewer = review["reviewer"]
            for section in REVIEW_ITEM_KEYS:
                for item in review["items"].get(section, []):
                    required.add(reviewer + ":" + item)
        missing = required - seen
        require(not missing, "review items silently dropped: "
              + "; ".join(sorted(missing))[:1500])
    except Refused as exc:
        ctx.incomplete(check_id, str(exc), code="INCOMPLETE_DISPOSITIONS")
    ctx.disposition_sha = table_sha
    ctx.record(check_id, "PASS", "every review item dispositioned",
               receipts=((name, table_sha),))


# ---------------------------------------------------------------- pr body

def pr_body(ctx):
    check_id = "pr-body-hash-binding"
    manifest = ctx.manifest
    name = manifest["artifacts"]["published_pr_body"]
    try:
        body_raw = file_bytes(ctx.evidence, name, limit=2 * 1024**2)
    except Refused as exc:
        ctx.incomplete(check_id, "published PR body: " + str(exc),
                       code="INCOMPLETE_EVIDENCE")
    body_sha = sha(body_raw)
    try:
        try:
            body = body_raw.decode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise Refused("PR body must be UTF-8") from exc
        draft_raw = file_bytes(ctx.evidence, manifest["artifacts"]["reviewed_pr_body"],
                               limit=2 * 1024**2)
        required_hashes = (
            [manifest["frozen_candidate_commit"], manifest["frozen_candidate_tree"],
             ctx.manifest_sha, ctx.disposition_sha, sha(draft_raw),
             manifest["review_bundle"]["bundle_sha256"]]
            + sorted(ctx.receipt_shas.values()) + sorted(ctx.audit_shas)
            + sorted(ctx.review_shas))
        missing = [value for value in required_hashes if value not in body]
        require(not missing, "PR body omits bound hashes: " + ",".join(missing[:4]))
        require("attempt " + str(manifest["gate_attempt_ordinal"]) in body,
                "PR body must name the gate attempt ordinal")
        require("limitations" in body.lower(), "PR body needs a limitations section")
        for fragment in PR_BODY_BUILTIN_FRAGMENTS:
            require(fragment in body, "PR body missing required fragment: " + fragment)
        policy = manifest["pr_body"]
        require(policy["github_disclaimer"] in body,
                "PR body must state the GitHub evidence disclaimer")
        for fragment in policy["required_fragments"]:
            require(fragment in body, "PR body missing manifest fragment: " + fragment[:80])
        for pattern in PR_BODY_FORBIDDEN:
            require(not pattern.search(body),
                    "PR body claims GitHub-side evidence that does not exist")
        for pattern in policy["forbidden_patterns"]:
            require(not re.search(pattern, body),
                    "PR body matched a manifest forbidden pattern: " + pattern[:120])
    except Refused as exc:
        ctx.fail(check_id, str(exc), code="FAIL_PR_BODY_BINDING")
    ctx.pr_body_sha = body_sha
    ctx.record(check_id, "PASS", "published body binds every evidence hash",
               receipts=((name, body_sha),))


# ---------------------------------------------------------------- verdict

def evaluate(evidence_dir, repo=None, now=None, manifest_name="command-manifest.json",
             activation_source=ACTIVATION_SOURCE):
    """Evaluate one gate attempt.  Returns the canonical verdict record."""
    now = now or _now()
    ctx = Ctx(evidence_dir, repo, now, activation_source)
    code, detail, status = "OK", "", None
    try:
        load_manifest(ctx, manifest_name)
        check_freeze(ctx)
        host_checks(ctx)
        audits(ctx)
        reviews(ctx)
        dispositions(ctx)
        pr_body(ctx)
        if ctx.now + dt.timedelta(seconds=FINALIZATION_RESERVE_SECONDS) >= utc(DEADLINE_UTC):
            ctx.incomplete("verdict", "verdict cannot emit before deadline minus "
                           "finalization reserve", code="INCOMPLETE_DEADLINE")
        if ctx.repo is not None:
            try:
                head = git_text(ctx.repo, "rev-parse", "HEAD")
                tree = git_text(ctx.repo, "rev-parse", "HEAD^{tree}")
                branch = git_text(ctx.repo, "branch", "--show-current")
                clean = git(ctx.repo, "status", "--porcelain=v1", "-z",
                            "--untracked-files=all") == b""
            except Refused as exc:
                raise Abort("FAIL", "FAIL_CANDIDATE_DRIFT",
                            "identity re-check failed: " + str(exc)) from exc
            if (head, tree, branch, clean) != (
                    ctx.manifest["frozen_candidate_commit"],
                    ctx.manifest["frozen_candidate_tree"], BRANCH, True):
                raise Abort("FAIL", "FAIL_CANDIDATE_DRIFT",
                            "candidate drifted between checks and verdict")
        status = "PASS_CONSTRUCTION_ONLY"
    except Abort as exc:
        status, code, detail = exc.status, exc.code, exc.detail
    except Refused as exc:
        status, code, detail = "INCOMPLETE", "INCOMPLETE_EVIDENCE", str(exc)
    except Exception as exc:  # noqa: BLE001 -- fail closed, never silently pass
        status, code, detail = "INCOMPLETE", "INCOMPLETE_GATE_ERROR", \
            type(exc).__name__ + ": " + str(exc)
    checks = [ctx.checks.get(cid, {"id": cid, "status": "SKIPPED_NOT_RUN",
                                   "receipt_sha256": None, "receipts": [],
                                   "detail": "not reached"})
              for cid in CHECK_ORDER]
    verdict = {
        "schema": "recursion-publication-gate-verdict/v1",
        "campaign": CAMPAIGN,
        "parent_goal": PARENT,
        "gate_attempt_ordinal": (ctx.manifest or {}).get("gate_attempt_ordinal"),
        "candidate": (ctx.manifest or {}).get("frozen_candidate_commit"),
        "candidate_tree": (ctx.manifest or {}).get("frozen_candidate_tree"),
        "review_branch": BRANCH,
        "pull_request": PULL_REQUEST,
        "manifest_sha256": ctx.manifest_sha,
        "checks": checks,
        "owned_audit_sha256": list(ctx.audit_shas),
        "review_sha256": list(ctx.review_shas),
        "disposition_table_sha256": ctx.disposition_sha,
        "pr_body_sha256": ctx.pr_body_sha,
        "cgroup_verification": ctx.cgroup_verification,
        "started_utc": now.isoformat().replace("+00:00", "Z"),
        "finished_utc": _now().isoformat().replace("+00:00", "Z"),
        "status": status,
        "code": code,
        "detail": detail,
        "scientific_admission": SCIENTIFIC_ADMISSION,
        "accepted": False,
        "merge_authority": MERGE_AUTHORITY,
        "limitations": ctx.limitations,
    }
    if status == "PASS_CONSTRUCTION_ONLY":
        require(all(entry["status"] == "PASS" for entry in checks),
                "PASS requires every check PASS")
    return verdict


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True,
                        help="retained attempt evidence directory")
    parser.add_argument("--repo", required=True,
                        help="native review-branch workspace for git identity re-checks")
    parser.add_argument("--manifest", default="command-manifest.json",
                        help="manifest path relative to the evidence root")
    parser.add_argument("--activation-source", default=ACTIVATION_SOURCE,
                        help="expected activation source commit")
    parser.add_argument("--emit", default=None,
                        help="exclusive-create path for the verdict record")
    parser.add_argument("--now", default=None,
                        help="ISO-8601 UTC override for evaluation time (testing)")
    args = parser.parse_args(argv)
    now = utc(args.now) if args.now else None
    verdict = evaluate(args.evidence, repo=args.repo, now=now,
                       manifest_name=args.manifest,
                       activation_source=args.activation_source)
    raw = canonical_bytes(verdict) + b"\n"
    if args.emit:
        put_exclusive(args.emit, raw)
    sys.stdout.write(raw.decode("utf-8"))
    return {"PASS_CONSTRUCTION_ONLY": 0, "FAIL": 2}.get(verdict["status"], 3)


if __name__ == "__main__":
    raise SystemExit(main())
