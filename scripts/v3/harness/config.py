"""Load the provider config. The file names commands and capabilities, not secrets."""

from __future__ import annotations

import json
import re
from pathlib import Path

from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.providers import adapters


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT / "config" / "harness.json"
SCHEMA_PATH = ROOT / "config" / "harness.schema.json"
_VALIDATOR = None
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
    _check_schema(payload, source)
    _require_exact_keys(
        payload,
        {"budgets", "landing", "orchestration", "providers", "review", "routing", "version"},
        "config",
    )
    version = payload["version"]
    if isinstance(version, bool) or version != 1:
        raise HarnessError("provider config version must be 1")
    providers = _providers(payload["providers"])
    routing = _routing(payload["routing"], [item["name"] for item in providers])
    orchestration = _orchestration(payload["orchestration"])
    review = _review(payload["review"])
    budgets = _budgets(payload["budgets"])
    landing = _landing(payload["landing"])
    return {
        "budgets": budgets,
        "landing": landing,
        "orchestration": orchestration,
        "providers": providers,
        "review": review,
        "routing": routing,
        "version": 1,
    }


def _validator():
    global _VALIDATOR
    if _VALIDATOR is not None:
        return _VALIDATOR
    if not SCHEMA_PATH.is_file():
        raise HarnessError(f"missing config schema {SCHEMA_PATH}")
    try:
        import jsonschema
    except ImportError as exc:
        raise HarnessError("jsonschema is required to validate the config") from exc
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HarnessError(f"config schema is not JSON: {SCHEMA_PATH}") from exc
    validator = jsonschema.Draft202012Validator(schema)
    validator.check_schema(schema)
    _VALIDATOR = validator
    return validator


def _check_schema(payload: dict, source: Path) -> None:
    """Reject a config the schema does not accept. The path names the bad field."""

    from scripts.v3.harness.redact import redact_text

    errors = sorted(_validator().iter_errors(payload), key=lambda error: (list(error.absolute_path), error.message))
    if not errors:
        return
    lines = []
    for error in errors:
        location = _schema_location(error.absolute_path)
        message = redact_text(error.message)
        if location:
            lines.append(f"{source}: {location}: {message}")
        else:
            lines.append(f"{source}: {message}")
    raise HarnessError("\n".join(lines))


def _schema_location(path) -> str:
    parts: list[str] = []
    for item in path:
        if isinstance(item, int):
            if not parts:
                parts.append(f"[{item}]")
            else:
                parts[-1] = f"{parts[-1]}[{item}]"
        else:
            parts.append(str(item))
    return ".".join(parts)


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
        _require_exact_keys(
            item, {"argv", "capabilities", "enabled", "name", "timeout_seconds"}, "provider"
        )
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
        timeout_seconds = _positive_int(item["timeout_seconds"], f"provider {name} timeout_seconds")
        parsed.append(
            {
                "argv": list(argv),
                "capabilities": list(capabilities),
                "enabled": item["enabled"],
                "name": name,
                "timeout_seconds": timeout_seconds,
            }
        )
    if seen != set(known):
        missing = sorted(set(known) - seen)
        raise HarnessError(f"config is missing providers: {missing}")
    return parsed


def _routing(value: object, names: list[str]) -> dict:
    if not isinstance(value, dict):
        raise HarnessError("config routing must be an object")
    _require_exact_keys(
        value,
        {"backoff_seconds", "cooldown_seconds", "preference", "required_capabilities", "retries", "weights"},
        "routing",
    )
    required = _string_tuple(value["required_capabilities"], "routing.required_capabilities")
    preference = _string_tuple(value["preference"], "routing.preference")
    if sorted(preference) != sorted(names) or len(preference) != len(names):
        raise HarnessError("routing.preference must list each provider once")
    retries = value["retries"]
    if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
        raise HarnessError("routing.retries must be an integer >= 0")
    backoff = value["backoff_seconds"]
    if isinstance(backoff, bool) or not isinstance(backoff, int) or backoff < 0:
        raise HarnessError("routing.backoff_seconds must be an integer >= 0")
    cooldown = value["cooldown_seconds"]
    if isinstance(cooldown, bool) or not isinstance(cooldown, int) or cooldown < 0:
        raise HarnessError("routing.cooldown_seconds must be an integer >= 0")
    return {
        "backoff_seconds": backoff,
        "cooldown_seconds": cooldown,
        "preference": list(preference),
        "required_capabilities": list(required),
        "retries": retries,
        "weights": _weights(value["weights"], names),
    }


def _weights(value: object, names: list[str]) -> dict[str, int]:
    if not isinstance(value, dict):
        raise HarnessError("routing.weights must be an object")
    if set(value) != set(names):
        raise HarnessError("routing.weights must name each provider once")
    parsed = {}
    for name in names:
        weight = value[name]
        if isinstance(weight, bool) or not isinstance(weight, int) or weight < 1:
            raise HarnessError(f"routing.weights.{name} must be an integer >= 1")
        parsed[name] = weight
    return parsed


def _orchestration(value: object) -> dict:
    if not isinstance(value, dict):
        raise HarnessError("config orchestration must be an object")
    _require_exact_keys(value, {"concurrency"}, "orchestration")
    return {"concurrency": _positive_int(value["concurrency"], "orchestration.concurrency")}


def _review(value: object) -> dict:
    if not isinstance(value, dict):
        raise HarnessError("config review must be an object")
    _require_exact_keys(value, {"accept_unreviewed", "max_rounds"}, "review")
    return {
        "accept_unreviewed": _bool(value["accept_unreviewed"], "review.accept_unreviewed"),
        "max_rounds": _positive_int(value["max_rounds"], "review.max_rounds"),
    }


def _landing(value: object) -> dict:
    if not isinstance(value, dict):
        raise HarnessError("config landing must be an object")
    _require_exact_keys(value, {"base_ref"}, "landing")
    return {"base_ref": _git_ref(value["base_ref"], "landing.base_ref")}


def _bool(value: object, where: str) -> bool:
    if not isinstance(value, bool):
        raise HarnessError(f"{where} must be a boolean")
    return value


def _git_ref(value: object, where: str) -> str:
    if not isinstance(value, str) or value.strip() == "" or any(char in value for char in "\n\r\x00"):
        raise HarnessError(f"{where} must be a git ref")
    return value.strip()


def _budgets(value: object) -> dict:
    if not isinstance(value, dict):
        raise HarnessError("config budgets must be an object")
    _require_exact_keys(value, {"max_cost", "max_input_tokens", "max_output_tokens"}, "budgets")
    return {
        "max_cost": _optional_number(value["max_cost"], "budgets.max_cost"),
        "max_input_tokens": _optional_int(value["max_input_tokens"], "budgets.max_input_tokens"),
        "max_output_tokens": _optional_int(value["max_output_tokens"], "budgets.max_output_tokens"),
    }


def _optional_int(value: object, where: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise HarnessError(f"{where} must be null or an integer >= 0")
    return value


def _optional_number(value: object, where: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise HarnessError(f"{where} must be null or a number >= 0")
    return float(value)


def _positive_int(value: object, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise HarnessError(f"{where} must be an integer >= 1")
    return value


def starter_config(enabled: set[str]) -> dict:
    """Build a version-1 config. ``enabled`` names the providers that start on."""

    known = adapters()
    unknown = sorted(enabled - set(known))
    if unknown:
        raise HarnessError(f"unknown providers: {unknown}")
    return {
        "version": 1,
        "review": {"accept_unreviewed": False, "max_rounds": 2},
        "landing": {"base_ref": "HEAD"},
        "budgets": {
            "max_input_tokens": 1000000,
            "max_output_tokens": 1000000,
            "max_cost": None,
        },
        "orchestration": {"concurrency": 2},
        "routing": {
            "required_capabilities": ["execute"],
            "preference": list(known),
            "retries": 1,
            "backoff_seconds": 1,
            "cooldown_seconds": 60,
            "weights": {name: 1 for name in known},
        },
        "providers": [
            {
                "name": name,
                "enabled": name in enabled,
                "capabilities": list(cls.CAPABILITIES),
                "argv": list(cls.STATIC_ARGV),
                "timeout_seconds": 120,
            }
            for name, cls in known.items()
        ],
    }


def write_starter(path: Path, enabled: set[str], *, force: bool = False) -> dict:
    """Write a starter config. An existing file is left in place without ``force``."""

    target = Path(path)
    if target.is_dir():
        raise HarnessError(f"{target} is a directory")
    if target.exists() and not force:
        raise HarnessError(f"refusing to overwrite {target}; pass --force")
    payload = starter_config(enabled)
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    target.write_text(text, encoding="utf-8", newline="\n")
    return payload


def _string_tuple(value: object, where: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise HarnessError(f"{where} must be a non-empty list")
    if any(not isinstance(item, str) or item == "" for item in value):
        raise HarnessError(f"{where} must be non-empty strings")
    if len(value) != len(set(value)):
        raise HarnessError(f"{where} contains a duplicate")
    return tuple(value)
