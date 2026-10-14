"""Fake claude, codex, and grok processes for the console end-to-end test.

The launcher sets RECURSION_STUB_PROVIDER to claude, codex, or grok. Stdout is
the stream format that provider's adapter captures. RECURSION_STUB_MODE=fail
exits 1 and writes a marker on stderr that the harness must not keep.
"""

from __future__ import annotations

import os
import sys


def main() -> int:
    sys.stdin.read()
    provider = os.environ.get("RECURSION_STUB_PROVIDER", "")
    log_path = os.environ.get("RECURSION_STUB_LOG")
    if log_path and provider:
        with open(log_path, "a", encoding="utf-8") as handle:
            handle.write(provider + "\n")
    if provider not in {"claude", "codex", "grok"}:
        sys.stderr.write(f"unknown stub provider {provider!r}\n")
        return 2
    if os.environ.get("RECURSION_STUB_MODE") == "fail":
        sys.stderr.write("SECRET should not leak\n")
        return 1
    sys.stdout.write("VERDICT approve\n")
    sys.stdout.write(f"stub provider={provider}\n")
    if provider == "claude":
        line = (
            '{"type":"result","usage":{"input_tokens":11,"output_tokens":4},'
            '"total_cost_usd":0.01}\n'
        )
    elif provider == "codex":
        line = '{"type":"turn.completed","usage":{"input_tokens":6,"output_tokens":2}}\n'
    else:
        line = (
            '{"type":"text","data":"stub reply"}\n'
            '{"type":"end","usage":{"input_tokens":9,"output_tokens":3},"total_cost_usd":0.03}\n'
        )
    sys.stdout.write(line)
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
