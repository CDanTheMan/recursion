#!/usr/bin/env python3
"""validate-decision.py — the ONE definition of a well-formed Hermes decision.

    validate-decision.py '<verb list>' '<json>'
      -> prints "OK <canonical-json>" and exits 0
      -> prints "ERR <reason>"          and exits 1

WHY IT IS ITS OWN FILE. It was originally inlined in hermes-decide.sh as a heredoc-fed
python snippet, and the test re-implemented the same rules to check them. Two problems, both
real: the heredoc form silently broke (`python3 - <<'PY'` consumes stdin for the SCRIPT, so
the piped JSON never arrived and every decision was rejected), and a test that re-implements
the rule validates a copy rather than the code that runs. One file, one definition, exercised
directly by the suite.

The rules encode CONTROL_PLANE.md, not taste:
  - the verb must be on the whitelist the actuator recognises;
  - args become PROCESS ARGUMENTS, so they must be boring — this is an injection boundary;
  - `goal` is mandatory (invariant 12: no work without a parent goal);
  - `wrong_if` is mandatory (the decision log has always required a falsifier; a decision
    that cannot say what would make it wrong is a guess with better formatting).
"""
import json
import math
import re
import sys

ARG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,80}")
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
AUTHORING_TEXT_VERBS = {
    "roadmap-add", "note", "assist-answer", "portfolio-add",
    "pilot-plan-propose", "pilot-plan-approve", "pilot-window-open", "pilot-window-close",
    "pilot-task-create", "pilot-block", "pilot-escalate",
}
PILOT_VERBS = {
    "pilot-plan-propose", "pilot-task-create", "pilot-worker-request",
    "pilot-verifier-request", "pilot-block", "pilot-escalate", "pilot-goal-verify",
}
PHASE7_VERBS = {
    "notification-reconcile", "notification-deliver", "notification-portfolio",
    "notification-audit", "notification-recover",
}
PHASE8_HEAD_VERBS = {"pilot-plan-approve", "pilot-window-open", "pilot-window-close"}
ROUTING_RECONCILER_VERBS = {"routing-refuse"}
MAX_DECISION_BYTES = 2 * 1024 * 1024


def safe_diagnostic(message):
    """Keep validator diagnostics useful without reflecting an absolute caller path."""
    return re.sub(r"(?:[A-Za-z]:[\\/]|\\\\|(?<![A-Za-z0-9_])/)[^\s,;)]*", "<path>", str(message))


def parse_finite(value):
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("non-finite JSON number is forbidden")
    return parsed
ARITY = {
    "noop": (0, 0),
    "conduct": (0, 0),
    "reap": (0, 0),
    "plan": (1, 1),
    "work": (1, 1),
    "publish": (1, 1),
    "resolve-esc": (1, 1),
    "register": (1, 1),
    "roadmap-add": (1, 1),
    "note": (1, 1),
    "assist-answer": (1, 1),
    "roadmap-new": (2, 2),
    "portfolio-add": (2, 2),
    "project-topic-bind": (2, 2),
    "pilot-plan-propose": (2, 2),
    "pilot-plan-approve": (3, 3),
    "pilot-window-open": (4, 4),
    "pilot-window-close": (2, 2),
    "pilot-task-create": (4, 5),
    "pilot-worker-request": (3, 3),
    "pilot-verifier-request": (3, 3),
    "pilot-block": (3, 3),
    "pilot-escalate": (2, 2),
    "pilot-goal-verify": (2, 2),
    # Phase 6 internal decisions are emitted by the deterministic reconciler, then travel
    # through the same durable queue and sole actuator as every other state change.
    "reconcile-goal": (2, 2),
    "task-transition": (6, 6),
    "goal-transition": (5, 5),
    "verify-goal": (2, 2),
    "publish-task": (3, 3),
    "notification-reconcile": (2, 2),
    "notification-deliver": (2, 2),
    "notification-portfolio": (2, 2),
    "notification-audit": (2, 2),
    "notification-recover": (2, 2),
    "routing-refuse": (2, 2),
    "escalate": (1, 3),
}


def validate(verbs, raw, expected_actor=None):
    """Return (ok: bool, message: str)."""
    try:
        if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_DECISION_BYTES:
            raise ValueError("decision exceeds the bounded input size")
        d = json.loads(raw, parse_float=parse_finite,
                       parse_constant=lambda name: (_ for _ in ()).throw(ValueError(name)))
    except (json.JSONDecodeError, ValueError, TypeError, UnicodeError, OverflowError, RecursionError) as e:
        return False, "malformed JSON: %s" % e
    if not isinstance(d, dict):
        return False, "decision is not an object"

    verb = str(d.get("verb", "")).strip()
    if verb not in verbs:
        return False, "verb %r is not on the whitelist" % verb

    actor = str(d.get("actor", ""))
    if expected_actor:
        if actor != expected_actor:
            return False, "actor %r does not match routed decider %r" % (actor, expected_actor)
        if expected_actor.startswith("pilot-") and verb not in (PILOT_VERBS | {"noop"}):
            return False, "project-pilot decider may emit only noop or project-pilot verbs"

    args = d.get("args", []) or []
    if not isinstance(args, list) or any(not isinstance(a, str) for a in args):
        return False, "args must be a list of strings"
    bad = [a for a in args if not ARG_RE.fullmatch(a)]
    if bad:
        return False, "unsafe argument(s): %r" % bad
    if any(".." in a for a in args):
        return False, "path traversal in argument"
    if verb in ARITY:
        minimum, maximum = ARITY[verb]
        if not minimum <= len(args) <= maximum:
            return False, "%s requires %d..%d argument(s)" % (verb, minimum, maximum)

    # `text` carries prose for the authoring verbs (a roadmap item, a note, an escalation
    # title). It is NOT held to ARG_RE: that pattern exists because args become process
    # arguments, and prose cannot survive it. Passed as one argv element and never through a
    # shell, the risks that remain are newlines/control characters (which would forge extra
    # lines in an append-only file) and a leading dash (which would be read as a flag).
    text = d.get("text", "")
    if text is not None and not isinstance(text, str):
        return False, "text must be a string"
    text = text or ""
    if text:
        if len(text) > 500:
            return False, "text is too long (%d chars, max 500)" % len(text)
        if any(ord(ch) < 32 for ch in text):
            return False, "text contains newlines or control characters"
        if text.lstrip().startswith("-"):
            return False, "text may not begin with '-' (it would be read as a flag)"
        if re.search(r"`|\$\(|\$\{|[;&|<>]", text):
            return False, "text contains shell-shaped syntax"
        if re.search(r"(^|\s)(#{1,6}\s|\*\*|__|\[[^]]+\]\()", text):
            return False, "text contains Markdown markup"
    if verb in AUTHORING_TEXT_VERBS and not text.strip():
        return False, "%s requires bounded prose in text" % verb
    plan = d.get("plan")
    if verb == "pilot-plan-propose" and not isinstance(plan, dict):
        return False, "pilot-plan-propose requires a structured plan object"
    if verb != "pilot-plan-propose" and plan is not None:
        return False, "plan payload is allowed only for pilot-plan-propose"

    instruction_id = d.get("instruction_id")
    if instruction_id is not None and not ID_RE.fullmatch(str(instruction_id)):
        return False, "instruction_id is not a canonical identifier"
    if verb == "assist-answer" and not instruction_id:
        return False, "assist-answer requires instruction_id correlation"
    if verb in PILOT_VERBS:
        actor = str(d.get("actor", ""))
        project = str(d.get("project", ""))
        if not actor.startswith("pilot-") or not ID_RE.fullmatch(actor):
            return False, "project-pilot verb requires a canonical pilot actor"
        if not ID_RE.fullmatch(project) or not args or args[0] != project:
            return False, "project-pilot verb must target its declared project"
        if not instruction_id:
            return False, "project-pilot verb requires topic instruction correlation"
    if verb in PHASE8_HEAD_VERBS:
        actor = str(d.get("actor", ""))
        project = str(d.get("project", ""))
        if actor != "head-hermes":
            return False, "Phase 8 approval/window verb requires Head Hermes"
        if not ID_RE.fullmatch(project) or not args or args[0] != project:
            return False, "Phase 8 approval/window verb must target its declared project"
        if not instruction_id:
            return False, "Phase 8 approval/window verb requires Lucas instruction correlation"
    if verb in PHASE7_VERBS:
        actor = str(d.get("actor", ""))
        project = str(d.get("project", ""))
        if not ID_RE.fullmatch(project) or not args or args[0] != project:
            return False, "Phase 7 verb must target its declared project"
        if verb == "notification-portfolio":
            if actor != "head-hermes":
                return False, "portfolio result must be emitted by Head Hermes"
        elif not actor.startswith("pilot-") or not ID_RE.fullmatch(actor):
            return False, "Phase 7 project action requires a canonical pilot actor"
    if verb in ROUTING_RECONCILER_VERBS:
        actor = str(d.get("actor", ""))
        project = str(d.get("project", ""))
        if actor != "head-hermes" and (not actor.startswith("pilot-") or not ID_RE.fullmatch(actor)):
            return False, "routing refusal requires a canonical routed actor"
        if not ID_RE.fullmatch(project) or len(args) != 2 or args[0] != project:
            return False, "routing refusal must target its declared project"
        if re.fullmatch(r"[0-9a-f]{64}", args[1]) is None:
            return False, "routing refusal requires an exact instruction signature"
        if not instruction_id:
            return False, "routing refusal requires instruction correlation"

    for req in ("goal", "wrong_if"):
        if not str(d.get(req, "")).strip():
            return False, (
                "missing required field %r — a decision must name the goal it serves "
                "and what would make it wrong" % req
            )

    return True, json.dumps(d, separators=(",", ":"), sort_keys=True)


def main():
    try:
        if len(sys.argv) < 3:
            print("ERR usage: validate-decision.py '<verbs>' '<json>' [routed-decider]")
            return 1
        verbs = set(sys.argv[1].split())
        expected_actor = sys.argv[3] if len(sys.argv) > 3 else None
        ok, msg = validate(verbs, sys.argv[2], expected_actor)
        print(("OK " if ok else "ERR ") + (msg if ok else safe_diagnostic(msg)))
        return 0 if ok else 1
    except (OSError, ValueError, TypeError, OverflowError, RecursionError,
            UnicodeError, json.JSONDecodeError):
        print("ERR controlled validator failure")
        return 2


if __name__ == "__main__":
    sys.exit(main())
