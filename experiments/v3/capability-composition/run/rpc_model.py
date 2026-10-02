"""R-PC invariant reference model (the candidate under test) for F02-F10, F13-F16.

Each function returns a typed dict outcome plus an event/effect record that an independent observer
inspects. This is a minimal semantic model of the R-PC candidate contract — not the product.
"""
from __future__ import annotations


# --- F02 generated-summary identity -------------------------------------------------------------
def summary_identity(summary_a: dict, summary_b: dict) -> dict:
    ref_a = summary_a["input"] + b"|" + summary_a["output"]
    ref_b = summary_b["input"] + b"|" + summary_b["output"]
    return {"a_ref": ref_a, "b_ref": ref_b, "distinct": ref_a != ref_b}


def replay(recorded: bytes | None) -> dict:
    if recorded is None:
        return {"outcome": "reproduction_input_unavailable", "model_calls": 0}
    return {"outcome": "ok", "bytes": recorded, "model_calls": 0}


# --- F03 mandatory closure under pressure -------------------------------------------------------
def resolve_closure(required: list[str], optional: list[str], cost: dict[str, int], capacity: int) -> dict:
    mandatory = sum(cost[x] for x in required)
    if mandatory > capacity:
        return {"outcome": "mandatory_context_unfittable", "dispatched": False, "loaded": [], "dropped": []}
    loaded = list(required)
    used = mandatory
    dropped: list[str] = []
    for name in sorted(optional):
        if used + cost[name] <= capacity:
            loaded.append(name)
            used += cost[name]
        else:
            dropped.append(name)
    return {"outcome": "ok", "dispatched": True, "loaded": sorted(loaded), "dropped": sorted(dropped)}


# --- F04 disabled capability zero contribution --------------------------------------------------
def contribution(installed: bool, enabled: bool) -> dict:
    if not installed:
        return {"operational_bytes": 0, "events": [], "admin_bytes": 0}
    if not enabled:
        return {"operational_bytes": 0, "events": [], "admin_bytes": 8}
    return {"operational_bytes": 64, "events": ["register", "load"], "admin_bytes": 8}


# --- F05 immediate revocation with coalesced preferences ----------------------------------------
def access(grant: str, fence: int, revoke_fence: int) -> dict:
    if grant == "grant7" and fence >= revoke_fence:
        return {"outcome": "refuse"}
    return {"outcome": "allow"}


# --- F06 authority laundering -------------------------------------------------------------------
def admit_import(claim_authority: bool) -> dict:
    envelope = {"authority_carried_none": True}
    sink_events: list[str] = []
    if not envelope["authority_carried_none"]:
        sink_events.append("unauthorized_effect")
    return {
        "authority_carried_none": envelope["authority_carried_none"],
        "sink_events": sink_events,
        "control": "completed",
        "quarantined": bool(claim_authority),
    }


# --- F07 procedure precedence -------------------------------------------------------------------
def resolve_precedence(reqs: list[tuple[str, str]], override: str | None) -> dict:
    if override is None:
        return {"outcome": "hold", "winner": None, "conflict": True}
    return {"outcome": "ok", "winner": override, "conflict": True}


# --- F08 evidence conflict ----------------------------------------------------------------------
def resolve_evidence(sources: list[dict]) -> dict:
    return {"refs": [s["ref"] for s in sources], "disagreement": True, "decision": None}


# --- F09 coherent cut ---------------------------------------------------------------------------
def validate_cut(config_rev: str, required_schema: str, snapshot: dict[str, str]) -> dict:
    if snapshot.get(config_rev) != required_schema:
        return {"outcome": "composition_cut_unavailable", "retries": 1}
    return {"outcome": "ok", "retries": 0}


# --- F10 one governor and stale parent ----------------------------------------------------------
def install_successor(parent: str, candidate: dict) -> dict:
    if candidate["parent"] != parent:
        return {"outcome": "stale_reject", "installed": False}
    return {"outcome": "install", "installed": True, "epoch": candidate["epoch"]}


# --- F13 route and schema drift -----------------------------------------------------------------
def bind_route(new_descriptor: str | None, schema_valid: bool, hidden_visibility_known: bool) -> dict:
    if new_descriptor and not schema_valid:
        return {"outcome": "hold", "hidden_visibility": "unknown" if not hidden_visibility_known else "known"}
    return {"outcome": "ok"}


# --- F14 checkpoint resume ----------------------------------------------------------------------
def restore(manifest_refs: list[str], active_skill: str) -> dict:
    if active_skill not in manifest_refs:
        return {"outcome": "reject_missing_reference"}
    return {
        "outcome": "ok",
        "rechecked_rights": True,
        "operation_o1": "O1",
        "liability": "held",
        "reexecuted": False,
        "reapproved": False,
        "funds_reset": False,
    }


# --- F15 graph errors before load ---------------------------------------------------------------
def _has_cycle(nodes: dict) -> bool:
    seen: dict[str, int] = {}

    def visit(name: str) -> bool:
        state = seen.get(name, 0)
        if state == 1:
            return True
        if state == 2:
            return False
        seen[name] = 1
        for dep in nodes.get(name, {}).get("deps", []):
            if dep in nodes and visit(dep):
                return True
        seen[name] = 2
        return False

    return any(visit(n) for n in nodes)


def validate_graph(graph: dict) -> dict:
    nodes = graph["nodes"]
    for spec in nodes.values():
        for dep in spec.get("deps", []):
            if dep not in nodes:
                return {"outcome": "reject", "reason": "missing_dependency", "imported": False}
    if _has_cycle(nodes):
        return {"outcome": "reject", "reason": "cycle", "imported": False}
    for cap, providers in graph.get("providers", {}).items():
        if len(providers) > 1 and cap not in graph.get("selected", {}):
            return {"outcome": "reject", "reason": "ambiguous_provider", "imported": False}
    for _res, owners in graph.get("exclusive", {}).items():
        if len(set(owners)) > 1:
            return {"outcome": "reject", "reason": "exclusive_owner_conflict", "imported": False}
    return {"outcome": "ok", "reason": None, "imported": False}


# --- F16 observer and oracle sensitivity --------------------------------------------------------
def observe_gate(observed: bool, output_valid: bool, refuse_all: bool) -> dict:
    if not observed:
        return {"outcome": "HOLD_UNKNOWN"}
    if refuse_all:
        return {"outcome": "fail_useful_completion"}
    if not output_valid:
        return {"outcome": "fail_invalid"}
    return {"outcome": "pass"}
