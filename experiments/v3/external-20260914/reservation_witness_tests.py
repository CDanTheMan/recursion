"""Independent witness harness for the v3 shared-reservations finite model.

Runs fixed ordered action paths taken from the supplied profiles in
experiments/v3/shared-reservations/wr_domain.py through the inclusive reducer
(wr_inclusive.step). For the correct model each edge is also stepped through
the independently coded authority/broker split representation
(wr_split.edges, flattened via wr_split.flat) and every dataclass field of
the two resulting states is compared. Literal expected outcomes are asserted
for every edge, so reducer agreement is an additional oracle, never the only
one. The reducers under test are imported, not edited or copied.

Correct-model edges are checked against:
    sum(free) + in_flight + sum(reserved) + sum(consumed) == 10
    sum(reserved) + sum(consumed) <= 10
where in_flight is 1 exactly when the rights design sits in transfer state 1
(durable debit without durable application).

Gate: python3 -B experiments/v3/external-20260914/reservation_witness_tests.py
Prints V3_RESERVATION_WITNESS_PASS only when all tests pass within the
500-transition budget.
"""

import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                 'shared-reservations'),
)

import wr_domain
import wr_inclusive
import wr_split

TOTAL = 10
TRANSITION_BUDGET = 500
_TRANSITIONS = [0]


def conserved(state, design):
    in_flight = 1 if design == 'rights' and state.transfer == 1 else 0
    return (sum(state.free) + in_flight + sum(state.reserved)
            + sum(state.consumed) == TOTAL)


def within_bound(state):
    return sum(state.reserved) + sum(state.consumed) <= TOTAL


class ReservationWitnessTests(unittest.TestCase):
    maxDiff = None

    def witness(self, design, profile_name, path, mutant=None):
        """Execute an ordered (action, expected_outcome) path.

        Every action must be enabled by the profile prerequisite structure.
        For the correct model (mutant is None) the split representation is
        stepped through the same action, the flattened split state must equal
        the inclusive state field for field, and both invariants must hold
        after the edge. Returns the trace of states after each edge.
        """
        profile = wr_domain.PROFILES[profile_name]
        state = wr_domain.initial(design)
        split = wr_split.pack(state)
        trace = []
        for action, expected in path:
            self.assertIn(action, wr_domain.available(state, profile),
                          msg=f'{action} not enabled in {profile_name}')
            outcome, state = wr_inclusive.step(state, action, profile, design,
                                               mutant)
            _TRANSITIONS[0] += 1
            self.assertEqual(expected, outcome,
                             msg=f'{design} {profile_name} {action}')
            if mutant is None:
                self.assertTrue(
                    conserved(state, design),
                    msg=f'conservation broken after {design} {action}: {state}')
                self.assertTrue(
                    within_bound(state),
                    msg=f'admission bound broken after {design} {action}: {state}')
                match = None
                for label, nxt in wr_split.edges(split, profile, design):
                    if label == action + '=' + outcome:
                        match = nxt
                        break
                self.assertIsNotNone(
                    match,
                    msg=f'split reducer produced no edge {action}={outcome}')
                _TRANSITIONS[0] += 1
                flat = wr_split.flat(match)
                for name in wr_domain.NAMES:
                    self.assertEqual(
                        getattr(state, name), getattr(flat, name),
                        msg=f'field {name} after {design} {action}')
                split = match
            self.assertLessEqual(_TRANSITIONS[0], TRANSITION_BUDGET)
            trace.append(state)
        return trace

    def test_stale_read_cannot_admit_twelve(self):
        # trace21 shape: both goals read ten; the serialized current-balance
        # check, not the stale read, governs admission.
        trace = self.witness('central', 'stale-read-race', [
            ('read0', 'ok'), ('read1', 'ok'),
            ('reserve0', 'admitted'), ('reserve1', 'denied')])
        final = trace[-1]
        self.assertEqual((10, 10), final.reads)
        self.assertEqual((4, 0), final.free)
        self.assertEqual((6, 0), final.reserved)
        self.assertEqual(1, final.issued)
        trace = self.witness('rights', 'stale-read-race', [
            ('read0', 'ok'), ('read1', 'ok'),
            ('reserve0', 'denied'), ('reserve1', 'denied')])
        final = trace[-1]
        self.assertEqual((5, 5), final.reads)
        self.assertEqual((5, 5), final.free)
        self.assertEqual((0, 0), final.reserved)

    def test_unknown_survives_restart_quota_wait(self):
        # Ambiguous sent attempt: receipt lost, then quota reset, worker
        # exit/wait, restart and a new incarnation must not resend or release.
        path = [('reserve0', 'admitted'), ('intent0', 'ok'), ('send0', 'sent'),
                ('accept0', 'ok'), ('lose0', 'ok'), ('quota_reset', 'ok'),
                ('exit', 'ok'), ('wait', 'ok'), ('restart', 'ok'),
                ('new_worker', 'ok'), ('compute', 'ok'),
                ('resend0', 'blocked'), ('reserve1', 'denied')]
        trace = self.witness('central', 'local-lifetime',
                             [('transfer_debit', 'not-applicable'),
                              ('transfer_install', 'not-applicable')] + path)
        lost = trace[6]   # after lose0
        self.assertEqual((1, 0), lost.sent)
        self.assertEqual((1, 0), lost.remote)
        self.assertEqual((0, 0), lost.receipt)
        self.assertEqual(1, lost.quarantine)
        self.assertEqual((6, 0), lost.reserved)
        booted = trace[10]  # after restart
        self.assertEqual(1, booted.boot)
        self.assertEqual((6, 0), booted.reserved)
        final = trace[-1]
        self.assertEqual((4, 0), final.free)
        self.assertEqual((6, 0), final.reserved)
        self.assertEqual((0, 0), final.consumed)
        self.assertEqual((0, 0), final.receipt)
        self.assertEqual(1, final.quota_epoch)
        self.assertEqual(1, final.quota_used)
        self.assertEqual(0, final.worker)
        self.assertEqual(1, final.incarnation)
        self.assertEqual((1, 1), final.lifetime)
        trace = self.witness('rights', 'local-lifetime',
                             [('transfer_debit', 'ok'),
                              ('transfer_install', 'ok')] + path)
        final = trace[-1]
        self.assertEqual((0, 4), final.free)
        self.assertEqual((6, 0), final.reserved)
        self.assertEqual(2, final.transfer)
        self.assertEqual((0, 0), final.receipt)

    def test_classification_does_not_settle(self):
        # Classification records a verdict only; a conflict then holds
        # reconciliation. R stays reserved throughout.
        path = [('reserve0', 'admitted'), ('intent0', 'ok'), ('send0', 'sent'),
                ('accept0', 'ok'), ('receive0', 'ok'), ('classify0', 'ok'),
                ('conflict0', 'ok'), ('reconcile0', 'held'),
                ('reserve1', 'denied')]
        trace = self.witness('central', 'classification-hold',
                             [('transfer_debit', 'not-applicable'),
                              ('transfer_install', 'not-applicable')] + path)
        classified = trace[7]  # after classify0
        self.assertEqual((1, 0), classified.classification)
        self.assertEqual((6, 0), classified.reserved)
        self.assertEqual((0, 0), classified.consumed)
        final = trace[-1]
        self.assertEqual((6, 0), final.reserved)
        self.assertEqual((0, 0), final.consumed)
        self.assertEqual(1, final.conflict)
        self.assertEqual(1, final.quarantine)
        self.assertEqual((4, 0), final.free)
        trace = self.witness('rights', 'classification-hold',
                             [('transfer_debit', 'ok'),
                              ('transfer_install', 'ok')] + path)
        final = trace[-1]
        self.assertEqual((6, 0), final.reserved)
        self.assertEqual((0, 0), final.consumed)
        self.assertEqual((0, 4), final.free)

    def test_success_settlement_is_idempotent(self):
        # A trusted success receipt settles R->C exactly once; a repeat
        # reconcile and a matching duplicate request are duplicates.
        path = [('reserve0', 'admitted'), ('intent0', 'ok'), ('send0', 'sent'),
                ('accept0', 'ok'), ('receive0', 'ok'), ('classify0', 'ok'),
                ('reconcile0', 'settled'), ('settle_again0', 'duplicate'),
                ('duplicate0', 'duplicate'), ('reserve1', 'denied')]
        trace = self.witness('central', 'success-consumption',
                             [('transfer_debit', 'not-applicable'),
                              ('transfer_install', 'not-applicable')] + path)
        settled = trace[8]  # after reconcile0
        self.assertEqual((6, 0), settled.consumed)
        self.assertEqual((0, 0), settled.reserved)
        final = trace[-1]
        self.assertEqual((6, 0), final.consumed)
        self.assertEqual((0, 0), final.reserved)
        self.assertEqual((4, 0), final.free)
        trace = self.witness('rights', 'success-consumption',
                             [('transfer_debit', 'ok'),
                              ('transfer_install', 'ok')] + path)
        final = trace[-1]
        self.assertEqual((6, 0), final.consumed)
        self.assertEqual((0, 0), final.reserved)
        self.assertEqual((0, 4), final.free)

    def test_nonexecution_releases_once(self):
        # Terminal nonexecution releases R to free exactly once; afterwards
        # the central pool admits six again while the rights holder cannot.
        path = [('reserve0', 'admitted'), ('intent0', 'ok'), ('send0', 'sent'),
                ('refuse0', 'ok'), ('lose0', 'ok'), ('restart', 'ok'),
                ('query0', 'ok'), ('classify0', 'ok'),
                ('reconcile0', 'settled'), ('settle_again0', 'duplicate'),
                ('duplicate0', 'duplicate')]
        trace = self.witness('central', 'lost-receipt-refusal',
                             [('transfer_debit', 'not-applicable'),
                              ('transfer_install', 'not-applicable')] + path
                             + [('reserve1', 'admitted')])
        released = trace[11]  # after reconcile0
        self.assertEqual((10, 0), released.free)
        self.assertEqual((0, 0), released.reserved)
        self.assertEqual((0, 0), released.consumed)
        again = trace[12]  # settle_again0 released nothing a second time
        self.assertEqual((10, 0), again.free)
        final = trace[-1]
        self.assertEqual((4, 0), final.free)
        self.assertEqual((0, 6), final.reserved)
        trace = self.witness('rights', 'lost-receipt-refusal',
                             [('transfer_debit', 'ok'),
                              ('transfer_install', 'ok')] + path
                             + [('reserve1', 'denied')])
        released = trace[11]
        self.assertEqual((6, 4), released.free)
        final = trace[-1]
        self.assertEqual((6, 4), final.free)
        self.assertEqual((0, 0), final.reserved)

    def test_wrong_owner_and_changed_payload_refuse(self):
        # Every mutated identity probe and the foreign release are refused
        # without touching the durable reservation.
        path = [('reserve0', 'admitted'), ('wrong_owner0', 'owner-refused'),
                ('changed_payload0', 'payload-conflict'),
                ('wrong_goal0', 'identity-conflict'),
                ('changed_amount0', 'identity-conflict'),
                ('changed_attempt0', 'identity-conflict'),
                ('intent0', 'ok'), ('send0', 'sent'), ('accept0', 'ok'),
                ('lose0', 'ok'), ('foreign_release0', 'owner-refused'),
                ('duplicate0', 'duplicate')]
        trace = self.witness('central', 'owner-and-identity',
                             [('transfer_debit', 'not-applicable'),
                              ('transfer_install', 'not-applicable')] + path)
        final = trace[-1]
        self.assertEqual((6, 0), final.reserved)
        self.assertEqual((4, 0), final.free)
        self.assertEqual((1, 0), final.sent)
        self.assertEqual((1, 0), final.remote)
        self.assertEqual(1, final.quarantine)
        self.assertEqual((('pool10', 'goalA', 'opA', 'attemptA', 'payloadA',
                           'ownerA', 6), ()), final.bindings)
        trace = self.witness('rights', 'owner-and-identity',
                             [('transfer_debit', 'ok'),
                              ('transfer_install', 'ok')] + path)
        final = trace[-1]
        self.assertEqual((6, 0), final.reserved)
        self.assertEqual((0, 4), final.free)

    def test_duplicate_transfer_cannot_mint(self):
        # trace22 shape: debit survives restart, install applies once,
        # duplicate install is a stutter, timeout cannot reclaim.
        rights_path = [('capture', 'ok'), ('copy', 'ok'), ('reader_wait', 'ok'),
                       ('transfer_debit', 'ok'), ('restart', 'ok'),
                       ('transfer_install', 'ok'),
                       ('transfer_duplicate', 'duplicate'),
                       ('transfer_timeout', 'held'), ('transfer_ack', 'ok'),
                       ('restore_old', 'stale-rejected'), ('install', 'ok'),
                       ('reserve0', 'admitted'), ('reserve1', 'denied')]
        trace = self.witness('rights', 'transfer-interruption', rights_path)
        debited = trace[3]
        self.assertEqual((5, 4), debited.free)
        self.assertEqual(1, debited.transfer)
        applied = trace[5]
        self.assertEqual((6, 4), applied.free)
        self.assertEqual(2, applied.transfer)
        dup = trace[6]  # duplicate install minted nothing
        self.assertEqual((6, 4), dup.free)
        self.assertEqual(2, dup.transfer)
        final = trace[-1]
        self.assertEqual((0, 4), final.free)
        self.assertEqual((6, 0), final.reserved)
        self.assertEqual(2, final.transfer)
        self.assertTrue(final.ack)
        central_path = [('capture', 'ok'), ('copy', 'ok'), ('reader_wait', 'ok'),
                        ('transfer_debit', 'not-applicable'), ('restart', 'ok'),
                        ('transfer_install', 'not-applicable'),
                        ('transfer_duplicate', 'not-applicable'),
                        ('transfer_timeout', 'not-applicable'),
                        ('transfer_ack', 'unavailable'),
                        ('restore_old', 'no-change'), ('install', 'ok'),
                        ('reserve0', 'admitted'), ('reserve1', 'denied')]
        trace = self.witness('central', 'transfer-interruption', central_path)
        final = trace[-1]
        self.assertEqual((4, 0), final.free)
        self.assertEqual((6, 0), final.reserved)
        self.assertEqual(0, final.transfer)

    def test_stale_snapshot_cannot_restore_rights(self):
        # A copied stale snapshot may be installed as a presentation cursor,
        # but it cannot roll back the durable ledger.
        path = [('transfer_debit', None), ('transfer_install', None),
                ('reserve0', 'admitted'), ('intent0', 'ok'), ('send0', 'sent'),
                ('accept0', 'ok'), ('lose0', 'ok'), ('copy', 'ok'),
                ('reader_wait', 'ok'), ('install', 'ok'),
                ('restore_old', 'stale-rejected'), ('reserve1', 'denied')]
        rights_path = [('capture', 'ok')] + [
            (a, 'ok' if e is None else e) for a, e in path]
        trace = self.witness('rights', 'snapshot-uncertainty', rights_path)
        installed = trace[10]  # install of the stale snapshot
        self.assertEqual(installed.snapshot, installed.installed)
        self.assertEqual((5, 5), installed.installed[1])
        self.assertEqual(0, installed.installed_cursor)
        self.assertNotEqual(installed.snapshot[0], installed.revision)
        self.assertEqual((0, 4), installed.free)      # ledger not rolled back
        self.assertEqual((6, 0), installed.reserved)
        self.assertEqual(2, installed.transfer)
        final = trace[-1]
        self.assertEqual((0, 4), final.free)
        self.assertEqual((6, 0), final.reserved)
        central_path = [('capture', 'ok'),
                        ('transfer_debit', 'not-applicable'),
                        ('transfer_install', 'not-applicable')] + [
            (a, e) for a, e in path[2:]]
        trace = self.witness('central', 'snapshot-uncertainty', central_path)
        installed = trace[10]
        self.assertEqual((10, 0), installed.installed[1])
        self.assertEqual((4, 0), installed.free)
        self.assertEqual((6, 0), installed.reserved)
        final = trace[-1]
        self.assertEqual((4, 0), final.free)
        self.assertEqual((6, 0), final.reserved)

    def test_mutant_controls(self):
        # Each enabled mutant must produce its expected invariant/outcome
        # violation; a surviving mutant is a failure of this test.
        # 1. serialization: stale reads admit twelve units.
        trace = self.witness('central', 'stale-read-race',
                             [('read0', 'ok'), ('read1', 'ok'),
                              ('reserve0', 'admitted'),
                              ('reserve1', 'admitted')],
                             mutant='serialization')
        bad = trace[-1]
        self.assertEqual((6, 6), bad.reserved)
        self.assertEqual((-2, 0), bad.free)
        self.assertFalse(within_bound(bad))
        # 2. classification-release: classify alone releases R, so the later
        # reconcile finds nothing to settle.
        trace = self.witness('central', 'success-consumption',
                             [('transfer_debit', 'not-applicable'),
                              ('transfer_install', 'not-applicable'),
                              ('reserve0', 'admitted'), ('intent0', 'ok'),
                              ('send0', 'sent'), ('accept0', 'ok'),
                              ('receive0', 'ok'), ('classify0', 'ok'),
                              ('reconcile0', 'duplicate')],
                             mutant='classification-release')
        classified = trace[7]
        self.assertEqual((0, 0), classified.reserved)
        self.assertEqual((10, 0), classified.free)
        self.assertEqual((0, 0), classified.consumed)
        # 3. settlement-idempotence: a second settle double-consumes.
        trace = self.witness('central', 'success-consumption',
                             [('transfer_debit', 'not-applicable'),
                              ('transfer_install', 'not-applicable'),
                              ('reserve0', 'admitted'), ('intent0', 'ok'),
                              ('send0', 'sent'), ('accept0', 'ok'),
                              ('receive0', 'ok'), ('classify0', 'ok'),
                              ('reconcile0', 'settled'),
                              ('settle_again0', 'settled')],
                             mutant='settlement-idempotence')
        bad = trace[-1]
        self.assertEqual((12, 0), bad.consumed)
        self.assertFalse(conserved(bad, 'central'))
        # 4. duplicate-credit: a repeated install mints a right.
        trace = self.witness('rights', 'transfer-free',
                             [('transfer_debit', 'ok'),
                              ('transfer_install', 'ok'),
                              ('transfer_duplicate', 'ok')],
                             mutant='duplicate-credit')
        bad = trace[-1]
        self.assertEqual((7, 4), bad.free)
        self.assertFalse(conserved(bad, 'rights'))


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ReservationWitnessTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    ok = result.wasSuccessful() and _TRANSITIONS[0] <= TRANSITION_BUDGET
    if ok:
        print('V3_RESERVATION_WITNESS_PASS')
    sys.exit(0 if ok else 1)
