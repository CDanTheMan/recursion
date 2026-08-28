#!/usr/bin/env python3
"""PAUSE/resume interlock for the remote-adapter admission lock.

The ordinary pause/resume scripts use this small local helper so a PAUSE transition and a
remote outbound critical section have one ordering.  It performs no network I/O.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import remote_backend as rb


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("set", "clear"))
    parser.add_argument("--base", required=True)
    parser.add_argument("--reason", default="")
    args = parser.parse_args()
    base = Path(args.base).resolve()
    with rb.remote_state_lock(base, "pause-control"):
        path = rb.pause_path(base)
        if args.action == "set":
            content = f"PAUSED {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
            content += f"reason: {args.reason}\n"
            rb.atomic_bytes(path, content.encode("utf-8"))
        elif path.exists():
            if path.is_symlink() or not path.is_file():
                raise rb.RemoteError("request-invalid", "unsafe state/PAUSE path")
            path.unlink()
            rb._fsync_directory(path.parent)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except rb.RemoteError as exc:
        print(str(exc), flush=True)
        raise SystemExit(exc.exit_code)
