---
title: Hermes Project Pilot Phase 8 Handoff
type: handoff
status: blocked
last-verified: 2026-08-10
related:
  - CONTROL_PLANE.md
  - docs/architecture.md
  - docs/delegation-design.md
  - docs/autonomous-loops-architecture-and-roadmap.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
  - docs/plans/hermes-project-pilot-phase7-handoff.md
---
# Hermes project pilot Phase 8 handoff

## Current state

- The Phase 7 merge gate passed before Phase 8 authoring. Phase 7 implementation
  `b4d3a30317e7d11f8e31b5e2578eb53aaeb5155c` is an ancestor of merged
  `origin/master` at `7aa6e0f44ffd5145d15c38dfad893ed46389308b` (PR #28), and the Phase 7
  handoff/evidence artifacts are present.
- Phase 8 red-control commit: `234d49b46197b7e120ca96b7efdfdc904ba87ec0`.
- Phase 8 implementation commit: `7d0dc10fcb5914f98353be1f73deb15498e71b7c`.
- Merge state: Lucas reviewed and merged Phase 8 through PR #29 as exact merge commit
  `9422b9cc5bf4270b7184b9af6fa31cae8e6a6876`; all four Phase 8 commits are ancestors and the
  review branch was pruned.
- The Phase 1 remediation evidence was subsequently merged through PR #31 as exact current
  `origin/master` `b23069ee49519fda5896f43ec888efd71b533167`; evidence commit
  `71e651ad958fa0e50904e7730e711ed39e6e2d82` and Phase 7 implementation `b4d3a303...` are
  ancestors, and the review branch is pruned.
- Exact Linux proof: 17/17 historical baseline; every Phase 1-7 behavioral control and positive
  audit; all six Phase 8 plan/window/assist controls; the real Linux parallel-capacity control; and
  the Phase 8 positive architecture audit are green at the exact implementation OID.
- The separate Phase 1 compatibility remediation was reviewed and merged through PR #30 as
  `fa0263587479b3c43b0ba6bb61f5b176383f7cec`, then successfully deployed under PAUSE using frozen
  Hermes `498061d8f1dcd855419b30e8729c869596a89ca6`. The two former live Phase 1 deployment findings
  are closed; live Phase 1, dependency/OSV, systemd security, rollback, and independent closure
  gates pass.
- The Phase 8 deployment preflight found production `loop/auto` at
  `73987156f5d22d2f2f50ddc542c978d0c48f88b8`, containing merged `origin/master` `fa026358...` as
  an ancestor. PAUSE remains asserted at SHA-256
  `919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`.
- Lucas authorized one fresh PAUSE-held Phase 8 actuator deployment. The exact reviewed unit
  reached active/running state, but its first deterministic PAUSE-safe queue transition was
  blocked by five legacy pre-schema records in `state/decisions.jsonl`. Automatic rollback
  restored the runtime snapshot, cron, and the sole valid pending decision and removed the unit.
- Phase 8 is therefore still not deployed. PAUSE remains exact; `hermes-gateway` and cron are
  active; the actuator is absent; workers and project processes are zero; model routing remains
  unset; capacity remains zero; and all nine outboxes remain paused and empty. No PAUSE lift,
  observed pilot, human-visible notification, product-repository mutation, or soak occurred.
- The evidence-correction branch was reviewed, merged through PR #34 as `52f6ad37250d7b7bc798d86c04768aef8cc09c07`,
  and pruned. The separate PAUSE/resync correction is now reviewable as red commit `2688671...`,
  implementation commit `1a16d81...`, and historical-control harness commit `5bbfad5...`. Exact
  Linux proof is green; none of these commits is deployed.

The exact commands, OIDs, results, live snapshot, GitHub inventory, rollback gates, and raw-log
hashes are appended to `docs/plans/hermes-project-pilot-phase0-evidence.md`.

## Why the previous Chiron plan is not executable

The production Chiron registry still contains the pre-Phase-8 goal
`goal-chiron-learning-shell` and legacy tasks `chiron-001` through `chiron-003`. That state predates
the Hermes plan-synthesis contract and is not a valid autonomous Phase 8 plan. Phase 8 therefore
does not reopen, reinterpret, or silently upgrade it.

A Chiron pilot can begin only from a fresh Lucas instruction that produces a new, schema-complete
plan with new plan, goal, and task identities. The plan must contain:

- a bounded Phase 6 budget and complete Phase 5 worker/verifier task envelopes;
- an acyclic dependency graph, exact allowed paths, and explicit non-goals;
- non-vacuous task and terminal gates;
- review-branch-only publication, with credentials, merge, and deployment excluded; and
- one deterministic stop condition and bounded prose fields.

The proposal is stored at `state/plans/<project>/<plan>.json`. Head Hermes cannot materialize its
goal or tasks until a separate authenticated Lucas instruction names the exact plan ID and SHA-256
digest. Replaying the approval is idempotent. A collision, stale digest, malformed plan, reused
identity, missing field, cycle, vacuous gate, or partial materialization fails closed.

## Implemented Phase 8 path

Phase 8 uses the existing hierarchy and adds no parallel scheduler, executor, publisher, store,
sender, or worker launcher:

```text
Lucas instruction
  -> authenticated intake record
  -> logical project pilot or Head Hermes planning invocation
  -> schema-validated decision
  -> existing durable decision queue
  -> existing conduct-hermes.sh sole actuator
  -> fresh immutable plan proposal
  -> separate Lucas exact-digest approval
  -> Phase 6 goal + Phase 5 task DAG materialization
  -> separate Lucas exact-goal bounded window authorization
  -> scheduler/actuator admission recheck
  -> Phase 5 bounded worker + independent verifier
  -> Phase 6 reconciliation and review-branch publication
  -> Phase 7 outbox -> existing notify.sh -> exact delivery acknowledgement
  -> deterministic terminal closure
```

The implementation provides:

- event-invoked logical GPT project pilots with a project-scoped live brief; `RECURSION_PILOT_MODEL`
  is required and fails closed when no human-owned model alias is configured;
- Head-Hermes-only plan approval, window approval/closure, and assist-answer routing;
- durable pilot windows that are armed while PAUSE is present, activate only on the first unpaused
  scheduler observation, admit exactly one named goal for a bounded duration, and are rechecked at
  scheduler and final worker/action boundaries;
- automatic closure of every open pilot window when PAUSE is observed, so a later resume cannot
  replay stale authority;
- compare-and-swap assist resumption of the same blocked goal and task exactly once, with failed
  actuator actions reopening rather than losing their originating instruction;
- direct pilot notification suppression so Phase 7 remains the only human-visible outbox path;
- global worker capacity through `RECURSION_PILOT_GLOBAL_CONCURRENCY` plus one active worker per
  project, implemented as filtered claims in the existing decision queue and sole actuator;
- PAUSE-safe draining only for inert plan/approval/window/assist state transitions, never worker,
  gate, publication, or delivery work; and
- backup coverage for plans, windows, decisions, actions, goals, tasks, assists, runs, events,
  reports, and delivery state.

The checked-in Chiron and golden-stallion-client pilot records gain only
`"window_required": true`. Their production concurrency remains zero. No model alias or global
concurrency value was configured.

## Red-to-green and exact-commit proof

On untouched merged base `7aa6e0f`, the Phase 8 falsifier overlay reported `0/6 controls passed`.
The red suite was preserved in its own commit before implementation. It covers fresh plan shape,
atomic rejection, exact-digest approval, exact-goal bounded admission, PAUSE revocation, and
same-task assist resumption.

At exact implementation OID `7d0dc10`, those six controls pass. The independent Linux parallel
test also proves two projects overlap when global capacity is two while a second task from either
project remains blocked by per-project capacity one. The complete 17-command Linux matrix ended:

```text
MATRIX_TOTAL=17 MATRIX_FAILED=0
```

Every individual command log ended `RC=0`; `matrix2.err` was empty. The disposable Linux bundle and
archive fixtures were removed after the logs were copied and hashed locally. No test used the live
production tree, transport, credentials, project worktrees, or product repositories.

## Read-only production preflight

The final snapshot at `2026-08-08T17:18:24Z` found:

| Gate | Observed state |
|---|---|
| deployed checkout | `loop/auto` at `87189cd6e43ecc3d91f78881b82fb2186c7b2ebe`; Phase 7 merge and implementation are ancestors |
| tracked production changes after Phase 7 merge | awareness-only board/brief/event/inbox/escalation files |
| untracked production file | `.env.bak.1786014440`; pre-existing/user-owned, not read or changed |
| PAUSE | present, `root:root`, mode `0644`, 189 bytes, SHA-256 `919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db` before and after |
| services | `hermes-gateway=active`; hardened `recursion-hermes-gateway=inactive`; supervisor timer/service inactive |
| workers | zero `recursion-worker-*` units; zero active project-worktree processes |
| delivery state | zero notification events and zero deliveries for all nine registered projects |
| pending execution | no decision/action/run/lease directories and no pending/running decision or action files |
| pilot capacity | Chiron and GSC `concurrency_limit=0`, `max_inflight_workers=0`, publication false |
| runtime routing | `RECURSION_PILOT_MODEL`, `RECURSION_DECIDE_MODEL`, and `RECURSION_PILOT_GLOBAL_CONCURRENCY` unset |
| live Phase 1 audit | return `1` with exactly the two known deployment gates: unrestricted/root gateway and advisories in `aiohttp==3.14.1` plus `cryptography==48.0.1` |
| branch protection | authenticated protection endpoint returned HTTP 403 for every registered repository; none is verifiably protected |
| backup/restore | exact fixture backup/restore and crash recovery green; production script present and PAUSE/lock-gated; no production snapshot/restore drill yet authorized or demonstrated |

The deployed OID differs from the Phase 7 handoff's earlier snapshot because the PAUSE-safe
awareness cadence created board/morning commits after merging `origin/master`. Phase 8 did not
create them. The production `origin` cannot currently authenticate with its default recursion key;
that observation was read-only and was not repaired or bypassed.

The two live Phase 1 findings, unverified default-branch protection, absent production
backup/restore drill, unset pilot model alias, zero configured capacity, and unpublished/unmerged
Phase 8 implementation are deployment and pilot gates, not waivers.

## Santa Clara repository evidence

GitHub reports `NotSkittlz/santa-clara-construction` as a private, unarchived repository with
default branch `main`, size zero, and this account holding admin/push access. Its deploy-key endpoint
contains one verified writable key titled `gs-recursion`, created `2026-08-06T08:00:05Z`.

On `gs-recursion`, `/root/.ssh/santa-clara-construction_deploy` is readable, has ED25519 fingerprint
`SHA256:AioH/xSd+WQNtGNqvSjKLJQwbWf74Dgo5lNOFqyp4lk`, and authenticates to GitHub specifically as
`NotSkittlz/santa-clara-construction`. No key bytes were printed. The remote is empty, and the
project has no topic, goal, or actionable charter, so it correctly remains pending with concurrency
zero. Phase 8 did not clone or activate it.

## Rollback gates for future authorized actions

Every item below is a runbook, not current authorization. Before each action, recapture the exact
deployed OID, PAUSE hash, service state, queue/outbox counts, and a manifest-hashed runtime snapshot
outside the checkout. If the deployed OID moves from the value above, that newly observed OID
becomes the rollback OID only after the same read-only checks pass.

1. **Phase 8 deployment.** Keep PAUSE asserted; quiesce writers; take and verify the runtime
   snapshot; deploy only Lucas-reviewed merged code. On any mismatch, keep/reassert PAUSE, stop the
   supervisor and all worker units, restore the pre-deploy snapshot into staging and verify its
   manifest, then deploy a reviewed inverse commit returning the code to the captured pre-deploy
   OID/tree. Never reset, force-push, or use the dirty local master.
2. **Chiron success window.** PAUSE is removed only after the new plan digest and exact goal/window
   instruction are recorded. Rollback is to restore the same 189-byte PAUSE file and verify its
   SHA-256, observe automatic window closure, terminate/verify zero worker units, leave any review
   branch unmerged, and reconcile the goal to a deterministic stopped state. Restore the pre-window
   runtime snapshot if any chain object is missing or duplicated.
3. **Chiron assist window.** Use a distinct exact-goal window. Rollback is identical, plus prove the
   assist and instruction remain durably correlated and the task has not resumed more than once.
   Never fabricate an answer or create a replacement task.
4. **GSC offline window.** Capture the product HEAD plus hashes of the conformance/native-diff gate,
   tests, fixtures, oracle, baseline, and corpus manifest first. On any hash change or live-game
   dependency, reassert PAUSE, close the window, terminate the worker, leave the review branch
   unmerged, restore runtime state if required, and reject the result. Do not rewrite a baseline to
   make the task pass.
5. **Parallel window.** Authorize exactly two named goals and the reviewed global/per-project
   capacity values for that window only. On overlap, isolation, reporting, or capacity mismatch,
   reassert PAUSE, close both windows, terminate all worker units, verify no queued work or sends,
   and restore the pre-window snapshot before any retry.
6. **Soak fault windows.** Record each gateway restart, host reboot, PAUSE interruption, and
   notification-failure injection as a separately observed sub-window. Each sub-window rolls back
   to PAUSE plus the captured service/configuration state; delivery retry uses only the Phase 7
   outbox and exact transport evidence. Any lost/duplicate action, event, report, or delivery ends
   the soak and prevents promotion.

After every future window: PAUSE must be present with the expected hash, all pilot windows closed,
worker/worktree process counts zero, no unintended sends, and the exact
instruction/plan/goal/task/run/commit/gate/verifier/review/report/delivery chain complete. Partial
evidence is a no-go for the next window.

## Authorization boundary and next action

Lucas approved the Phase 8 implementation plan and replacement of the old Chiron plan shape,
reviewed and merged the implementation and evidence branches, and separately authorized one fresh
PAUSE-held actuator deployment. That production authorization did not include a retry, data
migration, compatibility repair, configuration/capacity change, PAUSE removal, human-visible
notification, or pilot window. The failed deployment was rolled back and was not retried.

The next admissible action is a separate reviewable Phase 8 compatibility patch for legacy
decision-journal import. It must preserve the append-only source records, fail closed for new
invalid decisions, deterministically handle already-existing legacy no-op records, surface import
failure in actuator evidence, and include a live-journal-shaped regression proving the current
valid PAUSE-safe no-op executes exactly once. Only after that patch is reviewed, merged, and
pruned may a fresh preflight and separately authorized deployment retry be proposed. The first
Chiron window still additionally requires deployed Phase 8 code, a configured human-owned pilot
model alias and bounded capacity, a fresh Lucas goal instruction, exact plan-digest approval, and
exact window authorization.

## Post-merge hardening follow-up

Lucas subsequently reported the Phase 8 branch merged and pruned. A fresh fetch verified PR #29's
merge commit `9422b9cc5bf4270b7184b9af6fa31cae8e6a6876` at `origin/master`, all four Phase 8 commits as
ancestors, the remote review branch absent, and every Phase 8 handoff/evidence artifact present.

Under Lucas's separate, narrow authorization, the production backup/restore gate was then
demonstrated while PAUSE remained asserted. The root-owned mode-`0700` snapshot and evidence are
retained at
`/var/backups/recursion/hermes-pre-phase8-20260808T224858Z-5a8b2f7464cb`; exact restore occurred
only in `/var/tmp/recursion-restore-drill-20260808T224858Z-5a8b2f7464cb`, all manifest and recovery
checks passed, and that disposable staging path was removed. `hermes-gateway` alone was stopped for
the snapshot and restarted active. No deploy, configuration change, PAUSE removal, notification,
worker, or product-repository mutation occurred.

The final PAUSE SHA-256 remained
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`; production remained
`loop/auto` at `5a8b2f7464cb5f87bc09ea2e611cfa1453ca1c26`; workers were zero; and all nine outboxes were paused
with zero events and deliveries. The live Phase 1 audit still has exactly the same two deployment
gates. Full commands, negative observations, results, rollback evidence, and retained-evidence
hashes are appended to `docs/plans/hermes-project-pilot-phase0-evidence.md`.

The backup/restore gate is therefore closed. Remaining prerequisites are: activate personal
GitHub Pro and prove default-branch protection for the private repositories, remediate the two
Phase 1 live findings through reviewed deployment, deploy the exact merged Phase 8 code under
PAUSE, configure approved model/capacity values, then obtain a separate authorization for each
ordered pilot window. The authorized personal GitHub Pro attempt was blocked before any billing
mutation because this session had no signed-in controllable browser; no organization budget or
billing setting was changed.

### Branch-protection follow-up

Lucas subsequently activated personal GitHub Pro and explicitly authorized protection for every
initialized personal repository. Classic rules now protect `recursion/master` plus the `main`
branches of `golden-stallion`, `golden-stallion-extension`, `golden-stallion-client`,
`ai-investment-cockpit`, `edgar-morning-brew`, `guerra-construction-group`, and `chiron`.

All eight persisted rules were re-opened and field-audited: pull requests required; approval count
not required to avoid a one-user deadlock; conversations resolved; administrators unable to
bypass; force pushes and deletions disabled; status, signature, deployment, linear-history, and
lock requirements inactive. The empty Santa Clara repository remains deferred until its first
`main` branch. No organization budget or billing setting was changed.

The initialized-project branch-protection gate is closed. Remaining pre-deployment gates are the
two unchanged live Phase 1 findings. After those are remediated through a reviewed, PAUSE-held
deployment action, the exact merged Phase 8 code can be proposed for its own PAUSE-held deployment;
model/capacity configuration and every pilot window still require their applicable separate
authorization.

### Phase 1 remediation blocker

Lucas separately authorized the Phase 1 production remediation. The complete PAUSE-held preflight
passed the 17/17 baseline, every Phase 1-7 control suite, and every Phase 1-7 positive audit. The
transaction then failed closed before stopping or changing the service: the reviewed
`cryptography==50.0.0` requirement is OSV-clear but conflicts with Hermes Agent 0.20.0's exact
`cryptography==48.0.1` distribution metadata, so mandatory `uv pip check` returned one
incompatibility. The installed and existing upstream source refs retain that exact pin, while the
latest published Hermes Agent is older and pins an earlier vulnerable version.

Production therefore remains unchanged: the gateway is active under its original root unit and
venv, both Phase 1 findings remain, no service identities or state directories were created, all
pilot supervisors and workers are inactive, no notification was sent, and PAUSE remains
byte-identical at
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`. Exact logs, staged failure,
rollback material, and a file manifest are retained in the root-owned mode-`0700` bundle
`/var/backups/recursion/phase1-remediation-20260809T010739Z-7d682044`.

Do not deploy Phase 8 or retry by overriding package metadata, ignoring `pip check`, or using
`--no-deps`. The next gate is a reviewed Hermes Agent artifact that declares and tests support for
`cryptography==50.0.0`; after that artifact exists, rerun the same staged compatibility/import/OSV
checks and the transactional identity migration. Pilot authorization remains out of scope.

### Phase 1 compatibility patch ready for review

Lucas authorized a separate Hermes Agent compatibility fork. The personal fork now exists at
`NotSkittlz/hermes-agent`; clean local branch `review/phase1-cryptography50` is based directly on
the deployed Hermes source OID `36cb5ae5530a75def7df3195e49b7a4aa2add482`, which was verified
as an ancestor of upstream `main` `b79e83827d1e275f3b5f91594e9f7136d7293e5a`.

The local, unpushed review patch updates cryptography to `50.0.0`, every declared and lazy aiohttp
pin to `3.14.3`, and the complete lock to eliminate the additional h2 advisory with `h2==4.4.1`.
The 249-package lock and 126-package production-shaped environment are OSV-clear; `uv lock
--check`, `uv pip check`, installed metadata, gateway/provider imports, RSA/AES round trips, and the
canonical 144-test targeted suite all pass. The universal all-extras graph resolves; a literal
Windows all-extras install remains platform-blocked at Matrix's Unix-only `python-olm` source
build. A separate full-suite attempt timed out at 1,804 seconds without a summary and is not
claimed as green; all spawned local test processes were terminated and verified absent.

The exact commands, resolved transitions, negative evidence, cleanup, and audit results are in the
Phase 0 evidence document. No production or PAUSE action occurred. The next admissible step is
Lucas review/publication of the compatibility source patch; production retry still requires a new
PAUSE-held preflight and separate authorization. Do not deploy Phase 8 or start a pilot window.

### Authorized compatibility deployment: new sandbox gate

Lucas authorized publication and testing of the Hermes compatibility patch. Branch
`review/phase1-cryptography50` is published at exact OID
`498061d8f1dcd855419b30e8729c869596a89ca6`; it was not merged or pruned. Three PAUSE-held attempts
were fail-closed and are retained at:

- `/var/backups/recursion/phase1-remediation-20260809T052659Z-498061d8` — metadata-verifier defect,
  before service mutation;
- `/var/backups/recursion/phase1-remediation-20260809T060745Z-498061d8` — missing
  `/etc/sysusers.d` parent after gateway stop, followed by successful automatic and independent
  rollback; and
- `/var/backups/recursion/phase1-remediation-20260809T141605Z-498061d8` — exact reviewed artifact
  reached hardened live readiness and closed both Phase 1 findings, but the Phase 1 positive audit
  exposed a new sandbox-executable permission blocker and triggered rollback.

The final attempt had a third fresh `17/17` baseline plus every Phase 1-7 control and positive audit
green before mutation. Its staged environment passed all 104 dependency checks, exact source and
metadata verification, imports, RS256, and complete OSV. While live under the reviewed unit, the
gateway ran as `hermes-gateway`, the live Phase 1 audit was `ALL PASS`, systemd exposure was
`3.6 OK`, the post-switch baseline was 17/17, and the Phase 1 red/artifact controls passed. The
subsequent positive audit failed with:

```text
env: '/workspace/.recursion-sandbox/claude': Permission denied
```

The reviewed unit and transaction use `UMask=0077`; the existing sandbox helper creates the copied
non-`/usr` executable directory after its worktree ownership handoff without explicitly granting
the dedicated runner traversal. This exact hardened-umask path now requires a separate reviewed
Recursion patch and red control. No production chmod, manual worker invocation, weakened test, or
retry was used.

Rollback and independent verification passed. Production is again active on the original root
gateway/unit, original Hermes OID `36cb5ae5530a75def7df3195e49b7a4aa2add482`, `aiohttp==3.14.1`,
and `cryptography==48.0.1`; the original two live findings therefore reproduce exactly. Final
production awareness OID is `6ce55f71a9d5cbef41510379b4f755b5290d3f90`; PAUSE remains exact at
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`; active agents and workers are
zero; all execution units are inactive; and all nine outboxes are paused with zero events. The
created service identities and mode-`0700` state directories remain inert for forensics; reviewed
sysusers/tmpfiles files were rolled back.

Phase 1 remediation, Phase 8 deployment, model/capacity configuration, PAUSE removal,
notifications, and every pilot window remain blocked. Full exact commands, results, rollback
proof, bundle contents, and manifest evidence are appended to the Phase 0 evidence document.

### Hardened-umask sandbox compatibility patch ready for review

Lucas authorized the separate Recursion compatibility change. A new exact regression first
reproduced the copied-executable failure under inherited `umask 0077` as the only Phase 1 control
failure. The fix keeps the copied non-`/usr` executable root-owned while granting only the
`recursion-runner` group access: directory mode `0710`, executable mode `0550`. The existing cleanup,
OS boundary, allowed-path gate, systemd properties, network policy, and publisher controls remain
unchanged.

Focused Linux proof then passed the Phase 1 control and positive audit, completing bounded work as
dedicated UID `981`. The full process-wide-`0077` matrix passed baseline 17/17 plus every Phase 1-7
control and every Phase 1-7 positive audit, ending `FULL_UMASK_MATRIX=ALL_PASS` with zero residual
workers. One preliminary detached-HEAD run was correctly refused by the baseline before suite
execution; that negative fixture result is preserved, and the unchanged named-branch rerun is the
claimed evidence.

The exact three implementation/control file hashes, patch, commands, logs, final production state,
and manifest are retained at root-owned mode-`0700`
`/var/backups/recursion/phase1-umask-compat-20260809T174059Z-9422b9cc`. The disposable test clone was
removed after the manifest passed. Final production remains unchanged on awareness OID
`ddff98258b39f6d8d5f4811ea2ff7ee47952a017`, original Hermes OID
`36cb5ae5530a75def7df3195e49b7a4aa2add482`, original root gateway PID `2542748`, and exact PAUSE
SHA-256 `919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`; workers are zero,
execution units are inactive, and all nine outboxes are paused with zero events.

The five-file Recursion change is staged only on `review/hermes-post-phase8-hardening`. It is not
committed, pushed, merged, or deployed. The next action is Lucas review/publication of this patch.
Only after it is merged into `origin/master` may a new full PAUSE-held preflight and separately
authorized Phase 1 deployment be proposed. Phase 8 deployment and every pilot window remain
blocked.

### Merged remediation deployment failed closed and rolled back

Lucas subsequently merged PR #30 as exact commit
`fa0263587479b3c43b0ba6bb61f5b176383f7cec` and explicitly authorized one fresh PAUSE-held,
gateway-only Phase 1 remediation window with frozen Hermes
`498061d8f1dcd855419b30e8729c869596a89ca6`. Fresh workstation fetch, production OID/ancestry,
artifact hashes, PR merge metadata, and `recursion/master` protection were re-verified.

The fresh preflight passed baseline 17/17, all Phase 1-7 controls, and all Phase 1-7 positive audits
while reproducing exactly the two known live Phase 1 findings. Immediate state capture and the exact
rollback were retained before `FINAL_PREDEPLOY_GATE=PASS`.

The staged frozen-Hermes environment passed exact metadata/import/RS256 verification, `uv pip
check`, and the complete 104-package OSV audit. During the authorized maintenance window, only
`hermes-gateway` was stopped. Migration then failed closed before the venv or unit switch because
plain `rsync --delete` preserved pre-existing excluded destination `bin/` and `logs/`; the explicit
forbidden-path assertion rejected them.

Automatic rollback and independent verification both passed. Final production is again the old
active root gateway with Hermes `36cb5ae...`, `aiohttp==3.14.1`, `cryptography==48.0.1`, and the old
unit hash. PAUSE remains exact at
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`; workers and project
processes are zero; all execution units are inactive; all nine outboxes are paused and empty; no
notification, pilot, flag, capacity, product-repository, or Phase 8 deployment action occurred.

The root-owned evidence bundle is
`/var/backups/recursion/phase1-remediation-20260809T225227Z-498061d8`; its manifest verifies and has
SHA-256 `9d68d0d735a9e6adc661f510c70c6a7053617e3f06770ffe5b93c3ca5585a93a`. A read-only dry run proved
the prospective correction: add `--delete-excluded` so excluded source paths are also removed from
the migrated destination. The syntax-checked candidate has SHA-256
`4df3299a546802ea15f0080fdc6dd33a108876c20d73e50e921bef03ef38ecaf` and was not launched.

Phase 1 remediation therefore remains open, and Phase 8 deployment/pilots remain blocked. The next
admissible action is another complete PAUSE-held preflight followed by a new explicit authorization
for that gateway-maintenance window. Full commands, negative evidence, rollback proof, and final
state are appended to the Phase 0 evidence document.

### Corrected Phase 1 deployment succeeded under PAUSE

Lucas authorized a new full preflight and corrected gateway-only deployment using merged Recursion
`fa0263587479b3c43b0ba6bb61f5b176383f7cec`, frozen Hermes
`498061d8f1dcd855419b30e8729c869596a89ca6`, and the reviewed `rsync --delete-excluded`
correction. The boundary prohibited PAUSE removal, notification, configuration/capacity changes,
and pilots.

The new root-owned bundle is
`/var/backups/recursion/phase1-remediation-20260809T233144Z-498061d8`. Fresh authenticated OID, PR,
artifact, protection-rule, backup, configuration, destination, and rollback gates all passed. The
fresh preflight passed baseline 17/17 and all Phase 1-7 controls/audits while reproducing the two
old live deployment findings.

The corrected transaction passed its staged 104-package compatibility/OSV/import/RS256 gates,
stopped only `hermes-gateway`, migrated state without inherited root-runtime paths, switched the
venv and reviewed unit, and reached bounded non-root readiness. Post-deployment live Phase 1,
baseline 17/17, and every Phase 1-7 control and positive audit ended `ALL PASS`. Independent closure
also passed exact source/dependency metadata, configuration hashes, service properties, active
agent/worker counts, outbox inertness, live Phase 1, and systemd security.

Final production runs exact Hermes `498061d8...` as `hermes-gateway:hermes-gateway` with `UMask=0077`,
`NoNewPrivileges=yes`, `PrivateTmp=yes`, `PrivateDevices=yes`, `ProtectSystem=strict`, and
`ProtectHome=yes`; systemd exposure is `3.6 OK`. `aiohttp==3.14.3` and
`cryptography==50.0.0` are OSV-clear. The retained old venv is
`/usr/local/lib/hermes-agent/venv.pre-phase1-498061d8f1dc` for exact rollback.

Final PAUSE SHA-256 is
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`; active agents and workers
are zero; execution/supervisor units are inactive; all nine outboxes are paused and empty; project
and runtime configuration hashes are unchanged; and no notification or pilot occurred. The final
evidence manifest verifies and has SHA-256
`bea07eb20a4ed1c5e2214592690eb1323f70201e1e51dfe11064cfacfec5eeba`.

Two evidence-only negative observations are retained in the Phase 0 evidence: an initial closure
assertion did not distinguish clean pre-start migration state from service-owned runtime paths, and
the transaction's initial manifest preceded the last tee output. Neither was accepted as positive
evidence; the corrected independent verifier and post-log reseal both passed.

The two live Phase 1 deployment gates are now closed. This does not deploy Phase 8, configure
models/capacity, lift PAUSE, authorize a pilot, or promote beyond Phase 8. Those remain separately
gated next actions.

## Phase 8 actuator deployment: failed closed and rolled back

Lucas explicitly authorized one fresh PAUSE-held Phase 8 actuator deployment, bounded to the exact
reviewed `hermes-actuator.service`. The boundary excluded gateway changes, PAUSE removal,
model/capacity configuration, notification, pilots, and product-repository changes, and required
automatic rollback on any mismatch.

Fresh authenticated evidence found current workstation `origin/master` at PR #31 merge
`b23069ee49519fda5896f43ec888efd71b533167`, the Phase 1 evidence commit `71e651ad...` and Phase 7
implementation `b4d3a303...` as ancestors, the evidence review branch pruned, and protection rule
`81491567` still requiring a pull request and conversation resolution with administrator bypass,
force-push, and deletion disabled. The production checkout remained `loop/auto` at
`73987156f5d22d2f2f50ddc542c978d0c48f88b8`; its executable tree had no drift after reviewed
runtime base `fa026358...`, and all 18 Phase 8 runtime/config blobs matched current merged master.

An initial preflight stopped before deployment because it assumed an empty pending queue. Read-only
inspection found exactly one valid Head Hermes PAUSE-safe no-op projection,
`decision-6f037cbf6fb51a7f641ea9d6`, with SHA-256
`883d9f53e2d7263d8ffa733fe61bff959cf1b7e341d4a293d0a9b00f8e0c6684`. The gate was narrowed to
accept only that exact record; a second or different record remained fatal. No live data changed.
The fresh corrected preflight then passed the 17/17 baseline, every Phase 1-8 control and positive
audit, and live Phase 1.

The authorized transaction used root-owned mode-`0700` bundle
`/var/backups/recursion/phase8-actuator-20260810T004518Z-b23069ee`. It stopped only cron, left the
hardened gateway running, created and verified a 19-file runtime snapshot, restored and verified it
in disposable staging, and removed staging. After `FINAL_PREDEPLOY_GATE=PASS`, the exact reviewed
unit (SHA-256 `5cfd8853d6e66068670aa5f9afcfa5b5671730af927d166a8dca4dad50486d4e`)
was installed and reached active/running as PID `2934221` from `2026-08-10T01:11:45Z`.

The expected PAUSE-safe no-op did not leave pending state within the bounded observation. The
transaction failed at `2026-08-10T01:12:10Z` with
`DEPLOY_FAIL=paused-noop-still-pending` and automatically rolled back by `01:12:12Z`. It disabled
and removed the actuator unit, restored the exact runtime snapshot and prior crontab/cron state,
and left the gateway untouched. No action, event, report, delivery, notification, or pilot was
created, and no retry occurred.

Read-only root-cause proof found six records in `state/decisions.jsonl`. The first five are legacy
pre-schema no-ops whose prose `goal_id` values are not canonical identifiers; the sixth is the
valid pending no-op. `conduct-hermes.sh --paused-safe` calls `decision-queue.py import-journal`
before claiming pending work. Import normalizes and validates line 1 before checking existing
projections, fails on that legacy `goal_id`, and returns before line 6 can be claimed. The actuator
currently suppresses that command's diagnostic and continues its loop, explaining the silent
pending record. The journal itself was not edited, migrated, skipped, or drained.

Independent closure reran the complete matrix from `2026-08-10T01:17:19Z` through `01:36:16Z`;
all 18 control/audit commands returned zero. A new snapshot matched all 19 pre-deployment runtime
records exactly after excluding only `created_at`, restored and verified in disposable staging,
and staging was removed. Final state at `01:37:02Z` was:

```text
PAUSE=919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db
CONTROL_PLANE=da43555b6977e55fc0bb185fd7d6d5e76384b638cbcaff4d798596cce68630d4
ACTUATOR_LOAD=not-found
ACTUATOR_ACTIVE=inactive
ACTUATOR_ENABLED=not-found
CRON_ACTIVE=active
GATEWAY_ACTIVE=active
GATEWAY_PID=2781295
WORKERS=0
PROJECT_PROCESSES=0
OUTBOXES=9 paused=true events=0 deliveries=0
MODEL_ROUTING=unset
CAPACITY=zero
```

The bundle's 169 data files were sealed after all log writers stopped; its manifest verifies and
has SHA-256 `2de6f66997e384d5e360b8005d12cdf73a88f3e895bfa93d38a4156992e13319`.
Phase 8 remains undeployed and every pilot remains blocked. The next admissible action is the
separate reviewed legacy-journal compatibility patch described above, followed only after merge by
a fresh preflight and separately authorized deployment retry.

## Compatibility merge, evidence correction, and PAUSE-resync blocker

Lucas reviewed, merged, and pruned both Phase 8 follow-up branches. Workstation fetch established
current `origin/master` `be3cb8b6462bc6bbe2ba12305e6bee47ee102fc8`, with evidence commit
`abdf4fe4bd1e8cd5ef19c5956b54a441738891a2`, compatibility commit
`1748f75443b2d81b5951339f88e7c3fc5d2bf6cc`, Phase 7 implementation `b4d3a303...`, and their
merge commits as ancestors. The review branches were absent. GitHub protection rule `81491567`
still required pull requests and conversation resolution, applied to administrators, and disabled
force pushes and deletion.

Lucas then authorized corrected Phase 8 production testing. The authorization was interpreted as
merged compatibility code plus actuator verification under PAUSE; it did not authorize PAUSE
removal, a pilot window, notification, model/capacity/configuration change, gateway maintenance,
or product-repository work.

### Stale compatibility hash stopped the first preflight

Before a control or production mutation, exact merged-source extraction found that the compatibility
handoff's `scripts/decision-queue.py` Linux SHA-256 was stale. The reviewed Git blob is
`510fce16166a6e69b2604cdecd10441262ca202a`; its Linux SHA-256 is
`082c82b6ff5e82fd2123322f8dc695323ca3091ff959254b12f4a46c77fd8a08`, not the recorded
`b487eb78...`. The other five recorded hashes matched. This was not accepted as a line-ending
explanation or silently waived.

The stopped attempt is retained at root-owned mode-`0700` bundle
`/var/backups/recursion/phase8-actuator-20260810T024806Z-be3cb8b`. Its corrected final state showed
production unchanged at `73987156...`, exact PAUSE/journal/pending hashes, absent actuator, active
gateway/cron, zero workers/processes, zero legacy markers, unset routing/capacity, and all nine
outboxes paused and empty. Its manifest verifies with SHA-256
`b7b50eb68331e502bf2c7edccf6d0183371a09427ff853ac04d6d3508495d2f5`. An initial final-state
capture had shell-quoting errors; it is retained as `final-state-attempt1.txt` and was not used as
positive evidence.

### Evidence-only rerun exposed a higher-priority PAUSE defect

Lucas separately authorized an evidence-only correction branch and a rerun of the exact merged
Linux matrix plus disposable live-shaped proof. Clean authoring branch
`review/hermes-phase8-preflight-evidence-correction` started from `be3cb8b...`. A fresh root-owned
bundle staged exact reviewed source outside `/opt/recursion`.

Negative setup observations were preserved rather than converted to passes: the first composite
upload command failed on Windows-to-SSH quoting before target creation; a later standalone Python
syntax wrapper misquoted its compile mode; and matrix attempt 1 failed before tests because the
new bundle parent was mode `0755` while its evidence child was `0700`. After preserving those logs,
only the bundle parent was corrected to `0700`.

Matrix attempt 2 also stopped before its first test because the live HEAD gate changed. Read-only
reconstruction established this exact chain:

```text
2026-08-10T03:15:01Z cron starts cycle.sh with state/PAUSE present
cycle.sh classifies resync as awareness and calls resync.sh sync under PAUSE
resync advances local master by six commits to be3cb8b...
resync creates ce9904b3dfed64c90f95b5214b0fc5460f81810f
  first parent 73987156f5d22d2f2f50ddc542c978d0c48f88b8
  second parent be3cb8b6462bc6bbe2ba12305e6bee47ee102fc8
cycle records deliver=0 and commits morning/board awareness
final loop/auto = 30fb73f56496d1d8e72f00dceb4b59de4bd21a00
```

The merge changed the two evidence docs, compatibility handoff, production plan, and all six
compatibility implementation/control files in the production checkout. Exact merged
`decision-queue.py` blob `510fce1...` is therefore already present on production, but the actuator
unit remains absent and no queue processing occurred. This checkout change happened before the
authorized full baseline, runtime snapshot, staging restore, exact rollback, and
`FINAL_PREDEPLOY_GATE`; it is not a successful deployment and must not be described as one.

The behavior is a direct precedence conflict. Live `CONTROL_PLANE.md` says PAUSE halts
branch-changing maintenance. Lower-ranked `scripts/cycle.sh` says resync runs under PAUSE, and
`scripts/tests/pause-semantics.test.sh` positively requires it. The relevant live SHA-256 values
are `904fc1a5...` (`cycle.sh`), `511383a5...` (`resync.sh`), and `6882f93f...`
(`pause-semantics.test.sh`). Under the constitution, the control plane wins; the implementation and
test are stale.

The retained evidence bundle is
`/var/backups/recursion/phase8-evidence-correction-20260810T032141Z-be3cb8b`. Its manifest verifies
with SHA-256 `34ddf6d0c4666f5b5ac5613c5e480ce6bc437a4eec6d421d70b8cd4921899ad9`.
Final state at `2026-08-10T03:27:38Z` was exact PAUSE, unchanged journal and pending decision,
zero legacy markers, absent/inactive actuator, active gateway PID `2781295`, active cron, zero
workers/project processes, unchanged configuration, and nine paused empty outboxes. The cycle log
proves `deliver=0`. No control matrix, live-shaped proof, service mutation, action, event,
notification delivery, or pilot started.

### New gate

Phase 8 actuator testing is blocked. The next admissible implementation is a separate reviewable
PAUSE/resync control patch, not a manual reset or workaround. It must:

1. add a red control proving current paused `cycle.sh -> resync.sh sync` changes the checked-out
   executable tree;
2. preserve read-only fetch/status/behind awareness under PAUSE;
3. refuse checkout, fast-forward, merge, or other branch-changing maintenance while paused;
4. leave the current exact PAUSE/journal/pending state untouched; and
5. pass the complete historical matrix before review.

Only after Lucas reviews/merges/prunes that patch may a new full PAUSE-held preflight and separately
authorized production correction be proposed. Actuator deployment and every pilot window remain
blocked.

## PAUSE-safe portfolio awareness patch

Lucas reported the evidence-correction branch merged and pruned and authorized the separate
PAUSE/resync control patch. A fresh fetch established PR #34 merge
`52f6ad37250d7b7bc798d86c04768aef8cc09c07`, evidence commit `03a5b6a...` as an ancestor, and the
remote review ref absent. The protected dirty workstation master remained exactly `20c1fa7...`
with its 20 pre-existing entries. Clean branch `review/hermes-phase8-pause-resync` was created from
that exact merged base.

The implementation stays in the canonical `cycle.sh -> resync.sh` path:

- `resync.sh observe` performs the existing authenticated `ls-remote` and fetch, evaluates current
  drift/dirt/local-only state, and records the same durable escalations, but has no checkout,
  fast-forward, merge, or local-branch update path;
- paused `cycle.sh` selects `observe` and labels the tick as fetch/status-only; and
- resumed `cycle.sh` still selects the existing `sync` path before dispatch, so the stale-base
  protection remains non-vacuous.

The commit chain is:

```text
2688671a80e7a69929f0b1e137e43485196d72ac  Add paused resync branch-mutation control
1a16d81c396dde5fbcc87d9ac80cca3017fc3bf2  Keep paused portfolio resync read-only
5bbfad5fc46975b6f3de89744a4cd89ab671e201  Stabilize planner concurrency falsifier
```

At exact red commit `2688671...`, the new end-to-end test fetched the disposable remote tip but
also proved old paused `sync` moved local `main` and changed the checked-out executable SHA. It
ended `pause-semantics: 1 FAILED`; every other PAUSE assertion and the resumed fast-forward control
passed. At `1a16d81...`, the direct resync suite and PAUSE suite passed: remote-tracking awareness
advanced, all local heads and the checked-out executable remained exact, and resumed sync still
fast-forwarded.

The complete matrix exposed an independent timing defect in the historical Phase 2 test. Its
old `ls` barrier ran only after one planner held the lock, so the peer could not reach the barrier;
two full sequences produced a false one-task result while five isolated reruns and an exact
baseline/Phase-1-prefix diagnostic passed. Commit `5bbfad5...` aligns both planners immediately
before lock acquisition and preserves the old vulnerable-read barrier only when no planner lock
exists. Five consecutive current-code runs passed. Overlaying that corrected falsifier on exact
pre-Phase-2 base `b25b329...` still produced all six intended failures, including
`planner CAS missing`; the invariant was strengthened, not waived.

The final exact-commit Linux matrix ran from `2026-08-10T04:24:52Z` through `04:44:09Z` and ended:

```text
BASELINE_SUITES=17
BASELINE_FAILED_SUITES=0
phase1-control through phase8-audit: RC=0
MATRIX_TOTAL=17 MATRIX_PASSED=17 MATRIX_FAILED=0
MATRIX_RESULT=PASS
```

All raw red, green, failed-attempt, timing-diagnostic, pre-change falsifier, and final-matrix logs
are retained root-owned and mode `0700` at
`/var/backups/recursion/phase8-pause-resync-authoring-20260810T034342Z-52f6ad3`. The evidence
manifest SHA-256 is `62ec571b6d750d6ebbd9614ab0729ff0bec8f8e8c9d1c88775d5b2b7021a0872`.

Final read-only production verification at `2026-08-10T04:47:21Z` matched the pre-test snapshot:

```text
HEAD=30fb73f56496d1d8e72f00dceb4b59de4bd21a00
MASTER=ORIGIN_MASTER=be3cb8b6462bc6bbe2ba12305e6bee47ee102fc8
PAUSE=919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db
JOURNAL=c0a03878fc98df2bb6e6a83496d003dd198e53a8477cb004af6a3909f5b103a0
PENDING=883d9f53e2d7263d8ffa733fe61bff959cf1b7e341d4a293d0a9b00f8e0c6684
GATEWAY=active/running PID 2781295
CRON=active
ACTUATOR=not-found/inactive
WORKERS=0
OUTBOXES=9 paused=true events=0 deliveries=0
```

No `/opt/recursion` file, service, configuration, notification route, action/event/delivery,
product repository, PAUSE state, or pilot window was changed. The next gate is Lucas review,
merge, and pruning of this branch. Only then may a fresh PAUSE-held production correction be
proposed; it still requires separate authorization. Phase 8 actuator deployment and every pilot
remain blocked.
