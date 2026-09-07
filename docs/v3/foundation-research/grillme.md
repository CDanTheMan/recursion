# Foundation GRILLME packet

2026-09-05. Ten proposals, all **pending**. This run prepares decisions; it does not conduct GRILLME.
Current Owner rulings OR-018/OR-019 and Lucas-first scope are retained. Read [synthesis.md](synthesis.md), then use [decisions.json](decisions.json) as the structured question record.

## 1. Freeze the model's cross-contract identity and fence mapping before E-FHAR2-101.

ID: `decision.foundation.model-boundary`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: OR-018/019 and E-FHAR2-101 already select the boundary; six mappings remain unproved, not a new architecture choice.

1. One aggregate plus explicit adapter proof obligations (recommended): smallest reviewable state space; cannot claim broker/runtime proof.
2. Include bounded broker cursor/credit state now: stronger interaction coverage with larger state space.

Recommendation: Keep the existing finite scope; write a closed projection for effect/packet/goal/plan identities, distinct fence domains and ambiguity; model broker RESET as an adapter obligation unless a counterexample couples it to canonical append. Both options retain the abstract FlowBound queue/retention and non-blocking-append invariant; only detailed broker wire state may move to an adapter proof.

Default versus configuration: proposed fixed model boundary; future exploration bounds configurable. Classification: prerequisite.

Evidence: FND-001, FND-002, FND-003; SRC-V3-095, SRC-V3-104. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required check: explicit model mapping and guard-removal counterexamples before freeze.
Falsifier: A trace admits a stale result, ambiguous retry, future PAUSE permission, or unbound writer.

Affected contracts: [ARCHITECTURE.md](../ARCHITECTURE.md), [PLANNING.md](../PLANNING.md), [EXECUTION-FABRIC.md](../EXECUTION-FABRIC.md), [ACCEPTANCE.md](../ACCEPTANCE.md), [CONSTRUCTION-RUNBOOK.md](../CONSTRUCTION-RUNBOOK.md).
Red designs: `fixture.foundation.model.effect-map`, `fixture.foundation.model.stale-fence`, `fixture.foundation.model.pause`, `fixture.foundation.model.split-writer`, `fixture.foundation.model.partition`, `fixture.foundation.model.broker-gap` in [evidence.json](evidence.json).
Dependency: `model.freeze`. Blocked pending answer: Formal-model freeze; no M1 repair is authorized.

## 2. Define the minimum contract for a governed interactive route and the scope of native-loop work.

ID: `decision.foundation.engine-floor`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: OR-019 permits optional upstream engines; universal native-feature parity and a complete native loop remain unselected.

1. Typed governed routes plus explicitly restricted native terminal sessions (recommended): preserves capability differences and upfront limits.
2. Only engines passing the full mediation floor: smaller route catalog, stronger uniform guarantees.
3. Develop a complete native loop first: more ownership and BYOK freedom, higher implementation and evaluation cost.

Recommendation: One Recursion CLI and canonical command bus; typed engine adapters with versioned optional extensions. Use BYOK for a later native-loop comparator. Refuse any work whose required fence cannot be enforced at the actual resource.

Default versus configuration: proposed common base; optional capabilities and engine choice configurable. Classification: accommodation.

Evidence: FND-004, FND-005, FND-006; SRC-V3-107, SRC-V3-113, SRC-V3-114, SRC-V3-120, SRC-V3-104, SRC-V3-139, SRC-V3-140, SRC-V3-141, SRC-V3-142, SRC-V3-143. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required comparison: `experiment.foundation.adapter`.
Falsifier: A supposedly governed route performs an effect outside its declared mediation/containment boundary.

Affected contracts: [ARCHITECTURE.md](../ARCHITECTURE.md), [CLI.md](../CLI.md), [ROUTE-CAPABILITIES.md](../ROUTE-CAPABILITIES.md), [EXECUTION-FABRIC.md](../EXECUTION-FABRIC.md), [SECURITY.md](../SECURITY.md).
Red designs: `fixture.foundation.adapter.descendant`, `fixture.foundation.adapter.command-collision`, `fixture.foundation.adapter.cancel-ambiguous` in [evidence.json](evidence.json).
Dependency: `adapter.construction`. Blocked pending answer: Interactive adapter implementation and claims of Recursion command parity.

## 3. Choose the public authentication promise for Recursion's native and delegated modes.

ID: `decision.foundation.authentication`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: Technical authentication, usage entitlement and distribution are independent; Owner wants Recursion UX with Claude Code where required.

1. Route-specific BYOK and user-authenticated upstream binaries (recommended): honest limits, additional setup surfaces.
2. BYOK-only initial public support: simpler terms and usage accounting; excludes subscription-driven workflow.
3. Promise broad subscription reuse only after explicit provider agreements: larger market scope with unresolved prerequisites.

Recommendation: Keep Claude SDK/API and unmodified Claude Code sessions separate. Let the upstream binary conduct its own sign-in; no token interception or pooled credentials. Codex login capability does not establish a universal third-party OAuth right.

Default versus configuration: proposed public wording; user selects eligible route. Classification: accommodation.

Evidence: FND-006; SRC-V3-112, SRC-V3-108, SRC-V3-116. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required comparison: `experiment.foundation.adapter`.
Falsifier: A required Recursion feature needs unsupported login reuse, binary modification or usage intermediation.

Affected contracts: [PRODUCT.md](../PRODUCT.md), [CLI.md](../CLI.md), [SECURITY.md](../SECURITY.md), [ROUTE-CAPABILITIES.md](../ROUTE-CAPABILITIES.md).
Red designs: `fixture.foundation.adapter.auth-boundary` in [evidence.json](evidence.json).
Dependency: `public.auth-promise`. Blocked pending answer: Public subscription support wording and redistribution packaging, not formal-model work.

## 4. Whether to add an optional agent-assisted /setup after deterministic bootstrap.

ID: `decision.foundation.setup`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: CLI already mandates schema-driven zero-model setup; agent assistance is new and unproved.

1. Deterministic setup plus optional proposal-only assistant (recommended): offline and first-auth recovery remain possible.
2. Deterministic setup only for v3.0: lower complexity and support burden.

Recommendation: Keep credential entry in protected provider/OS flows and outside prompts. Assistant may explain presets and propose a scoped diff; validation, explicit application and rollback remain deterministic.

Default versus configuration: zero-model default; agent-assisted explanation optional. Classification: accommodation.

Evidence: FND-012; SRC-V3-108, SRC-V3-112. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required comparison: `experiment.foundation.setup`.
Falsifier: A fresh offline installation needs a model to recover or an assistant sees a credential.

Affected contracts: [CLI.md](../CLI.md), [PRODUCT.md](../PRODUCT.md), [SECURITY.md](../SECURITY.md).
Red designs: `fixture.foundation.setup.no-agent`, `fixture.foundation.setup.secret`, `fixture.foundation.setup.rollback` in [evidence.json](evidence.json).
Dependency: `setup.extension`. Blocked pending answer: Agent-assisted setup implementation.

## 5. Choose provisional compaction and cache-refresh defaults pending measurements.

ID: `decision.foundation.context-policy`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: CONTEXT already has capsules, fidelity checks and one compaction owner; hybrid benefit and refresh savings remain hypotheses.

1. Event-driven continuation, route-aware compaction, no model keepalive (recommended): avoids speculative idle spend.
2. Opt-in provider-specific refresh only after total-cost trials: possible latency savings, additional quota and privacy cost.

Recommendation: Use hard non-droppable control state and fidelity refusal. Separate capacity, price threshold and cache retention. Require experiment.foundation.cache before enabling periodic model refresh; preserve native compaction boundaries through epoch-bound ownership.

Default versus configuration: no model keepalive proposed default; thresholds and eligible retention configurable. Classification: later-experiment.

Evidence: FND-009, FND-010, FND-011; SRC-V3-130, SRC-V3-131, SRC-V3-132, SRC-V3-129, SRC-V3-133. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required comparison: `experiment.foundation.compaction`, `experiment.foundation.cache`.
Falsifier: Refresh costs more per successful task, or a summary loses authority/evidence despite a high cache-hit rate.

Affected contracts: [CONTEXT.md](../CONTEXT.md), [TELEMETRY.md](../TELEMETRY.md), [PERFORMANCE-PLAN.md](../PERFORMANCE-PLAN.md).
Red designs: `fixture.foundation.context.directive-loss`, `fixture.foundation.cache.zero-work`, `fixture.foundation.context.double-owner` in [evidence.json](evidence.json).
Dependency: `context.optimization`. Blocked pending answer: Optimization defaults and claimed savings; capsule contract already stands.

## 6. Set the first remote deployment authority domain.

ID: `decision.foundation.remote-scope`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: Single-authority integrity is specified; single-user multi-node does not provide hosted tenant isolation.

1. One Owner/authority domain across enrolled nodes (recommended): test fencing and partitions before tenancy.
2. Organization-operated instance next: requires identity/role and audit contracts.
3. Hosted multi-tenant service: defer until isolated authorities, quotas, secrets and support obligations are designed.

Recommendation: Keep client, coordinator, executor, engine, inference provider and account pool separate. One canonical writer per aggregate, explicit enrollment/revocation, manifest-first artifacts and reconnect revalidation; disconnected work cannot publish or widen authority.

Default versus configuration: one authority domain proposed first; topology/locality configurable. Classification: accommodation.

Evidence: FND-013; SRC-V3-110, SRC-V3-123, SRC-V3-124, SRC-V3-104. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required comparison: `experiment.foundation.remote`.
Falsifier: A disconnected or replaced node commits canonical state or publishes without fresh authority.

Affected contracts: [ARCHITECTURE.md](../ARCHITECTURE.md), [EXECUTION-FABRIC.md](../EXECUTION-FABRIC.md), [TERMINAL-RUNTIME.md](../TERMINAL-RUNTIME.md), [PRODUCT.md](../PRODUCT.md), [SECURITY.md](../SECURITY.md).
Red designs: `fixture.foundation.remote.split-brain`, `fixture.foundation.remote.offline-revocation`, `fixture.foundation.remote.sleep` in [evidence.json](evidence.json).
Dependency: `remote.construction`. Blocked pending answer: Remote runtime construction and organization/hosted scope; OR-015 still blocked.

## 7. Choose an initial evaluation profile for model allocation without turning models into authority roles.

ID: `decision.foundation.escalation`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: Head/ARM/worker and direct Owner-to-ARM interaction are accepted; model ladder efficiency is unproved.

1. Evaluate single agent, simple delegation, all-frontier and mixed fleet equally (recommended): evidence before policy.
2. Start with all-frontier as a temporary quality baseline: higher included-capacity pressure, easier attribution.

Recommendation: Escalate on bounded evidence of difficulty, novelty or failure. Model replacement retains role and scope; permission escalation and lease replacement require separate transitions. Deterministic status heartbeats do not imply continuous model thought.

Default versus configuration: evaluation treatments configurable; authority invariants fixed. Classification: later-experiment.

Evidence: FND-014, FND-015; SRC-V3-135, SRC-V3-136, SRC-V3-137, SRC-V3-093. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required comparison: `experiment.foundation.delegation`.
Falsifier: Mixed routing raises failure/review cost at equal budget or escalation widens authority.

Affected contracts: [EXECUTIVES.md](../EXECUTIVES.md), [PLANNING.md](../PLANNING.md), [PERFORMANCE-PLAN.md](../PERFORMANCE-PLAN.md).
Red designs: `fixture.foundation.fleet.stronger-no-grant`, `fixture.foundation.fleet.correlated-error` in [evidence.json](evidence.json).
Dependency: `fleet.policy`. Blocked pending answer: Optimization profile, not accepted executive hierarchy.

## 8. Choose the adapter support window and emergency update admission policy.

ID: `decision.foundation.updates`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: Pinned typed adapters exist as direction; unchanged protocol names do not prove unchanged behavior.

1. Current certified build plus one prior certified build (recommended proposal): bounded maintenance and a rollback target.
2. Only one certified build: lower maintenance, more disruptive emergency replacement.
3. Wider version ranges: easier adoption, much larger replay and security burden.

Recommendation: Discover releases without auto-activating them. Diff source/schema/default tools/terms, stage with recorded digests, run synthetic transcripts and failure probes, quarantine discrepancies, explicitly promote at route-epoch boundaries; emergencies may disable admission while evidence is gathered.

Default versus configuration: support-window proposal; update channel configurable, evidence gates fixed. Classification: accommodation.

Evidence: FND-007, FND-016; SRC-V3-111, SRC-V3-117, SRC-V3-118, SRC-V3-119, SRC-V3-004, SRC-V3-005. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required comparison: `experiment.foundation.updates`.
Falsifier: A build passes version negotiation but changes permission/tool/replay semantics undetected.

Affected contracts: [PLUGINS-AND-EDITIONS.md](../PLUGINS-AND-EDITIONS.md), [ROUTE-CAPABILITIES.md](../ROUTE-CAPABILITIES.md), [SECURITY.md](../SECURITY.md), [ACCEPTANCE.md](../ACCEPTANCE.md).
Red designs: `fixture.foundation.update.silent-tool`, `fixture.foundation.update.resume-drift`, `fixture.foundation.update.rollback` in [evidence.json](evidence.json).
Dependency: `adapter.support-policy`. Blocked pending answer: Public compatibility window and automatic update implementation.

## 9. Set the initial upstream command/plugin import depth.

ID: `decision.foundation.plugin-bridge`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: Plugin grants are independent and fenced; upstream commands cannot inherit authority through origin.

1. Schema-declared command adapters only (recommended): namespace and argument checks; unsupported features explicit.
2. Also execute upstream plugin environments: greater compatibility with a larger grant and dependency surface.

Recommendation: Use separate provider, engine and Recursion plugin manifests. Reserve core commands, namespace imported aliases, expose translation losses and validate arguments/grants before dispatch. Removal must preserve canonical boot/recovery.

Default versus configuration: minimal bridge proposed first; optional adapters configurable. Classification: accommodation.

Evidence: FND-004, FND-016; SRC-V3-120, SRC-V3-107, SRC-V3-069, SRC-V3-004. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required comparison: `experiment.foundation.adapter`, `experiment.foundation.updates`.
Falsifier: An imported command shadows a core command or a disabled plugin contributes authority or unavoidable idle work.

Affected contracts: [CLI.md](../CLI.md), [PLUGINS-AND-EDITIONS.md](../PLUGINS-AND-EDITIONS.md), [SECURITY.md](../SECURITY.md).
Red designs: `fixture.foundation.adapter.command-collision`, `fixture.foundation.plugin.disabled`, `fixture.foundation.plugin.reload-fence` in [evidence.json](evidence.json).
Dependency: `plugin.import-scope`. Blocked pending answer: Advanced compatibility import; existing independent grant rules remain.

## 10. Select the first external learning cohort after Lucas-first validation.

ID: `decision.foundation.audience-validation`. Status: **pending**. Owner answer: **pending**.

Current rule and issue: Lucas-first is accepted. Three-audience ambition supplies no market-demand or enterprise willingness-to-pay evidence.

1. Developers/power users first (recommended): bounded repository workflows and diagnosable failures.
2. Casual users first: earlier setup/comprehension feedback, higher support and recovery demands.
3. Organization pilots first: audit/identity feedback, slower procurement and broader requirements.

Recommendation: Keep one product with optional profiles. First validate a small bounded repository task, interruption/recovery and cost comprehension; test novice setup separately. Defer hosted tenancy, commercial tiers and graphical/media extensions.

Default versus configuration: Lucas-first fixed; proposed next cohort and optional profiles. Classification: later-experiment.

Evidence: FND-008, FND-012, FND-017; SRC-V3-136, SRC-V3-137. Proposal only; no Owner answer or runtime/performance outcome is supplied.
Required comparison: `experiment.foundation.setup`, `experiment.foundation.resources`.
Falsifier: Target users cannot finish/recover the task or understand cost and authority without repeated expert help.

Affected contracts: [PRODUCT.md](../PRODUCT.md), [PLUGINS-AND-EDITIONS.md](../PLUGINS-AND-EDITIONS.md), [INTERACTION-SURFACES.md](../INTERACTION-SURFACES.md), [ROADMAP.md](../ROADMAP.md).
Red designs: `fixture.foundation.ux.false-progress`, `fixture.foundation.setup.no-agent` in [evidence.json](evidence.json).
Dependency: `external.product-study`. Blocked pending answer: External cohort and adoption claims; no change to near-term construction order.

## Recording the later session

Follow [PLANNING.md](../PLANNING.md)'s GRILLME protocol one consequential decision at a time. Preserve each exact Owner answer in the authorized private intent record; commit only a publication-safe disposition with provenance. Update the structured status and affected canonical documents, check cross-decision consistency, and compile an accepted versioned GoalSpec and construction DAG. Re-run documentation checks after changes. An answer to a product question does not by itself authorize implementation, spending, publication or deployment. Unanswered choices remain pending; do not infer consent from silence.
