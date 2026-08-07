---
title: Hermes Project Pilot Phase 0 Evidence
type: verification
status: blocked
last-verified: 2026-08-06
related:
  - CONTROL_PLANE.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/architecture.md
  - docs/delegation-design.md
---
# Hermes project pilot Phase 0 evidence

## Verdict

Phase 0 established a reproducible green baseline and red controls for the confirmed audit
defects. No defect was fixed. Production remains paused, no pilot ran, no autonomous execution was
enabled, no product repository changed, and no protected or default branch was pushed or merged.
The Phase 0-only commit was subsequently published on a review branch as draft PR #21 for Lucas's
review; that publication did not change the live control plane.

Phases 1-3 are blocked on review of this evidence and implementation of the red controls. Pilots
and autonomous execution remain forbidden until those phases pass review.

## Immutable starting points

| Item | Evidence |
|---|---|
| Authoring base | `origin/master` at `b1391908c17dc61c65613b0adda85918b486c1cd` |
| Authoring branch | `review/hermes-phase0-controls` in `C:\Users\drfoo\github\recursion-hermes-phase0` |
| Phase 0 commit | `2e98bc57a6a0ff1257f4d23166af36c10619f902` (`Add Hermes pilot Phase 0 controls`) |
| Review publication | draft PR #21 (`https://github.com/NotSkittlz/recursion/pull/21`), `review/hermes-phase0-controls` -> `master` |
| Deployed commit | `/opt/recursion` branch `loop/auto` at `58b912c46b0bbba8f420fdda685e05b958279daa` |
| User-owned checkout | `master` at `20c1fa77042f3aa9f5d8978352792f3b058bc0d1`, ahead 5 / behind 115; dirty state preserved |
| Production plan | copied byte-for-byte into the authoring worktree; SHA-256 `b47295865fcc6be190d47f36e5a6eaa7d2260522baf8b816b30c521edc6873bd` |
| Remote PAUSE | present before and after every live check; SHA-256 `919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db` |

The live PAUSE reason is the 2026-08-06 human-led architecture rebase halt. The only live-tree
anomaly observed was an untracked `.env.bak.1786014440`; it was not opened, moved, or changed.
The pre-existing live flags remain `RECURSION_ALLOW_PUSH=1`, `RECURSION_AUTO_DRAIN=1`,
`RECURSION_AUTO_PLAN=1`, `RECURSION_AUTO_REFLECT=1`, and `RECURSION_ALLOW_AUTOMERGE=0`.
Phase 0 did not edit them; this makes the interruptive PAUSE control a critical prerequisite.

## Next-session handoff

Phase 0 is committed and published for review. Do not begin implementation unless PR #21 has been
reviewed and merged. After approval, fetch the new `origin/master` and create a new clean Phase 1
authoring worktree/branch from that exact commit. Do not reuse or modify the dirty local `master`,
and do not base Phase 1 on an unmerged review branch.

Phase 1 is the only authorized implementation scope for the next session. Reproduce the existing
17/17 green baseline and the intended Phase 1 red results first, then make the Phase 1 controls pass
while keeping the baseline green. Append the exact green-after-red commands, commit OID, results,
and live PAUSE evidence to this document. Do not begin Phase 2, run a pilot, enable autonomous
execution, merge or deploy, or remove `state/PAUSE`.

## Existing baseline

Run `scripts/audit/hermes-pilot-phase0-baseline.sh` from a named Linux branch at the authoring
base. It deliberately excludes the new `*-red.test.sh` controls, asserts that live PAUSE exists
before and after, and records both baseline and deployed commits.

The 16 existing `scripts/tests/*.sh` suites plus `scripts/work.selftest.sh` all passed at
`b1391908`. Two harness constraints are load-bearing:

- do not export `RECURSION_NO_NOTIFY=1` around the whole suite; notification tests install their
  own safe stubs and a suite-level override makes their positive controls vacuous;
- do not run `work.selftest.sh` from detached HEAD; it writes the source branch into its freshness
  fixture, so detached HEAD correctly fails as an unprovable branch.

## Pre-fix red controls

All four commands below returned `1`, as intended. `UNEXPECTED_RED_CONTROL_RESULTS=0` in the
combined disposable-clone run. The live audit was read-only and re-asserted PAUSE afterward.

| Control | Red evidence on pre-change code |
|---|---|
| `scripts/tests/hermes-pilot-phase1-red.test.sh` | 8 failures: mid-run PAUSE reached the gate; worker read controller data, wrote outside, and called publisher; protected/ref-expression spellings were not failed closed |
| `scripts/tests/hermes-pilot-phase2-red.test.sh` | 6 failures: ten replays ran ten actions; crash recovery double-launched; planners collided; three invalid tasks ran; contended lock wrote unlocked; interrupted update exposed a partial file |
| `scripts/tests/hermes-pilot-phase3-red.test.sh` | 6 failures: gateway retained direct execution; authoring text was dropped; instruction closed without action; missing usage passed; authority inputs truncated; singleton decision lost pending work |
| `scripts/audit/hermes-pilot-live-phase1-red.sh` | 2 failures: gateway runs unrestricted as root; 2 of 104 installed dependencies had OSV advisories |

The live dependency findings were:

- `aiohttp==3.14.1`: `GHSA-cq5v-8q36-5273`, `GHSA-mfx4-hv73-q22v`,
  `GHSA-mq44-7p77-q5h7`, `PYSEC-2026-3545`, `PYSEC-2026-3546`, `PYSEC-2026-3547`;
- `cryptography==48.0.1`: `GHSA-g6cj-pr64-35w5`, `GHSA-jwv3-5hgf-82ww`,
  `GHSA-m2h6-j472-rp4c`, `PYSEC-2026-3552`, `PYSEC-2026-3553`, `PYSEC-2026-3554`.

Phase 1 must update them or record a reviewed reachability exception. Phase 0 makes no dependency
or service change.

## Authenticated default-branch protection inventory

The GitHub REST API was queried with the configured authenticated Git credential. Repository
metadata returned `200` for every registered repository and confirmed that the registry's branch
matches GitHub's default branch. The protection endpoint returned `403` for every row with:
`Upgrade to GitHub Pro or make this repository public to enable this feature.`

| Project | Registry status | Default | Protection result |
|---|---|---|---|
| recursion | active | `master` | `403`, feature unavailable |
| golden-stallion | active | `main` | `403`, feature unavailable |
| golden-stallion-extension | active | `main` | `403`, feature unavailable |
| golden-stallion-client | active | `main` | `403`, feature unavailable |
| ai-investment-cockpit | active | `main` | `403`, feature unavailable |
| edgar-morning-brew | active | `main` | `403`, feature unavailable |
| guerra-construction-group | active | `main` | `403`, feature unavailable |
| chiron | active | `main` | `403`, feature unavailable |
| santa-clara-construction | pending | `main` | `403`, feature unavailable |

These branches are not verifiably protected. No repository setting was changed. Publication must
therefore fail closed locally and remain review-branch-only; protection cannot be treated as a
backstop. Enabling a GitHub plan or changing repository visibility is Lucas's decision.

## Notification destination inventory

No token or message content was read. Stable IDs came from `.env` destination fields,
`state/portfolio.tsv`, and gateway session identities.

| Intended destination | Stable ID | Current state |
|---|---|---|
| Lucas direct account | chat/user `8913126684` | configured as `TELEGRAM_CHAT_ID`, but currently only a fallback because the Cockpit chat is configured |
| Head Hermes / home | chat `-1003894008732`, thread `1` | configured as the Cockpit home thread; not yet a separately named durable outbox destination |
| recursion topic | chat `-1003894008732`, thread `3` | registered active |
| golden-stallion topic | chat `-1003894008732`, thread `4` | registered active |
| golden-stallion-extension topic | chat `-1003894008732`, thread `5` | registered active |
| golden-stallion-client topic | chat `-1003894008732`, thread `6` | registered active |
| ai-investment-cockpit topic | chat `-1003894008732`, thread `7` | registered active |
| edgar-morning-brew topic | chat `-1003894008732`, thread `8` | registered active |
| guerra-construction-group topic | chat `-1003894008732`, thread `9` | registered active |
| chiron topic | chat `-1003894008732`, thread `10` | registered active |
| santa-clara-construction topic | none | pending project; cannot activate without a topic and key |

"All accounts" therefore means project topic + Cockpit home/Head Hermes + Lucas direct account,
with an extensible destination list. Current `notify.sh` selects one target; it does not fan one
event out to all three classes. Phase 7 owns that outbox behavior, but the stable IDs above are the
Phase 0 inventory.

## Rollback and backup/restore procedure

This is the reviewed procedure definition, not an authorization to execute it. Until Phase 2
ships atomic state and fail-closed locks, backups require a human-approved quiesced window.

### Backup

1. Assert `state/PAUSE` exists and copy it first into a root-owned `0700` snapshot directory
   outside every git checkout, named with UTC timestamp and deployed commit. Abort if PAUSE is
   absent.
2. Quiesce every writer for the maintenance window: gateway, actuator, planner, intake, cron-driven
   state writers, and workers. Record their prior running state; do not lift PAUSE.
3. Capture a manifest of commit OIDs, branches, worktrees, service unit, cron listing, package
   versions, and file owner/mode. Do not copy deploy keys or tokens into the review bundle.
4. Copy runtime state with metadata: `state/PAUSE`, `.board*`, `.intake-watermark`, instructions,
   assists, decisions, latest pointer, events, escalations, leases/locks metadata, future action and
   delivery queues, GSC runtime baselines, and any checksummed seed manifests/corpora.
5. Snapshot the Hermes SQLite store with SQLite's online backup API, including a subsequent
   `PRAGMA integrity_check`; do not raw-copy a live WAL database.
6. Back up `.env` and gateway credentials separately in the operator's encrypted secret store.
   Record only hashes and presence in the runtime manifest.
7. Hash every snapshot file, fsync snapshot + manifest, then restart awareness-only components.
   Re-assert PAUSE and confirm no worker, gate, publication, or branch-changing process exists.

Git clones are restored from their remotes, not from copied working trees. Gitignored corpora are
restored only through their checksummed seed manifests; absence fails loudly.

### Restore

1. Assert PAUSE and quiesce writers. Restore into a new staging directory, never over live state.
2. Verify manifest hashes, ownership/modes, SQLite integrity, schema versions, event ordering, and
   that every queued/running object has a valid parent. Treat pre-snapshot `running` leases as stale;
   do not relaunch until reconciliation decides.
3. Move the current runtime directory to a timestamped quarantine path, then atomically rename the
   verified staging directory into place. Restore `state/PAUSE` before any service can start.
4. Start awareness-only services and reconcile instructions, actions, processes, worktrees, refs,
   and deliveries. Replays must produce zero duplicate actions or notifications.
5. Run the baseline and all controls. If any required control is red unexpectedly or any pending
   object is unaccounted for, roll back to quarantine and remain paused.
6. Resume execution only after Lucas explicitly approves it. For this project, that cannot happen
   before Phases 1-3 pass review.

### Code/service rollback

Keep PAUSE set. Revert the reviewed change through GitHub review rather than rewriting history;
deploy the resulting known-good commit to `loop/auto` through the normal human workflow. Restore a
previous systemd unit or dependency environment only from its versioned manifest, then run
`daemon-reload`, service hardening controls, baseline tests, and read-only status checks. Never use
a force push or make the dirty local `master` the rollback source.

## Phase 1 authoring evidence

### Publication gate and clean base

GitHub reported PR #21 merged into `master` as
`aadf7b301c9bd3e73b94c6cf5a47e6b5de893146`. Git ancestry checks proved both the distinct Phase 0
controls commit `2e98bc57a6a0ff1257f4d23166af36c10619f902` and the review-branch handoff tip
`22a6255363fbc9ad977b37d9f7183972265befd4` are ancestors of current `origin/master`. The merged
tree contains the Phase 0 controls. GitHub has no separately recorded review submission on the PR;
the merge by Lucas is the available review/approval event.

After fetching, Phase 1 was authored in the clean worktree
`C:\Users\drfoo\github\recursion-hermes-phase1` on `review/hermes-phase1-controls`, based exactly on
merged `origin/master` at `aadf7b3`. The dirty user-owned `master` remained at `20c1fa7` with its
files untouched. Its graph changed from ahead 5 / behind 115 to ahead 5 / behind 118 only because
the requested fetch advanced `origin/master`; it was not used as an authoring base.

### Reproduced starting evidence

The following commands ran in a disposable Linux clone of the merged base before Phase 1 changes:

```text
bash scripts/audit/hermes-pilot-phase0-baseline.sh
# rc=0; BASELINE_SUITES=17; BASELINE_FAILED_SUITES=0

bash scripts/tests/hermes-pilot-phase1-red.test.sh
# rc=1; 8 intended failures

bash scripts/audit/hermes-pilot-live-phase1-red.sh
# rc=1; 2 intended failures

bash scripts/tests/hermes-pilot-phase2-red.test.sh
# rc=1; 6 intended failures

bash scripts/tests/hermes-pilot-phase3-red.test.sh
# rc=1; 6 intended failures
```

### Green after red

The Phase 1 implementation is commit
`0da2e1c8b0bea07849166aae58f80d9ed8191a49` (`Implement Hermes pilot Phase 1 controls`). A fresh
disposable Linux clone at that exact commit produced:

```text
bash scripts/tests/hermes-pilot-phase1-red.test.sh
# rc=0; 8/8 Phase 1 controls passed; hermes-pilot-phase1-red: ALL PASS

bash scripts/audit/hermes-pilot-phase1-green.sh
# rc=0; strict sandbox bounded work as uid 65534; canonical review-only publication passed;
# protected/default ref remained unchanged; aiohttp==3.14.3 OSV_CLEAR;
# cryptography==50.0.0 OSV_CLEAR; artifact and aggregate audits: ALL PASS

bash scripts/audit/hermes-pilot-phase0-baseline.sh
# rc=0; BASELINE_COMMIT=0da2e1c8b0bea07849166aae58f80d9ed8191a49;
# BASELINE_SUITES=17; BASELINE_FAILED_SUITES=0
```

The Phase 1 controls add interruptive PAUSE enforcement, a non-root OS sandbox boundary for model
workers, canonical review-ref-only publication, hardened gateway service artifacts, and clean
dependency pins. The proposed deployment and rollback sequence is documented in
`docs/plans/hermes-project-pilot-phase1-deployment.md`; it was not executed.

### Phase boundary and live PAUSE

The next-phase controls were rerun only to prove scope was not crossed:

```text
bash scripts/tests/hermes-pilot-phase2-red.test.sh
# rc=1; 6 intended failures remain

bash scripts/tests/hermes-pilot-phase3-red.test.sh
# rc=1; 6 intended failures remain
```

The undeployed live audit remains intentionally red:

```text
bash scripts/audit/hermes-pilot-live-phase1-red.sh
# rc=1; 2 intended live failures remain: the installed gateway is still unrestricted and its
# installed aiohttp==3.14.1 / cryptography==48.0.1 environment still reports advisories
```

This is the expected deployment gate, not a claim that live Phase 1 acceptance is complete. The
authoring controls are green, but publication, review, merge, and a separately authorized paused
deployment are required before the two live findings can turn green.

After all checks, `/opt/recursion/state/PAUSE` remained present with SHA-256
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`; `/opt/recursion` remained
`loop/auto` at `58b912c46b0bbba8f420fdda685e05b958279daa`; and no `recursion-worker-*` transient unit was
left behind. No Phase 2 implementation, pilot, autonomous execution, PAUSE removal, deployment,
merge, push, or new PR occurred.
