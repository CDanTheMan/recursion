"""Strict, dependency-free contracts for the Recursion v2 MVP."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA_VERSION = 2
MAX_BYTES, MAX_NODES, MAX_DEPTH, MAX_STRING, MAX_LIST = 262_144, 10_000, 64, 65_536, 1_000
ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")
TIME_RE = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
ENDPOINT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
PATH_PART_RE = re.compile(r"^[^/\\\x00]+$")
KINDS = {"supervisor", "task", "capability_grant", "budget", "receipt", "checkpoint", "verification", "recovery"}
DIGEST_FIELD = {"supervisor": "supervisor_digest", "task": "task_digest", "capability_grant": "grant_digest", "budget": "budget_digest", "receipt": "receipt_digest", "checkpoint": "checkpoint_digest", "verification": "verification_digest", "recovery": "recovery_digest", "assignment": "assignment_digest", "candidate": "candidate_digest", "evidence": "evidence_digest"}
FIELDS = {
 "supervisor": {"schema_version","kind","id","parent_goal","final_authority","executive_identity","status","pause_observed","pause_epoch","policy_digest","valid_from","valid_until","supervisor_digest"},
 "task": {"schema_version","kind","id","project_id","source_repository","source_branch","source_sha","parent_goal","parent_task_id","parent_task_digest","depth","allowed_paths","non_goals","acceptance","requested_capabilities","budget_id","verification_policy","gate_digest","created_at","expires_at","task_digest"},
 "capability_grant": {"schema_version","kind","id","task_id","task_digest","capabilities","allowed_paths","network_policy","endpoints","issued_at","expires_at","grant_digest"},
 "budget": {"schema_version","kind","id","task_id","task_digest","parent_budget_id","token_limit","wall_seconds","concurrency_limit","cost_limit_cents","metered_spend_allowed","approval_digest","calendar_month_ceiling_cents","remaining_tokens","remaining_wall_seconds","remaining_cost_cents","budget_digest"},
 "receipt": {"schema_version","kind","id","task_id","task_digest","assignment_digest","adapter","candidate_id","candidate_commit","result_digest","status","usage","checkpoint_digests","started_at","finished_at","receipt_digest"},
 "checkpoint": {"schema_version","kind","id","task_id","task_digest","packet_digest","context_digest","state_digest","sequence","prev_digest","created_at","checkpoint_digest"},
 "verification": {"schema_version","kind","id","task_id","task_digest","receipt_digest","candidate_id","candidate_commit","candidate_digest","result_digest","gate_digest","evidence_digest","status","verifier_task_id","verifier_task_digest","verified_at","verification_digest"},
 "recovery": {"schema_version","kind","id","task_id","task_digest","prior_checkpoint_digest","prior_receipt_digest","action","state","failure_class","attempt","created_at","outcome","recovery_digest"},
}
REQUIRED = {kind: set(fields) for kind, fields in FIELDS.items()}
_SECRET = re.compile(r"(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_-]{12,}|github_pat_[A-Za-z0-9_]{12,}|xox[baprs]-[A-Za-z0-9-]{12,}|AKIA[0-9A-Z]{16}|npm_[A-Za-z0-9]{12,}|AIza[0-9A-Za-z_-]{20,}|bearer[ \t]+[^ \t]+|(?:api[_-]?key|password|secret|token)[ \t]*[:=]|-----BEGIN [A-Z ]+ KEY-----)", re.I)
_SECRET_KEYS = {"password","credential","credentials","api_key","apikey","secret","token","private_key","private_reasoning","chain_of_thought","hidden_reasoning","cot"}

class ContractError(ValueError):
    """Typed fail-closed contract failure."""

def _walk(value: Any) -> None:
    count = 0; stack: list[tuple[Any, int]] = [(value, 0)]
    while stack:
        current, depth = stack.pop(); count += 1
        if count > MAX_NODES: raise ContractError("JSON node limit exceeded")
        if depth > MAX_DEPTH: raise ContractError("JSON depth limit exceeded")
        if isinstance(current, str):
            if len(current) > MAX_STRING: raise ContractError("JSON string limit exceeded")
            if _SECRET.search(current): raise ContractError("secret material")
        elif isinstance(current, dict):
            if len(current) > MAX_LIST: raise ContractError("JSON object limit exceeded")
            for key, child in current.items():
                if not isinstance(key, str): raise ContractError("object keys must be strings")
                if len(key) > MAX_STRING: raise ContractError("JSON string limit exceeded")
                low = key.lower()
                if low in _SECRET_KEYS or "chain_of_thought" in low or "private_reasoning" in low: raise ContractError("secret or private-reasoning field")
                stack.append((child, depth + 1))
        elif isinstance(current, list):
            if len(current) > MAX_LIST: raise ContractError("JSON list limit exceeded")
            stack.extend((child, depth + 1) for child in reversed(current))
        elif isinstance(current, float) and not math.isfinite(current): raise ContractError("nonfinite number")
        elif current is not None and not isinstance(current, (bool, int, float)): raise ContractError("value is not JSON data")

def canonical_json(value: Any) -> bytes:
    try:
        _walk(value)
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    except ContractError: raise
    except (TypeError, ValueError, OverflowError, RecursionError, UnicodeError) as exc: raise ContractError("not canonical JSON") from exc
    if len(encoded) > MAX_BYTES: raise ContractError("JSON byte limit exceeded")
    return encoded

def digest(record: Mapping[str, Any]) -> str:
    if not isinstance(record, Mapping): raise ContractError("record must be an object")
    body = dict(record); field = DIGEST_FIELD.get(record.get("kind"))
    if field: body.pop(field, None)
    return hashlib.sha256(canonical_json(body)).hexdigest()
canonical_digest = digest
compute_digest = digest
canonicalize = canonical_json

def _str(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_STRING or _SECRET.search(value): raise ContractError(f"{name} must be a safe non-empty string")
    return value
def _id(value: Any, name: str) -> None:
    if not isinstance(value, str) or not ID_RE.fullmatch(value): raise ContractError(f"{name} is not canonical")
def _digest(value: Any, name: str) -> None:
    if not isinstance(value, str) or not DIGEST_RE.fullmatch(value): raise ContractError(f"{name} is not a SHA-256 digest")
def _time(value: Any, name: str) -> _dt.datetime:
    _str(value, name)
    if not TIME_RE.fullmatch(value): raise ContractError(f"{name} is not canonical UTC time")
    try: return _dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc)
    except ValueError as exc: raise ContractError(f"{name} is not a valid UTC time") from exc
def parse_time(value: str) -> _dt.datetime: return _time(value, "time")
def _reference_time(value: str | _dt.datetime | None) -> _dt.datetime | None:
    if value is None: return None
    if isinstance(value, _dt.datetime):
        if value.tzinfo is None: raise ContractError("reference time must be timezone-aware")
        return value.astimezone(_dt.timezone.utc)
    return _time(value, "observed_at")
def _list(value: Any, name: str, *, nonempty: bool = True) -> None:
    if not isinstance(value, list) or (nonempty and not value) or len(value) > MAX_LIST: raise ContractError(f"{name} must be a {'non-empty ' if nonempty else ''}list")
    try: duplicate = len({json.dumps(item, sort_keys=True, separators=(",", ":")) for item in value}) != len(value)
    except (TypeError, ValueError, RecursionError) as exc: raise ContractError(f"{name} is not JSON data") from exc
    if duplicate: raise ContractError(f"{name} contains duplicates")
    if any(not isinstance(item, str) or not item for item in value): raise ContractError(f"{name} must contain strings")
def _paths(value: Any, name: str) -> None:
    _list(value, name)
    for path in value:
        if path.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", path) or "\x00" in path: raise ContractError(f"{name} contains an unsafe path")
        if any(not part or part in {".", ".."} or not PATH_PART_RE.fullmatch(part) for part in path.split("/")): raise ContractError(f"{name} contains an unsafe path")
def _subset(child: list[str], parent: list[str]) -> bool: return all(any(item == base or item.startswith(base.rstrip("/") + "/") for base in parent) for item in child)
def _integer(value: Any, name: str, minimum: int = 0) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum: raise ContractError(f"{name} must be an integer")
def _money(value: Any, name: str) -> None: _integer(value, name, 0)
def _common(record: Any, kind: str) -> dict[str, Any]:
    if not isinstance(record, dict): raise ContractError("record must be an object")
    canonical_json(record)
    extra, missing = set(record) - FIELDS[kind], REQUIRED[kind] - set(record)
    if extra: raise ContractError("unknown fields: " + ", ".join(sorted(extra)))
    if missing: raise ContractError("missing fields: " + ", ".join(sorted(missing)))
    if record["schema_version"] != SCHEMA_VERSION or isinstance(record["schema_version"], bool): raise ContractError("schema_version must be 2")
    if record["kind"] != kind: raise ContractError(f"kind must be {kind}")
    _id(record["id"], f"{kind}.id"); return record
def _nullable_digest(value: Any, name: str) -> None:
    if value is not None: _digest(value, name)
def _validate_self_digest(record: dict[str, Any]) -> None:
    field = DIGEST_FIELD[record["kind"]]; _digest(record[field], field)
    if record[field] != digest(record): raise ContractError(f"{field} mismatch")

def validate(record: dict[str, Any], *, parent_task: dict[str, Any] | None = None, parent_budget: dict[str, Any] | None = None, observed_at: str | _dt.datetime | None = None, reference_time: str | _dt.datetime | None = None) -> dict[str, Any]:
    if not isinstance(record, dict) or record.get("kind") not in KINDS: raise ContractError("unknown kind")
    kind = record["kind"]; o = _common(record, kind); ref = _reference_time(observed_at if observed_at is not None else reference_time)
    if kind == "supervisor":
        _id(o["parent_goal"], "parent_goal")
        if o["final_authority"] not in {"lucas", "Lucas", "lucas-final-authority"}: raise ContractError("final authority must be Lucas")
        if o["executive_identity"] not in {"hermes", "Hermes", "hermes-executive"}: raise ContractError("executive identity must be Hermes")
        if o["status"] not in {"active", "paused", "expired", "revoked"}: raise ContractError("invalid supervisor status")
        if not isinstance(o["pause_observed"], bool): raise ContractError("pause_observed must be boolean")
        _integer(o["pause_epoch"], "pause_epoch"); _digest(o["policy_digest"], "policy_digest")
        start, end = _time(o["valid_from"], "valid_from"), _time(o["valid_until"], "valid_until")
        if end <= start: raise ContractError("validity interval is reversed")
        if ref is not None and not start <= ref <= end: raise ContractError("record outside validity interval")
    elif kind == "task":
        for name in ("project_id", "parent_goal"): _id(o[name], name)
        if o["parent_task_id"] is None:
            if o["parent_task_digest"] is not None or o["depth"] != 0: raise ContractError("root task parent binding is invalid")
        else: _id(o["parent_task_id"], "parent_task_id"); _digest(o["parent_task_digest"], "parent_task_digest")
        _integer(o["depth"], "depth")
        if o["depth"] > 2: raise ContractError("orchestration depth exceeds 2")
        _str(o["source_repository"], "source_repository"); _str(o["source_branch"], "source_branch")
        if not isinstance(o["source_sha"], str) or not SHA_RE.fullmatch(o["source_sha"]): raise ContractError("source_sha invalid")
        _paths(o["allowed_paths"], "allowed_paths"); _list(o["non_goals"], "non_goals"); _str(o["acceptance"], "acceptance"); _list(o["requested_capabilities"], "requested_capabilities")
        _id(o["budget_id"], "budget_id"); _str(o["verification_policy"], "verification_policy"); _digest(o["gate_digest"], "gate_digest")
        created = _time(o["created_at"], "created_at")
        if o["expires_at"] is not None:
            expires = _time(o["expires_at"], "expires_at")
            if expires <= created: raise ContractError("task expiry is not after creation")
            if ref is not None and ref > expires: raise ContractError("task expired")
        if parent_task is not None:
            validate(parent_task, observed_at=ref)
            if o["parent_task_id"] != parent_task["id"] or o["parent_task_digest"] != parent_task["task_digest"]: raise ContractError("child task parent binding mismatch")
            for name in ("project_id", "source_repository", "source_branch", "source_sha", "parent_goal"):
                if o[name] != parent_task[name]: raise ContractError("child task inherited identity mismatch")
            if o["depth"] != parent_task["depth"] + 1: raise ContractError("invalid child depth")
            if not _subset(o["allowed_paths"], parent_task["allowed_paths"]): raise ContractError("child allowed_paths escalate")
            if not set(o["requested_capabilities"]).issubset(parent_task["requested_capabilities"]): raise ContractError("child capabilities escalate")
    elif kind == "capability_grant":
        _id(o["task_id"], "task_id"); _digest(o["task_digest"], "task_digest"); _list(o["capabilities"], "capabilities"); _paths(o["allowed_paths"], "allowed_paths")
        if o["network_policy"] not in {"none", "provider-only", "allowlist"}: raise ContractError("network_policy is not typed")
        _list(o["endpoints"], "endpoints")
        for endpoint in o["endpoints"]:
            if endpoint != "none" and not ENDPOINT_RE.fullmatch(endpoint): raise ContractError("endpoint is not canonical")
        if o["network_policy"] == "none" and o["endpoints"] != ["none"]: raise ContractError("none network policy must have none endpoint")
        if o["network_policy"] != "none" and "none" in o["endpoints"]: raise ContractError("typed network endpoints mismatch")
        issued, expires = _time(o["issued_at"], "issued_at"), _time(o["expires_at"], "expires_at")
        if expires <= issued: raise ContractError("grant expiry is not after issued_at")
        if ref is not None and ref > expires: raise ContractError("grant expired")
    elif kind == "budget":
        _id(o["task_id"], "task_id"); _digest(o["task_digest"], "task_digest")
        if o["parent_budget_id"] is not None: _id(o["parent_budget_id"], "parent_budget_id")
        for name in ("token_limit", "wall_seconds", "concurrency_limit"): _integer(o[name], name, 1)
        for name in ("cost_limit_cents", "calendar_month_ceiling_cents", "remaining_cost_cents"): _money(o[name], name)
        if o["calendar_month_ceiling_cents"] > 2000: raise ContractError("monthly ceiling exceeds 2000 cents")
        if not isinstance(o["metered_spend_allowed"], bool): raise ContractError("metered_spend_allowed must be boolean")
        if o["metered_spend_allowed"]: _digest(o["approval_digest"], "approval_digest")
        elif o["approval_digest"] is not None: raise ContractError("approval digest must be null when metered is false")
        for name, limit in (("remaining_tokens", o["token_limit"]), ("remaining_wall_seconds", o["wall_seconds"]), ("remaining_cost_cents", o["cost_limit_cents"])):
            _integer(o[name], name)
            if o[name] > limit: raise ContractError(f"{name} exceeds limit")
        if parent_budget is not None:
            validate(parent_budget, observed_at=ref)
            if o["parent_budget_id"] != parent_budget["id"]: raise ContractError("child budget parent mismatch")
            for name in ("token_limit","wall_seconds","concurrency_limit","cost_limit_cents","calendar_month_ceiling_cents","remaining_tokens","remaining_wall_seconds","remaining_cost_cents"):
                if o[name] > parent_budget[name]: raise ContractError("child budget escalation")
            if o["metered_spend_allowed"] and not parent_budget["metered_spend_allowed"]: raise ContractError("child metered permission escalation")
    elif kind == "receipt":
        _id(o["task_id"], "task_id"); _digest(o["task_digest"], "task_digest"); _digest(o["assignment_digest"], "assignment_digest"); _str(o["adapter"], "adapter"); _id(o["candidate_id"], "candidate_id")
        if not isinstance(o["candidate_commit"], str) or not SHA_RE.fullmatch(o["candidate_commit"]): raise ContractError("candidate_commit invalid")
        _digest(o["result_digest"], "result_digest")
        if o["status"] not in {"queued","running","succeeded","failed","cancelled","expired","rejected"}: raise ContractError("receipt status invalid")
        usage = o["usage"]
        if not isinstance(usage, dict) or set(usage) != {"tokens","input_tokens","output_tokens","wall_seconds","cost_cents"}: raise ContractError("usage has unknown or missing fields")
        for name in usage: _integer(usage[name], f"usage.{name}")
        _list(o["checkpoint_digests"], "checkpoint_digests")
        for item in o["checkpoint_digests"]: _digest(item, "checkpoint_digest")
        started, finished = _time(o["started_at"], "started_at"), _time(o["finished_at"], "finished_at")
        if finished < started: raise ContractError("receipt times reversed")
        if ref is not None and finished > ref: raise ContractError("receipt is from the future")
    elif kind == "checkpoint":
        _id(o["task_id"], "task_id"); _digest(o["task_digest"], "task_digest")
        for name in ("packet_digest","context_digest","state_digest"): _digest(o[name], name)
        _integer(o["sequence"], "sequence"); _nullable_digest(o["prev_digest"], "prev_digest"); _time(o["created_at"], "created_at")
        if o["sequence"] == 0 and o["prev_digest"] is not None: raise ContractError("genesis checkpoint has predecessor")
        if o["sequence"] > 0 and o["prev_digest"] is None: raise ContractError("checkpoint chain gap")
    elif kind == "verification":
        _id(o["task_id"], "task_id"); _digest(o["task_digest"], "task_digest"); _digest(o["receipt_digest"], "receipt_digest"); _id(o["candidate_id"], "candidate_id")
        if not isinstance(o["candidate_commit"], str) or not SHA_RE.fullmatch(o["candidate_commit"]): raise ContractError("candidate_commit invalid")
        for name in ("candidate_digest","result_digest","gate_digest","evidence_digest"): _digest(o[name], name)
        if o["status"] not in {"pass","fail"}: raise ContractError("verification status must be pass or fail")
        _id(o["verifier_task_id"], "verifier_task_id"); _digest(o["verifier_task_digest"], "verifier_task_digest"); _time(o["verified_at"], "verified_at")
        if o["verifier_task_id"] == o["task_id"] or o["verifier_task_digest"] == o["task_digest"]: raise ContractError("self-verification")
    elif kind == "recovery":
        _id(o["task_id"], "task_id"); _digest(o["task_digest"], "task_digest"); _digest(o["prior_checkpoint_digest"], "prior_checkpoint_digest"); _digest(o["prior_receipt_digest"], "prior_receipt_digest")
        if o["action"] not in {"resume","retry","abort","pause","reconcile"}: raise ContractError("recovery action invalid")
        if o["state"] not in {"queued","running","paused","succeeded","failed","terminal"}: raise ContractError("recovery state invalid")
        if o["failure_class"] not in {"none","timeout","host-loss","provider-unavailable","quota-exhausted","invalid-result","authorization","unknown"}: raise ContractError("recovery failure class invalid")
        _integer(o["attempt"], "attempt", 1); _time(o["created_at"], "created_at")
        if o["outcome"] not in {"requeued","resumed","aborted","paused","completed","failed"}: raise ContractError("recovery outcome invalid")
    _validate_self_digest(o); return o

validate_contract = validate

def validate_checkpoint_chain(checkpoints: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(checkpoints, Sequence) or isinstance(checkpoints, (str, bytes)) or not checkpoints: raise ContractError("checkpoint chain must be non-empty")
    previous = None
    for index, item in enumerate(checkpoints):
        validate(item)
        if item["sequence"] != index or item["prev_digest"] != previous: raise ContractError("checkpoint chain is not monotonic")
        previous = item["checkpoint_digest"]
    return list(checkpoints)
def validate_child_budget(child: dict[str, Any], parent: dict[str, Any]) -> dict[str, Any]: return validate(child, parent_budget=parent)

def _records_map(records: Mapping[str, Any] | Sequence[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    values = list(records.values()) if isinstance(records, Mapping) else list(records); result = {}
    for item in values:
        if not isinstance(item, dict): raise ContractError("record must be an object")
        if item.get("kind") in KINDS:
            validate(item); field = DIGEST_FIELD[item["kind"]]
        else:
            # Assignment/candidate/evidence are owned by the execution-fabric
            # layer.  They are accepted here only as immutable adjuncts, never
            # as substitutes for an MVP record.
            if not isinstance(item, dict) or not isinstance(item.get("id"), str): raise ContractError("adjunct record id is required")
            field = next((name for name in ("assignment_digest", "candidate_digest", "evidence_digest", "digest") if name in item), None)
            if field is None: raise ContractError("adjunct record digest is required")
            _digest(item[field], field)
            if item[field] != hashlib.sha256(canonical_json({k: v for k, v in item.items() if k != field})).hexdigest(): raise ContractError("adjunct digest mismatch")
        result[item["id"]] = item; result[item[field]] = item
    return result
def validate_cross_records(records: Mapping[str, Any] | Sequence[dict[str, Any]], *, observed_at: str | _dt.datetime | None = None, reference_time: str | _dt.datetime | None = None) -> list[dict[str, Any]]:
    values = list(records.values()) if isinstance(records, Mapping) else list(records); by_id = _records_map(values); ref = observed_at if observed_at is not None else reference_time
    for item in values:
        kind, task = item["kind"], by_id.get(item.get("task_id"))
        if kind == "task" and item.get("parent_task_id") is not None:
            parent = by_id.get(item["parent_task_id"])
            if not parent or parent.get("kind") != "task": raise ContractError("unknown parent task")
            validate(item, parent_task=parent, observed_at=ref)
        if kind in {"capability_grant","budget","receipt","checkpoint","verification","recovery"}:
            if not task or task.get("kind") != "task" or item.get("task_digest") != task.get("task_digest"): raise ContractError(f"{kind} task binding mismatch")
        if kind == "capability_grant":
            if not _subset(item["allowed_paths"], task["allowed_paths"]) or not set(item["capabilities"]).issubset(task["requested_capabilities"]): raise ContractError("grant exceeds task")
        elif kind == "budget" and item["parent_budget_id"] is not None:
            parent = by_id.get(item["parent_budget_id"])
            if not parent or parent.get("kind") != "budget": raise ContractError("unknown parent budget")
            validate(item, parent_budget=parent, observed_at=ref)
        elif kind == "receipt":
            assignment = by_id.get(item["assignment_digest"])
            if not assignment or assignment.get("kind") != "assignment": raise ContractError("assignment binding mismatch")
        elif kind == "checkpoint":
            prior = by_id.get(item["prev_digest"]) if item["prev_digest"] else None
            if item["sequence"] == 0 and prior is not None: raise ContractError("genesis checkpoint has predecessor")
            if item["sequence"] > 0 and (not prior or prior.get("kind") != "checkpoint" or prior.get("task_digest") != item["task_digest"] or prior.get("sequence") != item["sequence"] - 1): raise ContractError("checkpoint predecessor mismatch")
        elif kind == "verification":
            receipt, verifier = by_id.get(item["receipt_digest"]), by_id.get(item["verifier_task_id"])
            if not receipt or receipt.get("kind") != "receipt": raise ContractError("verification receipt mismatch")
            for name in ("task_id","task_digest","candidate_id","candidate_commit","result_digest"):
                if item[name] != receipt[name]: raise ContractError("verification receipt/candidate mismatch")
            candidate = by_id.get(item["candidate_digest"])
            if not candidate or candidate.get("kind") != "candidate": raise ContractError("verification candidate binding mismatch")
            for name in ("task_digest", "candidate_id", "candidate_commit", "result_digest"):
                if name in candidate and item[name] != candidate[name]: raise ContractError("verification candidate binding mismatch")
            evidence = by_id.get(item["evidence_digest"])
            if not evidence or evidence.get("kind") != "evidence" or evidence.get("task_digest", item["task_digest"]) != item["task_digest"]: raise ContractError("verification evidence binding mismatch")
            if not verifier or verifier.get("kind") != "task" or verifier.get("task_digest") != item["verifier_task_digest"]: raise ContractError("verifier task binding mismatch")
            if verifier["id"] == task["id"] or verifier["task_digest"] == task["task_digest"]: raise ContractError("self-verification")
            if verifier.get("parent_task_id") == task["id"] and verifier.get("parent_task_digest") != task["task_digest"]: raise ContractError("verifier parent identity mismatch")
        elif kind == "recovery":
            checkpoint, receipt = by_id.get(item["prior_checkpoint_digest"]), by_id.get(item["prior_receipt_digest"])
            if not checkpoint or checkpoint.get("kind") != "checkpoint" or checkpoint.get("task_digest") != item["task_digest"]: raise ContractError("recovery checkpoint binding mismatch")
            if not receipt or receipt.get("kind") != "receipt" or receipt.get("task_digest") != item["task_digest"]: raise ContractError("recovery receipt binding mismatch")
    return values
def validate_cross_record(record: dict[str, Any], records: Mapping[str, Any] | Sequence[dict[str, Any]] | None = None, **kwargs: Any) -> dict[str, Any]:
    if records is None: records = [record, *[value for value in kwargs.values() if isinstance(value, dict)]]
    validate_cross_records(records, observed_at=kwargs.get("observed_at"), reference_time=kwargs.get("reference_time")); return record
validate_records = validate_cross_records

def validate_supervisor(record: dict[str, Any], **kwargs: Any) -> dict[str, Any]: return validate(record, **kwargs)
def validate_task(record: dict[str, Any], **kwargs: Any) -> dict[str, Any]: return validate(record, **kwargs)
def validate_capability_grant(record: dict[str, Any], **kwargs: Any) -> dict[str, Any]: return validate(record, **kwargs)
def validate_budget(record: dict[str, Any], **kwargs: Any) -> dict[str, Any]: return validate(record, **kwargs)
def validate_receipt(record: dict[str, Any], **kwargs: Any) -> dict[str, Any]: return validate(record, **kwargs)
def validate_checkpoint(record: dict[str, Any], **kwargs: Any) -> dict[str, Any]: return validate(record, **kwargs)
def validate_verification(record: dict[str, Any], **kwargs: Any) -> dict[str, Any]: return validate(record, **kwargs)
def validate_recovery(record: dict[str, Any], **kwargs: Any) -> dict[str, Any]: return validate(record, **kwargs)
