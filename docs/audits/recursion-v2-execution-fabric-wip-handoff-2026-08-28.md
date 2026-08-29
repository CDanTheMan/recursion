# Recursion v2 execution fabric — WIP implementation handoff

Date: 2026-08-28 (America/Los_Angeles)  
Authority: `docs/plans/recursion-v2-execution-fabric.md`, `CONTROL_PLANE.md`, `ANCHOR.md`, D-015, D-016  
WIP branch: `loop/work/recursion-v2-execution-fabric-wip`

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
