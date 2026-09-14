"""Literal and adversarial tests for the inert recovery reservation ledger.

The expectations in PREFIX_CASES were frozen before ledger.py existed.  They are
deliberately plain tuples so the expected arithmetic is not computed by the reducer.
"""

import copy
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from ledger import (  # noqa: E402
    AdmissionError,
    ConflictError,
    Ledger,
    ValidationError,
    replay,
)


def binding(task, goal, unit, quantum, window):
    return {
        "task_id": task,
        "goal_id": goal,
        "unit": unit,
        "quantum": quantum,
        "window_id": window,
    }


TOKENS = binding("task-a", "goal-a", "tokens", 1, "provider-window-1")
CENTS = binding("task-b", "goal-a", "usd-minor", 1, "billing-window-1")


def freeze(
    event_id,
    boundary_id,
    bind,
    normal_use,
    p,
    q,
    previous=None,
    sources=(),
    required_components=(),
):
    return {
        "event_id": event_id,
        "type": "boundary_frozen",
        "boundary_id": boundary_id,
        "binding": copy.deepcopy(bind),
        "normal_use": normal_use,
        "fraction": {"p": p, "q": q},
        "previous_boundary_id": previous,
        "normal_source_ids": list(sources),
        "component_ids": list(required_components),
    }


def reserve(event_id, reservation_id, boundary_id, bind, amount, components=()):
    return {
        "event_id": event_id,
        "type": "reservation_created",
        "reservation_id": reservation_id,
        "effect_id": "effect-" + reservation_id,
        "boundary_id": boundary_id,
        "binding": copy.deepcopy(bind),
        "upper_bound": amount,
        "components": [copy.deepcopy(row) for row in components],
    }


def settle(event_id, settlement_id, reservation_id, boundary_id, bind, actual, components=()):
    return {
        "event_id": event_id,
        "type": "reservation_settled",
        "settlement_id": settlement_id,
        "reservation_id": reservation_id,
        "effect_id": "effect-" + reservation_id,
        "boundary_id": boundary_id,
        "binding": copy.deepcopy(bind),
        "actual": actual,
        "components": [copy.deepcopy(row) for row in components],
    }


def unknown(event_id, reservation_id, boundary_id, bind):
    return {
        "event_id": event_id,
        "type": "effect_unknown",
        "reservation_id": reservation_id,
        "effect_id": "effect-" + reservation_id,
        "boundary_id": boundary_id,
        "binding": copy.deepcopy(bind),
    }


def restart(event_id):
    return {"event_id": event_id, "type": "process_restarted"}


def reset(event_id, boundary_id, bind, identity_status, reset_id=None):
    return {
        "event_id": event_id,
        "type": "provider_counter_reset",
        "reset_id": reset_id or ("reset-" + boundary_id),
        "boundary_id": boundary_id,
        "binding": copy.deepcopy(bind),
        "identity_status": identity_status,
    }


def normal(event_id, source_id, boundary_id, bind, amount):
    return {
        "event_id": event_id,
        "type": "normal_use_verified",
        "source_id": source_id,
        "boundary_id": boundary_id,
        "binding": copy.deepcopy(bind),
        "amount": amount,
    }


def cap(event_id, component_id, kind, scope_id, unit, quantum, window, ceiling, used=0, status="known"):
    return {
        "event_id": event_id,
        "type": "cap_configured",
        "component_id": component_id,
        "kind": kind,
        "scope_id": scope_id,
        "unit": unit,
        "quantum": quantum,
        "window_id": window,
        "ceiling": ceiling,
        "used": used,
        "identity_status": status,
    }


def claim(component_id, unit, quantum, window, amount):
    return {
        "component_id": component_id,
        "unit": unit,
        "quantum": quantum,
        "window_id": window,
        "amount": amount,
    }


FLOOR_EVENTS = (
    freeze("floor-1", "floor", TOKENS, 10, 1, 3),
)

PARTIAL_EVENTS = (
    freeze("partial-1", "partial", TOKENS, 100, 1, 10),
    reserve("partial-2", "r-partial", "partial", TOKENS, 8),
    settle("partial-3", "s-partial", "r-partial", "partial", TOKENS, 3),
)

UNKNOWN_EVENTS = (
    freeze("unknown-1", "unknown", TOKENS, 100, 1, 10),
    reserve("unknown-2", "r-unknown", "unknown", TOKENS, 7),
    unknown("unknown-3", "r-unknown", "unknown", TOKENS),
    reset("unknown-4", "unknown", TOKENS, "reconciled"),
    restart("unknown-5"),
)

NORMAL_EVENTS = (
    freeze("normal-1", "normal-old", TOKENS, 100, 1, 10),
    normal("normal-2", "normal-source-50", "normal-old", TOKENS, 50),
    freeze(
        "normal-3",
        "normal-new",
        TOKENS,
        150,
        1,
        10,
        previous="normal-old",
        sources=("normal-source-50",),
    ),
)

COMPONENT_CLAIMS = (
    claim("parent-cap", "tokens", 1, "provider-window-1", 6),
    claim("pool-cap", "tokens", 1, "provider-window-1", 6),
    claim("resource-cap", "quota-points", 1, "quota-window-1", 3),
)
COMPONENT_EVENTS = (
    cap("component-1", "parent-cap", "parent", "goal-a", "tokens", 1, "provider-window-1", 20),
    cap("component-2", "pool-cap", "pool", "pool-a", "tokens", 1, "provider-window-1", 7),
    cap("component-3", "resource-cap", "resource", "route-a", "quota-points", 1, "quota-window-1", 3),
    freeze(
        "component-4",
        "component",
        TOKENS,
        100,
        1,
        10,
        required_components=("parent-cap", "pool-cap", "resource-cap"),
    ),
    reserve("component-5", "r-component", "component", TOKENS, 6, COMPONENT_CLAIMS),
)

UNLIKE_EVENTS = (
    freeze("unlike-1", "token-boundary", TOKENS, 50, 1, 10),
    freeze("unlike-2", "cent-boundary", CENTS, 50, 1, 10),
    reserve("unlike-3", "r-token", "token-boundary", TOKENS, 4),
    reserve("unlike-4", "r-cent", "cent-boundary", CENTS, 4),
)


# A boundary signature is:
# (N, B, C, R, available, pending_normal_use, blockers,
#  ((reservation_id, status, upper_bound, actual), ...))
# A component signature is:
# (kind, used, ceiling, C, R, available, blockers)
# All values below are literal expectations, frozen before reducer implementation.
PREFIX_CASES = {
    "floor-non-integral": {
        "events": FLOOR_EVENTS,
        "boundaries": ("floor",),
        "caps": (),
        "expected": (
            ((("floor", (10, 3, 0, 0, 3, 0, (), ())),), ()),
        ),
    },
    "reserve-partial-settle": {
        "events": PARTIAL_EVENTS,
        "boundaries": ("partial",),
        "caps": (),
        "expected": (
            ((("partial", (100, 10, 0, 0, 10, 0, (), ())),), ()),
            ((("partial", (100, 10, 0, 8, 2, 0, (), (("r-partial", "reserved", 8, None),))),), ()),
            ((("partial", (100, 10, 3, 0, 7, 0, (), (("r-partial", "settled", 8, 3),))),), ()),
        ),
    },
    "unknown-reset-restart": {
        "events": UNKNOWN_EVENTS,
        "boundaries": ("unknown",),
        "caps": (),
        "expected": (
            ((("unknown", (100, 10, 0, 0, 10, 0, (), ())),), ()),
            ((("unknown", (100, 10, 0, 7, 3, 0, (), (("r-unknown", "reserved", 7, None),))),), ()),
            ((("unknown", (100, 10, 0, 7, 3, 0, (), (("r-unknown", "unknown", 7, None),))),), ()),
            ((("unknown", (100, 10, 0, 7, 3, 0, (), (("r-unknown", "unknown", 7, None),))),), ()),
            ((("unknown", (100, 10, 0, 7, 3, 0, (), (("r-unknown", "unknown", 7, None),))),), ()),
        ),
    },
    "verified-normal-successor": {
        "events": NORMAL_EVENTS,
        "boundaries": ("normal-old", "normal-new"),
        "caps": (),
        "expected": (
            ((("normal-old", (100, 10, 0, 0, 10, 0, (), ())), ("normal-new", None)), ()),
            ((("normal-old", (100, 10, 0, 0, 10, 50, (), ())), ("normal-new", None)), ()),
            ((("normal-old", (100, 10, 0, 0, 10, 0, (), ())), ("normal-new", (150, 15, 0, 0, 15, 0, (), ()))), ()),
        ),
    },
    "componentwise-limits": {
        "events": COMPONENT_EVENTS,
        "boundaries": ("component",),
        "caps": ("parent-cap", "pool-cap", "resource-cap"),
        "expected": (
            ((("component", None),), (("parent-cap", ("parent", 0, 20, 0, 0, 20, ())), ("pool-cap", None), ("resource-cap", None))),
            ((("component", None),), (("parent-cap", ("parent", 0, 20, 0, 0, 20, ())), ("pool-cap", ("pool", 0, 7, 0, 0, 7, ())), ("resource-cap", None))),
            ((("component", None),), (("parent-cap", ("parent", 0, 20, 0, 0, 20, ())), ("pool-cap", ("pool", 0, 7, 0, 0, 7, ())), ("resource-cap", ("resource", 0, 3, 0, 0, 3, ())))),
            ((("component", (100, 10, 0, 0, 10, 0, (), ())),), (("parent-cap", ("parent", 0, 20, 0, 0, 20, ())), ("pool-cap", ("pool", 0, 7, 0, 0, 7, ())), ("resource-cap", ("resource", 0, 3, 0, 0, 3, ())))),
            ((("component", (100, 10, 0, 6, 4, 0, (), (("r-component", "reserved", 6, None),))),), (("parent-cap", ("parent", 0, 20, 0, 6, 14, ())), ("pool-cap", ("pool", 0, 7, 0, 6, 1, ())), ("resource-cap", ("resource", 0, 3, 0, 3, 0, ())))),
        ),
    },
    "unlike-units-distinct": {
        "events": UNLIKE_EVENTS,
        "boundaries": ("token-boundary", "cent-boundary"),
        "caps": (),
        "expected": (
            ((("token-boundary", (50, 5, 0, 0, 5, 0, (), ())), ("cent-boundary", None)), ()),
            ((("token-boundary", (50, 5, 0, 0, 5, 0, (), ())), ("cent-boundary", (50, 5, 0, 0, 5, 0, (), ()))), ()),
            ((("token-boundary", (50, 5, 0, 4, 1, 0, (), (("r-token", "reserved", 4, None),))), ("cent-boundary", (50, 5, 0, 0, 5, 0, (), ()))), ()),
            ((("token-boundary", (50, 5, 0, 4, 1, 0, (), (("r-token", "reserved", 4, None),))), ("cent-boundary", (50, 5, 0, 4, 1, 0, (), (("r-cent", "reserved", 4, None),)))), ()),
        ),
    },
}

REQUIRED_CASES = (
    "literal-prefix-audit",
    "positive-reserve-partial-settlement",
    "competing-reservations",
    "unknown-effect-serialize-reopen",
    "duplicate-settlement-charges-once",
    "conflicting-duplicate-refuses",
    "cumulative-retries-cap",
    "provider-reset-daemon-restart",
    "recovery-cost-not-normal-use",
    "verified-additional-normal-work",
    "unknown-baseline-window-blocks",
    "invalid-integers-fraction-quantum",
    "componentwise-parent-pool-resource",
    "unlike-units-never-combine",
    "observation-without-admission",
)

MUTATION_NAMES = (
    "erase-R-on-restart",
    "erase-C-on-provider-reset",
    "charge-duplicate-settlement",
    "ceil-instead-of-floor",
    "count-recovery-as-normal-use",
    "mix-unlike-units",
)


def boundary_signature(instance, boundary_id):
    if boundary_id not in instance.boundary_ids():
        return None
    view = instance.observe(boundary_id)
    return (
        view["N"],
        view["B"],
        view["C"],
        view["R"],
        view["available"],
        view["pending_normal_use"],
        tuple(view["blockers"]),
        tuple(
            (row["reservation_id"], row["status"], row["upper_bound"], row["actual"])
            for row in view["reservations"]
        ),
    )


def cap_signature(instance, component_id):
    if component_id not in instance.component_ids():
        return None
    view = instance.observe_component(component_id)
    return (
        view["kind"],
        view["used"],
        view["ceiling"],
        view["C"],
        view["R"],
        view["available"],
        tuple(view["blockers"]),
    )


def selected_signature(instance, boundary_ids, component_ids):
    return (
        tuple((item, boundary_signature(instance, item)) for item in boundary_ids),
        tuple((item, cap_signature(instance, item)) for item in component_ids),
    )


def audit_all_prefixes():
    count = 0
    for name, case in PREFIX_CASES.items():
        events = case["events"]
        expected = case["expected"]
        if len(events) != len(expected):
            raise AssertionError("unfrozen prefix inventory: " + name)
        for end, literal in enumerate(expected, 1):
            count += 1
            actual = selected_signature(
                replay(events[:end]), case["boundaries"], case["caps"]
            )
            if actual != literal:
                raise AssertionError((name, end, literal, actual))
    return count


def assert_raises(error, fn, *args):
    try:
        fn(*args)
    except error:
        return
    raise AssertionError("expected " + error.__name__)


class EraseROnRestart(Ledger):
    def _apply_restart(self, event):
        result = super()._apply_restart(event)
        for account in self._accounts.values():
            account["R"] = 0
        return result


class EraseCOnReset(Ledger):
    def _apply_reset(self, event):
        result = super()._apply_reset(event)
        account = self._accounts[self._boundaries[event["boundary_id"]]["account_key"]]
        account["C"] = 0
        return result


class ChargeDuplicateSettlement(Ledger):
    def _apply_settlement(self, event):
        result = super()._apply_settlement(event)
        if result == "duplicate":
            reservation = self._reservations[event["reservation_id"]]
            account = self._accounts[
                self._boundaries[reservation["boundary_id"]]["account_key"]
            ]
            account["C"] += event["actual"]
        return result


class CeilAllowance(Ledger):
    def _apply_boundary(self, event):
        result = super()._apply_boundary(event)
        if result == "applied":
            boundary = self._boundaries[event["boundary_id"]]
            if boundary["N"] is not None:
                boundary["B"] = (
                    boundary["p"] * boundary["N"] + boundary["q"] - 1
                ) // boundary["q"]
        return result


class CountRecoveryAsNormal(Ledger):
    def _apply_settlement(self, event):
        result = super()._apply_settlement(event)
        if result == "applied":
            boundary = self._boundaries[event["boundary_id"]]
            boundary["N"] += event["actual"]
            boundary["B"] = boundary["p"] * boundary["N"] // boundary["q"]
        return result


class MixUnlikeUnits(Ledger):
    def _apply_reservation(self, event):
        result = super()._apply_reservation(event)
        if result == "applied":
            source = self._boundaries[event["boundary_id"]]
            for key, account in self._accounts.items():
                if key != source["account_key"] and key[1] == source["binding"]["goal_id"]:
                    account["R"] += event["upper_bound"]
        return result


MUTANT_CLASSES = {
    "erase-R-on-restart": EraseROnRestart,
    "erase-C-on-provider-reset": EraseCOnReset,
    "charge-duplicate-settlement": ChargeDuplicateSettlement,
    "ceil-instead-of-floor": CeilAllowance,
    "count-recovery-as-normal-use": CountRecoveryAsNormal,
    "mix-unlike-units": MixUnlikeUnits,
}


def replay_with(ledger_class, events):
    instance = ledger_class()
    for event in events:
        instance.append(event)
    return instance


def mutant_prefix_rejected(ledger_class, case_name):
    case = PREFIX_CASES[case_name]
    try:
        for end, expected in enumerate(case["expected"], 1):
            state = replay_with(ledger_class, case["events"][:end])
            actual = selected_signature(state, case["boundaries"], case["caps"])
            if actual != expected:
                return True
    except (AdmissionError, ConflictError, ValidationError):
        return True
    return False


def run_mutation_controls():
    detected = []
    if mutant_prefix_rejected(EraseROnRestart, "unknown-reset-restart"):
        detected.append("erase-R-on-restart")

    reset_events = PARTIAL_EVENTS + (reset("mut-reset", "partial", TOKENS, "reconciled"),)
    expected_partial = PREFIX_CASES["reserve-partial-settle"]["expected"][-1][0][0][1]
    state = replay_with(EraseCOnReset, reset_events)
    if boundary_signature(state, "partial") != expected_partial:
        detected.append("erase-C-on-provider-reset")

    duplicate = settle("partial-duplicate", "s-partial", "r-partial", "partial", TOKENS, 3)
    state = replay_with(ChargeDuplicateSettlement, PARTIAL_EVENTS + (duplicate,))
    if boundary_signature(state, "partial") != expected_partial:
        detected.append("charge-duplicate-settlement")

    if mutant_prefix_rejected(CeilAllowance, "floor-non-integral"):
        detected.append("ceil-instead-of-floor")
    if mutant_prefix_rejected(CountRecoveryAsNormal, "reserve-partial-settle"):
        detected.append("count-recovery-as-normal-use")
    if mutant_prefix_rejected(MixUnlikeUnits, "unlike-units-distinct"):
        detected.append("mix-unlike-units")

    if tuple(MUTANT_CLASSES) != MUTATION_NAMES or tuple(detected) != MUTATION_NAMES:
        raise AssertionError((MUTATION_NAMES, detected))
    return tuple(detected)


class RecoveryLedgerTests(unittest.TestCase):
    def test_literal_prefix_audit(self):
        self.assertEqual(audit_all_prefixes(), 21)

    def test_positive_reserve_partial_settlement(self):
        state = replay(PARTIAL_EVENTS)
        self.assertEqual(boundary_signature(state, "partial")[:6], (100, 10, 3, 0, 7, 0))

    def test_competing_reservations(self):
        events = (
            freeze("compete-1", "compete", TOKENS, 100, 1, 10),
            reserve("compete-2", "r-six", "compete", TOKENS, 6),
            reserve("compete-3", "r-four", "compete", TOKENS, 4),
        )
        state = replay(events)
        self.assertEqual(boundary_signature(state, "compete")[3:5], (10, 0))
        assert_raises(
            AdmissionError,
            state.append,
            reserve("compete-4", "r-one", "compete", TOKENS, 1),
        )

    def test_unknown_effect_serialize_reopen(self):
        state = replay(UNKNOWN_EVENTS)
        reopened = Ledger.from_json(state.to_json())
        self.assertEqual(
            boundary_signature(reopened, "unknown"),
            PREFIX_CASES["unknown-reset-restart"]["expected"][-1][0][0][1],
        )
        self.assertEqual(json.loads(reopened.to_json()), json.loads(state.to_json()))
        reopened.append(
            settle(
                "unknown-6",
                "s-unknown",
                "r-unknown",
                "unknown",
                TOKENS,
                2,
            )
        )
        self.assertEqual(boundary_signature(reopened, "unknown")[2:5], (2, 0, 8))

    def test_duplicate_settlement_charges_once(self):
        duplicate = settle("dup-new-event", "s-partial", "r-partial", "partial", TOKENS, 3)
        state = replay(PARTIAL_EVENTS + (duplicate,))
        self.assertEqual(boundary_signature(state, "partial")[2:4], (3, 0))
        self.assertIn('"event_id":"dup-new-event"', state.to_json())
        assert_raises(
            ConflictError,
            state.append,
            reserve("dup-new-event", "r-alias", "partial", TOKENS, 1),
        )

    def test_conflicting_duplicate_refuses(self):
        state = replay(PARTIAL_EVENTS)
        bad = settle("dup-conflict", "s-partial", "r-partial", "partial", TOKENS, 4)
        assert_raises(ConflictError, state.append, bad)
        bad_event = copy.deepcopy(PARTIAL_EVENTS[-1])
        bad_event["actual"] = 4
        assert_raises(ConflictError, replay, PARTIAL_EVENTS + (bad_event,))

    def test_cumulative_retries_cap(self):
        events = (
            freeze("retry-1", "retry", TOKENS, 100, 1, 10),
            reserve("retry-2", "r-retry-1", "retry", TOKENS, 6),
            settle("retry-3", "s-retry-1", "r-retry-1", "retry", TOKENS, 6),
            reserve("retry-4", "r-retry-2", "retry", TOKENS, 4),
            settle("retry-5", "s-retry-2", "r-retry-2", "retry", TOKENS, 4),
        )
        state = replay(events)
        self.assertEqual(boundary_signature(state, "retry")[2:5], (10, 0, 0))
        assert_raises(
            AdmissionError,
            state.append,
            reserve("retry-6", "r-retry-3", "retry", TOKENS, 1),
        )

    def test_provider_reset_daemon_restart(self):
        events = (
            freeze("preserve-1", "preserve", TOKENS, 100, 1, 10),
            reserve("preserve-2", "r-done", "preserve", TOKENS, 2),
            settle("preserve-3", "s-done", "r-done", "preserve", TOKENS, 2),
            reserve("preserve-4", "r-held", "preserve", TOKENS, 6),
            reset(
                "preserve-5",
                "preserve",
                TOKENS,
                "reconciled",
                reset_id="preserve-reset-1",
            ),
            restart("preserve-6"),
        )
        state = replay(events)
        self.assertEqual(boundary_signature(state, "preserve")[2:5], (2, 6, 2))
        self.assertEqual(boundary_signature(Ledger.from_json(state.to_json()), "preserve")[2:5], (2, 6, 2))
        state.append(
            reset(
                "preserve-7",
                "preserve",
                TOKENS,
                "unknown",
                reset_id="preserve-reset-2",
            )
        )
        self.assertEqual(boundary_signature(state, "preserve")[2:5], (2, 6, None))
        assert_raises(
            AdmissionError,
            state.append,
            reserve("preserve-8", "r-reset-blocked", "preserve", TOKENS, 1),
        )
        state.append(
            reset(
                "preserve-9",
                "preserve",
                TOKENS,
                "reconciled",
                reset_id="preserve-reset-2",
            )
        )
        self.assertEqual(boundary_signature(state, "preserve")[2:5], (2, 6, 2))

        window_two = binding("task-reset", "goal-reset", "tokens", 1, "window-2")
        window_one = binding("task-reset", "goal-reset", "tokens", 1, "window-1")
        cross_window = replay(
            (
                freeze("cross-1", "cross-old", window_one, 100, 1, 10),
                reset(
                    "cross-2",
                    "cross-old",
                    window_one,
                    "unknown",
                    reset_id="cross-reset-old",
                ),
                normal("cross-3", "cross-normal-50", "cross-old", window_one, 50),
                freeze(
                    "cross-4",
                    "cross-new",
                    window_two,
                    150,
                    1,
                    10,
                    previous="cross-old",
                    sources=("cross-normal-50",),
                ),
                reset(
                    "cross-5",
                    "cross-new",
                    window_two,
                    "unknown",
                    reset_id="cross-reset-new",
                ),
                reset(
                    "cross-6",
                    "cross-old",
                    window_one,
                    "reconciled",
                    reset_id="cross-reset-old",
                ),
            )
        )
        self.assertIn(
            "unknown-counter-reset-identity",
            cross_window.observe("cross-new")["blockers"],
        )
        self.assertEqual(
            cross_window.observe("cross-new")["unresolved_resets"],
            [
                {
                    "reset_id": "cross-reset-new",
                    "boundary_id": "cross-new",
                    "window_id": "window-2",
                }
            ],
        )
        assert_raises(
            AdmissionError,
            cross_window.append,
            reserve("cross-7", "r-cross-blocked", "cross-new", window_two, 1),
        )
        cross_window.append(
            reset(
                "cross-8",
                "cross-new",
                window_two,
                "reconciled",
                reset_id="cross-reset-new",
            )
        )
        self.assertEqual(cross_window.append(
            reserve("cross-9", "r-cross-admitted", "cross-new", window_two, 1)
        ), "applied")

    def test_recovery_cost_not_normal_use(self):
        state = replay(PARTIAL_EVENTS)
        self.assertEqual(boundary_signature(state, "partial")[:2], (100, 10))

    def test_verified_additional_normal_work(self):
        state = replay(NORMAL_EVENTS)
        self.assertEqual(boundary_signature(state, "normal-old")[:2], (100, 10))
        self.assertEqual(boundary_signature(state, "normal-new")[:2], (150, 15))
        carried_events = PARTIAL_EVENTS + (
            normal("carry-1", "carry-normal-50", "partial", TOKENS, 50),
            freeze(
                "carry-2",
                "partial-successor",
                TOKENS,
                150,
                1,
                10,
                previous="partial",
                sources=("carry-normal-50",),
            ),
        )
        carried = replay(carried_events)
        self.assertEqual(
            boundary_signature(carried, "partial-successor")[:5],
            (150, 15, 3, 0, 12),
        )
        carried.append(
            reserve("carry-3", "r-carried", "partial-successor", TOKENS, 12)
        )
        assert_raises(
            AdmissionError,
            carried.append,
            reserve("carry-4", "r-carried-over", "partial-successor", TOKENS, 1),
        )

        duplicate_root = freeze("carry-root", "duplicate-root", TOKENS, 100, 1, 10)
        assert_raises(ConflictError, replay, (PARTIAL_EVENTS[0], duplicate_root))

        held = replay(
            UNKNOWN_EVENTS
            + (
                reset(
                    "carry-unknown-reset",
                    "unknown",
                    TOKENS,
                    "unknown",
                    reset_id="carry-unknown-reset-id",
                ),
                normal("carry-unknown-normal", "carry-unknown-50", "unknown", TOKENS, 50),
                freeze(
                    "carry-unknown-next",
                    "unknown-successor",
                    TOKENS,
                    150,
                    1,
                    10,
                    previous="unknown",
                    sources=("carry-unknown-50",),
                ),
            )
        )
        self.assertEqual(boundary_signature(held, "unknown-successor")[2:4], (0, 7))
        self.assertIn(
            "unknown-counter-reset-identity",
            held.observe("unknown-successor")["blockers"],
        )
        assert_raises(
            AdmissionError,
            held.append,
            reserve("carry-unknown-block", "r-carry-unknown", "unknown-successor", TOKENS, 1),
        )

    def test_unknown_baseline_window_blocks(self):
        unknown_baseline = freeze("block-1", "block-baseline", TOKENS, None, 1, 10)
        unknown_window_binding = binding("task-window", "goal-a", "tokens", 1, None)
        unknown_window = freeze("block-2", "block-window", unknown_window_binding, 100, 1, 10)
        state = replay((unknown_baseline, unknown_window))
        self.assertEqual(state.observe("block-baseline")["blockers"], ["unknown-baseline"])
        self.assertEqual(state.observe("block-window")["blockers"], ["unknown-window"])
        assert_raises(
            AdmissionError,
            state.append,
            reserve("block-3", "r-block", "block-baseline", TOKENS, 1),
        )
        state.append(
            normal(
                "block-4",
                "block-window-normal",
                "block-window",
                unknown_window_binding,
                50,
            )
        )
        resolved_window_binding = binding(
            "task-window", "goal-a", "tokens", 1, "provider-window-resolved"
        )
        state.append(
            freeze(
                "block-5",
                "block-window-successor",
                resolved_window_binding,
                150,
                1,
                10,
                previous="block-window",
                sources=("block-window-normal",),
            )
        )
        self.assertIn(
            "unknown-window",
            state.observe("block-window-successor")["blockers"],
        )
        assert_raises(
            AdmissionError,
            state.append,
            reserve(
                "block-6",
                "r-block-window",
                "block-window-successor",
                resolved_window_binding,
                1,
            ),
        )

    def test_invalid_integers_fraction_quantum(self):
        variants = []
        for field, value in (("normal_use", True), ("normal_use", -1)):
            event = freeze("invalid-" + field + str(value), "invalid-" + str(len(variants)), TOKENS, 10, 1, 10)
            event[field] = value
            variants.append(event)
        event = freeze("invalid-p", "invalid-p", TOKENS, 10, -1, 10)
        variants.append(event)
        event = freeze("invalid-q", "invalid-q", TOKENS, 10, 1, 0)
        variants.append(event)
        event = freeze("invalid-fraction", "invalid-fraction", TOKENS, 10, 11, 10)
        variants.append(event)
        for quantum in (0, -1, True, 1.0):
            bind = binding("task-a", "goal-a", "tokens", quantum, "provider-window-1")
            variants.append(freeze("invalid-quantum-" + repr(quantum), "invalid-q-" + repr(quantum), bind, 10, 1, 10))
        for event in variants:
            assert_raises(ValidationError, replay, (event,))
        state = replay((freeze("invalid-r-1", "invalid-r", TOKENS, 100, 1, 10),))
        for amount in (True, -1, 0, 1.5):
            assert_raises(
                ValidationError,
                state.append,
                reserve("invalid-r-" + repr(amount), "invalid-res-" + repr(amount), "invalid-r", TOKENS, amount),
            )

    def test_componentwise_parent_pool_resource(self):
        state = replay(COMPONENT_EVENTS)
        self.assertEqual(cap_signature(state, "resource-cap")[3:6], (0, 3, 0))
        extra_claims = (
            claim("parent-cap", "tokens", 1, "provider-window-1", 1),
            claim("pool-cap", "tokens", 1, "provider-window-1", 1),
            claim("resource-cap", "quota-points", 1, "quota-window-1", 1),
        )
        assert_raises(
            AdmissionError,
            state.append,
            reserve("component-6", "r-component-2", "component", TOKENS, 1, extra_claims),
        )
        component_actual = (
            claim("parent-cap", "tokens", 1, "provider-window-1", 4),
            claim("pool-cap", "tokens", 1, "provider-window-1", 4),
            claim("resource-cap", "quota-points", 1, "quota-window-1", 2),
        )
        settlement = settle(
            "component-7",
            "s-component",
            "r-component",
            "component",
            TOKENS,
            4,
            component_actual,
        )
        state.append(settlement)
        self.assertEqual(cap_signature(state, "pool-cap")[3:6], (4, 0, 3))
        duplicate = copy.deepcopy(settlement)
        duplicate["event_id"] = "component-8"
        self.assertEqual(state.append(duplicate), "duplicate")
        self.assertEqual(cap_signature(state, "pool-cap")[3:6], (4, 0, 3))

        # Each component kind gets its own decisive bottleneck.  Disabling either
        # parent or pool enforcement must no longer survive behind resource refusal.
        for target_kind in ("parent", "pool", "resource"):
            prefix = "guard-" + target_kind
            component_ids = (prefix + "-parent", prefix + "-pool", prefix + "-resource")
            ceilings = {
                "parent": 6 if target_kind == "parent" else 20,
                "pool": 6 if target_kind == "pool" else 20,
                "resource": 6 if target_kind == "resource" else 20,
            }
            events = []
            for index, kind in enumerate(("parent", "pool", "resource"), 1):
                events.append(
                    cap(
                        prefix + "-cap-" + str(index),
                        prefix + "-" + kind,
                        kind,
                        prefix + "-scope-" + kind,
                        "tokens",
                        1,
                        "provider-window-1",
                        ceilings[kind],
                    )
                )
            events.append(
                freeze(
                    prefix + "-freeze",
                    prefix + "-boundary",
                    TOKENS,
                    200,
                    1,
                    10,
                    required_components=component_ids,
                )
            )
            first_claims = tuple(
                claim(item, "tokens", 1, "provider-window-1", 6)
                for item in component_ids
            )
            events.append(
                reserve(
                    prefix + "-reserve",
                    prefix + "-r-six",
                    prefix + "-boundary",
                    TOKENS,
                    6,
                    first_claims,
                )
            )
            guarded = replay(tuple(events))
            one_claims = tuple(
                claim(item, "tokens", 1, "provider-window-1", 1)
                for item in component_ids
            )
            assert_raises(
                AdmissionError,
                guarded.append,
                reserve(
                    prefix + "-over",
                    prefix + "-r-over",
                    prefix + "-boundary",
                    TOKENS,
                    1,
                    one_claims,
                ),
            )

        omitted = reserve(
            "component-omit",
            "r-component-omit",
            "component",
            TOKENS,
            1,
            (),
        )
        assert_raises(ValidationError, replay, COMPONENT_EVENTS + (omitted,))
        underclaimed = reserve(
            "component-underclaim",
            "r-component-underclaim",
            "component",
            TOKENS,
            6,
            (
                claim("parent-cap", "tokens", 1, "provider-window-1", 5),
                claim("pool-cap", "tokens", 1, "provider-window-1", 5),
                claim("resource-cap", "quota-points", 1, "quota-window-1", 3),
            ),
        )
        assert_raises(
            ValidationError,
            replay,
            COMPONENT_EVENTS[:4] + (underclaimed,),
        )

    def test_unlike_units_never_combine(self):
        state = replay(UNLIKE_EVENTS)
        self.assertEqual(state.observe("token-boundary")["R"], 4)
        self.assertEqual(state.observe("cent-boundary")["R"], 4)
        wrong = reserve("unlike-5", "r-wrong", "token-boundary", CENTS, 1)
        assert_raises(ValidationError, state.append, wrong)

    def test_observation_without_admission(self):
        state = replay((freeze("observe-1", "observe", TOKENS, None, 1, 10),))
        before = state.to_json()
        self.assertIsNone(state.observe("observe")["available"])
        self.assertEqual(state.to_json(), before)

    def test_required_mutations(self):
        self.assertEqual(run_mutation_controls(), MUTATION_NAMES)


TEST_METHOD_TO_CASE = {
    "test_literal_prefix_audit": "literal-prefix-audit",
    "test_positive_reserve_partial_settlement": "positive-reserve-partial-settlement",
    "test_competing_reservations": "competing-reservations",
    "test_unknown_effect_serialize_reopen": "unknown-effect-serialize-reopen",
    "test_duplicate_settlement_charges_once": "duplicate-settlement-charges-once",
    "test_conflicting_duplicate_refuses": "conflicting-duplicate-refuses",
    "test_cumulative_retries_cap": "cumulative-retries-cap",
    "test_provider_reset_daemon_restart": "provider-reset-daemon-restart",
    "test_recovery_cost_not_normal_use": "recovery-cost-not-normal-use",
    "test_verified_additional_normal_work": "verified-additional-normal-work",
    "test_unknown_baseline_window_blocks": "unknown-baseline-window-blocks",
    "test_invalid_integers_fraction_quantum": "invalid-integers-fraction-quantum",
    "test_componentwise_parent_pool_resource": "componentwise-parent-pool-resource",
    "test_unlike_units_never_combine": "unlike-units-never-combine",
    "test_observation_without_admission": "observation-without-admission",
}

DECLARED_SEQUENCES = tuple(case["events"] for case in PREFIX_CASES.values())
PREFIX_COUNT = sum(len(case["events"]) for case in PREFIX_CASES.values())
DECLARED_SEQUENCE_LIMIT = 256
MAX_SEQUENCE_EVENTS = 32


def main():
    if tuple(TEST_METHOD_TO_CASE.values()) != REQUIRED_CASES:
        print("RECOVERY_LEDGER_TEST_FAIL required case inventory changed", file=sys.stderr)
        return 1
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RecoveryLedgerTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        print("RECOVERY_LEDGER_TEST_FAIL", file=sys.stderr)
        return 1
    mutations = run_mutation_controls()
    print(
        "RECOVERY_LEDGER_TEST_PASS "
        + json.dumps(
            {
                "cases": len(REQUIRED_CASES),
                "prefixes": PREFIX_COUNT,
                "mutations": len(mutations),
                "selected_sequences": len(DECLARED_SEQUENCES),
                "sequence_limit": DECLARED_SEQUENCE_LIMIT,
                "max_events_limit": MAX_SEQUENCE_EVENTS,
                "provider_calls": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
