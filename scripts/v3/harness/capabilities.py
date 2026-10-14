"""Choose providers by declared capability. This is not M1B route selection.

M1B still admits ``route-a`` or refuses the run. Provider names here are a
separate namespace: a capability match never aliases ``ROUTE-INCLUDED``.
"""

from __future__ import annotations

from scripts.v3.harness.availability import order_candidates
from scripts.v3.harness.errors import HarnessError


def select_candidates(
    config: dict,
    *,
    provider: str | None = None,
    extra_capabilities: list[str] | None = None,
    fallback: bool = False,
) -> list[str]:
    """Return enabled providers that hold every required capability.

    Higher ``routing.weights`` run first. Equal weights keep preference order.
    An explicit ``provider`` must itself be capable. Without ``fallback`` it is
    the only candidate. With ``fallback`` it runs first and the remaining
    capable providers follow weight order.
    """

    required = set(config["routing"]["required_capabilities"])
    if extra_capabilities:
        required.update(extra_capabilities)
    by_name = {item["name"]: item for item in config["providers"]}
    capable: list[str] = []
    for name in config["routing"]["preference"]:
        item = by_name[name]
        if item["enabled"] and required <= set(item["capabilities"]):
            capable.append(name)
    ordered = order_candidates(
        capable,
        preference=list(config["routing"]["preference"]),
        weights=config["routing"].get("weights") or {},
    )
    if provider is not None:
        if provider not in by_name:
            known = ", ".join(sorted(by_name))
            raise HarnessError(f"unknown provider {provider!r}; known providers: {known}")
        if not by_name[provider]["enabled"]:
            raise HarnessError(f"provider {provider!r} is disabled")
        if provider not in capable:
            have = ", ".join(by_name[provider]["capabilities"])
            need = ", ".join(sorted(required))
            raise HarnessError(
                f"provider {provider!r} does not satisfy capabilities [{need}] (has [{have}])"
            )
        if not fallback:
            return [provider]
        return [provider, *[name for name in ordered if name != provider]]
    if not ordered:
        need = ", ".join(sorted(required))
        raise HarnessError(f"no enabled provider satisfies capabilities [{need}]")
    return ordered
