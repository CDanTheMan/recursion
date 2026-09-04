"""Pure M1A strict JSON decoding and RFC 8785-compatible canonical digests."""

from __future__ import annotations

import copy
import hashlib
import json


MAX_IJSON_INTEGER = 9_007_199_254_740_991
MAX_INPUT_BYTES = 1_048_576
MAX_COLLECTION_ITEMS = 2_048
MAX_DEPTH = 16

COMMAND_FIELDS = {
    "command_schema_version", "command_id", "command_type", "actor_id", "auth_ref",
    "lease_ref", "logical_time", "expected_state_version", "expected_state_digest",
    "goal_ref", "plan_ref", "payload", "payload_digest", "candidate_digest",
    "content_digest",
}
EVENT_FIELDS = {
    "event_schema_version", "event_id", "stream_id", "sequence", "previous_event_digest",
    "logical_time", "command_id", "command_digest", "event_type", "primary_record",
    "related_records", "state_delta_digest", "content_digest",
}
DOMAIN_FIELDS = {
    "object_type", "schema_version", "id", "version", "created_by_actor_id",
    "created_under_lease", "causation_id", "correlation_id", "created_logical_time",
    "payload", "content_digest",
}


class M1AError(ValueError):
    """A closed, stable M1A failure rather than a host-language parser exception."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(detail or code)
        self.code = code
        self.detail = detail


def _parse_int(raw: str) -> int:
    if raw == "-0":
        raise M1AError("E-SCHEMA-INVALID", "lexical negative zero")
    digits = raw[1:] if raw.startswith("-") else raw
    if len(digits) > 16:
        raise M1AError("E-SCHEMA-BOUND", "integer bound exceeded")
    try:
        value = int(raw)
    except ValueError as exc:
        raise M1AError("E-SCHEMA-INVALID", "invalid integer") from exc
    if abs(value) > MAX_IJSON_INTEGER:
        raise M1AError("E-SCHEMA-BOUND", "integer bound exceeded")
    return value


def _reject_float(_raw: str):
    raise M1AError("E-SCHEMA-INVALID", "floating-point value")


def _reject_constant(raw: str):
    raise M1AError("E-SCHEMA-INVALID", f"non-I-JSON constant {raw}")


def _pairs_no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise M1AError("E-SCHEMA-DUPLICATE", f"duplicate key {key}")
        result[key] = value
    return result


def _check_tree(value, *, depth: int = 0) -> None:
    if depth > MAX_DEPTH:
        raise M1AError("E-SCHEMA-BOUND", "nesting depth exceeded")
    if isinstance(value, str):
        if "\x00" in value:
            raise M1AError("E-SCHEMA-INVALID", "NUL string")
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise M1AError("E-SCHEMA-INVALID", "unpaired surrogate") from exc
    elif isinstance(value, bool) or value is None:
        return
    elif isinstance(value, int):
        if abs(value) > MAX_IJSON_INTEGER:
            raise M1AError("E-SCHEMA-BOUND", "integer bound exceeded")
    elif isinstance(value, list):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise M1AError("E-SCHEMA-BOUND", "array count exceeded")
        for item in value:
            _check_tree(item, depth=depth + 1)
    elif isinstance(value, dict):
        if len(value) > MAX_COLLECTION_ITEMS:
            raise M1AError("E-SCHEMA-BOUND", "object count exceeded")
        for key, item in value.items():
            _check_tree(key, depth=depth + 1)
            _check_tree(item, depth=depth + 1)
    else:
        raise M1AError("E-SCHEMA-INVALID", "unsupported JSON value")


def strict_loads(raw: str | bytes):
    if isinstance(raw, bytes):
        if len(raw) > MAX_INPUT_BYTES:
            raise M1AError("E-SCHEMA-BOUND", "input byte bound exceeded")
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise M1AError("E-SCHEMA-INVALID", "invalid UTF-8") from exc
    elif isinstance(raw, str):
        try:
            size = len(raw.encode("utf-8", errors="strict"))
        except UnicodeEncodeError as exc:
            raise M1AError("E-SCHEMA-INVALID", "unpaired surrogate") from exc
        if size > MAX_INPUT_BYTES:
            raise M1AError("E-SCHEMA-BOUND", "input byte bound exceeded")
        text = raw
    else:
        raise M1AError("E-SCHEMA-INVALID", "input must be bytes or text")
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_no_duplicates,
            parse_int=_parse_int,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except M1AError:
        raise
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise M1AError("E-SCHEMA-INVALID", "malformed JSON") from exc
    _check_tree(value)
    return value


def _require_closed(value: dict, allowed: set[str]) -> None:
    unknown = set(value) - allowed
    if unknown:
        raise M1AError("E-SCHEMA-UNKNOWN-FIELD", min(unknown))
    missing = allowed - set(value)
    if missing:
        raise M1AError("E-SCHEMA-MISSING-FIELD", min(missing))


def decode(raw: str | bytes, schema_epoch: str = "m1a-1"):
    """Decode one closed M1A envelope without observing ambient schema files."""

    if schema_epoch != "m1a-1":
        raise M1AError("E-SCHEMA-UNKNOWN-VERSION", schema_epoch)
    value = strict_loads(raw)
    if not isinstance(value, dict):
        raise M1AError("E-SCHEMA-INVALID", "root must be an object")
    if "command_schema_version" in value:
        if value["command_schema_version"] != "m1a-command-1":
            raise M1AError("E-SCHEMA-UNKNOWN-VERSION", str(value["command_schema_version"]))
        _require_closed(value, COMMAND_FIELDS)
    elif "event_schema_version" in value:
        if value["event_schema_version"] != "m1a-event-1":
            raise M1AError("E-SCHEMA-UNKNOWN-VERSION", str(value["event_schema_version"]))
        _require_closed(value, EVENT_FIELDS)
    elif "schema_version" in value or "object_type" in value:
        if "schema_version" not in value:
            raise M1AError("E-SCHEMA-MISSING-FIELD", "schema_version")
        _require_closed(value, DOMAIN_FIELDS)
    else:
        raise M1AError("E-SCHEMA-MISSING-FIELD", "registered envelope discriminator")
    return value


def _utf16_key(value: str) -> bytes:
    return value.encode("utf-16be")


def canonical_bytes(value) -> bytes:
    """Return the RFC 8785 bytes for M1A's integer-only I-JSON subset."""

    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > MAX_IJSON_INTEGER:
            raise M1AError("E-SCHEMA-BOUND", "integer bound exceeded")
        return str(value).encode("ascii")
    if isinstance(value, str):
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise M1AError("E-SCHEMA-INVALID", "unpaired surrogate") from exc
        return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if isinstance(value, list):
        return b"[" + b",".join(canonical_bytes(item) for item in value) + b"]"
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise M1AError("E-SCHEMA-INVALID", "object key must be text")
        keys = sorted(value, key=_utf16_key)
        return b"{" + b",".join(
            canonical_bytes(key) + b":" + canonical_bytes(value[key]) for key in keys
        ) + b"}"
    raise M1AError("E-SCHEMA-INVALID", "unsupported canonical value")


def digest(value, *, omit_content_digest: bool = False) -> str:
    operand = copy.deepcopy(value)
    if omit_content_digest and isinstance(operand, dict):
        operand.pop("content_digest", None)
    return hashlib.sha256(canonical_bytes(operand)).hexdigest()


def seal(value: dict) -> dict:
    result = copy.deepcopy(value)
    result.pop("content_digest", None)
    result["content_digest"] = digest(result)
    return result
