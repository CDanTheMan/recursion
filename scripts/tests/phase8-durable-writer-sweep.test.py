#!/usr/bin/env python3
"""Phase 8 class sweep for durable writers, hostile inputs, and schema parity.

The harness intentionally uses one caller-owned directory under the system temp
directory.  It does not use TemporaryDirectory because the Windows test host
may deny cleanup of directories held by native directory handles.
"""

from __future__ import annotations

import copy
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

try:
    import jsonschema
    from jsonschema import Draft202012Validator, validators
except ImportError as exc:  # pragma: no cover - environment prerequisite
    print(f"phase8-durable-writer-sweep: SKIP (jsonschema unavailable: {exc})")
    raise SystemExit(77)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import execution_fabric as fabric  # noqa: E402


NOW = "2026-08-28T12:00:00Z"
SOURCE = "a" * 40
RESULT = "b" * 40


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


def _strict_validator(schema: dict) -> Draft202012Validator:
    """Apply the runtime's exact Python numeric policy to JSON Schema types."""
    checker = Draft202012Validator.TYPE_CHECKER.redefine_many({
        "integer": lambda _checker, value: type(value) is int,
        "number": lambda _checker, value: (type(value) in {int, float} and
                                            math.isfinite(value) if type(value) is float else type(value) is int),
    })
    strict_class = validators.extend(Draft202012Validator, type_checker=checker)
    return strict_class(schema)


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
    validator = _strict_validator(schema)
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
    mismatches: list[str] = []
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
            mismatches.append(f"{kind}.{field}: raw runtime exception {type(exc).__name__}")
            runtime_ok = False
        else:
            runtime_ok = True
        if schema_ok != runtime_ok:
            mismatches.append(f"{kind}.{field}={value!r}: schema={schema_ok} runtime={runtime_ok}")
    if mismatches:
        raise AssertionError("schema/runtime mismatches:\n" + "\n".join(mismatches))
    print(f"ok    CLASS D differential: {len(cases)} constrained mutations, zero mismatches/raw exceptions")
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
    elif hostile == "absent":
        pass
    elif hostile is None:
        path.write_bytes(b"inside-before\n")
    else:
        raise AssertionError(hostile)

    before = outside.read_bytes()
    try:
        _writer(mode, path, root)
    except fabric.FabricError:
        if hostile in {None, "absent"}:
            raise
    except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError, OSError) as exc:
        raise AssertionError(f"{mode}/{hostile} leaked {type(exc).__name__}") from exc
    else:
        if hostile not in {None, "absent"}:
            raise AssertionError(f"{mode}/{hostile} was accepted")
    if outside.read_bytes() != before:
        raise AssertionError(f"{mode}/{hostile} touched bytes outside root")


def run_shared_battery(root: Path) -> int:
    cases = ("hardlink", "race-hardlink", "junction-leaf", "junction-ancestor", "junction-root", "absent")
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
        shared = run_shared_battery(run_root / "shared")
        positive = run_positive_controls(run_root / "positive")
        print(f"phase8-durable-writer-sweep: PASS differential={differential} hostile={hostile} shared={shared} positive={positive}")
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
