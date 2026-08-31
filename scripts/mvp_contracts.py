"""Strict, deterministic Recursion v2 MVP contracts.

This module deliberately has no execution side effects.  Records are plain JSON,
with an SHA-256 digest over canonical JSON (excluding the record's own digest).
"""
from __future__ import annotations
import datetime as _dt, hashlib, json, math, re
from typing import Any

SCHEMA_VERSION = 2
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")
KINDS = {"supervisor", "task", "capability_grant", "budget", "receipt", "checkpoint", "verification", "recovery"}

FIELDS = {
 "supervisor": {"schema_version","kind","id","parent_goal","policy_digest","created_at","expires_at"},
 "task": {"schema_version","kind","id","project_id","source_repository","source_branch","source_sha","parent_goal","parent_task_id","depth","allowed_paths","requested_capabilities","gate_digest","created_at"},
 "capability_grant": {"schema_version","kind","id","task_id","capabilities","allowed_paths","network_policy","endpoints","expires_at","grant_digest"},
 "budget": {"schema_version","kind","id","task_id","parent_budget_id","token_limit","wall_seconds","concurrency_limit","cost_limit_usd","metered_spend_allowed","calendar_month_ceiling_usd","remaining_tokens","remaining_wall_seconds","remaining_cost_usd"},
 "receipt": {"schema_version","kind","id","task_id","assignment_digest","adapter","candidate_commit","result_digest","usage","checkpoint_digests","receipt_digest"},
 "checkpoint": {"schema_version","kind","id","task_id","sequence","prev_digest","state_digest","created_at","checkpoint_digest"},
 "verification": {"schema_version","kind","id","task_id","receipt_digest","candidate_digest","gate_digest","evidence_digest","verifier_task_id","verified_at"},
 "recovery": {"schema_version","kind","id","task_id","prior_checkpoint_digest","prior_receipt_digest","action","state","created_at","recovery_digest"},
}
DIGEST_FIELD = {"capability_grant":"grant_digest","receipt":"receipt_digest","checkpoint":"checkpoint_digest","recovery":"recovery_digest"}
REQUIRED = {
 "supervisor":{"schema_version","kind","id","parent_goal","policy_digest","created_at"},
 "task":{"schema_version","kind","id","project_id","source_repository","source_branch","source_sha","parent_goal","depth","allowed_paths","requested_capabilities","gate_digest","created_at"},
 "capability_grant":{"schema_version","kind","id","task_id","capabilities","allowed_paths","network_policy","endpoints","expires_at","grant_digest"},
 "budget":{"schema_version","kind","id","task_id","token_limit","wall_seconds","concurrency_limit","cost_limit_usd","metered_spend_allowed","calendar_month_ceiling_usd"},
 "receipt":{"schema_version","kind","id","task_id","assignment_digest","adapter","candidate_commit","result_digest","usage","checkpoint_digests","receipt_digest"},
 "checkpoint":{"schema_version","kind","id","task_id","sequence","prev_digest","state_digest","created_at","checkpoint_digest"},
 "verification":{"schema_version","kind","id","task_id","receipt_digest","candidate_digest","gate_digest","evidence_digest","verifier_task_id","verified_at"},
 "recovery":{"schema_version","kind","id","task_id","prior_checkpoint_digest","prior_receipt_digest","action","state","created_at","recovery_digest"},
}
_SECRET = re.compile(r"(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_-]{12,}|bearer\s+\S+|(?:api[_-]?key|password|secret)\s*[:=]|BEGIN [A-Z ]+ PRIVATE KEY)", re.I)

class ContractError(ValueError): pass

def canonical_json(value: Any) -> bytes:
    def reject(x: Any):
        if isinstance(x, float) and not math.isfinite(x): raise ContractError("nonfinite number")
        if isinstance(x, str) and _SECRET.search(x): raise ContractError("secret material")
        if isinstance(x, dict):
            for k,v in x.items():
                if not isinstance(k,str): raise ContractError("object key must be string")
                if k.lower() in {"password", "credential", "credentials", "api_key", "secret", "chain_of_thought", "hidden_reasoning"}: raise ContractError("secret or hidden reasoning field")
                reject(v)
        elif isinstance(x,list):
            for v in x: reject(v)
    reject(value)
    try: return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False, allow_nan=False).encode()
    except (TypeError,ValueError) as e: raise ContractError("not canonical JSON") from e

def digest(record: dict) -> str:
    body = {k:v for k,v in record.items() if k != DIGEST_FIELD.get(record.get("kind"))}
    return hashlib.sha256(canonical_json(body)).hexdigest()

def _str(v, name):
    if not isinstance(v,str) or not v: raise ContractError(f"{name} must be nonempty string")
    if _SECRET.search(v): raise ContractError("secret material")
    return v
def _id(v,name):
    _str(v,name)
    if not ID_RE.fullmatch(v): raise ContractError(f"{name} is not canonical")
def _dig(v,name):
    if not isinstance(v,str) or not DIGEST_RE.fullmatch(v): raise ContractError(f"{name} invalid digest")
def _time(v,name):
    _str(v,name)
    if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ",v): raise ContractError(f"{name} invalid UTC time")
    try: t=_dt.datetime.strptime(v,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=_dt.timezone.utc)
    except ValueError as e: raise ContractError(f"{name} invalid UTC time") from e
    now=_dt.datetime.now(_dt.timezone.utc)
    if t < now-_dt.timedelta(days=366) or t > now+_dt.timedelta(days=366): raise ContractError(f"{name} stale or implausible")
def _list(v,name):
    if not isinstance(v,list) or not v or any(not isinstance(x,str) or not x for x in v) or len(set(v)) != len(v): raise ContractError(f"{name} must be unique nonempty strings")
    for x in v:
        if _SECRET.search(x): raise ContractError("secret material")
def _pathlist(v):
    _list(v,"allowed_paths")
    for p in v:
        if p.startswith(("/","\\")) or "\\" in p or any(x in ("..","") for x in p.split("/")) or "\x00" in p: raise ContractError("path traversal")
def _integer(v,name,minimum=0):
    if isinstance(v,bool) or not isinstance(v,int) or v<minimum: raise ContractError(f"{name} must be integer")
def _number(v,name,minimum=0):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<minimum: raise ContractError(f"{name} invalid number")

def validate(record: dict, *, parent_task: dict|None=None, parent_budget: dict|None=None) -> dict:
    if not isinstance(record,dict): raise ContractError("record must be object")
    kind=record.get("kind")
    if kind not in KINDS: raise ContractError("unknown kind")
    if set(record) != FIELDS[kind] or not REQUIRED[kind] <= set(record): raise ContractError("unknown or missing field")
    if record.get("schema_version") != 2 or isinstance(record.get("schema_version"),bool): raise ContractError("schema_version must be 2")
    _id(record["id"],"id")
    # all textual values are secret-scanned; this also catches nested usage/state.
    canonical_json(record)
    if kind in ("supervisor","task"): _time(record["created_at"],"created_at")
    if kind=="supervisor":
        _id(record["parent_goal"],"parent_goal"); _dig(record["policy_digest"],"policy_digest")
        if record["expires_at"] is not None: _time(record["expires_at"],"expires_at")
    elif kind=="task":
        for n in ("project_id","parent_goal"): _id(record[n],n)
        if record["parent_task_id"] is not None: _id(record["parent_task_id"],"parent_task_id")
        _integer(record["depth"],"depth");
        if record["depth"]>2: raise ContractError("orchestration depth exceeds 2")
        if parent_task and record["depth"] != parent_task["depth"]+1: raise ContractError("invalid child depth")
        _str(record["source_repository"],"source_repository"); _str(record["source_branch"],"source_branch")
        if not SHA_RE.fullmatch(record["source_sha"]): raise ContractError("source_sha invalid")
        _pathlist(record["allowed_paths"]); _list(record["requested_capabilities"],"requested_capabilities"); _dig(record["gate_digest"],"gate_digest")
    elif kind=="capability_grant":
        _id(record["task_id"],"task_id"); _list(record["capabilities"],"capabilities"); _pathlist(record["allowed_paths"]); _list(record["endpoints"],"endpoints"); _str(record["network_policy"],"network_policy"); _time(record["expires_at"],"expires_at"); _dig(record["grant_digest"],"grant_digest")
        if record["grant_digest"] != digest(record): raise ContractError("grant digest mismatch")
    elif kind=="budget":
        _id(record["task_id"],"task_id");
        if record["parent_budget_id"] is not None: _id(record["parent_budget_id"],"parent_budget_id")
        for n in ("token_limit","wall_seconds","concurrency_limit"): _integer(record[n],n,1)
        _number(record["cost_limit_usd"],"cost_limit_usd"); _number(record["calendar_month_ceiling_usd"],"calendar_month_ceiling_usd")
        if record["calendar_month_ceiling_usd"]>20: raise ContractError("calendar ceiling exceeds USD 20")
        if not isinstance(record["metered_spend_allowed"],bool): raise ContractError("metered_spend_allowed must be boolean")
        for n in ("remaining_tokens","remaining_wall_seconds","remaining_cost_usd"):
            if record[n] is not None: _number(record[n],n)
        if parent_budget:
            if record["parent_budget_id"] != parent_budget.get("id"): raise ContractError("child budget parent mismatch")
            if record["token_limit"]>parent_budget["token_limit"] or record["wall_seconds"]>parent_budget["wall_seconds"] or record["concurrency_limit"]>parent_budget["concurrency_limit"] or record["cost_limit_usd"]>parent_budget["cost_limit_usd"]: raise ContractError("child budget escalation")
            if record["remaining_tokens"] is not None and parent_budget.get("remaining_tokens") is not None and record["remaining_tokens"] > parent_budget["remaining_tokens"]: raise ContractError("child token remainder escalation")
            if record["remaining_wall_seconds"] is not None and parent_budget.get("remaining_wall_seconds") is not None and record["remaining_wall_seconds"] > parent_budget["remaining_wall_seconds"]: raise ContractError("child wall remainder escalation")
            if record["remaining_cost_usd"] is not None and parent_budget.get("remaining_cost_usd") is not None and record["remaining_cost_usd"] > parent_budget["remaining_cost_usd"]: raise ContractError("child cost remainder escalation")
    elif kind=="receipt":
        _id(record["task_id"],"task_id"); _dig(record["assignment_digest"],"assignment_digest"); _str(record["adapter"],"adapter");
        if not SHA_RE.fullmatch(record["candidate_commit"]): raise ContractError("candidate_commit invalid")
        _dig(record["result_digest"],"result_digest");
        if not isinstance(record["usage"],dict): raise ContractError("usage must object")
        _list(record["checkpoint_digests"],"checkpoint_digests"); _dig(record["receipt_digest"],"receipt_digest")
        if record["receipt_digest"] != digest(record): raise ContractError("receipt digest mismatch")
    elif kind=="checkpoint":
        _id(record["task_id"],"task_id"); _integer(record["sequence"],"sequence");
        if record["prev_digest"] is not None: _dig(record["prev_digest"],"prev_digest")
        _dig(record["state_digest"],"state_digest"); _time(record["created_at"],"created_at"); _dig(record["checkpoint_digest"],"checkpoint_digest")
        if record["checkpoint_digest"] != digest(record): raise ContractError("checkpoint digest mismatch")
        if record["sequence"]==0 and record["prev_digest"] is not None: raise ContractError("genesis checkpoint has predecessor")
        if record["sequence"]>0 and record["prev_digest"] is None: raise ContractError("checkpoint chain gap")
    elif kind=="verification":
        _id(record["task_id"],"task_id"); _dig(record["receipt_digest"],"receipt_digest"); _dig(record["candidate_digest"],"candidate_digest"); _dig(record["gate_digest"],"gate_digest"); _dig(record["evidence_digest"],"evidence_digest"); _id(record["verifier_task_id"],"verifier_task_id"); _time(record["verified_at"],"verified_at")
        if record["verifier_task_id"]==record["task_id"]: raise ContractError("self-verification")
    elif kind=="recovery":
        _id(record["task_id"],"task_id"); _dig(record["prior_checkpoint_digest"],"prior_checkpoint_digest"); _dig(record["prior_receipt_digest"],"prior_receipt_digest"); _str(record["action"],"action"); _str(record["state"],"state"); _time(record["created_at"],"created_at"); _dig(record["recovery_digest"],"recovery_digest")
        if record["recovery_digest"] != digest(record): raise ContractError("recovery digest mismatch")
    return record

def validate_contract(record: dict, **kwargs) -> dict: return validate(record, **kwargs)
def canonical_digest(record: dict) -> str: return digest(record)
def canonicalize(record: dict) -> bytes: return canonical_json(record)
def compute_digest(record: dict) -> str: return digest(record)
def validate_child_budget(child: dict, parent: dict) -> dict: return validate(child, parent_budget=parent)
def validate_checkpoint_chain(checkpoints: list[dict]) -> list[dict]:
    previous = None
    for i, item in enumerate(checkpoints):
        validate(item)
        if item["sequence"] != i or item["prev_digest"] != previous: raise ContractError("checkpoint chain mismatch")
        previous = item["checkpoint_digest"]
    return checkpoints
