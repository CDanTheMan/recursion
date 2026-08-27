#!/usr/bin/env python3
"""verify-branch-protection.py — machine-checkable close-out for esc-0001.

esc-0001 ("Disable autonomous merging and verify branch protection") cannot be closed by
anyone asserting that it is done. It closes when three facts are checked and one of them —
the state of GitHub itself — is checked against GitHub, not against a note in this repo:

  1. env       RECURSION_ALLOW_AUTOMERGE must be unset or "0".
  2. tasks     no state/tasks/*.md may carry an enabling `automerge:` (or a leftover
               `automerge_scope:`) in its header region. Both fields are named in the
               recorded remediation, state/PROPOSALS.md step 2.
  3. remote    for every ACTIVE row in state/portfolio.tsv, the registered default branch
               must actually be protected on GitHub — classic branch protection, or a
               ruleset carrying a pull_request / update rule that the caller cannot bypass.

It fails CLOSED. "I could not check" is never reported as "protected": a row that cannot be
resolved, reached, or read comes back UNVERIFIABLE and the run exits 3. A verifier that
answers "clean" when it learned nothing is worse than no verifier, because it retires a real
escalation with a fabricated fact.

Exit codes:
  0  every check verified clean
  1  at least one VIOLATION (including an UNPROTECTED default branch)
  2  usage or input error (bad argument, missing root, unreadable portfolio)
  3  no VIOLATION, but at least one UNVERIFIABLE row — protection cannot be claimed

Auth: GITHUB_TOKEN or GH_TOKEN, sent as a Bearer header. With no token every remote row is
UNVERIFIABLE (exit 3) — the tool never guesses from a public, unauthenticated read. The token
value is scrubbed out of every line this program prints or writes.

Reading classic branch protection requires admin rights on the repo; a read-only token gets
403 and the row is reported UNVERIFIABLE, which is the honest answer.

Test hook: RECURSION_GH_API_BASE redirects the API base URL, in the same spirit as
RECURSION_ENGINE_DIR. It exists so scripts/tests/verify-branch-protection.test.py can stub
the API on 127.0.0.1. It is NEVER set on the box; if it is set, the run says so on every
remote line so no stubbed result can be mistaken for evidence about GitHub.

  scripts/verify-branch-protection.py [--root PATH] [--json PATH] [--quiet]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROG = "verify-branch-protection"
API_DEFAULT = "https://api.github.com"
TIMEOUT_S = 15

# Values that mean "automerge is off". Anything else is read as a grant, including a value
# nobody recognizes — an unknown setting for this field is not a safe setting.
AUTOMERGE_OFF = {"", "no", "false", "0", "off"}

# Ruleset rule types that actually stop a fast-forward push to the default branch, which is
# the exact move esc-0001 is about. `non_fast_forward`, `deletion` and `creation` do not stop
# it, so they are deliberately NOT here: a repo carrying only those is UNPROTECTED.
RULESET_BLOCKING_TYPES = {"pull_request", "update"}

SSH_REMOTE_RE = re.compile(r"^git@github\.com:([^/\s]+)/(.+?)(?:\.git)?$")
HTTPS_REMOTE_RE = re.compile(r"^https://github\.com/([^/\s]+)/(.+?)(?:\.git)?/?$")

VIOLATION_STATUSES = {"VIOLATION", "UNPROTECTED"}


def scrub(text: str, secrets: list[str]) -> str:
    """Never let a credential reach stdout, stderr, or the evidence file."""
    for secret in secrets:
        if secret:
            text = text.replace(secret, "***")
    return text


def scrub_tree(value, secrets):
    """Scrub the record itself, not its serialization — a token containing a character that
    JSON escapes would survive a scrub applied to the dumped text."""
    if isinstance(value, str):
        return scrub(value, secrets)
    if isinstance(value, list):
        return [scrub_tree(item, secrets) for item in value]
    if isinstance(value, dict):
        return {scrub(str(key), secrets): scrub_tree(item, secrets)
                for key, item in value.items()}
    return value


def result(check: str, status: str, subject: str, detail: str, **extra) -> dict:
    record = {"check": check, "status": status, "subject": subject, "detail": detail}
    record.update(extra)
    return record


# --- 1. env ---------------------------------------------------------------------------


def check_env(environ) -> dict:
    raw = environ.get("RECURSION_ALLOW_AUTOMERGE")
    if raw is None:
        return result("env", "OK", "RECURSION_ALLOW_AUTOMERGE", "unset")
    value = raw.strip()
    if value == "0":
        return result("env", "OK", "RECURSION_ALLOW_AUTOMERGE", 'set to "0"')
    return result(
        "env", "VIOLATION", "RECURSION_ALLOW_AUTOMERGE",
        f'set to "{value}" — must be unset or "0" in the box .env (human action)',
    )


# --- 2. tasks -------------------------------------------------------------------------


def header_fields(text: str) -> dict:
    """`key: value` lines up to the first blank line. The body is prose, not contract."""
    fields = {}
    for line in text.splitlines():
        if not line.strip():
            break
        key, separator, value = line.partition(":")
        if separator and key.strip():
            fields.setdefault(key.strip().lower(), value.strip())
    return fields


def check_tasks(root: Path) -> list[dict]:
    task_dir = root / "state" / "tasks"
    if not task_dir.is_dir():
        return [result("tasks", "OK", "state/tasks", "no task directory to scan")]
    results, scanned = [], 0
    for task in sorted(task_dir.glob("*.md")):
        try:
            text = task.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            results.append(result(
                "tasks", "UNVERIFIABLE", f"state/tasks/{task.name}",
                f"task file could not be read ({exc.__class__.__name__})",
            ))
            continue
        scanned += 1
        fields = header_fields(text)
        offences = []
        automerge = fields.get("automerge", "").strip().lower()
        if "automerge" in fields and automerge not in AUTOMERGE_OFF:
            offences.append(f"automerge: {fields['automerge']}")
        scope = fields.get("automerge_scope", "").strip()
        if scope:
            offences.append(f"automerge_scope: {scope}")
        if offences:
            results.append(result(
                "tasks", "VIOLATION", f"state/tasks/{task.name}",
                "header carries " + " and ".join(offences) + " (human action: remove it)",
            ))
    # The summary line is only earned by a scan that flagged nothing at all. A run that could
    # not read a file has not established "none carries automerge".
    if not results:
        results.append(result(
            "tasks", "OK", "state/tasks",
            f"{scanned} task file(s) scanned, none carries automerge",
        ))
    return results


# --- 3. remote protection -------------------------------------------------------------


def parse_remote(remote: str):
    """(owner, repo) for a GitHub remote, else None. Anything else is not ours to judge."""
    candidate = (remote or "").strip()
    for pattern in (SSH_REMOTE_RE, HTTPS_REMOTE_RE):
        match = pattern.match(candidate)
        if match:
            owner, repo = match.group(1), match.group(2).strip("/")
            if owner and repo and "/" not in repo:
                return owner, repo
    return None


def read_portfolio(path: Path):
    """Parse state/portfolio.tsv the way scripts/publish.sh registry_row() does.

    Columns: project, path, remote, branch(default), key, roadmap, topic, status. Comment and
    blank lines are skipped; a row with fewer than 8 fields leaves `status` empty, so
    publish.sh skips it and so do we — it is counted and reported, never silently dropped.

    One deliberate divergence: a trailing CR is stripped. publish.sh does not, so a CRLF
    portfolio would make every row read as status "active\\r" and be skipped — which would
    make this verifier check nothing while reporting success. Stripping fails closed.
    """
    rows, malformed = [], []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) < 8:
            malformed.append(number)
            continue
        project, repo_path, remote, branch, key, roadmap, topic, status = fields[:8]
        if status.strip() != "active":
            continue
        rows.append({
            "project": project.strip(), "path": repo_path.strip(),
            "remote": remote.strip(), "branch": branch.strip(),
            "key": key.strip(), "line": number,
        })
    return rows, malformed


def github_get(base: str, path: str, token: str):
    """(status_code, payload, error). Any failure is an error, never an assumption."""
    url = base.rstrip("/") + path
    request = urllib.request.Request(url, method="GET")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("User-Agent", PROG)
    request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_S) as response:
            body = response.read()
            try:
                payload = json.loads(body.decode("utf-8")) if body else None
            except (UnicodeDecodeError, json.JSONDecodeError):
                return response.status, None, "response was not JSON"
            return response.status, payload, None
    except urllib.error.HTTPError as exc:
        try:
            exc.read()
        except Exception:  # noqa: BLE001 - draining the body must never mask the status
            pass
        return exc.code, None, None
    except urllib.error.URLError as exc:
        return None, None, f"request failed ({exc.reason})"
    except OSError as exc:
        return None, None, f"request failed ({exc.__class__.__name__})"


def rule_blocks_push(rule) -> bool:
    if not isinstance(rule, dict):
        return False
    if str(rule.get("type", "")).strip() not in RULESET_BLOCKING_TYPES:
        return False
    if str(rule.get("current_user_can_bypass", "")).strip() == "always":
        return False
    actors = rule.get("bypass_actors")
    if isinstance(actors, list) and actors:
        return False
    return True


def check_remote(row: dict, base: str, token: str, stubbed: bool) -> dict:
    project, branch = row["project"], row["branch"]
    subject = f"{project}@{branch or '?'}"
    common = {"project": project, "branch": branch, "portfolio_line": row["line"]}
    note = " [RECURSION_GH_API_BASE is set: stubbed, not GitHub]" if stubbed else ""

    if not branch:
        return result("remote", "UNVERIFIABLE", subject,
                      "portfolio row has no registered default branch", **common)
    owned = parse_remote(row["remote"])
    if owned is None:
        # The remote is echoed because the human has to go fix the row, and it is echoed
        # through scrub() because a `https://user:token@host/...` remote is the classic way a
        # credential ends up in a log.
        return result("remote", "UNVERIFIABLE", subject,
                      f"remote is not a recognized GitHub URL, so protection cannot be checked "
                      f"here: {row['remote']}", **common)
    owner, repo = owned
    common.update({"owner": owner, "repo": repo})
    if not token:
        return result("remote", "UNVERIFIABLE", subject,
                      "no GITHUB_TOKEN or GH_TOKEN in the environment", **common)

    evidence = {}
    status, _payload, error = github_get(
        base, f"/repos/{owner}/{repo}/branches/{branch}/protection", token)
    evidence["classic"] = error or status
    if error:
        return result("remote", "UNVERIFIABLE", subject,
                      f"classic protection query failed: {error}{note}",
                      evidence=evidence, **common)
    if status == 200:
        return result("remote", "PROTECTED", subject,
                      f"classic branch protection is enabled{note}",
                      method="classic", evidence=evidence, **common)
    if status != 404:
        return result("remote", "UNVERIFIABLE", subject,
                      f"classic protection query returned HTTP {status} "
                      f"(a read-only token cannot read protection){note}",
                      evidence=evidence, **common)

    status, payload, error = github_get(
        base, f"/repos/{owner}/{repo}/rules/branches/{branch}", token)
    evidence["rulesets"] = error or status
    if error or status != 200:
        return result("remote", "UNVERIFIABLE", subject,
                      f"classic protection is absent and the ruleset query "
                      f"{error or f'returned HTTP {status}'} — cannot tell protected from "
                      f"unprotected{note}", evidence=evidence, **common)
    rules = payload if isinstance(payload, list) else []
    blocking = [str(rule.get("type")) for rule in rules if rule_blocks_push(rule)]
    if blocking:
        return result("remote", "PROTECTED", subject,
                      f"ruleset rule(s) {', '.join(sorted(set(blocking)))} restrict pushes to "
                      f"the default branch{note}",
                      method="ruleset", evidence=evidence, **common)
    return result("remote", "UNPROTECTED", subject,
                  f"no classic protection and no blocking ruleset rule "
                  f"({len(rules)} rule(s) apply) — the default branch accepts direct "
                  f"pushes{note}", evidence=evidence, **common)


# --- evidence -------------------------------------------------------------------------


def write_evidence(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=str(path.parent))
    temporary = Path(name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as out:
            json.dump(record, out, indent=2, sort_keys=True)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


# --- entry point ----------------------------------------------------------------------


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog=PROG, description="Verify esc-0001 close-out facts.")
    parser.add_argument("--root", help="control-plane root (default: $RECURSION_ROOT)")
    parser.add_argument("--json", dest="json_path", help="write an evidence record here")
    parser.add_argument("--quiet", action="store_true", help="evidence file only, no stdout")
    args = parser.parse_args(argv)

    environ = os.environ
    token = (environ.get("GITHUB_TOKEN") or environ.get("GH_TOKEN") or "").strip()
    secrets = [
        value for value in (environ.get("GITHUB_TOKEN"), environ.get("GH_TOKEN"), token)
        if value and value.strip()
    ]
    base_override = environ.get("RECURSION_GH_API_BASE", "").strip()
    base = base_override or API_DEFAULT

    root = Path(args.root or environ.get("RECURSION_ROOT")
                or Path(__file__).resolve().parents[1]).resolve()
    if not root.is_dir():
        print(scrub(f"{PROG}: root is not a directory: {root}", secrets), file=sys.stderr)
        return 2

    results = [check_env(environ)]
    results.extend(check_tasks(root))

    portfolio = root / "state" / "portfolio.tsv"
    if not portfolio.is_file():
        print(scrub(f"{PROG}: no portfolio registry: {portfolio}", secrets), file=sys.stderr)
        return 2
    try:
        rows, malformed = read_portfolio(portfolio)
    except OSError as exc:
        print(scrub(f"{PROG}: portfolio unreadable ({exc.__class__.__name__})", secrets),
              file=sys.stderr)
        return 2

    if malformed:
        results.append(result(
            "portfolio", "SKIPPED", "state/portfolio.tsv",
            f"{len(malformed)} malformed row(s) skipped at line(s) "
            f"{', '.join(str(number) for number in malformed)} — fewer than 8 tab-separated "
            "fields, so publish.sh cannot resolve them either",
            malformed_lines=malformed,
        ))
    for row in rows:
        results.append(check_remote(row, base, token, bool(base_override)))

    violations = [item for item in results if item["status"] in VIOLATION_STATUSES]
    unverifiable = [item for item in results if item["status"] == "UNVERIFIABLE"]
    if violations:
        verdict, code = "violation", 1
    elif unverifiable:
        verdict, code = "unverifiable", 3
    else:
        verdict, code = "clean", 0

    lines = [
        f"{item['check']}: {item['status']} {item['subject']} — {item['detail']}"
        for item in results
    ]
    lines.append(
        f"verdict: {verdict.upper()} ({len(violations)} violation(s), "
        f"{len(unverifiable)} unverifiable) exit={code}"
    )
    if not args.quiet:
        for line in lines:
            print(scrub(line, secrets))

    if args.json_path:
        record = {
            "schema_version": 1,
            "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "results": scrub_tree(results, secrets),
            "verdict": verdict,
        }
        try:
            write_evidence(Path(args.json_path), record)
        except OSError as exc:
            print(scrub(f"{PROG}: could not write evidence ({exc.__class__.__name__})",
                        secrets), file=sys.stderr)
            return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
