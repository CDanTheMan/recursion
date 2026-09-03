---
title: Recursion v2 current architecture and v3 migration map
status: evidence-grounded proposal
last-updated: 2026-09-03
baseline-commit: 98113d6c6d3debe2a4d207c51bb1780f7356d714
---

# Recursion v2 current architecture and v3 migration map

This document maps the accepted v2 source baseline to the proposed v3 design. It does not
claim that the current deployment matches the repository. No deployment host was inspected
during this campaign, so deployment state is `unknown`.

## Evidence boundary

The repository was inspected at `98113d6c6d3debe2a4d207c51bb1780f7356d714`.
The v2 source-only acceptance command, `python -u
scripts/tests/recursion-v2-mvp.test.py`, passed on 2026-09-03. A repository-wide caller
search found no consumer of `MVPOrchestrator` outside the MVP modules and tests. These facts
establish tested source behavior, not live enablement.

| Layer | Observed source path | Status at the baseline | Important boundary |
|---|---|---|---|
| Periodic supervisor | `loop/supervisor/run.sh` | operational-path source | Produces bounded briefs with Hermes; it is not the v2 MVP orchestrator |
| Head decision | `scripts/hermes-decide.sh` -> `scripts/decision-queue.py` -> `scripts/conduct-hermes.sh` | operational-path source | Model emits a validated decision; deterministic code actuates a fixed verb |
| Project executive | `scripts/project-pilot.py` plus pilot/goal/plan records | operational-path source | Current Project Pilot is a candidate compatibility predecessor, pending Lucas's ARM ruling; it is not a first-class `ArmRun` |
| Reconciliation | `scripts/project-reconcile.py` | operational-path source | Reconciles goal/task/run evidence and schedules bounded work |
| Worker and gate | `scripts/work.sh`, `worker-sandbox.sh`, assignment and evidence validators | operational-path source | Exclusive worktree, scope check, gate, distinct verifier, candidate binding |
| Publication | `scripts/publish.sh` | operational-path source | Separate fail-closed publisher; review branch only |
| V2 contracts/kernel | `mvp_contracts.py`, `mvp_kernel.py` | source-only, tested | Strict bounded packet graph and authority-subset checks; maximum task depth 2 |
| V2 placement/integration | `execution_fabric.py` | source-only, tested | Deterministic placement, durable leases/recovery, verification receipts and integration intent |
| V2 composition | `mvp_orchestrator.py` | source-only and test-only | Composes authority, placement, verification and review intent; no non-test runtime caller found |
| V2 adapters/control | `mvp_adapters.py`, `mvp_control_surface.py` | source-only, tested | Five adapter contracts; commands produce intents and do not mutate canonical state directly |
| Remote adapters | `remote_assignment.py`, `remote_backend.py`, `cursor-cloud-adapter.py`, `grok-bot-dispatcher.py` | source-only/test-only; live status unknown | Loadable manifests and human enablement are absent from the baseline; fake-transport controls are primary evidence |

`operational-path source` means code participates in the repository's configured execution
path. It does not mean deployed or currently enabled. `source-only, tested` means its
contract is executable and the documented gate passed, but the normal execution path does
not invoke it. `test-only` means the only caller or exercised transport found is a test.
`proposed` is reserved for v3 design with no current implementation. `deployed` requires
direct live-host evidence; no row in this campaign has that status, so deployment is
explicitly `unknown`. Historical audit documents are provenance, not a live observation.

## Exact source and test anchors

These anchors make the source classification reproducible without treating prose as runtime
evidence.

| Concern | Source symbols or shell entry points | Test evidence |
|---|---|---|
| Head decision/actuation | `hermes-decide.sh::build_brief`; `decision-queue.py::enqueue`, `claim`, `transition`; `conduct-hermes.sh::drain_queue` | `scripts/tests/decision-identity.test.py`; `scripts/tests/hermes-conductor.test.sh` |
| Project Pilot/reconciliation | `project-pilot.py::execute_value`; `project-reconcile.py::commit_reconcile_transition`, `admit_work`, `reconcile` | `scripts/tests/project-pilot-status-fail-closed.test.py`; `scripts/tests/hermes-pilot-phase8-red.py` |
| Worker/gate/evidence | `work.sh::fresh_window_admission`, `make_phase5_assignment`, `scope_check`, `verify`, `run_independent_verifier`; `worker-evidence.py::validate_execution_evidence` | `scripts/tests/phase5-runtime-contract.test.py`; `scripts/tests/worker-evidence-assignment.test.py` |
| V2 contract/kernel | `mvp_contracts.py::validate`, `validate_cross_records`; `mvp_kernel.py::TaskPacket`, `_build_packet_impl`, `_spawn_child_impl`, `validate_packet` | `scripts/tests/mvp-contracts.test.py::MvpContractsTest`; `scripts/tests/mvp-kernel.test.py::KernelTest` |
| V2 fabric | `execution_fabric.py::resolve_placement`, `DurableFabricStore`, `PlacementGovernor`, `verify_candidate_result` | `scripts/tests/execution-fabric-phase8.test.py::FabricPlacementTests`, `DurableStateTests`, `IntegrationTests` |
| V2 composition | `mvp_orchestrator.py::MVPOrchestrator.dispatch`, `verify`, `review_intent` | `scripts/tests/mvp-orchestrator.test.py::OrchestratorTest`; repository-wide import/caller search |
| V2 adapters/control | `mvp_adapters.py::negotiate`, `_build_dispatch_plan_impl`, `record_result`; `mvp_control_surface.py::handle_command`, `evaluate_watchdog` | `scripts/tests/mvp-adapters.test.py::AdapterTest`; `scripts/tests/mvp-control-surface.test.py::ControlSurfaceTests` |
| Remote attempts | `remote_assignment.py::validate_assignment`; `remote_backend.py::begin_attempt`, `reconcile_attempt`, `write_session`, `write_usage` | `scripts/tests/cursor-cloud-adapter.test.py` fake transport; `scripts/tests/remote-backend.test.py` |
| Publication | `project-reconcile.py::publish_task`; `publish.sh::publish_one` | `scripts/tests/hermes-pilot-phase6-red.test.sh`; `scripts/tests/cursor-cloud-adapter.test.py` publication-ref refusals |

The clean aggregate `scripts/tests/recursion-v2-mvp.test.py::MVPCompletionTests` passed on
2026-09-03 and composes the focused suites. Its success is source evidence only.

## Current control flow

```text
owner instruction / scheduled supervisor input
  -> Head Hermes text decision
  -> schema validation + durable decision queue
  -> deterministic conductor
  -> Project Pilot goal/plan/window authority
  -> project reconciler
  -> work.sh assignment + isolated worktree + engine
  -> scope/gate + independent verifier evidence
  -> publication decision
  -> publish.sh review branch
  -> owner review/merge/deploy
```

The source has multiple intentionally narrow stores and projections: Markdown task/goal
records, JSON/JSONL runtime records, Git refs/commits, lock directories and process evidence.
That is not automatically incorrect, but it makes global replay, schema migration and
single-writer ownership difficult. V3 must not add SQLite as another writable truth beside
these stores.

## V2 to v3 traceability

| V2 mechanism | Preserve in v3 | Gap to close | Migration proof |
|---|---|---|---|
| Lucas is final authority; model proposes and code actuates | unchanged | Represent the boundary in every command/event envelope | Forbidden verb and authority-widening fixtures fail before append/effect |
| Project Pilot plan, goal and window | goal-scoped `ArmRun` | Durable executive identity, lease, checkpoint, escalation and model replacement | Import fixture projects the same authority; restart does not change actor identity |
| Immutable task plus assignment records | `TaskNode` and `WorkPacket` | One versioned cross-record graph and explicit parent goal/executive | V2 fixture round-trips or produces a typed incompatibility |
| Child path/capability/budget subset | unchanged invariant | Generalize beyond the v2 depth-two MVP without unbounded recursion | Property tests prove every descendant is a non-widening subset and depth/branch limits are enforced |
| Engine/provider/model/pool/host/sandbox attribution | `Route` and `RouteLease` | Remove hard-coded executive identity and keep billing/account distinct | Every dispatch has one explicit route resolution and no implicit pool/provider fallback |
| Durable lease, result and restart reconciliation | canonical event/action protocol | Unify overlapping attempt/lease implementations | Crash and duplicate delivery replay to one terminal outcome without a repeated external effect |
| Independent verifier receipt | `EvidenceBundle` plus verifier assignment | Clean-room evidence and risk-scaled verifier policy | Implementer cannot mint verifier identity; exact candidate/source/gate bindings rederive |
| Review intent separate from publication | unchanged invariant | Publication provenance as a required v3 object | Only the publisher actuator can emit a review publication receipt |
| PAUSE checks across scripts | one kernel-owned policy transition | Define immediate emergency stop versus safe-checkpoint model swap | Race tests prove no new effect admits after the pause epoch |
| Project/source status files and Git ledger | read-only compatibility projection | One canonical event writer without erasing human-readable views | Projection rebuild and diff against frozen v2 fixtures are exact |
| Remote assignment secret references and ambiguous-attempt refusal | unchanged invariant | Signed node envelopes, fencing and enrollment | Replay, stale epoch, disconnect and credential-scope fault suite passes |
| MVP supervisor `executive_identity = hermes` | preserve Hermes logical role | Separate actor identity from selected model/provider | Compatibility reader maps the literal; v3 schema does not route on that literal |

## Single-writer strangler sequence

### Owner-selected first rehearsal

The first cutover rehearsal targets the **local execution-attempt/lease aggregate** only. It
uses synthetic work and no network, provider, publication, credential or deployment effect.
Before the rehearsal, enumerate and freeze every applicable legacy writer across `work.sh`,
assignment/run evidence and the MVP fabric lease/result stores. If ownership cannot be made
exact, stop rather than selecting a convenient subset.

The 2026-09-03 source audit reached that stop condition for the broad aggregate. It found
separate mutation paths for task lifecycle, assignment persistence, run/evidence, accepted
results and fabric lease/result state; `work.sh::set_status` also retains a direct task-file
fallback. No common monotonic writer epoch fences those paths, and the fabric store has no
non-test production caller in the inspected baseline. The owner-selected rehearsal is therefore
**not ready to execute** and is not silently redefined.

The later proposed M1C may use a smaller **fabric-only state-contract requirement fixture** around
`DurableFabricStore`, with immutable assignment input and no task, run/evidence, result-ledger,
remote, Git or publication writes. That fixture proves schema/replay/fault vocabulary only; it
is not a cutover, does not satisfy OR-015 by itself and must not be reported as the local
execution-attempt/lease rehearsal.

The gate requires exact canonical replay parity, one enforced fencing epoch, duplicate/stale
lease refusal, crash recovery at every transition, backup/restore and a proven return to the
frozen legacy writer without repeating work. Concurrency, retry count, fixture volume, resource
limits, verifier tier and optional model assistance are schema-configurable. The default gate is
deterministic and zero-model; model calls may analyze evidence but cannot be required to prove
replay or spend subscription quota merely to rerun the rehearsal.

1. Freeze representative v2 fixtures and their source commit. The first v3 code reads only
   synthetic or copied fixtures; it does not touch operational state.
2. Define v3 object/event schemas and a pure compatibility reader. Reject unknown or
   lossy fields explicitly.
3. Replay fixtures into an in-memory projection and compare a canonical digest. This tests
   interpretation without creating a second writer.
4. Add a shadow reader against a copied state snapshot. Record disagreements; do not repair
   the legacy store from v3.
5. Define aggregate boundaries and a write-ownership table. A cutover may transfer one
   aggregate only after every legacy writer for that aggregate is fenced.
6. During dual-read, exactly one side writes. Cross-aggregate invariants use an explicit
   bridge event and are tested before cutover.
7. Rollback re-enables the old writer only from the last verified compatibility checkpoint;
   it never merges two independent histories.
8. Remove a compatibility path only after replay, backup/restore and rollback evidence has
   survived a private canary.

## Proposed write-ownership inventory

This is the minimum inventory a construction task must verify against its exact starting
commit and, under separate authority, any live deployment. `Unknown` blocks a cutover.

| Aggregate/effect | Baseline writer(s) and store | Fence condition before v3 admission | Proposed v3 ownership and rollback boundary |
|---|---|---|---|
| Head decision lifecycle | `decision-queue.py::enqueue/claim/transition`; decision journal plus pending/running/terminal projections; `conduct-hermes.sh` actuates | Stop legacy admission, reconcile every claimed decision, bind the last journal identity, then make compatibility views read-only | Kernel event writer owns decision state; fixed actuator remains post-commit. Before an external effect restore checkpoint; after an ambiguous effect reconcile forward |
| Project goal/plan/window | `project-pilot.py::execute_value` and `project-reconcile.py::commit_reconcile_transition`; project/pilot/goal/task/event files | Quiesce both writers for the selected project aggregate, import exact digests, prove projection parity, then reject legacy mutation | Kernel owns `GoalSpec`/`ArmRun` events only after Lucas ratifies ARM semantics; legacy files become read-only projections |
| Worker assignment/run/evidence | `work.sh` plus `assignment.py::persist_assignment`, `worker-evidence.py`, run/task/evidence files | First-rehearsal target together with the local MVP fabric row: admit no new legacy run for the synthetic task class; enumerate/fence every applicable writer, terminalize or quarantine every existing run and bind worktree/source state | Kernel owns the synthetic local attempt/lease/result state only after exact replay/crash/rollback proof; engine adapter owns no canonical writes. No external effect is permitted |
| MVP fabric lease/result/verification | `execution_fabric.py::DurableFabricStore` and `VerificationReceiptStore`; fabric JSONL/receipt stores | First-rehearsal target together with local worker assignment: prove no non-test runtime caller or, if later found, stop it and reconcile all leases before import | Treat baseline records as synthetic fixture shapes, not live truth. V3 writer starts only after replay equivalence, fencing and rollback proof; no dual journal |
| Remote attempt/session/usage | `remote_backend.py::begin_attempt/reconcile_attempt/write_session/write_usage`; per-backend journals/projections | Verify deployment/manifest state; disable new remote mutation, reconcile every open/ambiguous attempt, advance the fencing epoch | Kernel owns attempt state; transport returns observations. Any possibly accepted remote request is reconciliation-only |
| Publication and Git ref effect | `project-reconcile.py::publish_task` creates intent; `publish.sh::publish_one` is the sole review-ref writer | Drain or reject legacy publication intents, bind exact candidate/source/ref, keep PAUSE and protected-ref guards active | Kernel owns publication intent/receipt state; one publisher actuator owns the Git effect. A pushed review ref is never "rolled back" by state restoration |
| Cross-aggregate transition | Current reconciler/conductor coordinates file and Git mutations across the rows above | Name the source and destination aggregates, persist a bridge/saga id, and allow only one side to advance each step | Kernel saga/outbox owns coordination; each aggregate retains one writer. Ambiguity blocks the dependent effect until reconciled |

The exact writer audit must also include `taskctl.sh::_set_fields/transition_fields/emit_event`,
Project Pilot and reconciler transition writers, `work.sh::set_status` fallback,
`work.sh::make_phase5_assignment`, `assignment.py::persist_assignment`,
`taskctl.sh::_persist_assignment_locked`, `worker-evidence.py`, the
`validate-assignment-result.py --record` result ledger, `DurableFabricStore`,
`VerificationReceiptStore`, remote attempt/session/usage journals and the publisher. The
machine-readable allowlist must reject a new or renamed writer rather than rely on this prose.

## Failure and rollback rules

- A projection mismatch is a blocker, not a best-effort conversion.
- An unknown deployment version remains `unknown`; repository history never fabricates live
  status.
- Shadow-read success does not prove write contention, liveness or crash recovery. Those
  require separate fault tests.
- Compatibility adapters may translate records, but may not authorize, publish, spend,
  resolve credentials or write both systems.
- Before any runtime cutover, the rollback boundary is the frozen source/state checkpoint
  plus a tested reverse compatibility reader. After an irreversible schema or effect, stop
  and require owner approval rather than promising rollback.

## Recommended cutover decision rule

Fence a legacy writer for one aggregate only at an explicit maintenance checkpoint where all
of the following are proven against the exact deployment revision:

1. Every legacy admission and mutation path for that aggregate is enumerated and can be
   mechanically refused.
2. No active lease, open or ambiguous external attempt, pending publication intent, partially
   applied cross-aggregate saga or unspooled disconnected-node result remains.
3. The frozen legacy source/state digest imports into v3 and rebuilds the expected projection
   without lossy or best-effort fields.
4. Backup/restore, reverse compatibility reader and rollback admission have passed against the
   same fixture.
5. A new fencing epoch makes stale legacy or remote writes fail closed.
6. The selected canary aggregate is low risk, owner approved and independently monitored.

Before the first externally accepted effect, rollback may restore the last verified checkpoint
and legacy writer. Once a provider submission, pushed ref, sent message, credential operation,
deployment or service change may have been accepted, state restoration cannot undo reality:
retain the v3 record, block dependent effects and reconcile forward. The exact effect taxonomy
and canary aggregate still require research and Lucas's final decision.

For the no-effect state contract, the canonical event envelope contains aggregate type/id,
contiguous sequence, event/command/idempotency/causation identities, writer id, fence epoch,
logical time, previous/current digests, schema version and typed payload. A full rehearsal
cannot proceed until every included legacy writer can be mechanically refused and the same
epoch is checked at admission and execution. Shadow projection equality alone does not satisfy
that proof.

## Material uncertainties

The live deployment revision and enabled feature set were not inspected. The current Project
Pilot-to-ARM semantic mapping is an evidence-backed proposal, not a ratified rename. V2's
source gate demonstrates strong safety behavior but not production performance or operational
use. These limits are retained in [CLAIM-LEDGER.md](CLAIM-LEDGER.md).
