#!/usr/bin/env python3
"""Hermetic controls for usage-reconcile.py's Phase 3 (D-016) additions:

  - normalize() carries capacity_pool/host/assignment_digest straight off the run record,
    and prefers a record-level `provider` (assignment-native) over usage.provider (legacy
    worker-declared) without breaking a record that only ever had the latter.
  - the new `quota` subcommand reconciles ledger usage against a capacity pool's declared
    quota period (within-limit / exceeded / no-limit-declared / unmeasurable), fail-closed
    on an unknown or malformed pool.

Runs the real CLI as a subprocess against disposable tempdirs; nothing touches the live
repo's state/.
"""

from __future__ import annotations

import datetime
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
SCRIPTS = SOURCE / "scripts"
USAGE_RECONCILE = SCRIPTS / "usage-reconcile.py"

sys.path.insert(0, str(SCRIPTS))
from jsonl_durable import read_jsonl_objects  # noqa: E402
import assignment as amod  # noqa: E402

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(USAGE_RECONCILE), *args], capture_output=True, text=True)


def iso_week_of(date: datetime.date) -> str:
    year, week, _ = date.isocalendar()
    return f"{year:04d}-W{week:02d}"


FIXED_DATE = datetime.date(2026, 8, 28)
FIXED_TS = f"{FIXED_DATE.isoformat()}T12:00:00Z"
FIXED_WEEK = iso_week_of(FIXED_DATE)


def evidence(run_id: str, task_id: str, *, engine=None, provider=None, capacity_pool=None,
             host=None, assignment_digest=None, usage_provider=None, cost_usd=0.0, tokens=0,
             billing_basis="metered", evidence_source="receipt-v1") -> dict:
    value = {
        "schema_version": 1, "id": run_id, "task_id": task_id, "role": "implementer",
        "model_alias": "sonnet-routine", "status": "succeeded", "outcome": "worker-complete",
        "started_at": FIXED_TS, "finished_at": FIXED_TS,
        "usage": {"provider": usage_provider, "billing_basis": billing_basis,
                  "tokens": tokens, "cost_usd": cost_usd, "evidence_source": evidence_source},
    }
    for key, item in (("engine", engine), ("provider", provider), ("capacity_pool", capacity_pool),
                      ("host", host), ("assignment_digest", assignment_digest)):
        if item is not None:
            value[key] = item
    return value


def persist_assignment(root: Path, task_id: str, *, provider: str, pool: str | None,
                       billing: str = "metered", engine: str = "cursor") -> str:
    value = amod.resolve_assignment(
        task_id=task_id, project_id="project", role="implementer", source_repository="/repo",
        source_branch="main", source_sha="a" * 40, engine=engine,
        provider=provider, capacity_pool=pool, billing_basis=billing,
        metered_approved=(billing == "metered"), host="gs-recursion",
        sandbox_profile="strict-linux", network_profile="provider-only", allowed_paths=["app"],
        publication_policy="verified-integration-only", created_at="2026-08-24T00:00:00Z",
        capacity_pool_dir=root / "pools",
    )
    amod.persist_assignment(root / "assignments", value)
    return value["assignment_digest"]


def test_normalize_provider_preference(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    ledger = tmp_path / "ledger.jsonl"
    write_pool(tmp_path / "pools", "pool-a", limit=100, unit="usd")
    digest = persist_assignment(tmp_path, "task-a", provider="cursor", pool="pool-a", billing="metered")

    (runs_dir / "a.json").write_text(json.dumps(evidence(
        "run-a", "task-a", engine="hermes", provider="cursor",
        capacity_pool="pool-a", host="gs-recursion", assignment_digest=digest,
        usage_provider="cursor", cost_usd=1.0, tokens=100,
    )), encoding="utf-8")
    (runs_dir / "b.json").write_text(json.dumps(evidence(
        "run-b", "task-b", usage_provider="anthropic-claude-code", cost_usd=2.0, tokens=200,
    )), encoding="utf-8")

    result = run(["ingest", "--runs-dir", str(runs_dir), "--ledger", str(ledger)])
    check(result.returncode == 0, f"ingest exits 0 (got {result.returncode}, stderr={result.stderr!r})")
    rows = {row["run_id"]: row for row in read_jsonl_objects(ledger) if row.get("record") == "run"}

    row_a = rows.get("run-a", {})
    check(row_a.get("provider") == "cursor",
          "an assignment-native record's provider is loaded from the persisted assignment")
    check(row_a.get("capacity_pool") == "pool-a", "normalize() carries capacity_pool through")
    check(row_a.get("host") == "gs-recursion", "normalize() carries host through")
    check(row_a.get("assignment_digest") == digest, "normalize() carries assignment_digest through")
    check(row_a.get("engine") == "cursor", "normalize() derives engine from the persisted assignment")

    row_b = rows.get("run-b", {})
    check(row_b.get("provider") == "anthropic-claude-code",
          "a legacy record (no record-level provider) still falls back to usage.provider")
    check(row_b.get("capacity_pool") is None, "a legacy record has no capacity_pool")
    check(row_b.get("assignment_digest") is None, "a legacy record has no assignment_digest")


def write_pool(pool_dir: Path, pool_id: str, *, limit, unit, period="weekly", on_demand=False) -> None:
    pool_dir.mkdir(parents=True, exist_ok=True)
    (pool_dir / f"{pool_id}.json").write_text(json.dumps({
        "schema_version": 1, "id": pool_id, "kind": "subscription", "billing_basis": "metered",
        "provider": "cursor", "quota": {"period": period, "source": "declared",
                                        "limit": limit, "unit": unit},
        "on_demand": on_demand,
    }), encoding="utf-8")


def test_quota_within_and_exceeded(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"; runs_dir.mkdir()
    ledger = tmp_path / "ledger.jsonl"
    pool_dir = tmp_path / "pools"
    write_pool(pool_dir, "pool-b", limit=10.0, unit="usd")
    digest = persist_assignment(tmp_path, "task-q", provider="cursor", pool="pool-b")
    (runs_dir / "a.json").write_text(json.dumps(evidence(
        "run-q1", "task-q", capacity_pool="pool-b", cost_usd=3.0, tokens=100,
        usage_provider="cursor", assignment_digest=digest,
    )), encoding="utf-8")
    run(["ingest", "--runs-dir", str(runs_dir), "--ledger", str(ledger)])

    write_pool(pool_dir, "pool-b", limit=10.0, unit="usd")
    within = run(["quota", "--pool-id", "pool-b", "--capacity-pool-dir", str(pool_dir),
                 "--ledger", str(ledger), "--period", FIXED_WEEK])
    check(within.returncode == 0, f"quota exits 0 for a valid pool (got {within.returncode}, stderr={within.stderr!r})")
    report = json.loads(within.stdout)
    check(report.get("status") == "within-limit", f"3.0 usd consumed against a 10.0 usd limit is within-limit (got {report.get('status')})")
    check(report.get("consumed") == 3.0, "quota report sums cost_usd for the matching pool/period")

    write_pool(pool_dir, "pool-b", limit=2.0, unit="usd")
    exceeded = run(["quota", "--pool-id", "pool-b", "--capacity-pool-dir", str(pool_dir),
                   "--ledger", str(ledger), "--period", FIXED_WEEK])
    exceeded_report = json.loads(exceeded.stdout)
    check(exceeded_report.get("status") == "exceeded", f"3.0 usd consumed against a 2.0 usd limit is exceeded (got {exceeded_report.get('status')})")
    check(exceeded_report.get("on_demand_required") is True,
          "an exceeded pool with on_demand=false reports on_demand_required")


def test_quota_no_limit_and_unmeasurable(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"; runs_dir.mkdir()
    ledger = tmp_path / "ledger.jsonl"
    pool_dir = tmp_path / "pools"
    write_pool(pool_dir, "pool-c", limit=None, unit=None)
    digest = persist_assignment(tmp_path, "task-q2", provider="cursor", pool="pool-c")
    (runs_dir / "a.json").write_text(json.dumps(evidence(
        "run-q2", "task-q2", capacity_pool="pool-c", cost_usd=1.0, tokens=10, usage_provider="cursor",
        assignment_digest=digest,
    )), encoding="utf-8")
    run(["ingest", "--runs-dir", str(runs_dir), "--ledger", str(ledger)])

    write_pool(pool_dir, "pool-c", limit=None, unit=None)
    no_limit = run(["quota", "--pool-id", "pool-c", "--capacity-pool-dir", str(pool_dir),
                   "--ledger", str(ledger), "--period", FIXED_WEEK])
    check(json.loads(no_limit.stdout).get("status") == "no-limit-declared",
          "a pool with no declared limit is informational only")

    write_pool(pool_dir, "pool-c", limit=5.0, unit="widgets")
    unmeasurable = run(["quota", "--pool-id", "pool-c", "--capacity-pool-dir", str(pool_dir),
                       "--ledger", str(ledger), "--period", FIXED_WEEK])
    check(json.loads(unmeasurable.stdout).get("status") == "unmeasurable",
          "a declared limit against a unit this tool cannot meter is never silently 'within-limit'")


def test_quota_unknown_pool_fails_closed(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    pool_dir = tmp_path / "pools"; pool_dir.mkdir()
    result = run(["quota", "--pool-id", "does-not-exist", "--capacity-pool-dir", str(pool_dir),
                 "--ledger", str(ledger)])
    check(result.returncode == 2, f"an unknown capacity pool fails closed with exit 2 (got {result.returncode})")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        test_normalize_provider_preference(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_quota_within_and_exceeded(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_quota_no_limit_and_unmeasurable(Path(tmp))
    with tempfile.TemporaryDirectory() as tmp:
        test_quota_unknown_pool_fails_closed(Path(tmp))

    if failures:
        print(f"usage-reconcile-quota.test: {len(failures)} FAILED")
        return 1
    print("usage-reconcile-quota.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
