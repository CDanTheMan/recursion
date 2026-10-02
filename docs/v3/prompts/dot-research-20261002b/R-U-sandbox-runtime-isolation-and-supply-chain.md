---
title: R-U — Sandbox runtime isolation and supply chain
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-U — Sandbox runtime isolation and supply chain

This is an isolation-and-supply-chain handoff for accepted Owner decisions D-018, D-019, D-022,
D-024 and D-031, with the capability and plugin surface those decisions require and the gap
register in [GAPS.md](../../research-lane/GAPS.md). It builds directly on
[R-G](R-G-plugin-import-and-cross-harness-reuse.md), the plugin-import and cross-harness-reuse
handoff, and on [R-E](R-E-trusted-launch-boundary.md), the trusted-launch-boundary handoff: R-E
separates Recursion from the user's credential store, and R-G imports third-party plugin
ecosystems, while R-U designs the *runtime boundary* those plugins, tools and delegated agents
execute inside and the *supply-chain* evidence that admits them. It must extend, not restate, the
plugin-manifest and capability/grant/attenuation/refusal/accounting semantics those lanes share.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone agent harness and a harness
orchestrator that delegates through other harnesses. Hermes-led control was retired on
2026-09-28 (state/DECISIONS.md D-017); Hermes is an optional upstream integration, not the
executive control plane. Workers are bounded executors. An implementer's own PASS is never
acceptance; independent review is required, and missing verification is never a pass.
`CONTROL_PLANE.md` is the operative constitution; a research session may propose amendments
but must never edit it. No research session performs implementation,
provider/model/authentication/configuration changes, spending, deployment, publication or
merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula,
captures and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs,
pinned source, licenses, peer-reviewed work). Classify every consequential claim as
source-documented, locally observed, inferred or unverified; keep `unknown` distinct from
zero. Model consensus and vendor marketing are not evidence. Every recommendation needs a
competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never
secrets, credentials, personal data, private repository content, local paths, or
account/infrastructure identifiers.

### Lane context

- The object of study is the **execution boundary** for every party that runs inside Recursion:
  first-party plugins, ported or third-party plugins, local tools invoked by a tool adapter, and
  delegated upstream agents or subprocesses. The question is not "which sandbox wins" but what a
  capability-scoped execution contract must guarantee on the accepted platform floors, and what
  evidence admits untrusted bytes into the boundary at all.
- D-018 makes Recursion a first-class native harness *and* a first-class unifying wrapper over the
  wider harness ecosystem whose purpose is to remove lock-in and cut quota/usage burn. A wrapper
  that imports foreign plugins and drives foreign CLIs necessarily executes foreign code; the
  isolation tier therefore has to be strong enough to make an untrusted plugin and an untrusted
  upstream harness acceptable, without tying Recursion to one vendor runtime.
- D-019 builds the comprehensive capability and plugin surface but ships every capability as an
  **opt-in plugin or profile** rather than a default. The consequence for this lane is a hard
  **disabled-path inertness** invariant: a capability that is not enabled must produce zero
  effects, zero activations, zero network egress and zero resource consumption — not merely a
  hidden UI.
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain` — across configuration, the formal model and the broker. The sandbox
  contract must map to that vocabulary: what a Stop mode does to a running sandboxed process, its
  descendants, its mounts, its handles and its network sockets, and what "terminated" is claimed
  to mean.
- D-024 makes **productive continuity** the headline measurable differentiator: a currently
  authorized task survives a harness change, compaction, a source fork or a lost machine while
  preserving authority, evidence and honest accounting. An isolation boundary must not be a place
  where authority, evidence or accounting silently diverge, and recovery after a sandbox crash
  must be honest about what executed and what did not.
- D-031 forbids marketing Recursion on a "vendors sabotage quota" claim: containment failures,
  quarantine outcomes and dependency incidents are reported as measured facts, never as
  vendor-intent narratives.
- Authority is **not** origin-based. A plugin signed by a trusted publisher, a binary from a
  "trusted" path, or a tool from a first-party harness carries **no** authority merely by where it
  came from. Authority is a typed capability grant attenuated from the task's GoalSpec, and no
  origin, signature, cache hit or prior run may widen it.
- Already accepted, non-negotiable direction this lane must respect: the kernel owns authority
  admission; capability grants are typed, attenuated and revocable; no research session selects a
  sandbox, runtime or packaging format; `unknown` is never collapsed to zero; and every
  recommendation carries a competing option, a decisive falsifier and an explicit non-proof.
- Prior comparison coverage to extend, not reinvent: the plugin-isolation tier left undecided by
  DS-18/G-10, the containment and zero-effect disabled invariant in G-19, the platform-profile
  floors of D-028 (Windows 11 25H2 build 26200 and 24H2 Enterprise, Linux 6.12 LTS primary / 6.6
  LTS minimum with cgroup v2, WSL2 dev/test only, local NTFS/ext4 only), and the source-documented
  public behavior of OS sandboxes, WASM/WASI runtimes, process/Job Object confinement and
  container isolation.
- Evidence status: no sandbox, escape test, containment fixture, SBOM generator, signature
  verifier or provenance consumer has been implemented or measured by Recursion for this lane.
  Every isolation-strength, performance, compatibility and supply-chain statement below is to be
  established from public source, documented behavior and a synthetic provider-free fixture, or
  marked `unknown`.

## Purpose

Produce the decision-ready **sandbox runtime isolation and supply-chain design candidate** for
Recursion. The lane specifies the capability-scoped execution boundary for plugins, tools and
delegated agents; the least-privilege and resource-limit contract; containment and escape-test
requirements; the supply-chain admission path (bill of materials, signatures, provenance,
dependency security and quarantining); the invariant that authority is never origin-derived; and
disabled-path inertness. It compares the placement options for the boundary — in-process, WASM,
process/OS-sandbox, container and remote/host — each with a competing option and a decisive
falsifier, and it does not select one. It delivers a design candidate with provider-free
acceptance fixtures. It does not select a language, store, framework, runtime, sandbox, packaging
format or vendor, does not qualify any route, and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, sandbox, isolation technology, packaging
format, container runtime, WASM runtime or vendor.** Do not decide an Owner question recorded in
D-018, D-019, D-022, D-024 or D-031. Treat every named external runtime or product as prior art
cited from public documentation, not as an endorsed or selected component. No provider, model or
account call is made; no sandbox is installed or executed; no credential or account is touched.
Do not claim that a signature, publisher, file origin, cache hit or capability *name* confers
authority; authority is a typed grant. Do not claim that any isolation tier is escape-proof — it
is a hypothesis with a falsifier. Do not assert quantitative containment, performance or supply
chain guarantees that were not measured; record them `unknown`.

## Inputs to read

None from this repository: the rescope, the plugin-manifest and capability semantics, the
trusted-launch boundary and the platform floors are summarized in `## Baked context` above, and
no repository, connector or private-source access is assumed. The session must, however, retrieve
the public documentation it cites — the platform sandbox and confinement documentation for the
accepted Windows and Linux floors, the WASM/WASI specification and its capability model, the
process/Job Object and cgroup v2 confinement documentation, the container isolation
specifications, the SBOM standards (for example SPDX and CycloneDX), the in-toto/SLSA provenance
specifications, the Sigstore signing and transparency-log documentation, and the public
dependency-vulnerability and advisory sources — and pin each claim to a URL and retrieval date.

## Research questions

### Capability-scoped execution and least privilege

1. What is the typed capability model for a sandboxed party in Recursion — filesystem paths and
   modes, network destinations, process/child creation, environment, device and IPC access,
   clock, entropy, service endpoints — and how is each capability attenuated from the task's
   GoalSpec so that a plugin cannot request, synthesize or accumulate authority the task did not
   hold?
2. How is least privilege enforced at the boundary rather than by convention: default-deny for
   every capability the manifest does not explicitly enumerate, and a refusal path that reports
   *which* capability was missing rather than degrading silently?
3. How do resource limits apply per party and per task — CPU time, wall time, memory, address
   space, file descriptors and handles, child-process count, disk and temporary-space quota,
   network bytes and connection count, and output volume — and how are limits made visible,
   auditable and enforced at the OS or runtime layer rather than inside the guest?
4. How is capability **revocation** applied to a running sandboxed party (D-022 vocabulary) so that
   an authority change mid-execution takes effect without requiring the whole task to restart, and
   what is the honest boundary between "asked to stop" and "observed stopped"?
5. How is the boundary kept consistent across the accepted Windows and Linux floors, including
   the WSL2 dev/test distinction, so that a capability means the same thing (or is explicitly
   `unknown`/unsupported) on each profile?

### Containment and escape tests

6. What containment claims must the design make explicit — process and descendant containment,
   filesystem view isolation, network egress control, credential non-access, kernel and host
   surface restriction, and inter-party isolation between two sandboxed plugins — and which of
   them can be tested provider-free?
7. What escape and abuse test suite is required: path and mount traversal, symlink and junction
   escape, `..` and NTFS reparse-point abuse, inherited handle or descriptor leakage,
   environment and credential leakage, child-process or orphan escape, signal/channel smuggling,
   fork bombs and resource exhaustion, and network pivot attempts — with an exact pass/fail
   predicate per case?
8. How is whole-descendant-tree termination proven — that a Stop in Aggressive/Full/Lazy mode
   reaps the sandboxed party and every process it spawned across Windows Job Objects and Linux
   cgroups — given that DS-09/G-23 record whole-descendant-tree termination as unverifiable from
   schema?
9. What is the **disabled-path inertness** fixture: with a capability or plugin disabled, prove
   zero process started, zero bytes read or written outside the disabled runtime's own inert
   storage, zero network egress, zero activation and zero resource consumption, so that D-019's
   opt-in rule is a tested invariant rather than a default bitmap?
10. How is each containment claim classified as source-documented, locally observed, inferred or
    `unknown`, and what decimal or categorical threshold would falsify a claim of effective
    isolation on each platform profile?

### Supply chain: SBOM, signatures, provenance and dependency security

11. What supply-chain admission contract is required before a plugin, tool or delegated agent
    may execute: a machine-readable bill of materials of its transitive dependencies, a
    verifiable signature over the artifact, an attestation of how and from what it was built
    (provenance), and a declared capability manifest that is checked against the grant it
    receives?
12. How are signatures, provenance and SBOMs verified offline and deterministically, including
    revocation, expiry, transparency-log inclusion and key rotation, so that verification never
    requires a live vendor service and never becomes a bootstrap trust could not check?
13. How is the dependency-security loop defined — advisory and vulnerability feeds, pinned and
    reproducible dependency resolution, lockfile integrity, transitive-dependency risk surfacing,
    quarantine and rollback of a bad artifact, and a consent gate before an updated dependency
    may gain new capabilities?
14. What threat model covers a **compromised publisher**, a typosquatted or substituted
    dependency, a build-server compromise, a silent capability expansion in an updated artifact,
    and a malicious SBOM or provenance document, and which of these can be detected by this
    contract versus merely recorded?
15. How does the contract keep authority non-origin-based: a valid signature, a known publisher, a
    first-party package or a previously accepted artifact must not itself confer authority; the
    admitted capabilities must still be within the attenuated grant of the running task.

### Placement options and falsifiers

16. Compare the competing boundary placements — in-process/isolated-module, WASM/WASI with
    capability imports, a supervised child process with OS sandboxing, a container-style
    namespace boundary, and a remote/host execution boundary — on containment strength, platform
    parity, startup and steady-state cost, capability granularity, supply-chain surface,
    debuggability and dependency cost. Do not select one.
17. What negative trace would eliminate a placement option before any benchmark — for example a
    platform floor on which the mechanism has no supported primitive, an inability to enforce
    network egress, or a documented inability to revoke a capability at runtime?
18. What is the decisive falsifier for the claim "the disabled path is inert" and for "the
    isolation tier is adequate for untrusted third-party plugins," and what measured failure
    (escape, leak, resource blow-up, platform divergence) would reverse a preference?

### Provider-free acceptance fixtures

19. What provider-free fixtures must accept or reject: a default-deny capability probe, a
    capability-attenuation escalation attempt, a resource-limit saturation, a whole-descendant
    termination across each platform floor, a forbidden-network-egress probe, a cross-party
    isolation probe, a disabled-path inertness soak, an SBOM/signature/provenance verification
    set with negative cases, and a quarantine-and-rollback drill — and what is the exact
    pass/fail predicate for each?
20. How do the fixtures prove that no origin, signature or cache hit widens authority, that a
    Stop reaps the whole sandboxed tree, and that a blocked or failing sandbox cannot block the
    canonical writer, Stop or recovery — using synthetic artifacts and local processes only,
    with no provider call?

## Deliverable

A sandbox runtime isolation and supply-chain design candidate containing: a capability-scoped
execution and least-privilege section that defines the typed capability lattice, default-deny
enforcement, per-party resource limits, runtime revocation and cross-platform parity; a
containment and escape-test section that enumerates claims, the escape/abuse suite, whole-
descendant-tree termination, and the disabled-path-inertness fixture with exact predicates; a
supply-chain section defining the SBOM, signature, provenance, dependency-security, quarantine
and rollback contract plus a threat model, and the rule that authority is never origin-based; a
placement-options section comparing in-process, WASM/WASI, OS-sandboxed process, container and
remote boundaries with a competing option, a negative trace and a decisive falsifier for each,
selecting none; and a provider-free fixture suite for every predicate above. Each recommendation
names a competing option, a decisive falsifier and what it does not prove. No language, store,
framework, runtime, sandbox, isolation technology, packaging format or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, sandbox, isolation
  technology, container runtime, WASM runtime, packaging format or vendor.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No assertion that any isolation tier is escape-proof, that a signature or publisher confers
  authority, or that a capability name grants access; each is a tested or `unknown` claim.
- No claim that disabled capabilities consume some "small" resources; the invariant is zero
  effect, zero activation, zero egress and zero consumption, with a falsifier.
- No provider, model, credential or account call; no sandbox, container or runtime installed or
  run; every fixture is synthetic and provider-free.
- No new executive tier, no separate AI "ARM manager", and no security boundary that silently
  replaces the kernel's authority admission.
- No reopening of D-018, D-019, D-022, D-024 or D-031, and no reopening of the platform floors
  in D-028 or the trusted-launch boundary in D-029.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The capability-scoped execution section defines a typed capability lattice for filesystem,
  network, process, environment, device and IPC, enforced default-deny, attenuated from the
  task's GoalSpec, revocable at runtime under the D-022 vocabulary, and consistently across the
  Windows and Linux profile floors.
- The least-privilege section defines per-party and per-task resource limits and how each is
  enforced at the OS or runtime layer rather than inside the guest.
- The containment section enumerates containment claims, gives an escape/abuse test suite with
  exact pass/fail predicates, proves whole-descendant-tree termination across the platform
  floors, and specifies the disabled-path-inertness fixture with a zero-effect predicate.
- The supply-chain section defines a BOM, signature, provenance, dependency-security, quarantine
  and rollback contract, verifiable offline and deterministically, plus a threat model covering a
  compromised publisher, a substituted dependency, a build-server compromise and a silent
  capability expansion.
- The candidate states that authority is never origin-based: signature, publisher, file origin,
  cache hit and capability name confer no authority, and admitted capabilities remain inside the
  attenuated grant.
- The placement-options section compares in-process, WASM/WASI, OS-sandboxed process, container
  and remote boundaries, each with a competing option, a negative trace and a decisive
  falsifier, and selects none of them.
- The provider-free fixture suite specifies predicates for the default-deny probe, attenuation
  escalation, resource saturation, descendant termination, network-egress blocking, cross-party
  isolation, disabled-path inertness, supply-chain verification with negative cases, and
  quarantine-and-rollback, and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not
  prove; no language, store, framework, runtime, sandbox, isolation technology, packaging format
  or vendor is selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured escape resistance, no
  measured containment or performance advantage, no supply-chain guarantee against a determined
  attacker, no route qualification, and no entitlement.
- Protected paths are untouched; privacy and secret scan are clean.
