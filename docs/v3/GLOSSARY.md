---
title: Recursion v3 normalized glossary and ownership model
status: proposed-canonical-vocabulary
last-updated: 2026-09-03
---

# Recursion v3 normalized glossary and ownership model

These names remove the main ambiguities discovered in the source and design transcript. A
schema milestone may refine field names, but it should not create a second synonym set.

## Actors and authority

| Term | Definition | Not the same as |
|---|---|---|
| `Owner` | Lucas, the principal and final authority | a model, administrator role or route account |
| `Head Hermes` | Durable portfolio executive directly accountable to the Owner; `Main Assistant` is its UI role name | one provider session or the deterministic kernel |
| `ARM executive` | Durable goal-scoped executive that plans and delegates inside one approved `GoalSpec` | a worker, Project Pilot script or AI ARM Manager |
| `Delegated worker` | Bounded executor of one `WorkPacket` | an executive with authority to redefine the goal |
| `Verifier` | Separately assigned evaluator of exact candidate/gate evidence | the implementer, vendor self-report or publisher |
| `Kernel` | Deterministic authority, event and action enforcement substrate | a semantic manager or planning agent |
| `Principal` | Identity whose signed grant is being exercised | whichever process happens to hold a session |
| `CapabilityGrant` | Versioned subset of parent authority | a tool merely being installed or discoverable |

Head Hermes directly owns ARM lifecycle. An ARM directly owns its task DAG and delegates
workers. The kernel owns neither portfolio priorities nor ARM plans.

## Durable product objects

| Object | Canonical owner | Meaning |
|---|---|---|
| `OwnerIntent` | Owner/authority plane | Exact non-lossy directive plus amendments and source |
| `GoalSpec` | Owner then Head | Immutable versioned goal, scope, non-goals, budget, privacy, gates and stop rules |
| `ExecutiveProfile` | reviewed configuration | Reusable defaults; never active state or authority by itself |
| `ArmRun` | Head creates; ARM advances | One leased execution of a `GoalSpec`, retaining identity across model/session swaps |
| `TaskNode` | ARM | DAG node describing bounded work and dependencies |
| `WorkPacket` | kernel issues from approved task | Immutable executable authority for a worker or verifier |
| `Route` | deterministic resolver | Complete engine/provider/model/account/pool/host/sandbox selection plus explanation |
| `RouteLease` | kernel/capacity pool | Time- and quota-bounded reservation; not entitlement ownership |
| `ContextCapsule` | context compiler | Content-addressed provider-neutral manifest; payload hydration remains policy-scoped |
| `Checkpoint` | kernel records; engine produces observations | Mechanically safe boundary with source, state and evidence bindings |
| `EvidenceBundle` | evidence plane | Candidate, source, gate, usage and independent-verifier bindings |
| `PublicationIntent` | Head/ARM may propose | Request for the sole publisher to create a review artifact |
| `PublicationReceipt` | publisher actuator | Durable result of the reviewed publication path; never a merge/deploy receipt |
| `Node` | installation trust domain | Registered execution host with identity, roles and capability evidence |
| `PluginManifest` | reviewed configuration | Data declaration of capability, dependencies, privileges, lifecycle and version |

## Route vocabulary

| Term | Definition |
|---|---|
| `Engine` | Harness or execution protocol, such as a native loop or external CLI |
| `Provider` | Service that serves a model or remote execution API |
| `Model` | Named model capability selected through a provider |
| `Account` | Credential/entitlement identity; durable records contain only an opaque reference |
| `CapacityPool` | Bounded subscription, metered, local or remote capacity with billing and fallback policy |
| `Host` | Machine on which the engine/process executes |
| `SandboxProfile` | Filesystem, process, network and resource boundary applied to execution |
| `ProviderSession` | Disposable route-local continuity/cache affinity handle; never canonical actor identity |
| `RouteCapabilityDescriptor` | Dated evidence about supported context, tools, controls, billing/privacy unknowns and expiry |

A model listing does not create a route. A route exists only when all required objects resolve
inside current authority. Subscription exhaustion never turns into metered usage implicitly.

## Event and effect ownership

| Category | Examples | Persistence/ordering | Owner |
|---|---|---|---|
| Authority event | goal approved, grant narrowed, pause epoch advanced | durable, globally ordered within authority domain | kernel after authenticated command |
| Executive event | ARM created, plan amended, task proposed, escalation raised | durable per aggregate | Head or ARM proposes; kernel validates/appends |
| Execution event | lease acquired, dispatch admitted, checkpoint reached, result observed | durable and idempotency-bound | kernel plus normalized engine observation |
| Evidence event | gate result, verifier receipt, candidate binding | durable, append-only | gate/verifier identity through kernel |
| Publication event | review intent admitted, review ref published | durable, separate actuator | kernel/publisher |
| Ephemeral signal | token delta, progress frame, sampled CPU, UI cursor | bounded/loss-tolerant unless promoted | engine/observer |
| External effect | model request, process launch, Git ref update, notification | action record before effect; receipt/reconciliation after | one deterministic actuator |

Ephemeral data becomes durable only through an explicit typed promotion. Model prose and
provider self-reports are observations until a trusted gate or reconciler binds them.

## State ownership rule

One aggregate has one writable authority at a time. SQLite/WAL is the proposed future event
and projection store; content-addressed artifacts hold large payloads; Git/Markdown/JSON views
remain configuration, evidence exports or compatibility projections. None may silently become
a second runtime writer. See [CURRENT-AND-MIGRATION.md](CURRENT-AND-MIGRATION.md).
