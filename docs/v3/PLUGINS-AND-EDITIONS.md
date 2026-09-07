---
title: Recursion v3 plugins and editions direction
status: accepted-direction-with-open-trust-research
last-updated: 2026-09-07
---

# Recursion v3 plugins and editions hypothesis

## Mark 3 capability availability and activation — 2026-09-07

OR-039 makes configuration and plugin compatibility central architectural priorities.
Separate a supported capability from its installation dependencies, activation for a task,
default setting and placement in kernel/service/plugin. Lean configurations may defer optional
loading or place it elsewhere; they cannot silently erase accepted capabilities from the release.
Preserve rich configurations, local execution and all four incompatibility response modes.

Compare manifest-based lazy loading, isolated plugin workers and harness-specific adapters,
measuring installed-but-disabled import, connection, process, memory and inference costs.
Plugin boundaries are not automatically faster, safer or cheaper. Compare semantic behavior,
dependency/isolation failure, configuration propagation and rollback alongside resource use.

MCP coverage includes tools, resources, prompts and host interaction, capability/schema
negotiation, discovery, context cost, connections/subscriptions where supported, cancellation,
authentication and accounting. A common protocol name does not prove equivalent host behavior.
Measure explicit composition losses and retain Owner-visible explanations without hidden fallback.

## Behavioral portability and incompatibility — proposed 2026-09-07

MKR-014 replaces a metadata-only notion of conversion with a capability-specific loss map.
Local execution remains required; it separately declares dependency availability, network,
credential, host permission and inference requirements. No inference or installation occurs
during deterministic capability resolution.

| Surface | Preserved meaning | Concrete adapter limit |
|---|---|---|
| Tools | Input/output schemas, typed results, provenance, effect class, grant, idempotency | MCP annotations are untrusted; dropping output schemas/resource links is a recorded loss |
| Resources | URI/version/digest, audience and subscription behavior | MCP context inclusion is host-controlled; a browser snapshot is an observation |
| Prompts/skills | Versioned instruction contribution and invocation rules | Model-selected instructions are not deterministic commands or grants |
| Hooks | Timing, blocking, mutation, failure and cleanup semantics | PreToolUse, compaction and lifecycle hooks differ by host; file ingestion may bypass them |
| Authentication | Credential source, audience, scope, expiry and grant | MCP HTTP tokens, stdio environment, browser cookies and app permissions are different authorities |
| UI | Target/session identity and input/output contract | Terminal, host widgets, browser tabs and CDP child targets are not interchangeable |
| Memory | Explicit context reference, freshness and authority boundary | Persistent browser profiles and conversation state do not become canonical memory |
| Dependencies | Artifact/lock digest, install owner, executable, network needs | Playwright browser/extension and OpenCode startup Bun installs are admitted effects |
| Lifecycle | Ownership, disposal, restart, epoch and settlement | Cordis cleanup and cancellation do not compensate external effects |

Primary mechanisms: SRC-V3-171/SRC-V3-177 through SRC-V3-183/SRC-V3-198/SRC-V3-202.
Chrome debugger permission and child-target handling need separate checks; a closed tab or
revoked extension grant must not trigger relogin, reattachment or rerouting silently.

All four accepted responses retain an inspectable incompatibility marker with requested
capability, adapter/version, missing requirement, translation loss and effective config:

| Response | Proposed behavior on attempted invocation |
|---|---|
| state_incompatibility | Return a typed refusal and leave the marker visible |
| recommend_combinations | Refuse effects and display compatible combinations and their losses |
| no_action | Return a deterministic no-effect receipt; no proactive notification, repair or substitution |
| notify_and_recommend | Same no-effect refusal plus configured notification and compatible suggestions |

A request reaching an incompatible route records `status=incompatible, attempted=false,
effect=none`, meaning no execution was attempted. It may append the local canonical request and
refusal receipt; it performs no plugin import, process/model/tool start, auth, installation,
network repair, reroute, quota use or spend. A failure after an admitted effect instead reports
failed/cancelled/uncertain and cannot reuse this no-effect status. Recommendations never activate
themselves. This is a proposed resolution of the handoff's invocation ambiguity, not a new Owner
answer.

Rich SDK/server/protocol/extension composition is preferred when it meets concrete semantics.
A wrapper remains useful when its declared losses satisfy the workflow. Local browser execution,
a local model and offline operation are independent capabilities. Native and upstream paths
share the same grants and configuration revision rules in [CLI](CLI.md); plugin output enters
as a proposal/observation and cannot write canonical state directly.

## Mark 2 Owner direction — 2026-09-06

OR-029 requires browser/MCP workflows, adaptation of other harness plugins and a local execution path even when the chosen upstream route is incompatible. Preserve the inspectable incompatibility marker and four configurable responses: state incompatibility, recommend combinations, no action, notify and recommend. Local execution does not establish offline operation, universal conversion or automatic fallback. Support both configuration-propagation choices; OR-033 adds six update modes and compatible recovery preserving newest work. Exact mechanics and presets remain in the [Mark 2 research mandate](foundation-research/mark2/handoff.md).

## Platform plugin requirement — accepted 2026-09-06

OR-023 makes configurable extension behavior foundational. Investigate one user-facing schema
with distinct native-loop and supported upstream implementations, declaring capability/version
requirements, supplying component, settings translation/loss, grants, resource cost and
conformance tests. Hooks, MCP, server interfaces and upstream plugins are supported integration
candidates; arbitrary plugin-runtime emulation is still unproved.

Approachable presets and detailed controls must explain effective settings, conflicts,
engine/host changes, update timing and recovery. Installing or loading upstream extensions is
an admitted effect; a plugin's origin does not widen authority. The previous command-only bridge
proposal is a starting point, not a ceiling on first-release useful coverage. See the
[configuration and plugin contract](foundation-research/platform-round/interaction-contract.md).

## Upstream compatibility and support policy — proposed

Provider adapters, engine adapters and Recursion plugins have different ownership and billing
boundaries. Proposed initial command imports are schema-declared and namespaced; execution of
arbitrary upstream plugin environments remains deferred. Retain independent grants, digest-bound
manifests, no-import disabled paths, staged/fenced reload and adapter-free boot/recovery. FND-016.

A proposed support window is the current certified build plus one previous certified build.
Discover and diff upstream source/schema/default tools/terms; stage, replay-test, quarantine,
explicitly promote at a route-epoch boundary and retain a tested rollback. A security emergency
may require refusing new admissions; it does not justify silent policy expansion. Signatures,
SBOMs and protocol versions do not prove semantic compatibility. Pending
`decision.foundation.updates` and `decision.foundation.plugin-bridge`; no updates were installed.

One product with optional profiles remains the direction. The three audiences introduce research
questions, not commercial editions, tenant isolation or compliance certification. FND-008.

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
- full artifact digest and transitive dependency-lock digest; shortened hashes are display only;
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
Manifest resolution and policy checks occur before code import or installation. Discovery is lazy
and bounded: task-specific tool schemas and context enter a WorkPacket only after admission and
consume explicit context/resource budgets.

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
| `core` | kernel, local replay/status and owner CLI; no provider, engine, plugin or frontend is required to boot or recover |
| `standard` | common CLI/provider integrations, planning, context, telemetry, local verification |
| `remote` | node enrollment, authenticated transport, remote execution and observation |
| `full` | all first-party plugins and advanced policies |
| `custom` | schema-validated owner-selected plugin set |

Edition manifests lock exact plugin versions and defaults. Installation should not download or start disabled heavy plugins. A user can add/remove plugins later without migrating to a different product.

Every edition is proposed to share future product defaults: `checkpoint` PAUSE, trusted bounded autonomy,
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

Trust tiers are `T0-kernel`, `T1-signed-built-in`, `T2-signed-isolated-third-party`,
`T3-untrusted-view`, and `T4-external-engine/provider`. A tier is an isolation and review
requirement, never an authority grant. Effective capability is the intersection of artifact
declaration, GoalSpec, constitution, route/account, budget, privacy/egress, PAUSE and explicit
Owner grants; every deny is retained.

The canonical lifecycle contract is:

```text
discovered -> verified -> admitted -> staged -> active
      |            |          |          |        |
      +-------- quarantined/rejected -----+--------+
active -> drain-and-fence -> retired | replaced
active -> revoked -> drain-and-fence -> retained-evidence | retired
```

Reload is a fenced transition, not an in-place mutation: discover and verify the candidate, stage
it, stop new admission to the old version, drain/cancel according to policy, unregister old
capabilities, preserve evidence, advance the epoch, then activate. Old WorkPackets, leases and
subscriptions fail stale. Ambiguous external effects enter reconciliation and never become success.

Revocation blocks new admission immediately. Existing work follows its effect-specific PAUSE
policy and may enter reconciliation; “revoked” does not assert that a remote effect stopped.
A disabled plugin performs no code execution, import or installation; credential access; network
call; subprocess, thread, timer or watcher; background callback; context/tool enumeration; model
turn; quota reservation/debit; spend; or unbounded event subscription. The release manifest retains only the minimal identity/capability
metadata needed to explain that absence; omitting installed payload weight does not omit the
capability-resolution contract.

The exact lifecycle, disabled-path traps, browser-origin rules and release receipts are specified
in [FRONTIER-HARNESS-RESEARCH-TRANCHE-2-EVIDENCE.md](FRONTIER-HARNESS-RESEARCH-TRANCHE-2-EVIDENCE.md#e-fhar2-105--plugin-and-frontend-isolation).

Trusted built-ins may use an immutable typed in-process contributor registry. Third-party or
changeable plugins default to a bounded isolated subprocess or remote protocol adapter with a
capability token and immutable WorkPacket. Protocol negotiation, consent, a signature or a metadata
HMAC never grants GoalSpec, plan, effect or publication authority. Future web/desktop clients use a
redacted observer projection plus a separate authenticated idempotent command API; sandboxed rich
views remain presentation.

One-step novice acknowledgement may combine only digest pinning, requested functional verbs
and the declared workspace sandbox when local policy permits it. Credentials, network egress,
model launch, quota reservations, route/account access, metered spending, automatic update,
downgrade and grant administration remain individually visible grant dimensions. Lucas has
not yet selected which of those dimensions may share an acknowledgement.

Primary trust anchors opened 2026-09-03 are [The Update Framework
specification 1.0.36](https://theupdateframework.github.io/specification/v1.0.36/), [SLSA
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
