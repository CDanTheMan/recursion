# Recursion v2 execution fabric — WIP implementation handoff

Date: 2026-08-28 (America/Los_Angeles)  
Authority: `docs/plans/recursion-v2-execution-fabric.md`, `CONTROL_PLANE.md`, `ANCHOR.md`, D-015, D-016  
WIP branch: `loop/work/recursion-v2-execution-fabric-wip`

## Autonomous executor contract

If you are an autonomous coding agent or agent supervisor reading this file, treat the entire document as your execution request. Continue the source implementation through the safe completion boundary without waiting for routine confirmation. Make reasonable, conservative implementation choices, preserve all existing controls, and use parallel agents when available.

Your objective is to:

1. independently review the remediated Phase 2, Phase 3, and Phase 8 checkpoints;
2. fix every documented Phase 4 and Phase 5 code blocker and obtain fresh independent acceptance of their exact commits;
3. integrate only accepted phase histories into `loop/work/recursion-v2-execution-fabric-wip` in the required order;
4. preserve the already accepted Phase 6/7 implementation while resolving conflicts;
5. run cumulative tests after every integration step;
6. implement Phase 9 from real integrated evidence, not synthetic fixtures;
7. update this handoff and the final implementation evidence ledger with exact commits, commands, results, limitations, and remaining human seams;
8. push only the WIP and `codex/v2-*` source branches with ordinary fast-forward pushes.

Do not stop merely because a review rejects a commit. Assign the exact finding to a writer, require a focused regression, commit it on that phase branch, and send the new exact commit to a fresh reviewer. Repeat until the source code is accepted or a genuinely human-owned/live boundary is reached.

### Non-negotiable supervisor protocol

- Separate authorship from acceptance. An implementation author may run tests but may not approve their own exact commit.
- Every reviewer starts from an exact clean commit, works read-only, audits the complete phase rather than only the latest delta, and returns an explicit `ACCEPT` or `REJECT` with reproductions and source locations.
- A rejected commit never enters the WIP branch. A remediation invalidates any earlier acceptance and requires another fresh review.
- Treat uncaught exceptions, schema/runtime mismatches, unsafe direct-object construction, path/symlink/reparse races, stale authority, credential exposure, ambiguous reconciliation, and vacuous tests as hard failures.
- Preserve unrelated user changes. Never use destructive reset/checkout commands to clean a worktree.
- Never resolve a conflict by selecting an entire side. Reconstruct the combined invariant and retain tests from both phases.
- Continue autonomously through code, tests, review, local integration, documentation, and authorized branch publication. Stop at deployment, live provider/controller calls, PAUSE removal, credential/spend changes, protected/default-branch publication, or destructive cleanup.

## Fresh-clone bootstrap

Use a new clone. Do not depend on the original Windows paths in the frozen checkpoint descriptions.

```bash
git clone https://github.com/NotSkittlz/recursion.git
cd recursion
git fetch origin --prune
git switch --track origin/loop/work/recursion-v2-execution-fabric-wip
git status --short
```

The status output must be empty before proceeding. Materialize isolated phase worktrees from the published remote branches:

```bash
for branch in \
  codex/v2-adapters \
  codex/v2-claude-sonnet \
  codex/v2-hardening \
  codex/v2-cursor-runtime \
  codex/v2-claude-opus \
  codex/v2-placement
do
  git show-ref --verify --quiet "refs/heads/$branch" \
    || git branch --track "$branch" "origin/$branch"
  directory="../${branch//\//-}"
  git worktree add "$directory" "$branch"
done
```

Verify the immutable frozen phase checkpoints before editing:

```text
codex/v2-adapters        31a21c0f12ab6e23895a988b1bc7cb38631562e6
codex/v2-claude-sonnet   cfb5d58a92b355540fc8ad1e1cac8a76ab37c43e
codex/v2-hardening       ce1529685c4760eda5442d2cea5c945d9b25693a
codex/v2-cursor-runtime  04b26bdd0b725a910cb389c44d7acea1b1c6503a
codex/v2-claude-opus     fb4d2d633dea12138e7b2b008e5b1c836bd00913
codex/v2-placement       f89d0a23f985453daa806d4fb2b971bc5b3bc14a
```

If a remote branch has advanced beyond its frozen SHA, inspect its new commits and recorded review evidence. Do not reset or force-push it. Resume from the newer commit only when its provenance is clear; otherwise create a new `codex/` remediation branch from the frozen SHA and record that choice here.

After checkout, the complete provider prompt can be only:

> Read `docs/audits/recursion-v2-execution-fabric-wip-handoff-2026-08-28.md` completely, then execute its Autonomous executor contract through the documented safe completion boundary. Act as the strict supervisor, use independent writers and reviewers where available, persist progress to the published phase/WIP branches, and do not cross any listed human or live-system seam.

## Safety and operational state

- This is a source-only implementation handoff. It does not authorize deployment, credential changes, spending, PAUSE removal, protected/default-branch publication, or destructive cleanup.
- `gs-recursion` remains PAUSED. No live controller, provider, credential, deployment, or production state was changed during this implementation run.
- Every phase worktree listed below was clean when the swarm was frozen.
- Do not infer completion from a green author test. A phase is integrated only after a fresh independent adversarial review explicitly accepts its exact commit.

## Integrated WIP state

The WIP branch currently contains only accepted Phase 0 and Phase 1 work.

- Pre-handoff WIP HEAD: `52e56c5502ff3f4c923590f540ab88619f9b6d11`
- Phase 0: accepted and integrated. Audit: `docs/audits/recursion-v2-phase0-preflight-2026-08-28.md`.
- Phase 1: accepted and integrated. The final contract suite passed 16/16 plus an exact 5,292-case runtime/root/direct mutation matrix.
- Phases 2–8 are intentionally not cherry-picked into the WIP branch yet. Their exact source branches and dispositions follow.

## Frozen phase checkpoints

### Phase 2 — repository adapters and acceptance contracts

- Branch: `codex/v2-adapters`
- HEAD: `31a21c0f12ab6e23895a988b1bc7cb38631562e6`
- Disposition: **REMEDIATED; FRESH INDEPENDENT REVIEW REQUIRED**.
- The prior reviewer rejected 11 unique public-schema/runtime gate grammar mismatches found by a 4,236-command differential corpus.
- The latest commit unifies the schema/runtime lexical boundary; rejects path-qualified launchers, dynamic wrapper options, traversal/backslash tricks, Git redirects, malformed quoting/segments, result-report dependence, and bounded-length mismatches; and adds a deterministic differential regression.
- Author verification at the frozen commit: strict gate 10/10, repository contract 16/16, nine descriptors under Draft 7 and Draft 2020-12 plus CLI, planner automerge, compile, Bash syntax, diff check, and zero differential mismatches/raw exceptions.
- Next action: fresh read-only hostile review of the exact HEAD. Do not integrate based only on the author result.

### Phase 3 — immutable assignment and durable evidence

- Branch: `codex/v2-claude-sonnet`
- HEAD: `cfb5d58a92b355540fc8ad1e1cac8a76ab37c43e`
- Disposition: **REMEDIATED; FRESH INDEPENDENT REVIEW REQUIRED**.
- The prior reviewer proved a Windows parent-directory swap could redirect generic durable-lock creation outside the intended tree even though the lock leaf itself was protected.
- The latest commit pins every Windows parent component with native handles that deny delete sharing, rejects reparse components and leaves, revalidates volume/file identity after open, and retains pins through the lock lifetime.
- Author verification at the frozen commit: deterministic parent-swap and leaf-junction regressions, Phase 3 and adjacent durability suites, 48-process identical/divergent stress, compile, Bash syntax, and diff check.
- Next action: independently reproduce the parent rename/junction race and all earlier assignment/index/cache swap cases at the exact HEAD.

### Phase 4 — Linux isolation, provider egress, backup, and secrets

- Branch: `codex/v2-hardening`
- HEAD: `ce1529685c4760eda5442d2cea5c945d9b25693a`
- Disposition: **REJECT — TWO CODE BLOCKERS REMAIN**.
- The latest commit correctly fixes Cursor-style plans with `env_passthrough: []`: proxy coordinates and assignment-scoped Basic credentials are now materialized in the root-owned transient `EnvironmentFile`, passed to `systemd-run`, and cleaned up.
- Remaining blockers from the fresh full review:
  1. `scripts/provider-egress.py` still accepts `--assignment-token` and `--assignment-identity`, leaving a reachable argv-secret interface even though the worker uses environment-only injection.
  2. `scripts/provider_contract.py` accepts numeric IP-literal authorities such as `1.2.3.4:443`, while the live proxy contract rejects them. Shared profile validation must enforce canonical DNS-only authorities.
- Next action: remove the argv-secret options entirely, use only the ephemeral environment interface, reject IP literals in shared profile validation, add regressions, rerun the provider/backup/secret suites, then obtain a fresh independent review.
- Still human/live pending after code acceptance: Linux/systemd ownership and isolation proof, provider-network integration, and a real encrypted off-host restore drill.

### Phase 5 — generalized engine runtime and gate provenance

- Branch: `codex/v2-cursor-runtime`
- HEAD: `04b26bdd0b725a910cb389c44d7acea1b1c6503a`
- Disposition: **REJECT — FIVE CODE BLOCKERS REMAIN**.
- The frozen commit does correctly enforce provider/profile-scoped environment allowlists, provider/profile/endpoint equality, required network capability, non-vacuous gate-file binding, source/controller HEAD checks, and token-free durable plans.
- Remaining blockers from the fresh full review:
  1. Strict-direct gate validation accepts an interpreter traversal such as `python3 ../outside.py` when another gate file is independently hashed; execution can resolve outside the allowed tree.
  2. Engine manifests, provider profiles, and capacity-pool policy are read from live controller files without authenticating those exact files to `controller_sha`; an alternate canonical controller root at the same commit is also accepted.
  3. Assignment validation checks `source_branch` syntax but does not prove that the named branch identifies the assigned source commit/current checked-out authority.
  4. `worker-evidence.py finish` accepts execution evidence without comparing its engine, provider, profile, endpoints, model, argv, and assignment identity to the immutable assignment; reconciliation does not close this gap.
  5. The declared `sentry-local` profile has no endpoints, while the provider capability path requires at least one authority, making the registered local engine permanently unavailable.
- Next action: remediate all five as one authority-consistency change, add adversarial tests for each, rerun the complete Phase 5 suite, then obtain a fresh independent review.

### Phases 6 and 7 — pilot loop, notifications, and remote adapters

- Branch: `codex/v2-claude-opus`
- HEAD: `fb4d2d633dea12138e7b2b008e5b1c836bd00913`
- Disposition: **CODE ACCEPTED; HOLD FOR ORDERED INTEGRATION**.
- Independent review passed all five remote suites twice, the eight-round Cursor reconciliation race stress, endpoint/schema/runtime differential matrices, secrecy behavior, compile/schema checks, and diff check.
- Draft 7 cannot compare sibling branch fields; the limitation is documented and the runtime enforces `integration_branch != default_branch`.
- Still human/live pending: Linux-only Phase 6/7 positive audit and real Cursor/Grok transport proof.

### Phase 8 — placement, leases, recovery, receipts, and Windows harness

- Branch: `codex/v2-placement`
- HEAD: `f89d0a23f985453daa806d4fb2b971bc5b3bc14a`
- Disposition: **CODE PREVIOUSLY ACCEPTED; HARNESS REMEDIATED; FRESH FINAL REVIEW REQUIRED**.
- The fabric code previously passed independent review after fixes for lease-expiry recovery, schema parity, direct-dataclass validation bypasses, fixed trust registration, receipt authentication, PAUSE, and routing.
- The latest test-only commit adds fixture-local Windows compatibility, explicit Git Bash/Python handling, portable process termination, and lock-owner assertions for both `work.sh` and `conduct-hermes.sh`.
- Author verification at the frozen commit: fabric 27/27, direct 9/9, reject 6/6, legacy 6 plus one explicit Linux-only skip, parallel and Windows harness pass, compile/Bash/diff checks pass.
- Next action: fresh independent read-only final review of the exact HEAD. Linux owner/mode/symlink/systemd/actuator evidence remains pending.

### Phase 9 — final evidence and completion ledger

- Disposition: **NOT STARTED**.
- Do not reuse the earlier synthetic scaffold (`474571b`); it was rejected as vacuous.
- Build Phase 9 only after accepted Phase 2–8 commits are integrated and cumulative tests run from the WIP branch.

## Required integration order

After the exact phase commits receive the dispositions required above, integrate in this order:

1. Phase 2
2. Phase 3
3. Phase 4
4. Phase 5
5. Phases 6/7
6. Phase 8
7. Phase 9 evidence ledger

Resolve overlaps manually and preserve every accepted control. Known high-conflict files include:

- `scripts/work.sh` — Phases 3, 4, 5, 8
- engine schemas/manifests, provider egress/network, resolver, and worker sandbox — Phases 4 and 5
- assignment, scorecard, task control, usage reconcile, and worker evidence — Phases 3 and 5
- `scripts/jsonl_durable.py` — Phases 3, 6/7, and 8
- PAUSE/resume control — Phases 4, 6/7, and 8
- `scripts/conduct-hermes.sh` — Phases 4, 6/7, and 8

Run the cumulative accepted suites after every cherry-pick group. Never resolve a conflict by blindly choosing one phase's complete file.

### Integration mechanics

Integrate a phase's complete unique history, not only its tip commit. From a clean WIP worktree, after the phase's exact tip has a fresh acceptance:

```bash
git switch loop/work/recursion-v2-execution-fabric-wip
git fetch origin --prune
phase=origin/codex/v2-adapters   # replace for the accepted phase
base="$(git merge-base HEAD "$phase")"
git log --reverse --oneline "$base..$phase"
git cherry-pick $(git rev-list --reverse "$base..$phase")
```

Before cherry-picking, inspect the listed commits and confirm they contain only that phase's intended history. If a phase branch was rebased, merged, or contains unrelated commits, stop the cherry-pick and reconstruct a reviewed minimal series on a new `codex/` branch. Never force the WIP branch through a non-fast-forward remote update.

After resolving any conflict:

1. run `git diff --check`;
2. run every test belonging to both overlapping phases;
3. inspect authority-, secret-, path-, locking-, and evidence-bearing code manually;
4. commit only when the combined behavior is green;
5. obtain another integration-level review when conflict resolution changed semantics;
6. push the WIP branch with a normal fast-forward push.

## Mandatory local test matrix

Run from each phase worktree before acceptance. Use the platform's Python executable consistently and a real `jsonschema` installation where schema parity is tested.

### Phase 2

```bash
python scripts/tests/validate-gate.test.py
python scripts/tests/repository-contract.test.py
bash scripts/tests/plan-automerge.test.sh
bash -n scripts/tests/plan-automerge.test.sh
git diff --check
```

The reviewer must also generate a broad schema-versus-runtime acceptance-gate corpus containing valid chains and hostile quoting, escaping, traversal, absolute paths, redirects, wrapper flags, dynamic interpreters, result-report dependence, empty segments, and length boundaries. Required result: zero raw exceptions and zero mismatches.

### Phase 3

```bash
python scripts/tests/assignment.test.py
python scripts/tests/validate-assignment-result.test.py
python scripts/tests/worker-evidence-assignment.test.py
python scripts/tests/usage-reconcile.test.py
python scripts/tests/usage-reconcile-quota.test.py
python scripts/tests/engine-scorecard.test.py
python scripts/tests/engine-scorecard-assignment.test.py
python scripts/tests/jsonl-durability.test.py
bash scripts/tests/hermes-pilot-phase3-red.test.sh
git diff --check
```

On Windows, independently exercise parent-directory and leaf-junction swaps plus at least 40 identical and 40 conflicting concurrent assignment writers. On POSIX, exercise the equivalent dirfd/no-follow boundaries. No record, lock, index, cache, or temporary may escape the intended root.

### Phase 4

```bash
python scripts/tests/provider-connect-proxy.test.py
python scripts/tests/provider-egress.test.py
python scripts/tests/backup-offsite.test.py
python scripts/tests/secret-runtime.test.py
python scripts/tests/runtime-state-recovery.test.py
bash scripts/tests/phase4-scope-recovery.test.sh
bash scripts/tests/hermes-pilot-phase4-red.test.sh
python scripts/tests/phase4-linux-proof.test.py
bash scripts/tests/provider-network-root.test.sh
git diff --check
```

Linux/root/systemd tests may report a truthful unsupported/pending outcome off-box. That is not permission to weaken them or to claim production proof. All platform-independent provider, parser, secret, backup, and state tests must pass.

### Phase 5

```bash
python scripts/tests/phase5-hardening.test.py
python scripts/tests/phase5-runtime-contract.test.py
python scripts/tests/engine-manifest-schema.test.py
python scripts/tests/engine-manifest.test.py
python scripts/tests/resolve-engine.test.py
python scripts/tests/validate-gate.test.py
python scripts/tests/worker-sandbox-plugin.test.py
bash scripts/tests/worker-sandbox-hermes-usage.test.sh
bash scripts/tests/worker-gate-authority.test.sh
bash scripts/tests/hermes-pilot-phase5-red.test.sh
python scripts/tests/provider-connect-proxy.test.py
bash scripts/tests/provider-network-root.test.sh
git diff --check
```

Add focused regressions for every one of the five frozen blockers. Then perform a hostile assignment/gate/evidence mutation matrix covering dirty and alternate controller roots, source branch identity, gate traversal, policy-file provenance, execution-evidence mismatches, provider/profile/env cross-binding, and local/no-egress engines.

### Phases 6 and 7

```bash
python scripts/tests/remote-backend.test.py
python scripts/tests/remote-assignment.test.py
python scripts/tests/remote-hardening.test.py
python scripts/tests/cursor-cloud-adapter.test.py
python scripts/tests/grok-bot-dispatcher.test.py
bash scripts/tests/hermes-pilot-phase6-red.test.sh
python scripts/tests/hermes-pilot-phase7-red.py
python scripts/tests/notification-transition-receipt.test.py
python scripts/tests/invalid-task-contract-notification.test.py
git diff --check
```

Re-run the remote suites after integration even though the frozen source commit was accepted. Conflict resolution may invalidate that acceptance.

### Phase 8

```bash
python scripts/tests/execution-fabric-phase8.test.py
python scripts/tests/hermes-phase8-routing-recovery-red.py
python scripts/tests/hermes-pilot-phase8-red.py
python scripts/tests/hermes-pilot-phase8-reject-red.py
python scripts/tests/hermes-pilot-phase8-parallel.py
python scripts/tests/hermes-pilot-phase8-legacy-journal-red.py
python scripts/tests/phase8-windows-harness.test.py
python scripts/tests/phase8-notification-authentication.test.py
python scripts/tests/phase8-head-window-admission.test.py
python scripts/tests/phase8-exact-instruction-turn.test.py
python scripts/tests/phase8-authority-availability.test.py
git diff --check
```

Require exact schema validation with `jsonschema`; a missing dependency is an environment failure, not a product pass. Preserve explicit Linux-only skips as pending production evidence.

## Phase 9 and autonomous completion criteria

Create `docs/audits/recursion-v2-implementation-evidence-2026-08-28.md` only from the integrated WIP branch. It must include:

- exact accepted phase tips and integrated WIP commits;
- reviewer identity/context separation and explicit dispositions;
- every command run, exit status, and meaningful count;
- schema/runtime differential and concurrency-stress results;
- conflict resolutions and the controls preserved from each side;
- all unsupported or human-owned live gates, labeled `PENDING` rather than passed;
- proof that PAUSE, credentials, deployment, spending, default branches, and live services were untouched;
- the final clean WIP status and remote branch tip.

The autonomous source task is complete only when:

1. Phase 2, Phase 3, Phase 4, Phase 5, and Phase 8 have fresh independent acceptance at their final exact commits;
2. Phases 2–8 are integrated in order with cumulative suites green;
3. no unresolved conflict markers, dirty files, schema/runtime mismatches, raw test exceptions, or unreviewed semantic conflict resolutions remain;
4. Phase 9 evidence truthfully distinguishes source completion from live/production proof;
5. the WIP and phase branches are pushed by fast-forward and their remote SHAs are recorded.

Do not mark production complete. Deployment, PAUSE removal, live provider proof, credential/spend changes, off-host restore proof, protected/default-branch publication, and destructive cleanup remain explicit human seams.

## Progress persistence and publication

After every material remediation or acceptance:

1. commit the phase branch with a focused message;
2. record the exact SHA, reviewer disposition, commands, and remaining gaps in this handoff or the final evidence ledger;
3. push the phase branch with `git push origin <branch>` and no force option;
4. after accepted integration and cumulative tests, push `loop/work/recursion-v2-execution-fabric-wip` normally;
5. verify publication with `git ls-remote --heads origin <branch>`.

If a push is rejected, fetch and inspect. Never force-push, delete a remote ref, or overwrite another provider's work.

## Host/tooling notes

- Windows authoring host: use `C:\Program Files\Git\bin\bash.exe` explicitly. Plain `bash` may resolve to unavailable WSL.
- Some Linux controller tests require `fcntl`, `flock`, root ownership, systemd, namespaces, or `/opt/recursion`. A fixture-local compatibility shim is acceptable only for hermetic Windows tests; it is not production evidence.
- Use a Python environment with `jsonschema` for public schema/runtime parity suites. One bundled Python lacked it; the system Python used during review provided it.
- Local Cursor CLI was unavailable. Remote Cursor dispatch was not used because the controller is PAUSED. Do not lift PAUSE merely to complete tests.

## Resume checklist

1. Fetch the WIP and `codex/v2-*` phase branches.
2. Verify every exact commit and a clean worktree before review or remediation.
3. Finish Phase 4 and Phase 5 blockers.
4. Independently review Phase 2, Phase 3, Phase 4, Phase 5, and the Phase 8 harness.
5. Cherry-pick only explicitly accepted exact commits in the required order.
6. Run cumulative tests after each integration and inspect every conflict manually.
7. Produce `docs/audits/recursion-v2-implementation-evidence-2026-08-28.md` from real integrated evidence.
8. Leave deployment, credentials, PAUSE removal, live transport, spending, and protected/default-branch publication for an explicit human-owned window.

When this checklist is complete, leave the repository and every worktree clean, publish the exact safe branch tips, and return a concise completion report with the WIP SHA, phase SHAs, accepted/pending table, evidence-document link, and remaining human seams.
