#!/usr/bin/env python3
"""Phase 8 class sweep for durable writers, hostile inputs, and schema parity.

The harness intentionally uses one caller-owned directory under the system temp
directory.  It does not use TemporaryDirectory because the Windows test host
may deny cleanup of directories held by native directory handles.
"""

from __future__ import annotations

import copy
import hashlib
import hmac
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch

try:
    import jsonschema
    from importlib.metadata import version as package_version
    from jsonschema import Draft202012Validator
except ImportError as exc:  # pragma: no cover - environment prerequisite
    print(f"phase8-durable-writer-sweep: SKIP (jsonschema unavailable: {exc})")
    raise SystemExit(77)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import execution_fabric as fabric  # noqa: E402


NOW = "2026-08-28T12:00:00Z"
SOURCE = "a" * 40
RESULT = "b" * 40
JSONSCHEMA_VERSION = package_version("jsonschema")


# Draft 2020-12 defines an integer by its numeric value, so a JSON number such
# as 1.0 is an integer to the stock validator.  No standard keyword can reject
# 1.0 while accepting 1; the runtime's exact-Python-int policy is intentionally
# stricter than the published schema for these ten cases.
_JUSTIFIED_INTEGER_FLOAT_SCHEMA_ONLY = frozenset({
    "host_registration.max_concurrency=1.0",
    "host_registration.workload_concurrency={'implementer': 1.0}",
    "host_heartbeat.sequence=1.0",
    "host_heartbeat.lease_epoch=1.0",
    "pool_status.max_concurrency=1.0",
    "pool_status.quota_remaining=1.0",
    "pool_status.account_quota_remaining=1.0",
    "placement_requirements.schema_version=1.0",
    "placement_candidate.weight=1.0",
    "assignment.schema_version=1.0",
})

# NaN is not a JSON number and Python's jsonschema API can nevertheless be
# handed one directly.  Its minimum/maximum comparisons are all false, so no
# standard numeric keyword can reject it.  The runtime parse boundary rejects
# NaN before records reach this API; these four direct-object cases are the
# deliberately documented residual parity gap.
_JUSTIFIED_NAN_SCHEMA_ONLY = frozenset({
    "pool_status.cost_per_run=NaN",
    "placement_requirements.model_parameters={'bad': NaN}",
    "placement_candidate.cost_per_run=NaN",
    "assignment.model_parameters={'bad': NaN}",
})
_JUSTIFIED_SCHEMA_ONLY = (_JUSTIFIED_INTEGER_FLOAT_SCHEMA_ONLY |
                          _JUSTIFIED_NAN_SCHEMA_ONLY)


def _make_junction(link: Path, target: Path) -> None:
    if os.name == "nt":
        result = subprocess.run(["cmd.exe", "/c", "mklink", "/J", str(link), str(target)],
                                capture_output=True, text=True)
        if result.returncode != 0:
            raise OSError(result.returncode, result.stderr.strip() or "junction creation failed")
    else:
        link.symlink_to(target, target_is_directory=True)


def _records() -> tuple[fabric.HostRegistration, fabric.HostHeartbeat, fabric.PoolStatus,
                        fabric.PlacementRequirements, fabric.PlacementCandidate,
                        fabric.Assignment, fabric.VerificationReceipt, fabric.RoutingPolicy]:
    host = fabric.HostRegistration.build(
        host_id="host-one", capabilities=("terminal", "workspace-edit", "structured-result"),
        operating_system="windows", architectures=("x86_64",), sandbox_profiles=("isolated",),
        network_profiles=("none",), trust_class="controller-registered", max_concurrency=2,
        workload_concurrency={"implementer": 2}, registered_at=NOW,
        network_endpoints={"none": ()})
    heartbeat = fabric.HostHeartbeat(host.host_id, host.registration_digest, 1, NOW, 1)
    pool = fabric.PoolStatus("pool-one", "included", ("implementer",), ("project-one",),
                             ("model-one",), 2, 0, 10, "daily", False, 0.0)
    requirements = fabric.PlacementRequirements(
        "task-one", "project-one", "implementer", ("terminal",), "windows", "isolated", "none",
        ("included",), 10.0, "model-one", (), (), SOURCE)
    candidate = fabric.PlacementCandidate(
        "candidate-one", "engine-one", "provider-one", "pool-one", "model-one", "host-one",
        "isolated", "none", ("terminal",), "windows", "included", 0.0, ("implementer",))
    assignment, trace = fabric.resolve_placement(
        requirements, (candidate,), {host.host_id: host}, {host.host_id: heartbeat},
        {pool.pool_id: pool}, now_epoch=1787918400, created_at=NOW)
    assert assignment is not None and not trace
    receipt = fabric.VerificationReceipt.build(
        receipt_id="receipt-one", assignment_digest=assignment.assignment_digest,
        source_sha=SOURCE, candidate_id="candidate-one", result_commit=RESULT,
        diff_digest="c" * 64, scope_digest="d" * 64, gate_digest="e" * 64,
        verifier_identity="controller/verifier-one", verified_at=NOW)
    policy = fabric.RoutingPolicy.build(policy_id="policy-one", allowed_billing_basis=("included",),
                                        allow_on_demand=False)
    return host, heartbeat, pool, requirements, candidate, assignment, receipt, policy


def _stock_validator(schema: dict) -> Draft202012Validator:
    """Use the shipped schema with the stock Draft 2020-12 validator."""
    return Draft202012Validator(schema)


def _parity_label(kind: str, field: str, value: object) -> str:
    def render(item: object) -> str:
        if isinstance(item, float):
            if math.isnan(item):
                return "NaN"
            if math.isinf(item):
                return "Infinity" if item > 0 else "-Infinity"
        if isinstance(item, dict):
            return "{" + ", ".join(f"{render(key)}: {render(nested)}"
                                   for key, nested in item.items()) + "}"
        if isinstance(item, list):
            return "[" + ", ".join(render(nested) for nested in item) + "]"
        return repr(item)

    rendered = render(value)
    return f"{kind}.{field}={rendered}"


def _runtime_parser(kind: str, value: dict) -> object:
    parsers = {
        "host_registration": fabric.HostRegistration.from_dict,
        "host_heartbeat": fabric.HostHeartbeat.from_dict,
        "pool_status": fabric.PoolStatus.from_dict,
        "placement_requirements": fabric.PlacementRequirements.from_dict,
        "placement_candidate": fabric.PlacementCandidate.from_dict,
        "assignment": fabric.Assignment.from_dict,
        "verification_receipt": fabric.VerificationReceipt.from_dict,
        "routing_policy": fabric.RoutingPolicy.from_dict,
    }
    return parsers[kind](value)


def _refresh_digest(kind: str, value: dict) -> None:
    if kind == "host_registration":
        value["registration_digest"] = fabric.digest_record(
            {key: item for key, item in value.items() if key != "registration_digest"})
    elif kind == "routing_policy":
        value["policy_digest"] = fabric.digest_record(
            {key: item for key, item in value.items() if key != "policy_digest"})
    elif kind == "assignment":
        value["assignment_digest"] = fabric.digest_record(
            {key: item for key, item in value.items() if key != "assignment_digest"})
    elif kind == "verification_receipt":
        value["receipt_digest"] = fabric.digest_record(
            {key: item for key, item in value.items() if key != "receipt_digest"})


def run_differential() -> int:
    schema_path = Path(__file__).resolve().parents[2] / "schemas" / "control-plane" / "v1" / "execution-fabric.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = _stock_validator(schema)
    host, heartbeat, pool, requirements, candidate, assignment, receipt, policy = _records()
    bases = {item.to_dict()["kind"]: item.to_dict() for item in
             (host, heartbeat, pool, requirements, candidate, assignment, receipt, policy)}
    cases: list[tuple[str, str, object]] = [
        (kind, "valid", None) for kind in bases
    ]
    cases.extend(
        (kind, field, value) for kind, field, value in (
        ("host_registration", "max_concurrency", True),
        ("host_registration", "max_concurrency", 1.0),
        ("host_registration", "max_concurrency", 10 ** 500),
        ("host_registration", "capabilities", [""]),
        ("host_registration", "workload_concurrency", {"implementer": 1.0}),
        ("host_registration", "registered_at", "2026-02-30T12:00:00Z"),
        ("host_registration", "network_endpoints", {"none": [""]}),
        ("host_heartbeat", "sequence", True),
        ("host_heartbeat", "sequence", 1.0),
        ("host_heartbeat", "lease_epoch", 1.0),
        ("host_heartbeat", "observed_at", "2026-02-30T12:00:00Z"),
        ("pool_status", "in_flight", True),
        ("pool_status", "max_concurrency", 1.0),
        ("pool_status", "quota_remaining", 1.0),
        ("pool_status", "quota_period", ""),
        ("pool_status", "on_demand", 1),
        ("pool_status", "cost_per_run", float("nan")),
        ("pool_status", "cost_per_run", float("inf")),
        ("pool_status", "account_id", ""),
        ("pool_status", "account_quota_remaining", 1.0),
        ("placement_requirements", "schema_version", 1.0),
        ("placement_requirements", "max_cost_usd", True),
        ("placement_requirements", "max_cost_usd", 1.0),
        ("placement_requirements", "max_cost_usd", float("inf")),
        ("placement_requirements", "operating_system", ""),
        ("placement_requirements", "model", ""),
        ("placement_requirements", "source_branch", "feature/$bad"),
        ("placement_requirements", "source_branch", "feature//bad"),
        ("placement_requirements", "allowed_paths", ["src..file"]),
        ("placement_requirements", "allowed_paths", [""]),
        ("placement_requirements", "policy", "unregistered-policy"),
        ("placement_requirements", "manual_candidate_id", ""),
        ("placement_requirements", "seed_manifest_digest", "bad"),
        ("placement_requirements", "model_parameters", {"bad": float("nan")}),
        ("placement_requirements", "publication_policy", ""),
        ("placement_candidate", "weight", True),
        ("placement_candidate", "weight", 1.0),
        ("placement_candidate", "weight", 0),
        ("placement_candidate", "enabled", 1),
        ("placement_candidate", "speed_score", True),
        ("placement_candidate", "cost_per_run", float("nan")),
        ("placement_candidate", "reviewer_score", float("inf")),
        ("placement_candidate", "required_endpoints", [""]),
        ("assignment", "schema_version", True),
        ("assignment", "schema_version", 1.0),
        ("assignment", "source_branch", "feature//bad"),
        ("assignment", "allowed_paths", [""]),
        ("assignment", "model_parameters", {"bad": float("nan")}),
        ("assignment", "candidate_id", ""),
        ("verification_receipt", "verifier_identity", "controller/verifier\n"),
        ("verification_receipt", "verified_at", "2026-02-30T12:00:00Z"),
        ("verification_receipt", "authentication_tag", ""),
        ("routing_policy", "allow_on_demand", 1),
        )
    )
    runtime_only: list[str] = []
    schema_only: list[str] = []
    raw_runtime: list[str] = []
    for kind, field, value in cases:
        candidate_value = copy.deepcopy(bases[kind])
        if field != "valid":
            candidate_value[field] = value
            try:
                _refresh_digest(kind, candidate_value)
            except fabric.FabricError:
                # An oversized/non-finite mutation is rejected by canonicalization
                # itself; the stale digest must not turn it into a false positive.
                pass
        schema_ok = validator.is_valid(candidate_value)
        try:
            _runtime_parser(kind, candidate_value)
        except fabric.FabricError:
            runtime_ok = False
        except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError, OSError) as exc:
            raw_runtime.append(f"{_parity_label(kind, field, value)}: {type(exc).__name__}")
            runtime_ok = False
        else:
            runtime_ok = True
        label = _parity_label(kind, field, value)
        if runtime_ok and not schema_ok:
            runtime_only.append(label)
        elif schema_ok and not runtime_ok:
            schema_only.append(label)
    if raw_runtime:
        raise AssertionError("raw runtime exceptions:\n" + "\n".join(raw_runtime))
    if runtime_only:
        raise AssertionError("runtime_only acceptance is unsafe:\n" + "\n".join(runtime_only))
    actual_schema_only = frozenset(schema_only)
    if actual_schema_only != _JUSTIFIED_SCHEMA_ONLY:
        unexpected = sorted(actual_schema_only - _JUSTIFIED_SCHEMA_ONLY)
        missing = sorted(_JUSTIFIED_SCHEMA_ONLY - actual_schema_only)
        raise AssertionError(
            "schema_only set changed; unexpected=" + repr(unexpected) +
            " missing=" + repr(missing))
    print(f"ok    CLASS D differential: {len(cases)} stock-schema cases "
          f"jsonschema={JSONSCHEMA_VERSION} runtime_only={len(runtime_only)} "
          f"schema_only={len(schema_only)} raw={len(raw_runtime)}")
    return len(cases)


def run_hostile_inputs(root: Path) -> int:
    root.mkdir(parents=True, exist_ok=True)
    host, heartbeat, pool, requirements, candidate, assignment, receipt, policy = _records()
    cases = [
        ("non-object root", lambda: fabric.PlacementRequirements.from_dict(True)),
        ("bool integer", lambda: fabric.HostHeartbeat.from_dict(dict(heartbeat.to_dict(), sequence=True))),
        ("float integer", lambda: fabric.HostHeartbeat.from_dict(dict(heartbeat.to_dict(), sequence=1.0))),
        ("huge integer", lambda: fabric.HostHeartbeat.from_dict(dict(heartbeat.to_dict(), sequence=10 ** 500))),
        ("1e999", lambda: fabric.PlacementRequirements.from_dict(dict(requirements.to_dict(), max_cost_usd=float("inf")))),
        ("NaN", lambda: fabric.PlacementRequirements.from_dict(dict(requirements.to_dict(), max_cost_usd=float("nan")))),
        ("1e999 JSON", lambda: fabric._json_load("1e999")),
        ("Infinity JSON", lambda: fabric._json_load("Infinity")),
        ("NaN JSON", lambda: fabric._json_load("NaN")),
        ("huge JSON integer", lambda: fabric._json_load("1" + "0" * 500)),
        ("deeply nested JSON", lambda: fabric._json_load("[" * 65 + "0" + "]" * 65)),
        ("invalid UTF-8", lambda: _invalid_utf8_journal(root)),
    ]
    typed = 0
    for label, operation in cases:
        try:
            operation()
        except fabric.FabricError:
            typed += 1
        except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError, OSError) as exc:
            raise AssertionError(f"{label} leaked {type(exc).__name__}") from exc
        else:
            raise AssertionError(f"{label} was accepted")

    authority = root / "input-authority.key"
    authority.write_bytes(b"authority")
    if os.name != "nt":
        authority.chmod(0o600)
    registry = fabric.VerificationKeyRegistry.provision(
        root / "input-verifiers.json", authority_key_path=authority,
        verification_keys={"controller/verifier-one": "test-key"}, root=root)
    receipt_path = root / "input-receipts.jsonl"
    store = fabric.VerificationReceiptStore(receipt_path, root=root, verification_registry=registry)
    store.issue(receipt)
    receipt_path.write_bytes(b"{malformed receipt\n")
    try:
        fabric.VerificationReceiptStore(receipt_path, root=root, verification_registry=registry)
    except fabric.ReconciliationError:
        typed += 1
    except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError, OSError) as exc:
        raise AssertionError(f"malformed receipt JSON leaked {type(exc).__name__}") from exc
    else:
        raise AssertionError("malformed receipt JSON was accepted")
    print(f"ok    CLASS B/A hostile-input matrix: {typed} cases typed, no traceback/raw exception")
    return typed


def _invalid_utf8_journal(root: Path) -> None:
    path = root / "invalid-utf8.jsonl"
    path.write_bytes(b"\xff\n")
    fabric.DurableFabricStore(path, root=root)


def _writer(mode: str, path: Path, root: Path) -> object:
    if mode == "append":
        return fabric._append_bytes(path, b"writer-payload\n")
    if mode == "replace":
        return fabric._replace_store_bytes(path, b"writer-payload\n")
    if mode == "read":
        return fabric._read_store_bytes(path)
    raise AssertionError(mode)


def _assert_handles_released(path: Path, lock_path: Path, label: str) -> None:
    """Prove a completed durable operation released its leaf and lock handles."""
    released = path.with_name(path.name + ".release-check")
    path.rename(released)
    released.unlink()
    lock_path.unlink(missing_ok=True)
    print(f"ok    handle release: {label}")


def _run_case(case: Path, mode: str, hostile: str | None) -> None:
    root = case / "root"
    outside_dir = case / "outside"
    case.mkdir(parents=True)
    outside_dir.mkdir()
    if hostile == "junction-root":
        real_root = case / "real-root"
        real_root.mkdir()
        _make_junction(root, real_root)
    else:
        root.mkdir()
    path = root / "store.jsonl"
    outside = outside_dir / "outside.jsonl"
    outside.write_bytes(b"outside-before\n")

    if hostile == "hardlink":
        os.link(outside, path)
    elif hostile == "junction-leaf":
        target = outside_dir / "leaf-target"
        target.mkdir()
        _make_junction(path, target)
    elif hostile == "junction-ancestor":
        ancestor = root / "nested"
        target = outside_dir / "ancestor-target"
        target.mkdir()
        _make_junction(ancestor, target)
        path = ancestor / "store.jsonl"
    elif hostile == "junction-root":
        path = root / "store.jsonl"
    elif hostile == "race-hardlink":
        path.write_bytes(b"inside-before\n")

        injected = False
        if mode == "read":
            original_read = os.read

            def inject_read(descriptor, size):
                nonlocal injected
                result = original_read(descriptor, size)
                if result and not injected:
                    injected = True
                    path.unlink(missing_ok=True)
                    os.link(outside, path)
                return result

            context = patch.object(fabric.os, "read", side_effect=inject_read)
        else:
            original = fabric._revalidate_destination

            def inject(directory, candidate_path, *, expected_identity, must_exist):
                nonlocal injected
                result = original(directory, candidate_path, expected_identity=expected_identity, must_exist=must_exist)
                if candidate_path == path and not injected:
                    injected = True
                    path.unlink(missing_ok=True)
                    os.link(outside, path)
                return result

            context = patch.object(fabric, "_revalidate_destination", side_effect=inject)

        with context:
            try:
                _writer(mode, path, root)
            except fabric.FabricError:
                pass
            else:
                raise AssertionError(f"{mode} accepted hardlink race")
        if not injected:
            raise AssertionError(f"{mode} race hook did not execute")
        if outside.read_bytes() != b"outside-before\n":
            raise AssertionError(f"{mode} hardlink race touched bytes outside root")
        return
    elif hostile == "race-hardlink-create":
        path.write_bytes(b"inside-before\n")
        created_link = outside_dir / "inside-hardlink.jsonl"
        injected = False
        if mode == "read":
            original_read = os.read

            def inject_read(descriptor, size):
                nonlocal injected
                result = original_read(descriptor, size)
                if result and not injected:
                    injected = True
                    os.link(path, created_link)
                return result

            context = patch.object(fabric.os, "read", side_effect=inject_read)
        else:
            original = fabric._revalidate_destination

            def inject(directory, candidate_path, *, expected_identity, must_exist):
                nonlocal injected
                result = original(directory, candidate_path, expected_identity=expected_identity, must_exist=must_exist)
                if candidate_path == path and not injected:
                    injected = True
                    os.link(path, created_link)
                return result

            context = patch.object(fabric, "_revalidate_destination", side_effect=inject)

        with context:
            try:
                _writer(mode, path, root)
            except fabric.FabricError:
                pass
            else:
                raise AssertionError(f"{mode} accepted hardlink creation race")
        if not injected:
            raise AssertionError(f"{mode} hardlink creation hook did not execute")
        if created_link.exists():
            created_link.unlink()
        if outside.read_bytes() != b"outside-before\n":
            raise AssertionError(f"{mode} hardlink creation race touched bytes outside root")
        return
    elif hostile == "race-absent":
        if mode == "read":
            raise AssertionError("read has no absent-destination commit to race")
        calls = 0
        injected = False
        original = fabric._revalidate_destination

        def inject(directory, candidate_path, *, expected_identity, must_exist):
            nonlocal calls, injected
            result = original(directory, candidate_path, expected_identity=expected_identity, must_exist=must_exist)
            calls += 1
            if candidate_path == path and calls == 2 and not must_exist:
                os.link(outside, path)
                injected = True
            return result

        with patch.object(fabric, "_revalidate_destination", side_effect=inject):
            try:
                _writer(mode, path, root)
            except fabric.ReconciliationError as exc:
                if (getattr(exc, "code", None) != "UNSAFE_STORE_PATH" or
                        str(exc) != "durable store destination appeared before commit"):
                    raise AssertionError(
                        f"{mode} absent-destination race was not rejected by the atomic no-clobber guard: {exc}") from exc
            else:
                raise AssertionError(f"{mode} accepted an absent-destination race")
        if not injected:
            raise AssertionError(f"{mode} absent-destination race hook did not execute")
        path.unlink(missing_ok=True)
        if outside.read_bytes() != b"outside-before\n":
            raise AssertionError(f"{mode} absent-destination race touched outside bytes")
        return
    elif hostile == "absent":
        pass
    elif hostile is None:
        path.write_bytes(b"inside-before\n")
    else:
        raise AssertionError(hostile)

    before = outside.read_bytes()
    try:
        result = _writer(mode, path, root)
    except fabric.FabricError as exc:
        if hostile in {None, "absent"}:
            raise
        if hostile == "junction-leaf" and mode == "append" and str(exc) != "durable store leaf is not a unique regular file":
            raise AssertionError(f"junction-leaf guard produced unexpected refusal: {exc}") from exc
        if hostile in {"junction-ancestor", "junction-root"} and mode == "append":
            expected = ("store parent is not a real directory" if os.name == "nt"
                        else "store parent cannot be pinned safely")
            if str(exc) != expected:
                raise AssertionError(f"{hostile} pin guard produced unexpected refusal: {exc}") from exc
    except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError, OSError) as exc:
        raise AssertionError(f"{mode}/{hostile} leaked {type(exc).__name__}") from exc
    else:
        if hostile not in {None, "absent"}:
            raise AssertionError(f"{mode}/{hostile} was accepted")
        if hostile == "absent":
            if mode == "read" and result is not None:
                raise AssertionError("read/absent returned a record for a missing destination")
            if mode != "read" and path.read_bytes() != b"writer-payload\n":
                raise AssertionError(f"{mode}/absent did not publish the expected replacement")
    if outside.read_bytes() != before:
        raise AssertionError(f"{mode}/{hostile} touched bytes outside root")


def run_shared_battery(root: Path) -> int:
    cases = ("hardlink", "race-hardlink", "race-hardlink-create", "junction-leaf", "junction-ancestor", "junction-root", "absent")
    sites = (
        ("journal append", "append"),
        ("receipt issue append", "append"),
        ("receipt-store reload", "read"),
        ("verification-key registry write", "replace"),
        ("host-registry snapshot write", "replace"),
        ("integration journal/index append", "append"),
        ("replace destination exists", "replace"),
        ("replace destination absent", "replace"),
    )
    total = 0
    for label, mode in sites:
        for hostile in cases:
            case = root / f"{mode}-{hostile}-{label.replace(' ', '-')}"
            _run_case(case, mode, hostile)
            total += 1
        print(f"ok    {label}: hardlink/junction/race/absent battery ({len(cases)}/{len(cases)})")
    return total


def run_isolated_windows_reparse_guard(root: Path) -> int:
    """Prove the initial Windows handle reparse bit is independently enforced."""
    if os.name != "nt":
        print("skip  Windows handle-only reparse guard: native Windows handle reparse metadata is unavailable on POSIX (77)")
        return 77

    root.mkdir(parents=True, exist_ok=True)
    target = root / "real-directory"
    target.mkdir()

    opened: list[object] = []

    def report_handle_reparse(path, **kwargs):
        handle = object()
        opened.append(handle)
        return (handle, ("synthetic", os.fspath(path)), True, 1,
                os.fspath(path) == os.fspath(target))

    # The independent path-level check and later pinned validation are
    # deliberately quiet; weakening only the handle tuple's reparse sub-guard
    # must therefore make this behavior case accept the synthetic reparse object.
    with patch.object(fabric, "_windows_path_is_reparse", return_value=False), \
            patch.object(fabric, "_windows_open", side_effect=report_handle_reparse), \
            patch.object(fabric, "_close_windows", return_value=None), \
            patch.object(fabric._WindowsPinnedDirectory, "validate", return_value=None):
        try:
            with fabric._pin_store_directory(target):
                pass
        except fabric.ReconciliationError as exc:
            if (getattr(exc, "code", None) != "UNSAFE_STORE_PATH" or
                    str(exc) != "store parent is not a real directory"):
                raise AssertionError(f"isolated handle reparse guard produced unexpected refusal: {exc}") from exc
        else:
            raise AssertionError("isolated handle reparse guard accepted a reparse-marked directory")
    print("ok    Windows handle-only reparse guard: behavioral line-539 sub-guard refused (native tuple seam)")
    return 1


def run_posix_source_race(root: Path) -> int:
    """Exercise the POSIX source-handle guard and its pre-commit ordering."""
    if os.name == "nt":
        # Windows cannot provide POSIX dir_fd semantics, so exercise the
        # production branch with mocked descriptors.  The synthetic source
        # identity changes only before the pre-commit validation; a fake
        # os.replace restores it so the post-commit validations cannot mask a
        # missing line-834 guard.
        source_changed = False
        replace_called = False
        revalidation_calls = 0
        directory = object()
        current_descriptor = object()
        temporary_descriptor = object()
        current_identity = ("current",)
        temporary_identity = ("temporary",)

        def fake_leaf_info(descriptor):
            return "temporary" if descriptor is temporary_descriptor else "current"

        def validate_leaf_info(info, *, identity=None):
            actual = temporary_identity if info == "temporary" and not source_changed else (
                ("changed",) if info == "temporary" else current_identity)
            if actual != identity:
                raise fabric.ReconciliationError("UNSAFE_STORE_PATH", "synthetic source identity changed")
            return actual

        def revalidate_destination(*args, **kwargs):
            nonlocal revalidation_calls, source_changed
            revalidation_calls += 1
            if revalidation_calls == 2:
                source_changed = True

        def observe_replace(*args, **kwargs):
            nonlocal replace_called, source_changed
            replace_called = True
            source_changed = False

        path = root / "store" / "store.jsonl"
        with patch.object(fabric.os, "name", "posix"), \
                patch.object(fabric, "_pin_store_directory", return_value=nullcontext(directory)), \
                patch.object(fabric, "_open_leaf_in_directory",
                             return_value=(current_descriptor, current_identity)), \
                patch.object(fabric, "_write_new_leaf",
                             return_value=(temporary_descriptor, temporary_identity)), \
                patch.object(fabric, "_validate_pinned_directory", return_value=None), \
                patch.object(fabric, "_leaf_info_for_descriptor", side_effect=fake_leaf_info), \
                patch.object(fabric, "_validate_leaf_info", side_effect=validate_leaf_info), \
                patch.object(fabric, "_revalidate_destination", side_effect=revalidate_destination), \
                patch.object(fabric.os, "replace", side_effect=observe_replace), \
                patch.object(fabric.os, "close", return_value=None), \
                patch.object(fabric.os, "unlink", return_value=None):
            try:
                fabric._replace_store_bytes(path, b"writer-payload\n")
            except fabric.ReconciliationError as exc:
                if (getattr(exc, "code", None) != "UNSAFE_STORE_PATH" or
                        str(exc) != "synthetic source identity changed"):
                    raise AssertionError(f"POSIX source guard produced unexpected refusal: {exc}") from exc
            else:
                raise AssertionError("POSIX source identity change was accepted")
        if replace_called:
            raise AssertionError("POSIX source guard allowed os.replace after source identity changed")
        print("ok    POSIX replace source revalidation: behavioral line-834 guard refused (descriptor seam)")
        return 1
    root.mkdir(parents=True, exist_ok=True)
    store_root = root / "store"
    outside = root / "outside"; outside.write_bytes(b"outside-before\n")
    path = store_root / "store.jsonl"; store_root.mkdir()
    path.write_bytes(b"inside-before\n")
    created_link = root / "source-hardlink"
    injected = False
    replace_called = False
    original_revalidate = fabric._revalidate_destination
    original_replace = fabric.os.replace

    def inject_revalidate(directory, candidate_path, *, expected_identity, must_exist):
        nonlocal injected
        result = original_revalidate(directory, candidate_path, expected_identity=expected_identity, must_exist=must_exist)
        if candidate_path == path and not injected:
            temporary = next(item for item in store_root.iterdir() if item.name.startswith(".store.jsonl.tmp."))
            os.link(temporary, created_link)
            injected = True
        return result

    def observe_replace(*args, **kwargs):
        nonlocal replace_called
        replace_called = True
        return original_replace(*args, **kwargs)

    try:
        with patch.object(fabric, "_revalidate_destination", side_effect=inject_revalidate), \
                patch.object(fabric.os, "replace", side_effect=observe_replace):
            try:
                fabric._replace_store_bytes(path, b"writer-payload\n")
            except fabric.FabricError:
                pass
            else:
                raise AssertionError("POSIX source race was accepted")
        if not injected:
            raise AssertionError("POSIX source race hook did not execute")
        if replace_called:
            raise AssertionError("POSIX source guard allowed os.replace after source identity changed")
        if outside.read_bytes() != b"outside-before\n":
            raise AssertionError("POSIX source race touched bytes outside root")
    finally:
        created_link.unlink(missing_ok=True)
    print("ok    POSIX replace source revalidation: same-handle race refused before os.replace")
    return 1


def run_production_writer_convergence(root: Path) -> int:
    """Exercise every durable production entry point through its shared writer."""
    root.mkdir(parents=True, exist_ok=True)
    host, heartbeat, pool, requirements, candidate, assignment, receipt, _ = _records()

    def placement_requirements(task_id: str) -> fabric.PlacementRequirements:
        return fabric.PlacementRequirements(
            task_id, requirements.project_id, requirements.role, requirements.capabilities,
            requirements.operating_system, requirements.sandbox_profile, requirements.network_profile,
            requirements.billing_basis, requirements.max_cost_usd, requirements.model,
            requirements.model_parameters, requirements.allowed_paths, requirements.source_sha)

    # Build all stateful fixtures before observing the writers.  The setup
    # mutations themselves are intentionally not part of the route matrix.
    host_registry = fabric.DurableHostRegistry(root / "convergence-hosts.json", root=root, now=NOW)
    fabric_store = fabric.DurableFabricStore(root / "convergence-create.jsonl", root=root)
    placement_store = fabric.DurableFabricStore(root / "convergence-placement.jsonl", root=root)
    restart_store = fabric.DurableFabricStore(root / "convergence-restart.jsonl", root=root)
    expire_store = fabric.DurableFabricStore(root / "convergence-expire.jsonl", root=root)
    recovery_store = fabric.DurableFabricStore(root / "convergence-recovery.jsonl", root=root)
    result_store = fabric.DurableFabricStore(root / "convergence-result.jsonl", root=root)
    for store, lease_id in ((restart_store, "lease-restart"), (expire_store, "lease-expire"),
                            (recovery_store, "lease-recovery"), (result_store, "lease-result")):
        store.create_lease(assignment, lease_id=lease_id, attempt_id=f"{lease_id}-attempt",
                           remote_session_id=f"{lease_id}-session", now=NOW,
                           expires_at="2026-08-28T12:05:00Z")
    recovery_store.reconcile_restart(now="2026-08-28T12:01:00Z")

    authority = root / "convergence-authority.key"
    authority.write_bytes(b"convergence-authority")
    if os.name != "nt":
        authority.chmod(0o600)
    replace_counts = {"calls": 0}
    append_counts = {"calls": 0}
    operations: list[tuple[str, str, object]] = []

    def invoke(label: str, expected: str, operation: object) -> None:
        before = (replace_counts["calls"], append_counts["calls"])
        operation()
        after = (replace_counts["calls"], append_counts["calls"])
        index = 0 if expected == "replace" else 1
        if after[index] <= before[index]:
            helper = "_replace_store_bytes" if expected == "replace" else "_append_bytes"
            raise AssertionError(f"production entry point {label} bypassed {helper}")
        operations.append((label, expected, after[index] - before[index]))

    original_replace = fabric._replace_store_bytes
    original_append = fabric._append_bytes

    def observe_replace(path, data, **kwargs):
        replace_counts["calls"] += 1
        return original_replace(path, data, **kwargs)

    def observe_append(path, data, **kwargs):
        append_counts["calls"] += 1
        return original_append(path, data, **kwargs)

    with patch.object(fabric, "_replace_store_bytes", side_effect=observe_replace), \
            patch.object(fabric, "_append_bytes", side_effect=observe_append):
        invoke("DurableHostRegistry.register", "replace",
               lambda: host_registry.register(host))
        invoke("DurableHostRegistry.heartbeat", "replace",
               lambda: host_registry.heartbeat(heartbeat, now=NOW))
        invoke("DurableFabricStore.create_lease", "append",
               lambda: fabric_store.create_lease(assignment, lease_id="lease-create",
                                                 attempt_id="attempt-create", remote_session_id="session-create",
                                                 now=NOW, expires_at="2026-08-28T12:05:00Z"))
        invoke("DurableFabricStore.admit_placement", "append",
               lambda: placement_store.admit_placement(
                   placement_requirements("task-placement"), [candidate],
                   {host.host_id: host}, {host.host_id: heartbeat}, {pool.pool_id: pool},
                   lease_id="lease-placement", attempt_id="attempt-placement",
                   remote_session_id="session-placement", now=NOW,
                   expires_at="2026-08-28T12:05:00Z"))
        invoke("DurableFabricStore.reconcile_restart", "append",
               lambda: restart_store.reconcile_restart(now="2026-08-28T12:01:00Z"))
        invoke("DurableFabricStore.expire", "append",
               lambda: expire_store.expire(now="2026-08-28T12:06:00Z"))
        invoke("DurableFabricStore.record_recovery_query", "append",
               lambda: recovery_store.record_recovery_query(
                   "lease-recovery", state="running", observed_at="2026-08-28T12:02:00Z",
                   controller_now="2026-08-28T12:02:00Z"))
        invoke("DurableFabricStore.accept_result", "append",
               lambda: result_store.accept_result(
                   attempt_id="lease-result-attempt", lease_id="lease-result",
                   assignment_digest_value=assignment.assignment_digest, result_digest="f" * 64,
                   status="succeeded", observed_at=NOW, controller_now="2026-08-28T12:01:00Z"))

        registry_holder: dict[str, fabric.VerificationKeyRegistry] = {}

        def provision_registry() -> None:
            registry_holder["registry"] = fabric.VerificationKeyRegistry.provision(
                root / "convergence-verifiers.json", authority_key_path=authority,
                verification_keys={"controller/verifier-one": "convergence-key"}, root=root)

        invoke("VerificationKeyRegistry.provision", "replace", provision_registry)
        registry = registry_holder["registry"]
        invoke("VerificationKeyRegistry.rotate", "replace",
               lambda: registry.rotate("controller/verifier-one", "convergence-rotated-key"))

        receipt_store = fabric.VerificationReceiptStore(
            root / "convergence-receipts.jsonl", root=root, verification_registry=registry)
        invoke("VerificationReceiptStore.issue", "append", lambda: receipt_store.issue(receipt))
        issued = receipt_store.get(receipt.receipt_id)
        if issued is None:
            raise AssertionError("convergence receipt was not issued")
        coordinator = fabric.IntegrationCoordinator(
            root / "convergence-integration.jsonl", root=root, receipt_store=receipt_store)
        invoke("IntegrationCoordinator.set_project_policy", "append",
               lambda: coordinator.set_project_policy(
                   project_id="project-one", default_branch="main", integration_branch="integration"))
        invoke("IntegrationCoordinator.admit", "append",
               lambda: coordinator.admit(
                   candidate_id="candidate-one", project_id="project-one", source_sha=SOURCE,
                   result_commit=RESULT, assignment=assignment, result_ref="cursor/candidate-one",
                   classification="current-compatible", verification_receipt=issued))
        invoke("IntegrationCoordinator.complete", "append",
               lambda: coordinator.complete("candidate-one"))

    labels = {label for label, _, _ in operations}
    if len(labels) != 14:
        raise AssertionError(f"production convergence covered {len(labels)} entry points, not 14")
    print(f"ok    production convergence: {len(labels)} entry points routed through shared commits "
          f"(append_calls={append_counts['calls']} replace_calls={replace_counts['calls']})")
    return len(labels)


def run_production_commit_races(root: Path) -> int:
    """Run shared-writer and absent-destination races from production callers."""
    root.mkdir(parents=True, exist_ok=True)
    host, _, _, _, _, assignment, _, _ = _records()

    # _replace_store_bytes: mutate the destination into an outside hardlink
    # after its first final-name probe, then require the production register
    # path to refuse before publishing.
    replace_case = root / "production-replace-race"
    replace_case.mkdir()
    outside_dir = replace_case / "outside"
    outside_dir.mkdir()
    outside = outside_dir / "outside.jsonl"
    outside.write_bytes(b"outside-before\n")
    registry_path = replace_case / "hosts.json"
    registry = fabric.DurableHostRegistry(registry_path, root=replace_case, now=NOW)
    registry.register(host)
    changed = host.to_dict()
    changed["host_id"] = "host-two"
    changed["registration_digest"] = fabric.digest_record(
        {key: value for key, value in changed.items() if key != "registration_digest"})
    replacement_host = fabric.HostRegistration.from_dict(changed)
    injected = False
    refused = False
    refusal_message = ""
    commit_called = False
    accepted = False
    original_revalidate = fabric._revalidate_destination

    def inject_replace(directory, candidate_path, *, expected_identity, must_exist):
        nonlocal injected
        result = original_revalidate(directory, candidate_path,
                                      expected_identity=expected_identity, must_exist=must_exist)
        if Path(candidate_path) == registry_path and not injected:
            registry_path.unlink()
            os.link(outside, registry_path)
            injected = True
        return result

    if os.name == "nt":
        original_commit = fabric._windows_replace_by_handle

        def observe_commit(*args, **kwargs):
            nonlocal commit_called
            commit_called = True
            return original_commit(*args, **kwargs)

        commit_context = patch.object(fabric, "_windows_replace_by_handle", side_effect=observe_commit)
    else:
        original_commit = fabric.os.replace

        def observe_commit(*args, **kwargs):
            nonlocal commit_called
            commit_called = True
            return original_commit(*args, **kwargs)

        commit_context = patch.object(fabric.os, "replace", side_effect=observe_commit)

    try:
        with patch.object(fabric, "_revalidate_destination", side_effect=inject_replace), commit_context:
            try:
                registry.register(replacement_host)
            except fabric.ReconciliationError as exc:
                refusal_message = str(exc)
                refused = (getattr(exc, "code", None) == "UNSAFE_STORE_PATH" and
                           ("identity" in str(exc) or "unique regular file" in str(exc)))
            else:
                accepted = True
        print(f"probe production _replace_store_bytes via DurableHostRegistry.register: "
              f"adversarial_condition_established={injected} accepted={accepted} refusal={refusal_message!r}")
        if not injected:
            raise AssertionError("production replace race did not arm; refusing verdict")
        if accepted:
            raise AssertionError("production replace race was accepted")
        if not refused:
            raise AssertionError("production replace race was not refused by identity/link-count binding")
        if commit_called:
            raise AssertionError("production replace race reached the atomic commit")
        if outside.read_bytes() != b"outside-before\n":
            raise AssertionError("production replace race touched outside bytes")
        print("ok    production _replace_store_bytes race: DurableHostRegistry.register refused before publish")
    finally:
        registry_path.unlink(missing_ok=True)

    # _append_bytes: the expiration journal append must reject the same
    # destination identity race before the replacement reaches the commit.
    append_case = root / "production-append-race"
    append_case.mkdir()
    outside_dir = append_case / "outside"
    outside_dir.mkdir()
    outside = outside_dir / "outside.jsonl"
    outside.write_bytes(b"outside-before\n")
    store_path = append_case / "fabric.jsonl"
    store = fabric.DurableFabricStore(store_path, root=append_case)
    store.create_lease(assignment, lease_id="lease-append-race", attempt_id="attempt-append-race",
                       remote_session_id="session-append-race", now=NOW,
                       expires_at="2026-08-28T12:05:00Z")
    injected = False
    refused = False
    refusal_message = ""
    commit_called = False
    accepted = False

    def inject_append(directory, candidate_path, *, expected_identity, must_exist):
        nonlocal injected
        result = original_revalidate(directory, candidate_path,
                                      expected_identity=expected_identity, must_exist=must_exist)
        if Path(candidate_path) == store_path and not injected:
            store_path.unlink()
            os.link(outside, store_path)
            injected = True
        return result

    if os.name == "nt":
        original_commit = fabric._windows_replace_by_handle

        def observe_commit(*args, **kwargs):
            nonlocal commit_called
            commit_called = True
            return original_commit(*args, **kwargs)

        commit_context = patch.object(fabric, "_windows_replace_by_handle", side_effect=observe_commit)
    else:
        original_commit = fabric.os.replace

        def observe_commit(*args, **kwargs):
            nonlocal commit_called
            commit_called = True
            return original_commit(*args, **kwargs)

        commit_context = patch.object(fabric.os, "replace", side_effect=observe_commit)

    try:
        with patch.object(fabric, "_revalidate_destination", side_effect=inject_append), commit_context:
            try:
                store.expire(now="2026-08-28T12:06:00Z")
            except fabric.ReconciliationError as exc:
                refusal_message = str(exc)
                refused = (getattr(exc, "code", None) == "UNSAFE_STORE_PATH" and
                           ("identity" in str(exc) or "unique regular file" in str(exc)))
            else:
                accepted = True
        print(f"probe production _append_bytes via DurableFabricStore.expire: "
              f"adversarial_condition_established={injected} accepted={accepted} refusal={refusal_message!r}")
        if not injected:
            raise AssertionError("production append race did not arm; refusing verdict")
        if accepted:
            raise AssertionError("production append race was accepted")
        if not refused:
            raise AssertionError("production append race was not refused by identity/link-count binding")
        if commit_called:
            raise AssertionError("production append race reached the atomic commit")
        if outside.read_bytes() != b"outside-before\n":
            raise AssertionError("production append race touched outside bytes")
        print("ok    production _append_bytes race: DurableFabricStore.expire refused before publish")
    finally:
        store_path.unlink(missing_ok=True)

    # Absent-destination arm: establish a competing create at os.link itself
    # and invoke the no-clobber path through create_lease.
    absent_case = root / "production-absent-race"
    absent_case.mkdir()
    outside_dir = absent_case / "outside"
    outside_dir.mkdir()
    outside = outside_dir / "outside.jsonl"
    outside.write_bytes(b"outside-before\n")
    absent_path = absent_case / "fabric.jsonl"
    absent_store = fabric.DurableFabricStore(absent_path, root=absent_case)
    injected = False
    refused = False
    accepted = False
    original_link = fabric.os.link

    def inject_absent(*args, **kwargs):
        nonlocal injected
        if not injected:
            original_link(outside, absent_path)
            injected = True
        return original_link(*args, **kwargs)

    try:
        with patch.object(fabric.os, "link", side_effect=inject_absent):
            try:
                absent_store.create_lease(
                    assignment, lease_id="lease-absent-race", attempt_id="attempt-absent-race",
                    remote_session_id="session-absent-race", now=NOW,
                    expires_at="2026-08-28T12:05:00Z")
            except fabric.ReconciliationError as exc:
                refused = (getattr(exc, "code", None) == "UNSAFE_STORE_PATH" and
                           str(exc) == "durable store destination appeared before commit")
            else:
                accepted = True
        print(f"probe production _commit_absent_leaf via DurableFabricStore.create_lease: "
              f"adversarial_condition_established={injected} accepted={accepted}")
        if not injected:
            raise AssertionError("production absent-destination race did not arm; refusing verdict")
        if accepted:
            raise AssertionError("production absent-destination race was accepted")
        if not refused:
            raise AssertionError("production absent-destination race was not refused by no-clobber guard")
        if outside.read_bytes() != b"outside-before\n":
            raise AssertionError("production absent-destination race touched outside bytes")
        print("ok    production absent-destination race: DurableFabricStore.create_lease refused competing create")
    finally:
        absent_path.unlink(missing_ok=True)

    return 3


def run_absent_destination_guard(root: Path) -> int:
    """Exercise the line-730 FileExistsError guard without its outer fallback."""
    root.mkdir(parents=True, exist_ok=True)
    temporary = root / "temporary.jsonl"
    destination = root / "destination.jsonl"
    temporary.write_bytes(b"temporary\n")
    with fabric._pin_store_directory(root) as directory:
        with patch.object(fabric.os, "link", side_effect=FileExistsError("synthetic competing create")):
            try:
                fabric._commit_absent_leaf(directory, temporary, destination, object(), object())
            except fabric.ReconciliationError as exc:
                if (getattr(exc, "code", None) != "UNSAFE_STORE_PATH" or
                        str(exc) != "durable store destination appeared before commit"):
                    raise AssertionError(f"absent-destination guard produced unexpected refusal: {exc}") from exc
            except FileExistsError as exc:
                raise AssertionError("absent-destination guard leaked the competing-create error") from exc
            else:
                raise AssertionError("absent-destination guard accepted a competing create")
    print("ok    absent destination guard: line-730 competing-create marker was produced directly")
    return 1


def run_absent_destination_race(root: Path) -> int:
    """Prove an absent destination cannot be replaced after a competing create."""
    root.mkdir(parents=True, exist_ok=True)
    for mode in ("append", "replace"):
        _run_case(root / f"{mode}-race-absent", mode, "race-absent")
    print("ok    absent destination race: atomic no-clobber commit refused competing create")
    return 2


def run_registry_boundaries(root: Path) -> int:
    """Keep key encoding and verifier identity checks sensitive in runtime and schema."""
    root.mkdir(parents=True, exist_ok=True)
    schema_path = Path(__file__).resolve().parents[2] / "schemas" / "control-plane" / "v1" / "execution-fabric.schema.json"
    validator = _stock_validator(json.loads(schema_path.read_text(encoding="utf-8")))
    mutations = (("key-hex", "key_hex", "AA"), ("verifier-identity", "verifier_identity", "controller/\n"))
    checked = 0
    for label, field, value in mutations:
        case = root / label; case.mkdir()
        authority = case / "authority.key"; authority.write_bytes(b"authority")
        if os.name != "nt":
            authority.chmod(0o600)
        registry = fabric.VerificationKeyRegistry.provision(
            case / "verifiers.json", authority_key_path=authority,
            verification_keys={"controller/verifier-one": "test-key"}, root=case)
        state = json.loads(registry.path.read_text(encoding="utf-8"))
        state["keys"][0][field] = value
        state["registry_digest"] = fabric.digest_record({key: state[key] for key in
                                                           state if key not in {"registry_digest", "authentication_tag"}})
        state["authentication_tag"] = hmac.new(
            b"authority", state["registry_digest"].encode(), hashlib.sha256).hexdigest()
        registry.path.write_text(json.dumps(state), encoding="utf-8")
        if validator.is_valid(state):
            raise AssertionError(f"{label} schema accepted invalid registry state")
        try:
            registry.reload()
        except fabric.FabricError as exc:
            if label == "key-hex" and getattr(exc, "code", None) != "INVALID_FIELD":
                raise AssertionError(f"{label} runtime produced {exc.code}, not INVALID_FIELD")
            if label == "verifier-identity" and getattr(exc, "code", None) != "VERIFIER_UNTRUSTED":
                raise AssertionError(f"{label} runtime produced {exc.code}, not VERIFIER_UNTRUSTED")
        else:
            raise AssertionError(f"{label} runtime accepted invalid registry state")
        checked += 1
        print(f"ok    registry {label}: schema and runtime rejected {value!r}")

    retired_case = root / "retired-key-hex"
    retired_case.mkdir()
    authority = retired_case / "authority.key"
    authority.write_bytes(b"authority")
    if os.name != "nt":
        authority.chmod(0o600)
    retired_registry = fabric.VerificationKeyRegistry.provision(
        retired_case / "verifiers.json", authority_key_path=authority,
        verification_keys={"controller/verifier-one": "test-key"}, root=retired_case)
    retired_registry.rotate("controller/verifier-one", "rotated-key")
    state = json.loads(retired_registry.path.read_text(encoding="utf-8"))
    state["retired_keys"][0]["key_hex"] = "AA"
    state["registry_digest"] = fabric.digest_record({key: state[key] for key in
                                                       state if key not in {"registry_digest", "authentication_tag"}})
    state["authentication_tag"] = hmac.new(
        b"authority", state["registry_digest"].encode(), hashlib.sha256).hexdigest()
    retired_registry.path.write_text(json.dumps(state), encoding="utf-8")
    if validator.is_valid(state):
        raise AssertionError("retired-key-hex schema accepted invalid registry state")
    try:
        retired_registry.reload()
    except fabric.FabricError as exc:
        if getattr(exc, "code", None) != "INVALID_FIELD":
            raise AssertionError(
                f"retired-key-hex runtime produced {exc.code}, not INVALID_FIELD")
    else:
        raise AssertionError("retired-key-hex runtime accepted invalid registry state")
    checked += 1
    print("ok    registry retired-key-hex: schema and runtime rejected 'AA'")
    return checked


def run_placement_boundaries() -> int:
    """Exercise every caller-controlled placement container and identity binding."""
    host, heartbeat, pool, requirements, candidate, _, _, _ = _records()
    values = {
        "candidates": None,
        "hosts": [],
        "heartbeats": [],
        "pools": [],
    }
    checked = 0
    for field, value in values.items():
        kwargs = {
            "requirements": requirements, "candidates": [candidate],
            "hosts": {host.host_id: host}, "heartbeats": {host.host_id: heartbeat},
            "pools": {pool.pool_id: pool}, "now_epoch": 1787918400, "created_at": NOW,
        }
        kwargs[field] = value
        try:
            fabric.resolve_placement(**kwargs)
        except fabric.FabricError as exc:
            if getattr(exc, "code", None) != "INVALID_FIELD":
                raise AssertionError(f"placement {field} produced {exc.code}, not INVALID_FIELD")
        except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError, OSError, AttributeError) as exc:
            raise AssertionError(f"placement {field} leaked {type(exc).__name__}") from exc
        else:
            raise AssertionError(f"placement {field} accepted malformed container")
        checked += 1
    identity_cases = (
        ("hosts", {"host-alias": host}, {host.host_id: heartbeat}, {pool.pool_id: pool}, candidate),
        ("heartbeats", {host.host_id: host}, {"host-alias": heartbeat}, {pool.pool_id: pool}, candidate),
        ("pools", {host.host_id: host}, {host.host_id: heartbeat}, {"pool-alias": pool}, candidate),
    )
    for field, hosts, heartbeats, pools, selected in identity_cases:
        if field == "hosts":
            selected = fabric.PlacementCandidate.from_dict({**candidate.to_dict(), "host_id": "host-alias"})
            heartbeats = {"host-alias": heartbeat}
        try:
            fabric.resolve_placement(requirements, [selected], hosts, heartbeats, pools,
                                     now_epoch=1787918400, created_at=NOW)
        except fabric.SchemaError as exc:
            if getattr(exc, "code", None) != "IDENTITY_MISMATCH":
                raise AssertionError(f"placement {field} produced {exc.code}, not IDENTITY_MISMATCH")
        else:
            raise AssertionError(f"placement {field} accepted a mismatched registry key")
        checked += 1
    try:
        fabric.resolve_placement(requirements, [candidate], {host.host_id: host},
                                 {host.host_id: heartbeat}, {pool.pool_id: pool},
                                 now_epoch=1787918400, created_at=NOW, pause_guard=True)
    except fabric.FabricError as exc:
        if (getattr(exc, "code", None) != "INVALID_INPUT" or
                str(exc) != "invalid placement input" or os.path.isabs(str(exc)) or exc.__cause__ is not None):
            raise AssertionError(f"pause_guard wrong type produced {exc.code}, not INVALID_INPUT")
    except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError, OSError, AttributeError) as exc:
        raise AssertionError(f"pause_guard wrong type leaked {type(exc).__name__}") from exc
    else:
        raise AssertionError("pause_guard wrong type was accepted")
    checked += 1
    internal_typo = "synthetic internal typo"
    with patch.object(fabric, "_candidate_sort_key", side_effect=AttributeError(internal_typo)):
        try:
            fabric.resolve_placement(requirements, [candidate], {host.host_id: host},
                                     {host.host_id: heartbeat}, {pool.pool_id: pool},
                                     now_epoch=1787918400, created_at=NOW)
        except AttributeError as exc:
            if str(exc) != internal_typo:
                raise AssertionError(f"internal AttributeError was changed: {exc}") from exc
        except fabric.FabricError as exc:
            raise AssertionError(
                f"internal AttributeError was masked as a typed refusal ({exc.code})") from exc
        else:
            raise AssertionError("synthetic internal AttributeError was swallowed")
    checked += 1
    assignment, _ = fabric.resolve_placement(
        requirements, [candidate], {host.host_id: host}, {host.host_id: heartbeat}, {pool.pool_id: pool},
        now_epoch=1787918400, created_at=NOW, pause_guard=fabric.PauseGuard(False))
    if assignment is None:
        raise AssertionError("legitimate open pause_guard blocked placement")
    checked += 1
    print(f"ok    placement boundary matrix: {checked} malformed/mismatched containers rejected; internal AttributeError propagated")
    return checked


def run_positive_controls(root: Path) -> int:
    root.mkdir(parents=True, exist_ok=True)
    host, heartbeat, pool, requirements, candidate, assignment, receipt, policy = _records()
    fabric_path = root / "positive-fabric.jsonl"
    fabric_store = fabric.DurableFabricStore(fabric_path, root=root)
    fabric_store.create_lease(assignment, lease_id="lease-positive", attempt_id="attempt-positive",
                              remote_session_id="session-positive", now=NOW,
                              expires_at="2026-08-28T12:05:00Z")
    _assert_handles_released(fabric_path, fabric_store.lock_path, "lease creation")

    authority = root / "positive-authority.key"
    authority.write_bytes(b"controller-authority-test-key")
    if os.name != "nt":
        authority.chmod(0o600)
    verifier_path = root / "positive-verifiers.json"
    registry = fabric.VerificationKeyRegistry.provision(
        verifier_path, authority_key_path=authority,
        verification_keys={"controller/verifier-one": "test-key"}, root=root)
    registry.rotate("controller/verifier-two", "rotated-key")

    host_registry = fabric.DurableHostRegistry(root / "positive-hosts.json", root=root, now=NOW)
    host_registry.register(host)
    host_registry.heartbeat(heartbeat, now=NOW)

    receipts = fabric.VerificationReceiptStore(root / "positive-receipts.jsonl", root=root,
                                               verification_registry=registry)
    receipts.issue(receipt)
    registry.rotate("controller/verifier-one", "rotated-verifier-key")
    schema_path = Path(__file__).resolve().parents[2] / "schemas" / "control-plane" / "v1" / "execution-fabric.schema.json"
    _stock_validator(json.loads(schema_path.read_text(encoding="utf-8"))).validate(
        json.loads(verifier_path.read_text(encoding="utf-8")))
    if receipts.get(receipt.receipt_id) is None:
        raise AssertionError("rotated-out receipt was not verifiable from retired key history")
    coordinator = fabric.IntegrationCoordinator(root / "positive-integration.jsonl", root=root,
                                                receipt_store=receipts)
    coordinator.set_project_policy(project_id="project-one", default_branch="main",
                                   integration_branch="integration")
    coordinator.admit(candidate_id="candidate-one", project_id="project-one", source_sha=SOURCE,
                      result_commit=RESULT, assignment=assignment,
                      result_ref="cursor/candidate-one", classification="current-compatible",
                      verification_receipt=receipts.get(receipt.receipt_id))
    _assert_handles_released(verifier_path, registry.lock_path, "verification registry write")
    _assert_handles_released(receipts.path, receipts.lock_path, "receipt issue")
    _assert_handles_released(host_registry.path, host_registry.lock_path, "host-registry update")
    _assert_handles_released(coordinator.path, coordinator.lock_path, "integration journal append")
    absent = root / "positive-absent-replace.jsonl"
    fabric._replace_store_bytes(absent, b"absent-destination\n", expected_identity=None)
    if absent.read_bytes() != b"absent-destination\n":
        raise AssertionError("absent destination positive replace did not publish exact bytes")
    _assert_handles_released(absent, root / "positive-absent-replace.jsonl.lock", "absent-destination replace")
    print("ok    positive controls: lease, host registry, verifier registry, receipt, integration, absent replace")
    return 6


def main() -> int:
    requested = os.environ.get("CODEX_W8F_SCRATCH")
    scratch = Path(requested) if requested else Path(tempfile.gettempdir()) / ("codex-w8f-" + uuid.uuid4().hex)
    scratch.mkdir(parents=True, exist_ok=True)
    run_root = scratch / ("writer-sweep-" + uuid.uuid4().hex)
    run_root.mkdir()
    try:
        differential = run_differential()
        hostile = run_hostile_inputs(run_root / "inputs")
        placement = run_placement_boundaries()
        registry = run_registry_boundaries(run_root / "registry")
        shared = run_shared_battery(run_root / "shared")
        isolated_reparse = run_isolated_windows_reparse_guard(run_root / "isolated-reparse")
        absent_guard = run_absent_destination_guard(run_root / "absent-guard")
        absent_race = run_absent_destination_race(run_root / "absent-race")
        posix = run_posix_source_race(run_root / "posix")
        convergence = run_production_writer_convergence(run_root / "production-convergence")
        production_races = run_production_commit_races(run_root / "production-races")
        positive = run_positive_controls(run_root / "positive")
        print(f"phase8-durable-writer-sweep: PASS differential={differential} hostile={hostile} placement={placement} registry={registry} shared={shared} isolated_reparse={isolated_reparse} absent_guard={absent_guard} absent_race={absent_race} posix={posix} convergence={convergence} production_races={production_races} positive={positive}")
        return 0
    finally:
        # Only this harness-owned child is cleaned.  The caller-owned scratch
        # directory itself is removed by the author after all verification.
        try:
            shutil.rmtree(run_root)
        except (PermissionError, OSError):
            pass


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PermissionError as exc:
        if getattr(exc, "winerror", None) == 5 or getattr(exc, "errno", None) == 5 or os.name != "nt":
            print(f"phase8-durable-writer-sweep: SKIP (host ACL prevents explicit temp fixture: {exc})")
            raise SystemExit(77)
        raise
    except OSError as exc:
        if getattr(exc, "winerror", None) == 5 or getattr(exc, "errno", None) == 5:
            print(f"phase8-durable-writer-sweep: SKIP (host ACL prevents explicit temp fixture: {exc})")
            raise SystemExit(77)
        raise
