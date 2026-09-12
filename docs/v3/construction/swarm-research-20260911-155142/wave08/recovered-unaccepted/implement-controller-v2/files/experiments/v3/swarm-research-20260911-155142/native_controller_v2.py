"""Fail-closed native admission for the active Recursion scientific campaign.

Second source-only controller candidate (v2).  Relative to the reviewed
controller-proposal-01/native_local.py this source applies the Wave07 focused
delta items D1-D10 plus the independently supportable Grok review
requirements, under the live 5,000,000-unit cumulative ceiling only.  The
rejected 7,000,000-unit dynamic-ceiling plan and the rejected control entry
are unadmitted inputs: no field this controller reads can raise the ceiling,
and the only admitted control target is the not-yet-authored
control_entry_v2.py carrying a mandatory pre-dispatch durable receipt.

Applied changes:

* policy/model revision lineage: policy revision 2 and the exact
  Astra-to-Sol-xhigh model revision propagate into the budget plan, every
  phase manifest, method bundle, both prospective reviews, every
  reservation row and every receipt;
* exact clean-candidate identity adds worktree-root, non-shallow history
  and absent-submodule proofs;
* the exact git-byte source closure requires an exactly declared baseline
  drift set and mandatory membership of the control suite, the control
  entry shim and the model revision;
* prospective budget lineage is a contiguous hash chain, and the only
  admitted control accounting is the additive global-ledger mapping (any
  non-additive collapse or control-narrowing is refused);
* the phase-manifest set must exactly equal the complete planned command
  set before and during every admission;
* control commands must carry a mandatory pre-dispatch receipt schema: the
  exact canonical bytes of this command's own hash-linked, fsynced,
  nonrefundable reservation row are mounted read-only into the sandbox
  before run_command is ever called, the argv names that mount and the
  receipt identity, and the payload contract plus a post-dispatch check
  require the emitted receipt to echo the real ledger row's runtime
  sha256 and ordinal, which cannot be forged from the manifest;
* controller-owned append-only audit ledger gates every dependency mount
  and strictly postdates the producer receipt;
* post-reservation pending/uncertain markers make a controller crash
  crash-detectable while no refund or retry identity exists; and
* the Windows-host-bound inherited 87-command gate obligation is carried
  literally in admission, execution and audit receipts; native PASS
  remains partial validation only.

Incomplete fixed control suites are not plannable: a control command must
declare all 27 retained control calls and an empty unavailable set, since
no admitted incomplete-suite status exists.  Repeats of control commands
are refused because the mandatory per-command receipt binding cannot be
expressed under exact argv repetition.  With the only admitted additive
mapping a single complete suite already exceeds the remaining 76582-unit
margin, so every control-bearing plan refuses at the ceiling check; this
preserves refusal rather than resolving the deficit.

It never launches a provider and it is not a scientific approval.  Once the
missing external manifests and two exact Sol xhigh reviews exist, ``run``
admits one non-retryable command through the unchanged frozen
``foundry_tools.run_command``.  ``audit`` performs a separate
controller-owned retained-byte audit; it does not import or execute
research.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import time


CAMPAIGN = "research-20260911-155142"
PARENT = "goal-recursion-v2-execution-fabric"
BRANCH = "codex/swarm-research-20260911-155142"
ROOT = Path("/opt/recursion-foundry/workspaces/research-20260911-155142")
COMMON_REPO = Path("/opt/recursion-foundry/repo")
WINDOWS_REPO = Path("/mnt/c/Users/Lucas/Documents/GitHub/recursion")
CACHE = Path("/var/lib/recursion-foundry/campaigns/research-20260911-155142")
SELF_REL = "experiments/v3/swarm-research-20260911-155142/native_controller_v2.py"
SELF = ROOT / SELF_REL
FROZEN = Path("/opt/recursion-foundry/source-v3-20260911-155142-r3b")
RUNTIME_MANIFEST = CACHE / "framework-v3-qualification-r3b/frozen-runtime.json"
RUNTIME_RECEIPT = CACHE / "framework-v3-qualification-r3b/receipt.json"
ACTIVATION = CACHE / "activation.json"
POLICY = CACHE / "policy.json"
USAGE = CACHE / "usage.json"
BASELINE_GIT_CLOSURE = CACHE / "source-closure-git-01.json"
BASELINE_INDEPENDENT_CLOSURE = CACHE / "source-closure-independent-01.json"
BUDGET_PLAN = CACHE / "native-scientific-budget-01.json"
BUDGET_HISTORY = CACHE / "native-scientific-budget-history"
SOURCE_CLOSURE = CACHE / "native-source-closure-02.json"
PHASE_ROOT = CACHE / "native-phase-manifests-01"
METHOD_ROOT = CACHE / "native-method-reviews-01"
ATTEMPT_ROOT = CACHE / "native-scientific-attempts-01"
RESERVATION_ROOT = CACHE / "native-scientific-reservations-01"
AUDIT_ROOT = CACHE / "native-owned-retained-audits-01"
LOCK_ROOT = CACHE / "native-scientific-controller-lock-01"

MODEL_REVISION = "docs/v3/construction/swarm-research-20260911-155142/model-revision-01.json"
RESEARCH_ENTRY = "experiments/v3/swarm-research-20260911-155142/research_entry.py"
BOUNDARY = "experiments/v3/swarm-research-20260911-155142/boundary.py"
INVENTORY_AUDIT = "experiments/v3/swarm-research-20260911-155142/inventory_audit.py"
RETAINED_AUDIT = "experiments/v3/swarm-research-20260911-155142/boundary_audit.py"
BOUNDARY_CONTROLS = "experiments/v3/swarm-research-20260911-155142/boundary_controls.py"
CONTROL_ENTRY = "experiments/v3/swarm-research-20260911-155142/control_entry_v2.py"
KERNEL = "scripts/v3/planning/replay/kernel.py"
ALLOWED_SOURCE_ROOTS = ("docs/v3/construction/swarm-research-20260911-155142/",
                        "experiments/v3/swarm-research-20260911-155142/")

START = dt.datetime.fromisoformat("2026-09-11T15:51:42+00:00")
END = dt.datetime.fromisoformat("2026-09-11T23:51:42+00:00")
DISPATCH_END = dt.datetime.fromisoformat("2026-09-11T21:01:42+00:00")
INHERITED = 3_823_610
CEILING = 5_000_000
FULL_GATE_PAIR = 655_520
FIXTURE_RESERVE = 4_096
PAYLOAD_LIMIT = 900_000
MAX_SECONDS = 60
MAX_INPUT = 32 * 1024**2
MAX_OUTPUT = 1024 * 1024
MAX_ATTEMPT = 256 * 1024**2
JOB_BYTES = 2 * 1024**3
RESERVE_BYTES = 3 * 1024**3
MAX_TELEMETRY_AGE = 900
MAX_BUDGET_LINEAGE = 32
MAX_UNCERTAIN_BYTES = 256 * 1024
QUOTA_RESETS = {"codex-primary": 1789692198}

EXPECTED_POLICY_REVISION = 2
GATE_OBLIGATION = "WINDOWS_HOST_BOUND_NOT_SATISFIED_BY_NATIVE_RECEIPT"
INHERITED_GATE_OBLIGATION = {"status": "PENDING_WINDOWS_HOST_RECEIPTS", "commands": 87,
                             "includes_batch07": True, "portable_to_native": False}
CONTROL_LEDGER_MAPPING = {"mapping": "additive-global-ledger",
                          "reservation_units_are_not_additive": False}
CONTROL_RECEIPT_SCHEMA = "recursion-native-control-pre-dispatch-receipt/v1"
RETAINED_CONTROL_COUNT = 27
WITNESS_DEPENDENT_RETAINED = frozenset({
    "duplicate-case", "cross-unit-case", "journal-only-generation-disagreement",
    "false-q-invocation-on-refused-attestation", "dropped-refusal-event-structural",
    "cross-case-stage-proof", "staged-identity-misused-as-authority"})

PYTHON = Path("/usr/bin/python3.12")
PYTHON_SHA256 = "e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f"
RUNTIME_MANIFEST_SHA256 = "b6dab5d5d9a9dae2db40e51df50440b1d73fc7a15410fbd8605268bd5a002ecd"
RUNTIME_RECEIPT_SHA256 = "0780ea9994f76f3615e40193b7d63a3e4904727730972e2ed5f06b5c07d95898"
BASELINE_GIT_SHA256 = "52cb4fd9c1cedcb24a2ef99ca61880fcb8917a4f9271fe1c29263d2cd27033e5"
BASELINE_INDEPENDENT_SHA256 = "72a91154144f284ddeeb401dd0cb5b2aa9a1d48071b5e66c9f66e8d5ecc19fb8"

ID_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?")
HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")
CGROUP_RE = re.compile(r"/sys/fs/cgroup/recursion-foundry-tool-[0-3]")
WINDOWS_RESERVED = {"con", "prn", "aux", "nul",
                    *(f"com{i}" for i in range(10)), *(f"lpt{i}" for i in range(10))}

ACTIVATION_KEYS = {
    "campaign", "parent_goal", "start_utc", "deadline_utc", "source_commit",
    "review_branch", "native_workspace", "native_evidence", "authority",
    "allowed_roots", "framework_fix_roots", "models", "inherited_charge",
    "budget_revision", "cumulative_limit", "initial_wave_model_state_reservation",
    "research_execution_admitted", "rolling_reserve", "quota_observation",
    "retained_unknown_provider_slots", "initial_worker_slots", "machine_command_slots",
    "non_goals", "validation_obligation",
}
POLICY_KEYS = {
    "revision", "parent_goal", "campaign", "recorded_utc", "immutable_start_utc",
    "immutable_deadline_utc", "inherited_charged_units", "cumulative_ceiling",
    "quota_reserve_percentage_points", "finalization_reserve_seconds",
    "full_gate_admission_seconds", "gate_state_reserve", "reason",
    "new_research_execution_admitted", "historical_gate_portability",
    "unknown_provider_reservations",
}
EXECUTION_KEYS = {
    "schema", "campaign", "parent_goal", "candidate", "candidate_tree", "command_id", "role",
    "phase_manifest_sha256", "budget_plan_sha256", "activation_sha256", "policy_sha256",
    "policy_revision", "budget_revision",
    "model_revision_sha256", "source_closure_sha256", "controller_sha256",
    "reservation_sha256", "reservation_ordinal", "accounting", "argv", "seconds",
    "started_utc", "finished_utc", "status", "scientific_approval", "full_gate_equivalence",
    "input_membership", "dependency_membership", "review_membership", "admission_sha256",
    "outcome", "stdout_sha256", "stderr_sha256", "output_sha256", "payload_sha256",
    "postcheck_failures", "error", "attempt_membership", "attempt_bytes",
    "inherited_full_gate_obligation",
}
ADMISSION_KEYS = {
    "schema", "campaign", "parent_goal", "candidate", "candidate_tree", "command_id", "role",
    "phase_manifest_sha256", "budget_plan_sha256", "activation_sha256", "policy_sha256",
    "policy_revision", "budget_revision",
    "model_revision_sha256", "source_closure_sha256", "controller_sha256",
    "reservation_sha256", "reservation_ordinal", "accounting", "argv", "seconds",
    "input_membership", "dependency_membership", "review_membership", "status", "admitted_utc",
    "refundable", "scientific_approval", "full_gate_equivalence",
    "inherited_full_gate_obligation", "pre_dispatch_receipt",
}
OWNED_AUDIT_KEYS = {
    "schema", "campaign", "parent_goal", "candidate", "candidate_tree", "command_id",
    "producer_role", "phase_manifest_sha256", "budget_plan_sha256", "controller_sha256",
    "source_closure_sha256", "execution_sha256", "reservation_sha256", "reservation_ordinal",
    "admission_sha256", "output_sha256", "attempt_membership", "source_membership_verified",
    "quiescence_verified", "audit_ordinal", "previous_audit_sha256",
    "policy_revision", "budget_revision", "inherited_full_gate_obligation",
    "created_utc", "status", "scientific_approval",
}
ROLES = {"inventory", "inventory-auditor", "explore", "retained-auditor", "control", "repeat"}
TYPE_NAMES = {"null", "bool", "int", "float", "str", "list", "object"}


class Refused(ValueError):
    pass


def require(value, reason):
    if not value:
        raise Refused(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def now():
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
    require(type(raw) is bytes and not raw.startswith(b"\xef\xbb\xbf"), "UTF-8 JSON without BOM required")

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


def safe_rel(value):
    require(type(value) is str and 0 < len(value) <= 240, "bounded relative path required")
    path = PurePosixPath(value)
    require(not path.is_absolute() and str(path) == value and all(
        re.fullmatch(r"[A-Za-z0-9_.-]+", part) and part not in {".", ".."}
        and not part.startswith(".") and not part.endswith((".", " "))
        and part.lower().split(".")[0] not in WINDOWS_RESERVED for part in path.parts),
        "canonical portable relative path required")
    return value


def fixed_file(path, limit=40 * 1024**2, root=None, canonical=False):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), "missing/nonregular/symlink file: " + str(path))
    resolved = path.resolve(strict=True)
    if root is not None:
        require(resolved.is_relative_to(Path(root).resolve(strict=True)), "file escapes fixed root")
    size = resolved.stat().st_size
    require(0 < size <= limit, "file outside byte bound: " + str(path))
    raw = resolved.read_bytes()
    value = strict_json(raw)
    if canonical:
        require(raw == canonical_bytes(value) + b"\n", "external record is not exact canonical JSON")
    return value, raw


def put_exclusive(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    require(path.parent.resolve() == path.parent and not path.parent.is_symlink(), "noncanonical output parent")
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


def git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.STDOUT,
                                       timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Refused("git observation failed: " + " ".join(args)) from exc


def git_text(*args):
    return git(*args).decode("utf-8", errors="strict").strip()


def exact_keys(value, keys, reason):
    require(type(value) is dict and set(value) == set(keys), reason)


def validate_activation(value):
    exact_keys(value, ACTIVATION_KEYS, "actual flat activation schema changed")
    require(value["campaign"] == CAMPAIGN and value["parent_goal"] == PARENT,
            "activation identity")
    require(value["start_utc"] == "2026-09-11T15:51:42Z"
            and value["deadline_utc"] == "2026-09-11T23:51:42Z", "activation clock")
    require(value["source_commit"] == "235aaa7e76095ee18460d9b7ba7a6a8bad1005ac"
            and value["review_branch"] == BRANCH, "activation git identity")
    require(value["native_workspace"] == str(ROOT) and value["native_evidence"] == str(CACHE),
            "activation native paths")
    require(value["allowed_roots"] == [
        "docs/v3/construction/swarm-research-20260911-155142/",
        "experiments/v3/swarm-research-20260911-155142/"], "activation write roots")
    require(value["framework_fix_roots"] == ["tools/construction_swarm/",
            "docs/v3/construction-swarm/"], "activation framework roots")
    require(value["inherited_charge"] == INHERITED and value["cumulative_limit"] == CEILING,
            "activation accounting")
    require(value["budget_revision"] == 1 and value["research_execution_admitted"] is False,
            "activation remains immutable historical record")
    require(value["machine_command_slots"] == 4, "four qualified command slots")
    return value


def validate_policy(value):
    exact_keys(value, POLICY_KEYS, "policy schema changed")
    require(value["campaign"] == CAMPAIGN and value["parent_goal"] == PARENT,
            "policy identity")
    require(value["revision"] == EXPECTED_POLICY_REVISION, "policy lineage revision")
    require(START < utc(value["recorded_utc"]) <= now(),
            "policy recorded inside campaign window")
    require(value["immutable_start_utc"] == "2026-09-11T15:51:42Z"
            and value["immutable_deadline_utc"] == "2026-09-11T23:51:42Z", "policy clock")
    require(value["inherited_charged_units"] == INHERITED
            and value["cumulative_ceiling"] == CEILING, "policy inherited accounting")
    require(value["gate_state_reserve"] == FULL_GATE_PAIR,
            "655520 is the complete inherited two-gate pair reserve")
    require(value["finalization_reserve_seconds"] == 10_200
            and value["full_gate_admission_seconds"] == 4_800, "policy time reserve")
    require(value["full_gate_admission_seconds"] * 2 + 600
            == value["finalization_reserve_seconds"],
            "inherited two-gate Windows reserve arithmetic")
    require(type(value["quota_reserve_percentage_points"]) is int
            and value["quota_reserve_percentage_points"] > 0, "quota reserve")
    require(type(value["unknown_provider_reservations"]) is str,
            "held unknown-provider reservation statement")
    require(value["new_research_execution_admitted"] is False
            and value["historical_gate_portability"].startswith("BLOCKED:"),
            "native work is not historical full-gate approval")
    return value


def validate_model_revision(value):
    exact_keys(value, {"campaign", "parent_goal", "recorded_utc", "owner_instruction",
                       "supersedes", "effective", "clock", "effects", "unchanged"},
               "model revision schema")
    require(value["campaign"] == CAMPAIGN and value["parent_goal"] == PARENT,
            "model revision identity")
    require(value["supersedes"] == {"lead": "gpt-6-astra high standard",
            "same_model_independent_review": "gpt-6-astra"},
            "model lineage supersedes exactly Astra")
    require(value["effective"] == {"lead": "gpt-5.6-sol xhigh",
            "same_model_independent_review": "gpt-5.6-sol xhigh",
            "worker": "swe-2-max",
            "coordinator": "cursor-grok-4.5-high NON-FAST",
            "explicit_coordinator_alternative":
                "opencode-go/muse-spark-1.3-contributor only as previously authorized"},
            "exact Sol-era effective model set")
    require(value["clock"] == {"start_utc": "2026-09-11T15:51:42Z",
            "hard_deadline_utc": "2026-09-11T23:51:42Z", "restarted": False},
            "model revision did not restart clock")
    require(START <= utc(value["recorded_utc"]) <= now(),
            "model revision inside campaign window")
    require({"scientific scope and acceptance obligations",
             "native WSL execution boundary",
             "held uncertain reservations",
             "included-capacity-only policy",
             "no reset, purchase, merge or restart"} <= set(value["unchanged"]),
            "model revision preserved obligations")
    return value


def validate_usage(policy):
    value, raw = fixed_file(USAGE, limit=64 * 1024)
    exact_keys(value, {"checked_utc", "binding_windows", "remaining_percent",
                       "reset_credits_used", "new_metered_spend", "source"}, "usage schema")
    checked = utc(value["checked_utc"])
    age = (now() - checked).total_seconds()
    require(0 <= age <= MAX_TELEMETRY_AGE, "quota telemetry is not current <=900s")
    windows = value["binding_windows"]
    require(type(windows) is list and len(windows) == 1, "exact binding quota window")
    window = windows[0]
    exact_keys(window, {"name", "used_percent", "remaining_percent", "resets_at"},
               "quota window schema")
    require(type(window["used_percent"]) is int and type(window["remaining_percent"]) is int
            and 0 <= window["used_percent"] < 100
            and window["remaining_percent"] == 100 - window["used_percent"],
            "usable exact quota percentages")
    require({window["name"]: window["resets_at"]} == QUOTA_RESETS
            and now().timestamp() < window["resets_at"], "unchanged pre-reset quota identity")
    require(value["remaining_percent"] == window["remaining_percent"]
            and value["remaining_percent"] > policy["quota_reserve_percentage_points"],
            "rolling quota reserve")
    require(value["reset_credits_used"] == 0 and value["new_metered_spend"] == 0,
            "included capacity only")
    return value, sha(raw)


def validate_runtime():
    require(Path(__file__).resolve() == SELF and SELF.is_file() and not SELF.is_symlink(),
            "controller must execute only from its fixed reviewed path")
    require(Path(sys.executable).resolve() == PYTHON and sha(PYTHON.read_bytes()) == PYTHON_SHA256,
            "fixed qualified Python interpreter")
    manifest, raw = fixed_file(RUNTIME_MANIFEST, limit=128 * 1024)
    require(sha(raw) == RUNTIME_MANIFEST_SHA256, "frozen runtime manifest pin")
    exact_keys(manifest, {"source", "candidate", "files", "qualification_receipt_sha256",
                          "original_runtime_unchanged"}, "runtime manifest schema")
    require(manifest["source"] == str(FROZEN)
            and manifest["candidate"] == "dc6e8d02a2ae371f22e054ca4bea3e21163f5f85"
            and manifest["qualification_receipt_sha256"] == RUNTIME_RECEIPT_SHA256
            and manifest["original_runtime_unchanged"] is True, "fixed runtime identity")
    require(FROZEN.is_dir() and not FROZEN.is_symlink() and FROZEN.resolve() == FROZEN,
            "canonical frozen runtime root")
    found = {p.relative_to(FROZEN).as_posix(): sha(p.read_bytes())
             for p in (FROZEN / "tools").rglob("*.py") if p.is_file() and not p.is_symlink()}
    require(found == manifest["files"], "exact frozen Python runtime membership")
    receipt, receipt_raw = fixed_file(RUNTIME_RECEIPT, limit=256 * 1024)
    require(sha(receipt_raw) == RUNTIME_RECEIPT_SHA256
            and receipt["candidate"] == manifest["candidate"] and receipt["exit_code"] == 0
            and receipt["sources"] == manifest["files"]
            and receipt["scientific_research_executed"] is False
            and receipt["provider_dispatches"] == 0, "qualified frozen runtime receipt")
    require(not any(name == "tools" or name.startswith("tools.") for name in sys.modules),
            "trusted tools imported before pin verification")
    sys.path.insert(0, str(FROZEN))
    modules = {}
    for name in ("tools.construction_swarm.ledger", "tools.construction_swarm.capacity",
                 "tools.construction_swarm.foundry_tools"):
        module = importlib.import_module(name)
        origin = Path(module.__file__).resolve()
        relative = origin.relative_to(FROZEN).as_posix()
        require(manifest["files"].get(relative) == sha(origin.read_bytes()),
                "import escaped pinned runtime")
        modules[name.rsplit(".", 1)[1]] = module
    return modules


def marker_paths():
    roots = (ROOT, COMMON_REPO, WINDOWS_REPO, CACHE, FROZEN)
    return tuple(path for root in roots for path in (root / "PAUSE", root / "STOP",
                                                      root / "state/PAUSE", root / "state/STOP"))


def parent_active():
    path = ROOT / "state/goals" / (PARENT + ".md")
    require(path.is_file() and not path.is_symlink(), "active parent goal record missing")
    fields = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            if key in {"id", "status"}:
                fields[key] = value
    require(fields == {"id": PARENT, "status": "active"}, "parent goal is not active")


def resource_check(capacity):
    require(capacity.free_memory() >= JOB_BYTES + RESERVE_BYTES, "less than 5GiB free RAM")
    require(shutil.disk_usage(CACHE).free >= 1024**3, "less than 1GiB evidence disk")


def scope(candidate, activation):
    require(ROOT.is_dir() and not ROOT.is_symlink() and ROOT.resolve() == ROOT,
            "fixed canonical native workspace")
    require(COMMON_REPO.is_dir() and COMMON_REPO.resolve() == COMMON_REPO,
            "fixed common repository")
    require(git_text("rev-parse", "--git-common-dir") == str(COMMON_REPO / ".git"),
            "unexpected git common directory")
    require(git_text("rev-parse", "--show-toplevel") == str(ROOT),
            "candidate worktree root")
    require(git_text("rev-parse", "--is-shallow-repository") == "false",
            "shallow clone cannot prove ancestry")
    require(not (ROOT / ".gitmodules").exists(),
            "submodule state cannot be proven clean")
    require(git_text("rev-parse", "HEAD") == candidate and HEX40.fullmatch(candidate),
            "exact candidate HEAD")
    require(git("status", "--porcelain=v1", "-z", "--untracked-files=all") == b"",
            "candidate workspace is not exactly clean")
    require(git_text("branch", "--show-current") == BRANCH, "wrong review branch")
    require(git_text("cat-file", "-t", candidate) == "commit", "candidate commit missing")
    base = activation["source_commit"]
    require(git_text("merge-base", base, candidate) == base, "candidate ancestry base changed")
    try:
        subprocess.check_call(["git", "merge-base", "--is-ancestor", base, candidate], cwd=ROOT,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Refused("activation source is not candidate ancestor") from exc
    require(git("rev-list", "--merges", base + ".." + candidate).strip() == b"",
            "merge commit in exact campaign ancestry")
    changed = git_text("diff", "--name-only", base, candidate).splitlines()
    roots = tuple(activation["allowed_roots"] + activation["framework_fix_roots"])
    require(all(path.startswith(roots) for path in changed), "candidate changed protected path")
    require(git("diff", "--name-only", "--diff-filter=D", base, candidate).strip() == b"",
            "candidate deletes inherited path")
    parent_active()
    require(not any(path.exists() for path in marker_paths()), "PAUSE/STOP marker present")


def validate_source_closure(value, raw, candidate, tree):
    exact_keys(value, {"schema", "campaign", "parent_goal", "candidate", "candidate_tree",
                       "baseline_git_closure_sha256", "baseline_independent_closure_sha256",
                       "baseline_drift_paths", "files", "file_count", "total_bytes",
                       "third_party_runtime", "external_schema_references", "limitations"},
               "source closure schema")
    require(value["schema"] == "recursion-native-source-closure/v1"
            and value["campaign"] == CAMPAIGN and value["parent_goal"] == PARENT
            and value["candidate"] == candidate and value["candidate_tree"] == tree,
            "source closure candidate identity")
    require(value["baseline_git_closure_sha256"] == BASELINE_GIT_SHA256
            and value["baseline_independent_closure_sha256"] == BASELINE_INDEPENDENT_SHA256,
            "baseline closure bindings")
    baseline, baseline_raw = fixed_file(BASELINE_GIT_CLOSURE, limit=4 * 1024**2)
    independent, independent_raw = fixed_file(BASELINE_INDEPENDENT_CLOSURE, limit=4 * 1024**2)
    require(sha(baseline_raw) == BASELINE_GIT_SHA256
            and sha(independent_raw) == BASELINE_INDEPENDENT_SHA256
            and baseline["independent_artifact_sha256"] == BASELINE_INDEPENDENT_SHA256,
            "preserved independent/Git baseline closure pair")
    declared_drift = value["baseline_drift_paths"]
    require(type(declared_drift) is list and declared_drift == sorted(set(declared_drift))
            and all(path.startswith(ALLOWED_SOURCE_ROOTS)
                    for path in map(safe_rel, declared_drift)),
            "declared baseline drift paths")
    files = value["files"]
    require(type(files) is list and 55 <= len(files) <= 200, "bounded complete source closure")
    paths, total = [], 0
    records = {}
    for row in files:
        exact_keys(row, {"path", "git_blob", "sha256", "bytes"}, "source member schema")
        path = safe_rel(row["path"])
        require(path not in records and HEX40.fullmatch(row["git_blob"])
                and HEX64.fullmatch(row["sha256"])
                and type(row["bytes"]) is int and 0 < row["bytes"] <= 2 * 1024**2,
                "source member identity")
        source = git("show", candidate + ":" + path)
        require(len(source) == row["bytes"] and sha(source) == row["sha256"]
                and git_text("rev-parse", candidate + ":" + path) == row["git_blob"],
                "source closure differs from exact candidate bytes")
        try:
            source.decode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise Refused("research source is not UTF-8 text: " + path) from exc
        paths.append(path)
        records[path] = row
        total += len(source)
    require(paths == sorted(paths) and len(set(paths)) == len(paths), "sorted unique source closure")
    require(value["file_count"] == len(files) and value["total_bytes"] == total
            and total <= 2 * 1024**2, "source closure count/byte bound")
    baseline_rows = {row["path"]: row for row in baseline["files"]}
    require(set(baseline_rows) <= set(records), "baseline source path omitted")
    drifted = {path for path, row in baseline_rows.items()
               if records[path]["sha256"] != row["sha256"]}
    require(drifted == set(declared_drift), "declared baseline drift set exact")
    new_paths = set(records) - set(baseline_rows)
    require(all(path.startswith(ALLOWED_SOURCE_ROOTS) for path in new_paths),
            "non-baseline source outside allowed roots")
    require({RESEARCH_ENTRY, BOUNDARY, INVENTORY_AUDIT, RETAINED_AUDIT, BOUNDARY_CONTROLS,
             CONTROL_ENTRY, KERNEL, MODEL_REVISION} <= set(records),
            "required wrapper/research/auditor/control/kernel source omitted")
    require(value["third_party_runtime"] == independent["third_party_runtime"]
            and value["external_schema_references"] == independent["external_schema_references"],
            "preserved external/runtime closure metadata")
    return records


def accounting_units(accounting):
    require(type(accounting) is dict and 2 <= len(accounting) <= 8
            and accounting.get("planning_fixture_calls") == FIXTURE_RESERVE,
            "each scientific command reserves 4096 fixture calls")
    require(all(type(key) is str and re.fullmatch(r"[a-z][a-z0-9_]{0,63}", key)
                and type(value) is int and value >= 0 for key, value in accounting.items()),
            "typed nonnegative mixed-unit accounting")
    require(sum(value for key, value in accounting.items() if key != "planning_fixture_calls") > 0,
            "positive non-fixture scientific charge required")
    return sum(accounting.values())


def validate_budget_lineage(value, depth=0):
    revision = value["budget_revision"]
    require(type(revision) is int and revision >= 1, "budget revision ordinal")
    require(depth <= MAX_BUDGET_LINEAGE, "budget lineage depth bound")
    supersedes = value["supersedes_budget_sha256"]
    if revision == 1:
        require(supersedes is None, "revision-1 budget plan supersedes nothing")
        return
    require(type(supersedes) is str and HEX64.fullmatch(supersedes),
            "budget lineage supersedes hash")
    ancestor_path = BUDGET_HISTORY / f"{revision - 1:06d}.json"
    require(ancestor_path.is_file() and not ancestor_path.is_symlink(),
            "budget lineage supersedes file missing")
    ancestor, ancestor_raw = fixed_file(ancestor_path, limit=1024 * 1024,
                                        root=BUDGET_HISTORY, canonical=True)
    require(sha(ancestor_raw) == supersedes, "budget lineage supersedes hash binding")
    require(type(ancestor) is dict and ancestor.get("campaign") == CAMPAIGN
            and ancestor.get("parent_goal") == PARENT
            and ancestor.get("budget_revision") == revision - 1,
            "budget lineage ordinal chain")
    validate_budget_lineage(ancestor, depth + 1)


def control_invocation_totals(commands):
    totals = {"outer_binding_calls": 0, "inventory_auditor_calls": 0,
              "retained_auditor_calls": 0, "planning_fixture_calls": 0}
    for row in commands:
        if row["role"] == "control":
            totals["outer_binding_calls"] += 3
            totals["inventory_auditor_calls"] += 7
            totals["retained_auditor_calls"] += 1 + RETAINED_CONTROL_COUNT
            totals["planning_fixture_calls"] += FIXTURE_RESERVE
    return totals


def validate_budget_plan(value, candidate, tree, activation_sha, policy_sha, policy_revision,
                         model_pin, closure_sha, controller_sha):
    exact_keys(value, {"schema", "campaign", "parent_goal", "candidate", "candidate_tree",
                       "activation_sha256", "policy_sha256", "policy_revision",
                       "budget_revision", "supersedes_budget_sha256", "model_revision",
                       "source_closure_sha256", "controller_sha256", "quota_reset_identities",
                       "control_ledger_mapping", "inherited_gate_obligation",
                       "full_gate_pair_units", "commands", "obligations"}, "budget plan schema")
    require(value["schema"] == "recursion-native-scientific-budget/v1"
            and value["campaign"] == CAMPAIGN and value["parent_goal"] == PARENT
            and value["candidate"] == candidate and value["candidate_tree"] == tree,
            "budget plan candidate identity")
    require(value["activation_sha256"] == activation_sha
            and value["policy_sha256"] == policy_sha
            and value["policy_revision"] == policy_revision
            and value["model_revision"] == model_pin
            and value["source_closure_sha256"] == closure_sha
            and value["controller_sha256"] == controller_sha
            and value["quota_reset_identities"] == QUOTA_RESETS, "budget plan exact bindings")
    require(value["control_ledger_mapping"] == CONTROL_LEDGER_MAPPING,
            "only the additive global-ledger control mapping is admitted")
    require(value["inherited_gate_obligation"] == INHERITED_GATE_OBLIGATION,
            "inherited_gate_obligation")
    validate_budget_lineage(value)
    require(value["full_gate_pair_units"] == FULL_GATE_PAIR, "full gate pair reserved exactly once")
    commands = value["commands"]
    require(type(commands) is list and 6 <= len(commands) <= 128, "finite complete command plan")
    seen, rows = set(), {}
    for row in commands:
        exact_keys(row, {"id", "role", "accounting", "depends_on", "repeat_of",
                         "history_indices"}, "budget command schema")
        command_id = row["id"]
        require(type(command_id) is str and ID_RE.fullmatch(command_id) and command_id not in seen,
                "unique command id")
        require(row["role"] in ROLES, "known command role")
        accounting_units(row["accounting"])
        require(type(row["depends_on"]) is list and len(row["depends_on"]) <= 32
                and len(set(row["depends_on"])) == len(row["depends_on"])
                and all(dep in seen for dep in row["depends_on"]), "ordered acyclic dependencies")
        indices = row["history_indices"]
        require(type(indices) is list and len(indices) <= 24
                and len(set(indices)) == len(indices)
                and all(type(index) is int and 0 <= index < 384 for index in indices),
                "bounded exact history indices")
        if row["role"] == "repeat":
            require(row["repeat_of"] in seen
                    and rows[row["repeat_of"]]["role"] not in {"repeat", "control"},
                    "repeat binds earlier non-repeat non-control command")
            original = rows[row["repeat_of"]]
            require(row["accounting"] == original["accounting"]
                    and row["history_indices"] == original["history_indices"],
                    "repeat carries full original charge")
        else:
            require(row["repeat_of"] is None, "only repeat has repeat_of")
            if row["role"] in {"explore", "retained-auditor", "control"}:
                require(indices, "history-bearing role needs indices")
            else:
                require(not indices, "non-history role cannot claim indices")
        seen.add(command_id)
        rows[command_id] = row
    obligations = value["obligations"]
    exact_keys(obligations, {"all_new_remaining_charges_included", "audit_command_ids",
                             "control_command_ids", "repeat_command_ids",
                             "control_invocation_totals"}, "budget obligations")
    require(obligations["all_new_remaining_charges_included"] is True, "remaining charges incomplete")
    require(obligations["audit_command_ids"] == [r["id"] for r in commands
            if r["role"] in {"inventory-auditor", "retained-auditor"}], "audit charge list")
    require(obligations["control_command_ids"] == [r["id"] for r in commands
            if r["role"] == "control"], "control charge list")
    require(obligations["repeat_command_ids"] == [r["id"] for r in commands
            if r["role"] == "repeat"], "repeat charge list")
    require(obligations["audit_command_ids"] and obligations["control_command_ids"]
            and len(obligations["repeat_command_ids"]) >= 2, "audits, controls and two repeats required")
    require(obligations["control_invocation_totals"] == control_invocation_totals(commands),
            "control invocation totals differ from additive command plan")
    grand = INHERITED + FULL_GATE_PAIR + sum(accounting_units(row["accounting"]) for row in commands)
    require(grand <= CEILING, "complete mixed-unit plan exceeds cumulative ceiling")
    return rows, grand


def pointer(value, path):
    require(type(path) is str and path.startswith("/") and len(path) <= 240, "JSON pointer")
    current = value
    for token in path[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if type(current) is dict:
            require(token in current, "missing payload pointer: " + path)
            current = current[token]
        elif type(current) is list and token.isdigit():
            index = int(token)
            require(index < len(current), "payload pointer index")
            current = current[index]
        else:
            raise Refused("invalid payload pointer: " + path)
    return current


def type_name(value):
    if value is None:
        return "null"
    if type(value) is bool:
        return "bool"
    if type(value) is int:
        return "int"
    if type(value) is float:
        return "float"
    if type(value) is str:
        return "str"
    if type(value) is list:
        return "list"
    if type(value) is dict:
        return "object"
    raise Refused("unsupported JSON value type")


def validate_contract(contract, payload):
    exact_keys(contract, {"exact_keys", "required_values", "required_types", "required_lengths"},
               "payload contract schema")
    require(type(contract["required_values"]) is dict and type(contract["required_types"]) is dict
            and type(contract["required_lengths"]) is dict, "payload contract maps")
    keys = contract["exact_keys"]
    require(type(keys) is list and keys == sorted(set(keys))
            and all(type(key) is str for key in keys), "exact sorted payload keys")
    require(type(payload) is dict and set(payload) == set(keys), "exact payload top-level shape")
    for path, expected in contract["required_values"].items():
        require(pointer(payload, path) == expected
                and type(pointer(payload, path)) is type(expected), "payload value: " + path)
    for path, expected in contract["required_types"].items():
        require(expected in TYPE_NAMES and type_name(pointer(payload, path)) == expected,
                "payload type: " + path)
    for path, expected in contract["required_lengths"].items():
        value = pointer(payload, path)
        require(type(expected) is int and expected >= 0 and type(value) in {list, dict, str}
                and len(value) == expected, "payload length: " + path)


def required_value(contract, path, expected):
    actual = contract["required_values"].get(path, object())
    require(actual == expected and type(actual) is type(expected), "contract omits required value " + path)


def required_type(contract, path, expected):
    actual = contract["required_types"].get(path, object())
    require(actual == expected, "contract omits required type " + path)


def wrapper_parts(argv, closure):
    require(type(argv) is list and 12 <= len(argv) <= 64
            and all(type(arg) is str and 0 < len(arg) <= 16_384 and "\0" not in arg for arg in argv),
            "bounded exact argv")
    prefix = ["/usr/bin/python3", "-B", RESEARCH_ENTRY, "--fixture-limit", "4096",
              "--target"]
    require(argv[:6] == prefix and argv[7:10] == ["--payload-limit", str(PAYLOAD_LIMIT), "--"],
            "mandatory exact research_entry wrapper argv")
    target = safe_rel(argv[6])
    require(target != RESEARCH_ENTRY and target in closure
            and target.startswith("experiments/v3/swarm-research-20260911-155142/")
            and target.endswith(".py"), "reviewed campaign target")
    return target, argv[10:]


def control_pre_dispatch_receipt(command_id, plan_sha):
    return {"schema": CONTROL_RECEIPT_SCHEMA,
            "receipt_id": "command-reservation/" + command_id,
            "plan_sha256": plan_sha, "refundable": False}


def validate_phase_command(command, planned, rows, closure):
    expected_keys = {"id", "role", "argv", "seconds", "accounting", "dependencies",
                     "payload_contract"}
    if planned["role"] == "control":
        expected_keys = expected_keys | {"control_plan_sha256", "control_invocations",
                                         "unavailable_retained_controls",
                                         "pre_dispatch_receipt"}
    exact_keys(command, expected_keys, "phase command schema")
    require(command["id"] == planned["id"] and command["role"] == planned["role"]
            and command["accounting"] == planned["accounting"], "phase differs from budget plan")
    require(type(command["seconds"]) is int and 1 <= command["seconds"] <= MAX_SECONDS,
            "unchanged run_command <=60s")
    target, args = wrapper_parts(command["argv"], closure)
    dependencies = command["dependencies"]
    require(type(dependencies) is list and len(dependencies) == len(planned["depends_on"]),
            "exact dependency count")
    for expected, dep in zip(planned["depends_on"], dependencies):
        exact_keys(dep, {"command", "mount", "output_sha256", "execution_sha256",
                         "owned_audit_sha256", "producer_phase_sha256"}, "dependency binding schema")
        require(dep["command"] == expected and dep["mount"] == "inputs/" + expected + ".json"
                and all(HEX64.fullmatch(dep[field]) for field in
                        ("output_sha256", "execution_sha256", "owned_audit_sha256",
                         "producer_phase_sha256")), "exact dependency hashes/mount")
    role = planned["role"]
    indices = planned["history_indices"]
    contract = command["payload_contract"]
    if role == "inventory":
        require(target == BOUNDARY and not dependencies and args == ["--mode", "inventory",
                "--symbolic-limit", "40512", "--stdout-limit", str(PAYLOAD_LIMIT)],
                "exact inventory invocation")
        require(command["accounting"] == {"planning_fixture_calls": 4096,
                "symbolic_units": 40512}, "inventory accounting")
        required_value(contract, "/symbolic_units", 40512)
        required_value(contract, "/symbolic_limit", 40512)
        required_value(contract, "/complete_original_profile_execution", False)
        require(contract["required_lengths"].get("/selected") == 192, "inventory membership length")
    elif role == "inventory-auditor":
        producers = [dep for dep in dependencies if rows[dep["command"]]["role"] == "inventory"]
        require(target == INVENTORY_AUDIT and len(producers) == 1 and args == ["--inventory",
                producers[0]["mount"], "--symbolic-limit", "40512", "--expected-producer-limit",
                "40512", "--stdout-limit", str(PAYLOAD_LIMIT)], "exact inventory audit invocation")
        require(command["accounting"] == {"planning_fixture_calls": 4096,
                "symbolic_units": 40512}, "inventory audit accounting")
        required_value(contract, "/status", "INDEPENDENT_INVENTORY_MATCH")
        required_value(contract, "/symbolic_units", 40512)
        required_value(contract, "/source_adapter_histories_executed", 0)
        required_value(contract, "/source_truth_established", False)
    elif role == "explore":
        inventories = [dep for dep in dependencies if rows[dep["command"]]["role"] == "inventory"]
        require(target == BOUNDARY and len(inventories) == 1, "explore needs exact inventory")
        expected_args = ["--mode", "explore", "--symbolic-limit", "192", "--inventory",
                         inventories[0]["mount"], "--indices", ",".join(map(str, indices)),
                         "--state-limit", str(70 * len(indices)), "--stdout-limit", str(PAYLOAD_LIMIT)]
        require(args == expected_args, "exact bounded explore invocation")
        require(command["accounting"] == {"planning_fixture_calls": 4096,
                "representation_visits": 70 * len(indices), "symbolic_units": 192},
                "explore mixed accounting")
        for path, expected in {"/status": "BOUNDED_PARTIAL_SHARD", "/history_indices": indices,
                "/histories": len(indices), "/total_histories": 384, "/symbolic_units": 192,
                "/symbolic_limit": 192, "/state_visits": 70 * len(indices),
                "/state_limit": 70 * len(indices), "/predicted_acceptance_asserted": False,
                "/complete_domain": False, "/reductions_used": False,
                "/source_truth_established": False}.items():
            required_value(contract, path, expected)
        require(contract["required_lengths"].get("/cases") == len(indices), "case count contract")
    elif role == "retained-auditor":
        inventories = [dep for dep in dependencies if rows[dep["command"]]["role"] == "inventory"]
        explores = [dep for dep in dependencies if rows[dep["command"]]["role"] in {"explore", "repeat"}
                    and rows[dep["command"]]["history_indices"] == indices]
        require(target == RETAINED_AUDIT and len(inventories) == len(explores) == 1,
                "retained audit exact inputs")
        charge = 192 + 35 * len(indices)
        expected_args = ["--inventory", inventories[0]["mount"], "--result", explores[0]["mount"],
                         "--indices", ",".join(map(str, indices)), "--charge-limit", str(charge),
                         "--stdout-limit", str(PAYLOAD_LIMIT)]
        require(args == expected_args and command["accounting"] == {
                "planning_fixture_calls": 4096, "retained_audit_units": charge},
                "retained audit argv/accounting")
        required_value(contract, "/auditor", "boundary-retained-auditor")
        required_value(contract, "/ordinals", indices)
        required_value(contract, "/histories", len(indices))
        required_value(contract, "/charged_units", charge)
        required_value(contract, "/model_execution", "none; unchanged check.audit_case typed replay only")
    elif role == "control":
        count = len(indices)
        require(target == CONTROL_ENTRY,
                "reviewed campaign target for controls is the control_entry_v2 shim")
        inventories = [dep for dep in dependencies if rows[dep["command"]]["role"] == "inventory"]
        results = [dep for dep in dependencies
                   if rows[dep["command"]]["role"] in {"explore", "repeat"}
                   and rows[dep["command"]]["history_indices"] == indices]
        require(len(inventories) == len(results) == 1,
                "control binds retained audit exact inputs")
        inventory_dep, result_dep = inventories[0], results[0]
        plan_sha = command["control_plan_sha256"]
        require(type(plan_sha) is str and HEX64.fullmatch(plan_sha),
                "control durable precharge plan hash")
        require(command["control_invocations"] == {
            "outer_binding_calls": 3, "inventory_auditor_calls": 7,
            "retained_auditor_baseline_calls": 1,
            "retained_auditor_control_calls": RETAINED_CONTROL_COUNT,
            "indices": count}, "control invocation accounting declaration")
        unavailable = command["unavailable_retained_controls"]
        require(type(unavailable) is list and not unavailable
                and set(unavailable) <= WITNESS_DEPENDENT_RETAINED,
                "unavailable_retained_controls must be empty; incomplete suites are not plannable")
        require(command["pre_dispatch_receipt"]
                == control_pre_dispatch_receipt(command["id"], plan_sha),
                "mandatory pre-dispatch durable receipt binding")
        require(command["accounting"] == {
            "planning_fixture_calls": FIXTURE_RESERVE,
            "control_units": 3 + 7 * 40512
                + (1 + RETAINED_CONTROL_COUNT) * (192 + 35 * count)},
            "control additive accounting")
        receipt_mount = "inputs/" + command["id"] + ".reservation.json"
        expected_args = ["--inventory", inventory_dep["mount"],
                         "--result", result_dep["mount"],
                         "--indices", ",".join(map(str, indices)),
                         "--expected-producer-limit", "40512",
                         "--command-id", command["id"],
                         "--control-plan-sha256", plan_sha,
                         "--durable-receipt", receipt_mount,
                         "--durable-receipt-schema", CONTROL_RECEIPT_SCHEMA,
                         "--durable-receipt-id", "command-reservation/" + command["id"],
                         "--inventory-input-sha256", inventory_dep["output_sha256"],
                         "--result-input-sha256", result_dep["output_sha256"],
                         "--stdout-limit", str(PAYLOAD_LIMIT)]
        require(args == expected_args, "exact control entry invocation")
        for path, expected in {
            "/status": "COMPLETE_FIXED_CONTROL_SUITE",
            "/all_available_controls_detected": True,
            "/all_required_controls_detected": True,
            "/durable_precharge_plan_sha256": plan_sha,
            "/durable_precharge_receipt/schema": CONTROL_RECEIPT_SCHEMA,
            "/durable_precharge_receipt/receipt_id": "command-reservation/" + command["id"],
            "/durable_precharge_receipt/plan_sha256": plan_sha,
            "/durable_precharge_receipt/refundable": False,
            "/reservation_units_are_not_additive": False,
            "/producer_asserted_controls_accepted": False,
            "/outer_binding_bypassed_for_semantic_controls": True,
            "/original_model_or_reducer_execution_by_runner": False,
            "/runner_source_sha256": closure[BOUNDARY_CONTROLS]["sha256"],
            "/wrapper_fixture_kernel_calls_in_durable_plan": FIXTURE_RESERVE,
            "/expected_indices": indices,
            "/expected_producer_limit": 40512,
            "/inventory_input_sha256": inventory_dep["output_sha256"],
            "/result_input_sha256": result_dep["output_sha256"],
        }.items():
            required_value(contract, path, expected)
        required_type(contract, "/durable_precharge_receipt/reservation_sha256", "str")
        required_type(contract, "/durable_precharge_receipt/reservation_ordinal", "int")
    else:
        original = rows[planned["repeat_of"]]
        require(original["role"] != "control",
                "repeat of a control command cannot rebind its durable receipt")
        original_phase, _ = fixed_file(PHASE_ROOT / (original["id"] + ".json"),
                                       limit=512 * 1024, root=PHASE_ROOT, canonical=True)
        original_command = original_phase.get("command")
        original_target = validate_phase_command(original_command, original, rows, closure)
        require(original["accounting"] == command["accounting"]
                and command["argv"] == original_command["argv"]
                and command["seconds"] == original_command["seconds"]
                and command["dependencies"] == original_command["dependencies"]
                and command["payload_contract"] == original_command["payload_contract"],
                "repeat is exact full-charge command repetition")
        target = original_target
    return target


def load_reviews(command_id, candidate, phase_sha, plan_sha, phase, model_revision,
                 policy_revision, budget_revision):
    bundle_path = METHOD_ROOT / (command_id + ".json")
    bundle, raw = fixed_file(bundle_path, limit=128 * 1024, root=METHOD_ROOT, canonical=True)
    exact_keys(bundle, {"schema", "campaign", "parent_goal", "candidate",
                        "phase_manifest_sha256", "budget_plan_sha256", "controller_sha256",
                        "source_closure_sha256", "policy_sha256", "policy_revision",
                        "budget_revision", "model_revision_sha256",
                        "status", "reviews"}, "method bundle schema")
    require(bundle["schema"] == "recursion-native-method-bundle/v1"
            and bundle["campaign"] == CAMPAIGN and bundle["parent_goal"] == PARENT
            and bundle["candidate"] == candidate and bundle["phase_manifest_sha256"] == phase_sha
            and bundle["budget_plan_sha256"] == plan_sha
            and bundle["controller_sha256"] == phase["controller_sha256"]
            and bundle["source_closure_sha256"] == phase["source_closure_sha256"]
            and bundle["policy_sha256"] == phase["policy_sha256"]
            and bundle["policy_revision"] == policy_revision
            and bundle["budget_revision"] == budget_revision
            and bundle["model_revision_sha256"] == phase["model_revision"]["sha256"]
            and bundle["status"] == "APPROVED_FOR_EXECUTION", "exact method bundle bindings")
    require(type(bundle["reviews"]) is list and len(bundle["reviews"]) == 2,
            "two prospective Sol reviews")
    members, names = [], set()
    revision_time = utc(model_revision["recorded_utc"])
    for member in bundle["reviews"]:
        exact_keys(member, {"path", "sha256"}, "review member schema")
        relative = safe_rel(member["path"])
        require(HEX64.fullmatch(member["sha256"]), "review digest")
        review, review_raw = fixed_file(METHOD_ROOT / relative, limit=64 * 1024,
                                        root=METHOD_ROOT, canonical=True)
        require(sha(review_raw) == member["sha256"], "review byte binding")
        exact_keys(review, {"schema", "campaign", "parent_goal", "candidate",
                            "phase_manifest_sha256", "budget_plan_sha256", "controller_sha256",
                            "source_closure_sha256", "policy_sha256", "policy_revision",
                            "budget_revision", "model_revision_sha256",
                            "model", "effort", "reviewer", "reviewed_utc", "status",
                            "scientific_execution_authorized", "limitations"}, "review schema")
        require(review["schema"] == "recursion-native-sol-review/v1"
                and review["campaign"] == CAMPAIGN and review["parent_goal"] == PARENT
                and review["candidate"] == candidate and review["phase_manifest_sha256"] == phase_sha
                and review["budget_plan_sha256"] == plan_sha
                and review["controller_sha256"] == phase["controller_sha256"]
                and review["source_closure_sha256"] == phase["source_closure_sha256"]
                and review["policy_sha256"] == phase["policy_sha256"]
                and review["policy_revision"] == policy_revision
                and review["budget_revision"] == budget_revision
                and review["model_revision_sha256"] == phase["model_revision"]["sha256"]
                and review["model"] == "gpt-5.6-sol" and review["effort"] == "xhigh"
                and review["status"] == "APPROVE_FOR_EXECUTION"
                and review["scientific_execution_authorized"] is True,
                "prospective exact Sol xhigh execution approval")
        require(type(review["reviewer"]) is str and review["reviewer"] not in names
                and revision_time <= utc(review["reviewed_utc"]) <= now(), "independent review identity/time")
        require(type(review["limitations"]) is list, "review limitations")
        names.add(review["reviewer"])
        members.append({"path": relative, "sha256": member["sha256"],
                        "reviewer": review["reviewer"]})
    return members, sha(raw)


def validate_phase_set(rows):
    require(PHASE_ROOT.is_dir() and not PHASE_ROOT.is_symlink()
            and PHASE_ROOT.resolve() == PHASE_ROOT, "canonical phase manifest root")
    require({path.stem for path in PHASE_ROOT.glob("*.json")} == set(rows),
            "phase manifest set differs from complete budget plan")


def load_context(command_id, capacity=None, dispatch=False):
    require(type(command_id) is str and ID_RE.fullmatch(command_id), "command id")
    activation, activation_raw = fixed_file(ACTIVATION, limit=128 * 1024)
    policy, policy_raw = fixed_file(POLICY, limit=64 * 1024)
    validate_activation(activation)
    validate_policy(policy)
    policy_revision = policy["revision"]
    dispatch_end = END - dt.timedelta(seconds=policy["finalization_reserve_seconds"])
    require(dispatch_end == DISPATCH_END, "policy finalization reserve changed")
    candidate = git_text("rev-parse", "HEAD")
    scope(candidate, activation)
    tree = git_text("rev-parse", candidate + "^{tree}")
    controller_sha = sha(SELF.read_bytes())
    require(sha(git("show", candidate + ":" + SELF_REL)) == controller_sha,
            "controller bytes bound to exact candidate")
    closure, closure_raw = fixed_file(SOURCE_CLOSURE, limit=4 * 1024**2, canonical=True)
    closure_records = validate_source_closure(closure, closure_raw, candidate, tree)
    model_raw = git("show", candidate + ":" + MODEL_REVISION)
    model_revision = strict_json(model_raw)
    validate_model_revision(model_revision)
    model_pin = {"path": MODEL_REVISION,
                 "git_blob": git_text("rev-parse", candidate + ":" + MODEL_REVISION),
                 "sha256": sha(model_raw)}
    plan, plan_raw = fixed_file(BUDGET_PLAN, limit=1024 * 1024, canonical=True)
    rows, grand = validate_budget_plan(plan, candidate, tree, sha(activation_raw),
                                       sha(policy_raw), policy_revision, model_pin,
                                       sha(closure_raw), controller_sha)
    budget_revision = plan["budget_revision"]
    require(command_id in rows, "command absent from complete budget plan")
    validate_phase_set(rows)
    phase_path = PHASE_ROOT / (command_id + ".json")
    phase, phase_raw = fixed_file(phase_path, limit=512 * 1024, root=PHASE_ROOT, canonical=True)
    exact_keys(phase, {"schema", "campaign", "parent_goal", "candidate", "candidate_tree",
                       "budget_plan_sha256", "activation_sha256", "policy_sha256",
                       "policy_revision", "budget_revision", "model_revision",
                       "source_closure_sha256", "controller_sha256", "command_ordinal",
                       "history_indices", "repeat_of", "created_utc", "command"},
               "phase manifest schema")
    require(phase["schema"] == "recursion-native-phase/v1" and phase["campaign"] == CAMPAIGN
            and phase["parent_goal"] == PARENT and phase["candidate"] == candidate
            and phase["candidate_tree"] == tree and phase["budget_plan_sha256"] == sha(plan_raw)
            and phase["activation_sha256"] == sha(activation_raw)
            and phase["policy_sha256"] == sha(policy_raw)
            and phase["policy_revision"] == policy_revision
            and phase["budget_revision"] == budget_revision
            and phase["model_revision"] == model_pin
            and phase["source_closure_sha256"] == sha(closure_raw)
            and phase["controller_sha256"] == controller_sha, "phase exact bindings")
    require(type(phase["command_ordinal"]) is int
            and 0 <= phase["command_ordinal"] < len(plan["commands"])
            and plan["commands"][phase["command_ordinal"]]["id"] == command_id,
            "phase command ordinal")
    require(phase["history_indices"] == rows[command_id]["history_indices"]
            and phase["repeat_of"] == rows[command_id]["repeat_of"],
            "phase plan row echo")
    require(START <= utc(phase["created_utc"]) <= now(),
            "phase created_utc inside campaign UTC window")
    target = validate_phase_command(phase["command"], rows[command_id], rows, closure_records)
    reviews, method_sha = load_reviews(command_id, candidate, sha(phase_raw), sha(plan_raw),
                                       phase, model_revision, policy_revision, budget_revision)
    usage, usage_sha = validate_usage(policy)
    if dispatch:
        require(START <= now() < dispatch_end
                and now() + dt.timedelta(seconds=phase["command"]["seconds"] + 120) < dispatch_end,
                "research dispatch deadline and queue reserve")
    else:
        require(START <= now() < END, "campaign hard deadline")
    if capacity is not None:
        resource_check(capacity)
    return {"activation": activation, "activation_sha": sha(activation_raw), "policy": policy,
            "policy_sha": sha(policy_raw), "policy_revision": policy_revision,
            "budget_revision": budget_revision, "dispatch_end": dispatch_end,
            "candidate": candidate, "tree": tree,
            "controller_sha": controller_sha, "closure": closure_records,
            "closure_sha": sha(closure_raw), "model_revision": model_revision,
            "model_pin": model_pin, "plan": plan, "plan_sha": sha(plan_raw), "rows": rows,
            "grand_total": grand, "phase": phase, "phase_sha": sha(phase_raw),
            "command": phase["command"], "target": target, "reviews": reviews,
            "method_sha": method_sha, "usage_sha": usage_sha}


def read_reservations(ctx):
    RESERVATION_ROOT.mkdir(parents=True, exist_ok=True)
    require(RESERVATION_ROOT.resolve() == RESERVATION_ROOT and not RESERVATION_ROOT.is_symlink(),
            "canonical reservation root")
    files = sorted(RESERVATION_ROOT.glob("*.json"))
    require([p.name for p in files] == [f"{i:06d}.json" for i in range(len(files))],
            "contiguous append-only reservation ledger")
    total, previous, rows = INHERITED, None, []
    for ordinal, path in enumerate(files):
        value, raw = fixed_file(path, limit=64 * 1024, root=RESERVATION_ROOT, canonical=True)
        exact_keys(value, {"schema", "ordinal", "reservation_id", "purpose", "command_id",
                           "candidate", "budget_plan_sha256", "phase_manifest_sha256",
                           "accounting", "reserved_units", "previous_total", "new_total",
                           "previous_sha256", "refundable", "created_utc", "outstanding_units",
                           "budget_revision", "policy_revision", "receipt_id"},
                   "reservation row schema")
        require(value["schema"] == "recursion-native-reservation/v1" and value["ordinal"] == ordinal
                and value["previous_total"] == total and value["previous_sha256"] == previous
                and value["refundable"] is False and value["candidate"] == ctx["candidate"]
                and value["budget_plan_sha256"] == ctx["plan_sha"]
                and value["budget_revision"] == ctx["budget_revision"]
                and value["policy_revision"] == ctx["policy_revision"], "reservation chain binding")
        require(value["receipt_id"] == (None if value["command_id"] is None
                else "command-reservation/" + value["command_id"]),
                "reservation receipt identity")
        require(type(value["reserved_units"]) is int and value["reserved_units"] >= 0
                and value["reserved_units"] == sum(value["accounting"].values()),
                "reservation mixed-unit arithmetic")
        total += value["reserved_units"]
        require(value["new_total"] == total and total <= CEILING, "reservation cumulative total")
        require(value["outstanding_units"] == ctx["grand_total"] - total,
                "reservation retains every future plan charge")
        previous = sha(raw)
        rows.append((value, previous))
    if rows:
        pair = rows[0][0]
        require(pair["purpose"] == "inherited-full-gate-pair" and pair["command_id"] is None
                and pair["phase_manifest_sha256"] is None and pair["receipt_id"] is None
                and pair["accounting"] == {"inherited_full_gate_pair_units": FULL_GATE_PAIR}
                and pair["reserved_units"] == FULL_GATE_PAIR, "single exact inherited gate-pair row")
        require(sum(row[0]["purpose"] == "inherited-full-gate-pair" for row in rows) == 1,
                "full-gate pair reserve appears exactly once")
    command_rows = {row[0]["command_id"]: row for row in rows if row[0]["command_id"] is not None}
    require(len(command_rows) == len(rows) - bool(rows), "unique command reservations")
    for command_id, (row, _) in command_rows.items():
        require(command_id in ctx["rows"] and row["purpose"] == "scientific-command"
                and row["accounting"] == ctx["rows"][command_id]["accounting"],
                "reservation belongs to complete plan")
    return rows, command_rows, total, previous


def append_reservation(ctx, purpose, command_id, phase_sha, accounting, outstanding, previous_total,
                       previous_sha, ordinal):
    row = {"schema": "recursion-native-reservation/v1", "ordinal": ordinal,
           "reservation_id": ("full-gate-pair" if command_id is None else "command/" + command_id),
           "purpose": purpose, "command_id": command_id, "candidate": ctx["candidate"],
           "budget_plan_sha256": ctx["plan_sha"], "phase_manifest_sha256": phase_sha,
           "accounting": accounting, "reserved_units": sum(accounting.values()),
           "previous_total": previous_total,
           "new_total": previous_total + sum(accounting.values()),
           "previous_sha256": previous_sha, "refundable": False,
           "created_utc": now().isoformat(), "outstanding_units": outstanding,
           "budget_revision": ctx["budget_revision"], "policy_revision": ctx["policy_revision"],
           "receipt_id": (None if command_id is None
                          else "command-reservation/" + command_id)}
    raw = canonical_bytes(row) + b"\n"
    path = RESERVATION_ROOT / f"{ordinal:06d}.json"
    put_exclusive(path, raw)
    return row, sha(raw)


def reserve_command(ctx, ledger):
    LOCK_ROOT.mkdir(parents=True, exist_ok=True)
    with ledger.controller_lock(LOCK_ROOT):
        # Old prototype ledgers cannot be silently ignored or reset.
        require(not any((CACHE / "reservations").glob("*.json")), "legacy split reservation ledger present")
        fresh = load_context(ctx["command"]["id"], dispatch=True)
        require(fresh["phase_sha"] == ctx["phase_sha"] and fresh["plan_sha"] == ctx["plan_sha"],
                "admission inputs changed before reservation")
        rows, command_rows, total, previous = read_reservations(ctx)
        require(ctx["command"]["id"] not in command_rows, "command reservation is non-retryable")
        unreserved = [row for row in ctx["plan"]["commands"] if row["id"] not in command_rows]
        expected_final = total + sum(accounting_units(row["accounting"]) for row in unreserved)
        if not rows:
            expected_final += FULL_GATE_PAIR
        require(expected_final == ctx["grand_total"] <= CEILING,
                "all remaining/audit/control/repeat charges plus gate pair not retained")
        if not rows:
            pair_outstanding = ctx["grand_total"] - INHERITED - FULL_GATE_PAIR
            _, previous = append_reservation(ctx, "inherited-full-gate-pair", None, None,
                {"inherited_full_gate_pair_units": FULL_GATE_PAIR}, pair_outstanding,
                total, previous, 0)
            total += FULL_GATE_PAIR
            rows, command_rows, total, previous = read_reservations(ctx)
        accounting = ctx["command"]["accounting"]
        charge = accounting_units(accounting)
        outstanding = ctx["grand_total"] - total - charge
        row, row_sha = append_reservation(ctx, "scientific-command", ctx["command"]["id"],
                                          ctx["phase_sha"], accounting, outstanding,
                                          total, previous, len(rows))
        return row, row_sha


def attempt_membership(directory):
    paths = sorted(directory.rglob("*"))
    require(not any(path.is_symlink() for path in paths), "symlink in retained attempt")
    return {path.relative_to(directory).as_posix(): sha(path.read_bytes())
            for path in paths if path.is_file() and path.name != "execution.json"}


def validate_reservation_for(ctx, command_id, phase_sha):
    rows, command_rows, _, _ = read_reservations(ctx)
    require(command_id in command_rows, "producer reservation missing")
    row, row_sha = command_rows[command_id]
    require(row["phase_manifest_sha256"] == phase_sha
            and row["accounting"] == ctx["rows"][command_id]["accounting"],
            "producer reservation phase/accounting")
    return row, row_sha


def validate_attempt_core(ctx, command_id, expected=None):
    directory = ATTEMPT_ROOT / command_id
    require(directory.is_dir() and not directory.is_symlink()
            and directory.resolve().is_relative_to(ATTEMPT_ROOT.resolve()), "owned attempt directory")
    require((directory / "execution.json").is_file(),
            "producer attempt has a nonrefundable reservation but no terminal receipt; "
            "outcome is permanently unknown and inadmissible")
    execution, execution_raw = fixed_file(directory / "execution.json", limit=2 * 1024**2,
                                          root=directory, canonical=True)
    exact_keys(execution, EXECUTION_KEYS, "producer execution receipt schema")
    require(execution["schema"] == "recursion-native-execution/v1"
            and execution["campaign"] == CAMPAIGN and execution["parent_goal"] == PARENT
            and execution["candidate"] == ctx["candidate"]
            and execution["candidate_tree"] == ctx["tree"] and execution["command_id"] == command_id
            and execution["budget_plan_sha256"] == ctx["plan_sha"]
            and execution["activation_sha256"] == ctx["activation_sha"]
            and execution["policy_sha256"] == ctx["policy_sha"]
            and execution["policy_revision"] == ctx["policy_revision"]
            and execution["budget_revision"] == ctx["budget_revision"]
            and execution["model_revision_sha256"] == ctx["model_pin"]["sha256"]
            and execution["source_closure_sha256"] == ctx["closure_sha"]
            and execution["controller_sha256"] == ctx["controller_sha"]
            and execution["inherited_full_gate_obligation"] == GATE_OBLIGATION
            and execution["status"] == "PASS_LOCAL_RESEARCH_ONLY"
            and execution["scientific_approval"] is False
            and execution["full_gate_equivalence"] is False, "producer exact local-only PASS")
    producer_phase, producer_phase_raw = fixed_file(PHASE_ROOT / (command_id + ".json"),
        limit=512 * 1024, root=PHASE_ROOT, canonical=True)
    require(sha(producer_phase_raw) == execution["phase_manifest_sha256"], "producer phase bytes")
    load_reviews(command_id, ctx["candidate"], sha(producer_phase_raw), ctx["plan_sha"],
                 producer_phase, ctx["model_revision"], ctx["policy_revision"],
                 ctx["budget_revision"])
    row, row_sha = validate_reservation_for(ctx, command_id, sha(producer_phase_raw))
    require(row_sha == execution["reservation_sha256"]
            and row["ordinal"] == execution["reservation_ordinal"], "producer reservation binding")
    membership = attempt_membership(directory)
    require(membership == execution["attempt_membership"], "producer full retained membership")
    admission_path = directory / "admission.json"
    require(membership.get("admission.json") == execution["admission_sha256"]
            and sha(admission_path.read_bytes()) == execution["admission_sha256"],
            "producer admission membership")
    admission, _ = fixed_file(admission_path, limit=2 * 1024**2, root=directory, canonical=True)
    exact_keys(admission, ADMISSION_KEYS, "producer admission schema")
    producer_command = producer_phase.get("command")
    require(admission["status"] == "ADMITTED_BEFORE_EXECUTION"
            and admission["candidate"] == ctx["candidate"]
            and admission["phase_manifest_sha256"] == sha(producer_phase_raw)
            and admission["reservation_sha256"] == row_sha
            and admission["accounting"] == row["accounting"]
            and admission["policy_revision"] == ctx["policy_revision"]
            and admission["budget_revision"] == ctx["budget_revision"]
            and admission["inherited_full_gate_obligation"] == GATE_OBLIGATION
            and admission["pre_dispatch_receipt"] == (producer_command.get("pre_dispatch_receipt")
                if type(producer_command) is dict else None),
            "producer durable admission")
    output_path = directory / "output.json"
    payload, output_raw = fixed_file(output_path, limit=MAX_OUTPUT, root=directory)
    require(output_raw == canonical_bytes(payload) and sha(output_raw) == execution["output_sha256"]
            and membership.get("output.json") == execution["output_sha256"],
            "producer exact canonical payload bytes")
    outcome = execution["outcome"]
    exact_keys(outcome, {"exit_code", "reason", "cleanup_error", "transport_error",
                         "elapsed_seconds", "pipes_closed", "direct_process_exited",
                         "local_quiescent", "isolation"}, "producer outcome schema")
    exact_keys(outcome["isolation"], {"path", "quiescent", "cleanup_error", "started_unix",
                                      "memory_peak", "ended_unix"}, "producer isolation schema")
    require(outcome["exit_code"] == 0 and outcome["reason"] is None
            and outcome["cleanup_error"] is None and outcome["pipes_closed"] is True
            and outcome["direct_process_exited"] is True and outcome["local_quiescent"] is True
            and outcome["isolation"]["quiescent"] is True
            and outcome["isolation"]["cleanup_error"] is None
            and CGROUP_RE.fullmatch(outcome["isolation"]["path"])
            and not Path(outcome["isolation"]["path"]).exists(), "producer quiescence")
    if expected is not None:
        require(sha(execution_raw) == expected["execution_sha256"]
                and sha(producer_phase_raw) == expected["producer_phase_sha256"]
                and execution["output_sha256"] == expected["output_sha256"],
                "consumer exact producer hashes")
    return directory, execution, sha(execution_raw), membership, payload, output_raw


def read_audit_ledger(ctx):
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    require(AUDIT_ROOT.resolve() == AUDIT_ROOT and not AUDIT_ROOT.is_symlink(),
            "canonical owned audit root")
    files = sorted(AUDIT_ROOT.glob("*.json"))
    require([path.name for path in files] == [f"{i:06d}.json" for i in range(len(files))],
            "contiguous append-only owned audit ledger")
    previous, rows = None, []
    for ordinal, path in enumerate(files):
        value, raw = fixed_file(path, limit=2 * 1024**2, root=AUDIT_ROOT, canonical=True)
        exact_keys(value, OWNED_AUDIT_KEYS, "owned retained audit schema")
        require(value["schema"] == "recursion-native-owned-retained-audit/v1"
                and value["audit_ordinal"] == ordinal
                and value["previous_audit_sha256"] == previous,
                "previous_audit_sha256 chain binding")
        require(value["campaign"] == CAMPAIGN and value["parent_goal"] == PARENT
                and value["candidate"] == ctx["candidate"]
                and value["candidate_tree"] == ctx["tree"]
                and value["budget_plan_sha256"] == ctx["plan_sha"]
                and value["controller_sha256"] == ctx["controller_sha"]
                and value["source_closure_sha256"] == ctx["closure_sha"]
                and value["policy_revision"] == ctx["policy_revision"]
                and value["budget_revision"] == ctx["budget_revision"]
                and value["inherited_full_gate_obligation"] == GATE_OBLIGATION
                and value["status"] == "OWNED_RETAINED_AUDIT_PASS"
                and value["scientific_approval"] is False
                and value["command_id"] in ctx["rows"]
                and value["producer_role"] == ctx["rows"][value["command_id"]]["role"],
                "owned audit chain binding")
        previous = sha(raw)
        rows.append((value, previous))
    require(len({row[0]["command_id"] for row in rows}) == len(rows),
            "unique audited command ids")
    return rows


def verify_dependency(ctx, binding):
    command_id = binding["command"]
    directory, execution, execution_sha, membership, _, output_raw = validate_attempt_core(
        ctx, command_id, binding)
    matches = [(row, row_sha) for row, row_sha in read_audit_ledger(ctx)
               if row["command_id"] == command_id]
    require(len(matches) == 1, "exactly one owned audit row per producer")
    audit_value, audit_sha = matches[0]
    require(audit_sha == binding["owned_audit_sha256"]
            and audit_value["execution_sha256"] == execution_sha
            and audit_value["phase_manifest_sha256"] == execution["phase_manifest_sha256"]
            and audit_value["attempt_membership"] == membership
            and audit_value["output_sha256"] == sha(output_raw)
            and audit_value["admission_sha256"] == execution["admission_sha256"]
            and audit_value["reservation_sha256"] == execution["reservation_sha256"]
            and audit_value["reservation_ordinal"] == execution["reservation_ordinal"]
            and audit_value["quiescence_verified"] is True
            and audit_value["source_membership_verified"] is True
            and utc(audit_value["created_utc"]) > utc(execution["finished_utc"]),
            "independent owned retained audit binding")
    return output_raw, {"command": command_id, "mount": binding["mount"],
                        "output_sha256": sha(output_raw), "execution_sha256": execution_sha,
                        "owned_audit_sha256": audit_sha,
                        "producer_phase_sha256": binding["producer_phase_sha256"]}


def build_inputs(ctx):
    files, membership, dependencies = {}, {}, []
    for path, row in ctx["closure"].items():
        raw = git("show", ctx["candidate"] + ":" + path)
        require(sha(raw) == row["sha256"], "source changed during mount build")
        files[path] = raw.decode("utf-8", errors="strict")
        membership[path] = sha(raw)
    for binding in ctx["command"]["dependencies"]:
        raw, member = verify_dependency(ctx, binding)
        mount = binding["mount"]
        require(mount not in files, "dependency/source mount collision")
        files[mount] = raw.decode("utf-8", errors="strict")
        membership[mount] = sha(raw)
        dependencies.append(member)
    require(sum(len(value.encode("utf-8")) for value in files.values()) <= MAX_INPUT,
            "mounted source/dependency closure exceeds 32MiB")
    return files, membership, dependencies


def mount_control_receipt(ctx, files, input_membership, row, row_sha):
    """Mount this command's own durable ledger row read-only for the control shim.

    The mounted bytes are the exact canonical reservation row created by the
    pre-dispatch nonrefundable reservation.  The runtime sha256 is verified
    against the ledger hash so the sandbox can only read the real row.
    """
    mount = "inputs/" + ctx["command"]["id"] + ".reservation.json"
    require(mount not in files, "receipt/source mount collision")
    raw = canonical_bytes(row) + b"\n"
    require(sha(raw) == row_sha, "mounted durable receipt differs from ledger row")
    files[mount] = raw.decode("utf-8")
    input_membership[mount] = row_sha
    require(sum(len(value.encode("utf-8")) for value in files.values()) <= MAX_INPUT,
            "mounted source/dependency/receipt closure exceeds 32MiB")
    return mount


def gate_source(argv):
    return ("import os,shutil,subprocess,sys\n"
            "shutil.copytree(\"/src\", \"/work/repo\")\n"
            "os.chdir(\"/work/repo\")\n"
            f"raise SystemExit(subprocess.call({argv!r}))\n").encode("utf-8")


def validate_envelope(ctx, stdout, expected_inputs):
    raw = stdout.encode("utf-8")
    envelope = strict_json(raw)
    require(raw == canonical_bytes(envelope) + b"\n", "wrapper stdout is not one canonical JSON envelope")
    exact_keys(envelope, {"payload", "fixture_accounting"}, "research_entry envelope")
    accounting = envelope["fixture_accounting"]
    exact_keys(accounting, {"unit", "limit", "calls", "by_function", "kernel_sha256",
                            "target_sha256", "executed_source_hashes",
                            "all_research_units_counted_by_this_hook"}, "fixture accounting envelope")
    require(accounting["unit"] == "planning-kernel-genesis-or-admit-call"
            and type(accounting["limit"]) is int and accounting["limit"] == FIXTURE_RESERVE
            and type(accounting["calls"]) is int and 0 <= accounting["calls"] <= FIXTURE_RESERVE,
            "4096 fixture reservation and actual call bound")
    by_function = accounting["by_function"]
    require(type(by_function) is dict and set(by_function) == {"genesis", "admit"}
            and all(type(value) is int and value >= 0 for value in by_function.values())
            and sum(by_function.values()) == accounting["calls"], "fixture call breakdown")
    require(accounting["kernel_sha256"] == ctx["closure"][KERNEL]["sha256"]
            and accounting["target_sha256"] == ctx["closure"][ctx["target"]]["sha256"]
            and accounting["all_research_units_counted_by_this_hook"] is False,
            "wrapper kernel/target/claim binding")
    expected = dict(expected_inputs)
    expected["foundry_command_gate.py"] = sha(gate_source(ctx["command"]["argv"]))
    require(accounting["executed_source_hashes"] == expected,
            "wrapper executed source set differs from exact mount")
    validate_contract(ctx["command"]["payload_contract"], envelope["payload"])
    return envelope["payload"], raw


def verify_control_receipt_echo(payload, row, row_sha):
    """The control payload must echo the real ledger row it was mounted.

    reservation_sha256/reservation_ordinal are runtime values absent from argv
    and from the manifest, so a correct echo proves the sandbox actually read
    the mounted nonrefundable row rather than fabricating a receipt from
    declared fields alone.
    """
    echo = payload.get("durable_precharge_receipt") if type(payload) is dict else None
    require(type(echo) is dict
            and echo.get("schema") == CONTROL_RECEIPT_SCHEMA
            and echo.get("receipt_id") == row["receipt_id"]
            and echo.get("refundable") is False
            and echo.get("reservation_sha256") == row_sha
            and echo.get("reservation_ordinal") == row["ordinal"],
            "control receipt does not echo the real pre-dispatch ledger row")


def normalized_outcome(outcome):
    isolation = outcome.get("isolation") or {}
    return {"exit_code": outcome.get("exit_code"), "reason": outcome.get("reason"),
            "cleanup_error": outcome.get("cleanup_error"), "transport_error": outcome.get("error"),
            "elapsed_seconds": outcome.get("elapsed_seconds"),
            "pipes_closed": outcome.get("pipes_closed"),
            "direct_process_exited": outcome.get("direct_process_exited"),
            "local_quiescent": outcome.get("local_quiescent"), "isolation": isolation}


def require_clean_outcome(outcome):
    isolation = outcome.get("isolation") or {}
    require(outcome.get("exit_code") == 0 and outcome.get("reason") is None
            and outcome.get("cleanup_error") is None and outcome.get("pipes_closed") is True
            and outcome.get("direct_process_exited") is True and outcome.get("local_quiescent") is True,
            "command transport did not end cleanly")
    require(isolation.get("quiescent") is True and isolation.get("cleanup_error") is None
            and CGROUP_RE.fullmatch(str(isolation.get("path")))
            and type(isolation.get("memory_peak")) is int
            and 0 <= isolation["memory_peak"] <= JOB_BYTES
            and not Path(isolation["path"]).exists(), "owned cgroup not independently quiescent")
    require(type(outcome.get("stdout")) is str and type(outcome.get("stderr")) is str
            and len(outcome["stdout"].encode("utf-8")) + len(outcome["stderr"].encode("utf-8"))
            <= MAX_OUTPUT and outcome["stderr"] == "", "bounded clean decoded output")


def guard_failures(ctx, capacity, dispatch):
    failures = []
    try:
        activation, activation_raw = fixed_file(ACTIVATION, limit=128 * 1024)
        policy, policy_raw = fixed_file(POLICY, limit=64 * 1024)
        validate_activation(activation)
        validate_policy(policy)
        if sha(activation_raw) != ctx["activation_sha"] or sha(policy_raw) != ctx["policy_sha"]:
            failures.append("activation-or-policy-drift")
        if git_text("rev-parse", "HEAD") != ctx["candidate"]:
            failures.append("candidate-drift")
        if git("status", "--porcelain=v1", "-z", "--untracked-files=all") != b"":
            failures.append("workspace-dirty")
        if (sha(BUDGET_PLAN.read_bytes()) != ctx["plan_sha"]
                or sha(SOURCE_CLOSURE.read_bytes()) != ctx["closure_sha"]
                or sha((PHASE_ROOT / (ctx["command"]["id"] + ".json")).read_bytes()) != ctx["phase_sha"]
                or sha((METHOD_ROOT / (ctx["command"]["id"] + ".json")).read_bytes()) != ctx["method_sha"]
                or {p.stem for p in PHASE_ROOT.glob("*.json")} != set(ctx["rows"])):
            failures.append("manifest-or-review-drift")
        model_raw = git("show", ctx["candidate"] + ":" + MODEL_REVISION)
        if sha(model_raw) != ctx["model_pin"]["sha256"]:
            failures.append("model-revision-drift")
        parent_active()
        if any(path.exists() for path in marker_paths()):
            failures.append("pause-or-stop")
        validate_usage(policy)
        resource_check(capacity)
        if now() >= (ctx["dispatch_end"] if dispatch else END):
            failures.append("deadline")
    except BaseException as exc:
        failures.append("guard-error:" + type(exc).__name__ + ":" + str(exc)[:500])
    return failures


def stop_gate(ctx, capacity):
    state = {"checked": 0.0, "failures": []}

    def stop():
        if time.monotonic() - state["checked"] >= 1.0:
            state["checked"] = time.monotonic()
            state["failures"] = guard_failures(ctx, capacity, dispatch=True)
        return bool(state["failures"])

    stop.state = state
    return stop


def final_execution(directory, receipt):
    receipt["attempt_membership"] = attempt_membership(directory)
    for _ in range(10):
        raw = canonical_bytes(receipt) + b"\n"
        total = sum(path.stat().st_size for path in directory.rglob("*") if path.is_file()) + len(raw)
        if receipt.get("attempt_bytes") == total:
            break
        receipt["attempt_bytes"] = total
    raw = canonical_bytes(receipt) + b"\n"
    require(receipt["attempt_bytes"] <= MAX_ATTEMPT, "retained attempt exceeds 256MiB")
    put_exclusive(directory / "execution.json", raw)
    return sha(raw)


def uncertain_record(ctx, command_id, row, row_sha, observation):
    try:
        subset = {key: observation.get(key) for key in
                  ("exit_code", "reason", "cleanup_error", "error", "elapsed_seconds",
                   "pipes_closed", "direct_process_exited", "local_quiescent", "isolation")}
        raw = canonical_bytes({"schema": "recursion-native-attempt-uncertain/v1",
            "campaign": CAMPAIGN, "parent_goal": PARENT, "candidate": ctx["candidate"],
            "command_id": command_id, "reservation_sha256": row_sha,
            "reservation_ordinal": row["ordinal"],
            "phase_manifest_sha256": ctx["phase_sha"],
            "policy_revision": ctx["policy_revision"],
            "budget_revision": ctx["budget_revision"],
            "recorded_utc": now().isoformat(), "observation": subset})
        require(len(raw) <= MAX_UNCERTAIN_BYTES, "bounded uncertain observation")
    except BaseException:
        raw = canonical_bytes({"schema": "recursion-native-attempt-uncertain/v1",
            "campaign": CAMPAIGN, "parent_goal": PARENT, "candidate": ctx["candidate"],
            "command_id": command_id, "reservation_sha256": row_sha,
            "reservation_ordinal": row["ordinal"],
            "phase_manifest_sha256": ctx["phase_sha"],
            "policy_revision": ctx["policy_revision"],
            "budget_revision": ctx["budget_revision"],
            "recorded_utc": now().isoformat(),
            "observation": {"serialization": "failed"}})
    return raw + b"\n"


def run(command_id):
    modules = validate_runtime()
    ctx = load_context(command_id, modules["capacity"], dispatch=True)
    files, input_membership, dependency_membership = build_inputs(ctx)
    ATTEMPT_ROOT.mkdir(parents=True, exist_ok=True)
    directory = ATTEMPT_ROOT / command_id
    directory.mkdir(parents=False, exist_ok=False)
    row = row_sha = None
    started = now().isoformat()
    receipt = {"schema": "recursion-native-execution/v1", "campaign": CAMPAIGN,
        "parent_goal": PARENT, "candidate": ctx["candidate"], "candidate_tree": ctx["tree"],
        "command_id": command_id, "role": ctx["command"]["role"],
        "phase_manifest_sha256": ctx["phase_sha"], "budget_plan_sha256": ctx["plan_sha"],
        "activation_sha256": ctx["activation_sha"], "policy_sha256": ctx["policy_sha"],
        "policy_revision": ctx["policy_revision"], "budget_revision": ctx["budget_revision"],
        "model_revision_sha256": ctx["model_pin"]["sha256"],
        "source_closure_sha256": ctx["closure_sha"], "controller_sha256": ctx["controller_sha"],
        "reservation_sha256": None, "reservation_ordinal": None,
        "accounting": ctx["command"]["accounting"], "argv": ctx["command"]["argv"],
        "seconds": ctx["command"]["seconds"], "started_utc": started, "finished_utc": None,
        "status": "FAILED_RETAINED", "scientific_approval": False,
        "full_gate_equivalence": False,
        "inherited_full_gate_obligation": GATE_OBLIGATION,
        "input_membership": input_membership,
        "dependency_membership": dependency_membership, "review_membership": ctx["reviews"],
        "admission_sha256": None, "outcome": None, "stdout_sha256": None,
        "stderr_sha256": None, "output_sha256": None, "payload_sha256": None,
        "postcheck_failures": [], "error": None, "attempt_membership": {}, "attempt_bytes": 0}
    try:
        row, row_sha = reserve_command(ctx, modules["ledger"])
        receipt["reservation_sha256"] = row_sha
        receipt["reservation_ordinal"] = row["ordinal"]
        pending = {"schema": "recursion-native-attempt-pending/v1", "campaign": CAMPAIGN,
            "parent_goal": PARENT, "candidate": ctx["candidate"], "command_id": command_id,
            "reservation_sha256": row_sha, "reservation_ordinal": row["ordinal"],
            "phase_manifest_sha256": ctx["phase_sha"],
            "policy_revision": ctx["policy_revision"],
            "budget_revision": ctx["budget_revision"],
            "started_utc": started, "status": "RESERVED_AWAITING_TERMINAL_RECEIPT"}
        put_exclusive(directory / "pending.json", canonical_bytes(pending) + b"\n")
        if ctx["command"]["role"] == "control":
            mount_control_receipt(ctx, files, input_membership, row, row_sha)
        admission = {"schema": "recursion-native-admission/v1", "campaign": CAMPAIGN,
            "parent_goal": PARENT, "candidate": ctx["candidate"], "candidate_tree": ctx["tree"],
            "command_id": command_id, "role": ctx["command"]["role"],
            "phase_manifest_sha256": ctx["phase_sha"], "budget_plan_sha256": ctx["plan_sha"],
            "activation_sha256": ctx["activation_sha"], "policy_sha256": ctx["policy_sha"],
            "policy_revision": ctx["policy_revision"], "budget_revision": ctx["budget_revision"],
            "model_revision_sha256": ctx["model_pin"]["sha256"],
            "source_closure_sha256": ctx["closure_sha"], "controller_sha256": ctx["controller_sha"],
            "reservation_sha256": row_sha, "reservation_ordinal": row["ordinal"],
            "accounting": ctx["command"]["accounting"], "argv": ctx["command"]["argv"],
            "seconds": ctx["command"]["seconds"], "input_membership": input_membership,
            "dependency_membership": dependency_membership, "review_membership": ctx["reviews"],
            "status": "ADMITTED_BEFORE_EXECUTION", "admitted_utc": now().isoformat(),
            "refundable": False, "scientific_approval": False, "full_gate_equivalence": False,
            "inherited_full_gate_obligation": GATE_OBLIGATION,
            "pre_dispatch_receipt": ctx["command"].get("pre_dispatch_receipt")}
        admission_raw = canonical_bytes(admission) + b"\n"
        put_exclusive(directory / "admission.json", admission_raw)
        receipt["admission_sha256"] = sha(admission_raw)
        pre = guard_failures(ctx, modules["capacity"], dispatch=True)
        require(not pre, "pre-execution live guard: " + ";".join(pre))
        stop = stop_gate(ctx, modules["capacity"])
        outcome = modules["foundry_tools"].run_command(files, ctx["command"]["argv"],
                                                        ctx["command"]["seconds"], stop=stop)
        stdout_raw = outcome.get("stdout", "").encode("utf-8")
        stderr_raw = outcome.get("stderr", "").encode("utf-8")
        put_exclusive(directory / "stdout.log", stdout_raw)
        put_exclusive(directory / "stderr.log", stderr_raw)
        receipt["outcome"] = normalized_outcome(outcome)
        receipt["stdout_sha256"] = sha(stdout_raw)
        receipt["stderr_sha256"] = sha(stderr_raw)
        require_clean_outcome(outcome)
        payload, _ = validate_envelope(ctx, outcome["stdout"], input_membership)
        if ctx["command"]["role"] == "control":
            verify_control_receipt_echo(payload, row, row_sha)
        payload_raw = canonical_bytes(payload)
        put_exclusive(directory / "output.json", payload_raw)
        receipt["output_sha256"] = sha(payload_raw)
        receipt["payload_sha256"] = sha(payload_raw)
        post = guard_failures(ctx, modules["capacity"], dispatch=True)
        receipt["postcheck_failures"] = post
        require(not post and not stop.state["failures"], "during/post live guard failed")
        receipt["status"] = "PASS_LOCAL_RESEARCH_ONLY"
    except modules["foundry_tools"].ToolUncertain as exc:
        observation = exc.observation
        for name in ("stdout", "stderr"):
            if type(observation.get(name)) is str and not (directory / (name + ".log")).exists():
                raw = observation[name].encode("utf-8")
                put_exclusive(directory / (name + ".log"), raw)
                receipt[name + "_sha256"] = sha(raw)
        try:
            put_exclusive(directory / "uncertain.json",
                          uncertain_record(ctx, command_id, row, row_sha, observation))
        except BaseException:
            pass
        receipt["outcome"] = normalized_outcome(observation)
        receipt["status"] = "UNKNOWN_RETAINED"
        receipt["error"] = "uncertain cleanup; nonrefundable reservation retained"
    except BaseException as exc:
        receipt["status"] = "FAILED_RETAINED"
        receipt["error"] = (type(exc).__name__ + ": " + str(exc))[:4000]
        if row is None:
            try:
                directory.rmdir()
            except OSError:
                pass
    finally:
        if row is not None:
            receipt["finished_utc"] = now().isoformat()
            receipt["postcheck_failures"] = guard_failures(ctx, modules["capacity"], dispatch=False)
            if receipt["status"] == "PASS_LOCAL_RESEARCH_ONLY" and receipt["postcheck_failures"]:
                receipt["status"] = "FAILED_RETAINED"
                receipt["error"] = "terminal live guard failed"
            try:
                execution_sha = final_execution(directory, receipt)
            except BaseException as exc:
                try:
                    put_exclusive(directory / "execution-write-failed.json",
                        canonical_bytes({"schema": "recursion-native-terminal-write-failure/v1",
                            "command_id": command_id, "reservation_sha256": row_sha,
                            "error": (type(exc).__name__ + ": " + str(exc))[:1000]}) + b"\n")
                except BaseException:
                    pass
            else:
                print(json.dumps({"status": receipt["status"], "execution_sha256": execution_sha,
                                  "owned_retained_audit_required": True}, sort_keys=True), flush=True)
    require(row is not None, "reservation was not created")
    require(receipt["status"] == "PASS_LOCAL_RESEARCH_ONLY", "retained non-PASS scientific attempt")
    return receipt


def audit(command_id):
    modules = validate_runtime()
    ctx = load_context(command_id, modules["capacity"], dispatch=False)
    directory, execution, execution_sha, membership, _, output_raw = validate_attempt_core(ctx, command_id)
    # Rebuild every mounted source/dependency byte and compare to durable admission.
    _, rebuilt_membership, _ = build_inputs(ctx)
    if ctx["command"]["role"] == "control":
        row, row_sha = validate_reservation_for(ctx, command_id, ctx["phase_sha"])
        require(row_sha == execution["reservation_sha256"],
                "control audit reservation identity")
        rebuilt_membership["inputs/" + command_id + ".reservation.json"] = row_sha
    require(rebuilt_membership == execution["input_membership"], "independent source membership replay")
    require(not guard_failures(ctx, modules["capacity"], dispatch=False), "audit live guard")
    ledger_rows = read_audit_ledger(ctx)
    require(command_id not in {row[0]["command_id"] for row in ledger_rows},
            "owned audit is non-retryable")
    created = now()
    require(created > utc(execution["finished_utc"]), "audit is a later controller invocation")
    value = {"schema": "recursion-native-owned-retained-audit/v1", "campaign": CAMPAIGN,
        "parent_goal": PARENT, "candidate": ctx["candidate"], "candidate_tree": ctx["tree"],
        "command_id": command_id, "producer_role": ctx["rows"][command_id]["role"],
        "phase_manifest_sha256": ctx["phase_sha"], "budget_plan_sha256": ctx["plan_sha"],
        "controller_sha256": ctx["controller_sha"], "source_closure_sha256": ctx["closure_sha"],
        "policy_revision": ctx["policy_revision"], "budget_revision": ctx["budget_revision"],
        "execution_sha256": execution_sha, "reservation_sha256": execution["reservation_sha256"],
        "reservation_ordinal": execution["reservation_ordinal"],
        "admission_sha256": execution["admission_sha256"], "output_sha256": sha(output_raw),
        "attempt_membership": membership, "source_membership_verified": True,
        "quiescence_verified": True, "audit_ordinal": len(ledger_rows),
        "previous_audit_sha256": ledger_rows[-1][1] if ledger_rows else None,
        "inherited_full_gate_obligation": GATE_OBLIGATION,
        "created_utc": created.isoformat(), "status": "OWNED_RETAINED_AUDIT_PASS",
        "scientific_approval": False}
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    raw = canonical_bytes(value) + b"\n"
    put_exclusive(AUDIT_ROOT / f"{len(ledger_rows):06d}.json", raw)
    require(not guard_failures(ctx, modules["capacity"], dispatch=False), "post-audit live guard")
    print(json.dumps({"status": value["status"], "audit_sha256": sha(raw)}, sort_keys=True), flush=True)
    return value


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    require(len(argv) == 2 and argv[0] in {"run", "audit"},
            "usage: native_controller_v2.py {run|audit} <command-id>")
    (run if argv[0] == "run" else audit)(argv[1])


if __name__ == "__main__":
    main()
