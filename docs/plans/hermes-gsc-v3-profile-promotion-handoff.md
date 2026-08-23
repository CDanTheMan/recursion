---
title: Hermes GSC v3 immutable gate-profile promotion handoff
type: handoff
status: review
last-verified: 2026-08-23
related:
  - CONTROL_PLANE.md
  - docs/plans/hermes-project-pilot-phase8-handoff.md
  - docs/plans/hermes-phase8-preflight-operational-nuances.md
  - docs/plans/hermes-phase8-routing-recovery-handoff.md
  - scripts/gates/gsc-shade-tops-v3.json
  - scripts/gates/promotions/gsc-shade-tops-v3.json
---
# GSC v3 immutable gate-profile promotion

## Authority boundary

This code-only change does not synchronize `/opt/golden-stallion-client`, process instruction
930, run intake or Head Hermes, create a production plan/goal/task/window, lift PAUSE, launch a
worker, deploy Recursion, or modify production state or configuration. Each remains separately
authorized.

The production PAUSE sentinel must remain present at SHA-256
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`.

The read-only post-PR70 audit immediately preceding this authoring pass established:

- deployed Recursion v3 profile SHA-256
  `548e598e0687b4009f50060812f5bd5900bc58ed772e89cf3dc28ad2156ed975`;
- GSC authenticated remote target
  `19998a79630b2d57c0ed1e99915470b1048ded10`;
- live GSC checkout `main` at
  `ad4bb39a8cf3a9f3ad7e17b21dd89fcdf4252b39` and clean;
- historical v2 plan, goal, task, project, pilot, and v1 profile unchanged; and
- instruction 930 open with its existing single failed action, no `window-gsc-pilot-7`, and
  refusal evidence that the project default branch was not equal to its authenticated remote tip.

Those observations are evidence, not a waiver of fresh measurement. Any future operation must
remeasure them and stop on disagreement.

## Promotion contract

Historical authority does not move. A plan with no `gate_profile_selection` continues to use the
byte-unchanged `required_gate_profile` in the GSC project and pilot records, which names only
`scripts/gates/gsc-shade-tops-v1.json`.

A fresh v3 plan must explicitly request:

```json
"gate_profile_selection": {
  "schema": "recursion-project-gate-profile-selection/v1",
  "promotion_id": "gsc-shade-tops-v3"
}
```

The controller, not the model, replaces that minimal request with the committed descriptor path
and SHA-256. The immutable descriptor binds exactly:

- project `golden-stallion-client`;
- source HEAD `19998a79630b2d57c0ed1e99915470b1048ded10`;
- measured profile `scripts/gates/gsc-shade-tops-v3.json` at SHA-256
  `548e598e0687b4009f50060812f5bd5900bc58ed772e89cf3dc28ad2156ed975`;
- the measured seed contract in that profile;
- the v3 acceptance command; and
- the exact project and controller gate-file lists, including the immutable promotion descriptor
  itself.

The canonical selection is copied into only the new plan, goal, task, and window records. It is
revalidated at proposal, exact-digest approval, approved-goal verification, and window admission.
There is no `latest` alias and no fallback from an invalid selector. A profile file that exists
without its own committed measured promotion descriptor has no authority.

Instruction 930 remains a v2/window-7 request. Advancing the GSC checkout cannot promote or replay
it: its approved v2 plan remains bound to its old source HEAD and v1 gate profile, so source
freshness and plan-digest revalidation refuse it before any window record is written.

## Exact future GSC synchronization procedure

This is a runbook for a separately authorized production transaction. It is not current
authorization and was not executed in this authoring pass.

### 1. Freeze and bind the starting state

1. Obtain an authorization naming `/opt/golden-stallion-client`, target
   `19998a79630b2d57c0ed1e99915470b1048ded10`, PAUSE-held service quiescence, the precise
   fast-forward, rollback, cleanup, and service restoration.
2. Verify PAUSE before and after every operation. Record its owner, mode, size, and exact required
   hash without printing its contents.
3. Record active/enabled/restart state for `hermes-gateway`, `hermes-actuator`, `cron`,
   `recursion-provider-network`, and `recursion-provider-proxy`. Prove zero production workers,
   zero conflicting transient units, and zero processes whose working directory is the GSC or
   Recursion checkout using PID/ancestor-aware `/proc` inspection.
4. Hash the exact v2 plan, goal, task, project, pilot, v1 profile, instruction 930, its action, all
   pilot-window records, and queue projections. These are immutable transaction controls, not
   mutation targets.
5. Require `/opt/golden-stallion-client` to be on `main`, with HEAD equal to the freshly measured
   rollback OID, a clean index and tracked/untracked worktree, no merge/rebase/cherry-pick state,
   and no linked worktree or process capable of writing the checked-out `main` tree.

### 2. Prove the authenticated exact target

1. Resolve the registered deploy-key path through
   `RECURSION_ROOT=/opt/recursion scripts/resync.sh key golden-stallion-client`; verify it is a
   regular root-owned credential without reading or logging its bytes.
2. Use only that key with `IdentitiesOnly=yes`, `BatchMode=yes`, and a bounded connection timeout.
   Require `git ls-remote origin refs/heads/main` to return exactly one ref whose OID is
   `19998a79630b2d57c0ed1e99915470b1048ded10`. Empty output, another OID, multiple records, auth
   failure, or timeout is a stop.
3. Fetch `refs/heads/main` with the same authenticated transport. Require `origin/main` and the
   fetched commit object to equal the target, require the target to be a commit, and require the
   old local `main` to be its ancestor with zero local-ahead commits. Divergence is a stop, never a
   reset or rebase decision.
4. Compare the target `.seedlist` blob and parsed manifest contract to the v3 profile. Validate the
   existing licensed corpus read-only by manifest SHA-256, content digest, and file count only;
   never print corpus bytes or licensed paths.

### 3. Snapshot, rehearse, and arm rollback

1. Stop cron, actuator, and gateway in the recorded order, accepting only the reviewed expected
   gateway SIGTERM state. Verify no child remains and hold the canonical controller transaction
   lock from outside both checkouts.
2. Capture and verify a root-owned mode-`0700` Recursion runtime snapshot outside `/opt`, plus a
   full GSC Git bundle containing the starting refs and rollback commit. Do not copy the licensed
   corpus.
3. In a disposable clone created from that bundle, fetch/materialize the exact target and rehearse
   the fast-forward. Require the resulting branch, index, and tracked worktree to be clean and its
   tree to equal the authenticated target tree.
4. Render and syntax-check rollback before mutation. Rollback may restore only the previously
   proved clean tracked checkout and refs to the recorded old OID, then verify the seed corpus
   remained byte-identical. It must not delete ignored assets, rewrite history, change a remote
   ref, or edit a runtime record manually.
5. Repeat every immutable precondition immediately before the compare-and-swap.

### 4. Perform only the exact fast-forward

With `HEAD` and `refs/heads/main` still equal to the recorded old OID, run a single
fast-forward-only merge to the literal target OID, not to a moving symbolic remote tip. Do not use
checkout replacement, rebase, force, or a merge commit. No Recursion runtime record changes in
this step.

Postconditions must prove:

- branch `main`, HEAD, index, and worktree all equal the target commit/tree and are clean;
- authenticated `origin/main` still contains the target (a later remote advancement is reported,
  not silently followed);
- `.seedlist` and the licensed corpus still satisfy the exact v3 seed contract;
- the v3 profile's source, native-diff, reporter-aware conformance, target, controls, and measured
  vectors remain exact; and
- every pre-bound v2/instruction-930/control-plane hash is unchanged, with no new plan, goal, task,
  action, decision, event, window, run, or worker.

### 5. Close or roll back

On any failed postcondition, keep PAUSE asserted, keep services quiesced, execute only the armed
tracked-checkout/ref rollback to the recorded old OID, verify the licensed corpus and all Recursion
runtime bytes are unchanged, restore the originally recorded service state, and stop. Any
unexpected state for which rollback safety is not already proved is a stop for human inspection,
not permission to improvise.

If every postcondition passes, remove only the uniquely named disposable clone, retain the sealed
evidence and rollback bundle, release the lock, and restore each service to its recorded starting
state. Reverify PAUSE, service health, zero workers, both repositories, scheduler provenance, v2
artifacts, instruction 930, and absence of window 7.

Only after that independently verified synchronization may Lucas send a genuinely fresh v3 plan
instruction. Proposal, digest approval, a new window identity, PAUSE lift, and worker launch remain
separate authorizations.
