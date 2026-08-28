#!/usr/bin/env python3
"""Remote execution backend foundation: manifests, transport seam, durable attempts. INERT.

Shared by the Phase 6 (Cursor Cloud) and Phase 7 (Grok Bot) adapters of
docs/plans/recursion-v2-execution-fabric.md. See scripts/remote/README.md for the enablement
chain and docs/plans/remote-execution-adapters.md for the design.

Four things live here, and each exists because BOTH adapters would otherwise grow their own:

  1. **Manifest resolution.** ``scripts/remote/<name>.json`` describes an endpoint, a
     credential REFERENCE, a capacity pool, a lease width, and a publication policy. It
     never holds a secret value. Resolution is fail-closed and mirrors
     scripts/resolve-connector.py exactly: 3 = absent or disabled, 2 = present but invalid,
     0 = resolved.

  2. **The transport seam.** Every byte that would leave this box goes through a
     ``Transport``. Production supplies ``HttpsTransport``; the controls supply a fake. The
     production transport refuses to be constructed unless a third, human-owned flag
     (``RECURSION_REMOTE_LIVE=1``) is set, so no test and no accidental import can open a
     socket.

  3. **Durable attempts.** An attempt record is committed BEFORE any request is sent and
     closed after. That ordering is the whole contract: a process that dies mid-request
     leaves an ``open`` attempt, and an open attempt is a question ("did that land?"), never
     a licence to re-send. Restart recovery finds them; reconciliation closes them against
     independently observed provider state.

  4. **The account-shared lease.** Grok Bots share one account-scoped computer (audit
     2026-08-28); Cursor Cloud runs consume a pool quota rather than Hetzner CPU. Both are
     bounded by a witnessed slot lock, reusing scripts/runtime-state.py's proven
     mkdir/PID-witnessed lock rather than a second implementation.

Nothing here is enabled. Every entry point refuses until a human sets the flags in the box
.env, and the loop never writes them (CLAUDE.md rule 3).
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from jsonl_durable import append_jsonl as durable_append_jsonl, read_jsonl_objects
from remote_assignment import (  # noqa: F401  (re-exported for the adapters)
    EXIT_DEFER,
    EXIT_INVALID,
    EXIT_OK,
    EXIT_REFUSED,
    EXIT_RETRYABLE,
    EXIT_UNAVAILABLE,
    RemoteError,
    SLUG_RE,
    canonical_digest,
    resolve_secret,
    screen_for_secret_material,
    validate_branch_name,
    validate_https_url,
    validate_secret_ref,
)

PROG = "remote-backend"
SCHEMA_VERSION = 1

NAME_RE = re.compile(r"[a-z][a-z0-9-]{1,31}")
BACKEND_KINDS = frozenset({"cursor-cloud", "grok-routine"})
BILLING_BASES = frozenset({"included", "metered", "local"})
CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f\x7f]")
ATTEMPT_ID_RE = re.compile(r"[0-9a-f]{16}-\d{1,3}")
DISPATCH_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{7,63}")

MANIFEST_KEYS = {
    "schema_version",
    "name",
    "kind",
    "description",
    "endpoint",
    "endpoint_ref",
    "credential_ref",
    "signing_key_ref",
    "capacity_pool",
    "host_id",
    "billing_basis",
    "on_demand",
    "timeout_seconds",
    "max_attempts",
    "concurrency_lease",
    "publication",
}
PUBLICATION_KEYS = {
    "default_branch",
    "integration_branch",
    "task_branch_pattern",
    "allowed_result_branch_patterns",
}

ATTEMPT_OPEN = "open"
ATTEMPT_SUCCEEDED = "succeeded"
ATTEMPT_FAILED = "failed"
ATTEMPT_DEFERRED = "deferred"
ATTEMPT_UNRECONCILED = "unreconciled"
ATTEMPT_STATES = frozenset({
    ATTEMPT_OPEN, ATTEMPT_SUCCEEDED, ATTEMPT_FAILED, ATTEMPT_DEFERRED, ATTEMPT_UNRECONCILED,
})


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def now_iso(clock=None) -> str:
    seconds = int(clock() if clock is not None else time.time())
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(seconds))


def is_plain_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


# --- manifests ---------------------------------------------------------------------------

def manifest_dir() -> Path:
    override = os.environ.get("RECURSION_REMOTE_DIR", "").strip()
    if override:
        return Path(override)
    return _SCRIPT_DIR / "remote"


def manifest_path(name: str) -> Path:
    return manifest_dir() / f"{name}.json"


def enabled_env_name(name: str) -> str:
    return "RECURSION_REMOTE_" + name.upper().replace("-", "_") + "_ENABLED"


def _bad(message: str) -> RemoteError:
    return RemoteError("manifest-invalid", message)


def _validate_publication(value: object) -> dict:
    if not isinstance(value, dict):
        raise _bad("publication must be a JSON object")
    missing = PUBLICATION_KEYS - value.keys()
    if missing:
        raise _bad("publication missing key(s): " + ", ".join(sorted(missing)))
    extra = value.keys() - PUBLICATION_KEYS
    if extra:
        raise _bad("publication has unknown key(s): " + ", ".join(sorted(extra)))
    out: dict[str, object] = {}
    for field in ("default_branch", "integration_branch"):
        try:
            out[field] = validate_branch_name(value[field], f"publication.{field}")
        except RemoteError as exc:
            raise _bad(exc.message) from exc
    if out["default_branch"] == out["integration_branch"]:
        raise _bad("publication.integration_branch must differ from default_branch; the "
                   "integration branch is a disposable review artifact, not production")
    pattern = value["task_branch_pattern"]
    if not isinstance(pattern, str) or "<task-id>" not in pattern:
        raise _bad("publication.task_branch_pattern must contain the literal '<task-id>'")
    try:
        validate_branch_name(pattern.replace("<task-id>", "x"), "publication.task_branch_pattern")
    except RemoteError as exc:
        raise _bad(exc.message) from exc
    out["task_branch_pattern"] = pattern
    patterns = value["allowed_result_branch_patterns"]
    if not isinstance(patterns, list) or not patterns:
        raise _bad("publication.allowed_result_branch_patterns must be a nonempty list")
    cleaned: list[str] = []
    for item in patterns:
        if not isinstance(item, str) or not item or CONTROL_CHAR_RE.search(item):
            raise _bad("publication.allowed_result_branch_patterns entries must be nonempty "
                       "strings without control characters")
        if item in ("*", "**", "/*"):
            raise _bad("publication.allowed_result_branch_patterns may not be an unrestricted "
                       "wildcard; an external worker must not be able to return any ref")
        cleaned.append(item)
    if len(set(cleaned)) != len(cleaned):
        raise _bad("publication.allowed_result_branch_patterns contains a duplicate")
    out["allowed_result_branch_patterns"] = cleaned
    return out


def validate_manifest(data: object, name: str) -> dict:
    if not isinstance(data, dict):
        raise _bad("manifest must be a JSON object")
    missing = MANIFEST_KEYS - data.keys()
    if missing:
        raise _bad("manifest missing required key(s): " + ", ".join(sorted(missing)))
    extra = data.keys() - MANIFEST_KEYS
    if extra:
        raise _bad("manifest has unknown key(s): " + ", ".join(sorted(extra)))

    if not is_plain_int(data["schema_version"]) or data["schema_version"] != SCHEMA_VERSION:
        raise _bad(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(data["name"], str) or not NAME_RE.fullmatch(data["name"]):
        raise _bad("name must match ^[a-z][a-z0-9-]{1,31}$")
    if data["name"] != name:
        raise _bad(f"name {data['name']!r} does not match filename stem {name!r}")
    if data["kind"] not in BACKEND_KINDS:
        raise _bad("kind must be one of " + ", ".join(sorted(BACKEND_KINDS)))
    if not isinstance(data["description"], str) or not data["description"]:
        raise _bad("description must be a nonempty string")

    endpoint = data["endpoint"]
    endpoint_ref = data["endpoint_ref"]
    if (endpoint is None) == (endpoint_ref is None):
        raise _bad("exactly one of endpoint / endpoint_ref must be set; the other must be null")
    if endpoint is not None:
        validate_https_url(endpoint, "endpoint", code="manifest-invalid")
    else:
        validate_secret_ref(endpoint_ref, "endpoint_ref")

    validate_secret_ref(data["credential_ref"], "credential_ref")

    signing = data["signing_key_ref"]
    if data["kind"] == "grok-routine":
        if signing is None:
            raise _bad("a grok-routine backend must declare signing_key_ref; an unsigned "
                       "outbound routine call is not authenticated")
        validate_secret_ref(signing, "signing_key_ref")
        if signing == data["credential_ref"]:
            raise _bad("signing_key_ref must differ from credential_ref")
    elif signing is not None:
        raise _bad(f"signing_key_ref must be null for kind {data['kind']!r}")

    for field in ("capacity_pool", "host_id"):
        if not isinstance(data[field], str) or not SLUG_RE.fullmatch(data[field]):
            raise _bad(f"{field} must match ^[a-z][a-z0-9-]{{1,63}}$")
    if data["billing_basis"] not in BILLING_BASES:
        raise _bad("billing_basis must be one of " + ", ".join(sorted(BILLING_BASES)))
    if not isinstance(data["on_demand"], bool):
        raise _bad("on_demand must be a boolean")

    if not is_plain_int(data["timeout_seconds"]) or not (1 <= data["timeout_seconds"] <= 600):
        raise _bad("timeout_seconds must be an integer in 1..600")
    if not is_plain_int(data["max_attempts"]) or not (1 <= data["max_attempts"] <= 10):
        raise _bad("max_attempts must be an integer in 1..10")
    if not is_plain_int(data["concurrency_lease"]) or not (1 <= data["concurrency_lease"] <= 8):
        raise _bad("concurrency_lease must be an integer in 1..8")

    publication = _validate_publication(data["publication"])

    normalised = {
        "schema_version": SCHEMA_VERSION,
        "name": data["name"],
        "kind": data["kind"],
        "description": data["description"],
        "endpoint": endpoint,
        "endpoint_ref": endpoint_ref,
        "credential_ref": data["credential_ref"],
        "signing_key_ref": signing,
        "capacity_pool": data["capacity_pool"],
        "host_id": data["host_id"],
        "billing_basis": data["billing_basis"],
        "on_demand": data["on_demand"],
        "timeout_seconds": data["timeout_seconds"],
        "max_attempts": data["max_attempts"],
        "concurrency_lease": data["concurrency_lease"],
        "publication": publication,
    }
    # A manifest is a tracked file. A value pasted where a reference belongs must fail review
    # by failing validation, not by being noticed. The *_ref keys are exempt from the
    # key-NAME screen (validate_secret_ref already proved each holds a reference), but their
    # values still go through the value screen below.
    screen_for_secret_material(normalised, "manifest", code="manifest-invalid")
    return normalised


def load_manifest(path: Path, name: str) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _bad(f"could not read manifest {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise _bad(f"manifest {path} is not valid JSON: {exc}") from exc
    return validate_manifest(data, name)


def resolve_backend(name: str, kind: str | None = None) -> dict:
    """Name -> validated manifest, or raise. The single authority; adapters import this.

    Enablement is checked AFTER validation, deliberately: a broken manifest must report as
    broken (2), not as absent (3). Otherwise the day a human flips the flags is the day they
    discover the manifest never parsed.
    """
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise RemoteError("request-invalid",
                          f"invalid backend name {name!r}: must match ^[a-z][a-z0-9-]{{1,31}}$")
    path = manifest_path(name)
    if not path.is_file():
        raise RemoteError("manifest-absent", f"manifest not found: {path}")
    data = load_manifest(path, name)
    if kind is not None and data["kind"] != kind:
        raise _bad(f"backend {name!r} is kind {data['kind']!r}, not {kind!r}")
    if os.environ.get("RECURSION_REMOTE_ADAPTERS", "") != "1":
        raise RemoteError("adapter-disabled", "RECURSION_REMOTE_ADAPTERS is not enabled")
    enable_var = enabled_env_name(name)
    if os.environ.get(enable_var, "") != "1":
        raise RemoteError("adapter-disabled", f"{enable_var} is not enabled")
    # Metered/on-demand spend is a human policy decision, never a consequence of a manifest
    # edit. Same rule as the hermes/metered engine path (D-015 principle 2).
    if (data["billing_basis"] == "metered" or data["on_demand"]) \
            and os.environ.get("RECURSION_ALLOW_METERED", "") != "1":
        raise RemoteError("adapter-disabled",
                          f"backend {name!r} is metered or on-demand and "
                          "RECURSION_ALLOW_METERED is not set")
    return data


def backend_endpoint(manifest: dict) -> str:
    """The base URL, resolving endpoint_ref from env when the URL is itself human-owned.

    A Grok routine webhook URL is a bearer-grade secret (anyone holding it can post to the
    routine), so it lives in .env behind a reference. A Cursor Cloud base URL is public and
    sits in the manifest.
    """
    if manifest["endpoint"] is not None:
        return manifest["endpoint"]
    env_name = validate_secret_ref(manifest["endpoint_ref"], "endpoint_ref")
    value = resolve_secret(env_name, "endpoint_ref")
    try:
        validate_https_url(value, "endpoint_ref value", allow_query=True)
    except RemoteError as exc:
        # The message deliberately does not echo the value: this URL is bearer-grade.
        raise RemoteError("credential-absent",
                          f"the value of {env_name} is not a well-formed https URL "
                          "(value withheld)") from exc
    return value


# --- transport seam ----------------------------------------------------------------------

class TransportResponse:
    __slots__ = ("status", "headers", "body")

    def __init__(self, status: int, headers: dict | None, body: bytes) -> None:
        self.status = int(status)
        self.headers = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
        self.body = bytes(body)

    def json(self) -> dict:
        try:
            value = json.loads(self.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RemoteError("malformed-response",
                              f"response body is not valid UTF-8 JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise RemoteError("malformed-response", "response body is not a JSON object")
        return value


class Transport:
    """The only path to the network. Adapters take one; controls pass a fake."""

    def request(self, method: str, url: str, headers: dict, body: bytes | None,
                timeout: int) -> TransportResponse:
        raise NotImplementedError

    def stream_lines(self, method: str, url: str, headers: dict, body: bytes | None,
                     timeout: int):
        """Yield decoded text lines. Default: no streaming capability."""
        raise RemoteError("request-invalid",
                          "this transport does not implement streaming")


class RefusingTransport(Transport):
    """The default. Present so an adapter constructed without a transport fails loudly
    rather than silently acquiring one."""

    def request(self, method: str, url: str, headers: dict, body: bytes | None,
                timeout: int) -> TransportResponse:
        raise RemoteError("live-transport-disabled",
                          "no transport was supplied; this adapter performs no network I/O "
                          "of its own")

    def stream_lines(self, method: str, url: str, headers: dict, body: bytes | None,
                     timeout: int):
        raise RemoteError("live-transport-disabled",
                          "no transport was supplied; this adapter performs no network I/O "
                          "of its own")


class HttpsTransport(Transport):
    """Production transport. Triple-gated and never constructed by any control.

    ``RECURSION_REMOTE_LIVE=1`` is a third human-owned flag on top of the adapter flags. Its
    only job is to make "this session cannot reach the internet" a structural property of the
    code rather than a claim in a test file: the controls assert that constructing this class
    without the flag raises, so a regression that started opening sockets would fail the
    suite instead of quietly succeeding.
    """

    def __init__(self, *, user_agent: str = "recursion-remote-adapter/1") -> None:
        if os.environ.get("RECURSION_REMOTE_LIVE", "") != "1":
            raise RemoteError("live-transport-disabled",
                              "RECURSION_REMOTE_LIVE is not set; the live transport refuses "
                              "to be constructed")
        self.user_agent = user_agent

    def _open(self, method: str, url: str, headers: dict, body: bytes | None, timeout: int):
        import urllib.error
        import urllib.request

        if not url.startswith("https://"):
            raise RemoteError("request-invalid", "the live transport speaks https only")
        request = urllib.request.Request(url=url, data=body, method=method.upper())
        request.add_header("User-Agent", self.user_agent)
        for key, value in headers.items():
            request.add_header(str(key), str(value))
        try:
            return urllib.request.urlopen(request, timeout=timeout)  # noqa: S310 (https enforced)
        except urllib.error.HTTPError as exc:
            return exc
        except TimeoutError as exc:
            raise RemoteError("transport-timeout", f"request timed out after {timeout}s") from exc
        except urllib.error.URLError as exc:
            raise RemoteError("transport-error", f"transport failure: {exc.reason}") from exc
        except OSError as exc:
            raise RemoteError("transport-error", f"transport failure: {exc}") from exc

    def request(self, method: str, url: str, headers: dict, body: bytes | None,
                timeout: int) -> TransportResponse:
        handle = self._open(method, url, headers, body, timeout)
        with contextlib.closing(handle):
            payload = handle.read()
            status = getattr(handle, "status", None) or handle.getcode()
            return TransportResponse(status, dict(handle.headers.items()), payload)

    def stream_lines(self, method: str, url: str, headers: dict, body: bytes | None,
                     timeout: int):
        handle = self._open(method, url, headers, body, timeout)
        with contextlib.closing(handle):
            for raw in handle:
                yield raw.decode("utf-8", errors="replace").rstrip("\r\n")


def classify_status(status: int, body: bytes) -> None:
    """Map an HTTP status onto the typed taxonomy. 2xx returns; everything else raises.

    429 and 402 are separated on purpose: a rate limit is retryable at the same cost, while
    a quota/payment refusal is a DEFER. Quota exhaustion must never become an argument for
    spending money -- that is Lucas's decision and lives in .env, not in an error handler
    (plan invariant 8).
    """
    if 200 <= status < 300:
        return
    snippet = body[:200].decode("utf-8", errors="replace")
    if status in (401, 403):
        raise RemoteError("auth-failed",
                          f"provider rejected the credential (HTTP {status}); a human "
                          "re-authorises through the credential window")
    if status == 404:
        raise RemoteError("not-found", f"provider returned HTTP 404: {snippet}")
    if status == 402:
        raise RemoteError("quota-exhausted",
                          f"provider reports the pool is exhausted (HTTP 402): {snippet}")
    if status == 429:
        raise RemoteError("rate-limited", f"provider rate limited the request: {snippet}")
    if status == 503:
        raise RemoteError("provider-unavailable",
                          f"provider is unavailable (HTTP 503): {snippet}")
    if 500 <= status < 600:
        raise RemoteError("provider-error", f"provider error HTTP {status}: {snippet}")
    raise RemoteError("request-invalid", f"provider rejected the request HTTP {status}: {snippet}")


# --- PAUSE -------------------------------------------------------------------------------

def pause_path(base: Path) -> Path:
    return Path(base) / "state" / "PAUSE"


def is_paused(base: Path) -> bool:
    return pause_path(base).is_file()


def assert_not_paused(base: Path, operation: str) -> None:
    """PAUSE halts every external effect and preserves local awareness (CONTROL_PLANE.md).

    Callers that only read durable local records must NOT call this: a paused box that cannot
    tell you what it was doing is a failure, not a safety feature.
    """
    if is_paused(base):
        raise RemoteError("paused",
                          f"state/PAUSE is present; refusing {operation}. Local awareness "
                          "operations remain available.")


# --- the account-shared concurrency lease -------------------------------------------------

_RUNTIME_STATE_PATH = _SCRIPT_DIR / "runtime-state.py"
_runtime_state_module = None


def _runtime_state():
    """Load scripts/runtime-state.py by path (its filename is not an identifier)."""
    global _runtime_state_module
    if _runtime_state_module is None:
        spec = importlib.util.spec_from_file_location(
            "recursion_runtime_state", _RUNTIME_STATE_PATH)
        if spec is None or spec.loader is None:
            raise RemoteError("request-invalid",
                              f"runtime-state module is missing: {_RUNTIME_STATE_PATH}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _runtime_state_module = module
    return _runtime_state_module


class AccountLease:
    """One witnessed slot lock per concurrent remote run, keyed by capacity pool.

    Grok Bot's boundary is the reason this is keyed by POOL and not by task: every Bot on the
    account shares one computer, one filesystem and one set of logins, so two "parallel" Bots
    editing code are one writer with two screens. Cursor Cloud uses the same mechanism for a
    different reason -- to keep vendor runs inside the pool's measured concurrency.

    Exhaustion raises ``lease-unavailable``, which is a DEFER (exit 75). The task stays
    queued. It is not a failure and it never escalates.
    """

    def __init__(self, base: Path, pool_id: str, slots: int) -> None:
        if not SLUG_RE.fullmatch(pool_id):
            raise RemoteError("request-invalid", "lease pool id must match ^[a-z][a-z0-9-]{1,63}$")
        if not is_plain_int(slots) or not (1 <= slots <= 8):
            raise RemoteError("request-invalid", "lease slots must be an integer in 1..8")
        self.base = Path(base)
        self.pool_id = pool_id
        self.slots = slots
        self.path: Path | None = None
        self.slot: int | None = None

    def _lock_dir(self) -> Path:
        return self.base / "state" / ".locks"

    def __enter__(self) -> "AccountLease":
        runtime = _runtime_state()
        self._lock_dir().mkdir(parents=True, exist_ok=True)
        # The shared acquire retries for ~10s by default, which is right for a maintenance
        # mutex and wrong for probing N slots. One attempt per slot, then defer.
        previous = {name: os.environ.get(name)
                    for name in ("RECURSION_LOCK_ATTEMPTS", "RECURSION_LOCK_DELAY_S")}
        os.environ["RECURSION_LOCK_ATTEMPTS"] = "1"
        os.environ["RECURSION_LOCK_DELAY_S"] = "0"
        try:
            for slot in range(self.slots):
                candidate = self._lock_dir() / f"remote-{self.pool_id}-slot-{slot}.lock"
                try:
                    runtime.acquire_witnessed_directory_lock(
                        candidate, f"remote-{self.pool_id}-slot-{slot}", os.getpid())
                except (RuntimeError, OSError):
                    # A contended slot and an unusable one both mean "not this slot". The loop
                    # ends in a DEFER, so failing to take a lease is never a crash.
                    continue
                self.path = candidate
                self.slot = slot
                return self
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
        raise RemoteError("lease-unavailable",
                          f"all {self.slots} slot(s) of capacity pool {self.pool_id!r} are "
                          "held; deferring")

    def __exit__(self, *_: object) -> None:
        if self.path is None:
            return
        runtime = _runtime_state()
        with contextlib.suppress(RuntimeError, OSError):
            runtime.release_witnessed_directory_lock(
                self.path, f"remote-{self.pool_id}-slot-{self.slot}", os.getpid())
        self.path = None
        self.slot = None


# --- durable attempts ---------------------------------------------------------------------

def remote_root(base: Path, backend: str) -> Path:
    return Path(base) / "state" / "remote" / backend


def attempts_journal(base: Path, backend: str) -> Path:
    return remote_root(base, backend) / "attempts.jsonl"


def attempt_projection(base: Path, backend: str, attempt_id: str) -> Path:
    return remote_root(base, backend) / "attempts" / f"{attempt_id}.json"


def session_path(base: Path, backend: str, dispatch_id: str) -> Path:
    return remote_root(base, backend) / "sessions" / f"{dispatch_id}.json"


def idempotency_key(backend: str, operation: str, assignment_digest: str,
                    dispatch_id: str, request_digest: str) -> str:
    """The dedup anchor.

    Includes ``request_digest`` so that "the same dispatch with a different body" is a
    different key rather than a silent replay of the first body. Includes
    ``assignment_digest`` so that a retry which rebound the source, pool or model cannot
    deduplicate against the original run.
    """
    return canonical_digest({
        "backend": backend,
        "operation": operation,
        "assignment_digest": assignment_digest,
        "dispatch_id": dispatch_id,
        "request_digest": request_digest,
    })


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".remote-", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, str(path))
    except BaseException:
        with contextlib.suppress(OSError):
            os.remove(tmp_name)
        raise


def read_attempts(base: Path, backend: str) -> list[dict]:
    path = attempts_journal(base, backend)
    if not path.is_file():
        return []
    return [row for row in read_jsonl_objects(path) if isinstance(row, dict)]


def _commit_attempt(base: Path, backend: str, body: dict) -> dict:
    """Journal first (durable, content-addressed, deduped), then project.

    ``record_id`` is the digest of the record's own content, so a crash between the append
    and the projection is repaired by simply repeating the call: the second append
    deduplicates against the first instead of doubling the row.
    """
    record = {key: value for key, value in body.items() if key != "record_id"}
    screen_for_secret_material(record, "attempt")
    record["record_id"] = canonical_digest(record)
    durable_append_jsonl(attempts_journal(base, backend), record,
                         dedupe_field="record_id", dedupe_value=record["record_id"])
    atomic_json(attempt_projection(base, backend, record["attempt_id"]), record)
    return record


def latest_states(rows: list[dict]) -> dict[str, dict]:
    """Fold the append-only journal into the current state of each attempt."""
    folded: dict[str, dict] = {}
    for row in rows:
        attempt_id = row.get("attempt_id")
        if isinstance(attempt_id, str):
            folded[attempt_id] = row
    return folded


class AttemptHandle:
    """A durable, committed intent to perform one remote operation.

    ``replayed`` means a prior attempt with this exact idempotency key already succeeded:
    the caller must return the stored result and send nothing.
    ``unreconciled`` means a prior attempt with this key is still ``open`` -- a process died
    between commit and close. The caller must reconcile it against independently observed
    provider state before another send is permitted.
    """

    __slots__ = ("base", "backend", "record", "replayed", "unreconciled", "closed")

    def __init__(self, base: Path, backend: str, record: dict, *, replayed: bool = False,
                 unreconciled: bool = False) -> None:
        self.base = Path(base)
        self.backend = backend
        self.record = record
        self.replayed = replayed
        self.unreconciled = unreconciled
        self.closed = replayed or unreconciled

    @property
    def attempt_id(self) -> str:
        return self.record["attempt_id"]

    def _close(self, state: str, outcome: str, detail: dict | None, clock=None) -> dict:
        if state not in ATTEMPT_STATES:
            raise RemoteError("request-invalid", f"unknown attempt state {state!r}")
        if self.closed:
            raise RemoteError("request-invalid",
                              f"attempt {self.attempt_id} is already closed")
        closed_at = now_iso(clock)
        body = dict(self.record)
        body.update({
            "state": state,
            "outcome": outcome,
            "detail": dict(detail or {}),
            "closed_at": closed_at,
            "updated_at": closed_at,
        })
        self.record = _commit_attempt(self.base, self.backend, body)
        self.closed = True
        return self.record

    def succeed(self, outcome: str = "ok", detail: dict | None = None, clock=None) -> dict:
        return self._close(ATTEMPT_SUCCEEDED, outcome, detail, clock)

    def fail(self, error: RemoteError, clock=None) -> dict:
        return self._close(ATTEMPT_FAILED, error.code, error.as_record(), clock)

    def defer(self, error: RemoteError, clock=None) -> dict:
        return self._close(ATTEMPT_DEFERRED, error.code, error.as_record(), clock)


def begin_attempt(base: Path, backend: str, *, dispatch_id: str, operation: str,
                  assignment_digest: str, request_digest: str, max_attempts: int,
                  clock=None) -> AttemptHandle:
    """Commit the intent BEFORE any I/O, and refuse to re-send what may already have landed."""
    if not DISPATCH_ID_RE.fullmatch(dispatch_id or ""):
        raise RemoteError("request-invalid",
                          "dispatch_id must match ^[a-z0-9][a-z0-9-]{7,63}$")
    key = idempotency_key(backend, operation, assignment_digest, dispatch_id, request_digest)
    rows = read_attempts(base, backend)
    mine = [row for row in latest_states(rows).values() if row.get("idempotency_key") == key]

    for row in mine:
        if row.get("state") == ATTEMPT_SUCCEEDED:
            return AttemptHandle(base, backend, row, replayed=True)
    for row in mine:
        if row.get("state") == ATTEMPT_OPEN:
            return AttemptHandle(base, backend, row, unreconciled=True)

    attempt_number = len(mine) + 1
    if attempt_number > max_attempts:
        raise RemoteError("attempts-exhausted",
                          f"{operation} for dispatch {dispatch_id} has used its "
                          f"{max_attempts} permitted attempt(s)")
    opened_at = now_iso(clock)
    attempt_id = f"{key[:16]}-{attempt_number}"
    body = {
        "schema_version": SCHEMA_VERSION,
        "attempt_id": attempt_id,
        "idempotency_key": key,
        "backend": backend,
        "operation": operation,
        "dispatch_id": dispatch_id,
        "assignment_digest": assignment_digest,
        "request_digest": request_digest,
        "attempt_number": attempt_number,
        "max_attempts": max_attempts,
        "state": ATTEMPT_OPEN,
        "outcome": "",
        "detail": {},
        "opened_at": opened_at,
        "closed_at": "",
        "updated_at": opened_at,
    }
    return AttemptHandle(base, backend, _commit_attempt(base, backend, body))


def open_attempts(base: Path, backend: str) -> list[dict]:
    """Restart recovery, awareness half: what was in flight when the controller died.

    Pure local read -- available under PAUSE.
    """
    return sorted((row for row in latest_states(read_attempts(base, backend)).values()
                   if row.get("state") == ATTEMPT_OPEN),
                  key=lambda row: (row.get("opened_at", ""), row.get("attempt_id", "")))


def reconcile_attempt(base: Path, backend: str, attempt_id: str, *, observed: str,
                      observer: str, detail: dict | None = None, clock=None) -> dict:
    """Close an open attempt against independently observed provider state.

    ``observed`` is one of ``landed`` / ``not-landed`` / ``unknown``. ``unknown`` does NOT
    reopen the attempt for re-sending: it moves to ``unreconciled``, which is a terminal
    state requiring a human. Guessing here is exactly how a duplicate dispatch happens.
    """
    if observed not in ("landed", "not-landed", "unknown"):
        raise RemoteError("request-invalid",
                          "observed must be landed, not-landed, or unknown")
    if not isinstance(observer, str) or not observer.strip():
        raise RemoteError("request-invalid", "reconciliation must record who observed it")
    if not ATTEMPT_ID_RE.fullmatch(attempt_id or ""):
        raise RemoteError("request-invalid",
                          "attempt_id must match ^[0-9a-f]{16}-[0-9]{1,3}$")
    rows = latest_states(read_attempts(base, backend))
    record = rows.get(attempt_id)
    if record is None:
        raise RemoteError("not-found", f"no attempt {attempt_id} for backend {backend}")
    if record.get("state") != ATTEMPT_OPEN:
        raise RemoteError("request-invalid",
                          f"attempt {attempt_id} is {record.get('state')!r}, not open")
    state = {
        "landed": ATTEMPT_SUCCEEDED,
        "not-landed": ATTEMPT_FAILED,
        "unknown": ATTEMPT_UNRECONCILED,
    }[observed]
    closed_at = now_iso(clock)
    body = dict(record)
    body.update({
        "state": state,
        "outcome": f"reconciled:{observed}",
        "detail": {"observer": observer, "observed": observed, **dict(detail or {})},
        "closed_at": closed_at,
        "updated_at": closed_at,
    })
    return _commit_attempt(base, backend, body)


def write_session(base: Path, backend: str, dispatch_id: str, record: dict) -> Path:
    if not DISPATCH_ID_RE.fullmatch(dispatch_id or ""):
        raise RemoteError("request-invalid", "dispatch_id must match ^[a-z0-9][a-z0-9-]{7,63}$")
    screen_for_secret_material(record, "session")
    path = session_path(base, backend, dispatch_id)
    atomic_json(path, record)
    return path


def read_session(base: Path, backend: str, dispatch_id: str) -> dict:
    path = session_path(base, backend, dispatch_id)
    if not path.is_file():
        raise RemoteError("not-found", f"no session record for dispatch {dispatch_id}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RemoteError("malformed-response", f"session record is unreadable: {exc}") from exc
    if not isinstance(value, dict):
        raise RemoteError("malformed-response", "session record is not a JSON object")
    return value


def list_sessions(base: Path, backend: str) -> list[dict]:
    directory = remote_root(base, backend) / "sessions"
    if not directory.is_dir():
        return []
    out: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        with contextlib.suppress(OSError, json.JSONDecodeError):
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                out.append(value)
    return out


# --- CLI: validation only ------------------------------------------------------------------

def validate_directory() -> int:
    directory = manifest_dir()
    if not directory.is_dir():
        diag(f"remote backend directory not found: {directory}")
        return EXIT_UNAVAILABLE
    paths = sorted(directory.glob("*.json"))
    invalid = 0
    for path in paths:
        stem = path.name[: -len(".json")]
        if not NAME_RE.fullmatch(stem):
            diag(f"{path.name}: filename stem must match ^[a-z][a-z0-9-]{{1,31}}$")
            invalid += 1
            continue
        try:
            load_manifest(path, stem)
        except RemoteError as exc:
            diag(f"{path.name}: {exc.message}")
            invalid += 1
    if invalid:
        diag(f"{invalid} of {len(paths)} manifest(s) invalid in {directory}")
        return EXIT_INVALID
    diag(f"{len(paths)} manifest(s) valid in {directory}")
    return EXIT_OK


def main() -> int:
    parser = argparse.ArgumentParser(prog=PROG, description=__doc__.splitlines()[0])
    parser.add_argument("--validate", action="store_true",
                        help="validate every manifest in the remote backend directory")
    args = parser.parse_args()
    if not args.validate:
        diag("this module has no runtime entry point; use --validate, or import it from an "
             "adapter (scripts/cursor-cloud-adapter.py, scripts/grok-bot-dispatcher.py)")
        return EXIT_INVALID
    return validate_directory()


if __name__ == "__main__":
    raise SystemExit(main())
