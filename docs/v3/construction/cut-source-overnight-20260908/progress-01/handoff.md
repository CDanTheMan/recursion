# Conditional progress handoff — 2026-09-09

Parent goal-recursion-v2-execution-fabric; same SC-CUT-SOURCE-01 campaign. Original
activation 2026-09-09T03:40:33Z, discovery cutoff 12:30Z and hard stop 15:30Z
(08:30 Los Angeles) remain fixed across continuations. Astra High Standard remains
unchanged. Root is the sole writer; workers are read-only. Included capacity only,
no metered spend, and no reset has been used. The existing one-reset authorization
requires actual depletion and the durable ledger; no automatic quota-reset restart.

This branch, codex/v3-cut-source-progress-20260909, adds only progress-01 files to
frozen documentation candidate 8f457c546e4d85fada73913efb900f921eaf6b1a. That candidate
is now published as draft PR 112 after two complete gates and two independent exact
reviews. predecessor.json binds its immutable 267-file evidence closure through
completion.json. Preserve that worktree and every earlier frozen worktree.

This study assumes already accepted original immutable records and fixed source
metadata. Only visible record count changes invalidate its local collection check.
It examines logical scheduling work and waiting, not source validity, crashes,
physical time, runtime integration or the deferred Q1–Q6. The original four-event
flow, A6/B6 pool10, attempts 1–2, six obligations and 27 rows remain unchanged.

The first preparation at a8fda63 and exploration at 0fff9ce remain retained. Reviews
identified reporting and provenance gaps; method-review.md records their repairs.
Fresh preparation at 11fd058, run 20260909T090511266800, regenerated the same complete
input bytes and bound the final executable sources and specification. Preparation
used 1.156 seconds and 23,228,416-byte job peak, with zero owned processes after cleanup.
input-provenance.json names its exact receipt; no source-validity result is implied.

Fresh exploration at 82911c2, run 20260909T090633347607, passed in 3.359 seconds with
126,713,856-byte job peak and successful cleanup. Its 234 retained file hashes, all
four graph bytes and every earlier result field were verified. results.json and
evidence.json bind that complete result. Both representations agree across 80,098
states and 80,528 edges with zero frontier. Four input streams yield three distinct
record-count domains; the two N=4 graphs are identical. All quiet continuations
complete and all four accounting controls are detected. See findings.md for
measurements and progress-bounds.md for separately reasoned claims and the manual
22-action example outside H6. No additional enumeration coverage is claimed.

Final acceptance requires two runs on the identical clean candidate:
`python -X utf8 -B experiments/v3/cut-source-overnight/progress-01/pg_check.py --candidate FULL_HASH`
Each runs 18 frozen predecessor checks and 25 regressions, then freshly prepares and
explores with complete input/result/graph equality. Shared owned-job, usage, memory,
artifact, PAUSE, parent and fixed-clock checks remain binding. Two independent
exact-candidate reviews must also approve before normal review-branch publication
and a draft PR against freshly verified master. Lucas handles merging. Actual gate,
review and publication outcomes belong in the candidate's external evidence folder;
this committed checkpoint itself makes no publication-ready claim.

All failures and superseded evidence are retained. The broader campaign remains
incomplete and Q1–Q6 remain deferred after the observed cybersecurity notice; its
cause is unknown. No new notice has been observed during this conservative work.
Do not route interrupted work through another model. Do not change publisher scripts,
config, auth, routing, cron, providers, runtime, deployment or protected history.
