#!/usr/bin/env python3
"""Linux-only ownership/sandbox proof boundary.

This test never starts a service or changes a host namespace. The actual transient-systemd
proof remains an explicitly human-run Linux gate; off Linux and without root it is a real,
visible not-proven result (exit 77), never a counted production pass.
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    if sys.platform != "linux":
        print("SKIP - phase4-linux-proof: Linux-only sandbox/ownership proof")
        return 77
    if os.geteuid() != 0:
        print("SKIP - phase4-linux-proof: root is required for ownership proof")
        return 77
    if shutil.which("systemd-run") is None:
        print("SKIP - phase4-linux-proof: systemd-run is absent; no host mutation attempted")
        return 77
    with tempfile.TemporaryDirectory(prefix="recursion-phase4-proof-") as tmp:
        plan = Path(tmp) / "plan.json"
        plan.write_text("{}\n", encoding="utf-8")
        os.chmod(plan, 0o600)
        info = plan.stat()
        if info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o600:
            print("FAIL - root-owned 0600 plan fixture was not created")
            return 1
    worker = (ROOT / "scripts/worker-sandbox.sh").read_text(encoding="utf-8")
    if "NetworkNamespacePath=$PROVIDER_NETNS" not in worker \
            or "root-owned and not group/other-writable" not in worker:
        print("FAIL - worker sandbox lacks provider namespace and ownership checks")
        return 1
    print("ok - Linux ownership fixture and worker sandbox checks are present")
    print("PREPARED - phase4-linux-proof: transient systemd sandbox proof is human-run only")
    print("NOT PRODUCTION-PROVEN - no live Linux/systemd evidence was collected")
    return 77


if __name__ == "__main__":
    raise SystemExit(main())
