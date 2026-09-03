---
title: Recursion v3 plugins and editions hypothesis
status: hypothesis
last-updated: 2026-09-03
---

# Recursion v3 plugins and editions hypothesis

## Boundary

V3 should be extensible like a modern harness without making its integrity constitution replaceable by an ordinary plugin.

### Privileged kernel

The small kernel owns:

- identity and authority verification;
- GoalSpec and Owner Intent integrity;
- event ordering and canonical state writes;
- parent/child budget inheritance;
- executive and worker leases;
- PAUSE and revocation;
- evidence/provenance admission;
- publication boundary;
- plugin capability enforcement.

### Capability plugins

Plugins may provide:

- native/external agent engines;
- providers and model catalogs;
- subscription/API/local capacity telemetry;
- routing heuristics;
- context sources and repository indexes;
- compaction strategies;
- gates and verifiers;
- node transports;
- sandboxes and permission mappings;
- notifications, observers, UIs, and editors;
- artifact stores and optional telemetry exporters.

The research campaign challenged this boundary. Anything moved into the kernel pays a permanent complexity and security cost; anything moved out must not be able to weaken invariants. Routing plugins may score or reorder only routes the kernel has already found eligible; the kernel revalidates every proposed route and rejects any authority, privacy, billing, or capability expansion.

## Capability graph

Plugins compose through a deterministic, versioned capability graph rather than mutating global behavior.

Each manifest declares:

- plugin and protocol version;
- provided and required capabilities;
- exclusive resources and conflicts;
- configuration schema fragment;
- durable and ephemeral event subscriptions;
- process/isolation mode;
- filesystem, network, credential, and model access;
- CPU, memory, disk, and concurrency envelope;
- lifecycle hooks and health probes;
- provenance, license, integrity digest, and update source.

Resolution produces a cached graph and a complete rejection explanation. Cycles, incompatible ownership, ambiguous providers, and missing dependencies fail before autonomous work starts.

## Event bus

Inter-plugin coordination uses typed kernel events, not direct plugin-to-plugin calls.

- Durable lineage events are ordered, authenticated, replayable, and schema migrated.
- Ephemeral operational events are bounded, backpressured, sampled where appropriate, and disposable.
- Plugins receive only event types and fields permitted by their manifest and project classification.
- Field values, identifiers, payload sizes, timing, and subscription patterns are part of the disclosure analysis; redacting obvious text is not sufficient for a public observer.
- One faulty plugin cannot block the durable writer indefinitely.

## Failure containment

Plugins have circuit breakers, bounded queues, timeouts, restart budgets, and explicit degraded modes. Failure handling should:

1. stop admitting work that requires the failed capability;
2. preserve active checkpoints and canonical state;
3. retry only within a bounded policy;
4. select an already approved equivalent capability if policy permits;
5. quarantine the plugin when integrity or repeated failure warrants it;
6. escalate without globally stopping unrelated projects.

The kernel, state writer, PAUSE, and owner CLI remain usable when an optional plugin fails.

## Resource Discipline Contract

Every optional subsystem declares and proves:

- idle CPU and memory ceiling;
- startup and steady-state latency budget;
- disk growth and retention behavior;
- worker/concurrency limits;
- event and polling frequency;
- overload shedding behavior;
- unload/restart semantics;
- performance regression gate for its supported edition.

The resource governor sheds expendable caches, background indexing, speculative planning, and optional observers before integrity, active checkpoints, required gates, or owner control. Exact ordering is configurable within those priorities.

## Editions

One source tree produces versioned release manifests:

| Edition | Intended surface |
|---|---|
| `core` | kernel, local state, Git/worktree execution, one basic provider/engine path, CLI |
| `standard` | common CLI/provider integrations, planning, context, telemetry, local verification |
| `remote` | node enrollment, authenticated transport, remote execution and observation |
| `full` | all first-party plugins and advanced policies |
| `custom` | schema-validated owner-selected plugin set |

Edition manifests lock exact plugin versions and defaults. Installation should not download or start disabled heavy plugins. A user can add/remove plugins later without migrating to a different product.

## Distribution and updates

- Built-in registry plus filesystem/Git/package sources, each pinned to an immutable digest before activation.
- Lockfile with digest and transitive dependency resolution.
- Reproducible offline installation from a bundle.
- Signed first-party releases. Third-party publisher trust policy is owner-selected, but unsigned or unverifiable code defaults to unprivileged isolation and cannot receive kernel-adjacent capability without a separate explicit owner decision.
- Update proposal, staging, verification, and rollback separate from agent authority.
- No mandatory centralized marketplace or remote kill switch.

## Feature Admission Contract

Before a feature or plugin enters the roadmap, record:

- user problem and measurable benefit;
- why configuration or an existing plugin cannot solve it;
- kernel versus plugin justification;
- resource and complexity cost;
- privacy, security, and authority effects;
- failure containment and uninstall story;
- acceptance benchmark;
- provenance and license compatibility;
- default enabled/disabled state by edition;
- falsifier and removal criteria.

This is the primary defense against an ambitious v3 becoming slow, opaque bloat.
