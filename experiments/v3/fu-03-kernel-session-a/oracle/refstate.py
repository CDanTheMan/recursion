#!/usr/bin/env python3
"""Independent reference oracle for the FU-03 kernel (CAND RCV1 20261001).

Authored from ``docs/v3/research-lane/followups-20261002/raw/ds-FU-03-formal-model-vectors.md``
sections 3, 4, 5, 8 and 9.  This module does **not** import, call or consult any TLA model,
live reducer, provider or network resource.  It is pure Python 3.12 stdlib, deterministic and
provider-free.

Provided surface
----------------
``RefState(log)``   fold a canonical committed event log into canonical state (section 4).
``RefValid(log)``   structural validation: schema, aggregate, writer epoch, ordinal,
                    predecessor chain, digest binding, command binding and semantic
                    preconditions (sections 4, 5).
``RefProject(log)`` the fixed 16-field projection tuple (section 5).

Supporting records and helpers are defined explicitly so a reviewer can compare them with the
prose equations.  Digests are concrete domain-separated SHA-256 over deterministic CBOR
(section 8); the abstraction's symbolic injective ``DigestOf`` is intentionally stronger and is
*not* reproduced here.

Evidence class: reference implementation / inference.  A pass proves only what the bounded
vectors and trace checker exercise.  See README.md for the explicit non-proofs.
"""
from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass, field, replace
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants (ds-FU-03 section 3)
# ---------------------------------------------------------------------------
SCHEMA_EPOCH = 1
AGGREGATE = 1
TASK = 1
GENESIS_PREV = bytes(32)
MAX_COMMITTED_EVENTS = 20
OUTBOX_CAPACITY = 2
QUEUE_CAPACITY = 2

WORKERS = (1, 2)
GOAL_EPOCHS = (1, 2)
PLAN_REVISIONS = (1, 2)
LEASE_EPOCHS = (1, 2, 3)
WRITER_EPOCHS = (1, 2)
PAUSE_EPOCHS = (0, 1)
ATTEMPTS = (1, 2)

PRINCIPAL_H = 0
PRINCIPAL_W1 = 1
PRINCIPAL_W2 = 2
PRINCIPAL_X = 3
VERIFIER_PRINCIPAL = PRINCIPAL_W2

# Result value codes (section 8): 0 null, 1 R1=b"\x01", 2 R2=b"\x02".
RESULT_VALUE_CODES = {0: None, 1: b"\x01", 2: b"\x02"}

# Command / event kinds (section 3, section 8).
KIND_GRANT_LEASE = 0
KIND_REVOKE_LEASE = 1
KIND_AMEND_PLAN = 2
KIND_ADVANCE_GOAL = 3
KIND_ADVANCE_WRITER = 4
KIND_PAUSE = 5
KIND_RESUME = 6
KIND_START = 7
KIND_SUBMIT = 8
KIND_VERIFY = 9
KIND_ARM_TIMER = 10
KIND_FIRE_TIMER = 11
KIND_RETRY = 12
KIND_CANCEL = 13
KIND_PREPARE_EFFECT = 14
KIND_MARK_DISPATCH = 15
KIND_OBSERVE_EFFECT = 16
KIND_RECONCILE_EFFECT = 17
EVENT_EFFECT_PREPARED = 18
EVENT_OUTBOX_ENQUEUED = 19

COMMAND_KINDS = tuple(range(18))

# Task status codes.
ST_READY = 0
ST_RUNNING = 1
ST_SUBMITTED = 2
ST_FAILED = 3
ST_DONE = 4
ST_CANCELLED = 5
ST_RESERVED_INVALID = 6

# Effect status codes.
ES_NONE = 0
ES_PREPARED = 1
ES_INFLIGHT = 2
ES_UNKNOWN = 3
ES_SUCCEEDED = 4
ES_KNOWN_NO_EFFECT = 5

# Timer status codes.
TS_DISARMED = 0
TS_ARMED = 1
TS_FIRED = 2

# Effect outcome codes.
OUTCOME_SUCCESS = 0
OUTCOME_KNOWN_NO_EFFECT = 1
OUTCOME_UNKNOWN = 2

# State map keys (section 8).
SK_SCHEMA = 0
SK_AGGREGATE = 1
SK_ORDINAL = 2
SK_TAIL = 3
SK_GOAL = 4
SK_PLAN = 5
SK_LEASE = 6
SK_WRITER = 7
SK_PAUSE_EPOCH = 8
SK_PAUSED = 9
SK_STATUS = 10
SK_OWNER = 11
SK_ATTEMPT = 12
SK_EFFECT = 13
SK_TIMER = 14
SK_RESULT = 15
SK_CANCELLED = 16
SK_RECEIPTS = 17
SK_OUTBOX = 18
SK_RETRY_READY = 19

# Refusal codes (section 9).
MALFORMED = 0
NONCANONICAL = 1
UNSUPPORTED_SCHEMA = 2
UNKNOWN_KIND = 3
FIELD_INVALID = 4
COMMAND_CONFLICT = 5
EXPECTED_STATE_MISMATCH = 6
AUTHORITY_DENIED = 7
GOAL_EPOCH_STALE = 8
PLAN_REVISION_STALE = 9
LEASE_EPOCH_STALE = 10
PAUSED = 11
PAUSE_EPOCH_STALE = 12
ATTEMPT_INVALID = 13
CANCELLED = 14
EFFECT_UNSAFE = 15
VERIFIER_INVALID = 16
CHAIN_MISMATCH = 17

REFUSAL_NAMES = {
    MALFORMED: "MALFORMED",
    NONCANONICAL: "NONCANONICAL",
    UNSUPPORTED_SCHEMA: "UNSUPPORTED_SCHEMA",
    UNKNOWN_KIND: "UNKNOWN_KIND",
    FIELD_INVALID: "FIELD_INVALID",
    COMMAND_CONFLICT: "COMMAND_CONFLICT",
    EXPECTED_STATE_MISMATCH: "EXPECTED_STATE_MISMATCH",
    AUTHORITY_DENIED: "AUTHORITY_DENIED",
    GOAL_EPOCH_STALE: "GOAL_EPOCH_STALE",
    PLAN_REVISION_STALE: "PLAN_REVISION_STALE",
    LEASE_EPOCH_STALE: "LEASE_EPOCH_STALE",
    PAUSED: "PAUSED",
    PAUSE_EPOCH_STALE: "PAUSE_EPOCH_STALE",
    ATTEMPT_INVALID: "ATTEMPT_INVALID",
    CANCELLED: "CANCELLED",
    EFFECT_UNSAFE: "EFFECT_UNSAFE",
    VERIFIER_INVALID: "VERIFIER_INVALID",
    CHAIN_MISMATCH: "CHAIN_MISMATCH",
}

# Stable detail enums (section 9).
DET_NONE = 0
DET_TRUNCATED = 1
DET_DUPLICATE_KEY = 2
DET_NONSHORTEST = 3
DET_MAP_ORDER = 4
DET_BAD_UTF8 = 5
DET_FORBIDDEN_TYPE = 6
DET_MISSING_FIELD = 7
DET_UNKNOWN_FIELD = 8
DET_RANGE = 9
DET_SCHEMA = 10
DET_KIND = 11
DET_COMMAND_DIGEST = 12
DET_EXPECTED_ORDINAL = 13
DET_EXPECTED_DIGEST = 14
DET_AGGREGATE = 15
DET_TASK = 16
DET_PRINCIPAL = 17
DET_CAPABILITY = 18
DET_GOAL = 19
DET_PLAN = 20
DET_LEASE = 21
DET_OWNER = 22
DET_WRITER_EPOCH = 23
DET_PAUSED = 24
DET_PAUSE_EPOCH = 25
DET_ATTEMPT = 26
DET_BAD_TRANSITION = 27
DET_TIMER = 28
DET_CAPACITY = 29
DET_CANCELLED = 30
DET_EFFECT_STATE = 31
DET_EFFECT_TOKEN = 32
DET_EFFECT_OUTCOME = 33
DET_SELF_VERIFY = 34
DET_RESULT_BINDING = 35
DET_CHAIN_ORDINAL = 36
DET_CHAIN_PREVIOUS = 37
DET_CHAIN_DIGEST = 38
DET_TRAILING_BYTES = 39
DET_DEPTH_LIMIT = 40
DET_ITEM_LIMIT = 41

DETAIL_NAMES = {v: k for k, v in {
    "NONE": DET_NONE, "TRUNCATED": DET_TRUNCATED, "DUPLICATE_KEY": DET_DUPLICATE_KEY,
    "NONSHORTEST": DET_NONSHORTEST, "MAP_ORDER": DET_MAP_ORDER, "BAD_UTF-8": DET_BAD_UTF8,
    "FORBIDDEN_TYPE": DET_FORBIDDEN_TYPE, "MISSING_FIELD": DET_MISSING_FIELD,
    "UNKNOWN_FIELD": DET_UNKNOWN_FIELD, "RANGE": DET_RANGE, "SCHEMA": DET_SCHEMA,
    "KIND": DET_KIND, "COMMAND_DIGEST": DET_COMMAND_DIGEST,
    "EXPECTED_ORDINAL": DET_EXPECTED_ORDINAL, "EXPECTED_DIGEST": DET_EXPECTED_DIGEST,
    "AGGREGATE": DET_AGGREGATE, "TASK": DET_TASK, "PRINCIPAL": DET_PRINCIPAL,
    "CAPABILITY": DET_CAPABILITY, "GOAL": DET_GOAL, "PLAN": DET_PLAN, "LEASE": DET_LEASE,
    "OWNER": DET_OWNER, "WRITER_EPOCH": DET_WRITER_EPOCH, "PAUSED": DET_PAUSED,
    "PAUSE_EPOCH": DET_PAUSE_EPOCH, "ATTEMPT": DET_ATTEMPT,
    "BAD_TRANSITION": DET_BAD_TRANSITION, "TIMER": DET_TIMER, "CAPACITY": DET_CAPACITY,
    "CANCELLED": DET_CANCELLED, "EFFECT_STATE": DET_EFFECT_STATE,
    "EFFECT_TOKEN": DET_EFFECT_TOKEN, "EFFECT_OUTCOME": DET_EFFECT_OUTCOME,
    "SELF_VERIFY": DET_SELF_VERIFY, "RESULT_BINDING": DET_RESULT_BINDING,
    "CHAIN_ORDINAL": DET_CHAIN_ORDINAL, "CHAIN_PREVIOUS": DET_CHAIN_PREVIOUS,
    "CHAIN_DIGEST": DET_CHAIN_DIGEST, "TRAILING_BYTES": DET_TRAILING_BYTES,
    "DEPTH_LIMIT": DET_DEPTH_LIMIT, "ITEM_LIMIT": DET_ITEM_LIMIT,
}.items()}

DOMAINS = ("state", "event", "packet", "command", "projection", "effecttoken", "manifest")

_H_KINDS = frozenset({
    KIND_GRANT_LEASE, KIND_REVOKE_LEASE, KIND_AMEND_PLAN, KIND_ADVANCE_GOAL,
    KIND_ADVANCE_WRITER, KIND_PAUSE, KIND_RESUME, KIND_ARM_TIMER, KIND_FIRE_TIMER,
    KIND_CANCEL, KIND_RECONCILE_EFFECT, KIND_OBSERVE_EFFECT,
})
_WORKER_KINDS = frozenset({
    KIND_START, KIND_SUBMIT, KIND_RETRY, KIND_PREPARE_EFFECT, KIND_MARK_DISPATCH,
})
_PAUSE_FORBIDDEN = frozenset({
    KIND_START, KIND_SUBMIT, KIND_RETRY, KIND_PREPARE_EFFECT, KIND_MARK_DISPATCH,
    KIND_ARM_TIMER, KIND_FIRE_TIMER,
})
_CANCEL_FORBIDDEN = frozenset({
    KIND_START, KIND_SUBMIT, KIND_VERIFY, KIND_RETRY, KIND_PREPARE_EFFECT,
    KIND_MARK_DISPATCH, KIND_ARM_TIMER, KIND_FIRE_TIMER,
})


# ---------------------------------------------------------------------------
# Refusal value (tagged result, section 3/9)
# ---------------------------------------------------------------------------
class Refusal(Exception):
    """A structured refusal ``(code, detail, path, expected, observed)``."""

    def __init__(
        self,
        code: int,
        detail: int = DET_NONE,
        path: Optional[list] = None,
        expected: Any = None,
        observed: Any = None,
        message: str = "",
        index: Optional[int] = None,
    ) -> None:
        self.code = code
        self.detail = detail
        self.path = list(path) if path is not None else []
        self.expected = expected
        self.observed = observed
        self.index = index
        self.message = message
        super().__init__(f"{REFUSAL_NAMES.get(code, code)}/{detail} {message}".strip())

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "detail": self.detail,
            "path": self.path,
            "expected": _jsonable(self.expected),
            "observed": _jsonable(self.observed),
        }


def _jsonable(value: Any) -> Any:
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    return value


# ---------------------------------------------------------------------------
# Deterministic CBOR (section 7/8) and domain-separated digest (section 8)
# ---------------------------------------------------------------------------
def _cbor_head(major: int, n: int) -> bytes:
    if n < 0:
        raise ValueError("CBOR head argument must be non-negative")
    if n < 24:
        return bytes([(major << 5) | n])
    if n < 0x100:
        return bytes([(major << 5) | 24, n])
    if n < 0x10000:
        return bytes([(major << 5) | 25]) + struct.pack(">H", n)
    if n < 0x100000000:
        return bytes([(major << 5) | 26]) + struct.pack(">I", n)
    if n < 0x10000000000000000:
        return bytes([(major << 5) | 27]) + struct.pack(">Q", n)
    raise ValueError("integer does not fit the CBOR unsigned-integer profile")


def cbor_encode(value: Any) -> bytes:
    """Canonical deterministic CBOR for the permitted profile (section 7)."""
    if value is None:
        return b"\xf6"
    if value is True:
        return b"\xf5"
    if value is False:
        return b"\xf4"
    if isinstance(value, int):
        if value >= 0:
            return _cbor_head(0, value)
        return _cbor_head(1, -1 - value)
    if isinstance(value, (bytes, bytearray)):
        raw = bytes(value)
        return _cbor_head(2, len(raw)) + raw
    if isinstance(value, str):
        raw = value.encode("utf-8")
        return _cbor_head(3, len(raw)) + raw
    if isinstance(value, (list, tuple)):
        parts = [_cbor_head(4, len(value))]
        parts.extend(cbor_encode(item) for item in value)
        return b"".join(parts)
    if isinstance(value, dict):
        items = []
        for key in value:
            if not isinstance(key, int) or isinstance(key, bool) or key < 0:
                raise ValueError("map keys must be unsigned integers under this profile")
            items.append(key)
        ordered = sorted(items)
        parts = [_cbor_head(5, len(ordered))]
        for key in ordered:
            parts.append(cbor_encode(key))
            parts.append(cbor_encode(value[key]))
        return b"".join(parts)
    raise ValueError(f"unsupported typed value: {type(value)!r}")


def _decode_head(data: bytes, offset: int):
    if offset >= len(data):
        raise Refusal(MALFORMED, DET_TRUNCATED, [])
    ib = data[offset]
    offset += 1
    major = ib >> 5
    ai = ib & 0x1F
    if ai < 24:
        return major, ai, offset
    if ai == 24:
        if offset + 1 > len(data):
            raise Refusal(MALFORMED, DET_TRUNCATED, [])
        n = data[offset]
        offset += 1
        if n < 24:
            raise Refusal(NONCANONICAL, DET_NONSHORTEST, [])
        return major, n, offset
    if ai == 25:
        if offset + 2 > len(data):
            raise Refusal(MALFORMED, DET_TRUNCATED, [])
        n = struct.unpack_from(">H", data, offset)[0]
        offset += 2
        if n < 0x100:
            raise Refusal(NONCANONICAL, DET_NONSHORTEST, [])
        return major, n, offset
    if ai == 26:
        if offset + 4 > len(data):
            raise Refusal(MALFORMED, DET_TRUNCATED, [])
        n = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        if n < 0x10000:
            raise Refusal(NONCANONICAL, DET_NONSHORTEST, [])
        return major, n, offset
    if ai == 27:
        if offset + 8 > len(data):
            raise Refusal(MALFORMED, DET_TRUNCATED, [])
        n = struct.unpack_from(">Q", data, offset)[0]
        offset += 8
        if n < 0x100000000:
            raise Refusal(NONCANONICAL, DET_NONSHORTEST, [])
        return major, n, offset
    raise Refusal(FIELD_INVALID, DET_FORBIDDEN_TYPE, [])


def _decode_item(data: bytes, offset: int, depth: int):
    if depth > 64:
        raise Refusal(FIELD_INVALID, DET_DEPTH_LIMIT, [])
    major, n, offset = _decode_head(data, offset)
    if major == 0:
        return n, offset
    if major == 1:
        return -1 - n, offset
    if major == 2:
        if offset + n > len(data):
            raise Refusal(MALFORMED, DET_TRUNCATED, [])
        return data[offset:offset + n], offset + n
    if major == 3:
        if offset + n > len(data):
            raise Refusal(MALFORMED, DET_TRUNCATED, [])
        raw = data[offset:offset + n]
        try:
            return raw.decode("utf-8"), offset + n
        except UnicodeDecodeError:
            raise Refusal(MALFORMED, DET_BAD_UTF8, []) from None
    if major == 4:
        items = []
        for _ in range(n):
            item, offset = _decode_item(data, offset, depth + 1)
            items.append(item)
        return items, offset
    if major == 5:
        result: dict = {}
        last = -1
        for _ in range(n):
            if offset >= len(data):
                raise Refusal(MALFORMED, DET_TRUNCATED, [])
            key_major = data[offset] >> 5
            if key_major != 0:
                raise Refusal(FIELD_INVALID, DET_FORBIDDEN_TYPE, [])
            key, offset = _decode_item(data, offset, depth + 1)
            if key in result:
                raise Refusal(NONCANONICAL, DET_DUPLICATE_KEY, [key])
            if key <= last:
                raise Refusal(NONCANONICAL, DET_MAP_ORDER, [])
            last = key
            value, offset = _decode_item(data, offset, depth + 1)
            result[key] = value
        return result, offset
    if major == 7:
        if n == 20:
            return False, offset
        if n == 21:
            return True, offset
        if n == 22:
            return None, offset
        raise Refusal(FIELD_INVALID, DET_FORBIDDEN_TYPE, [])
    raise Refusal(FIELD_INVALID, DET_FORBIDDEN_TYPE, [])


def cbor_decode(data: bytes) -> Any:
    """Strict decoder for the canonical profile; raises ``Refusal`` on noncanonical input."""
    value, offset = _decode_item(bytes(data), 0, 0)
    if offset != len(data):
        raise Refusal(MALFORMED, DET_TRAILING_BYTES, [])
    return value


def D(domain: str, epoch: int, value: Any) -> bytes:
    """Domain-separated SHA-256 preimage from ds-FU-03 section 8."""
    if domain not in DOMAINS:
        raise ValueError(f"unknown digest domain {domain!r}")
    payload = cbor_encode(value)
    preimage = (
        b"RCV1/"
        + domain.encode("ascii")
        + b"\x00"
        + struct.pack(">H", epoch)
        + struct.pack(">Q", len(payload))
        + payload
    )
    return hashlib.sha256(preimage).digest()


def _int_keys(mapping: dict) -> dict:
    return {int(k): v for k, v in mapping.items()}


# ---------------------------------------------------------------------------
# Records (section 8)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Command:
    schema_epoch: int
    id: int
    kind: int
    aggregate: int
    task: int
    principal: Optional[int]
    capability: int
    goal: int
    plan: int
    lease: int
    writer: int
    pause_epoch: int
    attempt: int
    expected_ordinal: int
    expected_state_digest: bytes
    payload: dict = field(default_factory=dict)

    def to_map(self) -> dict:
        return {
            0: self.schema_epoch,
            1: self.id,
            2: self.kind,
            3: self.aggregate,
            4: self.task,
            5: self.principal,
            6: self.capability,
            7: self.goal,
            8: self.plan,
            9: self.lease,
            10: self.writer,
            11: self.pause_epoch,
            12: self.attempt,
            13: self.expected_ordinal,
            14: self.expected_state_digest,
            15: self.payload,
        }

    @classmethod
    def from_map(cls, raw: dict) -> "Command":
        m = _int_keys(raw)
        return cls(
            schema_epoch=m[0], id=m[1], kind=m[2], aggregate=m[3], task=m[4],
            principal=m[5], capability=m[6], goal=m[7], plan=m[8], lease=m[9],
            writer=m[10], pause_epoch=m[11], attempt=m[12], expected_ordinal=m[13],
            expected_state_digest=bytes(m[14]), payload=_int_keys(m[15]),
        )


def command_digest(cmd: Command) -> bytes:
    return D("command", SCHEMA_EPOCH, cmd.to_map())


@dataclass(frozen=True)
class StoredEvent:
    schema_epoch: int
    aggregate: int
    ordinal: int
    previous: bytes
    command_digest: bytes
    kind: int
    payload: dict  # {0: command map, 1: event-specific data}
    writer: int
    digest: bytes

    def body_map(self) -> dict:
        return {
            0: self.schema_epoch,
            1: self.aggregate,
            2: self.ordinal,
            3: self.previous,
            4: self.command_digest,
            5: self.kind,
            6: self.payload,
            7: self.writer,
        }

    def to_map(self) -> dict:
        body = self.body_map()
        body[8] = self.digest
        return body

    @classmethod
    def from_map(cls, raw: dict) -> "StoredEvent":
        m = _int_keys(raw)
        payload = _int_keys(m[6])
        payload[0] = _int_keys(payload[0])
        return cls(
            schema_epoch=m[0], aggregate=m[1], ordinal=m[2], previous=bytes(m[3]),
            command_digest=bytes(m[4]), kind=m[5], payload=payload, writer=m[7],
            digest=bytes(m[8]),
        )


def event_digest(event: StoredEvent) -> bytes:
    return D("event", SCHEMA_EPOCH, event.body_map())


@dataclass(frozen=True)
class EffectRecord:
    status: int
    effect_id: Optional[int] = None
    attempt: Optional[int] = None
    goal: Optional[int] = None
    plan: Optional[int] = None
    lease: Optional[int] = None
    pause_epoch: Optional[int] = None
    issuing_command_id: Optional[int] = None
    token: Optional[bytes] = None
    writer: Optional[int] = None

    def to_map(self) -> dict:
        if self.status == ES_NONE:
            return {0: ES_NONE, 1: None, 2: None, 3: None, 4: None, 5: None,
                    6: None, 7: None, 8: None, 9: None}
        return {
            0: self.status, 1: self.effect_id, 2: self.attempt, 3: self.goal,
            4: self.plan, 5: self.lease, 6: self.pause_epoch,
            7: self.issuing_command_id, 8: self.token, 9: self.writer,
        }


@dataclass(frozen=True)
class TimerRecord:
    status: int
    attempt: Optional[int] = None
    goal: Optional[int] = None
    plan: Optional[int] = None
    pause_epoch: Optional[int] = None

    def to_map(self) -> dict:
        if self.status == TS_DISARMED:
            return {0: TS_DISARMED, 1: None, 2: None, 3: None, 4: None}
        return {
            0: self.status, 1: self.attempt, 2: self.goal, 3: self.plan,
            4: self.pause_epoch,
        }


@dataclass(frozen=True)
class ResultRecord:
    value: Optional[bytes] = None
    producer: Optional[int] = None
    verified: Optional[bytes] = None
    attempt: Optional[int] = None
    goal: Optional[int] = None
    plan: Optional[int] = None
    producer_lease: Optional[int] = None

    def to_map(self) -> dict:
        return {
            0: self.value, 1: self.producer, 2: self.verified, 3: self.attempt,
            4: self.goal, 5: self.plan, 6: self.producer_lease,
        }


@dataclass(frozen=True)
class Receipt:
    id: int
    command_digest: bytes
    first_ordinal: int
    last_ordinal: int
    last_event_digest: bytes
    result_class: int
    result_bytes: bytes

    def to_map(self) -> dict:
        return {
            0: self.id, 1: self.command_digest, 2: self.first_ordinal,
            3: self.last_ordinal, 4: self.last_event_digest, 5: self.result_class,
            6: self.result_bytes,
        }


def _receipt_result_bytes(command_id: int, first: int, last: int, last_digest: bytes) -> bytes:
    return cbor_encode({0: command_id, 1: first, 2: last, 3: last_digest})


@dataclass(frozen=True)
class OutboxEntry:
    token: bytes
    aggregate: int
    task: int
    goal: int
    plan: int
    lease: int
    writer: int
    pause_epoch: int
    attempt: int
    effect_id: int
    command_id: int
    owner: Optional[int]

    def to_map(self) -> dict:
        return {
            0: self.token, 1: self.aggregate, 2: self.task, 3: self.goal,
            4: self.plan, 5: self.lease, 6: self.writer, 7: self.pause_epoch,
            8: self.attempt, 9: self.effect_id, 10: self.command_id, 11: self.owner,
        }

    @classmethod
    def from_map(cls, raw: dict) -> "OutboxEntry":
        m = _int_keys(raw)
        return cls(
            token=bytes(m[0]), aggregate=m[1], task=m[2], goal=m[3], plan=m[4],
            lease=m[5], writer=m[6], pause_epoch=m[7], attempt=m[8],
            effect_id=m[9], command_id=m[10], owner=m[11],
        )


# ---------------------------------------------------------------------------
# Canonical state (section 3 / section 8)
# ---------------------------------------------------------------------------
@dataclass
class KernelState:
    schema_epoch: int = SCHEMA_EPOCH
    aggregate: int = AGGREGATE
    ordinal: int = 0
    tail: bytes = GENESIS_PREV
    goal: int = 1
    plan: int = 1
    lease: int = 1
    writer: int = 1
    pause_epoch: int = 0
    paused: bool = False
    status: int = ST_READY
    owner: Optional[int] = PRINCIPAL_W1
    attempt: int = 0
    effect: Optional[EffectRecord] = None
    timer: Optional[TimerRecord] = None
    result: Optional[ResultRecord] = None
    cancelled: bool = False
    receipts: list[Receipt] = field(default_factory=list)
    outbox: list[OutboxEntry] = field(default_factory=list)
    retry_ready: bool = False

    def copy(self) -> "KernelState":
        return replace(self, receipts=list(self.receipts), outbox=list(self.outbox))

    def to_map(self) -> dict:
        return {
            0: self.schema_epoch,
            1: self.aggregate,
            2: self.ordinal,
            3: self.tail,
            4: self.goal,
            5: self.plan,
            6: self.lease,
            7: self.writer,
            8: self.pause_epoch,
            9: self.paused,
            10: self.status,
            11: self.owner,
            12: self.attempt,
            13: self.effect.to_map() if self.effect is not None else None,
            14: self.timer.to_map() if self.timer is not None else None,
            15: self.result.to_map() if self.result is not None else None,
            16: self.cancelled,
            17: [r.to_map() for r in self.receipts],
            18: [o.to_map() for o in self.outbox],
            19: self.retry_ready,
        }

    def receipt_by_id(self, command_id: int) -> Optional[Receipt]:
        for receipt in self.receipts:
            if receipt.id == command_id:
                return receipt
        return None


def genesis_state() -> KernelState:
    return KernelState()


def state_digest(state: KernelState) -> bytes:
    return D("state", SCHEMA_EPOCH, state.to_map())


def state_digest_hex(state: KernelState) -> str:
    return state_digest(state).hex()


def projection_tuple(state: KernelState) -> tuple:
    """The fixed 16-field projection tuple from ds-FU-03 section 5."""
    return (
        state.aggregate,
        state.ordinal,
        state.tail,
        state.status,
        state.goal,
        state.plan,
        state.lease,
        state.owner,
        state.attempt,
        state.paused,
        state.pause_epoch,
        state.cancelled,
        state.result.value if state.result is not None else None,
        state.result.verified if state.result is not None else None,
        state.effect.status if state.effect is not None else ES_NONE,
        state.timer.status if state.timer is not None else TS_DISARMED,
    )


def projection_json(state: KernelState) -> list:
    return [_jsonable(v) for v in projection_tuple(state)]


def projection_digest(state: KernelState) -> bytes:
    return D("projection", SCHEMA_EPOCH, list(projection_tuple(state)))


# ---------------------------------------------------------------------------
# Admission helpers (section 4)
# ---------------------------------------------------------------------------
def default_principal(state: KernelState, kind: int) -> Optional[int]:
    if kind in _H_KINDS:
        return PRINCIPAL_H
    if kind == KIND_VERIFY:
        return VERIFIER_PRINCIPAL
    if kind in _WORKER_KINDS:
        return state.owner
    return PRINCIPAL_H


def _disarmed_timer() -> TimerRecord:
    return TimerRecord(TS_DISARMED)


def _effect_token(command: Command, effect_id: int) -> bytes:
    return D("effecttoken", SCHEMA_EPOCH, [AGGREGATE, effect_id, command.attempt, command.id])


def _effect_fence_map(command: Command, state: KernelState, effect_id: int) -> dict:
    token = _effect_token(command, effect_id)
    return {
        0: token, 1: AGGREGATE, 2: TASK, 3: state.goal, 4: state.plan, 5: state.lease,
        6: state.writer, 7: state.pause_epoch, 8: state.attempt, 9: effect_id,
        10: command.id, 11: state.owner,
    }


def _bad(detail: int, path: Optional[list] = None, expected=None, observed=None, msg: str = ""):
    raise Refusal(FIELD_INVALID, detail, path, expected, observed, msg)


def _check_semantics(state: KernelState, command: Command) -> None:
    """Step 10 of section 4: attempt, transition, effect, verifier, timer, capacity."""
    kind = command.kind
    payload = command.payload

    if kind == KIND_GRANT_LEASE:
        worker = payload.get(0)
        if worker not in WORKERS:
            _bad(DET_RANGE, [15, 0], "worker", worker)
        if state.lease >= 3:
            _bad(DET_BAD_TRANSITION, [9], LEASE_EPOCHS, state.lease, "lease bound")
    elif kind == KIND_REVOKE_LEASE:
        if state.lease >= 3:
            _bad(DET_BAD_TRANSITION, [9], LEASE_EPOCHS, state.lease, "lease bound")
    elif kind == KIND_AMEND_PLAN:
        if state.plan != 1:
            _bad(DET_BAD_TRANSITION, [8], 1, state.plan)
    elif kind == KIND_ADVANCE_GOAL:
        if state.goal != 1:
            _bad(DET_BAD_TRANSITION, [7], 1, state.goal)
    elif kind == KIND_ADVANCE_WRITER:
        if state.writer != 1:
            _bad(DET_BAD_TRANSITION, [10], 1, state.writer)
    elif kind == KIND_PAUSE:
        if state.paused or state.pause_epoch != 0:
            _bad(DET_BAD_TRANSITION, ["state", SK_PAUSED], False, state.paused)
    elif kind == KIND_RESUME:
        if not state.paused:
            _bad(DET_BAD_TRANSITION, ["state", SK_PAUSED], True, state.paused)
    elif kind == KIND_START:
        if state.owner is None:
            _bad(DET_OWNER, ["state", SK_OWNER], "worker", None)
        if state.status != ST_READY:
            _bad(DET_BAD_TRANSITION, ["state", SK_STATUS], ST_READY, state.status)
        if state.attempt != 0:
            _bad(DET_ATTEMPT, ["state", SK_ATTEMPT], 0, state.attempt)
    elif kind == KIND_SUBMIT:
        value_code = payload.get(0)
        outcome = payload.get(1)
        if value_code not in (1, 2):
            _bad(DET_RANGE, [15, 0], "result value", value_code)
        if outcome not in (0, 1):
            _bad(DET_RANGE, [15, 1], "outcome", outcome)
        if command.attempt != state.attempt:
            _bad(DET_ATTEMPT, [12], state.attempt, command.attempt)
        if state.status != ST_RUNNING:
            _bad(DET_BAD_TRANSITION, ["state", SK_STATUS], ST_RUNNING, state.status)
    elif kind == KIND_VERIFY:
        value_code = payload.get(0)
        if value_code not in (1, 2):
            _bad(DET_RANGE, [15, 0], "result value", value_code)
        expected_value = RESULT_VALUE_CODES[value_code]
        if state.status != ST_SUBMITTED or state.result is None:
            raise Refusal(VERIFIER_INVALID, DET_RESULT_BINDING, ["state", SK_STATUS])
        if command.attempt != state.attempt:
            raise Refusal(VERIFIER_INVALID, DET_RESULT_BINDING, [12])
        if state.result.attempt != state.attempt or state.result.goal != state.goal or \
                state.result.plan != state.plan:
            raise Refusal(VERIFIER_INVALID, DET_RESULT_BINDING, ["state", SK_RESULT])
        if expected_value != state.result.value:
            raise Refusal(VERIFIER_INVALID, DET_RESULT_BINDING, [15, 0],
                          _jsonable(state.result.value), _jsonable(expected_value))
        if state.result.producer == VERIFIER_PRINCIPAL:
            raise Refusal(VERIFIER_INVALID, DET_SELF_VERIFY, [5])
    elif kind == KIND_ARM_TIMER:
        if state.status != ST_FAILED:
            _bad(DET_BAD_TRANSITION, ["state", SK_STATUS], ST_FAILED, state.status)
        if state.timer is not None and state.timer.status != TS_DISARMED:
            _bad(DET_TIMER, ["state", SK_TIMER, 0], TS_DISARMED, state.timer.status)
        if state.attempt >= 2:
            _bad(DET_ATTEMPT, ["state", SK_ATTEMPT], "<2", state.attempt)
    elif kind == KIND_FIRE_TIMER:
        if state.timer is None or state.timer.status != TS_ARMED:
            _bad(DET_TIMER, ["state", SK_TIMER, 0], TS_ARMED,
                 None if state.timer is None else state.timer.status)
        timer = state.timer
        if (timer.attempt, timer.goal, timer.plan, timer.pause_epoch) != \
                (state.attempt, state.goal, state.plan, state.pause_epoch):
            _bad(DET_TIMER, ["state", SK_TIMER], "captured fields current",
                 (timer.attempt, timer.goal, timer.plan, timer.pause_epoch))
    elif kind == KIND_RETRY:
        if state.status != ST_FAILED:
            _bad(DET_BAD_TRANSITION, ["state", SK_STATUS], ST_FAILED, state.status)
        if state.attempt >= 2:
            raise Refusal(ATTEMPT_INVALID, DET_ATTEMPT, ["state", SK_ATTEMPT])
        if not state.retry_ready:
            _bad(DET_TIMER, ["state", SK_TIMER, 0], "fired matching timer", state.retry_ready)
        if state.effect is not None and state.effect.status not in (ES_NONE, ES_KNOWN_NO_EFFECT):
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_STATE, ["state", SK_EFFECT])
    elif kind == KIND_CANCEL:
        pass  # cancelled handled at step 9; otherwise always allowed for H
    elif kind == KIND_PREPARE_EFFECT:
        effect_id = payload.get(0)
        if effect_id not in (1,):
            _bad(DET_RANGE, [15, 0], "effect id", effect_id)
        if state.status != ST_RUNNING:
            _bad(DET_BAD_TRANSITION, ["state", SK_STATUS], ST_RUNNING, state.status)
        if command.attempt != state.attempt:
            _bad(DET_ATTEMPT, [12], state.attempt, command.attempt)
        if state.effect is not None and state.effect.status != ES_NONE:
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_STATE, ["state", SK_EFFECT])
        if len(state.outbox) >= OUTBOX_CAPACITY:
            _bad(DET_CAPACITY, ["state", SK_OUTBOX], OUTBOX_CAPACITY, len(state.outbox))
    elif kind == KIND_MARK_DISPATCH:
        token = payload.get(0)
        if state.effect is None or state.effect.status != ES_PREPARED:
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_STATE, ["state", SK_EFFECT])
        effect = state.effect
        if token != effect.token:
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_TOKEN, [15, 0])
        if (effect.attempt, effect.goal, effect.plan, effect.lease, effect.writer,
                effect.pause_epoch) != (state.attempt, state.goal, state.plan, state.lease,
                                        state.writer, state.pause_epoch):
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_STATE, ["state", SK_EFFECT])
        matches = [o for o in state.outbox if o.token == token]
        if len(matches) != 1:
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_TOKEN, ["state", SK_OUTBOX])
        if matches[0].owner != state.owner:
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_STATE, ["state", SK_EFFECT])
    elif kind == KIND_OBSERVE_EFFECT:
        token = payload.get(0)
        outcome = payload.get(1)
        if outcome not in (0, 1, 2):
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_OUTCOME, [15, 1])
        if state.effect is None or state.effect.status not in (ES_INFLIGHT, ES_UNKNOWN):
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_STATE, ["state", SK_EFFECT])
        if token != state.effect.token:
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_TOKEN, [15, 0])
    elif kind == KIND_RECONCILE_EFFECT:
        token = payload.get(0)
        outcome = payload.get(1)
        if outcome not in (0, 1):
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_OUTCOME, [15, 1])
        if state.effect is None or state.effect.status not in (ES_INFLIGHT, ES_UNKNOWN):
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_STATE, ["state", SK_EFFECT])
        if token != state.effect.token:
            raise Refusal(EFFECT_UNSAFE, DET_EFFECT_TOKEN, [15, 0])


def check_command(state: KernelState, command: Command, index: Optional[int] = None) -> None:
    """Ordered admission/guard checks from section 4.  Raises ``Refusal`` on first failure.

    Duplicate command identity (step 1) is handled by ``admit``/the fold because the required
    outcome differs between the two contexts.
    """
    def refuse(code, detail, path=None, expected=None, observed=None, msg=""):
        raise Refusal(code, detail, path, expected, observed, msg, index=index)

    if command.schema_epoch != SCHEMA_EPOCH:
        refuse(UNSUPPORTED_SCHEMA, DET_SCHEMA, [0], SCHEMA_EPOCH, command.schema_epoch)
    if command.kind not in COMMAND_KINDS:
        refuse(UNKNOWN_KIND, DET_KIND, [2], COMMAND_KINDS, command.kind)

    # Step 2: Expected(K, c).
    if command.expected_ordinal != state.ordinal:
        refuse(EXPECTED_STATE_MISMATCH, DET_EXPECTED_ORDINAL, [13],
               state.ordinal, command.expected_ordinal)
    current_digest = state_digest(state)
    if command.expected_state_digest != current_digest:
        refuse(EXPECTED_STATE_MISMATCH, DET_EXPECTED_DIGEST, [14],
               current_digest, command.expected_state_digest)

    # Step 3: aggregate, task, principal, capability authorization.
    if command.aggregate != AGGREGATE:
        refuse(AUTHORITY_DENIED, DET_AGGREGATE, [3], AGGREGATE, command.aggregate)
    if command.task != TASK:
        refuse(AUTHORITY_DENIED, DET_TASK, [4], TASK, command.task)
    if command.kind in _H_KINDS:
        if command.principal != PRINCIPAL_H:
            refuse(AUTHORITY_DENIED, DET_PRINCIPAL, [5], PRINCIPAL_H, command.principal)
    elif command.kind == KIND_VERIFY:
        if command.principal != VERIFIER_PRINCIPAL:
            refuse(VERIFIER_INVALID, DET_PRINCIPAL, [5], VERIFIER_PRINCIPAL, command.principal)
    if command.capability != command.kind:
        refuse(AUTHORITY_DENIED, DET_CAPABILITY, [6], command.kind, command.capability)

    # Step 4: goal epoch.
    if command.goal != state.goal:
        refuse(GOAL_EPOCH_STALE, DET_GOAL, [7], state.goal, command.goal)
    # Step 5: plan revision.
    if command.plan != state.plan:
        refuse(PLAN_REVISION_STALE, DET_PLAN, [8], state.plan, command.plan)
    # Step 6: writer epoch.
    if command.writer != state.writer:
        refuse(AUTHORITY_DENIED, DET_WRITER_EPOCH, [10], state.writer, command.writer)

    # Step 7: worker lease/owner; verifier numeric lease.
    if command.kind in _WORKER_KINDS:
        if command.lease != state.lease:
            refuse(LEASE_EPOCH_STALE, DET_LEASE, [9], state.lease, command.lease)
        if command.principal != state.owner:
            refuse(AUTHORITY_DENIED, DET_OWNER, [5], state.owner, command.principal)
    elif command.kind == KIND_VERIFY:
        if command.lease != state.lease:
            refuse(LEASE_EPOCH_STALE, DET_LEASE, [9], state.lease, command.lease)

    # Step 8: pause epoch, then paused work guard.
    if command.pause_epoch != state.pause_epoch:
        refuse(PAUSE_EPOCH_STALE, DET_PAUSE_EPOCH, [11], state.pause_epoch, command.pause_epoch)
    if state.paused and command.kind in _PAUSE_FORBIDDEN:
        refuse(PAUSED, DET_PAUSED, ["state", SK_PAUSED], False, True)

    # Step 9: cancellation.
    if state.cancelled:
        if command.kind == KIND_CANCEL:
            refuse(FIELD_INVALID, DET_BAD_TRANSITION, [2])
        if command.kind in _CANCEL_FORBIDDEN:
            refuse(CANCELLED, DET_CANCELLED, ["state", SK_CANCELLED], False, True)

    # Step 10: semantic guards and capacity.
    _check_semantics(state, command)


# ---------------------------------------------------------------------------
# Event application and batch construction
# ---------------------------------------------------------------------------
def _apply_event(state: KernelState, command: Command, event: StoredEvent) -> None:
    kind = event.kind
    payload = command.payload

    if kind == KIND_GRANT_LEASE:
        state.lease += 1
        state.owner = payload.get(0)
    elif kind == KIND_REVOKE_LEASE:
        state.lease += 1
        state.owner = None
    elif kind == KIND_AMEND_PLAN:
        state.plan = 2
        state.retry_ready = False
        state.timer = _disarmed_timer()
    elif kind == KIND_ADVANCE_GOAL:
        state.goal = 2
        state.retry_ready = False
        state.timer = _disarmed_timer()
    elif kind == KIND_ADVANCE_WRITER:
        state.writer = 2
    elif kind == KIND_PAUSE:
        state.pause_epoch = 1
        state.paused = True
    elif kind == KIND_RESUME:
        state.paused = False
    elif kind == KIND_START:
        state.status = ST_RUNNING
        state.attempt = 1
    elif kind == KIND_SUBMIT:
        outcome = payload.get(1)
        if outcome == 0:
            state.status = ST_SUBMITTED
            state.result = ResultRecord(
                value=RESULT_VALUE_CODES[payload.get(0)],
                producer=command.principal,
                verified=None,
                attempt=state.attempt,
                goal=state.goal,
                plan=state.plan,
                producer_lease=state.lease,
            )
        else:
            state.status = ST_FAILED
            state.result = None
    elif kind == KIND_VERIFY:
        state.status = ST_DONE
        assert state.result is not None
        state.result = replace(state.result, verified=RESULT_VALUE_CODES[payload.get(0)])
    elif kind == KIND_ARM_TIMER:
        state.timer = TimerRecord(TS_ARMED, state.attempt, state.goal, state.plan,
                                 state.pause_epoch)
        state.retry_ready = False
    elif kind == KIND_FIRE_TIMER:
        assert state.timer is not None
        state.timer = replace(state.timer, status=TS_FIRED)
        state.retry_ready = True
    elif kind == KIND_RETRY:
        state.attempt += 1
        state.status = ST_RUNNING
        state.result = None
        state.timer = _disarmed_timer()
        state.retry_ready = False
        state.effect = None
    elif kind == KIND_CANCEL:
        state.cancelled = True
        state.status = ST_CANCELLED
        state.retry_ready = False
        state.timer = _disarmed_timer()
    elif kind == EVENT_EFFECT_PREPARED:
        fence = OutboxEntry.from_map(event.payload[1])
        state.effect = EffectRecord(
            status=ES_PREPARED,
            effect_id=fence.effect_id,
            attempt=fence.attempt,
            goal=fence.goal,
            plan=fence.plan,
            lease=fence.lease,
            pause_epoch=fence.pause_epoch,
            issuing_command_id=fence.command_id,
            token=fence.token,
            writer=fence.writer,
        )
    elif kind == EVENT_OUTBOX_ENQUEUED:
        state.outbox = state.outbox + [OutboxEntry.from_map(event.payload[1])]
    elif kind == KIND_MARK_DISPATCH:
        assert state.effect is not None
        token = payload.get(0)
        state.effect = replace(state.effect, status=ES_INFLIGHT)
        state.outbox = [o for o in state.outbox if o.token != token]
    elif kind == KIND_OBSERVE_EFFECT:
        outcome = payload.get(1)
        status = {OUTCOME_SUCCESS: ES_SUCCEEDED,
                  OUTCOME_KNOWN_NO_EFFECT: ES_KNOWN_NO_EFFECT,
                  OUTCOME_UNKNOWN: ES_UNKNOWN}[outcome]
        assert state.effect is not None
        state.effect = replace(state.effect, status=status)
    elif kind == KIND_RECONCILE_EFFECT:
        outcome = payload.get(1)
        status = {OUTCOME_SUCCESS: ES_SUCCEEDED,
                  OUTCOME_KNOWN_NO_EFFECT: ES_KNOWN_NO_EFFECT}[outcome]
        assert state.effect is not None
        state.effect = replace(state.effect, status=status)
    else:
        raise Refusal(FIELD_INVALID, DET_BAD_TRANSITION, [5], "known event kind", kind)

    state.ordinal = event.ordinal
    state.tail = event.digest


@dataclass
class Batch:
    command: Command
    events: list[StoredEvent]
    receipt: Receipt
    pre_state: KernelState
    post_state: KernelState


class Admission:
    """Result of ``admit``: ``fresh``, ``cached`` or ``refused``."""

    def __init__(self, outcome: str, batch: Optional[Batch] = None,
                 receipt: Optional[Receipt] = None, refusal: Optional[Refusal] = None):
        self.outcome = outcome
        self.batch = batch
        self.receipt = receipt
        self.refusal = refusal


def build_batch(state: KernelState, command: Command) -> Batch:
    pre = state.copy()
    post = state.copy()
    events: list[StoredEvent] = []
    if command.kind == KIND_PREPARE_EFFECT:
        fence = _effect_fence_map(command, state, command.payload.get(0))
        event_kinds = (EVENT_EFFECT_PREPARED, EVENT_OUTBOX_ENQUEUED)
    else:
        fence = None
        event_kinds = (command.kind,)

    previous = state.tail
    ordinal = state.ordinal
    command_digest_value = command_digest(command)
    for event_kind in event_kinds:
        ordinal += 1
        data = fence if fence is not None else None
        candidate = StoredEvent(
            schema_epoch=SCHEMA_EPOCH,
            aggregate=AGGREGATE,
            ordinal=ordinal,
            previous=previous,
            command_digest=command_digest_value,
            kind=event_kind,
            payload={0: command.to_map(), 1: data},
            writer=state.writer,
            digest=b"",
        )
        candidate = replace(candidate, digest=event_digest(candidate))
        events.append(candidate)
        previous = candidate.digest
        _apply_event(post, command, candidate)

    receipt = Receipt(
        id=command.id,
        command_digest=command_digest_value,
        first_ordinal=events[0].ordinal,
        last_ordinal=events[-1].ordinal,
        last_event_digest=events[-1].digest,
        result_class=0,
        result_bytes=_receipt_result_bytes(command.id, events[0].ordinal,
                                           events[-1].ordinal, events[-1].digest),
    )
    post.receipts = sorted(post.receipts + [receipt], key=lambda r: r.id)
    return Batch(command=command, events=events, receipt=receipt, pre_state=pre, post_state=post)


def admit(state: KernelState, command: Command) -> Admission:
    """Admission function (section 4).  Returns fresh batch, cached receipt or refusal."""
    existing = state.receipt_by_id(command.id)
    if existing is not None:
        if existing.command_digest == command_digest(command):
            return Admission("cached", receipt=existing)
        return Admission("refused", refusal=Refusal(
            COMMAND_CONFLICT, DET_COMMAND_DIGEST, [1],
            expected=existing.command_digest, observed=command_digest(command)))
    try:
        check_command(state, command)
    except Refusal as refusal:
        return Admission("refused", refusal=refusal)
    batch = build_batch(state, command)
    return Admission("fresh", batch=batch, receipt=batch.receipt)


# ---------------------------------------------------------------------------
# Structural validation and folding
# ---------------------------------------------------------------------------
def _normalise_event(raw: Any) -> StoredEvent:
    if isinstance(raw, StoredEvent):
        return raw
    if isinstance(raw, dict):
        return StoredEvent.from_map(raw)
    raise Refusal(CHAIN_MISMATCH, DET_BAD_TRANSITION, [],
                  "StoredEvent", type(raw).__name__)


def _check_event_structure(event: StoredEvent, expected_ordinal: int,
                           previous_digest: bytes, state: KernelState,
                           index: int) -> None:
    if event.schema_epoch != SCHEMA_EPOCH:
        raise Refusal(UNSUPPORTED_SCHEMA, DET_SCHEMA, [0], SCHEMA_EPOCH,
                      event.schema_epoch, index=index)
    if event.aggregate != AGGREGATE:
        raise Refusal(CHAIN_MISMATCH, DET_AGGREGATE, [1], AGGREGATE,
                      event.aggregate, index=index)
    if event.ordinal != expected_ordinal:
        raise Refusal(CHAIN_MISMATCH, DET_CHAIN_ORDINAL, [2], expected_ordinal,
                      event.ordinal, index=index)
    if event.previous != previous_digest:
        raise Refusal(CHAIN_MISMATCH, DET_CHAIN_PREVIOUS, [3], previous_digest,
                      event.previous, index=index)
    computed = event_digest(event)
    if event.digest != computed:
        raise Refusal(CHAIN_MISMATCH, DET_CHAIN_DIGEST, [8], computed,
                      event.digest, index=index)
    if event.writer != state.writer:
        raise Refusal(CHAIN_MISMATCH, DET_WRITER_EPOCH, [7], state.writer,
                      event.writer, index=index)


def _fold(log: list) -> KernelState:
    """Fold a canonical committed event log.  Raises ``Refusal`` at the first violation."""
    state = genesis_state()
    previous_digest = GENESIS_PREV
    index = 0
    length = len(log)
    while index < length:
        event = _normalise_event(log[index])
        _check_event_structure(event, index + 1, previous_digest, state, index)

        command_raw = event.payload[0]
        command = Command.from_map(command_raw)
        if command_digest(command) != event.command_digest:
            raise Refusal(CHAIN_MISMATCH, DET_COMMAND_DIGEST, [4],
                          command_digest(command), event.command_digest, index=index)

        existing = state.receipt_by_id(command.id)
        if existing is not None:
            if existing.command_digest == command_digest(command):
                raise Refusal(FIELD_INVALID, DET_BAD_TRANSITION, [1],
                              "cached receipt reuse", "duplicate append", index=index)
            raise Refusal(COMMAND_CONFLICT, DET_COMMAND_DIGEST, [1],
                          existing.command_digest, command_digest(command), index=index)

        try:
            check_command(state, command, index=index)
        except Refusal as refusal:
            if refusal.index is None:
                refusal.index = index
            raise

        if command.kind == KIND_PREPARE_EFFECT:
            if event.kind != EVENT_EFFECT_PREPARED:
                raise Refusal(FIELD_INVALID, DET_BAD_TRANSITION, [5],
                              EVENT_EFFECT_PREPARED, event.kind, index=index)
            if index + 1 >= length:
                raise Refusal(CHAIN_MISMATCH, DET_CHAIN_ORDINAL, [2],
                              index + 2, None, index=index)
            second = _normalise_event(log[index + 1])
            _check_event_structure(second, index + 2, event.digest, state, index + 1)
            if second.kind != EVENT_OUTBOX_ENQUEUED:
                raise Refusal(FIELD_INVALID, DET_BAD_TRANSITION, [5],
                              EVENT_OUTBOX_ENQUEUED, second.kind, index=index + 1)
            second_command = Command.from_map(second.payload[0])
            if command_digest(second_command) != second.command_digest or \
                    second.command_digest != event.command_digest:
                raise Refusal(CHAIN_MISMATCH, DET_COMMAND_DIGEST, [4], index=index + 1)
            _apply_event(state, command, event)
            _apply_event(state, command, second)
            last_event = second
            batch_size = 2
        else:
            if event.kind != command.kind:
                raise Refusal(FIELD_INVALID, DET_BAD_TRANSITION, [5],
                              command.kind, event.kind, index=index)
            _apply_event(state, command, event)
            last_event = event
            batch_size = 1

        receipt = Receipt(
            id=command.id,
            command_digest=command_digest(command),
            first_ordinal=event.ordinal,
            last_ordinal=last_event.ordinal,
            last_event_digest=last_event.digest,
            result_class=0,
            result_bytes=_receipt_result_bytes(command.id, event.ordinal,
                                               last_event.ordinal, last_event.digest),
        )
        state.receipts = sorted(state.receipts + [receipt], key=lambda r: r.id)
        previous_digest = last_event.digest
        index += batch_size

    return state


@dataclass
class ValidationResult:
    status: str
    code: Optional[int] = None
    detail: Optional[int] = None
    path: Optional[list] = None
    first_index: Optional[int] = None
    message: str = ""

    @property
    def valid(self) -> bool:
        return self.status == "VALID_BOUNDED"

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "code": self.code,
            "detail": self.detail,
            "path": self.path,
            "first_index": self.first_index,
            "message": self.message,
        }


def validate_log(log: Any) -> ValidationResult:
    if not isinstance(log, list):
        return ValidationResult("INCONCLUSIVE", message="log is not a list")
    if len(log) > MAX_COMMITTED_EVENTS:
        return ValidationResult("OUT_OF_SCOPE",
                                message="log exceeds MaxCommittedEvents=20")
    try:
        _fold(log)
    except Refusal as refusal:
        return ValidationResult("INVALID_TRACE", refusal.code, refusal.detail,
                                refusal.path, refusal.index, refusal.message)
    return ValidationResult("VALID_BOUNDED", message="ok")


def RefValid(log: Any) -> bool:
    """True only for a structurally valid, in-bounds canonical committed log."""
    return validate_log(log).valid


def RefState(log: Any) -> KernelState:
    """Fold a canonical committed log into canonical state (sections 3-4)."""
    result = validate_log(log)
    if not result.valid:
        raise Refusal(
            result.code if result.code is not None else CHAIN_MISMATCH,
            result.detail if result.detail is not None else DET_BAD_TRANSITION,
            result.path, message=result.message, index=result.first_index)
    return _fold(log)


def RefProject(log: Any) -> tuple:
    """The fixed 16-field projection tuple for a canonical committed log (section 5)."""
    return projection_tuple(RefState(log))


# ---------------------------------------------------------------------------
# Fixture construction helper (mirrors the section 10 ``Fresh`` construction)
# ---------------------------------------------------------------------------
def make_command(state: KernelState, kind: int, payload: Optional[dict] = None, *,
                 command_id: Optional[int] = None,
                 aggregate: Optional[int] = None,
                 task: Optional[int] = None,
                 principal: Optional[int] = None,
                 capability: Optional[int] = None,
                 goal: Optional[int] = None,
                 plan: Optional[int] = None,
                 lease: Optional[int] = None,
                 writer: Optional[int] = None,
                 pause_epoch: Optional[int] = None,
                 attempt: Optional[int] = None,
                 expected_ordinal: Optional[int] = None,
                 expected_state_digest: Optional[bytes] = None) -> Command:
    next_id = command_id if command_id is not None else _next_unused_id(state)
    return Command(
        schema_epoch=SCHEMA_EPOCH,
        id=next_id,
        kind=kind,
        aggregate=AGGREGATE if aggregate is None else aggregate,
        task=TASK if task is None else task,
        principal=default_principal(state, kind) if principal is None else principal,
        capability=kind if capability is None else capability,
        goal=state.goal if goal is None else goal,
        plan=state.plan if plan is None else plan,
        lease=state.lease if lease is None else lease,
        writer=state.writer if writer is None else writer,
        pause_epoch=state.pause_epoch if pause_epoch is None else pause_epoch,
        attempt=state.attempt if attempt is None else attempt,
        expected_ordinal=state.ordinal if expected_ordinal is None else expected_ordinal,
        expected_state_digest=(state_digest(state) if expected_state_digest is None
                               else expected_state_digest),
        payload=dict(payload or {}),
    )


def _next_unused_id(state: KernelState) -> int:
    used = {r.id for r in state.receipts}
    candidate = 1
    while candidate in used:
        candidate += 1
    return candidate


def resolve_payload(state: KernelState, raw_payload: dict) -> dict:
    """Resolve a JSON-friendly payload map into a typed one.

    Values may be integers, ``"hex:<hex>"`` byte strings, or the dynamic tokens
    ``"@effect_token"``, ``"@outbox_token"`` and ``"@wrong_token"``.
    """
    resolved: dict = {}
    for key, value in (raw_payload or {}).items():
        k = int(key)
        if isinstance(value, str):
            if value.startswith("hex:"):
                resolved[k] = bytes.fromhex(value[4:])
            elif value == "@effect_token":
                resolved[k] = state.effect.token if state.effect is not None else b""
            elif value == "@outbox_token":
                resolved[k] = state.outbox[0].token if state.outbox else b""
            elif value == "@wrong_token":
                resolved[k] = b"\xff" * 32
            else:
                resolved[k] = value
        else:
            resolved[k] = value
    return resolved


def command_from_spec(state: KernelState, spec: dict) -> Command:
    """Build a command from a JSON descriptor against the current canonical state."""
    overrides = {}
    for key in ("aggregate", "task", "principal", "capability", "goal", "plan", "lease",
                "writer", "pause_epoch", "attempt", "expected_ordinal"):
        if key in spec and spec[key] is not None:
            overrides[key] = spec[key]
    expected_digest = None
    if spec.get("expected_digest") not in (None, ""):
        expected_digest = bytes.fromhex(spec["expected_digest"])
    return make_command(
        state,
        int(spec["kind"]),
        resolve_payload(state, spec.get("payload", {})),
        command_id=spec.get("id"),
        expected_state_digest=expected_digest,
        **overrides,
    )
