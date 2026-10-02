#!/usr/bin/env python3
"""Independent observation side for FU-03 Stage B (provider-free).

This module is deliberately independent of the Session A reference oracle: it does **not**
import, call or consult ``refstate`` or ``trace_checker``.  It folds a finite schedule of
receiver-fence, Stop-lifecycle and reservation/liability facts into observation ledgers that
the Stage B runner compares against the oracle's expectation side.

Every ledger here is a *simulation* of a receiver, an ownership/Stop graph and a typed-unit
resource account.  A simulated receiver is not qualification of an external service, native
process containment or real automatic takeover; see the Stage B README non-proofs.

Pure Python 3.12 stdlib, deterministic, provider-free, no network, no secrets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Issuers qualified to move the receiver fence.  An unqualified issuer can neither raise nor
# lower the floor, and its mutations are refused regardless of epoch.
QUALIFIED_ISSUERS = frozenset({"authority:current"})

# Outcomes recorded by the receiver mutation ledger.
ACCEPTED = "accepted"
PRIOR_EXPOSURE = "prior_exposure"
REFUSED_STALE = "refused_stale"
REFUSED_UNQUALIFIED = "refused_unqualified"


@dataclass
class Mutation:
    epoch: int
    op: str
    issuer: str
    outcome: str
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "epoch": self.epoch,
            "op": self.op,
            "issuer": self.issuer,
            "outcome": self.outcome,
            "detail": self.detail,
        }


class ReceiverFenceObserver:
    """Durable installed-fence floor, install acknowledgement, mutation ledger and accepted
    committed prefix, observed independently of the candidate reducer.

    The floor is monotonic.  Before any floor is installed a mutation is recorded as *prior
    exposure* (an exposure interval that is never erased and never promoted to a known state);
    after a floor is installed an epoch below it is refused and at or above it is accepted.
    An unqualified issuer is refused for both install and mutation.
    """

    def __init__(self) -> None:
        self.floor: Optional[int] = None
        self.install_acked = False
        self.install_history: list[int] = []
        self.mutations: list[Mutation] = []
        self.durable_prefix: list[tuple[int, str]] = []
        self.restarts = 0

    # -- fence installation -------------------------------------------------
    def install(self, floor: int, issuer: str = "authority:current", *, ack: bool = True) -> Mutation:
        mutation = Mutation(epoch=floor, op="install-floor", issuer=issuer, outcome=ACCEPTED)
        if issuer not in QUALIFIED_ISSUERS:
            mutation.outcome = REFUSED_UNQUALIFIED
            self.mutations.append(mutation)
            return mutation
        if self.floor is not None and floor <= self.floor:
            mutation.outcome = REFUSED_STALE
            mutation.detail = "floor would regress"
            self.mutations.append(mutation)
            return mutation
        self.floor = floor
        self.install_acked = bool(ack)
        self.install_history.append(floor)
        self.mutations.append(mutation)
        return mutation

    # -- mutations ----------------------------------------------------------
    def propose(self, epoch: int, op: str, issuer: str = "authority:current") -> Mutation:
        mutation = Mutation(epoch=epoch, op=op, issuer=issuer, outcome=ACCEPTED)
        if issuer not in QUALIFIED_ISSUERS:
            mutation.outcome = REFUSED_UNQUALIFIED
            mutation.detail = "issuer not qualified to mutate"
        elif self.floor is None:
            mutation.outcome = PRIOR_EXPOSURE
            mutation.detail = "no installed floor; exposure interval pending/unknown"
        elif epoch < self.floor:
            mutation.outcome = REFUSED_STALE
            mutation.detail = f"epoch {epoch} below installed floor {self.floor}"
        self.mutations.append(mutation)
        return mutation

    # -- durable accepted prefix -------------------------------------------
    def commit(self, ordinal: int, digest_hex: str) -> None:
        expected = (self.durable_prefix[-1][0] + 1) if self.durable_prefix else 1
        if ordinal != expected:
            raise ValueError(f"durable append ordinal {ordinal} != expected {expected}")
        self.durable_prefix.append((ordinal, digest_hex))

    def restart(self) -> None:
        """Restart preserves the durable floor, install acknowledgement and prefix."""
        self.restarts += 1

    # -- observations -------------------------------------------------------
    def durable_ordinal(self) -> int:
        return self.durable_prefix[-1][0] if self.durable_prefix else 0

    def durable_tail_hex(self) -> str:
        return self.durable_prefix[-1][1] if self.durable_prefix else ""

    def accepted_total(self) -> int:
        return sum(1 for m in self.mutations if m.outcome in (ACCEPTED, PRIOR_EXPOSURE))

    def post_install_accepted(self) -> int:
        return sum(1 for m in self.mutations if m.outcome == ACCEPTED and m.op != "install-floor")

    def prior_exposure_count(self) -> int:
        return sum(1 for m in self.mutations if m.outcome == PRIOR_EXPOSURE)

    def refused_stale_count(self) -> int:
        return sum(1 for m in self.mutations if m.outcome == REFUSED_STALE)

    def refused_unqualified_count(self) -> int:
        return sum(1 for m in self.mutations if m.outcome == REFUSED_UNQUALIFIED)

    def floor_monotonic(self) -> bool:
        return all(b > a for a, b in zip(self.install_history, self.install_history[1:]))

    def to_dict(self) -> dict:
        return {
            "floor": self.floor,
            "install_acked": self.install_acked,
            "install_history": list(self.install_history),
            "floor_monotonic": self.floor_monotonic(),
            "mutations": [m.to_dict() for m in self.mutations],
            "accepted_total": self.accepted_total(),
            "post_install_accepted": self.post_install_accepted(),
            "prior_exposure_count": self.prior_exposure_count(),
            "refused_stale_count": self.refused_stale_count(),
            "refused_unqualified_count": self.refused_unqualified_count(),
            "durable_ordinal": self.durable_ordinal(),
            "durable_tail_hex": self.durable_tail_hex(),
            "restarts": self.restarts,
        }


@dataclass
class MemberFacts:
    requested: bool = False
    accepted: bool = False
    fenced: bool = False
    acknowledged: bool = False
    local_exited: bool = False
    remote_observed: bool = False

    def to_dict(self) -> dict:
        return {
            "requested": self.requested,
            "accepted": self.accepted,
            "fenced": self.fenced,
            "acknowledged": self.acknowledged,
            "local_exited": self.local_exited,
            "remote_observed": self.remote_observed,
        }

    def quiescent(self) -> bool:
        return self.local_exited or self.remote_observed


class StopObserver:
    """Per-Stop-mode target set and lifecycle facts over an ownership graph.

    Aggressive targets only the selected actor.  Full targets the rooted owned closure from the
    selected roots.  Lazy targets the named next-operation boundary members.  Borrowed (unrelated)
    members are never silently included.  ``unresolved`` members are those with no local exit and
    no remote observation; they keep their liability and block a drained/quiescent claim.
    """

    MODES = ("Aggressive", "Full", "Lazy")

    def __init__(self) -> None:
        self.parent: dict[str, Optional[str]] = {}
        self.borrowed: set[str] = set()
        self.facts: dict[str, MemberFacts] = {}
        self.mode: Optional[str] = None
        self.selected: set[str] = set()
        self.targets: set[str] = set()
        self.boundary_reached = False
        self.relaunch_accepted = False

    def add_member(self, member: str, parent: Optional[str] = None, *, borrowed: bool = False) -> None:
        self.parent[member] = parent
        self.facts.setdefault(member, MemberFacts())
        if borrowed:
            self.borrowed.add(member)

    def _owned_closure(self, roots: set[str]) -> set[str]:
        closure = set(roots)
        changed = True
        while changed:
            changed = False
            for member, parent in self.parent.items():
                if member in self.borrowed:
                    continue
                if parent in closure and member not in closure:
                    closure.add(member)
                    changed = True
        return closure

    def stop(self, mode: str, selected: set[str], *, boundary_reached: bool = False) -> None:
        if mode not in self.MODES:
            raise ValueError(f"unknown Stop mode {mode!r}")
        self.mode = mode
        self.selected = set(selected)
        self.boundary_reached = bool(boundary_reached)
        if mode == "Aggressive":
            self.targets = set(selected)
        elif mode == "Full":
            self.targets = self._owned_closure(set(selected))
        else:  # Lazy
            self.targets = set(selected)
        for member in self.targets:
            self.facts.setdefault(member, MemberFacts()).requested = True

    def record(self, member: str, fact: str) -> None:
        if member not in self.facts:
            raise ValueError(f"unknown member {member!r}")
        if member not in self.targets:
            raise ValueError(f"{member!r} is outside the {self.mode} target set")
        if fact not in MemberFacts().__dict__:
            raise ValueError(f"unknown fact {fact!r}")
        setattr(self.facts[member], fact, True)

    def relaunch(self, member: str, *, accepted: bool) -> None:
        if accepted:
            self.relaunch_accepted = True

    def unresolved(self) -> list[str]:
        return sorted(m for m, f in self.facts.items()
                      if m in self.targets and not f.quiescent())

    def excluded(self) -> list[str]:
        return sorted(set(self.parent) - self.targets)

    def borrowed_preserved(self) -> bool:
        return all(m not in self.targets for m in self.borrowed)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "selected": sorted(self.selected),
            "targets": sorted(self.targets),
            "excluded": self.excluded(),
            "borrowed": sorted(self.borrowed),
            "borrowed_preserved": self.borrowed_preserved(),
            "boundary_reached": self.boundary_reached,
            "relaunch_accepted": self.relaunch_accepted,
            "facts": {m: f.to_dict() for m, f in sorted(self.facts.items())},
            "unresolved": self.unresolved(),
        }


class ConservationObserver:
    """Typed-unit reservation/liability account: settled (S), outstanding (O), withheld (H) and
    proposed (P), plus uncertain liabilities annotated at most once.

    Recovery moves withheld allowance into outstanding *without changing the conserved total*.
    Settled and outstanding are disjoint.  A missing counter is never read as released liability
    or zero usage: an uncertain liability stays annotated exactly once until an authoritative
    settlement arrives.
    """

    def __init__(self, gross: int) -> None:
        self.gross = int(gross)
        self.settled = 0
        self.outstanding = 0
        self.withheld = 0
        self.proposed = 0
        self.operations: dict[str, int] = {}
        self.uncertain: dict[str, int] = {}
        self.raw_reports: dict[str, Optional[int]] = {}
        self.reasons: dict[str, str] = {}
        self.duplicate_meter_ignored = 0

    # -- lifecycle ----------------------------------------------------------
    def reserve(self, op_id: str, amount: int) -> bool:
        if op_id in self.operations:
            return False
        self.operations[op_id] = int(amount)
        self.outstanding += int(amount)
        return True

    def settle(self, op_id: str, amount: int) -> bool:
        held = self.operations.get(op_id)
        if held is None or amount > held:
            return False
        self.operations.pop(op_id)
        self.outstanding -= held
        self.settled += int(amount)
        return True

    def withhold(self, amount: int) -> None:
        self.withheld += int(amount)

    def recover_withheld(self, amount: int) -> None:
        """Move withheld allowance into outstanding; the conserved total is unchanged."""
        amount = min(int(amount), self.withheld)
        self.withheld -= amount
        self.outstanding += amount

    # -- uncertain / raw reports -------------------------------------------
    def annotate_uncertain(self, key: str, amount: int) -> bool:
        if key in self.uncertain:
            return False
        self.uncertain[key] = int(amount)
        return True

    def record_raw_report(self, key: str, raw: Optional[int], validated: Optional[int], reason: str) -> None:
        self.raw_reports[key] = raw
        self.reasons[key] = reason
        if validated is not None:
            self.raw_reports[key + ":validated"] = validated

    def note_duplicate_meter(self) -> None:
        self.duplicate_meter_ignored += 1

    # -- observations -------------------------------------------------------
    def total(self) -> int:
        return self.settled + self.outstanding + self.withheld + self.proposed

    def conserved(self) -> bool:
        return self.total() <= self.gross

    def disjoint(self) -> bool:
        return self.settled >= 0 and self.outstanding >= 0

    def liability_count(self) -> int:
        return len(self.operations)

    def uncertain_annotated_once(self) -> bool:
        return len(set(self.uncertain)) == len(self.uncertain)

    def to_dict(self) -> dict:
        return {
            "gross": self.gross,
            "settled": self.settled,
            "outstanding": self.outstanding,
            "withheld": self.withheld,
            "proposed": self.proposed,
            "total": self.total(),
            "conserved": self.conserved(),
            "disjoint": self.disjoint(),
            "liability_count": self.liability_count(),
            "uncertain": dict(self.uncertain),
            "uncertain_annotated_once": self.uncertain_annotated_once(),
            "raw_reports": dict(self.raw_reports),
            "reasons": dict(self.reasons),
            "duplicate_meter_ignored": self.duplicate_meter_ignored,
        }


class ReceiptBindingObserver:
    """Independent per-operation receipt binding: distinguishes the original incarnation of an
    operation from a wrong incarnation and deduplicates historical receipts."""

    def __init__(self) -> None:
        self.bindings: dict[str, dict] = {}
        self.accepted = 0
        self.duplicates = 0
        self.wrong_incarnation_refused = 0
        self.historical = 0

    def record(self, op_id: str, incarnation: str, payload_digest: str) -> str:
        existing = self.bindings.get(op_id)
        if existing is None:
            self.bindings[op_id] = {"incarnation": incarnation, "digest": payload_digest}
            self.accepted += 1
            return "accepted"
        if existing["incarnation"] != incarnation:
            self.wrong_incarnation_refused += 1
            return "wrong_incarnation"
        if existing["digest"] == payload_digest:
            self.duplicates += 1
            return "duplicate"
        self.historical += 1
        return "historical_conflict"

    def to_dict(self) -> dict:
        return {
            "bindings": dict(self.bindings),
            "accepted": self.accepted,
            "duplicates": self.duplicates,
            "wrong_incarnation_refused": self.wrong_incarnation_refused,
            "historical": self.historical,
        }
