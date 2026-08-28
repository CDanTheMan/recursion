---
title: Recursion v2 Phase 0 live preflight
type: audit
status: in-progress
observed: 2026-08-28T19:32:12Z
source_plan: docs/plans/recursion-v2-execution-fabric.md
---
# Recursion v2 Phase 0 live preflight — 2026-08-28

This artifact records the first read-only Phase 0 observation made after Lucas authorized the
Recursion v2 implementation session. It is evidence, not deployment authority. No live file,
service, credential, cron entry, routing flag, branch, or working-tree path was changed.

## PAUSE witness

- Before the audit batch: `919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`
- After the audit batch and the separate dirty-diff read:
  `919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`
- Live path: `/opt/recursion/state/PAUSE`

The local Windows review checkout did not contain `state/PAUSE`; that local fact was not treated
as evidence about the live controller.

## Controller baseline

| Item | Observation |
|---|---|
| Host | `gs-recursion-nbg` |
| Checkout | `/opt/recursion` |
| Branch | `loop/auto` |
| HEAD | `03c8fa4b937f1ba1c1929ea0ca9161befcf0679b` |
| Live `master` | `0edeacbeaab06daf8ea0addffc9f9fa14cc593eb` |
| Live `origin/master` | `928e221bbe90b9ad313be9e66a000643fe4d8f24` |
| `origin/master...loop/auto` | 8 commits left, 129 commits right |
| Worktrees | one: `/opt/recursion` |
| Worker processes | none observed |

`hermes-gateway`, `hermes-actuator`, `recursion-provider-network`, and
`recursion-provider-proxy` were active and enabled. No execution was launched.

The committed live `loop/auto` history was fetched read-only into the local ref
`live/loop-auto` and merged into the WIP integration branch without modifying the live ref. The
merge was mechanically conflict-free. Historical task and goal files deleted in the live runtime
tree are restored byte-for-byte from the reviewed WIP parent because v2 requires historical state
to remain truthful and readable.

## Rollback boundary

The exact pre-phase review head is `9c7a42c4b5098c443bc87ed4b6f7210ebdeff5fc`. The exact live
committed head and dirty-diff digest are recorded above. Because this session made no live
mutation, rollback before a future deployment is to abandon the WIP candidate; the controller is
already at the recorded pre-phase baseline. No force push, reset, or live restore is required.

Any later deployment is a separate human window. Its runbook must take a new snapshot and PAUSE
witness, prove how newer runtime state is preserved, and define its own restore transaction before
changing `/opt/recursion`. This artifact does not authorize that window.

## Dirty live state

The live checkout had exactly two tracked dirty paths:

- `state/briefs/2026-08-28.md`
- `state/escalations.tsv`

The original remote observer reported the binary diff stream SHA-256 as
`42fa68b7d5d0f09be4d1824998dcd4e50984fea5acceca9f869d487bb7e361b9`. Its raw
stream was not retained, and an independent review correctly found that this formatting-dependent
digest could not be reproduced from the abbreviated `index` lines in the excerpt below. It remains
an observation, not the canonical witness.

The canonical reconstruction is
`git diff --full-index --binary live/loop-auto 1514ab3 -- state/briefs/2026-08-28.md
state/escalations.tsv`. Its byte-exact stream is stored as
`docs/audits/recursion-v2-phase0-live-dirty-canonical.patch`, has SHA-256
`3608a7e7e404b296968124df7e316e72b488c956a32c0f4b216c0b26f3fe072a`, and compares
identically to a fresh invocation of that command. Commit `1514ab3` is the local preservation
commit containing the captured live file bytes; `live/loop-auto` is the fetched committed live
baseline. The following block is a human-readable excerpt only.

```diff
diff --git a/state/briefs/2026-08-28.md b/state/briefs/2026-08-28.md
index 7e51edf1..390a0d47 100644
--- a/state/briefs/2026-08-28.md
+++ b/state/briefs/2026-08-28.md
@@ -2,15 +2,13 @@
 > No arms, planning, drain, or reflection ran. Lift with `scripts/resume.sh`.

## Needs a decision today
-- Physics scheduling is blocked: provide the first Fall 2026 course/topic/lecture date, or explicitly defer scheduling. This remains unresolved since 2026-08-12.
+- **Physics scheduling remains blocked:** provide the first Fall 2026 course/topic/lecture date, or explicitly defer scheduling. This is already recorded in `esc-0004` through `esc-0010`; do not create another duplicate.

## Stale
-- Physics gap map was last assessed 2026-08-04; its only recorded gap is still unassessed.
-- The Fall 2026 syllabus map still contains no actual lecture block.
+- **Physics gap map** was last updated 2026-08-04. Its only tracked concept, Lagrangian mechanics, remains not started with no assessment evidence.

## Syllabus lead
-- Unmeasurable: no course, topic, or lecture date is recorded. Pause new scheduled blocks until the first block is supplied or scheduling is explicitly deferred.
+- **Unassessable:** the syllabus table still has no actual lecture block, so weeks ahead/behind and the pause-new-blocks decision cannot be calculated.

## Today’s physics
-- Lagrangian mechanics — first verify the Newtonian-mechanics and calculus-of-variations prerequisites before treating it as ready.
-
+- **Lagrangian mechanics** — begin with the Euler–Lagrange formulation, after confirming the relevant Newtonian-mechanics and calculus-of-variations prerequisites.
diff --git a/state/escalations.tsv b/state/escalations.tsv
index 2da829d1..3fe61a58 100644
--- a/state/escalations.tsv
+++ b/state/escalations.tsv
@@ -1,11 +1,11 @@
 #id	key	status	first_seen	last_seen	count	workstream	pointer	title
-esc-0001	resync-localonly-recursion	open	2026-08-12T09:15:04Z	2026-08-28T15:15:05Z	134	portfolio	/opt/recursion	recursion: 2 local branch(es) hold commits on no remote
-esc-0002	resync-dirty-recursion	open	2026-08-12T09:15:05Z	2026-08-28T15:15:06Z	144	portfolio	/opt/recursion	recursion: uncommitted changes in the working tree
+esc-0001	resync-localonly-recursion	open	2026-08-12T09:15:04Z	2026-08-28T18:15:05Z	135	portfolio	/opt/recursion	recursion: 2 local branch(es) hold commits on no remote
+esc-0002	resync-dirty-recursion	open	2026-08-12T09:15:05Z	2026-08-28T18:15:05Z	145	portfolio	/opt/recursion	recursion: uncommitted changes in the working tree
@@
-esc-0007	fallback-spend:openrouter	open	2026-08-14T03:00:03Z	2026-08-28T15:00:02Z	116	recursion	state/.openrouter-usage.json	⚠ Recursion FALLBACK FIRED: OpenRouter metered spend +$0.0281 since last check (cumulative $37.824751501). The loop dropped off the ChatGPT Pro sub — check quota/gateway logs (journalctl -u hermes-gateway).
+esc-0007	fallback-spend:openrouter	open	2026-08-14T03:00:03Z	2026-08-28T18:00:02Z	117	recursion	state/.openrouter-usage.json	⚠ Recursion FALLBACK FIRED: OpenRouter metered spend +$0.0281 since last check (cumulative $37.824751501). The loop dropped off the ChatGPT Pro sub — check quota/gateway logs (journalctl -u hermes-gateway).
```

The brief edits are advisory/runtime content. The escalation edits are monotonic observation-count
updates. After preservation in this artifact, the exact captured delta was applied to the local
WIP review candidate. The live checkout remained untouched; any later deployment must re-observe
drift and reconcile rather than overwrite newer runtime state.

## Registered repository observations

All observed active project working trees other than Recursion were clean. Observed local heads:

| Project | Local head | Authenticated default-branch head |
|---|---|---|
| `recursion` | `03c8fa4b937f1ba1c1929ea0ca9161befcf0679b` | `928e221bbe90b9ad313be9e66a000643fe4d8f24` |
| `golden-stallion` | `44ca42133e185be6954fde46063bea6f86310fab` | `bee0cf914d7398f951b626841664dbf50ad7c6d0` |
| `golden-stallion-extension` | `df30c746fae34bae8bbe3f2c0837d8593cece7a3` | `0e9fe693c621f35aaa1cf49171943a1c5403f695` |
| `golden-stallion-client` | `19998a79630b2d57c0ed1e99915470b1048ded10` | `7a7462e97bc4efaa26faf2f9614f948145c9c8fb` |
| `ai-investment-cockpit` | `095b88f75ed630b4a6e30358e2db9753c05f3a12` | `1199a75497a281f2ba78d397d0d6600bce4f5f47` |
| `edgar-morning-brew` | `bb90c53756b629f10e2b0112c56b5e6c62694285` | `fcf72a066ebda5e175b8e503069b16c30ad5b702` |
| `guerra-construction-group` | `977bd4e7634b6526e1fd91b716bd35646161cb9d` | `977bd4e7634b6526e1fd91b716bd35646161cb9d` |
| `chiron` | `5b7ae26129c13c33874ccd6d981ce29d9d122364` | `35c836b503db78468316fbd539ec1b521abf8b78` |

`santa-clara-construction` remained pending and absent.

Explicit dispositions for the observations above are:

- `recursion`: preserve live `loop/auto` at `03c8fa4b...` and its two dirty paths; the committed
  history was fetched and merged only into this disposable WIP branch. Do not fast-forward or
  rewrite the live checkout. `928e221b...` is the authenticated default-branch observation, not
  deployment authority; a future deployment window must fetch again and reconcile newer state.
- `golden-stallion`, `golden-stallion-extension`, `ai-investment-cockpit`, and
  `edgar-morning-brew`: preserve each observed local head without reset or deletion. Treat the
  authenticated remote default head in the table as the only eligible basis for a *new* immutable
  assignment after a fresh fetch. The observed local drift is not eligible for worker dispatch.
- `golden-stallion-client`: preserve the observed local head. Treat authenticated `main`
  `7a7462e9...` as the next-assignment basis after a fresh fetch; the old source-bound task was
  closed rather than rebound.
- `guerra-construction-group`: local and authenticated default heads were already identical;
  preserve `977bd4e7...`, with no task or publication authorized by this audit.
- `chiron`: preserve the observed local duplicate and its history untouched. The authenticated
  default head `35c836b5...` is the source observation; cleanup remains forbidden until the Phase 9
  parity, reference, migration, and independent-review gates pass.
- `santa-clara-construction`: no checkout or commit existed to reconcile. Keep it pending; no task
  may infer or manufacture a source ref.

`state/leases` contained no entries. The eight paths under `state/.locks` were zero-byte regular
files used as `flock(2)` lock targets, not lease records. Two short-lived, PID-owned control locks
(`hermes-control.lock` and `decision-queue.lock`) were observed during an awareness cycle and
released before their process details could be sampled. No worker process or unowned lease was
observed. A later sample showed no matching control process and no held `state/.locks` flock. The
transient sample aligned with the configured six-hour `hermes-decide.sh` cadence.

A read-only Linux follow-up at `2026-08-28T21:39:47Z` re-witnessed the same PAUSE hash and live
HEAD, found no lease entries, no worker/lease process, and no held `state/.locks` flock. Root's
crontab schedules `hermes-decide.sh` every six hours. The four dated decision-log entries report
only an exact authenticated Head-Hermes window decision without a model call; the dated cycle log
repeatedly records `PAUSED`, fetch/status-only repository observation, and `skipping
plan/drain/conduct (execution)`. The 21:15 cycle also preserved Git state and skipped execution.
This closes the transient-lock question as awareness-only for the observed Linux interval; it is
not a claim about a future deployment.

The stale GSC source-bound goal/task was closed through the canonical crash-consistent transition
path: the pilot descriptor and v2 goal share transition `transition-e5b33cc2...`; the v2 task is
stale through `transition-04d2903b...`; and both goal transitions have separate durable
`goal-terminal` events. The older unpinned goal/task was closed as superseded through
`transition-9ce1f6b9...` and `transition-7ef28086...`. Projection versions and event sequences were
advanced rather than edited in place. The authenticated current `main` head is
`7a7462e97bc4efaa26faf2f9614f948145c9c8fb`; no state record was silently rebound to it. A future
attempt requires a new task and immutable assignment.

## Remaining Phase 0 gate work

- validate the merged candidate and this rollback procedure independently.

Until those items pass, Phase 0 remains in progress and no live deployment or PAUSE transition is
authorized.
