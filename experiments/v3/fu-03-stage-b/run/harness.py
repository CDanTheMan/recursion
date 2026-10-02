#!/usr/bin/env python3
"""Provider-free synthetic harness for the FU-03 Stage B crash-cut matrix.

For every fixture in ``experiments/v3/fu-03-stage-b/fixtures.json`` this module materializes the
fixture's finite schedule into

(a) a canonical committed event log conforming to the Session A oracle's semantics, and
(b) an independent observation side folded by :mod:`observers` (receiver fence, Stop lifecycle,
    reservation/liability conservation).  The observers never import the oracle.

The oracle is used here only as a *canonical log writer* (``command_from_spec`` / ``admit``) so
that the materialized prefix is well-formed input for the expectation side.  The observation side
is built from separate schedules.  The comparison and classification live in ``run_stage_b.py``.

A simulated receiver is not qualification of an external service, native process containment or
real automatic takeover.  Pure Python 3.12 stdlib, deterministic, provider-free.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

HERE = Path(__file__).resolve().parent
ORACLE_DIR = HERE.parents[1] / "fu-03-kernel-session-a" / "oracle"
if str(ORACLE_DIR) not in sys.path:
    sys.path.insert(0, str(ORACLE_DIR))

import refstate as R  # noqa: E402  (canonical log writer only)

import observers as O  # noqa: E402

# Oracle enum aliases used to express expectations.
ES_NONE = R.ES_NONE
ES_PREPARED = R.ES_PREPARED
ES_INFLIGHT = R.ES_INFLIGHT
ES_UNKNOWN = R.ES_UNKNOWN
ES_SUCCEEDED = R.ES_SUCCEEDED
ES_KNOWN_NO_EFFECT = R.ES_KNOWN_NO_EFFECT
ST_RUNNING = R.ST_RUNNING
ST_DONE = R.ST_DONE
ST_CANCELLED = R.ST_CANCELLED

COMMAND_CONFLICT = R.COMMAND_CONFLICT
DET_COMMAND_DIGEST = R.DET_COMMAND_DIGEST
LEASE_EPOCH_STALE = R.LEASE_EPOCH_STALE
EFFECT_UNSAFE = R.EFFECT_UNSAFE
ATTEMPT_INVALID = R.ATTEMPT_INVALID


def jsonable(value):
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    return value


@dataclass
class Check:
    """One evaluated comparison.  ``fn(expectation, observation) -> bool``."""

    name: str
    kind: str  # "expect" | "observe" | "agree"
    fn: Callable[[dict, dict], bool]
    detail: str


@dataclass
class KRun:
    """Materializes a canonical committed event log with the oracle's own constructors."""

    log: list = field(default_factory=list)
    state: object = None
    admissions: list = field(default_factory=list)
    cmds: dict = field(default_factory=dict)
    _extra_ids: list = field(default_factory=list)

    def __post_init__(self) -> None:
        self.state = R.genesis_state()

    def _next_id(self) -> int:
        used = {r.id for r in self.state.receipts} | set(self._extra_ids)
        candidate = 1
        while candidate in used:
            candidate += 1
        self._extra_ids.append(candidate)
        return candidate

    def fresh(self, spec: dict, label: Optional[str] = None) -> object:
        command = R.command_from_spec(self.state, spec)
        admission = R.admit(self.state, command)
        self.admissions.append({
            "label": label or f"fresh:{spec.get('kind')}",
            "outcome": admission.outcome,
            "code": None if admission.refusal is None else admission.refusal.code,
            "detail": None if admission.refusal is None else admission.refusal.detail,
        })
        if admission.outcome != "fresh":
            raise AssertionError(f"expected fresh admission for {spec!r}; got {admission.outcome}")
        self.state = admission.batch.post_state
        self.log.extend(admission.batch.events)
        return command

    def again(self, command, label: str) -> object:
        admission = R.admit(self.state, command)
        self.admissions.append({
            "label": label,
            "outcome": admission.outcome,
            "code": None if admission.refusal is None else admission.refusal.code,
            "detail": None if admission.refusal is None else admission.refusal.detail,
        })
        return admission

    def variant(self, spec: dict, label: str) -> object:
        command = R.command_from_spec(self.state, spec)
        admission = R.admit(self.state, command)
        self.admissions.append({
            "label": label,
            "outcome": admission.outcome,
            "code": None if admission.refusal is None else admission.refusal.code,
            "detail": None if admission.refusal is None else admission.refusal.detail,
        })
        return admission

    def replayed(self) -> "KRun":
        """Return a fresh fold of the same committed event log (retained-prefix replay)."""
        clone = KRun()
        clone.log = list(self.log)
        clone.state = R.RefState(self.log)
        return clone

    def event_maps(self) -> list:
        return [jsonable(event.to_map()) for event in self.log]

    def event_maps_raw(self) -> list:
        """Raw stored-event maps (bytes preserved) for the in-process trace bridge."""
        return [event.to_map() for event in self.log]

    def log_digest(self) -> str:
        import hashlib
        import json
        canonical = json.dumps(self.event_maps(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


@dataclass
class Scenario:
    fixture_id: str
    cut_point: str
    fence_state: str
    stop_mode: str
    run: Optional[KRun]
    receiver: Optional[O.ReceiverFenceObserver] = None
    stop: Optional[O.StopObserver] = None
    resources: Optional[O.ConservationObserver] = None
    receipt: Optional[O.ReceiptBindingObserver] = None
    trace: Optional[dict] = None
    trace_negative: Optional[dict] = None
    supported: bool = True
    fallback_disposition: str = "blocked"
    reason: str = ""
    expectation_note: str = ""
    observation_note: str = ""
    checks: list = field(default_factory=list)
    positive: bool = False
    negative: bool = False

    def observation(self) -> dict:
        return {
            "receiver": None if self.receiver is None else self.receiver.to_dict(),
            "stop": None if self.stop is None else self.stop.to_dict(),
            "resources": None if self.resources is None else self.resources.to_dict(),
            "receipt": None if self.receipt is None else self.receipt.to_dict(),
        }

    def observer_names(self) -> list:
        names = []
        if self.receiver is not None:
            names.append("receiver-fence")
        if self.stop is not None:
            names.append("stop-lifecycle")
        if self.resources is not None:
            names.append("reservation-liability")
        if self.receipt is not None:
            names.append("receipt-binding")
        return names

    def has_expectation(self) -> bool:
        return self.run is not None and len(self.run.log) >= 0

    def has_observation(self) -> bool:
        return any(v is not None for v in self.observation().values())


# ---------------------------------------------------------------------------
# Check helpers
# ---------------------------------------------------------------------------
def expect(name: str, fn: Callable, detail: str) -> Check:
    return Check(name, "expect", fn, detail)


def observe(name: str, fn: Callable, detail: str) -> Check:
    return Check(name, "observe", fn, detail)


def agree(name: str, fn: Callable, detail: str) -> Check:
    return Check(name, "agree", fn, detail)


def _admission(exp: dict, label: str) -> Optional[dict]:
    for entry in exp.get("admissions", []):
        if entry["label"] == label:
            return entry
    return None


def _fresh_count(exp: dict) -> int:
    return sum(1 for entry in exp.get("admissions", []) if entry["outcome"] == "fresh")


# ---------------------------------------------------------------------------
# Scenario builders
# ---------------------------------------------------------------------------
def _sb01() -> Scenario:
    run = KRun()
    run.variant({"kind": R.KIND_START, "writer": 2}, "distinct-identity-after-crash")
    receiver = O.ReceiverFenceObserver()
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "empty committed prefix is valid"),
        expect("no-committed-event", lambda e, o: e["log_len"] == 0 and e["project"][1] == 0,
               "pre-admission crash commits no event"),
        expect("no-receipt", lambda e, o: e["receipt_count"] == 0, "no receipt for the failed identity"),
        expect("distinct-identity-refused",
               lambda e, o: (_admission(e, "distinct-identity-after-crash") or {}).get("outcome") == "refused",
               "a distinct identity is refused by the authority checks, not admitted"),
        observe("receiver-untouched", lambda e, o: o["receiver"]["accepted_total"] == 0,
                "no receiver mutation before admission"),
        agree("zero-effect-both-sides",
              lambda e, o: e["effect_count"] == 0 and o["receiver"]["accepted_total"] == 0,
              "committed effect count and receiver mutations are both zero"),
    ]
    return Scenario(
        "SB-01", "admit", "not-installed", "Full", run, receiver=receiver, checks=checks,
        expectation_note="RefValid(empty)=VALID_BOUNDED; ordinal/tail/receipts unchanged",
        observation_note="receiver ledger sees zero mutations; no fence installed",
    )


def _sb02() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.variant({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "second-prepare")
    receiver = O.ReceiverFenceObserver()
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 2)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "prepared batch is a valid prefix"),
        expect("effect-prepared", lambda e, o: e["project"][14] == ES_PREPARED, "effect is ES_PREPARED"),
        expect("outbox-one", lambda e, o: e["outbox_len"] == 1, "one outbox entry for the stable token"),
        expect("receipts-per-fresh-command",
               lambda e, o: e["receipt_count"] == _fresh_count(e),
               "one receipt per logical operation; the refused second PrepareEffect adds none"),
        expect("second-prepare-refused",
               lambda e, o: (_admission(e, "second-prepare") or {}).get("outcome") == "refused",
               "a second PrepareEffect does not create a second intent"),
        observe("no-receiver-effect", lambda e, o: o["receiver"]["accepted_total"] == 0,
                "prepared intent is not dispatched"),
        agree("held-reservation",
              lambda e, o: o["resources"]["outstanding"] == 2 and e["effect_status"] == ES_PREPARED,
              "reservation stays held while the intent is prepared"),
    ]
    return Scenario(
        "SB-02", "prepared", "not-installed", "Full", run, receiver=receiver, resources=resources,
        checks=checks,
        expectation_note="RefProject effect=ES_PREPARED, outbox=1, receipts=1",
        observation_note="receiver mutation 0; reservation held",
    )


def _sb03() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.fresh({"kind": R.KIND_OBSERVE_EFFECT, "payload": {"0": "@effect_token", "1": 0}}, "observe-success")
    replay = run.replayed()
    receiver = O.ReceiverFenceObserver()
    for event in run.log:
        receiver.commit(event.ordinal, event.digest.hex())
    trace = {"trace_id": "SB-03-replay",
             "steps": [{"events": run.event_maps_raw()}]}
    negative = {"trace_id": "SB-03-duplicate-append",
                "steps": [{"events": run.event_maps_raw()},
                          {"events": [run.event_maps_raw()[-1]]}]}
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "acknowledged prefix is valid"),
        expect("replay-identical",
               lambda e, o: e["replay_project"] == e["project"] and e["replay_digest"] == e["digest"],
               "replay folds to the identical reference state"),
        expect("effect-succeeded", lambda e, o: e["project"][14] == ES_SUCCEEDED,
               "acknowledged effect settled"),
        agree("durable-order-binds",
              lambda e, o: e["project"][1] == o["receiver"]["durable_ordinal"]
              and e["project"][2].hex() == o["receiver"]["durable_tail_hex"],
              "RefProject ordinal/tail bind the independently observed durable prefix"),
        expect("trace-valid", lambda e, o: e["trace"]["verdict"] == "VALID_BOUNDED",
               "trace bridge accepts the retained prefix"),
        expect("trace-negative-rejected",
               lambda e, o: e["trace_negative"]["verdict"] == "INVALID_TRACE",
               "trace bridge rejects a duplicate append"),
    ]
    return Scenario(
        "SB-03", "commit", "not-installed", "Full", run, receiver=receiver, trace=trace,
        trace_negative=negative, checks=checks,
        expectation_note="RefValid=VALID_BOUNDED; replay == live fold; RefProject ordinal/tail bind",
        observation_note="durable prefix ordinal/tail observed independently; trace controls run",
    )


def _sb04() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    dispatch = run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.again(dispatch, "duplicate-dispatch")
    run.variant({"kind": R.KIND_MARK_DISPATCH, "id": dispatch.id, "payload": {"0": "@wrong_token"}},
                "changed-bytes")
    receiver = O.ReceiverFenceObserver()
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 3)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "dispatch prefix is valid"),
        expect("inflight-or-unknown",
               lambda e, o: e["project"][14] in (ES_INFLIGHT, ES_UNKNOWN),
               "no ES_SUCCEEDED without an observation"),
        expect("outbox-cleared", lambda e, o: e["outbox_len"] == 0, "dispatched token left the outbox"),
        expect("receipts-per-fresh-command",
               lambda e, o: e["receipt_count"] == _fresh_count(e),
               "one receipt per command; the duplicate adds none and the conflict is refused"),
        expect("duplicate-cached",
               lambda e, o: (_admission(e, "duplicate-dispatch") or {}).get("outcome") == "cached",
               "retry is a cached duplicate"),
        expect("changed-bytes-conflict",
               lambda e, o: (_admission(e, "changed-bytes") or {}).get("code") == COMMAND_CONFLICT,
               "changed bytes under the same id conflict"),
        observe("no-receiver-effect", lambda e, o: o["receiver"]["accepted_total"] == 0,
                "no mutation before receiver acceptance"),
        agree("reservation-held",
              lambda e, o: o["resources"]["outstanding"] == 3 and e["effect_count"] == 1,
              "one dispatched effect identity maps to one held reservation"),
    ]
    return Scenario(
        "SB-04", "dispatch", "not-installed", "Full", run, receiver=receiver, resources=resources,
        checks=checks,
        expectation_note="effect ES_INFLIGHT/UNKNOWN; duplicate cached; changed bytes COMMAND_CONFLICT",
        observation_note="receiver mutation 0 pre-acceptance; reservation held",
    )


def _sb05() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.fresh({"kind": R.KIND_OBSERVE_EFFECT, "payload": {"0": "@effect_token", "1": 2}}, "observe-unknown")
    run.fresh({"kind": R.KIND_RECONCILE_EFFECT, "payload": {"0": "@effect_token", "1": 0}}, "reconcile-success")
    receiver = O.ReceiverFenceObserver()
    receiver.propose(7, "apply-effect")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 4)
    resources.settle("op-1", 4)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "response-loss prefix is valid"),
        expect("unknown-then-succeeded",
               lambda e, o: e["project"][14] == ES_SUCCEEDED, "reconciliation settles the original effect"),
        expect("receipts-per-fresh-command",
               lambda e, o: e["receipt_count"] == _fresh_count(e),
               "receipt id stable across retry; no second effect id"),
        observe("receiver-mutated-once", lambda e, o: o["receiver"]["accepted_total"] == 1,
                "independent ledger shows exactly one mutation"),
        agree("single-effect-both-sides",
              lambda e, o: e["effect_count"] == 1 and o["receiver"]["accepted_total"] == 1,
              "one committed effect for the stable operation"),
        agree("settled-once",
              lambda e, o: o["resources"]["settled"] == 4 and o["resources"]["outstanding"] == 0,
              "liability settled once, never double-released"),
    ]
    return Scenario(
        "SB-05", "response-loss-before-receipt", "not-installed", "Full", run,
        receiver=receiver, resources=resources, checks=checks, positive=True,
        expectation_note="effect ES_UNKNOWN until reconcile, then ES_SUCCEEDED; receipts stable",
        observation_note="receiver ledger mutation count == 1; liability settled once",
    )


def _sb06() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.fresh({"kind": R.KIND_OBSERVE_EFFECT, "payload": {"0": "@effect_token", "1": 2}}, "observe-unknown")
    receiver = O.ReceiverFenceObserver()
    receiver.propose(7, "apply-effect")
    receiver.propose(6, "stale-fenced-request", issuer="authority:old")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 2)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "post-dispatch retry prefix is valid"),
        expect("unresolved-not-succeeded", lambda e, o: e["project"][14] == ES_UNKNOWN,
               "reply loss leaves the effect unresolved"),
        expect("attempt-unchanged", lambda e, o: e["project"][8] == 1,
               "no new attempt without the semantic owner"),
        observe("single-mutation", lambda e, o: o["receiver"]["accepted_total"] == 1,
                "exactly one receiver mutation for the stable operation"),
        observe("stale-request-refused",
                lambda e, o: o["receiver"]["refused_unqualified_count"] >= 1,
                "stale/unqualified request causes no mutation"),
        agree("unresolved-holds-liability",
              lambda e, o: o["resources"]["outstanding"] == 2 and e["effect_count"] == 1,
              "the unresolved effect keeps its held liability"),
    ]
    return Scenario(
        "SB-06", "response-loss-after-dispatch", "not-installed", "Full", run,
        receiver=receiver, resources=resources, checks=checks,
        expectation_note="one effect, unresolved; attempt not raised by retry",
        observation_note="one receiver mutation; stale request refused",
    )


def _sb07() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.fresh({"kind": R.KIND_OBSERVE_EFFECT, "payload": {"0": "@effect_token", "1": 0}}, "observe-success")
    receiver = O.ReceiverFenceObserver()
    receiver.install(8)
    for event in run.log:
        receiver.commit(event.ordinal, event.digest.hex())
    receiver.propose(7, "stale-writer-A")
    receiver.propose(8, "valid-writer-B")
    receiver.restart()
    receiver.propose(7, "stale-after-restart")
    receiver.install(8, issuer="authority:rogue")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 1)
    resources.settle("op-1", 1)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "accepted prefix valid across restart"),
        expect("effect-settled", lambda e, o: e["project"][14] == ES_SUCCEEDED, "one accepted effect"),
        observe("floor-eight", lambda e, o: o["receiver"]["floor"] == 8,
                "durable installed floor equals 8"),
        observe("floor-monotonic",
                lambda e, o: o["receiver"]["floor_monotonic"] and o["receiver"]["restarts"] == 1,
                "floor never regresses, including across restart"),
        observe("stale-rejected", lambda e, o: o["receiver"]["refused_stale_count"] >= 1,
                "zero epoch-7 mutations after install"),
        observe("rogue-issuer-refused",
                lambda e, o: o["receiver"]["refused_unqualified_count"] == 1,
                "unqualified issuer cannot move the floor"),
        agree("one-post-install-effect",
              lambda e, o: o["receiver"]["post_install_accepted"] == 1 and e["effect_count"] == 1,
              "one accepted post-install mutation maps to one committed effect"),
    ]
    return Scenario(
        "SB-07", "commit", "installed-old-epoch", "Full", run, receiver=receiver,
        resources=resources, checks=checks, negative=True,
        expectation_note="canonical order binds across restart; stale epoch refused",
        observation_note="floor 8 monotonic; stale epoch-7 and rogue issuer refused",
    )


def _sb08() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.fresh({"kind": R.KIND_OBSERVE_EFFECT, "payload": {"0": "@effect_token", "1": 0}}, "observe-success")
    receiver = O.ReceiverFenceObserver()
    receiver.install(8)
    receiver.propose(7, "stale-epoch-7")
    receiver.propose(4, "lower-floor")
    receiver.propose(99, "fabricated-higher-floor", issuer="authority:rogue")
    receiver.install(99, issuer="authority:rogue")
    receiver.restart()
    receiver.propose(7, "stale-after-restart")
    for event in run.log:
        receiver.commit(event.ordinal, event.digest.hex())
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 1)
    resources.settle("op-1", 1)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "valid prefix under installed current fence"),
        expect("effect-settled", lambda e, o: e["project"][14] == ES_SUCCEEDED, "one accepted effect"),
        observe("zero-stale-accepted",
                lambda e, o: o["receiver"]["refused_stale_count"] >= 1
                and o["receiver"]["post_install_accepted"] == 0,
                "no epoch below floor is accepted"),
        observe("floor-monotonic",
                lambda e, o: o["receiver"]["floor"] == 8 and o["receiver"]["floor_monotonic"],
                "floor stays 8 across restart; rogue cannot raise it"),
        observe("rogue-refused",
                lambda e, o: o["receiver"]["refused_unqualified_count"] >= 1,
                "unqualified issuer refused"),
        agree("no-fabricated-effect",
              lambda e, o: o["receiver"]["post_install_accepted"] == 0 and e["effect_count"] == 1,
              "no stale mutation is witnessed as a committed effect"),
    ]
    return Scenario(
        "SB-08", "dispatch", "installed-current", "Full", run, receiver=receiver,
        resources=resources, checks=checks,
        expectation_note="no witnessing receipt for a stale attempt",
        observation_note="installed floor monotonic across restart; stale and rogue refused",
    )


def _sb09() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.fresh({"kind": R.KIND_OBSERVE_EFFECT, "payload": {"0": "@effect_token", "1": 2}}, "observe-unknown")
    receiver = O.ReceiverFenceObserver()
    receiver.propose(7, "pre-install-old-epoch")
    receiver.install(8)
    receiver.propose(7, "stale-after-install")
    receiver.propose(8, "current-epoch")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 2)
    checks = [
        expect("not-promoted",
               lambda e, o: e["project"][14] != ES_KNOWN_NO_EFFECT,
               "missing observation never promotes to ES_KNOWN_NO_EFFECT"),
        observe("pre-install-exposure-recorded",
                lambda e, o: o["receiver"]["prior_exposure_count"] == 1,
                "pre-install mutation recorded as prior exposure, never erased"),
        observe("post-install-stale-refused",
                lambda e, o: o["receiver"]["refused_stale_count"] == 1,
                "a distinct stale-after-install attempt is refused"),
        agree("unknown-outcome-preserved",
              lambda e, o: e["project"][14] == ES_UNKNOWN
              and o["resources"]["outstanding"] == 2,
              "pre-install exposure stays unknown with held liability"),
    ]
    return Scenario(
        "SB-09", "dispatch", "not-installed", "Full", run, receiver=receiver,
        resources=resources, checks=checks, supported=False, fallback_disposition="unknown",
        reason="pre-install exposure interval cannot be independently resolved; its effect outcome "
               "stays pending/unknown and is never promoted to a known state",
        expectation_note="effect status distinguishes pre-install unknown from post-install rejection",
        observation_note="prior-exposure and post-install stale-rejection recorded distinctly",
    )


def _stop_graph(observer: O.StopObserver) -> None:
    observer.add_member("root")
    observer.add_member("worker", "root")
    observer.add_member("child", "worker")
    observer.add_member("shell", "root")
    observer.add_member("monitor", "root")
    observer.add_member("relauncher", "root")
    observer.add_member("consultant", None, borrowed=True)


def _sb10() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    before = len(run.log)
    run.variant({"kind": R.KIND_START}, "late-relaunch-of-stopped-actor")
    stop = O.StopObserver()
    _stop_graph(stop)
    stop.stop("Aggressive", {"worker"})
    for fact in ("accepted", "fenced", "acknowledged"):
        stop.record("worker", fact)
    stop.relaunch("worker", accepted=False)
    resources = O.ConservationObserver(gross=10)
    resources.reserve("borrowed-op", 2)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "committed prefix valid at the Stop cut"),
        expect("no-new-admission",
               lambda e, o: e["log_len"] == before,
               "no new admission for the stopped selected actor"),
        expect("late-relaunch-refused",
               lambda e, o: (_admission(e, "late-relaunch-of-stopped-actor") or {}).get("outcome") == "refused",
               "a late relaunch is refused by the authority checks"),
        observe("selected-only",
                lambda e, o: o["stop"]["targets"] == ["worker"] and "child" in o["stop"]["excluded"],
                "Aggressive target set excludes descendants"),
        observe("borrowed-preserved", lambda e, o: o["stop"]["borrowed_preserved"] is True,
                "the unrelated borrowed operation is not a target"),
        observe("worker-fenced", lambda e, o: o["stop"]["facts"]["worker"]["fenced"] is True,
                "the selected actor is fenced"),
        agree("borrowed-liability-preserved",
              lambda e, o: o["resources"]["outstanding"] == 2 and e["effect_count"] == 1,
              "borrowed operation keeps its own reservation"),
    ]
    return Scenario(
        "SB-10", "dispatch", "installed-current", "Aggressive", run, stop=stop,
        resources=resources, checks=checks,
        expectation_note="no new admission for the stopped actor; unrelated op unaffected",
        observation_note="Aggressive targets selected actor only; descendant and borrowed excluded",
    )


def _sb11() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    stop = O.StopObserver()
    _stop_graph(stop)
    stop.add_member("remote", "root")
    stop.stop("Full", {"root"})
    for member in ("root", "worker", "child", "shell", "monitor", "relauncher"):
        for fact in ("accepted", "fenced", "acknowledged", "local_exited"):
            stop.record(member, fact)
    stop.record("remote", "accepted")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("remote-op", 5)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "valid prefix at the Full Stop cut"),
        observe("rooted-closure",
                lambda e, o: set(o["stop"]["targets"]) ==
                {"root", "worker", "child", "shell", "monitor", "relauncher", "remote"},
                "Full targets every rooted owned member"),
        observe("borrowed-preserved", lambda e, o: o["stop"]["borrowed_preserved"] is True,
                "borrowed operation preserved"),
        observe("unreachable-unresolved",
                lambda e, o: "remote" in o["stop"]["unresolved"],
                "unreachable member is unresolved, not stopped"),
        agree("remote-liability-held",
              lambda e, o: o["resources"]["outstanding"] == 5,
              "unreachable member keeps held liability"),
    ]
    return Scenario(
        "SB-11", "dispatch", "installed-current", "Full", run, stop=stop, resources=resources,
        checks=checks, supported=False, fallback_disposition="unknown",
        reason="a rooted member is unreachable, so the closure is computed but the stop is not "
               "complete; the member stays unresolved with held liability and no drained claim is made",
        expectation_note="no new rooted admission or relaunch",
        observation_note="owned closure enumerated; unreachable member unresolved",
    )


def _sb12() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    stop = O.StopObserver()
    _stop_graph(stop)
    stop.stop("Lazy", {"worker"}, boundary_reached=False)
    stop.record("worker", "accepted")
    stop.record("worker", "fenced")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("lazy-op", 3)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "valid prefix at the Lazy Stop cut"),
        observe("boundary-not-reached", lambda e, o: o["stop"]["boundary_reached"] is False,
                "named next-operation boundary not reached before the deadline"),
        observe("not-observed-stopped",
                lambda e, o: o["stop"]["facts"]["worker"]["remote_observed"] is False
                and o["stop"]["facts"]["worker"]["local_exited"] is False,
                "no observed-stopped without boundary evidence"),
        observe("facts-distinct",
                lambda e, o: o["stop"]["facts"]["worker"]["requested"] is True
                and o["stop"]["facts"]["worker"]["accepted"] is True,
                "requested/accepted/fenced/observed stay distinct"),
        agree("unresolved-liability-held",
              lambda e, o: o["resources"]["outstanding"] == 3,
              "unresolved Lazy stop keeps held liability"),
    ]
    return Scenario(
        "SB-12", "response-loss-after-dispatch", "installed-current", "Lazy", run, stop=stop,
        resources=resources, checks=checks, supported=False, fallback_disposition="unknown",
        reason="the Lazy deadline is reached without boundary or quiescence evidence; the member is "
               "unresolved and the observation is not promoted to stopped",
        expectation_note="named boundary or unresolved status, never observed-stopped",
        observation_note="facts separate requested/accepted/fenced/observed; boundary absent",
    )


def _sb13() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    prepare_id = run.state.receipts[-1].id if run.state.receipts else 1
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.fresh({"kind": R.KIND_CANCEL}, "cancel-ack")
    run.fresh({"kind": R.KIND_OBSERVE_EFFECT, "payload": {"0": "@effect_token", "1": 0}}, "late-valid-receipt")
    run.variant({"kind": R.KIND_PREPARE_EFFECT, "id": prepare_id, "payload": {"0": 1}},
                "wrong-incarnation-receipt")
    receipt = O.ReceiptBindingObserver()
    receipt.record("op-1", "incarnation-1", "digest-A")
    receipt.record("op-1", "incarnation-1", "digest-A")
    receipt.record("op-1", "incarnation-2", "digest-A")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 2)
    resources.settle("op-1", 2)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "late-receipt prefix is valid"),
        expect("effect-not-rolled-back",
               lambda e, o: e["project"][14] == ES_SUCCEEDED and e["project"][11] is True,
               "cancel ack is neither terminal success nor rollback of the effect"),
        expect("result-unchanged", lambda e, o: e["project"][12] is None,
               "result value is unchanged by the cancel acknowledgement"),
        expect("wrong-incarnation-conflict",
               lambda e, o: (_admission(e, "wrong-incarnation-receipt") or {}).get("code") == COMMAND_CONFLICT,
               "wrong-incarnation receipt conflicts under the same id"),
        observe("historical-deduped",
                lambda e, o: o["receipt"]["accepted"] == 1 and o["receipt"]["duplicates"] == 1,
                "late valid receipt classifies only the original operation"),
        observe("wrong-incarnation-refused",
                lambda e, o: o["receipt"]["wrong_incarnation_refused"] == 1,
                "wrong-incarnation receipt rejected"),
        agree("one-effect-one-receipt",
              lambda e, o: e["effect_count"] == 1 and o["receipt"]["accepted"] == 1,
              "one effect maps to one accepted receipt binding"),
    ]
    return Scenario(
        "SB-13", "response-loss-after-dispatch", "installed-current", "Aggressive", run,
        receipt=receipt, resources=resources, checks=checks,
        expectation_note="effect not rolled back by cancel; result unchanged; wrong incarnation conflicts",
        observation_note="receipt binding dedupes historical and refuses wrong incarnation",
    )


def _sb14() -> Scenario:
    run = KRun()
    start = run.fresh({"kind": R.KIND_START}, "start")
    run.again(start, "duplicate-identical")
    run.variant({"kind": R.KIND_START, "id": start.id, "payload": {}}, "changed-bytes-same-id")
    run.fresh({"kind": R.KIND_GRANT_LEASE, "payload": {"0": 2}}, "grant-lease")
    run.variant({"kind": R.KIND_SUBMIT, "payload": {"0": 1, "1": 0}, "lease": 1}, "stale-lease")
    receiver = O.ReceiverFenceObserver()
    receiver.install(8)
    for event in run.log:
        receiver.commit(event.ordinal, event.digest.hex())
    receiver.propose(8, "duplicate-applied")
    receiver.propose(8, "duplicate-applied")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 1)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "replacement prefix is valid"),
        expect("duplicate-cached",
               lambda e, o: (_admission(e, "duplicate-identical") or {}).get("outcome") == "cached",
               "identical duplicate returns the original receipt"),
        expect("changed-conflict",
               lambda e, o: (_admission(e, "changed-bytes-same-id") or {}).get("code") == COMMAND_CONFLICT,
               "changed bytes under the same id conflict"),
        expect("stale-lease-refused",
               lambda e, o: (_admission(e, "stale-lease") or {}).get("code") == LEASE_EPOCH_STALE,
               "stale lease epoch refuses rather than starting new work"),
        agree("cached-no-new-event",
              lambda e, o: e["project"][1] == o["receiver"]["durable_ordinal"],
              "a cached duplicate does not advance the canonical ordinal or durable prefix"),
    ]
    return Scenario(
        "SB-14", "commit", "installed-old-epoch", "Full", run, receiver=receiver,
        resources=resources, checks=checks, negative=True,
        expectation_note="duplicate cached; changed bytes COMMAND_CONFLICT; stale lease refused",
        observation_note="dedupe ledger shows no second durable append",
    )


def _sb15() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    receiver = O.ReceiverFenceObserver()
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 2)
    return Scenario(
        "SB-15", "response-loss-before-receipt", "not-installed", "Lazy", run, receiver=receiver,
        resources=resources, supported=False, fallback_disposition="unsupported",
        reason="transport-delivered and applied-business-outcome stages have no independent observer "
               "in a provider-free harness, so the stage projection cannot be cross-checked at the cut",
        expectation_note="RefProject [3]/[12]/[14] read without collapsing to one success flag",
        observation_note="only the canonical draft stage is observable; later stages unmodeled",
    )


def _sb16() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.fresh({"kind": R.KIND_OBSERVE_EFFECT, "payload": {"0": "@effect_token", "1": 2}}, "observe-unknown")
    resources = O.ConservationObserver(gross=10)
    resources.record_raw_report("crash-meter", raw=0, validated=None, reason="crash_incomplete_meter")
    resources.record_raw_report("witnessed-no-call", raw=0, validated=0, reason="complete_witnessed_no_call")
    resources.reserve("op-1", 4)
    resources.annotate_uncertain("op-1", 4)
    resources.recover_withheld(0)
    receiver = O.ReceiverFenceObserver()
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "valid prefix at the admit cut"),
        expect("effect-unknown", lambda e, o: e["project"][14] == ES_UNKNOWN, "no fabricated settlement"),
        observe("crash-zero-not-validated",
                lambda e, o: o["resources"]["reasons"].get("crash-meter") == "crash_incomplete_meter"
                and o["resources"]["raw_reports"].get("crash-meter:validated") is None,
                "raw crash-zero retained raw; validated value null with reason"),
        observe("witnessed-zero-known",
                lambda e, o: o["resources"]["raw_reports"].get("witnessed-no-call:validated") == 0,
                "only a complete witnessed no-call yields a known zero"),
        observe("uncertain-once",
                lambda e, o: o["resources"]["uncertain_annotated_once"]
                and o["resources"]["uncertain"] == {"op-1": 4},
                "uncertain liability annotated exactly once"),
        agree("conserved",
              lambda e, o: o["resources"]["conserved"] and o["resources"]["total"] <= 10,
              "conserved total stays within the gross limit"),
        agree("unknown-effect-holds-liability",
              lambda e, o: e["effect_count"] == 1 and o["resources"]["liability_count"] == 1,
              "the unresolved effect keeps exactly one held liability"),
    ]
    return Scenario(
        "SB-16", "admit", "not-installed", "Full", run, receiver=receiver, resources=resources,
        checks=checks,
        expectation_note="conserved totals; no settlement without observation",
        observation_note="raw zero not validated; uncertain annotated once; totals conserved",
    )


def _sb17() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    run.fresh({"kind": R.KIND_OBSERVE_EFFECT, "payload": {"0": "@effect_token", "1": 2}}, "observe-unknown")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 5)
    resources.annotate_uncertain("op-1", 5)
    resources.withhold(5)
    total_before = resources.total()
    resources.recover_withheld(5)
    total_after = resources.total()
    resources.note_duplicate_meter()
    resources.note_duplicate_meter()
    receiver = O.ReceiverFenceObserver()
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "recovery prefix is valid"),
        expect("unsettled", lambda e, o: e["project"][14] == ES_UNKNOWN,
               "status does not settle without an authoritative observation"),
        observe("recovery-total-invariant",
                lambda e, o: o["resources"]["total"] == total_before == total_after,
                "withheld moves to outstanding without changing the conserved total"),
        observe("uncertain-once",
                lambda e, o: o["resources"]["uncertain_annotated_once"
                               ] and o["resources"]["uncertain"].get("op-1") == 5,
                "one uncertainty is not counted twice"),
        observe("duplicate-meter-ignored",
                lambda e, o: o["resources"]["duplicate_meter_ignored"] == 2,
                "a duplicate cumulative meter does not double-count"),
        agree("disjoint-and-conserved",
              lambda e, o: o["resources"]["disjoint"] and o["resources"]["conserved"],
              "settled and outstanding disjoint; total within gross"),
    ]
    return Scenario(
        "SB-17", "response-loss-after-dispatch", "installed-current", "Lazy", run,
        receiver=receiver, resources=resources, checks=checks,
        expectation_note="effect unresolved; liability attached exactly once",
        observation_note="recovery preserves the total; uncertain annotated once",
    )


def _sb18() -> Scenario:
    run = KRun()
    occurrence = run.fresh({"kind": R.KIND_START}, "eligible-occurrence")
    run.again(occurrence, "duplicate-identical-occurrence")
    run.variant({"kind": R.KIND_START, "id": occurrence.id, "payload": {}}, "altered-payload")
    run.fresh({"kind": R.KIND_GRANT_LEASE, "payload": {"0": 2}}, "advance")
    run.variant({"kind": R.KIND_SUBMIT, "payload": {"0": 1, "1": 0}, "lease": 1}, "expired-occurrence")
    receiver = O.ReceiverFenceObserver()
    receiver.install(8)
    for event in run.log:
        receiver.commit(event.ordinal, event.digest.hex())
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 1)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "eligible occurrence prefix is valid"),
        expect("receipts-per-fresh-command",
               lambda e, o: e["receipt_count"] == _fresh_count(e),
               "one receipt for the eligible key; duplicate is cached and altered is refused"),
        expect("duplicate-cached",
               lambda e, o: (_admission(e, "duplicate-identical-occurrence") or {}).get("outcome") == "cached",
               "identical occurrence returns the original receipt"),
        expect("altered-conflict",
               lambda e, o: (_admission(e, "altered-payload") or {}).get("code") == COMMAND_CONFLICT,
               "altered payload under the same key conflicts"),
        expect("expired-refused",
               lambda e, o: (_admission(e, "expired-occurrence") or {}).get("outcome") == "refused",
               "expired/superseded occurrence yields zero new admissions"),
        agree("one-admission-one-append",
              lambda e, o: e["project"][1] == o["receiver"]["durable_ordinal"],
              "exactly one logical admission maps to one durable append"),
    ]
    return Scenario(
        "SB-18", "admit", "installed-old-epoch", "Full", run, receiver=receiver,
        resources=resources, checks=checks,
        expectation_note="one receipt; altered bytes conflict; expired refused",
        observation_note="key/receipt map shows a single admission",
    )


def _sb19() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_SUBMIT, "payload": {"0": 1, "1": 1}}, "attempt-1-fail")
    run.fresh({"kind": R.KIND_ARM_TIMER}, "arm-1")
    run.fresh({"kind": R.KIND_FIRE_TIMER}, "fire-1")
    run.fresh({"kind": R.KIND_RETRY}, "retry-to-attempt-2")
    run.fresh({"kind": R.KIND_SUBMIT, "payload": {"0": 1, "1": 1}}, "attempt-2-fail")
    run.variant({"kind": R.KIND_RETRY}, "retry-beyond-bound")
    receiver = O.ReceiverFenceObserver()
    receiver.install(8)
    receiver.propose(8, "apply-attempt-1")
    receiver.propose(8, "transport-duplicate")
    resources = O.ConservationObserver(gross=10)
    resources.reserve("op-1", 2)
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "bounded retry prefix is valid"),
        expect("attempt-bounded", lambda e, o: e["project"][8] <= 2, "attempt never exceeds the bound"),
        expect("bound-refused",
               lambda e, o: (_admission(e, "retry-beyond-bound") or {}).get("code") == ATTEMPT_INVALID,
               "a missing nested retry upper bound refuses the bounded profile"),
        expect("receipts-per-fresh-command",
               lambda e, o: e["receipt_count"] == _fresh_count(e),
               "a lost acknowledgement reconciles the original identity; no extra receipt"),
        agree("bounded-liability",
              lambda e, o: o["resources"]["outstanding"] == 2 and e["effect_count"] == 0,
              "combined attempt and liability total stays within the bound"),
    ]
    return Scenario(
        "SB-19", "dispatch", "installed-current", "Full", run, receiver=receiver,
        resources=resources, checks=checks,
        expectation_note="attempt <= 2; third retry refused ATTEMPT_INVALID; receipt stable",
        observation_note="receiver registry distinguishes transport duplicate from new attempt",
    )


def _sb20() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    receiver = O.ReceiverFenceObserver()
    resources = O.ConservationObserver(gross=10)
    return Scenario(
        "SB-20", "commit", "installed-old-epoch", "Full", run, receiver=receiver,
        resources=resources, supported=False, fallback_disposition="unsupported",
        reason="writer takeover requires the declared availability condition, plugin membership and a "
               "restored-backup path that the synthetic kernel does not model; only the stale-append "
               "refusal is in scope",
        expectation_note="single accepted writer after required fencing evidence",
        observation_note="accepted-write order observable, availability/dual-authority semantics absent",
    )


def _sb21() -> Scenario:
    return Scenario(
        "SB-21", "commit", "installed-current", "Full", None, supported=False,
        fallback_disposition="blocked",
        reason="requires an authorized native abrupt reset and durable store; a synthetic substitute "
               "does not qualify and no observer is present for the fault-triggered evidence",
        expectation_note="unavailable: native pre/post-fault ledger cannot be produced provider-free",
        observation_note="absent: no independent native containment observer",
    )


def _sb22() -> Scenario:
    return Scenario(
        "SB-22", "admit", "not-installed", "Full", None, supported=False,
        fallback_disposition="blocked",
        reason="requires a real process launch and incarnation register; a simulated receiver does not "
               "qualify native process containment",
        expectation_note="unavailable: no real launch acknowledgement to bind",
        observation_note="absent: no independent process-incarnation observer",
    )


def _sb23() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    run.fresh({"kind": R.KIND_PREPARE_EFFECT, "payload": {"0": 1}}, "prepare")
    run.fresh({"kind": R.KIND_MARK_DISPATCH, "payload": {"0": "@effect_token"}}, "dispatch")
    resources = O.ConservationObserver(gross=10)
    resources.record_raw_report("interrupted-stream", raw=0, validated=None,
                                reason="explicit_zeroed_crash_report")
    resources.reserve("op-1", 3)
    resources.annotate_uncertain("op-1", 3)
    receiver = O.ReceiverFenceObserver()
    checks = [
        expect("valid-bounded", lambda e, o: e["valid"] is True, "interrupted prefix is valid"),
        expect("unresolved-result", lambda e, o: e["project"][12] is None,
               "result value stays unresolved until a valid observation"),
        expect("effect-unresolved", lambda e, o: e["project"][14] in (ES_INFLIGHT, ES_UNKNOWN),
               "no settlement without an authoritative observation"),
        observe("zero-not-adopted",
                lambda e, o: o["resources"]["raw_reports"].get("interrupted-stream:validated") is None
                and o["resources"]["reasons"].get("interrupted-stream") == "explicit_zeroed_crash_report",
                "explicit zeroed report is not adopted as actual usage"),
        agree("liability-held",
              lambda e, o: e["effect_count"] == 1 and o["resources"]["liability_count"] == 1,
              "interrupted stream holds one liability and reports unknown"),
        agree("conserved",
              lambda e, o: o["resources"]["conserved"],
              "conserved total within the gross limit"),
    ]
    return Scenario(
        "SB-23", "response-loss-before-receipt", "not-installed", "Lazy", run, receiver=receiver,
        resources=resources, checks=checks,
        expectation_note="attempt/retry reflect reconciliation, not blind restart; result unresolved",
        observation_note="zeroed crash report retained raw; liability held without zero usage",
    )


def _sb24() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    receiver = O.ReceiverFenceObserver()
    return Scenario(
        "SB-24", "response-loss-after-dispatch", "installed-current", "Aggressive", run,
        receiver=receiver, supported=False, fallback_disposition="unsupported",
        reason="a generic native abort, a queued follow-up and a pending-approval reconnect have no "
               "provider-free observer; only the cancel-ack-is-not-terminal part is represented",
        expectation_note="effect status unaffected by a prior cancel acknowledgement",
        observation_note="old-epoch approval response binding absent",
    )


def _sb25() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    receiver = O.ReceiverFenceObserver()
    return Scenario(
        "SB-25", "admit", "installed-old-epoch", "Lazy", run, receiver=receiver,
        supported=False, fallback_disposition="unsupported",
        reason="offline spooling, partition recovery and reconnect require an external transport and "
               "authority trace that the synthetic kernel does not provide",
        expectation_note="stale post-reconnect work refused by current authority checks",
        observation_note="no provider-free spool/reconnect observer",
    )


def _sb26() -> Scenario:
    run = KRun()
    run.fresh({"kind": R.KIND_START}, "start")
    receiver = O.ReceiverFenceObserver()
    return Scenario(
        "SB-26", "response-loss-after-dispatch", "installed-current", "Lazy", run,
        receiver=receiver, supported=False, fallback_disposition="unsupported",
        reason="TTL expiry and an effect observable outside the harness require an external service "
               "clock and observer; a simulated receiver does not qualify that service",
        expectation_note="protocol completion distinguished from tool-level outcome",
        observation_note="no external effect-observability or TTL observer",
    )


BUILDERS = [
    _sb01, _sb02, _sb03, _sb04, _sb05, _sb06, _sb07, _sb08, _sb09,
    _sb10, _sb11, _sb12, _sb13, _sb14, _sb15, _sb16, _sb17, _sb18,
    _sb19, _sb20, _sb21, _sb22, _sb23, _sb24, _sb25, _sb26,
]

FIXTURE_ORDER = [f"SB-{n:02d}" for n in range(1, 27)]

POSITIVE_CONTROL = "SB-05"
NEGATIVE_CONTROLS = ("SB-07", "SB-14")


def build_scenarios() -> dict:
    scenarios = {}
    for builder in BUILDERS:
        scenario = builder()
        if scenario.fixture_id in scenarios:
            raise AssertionError(f"duplicate scenario {scenario.fixture_id}")
        scenarios[scenario.fixture_id] = scenario
    missing = [fid for fid in FIXTURE_ORDER if fid not in scenarios]
    if missing:
        raise AssertionError(f"missing scenarios: {missing}")
    return scenarios
