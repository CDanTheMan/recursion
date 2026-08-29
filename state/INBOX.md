# INBOX — questions and escalations requiring a human decision

(reset 2026-08-12 for first production launch on Lucas's instruction; pre-Hermes content archived at /var/backups/recursion/pre-launch-scrape-20260812T075324Z)

## [esc-0004] 2026-08-12 12:15 — Supply the first Fall 2026 physics lecture block so the lead can be scheduled
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: Fall 2026 table contains only the `_fill from actual syllabus once posted_` placeholder; ANCHOR sets Berkeley start at 2026-08-26 and a three-week lead target
**Blocked on:** the course/topic and first lecture date from the actual syllabus
**Context:** lead, target dates, and the pause-new-blocks rule cannot be evaluated without a real lecture block
**Options:** provide the official syllabus; provide only the first course/topic/date; explicitly defer physics scheduling until the syllabus is available

## [esc-0005] 2026-08-12 15:15 — Supply the first Fall 2026 physics lecture block
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: the Fall 2026 table contains only `_fill from actual syllabus once posted_`; ANCHOR sets Berkeley start at 2026-08-26 and a three-week lead target.
**Blocked on:** the course, topic, and first lecture date from the actual syllabus.
**Context:** lead, target dates, and the pause-new-blocks rule cannot be evaluated without a real lecture block.
**Options:** provide the official syllabus; provide only the first course/topic/date; explicitly defer physics scheduling until the syllabus is available.

## [esc-0006] 2026-08-13 09:15 — Supply the first Fall 2026 physics lecture block or defer scheduling
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: the Fall 2026 table contains only `_fill from actual syllabus once posted_`; CURRENT INBOX `esc-0004` and `esc-0005` identify the same unresolved blocker.
**Blocked on:** the course, first topic block, and first lecture date from the actual syllabus.
**Context:** ANCHOR requires a three-week lecture lead; syllabus rules require pausing new blocks if lead falls below one week. Neither can be evaluated without the first block.
**Options:** provide the official syllabus; provide the first course/topic/date only; explicitly defer physics scheduling until the syllabus is available.

## [esc-0008] 2026-08-14 15:15 — Supply the first Fall 2026 physics lecture block or explicitly defer scheduling
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: the Fall 2026 table contains only `_fill from actual syllabus once posted_`; CURRENT INBOX esc-0004 through esc-0006 record the same unresolved blocker.
**Blocked on:** the course, first topic block, and first lecture date from the actual syllabus.
**Context:** ANCHOR requires a three-week lecture lead; syllabus rules require pausing new blocks below one week. Neither can be evaluated without the first block.
**Options:** provide the official syllabus; provide the first course/topic/date only; explicitly defer physics scheduling until the syllabus is available.

## [esc-0009] 2026-08-15 18:15 — Provide the first Fall 2026 physics lecture block or explicitly defer scheduling
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: the Fall 2026 table contains only `_fill from actual syllabus once posted_`; CURRENT INBOX esc-0004, esc-0005, esc-0006, and esc-0008 are duplicate unresolved instances.
**Blocked on:** the course, first topic block, and first lecture date from the actual syllabus.
**Context:** ANCHOR requires a three-week lecture lead; the syllabus rule requires pausing new blocks below one week. Neither can be evaluated without the first block.
**Options:** provide the official syllabus; provide only the first course/topic/date; explicitly defer physics scheduling until the syllabus is available.

## [esc-0010] 2026-08-18 06:15 — Provide the first Fall 2026 physics lecture block or defer scheduling
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice contains only `_fill from actual syllabus once posted_`; CURRENT INBOX esc-0004, esc-0005, esc-0006, esc-0008, and esc-0009 are duplicate unresolved instances.
**Blocked on:** the course, first topic block, and first lecture date from the actual syllabus.
**Context:** ANCHOR requires a three-week lecture lead, and the syllabus rules require pausing new blocks below one week. Neither can be evaluated from the current ledger.
**Options:** provide the official syllabus; provide only the first course/topic/date; explicitly defer physics scheduling until the syllabus is available.

## [esc-0002] 2026-08-29 — May a v2 acceptance gate have side effects?
**Workstream:** recursion-v2 execution fabric
**Pointer:** `scripts/validate-gate.py` (Phase 2, `codex/v2-adapters` @ `33fb08c`);
`scripts/tests/hermes-pilot-phase5-red.test.sh:411` (Phase 5, `codex/v2-cursor-runtime`);
measurement `tmp/integ-p2c` = `8056ace`.
**Blocked on:** a decision on whether an acceptance gate may mutate state, which is not recorded in
`DECISIONS.md`. D-009 governs the GSC native-diff gate and does not speak to this.

**Context.** Phase 2 closed a reviewed blocker by deleting four non-strict relaxations, so direct commands
now run one validator and one grammar in both modes. That closure is correct on its own terms — the same
relaxations were admitting `bash -c true`, `python3 -c true`, `env test -s app/a` and `../outside.sh`.

It also refuses one acceptance command that bare WIP accepted. Phase 5's heavy-contention arm declares:

```
mktask heavy-contention "test -s app/heavy.txt && touch $HEAVY_GATE_MARKER"
```

Measured, each validator run inside its own checkout:

```
bare WIP a84525d   default (non-strict)   rc=0  ACCEPTED
bare WIP a84525d   --strict-direct        rc=2  refused
Phase 2  33fb08c   --legacy-compound      rc=2  refused
Phase 2  33fb08c   --strict-direct        rc=2  refused
```

`touch` was never in the strict grammar; the non-strict relaxation is what admitted it. Consequence at
`tmp/integ-p2c`: `phase5-red` and `phase5-green` each fail one assertion, `contended heavy gate did not fail
closed (rc=0 status=escalated gate=held)`. Serial repeat, n=10: `pass=0 fail=10`. Deterministic, not a race.
Phase 2 is otherwise 10/12 with all three of its own suites green.

**Why this is not mine to choose.** The command is not vacuous — its decisive element is `test -s
app/heavy.txt`, and the `touch` is the harness's probe for whether the gate body executed. So the vacuity
argument that justifies refusing bare `touch` does not reach this compound. Deciding it sets the contract for
what an acceptance gate *is*, which is the central safety mechanism of the fabric. I already made one wrong
unilateral call on this exact surface: I required `test -s app/result.txt && touch C:/phase5-marker` to keep
passing, a writer widened the grammar to obey, and bare `touch` became an admissible gate. I am not
repeating that.

**Options.**
- **A — gates are predicates.** Keep the refusal. Phase 5's fixture stops using the gate as instrumentation
  and observes execution another way. Cleanest contract; requires editing another phase's red fixture.
- **B — constrained mutation.** Re-admit `touch` only as a non-leading element of a compound whose leading
  element is a real test, operand required and confined to declared paths, never absolute. Phase 5's marker
  moves inside the workspace. Preserves both intents; re-opens a side-effect surface.
- **C — leave it.** Phase 2 and Phase 5 cannot both be accepted, and the ordered integration stalls at
  step 2.

**Recommendation: B**, because it satisfies the vacuity argument in full (bare and absolute `touch` stay
refused) without asserting a gate-contract change that nothing in the control plane records. But B still
touches both phases, so it wants a human yes.

**Not blocking other work.** Phases 3, 4, 5, 6/7 and 8 continue; this surfaces only when Phase 2 and Phase 5
integrate together.
