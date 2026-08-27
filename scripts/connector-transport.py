#!/usr/bin/env python3
"""notify.sh transport adapter for a declarative connector manifest. INERT BY DEFAULT.

notify.sh's durable mode contains one already-existing hook:

    RESPONSE="$("$RECURSION_NOTIFY_TRANSPORT" "$DESTINATION" "$MSG" "$DELIVERY_ID" "$EVENT_ID")"

RECURSION_NOTIFY_TRANSPORT is unset on the box. A human may LATER point it at this file;
until then nothing here can run, and notify.sh is untouched. See
docs/plans/engine-plugin-architecture.md Component 6 and scripts/connectors/README.md.

What this adapter does and, more importantly, does not do:
  * resolves the connector named by RECURSION_CONNECTOR_ACTIVE through the same
    fail-closed chain as scripts/resolve-connector.py (that module is the one authority;
    it is imported, not reimplemented);
  * builds the child argv by EXACT-ELEMENT placeholder substitution -- no shell, no
    string interpolation -- so a destination or message carrying spaces, quotes or shell
    metacharacters arrives as exactly one argv element;
  * execs the transport with a filtered environment (env_passthrough names plus
    PATH/HOME/LANG) so nothing else in the parent environment reaches the child;
  * passes the child's stdout through BYTE-EXACT.

It never parses, edits, wraps, or fabricates an acknowledgement. notify.sh remains the
sole ack validator; a zero exit from this file is not delivery evidence, and there is no
code path here that can produce an ack body of its own.

Exit codes (notify.sh's vocabulary: 10 retryable, 11 config-missing, 12 refused/invalid):
   0  the child exited 0; its stdout was written to our stdout unmodified
  10  retryable: the child exceeded timeout_seconds and was killed, or exited nonzero
  12  refused: wrong argv count, control characters in destination/message, no active
      connector, connector absent/disabled/invalid, or the declared executable could not
      be spawned
Note: notify.sh's transport branch currently collapses every nonzero rc to its own 12
(`[ "$TRANSPORT_RC" -eq 0 ] || exit 12`). Distinguishing 10 from 12 there is part of the
D-014-gated follow-on; the codes are emitted correctly here so that widening is a
one-line change in notify.sh rather than a rewrite here.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

PROG = "connector-transport"

RESOLVER_PATH = Path(__file__).resolve().parent / "resolve-connector.py"

RC_OK = 0
RC_RETRYABLE = 10
RC_REFUSED = 12

# PATH/HOME/LANG are process plumbing, not payload. Everything else in the parent
# environment -- including every RECURSION_* flag and any credential the caller happened
# to export -- stays out of the child unless the manifest names it.
BASE_ENV_NAMES = ("PATH", "HOME", "LANG")
# A message may carry newlines and tabs; nothing else below 0x20, and never DEL. A
# destination is a machine identifier and carries no control characters at all. NUL
# cannot reach us through argv (the OS forbids it) -- it is checked anyway, because the
# check must not depend on which channel the caller used.
MESSAGE_ALLOWED_CONTROLS = ("\n", "\t")


class Refusal(Exception):
    """Non-retryable: the request or the configuration is wrong (exit 12)."""


def diag(message: str) -> None:
    print(f"{PROG}: {message}", file=sys.stderr)


def has_forbidden_control(text: str, allowed: tuple) -> bool:
    for char in text:
        code = ord(char)
        if (code < 0x20 or code == 0x7F) and char not in allowed:
            return True
    return False


def load_resolver():
    """Import scripts/resolve-connector.py by path (its name is not an identifier)."""
    spec = importlib.util.spec_from_file_location("recursion_resolve_connector", RESOLVER_PATH)
    if spec is None or spec.loader is None:
        raise Refusal(f"connector resolver is missing: {RESOLVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except BaseException as exc:  # a broken resolver is a refusal, never a fallback
        raise Refusal(f"connector resolver failed to load: {exc}") from exc
    return module


def resolve_active_plan():
    resolver = load_resolver()
    active = os.environ.get("RECURSION_CONNECTOR_ACTIVE", "").strip()
    if not active:
        raise Refusal("RECURSION_CONNECTOR_ACTIVE is not set; no connector is active")
    try:
        plan = resolver.resolve_connector(active)
    except resolver.ConnectorError as exc:
        raise Refusal(f"connector {active!r} is invalid: {exc}") from exc
    except resolver.ConnectorUnavailable as exc:
        raise Refusal(f"connector {active!r} is unavailable: {exc}") from exc
    # Fail closed on an unexpected plan shape rather than trusting a dict we were handed.
    argv = plan.get("transport_argv")
    executable = plan.get("executable")
    timeout = plan.get("timeout_seconds")
    if not isinstance(argv, list) or argv[:1] != ["{{EXE}}"]:
        raise Refusal("resolved plan has no {{EXE}} at transport_argv[0]")
    if argv.count("{{DESTINATION}}") != 1 or argv.count("{{MESSAGE}}") != 1:
        raise Refusal("resolved plan does not carry exactly one destination and message placeholder")
    if not isinstance(executable, str) or not os.path.isabs(executable):
        raise Refusal("resolved plan executable is not an absolute path")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or not (1 <= timeout <= 120):
        raise Refusal("resolved plan timeout_seconds is out of contract")
    return plan


def build_transport_argv(plan: dict, destination: str, message: str) -> list:
    """Exact-element substitution only -- the same rule as worker-sandbox.sh build_plan_argv."""
    run = []
    for element in plan["transport_argv"]:
        if element == "{{EXE}}":
            run.append(plan["executable"])
        elif element == "{{DESTINATION}}":
            run.append(destination)
        elif element == "{{MESSAGE}}":
            run.append(message)
        else:
            run.append(element)
    return run


def child_environment(plan: dict) -> dict:
    env = {}
    for name in BASE_ENV_NAMES:
        value = os.environ.get(name)
        if value is not None:
            env[name] = value
    for name in plan["env_passthrough"]:
        value = os.environ.get(name)
        if value is not None:
            env[name] = value
    return env


def main() -> int:
    args = sys.argv[1:]
    if len(args) != 4:
        diag(f"expected 4 arguments (destination message delivery_id event_id), got {len(args)}")
        return RC_REFUSED
    destination, message, delivery_id, _event_id = args

    if not destination:
        diag("destination is empty")
        return RC_REFUSED
    if not message:
        diag(f"message is empty (delivery {delivery_id or '-'})")
        return RC_REFUSED
    if has_forbidden_control(destination, ()):
        diag("destination contains a control character")
        return RC_REFUSED
    if has_forbidden_control(message, MESSAGE_ALLOWED_CONTROLS):
        diag("message contains a control character other than newline or tab")
        return RC_REFUSED

    try:
        plan = resolve_active_plan()
    except Refusal as exc:
        diag(str(exc))
        return RC_REFUSED

    run = build_transport_argv(plan, destination, message)
    env = child_environment(plan)
    try:
        # stderr is inherited: the child's diagnostics belong to whoever is watching the
        # process, and must never be mixed into the acknowledgement stream on stdout.
        completed = subprocess.run(
            run,
            env=env,
            stdout=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            timeout=plan["timeout_seconds"],
            shell=False,
        )
    except subprocess.TimeoutExpired:
        # subprocess.run has already killed and reaped the child. Partial stdout is
        # discarded: a truncated body is not an acknowledgement, and the send may or may
        # not have landed, which is exactly what 10 means.
        diag(f"transport exceeded {plan['timeout_seconds']}s and was killed (delivery {delivery_id or '-'})")
        return RC_RETRYABLE
    except OSError as exc:
        diag(f"could not exec {plan['executable']}: {exc}")
        return RC_REFUSED

    # Byte-exact passthrough, in both outcomes. The adapter does not interpret the body,
    # so it neither edits nor suppresses it; only the exit code carries a verdict, and
    # notify.sh requires rc 0 before it looks at the body at all.
    if completed.stdout:
        sys.stdout.buffer.write(completed.stdout)
        sys.stdout.buffer.flush()
    if completed.returncode != 0:
        diag(f"transport exited {completed.returncode} (delivery {delivery_id or '-'})")
        return RC_RETRYABLE
    return RC_OK


if __name__ == "__main__":
    raise SystemExit(main())
