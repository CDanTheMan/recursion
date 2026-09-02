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
import weakref
from dataclasses import dataclass
from types import FunctionType, MappingProxyType
from typing import Any, Mapping, Sequence

import mvp_contracts as contracts

MAX_BYTES = contracts.MAX_BYTES
MAX_ITEMS = 256
MAX_EVIDENCE = 128
MAX_DEPTH = 2


class KernelError(ValueError):
    """Fail-closed packet admission error."""


def _plain(value: Any, *, _active: set[int] | None = None,
           _nodes: list[int] | None = None, _depth: int = 0) -> Any:
    """Thaw containers with explicit cycle/depth/node bounds.

    ``mvp_contracts`` is deliberately defensive, but a caller can still hand the
    kernel a custom Mapping or a self-referential list before contract validation
    gets a chance to run.  Detect those shapes here so they always become a typed
    kernel failure rather than a Python recursion failure.
    """
    if _active is None:
        _active, _nodes = set(), [0]
    assert _nodes is not None
    if _depth > contracts.MAX_DEPTH:
        raise KernelError("JSON depth limit exceeded")
    if isinstance(value, Mapping):
        marker = id(value)
        if marker in _active:
            raise KernelError("cyclic mapping")
        _active.add(marker)
        _nodes[0] += 1
        if _nodes[0] > contracts.MAX_NODES:
            _active.remove(marker)
            raise KernelError("JSON node limit exceeded")
        try:
            return {k: _plain(v, _active=_active, _nodes=_nodes, _depth=_depth + 1)
                    for k, v in value.items()}
        finally:
            _active.remove(marker)
    if isinstance(value, (list, tuple)):
        marker = id(value)
        if marker in _active:
            raise KernelError("cyclic sequence")
        _active.add(marker)
        _nodes[0] += 1
        if _nodes[0] > contracts.MAX_NODES:
            _active.remove(marker)
            raise KernelError("JSON node limit exceeded")
        try:
            return [_plain(v, _active=_active, _nodes=_nodes, _depth=_depth + 1)
                    for v in value]
        finally:
            _active.remove(marker)
    return value


def _canonical(value: Any, limits: "KernelLimits | None" = None) -> bytes:
    try:
        encoded = contracts.canonical_json(_plain(value))
    except (contracts.ContractError, KernelError, RecursionError, TypeError, ValueError) as exc:
        raise KernelError(str(exc)) from exc
    if limits is not None and len(encoded) > limits.max_bytes:
        raise KernelError("JSON byte limit exceeded")
    return encoded


def _sha(value: Any, limits: "KernelLimits | None" = None) -> str:
    try:
        return hashlib.sha256(_canonical(value, limits)).hexdigest()
    except RecursionError as exc:
        raise KernelError("recursive value") from exc


def _record_digest(record: Mapping[str, Any]) -> str:
    try:
        return contracts.digest(_plain(record))
    except (contracts.ContractError, KernelError, RecursionError, TypeError, ValueError) as exc:
        raise KernelError(str(exc)) from exc


def _contract(record: Any, *, parent_task: dict[str, Any] | None = None,
              parent_budget: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise KernelError("record must be an object")
    try:
        return contracts.validate(_plain(record), parent_task=parent_task,
                                  parent_budget=parent_budget)
    except (contracts.ContractError, KernelError, RecursionError, TypeError, ValueError) as exc:
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
        # Keep the backing mapping immutable as well as the public dataclass.
        # A mutable private dict would let a caller alter an issued packet and
        # then attempt to re-sign it in place.
        self._data = MappingProxyType(dict(data))

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __deepcopy__(self, memo: dict[int, Any]) -> "MappingProxy":
        copied = {key: copy.deepcopy(value, memo) for key, value in self._data.items()}
        return MappingProxy(copied)


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

    def __post_init__(self, _freeze_fn=_freeze, _plain_fn=_plain) -> None:
        object.__setattr__(self, "value", _freeze_fn(_plain_fn(self.value)))

    def to_dict(self, _plain_fn=_plain) -> dict[str, Any]:
        return copy.deepcopy(_plain_fn(self.value))

    def __getitem__(self, key: str) -> Any:
        return self.value[key]


def _new_packet_issuance():
    """Return private exact-identity issuance and admission checks.

    The ledger is deliberately held only by these closures.  It contains weak
    references keyed by object identity, so it authenticates the object that a
    factory returned without becoming durable state or retaining packets.
    """
    issued: dict[int, tuple[weakref.ReferenceType[TaskPacket], bytes]] = {}

    def issue(body: Mapping[str, Any] | TaskPacket) -> TaskPacket:
        packet = body if isinstance(body, TaskPacket) else TaskPacket(body, body["packet_digest"])
        identity = id(packet)
        snapshot = contracts.canonical_json(_plain(packet.to_dict()))

        def released(reference: weakref.ReferenceType[TaskPacket]) -> None:
            entry = issued.get(identity)
            if entry is not None and entry[0] is reference:
                issued.pop(identity, None)

        issued[identity] = (weakref.ref(packet, released), snapshot)
        return packet

    def require(packet: Any) -> TaskPacket:
        if not isinstance(packet, TaskPacket):
            raise KernelError("packet must be immutable TaskPacket")
        entry = issued.get(id(packet))
        if entry is None or entry[0]() is not packet:
            raise KernelError("packet was not issued by a kernel factory")
        try:
            current = contracts.canonical_json(_plain(packet.to_dict()))
        except Exception as exc:
            raise KernelError("issued packet was mutated") from exc
        if current != entry[1]:
            raise KernelError("issued packet was mutated")
        return packet

    return issue, require


_packet_issue, _require_issued_packet = _new_packet_issuance()
del _new_packet_issuance


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
_PARENT_REF_FIELDS = {"packet_digest", "task", "assignment", "budget", "grant",
                      "supervisor_digest", "pause_epoch", "limits", "lineage_refs"}
_RAW_CONTEXT_LABEL = re.compile(
    r"(?<![a-z0-9])(?:(?:context|raw|original)\s+)?"
    r"(?:prompt|message|messages|transcript|conversation)\s*[:=]"
    r"|(?<![a-z0-9])private\s+output\s*[:=]"
)
_RAW_CONTEXT_BARE = {"raw prompt", "raw message", "original prompt", "original message",
                     "prompt", "message", "messages", "transcript", "conversation"}


def _has_raw_context_content(value: str) -> bool:
    """Reject bounded, explicitly labelled raw/private context payloads only."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    folded = "".join(
        " " if char.isspace() or unicodedata.category(char).startswith("Z")
        or unicodedata.category(char) in {"Cf", "Pc", "Pd"}
        else char
        for char in normalized
    )
    # Scan the complete contract-bounded summary.  Bare labels are rejected only
    # when they are the complete value; ordinary prose such as "Public summary of
    # the conversation." remains admissible.  Label forms are unsafe anywhere,
    # including after a long benign prefix and with Unicode separators.
    if folded.strip(" \t\r\n.,;!?()[]{}\"'") in _RAW_CONTEXT_BARE:
        return True
    return _RAW_CONTEXT_LABEL.search(folded) is not None


def _parent_reference(parent: TaskPacket) -> dict[str, Any]:
    """Project only the immutable authority needed to validate a child.

    Context, evidence, checkpoints, receipts, candidates, and the nested parent
    are deliberately omitted.  The packet digest remains the external immutable
    anchor for the complete parent packet; the projection is not treated as a
    replacement for that anchor.
    """
    _require_issued_packet(parent)
    p = parent.to_dict()
    prior = p.get("parent")
    prior_refs = prior.get("lineage_refs", ()) if isinstance(prior, Mapping) else ()
    if (not isinstance(prior_refs, Sequence) or isinstance(prior_refs, (str, bytes))
            or any(not isinstance(item, str) for item in prior_refs)):
        raise KernelError("parent lineage is invalid")
    lineage_refs = [parent.packet_digest, *list(prior_refs)]
    if len(lineage_refs) > MAX_DEPTH or len(set(lineage_refs)) != len(lineage_refs):
        raise KernelError("parent lineage is too deep or cyclic")
    return {
        "packet_digest": parent.packet_digest,
        "task": p["task"], "assignment": p["assignment"],
        "budget": p["budget"], "grant": p["grant"],
        "supervisor_digest": p["supervisor_digest"],
        "pause_epoch": p["pause_epoch"], "limits": p["limits"],
        "lineage_refs": lineage_refs,
    }


def _packet_body_digest(packet: TaskPacket) -> str:
    """Recompute a packet's outer digest without trusting its stored value."""
    body = packet.to_dict()
    supplied = body.pop("packet_digest", None)
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if supplied != packet.packet_digest or supplied != actual:
        raise KernelError("packet digest mismatch")
    return actual


def _anchor_reference(anchor: Any, *, expected_digest: str | None = None) -> dict[str, Any]:
    """Resolve an explicit trusted parent anchor to its compact authority view.

    A digest is deliberately never accepted by itself.  A ``TaskPacket`` (or a
    complete persisted packet mapping) supplies the omitted authority records;
    a compact authority mapping is accepted only alongside an independently
    supplied digest.
    """
    if isinstance(anchor, TaskPacket):
        _require_issued_packet(anchor)
        digest = _packet_body_digest(anchor)
        if expected_digest is not None and expected_digest != digest:
            raise KernelError("parent packet digest anchor mismatch")
        return _parent_reference(anchor)
    if not isinstance(anchor, Mapping):
        raise KernelError("trusted parent anchor is required")
    value = _plain(anchor)
    if set(value) == _PARENT_REF_FIELDS:
        digest = value["packet_digest"]
        if expected_digest is None:
            raise KernelError("compact parent anchor requires an independent digest")
        if digest != expected_digest:
            raise KernelError("parent packet digest anchor mismatch")
        return value
    if "packet_digest" not in value or set(value) != _PACKET_FIELDS | {"packet_digest"}:
        raise KernelError("trusted parent anchor is not a complete packet")
    digest = value["packet_digest"]
    body = dict(value)
    body.pop("packet_digest")
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if digest != actual:
        raise KernelError("trusted parent packet digest mismatch")
    if expected_digest is not None and expected_digest != digest:
        raise KernelError("parent packet digest anchor mismatch")
    return _parent_reference(TaskPacket(value, digest))


def _lineage_digests(values: Sequence[Any], immediate_digest: str) -> list[str]:
    """Resolve trusted ancestor anchors, accepting either full or tail form."""
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise KernelError("trusted parent lineage is invalid")
    anchors = list(values)
    if anchors:
        first = anchors[0]
        first_digest = (first.packet_digest if isinstance(first, TaskPacket)
                        else first.get("packet_digest") if isinstance(first, Mapping) else first)
        if first_digest == immediate_digest:
            anchors = anchors[1:]
    result: list[str] = []
    for item in anchors:
        if isinstance(item, str):
            # Bare ancestor digests cannot authenticate omitted authority records.
            raise KernelError("trusted ancestor authority is required")
        result.append(_anchor_reference(item)["packet_digest"])
    return result


def _authority_packet(reference: Mapping[str, Any]) -> dict[str, Any]:
    """Make a narrow packet-shaped view for shared child checks."""
    return {
        "task": _plain(reference["task"]),
        "assignment": _plain(reference["assignment"]),
        "budget": _plain(reference["budget"]),
        "grant": _plain(reference["grant"]),
        "supervisor_digest": reference["supervisor_digest"],
        "pause_epoch": reference["pause_epoch"],
        "limits": _plain(reference["limits"]),
    }


def _authority_chain(anchor: Any) -> list[dict[str, Any]]:
    """Return packet authority projections from an anchor through its parents."""
    if isinstance(anchor, TaskPacket):
        current: Mapping[str, Any] | None = anchor.to_dict()
    elif isinstance(anchor, Mapping):
        current = _plain(anchor)
        if set(current) == _PARENT_REF_FIELDS:
            current = _authority_packet(current)
    else:
        raise KernelError("trusted parent anchor is required")
    result: list[dict[str, Any]] = []
    while isinstance(current, Mapping):
        if not all(name in current for name in ("task", "budget")):
            break
        result.append({"task": _plain(current["task"]),
                       "budget": _plain(current["budget"])})
        prior = current.get("parent")
        if not isinstance(prior, Mapping):
            break
        current = _authority_packet(prior)
    return result


def _validate_parent_reference(reference: Any, child: Mapping[str, Any],
                               limits: KernelLimits, *,
                               expected_parent: Any | None = None,
                               expected_parent_digest: str | None = None,
                               expected_lineage: Sequence[Any] | None = None) -> dict[str, Any]:
    if not isinstance(reference, Mapping):
        raise KernelError("parent authority reference is invalid")
    value = _plain(reference)
    if set(value) != _PARENT_REF_FIELDS:
        raise KernelError("parent authority reference is not strict")
    digest = value["packet_digest"]
    if not isinstance(digest, str) or not contracts.DIGEST_RE.fullmatch(digest):
        raise KernelError("parent packet digest anchor is invalid")
    if expected_parent is None:
        raise KernelError("trusted parent authority is required")
    expected_reference = _anchor_reference(expected_parent,
                                           expected_digest=expected_parent_digest)
    if value != expected_reference:
        raise KernelError("parent authority reference mismatch")
    refs = value["lineage_refs"]
    if (not isinstance(refs, list) or not refs or len(refs) > MAX_DEPTH
            or any(not isinstance(item, str) or not contracts.DIGEST_RE.fullmatch(item) for item in refs)
            or refs[0] != digest or len(set(refs)) != len(refs)):
        raise KernelError("parent packet lineage is invalid")
    if expected_lineage is not None:
        expected = [digest, *_lineage_digests(expected_lineage, digest)]
        if expected != refs:
            raise KernelError("parent packet lineage anchor mismatch")
    elif len(refs) > 1 and expected_parent is None:
        raise KernelError("trusted ancestor packet lineage is required")
    if value["limits"] != limits.to_dict():
        raise KernelError("parent kernel limits changed")
    for name in ("task", "assignment", "budget", "grant"):
        if not isinstance(value[name], Mapping):
            raise KernelError("parent authority record is invalid")
    parent_task = _plain(value["task"])
    parent_budget = _plain(value["budget"])
    parent_assignment = _plain(value["assignment"])
    parent_grant = _plain(value["grant"])
    try:
        contracts.validate(parent_task)
        contracts.validate(parent_budget)
        contracts.validate(parent_grant)
    except contracts.ContractError as exc:
        raise KernelError(str(exc)) from exc
    _validate_assignment(parent_assignment, parent_task)
    if (parent_budget["task_id"] != parent_task["id"]
            or parent_budget["task_digest"] != parent_task["task_digest"]
            or parent_grant["task_id"] != parent_task["id"]
            or parent_grant["task_digest"] != parent_task["task_digest"]):
        raise KernelError("parent authority task binding mismatch")
    if (not _paths_subset(parent_grant["allowed_paths"], parent_task["allowed_paths"])
            or not set(parent_grant["capabilities"]).issubset(parent_task["requested_capabilities"])):
        raise KernelError("parent grant exceeds task")
    if parent_task["depth"] != child["depth"] - 1:
        raise KernelError("parent depth binding mismatch")
    return value


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
    """Validate the complete assignment projection, including immutable source."""
    value = _plain(assignment)
    if set(value) != _ASSIGNMENT_FIELDS:
        raise KernelError("assignment fields are not strict")
    if value.get("kind") != "assignment":
        raise KernelError("assignment kind is invalid")
    if (not isinstance(value.get("id"), str)
            or not contracts.ID_RE.fullmatch(value["id"])
            or value.get("task_id") != task.get("id")
            or value.get("task_digest") != task.get("task_digest")):
        raise KernelError("assignment task binding mismatch")
    source_fields = ("source_repository", "source_branch", "source_sha")
    if any(value[name] != task.get(name) for name in source_fields):
        raise KernelError("assignment source binding mismatch")
    if (not isinstance(value["source_repository"], str)
            or not isinstance(value["source_branch"], str)
            or not isinstance(value["source_sha"], str)
            or not contracts.SHA_RE.fullmatch(value["source_sha"])
            or value["assignment_digest"] != _record_digest(value)):
        raise KernelError("assignment digest or source projection is invalid")


def _validate_aggregate(body: Mapping[str, Any], limits: KernelLimits) -> None:
    """Apply persisted aggregate byte/token bounds to the exact packet body."""
    try:
        encoded = _canonical(body)
    except KernelError:
        raise
    if len(encoded) > limits.max_bytes:
        raise KernelError("packet JSON byte limit exceeded")
    # max_tokens is intentionally scoped to the selected context list.  The
    # packet-wide byte ceiling remains the aggregate admission bound.


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
    values: list[dict[str, Any]] = []

    def add(item: Mapping[str, Any]) -> None:
        value = _plain(item)
        if value not in values:
            values.append(value)

    for item in (supervisor, task, assignment, budget, grant):
        add(item)
    if parent_task is not None:
        add(parent_task)
    if parent_budget is not None:
        add(parent_budget)
    for item in parent_lineage:
        add(item["task"])
        add(item["budget"])
    for item in checkpoint_chain:
        add(item)
    if checkpoint is not None:
        add(checkpoint)
    if receipt is not None:
        add(receipt)
    if candidate is not None:
        add(candidate)
    for item in evidence:
        add(item)
    try:
        contracts.validate_cross_records(values)
    except contracts.ContractError as exc:
        raise KernelError(str(exc)) from exc


def _paths_subset(child: Sequence[str], parent: Sequence[str]) -> bool:
    return all(any(item == base or item.startswith(base.rstrip("/") + "/") for base in parent)
               for item in child)


def _validate_child_semantics(parent: TaskPacket | Mapping[str, Any], body: Mapping[str, Any]) -> None:
    p = parent.to_dict() if isinstance(parent, TaskPacket) else _authority_packet(parent)
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
                        expected_parent: Any | None = None,
                        expected_parent_digest: str | None = None,
                        expected_lineage: Sequence[Any] | None = None) -> None:
    if expected_parent_digest is not None and expected_parent is None:
        raise KernelError("digest-only parent anchors are not trusted")
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
    if math.ceil(len(_canonical(context)) / 4) > limits.max_tokens:
        raise KernelError("context token limit exceeded")
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
        required_checkpoint_fields = ("task_id", "task_digest", "packet_digest",
                                      "context_digest", "sequence", "checkpoint_digest")
        if any(name not in cp for name in required_checkpoint_fields):
            raise KernelError("checkpoint record is incomplete")
        if cp["task_id"] != body["task"]["id"] or cp["task_digest"] != body["task"]["task_digest"]:
            raise KernelError("checkpoint task binding mismatch")
        if cp["context_digest"] != _sha(context):
            raise KernelError("checkpoint context binding mismatch")
        base = dict(body)
        base["checkpoint"] = None
        base["checkpoint_chain"] = []
        checkpoint_base = dict(base)
        # Receipts may refer to a checkpoint, so including the receipt in the
        # checkpoint's packet anchor would create an unresolvable digest cycle.
        # Adjuncts remain in the anchor; only the checkpoint/receipt edge is
        # removed, preserving the packet's selected context and evidence.
        checkpoint_base["receipt"] = None
        if cp["packet_digest"] not in {_sha(base), _sha(checkpoint_base)}:
            raise KernelError("checkpoint packet binding mismatch")
        try:
            contracts.validate_checkpoint_chain(chain + [cp])
        except contracts.ContractError as exc:
            raise KernelError(str(exc)) from exc
    elif chain:
        raise KernelError("checkpoint history requires a checkpoint")
    parent_snapshot = parent
    parent_reference = None
    if body["parent"] is not None:
        parent_reference = _validate_parent_reference(
            body["parent"], body["task"], limits,
            expected_parent=(parent if parent is not None else expected_parent),
            expected_parent_digest=expected_parent_digest,
            expected_lineage=expected_lineage,
        )
        if parent is not None:
            expected_reference = _parent_reference(parent)
            if parent_reference != expected_reference:
                raise KernelError("parent authority reference mismatch")
        parent_task = _plain(parent_reference["task"])
        parent_budget = _plain(parent_reference["budget"])
    else:
        if expected_parent is not None or expected_parent_digest is not None or expected_lineage is not None:
            raise KernelError("unexpected parent packet anchor")
        parent_task = parent_budget = None
    if parent_task is None:
        authority_lineage: list[dict[str, Any]] = []
        if expected_parent is not None:
            authority_lineage.extend(_authority_chain(expected_parent)[1:])
        if expected_lineage is not None:
            for anchor in expected_lineage:
                if not isinstance(anchor, str):
                    authority_lineage.extend(_authority_chain(anchor))
        _records(supervisor=body["supervisor"], task=body["task"], assignment=body["assignment"],
                 budget=body["budget"], grant=body["grant"], checkpoint=checkpoint,
                 checkpoint_chain=chain, receipt=body["receipt"], candidate=body["candidate"],
                 evidence=evidence, parent_lineage=authority_lineage)
    else:
        # Use the same complete record collector for child packets.  The compact
        # parent projection contributes immediate task/budget authority while
        # every child adjunct is contract- and cross-record validated together.
        _records(supervisor=body["supervisor"], task=body["task"],
                 assignment=body["assignment"], budget=body["budget"],
                 grant=body["grant"], checkpoint=checkpoint,
                 checkpoint_chain=chain, receipt=body["receipt"],
                 candidate=body["candidate"], evidence=evidence,
                 parent_task=parent_task, parent_budget=parent_budget,
                 parent_lineage=(_authority_chain(parent)[1:] if parent is not None
                                 else _authority_chain(expected_parent)[1:] if expected_parent is not None
                                 else ()))
    if body["task"]["parent_task_id"] is None and body["depth"] != 0:
        raise KernelError("root task depth mismatch")
    if parent_snapshot is not None:
        _validate_child_semantics(parent_snapshot, body)
    elif parent_reference is not None:
        _validate_child_semantics(parent_reference, body)
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
        parent_v = _parent_reference(parent)
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


def _build_packet_impl(*, task: Mapping[str, Any], assignment: Mapping[str, Any],
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


def _spawn_child_impl(parent: TaskPacket, *, task: Mapping[str, Any], assignment: Mapping[str, Any],
                 budget: Mapping[str, Any], grant: Mapping[str, Any],
                 expected_parent: Any | None = None,
                 expected_parent_digest: str | None = None,
                 expected_lineage: Sequence[Any] | None = None,
    **kwargs: Any) -> TaskPacket:
    _require_issued_packet(parent)
    if expected_parent is None:
        raise KernelError("spawn_child requires an explicit expected_parent anchor")
    _packet_body_digest(parent)
    expected_reference = _anchor_reference(expected_parent,
                                           expected_digest=expected_parent_digest)
    if expected_reference != _parent_reference(parent):
        raise KernelError("parent authority anchor mismatch")
    if parent["depth"] == 0:
        if expected_lineage is not None:
            # A caller may provide the full one-element lineage (the root
            # itself); it contributes no ancestor beyond the immediate parent.
            if _lineage_digests(expected_lineage, parent.packet_digest):
                raise KernelError("root parent has no ancestor lineage")
    else:
        if expected_lineage is None:
            raise KernelError("grandchild admission requires trusted ancestor lineage")
        ancestors = list(expected_lineage)
        first_digest = (ancestors[0].packet_digest if ancestors
                        and isinstance(ancestors[0], TaskPacket) else
                        ancestors[0].get("packet_digest") if ancestors
                        and isinstance(ancestors[0], Mapping) else None)
        if first_digest == parent.packet_digest:
            ancestors = ancestors[1:]
        if not ancestors:
            raise KernelError("grandchild admission requires trusted ancestor lineage")
        _validate_packet(parent, expected_parent=ancestors[0],
                         expected_lineage=ancestors[1:] or None)
    if parent["depth"] >= MAX_DEPTH:
        raise KernelError("maximum depth blocks child admission")
    if kwargs.get("pause") or kwargs.get("pause_epoch", parent["pause_epoch"]) > parent["pause_epoch"]:
        raise KernelError("PAUSE blocks child admission")
    limits = kwargs.pop("limits", None)
    if limits is None:
        limits = KernelLimits.from_value(parent["limits"])
    elif limits != KernelLimits.from_value(parent["limits"]):
        raise KernelError("child kernel limits changed")
    child = _build_packet_impl(task=task, assignment=assignment, budget=budget, grant=grant,
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
    _validate_semantics(body, limits, parent=parent,
                        expected_parent=expected_parent,
                        expected_parent_digest=expected_parent_digest,
                        expected_lineage=expected_lineage)
    body["packet_digest"] = hashlib.sha256(_canonical(body, limits)).hexdigest()
    return TaskPacket(body, body["packet_digest"])


def _retain_context_impl(packet: TaskPacket, items: Sequence[Mapping[str, Any]], *,
                   limits: KernelLimits | None = None, pause: bool | None = None,
                   pause_epoch: int | None = None,
                   expected_parent: Any | None = None,
                   expected_parent_digest: str | None = None,
                   expected_lineage: Sequence[Any] | None = None) -> TaskPacket:
    validate_packet(packet, pause_observed=pause is True, pause_epoch=pause_epoch,
                    expected_parent=expected_parent,
                    expected_parent_digest=expected_parent_digest,
                    expected_lineage=expected_lineage)
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
        # Token accounting is scoped strictly to the canonical selected context
        # list.  The packet-wide byte bound is checked separately below.
        context_tokens = math.ceil(len(_canonical(trial)) / 4)
        prospective = packet.to_dict()
        prospective["context"] = trial
        prospective.pop("packet_digest", None)
        encoded = _canonical(prospective)
        if (len(encoded) > lim.max_bytes or context_tokens > lim.max_tokens
                or len(trial) > lim.max_items):
            if item["mandatory"]:
                raise KernelError("mandatory context overflows limits")
            continue
        chosen = trial
    body = packet.to_dict()
    body["context"] = chosen
    body.pop("packet_digest", None)
    _validate_semantics(body, lim,
                        expected_parent=expected_parent,
                        expected_parent_digest=expected_parent_digest,
                        expected_lineage=expected_lineage)
    body["packet_digest"] = hashlib.sha256(_canonical(body, lim)).hexdigest()
    return TaskPacket(body, body["packet_digest"])


def validate_packet(packet: TaskPacket | Mapping[str, Any], *,
                    pause_observed: bool | None = None,
                    pause_epoch: int | None = None,
                    checkpoint: Mapping[str, Any] | None = None,
                    expected_parent: Any | None = None,
                    expected_parent_digest: str | None = None,
                    expected_lineage: Sequence[Any] | None = None) -> TaskPacket:
    return _validate_packet(packet, pause_observed=pause_observed,
                            pause_epoch=pause_epoch, checkpoint=checkpoint,
                            expected_parent=expected_parent,
                            expected_parent_digest=expected_parent_digest,
                            expected_lineage=expected_lineage)


def _validate_packet(packet: TaskPacket | Mapping[str, Any], *,
                     pause_observed: bool | None = None,
                     pause_epoch: int | None = None,
                     checkpoint: Mapping[str, Any] | None = None,
                     expected_parent: Any | None = None,
                     expected_parent_digest: str | None = None,
                     expected_lineage: Sequence[Any] | None = None,
                     _require_issued: bool = True) -> TaskPacket:
    if _require_issued:
        _require_issued_packet(packet)
    try:
        body = packet.to_dict()
        supplied = body.pop("packet_digest", None)
        if supplied != packet.packet_digest or supplied != hashlib.sha256(_canonical(body)).hexdigest():
            raise KernelError("packet digest mismatch")
    except (KernelError, RecursionError, TypeError, ValueError) as exc:
        if isinstance(exc, KernelError):
            raise
        raise KernelError("packet is recursive or not canonical") from exc
    if pause_observed is True:
        raise KernelError("PAUSE blocks packet admission")
    if pause_epoch is not None and (type(pause_epoch) is not int or pause_epoch < 0 or pause_epoch > body.get("pause_epoch", -1)):
        raise KernelError("late PAUSE blocks packet admission")
    lim = KernelLimits.from_value(body.get("limits"))
    _validate_semantics(
        body, lim,
        expected_parent=expected_parent,
        expected_parent_digest=expected_parent_digest,
        expected_lineage=expected_lineage,
    )
    if checkpoint is not None and body.get("checkpoint") != _plain(checkpoint):
        raise KernelError("checkpoint lineage mismatch")
    return packet


def _bind_packet_factories():
    """Install factory wrappers over an immutable callable graph.

    Python module globals are mutable, including private names.  Capturing only
    the three top-level implementations is therefore insufficient: a factory
    can reach a replaced ``_make_body`` or validator through its function
    globals.  The binding below gives every module-defined function a private
    globals dictionary whose function entries point at the corresponding
    snapshots.  The public wrappers then structurally validate and fingerprint
    the exact result before the private weak issuance ledger enrolls it.
    """
    module_globals = globals()
    trusted_globals = dict(module_globals)
    functions = {
        name: value for name, value in module_globals.items()
        if isinstance(value, FunctionType) and value.__globals__ is module_globals
    }
    trusted = {}
    for name, function in functions.items():
        clone = FunctionType(function.__code__, trusted_globals, function.__name__,
                             function.__defaults__, function.__closure__)
        clone.__kwdefaults__ = (dict(function.__kwdefaults__)
                                if function.__kwdefaults__ is not None else None)
        clone.__annotations__ = dict(getattr(function, "__annotations__", {}))
        trusted[name] = clone
    trusted_globals.update(trusted)

    issue = trusted["_packet_issue"]
    require_issued = trusted["_require_issued_packet"]
    validate = trusted["_validate_packet"]
    # Keep the validator's exact code object in the sealed factory graph.  A
    # caller can reach the private globals dictionary through ``build_impl``
    # and can replace both the global validator and the ``enroll`` closure
    # cell.  Function names/modules are forgeable metadata; this identity is
    # the independent anchor consumers use to detect that paired mutation.
    validator_code = validate.__code__

    def enroll(result: Any, *, expected_parent: Any | None = None,
               expected_parent_digest: str | None = None,
               expected_lineage: Sequence[Any] | None = None) -> TaskPacket:
        if validate.__code__ is not validator_code:
            raise KernelError("kernel validator graph is not trusted")
        # Validate the factory result before enrollment.  This is deliberately
        # independent of the issuance ledger; the second check below proves
        # that the exact object enrolled and the object validated are identical.
        validate(result, expected_parent=expected_parent,
                 expected_parent_digest=expected_parent_digest,
                 expected_lineage=expected_lineage, _require_issued=False)
        enrolled = issue(result)
        require_issued(enrolled)
        return enrolled

    build_impl = trusted["_build_packet_impl"]
    spawn_impl = trusted["_spawn_child_impl"]
    retain_impl = trusted["_retain_context_impl"]

    def build_packet(*args: Any, **kwargs: Any) -> TaskPacket:
        return enroll(build_impl(*args, **kwargs),
                      expected_parent=kwargs.get("expected_parent"),
                      expected_parent_digest=kwargs.get("expected_parent_digest"),
                      expected_lineage=kwargs.get("expected_lineage"))

    def spawn_child(*args: Any, **kwargs: Any) -> TaskPacket:
        parent = args[0] if args else kwargs.get("parent")
        return enroll(spawn_impl(*args, **kwargs),
                      expected_parent=kwargs.get("expected_parent", parent),
                      expected_parent_digest=kwargs.get("expected_parent_digest"),
                      expected_lineage=kwargs.get("expected_lineage"))

    def retain_context(*args: Any, **kwargs: Any) -> TaskPacket:
        packet = args[0] if args else kwargs.get("packet")
        return enroll(retain_impl(*args, **kwargs),
                      expected_parent=kwargs.get("expected_parent"),
                      expected_parent_digest=kwargs.get("expected_parent_digest"),
                      expected_lineage=kwargs.get("expected_lineage"))

    def validate_packet_public(packet: TaskPacket | Mapping[str, Any], *,
                               pause_observed: bool | None = None,
                               pause_epoch: int | None = None,
                               checkpoint: Mapping[str, Any] | None = None,
                               expected_parent: Any | None = None,
                               expected_parent_digest: str | None = None,
                               expected_lineage: Sequence[Any] | None = None) -> TaskPacket:
        if validate.__code__ is not validator_code:
            raise KernelError("kernel validator graph is not trusted")
        return validate(packet, pause_observed=pause_observed, pause_epoch=pause_epoch,
                        checkpoint=checkpoint, expected_parent=expected_parent,
                        expected_parent_digest=expected_parent_digest,
                        expected_lineage=expected_lineage)

    return build_packet, spawn_child, retain_context, validate_packet_public


build_packet, spawn_child, retain_context, validate_packet = _bind_packet_factories()
del _bind_packet_factories, _packet_issue


__all__ = ["KernelError", "KernelLimits", "TaskPacket", "build_packet", "spawn_child",
           "retain_context", "validate_packet"]
