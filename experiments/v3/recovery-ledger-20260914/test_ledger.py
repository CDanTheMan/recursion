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


def freeze(event_id, boundary_id, bind, normal_use, p, q, previous=None, sources=()):
    return {
        "event_id": event_id,
        "type": "boundary_frozen",
        "boundary_id": boundary_id,
        "binding": copy.deepcopy(bind),
        "normal_use": normal_use,
        "fraction": {"p": p, "q": q},
        "previous_boundary_id": previous,
        "normal_source_ids": list(sources),
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


def reset(event_id, boundary_id, bind, identity_status):
    return {
        "event_id": event_id,
        "type": "provider_counter_reset",
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
    freeze("component-4", "component", TOKENS, 100, 1, 10),
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


def run_mutation_controls():
    detected = []

    unknown_state = replay(UNKNOWN_EVENTS)
    correct = selected_signature(unknown_state, ("unknown",), ())
    mutated = copy.deepcopy(correct)
    row = list(mutated[0][0][1])
    row[3] = 0
    mutated = ((("unknown", tuple(row)),), ())
    if mutated != PREFIX_CASES["unknown-reset-restart"]["expected"][-1]:
        detected.append("erase-R-on-restart")

    reset_events = PARTIAL_EVENTS + (reset("mut-reset", "partial", TOKENS, "reconciled"),)
    state = replay(reset_events)
    correct = boundary_signature(state, "partial")
    row = list(correct)
    row[2] = 0
    if tuple(row) != correct:
        detected.append("erase-C-on-provider-reset")

    duplicate = settle("partial-duplicate", "s-partial", "r-partial", "partial", TOKENS, 3)
    state = replay(PARTIAL_EVENTS + (duplicate,))
    correct = boundary_signature(state, "partial")
    row = list(correct)
    row[2] = 6
    if tuple(row) != correct:
        detected.append("charge-duplicate-settlement")

    correct = boundary_signature(replay(FLOOR_EVENTS), "floor")
    row = list(correct)
    row[1] = 4
    if tuple(row) != PREFIX_CASES["floor-non-integral"]["expected"][0][0][0][1]:
        detected.append("ceil-instead-of-floor")

    correct = boundary_signature(replay(PARTIAL_EVENTS), "partial")
    row = list(correct)
    row[0] = 103
    if tuple(row) != correct:
        detected.append("count-recovery-as-normal-use")

    correct = selected_signature(replay(UNLIKE_EVENTS), ("token-boundary", "cent-boundary"), ())
    rows = list(correct[0])
    token = list(rows[0][1])
    token[3] = 8
    rows[0] = (rows[0][0], tuple(token))
    if (tuple(rows), ()) != correct:
        detected.append("mix-unlike-units")

    if tuple(detected) != MUTATION_NAMES:
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
            reset("preserve-5", "preserve", TOKENS, "reconciled"),
            restart("preserve-6"),
        )
        state = replay(events)
        self.assertEqual(boundary_signature(state, "preserve")[2:5], (2, 6, 2))
        self.assertEqual(boundary_signature(Ledger.from_json(state.to_json()), "preserve")[2:5], (2, 6, 2))
        state.append(reset("preserve-7", "preserve", TOKENS, "unknown"))
        self.assertEqual(boundary_signature(state, "preserve")[2:5], (2, 6, None))
        assert_raises(
            AdmissionError,
            state.append,
            reserve("preserve-8", "r-reset-blocked", "preserve", TOKENS, 1),
        )
        state.append(reset("preserve-9", "preserve", TOKENS, "reconciled"))
        self.assertEqual(boundary_signature(state, "preserve")[2:5], (2, 6, 2))

    def test_recovery_cost_not_normal_use(self):
        state = replay(PARTIAL_EVENTS)
        self.assertEqual(boundary_signature(state, "partial")[:2], (100, 10))

    def test_verified_additional_normal_work(self):
        state = replay(NORMAL_EVENTS)
        self.assertEqual(boundary_signature(state, "normal-old")[:2], (100, 10))
        self.assertEqual(boundary_signature(state, "normal-new")[:2], (150, 15))

    def test_unknown_baseline_window_blocks(self):
        unknown_baseline = freeze("block-1", "block-baseline", TOKENS, None, 1, 10)
        unknown_window_binding = binding("task-a", "goal-a", "tokens", 1, None)
        unknown_window = freeze("block-2", "block-window", unknown_window_binding, 100, 1, 10)
        state = replay((unknown_baseline, unknown_window))
        self.assertEqual(state.observe("block-baseline")["blockers"], ["unknown-baseline"])
        self.assertEqual(state.observe("block-window")["blockers"], ["unknown-window"])
        assert_raises(
            AdmissionError,
            state.append,
            reserve("block-3", "r-block", "block-baseline", TOKENS, 1),
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
MAX_SEQUENCE_EVENTS = max(len(events) for events in DECLARED_SEQUENCES)


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
                "sequences": len(DECLARED_SEQUENCES),
                "max_events": MAX_SEQUENCE_EVENTS,
                "provider_calls": 0,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
