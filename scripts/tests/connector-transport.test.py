#!/usr/bin/env python3
"""Control: connector-transport.py adapter contract.

Frozen contract: scripts/connector-transport.py header, scripts/connectors/README.md, and
notify.sh's exit-code vocabulary (10 retryable, 11 config-missing, 12 refused/invalid).

The adapter is the only new code that could ever exec a transport, so the controls that
matter here are refusal, argv-injection containment, environment isolation, timeout, and
byte-exact stdout passthrough. STUB_ACK below is fixture bytes shaped like a Telegram
reply purely so the passthrough assertion has a distinctive payload; it is NOT a
transport acknowledgement and proves no delivery. Nothing in this file contacts a network.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[2]
ADAPTER = SOURCE / "scripts" / "connector-transport.py"

# Odd spacing plus a bare CRLF: text-mode translation or any re-serialization would show up.
STUB_ACK = b'{"ok": true,   "result": {"message_id": 4242,\n "chat": {"id": -1002003004}},\r\n "transport": "telegram"}'

ALLOWED_ENV = "CONNECTOR_TEST_ALLOWED"
FORBIDDEN_ENV = "CONNECTOR_TEST_FORBIDDEN_TOKEN"

STUB_SOURCE = '''import json, os, sys, time
# argv: stub.py <record-path> <mode> <destination> <message>
record, mode, destination, message = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with open(record, "w", encoding="utf-8") as handle:
    json.dump({"argv": sys.argv, "env": dict(os.environ)}, handle)
if mode == "hang":
    time.sleep(30)
sys.stdout.buffer.write(%(ack)r)
sys.stdout.buffer.flush()
sys.exit(3 if mode == "fail" else 0)
''' % {"ack": STUB_ACK}

failures: list[str] = []


def check(condition: bool, label: str) -> None:
    if condition:
        print(f"ok - {label}")
    else:
        print(f"FAIL - {label}")
        failures.append(label)


def write_fixture(tmp_dir: Path, mode: str, timeout_seconds: int = 20) -> Path:
    """Manifest + stub transport in a disposable connector dir. Returns the record path."""
    stub = tmp_dir / "stub-transport.py"
    stub.write_text(STUB_SOURCE, encoding="utf-8")
    record = tmp_dir / f"record-{mode}.json"
    manifest = {
        "schema_version": 1,
        "name": "stubconn",
        "description": "Stub connector for connector-transport.py controls",
        # sys.executable is absolute in both accepted forms (POSIX on the box, drive-absolute
        # on a workstation), so the fixture needs no test-only bypass in the transport path.
        "executable": sys.executable,
        "transport_argv": [
            "{{EXE}}", str(stub), str(record), mode, "{{DESTINATION}}", "{{MESSAGE}}",
        ],
        "ack_contract": "telegram",
        "env_passthrough": [ALLOWED_ENV],
        "timeout_seconds": timeout_seconds,
    }
    (tmp_dir / "stubconn.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return record


def build_env(
    tmp_dir: Path,
    connectors: str | None = "1",
    enabled: str | None = "1",
    active: str | None = "stubconn",
) -> dict:
    env = dict(os.environ)
    for key in [name for name in env if name.startswith("RECURSION_")]:
        env.pop(key)
    env["RECURSION_CONNECTOR_DIR"] = str(tmp_dir)
    if connectors is not None:
        env["RECURSION_CONNECTORS"] = connectors
    if enabled is not None:
        env["RECURSION_CONNECTOR_STUBCONN_ENABLED"] = enabled
    if active is not None:
        env["RECURSION_CONNECTOR_ACTIVE"] = active
    env[ALLOWED_ENV] = "allowed-value"
    env[FORBIDDEN_ENV] = "must-not-reach-the-child"
    return env


def run_adapter(args: list, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ADAPTER), *args], capture_output=True, env=env
    )


def test_refusals() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        record = write_fixture(tmp_dir, "ok")
        args = ["project-topic:telegram:-1002003004:7", "hello", "d-1", "e-1"]

        cases = [
            ("no active connector", build_env(tmp_dir, active=None)),
            ("connectors globally disabled", build_env(tmp_dir, connectors=None)),
            ("per-connector flag disabled", build_env(tmp_dir, enabled=None)),
            ("active names a reserved builtin (telegram)", build_env(tmp_dir, active="telegram")),
            ("active connector has no manifest", build_env(tmp_dir, active="ghostconn")),
            ("active connector name is malformed", build_env(tmp_dir, active="Stub Conn")),
        ]
        for label, env in cases:
            if record.exists():
                record.unlink()
            result = run_adapter(args, env)
            check(result.returncode == 12, f"{label} exits 12 (got {result.returncode})")
            check(not record.exists(), f"{label} never launches the transport")
            check(result.stdout == b"", f"{label} writes nothing to stdout")

        # Wrong argv count is a caller bug, refused before anything is resolved.
        for count, argv in ((3, args[:3]), (5, args + ["extra"]), (0, [])):
            if record.exists():
                record.unlink()
            result = run_adapter(argv, build_env(tmp_dir))
            check(result.returncode == 12, f"{count} arguments exits 12 (got {result.returncode})")
            check(not record.exists(), f"{count} arguments never launches the transport")


def test_control_character_refusals() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        record = write_fixture(tmp_dir, "ok")
        env = build_env(tmp_dir)

        # NUL cannot be carried through argv at all (the OS forbids it), so the payloads
        # here are the control characters that CAN reach a process.
        refused = [
            ("destination with \\x01", ["dest\x01ination", "hello", "d-1", "e-1"]),
            ("destination with a newline", ["dest\nination", "hello", "d-1", "e-1"]),
            ("destination with a tab", ["dest\tination", "hello", "d-1", "e-1"]),
            ("destination with DEL", ["dest\x7fination", "hello", "d-1", "e-1"]),
            ("message with \\x07", ["project-topic:telegram:-100:7", "bel\x07l", "d-1", "e-1"]),
            ("message with \\x1b", ["project-topic:telegram:-100:7", "esc\x1b[0m", "d-1", "e-1"]),
            ("message with DEL", ["project-topic:telegram:-100:7", "del\x7fete", "d-1", "e-1"]),
            ("empty destination", ["", "hello", "d-1", "e-1"]),
            ("empty message", ["project-topic:telegram:-100:7", "", "d-1", "e-1"]),
        ]
        for label, argv in refused:
            if record.exists():
                record.unlink()
            result = run_adapter(argv, env)
            check(result.returncode == 12, f"{label} exits 12 (got {result.returncode})")
            check(not record.exists(), f"{label} never launches the transport")

        # Newline and tab are legal in a message body and must survive intact.
        if record.exists():
            record.unlink()
        body = "line one\nline two\tindented"
        result = run_adapter(["project-topic:telegram:-100:7", body, "d-1", "e-1"], env)
        check(result.returncode == 0, f"message with newline/tab is accepted (got {result.returncode})")
        if record.exists():
            seen = json.loads(record.read_text(encoding="utf-8"))
            check(seen["argv"][4] == body, "message newlines and tabs reach the child unchanged")
        else:
            check(False, "message newlines and tabs reach the child unchanged")


def test_success_path_and_isolation() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        record = write_fixture(tmp_dir, "ok")
        # Spaces, quotes and shell metacharacters in one destination: if any layer went
        # through a shell or interpolated a string, this would split or execute.
        destination = 'project-topic:telegram:-100 "quoted" & echo pwned; rm -rf / #'
        message = "brief: 3 tasks green $(whoami) `id` | tee /tmp/x"
        result = run_adapter([destination, message, "d-42", "e-42"], build_env(tmp_dir))
        check(result.returncode == 0, f"valid + enabled send exits 0 (got {result.returncode})")
        check(result.stdout == STUB_ACK, "child stdout is passed through byte-exact")

        if not record.exists():
            check(False, "transport child recorded its argv and environment")
            return
        seen = json.loads(record.read_text(encoding="utf-8"))
        argv, env = seen["argv"], seen["env"]
        check(len(argv) == 5, f"child received exactly 5 argv elements (got {len(argv)})")
        check(argv[3] == destination, "destination arrives as ONE argv element, unmangled")
        check(argv[4] == message, "message arrives as ONE argv element, unmangled")
        check(argv[2] == "ok", "literal manifest elements pass through unchanged")

        check(env.get(ALLOWED_ENV) == "allowed-value", "declared env_passthrough name reaches the child")
        check(FORBIDDEN_ENV not in env, "undeclared parent env var does NOT reach the child")
        leaked = sorted(name for name in env if name.startswith("RECURSION_"))
        check(leaked == [], f"no RECURSION_* variable reaches the child (found {leaked})")
        unexpected = sorted(
            name for name in env
            if name not in {"PATH", "HOME", "LANG", ALLOWED_ENV}
        )
        check(unexpected == [], f"child environment is exactly the allowed set (extra: {unexpected})")


def test_timeout_is_retryable() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        write_fixture(tmp_dir, "hang", timeout_seconds=1)
        started = time.monotonic()
        result = run_adapter(
            ["project-topic:telegram:-100:7", "hello", "d-9", "e-9"], build_env(tmp_dir)
        )
        elapsed = time.monotonic() - started
        check(result.returncode == 10, f"timed-out transport exits 10 (got {result.returncode})")
        check(elapsed < 15, f"timed-out transport is killed promptly (took {elapsed:.1f}s)")
        check(result.stdout == b"", "timed-out transport contributes no acknowledgement bytes")


def test_child_failure_is_retryable() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        write_fixture(tmp_dir, "fail")
        result = run_adapter(
            ["project-topic:telegram:-100:7", "hello", "d-7", "e-7"], build_env(tmp_dir)
        )
        check(result.returncode == 10, f"nonzero-exit transport exits 10 (got {result.returncode})")
        check(result.stdout == STUB_ACK, "failed child's stdout is still passed through unmodified")


def test_missing_executable_is_refused() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        write_fixture(tmp_dir, "ok")
        manifest = json.loads((tmp_dir / "stubconn.json").read_text(encoding="utf-8"))
        absent = "/usr/local/bin/no-such-transport"
        if os.name == "nt":
            absent = str(Path(sys.executable).drive or "C:") + "\\no-such-transport.exe"
        manifest["executable"] = absent
        (tmp_dir / "stubconn.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        result = run_adapter(
            ["project-topic:telegram:-100:7", "hello", "d-8", "e-8"], build_env(tmp_dir)
        )
        check(result.returncode == 12, f"unspawnable executable exits 12 (got {result.returncode})")
        check(result.stdout == b"", "unspawnable executable writes nothing to stdout")


def main() -> int:
    test_refusals()
    test_control_character_refusals()
    test_success_path_and_isolation()
    test_timeout_is_retryable()
    test_child_failure_is_retryable()
    test_missing_executable_is_refused()

    if failures:
        print(f"connector-transport.test: {len(failures)} FAILED")
        return 1
    print("connector-transport.test: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
