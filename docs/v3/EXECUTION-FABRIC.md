---
title: Recursion v3 execution fabric hypothesis
status: hypothesis
last-updated: 2026-09-07
---

# Recursion v3 execution fabric hypothesis

## Role execution and accounting closure — proposed 2026-09-07

MKR-002/MKR-008 extend the existing Route/WorkPacket projection, not the M1 wire schema.
Admission resolves every model-using dependency before starting the workflow:

| Role | Native execution path | Upstream-only execution path | Accounting binding |
|---|---|---|---|
| Head/ARM planning | Admitted native model call | Eligible bounded harness session producing a validated proposal | Goal pool and planning reservation |
| Implementation | Native model/tool loop | Supported upstream session and scoped tools | Task attempt plus descendant reservations |
| Review | Separate eligible native verifier | Clean eligible harness verifier session | Review reserve and exact independence class |
| Summarization/memory | Deterministic extraction or explicitly bound model | Harness-native transform or eligible summarizer session | Context-service reservation, including failed transforms |
| Recovery analysis | Deterministic reconciliation or admitted model | Eligible recovery session only within the remaining cap | Cumulative recovery ledger |
| Setup assistance | Deterministic wizard first; optional admitted model | Optional eligible setup session | Explicit setup allowance; never necessary to boot |
| Consultation | Admitted role session | Eligible assistant/harness session | Parent consultation/depth budget |
| Learned routing/retrieval | Optional explicit model route | Eligible bound helper session | Router/retrieval reservation; deterministic alternative when equivalent |
| Hidden auxiliaries | Explicitly catalogued classifier/title/vision/helper | Harness feature enabled only with an eligible documented path | Same explicit pool ledger; unknown usage is not zero |

Each binding records role/run/goal version, provider/model, executing harness, interface/build,
credential reference, billing pool/unit, host, effective config, tools/grants, verification class,
observation source and conservative reservation rule. Included subscription capacity and API
spending are distinct units. Provider reset timestamps change availability, not task budgets.
Internal child usage must be counted once without losing parent lineage.

An upstream-only configuration must complete the required dependency closure with direct API
credentials absent. A helper that discovers a different provider, asks for a second key or
silently uses a metered pool fails admission. Unknown counters require a documented conservative
bound or a visible blocked configuration; they cannot become zero-cost calls. Same-provider
review is usable only under its permitted independence class. See the source-specific limits
in [the integration matrix](foundation-research/mark2-research/compatibility.json).

Ordinary persistence, scheduling, health observations, queueing, configuration compilation,
accounting and status are deterministic and event driven. Model inference is invoked for bounded
semantic work. A provider session can accelerate continuation; it is not the canonical writer,
authority source or scheduler. Native and upstream implementations share the same integrity path.

## Native and delegated engine accommodation — proposed

A provider adapter maps inference requests and billing fields; an engine adapter maps another
harness's lifecycle/tools/session; a Recursion plugin contributes optional admitted behavior.
Keep these identities separate. The common command bus owns canonical admission; engine events
are evidence inputs. Optional controls require explicit versioned capability negotiation.
The [foundation matrix](foundation-research/compatibility.json) distinguishes queued input,
active steering, question/approval exchanges, cancellation, native resume and recovery. FND-004.

Before any governed dispatch, bind packet/goal/plan/policy/grant/route and relevant lease/fence
identities. An upstream shell approval does not identify every descendant effect. Restrict or
refuse a route when a task-required fence cannot reach the protected resource. Process termination
remains `not-evaluated` for external effects; unknown outcomes stay ambiguous until reconciled.
M1A metered-spend/publication prohibitions cannot be widened by M1B route vocabulary or M1C
eligibility records. FND-002/FND-003/FND-005.

For future nodes, distinguish client host, authority coordinator, execution host, engine, inference
provider and account pool. Enrollment/revocation, locality and manifest-first transfer are adapter
concerns; one writer per aggregate and reconnect revalidation remain integrity obligations.
Disconnected nodes spool evidence and finish only previously permitted local work; no publication
or authority expansion. Single-user multi-node operation does not imply multi-tenant isolation.
`decision.foundation.remote-scope` and `experiment.foundation.remote` remain pending. FND-013.

## Separation of concerns

V3 resolves an execution route from independent declarations:

```text
task requirements
  + executive policy
  + model capability
  + engine/harness capability
  + provider and transport
  + capacity pool and billing basis
  + credential reference
  + host/node capability
  + sandbox and network profile
  + project privacy and publication policy
  -> immutable resolved route
```

A model is not a provider, a subscription is not a model, a CLI is not a billing pool, and a host is not authority. Keeping them separate lets the same GoalSpec survive subscription, provider, and machine changes.

## Route entities

- **Engine:** native Recursion loop, Codex CLI, Cursor CLI, Claude Code, Gemini CLI, OpenCode, Hermes, or another harness adapter.
- **Provider:** the service that performs inference or local endpoint contract.
- **Model:** a versioned capability description independent of delivery route.
- **Capacity pool:** one subscription, API account/budget, enterprise entitlement, local accelerator, or shared quota domain.
- **Route:** an eligible combination of engine, provider, model, pool, credential reference, and execution mode.
- **Host:** a registered execution node with measured resources and capabilities.
- **Profile:** sandbox, permission, network, context, verification, and resource rules.

One model may be reachable through several routes with different price, quota, privacy, cache, and health state. One CLI may expose several models or providers. Telemetry remains route-aware so it does not attribute Cursor subscription use to an abstract model or treat API and OAuth billing as interchangeable.

## Capacity pools

Capacity is model-aware and account-aware. A pool tracks:

- billing basis: subscription, metered, local, or unknown;
- models and reasoning modes actually exposed;
- concurrent-session and rate-limit observations;
- reset windows or uncertainty bounds;
- recent success, throttling, refusal, and outage signals;
- prompt/context cache evidence when observable;
- reservations and aggregate parent-goal consumption;
- privacy and provider-training constraints;
- health and credential-reference status without storing credentials.

Opaque flat subscriptions use confidence-aware shadow prices based on remaining capacity, resets, recent throttles, and opportunity cost. They must not be converted to fictional dollar prices. Metered pools use real configured prices and hard budget authority.

## Billing boundary

Automatic selection occurs only inside an owner-approved route envelope. Switching from a subscription/OAuth route to a metered API route is not ordinary failover; it is a billing-authority transition and requires existing parent-goal authorization.

The session's proposed default for the private deployment is a single aggregate `$10` metered budget for the parent goal when explicitly granted. It is not renewed per task. Public defaults should grant no metered fallback.

## Routing objective

The router does not simply choose the cheapest or strongest model. It predicts the least scarce eligible route likely to meet the task's quality floor, considering:

- task type, complexity, uncertainty, and risk;
- measured gate success and repair history by route;
- verifier disagreement and downstream review cost;
- context/session affinity and expected compaction cost;
- quota pressure, reset horizon, latency, and local resource load;
- privacy, egress, tool, and permission compatibility;
- reserved capacity for planning, integration, verification, and recovery.

Every route choice produces a deterministic explanation and a recorded feature snapshot. Online learning may reorder already approved routes but cannot add providers, widen authority, enable training use, or increase budgets.

Provider or plugin heuristics propose scores only over the kernel-produced eligible set. The deterministic admission layer validates the selected route again immediately before launch; a heuristic output is never an authorization.

## Checkpoint-driven adaptation

Routes remain stable between meaningful checkpoints. Re-resolution occurs after:

- task completion or decomposition;
- quota/throttle/outage event;
- verified capability mismatch;
- new failure evidence;
- material repository or plan change;
- owner override;
- scheduled capacity reset.

This avoids destroying cache/session affinity through constant micro-routing.

## Concurrency and admission

Admission is hierarchical and adaptive across node, pool, route, model, repository, goal, and review capacity. It:

- reserves configurable CPU/RAM/disk headroom for the OS and controller;
- uses measured task resource classes and foreground-machine activity;
- queues work when the appropriate quality route is unavailable;
- prevents overlapping writers and serializes integration per repository;
- protects capacity for verification and recovery;
- applies backpressure before throttling, lag, branch proliferation, or unreviewed-output growth;
- uses event-driven wakeups rather than polling;
- permits an audited owner override without concealing risk.

The private deployment historically carried an owner policy ceiling of 75 unique unreviewed
branches. Lucas has ruled that v3 uses measured, configurable branch/worktree admission instead
of treating 75 as universal. Signals include disk/inodes, Git/index latency, active process and
worktree cost, integration conflicts, stale age, unreviewed change volume and owner review
service rate. Policy uses hysteresis plus an explicit owner hard ceiling. Automatic pruning
remains limited to branches proven merged, superseded, or content-identical. More machine
headroom never justifies producing evidence faster than it can be reviewed.

## Scheduling

Goals receive priorities and optional reservations. Unused capacity may be borrowed. Interactive work may move ahead of queued autonomous work without killing safe active work. A goal consumes a whole node only when explicitly marked exclusive.

Configurable postures include:

- `quality-wait`;
- `quality-first-adaptive`;
- `throughput`;
- `cost-first`;
- `maximum`;
- owner-defined weighted policies.

## Node fabric

V3 hypothesizes a hub-and-spoke authority fabric:

- one authoritative controller per authority domain/OS account;
- authenticated enrolled nodes with separate controller, executor, observer, and verifier capabilities;
- signed, replay-protected parent-goal envelopes and work packets;
- least-privilege node roles and revocation;
- manifest-first, lazy transfer of content-addressed context and repository evidence;
- local spooling of signed events during disconnection;
- no autonomous authority expansion while disconnected;
- reconciliation through the controller before publication.

An owner authenticated on both devices may execute remote commands when the signed goal, node capability, permission profile, and risk-based step-up requirements permit it. Remote access is protected infrastructure, not a mechanism for locking an owner out of locally installed open-source software.

## Worker and integration flow

```text
ARM TaskNode
  -> exclusive worktree + immutable WorkPacket
  -> eligible native/external harness route
  -> normalized checkpoint/result
  -> controller-owned machine gate
  -> clean independent verification package
  -> evidence-based dispute resolution
  -> serialized integration candidate
  -> publication intent
  -> approved review branch
```

Verifiers receive GoalSpec, exact tree, diff, gates, and observable evidence, but not the implementer's persuasive narrative or hidden reasoning. Disagreement is resolved by collecting discriminating evidence, not model majority vote.

## Evidence hierarchy

From strongest to weakest:

1. exact source/candidate identity and reproducible machine evidence;
2. observed runtime/visual behavior with provenance;
3. independent verifier findings tied to exact evidence;
4. implementation reports and model explanations;
5. unsupported model assertion.

Lower levels may guide investigation but cannot overrule contradictory higher-level evidence.
