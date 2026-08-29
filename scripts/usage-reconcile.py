#!/usr/bin/env python3
"""Per-run usage/cost telemetry for engine arms (D-015 follow-on).

Normalizes the controller's per-run usage evidence into an append-only ledger, then
rolls it up weekly. The load-bearing output is not the total: it is the honest split
between cost we have a provider receipt for, cost that is only a controller policy
declaration, and cost we cannot ground at all. Cursor and the other metered plugin
engines emit no programmatic receipt today, so their real spend is UNKNOWN -- making
that gap visible is the point (it informs the September subscription decision).

Never estimates. A run without groundable numbers is reported as unreconciled, never
as zero.

Exit codes: 0 ok; 1 runtime failure (unreadable input, network/parse failure);
2 usage error (bad arguments, unusable ledger); 3 disabled (opt-in gate off or
credential absent -- mirrors resolve-engine.py's "human-owned mapping absent").
"""

from __future__ import annotations

import argparse
import calendar
import datetime
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from jsonl_durable import JsonlDurabilityError, append_jsonl, read_jsonl_objects
import assignment as assignment_mod

PROG = "usage-reconcile"
LEDGER_SCHEMA_VERSION = 1

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS_DIR = ROOT / "state" / "runs"
DEFAULT_LEDGER = ROOT / "state" / "usage" / "ledger.jsonl"
DEFAULT_REPORT_DIR = ROOT / "state" / "reports"

ENGINE_RE = re.compile(r"[a-z][a-z0-9-]{1,31}")
WEEK_RE = re.compile(r"[0-9]{4}-W[0-9]{2}")
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

ROLES = {"implementer", "verifier"}
BILLING_BASES = {"flat-subscription", "metered", "local"}

# Sources the controller writes itself (work.sh). They declare the manifest's billing
# policy; they are NOT provider receipts, so their tokens/cost_usd of 0 mean "policy says
# this run has no separately-billed marginal cost", not "we measured zero".
POLICY_RECORD_SOURCES = {"controller-engine-policy-v1", "engine-manifest-v1"}

# Provider receipt names are an allowlist, not a heuristic.  A usage file can be edited by
# the worker, so an arbitrary nonempty evidence_source is never enough to call its numbers
# grounded provider spend.  ``receipt-v1`` is the controller's generic provider-receipt
# profile; engine-specific sources are derived below from the trusted engine manifests.
GENERIC_PROVIDER_RECEIPT_SOURCE = "receipt-v1"

# The only provider->engine pair not derivable from a manifest (claude is a builtin).
BUILTIN_PROVIDER_ENGINES = {"anthropic-claude-code": "claude"}

COST_BASES = ("receipt", "policy-record", "unreconciled")

OPENROUTER_CREDITS_URL = "https://openrouter.ai/api/v1/credits"
SNAPSHOT_TIMEOUT_S = 15
SNAPSHOT_MAX_BYTES = 1 << 20

# One page, hard cap (CLAUDE.md "Bounded output"). Rows beyond the budget are dropped
# with an explicit count -- never appended.
REPORT_MAX_LINES = 60
REPORT_MAX_GROUP_ROWS = 18


class UsageError(Exception):
    """Arguments or on-disk inputs the tool refuses to guess past (exit code 2)."""


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def now_iso() -> str:
    return time.strftime(TS_FORMAT, time.gmtime())


def plain_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def plain_number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def nonempty_str(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def epoch_of(value: object) -> int | None:
    text = nonempty_str(value)
    if text is None:
        return None
    try:
        return calendar.timegm(time.strptime(text, TS_FORMAT))
    except ValueError:
        return None


def iso_week(struct: time.struct_time) -> str:
    year, week, _ = datetime.date(struct.tm_year, struct.tm_mon, struct.tm_mday).isocalendar()
    return f"{year:04d}-W{week:02d}"


def iso_week_of(value: object) -> str | None:
    epoch = epoch_of(value)
    return None if epoch is None else iso_week(time.gmtime(epoch))


# --- quota-period reconciliation (Phase 3, D-016) ---------------------------------------
# A capacity pool's quota resets on its own declared cadence (daily/weekly/monthly), never
# on the reporting ISO-week bucket above -- those are two independent concepts that happen
# to share a "week" case.

def period_key(period: str, struct: time.struct_time) -> str:
    if period == "daily":
        return time.strftime("%Y-%m-%d", struct)
    if period == "monthly":
        return time.strftime("%Y-%m", struct)
    return iso_week(struct)


def period_key_of(period: str, value: object) -> str | None:
    epoch = epoch_of(value)
    return None if epoch is None else period_key(period, time.gmtime(epoch))


def current_period_key(period: str) -> str:
    return period_key(period, time.gmtime())


def current_iso_week() -> str:
    return iso_week(time.gmtime())


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, str(path))
    finally:
        if os.path.exists(name):
            os.unlink(name)


# --- engine derivation ------------------------------------------------------------------
# The run-evidence schema (worker-evidence.py) records role and model_alias but NOT the
# engine, so the engine name is reconstructed from the usage record's provider via the
# shipped manifests. A provider claimed by two manifests is ambiguous and resolves to
# "unknown" rather than to a guess.

def manifest_dir() -> Path:
    override = os.environ.get("RECURSION_ENGINE_DIR", "").strip()
    return Path(override) if override else Path(__file__).resolve().parent / "engines"


def provider_engine_map() -> dict:
    mapping: dict[str, str | None] = {}
    directory = manifest_dir()
    try:
        candidates = sorted(directory.glob("*.json"))
    except OSError:
        return mapping
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        name = nonempty_str(data.get("name"))
        billing = data.get("billing")
        provider = nonempty_str(billing.get("provider")) if isinstance(billing, dict) else None
        if name is None or provider is None or not ENGINE_RE.fullmatch(name):
            continue  # model-aliases.json and any non-manifest JSON land here
        if provider in mapping and mapping[provider] != name:
            mapping[provider] = None  # claimed by two manifests: ambiguous, never guessed
        else:
            mapping.setdefault(provider, name)
    return mapping


def derive_engine(record: dict, usage: dict, provider: str | None, mapping: dict) -> str:
    for candidate in (record.get("engine"), usage.get("engine")):
        text = nonempty_str(candidate)
        if text is not None and ENGINE_RE.fullmatch(text):
            return text
    if provider is not None:
        builtin = BUILTIN_PROVIDER_ENGINES.get(provider)
        if builtin is not None:
            return builtin
        resolved = mapping.get(provider)
        if resolved is not None:
            return resolved
    return "unknown"


# --- normalization ----------------------------------------------------------------------

def looks_like_evidence(data: object) -> bool:
    """Discriminate run-evidence records from the scope/result/seed/plan JSON alongside them."""
    return isinstance(data, dict) and "id" in data and "task_id" in data


def classify_cost(usage: dict) -> tuple[int | None, float | None, str]:
    evidence_source = nonempty_str(usage.get("evidence_source"))
    basis = usage.get("billing_basis")
    if evidence_source is None or basis not in BILLING_BASES:
        return None, None, "unreconciled"
    tokens = plain_int(usage.get("tokens"))
    cost = plain_number(usage.get("cost_usd"))
    if tokens is None or cost is None:
        return None, None, "unreconciled"
    if evidence_source in POLICY_RECORD_SOURCES:
        return tokens, cost, "policy-record"
    provider = nonempty_str(usage.get("provider"))
    trusted_engines = provider_engine_map()
    trusted_engines.update(BUILTIN_PROVIDER_ENGINES)
    engine = trusted_engines.get(provider)
    allowed_sources = {GENERIC_PROVIDER_RECEIPT_SOURCE}
    if engine is not None:
        allowed_sources.add(f"{engine}-usage-v1")
    if basis == "metered" and engine is not None and evidence_source in allowed_sources:
        return tokens, cost, "receipt"
    return None, None, "unreconciled"


def normalize(record: dict, mapping: dict, assignment_root: Path | None = None) -> dict:
    usage = record.get("usage") if isinstance(record.get("usage"), dict) else {}
    assignment_record = None
    assignment_digest = nonempty_str(record.get("assignment_digest"))
    if assignment_digest:
        if assignment_root is None:
            raise UsageError("assignment-native run has no assignment root")
        assignment_record = assignment_mod.load_assignment(
            assignment_root, nonempty_str(record.get("task_id")) or "", assignment_digest)
        if assignment_record is None:
            raise UsageError(f"persisted assignment is absent for run {record.get('id')}")
        try:
            assignment_mod.validate_assignment(assignment_record, require_source_evidence=True)
        except assignment_mod.AssignmentError as exc:
            raise UsageError(f"persisted assignment is invalid for run {record.get('id')}: {exc}") from exc
        provider = assignment_record["provider"]
        basis = assignment_record.get("billing_basis")
        if record.get("task_id") != assignment_record["task_id"]:
            raise UsageError("run task_id does not match persisted assignment")
        if record.get("role") != assignment_record["role"]:
            raise UsageError("run role does not match persisted assignment")
        if usage.get("provider") not in (None, provider) or usage.get("billing_basis") not in (None, basis):
            raise UsageError("worker usage disagrees with persisted assignment")
        if basis == "metered" and not assignment_record.get("metered_approved"):
            raise UsageError("unapproved metered usage cannot be reconciled")
    else:
        # Versioned legacy compatibility: records written before Phase 3 retain their old
        # provider/engine join and are explicitly distinguishable from assignment-native rows.
        provider = nonempty_str(usage.get("provider"))
        basis = usage.get("billing_basis")
    tokens, cost, cost_basis = classify_cost(usage)
    role = record.get("role") if record.get("role") in ROLES else None
    started_at = nonempty_str(record.get("started_at"))
    finished_at = nonempty_str(record.get("finished_at"))
    start_epoch, finish_epoch = epoch_of(started_at), epoch_of(finished_at)
    wall = None
    if start_epoch is not None and finish_epoch is not None and finish_epoch >= start_epoch:
        wall = finish_epoch - start_epoch
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "record": "run",
        "run_id": record["id"],
        "task_id": nonempty_str(record.get("task_id")),
        "role": role,
        "engine": assignment_record["engine"] if assignment_record else derive_engine(record, usage, provider, mapping),
        "provider": provider,
        "capacity_pool": assignment_record.get("capacity_pool") if assignment_record else None,
        "host": assignment_record.get("host") if assignment_record else None,
        "assignment_digest": assignment_digest,
        "model_alias": nonempty_str(record.get("model_alias")),
        "model": assignment_record.get("model") if assignment_record else (nonempty_str(record.get("model")) or nonempty_str(record.get("resolved_model"))),
        "sandbox_profile": assignment_record.get("sandbox_profile") if assignment_record else None,
        "network_profile": assignment_record.get("network_profile") if assignment_record else None,
        "source_repository": assignment_record.get("source_repository") if assignment_record else None,
        "source_branch": assignment_record.get("source_branch") if assignment_record else None,
        "source_sha": assignment_record.get("source_sha") if assignment_record else None,
        "billing_basis": basis if basis in BILLING_BASES else None,
        "evidence_source": nonempty_str(usage.get("evidence_source")),
        "tokens": tokens,
        "cost_usd": cost,
        "cost_basis": cost_basis,
        "started_at": started_at,
        "finished_at": finished_at,
        "wall_seconds": wall,
        "status": nonempty_str(record.get("status")),
        "outcome": nonempty_str(record.get("outcome")),
    }


def evidence_files(runs_dir: Path) -> list:
    """Top-level run records plus one level of per-run evidence subdirectories."""
    found: list[Path] = []
    try:
        entries = sorted(runs_dir.iterdir())
    except OSError as exc:
        raise UsageError(f"cannot read runs directory {runs_dir}: {exc}") from exc
    for entry in entries:
        if entry.is_file() and entry.suffix == ".json":
            found.append(entry)
        elif entry.is_dir():
            try:
                found.extend(sorted(child for child in entry.iterdir()
                                    if child.is_file() and child.suffix == ".json"))
            except OSError:
                continue
    return found


def existing_run_ids(ledger: Path) -> set:
    try:
        rows = read_jsonl_objects(ledger)
    except JsonlDurabilityError as exc:
        raise UsageError(f"ledger is unusable: {exc}") from exc
    return {row["run_id"] for row in rows
            if isinstance(row, dict) and isinstance(row.get("run_id"), str)}


def command_ingest(args: argparse.Namespace) -> int:
    runs_dir, ledger = Path(args.runs_dir), Path(args.ledger)
    if not runs_dir.is_dir():
        diag(f"runs directory absent: {runs_dir}")
        return 2
    seen = existing_run_ids(ledger)
    mapping = provider_engine_map()
    counts = {"ingested": 0, "duplicate": 0, "incomplete": 0, "malformed": 0, "non-evidence": 0}

    for path in evidence_files(runs_dir):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            counts["malformed"] += 1
            diag(f"skipped unreadable evidence file: {path.name}")
            continue
        if not looks_like_evidence(data):
            counts["non-evidence"] += 1
            continue
        run_id = nonempty_str(data.get("id"))
        if run_id is None or nonempty_str(data.get("task_id")) is None \
                or plain_int(data.get("schema_version")) != 1:
            counts["malformed"] += 1
            diag(f"skipped evidence record with unusable identity: {path.name}")
            continue
        if nonempty_str(data.get("finished_at")) is None:
            counts["incomplete"] += 1  # still in flight; ingest only terminal runs
            continue
        if run_id in seen:
            counts["duplicate"] += 1
            continue
        try:
            assignment_root = runs_dir.parent / "assignments" if runs_dir.name != "runs" else runs_dir.parent / "assignments"
            outcome = append_jsonl(ledger, normalize(data, mapping, assignment_root),
                                   dedupe_field="run_id", dedupe_value=run_id)
        except JsonlDurabilityError as exc:
            diag(f"ledger append failed: {exc}")
            return 1
        seen.add(run_id)
        counts["ingested" if outcome.appended else "duplicate"] += 1

    print(f"{PROG}: " + " ".join(f"{key}={value}" for key, value in counts.items()))
    return 0


# --- rollup -----------------------------------------------------------------------------

def blank_totals() -> dict:
    return {"runs": 0, "tokens": 0, "cost_usd": 0.0,
            "by_basis": {basis: {"runs": 0, "tokens": 0, "cost_usd": 0.0} for basis in COST_BASES}}


def accumulate(bucket: dict, row: dict) -> None:
    basis = row["cost_basis"] if row.get("cost_basis") in COST_BASES else "unreconciled"
    bucket["runs"] += 1
    bucket["by_basis"][basis]["runs"] += 1
    if basis == "unreconciled":
        return  # tokens/cost are absent by construction; never add a stand-in zero
    tokens, cost = row.get("tokens") or 0, row.get("cost_usd") or 0.0
    bucket["tokens"] += tokens
    bucket["cost_usd"] += cost
    bucket["by_basis"][basis]["tokens"] += tokens
    bucket["by_basis"][basis]["cost_usd"] += cost


def valid_amount(value: object, allow_float: bool) -> bool:
    """True if *value* is absent (None), or a non-negative number of the allowed kind."""
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    if allow_float:
        return isinstance(value, (int, float)) and value >= 0
    return isinstance(value, int) and value >= 0


def ledger_row_is_corrupt(row: dict) -> bool:
    """A run row whose shape cannot be trusted for aggregation.

    The ledger is append-only and never rewritten, so one bad row must never crash the
    rollup or disable it permanently. tokens must be int>=0 (or absent); cost_usd must be
    int/float>=0 (or absent). A row that claims cost_basis "receipt" but is missing either
    number is not actually receipt-grade -- it must not be silently counted as $0.00 in the
    column the report presents as measured money.
    """
    tokens, cost = row.get("tokens"), row.get("cost_usd")
    if not valid_amount(tokens, allow_float=False):
        return True
    if not valid_amount(cost, allow_float=True):
        return True
    if row.get("cost_basis") == "receipt" and (tokens is None or cost is None):
        return True
    return False


def group_key(row: dict) -> str:
    return row.get("model") or row.get("model_alias") or "(no alias)"


def build_rollup(rows: list, week: str) -> dict:
    groups: dict[tuple, dict] = {}
    totals = blank_totals()
    snapshots = []
    outside = unbucketable = corrupt = 0
    valid_runs: list[dict] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("record") == "openrouter-snapshot":
            if iso_week_of(row.get("fetched_at")) == week:
                snapshots.append(row)
            continue
        if row.get("record") != "run":
            continue
        if ledger_row_is_corrupt(row):
            corrupt += 1  # shape failed validation -- skipped, never crashes, never a $0 receipt
            continue
        valid_runs.append(row)
        bucket = iso_week_of(row.get("finished_at")) or iso_week_of(row.get("started_at"))
        if bucket is None:
            unbucketable += 1
            continue
        if bucket != week:
            outside += 1
            continue
        key = (row.get("engine") or "unknown", group_key(row))
        accumulate(groups.setdefault(key, blank_totals()), row)
        accumulate(totals, row)

    # Metered arms whose only evidence is a controller declaration: the recorded 0 is a
    # policy statement, so their real spend is unknown. This is the gap the report exists
    # to surface.
    unreceipted: dict[str, int] = {}
    for row in valid_runs:
        if (iso_week_of(row.get("finished_at")) or iso_week_of(row.get("started_at"))) != week:
            continue
        if row.get("billing_basis") == "metered" and row.get("cost_basis") != "receipt":
            engine = row.get("engine") or "unknown"
            unreceipted[engine] = unreceipted.get(engine, 0) + 1

    ordered = sorted(groups.items(), key=lambda item: (-item[1]["cost_usd"], item[0]))
    return {
        "schema_version": LEDGER_SCHEMA_VERSION,
        "record": "usage-rollup",
        "week": week,
        "generated_at": now_iso(),
        "ledger_records": len(rows),
        "runs_outside_week": outside,
        "runs_unbucketable": unbucketable,
        "corrupt_ledger_rows": corrupt,
        "totals": totals,
        "groups": [{"engine": engine, "alias": alias, **values} for (engine, alias), values in ordered],
        "metered_without_receipt": dict(sorted(unreceipted.items())),
        "openrouter_snapshots": [
            {"fetched_at": snap.get("fetched_at"), "total_credits": snap.get("total_credits"),
             "total_usage": snap.get("total_usage")}
            for snap in sorted(snapshots, key=lambda snap: snap.get("fetched_at") or "")
        ],
    }


def money(value: float) -> str:
    return f"{value:.2f}"


def runs_of(count: int) -> str:
    return f"{count} run" if count == 1 else f"{count} runs"


def render_report(rollup: dict, ledger: Path) -> str:
    totals, basis = rollup["totals"], rollup["totals"]["by_basis"]
    lines = [
        f"# Usage — {rollup['week']}",
        "",
        f"Generated {rollup['generated_at']} by scripts/usage-reconcile.py from {ledger.as_posix()}.",
        "Evidence basis: per-run controller usage records under state/runs, normalized into the",
        "ledger. Nothing here is estimated. A run whose cost cannot be grounded is counted as",
        "unreconciled, never as zero.",
        "",
    ]
    if totals["runs"] == 0:
        lines += [
            "Runs in week: 0",
            "",
            "No run evidence for this week. That is an absence of records, not a statement that",
            "nothing ran — check state/runs and re-run `usage-reconcile.py ingest`.",
        ]
    else:
        lines += [
            f"Runs in week: {totals['runs']} "
            f"(ledger records {rollup['ledger_records']}, outside week {rollup['runs_outside_week']}, "
            f"undated {rollup['runs_unbucketable']})",
            "",
            f"{'engine / alias':<38}{'runs':>5}{'tokens':>10}{'cost_usd':>10}"
            f"{'rcpt':>6}{'plcy':>6}{'unrc':>6}",
            "-" * 81,
        ]
        shown = rollup["groups"][:REPORT_MAX_GROUP_ROWS]
        for group in shown:
            label = f"{group['engine']} / {group['alias']}"
            lines.append(
                f"{label[:37]:<38}{group['runs']:>5}{group['tokens']:>10}"
                f"{money(group['cost_usd']):>10}{group['by_basis']['receipt']['runs']:>6}"
                f"{group['by_basis']['policy-record']['runs']:>6}"
                f"{group['by_basis']['unreconciled']['runs']:>6}"
            )
        dropped = len(rollup["groups"]) - len(shown)
        if dropped:
            lines.append(f"({dropped} more group(s) omitted — full detail in the JSON beside this file)")
        lines += [
            "-" * 81,
            f"{'TOTAL':<38}{totals['runs']:>5}{totals['tokens']:>10}{money(totals['cost_usd']):>10}"
            f"{basis['receipt']['runs']:>6}{basis['policy-record']['runs']:>6}"
            f"{basis['unreconciled']['runs']:>6}",
            "",
            f"Cost by basis: receipted ${money(basis['receipt']['cost_usd'])} "
            f"({runs_of(basis['receipt']['runs'])}) | "
            f"policy-record ${money(basis['policy-record']['cost_usd'])} "
            f"({runs_of(basis['policy-record']['runs'])}) | "
            f"unreconciled — ({runs_of(basis['unreconciled']['runs'])})",
            "Only the receipted column is measured money. Policy-record figures are controller",
            "declarations generated from the engine manifest; unreconciled runs carry no numbers.",
        ]
        if rollup["metered_without_receipt"]:
            detail = ", ".join(f"{engine} ({count})"
                               for engine, count in rollup["metered_without_receipt"].items())
            lines += [
                "",
                f"Metered runs with no provider receipt: {detail}",
                "These bill real money and the ledger's 0 is a declaration, not a measurement.",
                "Treat metered spend for these engines as UNKNOWN until a receipt source exists.",
            ]
    if rollup["corrupt_ledger_rows"]:
        lines += [
            "",
            f"{rollup['corrupt_ledger_rows']} corrupt ledger row(s) excluded: shape failed",
            "validation (non-numeric/negative tokens or cost_usd, or a receipt claim missing",
            "the numbers behind it). Not counted as zero, not counted as measured money.",
        ]
    snapshots = rollup["openrouter_snapshots"]
    if snapshots:
        first = plain_number(snapshots[0].get("total_usage"))
        last = plain_number(snapshots[-1].get("total_usage"))
        span = money(last - first) if first is not None and last is not None else "unknown"
        lines += [
            "",
            f"OpenRouter account snapshots in week: {len(snapshots)} "
            f"(total_usage delta ${span}). Account-level, not attributable per run.",
        ]
    return "\n".join(lines[:REPORT_MAX_LINES]) + "\n"


def command_rollup(args: argparse.Namespace) -> int:
    ledger, out_dir = Path(args.ledger), Path(args.out)
    week = args.week or current_iso_week()
    if not WEEK_RE.fullmatch(week):
        diag(f"invalid --week {week!r}: expected YYYY-Www")
        return 2
    try:
        rows = read_jsonl_objects(ledger)
    except JsonlDurabilityError as exc:
        diag(f"ledger is unusable: {exc}")
        return 2
    rollup = build_rollup(rows, week)
    report_path = out_dir / f"usage-{week}.md"
    json_path = out_dir / f"usage-{week}.json"
    try:
        atomic_text(report_path, render_report(rollup, ledger))
        atomic_text(json_path, json.dumps(rollup, indent=2, sort_keys=True) + "\n")
    except OSError as exc:
        diag(f"cannot write report to {out_dir}: {exc}")
        return 1
    print(f"{PROG}: wrote {report_path.as_posix()} ({rollup['totals']['runs']} runs)")
    return 0


# --- openrouter account snapshot --------------------------------------------------------

class _RefuseRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuses every HTTP redirect outright, on any status code, scheme, or host.

    Returning None (instead of a followed Request) makes urllib fall through to the 3xx's
    own HTTPError, which the HTTP-failure branch below already reports tersely. Without
    this, urlopen's default redirect handler copies the Authorization header onto whatever
    Location a response names -- cross-origin, https->http, anywhere -- which would let a
    single redirect exfiltrate the credential. Fail closed instead: no redirect is ever
    followed, so the header can reach only the URL this call was configured with.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def command_snapshot(args: argparse.Namespace) -> int:
    if os.environ.get("RECURSION_USAGE_OPENROUTER", "") != "1":
        diag("openrouter snapshot disabled (RECURSION_USAGE_OPENROUTER is not 1)")
        return 3
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        diag("openrouter snapshot disabled (OPENROUTER_API_KEY is absent)")
        return 3
    url = os.environ.get("RECURSION_USAGE_OPENROUTER_URL", "").strip() or OPENROUTER_CREDITS_URL

    request = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {key}", "Accept": "application/json"})
    opener = urllib.request.build_opener(_RefuseRedirectHandler)
    try:
        with opener.open(request, timeout=SNAPSHOT_TIMEOUT_S) as response:
            raw = response.read(SNAPSHOT_MAX_BYTES)
    except urllib.error.HTTPError as exc:
        # Terse by construction: neither the key, the URL, nor the body may reach a log.
        diag(f"openrouter request rejected with HTTP status {exc.code}")
        return 1
    except (urllib.error.URLError, TimeoutError, OSError):
        diag("openrouter request failed (network error)")
        return 1

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        diag("openrouter response is not valid JSON")
        return 1
    body = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(body, dict):
        diag("openrouter response has no data object")
        return 1
    credits, usage = plain_number(body.get("total_credits")), plain_number(body.get("total_usage"))
    if credits is None or usage is None:
        diag("openrouter response is missing total_credits/total_usage")
        return 1

    record = {"schema_version": LEDGER_SCHEMA_VERSION, "record": "openrouter-snapshot",
              "fetched_at": now_iso(), "total_credits": credits, "total_usage": usage,
              "evidence_source": "openrouter-credits-v1"}
    try:
        append_jsonl(Path(args.ledger), record)
    except JsonlDurabilityError as exc:
        diag(f"ledger append failed: {exc}")
        return 1
    print(f"{PROG}: openrouter snapshot recorded")
    return 0


def command_quota(args: argparse.Namespace) -> int:
    pool_dir = Path(args.capacity_pool_dir) if args.capacity_pool_dir else assignment_mod.capacity_pool_dir()
    try:
        pool = assignment_mod.load_capacity_pool(pool_dir, args.pool_id)
    except assignment_mod.AssignmentError as exc:
        diag(str(exc))
        return 2
    try:
        rows = read_jsonl_objects(Path(args.ledger))
    except JsonlDurabilityError as exc:
        diag(f"ledger is unusable: {exc}")
        return 2

    period = pool["quota"]["period"]
    key = args.period or current_period_key(period)
    unit = pool["quota"].get("unit")
    limit = pool["quota"].get("limit")

    runs = tokens = 0
    cost = 0.0
    ledger_parent = Path(args.ledger).parent
    assignment_root = ledger_parent.parent / "assignments" if ledger_parent.name == "usage" else ledger_parent / "assignments"
    for row in rows:
        if not isinstance(row, dict) or row.get("record") != "run":
            continue
        pool_id = row.get("capacity_pool")
        if row.get("assignment_digest"):
            persisted = assignment_mod.load_assignment(
                assignment_root, str(row.get("task_id") or ""), row["assignment_digest"])
            if persisted is None:
                diag(f"assignment is absent for quota row {row.get('run_id')}")
                return 2
            try:
                assignment_mod.validate_assignment(persisted, require_source_evidence=True)
            except assignment_mod.AssignmentError as exc:
                diag(f"assignment is invalid for quota row {row.get('run_id')}: {exc}")
                return 2
            if row.get("provider") != persisted["provider"] or row.get("capacity_pool") != persisted.get("capacity_pool"):
                diag(f"quota row attribution disagrees with persisted assignment: {row.get('run_id')}")
                return 2
            pool_id = persisted.get("capacity_pool")
        if pool_id != args.pool_id:
            continue
        bucket = period_key_of(period, row.get("finished_at")) or period_key_of(period, row.get("started_at"))
        if bucket != key:
            continue
        runs += 1
        tokens += row.get("tokens") or 0
        cost += row.get("cost_usd") or 0.0

    meters = {"usd": cost, "tokens": tokens, "requests": runs}
    consumed = meters.get(unit) if unit else None
    if limit is None:
        status = "no-limit-declared"
    elif unit is not None and unit not in meters:
        status = "unmeasurable"  # a declared limit against a unit this tool cannot meter
    elif consumed is not None and consumed >= limit:
        status = "exceeded"
    else:
        status = "within-limit"
    on_demand_required = status == "exceeded" and pool.get("on_demand") is False

    report = {
        "schema_version": LEDGER_SCHEMA_VERSION, "record": "quota-reconciliation",
        "pool_id": args.pool_id, "period": period, "period_key": key,
        "unit": unit, "limit": limit, "consumed": consumed,
        "runs": runs, "tokens": tokens, "cost_usd": cost,
        "status": status, "on_demand_required": on_demand_required,
        "generated_at": now_iso(),
    }
    print(json.dumps(report, sort_keys=True))
    return 0


def parse_args(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=PROG, description="Engine usage/cost reconciliation.")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="normalize run evidence into the usage ledger")
    ingest.add_argument("--runs-dir", default=str(DEFAULT_RUNS_DIR))
    ingest.add_argument("--ledger", default=str(DEFAULT_LEDGER))

    rollup = sub.add_parser("rollup", help="emit the weekly one-page report plus machine JSON")
    rollup.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    rollup.add_argument("--out", default=str(DEFAULT_REPORT_DIR))
    rollup.add_argument("--week", default=None, metavar="YYYY-Www")

    snapshot = sub.add_parser("openrouter-snapshot",
                              help="opt-in account-level OpenRouter reconciliation")
    snapshot.add_argument("--ledger", default=str(DEFAULT_LEDGER))

    quota = sub.add_parser("quota", help="Phase 3: reconcile ledger usage against a capacity pool's quota period")
    quota.add_argument("--pool-id", required=True)
    quota.add_argument("--capacity-pool-dir", default=None)
    quota.add_argument("--ledger", default=str(DEFAULT_LEDGER))
    quota.add_argument("--period", default=None, metavar="PERIOD-KEY",
                       help="override the computed current period key (for reproducible tests/reports)")
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args(sys.argv[1:])
    handlers = {"ingest": command_ingest, "rollup": command_rollup,
                "openrouter-snapshot": command_snapshot, "quota": command_quota}
    try:
        return handlers[args.command](args)
    except UsageError as exc:
        diag(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
