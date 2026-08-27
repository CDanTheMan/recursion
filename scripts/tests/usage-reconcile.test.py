#!/usr/bin/env python3
"""Controls for scripts/usage-reconcile.py — per-run usage/cost telemetry (D-015 follow-on).

Hermetic: every case runs against a Python tempfile directory with its own runs dir,
ledger, and engine-manifest dir (RECURSION_ENGINE_DIR, the same test-only hook
resolve-engine.py uses). The snapshot cases talk to a local http.server thread through
RECURSION_USAGE_OPENROUTER_URL — no real network, no real credential.
"""

from __future__ import annotations

import http.server
import json
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
TOOL = SOURCE / "scripts" / "usage-reconcile.py"

FAKE_KEY = "sk-or-v1-TESTKEY-must-never-be-echoed"

CURSOR_MANIFEST = {
    "schema_version": 1, "name": "cursor", "description": "stub",
    "executable": "cursor-agent", "argv": ["{{EXE}}", "-p", "{{PROMPT}}"],
    "model": {"required": False, "argv_suffix": []}, "roles": ["implementer", "verifier"],
    "billing": {"basis": "metered", "provider": "cursor"},
    "network": {"policy": "provider-only", "endpoints": []},
    "availability_probe": None, "concurrency_cap": None, "env_passthrough": [],
}
OPENCODE_MANIFEST = {
    "schema_version": 1, "name": "opencode", "description": "stub",
    "executable": "opencode", "argv": ["{{EXE}}", "run", "--", "{{PROMPT}}"],
    "model": {"required": True, "argv_suffix": []}, "roles": ["implementer", "verifier"],
    "billing": {"basis": "metered", "provider": "openrouter-via-opencode"},
    "network": {"policy": "provider-only", "endpoints": []},
    "availability_probe": None, "concurrency_cap": None, "env_passthrough": [],
}

CLAUDE_USAGE = {"schema_version": 1, "provider": "anthropic-claude-code",
                "billing_basis": "flat-subscription", "tokens": 0, "cost_usd": 0,
                "evidence_source": "controller-engine-policy-v1"}
CURSOR_USAGE = {"schema_version": 1, "provider": "cursor", "billing_basis": "metered",
                "tokens": 0, "cost_usd": 0, "evidence_source": "engine-manifest-v1"}
RECEIPT_USAGE = {"schema_version": 1, "provider": "openrouter-via-opencode",
                 "billing_basis": "metered", "tokens": 1200, "cost_usd": 0.42,
                 "evidence_source": "opencode-usage-v1"}

failures: list = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def evidence(run_id: str, role: str, alias: str, usage: dict | None,
             started: str = "2026-08-24T10:00:00Z",
             finished: str | None = "2026-08-24T10:05:00Z") -> dict:
    """A worker-evidence.py record as it exists on disk after `finish`."""
    record = {
        "schema_version": 1, "id": run_id, "task_id": "T-100", "worker": f"{role}:{alias}",
        "role": role, "model_alias": alias, "worktree": "/tmp/wt", "base_commit": "0" * 40,
        "pid": 4242, "process_group": 4242, "lease_expires": "0",
        "deadline": "2026-08-24T11:00:00Z", "deadline_epoch": 0, "network_policy": "provider-only",
        "heartbeat_at": started, "log": "loop/logs/x.out", "usage": usage or {}, "result": {},
        "changed_files": [], "status": "running", "started_at": started,
    }
    if finished is not None:
        record.update(status="succeeded", outcome="done", exit_code=0, finished_at=finished)
    return record


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def run_tool(args: list, engines: Path | None = None, env_extra: dict | None = None) \
        -> subprocess.CompletedProcess:
    env = dict(os.environ)
    for name in ("RECURSION_ENGINE_DIR", "RECURSION_USAGE_OPENROUTER",
                 "RECURSION_USAGE_OPENROUTER_URL", "OPENROUTER_API_KEY"):
        env.pop(name, None)
    if engines is not None:
        env["RECURSION_ENGINE_DIR"] = str(engines)
    env.update(env_extra or {})
    return subprocess.run([sys.executable, str(TOOL), *args],
                          capture_output=True, text=True, env=env)


def ledger_rows(ledger: Path) -> list:
    if not ledger.is_file():
        return []
    return [json.loads(line) for line in
            ledger.read_text(encoding="utf-8").splitlines() if line.strip()]


def counts_from(stdout: str) -> dict:
    fields = stdout.strip().split()[1:]
    return dict(part.split("=", 1) for part in fields)


class StubHandler(http.server.BaseHTTPRequestHandler):
    payload = b'{"data":{"total_credits":25.0,"total_usage":9.5}}'
    status = 200

    def do_GET(self) -> None:  # noqa: N802 - http.server API
        self.send_response(type(self).status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(type(self).payload)))
        self.end_headers()
        self.wfile.write(type(self).payload)

    def log_message(self, *args) -> None:
        pass


def serve(payload: bytes, status: int):
    handler = type("Handler", (StubHandler,), {"payload": payload, "status": status})
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/credits"


def case_ingest(tmp: Path, engines: Path) -> None:
    runs, ledger = tmp / "runs", tmp / "usage" / "ledger.jsonl"
    write_json(runs / "r-claude.json", evidence("r-claude", "implementer", "opus-complex", CLAUDE_USAGE))
    write_json(runs / "r-cursor.json", evidence("r-cursor", "verifier", "cursor-primary", CURSOR_USAGE))
    write_json(runs / "r-receipt.json", evidence("r-receipt", "implementer", "opencode-flex", RECEIPT_USAGE))
    # Files that live in state/runs alongside evidence but are not evidence records.
    write_json(runs / "r-claude-scope.json", {"entries": ["a.py"]})
    (runs / "r-broken.json").write_text("{not json", encoding="utf-8", newline="\n")
    write_json(runs / "r-badid.json", {"schema_version": 1, "id": 7, "task_id": "T-1",
                                       "finished_at": "2026-08-24T10:05:00Z"})
    write_json(runs / "r-running.json",
               evidence("r-running", "implementer", "opus-complex", CLAUDE_USAGE, finished=None))
    # A verifier evidence subdirectory, one level down, as work.sh creates it.
    write_json(runs / "r-verify-evidence" / "run.json",
               evidence("r-nested", "verifier", "gemini-review", CURSOR_USAGE))

    result = run_tool(["ingest", "--runs-dir", str(runs), "--ledger", str(ledger)], engines)
    check(result.returncode == 0, f"ingest exits 0 (got {result.returncode}) {result.stderr.strip()}")
    counts = counts_from(result.stdout)
    check(counts.get("ingested") == "4", f"ingest counts 4 records (got {counts.get('ingested')})")
    check(counts.get("malformed") == "2", f"malformed counted twice (got {counts.get('malformed')})")
    check(counts.get("incomplete") == "1", f"in-flight run not ingested (got {counts.get('incomplete')})")
    check(counts.get("non-evidence") == "1", f"scope file skipped (got {counts.get('non-evidence')})")

    rows = {row["run_id"]: row for row in ledger_rows(ledger)}
    check(set(rows) == {"r-claude", "r-cursor", "r-receipt", "r-nested"},
          f"ledger holds exactly the terminal runs (got {sorted(rows)})")

    claude = rows.get("r-claude", {})
    check(claude.get("engine") == "claude", f"claude provider maps to engine (got {claude.get('engine')})")
    check(claude.get("cost_basis") == "policy-record",
          f"claude flat-subscription is a policy record (got {claude.get('cost_basis')})")
    check(claude.get("role") == "implementer" and claude.get("model_alias") == "opus-complex",
          "claude role/alias carried through")
    check(claude.get("wall_seconds") == 300, f"wall_seconds computed (got {claude.get('wall_seconds')})")
    check(claude.get("outcome") == "done", "outcome carried through")
    check(claude.get("model") is None, "model stays null - the evidence schema does not carry it")

    cursor = rows.get("r-cursor", {})
    check(cursor.get("engine") == "cursor",
          f"manifest provider maps to plugin engine (got {cursor.get('engine')})")
    check(cursor.get("cost_basis") == "policy-record" and cursor.get("billing_basis") == "metered",
          "metered cursor run is policy-record, not a receipt")

    receipt = rows.get("r-receipt", {})
    check(receipt.get("cost_basis") == "receipt" and receipt.get("cost_usd") == 0.42
          and receipt.get("tokens") == 1200, "provider-sourced usage classifies as a receipt")

    # Nothing invented: a malformed record contributes no ledger row at all.
    check(all(row.get("run_id") not in (7, "7") for row in ledger_rows(ledger)),
          "malformed record invents no ledger row")

    # Idempotent re-ingest.
    again = run_tool(["ingest", "--runs-dir", str(runs), "--ledger", str(ledger)], engines)
    check(again.returncode == 0, f"re-ingest exits 0 (got {again.returncode})")
    repeat = counts_from(again.stdout)
    check(repeat.get("ingested") == "0" and repeat.get("duplicate") == "4",
          f"re-ingest duplicates nothing (got {again.stdout.strip()})")
    check(len(ledger_rows(ledger)) == 4, "ledger length unchanged after re-ingest")


def case_engine_unknown(tmp: Path, engines: Path) -> None:
    runs, ledger = tmp / "runs2", tmp / "usage2" / "ledger.jsonl"
    write_json(runs / "r-strange.json", evidence(
        "r-strange", "implementer", "mystery-alias",
        {"schema_version": 1, "provider": "not-in-any-manifest", "billing_basis": "metered",
         "tokens": 0, "cost_usd": 0, "evidence_source": "engine-manifest-v1"}))
    write_json(runs / "r-nousage.json", evidence("r-nousage", "implementer", "opus-complex", None))
    result = run_tool(["ingest", "--runs-dir", str(runs), "--ledger", str(ledger)], engines)
    check(result.returncode == 0, f"unknown-provider ingest exits 0 (got {result.returncode})")
    rows = {row["run_id"]: row for row in ledger_rows(ledger)}
    check(rows.get("r-strange", {}).get("engine") == "unknown",
          "unmapped provider yields engine 'unknown', not a guess")
    empty = rows.get("r-nousage", {})
    check(empty.get("cost_basis") == "unreconciled" and empty.get("tokens") is None
          and empty.get("cost_usd") is None, "absent usage record is unreconciled with null numbers")


def case_shipped_manifests(tmp: Path) -> None:
    """The mapping must resolve against the manifests actually shipped in scripts/engines."""
    runs, ledger = tmp / "runs3", tmp / "usage3" / "ledger.jsonl"
    write_json(runs / "r-ship.json", evidence("r-ship", "verifier", "cursor-primary", CURSOR_USAGE))
    result = run_tool(["ingest", "--runs-dir", str(runs), "--ledger", str(ledger)], engines=None)
    check(result.returncode == 0, f"shipped-manifest ingest exits 0 (got {result.returncode})")
    rows = ledger_rows(ledger)
    check(bool(rows) and rows[0].get("engine") == "cursor",
          "shipped scripts/engines/cursor.json maps provider 'cursor' to engine 'cursor'")


def case_rollup(tmp: Path, engines: Path) -> None:
    runs, ledger, out = tmp / "runs4", tmp / "usage4" / "ledger.jsonl", tmp / "reports4"
    write_json(runs / "a.json", evidence("a", "implementer", "opus-complex", CLAUDE_USAGE))
    write_json(runs / "b.json", evidence("b", "verifier", "cursor-primary", CURSOR_USAGE))
    write_json(runs / "c.json", evidence("c", "verifier", "cursor-primary", CURSOR_USAGE))
    write_json(runs / "d.json", evidence("d", "implementer", "opencode-flex", RECEIPT_USAGE))
    write_json(runs / "e.json", evidence("e", "implementer", "opencode-flex", RECEIPT_USAGE))
    write_json(runs / "f.json", evidence("f", "implementer", "opus-complex", None))
    # Out of week: 2026-08-17 is 2026-W34.
    write_json(runs / "g.json", evidence("g", "implementer", "opus-complex", CLAUDE_USAGE,
                                         started="2026-08-17T10:00:00Z",
                                         finished="2026-08-17T10:01:00Z"))
    run_tool(["ingest", "--runs-dir", str(runs), "--ledger", str(ledger)], engines)

    result = run_tool(["rollup", "--ledger", str(ledger), "--out", str(out), "--week", "2026-W35"],
                      engines)
    check(result.returncode == 0, f"rollup exits 0 (got {result.returncode}) {result.stderr.strip()}")
    machine = json.loads((out / "usage-2026-W35.json").read_text(encoding="utf-8"))
    totals, basis = machine["totals"], machine["totals"]["by_basis"]
    check(totals["runs"] == 6, f"six runs land in 2026-W35 (got {totals['runs']})")
    check(machine["runs_outside_week"] == 1, f"W34 run excluded (got {machine['runs_outside_week']})")
    check(totals["tokens"] == 2400, f"tokens sum to 2400 (got {totals['tokens']})")
    check(abs(totals["cost_usd"] - 0.84) < 1e-9, f"cost sums to 0.84 (got {totals['cost_usd']})")
    check(basis["receipt"]["runs"] == 2 and abs(basis["receipt"]["cost_usd"] - 0.84) < 1e-9,
          f"receipted split is 2 runs / $0.84 (got {basis['receipt']})")
    check(basis["policy-record"]["runs"] == 3 and basis["policy-record"]["cost_usd"] == 0.0,
          f"policy-record split is 3 runs / $0.00 (got {basis['policy-record']})")
    check(basis["unreconciled"]["runs"] == 1 and basis["unreconciled"]["cost_usd"] == 0.0,
          f"unreconciled split is 1 run (got {basis['unreconciled']})")
    check(machine["metered_without_receipt"] == {"cursor": 2},
          f"cursor surfaces as metered-without-receipt (got {machine['metered_without_receipt']})")

    groups = {(group["engine"], group["alias"]): group for group in machine["groups"]}
    check(groups.get(("cursor", "cursor-primary"), {}).get("runs") == 2,
          "grouping is engine then alias")
    check(len(groups) == 4, f"four engine/alias groups (got {len(groups)})")

    report = (out / "usage-2026-W35.md").read_text(encoding="utf-8")
    check(len(report.splitlines()) <= 60, f"report is one page (got {len(report.splitlines())} lines)")
    check("Evidence basis:" in report, "report states its own evidence basis")
    check("never as zero" in report, "report states that nothing is estimated")
    check("Metered runs with no provider receipt: cursor (2)" in report,
          "report names the metered arms with no receipt")
    check("policy-record $0.00 (3 runs)" in report, "report prints the receipt/policy split")


def case_rollup_empty(tmp: Path, engines: Path) -> None:
    ledger, out = tmp / "usage5" / "ledger.jsonl", tmp / "reports5"
    result = run_tool(["rollup", "--ledger", str(ledger), "--out", str(out), "--week", "2026-W35"],
                      engines)
    check(result.returncode == 0, f"empty-ledger rollup exits 0 (got {result.returncode})")
    report = (out / "usage-2026-W35.md").read_text(encoding="utf-8")
    check("Runs in week: 0" in report, "empty rollup reports zero runs")
    check("absence of records" in report,
          "empty rollup calls the gap an absence of records, not a zero-spend claim")
    machine = json.loads((out / "usage-2026-W35.json").read_text(encoding="utf-8"))
    check(machine["totals"]["runs"] == 0 and machine["groups"] == [], "empty rollup JSON is empty")

    bad = run_tool(["rollup", "--ledger", str(ledger), "--out", str(out), "--week", "week-35"],
                   engines)
    check(bad.returncode == 2, f"malformed --week exits 2 (got {bad.returncode})")


def case_snapshot_disabled(tmp: Path) -> None:
    ledger = tmp / "usage6" / "ledger.jsonl"
    off = run_tool(["openrouter-snapshot", "--ledger", str(ledger)],
                   env_extra={"OPENROUTER_API_KEY": FAKE_KEY})
    check(off.returncode == 3, f"snapshot without the opt-in flag exits 3 (got {off.returncode})")
    check(off.stderr.count("\n") == 1, "refusal is one line on stderr")
    check(FAKE_KEY not in off.stdout + off.stderr, "refusal never echoes the key")

    nokey = run_tool(["openrouter-snapshot", "--ledger", str(ledger)],
                     env_extra={"RECURSION_USAGE_OPENROUTER": "1"})
    check(nokey.returncode == 3, f"snapshot without a key exits 3 (got {nokey.returncode})")
    check(not ledger.exists(), "a refused snapshot writes nothing to the ledger")


def case_snapshot_success(tmp: Path) -> None:
    ledger = tmp / "usage7" / "ledger.jsonl"
    server, url = serve(b'{"data":{"total_credits":25.0,"total_usage":9.5}}', 200)
    try:
        result = run_tool(["openrouter-snapshot", "--ledger", str(ledger)], env_extra={
            "RECURSION_USAGE_OPENROUTER": "1", "OPENROUTER_API_KEY": FAKE_KEY,
            "RECURSION_USAGE_OPENROUTER_URL": url})
    finally:
        server.shutdown()
        server.server_close()
    check(result.returncode == 0, f"snapshot exits 0 (got {result.returncode}) {result.stderr.strip()}")
    rows = ledger_rows(ledger)
    check(len(rows) == 1 and rows[0].get("record") == "openrouter-snapshot",
          f"one snapshot record appended (got {rows})")
    snap = rows[0] if rows else {}
    check(snap.get("total_credits") == 25.0 and snap.get("total_usage") == 9.5,
          "snapshot carries the account totals")
    check(snap.get("schema_version") == 1 and bool(snap.get("fetched_at")),
          "snapshot record is versioned and timestamped")
    check(FAKE_KEY not in result.stdout + result.stderr, "success path never echoes the key")


def case_snapshot_failure(tmp: Path) -> None:
    ledger = tmp / "usage8" / "ledger.jsonl"
    server, url = serve(b'{"error":{"message":"invalid api key ' + FAKE_KEY.encode() + b'"}}', 401)
    try:
        result = run_tool(["openrouter-snapshot", "--ledger", str(ledger)], env_extra={
            "RECURSION_USAGE_OPENROUTER": "1", "OPENROUTER_API_KEY": FAKE_KEY,
            "RECURSION_USAGE_OPENROUTER_URL": url})
    finally:
        server.shutdown()
        server.server_close()
    check(result.returncode != 0 and result.returncode != 3,
          f"HTTP failure exits nonzero and not 3 (got {result.returncode})")
    combined = result.stdout + result.stderr
    check(FAKE_KEY not in combined, "failure path never echoes the key")
    check("invalid api key" not in combined, "failure path never echoes the response body")
    check(url not in combined, "failure path never echoes the request URL")
    check(not ledger.exists(), "a failed snapshot writes nothing to the ledger")

    server, url = serve(b"this is not json", 200)
    try:
        broken = run_tool(["openrouter-snapshot", "--ledger", str(ledger)], env_extra={
            "RECURSION_USAGE_OPENROUTER": "1", "OPENROUTER_API_KEY": FAKE_KEY,
            "RECURSION_USAGE_OPENROUTER_URL": url})
    finally:
        server.shutdown()
        server.server_close()
    check(broken.returncode == 1, f"unparseable response exits 1 (got {broken.returncode})")
    check(FAKE_KEY not in broken.stdout + broken.stderr, "parse-failure path never echoes the key")


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        engines = tmp / "engines"
        engines.mkdir()
        write_json(engines / "cursor.json", CURSOR_MANIFEST)
        write_json(engines / "opencode.json", OPENCODE_MANIFEST)
        write_json(engines / "model-aliases.json", {"schema_version": 1, "aliases": {}})

        case_ingest(tmp, engines)
        case_engine_unknown(tmp, engines)
        case_shipped_manifests(tmp)
        case_rollup(tmp, engines)
        case_rollup_empty(tmp, engines)
        case_snapshot_disabled(tmp)
        case_snapshot_success(tmp)
        case_snapshot_failure(tmp)

    if failures:
        print(f"usage-reconcile.test: {len(failures)} FAILED")
        return 1
    print("usage-reconcile.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
