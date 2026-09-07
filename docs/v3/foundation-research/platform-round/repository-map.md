# Repository and capability map

2026-09-06. Inspected baseline: `b1b18a1aa59868c4056a730ffc5474ac0f272c10`.
The Owner's platform clarification governs the first usable release under `docs/v3`.
"Implemented" below means source exists; test passes and deployment are separate evidence.

## Reusable substrate

| Source at baseline | Existing behavior and evidence boundary | Reuse or revision |
|---|---|---|
| [M1A canonical validation](../../../../scripts/v3/planning/validation/canonical.py), `canonical_bytes`, `seal`; [contracts](../../../../scripts/v3/planning/validation/contracts.py), `validate_dag` | Strict wire/identity validation, DAG and scope checks; pure Python code | Reuse semantics and frozen vectors; not a language selection or persistent writer |
| [M1A replay](../../../../scripts/v3/planning/replay/kernel.py), `genesis`, `reduce`; [conformance](../../../../scripts/tests/v3/planning/conformance.test.py) | In-memory event projection, immutable packet derivation and exact replay fixtures | Extend model mapping; runtime durability remains unimplemented here |
| [M1B route oracle](../../../../scripts/tests/v3/execution/reference_oracle.py), `resolve_route`; [conformance](../../../../scripts/tests/v3/execution/conformance.test.py) | Inert route/provider/model/pool/host/sandbox and eligibility checks over supplied descriptors | Good model-free admission precedent; does not prove any upstream-only reasoning workflow |
| [M1C oracle](../../../../scripts/tests/v3/integrity/reference_oracle.py); [conformance](../../../../scripts/tests/v3/integrity/conformance.test.py) | Inert effect/fence/admission/goal/policy/route/budget identity and ambiguity cases; side-effect counters remain zero | Reuse constraints and red fixtures; not real resource fencing or the broad writer rehearsal |
| [Execution fabric](../../../../scripts/execution_fabric.py), `resolve_placement`, `PoolStatus`, `RoutingPolicy` | Existing v2 separation of account, model, pool, engine, host and assignment; deterministic rejection trace | Adapt behind v3 contracts; no hidden dependence on model inference in placement |
| [Execution fabric](../../../../scripts/execution_fabric.py), `PlacementGovernor`, `DurableFabricStore` | Governor's reservations explicitly ephemeral; fabric journal persists its own lease/attempt/result state | Durable aggregate reservations and a common fence still need design/proof |
| [Remote backend](../../../../scripts/remote_backend.py), `begin_attempt`, `reconcile_attempt`; [remote tests](../../../../scripts/tests/remote-hardening.test.py) | Intent-before-I/O, idempotency, no resend of unreconciled attempt, landed/not-landed/unknown | Reuse attempt semantics; not proof of cross-OS continuation or an old worker's inability to act |
| [Engine resolver](../../../../scripts/resolve-engine.py), [connector resolver](../../../../scripts/resolve-connector.py), [assignment resolver](../../../../scripts/resolve-assignment.py) | Existing manifest validation and launch/transport/assignment planning | Characterize and reuse deterministic resolution; v3 scope/template composition needs its own model |
| [Execution fabric](../../../../scripts/execution_fabric.py), `IntegrationCoordinator` | Serializes per-project candidate admission with source/assignment/verification binding; no Git operations | Reuse accepted-result gate; publication and common writer migration remain separate |
| [Current/migration audit](../../CURRENT-AND-MIGRATION.md), [M1C campaign](../../M1C-CONSTRUCTION-CAMPAIGN.md) | Task, assignment, run/evidence, accepted-result and fabric stores lack a common writer fence | OR-015 remains blocked; fabric-only fixtures cannot remove this gap |

Links resolve from this nested research directory. Source/test claims were inspected; final
documentation gates rerun the frozen suite. No running deployment was inspected.

## Requirements to evidence, ownership and next check

R = shared runtime; A = engine/provider adapter; X = supported upstream extension; N = native
loop. These owners are proposed implementation assignments, not claims that features exist.

| ID | Owner requirement | Existing foundation | Disposition / ownership | Decisive next check and milestone |
|---|---|---|---|---|
| scope | Common configurable platform; first usable new v3; terminal first | PRODUCT, ARCHITECTURE, OR-018/019 | Revise narrower release prose; R+A+X+N | All six deliverables trace to this release; preparation |
| audiences | Developer first, approachable novice operation, eventual organizations | PRODUCT; prior audience evidence | Reuse jobs; market demand unproven | Four scenario outcomes and setup comprehension; release / later tenancy |
| native | Independently useful direct-model native loop | Optional-loop proposal; no implemented v3 loop | Required first release; N behind R | Native-only synthetic task and ten-control trial; integration then release |
| upstream | Independently useful supported upstream harness | Typed engine requirements and historical matrix | Strengthen required coverage; R+A+X | Harness-only task with no hidden direct connection; integration then release |
| combined | Stages/roles cross eligible execution paths coherently | WorkPacket, Route, ContextCapsule, effects | Reuse identity; transition proof missing; R+A+X+N | Route change with pending input/config/reservations; release |
| roles | All reasoning roles explicitly executed/accounted | Head/ARM identity and provider-neutral direction | Add role dependency closure; R+A+N | Missing summarizer/reviewer route fails before execution; integration |
| idle | Persistent runtime without continuous inference | Event-driven actor and resource contracts | Already specified, unmeasured; R | Idle call trap, CPU/RSS/wakeups/write growth; release |
| controls | Ten interactive CLI capabilities | CLI/terminal/broker contracts, partial upstream source evidence | Define common observable semantics; R+A+X+N | Ten rows in interaction contract tested alone and combined; release |
| coverage | Maximum useful common and unique engine features | Capability negotiation; command bridge proposal | Investigate richer supported extension combinations; A+X | Compare basic wrapper, rich adapter and extension composition; integration |
| configuration | Engines/tools/context/memory/routing/delegation/verification/scheduling/placement/policies | CLI schema/provenance/lifecycle and v2 resolvers | Add profile/workflow/account relations and per-field merge; R+A+X+N | Contradictory scopes, switch engine/host, inspect compiled settings; early interface |
| plugins | One user config, different native/upstream implementations | Manifests, grant dimensions, lazy plugins, staged reload | Add multi-implementation capability contract; R+A+X+N | Same command semantics across two pipelines; unsupported translation exposed; release |
| setup | Assisted setup/import/preview/guided repair | Model-free wizard and optional assistant proposal | Accepted product experience; mechanics unproven; R+A+N | First-auth/offline path and assistant on upstream-only route; release |
| updates | Effective time, compatibility and recovery | Digest-bound staged reload, rollback proposal | Reuse contracts; release/state rollback proof missing; R+A+X | Incompatible plugin, active task and failed schema transition; release |
| remote | Authorized cross-device control and compatible placement | Terminal detach and v2 remote/fabric primitives | New end-to-end v3 proof required; R+A | Windows/Linux worker and coordinator faults; release |
| resources | PCs, servers, GPUs, approved cloud; macOS opportunity | HostRegistration, PoolStatus, PlacementRequirements | Expand profile comparison without enrolling machines; R+A | Placement/transfer/failure costs on compatible tasks; release / expanded certification |
| continuity | Identity/grants/input/budgets/artifacts/verification survive transitions | Capsule, M1 evidence and remote-attempt vocabulary | Preserve together; old-worker fencing unproven; R+A+X+N | Partition with old worker alive, lost receipt, backup restoration; early model / release |
| optimization | Whole-workflow context/session/evidence/delegation/capacity/placement/verification/idle improvements | CONTEXT, TELEMETRY, PERFORMANCE-PLAN; unrun experiments | Reuse full vector; add interactions and direct-engine comparison | Trials include all attempts, model roles and human review; release |
| priorities | Responsiveness > subscription efficiency > task completion, within hard floors | OR-017 previously equal treatment | Supersede default ranking; retain full vector and visible tradeoffs | Paired metrics and preregistered practical tolerances; measurement |
| eligibility | Provider/engine/interface/auth/billing/host separate; usage/distribution distinct | Route/M1B catalog and source records | Source refresh and richer route schema; R+A | Exact context-specific eligibility record independent of technical test; integration |
| innovation | Seek mechanisms beyond current framework choices | Prior kernel/workflow/plugin/context research | Open reuse/adapt/build comparison; implementation unselected | Every candidate maps to mechanism, substrate, test and removal rule; roadmap |
| sequence | Formal model -> languages -> storage, with earlier small integration probes | E-FHAR2-101 and existing comparison protocols | Preserve; probes must not become production selection | Contract counterexamples before freeze, equal neutral vectors afterwards |
| later | Dedicated GUI, advanced infrastructure and distributed inference | Deferred GUI/hosted-tenancy scope | Keep explicit milestones; no implied launch dependency | Capability-demand and measured-value admission at later milestone |

Canonical references: [PRODUCT](../../PRODUCT.md), [ARCHITECTURE](../../ARCHITECTURE.md),
[CLI](../../CLI.md), [EXECUTIVES](../../EXECUTIVES.md),
[PLUGINS-AND-EDITIONS](../../PLUGINS-AND-EDITIONS.md), [CONTEXT](../../CONTEXT.md),
[TELEMETRY](../../TELEMETRY.md), [PERFORMANCE-PLAN](../../PERFORMANCE-PLAN.md).

## Consequential revisions

The small deterministic kernel remains compatible with a comprehensive platform: the large
capability surface need not all be privileged code. Owning the native loop is now required;
writing every library from scratch is not. An SDK running an upstream vendor's loop remains
upstream execution even when embedded in a Recursion process.

The old foundation verdict and ten pending questions describe September 5. New accepted
Owner requirements supersede optional-native and equal-default-priority wording. They do not
choose a language/store, certify an engine, approve a new authentication route, resolve the
model/broker proof split or authorize deployment. The historical evidence remains recoverable.
