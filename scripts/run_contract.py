"""Strict runtime contract for control-plane v1 run evidence.

The JSON schema intentionally leaves additional producer evidence fields open.  This module
therefore validates every declared ``run`` property exactly while rejecting malformed values
before worker state transitions use them.  Parsing callers separately enforce byte and nesting
limits; this validator also rejects non-finite numeric values anywhere in the decoded object.
"""

from __future__ import annotations

import math
import re
from typing import Any


IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SHA_RE = re.compile(r"^[0-9a-f]{40,64}$")
DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
MODEL_ALIAS_RE = re.compile(r"^[a-z][a-z0-9-]{2,31}$")
MODEL_ALIASES = frozenset({"sonnet-routine", "opus-complex", "opus-review"})
NETWORK_POLICIES = frozenset({"provider-only", "none"})
NETWORK_PROFILES = frozenset({"anthropic", "cursor", "gemini", "openrouter", "sentry-local"})
RUN_STATUSES = frozenset({
    "pending", "prepared", "running", "succeeded", "failed", "blocked", "cancelled", "stale",
})

MAX_NESTING = 32
MAX_CONTAINER_ITEMS = 10000
MAX_STRING_BYTES = 1 << 20

# Complete projection required whenever a run claims an immutable assignment. Keep this list
# next to the conditional so producers cannot silently drift from the runtime contract.
ASSIGNMENT_ATTRIBUTION_FIELDS = (
    "project_id", "engine", "provider", "capacity_pool", "billing_basis",
    "metered_approved", "host", "model", "sandbox_profile", "network_policy", "network_profile",
    "source_repository", "source_branch", "source_sha", "source_evidence",
    "allowed_paths", "publication_policy", "default_branch", "integration_branch",
    "assignment",
)


class RunContractError(ValueError):
    """A run record is not accepted by the control-plane v1 runtime contract."""


def _walk(value: object, depth: int = 0) -> None:
    if depth > MAX_NESTING:
        raise RunContractError("run evidence nesting exceeds the limit")
    if isinstance(value, str):
        try:
            encoded_length = len(value.encode("utf-8", "strict"))
        except UnicodeError as exc:
            raise RunContractError("run evidence contains invalid text") from exc
        if encoded_length > MAX_STRING_BYTES:
            raise RunContractError("run evidence string exceeds the limit")
        return
    if isinstance(value, float) and not math.isfinite(value):
        raise RunContractError("run evidence contains a non-finite number")
    if isinstance(value, dict):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise RunContractError("run evidence object has too many fields")
        for key, item in value.items():
            if not isinstance(key, str):
                raise RunContractError("run evidence object keys must be strings")
            _walk(key, depth + 1)
            _walk(item, depth + 1)
    elif isinstance(value, list):
        if len(value) > MAX_CONTAINER_ITEMS:
            raise RunContractError("run evidence array has too many items")
        for item in value:
            _walk(item, depth + 1)


def _required_string(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) < 1:
        raise RunContractError(f"run evidence {label} must be a nonempty string")


def _identifier(value: object, label: str) -> None:
    if not isinstance(value, str) or not IDENTIFIER_RE.fullmatch(value):
        raise RunContractError(f"run evidence {label} is not a canonical identifier")


def _nonnegative_int(value: object, label: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise RunContractError(f"run evidence {label} must be a non-negative integer")


def _optional_string(value: object, label: str) -> None:
    if value is not None:
        _required_string(value, label)


def validate_run(value: object) -> dict[str, Any]:
    """Validate the ``$defs.run`` shape and return the original object.

    Unknown fields are accepted because the published schema has ``additionalProperties``
    enabled.  The conditional assignment projection is enforced exactly as the schema's
    ``allOf/if/then`` clause requires.
    """
    _walk(value)
    if not isinstance(value, dict):
        raise RunContractError("run evidence must be an object")

    required = {
        "schema_version", "id", "task_id", "worker", "worktree", "base_commit", "pid",
        "lease_expires", "deadline", "usage", "result", "status",
    }
    missing = required - value.keys()
    if missing:
        raise RunContractError("run evidence is missing required fields")
    if isinstance(value.get("schema_version"), bool) or value.get("schema_version") != 1 \
            or not isinstance(value.get("schema_version"), int):
        raise RunContractError("run evidence schema_version must be 1")

    _identifier(value.get("id"), "id")
    _identifier(value.get("task_id"), "task_id")
    for label in ("worker", "worktree", "lease_expires", "deadline"):
        _required_string(value.get(label), label)
    if not isinstance(value.get("base_commit"), str) or not SHA_RE.fullmatch(value["base_commit"]):
        raise RunContractError("run evidence base_commit is not a canonical object id")
    _nonnegative_int(value.get("pid"), "pid")
    if "process_group" in value:
        _nonnegative_int(value["process_group"], "process_group")

    if "role" in value and (not isinstance(value["role"], str)
                            or value["role"] not in {"implementer", "verifier"}):
        raise RunContractError("run evidence role is invalid")
    if "model_alias" in value:
        alias = value["model_alias"]
        if not isinstance(alias, str) or (alias not in MODEL_ALIASES
                                          and MODEL_ALIAS_RE.fullmatch(alias) is None):
            raise RunContractError("run evidence model_alias is invalid")
    if "network_policy" in value and (not isinstance(value["network_policy"], str)
                                      or value["network_policy"] not in NETWORK_POLICIES):
        raise RunContractError("run evidence network_policy is invalid")
    if "assignment_digest" in value and (
            not isinstance(value["assignment_digest"], str)
            or not DIGEST_RE.fullmatch(value["assignment_digest"])):
        raise RunContractError("run evidence assignment_digest is invalid")
    if "assignment" in value and not isinstance(value["assignment"], dict):
        raise RunContractError("run evidence assignment must be an object")
    if "project_id" in value:
        _identifier(value["project_id"], "project_id")
    if "engine" in value:
        _required_string(value["engine"], "engine")
    if "provider" in value:
        _required_string(value["provider"], "provider")
    if "capacity_pool" in value and value["capacity_pool"] is not None:
        _required_string(value["capacity_pool"], "capacity_pool")
    if "billing_basis" in value:
        _optional_string(value["billing_basis"], "billing_basis")
    if "metered_approved" in value and not isinstance(value["metered_approved"], bool):
        raise RunContractError("run evidence metered_approved must be boolean")
    for label in ("host", "sandbox_profile", "source_repository", "source_branch", "publication_policy"):
        if label in value:
            _required_string(value[label], label)
    if "model" in value and value["model"] is not None:
        _required_string(value["model"], "model")
    if "network_profile" in value and (not isinstance(value["network_profile"], str)
                                       or value["network_profile"] not in NETWORK_PROFILES):
        raise RunContractError("run evidence network_profile is invalid")
    if "source_sha" in value and (
            not isinstance(value["source_sha"], str) or not SHA_RE.fullmatch(value["source_sha"])):
        raise RunContractError("run evidence source_sha is invalid")
    if "source_evidence" in value and not isinstance(value["source_evidence"], dict):
        raise RunContractError("run evidence source_evidence must be an object")
    for label in ("default_branch", "integration_branch"):
        if label in value:
            _required_string(value[label], label)
    if "allowed_paths" in value:
        paths = value["allowed_paths"]
        if not isinstance(paths, list) or not paths or not all(
                isinstance(item, str) and len(item) >= 1 for item in paths):
            raise RunContractError("run evidence allowed_paths is invalid")
    if not isinstance(value.get("usage"), dict):
        raise RunContractError("run evidence usage must be an object")
    if not isinstance(value.get("result"), (dict, str)):
        raise RunContractError("run evidence result must be an object or string")
    if value.get("status") not in RUN_STATUSES:
        raise RunContractError("run evidence status is invalid")
    # A prepared record is the one pre-launch boundary and may retain the schema's optional
    # process_group compatibility.  Every later state is an active worker boundary, where
    # validate-control-state.py requires both live process identities and worker-evidence.py
    # activate() produces both fields together.
    if value["status"] != "prepared":
        if value.get("pid", 0) < 1:
            raise RunContractError("run evidence active pid must be positive")
        if not isinstance(value.get("process_group"), int) or value["process_group"] < 1:
            raise RunContractError("run evidence active process_group must be positive")

    if "assignment_digest" in value:
        if not set(ASSIGNMENT_ATTRIBUTION_FIELDS) <= value.keys():
            raise RunContractError("assignment-bound run evidence is missing attribution fields")
    return value


validate_run_evidence = validate_run
