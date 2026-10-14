"""Opt-in live smoke for signed-in provider CLIs.

``recursion doctor --live`` is the only caller. The default doctor command
and the test suite do not send a prompt. A ``CI`` or ``GITHUB_ACTIONS``
environment refuses before any provider process starts.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from collections.abc import Mapping
from pathlib import Path

from scripts.v3.harness.doctor import diagnose
from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.providers import ProviderRequest, open_provider
from scripts.v3.harness.streams import parse_transcript


LIVE_PROMPT = "Reply with the single word pong. Do not use tools and do not change any files."
_TEXT_LIMIT = 200


def smoke_live(
    config: dict,
    *,
    environ: Mapping[str, str] | None = None,
    diagnose_fn=diagnose,
    execute=None,
    make_repo=None,
) -> dict:
    """Prompt each enabled, signed-in provider once and attach the results.

    ``live_ok`` is true when every attempted prompt passed. It is also true
    when no provider was attempted. Skipped providers are listed and do not
    count as failures.
    """

    env = os.environ if environ is None else environ
    if env.get("CI") or env.get("GITHUB_ACTIONS"):
        raise HarnessError("doctor --live does not run in CI")
    report = dict(diagnose_fn(config))
    run = _execute if execute is None else execute
    repo_of = make_smoke_repo if make_repo is None else make_repo
    rows = []
    attempted = 0
    passed = 0
    for item in report.get("providers", []):
        row = _one(item, config, execute=run, make_repo=repo_of)
        rows.append(row)
        if row["status"] == "ran":
            attempted += 1
            if row["ok"]:
                passed += 1
    report["live"] = rows
    report["live_ok"] = passed == attempted
    return report


def make_smoke_repo() -> Path:
    """Create a throwaway git repo with one commit. Global git config is untouched."""

    root = Path(tempfile.mkdtemp(prefix="recursion-smoke-"))
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "recursion"
    env["GIT_AUTHOR_EMAIL"] = "recursion@localhost"
    env["GIT_COMMITTER_NAME"] = "recursion"
    env["GIT_COMMITTER_EMAIL"] = "recursion@localhost"

    def git(*args: str) -> None:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise HarnessError("smoke repository could not be created")

    try:
        git("init", "-q")
        (root / "README.md").write_text("smoke\n", encoding="utf-8")
        git("add", "README.md")
        git("-c", "commit.gpgsign=false", "commit", "-q", "-m", "smoke")
    except Exception:
        shutil.rmtree(root, ignore_errors=True)
        raise
    return root


def _one(item: dict, config: dict, *, execute, make_repo) -> dict:
    name = item["name"]
    reason = _skip_reason(item)
    if reason is not None:
        return {"error": None, "name": name, "ok": None, "reason": reason, "status": "skipped", "text": None}
    repo = None
    try:
        repo = make_repo()
        request = ProviderRequest(
            task=LIVE_PROMPT,
            packet_id="PACKET-SMOKE",
            route_id="route-a",
            kind="execute",
            cwd=str(repo),
        )
        result = execute(name, request, _timeout(config, name))
        parsed = parse_transcript(name, result.text)
        body = parsed["text"].strip()
        if not body:
            return {
                "error": "empty transcript",
                "name": name,
                "ok": False,
                "reason": None,
                "status": "ran",
                "text": None,
            }
        return {
            "error": None,
            "name": name,
            "ok": True,
            "reason": None,
            "status": "ran",
            "text": body[:_TEXT_LIMIT],
        }
    except Exception as exc:
        message = str(exc).strip() or type(exc).__name__
        return {
            "error": message[:_TEXT_LIMIT],
            "name": name,
            "ok": False,
            "reason": None,
            "status": "ran",
            "text": None,
        }
    finally:
        if repo is not None:
            shutil.rmtree(repo, ignore_errors=True)


def _skip_reason(item: dict) -> str | None:
    if item["name"] == "fixture":
        return "not-a-cli"
    if not item.get("enabled"):
        return "disabled"
    if not item.get("installed"):
        return "not-installed"
    if item.get("signed_in") != "signed-in":
        return "not-signed-in"
    return None


def _timeout(config: dict, name: str) -> int:
    for item in config["providers"]:
        if item["name"] == name:
            return int(item["timeout_seconds"])
    return 120


def _execute(name: str, request: ProviderRequest, timeout: int):
    return open_provider(name).execute(request, allow_live=True, timeout_seconds=timeout)
