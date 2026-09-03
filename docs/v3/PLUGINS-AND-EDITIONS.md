---
title: Recursion v3 plugins and editions direction
status: accepted-direction-with-open-trust-research
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
- scholarly/source discovery, DOI/metadata resolution, licensed retrieval, citation/retraction
  checks and reproducible experiment adapters;
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

Every edition shares the common defaults: `checkpoint` PAUSE, trusted bounded autonomy,
digest-aware plugin grants and detachable multi-terminal operation. `standard` adds richer local
orchestration. `full` adds advanced and distributed first-party capabilities. Installing `full`
does not enable maximum `sovereign` authority; that separately named capability preset requires
an explicit owner action and displays its full blast radius.

## Distribution and updates

- Built-in registry plus filesystem/Git/package sources, each pinned to an immutable digest before activation.
- Lockfile with digest and transitive dependency resolution.
- Reproducible offline installation from a bundle.
- Signed first-party releases and maintainer-approved plugins, rooted in the installation trust
  root. A valid signature proves publisher/review-policy identity, not that every requested
  capability is safe for every project.
- Unsigned local plugins remain installable and may implement the complete plugin API. The CLI
  warns that they are not maintainer approved, pins the exact digest and displays all requested
  authority. A configured local policy may let that acknowledgement mint the requested
  digest-aware grants. Plugin model launches, subscription quota, metered spending,
  provider/account use, updates and revocation remain separately visible and configurable;
  their one-step versus staged consent mechanics remain an owner-visible research question.
- Update proposal, staging, verification, and rollback separate from agent authority.
- No mandatory centralized marketplace or remote kill switch.

Signatures, transparency records, provenance and software bills of materials establish
publisher/key role, artifact identity, traceability and freshness only within their threat
models. They do not prove benign runtime behavior, fit for a project, quota entitlement or
spending authority. TUF's target files are opaque to the framework, and SLSA provenance is a
tamper/traceability control rather than a safety verdict. Admission therefore binds the exact
artifact and dependency-lock digests to separate functional, OS, model-launch, route/account,
quota, metered-spend, update and revocation grants.

The lifecycle contract is:

```text
discovered -> inspected -> digest-pinned -> acknowledged -> admitted -> active
                  |              |              |             |
                  +---------- rejected/quarantined -----------+
active -> suspended -> revalidated -> active
active -> revoked -> draining/terminated -> retained-evidence/uninstalled
update-proposed -> staged -> verified -> acknowledged -> activated | rolled-back
```

Revocation blocks new admission immediately. Existing work follows its effect-specific PAUSE
policy and may enter reconciliation; “revoked” does not assert that a remote effect stopped.
A disabled plugin performs no code execution, import, network call, subprocess, background
task, quota debit or spend. The release manifest retains only the minimal identity/capability
metadata needed to explain that absence; omitting installed payload weight does not omit the
capability-resolution contract.

One-step novice acknowledgement may combine only digest pinning, requested functional verbs
and the declared workspace sandbox when local policy permits it. Credentials, network egress,
model launch, quota reservations, route/account access, metered spending, automatic update,
downgrade and grant administration remain individually visible grant dimensions. Lucas has
not yet selected which of those dimensions may share an acknowledgement.

Primary trust anchors opened 2026-09-03 are [The Update Framework
specification](https://theupdateframework.github.io/specification/latest/), [SLSA
v1.2](https://slsa.dev/spec/v1.2/) and [Sigstore signing](https://docs.sigstore.dev/cosign/signing/overview/).
Their guarantees are applied narrowly; no one mechanism replaces Recursion's runtime authority
or acceptance gates.

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
