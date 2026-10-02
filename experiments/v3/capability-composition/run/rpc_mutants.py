"""Planted mutants for the R-PC invariant fixtures.

Each mutant violates exactly one documented predicate; the gate must detect every one. Mutants are
isolated test inputs, not instructions.
"""
from __future__ import annotations


def m_summary_equal_seed(summary_a: dict, summary_b: dict) -> dict:
    return {"a_ref": b"same", "b_ref": b"same", "distinct": False}


def m_replay_regenerates(recorded: bytes | None) -> dict:
    return {"outcome": "ok", "bytes": b"regenerated", "model_calls": 1}


def m_closure_auto_budget(required, optional, cost, capacity) -> dict:
    return {"outcome": "ok", "dispatched": True, "loaded": [required[0]], "dropped": [required[1]]}


def m_disabled_leaks(installed: bool, enabled: bool) -> dict:
    if not installed:
        return {"operational_bytes": 0, "events": [], "admin_bytes": 0}
    return {"operational_bytes": 16, "events": ["catalog_read"], "admin_bytes": 8}


def m_revoke_delayed(grant: str, fence: int, revoke_fence: int) -> dict:
    return {"outcome": "allow"}


def m_trust_claim(claim_authority: bool) -> dict:
    envelope = {"authority_carried_none": not claim_authority}
    sink = [] if envelope["authority_carried_none"] else ["unauthorized_effect"]
    return {"authority_carried_none": envelope["authority_carried_none"], "sink_events": sink, "control": "completed"}


def m_precedence_last_loaded(reqs, override) -> dict:
    return {"outcome": "ok", "winner": reqs[-1][0], "conflict": True}


def m_evidence_synth(sources) -> dict:
    return {"refs": [sources[0]["ref"]], "disagreement": False, "decision": sources[0]["value"]}


def m_cut_accept_latest(config_rev, required_schema, snapshot) -> dict:
    return {"outcome": "ok", "retries": 0}


def m_successor_last_completion(parent, candidate) -> dict:
    return {"outcome": "install", "installed": True, "epoch": candidate["epoch"]}


def m_route_name_only(new_descriptor, schema_valid, hidden_visibility_known) -> dict:
    return {"outcome": "ok"}


def m_restore_replay(manifest_refs, active_skill) -> dict:
    return {"outcome": "ok", "rechecked_rights": False, "operation_o1": "O1", "liability": "cleared", "reexecuted": True, "reapproved": True, "funds_reset": True}


def m_graph_import_to_discover(graph) -> dict:
    return {"outcome": "ok", "reason": None, "imported": True}


def m_silence_pass(observed, output_valid, refuse_all) -> dict:
    if refuse_all:
        return {"outcome": "fail_useful_completion"}
    if not output_valid:
        return {"outcome": "fail_invalid"}
    return {"outcome": "pass"}
