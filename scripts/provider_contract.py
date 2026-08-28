"""Fail-closed provider egress profile contract (Phase 4).

Profiles describe a provider capability; they never contain credentials.  The shipped
profiles are deliberately disabled.  This module is shared by the offline resolver and
the proxy/sandbox boundary so an endpoint cannot be admitted by one layer and rejected
or broadened by another.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable


NAME_RE = re.compile(r"[a-z][a-z0-9-]{1,63}\Z")
HOST_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+\Z")
ENV_RE = re.compile(r"[A-Z][A-Z0-9_]{2,63}\Z")
NAMESPACE_RE = re.compile(r"recursion-provider-[a-z0-9-]{1,40}\Z")
PROXY_ENV = frozenset({"HTTP_PROXY", "HTTPS_PROXY"})
PROFILE_KEYS = {"schema_version", "id", "provider", "enabled", "namespace", "proxy", "authorities"}
PROXY_KEYS = {"type", "host", "port", "env"}
DEPLOYED_PROFILE_DIR = Path("/etc/recursion/providers")
ENGINE_PROFILE_MAP = {
    "claude": "anthropic",
    "hermes": "anthropic",
    "cursor": "cursor",
    "gemini": "google-gemini",
    "opencode": "openrouter-via-opencode",
}


class ProviderProfileError(ValueError):
    """A provider profile is absent, malformed, disabled, or mismatched."""


def parse_authority(value: object) -> tuple[str, int]:
    if not isinstance(value, str) or value.count(":") != 1:
        raise ProviderProfileError("authority must be a DNS name and explicit port")
    host, port_text = value.rsplit(":", 1)
    if not HOST_RE.fullmatch(host.lower()) or not port_text.isascii() or not port_text.isdecimal():
        raise ProviderProfileError("authority must be a canonical DNS name and explicit port")
    port = int(port_text, 10)
    if not 1 <= port <= 65535:
        raise ProviderProfileError("authority port is out of range")
    return host.lower(), port


def _require_dict(value: object, keys: set[str], where: str) -> dict:
    if not isinstance(value, dict):
        raise ProviderProfileError(f"{where} must be an object")
    missing = keys - value.keys()
    extra = value.keys() - keys
    if missing:
        raise ProviderProfileError(f"{where} missing key(s): {', '.join(sorted(missing))}")
    if extra:
        raise ProviderProfileError(f"{where} has unknown key(s): {', '.join(sorted(extra))}")
    return value


def validate_profile(value: object, expected_id: str | None = None) -> dict:
    profile = _require_dict(value, PROFILE_KEYS, "provider profile")
    if profile["schema_version"] != 1:
        raise ProviderProfileError("schema_version must be 1")
    profile_id = profile["id"]
    provider = profile["provider"]
    if not isinstance(profile_id, str) or not NAME_RE.fullmatch(profile_id):
        raise ProviderProfileError("id is not a valid profile name")
    if expected_id is not None and profile_id != expected_id:
        raise ProviderProfileError("profile id does not match requested provider")
    if not isinstance(provider, str) or not NAME_RE.fullmatch(provider):
        raise ProviderProfileError("provider is not a valid provider name")
    if not isinstance(profile["enabled"], bool):
        raise ProviderProfileError("enabled must be a boolean")
    namespace = profile["namespace"]
    if not isinstance(namespace, str) or not NAMESPACE_RE.fullmatch(namespace):
        raise ProviderProfileError("namespace must be a fixed recursion-provider namespace name")
    proxy = _require_dict(profile["proxy"], PROXY_KEYS, "proxy")
    if proxy["type"] != "connect-proxy":
        raise ProviderProfileError('proxy.type must be "connect-proxy"')
    if proxy["host"] != "127.0.0.1":
        raise ProviderProfileError("proxy.host must be the loopback proxy boundary")
    if not isinstance(proxy["port"], int) or isinstance(proxy["port"], bool) \
            or not 1 <= proxy["port"] <= 65535:
        raise ProviderProfileError("proxy.port must be an integer in 1..65535")
    env = proxy["env"]
    if not isinstance(env, list) or len(set(env)) != len(env) \
            or not all(isinstance(name, str) and ENV_RE.fullmatch(name) for name in env):
        raise ProviderProfileError("proxy.env must contain unique environment variable names")
    if set(env) != PROXY_ENV:
        raise ProviderProfileError("proxy.env must inject exactly HTTP_PROXY and HTTPS_PROXY")
    authorities = profile["authorities"]
    if not isinstance(authorities, list) or len(set(authorities)) != len(authorities):
        raise ProviderProfileError("authorities must be a unique list")
    parsed = [parse_authority(item) for item in authorities]
    if not parsed:
        raise ProviderProfileError("at least one provider authority is required")
    return profile


def load_profile(path: Path, expected_id: str | None = None) -> dict:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProviderProfileError(f"provider profile is unreadable: {path}") from exc
    return validate_profile(raw, expected_id)


def profile_directory(script_dir: Path | str) -> Path:
    override = os.environ.get("RECURSION_PROVIDER_DIR", "").strip()
    # The checked-in profiles are review fixtures, not an implicit production source.  The
    # deployed proxy and every resolver must read the same human-owned /etc directory.
    return Path(override) if override else DEPLOYED_PROFILE_DIR


def profile_for_provider(provider: str, directory: Path) -> dict:
    if not isinstance(provider, str) or not NAME_RE.fullmatch(provider):
        raise ProviderProfileError("provider name is invalid")
    return load_profile(directory / f"{provider}.json", provider)


def assert_endpoints_match(profile: dict, endpoints: Iterable[str]) -> None:
    expected = {str(item).lower() for item in endpoints}
    actual = {host for host, _ in (parse_authority(item) for item in profile["authorities"])}
    if expected != actual:
        raise ProviderProfileError("profile authorities do not exactly match engine endpoints")


def proxy_environment(profile: dict, endpoints: Iterable[str]) -> dict[str, str]:
    validate_profile(profile)
    assert_endpoints_match(profile, endpoints)
    if not profile["enabled"]:
        raise ProviderProfileError("provider egress profile is disabled")
    value = f"http://{profile['proxy']['host']}:{profile['proxy']['port']}"
    return {name: value for name in profile["proxy"]["env"]}


def enabled_allowlist(directory: Path, profiles: Iterable[str] | None = None) -> set[tuple[str, int]]:
    names = list(profiles) if profiles is not None else enabled_profile_names(directory)
    if not names:
        raise ProviderProfileError("no provider profiles were selected")
    allowed: set[tuple[str, int]] = set()
    for name in names:
        profile = profile_for_provider(name, directory)
        if not profile["enabled"]:
            raise ProviderProfileError(f"provider egress profile is disabled: {name}")
        allowed.update(parse_authority(item) for item in profile["authorities"])
    return allowed


def enabled_profile_names(directory: Path) -> list[str]:
    """Return only profiles whose human-owned record explicitly says enabled=true."""
    names: list[str] = []
    for path in sorted(directory.glob("*.json")):
        profile = load_profile(path, path.stem)
        if profile["enabled"]:
            names.append(profile["id"])
    if not names:
        raise ProviderProfileError("all provider profiles are disabled; refusing provider egress")
    return names


def engine_profile(engine: str, directory: Path, endpoints: Iterable[str] | None = None) -> dict:
    """Authenticate one engine assignment to exactly one enabled provider profile."""
    if not isinstance(engine, str) or not NAME_RE.fullmatch(engine):
        raise ProviderProfileError("engine name is invalid")
    profile_name = ENGINE_PROFILE_MAP.get(engine)
    if profile_name is None:
        raise ProviderProfileError(f"no provider profile is bound to engine: {engine}")
    profile = profile_for_provider(profile_name, directory)
    if endpoints is not None:
        assert_endpoints_match(profile, endpoints)
    if not profile["enabled"]:
        raise ProviderProfileError(f"provider egress profile is disabled: {profile_name}")
    return profile
