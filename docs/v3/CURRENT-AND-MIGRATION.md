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
| Project executive | `scripts/project-pilot.py` plus pilot/goal/plan records | operational-path source | Current Project Pilot is the predecessor of a v3 ARM executive, not a first-class `ArmRun` |
| Reconciliation | `scripts/project-reconcile.py` | operational-path source | Reconciles goal/task/run evidence and schedules bounded work |
| Worker and gate | `scripts/work.sh`, `worker-sandbox.sh`, assignment and evidence validators | operational-path source | Exclusive worktree, scope check, gate, distinct verifier, candidate binding |
| Publication | `scripts/publish.sh` | operational-path source | Separate fail-closed publisher; review branch only |
| V2 contracts/kernel | `mvp_contracts.py`, `mvp_kernel.py` | source-only, tested | Strict bounded packet graph and authority-subset checks; maximum task depth 2 |
| V2 placement/integration | `execution_fabric.py` | source-only, tested | Deterministic placement, durable leases/recovery, verification receipts and integration intent |
| V2 composition | `mvp_orchestrator.py` | source-only, tested | Composes authority, placement, verification and review intent; no non-test runtime caller found |
| V2 adapters/control | `mvp_adapters.py`, `mvp_control_surface.py` | source-only, tested | Five adapter contracts; commands produce intents and do not mutate canonical state directly |
| Remote adapters | `remote_assignment.py`, `remote_backend.py`, `cursor-cloud-adapter.py`, `grok-bot-dispatcher.py` | shipped inert | Loadable manifests and human enablement are absent; fake-transport controls are primary evidence |

`operational-path source` means code participates in the repository's configured execution
path. It does not mean deployed or currently enabled. `source-only, tested` means its
contract is executable and the documented gate passed, but the normal execution path does
not invoke it. Historical audit documents are provenance, not a live observation.

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
| Child path/capability/budget subset | unchanged invariant | Generalize beyond the v2 depth-two MVP without unbounded recursion | Property tests prove every descendant is a strict subset and depth/branch limits are enforced |
| Engine/provider/model/pool/host/sandbox attribution | `Route` and `RouteLease` | Remove hard-coded executive identity and keep billing/account distinct | Every dispatch has one explicit route resolution and no implicit pool/provider fallback |
| Durable lease, result and restart reconciliation | canonical event/action protocol | Unify overlapping attempt/lease implementations | Crash and duplicate delivery replay to one terminal outcome without a repeated external effect |
| Independent verifier receipt | `EvidenceBundle` plus verifier assignment | Clean-room evidence and risk-scaled verifier policy | Implementer cannot mint verifier identity; exact candidate/source/gate bindings rederive |
| Review intent separate from publication | unchanged invariant | Publication provenance as a required v3 object | Only the publisher actuator can emit a review publication receipt |
| PAUSE checks across scripts | one kernel-owned policy transition | Define immediate emergency stop versus safe-checkpoint model swap | Race tests prove no new effect admits after the pause epoch |
| Project/source status files and Git ledger | read-only compatibility projection | One canonical event writer without erasing human-readable views | Projection rebuild and diff against frozen v2 fixtures are exact |
| Remote assignment secret references and ambiguous-attempt refusal | unchanged invariant | Signed node envelopes, fencing and enrollment | Replay, stale epoch, disconnect and credential-scope fault suite passes |
| MVP supervisor `executive_identity = hermes` | preserve Hermes logical role | Separate actor identity from selected model/provider | Compatibility reader maps the literal; v3 schema does not route on that literal |

## Single-writer strangler sequence

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

## Material uncertainties

The live deployment revision and enabled feature set were not inspected. The current Project
Pilot-to-ARM semantic mapping is an evidence-backed proposal, not a ratified rename. V2's
source gate demonstrates strong safety behavior but not production performance or operational
use. These limits are retained in [CLAIM-LEDGER.md](CLAIM-LEDGER.md).
