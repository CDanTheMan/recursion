"""See whether git and the configured provider CLIs are usable.

Sign-in probes are local: a version flag, a documented status command, an
environment variable name, or the presence of a credential file. The file
contents and the command output are not returned. A missing figure is unknown.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

from scripts.v3.harness.providers import adapters


_PROBE_TIMEOUT = 10
_ENV_NAMES = {
    "cursor": ("CURSOR_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS"),
    "grok": ("XAI_API_KEY",),
}
_CLAUDE_METHODS = {"none", "claude.ai", "oauth_token", "api_key", "api_key_helper", "third_party"}
_SECRET_ENV = re.compile(r"(?i)(api[_-]?key|token|secret|password|authorization|credential)")
_TOKEN_RE = re.compile(r"(?i)(?:sk-[A-Za-z0-9]{8,}|xai-[A-Za-z0-9]{8,}|bearer\s+[A-Za-z0-9._\-]{12,})")
_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_SIGNED_IN_WORDS = {"authenticated", "logged-in", "logged_in", "ok", "success"}
_SIGNED_OUT_WORDS = {"logged-out", "logged_out", "none", "not_logged_in", "signed_out", "unauthenticated"}


def resolve_executable(
    name: str,
    *,
    path: str | None = None,
    pathext: str | None = None,
    platform: str | None = None,
) -> Path | None:
    """Return the first PATH match for ``name``, including Windows shims.

    On Windows the search also tries ``PATHEXT`` and always tries ``.exe``,
    ``.cmd``, ``.bat``, and ``.ps1``, ignoring case. An absolute path is used
    as itself.
    """

    if not name:
        return None
    direct = Path(name)
    if direct.is_absolute():
        return direct if direct.is_file() else None
    if "/" in name or "\\" in name:
        return None
    system = sys.platform if platform is None else platform
    win32 = system == "win32"
    path_value = os.environ.get("PATH", "") if path is None else path
    for directory_text in path_value.split(os.pathsep):
        if not directory_text:
            continue
        directory = Path(directory_text)
        for candidate in _candidate_names(name, win32=win32, pathext=pathext):
            found = _find_named(directory, candidate, win32=win32)
            if found is not None:
                return found
    return None


def discover_installed(
    *,
    environ: Mapping[str, str] | None = None,
    platform: str | None = None,
    path: str | None = None,
) -> list[str]:
    """Return each offline fixture plus every provider whose command resolves."""

    env = os.environ if environ is None else environ
    search = env.get("PATH", "") if path is None else path
    found = []
    for name, cls in adapters().items():
        if getattr(cls, "OFFLINE", False) or resolve_executable(
            cls.STATIC_ARGV[0], path=search, platform=platform
        ) is not None:
            found.append(name)
    return found


def live_requested(
    command: str,
    *,
    environ: Mapping[str, str] | None = None,
    platform: str | None = None,
) -> bool:
    """True only for an opted-in smoke test outside CI."""

    env = os.environ if environ is None else environ
    if env.get("CI") or env.get("GITHUB_ACTIONS"):
        return False
    if env.get("RECURSION_LIVE") != "1":
        return False
    return resolve_executable(command, path=env.get("PATH", ""), platform=platform) is not None


def diagnose(
    config: dict,
    *,
    environ: Mapping[str, str] | None = None,
    platform: str | None = None,
    home: Path | None = None,
    path: str | None = None,
    run=None,
    git_run=None,
) -> dict:
    """Report git, Windows long paths, and one row per configured provider.

    ``ok`` is true when at least one enabled provider is usable. An offline
    fixture is usable whenever it is enabled. Another provider is usable when
    it is enabled and its executable resolves.
    """

    env = os.environ if environ is None else environ
    system = sys.platform if platform is None else platform
    root = Path.home() if home is None else home
    search = env.get("PATH", "") if path is None else path
    invoke = _default_run if run is None else run
    git_invoke = _default_run if git_run is None else git_run
    rows = [
        _provider_row(item, environ=env, platform=system, home=root, path=search, run=invoke)
        for item in config["providers"]
    ]
    report = {
        "git": _git_row(platform=system, run=git_invoke),
        "ok": any(row["usable"] for row in rows),
        "providers": rows,
    }
    return _scrub(report, _secret_values(env))


def _provider_row(item: dict, *, environ, platform: str, home: Path, path: str, run) -> dict:
    name = item["name"]
    command = item["argv"][0]
    enabled = bool(item["enabled"])
    cls = adapters().get(name)
    if cls is not None and getattr(cls, "OFFLINE", False):
        return _row(
            name=name,
            command=command,
            enabled=enabled,
            installed=True,
            resolved=None,
            version=None,
            signed_in="not-applicable",
            auth_method=None,
            usable=enabled,
        )
    resolved = resolve_executable(command, path=path, platform=platform)
    version = _version(run, resolved) if resolved is not None else None
    signed_in, auth_method = _signed_in(name, resolved, environ=environ, home=home, run=run)
    installed = resolved is not None
    return _row(
        name=name,
        command=command,
        enabled=enabled,
        installed=installed,
        resolved=None if resolved is None else str(resolved),
        version=version,
        signed_in=signed_in,
        auth_method=auth_method,
        usable=enabled and installed,
    )


def _row(**fields) -> dict:
    return fields


def _signed_in(name: str, resolved: Path | None, *, environ, home: Path, run) -> tuple[str, str | None]:
    if _env_present(environ, _ENV_NAMES.get(name, ())):
        return "signed-in", "env"
    if name == "gemini":
        return _file_auth(home / ".gemini" / "oauth_creds.json")
    if name == "grok":
        return _file_auth(home / ".grok" / "auth.json")
    if name == "opencode":
        cached = _file_auth(home / ".local" / "share" / "opencode" / "auth.json")
        if cached[0] == "signed-in":
            return cached
    if resolved is None:
        return "unknown", None
    if name == "claude":
        return _claude_auth(run, resolved)
    if name == "codex":
        return _codex_auth(run, resolved)
    if name == "cursor":
        return _cursor_auth(run, resolved)
    if name == "opencode":
        return _opencode_auth(run, resolved)
    return "unknown", None


def _env_present(environ: Mapping[str, str], names: tuple[str, ...]) -> bool:
    return any(bool(environ.get(name)) for name in names)


def _file_auth(path: Path) -> tuple[str, str | None]:
    try:
        if path.is_file() and path.stat().st_size > 0:
            return "signed-in", "cached"
    except OSError:
        return "unknown", None
    return "signed-out", None


def _claude_auth(run, resolved: Path) -> tuple[str, str | None]:
    completed = _capture(run, [str(resolved), "auth", "status"])
    if completed is None:
        return "unknown", None
    method = _claude_method(completed.stdout or "")
    if completed.returncode == 0:
        return "signed-in", method or "status"
    if completed.returncode == 1:
        return "signed-out", method
    return "unknown", None


def _claude_method(stdout: str) -> str | None:
    payload = _json_object(stdout)
    if not isinstance(payload, dict):
        return None
    method = payload.get("authMethod")
    if isinstance(method, str) and method in _CLAUDE_METHODS:
        return method
    return None


def _codex_auth(run, resolved: Path) -> tuple[str, str | None]:
    completed = _capture(run, [str(resolved), "login", "status"])
    if completed is None:
        return "unknown", None
    if completed.returncode == 0:
        return "signed-in", "login-status"
    return "signed-out", "login-status"


def _cursor_auth(run, resolved: Path) -> tuple[str, str | None]:
    completed = _capture(run, [str(resolved), "status", "--format", "json"])
    if completed is None:
        return "unknown", None
    state = _cursor_state(completed.stdout or "")
    if state == "unknown":
        return "unknown", None
    return state, "status"


def _cursor_state(stdout: str) -> str:
    payload = _json_object(stdout)
    if isinstance(payload, dict):
        for key in ("authenticated", "isAuthenticated", "loggedIn", "logged_in", "isLoggedIn"):
            value = payload.get(key)
            if isinstance(value, bool):
                return "signed-in" if value else "signed-out"
        for key in ("status", "state", "auth"):
            value = payload.get(key)
            if not isinstance(value, str):
                continue
            word = value.strip().lower().replace(" ", "_")
            if word in _SIGNED_IN_WORDS:
                return "signed-in"
            if word in _SIGNED_OUT_WORDS:
                return "signed-out"
    lowered = stdout.lower()
    if any(phrase in lowered for phrase in ("not logged in", "logged out", "not authenticated", "signed out")):
        return "signed-out"
    if any(phrase in lowered for phrase in ("logged in", "authenticated")):
        return "signed-in"
    return "unknown"


def _opencode_auth(run, resolved: Path) -> tuple[str, str | None]:
    completed = _capture(run, [str(resolved), "auth", "list"])
    if completed is None or completed.returncode != 0:
        return "unknown", None
    state = _opencode_state(completed.stdout or "")
    if state == "unknown":
        return "unknown", None
    return state, "auth-list"


def _opencode_state(stdout: str) -> str:
    """Read ``opencode auth list`` without keeping credential names or secrets.

    A JSON array of integrations is accepted when the body is JSON. An empty
    array is signed out. The text form is a credentials count, ``No
    authenticated integrations``, or a table whose rows end in ``stored`` or
    ``environment``. ANSI color codes are removed before that read.
    """

    stripped = _ANSI.sub("", stdout).strip()
    if not stripped:
        return "unknown"
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        payload = None
    if isinstance(payload, list):
        return "signed-in" if payload else "signed-out"
    if isinstance(payload, dict):
        for key in ("integrations", "credentials", "providers"):
            value = payload.get(key)
            if isinstance(value, list):
                return "signed-in" if value else "signed-out"
        return "signed-in" if payload else "signed-out"
    lowered = stripped.lower()
    if "no authenticated integrations" in lowered or "no credentials" in lowered:
        return "signed-out"
    if re.search(r"\b[1-9]\d*\s+credentials\b", lowered):
        return "signed-in"
    if re.search(r"\b0\s+credentials\b", lowered):
        return "signed-out"
    if re.search(r"(?m)\b(?:stored|environment)\s*$", lowered):
        return "signed-in"
    return "unknown"


def _version(run, resolved: Path) -> str | None:
    completed = _capture(run, [str(resolved), "--version"])
    if completed is None or completed.returncode != 0:
        return None
    for line in (completed.stdout or "").splitlines():
        text = line.strip()
        if text:
            return text[:200]
    return None


def _git_row(*, platform: str, run) -> dict:
    completed = _capture(run, ["git", "--version"])
    if completed is None or completed.returncode != 0:
        return {"available": False, "longpaths": None, "version": None}
    version = None
    for line in (completed.stdout or "").splitlines():
        text = line.strip()
        if text:
            version = text[:200]
            break
    longpaths = _longpaths(run) if platform == "win32" else None
    return {"available": True, "longpaths": longpaths, "version": version}


def _longpaths(run) -> bool:
    completed = _capture(run, ["git", "config", "--get", "core.longpaths"])
    if completed is None:
        return False
    return (completed.stdout or "").strip().lower() in {"1", "true", "yes"}


def _capture(run, argv: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        completed = run(list(argv), _PROBE_TIMEOUT)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if not isinstance(completed, subprocess.CompletedProcess):
        return None
    return completed


def _default_run(argv: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        stdin=subprocess.DEVNULL,
        timeout=timeout,
    )


def _candidate_names(name: str, *, win32: bool, pathext: str | None) -> list[str]:
    names = [name]
    if not win32:
        return names
    suffixes: list[str] = []
    raw = ".COM;.EXE;.BAT;.CMD" if pathext is None else pathext
    for piece in raw.split(";"):
        piece = piece.strip()
        if not piece:
            continue
        if not piece.startswith("."):
            piece = "." + piece
        suffixes.append(piece)
    for required in (".exe", ".cmd", ".bat", ".ps1"):
        if required.casefold() not in {item.casefold() for item in suffixes}:
            suffixes.append(required)
    seen = {name.casefold()}
    for suffix in suffixes:
        if name.casefold().endswith(suffix.casefold()):
            continue
        candidate = name + suffix
        if candidate.casefold() in seen:
            continue
        seen.add(candidate.casefold())
        names.append(candidate)
    return names


def _find_named(directory: Path, candidate: str, *, win32: bool) -> Path | None:
    if not win32:
        direct = directory / candidate
        return direct if direct.is_file() else None
    # Windows Path.is_file matches any case and reports the name we asked for.
    # Scan the directory so the result keeps the on-disk shim name.
    if not directory.is_dir():
        return None
    target = candidate.casefold()
    try:
        entries = list(directory.iterdir())
    except OSError:
        return None
    for entry in entries:
        if entry.name.casefold() == target and entry.is_file():
            return entry
    return None


def _json_object(text: str) -> dict | None:
    stripped = text.strip()
    if not stripped.startswith("{"):
        return None
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _secret_values(environ: Mapping[str, str]) -> list[str]:
    values = []
    for key, value in environ.items():
        if isinstance(value, str) and len(value) >= 8 and _SECRET_ENV.search(key):
            values.append(value)
    values.sort(key=len, reverse=True)
    return values


def _scrub(value: object, secrets: list[str]) -> object:
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            if secret and secret in redacted:
                redacted = redacted.replace(secret, "[redacted]")
        return _TOKEN_RE.sub("[redacted]", redacted)
    if isinstance(value, list):
        return [_scrub(item, secrets) for item in value]
    if isinstance(value, dict):
        return {key: _scrub(item, secrets) for key, item in value.items()}
    return value
