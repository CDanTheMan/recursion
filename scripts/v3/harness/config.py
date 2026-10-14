"""Load the provider config. The file names commands and capabilities, not secrets."""

from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.providers import adapters


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / "config" / "harness.json"
_SECRET_KEY = re.compile(
    r"(?i)^(api[_-]?key|token|secret|password|authorization|credential|xai_api_key)$"
)


def default_config_path() -> Path:
    return DEFAULT_CONFIG


def load_config(path: Path | None = None) -> dict:
    """Read and check one provider config.

    Provider argv and capabilities must match the adapter classes. Credential
    keys are refused so a config cannot become a secret store.
    """

    source = Path(path) if path is not None else DEFAULT_CONFIG
    if not source.is_file():
        raise HarnessError(f"missing provider config {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HarnessError(f"provider config is not JSON: {source}") from exc
    _reject_secrets(payload)
    if not isinstance(payload, dict):
        raise HarnessError("provider config must be an object")
    _require_exact_keys(payload, {"providers", "routing", "version"}, "config")
    version = payload["version"]
    if isinstance(version, bool) or version != 1:
        raise HarnessError("provider config version must be 1")
    providers = _providers(payload["providers"])
    routing = _routing(payload["routing"], [item["name"] for item in providers])
    return {"providers": providers, "routing": routing, "version": 1}


def _require_exact_keys(value: dict, expected: set[str], where: str) -> None:
    found = set(value)
    if found != expected:
        missing = sorted(expected - found)
        extra = sorted(found - expected)
        raise HarnessError(f"{where} keys mismatch; missing={missing} extra={extra}")


def _reject_secrets(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or _SECRET_KEY.fullmatch(key):
                raise HarnessError(f"config key {key!r} is not allowed")
            _reject_secrets(item)
    elif isinstance(value, list):
        for item in value:
            _reject_secrets(item)


def _providers(value: object) -> list[dict]:
    if not isinstance(value, list) or not value:
        raise HarnessError("config providers must be a non-empty list")
    known = adapters()
    parsed = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            raise HarnessError("each provider entry must be an object")
        _require_exact_keys(item, {"argv", "capabilities", "enabled", "name"}, "provider")
        name = item["name"]
        if not isinstance(name, str) or name not in known:
            raise HarnessError(f"unknown provider in config: {name!r}")
        if name in seen:
            raise HarnessError(f"duplicate provider in config: {name}")
        seen.add(name)
        if not isinstance(item["enabled"], bool):
            raise HarnessError(f"provider {name} enabled must be a boolean")
        argv = _string_tuple(item["argv"], f"provider {name} argv")
        capabilities = _string_tuple(item["capabilities"], f"provider {name} capabilities")
        cls = known[name]
        if argv != cls.STATIC_ARGV:
            raise HarnessError(f"provider {name} argv does not match the adapter")
        if capabilities != cls.CAPABILITIES:
            raise HarnessError(f"provider {name} capabilities do not match the adapter")
        parsed.append(
            {
                "argv": list(argv),
                "capabilities": list(capabilities),
                "enabled": item["enabled"],
                "name": name,
            }
        )
    if seen != set(known):
        missing = sorted(set(known) - seen)
        raise HarnessError(f"config is missing providers: {missing}")
    return parsed


def _routing(value: object, names: list[str]) -> dict:
    if not isinstance(value, dict):
        raise HarnessError("config routing must be an object")
    _require_exact_keys(value, {"preference", "required_capabilities", "retries"}, "routing")
    required = _string_tuple(value["required_capabilities"], "routing.required_capabilities")
    preference = _string_tuple(value["preference"], "routing.preference")
    if sorted(preference) != sorted(names) or len(preference) != len(names):
        raise HarnessError("routing.preference must list each provider once")
    retries = value["retries"]
    if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
        raise HarnessError("routing.retries must be an integer >= 0")
    return {
        "preference": list(preference),
        "required_capabilities": list(required),
        "retries": retries,
    }


def _string_tuple(value: object, where: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise HarnessError(f"{where} must be a non-empty list")
    if any(not isinstance(item, str) or item == "" for item in value):
        raise HarnessError(f"{where} must be non-empty strings")
    if len(value) != len(set(value)):
        raise HarnessError(f"{where} contains a duplicate")
    return tuple(value)
