---
title: R-X — Node fabric and remote execution protocol
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-X — Node fabric and remote execution protocol

This is a multi-node execution handoff for accepted Owner decisions D-018, D-019, D-020, D-022,
D-024 and D-031, with the gap register in [GAPS.md](../../research-lane/GAPS.md). It builds
directly on [R-O](R-O-performance-and-configurability-engineering.md), the backend-performance
handoff, and on [R-U](R-U-sandbox-runtime-isolation-and-supply-chain.md), the isolation handoff:
R-U designs the boundary a party executes inside, while R-X designs how that boundary is
**enrolled, authenticated, placed, leased, fenced and recovered across nodes**. It must consume
the already accepted availability contract in D-020 and must not reopen it.

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

- The object of study is the **node fabric**: how more than one machine participates in a
  Recursion goal — enrollment, authenticated transport, placement and offload decisions,
  distributed leases and fencing, disconnect and reconnect, recorded-work recovery, cross-OS
  semantics and the protocol shape — while exactly one fenced canonical writer owns the
  authoritative event order.
- D-020 is the governing accepted decision and must be consumed, not reopened. It requires
  **automatic node takeover** for long-running autonomous work (user-toggleable) while the
  shipping **core is single-node**; the kernel owns the monotonic fence/epoch and a
  store/availability seam; the replicated store plus coordinator election ship as a first-party
  plugin in the `remote`/`full` editions; and the default install compiles in no consensus. It
  explicitly distinguishes multi-node **execution** (first release, OR-025) from multi-node
  **canonical-writer failover** (a plugin). R-X must hold that distinction: this lane designs
  remote *execution*, and it treats writer takeover only as a boundary it must not violate.
- D-018 makes Recursion a first-class native harness *and* a unifying wrapper whose purpose is to
  remove lock-in and cut quota/usage burn. Remote placement must be broker-neutral, route-neutral
  and vendor-neutral, and must not depend on a specific cloud, orchestrator or message bus.
- D-019 ships every capability as an **opt-in plugin or profile** with no default spend. Remote
  nodes, coordination topologies and remote execution are opt-in; an idle node must do no
  inference, hold no lease and consume no more than a health check, and the lean/default profile
  must be single-node with no fabric runtime active.
- D-022 adopts one pause/stop vocabulary — **Aggressive / Full / Lazy** plus `checkpoint`,
  `interrupt` and `drain`. In the fabric the vocabulary must mean the same thing: what Stop does
  to a remotely running party, its descendants and its leases; a socket close or killed remote
  PID is not external rollback; and `drain` must define how a node is removed without losing
  durable work.
- D-024 makes **productive continuity** the headline measurable differentiator across harness
  change, compaction, source fork and **lost machine**. The fabric is the mechanism under "lost
  machine": recorded work must resume without inventing completion, authority must survive the
  move, evidence must travel with the manifest and accounting must stay honest about what
  executed and where.
- D-031 forbids a "vendors sabotage quota" claim; node and network incidents are reported as
  measured facts, never as vendor-intent narratives.
- Authority is not origin-based: being enrolled, being on the local network, having a valid
  certificate or having executed a previous task **confers no authority**. A remote node receives
  only the attenuated grant and the minimum manifest the task's GoalSpec authorizes.
- Already accepted direction this lane must respect: exactly one fenced canonical writer owns the
  authoritative event order; the kernel owns the monotonic fence/epoch; a remote worker is a
  bounded executor, never a second writer or a second portfolio executive; the non-droppable
  control kernel and rehydration locator semantics travel with a capsule; cross-node delivery
  sends the manifest and minimum control kernel first, then hydrates only authorized artifacts
  after digest validation; and every recommendation carries a competing option, a decisive
  falsifier and a non-proof.
- Recorded evidence this lane inherits: G-06 is closed by D-020 but G-05 (IPC/process-broker
  protocol freeze, including version negotiation, snapshot materialization, cursor rollover and
  ACK-release wording) and G-04 (OS native-semantics conformance, including supervisor races)
  remain open; DS-23 records the broker protocol as only conditionally adopted; DS-25 records the
  recovery matrix as unmeasured; DS-20 records the coordinator-small capacity profile as a target,
  not a demonstrated point. No multi-node transport, enrollment flow or failover path exists or
  has been measured.
- Prior comparison coverage to extend, not reinvent: public distributed-lease and fencing-token
  literature, Raft/Paxos election documentation and its failure semantics, authenticated-transport
  and certificate-enrollment practice, and the documented remote-control surfaces of public
  upstream harnesses. These are cited from public documentation, not adopted or endorsed.
- Evidence status: no node was enrolled, no transport was authenticated, no lease or fence was
  exercised, no disconnect was replayed and no remote recovery ran. Every latency, availability,
  placement, security and recovery statement below is to be established from public source and a
  synthetic provider-free fixture, or marked `unknown`.

## Purpose

Produce the decision-ready **node fabric and remote-execution-protocol design candidate** for
Recursion. The lane specifies node enrollment and identity; authenticated and encrypted transport
with version negotiation; placement and offload decisions; distributed leases and fencing
consistent with the single fenced canonical writer; disconnect, reconnect, partition and drain
semantics; recorded-work recovery after a lost machine; cross-OS path, process, signal and
filesystem semantics; the security model for an enrolled but not-fully-trusted node; and the
shape of the protocol, without selecting a transport, framework or store. It explicitly
distinguishes multi-node execution from canonical-writer availability per D-020, and it compares
competing designs (central coordinator, direct peer, delegated-to-upstream) with a decisive
falsifier for each, selecting none. It delivers a design candidate with provider-free fixtures.
It does not select a language, store, framework, transport or vendor, does not qualify any route,
and executes no provider call.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, store, framework, runtime, transport protocol, message bus, container
orchestrator, certificate authority or vendor.** Do not decide an Owner question recorded in
D-018, D-019, D-020, D-022, D-024 or D-031, and do not reopen D-020 or the single-writer
contract. No provider, model or account call is made; no node is enrolled, no transport is
contacted and no credential or account is touched. Do not claim that enrollment, a valid
certificate, local-network proximity or prior execution confers authority. Do not claim that
automatic takeover is in the shipping core; per D-020 the core is single-node and takeover is a
first-party plugin. Do not assert measured availability, failover time, placement quality or
transport performance; record each as a hypothesis with a falsifier or as `unknown`.

## Inputs to read

None from this repository: the rescope, the D-020 availability contract, the capsule and
rehydration semantics, the pause/stop vocabulary and the continuity endpoints are summarized in
`## Baked context` above, and no repository, connector or private-source access is assumed. The
session must, however, retrieve the public documentation it cites — the lease, fencing-token and
consensus literature (for example Raft and Paxos and their published failure analyses),
authenticated-transport and mutual-TLS/SPIFFE-style identity documentation, the accepted platform
floors' process-, signal-, path- and filesystem-semantics documentation, network-partition and
CRDT/at-least-once delivery references, and the public remote-control documentation of the
upstream harnesses named in the comparison — and pin each claim to a URL and retrieval date.

## Research questions

### Enrollment, identity and authenticated transport

1. What is the node-enrollment contract: how a node joins, how its identity is established and
   bound, how enrollment is authorized by the Owner, how a node is revoked, and how enrollment
   avoids conferring authority beyond the task's attenuated grant?
2. What authenticated, encrypted transport requirements must hold — mutual authentication,
   forward secrecy, replay resistance, message integrity, version negotiation and downgrade
   refusal — and how are they validated on the accepted Windows and Linux floors without
   selecting a transport?
3. How do nodes establish a shared, verifiable notion of identity and epoch so that a stale or
   cloned node cannot act as a live one, and what is the decisive falsifier for each identity
   assumption?
4. How is the **minimum control kernel** delivered first and authorized artifacts hydrated only
   after digest validation, and how is a hydration request that would widen authority or egress
   refused rather than served?

### Placement, leases and fencing

5. What placement and offload decision inputs are required — node capability descriptors, OS and
   application availability, resource headroom, locality of repository/source data, latency,
   cost, privacy/egress bounds and current load — and how is a placement justified from recorded
   facts rather than a heuristic score?
6. How are distributed **leases** defined for remote execution so that a task or step has at most
   one active executor at a time, and how do leases interact with the single fenced canonical
   writer without making the remote node a second writer?
7. How are **fencing tokens/epochs** issued, carried on every mutating request and checked at the
   receiver, so that a paused, partitioned or slow former holder cannot commit stale work, and
   what is the negative trace that proves stale-work rejection?
8. What is the honest ordering guarantee between "lease granted", "work started", "work
   recorded" and "work settled", and how is a lost acknowledgement represented so it is never
   read as success?
9. How does the design keep the shipping core single-node and consensus-free, with any replicated
   coordination confined to the D-020 plugin seam, and what falsifier would show consensus leaked
   into the core?

### Disconnect, reconnect, drain and recovery

10. How are disconnect, reconnect, partition, node retirement and node crash distinguished, and
    what does each do to running work, leases, fences and recorded events?
11. How does **recorded-work recovery** resume after a lost machine: which checkpoint and
    canonical suffix are sufficient, what is verified before resuming, and how is partial or
    uncertain work classified as re-executable, resumable or `unknown` rather than assumed
    complete (D-024)?
12. How is duplicate execution prevented or made safely idempotent when a task resumes elsewhere,
    and what evidence proves that the same effect was not applied twice?
13. How does `drain` remove a node without losing durable work or violating the pause/stop
    vocabulary, and how are in-flight effects fenced during drain?
14. How do reconnect and partition heal the view without inventing an event, and how is a replay
    gap across the fabric represented as a marker rather than a fabricated timeline?

### Cross-OS semantics and security model

15. What cross-OS semantics must the fabric normalize or explicitly mark `unknown`: path and drive
    semantics, case sensitivity, line endings, process creation and termination, signals versus
    job objects, filesystem atomicity, file locking and available sandbox primitives on each
    accepted platform floor?
16. What is the security model for an enrolled but not-fully-trusted node — what it may read,
    what it may write, what it may observe, and how a malicious or compromised node is contained,
    revoked and its stale work fenced?
17. How is a node prevented from widening its own authority, forging events, replaying another
    node's messages, or acting as a second canonical writer, and what is the falsifier for each?
18. How are egress, privacy and data-residency bounds attached to a task enforced at placement so
    private content never lands on a node the task's GoalSpec did not authorize?

### Protocol shape and provider-free fixtures

19. What is the shape of the protocol: which message classes (hello/welcome, descriptor,
    lease-grant, fence-carrying request, record/ack, heartbeat, drain, revoke, reset/gap), what
    cursor and epoch fields each carries, and why the shape is transport-agnostic without
    selecting an encoding?
20. How does the fabric protocol relate to the already known broker/IPC protocol and its open
    freeze blockers in G-05, and what must be shared, distinct or explicitly deferred?
21. What provider-free fixtures must accept or reject: an enrollment and revocation drill, a
    mutual-authentication and downgrade-refusal probe, a placement-refusal on egress bounds, a
    stale-holder fence rejection, a partition with stale-work replay, a disconnect/reconnect
    recording gap, a lost-machine resume, a drain with in-flight effects, and a cross-OS
    normalization matrix — and what is the exact pass/fail predicate for each?
22. How do the fixtures prove that a remote node never becomes a second writer or a second
    portfolio executive, that enrollment confers no authority, that an idle node spends nothing,
    and that recovery never invents completion — using synthetic messages and local processes
    only, with no provider call?

## Deliverable

A node fabric and remote-execution-protocol design candidate containing: an enrollment, identity
and authenticated-transport section; a placement, lease and fencing section that keeps the
shipping core single-node and consensus-free; a disconnect, reconnect, drain and recorded-work
recovery section covering lost-machine continuity; a cross-OS semantics and node-security section
with a threat model; and a protocol-shape section with message classes and cursor/epoch fields,
transport-agnostic and non-selecting, plus a provider-free fixture suite. The candidate explicitly
distinguishes multi-node execution from canonical-writer availability (D-020), states that
enrollment confers no authority, and gives each placement, lease, fence, recovery and security
recommendation a competing option, a decisive falsifier and what it does not prove. No language,
store, framework, runtime, transport, message bus, orchestrator or vendor is selected.

## Non-goals

- No selection of a language, package manager, store, framework, runtime, transport protocol,
  message bus, container orchestrator, certificate authority or vendor.
- No reopening of D-020, the single fenced canonical writer, the kernel's fence/epoch ownership or
  the store/availability seam.
- No claim that automatic takeover is in the shipping core; per D-020 the core is single-node and
  takeover is a first-party plugin.
- No assertion that enrollment, a certificate, local-network proximity or prior execution confers
  authority; each is falsifiable and none widens the task grant.
- No second canonical writer and no second portfolio executive created by a node, lease, placement
  or remote view.
- No route qualification, account or subscription entitlement claim, or eligibility finding.
- No provider, model, credential or account call; no node enrolled or transport contacted; every
  fixture is synthetic, local and provider-free.
- No claim of measured availability, failover time, placement quality, transport performance or
  recovery time; each is a hypothesis with a falsifier or `unknown`.
- No new executive tier and no standing autonomous executive.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The enrollment and transport section defines authorized enrollment, revocable identity, mutual
  authentication, forward secrecy, replay resistance, integrity, version negotiation with
  downgrade refusal, and the minimum-control-kernel-first hydration rule.
- The placement, lease and fencing section defines placement inputs and justification, at-most-one
  active executor per task/step, receiver-checked fencing epochs, honest ordering between granted,
  started, recorded and settled, and keeps the shipping core single-node and consensus-free with
  any replicated coordination confined to the D-020 plugin seam.
- The connectivity section distinguishes disconnect, reconnect, partition, retirement and crash,
  and defines `drain` under the D-022 vocabulary.
- The recovery section defines recorded-work resume after a lost machine, verification before
  resume, duplicate-execution prevention, and classification of partial work as re-executable,
  resumable or `unknown`; no completion is invented.
- The cross-OS and security section normalizes or marks `unknown` the path, process, signal,
  filesystem, locking and sandbox differences across the platform floors, and defines containment,
  revocation and stale-work fencing for an enrolled but untrusted node.
- The protocol-shape section names message classes, cursor and epoch fields, is transport-
  agnostic, relates to the broker/IPC protocol and its G-05 freeze blockers, and selects no
  transport or encoding.
- The candidate states in terms that multi-node execution is distinct from canonical-writer
  availability (D-020) and that enrollment confers no authority.
- The provider-free fixture suite specifies predicates for enrollment/revocation, mutual
  authentication and downgrade refusal, egress-bounded placement refusal, stale-holder fence
  rejection, partition replay, disconnect/reconnect gap recording, lost-machine resume, drain with
  in-flight effects and cross-OS normalization, and no fixture requires a provider call.
- Every recommendation names a competing option, a decisive falsifier and what it does not prove;
  no language, store, framework, transport or vendor is selected and no route is qualified.
- The candidate explicitly states what it does not establish: no measured availability or
  failover, no placement or transport performance claim, no security guarantee against a
  determined node, no route qualification and no entitlement.
- Protected paths are untouched; privacy and secret scan are clean.
