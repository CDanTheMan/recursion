"""Pure, bounded task-packet kernel.

The authoritative wire-record rules live in :mod:`mvp_contracts`.  This module is
computation-only: it has no filesystem, process, network, git, scheduler, lease,
budget-ledger, store, or verifier side effects.
"""
from __future__ import annotations

import copy
import hashlib
import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import mvp_contracts as contracts

MAX_BYTES = contracts.MAX_BYTES
MAX_ITEMS = 256
MAX_EVIDENCE = 128
MAX_DEPTH = 2


class KernelError(ValueError):
    """Fail-closed packet admission error."""


def _plain(value: Any) -> Any:
    """Thaw all mapping/list implementations before canonical serialization."""
    if isinstance(value, Mapping):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _canonical(value: Any, limits: "KernelLimits | None" = None) -> bytes:
    try:
        encoded = contracts.canonical_json(_plain(value))
    except contracts.ContractError as exc:
        raise KernelError(str(exc)) from exc
    if limits is not None and len(encoded) > limits.max_bytes:
        raise KernelError("JSON byte limit exceeded")
    return encoded


def _sha(value: Any, limits: "KernelLimits | None" = None) -> str:
    return hashlib.sha256(_canonical(value, limits)).hexdigest()


def _record_digest(record: Mapping[str, Any]) -> str:
    try:
        return contracts.digest(_plain(record))
    except contracts.ContractError as exc:
        raise KernelError(str(exc)) from exc


def _contract(record: Any, *, parent_task: dict[str, Any] | None = None,
              parent_budget: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise KernelError("record must be an object")
    try:
        return contracts.validate(_plain(record), parent_task=parent_task,
                                  parent_budget=parent_budget)
    except contracts.ContractError as exc:
        raise KernelError(str(exc)) from exc


@dataclass(frozen=True)
class KernelLimits:
    max_bytes: int = MAX_BYTES
    max_tokens: int = 16_384
    max_items: int = MAX_ITEMS
    max_evidence: int = MAX_EVIDENCE
    max_depth: int = MAX_DEPTH

    def __post_init__(self) -> None:
        values = (self.max_bytes, self.max_tokens, self.max_items, self.max_evidence)
        if any(type(value) is not int or value < 1 for value in values):
            raise KernelError("invalid kernel limits")
        if self.max_depth != MAX_DEPTH:
            raise KernelError("max_depth must be exactly 2")
        if self.max_bytes > MAX_BYTES or self.max_items > contracts.MAX_LIST:
            raise KernelError("kernel limits exceed contract limits")

    def to_dict(self) -> dict[str, int]:
        return {"max_bytes": self.max_bytes, "max_tokens": self.max_tokens,
                "max_items": self.max_items, "max_evidence": self.max_evidence,
                "max_depth": self.max_depth}

    @classmethod
    def from_value(cls, value: Any) -> "KernelLimits":
        fields = {"max_bytes", "max_tokens", "max_items", "max_evidence", "max_depth"}
        if not isinstance(value, Mapping) or set(value) != fields:
            raise KernelError("packet limits are not strict")
        try:
            return cls(**{key: value[key] for key in fields})
        except TypeError as exc:
            raise KernelError("invalid kernel limits") from exc


class MappingProxy(Mapping[str, Any]):
    """Immutable mapping that is always thawed before canonical JSON."""
    __slots__ = ("_data",)

    def __init__(self, data: Mapping[str, Any]):
        self._data = dict(data)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxy({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


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


_PACKET_FIELDS = {
    "schema_version", "supervisor", "supervisor_digest", "task", "assignment",
    "budget", "grant", "depth", "pause", "pause_epoch", "context",
    "evidence_refs", "checkpoint", "checkpoint_chain", "receipt", "candidate",
    "evidence", "limits", "parent",
}
_CONTEXT_FIELDS = {"id", "summary", "priority", "mandatory", "sequence", "digest",
                   "evidence_refs"}
_REF_FIELDS = {"id", "sha256"}
_ASSIGNMENT_FIELDS = {"kind", "id", "task_id", "task_digest", "assignment_digest",
                      "source_repository", "source_branch", "source_sha"}
_RAW_CONTEXT_LABEL = re.compile(
    r"^(?:(?:raw|original)\s+)?(?:prompt|message|messages|transcript|conversation)\s*[:=]"
    r"|^private\s+output\s*[:=]"
)


def _has_raw_context_content(value: str) -> bool:
    """Reject bounded, explicitly labelled raw/private context payloads only."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    folded = "".join(
        " " if char.isspace() or unicodedata.category(char) in {"Cf", "Pc", "Pd"}
        else char
        for char in normalized
    )
    # Keep this classifier narrow: ordinary prose such as "conversation summary"
    # remains admissible; only reserved labels that introduce a payload are banned.
    return _RAW_CONTEXT_LABEL.search(folded[:512]) is not None


def _ref(value: Any, limits: KernelLimits) -> dict[str, str]:
    if not isinstance(value, Mapping) or set(value) != _REF_FIELDS:
        raise KernelError("evidence ref must be canonical id+sha256")
    result = _plain(value)
    if (not isinstance(result["id"], str) or not isinstance(result["sha256"], str)
            or not contracts.ID_RE.fullmatch(result["id"])
            or not contracts.DIGEST_RE.fullmatch(result["sha256"])):
        raise KernelError("evidence ref must be canonical id+sha256")
    _canonical(result, limits)
    return result


def _refs(values: Any, limits: KernelLimits) -> list[dict[str, str]]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise KernelError("evidence refs are bounded")
    if len(values) > limits.max_evidence:
        raise KernelError("evidence refs are bounded")
    result = [_ref(item, limits) for item in values]
    if len({(item["id"], item["sha256"]) for item in result}) != len(result):
        raise KernelError("duplicate evidence ref")
    return result


def _context_item(item: Any, limits: KernelLimits, sequence: int | None = None) -> dict[str, Any]:
    if not isinstance(item, Mapping):
        raise KernelError("context item must be an object")
    row = _plain(item)
    if set(row) - _CONTEXT_FIELDS:
        raise KernelError("context permits summaries and evidence only")
    if "summary" not in row or not isinstance(row["summary"], str) or not row["summary"].strip():
        raise KernelError("context summary required")
    if _has_raw_context_content(row["summary"]):
        raise KernelError("context summary contains raw or private content")
    if "id" in row and (not isinstance(row["id"], str)
                         or not contracts.ID_RE.fullmatch(row["id"])):
        raise KernelError("context id is not canonical")
    for name in ("priority", "sequence"):
        if name in row and (type(row[name]) is not int or row[name] < 0):
            raise KernelError(f"context {name} is not a nonnegative integer")
    if "mandatory" in row and type(row["mandatory"]) is not bool:
        raise KernelError("context mandatory must be boolean")
    if sequence is not None:
        row.setdefault("sequence", sequence)
    row.setdefault("priority", 0)
    row.setdefault("mandatory", False)
    if "evidence_refs" in row:
        row["evidence_refs"] = _refs(row["evidence_refs"], limits)
    unsigned = dict(row)
    supplied = unsigned.pop("digest", None)
    actual = _sha(unsigned)
    if supplied is not None and (not isinstance(supplied, str) or supplied != actual):
        raise KernelError("context digest mismatch")
    row["digest"] = actual
    # Structural/safety validation is independent of the packet's persisted
    # aggregate limit.  Retention decides whether optional rows fit as a group.
    _canonical(row)
    return row


def _validate_assignment(assignment: Mapping[str, Any], task: Mapping[str, Any]) -> None:
    """Validate the optional, strict assignment source projection."""
    value = _plain(assignment)
    if set(value) - _ASSIGNMENT_FIELDS:
        raise KernelError("assignment has unknown fields")
    source_fields = {"source_repository", "source_branch", "source_sha"}
    present = source_fields & set(value)
    if present and present != source_fields:
        raise KernelError("assignment source projection is incomplete")
    if present and any(value[name] != task[name] for name in source_fields):
        raise KernelError("assignment source binding mismatch")


def _validate_aggregate(body: Mapping[str, Any], limits: KernelLimits) -> None:
    """Apply persisted aggregate byte/token bounds to the exact packet body."""
    try:
        encoded = _canonical(body)
    except KernelError:
        raise
    if len(encoded) > limits.max_bytes:
        raise KernelError("packet JSON byte limit exceeded")
    if math.ceil(len(encoded) / 4) > limits.max_tokens:
        raise KernelError("packet token limit exceeded")


def _records(*, supervisor: Mapping[str, Any], task: Mapping[str, Any],
             assignment: Mapping[str, Any], budget: Mapping[str, Any],
             grant: Mapping[str, Any], checkpoint: Mapping[str, Any] | None = None,
             checkpoint_chain: Sequence[Mapping[str, Any]] = (),
             receipt: Mapping[str, Any] | None = None,
             candidate: Mapping[str, Any] | None = None,
             evidence: Sequence[Mapping[str, Any]] = (),
             parent_task: Mapping[str, Any] | None = None,
             parent_budget: Mapping[str, Any] | None = None,
             parent_lineage: Sequence[Mapping[str, Any]] = ()) -> None:
    values = [_plain(item) for item in (supervisor, task, assignment, budget, grant)]
    if parent_task is not None:
        values.append(_plain(parent_task))
    if parent_budget is not None:
        values.append(_plain(parent_budget))
    for item in parent_lineage:
        values.extend((_plain(item["task"]), _plain(item["budget"])))
    values.extend(_plain(item) for item in checkpoint_chain)
    if checkpoint is not None:
        values.append(_plain(checkpoint))
    if receipt is not None:
        values.append(_plain(receipt))
    if candidate is not None:
        values.append(_plain(candidate))
    values.extend(_plain(item) for item in evidence)
    try:
        contracts.validate_cross_records(values)
    except contracts.ContractError as exc:
        raise KernelError(str(exc)) from exc


def _paths_subset(child: Sequence[str], parent: Sequence[str]) -> bool:
    return all(any(item == base or item.startswith(base.rstrip("/") + "/") for base in parent)
               for item in child)


def _validate_child_semantics(parent: TaskPacket, body: Mapping[str, Any]) -> None:
    p = parent.to_dict()
    pt, t = p["task"], body["task"]
    if body["supervisor_digest"] != p["supervisor_digest"] or body["pause_epoch"] != p["pause_epoch"]:
        raise KernelError("child supervisor identity or pause epoch changed")
    for field in ("project_id", "source_repository", "source_branch", "source_sha", "parent_goal"):
        if t[field] != pt[field]:
            raise KernelError("child identity escalation")
    try:
        contracts.validate(t, parent_task=pt)
    except contracts.ContractError as exc:
        raise KernelError(str(exc)) from exc
    pa, a = p["assignment"], body["assignment"]
    if a["id"] != pa["id"]:
        raise KernelError("child assignment identity changed")
    if (set(a) - {"task_id", "task_digest", "assignment_digest"}
            != set(pa) - {"task_id", "task_digest", "assignment_digest"}):
        raise KernelError("child assignment identity changed")
    for key in set(pa) - {"task_id", "task_digest", "assignment_digest"}:
        if a.get(key) != pa.get(key):
            raise KernelError("child assignment identity changed")
    pg, g = p["grant"], body["grant"]
    if g["id"] != pg["id"] or g["network_policy"] != pg["network_policy"]:
        raise KernelError("child grant identity or network policy changed")
    if not set(g["capabilities"]).issubset(pg["capabilities"]):
        raise KernelError("child grant capability escalation")
    if not _paths_subset(g["allowed_paths"], pg["allowed_paths"]):
        raise KernelError("child grant path escalation")
    if not set(g["endpoints"]).issubset(pg["endpoints"]):
        raise KernelError("child grant endpoint escalation")
    if g["issued_at"] < pg["issued_at"] or g["expires_at"] > pg["expires_at"]:
        raise KernelError("child grant validity escalation")
    pb, b = p["budget"], body["budget"]
    if b["parent_budget_id"] != pb["id"] or b["id"] != t["budget_id"]:
        raise KernelError("child budget lineage mismatch")
    try:
        contracts.validate(b, parent_budget=pb)
    except contracts.ContractError as exc:
        raise KernelError(str(exc)) from exc
    for field in ("token_limit", "wall_seconds", "concurrency_limit", "cost_limit_cents",
                  "calendar_month_ceiling_cents", "remaining_tokens", "remaining_wall_seconds",
                  "remaining_cost_cents"):
        if b[field] > pb[field]:
            raise KernelError("child budget escalation")
    for field in ("metered_spend_allowed", "approval_digest"):
        if b[field] != pb[field]:
            raise KernelError("child budget approval escalation")
    if body["limits"] != p["limits"]:
        raise KernelError("child kernel limits changed")


def _validate_semantics(body: Mapping[str, Any], limits: KernelLimits,
                        *, parent: TaskPacket | None = None,
                        _snapshot_depth: int = 0) -> None:
    if set(body) != _PACKET_FIELDS:
        raise KernelError("packet fields are not strict")
    for name in ("supervisor", "task", "assignment", "budget", "grant"):
        if not isinstance(body[name], Mapping):
            raise KernelError(f"packet {name} record is invalid")
    if type(body["schema_version"]) is not int or body["schema_version"] != 1:
        raise KernelError("packet schema_version must be 1")
    if type(body["depth"]) is not int or body["depth"] != body["task"]["depth"]:
        raise KernelError("packet depth binding mismatch")
    if body["depth"] < 0 or body["depth"] > MAX_DEPTH:
        raise KernelError("packet depth is out of range")
    if body["supervisor_digest"] != body["supervisor"]["supervisor_digest"]:
        raise KernelError("supervisor digest binding mismatch")
    _validate_assignment(body["assignment"], body["task"])
    if body["task"]["parent_goal"] != body["supervisor"]["parent_goal"]:
        raise KernelError("supervisor task goal binding mismatch")
    if body["pause"] is not False:
        raise KernelError("paused packet cannot be admitted")
    if type(body["pause_epoch"]) is not int or body["pause_epoch"] < 0:
        raise KernelError("pause epoch is invalid")
    if body["pause_epoch"] != body["supervisor"].get("pause_epoch"):
        raise KernelError("pause epoch binding mismatch")
    for record in (body["supervisor"], body["task"], body["assignment"], body["budget"], body["grant"]):
        _canonical(record, limits)
    context = body["context"]
    if not isinstance(context, list) or len(context) > limits.max_items:
        raise KernelError("context item limit exceeded")
    normalized = [_context_item(item, limits) for item in context]
    if normalized != context:
        raise KernelError("context is not canonical")
    refs = _refs(body["evidence_refs"], limits)
    if refs != body["evidence_refs"]:
        raise KernelError("evidence refs are not canonical")
    evidence = body["evidence"]
    if not isinstance(evidence, list) or len(evidence) > limits.max_evidence:
        raise KernelError("evidence records are bounded")
    evidence_by_ref = {(_plain(item).get("id"), _record_digest(item)): _plain(item) for item in evidence}
    for ref in refs:
        if (ref["id"], ref["sha256"]) not in evidence_by_ref:
            raise KernelError("evidence ref is not declared and bound")
    for item in context:
        for ref in item.get("evidence_refs", []):
            if (ref["id"], ref["sha256"]) not in evidence_by_ref:
                raise KernelError("context evidence ref is not declared and bound")
    chain = body["checkpoint_chain"]
    if not isinstance(chain, list):
        raise KernelError("checkpoint chain is not a list")
    checkpoint = body["checkpoint"]
    if checkpoint is not None:
        if not isinstance(checkpoint, Mapping):
            raise KernelError("checkpoint must be a record")
        cp = _plain(checkpoint)
        if cp["task_id"] != body["task"]["id"] or cp["task_digest"] != body["task"]["task_digest"]:
            raise KernelError("checkpoint task binding mismatch")
        if cp["context_digest"] != _sha(context):
            raise KernelError("checkpoint context binding mismatch")
        base = dict(body)
        base["checkpoint"] = None
        base["checkpoint_chain"] = []
        if cp["packet_digest"] != _sha(base):
            raise KernelError("checkpoint packet binding mismatch")
        try:
            contracts.validate_checkpoint_chain(chain + [cp])
        except contracts.ContractError as exc:
            raise KernelError(str(exc)) from exc
    elif chain:
        raise KernelError("checkpoint history requires a checkpoint")
    parent_snapshot = parent
    if parent_snapshot is None and body["parent"] is not None:
        if not isinstance(body["parent"], Mapping):
            raise KernelError("parent packet snapshot is invalid")
        if _snapshot_depth >= MAX_DEPTH:
            raise KernelError("parent packet snapshot depth exceeded")
        parent_value = _plain(body["parent"])
        if set(parent_value) != _PACKET_FIELDS | {"packet_digest"}:
            raise KernelError("parent packet snapshot is incomplete")
        parent_digest = parent_value.pop("packet_digest", None)
        if (not isinstance(parent_digest, str)
                or parent_digest != hashlib.sha256(_canonical(parent_value)).hexdigest()):
            raise KernelError("parent packet snapshot digest mismatch")
        parent_limits = KernelLimits.from_value(parent_value.get("limits"))
        _validate_semantics(parent_value, parent_limits,
                            _snapshot_depth=_snapshot_depth + 1)
        parent_snapshot = TaskPacket(parent_value, parent_digest)
    parent_task = parent_snapshot.to_dict()["task"] if parent_snapshot is not None else None
    parent_budget = parent_snapshot.to_dict()["budget"] if parent_snapshot is not None else None
    lineage: list[dict[str, Any]] = []
    cursor = parent_snapshot
    while cursor is not None:
        snapshot = cursor.to_dict()
        lineage.append(snapshot)
        nested = snapshot.get("parent")
        cursor = TaskPacket(nested, nested.get("packet_digest", "")) if nested is not None else None
    _records(supervisor=body["supervisor"], task=body["task"], assignment=body["assignment"],
             budget=body["budget"], grant=body["grant"], checkpoint=checkpoint,
             checkpoint_chain=chain, receipt=body["receipt"], candidate=body["candidate"],
             evidence=evidence, parent_task=parent_task, parent_budget=parent_budget,
             parent_lineage=[item for item in lineage[1:]])
    if body["task"]["parent_task_id"] is None and body["depth"] != 0:
        raise KernelError("root task depth mismatch")
    if parent_snapshot is not None:
        _validate_child_semantics(parent_snapshot, body)
    _validate_aggregate(body, limits)


def _make_body(*, supervisor: Mapping[str, Any], task: Mapping[str, Any],
               assignment: Mapping[str, Any], budget: Mapping[str, Any],
               grant: Mapping[str, Any], context: Sequence[Mapping[str, Any]],
               evidence_refs: Sequence[Mapping[str, Any]], limits: KernelLimits,
               checkpoint: Mapping[str, Any] | None, checkpoint_chain: Sequence[Mapping[str, Any]],
               receipt: Mapping[str, Any] | None, candidate: Mapping[str, Any] | None,
               evidence: Sequence[Mapping[str, Any]], parent: TaskPacket | None = None) -> dict[str, Any]:
    sup = _contract(supervisor)
    if sup["pause_observed"] or sup["status"] != "active":
        raise KernelError("PAUSE blocks packet admission")
    task_v = _plain(task)
    if type(task_v.get("depth")) is not int or not 0 <= task_v["depth"] <= MAX_DEPTH:
        raise KernelError("invalid packet depth")
    ctx = [_context_item(item, limits, index) for index, item in enumerate(context)]
    refs = _refs(evidence_refs, limits)
    evidence_v = [_plain(item) for item in evidence]
    chain_v = [_plain(item) for item in checkpoint_chain]
    parent_v = None
    if parent is not None:
        previous = parent.to_dict()
        # Preserve the exact parent body so its packet digest authenticates every
        # field, including context, checkpoints, and the nested lineage.
        parent_v = previous
    body = {
        "schema_version": 1, "supervisor": sup,
        "supervisor_digest": sup["supervisor_digest"], "task": task_v,
        "assignment": _plain(assignment), "budget": _plain(budget), "grant": _plain(grant),
        "depth": task_v["depth"], "pause": False, "pause_epoch": sup["pause_epoch"],
        "context": ctx, "evidence_refs": refs,
        "checkpoint": _plain(checkpoint) if checkpoint is not None else None,
        "checkpoint_chain": chain_v, "receipt": _plain(receipt) if receipt is not None else None,
        "candidate": _plain(candidate) if candidate is not None else None, "evidence": evidence_v,
        "limits": limits.to_dict(), "parent": parent_v,
    }
    _validate_semantics(body, limits, parent=parent)
    raw = _canonical(body, limits)
    digest = hashlib.sha256(raw).hexdigest()
    body["packet_digest"] = digest
    return body


def build_packet(*, task: Mapping[str, Any], assignment: Mapping[str, Any],
                 budget: Mapping[str, Any], grant: Mapping[str, Any],
                 supervisor_digest: str | None = None,
                 supervisor: Mapping[str, Any] | None = None,
                 context: Sequence[Mapping[str, Any]] = (),
                 evidence_refs: Sequence[Mapping[str, Any]] = (),
                 evidence: Sequence[Mapping[str, Any]] = (),
                 candidate: Mapping[str, Any] | None = None,
                 receipt: Mapping[str, Any] | None = None,
                 checkpoint: Mapping[str, Any] | None = None,
                 checkpoint_chain: Sequence[Mapping[str, Any]] = (),
                 pause: bool = False, pause_epoch: int | None = None,
                 limits: KernelLimits | None = None,
                 _parent: TaskPacket | None = None) -> TaskPacket:
    lim = limits or KernelLimits()
    if pause:
        raise KernelError("PAUSE blocks packet admission")
    if supervisor is None:
        raise KernelError("full validated supervisor record is required")
    sup = _plain(supervisor)
    if supervisor_digest is not None and supervisor_digest != sup.get("supervisor_digest"):
        raise KernelError("supervisor digest mismatch")
    if pause_epoch is not None:
        if type(pause_epoch) is not int or pause_epoch < 0:
            raise KernelError("pause epoch is invalid")
        if pause_epoch != sup.get("pause_epoch"):
            raise KernelError("stale or future PAUSE blocks packet admission")
    body = _make_body(supervisor=sup, task=task, assignment=assignment, budget=budget,
                      grant=grant, context=context, evidence_refs=evidence_refs, limits=lim,
                      checkpoint=checkpoint, checkpoint_chain=checkpoint_chain, receipt=receipt,
                      candidate=candidate, evidence=evidence, parent=_parent)
    return TaskPacket(body, body["packet_digest"])


def spawn_child(parent: TaskPacket, *, task: Mapping[str, Any], assignment: Mapping[str, Any],
                budget: Mapping[str, Any], grant: Mapping[str, Any], **kwargs: Any) -> TaskPacket:
    validate_packet(parent)
    if parent["depth"] >= MAX_DEPTH:
        raise KernelError("maximum depth blocks child admission")
    if kwargs.get("pause") or kwargs.get("pause_epoch", parent["pause_epoch"]) > parent["pause_epoch"]:
        raise KernelError("PAUSE blocks child admission")
    limits = kwargs.pop("limits", None)
    if limits is None:
        limits = KernelLimits.from_value(parent["limits"])
    elif limits != KernelLimits.from_value(parent["limits"]):
        raise KernelError("child kernel limits changed")
    child = build_packet(task=task, assignment=assignment, budget=budget, grant=grant,
                        supervisor=parent["supervisor"], supervisor_digest=parent["supervisor_digest"],
                        context=kwargs.pop("context", ()), evidence_refs=kwargs.pop("evidence_refs", ()),
                        evidence=kwargs.pop("evidence", ()), candidate=kwargs.pop("candidate", None),
                        receipt=kwargs.pop("receipt", None), checkpoint=kwargs.pop("checkpoint", None),
                        checkpoint_chain=kwargs.pop("checkpoint_chain", ()), limits=limits,
                        _parent=parent)
    if kwargs:
        raise KernelError("unknown child admission options")
    body = child.to_dict()
    body.pop("packet_digest", None)
    _validate_semantics(body, limits, parent=parent)
    body["packet_digest"] = hashlib.sha256(_canonical(body, limits)).hexdigest()
    return TaskPacket(body, body["packet_digest"])


def retain_context(packet: TaskPacket, items: Sequence[Mapping[str, Any]], *,
                   limits: KernelLimits | None = None, pause: bool | None = None,
                   pause_epoch: int | None = None) -> TaskPacket:
    validate_packet(packet, pause_observed=pause is True, pause_epoch=pause_epoch)
    stored = KernelLimits.from_value(packet["limits"])
    lim = stored if limits is None else limits
    if lim != stored:
        raise KernelError("retention cannot change packet limits")
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        raise KernelError("context items must be a sequence")
    selected = [_context_item(item, lim, index) for index, item in enumerate(items)]
    if len(selected) > lim.max_items:
        raise KernelError("context item limit exceeded")
    key = lambda item: (-item["priority"], item["sequence"], item["digest"])
    ordered = sorted((item for item in selected if item["mandatory"]), key=key)
    ordered += sorted((item for item in selected if not item["mandatory"]), key=key)
    chosen: list[dict[str, Any]] = []
    for item in ordered:
        trial = chosen + [item]
        # Compute selection cost from the exact canonical UTF-8 bytes without
        # raising on the custom limit; optional rows can then be skipped.  Use
        # the whole packet, since its fixed records also consume the budget.
        prospective = packet.to_dict()
        prospective["context"] = trial
        prospective.pop("packet_digest", None)
        encoded = _canonical(prospective)
        estimate = math.ceil(len(encoded) / 4)
        if len(encoded) > lim.max_bytes or estimate > lim.max_tokens or len(trial) > lim.max_items:
            if item["mandatory"]:
                raise KernelError("mandatory context overflows limits")
            continue
        chosen = trial
    body = packet.to_dict()
    body["context"] = chosen
    body.pop("packet_digest", None)
    _validate_semantics(body, lim)
    body["packet_digest"] = hashlib.sha256(_canonical(body, lim)).hexdigest()
    return TaskPacket(body, body["packet_digest"])


def validate_packet(packet: TaskPacket | Mapping[str, Any], *,
                    pause_observed: bool | None = None,
                    pause_epoch: int | None = None,
                    checkpoint: Mapping[str, Any] | None = None) -> TaskPacket:
    if not isinstance(packet, TaskPacket):
        raise KernelError("packet must be immutable TaskPacket")
    body = packet.to_dict()
    supplied = body.pop("packet_digest", None)
    if supplied != packet.packet_digest or supplied != hashlib.sha256(_canonical(body)).hexdigest():
        raise KernelError("packet digest mismatch")
    if pause_observed is True:
        raise KernelError("PAUSE blocks packet admission")
    if pause_epoch is not None and (type(pause_epoch) is not int or pause_epoch < 0 or pause_epoch > body.get("pause_epoch", -1)):
        raise KernelError("late PAUSE blocks packet admission")
    lim = KernelLimits.from_value(body.get("limits"))
    _validate_semantics(body, lim)
    if checkpoint is not None and body.get("checkpoint") != _plain(checkpoint):
        raise KernelError("checkpoint lineage mismatch")
    return packet


__all__ = ["KernelError", "KernelLimits", "TaskPacket", "build_packet", "spawn_child",
           "retain_context", "validate_packet"]
