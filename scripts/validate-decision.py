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
import re
import sys

ARG_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,80}")
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
AUTHORING_TEXT_VERBS = {"roadmap-add", "note", "assist-answer"}
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
    "escalate": (1, 3),
}


def validate(verbs, raw):
    """Return (ok: bool, message: str)."""
    try:
        d = json.loads(raw)
    except Exception as e:
        return False, "malformed JSON: %s" % e
    if not isinstance(d, dict):
        return False, "decision is not an object"

    verb = str(d.get("verb", "")).strip()
    if verb not in verbs:
        return False, "verb %r is not on the whitelist" % verb

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

    instruction_id = d.get("instruction_id")
    if instruction_id is not None and not ID_RE.fullmatch(str(instruction_id)):
        return False, "instruction_id is not a canonical identifier"
    if verb == "assist-answer" and not instruction_id:
        return False, "assist-answer requires instruction_id correlation"

    for req in ("goal", "wrong_if"):
        if not str(d.get(req, "")).strip():
            return False, (
                "missing required field %r — a decision must name the goal it serves "
                "and what would make it wrong" % req
            )

    return True, json.dumps(d, separators=(",", ":"), sort_keys=True)


def main():
    if len(sys.argv) < 3:
        print("ERR usage: validate-decision.py '<verbs>' '<json>'")
        return 1
    verbs = set(sys.argv[1].split())
    ok, msg = validate(verbs, sys.argv[2])
    print(("OK " if ok else "ERR ") + msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
