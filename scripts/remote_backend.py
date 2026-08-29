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
import socket
import stat
import sys
import tempfile
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from jsonl_durable import (
    _win_close_lock_parent_pins,
    _win_pin_lock_parent,
    _win_validate_lock_parent_pins,
    append_jsonl as durable_append_jsonl,
    read_jsonl_objects,
)
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
    validate_branch_pattern,
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
# A response or exception in this set does not prove that the provider did not accept a
# mutating request.  The attempt therefore remains OPEN for reconciliation; closing it as a
# retryable failure would authorize a duplicate create.
AMBIGUOUS_MUTATION_ERRORS = frozenset({
    "transport-error", "transport-timeout", "provider-error", "provider-unavailable",
    "rate-limited", "malformed-response",
})


def _lstat(path: Path):
    try:
        return path.lstat()
    except FileNotFoundError:
        return None


def _lexical_absolute(path: Path) -> Path:
    """Make a path absolute without following a symlink or reparse point."""
    path = Path(path)
    return path if path.is_absolute() else Path.cwd() / path


def _same_identity(left: os.stat_result, right: os.stat_result) -> bool:
    return (int(left.st_dev), int(left.st_ino)) == (int(right.st_dev), int(right.st_ino))


def _relative_directory_open_supported() -> bool:
    supported = getattr(os, "supports_dir_fd", set())
    return os.open in supported and os.stat in supported


def _directory_open_flags() -> int:
    return (os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0))


def _directory_create_mode() -> int:
    # The mode argument is an ACL request on this Windows host; 0o700 creates a directory
    # that even its creating process cannot reopen.  POSIX keeps the least-privilege mode.
    return 0o777 if os.name == "nt" else 0o700


def _verify_directory_descriptor(descriptor: int) -> os.stat_result:
    try:
        info = os.fstat(descriptor)
    except OSError:
        raise RemoteError("request-invalid", "unsafe runtime storage directory") from None
    if not stat.S_ISDIR(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400):
        raise RemoteError("request-invalid", "unsafe runtime storage directory")
    return info


class _PinnedDirectory:
    """Hold every parent component open and authenticate its current pathname entry."""

    def __init__(self, path: Path, *, create: bool = True) -> None:
        self.path = _lexical_absolute(path)
        self.create = create
        self.descriptor: int | None = None
        self._fds: list[int] = []
        self._components: list[tuple[int, str, int, tuple[int, int]]] = []
        self._relative = _relative_directory_open_supported()

    def __enter__(self) -> "_PinnedDirectory":
        try:
            if self._relative:
                current = os.open(self.path.anchor, _directory_open_flags())
                self._fds.append(current)
                for name in self.path.parts[1:]:
                    try:
                        child = os.open(name, _directory_open_flags(), dir_fd=current)
                    except FileNotFoundError:
                        if not self.create:
                            raise RemoteError(
                                "not-found", "runtime storage directory is absent"
                            ) from None
                        created = False
                        try:
                            os.mkdir(name, _directory_create_mode(), dir_fd=current)
                            created = True
                        except FileExistsError:
                            pass
                        if created and os.name != "nt":
                            os.fsync(current)
                        child = os.open(name, _directory_open_flags(), dir_fd=current)
                    child_info = _verify_directory_descriptor(child)
                    entry_info = os.stat(name, dir_fd=current, follow_symlinks=False)
                    if not _same_identity(child_info, entry_info):
                        os.close(child)
                        raise RemoteError(
                            "request-invalid", "runtime storage directory changed while opening"
                        )
                    self._components.append(
                        (current, name, child, (int(child_info.st_dev), int(child_info.st_ino)))
                    )
                    self._fds.append(child)
                    current = child
                self.descriptor = current
            else:
                current = Path(self.path.anchor)
                for name in self.path.parts[1:]:
                    current /= name
                    info = _lstat(current)
                    if info is None:
                        if not self.create:
                            raise RemoteError(
                                "not-found", "runtime storage directory is absent"
                            )
                        try:
                            current.mkdir(mode=_directory_create_mode())
                        except FileExistsError:
                            pass
                        info = _lstat(current)
                    if info is None or _is_link_or_reparse(current, info) \
                            or not stat.S_ISDIR(info.st_mode):
                        raise RemoteError("request-invalid", "unsafe runtime storage directory")
            self.verify()
            return self
        except BaseException as exc:
            self.close()
            if isinstance(exc, RemoteError):
                raise
            raise RemoteError("request-invalid", "unsafe runtime storage directory") from None

    def __exit__(self, *_: object) -> bool:
        self.close()
        return False

    def verify(self) -> None:
        if self._relative:
            assert self.descriptor is not None
            for parent, name, child, identity in self._components:
                child_info = _verify_directory_descriptor(child)
                try:
                    entry_info = os.stat(name, dir_fd=parent, follow_symlinks=False)
                except OSError:
                    raise RemoteError(
                        "request-invalid", "runtime storage directory changed after opening"
                    ) from None
                if (int(child_info.st_dev), int(child_info.st_ino)) != identity \
                        or not _same_identity(child_info, entry_info):
                    raise RemoteError(
                        "request-invalid", "runtime storage directory changed after opening"
                    )
            _verify_directory_descriptor(self.descriptor)
            return
        current = Path(self.path.anchor)
        for name in self.path.parts[1:]:
            current /= name
            info = _lstat(current)
            if info is None or _is_link_or_reparse(current, info) \
                    or not stat.S_ISDIR(info.st_mode):
                raise RemoteError(
                    "request-invalid", "runtime storage directory changed after opening"
                )

    def open_leaf(self, name: str, flags: int, mode: int = 0o600) -> int:
        self.verify()
        try:
            if self._relative:
                assert self.descriptor is not None
                return os.open(name, flags, mode, dir_fd=self.descriptor)
            return os.open(self.path / name, flags, mode)
        except OSError:
            raise RemoteError("request-invalid", "unsafe runtime storage file") from None

    def leaf_stat(self, name: str) -> os.stat_result | None:
        try:
            if self._relative:
                assert self.descriptor is not None
                return os.stat(name, dir_fd=self.descriptor, follow_symlinks=False)
            return (self.path / name).lstat()
        except FileNotFoundError:
            return None
        except OSError:
            raise RemoteError("request-invalid", "unsafe runtime storage file") from None

    def fsync(self) -> None:
        if os.name != "nt" and self.descriptor is not None:
            os.fsync(self.descriptor)

    def close(self) -> None:
        for descriptor in reversed(self._fds):
            try:
                os.close(descriptor)
            except OSError:
                pass
        self._fds.clear()
        self.descriptor = None


def _is_link_or_reparse(path: Path, stat_result) -> bool:
    if stat.S_ISLNK(stat_result.st_mode) or path.is_symlink():
        return True
    # Windows junctions are reparse points but pathlib does not report them as symlinks.
    return bool(getattr(stat_result, "st_file_attributes", 0) & 0x400)


def _safe_directory(path: Path) -> Path:
    """Create/check a directory one component at a time without following links."""
    with _PinnedDirectory(path):
        return _lexical_absolute(path)


def _pinned_directory_child(parent: _PinnedDirectory, name: str) -> Path:
    """Address a child through a retained POSIX directory descriptor."""
    if (os.name != "nt" and parent._relative and parent.descriptor is not None
            and Path("/proc/self/fd").is_dir()):
        return Path("/proc/self/fd") / str(parent.descriptor) / name
    return parent.path / name


def _safe_file(path: Path, *, create_parent: bool = True) -> Path:
    path = Path(path)
    with _PinnedDirectory(path.parent, create=create_parent) as parent:
        stat_result = parent.leaf_stat(path.name)
        if stat_result is not None and (
                _is_link_or_reparse(path, stat_result)
                or not stat.S_ISREG(stat_result.st_mode)
                or int(getattr(stat_result, "st_nlink", 1)) != 1):
            raise RemoteError("request-invalid", "unsafe runtime storage file")
    return path


def _safe_existing_lock(path: Path) -> None:
    stat_result = _lstat(path)
    if stat_result is not None and (
            _is_link_or_reparse(path, stat_result) or not path.is_dir()):
        raise RemoteError("request-invalid", "unsafe runtime lock path")


def _fsync_directory(path: Path, descriptor: int | None = None) -> None:
    if os.name == "nt":
        return
    close_descriptor = descriptor is None
    if descriptor is None:
        descriptor = os.open(str(path), _directory_open_flags())
    try:
        os.fsync(descriptor)
    finally:
        if close_descriptor:
            os.close(descriptor)


def _before_remote_leaf_open(_path: Path) -> None:
    """Test seam for the check-to-open window; production has no side effect."""


def _before_remote_leaf_remove(_path: Path) -> None:
    """Test seam for the checked PAUSE removal window; production has no side effect."""


def _before_remote_leaf_replace(_path: Path) -> None:
    """Test seam for the checked-parent-to-replace window; production has no side effect."""


def _verify_runtime_leaf(parent: _PinnedDirectory, name: str,
                         descriptor: int | None = None) -> os.stat_result | None:
    parent.verify()
    info = parent.leaf_stat(name)
    if info is None:
        return None
    if (_is_link_or_reparse(parent.path / name, info)
            or not stat.S_ISREG(info.st_mode)
            or int(getattr(info, "st_nlink", 1)) != 1):
        raise RemoteError("request-invalid", "unsafe runtime storage file")
    if descriptor is not None:
        try:
            opened = os.fstat(descriptor)
        except OSError:
            raise RemoteError("request-invalid", "runtime storage file changed after opening") from None
        if not _same_identity(info, opened):
            raise RemoteError("request-invalid", "runtime storage file changed after opening")
    return info


def _open_runtime_leaf(parent: _PinnedDirectory, path: Path, flags: int,
                       mode: int = 0o600,
                       expected: os.stat_result | None = None) -> tuple[int, os.stat_result]:
    parent.verify()
    _before_remote_leaf_open(path)
    descriptor = parent.open_leaf(path.name, flags, mode)
    try:
        info = _verify_runtime_leaf(parent, path.name, descriptor)
        if info is None:
            raise RemoteError("request-invalid", "runtime storage file disappeared after opening")
        if expected is not None and not _same_identity(expected, info):
            raise RemoteError("request-invalid", "runtime storage file changed before opening")
        parent.verify()
        return descriptor, info
    except BaseException:
        os.close(descriptor)
        raise


def _create_relative_temp(parent: _PinnedDirectory, prefix: str) -> tuple[int, str]:
    if not parent._relative:
        try:
            descriptor, name = tempfile.mkstemp(prefix=prefix, dir=str(parent.path))
        except OSError:
            raise RemoteError("request-invalid", "runtime temporary file could not be created") from None
        return descriptor, Path(name).name
    assert parent.descriptor is not None
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    generator = getattr(tempfile, "_get_candidate_names")()
    for _attempt in range(100):
        name = prefix + next(generator)
        try:
            return os.open(name, flags, 0o600, dir_fd=parent.descriptor), name
        except FileExistsError:
            continue
        except OSError:
            break
    raise RemoteError("request-invalid", "runtime temporary file could not be created")


def _replace_relative(parent: _PinnedDirectory, temporary: str, target: str,
                      path: Path | None = None,
                      expected: os.stat_result | None = None) -> None:
    parent.verify()
    if path is not None:
        _before_remote_leaf_replace(path)
        parent.verify()
    current = parent.leaf_stat(target)
    if expected is None:
        if current is not None:
            raise RemoteError("request-invalid", "runtime storage file changed before replacement")
    elif current is None or not _same_identity(expected, current):
        raise RemoteError("request-invalid", "runtime storage file changed before replacement")
    try:
        if parent._relative:
            assert parent.descriptor is not None
            os.replace(temporary, target, src_dir_fd=parent.descriptor, dst_dir_fd=parent.descriptor)
        else:
            os.replace(parent.path / temporary, parent.path / target)
    except OSError:
        raise RemoteError("request-invalid", "runtime durable replacement could not be completed") from None
    parent.verify()


def _unlink_relative(parent: _PinnedDirectory, name: str) -> None:
    try:
        if parent._relative:
            assert parent.descriptor is not None
            os.unlink(name, dir_fd=parent.descriptor)
        else:
            os.unlink(parent.path / name)
    except FileNotFoundError:
        return
    except OSError:
        raise RemoteError("request-invalid", "runtime temporary file cleanup failed") from None


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
        try:
            validate_branch_pattern(item, "publication.allowed_result_branch_patterns entry")
        except RemoteError as exc:
            raise _bad(exc.message) from exc
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
    if not isinstance(data["kind"], str) or data["kind"] not in BACKEND_KINDS:
        raise _bad("kind must be one of " + ", ".join(sorted(BACKEND_KINDS)))
    if not isinstance(data["description"], str) or not data["description"]:
        raise _bad("description must be a nonempty string")

    endpoint = data["endpoint"]
    endpoint_ref = data["endpoint_ref"]
    if data["kind"] == "cursor-cloud" and (endpoint is None or endpoint_ref is not None):
        raise _bad("cursor-cloud requires endpoint and endpoint_ref must be null")
    if data["kind"] == "grok-routine" and (endpoint is not None or endpoint_ref is None):
        raise _bad("grok-routine requires endpoint_ref and endpoint must be null")
    # The two exhaustive kind-specific branches above enforce endpoint exclusivity.  A
    # standalone XOR check would be unreachable and would look like an independent control
    # while every violating shape had already been refused by its kind branch.
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
    if not isinstance(data["billing_basis"], str) or data["billing_basis"] not in BILLING_BASES:
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
    screen_for_secret_material(
        normalised, "manifest", code="manifest-invalid",
        allowed_reference_paths={
            ("endpoint_ref",), ("credential_ref",), ("signing_key_ref",),
        })
    return normalised


def load_manifest(path: Path, name: str) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError, ValueError, TypeError, OverflowError,
            RecursionError):
        raise _bad(f"could not read manifest {name}") from None
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError, TypeError, OverflowError, RecursionError):
        raise _bad(f"manifest {name} is not valid JSON") from None
    return validate_manifest(data, name)


def resolve_backend(name: str, kind: str | None = None) -> dict:
    """Name -> validated manifest, or raise. The single authority; adapters import this.

    Enablement is checked AFTER validation, deliberately: a broken manifest must report as
    broken (2), not as absent (3). Otherwise the day a human flips the flags is the day they
    discover the manifest never parsed.
    """
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        raise RemoteError("request-invalid", "invalid backend identifier")
    path = manifest_path(name)
    if not path.is_file():
        raise RemoteError("manifest-absent", f"manifest not found: {name}")
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
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError,
                OverflowError, RecursionError):
            raise RemoteError("malformed-response",
                              "response body is not valid UTF-8 JSON") from None
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
        except Exception as exc:  # noqa: BLE001 - normalize every urllib/socket failure
            raise self._normalize_io_error(exc, timeout) from None

    @staticmethod
    def _normalize_io_error(exc: Exception, timeout: int) -> RemoteError:
        """Convert network failures without copying exception text into a durable/log path."""
        if isinstance(exc, (TimeoutError, socket.timeout)):
            return RemoteError("transport-timeout", "transport timed out")
        return RemoteError("transport-error", "transport failed while communicating with provider")

    def request(self, method: str, url: str, headers: dict, body: bytes | None,
                timeout: int) -> TransportResponse:
        handle = self._open(method, url, headers, body, timeout)
        try:
            with contextlib.closing(handle):
                try:
                    payload = handle.read()
                    status = getattr(handle, "status", None) or handle.getcode()
                    headers_out = dict(handle.headers.items())
                except Exception as exc:  # noqa: BLE001 - normalize read/provider I/O failures
                    raise self._normalize_io_error(exc, timeout) from None
                return TransportResponse(status, headers_out, payload)
        except RemoteError:
            raise
        except Exception as exc:  # noqa: BLE001 - closing and response plumbing are I/O too
            raise self._normalize_io_error(exc, timeout) from None

    def stream_lines(self, method: str, url: str, headers: dict, body: bytes | None,
                     timeout: int):
        handle = self._open(method, url, headers, body, timeout)
        try:
            with contextlib.closing(handle):
                try:
                    for raw in handle:
                        yield raw.decode("utf-8", errors="replace").rstrip("\r\n")
                except Exception as exc:  # noqa: BLE001 - normalize iterator/read failures
                    raise self._normalize_io_error(exc, timeout) from None
        except RemoteError:
            raise
        except Exception as exc:  # noqa: BLE001 - closing is part of stream I/O
            raise self._normalize_io_error(exc, timeout) from None


def classify_status(status: int, body: bytes) -> None:
    """Map an HTTP status onto the typed taxonomy. 2xx returns; everything else raises.

    429 and 402 are separated on purpose: a rate limit is retryable at the same cost, while
    a quota/payment refusal is a DEFER. Quota exhaustion must never become an argument for
    spending money -- that is Lucas's decision and lives in .env, not in an error handler
    (plan invariant 8).
    """
    if 200 <= status < 300:
        return
    if status in (401, 403):
        raise RemoteError("auth-failed",
                          f"provider rejected the credential (HTTP {status}); a human "
                          "re-authorises through the credential window")
    if status == 404:
        raise RemoteError("not-found", "provider returned HTTP 404")
    if status == 402:
        raise RemoteError("quota-exhausted", "provider reports the pool is exhausted (HTTP 402)")
    if status == 429:
        raise RemoteError("rate-limited", "provider rate limited the request")
    if status == 503:
        raise RemoteError("provider-unavailable", "provider is unavailable (HTTP 503)")
    if 500 <= status < 600:
        raise RemoteError("provider-error", f"provider error HTTP {status}")
    raise RemoteError("request-invalid", f"provider rejected the request HTTP {status}")


# --- PAUSE -------------------------------------------------------------------------------

def pause_path(base: Path) -> Path:
    state = _safe_directory(Path(base) / "state")
    return _safe_file(state / "PAUSE")


def _runtime_file_exists(path: Path) -> bool:
    try:
        with _PinnedDirectory(path.parent, create=False) as parent:
            return _verify_runtime_leaf(parent, path.name) is not None
    except RemoteError as exc:
        if exc.code == "not-found":
            return False
        raise


def is_paused(base: Path) -> bool:
    path = pause_path(base)
    return _runtime_file_exists(path)


def remove_runtime_file(path: Path) -> bool:
    """Remove one checked runtime file through its pinned parent directory."""
    try:
        with _PinnedDirectory(path.parent, create=False) as parent:
            expected = _verify_runtime_leaf(parent, path.name)
            if expected is None:
                return False
            _before_remote_leaf_remove(path)
            parent.verify()
            current = _verify_runtime_leaf(parent, path.name)
            if current is None or not _same_identity(expected, current):
                raise RemoteError("request-invalid", "runtime storage file changed before removal")
            try:
                if parent._relative:
                    assert parent.descriptor is not None
                    os.unlink(path.name, dir_fd=parent.descriptor)
                else:
                    os.unlink(parent.path / path.name)
            except OSError:
                raise RemoteError("request-invalid", "runtime storage file could not be removed") from None
            parent.verify()
            _fsync_directory(path.parent, parent.descriptor)
            return True
    except RemoteError as exc:
        if exc.code == "not-found":
            return False
        raise


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
        return _safe_directory(self.base / "state" / ".locks")

    def __enter__(self) -> "AccountLease":
        runtime = _runtime_state()
        self._lock_dir()
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
                    _safe_existing_lock(candidate)
                    runtime.acquire_witnessed_directory_lock(
                        candidate, f"remote-{self.pool_id}-slot-{slot}", os.getpid())
                except (RemoteError, RuntimeError, OSError):
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
    if not isinstance(backend, str) or not NAME_RE.fullmatch(backend):
        raise RemoteError("request-invalid", "backend name cannot name runtime storage")
    return _safe_directory(Path(base) / "state" / "remote" / backend)


def attempts_journal(base: Path, backend: str) -> Path:
    return _safe_file(remote_root(base, backend) / "attempts.jsonl")


def attempt_projection(base: Path, backend: str, attempt_id: str) -> Path:
    if not isinstance(attempt_id, str) or not ATTEMPT_ID_RE.fullmatch(attempt_id):
        raise RemoteError("request-invalid", "attempt_id cannot name runtime storage")
    return _safe_file(remote_root(base, backend) / "attempts" / f"{attempt_id}.json")


def session_path(base: Path, backend: str, dispatch_id: str) -> Path:
    if not isinstance(dispatch_id, str) or not DISPATCH_ID_RE.fullmatch(dispatch_id):
        raise RemoteError("request-invalid", "dispatch_id cannot name runtime storage")
    return _safe_file(remote_root(base, backend) / "sessions" / f"{dispatch_id}.json")


def usage_path(base: Path, backend: str, dispatch_id: str) -> Path:
    if not isinstance(dispatch_id, str) or not DISPATCH_ID_RE.fullmatch(dispatch_id):
        raise RemoteError("request-invalid", "dispatch_id cannot name runtime storage")
    return _safe_file(remote_root(base, backend) / "usage" / f"{dispatch_id}.json")


class RemoteStateLock:
    """Cross-process serialization for the remote journal and projections.

    The lock covers the read/check/reserve/project transition, not merely the append.  The
    same lock is held across an outbound mutation by ``outbound_admission``; PAUSE writers
    use it too, giving PAUSE and send one linearization point.
    """

    def __init__(self, base: Path, backend: str) -> None:
        if not isinstance(backend, str) or not NAME_RE.fullmatch(backend):
            raise RemoteError("request-invalid", "backend name cannot name a lock")
        self.base = Path(base)
        self.backend = backend
        self.path: Path | None = None
        self._lock_parent: _PinnedDirectory | None = None
        self._native_lock_parent_pins: list[tuple[Path, int, tuple[int, int, int]]] = []

    def __enter__(self) -> "RemoteStateLock":
        runtime = _runtime_state()
        lock_parent: _PinnedDirectory | None = None
        if os.name == "nt":
            self._native_lock_parent_pins = _win_pin_lock_parent(
                self.base / "state" / ".locks", create=True
            )
            candidate = self.base / "state" / ".locks" / "remote-state.lock"
        else:
            lock_parent = _PinnedDirectory(self.base / "state" / ".locks", create=True)
            lock_parent.__enter__()
            candidate = _pinned_directory_child(lock_parent, "remote-state.lock")
        acquired = False
        # One admission/state lock covers every remote backend and PAUSE writer.  A
        # backend-specific lock would leave the PAUSE transition racing a sender from the
        # other adapter.
        try:
            _safe_existing_lock(candidate)
            # On POSIX candidate is rooted at /proc/self/fd/<pinned-parent>, so the
            # runtime lock publisher never re-resolves the checked parent pathname.
            runtime.acquire_witnessed_directory_lock(candidate, "remote-state", os.getpid())
            acquired = True
            if self._native_lock_parent_pins:
                _win_validate_lock_parent_pins(self._native_lock_parent_pins)
            elif lock_parent is not None:
                lock_parent.verify()
            self.path = candidate
            self._lock_parent = lock_parent
            lock_parent = None
            return self
        except BaseException:
            if acquired:
                with contextlib.suppress(RuntimeError, OSError):
                    runtime.release_witnessed_directory_lock(
                        candidate, "remote-state", os.getpid())
            if lock_parent is not None:
                lock_parent.close()
            if self._native_lock_parent_pins:
                _win_close_lock_parent_pins(self._native_lock_parent_pins)
                self._native_lock_parent_pins = []
            raise

    def __exit__(self, *_: object) -> None:
        if self.path is None:
            return
        runtime = _runtime_state()
        parent = self._lock_parent
        try:
            runtime.release_witnessed_directory_lock(
                self.path, "remote-state", os.getpid())
        finally:
            if parent is not None:
                parent.close()
            self._lock_parent = None
            if self._native_lock_parent_pins:
                _win_close_lock_parent_pins(self._native_lock_parent_pins)
                self._native_lock_parent_pins = []
            self.path = None


def remote_state_lock(base: Path, backend: str) -> RemoteStateLock:
    return RemoteStateLock(base, backend)


@contextlib.contextmanager
def outbound_admission(base: Path, backend: str, operation: str):
    """Atomically admit a mutation with PAUSE and hold the admission through send."""
    with remote_state_lock(base, backend):
        # This is intentionally the first operation under the shared lock.  pause.sh and
        # resume.sh acquire the same lock before changing state/PAUSE, so a PAUSE request is
        # ordered either before admission (send is refused) or after the send completes.
        assert_not_paused(base, operation)
        yield


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
    if not isinstance(value, dict):
        raise RemoteError("request-invalid", "durable JSON records must be objects")
    with _PinnedDirectory(path.parent) as parent:
        target = _verify_runtime_leaf(parent, path.name)
        fd, tmp_name = _create_relative_temp(parent, ".remote-")
        try:
            if hasattr(os, "fchmod"):
                os.fchmod(fd, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                try:
                    json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
                except (TypeError, ValueError, OverflowError, RecursionError):
                    raise RemoteError(
                        "request-invalid", "durable JSON records must contain finite JSON"
                    ) from None
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            _replace_relative(parent, tmp_name, path.name, path, target)
            _fsync_directory(path.parent, parent.descriptor)
        except BaseException:
            with contextlib.suppress(OSError):
                os.close(fd)
            with contextlib.suppress(OSError, RemoteError):
                _unlink_relative(parent, tmp_name)
            raise


def atomic_bytes(path: Path, value: bytes) -> None:
    """Atomically replace a runtime file, refusing symlink targets and syncing its parent."""
    if not isinstance(value, bytes):
        raise RemoteError("request-invalid", "atomic runtime content must be bytes")
    with _PinnedDirectory(path.parent) as parent:
        target = _verify_runtime_leaf(parent, path.name)
        fd, tmp_name = _create_relative_temp(parent, ".remote-")
        try:
            if hasattr(os, "fchmod"):
                os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
            _replace_relative(parent, tmp_name, path.name, path, target)
            _fsync_directory(path.parent, parent.descriptor)
        except BaseException:
            with contextlib.suppress(OSError):
                os.close(fd)
            with contextlib.suppress(OSError, RemoteError):
                _unlink_relative(parent, tmp_name)
            raise


def read_attempts(base: Path, backend: str) -> list[dict]:
    with remote_state_lock(base, backend):
        return _read_attempts_unlocked(base, backend)


def _read_attempts_unlocked(base: Path, backend: str) -> list[dict]:
    path = attempts_journal(base, backend)
    if not _runtime_file_exists(path):
        return []
    return [row for row in read_jsonl_objects(path) if isinstance(row, dict)]


def _commit_attempt(base: Path, backend: str, body: dict) -> dict:
    """Journal first (durable, content-addressed, deduped), then project.

    ``record_id`` is the digest of the record's own content, so a crash between the append
    and the projection is repaired by simply repeating the call: the second append
    deduplicates against the first instead of doubling the row.
    """
    attempt_id = body.get("attempt_id")
    if not isinstance(attempt_id, str) or not ATTEMPT_ID_RE.fullmatch(attempt_id):
        raise RemoteError("request-invalid", "attempt_id cannot name runtime storage")
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

    def _close(self, state: str, outcome: str, detail: dict | None, clock=None,
               *, lock_held: bool = False) -> dict:
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
        if lock_held:
            self.record = _commit_attempt(self.base, self.backend, body)
        else:
            with remote_state_lock(self.base, self.backend):
                current = latest_states(_read_attempts_unlocked(self.base, self.backend)).get(
                    self.attempt_id)
                if current is None or current.get("state") != ATTEMPT_OPEN:
                    raise RemoteError("request-invalid",
                                      f"attempt {self.attempt_id} is no longer open")
                self.record = _commit_attempt(self.base, self.backend, body)
        self.closed = True
        return self.record

    def succeed(self, outcome: str = "ok", detail: dict | None = None, clock=None,
                *, lock_held: bool = False) -> dict:
        return self._close(ATTEMPT_SUCCEEDED, outcome, detail, clock, lock_held=lock_held)

    def fail(self, error: RemoteError, clock=None, *, lock_held: bool = False) -> dict:
        return self._close(ATTEMPT_FAILED, error.code, error.as_record(), clock,
                           lock_held=lock_held)

    def defer(self, error: RemoteError, clock=None, *, lock_held: bool = False) -> dict:
        return self._close(ATTEMPT_DEFERRED, error.code, error.as_record(), clock,
                           lock_held=lock_held)


def lookup_attempt(base: Path, backend: str, *, dispatch_id: str, operation: str,
                   assignment_digest: str, request_digest: str,
                   lock_held: bool = False) -> AttemptHandle | None:
    """Look up an existing reservation without creating one.

    Adapters use this while holding outbound admission so a replay can be returned even if a
    credential has since been rotated or removed. New work still resolves credentials before
    calling ``begin_attempt`` and therefore consumes no attempt on configuration failure.
    """
    if not DISPATCH_ID_RE.fullmatch(dispatch_id or ""):
        raise RemoteError("request-invalid",
                          "dispatch_id must match ^[a-z0-9][a-z0-9-]{7,63}$")
    key = idempotency_key(backend, operation, assignment_digest, dispatch_id, request_digest)
    lock = contextlib.nullcontext() if lock_held else remote_state_lock(base, backend)
    with lock:
        mine = [row for row in latest_states(_read_attempts_unlocked(base, backend)).values()
                if row.get("idempotency_key") == key]
        for row in mine:
            if row.get("state") == ATTEMPT_SUCCEEDED:
                return AttemptHandle(base, backend, row, replayed=True)
        for row in mine:
            if row.get("state") == ATTEMPT_OPEN:
                return AttemptHandle(base, backend, row, unreconciled=True)
    return None


def begin_attempt(base: Path, backend: str, *, dispatch_id: str, operation: str,
                  assignment_digest: str, request_digest: str, max_attempts: int,
                  clock=None, lock_held: bool = False) -> AttemptHandle:
    """Commit the intent BEFORE any I/O, and refuse to re-send what may already have landed."""
    if not DISPATCH_ID_RE.fullmatch(dispatch_id or ""):
        raise RemoteError("request-invalid",
                          "dispatch_id must match ^[a-z0-9][a-z0-9-]{7,63}$")
    key = idempotency_key(backend, operation, assignment_digest, dispatch_id, request_digest)
    lock = contextlib.nullcontext() if lock_held else remote_state_lock(base, backend)
    with lock:
        rows = _read_attempts_unlocked(base, backend)
        mine = [row for row in latest_states(rows).values()
                if row.get("idempotency_key") == key]

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
        "pre_send_intent": {
            "operation": operation,
            "idempotency_key": key,
            "request_digest": request_digest,
        },
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
    if detail is not None and not isinstance(detail, dict):
        raise RemoteError("request-invalid", "reconciliation detail must be an object")
    evidence = dict(detail or {})
    screen_for_secret_material(evidence, "reconciliation evidence")
    with remote_state_lock(base, backend):
        rows = latest_states(_read_attempts_unlocked(base, backend))
        record = rows.get(attempt_id)
        if record is None:
            raise RemoteError("not-found", f"no attempt {attempt_id} for backend {backend}")
        if record.get("state") != ATTEMPT_OPEN:
            raise RemoteError("request-invalid",
                              f"attempt {attempt_id} is {record.get('state')!r}, not open")

        # A cancel is not a generic mutation.  "landed" only means success when the provider
        # reported its terminal cancellation state for this exact session and attempt.  A
        # missing, active, completed, or unknown observation must not turn a cancel request
        # into a successful cancellation or authorize a second request.
        if record.get("operation") == "cancel" and observed == "landed":
            raw_status = evidence.get("provider_status", evidence.get("vendor_state"))
            if (not isinstance(raw_status, str)
                    or raw_status.strip().upper() not in {"CANCELLED", "CANCELED"}):
                raise RemoteError(
                    "unreconciled-attempt",
                    "cancel reconciliation requires provider-terminal CANCELLED/CANCELED "
                    "evidence bound to the attempt and session")
            if evidence.get("attempt_id") != attempt_id:
                raise RemoteError("unreconciled-attempt",
                                  "cancel evidence is not bound to this attempt")
            if evidence.get("dispatch_id") != record.get("dispatch_id"):
                raise RemoteError("unreconciled-attempt",
                                  "cancel evidence is not bound to this dispatch")
            try:
                session = _read_session_unlocked(base, backend, record["dispatch_id"])
            except (KeyError, RemoteError) as exc:
                raise RemoteError("unreconciled-attempt",
                                  "cancel evidence has no readable bound session") from exc
            session_status = session.get("vendor_state")
            if (session.get("assignment_digest") != record.get("assignment_digest")
                    or session.get("run_id") != evidence.get("run_id")
                    or session.get("state") != "cancelled"
                    or not isinstance(session_status, str)
                    or session_status.strip().upper() != raw_status.strip().upper()):
                raise RemoteError("unreconciled-attempt",
                                  "cancel evidence does not match the admitted session")

        if record.get("operation") == "cancel" and observed == "not-landed":
            raise RemoteError("unreconciled-attempt",
                              "a cancel is not failed merely because terminal cancellation "
                              "has not been observed")
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
            "detail": {"observer": observer, "observed": observed, **evidence},
            "closed_at": closed_at,
            "updated_at": closed_at,
        })
        return _commit_attempt(base, backend, body)


def _read_session_unlocked(base: Path, backend: str, dispatch_id: str) -> dict:
    """Read and screen one session while the caller holds ``remote_state_lock``."""
    path = session_path(base, backend, dispatch_id)
    with _PinnedDirectory(path.parent, create=False) as parent:
        value = _read_runtime_json(parent, path, "session record is unreadable",
                                   f"no session record for dispatch {dispatch_id}")
    if not isinstance(value, dict):
        raise RemoteError("malformed-response", "session record is not a JSON object")
    allowed = _session_reference_paths(backend, value)
    screen_for_secret_material(value, "session", allowed_reference_paths=allowed)
    return value


def _session_reference_paths(backend: str, record: dict) -> set[tuple[str, ...]]:
    """Return reference paths for the one concrete session schema that defines them."""
    if backend == "grok-bot" and record.get("kind") == "grok-routine-dispatch":
        return {("endpoint_ref",), ("signing_key_ref",)}
    return set()


def _read_runtime_json(parent: _PinnedDirectory, path: Path, malformed_message: str,
                       missing_message: str) -> object:
    """Read one runtime record from a parent handle, with same-handle identity checks."""
    expected = _verify_runtime_leaf(parent, path.name)
    if expected is None:
        raise RemoteError("not-found", missing_message)
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0)
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor, _info = _open_runtime_leaf(parent, path, flags, expected=expected)
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            value = json.load(handle)
            _verify_runtime_leaf(parent, path.name, handle.fileno())
        parent.verify()
        return value
    except RemoteError:
        raise
    except (OSError, json.JSONDecodeError):
        raise RemoteError("malformed-response", malformed_message) from None


def write_session(base: Path, backend: str, dispatch_id: str, record: dict,
                  *, lock_held: bool = False) -> Path:
    if not DISPATCH_ID_RE.fullmatch(dispatch_id or ""):
        raise RemoteError("request-invalid", "dispatch_id must match ^[a-z0-9][a-z0-9-]{7,63}$")
    allowed = _session_reference_paths(backend, record)
    screen_for_secret_material(record, "session", allowed_reference_paths=allowed)
    lock = contextlib.nullcontext() if lock_held else remote_state_lock(base, backend)
    with lock:
        path = session_path(base, backend, dispatch_id)
        atomic_json(path, record)
    return path


def read_session(base: Path, backend: str, dispatch_id: str, *, lock_held: bool = False) -> dict:
    lock = contextlib.nullcontext() if lock_held else remote_state_lock(base, backend)
    with lock:
        return _read_session_unlocked(base, backend, dispatch_id)


def list_sessions(base: Path, backend: str) -> list[dict]:
    with remote_state_lock(base, backend):
        directory = _safe_directory(remote_root(base, backend) / "sessions")
        out: list[dict] = []
        with _PinnedDirectory(directory) as parent:
            if parent._relative:
                assert parent.descriptor is not None
                names = sorted(os.listdir(parent.descriptor))
            else:
                names = sorted(path.name for path in directory.glob("*.json"))
            for name in names:
                if not name.endswith(".json"):
                    continue
                path = directory / name
                value = _read_runtime_json(parent, path, "session record is unreadable",
                                            "session record disappeared")
                if isinstance(value, dict):
                    allowed = _session_reference_paths(backend, value)
                    screen_for_secret_material(value, "session",
                                               allowed_reference_paths=allowed)
                    out.append(value)
        return out


def write_usage(base: Path, backend: str, dispatch_id: str, record: dict,
                *, lock_held: bool = False) -> Path:
    if not DISPATCH_ID_RE.fullmatch(dispatch_id or ""):
        raise RemoteError("request-invalid", "dispatch_id must match ^[a-z0-9][a-z0-9-]{7,63}$")
    screen_for_secret_material(record, "usage")
    lock = contextlib.nullcontext() if lock_held else remote_state_lock(base, backend)
    with lock:
        path = usage_path(base, backend, dispatch_id)
        atomic_json(path, record)
    return path


def read_usage(base: Path, backend: str, dispatch_id: str) -> dict:
    with remote_state_lock(base, backend):
        path = usage_path(base, backend, dispatch_id)
        with _PinnedDirectory(path.parent, create=False) as parent:
            value = _read_runtime_json(parent, path, "usage record is unreadable",
                                       f"no usage record for dispatch {dispatch_id}")
        if not isinstance(value, dict):
            raise RemoteError("malformed-response", "usage record is not a JSON object")
        screen_for_secret_material(value, "usage")
        return value


# --- CLI: validation only ------------------------------------------------------------------

def validate_directory() -> int:
    directory = manifest_dir()
    if not directory.is_dir():
        diag("remote backend directory not found")
        return EXIT_UNAVAILABLE
    paths = sorted(directory.glob("*.json"))
    invalid = 0
    for path in paths:
        stem = path.name[: -len(".json")]
        if not NAME_RE.fullmatch(stem):
            diag("manifest filename has an invalid backend identifier")
            invalid += 1
            continue
        try:
            load_manifest(path, stem)
        except RemoteError as exc:
            diag(f"manifest {stem}: {exc.message}")
            invalid += 1
    if invalid:
        diag(f"{invalid} of {len(paths)} manifest(s) invalid")
        return EXIT_INVALID
    diag(f"{len(paths)} manifest(s) valid")
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
