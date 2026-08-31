"""Pure task-packet and bounded context-retention kernel for Recursion v2.

This is deliberately a computation-only seam.  It does not launch work, own leases,
budgets, receipts, checkpoints, or a scheduler; those remain execution-fabric concerns.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from execution_fabric import digest_record

MAX_BYTES = 262_144
MAX_ITEMS = 256
MAX_EVIDENCE = 128
MAX_DEPTH = 2
_SHA = re.compile(r"^[0-9a-f]{64}$")
_ID = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
_BAD = re.compile(r"(?:chain\s*of\s*thought|private\s+reasoning|hidden\s+reasoning|scratchpad|api[_-]?key|password|secret|bearer\s+)", re.I)
_BAD_KEY = re.compile(r"^(?:password|credential|credentials|api[_-]?key|secret|token|private[_-]?key|private[_-]?reasoning|chain[_-]?of[_-]?thought|cot)$", re.I)


class KernelError(ValueError):
    pass


def _json(value: Any) -> bytes:
    def walk(x: Any, depth: int = 0) -> None:
        if depth > 64:
            raise KernelError("input is too deep")
        if isinstance(x, str):
            if _BAD.search(x):
                raise KernelError("secret or private reasoning material")
        elif isinstance(x, Mapping):
            if len(x) > MAX_ITEMS:
                raise KernelError("object is too large")
            for k, v in x.items():
                if not isinstance(k, str) or _BAD_KEY.search(k):
                    raise KernelError("unsafe or invalid field")
                walk(v, depth + 1)
        elif isinstance(x, (list, tuple)):
            if len(x) > MAX_ITEMS:
                raise KernelError("list is too large")
            for v in x:
                walk(v, depth + 1)
        elif isinstance(x, float) and not math.isfinite(x):
            raise KernelError("nonfinite number")
        elif x is not None and type(x) not in (bool, int, float):
            raise KernelError("value is not JSON data")
    walk(value)
    try:
        out = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()
    except (TypeError, ValueError, OverflowError, UnicodeError, RecursionError) as exc:
        raise KernelError("invalid JSON") from exc
    if len(out) > MAX_BYTES:
        raise KernelError("JSON byte limit exceeded")
    return out


def _digest(value: Mapping[str, Any]) -> str:
    # execution_fabric's digest excludes its conventional `digest` field.
    return digest_record(value)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    return value


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


@dataclass(frozen=True)
class KernelLimits:
    max_bytes: int = MAX_BYTES
    max_tokens: int = 16_384
    max_items: int = MAX_ITEMS
    max_evidence: int = MAX_EVIDENCE
    max_depth: int = MAX_DEPTH

    def __post_init__(self) -> None:
        if any(type(x) is not int or x < 1 for x in (self.max_bytes, self.max_tokens, self.max_items, self.max_evidence)) or self.max_depth != 2:
            raise KernelError("invalid kernel limits")


@dataclass(frozen=True)
class TaskPacket:
    value: Mapping[str, Any]
    packet_digest: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _freeze(_plain(self.value)))

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(_plain(self.value))

    def __getitem__(self, key: str) -> Any:
        return self.value[key]


def _record_digest(record: Any, name: str) -> str:
    if not isinstance(record, Mapping):
        raise KernelError(f"{name} must be an object")
    _json(record)
    field = "assignment_digest" if name == "assignment" else name + "_digest"
    supplied = record.get(field)
    unsigned = dict(record)
    unsigned.pop(field, None)
    actual = _digest(unsigned)
    if supplied is not None and supplied != actual:
        raise KernelError(f"{name} digest mismatch")
    return supplied or actual


def _evidence(refs: Sequence[Mapping[str, Any]], limits: KernelLimits) -> list[dict[str, str]]:
    if not isinstance(refs, Sequence) or isinstance(refs, (str, bytes)) or len(refs) > limits.max_evidence:
        raise KernelError("evidence refs are bounded")
    out = []
    for ref in refs:
        if not isinstance(ref, Mapping) or set(ref) != {"id", "sha256"} or not isinstance(ref["id"], str) or not _ID.fullmatch(ref["id"]) or not isinstance(ref["sha256"], str) or not _SHA.fullmatch(ref["sha256"]):
            raise KernelError("evidence ref must be canonical id+sha256")
        out.append({"id": ref["id"], "sha256": ref["sha256"]})
    if len({(x["id"], x["sha256"]) for x in out}) != len(out):
        raise KernelError("duplicate evidence ref")
    return out


def build_packet(*, task: Mapping[str, Any], assignment: Mapping[str, Any], budget: Mapping[str, Any], grant: Mapping[str, Any], supervisor_digest: str, context: Sequence[Mapping[str, Any]] = (), evidence_refs: Sequence[Mapping[str, Any]] = (), pause: bool = False, checkpoint: Mapping[str, Any] | None = None, limits: KernelLimits | None = None) -> TaskPacket:
    lim = limits or KernelLimits()
    if pause:
        raise KernelError("PAUSE blocks packet admission")
    for name, value in (("task", task), ("assignment", assignment), ("budget", budget), ("grant", grant)):
        _record_digest(value, name)
    if not isinstance(supervisor_digest, str) or not _SHA.fullmatch(supervisor_digest):
        raise KernelError("supervisor digest invalid")
    depth = task.get("depth")
    if type(depth) is not int or not 0 <= depth <= lim.max_depth:
        raise KernelError("invalid packet depth")
    ctx = list(context)
    if len(ctx) > lim.max_items:
        raise KernelError("context item limit exceeded")
    for item in ctx:
        if not isinstance(item, Mapping) or set(item) - {"id", "summary", "priority", "mandatory", "sequence", "digest", "evidence_refs"}:
            raise KernelError("context permits summaries and evidence only")
        if "summary" not in item or not isinstance(item["summary"], str) or not item["summary"].strip():
            raise KernelError("context summary required")
        _json(item)
        if "evidence_refs" in item:
            _evidence(item["evidence_refs"], lim)
    refs = _evidence(evidence_refs, lim)
    body = {"schema_version": 1, "task": _plain(task), "assignment": _plain(assignment), "budget": _plain(budget), "grant": _plain(grant), "supervisor_digest": supervisor_digest, "depth": depth, "pause": False, "context": ctx, "evidence_refs": refs, "checkpoint": _plain(checkpoint) if checkpoint is not None else None}
    raw = _json(body)
    if len(raw) > lim.max_bytes:
        raise KernelError("packet byte limit exceeded")
    packet_digest = hashlib.sha256(raw).hexdigest()
    body["packet_digest"] = packet_digest
    return TaskPacket(body, packet_digest)


def spawn_child(parent: TaskPacket, *, task: Mapping[str, Any], assignment: Mapping[str, Any], budget: Mapping[str, Any], grant: Mapping[str, Any], **kwargs: Any) -> TaskPacket:
    validate_packet(parent)
    if parent["pause"] or parent["depth"] >= 2:
        raise KernelError("PAUSE or maximum depth blocks child admission")
    for field in ("parent_task_id", "parent_task_digest"):
        if field not in task:
            raise KernelError("child parent binding is required")
    if task["parent_task_id"] != parent["task"].get("id") or task["parent_task_digest"] != _record_digest(parent["task"], "task"):
        raise KernelError("child parent binding mismatch")
    if task.get("depth") != parent["depth"] + 1:
        raise KernelError("child depth mismatch")
    for key in ("source_repository", "source_branch", "source_sha", "parent_goal"):
        if task.get(key) != parent["task"].get(key):
            raise KernelError("child identity escalation")
    if not set(task.get("requested_capabilities", ())).issubset(parent["task"].get("requested_capabilities", ())):
        raise KernelError("child capability escalation")
    if not set(task.get("allowed_paths", ())).issubset(parent["task"].get("allowed_paths", ())):
        raise KernelError("child path escalation")
    if assignment.get("assignment_digest") != parent["assignment"].get("assignment_digest"):
        raise KernelError("child assignment escalation")
    if budget.get("task_digest") not in {parent["budget"].get("task_digest"), _record_digest(task, "task")}:
        raise KernelError("child budget binding mismatch")
    return build_packet(task=task, assignment=assignment, budget=budget, grant=grant, supervisor_digest=parent["supervisor_digest"], pause=bool(kwargs.pop("pause", False)), limits=kwargs.pop("limits", None), **kwargs)


def retain_context(packet: TaskPacket, items: Sequence[Mapping[str, Any]], *, limits: KernelLimits | None = None, pause: bool | None = None) -> TaskPacket:
    validate_packet(packet, pause_observed=pause)
    lim = limits or KernelLimits()
    selected = []
    for seq, item in enumerate(items):
        if not isinstance(item, Mapping) or "summary" not in item:
            raise KernelError("context item must be a selected summary")
        row = dict(item); row.setdefault("sequence", seq); row.setdefault("priority", 0); row.setdefault("mandatory", False)
        selected.append(row)
    mandatory = [x for x in selected if x["mandatory"]]
    optional = [x for x in selected if not x["mandatory"]]
    ordered = mandatory + sorted(optional, key=lambda x: (-x["priority"], x["sequence"], _digest(x)))
    chosen = []
    for item in ordered:
        trial = chosen + [item]
        estimate = math.ceil(len(_json(trial)) / 4)
        if len(_json(trial)) > lim.max_bytes or estimate > lim.max_tokens or len(trial) > lim.max_items:
            if item in mandatory:
                raise KernelError("mandatory context overflows limits")
            continue
        chosen = trial
    body = packet.to_dict(); body["context"] = chosen; body["pause"] = bool(pause) if pause is not None else bool(packet["pause"])
    body.pop("packet_digest", None); raw = _json(body); body["packet_digest"] = hashlib.sha256(raw).hexdigest()
    return TaskPacket(body, body["packet_digest"])


def validate_packet(packet: TaskPacket | Mapping[str, Any], *, pause_observed: bool | None = None, checkpoint: Mapping[str, Any] | None = None) -> TaskPacket:
    if not isinstance(packet, TaskPacket):
        raise KernelError("packet must be immutable TaskPacket")
    body = packet.to_dict(); supplied = body.pop("packet_digest", None)
    if supplied != packet.packet_digest or supplied != hashlib.sha256(_json(body)).hexdigest():
        raise KernelError("packet digest mismatch")
    if pause_observed is True:
        raise KernelError("PAUSE blocks packet admission")
    if set(body) != {"schema_version", "task", "assignment", "budget", "grant", "supervisor_digest", "depth", "pause", "context", "evidence_refs", "checkpoint"}:
        raise KernelError("packet fields are not strict")
    if body.get("pause"):
        raise KernelError("paused packet cannot be admitted")
    for name in ("task", "assignment", "budget", "grant"):
        _record_digest(body[name], name)
    _evidence(body["evidence_refs"], KernelLimits())
    if checkpoint is not None and body.get("checkpoint") != _plain(checkpoint):
        raise KernelError("checkpoint lineage mismatch")
    _json(body)
    return packet
