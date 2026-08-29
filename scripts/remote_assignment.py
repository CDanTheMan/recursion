#!/usr/bin/env python3
"""Immutable assignment envelope contract for the remote execution adapters. INERT.

Shared foundation for the Phase 6 (Cursor Cloud) and Phase 7 (Grok Bot) adapters of
docs/plans/recursion-v2-execution-fabric.md. This module is pure: it validates, canonicalises
and digests. It opens no socket, reads no credential value into any record, and has no CLI.

What lives here:

  * the typed error taxonomy both adapters raise (code -> retryable -> process exit code),
    so a caller never has to string-match a message to decide whether to retry, defer, or
    stop;
  * the immutable assignment contract -- the subset of the plan's assignment record that a
    remote backend needs -- plus its canonical digest;
  * the secret-REFERENCE contract. A manifest, an assignment, and an envelope carry
    ``secret:<ENV_NAME>`` strings. They never carry a value. ``resolve_secret`` is the only
    function that reads a value, it returns it to the caller, and no function in this
    package writes a resolved value anywhere;
  * a deliberately over-broad screen for secret MATERIAL that refuses to let a credential
    shape reach a durable record or an outbound envelope.

This is NOT the Phase 1 canonical registry. Phase 1 defines engine/provider/pool/model/host/
sandbox/routing/project schemas and their compatibility readers; that work is not in this
scope. What is here is the minimum the two remote adapters must agree on so they do not each
grow their own digest and their own idea of what an assignment is.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from urllib.parse import urlsplit

SCHEMA_VERSION = 1

# --- exit vocabulary --------------------------------------------------------------------
# 0/2/3 are the house codes (scripts/resolve-engine.py, scripts/resolve-connector.py):
# 0 ok, 2 present-but-invalid, 3 absent-or-disabled. 4 and 75 extend it:
# 4  refused by policy -- PAUSE, an unauthorized result, a redaction violation. A human
#    decides; retrying changes nothing.
# 10 retryable transport failure -- the same request may be re-sent after backoff.
# 75 defer -- the established requeue code (docs/plans/engine-plugin-architecture.md
#    Component 4 step 3). The task stays queued; this is not a failure and never escalates.
EXIT_OK = 0
EXIT_INVALID = 2
EXIT_UNAVAILABLE = 3
EXIT_REFUSED = 4
EXIT_RETRYABLE = 10
EXIT_DEFER = 75

# code -> (retryable, exit_code)
ERROR_TABLE: dict[str, tuple[bool, int]] = {
    # absent / disabled / human configuration seam
    "manifest-absent": (False, EXIT_UNAVAILABLE),
    "adapter-disabled": (False, EXIT_UNAVAILABLE),
    "credential-absent": (False, EXIT_UNAVAILABLE),
    "auth-failed": (False, EXIT_UNAVAILABLE),
    # present but wrong
    "manifest-invalid": (False, EXIT_INVALID),
    "request-invalid": (False, EXIT_INVALID),
    "assignment-invalid": (False, EXIT_INVALID),
    "malformed-response": (False, EXIT_INVALID),
    "not-found": (False, EXIT_INVALID),
    # policy refusals
    "paused": (False, EXIT_REFUSED),
    "unauthorized-result": (False, EXIT_REFUSED),
    "redaction-violation": (False, EXIT_REFUSED),
    "result-channel-violation": (False, EXIT_REFUSED),
    "attempts-exhausted": (False, EXIT_REFUSED),
    "unreconciled-attempt": (False, EXIT_REFUSED),
    "live-transport-disabled": (False, EXIT_REFUSED),
    # retryable transport
    "transport-error": (True, EXIT_RETRYABLE),
    "transport-timeout": (True, EXIT_RETRYABLE),
    "rate-limited": (True, EXIT_RETRYABLE),
    "provider-error": (True, EXIT_RETRYABLE),
    # defer -- capacity, not failure
    "lease-unavailable": (True, EXIT_DEFER),
    "quota-exhausted": (True, EXIT_DEFER),
    "provider-unavailable": (True, EXIT_DEFER),
}


class RemoteError(Exception):
    """A typed adapter outcome. ``code`` is the contract; the message is for humans."""

    def __init__(self, code: str, message: str, detail: dict | None = None) -> None:
        if code not in ERROR_TABLE:
            raise KeyError(f"unknown remote error code: {code!r}")
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.detail = dict(detail or {})

    @property
    def retryable(self) -> bool:
        return ERROR_TABLE[self.code][0]

    @property
    def exit_code(self) -> int:
        return ERROR_TABLE[self.code][1]

    def as_record(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
            "exit_code": self.exit_code,
            "detail": self.detail,
        }


# --- canonicalisation -------------------------------------------------------------------

def canonical_bytes(value: object) -> bytes:
    """One serialisation, forever: sorted keys, no insignificant whitespace, UTF-8.

    Every digest in both adapters is taken over this. Two processes that disagree about
    key order must still produce the same assignment_digest, or idempotency is a lie.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def canonical_digest(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


# --- secret references ------------------------------------------------------------------

SECRET_REF_RE = re.compile(r"secret:([A-Z][A-Z0-9_]{2,63})")
ENV_NAME_RE = re.compile(r"[A-Z][A-Z0-9_]{2,63}")

# A remote backend may hold exactly one credential: its own. It may never name a credential
# that grants authority over the controller, the deploy path, or another provider. The Grok
# Bot boundary in particular (audit 2026-08-28, "Grok Bot"): all Bots share one account-scoped
# computer, so a deploy key handed to one is a deploy key handed to every session on it.
CONTROLLER_CREDENTIAL_ENV = frozenset({
    "GITHUB_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "OPENROUTER_API_KEY",
    "ANTHROPIC_API_KEY",
    "GH_TOKEN",
})
CONTROLLER_CREDENTIAL_PREFIX = ("RECURSION_", "SSH_", "GIT_SSH", "AWS_", "HERMES_")

# Key NAMES that announce a credential value. Broad, in the spirit of resolve-connector.py's
# env_passthrough screen, but not so broad that ordinary structural names collide: a bare
# "KEY" would reject `idempotency_key`, which carries no secret and must be recorded. Only the
# explicitly permitted manifest reference fields are exempt, and validate_secret_ref proves
# those values are references rather than credentials.
SECRET_KEY_SUBSTRING_RE = re.compile(
    r"(?:^|_)(?:TOKEN|SECRET|PASSWORD|CREDENTIAL|COOKIE|BEARER|API_?KEY|ACCESS_?KEY|"
    r"PRIVATE_?KEY|SIGNING_?KEY|AUTH_?KEY)(?:$|_)",
    re.IGNORECASE,
)
# A reference is data with authority.  It is valid only in these manifest fields; a
# generic ``*_ref`` field must not become a covert way to smuggle a credential reference
# through an envelope, assignment, response, or durable record.
EXPLICIT_SECRET_REFERENCE_FIELDS = frozenset({
    "endpoint_ref", "credential_ref", "signing_key_ref",
})

# Shapes of real credentials, anchored so an ordinary word cannot trip them ("risk-register"
# contains "sk-"). The label, never the matched text, is what appears in an error message:
# a screen that prints the secret it found is a leak with good intentions.
SECRET_VALUE_PATTERNS = (
    ("openai-style-key", re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{16,}")),
    ("stripe-style-key", re.compile(r"(?<![A-Za-z0-9])sk_(?:live|test)_[A-Za-z0-9]{12,}")),
    ("github-token", re.compile(
        r"(?<![A-Za-z0-9])(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("xai-key", re.compile(r"(?<![A-Za-z0-9])xai-[A-Za-z0-9]{16,}")),
    ("slack-token", re.compile(r"(?<![A-Za-z0-9])xox[abprs]-[A-Za-z0-9-]{10,}")),
    ("aws-access-key-id", re.compile(r"(?<![A-Za-z0-9])(?:AKIA|ASIA)[0-9A-Z]{16}")),
    ("pem-private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("json-web-token", re.compile(
        r"(?<![A-Za-z0-9])eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("authorization-header", re.compile(r"(?<![A-Za-z0-9])Bearer\s+\S{8,}")),
)

CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")


def validate_secret_ref(value: object, field: str,
                        code: str = "manifest-invalid") -> str:
    """``secret:<ENV_NAME>`` -> ``ENV_NAME``. Refuses anything that is not a reference."""
    if not isinstance(value, str) or not SECRET_REF_RE.fullmatch(value):
        raise RemoteError(code,
                          f"{field} must be a secret reference of the form "
                          f"'secret:<ENV_NAME>' (env name ^[A-Z][A-Z0-9_]{{2,63}}$), never a value")
    name = value.split(":", 1)[1]
    if name in CONTROLLER_CREDENTIAL_ENV or name.startswith(CONTROLLER_CREDENTIAL_PREFIX):
        raise RemoteError(code,
                          f"{field} names {name}, a controller/deploy credential; a remote "
                          "backend may reference only its own credential")
    return name


def resolve_secret(env_name: str, field: str) -> str:
    """The only reader of a credential value in this package. The value is returned to the
    caller and is never written to a record, a projection, a log, or an envelope."""
    if not ENV_NAME_RE.fullmatch(env_name):
        raise RemoteError("manifest-invalid", f"{field} resolves to an invalid env var name")
    value = os.environ.get(env_name, "")
    if not value.strip():
        raise RemoteError("credential-absent",
                          f"{field} references {env_name}, which is unset or empty; a human "
                          "sets this in the box .env and the loop never writes it")
    return value


def looks_like_secret_material(value: str) -> str:
    """Return the LABEL of the credential shape a string matched, or '' when it is clean.

    The label, never the match: an error message that quotes the credential it caught has
    moved the credential into a log line.
    """
    for label, pattern in SECRET_VALUE_PATTERNS:
        if pattern.search(value):
            return label
    return ""


def screen_for_secret_material(value: object, where: str,
                               code: str = "redaction-violation",
                               *, allowed_reference_paths=()) -> None:
    """Refuse credential-shaped material, with only exact schema paths exempted.

    ``credential_ref`` and friends are not globally safe field names.  The caller must pass
    the exact root-relative paths authorized by the schema, for example
    ``{("credential_ref",), ("endpoint_ref",)}`` for a validated manifest.  Nested records,
    arbitrary session fields, and all other structures receive no exemption.
    """
    allowed = {tuple(path) for path in allowed_reference_paths}

    def walk(item: object, display: str, path: tuple[str, ...]) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str):
                    raise RemoteError(code, f"{display} has a non-string key")
                child_path = path + (key,)
                if SECRET_KEY_SUBSTRING_RE.search(key) and child_path not in allowed:
                    raise RemoteError(
                        code,
                        f"{display}.{key} is a credential-shaped key name; remote records "
                        "and envelopes carry references, never secrets")
                walk(child, f"{display}.{key}", child_path)
            return
        if isinstance(item, list):
            for index, child in enumerate(item):
                walk(child, f"{display}[{index}]", path)
            return
        if isinstance(item, str):
            label = looks_like_secret_material(item)
            if label:
                raise RemoteError(code, f"{display} contains a value shaped like a {label}")
            if SECRET_REF_RE.fullmatch(item):
                if path not in allowed:
                    raise RemoteError(
                        code,
                        f"{display} contains a secret reference outside an explicitly "
                        "permitted schema field")
                # Validate even an explicitly allowed path here.  This prevents a caller from
                # treating the path exemption as proof that the reference itself is safe.
                validate_secret_ref(item, display, code=code)
            elif SECRET_REF_RE.search(item):
                raise RemoteError(code, f"{display} embeds a secret reference inside free text")

    walk(value, where, ())


# --- the immutable assignment -----------------------------------------------------------

TASK_ID_RE = re.compile(r"[a-z0-9][a-z0-9._-]{2,63}")
SLUG_RE = re.compile(r"[a-z][a-z0-9-]{1,63}")
SHA_RE = re.compile(r"[0-9a-f]{40}")
DIGEST_RE = re.compile(r"[0-9a-f]{64}")
ISO_UTC_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
MODEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}")

PUBLICATION_POLICIES = frozenset({"verified-integration-only", "review-branch-only"})

ASSIGNMENT_REQUIRED = (
    "task_id",
    "project_id",
    "source_repository",
    "source_branch",
    "source_sha",
    "engine",
    "provider",
    "capacity_pool",
    "host",
    "sandbox_profile",
    "publication_policy",
    "created_at",
)
# Present in every normalised assignment, defaulted when absent, so the digest is total: a
# field that is sometimes in the hashed set and sometimes not is a digest that cannot be
# compared across two runs.
ASSIGNMENT_OPTIONAL: dict[str, object] = {
    "seed_manifest_digest": "",
    "gate_digest": "",
    "model": "",
    "model_parameters": {},
    "network_profile": "",
    "allowed_paths": [],
    # Additional repositories are explicit, pinned inputs to a multi-repository task.  A
    # caller cannot widen this list at reconciliation time because it is part of the
    # immutable assignment digest.
    "authorized_repositories": [],
}
ASSIGNMENT_KEYS = frozenset(ASSIGNMENT_REQUIRED) | frozenset(ASSIGNMENT_OPTIONAL)


def _invalid(message: str) -> RemoteError:
    return RemoteError("assignment-invalid", message)


def validate_branch_name(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise _invalid(f"{field} must be a nonempty Git branch name")
    try:
        result = subprocess.run(
            ["git", "check-ref-format", "--branch", value],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except (OSError, ValueError):
        # ValueError covers strings Git cannot receive (notably an embedded NUL).  OSError
        # keeps a missing/unlaunchable Git binary fail closed instead of accepting a ref by
        # falling back to a subtly different local implementation.
        result = None
    if result is None or result.returncode != 0:
        raise _invalid(f"{field} is not a Git-valid branch name")
    return value


def validate_branch_pattern(value: object, field: str) -> str:
    """Validate a limited fnmatch pattern by probing its literal ref shape first.

    Result patterns are policy inputs, not returned refs, so ``*`` and ``?`` are allowed.
    Git-ref metacharacters and malformed path components are not.  Replacing the glob
    operators with ordinary characters before ``validate_branch_name`` keeps fnmatch from
    becoming the first parser of an attacker-controlled ref pattern.
    """
    if not isinstance(value, str) or not value:
        raise _invalid(f"{field} must be a nonempty branch pattern")
    probe = value.replace("*", "x").replace("?", "x")
    validate_branch_name(probe, field)
    return value


def validate_https_url(value: object, field: str, *, require_path: bool = False,
                       allow_query: bool = False,
                       code: str = "assignment-invalid") -> str:
    """https only, and no userinfo.

    A URL in this system travels to a vendor or is recorded durably. ``https://user:pass@host``
    would carry a credential inside a field everything else treats as non-secret, so the
    authority is rejected outright rather than stripped.
    """
    if not isinstance(value, str) or not value:
        raise RemoteError(code, f"{field} must be a nonempty string")
    if CONTROL_CHAR_RE.search(value):
        raise RemoteError(code, f"{field} contains a control character")
    try:
        parts = urlsplit(value)
    except ValueError:
        # urlsplit raises for malformed authority syntax (for example an unmatched
        # IPv6 bracket).  Parser details are not part of the boundary contract.
        raise RemoteError(code, f"{field} is not a well-formed https URL") from None
    if parts.scheme != "https":
        raise RemoteError(code,
                          f"{field} must be an https:// URL (got scheme {parts.scheme!r}); "
                          "ssh and scp-style remotes imply a key on the remote host")
    if "@" in parts.netloc:
        raise RemoteError(code, f"{field} carries userinfo in its authority; that is a credential")
    if not parts.hostname:
        raise RemoteError(code, f"{field} must name a host")
    if parts.fragment or (parts.query and not allow_query):
        raise RemoteError(code, f"{field} must not carry a query string or fragment")
    if require_path and not parts.path.strip("/"):
        raise RemoteError(code, f"{field} must name a repository path")
    return value


def validate_repository_url(value: object, field: str) -> str:
    return validate_https_url(value, field, require_path=True)


def validate_allowed_paths(value: object) -> list[str]:
    if not isinstance(value, list):
        raise _invalid("allowed_paths must be a list of repository-relative POSIX paths")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise _invalid("allowed_paths entries must be nonempty strings")
        if CONTROL_CHAR_RE.search(item):
            raise _invalid("allowed_paths entry contains a control character")
        if item.startswith("/") or (len(item) > 1 and item[1] == ":"):
            raise _invalid("allowed_paths contains an absolute path")
        if "\\" in item:
            raise _invalid("allowed_paths contains a non-POSIX path")
        if any(segment == ".." for segment in item.split("/")):
            raise _invalid("allowed_paths contains a path that escapes the worktree")
        out.append(item)
    if len(set(out)) != len(out):
        raise _invalid("allowed_paths contains a duplicate")
    return sorted(out)


def validate_assignment(value: object) -> dict:
    """Return the normalised, digestible assignment, or raise ``assignment-invalid``.

    ``source_sha`` must be a full 40-hex commit. That is the whole point of the field: a
    branch name resolves differently at two moments, and a run bound to a moving ref cannot
    be reconciled against what it actually built.
    """
    if not isinstance(value, dict):
        raise _invalid("assignment must be a JSON object")
    unknown = value.keys() - ASSIGNMENT_KEYS
    if unknown:
        raise _invalid("assignment has unknown key(s): " + ", ".join(sorted(unknown)))
    missing = set(ASSIGNMENT_REQUIRED) - value.keys()
    if missing:
        raise _invalid("assignment missing required key(s): " + ", ".join(sorted(missing)))

    normalised: dict[str, object] = {}
    for field in ("task_id", "project_id"):
        raw = value[field]
        if not isinstance(raw, str) or not TASK_ID_RE.fullmatch(raw):
            raise _invalid(f"{field} must match ^[a-z0-9][a-z0-9._-]{{2,63}}$")
        normalised[field] = raw
    for field in ("engine", "provider", "capacity_pool", "host", "sandbox_profile"):
        raw = value[field]
        if not isinstance(raw, str) or not SLUG_RE.fullmatch(raw):
            raise _invalid(f"{field} must match ^[a-z][a-z0-9-]{{1,63}}$")
        normalised[field] = raw

    normalised["source_repository"] = validate_repository_url(
        value["source_repository"], "source_repository")
    normalised["source_branch"] = validate_branch_name(value["source_branch"], "source_branch")

    sha = value["source_sha"]
    if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
        raise _invalid("source_sha must be exactly 40 lowercase hex characters; an "
                       "abbreviated sha, a branch name, a tag, or HEAD is refused")
    normalised["source_sha"] = sha

    policy = value["publication_policy"]
    if not isinstance(policy, str) or policy not in PUBLICATION_POLICIES:
        raise _invalid("publication_policy must be one of "
                       + ", ".join(sorted(PUBLICATION_POLICIES)))
    normalised["publication_policy"] = policy

    created_at = value["created_at"]
    if not isinstance(created_at, str) or not ISO_UTC_RE.fullmatch(created_at):
        raise _invalid("created_at must be an ISO-8601 UTC timestamp (YYYY-MM-DDTHH:MM:SSZ)")
    normalised["created_at"] = created_at

    for field, default in ASSIGNMENT_OPTIONAL.items():
        raw = value.get(field, default)
        if field in ("seed_manifest_digest", "gate_digest"):
            if not isinstance(raw, str) or (raw and not DIGEST_RE.fullmatch(raw)):
                raise _invalid(f"{field} must be empty or 64 lowercase hex characters")
            normalised[field] = raw
        elif field == "model":
            if not isinstance(raw, str) or (raw and not MODEL_RE.fullmatch(raw)):
                raise _invalid("model must be empty or a plain model identifier")
            normalised[field] = raw
        elif field == "model_parameters":
            if not isinstance(raw, dict):
                raise _invalid("model_parameters must be an object")
            for key, item in raw.items():
                if not isinstance(key, str) or not key:
                    raise _invalid("model_parameters keys must be nonempty strings")
                if not isinstance(item, (str, int, float, bool)):
                    raise _invalid(f"model_parameters.{key} must be a string, number or "
                                   "boolean; nested structures are not part of the digest "
                                   "contract")
            normalised[field] = dict(raw)
        elif field == "network_profile":
            if not isinstance(raw, str) or (raw and not SLUG_RE.fullmatch(raw)):
                raise _invalid("network_profile must be empty or ^[a-z][a-z0-9-]{1,63}$")
            normalised[field] = raw
        elif field == "allowed_paths":
            normalised[field] = validate_allowed_paths(raw)
        else:  # authorized_repositories
            if not isinstance(raw, list):
                raise _invalid("authorized_repositories must be a list")
            repos: list[dict[str, str]] = []
            seen: set[str] = set()
            for item in raw:
                if not isinstance(item, dict) or set(item) != {
                        "repository", "source_branch", "source_sha"}:
                    raise _invalid("authorized_repositories entries must contain exactly "
                                   "repository, source_branch and source_sha")
                repository = validate_repository_url(
                    item["repository"], "authorized_repositories.repository")
                source_branch = validate_branch_name(
                    item["source_branch"], "authorized_repositories.source_branch")
                source_sha = item["source_sha"]
                if not isinstance(source_sha, str) or not SHA_RE.fullmatch(source_sha):
                    raise _invalid("authorized_repositories.source_sha must be exactly 40 "
                                   "lowercase hex characters")
                if repository in seen:
                    raise _invalid("authorized_repositories contains a duplicate repository")
                seen.add(repository)
                repos.append({"repository": repository, "source_branch": source_branch,
                              "source_sha": source_sha})
            if any(item["repository"] == normalised["source_repository"] for item in repos):
                raise _invalid("authorized_repositories must not duplicate source_repository")
            normalised[field] = sorted(repos, key=lambda item: item["repository"])

    # An assignment is a tracked, transmitted, durably-recorded object. Nothing in it may be
    # a credential, in any field, under any name.
    screen_for_secret_material(normalised, "assignment", code="assignment-invalid")
    return normalised


def assignment_digest(assignment: dict) -> str:
    """sha256 over the canonical normalised assignment.

    Changing ANY assignment field changes this digest, which is what makes it usable as the
    idempotency anchor: a 'retry' that quietly rebound the source, the pool, or the model is
    a different assignment and must not deduplicate against the original.
    """
    return canonical_digest(validate_assignment(assignment))


def assignment_reference(assignment: dict) -> dict:
    """The non-secret subset safe to transmit to a vendor or a supervisory Bot.

    Deliberately excludes sandbox_profile, network_profile and allowed_paths: those describe
    how Recursion contains the work, and an external executor neither needs nor should learn
    the containment shape it is being run under.
    """
    normalised = validate_assignment(assignment)
    return {
        "task_id": normalised["task_id"],
        "project_id": normalised["project_id"],
        "source_repository": normalised["source_repository"],
        "source_branch": normalised["source_branch"],
        "source_sha": normalised["source_sha"],
        "publication_policy": normalised["publication_policy"],
        "authorized_repositories": normalised["authorized_repositories"],
        "assignment_digest": canonical_digest(normalised),
    }
