---
title: Hermes Project Pilot Phase 8 Legacy Journal Compatibility Handoff
type: handoff
status: ready-for-review
last-verified: 2026-08-09
related:
  - CONTROL_PLANE.md
  - docs/architecture.md
  - docs/delegation-design.md
  - docs/autonomous-loops-architecture-and-roadmap.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
  - docs/plans/hermes-project-pilot-phase8-handoff.md
---
# Hermes project pilot Phase 8 legacy journal compatibility handoff

## Scope and state

Lucas authorized a separate reviewable compatibility patch after the PAUSE-held Phase 8 actuator
deployment failed its first deterministic queue transition and automatically rolled back. This
authoring session did not authorize or perform a production deployment, journal migration, PAUSE
removal, notification, configuration/capacity change, pilot, commit, or push.

The patch was authored in clean worktree
`C:\Users\drfoo\github\recursion-hermes-phase8-legacy-journal-compat` on branch
`review/hermes-phase8-legacy-journal-compat`, created from exact current `origin/master`
`b23069ee49519fda5896f43ec888efd71b533167`. The dirty master remains separate and untouched at
`20c1fa77042f3aa9f5d8978352792f3b058bc0d1`.

Production remains unchanged: the actuator unit is absent/inactive, the hardened gateway and cron
are active, workers are zero, and PAUSE remains SHA-256
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`.

## Reproduced defect

The live append-only `state/decisions.jsonl` has SHA-256
`c0a03878fc98df2bb6e6a83496d003dd198e53a8477cb004af6a3909f5b103a0` and six records. The first
five are pre-schema PAUSE no-ops with prose goals; the sixth is current schema-v1 decision
`decision-6f037cbf6fb51a7f641ea9d6`. Its exact pending projection has SHA-256
`883d9f53e2d7263d8ffa733fe61bff959cf1b7e341d4a293d0a9b00f8e0c6684`.

Before the patch, `decision-queue.py import-journal` normalized and validated line 1 before looking
for line 6's existing projection. The non-canonical legacy `goal_id` returned `73`; the actuator's
PAUSE path discarded both output streams and ignored the return. The valid current no-op therefore
remained pending without a diagnostic.

The new Linux regression first ran on unmodified merged code and ended with three expected
failures out of five controls:

```text
FAIL  five reviewed legacy noops are marked without execution and the current noop succeeds once
ok    a new invalid schema-v1 record fails before any marker or projection is written
ok    an unreviewed schema-less noop is not accepted as legacy
FAIL  a changed legacy marker fails closed instead of rewriting migration evidence
FAIL  the supervised actuator reports a journal-import failure while preserving pending state
hermes-pilot-phase8-legacy-journal-red: 3 FAILED
```

No production state was used as a writable fixture.

## Compatibility boundary

The implementation does not loosen schema validation and does not infer legacy status from shape,
age, verb, or prose. It adds one reviewed constant containing the exact ordered SHA-256 values of
the five immutable historical source lines:

```text
d589999830dbae9f212aaefaa95dab3562e89654c799426799f6ce71e3afe081
726c5d82795ee7b42def62b2601f36d0662cb0f5de6f5e4886b11b77f597cc8a
3bd740a2f8242645af25a01dda28f3db636d8e67fb066db1c6c39e793fb6d7ee
160cee2fed8ead1e0154bb3635cb19588a3ad312fb4ae4c5501a3b9da4e7784b
6c14cb6556f79e81bc3b1b4a0a4cb3c14593cb22902e7170410c990372678dda
```

Every accepted line must also have the exact reviewed pre-schema field set and values for `noop`,
empty args/text, high confidence, string cost `0.0`, known project, and `openai-codex` provider.
The lines must form the complete ordered prefix. A subset, reordering, changed byte, merely similar
record, or invalid record after the prefix is refused.

Import is now two-pass under the existing decision-queue lock:

1. Parse, normalize, and validate the entire journal in memory.
2. Classify only the exact five reviewed hashes as non-executable legacy records.
3. Refuse any other invalid record before creating a marker or projection.
4. Verify every existing marker equals the deterministic expected object and reject unexpected,
   malformed, or tampered markers.
5. Atomically create only missing hash-only markers, then import only missing valid decisions.

Markers live inside the existing backup-covered queue at `state/decision-queue/legacy`; they do not
join `QUEUE_DIRS`, cannot be claimed, and contain no source goal/reason prose. Each records source
line/hash, a hash of the legacy goal, deterministic normalized identity, project, classification
`reviewed-pre-schema-noop`, and disposition `not-enqueued`. The raw journal is neither edited nor
rewritten.

`conduct-hermes.sh` now maps an import failure to actuator error `74`, logs a bounded diagnostic,
and preserves pending state. `hermes-actuator.sh` no longer silently accepts a failed PAUSE-safe
queue pass; it records the return while continuing to preserve PAUSE and supervision. No second
scheduler, store, executor, migration command, or manual data path was added.

## Red-to-green and adversarial controls

The final regression has six controls and ends:

```text
ok    five reviewed legacy noops are marked without execution and the current noop succeeds once
ok    a new invalid schema-v1 record fails before any marker or projection is written
ok    an unreviewed schema-less noop is not accepted as legacy
ok    an incomplete reviewed legacy prefix is not accepted
ok    a changed legacy marker fails closed instead of rewriting migration evidence
ok    the supervised actuator reports a journal-import failure while preserving pending state
hermes-pilot-phase8-legacy-journal-red: ALL PASS
```

The success fixture proves:

- all five historical records create markers but zero decisions/actions/events;
- the one current projection moves pending -> succeeded exactly once;
- its sole action has attempts `1` and lifecycle `pending`, `running`, `succeeded`;
- the append-only source journal is byte-identical;
- a second queue pass changes no queue, action, or action-event hash;
- new invalid schema-v1, unreviewed legacy-shaped, partial-prefix, reordered, and marker-tamper
  inputs fail closed before a write; and
- actuator diagnostics are visible without exposing source prose.

Existing Phase 3 restart/drain and actuator tests and the complete Phase 8 plan/window/parallel
tests also passed independently before the full matrix.

## Exact Linux matrix and live-shaped disposable proof

A clean disposable repository was created from exact base `b23069ee...`; the six-file patch was
committed only inside that disposable fixture as OID
`180fe1f935b33a8c12917bd28b18963c39b78f6e`. From `2026-08-10T02:02:56Z` through
`02:22:17Z`, all commands returned zero:

```text
phase0-baseline RC=0
phase1-control RC=0  phase1-audit RC=0
phase2-control RC=0  phase2-audit RC=0
phase3-control RC=0  phase3-audit RC=0
phase4-control RC=0  phase4-audit RC=0
phase5-control RC=0  phase5-audit RC=0
phase6-control RC=0  phase6-audit RC=0
phase7-control RC=0  phase7-audit RC=0
phase8-control RC=0  phase8-audit RC=0
live-phase1 RC=0
FULL_MATRIX=PASS
```

The matrix log SHA-256 was
`c96c0907c1c14db339d9a4f7937017ae24649535df39fe6427f4e66d5ddccda9`; the summary SHA-256 was
`b828fb9a0e9e4121683a91f7f61b03b7336fc17cc1b8840441ee5ba9ebbb7c86`.

One final root-owned disposable `/tmp` fixture copied the exact live journal and pending projection
without changing their production files. Running the patched `conduct-hermes.sh --paused-safe`
there produced:

```text
EXACT_LIVE_SNAPSHOT_FIRST_PASS=PASS markers=5 decisions=1 actions=1 events=3
EXACT_LIVE_SNAPSHOT_REPLAY=PASS no-state-change
PRODUCTION_PAUSE=919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db
PRODUCTION_JOURNAL=c0a03878fc98df2bb6e6a83496d003dd198e53a8477cb004af6a3909f5b103a0
PRODUCTION_PENDING=883d9f53e2d7263d8ffa733fe61bff959cf1b7e341d4a293d0a9b00f8e0c6684
PRODUCTION_MUTATION=false
```

The second pass left every disposable marker/decision/action/event hash unchanged. No delivery or
notification state was created. The fixture and uploaded helper were removed.

## Review surface and next gate

The review surface is exactly:

```text
scripts/decision-queue.py
scripts/conduct-hermes.sh
scripts/hermes-actuator.sh
scripts/tests/hermes-pilot-phase8-legacy-journal-red.py
scripts/tests/hermes-pilot-phase8-red.test.sh
scripts/audit/hermes-pilot-phase8-green.sh
```

Workstation SHA-256 values after the full proof are:

```text
b487eb78b2f04c315a0239338fb97465b8bfea383466a5ec981f1643bd4e3757  scripts/decision-queue.py
9df686a4e6cc8685b7205ab6bb01fc493780b3922e44e071b5f394d6891c1177  scripts/conduct-hermes.sh
491b5a59e0c39337f65568ba61c0cdd68707d80b87a4544ab6aeb4eb7efb05f0  scripts/hermes-actuator.sh
ee33bc7ef492c268fc010479c96c58948bb55b01e87c234ae69d4131f0b56cf8  scripts/tests/hermes-pilot-phase8-legacy-journal-red.py
6b762cbb272f641739ae8f291df2eab7406241a80ea3e4e292fb040da106edc9  scripts/tests/hermes-pilot-phase8-red.test.sh
f7494d64c037693c5c3a701d48c6b23e83fafb5dc9db77770c60dda5d388391a  scripts/audit/hermes-pilot-phase8-green.sh
```

This branch is review-only. It must be reviewed and merged before any fresh deployment can be
proposed. Merge does not authorize deployment. A retry still requires a new full PAUSE-held
preflight, exact merged OID/blob verification, a new runtime snapshot/staging restore, and separate
Lucas authorization. Until then, Phase 8 remains undeployed and every pilot remains blocked.
