#!/usr/bin/env python3
"""Mark systemd's exact Hermes gateway MainPID for intentional SIGTERM."""

from __future__ import annotations

import re
import os
from pathlib import Path
import sys
from typing import Sequence


EX_USAGE = 64
EX_MARKER_FAILURE = 1


def main(argv: Sequence[str]) -> int:
    if len(argv) != 1 or re.fullmatch(r"[1-9][0-9]*", argv[0]) is None:
        print("hermes-gateway-planned-stop: expected one canonical positive PID", file=sys.stderr)
        return EX_USAGE

    target_pid = int(argv[0])
    if target_pid <= 1:
        print("hermes-gateway-planned-stop: refusing unsafe PID", file=sys.stderr)
        return EX_USAGE

    try:
        from gateway.status import _get_planned_stop_marker_path, write_planned_stop_marker

        home_raw = os.environ.get("HERMES_HOME", "").strip()
        if not home_raw or not Path(home_raw).is_absolute():
            raise ValueError("HERMES_HOME is not an absolute path")
        home = Path(home_raw).resolve(strict=True)
        marker = Path(_get_planned_stop_marker_path()).resolve(strict=False)
        if marker == home or not marker.is_relative_to(home):
            raise ValueError("planned-stop marker is outside HERMES_HOME")

        marked = write_planned_stop_marker(target_pid)
    except Exception:
        print("hermes-gateway-planned-stop: marker creation raised", file=sys.stderr)
        return EX_MARKER_FAILURE

    if marked is not True:
        print("hermes-gateway-planned-stop: marker creation failed", file=sys.stderr)
        return EX_MARKER_FAILURE
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
