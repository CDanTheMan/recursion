#!/usr/bin/env python3
"""FU-04 experiment gate for the kickoff.

Deterministic and provider-free. Requires a prior run of probe_windows.py.

    python -X utf8 -B experiments/v3/fu-04-os-conformance/check_fu04.py

A pass certifies only that (a) the manifest is intact and still unqualified, (b) all 20 negative
traces are preregistered and unexecuted, and (c) safe host probes were recorded with no fabricated
result. It is not platform qualification and not a certification of any OS build.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST = ROOT / "docs/v3/research-lane/followups-20261002/machine/platform-manifest.json"
TRACES = ROOT / "docs/v3/research-lane/followups-20261002/machine/negative-traces.json"
PROBES = HERE / "results" / "probes.json"
FLOORS = HERE / "platform-floors.json"


def fail(message: str) -> None:
    print(f"FU04_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    for path in (MANIFEST, TRACES, PROBES, FLOORS):
        if not path.exists():
            fail(f"missing file: {path}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract_status") != "proposed_unexecuted":
        fail("manifest is no longer proposed_unexecuted")
    profiles = manifest.get("profiles", [])
    if len(profiles) < 1:
        fail("manifest has no profiles")
    for prof in profiles:
        if prof.get("scope_decision") != "pending_owner":
            fail(f"profile {prof.get('target_id')} is not pending_owner")
        if prof.get("profile_key") is not None:
            fail(f"profile {prof.get('target_id')} has a pinned key but no evidence")

    traces = json.loads(TRACES.read_text(encoding="utf-8"))
    if traces.get("status") != "proposed_unexecuted":
        fail("negative-trace catalog is no longer proposed_unexecuted")
    fixtures = traces.get("fixtures", [])
    ids = {f.get("fixture_id") for f in fixtures}
    for n in range(1, 21):
        if f"PF{n:02d}" not in ids:
            fail(f"missing negative trace PF{n:02d}")
    executed = [f["fixture_id"] for f in fixtures if f.get("execution_status") != "unexecuted"]
    if executed:
        fail(f"traces claim execution without harness evidence: {executed}")

    probes = json.loads(PROBES.read_text(encoding="utf-8"))
    results = probes.get("probes", [])
    observed = [p for p in results if p.get("status") == "observed"]
    if len(observed) < 3:
        fail(f"expected >=3 observed safe probes, found {len(observed)}")
    if not probes.get("destructive_not_run"):
        fail("destructive traces are not explicitly recorded as not run")

    case_ids = {p.get("case_id") for p in profiles}
    floors = json.loads(FLOORS.read_text(encoding="utf-8"))
    mapped = {d["case_id"]: d["disposition"] for d in floors.get("profile_dispositions", [])}
    if set(mapped) != case_ids:
        fail(f"floors mapping does not cover every manifest case: {sorted(case_ids ^ set(mapped))}")
    if any(d == "qualified" for d in mapped.values()):
        fail("floors claim a qualified profile without trace evidence")
    oos = floors.get("storage", {}).get("out_of_scope", [])
    if "SMB" not in oos or "NFS" not in oos:
        fail("SMB/NFS must be out of canonical scope")
    if not floors.get("power_loss", {}).get("definition"):
        fail("power-loss definition missing")

    in_scope = sorted(k for k, v in mapped.items() if v == "in_scope_unqualified")
    print(f"FU04_PASS manifest unqualified ({len(profiles)} profiles; in scope: {in_scope}); "
          f"{len(fixtures)} traces unexecuted; {len(observed)} safe probes observed; "
          f"{len(probes['destructive_not_run'])} destructive traces not run; "
          f"floors pinned (D-028)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
